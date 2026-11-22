"""Picture packs for MENTAL HEALTH AND WELLBEING (the owner's request of 2026-11-22). Used by build_packs.py in the same
way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]. The limit
counts pictures.

Why: the owner is blind and wants his offline assistant to recognise the everyday things people use for calm, sleep
and quitting (weighted blankets, fidget toys, stress balls, sleep masks, meditation cushions, nicotine patches and
breathalyzers) and to say the help that goes with them. Most of mental health is not pictures: the reference books
(textbooks/mental_health.py) carry it.

Answers say only what the Commons category names (with a plain line written here), never a diagnosis, and every
answer ends with the health note (the owner's words):
  HEALTH_NOTE  "General information, not medical advice or a diagnosis. In an emergency call 911; in a mental health
               crisis call or text 988."
with, for the quitting things, the free quitline (QUIT_NOTE, 1-800-QUIT-NOW, CDC) and, for breathalyzers, never
drinking and driving (DRIVE_NOTE).

The pack (MENTAL_HEALTH_PACKS):
  commons_wellbeing_aids  Wikimedia Commons (CC0, public domain or CC BY files only): weighted blankets, fidget
                          spinners and fidget toys, stress balls, sleep masks, zafus (meditation cushions), nicotine
                          patches and nicotine replacement therapy, and breathalyzers. Files whose words name a child
                          are left out.

Open Images was counted for this subject on 2026-11-22 (Sleep mask, Earplug, Breathalyzer, Massage, Meditation and
others): almost no human-checked photos, or asked by other packs already, so there is no Open Images pack. Cigarettes,
vapes and pipes are the drugs packs' (drug_firearm_packs); meditation and yoga photos of people are the people and
expression packs'. What was looked at and left out is in the kit's mental_health_sources.py.

    python packs/mental_health_packs.py commons_wellbeing_aids --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

HEALTH_NOTE = ("General information, not medical advice or a diagnosis. In an emergency call 911; in a mental health "
               "crisis call or text 988.")
QUIT_NOTE = "Free help to quit smoking: call the quitline, 1-800-QUIT-NOW (CDC)."
DRIVE_NOTE = "Never drink and drive."
ASK_WHAT = "What is this?"


def thing(category, words, notes=HEALTH_NOTE, deeper=False):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]); the notes always end with the health note."""
    if not notes.endswith(HEALTH_NOTE):
        notes = f"{notes} {HEALTH_NOTE}"
    return (category, deeper, [(ASK_WHAT, f"This is {words}. {notes}")])


WELLBEING_AIDS = [
    thing("Weighted blankets", "a weighted blanket, a blanket made heavy with beads or pellets sewn into it"),
    thing("Fidget spinners", "a fidget spinner, a small toy that spins between the fingers"),
    thing("Fidget toys", "a fidget toy, a small object for keeping the hands busy"),
    thing("Stress balls", "a stress ball, a soft ball to squeeze in the hand"),
    thing("Sleep masks", "a sleep mask, which covers the eyes to block out light"),
    thing("Zafu", "a zafu, a round cushion for sitting meditation"),
    thing("Nicotine patches", "a nicotine patch, a skin patch that releases nicotine to help people quit smoking; use "
                              "it as its label directs", QUIT_NOTE),
    thing("Nicotine replacement therapy", "nicotine replacement therapy (patches, gum, lozenges, inhalers or nasal "
                                          "spray), medicines that help people quit smoking; use them as the label "
                                          "directs", QUIT_NOTE),
    thing("Breathalyzers", "a breathalyzer, a device that measures the alcohol in a person's breath", DRIVE_NOTE),
]


def build_commons_wellbeing_aids(limit):
    """The commons_wellbeing_aids pack (see the module docstring); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(WELLBEING_AIDS, limit, "wellbeing", adults_only=True)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
MENTAL_HEALTH_PACKS = {
    "commons_wellbeing_aids": (build_commons_wellbeing_aids, COMMONS_LICENCE.format(
        what="weighted blanket, fidget toy, stress ball, sleep mask, meditation cushion, nicotine replacement and "
             "breathalyzer")),
}
MENTAL_HEALTH_LIMITS = {
    "commons_wellbeing_aids": 300,         # 9 categories, few files each (about 270)
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
MENTAL_HEALTH_COMMONS_KEYS = ("commons_wellbeing_aids",)
# The Commons category specs of the packs (for the self-test).
MENTAL_HEALTH_SPECS = list(WELLBEING_AIDS)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a mental health pack builder.")
    parser.add_argument("key", choices=sorted(MENTAL_HEALTH_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = MENTAL_HEALTH_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
