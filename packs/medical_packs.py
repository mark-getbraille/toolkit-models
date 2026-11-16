"""Pack builders for medical pictures, used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}.

The kit uses these packs only when the person training ticks "Include medical and anatomy pictures" (content
"medical" in training-kit/kit/sources.py).

Why: blind people meet medical pictures (a rash on their own arm photographed with a phone, an X-ray in a letter, a
figure in a health article) and a describing model should say plainly what is visible, never sound sure about a
diagnosis, and send the person to a doctor.

Rules kept by every builder here:
  - Licence checked at the source, picture by picture where the source gives a licence per picture: CC0, public
    domain (US government works) or CC BY (credit kept). Never NC, ND, SA, research-only or credentialed sets.
  - Adults only where people are photographed: records under 18, or with no age in a collection that includes
    children, are left out (each builder says how it knows the age). The one exception is the childhood_illness
    pack, made at the owner's request so that a blind parent or carer can learn what a childhood rash looks like:
    close clinical pictures of one affected part of the body only, never an unclothed or whole child (see
    CHILD_NOT_SHOWN), for recognising illness only.
  - Nothing sexual, and no clinical photographs of the genitals, groin, buttocks or breasts (GENITAL_AREA).
  - Answers are written with fixed sentences from each source's own labels, captions and metadata (nothing is
    written by an AI model). A named condition is always "This looks like <condition> (<plain explanation>)." and
    every answer ends with DOCTOR ("Only a doctor can diagnose this.").

The packs (MEDICAL_PACKS):
  skin_lesion_photos  PAD-UFES-20 (Pacheco et al., Federal University of Espirito Santo, Brazil; Mendeley Data
                      zr7vgbcyr2, CC BY 4.0): skin spots photographed with smartphones, with the diagnosis, the body
                      site, the patient's age and what the patient said (itching, bleeding, growth). Age 18 or over.
  isic_skin           ISIC Archive (International Skin Imaging Collaboration): dermoscopy and clinical close-up
                      pictures of skin spots whose own licence is CC0 or CC BY (never CC BY-NC), with an
                      approximate age of 20 or more (the archive rounds ages to 5 years, so 20 means at least 18),
                      balanced across diagnoses.
  gi_endoscopy        HyperKvasir (Borgli et al., Simula and Baerum Hospital, Norway; OSF mh9sj, CC BY 4.0):
                      pictures from inside the gut taken during gastroscopies and colonoscopies, labelled by doctors
                      (landmarks, polyps, inflammation). No person is photographed (inside the body only).
  chest_xray          NIH ChestX-ray14 (NIH Clinical Center; "no restrictions on the use", with a link, the CVPR
                      2017 citation and the Clinical Center credited): chest X-rays with labels mined from the
                      reports, patient age 18 or over (from the data's own age column).
  case_report_figures Figures of published case reports in PubMed Central whose article licence is CC BY or CC0
                      (checked article by article in PMC's own metadata), single-picture figures that are clinical
                      photographs, scans, X-rays, endoscopy or microscope pictures, with the authors' caption. Only
                      articles whose title and abstract give the patient's age as 18 or over and mention no child.
  vet_case_figures    The same for veterinary case reports (animals: no age rule), CC BY or CC0 only.
  cdc_medical         CDC Public Health Image Library: photographs whose own copyright field says they are public
                      domain (never those marked "copyright protected"), showing a part of an adult's body with a
                      sign of illness; only captions that say the person is an adult (an age of 18 or more, "man",
                      "woman", "adult").
  childhood_illness   CDC Public Health Image Library, public-domain photographs only: close clinical pictures of
                      a childhood illness (chickenpox, measles, impetigo, ringworm, head lice and similar) on one
                      part of the body (face, arm, leg, hand, foot, back, chest, an eye, the scalp). For recognising
                      illness only.

    python packs/medical_packs.py isic_skin --limit 8      (prints a few rows: a quick check of one builder)

Rejected sources (checked November 2026) are listed in REJECTED below, with the reason.
"""

import concurrent.futures
import csv
import html
import io
import json
import random
import re
import sys
import time

from build_packs import session, clean, smaller, fetch_all, first_sentences, say, article  # noqa: F401
from food_packs import with_twins, listed, sentence, count_pictures

DOCTOR = "Only a doctor can diagnose this."
CHILD_DOCTOR = "Only a doctor can diagnose this; if a child seems unwell, contact a doctor."
DESCRIBE = "Describe this picture."
WHAT_SKIN = "What is this mark on the skin?"
WHAT_FIGURE = "What does this medical picture show?"

# Sources looked at and left out, with the reason (for the report and the next person).
REJECTED = {
    "PadChest": "CC BY-SA 4.0 (share-alike).",
    "MIMIC-CXR, CheXpert, VinDr-CXR, BRSET and other PhysioNet sets": "credentialed access or a data-use agreement.",
    "Zenodo re-uploads of VinDr-CXR and RSNA": "re-uploads under a licence the original owners did not give.",
    "RSNA and most Kaggle chest X-ray sets": "competition or research-only terms.",
    "Kermany chest X-rays (Mendeley rscbjbr9sj)": "CC BY 4.0 but all children aged 1 to 5.",
    "PAPILA fundus photos (figshare 14798004)": "GPL 3.0, not one of the allowed licences.",
    "Kvasir-Capsule": "CC BY 4.0, but its pictures are only on datasets.simula.no, whose certificate could not be "
                      "verified from the build machine; can be added later.",
    "ROCO, MedICaT, PMC-OA, PMC-15M": "derived from PubMed Central with mixed licences (MedICaT under its own "
                                      "terms; PMC-15M not released); case_report_figures reads PMC directly and "
                                      "checks each article's own licence instead.",
    "DermNet, HAM10000, Fitzpatrick17k, SCIN": "non-commercial or restricted terms.",
    "ISIC pictures under CC BY-NC": "non-commercial.",
    "CDC PHIL pictures marked 'copyright protected'": "copyrighted (each PHIL picture's own field is checked).",
}


# ----------------------------------------------------------------- shared filters and plain words

# Words that name a young person (adult packs leave the record out; childhood_illness uses them to know it is a
# child). Wide on purpose.
CHILD = re.compile(r"\b(child\w*|kids?|boys?|girls?|infan\w*|bab(y|ies)|toddler\w*|newborn\w*|neonat\w*|teen\w*|"
                   r"juvenile\w*|youths?|adolescen\w*|minors?|p(a)?ediatric\w*|schoolchild\w*|preschool\w*|"
                   r"fetus|fetal|foetus|foetal|prenatal|antenatal|\d+[- ](month|week|day)s?[- ]old|"
                   r"son|daughter|pupil|student)\b", re.I)

# Clinical photographs of these parts of the body are left out of every pack (the owner allows medical pictures,
# not intimate ones). Scans (CT, MRI, ultrasound, X-ray) of the same parts are kept in the adult packs.
GENITAL_AREA = re.compile(r"\b(genit\w*|penis|penile|scrot\w*|testic\w*|vulv\w*|vagin\w*|labia\w*|clitor\w*|"
                          r"peri-?ne\w*|perianal|anus|anal|rect(um|al)? (exam\w*)|groin|inguinal|pubic|pubis|"
                          r"buttock\w*|glute\w*|breasts?|nipples?|areola\w*|mammary|intimate|private parts?|"
                          r"nude|naked|unclothed|undressed|sexual\w*|sex(es)?|erotic\w*|porn\w*|intercourse)\b", re.I)

# Plain words for medical words in captions (the medical word stays in brackets so nothing is lost).
PLAIN_WORDS = [
    (r"\bmaculopapular\b", "flat and raised (maculopapular)"),
    (r"\bvesicular\b", "blistering (vesicular)"),
    (r"\bvesicles\b", "small fluid-filled blisters (vesicles)"),
    (r"\bpustules\b", "pus-filled bumps (pustules)"),
    (r"\bpustular\b", "pus-filled (pustular)"),
    (r"\bpapules\b", "small raised bumps (papules)"),
    (r"\bmacules\b", "flat spots (macules)"),
    (r"\berythematous\b", "reddened"),
    (r"\berythema\b", "redness (erythema)"),
    (r"\bcutaneous\b", "skin"),
    (r"\blesions\b", "spots or sores"),
    (r"\blesion\b", "spot or sore"),
    (r"\bexanthem\b", "widespread rash (exanthem)"),
    (r"\beruption\b", "rash"),
    (r"\bulcerations?\b", "open sores"),
    (r"\bedema\b|\boedema\b", "swelling"),
    (r"\bedematous\b|\boedematous\b", "swollen"),
    (r"\bconjunctival\b", "of the white of the eye (conjunctival)"),
    (r"\bvolar\b", "inner (palm-side)"),
    (r"\bventral\b", "front"),
    (r"\bdorsal\b", "back"),
    (r"\banterior\b", "front"),
    (r"\bposterior\b", "back"),
    (r"\bposterolateral\b", "back and side"),
    (r"\banterolateral\b", "front and side"),
    (r"\blateral\b", "side"),
    (r"\bproximal\b", "upper"),
    (r"\bdistal\b", "lower"),
    (r"\bpinna\b", "outer ear"),
    (r"\bpalpebral\b", "eyelid"),
]


def plain(text):
    """Text with medical words given in plain words (PLAIN_WORDS); case of the first letter kept."""
    for pattern, words in PLAIN_WORDS:
        text = re.sub(pattern, words, text, flags=re.I)
    return text


AGE = re.compile(r"\b(\d{1,3})[- ](year|yr)s?[- ]old\b|\baged (\d{1,3})\b|\b(\d{1,3}) ?(?:years?|yrs?) of age\b", re.I)


def ages(text):
    """The ages in years a text gives ("a 45-year-old man", "aged 70")."""
    return [int(next(g for g in m.groups() if g and g.isdigit())) for m in AGE.finditer(text or "")]


def adult_only(*texts):
    """(True, age) when the texts give at least one age, every age is 18 or more, and no word names a child;
    otherwise (False, None)."""
    text = " ".join(clean(t) for t in texts if t)
    found = ages(text)
    if not found or min(found) < 18 or CHILD.search(text):
        return False, None
    return True, found[0]


SEX = re.compile(r"\b(man|male|gentleman|woman|female|lady)\b", re.I)


def sex_of(text):
    """ "man", "woman" or "person" from the word after an age ("a 45-year-old woman")."""
    m = SEX.search(text or "")
    return {"man": "man", "male": "man", "gentleman": "man", "woman": "woman", "female": "woman",
            "lady": "woman"}[m.group(1).lower()] if m else "person"


def an_age(age):
    """ "a" or "an" before a number said aloud ("an 18-year-old", "an 80-year-old", "a 45-year-old")."""
    return "an" if str(age).startswith("8") or str(age) in ("11", "18") or str(age).startswith("18") else "a"


def who_with_age(age, sex):
    """ "a 45-year-old woman", "an 80-year-old man", "a 30-year-old person"."""
    return f"{an_age(age)} {age}-year-old {sex or 'person'}"


def looks_like(name, explanation):
    """The fixed sentence for a named condition: "This looks like X (explanation)." """
    return f"This looks like {name} ({explanation})." if explanation else f"This looks like {name}."


def safe_name(text):
    """A file-name-safe version of a record identifier."""
    return re.sub(r"[^\w.-]+", "_", str(text))[:80]


# ----------------------------------------------------------------- PAD-UFES-20 (smartphone skin photos)

PAD_DATASET = "https://data.mendeley.com/public-api/datasets/zr7vgbcyr2"
PAD_CREDIT = "PAD-UFES-20 (Pacheco, Lima, Salomao et al., Federal University of Espirito Santo), Mendeley Data " \
             "zr7vgbcyr2, https://doi.org/10.17632/zr7vgbcyr2.1, CC BY 4.0"
PAD_DIAGNOSES = {
    "BCC": ("a basal cell carcinoma", "a common skin cancer that grows slowly"),
    "SCC": ("a squamous cell carcinoma", "a skin cancer that should be treated early"),
    "ACK": ("an actinic keratosis", "a rough, scaly patch caused by years of sun, which can sometimes turn into "
                                    "skin cancer"),
    "SEK": ("a seborrheic keratosis", "a harmless, wart-like growth that is common in older people"),
    "NEV": ("a mole", "a nevus, usually harmless"),
    "MEL": ("a melanoma", "a serious skin cancer"),
}
PAD_SITES = {"FACE": "face", "FOREARM": "forearm", "CHEST": "chest", "BACK": "back", "ARM": "arm", "NOSE": "nose",
             "HAND": "hand", "NECK": "neck", "THIGH": "thigh", "EAR": "ear", "ABDOMEN": "belly", "LIP": "lip",
             "SCALP": "scalp", "FOOT": "foot"}
PAD_REPORTED = (("itch", "it itches"), ("hurt", "it hurts"), ("grew", "it has grown"), ("changed", "it has changed"),
                ("bleed", "it has bled"))


def pad_answer(r):
    """The answer for one PAD-UFES-20 record: what the photo shows, what the patient said, the diagnosis."""
    name, explanation = PAD_DIAGNOSES[r["diagnostic"]]
    sex = {"MALE": "man", "FEMALE": "woman"}.get(r.get("gender", ""), "person")
    site = PAD_SITES[r["region"]]
    text = f"A close-up phone photo of a skin spot on the {site} of {who_with_age(int(r['age']), sex)}."
    try:
        d1, d2 = float(r.get("diameter_1") or 0), float(r.get("diameter_2") or 0)
    except ValueError:
        d1 = d2 = 0
    if d1 and d2:
        text += f" It is about {d1:g} by {d2:g} mm."
    if r.get("elevation") == "True":
        text += " It is raised above the skin."
    said = [words for key, words in PAD_REPORTED if r.get(key) == "True"]
    if said:
        text += f" The person said that {listed(said)}."
    return f"{text} {looks_like(name, explanation)} {DOCTOR}"


def build_skin_lesion_photos(limit):
    """The skin_lesion_photos pack: [(name, JPEG, row)]. Reads metadata.csv, keeps adults (age 18 or more; 39 of
    2,298 photos are of children and are left out), then takes the chosen photos out of the three image zips
    (about 1.2 GB each) piece by piece over HTTP, without downloading the zips."""
    from world_life_packs import remote_zip
    s = session()
    files = {f["filename"]: f["content_details"]["download_url"] for f in s.get(PAD_DATASET, timeout=60).json()["files"]}
    table = s.get(files["metadata.csv"], timeout=120).content.decode("utf-8-sig")
    records = [r for r in csv.DictReader(io.StringIO(table))
               if r.get("age", "").isdigit() and int(r["age"]) >= 18 and r["diagnostic"] in PAD_DIAGNOSES
               and r["region"] in PAD_SITES]
    say(f"PAD-UFES-20: {len(records)} photos of adults")
    random.Random(61).shuffle(records)
    # Rarer diagnoses first in turn, so melanoma and moles are not crowded out by the many carcinomas.
    by_kind = {}
    for r in records:
        by_kind.setdefault(r["diagnostic"], []).append(r)
    chosen, queues = [], [q for _, q in sorted(by_kind.items())]
    while queues and len(chosen) < limit:
        for q in list(queues):
            if len(chosen) < limit:
                chosen.append(q.pop())
            if not q:
                queues.remove(q)
    wanted = {r["img_id"]: r for r in chosen}
    out = []
    for name, url in files.items():
        if not name.endswith(".zip") or len(out) >= len(wanted):
            continue
        z = remote_zip(url, s)
        for info in z.infolist():
            r = wanted.get(info.filename.rsplit("/", 1)[-1])
            if not r:
                continue
            data = smaller(z.read(info))
            if data:
                out.append((f"pad-{r['img_id'].rsplit('.', 1)[0]}.jpg", data,
                            {"question": WHAT_SKIN, "answer": pad_answer(r), "credit": PAD_CREDIT}))
    random.Random(62).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- ISIC Archive (dermoscopy and close-ups)

ISIC = "https://api.isic-archive.com/api/v2/images/"
ISIC_BASE = '(copyright_license:CC-0 OR copyright_license:CC-BY) AND age_approx:[20 TO *] AND ' \
            '(image_type:dermoscopic OR image_type:"clinical: close-up")'
# The diagnoses used, each with its plain words (diagnosis_3 in the archive).
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
    "Fibroepithelial polyp": ("a skin tag (fibroepithelial polyp)", "a harmless soft growth"),
    "Dermatofibroma": ("a dermatofibroma", "a harmless firm bump in the skin"),
    "Verruca": ("a wart (verruca)", "a harmless growth caused by a virus"),
    "Hemangioma": ("a hemangioma", "a harmless growth of small blood vessels"),
    "Atypical melanocytic neoplasm": ("an unusual mole (atypical melanocytic neoplasm)", "doctors watch or remove "
                                                                                         "these to be safe"),
    "Scar": ("a scar", ""),
    "Angiokeratoma": ("an angiokeratoma", "a harmless dark red or purple spot of small blood vessels"),
    "Neurofibroma": ("a neurofibroma", "a harmless soft growth on a nerve"),
}
ISIC_TYPES = {"dermoscopic": "A dermoscopy picture (a close-up taken through a skin magnifier with a light)",
              "clinical: close-up": "A close-up photo"}
ISIC_INTIMATE = re.compile(r"genit|scrot|mons|areola|perianal|perigenital|inguinal|buttock|suprapubic|anogenital",
                           re.I)


def isic_site(clinical):
    """The most exact body site of an ISIC record in plain words ("the upper back", "the cheek"), or ""."""
    for key in ("anatom_site_5", "anatom_site_4", "anatom_site_3", "anatom_site_2", "anatom_site_1"):
        site = clean(clinical.get(key))
        if site:
            site = site.lower().replace("anterior trunk", "front of the body").replace(
                "posterior trunk", "back").replace("upper extremity", "arm").replace(
                "lower extremity", "leg").replace("anterior ", "front of the ").replace("posterior ", "back of the ")
            return "the " + re.sub(r"^the ", "", site)
    return ""


def isic_answer(record):
    """The answer for one ISIC record."""
    clinical = record["metadata"]["clinical"]
    kind = ISIC_TYPES[record["metadata"]["acquisition"]["image_type"]]
    site = isic_site(clinical)
    sex = {"male": "man", "female": "woman"}.get(clinical.get("sex"), "person")
    text = f"{kind} of a skin spot" + (f" on {site}" if site else "") + \
        f" of an adult {sex} aged about {clinical['age_approx']}."
    name, explanation = ISIC_DIAGNOSES[clinical["diagnosis_3"]]
    return f"{text} {looks_like(name, explanation)} {DOCTOR}"


def isic_page(s, query, url=None):
    """One page (up to 100 records) of an ISIC search, and the next page's address."""
    for attempt in range(4):
        try:
            r = s.get(url, timeout=120) if url else \
                s.get(ISIC + "search/", params={"query": query, "limit": 100}, timeout=120)
            if r.status_code == 200:
                data = r.json()
                return data.get("results") or [], data.get("next")
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(5 * (attempt + 1))
    return [], None


def build_isic_skin(limit):
    """The isic_skin pack: [(name, JPEG, row)]. For each diagnosis in ISIC_DIAGNOSES, asks the archive for adult
    pictures under CC0 or CC BY and takes an equal share (a diagnosis with fewer gives what it has, and the others
    share what is left), checking each record's own licence and age again."""
    s = session()
    share = max(2, limit // len(ISIC_DIAGNOSES) + 1)
    found = {}
    for diagnosis in ISIC_DIAGNOSES:
        query = f'{ISIC_BASE} AND diagnosis_3:"{diagnosis}"'
        records, url = [], None
        while len(records) < share * 3:
            page, url = isic_page(s, query, url)
            for r in page:
                clinical = r.get("metadata", {}).get("clinical", {})
                kind = r.get("metadata", {}).get("acquisition", {}).get("image_type")
                if r.get("copyright_license") not in ("CC-0", "CC-BY") or (clinical.get("age_approx") or 0) < 20 \
                        or kind not in ISIC_TYPES or clinical.get("diagnosis_3") != diagnosis \
                        or ISIC_INTIMATE.search(" ".join(str(v) for k, v in clinical.items() if "anatom" in k)):
                    continue
                records.append(r)
            if not url or not page:
                break
            time.sleep(0.5)
        random.Random(diagnosis).shuffle(records)
        found[diagnosis] = records
        say(f"ISIC {diagnosis}: {len(records)} usable")
    chosen, queues = [], [q for q in found.values() if q]
    while queues and len(chosen) < int(limit * 1.05) + 2:
        for q in list(queues):
            chosen.append(q.pop())
            if not q:
                queues.remove(q)
    items = []
    for r in chosen:
        licence = {"CC-0": "CC0", "CC-BY": "CC BY 4.0"}[r["copyright_license"]]
        credit = f"ISIC Archive, {r['isic_id']}, {clean(r.get('attribution')) or 'Anonymous'}, {licence}, " \
                 f"https://api.isic-archive.com/images/{r['isic_id']}/"
        items.append((f"isic-{r['isic_id']}.jpg", r["files"]["full"]["url"],
                      {"question": WHAT_SKIN, "answer": isic_answer(r), "credit": credit}))
    return fetch_all(items, workers=6)[:limit]


# ----------------------------------------------------------------- HyperKvasir (gut endoscopy)

HK_NODE = "https://api.osf.io/v2/nodes/mh9sj/files/osfstorage/"
HK_CREDIT = "HyperKvasir (Borgli, Thambawita, Smedsrud et al., Scientific Data 7, 283, 2020), OSF mh9sj, " \
            "https://osf.io/mh9sj/, CC BY 4.0"
UPPER = "A picture from inside the upper gut, taken with an endoscope (a camera on a thin tube passed through the " \
        "mouth)"
LOWER = "A picture from inside the large bowel, taken with a colonoscope (a camera on a thin tube)"
HK_FINDINGS = {
    "pylorus": (UPPER, "the stomach's exit into the small intestine (the pylorus)", "a normal pylorus", ""),
    "z-line": (UPPER, "the place where the food pipe meets the stomach (the Z-line)", "a normal Z-line", ""),
    "retroflex-stomach": (UPPER, "the top of the stomach, with the camera bent back to look up at where it came "
                                 "in", "a normal stomach", ""),
    "esophagitis-a": (UPPER, "the lower food pipe, with a few red streaks in its lining",
                      "mild oesophagitis", "inflammation of the food pipe, often from acid reflux"),
    "esophagitis-b-d": (UPPER, "the lower food pipe, with red, raw-looking streaks in its lining",
                        "oesophagitis", "inflammation of the food pipe, often from acid reflux"),
    "barretts": (UPPER, "the lower food pipe, where salmon-pink lining reaches up from the stomach",
                 "Barrett's oesophagus", "a change in the lining of the food pipe after years of acid reflux, which "
                                         "doctors check regularly"),
    "barretts-short-segment": (UPPER, "the lower food pipe, where a short tongue of salmon-pink lining reaches up "
                                      "from the stomach", "short-segment Barrett's oesophagus",
                               "a change in the lining of the food pipe after years of acid reflux"),
    "cecum": (LOWER, "the start of the large bowel (the caecum)", "a normal caecum", ""),
    "ileum": (LOWER, "the last part of the small intestine (the ileum)", "a normal ileum", ""),
    "retroflex-rectum": (LOWER, "the rectum, with the camera bent back to look towards the way out",
                         "a normal rectum", ""),
    "hemorrhoids": (LOWER, "the end of the rectum, with swollen bulges in its lining",
                    "haemorrhoids", "swollen veins at the end of the bowel, which are common"),
    "polyps": (LOWER, "the bowel lining, with a small lump growing from it", "a polyp",
               "a growth on the bowel lining, usually harmless, which doctors often remove because some can turn "
               "into cancer"),
    "ulcerative-colitis-grade-0-1": (LOWER, "the bowel lining, slightly red", "very mild ulcerative colitis",
                                     "a long-lasting inflammation of the large bowel"),
    "ulcerative-colitis-grade-1": (LOWER, "the bowel lining, red with fewer visible blood vessels",
                                   "mild ulcerative colitis", "a long-lasting inflammation of the large bowel"),
    "ulcerative-colitis-grade-1-2": (LOWER, "the bowel lining, red and swollen", "mild to moderate ulcerative "
                                                                                 "colitis",
                                     "a long-lasting inflammation of the large bowel"),
    "ulcerative-colitis-grade-2": (LOWER, "the bowel lining, red, swollen and fragile with small sores",
                                   "moderate ulcerative colitis", "a long-lasting inflammation of the large bowel"),
    "ulcerative-colitis-grade-2-3": (LOWER, "the bowel lining, red, swollen, with sores", "moderate to severe "
                                                                                          "ulcerative colitis",
                                     "a long-lasting inflammation of the large bowel"),
    "ulcerative-colitis-grade-3": (LOWER, "the bowel lining, badly inflamed with bleeding sores",
                                   "severe ulcerative colitis", "a long-lasting inflammation of the large bowel"),
    "dyed-lifted-polyps": (LOWER, "a polyp raised on a cushion of blue dye injected under it",
                           "a polyp being prepared for removal", "the blue dye lifts it away from the bowel wall"),
    "dyed-resection-margins": (LOWER, "a blue-stained patch where a polyp has just been cut away",
                               "the edges of a polyp removal", "doctors check them to make sure all of it is gone"),
    "bbps-0-1": (LOWER, "the bowel, with stool and cloudy liquid covering much of the lining",
                 "a poorly cleaned bowel", "the bowel preparation before the test did not clear it well enough to "
                                           "see everything"),
    "bbps-2-3": (LOWER, "the bowel lining, clean and clearly visible", "a well-cleaned bowel",
                 "the bowel preparation worked well"),
    "impacted-stool": (LOWER, "the bowel, with a large lump of stool blocking the view", "impacted stool",
                       "hard stool stuck in the bowel"),
}


def hk_answer(finding):
    """The answer for one HyperKvasir label."""
    where, what, name, explanation = HK_FINDINGS[finding]
    return f"{where}, showing {what}. {looks_like(name, explanation)} {DOCTOR}"


def osf_children(s, url):
    """The entries of one OSF folder (all pages, 100 at a time)."""
    out, url = [], url + ("&" if "?" in url else "?") + "page[size]=100"
    while url:
        for attempt in range(4):
            try:
                data = s.get(url, timeout=120).json()
                break
            except Exception:  # noqa: BLE001 - tried again
                time.sleep(5 * (attempt + 1))
        else:
            return out
        out += data.get("data") or []
        url = (data.get("links") or {}).get("next")
    return out


def build_gi_endoscopy(limit):
    """The gi_endoscopy pack: [(name, JPEG, row)]. Walks HyperKvasir's labelled-images folders on OSF (tract,
    kind, finding), takes an equal share of each finding (a rare finding gives what it has) and fetches each
    picture by its own OSF address."""
    s = session()
    root = next(x for x in osf_children(s, HK_NODE) if x["attributes"]["name"] == "labeled-images")
    folders = []
    for tract in osf_children(s, root["relationships"]["files"]["links"]["related"]["href"]):
        if tract["attributes"]["kind"] != "folder":
            continue
        for kind in osf_children(s, tract["relationships"]["files"]["links"]["related"]["href"]):
            for finding in osf_children(s, kind["relationships"]["files"]["links"]["related"]["href"]):
                if finding["attributes"]["name"] in HK_FINDINGS:
                    folders.append(finding)
    share = max(1, limit // len(folders) + 1)
    found = {}
    for folder in folders:
        name = folder["attributes"]["name"]
        pictures = [x for x in osf_children(s, folder["relationships"]["files"]["links"]["related"]["href"])
                    if x["attributes"]["name"].lower().endswith(".jpg")]
        random.Random(name).shuffle(pictures)
        found[name] = pictures
        say(f"HyperKvasir {name}: {len(pictures)} pictures")
    chosen, queues = [], [(n, q[:share * 4]) for n, q in sorted(found.items()) if q]
    while queues and len(chosen) < int(limit * 1.05) + 2:
        for entry in list(queues):
            name, q = entry
            x = q.pop()
            chosen.append((f"hyperkvasir-{x['attributes']['name']}", x["links"]["download"],
                           {"question": DESCRIBE, "answer": hk_answer(name), "credit": HK_CREDIT}))
            if not q:
                queues.remove(entry)
    return fetch_all(chosen, workers=4, pause=0.2)[:limit]


# ----------------------------------------------------------------- NIH ChestX-ray14

NIH_MIRROR = "https://huggingface.co/datasets/alkzar90/NIH-Chest-X-ray-dataset/resolve/main/data/"
NIH_CREDIT = "NIH Chest X-ray Dataset (ChestX-ray14), NIH Clinical Center (the data provider), " \
             "https://nihcc.app.box.com/v/ChestXray-NIHCC; Wang et al., ChestX-ray8, CVPR 2017. No restrictions " \
             "on use, with this attribution."
NIH_FINDINGS = {
    "Atelectasis": ("atelectasis", "part of a lung not fully filled with air"),
    "Cardiomegaly": ("cardiomegaly", "an enlarged heart"),
    "Effusion": ("a pleural effusion", "fluid around a lung"),
    "Infiltration": ("an infiltrate", "a hazy area in the lung, as from infection or fluid"),
    "Mass": ("a mass", "a lump larger than 3 cm"),
    "Nodule": ("a nodule", "a small round spot in a lung"),
    "Pneumonia": ("pneumonia", "a lung infection"),
    "Pneumothorax": ("a pneumothorax", "air outside the lung, which can make it collapse"),
    "Consolidation": ("consolidation", "part of a lung filled with fluid or tissue instead of air"),
    "Edema": ("pulmonary oedema", "fluid in the lungs"),
    "Emphysema": ("emphysema", "damaged air sacs in the lungs"),
    "Fibrosis": ("fibrosis", "scarring of the lungs"),
    "Pleural_Thickening": ("pleural thickening", "a thickened lining around a lung"),
    "Hernia": ("a hiatus hernia", "part of the stomach pushed up into the chest"),
}
NIH_VIEWS = {"PA": "taken from behind (a PA view, the usual standing chest X-ray)",
             "AP": "taken from the front (an AP view, often taken in bed)"}


def nih_answer(r):
    """The answer for one NIH record (labels mined from the radiology reports, about 90% right, so said
    carefully)."""
    sex = {"M": "man", "F": "woman"}.get(r["Patient Gender"], "person")
    text = f"A chest X-ray of {who_with_age(int(r['Patient Age']), sex)}, {NIH_VIEWS[r['View Position']]}."
    labels = [x for x in r["Finding Labels"].split("|") if x in NIH_FINDINGS]
    if not labels:
        return f"{text} Nothing unusual was noted in the report for this X-ray. {DOCTOR}"
    named = [f"{NIH_FINDINGS[x][0]} ({NIH_FINDINGS[x][1]})" for x in labels]
    return f"{text} This looks like it shows {listed(named)}. {DOCTOR}"


def build_chest_xray(limit):
    """The chest_xray pack: [(name, JPEG, row)]. Reads the NIH label table (Data_Entry_2017_v2020.csv), keeps
    patients aged 18 to 100 (the table has a few impossible ages), one X-ray per patient, about a third with no
    finding and the rest spread over the findings, then takes the pictures out of the twelve zips of the Hugging
    Face copy of NIH's files piece by piece (HTTP ranges), without downloading the zips."""
    from world_life_packs import remote_zip
    s = session()
    table = s.get(NIH_MIRROR + "Data_Entry_2017_v2020.csv", timeout=300).content.decode("utf-8-sig")
    rows = [r for r in csv.DictReader(io.StringIO(table))
            if r["Patient Age"].isdigit() and 18 <= int(r["Patient Age"]) <= 100 and r["View Position"] in NIH_VIEWS]
    random.Random(63).shuffle(rows)
    one_each, seen = [], set()
    for r in rows:
        if r["Patient ID"] not in seen:
            seen.add(r["Patient ID"])
            one_each.append(r)
    say(f"NIH ChestX-ray14: {len(rows)} X-rays of adults, {len(one_each)} patients")
    normal = [r for r in one_each if r["Finding Labels"] == "No Finding"]
    by_finding = {}
    for r in one_each:
        if r["Finding Labels"] != "No Finding":
            first = min(r["Finding Labels"].split("|"), key=lambda x: sum(1 for _ in by_finding.get(x, [])))
            by_finding.setdefault(first, []).append(r)
    chosen = normal[:limit // 3]
    queues = [q for _, q in sorted(by_finding.items())]
    while queues and len(chosen) < limit:
        for q in list(queues):
            if len(chosen) < limit:
                chosen.append(q.pop())
            if not q:
                queues.remove(q)
    wanted = {r["Image Index"]: r for r in chosen}
    out = []
    for number in range(1, 13):
        if len(out) >= len(wanted):
            break
        z = remote_zip(f"{NIH_MIRROR}images/images_{number:03d}.zip", s)
        for info in z.infolist():
            r = wanted.get(info.filename.rsplit("/", 1)[-1])
            if r:
                data = smaller(z.read(info))
                if data:
                    out.append((f"nih-{r['Image Index'].rsplit('.', 1)[0]}.jpg", data,
                                {"question": DESCRIBE, "answer": nih_answer(r), "credit": NIH_CREDIT}))
    random.Random(64).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- PubMed Central case reports (CC BY or CC0)

EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PMC_S3 = "https://pmc-oa-opendata.s3.amazonaws.com/"
PMC_FREE = {"CC BY": "CC BY", "CC0": "CC0"}       # PMC's license_code values allowed (never CC BY-NC, -SA, -ND)
HUMAN_QUERY = 'PUB_TYPE:"Case Reports" AND IN_PMC:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND ' \
              '(ABSTRACT:"year-old" OR TITLE:"year-old")'
VET_QUERY = 'IN_PMC:y AND (LICENSE:"cc by" OR LICENSE:"cc0") AND (PUB_TYPE:"Case Reports" OR TITLE:"case report") ' \
            'AND (TITLE:dog OR TITLE:dogs OR TITLE:cat OR TITLE:cats OR TITLE:canine OR TITLE:feline OR TITLE:horse ' \
            'OR TITLE:equine OR TITLE:cow OR TITLE:cattle OR TITLE:bovine OR TITLE:calf OR TITLE:sheep OR ' \
            'TITLE:goat OR TITLE:pig OR TITLE:rabbit OR TITLE:parrot OR TITLE:veterinary)'
# What kind of picture a caption describes, in order: the first that matches. ("" means: not a picture of a
# patient, for example a chart; left out.)
FIGURE_KINDS = [
    (r"\b(flow ?chart|flow ?diagram|timeline|graph|chart|kaplan|curve|schematic|diagram|illustration|algorithm|"
     r"pedigree|table|western blot|gel electrophoresis|sequenc\w+|phylogen\w*|PCR|cartoon|drawing)\b", ""),
    (r"\bdermoscop\w*", "a dermoscopy picture (a close-up taken through a skin magnifier with a light)"),
    (r"\b(fundus|fundoscop\w*|funduscop\w*|retinal photograph\w*)\b", "a photograph of the back of the eye (fundus)"),
    (r"\b(slit[- ]lamp)\b", "a slit-lamp photograph of the eye (taken with an eye doctor's microscope)"),
    (r"\b(optical coherence tomograph\w*|OCT)\b", "an OCT scan of the eye (a cross-section picture of the retina)"),
    (r"\b(endoscop\w*|colonoscop\w*|gastroscop\w*|bronchoscop\w*|laryngoscop\w*|cystoscop\w*|duodenoscop\w*|"
     r"esophagogastroduodenoscop\w*|EGD|sigmoidoscop\w*|arthroscop\w*|laparoscop\w*|hysteroscop\w*|"
     r"otoscop\w*|nasendoscop\w*)\b", "an endoscopy picture (taken with a camera on a thin tube inside the body)"),
    (r"\b(PET[- /]CT|PET|positron emission)\b", "a PET scan"),
    (r"\b(CT|computed tomograph\w*|CTA|HRCT|tomodensitometr\w*)\b", "a CT scan"),
    (r"\b(MRI|MR imag\w*|magnetic resonance|T1-weighted|T2-weighted|FLAIR|MRA)\b", "an MRI scan"),
    (r"\b(echocardiogra\w*|ultrasound|ultrasonograph\w*|sonograph\w*|doppler)\b", "an ultrasound picture"),
    (r"\b(angiogra\w*|venogra\w*|arteriogra\w*)\b", "an angiogram (an X-ray picture of blood vessels)"),
    (r"\b(x-?rays?|radiograph\w*|CXR|plain film|orthopantomogra\w*|panoramic radiograph\w*|mammogra\w*)\b",
     "an X-ray"),
    (r"\b(histolog\w*|histopatholog\w*|H&E|hematoxylin|haematoxylin|immunohistochem\w*|microscop\w*|"
     r"magnification|cytolog\w*|smear|stain(ed|ing)?|biopsy specimen|[x×] ?\d{2,4}\b)", "a microscope picture"),
    (r"\b(photograph\w*|clinical (photo|picture|image|appearance)\w*|photo|clinical image|gross (specimen|"
     r"appearance|examination)|intra-?operative\w*|appearance of|clinical view|close-up|on examination|"
     r"physical examination)\b", "a photograph"),
]
FIGURE_KINDS = [(re.compile(p, re.I), k) for p, k in FIGURE_KINDS]
# Captions of figures with several panels ("(A) ... (B) ...") or several pictures are left out: one picture, one
# caption.
MULTI_PANEL = re.compile(r"\(\s*[a-hA-H]\s*[),\-–]|\b[A-H]\s*[):.]\s|\b(panels?|left|right) (and|to)\b|"
                         r"\b[a-hA-H]\)|\b[A-H],\s*[A-H]\b|\(\s*[A-H]\s+and\s+[A-H]\s*\)", re.I)


def figure_kind(caption):
    """The kind of picture a caption describes ("a CT scan" ...), or "" (left out)."""
    for pattern, kind in FIGURE_KINDS:
        if pattern.search(caption):
            return kind
    return ""


def europe_pmc(s, query, want):
    """Europe PMC search results (core: title, abstract, authors, licence) for a query, pages of 1,000 (cursor),
    until want results or the end; newest first, so recent journals with good captions come first."""
    out, cursor = [], "*"
    while len(out) < want:
        for attempt in range(4):
            try:
                data = s.get(EUROPE_PMC, timeout=180, params={
                    "query": query, "format": "json", "resultType": "core", "pageSize": 1000,
                    "cursorMark": cursor, "sort": "P_PDATE_D desc"}).json()
                break
            except Exception:  # noqa: BLE001 - tried again
                time.sleep(10 * (attempt + 1))
        else:
            break
        results = (data.get("resultList") or {}).get("result") or []
        out += [r for r in results if r.get("pmcid")]
        if not results or data.get("nextCursorMark") in (None, cursor):
            break
        cursor = data["nextCursorMark"]
        time.sleep(1)
    return out


def pmc_article(s, pmcid):
    """(PMC metadata JSON, article XML text) from PMC's open-access bucket (the newest version), or (None, None)."""
    try:
        listing = s.get(PMC_S3, params={"list-type": "2", "prefix": f"metadata/{pmcid}.", "max-keys": 20},
                        timeout=60).text
        keys = re.findall(r"<Key>(metadata/[^<]+\.json)</Key>", listing)
        if not keys:
            return None, None
        meta = s.get(PMC_S3 + max(keys, key=lambda k: int(re.search(r"\.(\d+)\.json$", k).group(1))),
                     timeout=60).json()
        xml = s.get(meta["xml_url"].replace("s3://pmc-oa-opendata/", PMC_S3).split("?")[0], timeout=120).text
        return meta, xml
    except Exception:  # noqa: BLE001 - left out
        return None, None


def pmc_figures(xml, meta):
    """[(label, caption, picture address)] for the one-picture figures of an article."""
    media = {}
    for url in meta.get("media_urls") or []:
        name = url.split("?")[0].rsplit("/", 1)[-1]
        stem, ext = name.rsplit(".", 1) if "." in name else (name, "")
        if ext.lower() in ("jpg", "jpeg", "png", "gif", "webp", "tif", "tiff"):
            if stem not in media or ext.lower() in ("jpg", "jpeg"):      # a JPEG first when there are two
                media[stem] = url.replace("s3://pmc-oa-opendata/", PMC_S3).split("?")[0]
    out = []
    for fig in re.findall(r"<fig\b.*?</fig>", xml, re.S):
        graphics = re.findall(r'<graphic\b[^>]*xlink:href="([^"]+)"', fig)
        if len(graphics) != 1:
            continue
        stem = graphics[0].rsplit("/", 1)[-1]
        stem = stem.rsplit(".", 1)[0] if re.search(r"\.(jpe?g|png|gif|webp|tiff?)$", stem, re.I) else stem
        if stem not in media:
            continue
        label = clean(re.search(r"<label>(.*?)</label>", fig, re.S).group(1)) if "<label>" in fig else ""
        caption = re.search(r"<caption>(.*?)</caption>", fig, re.S)
        caption = clean(caption.group(1)) if caption else ""
        out.append((label, caption, media[stem]))
    return out


def case_rows(record, meta, label, caption, kind, who):
    """The row for one case-report figure: the kind of picture, whose, and the authors' caption."""
    licence = PMC_FREE[meta["license_code"]]
    authors = clean(record.get("authorString"))
    if len(authors) > 120:
        authors = authors[:authors.rfind(",", 0, 120)] + " et al."
    credit = f"{authors}, \"{clean(record.get('title')).rstrip('.')}\", {clean(meta.get('citation'))}, " \
             f"{label or 'figure'}, {licence}, https://pmc.ncbi.nlm.nih.gov/articles/{meta['pmcid']}/"
    caption = caption if caption.endswith((".", "!", "?")) else caption + "."
    answer = f"This is {kind} from a published case report about {who}. The authors' caption says: {caption} " \
             f"{DOCTOR}"
    return {"question": WHAT_FIGURE, "answer": answer, "credit": credit}


def case_items(query, want, adults, prefix):
    """(name, picture address, row) for figures of the case reports a Europe PMC query finds: licence checked in
    PMC's own metadata (CC BY or CC0 only); for people (adults=True) only articles whose title and abstract give an
    age of 18 or more and name no child; one-picture figures whose caption says what kind of picture it is, not
    multi-panel, and no clinical photographs of intimate areas."""
    s = session()
    records = europe_pmc(s, query, want * 3)
    say(f"Europe PMC: {len(records)} case reports found")
    random.Random(prefix).shuffle(records)

    def one(record):
        """The usable figures of one article ([] when none)."""
        text = f"{record.get('title', '')} {record.get('abstractText', '')}"
        who = "an animal"
        if adults:
            ok, age = adult_only(text)
            if not ok:
                return []
            m = re.search(rf"\b{age}[- ](?:year|yr)s?[- ]old\s+(\w+)", clean(text), re.I)
            who = who_with_age(age, sex_of(m.group(1) if m else ""))
        meta, xml = pmc_article(s, record["pmcid"])
        if not meta or meta.get("license_code") not in PMC_FREE or meta.get("is_retracted"):
            return []
        out = []
        for label, caption, url in pmc_figures(xml, meta):
            words = len(caption.split())
            if words < 6 or words > 120 or MULTI_PANEL.search(caption):
                continue
            kind = figure_kind(caption)
            if not kind or (adults and CHILD.search(caption)):
                continue
            if kind in ("a photograph", "an endoscopy picture (taken with a camera on a thin tube inside the body)") \
                    and GENITAL_AREA.search(caption):
                continue
            if GENITAL_AREA.search(caption) and re.search(r"\b(nude|naked|sexual\w*|erotic|porn\w*)\b", caption, re.I):
                continue
            name = f"{prefix}-{meta['pmcid']}-{safe_name(label or url.rsplit('/', 1)[-1])}.jpg"
            out.append((name, url, case_rows(record, meta, label, caption, kind, who)))
        return out[:3]                                     # at most three figures of one article

    items = []
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for start in range(0, len(records), 200):
            for got in pool.map(one, records[start:start + 200]):
                items += got
            say(f"  {min(start + 200, len(records))} articles read, {len(items)} usable figures")
            if len(items) >= want:
                break
    return items[:want]


def build_case_report_figures(limit):
    """The case_report_figures pack: [(name, JPEG, row)] from adult human case reports (CC BY or CC0)."""
    items = case_items(HUMAN_QUERY, int(limit * 1.1) + 2, True, "pmc")
    return fetch_all(items, workers=4, pause=0.1)[:limit]


def build_vet_case_figures(limit):
    """The vet_case_figures pack: [(name, JPEG, row)] from veterinary case reports (CC BY or CC0)."""
    items = case_items(VET_QUERY, int(limit * 1.1) + 2, False, "pmcvet")
    return fetch_all(items, workers=4, pause=0.1)[:limit]


# ----------------------------------------------------------------- CDC Public Health Image Library

PHIL = "https://wwwn.cdc.gov/phil/"
PHIL_PUBLIC = "Permission is not required for public domain images"   # the start of a public-domain item's field
PHIL_CREDIT = "CDC Public Health Image Library (PHIL), https://phil.cdc.gov, public domain"
# Not a clinical photograph of a person: left out.
PHIL_NOT_CLINICAL = re.compile(r"\b(micrograph\w*|microscop\w*|magnifi\w*|\d+x\b|TEM|SEM|electron|culture\w*|"
                               r"colon(y|ies)|agar|petri|slide|specimen|stain\w*|graph|chart|map|poster|"
                               r"illustration|drawing|diagram|cartoon|infographic|vial|syringe|vaccinat\w*|"
                               r"laborator\w*|team|staff|officer|worker|village|scene|campaign|clinic\b|hospital|"
                               r"crowd|mosquito\w*|tick|flea|mite|louse|lice|rat|rodent|virion\w*|bacteri\w* (cells|"
                               r"colonies)|scab|vector|larva\w*|egg)\b", re.I)
# The parts of the body a clinical photograph may show (one of them must be named).
BODY_PART = re.compile(r"\b(face|facial|forehead|cheeks?|chin|nose|lips?|mouth|tongue|palate|gums?|teeth|tooth|"
                       r"throat|tonsils?|eyes?|eyelids?|conjunctiva\w*|ears?|scalp|hair|neck|arms?|forearms?|"
                       r"elbows?|wrists?|hands?|palms?|fingers?|fingernails?|nails?|thumbs?|legs?|thighs?|knees?|"
                       r"shins?|calf|calves|ankles?|feet|foot|soles?|toes?|toenails?|heels?|back|shoulders?|"
                       r"chest|skin)\b", re.I)


def phil_field(page, field):
    """One field of a PHIL details page (lblDesc, lblCopyRight, lblContprov, lblPhotoCredit, lblCretDt)."""
    m = re.search(rf'<span id="{field}">(.*?)</span>\s*</td>', page, re.S)
    return clean(m.group(1)) if m else ""


def phil_search(s, keyword, most=400):
    """The PHIL ids a keyword search finds (photos only), all result pages (the site pages with postbacks)."""
    page_url = PHIL + "QuickSearch.aspx"

    def hidden(text):
        """The form's hidden fields."""
        return {m.group(1): html.unescape(m.group(2)) for m in
                re.finditer(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', text)}
    box = "ctl00$contentArea2$ucQuickSearch$txtQuickKeywords"
    try:
        text = s.get(page_url, timeout=60).text
        form = dict(hidden(text), **{box: keyword, "ctl00$contentArea2$ucQuickSearch$bntSearch": "Search",
                                     "ctl00$contentArea2$ucQuickSearch$chkTypes$chkTypes_0": "Photo"})
        text = s.post(page_url, data=form, timeout=120).text
    except Exception:  # noqa: BLE001 - nothing found
        return []
    ids, page = [], 1
    while len(ids) < most:
        ids += [p for p in dict.fromkeys(re.findall(r"Details\.aspx\?pid=(\d+)", text)) if p not in ids]
        links = re.findall(r"__doPostBack\(&#39;([^&]+dpImages[^&]+)&#39;,&#39;&#39;\)\">(\d+|\.\.\.)<", text)
        nxt = [t for t, n in links if n == str(page + 1)] or [t for t, n in links if n == "..."][-1:]
        if not nxt or page > 60:
            break
        try:
            text = s.post(page_url, data=dict(hidden(text), **{"__EVENTTARGET": nxt[0], "__EVENTARGUMENT": "",
                                                               box: keyword}), timeout=120).text
        except Exception:  # noqa: BLE001 - what was found so far
            break
        page += 1
        time.sleep(0.5)
    return ids


def phil_record(s, pid):
    """{"pid", "caption", "provider", "photographer", "year", "public", "picture"} for one PHIL item, or None."""
    for attempt in range(3):
        try:
            page = s.get(f"{PHIL}Details.aspx?pid={pid}", timeout=90).text
            break
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(5 * (attempt + 1))
    else:
        return None
    picture = re.search(r'(?:src|href)="([^"]*PHIL_Images/[^"]*_lores\.jpg)"', page, re.I)
    rights = phil_field(page, "lblCopyRight")
    provider, photographer = phil_field(page, "lblContprov"), phil_field(page, "lblPhotoCredit")
    public = rights.startswith(PHIL_PUBLIC) and "copyright protected" not in rights.lower() \
        and "©" not in f"{provider} {photographer}" and "copyright" not in f"{provider} {photographer}".lower()
    return {"pid": pid, "caption": phil_field(page, "lblDesc"), "provider": provider, "photographer": photographer,
            "year": phil_field(page, "lblCretDt"), "public": public,
            "picture": re.sub(r"(?<!:)/{2,}", "/", picture.group(1)) if picture else ""}


LEAD_IN = re.compile(r"^(this|the|captured in \d{4}, this|in this|here,? (?:is|are)|these|shown here (?:is|are))\s+"
                     r"(\d{4}\s+|historic(al)?\s+)?(image|photograph|photo|picture|close-up image|close-up photograph)?"
                     r"\s*(was captured[^,]*,\s*and\s+)?(depict(s|ed)|show(s|ed)|reveal(s|ed)|present(s|ed)|"
                     r"highlight(s|ed)|illustrat(es|ed)|demonstrat(es|ed)|captur(es|ed)|is|was)?\s*", re.I)
CUT_AT = re.compile(r",?\s+(?:that|which)\s+(?:proved|turned out|was|were|had been)\b|,?\s+(?:due to|caused by|"
                    r"consistent with|associated with|attributed to|brought on by|diagnosed as|indicative of|"
                    r"characteristic of|typical of|as a result of|resulting from|secondary to|from a case of|"
                    r"in a case of|of a case of)\b|\.\s|;|,\s+(?:a|an)\s+\w+\s+(?:disease|infection|condition)\b",
                    re.I)


def phil_description(caption, condition_words):
    """A plain description of what a PHIL photograph shows, from its caption's first sentence: the lead-in ("This
    image depicted") and the part naming the cause ("due to chickenpox") are taken off, medical words given in
    plain words. "" when what is left still names the condition or is too short."""
    text = first_sentences(caption, 60).split(". ")[0]
    text = LEAD_IN.sub("", text).strip(" ,")
    text = CUT_AT.split(text)[0].strip(" ,.")
    text = re.sub(r"\bpatient[’']s\b", "person's", text)
    text = re.sub(r"\b(a|the) patient\b", r"\1 person", text)
    if len(text.split()) < 4 or condition_words.search(text):
        return ""
    return sentence(plain(text))


# Childhood illnesses (and conditions of the skin, eyes and scalp met in childhood), with the plain words.
CHILD_CONDITIONS = [
    (r"chickenpox|chicken pox|varicella(?! zoster virus \(vzv\), also known)", "chickenpox (varicella)",
     "a common virus infection that causes itchy spots that turn into blisters and then crust over"),
    (r"measles|rubeola", "measles", "a virus infection that causes a fever and a red, blotchy rash"),
    (r"rubella|german measles", "rubella (German measles)", "a mild virus infection with a pink rash"),
    (r"hand,? foot,? and mouth", "hand, foot and mouth disease", "a common virus infection with sores in the "
                                                                 "mouth and spots on the hands and feet"),
    (r"impetigo", "impetigo", "a common skin infection with crusted, golden-brown sores"),
    (r"eczema|atopic dermatitis", "eczema", "dry, itchy, inflamed skin"),
    (r"conjunctivitis|pink ?eye", "conjunctivitis (pink eye)", "inflammation of the clear layer over the white of "
                                                               "the eye"),
    (r"scarlet fever|scarlatina", "scarlet fever", "a throat infection with a rough, red rash"),
    (r"ringworm|tinea", "ringworm (tinea)", "a fungal skin infection that often makes a ring-shaped rash"),
    (r"head lice|pediculosis capitis|nits\b", "head lice", "tiny insects that live in the hair and lay eggs "
                                                          "(nits) on it"),
    (r"scabies", "scabies", "tiny mites that burrow in the skin and cause an itchy rash"),
    (r"insect bites?|bed ?bug bites?|flea bites?|mosquito bites?", "insect bites", "itchy red bumps where an insect "
                                                                                   "bit"),
    (r"mumps", "mumps", "a virus infection that makes the glands in front of the ears swell"),
    (r"erythema infectiosum|fifth disease|slapped cheek", "fifth disease (slapped cheek)",
     "a mild virus infection with bright red cheeks"),
    (r"roseola", "roseola", "a mild virus infection with a high fever and then a pink rash"),
    (r"molluscum", "molluscum contagiosum", "a harmless virus that causes small, pearly bumps"),
    (r"kawasaki", "Kawasaki disease", "an illness with fever and inflammation of blood vessels, which needs a "
                                      "doctor quickly"),
    (r"diphtheria", "diphtheria", "a serious throat infection, now rare where children are vaccinated"),
    (r"strep(tococcal)? (throat|pharyngitis)|tonsillitis", "a throat infection", "red, swollen throat and tonsils"),
    (r"cellulitis", "cellulitis", "a skin infection that makes the skin red, warm and swollen"),
    (r"herpes simplex|cold sores?|herpetic gingivostomatitis", "a cold sore (herpes simplex)", "a common virus that "
                                                                                                "causes small "
                                                                                                "blisters"),
    (r"thrush|oral candidiasis", "oral thrush", "a yeast infection that makes white patches in the mouth"),
    (r"warts?|verruca", "warts", "harmless growths caused by a virus"),
    (r"lyme|erythema migrans", "Lyme disease (erythema migrans)", "a tick-borne infection; the rash often looks "
                                                                  "like a bull's-eye"),
    (r"mpox|monkeypox", "mpox", "a virus infection that causes spots that turn into blisters"),
]
CHILD_CONDITIONS = [(re.compile(rf"\b({p})", re.I), name, why) for p, name, why in CHILD_CONDITIONS]
# Adult conditions met in the PHIL search (in addition to the childhood ones above, which adults get too).
ADULT_CONDITIONS = CHILD_CONDITIONS + [(re.compile(rf"\b({p})", re.I), name, why) for p, name, why in [
    (r"herpes zoster|shingles|zoster", "shingles (herpes zoster)", "a painful rash of blisters, usually on one side "
                                                                   "of the body, from the chickenpox virus waking up"),
    (r"leprosy|hansen", "leprosy (Hansen's disease)", "a slow bacterial infection of the skin and nerves, curable "
                                                      "with medicine"),
    (r"leishmaniasis", "cutaneous leishmaniasis", "a skin sore caused by a parasite spread by sand flies"),
    (r"buruli", "a Buruli ulcer", "a skin infection that causes a large painless sore"),
    (r"yaws", "yaws", "a bacterial skin infection of warm countries"),
    (r"sporotrichosis", "sporotrichosis", "a fungal skin infection, often from plant thorns"),
    (r"anthrax", "cutaneous anthrax", "a rare skin infection with a black scab"),
    (r"jaundice|icter", "jaundice", "yellowing of the skin or eyes, often from a liver problem"),
    (r"goiter|goitre", "a goitre", "a swelling of the thyroid gland in the neck"),
    (r"trachoma", "trachoma", "an eye infection that can scar the eyelid"),
    (r"filariasis|elephantiasis", "lymphatic filariasis (elephantiasis)", "a parasitic infection that makes a limb "
                                                                          "swell greatly"),
    (r"frostbite", "frostbite", "skin and tissue damaged by freezing"),
    (r"burns?\b", "a burn", ""),
    (r"dengue", "dengue", "a virus infection spread by mosquitoes, sometimes with a rash"),
    (r"rocky mountain spotted fever|spotted fever", "spotted fever", "a tick-borne infection with a spotted rash"),
    (r"pellagra", "pellagra", "a skin rash from lack of vitamin B3 (niacin)"),
    (r"psoriasis", "psoriasis", "a long-lasting skin condition with thick, scaly patches"),
    (r"vitiligo", "vitiligo", "patches of skin that have lost their colour"),
    (r"cancer|carcinoma|melanoma|tumou?r", "a skin growth that may be a cancer", ""),
    (r"keratitis|corneal ulcer", "keratitis", "inflammation of the clear front of the eye"),
]]
PHIL_ADULT_KEYWORDS = ("rash", "skin lesions", "shingles", "herpes zoster", "leprosy", "leishmaniasis", "Buruli ulcer",
                       "yaws", "sporotrichosis", "cutaneous anthrax", "jaundice", "goiter", "trachoma",
                       "lymphatic filariasis", "frostbite", "burns", "Lyme disease", "erythema migrans", "mpox",
                       "monkeypox", "cellulitis", "tinea", "scabies", "conjunctivitis", "dengue", "spotted fever",
                       "pellagra", "psoriasis", "measles", "impetigo", "warts", "oral lesions", "tongue", "eye",
                       "ulcer", "wound")
PHIL_CHILD_KEYWORDS = ("chickenpox", "varicella", "measles", "rubella", "hand foot and mouth", "impetigo", "eczema",
                       "conjunctivitis", "scarlet fever", "ringworm", "tinea capitis", "head lice", "scabies",
                       "insect bites", "mumps", "fifth disease", "erythema infectiosum", "roseola", "molluscum",
                       "Kawasaki", "diphtheria", "tonsillitis", "cellulitis", "herpes simplex", "thrush", "warts",
                       "child rash", "infant rash")
# Whole-body or intimate pictures of children are never used: any of these words in the caption leaves a picture out
# of childhood_illness (the owner's list, and more words that mean the same).
CHILD_NOT_SHOWN = re.compile(r"\b(nude|naked|nudity|unclothed|undressed|disrobed|bare|shirtless|genit\w*|groin|"
                             r"inguinal|diapers?|nappy|nappies|buttocks?|glute\w*|perine\w*|perianal|anus|anal|"
                             r"private parts?|bath\w*|full[- ]body|whole[- ]body|entire body|full[- ]length|"
                             r"whole child|entire child|torso|trunk|abdomen|abdominal|belly|stomach|pelvi\w*|"
                             r"hips?|thighs?|body|bodies|generali[sz]ed|widespread|all over|head to toe|"
                             r"(front|back|side|anterior|posterior|lateral|posterolateral|anterolateral|frontal) "
                             r"views? of (a|an|the|this) [\w-]*\s*(\d+[- ](year|month|week)[- ]old\s*)?"
                             r"(child|boy|girl|infant|baby|toddler|patient|person|youngster|individual)|"
                             r"smallpox|variola|vaccinia|chest|breast\w*)\b", re.I)
# A close picture of one allowed part of the body (owner: face, arm, leg, hand, foot, back or chest of a young
# child, an eye, the scalp). Back and chest pictures of children are left out by CHILD_NOT_SHOWN above to be safe
# unless the caption says it is a close view of the back.
CHILD_PART = re.compile(r"\b(face|facial|forehead|cheeks?|chin|nose|lips?|mouth|tongue|eyes?|eyelids?|"
                        r"conjunctiva\w*|ears?|scalp|hair|neck|arms?|forearms?|elbows?|wrists?|hands?|palms?|"
                        r"fingers?|fingernails?|thumbs?|legs?|knees?|shins?|calf|calves|ankles?|feet|foot|soles?|"
                        r"toes?|heels?|back|shoulders?)\b", re.I)
CHILD_EXCLUDED, CHILD_KEPT = [], []        # (pid, caption, reason) for the quick check


def phil_condition(caption, conditions):
    """(name, plain words, pattern) of the first condition a caption names, or None."""
    for pattern, name, why in conditions:
        if pattern.search(caption):
            return name, why, pattern
    return None


def all_condition_words(conditions):
    """One pattern matching any condition name (for phil_description)."""
    return re.compile("|".join(p.pattern for p, _, _ in conditions) + r"|\bvirus\b|\binfection\b|\bdisease\b", re.I)


def phil_credit(r):
    """The credit of one PHIL item."""
    who = r["provider"] + (f", photo by {r['photographer']}" if r["photographer"] else "")
    return f"{PHIL_CREDIT}, ID {r['pid']}, {who}" + (f", {r['year']}" if r["year"] else "") + \
        f", https://phil.cdc.gov/Details.aspx?pid={r['pid']}"


def phil_records(keywords, want, budget):
    """PHIL records for a list of keywords: ids from each search (in turn), then each item's details page; only
    public-domain items. Stops after budget details pages."""
    s = session()
    ids = []
    for keyword in keywords:
        found = phil_search(s, keyword)
        ids += [p for p in found if p not in ids]
        say(f"PHIL '{keyword}': {len(found)} photos ({len(ids)} in all)")
        time.sleep(0.5)
    random.Random(65).shuffle(ids)
    records = []
    with concurrent.futures.ThreadPoolExecutor(3) as pool:
        for start in range(0, min(len(ids), budget), 60):
            records += [r for r in pool.map(lambda p: phil_record(s, p), ids[start:start + 60])
                        if r and r["public"] and r["picture"] and r["caption"]]
            if len(records) >= want:
                break
    say(f"PHIL: {len(records)} public-domain records read")
    return records


def build_cdc_medical(limit):
    """The cdc_medical pack: [(name, JPEG, row)]. PHIL public-domain photographs of a sign of illness on an
    adult's body: the caption must say the person is an adult (an age of 18 or more, or "man", "woman", "adult")
    and name no child, show a part of the body, not be a microscope picture, a culture or a scene, and name no
    intimate area."""
    words = all_condition_words(ADULT_CONDITIONS)
    items = []
    for r in phil_records(PHIL_ADULT_KEYWORDS, int(limit * 3) + 20, int(limit * 6) + 60):
        caption = r["caption"]
        found = ages(caption)
        adult = (found and min(found) >= 18) or (not found and re.search(r"\b(man|woman|men|women|adult|elderly|"
                                                                          r"gentleman|lady)\b", caption, re.I))
        if not adult or CHILD.search(caption) or GENITAL_AREA.search(caption) or PHIL_NOT_CLINICAL.search(caption) \
                or not BODY_PART.search(caption) or re.search(r"\b(smallpox|variola|vaccinia)\b", caption, re.I):
            continue
        condition = phil_condition(caption, ADULT_CONDITIONS)
        text = phil_description(caption, words)
        if not text:
            continue
        answer = text + (" " + looks_like(*condition[:2]) if condition else "") + " " + DOCTOR
        items.append((f"phil-{r['pid']}.jpg", r["picture"], {"question": DESCRIBE, "answer": answer,
                                                              "credit": phil_credit(r)}))
        if len(items) >= int(limit * 1.05) + 2:
            break
    say(f"CDC PHIL adult medical: {len(items)} usable")
    return fetch_all(items, workers=3, pause=0.3)[:limit]


def child_reason(caption):
    """Why a PHIL caption is left out of childhood_illness ("" when it is kept)."""
    bad = CHILD_NOT_SHOWN.search(caption)
    if bad:
        return f"not shown: {bad.group(0)}"
    if PHIL_NOT_CLINICAL.search(caption) and not re.search(r"\b(head lice|nits)\b", caption, re.I):
        return f"not a clinical photo: {PHIL_NOT_CLINICAL.search(caption).group(0)}"
    if not CHILD_PART.search(caption):
        return "no single part of the body named"
    if not phil_condition(caption, CHILD_CONDITIONS):
        return "no childhood illness named"
    return ""


def build_childhood_illness(limit):
    """The childhood_illness pack: [(name, JPEG, row)]. For recognising illness only. PHIL public-domain
    photographs of a childhood illness on one part of the body; every caption that mentions an unclothed or whole
    child, an intimate area, a bath, nappies, the torso or a whole-body view is left out (CHILD_NOT_SHOWN), and so
    are microscope pictures, scenes and old smallpox pictures. The answer describes the sign plainly, names the
    illness carefully and ends with CHILD_DOCTOR."""
    words = all_condition_words(CHILD_CONDITIONS)
    items = []
    for r in phil_records(PHIL_CHILD_KEYWORDS, int(limit * 4) + 30, int(limit * 8) + 80):
        caption = r["caption"]
        reason = child_reason(caption)
        if not reason:
            text = phil_description(caption, words)
            if not text:
                reason = "the caption gives no plain description apart from the illness"
        if reason:
            CHILD_EXCLUDED.append((r["pid"], caption[:160], reason))
            continue
        name, why, _ = phil_condition(caption, CHILD_CONDITIONS)
        answer = f"{text} {looks_like(name, why)} {CHILD_DOCTOR}"
        CHILD_KEPT.append((r["pid"], caption[:160], name))
        items.append((f"phil-child-{r['pid']}.jpg", r["picture"],
                      {"question": DESCRIBE, "answer": answer, "credit": phil_credit(r)}))
        if len(items) >= int(limit * 1.05) + 2:
            break
    say(f"CDC PHIL childhood illness: {len(items)} usable, {len(CHILD_EXCLUDED)} left out")
    return fetch_all(items, workers=3, pause=0.3)[:limit]


# ----------------------------------------------------------------- the packs

MEDICAL_PACKS = {
    "skin_lesion_photos": (build_skin_lesion_photos,
                           "PAD-UFES-20: a skin lesion dataset composed of patient data and clinical images "
                           "collected from smartphones (Andre G. C. Pacheco, Gustavo R. Lima, Amanda S. Salomao et "
                           "al., Federal University of Espirito Santo, Brazil), Mendeley Data zr7vgbcyr2, "
                           "https://doi.org/10.17632/zr7vgbcyr2.1, CC BY 4.0 "
                           "(https://creativecommons.org/licenses/by/4.0/). Adults (18 or over) only; photos made "
                           "smaller; answers written from the data's diagnosis, body site and patient answers."),
    "isic_skin": (build_isic_skin, "ISIC Archive, International Skin Imaging Collaboration, "
                                   "https://www.isic-archive.com: only pictures whose own licence is CC0 or CC BY 4.0 "
                                   "(never CC BY-NC), each credited below with its contributor; adults only "
                                   "(approximate age 20 or more); answers written from the archive's diagnosis, "
                                   "body site and age."),
    "gi_endoscopy": (build_gi_endoscopy, "HyperKvasir (Hanna Borgli, Vajira Thambawita, Pia H. Smedsrud et al., "
                                         "'HyperKvasir, a comprehensive multi-class image and video dataset for "
                                         "gastrointestinal endoscopy', Scientific Data 7, 283, 2020), "
                                         "https://osf.io/mh9sj/, CC BY 4.0. Answers written from its doctors' "
                                         "labels."),
    "chest_xray": (build_chest_xray, "NIH Chest X-ray Dataset (ChestX-ray14). Data provider: NIH Clinical Center, "
                                     "https://nihcc.app.box.com/v/ChestXray-NIHCC. Citation: Xiaosong Wang, Yifan "
                                     "Peng, Le Lu, Zhiyong Lu, Mohammadhadi Bagheri, Ronald Summers, 'ChestX-ray8: "
                                     "Hospital-scale Chest X-ray Database and Benchmarks on Weakly-Supervised "
                                     "Classification and Localization of Common Thorax Diseases', IEEE CVPR 2017. "
                                     "The NIH states there are no restrictions on the use of the images, with this "
                                     "link, citation and acknowledgement. Pictures read from the copy at "
                                     "https://huggingface.co/datasets/alkzar90/NIH-Chest-X-ray-dataset. Adults (18 "
                                     "or over) only; labels were mined from reports by software and may be wrong."),
    "case_report_figures": (build_case_report_figures,
                            "Figures from case reports in PubMed Central (https://pmc.ncbi.nlm.nih.gov), each "
                            "article's licence checked in PMC's open-access metadata: CC BY or CC0 only, each figure "
                            "credited below with its authors, article and licence. Adult patients only (age 18 or "
                            "over in the title or abstract). The captions are the authors' own."),
    "vet_case_figures": (build_vet_case_figures,
                         "Figures from veterinary case reports in PubMed Central (https://pmc.ncbi.nlm.nih.gov), "
                         "each article's licence checked in PMC's open-access metadata: CC BY or CC0 only, each "
                         "figure credited below with its authors, article and licence. The captions are the "
                         "authors' own."),
    "cdc_medical": (build_cdc_medical, "CDC Public Health Image Library (PHIL), https://phil.cdc.gov: public-domain "
                                       "photographs only (each item's copyright field checked; items marked "
                                       "'copyright protected' are left out), credited below with CDC and the "
                                       "photographer where known, as CDC asks. Adults only (the caption says so)."),
    "childhood_illness": (build_childhood_illness,
                          "FOR RECOGNISING ILLNESS ONLY: close clinical pictures of childhood illnesses, so that a "
                          "blind parent or carer can learn what a rash or sign looks like. CDC Public Health Image "
                          "Library (PHIL), https://phil.cdc.gov: public-domain photographs only (each item's "
                          "copyright field checked), credited below with CDC and the photographer where known. "
                          "Only pictures of one part of the body (face, arm, leg, hand, foot, back, an eye, the "
                          "scalp); any picture whose caption mentions an unclothed or whole child, an intimate "
                          "area, a nappy or a bath is left out."),
}

# How many pictures a full build takes from each collection (about what each offers after the checks, November
# 2026).
MEDICAL_LIMITS = {
    "skin_lesion_photos": 2259,      # every adult photo
    "isic_skin": 12000,              # of about 75,000 adult CC0 or CC BY pictures, balanced over 20 diagnoses
    "gi_endoscopy": 8000,            # of 10,662 labelled pictures, balanced over 23 findings
    "chest_xray": 8000,              # of about 27,000 adult patients, one X-ray each
    "case_report_figures": 20000,    # of about 200,000 CC BY or CC0 case reports
    "vet_case_figures": 3000,
    "cdc_medical": 600,
    "childhood_illness": 300,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing); for
    childhood_illness also five captions the filter left out and five it kept."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one medical pack builder.")
    parser.add_argument("key", choices=sorted(MEDICAL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    started = time.time()
    entries = MEDICAL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, in {time.time() - started:.0f} s")
    if args.key == "childhood_illness":
        say("Left out by the filter, for example:")
        for pid, caption, reason in random.Random(1).sample(CHILD_EXCLUDED, min(5, len(CHILD_EXCLUDED))):
            say(f"  PHIL {pid}: {caption}  ({reason})")
        say("Kept, for example:")
        for pid, caption, name in CHILD_KEPT[:5]:
            say(f"  PHIL {pid}: {caption}  ({name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
