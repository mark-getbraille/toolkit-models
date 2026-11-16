"""More large collections of described pictures and of questions about pictures, for the Picture Model Training Kit.

Every collection here was checked for three things before it was added:
  1. its words are under CC0, public domain, CC BY, ODC-BY, CDLA-Permissive, MIT, Apache or BSD (never NC, ND or
     research-only);
  2. its words were written (or spoken) by people, never by GPT, Gemini, Claude or another model;
  3. every picture used is itself under a licence that allows sharing. Most of these collections use COCO's photos,
     and COCO photos come from Flickr under several licences, some of them non-commercial: only photos whose own
     licence is CC BY 2.0 or "no known copyright restrictions" are used (sources.COCO_FREE_LICENCES), about 17 in
     every 100 COCO photos. Open Images photos are all CC BY 2.0; VizWiz photos are CC BY 4.0.

The collections:
  vqav2_val          VQA v2, its "val2014" part (the ready-made coco_questions pack uses only the "train2014" part,
                     so nothing is repeated): short questions about everyday photos, answered by ten people each.
  okvqa              OK-VQA: questions that need some general knowledge ("What is this animal's diet?").
  visdial            Visual Dialog: one person asked about a photo they could not see, another person who could see
                     it answered. Close to what a blind person asks.
  visual_genome_qa   Visual Genome's questions and answers (what, where, how many, what colour ...).
  ln_coco            Localized Narratives on COCO photos: people described the photo aloud.
  ln_open_images_more Localized Narratives on the Open Images "validation" and "test" photos (the kit's own
                     localized_narratives source uses only the "train" photos, so nothing is repeated).
  vizwiz_captions_train VizWiz Captions, its "train" part (sources.vizwiz_captions uses only the "val" part):
                     photos taken by blind people, described in one sentence.

Main parts: MORE_SOURCES (Source entries in the same form as sources.SOURCES), one prepare_<key>(source, data_dir,
work, cap) function per collection, and NEEDS_LICENCE_CHECK (a collection that is ready but whose licence is not yet
written down by its makers; it is not trained on until it is).
"""

import json
import os
import random
import re
import zipfile

import sources
from sources import (BRIEF, CANNOT_TELL, DETAILED, NARRATE, Source, clean, download_file, fetch_pictures,
                     hf_parquet_files, hf_parquet_rows, tidy_narrative)

VQA_URL = "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/"
OKVQA_URL = "https://okvqa.allenai.org/static/data/"
VG_URL = "https://homes.cs.washington.edu/~ranjay/visualgenome/data/dataset/"
LN_URL = "https://storage.googleapis.com/localized-narratives/annotations/"
VIZWIZ_URL = "https://vizwiz.cs.colorado.edu/"

# A long spoken description (at least this many words) is learned as "Describe this picture in detail."; a shorter
# one as "Describe this picture.".
DETAILED_WORDS = 45


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


# ----------------------------------------------------------------- shared helpers

def coco_free_photos():
    """The COCO photos that may be shared: {COCO image number: address of the photo}, only those whose own licence is
    CC BY 2.0 or "no known copyright restrictions" (about 20,800 of 123,287). The list comes from the phiyodr copy of
    COCO 2017 on Hugging Face (30 MB), which gives each photo's licence; COCO 2017 holds the same photos, with the same
    numbers, as COCO 2014."""
    say("  Reading COCO's list of photos and their licences.")
    free = {}
    for name in hf_parquet_files("phiyodr/coco2017", r"^data/"):
        for row in hf_parquet_rows("phiyodr/coco2017", name, ["license", "image_id", "coco_url"]):
            if row.get("license") in sources.COCO_FREE_LICENCES:
                free[int(row["image_id"])] = row["coco_url"]
    return free


def download_to(work, url, name=None):
    """Download url into the work folder once (carrying on from a part already there); the path."""
    path = os.path.join(work, name or url.rsplit("/", 1)[-1])
    download_file(url, path)
    return path


def json_in_zip(path, member=None):
    """The JSON file inside a zip (the first one, or member)."""
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith(".json")]
        with z.open(member or names[0]) as f:
            return json.load(f)


def sentence(text):
    """A short answer as a sentence: a capital first letter and a full stop ("red and white" -> "Red and white.")."""
    text = clean(text)
    if not text:
        return ""
    return text[0].upper() + text[1:] + ("" if text.endswith((".", "?", "!")) else ".")


def as_question(text):
    """A question with a capital first letter and a question mark."""
    return sources.as_question(text)


def agreed_answer(answers, at_least=3):
    """The answer most of the people gave, as a sentence, when at least at_least of them gave it (VQA counts an
    answer as right when three people gave it); CANNOT_TELL when most said it cannot be answered; "" otherwise."""
    counts = {}
    for a in answers or []:
        a = clean(a).lower()
        if a:
            counts[a] = counts.get(a, 0) + 1
    if not counts:
        return ""
    best = max(counts, key=counts.get)
    if counts[best] < at_least:
        return ""
    if best in ("unanswerable", "unsuitable", "unsuitable image"):
        return CANNOT_TELL
    return sentence(best)


def fetch_shared(items, folder, workers=8):
    """Like sources.fetch_pictures, for collections with several questions about the same photo: each photo is
    downloaded once (items are (file name, address, row), and rows with the same file name share it); the rows
    whose photo came, with "picture" set."""
    by_name, order = {}, []
    for name, url, row in items:
        if name not in by_name:
            by_name[name] = (url, [])
            order.append(name)
        by_name[name][1].append(row)
    got = fetch_pictures([(name, by_name[name][0], {"name": name}) for name in order], folder, workers=workers)
    rows = []
    for result in got:
        for row in by_name[result["name"]][1]:
            rows.append(dict(row, picture=result["picture"]))
    return rows


def pick_by_photo(per_photo, want, seed, most_each):
    """Pick rows from several photos: per_photo is {photo: [rows]}; photos are shuffled with seed and at most most_each
    rows are taken from each, until there are want rows. Spreading the rows over many photos teaches more than many
    questions about a few photos."""
    photos = sorted(per_photo)
    rng = random.Random(seed)
    rng.shuffle(photos)
    picked = []
    for photo in photos:
        rows = per_photo[photo][:]
        rng.shuffle(rows)
        picked += rows[:most_each]
        if len(picked) >= want:
            break
    return picked[:want]


# ----------------------------------------------------------------- the collections

def prepare_vqav2_val(source, data_dir, work, cap):
    """VQA v2, val2014 part: questions about everyday COCO photos with the answer at least three of ten people gave
    (CC BY 4.0, visualqa.org, written in the files themselves). Only COCO photos under CC BY 2.0 or no known
    copyright; at most 4 questions per photo."""
    free = coco_free_photos()
    say("  Downloading the VQA v2 questions and answers (14 MB).")
    questions = json_in_zip(download_to(work, VQA_URL + "v2_Questions_Val_mscoco.zip"))["questions"]
    annotations = json_in_zip(download_to(work, VQA_URL + "v2_Annotations_Val_mscoco.zip"))["annotations"]
    asked = {q["question_id"]: q for q in questions if q["image_id"] in free}
    per_photo = {}
    for a in annotations:
        q = asked.get(a["question_id"])
        if not q:
            continue
        answer, question = agreed_answer([x["answer"] for x in a["answers"]]), as_question(q["question"])
        if answer and question:
            per_photo.setdefault(q["image_id"], []).append(
                (f"{q['image_id']}.jpg", free[q["image_id"]], {"question": question, "answer": answer, "split": ""}))
    items = pick_by_photo(per_photo, int((cap + source.test) * 1.1), 41, 4)
    say(f"  Fetching the COCO photos for {len(items)} VQA v2 questions.")
    return fetch_shared(items, os.path.join(data_dir, "vqav2_val"))


def prepare_okvqa(source, data_dir, work, cap):
    """OK-VQA: questions about COCO photos that need general knowledge, with the answer at least three of the
    people gave (CC BY 4.0, okvqa.allenai.org, written in the files themselves). Its own val2014 part gives the test
    pictures. Only COCO photos under CC BY 2.0 or no known copyright."""
    free = coco_free_photos()
    items = []
    for part in ("train2014", "val2014"):
        questions = json_in_zip(download_to(work, OKVQA_URL + f"OpenEnded_mscoco_{part}_questions.json.zip",
                                            f"okvqa_{part}_questions.zip"))["questions"]
        annotations = json_in_zip(download_to(work, OKVQA_URL + f"mscoco_{part}_annotations.json.zip",
                                              f"okvqa_{part}_annotations.zip"))["annotations"]
        asked = {q["question_id"]: q for q in questions if q["image_id"] in free}
        for a in annotations:
            q = asked.get(a["question_id"])
            if not q:
                continue
            answer, question = agreed_answer([x["answer"] for x in a["answers"]]), as_question(q["question"])
            if answer and question and answer != CANNOT_TELL:
                items.append((f"{q['image_id']}.jpg", free[q["image_id"]],
                              {"question": question, "answer": answer, "split": "test" if part == "val2014" else ""}))
    random.Random(43).shuffle(items)
    items = items[:int((cap + source.test) * 1.1)]
    say(f"  Fetching the COCO photos for {len(items)} OK-VQA questions.")
    return fetch_shared(items, os.path.join(data_dir, "okvqa"))


# A question that points back to an earlier one ("are they single story", "what colour is it") cannot be understood
# alone; only questions without these words are used from Visual Dialog's conversations.
POINTS_BACK = re.compile(r"\b(it|its|it's|they|them|their|theirs|he|him|his|she|her|hers|those|these|that one|"
                         r"the other|else|another|any other|other)\b", re.I)


def prepare_visdial(source, data_dir, work, cap):
    """Visual Dialog 1.0: one person asked ten questions about a COCO photo they could not see (they had only a
    one-line description), and a second person, who saw the photo, answered (CC BY 4.0, visualdialog.org; the jxu124
    copy on Hugging Face, 33 MB, words only). Questions that point back to an earlier one ("are they ...") are left
    out, at most 3 per photo. Only COCO photos under CC BY 2.0 or no known copyright."""
    free = coco_free_photos()
    say("  Reading the Visual Dialog conversations (33 MB).")
    per_photo = {}
    for name in hf_parquet_files("jxu124/visdial", r"^data/train-"):
        for row in hf_parquet_rows("jxu124/visdial", name, ["dialog", "global_image_id"]):
            image_id = int(str(row["global_image_id"]).rsplit(".", 1)[-1])
            if image_id not in free:
                continue
            for question, answer in row.get("dialog") or []:
                question, answer = clean(question), clean(answer)
                if len(question.split()) < 3 or POINTS_BACK.search(question) or not answer:
                    continue
                if re.fullmatch(r"(?i)(can'?t|cannot) (tell|see)( that)?|not sure|unsure|i don'?t know", answer):
                    answer = CANNOT_TELL
                per_photo.setdefault(image_id, []).append(
                    (f"{image_id}.jpg", free[image_id],
                     {"question": as_question(question), "answer": sentence(answer), "split": ""}))
    items = pick_by_photo(per_photo, int((cap + source.test) * 1.1), 47, 3)
    say(f"  Fetching the COCO photos for {len(items)} Visual Dialog questions.")
    return fetch_shared(items, os.path.join(data_dir, "visdial"))


def prepare_visual_genome_qa(source, data_dir, work, cap):
    """Visual Genome: questions and answers people wrote about photos (CC BY 4.0, visualgenome.org). Visual Genome's
    own photo files are not used: only its photos that are also COCO photos under CC BY 2.0 or no known copyright,
    fetched from COCO. At most 4 questions per photo."""
    free = coco_free_photos()
    say("  Downloading Visual Genome's list of photos and its questions (27 MB).")
    to_coco = {}
    for image in json_in_zip(download_to(work, VG_URL + "image_data.json.zip", "vg_image_data.json.zip")):
        if image.get("coco_id") and image["coco_id"] in free:
            to_coco[image["image_id"]] = image["coco_id"]
    per_photo = {}
    for entry in json_in_zip(download_to(work, VG_URL + "question_answers.json.zip", "vg_question_answers.json.zip")):
        coco_id = to_coco.get(entry.get("id"))              # each entry is {"id": Visual Genome photo, "qas": [...]}
        if not coco_id:
            continue
        for qa in entry.get("qas") or []:
            question, answer = as_question(qa.get("question")), sentence(qa.get("answer"))
            if question and answer:
                per_photo.setdefault(coco_id, []).append(
                    (f"{coco_id}.jpg", free[coco_id], {"question": question, "answer": answer, "split": ""}))
    items = pick_by_photo(per_photo, int((cap + source.test) * 1.1), 53, 4)
    say(f"  Fetching the COCO photos for {len(items)} Visual Genome questions.")
    return fetch_shared(items, os.path.join(data_dir, "visual_genome_qa"))


def narrative_row(text, split=""):
    """A Localized Narratives row: the long ones are "Describe this picture in detail.", the others "Describe this
    picture."; None when it is too short or too long."""
    words = len(text.split())
    if not 12 <= words <= 150:
        return None
    return {"question": DETAILED if words >= DETAILED_WORDS else NARRATE, "answer": text, "split": split}


def prepare_ln_coco(source, data_dir, work, cap):
    """Localized Narratives on COCO photos: people described the photo aloud while pointing, written down (Google;
    descriptions CC BY 4.0). Only COCO photos under CC BY 2.0 or no known copyright; COCO's val2017 part gives the
    test pictures."""
    free = coco_free_photos()
    items = []
    for part, split in (("coco_train_captions.jsonl", ""), ("coco_val_captions.jsonl", "test")):
        say(f"  Downloading the Localized Narratives for COCO ({part}).")
        with open(download_to(work, LN_URL + part, "ln_" + part), encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                image_id = int(entry["image_id"])
                row = narrative_row(sources.tidy_narrative(entry.get("caption")), split) if image_id in free else None
                if row:
                    items.append((f"{image_id}.jpg", free[image_id], row))
    random.Random(59).shuffle(items)
    items = items[:int((cap + source.test) * 1.1)]
    say(f"  Fetching {len(items)} COCO photos.")
    return fetch_shared(items, os.path.join(data_dir, "ln_coco"))


def prepare_ln_open_images_more(source, data_dir, work, cap):
    """Localized Narratives on the Open Images "validation" and "test" photos (Google; descriptions CC BY 4.0,
    photos CC BY 2.0), about 167,000 descriptions that the localized_narratives source (train photos) does not use.
    The validation part gives the test pictures."""
    items = []
    for part, folder, split in (("open_images_validation_captions.jsonl", "validation", "test"),
                                ("open_images_test_captions.jsonl", "test", "")):
        say(f"  Downloading the Localized Narratives for Open Images ({part}, up to 31 MB).")
        with open(download_to(work, LN_URL + part, "ln_" + part), encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                row = narrative_row(tidy_narrative(entry.get("caption")), split)
                if row:
                    items.append((f"{entry['image_id']}.jpg",
                                  f"https://open-images-dataset.s3.amazonaws.com/{folder}/{entry['image_id']}.jpg",
                                  row))
    random.Random(61).shuffle(items)
    items = items[:int((cap + source.test) * 1.15)]               # some photos no longer download
    say(f"  Fetching {len(items)} Open Images photos.")
    return fetch_shared(items, os.path.join(data_dir, "ln_open_images_more"))


def prepare_vizwiz_captions_train(source, data_dir, work, cap):
    """VizWiz Captions, train part: about 23,000 photos taken by blind people, each described in one sentence by
    five people (CC BY 4.0, written in the file itself; vizwiz.org). VizWiz's "too blurry to describe" stock answer
    and rejected descriptions are left out; the first good description of each photo is used. The photos are fetched
    one by one from VizWiz's own server, so the 10 GB archive is not needed."""
    say("  Downloading the VizWiz Captions descriptions (4.5 MB).")
    data = json_in_zip(download_to(work, VIZWIZ_URL + "VizWiz_final/caption/annotations.zip",
                                   "vizwiz_caption_annotations.zip"), "annotations/train.json")
    first = {}
    for a in data["annotations"]:
        caption = clean(a.get("caption"))
        if a.get("is_precanned") or a.get("is_rejected") or len(caption.split()) < 4 or a["image_id"] in first:
            continue
        first[a["image_id"]] = sentence(caption)
    items = []
    for image in data["images"]:
        if image["id"] in first:
            items.append((image["file_name"], VIZWIZ_URL + "VizWiz_visualization_img/" + image["file_name"],
                          {"question": BRIEF, "answer": first[image["id"]], "split": ""}))
    random.Random(67).shuffle(items)
    items = items[:int((cap + source.test) * 1.05)]
    say(f"  Fetching {len(items)} VizWiz photos.")
    return fetch_pictures(items, os.path.join(data_dir, "vizwiz_captions_train"), workers=6)


# VizWiz Image Quality Issues: what is wrong with a photo, by vote of five people. Its words are not under a written
# licence yet (the VizWiz pages for questions and captions say CC BY 4.0, this one says nothing), so it is in
# NEEDS_LICENCE_CHECK, not in MORE_SOURCES.
QUALITY = "Is this photo good enough to see what it shows? If not, what is wrong with it?"
FLAWS = (("BLR", "it is blurry"), ("DRK", "it is too dark"), ("BRT", "it is too bright"),
         ("FRM", "the object is not fully in the picture"), ("OBS", "something, such as a finger, is in the way"),
         ("ROT", "it is turned sideways or upside down"))


def quality_answer(entry):
    """The answer for one VizWiz photo: what at least three of the five people said is wrong with it."""
    flaws = entry.get("flaws") or {}
    wrong = [words for code, words in FLAWS if flaws.get(code, 0) >= 3]
    unreadable = entry.get("unrecognizable", 0) >= 3
    if unreadable:
        return "No, it is hard to tell what this shows" + (": " + ", and ".join(wrong) if wrong else "") + "."
    if wrong:
        return "It can be seen, but it could be better: " + ", and ".join(wrong) + "."
    if flaws.get("NON", 0) >= 3:
        return "Yes, the photo is clear enough."
    return ""                                              # the people did not agree: left out


def prepare_vizwiz_quality(source, data_dir, work, cap):
    """VizWiz Image Quality Issues (see QUALITY above): photos taken by blind people, with what is wrong with each."""
    path = download_to(work, VIZWIZ_URL + "VizWiz_final/image_quality/annotations.zip", "vizwiz_quality.zip")
    items = []
    for part in ("train.json", "val.json"):
        for entry in json_in_zip(path, part):
            answer = quality_answer(entry)
            if answer:
                items.append((entry["image"], VIZWIZ_URL + "VizWiz_visualization_img/" + entry["image"],
                              {"question": QUALITY, "answer": answer, "split": "test" if part == "val.json" else ""}))
    random.Random(71).shuffle(items)
    items = items[:int((cap + source.test) * 1.05)]
    say(f"  Fetching {len(items)} VizWiz photos.")
    return fetch_pictures(items, os.path.join(data_dir, "vizwiz_quality"), workers=6)


# ----------------------------------------------------------------- the table

COCO_PHOTOS = "photos from COCO, only those under CC BY 2.0 or no known copyright restrictions"

MORE_SOURCES = [
    Source("vqav2_val", "VQA v2 (second part): questions about everyday photos, answered by ten people",
           "CC BY 4.0 (visualqa.org; written in the files); " + COCO_PHOTOS,
           "VQA v2 (Goyal et al., 2017), CC BY 4.0, https://visualqa.org; " + COCO_PHOTOS, "permissive",
           6000, 20, prepare_vqav2_val, "up to 1 GB of photos"),
    Source("okvqa", "OK-VQA: questions about photos that need general knowledge",
           "CC BY 4.0 (okvqa.allenai.org; written in the files); " + COCO_PHOTOS,
           "OK-VQA (Marino et al., 2019), CC BY 4.0, https://okvqa.allenai.org; " + COCO_PHOTOS, "permissive",
           750, 20, prepare_okvqa, "up to 400 MB of photos"),
    Source("visdial", "Visual Dialog: questions from someone who could not see the photo, answered by one who could",
           "CC BY 4.0 (visualdialog.org); " + COCO_PHOTOS,
           "Visual Dialog 1.0 (Das et al., 2017), CC BY 4.0, https://visualdialog.org; " + COCO_PHOTOS, "permissive",
           8000, 20, prepare_visdial, "up to 3 GB of photos"),
    Source("visual_genome_qa", "Visual Genome: questions and answers about photos",
           "CC BY 4.0 (visualgenome.org); " + COCO_PHOTOS,
           "Visual Genome (Krishna et al., 2017), CC BY 4.0, https://visualgenome.org; " + COCO_PHOTOS, "permissive",
           8000, 20, prepare_visual_genome_qa, "up to 1.3 GB of photos"),
    Source("ln_coco", "Localized Narratives on COCO: photos described aloud by people",
           "CC BY 4.0 descriptions (google.github.io/localized-narratives); " + COCO_PHOTOS,
           "Localized Narratives (Pont-Tuset et al., 2020), CC BY 4.0; " + COCO_PHOTOS, "permissive",
           7000, 20, prepare_ln_coco, "up to 3.3 GB of photos"),
    Source("ln_open_images_more", "Localized Narratives on more Open Images photos, described aloud",
           "CC BY 4.0 descriptions (google.github.io/localized-narratives); Open Images photos, CC BY 2.0",
           "Localized Narratives (Pont-Tuset et al., 2020), CC BY 4.0; photos from Open Images, CC BY 2.0",
           "permissive", 15000, 20, prepare_ln_open_images_more, "up to 13 GB of photos"),
    Source("vizwiz_captions_train", "VizWiz Captions (train part): photos taken by blind people, one sentence each",
           "CC BY 4.0 (vizwiz.org; written in the file)",
           "VizWiz-Captions (Gurari et al., 2020), CC BY 4.0, https://vizwiz.org", "permissive", 7000, 20,
           prepare_vizwiz_captions_train, "up to 12 GB of photos"),
]

# Ready, but not trained on: its makers have not written down a licence for its words yet (see QUALITY above).
NEEDS_LICENCE_CHECK = [
    Source("vizwiz_quality", "VizWiz photo quality: is the photo clear, and if not, what is wrong",
           "Not written down (vizwiz.org/tasks-and-datasets/image-quality-issues); photos CC BY 4.0",
           "VizWiz Image Quality Issues (Chiu et al., 2020), https://vizwiz.org", "permissive", 6000, 20,
           prepare_vizwiz_quality, "up to 10 GB of photos"),
]
