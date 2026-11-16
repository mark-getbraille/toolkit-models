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

Sizes (--size): each source has a cap for "normal"; "quick" uses a tenth of it (a try of an hour or two) and
"full" three times as much (several nights on a fast card).

A finished source is not prepared again when the kit is started again (its rows are kept in data/<key>-<size>.jsonl;
a bigger size prepares it again, but pictures already downloaded are kept).

Main parts: Source, SOURCES, chosen(with_wikipedia), prepare_source(source, data_dir, work, cap), questions.
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
    group      "permissive" or "share-alike"
    cap        the most pictures to use at "normal" size
    test       how many of its pictures are kept back for the test
    prepare    a function (source, data_dir, work, cap) -> [rows], each with "split" ("train", "test" or "")
    download   roughly how much it downloads, for the screen ("7.6 GB")"""

    def __init__(self, key, name, licence, credit, group, cap, test, prepare, download):
        """Store the fields (see the class docstring)."""
        self.key, self.name, self.licence, self.credit, self.group = key, name, licence, credit, group
        self.cap, self.test, self.prepare, self.download = cap, test, prepare, download


# ----------------------------------------------------------------- shared helpers

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
        if not os.path.exists(path):
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
    if os.path.exists(path) or smaller(data or b"", path):
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
            if os.path.exists(path) or smaller(tar.extractfile(member).read(), path):
                rows.append({"picture": path, "question": DETAILED, "answer": clean(text), "split": split})
            count += 1
            if count % 1000 == 0:
                say(f"    {count} pictures done")
    os.remove(archive)                                     # the small copies are kept; 7.6 GB freed
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
                              f"https://www.artic.edu/iiif/2/{art['image_id']}/full/843,/0/default.jpg",
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
        if not obj.get("isPublicDomain") or not obj.get("primaryImageSmall") or not clean(obj.get("title")):
            return None
        parts = [clean(obj["title"])]
        if clean(obj.get("artistDisplayName")):
            parts.append("by " + clean(obj["artistDisplayName"]))
        answer = ", ".join(parts)
        if clean(obj.get("objectDate")):
            answer += ", " + clean(obj["objectDate"])
        answer += "." + (" " + clean(obj["medium"]) + "." if clean(obj.get("medium")) else "")
        return (f"{object_id}.jpg", obj["primaryImageSmall"], {"question": ARTWORK, "answer": answer, "split": ""})

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
                href = links[0]["href"].replace("~thumb.", "~medium.")
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
        try:
            os.remove(os.path.realpath(local))             # the pictures are kept; the 1 GB file is not
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
                if os.path.exists(path) or smaller(tar.extractfile(member).read(), path):
                    rows.append({"picture": path, "question": BRIEF, "answer": english[name], "split": ""})
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
                entries.append((image["id"], location["url"][:-len("/info.json")] + "/full/!896,896/0/default.jpg",
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


SOURCES = [
    Source("docci", "DOCCI: photos described in about 120 words",
           "CC BY 4.0, descriptions and photos (google.github.io/docci)",
           "DOCCI by Google, CC BY 4.0, https://google.github.io/docci/", "permissive", 9647, 25, prepare_docci,
           "7.6 GB"),
    Source("vizwiz_captions", "VizWiz Captions: photos taken by blind people, one sentence each",
           "CC BY 4.0 (vizwiz.org)",
           "VizWiz-Captions (Gurari et al., 2020), CC BY 4.0, https://vizwiz.org", "permissive", 3000, 10,
           prepare_vizwiz_captions, "3.5 GB"),
    Source("vizwiz_vqa", "VizWiz questions: what blind people asked about their own photos",
           "CC BY 4.0 (vizwiz.org)",
           "VizWiz VQA (Gurari et al., 2018), CC BY 4.0, https://vizwiz.org", "permissive", 3500, 10,
           prepare_vizwiz_vqa, "up to 4 GB"),
    Source("textcaps", "TextCaps: descriptions that read out the text in the picture",
           "CC BY 4.0 descriptions (textvqa.org); Open Images photos, CC BY 2.0",
           "TextCaps (Sidorov et al., 2020), CC BY 4.0, https://textvqa.org/textcaps; photos from Open Images",
           "permissive", 2500, 10, prepare_textcaps, "up to 2 GB"),
    Source("textvqa", "TextVQA: questions about the text in photos",
           "CC BY 4.0 (textvqa.org); Open Images photos, CC BY 2.0",
           "TextVQA (Singh et al., 2019), CC BY 4.0, https://textvqa.org; photos from Open Images", "permissive",
           1500, 10, prepare_textvqa, "up to 2 GB"),
    Source("localized_narratives", "Localized Narratives: photos described aloud by people",
           "CC BY 4.0 descriptions (google.github.io/localized-narratives); Open Images photos, CC BY 2.0",
           "Localized Narratives (Pont-Tuset et al., 2020), CC BY 4.0; photos from Open Images, CC BY 2.0",
           "permissive", 3000, 10, prepare_localized_narratives, "about 1 GB"),
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
           "no known copyright restrictions", "permissive", 3000, 10, prepare_coco, "about 1 GB"),
    Source("crossmodal", "Crossmodal-3600: photos from around the world, carefully described",
           "CC BY 4.0 descriptions; Open Images photos, CC BY 2.0 (google.github.io/crossmodal-3600)",
           "Crossmodal-3600 (Thapliyal et al., 2022), CC BY 4.0, https://google.github.io/crossmodal-3600/",
           "permissive", 2500, 10, prepare_crossmodal, "316 MB"),
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
    Source("concadia", "Concadia: Wikipedia pictures with their alt text",
           "CC BY-SA 4.0 (Wikipedia's text); pictures under their own Wikimedia Commons licences",
           "Concadia (Kreiss et al., 2022) from Wikipedia, CC BY-SA 4.0, https://github.com/elisakreiss/concadia",
           "share-alike", 5000, 10, prepare_concadia, "up to 2 GB"),
    Source("wikipedia", "Wikipedia: alt text written for screen-reader users",
           "CC BY-SA 4.0 (wikimedia/wit_base); pictures under their own Wikimedia Commons licences",
           "Wikipedia-based Image Text (WIT) by Wikimedia, CC BY-SA 4.0, https://huggingface.co/datasets/wikimedia/"
           "wit_base", "share-alike", 5000, 15, prepare_wikipedia, "about 11 GB, deleted as it goes"),
]


def chosen(with_wikipedia=False):
    """The sources to train on: the permissive ones, and the share-alike ones too with with_wikipedia."""
    return [s for s in SOURCES if s.group == "permissive" or with_wikipedia]


def prepare_source(source, data_dir, work, size="normal", seed=7):
    """Prepare one source once for a size: (train rows, test rows), also written to data/<key>-<size>.jsonl, which a
    restarted kit reads instead of preparing again (a bigger size prepares again, using the pictures already there). Its "test" rows (or, without them, a random few) are the test pictures; the
    rest, up to its cap for the size, are for training."""
    path = os.path.join(data_dir, f"{source.key}-{size}.jsonl")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
    else:
        cap = max(50, int(source.cap * SIZES[size]))
        rows = source.prepare(source, data_dir, work, cap)
        rows = [dict(r, source=source.key) for r in rows if r.get("picture") and clean(r.get("answer"))]
        with open(path + ".part", "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        os.replace(path + ".part", path)
    rng = random.Random(f"{seed}-{source.key}")
    marked = [r for r in rows if r.get("split") == "test"]
    others = [r for r in rows if r.get("split") != "test"]
    rng.shuffle(marked)
    rng.shuffle(others)
    if len(marked) >= source.test:
        test, rest = marked[:source.test], others
    else:
        test, rest = others[:source.test], others[source.test:]
    cap = max(50, int(source.cap * SIZES[size]))
    return rest[:cap], test
