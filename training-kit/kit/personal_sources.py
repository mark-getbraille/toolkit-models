"""Personal-use collections for the Picture Model Training Kit: publicly downloadable collections whose licence or
terms allow non-commercial use only, or research and educational use only.

They are never in a ready-made pack and never re-shared by the kit's makers. Each one is downloaded by the kit on the
user's own computer, straight from the place its makers publish it, only when the user ticks the personal-use choice
(sources.py: --personal-noncommercial, and --personal-research with --accept-research-terms). An add-on trained with
any of them is for PERSONAL USE ONLY (sources.PERSONAL_WARNING).

Groups (Source.group):
  "noncommercial"  CC BY-NC, CC BY-NC-SA, or another licence that clearly allows personal, non-commercial use (a
                   copyleft licence such as GPL-3.0, or a custom licence such as SCIN's, is said so in its summary).
  "research"       terms that say research, academic or educational use only. The program shows each one's terms
                   (Source.terms, Source.terms_summary) before the user agrees.

Every entry here was checked at its source in November 2026 (the link is in Source.terms). Every entry can be
downloaded without signing up, logging in, filling in a form or signing an agreement. No words written by an AI model
are used: the answers are made with fixed sentences from each collection's own labels, or are people's own words.

Safety, as in packs/body_packs.py and packs/medical_packs.py:
  - Nothing sexual. Skin pictures of the genitals, groin, buttocks or breasts are left out (INTIMATE_SITE).
  - Medical collections (content "medical") use adults only (an age of 18 or more given in the data; ISIC's rounded
    ages from 20) and every answer ends with DOCTOR.
  - Everyday photos may show children, as in the open COCO collections; a row whose people's own words name a child is
    marked "child": true, so picture-making leaves it out (train_pictures.py).
  - Facial expressions: the answer gives the visible signs first (mouth, eyes, eyebrows), then a careful reading
    ("she seems to be ...", never a certainty about feelings), and says the expression was posed when it was.
  - People collections are never used for picture-making (PERSONAL_PICTURE_MAKING_OK holds only collections whose
    answers describe the whole photo and whose child rows are marked).

The collections (PERSONAL_SOURCES):
  noncommercial
    ham10000       HAM10000 skin spots (Harvard Dataverse, CC BY-NC 4.0); only the pictures used are read out of the
                   two zips (HTTP ranges), and their originals kept in the downloads folder.
    isic_nc        ISIC Archive skin spots whose own licence is CC BY-NC (the open isic_skin pack takes the CC0 and CC BY
                   ones); HAM10000's own pictures are left out here so nothing is learned twice.
    scin           SCIN (Google): skin problems photographed by adults with their phones, with what they reported and
                   dermatologists' labels (SCIN Data Use License: any use, but never trying to identify a person).
    coco_nc        COCO photos under non-commercial Flickr licences (the ones the open kit leaves out), with COCO's
                   one-sentence descriptions.
    vqav2_nc       VQA v2 questions on those photos (val2014 part).
    ln_coco_nc     Localized Narratives (spoken descriptions) on those photos.
    xfund          XFUND forms in seven languages (CC BY-NC-SA 4.0): the title and the filled-in fields.
    scienceqa      ScienceQA (CC BY-NC-SA 4.0): school science questions about diagrams, maps and photos, with the
                   explanation people wrote.
    chartqa        ChartQA (GPL-3.0, copyleft: treated as personal use): questions people wrote about real charts (only
                   the "human" part; its machine-made questions are left out).
  research
    food101        Food-101 (ETH Zurich): 101 dishes ("scientific fair use" only).
    stanford_dogs  Stanford Dogs: 120 dog breeds (ImageNet pictures: non-commercial research and education).
    fgvc_aircraft  FGVC-Aircraft: 100 aircraft models (non-commercial research only); the copyright strip at the bottom
                   of each photo is cut off, as its makers ask.
    funsd          FUNSD: noisy scanned forms (non-commercial, research and educational use).
    ai2d           AI2D: school science diagrams with multiple-choice questions (academic, non-profit research).
    jaffe          JAFFE: posed facial expressions of ten Japanese women (non-commercial scientific research).

Needing sign-up (not downloaded by the kit; the guide can mention them):
  Places365 (now a request form), ADE20K (account), SUN397 (download page gone), Flickr30k and Flickr30k Entities
  (request form; so also Localized Narratives on Flickr30k), DCI (its SA-1B pictures need Meta's licence agreement),
  Mapillary Vistas and Mapillary Traffic Signs (account), MIMIC and other PhysioNet sets (credentialed), DFU diabetic
  foot ulcers (registration and agreement), Derm7pt (registration), NABirds (form), Objects365 (Biendata account),
  RPC retail checkout (Kaggle login, or Baidu account), DocVQA, InfographicVQA and the ICDAR sets (RRC account),
  DeepFashion and DeepFashion-MultiModal (agreement), CompCars (agreement by email), ArtEmis (form), ImageNet and
  Cityscapes (accounts), Recipe1M (account), RAF-DB, AffectNet, Emotic, BoLD, KDEF, CK+, JAFFE's own site and Jester
  (request forms or agreements), FER2013 (Kaggle login; no mirror with stated terms).

Looked at and left out (see REJECTED for the reason of each).

Main parts: PERSONAL_SOURCES, PERSONAL_PICTURE_MAKING_OK, REJECTED, one prepare_<key>(source, data_dir, work, cap)
function per collection, and the helpers remote_zip (a zip on the web read piece by piece over HTTP) and
zip_members (training copies of chosen pictures in such a zip, keeping the originals).
"""

import ast
import concurrent.futures
import csv
import io
import json
import os
import random
import re
import tarfile
import threading
import time
import zipfile

import sources
from sources import (BRIEF, Source, USER_AGENT, clean, download_file, fetch_pictures, have,
                     hf_parquet_files, hf_parquet_rows, smaller)
from big_sources import even_pick
from more_sources import agreed_answer, as_question, download_to, fetch_shared, json_in_zip, narrative_row, sentence

DOCTOR = "Only a doctor can diagnose this."


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


# ----------------------------------------------------------------- shared helpers

class RemoteFile(io.RawIOBase):
    """A file on the web read piece by piece with HTTP range requests, so Python's zipfile can list a big zip and
    read single pictures out of it without downloading the whole zip. The address is asked again for every piece,
    so a download link that redirects to a short-lived signed address (Harvard Dataverse) keeps working."""

    def __init__(self, url, size=None, session=None):
        """url: the file's address; size: its size in bytes when known (otherwise asked with a HEAD request)."""
        import requests
        super().__init__()
        self.url, self.pos = url, 0
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        if size is None:
            head = self.session.head(url, allow_redirects=True, timeout=60)
            size = int(head.headers.get("content-length", 0))
        if not size:
            raise RuntimeError(f"the size of {url} could not be found")
        self.size = size

    def readable(self):
        """It can be read."""
        return True

    def seekable(self):
        """It can be moved about in."""
        return True

    def seek(self, offset, whence=0):
        """Move to offset (from the start, the current place or the end)."""
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def tell(self):
        """The current place."""
        return self.pos

    def readinto(self, buffer):
        """Read the next piece into buffer with one range request (tried up to four times)."""
        if self.pos >= self.size:
            return 0
        end = min(self.size, self.pos + len(buffer)) - 1
        for attempt in range(4):
            try:
                r = self.session.get(self.url, headers={"Range": f"bytes={self.pos}-{end}"}, timeout=120)
                if r.status_code == 206:
                    data = r.content
                    buffer[:len(data)] = data
                    self.pos += len(data)
                    return len(data)
            except Exception:  # noqa: BLE001 - tried again
                pass
            time.sleep(3 * (attempt + 1))
        raise RuntimeError(f"part of {self.url} could not be read; it is tried again the next time")


def remote_zip(url, size=None):
    """A zipfile.ZipFile for a zip on the web, read piece by piece (see RemoteFile)."""
    return zipfile.ZipFile(io.BufferedReader(RemoteFile(url, size), 1 << 20))


def zip_members(source, data_dir, work, open_zip, chosen, workers=4, prepare_picture=None):
    """Training copies of chosen pictures inside a zip: chosen is [(name in the zip, row)]. Each picture's original
    is kept in the downloads folder (work/<key>/), so a stopped run carries on and the picture library keeps it;
    open_zip() gives a ZipFile (a remote_zip, opened once per worker). prepare_picture(bytes) may change the picture
    first (FGVC-Aircraft's strip). The rows whose picture worked, with "picture" set."""
    keep = os.path.join(work, source.key)
    folder = os.path.join(data_dir, source.key)
    os.makedirs(keep, exist_ok=True)
    os.makedirs(folder, exist_ok=True)
    local = threading.local()

    def one(item):
        """One picture: its row with "picture", or None."""
        name, row = item
        safe = re.sub(r"[^\w.-]", "_", name)[-120:]
        target = os.path.join(folder, os.path.splitext(safe)[0] + ".jpg")
        if not have(target):
            original = os.path.join(keep, safe)
            if not os.path.exists(original):
                if not hasattr(local, "zip"):
                    local.zip = open_zip()
                try:
                    data = local.zip.read(name)
                except Exception:  # noqa: BLE001 - a picture that cannot be read is left out
                    return None
                with open(original + ".part", "wb") as f:
                    f.write(data)
                os.replace(original + ".part", original)
            with open(original, "rb") as f:
                data = f.read()
            if prepare_picture:
                data = prepare_picture(data)
            if not data or not smaller(data, target):
                return None
        return dict(row, picture=target)

    rows, done = [], 0
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for result in pool.map(one, chosen):
            done += 1
            if result:
                rows.append(result)
            if done % 250 == 0:
                say(f"    {done} of {len(chosen)} pictures done")
    return rows


def a_or_an(word):
    """ "a" or "an" before a word ("an Airbus", "a Boeing")."""
    return "an" if word[:1].lower() in "aeiou" else "a"


# Words that name a child in people's own descriptions and questions: such a row gets "child": true, so a
# picture-making model never learns from it.
CHILD_WORDS = re.compile(r"\b(child\w*|kids?|boys?|girls?|bab(y|ies)|toddlers?|infants?|newborns?|teen\w*|"
                         r"youngsters?|schoolchildren|schoolboys?|schoolgirls?|students?|pupils?|sons?|daughters?|"
                         r"little ones?|minors?|juveniles?|youths?)\b", re.I)

# Body sites whose skin pictures are left out (the owner allows medical pictures, not intimate ones).
INTIMATE_SITE = re.compile(r"genit|groin|scrot|penis|penile|vulv|vagin|labia|pubic|mons|perianal|perigenital|"
                           r"anogenital|inguinal|buttock|glute|breast|nipple|areola|suprapubic", re.I)


def looks_like(name, explanation):
    """The fixed sentence for a named condition, as in the open medical packs: "This looks like X (explanation)." A
    name with its own brackets ("hives (urticaria)") shares them with the explanation: "hives (urticaria, ...)"."""
    inner = re.match(r"(.*) \((.*)\)$", name)
    if inner and explanation:
        return f"This looks like {inner.group(1)} ({inner.group(2)}, {explanation})."
    return f"This looks like {name} ({explanation})." if explanation else f"This looks like {name}."


# ----------------------------------------------------------------- skin: HAM10000 and ISIC under CC BY-NC

DATAVERSE = "https://dataverse.harvard.edu/api/"
HAM_DOI = "doi:10.7910/DVN/DBW86T"
DERMOSCOPY = "A dermoscopy picture (a close-up taken through a skin magnifier with a light)"
HAM_DIAGNOSES = {
    "nv": ("a mole", "a nevus, usually harmless"),
    "mel": ("a melanoma", "a serious skin cancer"),
    "bkl": ("a harmless keratosis", "a benign growth such as a seborrheic keratosis, a sun spot or a fading "
                                    "lichen planus-like keratosis"),
    "bcc": ("a basal cell carcinoma", "a common skin cancer that grows slowly"),
    "akiec": ("an actinic keratosis or an early skin cancer", "a rough, scaly patch caused by years of sun, or "
                                                              "Bowen's disease, a skin cancer still only in the top "
                                                              "layer of the skin"),
    "vasc": ("a growth of small blood vessels", "such as a cherry angioma or an angiokeratoma, usually harmless"),
    "df": ("a dermatofibroma", "a harmless firm bump in the skin"),
}
HAM_SITES = {"abdomen": "the belly", "acral": "the palm or sole", "back": "the back", "chest": "the chest",
             "ear": "the ear", "face": "the face", "foot": "the foot", "hand": "the hand", "lower extremity": "the leg",
             "neck": "the neck", "scalp": "the scalp", "trunk": "the body", "upper extremity": "the arm"}
WHAT_SKIN = "What is this mark on the skin?"


def dataverse_files(doi):
    """{file name: (download address, size)} of the latest version of a Harvard Dataverse dataset."""
    import requests
    data = requests.get(f"{DATAVERSE}datasets/:persistentId/", params={"persistentId": doi}, timeout=60,
                        headers={"User-Agent": USER_AGENT}).json()["data"]["latestVersion"]
    return {f["dataFile"]["filename"]: (f"{DATAVERSE}access/datafile/{f['dataFile']['id']}",
                                        f["dataFile"].get("filesize"))
            for f in data["files"]}


def ham_answer(r):
    """The answer for one HAM10000 record (age, sex, body site and diagnosis from its metadata)."""
    sex = {"male": "man", "female": "woman"}.get(r.get("sex"), "person")
    site = HAM_SITES.get(r.get("localization"), "")
    text = f"{DERMOSCOPY} of a skin spot" + (f" on {site}" if site else "") + \
        f" of an adult {sex} aged about {int(float(r['age']))}."
    return f"{text} {looks_like(*HAM_DIAGNOSES[r['dx']])} {DOCTOR}"


def prepare_ham10000(source, data_dir, work, cap):
    """HAM10000 (Tschandl, Rosendahl and Kittler, 2018; Harvard Dataverse DBW86T, CC BY-NC 4.0): 10,015 dermoscopy
    pictures with the diagnosis, age, sex and body site. Adults aged 20 or more (ages are rounded to 5 years), no
    genital sites, balanced across the seven diagnoses. One picture per skin spot. Only the chosen pictures are read
    out of the two image zips (2.8 GB together) by HTTP ranges."""
    files = dataverse_files(HAM_DOI)
    meta_url = files["HAM10000_metadata.tab"][0] + "?format=original"
    import requests
    table = requests.get(meta_url, timeout=120, headers={"User-Agent": USER_AGENT}).content.decode("utf-8-sig")
    groups, seen = {}, set()
    for r in csv.DictReader(io.StringIO(table)):
        try:
            age = float(r.get("age") or 0)
        except ValueError:
            continue
        if age < 20 or r["dx"] not in HAM_DIAGNOSES or INTIMATE_SITE.search(r.get("localization", "")) \
                or r.get("localization") == "genital" or r["lesion_id"] in seen:
            continue
        seen.add(r["lesion_id"])
        groups.setdefault(r["dx"], []).append(r["image_id"])
    records = {r["image_id"]: r for r in csv.DictReader(io.StringIO(table))}
    picked = set(even_pick(groups, cap + source.test, 101))
    say(f"  HAM10000: {len(picked)} pictures of adults, from {len(groups)} diagnoses.")
    rows = []
    for name in ("HAM10000_images_part_1.zip", "HAM10000_images_part_2.zip"):
        url, size = files[name]
        z = remote_zip(url, size)
        chosen = [(n, {"question": WHAT_SKIN, "answer": ham_answer(records[base]), "split": ""})
                  for n in z.namelist() for base in [os.path.splitext(os.path.basename(n))[0]] if base in picked]
        z.close()
        say(f"  Reading {len(chosen)} pictures out of {name}.")
        rows += zip_members(source, data_dir, work, lambda u=url, s=size: remote_zip(u, s), chosen)
    return rows


ISIC = "https://api.isic-archive.com/api/v2/images/"
ISIC_NC_BASE = 'copyright_license:CC-BY-NC AND age_approx:[20 TO *] AND ' \
               '(image_type:dermoscopic OR image_type:"clinical: close-up")'
# Attributions of HAM10000's own pictures, which the ham10000 collection already uses.
HAM_ATTRIBUTION = re.compile(r"Medical University of Vienna|Rosendahl", re.I)
ISIC_DIAGNOSES = {
    "Nevus": ("a mole", "a nevus, usually harmless"),
    "Basal cell carcinoma": ("a basal cell carcinoma", "a common skin cancer that grows slowly"),
    "Seborrheic keratosis": ("a seborrheic keratosis", "a harmless, wart-like growth"),
    "Solar or actinic keratosis": ("an actinic keratosis", "a rough, scaly patch caused by years of sun, which can "
                                                           "sometimes turn into skin cancer"),
    "Melanoma in situ": ("an early melanoma (melanoma in situ)", "a skin cancer still only in the top layer of the "
                                                                 "skin"),
    "Melanoma Invasive": ("a melanoma", "a serious skin cancer"),
    "Melanoma, NOS": ("a melanoma", "a serious skin cancer"),
    "Squamous cell carcinoma, NOS": ("a squamous cell carcinoma", "a skin cancer that should be treated early"),
    "Squamous cell carcinoma in situ": ("an early squamous cell carcinoma (in situ)", "a skin cancer still only in "
                                                                                      "the top layer of the skin"),
    "Solar lentigo": ("a sun spot (solar lentigo)", "a harmless flat brown spot caused by sun"),
    "Lentigo NOS": ("a lentigo", "a harmless flat brown spot"),
    "Lichen planus like keratosis": ("a lichen planus-like keratosis", "a harmless spot that is often a fading "
                                                                       "sun spot or seborrheic keratosis"),
    "Dermatofibroma": ("a dermatofibroma", "a harmless firm bump in the skin"),
    "Hemangioma": ("a hemangioma", "a harmless growth of small blood vessels"),
    "Angiokeratoma": ("an angiokeratoma", "a harmless dark red or purple spot of small blood vessels"),
    "Atypical melanocytic neoplasm": ("an unusual mole (atypical melanocytic neoplasm)", "doctors watch or remove "
                                                                                         "these to be safe"),
}
ISIC_TYPES = {"dermoscopic": DERMOSCOPY, "clinical: close-up": "A close-up photo"}


def isic_site(clinical):
    """The most exact body site of an ISIC record in plain words ("the upper back"), or ""."""
    for key in ("anatom_site_5", "anatom_site_4", "anatom_site_3", "anatom_site_2", "anatom_site_1",
                "anatom_site_general"):
        site = clean(clinical.get(key))
        if site:
            site = site.lower().replace("anterior torso", "front of the body").replace(
                "posterior torso", "back").replace("upper extremity", "arm").replace(
                "lower extremity", "leg").replace("anterior ", "front of the ").replace("posterior ", "back of the ")
            return "the " + re.sub(r"^the ", "", site)
    return ""


def isic_answer(record):
    """The answer for one ISIC record: kind of picture, body site, age, sex and the diagnosis."""
    clinical = record["metadata"]["clinical"]
    kind = ISIC_TYPES[record["metadata"]["acquisition"]["image_type"]]
    site = isic_site(clinical)
    sex = {"male": "man", "female": "woman"}.get(clinical.get("sex"), "person")
    text = f"{kind} of a skin spot" + (f" on {site}" if site else "") + \
        f" of an adult {sex} aged about {clinical['age_approx']}."
    return f"{text} {looks_like(*ISIC_DIAGNOSES[clinical['diagnosis_3']])} {DOCTOR}"


def isic_page(session, query, url=None):
    """One page (up to 100 records) of an ISIC search, and the next page's address."""
    for attempt in range(4):
        try:
            r = session.get(url, timeout=120) if url else \
                session.get(ISIC + "search/", params={"query": query, "limit": 100}, timeout=120)
            if r.status_code == 200:
                data = r.json()
                return data.get("results") or [], data.get("next")
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(5 * (attempt + 1))
    return [], None


def prepare_isic_nc(source, data_dir, work, cap):
    """ISIC Archive pictures whose own licence is CC BY-NC (about 248,000; most from the Hospital Clinic of Barcelona
    and Memorial Sloan Kettering): adults (rounded age 20 or more), dermoscopy or close-up photos, no intimate body
    sites, an equal share for each diagnosis. Each record's licence, age and site are checked again."""
    import requests
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    share = max(2, (cap + source.test) // len(ISIC_DIAGNOSES) + 1)
    groups = {}
    for diagnosis in ISIC_DIAGNOSES:
        records, url = [], None
        while len(records) < share * 2:
            page, url = isic_page(session, f'{ISIC_NC_BASE} AND diagnosis_3:"{diagnosis}"', url)
            for r in page:
                meta = r.get("metadata") or {}
                clinical, kind = meta.get("clinical") or {}, (meta.get("acquisition") or {}).get("image_type")
                sites = " ".join(str(v) for k, v in clinical.items() if "anatom" in k)
                if r.get("copyright_license") != "CC-BY-NC" or (clinical.get("age_approx") or 0) < 20 \
                        or kind not in ISIC_TYPES or clinical.get("diagnosis_3") != diagnosis \
                        or INTIMATE_SITE.search(sites) or HAM_ATTRIBUTION.search(r.get("attribution") or ""):
                    continue
                records.append((f"{r['isic_id']}.jpg", r["files"]["full"]["url"],
                                {"question": WHAT_SKIN, "answer": isic_answer(r), "split": ""}))
            if not url or not page:
                break
            time.sleep(0.5)
        if records:
            groups[diagnosis] = records
        say(f"  ISIC {diagnosis}: {len(records)} usable")
    items = even_pick(groups, int((cap + source.test) * 1.05), 103)
    say(f"  Fetching {len(items)} ISIC pictures.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- skin: SCIN (Google)

SCIN_URL = "https://storage.googleapis.com/dx-scin-public-data/"
WHAT_SKIN_PROBLEM = "What could this skin problem be?"
# The dermatologists' most likely condition (its weight at least one half), in plain words.
SCIN_CONDITIONS = {
    "Eczema": ("eczema", "dry, itchy, inflamed skin"),
    "Allergic Contact Dermatitis": ("an allergic skin reaction (allergic contact dermatitis)", "a rash where the "
                                                                                               "skin touched "
                                                                                               "something it is "
                                                                                               "allergic to"),
    "Irritant Contact Dermatitis": ("irritated skin (irritant contact dermatitis)", "a rash where something harsh "
                                                                                    "touched the skin"),
    "CD - Contact dermatitis": ("contact dermatitis", "a rash where the skin touched something"),
    "Urticaria": ("hives (urticaria)", "raised, itchy welts that come and go"),
    "Insect Bite": ("insect bites", ""),
    "Folliculitis": ("folliculitis", "small red or pus-filled bumps around hairs"),
    "Psoriasis": ("psoriasis", "thick, red, scaly patches that come and go"),
    "Tinea": ("a fungal infection (ringworm or tinea)", "often a ring-shaped, scaly rash"),
    "Tinea Versicolor": ("tinea versicolor", "a common yeast infection that leaves lighter or darker patches"),
    "Herpes Zoster": ("shingles (herpes zoster)", "a painful, blistering rash on one side of the body"),
    "Herpes Simplex": ("a cold sore or herpes simplex", "small painful blisters caused by a virus"),
    "Acne": ("acne", "spots, blackheads and pimples"),
    "Pigmented purpuric eruption": ("a pigmented purpuric eruption", "harmless rust-coloured specks from tiny leaks "
                                                                     "of blood under the skin"),
    "Impetigo": ("impetigo", "a contagious skin infection with honey-coloured crusts"),
    "Acute dermatitis, NOS": ("dermatitis", "an inflamed, red, itchy rash"),
    "Pityriasis rosea": ("pityriasis rosea", "a harmless rash of oval, scaly patches that fades by itself"),
    "O/E - ecchymoses present": ("bruising", ""),
    "Rosacea": ("rosacea", "redness and small bumps on the face"),
    "Leukocytoclastic Vasculitis": ("inflamed small blood vessels (leukocytoclastic vasculitis)", "small raised "
                                                                                                   "purple-red spots"),
    "Keratosis pilaris": ("keratosis pilaris", "harmless small rough bumps, often on the upper arms"),
    "Lichen Simplex Chronicus": ("lichen simplex chronicus", "thick, leathery skin from long scratching"),
    "Drug Rash": ("a rash caused by a medicine", ""),
    "Molluscum Contagiosum": ("molluscum contagiosum", "small, firm, pearly bumps caused by a virus"),
    "Purpura": ("purpura", "purple spots from bleeding under the skin"),
    "Lichen planus/lichenoid eruption": ("lichen planus", "itchy, flat-topped, purplish bumps"),
    "Granuloma annulare": ("granuloma annulare", "a harmless ring of small firm bumps"),
    "Seborrheic Dermatitis": ("seborrheic dermatitis", "red, flaky, greasy patches, like dandruff"),
    "Perioral Dermatitis": ("perioral dermatitis", "a rash of small red bumps around the mouth"),
    "Verruca vulgaris": ("a wart", "a harmless growth caused by a virus"),
    "Photodermatitis": ("a sun-related rash (photodermatitis)", ""),
    "Stasis Dermatitis": ("stasis dermatitis", "inflamed skin on the lower legs from poor circulation"),
    "Miliaria": ("heat rash (miliaria)", "tiny bumps from blocked sweat glands"),
    "Scabies": ("scabies", "a very itchy rash caused by tiny mites"),
    "Abscess": ("an abscess", "a painful swelling filled with pus"),
    "Viral Exanthem": ("a viral rash", "a widespread rash that comes with a virus"),
    "Prurigo nodularis": ("prurigo nodularis", "hard, very itchy lumps"),
}
SCIN_AGES = {"AGE_18_TO_29": "18 to 29", "AGE_30_TO_39": "30 to 39", "AGE_40_TO_49": "40 to 49",
             "AGE_50_TO_59": "50 to 59", "AGE_60_TO_69": "60 to 69", "AGE_70_TO_79": "70 to 79",
             "AGE_80_OR_ABOVE": "80 or over"}
SCIN_PARTS = (("head_or_neck", "the head or neck"), ("arm", "an arm"), ("palm", "a palm"),
              ("back_of_hand", "the back of a hand"), ("torso_front", "the front of the body"),
              ("torso_back", "the back"), ("leg", "a leg"), ("foot_top_or_side", "a foot"), ("foot_sole", "a sole"))
SCIN_FELT = (("itching", "it itches"), ("burning", "it burns"), ("pain", "it hurts"), ("bleeding", "it has bled"),
             ("increasing_size", "it is getting bigger"), ("darkening", "it is getting darker"))
SCIN_DURATION = {"ONE_DAY": "a day ago", "LESS_THAN_ONE_WEEK": "less than a week ago",
                 "ONE_TO_FOUR_WEEKS": "one to four weeks ago", "ONE_TO_THREE_MONTHS": "one to three months ago",
                 "THREE_TO_TWELVE_MONTHS": "three to twelve months ago", "MORE_THAN_ONE_YEAR": "more than a year ago",
                 "MORE_THAN_FIVE_YEARS": "more than five years ago"}
SCIN_SHOTS = {"CLOSE_UP": "A close-up phone photo", "AT_AN_ANGLE": "A phone photo, taken at an angle,",
              "AT_DISTANCE": "A phone photo, taken from further away,"}


def listed(items):
    """Items in a sentence: "a", "a and b", "a, b and c"."""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def scin_answer(case, condition, shot):
    """The answer for one SCIN photo: the kind of photo, where on the body, who, what the person reported, how long
    ago it began, and the dermatologists' most likely condition."""
    sex = {"MALE": "a man", "FEMALE": "a woman"}.get(case.get("sex_at_birth"), "a person")
    parts = [words for key, words in SCIN_PARTS if case.get(f"body_parts_{key}") == "YES"]
    text = f"{SCIN_SHOTS.get(shot, 'A phone photo')} of a skin problem" + \
        (f" on {listed(parts)}" if parts and len(parts) <= 3 else "") + \
        f" of {sex} aged {SCIN_AGES[case['age_group']]}."
    felt = [words for key, words in SCIN_FELT if case.get(f"condition_symptoms_{key}") == "YES"]
    if felt:
        text += f" The person said that {listed(felt)}."
    if case.get("condition_duration") in SCIN_DURATION:
        text += f" It began {SCIN_DURATION[case['condition_duration']]}."
    return f"{text} {looks_like(*SCIN_CONDITIONS[condition])} {DOCTOR}"


def prepare_scin(source, data_dir, work, cap):
    """SCIN (Skin Condition Image Network; Google and Stanford Medicine, 2024): about 10,000 photos that adults in the
    United States took of their own skin problems with their phones, with what they reported and the conditions three
    dermatologists gave (SCIN Data Use License). Used: cases with an adult age group given, judged gradable, whose
    most likely condition (weight at least one half) is in SCIN_CONDITIONS; never cases on the genitals, groin or
    buttocks; for the front of the body, only close-ups. One photo per case (a close-up when there is one), balanced
    across conditions."""
    import requests
    cases = {r["case_id"]: r for r in csv.DictReader(io.StringIO(
        requests.get(SCIN_URL + "dataset/scin_cases.csv", timeout=120).content.decode("utf-8-sig")))}
    groups = {}
    for r in csv.DictReader(io.StringIO(requests.get(SCIN_URL + "dataset/scin_labels.csv",
                                                      timeout=120).content.decode("utf-8-sig"))):
        case = cases.get(r["case_id"])
        if not case or case.get("age_group") not in SCIN_AGES or \
                not (r.get("dermatologist_gradable_for_skin_condition_1") or "").startswith("DEFAULT_YES") or \
                case.get("body_parts_genitalia_or_groin") == "YES" or case.get("body_parts_buttocks") == "YES":
            continue
        try:
            weights = ast.literal_eval(r.get("weighted_skin_condition_label") or "{}")
        except (ValueError, SyntaxError):
            continue
        if not weights:
            continue
        condition, weight = max(weights.items(), key=lambda kv: kv[1])
        if weight < 0.5 or condition not in SCIN_CONDITIONS:
            continue
        shots = [(case.get(f"image_{n}_path"), case.get(f"image_{n}_shot_type")) for n in (1, 2, 3)]
        shots = [s for s in shots if s[0]]
        close = [s for s in shots if s[1] == "CLOSE_UP"]
        if case.get("body_parts_torso_front") == "YES":
            shots = close                                  # only close-ups of the front of the body
        shot = (close or shots or [None])[0]
        if shot:
            groups.setdefault(condition, []).append((case["case_id"], shot[0], shot[1], condition))
    picked = even_pick(groups, cap + source.test, 107)
    say(f"  SCIN: {len(picked)} photos from {len(groups)} conditions.")
    items = [(os.path.basename(path).replace(".png", ".jpg"), SCIN_URL + path,
              {"question": WHAT_SKIN_PROBLEM, "answer": scin_answer(cases[case_id], condition, shot), "split": ""})
             for case_id, path, shot, condition in picked]
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- COCO photos under non-commercial licences

# COCO's licence numbers: 1 CC BY-NC-SA 2.0, 2 CC BY-NC 2.0, 3 CC BY-NC-ND 2.0 (the open kit uses 4 and 7 only).
COCO_NC_LICENCES = (1, 2, 3)


def coco_nc_photos():
    """The COCO photos under a non-commercial licence: {COCO image number: (address, child)}, where child is True
    when any of the photo's five COCO descriptions names a child. Read from the same list the open kit uses (the
    phiyodr copy of COCO 2017 on Hugging Face, 30 MB); the photos themselves come from cocodataset.org."""
    say("  Reading COCO's list of photos, their licences and descriptions.")
    found = {}
    for name in hf_parquet_files("phiyodr/coco2017", r"^data/"):
        for row in hf_parquet_rows("phiyodr/coco2017", name, ["license", "image_id", "coco_url", "captions"]):
            if row.get("license") in COCO_NC_LICENCES:
                child = any(CHILD_WORDS.search(c or "") for c in row.get("captions") or [])
                found[int(row["image_id"])] = (row["coco_url"], child, row.get("captions") or [])
    return found


def prepare_coco_nc(source, data_dir, work, cap):
    """COCO Captions on the photos under non-commercial Flickr licences: one of the five one-sentence descriptions
    people wrote (CC BY 4.0), the first good one. "child" marks photos whose descriptions name a child."""
    photos = coco_nc_photos()
    ids = sorted(photos)
    random.Random(109).shuffle(ids)
    items = []
    for image_id in ids[:int((cap + source.test) * 1.1)]:
        url, child, captions = photos[image_id]
        caption = next((clean(c) for c in captions if len(clean(c).split()) >= 5), "")
        if caption:
            items.append((f"{image_id}.jpg", url, {"question": BRIEF, "answer": sentence(caption), "split": "",
                                                   "child": child}))
    say(f"  Fetching {len(items)} COCO photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key))


def prepare_vqav2_nc(source, data_dir, work, cap):
    """VQA v2, val2014 part, on the COCO photos under non-commercial licences: the answer at least three of ten people
    gave (CC BY 4.0). At most 4 questions per photo."""
    from more_sources import VQA_URL, pick_by_photo
    photos = coco_nc_photos()
    say("  Downloading the VQA v2 questions and answers (14 MB).")
    questions = json_in_zip(download_to(work, VQA_URL + "v2_Questions_Val_mscoco.zip"))["questions"]
    annotations = json_in_zip(download_to(work, VQA_URL + "v2_Annotations_Val_mscoco.zip"))["annotations"]
    asked = {q["question_id"]: q for q in questions if q["image_id"] in photos}
    per_photo = {}
    for a in annotations:
        q = asked.get(a["question_id"])
        if not q:
            continue
        answer, question = agreed_answer([x["answer"] for x in a["answers"]]), as_question(q["question"])
        if answer and question:
            url, child, _captions = photos[q["image_id"]]
            child = child or bool(CHILD_WORDS.search(question + " " + answer))
            per_photo.setdefault(q["image_id"], []).append(
                (f"{q['image_id']}.jpg", url, {"question": question, "answer": answer, "split": "", "child": child}))
    items = pick_by_photo(per_photo, int((cap + source.test) * 1.1), 113, 4)
    say(f"  Fetching the COCO photos for {len(items)} VQA v2 questions.")
    return fetch_shared(items, os.path.join(data_dir, source.key))


def prepare_ln_coco_nc(source, data_dir, work, cap):
    """Localized Narratives on the COCO photos under non-commercial licences: people described the photo aloud,
    written down (Google; CC BY 4.0). COCO's val2017 part gives the test pictures."""
    from more_sources import LN_URL
    photos = coco_nc_photos()
    items = []
    for part, split in (("coco_train_captions.jsonl", ""), ("coco_val_captions.jsonl", "test")):
        say(f"  Downloading the Localized Narratives for COCO ({part}).")
        with open(download_to(work, LN_URL + part, "ln_" + part), encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                image_id = int(entry["image_id"])
                if image_id not in photos:
                    continue
                row = narrative_row(sources.tidy_narrative(entry.get("caption")), split)
                if row:
                    url, child, _captions = photos[image_id]
                    row["child"] = child or bool(CHILD_WORDS.search(row["answer"]))
                    items.append((f"{image_id}.jpg", url, row))
    random.Random(127).shuffle(items)
    items = items[:int((cap + source.test) * 1.1)]
    say(f"  Fetching {len(items)} COCO photos.")
    return fetch_shared(items, os.path.join(data_dir, source.key))


# ----------------------------------------------------------------- forms: XFUND and FUNSD

READ_FORM = "Read out the title of this form and its filled-in fields."
XFUND_URL = "https://github.com/doc-analysis/XFUND/releases/download/v1.0/"
XFUND_LANGUAGES = {"de": "German", "es": "Spanish", "fr": "French", "it": "Italian", "ja": "Japanese",
                   "pt": "Portuguese", "zh": "Chinese"}
MOST_FIELDS = 25
# Fields whose values are identity numbers (FUNSD's real forms hold some US Social Security numbers): left out.
PRIVATE_FIELD = re.compile(r"\bS\.?S\.?\s*(#|no\b|n[ou]m)|social security|\bSSN\b|seguro social|s[ée]curit[ée] "
                           r"sociale|sicurezza sociale|codice fiscale|passport|pasaporte|passeport|passaporto|"
                           r"ausweis|c[ée]dula|identidad|identit[ée]|identit[àa]|date of birth|geburtsdatum|"
                           r"nacimiento|naissance|nascita|身份证|マイナンバー",
                           re.I)


def form_answer(entities, language=""):
    """The answer for one form from its annotated parts (XFUND and FUNSD share the form): the headers, then each
    question (a field's name) with the answers linked to it, in reading order (top to bottom, left to right). None
    when the form has no linked fields or more than MOST_FIELDS of them (the answer would be too long)."""
    by_id = {e["id"]: e for e in entities}
    order = lambda e: (e["box"][1] // 15, e["box"][0])                 # noqa: E731 - same line within 15 pixels
    headers = [clean(e["text"]) for e in sorted(entities, key=order) if e["label"] == "header" and clean(e["text"])]
    fields = []
    for e in sorted(entities, key=order):
        if e["label"] != "question" or not clean(e["text"]):
            continue
        linked = [by_id[b] for a, b in e.get("linking") or [] if a == e["id"] and b in by_id] + \
                 [by_id[a] for a, b in e.get("linking") or [] if b == e["id"] and a in by_id]
        answers = [clean(x["text"]) for x in sorted(linked, key=order) if x["label"] == "answer" and clean(x["text"])]
        if answers and not PRIVATE_FIELD.search(e["text"]):
            fields.append(f"{clean(e['text']).rstrip(':').strip()}: {'; '.join(answers)}")
    if not fields or len(fields) > MOST_FIELDS:
        return None
    text = (f"This is a form in {language}. " if language else "")
    if headers:
        text += "Its title reads: " + " / ".join(headers[:3]) + ". "
    return text + "The filled-in fields are: " + ". ".join(fields) + "."


def prepare_xfund(source, data_dir, work, cap):
    """XFUND (Xu et al., 2022; Microsoft; CC BY-NC-SA 4.0): 1,393 real forms in German, Spanish, French, Italian,
    Japanese, Portuguese and Chinese, each part of the text marked as a field name, an answer or a header, and linked.
    "Read out the title of this form and its filled-in fields." Only the chosen form pictures are read out of the
    release zips (about 1.9 GB together) by HTTP ranges; the val part gives the test pictures."""
    import requests
    groups = {}
    for code, language in XFUND_LANGUAGES.items():
        for part in ("train", "val"):
            data = requests.get(f"{XFUND_URL}{code}.{part}.json", timeout=120,
                                headers={"User-Agent": USER_AGENT}).json()
            for doc in data["documents"]:
                answer = form_answer(doc["document"], language)
                if answer:
                    groups.setdefault(code, []).append((f"{code}.{part}", doc["img"]["fname"], answer,
                                                        "test" if part == "val" else ""))
    picked = even_pick(groups, cap + source.test, 131)
    rows = []
    for zip_name in sorted({p[0] for p in picked}):
        chosen = [(fname, {"question": READ_FORM, "answer": answer, "split": split})
                  for z, fname, answer, split in picked if z == zip_name]
        say(f"  Reading {len(chosen)} forms out of {zip_name}.zip.")
        url = f"{XFUND_URL}{zip_name}.zip"
        rows += zip_members(source, data_dir, work, lambda u=url: remote_zip(u), chosen, workers=2)
    return rows


FUNSD_URL = "https://guillaumejaume.github.io/FUNSD/dataset.zip"


def prepare_funsd(source, data_dir, work, cap):
    """FUNSD (Jaume, Ekenel and Thiran, 2019; EPFL): 199 noisy scanned forms (from the RVL-CDIP tobacco documents),
    each part of the text marked and linked as in XFUND: "Read out the title of this form and its filled-in fields."
    The zip is 17 MB, downloaded once; its testing_data part gives the test pictures."""
    archive = download_to(work, FUNSD_URL, "funsd_dataset.zip")
    rows = []
    with zipfile.ZipFile(archive) as z:
        chosen = []
        for name in z.namelist():
            if "__MACOSX" in name or not re.search(r"/annotations/[^/]+\.json$", name):
                continue
            answer = form_answer(json.loads(z.read(name))["form"])
            if answer:
                picture = name.replace("/annotations/", "/images/")[:-5] + ".png"
                chosen.append((picture, {"question": READ_FORM, "answer": answer,
                                         "split": "test" if "testing_data" in name else ""}))
        rows = zip_members(source, data_dir, work, lambda: zipfile.ZipFile(archive), chosen[:cap + source.test * 3])
    return rows


# ----------------------------------------------------------------- school science, diagrams and charts

def choice_question(question, choices, context=""):
    """A multiple-choice question in plain text: the context (when given), the question, then "Choices: a, b, c." """
    text = (clean(context) + "\n" if clean(context) else "") + clean(question)
    return text + "\nChoices: " + "; ".join(clean(c) for c in choices) + "."


def first_sentences(text, most_words=60):
    """The first sentences of text, at most about most_words words."""
    out = ""
    for s in re.split(r"(?<=[.!?])\s+", clean(text)):
        if out and len((out + " " + s).split()) > most_words:
            break
        out = (out + " " + s).strip()
    return out


def prepare_scienceqa(source, data_dir, work, cap):
    """ScienceQA (Lu et al., 2022; CC BY-NC-SA 4.0): school science questions with a picture (diagrams, maps, photos
    of animals and objects), several choices, the right answer and the explanation people wrote (from IXL). Only
    questions with a picture; "The answer is: ... ." and the first sentences of the explanation. Its validation part
    gives the test pictures."""
    rows = []
    for name in hf_parquet_files("derek-thomas/ScienceQA", r"^data/(train|validation)-"):
        split = "test" if "/validation-" in name else ""
        say(f"  ScienceQA part {name.rsplit('/', 1)[-1].split('-')[0]}.")
        found = [(index, row) for index, row in enumerate(hf_parquet_rows("derek-thomas/ScienceQA", name))
                 if (row.get("image") or {}).get("bytes") and row.get("choices") and row.get("answer") is not None
                 and row["answer"] < len(row["choices"])]
        random.Random(137).shuffle(found)
        want = source.test * 3 if split == "test" else cap
        for index, row in found[:want]:
            choices = row["choices"]
            answer = f"The answer is: {clean(choices[row['answer']])}."
            why = first_sentences(row.get("solution"))
            if why:
                answer += " " + why
            child = bool(CHILD_WORDS.search(row.get("question") or ""))
            path = sources.save_picture(f"scienceqa-{split or 'train'}-{index}", row["image"]["bytes"],
                                        os.path.join(data_dir, source.key))
            if path:
                rows.append({"picture": path, "question": choice_question(row["question"], choices, row.get("hint")),
                             "answer": answer, "split": split, "child": child})
    return rows


def prepare_chartqa(source, data_dir, work, cap):
    """ChartQA (Masry et al., 2022; GPL-3.0; the authors' own copy on Hugging Face): real charts from Statista, Pew,
    Our World in Data and the OECD, with questions people wrote ("human" rows only; the machine-made "augmented"
    rows are left out). Its val part gives the test pictures."""
    files = hf_parquet_files("ahmed-masry/ChartQA", r"^data/(train|val)-")
    rows, per_train_file = [], cap // max(1, sum(1 for f in files if "/train-" in f)) + 1
    for name in files:
        split = "test" if "/val-" in name else ""
        say(f"  ChartQA part {name.rsplit('/', 1)[-1]}.")
        found = [row for row in hf_parquet_rows("ahmed-masry/ChartQA", name)
                 if row.get("type") == "human" and clean(row.get("query")) and clean(row.get("label"))]
        random.Random(f"163-{name}").shuffle(found)
        for row in found[:source.test * 3 if split else per_train_file]:
            path = sources.save_picture(f"chartqa-{split or 'train'}-{row['imgname']}", row.get("image"),
                                        os.path.join(data_dir, source.key))
            if path:
                rows.append({"picture": path, "question": as_question(row["query"]),
                             "answer": sentence(chart_answer(row["label"])), "split": split})
    return rows


def chart_answer(label):
    """A ChartQA answer in words: a list written as "[Africa, Northern America]" becomes "Africa and Northern
    America"."""
    label = clean(label)
    if label.startswith("[") and label.endswith("]"):
        items = [clean(x).strip("'\"") for x in label[1:-1].split(",") if clean(x)]
        return listed(items) if items else ""
    return label


AI2D_URL = "https://ai2-public-datasets.s3.amazonaws.com/diagrams/ai2d-all.zip"


def prepare_ai2d(source, data_dir, work, cap):
    """AI2D (Kembhavi et al., 2016; Allen Institute for AI): about 5,000 school science diagrams (life cycles, parts of
    a plant, food webs, the moon's phases ...) with multiple-choice questions people wrote. The 990 MB zip is
    downloaded once. "The answer is: ... ." At most 3 questions per diagram."""
    archive = download_to(work, AI2D_URL, "ai2d-all.zip")
    return ai2d_rows(source, data_dir, work, cap, lambda: zipfile.ZipFile(archive))


def ai2d_rows(source, data_dir, work, cap, open_zip):
    """AI2D's rows from its zip (open_zip() gives the ZipFile): diagrams picked at random, their questions kept."""
    z = open_zip()
    names = sorted(n for n in z.namelist() if n.startswith("ai2d/questions/") and n.endswith(".json"))
    random.Random(139).shuffle(names)
    chosen, count = [], 0
    for name in names:
        if count >= cap + source.test:
            break
        data = json.loads(z.read(name))
        for question, q in list(data.get("questions", {}).items())[:3]:
            choices = q.get("answerTexts") or []
            if not choices or not 0 <= q.get("correctAnswer", -1) < len(choices):
                continue
            chosen.append((f"ai2d/images/{data['imageName']}",
                           {"question": choice_question(question, choices),
                            "answer": f"The answer is: {clean(choices[q['correctAnswer']])}.", "split": ""}))
            count += 1
    z.close()
    return zip_members(source, data_dir, work, open_zip, chosen, workers=2)


# ----------------------------------------------------------------- food, dogs and aircraft

def prepare_food101(source, data_dir, work, cap):
    """Food-101 (Bossard, Guillaumin and Van Gool, 2014; ETH Zurich): 101 dishes, photos from Foodspotting. The ETH
    copy on Hugging Face (ethz/food101), whose parquet files are read piece by piece: first only the labels, then
    only the parts that hold the chosen photos. Its validation part (250 hand-checked photos per dish) is used,
    balanced across dishes. "What food is this?" """
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem
    fs = HfFileSystem()
    files = hf_parquet_files("ethz/food101", r"^data/validation-")
    groups, names = {}, None
    for name in files:
        f = pq.ParquetFile(fs.open(f"datasets/ethz/food101/{name}"))
        if names is None:
            info = json.loads(f.schema_arrow.metadata[b"huggingface"])["info"]["features"]["label"]
            names = info["names"]
        labels = f.read(columns=["label"]).column("label").to_pylist()
        for index, label in enumerate(labels):
            groups.setdefault(label, []).append((name, index))
    picked = even_pick(groups, cap + source.test, 149)
    folder = os.path.join(data_dir, source.key)
    rows = []
    for name in files:
        wanted = sorted(i for n, i in picked if n == name)
        if not wanted:
            continue
        say(f"  Reading {len(wanted)} Food-101 photos from {name.rsplit('/', 1)[-1]}.")
        f = pq.ParquetFile(fs.open(f"datasets/ethz/food101/{name}"))
        start = 0
        for group in range(f.num_row_groups):
            size = f.metadata.row_group(group).num_rows
            inside = [i for i in wanted if start <= i < start + size]
            if inside:
                table = f.read_row_group(group, columns=["image", "label"]).to_pylist()
                for i in inside:
                    row = table[i - start]
                    dish = names[row["label"]].replace("_", " ")
                    path = sources.save_picture(f"food101-{row['label']}-{name[-20:-8]}-{i}",
                                                (row.get("image") or {}).get("bytes"), folder)
                    if path:
                        rows.append({"picture": path, "question": "What food is this?",
                                     "answer": f"This looks like {dish}.", "split": ""})
            start += size
    return rows


DOGS_URL = "http://vision.stanford.edu/aditya86/ImageNetDogs/images.tar"


def dog_breed(folder):
    """A breed in plain words from a Stanford Dogs folder ("n02085620-Chihuahua" -> "Chihuahua",
    "n02088094-Afghan_hound" -> "Afghan hound")."""
    name = folder.split("-", 1)[-1].replace("_", " ")
    return name[0].upper() + name[1:] if name.islower() else name


def prepare_stanford_dogs(source, data_dir, work, cap):
    """Stanford Dogs (Khosla et al., 2011): 20,580 ImageNet photos of 120 dog breeds. The 790 MB tar is downloaded
    once (kept, and it resumes); photos are picked evenly across breeds. "What breed of dog is this?" """
    archive = os.path.join(work, "stanford_dogs_images.tar")
    say("  Downloading the Stanford Dogs photos (790 MB, kept in the downloads folder; it resumes if stopped).")
    download_file(DOGS_URL, archive)
    with tarfile.open(archive) as tar:
        return dogs_rows(source, data_dir, work, cap, tar)


def dogs_rows(source, data_dir, work, cap, tar):
    """Stanford Dogs rows from its open tar (any tar whose members are Images/<folder>/<photo>.jpg)."""
    groups, members = {}, {}
    for m in tar.getmembers():
        parts = m.name.split("/")
        if m.isfile() and len(parts) == 3 and parts[2].lower().endswith(".jpg"):
            groups.setdefault(parts[1], []).append(m.name)
            members[m.name] = m
    picked = even_pick(groups, cap + source.test, 151)
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows = []
    for name in picked:
        breed = dog_breed(name.split("/")[1])
        target = os.path.join(folder, os.path.basename(name))
        if have(target) or smaller(tar.extractfile(members[name]).read(), target):
            rows.append({"picture": target, "question": "What breed of dog is this?",
                         "answer": f"This looks like {a_or_an(breed)} {breed}.", "split": ""})
    say(f"  {len(rows)} dog photos from {len(groups)} breeds.")
    return rows


AIRCRAFT_URL = "https://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/archives/fgvc-aircraft-2013b.tar.gz"


def without_banner(data):
    """An FGVC-Aircraft photo without the 20-pixel strip at its bottom that names the photographer (the dataset's
    makers ask for it to be removed), as JPEG bytes; None when it cannot be read."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:  # noqa: BLE001 - left out
        return None
    img = img.crop((0, 0, img.width, max(1, img.height - 20)))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=95)
    return out.getvalue()


def aircraft_answer(variant, manufacturer):
    """ "This looks like a Boeing 737-800." (the manufacturer is added when the model's name does not hold it)."""
    name = variant if manufacturer.split()[0].lower() in variant.lower() else f"{manufacturer} {variant}"
    return f"This looks like {a_or_an(name)} {name}."


def prepare_fgvc_aircraft(source, data_dir, work, cap):
    """FGVC-Aircraft (Maji et al., 2013; Oxford): 10,000 photos by aircraft spotters of 100 aircraft models, with each
    model's manufacturer. The 2.7 GB tar.gz is downloaded once (kept; it resumes) and read once: its label lists come
    first, so the photos are picked evenly across models before they are reached. "What aircraft is this?" """
    archive = os.path.join(work, "fgvc-aircraft-2013b.tar.gz")
    say("  Downloading FGVC-Aircraft (2.7 GB, kept in the downloads folder; it resumes if stopped).")
    download_file(AIRCRAFT_URL, archive)
    with tarfile.open(archive, "r|gz") as tar:
        return aircraft_rows(source, data_dir, work, cap, tar)


def aircraft_rows(source, data_dir, work, cap, tar, picker=None):
    """FGVC-Aircraft rows from its tar read in order (label lists first, then photos). picker(groups, want) may
    replace the even pick (the quick check uses it)."""
    variants, makers, picked = {}, {}, None
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows = []
    for m in tar:
        name = m.name.rsplit("/", 1)[-1]
        if name in ("images_variant_trainval.txt", "images_variant_test.txt",
                    "images_manufacturer_trainval.txt", "images_manufacturer_test.txt"):
            into = variants if "variant" in name else makers
            for line in tar.extractfile(m).read().decode("utf-8").splitlines():
                if " " in line:
                    number, label = line.split(" ", 1)
                    into[number] = label.strip()
        elif m.isfile() and name.endswith(".jpg"):
            if picked is None:
                groups = {}
                for number, variant in variants.items():
                    if number in makers:
                        groups.setdefault(variant, []).append(number)
                picked = set((picker or (lambda g, w: even_pick(g, w, 157)))(groups, cap + source.test))
                say(f"  FGVC-Aircraft: {len(picked)} photos picked from {len(groups)} models.")
            number = name[:-4]
            if number in picked:
                target = os.path.join(folder, name)
                data = None if have(target) else without_banner(tar.extractfile(m).read())
                if have(target) or (data and smaller(data, target)):
                    rows.append({"picture": target, "question": "What aircraft is this?",
                                 "answer": aircraft_answer(variants[number], makers[number]), "split": ""})
                if len(rows) >= len(picked):
                    break
    return rows


# ----------------------------------------------------------------- facial expressions: JAFFE

JAFFE_URL = "https://zenodo.org/api/records/14974867/files/jaffe.zip/content"
EXPRESSION_QUESTION = "What expression is on this person's face?"
# The visible signs first, then a careful reading (never a certainty about how she feels).
JAFFE_EXPRESSIONS = {
    "HA": "The corners of her mouth are drawn up in a smile and her cheeks are raised. She seems to be smiling, as "
          "if happy.",
    "SA": "The corners of her mouth turn down, her inner eyebrows are drawn up and her eyelids droop a little. She "
          "looks sad.",
    "SU": "Her eyebrows are raised high, her eyes are wide open and her mouth hangs open. She looks surprised.",
    "AN": "Her eyebrows are drawn down and together, her eyes narrowed and her lips pressed together. She looks "
          "angry.",
    "DI": "Her nose is wrinkled, her upper lip raised and her eyebrows lowered. She looks disgusted.",
    "FE": "Her eyebrows are raised and drawn together, her eyes wide and her mouth stretched. She looks afraid.",
    "NE": "Her mouth is relaxed and closed, and her eyebrows and eyes are at rest. Her face looks neutral, showing "
          "no particular expression.",
}


def jaffe_answer(code):
    """The answer for one JAFFE photo: what it is, the visible signs, a careful reading, and that it was posed."""
    return (f"A black-and-white photo of a Japanese woman's face, looking at the camera. "
            f"{JAFFE_EXPRESSIONS[code]} This expression was posed for the photo.")


def prepare_jaffe(source, data_dir, work, cap):
    """JAFFE (Lyons, Kamachi and Gyoba, 1998; Zenodo 14974867): 213 black-and-white photos of ten Japanese women
    posing seven expressions (happy, sad, surprised, angry, disgusted, afraid, neutral), labelled in the file names
    ("KA.HA1.29.tiff"). The 12 MB zip is downloaded once."""
    archive = download_to(work, JAFFE_URL, "jaffe.zip")
    chosen = []
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            m = re.search(r"/([A-Z]{2})\.([A-Z]{2})\d\.\d+\.tiff$", name)
            if m and m.group(2) in JAFFE_EXPRESSIONS:
                chosen.append((name, {"question": EXPRESSION_QUESTION, "answer": jaffe_answer(m.group(2)),
                                      "split": ""}))
    return zip_members(source, data_dir, work, lambda: zipfile.ZipFile(archive), chosen)


# ----------------------------------------------------------------- what was looked at and left out

REJECTED = {
    "Fitzpatrick17k": "CC BY-NC-SA 3.0 covers only its labels; the pictures stay the property of the two skin atlases "
                      "they link to, no ages are given (children are included) and genital conditions are common.",
    "Derm7pt": "registration on derm.cs.sfu.ca.",
    "DermNet": "no download; its pictures are licensed one by one, for a fee for most uses.",
    "Kvasir v2": "research and education only, but datasets.simula.no's certificate cannot be checked (the open "
                 "HyperKvasir pack already covers the same kind of pictures under CC BY 4.0).",
    "DFU diabetic foot ulcers": "registration and a licence agreement.",
    "UEC Food-256": "its download pages (foodcam.mobi, mm.cs.uec.ac.jp) are gone (404).",
    "ISIA Food-500": "no terms written; served from a bare IP address over plain HTTP, split into ten parts.",
    "FoodSeg103": "its server answers 502, the zip needs a password, and its pictures come from Recipe1M, which "
                  "needs an account.",
    "Oxford-IIIT Pet": "CC BY-SA 4.0: share-alike, so it belongs with Wikipedia (--with-wikipedia), not here.",
    "HaGRID hand gestures": "a variant of CC BY-SA 4.0: share-alike, so it belongs with the share-alike group.",
    "CUB-200-2011": "CaltechDATA says CC BY: it belongs in the open kit, not here (its Flickr photos have no licence "
                    "of their own written down, so check before adding it there).",
    "FoodSeg103, PlantVillage, PlantDoc, Pl@ntNet-300K, Fashionpedia": "openly licensed (Apache, CC0 or CC BY): "
                                                                       "for the open kit, not this list.",
    "TextCaps, TextVQA, TextOCR, nocaps": "all their photos are Open Images photos, which are all CC BY 2.0: nothing "
                                          "non-free to add (nocaps' captions are CC BY 2.0 too: open kit).",
    "Google Landmarks v2": "its pictures come from Wikimedia Commons, which allows no non-commercial licences: "
                           "they belong to the open or share-alike groups.",
    "Total-Text": "its new terms (2026) allow only non-commercial academic research, and research by or for a company "
                  "needs written confirmation first (the owner works through a company).",
    "VizWiz Image Quality Issues": "still no licence or terms written for its labels (photos CC BY 4.0); kept in "
                                   "more_sources.NEEDS_LICENCE_CHECK.",
    "Rico (Screen2Words, Widget Captioning)": "the words are CC BY 4.0, but the Rico screenshots have no licence or "
                                              "terms written anywhere (interactionmining.org); left out until they do.",
    "Visual Genome (all photos)": "its photo server (cs.stanford.edu) fails certificate checks; the open kit already "
                                  "uses its COCO photos.",
    "MIT Indoor 67": "research only, but the download (groups.csail.mit.edu) is gone (404).",
    "Stanford Cars, Stanford Online Products, FigureQA, GroZi-120": "their download sites do not answer.",
    "SVHN house numbers": "non-commercial use only, but its labels are MATLAB v7.3 files that need an extra library "
                          "(h5py) the kit does not install.",
    "SKU-110K, Products-10K": "shelf boxes or product numbers only, no names or descriptions to learn from.",
    "Oxford 102 Flowers": "no licence or terms written, and its files do not name the flowers.",
    "SemArt": "its download page (Aston research data) gives no terms that could be checked.",
    "DVQA, SlideVQA": "DVQA's charts and questions are made by a program (and on Google Drive only); SlideVQA's "
                      "slides must be scraped from SlideShare.",
    "WikiArt": "no official download; the artworks are largely in copyright.",
    "ExpW facial expressions": "on Google Drive and Baidu only, with no terms written.",
    "CK+48 (Zenodo 18983820)": "a re-upload of CK+ under CC BY that CK+'s owners did not give (CK+ needs an agreement).",
    "COCO photos under CC BY-SA, CC BY-ND or US-government licences": "not non-commercial licences; left for the "
                                                                      "groups they belong to.",
}


# ----------------------------------------------------------------- the table

COCO_NC_PHOTOS = "photos from COCO under CC BY-NC, CC BY-NC-SA or CC BY-NC-ND 2.0 (each photo's own Flickr licence)"
HAM_TERMS = "https://doi.org/10.7910/DVN/DBW86T"

PERSONAL_SOURCES = [
    # ---- noncommercial
    Source("ham10000", "HAM10000: skin spots under a skin magnifier, with the diagnosis (personal use)",
           "CC BY-NC 4.0 (Harvard Dataverse, doi:10.7910/DVN/DBW86T, version 4)",
           "HAM10000 (Tschandl, Rosendahl and Kittler, 2018), Harvard Dataverse, CC BY-NC 4.0, "
           "https://doi.org/10.7910/DVN/DBW86T", "noncommercial", 2000, 20, prepare_ham10000,
           "up to 600 MB of pictures", content="medical", terms=HAM_TERMS,
           terms_summary="CC BY-NC 4.0: free to use and adapt with credit, but not for commercial purposes."),
    Source("isic_nc", "ISIC Archive: skin spots under CC BY-NC, with the diagnosis (personal use)",
           "CC BY-NC 4.0, each picture's own licence (api.isic-archive.com)",
           "ISIC Archive (International Skin Imaging Collaboration), pictures under CC BY-NC, contributors as named "
           "in each record, https://www.isic-archive.com", "noncommercial", 3000, 20, prepare_isic_nc,
           "up to 1.5 GB of pictures", content="medical",
           terms="https://api.isic-archive.com/terms-of-use/",
           terms_summary="Each picture's own licence, here CC BY-NC: use with credit, not for commercial purposes."),
    Source("scin", "SCIN: skin problems photographed by adults with their phones (personal use)",
           "SCIN Data Use License (github.com/google-research-datasets/scin/blob/main/LICENSE)",
           "SCIN: Skin Condition Image Network (Google Research and Stanford Medicine, 2024), SCIN Data Use License, "
           "https://github.com/google-research-datasets/scin", "noncommercial", 1500, 15, prepare_scin,
           "up to 1 GB of photos", content="medical",
           terms="https://github.com/google-research-datasets/scin/blob/main/LICENSE",
           terms_summary="Google's own licence, like CC BY: use and adapt with credit, but never try to find out "
                         "who the people in the photos are. Not a standard open licence, so it is kept for personal "
                         "use here."),
    Source("coco_nc", "COCO: everyday photos under non-commercial licences, one sentence each (personal use)",
           "CC BY 4.0 descriptions (cocodataset.org); " + COCO_NC_PHOTOS,
           "COCO Captions (Chen et al., 2015), CC BY 4.0, https://cocodataset.org; Flickr photos under CC BY-NC, "
           "CC BY-NC-SA or CC BY-NC-ND 2.0", "noncommercial", 6000, 20, prepare_coco_nc, "up to 1 GB of photos",
           terms="https://cocodataset.org/#termsofuse",
           terms_summary="The descriptions are CC BY 4.0; the photos keep their Flickr licences, here only "
                         "non-commercial ones (CC BY-NC, BY-NC-SA or BY-NC-ND 2.0)."),
    Source("vqav2_nc", "VQA v2: questions about everyday photos under non-commercial licences (personal use)",
           "CC BY 4.0 (visualqa.org); " + COCO_NC_PHOTOS,
           "VQA v2 (Goyal et al., 2017), CC BY 4.0, https://visualqa.org; " + COCO_NC_PHOTOS, "noncommercial",
           8000, 20, prepare_vqav2_nc, "up to 1.5 GB of photos", terms="https://visualqa.org/terms.html",
           terms_summary="Questions and answers CC BY 4.0; the photos are COCO photos under non-commercial Flickr "
                         "licences."),
    Source("ln_coco_nc", "Localized Narratives: everyday photos under non-commercial licences, described aloud "
                         "(personal use)",
           "CC BY 4.0 descriptions (google.github.io/localized-narratives); " + COCO_NC_PHOTOS,
           "Localized Narratives (Pont-Tuset et al., 2020), CC BY 4.0; " + COCO_NC_PHOTOS, "noncommercial",
           8000, 20, prepare_ln_coco_nc, "up to 1.5 GB of photos",
           terms="https://google.github.io/localized-narratives/",
           terms_summary="Descriptions CC BY 4.0; the photos are COCO photos under non-commercial Flickr licences."),
    Source("xfund", "XFUND: forms in seven languages, their title and filled-in fields (personal use)",
           "CC BY-NC-SA 4.0 (github.com/doc-analysis/XFUND)",
           "XFUND (Xu et al., 2022, Microsoft), CC BY-NC-SA 4.0, https://github.com/doc-analysis/XFUND",
           "noncommercial", 1000, 20, prepare_xfund, "up to 700 MB of form pictures",
           terms="https://github.com/doc-analysis/XFUND#license",
           terms_summary="CC BY-NC-SA 4.0: use with credit, not for commercial purposes, and anything made from it "
                         "keeps the same licence."),
    Source("scienceqa", "ScienceQA: school science questions about diagrams, maps and photos (personal use)",
           "CC BY-NC-SA 4.0 (github.com/lupantech/ScienceQA)",
           "ScienceQA (Lu et al., 2022), CC BY-NC-SA 4.0, https://scienceqa.github.io", "noncommercial", 3000, 20,
           prepare_scienceqa, "about 700 MB", terms="https://github.com/lupantech/ScienceQA#license",
           terms_summary="CC BY-NC-SA 4.0: use with credit, not for commercial purposes, and anything made from it "
                         "keeps the same licence."),
    Source("chartqa", "ChartQA: questions people asked about real charts (personal use)",
           "GPL-3.0 (huggingface.co/datasets/ahmed-masry/ChartQA); charts from Statista, Pew, Our World in Data and "
           "the OECD",
           "ChartQA (Masry et al., 2022), GPL-3.0, https://github.com/vis-nlp/ChartQA", "noncommercial", 3000, 20,
           prepare_chartqa, "about 1 GB", terms="https://huggingface.co/datasets/ahmed-masry/ChartQA",
           terms_summary="GPL-3.0, a copyleft licence: anything shared that is made from it must be shared under "
                         "GPL-3.0 too; the charts' own websites keep their rights. Kept for personal use here."),
    # ---- research
    Source("food101", "Food-101: 101 dishes (research terms; personal use)",
           "Research use: the photos belong to their Foodspotting authors; only scientific fair use is allowed "
           "(data.vision.ee.ethz.ch/cvl/datasets_extra/food-101)",
           "Food-101 (Bossard, Guillaumin and Van Gool, 2014), ETH Zurich; photos from Foodspotting",
           "research", 3000, 20, prepare_food101, "up to 700 MB",
           terms="https://huggingface.co/datasets/ethz/food101#licensing-information",
           terms_summary="ETH Zurich does not own the photos; any use beyond scientific fair use must be agreed "
                         "with each photo's owner."),
    Source("stanford_dogs", "Stanford Dogs: 120 dog breeds (research terms; personal use)",
           "ImageNet terms: non-commercial research and education only (image-net.org/download)",
           "Stanford Dogs (Khosla, Jayadevaprakash, Yao and Fei-Fei, 2011), from ImageNet, "
           "http://vision.stanford.edu/aditya86/ImageNetDogs/", "research", 2400, 20, prepare_stanford_dogs,
           "790 MB, once", terms="https://image-net.org/download.php",
           terms_summary="ImageNet's photos: for non-commercial research and educational use only; the photos "
                         "belong to their owners."),
    Source("fgvc_aircraft", "FGVC-Aircraft: 100 aircraft models (research terms; personal use)",
           "Non-commercial research only; the photographers keep their copyright "
           "(robots.ox.ac.uk/~vgg/data/fgvc-aircraft)",
           "FGVC-Aircraft (Maji et al., 2013), University of Oxford, photos by the aircraft spotters named on its "
           "page, https://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/", "research", 2000, 20, prepare_fgvc_aircraft,
           "2.7 GB, once", terms="https://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/",
           terms_summary="The photographers lent their photos exclusively for non-commercial research and keep "
                         "their copyright; any other use needs their permission."),
    Source("funsd", "FUNSD: noisy scanned forms, their title and filled-in fields (research terms; personal use)",
           "Non-commercial, research and educational use only (guillaumejaume.github.io/FUNSD/work)",
           "FUNSD (Jaume, Ekenel and Thiran, 2019), EPFL LTS5; forms from RVL-CDIP",
           "research", 199, 10, prepare_funsd, "17 MB, once", terms="https://guillaumejaume.github.io/FUNSD/work",
           terms_summary="For non-commercial, research and educational purposes only, by people aged 18 or over; "
                         "the scanned forms keep their own copyright."),
    Source("ai2d", "AI2D: school science diagrams with questions (research terms; personal use)",
           "AI2 licence for non-commercial use: academic, non-profit or government research "
           "(license.txt in ai2d-all.zip)",
           "AI2 Diagrams (Kembhavi et al., 2016), Allen Institute for AI, https://prior.allenai.org/projects/"
           "diagram-understanding", "research", 3000, 20, prepare_ai2d, "990 MB, once",
           terms="https://prior.allenai.org/projects/diagram-understanding",
           terms_summary="For academic, non-profit or government researchers only; not in a for-profit business; "
                         "never shared on or published."),
    Source("jaffe", "JAFFE: posed facial expressions, with the visible signs (research terms; personal use)",
           "Non-commercial scientific research only; never redistributed or posted (zenodo.org/records/14974867)",
           "JAFFE: The Japanese Female Facial Expression Dataset (Lyons, Kamachi and Gyoba, 1998), "
           "https://doi.org/10.5281/zenodo.14974867", "research", 213, 10, prepare_jaffe, "12 MB, once",
           terms="https://zenodo.org/records/14974867",
           terms_summary="Only for non-commercial scientific research; the photos must never be shared, posted or "
                         "shown publicly."),
]

# The personal-use collections whose rows suit a picture-making model: real photos with whole-picture descriptions
# that people wrote. Rows marked "child" are still left out there; skin pictures, forms, charts, diagrams,
# questions and faces never.
PERSONAL_PICTURE_MAKING_OK = {"coco_nc", "ln_coco_nc"}
