"""Picture packs for HOMESTEADING AND SMALL LIVESTOCK (the owner's request of 2026-11-22). Used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a
picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same
picture. The limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise the equipment and
animals of a small homestead (coops, nest boxes, beehives and beekeeping tools, honey extractors, cattle crushes,
sheep pens, wells, rainwater tanks, composting toilets, butter churns and cream separators) and to say the handling
and safety rules that go with each.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no breed, sex, age or health is named unless the category itself names it. Answers end with the safety notes
that fit (the same words in the kit's homestead_sources.py):
  HANDLING_NOTE  calm handling, an escape route, never between a mother and her young.
  POULTRY_NOTE   wash hands after touching poultry, eggs or pens (Salmonella); children under 5 and chicks.
  BEE_NOTE       veil and smoker, and stings and allergies.
  WELL_NOTE      test well water every year; never enter a septic tank, well pit or manure pit.
  POWER_NOTE     solar, battery and generator wiring by a qualified electrician.

The packs (HOMESTEAD_PACKS):
  commons_homestead_poultry_bees  Wikimedia Commons (CC0, public domain or CC BY files only): egg incubators, egg
                                  candling, chicken tractors, nest boxes, duck houses, beehives (Langstroth and top-bar), bee smokers, beekeeping
                                  suits, hive tools, honey extractors and honeycombs.
  commons_homestead_farmstead     Commons: cattle crushes (squeeze chutes), sheep pens, barbed-wire fences, hand
                                  milking, water wells, rainwater harvesting, root cellars, off-grid homes, composting toilets,
                                  butter churns and cream separators.
  open_images_homestead           Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                                  farm animals (chickens, roosters, ducks, geese, turkeys, goats, sheep, pigs, rabbits,
                                  cattle), beekeeping (honeycomb, beekeepers, apiaries), the farm (hay, barns, silos,
                                  chicken coops, pastures) and water wells. No label is asked twice (packs/test_homestead.py checks).

Not repeated here: the breeds packs (commons_breeds, na_domestic_animals: chicken, duck, goat, sheep, rabbit and pig
breeds), the farm packs (farm machinery), the Commons categories other packs ask (Chicken coops, Egg cartons, Sheep
shearing, Rabbit hutches, Hay bales, Electric fences, Ear tags, Hand pumps, Septic tanks, Fence posts, and the power packs' Wind
pumps) and the Open
Images labels other packs ask (Bee, Beehive, Honey, Fence, Egg, and the power packs' Solar panel,
Wind turbine and Windmill). What was looked at and left out is in the
kit's homestead_sources.py (HOMESTEAD_NOT_INCLUDED).

    python packs/homestead_packs.py commons_homestead_poultry_bees --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from outdoor_cooking_packs import with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

HANDLING_NOTE = ("Handling animals: move calmly and quietly, keep an escape route, and never step between a mother "
                 "animal and her young; be careful around bucks, rams, boars and roosters.")
POULTRY_NOTE = ("Hygiene: wash your hands with soap and water after touching poultry, eggs, feeders or pens "
                "(Salmonella); children under 5 should not handle chicks or ducklings.")
BEE_NOTE = ("Bees: wear a veil and use a smoker when opening a hive; anyone allergic to stings should keep their "
            "emergency medicine with them and not work bees alone. For trouble breathing after a sting, call 911.")
WELL_NOTE = ("Water: test well water every year for bacteria and nitrates; never climb into a well, cistern, septic "
             "tank or manure pit, where gases can kill in minutes.")
POWER_NOTE = "Power: solar, battery, inverter and generator wiring is work for a qualified electrician."
ASK_WHAT = "What is this?"


def thing(category, words, notes="", deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


# ----------------------------------------------------------------- Commons: poultry and bees

# Commons "Candling" may hold candle-making too: only files whose own words name eggs.
EGG_WORDS = re.compile(r"\b(eggs?|ovoscope|embryos?|hatch\w*|incubat\w*)\b", re.I)
POULTRY_BEES = [
    thing("Incubators (poultry)", "an egg incubator, which keeps eggs warm and turns them until they hatch",
          POULTRY_NOTE, True),
    thing("Incubators (eggs)", "an egg incubator", POULTRY_NOTE, True),
    thing("Candling", "egg candling: shining a bright light through an egg to see inside it", POULTRY_NOTE,
          pattern=EGG_WORDS),
    thing("Chicken tractors", "a chicken tractor, a movable coop without a floor that lets hens graze fresh ground",
          POULTRY_NOTE),
    thing("Nest boxes", "a nest box, where hens or other birds lay their eggs", POULTRY_NOTE, True),
    thing("Duck houses", "a duck house, a shelter for ducks", POULTRY_NOTE),
    thing("Beehives", "a beehive", BEE_NOTE),
    thing("Langstroth hives", "a Langstroth hive, a stack of boxes holding removable frames of comb", BEE_NOTE),
    thing("Top-bar hives", "a top-bar hive, a long box whose comb hangs from bars across the top", BEE_NOTE),
    thing("Bee smokers", "a bee smoker, a can with bellows that puffs cool smoke to calm bees", BEE_NOTE),
    thing("Beekeeping suits", "a beekeeping suit with a veil", BEE_NOTE),
    thing("Hive tools", "a hive tool, a flat metal bar for prying hive boxes and frames apart", BEE_NOTE),
    thing("Honey extractors", "a honey extractor, a drum that spins frames of comb to fling the honey out"),
    thing("Honeycombs", "honeycomb, the wax cells bees build for honey and young bees", deeper=True),
]

# ----------------------------------------------------------------- Commons: the farmstead

FARMSTEAD = [
    thing("Cattle crushes", "a cattle crush (squeeze chute), a strong stall that holds an animal still for care",
          HANDLING_NOTE),
    thing("Sheep pens", "a sheep pen", HANDLING_NOTE, True),
    thing("Barbed wire fences", "a barbed-wire fence",
          "Barbed wire cuts: wear gloves, and keep it tight so animals do not tangle in it."),
    thing("Water wells", "a water well", WELL_NOTE),
    thing("Rainwater harvesting", "rainwater harvesting: gutters, barrels or tanks that collect rain from a roof",
          "Collected rainwater is not safe to drink unless it is treated.", True),
    thing("Root cellars", "a root cellar, an underground store that keeps vegetables cool"),
    thing("Off-the-grid", "an off-grid home or system, one not connected to the public electricity or water network",
          POWER_NOTE, True),
    thing("Composting toilets", "a composting toilet, which turns waste into compost without water", deeper=True),
    thing("Milking by hand", "milking by hand", HANDLING_NOTE + " Wash hands and udders first, and keep milk cold.",
          True),
    thing("Butter churns", "a butter churn, which shakes or beats cream until it turns into butter"),
    thing("Cream separators", "a cream separator, which spins milk to separate the cream"),
]


def build_commons_homestead_poultry_bees(limit):
    """The commons_homestead_poultry_bees pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(POULTRY_BEES, limit, "hspoultrybees")


def build_commons_homestead_farmstead(limit):
    """The commons_homestead_farmstead pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FARMSTEAD, limit, "hsfarmstead")


# ----------------------------------------------------------------- Open Images

HOMESTEAD_OI = [
    group("What farm animals are in this picture?",
          {"Chicken": "a chicken", "Rooster": "a rooster", "Duck": "a duck", "Goose": "a goose", "Turkey": "a turkey",
           "Goat": "a goat", "Sheep": "a sheep", "Pig": "a pig", "Rabbit": "a rabbit", "Cattle": "cattle",
           "Poultry": "poultry", "Livestock": "livestock"}, HANDLING_NOTE),
    group("What beekeeping things are in this picture?",
          {"Honeycomb": "honeycomb", "Beekeeper": "a beekeeper", "Apiary": "an apiary (a bee yard)"}, BEE_NOTE),
    group("What farm buildings or land are in this picture?",
          {"Hay": "hay", "Barn": "a barn", "Silo": "a silo", "Chicken coop": "a chicken coop", "Farm": "a farm",
           "Ranch": "a ranch", "Pasture": "a pasture"}),
    group("Is there a water well in this picture?", {"Water well": "a water well"}, WELL_NOTE),
]


def build_open_images_homestead(limit):
    """open_images_homestead (see the module docstring); every "yes" answer carries its group's note too."""
    return with_yes_notes(build_oi_gap("open_images_homestead", HOMESTEAD_OI, limit, 9401), HOMESTEAD_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
HOMESTEAD_PACKS = {
    "commons_homestead_poultry_bees": (build_commons_homestead_poultry_bees, COMMONS_LICENCE.format(
        what="egg incubator, candling, chicken tractor, nest box, duck house, beehive, bee smoker, hive tool and honey extractor")),
    "commons_homestead_farmstead": (build_commons_homestead_farmstead, COMMONS_LICENCE.format(
        what="cattle crush, sheep pen, fence, hand milking, well, rainwater, root cellar, off-grid, composting toilet, butter churn "
             "and cream separator")),
    "open_images_homestead": (build_open_images_homestead, OI_LICENCE),
}
HOMESTEAD_LIMITS = {
    "commons_homestead_poultry_bees": 800,   # 14 categories; Beehives and Honeycombs have most files
    "commons_homestead_farmstead": 800,      # 11 categories
    "open_images_homestead": 1500,           # 23 labels; farm animals have most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
HOMESTEAD_COMMONS_KEYS = ("commons_homestead_poultry_bees", "commons_homestead_farmstead")
# The Commons category specs of the packs (for the self-test).
HOMESTEAD_SPECS = POULTRY_BEES + FARMSTEAD


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a homestead pack builder.")
    parser.add_argument("key", choices=sorted(HOMESTEAD_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = HOMESTEAD_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
