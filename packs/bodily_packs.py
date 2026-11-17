"""Pack builders for pictures of bodily fluids and waste, used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"} with, where known, "place", "child": True (the picture may show a child or comes from a report about a child)
and "content": "medical" (human medical material: stool, vomit, urine, blood; used only with the medical box). Pet and
yard material has no content mark (""). A picture with more than one question comes once with its JPEG and then again
as (None, None, row) rows naming the same picture (food_packs.with_twins). The limit counts pictures.

Why: a blind parent asks "my child was sick: what does this look like? is there blood in it?", and a blind dog owner
photographs the yard and asks "has my dog pooped here, and where?". A describer should say plainly what is visible
(colour, how loose or firm, any blood or mucus, where it is in the picture), never sound sure about a diagnosis, and say
when to get help.

Rules kept by every builder here (as in medical_packs.py):
  - Licence checked at the source, picture by picture where the source gives one: CC0, public domain, CC BY, or
    Apache-2.0 for a whole dataset. Never NC, ND, SA or research-only (those are in
    training-kit/kit/bodily_sources.py).
  - Answers are fixed sentences filled from each source's own labels, measurements and captions (nothing is written by
    an AI model). Human medical answers end with a fixed line saying when to see a doctor (STOOL_ADVICE,
    VOMIT_ADVICE, URINE_ADVICE, BLOOD_ADVICE).
  - Children: stool, vomit, urine and nappy contents may come from a child (they do not show the child). A picture from
    a report about a child is kept only when its caption is about the stool, urine or vomit itself and names no part of
    the body, and is marked "child". Open Images photos with a child in them are left out. Nothing unclothed, nothing
    sexual, no clinical photographs of intimate areas (medical_packs.GENITAL_AREA).

The packs (BODILY_PACKS):
  scatspotter          ScatSpotter ("ShitSpotter", Jon Crall, Kitware; CC BY 4.0, huggingface.co/datasets/erotemic/
                       shitspotter): phone photos of dog poop on grass, leaves, snow and pavements in upstate New York,
                       each pile outlined by hand. "Has a dog pooped in this picture? Where?" -> "Yes: there is one
                       pile of dog poop on the ground, near the bottom left of the picture." and "Is there anything on
                       the ground I should avoid stepping in?"; the "after" photos taken once the poop was picked up
                       give the "No" answers.
  inat_droppings       iNaturalist observations marked "Evidence of presence: Scat" for dogs, cats, horses, farm
                       animals, garden birds and animals of yards and parks (fox, deer, rabbit, hedgehog, raccoon, Canada
                       goose, pigeon), each photo's own licence CC0 or CC BY. "What is this?" -> "This is dog poop
                       (droppings left by a domestic dog)."
  open_images_bodily   Google Open Images V7 (labels CC BY 4.0; photos CC BY 2.0, checked photo by photo): photos whose
                       labels people checked by hand for blood, an injury, a bandage, a sticking plaster, poop, a cat
                       litter box or cat litter, or a stain: "Is there blood in this picture?" with "yes" from a label
                       people confirmed and "no" from one they checked and rejected. Photos with a child, a costume or
                       Halloween in their labels are left out.
  commons_bodily       Wikimedia Commons categories of human stool, the Bristol stool chart, vomit, urine and urine
                       colour charts, blood stains, nosebleeds, and dog, cat, horse, cow and bird droppings: pictures
                       CC0, public domain or CC BY (author credited). The category's own answer, and the file's English
                       caption or description where it is a real description. Pictures of a person's body only when the
                       file's words say the person is an adult.
  case_report_bodily   Figures of case reports in PubMed Central whose article licence is CC BY or CC0 (checked in
                       PMC's own metadata), one-picture photographs of stool (black, bloody or pale stool), vomit
                       (blood or "coffee grounds"), urine (red, dark, purple) or a nosebleed, with the authors' caption.
                       Adults (18 or over), or a child's report when the photo shows only the stool, urine or vomit.
  vet_case_bodily      The same for veterinary case reports about dogs, cats, rabbits and horses: diarrhoea, bloody
                       stool, vomit and urine (content "", pet material).
  urine_samples        Urine samples photographed in clear pots with four phones (celesca/urine-detector on Hugging
                       Face, Apache-2.0): the colour measured on each photo by its makers, and their laboratory's note
                       of whether the urine was clear or cloudy. "What colour is this urine?" The photos are HEIC files:
                       the builder needs the pillow-heif package (add "urine_samples" to the pillow-heif line of
                       .github/workflows/packs.yml); without it the pack is empty.

Not open, or needing sign-up (Roboflow and Kaggle dog-poop sets, the stool-colour cards of Taiwan, Japan and Ontario,
research stool collections): training-kit/kit/bodily_sources.py.

    python packs/bodily_packs.py scatspotter --limit 8      (prints a few rows: a quick check of one builder)
"""

import colorsys
import concurrent.futures
import csv
import io
import json
import random
import re
import sys
import time
import zipfile

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, article, inat_place, ALT_TEXT  # noqa: F401
from food_packs import (with_twins, listed, sentence, count_pictures, oi_lines, oi_licence_name, commons_members,
                        commons_entries, commons_place, commons_description, OI_CLASSES, OI_PICTURE)
from everyday_packs import RemoteZip, fetch_from_zip, number_word
from expression_packs import CHILD as CHILD_WORDS, OI_CHILD
from medical_packs import (europe_pmc, pmc_article, pmc_figures, adult_only, who_with_age, sex_of, animal_of,
                           safe_name, MULTI_PANEL, GENITAL_AREA, CHILD, PMC_FREE, DOCTOR, VET)
from places import where, country_at

# The fixed sentences said after a human medical answer (the owner's wording).
STOOL_ADVICE = "Only a doctor can diagnose this; if a child has blood in their stool, a black stool, or seems " \
               "unwell, contact a doctor."
VOMIT_ADVICE = "If vomit contains blood or looks like coffee grounds, get medical help."
URINE_ADVICE = "Only a doctor can diagnose this; if urine looks red, brown or cola-coloured, or stays very dark, " \
               "contact a doctor."
BLOOD_ADVICE = "If bleeding is heavy or does not stop, get medical help."
PET_ADVICE = "Only a vet can diagnose this; if a pet has blood in its poop or vomit, or seems unwell, contact a vet."

MEDICAL = {"content": "medical"}


def plain_rows(rows, **extra):
    """The rows with extra fields added to each (credit, place, child, content)."""
    return [dict(r, **extra) for r in rows]


# ----------------------------------------------------------------- where something is in a picture

def spot(cx, cy):
    """Plain words for a point given as shares of the picture's width and height (0 to 1): "near the bottom left",
    "in the middle", "near the top"."""
    across = "left" if cx < 0.36 else "right" if cx > 0.64 else ""
    down = "top" if cy < 0.36 else "bottom" if cy > 0.64 else ""
    if not across and not down:
        return "in the middle of the picture"
    if not down:
        return f"in the middle of the picture, towards the {across}"
    return f"near the {down} {across}".rstrip() + " of the picture"


def size_word(share):
    """ "a small" or "a" pile, from the share of the picture a pile's box covers."""
    return "a small pile" if share < 0.004 else "a pile"


# ----------------------------------------------------------------- ScatSpotter (dog poop, CC BY 4.0)

SCAT_REPO = "https://huggingface.co/datasets/erotemic/shitspotter/resolve/main/"
SCAT_CREDIT = "ScatSpotter / ShitSpotter dataset (Jon Crall, Kitware, 'ScatSpotter: A Dog Poop Detection Dataset', " \
              "WACV Workshops 2026, arXiv 2412.16473), CC BY 4.0, https://github.com/Erotemic/shitspotter"
DOG_Q = "Has a dog pooped in this picture? Where?"
STEP_Q = "Is there anything on the ground I should avoid stepping in?"
# Annotation names that mean the picture is unsure (something that may be poop, or left over from it): a picture with
# one of them is not used at all. A picture with anything else outlined (a leaf, a pine cone) is not used for "No".
SCAT_UNSURE = {"unknown", "ignore", "residue", "yellowsnow"}


def scat_splits(s):
    """The newest train and validation kwcoco files (images, annotations, categories) from kwcoco_splits.zip: the
    images whose poop has been outlined, so a picture with no outline there has no poop."""
    outer = zipfile.ZipFile(io.BytesIO(s.get(SCAT_REPO + "kwcoco_splits.zip", timeout=300).content))
    chosen = {}
    for name in outer.namelist():
        m = re.search(r"/(train|vali)_imgs(\d+)_\w+\.kwcoco\.zip$", "/" + name)
        if m and "simplified" not in name and int(m.group(2)) > chosen.get(m.group(1), ("", 0))[1]:
            chosen[m.group(1)] = (name, int(m.group(2)))
    out = []
    for name, _ in chosen.values():
        inner = zipfile.ZipFile(io.BytesIO(outer.read(name)))
        out.append(json.loads(inner.read(inner.namelist()[0])))
    return out


def scat_answers(piles, width, height):
    """(the "Where?" answer, the "avoid stepping" answer) for one picture from its piles' boxes [x, y, w, h]."""
    if not piles:
        return ("No: I can't see any dog poop in this picture.",
                "I can't see any dog poop or anything else to avoid on the ground in this picture.")
    piles = sorted(piles, key=lambda b: -b[2] * b[3])
    places = [spot((x + w / 2) / width, (y + h / 2) / height) for x, y, w, h in piles]
    if len(piles) == 1:
        x, y, w, h = piles[0]
        where_text = f"there is {size_word(w * h / (width * height))} of dog poop on the ground, {places[0]}"
        return f"Yes: {where_text}.", f"Yes: {where_text}. Step around it."
    counts = {}
    for p in places:                                  # the biggest pile's place first
        counts[p] = counts.get(p, 0) + 1
    n = number_word(len(piles))
    if len(counts) == 1:
        text = f"there are {n} piles of dog poop on the ground, all {places[0]}"
    else:
        detail = listed([f"{number_word(k)} {p}" for p, k in counts.items()])
        text = f"there are {n} piles of dog poop on the ground: {detail}"
    return f"Yes: {text}.", f"Yes: {text}. Step around them."


def scat_place(image):
    """{"place": country} from a photo's own coordinates (kwcoco "geos_point", longitude first, as fractions)."""
    from fractions import Fraction
    try:
        lon, lat = [float(Fraction(str(v))) for v in image["geos_point"]["coordinates"]]     # "-26556071/360000"
        return where(country_at(lat, lon))
    except Exception:  # noqa: BLE001 - no place
        return {}


def build_scatspotter(limit):
    """The ScatSpotter pack: [(name, JPEG, row)]. Reads the train and validation lists (pictures in their camera's
    own orientation only, so the outlines match), then: every picture with outlined poop gives the "Where?" and
    "avoid stepping" rows; pictures with nothing outlined, taken within five minutes after a picture with poop in the
    same batch (the "after" photo once the poop was picked up, and the nearby "negative" photo), give the "No" rows.
    About two pictures with poop for each without. The pictures are read one by one out of the batch zips."""
    s = session()
    images, outlined, unsure = {}, {}, set()
    for data in scat_splits(s):
        names = {c["id"]: c["name"] for c in data["categories"]}
        for image in data["images"]:
            if image.get("exif_ori") == 1 and image.get("width") and image.get("file_name", "").startswith("assets/"):
                images[image["file_name"]] = image
        ids = {image["id"]: image["file_name"] for image in data["images"]}
        for a in data["annotations"]:
            name, file_name = names.get(a["category_id"], ""), ids.get(a["image_id"])
            if name == "poop" and a.get("bbox"):
                outlined.setdefault(file_name, []).append(a["bbox"])
            elif name != "poop":                    # something else outlined (a leaf, a pine cone, "unknown")
                unsure.add((file_name, name))
    skip = {f for f, n in unsure if n in SCAT_UNSURE}
    other = {f for f, _ in unsure}
    positives = [f for f in images if f in outlined and f not in skip]
    # Pictures without poop: in the same batch, within five minutes after a picture with poop.
    by_batch = {}
    for f, image in images.items():
        by_batch.setdefault(image.get("cohort"), []).append((image.get("datetime") or "", f))
    negatives = []
    for batch in by_batch.values():
        batch.sort()
        last_with = None
        for stamp, f in batch:
            if f in outlined:
                last_with = stamp
            elif last_with and f not in other and stamp[:10] == last_with[:10] and stamp > last_with \
                    and _minutes(last_with, stamp) <= 5:
                negatives.append(f)
    say(f"ScatSpotter: {len(positives)} pictures with dog poop outlined, {len(negatives)} 'after' pictures without")
    rng = random.Random(61)
    rng.shuffle(positives)
    rng.shuffle(negatives)
    want_neg = max(1, limit // 3)
    chosen = positives[:limit - min(want_neg, len(negatives))] + negatives[:want_neg]
    chosen = chosen[:int(limit * 1.05) + 2]
    by_zip = {}
    for f in chosen:
        by_zip.setdefault(f.split("/")[1], []).append(f)
    out = []
    for batch, files in sorted(by_zip.items()):
        try:
            zipped = RemoteZip(SCAT_REPO + f"assets/{batch}.zip")
            where_in = {name: (offset, csize, method) for name, offset, csize, method in zipped.entries()}
        except Exception as e:  # noqa: BLE001 - next batch
            say(f"  ScatSpotter batch {batch} could not be read ({str(e)[:100]})")
            continue
        items = []
        for f in files:
            inner = f.split("/", 1)[1]
            if inner not in where_in:
                continue
            image = images[f]
            where_text, step = scat_answers(outlined.get(f, []), image["width"], image["height"])
            extra = {"credit": SCAT_CREDIT, **scat_place(image)}
            rows = [dict({"question": DOG_Q, "answer": where_text}, **extra),
                    dict({"question": STEP_Q, "answer": step}, **extra)]
            items.append((f"scat-{safe_name(image.get('name') or inner)}.jpg", where_in[inner], rows))
        out += fetch_from_zip(zipped, items, workers=4)
        say(f"  ScatSpotter: {len(out)} pictures read so far")
        if len(out) >= limit:
            break
    rng.shuffle(out)
    return with_twins(out[:limit])


def _minutes(a, b):
    """Minutes from time stamp a to b ("2023-02-11T16:19:48"); a large number when they cannot be read."""
    import datetime
    try:
        return (datetime.datetime.fromisoformat(b[:19]) - datetime.datetime.fromisoformat(a[:19])).total_seconds() / 60
    except ValueError:
        return 10 ** 6


# ----------------------------------------------------------------- iNaturalist droppings ("Evidence of presence: Scat")

INAT = "https://api.inaturalist.org/v1/"
INAT_FREE = ("cc0", "cc-by")
# The animals, by scientific name, with the plain words for their droppings, whether every observation counts (the
# animal lives with people, so the observer's own name for it is used, "casual" ones too) or only research-grade ones,
# and how many pictures each may give at most (a share of the limit).
INAT_ANIMALS = [
    ("Canis familiaris", "dog poop", "a domestic dog", True, 0.25),
    ("Felis catus", "cat poop", "a domestic cat", True, 0.08),
    ("Equus caballus", "horse manure (horse droppings)", "a horse", True, 0.08),
    ("Equus asinus", "donkey droppings", "a donkey", True, 0.02),
    ("Bos taurus", "a cow pat (cow dung)", "a cow", True, 0.06),
    ("Ovis aries", "sheep droppings", "a sheep", True, 0.03),
    ("Capra hircus", "goat droppings", "a goat", True, 0.02),
    ("Branta canadensis", "goose droppings", "a Canada goose", False, 0.05),
    ("Columba livia", "pigeon droppings", "a pigeon", False, 0.03),
    ("Vulpes vulpes", "fox droppings (fox scat)", "a red fox", False, 0.05),
    ("Procyon lotor", "raccoon droppings", "a raccoon", False, 0.04),
    ("Odocoileus virginianus", "deer droppings", "a white-tailed deer", False, 0.04),
    ("Capreolus capreolus", "deer droppings", "a roe deer", False, 0.02),
    ("Oryctolagus cuniculus", "rabbit droppings", "a rabbit", False, 0.03),
    ("Sylvilagus floridanus", "rabbit droppings", "an eastern cottontail rabbit", False, 0.02),
    ("Erinaceus europaeus", "hedgehog droppings", "a hedgehog", False, 0.02),
    ("Aves", "bird droppings", "a bird", False, 0.14),
]
INAT_SINGULAR = {"dog poop", "cat poop", "horse manure (horse droppings)", "a cow pat (cow dung)"}
WHAT_Q = "What is this?"
WHO_Q = "What animal left these droppings?"


def inat_taxon(s, name):
    """The iNaturalist taxon id of a scientific name (exact match), or None."""
    try:
        for t in s.get(INAT + "taxa", params={"q": name, "per_page": 10}, timeout=60).json().get("results", []):
            if t.get("name", "").lower() == name.lower():
                return t["id"]
    except Exception:  # noqa: BLE001 - left out
        pass
    return None


def inat_scat(s, taxon, grades, want, licences=INAT_FREE):
    """Observations of a taxon marked as scat whose first photo's own licence is one of licences, up to want."""
    out, page = [], 1
    while len(out) < want and page <= 20:
        try:
            data = s.get(INAT + "observations", timeout=60, params={
                "taxon_id": taxon, "term_id": 22, "term_value_id": 25, "photo_license": ",".join(licences),
                "quality_grade": grades, "per_page": 200, "page": page, "order_by": "votes"}).json()
        except Exception:  # noqa: BLE001 - what was found
            break
        results = data.get("results") or []
        for o in results:
            photos = o.get("photos") or []
            if photos and (photos[0].get("license_code") or "") in licences:
                out.append(o)
        if len(results) < 200:
            break
        page += 1
        time.sleep(1.1)                      # iNaturalist asks for at most about one request a second
    return out[:want]


def inat_rows(o, words, animal, licence_names=None):
    """The rows for one scat observation: what it is, and (for research-grade or domestic ones) which animal, with
    the species named for wild birds."""
    taxon = o.get("taxon") or {}
    common, latin = clean(taxon.get("preferred_common_name")), taxon.get("name", "")
    if words == "bird droppings" and o.get("quality_grade") == "research" and common and latin != "Aves":
        animal = f"{article(common)} {common} ({latin})"
    elif latin and words != "bird droppings" and " " in latin:
        animal = f"{animal} ({latin})"
    photo = o["photos"][0]
    login = (o.get("user") or {}).get("login", "an iNaturalist user")
    licence = (licence_names or {}).get(photo["license_code"], photo["license_code"].upper())
    credit = f"Photo by {login} on iNaturalist, {licence}, https://www.inaturalist.org/observations/{o['id']}"
    lead = "This is" if words in INAT_SINGULAR else "These are"
    rows = [{"question": WHAT_Q, "answer": f"{lead} {words}, left by {animal}."},
            {"question": WHO_Q, "answer": f"They look like droppings left by {animal}."}]
    return plain_rows(rows, credit=credit, **inat_place(o))


def build_inat_droppings(limit):
    """The iNaturalist droppings pack: [(name, JPEG, row)] from scat observations of the animals in INAT_ANIMALS,
    each observation's first photo (iNaturalist's "large" copy) under CC0 or CC BY."""
    s, items = session(), []
    for latin, words, animal, domestic, share in INAT_ANIMALS:
        taxon = inat_taxon(s, latin)
        if not taxon:
            say(f"iNaturalist: {latin} not found")
            continue
        grades = "research,needs_id,casual" if domestic else "research"
        found = inat_scat(s, taxon, grades, max(3, int(limit * share * 1.2)))
        # Dingoes are filed under Canis familiaris on iNaturalist; they are wild, not pets.
        found = [o for o in found if "dingo" not in ((o.get("taxon") or {}).get("name") or "").lower()]
        for o in found:
            photo = o["photos"][0]
            items.append((f"inatscat-{photo['id']}.jpg", photo["url"].replace("/square.", "/large."),
                          inat_rows(o, words, animal)))
        say(f"iNaturalist droppings of {latin}: {len(found)}")
        time.sleep(1.1)
    random.Random(62).shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.3)[:limit])


# ----------------------------------------------------------------- Open Images V7: blood, injuries, poop, litter boxes

OI_TRAIN_LABELS = "https://storage.googleapis.com/openimages/v7/oidv7-train-annotations-human-imagelabels.csv"
OI_ALL_LABELS = (OI_TRAIN_LABELS, "https://storage.googleapis.com/openimages/v7/oidv7-val-annotations-human-imagelabels"
                                  ".csv", "https://storage.googleapis.com/openimages/v7/oidv7-test-annotations-human-"
                                          "imagelabels.csv")
OI_ALL_IMAGES = ("https://storage.googleapis.com/openimages/v6/oidv6-train-images-with-labels-with-rotation.csv",
                 "https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv",
                 "https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv")
# Each label with its question and the answers for "people confirmed it" and "people checked: not there".
OI_BODILY = {
    "Blood": ("Is there blood in this picture?", "Yes, there is blood in this picture.",
              "No, I can't see any blood in this picture."),
    "Injury": ("Is there an injury in this picture?", "Yes: it shows an injury (a wound).",
               "No, I can't see an injury in this picture."),
    "Bandage": ("Is there a bandage in this picture?", "Yes, there is a bandage.", "No, I can't see a bandage."),
    "Band-aid": ("Is there a sticking plaster in this picture?", "Yes, there is a sticking plaster (a Band-Aid).",
                 "No, I can't see a sticking plaster."),
    "Feces": ("Is there any poop in this picture?", "Yes, there is poop (faeces) in this picture.",
              "No, I can't see any poop in this picture."),
    "Litter box": ("Is there a cat litter box in this picture?", "Yes, there is a cat litter box (litter tray).",
                   "No, I can't see a cat litter box."),
    "Cat litter": ("Is there cat litter in this picture?", "Yes, there is cat litter.", "No, I can't see cat litter."),
    "Stain": ("Is there a stain in this picture?", "Yes, there is a stain.", "No, I can't see a stain."),
}
OI_MEDICAL = {"Blood", "Injury"}             # a photo with one of these confirmed is human medical material
# Labels that leave a photo out: children (expression_packs.OI_CHILD), and costumes and horror (fake blood).
OI_LEAVE_OUT = set(OI_CHILD) | {"Halloween", "Costume", "Zombie", "Cosplay", "Fictional character", "Horror",
                                "Nudity", "Swimwear", "Undergarment", "Brassiere", "Lingerie"}


def oi_label_lines(s, mids, leave_mids):
    """{image id: {label name: 1 or 0}} for the bodily labels, and the set of images with a leave-out label confirmed,
    from the train, validation and test lists (about 2.8 GB, read as it downloads)."""
    labels, leave = {}, set()
    for url in OI_ALL_LABELS:
        for cells in csv.reader(oi_lines(s, url)):
            if len(cells) != 4:
                continue
            if cells[2] in leave_mids:
                if cells[3].startswith("1"):
                    leave.add(cells[0])
            elif cells[2] in mids:
                try:
                    value = round(float(cells[3]))
                except ValueError:
                    continue
                labels.setdefault(cells[0], {})[mids[cells[2]]] = value
        say(f"  Open Images: {len(labels)} photos with a bodily label after {url.rsplit('/', 1)[-1]}")
    return labels, leave


def build_open_images_bodily(limit):
    """The Open Images bodily pack: [(name, JPEG or None, row)]. Every photo with a bodily label confirmed comes
    first, then about as many with only "not there" checks (the "No" answers); photos with a child, a costume or
    nudity label confirmed are left out, as are photos whose own licence is not CC BY or that need turning."""
    s = session()
    names = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            names.setdefault(line[1], line[0])
    mids = {names[n]: n for n in OI_BODILY if n in names}
    leave_mids = {names[n] for n in OI_LEAVE_OUT if n in names}
    labels, leave = oi_label_lines(s, mids, leave_mids)
    wanted = {i for i in labels if i not in leave}
    photos = {}
    for url in OI_ALL_IMAGES:
        subset = "train" if "train" in url else "validation" if "validation" in url else "test"
        for r in csv.DictReader(oi_lines(s, url)):
            if r["ImageID"] in wanted:
                licence = oi_licence_name(r.get("License") or "")
                if licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                    photos[r["ImageID"]] = (subset, licence, clean(r.get("Author")) or "an unnamed photographer",
                                            r.get("OriginalLandingURL") or "")
    yes, no = [], []
    for image_id, found in labels.items():
        if image_id not in photos:
            continue
        subset, licence, author, page = photos[image_id]
        credit = (f"Photo by {author}" + (f" ({page})" if page else "") + f", {licence}; labels from Open Images V7 "
                  f"(Google), CC BY 4.0")
        medical = any(found.get(n) == 1 for n in OI_MEDICAL)
        rows = []
        for label, value in found.items():
            question, said_yes, said_no = OI_BODILY[label]
            rows.append({"question": question, "answer": said_yes if value == 1 else said_no, "credit": credit,
                         **(MEDICAL if medical else {})})
        item = (f"oibody-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id), rows)
        (yes if any(v == 1 for v in found.values()) else no).append(item)
    say(f"Open Images: {len(yes)} usable photos with a bodily label confirmed, {len(no)} with only 'not there'")
    random.Random(63).shuffle(yes)
    random.Random(64).shuffle(no)
    chosen = yes[:int(limit * 0.6) + 1]
    chosen += no[:int(limit * 1.1) + 2 - len(chosen)]
    return with_twins(fetch_all(chosen, workers=8)[:limit])


# ----------------------------------------------------------------- Wikimedia Commons categories

# Each category: (question, answer, whether its human material is medical, whether a picture may show a person's body
# and so needs the file's words to say the person is an adult, whether one level of subcategories is used too).
COMMONS_BODILY = {
    "Human feces": ("What is this?", "This is human poop (stool). " + STOOL_ADVICE, True, False, False),
    "Melena": ("What does this stool look like?", "It is black and tarry: this can be a sign of bleeding in the gut "
                                                  "(melena). " + STOOL_ADVICE, True, False, False),
    "Bristol Stool Chart": ("What does this chart show?",
                            "This is the Bristol Stool Form Scale: a chart of seven types of stool, from type 1 "
                            "(separate hard lumps, like nuts) to type 7 (entirely liquid, no solid pieces). Types 3 "
                            "and 4 are the usual, healthy kinds.", True, False, False),
    "Vomit": ("What is this?", "This is vomit. " + VOMIT_ADVICE, True, False, False),
    "Urine": ("What is this?", "This is urine. " + URINE_ADVICE, True, False, False),
    "Urine color charts": ("What does this chart show?",
                           "This is a urine colour chart: it shows shades from pale yellow (drinking enough) to dark "
                           "yellow or amber (drink more water). " + URINE_ADVICE, True, False, False),
    "Hematuria": ("What does this urine look like?", "It is red or pink: it may have blood in it (haematuria). " +
                  URINE_ADVICE, True, False, False),
    "Blood stains": ("What is this stain?", "It looks like a blood stain.", True, False, True),
    "Epistaxis": ("What is happening here?", "This is a nosebleed: blood is coming from the nose. " + BLOOD_ADVICE,
                  True, True, False),
    "Dog feces": ("What is this?", "This is dog poop.", False, False, True),
    "Cat feces": ("What is this?", "This is cat poop.", False, False, False),
    "Horse dung": ("What is this?", "This is horse manure (horse droppings).", False, False, True),
    "Cow dung": ("What is this?", "This is cow dung (a cow pat).", False, False, True),
    "Bird droppings": ("What is this?", "These are bird droppings.", False, False, True),
    "Litter boxes": ("What is this?", "This is a cat litter box (litter tray).", False, False, False),
}
# Words that mean a picture is not a photograph of the thing (art, signs, products), or is not wanted.
COMMONS_NOT_THIS = re.compile(r"\b(art|drawings?|paintings?|logos?|icons?|emoji|sculptures?|toys?|models?|"
                              r"in literature|videos?|audio|microscop\w*|micrograph\w*|beetles?|insects?|fossil\w*|"
                              r"coprolites?|fuel|briquett\w*|paper|museum|caricatur\w*|cartoons?|signs?)\b", re.I)
ADULT_WORDS = re.compile(r"\b(man|woman|men|women|adults?|gentleman|lady|myself|my nose|\d{2}[- ]year[- ]old)\b",
                         re.I)


def commons_category_items(s, category, deeper, per_category, seen):
    """[(title, url, credit, text)] for up to per_category free files of a category (and one level of its
    subcategories when deeper), leaving out art, signs and the like."""
    titles = commons_members(s, category, "file")
    if deeper:
        for sub in commons_members(s, category, "subcat"):
            if not COMMONS_NOT_THIS.search(sub):
                titles += commons_members(s, sub.split(":", 1)[-1], "file")
    titles = [t for t in dict.fromkeys(titles) if t not in seen and not COMMONS_NOT_THIS.search(t)]
    random.Random(category).shuffle(titles)
    return commons_entries(s, titles[:per_category * 3]), len(titles)


def build_commons_bodily(limit):
    """The Commons bodily pack: [(name, JPEG, row)]. For each category of COMMONS_BODILY: its free files (CC0,
    public domain or CC BY), with the category's question and answer and, when the file has a real caption or
    description, "Write a short description ...". Pictures that may show a person's body are kept only when the
    file's words say the person is an adult and name no child; anything whose words are about nudity or intimate
    areas is left out; rows whose words name a child are marked "child"."""
    s, items, seen = session(), [], set()
    per_category = max(8, limit // len(COMMONS_BODILY) * 2)
    for category, (question, answer, medical, body, deeper) in COMMONS_BODILY.items():
        try:
            entries, total = commons_category_items(s, category, deeper, per_category, seen)
        except Exception as e:  # noqa: BLE001 - next category
            say(f"Commons {category}: could not be read ({str(e)[:100]})")
            continue
        found = 0
        for title, url, credit, text in entries:
            words = f"{title} {text}"
            if GENITAL_AREA.search(words) or (body and (not ADULT_WORDS.search(words) or CHILD.search(words))):
                continue
            seen.add(title)
            extra = {"credit": credit, **commons_place(title), **(MEDICAL if medical else {}),
                     **({"child": True} if CHILD_WORDS.search(words) else {})}
            rows = [dict({"question": question, "answer": answer}, **extra)]
            if text:
                rows.append(dict({"question": ALT_TEXT, "answer": text}, **extra))
            items.append((f"commons-body-{safe_name(title.split(':', 1)[-1].rsplit('.', 1)[0])}.jpg", url, rows))
            found += 1
            if found >= per_category:
                break
        say(f"Commons {category}: {found} free pictures ({total} files)")
    random.Random(65).shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)[:limit])


# ----------------------------------------------------------------- PubMed Central case reports

FIG_TERMS = ("stool", "stools", "feces", "faeces", "melena", "melaena", "hematochezia", "haematochezia",
             "vomit", "vomitus", "hematemesis", "haematemesis", "coffee-ground", "urine", "hematuria", "haematuria",
             "chromaturia", "epistaxis", "diarrhea", "diarrhoea", "diaper", "nappy")
FIG_QUERY = " OR ".join(f'FIG:"{t}"' for t in FIG_TERMS)
CASE_QUERY = f'IN_PMC:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND (PUB_TYPE:"Case Reports" OR TITLE:"case") ' \
             f'AND ({FIG_QUERY})'
VET_CASE_QUERY = CASE_QUERY + ' AND (TITLE:dog OR TITLE:dogs OR TITLE:canine OR TITLE:puppy OR TITLE:cat OR ' \
                              'TITLE:cats OR TITLE:feline OR TITLE:kitten OR TITLE:rabbit OR TITLE:horse OR ' \
                              'TITLE:equine OR TITLE:pony)'
# What the photo is of, from the caption: the first that matches, with the advice for people.
SUBSTANCES = [
    (re.compile(r"\b(vomit\w*|hae?matemesis|emesis|coffee[- ]ground\w*)\b", re.I), "vomit", VOMIT_ADVICE),
    (re.compile(r"\b(stools?|fa?eces|fa?ecal|mel(a)?ena|hae?matochezia|diarrh(o)?ea\w*|bowel movement\w*|"
                r"diapers?|napp(y|ies))\b", re.I), "stool", STOOL_ADVICE),
    (re.compile(r"\b(urine|urinary (bag|catheter bag)|hae?maturia|chromaturia)\b", re.I), "urine", URINE_ADVICE),
    (re.compile(r"\b(epistaxis|nosebleed\w*|nose ?bleed\w*)\b", re.I), "nosebleed", BLOOD_ADVICE),
]
# Captions of pictures that are not plain photographs (scans, endoscopy, microscope, charts); "blood-stained" and
# "stained with blood" are not the microscope's "stained".
NOT_A_PHOTO = re.compile(r"\b(CT|MRI|PET|computed tomograph\w*|magnetic resonance|x-?rays?|radiograph\w*|ultrasound|"
                         r"sonograph\w*|echocardiogra\w*|angiogra\w*|endoscop\w*|colonoscop\w*|gastroscop\w*|"
                         r"cystoscop\w*|EGD|sigmoidoscop\w*|capsule endoscop\w*|histolog\w*|histopatholog\w*|"
                         r"H&E|hae?matoxylin|immunohistochem\w*|microscop\w*|micrograph\w*|magnification|"
                         r"cytolog\w*|smear|gram stain\w*|cultures?|colon(ies|y)|agar|electrophoresis|"
                         r"chromatogra\w*|spectr\w*|graph|chart|curve|timeline|flow ?chart|diagram|schematic|"
                         r"table|algorithm|sequenc\w*|eggs? of|ova|oocysts?|larva\w*|parasites? (seen|found)|"
                         r"\d{2,4} ?[x×]|[x×] ?\d{2,4})\b", re.I)
# A caption that names a part of the body: for a child's report, the picture may show the child, so it is left out.
BODY_PART = re.compile(r"\b(face|facial|head|scalp|eyes?|nose|mouth|lips?|neck|chest|abdomen|abdominal|belly|"
                       r"stomach wall|back|arms?|hands?|fingers?|legs?|feet|foot|toes?|skin|body|patient|infant's|"
                       r"child's|baby's|boy's|girl's|bottom|perine\w*|gluteal)\b", re.I)


def substance_of(caption):
    """(substance, advice) for a caption about stool, vomit, urine or a nosebleed, or None."""
    return next(((name, advice) for pattern, name, advice in SUBSTANCES if pattern.search(caption)), None)


def bodily_figures(query, want, vet, prefix):
    """(name, picture address, row) for one-picture photographs of stool, vomit, urine or a nosebleed in case reports
    a Europe PMC query finds, licence checked in PMC's own metadata (CC BY or CC0). People: articles about adults
    (age 18 or more, no child named), or about a child when the caption is about the substance and names no part of
    the body (marked "child"). Animals: dogs, cats, rabbits and horses."""
    s = session()
    records = europe_pmc(s, query, want * 4)
    say(f"Europe PMC: {len(records)} case reports with a matching figure caption")
    random.Random(prefix).shuffle(records)

    def one(record):
        """The usable figures of one article ([] when none)."""
        text = f"{record.get('title', '')} {record.get('abstractText', '')}"
        about_child = False
        if vet:
            who = animal_of(record.get("title"))
            if who == "an animal":
                return []
        else:
            ok, age = adult_only(text)
            if ok:
                m = re.search(rf"\b{age}[- ](?:year|yr)s?[- ]old\s+(\w+)", clean(text), re.I)
                who = who_with_age(age, sex_of(m.group(1) if m else ""))
            elif CHILD.search(text):
                who, about_child = "a child", True
            else:
                return []
        meta, xml = pmc_article(s, record["pmcid"])
        if not meta or meta.get("license_code") not in PMC_FREE or meta.get("is_retracted"):
            return []
        out = []
        for label, caption, url in pmc_figures(xml, meta):
            words = len(caption.split())
            found = substance_of(caption)
            if not found or words < 5 or words > 100 or MULTI_PANEL.search(caption) or NOT_A_PHOTO.search(caption):
                continue
            if GENITAL_AREA.search(caption) or (about_child and BODY_PART.search(caption)):
                continue
            if not vet and not about_child and CHILD.search(caption):
                continue
            substance, advice = found
            if vet:
                advice = PET_ADVICE
            licence = PMC_FREE[meta["license_code"]]
            authors = clean(record.get("authorString"))
            if len(authors) > 120:
                authors = authors[:authors.rfind(",", 0, 120)] + " et al."
            credit = f"{authors}, \"{clean(record.get('title')).rstrip('.')}\", {clean(meta.get('citation'))}, " \
                     f"{label or 'figure'}, {licence}, https://pmc.ncbi.nlm.nih.gov/articles/{meta['pmcid']}/"
            caption = caption if caption.endswith((".", "!", "?")) else caption + "."
            row = {"question": "What does this picture show?", "credit": credit,
                   "answer": f"This is a photograph from a published case report about {who}. The authors' "
                             f"caption says: {caption} {advice}"}
            if not vet:
                row.update(MEDICAL)
            if about_child:
                row["child"] = True
            out.append((f"{prefix}-{meta['pmcid']}-{safe_name(label or url.rsplit('/', 1)[-1])}.jpg", url, row))
        return out[:2]                                     # at most two figures of one article

    items = []
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for start in range(0, len(records), 200):
            for got in pool.map(one, records[start:start + 200]):
                items += got
            say(f"  {min(start + 200, len(records))} articles read, {len(items)} usable figures")
            if len(items) >= want:
                break
    return items[:want]


def build_case_report_bodily(limit):
    """The case_report_bodily pack: [(name, JPEG, row)] from human case reports (CC BY or CC0)."""
    items = bodily_figures(CASE_QUERY, int(limit * 1.1) + 2, False, "pmcbody")
    return fetch_all(items, workers=4, pause=0.1)[:limit]


def build_vet_case_bodily(limit):
    """The vet_case_bodily pack: [(name, JPEG, row)] from veterinary case reports about pets (CC BY or CC0)."""
    items = bodily_figures(VET_CASE_QUERY, int(limit * 1.1) + 2, True, "pmcpet")
    return fetch_all(items, workers=4, pause=0.1)[:limit]


# ----------------------------------------------------------------- urine samples (celesca/urine-detector)

URINE_REPO = "celesca/urine-detector"
URINE_BASE = f"https://huggingface.co/datasets/{URINE_REPO}/resolve/main/"
URINE_CREDIT = "urine-detector dataset (celesca on Hugging Face), Apache-2.0, " \
               "https://huggingface.co/datasets/celesca/urine-detector"
URINE_Q = "What colour is this urine?"
URINE_CLEAR_Q = "Is this urine clear or cloudy?"
URINE_TURBIDITY = {"clear": "It is clear.", "slightly cloudy": "It is slightly cloudy.", "cloudy": "It is cloudy.",
                   "turbid": "It is cloudy (turbid)."}


def urine_colour(r, g, b):
    """(plain colour words, what the colour can mean) for the urine colour its makers measured on a photo (0-255)."""
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    h *= 360
    if s < 0.12:
        return "almost colourless, like water", "Very pale urine usually means you are drinking plenty."
    if h < 20 or h >= 330:
        return ("dark red or brown" if v < 0.45 else "red or pink"), \
            "Red, pink or brown urine can be a sign of blood in the urine."
    if h < 35:
        return ("brown" if v < 0.4 else "amber (orange-brown)" if v < 0.65 else "orange"), \
            "Amber or brown urine often means you need to drink more water."
    if h < 70:
        if s < 0.35:
            return "pale yellow", "Pale yellow is the usual colour when you drink enough."
        if s < 0.62:
            return "yellow", "Yellow is a usual urine colour."
        return "dark yellow", "Dark yellow urine can mean you need to drink more water."
    if h < 170:
        return "greenish", "Green urine is unusual; some foods and medicines cause it."
    return "bluish or purple", "Blue or purple urine is unusual; some medicines and infections cause it."


def xlsx_sheets(data, wanted):
    """{sheet name: [row as a list of cell texts]} for the sheets named in wanted (names compared without spaces at
    the ends) of an .xlsx file, read with the standard library: the values Excel last saved (formulas' results)."""
    import xml.etree.ElementTree as ET
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    book = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in book.namelist():
        for si in ET.fromstring(book.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t")))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))}
    out = {}
    for sheet in ET.fromstring(book.read("xl/workbook.xml")).find("m:sheets", ns):
        name = sheet.get("name", "").strip()
        if name not in wanted:
            continue
        target = rels[sheet.get(f"{{{ns['r']}}}id")].lstrip("/")
        path = target if target.startswith("xl/") else "xl/" + target
        rows = []
        for row in ET.fromstring(book.read(path)).iter(f"{{{ns['m']}}}row"):
            cells = {}
            for c in row.findall("m:c", ns):
                column = re.match(r"[A-Z]+", c.get("r", "A")).group(0)
                index = 0
                for ch in column:
                    index = index * 26 + ord(ch) - 64
                v = c.find("m:v", ns)
                text = (v.text or "") if v is not None else "".join(t.text or "" for t in c.iter(f"{{{ns['m']}}}t"))
                if c.get("t") == "s" and text.isdigit():
                    text = shared[int(text)]
                cells[index - 1] = text
            rows.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
        out[name] = rows
    return out


def urine_table():
    """({photo file name: (r, g, b)}, {sample number: turbidity}) from the dataset's spreadsheet: the "AI Training"
    sheet holds the colour measured on every photo, the "Database" sheet the laboratory's turbidity of each sample."""
    sheets = xlsx_sheets(session().get(URINE_BASE + "urine_data.xlsx", timeout=300).content,
                         {"AI Training", "Database"})
    colours, turbidity = {}, {}
    for r in sheets.get("AI Training", [])[1:]:
        try:
            colours[r[0].strip()] = tuple(int(float(x)) for x in r[2:5])
        except (ValueError, IndexError):
            continue
    for r in sheets.get("Database", [])[2:]:
        if len(r) > 8 and r[1].strip() and r[8].strip():
            turbidity.setdefault(r[1].strip().zfill(3), clean(r[8]).lower())
    return colours, turbidity


def build_urine_samples(limit):
    """The urine samples pack: [(name, JPEG or None, row)]. For each sample, the front photos (position F) of up to
    two of the four phones, each with the colour its makers measured on that photo and the sample's turbidity. The
    photos are HEIC files (named .jpg), read with pillow-heif."""
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        say("Urine samples: pillow-heif is not installed, so the HEIC photos cannot be read; the pack is empty.")
        return []
    colours, turbidity = urine_table()
    by_sample = {}
    for name in colours:
        m = re.match(r"(\d{3})_(.+)_F\d\.jpe?g$", name, re.I)
        if m:
            by_sample.setdefault(m.group(1), []).append(name)
    rng, items = random.Random(66), []
    for sample, names in sorted(by_sample.items()):
        rng.shuffle(names)
        for name in names[:2]:
            words, meaning = urine_colour(*colours[name])
            rows = [{"question": URINE_Q, "answer": f"This is a urine sample in a clear pot. It is {words}. "
                                                    f"{meaning} {URINE_ADVICE}"}]
            cloud = turbidity.get(sample)
            if cloud in URINE_TURBIDITY:
                extra = " Cloudy urine can have many causes; if it stays cloudy, or comes with pain or fever, " \
                        "contact a doctor." if cloud != "clear" else ""
                rows.append({"question": URINE_CLEAR_Q, "answer": URINE_TURBIDITY[cloud] + extra})
            rows = plain_rows(rows, credit=URINE_CREDIT, place="Thailand", **MEDICAL)
            items.append((f"urine-{safe_name(name.rsplit('.', 1)[0])}.jpg",
                          URINE_BASE + f"AI/{sample}/{name.replace(' ', '%20')}", rows))
    say(f"Urine samples: {len(by_sample)} samples, {len(items)} photos chosen")
    rng.shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.05) + 2], workers=4)[:limit])


# ----------------------------------------------------------------- the packs

BODILY_PACKS = {
    "scatspotter": (build_scatspotter,
                    "ScatSpotter / ShitSpotter dataset (Jon Crall, Kitware; 'ScatSpotter: A Dog Poop Detection "
                    "Dataset', WACV Workshops 2026, https://arxiv.org/abs/2412.16473), data CC BY 4.0 "
                    "(https://creativecommons.org/licenses/by/4.0/), https://github.com/Erotemic/shitspotter, read "
                    "from https://huggingface.co/datasets/erotemic/shitspotter. Photos made smaller; answers written "
                    "from the hand-drawn outlines."),
    "inat_droppings": (build_inat_droppings,
                       "iNaturalist observations marked 'Evidence of presence: Scat', https://www.inaturalist.org: "
                       "photos CC0 or CC BY (each photo's own licence checked), each credited below with its "
                       "photographer and observation."),
    "open_images_bodily": (build_open_images_bodily,
                           "Open Images V7 (Google): image-level labels verified by people, CC BY 4.0, "
                           "https://storage.googleapis.com/openimages/web/index.html. Each photo is CC BY 2.0 (checked "
                           "photo by photo), credited below with its photographer and Flickr page."),
    "commons_bodily": (build_commons_bodily,
                       "Wikimedia Commons categories of stool, vomit, urine, blood and animal droppings: captions "
                       "CC0; pictures CC0, public domain or CC BY, each with its author and file page below. "
                       "https://commons.wikimedia.org"),
    "case_report_bodily": (build_case_report_bodily,
                           "Figures from case reports in PubMed Central (https://pmc.ncbi.nlm.nih.gov), each article's "
                           "licence checked in PMC's open-access metadata: CC BY or CC0 only, each figure credited "
                           "below with its authors, article and licence. Photographs of stool, vomit, urine or a "
                           "nosebleed; adults, or a child's report when the photo shows only the stool, urine or "
                           "vomit. The captions are the authors' own."),
    "vet_case_bodily": (build_vet_case_bodily,
                        "Figures from veterinary case reports about dogs, cats, rabbits and horses in PubMed Central "
                        "(https://pmc.ncbi.nlm.nih.gov), each article's licence checked in PMC's open-access metadata: "
                        "CC BY or CC0 only, each figure credited below. The captions are the authors' own."),
    "urine_samples": (build_urine_samples,
                      "urine-detector (celesca on Hugging Face), Apache-2.0, "
                      "https://huggingface.co/datasets/celesca/urine-detector: urine samples photographed with four "
                      "phones in Thailand, with the colour measured on each photo and the laboratory's turbidity. "
                      "Photos converted from HEIC and made smaller; answers written from the dataset's own "
                      "measurements."),
}

# How many pictures a full build takes from each collection (about what each offers after the checks, November 2026).
BODILY_LIMITS = {
    "scatspotter": 3000,           # of about 3,100 pictures with poop and 1,500 'after' pictures (camera orientation)
    "inat_droppings": 2500,        # upper bound; the domestic animals give a few hundred, birds and wild ones more
    "open_images_bodily": 3000,    # about 900 photos with a label confirmed, the rest 'not there' checks
    "commons_bodily": 400,         # upper bound, not counted in full
    "case_report_bodily": 1500,    # upper bound; a few per cent of the matching articles have a usable photo
    "vet_case_bodily": 300,        # upper bound
    "urine_samples": 532,          # 266 samples, two phones' front photos each
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one bodily pack builder.")
    parser.add_argument("key", choices=sorted(BODILY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--brief", action="store_true", help="print only the questions and answers")
    args = parser.parse_args(argv)
    started = time.time()
    entries = BODILY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        if args.brief:
            say(f"{row['question']} -> {row['answer']}")
        else:
            say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, in {time.time() - started:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
