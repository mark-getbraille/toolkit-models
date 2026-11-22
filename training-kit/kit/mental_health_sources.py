"""MENTAL HEALTH AND WELLBEING for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/mental_health_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_wellbeing_aids;
  - the sources looked at for these subjects and left out, with the reason (MENTAL_HEALTH_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category names, with a plain line, and every answer ends with the note
(general information, not medical advice or a diagnosis; 911 in an emergency; call or text 988 in a mental health crisis; the quitline for the quitting things), the same words as the packs' (packs/test_health_life.py checks).

Picture-making (MENTAL_HEALTH_PICTURE_MAKING_OK): none (sleep masks and the like are often worn by people in their photos), so sources.py puts the pack in NOT_FOR_PICTURE_MAKING.
Topics: the home topic (Home and household): everyday things, no people's bodies and no medical photos.

    python -c "import sources, mental_health_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

MENTAL_HEALTH_SOURCES = [
    Source("commons_wellbeing_aids", "Calm, sleep and quitting aids: weighted blankets, fidget toys, stress balls, "
                                     "sleep masks, meditation cushions, nicotine patches and breathalyzers, with the "
                                     "988 and quitline notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 60 MB"),
]
MENTAL_HEALTH_PICTURE_MAKING_OK = set()
MENTAL_HEALTH_NOT_INCLUDED = {
    "Open Images labels for this subject": "Sleep mask, Earplug, Breathalyzer, Electronic cigarette, Massage and "
        "Blindfold have no or almost no human-checked photos in Open Images V7 (counted 2026-11-22); Meditation, Nap "
        "and Yoga are asked by other packs.",
    "Commons categories that do not exist or hold no files (2026-11-22)": "Light therapy, Light boxes (therapy), "
        "White noise machines, Meditation cushions, Nicotine gum, Nicotine lozenges; Earplugs exists but holds no "
        "files.",
    "Cigarettes, vapes and pipes": "the drugs packs' (commons_drug_paraphernalia): not repeated.",
    "Photos of people in distress, therapy sessions or hospitals": "not wanted: a describer should not guess anyone's "
        "mental state from a photo.",
}
