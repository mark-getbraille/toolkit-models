"""PLANT IDENTIFICATION for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/plant_id_packs.py (group "permissive"; the kit downloads them with
    prepare_pack);
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (PLANT_ID_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it, only when the user ticks the matching
choice. Every licence was checked at its source in November 2026.

These packs fill gaps in the kit's large plant collections (inaturalist and gbif_species through GBIF and the
open-data bucket, never the inaturalist.org site; plantnet; plantvillage; the weed, disease and garden packs):
poisonous plants and lookalikes, mushrooms, wild edible plants, bark and leaf shapes. Every answer ends with the
poison, skin, mushroom or foraging note, the same words as the packs' (packs/test_leisure_packs.py checks); no answer
says a plant is safe to eat.

Picture-making (PLANT_ID_PICTURE_MAKING_OK): the Commons plant collections (plants, no people).
Topics: in the nature topic.

    python -c "import sources, plant_id_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The notes, word for word as in packs/plant_id_packs.py.
POISON_NOTE = ("Poisonous: never eat, taste or touch an unknown plant, and keep children and pets away; if someone "
               "may have eaten it, call Poison Control at 1-800-222-1222 (US), or 911 if they are very ill.")
SKIN_NOTE = ("Its sap or oil can burn or blister skin: do not touch it; wash skin with soap and water and wash "
             "clothes and tools that touched it.")
MUSHROOM_NOTE = ("Mushrooms: never eat a wild mushroom unless an expert has identified it in person; deadly ones "
                 "(the death cap and destroying angels) look like edible ones, and a picture is never enough. If "
                 "someone ate a wild mushroom and feels ill, call Poison Control at 1-800-222-1222 or 911.")
FORAGE_NOTE = ("Foraging: never eat a wild plant unless an expert has confirmed it in person; deadly lookalikes "
               "exist, and a picture is never enough.")

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


def gear(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# Categories of packs/plant_id_packs.py, the same answers.
PLANT_ID_SA = [
    ("Toxicodendron radicans", "What plant is this?", "This is poison ivy (Toxicodendron radicans), whose leaves grow "
                                                      f"in threes. {SKIN_NOTE} {POISON_NOTE}", False),
    ("Conium maculatum", "What plant is this?", "This is poison hemlock (Conium maculatum); it looks like wild carrot "
                                                f"and parsley. {POISON_NOTE}", False),
    ("Cicuta maculata", "What plant is this?", "This is spotted water hemlock (Cicuta maculata), one of the most "
                                               "poisonous plants in North America; it looks like wild carrot and "
                                               f"parsnip. {POISON_NOTE}", False),
    ("Amanita phalloides", "What mushroom is this?", "This is the death cap (Amanita phalloides), a deadly mushroom. "
                                                     + MUSHROOM_NOTE, False),
    ("Amanita virosa", "What mushroom is this?", "This is a destroying angel (Amanita virosa), a deadly white "
                                                 "mushroom. " + MUSHROOM_NOTE, False),
    ("Cantharellus cibarius", "What mushroom is this?", "This is a chanterelle (Cantharellus cibarius); the "
                                                        f"jack-o'-lantern mushroom looks like it. {MUSHROOM_NOTE}",
     False),
    ("Daucus carota", "What plant is this?", "This is wild carrot or Queen Anne's lace (Daucus carota); deadly poison "
                                             f"hemlock and water hemlock look like it. {FORAGE_NOTE}", False),
    ("Bark (botany)", "What is this?", "This is tree bark. Bark's texture (smooth, peeling, ridged or flaky) is one "
                                       "way to tell trees apart, also by touch.", False),
]


def prepare_plant_id_commons_sa(source, data_dir, work, cap):
    """Commons poisonous plant, deadly and edible mushroom, wild carrot and bark categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(PLANT_ID_SA, cap, source.test, "plant-id-commons-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


PLANT_ID_SOURCES = [
    Source("commons_poisonous_plants", "Poisonous plants and lookalikes: poison ivy, oak and sumac, water and poison hemlock, giant hogweed, wild parsnip, castor bean, oleander, foxglove, yew, nightshade, jimsonweed, monkshood and more, with poison and skin notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 220 MB"),
    Source("commons_mushrooms_id", "Mushrooms: the death cap, destroying angels, fly agaric, deadly Galerina, false morels and jack-o'-lanterns, and morels, chanterelles, oyster mushrooms, porcini, chicken of the woods and puffballs, each with the expert rule (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_wild_plants_bark", "Wild edible plants and their deadly lookalikes, foraging, tree bark and leaf shapes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("plant_id_commons_sa", "Wikimedia Commons: poison ivy, the hemlocks, the death cap and destroying angel, chanterelles, wild carrot and tree bark, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 400, 10, prepare_plant_id_commons_sa, "about 100 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons plants and mushrooms (no people).
PLANT_ID_PICTURE_MAKING_OK = {"commons_poisonous_plants", "commons_mushrooms_id", "commons_wild_plants_bark",
                              "plant_id_commons_sa"}

PLANT_ID_NOT_INCLUDED = {
    "Plant collections that exist": "inaturalist, inaturalist_us, inaturalist_ca and gbif_species (GBIF and the "
        "iNaturalist open-data bucket, never the inaturalist.org site), plantnet, plantvillage, plantdoc, the weed "
        "packs (agml_weeds, plant_seedlings), the garden packs and commons_breeds: not repeated.",
    "ASPCA toxic plant photos and list": "Copyright of the ASPCA; link-only.",
    "MushroomExpert.com and Mushroom Observer": "MushroomExpert is copyright; Mushroom Observer's photos carry "
        "mixed licences (many non-commercial) and are reached through GBIF already.",
    "FDA Poisonous Plant Database pictures": "Retired (404, November 2026).",
    "Houseplants": "Commons Houseplants is another pack's category; the poisonous houseplant Dieffenbachia is here.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the plant identification share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PLANT_ID_SOURCES if s.key == "plant_id_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="plant_id-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
