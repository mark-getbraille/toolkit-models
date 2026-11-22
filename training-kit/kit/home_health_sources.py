"""HOME HEALTH CARE for the Picture Model Training Kit (the owner's requests of 2026-11-22: first aid in depth, home
treatment, long-term conditions, home nursing, dental care, midwifery and postpartum care, eye care). This file lists:
  - the ready-made packs built in packs/home_health_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_first_aid_supplies, commons_first_aid_skills, commons_dental_care, commons_eye_care,
    commons_birth_care, scin_skin_conditions, denpar_dental_xrays, open_images_home_health;
  - the share-alike Commons files of the main categories (home_health_commons_sa: only with the share-alike choice);
  - the sign-up and research-only collections looked at (HOME_HEALTH_SIGN_UP) and the ones left out
    (HOME_HEALTH_NOT_INCLUDED), with the reason.

Already in the kit and not repeated: medicines, pills, eye drops and medicine labels, medical supplies and
instruments, AEDs, first aid kits and stations, home tests, wheelchairs, walkers and white canes, plain spectacles and
sunglasses, dental instruments, toothbrushes and toothpaste (med_vet_packs, medication_label_packs,
health_test_packs, events_safety_packs, disability_packs, home_packs, and the DailyMed and C3PI personal-use
entries), and birth, breastfeeding, midwifery and newborn care photos (birth_and_feeding, medical_packs.py).

Every answer ends with the packs' note (the same words): EMERGENCY_NOTE, DENTAL_NOTE, EYE_NOTE or BIRTH_NOTE: call 911
(or the local emergency number) in an emergency; general information, not medical training or a diagnosis; ask a
doctor, nurse, pharmacist, dentist, eye doctor or midwife. Nothing is ever a diagnosis: SCIN's answers say what the
dermatologists who reviewed the photo named, and that only a doctor who examines the skin can say.

People: commons_first_aid_skills (adults doing CPR on each other or manikins) and scin_skin_conditions (adults'
skin, never the genitals, groin or buttocks) are describing only: HOME_HEALTH_BODILY_KEYS, which sources.py adds to
PEOPLE_AND_BODILY_PACK_KEYS. SCIN's rows carry "content": "medical", so they are used only when the training ticks
medical pictures.

Picture-making (HOME_HEALTH_PICTURE_MAKING_OK): the supply, dental, eye and birth-supply packs (things and drawings)
and the share-alike things; never the people, skin, X-ray or Open Images packs.

    python -c "import sources, home_health_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

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

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def thing(category, words, note=EMERGENCY_NOTE, deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the note."""
    return (category, "What is this?", f"This is {words}. {note}", deeper)


# Things only (the people and skin packs have no share-alike entry).
HOME_HEALTH_SA = [
    thing("Space blankets", "an emergency blanket (space blanket), a thin foil sheet that keeps body heat in"),
    thing("CPR masks", "a CPR mask (pocket mask), used to give rescue breaths without touching the person's mouth"),
    thing("Compression stockings", "compression stockings, which squeeze the legs to help blood flow"),
    thing("Interdental brushes", "an interdental brush, a tiny brush for cleaning between the teeth", DENTAL_NOTE),
    thing("Dental braces", "dental braces, which slowly straighten the teeth", DENTAL_NOTE),
    thing("Dental implants", "a dental implant, a metal post that holds a false tooth", DENTAL_NOTE),
    thing("Magnifying glasses", "a magnifying glass, a handheld lens that makes small print look bigger", EYE_NOTE),
    thing("Contact lenses", "a contact lens; never rinse or store lenses in tap water or saliva", EYE_NOTE),
    thing("Breast pumps", "a breast pump, for expressing breast milk", BIRTH_NOTE),
]


def prepare_home_health_commons_sa(source, data_dir, work, cap):
    """Commons first-aid, dental, eye and birth supply categories, files under CC BY-SA or GFDL; no files naming a
    child."""
    items = commons_sa_items(HOME_HEALTH_SA, cap, source.test, "homehealth-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


HOME_HEALTH_SOURCES = [
    Source("commons_first_aid_supplies", "First aid and home treatment things: space blankets, CPR masks, bag valve "
                                         "masks, training manikins, medical ID tags, tick removal, oral rehydration, "
                                         "calamine lotion, heating pads, compression stockings and catheters, each "
                                         "with the emergency note (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 10, prepare_pack, "about 110 MB"),
    Source("commons_first_aid_skills", "Adults doing CPR, chest compressions, abdominal thrusts and the recovery "
                                       "position, and first aid classes, with the emergency note (Wikimedia Commons, "
                                       "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 10, prepare_pack, "about 110 MB"),
    Source("commons_dental_care", "Dental care: water flossers, interdental brushes, tongue scrapers, braces, clear "
                                  "aligners, mouthguards and implants, with the dental note (Wikimedia Commons, "
                                  "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 130 MB"),
    Source("commons_eye_care", "Eye care: magnifying glasses, loupes and monoculars, reading glasses, bifocals and "
                               "progressive lenses, frames, lenses and nose pads, contact lenses and cases, eye drops, "
                               "eye charts and eye examination instruments, with the eye note (Wikimedia Commons, "
                               "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 260 MB"),
    Source("commons_birth_care", "Birth and postpartum supplies: breast pumps, nipple shields, birthing pools, cord "
                                 "clamps, baby thermometers, maternity pads, peri bottles, fetoscopes and Pinard "
                                 "horns, and drawings of fetal development (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 10, prepare_pack, "about 100 MB"),
    Source("scin_skin_conditions", "Skin conditions in adults' own photos with up to three dermatologists' labels, "
                                   "never a diagnosis (SCIN, Google Research and Stanford Medicine, ready-made pack; "
                                   "medical)",
           "SCIN Data Use License (attribution; adapting and sharing allowed), "
           "https://github.com/google-research-datasets/scin/blob/main/LICENSE",
           "SCIN (Skin Condition Image Network), Google Research and Stanford Medicine, 2024, "
           "https://github.com/google-research-datasets/scin", "permissive", 3000, 40, prepare_pack, "about 700 MB",
           content="medical"),
    Source("denpar_dental_xrays", "Dental X-rays (periapical radiographs) with the arch, side and FDI numbers of the "
                                  "teeth each shows (DenPAR, Zenodo 16645076, ready-made pack)",
           "CC BY 4.0 (DenPAR: Annotated Intra-Oral Periapical Radiographs Dataset, Zenodo 16645076)",
           "DenPAR: Annotated Intra-Oral Periapical Radiographs Dataset, https://zenodo.org/records/16645076, CC BY "
           "4.0", "permissive", 1000, 20, prepare_pack, "about 120 MB"),
    Source("open_images_home_health", "Blood pressure cuffs, ice packs, cotton swabs, tweezers, humidifiers, hand "
                                      "sanitiser, face masks, pulse oximeters, measuring spoons, dental floss, "
                                      "mouthwash, dentures, braces and contact lenses (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("home_health_commons_sa", "Wikimedia Commons: space blankets, CPR masks, compression stockings, "
                                     "interdental brushes, braces, implants, magnifying glasses, contact lenses and "
                                     "breast pumps, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 600, 10, prepare_home_health_commons_sa, "about 130 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# Describing only (people's bodies): added to sources.PEOPLE_AND_BODILY_PACK_KEYS.
HOME_HEALTH_BODILY_KEYS = ("commons_first_aid_skills", "scin_skin_conditions")
# Things and drawings only.
HOME_HEALTH_PICTURE_MAKING_OK = {"commons_first_aid_supplies", "commons_dental_care", "commons_eye_care",
                                 "commons_birth_care", "home_health_commons_sa"}

HOME_HEALTH_SIGN_UP = {
    "Fitzpatrick17k (Groh et al., 2021)":
        "16,577 skin condition photos with Fitzpatrick skin types; the images come from two dermatology atlases "
        "(DermaAmin and Atlas Dermatologico) and the repository (github.com/mattgroh/fitzpatrick17k) gives only "
        "links to them, for research. Research use only: the owner may fetch it himself for personal use.",
    "Diverse Dermatology Images, DDI (Stanford AIMI)":
        "656 biopsy-confirmed skin lesion images across skin tones; download needs a Stanford AIMI account and "
        "agreeing to a research use agreement (https://ddi-dataset.github.io). Personal use only.",
    "DermNet image library (dermnetnz.org)":
        "CC BY-NC-ND 3.0 NZ for its images: no derivatives and non-commercial, so a training set may not adapt "
        "them; link-only (https://dermnetnz.org/image-library).",
    "PAD-UFES-20 (Mendeley Data zr7vgbcyr2)":
        "2,298 smartphone photos of skin lesions with biopsy results, CC BY 4.0; its photos are of skin cancers and "
        "pre-cancers (not home care conditions). Recorded for a later pack.",
    "Kaggle and Roboflow dental and eye sets (intraoral photos, panoramic X-rays, retinal fundus photos)":
        "a free account and API key are needed; each set's licence and the origin of its photos must be checked "
        "one by one.",
    "DENTEX 2023 panoramic X-rays (Zenodo 7812323, CC BY 4.0)":
        "11 GB of panoramic X-rays with caries and periapical lesion labels; open, but too large for the pack "
        "builder in one pass. DenPAR is built instead.",
    "Retinal fundus and slit-lamp image sets (for example ODIR, APTOS, EyePACS, RFMiD)":
        "most are research-only or competition-only (Kaggle terms); retinal photos are for eye doctors, not for "
        "describing everyday pictures. Recorded only.",
}

HOME_HEALTH_NOT_INCLUDED = {
    "American Red Cross and American Heart Association pictures and guides":
        "copyright of the Red Cross and the AHA (\"All rights reserved\"); link-only in the reference library.",
    "A second birth, breastfeeding, midwifery and newborn care photo pack":
        "Commons' Breastfeeding, Kangaroo care, Childbirth, Midwifery, Midwives, Prenatal care and Newborn babies "
        "categories are already the birth_and_feeding pack (medical_packs.py), which keeps only respectful care "
        "scenes and a baby only with a parent or carer; not repeated. commons_birth_care adds the supplies and "
        "drawings.",
    "CDC PHIL wound and rash photos":
        "many are graphic clinical photos (disease and injury), beyond what ordinary first-aid guides show; the "
        "kit's cdc_phil packs take supplies and health behaviours only.",
    "Commons categories that do not exist or hold no files under the names tried (November 2026)":
        "Eye drops (already med_vet_packs'), CPR training, CPR manikins, Pocket masks, Pressure bandages, Elastic bandages, Gauze pads, Arm slings, "
        "Burn dressings, Cold packs, Instant cold packs, Emergency blankets, Epinephrine autoinjectors, Medical "
        "alert bracelets, Eyewash stations, Stop the Bleed, Poison control, Mr. Yuk, FAST (stroke), Mental health "
        "first aid, Peak flow meters, Inhaler spacers, Ostomy bags, Oxygen concentrators, Nasal cannulas, Hand "
        "sanitizer, Hot water bottles, Neti pots, Steri-Strips, Water flossers, Orthodontic retainers; Blood "
        "pressure monitors, Dentures, Gauze and Splinters are empty.",
    "Commons first aid and home care categories other packs already use":
        "Tourniquets, Triangular bandages, Cervical collars, Medical gloves, Autoinjectors, Naloxone, Ice packs, "
        "Sphygmomanometers, Glucose meters, Insulin pens, Inhalers, Nebulizers, Pill organizers, Pulse oximeters, "
        "Hand washing, Wrist braces, Toothbrushes, Electric toothbrushes, Dental floss, Mouthwash, Toothpaste, "
        "Adhesive bandages, Tweezers, Cotton swabs and Hospital beds (never asked twice).",
    "Open Images health labels already asked elsewhere or missing":
        "First aid kit, Bandage, Medical glove, Thermometer, Stethoscope, Syringe, Pill, Medicine, Crutch, "
        "Wheelchair, Toothbrush, Toothpaste and Stretcher are other packs'; there is no label for inhalers, "
        "defibrillators, splints, rashes or wounds.",
    "WHO, AHRQ and WikEM pictures":
        "their sites' robots.txt shut out AI companies' readers (checked 2026-11-22); not read.",
}
