"""Pack builders for pictures of pills and medicine packs, used by build_packs.py in the same way as its own PACKS:
each builder is build_<key>(limit) and returns [(file name, JPEG bytes, row)], where a row is {"question", "answer",
"credit"}.

Every answer is careful: it says what the medicine "looks like", never that it certainly is that medicine, and ends
with SAFETY ("Check the packaging or ask a pharmacist to be sure."). A model must never sound sure about a pill.

  taiwan_pills  Taiwan Food and Drug Administration, drug appearance open data (Open Government Data License v1.0,
                which allows commercial use and is compatible with CC BY 4.0): one photo per licensed tablet or
                capsule, on a millimetre scale, with its English name, shape, colour, score line, size and imprint.
                Asked: "What pill is this?"
  pharmassist   Pharmassist (Mendeley Data zbnhmbbymd, CC BY 4.0): photos of used, torn blister packs of 53 medicines
                sold in India, taken in Chennai. Only the original photos ("Raw"), never the dataset's altered copies.
                Asked: "What medicine is in this blister pack?"
  mediseg       MEDISEG (figshare 28574786, CC BY 4.0): photos of loose pills, often several kinds together in a pill
                box, of 32 medicines on the Hong Kong drug register, every pill marked. Asked: "What pills are in
                this picture?"

    python packs/pill_packs.py taiwan_pills --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import os
import random
import re
import sys
import tarfile
import tempfile
import time
import zipfile

from build_packs import session, clean, smaller, fetch_all, say  # noqa: F401
from places import with_place

SAFETY = "Check the packaging or ask a pharmacist to be sure."


# ----------------------------------------------------------------- shared helpers

UNITS = {"MG": "mg", "MCG": "mcg", "ML": "ml", "G": "g", "IU": "IU", "KG": "kg", "HCL": "HCl"}
FORM_WORDS = {"TABLET", "TABLETS", "CAPSULE", "CAPSULES", "TAB", "CAP", "FILM", "COATED", "FILM-COATED", "SOFT",
              "GELATIN", "CHEWABLE", "ORODISPERSIBLE", "GASTRO-RESISTANT", "PROLONGED-RELEASE", "SUSTAINED",
              "RELEASE", "EXTENDED", "DELAYED", "ENTERIC", "AND", "WITH", "FOR"}


def readable_case(text):
    """A medicine name written in capitals ("SODIUM BICARBONATE TABLETS 500MG") in readable case ("Sodium
    Bicarbonate tablets 500 mg"). Names that already have small letters are only tidied. Short words such as "F.C."
    or "SR" stay in capitals."""
    text = clean(text).replace("®", "").replace("™", "").replace("“", '"').replace("”", '"')
    text = re.sub(r"(\d)\s*(MG|MCG|ML|IU|mg|mcg|ml)\b", r"\1 \2", text)            # "500MG" -> "500 MG"
    text = re.sub(r'(\S)"(?=\w)', r'\1 "', text)                                   # 'mg"EVEREST"' -> 'mg "EVEREST"'
    if re.search(r"[a-z]", text):
        return re.sub(r"(\d) (MG|MCG|ML)\b", lambda m: f"{m.group(1)} {m.group(2).lower()}", text)

    def word(m):
        """One word in readable case."""
        w = m.group(0)
        if w in UNITS:
            return UNITS[w]
        if w in FORM_WORDS:
            return w.lower()
        if len(w) <= 2:
            return w
        return w[0] + w[1:].lower()

    text = re.sub(r"[A-Z][A-Z]*", word, text)
    return text[0].upper() + text[1:] if text else text


def article(words):
    """ "a" or "an" before words."""
    return "an" if words[:1].lower() in "aeiou" else "a"


def listed(parts):
    """ "a", "a and b" or "a, b and c"."""
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


# ----------------------------------------------------------------- Taiwan FDA drug appearance (Taiwan)

TW_DATA = "https://data.fda.gov.tw/data/opendata/export/42/json"
TW_CREDIT = "Taiwan Food and Drug Administration, drug appearance open data, Open Government Data License v1.0"
# Every value of the shape field (形狀) in the data: (English shape, or "" to leave the shape out; tablet or capsule).
TW_SHAPES = {"圓形": ("round", "tablet"), "膠囊": ("", "capsule"), "橢圓形": ("oval", "tablet"),
             "四邊形": ("rectangular", "tablet"), "三角形": ("triangular", "tablet"), "六邊形": ("hexagonal", "tablet"),
             "八邊形": ("octagonal", "tablet"), "水滴形": ("teardrop-shaped", "tablet"),
             "雙圓形": ("double-round", "tablet"), "五邊形": ("pentagonal", "tablet"), "其他": ("", "tablet")}
# Liquids and powders (液劑 ..., 顆粒劑、粉劑或散劑) have no pill to photograph: left out.
TW_NOT_A_PILL = re.compile(r"液劑|顆粒劑|粉劑|散劑")
TW_NOT_A_PILL_NAME = re.compile(r"\b(solution|syrup|injection|infusion|suspension|powder|granules?|liquid|mixture|"
                                r"cream|ointment|lotion|drops|spray|gel)\b", re.I)
# Every colour in the colour field (顏色); ";;;" separates the two colours of a two-coloured pill.
TW_COLOURS = {"白": "white", "黃": "yellow", "粉": "pink", "橘": "orange", "藍": "blue", "綠": "green", "棕": "brown",
              "紅": "red", "紫": "purple", "透明": "clear", "黑": "black", "灰": "grey", "藍綠": "blue-green"}
TW_SCORES = {"直線": "a score line", "十字": "a cross-shaped score line", "無": ""}
# Across for round and many-sided pills, long for long ones.
TW_LONG = {"", "oval", "rectangular", "teardrop-shaped", "double-round"}


def tw_parts(value):
    """The parts of a Taiwan field ("白;;;藍" -> ["白", "藍"]), without empty ones."""
    return [p.strip() for p in str(value or "").split(";;;") if p.strip()]


def tw_imprint(value):
    """The imprint text of one side ("頭CL;;;尾016" -> "CL 016"), or "" when there is none or it is described in
    Chinese ("六邊形裡面有K": a K inside a hexagon)."""
    parts = []
    for p in tw_parts(value):
        p = re.sub(r"^[頭尾]", "", p).strip()                 # 頭/尾: the cap or body of a capsule
        if p and p != "無" and not re.search(r"[⺀-鿿]", p) and p not in parts:
            parts.append(p)
    return " ".join(parts)


def tw_size(value):
    """The size in millimetres ("8.0" -> "8"), or "" when unknown."""
    sizes = []
    for p in tw_parts(value):
        try:
            sizes.append(float(p))
        except ValueError:
            continue
    if not sizes or not 1 <= max(sizes) <= 40:
        return ""
    return f"{max(sizes):g}"


def tw_row(record):
    """(picture address, row) for one Taiwan record that shows a single kind of tablet or capsule with an English
    name, or None."""
    name = readable_case(record.get("英文品名"))
    shapes = tw_parts(record.get("形狀"))
    pictures = [u for u in tw_parts(record.get("外觀圖檔連結")) if u.startswith("http")]
    # Several shapes mean several different pills under one licence (a pack of two kinds): left out.
    if not name or not pictures or len(shapes) != 1 or shapes[0] not in TW_SHAPES or TW_NOT_A_PILL.search(shapes[0]) \
            or TW_NOT_A_PILL_NAME.search(name):
        return None
    shape, kind = TW_SHAPES[shapes[0]]
    colours = []
    for c in tw_parts(record.get("顏色")):
        if c not in TW_COLOURS:
            return None                                      # an unknown colour: better left out than guessed
        if TW_COLOURS[c] not in colours:
            colours.append(TW_COLOURS[c])
    looks = " ".join(w for w in (" and ".join(colours), shape, kind) if w)
    text = f"This looks like {name}: {article(looks)} {looks}"
    size = tw_size(record.get("外觀尺寸"))
    if size:
        text += f" about {size} mm {'long' if shape in TW_LONG else 'across'}"
    marks = []
    first, second = tw_imprint(record.get("標註一")), tw_imprint(record.get("標註二"))
    if first and second and first != second:
        marks.append(f"the imprint '{first}' (and '{second}' on the other side)")
    elif first or second:
        marks.append(f"the imprint '{first or second}'")
    scores = [TW_SCORES.get(s, "") for s in tw_parts(record.get("刻痕"))]
    if scores and scores[0]:
        marks.append(scores[0])
    if marks:
        text += ", with " + " and ".join(marks)
    answer = f"{text}. {SAFETY}"
    return pictures[0], {"question": "What pill is this?", "answer": answer,
                         "credit": f"{name} (licence {clean(record.get('許可證字號'))}), {TW_CREDIT}"}


def build_taiwan_pills(limit):
    """The Taiwan pills pack's pictures: [(name, JPEG, row)]. Reads the open data (a zip holding one JSON list) and
    fetches the photos from mcp.fda.gov.tw politely (few at a time, with a pause)."""
    s = session()
    with zipfile.ZipFile(io.BytesIO(s.get(TW_DATA, timeout=300).content)) as z:
        records = json.loads(z.read(next(n for n in z.namelist() if n.endswith(".json"))).decode("utf-8-sig"))
    items, seen = [], set()
    for record in records:
        got = tw_row(record)
        if got and got[0] not in seen:
            seen.add(got[0])
            items.append((f"tw-{re.sub(r'[^0-9a-f-]', '', got[0].rsplit('/', 1)[-1].split('?')[0])[:40]}.jpg", *got))
    say(f"Taiwan FDA: {len(items)} usable pills of {len(records)} records")
    random.Random(41).shuffle(items)
    return with_place(fetch_all(items[:int(limit * 1.05) + 2], workers=3, pause=0.3)[:limit],
                      "Taiwan")                                # photographed for Taiwan's FDA register


# ----------------------------------------------------------------- Pharmassist blister packs (India)

PA_DATASET = "https://data.mendeley.com/public-api/datasets/zbnhmbbymd"
PA_CREDIT = "Pharmassist dataset (Kapilesh N et al., Vellore Institute of Technology), Mendeley Data zbnhmbbymd, " \
            "CC BY 4.0"
# Class labels written as on the pack ("Alprax 0-25" is Alprax 0.25).
PA_NAMES = {"Alprax 0-25": "Alprax 0.25", "GlimiSave M 0-5": "GlimiSave M 0.5", "Gluxit10": "Gluxit 10",
            "Pacimol650": "Pacimol 650", "Tayo60k": "Tayo 60K", "Sibelium 10mg": "Sibelium 10 mg"}
# Medicines in the set that are not tablets; "" where the form is not certain (vitamin D and cranberry products come
# as tablets or capsules), so the answer names only the medicine.
PA_FORMS = {"Strepsils": "lozenges", "Cofsils": "lozenges", "Bifilac": "capsules", "Becozinc": "capsules",
            "Vitamin E": "capsules", "Tayo60k": "", "D-Rise": "", "D3 More 2K": "", "Cranmed": ""}


def pa_answer(label):
    """The answer for one Pharmassist class label."""
    name = PA_NAMES.get(label, label)
    form = PA_FORMS.get(label, "tablets")
    return f"This looks like a blister pack of {name}{' ' + form if form else ''}. {SAFETY}"


def build_pharmassist(limit):
    """The Pharmassist pack's pictures: [(name, JPEG, row)]. metadata.csv tells which files are original photos
    ("Raw") and which medicine each shows; each raw photo is downloaded by its own address."""
    s = session()
    files = {f["filename"]: f for f in s.get(PA_DATASET, timeout=120).json().get("files", [])}
    table = s.get(files["metadata.csv"]["content_details"]["download_url"], timeout=120).content.decode("utf-8-sig")
    items = []
    for r in csv.DictReader(io.StringIO(table)):
        f = files.get(r.get("Filename", ""))
        if r.get("Image_Type") != "Raw" or not f or not r.get("Class_Label"):
            continue
        items.append((f"pharmassist-{r['Object_ID']}.jpg", f["content_details"]["download_url"],
                      {"question": "What medicine is in this blister pack?", "answer": pa_answer(r["Class_Label"]),
                       "credit": PA_CREDIT}))
    say(f"Pharmassist: {len(items)} original photos")
    random.Random(42).shuffle(items)
    return with_place(fetch_all(items[:int(limit * 1.05) + 2], workers=3, pause=0.3)[:limit],
                      "Chennai, India")                        # taken in Chennai (the dataset's record)


# ----------------------------------------------------------------- MEDISEG loose pills (Hong Kong)

MS_ARCHIVE = "https://ndownloader.figshare.com/files/52926545"         # MEDISEG.tar.gz, 439 MB
MS_CREDIT = "MEDISEG (Chu et al.), figshare 28574786, CC BY 4.0"
MS_SET = "MEDISEG/32pills/"
MS_SMALLEST = 25          # pixels (of 640): pictures where a pill is smaller than this are too small to tell
SALTS = re.compile(r"\b(hydrochloride|hydrobromide|sodium|potassium|calcium|tartrate|succinate|fumarate|acetate|"
                   r"besilate|besylate|bisulfate|maleate|mesylate|citrate)\b", re.I)
MS_FORM = re.compile(r"\b(FILM[- ]COATED|ORODISPERSIBLE|GASTRO-RESISTANT|PROLONGED-RELEASE)?\s*(TAB|TABLETS?)\b", re.I)


def ms_ingredient(text):
    """An ingredient without its salt or "(as ...)" ("clopidogrel (as bisulfate)" -> "clopidogrel")."""
    text = re.sub(r"\(.*?\)", "", clean(text))
    return " ".join(SALTS.sub("", text).split()).lower()


def ms_medicine(row):
    """(name, how it is taken, ingredients) for one metadata.csv row: ("Lasix 40 mg", "tablet", "frusemide")."""
    name = clean(row.get("name")).upper()
    maker = re.search(r"\(([A-Z ]+)\)", name)                  # "WARFARIN TAB 1MG (TEVA)"
    name = re.sub(r"\([A-Z ]+\)", "", name)
    form = MS_FORM.search(name)
    kind = (form.group(1).lower().replace("film coated", "film-coated") + " tablet") if form and form.group(1) \
        else "tablet"
    strength = re.search(r"(\d+(?:\.\d+)?)\s*MG(?:\s*/\s*(\d+(?:\.\d+)?)\s*MG)?", name)
    brand = MS_FORM.sub(" ", name[:strength.start()] if strength else name)
    brand = readable_case(" ".join(brand.split() + ([maker.group(1)] if maker else [])))
    if strength:
        brand = re.sub(rf"\s+{re.escape(strength.group(1))}$", "", brand)      # "Bisostad 5 ... 5MG": once only
        brand += f" {strength.group(1)} mg" + (f"/{strength.group(2)} mg" if strength.group(2) else "")
    ingredients = [ms_ingredient(v) for k, v in sorted(row.items()) if k.startswith("ingredients/") and clean(v)]
    return brand, kind, listed(ingredients) if ingredients else ""


def ms_answer(counts, medicines):
    """The answer for one picture: counts is {category: number of pills}, medicines {category: ms_medicine}."""
    total = sum(counts.values())
    parts = []
    for category, n in sorted(counts.items(), key=lambda kv: (-kv[1], medicines[kv[0]][0])):
        name, kind, ingredients = medicines[category]
        what = f"{name} {kind}s" if n > 1 else f"{article(name)} {name} {kind}"
        parts.append(f"{n} that {'look' if n > 1 else 'looks'} like {what}" + (f" ({ingredients})" if ingredients
                                                                               else ""))
    if total == 1:
        name, kind, ingredients = medicines[next(iter(counts))]
        text = f"There is 1 pill. It looks like {article(name)} {name} {kind}" + \
            (f" ({ingredients})" if ingredients else "")
    else:
        text = f"There are {total} pills: {listed(parts)}"
    return f"{text}. {SAFETY}"


def ms_archive():
    """The path of MEDISEG.tar.gz: MEDISEG_ARCHIVE when set (a copy already downloaded), else a download into a
    temporary file (deleted by the caller)."""
    path = os.environ.get("MEDISEG_ARCHIVE")
    if path and os.path.exists(path):
        return path, False
    s = session()
    handle, path = tempfile.mkstemp(suffix=".tar.gz")
    with os.fdopen(handle, "wb") as f, s.get(MS_ARCHIVE, timeout=1800, stream=True) as r:
        r.raise_for_status()
        for block in r.iter_content(1 << 20):
            f.write(block)
    return path, True


def ms_varied(pictures, limit):
    """Up to limit pictures, varied: one picture per original photo, then taken in turn from each mix of medicines
    (so the most photographed single pill does not fill the pack)."""
    groups, sources = {}, set()
    for p in pictures:
        source = re.sub(r"(_(jpe?g|png))?\.rf\.[0-9a-f]+\.\w+$", "", p["file"], flags=re.I)
        if source in sources:
            continue
        sources.add(source)
        groups.setdefault(tuple(sorted(p["counts"])), []).append(p)
    rng = random.Random(43)
    queues = [rng.sample(g, len(g)) for _, g in sorted(groups.items())]
    rng.shuffle(queues)
    out = []
    while queues and len(out) < limit:
        for q in list(queues):
            if len(out) >= limit:
                break
            out.append(q.pop())
            if not q:
                queues.remove(q)
    return out


def build_mediseg(limit):
    """The MEDISEG pack's pictures: [(name, JPEG, row)]. The 32-pill set: each picture's pills are counted from its
    marked outlines (COCO annotations, whose categories are named by the Hong Kong register numbers in
    metadata.csv). The 3-pill set is left out: its pictures are small crops (about 245 pixels) of only 3 medicines."""
    path, temporary = ms_archive()
    try:
        annotations, medicines = None, {}
        with tarfile.open(path, "r|gz") as tar:                 # first pass: the annotations and the register
            for member in tar:
                if member.name == MS_SET + "annotations.json":
                    annotations = json.load(tar.extractfile(member))
                elif member.name.endswith("MEDISEG/metadata.csv"):
                    table = tar.extractfile(member).read().decode("utf-8-sig")
                    medicines = {r["id"].strip(): ms_medicine(r) for r in csv.DictReader(io.StringIO(table))}
        categories = {c["id"]: c["name"].strip() for c in annotations["categories"] if c["name"].strip() in medicines}
        pictures = {i["id"]: {"file": i["file_name"], "counts": {}, "smallest": 9999} for i in annotations["images"]}
        for a in annotations["annotations"]:
            p = pictures[a["image_id"]]
            if a["category_id"] not in categories:
                p["smallest"] = 0                             # a pill of an unknown medicine: left out
                continue
            register = categories[a["category_id"]]
            p["counts"][register] = p["counts"].get(register, 0) + 1
            p["smallest"] = min(p["smallest"], min(a["bbox"][2:]))
        usable = [p for p in pictures.values() if p["counts"] and p["smallest"] >= MS_SMALLEST]
        say(f"MEDISEG: {len(usable)} usable pictures of {len(pictures)} (every pill at least {MS_SMALLEST} pixels)")
        chosen = {MS_SET + "images/" + p["file"]: p for p in ms_varied(usable, int(limit * 1.02) + 2)}
        out = []
        with tarfile.open(path, "r|gz") as tar:                 # second pass: the chosen pictures
            for member in tar:
                p = chosen.get(member.name)
                data = smaller(tar.extractfile(member).read()) if p else None
                if data:
                    out.append((f"mediseg-{len(out)}.jpg", data, {"question": "What pills are in this picture?",
                                "answer": ms_answer(p["counts"], medicines), "credit": MS_CREDIT}))
    finally:
        if temporary:
            os.remove(path)
    random.Random(44).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- the packs

PILL_PACKS = {
    "taiwan_pills": (build_taiwan_pills, "Taiwan Food and Drug Administration, drug appearance open data "
                                         "(https://data.fda.gov.tw), Open Government Data License, version 1.0 "
                                         "(https://data.gov.tw/en/license), compatible with CC BY 4.0. Answers "
                                         "written from the data's English names, shapes, colours, sizes and "
                                         "imprints."),
    "pharmassist": (build_pharmassist, "Pharmassist dataset (Kapilesh N, Tharaka P, Eesha C, Rekha D, Bhargavi R; "
                                       "Vellore Institute of Technology), Mendeley Data zbnhmbbymd, CC BY 4.0, "
                                       "https://data.mendeley.com/datasets/zbnhmbbymd (original photos only, made "
                                       "smaller)."),
    "mediseg": (build_mediseg, "MEDISEG (Wai Ip Chu et al.), figshare article 28574786, CC BY 4.0, "
                               "https://doi.org/10.6084/m9.figshare.28574786 (the 32-pill set; answers written from "
                               "its pill outlines and its Hong Kong drug-register list)."),
}

# How many pictures a full build takes from each collection (about what each offers after the checks).
PILL_LIMITS = {
    "taiwan_pills": 5500,
    "pharmassist": 2050,
    "mediseg": 6000,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one pill pack builder.")
    parser.add_argument("key", choices=sorted(PILL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    started = time.time()
    entries = PILL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries in {time.time() - started:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
