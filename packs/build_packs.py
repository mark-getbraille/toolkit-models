"""Build the training-data packs of the Picture Model Training Kit on GitHub's machines (.github/workflows/packs.yml)
and publish them in this repository's release "training-data", so the kit downloads a few large files from here
instead of contacting many museum websites from the trainer's computer.

A pack is a zip: rows.jsonl (one row per picture: {"file" (a picture in the zip) or "url" (a picture the kit fetches
itself), "question", "answer", "credit"}), the pictures (JPEG, at most 896 pixels on the long side) and CREDITS.txt
(the licence, and each picture's credit where its licence asks for one), and considered-<pack>.jsonl (every
candidate picture the shared checks saw, used or not, with the reason it was dropped: see considered()). A zip over 1.9 GB is published in numbered
parts (<pack>.zip.001 ...), like the converted models; packs.json lists every pack's parts, size and SHA-256.

Only pictures whose licence allows sharing are put in a pack: CC0, public domain, no known copyright, or CC BY with
its credit. Pictures under other licences are never copied: the COCO pack holds only the questions, answers and the
addresses of COCO's photos (CC BY 2.0 photos whose photographers COCO does not name), which the kit fetches.

The packs (PACKS):
  smithsonian    Smithsonian museums (CC0 pictures): accessibility alt text and extended descriptions where they
                 are real descriptions (the African American History and Culture, Air and Space, Hirshhorn, Freer
                 and other museums), and the American Art Museum's gallery labels as "Tell me about this museum
                 object."
  coco_questions Questions about COCO photos with their answers: VQAv2 (CC BY 4.0, the answer most of ten people
                 gave) and A-OKVQA (Apache-2.0, the answer with the person's explanation), on photos under CC BY 2.0
                 or no known copyright only (fetched by the kit from cocodataset.org).
  commons        Wikimedia Commons: Featured pictures and Quality images whose file has an English caption
                 (captions are CC0) and whose picture is CC0, public domain or CC BY (credit kept).
  tepapa         Te Papa, the Museum of New Zealand: records with a description whose picture is CC BY 4.0 or no
                 known copyright (credit kept), the first sentences of the description.

    python packs/build_packs.py smithsonian --out build/packs --limit 6000
"""

import argparse
import concurrent.futures
import hashlib
import html
import io
import json
import os
import random
import re
import sys
import time
import zipfile

# Run as a program (python packs/build_packs.py ...), this file is the module "__main__". The other pack files say
# "from build_packs import ...": point that name at this same running file, so it is not loaded a second time (a second
# copy would import those files again before they are ready and stop with an ImportError).
if __name__ == "__main__":
    sys.modules.setdefault("build_packs", sys.modules["__main__"])

# Where in the world each picture is from (a row's optional "place" and "place_kind"): packs/places.py.
from places import where, country_at, place_from_text  # noqa: E402

LONG_SIDE = 2048       # packs keep large pictures: the kit makes its training copies and keeps these in the library
PART_BYTES = 1_900_000_000
USER_AGENT = "PictureModelTrainingKit/2 (https://github.com/mark-getbraille/toolkit-models)"
DETAILED, ALT_TEXT = "Describe this picture in detail.", "Write a short description of this picture for someone who " \
                                                            "cannot see it."
NARRATE, MUSEUM = "Describe this picture.", "Tell me about this museum object."
CANNOT_TELL = "I can't tell from this picture."


def say(text):
    """Print a line at once (the workflow's log)."""
    print(text, flush=True)


# Every candidate picture the shared checks saw while this pack was built, and why it was dropped: the Commons, COCO
# and Open Images licence checks and every picture download (fetch_all) add to it through considered(). write_pack
# writes it into the pack as considered-<key>.jsonl, so a manifest can list the pictures that were NOT used too.
CONSIDERED = []


def considered(name, url="", reason=""):
    """Note one candidate picture: its name (the file name it would have in the pack, or its title), its web address,
    and the reason it was dropped ("" when it passed this check). Any builder may call this; write_pack writes the
    list into the pack."""
    CONSIDERED.append({"name": str(name or ""), "url": str(url or ""), "reason": str(reason or "")})


def considered_lines(rows, names):
    """The lines of considered-<key>.jsonl: one per candidate (the notes about the same address or name taken
    together), each {"name", "url", "used", "reason"}. names: the pictures written into the pack; rows: its rows."""
    urls = {r["url"] for r in rows if r.get("url")}
    merged = {}
    for note in CONSIDERED:
        one = merged.setdefault(note["url"] or note["name"], {"names": [], "url": note["url"], "reason": ""})
        if note["name"] and note["name"] not in one["names"]:
            one["names"].append(note["name"])
        if note["reason"] and not one["reason"]:
            one["reason"] = note["reason"]
    lines = []
    for one in merged.values():
        used = one["url"] in urls or any(n in names for n in one["names"])
        name = next((n for n in one["names"] if n in names), one["names"][0] if one["names"] else "")
        reason = "" if used else one["reason"] or ("passed the checks but is not in the pack (over the pack's limit, "
                                                     "or left out by a later check)")
        lines.append(json.dumps({"name": name, "url": one["url"], "used": used, "reason": reason}) + "\n")
    return lines


def clean(text):
    """Text without HTML tags and entities, with its spaces tidied."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))
    return " ".join(text.split())


NOT_ABOUT_THE_PICTURE = re.compile(r"originally appeared in|^(see also|references?|bibliography|this essay)\b", re.I)


def first_sentences(text, words=80):
    """The first sentences of a text, at most about words words, leaving out sentences about where the text was
    published ("This essay originally appeared in ...")."""
    out = ""
    for sentence in re.split(r"(?<=[.!?])\s+", clean(text)):
        if NOT_ABOUT_THE_PICTURE.search(sentence):
            continue
        if out and len((out + " " + sentence).split()) > words:
            break
        out = (out + " " + sentence).strip()
    return out


# A pack build may run only so long on GitHub's machines (the workflow sets PACK_TIME_LIMIT_MINUTES). After that
# time every download through session() fails at once, so the builder finishes quickly with the pictures it already
# has, and the pack is still written and published, smaller, instead of being cancelled with nothing.
STARTED = time.time()
TIME_LIMIT = float(os.environ.get("PACK_TIME_LIMIT_MINUTES", "0") or 0) * 60


def out_of_time():
    """True once the build's time limit (if any) has passed."""
    return bool(TIME_LIMIT) and time.time() - STARTED > TIME_LIMIT


LISTING_SHARE = 0.5     # the share of the time limit a pack may spend finding its pictures before fetching them


def listing_out_of_time():
    """True once a pack has spent LISTING_SHARE of the time limit on finding its pictures: it then stops looking and
    fetches what it has found (the USGS and Library of Congress packs spent the whole limit looking, so their
    downloads were refused and they came out empty or were cancelled, 17 November)."""
    return bool(TIME_LIMIT) and time.time() - STARTED > TIME_LIMIT * LISTING_SHARE


def session():
    """A requests session with the kit's name (Wikimedia asks for one with a contact). Once the build is out of time,
    every request it makes fails straight away (see TIME_LIMIT)."""
    import requests

    class TimedSession(requests.Session):
        """A session that stops downloading when the build's time is up."""

        def request(self, *args, **kwargs):
            """Make the request, or fail at once when out of time."""
            if out_of_time():
                raise requests.exceptions.ConnectionError("the pack's time limit has passed")
            return super().request(*args, **kwargs)

    s = TimedSession()
    s.headers["User-Agent"] = USER_AGENT
    return s


def smaller(data):
    """JPEG bytes at most LONG_SIDE pixels on the long side, or None when the picture cannot be read or is tiny."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:  # noqa: BLE001 - left out
        return None
    if min(img.size) < 64:
        return None
    img.thumbnail((LONG_SIDE, LONG_SIDE))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=90)
    return out.getvalue()


def fetch_all(items, workers=8, pause=0.0):
    """Download pictures: items are (name, address, row); returns [(name, JPEG bytes, row)] for those that came."""
    s = session()

    def one(item):
        """One picture, or None."""
        name, url, row = item
        if pause:
            time.sleep(pause)
        for _ in range(2):
            try:
                r = s.get(url, timeout=60)
                if r.status_code == 200:
                    data = smaller(r.content)
                    considered(name, url, "" if data else "the picture could not be read, or is smaller than 64 "
                                                          "pixels")
                    return (name, data, row) if data else None
                if r.status_code in (403, 404, 410):
                    considered(name, url, f"could not be downloaded (the server answered {r.status_code})")
                    return None
            except Exception:  # noqa: BLE001 - tried once more, then left out
                time.sleep(2)
        considered(name, url, "could not be downloaded (no good answer after two tries)")
        return None

    out, done = [], 0
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for result in pool.map(one, items):
            done += 1
            if result:
                out.append(result)
            if done % 500 == 0:
                say(f"  {done} of {len(items)} pictures fetched ({len(out)} usable)")
    return out


# ----------------------------------------------------------------- Smithsonian

SI_BUCKET = "https://smithsonian-open-access.s3-us-west-2.amazonaws.com"
SI_UNITS = ("nmaahc", "nasm", "hmsg", "fsg", "nmah", "saam", "npg", "nmafa", "acm", "chsdm")
SI_NOT_A_DESCRIPTION = re.compile(r"^(artist:|sitter:|h x w|\d|wood,|bronze,|oil on|albumen|gelatin|cyanotype\.)", re.I)
# Catalogue lines, not descriptions: sizes, materials lists and "Sitter: ..., Current owner: ..." text.
SI_CATALOGUE = re.compile(r"H x W|Current owner|Sitter:|Attribution:|Diameter|\bcm\b|\d+\s*in\.|\(overall\)|"
                          r"^[\w\s,;]+ on (paper|canvas|panel)\b", re.I)


def is_description(text, words=8):
    """True for text that describes (at least words words, not a catalogue line of sizes, materials or owners)."""
    return len(text.split()) >= words and not SI_NOT_A_DESCRIPTION.match(text) and not SI_CATALOGUE.search(text)


def si_keys(unit):
    """The metadata files of one Smithsonian museum in the open-access bucket."""
    import xml.etree.ElementTree as ET
    s, keys, token = session(), [], None
    while True:
        params = {"list-type": "2", "prefix": f"metadata/edan/{unit}/"}
        if token:
            params["continuation-token"] = token
        root = ET.fromstring(s.get(SI_BUCKET + "/", params=params, timeout=60).content)
        ns = {"s": root.tag.split("}")[0].strip("{")}
        keys += [k.text for k in root.findall("s:Contents/s:Key", ns) if k.text.endswith(".txt")]
        token_el = root.find("s:NextContinuationToken", ns)
        if token_el is None:
            return keys
        token = token_el.text


# The record's place labels by kind: where the object was made, where a photo or film was taken, what it shows.
SI_PLACE_KINDS = (("origin", ("place made", "made in", "made at", "origin", "manufacturer", "place printed",
                              "place issued", "place of issue")),
                  ("photo", ("place captured", "place filmed")),
                  ("depicted", ("place depicted", "depicted", "depicts", "depicts sights in")))


def si_place(content):
    """{"place", "place_kind"} from a Smithsonian record's own place fields ("Place made: Japan"), or {}."""
    given = {}
    for p in content.get("freetext", {}).get("place") or []:
        given.setdefault(clean(p.get("label")).lower(), p.get("content"))
    for kind, labels in SI_PLACE_KINDS:
        for label in labels:
            place = place_from_text(given.get(label))
            if place:
                return where(place, kind)
    return {}


def si_row(record):
    """(picture address, row) for a record with a CC0 picture and a real description, or None."""
    content = record.get("content", {})
    media = (content.get("descriptiveNonRepeating", {}).get("online_media") or {}).get("media", [])
    picture = next((m for m in media if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"),
                   None)
    if not picture or not picture.get("content"):
        return None
    alt, ext = clean(picture.get("altTextAccessibility")), clean(picture.get("extDescrAccessibility"))
    url = picture["content"] + "&max=2048"
    credit = f"{record.get('unitCode', 'Smithsonian')}, Smithsonian Institution, CC0: {record.get('title', '')}"
    if is_description(alt, 6):
        return url, {"question": ALT_TEXT, "answer": alt, "credit": credit, **si_place(content)}
    ext = first_sentences(ext, 90)
    if is_description(ext, 12):
        return url, {"question": NARRATE, "answer": ext, "credit": credit, **si_place(content)}
    for note in content.get("freetext", {}).get("notes", []):
        if note.get("label") in ("Gallery Label", "Luce Center Label", "Exhibition Label", "Description"):
            text = first_sentences(note.get("content"), 90)
            if len(text.split()) >= 15:
                title = clean(record.get("title"))
                answer = text if not title or title.lower() in text.lower() else f"{title}. {text}"
                return url, {"question": MUSEUM, "answer": answer, "credit": credit, **si_place(content)}
    return None


def build_smithsonian(limit):
    """The Smithsonian pack's pictures: [(name, JPEG, row)]."""
    s, items = session(), []
    per_unit = limit // len(SI_UNITS) + 200
    for unit in SI_UNITS:
        found = 0
        keys = si_keys(unit)
        say(f"Smithsonian {unit}: {len(keys)} files")
        random.Random(unit).shuffle(keys)
        for key in keys:
            try:
                text = s.get(f"{SI_BUCKET}/{key}", timeout=120).content.decode("utf-8", "replace")
            except Exception:  # noqa: BLE001 - next file
                continue
            for line in text.splitlines():
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                got = si_row(record)
                if got:
                    url, row = got
                    items.append((f"si-{len(items)}.jpg", url, row))
                    found += 1
            if found >= per_unit * 1.3:
                break
        say(f"  {found} usable records")
    random.Random(1).shuffle(items)
    return fetch_all(items[:int(limit * 1.2)], workers=6, pause=0.1)[:limit]


# ----------------------------------------------------------------- COCO questions (rows only)

COCO_FREE = (4, 7)
COCO_LICENCES = {1: "CC BY-NC-SA 2.0", 2: "CC BY-NC 2.0", 3: "CC BY-NC-ND 2.0", 4: "CC BY 2.0", 5: "CC BY-SA 2.0",
                 6: "CC BY-ND 2.0", 7: "no known copyright", 8: "United States Government Work"}


def coco_licences():
    """{COCO image id: its photo address} for photos under CC BY 2.0 or no known copyright (phiyodr/coco2017). The
    other photos are noted as considered and dropped for their licence."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download
    free = {}
    for name in HfApi().list_repo_files("phiyodr/coco2017", repo_type="dataset"):
        if name.endswith(".parquet"):
            table = pq.read_table(hf_hub_download("phiyodr/coco2017", name, repo_type="dataset"),
                                  columns=["license", "image_id", "coco_url"]).to_pylist()
            for r in table:
                if r["license"] in COCO_FREE:
                    free[r["image_id"]] = r["coco_url"]
                else:
                    considered(f"coco-{r['image_id']}", r["coco_url"], f"its COCO licence is "
                               f"{COCO_LICENCES.get(r['license'], r['license'])}, not CC BY 2.0 or no known copyright")
    return free


def most_common(answers):
    """The answer most people gave ("I can't tell" when most said it cannot be answered), as a sentence."""
    counts = {}
    for a in answers:
        a = clean(a).lower()
        if a:
            counts[a] = counts.get(a, 0) + 1
    if not counts:
        return ""
    best = max(counts, key=counts.get)
    if best in ("unanswerable", "unsuitable"):
        return CANNOT_TELL
    return best[0].upper() + best[1:] + ("" if best.endswith((".", "?", "!")) else ".")


def build_coco_questions(limit):
    """The COCO questions pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]."""
    import tarfile
    s = session()
    free = coco_licences()
    say(f"COCO: {len(free)} photos under CC BY 2.0 or no known copyright")
    rows = []
    # A-OKVQA: the answer and one of the people's explanations (Apache-2.0).
    data = s.get("https://prior-datasets.s3.us-east-2.amazonaws.com/aokvqa/aokvqa_v1p0.tar.gz", timeout=300).content
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        for member in tar:
            if member.name.endswith(("aokvqa_v1p0_train.json", "aokvqa_v1p0_val.json")):
                for q in json.load(tar.extractfile(member)):
                    if q["image_id"] in free and q.get("rationales") and q.get("direct_answers"):
                        answer = most_common(q["direct_answers"])
                        why = clean(q["rationales"][0])
                        rows.append({"url": free[q["image_id"]], "question": clean(q["question"]),
                                     "answer": f"{answer} {why[:1].upper() + why[1:]}".strip(),
                                     "credit": "A-OKVQA (Schwenk et al., 2022), Apache-2.0; photo from COCO, CC BY 2.0"})
    say(f"A-OKVQA: {len(rows)} questions")
    # VQAv2: the answer most of ten people gave (CC BY 4.0).
    questions = {}
    base = "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/"
    with zipfile.ZipFile(io.BytesIO(s.get(base + "v2_Questions_Train_mscoco.zip", timeout=300).content)) as z:
        for q in json.load(z.open(z.namelist()[0]))["questions"]:
            if q["image_id"] in free:
                questions[q["question_id"]] = q
    with zipfile.ZipFile(io.BytesIO(s.get(base + "v2_Annotations_Train_mscoco.zip", timeout=300).content)) as z:
        annotations = json.load(z.open(z.namelist()[0]))["annotations"]
    vqa = []
    for a in annotations:
        q = questions.get(a["question_id"])
        if q:
            answer = most_common([x["answer"] for x in a["answers"]])
            if answer:
                vqa.append({"url": free[q["image_id"]], "question": clean(q["question"]), "answer": answer,
                            "credit": "VQAv2 (Goyal et al., 2017), CC BY 4.0; photo from COCO, CC BY 2.0"})
    say(f"VQAv2: {len(vqa)} questions")
    random.Random(3).shuffle(vqa)
    rows += vqa[:max(0, limit - len(rows))]
    random.Random(4).shuffle(rows)
    return [(None, None, r) for r in rows[:limit]]


# ----------------------------------------------------------------- Wikimedia Commons

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
COMMONS_CATEGORIES = ("Category:Featured pictures on Wikimedia Commons", "Category:Quality images")
COMMONS_FREE = re.compile(r"^(cc0|public domain|pd|cc by \d|cc-by-\d|cc by-\d)", re.I)


def build_commons(limit):
    """The Commons pack's pictures: captioned Featured and Quality pictures under CC0, public domain or CC BY."""
    s, items, seen = session(), [], set()
    for category in COMMONS_CATEGORIES:
        params = {"action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": category,
                  "gcmtype": "file", "gcmlimit": 50, "prop": "imageinfo|info", "iiprop": "url|extmetadata",
                  "iiurlwidth": LONG_SIDE, "iiextmetadatafilter": "LicenseShortName|Artist|GPSLatitude|GPSLongitude", "maxlag": 5}
        while len(items) < limit * 1.3 and not out_of_time():
            try:
                data = s.get(COMMONS_API, params=params, timeout=60).json()
            except Exception:  # noqa: BLE001 - wait and try again once
                time.sleep(10)
                continue
            pages = list((data.get("query") or {}).get("pages", {}).values())
            ids = [f"M{p['pageid']}" for p in pages if p.get("pageid")]
            labels = {}
            if ids:
                entities = {}
                for attempt in range(4):        # Commons sometimes answers "slow down" with a web page, not data
                    try:
                        entities = s.get(COMMONS_API, timeout=60, params={
                            "action": "wbgetentities", "format": "json", "ids": "|".join(ids), "props": "labels",
                            "languages": "en", "maxlag": 5}).json().get("entities", {})
                        break
                    except Exception:  # noqa: BLE001 - wait longer each time; without labels the files still count
                        time.sleep(15 * (attempt + 1))
                labels = {k: ((v.get("labels") or {}).get("en") or {}).get("value", "") for k, v in entities.items()}
            for p in pages:
                info = (p.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata") or {}
                licence = clean((meta.get("LicenseShortName") or {}).get("value"))
                caption = clean(labels.get(f"M{p.get('pageid')}"))
                if p["pageid"] in seen:
                    continue
                why = ("no English caption of five words or more" if not caption or len(caption.split()) < 5 else
                       f"its licence ({licence or 'none given'}) is not CC0, public domain or CC BY"
                       if "SA" in licence.upper() or "NC" in licence.upper() or not COMMONS_FREE.match(licence) else
                       "no picture address" if not info.get("thumburl") else "")
                if why:
                    considered(p.get("title"), info.get("thumburl") or info.get("descriptionurl"), why)
                    continue
                seen.add(p["pageid"])
                artist = clean((meta.get("Artist") or {}).get("value"))
                credit = f"{p['title']} by {artist or 'unknown'}, {licence}, https://commons.wikimedia.org/wiki/" + \
                    p["title"].replace(" ", "_")
                answer = caption[:1].upper() + caption[1:] + ("" if caption.endswith((".", "!", "?")) else ".")
                place = country_at(clean((meta.get("GPSLatitude") or {}).get("value")),   # the camera's place
                                   clean((meta.get("GPSLongitude") or {}).get("value")))
                items.append((f"commons-{p['pageid']}.jpg", info["thumburl"],
                              {"question": ALT_TEXT, "answer": answer, "credit": credit, **where(place)}))
            if "continue" not in data:
                break
            params.update(data["continue"])
            time.sleep(1)
        say(f"Commons {category}: {len(items)} captioned free pictures so far")
    return fetch_all(items[:int(limit * 1.2)], workers=4, pause=0.2)[:limit]


# ----------------------------------------------------------------- Te Papa

TEPAPA_TERMS = ("dress", "chair", "bird", "photograph", "painting", "jug", "brooch", "hat", "fish", "shell", "basket",
                "cloak", "boat", "toy", "clock", "quilt", "vase", "map", "poster", "flower", "insect", "shoe", "lamp",
                "tool", "coin", "bottle", "doll", "mask", "fern", "plant", "landscape", "portrait", "building",
                "teapot", "cup", "box", "medal", "badge", "textile", "carving")
TEPAPA_FREE = ("Attribution 4.0", "CC BY 4.0", "No Known Copyright", "Public Domain", "CC0")


def tepapa_place(record):
    """{"place": ..., "place_kind": "origin"} from where a Te Papa object was made (its production place), or {}."""
    for production in record.get("production") or []:
        spatial = production.get("spatial") or {}
        nation = (spatial.get("nation") or [""])[0]
        place = place_from_text(f"{spatial.get('prefLabel')} ({nation})" if nation and spatial.get("prefLabel")
                                else spatial.get("title"))
        if place:
            return where(place, "origin")
    return {}


def build_tepapa(limit):
    """The Te Papa pack's pictures: records with a description whose picture is CC BY 4.0 or no known copyright."""
    s, items, seen = session(), [], set()
    token = s.get("https://data.tepapa.govt.nz/collection/search?q=x", timeout=60).json()["guestToken"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    for term in TEPAPA_TERMS:
        for start in range(0, 1000, 100):
            try:
                data = s.get("https://data.tepapa.govt.nz/collection/search", headers=headers, timeout=60,
                             params={"q": term, "from": start, "limit": 100}).json()
            except Exception:  # noqa: BLE001 - next term
                break
            results = data.get("results") or []
            for r in results:
                rep = (r.get("hasRepresentation") or [{}])[0]
                rights = clean((rep.get("rights") or {}).get("title"))
                text = first_sentences(r.get("description") or r.get("physicalDescription"), 80)
                if r.get("id") in seen or "NC" in rights or not any(f in rights for f in TEPAPA_FREE) \
                        or len(text.split()) < 10 or not rep.get("contentUrl"):
                    continue
                seen.add(r["id"])
                title = clean(r.get("title"))
                answer = text if not title or title.lower() in text.lower() else f"{title}. {text}"
                items.append((f"tepapa-{r['id']}.jpg", rep["contentUrl"].replace("/full", "/preview") if
                              rep["contentUrl"].endswith("/full") else rep["contentUrl"],
                              {"question": MUSEUM, "answer": answer,
                               "credit": f"Te Papa (record {r['id']}), {rights}", **tepapa_place(r)}))
            if len(results) < 100:
                break
            time.sleep(0.3)
        say(f"Te Papa '{term}': {len(items)} usable so far")
        if len(items) >= limit * 1.3:
            break
    return fetch_all(items[:int(limit * 1.2)], workers=4, pause=0.1)[:limit]


# ----------------------------------------------------------------- nature, food and everyday life

INAT_GROUPS = [("Plantae", "What plant is this?"), ("Fungi", "What mushroom or fungus is this?"),
               ("Insecta", "What insect is this?"), ("Aves", "What bird is this?"), ("Mammalia", "What animal is this?"),
               ("Reptilia", "What animal is this?"), ("Amphibia", "What animal is this?"),
               ("Arachnida", "What is this creature?"), ("Mollusca", "What is this creature?"),
               ("Actinopterygii", "What fish is this?")]


def article(word):
    """ "a" or "an" before a word."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def inat_place(observation):
    """{"place": country} from an observation's coordinates, or {} when they are hidden or blurred on purpose."""
    if observation.get("obscured") or observation.get("geoprivacy") in ("obscured", "private") \
            or observation.get("taxon_geoprivacy") in ("obscured", "private"):
        return {}
    point = str(observation.get("location") or "").split(",")
    return where(country_at(*point)) if len(point) == 2 else {}


def build_inaturalist(limit):
    """iNaturalist research-grade observations whose photo is CC0 or CC BY (credit kept): plants, fungi, insects,
    birds and other animals, named by the community ("This is a Shaggy Mane (Coprinus comatus)")."""
    s, items, seen = session(), [], set()
    per_group = limit // len(INAT_GROUPS) + 20
    for group, question in INAT_GROUPS:
        found = 0
        for page in range(1, 40):
            try:
                data = s.get("https://api.inaturalist.org/v1/observations", timeout=60, params={
                    "quality_grade": "research", "photo_license": "cc0,cc-by", "iconic_taxa": group,
                    "per_page": 200, "page": page, "order_by": "votes"}).json()
            except Exception:  # noqa: BLE001 - next group
                break
            results = data.get("results") or []
            for o in results:
                taxon, photos = o.get("taxon") or {}, o.get("photos") or []
                photo = next((ph for ph in photos if (ph.get("license_code") or "") in ("cc0", "cc-by")), None)
                if not photo or not taxon.get("name") or taxon["id"] in seen and found > per_group // 2:
                    continue
                seen.add(taxon["id"])
                latin, common = taxon["name"], clean(taxon.get("preferred_common_name"))
                answer = (f"This is {article(common)} {common} ({latin})." if common else f"This is {latin}.")
                login = (o.get("user") or {}).get("login", "an iNaturalist user")
                items.append((f"inat-{photo['id']}.jpg", photo["url"].replace("/square.", "/large."),
                              {"question": question, "answer": answer, **inat_place(o),
                               "credit": f"Photo by {login} on iNaturalist, {photo['license_code'].upper()}, "
                                         f"https://www.inaturalist.org/observations/{o['id']}"}))
                found += 1
            if found >= per_group or len(results) < 200:
                break
            time.sleep(1.1)                    # iNaturalist asks for at most about one request a second
        say(f"iNaturalist {group}: {found}")
    random.Random(7).shuffle(items)
    return fetch_all(items[:int(limit * 1.1)], workers=4, pause=0.3)[:limit]


N5K = "https://storage.googleapis.com/nutrition5k_dataset/nutrition5k_dataset/"


def build_nutrition5k(limit):
    """Nutrition5k (Google, CC BY 4.0): real cafeteria plates photographed from above, every ingredient weighed:
    "What food is on this plate, and roughly how much?" """
    s, items = session(), []
    for cafe in ("cafe1", "cafe2"):
        for line in s.get(f"{N5K}metadata/dish_metadata_{cafe}.csv", timeout=120).text.splitlines():
            cells = line.split(",")
            if len(cells) < 13:
                continue
            dish, calories, grams = cells[0], float(cells[1]), float(cells[2])
            parts = []
            for at in range(6, len(cells) - 6, 7):
                try:
                    parts.append((float(cells[at + 2]), cells[at + 1].strip()))
                except ValueError:
                    continue
            parts = [(g, n) for g, n in sorted(parts, reverse=True) if g >= 3 and n]
            if not parts or calories <= 0:
                continue
            named = [f"{n} (about {g:.0f} g)" for g, n in parts[:7]]
            listed = named[0] if len(named) == 1 else ", ".join(named[:-1]) + " and " + named[-1]
            answer = (f"The plate has {listed}{' and a little more' if len(parts) > 7 else ''}. In all about "
                      f"{grams:.0f} g of food and {calories:.0f} calories.")
            items.append((f"{dish}.jpg", f"{N5K}imagery/realsense_overhead/{dish}/rgb.png",
                          {"question": "What food is on this plate, and roughly how much?", "answer": answer,
                           "credit": "Nutrition5k (Thames et al., 2021), Google, CC BY 4.0"}))
    random.Random(8).shuffle(items)
    return fetch_all(items[:int(limit * 1.3)], workers=8)[:limit]


def build_fresh_rotten(limit):
    """Fresh or rotten fruit (Sultana et al., CC BY 4.0; the Project-AgML copy, its original photos): "Is this
    apple still good to eat?" """
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download
    out = []
    repo = "Project-AgML/fresh_rotten_fruit_classification"
    for name in sorted(f for f in HfApi().list_repo_files(repo, repo_type="dataset") if f.startswith("raw/")):
        for row in pq.read_table(hf_hub_download(repo, name, repo_type="dataset")).to_pylist():
            fruit = clean(row.get("fruit_type")).lower() or "fruit"
            data = smaller((row.get("image") or {}).get("bytes") or b"")
            if not data:
                continue
            answer = (f"No: this {fruit} is rotten and should not be eaten." if row["label"] == 1 else
                      f"Yes: this {fruit} looks fresh.")
            out.append((f"fruit-{len(out)}.jpg", data, {"question": f"Is this {fruit} still good to eat?",
                        "answer": answer, "credit": "Fresh and rotten fruits (Sultana et al.), CC BY 4.0"}))
    random.Random(9).shuffle(out)
    return out[:limit]


def mendeley_zip(dataset, version=1):
    """The first zip file of a Mendeley Data dataset, downloaded (its download address)."""
    s = session()
    files = s.get(f"https://data.mendeley.com/public-api/datasets/{dataset}/files?folder_id=root&version={version}",
                  timeout=60).json()
    zipped = next(f for f in files if f["filename"].lower().endswith(".zip"))
    return zipfile.ZipFile(io.BytesIO(s.get(zipped["content_details"]["download_url"], timeout=1800).content))


BANKNOTES = {"INDIA": ("Indian", "rupee", "India"), "THAI": ("Thai", "baht", "Thailand")}   # the last: its country


def build_banknotes(limit):
    """Indian and Thai banknotes photographed for visually impaired users (Mendeley 2kfz5yc7pt, CC BY 4.0):
    "Which banknote is this?" """
    z, out = mendeley_zip("2kfz5yc7pt"), []
    for name in z.namelist():
        folder = name.split("/")[-2] if "/" in name else ""
        m = re.match(r"(INDIA|THAI)(\d+)(NEW|OLD)?$", folder)
        if not m or not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        country, unit, issued = BANKNOTES[m.group(1)]
        design = {"NEW": " (the new design)", "OLD": " (the old design)"}.get(m.group(3) or "", "")
        data = smaller(z.read(name))
        if data:
            out.append((f"note-{len(out)}.jpg", data, {"question": "Which banknote is this?",
                        "answer": f"This is {article(country)} {country} {int(m.group(2)):,} {unit} note{design}.",
                        "credit": "Indian and Thai banknotes dataset (Mendeley Data 2kfz5yc7pt), CC BY 4.0",
                        **where(issued, "origin")}))
    random.Random(10).shuffle(out)
    return out[:limit]


CATTLE = {"FMD": "Yes: it shows signs of foot-and-mouth disease.", "LSD": "Yes: it shows signs of lumpy skin disease.",
          "HEALTHY FMD": "No: it shows no signs of foot-and-mouth disease.",
          "HEALTHY LSD": "No: it shows no signs of lumpy skin disease."}


def build_cattle_health(limit):
    """Beef cattle photographed on farms in Bangladesh, healthy or with foot-and-mouth disease or lumpy skin
    disease (Mendeley ggpwpscjvm, CC BY 4.0): "Does this cow show signs of disease?" """
    z, out = mendeley_zip("ggpwpscjvm"), []
    for name in z.namelist():
        folder = name.split("/")[-2] if "/" in name else ""
        if folder in CATTLE and name.lower().endswith((".jpg", ".jpeg", ".png")):
            data = smaller(z.read(name))
            if data:
                out.append((f"cattle-{len(out)}.jpg", data, {"question": "Does this cow show signs of disease?",
                            "answer": CATTLE[folder], "credit": "FMD-LSD cattle dataset (Mendeley Data ggpwpscjvm), "
                                                              "CC BY 4.0",
                            "place": "Cumilla, Bangladesh"}))         # farms in Cumilla (the dataset's record)
    random.Random(11).shuffle(out)
    return out[:limit]


CLOTHING = {"T-Shirt": "a T-shirt", "Longsleeve": "a long-sleeved top", "Pants": "a pair of trousers",
            "Shoes": "a pair of shoes", "Shirt": "a shirt", "Dress": "a dress", "Outwear": "a coat or jacket",
            "Shorts": "a pair of shorts", "Hat": "a hat", "Skirt": "a skirt", "Polo": "a polo shirt",
            "Undershirt": "an undershirt", "Blazer": "a blazer", "Hoodie": "a hoodie", "Body": "a baby bodysuit",
            "Top": "a top", "Blouse": "a blouse"}
CLOTHING_RAW = "https://raw.githubusercontent.com/alexeygrigorev/clothing-dataset/master/"


def build_clothing(limit):
    """Photos of clothing sent in by people (Grigorev clothing dataset, CC0): "What item of clothing is this?" """
    s, items = session(), []
    for line in s.get(CLOTHING_RAW + "images.csv", timeout=60).text.splitlines()[1:]:
        cells = line.split(",")
        if len(cells) >= 3 and cells[2] in CLOTHING:
            items.append((f"{cells[0]}.jpg", f"{CLOTHING_RAW}images/{cells[0]}.jpg",
                          {"question": "What item of clothing is this?", "answer": CLOTHING[cells[2]][0].upper()
                           + CLOTHING[cells[2]][1:] + ".", "credit": "Clothing dataset (Alexey Grigorev), CC0"}))
    random.Random(12).shuffle(items)
    return fetch_all(items[:int(limit * 1.1)], workers=6)[:limit]


# ----------------------------------------------------------------- eggs and beef

EGG_KINDS = {"Chicken_White_Layer": "a white chicken egg", "Chicken_Red_Layer": "a brown chicken egg",
             "Chicken_Country": "a country chicken egg", "Duck_Pati": "a duck egg", "Bird_Koel": "a koel's egg"}
EGG_STATES = {"Fresh": "It looks fresh.", "Half-Fresh": "It is no longer fully fresh: use it soon and check it "
                                                         "before eating.",
              "Rotten": "It looks rotten: do not eat it."}


def build_eggs(limit):
    """Egg freshness (Mendeley Data 49msr3ksxj, CC BY 4.0): only its "Raw Dataset" of real photos (not the altered
    copies), fresh, half-fresh or rotten, of five kinds of egg: "Is this egg fresh?" """
    z, out = mendeley_zip("49msr3ksxj", version=2), []
    for name in z.namelist():
        m = re.search(r"Raw Dataset/Egg Freshness Recognition/[^/]+/(Fresh|Half-Fresh|Rotten)__([A-Za-z_]+)/[^/]+$", name)
        if not m or m.group(2) not in EGG_KINDS or not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        data = smaller(z.read(name))
        if data:
            kind = EGG_KINDS[m.group(2)]
            out.append((f"egg-{len(out)}.jpg", data, {"question": "Is this egg fresh?",
                        "answer": f"This is {kind}. {EGG_STATES[m.group(1)]}",
                        "credit": "Egg variety and freshness dataset (Mendeley Data 49msr3ksxj), CC BY 4.0",
                        "place": "Dhaka, Bangladesh"}))           # bought at markets in Dhaka (the dataset's record)
    random.Random(13).shuffle(out)
    return out[:limit]


BEEF_CUTS = {"A": "inside skirt", "B": "knuckle", "S": "sirloin"}


def build_beef(limit):
    """Fresh and non-fresh beef (Mendeley Data wvhkpppddp, CC BY 4.0): 30 pieces of three cuts photographed the day
    they were bought and five days later (the original photos only, not the processed ones): "Is this meat still
    fresh?" """
    s = session()
    files = s.get("https://data.mendeley.com/public-api/datasets/wvhkpppddp/files?folder_id=root&version=1",
                  timeout=60).json()
    firsts = {}
    for f in files:
        m = re.match(r"(\d{8})_([ABS])\d+_\d+\.jpg$", f["filename"])
        if m:
            firsts.setdefault(m.group(2), set()).add(m.group(1))
    out = []
    for f in files:
        m = re.match(r"(\d{8})_([ABS])\d+_\d+\.jpg$", f["filename"])
        if not m:
            continue                                            # the processed "_seg" pictures are left out
        fresh = m.group(1) == min(firsts[m.group(2)])
        data = smaller(s.get(f["content_details"]["download_url"], timeout=120).content)
        if data:
            cut = BEEF_CUTS[m.group(2)]
            answer = (f"This is raw beef ({cut}). It looks fresh." if fresh else
                      f"This is raw beef ({cut}). It is no longer fresh (five days after it was bought): do not eat it.")
            out.append((f"beef-{len(out)}.jpg", data, {"question": "Is this meat still fresh?", "answer": answer,
                        "credit": "Fresh and non-fresh beef images (Mendeley Data wvhkpppddp), CC BY 4.0"}))
    return out[:limit]


# ----------------------------------------------------------------- English translations of other languages

# Packs whose descriptions are in another language also get an English version of each, translated on the processor
# by open OPUS-MT models (University of Helsinki), marked "translated": the kit never uses those for its test, so a
# translation mistake cannot make the model look better or worse. The models were chosen language by language
# (November 2026) by translating 20 real descriptions from each pack with each candidate and checking every output
# against the source by hand:
#   sv  opus-mt-tc-big-gmq-en (CC BY 4.0): clearly better than opus-mt-sv-en ("pencil sketch", "sideburns",
#       "checked dress", where opus-mt-sv-en left words untranslated or wrong); about 1 second a description.
#   nl  opus-mt-tc-bible-big-gmw-en (Apache 2.0): better than opus-mt-nl-en ("kneeling woman", "wagon", "stream
#       goddesses", where opus-mt-nl-en said "car" and "electricity goddesses"); about 1.2 seconds a description.
#   zh  opus-mt-zh-en (CC BY 4.0), as before: the tc-bible zhx-en model often left half the sentence out.
#   fi  opus-mt-tc-big-fi-en (CC BY 4.0) and cs opus-mt-tc-big-ces_slk-en (CC BY 4.0): about 17 of 20 right.
# Rejected: MADLAD-400 3B (Apache 2.0; its 8-bit CTranslate2 copy repeated and dropped words on short captions and
# took 1-3 seconds a description; the full model is 12 GB), M2M100 418M and 1.2B (MIT; slower and no better: "white
# eagle" for a duck, "frog" for a heron), and NLLB (CC BY-NC, not allowed). None of these licences limits the use of
# the translations.
# Japanese is still left out: every model tried got about 3 in 10 short STAIR captions wrong (OPUS-MT ja-en: a cat
# became "a fox"; M2M100 1.2B: a duck became "a white eagle", a man on a toilet "standing on top of his shoes"), and
# the long Japan Search descriptions came out garbled. A wrong translation teaches the model to describe what is not
# there, so Japanese descriptions are used in Japanese only.
TRANSLATE = {"ksamsok": "sv", "rijksmuseum": "nl", "coco_cn": "zh", "europeana_fi": "fi", "europeana_cs": "cs"}
MT_MODELS = {"sv": ("Helsinki-NLP/opus-mt-tc-big-gmq-en", "b243b46fc9e1eaf068ae0d8ae896ac1acd7d2380"),
             "nl": ("Helsinki-NLP/opus-mt-tc-bible-big-gmw-en", "5af4b912a33023bc682ee6f27456dab65dbeaa73"),
             "zh": ("Helsinki-NLP/opus-mt-zh-en", "cf109095479db38d6df799875e34039d4938aaa6"),
             "fi": ("Helsinki-NLP/opus-mt-tc-big-fi-en", "956e13710061738d21f677e4ed16a56546511c0f"),
             "cs": ("Helsinki-NLP/opus-mt-tc-big-ces_slk-en", "2c4f1841a6cf8a4a79cf8b523c7e8169b5711342")}
# At most this long is spent translating one pack (GitHub's machines have 4 processors; a build may run 350 minutes,
# and the pictures need time too). Descriptions not reached in time keep their own language only.
MT_SECONDS = 2.5 * 3600
CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯]")


def translation_ok(source, text, language):
    """True when a machine translation looks sound: not empty, not much shorter or longer than the source, no word
    or group of words repeated over and over, no language tag left in it and, from Japanese or Chinese, no Japanese
    or Chinese characters left untranslated. A failed one is dropped (the row in its own language stays)."""
    words = text.lower().split()
    if len(words) < 3 or ">>" in text:
        return False
    ratio = len(text) / max(1, len(source))
    if language in ("ja", "zh"):
        if CJK.search(text) or not 0.8 <= ratio <= 8:
            return False
    elif not 0.5 <= ratio <= 2.0:
        return False
    runs = [w.strip(".,;:!?\"'()") for w in words]
    if any(runs[i] and runs[i] == runs[i + 1] == runs[i + 2] for i in range(len(runs) - 2)):
        return False                                                       # "the the the"
    threes = [tuple(runs[i:i + 3]) for i in range(len(runs) - 2)]
    if len(threes) - len(set(threes)) >= 2:
        return False                                                       # a phrase said again and again
    common = max(runs.count(w) for w in set(runs) if len(w) > 3) if any(len(w) > 3 for w in runs) else 0
    return not (len(runs) >= 8 and common > len(runs) * 0.25)


def translate(texts, language, seconds=MT_SECONDS):
    """English translations of texts (OPUS-MT, on the processor, in batches of similar length so little time goes
    on padding). Texts not reached within seconds come back as "" (left untranslated)."""
    from huggingface_hub import snapshot_download
    from transformers import MarianMTModel, MarianTokenizer
    import torch
    repo, revision = MT_MODELS[language]
    folder = snapshot_download(repo, revision=revision, allow_patterns=[
        "*.json", "*.spm", "*.txt", "*.bin", "*.safetensors", "*vocab*", "*source*", "*target*"])
    tokenizer = MarianTokenizer.from_pretrained(folder)
    model = MarianMTModel.from_pretrained(folder).eval()
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    out, started, done = [""] * len(texts), time.time(), 0
    with torch.inference_mode():
        for start in range(0, len(order), 16):
            if time.time() - started > seconds:
                say(f"  time is up: {done} of {len(texts)} translated, the rest left in their own language")
                break
            group = order[start:start + 16]
            batch = tokenizer([texts[i] for i in group], return_tensors="pt", padding=True, truncation=True,
                              max_length=256)
            made = model.generate(**batch, max_new_tokens=256, num_beams=2)
            for i, text in zip(group, tokenizer.batch_decode(made, skip_special_tokens=True)):
                out[i] = clean(text)
            done += len(group)
            if start % 800 == 0:
                say(f"  translated {done} of {len(texts)} ({time.time() - started:.0f} seconds)")
    return out


def add_translations(key, entries):
    """For a pack in another language: an English row ("Describe this picture." and the translation) for every
    row in that language, pointing at the same picture (or address), marked translated, keeping the row's "child"
    and place marks. Rows already in English, and rows marked "twinned" (their collection wrote its own English),
    are not translated; a translation that fails translation_ok is dropped."""
    language = TRANSLATE.get(key)
    if not language:
        return entries
    skip = {i for i, (_, _, row) in enumerate(entries) if row.get("twinned")}
    entries = [(n, d, {k: v for k, v in r.items() if k != "twinned"}) if r.get("twinned") else (n, d, r)
               for n, d, r in entries]
    wanted = [i for i, (_, _, row) in enumerate(entries) if i not in skip
              and row.get("question") != "Describe this picture." and not row.get("translated")]
    english = translate([entries[i][2]["answer"] for i in wanted], language)
    more, dropped = [], 0
    for i, text in zip(wanted, english):
        name, data, row = entries[i]
        if not text:
            continue
        if not translation_ok(row["answer"], text, language):
            dropped += 1
            continue
        twin = {"question": "Describe this picture.", "answer": text, "translated": True,
                "credit": row.get("credit", "") + f"; English translation by {MT_MODELS[language][0]} "
                                                  "(machine translation)"}
        twin.update({k: row[k] for k in ("child", "place", "place_kind") if k in row})
        if data is not None:
            twin["file"] = f"pictures/{name}"
        elif row.get("url"):
            twin["url"] = row["url"]
        elif row.get("file"):
            twin["file"] = row["file"]
        else:
            continue
        more.append((None, None, twin))
    say(f"{len(more)} English translations added ({dropped} failed the check and were left out)")
    return entries + more


# ----------------------------------------------------------------- packing

PACKS = {
    "smithsonian": (build_smithsonian, "Smithsonian Institution Open Access, CC0. https://www.si.edu/openaccess"),
    "coco_questions": (build_coco_questions, "Questions: VQAv2, CC BY 4.0 (https://visualqa.org) and A-OKVQA, "
                                             "Apache-2.0 (https://allenai.org/project/a-okvqa). Photos are not in "
                                             "this pack: the kit fetches them from https://cocodataset.org (only "
                                             "photos under CC BY 2.0 or no known copyright)."),
    "commons": (build_commons, "Wikimedia Commons: captions CC0; pictures CC0, public domain or CC BY, each with "
                               "its author below. https://commons.wikimedia.org"),
    "inaturalist": (build_inaturalist, "iNaturalist: research-grade observations; photos CC0 or CC BY, each with its "
                                       "photographer below. https://www.inaturalist.org"),
    "nutrition5k": (build_nutrition5k, "Nutrition5k (Thames et al., 2021), Google, CC BY 4.0. "
                                       "https://github.com/google-research-datasets/Nutrition5k"),
    "fresh_rotten": (build_fresh_rotten, "Fresh and rotten fruits (Sultana et al.), CC BY 4.0, via "
                                         "https://huggingface.co/datasets/Project-AgML/fresh_rotten_fruit_classification"),
    "banknotes": (build_banknotes, "Dataset of Indian and Thai banknotes, Mendeley Data 2kfz5yc7pt, CC BY 4.0."),
    "cattle_health": (build_cattle_health, "FMD-LSD differential diagnosis dataset in beef cattle, Mendeley Data "
                                           "ggpwpscjvm, CC BY 4.0."),
    "clothing": (build_clothing, "Clothing dataset by Alexey Grigorev, CC0. "
                                 "https://github.com/alexeygrigorev/clothing-dataset"),
    "eggs": (build_eggs, "Egg variety and freshness dataset, Mendeley Data 49msr3ksxj, CC BY 4.0 (its real photos only)."),
    "beef": (build_beef, "Fresh and non-fresh beef meat images, Mendeley Data wvhkpppddp, CC BY 4.0."),
    "tepapa": (build_tepapa, "Museum of New Zealand Te Papa Tongarewa: record text CC BY 4.0; pictures CC BY 4.0 or "
                             "no known copyright restrictions, each credited below. https://collections.tepapa.govt.nz"),
}


# The worldwide collections (Japan, Sweden, the Netherlands, Japanese and Chinese captions), in their own file.
try:
    from world_packs import WORLD_PACKS
except ImportError:                    # run from another folder: add this one to the path first
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from world_packs import WORLD_PACKS
PACKS.update(WORLD_PACKS)

# Medicines: single pills (Taiwan FDA), blister packs (Pharmassist) and mixed pills (MEDISEG), in their own file.
from pill_packs import PILL_PACKS
PACKS.update(PILL_PACKS)

# Food: everyday food photos (Open Images), shop shelves (Grocery Store), fish freshness by the eye, Commons food.
from food_packs import FOOD_PACKS
PACKS.update(FOOD_PACKS)

# Household objects (Open Images, ORBIT, CORe50) and animals (LILA camera traps, GBIF species, Commons breeds).
from everyday_packs import EVERYDAY_PACKS
PACKS.update(EVERYDAY_PACKS)

# Reading: text in photos, receipts, document pages, charts and handwritten letters.
from text_packs import TEXT_PACKS
PACKS.update(TEXT_PACKS)

# Getting around (pedestrian lights, crossings, pavements, obstacles) and homes around the world.
from world_life_packs import LIFE_PACKS
PACKS.update(LIFE_PACKS)

# The human body: non-sexual nudes in museum art, and anatomy figures (the kit uses them only when chosen).
from body_packs import BODY_PACKS
PACKS.update(BODY_PACKS)

# Medical pictures (skin, X-rays, endoscopy, case-report figures, childhood illness, birth and feeding): content
# "medical", used only when the person training ticks "Include medical and anatomy pictures".
from medical_packs import MEDICAL_PACKS
PACKS.update(MEDICAL_PACKS)

# Facial expressions, gestures and body language (Open Images, Commons, BiCE-HG gestures, VQA questions).
from expression_packs import EXPRESSION_PACKS
PACKS.update(EXPRESSION_PACKS)

# More worldwide collections found by searching in other languages: Crossmodal-3600 (captions in 36 languages) and
# Finnish and Czech museums through Europeana.
from world_more_packs import WORLD_MORE_PACKS
PACKS.update(WORLD_MORE_PACKS)

# More museums and data portals found by searching in other languages (Hungary, Greece, Norway, Poland, Bangladesh,
# Indonesia), and Fashionpedia clothing.
from world_portal_packs import PORTAL_PACKS, PORTAL_TRANSLATE
PACKS.update(PORTAL_PACKS)
for _key, (_language, _model, _revision) in PORTAL_TRANSLATE.items():
    TRANSLATE[_key] = _language
    MT_MODELS.setdefault(_language, (_model, _revision))
from more_open_packs import MORE_OPEN_PACKS
PACKS.update(MORE_OPEN_PACKS)

# Documentary photos with real captions (Library of Congress, National Park Service, NASA Earth Observatory, ESO,
# USGS, Commons valued images): the open alternatives to commercial photo magazines.
from documentary_packs import DOCUMENTARY_PACKS
PACKS.update(DOCUMENTARY_PACKS)

# Disability and assistive technology: mobility aids, white canes, guide dogs, braille, tactile paving, accessible
# places and adaptive sports.
from disability_packs import DISABILITY_PACKS
PACKS.update(DISABILITY_PACKS)

# Graphic scenes described plainly (war, disasters, injuries and death) and practical safety scenes: rows marked
# "content": "graphic" are used by the kit only with the graphic-scenes choice, and never for picture-making.
from graphic_packs import GRAPHIC_PACKS
PACKS.update(GRAPHIC_PACKS)

# More archive, museum and news photographs with their makers' captions (US National Archives, New York Public Library,
# Getty Museum, Digital Commonwealth, Statens Museum for Kunst, Nationaal Archief, kremlin.ru, Australian War
# Memorial). Danish and Dutch captions get English translation twins; graphic rows carry "content": "graphic".
from archive_packs import ARCHIVE_PACKS, ARCHIVE_TRANSLATE
PACKS.update(ARCHIVE_PACKS)
for _key, (_language, _model, _revision) in ARCHIVE_TRANSLATE.items():
    TRANSLATE[_key] = _language
    MT_MODELS.setdefault(_language, (_model, _revision))

# Military equipment and the uniformed services, past and present (Commons models and uniforms found through Wikidata,
# Library of Congress, US National Archives, army.mil, the Smithsonian's air and history museums). War rows showing
# the dead or injured carry "content": "graphic".
from service_packs import SERVICE_PACKS
PACKS.update(SERVICE_PACKS)

# Bodily fluids and waste (dog poop in yards, animal droppings, blood, vomit, stool and urine): human medical rows
# carry "content": "medical". urine_samples needs pillow-heif (its photos are HEIC files).
from bodily_packs import BODILY_PACKS
PACKS.update(BODILY_PACKS)

# Sport, musical instruments, places of worship and religious life, landmarks and architecture, civilian vehicles,
# and toys, games, playing cards, chess and sheet music.
from culture_packs import CULTURE_PACKS
PACKS.update(CULTURE_PACKS)

# The land and the work done on it: crops and plant health, weeds, litter, clouds and weather, satellite views,
# industry, mining, energy and construction. Industrial accidents carry "content": "graphic". plp_floating_targets
# needs bsdtar or 7-Zip (its photos come in a RAR archive).
from land_industry_packs import LAND_PACKS
PACKS.update(LAND_PACKS)

# Practical home life: clock faces, seven-segment displays, household pests, appliances and their controls, plugs and
# batteries, laundry symbols, tools, toiletries, hairstyles and the kitchen (is the burner on?).
from home_packs import HOME_PACKS
PACKS.update(HOME_PACKS)

# Historical events by place and time (Commons through Wikidata, Library of Congress, US National Archives,
# Europeana) and safety training (ISO 7010, GHS and road signs, safety equipment and hazards, safety posters, D-Fire
# wildfire cameras). Rows naming the dead or wounded carry "content": "graphic".
from events_safety_packs import EVENTS_SAFETY_PACKS
PACKS.update(EVENTS_SAFETY_PACKS)

# Safety around munitions and guns, and children's rites: landmine, grenade, shell, bomb and rocket models,
# unexploded munitions and demining (Commons, AMLID drone photos), firearm and cartridge models, and baptisms, first
# communions, bar and bat mitzvahs and other rites (Commons, Europeana) behind a strict child-protection filter. Rows
# can carry "content": "graphic" or "child". amlid_landmines needs bsdtar or 7-Zip (its photos come in a 7z archive).
from safety_rites_packs import SAFETY_RITES_PACKS
PACKS.update(SAFETY_RITES_PACKS)

# Things and materials: Amazon Berkeley Objects products (rows carry "place_kind": "market", the country of the
# Amazon shop), Open Images people using things and technology, Commons electronics, tools, building supplies,
# kitchen gadgets and people at work, brick grades and building materials (CODD, NYUAD).
from things_packs import THINGS_PACKS
PACKS.update(THINGS_PACKS)

# Mechanical and automotive parts: Commons car, cycle and machine parts, engine bays and gauges, ISO machine symbols
# and warning lights, the Toyota Corolla engine bay, tyre condition, spark plug condition and planetary gearboxes.
from mechanical_packs import MECHANICAL_PACKS
PACKS.update(MECHANICAL_PACKS)

# People in daily activities: V-COCO and Visual Genome rows on COCO photos (rows only; the two packs on COCO's
# non-commercial and share-alike photos are for the kit's personal-use and share-alike choices), Open Images activity
# labels, Commons daily-life and work categories (with "People at work in" countries), Dollar Street routines.
from people_activity_packs import PEOPLE_ACTIVITY_PACKS
PACKS.update(PEOPLE_ACTIVITY_PACKS)


def sha256_of(path):
    """The SHA-256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_pack(key, entries, out):
    """Write the pack zip (rows.jsonl, pictures, CREDITS.txt), cut it into parts when over PART_BYTES; returns its
    manifest {"key", "rows", "pictures", "size", "sha256", "files"}."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{key}.zip")
    rows, credits, names = [], [], set()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        for name, data, row in entries:
            if data is not None:
                z.writestr(f"pictures/{name}", data)
                names.add(name)
                row = dict(row, file=f"pictures/{name}")       # (a translated twin already names its picture)
            rows.append(row)
            if row.get("credit"):
                credits.append(f"{row.get('file') or row.get('url')}: {row['credit']}")
        z.writestr("rows.jsonl", "".join(json.dumps(r) + "\n" for r in rows))
        z.writestr("CREDITS.txt", PACKS[key][1] + "\n\n" + "\n".join(credits) + "\n")
        # Every candidate the shared checks saw, used or not, with the reason it was dropped (see considered()).
        if CONSIDERED:
            z.writestr(f"considered-{key}.jsonl", "".join(considered_lines(rows, names)))
    size, digest = os.path.getsize(path), sha256_of(path)
    from convert_models import split_file          # the same splitting as the converted models
    parts = split_file(path, PART_BYTES)
    manifest = {"key": key, "rows": len(rows), "pictures": sum(1 for r in rows if r.get("file")), "size": size,
                "sha256": digest, "files": [os.path.basename(p) for p in parts]}
    with open(os.path.join(out, f"manifest-{key}.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    return manifest


def main(argv=None):
    """Build one pack (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("key", choices=sorted(PACKS))
    parser.add_argument("--out", default="build/packs")
    parser.add_argument("--limit", type=int, default=6000)
    args = parser.parse_args(argv)
    entries = PACKS[args.key][0](args.limit)
    if not entries:
        raise SystemExit(f"The {args.key} pack came out empty.")
    entries = add_translations(args.key, entries)
    manifest = write_pack(args.key, entries, args.out)
    say(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
