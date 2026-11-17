"""The collections of described pictures the Picture Model Training Kit learns from, in one table (SOURCES), and the
code that downloads each one and makes its pictures smaller.

Each Source says where the pictures come from, the licence of its pictures and of its words, its group and how many
of its pictures to use at most. Every collection is turned into rows {"picture", "question", "answer", "source"}:
the picture made smaller (at most LONG_SIDE pixels on its long side), the question the model is asked, and the
person's words as the answer.

Groups:
  "permissive"  CC0, public domain, CC BY, ODC-BY, Apache or MIT: the default. The trained add-on stays permissive
                (credit only), which the toolkit's rules ask for.
  "share-alike" CC BY-SA (Wikipedia): only with --with-wikipedia. The add-on is then labelled CC BY-SA 4.0 and
                credits Wikipedia, and is published as a separate choice.
  "noncommercial" CC BY-NC, CC BY-NC-SA or CC BY-NC-ND: only with --personal-noncommercial. The add-on is then
                for PERSONAL USE ONLY (never sold, published or put in a product), which the report, ATTRIBUTION.txt
                and PERSONAL-USE-ONLY.txt in the zip say.
  "research"    research-only or "academic use" terms: only with --personal-research (and --accept-research-terms).
                Personal use only, like "noncommercial".
  The two personal-use groups come from personal_sources.py (PERSONAL_SOURCES), when that file is there; without it
  the kit simply has none. A personal-use collection may give its terms page (terms=) and a one-line summary of its
  terms (terms_summary=), shown in the report and in the program's research-terms window.

Content choices (Source.content): most collections have none (""). A collection marked "nudity" (non-sexual nudes
in art) is only used with --with-nudity, and one marked "medical" (medical and anatomy pictures) only with
--with-medical, so the person training decides whether the model learns from those pictures. chosen() leaves out
what was not chosen; content_choices_text() says the choices in plain words for the report and ATTRIBUTION.txt.
Two more content tags come from the REVIEW collections (review_sources.py, adult_review_sources.py: pictures a
trusted sighted adult screens first, used through own_data.py from "Describe pictures" workspaces): "intimate"
(medical and educational pictures of adult genitals and breasts) is used only when BOTH with_nudity and with_medical
are chosen, and "sexual" (adult sexual content) only with with_sexual, which itself needs with_nudity; sexual content
is for personal use only. allowed_contents() gives the tags a training's choices allow. A picture-making model never
learns from either (PICTURE_MAKING_NEVER), nor from any review collection.

Sizes (--size): each source has a cap for "normal"; "quick" uses a tenth of it (a try of an hour or two) and
"full" three times as much (several nights on a fast card).

A finished source is not prepared again when the kit is started again (its rows are kept in data/<key>-<size>.jsonl;
a bigger size prepares it again, but pictures already downloaded are kept).

Main parts: Source, SOURCES, chosen(with_wikipedia, with_nudity=, with_medical=, with_noncommercial=, with_research=),
content_choices_text, PERSONAL_GROUPS, is_personal, terms_link, terms_summary, PERSONAL_WARNING,
prepare_source(source, data_dir, work, cap), questions.
"""

import concurrent.futures
import io
import json
import os
import random
import re
import tarfile
import time

LONG_SIDE = 896
# The permanent picture library (train.py --library): when set, every picture is also kept as a larger copy (at most
# ARCHIVE_SIDE pixels, high quality) under ARCHIVE_DIR, at the same place as its training copy under DATA_DIR, for
# future models; and downloaded originals (archives, data files, packs) are kept instead of deleted.
ARCHIVE_DIR = None
DATA_DIR = None
ARCHIVE_SIDE = 2048
KEEP_DOWNLOADS = False
USER_AGENT = "PictureModelTrainingKit/2"        # plain: some museum picture servers refuse longer ones

# The questions, in the toolkit's own words where it has them (vision/vlm.py PICTURE).
DETAILED = "Describe this picture in detail."
BRIEF = "Describe this picture in one sentence."
ALT_TEXT = "Write a short description of this picture for someone who cannot see it."
READ_TEXT = "Describe this picture in one sentence, and read out any text in it."
NARRATE = "Describe this picture."
ARTWORK = "What artwork is this?"
MUSEUM = "Tell me about this museum object."
SPACE = "What does this NASA picture show?"
CANNOT_TELL = "I can't tell from this picture."
SIZES = {"quick": 0.1, "normal": 1.0, "full": 3.0}

say = print                    # replaced by train.say when the kit runs


class Source:
    """One collection of described pictures (see the module docstring).

    key        its short name (also the name of its data file)
    name       its name in the report
    licence    the licence of its words and pictures, in plain words, with where it is written
    credit     the credit line for ATTRIBUTION.txt
    group      "permissive", "share-alike", "noncommercial" or "research" (see the module docstring)
    cap        the most pictures to use at "normal" size
    test       how many of its pictures are kept back for the test
    prepare    a function (source, data_dir, work, cap) -> [rows], each with "split" ("train", "test" or "")
    download   roughly how much it downloads, for the screen ("7.6 GB")
    content    "" for most collections; "nudity" (non-sexual nudes in art: only with --with-nudity) or "medical"
               (medical and anatomy pictures: only with --with-medical); "intimate" and "sexual" are known too (see
               allowed_contents), though today only review collections use them
    terms      for a personal-use collection: the web address of its licence or terms page ("" when none; the first
               web address in its licence or credit is used then)
    terms_summary  for a personal-use collection: its terms in one plain line ("" when none; its licence is used)"""

    def __init__(self, key, name, licence, credit, group, cap, test, prepare, download, content="", terms="",
                 terms_summary=""):
        """Store the fields (see the class docstring)."""
        if content not in CONTENTS:
            raise ValueError(f"unknown content {content!r} for {key}")
        self.key, self.name, self.licence, self.credit, self.group = key, name, licence, credit, group
        self.cap, self.test, self.prepare, self.download = cap, test, prepare, download
        self.content = content
        self.terms, self.terms_summary = terms, terms_summary


# The content choices a collection can need: "" (none), "nudity", "medical", "intimate" and "sexual" (see the module
# docstring and allowed_contents).
CONTENTS = ("", "nudity", "medical", "intimate", "sexual")
# The content tags a picture-making model never learns from, whatever is chosen.
PICTURE_MAKING_NEVER = ("intimate", "sexual")


def allowed_contents(with_nudity=False, with_medical=False, with_sexual=False):
    """The content tags a training's choices allow, as a set: "" always; "nudity" with with_nudity; "medical" with
    with_medical; "intimate" only with BOTH with_nudity and with_medical; "sexual" only with with_sexual AND
    with_nudity (the adult sexual content choice needs art with nudity)."""
    allowed = {""}
    for tag, on in (("nudity", with_nudity), ("medical", with_medical),
                    ("intimate", with_nudity and with_medical), ("sexual", with_sexual and with_nudity)):
        if on:
            allowed.add(tag)
    return allowed


# ----------------------------------------------------------------- shared helpers

def archive_path(path):
    """Where the library keeps the large copy of the training copy at path (None without a library)."""
    if ARCHIVE_DIR and DATA_DIR:
        return os.path.join(ARCHIVE_DIR, os.path.relpath(path, DATA_DIR))
    return None


def have(path):
    """True when a picture needs nothing more: its training copy is there and, with a picture library, its large
    copy too (a picture prepared before the library existed is downloaded again for its large copy)."""
    keep = archive_path(path)
    return os.path.exists(path) and (keep is None or os.path.exists(keep))


def smaller(data, path):
    """Save picture bytes as a JPEG at most LONG_SIDE pixels on its long side; False when it cannot be read or is
    tiny (under 64 pixels)."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGB")
    except Exception:  # noqa: BLE001 - a damaged picture is left out
        return False
    if min(img.size) < 64:
        return False
    if ARCHIVE_DIR and DATA_DIR:
        keep = os.path.join(ARCHIVE_DIR, os.path.relpath(path, DATA_DIR))
        if not os.path.exists(keep):
            os.makedirs(os.path.dirname(keep), exist_ok=True)
            larger = img.copy()
            larger.thumbnail((ARCHIVE_SIDE, ARCHIVE_SIDE))
            larger.save(keep, "JPEG", quality=93)
    img.thumbnail((LONG_SIDE, LONG_SIDE))
    img.save(path, "JPEG", quality=90)
    return True


def download_file(url, path):
    """Download url to path, carrying on from a part already there; says the progress every 5 percent."""
    import requests
    done = os.path.getsize(path) if os.path.exists(path) else 0
    head = requests.head(url, timeout=60, allow_redirects=True, headers={"User-Agent": USER_AGENT})
    total = int(head.headers.get("content-length", 0))
    if total and done == total:
        return
    headers = {"User-Agent": USER_AGENT, **({"Range": f"bytes={done}-"} if done else {})}
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        if done and r.status_code != 206:
            done = 0                                       # the server started again from the beginning
        next_say = 5
        with open(path, "ab" if done else "wb") as f:
            for block in r.iter_content(1 << 20):
                f.write(block)
                done += len(block)
                if total > 300_000_000 and done * 100 // total >= next_say:     # big files only
                    say(f"    {done * 100 // total} percent of {total / 1024 ** 3:.1f} GB")
                    next_say = done * 100 // total + 5


def fetch_pictures(items, folder, workers=8, pause=0.0):
    """Download pictures from the web: items are (file name, address, row); returns the rows whose picture came
    (made smaller into folder), with "picture" set. A picture that no longer exists is left out. Says the progress
    every 500 pictures. pause: seconds each download waits first (to be gentle with a museum's server)."""
    import requests
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    os.makedirs(folder, exist_ok=True)

    def one(item):
        """Fetch one picture; the row, or None."""
        name, url, row = item
        path = os.path.join(folder, name)
        if not have(path):
            if pause:
                time.sleep(pause)
            try:
                r = session.get(url, timeout=30)
                if r.status_code != 200 or not smaller(r.content, path):
                    return None
            except Exception:  # noqa: BLE001 - a picture that cannot be fetched is left out
                return None
        return dict(row, picture=path)

    out, done = [], 0
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for result in pool.map(one, items):
            done += 1
            if result:
                out.append(result)
            if done % 500 == 0:
                say(f"    {done} of {len(items)} pictures fetched ({len(out)} usable)")
    return out


def hf_parquet_files(repo, pattern, revision="main"):
    """The parquet files of a Hugging Face dataset whose names match the regular expression pattern, sorted."""
    from huggingface_hub import HfApi
    return sorted(f for f in HfApi().list_repo_files(repo, repo_type="dataset", revision=revision)
                  if f.endswith(".parquet") and re.search(pattern, f))


def hf_parquet_rows(repo, name, columns=None, revision="main"):
    """The rows of one parquet file of a Hugging Face dataset (downloaded once into the kit's cache)."""
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    local = hf_hub_download(repo, name, repo_type="dataset", revision=revision)
    return pq.read_table(local, columns=columns).to_pylist()


def clean(text):
    """A description with its spaces tidied; "" for nothing."""
    return " ".join(str(text or "").split())


def save_picture(row_id, data, folder):
    """Save picture bytes from a parquet row as a smaller JPEG named row_id; the path, or None."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, re.sub(r"[^\w.-]", "_", str(row_id)) + ".jpg")
    if have(path) or smaller(data or b"", path):
        return path
    return None


# ----------------------------------------------------------------- the collections

DOCCI_URL = "https://storage.googleapis.com/docci/data/"


def prepare_docci(source, data_dir, work, cap):
    """DOCCI: 15,000 photos, each described in about 120 words (Google; descriptions and photos CC BY 4.0). Its own
    "test" part gives the test pictures."""
    import requests
    folder = os.path.join(data_dir, "docci")
    os.makedirs(folder, exist_ok=True)
    descriptions = {}
    for line in requests.get(DOCCI_URL + "docci_descriptions.jsonlines", timeout=120).text.splitlines():
        if line.strip():
            entry = json.loads(line)
            if entry["split"] in ("train", "test"):
                descriptions[entry["image_file"]] = (entry["split"], entry["description"])
    archive = os.path.join(work, "docci_images.tar.gz")
    say("  Downloading DOCCI's pictures (7.6 GB).")
    download_file(DOCCI_URL + "docci_images.tar.gz", archive)
    say("  Making the DOCCI pictures smaller (this takes a while).")
    rows, count = [], 0
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            name = os.path.basename(member.name)
            if not member.isfile() or name not in descriptions:
                continue
            split, text = descriptions[name]
            path = os.path.join(folder, name)
            if have(path) or smaller(tar.extractfile(member).read(), path):
                rows.append({"picture": path, "question": DETAILED, "answer": clean(text), "split": split})
            count += 1
            if count % 1000 == 0:
                say(f"    {count} pictures done")
    if not KEEP_DOWNLOADS:
        os.remove(archive)                                 # the small copies are kept; 7.6 GB freed
    return rows


def prepare_vizwiz_captions(source, data_dir, work, cap):
    """VizWiz Captions: photos taken by blind people with one-sentence descriptions (CC BY 4.0; the lmms-lab copy on
    Hugging Face, its "val" part, which has the descriptions)."""
    rows = []
    files = hf_parquet_files("lmms-lab/VizWiz-Caps", r"^data/val-")
    for number, name in enumerate(files, 1):
        say(f"  VizWiz Captions part {number} of {len(files)} (about 500 MB).")
        for row in hf_parquet_rows("lmms-lab/VizWiz-Caps", name):
            caption = clean(row.get("caption"))
            if not caption or "quality issues are too severe" in caption.lower():
                continue                                   # VizWiz's "picture too blurry to describe" marker
            path = save_picture(f"vizwiz-{row['image_id']}", (row.get("image") or {}).get("bytes"),
                                os.path.join(data_dir, "vizwiz"))
            if path:
                rows.append({"picture": path, "question": BRIEF, "answer": caption, "split": ""})
    return rows


def as_question(text):
    """A question with a capital first letter and a question mark ("what is the brand" -> "What is the brand?")."""
    text = clean(text)
    if not text:
        return ""
    return text[0].upper() + text[1:] + ("" if text.endswith(("?", ".")) else "?")


def most_common(answers):
    """The answer most of VizWiz's ten people gave; CANNOT_TELL when most said the question cannot be answered."""
    counts = {}
    for a in answers or []:
        a = clean(a)
        if a:
            counts[a.lower()] = counts.get(a.lower(), 0) + 1
    if not counts:
        return ""
    best = max(counts, key=counts.get)
    if best in ("unanswerable", "unsuitable", "unsuitable image"):
        return CANNOT_TELL
    return best[0].upper() + best[1:] + ("" if best.endswith((".", "?", "!")) else ".")


def prepare_vizwiz_vqa(source, data_dir, work, cap):
    """VizWiz VQA: questions blind people asked about their own photos, with the answer most of ten people gave
    (CC BY 4.0, vizwiz.org; the copy with the photos inside on Hugging Face, of which only the photo, question and
    answers are used, never its machine-made columns). "I can't tell" is learned when most people could not answer."""
    rows = []
    files = hf_parquet_files("Multimodal-Fatima/VizWiz_train", r"^data/train-")
    for number, name in enumerate(files, 1):
        say(f"  VizWiz questions part {number} of {len(files)}.")
        for row in hf_parquet_rows("Multimodal-Fatima/VizWiz_train", name, ["image", "filename", "question",
                                                                              "answers"]):
            answer, question = most_common(row.get("answers")), as_question(row.get("question"))
            path = save_picture(f"vizwizq-{row['filename']}", (row.get("image") or {}).get("bytes"),
                                os.path.join(data_dir, "vizwiz_vqa")) if answer and question else None
            if path:
                rows.append({"picture": path, "question": question, "answer": answer, "split": ""})
        if len(rows) >= cap + source.test:
            break
    return rows


def prepare_textcaps(source, data_dir, work, cap):
    """TextCaps: one-sentence descriptions that read out the text in the picture (signs, labels, screens) (CC BY
    4.0, textvqa.org; photos from Open Images, CC BY 2.0)."""
    rows, seen = [], set()
    files = hf_parquet_files("lmms-lab-encoder/TextCaps", r"^data/(train|val)")
    for number, name in enumerate(files, 1):
        say(f"  TextCaps part {number} of {len(files)}.")
        for row in hf_parquet_rows("lmms-lab-encoder/TextCaps", name, ["image", "image_id", "caption_str",
                                                                        "set_name"]):
            caption = row.get("caption_str")
            if isinstance(caption, (list, tuple)):        # the five descriptions of the photo: the first is used
                caption = next((c for c in caption if clean(c)), "")
            caption = clean(caption)
            if row["image_id"] in seen or not caption:
                continue
            seen.add(row["image_id"])
            path = save_picture(f"textcaps-{row['image_id']}", (row.get("image") or {}).get("bytes"),
                                os.path.join(data_dir, "textcaps"))
            if path:
                rows.append({"picture": path, "question": READ_TEXT, "answer": caption[:1].upper() + caption[1:]
                             + ("" if caption.endswith((".", "!", "?")) else "."),
                             "split": "test" if row.get("set_name") == "val" else ""})
        if len(rows) >= cap + source.test:
            break
    return rows


def prepare_textvqa(source, data_dir, work, cap):
    """TextVQA: questions about the text in photos, with the answer most of ten people gave (CC BY 4.0; photos from
    Open Images, CC BY 2.0)."""
    rows = []
    files = hf_parquet_files("facebook/textvqa", r"^textvqa/train/", revision="refs/convert/parquet")
    for number, name in enumerate(files, 1):
        say(f"  TextVQA part {number} of {len(files)}.")
        for row in hf_parquet_rows("facebook/textvqa", name, ["image", "question_id", "question", "answers"],
                                   revision="refs/convert/parquet"):
            answer, question = most_common(row.get("answers")), as_question(row.get("question"))
            path = save_picture(f"textvqa-{row['question_id']}", (row.get("image") or {}).get("bytes"),
                                os.path.join(data_dir, "textvqa")) if answer and question else None
            if path:
                rows.append({"picture": path, "question": question, "answer": answer, "split": ""})
        if len(rows) >= cap + source.test:
            break
    return rows


SPOKEN_START = re.compile(r"^(in|on) (this|the) (image|picture|photo|photograph)\s*,?\s*(i|we)\s+(can\s+)?"
                          r"(see|find|observe)\s+(that\s+)?(there\s+(is|are)\s+)?", re.I)


def tidy_narrative(text):
    """A spoken description without its stock opening ("In this image I can see ..."), starting with a capital."""
    text = SPOKEN_START.sub("", clean(text))
    return text[:1].upper() + text[1:] if text else ""


def prepare_localized_narratives(source, data_dir, work, cap):
    """Localized Narratives: people described Open Images photos aloud, written down (Google; descriptions CC BY
    4.0, photos CC BY 2.0 from Open Images, fetched from its public copy)."""
    say("  Downloading the Localized Narratives descriptions (140 MB).")
    path = os.path.join(work, "ln_open_images_train.jsonl")
    download_file("https://storage.googleapis.com/localized-narratives/annotations/"
                  "open_images_train_v6_captions.jsonl", path)
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            text = tidy_narrative(entry.get("caption"))
            if 12 <= len(text.split()) <= 120:
                entries.append((entry["image_id"], text))
    random.Random(11).shuffle(entries)
    wanted = entries[:int((cap + source.test) * 1.15)]       # some photos no longer download
    say(f"  Fetching {len(wanted)} Open Images photos.")
    items = [(f"{i}.jpg", f"https://open-images-dataset.s3.amazonaws.com/train/{i}.jpg",
              {"question": NARRATE, "answer": t, "split": ""}) for i, t in wanted]
    return fetch_pictures(items, os.path.join(data_dir, "localized_narratives"))


def prepare_cooper_hewitt(source, data_dir, work, cap):
    """Cooper Hewitt, Smithsonian Design Museum: descriptions its cataloguers wrote for accessibility (CC0 words and
    pictures; the biglam copy on Hugging Face). Only descriptions of a good length without catalogue marks."""
    rows = []
    files = hf_parquet_files("biglam/cooper-hewitt-alt-text", r"^data/train-")
    for number, name in enumerate(files, 1):
        say(f"  Cooper Hewitt part {number} of {len(files)}.")
        for row in hf_parquet_rows("biglam/cooper-hewitt-alt-text", name):
            if not row.get("in_target_band") or row.get("has_format_prefix") or row.get("has_crossref") or \
                    row.get("has_artifact"):
                continue
            path = save_picture(f"ch-{row['record_id']}", (row.get("image") or {}).get("bytes"),
                                os.path.join(data_dir, "cooper_hewitt"))
            if path:
                rows.append({"picture": path, "question": ALT_TEXT, "answer": clean(row["description"]),
                             "split": ""})
        if len(rows) >= cap + source.test:
            break
    return rows


def prepare_art_institute(source, data_dir, work, cap):
    """Art Institute of Chicago: alt text written for screen readers, for its public-domain artworks (CC0 data and
    pictures, api.artic.edu). The museum's stock text "A work made of ..." is left out: about 1,700 remain."""
    import requests
    query = {"query": {"bool": {"must": [{"term": {"is_public_domain": True}},
                                         {"exists": {"field": "thumbnail.alt_text"}}],
                                "must_not": [{"match_phrase_prefix": {"thumbnail.alt_text": "A work made of"}}]}},
             "fields": ["id", "image_id", "thumbnail"], "limit": 100}
    items, page = [], 1
    while True:
        r = requests.post("https://api.artic.edu/api/v1/artworks/search", json=dict(query, page=page), timeout=60,
                          headers={"User-Agent": USER_AGENT, "AIC-User-Agent": USER_AGENT})
        data = r.json()
        for art in data.get("data", []):
            alt = clean((art.get("thumbnail") or {}).get("alt_text"))
            if art.get("image_id") and len(alt.split()) >= 4:
                items.append((f"{art['id']}.jpg",
                              f"https://www.artic.edu/iiif/2/{art['image_id']}/full/843,/0/default.jpg",   # the museum's own size
                              {"question": ALT_TEXT, "answer": alt, "split": ""}))
        if page >= data.get("pagination", {}).get("total_pages", 0) or len(items) >= cap + source.test:
            break
        page += 1
        time.sleep(1)
    items = items[:cap + source.test]
    say(f"  Fetching {len(items)} artworks from the Art Institute of Chicago.")
    return fetch_pictures(items, os.path.join(data_dir, "art_institute"), workers=4, pause=0.2)


def prepare_met(source, data_dir, work, cap):
    """The Metropolitan Museum of Art: its highlights (well-known works) that are in the public domain, learned as
    "What artwork is this?" with the title, artist, date and material (CC0, metmuseum.github.io)."""
    import requests
    api = "https://collectionapi.metmuseum.org/public/collection/v1/"
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    ids, offset = [], 0                    # the paged search (v1.1; v1 was retired on 1 October 2026)
    while True:
        page = session.get(api.replace("/v1/", "/v1.1/") + "search", timeout=60,
                           params={"isHighlight": "true", "hasImages": "true", "q": "*", "offset": offset,
                                   "limit": 100}).json()
        found = page.get("objectIDs") or []
        ids += found
        offset += len(found)
        if not found or offset >= page.get("total", 0):
            break
        time.sleep(0.2)
    random.Random(13).shuffle(ids)
    say(f"  Reading {min(len(ids), cap + source.test)} of the Met's highlights.")

    def one(object_id):
        """The fetch item of one object, or None."""
        try:
            time.sleep(0.05)
            obj = session.get(f"{api}objects/{object_id}", timeout=30).json()
        except Exception:  # noqa: BLE001 - left out
            return None
        if not obj.get("isPublicDomain") or not (obj.get("primaryImage") or obj.get("primaryImageSmall")) \
                or not clean(obj.get("title")):
            return None
        parts = [clean(obj["title"])]
        if clean(obj.get("artistDisplayName")):
            parts.append("by " + clean(obj["artistDisplayName"]))
        answer = ", ".join(parts)
        if clean(obj.get("objectDate")):
            answer += ", " + clean(obj["objectDate"])
        answer += "." + (" " + clean(obj["medium"]) + "." if clean(obj.get("medium")) else "")
        return (f"{object_id}.jpg", obj.get("primaryImage") or obj["primaryImageSmall"],
                {"question": ARTWORK, "answer": answer, "split": ""})

    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        items = [i for i in pool.map(one, ids[:int((cap + source.test) * 1.2)]) if i]
    return fetch_pictures(items, os.path.join(data_dir, "met"), workers=4, pause=0.05)


NASA_TOPICS = ("earth from space", "mars", "moon", "astronaut", "galaxy", "nebula", "space shuttle", "rocket launch",
               "international space station", "saturn", "jupiter", "hurricane", "aurora", "telescope", "rover",
               "spacewalk", "sun", "comet", "aircraft", "satellite")


def nasa_answer(title, description):
    """NASA's title and the first sentence or two of its caption, at most about 60 words; "" when it is a credit
    line or names a copyright (a picture NASA did not make)."""
    text = clean(description)
    if "copyright" in text.lower() or "©" in text:
        return ""
    if "---" in text:                      # "SL4-143-4707 (8 Feb. 1974) --- An overhead view ...": the caption
        text = text.split("---", 1)[1].strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    answer = ""
    for sentence in sentences:
        if len((answer + " " + sentence).split()) > 60:
            break
        answer = (answer + " " + sentence).strip()
    title = clean(title)
    if not answer:
        return ""
    return answer if title.lower() in answer.lower() else f"{title}. {answer}"


def prepare_nasa(source, data_dir, work, cap):
    """NASA Image and Video Library: space, Earth and aviation pictures with NASA's captions (NASA pictures are
    generally not under copyright; any naming a copyright are left out), learned as "What does this NASA picture
    show?"."""
    import requests
    items, seen = [], set()
    per_topic = (cap + source.test) // len(NASA_TOPICS) + 5
    for topic in NASA_TOPICS:
        got, page = 0, 1
        while got < per_topic and page <= 5:
            try:
                data = requests.get("https://images-api.nasa.gov/search", timeout=60,
                                    params={"q": topic, "media_type": "image", "page": page, "page_size": 100},
                                    headers={"User-Agent": USER_AGENT}).json()
            except Exception:  # noqa: BLE001 - this topic is skipped
                break
            found = data.get("collection", {}).get("items", [])
            if not found:
                break
            for item in found:
                info, links = (item.get("data") or [{}])[0], item.get("links") or []
                key = info.get("nasa_id")
                answer = nasa_answer(info.get("title"), info.get("description"))
                if not key or key in seen or not links or not answer:
                    continue
                seen.add(key)
                href = links[0]["href"].replace("~thumb.", "~large.")
                items.append((re.sub(r"[^\w.-]", "_", key) + ".jpg", href,
                              {"question": SPACE, "answer": answer, "split": ""}))
                got += 1
                if got >= per_topic:
                    break
            page += 1
            time.sleep(0.5)
    items = items[:int((cap + source.test) * 1.1)]
    say(f"  Fetching {len(items)} NASA pictures.")
    return fetch_pictures(items, os.path.join(data_dir, "nasa"))


EUROPEANA_FREE = ("creativecommons.org/publicdomain/", "creativecommons.org/licenses/by/")


def prepare_europeana(source, data_dir, work, cap):
    """Europeana: objects from museums, libraries and archives all over Europe, with an English description from
    the museum, only those whose licence is CC0, public domain or CC BY (each object's own licence is checked),
    learned as "Tell me about this museum object." Uses Europeana's public demonstration key."""
    import requests
    params = {"wskey": "api2demo", "query": "*", "reusability": "open", "media": "true", "profile": "rich",
              "qf": ["TYPE:IMAGE", "LANGUAGE:en"], "rows": 100, "cursor": "*"}
    items, rounds = [], 0
    while len(items) < (cap + source.test) * 1.2 and rounds < 200:
        try:
            data = requests.get("https://api.europeana.eu/record/v2/search.json", params=params, timeout=60,
                                headers={"User-Agent": USER_AGENT}).json()
        except Exception:  # noqa: BLE001 - stop here with what there is
            break
        for item in data.get("items", []):
            rights = " ".join(item.get("rights") or [])
            text = clean(((item.get("dcDescriptionLangAware") or {}).get("en") or [""])[0])
            url = (item.get("edmIsShownBy") or [""])[0]
            if not any(r in rights for r in EUROPEANA_FREE) or not url or not 10 <= len(text.split()) <= 90:
                continue
            title = clean(((item.get("dcTitleLangAware") or {}).get("en") or item.get("title") or [""])[0])
            answer = text if not title or title.lower() in text.lower() else f"{title}. {text}"
            items.append((re.sub(r"[^\w.-]", "_", item.get("id", str(len(items))))[-80:] + ".jpg", url,
                          {"question": MUSEUM, "answer": answer, "split": ""}))
        params["cursor"] = data.get("nextCursor")
        rounds += 1
        if not params["cursor"]:
            break
        time.sleep(0.5)
    items = items[:int((cap + source.test) * 1.2)]
    say(f"  Fetching {len(items)} pictures from Europeana's museums.")
    return fetch_pictures(items, os.path.join(data_dir, "europeana"), workers=6)


def prepare_wikipedia(source, data_dir, work, cap):
    """Wikipedia: pictures with the alt text written for screen-reader users, English only and at least six words
    (Wikimedia's WIT collection; CC BY-SA 4.0: only with --with-wikipedia). Each file is deleted after use."""
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq
    rows = []
    files = hf_parquet_files("wikimedia/wit_base", r"^data/train-")
    random.Random(17).shuffle(files)
    for number, name in enumerate(files, 1):
        say(f"  Wikipedia file {number} (about 1 GB; {len(rows)} pictures so far).")
        local = hf_hub_download("wikimedia/wit_base", name, repo_type="dataset")
        table = pq.read_table(local, columns=["image", "image_url", "wit_features"]).to_pylist()
        for row in table:
            features = row["wit_features"]
            alt = next((clean(a) for lang, a in zip(features["language"], features["caption_alt_text_description"])
                        if lang == "en" and a and len(a.split()) >= 6), "")
            if not alt:
                continue
            path = save_picture("wit-" + re.sub(r"\W", "_", row["image_url"])[-60:],
                                (row.get("image") or {}).get("bytes"), os.path.join(data_dir, "wikipedia"))
            if path:
                rows.append({"picture": path, "question": ALT_TEXT, "answer": alt, "split": ""})
        del table
        if not KEEP_DOWNLOADS:
            try:
                os.remove(os.path.realpath(local))         # the pictures are kept; the 1 GB file is not
            except OSError:
                pass
        if len(rows) >= cap + source.test:
            break
    return rows


COCO_FREE_LICENCES = (4, 7)       # 4: CC BY 2.0; 7: no known copyright restrictions (COCO's own licence list)


def prepare_coco(source, data_dir, work, cap):
    """COCO Captions: everyday photos with five one-sentence descriptions each (captions CC BY 4.0, cocodataset.org).
    Only photos whose own licence is CC BY 2.0 or "no known copyright restrictions" are used (about 20,800); the
    non-commercial ones are left out. The phiyodr copy on Hugging Face lists each photo's licence."""
    say("  Reading COCO's list of photos and their licences.")
    rows = []
    for name in hf_parquet_files("phiyodr/coco2017", r"^data/"):
        rows += [r for r in hf_parquet_rows("phiyodr/coco2017", name, ["license", "image_id", "coco_url", "captions"])
                 if r.get("license") in COCO_FREE_LICENCES and r.get("captions")]
    random.Random(19).shuffle(rows)
    items = []
    for row in rows[:int((cap + source.test) * 1.1)]:
        caption = clean(row["captions"][0])
        caption = caption[:1].upper() + caption[1:] + ("" if caption.endswith(".") else ".")
        items.append((f"{row['image_id']}.jpg", row["coco_url"],             # COCO serves its photos over http only
                      {"question": BRIEF, "answer": caption, "split": ""}))
    say(f"  Fetching {len(items)} COCO photos.")
    return fetch_pictures(items, os.path.join(data_dir, "coco"))


def prepare_crossmodal(source, data_dir, work, cap):
    """Crossmodal-3600 (Google): 3,600 photos from around the world with carefully written one-sentence English
    descriptions (captions CC BY 4.0; photos CC BY 2.0 from Open Images)."""
    import zipfile
    captions = os.path.join(work, "xm3600-captions.zip")
    download_file("https://google.github.io/crossmodal-3600/web-data/captions.zip", captions)
    english = {}
    with zipfile.ZipFile(captions) as z:
        for line in z.open("captions.jsonl"):
            entry = json.loads(line)
            first = next((clean(c) for c in (entry.get("en") or {}).get("caption", []) if clean(c)), "")
            if first:
                english[entry["image/key"] + ".jpg"] = first
    archive = os.path.join(work, "xm3600-images.tgz")
    say("  Downloading Crossmodal-3600's photos (316 MB).")
    download_file("https://open-images-dataset.s3.amazonaws.com/crossmodal-3600/images.tgz", archive)
    folder = os.path.join(data_dir, "crossmodal")
    os.makedirs(folder, exist_ok=True)
    rows = []
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            name = os.path.basename(member.name)
            if member.isfile() and name in english:
                path = os.path.join(folder, name)
                if have(path) or smaller(tar.extractfile(member).read(), path):
                    rows.append({"picture": path, "question": BRIEF, "answer": english[name], "split": ""})
    if not KEEP_DOWNLOADS:
        os.remove(archive)
    return rows


def digitalnz_items(partner, question, cap, test, min_words=8):
    """Fetch items of one New Zealand collection through DigitalNZ (no key needed): pictures whose record allows
    commercial use and changes, with a description of at least min_words words; (file name, address, row)."""
    import requests
    items, page = [], 1
    while len(items) < (cap + test) * 1.2 and page <= 400:
        try:
            data = requests.get("https://api.digitalnz.org/records.json", timeout=60, headers={"User-Agent": USER_AGENT},
                                params={"and[category][]": "Images", "and[usage][]": ["Use commercially", "Modify"],
                                        "and[content_partner][]": partner, "per_page": 100, "page": page}).json()
        except Exception:  # noqa: BLE001 - stop here with what there is
            break
        found = data.get("search", {}).get("results", [])
        if not found:
            break
        for record in found:
            text, url = clean(record.get("description")), record.get("large_thumbnail_url") or ""
            if url and min_words <= len(text.split()) <= 120:
                items.append((f"{record['id']}.jpg", url, {"question": question, "answer": text, "split": ""}))
        page += 1
        time.sleep(0.3)
    return items


def prepare_canterbury(source, data_dir, work, cap):
    """Canterbury Museum (New Zealand): its staff's descriptions of how each object or photograph looks, for
    pictures marked for commercial use and changes ("no known copyright restrictions" or CC BY), through DigitalNZ."""
    items = digitalnz_items("Canterbury Museum", NARRATE, cap, source.test, min_words=12)
    say(f"  Fetching {len(items)} pictures from Canterbury Museum.")
    return fetch_pictures(items, os.path.join(data_dir, "canterbury"), workers=4, pause=0.1)


def prepare_auckland(source, data_dir, work, cap):
    """Auckland War Memorial Museum (New Zealand): object and photograph records with descriptions, for pictures
    marked for commercial use and changes, through DigitalNZ; learned as "Tell me about this museum object." """
    items = digitalnz_items("Auckland War Memorial Museum Tāmaki Paenga Hira", MUSEUM, cap, source.test)
    say(f"  Fetching {len(items)} pictures from Auckland Museum.")
    return fetch_pictures(items, os.path.join(data_dir, "auckland"), workers=4, pause=0.1)


WELLCOME_FREE = ("pdm", "cc-0", "cc-by")


def prepare_wellcome(source, data_dir, work, cap):
    """Wellcome Collection (UK): prints, drawings and photographs whose catalogue titles describe them ("Galileo
    Galilei. Wood engraving by F.L. Meyer, 1878."), public domain, CC0 or CC BY pictures only; learned as "Tell me
    about this museum object." """
    import gzip
    path = os.path.join(work, "wellcome-images.json.gz")
    say("  Downloading Wellcome Collection's list of pictures (30 MB).")
    download_file("https://data.wellcomecollection.org/catalogue/v2/images.json.gz", path)
    entries = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            image = json.loads(line)
            location = (image.get("locations") or [{}])[0]
            title = clean((image.get("source") or {}).get("title"))
            if (location.get("license") or {}).get("id") in WELLCOME_FREE and 8 <= len(title.split()) <= 80 and \
                    location.get("url", "").endswith("/info.json"):
                entries.append((image["id"], location["url"][:-len("/info.json")] + "/full/!2048,2048/0/default.jpg",
                                title))
    random.Random(23).shuffle(entries)
    items = [(f"{i}.jpg", url, {"question": MUSEUM, "answer": title, "split": ""})
             for i, url, title in entries[:int((cap + source.test) * 1.1)]]
    say(f"  Fetching {len(items)} Wellcome Collection pictures.")
    return fetch_pictures(items, os.path.join(data_dir, "wellcome"), workers=6)


def prepare_concadia(source, data_dir, work, cap):
    """Concadia: about 97,000 pictures from Wikipedia with the alt text written for screen-reader users
    (Wikipedia's text is CC BY-SA 4.0: only with --with-wikipedia; the nirmalendu01 copy on Hugging Face)."""
    rows = []
    files = hf_parquet_files("nirmalendu01/concadia", r"^data/train-")
    for number, name in enumerate(files, 1):
        say(f"  Concadia part {number} of {len(files)}.")
        for index, row in enumerate(hf_parquet_rows("nirmalendu01/concadia", name, ["image", "article_id",
                                                                                     "description_raw"])):
            alt = clean(row.get("description_raw"))
            if len(alt.split()) < 5:
                continue
            path = save_picture(f"concadia-{number}-{index}", (row.get("image") or {}).get("bytes"),
                                os.path.join(data_dir, "concadia"))
            if path:
                rows.append({"picture": path, "question": ALT_TEXT, "answer": alt, "split": ""})
        if len(rows) >= cap + source.test:
            break
    return rows


PACKS_URL = "https://github.com/mark-getbraille/toolkit-models/releases/download/training-data/"


def prepare_pack(source, data_dir, work, cap):
    """A ready-made pack built on GitHub's machines and published in the kit's own repository (packs/build_packs.py):
    its parts are downloaded, joined, checked against packs.json's SHA-256 and unpacked; a row with "url" instead of a
    picture (COCO's photos, which may not be copied) is fetched from its own website."""
    import hashlib
    import requests
    import zipfile
    manifest = requests.get(PACKS_URL + "packs.json", timeout=60, headers={"User-Agent": USER_AGENT}).json()
    if source.key not in manifest:
        raise RuntimeError("this pack is not published yet")
    info = manifest[source.key]
    archive = os.path.join(work, f"{source.key}.zip")
    if not (os.path.exists(archive) and os.path.getsize(archive) == info["size"]):
        with open(archive + ".part", "wb") as joined:
            for number, name in enumerate(info["files"], 1):
                piece = os.path.join(work, name + ".download")
                say(f"  Downloading the {source.key} pack, part {number} of {len(info['files'])}.")
                download_file(PACKS_URL + name, piece)
                with open(piece, "rb") as f:
                    while True:
                        block = f.read(1 << 20)
                        if not block:
                            break
                        joined.write(block)
                os.remove(piece)
        os.replace(archive + ".part", archive)
    digest = hashlib.sha256()
    with open(archive, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    if digest.hexdigest() != info["sha256"]:
        os.remove(archive)
        raise RuntimeError("the pack's download was damaged; it is downloaded again the next time")
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows, to_fetch = [], []
    with zipfile.ZipFile(archive) as z:
        listed = [json.loads(line) for line in z.read("rows.jsonl").decode("utf-8").splitlines() if line.strip()]
        # Where each picture is from: a row without a place (a translated twin) takes that of its picture's other rows.
        known = {r.get("file") or r.get("url"): place_fields(r) for r in listed if r.get("place")}
        random.Random(29).shuffle(listed)
        for index, row in enumerate(listed[:int((cap + source.test) * 1.15)]):
            # A machine-translated twin is for training only, never for the test (split "no-test").
            base = {"question": row["question"], "answer": clean(row["answer"]),
                    "split": "no-test" if row.get("translated") else ""}
            if row.get("child"):                     # a picture of a child: never used to make pictures
                base["child"] = True
            base.update(place_fields(row) or known.get(row.get("file") or row.get("url"), {}))
            if row.get("file"):
                path = os.path.join(folder, os.path.basename(row["file"]))
                if have(path) or smaller(z.read(row["file"]), path):       # a training copy and a large copy
                    rows.append(dict(base, picture=path))
            elif row.get("url"):
                to_fetch.append((f"{source.key}-{index}.jpg", row["url"], base))
        with open(os.path.join(folder, "CREDITS.txt"), "wb") as out:
            out.write(z.read("CREDITS.txt"))
    if not KEEP_DOWNLOADS:
        os.remove(archive)
    if to_fetch:
        say(f"  Fetching {len(to_fetch)} pictures for the {source.key} pack from their own website.")
        rows += fetch_pictures(to_fetch, folder)
    return rows


# ----------------------------------------------------------------- where in the world a picture is from

# A row may carry "place" (a short place name, most specific first, ending with the country in English: "Kyoto,
# Japan") and "place_kind": "photo" (where the photo was taken; the same as none), "origin" (where an object was
# made) or "depicted" (the place a picture shows). Places come only from each collection's own records (packs/
# places.py builds them for the packs), never from a guess. train.py teaches the describer a few "Which country might
# this photo be from?" and "Where was this object made?" answers from them; train_pictures.py starts a description
# with its place, so a picture-making add-on learns what places look like.
PLACE_KINDS = ("photo", "origin", "depicted")
# Collections whose photos show the place itself (streets, homes, shops, landscapes), so a describer may learn to
# say which country a photo might be from; "own" is the person's own pictures with a place.txt.
PLACE_VISIBLE = {"dollar_street", "geode", "ptl_crossings", "uroac_crossings", "walkway_dhaka", "outdoor_navigation",
                 "seoul_sidewalks", "open_images_street", "commons", "lila_camera_traps", "grocery_store", "own"}
# Places that are parts of the world, not countries (GeoDE's regions and the like).
PLACE_REGIONS = {"africa", "the americas", "americas", "east asia", "europe", "south-east asia", "southeast asia",
                 "west asia", "asia", "oceania", "north america", "south america", "eastern north america",
                 "central america", "middle east", "southern africa"}
# Country names said with "the" ("taken in the USA").
THE_COUNTRIES = {"usa", "uk", "netherlands", "philippines", "united arab emirates", "czech republic",
                 "dominican republic", "democratic republic of the congo", "republic of the congo",
                 "central african republic", "bahamas", "gambia", "maldives", "solomon islands", "marshall islands",
                 "comoros", "seychelles", "vatican city", "united states", "united kingdom", "americas"}


def place_fields(row):
    """{"place": ..., "place_kind": ...} of a row (only what it has, tidied; "photo" is left out as the default),
    or {}."""
    place = clean(row.get("place")).strip(" ,.")
    if not place:
        return {}
    kind = clean(row.get("place_kind")).lower()
    return {"place": place, "place_kind": kind} if kind in PLACE_KINDS[1:] else {"place": place}


def place_country(place):
    """The country (or part of the world) of a place: its last part ("Kyoto, Japan" -> "Japan")."""
    return clean(place).split(",")[-1].strip(" .")


def is_region(place):
    """True when a place is a part of the world rather than a country ("East Asia")."""
    return place_country(place).lower() in PLACE_REGIONS


def place_words(place):
    """A place as it follows "in": "the USA", "the Netherlands", "Kyoto, Japan", "East Asia"."""
    place = clean(place).strip(" ,.")
    return ("the " + place) if place.lower() in THE_COUNTRIES else place


# ----------------------------------------------------------------- big archives downloaded by the kit itself

def unpack(archive, folder):
    """Unpack a zip, RAR or 7z archive into folder: zips with Python, the others with the tar program built into
    Windows 10 and 11 (bsdtar, which reads RAR and 7z); raises RuntimeError when that is not possible."""
    import subprocess
    import zipfile
    os.makedirs(folder, exist_ok=True)
    if archive.lower().endswith(".zip"):
        zipfile.ZipFile(archive).extractall(folder)
        return
    tar = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "tar.exe")
    if not os.path.exists(tar):
        import shutil
        tar = shutil.which("bsdtar") or shutil.which("tar")
    done = subprocess.run([tar, "-xf", archive, "-C", folder], capture_output=True, text=True,
                          creationflags=0x08000000 if os.name == "nt" else 0)
    if done.returncode != 0:
        raise RuntimeError("the archive could not be unpacked: " + (done.stderr or "").strip()[:200])


def pictures_in(folder):
    """Every picture file under folder (with its path), in a fixed order."""
    found = []
    for base, _dirs, files in os.walk(folder):
        for name in files:
            if name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                found.append(os.path.join(base, name))
    return sorted(found)


def archive_collection(source, data_dir, work, url, archive_name, label_of, cap, seed, place="", place_kind=""):
    """Download a big archive once (kept in the downloads folder, which is the picture library's), unpack it, turn
    each picture whose label_of(path) gives (question, answer) into a training copy and a full-size copy, and remove
    the unpacked folder again. Pictures are picked evenly from every label, at most cap + test of them. place and
    place_kind: where all its pictures are from, when the collection's record says so (see place_fields)."""
    archive = os.path.join(work, archive_name)
    say(f"  Downloading {archive_name} (kept for good in the picture library; it is large and resumes if stopped).")
    download_file(url, archive)
    unpacked = os.path.join(work, archive_name + ".unpacked")
    if not os.path.isdir(unpacked) or not os.listdir(unpacked):
        say("  Unpacking it (this takes a while).")
        unpack(archive, unpacked)
    by_label = {}
    for path in pictures_in(unpacked):
        got = label_of(os.path.relpath(path, unpacked))
        if got:
            by_label.setdefault(got, []).append(path)
    if not by_label:
        raise RuntimeError("no labelled pictures were found in the archive")
    want = cap + source.test
    per_label = max(1, want // len(by_label))
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows = []
    for (question, answer), paths in sorted(by_label.items()):
        random.Random(f"{seed}-{answer}").shuffle(paths)
        for path in paths[:per_label]:
            target = os.path.join(folder, re.sub(r"[^\w.-]", "_", os.path.relpath(path, unpacked))[-120:])
            target = os.path.splitext(target)[0] + ".jpg"
            with open(path, "rb") as f:
                data = f.read()
            if have(target) or smaller(data, target):
                rows.append({"picture": target, "question": question, "answer": answer, "split": "",
                             **place_fields({"place": place, "place_kind": place_kind})})
    import shutil
    shutil.rmtree(unpacked, ignore_errors=True)          # the archive stays; its unpacked copy is not needed
    say(f"  {len(rows)} pictures from {len(by_label)} kinds.")
    return rows


MEAT_QUESTION = "Is this meat still safe to cook?"


def meat_label(path):
    """Fresh or spoiled, from MeatScan's folder and file names; None for other files (masks, notes)."""
    lower = path.lower().replace("\\", "/")
    if "_seg" in lower or "mask" in lower:
        return None
    if "spoil" in lower or "rotten" in lower or "bad" in lower.split("/")[0]:
        return (MEAT_QUESTION, "No: this meat looks spoiled. Do not eat it.")
    if "fresh" in lower:
        return (MEAT_QUESTION, "Yes: this meat looks fresh.")
    return None


def prepare_meatscan(source, data_dir, work, cap):
    """MeatScan (Zenodo 16764338, CC BY 4.0): 11,000 photos of beef from markets in Ghana, fresh or spoiled: "Is this
    meat still safe to cook?". A 25 GB archive, downloaded once by the kit (too big for the GitHub packs)."""
    return archive_collection(source, data_dir, work,
                              "https://zenodo.org/api/records/16764338/files/MeatScan_Dataset.rar/content",
                              "MeatScan_Dataset.rar", meat_label, cap, 31,
                              place="Ghana")             # "captured in real-world Ghanaian environments"


def ghana_label(path):
    """A Ghanaian note or coin from its folder name ("5_Cedi_note", "50_pesewas_coin")."""
    m = re.search(r"(\d+)_(cedi|pesewas?)_(note|coin)", path.lower())
    if not m:
        return None
    amount, unit, kind = int(m.group(1)), m.group(2), m.group(3)
    unit = "cedi" if unit == "cedi" else "pesewa"
    return ("Which banknote or coin is this?", f"This is a Ghanaian {amount} {unit} {kind}.")


def prepare_ghana_money(source, data_dir, work, cap):
    """Ghana's banknotes and coins (Mendeley Data vws5r8mj4w, CC BY 4.0): "Which banknote or coin is this?"."""
    import requests
    files = requests.get("https://data.mendeley.com/public-api/datasets/vws5r8mj4w/files?folder_id=root&version=1",
                         timeout=60, headers={"User-Agent": USER_AGENT}).json()
    return archive_collection(source, data_dir, work, files[0]["content_details"]["download_url"],
                              "Ghana_Cedis_Currency.rar", ghana_label, cap, 32,
                              place="Ghana", place_kind="origin")       # Ghana's own money


SOURCES = [
    Source("docci", "DOCCI: photos described in about 120 words",
           "CC BY 4.0, descriptions and photos (google.github.io/docci)",
           "DOCCI by Google, CC BY 4.0, https://google.github.io/docci/", "permissive", 9647, 25, prepare_docci,
           "7.6 GB"),
    Source("vizwiz_captions", "VizWiz Captions: photos taken by blind people, one sentence each",
           "CC BY 4.0 (vizwiz.org)",
           "VizWiz-Captions (Gurari et al., 2020), CC BY 4.0, https://vizwiz.org", "permissive", 2500, 10,
           prepare_vizwiz_captions, "3.5 GB"),
    Source("vizwiz_vqa", "VizWiz questions: what blind people asked about their own photos",
           "CC BY 4.0 (vizwiz.org)",
           "VizWiz VQA (Gurari et al., 2018), CC BY 4.0, https://vizwiz.org", "permissive", 3500, 10,
           prepare_vizwiz_vqa, "up to 4 GB"),
    Source("textcaps", "TextCaps: descriptions that read out the text in the picture",
           "CC BY 4.0 descriptions (textvqa.org); Open Images photos, CC BY 2.0",
           "TextCaps (Sidorov et al., 2020), CC BY 4.0, https://textvqa.org/textcaps; photos from Open Images",
           "permissive", 2000, 10, prepare_textcaps, "up to 2 GB"),
    Source("textvqa", "TextVQA: questions about the text in photos",
           "CC BY 4.0 (textvqa.org); Open Images photos, CC BY 2.0",
           "TextVQA (Singh et al., 2019), CC BY 4.0, https://textvqa.org; photos from Open Images", "permissive",
           1500, 10, prepare_textvqa, "up to 2 GB"),
    Source("localized_narratives", "Localized Narratives: photos described aloud by people",
           "CC BY 4.0 descriptions (google.github.io/localized-narratives); Open Images photos, CC BY 2.0",
           "Localized Narratives (Pont-Tuset et al., 2020), CC BY 4.0; photos from Open Images, CC BY 2.0",
           "permissive", 2500, 10, prepare_localized_narratives, "about 1 GB"),
    Source("cooper_hewitt", "Cooper Hewitt, Smithsonian Design Museum: descriptions written for accessibility",
           "CC0, words and pictures (Smithsonian Open Access)",
           "Cooper Hewitt, Smithsonian Design Museum, CC0 (via biglam/cooper-hewitt-alt-text)", "permissive", 2500,
           10, prepare_cooper_hewitt, "up to 3 GB"),
    Source("art_institute", "Art Institute of Chicago: alt text written for screen readers",
           "CC0, data and public-domain pictures (api.artic.edu)",
           "Art Institute of Chicago, CC0, https://api.artic.edu", "permissive", 1700, 20, prepare_art_institute,
           "about 200 MB"),
    Source("met", "The Metropolitan Museum of Art: its best-known works by name",
           "CC0 (Met Open Access)", "The Metropolitan Museum of Art Open Access, CC0, https://metmuseum.github.io",
           "permissive", 1200, 5, prepare_met, "about 200 MB"),
    Source("nasa", "NASA: space, Earth and aviation pictures with NASA's captions",
           "Generally not under copyright (nasa.gov/nasa-brand-center/images-and-media); copyrighted ones left out",
           "NASA Image and Video Library, https://images.nasa.gov", "permissive", 800, 5, prepare_nasa,
           "about 150 MB"),
    Source("europeana", "Europeana: objects from museums and archives across Europe",
           "Each object's own licence: only CC0, public domain or CC BY are used (europeana.eu)",
           "Europeana and its partner museums, CC0 / public domain / CC BY per object, https://www.europeana.eu",
           "permissive", 1000, 5, prepare_europeana, "about 200 MB"),
    Source("coco", "COCO: everyday photos with one-sentence descriptions",
           "CC BY 4.0 descriptions (cocodataset.org); only photos under CC BY 2.0 or no known copyright",
           "COCO Captions (Chen et al., 2015), CC BY 4.0, https://cocodataset.org; Flickr photos under CC BY 2.0 or "
           "no known copyright restrictions", "permissive", 2000, 10, prepare_coco, "about 1 GB"),
    Source("crossmodal", "Crossmodal-3600: photos from around the world, carefully described",
           "CC BY 4.0 descriptions; Open Images photos, CC BY 2.0 (google.github.io/crossmodal-3600)",
           "Crossmodal-3600 (Thapliyal et al., 2022), CC BY 4.0, https://google.github.io/crossmodal-3600/",
           "permissive", 2000, 10, prepare_crossmodal, "316 MB"),
    Source("canterbury", "Canterbury Museum, New Zealand: how each object and photograph looks",
           "Each record's own licence: only those marked for commercial use and changes (DigitalNZ)",
           "Canterbury Museum, Christchurch, via DigitalNZ, https://digitalnz.org", "permissive", 2000, 10,
           prepare_canterbury, "about 300 MB"),
    Source("auckland", "Auckland War Memorial Museum, New Zealand: object and photograph records",
           "Each record's own licence: only those marked for commercial use and changes (DigitalNZ)",
           "Auckland War Memorial Museum Tāmaki Paenga Hira, via DigitalNZ, https://digitalnz.org", "permissive",
           1000, 5, prepare_auckland, "about 200 MB"),
    Source("wellcome", "Wellcome Collection, UK: prints, drawings and photographs by title",
           "Public domain, CC0 or CC BY pictures only; catalogue text CC0 (wellcomecollection.org)",
           "Wellcome Collection, London, https://wellcomecollection.org", "permissive", 1000, 5, prepare_wellcome,
           "about 200 MB"),
    Source("smithsonian", "Smithsonian museums: accessibility descriptions and gallery labels (ready-made pack)",
           "CC0, words and pictures (Smithsonian Open Access)",
           "Smithsonian Institution Open Access, CC0, https://www.si.edu/openaccess", "permissive", 2000, 10,
           prepare_pack, "about 300 MB"),
    Source("coco_questions", "Questions about everyday photos, answered with the reason (ready-made pack)",
           "VQAv2 CC BY 4.0 and A-OKVQA Apache-2.0; COCO photos under CC BY 2.0 or no known copyright only",
           "VQAv2 (Goyal et al., 2017), CC BY 4.0; A-OKVQA (Schwenk et al., 2022), Apache-2.0; photos from COCO",
           "permissive", 2500, 10, prepare_pack, "about 400 MB"),
    Source("commons", "Wikimedia Commons: featured and quality pictures with their captions (ready-made pack)",
           "Captions CC0; pictures CC0, public domain or CC BY (each credited in the pack's CREDITS.txt)",
           "Wikimedia Commons contributors (captions CC0; pictures credited in CREDITS.txt), "
           "https://commons.wikimedia.org", "permissive", 2000, 10, prepare_pack, "about 300 MB"),
    Source("tepapa", "Te Papa, Museum of New Zealand: object and photograph records (ready-made pack)",
           "Record text CC BY 4.0; pictures CC BY 4.0 or no known copyright (credited in CREDITS.txt)",
           "Museum of New Zealand Te Papa Tongarewa, CC BY 4.0, https://collections.tepapa.govt.nz", "permissive",
           1000, 5, prepare_pack, "about 150 MB"),
    Source("inaturalist", "iNaturalist: plants, mushrooms, insects, birds and other animals, named (ready-made pack)",
           "Photos CC0 or CC BY (each photographer credited in the pack's CREDITS.txt)",
           "iNaturalist contributors (photos CC0 or CC BY, credited in CREDITS.txt), https://www.inaturalist.org",
           "permissive", 4000, 10, prepare_pack, "about 600 MB"),
    Source("nutrition5k", "Nutrition5k: plates of food with every ingredient weighed (ready-made pack)",
           "CC BY 4.0 (Google)", "Nutrition5k (Thames et al., 2021), Google, CC BY 4.0", "permissive", 2500, 10,
           prepare_pack, "about 200 MB"),
    Source("fresh_rotten", "Fresh or rotten fruit (ready-made pack)", "CC BY 4.0 (Sultana et al.)",
           "Fresh and rotten fruits (Sultana et al.), CC BY 4.0", "permissive", 2000, 10, prepare_pack, "about 200 MB"),
    Source("banknotes", "Indian and Thai banknotes, photographed for blind users (ready-made pack)",
           "CC BY 4.0 (Mendeley Data)", "Indian and Thai banknotes dataset, Mendeley Data 2kfz5yc7pt, CC BY 4.0",
           "permissive", 1500, 10, prepare_pack, "about 200 MB"),
    Source("cattle_health", "Cattle health: foot-and-mouth and lumpy skin disease (ready-made pack)",
           "CC BY 4.0 (Mendeley Data)", "FMD-LSD beef cattle dataset, Mendeley Data ggpwpscjvm, CC BY 4.0",
           "permissive", 1200, 10, prepare_pack, "about 150 MB"),
    Source("clothing", "Clothing: what each item is (ready-made pack)", "CC0", "Clothing dataset by Alexey Grigorev, CC0",
           "permissive", 2000, 10, prepare_pack, "about 200 MB"),
    Source("japan_search", "Japan Search: Japanese museums and archives, described in Japanese (ready-made pack)",
           "CC0, public domain or CC BY pictures; descriptions under each database's open terms (jpsearch.go.jp/policy)",
           "Japan Search (National Diet Library) and its partner databases, https://jpsearch.go.jp", "permissive",
           1500, 10, prepare_pack, "about 400 MB"),
    Source("ksamsok", "Swedish museums (K-samsök): what each picture shows, in Swedish (ready-made pack)",
           "CC0, public domain or CC BY pictures; CC0 records (kulturarvsdata.se)",
           "Swedish museums via K-samsök (Swedish National Heritage Board), https://kulturarvsdata.se", "permissive",
           2500, 10, prepare_pack, "about 600 MB"),
    Source("rijksmuseum", "Rijksmuseum: scene descriptions in Dutch (ready-made pack)",
           "CC0 or public domain (data.rijksmuseum.nl/policy)", "Rijksmuseum, Amsterdam, CC0, https://data.rijksmuseum.nl",
           "permissive", 3000, 10, prepare_pack, "about 1.5 GB"),
    Source("stair_captions", "STAIR Captions: everyday photos described in Japanese (ready-made pack)",
           "CC BY 4.0 captions; COCO photos under CC BY 2.0 or no known copyright only",
           "STAIR Captions (Yoshikawa et al., 2017), CC BY 4.0; photos from COCO", "permissive", 2500, 10,
           prepare_pack, "about 400 MB (photos fetched from COCO)"),
    Source("coco_cn", "COCO-CN: everyday photos described in Chinese by people (ready-made pack)",
           "MIT; COCO photos under CC BY 2.0 or no known copyright only",
           "COCO-CN (Li et al., 2019), MIT; photos from COCO", "permissive", 2000, 10, prepare_pack,
           "about 300 MB (photos fetched from COCO)"),
    Source("taiwan_pills", "Pills and capsules: name, colour, shape, size and imprint (Taiwan FDA, ready-made pack)",
           "Open Government Data License, Taiwan, v1.0 (data.gov.tw/license)",
           "Taiwan Food and Drug Administration, drug appearance open data, Open Government Data License v1.0",
           "permissive", 4000, 20, prepare_pack, "about 1 GB"),
    Source("pharmassist", "Medicine blister packs: which medicine (ready-made pack)", "CC BY 4.0 (Mendeley Data zbnhmbbymd)",
           "Pharmassist dataset, Mendeley Data zbnhmbbymd, CC BY 4.0", "permissive", 2050, 15, prepare_pack,
           "about 500 MB"),
    Source("mediseg", "Several pills together: how many and which (MEDISEG, ready-made pack)",
           "CC BY 4.0 (figshare 28574786)", "MEDISEG (figshare 28574786), CC BY 4.0", "permissive", 4000, 20,
           prepare_pack, "about 300 MB"),
    Source("open_images_food", "Everyday food photos: what food, how eggs are cooked, frozen or not (ready-made pack)",
           "CC BY 4.0 labels; photos CC BY 2.0, each author credited",
           "Open Images V7 (Google), CC BY 4.0 labels; photos by their Flickr authors, CC BY 2.0", "permissive",
           6000, 20, prepare_pack, "about 1.5 GB"),
    Source("grocery_store", "Shop shelves: fruit, vegetables and packaged food (ready-made pack)", "MIT",
           "Grocery Store Dataset (Klasson, Zhang and Kjellstrom, 2019), MIT", "permissive", 5421, 20, prepare_pack,
           "about 600 MB"),
    Source("fish_eyes", "Fish freshness from the eye, eight kinds of fish (ready-made pack)",
           "CC BY 4.0 (Mendeley Data xzyx7pbr3w)", "Freshness of the Fish Eyes, Mendeley Data xzyx7pbr3w, CC BY 4.0",
           "permissive", 4390, 20, prepare_pack, "about 500 MB"),
    Source("commons_food", "Cooked eggs, steaks, frozen and spoiled food from Wikimedia Commons (ready-made pack)",
           "CC0, public domain or CC BY, each author credited", "Wikimedia Commons authors, credited in ATTRIBUTION.txt",
           "permissive", 1500, 10, prepare_pack, "about 300 MB"),
    Source("meatscan", "MeatScan: fresh or spoiled beef (a 25 GB download, kept in the picture library)",
           "CC BY 4.0 (zenodo.org/records/16764338)",
           "MeatScan (Zenodo 16764338), CC BY 4.0, https://zenodo.org/records/16764338", "permissive", 4000, 20,
           prepare_meatscan, "25 GB, once"),
    Source("ghana_money", "Ghana's banknotes and coins (a 2 GB download)", "CC BY 4.0 (Mendeley Data vws5r8mj4w)",
           "Ghana Cedis currency dataset, Mendeley Data vws5r8mj4w, CC BY 4.0", "permissive", 1500, 10,
           prepare_ghana_money, "2 GB, once"),
    Source("eggs", "Eggs: fresh, no longer fully fresh or rotten, five kinds (ready-made pack)",
           "CC BY 4.0 (Mendeley Data 49msr3ksxj)", "Egg variety and freshness dataset, Mendeley Data 49msr3ksxj, CC BY 4.0",
           "permissive", 3000, 15, prepare_pack, "about 400 MB"),
    Source("beef", "Beef: fresh, and five days after it was bought (ready-made pack)",
           "CC BY 4.0 (Mendeley Data wvhkpppddp)", "Fresh and non-fresh beef images, Mendeley Data wvhkpppddp, CC BY 4.0",
           "permissive", 60, 6, prepare_pack, "about 20 MB"),
    Source('open_images_objects', 'Household objects: what is in the picture, and is there a ... (ready-made pack)',
           'CC BY 4.0 labels; photos CC BY 2.0, each author credited',
           'Open Images V7 (Google), CC BY 4.0 labels; photos by their Flickr authors, CC BY 2.0', "permissive", 6000, 20, prepare_pack, 'about 1.5 GB'),
    Source('orbit', "ORBIT: blind people's own videos of their things: what it is, where it is, is it a good photo (ready-made pack)",
           'CC BY 4.0 (City, University of London figshare 14294597)',
           'ORBIT dataset (Massiceti et al., 2021), City, University of London, CC BY 4.0', "permissive", 5000, 20, prepare_pack, 'about 1 GB'),
    Source('core50', 'CORe50: hand-held everyday objects (ready-made pack)',
           'CC BY 4.0',
           'CORe50 (Lomonaco and Maltoni, 2017), CC BY 4.0', "permissive", 2000, 10, prepare_pack, 'about 200 MB'),
    Source('lila_camera_traps', 'Wildlife camera traps: which animal, day and night (ready-made pack)',
           'CDLA-Permissive-1.0 (lila.science)',
           'LILA BC camera-trap collections (lila.science), CDLA-Permissive 1.0', "permissive", 5000, 20, prepare_pack, 'about 1.5 GB'),
    Source('gbif_species', 'Species of the world: birds, mammals, fish, insects, plants and fungi (GBIF, ready-made pack)',
           'Each photo CC0, public domain or CC BY, photographer credited',
           'Photographers and institutions publishing through GBIF (gbif.org), credited in ATTRIBUTION.txt', "permissive", 5000, 20, prepare_pack, 'about 1.5 GB'),
    Source('commons_breeds', 'Breeds of dogs, cats, horses, cattle, sheep and other farm animals (Wikimedia Commons, ready-made pack)',
           'CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2000, 10, prepare_pack, 'about 500 MB'),
    Source('textocr', 'Reading text in everyday photos (TextOCR, ready-made pack)',
           'CC BY 4.0 words; photos CC BY 2.0, each author credited',
           'TextOCR (Singh et al., 2021), CC BY 4.0; photos from Open Images by their Flickr authors, CC BY 2.0', "permissive", 5000, 20, prepare_pack, 'about 1.5 GB'),
    Source('coco_text', 'Reading text in everyday photos (COCO-Text, ready-made pack)',
           'CC BY 4.0; COCO photos under CC BY 2.0 or no known copyright only',
           'COCO-Text v2 (Veit et al., 2016), CC BY 4.0; photos from COCO', "permissive", 1200, 10, prepare_pack, 'about 200 MB (photos fetched from COCO)'),
    Source('cord', 'Receipts: the total, the items and prices, the change (CORD, ready-made pack)',
           'CC BY 4.0',
           'CORD v2 (Park et al., 2019, NAVER Clova), CC BY 4.0', "permissive", 1000, 15, prepare_pack, 'about 200 MB'),
    Source('doclaynet', 'Document pages: what kind of document, the title, the text (DocLayNet, ready-made pack)',
           'CDLA-Permissive-1.0',
           'DocLayNet (Pfitzmann et al., 2022, IBM), CDLA-Permissive 1.0', "permissive", 4000, 20, prepare_pack, 'about 800 MB'),
    Source('plotqa', 'Charts: what the chart shows and its values (PlotQA, ready-made pack)',
           'CC BY 4.0',
           'PlotQA (Methani et al., 2020), CC BY 4.0, charts drawn from World Bank and other open data', "permissive", 4000, 20, prepare_pack, 'about 600 MB'),
    Source('loc_letters', 'Handwritten letters and diaries read by volunteers (Library of Congress By the People, ready-made pack)',
           'Transcriptions CC0; pages with no known copyright restrictions',
           'Library of Congress, By the People transcriptions (CC0), from collections with no known copyright restrictions', "permissive", 5000, 20, prepare_pack, 'about 1.5 GB'),
    Source('ptl_crossings', 'Pedestrian lights and which way the crossing goes (ImVisible, ready-made pack)',
           'MIT (github.com/samuelyu2002/ImVisible)',
           'ImVisible pedestrian traffic light dataset (Yu et al.), MIT', "permissive", 3000, 20, prepare_pack, 'about 600 MB'),
    Source('uroac_crossings', 'Pedestrian lights and crossings, day and night (UrOAC, ready-made pack)',
           'CC BY 4.0 (Mendeley Data fcrmp92ckn)',
           'UrOAC urban obstacles and crossings dataset, Mendeley Data fcrmp92ckn, CC BY 4.0', "permissive", 1000, 10, prepare_pack, 'about 300 MB'),
    Source('open_images_street', 'Getting around: stairs, lifts, doors, ramps, crossings, bus stops (ready-made pack)',
           'CC BY 4.0 labels; photos CC BY 2.0, each author credited',
           'Open Images V7 (Google), CC BY 4.0 labels; photos by their Flickr authors, CC BY 2.0', "permissive", 4000, 20, prepare_pack, 'about 1 GB'),
    Source('walkway_dhaka', 'Footpath obstacles and vehicles, where they are (Dhaka, ready-made pack)',
           'CC BY 4.0 (Mendeley Data m68g3h7p87)',
           'Walkway obstacle dataset, Dhaka, Mendeley Data m68g3h7p87, CC BY 4.0', "permissive", 1000, 10, prepare_pack, 'about 200 MB'),
    Source('outdoor_navigation', 'Pavements, ramps and crossings ahead (Bucharest, ready-made pack)',
           'CC BY 4.0 (Zenodo 14043015)',
           'Outdoor navigation dataset for visually impaired people, Zenodo 14043015, CC BY 4.0', "permissive", 700, 10, prepare_pack, 'about 150 MB'),
    Source('seoul_sidewalks', 'Pavements: condition, width and slope (Seoul, ready-made pack)',
           'CC0 (Zenodo 22908353)',
           'Seoul sidewalk accessibility dataset, Zenodo 22908353, CC0', "permissive", 514, 10, prepare_pack, 'about 200 MB'),
    Source('dollar_street', 'Dollar Street: homes and everyday things in about 60 countries (ready-made pack)',
           'CC BY 4.0 (gapminder.org/dollar-street)',
           'Dollar Street by Gapminder, CC BY 4.0, each photographer credited', "permissive", 5000, 20, prepare_pack, 'about 1.5 GB'),
    Source('geode', 'GeoDE: everyday objects and places from six world regions (ready-made pack)',
           'CC BY',
           'GeoDE (Ramaswamy et al., 2023, Princeton), CC BY', "permissive", 4000, 20, prepare_pack, 'about 800 MB'),
    Source('oi_expressions', 'Facial expressions, gestures and body language (Open Images, ready-made pack)',
           'CC BY 4.0 labels; photos CC BY 2.0, each author credited',
           'Open Images V7 (Google), CC BY 4.0 labels; photos by their Flickr authors, CC BY 2.0', "permissive", 8000, 20, prepare_pack, 'about 2 GB'),
    Source('commons_expressions', 'Facial expressions and gestures (Wikimedia Commons, ready-made pack)',
           'CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1500, 10, prepare_pack, 'about 400 MB'),
    Source('bice_gestures', 'Hand gestures seen from your own point of view (BiCE-HG, ready-made pack)',
           'CC BY 4.0 (University of Sheffield, doi 10.15131/shef.data.32374137)',
           'BiCE-HG hand gesture dataset, University of Sheffield, CC BY 4.0', "permissive", 1430, 10, prepare_pack, 'about 300 MB'),
    Source('vqa_expressions', 'Questions people asked about faces and feelings in photos (VQA and Visual Dialog, ready-made pack)',
           'CC BY 4.0; COCO photos under CC BY 2.0 or no known copyright only',
           'VQA v2 and Visual Dialog, CC BY 4.0; photos from COCO', "permissive", 1200, 10, prepare_pack, 'about 200 MB (photos fetched from COCO)'),
    Source('xm3600', 'Crossmodal-3600: 3,600 photos from around the world described by native speakers in 35 languages (ready-made pack)',
           'CC BY 4.0 captions; photos CC BY 2.0, each author credited',
           'Crossmodal-3600 (Thapliyal et al., 2022, Google), CC BY 4.0; photos from Open Images by their Flickr authors, CC BY 2.0', "permissive", 3600, 20, prepare_pack, 'about 1 GB'),
    Source('europeana_fi', 'Finnish museums: photos with their content descriptions, in Finnish with English (Europeana, ready-made pack)',
           'Record text CC0; pictures CC BY 4.0, CC0 or public domain',
           'Finnish Heritage Agency, Helsinki City Museum and other Finnish museums via Europeana, credited in ATTRIBUTION.txt', "permissive", 4000, 15, prepare_pack, 'about 300 MB'),
    Source('europeana_cs', 'Náprstek Museum, Prague: objects described in Czech with English (Europeana, ready-made pack)',
           'Record text CC0; pictures CC BY 4.0',
           'Náprstek Museum of Asian, African and American Cultures, Prague, via Europeana, CC BY 4.0', "permissive", 3000, 15, prepare_pack, 'about 200 MB'),
    Source('europeana_hu', 'Hungarian museums: objects and photos described in Hungarian, with English (Europeana, ready-made pack)',
           'Record text CC0; pictures CC BY 4.0, CC0 or public domain',
           'Hungarian museums via Europeana, credited in ATTRIBUTION.txt', "permissive", 3000, 15, prepare_pack, 'about 300 MB'),
    Source('europeana_el', 'Greek museums: objects and photos described in Greek, with English (Europeana, ready-made pack)',
           'Record text CC0; pictures CC BY 4.0, CC0 or public domain',
           'Greek museums via Europeana, credited in ATTRIBUTION.txt', "permissive", 3000, 15, prepare_pack, 'about 300 MB'),
    Source('europeana_no', 'Norwegian museums: photos described in Norwegian, with English (Europeana, ready-made pack)',
           'Record text CC0; pictures CC BY 4.0, CC0 or public domain',
           'Norwegian museums via Europeana, credited in ATTRIBUTION.txt', "permissive", 4000, 15, prepare_pack, 'about 400 MB'),
    Source('europeana_pl', 'Polish digital libraries: photo captions in Polish, with English (Europeana, ready-made pack)',
           'Record text CC0; pictures CC BY 4.0, CC0 or public domain',
           'Polish regional digital libraries via Europeana, credited in ATTRIBUTION.txt', "permissive", 1500, 10, prepare_pack, 'about 150 MB'),
    Source('bd_taka', 'Bangladeshi taka banknotes (ready-made pack)',
           'CC BY 4.0 (Mendeley Data 2r8367vkpm)',
           'Bangladeshi taka banknote dataset, Mendeley Data 2r8367vkpm, CC BY 4.0', "permissive", 547, 10, prepare_pack, 'about 100 MB'),
    Source('medpack_id', 'Medicine packets and loose pills: how many and where (Indonesia, ready-made pack)',
           'CC BY 4.0 (Mendeley Data d23kndp3sv)',
           'MedPackID dataset, Mendeley Data d23kndp3sv, CC BY 4.0', "permissive", 1444, 10, prepare_pack, 'about 300 MB'),
    Source('fashionpedia', 'Clothing: what people are wearing, in detail (Fashionpedia, ready-made pack)',
           'CC BY 4.0 labels; only photos under CC BY or CC0, each author credited',
           'Fashionpedia (Jia et al., 2020), CC BY 4.0; photos by their Flickr authors', "permissive", 4000, 20, prepare_pack, 'about 1 GB'),
    Source('loc_highsmith', "Carol M. Highsmith's photos of America with detailed captions (Library of Congress, ready-made pack)",
           'No known restrictions on publication (Library of Congress)',
           'Carol M. Highsmith Archive, Library of Congress, Prints and Photographs Division', "permissive", 4000, 20, prepare_pack, 'about 1.5 GB'),
    Source('loc_fsa', '1930s and 1940s documentary photos of American life (FSA/OWI, Library of Congress, ready-made pack)',
           'US government work, no known restrictions (Library of Congress)',
           'Farm Security Administration / Office of War Information collection, Library of Congress', "permissive", 4000, 20, prepare_pack, 'about 1.5 GB'),
    Source('loc_world', 'Historic travel photos of the world (Photochrom prints and Matson collection, Library of Congress, ready-made pack)',
           'No known restrictions (Library of Congress)',
           'Photochrom Print Collection and Matson (G. Eric and Edith) Photograph Collection, Library of Congress', "permissive", 3000, 15, prepare_pack, 'about 800 MB'),
    Source('npgallery', 'US national parks: places, wildlife and events, with captions (National Park Service, ready-made pack)',
           'Public domain (National Park Service)',
           'National Park Service, NPGallery, public domain', "permissive", 4000, 20, prepare_pack, 'about 1.5 GB'),
    Source('earth_observatory', 'The Earth from space, described (NASA Earth Observatory, ready-made pack)',
           'Not under copyright (NASA)',
           'NASA Earth Observatory', "permissive", 2000, 15, prepare_pack, 'about 800 MB'),
    Source('eso', 'Telescopes, observatories and the landscapes of Chile (ESO, ready-made pack)',
           'CC BY 4.0 (eso.org/public/copyright)',
           'ESO, CC BY 4.0', "permissive", 1200, 10, prepare_pack, 'about 500 MB'),
    Source('usgs', 'Rivers, volcanoes, fieldwork and landscapes (US Geological Survey, ready-made pack)',
           'Public domain (US Geological Survey)',
           'US Geological Survey multimedia gallery, public domain', "permissive", 3000, 15, prepare_pack, 'about 1 GB'),
    Source('commons_valued', 'Wikimedia Commons valued images with their captions (ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2500, 15, prepare_pack, 'about 1 GB'),
    Source('open_images_disability', 'Mobility aids and adaptive sports (Open Images, ready-made pack)',
           'Annotations CC BY 4.0 (Google Open Images); photos CC BY 2.0, each author credited',
           'Open Images (Google), CC BY 4.0 annotations; photos CC BY 2.0, credited in ATTRIBUTION.txt', "permissive",
           219, 10, prepare_pack, 'about 60 MB'),
    Source('commons_disability', 'Assistive technology: white canes, guide dogs, braille, prostheses, hearing aids, '
           'accessible places (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1500, 10, prepare_pack,
           'about 500 MB'),
    Source('tapad_tactile_paving', 'Tactile paving and its condition (TAPAD, Japan, ready-made pack)',
           'CC BY 4.0 (Zenodo 23388177)',
           'TAPAD tactile paving dataset, Zenodo 23388177, CC BY 4.0', "permissive", 2811, 15, prepare_pack,
           'about 700 MB'),
    Source('skin_lesion_photos', 'Skin spots photographed with a phone, adults (PAD-UFES-20, ready-made pack)',
           'CC BY 4.0 (Mendeley Data zr7vgbcyr2)',
           'PAD-UFES-20 (Pacheco et al., 2020), CC BY 4.0', "permissive", 2000, 20, prepare_pack, 'about 400 MB', content="medical"),
    Source('isic_skin', 'Skin spots through a skin magnifier, adults (ISIC Archive, ready-made pack)',
           'Each picture CC0 or CC BY (ISIC Archive)',
           'ISIC Archive contributors, CC0 or CC BY, credited in ATTRIBUTION.txt', "permissive", 6000, 20, prepare_pack, 'about 1.5 GB', content="medical"),
    Source('gi_endoscopy', 'Stomach and bowel camera pictures (HyperKvasir, ready-made pack)',
           'CC BY 4.0 (osf.io/mh9sj)',
           'HyperKvasir (Borgli et al., 2020), CC BY 4.0', "permissive", 5000, 20, prepare_pack, 'about 1 GB', content="medical"),
    Source('chest_xray', 'Chest X-rays of adults (NIH ChestX-ray14, ready-made pack)',
           'No restrictions on use, with credit (NIH Clinical Center)',
           'NIH Clinical Center, ChestX-ray14 (Wang et al., 2017)', "permissive", 5000, 20, prepare_pack, 'about 1.5 GB', content="medical"),
    Source('case_report_figures', 'Medical pictures from published case reports about adults (PubMed Central, ready-made pack)',
           'Each article CC BY or CC0 (PubMed Central open access)',
           'Authors of the case reports in PubMed Central, CC BY or CC0, credited in ATTRIBUTION.txt', "permissive", 10000, 20, prepare_pack, 'about 3 GB', content="medical"),
    Source('vet_case_figures', 'Animal medical pictures from published case reports (PubMed Central, ready-made pack)',
           'Each article CC BY or CC0 (PubMed Central open access)',
           'Authors of the veterinary case reports in PubMed Central, CC BY or CC0, credited in ATTRIBUTION.txt', "permissive", 2000, 15, prepare_pack, 'about 600 MB', content="medical"),
    Source('cdc_medical', 'Medical photos of adults from the CDC Public Health Image Library (ready-made pack)',
           'Public domain (US government), item by item',
           'CDC Public Health Image Library (phil.cdc.gov), public domain', "permissive", 600, 10, prepare_pack, 'about 150 MB', content="medical"),
    Source('medical_collections', 'Medical photos of adults from the Wellcome Collection and Europeana (ready-made pack)',
           'CC BY, CC0 or public domain, item by item',
           'Wellcome Collection and Europeana partner institutions, credited in ATTRIBUTION.txt', "permissive", 300, 10, prepare_pack, 'about 100 MB', content="medical"),
    Source('childhood_illness', 'Childhood illnesses: what a rash or sign looks like on a child (ready-made pack; describing only)',
           'Public domain, CC0 or CC BY, item by item',
           'CDC Public Health Image Library, Wellcome Collection and Europeana partners, credited in ATTRIBUTION.txt', "permissive", 300, 10, prepare_pack, 'about 100 MB', content="medical"),
    Source('birth_and_feeding', 'Pregnancy, birth, breastfeeding and newborns (ready-made pack; describing only)',
           'Public domain, CC0 or CC BY, item by item',
           'CDC, Wellcome Collection, Europeana partners and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1500, 10, prepare_pack, 'about 400 MB', content="medical"),
    # Pictures of the human body (packs/body_packs.py). Records mentioning children or sexual content are left out
    # when the packs are built; the person training still chooses whether to use them (--with-nudity, --with-medical).
    Source("art_nudes", "Nudes in art, described plainly and without anything sexual (ready-made pack)",
           "CC0 or public domain (The Met, Art Institute of Chicago, Cleveland Museum of Art, National Gallery of "
           "Art, Smithsonian; each work credited in the pack's CREDITS.txt)",
           "Non-sexual nudes in art from The Metropolitan Museum of Art, the Art Institute of Chicago, the Cleveland "
           "Museum of Art, the National Gallery of Art (Washington) and the Smithsonian American Art Museum, CC0 or "
           "public domain, each work credited in CREDITS.txt", "permissive", 3000, 10, prepare_pack, "about 600 MB",
           content="nudity"),
    Source("anatomy", "Anatomy figures: OpenStax Anatomy and Physiology and Gray's Anatomy plates (ready-made pack)",
           "OpenStax figures CC BY 4.0 (first edition); Gray's Anatomy (1918) plates public domain",
           "OpenStax, Anatomy and Physiology (2013, first edition), Rice University, CC BY 4.0, "
           "https://openstax.org/details/books/anatomy-and-physiology; Henry Gray, Anatomy of the Human Body (1918), "
           "public domain, via Wikimedia Commons", "permissive", 1500, 10, prepare_pack, "about 200 MB",
           content="medical"),
    Source("concadia", "Concadia: Wikipedia pictures with their alt text",
           "CC BY-SA 4.0 (Wikipedia's text); pictures under their own Wikimedia Commons licences",
           "Concadia (Kreiss et al., 2022) from Wikipedia, CC BY-SA 4.0, https://github.com/elisakreiss/concadia",
           "share-alike", 5000, 10, prepare_concadia, "up to 2 GB"),
    Source("wikipedia", "Wikipedia: alt text written for screen-reader users",
           "CC BY-SA 4.0 (wikimedia/wit_base); pictures under their own Wikimedia Commons licences",
           "Wikipedia-based Image Text (WIT) by Wikimedia, CC BY-SA 4.0, https://huggingface.co/datasets/wikimedia/"
           "wit_base", "share-alike", 5000, 15, prepare_wikipedia, "about 11 GB, deleted as it goes"),
]


def chosen(with_wikipedia=False, *, with_nudity=False, with_medical=False, with_noncommercial=False,
           with_research=False, with_sexual=False):
    """The sources to train on: the permissive ones; the share-alike ones too with with_wikipedia; the
    "noncommercial" ones with with_noncommercial and the "research" ones with with_research (both for personal use
    only). A collection with content "nudity" is only included with with_nudity, and one with content "medical" only
    with with_medical; "intimate" needs both, and "sexual" with_sexual and with_nudity (allowed_contents). A
    collection of any other group is never included."""
    allowed = allowed_contents(with_nudity, with_medical, with_sexual)
    groups = {"permissive": True, "share-alike": with_wikipedia, "noncommercial": with_noncommercial,
              "research": with_research}
    return [s for s in SOURCES if groups.get(s.group, False) and s.content in allowed]


# ----------------------------------------------------------------- personal-use collections

# The groups whose collections make the add-on PERSONAL USE ONLY.
PERSONAL_GROUPS = ("noncommercial", "research")

# The first lines of the report, of ATTRIBUTION.txt's personal part and of PERSONAL-USE-ONLY.txt.
PERSONAL_WARNING = ("PERSONAL USE ONLY. This add-on learned from collections whose licences do not allow commercial "
                    "use (and/or research-only collections). Do not sell it, publish it, put it in a product or share "
                    "it outside personal, non-commercial use.")


def is_personal(source):
    """True when a collection is for personal use only (its group is "noncommercial" or "research")."""
    return getattr(source, "group", "") in PERSONAL_GROUPS


def terms_link(source):
    """The web address of a collection's terms: its terms field, or else the first web address in its licence or
    credit ("" when there is none)."""
    if getattr(source, "terms", ""):
        return source.terms
    found = re.search(r"https?://\S+", f"{source.licence} {source.credit}")
    return found.group(0).rstrip(".,;)") if found else ""


def terms_summary(source):
    """A collection's terms in one plain line: its terms_summary, or else its licence."""
    return getattr(source, "terms_summary", "") or source.licence


def personal_sources(group=None):
    """The personal-use collections in SOURCES (only those of group when given: "noncommercial" or "research")."""
    return [s for s in SOURCES if is_personal(s) and (group is None or s.group == group)]


# Collections that a picture-making model (train_pictures.py) never trains on, whatever is chosen: pictures of
# children with childhood illnesses, and of birth, breastfeeding and newborns, are for describing only.
NOT_FOR_PICTURE_MAKING = ("childhood_illness", "birth_and_feeding")


def content_of(key):
    """The content choice ("", "nudity", "medical", "intimate" or "sexual") of the collection with this key ("" when unknown)."""
    return next((s.content for s in SOURCES if s.key == key), "")


def content_choices_text(with_nudity, with_medical, with_sexual=False):
    """The content choices in one plain sentence, for the report and ATTRIBUTION.txt: art with nudity, medical
    pictures, intimate medical pictures (only with both) and adult sexual content (only with with_sexual and art with
    nudity; personal use only)."""
    allowed = allowed_contents(with_nudity, with_medical, with_sexual)
    return ("Content choices: art with nudity (non-sexual) " + ("included" if with_nudity else "not included") +
            "; medical and anatomy pictures " + ("included" if with_medical else "not included") +
            "; intimate medical pictures from reviewed collections (needs both) " +
            ("included" if "intimate" in allowed else "not included") +
            "; adult sexual content from reviewed collections " +
            ("included (personal use only)" if "sexual" in allowed else "not included") + ".")


def prepare_source(source, data_dir, work, size="normal", seed=7):
    """Prepare one source once for a size: (train rows, test rows), also written to data/<key>-<size>.jsonl, which a
    restarted kit reads instead of preparing again (a bigger size prepares again, using the pictures already there). Its "test" rows (or, without them, a random few) are the test pictures; the
    rest, up to its cap for the size, are for training."""
    path = os.path.join(data_dir, f"{source.key}-{size}.jsonl")
    rows = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        missing = sum(1 for r in rows if not have(r["picture"]))
        if missing:
            # Prepared before the picture library existed (or interrupted): its pictures are downloaded again at
            # full size for the library; the list stays the same, so the training does not change.
            say(f"    {missing} of its pictures have no full-size copy in the picture library yet: downloading them "
                "again at full size.")
            try:
                source.prepare(source, data_dir, work, max(50, int(source.cap * SIZES[size])))
            except Exception as e:  # noqa: BLE001 - the pictures already there still train; tried again next time
                say(f"    The full-size copies could not be downloaded now ({str(e).splitlines()[0][:150]}); the "
                    "training uses the pictures already there, and they are tried again next time.")
    if rows is None:
        cap = max(50, int(source.cap * SIZES[size]))
        rows = source.prepare(source, data_dir, work, cap)
        rows = [dict(r, source=source.key) for r in rows if r.get("picture") and clean(r.get("answer"))]
        with open(path + ".part", "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        os.replace(path + ".part", path)
    rng = random.Random(f"{seed}-{source.key}")
    marked = [r for r in rows if r.get("split") == "test"]
    testable = [r for r in rows if r.get("split") not in ("test", "no-test")]
    untestable = [r for r in rows if r.get("split") == "no-test"]
    rng.shuffle(marked)
    rng.shuffle(testable)
    if len(marked) >= source.test:
        test, rest = marked[:source.test], testable + untestable
    else:
        test, rest = testable[:source.test], testable[source.test:] + untestable
    rng.shuffle(rest)
    cap = max(50, int(source.cap * SIZES[size]))
    return rest[:cap], test


def _add_collections(extra):
    """Put more collections (from their own files) into SOURCES, before the first collection that is not permissive
    (share-alike or personal-use), so the permissive collections stay together and in the order the kit trains
    them."""
    first_shared = next((i for i, s in enumerate(SOURCES) if s.group != "permissive"), len(SOURCES))
    known = {s.key for s in SOURCES}
    SOURCES[first_shared:first_shared] = [s for s in extra if s.key not in known]


# The large described-picture and question collections (VQA, Visual Dialog, Localized Narratives ...), in their own file.
# Imported here, at the end, because that file uses this one's helpers.
from more_sources import MORE_SOURCES  # noqa: E402

_add_collections(MORE_SOURCES)

# The big food downloads kept in the picture library (beef, fish, chicken, food packaging, Packeat produce).
from big_sources import BIG_SOURCES  # noqa: E402

_add_collections(BIG_SOURCES)

# The personal-use collections (non-commercial licences and research-only terms), in their own file, which may be
# missing: the kit then simply has none. PERSONAL_PICTURE_MAKING_OK: the keys of those a picture-making model may
# learn from (train_pictures.py); none when the file or the set is missing.
try:
    import personal_sources as _personal  # noqa: E402
except ImportError as _e:
    _personal = None
    if getattr(_e, "name", None) != "personal_sources":       # the file is there but cannot be loaded: say why
        say(f"(The personal-use collections could not be loaded: {_e}. They are left out.)")
PERSONAL_SOURCES = list(getattr(_personal, "PERSONAL_SOURCES", []) or [])
PERSONAL_PICTURE_MAKING_OK = set(getattr(_personal, "PERSONAL_PICTURE_MAKING_OK", ()) or ())

_add_collections(PERSONAL_SOURCES)

# Every other collection found (share-alike, non-commercial, research-only or no stated terms, and two open ones too
# big for a pack), each in the group its licence allows (packs/SOURCE-RULES.md); the file may be missing.
try:
    import extra_sources as _extra  # noqa: E402
except ImportError as _e:
    _extra = None
    if getattr(_e, "name", None) != "extra_sources":
        say(f"(The extra collections could not be loaded: {_e}. They are left out.)")
EXTRA_SOURCES = list(getattr(_extra, "EXTRA_SOURCES", []) or [])
_extra_ok = set(getattr(_extra, "EXTRA_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _extra_ok
# A picture-making model learns from an extra collection only when it is marked suitable (no people, children or
# medical pictures), whatever its group.
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in EXTRA_SOURCES if s.key not in _extra_ok)

_add_collections(EXTRA_SOURCES)

# Documentary photo collections that are not open (share-alike Commons featured pictures, Unsplash Lite for personal
# use); the file may be missing.
try:
    import documentary_sources as _documentary  # noqa: E402
except ImportError as _e:
    _documentary = None
    if getattr(_e, "name", None) != "documentary_sources":
        say(f"(The documentary collections could not be loaded: {_e}. They are left out.)")
DOCUMENTARY_SOURCES = list(getattr(_documentary, "DOCUMENTARY_SOURCES", []) or [])
_documentary_ok = set(getattr(_documentary, "DOCUMENTARY_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _documentary_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in DOCUMENTARY_SOURCES if s.key not in _documentary_ok)
_add_collections(DOCUMENTARY_SOURCES)

# Disability and assistive-technology collections that are not open (or not suitable for picture-making); the file
# may be missing.
try:
    import disability_sources as _disability  # noqa: E402
except ImportError as _e:
    _disability = None
    if getattr(_e, "name", None) != "disability_sources":
        say(f"(The disability collections could not be loaded: {_e}. They are left out.)")
DISABILITY_SOURCES = list(getattr(_disability, "DISABILITY_SOURCES", []) or [])
_disability_ok = set(getattr(_disability, "DISABILITY_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _disability_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in DISABILITY_SOURCES if s.key not in _disability_ok)
_add_collections(DISABILITY_SOURCES)
