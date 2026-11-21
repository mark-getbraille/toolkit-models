"""Pack builders for FOOD RIPENESS AND QUALITY from open research datasets, used by build_packs.py in the same way
as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row
is {"question", "answer", "credit"}, plus "place" where the dataset says where its photos were taken. The limit
counts pictures.

Why this file: the Commons food packs (home_safety_packs.commons_food_state, food_packs) find very few photos of
ripeness and spoilage, because Commons has almost no categories that say "unripe", "overripe" or "spoiled". These
datasets were made for exactly that question: people sorted every fruit into a stage or a quality class, so the
answer is the dataset's own label, never a guess from the picture (nothing is written by an AI model).

Every licence was checked on the Mendeley Data record itself on 2026-11-21 (its "data_licence" field), and every
download uses Mendeley Data's own public addresses: the dataset record (/public-api/datasets/<id>), the "Download
All" archive (/public-api/zip/<id>/download/<version>) or a listed file's download address (/public-files/...).
Mendeley's robots.txt leaves these addresses open (it closes /api/ and page listings only). The archives are read
piece by piece (world_life_packs.remote_zip), so only the photos taken are downloaded.

The packs (all CC BY 4.0):
  avocado_ripeness  'Hass' Avocado Ripening Photographic Dataset (Xavier, Rodrigues and Silva, Mendeley 3xd9n945v8):
                    14,710 photos of 478 avocados photographed every day as they ripened, each given one of five
                    stages of a Ripening Index in the makers' spreadsheet: underripe, breaking, ripe (first stage),
                    ripe (second stage, the end of shelf life) and overripe. "Is this avocado ripe?" An even share
                    of each stage.
  banana_ripeness   BananaImageBD (Ferdaus et al., Mendeley ptfscwtnyz, version 2): the 820 original photos of its
                    ripeness part, sorted by the makers into green, semi-ripe, ripe and overripe, taken at banana
                    wholesale markets in Bangladesh. "Is this banana ripe?" (The augmented copies are not used.)
  fruitnet_quality  FruitNet (Meshram and Patil, Mendeley b6fftwbr2v, version 3): phone photos of six Indian fruits
                    (apple, banana, guava, lime, orange, pomegranate) that the makers sorted into good quality, bad
                    quality and mixed (good and bad together). "Is this fruit good or bad?" An even share of each
                    fruit and class.

Not repeated: fresh_rotten (build_packs.py: fresh or rotten fruit, Sultana et al.) and agrob_tomato
(land_industry_packs.py: greenhouse tomato ripeness).

Run one builder alone for a quick check (prints rows, writes nothing):
    python3 packs/food_quality_packs.py avocado_ripeness --limit 10
"""

import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import smaller, say, pass_random
from food_packs import count_pictures
from world_life_packs import remote_zip
from places import where

MENDELEY_ZIP = "https://data.mendeley.com/public-api/zip/{id}/download/{version}"
PHOTO = re.compile(r"\.(jpe?g|png)$", re.I)


def a_or_an(word):
    """ "an" before a vowel sound, else "a" ("an apple", "a guava")."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def take_even(groups, limit, seed):
    """An even share of each group: {group: [items]} -> [items], at most limit in all, each group shuffled the same
    way each time (a different way on a top-up pass). A small group gives what it has and the others fill in."""
    rng = pass_random(seed)
    queues = {g: rng.sample(items, len(items)) for g, items in sorted(groups.items())}
    out = []
    while len(out) < limit and any(queues.values()):
        for g in sorted(queues):
            if queues[g] and len(out) < limit:
                out.append(queues[g].pop())
    return out


# ----------------------------------------------------------------- reading a spreadsheet without extra packages

def xlsx_rows(data):
    """The rows of the first sheet of an .xlsx file (bytes) as lists of cell texts. A small reader of the file's own
    XML, so the build needs no spreadsheet package; numbers come back as their text ("1", "2.0")."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t")))
    sheet = sorted(n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml$", n))[0]
    rows = []
    for row in ET.fromstring(z.read(sheet)).iter(f"{{{ns['m']}}}row"):
        cells = {}
        for c in row.findall("m:c", ns):
            col = re.match(r"[A-Z]+", c.get("r", "A")).group(0)
            v = c.find("m:v", ns)
            text = "" if v is None else (v.text or "")
            if c.get("t") == "s" and text.isdigit():
                text = shared[int(text)]
            elif c.get("t") == "inlineStr":
                text = "".join(t.text or "" for t in c.iter(f"{{{ns['m']}}}t"))
            cells[col] = text
        width = max((col_number(k) for k in cells), default=0)
        rows.append([cells.get(col_letters(i), "") for i in range(1, width + 1)])
    return rows


def col_number(letters):
    """A spreadsheet column's number ("A" -> 1, "AA" -> 27)."""
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def col_letters(n):
    """A spreadsheet column's letters (1 -> "A", 27 -> "AA")."""
    out = ""
    while n:
        n, r = divmod(n - 1, 26)
        out = chr(65 + r) + out
    return out


# ----------------------------------------------------------------- avocado_ripeness

AVOCADO = ("3xd9n945v8", 1)
AVOCADO_CREDIT = ("'Hass' Avocado Ripening Photographic Dataset (Pedro Xavier, Pedro Rodrigues and Cristina L. M. "
                  "Silva), Mendeley Data, doi:10.17632/3xd9n945v8.1, CC BY 4.0")
ASK_AVOCADO = "Is this avocado ripe?"
# The dataset's five-stage Ripening Index, in its makers' words (stage 4 is "the end of the avocados' shelf-life";
# stage 5 is "beyond its prime"), said as an answer.
AVOCADO_STAGES = {
    "1": "No: it is underripe (stage 1 of the 5 ripening stages its photographers used).",
    "2": "Not yet: it is breaking, just starting to ripen (stage 2 of 5).",
    "3": "Yes: it is ripe, in the first ripe stage (stage 3 of 5).",
    "4": "Yes: it is ripe, in the second ripe stage (stage 4 of 5), the end of its shelf life, so eat it soon.",
    "5": "It is overripe (stage 5 of 5): past its best.",
}


def avocado_stages(rows):
    """{photo name without .jpg: stage "1".."5"} from the makers' spreadsheet rows (a header row naming "File Name"
    and "Ripening Index Classification", then one row per photo). Rows without a stage 1 to 5 are left out."""
    if not rows:
        return {}
    head = [h.strip().lower() for h in rows[0]]
    try:
        name_at = head.index("file name")
        stage_at = next(i for i, h in enumerate(head) if h.startswith("ripening index"))
    except (ValueError, StopIteration):
        return {}
    out = {}
    for r in rows[1:]:
        if len(r) <= max(name_at, stage_at):
            continue
        stage = re.sub(r"\.0$", "", r[stage_at].strip())
        if r[name_at].strip() and stage in AVOCADO_STAGES:
            out[r[name_at].strip()] = stage
    return out


def build_avocado_ripeness(limit):
    """The avocado pack: an even share of the five ripening stages, each photo's stage from the makers'
    spreadsheet (a photo the spreadsheet does not list is left out)."""
    z = remote_zip(MENDELEY_ZIP.format(id=AVOCADO[0], version=AVOCADO[1]))
    names = z.namelist()
    sheet = next(n for n in names if n.lower().endswith(".xlsx"))
    stages = avocado_stages(xlsx_rows(z.read(sheet)))
    say(f"Avocado: {len(stages)} photos in the spreadsheet")
    groups = {}
    for n in names:
        stem = n.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if PHOTO.search(n) and stem in stages:
            groups.setdefault(stages[stem], []).append(n)
    out = []
    for n in take_even(groups, int(limit * 1.05) + 2, 3709):
        stage = stages[n.rsplit("/", 1)[-1].rsplit(".", 1)[0]]
        data = smaller(z.read(n))
        if data:
            out.append((f"avocado-{stage}-{len(out)}.jpg", data,
                        {"question": ASK_AVOCADO, "answer": AVOCADO_STAGES[stage], "credit": AVOCADO_CREDIT}))
    say(f"Avocado: {len(out)} photos")
    return out[:limit]


# ----------------------------------------------------------------- banana_ripeness

BANANA = ("ptfscwtnyz", 2)
BANANA_CREDIT = ("BananaImageBD: A Comprehensive Image Dataset of Common Banana Varieties with Different Ripeness "
                 "Stages in Bangladesh (Md Hasanul Ferdaus and others), Mendeley Data, doi:10.17632/ptfscwtnyz.2, "
                 "CC BY 4.0")
ASK_BANANA = "Is this banana ripe?"
BANANA_STAGES = {"green": "No: it is green (unripe).", "semi-ripe": "Nearly: it is semi-ripe.",
                 "ripe": "Yes: it is ripe.", "overripe": "It is overripe: very soft and sweet, past its best for "
                                                         "eating as it is."}


def banana_stage(name):
    """The ripeness stage of a photo of the ripeness part (not the augmented copies) from its folder
    ("Banana Ripeness Detection Dataset/Semi-ripe/x.jpg" -> "semi-ripe"), or ""."""
    parts = name.split("/")
    if len(parts) < 3 or "augmented" in name.lower() or parts[-3].lower() != "banana ripeness detection dataset":
        return ""
    stage = parts[-2].strip().lower()
    return stage if stage in BANANA_STAGES else ""


def build_banana_ripeness(limit):
    """The banana pack: the original ripeness photos (an inner zip of the Download All archive), an even share of
    the four stages."""
    outer = remote_zip(MENDELEY_ZIP.format(id=BANANA[0], version=BANANA[1]))
    inner_name = next(n for n in outer.namelist()
                      if n.rsplit("/", 1)[-1].lower() == "banana ripeness detection dataset.zip")
    z = zipfile.ZipFile(io.BytesIO(outer.read(inner_name)))
    groups = {}
    for n in z.namelist():
        stage = banana_stage(n) if PHOTO.search(n) else ""
        if stage:
            groups.setdefault(stage, []).append(n)
    out = []
    for n in take_even(groups, int(limit * 1.05) + 2, 2457):
        stage = banana_stage(n)
        data = smaller(z.read(n))
        if data:
            out.append((f"banana-{stage}-{len(out)}.jpg", data,
                        {"question": ASK_BANANA, "answer": BANANA_STAGES[stage], "credit": BANANA_CREDIT,
                         **where("Bangladesh")}))
    say(f"Banana: {len(out)} photos")
    return out[:limit]


# ----------------------------------------------------------------- fruitnet_quality

FRUITNET = ("b6fftwbr2v", 3)
FRUITNET_ZIP = ("https://data.mendeley.com/public-files/datasets/b6fftwbr2v/files/"
                "532e56bf-d855-4afd-86fd-2c8c425eb32c/file_downloaded")      # FruitNetDataset.zip, 3.25 GB
FRUITNET_CREDIT = ("FruitNet: Indian Fruits Dataset with quality (Vishal Meshram and Kailas Patil), Mendeley Data, "
                   "doi:10.17632/b6fftwbr2v.3, CC BY 4.0")
ASK_FRUIT = "Is this fruit good or bad?"
FRUITS = {"apple": "apple", "banana": "banana", "guava": "guava", "lime": "lime", "lemon": "lime", "orange": "orange",
          "pomegranate": "pomegranate"}


def fruitnet_label(name):
    """(fruit, quality "good", "bad" or "mixed") of a FruitNet photo from its folders ("Bad Quality_Fruits/
    Apple_Bad/x.jpg" -> ("apple", "bad"); "Mixed Qualit_Fruits/Lemon/x.jpg" -> ("lime", "mixed"), the makers'
    name for the lime folder there), or None."""
    parts = name.split("/")
    if len(parts) < 3:
        return None
    top, folder = parts[-3].lower(), parts[-2].lower()
    quality = "good" if top.startswith("good") else "bad" if top.startswith("bad") else \
        "mixed" if top.startswith("mixed") else ""
    fruit = FRUITS.get(folder.split("_")[0])
    if not quality or not fruit:
        return None
    if "_" in folder and folder.split("_")[1] != quality:
        return None
    return fruit, quality


def fruitnet_answer(fruit, quality):
    """The answer from the makers' class: "This is a good-quality guava, as the dataset's makers sorted it." """
    if quality == "mixed":
        return (f"These are {fruit}s of mixed quality: the dataset's makers photographed good and bad ones "
                f"together.")
    if quality == "good":
        return f"This is {a_or_an(fruit)} {fruit} of good quality, as the dataset's makers sorted it."
    return (f"This is {a_or_an(fruit)} {fruit} of bad quality, as the dataset's makers sorted it: do not eat fruit "
            f"that is rotten or mouldy.")


def build_fruitnet_quality(limit):
    """The FruitNet pack: an even share of each fruit and quality class, read piece by piece from the 3.25 GB
    archive (only the photos taken are downloaded)."""
    z = remote_zip(FRUITNET_ZIP)
    groups = {}
    for n in z.namelist():
        label = fruitnet_label(n) if PHOTO.search(n) else None
        if label:
            groups.setdefault(label, []).append(n)
    say(f"FruitNet: {sum(map(len, groups.values()))} photos in {len(groups)} fruit and quality classes")
    out = []
    for n in take_even(groups, int(limit * 1.05) + 2, 107686):
        fruit, quality = fruitnet_label(n)
        data = smaller(z.read(n))
        if data:
            out.append((f"fruitnet-{fruit}-{quality}-{len(out)}.jpg", data,
                        {"question": ASK_FRUIT, "answer": fruitnet_answer(fruit, quality),
                         "credit": FRUITNET_CREDIT, **where("India")}))
    say(f"FruitNet: {len(out)} photos")
    return out[:limit]


# ----------------------------------------------------------------- the packs

FOOD_QUALITY_PACKS = {
    "avocado_ripeness": (build_avocado_ripeness, "'Hass' Avocado Ripening Photographic Dataset (Xavier, Rodrigues "
                                                 "and Silva), CC BY 4.0, https://doi.org/10.17632/3xd9n945v8.1"),
    "banana_ripeness": (build_banana_ripeness, "BananaImageBD (Ferdaus et al.), ripeness stages, original photos "
                                               "only, CC BY 4.0, https://doi.org/10.17632/ptfscwtnyz.2"),
    "fruitnet_quality": (build_fruitnet_quality, "FruitNet: Indian fruits dataset with quality (Meshram and Patil), "
                                                 "CC BY 4.0, https://doi.org/10.17632/b6fftwbr2v.3"),
}

# How many pictures a full build takes from each.
FOOD_QUALITY_LIMITS = {
    "avocado_ripeness": 1500,     # of 14,710 (300 per stage; many photos are the same avocado on other days)
    "banana_ripeness": 820,       # all 820 original ripeness photos
    "fruitnet_quality": 2400,     # of about 19,500 (about 130 per fruit and class)
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one food ripeness and quality pack builder.")
    parser.add_argument("key", choices=sorted(FOOD_QUALITY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = FOOD_QUALITY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
