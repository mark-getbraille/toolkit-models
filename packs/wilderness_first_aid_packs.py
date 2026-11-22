"""Picture packs for WILDERNESS AND REMOTE FIRST AID (the owner's request of 2026-11-22: first aid when help is hours
or days away). Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and
returns [(file name, JPEG bytes or None, row)]. The limit counts pictures.

Why: the owner is blind and wants his offline assistant to recognise the rescue and first-aid gear of the backcountry
that no other pack asks about yet, and to say plainly what to do: call 911, or use the SOS of a satellite messenger
or a personal locator beacon where there is no signal. The reference books (textbooks/wilderness_first_aid.py) carry
the first aid itself.

Answers say only what the Commons category names (with a plain line written here), and every answer ends with the
wilderness note, the same words as the reference books' (packs/test_health_life.py checks):
  WILD_NOTE  "General information, not training, medical advice or a diagnosis. In an emergency call 911, or use the
             SOS of a satellite messenger or a personal locator beacon (PLB) where there is no phone signal. Take a
             wilderness first aid course before you go."
Mountain rescue photos show rescuers at work (describing only); files whose words name an injury, blood or a body
are left out (NO_GORE), and files naming a child too.

The pack (WILDERNESS_FIRST_AID_PACKS):
  commons_wilderness_rescue  Wikimedia Commons (CC0, public domain or CC BY files only): mountain rescue, rescue
                             sleds, avalanche transceivers, trauma shears and hand warmers.

Already packs, and not asked again: splints, stretchers, triangular bandages, tourniquets and first aid kits
(med_vet_packs), space blankets and tick removal (home_health_packs), camp water filters, purification tablets and
canteens (outdoor_cooking_packs), ticks, snakes, spiders, scorpions and poisonous plants (the nature packs:
na_animal_packs and the plant identification collection). Commons has no category of personal locator beacons,
satellite messengers, snakebite kits, SAM splints, blister plasters or signal mirrors (checked 2026-11-22), so they
cannot be pictured here. What was looked at and left out is in the kit's wilderness_first_aid_sources.py.

    python packs/wilderness_first_aid_packs.py commons_wilderness_rescue --limit 8      (prints a few rows)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

WILD_NOTE = ("General information, not training, medical advice or a diagnosis. In an emergency call 911, or use the "
             "SOS of a satellite messenger or a personal locator beacon (PLB) where there is no phone signal. Take a "
             "wilderness first aid course before you go.")
ASK_WHAT = "What is this?"
# Rescue photos: never one whose own words name an injury, blood, a body or a death.
NO_GORE = re.compile(r"^(?!.*\b(blood\w*|bleed\w*|wound\w*|injur\w*|corpse\w*|bod(y|ies)|dead|death|died|killed|"
                     r"fatal\w*|victims?|accident\w*|crash\w*|ouch|hurt|pain\w*|casualt\w*)\b)", re.I | re.S)


def thing(category, words, deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the wilderness note)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}. {WILD_NOTE}")])
    return spec + (pattern,) if pattern else spec


WILDERNESS_RESCUE = [
    thing("Mountain rescue", "mountain rescue: trained rescuers reaching, treating and carrying out people in the "
                             "mountains", pattern=NO_GORE),
    thing("Rescue sleds", "a rescue sled, a sled for carrying an injured person over snow", pattern=NO_GORE),
    thing("Avalanche transceivers", "an avalanche transceiver (beacon), worn by each person in avalanche terrain: it "
                                    "sends a signal, and the others switch theirs to search to find someone buried"),
    thing("Trauma shears", "trauma shears, blunt-tipped scissors for cutting away clothing and bandages", True),
    thing("Hand warmers", "a hand warmer, a small pack or device that gives off heat to warm cold hands"),
]


def build_commons_wilderness_rescue(limit):
    """The commons_wilderness_rescue pack (see the module docstring); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(WILDERNESS_RESCUE, limit, "wildrescue", adults_only=True)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
WILDERNESS_FIRST_AID_PACKS = {
    "commons_wilderness_rescue": (build_commons_wilderness_rescue, COMMONS_LICENCE.format(
        what="mountain rescue, rescue sled, avalanche transceiver, trauma shears and hand warmer")),
}
WILDERNESS_FIRST_AID_LIMITS = {
    "commons_wilderness_rescue": 200,      # 5 categories, about 180 files
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
WILDERNESS_FIRST_AID_COMMONS_KEYS = ("commons_wilderness_rescue",)
# The Commons category specs of the packs (for the self-test).
WILDERNESS_FIRST_AID_SPECS = list(WILDERNESS_RESCUE)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the wilderness first aid pack builder.")
    parser.add_argument("key", choices=sorted(WILDERNESS_FIRST_AID_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = WILDERNESS_FIRST_AID_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
