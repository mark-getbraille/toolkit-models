"""DISABILITIES, VETERANS AND IMMIGRATION DOCUMENTS for the Picture Model Training Kit (the owner's "people" request
of 2026-11-22). This file lists:
  - the ready-made packs built in packs/people_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_mobility_aids, commons_hearing_communication, commons_veterans and
    commons_immigration_documents;
  - the share-alike Commons files of the mobility and hearing categories (group "share-alike": only with the
    share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (PEOPLE_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it (the packs from the kit's own release),
only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the Commons category says, and describe disabled people plainly and respectfully, by what they
use. Every answer ends with its note (the same words as the packs': packs/test_people.py checks): ACCESS_NOTE (the
ADA and where to ask), HEARING_NOTE (audiologists, 711 relay), VETERAN_NOTE (VA.gov, the Veterans Crisis Line) and
IMMIGRATION_NOTE (keep documents safe, replace them only through USCIS or the State Department, no notarios, and the
not-legal-advice line).

Picture-making (PEOPLE_PICTURE_MAKING_OK): none of these. The mobility, hearing and veterans collections show
disabled people, veterans and graves, and a picture-making model must never learn to make identity or immigration
documents; sources.py puts every key here in NOT_FOR_PICTURE_MAKING.
Topics: the mobility aids, the hearing and communication access pictures (loops, captions, symbols, picture cards)
and their share-alike files in the health topic (Health and medical pictures); the immigration documents in the money
topic (Money and paperwork); the veterans pack in no topic (it is used in the general describer).

    python -c "import sources, people_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The notes, word for word as in packs/people_packs.py.
LEGAL = "General information, not legal advice; check the current rules or ask an accredited representative or lawyer."
ACCESS_NOTE = ("Disability rights (ADA): businesses, employers and governments must make reasonable changes so "
               "disabled people can take part; ask them, and see ADA.gov or call the ADA Information Line, "
               "800-514-0301.")
HEARING_NOTE = ("Hearing devices are fitted by an audiologist; anyone can reach a relay service for phone calls by "
                "dialling 711.")
VETERAN_NOTE = ("Veterans: for benefits, records and replacement medals see VA.gov or call 1-800-698-2411; Veterans "
                "Crisis Line: dial 988 then press 1.")
IMMIGRATION_NOTE = ("Keep immigration documents safe and a copy apart; replace a lost one only through USCIS "
                    "(uscis.gov) or the State Department, and never pay a notario. " + LEGAL)

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def item(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# The mobility and hearing categories of packs/people_packs.py, with the same answers.
PEOPLE_SA = [
    item("Manual wheelchairs", "a manual wheelchair, moved by its user with the push rims on the wheels or pushed by "
                               "a helper", ACCESS_NOTE, True),
    item("Sports wheelchairs", "a sports wheelchair, built light with angled wheels for sports such as basketball, "
                               "tennis and racing", deeper=True),
    item("Orthoses", "an orthosis (a brace or splint), worn to support, straighten or protect a part of the body; it "
                     "is fitted by an orthotist"),
    item("Leg braces", "a leg brace, an orthosis that supports the knee, ankle or the whole leg; it is fitted by an "
                       "orthotist"),
    item("Hearing induction loops", "a hearing induction loop (hearing loop) or its sign: a wire loop that sends "
                                    "sound straight to hearing aids and cochlear implants switched to the T "
                                    "(telecoil) setting", f"{HEARING_NOTE} {ACCESS_NOTE}", True),
    item("Audiometry", "a hearing test (audiometry): sounds of different pitches and loudness are played through "
                       "headphones and the person signals when they hear them", HEARING_NOTE, True),
    item("Accessibility symbols", "an accessibility symbol, a sign that shows an access feature such as wheelchair "
                                  "access, a hearing loop, sign language or audio description", ACCESS_NOTE, True),
]


def prepare_people_commons_sa(source, data_dir, work, cap):
    """Commons wheelchair, brace, hearing loop, hearing test and accessibility symbol categories, files under CC BY-SA
    or GFDL."""
    items = commons_sa_items(PEOPLE_SA, cap, source.test, "people-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

PEOPLE_SOURCES = [
    Source("commons_mobility_aids", "Mobility aids: manual and sports wheelchairs, orthoses and leg braces, "
                                    "with the ADA note (Wikimedia Commons, ready-made "
                                    "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 5, prepare_pack, "about 90 MB"),
    Source("commons_hearing_communication", "Hearing and communication access: hearing loops, hearing tests, "
                                            "captioning and subtitles, accessibility symbols, picture exchange "
                                            "cards and sensory rooms (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    Source("commons_veterans", "Veterans: US military ribbon bars, decorations and badges, dog tags, and folded "
                               "flags as at military funerals, with the VA and Veterans Crisis Line note (Wikimedia "
                               "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 10, prepare_pack, "about 110 MB"),
    Source("commons_immigration_documents", "Immigration documents: US passports and visas, travel documents and "
                                            "Social Security cards (samples, specimens and old documents), with the "
                                            "USCIS note (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 200, 5, prepare_pack, "about 45 MB"),
    Source("people_commons_sa", "Wikimedia Commons: manual and sports wheelchairs, orthoses, leg braces, hearing "
                                "loops, hearing tests and accessibility symbols, files under CC BY-SA or GFDL "
                                "(share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 300, 5, prepare_people_commons_sa, "about 70 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# No collection here may be used for picture-making (see the module docstring).
PEOPLE_PICTURE_MAKING_OK = set()

PEOPLE_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Wheelchairs, Electric wheelchairs, Mobility scooters, "
        "Rollators, Crutches, Walking sticks, Limb prostheses, Hearing aids and Hearing aid types (with "
        "Behind-the-ear hearing aids), Cochlear implants, Wheelchair ramps and lifts, Accessibility signs, "
        "Augmentative and alternative communication (disability_packs); Sign language interpreters "
        "(sign_language_packs); Grab bars (building_packs), Knee scooters (med_vet_packs), Patient lifts (the "
        "aging and care packs) and Wheelchair accessible taxis (driving_packs): not asked twice.",
    "Commons categories that do not exist or hold no files under the names tried (November 2026)": "Walkers "
        "(mobility aids), Walking frames, Quad canes, Transfer boards, Shower chairs, Wheelchair accessible vans and "
        "vehicles, Hand controls, Wheelchair cushions, Stair-climbing wheelchairs, Hearing aid batteries, "
        "Bone-anchored hearing aids, Audiometers, Teletypewriters for the deaf, TTY, Video relay services, "
        "Speech-generating devices, Communication boards, International Symbol of Access, Vibrating alarm clocks, "
        "Visual alarms, Doorbell signallers, Deaf symbols; for veterans and immigration: Purple Heart (medal), Bronze "
        "Star Medal, Navy Cross, Air Medal, National Defense Service Medal, Burial flags, Veterans Affairs medical "
        "centers, National cemeteries of the United States, Government-issued headstones, Permanent resident cards "
        "of the United States, Green cards, Employment Authorization Documents, United States passport cards, Form "
        "I-94, Certificates of naturalization, Refugee travel documents, Re-entry permits, Border crossing cards "
        "(Medal of Honor, Purple Heart and Silver Star hold no files of their own).",
    "Speech generating devices and Behind-the-ear hearing aids": "Subcategories of Augmentative and alternative "
        "communication and Hearing aid types, which disability_packs reads with their subcategories: not asked twice.",
    "United States Department of Veterans Affairs and Naturalization ceremonies in the United States": "The VA "
        "category mixes logos, officials and buildings, and the ceremonies show crowds of people (citizenship "
        "belongs to the citizenship collection): left out.",
    "Open Images": "Open Images V7 has no labels for hearing loops, captions, braces or medals beyond those other "
                   "packs ask (Wheelchair, Medal, Passport): not asked twice.",
    "Disabled and Here and other disability stock collections": "Disabled and Here is already in commons_disability; "
        "Getty's Disability Collection and Unsplash+ are not openly licensed.",
    "Real people's identity documents": "The categories chosen are of passports, visas and cards as objects "
        "(mostly samples, specimens and historical documents); the answers name only the kind of document, never a "
        "name or number written on it, and no category of anyone's own papers is read.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the people share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PEOPLE_SOURCES if s.key == "people_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="people-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
