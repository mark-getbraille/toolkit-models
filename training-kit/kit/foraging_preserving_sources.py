"""EDIBLE WILD PLANTS AND FORAGING and HOME FOOD PRESERVING for the Picture Model Training Kit (the owner's request of
2026-11-22). This file lists:
  - the ready-made packs built in packs/foraging_preserving_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_wild_food_plants, commons_wild_mushrooms, commons_home_preserving and inat_wild_edibles;
  - the sources looked at for these subjects and left out, with the reason (FORAGING_PRESERVING_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only; iNaturalist photos
CC0 or CC BY only, read through GBIF and the iNaturalist Open Dataset, never the inaturalist.org site).

Answers say only what the Commons category or the research-grade observation names, with the lookalike or
preparation warning the reference books give, and end with the foraging, mushroom, poison or home preserving note,
the same words as the packs' (packs/test_foraging_preserving.py checks). No answer says a wild plant or mushroom is
safe to eat.

Picture-making (FORAGING_PRESERVING_PICTURE_MAKING_OK): the Commons plant, mushroom and preserved food collections
(plants, fungi and food, no people as their subject). The iNaturalist pack is for describing only, like the kit's
other iNaturalist packs.
Topics: the wild plants and mushrooms in the nature topic, the preserved foods in the food topic.

    python -c "import sources, foraging_preserving_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

# The notes, word for word as in packs/foraging_preserving_packs.py.
FORAGE_NOTE = ("Foraging: never eat a wild plant unless an expert has confirmed it in person; deadly lookalikes "
               "exist, and a picture is never enough.")
MUSHROOM_NOTE = ("Mushrooms: never eat a wild mushroom unless an expert has confirmed it in person; deadly ones look "
                 "like edible ones, and a picture is never enough. If someone ate a wild mushroom and feels ill, call "
                 "Poison Control at 1-800-222-1222 or 911.")
POISON_NOTE = ("Poisonous: never eat, taste or touch an unknown plant, and keep children and pets away; if someone "
               "may have eaten it, call Poison Control at 1-800-222-1222 (US), or 911 if they are very ill.")
PRESERVE_NOTE = ("Home preserving: follow tested, current recipes (the USDA Complete Guide to Home Canning); process "
                 "low-acid foods such as vegetables and meat in a pressure canner, adjust for altitude, and throw away "
                 "bulging, leaking or foul-smelling jars without tasting them: botulism can kill.")

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
INAT_OPEN = "Each photo CC0 or CC BY (its iNaturalist observation, read through GBIF)"
INAT_CREDIT = "iNaturalist observers, CC0 or CC BY, credited in ATTRIBUTION.txt (via GBIF, https://www.gbif.org)"

FORAGING_PRESERVING_SOURCES = [
    Source("commons_wild_food_plants", "Wild greens, berries, nuts, roots, flowers and seaweeds foragers gather "
                                       "(purslane, ramps, fiddleheads, cattail, pawpaw, elderberry, black walnut, "
                                       "dulse and more) and their poisonous lookalikes (autumn crocus, moonseed, "
                                       "bracken, fool's parsley, hemlock water-dropwort), with the foraging and "
                                       "poison notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 10, prepare_pack, "about 330 MB"),
    Source("commons_wild_mushrooms", "More wild mushrooms: honey fungus, parasol, shaggy ink cap, lion's mane, hen of "
                                     "the woods and others, and the poisonous and deadly ones (false parasol, sulphur "
                                     "tuft, deadly webcap, yellow stainer), each with the expert rule (Wikimedia "
                                     "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("commons_home_preserving", "Home preserving: mason, Weck and Kilner jars, pickles, sauerkraut, kimchi, "
                                      "jam, marmalade, chutney, dried fruit, jerky, dried, salted and smoked fish and "
                                      "freeze-dried food, with the home preserving and botulism note (Wikimedia "
                                      "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("inat_wild_edibles", "Wild edible plants, mushrooms and their deadly lookalikes in the United States and "
                                "Canada: ramps, fiddleheads, milkweed, pawpaw, elderberry, morels, hen of the woods, "
                                "destroying angels, water hemlock, moonseed and more (iNaturalist through GBIF, "
                                "ready-made pack)",
           INAT_OPEN, INAT_CREDIT, "permissive", 1600, 15, prepare_pack, "about 700 MB"),
]
FORAGING_PRESERVING_PICTURE_MAKING_OK = {"commons_wild_food_plants", "commons_wild_mushrooms",
                                         "commons_home_preserving"}
FORAGING_PRESERVING_NOT_INCLUDED = {
    "Commons categories already used by other packs": "the poisonous plants, the common edible and deadly mushrooms "
        "and wild carrot, ramsons, elder, nettle, dandelion, blackberry and highbush blueberry (plant_id_sources.py); "
        "Root cellars (homestead), Food dehydrators (devices), Smoked meat and Canned food (outdoor cooking), Pressure "
        "cookers (home).",
    "Commons categories that do not exist or are empty (2026-11-22)": "Canning jars, Pressure canners, Jams, Fruit "
        "preserves, Vacuum packing, Home canning (empty), Fermented foods (empty), Food dehydration (empty), "
        "Preserves (empty).",
    "Commons Canning": "Its name is the Open Images label Canning that outdoor_cooking_packs asks, so it is left out "
        "to keep the names apart; mason, Weck and Kilner jars are here.",
    "iNaturalist's website and API": "Never read (\"ai-train=no\" and a robots.txt that refuses programs); the photos "
        "come from GBIF's records and the iNaturalist Open Dataset only.",
    "Mushroom Observer and MushroomExpert photos": "Mixed or non-commercial licences, or copyright; not used.",
    "Ball, Kerr, Presto and other makers' product photos": "Copyright; not used.",
}
