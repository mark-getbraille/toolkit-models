"""Picture packs for the "people" collections (the owner's request of 2026-11-22): disabilities other than blindness,
veterans, and immigration documents. Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; the limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise the things around
disabled people other than blind ones (manual and sports wheelchairs, braces, accessible taxis, hearing loops,
hearing tests, captions, accessibility symbols, picture cards for communication), the medals, badges and grave
markers of veterans, and the immigration documents people carry, each with a short note of what to do or where to
get help.

Answers say only what the source says (a Commons category's name), never a guess: no brand, model, person or rank is
named unless the category itself names it. Disabled people are described plainly and respectfully, by what they use
("a person using a wheelchair"), never with pity. Each answer about a disability, veterans' or immigration subject
ends with the note that fits it:
  ACCESS_NOTE       the ADA: businesses and governments must make reasonable changes, and where to ask (ADA.gov).
  HEARING_NOTE      an audiologist fits hearing devices; relay services by dialling 711.
  VETERAN_NOTE      the Veterans Crisis Line (988 then press 1) and VA.gov for benefits and replacement medals.
  IMMIGRATION_NOTE  keep documents safe and copies apart; replace them only through USCIS or the State Department;
                    beware of notarios; and "General information, not legal advice ...".

The packs (PEOPLE_PACKS), all Wikimedia Commons files CC0, public domain or CC BY only (each credited):
  commons_mobility_aids          manual and sports wheelchairs, orthoses and leg braces, wheelchair accessible taxis
                                 and the walking and transfer aids no other pack asks about;
  commons_hearing_communication  hearing induction loops, hearing tests (audiometry) and audiograms, captioning and
                                 subtitles, TTYs and videophones, accessibility symbols, picture exchange cards
                                 (PECS) and sensory rooms;
  commons_veterans               US military ribbon bars and decorations (the Combat Action Ribbon, Combat
                                 Infantryman Badge, Distinguished Flying Cross, Vietnam Service Medal), dog tags,
                                 and folded flags and flag folding as at military funerals;
  commons_immigration_documents  US passports and visas, other travel documents and Social Security cards (the
                                 sample, specimen and old documents Commons holds; no category of green cards or
                                 work permits exists there).

Not repeated here (disability_packs.py): wheelchairs, power chairs, scooters, rollators, crutches, walking sticks,
prostheses, hearing aids (with their types), cochlear implants, ramps, lifts, accessible toilets, accessibility signs,
AAC, sign language (sign_language_packs.py) and the vision collection's blindness pictures; Grab bars (building
packs), Knee scooters (medical packs) and Patient lifts (the aging and care packs). What was looked at and left out is
in the kit's people_sources.py (PEOPLE_NOT_INCLUDED).

    python packs/people_packs.py commons_mobility_aids --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

# ----------------------------------------------------------------- the notes (the kit uses the same words)

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
ASK_WHAT = "What is this?"


def thing(category, words, notes="", deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


# ----------------------------------------------------------------- Commons: mobility aids

MOBILITY_AIDS = [
    thing("Manual wheelchairs", "a manual wheelchair, moved by its user with the push rims on the wheels or pushed "
                                "by a helper", ACCESS_NOTE, True),
    thing("Sports wheelchairs", "a sports wheelchair, built light with angled wheels for sports such as basketball, "
                                "tennis and racing", deeper=True),
    thing("Orthoses", "an orthosis (a brace or splint), worn to support, straighten or protect a part of the body; it "
                      "is fitted by an orthotist"),
    thing("Leg braces", "a leg brace, an orthosis that supports the knee, ankle or the whole leg; it is fitted by an "
                        "orthotist"),
    thing("Wheelchair accessible taxis", "a wheelchair accessible taxi, with a ramp or lift so a wheelchair user can "
                                         "ride in their chair", ACCESS_NOTE, True),
]

# ----------------------------------------------------------------- Commons: hearing and communication access

HEARING_COMMUNICATION = [
    thing("Hearing induction loops", "a hearing induction loop (hearing loop) or its sign: a wire loop that sends "
                                     "sound straight to hearing aids and cochlear implants switched to the T "
                                     "(telecoil) setting", f"{HEARING_NOTE} {ACCESS_NOTE}", True),
    thing("Audiometry", "a hearing test (audiometry): sounds of different pitches and loudness are played through "
                        "headphones and the person signals when they hear them", HEARING_NOTE, True),
    thing("Captioning", "captioning: the words spoken on a screen shown as text, for deaf and hard of hearing "
                        "people", ACCESS_NOTE, True),
    thing("Subtitles", "subtitles: text on the screen that shows what is said in a film or programme"),
    thing("Accessibility symbols", "an accessibility symbol, a sign that shows an access feature such as wheelchair "
                                   "access, a hearing loop, sign language or audio description", ACCESS_NOTE, True),
    thing("Picture Exchange Communication System", "picture exchange (PECS) cards: picture cards a person hands over "
                                                   "or points to, to communicate; a speech-language pathologist "
                                                   "helps set them up"),
    thing("Audiograms", "an audiogram, the chart of a hearing test: how loud each pitch must be before the person "
                        "hears it, for each ear", HEARING_NOTE),
    thing("Telecommunications device for the deaf", "a TTY (text telephone, telecommunications device for the "
                                                    "deaf), which sends typed conversation over a phone line",
          HEARING_NOTE, True),
    thing("Videophones", "a videophone, a phone with a screen and camera; deaf people use them to call in sign "
                         "language and through video relay services", HEARING_NOTE, True),
    thing("Sensory rooms", "a sensory room: a calm room with soft light, sounds and things to touch, used by autistic "
                           "people and others who need a quiet sensory space", deeper=True),
]

# ----------------------------------------------------------------- Commons: veterans

VETERANS = [
    thing("Ribbon bars of the United States", "a US military ribbon bar: each coloured ribbon stands for a decoration "
                                              "or service medal its wearer received", VETERAN_NOTE, True),
    thing("Combat Action Ribbon", "the Combat Action Ribbon, a US Navy and Marine Corps award for taking part in "
                                  "ground or surface combat", VETERAN_NOTE, True),
    thing("Combat Infantryman Badge", "the Combat Infantryman Badge, a US Army badge for infantry soldiers who served "
                                      "in ground combat", VETERAN_NOTE, True),
    thing("Distinguished Flying Cross (United States)", "the Distinguished Flying Cross, a US military decoration "
                                                        "for heroism or extraordinary achievement in flight",
          VETERAN_NOTE, True),
    thing("Vietnam Service Medal", "the Vietnam Service Medal, a US military medal for service in the Vietnam War",
          VETERAN_NOTE, True),
    thing("Dog tags", "dog tags, the metal identification tags worn by military service members", VETERAN_NOTE, True),
    thing("Folded flags of the United States", "a US flag folded into a triangle, as it is presented at military "
                                               "funerals and ceremonies", VETERAN_NOTE),
    thing("Flag folding", "the folding of a US flag into a triangle, as done at military funerals and ceremonies",
          VETERAN_NOTE, True),
]

# ----------------------------------------------------------------- Commons: immigration documents

IMMIGRATION_DOCUMENTS = [
    thing("Passports of the United States", "a United States passport", IMMIGRATION_NOTE, True),
    thing("Visas of the United States", "a United States visa, the stamp or sticker in a passport that allows "
                                        "travel to the United States for a purpose", IMMIGRATION_NOTE, True),
    thing("Travel documents", "a travel document, a passport or other paper that lets its holder cross borders",
          IMMIGRATION_NOTE),
    thing("Social Security cards", "a US Social Security card, which shows a person's Social Security number; keep "
                                   "it at home in a safe place, not in a wallet", IMMIGRATION_NOTE),
]


def build_commons_mobility_aids(limit):
    """The commons_mobility_aids pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MOBILITY_AIDS, limit, "pplmobility")


def build_commons_hearing_communication(limit):
    """The commons_hearing_communication pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(HEARING_COMMUNICATION, limit, "pplhearing")


def build_commons_veterans(limit):
    """The commons_veterans pack (see the module docstring); files that name a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(VETERANS, limit, "pplveterans", adults_only=True)


def build_commons_immigration_documents(limit):
    """The commons_immigration_documents pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(IMMIGRATION_DOCUMENTS, limit, "pplimmigration")


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
PEOPLE_PACKS = {
    "commons_mobility_aids": (build_commons_mobility_aids, COMMONS_LICENCE.format(
        what="manual and sports wheelchair, orthosis, leg brace and accessible taxi")),
    "commons_hearing_communication": (build_commons_hearing_communication, COMMONS_LICENCE.format(
        what="hearing loop, audiometry, audiogram, captioning, subtitle, TTY, videophone, accessibility symbol, PECS "
             "and sensory room")),
    "commons_veterans": (build_commons_veterans, COMMONS_LICENCE.format(
        what="US military ribbon bar, decoration, badge, dog tag and folded flag")),
    "commons_immigration_documents": (build_commons_immigration_documents, COMMONS_LICENCE.format(
        what="US passport, visa, travel document and Social Security card")),
}
PEOPLE_LIMITS = {
    "commons_mobility_aids": 400,
    "commons_hearing_communication": 300,
    "commons_veterans": 500,
    "commons_immigration_documents": 200,
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS): all of them.
PEOPLE_COMMONS_KEYS = tuple(PEOPLE_PACKS)


def specs():
    """Every Commons category spec of the packs (for the self-test)."""
    return MOBILITY_AIDS + HEARING_COMMUNICATION + VETERANS + IMMIGRATION_DOCUMENTS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a people pack builder.")
    parser.add_argument("key", choices=sorted(PEOPLE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = PEOPLE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
