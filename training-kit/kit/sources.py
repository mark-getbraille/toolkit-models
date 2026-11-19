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
is for personal use only. One ready-made pack is marked "sexual" as a whole: erotic_art (packs/adult_art_packs.py,
erotic art showing adults), and museum_art_nudes is marked "nudity". allowed_contents() gives the tags a training's choices allow. A picture-making model never
learns from either (PICTURE_MAKING_NEVER), nor from any review collection.
One more content tag, "graphic" (war, disasters, injuries and death, described plainly: the dead and injured, wounds,
severe destruction with casualties), is used only with with_graphic (train.py --with-graphic). It can mark a whole
collection (Source.content) or single rows of any pack ("content": "graphic" in a pack's rows.jsonl, carried by
prepare_pack; keep_allowed() leaves out the rows a training's choices do not allow). A picture-making model never
learns from graphic content (PICTURE_MAKING_NEVER, and the graphic packs are in NOT_FOR_PICTURE_MAKING too).

Sizes (--size): each source has a cap for "normal"; "quick" uses a tenth of it (a try of an hour or two) and
"full" three times as much (several nights on a fast card).

A finished source is not prepared again when the kit is started again (its rows are kept in data/<key>-<size>.jsonl;
a bigger size prepares it again, but pictures already downloaded are kept).

Main parts: Source, SOURCES, chosen(with_wikipedia, with_nudity=, with_medical=, with_noncommercial=, with_research=,
with_sexual=, with_graphic=), allowed_contents, keep_allowed, content_choices_text, PERSONAL_GROUPS, is_personal, terms_link, terms_summary, PERSONAL_WARNING,
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
    content    "" for most collections; "nudity" (non-sexual nudes in art: only with --with-nudity), "medical"
               (medical and anatomy pictures: only with --with-medical) or "graphic" (war, disasters, injuries and
               death: only with --with-graphic); "intimate" and "sexual" are known too (see allowed_contents);
               "sexual" is used by the review collections and the erotic_art pack
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


# The content choices a collection (or a single row of a pack) can need: "" (none), "nudity", "medical", "intimate",
# "sexual" and "graphic" (see the module docstring and allowed_contents).
CONTENTS = ("", "nudity", "medical", "intimate", "sexual", "graphic")
# The content tags a picture-making model never learns from, whatever is chosen.
PICTURE_MAKING_NEVER = ("intimate", "sexual", "graphic")


def allowed_contents(with_nudity=False, with_medical=False, with_sexual=False, with_graphic=False):
    """The content tags a training's choices allow, as a set: "" always; "nudity" with with_nudity; "medical" with
    with_medical; "intimate" only with BOTH with_nudity and with_medical; "sexual" only with with_sexual AND
    with_nudity (the adult sexual content choice needs art with nudity); "graphic" (war, disasters, injuries and
    death) with with_graphic."""
    allowed = {""}
    for tag, on in (("nudity", with_nudity), ("medical", with_medical),
                    ("intimate", with_nudity and with_medical), ("sexual", with_sexual and with_nudity),
                    ("graphic", with_graphic)):
        if on:
            allowed.add(tag)
    return allowed


def row_content(row):
    """The content tag of one row ("" for none): its own "content" when it is a known tag. A row with a tag this kit
    does not know is treated as "unknown", so it is never used by mistake."""
    tag = str(row.get("content") or "").strip().lower()
    return tag if tag in CONTENTS else "unknown"


# The themes of erotic_art rows (packs/adult_art_packs.py): works of sexual violence, no consent or restraint, said
# plainly in their answers. A training can leave them out (train.py --without-sexual-violence).
SEXUAL_VIOLENCE_THEMES = ("sexual violence (artwork)", "no consent (artwork)", "restraint (artwork)")


def leave_out_themes(rows, themes):
    """The rows whose "theme" is not in themes (all rows when themes is empty)."""
    themes = set(themes or ())
    return [r for r in rows if str(r.get("theme") or "") not in themes] if themes else list(rows)


def keep_allowed(rows, allowed):
    """The rows whose own content tag (row_content: "content": "graphic" from any pack, for example) is in allowed
    (a set from allowed_contents); the others are left out. Rows without a tag are always kept."""
    return [r for r in rows if row_content(r) in allowed]


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
_PACKS_MANIFEST = {}


def packs_manifest():
    """The list of ready-made packs (packs.json), read once per run. When the packs are rebuilt, GitHub briefly has no
    packs.json (the old one is removed just before the new one is uploaded), so a failed or unreadable answer is tried
    again up to 6 times, a minute apart, before the packs are left out for this run."""
    import requests
    if "list" in _PACKS_MANIFEST:
        return _PACKS_MANIFEST["list"]
    problem = None
    for attempt in range(6):
        if attempt:
            say("    The list of ready-made packs could not be read just now; trying again in a minute.")
            time.sleep(60)
        try:
            answer = requests.get(PACKS_URL + "packs.json", timeout=60, headers={"User-Agent": USER_AGENT})
            answer.raise_for_status()
            listed = answer.json()
            if isinstance(listed, dict) and listed:
                _PACKS_MANIFEST["list"] = listed
                return listed
            problem = "the list of ready-made packs was empty"
        except Exception as e:  # noqa: BLE001 - a network or GitHub hiccup: try again
            problem = str(e).splitlines()[0][:200] if str(e) else type(e).__name__
    raise RuntimeError(f"the list of ready-made packs could not be read ({problem})")


def prepare_pack(source, data_dir, work, cap):
    """A ready-made pack built on GitHub's machines and published in the kit's own repository (packs/build_packs.py):
    its parts are downloaded, joined, checked against packs.json's SHA-256 and unpacked; a row with "url" instead of a
    picture (COCO's photos, which may not be copied) is fetched from its own website."""
    import hashlib
    import zipfile
    manifest = packs_manifest()
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
            if row.get("content"):                   # a row's own content tag ("graphic"): used only when chosen
                base["content"] = str(row["content"]).strip().lower()
            if row.get("theme"):                     # erotic_art's theme (sexual violence ...): can be left out
                base["theme"] = str(row["theme"]).strip().lower()
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
# made), "depicted" (the place a picture shows) or "market" (the country of the shop that sells a product, as ABO's
# Amazon shops: not where the photo was taken nor where the thing was made, so it is kept for the record only and
# never taught). Places come only from each collection's own records (packs/places.py builds them for the packs),
# never from a guess. train.py teaches the describer a few "Which country might this photo be from?" and "Where was
# this object made?" answers from them; train_pictures.py starts a description with its place, so a picture-making
# add-on learns what places look like (both leave "market" places out).
PLACE_KINDS = ("photo", "origin", "depicted", "market")
# Collections whose photos show the place itself (streets, homes, shops, landscapes), so a describer may learn to
# say which country a photo might be from; "own" is the person's own pictures with a place.txt.
PLACE_VISIBLE = {"dollar_street", "dollar_street_routines", "geode", "ptl_crossings", "uroac_crossings", "walkway_dhaka", "outdoor_navigation",
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
    Source("met_collection", "The Metropolitan Museum of Art: objects of every department, with their subjects (ready-made pack)",
           "CC0 (Met Open Access), each object's own public-domain mark checked",
           "The Metropolitan Museum of Art Open Access, CC0, credited in CREDITS.txt", "permissive", 6000, 20,
           prepare_pack, "about 1.2 GB"),
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
           "permissive", 1500, 20, prepare_pack, "about 500 MB"),
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
    # Graphic scenes described plainly: war, disasters, injuries and death, and practical safety scenes (packs/
    # graphic_packs.py). Their rows that show the dead or injured, wounds or destruction with casualties carry
    # "content": "graphic" and are used only with --with-graphic (keep_allowed); the other rows (ruins, signs,
    # shelters, floods) are used always. None of them is ever used for picture-making (GRAPHIC_PACK_KEYS).
    Source('loc_civil_war', 'The American Civil War and the Crimean War: battlefields, the dead and wounded, field '
           'hospitals and ruins (Library of Congress, ready-made pack)',
           'No known restrictions on publication (Library of Congress)',
           'Civil War Glass Negatives and Related Prints, and the Roger Fenton Crimean War Photograph Collection, '
           'Library of Congress, Prints and Photographs Division', "permissive", 2000, 15, prepare_pack,
           'about 800 MB'),
    Source('loc_war_disaster', 'The First World War, floods, fires and civil defence, 1900 to 1945 (Bain News Service '
           'and FSA/OWI, Library of Congress, ready-made pack)',
           'No known restrictions on publication (Library of Congress)',
           'George Grantham Bain Collection and Farm Security Administration / Office of War Information collection, '
           'Library of Congress', "permissive", 2000, 15, prepare_pack, 'about 800 MB'),
    Source('nara_war', 'War from the First World War to Vietnam: the wounded, aid stations, destruction and refugees '
           '(US Army Signal Corps, National Archives, ready-made pack)',
           'Public domain (US government work, National Archives, records marked Unrestricted)',
           'Photographs of American Military Activities (111-SC), U.S. National Archives and Records Administration, '
           'public domain', "permissive", 1200, 10, prepare_pack, 'about 500 MB'),
    Source('ushmm', 'The Holocaust: liberation of the camps, survivors, the dead, ghettos and trials, described '
           'factually (US Holocaust Memorial Museum, ready-made pack)',
           'Public domain (only photographs whose museum record says "Copyright: Public Domain")',
           'United States Holocaust Memorial Museum photo archive, public-domain photographs (mostly US Army Signal '
           'Corps, National Archives)', "permissive", 2000, 15, prepare_pack, 'about 700 MB'),
    Source('commons_war', 'War casualties, the wounded, aftermath and war damage, from the World Wars to Ukraine and '
           'Syria (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2000, 15, prepare_pack,
           'about 800 MB'),
    Source('commons_disasters', 'Earthquake, flood, tornado, landslide and fire damage (Wikimedia Commons and FEMA, '
           'ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors and FEMA, credited in ATTRIBUTION.txt', "permissive", 2000, 15, prepare_pack,
           'about 800 MB'),
    Source('commons_safety', 'Safety in danger: fallen power lines, floods, fire and smoke, unexploded bombs and mine '
           'signs, checkpoints, shelters, first aid and evacuation signs (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1500, 15, prepare_pack,
           'about 600 MB'),
    # More archive, museum and news photographs with their makers' captions (packs/archive_packs.py). Rows whose
    # caption names the dead, wounds or casualties carry "content": "graphic" and are used only with --with-graphic.
    Source('nara', 'American life, the environment and national parks, 1940s to 1970s: DOCUMERICA, War Relocation '
           'Authority and Ansel Adams photographs (US National Archives, ready-made pack)',
           'Public domain (US government work, National Archives, records marked Unrestricted)',
           'U.S. National Archives and Records Administration (412-DA, 210-G, 79-AA), public domain', "permissive",
           3300, 15, prepare_pack, 'about 1.5 GB'),
    Source('nypl', 'Photographs, stereoviews, postcards and prints with their titles (New York Public Library, '
           'ready-made pack)',
           'No known US copyright restrictions (items); metadata CC0 (New York Public Library)',
           'The New York Public Library, public-domain collections', "permissive", 4000, 15, prepare_pack,
           'about 1.5 GB'),
    Source('getty_museum', 'Art and objects with the museum\'s descriptions (J. Paul Getty Museum, ready-made pack)',
           'No Copyright (Getty Open Content); metadata CC0',
           'The J. Paul Getty Museum, Los Angeles, Open Content Program', "permissive", 5000, 15, prepare_pack,
           'about 1 GB'),
    Source('digital_commonwealth', 'Historic photographs of Massachusetts and beyond (Digital Commonwealth, '
           'ready-made pack)',
           'No known copyright restrictions (Digital Commonwealth records)',
           'Digital Commonwealth, Massachusetts libraries, archives and museums', "permissive", 2000, 15,
           prepare_pack, 'about 800 MB'),
    Source('smk', 'Danish art with descriptive titles, in Danish with English (Statens Museum for Kunst, ready-made '
           'pack)',
           'Public domain (CC0 / Public Domain Mark, open.smk.dk)',
           'Statens Museum for Kunst (National Gallery of Denmark), public domain', "permissive", 2000, 15,
           prepare_pack, 'about 800 MB'),
    Source('anefo', 'Dutch press photos, 1945 to 1989, in Dutch with English (Nationaal Archief, ready-made pack)',
           'CC0 or public domain (Nationaal Archief)',
           'Nationaal Archief, The Hague, mostly the Anefo collection, CC0 or public domain', "permissive", 4000, 15,
           prepare_pack, 'about 1.5 GB'),
    Source('kremlin', 'Meetings, ceremonies and visits, with their captions (en.kremlin.ru, ready-made pack)',
           'CC BY 4.0 (the site\'s own statement)',
           'Presidential Executive Office of Russia, en.kremlin.ru, CC BY 4.0', "permissive", 2000, 15, prepare_pack,
           'about 800 MB'),
    Source('awm', 'The World Wars and later conflicts, with the Memorial\'s captions (Australian War Memorial, '
           'ready-made pack)',
           'Copyright expired, public domain (Australian War Memorial records)',
           'Australian War Memorial, public-domain photographs', "permissive", 2000, 15, prepare_pack,
           'about 800 MB'),
    # Military equipment and the uniformed services, past and present (packs/service_packs.py). War rows that show the
    # dead, wounds or injuries carry "content": "graphic" and are used only with --with-graphic; rows naming a child
    # carry "child". Only the civil-aircraft pack is used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('commons_military', 'Military vehicles, aircraft, warships, small arms, armour and decorations, with facts '
           'from Wikidata (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited; facts from Wikidata (CC0)',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; facts from Wikidata, CC0', "permissive", 2700, 20,
           prepare_pack, 'about 1.2 GB'),
    Source('commons_airplanes', 'Airliners, business jets, light aircraft, airships and civil helicopters, with facts '
           'from Wikidata (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited; facts from Wikidata (CC0)',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; facts from Wikidata, CC0', "permissive", 1700, 15,
           prepare_pack, 'about 800 MB'),
    Source('commons_uniformed', 'Police, fire, ambulance, rangers, nurses, military and ceremonial uniforms and service '
           'vehicles by country (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 20, prepare_pack,
           'about 1.2 GB'),
    Source('loc_service', 'Soldiers, the Civil War and the First World War, tanks, warships, police, fire fighters and '
           'nurses (Library of Congress, ready-made pack)',
           'No known restrictions on publication (Library of Congress)',
           'Library of Congress, Prints and Photographs Division (Civil War glass negatives, Bain News Service and '
           'photos by subject)', "permissive", 2700, 20, prepare_pack, 'about 1.2 GB'),
    Source('nara_military', 'The US Navy, Marine Corps, Coast Guard and Army Signal Corps photographs with their '
           'captions (US National Archives, ready-made pack)',
           'Public domain (US government work, National Archives, records marked Unrestricted)',
           'Photo series 80-G, 127, 26-G and 111-SC, U.S. National Archives and Records Administration, public domain',
           "permissive", 2000, 15, prepare_pack, 'about 900 MB'),
    Source('army_mil', 'U.S. Army photos with their full captions (army.mil, ready-made pack)',
           'Public domain (US government work)',
           'U.S. Army photographers, www.army.mil/photos, public domain, each photographer credited in ATTRIBUTION.txt',
           "permissive", 170, 10, prepare_pack, 'about 80 MB'),
    Source('nasm_aircraft', 'Aircraft, flight uniforms, helmets, insignia and medals with the museum\'s records '
           '(Smithsonian National Air and Space Museum, ready-made pack)',
           'CC0 (Smithsonian Open Access)',
           'Smithsonian National Air and Space Museum, Smithsonian Open Access, CC0', "permissive", 800, 10,
           prepare_pack, 'about 350 MB'),
    Source('nmah_service', 'Uniforms, insignia, medals, arms and armour, police and fire objects with the museum\'s '
           'descriptions (Smithsonian National Museum of American History, ready-made pack)',
           'CC0 (Smithsonian Open Access, CC0 pictures only)',
           'Smithsonian National Museum of American History, Smithsonian Open Access, CC0', "permissive", 1000, 10,
           prepare_pack, 'about 450 MB'),
    # Bodily fluids and waste (packs/bodily_packs.py): dog poop in the yard, animal droppings, blood, vomit, stool and
    # urine. Human medical rows carry "content": "medical" (used only with --with-medical); the two packs that are all
    # human medical material are marked so as a whole. None is used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('scatspotter', 'Has a dog pooped here, and where? Phone photos of yards, paths and snow (ScatSpotter, '
           'ready-made pack)',
           'CC BY 4.0 (huggingface.co/datasets/erotemic/shitspotter)',
           'ScatSpotter (Jon Crall, Kitware, WACV Workshops 2026), CC BY 4.0, https://github.com/Erotemic/shitspotter',
           "permissive", 2000, 20, prepare_pack, 'about 900 MB'),
    Source('inat_droppings', 'Droppings of dogs, cats, horses, farm animals, birds and yard animals (iNaturalist, '
           'ready-made pack)',
           'Each photo CC0 or CC BY (its iNaturalist page)',
           'iNaturalist observers, CC0 or CC BY, credited in ATTRIBUTION.txt', "permissive", 1000, 15, prepare_pack,
           'about 450 MB'),
    Source('open_images_bodily', 'Is there blood in this picture? Blood, injuries, bandages, poop, litter boxes and '
           'stains (Open Images, ready-made pack)',
           'Labels CC BY 4.0; each photo CC BY 2.0 (Open Images V7)',
           'Open Images V7 (Google), labels CC BY 4.0; photographers credited in ATTRIBUTION.txt', "permissive",
           2000, 20, prepare_pack, 'about 900 MB'),
    Source('commons_bodily', 'Stool, vomit, urine, blood stains and animal droppings, and the Bristol stool chart '
           '(Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 70, 10, prepare_pack,
           'about 30 MB'),
    Source('case_report_bodily', 'Stool, vomit, urine and nosebleed photos from published case reports, adults '
           '(PubMed Central, ready-made pack)',
           'Each article CC BY or CC0 (PubMed Central open access)',
           'Authors of the case reports in PubMed Central, CC BY or CC0, credited in ATTRIBUTION.txt', "permissive",
           100, 10, prepare_pack, 'about 40 MB', content="medical"),
    Source('urine_samples', 'What colour is this urine? Samples in clear pots photographed with phones (urine-detector, '
           'ready-made pack)',
           'Apache-2.0 (huggingface.co/datasets/celesca/urine-detector)',
           'urine-detector (celesca on Hugging Face), Apache-2.0, https://huggingface.co/datasets/celesca/urine-detector',
           "permissive", 350, 10, prepare_pack, 'about 150 MB', content="medical"),
    # Sport, music, religion, landmarks, vehicles and games (packs/culture_packs.py): no row has a content tag; rows
    # naming a child carry "child". The packs with people in them (sport, festivals, street vehicles, Open Images) are
    # not used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('open_images_culture', 'Sports, musical instruments, vehicles, toys and kinds of building in everyday photos '
           '(Open Images, ready-made pack)',
           'Labels CC BY 4.0; each photo CC BY 2.0 (Open Images V7)',
           'Open Images V7 (Google), labels CC BY 4.0; photographers credited in ATTRIBUTION.txt', "permissive",
           5300, 20, prepare_pack, 'about 2.5 GB'),
    Source('wikidata_sports', 'Sports of the world, sports equipment and grounds, with facts from Wikidata (Wikimedia '
           'Commons, ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2000, 15,
           prepare_pack, 'about 900 MB'),
    Source('wikidata_instruments', 'Musical instruments of every culture, with facts from Wikidata (Wikimedia Commons, '
           'ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 15,
           prepare_pack, 'about 1.2 GB'),
    Source('met_instruments', 'Musical instruments with the museum\'s records (The Metropolitan Museum of Art, '
           'ready-made pack)',
           'CC0 (The Met Open Access, public-domain objects only)',
           'The Metropolitan Museum of Art, Department of Musical Instruments, Open Access, CC0', "permissive", 2300,
           15, prepare_pack, 'about 1 GB'),
    Source('wikidata_worship', 'Places of worship of every faith: what they are, where and of which faith (Wikidata and '
           'Wikimedia Commons, ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 20,
           prepare_pack, 'about 1.2 GB'),
    Source('commons_religious_life', 'Festivals, ceremonies, pilgrimages, religious objects and clergy dress of many '
           'faiths (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1300, 15, prepare_pack,
           'about 600 MB'),
    Source('wikidata_landmarks', 'Landmarks and World Heritage Sites: towers, castles, palaces, bridges, monuments '
           '(Wikidata and Wikimedia Commons, ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 20,
           prepare_pack, 'about 1.2 GB'),
    Source('wikidata_architecture', 'Architectural styles and parts of buildings (Wikidata and Wikimedia Commons, '
           'ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1700, 15,
           prepare_pack, 'about 800 MB'),
    Source('gldv2_landmarks', 'Landmarks and places around the world (Google Landmarks Dataset v2, ready-made pack)',
           'Labels CC BY 4.0; each image CC0, public domain or CC BY (its Commons page)',
           'Google Landmarks Dataset v2 (Weyand, Araujo, Cao and Sim, CVPR 2020), '
           'https://github.com/cvdfoundation/google-landmark ; image authors credited in ATTRIBUTION.txt',
           "permissive", 2700, 20, prepare_pack, 'about 1.2 GB'),
    Source('wikidata_vehicle_models', 'Car, motorcycle, bus, truck, tram, locomotive and ferry models, with facts from '
           'Wikidata (Wikimedia Commons, ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 20,
           prepare_pack, 'about 1.2 GB'),
    Source('commons_vehicle_kinds', 'Taxis, rickshaws, minibuses, school buses, bicycles, boats and other vehicles '
           '(Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1000, 15, prepare_pack,
           'about 450 MB'),
    Source('wikidata_toys_games', 'Playing cards, board and card games, toys, dice, LEGO and chess sets (Wikidata and '
           'Wikimedia Commons, ready-made pack)',
           'Facts CC0 (Wikidata); pictures CC0, public domain or CC BY, each author credited',
           'Wikidata (CC0) and Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1300, 15,
           prepare_pack, 'about 600 MB'),
    Source('playing_cards', 'Which playing card is this? Photos of real cards (French Playing Cards, ready-made pack)',
           'MIT licence (huggingface.co/datasets/drFarid/French-Playing-Cards)',
           'French Playing Cards (drFarid), MIT licence, https://huggingface.co/datasets/drFarid/French-Playing-Cards',
           "permissive", 1250, 15, prepare_pack, 'about 300 MB'),
    Source('chess_pieces', 'Chess pieces on a real board (Roboflow 100 Chess Pieces, ready-made pack)',
           'CC BY 4.0 (universe.roboflow.com/roboflow-100/chess-pieces-mjzgj)',
           'Chess Pieces (Joseph Nelson and Brad Dwyer, Roboflow), Roboflow 100, CC BY 4.0', "permissive", 200, 10,
           prepare_pack, 'about 60 MB'),
    Source('chess_positions', 'The position on a chessboard, square by square: computer-made renders (Chessboard '
           'renders, ready-made pack)',
           'CC BY 4.0 (huggingface.co/datasets/PeterAM4/chessboard-renders); positions from Lichess (CC0)',
           'Chessboard renders (Peter A. Massih, 2026), CC BY 4.0; positions from the Lichess database, CC0',
           "permissive", 2000, 15, prepare_pack, 'about 500 MB'),
    Source('chess_drawings', 'The position on a chessboard: flat computer drawings (Chessboard Detection Dataset, '
           'ready-made pack)',
           'CC BY 4.0 (huggingface.co/datasets/MohammedHemed/Chessboard-digital-images_with_fen)',
           'Chessboard Detection Dataset (Mohammed Hemed), CC BY 4.0; positions from the Lichess database, CC0',
           "permissive", 330, 10, prepare_pack, 'about 40 MB'),
    Source('drawn_cards', 'Which playing card is this? Computer drawings of cards (Playing cards, ready-made pack)',
           'MIT licence (huggingface.co/datasets/JackFurby/playing-cards)',
           'Playing cards (Jack Furby), MIT licence, https://huggingface.co/datasets/JackFurby/playing-cards',
           "permissive", 330, 10, prepare_pack, 'about 40 MB'),
    Source('deepscores_sheet_music', 'What a page of sheet music shows: clefs, time and key, notes, rests and dynamics '
           '(DeepScoresV2, ready-made pack)',
           'CC BY 4.0 (Zenodo 4012193)',
           'DeepScoresV2 (Tuggener, Satyawan, Pacha, Schmidhuber and Stadelmann, 2020), CC BY 4.0, '
           'https://zenodo.org/records/4012193', "permissive", 1300, 15, prepare_pack, 'about 400 MB'),
    # The land and the work done on it (packs/land_industry_packs.py): crops, weeds, litter, clouds, weather,
    # satellite views, industry, mining, energy and construction. Industrial accidents carry "content": "graphic".
    # The packs with people or droppings in them are not used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('agml_plant_health', 'Is this plant healthy? Crop leaves with a named disease or pest, Africa and Asia '
           '(17 datasets, ready-made pack)',
           'Each dataset CC BY 4.0 (Mendeley Data or Zenodo; iBean MIT)',
           'Crop disease datasets on Mendeley Data and Zenodo, CC BY 4.0 (iBean: MIT), from the Project-AgML copies, '
           'each credited in ATTRIBUTION.txt', "permissive", 4000, 20, prepare_pack, 'about 1.5 GB'),
    Source('agml_weeds', 'Weeds where they grow: Australia, India and Bangladesh (DeepWeeds, MH-Weed16, rice-field '
           'weeds, ready-made pack)',
           'CC BY 4.0 (each dataset)',
           'DeepWeeds, MH-Weed16 (Mendeley Data d3n3mgjjbv) and rice-field weeds of Bangladesh (Mendeley Data '
           'mt72bmxz73), CC BY 4.0, from the Project-AgML copies', "permissive", 2000, 15, prepare_pack,
           'about 600 MB'),
    Source('agml_harvest', 'Ready to pick? Banana bunches and dragon fruit (Mendeley Data, ready-made pack)',
           'CC BY 4.0 (Mendeley Data kjrsb7ztr9 and 2jpzbx8tm6)',
           'Banana Bunch Harvesting Dataset and Dragon Fruit Maturity dataset, Mendeley Data, CC BY 4.0',
           "permissive", 800, 10, prepare_pack, 'about 350 MB'),
    Source('gwhd_wheat', 'Wheat fields seen from above in 12 countries (Global Wheat Head Dataset 2021, ready-made '
           'pack)',
           'CC BY 4.0 (Zenodo 5092309)',
           'Global Wheat Head Dataset 2021 (David et al.), CC BY 4.0, https://doi.org/10.5281/zenodo.5092309',
           "permissive", 1300, 15, prepare_pack, 'about 600 MB'),
    Source('poultry_droppings', 'Do these chicken droppings show signs of disease? Farm photos from Tanzania '
           '(ready-made pack)',
           'CC BY 4.0 (Zenodo 4628934)',
           'Machine Learning Dataset for Poultry Diseases Diagnostics (Machuve et al.), CC BY 4.0, '
           'https://doi.org/10.5281/zenodo.4628934', "permissive", 1300, 15, prepare_pack, 'about 600 MB'),
    Source('inat_crops', 'Cultivated crops and fruit trees: wheat, rice, maize, cassava, coffee, tea and more '
           '(iNaturalist, ready-made pack)',
           'Each photo CC0 or CC BY (its iNaturalist page)',
           'iNaturalist observers, CC0 or CC BY, credited in ATTRIBUTION.txt', "permissive", 1600, 15, prepare_pack,
           'about 700 MB'),
    Source('trashnet', 'Which bin does it go in? Single pieces of rubbish (TrashNet, ready-made pack)',
           'MIT licence (github.com/garythung/trashnet)',
           'TrashNet (Gary Thung and Mindy Yang), MIT licence, https://github.com/garythung/trashnet', "permissive",
           1000, 10, prepare_pack, 'about 200 MB'),
    Source('taco_litter', 'Litter where it was dropped: woods, roads and beaches (TACO, ready-made pack)',
           'CC BY 4.0 (Zenodo 3587843)',
           'TACO: Trash Annotations in Context (Proenca and Simoes), CC BY 4.0, https://doi.org/10.5281/zenodo.3587843',
           "permissive", 1000, 10, prepare_pack, 'about 450 MB'),
    Source('ccsn_clouds', 'What kind of cloud is this? The sky in 11 cloud types and contrails (CCSN, ready-made pack)',
           'CC0 1.0 (Harvard Dataverse, doi 10.7910/DVN/CADDPD)',
           'Cirrus Cumulus Stratus Nimbus (CCSN) Database (Pu Liu), CC0, https://doi.org/10.7910/DVN/CADDPD',
           "permissive", 1700, 15, prepare_pack, 'about 200 MB'),
    Source('weather_images', 'What is the weather like? Cloudy, rainy, sunny and sunrise scenes (Multi-class Weather '
           'Dataset, ready-made pack)',
           'CC BY 4.0 (Mendeley Data 4drtyfjtfy)',
           'Multi-class Weather Dataset for Image Classification (Gbeminiyi Ajayi), CC BY 4.0, '
           'https://data.mendeley.com/datasets/4drtyfjtfy/1', "permissive", 700, 10, prepare_pack, 'about 150 MB'),
    Source('eurosat', 'Small satellite views of European land: crops, forest, rivers, motorways, housing (EuroSAT, '
           'ready-made pack)',
           'MIT licence (github.com/phelber/EuroSAT); contains modified Copernicus Sentinel data',
           'EuroSAT (Helber et al.), MIT licence, https://github.com/phelber/EuroSAT ; contains modified Copernicus '
           'Sentinel data', "permissive", 400, 10, prepare_pack, 'about 5 MB'),
    Source('commons_land_industry', 'Farming, the environment, factories, mines, energy and building sites (Wikimedia '
           'Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 20, prepare_pack,
           'about 1.2 GB'),
    Source('loc_haer', 'Dams, bridges, mines, mills, factories and railways with the survey\'s captions (Historic '
           'American Engineering Record, Library of Congress, ready-made pack)',
           'No known restrictions on images made by the U.S. Government (Library of Congress)',
           'Historic American Engineering Record, Library of Congress, Prints and Photographs Division', "permissive",
           2000, 15, prepare_pack, 'about 900 MB'),
    Source('plitter_street', 'Litter on streets in Thailand, Sri Lanka and the Mekong region, from vehicle cameras '
           '(pLitterStreet, ready-made pack)',
           'CC BY 4.0 (Zenodo 8288500)',
           'pLitterStreet (Mandhati, Deshapriya, Mendis and Gunasekara), CC BY 4.0, '
           'https://doi.org/10.5281/zenodo.8288500', "permissive", 1700, 15, prepare_pack, 'about 800 MB'),
    Source('plp_floating_targets', 'Floating plastic test targets off Lesvos, Greece, seen from a drone (Plastic Litter '
           'Projects, ready-made pack)',
           'CC BY 4.0 (Zenodo 3752719 and 7085112)',
           'PLP2019 (Topouzelis) and Plastic Litter Project 2021 (Papageorgiou and Topouzelis), University of the '
           'Aegean, CC BY 4.0', "permissive", 20, 10, prepare_pack, 'about 15 MB'),
    Source('usda_ars', 'Farm research, crops, insects and farm work with their captions (USDA Agricultural Research '
           'Service, ready-made pack)',
           'Public domain (US government work, USDA ARS image gallery)',
           'USDA Agricultural Research Service image gallery, public domain; credit: USDA ARS', "permissive", 200, 10,
           prepare_pack, 'about 90 MB'),
    # Practical home life (packs/home_packs.py): clock faces, seven-segment displays, household pests, appliances,
    # plugs and batteries, laundry symbols, tools, toiletries, hairstyles and the kitchen. Rows that may show a child
    # carry "child": true. The packs with people in them (hairstyles, head lice, worn jewellery and hats, Open Images
    # scenes) are not used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('clock_times', 'What time does this clock show? Analogue clocks in everyday photos (It\'s About Time, '
           'ready-made pack)',
           'Times: MIT licence (github.com/charigyang/itsabouttime); photos CC BY 2.0 or no known copyright '
           'restrictions (Open Images, COCO)',
           'It\'s About Time: Analog Clock Reading in the Wild (Charig Yang, Weidi Xie and Andrew Zisserman, CVPR '
           '2022), MIT licence; photos from Open Images V7 and COCO, each photographer credited in ATTRIBUTION.txt',
           "permissive", 870, 15, prepare_pack, 'about 400 MB'),
    Source('seven_segment', 'What number does this display show? Seven-segment LED and LCD displays (7SEG_OCR, '
           'ready-made pack)',
           'MIT licence (huggingface.co/datasets/MiXaiLL76/7SEG_OCR)',
           '7SEG_OCR by MiXaiLL76, MIT licence, https://huggingface.co/datasets/MiXaiLL76/7SEG_OCR', "permissive",
           2200, 15, prepare_pack, 'about 100 MB'),
    Source('open_images_home', 'Household pests, tools, devices, personal care, hairstyles and the kitchen in everyday '
           'photos (Open Images V7, ready-made pack)',
           'Labels CC BY 4.0; each photo CC BY 2.0, photographer named',
           'Open Images V7 (Google), labels CC BY 4.0; photos CC BY 2.0, each photographer credited in '
           'ATTRIBUTION.txt', "permissive", 2600, 20, prepare_pack, 'about 1.2 GB'),
    Source('commons_pests', 'Is there a bed bug here? Household pests, mould and damp (Wikimedia Commons, ready-made '
           'pack)',
           'Captions CC0; pictures CC0, public domain (including CDC, USDA and EPA photos) or CC BY, each author '
           'credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 600, 10, prepare_pack,
           'about 300 MB'),
    Source('commons_appliances', 'Thermostats, knobs, scales, meters, lift buttons and ticket machines (Wikimedia '
           'Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 470, 10, prepare_pack,
           'about 250 MB'),
    Source('commons_connectors', 'What kind of plug is this? Mains plugs and sockets, USB and other connectors, '
           'batteries and chargers (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 600, 10, prepare_pack,
           'about 300 MB'),
    Source('laundry_symbols', 'What does this laundry symbol mean? Care symbols, care labels and label photos '
           '(Wikimedia Commons, ready-made pack)',
           'CC0, public domain, CC BY or MIT (Tabler icons), file by file; the symbols are a GINETEX trademark',
           'Wikimedia Commons laundry symbol files (Tabler icons by Pawel Kuna, MIT licence), credited in '
           'ATTRIBUTION.txt', "permissive", 400, 10, prepare_pack, 'about 30 MB'),
    Source('commons_tools', 'Hand tools, power tools, screws, nails, plumbing parts and garden tools (Wikimedia '
           'Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 800, 15, prepare_pack,
           'about 400 MB'),
    Source('commons_personal', 'Toiletries, cosmetics, jewellery, watches, glasses, hats and bags (Wikimedia Commons, '
           'ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 670, 10, prepare_pack,
           'about 350 MB'),
    Source('commons_hairstyles', 'What hairstyle does this person have? Braids, cornrows, dreadlocks and more, adults '
           'only (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 400, 10, prepare_pack,
           'about 200 MB'),
    Source('commons_kitchen', 'Is the burner on? Cookers, flames, boiling water, utensils and cookware (Wikimedia '
           'Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 600, 10, prepare_pack,
           'about 300 MB'),
    # Historical events by place and time, and safety training (packs/events_safety_packs.py). Rows naming the dead or
    # wounded carry "content": "graphic". The event packs, the safety photos and the safety training photos show
    # people or hazards and are not used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('commons_events', 'What event does this picture show? Historical events of the whole world, with place and '
           'date from Wikidata (Wikimedia Commons, ready-made pack)',
           'Data and captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; event facts from Wikidata (CC0)', "permissive",
           2700, 20, prepare_pack, 'about 1.2 GB'),
    Source('loc_events', 'Parades, marches, inaugurations, funerals, fires and floods in news photos, about 1900-1945 '
           '(Bain and Harris & Ewing, Library of Congress, ready-made pack)',
           'No known restrictions on publication (Library of Congress)',
           'Library of Congress, Prints and Photographs Division: George Grantham Bain Collection and Harris & '
           'Ewing Collection', "permissive", 2000, 15, prepare_pack, 'about 900 MB'),
    Source('nara_events', 'Ceremonies, demonstrations, parades and other events in US government photographs (US '
           'National Archives, ready-made pack)',
           'Public domain (US government work, marked Unrestricted)',
           'U.S. National Archives and Records Administration, National Archives Catalog', "permissive", 1700, 15,
           prepare_pack, 'about 800 MB'),
    Source('europeana_events', 'Coronations, processions, funerals and festivals in old prints, drawings and photos '
           '(Europeana, ready-made pack)',
           'CC0, Public Domain Mark or CC BY, record by record',
           'Europeana partner museums and libraries, credited in ATTRIBUTION.txt', "permissive", 1000, 15,
           prepare_pack, 'about 500 MB'),
    Source('safety_signs', 'What does this sign mean? ISO 7010 safety signs, GHS hazard pictograms and road signs of '
           'many countries (Wikimedia Commons, ready-made pack)',
           'CC0, public domain or CC BY, file by file',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; GHS pictogram names from the UN Globally '
           'Harmonized System', "permissive", 1700, 15, prepare_pack, 'about 150 MB'),
    Source('commons_safety_photos', 'Fire extinguishers, defibrillators, exit signs and alarms, and hazards at home '
           'and in the street (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2700, 20, prepare_pack,
           'about 1.2 GB'),
    Source('safety_training', 'Safety posters and workplace safety photos (Library of Congress, OSHA, CDC, ready-made '
           'pack)',
           'Public domain or no known restrictions; Commons files CC0, public domain or CC BY, item by item',
           'Library of Congress (WPA Poster Collection, Prints and Photographs), Wikimedia Commons authors and US '
           'OSHA, CDC Public Health Image Library; credited in ATTRIBUTION.txt', "permissive", 800, 15,
           prepare_pack, 'about 400 MB'),
    Source('dfire_cameras', 'Is there fire or smoke? Frames from wildfire-watch cameras in Brazil (D-Fire, ready-made '
           'pack)',
           'CC0 1.0 (github.com/gaiasd/DFireDataset)',
           'D-Fire (Gaia, solutions on demand; de Venancio, Lisboa and Barbosa, 2022), CC0 1.0, '
           'https://github.com/gaiasd/DFireDataset', "permissive", 2700, 20, prepare_pack, 'about 600 MB'),
    # Safety around munitions and guns, and children's rites (packs/safety_rites_packs.py). Every munition answer
    # ends with a safety warning and every gun answer with a gun safety line; nothing says how to handle, fire or
    # disarm anything. Rows naming the dead or injured carry "content": "graphic" and are used only with
    # --with-graphic; rows of a child (mine-risk lessons, every rite pack row) carry "child". None of these packs is
    # used for picture-making (NOT_FOR_PICTURE_MAKING).
    Source('commons_munition_models', 'Is this a landmine? Landmine, grenade, shell, bomb and rocket models, with a '
           'safety warning (Wikimedia Commons with Wikidata, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited; facts from Wikidata (CC0)',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; facts from Wikidata, CC0', "permissive", 1000, 15,
           prepare_pack, 'about 450 MB'),
    Source('commons_uxo', 'Landmines, minefields, unexploded and loose munitions, demining and bomb disposal, with a '
           'safety warning (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1300, 15, prepare_pack,
           'about 600 MB'),
    Source('amlid_landmines', 'Mines on the ground seen from a drone, with a safety warning (AMLID, ready-made pack)',
           'CC BY 4.0 (Zenodo 18001447)',
           'Adaptive Multispectral Landmine Identification Dataset (AMLID), James Gallagher, Zenodo 18001447, CC BY '
           '4.0, https://zenodo.org/records/18001447', "permissive", 730, 10, prepare_pack, 'about 300 MB'),
    Source('commons_firearms', 'What gun is this? Pistols, revolvers, shotguns and rifles by model, maker and '
           'cartridge, with a gun safety line (Wikimedia Commons with Wikidata, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited; facts from Wikidata (CC0)',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; facts from Wikidata, CC0', "permissive", 2000, 15,
           prepare_pack, 'about 900 MB'),
    Source('commons_cartridges', 'What cartridge is this? Rimfire, centrefire and shotgun cartridges and their '
           'headstamps (Wikimedia Commons with Wikidata, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited; facts from Wikidata (CC0)',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; facts from Wikidata, CC0', "permissive", 1000, 15,
           prepare_pack, 'about 450 MB'),
    Source('commons_child_rites', 'Baptisms, christenings, brit milah, first communions, confirmations, bar and bat '
           'mitzvahs and other rites (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 800, 15, prepare_pack,
           'about 350 MB'),
    Source('europeana_child_rites', 'Baptisms, first communions and other rites in old photos (Europeana, ready-made '
           'pack)',
           'CC0, Public Domain Mark or CC BY, record by record',
           'Europeana partner museums and libraries, credited in ATTRIBUTION.txt', "permissive", 270, 10,
           prepare_pack, 'about 120 MB'),
    # Things and materials (packs/things_packs.py). abo_products rows carry "place_kind": "market" (the country of
    # the Amazon shop, not where the photo was taken; see PLACE_KINDS). The packs with people in them (Open Images and
    # Commons people using things, and Open Images technology photos, which often show people) are not used for
    # picture-making (NOT_FOR_PICTURE_MAKING); products, Commons things, bricks and building materials are.
    Source('abo_products', 'What is this? Electronics, tools, hardware, kitchen things and furniture from Amazon\'s '
           'catalogue in 19 countries (Amazon Berkeley Objects, ready-made pack)',
           'CC BY 4.0 (Amazon Berkeley Objects)',
           'Amazon Berkeley Objects: data and images by Amazon.com; dataset by Matthieu Guillaumin, Thomas '
           'Dideriksen, Kenan Deng, Himanshu Arora, Jasmine Collins and Jitendra Malik, CC BY 4.0', "permissive",
           2700, 20, prepare_pack, 'about 1.2 GB'),
    # Modern packaged goods (packs/packaged_goods_packs.py): the ABO catalogue photos of groceries, drinks, vitamins,
    # medicines, toiletries, cleaning products and pet food (rows carry "place_kind": "market", like abo_products),
    # and Open Images photos with a packaging label (often with people: not for picture-making). The personal-use FDA
    # recall photos and the collections looked at and left out are in packaged_goods_sources.py.
    Source('abo_packaged_goods', 'What is this? Packaged groceries, drinks, vitamins, medicines, toiletries, cleaning '
           'products and pet food, with brand, name and size, mostly from US and Canadian shops (Amazon Berkeley '
           'Objects, ready-made pack)',
           'CC BY 4.0 (Amazon Berkeley Objects)',
           'Amazon Berkeley Objects: data and images by Amazon.com; dataset by Matthieu Guillaumin, Thomas '
           'Dideriksen, Kenan Deng, Himanshu Arora, Jasmine Collins and Jitendra Malik, CC BY 4.0', "permissive",
           6000, 30, prepare_pack, 'about 2.7 GB'),
    Source('open_images_packaged_goods', 'What packaged goods are in this picture? Cans, bottles, cardboard packaging '
           'and ready meals in everyday photos (Open Images V7, ready-made pack)',
           'Labels CC BY 4.0 (Google Open Images); photos CC BY 2.0, each author credited',
           'Open Images V7 (Google), CC BY 4.0 labels; photos CC BY 2.0, credited in ATTRIBUTION.txt',
           "permissive", 500, 10, prepare_pack, 'about 150 MB'),
    # US state digital libraries and the Newberry Library (packs/state_collections_packs.py): only items whose own
    # rights statement is open, with no restricting words; people appear, so never for picture-making. The items with
    # no rights statement (or research-only words) are the personal-use entry in state_collections_personal_sources.py.
    Source("newberry_library", "Postcards, photographs, prints and maps of towns, buildings, landscapes and everyday "
           "life, mostly 1880 to 1950 (the Newberry Library, Chicago; ready-made pack)",
           "Each item's Rights Status No Copyright - United States (the Newberry's open access policy: any lawful use)",
           "From the Newberry Library, https://collections.newberry.org (each item credited in CREDITS.txt)",
           "permissive", 4000, 20, prepare_pack, "about 1.5 GB"),
    Source("state_libraries_midwest", "Towns, farms, buildings, work and daily life from Ohio, Indiana, Illinois, "
           "Wisconsin and North Dakota libraries and archives (state digital libraries, ready-made pack)",
           "Each item No Copyright - United States, No Known Copyright, Public Domain Mark, CC0 or CC BY (its own "
           "statement)", "Ohio Memory, Ball State University, Illinois Digital Archives, "
           "Ohio University, UW-Milwaukee and Digital Horizons (each item credited in CREDITS.txt)",
           "permissive", 3000, 20, prepare_pack, "about 1 GB"),
    Source("state_libraries_south", "Towns, farms, buildings, work and daily life from Georgia, Kentucky, Alabama "
           "and Maryland libraries and archives (state digital libraries, ready-made pack)",
           "Each item No Copyright - United States, No Known Copyright, Public Domain Mark, CC0 or CC BY (its own "
           "statement)", "The Digital Library of Georgia, Kentucky Digital Library, Auburn University, the Alabama "
           "Department of Archives and History and Digital Maryland (each item credited in CREDITS.txt)",
           "permissive", 3000, 20, prepare_pack, "about 1 GB"),
    Source("state_libraries_west", "Towns, farms, landscapes, work and daily life from Washington, New Mexico and "
           "Arizona university libraries (state digital libraries, ready-made pack)",
           "Each item No Copyright - United States, No Known Copyright, Public Domain Mark, CC0 or CC BY (its own "
           "statement)", "Washington State University, University of New Mexico and Northern Arizona University "
           "libraries (each item credited in CREDITS.txt)", "permissive", 2500, 20, prepare_pack, "about 800 MB"),
    Source('open_images_in_use', 'What is the person doing with it? People holding, using, playing, reading, eating '
           'and riding (Open Images V7, ready-made pack)',
           'Annotations CC BY 4.0 (Google Open Images); photos CC BY 2.0, each author credited',
           'Open Images V7 (Google), CC BY 4.0 annotations; photos CC BY 2.0, credited in ATTRIBUTION.txt',
           "permissive", 2700, 20, prepare_pack, 'about 1.2 GB'),
    Source('open_images_tech', 'Technology, electronics, building materials, workshop tools and kitchen gadgets in '
           'everyday photos (Open Images V7, ready-made pack)',
           'Labels CC BY 4.0; each photo CC BY 2.0, photographer named',
           'Open Images V7 (Google), labels CC BY 4.0; photos CC BY 2.0, each photographer credited in '
           'ATTRIBUTION.txt', "permissive", 2700, 20, prepare_pack, 'about 1.2 GB'),
    Source('commons_things', 'Electronic parts, devices, tools, building supplies and kitchen gadgets (Wikimedia '
           'Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1700, 15, prepare_pack,
           'about 800 MB'),
    Source('commons_in_use', 'People using laptops, tools, ladders and irons, cooking and at work (Wikimedia Commons, '
           'ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1000, 15, prepare_pack,
           'about 450 MB'),
    Source('brick_quality', 'What grade is this brick? First, second and third class, over-burnt and jhama bricks '
           '(Mendeley Data, ready-made pack)',
           'CC BY 4.0 (Mendeley Data n4wf5g4nrm)',
           'Brick quality grading dataset (Rahman, Iesmin, Noyon, Hasan, Rimi and Jahan), Mendeley Data n4wf5g4nrm, '
           'CC BY 4.0', "permissive", 1000, 15, prepare_pack, 'about 300 MB'),
    Source('codd_materials', 'Brick, concrete, tile, wood, pipe and other building waste at a recycling plant in '
           'Cyprus (CODD, ready-made pack)',
           'CC BY 4.0 (Mendeley Data wds85kt64j)',
           'CODD, Construction and Demolition Waste Object Detection Dataset (Demetriou, Mavromatidis, Petrou and '
           'Nicolaides), Mendeley Data wds85kt64j, CC BY 4.0', "permissive", 930, 15, prepare_pack, 'about 300 MB'),
    Source('nyuad_materials', 'What building material or surface is this? Concrete block, concrete, gypsum, mesh and '
           'plaster on a building site (NYU Abu Dhabi, ready-made pack)',
           'CC BY 4.0 (Mendeley Data zv66h54b8j)',
           'Construction material conditions (Mengiste, Mannem, Prieto and Garcia de Soto, NYU Abu Dhabi), Mendeley '
           'Data zv66h54b8j, CC BY 4.0', "permissive", 140, 10, prepare_pack, 'about 40 MB'),
    # Mechanical and automotive parts (packs/mechanical_packs.py): parts, engine bays, symbols, tyres, spark plugs and
    # gears, without people, so all are used for picture-making too.
    Source('commons_car_parts', 'What part is this? Car and lorry parts: engine, brakes, exhaust, gearbox, '
           'suspension, fluids (Wikimedia Commons, ready-made pack)', 'Captions CC0; pictures CC0, public domain or CC BY, each author credited', 'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2400, 20,
           prepare_pack, 'about 400 MB'),
    Source('commons_cycle_parts', 'What part is this? Bicycle, motorcycle and small-engine parts (Wikimedia Commons, '
           'ready-made pack)', 'Captions CC0; pictures CC0, public domain or CC BY, each author credited', 'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1700, 15, prepare_pack, 'about 300 MB'),
    Source('commons_machine_parts', 'What part is this? Bearings, gears, belts, valves, pumps, motors, fittings, '
           'plumbing, heating and air conditioning (Wikimedia Commons, ready-made pack)', 'Captions CC0; pictures CC0, public domain or CC BY, each author credited', 'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive",
           2400, 20, prepare_pack, 'about 400 MB'),
    Source('commons_engine_bays', 'Engine bays and where the battery, dipstick and other parts are, dashboards and '
           'gauges (Wikimedia Commons, ready-made pack)', 'Captions CC0; pictures CC0, public domain or CC BY, each author credited', 'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1000, 15, prepare_pack,
           'about 180 MB'),
    Source('iso_machine_symbols', 'What does this symbol mean? ISO 7000 machine symbols and dashboard warning lights '
           '(Wikimedia Commons, ready-made pack)', 'CC0 or public domain', 'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 1500, 15,
           prepare_pack, 'about 60 MB'),
    Source('corolla_engine_bay', 'Parts under the bonnet of a Toyota Corolla: battery, coolant, oil, fuses (Hugging '
           'Face, ready-made pack)', 'Apache-2.0 (stevenalbert10/Toyota-Corolla-Car-Parts)',
           'Toyota Corolla car parts dataset (stevenalbert10 on Hugging Face), Apache-2.0', "permissive", 1000, 15,
           prepare_pack, 'about 170 MB'),
    Source('tyre_condition', 'Is this tyre in good condition, and how far has it been driven? (Mendeley Data, '
           'ready-made pack)', 'CC BY 4.0 (Mendeley Data bn7ch8tvyp, 32b5vfj6tc and dfzbm2ktss)',
           'Tyre photos from Mendeley Data bn7ch8tvyp, 32b5vfj6tc (TyreNet) and dfzbm2ktss, CC BY 4.0, credited in '
           'ATTRIBUTION.txt', "permissive", 2800, 20, prepare_pack, 'about 450 MB'),
    Source('spark_plug_condition', 'Is this spark plug fouled or damaged? (Hugging Face, ready-made pack)',
           'BSD-3-Clause (eoinedge/spark-plug-classification)',
           'Spark plug classification dataset (eoinedge on Hugging Face), BSD-3-Clause', "permissive", 470, 10,
           prepare_pack, 'about 60 MB'),
    Source('planetary_gearbox', 'How many gears, and which? Planetary gearbox photos (Zenodo, ready-made pack)',
           'CC BY 4.0 (Zenodo 8223473)', 'Planetary gearbox images, Zenodo 8223473, CC BY 4.0', "permissive", 100, 10,
           prepare_pack, 'about 20 MB'),
    # People in daily activities (packs/people_activity_packs.py): what people are doing, from V-COCO and Visual
    # Genome (rows only: the photos are fetched from COCO, CC BY 2.0 or no known copyright), Open Images activity
    # labels, Commons daily-life and work categories and Dollar Street routines. All show people, so none is used for
    # picture-making (PEOPLE_AND_BODILY_PACK_KEYS). The non-commercial and share-alike COCO rows are in
    # people_activity_sources.py.
    Source('vcoco_actions', 'What is the person doing? Riding, holding, eating, reading, phoning and 20 more '
           'actions marked on COCO photos (V-COCO, ready-made pack)',
           'V-COCO MIT (github.com/s-gupta/v-coco); COCO boxes CC BY 4.0; photos CC BY 2.0 or no known copyright',
           'V-COCO (Gupta and Malik, 2015), MIT, https://github.com/s-gupta/v-coco; photos from COCO '
           '(cocodataset.org)', "permissive", 1700, 20, prepare_pack, 'about 300 MB (photos fetched from COCO)'),
    Source('vg_people_actions', 'What are the people doing? Relationships people drew on COCO photos (Visual '
           'Genome, ready-made pack)',
           'CC BY 4.0 (visualgenome.org); photos CC BY 2.0 or no known copyright',
           'Visual Genome (Krishna et al., 2017), CC BY 4.0, https://visualgenome.org; photos from COCO '
           '(cocodataset.org)', "permissive", 1700, 20, prepare_pack, 'about 300 MB (photos fetched from COCO)'),
    Source('open_images_activities', 'What is happening? Cooking, shopping, knitting, fishing, harvesting, a '
           'barber or a street vendor at work (Open Images V7, ready-made pack)',
           'Annotations CC BY 4.0 (Google Open Images); photos CC BY 2.0, each author credited',
           'Open Images V7 (Google), CC BY 4.0 annotations; photos CC BY 2.0, credited in ATTRIBUTION.txt',
           "permissive", 2700, 20, prepare_pack, 'about 1.8 GB'),
    Source('commons_daily_life', 'What is the person doing? Eating, reading, praying, queueing, carrying water, '
           'selling in the street and at work in about 70 countries (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2400, 20, prepare_pack,
           'about 500 MB'),
    Source('dollar_street_routines', 'Daily routines in homes around the world: washing hands and clothes, '
           'getting water, cleaning, guests at dinner (Dollar Street, ready-made pack)',
           'CC BY 4.0 (Gapminder Dollar Street), photographers credited',
           'Dollar Street by Gapminder, CC BY 4.0, https://www.gapminder.org/dollar-street', "permissive", 1100, 15,
           prepare_pack, 'about 250 MB'),
    # United States (packs/us_packs.py). The streets, cars and packaging packs show people (PEOPLE_AND_BODILY_PACK_KEYS).
    # The share-alike, non-commercial and research US collections are in us_sources.py.
    Source("loc_habs_houses", "American houses and rooms, outside and inside (Historic American Buildings Survey, ready-made pack)",
           "Public domain: no known restrictions on images made by the U.S. Government (https://www.loc.gov/rr/print/res/114_habs.html)",
           "Historic American Buildings Survey, Library of Congress, Prints and Photographs Division", "permissive", 3000, 20, prepare_pack, "about 600 MB"),
    Source("commons_us_homes", "US houses, house styles and rooms (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0",
           "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 4000, 20, prepare_pack, "about 700 MB"),
    Source("commons_us_streets", "US city streets and what people on them wear (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0",
           "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 3000, 20, prepare_pack, "about 500 MB"),
    Source("commons_us_cars", "Cars in the USA: which model, and its colour (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt)",
           "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2500, 20, prepare_pack, "about 450 MB"),
    Source("inaturalist_us", "Wild plants and animals in each US state, named (iNaturalist, ready-made pack)",
           "Photos CC0 or CC BY (each photographer credited in CREDITS.txt)",
           "iNaturalist contributors (photos CC0 or CC BY, credited in CREDITS.txt), https://www.inaturalist.org", "permissive", 5000, 20, prepare_pack, "about 750 MB"),
    Source("commons_us_money", "US banknotes and coins (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); the designs are US government work",
           "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1200, 10, prepare_pack, "about 200 MB"),
    Source("us_road_signs", "US road signs and what they mean (MUTCD drawings and photos, Wikimedia Commons, ready-made pack)",
           "Drawings public domain (US government work or simple shapes); photos CC0, public domain or CC BY",
           "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 150 MB"),
    Source("commons_packaging", "Packaged goods, packaging and US supermarkets (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0",
           "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2500, 20, prepare_pack, "about 400 MB"),
    # Modern America (packs/us_modern_packs.py). Agency photos, holidays, eating out, getting around and public places
    # show people (PEOPLE_AND_BODILY_PACK_KEYS); the share-alike entry and the C3PI pill photos are in us_modern_sources.py.
    Source("commons_us_agencies", "Modern American life in US government photos (USDA, FEMA, HUD, Forest Service; Wikimedia Commons, ready-made pack)",
           "Public domain (US government works); each Commons file checked: PD, CC0 or CC BY",
           "US federal agencies via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 4000, 20, prepare_pack, "about 800 MB"),
    Source("commons_us_controls", "Appliances, machines and controls: dishwashers, dryers, remotes, self-checkouts, card readers, pedestrian push buttons (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 400 MB"),
    Source("commons_us_holidays", "American holidays and events (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2500, 20, prepare_pack, "about 500 MB"),
    Source("commons_us_eating_out", "Diners, fast food, food trucks and food shops in the USA (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2500, 20, prepare_pack, "about 500 MB"),
    Source("commons_us_getting_around", "US subway, train and bus stations, airports, parking, gas and charging stations (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 3000, 20, prepare_pack, "about 600 MB"),
    Source("commons_us_public_places", "US post offices, banks, pharmacies, laundromats, hospitals, libraries and other public places (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 3000, 20, prepare_pack, "about 600 MB"),
    Source("us_federal_forms", "Blank US government forms: IRS, Medicare, OPM, VA, EEOC (ready-made pack)",
           "US government works, not subject to copyright (17 U.S.C. 105; irs.gov use-of-content page)",
           "IRS, CMS, OPM, VA and EEOC", "permissive", 200, 10, prepare_pack, "about 60 MB"),
    Source("imageinwords", "Photos with very detailed human descriptions (ImageInWords on DOCCI photos, ready-made pack)",
           "CC BY 4.0 (descriptions and photos, Google)",
           "ImageInWords (Garg et al., 2024) and DOCCI (Google), CC BY 4.0", "permissive", 500, 10, prepare_pack, "about 120 MB"),
    # Household devices (packs/device_packs.py): make, model and year from Wikidata product models, Commons device
    # categories and the Smithsonian's household devices. Files naming a person are left out. The share-alike and CO3D
    # entries are in device_sources.py.
    Source('wikidata_devices', 'What make and model is this? Household devices from Wikidata product models (ready-made pack)',
           'Data CC0 (Wikidata); captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt; model facts from Wikidata (CC0)', "permissive",
           2700, 20, prepare_pack, 'about 1.3 GB'),
    Source('commons_devices', 'VCRs, camcorders, Walkmans, answering machines, lawn tractors, fans and more (Wikimedia Commons, ready-made pack)',
           'Captions CC0; pictures CC0, public domain or CC BY, each author credited',
           'Wikimedia Commons authors, credited in ATTRIBUTION.txt', "permissive", 2200, 20, prepare_pack, 'about 600 MB'),
    Source('nmah_devices', 'Household devices in the National Museum of American History (Smithsonian, ready-made pack)',
           'CC0 (Smithsonian Open Access)', 'National Museum of American History, Smithsonian Institution, CC0',
           "permissive", 140, 10, prepare_pack, 'about 90 MB'),
    # Workplaces, farms and building mechanical systems in the US and Canada (packs/work_farm_mech_packs.py); the
    # share-alike entries are in work_farm_mech_sources.py.
    Source("work_commons_workplaces", "US and Canadian factories, warehouses, forklifts, pallet jacks, conveyors, machine shops and safety equipment (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1500, 20, prepare_pack, "about 500 MB"),
    Source("farm_commons_equipment", "Tractors, combines, balers, sprayers, silos, grain elevators, barns, milking parlours and greenhouses in the US and Canada (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2500, 20, prepare_pack, "about 850 MB"),
    Source("mech_commons_building", "Furnaces, boilers, air conditioners, ducts, well pumps, septic tanks, electrical panels, meters, propane tanks and chimneys (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1200, 20, prepare_pack, "about 400 MB"),
    Source("farm_usda_nrcs", "Conservation on US farms and ranches, with USDA NRCS captions (Wikimedia Commons, ready-made pack)",
           "Public domain (US government work); each Commons file checked",
           "USDA Natural Resources Conservation Service via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 3000, 20, prepare_pack, "about 1 GB"),
    # US state, county and city government photo streams copied to Commons (packs/state_packs.py); all show people.
    Source("commons_state_roads", "US state transportation and transit photos: roads, work zones, snowplows, bridges, buses and subways (Oregon DOT, NCDOT, MassDOT, Alaska DOT&PF, New York MTA; Wikimedia Commons, ready-made pack)",
           "Public domain or CC BY, each Commons file's own licence checked", "US state agencies via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 3500, 20, prepare_pack, "about 900 MB"),
    Source("commons_state_outdoors", "US state parks and wildlife agencies' photos: parks, trails, fish and wildlife (Virginia State Parks, Oregon and California Fish and Wildlife and more; Wikimedia Commons, ready-made pack)",
           "Public domain or CC BY, each Commons file's own licence checked", "US state agencies via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 3000, 20, prepare_pack, "about 750 MB"),
    Source("commons_state_response", "US state emergency response: National Guard and fire agencies in floods, fires, storms and vaccination (Wikimedia Commons, ready-made pack)",
           "Public domain or CC BY, each Commons file's own licence checked", "US state agencies via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 800, 10, prepare_pack, "about 200 MB"),
    Source("commons_state_community", "US cities, counties and state agencies at work in their communities (public works, events, redevelopment, archives; Wikimedia Commons, ready-made pack)",
           "Public domain or CC BY, each Commons file's own licence checked", "US state agencies via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 2500, 20, prepare_pack, "about 600 MB"),
    # Old US civil defense booklets and films (packs/civil_defense_packs.py); the UK, Canadian, Australian and NZ
    # material is in civil_defense_sources.py (research and non-commercial).
    Source("cd_booklets", "Drawings from US civil defense booklets, 1950 to 1985, with their captions (ready-made pack)",
           "Public domain (US government works, 17 U.S.C. 105)", "US civil defense agencies, via the Internet Archive, https://archive.org",
           "permissive", 1200, 20, prepare_pack, "about 150 MB"),
    Source("cd_films", "Stills from US civil defense films, 1950s to 1970s (ready-made pack)",
           "Public domain (public-domain mark or US government work)", "Prelinger Archives and US government films, via the Internet Archive, https://archive.org",
           "permissive", 1200, 20, prepare_pack, "about 120 MB"),
    # Non-profits and field manuals (packs/ngo_packs.py, packs/field_manual_packs.py).
    Source("owid_charts", "Charts from Our World in Data: what each chart shows and where its data come from (ready-made pack)",
           "CC BY 4.0 (https://ourworldindata.org/faqs)", "Our World in Data (Global Change Data Lab), CC BY 4.0 (each chart's page in CREDITS.txt)", "permissive", 3000, 20, prepare_pack, "about 250 MB"),
    Source("field_manual_figures", "Drawings from US Army field manuals and Navy training courses: knots, shelters, compasses, maps, machines, circuits, first aid (ready-made pack)",
           "Public domain (US government works, Distribution Statement A)", "US Army and US Navy; copies from the Internet Archive (credited in CREDITS.txt)", "permissive", 2500, 20, prepare_pack, "about 200 MB"),
    # Open sets from big technology companies (packs/bigtech_packs.py); none shows people. The research entries
    # (ScreenQA, PixMo, FinTabNet) are in bigtech_sources.py.
    Source("gso_objects", "What is this? Real products scanned in 3D by Google, computer-made views (Google Scanned Objects, ready-made pack)",
           "CC BY 4.0 (each model on Gazebo Fuel)", "Google Scanned Objects (Downs et al., Google Research, 2022), CC BY 4.0, https://app.gazebosim.org/GoogleResearch/fuel/models",
           "permissive", 2000, 20, prepare_pack, "about 60 MB"),
    Source("oi_crowdsourced", "Everyday things photographed by people around the world, mostly in India (Open Images Extended crowdsourced, ready-made pack)",
           "Each photo CC BY 4.0 with its giver's name; labels CC BY 4.0 (Google)", "Google Crowdsource givers (credited in CREDITS.txt); Open Images Extended (Google)",
           "permissive", 4000, 20, prepare_pack, "about 1.5 GB"),
    Source("pubtabnet_tables", "Tables from scientific articles, read out (PubTabNet, IBM; CC BY and CC0 articles only, ready-made pack)",
           "Annotations CDLA-Permissive-1.0 (IBM); each table from a CC BY or CC0 PubMed Central article", "PubTabNet (Zhong et al., IBM Research, 2020) and the articles' authors (credited in CREDITS.txt)",
           "permissive", 3000, 20, prepare_pack, "about 80 MB"),
    # Colleges and universities (packs/university_packs.py); DPLA CC BY-SA / BY-NC entries are in university_sources.py.
    Source("dpla_campus", "Campus life, college towns, farms and everyday scenes from US college and university libraries (Digital Public Library of America, ready-made pack)",
           "Each item No Copyright - United States, Public Domain Mark, CC0 or CC BY (its rights URI in DPLA); metadata CC0",
           "US college and university libraries via the Digital Public Library of America (credited in CREDITS.txt), https://dp.la", "permissive", 4000, 20, prepare_pack, "about 2 GB"),
    Source("commons_college_streams", "US college life since 1990: classes, sports, campus events and buildings, from colleges' own photo streams (Wikimedia Commons, ready-made pack)",
           "Public domain or CC BY, each file checked (credited in CREDITS.txt); captions by the colleges",
           "Wikimedia Commons copies of US colleges' photo streams (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 3000, 20, prepare_pack, "about 1.2 GB"),
    Source("commons_university_archives", "Everyday life about 1860 to 1960 in Washington, Ohio, the Prairies and Texas, from university libraries (Wikimedia Commons, ready-made pack)",
           "No known copyright restrictions or public domain (each file checked); descriptions from the libraries' records",
           "University of Washington, Miami University, University of Alberta and SMU libraries via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 2500, 15, prepare_pack, "about 900 MB"),
    # Canada (packs/canada_packs.py): Canadian equivalents of the US packs. The share-alike, non-commercial and research
    # Canadian collections are in canada_sources.py.
    Source("commons_ca_homes", "Canadian houses, house styles and rooms (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2500, 20, prepare_pack, "about 500 MB"),
    Source("commons_ca_streets", "Canadian city streets, including Québec (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("commons_ca_cars", "Cars in Canada: which model, and its colour (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1200, 20, prepare_pack, "about 250 MB"),
    Source("inaturalist_ca", "Wild plants and animals in each province and territory, named (iNaturalist) (ready-made pack)",
           "Photos CC0 or CC BY (each photographer credited in CREDITS.txt)",
           "iNaturalist contributors (photos CC0 or CC BY, credited in CREDITS.txt), https://www.inaturalist.org", "permissive", 4000, 20, prepare_pack, "about 600 MB"),
    Source("commons_ca_money", "Canadian banknotes and coins (old designs out of copyright, and freely licensed files) (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 600, 20, prepare_pack, "about 100 MB"),
    Source("ca_road_signs", "Canadian road signs, including Québec's French signs (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1500, 20, prepare_pack, "about 120 MB"),
    Source("commons_ca_shops", "Canadian shops and supermarkets, dépanneurs and chains (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 800, 20, prepare_pack, "about 180 MB"),
    Source("commons_ca_holidays", "Canadian holidays and events: Canada Day, Thanksgiving, Victoria Day, Remembrance Day, Saint-Jean-Baptiste (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1500, 20, prepare_pack, "about 350 MB"),
    Source("commons_ca_eating_out", "Coffee shops, diners and eating out in Canada (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1200, 20, prepare_pack, "about 250 MB"),
    Source("commons_ca_getting_around", "Getting around Canada: TTC, STM, TransLink, GO Transit, VIA Rail, ferries and airports (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("commons_ca_public_places", "Canadian public places: pharmacies, post offices, libraries, service centres (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("commons_ca_archives", "Canadian archive photos: Library and Archives Canada, Toronto, BAnQ (Commons copies under open licences) (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 3000, 20, prepare_pack, "about 700 MB"),
    Source("commons_ca_provincial", "Provincial and territorial government photos under their open licences (Ontario, Alberta, BC, New Brunswick, Yukon) (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1500, 20, prepare_pack, "about 350 MB"),
    Source("commons_ca_daily_life", "Everyday life in Canada: winter, skating, pond hockey, camping, cottage country, commuting, markets (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (OGL-Canada or provincial; credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    # A US state agency's own data feed (packs/state_web_packs.py): Caltrans traffic camera stills (people distant).
    Source("caltrans_cctv", "California highway traffic camera pictures (Caltrans; ready-made pack)",
           "Public domain (California public records; Caltrans Conditions of Use)", "California Department of Transportation (Caltrans), https://cwwp2.dot.ca.gov", "permissive", 2000, 20, prepare_pack, "about 50 MB"),
    # Current medicines, medical supplies and instruments and veterinary medicines (packs/med_vet_packs.py): nothing old
    # or from museum collections. Medicine answers say "This looks like ..." and end "Check the packaging or ask a
    # pharmacist to be sure." The share-alike, Open Facts supplements and DailyMed label entries are in med_vet_sources.py.
    Source("med_commons_supplies", "Medical supplies at home: bandages, syringes, insulin pens, inhalers, ice packs, pill organizers and more (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 500 MB"),
    Source("med_commons_instruments", "Surgical and medical instruments: scissors, forceps, clamps, scalpels, stethoscopes (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 600, 10, prepare_pack, "about 150 MB"),
    Source("med_commons_medicines", "Current medicines: tablets, capsules, blister packs, bottles and creams (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1500, 20, prepare_pack, "about 350 MB"),
    Source("vet_commons_medicine", "Veterinary medicines and animal care: pet and livestock medicines, ear tags, vet clinics (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 500, 10, prepare_pack, "about 120 MB"),
    Source("dental_instruments", "Dental and surgical instruments, one per photo: 22 kinds (Mendeley Data mh6zpc7y9g, ready-made pack)",
           "CC BY 4.0 (Mendeley Data mh6zpc7y9g)", "Dental instruments image set, Mendeley Data mh6zpc7y9g, CC BY 4.0",
           "permissive", 800, 20, prepare_pack, "about 300 MB"),
    Source("open_images_medical", "Medical things in everyday photos: gloves, masks, braces, stretchers, wheelchairs (Open Images V7, ready-made pack)",
           "Labels CC BY 4.0 (Google Open Images); photos CC BY 2.0, each author credited",
           "Open Images V7 (Google), CC BY 4.0 labels; photos CC BY 2.0, credited in ATTRIBUTION.txt", "permissive", 900, 20,
           prepare_pack, "about 400 MB"),
    Source("cdc_phil_supplies", "Medical supplies and protective equipment in CDC photos, 2000 or later (CDC Public Health Image Library, ready-made pack)",
           "Public domain (CDC PHIL items marked 'Permission is not required for public domain images')",
           "Centers for Disease Control and Prevention, Public Health Image Library (public domain)", "permissive", 400, 10,
           prepare_pack, "about 150 MB"),
    # Drugs, counterfeit pills and paraphernalia, and firearms and firearm accessories (packs/drug_firearm_packs.py).
    # Drug answers end "Drugs cannot be identified for sure by how they look ..."; gun answers "Treat every gun as
    # loaded ...". Never used for picture-making (DRUG_FIREARM_PACK_KEYS); the share-alike entry is in
    # drug_firearm_sources.py.
    Source("commons_drugs", "Drugs and counterfeit pills: cannabis, cocaine, heroin, meth, ecstasy tablets, fentanyl, seized drugs (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 800, 20, prepare_pack, "about 200 MB"),
    Source("commons_drug_paraphernalia", "Bongs, pipes, hookahs, vapes, rolling papers, grinders and drug paraphernalia (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1000, 20, prepare_pack, "about 250 MB"),
    Source("commons_cbp_seizures", "Drug seizures in US Customs and Border Protection photos (Wikimedia Commons copies, ready-made pack)",
           "Public domain (works of the US government, 17 U.S.C. 105); each Commons file's licence checked",
           "US Customs and Border Protection via Wikimedia Commons (credited in CREDITS.txt)", "permissive", 300, 10, prepare_pack, "about 80 MB"),
    Source("cdc_phil_drugs", "Street drugs, paraphernalia and e-cigarettes in CDC photos (CDC Public Health Image Library, ready-made pack)",
           "Public domain (CDC PHIL items marked 'Permission is not required for public domain images')",
           "Centers for Disease Control and Prevention, Public Health Image Library (public domain)", "permissive", 60, 5,
           prepare_pack, "about 15 MB"),
    Source("commons_firearm_accessories", "Gun accessories: holsters, speedloaders, scopes, red dot sights, lights, lasers, slings, suppressors, cases, safes and trigger locks (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 1500, 20, prepare_pack, "about 350 MB"),
    Source("commons_firearm_kinds", "Kinds of guns and their makers: revolvers, pistols, shotguns, rifles, flintlocks, air guns (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0", "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org", "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("wikidata_firearms", "What make and model of gun is this? Firearm models from Wikidata (ready-made pack)",
           "Data CC0 (Wikidata); captions CC0; pictures CC0, public domain or CC BY, each author credited",
           "Wikimedia Commons authors, credited in CREDITS.txt; model facts from Wikidata (CC0)", "permissive", 500, 10,
           prepare_pack, "about 120 MB"),
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
    # Fine-art nudity that art_nudes leaves out, and erotic art showing adults (packs/adult_art_packs.py). Labelled
    # collections: museum_art_nudes only with --with-nudity, erotic_art only with --with-sexual (which needs
    # --with-nudity; the add-on is then personal use only, see train.py). Never for picture-making
    # (ADULT_ART_PACK_KEYS). No photographs of people in either; any record naming or suggesting a young person is
    # left out of erotic_art, and of museum_art_nudes whenever it has a sexual or romantic word.
    Source("museum_art_nudes", "More nudes in art and life drawings: Madonna and Child, putti, mythology, lovers, classical statues, academic studies (ready-made pack)",
           "CC0, public domain or CC BY, item by item (The Met, Art Institute of Chicago, Cleveland, National Gallery "
           "of Art, Smithsonian, Minneapolis Institute of Art, SMK, Rijksmuseum, Europeana partners; each work "
           "credited in the pack's CREDITS.txt)",
           "Fine-art nudes from The Metropolitan Museum of Art, the Art Institute of Chicago, the Cleveland Museum of "
           "Art, the National Gallery of Art (Washington), the Smithsonian Institution, the Minneapolis Institute of "
           "Art, Statens Museum for Kunst, the Rijksmuseum and Europeana partners, each work credited with its "
           "licence in CREDITS.txt", "permissive", 2000, 10, prepare_pack, "about 400 MB", content="nudity"),
    Source("erotic_art", "Erotic art showing adults: shunga, Indian and Persian painting, Greek and Roman art, temple sculpture, European prints, sex-education drawings (ready-made pack)",
           "Public domain, CC0 or CC BY, item by item (The Met, Art Institute of Chicago, Cleveland Museum of Art, "
           "Wellcome Collection, Wikimedia Commons; each credited in the pack's CREDITS.txt)",
           "The Metropolitan Museum of Art, Art Institute of Chicago, Cleveland Museum of Art (CC0); Wellcome "
           "Collection (public domain, CC0 or CC BY 4.0); Wikimedia Commons authors (CC0, public domain or CC BY); "
           "each item credited in CREDITS.txt", "permissive", 1500, 10, prepare_pack, "about 300 MB",
           content="sexual"),
    Source("nude_photo_studies", "Non-sexual nude photographs: studio, art-school, medical and anthropometric studies of adults (Wellcome Collection, ready-made pack)",
           "Public domain, CC0 or CC BY 4.0, item by item (Wellcome Collection; each credited in the pack's "
           "CREDITS.txt)", "Wellcome Collection, credited in CREDITS.txt", "permissive", 300, 5, prepare_pack,
           "about 60 MB", content="nudity"),
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
           with_research=False, with_sexual=False, with_graphic=False):
    """The sources to train on: the permissive ones; the share-alike ones too with with_wikipedia; the
    "noncommercial" ones with with_noncommercial and the "research" ones with with_research (both for personal use
    only). A collection with content "nudity" is only included with with_nudity, and one with content "medical" only
    with with_medical; "intimate" needs both, "sexual" with_sexual and with_nudity, and "graphic" with_graphic
    (allowed_contents). A collection of any other group is never included. (Single rows tagged with a content the
    choices do not allow are left out later, by keep_allowed.)"""
    allowed = allowed_contents(with_nudity, with_medical, with_sexual, with_graphic)
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
# The graphic-scenes packs (packs/graphic_packs.py): war, disasters, injuries and death. A picture-making model never
# learns from them at all, not even from their rows that are not marked graphic.
GRAPHIC_PACK_KEYS = ("loc_civil_war", "loc_war_disaster", "nara_war", "ushmm", "commons_war", "commons_disasters",
                     "commons_safety")
NOT_FOR_PICTURE_MAKING = NOT_FOR_PICTURE_MAKING + GRAPHIC_PACK_KEYS
# Packs whose rows show people (soldiers, uniformed services, athletes, festivals, workers, street scenes, people with
# mobility aids), weapons, or medical and bodily material (blood, vomit, stool, urine, droppings): describing only.
# The other packs of those groups may be used for picture-making: civil aircraft, musical instruments, places of
# worship, landmarks and architecture, vehicle models, toys, cards, chess and sheet music, crops, weeds, litter,
# clouds, weather and satellite views.
PEOPLE_AND_BODILY_PACK_KEYS = (
    # service_packs.py: soldiers and uniformed services, weapons and war (all but commons_airplanes)
    "commons_military", "commons_uniformed", "loc_service", "nara_military", "army_mil", "nasm_aircraft",
    "nmah_service",
    # bodily_packs.py: bodily fluids and waste (all of them)
    "scatspotter", "inat_droppings", "open_images_bodily", "commons_bodily", "case_report_bodily", "urine_samples",
    # culture_packs.py: people playing sport, at festivals and ceremonies, and in street vehicles
    "open_images_culture", "wikidata_sports", "commons_religious_life", "commons_vehicle_kinds",
    # land_industry_packs.py: farm and factory workers, street scenes, and droppings
    "poultry_droppings", "commons_land_industry", "loc_haer", "plitter_street", "usda_ars",
    # disability_packs.py: people using wheelchairs, canes, guide dogs and other aids (tactile paving is used)
    "open_images_disability", "commons_disability",
    # home_packs.py: hairstyles, head lice and other pests on people, worn jewellery, glasses and hats, and Open
    # Images scenes with people (clocks, displays, appliances, plugs, laundry symbols, tools and the kitchen are used)
    "open_images_home", "commons_pests", "commons_personal", "commons_hairstyles",
    # events_safety_packs.py: event crowds, graphic war and disaster rows, hazards and workers (safety signs and the
    # D-Fire wildfire cameras are used)
    "commons_events", "loc_events", "nara_events", "europeana_events", "commons_safety_photos", "safety_training",
    # safety_rites_packs.py: munitions, firearms, cartridges and children's rites (all of them)
    "commons_munition_models", "commons_uxo", "amlid_landmines", "commons_firearms", "commons_cartridges",
    "commons_child_rites", "europeana_child_rites",
    # things_packs.py: people using things, and Open Images technology photos, which often show people (products,
    # Commons things, bricks and building materials are used)
    "open_images_in_use", "commons_in_use", "open_images_tech",
    # people_activity_packs.py: people in daily activities (all of them)
    "vcoco_actions", "vg_people_actions", "open_images_activities", "commons_daily_life", "dollar_street_routines",
    # us_packs.py: street people, people by cars, shop photos
    "commons_us_streets", "commons_us_cars", "commons_packaging",
    # us_modern_packs.py: agency photos, holidays, eating out, getting around, public places (controls, forms and
    # ImageInWords are used)
    "commons_us_agencies", "commons_us_holidays", "commons_us_eating_out", "commons_us_getting_around",
    "commons_us_public_places",
    # work_farm_mech_packs.py: workers at work and NRCS field photos (the farm and building packs are used)
    "work_commons_workplaces", "farm_usda_nrcs",
    # state_packs.py: US state, county and city government photos (all of them)
    "commons_state_roads", "commons_state_outdoors", "commons_state_response", "commons_state_community",
    # med_vet_packs.py: Open Images and CDC photos of people using medical things
    "open_images_medical", "cdc_phil_supplies",
    # canada_packs.py: Canadian streets, cars, shops, holidays, eating out, transit, public places, archives, daily life
    "commons_ca_streets", "commons_ca_cars", "commons_ca_shops", "commons_ca_holidays",
    "commons_ca_eating_out", "commons_ca_getting_around", "commons_ca_public_places", "commons_ca_archives",
    "commons_ca_provincial", "commons_ca_daily_life",
    # university_packs.py: campus life, students and townspeople (all of them)
    "dpla_campus", "commons_college_streams", "commons_university_archives",
    # state_web_packs.py: traffic camera views (people and cars far away)
    "caltrans_cctv",
    # field_manual_packs.py: many drawings show soldiers
    "field_manual_figures",
    # civil_defense_packs.py: civil defense booklets and film stills (people, attack, schoolchildren)
    "cd_booklets", "cd_films",
    # drug_firearm_packs.py: CBP seizure photos (officers) and CDC PHIL drug photos
    "commons_cbp_seizures", "cdc_phil_drugs",
    # adult_art_packs.py: nudes and erotic art (both of them)
    "museum_art_nudes", "erotic_art", "nude_photo_studies",
    # packaged_goods_packs.py: Open Images packaging photos, which often show people (the ABO catalogue photos of
    # packaged goods are used)
    "open_images_packaged_goods",
    # state_collections_packs.py: state digital libraries and the Newberry (people at work and in daily life)
    "newberry_library", "state_libraries_midwest", "state_libraries_south", "state_libraries_west",
)
NOT_FOR_PICTURE_MAKING = NOT_FOR_PICTURE_MAKING + PEOPLE_AND_BODILY_PACK_KEYS
# The drug and firearm packs (packs/drug_firearm_packs.py): describing only, never for picture-making, whether or not
# they show people (the two that do are in PEOPLE_AND_BODILY_PACK_KEYS too).
DRUG_FIREARM_PACK_KEYS = ("commons_drugs", "commons_drug_paraphernalia", "commons_cbp_seizures", "cdc_phil_drugs",
                          "commons_firearm_accessories", "commons_firearm_kinds", "wikidata_firearms")
NOT_FOR_PICTURE_MAKING = NOT_FOR_PICTURE_MAKING + tuple(k for k in DRUG_FIREARM_PACK_KEYS
                                                        if k not in NOT_FOR_PICTURE_MAKING)
# The nudes and erotic art packs (packs/adult_art_packs.py): describing only, never for picture-making (they are in
# PEOPLE_AND_BODILY_PACK_KEYS too).
ADULT_ART_PACK_KEYS = ("museum_art_nudes", "erotic_art", "nude_photo_studies")
NOT_FOR_PICTURE_MAKING = NOT_FOR_PICTURE_MAKING + tuple(k for k in ADULT_ART_PACK_KEYS
                                                        if k not in NOT_FOR_PICTURE_MAKING)
# The documented-adult photographs (adult_photo_review.py, gathered on the owner's own computer): review workspaces
# (never used for picture-making in any case: own_data leaves review pictures out of it), listed here too.
NOT_FOR_PICTURE_MAKING = NOT_FOR_PICTURE_MAKING + ("adult_photo_review",)


def content_of(key):
    """The content choice ("", "nudity", "medical", "intimate", "sexual" or "graphic") of the collection with this key
    ("" when unknown)."""
    return next((s.content for s in SOURCES if s.key == key), "")


def content_choices_text(with_nudity, with_medical, with_sexual=False, with_graphic=False):
    """The content choices in one plain sentence, for the report and ATTRIBUTION.txt: art with nudity, medical
    pictures, intimate medical pictures (only with both), adult sexual content (only with with_sexual and art with
    nudity; personal use only) and graphic scenes (war, disasters, injuries and death)."""
    allowed = allowed_contents(with_nudity, with_medical, with_sexual, with_graphic)
    return ("Content choices: art with nudity (non-sexual) " + ("included" if with_nudity else "not included") +
            "; medical and anatomy pictures " + ("included" if with_medical else "not included") +
            "; intimate medical pictures from reviewed collections (needs both) " +
            ("included" if "intimate" in allowed else "not included") +
            "; adult sexual content from reviewed collections " +
            ("included (personal use only)" if "sexual" in allowed else "not included") +
            "; graphic scenes (war, disasters, injuries and death, described plainly) " +
            ("included" if "graphic" in allowed else "not included") + ".")


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

# Graphic-scene collections that are not open (share-alike Commons files of war, disaster and safety scenes; the
# Imperial War Museums' photographs for personal use): war, disasters, injuries and death. A collection marked
# content "graphic" is used only with the graphic-scenes choice (--with-graphic), and a picture-making model never
# learns from any of them; the file may be missing.
try:
    import graphic_sources as _graphic  # noqa: E402
except ImportError as _e:
    _graphic = None
    if getattr(_e, "name", None) != "graphic_sources":
        say(f"(The graphic-scene collections could not be loaded: {_e}. They are left out.)")
GRAPHIC_SOURCES = list(getattr(_graphic, "GRAPHIC_SOURCES", []) or [])
_graphic_ok = set(getattr(_graphic, "GRAPHIC_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _graphic_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in GRAPHIC_SOURCES if s.key not in _graphic_ok)
_add_collections(GRAPHIC_SOURCES)

# More archive, museum and news-photo collections that are not open (the V&A and Digital Commonwealth's CC BY-NC-ND
# photos for personal use, Agência Brasil's journalistic-use photos); the file may be missing.
try:
    import archive_sources as _archive  # noqa: E402
except ImportError as _e:
    _archive = None
    if getattr(_e, "name", None) != "archive_sources":
        say(f"(The archive collections could not be loaded: {_e}. They are left out.)")
ARCHIVE_SOURCES = list(getattr(_archive, "ARCHIVE_SOURCES", []) or [])
_archive_ok = set(getattr(_archive, "ARCHIVE_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _archive_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in ARCHIVE_SOURCES if s.key not in _archive_ok)
_add_collections(ARCHIVE_SOURCES)

# Military and uniformed-services collections that are not open (share-alike Commons files of military models,
# weapons, civil aircraft and uniforms, Bundesarchiv photos, Europeana 1914-1918); the file may be missing.
try:
    import service_sources as _service  # noqa: E402
except ImportError as _e:
    _service = None
    if getattr(_e, "name", None) != "service_sources":
        say(f"(The military and uniformed-services collections could not be loaded: {_e}. They are left out.)")
SERVICE_SOURCES = list(getattr(_service, "SERVICE_SOURCES", []) or [])
_service_ok = set(getattr(_service, "SERVICE_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _service_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in SERVICE_SOURCES if s.key not in _service_ok)
_add_collections(SERVICE_SOURCES)

# Bodily fluid and waste collections that are not open (share-alike Commons and iNaturalist files, non-commercial
# iNaturalist droppings, blood stain patterns for personal use); human medical ones are marked "medical". None is for
# picture-making; the file may be missing.
try:
    import bodily_sources as _bodily  # noqa: E402
except ImportError as _e:
    _bodily = None
    if getattr(_e, "name", None) != "bodily_sources":
        say(f"(The bodily fluid and waste collections could not be loaded: {_e}. They are left out.)")
BODILY_SOURCES = list(getattr(_bodily, "BODILY_SOURCES", []) or [])
_bodily_ok = set(getattr(_bodily, "BODILY_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _bodily_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in BODILY_SOURCES if s.key not in _bodily_ok)
_add_collections(BODILY_SOURCES)

# Sport, music, religion, landmark, vehicle and game collections that are not open, and LEGO parts (open, but read
# from parquet files rather than a pack); the file may be missing.
try:
    import culture_sources as _culture  # noqa: E402
except ImportError as _e:
    _culture = None
    if getattr(_e, "name", None) != "culture_sources":
        say(f"(The sport, music, religion and landmark collections could not be loaded: {_e}. They are left out.)")
CULTURE_SOURCES = list(getattr(_culture, "CULTURE_SOURCES", []) or [])
_culture_ok = set(getattr(_culture, "CULTURE_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _culture_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in CULTURE_SOURCES if s.key not in _culture_ok)
_add_collections(CULTURE_SOURCES)

# Farming, environment, industry and mining collections that are not open (share-alike Commons files and plant
# seedlings, non-commercial weed and crop sets); the file may be missing.
try:
    import land_industry_sources as _land  # noqa: E402
except ImportError as _e:
    _land = None
    if getattr(_e, "name", None) != "land_industry_sources":
        say(f"(The farming, environment and industry collections could not be loaded: {_e}. They are left out.)")
LAND_SOURCES = list(getattr(_land, "LAND_SOURCES", []) or [])
_land_ok = set(getattr(_land, "LAND_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _land_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in LAND_SOURCES if s.key not in _land_ok)
_add_collections(LAND_SOURCES)

# Home-life collections that are not open (Open Beauty, Products and Pet Food Facts, share-alike Commons home and
# hairstyle files, DTD patterns); the file may be missing.
try:
    import home_sources as _home  # noqa: E402
except ImportError as _e:
    _home = None
    if getattr(_e, "name", None) != "home_sources":
        say(f"(The home-life collections could not be loaded: {_e}. They are left out.)")
HOME_SOURCES = list(getattr(_home, "HOME_SOURCES", []) or [])
_home_ok = set(getattr(_home, "HOME_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _home_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in HOME_SOURCES if s.key not in _home_ok)
_add_collections(HOME_SOURCES)

# Historical-event and safety collections that are not open (share-alike Commons event, safety and hazard files,
# research PPE sets and D-Fire's web pictures); the file may be missing.
try:
    import events_safety_sources as _events_safety  # noqa: E402
except ImportError as _e:
    _events_safety = None
    if getattr(_e, "name", None) != "events_safety_sources":
        say(f"(The historical-event and safety collections could not be loaded: {_e}. They are left out.)")
EVENTS_SAFETY_SOURCES = list(getattr(_events_safety, "EVENTS_SAFETY_SOURCES", []) or [])
_events_safety_ok = set(getattr(_events_safety, "EVENTS_SAFETY_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _events_safety_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in EVENTS_SAFETY_SOURCES if s.key not in _events_safety_ok)
_add_collections(EVENTS_SAFETY_SOURCES)

# Munition, firearm and children's-rite collections that are not open (share-alike Commons landmine, firearm and rite
# files, and MineInsight's demining robot pictures); the file may be missing. None is used for picture-making
# (SAFETY_RITES_PICTURE_MAKING_OK is empty).
try:
    import safety_rites_sources as _safety_rites  # noqa: E402
except ImportError as _e:
    _safety_rites = None
    if getattr(_e, "name", None) != "safety_rites_sources":
        say(f"(The munition, firearm and rite collections could not be loaded: {_e}. They are left out.)")
SAFETY_RITES_SOURCES = list(getattr(_safety_rites, "SAFETY_RITES_SOURCES", []) or [])
_safety_rites_ok = set(getattr(_safety_rites, "SAFETY_RITES_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _safety_rites_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in SAFETY_RITES_SOURCES if s.key not in _safety_rites_ok)
_add_collections(SAFETY_RITES_SOURCES)

# Drug and firearm collections that are not open (share-alike Commons drug, paraphernalia, accessory and gun-kind
# files); the file may be missing. None is used for picture-making (DRUG_FIREARM_PICTURE_MAKING_OK is empty).
try:
    import drug_firearm_sources as _drug_firearm  # noqa: E402
except ImportError as _e:
    _drug_firearm = None
    if getattr(_e, "name", None) != "drug_firearm_sources":
        say(f"(The drug and firearm collections could not be loaded: {_e}. They are left out.)")
DRUG_FIREARM_SOURCES = list(getattr(_drug_firearm, "DRUG_FIREARM_SOURCES", []) or [])
_drug_firearm_ok = set(getattr(_drug_firearm, "DRUG_FIREARM_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _drug_firearm_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in DRUG_FIREARM_SOURCES if s.key not in _drug_firearm_ok)
_add_collections(DRUG_FIREARM_SOURCES)

# The Princeton University Art Museum's nudes, figure studies and erotic art: personal use only (no rights statement
# on its records), downloaded on the owner's computer with the open packs' rules; the file may be missing. Never used
# for picture-making.
try:
    import princeton_personal_sources as _princeton  # noqa: E402
except ImportError as _e:
    _princeton = None
    if getattr(_e, "name", None) != "princeton_personal_sources":
        say(f"(The Princeton collection could not be loaded: {_e}. It is left out.)")
PRINCETON_SOURCES = list(getattr(_princeton, "PRINCETON_SOURCES", []) or [])
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in PRINCETON_SOURCES)
_add_collections(PRINCETON_SOURCES)

# US state digital library items with no rights statement, or whose rights words allow research or private study
# only: personal use only, downloaded on the owner's computer with the open packs' rules; the file may be missing.
# Never used for picture-making.
try:
    import state_collections_personal_sources as _state_collections  # noqa: E402
except ImportError as _e:
    _state_collections = None
    if getattr(_e, "name", None) != "state_collections_personal_sources":
        say(f"(The state digital library personal-use collection could not be loaded: {_e}. It is left out.)")
STATE_COLLECTIONS_SOURCES = list(getattr(_state_collections, "STATE_COLLECTIONS_SOURCES", []) or [])
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in STATE_COLLECTIONS_SOURCES)
_add_collections(STATE_COLLECTIONS_SOURCES)

# Things and materials collections that are not open (EPIC-KITCHENS, Charades, PACO, MINC); the file may be missing.
try:
    import things_sources as _things  # noqa: E402
except ImportError as _e:
    _things = None
    if getattr(_e, "name", None) != "things_sources":
        say(f"(The things and materials collections could not be loaded: {_e}. They are left out.)")
THINGS_SOURCES = list(getattr(_things, "THINGS_SOURCES", []) or [])
_things_ok = set(getattr(_things, "THINGS_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _things_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in THINGS_SOURCES if s.key not in _things_ok)
_add_collections(THINGS_SOURCES)

# Mechanical and automotive collections that are not open (share-alike symbols and parts, AutoVI, dashboard warning
# icons, car damage and parts sets); the file may be missing.
try:
    import mechanical_sources as _mechanical  # noqa: E402
except ImportError as _e:
    _mechanical = None
    if getattr(_e, "name", None) != "mechanical_sources":
        say(f"(The mechanical and automotive collections could not be loaded: {_e}. They are left out.)")
MECHANICAL_SOURCES = list(getattr(_mechanical, "MECHANICAL_SOURCES", []) or [])
_mechanical_ok = set(getattr(_mechanical, "MECHANICAL_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _mechanical_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in MECHANICAL_SOURCES if s.key not in _mechanical_ok)
_add_collections(MECHANICAL_SOURCES)

# People-in-daily-activity collections that are not open (share-alike Commons files, the COCO rows on non-commercial
# and share-alike photos, Stanford 40 Actions, SWiG and HAR); the file may be missing. None is used for
# picture-making (PEOPLE_ACTIVITY_PICTURE_MAKING_OK is empty).
try:
    import people_activity_sources as _people_activity  # noqa: E402
except ImportError as _e:
    _people_activity = None
    if getattr(_e, "name", None) != "people_activity_sources":
        say(f"(The people-in-daily-activity collections could not be loaded: {_e}. They are left out.)")
PEOPLE_ACTIVITY_SOURCES = list(getattr(_people_activity, "PEOPLE_ACTIVITY_SOURCES", []) or [])
_people_activity_ok = set(getattr(_people_activity, "PEOPLE_ACTIVITY_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _people_activity_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in PEOPLE_ACTIVITY_SOURCES if s.key not in _people_activity_ok)
_add_collections(PEOPLE_ACTIVITY_SOURCES)

# United States collections that are not open (Commons BY-SA, Open Facts products sold in the USA, iNaturalist BY-SA and
# BY-NC by state, CPSC recall photos, Freiburg Groceries); the file may be missing.
try:
    import us_sources as _us  # noqa: E402
except ImportError as _e:
    _us = None
    if getattr(_e, "name", None) != "us_sources":
        say(f"(The United States collections could not be loaded: {_e}. They are left out.)")
US_SOURCES = list(getattr(_us, "US_SOURCES", []) or [])
_us_ok = set(getattr(_us, "US_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _us_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in US_SOURCES if s.key not in _us_ok)
_add_collections(US_SOURCES)

# Packaged-goods collections that are not open (FDA recall photos: the recalling companies' own, personal use only);
# the file may be missing. None is used for picture-making (PACKAGED_GOODS_PICTURE_MAKING_OK is empty).
try:
    import packaged_goods_sources as _packaged_goods  # noqa: E402
except ImportError as _e:
    _packaged_goods = None
    if getattr(_e, "name", None) != "packaged_goods_sources":
        say(f"(The packaged-goods collections could not be loaded: {_e}. They are left out.)")
PACKAGED_GOODS_SOURCES = list(getattr(_packaged_goods, "PACKAGED_GOODS_SOURCES", []) or [])
_packaged_goods_ok = set(getattr(_packaged_goods, "PACKAGED_GOODS_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _packaged_goods_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(
    s.key for s in PACKAGED_GOODS_SOURCES if s.key not in _packaged_goods_ok)
_add_collections(PACKAGED_GOODS_SOURCES)

# Modern-America collections that are not open (Commons BY-SA files of the same categories; NLM's C3PI pill photos,
# research use only); the file may be missing.
try:
    import us_modern_sources as _us_modern  # noqa: E402
except ImportError as _e:
    _us_modern = None
    if getattr(_e, "name", None) != "us_modern_sources":
        say(f"(The modern-America collections could not be loaded: {_e}. They are left out.)")
US_MODERN_SOURCES = list(getattr(_us_modern, "US_MODERN_SOURCES", []) or [])
_us_modern_ok = set(getattr(_us_modern, "US_MODERN_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _us_modern_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in US_MODERN_SOURCES if s.key not in _us_modern_ok)
_add_collections(US_MODERN_SOURCES)

# Household device collections that are not open (Commons BY-SA device and model photos; CO3D stills, research use);
# the file may be missing.
try:
    import device_sources as _device  # noqa: E402
except ImportError as _e:
    _device = None
    if getattr(_e, "name", None) != "device_sources":
        say(f"(The household device collections could not be loaded: {_e}. They are left out.)")
DEVICE_SOURCES = list(getattr(_device, "DEVICE_SOURCES", []) or [])
_device_ok = set(getattr(_device, "DEVICE_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _device_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in DEVICE_SOURCES if s.key not in _device_ok)
_add_collections(DEVICE_SOURCES)

# Workplace, farm and building collections that are not open (Commons BY-SA and GFDL files); the file may be missing.
try:
    import work_farm_mech_sources as _wfm  # noqa: E402
except ImportError as _e:
    _wfm = None
    if getattr(_e, "name", None) != "work_farm_mech_sources":
        say(f"(The workplace, farm and building collections could not be loaded: {_e}. They are left out.)")
WORK_FARM_MECH_SOURCES = list(getattr(_wfm, "WORK_FARM_MECH_SOURCES", []) or [])
_wfm_ok = set(getattr(_wfm, "WORK_FARM_MECH_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _wfm_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in WORK_FARM_MECH_SOURCES if s.key not in _wfm_ok)
_add_collections(WORK_FARM_MECH_SOURCES)

# US state, county and city collections that are not open (share-alike Commons files); the file may be missing.
try:
    import state_sources as _state  # noqa: E402
except ImportError as _e:
    _state = None
    if getattr(_e, "name", None) != "state_sources":
        say(f"(The US state, county and city collections could not be loaded: {_e}. They are left out.)")
STATE_SOURCES = list(getattr(_state, "STATE_SOURCES", []) or [])
_state_ok = set(getattr(_state, "STATE_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _state_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in STATE_SOURCES if s.key not in _state_ok)
_add_collections(STATE_SOURCES)

# Medicine and medical supply collections that are not open (Commons BY-SA; Open Facts supplements sold in the US and
# Canada; DailyMed human and animal drug label pictures, research use); the file may be missing.
try:
    import med_vet_sources as _med_vet  # noqa: E402
except ImportError as _e:
    _med_vet = None
    if getattr(_e, "name", None) != "med_vet_sources":
        say(f"(The medicine and medical supply collections could not be loaded: {_e}. They are left out.)")
MED_VET_SOURCES = list(getattr(_med_vet, "MED_VET_SOURCES", []) or [])
_med_vet_ok = set(getattr(_med_vet, "MED_VET_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _med_vet_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in MED_VET_SOURCES if s.key not in _med_vet_ok)
_add_collections(MED_VET_SOURCES)

# Canadian collections that are not open (Commons BY-SA; Open Facts sold in Canada; iNaturalist BY-SA and BY-NC by
# province; Montréal archive photos (CC BY-NC-SA); blank CRA forms (non-commercial); Health Canada recall photos
# (research)); the file may be missing.
try:
    import canada_sources as _canada  # noqa: E402
except ImportError as _e:
    _canada = None
    if getattr(_e, "name", None) != "canada_sources":
        say(f"(The Canadian collections could not be loaded: {_e}. They are left out.)")
CANADA_SOURCES = list(getattr(_canada, "CANADA_SOURCES", []) or [])
_canada_ok = set(getattr(_canada, "CANADA_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _canada_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in CANADA_SOURCES if s.key not in _canada_ok)
_add_collections(CANADA_SOURCES)

# Sign-up collections: the owner's own free keys or request forms, downloaded only on his computer, for personal use
# (DVIDS, Kaggle Chess Positions, Flickr30k, Museums Victoria); without a key each says so and adds nothing. Its
# ready() tells the wizard which have what they need. The file may be missing.
try:
    import signup_sources as _signup  # noqa: E402
except ImportError as _e:
    _signup = None
    if getattr(_e, "name", None) != "signup_sources":
        say(f"(The sign-up collections could not be loaded: {_e}. They are left out.)")
SIGNUP_SOURCES = list(getattr(_signup, "SIGNUP_SOURCES", []) or [])
_signup_ok = set(getattr(_signup, "SIGNUP_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _signup_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in SIGNUP_SOURCES if s.key not in _signup_ok)
_add_collections(SIGNUP_SOURCES)


def signup_ready(source):
    """True when a collection has what it needs on this computer: a sign-up collection its keys or files
    (signup_sources.ready); every other collection True."""
    return _signup.ready(source) if _signup is not None else True

# College and university collections that are not open (DPLA CC BY-SA and CC BY-NC items); the file may be missing.
try:
    import university_sources as _university  # noqa: E402
except ImportError as _e:
    _university = None
    if getattr(_e, "name", None) != "university_sources":
        say(f"(The college and university collections could not be loaded: {_e}. They are left out.)")
UNIVERSITY_SOURCES = list(getattr(_university, "UNIVERSITY_SOURCES", []) or [])
_university_ok = set(getattr(_university, "UNIVERSITY_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _university_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in UNIVERSITY_SOURCES if s.key not in _university_ok)
_add_collections(UNIVERSITY_SOURCES)

# Research collections from big technology companies (ScreenQA on Rico screens, PixMo spoken captions and counting,
# FinTabNet tables); the file may be missing.
try:
    import bigtech_sources as _bigtech  # noqa: E402
except ImportError as _e:
    _bigtech = None
    if getattr(_e, "name", None) != "bigtech_sources":
        say(f"(The big-company collections could not be loaded: {_e}. They are left out.)")
BIGTECH_SOURCES = list(getattr(_bigtech, "BIGTECH_SOURCES", []) or [])
_bigtech_ok = set(getattr(_bigtech, "BIGTECH_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _bigtech_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in BIGTECH_SOURCES if s.key not in _bigtech_ok)
_add_collections(BIGTECH_SOURCES)

# US state agencies' own websites that are not open packs (Oregon TripCheck cameras, kept on this computer; Washington
# Ecology shoreline aerial photos, non-commercial); the file may be missing.
try:
    import state_web_sources as _state_web  # noqa: E402
except ImportError as _e:
    _state_web = None
    if getattr(_e, "name", None) != "state_web_sources":
        say(f"(The US state website collections could not be loaded: {_e}. They are left out.)")
STATE_WEB_SOURCES = list(getattr(_state_web, "STATE_WEB_SOURCES", []) or [])
_state_web_ok = set(getattr(_state_web, "STATE_WEB_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _state_web_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in STATE_WEB_SOURCES if s.key not in _state_web_ok)
_add_collections(STATE_WEB_SOURCES)

# Civil defence material that is not open (UK Home Office and "Protect and Survive" booklets and films, Australian
# and NZ handbooks: research; Canadian EMO pamphlets: non-commercial); the file may be missing.
try:
    import civil_defense_sources as _cd  # noqa: E402
except ImportError as _e:
    _cd = None
    if getattr(_e, "name", None) != "civil_defense_sources":
        say(f"(The civil defence collections could not be loaded: {_e}. They are left out.)")
CIVIL_DEFENSE_SOURCES = list(getattr(_cd, "CIVIL_DEFENSE_SOURCES", []) or [])
_cd_ok = set(getattr(_cd, "CIVIL_DEFENSE_PICTURE_MAKING_OK", ()) or ())
PERSONAL_PICTURE_MAKING_OK |= _cd_ok
NOT_FOR_PICTURE_MAKING = tuple(NOT_FOR_PICTURE_MAKING) + tuple(s.key for s in CIVIL_DEFENSE_SOURCES if s.key not in _cd_ok)
_add_collections(CIVIL_DEFENSE_SOURCES)
