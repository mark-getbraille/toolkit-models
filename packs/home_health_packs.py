"""Picture packs for HOME HEALTH CARE: first-aid supplies and first-aid skills (CPR, abdominal thrusts, the recovery
position), home treatment things (oral rehydration, calamine lotion, heating pads, compression stockings, catheters),
dental care products and appliances, eye care (magnifiers, reading glasses and bifocals, contact lenses and their
cases, eye charts), birth supplies and drawings, skin conditions with dermatologists' labels
(Google's SCIN), and dental X-rays with the teeth they show (DenPAR). Used by build_packs.py in the same way as its
own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]. The limit counts
pictures.

The owner's requests of 2026-11-22 (home health care: first aid in depth, home treatment, long-term conditions, home
nursing, dental care, midwifery and postpartum care, eye care). Already packs, and not asked again here
(packs/test_home_health.py checks every Commons category and Open Images label): medicines, pills, eye drops and
medicine labels, medical instruments and supplies (tourniquets, bandages, cervical collars, gloves, auto-injectors,
naloxone, blood pressure cuffs, glucose meters, insulin pens, inhalers, nebulisers, pill organisers, pulse
oximeters), AEDs and first aid kits, home tests, wheelchairs, walkers and white canes, toothbrushes, toothpaste,
floss and mouthwash, plain spectacles and sunglasses (med_vet_packs, medication_label_packs, health_test_packs,
events_safety_packs, disability_packs, home_packs), and birth, breastfeeding, midwifery, kangaroo care and newborn
photos (medical_packs.birth_and_feeding, which already keeps only respectful care scenes).

Answers say only what the source says (a Commons category's name with a plain line written here, an Open Images
label people confirmed, a dataset's own labels); NEVER a diagnosis. Every answer ends with a note:
  EMERGENCY_NOTE  first aid, home care and skin: "In an emergency, call 911 (or your local emergency number). This is
                  general information, not medical training or a diagnosis; ask a doctor, nurse or pharmacist."
  DENTAL_NOTE     dental: see a dentist today for a knocked-out tooth, a swollen face or a bad toothache; 911 in an
                  emergency; not a diagnosis, ask your dentist.
  EYE_NOTE        eyes: sudden vision loss, flashes with a curtain, a chemical splash or an eye injury is an
                  emergency; not a diagnosis, ask your eye doctor.
  BIRTH_NOTE      pregnancy, birth and newborn supplies: 911 in an emergency; not medical advice or a diagnosis, ask
                  your midwife or doctor.

People: the supply, dental and eye packs show things and drawings (files whose words name a child are left
out). Two packs show people and are describing only (HOME_HEALTH_BODILY_KEYS, added to the kit's
PEOPLE_AND_BODILY_PACK_KEYS): commons_first_aid_skills (adults doing CPR on each other or on manikins) and
scin_skin_conditions (rows marked "content": "medical").

The packs (Commons files CC0, public domain or CC BY; Open Images labels CC BY 4.0; the two datasets as named):
  commons_first_aid_supplies   Commons: space blankets, CPR masks, bag valve masks, Resusci Anne manikins, medical ID
                               tags, tick removal, oral rehydration, calamine lotion, heating pads, compression
                               stockings and urinary catheters; and the birth supplies and drawings (breast pumps,
                               the Apgar score chart, drawings of fetal development), too few for a pack of their
                               own.
  commons_first_aid_skills     Commons: CPR and chest compressions, abdominal thrusts (the Heimlich manoeuvre), the
                               recovery position and first aid classes (adults only; describing only).
  commons_dental_care          Commons: water flossers, interdental brushes, tongue scrapers, clear aligners,
                               mouthguards, implants, bridges and sealants.
  commons_eye_care             Commons: magnifying glasses, magnifiers, loupes, pinhole glasses,
                               reading glasses, bifocals, glasses frames, contact lenses and their cases, Snellen
                               charts and slit lamps.
  scin_skin_conditions         SCIN (Skin Condition Image Network, Google Research and Stanford Medicine, 2024; the
                               SCIN Data Use License: attribution, adapting and sharing allowed): adults' own photos
                               of skin conditions with up to three dermatologists' labels. Photos of the genitals,
                               groin or buttocks are left out, front-of-torso photos unless close up, and the label
                               "Inflicted skin lesions". "What do dermatologists think this skin condition is?" ->
                               "The dermatologists who reviewed this photo most often named eczema (also: allergic
                               contact dermatitis). This is not a diagnosis: ..."
  denpar_dental_xrays          DenPAR (Annotated Intra-Oral Periapical Radiographs, Zenodo 16645076, CC BY 4.0): dental
                               X-rays with the arch, side and FDI numbers of the teeth each one shows, from the
                               dataset's own table. "Which teeth does this dental X-ray show?" -> "The dataset says it
                               shows the lower right teeth: the lower right first premolar (44), ..."
  open_images_home_health      Open Images V7: blood pressure cuffs (sphygmomanometers), ice packs, cotton swabs,
                               tweezers, humidifiers, hand sanitiser, face masks, pulse oximeters, measuring spoons,
                               tissues, slings and braces, dental floss, mouthwash, dentures, dental braces and
                               contact lenses.

What was looked at and left out (DermNet, Fitzpatrick17k, DDI, PAD-UFES-20, retinal image sets, the Red Cross's and
AHA's pictures and others) is in the kit's home_health_sources.py.

    python packs/home_health_packs.py denpar_dental_xrays --limit 8      (prints a few rows: a quick check)
"""

import ast
import csv
import io
import re
import sys
import zipfile

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, fetch_all, ALT_TEXT  # noqa: F401
from gaps_oi_packs import group, build_oi_gap, QUICK

ASK_WHAT = "What is this?"
ASK_DOING = "What is happening in this picture?"

EMERGENCY_NOTE = ("In an emergency, call 911 (or your local emergency number). This is general information, not "
                  "medical training or a diagnosis; ask a doctor, nurse or pharmacist.")
DENTAL_NOTE = ("For a knocked-out tooth, a swollen face or a bad toothache, see a dentist today; in an emergency, call "
               "911 (or your local emergency number). This is general information, not a diagnosis; ask your "
               "dentist.")
EYE_NOTE = ("Sudden loss of vision, flashes with a curtain over your sight, a chemical splash or an eye injury is an "
            "emergency: call 911 (or your local emergency number) or go to an emergency room. This is general "
            "information, not a diagnosis; ask your eye doctor.")
BIRTH_NOTE = ("In an emergency, call 911 (or your local emergency number). This is general information, not medical "
              "advice or a diagnosis; ask your midwife or doctor.")
NOTES = (EMERGENCY_NOTE, DENTAL_NOTE, EYE_NOTE, BIRTH_NOTE)


def item(category, words, note=EMERGENCY_NOTE, deeper=True, question=ASK_WHAT, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, "This is <words>." and the
    note)]) and an optional pattern of words a file's title or description must have."""
    spec = (category, deeper, [(question, f"This is {words}. {note}")])
    return spec + ((pattern,) if pattern is not None else ())


# ----------------------------------------------------------------- Commons: first aid supplies

FIRST_AID = [
    item("Space blankets", "an emergency blanket (space blanket), a thin foil sheet that keeps body heat in"),
    item("CPR masks", "a CPR mask (pocket mask), used to give rescue breaths without touching the person's mouth"),
    item("Bag valve masks", "a bag valve mask, which trained responders squeeze to push air into the lungs"),
    item("Resusci Anne", "a Resusci Anne CPR training manikin, for practising chest compressions and rescue breaths"),
    item("Medical identification tags", "a medical ID tag or bracelet, which tells responders about a condition such "
                                        "as diabetes or an allergy"),
    item("Tick removal", "a tick being removed: grip it close to the skin with fine tweezers or a tick tool and pull "
                         "upward steadily", question=ASK_DOING),
    item("Oral rehydration therapy", "oral rehydration: drinking a solution of salts and sugar in clean water, mixed "
                                     "as the packet says, to replace what is lost with diarrhoea and vomiting"),
    item("Calamine lotion", "calamine lotion, a pink lotion that soothes itchy rashes and insect bites"),
    item("Heating pads", "a heating pad, for aching muscles; use a low setting and do not sleep on it"),
    item("Compression stockings", "compression stockings, which squeeze the legs to help blood flow"),
    item("Urinary catheters", "a urinary catheter, a thin tube that drains urine from the bladder; wash your hands "
                              "before and after touching it"),
]

# ----------------------------------------------------------------- Commons: first aid skills (people, adults only)

FIRST_AID_SKILLS = [
    item("Cardiopulmonary resuscitation", "CPR (cardiopulmonary resuscitation): pushing hard and fast in the middle of "
                                          "the chest, about 100 to 120 times a minute, after calling 911",
         question=ASK_DOING),
    item("Chest compressions", "chest compressions, the main part of CPR", question=ASK_DOING),
    item("Heimlich maneuver", "abdominal thrusts (the Heimlich manoeuvre) for someone who is choking; babies under "
                              "one year get back blows and chest thrusts instead", question=ASK_DOING),
    item("Recovery position", "the recovery position: a person who is breathing but not awake, laid on their side so "
                              "the airway stays open", question=ASK_DOING),
    item("First aid training", "a first aid class", question=ASK_DOING),
]

# ----------------------------------------------------------------- Commons: dental care

DENTAL = [
    item("Oral irrigators", "a water flosser (oral irrigator), which cleans between the teeth with a jet of water",
         DENTAL_NOTE),
    item("Interdental brushes", "an interdental brush, a tiny brush for cleaning between the teeth", DENTAL_NOTE),
    item("Tongue scrapers", "a tongue scraper", DENTAL_NOTE),
    item("Clear aligners", "clear aligners, see-through trays that straighten teeth", DENTAL_NOTE),
    item("Mouthguards", "a mouthguard, which protects the teeth in sport or from grinding", DENTAL_NOTE),
    item("Dental implants", "a dental implant, a metal post that holds a false tooth", DENTAL_NOTE),
    item("Dental bridges", "a dental bridge, a false tooth held by the teeth beside the gap", DENTAL_NOTE),
    item("Dental sealants", "dental sealants: thin coatings painted on the chewing surfaces of back teeth to prevent "
                            "decay", DENTAL_NOTE),
]

# ----------------------------------------------------------------- Commons: eye care

EYE = [
    item("Magnifying glasses", "a magnifying glass, a handheld lens that makes small print look bigger", EYE_NOTE),
    item("Loupes", "a loupe, a small strong magnifier held close to the eye", EYE_NOTE),
    item("Reading glasses", "a pair of reading glasses, which magnify for close work", EYE_NOTE),
    item("Magnifiers", "a magnifier: a lens, stand or dome that makes print and small things look bigger", EYE_NOTE),
    item("Pinhole glasses", "pinhole glasses: glasses with many tiny holes instead of lenses", EYE_NOTE),
    item("Bifocals", "bifocal glasses: the lower part of each lens is for reading, the upper part for distance",
         EYE_NOTE),
    item("Eyeglass frames", "a glasses frame", EYE_NOTE),
    item("Contact lenses", "a contact lens; never rinse or store lenses in tap water or saliva", EYE_NOTE),
    item("Contact lens cases", "a contact lens case; empty it, rinse it with fresh solution and let it air-dry every "
                               "day", EYE_NOTE),
    item("Snellen charts", "a Snellen eye chart, with rows of letters getting smaller, for testing sight", EYE_NOTE),
    item("Slit lamps", "a slit lamp, a microscope with a bright light for examining the eye", EYE_NOTE),
]

# ----------------------------------------------------------------- Commons: birth and postpartum supplies (things only)

BIRTH = [
    item("Breast pumps", "a breast pump, for expressing breast milk", BIRTH_NOTE),
    item("Apgar score", "a chart of the Apgar score: the newborn's appearance, pulse, grimace, activity and breathing, "
                        "each scored 0 to 2 at one and five minutes after birth", BIRTH_NOTE),
    item("Fetal development", "a drawing of a baby's development in the womb", BIRTH_NOTE),
]

def build_commons_first_aid_supplies(limit):
    """The commons_first_aid_supplies pack (see the module docstring), with the birth supplies and drawings (BIRTH,
    too few free files for a pack of their own); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(FIRST_AID + BIRTH, limit, "firstaid", adults_only=True)


def build_commons_first_aid_skills(limit):
    """The commons_first_aid_skills pack: adults doing CPR, abdominal thrusts and the recovery position on each
    other or on manikins (files naming a child are left out); describing only."""
    from home_packs import build_commons_topic
    return build_commons_topic(FIRST_AID_SKILLS, limit, "firstaidskill", adults_only=True)


def build_commons_dental_care(limit):
    """The commons_dental_care pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(DENTAL, limit, "dental", adults_only=True)


def build_commons_eye_care(limit):
    """The commons_eye_care pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(EYE, limit, "eyecare", adults_only=True)


# ----------------------------------------------------------------- SCIN skin conditions

SCIN = "https://storage.googleapis.com/dx-scin-public-data/"
SCIN_CREDIT = ("SCIN (Skin Condition Image Network), Google Research and Stanford Medicine, 2024, released under the "
               "SCIN Data Use License, https://github.com/google-research-datasets/scin")
SKIN_Q = "What do dermatologists think this skin condition is?"
LEFT_OUT_LABELS = re.compile(r"inflicted", re.I)


def scin_label_words(weighted):
    """[(condition, weight)] from SCIN's weighted_skin_condition_label ("{'Eczema': 0.41, ...}"), largest first;
    [] when it cannot be read."""
    try:
        labels = ast.literal_eval(weighted or "{}")
    except (ValueError, SyntaxError):
        return []
    return sorted(((str(k), float(v)) for k, v in labels.items()), key=lambda kv: -kv[1])


def scin_answer(weighted):
    """The answer for one case from its dermatologists' weighted labels, or "" (no labels, or a left-out label)."""
    labels = scin_label_words(weighted)
    if not labels or any(LEFT_OUT_LABELS.search(name) for name, _ in labels):
        return ""
    first = labels[0][0]
    others = [name for name, _ in labels[1:3]]
    answer = f"The dermatologists who reviewed this photo most often named {first.lower()}"
    if others:
        answer += f" (also: {', '.join(o.lower() for o in others)})"
    return answer + ". This is not a diagnosis: only a doctor who examines the skin can say. " + EMERGENCY_NOTE


def scin_case_ok(case):
    """True when a SCIN case may be shown: no photo of the genitals, groin or buttocks."""
    return case.get("body_parts_genitalia_or_groin") != "YES" and case.get("body_parts_buttocks") != "YES"


def scin_items(cases, labels, want):
    """(name, address, rows) of SCIN photos: each kept case's photos (front-of-torso photos only close up), with its
    dermatologists' labels; at most want."""
    by_case = {row["case_id"]: row for row in labels}
    items = []
    for case in cases:
        label = by_case.get(case.get("case_id"))
        if not label or not scin_case_ok(case):
            continue
        answer = scin_answer(label.get("weighted_skin_condition_label"))
        if not answer:
            continue
        for n in (1, 2, 3):
            path, shot = case.get(f"image_{n}_path"), case.get(f"image_{n}_shot_type")
            if not path or (case.get("body_parts_torso_front") == "YES" and shot != "CLOSE_UP"):
                continue
            rows = [{"question": SKIN_Q, "answer": answer, "credit": SCIN_CREDIT, "content": "medical"}]
            items.append((f"scin-{case['case_id'].lstrip('-')}-{n}.jpg", SCIN + path, rows))
    pass_random("scin").shuffle(items)
    return items[:want]


def build_scin_skin_conditions(limit):
    """The scin_skin_conditions pack (see the module docstring)."""
    from food_packs import with_twins
    s = session()
    cases = list(csv.DictReader(io.StringIO(s.get(SCIN + "dataset/scin_cases.csv", timeout=120).text)))
    labels = list(csv.DictReader(io.StringIO(s.get(SCIN + "dataset/scin_labels.csv", timeout=120).text)))
    items = scin_items(cases, labels, int(limit * 1.1) + 2)
    say(f"SCIN: {len(cases)} cases, {len(items)} photos chosen")
    return with_twins(fetch_all(items, workers=4)[:limit])


# ----------------------------------------------------------------- DenPAR dental X-rays

DENPAR = "https://zenodo.org/records/16645076/files/DenPAR%20Radiographs%20Dataset.zip?download=1"
DENPAR_CREDIT = ("DenPAR: Annotated Intra-Oral Periapical Radiographs Dataset, Zenodo record 16645076, CC BY 4.0, "
                 "https://zenodo.org/records/16645076")
XRAY_Q = "Which teeth does this dental X-ray show?"
KIND_Q = "What kind of picture is this?"
# FDI tooth numbers: the first digit is the quarter of the mouth, the second the tooth counted from the middle.
QUARTERS = {"1": "upper right", "2": "upper left", "3": "lower left", "4": "lower right"}
TEETH = {"1": "central incisor", "2": "lateral incisor", "3": "canine", "4": "first premolar",
         "5": "second premolar", "6": "first molar", "7": "second molar", "8": "third molar (wisdom tooth)"}


def fdi_name(number):
    """"lower right first molar" for FDI number "46", or "" for a number that is not an adult tooth's."""
    number = str(number).strip()
    if len(number) != 2 or number[0] not in QUARTERS or number[1] not in TEETH:
        return ""
    return f"{QUARTERS[number[0]]} {TEETH[number[1]]}"


def xray_answer(arch, site, teeth):
    """The answer for one radiograph from the dataset's own table: the FDI numbers of the teeth it shows, or "".
    Where in the mouth is worked out from the FDI numbers alone (their first digit), because the table's arch and
    site columns sometimes disagree with its own tooth numbers (about one row in thirteen); arch and site are not
    used."""
    numbers = [t.strip() for t in str(teeth or "").replace(";", ",").split(",") if t.strip()]
    names = [f"the {fdi_name(n)} ({n})" for n in numbers if fdi_name(n)]
    if not names or len(names) != len(numbers):
        return ""
    where = WHERE.get(frozenset(n[0] for n in numbers), "")
    listed = ", ".join(names[:-1]) + (" and " if len(names) > 1 else "") + names[-1]
    return (f"The dataset says it shows {'the ' + where + ' teeth: ' if where else 'these teeth: '}{listed}. The "
            f"numbers are FDI tooth numbers. " + DENTAL_NOTE)


# Where the teeth are, from the quarters of the mouth their FDI numbers name.
WHERE = {frozenset("1"): "upper right", frozenset("2"): "upper left", frozenset("3"): "lower left",
         frozenset("4"): "lower right", frozenset("12"): "upper front", frozenset("34"): "lower front"}


def denpar_rows(arch, site, teeth):
    """The rows of one DenPAR radiograph, or [] when its table row cannot be read."""
    answer = xray_answer(arch, site, teeth)
    if not answer:
        return []
    return [{"question": XRAY_Q, "answer": answer, "credit": DENPAR_CREDIT},
            {"question": KIND_Q, "answer": "This is a dental X-ray: an intraoral periapical radiograph, which shows "
                                           "a few whole teeth from crown to root tip. " + DENTAL_NOTE,
             "credit": DENPAR_CREDIT}]


def build_denpar_dental_xrays(limit):
    """The denpar_dental_xrays pack: the zip is read once (about 140 MB), its table gives each radiograph's teeth."""
    import openpyxl
    from build_packs import smaller
    from food_packs import with_twins
    s = session()
    data = s.get(DENPAR, timeout=900).content
    z = zipfile.ZipFile(io.BytesIO(data))
    sheet = openpyxl.load_workbook(io.BytesIO(z.read("Dataset/Characteristics of radiographs included.xlsx")),
                                   read_only=True).active
    table = {str(int(r[0])): r[1:4] for r in sheet.iter_rows(min_row=2, values_only=True) if r and r[0] is not None}
    images = {n.rsplit("/", 1)[-1][:-4]: n for n in z.namelist() if "/Images/" in n and n.lower().endswith(".jpg")}
    keys = sorted(set(images) & set(table))
    pass_random("denpar").shuffle(keys)
    out = []
    for key in keys:
        if len(out) >= limit:
            break
        rows = denpar_rows(*table[key])
        picture = smaller(z.read(images[key])) if rows else None
        if picture:
            out.append((f"denpar-{key}.jpg", picture, rows))
    say(f"DenPAR: {len(keys)} radiographs with a table row, {len(out)} kept")
    return with_twins(out)


# ----------------------------------------------------------------- Open Images

HOME_HEALTH_OI = [
    group("What first-aid or home care things are in this picture?",
          {"Sphygmomanometer": "a blood pressure cuff", "Ice pack": "an ice pack", "Cotton swab": "cotton swabs",
           "Tweezers": "tweezers", "Humidifier": "a humidifier", "Hand sanitizer": "hand sanitiser",
           "Face mask": "a face mask", "Pulse oximeter": "a pulse oximeter", "Measuring spoon": "a measuring spoon",
           "Facial tissue": "tissues", "Sling": "a sling", "Brace": "a brace"}, EMERGENCY_NOTE),
    group("What dental care things are in this picture?",
          {"Dental floss": "dental floss", "Mouthwash": "mouthwash", "Dentures": "dentures",
           "Dental braces": "dental braces"}, DENTAL_NOTE),
    group("What eye care things are in this picture?", {"Contact lens": "a contact lens"}, EYE_NOTE),
]


def build_open_images_home_health(limit):
    """The open_images_home_health pack (see the module docstring)."""
    return build_oi_gap("open_images_home_health", HOME_HEALTH_OI, limit, 9321)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
HOME_HEALTH_PACKS = {
    "commons_first_aid_supplies": (build_commons_first_aid_supplies, COMMONS_LICENCE.format(
        what="first-aid supply and home treatment")),
    "commons_first_aid_skills": (build_commons_first_aid_skills, COMMONS_LICENCE.format(
        what="CPR, abdominal thrust, recovery position and first aid class")),
    "commons_dental_care": (build_commons_dental_care, COMMONS_LICENCE.format(
        what="dental care product and dental appliance")),
    "commons_eye_care": (build_commons_eye_care, COMMONS_LICENCE.format(
        what="glasses, contact lens, eye drop, magnifier and eye examination")),
    "scin_skin_conditions": (build_scin_skin_conditions, SCIN_CREDIT + "; the dermatologists' labels are the "
                                                                       "dataset's own."),
    "denpar_dental_xrays": (build_denpar_dental_xrays, DENPAR_CREDIT + "; the teeth from the dataset's own table."),
    "open_images_home_health": (build_open_images_home_health, OI_LICENCE),
}
HOME_HEALTH_LIMITS = {
    "commons_first_aid_supplies": 600,     # 14 categories (with the birth ones), few files each
    "commons_first_aid_skills": 500,       # 5 categories
    "commons_dental_care": 600,            # 7 categories
    "commons_eye_care": 900,               # 12 categories
    "scin_skin_conditions": 3000,          # about 5,000 cases, some left out
    "denpar_dental_xrays": 1000,           # 1,000 radiographs with a table row
    "open_images_home_health": 1500,       # 17 labels, few photos each
}
HOME_HEALTH_COMMONS_KEYS = ("commons_first_aid_supplies", "commons_first_aid_skills", "commons_dental_care",
                            "commons_eye_care")
# Packs that show people's bodies: describing only (the kit's PEOPLE_AND_BODILY_PACK_KEYS).
HOME_HEALTH_BODILY_KEYS = ("commons_first_aid_skills", "scin_skin_conditions")


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a home health pack builder.")
    parser.add_argument("key", choices=sorted(HOME_HEALTH_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = HOME_HEALTH_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
