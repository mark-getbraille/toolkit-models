"""WILDERNESS AND REMOTE FIRST AID for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/wilderness_first_aid_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_wilderness_rescue;
  - the sources looked at for these subjects and left out, with the reason (WILDERNESS_FIRST_AID_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category names, with a plain line, and every answer ends with the note
(general information, not training, medical advice or a diagnosis; 911 or the SOS of a satellite messenger or PLB; take a wilderness first aid course), the same words as the packs' (packs/test_health_life.py checks).

Picture-making (WILDERNESS_FIRST_AID_PICTURE_MAKING_OK): none (mountain rescue photos show rescuers and the people they carry: WILDERNESS_FIRST_AID_BODILY_KEYS, describing only).
Topics: the health topic (Health and medical pictures), beside the first aid supplies.

    python -c "import sources, wilderness_first_aid_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

WILDERNESS_FIRST_AID_SOURCES = [
    Source("commons_wilderness_rescue", "Wilderness rescue gear: mountain rescue, rescue sleds, avalanche "
                                        "transceivers, trauma shears and hand warmers, with the 911 and SOS note "
                                        "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 200, 5, prepare_pack, "about 45 MB"),
]
WILDERNESS_FIRST_AID_PICTURE_MAKING_OK = set()
# The packs that show people (describing only; added to sources.PEOPLE_AND_BODILY_PACK_KEYS).
WILDERNESS_FIRST_AID_BODILY_KEYS = ("commons_wilderness_rescue",)
WILDERNESS_FIRST_AID_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Splints, Stretchers, Triangular bandages, tourniquets and "
        "first aid kits (med_vet_packs), space blankets and tick removal (home_health_packs), camp water filters and "
        "purification tablets (outdoor_cooking_packs); ticks, snakes, spiders, scorpions and poisonous plants are "
        "the nature packs' (na_animal_packs) and the plant identification collection's.",
    "Commons categories that do not exist (2026-11-22)": "Personal locator beacons, Emergency position-indicating "
        "radio beacons, Satellite messengers, Garmin inReach, SAM splints, Improvised splints, Improvised "
        "stretchers, Stokes baskets, Snakebite kits, Elastic bandages, Blister plasters, Signal mirrors, Emergency "
        "whistles, Bivouac sacks, Avalanche probes, Survival kits.",
    "Photos of injuries, wounds and venomous bites": "gore is not wanted; files whose words name blood, wounds, "
        "injuries, victims or deaths are left out of the rescue photos.",
    "NOLS, WMA, SOLO and Red Cross course pictures": "copyright; not used.",
}
