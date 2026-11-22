"""Picture packs for AGING AND DAILY LIVING (the owner's request of 2026-11-22, aging and end-of-life planning). Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)]. The limit counts pictures.

Why: the owner is blind and wants his offline assistant to recognise the daily-living aids older people and their
carers use at home that no other pack asks about yet: patient lifts, jar openers, toilet seat risers, bedpans,
incontinence pads and telecare alarms. Wheelchairs, walkers, rollators, canes, crutches, hearing aids, stair lifts,
grab bars, handrails, hospital beds, knee scooters, pill organisers and compression stockings are already asked by
disability_packs, building_packs, med_vet_packs and home_health_packs (packs/test_health_life.py checks that no
category is asked twice). End-of-life planning (advance directives, hospice, wills) is not pictures: the reference
books carry it (textbooks/aging_end_of_life.py).

Answers say only what the Commons category names (with a plain line written here), and every answer ends with the
aging note (the owner's health note, adapted):
  AGING_NOTE  "General information, not medical advice or a diagnosis: a doctor, nurse or occupational therapist can
              say which aid fits. In an emergency call 911; in a mental health crisis call or text 988."
Incontinence products are taken only when the file's own words name the product and not a person wearing it
(PRODUCT_ONLY); files whose words name a child are left out.

The pack (AGING_CARE_PACKS):
  commons_daily_living_aids  Wikimedia Commons (CC0, public domain or CC BY files only): patient lifts (hoists), jar
                             openers, toilet seat risers, bedpans, incontinence pads and telecare alarms.

Open Images was counted on 2026-11-22: Bath chair and the other daily-living labels have no human-checked photos, so
there is no Open Images pack. Commons "Bath chairs" is mostly the old wheeled chair from Bath, England, and is left
out. What was looked at and left out is in the kit's aging_care_sources.py.

    python packs/aging_care_packs.py commons_daily_living_aids --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

AGING_NOTE = ("General information, not medical advice or a diagnosis: a doctor, nurse or occupational therapist can "
              "say which aid fits. In an emergency call 911; in a mental health crisis call or text 988.")
ASK_WHAT = "What is this?"
# Incontinence pads: only the product itself, never a person wearing one.
PRODUCT_ONLY = re.compile(r"^(?!.*\b(wear\w*|worn|fetish\w*|abdl|nude|naked|underwear|model|person|woman|man|girl|"
                          r"boy|child|baby)\b).*\b(pads?|incontinence|pack\w*|products?|absorbent)\b", re.I | re.S)


def thing(category, words, deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the aging note)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}. {AGING_NOTE}")])
    return spec + (pattern,) if pattern else spec


DAILY_LIVING_AIDS = [
    thing("Patient lifts", "a patient lift (a hoist), which lifts a person between a bed, a chair and a toilet in a "
                           "sling; carers are trained to use one safely", True),
    thing("Jar openers", "a jar opener, a gripping tool that makes it easier to open jars and bottles", True),
    thing("Toilet seat risers", "a toilet seat riser (raised toilet seat), which makes the seat higher so sitting "
                                "down and standing up are easier"),
    thing("Bedpans", "a bedpan, a pan used as a toilet by someone who cannot get out of bed"),
    thing("Incontinence pads", "an incontinence pad, an absorbent pad for bladder leaks", pattern=PRODUCT_ONLY),
    thing("Telecare", "a telecare alarm, a button or pendant that calls for help at home (a personal emergency "
                      "response system)"),
]


def build_commons_daily_living_aids(limit):
    """The commons_daily_living_aids pack (see the module docstring); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(DAILY_LIVING_AIDS, limit, "dailyaids", adults_only=True)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
AGING_CARE_PACKS = {
    "commons_daily_living_aids": (build_commons_daily_living_aids, COMMONS_LICENCE.format(
        what="patient lift, jar opener, toilet seat riser, bedpan, incontinence pad and telecare")),
}
AGING_CARE_LIMITS = {
    "commons_daily_living_aids": 150,      # 6 categories, about 110 files
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
AGING_CARE_COMMONS_KEYS = ("commons_daily_living_aids",)
# The Commons category specs of the packs (for the self-test).
AGING_CARE_SPECS = list(DAILY_LIVING_AIDS)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the aging and daily living pack builder.")
    parser.add_argument("key", choices=sorted(AGING_CARE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = AGING_CARE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
