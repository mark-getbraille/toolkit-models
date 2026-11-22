"""Picture packs for PLANT IDENTIFICATION (the owner's request of 2026-11-22). Used by build_packs.py in the same way
as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture
with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The
limit counts pictures.

Why: the toolkit already has large plant collections (iNaturalist through GBIF and its open-data bucket, Pl@ntNet,
PlantVillage, the weed and plant disease packs, the garden packs, gbif_species). These packs fill the gaps the owner
named: poisonous plants and their edible lookalikes, mushrooms (the deadly ones and the ones people pick), wild edible
plants, and tree bark and leaf shapes. Every answer says the safety rule that fits:
  POISON_NOTE    never eat or touch an unknown plant; Poison Control 1-800-222-1222; children and pets.
  SKIN_NOTE      poison ivy, oak and sumac, giant hogweed and wild parsnip sap: wash skin and clothes.
  MUSHROOM_NOTE  never eat a wild mushroom unless an expert has identified it in person; deadly lookalikes.
  FORAGE_NOTE    never eat a wild plant unless an expert has confirmed it in person; lookalikes.
(The kit's plant_id_sources.py uses the same words; packs/test_leisure_packs.py checks.)

Answers say only what the source says: the Commons category's name (the plant's scientific name, with its usual
English name) and, for a lookalike, the dangerous plant it is confused with as the books describe it. No answer says
a plant is safe to eat.

The packs (PLANT_ID_PACKS):
  commons_poisonous_plants     Wikimedia Commons (CC0, public domain or CC BY files only): poison ivy, poison oak
                               and poison sumac, water hemlock, poison hemlock, giant hogweed, wild parsnip,
                               pokeweed, castor bean, oleander, foxglove, yew, bittersweet nightshade, jimsonweed,
                               monkshood, false hellebore, lily of the valley, dumb cane (Dieffenbachia) and the
                               Commons category of poisonous plants.
  commons_mushrooms_id         Commons: the death cap, destroying angels, fly agaric, deadly Galerina, false morel and
                               jack-o'-lantern mushroom, and the mushrooms people pick (morels, chanterelles, oyster
                               mushrooms, porcini, chicken of the woods, giant puffballs and edible mushrooms), every
                               one with the expert rule and its deadly lookalikes.
  commons_wild_plants_bark     Commons: wild carrot (Queen Anne's lace), wild garlic (ramsons), elder, stinging
                               nettle, dandelion, blackberry, highbush blueberry and staghorn sumac, edible plants and
                               foraging, tree bark and leaf shapes.

    python packs/plant_id_packs.py commons_mushrooms_id --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import QUICK

POISON_NOTE = ("Poisonous: never eat, taste or touch an unknown plant, and keep children and pets away; if someone "
               "may have eaten it, call Poison Control at 1-800-222-1222 (US), or 911 if they are very ill.")
SKIN_NOTE = ("Its sap or oil can burn or blister skin: do not touch it; wash skin with soap and water and wash "
             "clothes and tools that touched it.")
MUSHROOM_NOTE = ("Mushrooms: never eat a wild mushroom unless an expert has identified it in person; deadly ones "
                 "(the death cap and destroying angels) look like edible ones, and a picture is never enough. If "
                 "someone ate a wild mushroom and feels ill, call Poison Control at 1-800-222-1222 or 911.")
FORAGE_NOTE = ("Foraging: never eat a wild plant unless an expert has confirmed it in person; deadly lookalikes "
               "exist, and a picture is never enough.")
ASK_PLANT = "What plant is this?"
ASK_MUSHROOM = "What mushroom is this?"


def plant(category, words, notes, deeper=False, ask=ASK_PLANT):
    """A Commons spec: (category, deeper, [(question, "This is <words>." and the notes)])."""
    return (category, deeper, [(ask, f"This is {words}. {notes}")])


POISONOUS = [
    plant("Toxicodendron radicans", "poison ivy (Toxicodendron radicans), whose leaves grow in threes",
          f"{SKIN_NOTE} {POISON_NOTE}"),
    plant("Toxicodendron diversilobum", "Pacific poison oak (Toxicodendron diversilobum)", f"{SKIN_NOTE} {POISON_NOTE}"),
    plant("Toxicodendron vernix", "poison sumac (Toxicodendron vernix)", f"{SKIN_NOTE} {POISON_NOTE}"),
    plant("Cicuta maculata", "spotted water hemlock (Cicuta maculata), one of the most poisonous plants in North "
                             "America; it looks like wild carrot and parsnip", POISON_NOTE),
    plant("Cicuta virosa", "cowbane (Cicuta virosa), a water hemlock", POISON_NOTE),
    plant("Conium maculatum", "poison hemlock (Conium maculatum); it looks like wild carrot and parsley",
          POISON_NOTE),
    plant("Heracleum mantegazzianum", "giant hogweed (Heracleum mantegazzianum)", f"{SKIN_NOTE} {POISON_NOTE}"),
    plant("Pastinaca sativa", "wild parsnip (Pastinaca sativa), whose sap burns skin in sunlight",
          f"{SKIN_NOTE} {POISON_NOTE}"),
    plant("Phytolacca americana", "pokeweed (Phytolacca americana)", POISON_NOTE),
    plant("Ricinus communis", "castor bean (Ricinus communis), whose seeds are very poisonous", POISON_NOTE),
    plant("Nerium oleander", "oleander (Nerium oleander)", POISON_NOTE),
    plant("Digitalis purpurea", "foxglove (Digitalis purpurea)", POISON_NOTE),
    plant("Taxus baccata", "yew (Taxus baccata)", POISON_NOTE),
    plant("Solanum dulcamara", "bittersweet nightshade (Solanum dulcamara)", POISON_NOTE),
    plant("Datura stramonium", "jimsonweed (Datura stramonium)", POISON_NOTE),
    plant("Aconitum napellus", "monkshood (Aconitum napellus)", POISON_NOTE),
    plant("Veratrum viride", "false hellebore (Veratrum viride)", POISON_NOTE),
    plant("Convallaria majalis", "lily of the valley (Convallaria majalis); its leaves look like wild garlic's",
          POISON_NOTE),
    plant("Dieffenbachia", "dumb cane (Dieffenbachia), a houseplant poisonous to people and pets", POISON_NOTE, True),
    plant("Poisonous plants", "a poisonous plant", POISON_NOTE),
]
MUSHROOMS = [
    plant("Amanita phalloides", "the death cap (Amanita phalloides), a deadly mushroom", MUSHROOM_NOTE,
          ask=ASK_MUSHROOM),
    plant("Amanita virosa", "a destroying angel (Amanita virosa), a deadly white mushroom", MUSHROOM_NOTE,
          ask=ASK_MUSHROOM),
    plant("Amanita bisporigera", "a destroying angel (Amanita bisporigera), a deadly white mushroom", MUSHROOM_NOTE,
          ask=ASK_MUSHROOM),
    plant("Amanita muscaria", "the fly agaric (Amanita muscaria), a poisonous mushroom", MUSHROOM_NOTE,
          ask=ASK_MUSHROOM),
    plant("Galerina marginata", "the deadly Galerina (Galerina marginata)", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Gyromitra esculenta", "a false morel (Gyromitra esculenta), poisonous, which looks like true morels",
          MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Omphalotus olearius", "the jack-o'-lantern mushroom (Omphalotus olearius), poisonous, which looks like "
                                 "chanterelles", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Morchella", "a morel (Morchella); false morels look like it", MUSHROOM_NOTE, True, ASK_MUSHROOM),
    plant("Cantharellus cibarius", "a chanterelle (Cantharellus cibarius); the jack-o'-lantern mushroom looks like "
                                   "it", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Pleurotus ostreatus", "an oyster mushroom (Pleurotus ostreatus)", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Boletus edulis", "a porcini or king bolete (Boletus edulis)", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Laetiporus sulphureus", "chicken of the woods (Laetiporus sulphureus), a shelf fungus on trees",
          MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Calvatia gigantea", "a giant puffball (Calvatia gigantea); young deadly Amanitas can look like small "
                               "puffballs", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
    plant("Edible mushrooms", "a mushroom that the Commons category lists as edible", MUSHROOM_NOTE, ask=ASK_MUSHROOM),
]
WILD_BARK = [
    plant("Daucus carota", "wild carrot or Queen Anne's lace (Daucus carota); deadly poison hemlock and water hemlock "
                           "look like it", FORAGE_NOTE),
    plant("Allium ursinum", "wild garlic or ramsons (Allium ursinum); poisonous lily of the valley and autumn crocus "
                            "leaves look like it", FORAGE_NOTE),
    plant("Sambucus nigra", "elder (Sambucus nigra); its leaves, stems, roots and unripe or raw berries are "
                            "poisonous", FORAGE_NOTE),
    plant("Urtica dioica", "stinging nettle (Urtica dioica), whose hairs sting the skin", FORAGE_NOTE),
    plant("Taraxacum officinale", "dandelion (Taraxacum officinale)", FORAGE_NOTE),
    plant("Rubus fruticosus", "blackberry (Rubus fruticosus)", FORAGE_NOTE),
    plant("Vaccinium corymbosum", "highbush blueberry (Vaccinium corymbosum)", FORAGE_NOTE),
    plant("Rhus typhina", "staghorn sumac (Rhus typhina), with red fuzzy fruit clusters; poison sumac has white "
                          "berries and grows in wet places", FORAGE_NOTE),
    plant("Edible plants", "a plant the Commons category lists as edible", FORAGE_NOTE),
    plant("Foraging", "foraging: gathering wild food", FORAGE_NOTE, True),
    ("Bark (botany)", False, [("What is this?", "This is tree bark. Bark's texture (smooth, peeling, ridged or "
                                                "flaky) is one way to tell trees apart, also by touch.")]),
    ("Leaf shapes", True, [("What is this?", "This shows leaf shapes, used to identify plants (by the edge, the vein "
                                             "pattern and how leaves are arranged).")]),
]


def build_commons_poisonous_plants(limit):
    """The commons_poisonous_plants pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(POISONOUS, limit, "pidpoison")


def build_commons_mushrooms_id(limit):
    """The commons_mushrooms_id pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MUSHROOMS, limit, "pidmush")


def build_commons_wild_plants_bark(limit):
    """The commons_wild_plants_bark pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(WILD_BARK, limit, "pidwild")


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
PLANT_ID_PACKS = {
    "commons_poisonous_plants": (build_commons_poisonous_plants, COMMONS_LICENCE.format(
        what="poisonous plant (poison ivy, oak and sumac, hemlocks, hogweed, nightshade and others)")),
    "commons_mushrooms_id": (build_commons_mushrooms_id, COMMONS_LICENCE.format(
        what="deadly, poisonous and edible mushroom species")),
    "commons_wild_plants_bark": (build_commons_wild_plants_bark, COMMONS_LICENCE.format(
        what="wild edible plant, lookalike, foraging, bark and leaf shape")),
}
PLANT_ID_LIMITS = {
    "commons_poisonous_plants": 1000,     # 20 categories
    "commons_mushrooms_id": 900,          # 14 categories
    "commons_wild_plants_bark": 800,      # 12 categories
}
PLANT_ID_COMMONS_KEYS = tuple(PLANT_ID_PACKS)
PLANT_ID_SPECS = POISONOUS + MUSHROOMS + WILD_BARK


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a plant identification pack builder.")
    parser.add_argument("key", choices=sorted(PLANT_ID_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    QUICK["on"] = False
    entries = PLANT_ID_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
