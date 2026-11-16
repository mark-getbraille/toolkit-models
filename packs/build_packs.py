"""Build the training-data packs of the Picture Model Training Kit on GitHub's machines (.github/workflows/packs.yml)
and publish them in this repository's release "training-data", so the kit downloads a few large files from here
instead of contacting many museum websites from the trainer's computer.

A pack is a zip: rows.jsonl (one row per picture: {"file" (a picture in the zip) or "url" (a picture the kit fetches
itself), "question", "answer", "credit"}), the pictures (JPEG, at most 896 pixels on the long side) and CREDITS.txt
(the licence, and each picture's credit where its licence asks for one). A zip over 1.9 GB is published in numbered
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


def session():
    """A requests session with the kit's name (Wikimedia asks for one with a contact)."""
    import requests
    s = requests.Session()
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
                    return (name, data, row) if data else None
                if r.status_code in (403, 404, 410):
                    return None
            except Exception:  # noqa: BLE001 - tried once more, then left out
                time.sleep(2)
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
        return url, {"question": ALT_TEXT, "answer": alt, "credit": credit}
    ext = first_sentences(ext, 90)
    if is_description(ext, 12):
        return url, {"question": NARRATE, "answer": ext, "credit": credit}
    for note in content.get("freetext", {}).get("notes", []):
        if note.get("label") in ("Gallery Label", "Luce Center Label", "Exhibition Label", "Description"):
            text = first_sentences(note.get("content"), 90)
            if len(text.split()) >= 15:
                title = clean(record.get("title"))
                answer = text if not title or title.lower() in text.lower() else f"{title}. {text}"
                return url, {"question": MUSEUM, "answer": answer, "credit": credit}
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


def coco_licences():
    """{COCO image id: its photo address} for photos under CC BY 2.0 or no known copyright (phiyodr/coco2017)."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download
    free = {}
    for name in HfApi().list_repo_files("phiyodr/coco2017", repo_type="dataset"):
        if name.endswith(".parquet"):
            table = pq.read_table(hf_hub_download("phiyodr/coco2017", name, repo_type="dataset"),
                                  columns=["license", "image_id", "coco_url"]).to_pylist()
            free.update({r["image_id"]: r["coco_url"] for r in table if r["license"] in COCO_FREE})
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
                  "iiurlwidth": LONG_SIDE, "iiextmetadatafilter": "LicenseShortName|Artist", "maxlag": 5}
        while len(items) < limit * 1.3:
            try:
                data = s.get(COMMONS_API, params=params, timeout=60).json()
            except Exception:  # noqa: BLE001 - wait and try again once
                time.sleep(10)
                continue
            pages = list((data.get("query") or {}).get("pages", {}).values())
            ids = [f"M{p['pageid']}" for p in pages if p.get("pageid")]
            labels = {}
            if ids:
                entities = s.get(COMMONS_API, timeout=60, params={"action": "wbgetentities", "format": "json",
                                                                  "ids": "|".join(ids), "props": "labels",
                                                                  "languages": "en"}).json().get("entities", {})
                labels = {k: ((v.get("labels") or {}).get("en") or {}).get("value", "") for k, v in entities.items()}
            for p in pages:
                info = (p.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata") or {}
                licence = clean((meta.get("LicenseShortName") or {}).get("value"))
                caption = clean(labels.get(f"M{p.get('pageid')}"))
                if p["pageid"] in seen or not caption or len(caption.split()) < 5 or "SA" in licence.upper() \
                        or "NC" in licence.upper() or not COMMONS_FREE.match(licence) or not info.get("thumburl"):
                    continue
                seen.add(p["pageid"])
                artist = clean((meta.get("Artist") or {}).get("value"))
                credit = f"{p['title']} by {artist or 'unknown'}, {licence}, https://commons.wikimedia.org/wiki/" + \
                    p["title"].replace(" ", "_")
                answer = caption[:1].upper() + caption[1:] + ("" if caption.endswith((".", "!", "?")) else ".")
                items.append((f"commons-{p['pageid']}.jpg", info["thumburl"],
                              {"question": ALT_TEXT, "answer": answer, "credit": credit}))
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
                               "credit": f"Te Papa (record {r['id']}), {rights}"}))
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
                              {"question": question, "answer": answer,
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


def mendeley_zip(dataset):
    """The first zip file of a Mendeley Data dataset, downloaded (its download address)."""
    s = session()
    files = s.get(f"https://data.mendeley.com/public-api/datasets/{dataset}/files?folder_id=root&version=1",
                  timeout=60).json()
    zipped = next(f for f in files if f["filename"].lower().endswith(".zip"))
    return zipfile.ZipFile(io.BytesIO(s.get(zipped["content_details"]["download_url"], timeout=1800).content))


BANKNOTES = {"INDIA": ("Indian", "rupee"), "THAI": ("Thai", "baht")}


def build_banknotes(limit):
    """Indian and Thai banknotes photographed for visually impaired users (Mendeley 2kfz5yc7pt, CC BY 4.0):
    "Which banknote is this?" """
    z, out = mendeley_zip("2kfz5yc7pt"), []
    for name in z.namelist():
        folder = name.split("/")[-2] if "/" in name else ""
        m = re.match(r"(INDIA|THAI)(\d+)(NEW|OLD)?$", folder)
        if not m or not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        country, unit = BANKNOTES[m.group(1)]
        design = {"NEW": " (the new design)", "OLD": " (the old design)"}.get(m.group(3) or "", "")
        data = smaller(z.read(name))
        if data:
            out.append((f"note-{len(out)}.jpg", data, {"question": "Which banknote is this?",
                        "answer": f"This is {article(country)} {country} {int(m.group(2)):,} {unit} note{design}.",
                        "credit": "Indian and Thai banknotes dataset (Mendeley Data 2kfz5yc7pt), CC BY 4.0"}))
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
                                                              "CC BY 4.0"}))
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
    "tepapa": (build_tepapa, "Museum of New Zealand Te Papa Tongarewa: record text CC BY 4.0; pictures CC BY 4.0 or "
                             "no known copyright restrictions, each credited below. https://collections.tepapa.govt.nz"),
}


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
    rows, credits = [], []
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        for name, data, row in entries:
            if data is not None:
                z.writestr(f"pictures/{name}", data)
                row = dict(row, file=f"pictures/{name}")
            rows.append(row)
            if row.get("credit"):
                credits.append(f"{row.get('file') or row.get('url')}: {row['credit']}")
        z.writestr("rows.jsonl", "".join(json.dumps(r) + "\n" for r in rows))
        z.writestr("CREDITS.txt", PACKS[key][1] + "\n\n" + "\n".join(credits) + "\n")
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
    manifest = write_pack(args.key, entries, args.out)
    say(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
