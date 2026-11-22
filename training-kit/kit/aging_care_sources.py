"""AGING AND DAILY LIVING for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/aging_care_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_daily_living_aids;
  - the sources looked at for these subjects and left out, with the reason (AGING_CARE_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category names, with a plain line, and every answer ends with the note
(general information, not medical advice or a diagnosis; a doctor, nurse or occupational therapist can say which aid fits; 911; 988), the same words as the packs' (packs/test_health_life.py checks).

Picture-making (AGING_CARE_PICTURE_MAKING_OK): none (patient lifts are shown in use with people).
Topics: the health topic (Health and medical pictures).

    python -c "import sources, aging_care_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

AGING_CARE_SOURCES = [
    Source("commons_daily_living_aids", "Daily-living aids: patient lifts, jar openers, toilet seat risers, bedpans, "
                                        "incontinence pads and telecare alarms (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 150, 5, prepare_pack, "about 30 MB"),
]
AGING_CARE_PICTURE_MAKING_OK = set()
AGING_CARE_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Wheelchairs, Rollators, Walking sticks, Forearm crutches, "
        "Hearing aids, Stair lifts (disability_packs), Grab bars and Handrails (building_packs), Hospital beds, Knee "
        "scooters, Pill organizers (med_vet_packs), Compression stockings (home_health_packs).",
    "Commons categories that do not exist or hold no files (2026-11-22)": "Shower chairs, Shower seats, Reachers, "
        "Grabbers, Raised toilet seats, Bed rails, Lift chairs, Medical alert devices, Personal emergency response "
        "systems, Bed alarms, Automatic pill dispensers, Sock aids, Adaptive cutlery, Large button telephones, "
        "Transfer boards, Over-bed tables.",
    "Bath chairs, Adult diapers and Pillboxes on Commons": "Bath chairs are mostly the old wheeled chair from Bath; "
        "Adult diapers holds subcategories that may show people wearing them; Pillboxes are decorative boxes. Not "
        "used.",
    "Funerals, coffins and urns": "not asked for, and funeral photos can show the dead; not used.",
}
