"""Picture packs for CLEANING AND HOUSEHOLD MANAGEMENT (the owner's request of 2026-11-22). Used by build_packs.py in
the same way as its own PACKS (build_<key>(limit) returns [(file name, JPEG bytes or None, row)]).

Why: the owner wants the picture describer to name the cleaning tools and storage things in a photo (a broom and
dustpan, a mop and bucket, a squeegee, a toilet brush, rubber gloves, a spray bottle, a robot vacuum, a pantry or a
closet) and to say the cleaning safety rule: never mix cleaners.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed). Every
answer about cleaners, spray bottles, gloves or cleaning work ends with MIX_NOTE (never mix bleach with ammonia or
acids; one product at a time, fresh air, the label's directions; Poison Control), the same words as the kit's
practical_sources.py. The household chemical packs (commons_household_chemicals, chemical_packs) have the products
themselves; the laundry care label packs have laundry symbols.

The packs (HOUSEHOLD_PACKS):
  commons_cleaning_tools   Wikimedia Commons (CC0, public domain or CC BY files only): brooms, dustpans, mops and
                           mop buckets, cleaning sponges, feather dusters, squeegees, toilet
                           brushes, rubber gloves, spray bottles, dish racks, laundry baskets and
                           lint rollers; and organising: storage boxes, closets and pantries.
  open_images_cleaning     Open Images V7 (labels CC BY 4.0; photos CC BY, CC0 or the Public Domain Mark): cleaning
                           tools (dustpan, duster, squeegee, sponge), cleaning supplies (household
                           cleaning supply, cleaner, window cleaner, drain cleaner) and kitchen towels and paper towel
                           holders. No label is asked twice (packs/test_practical.py checks).

Not repeated here: device_packs (Vacuum cleaners), the packs that already ask Robotic vacuum cleaners and Window
cleaning (Commons) and Broom, Mop and Paper towel (Open Images), the household chemical and hazard packs, the laundry
packs, and the home repair and pest packs (home_crafts).

    python packs/household_packs.py commons_cleaning_tools --limit 8
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap
from outdoor_cooking_packs import thing, with_yes_notes

MIX_NOTE = ("Cleaning safety: never mix cleaning products; bleach mixed with ammonia, or with acids such as some "
            "toilet bowl and rust cleaners or vinegar, makes poisonous gas. Use one product at a time with fresh air, "
            "follow the label, and keep cleaners away from children. Poison Control: 1-800-222-1222 in the US.")

CLEANING_TOOLS = [
    thing("Brooms", "a broom for sweeping floors", "", True),
    thing("Dustpans", "a dustpan for sweeping dirt into"),
    thing("Mops", "a mop for washing floors", MIX_NOTE, True),
    thing("Mop buckets", "a mop bucket, often with a wringer to squeeze out the mop", MIX_NOTE),
    thing("Cleaning sponges", "a cleaning sponge", MIX_NOTE, True),
    thing("Feather dusters", "a feather duster for dusting"),
    thing("Squeegees", "a squeegee, a rubber blade for wiping water off windows, showers or floors"),
    thing("Toilet brushes", "a toilet brush", MIX_NOTE),
    thing("Rubber gloves", "rubber gloves for cleaning and washing up", MIX_NOTE, True),
    thing("Spray bottles", "a spray bottle; label it with what is inside, and never put a different cleaner in a "
                           "bottle without washing it out", MIX_NOTE),
    thing("Dish racks", "a dish rack for drying washed dishes"),
    thing("Laundry baskets", "a laundry basket", "", True),
    thing("Lint rollers", "a lint roller, a roll of sticky paper for lifting hair and fluff off clothes"),
    thing("Storage boxes", "storage boxes for organising things; labelled boxes (in large print or braille) make "
                           "things easy to find", "", True),
    thing("Closets", "a closet (wardrobe or cupboard) for clothes or storage", "", True),
    thing("Pantries", "a pantry, a cupboard or small room for storing food", "", True),
]


def build_commons_cleaning_tools(limit):
    """The commons_cleaning_tools pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CLEANING_TOOLS, limit, "cleaning")


CLEANING_OI = [
    group("What cleaning tools are in this picture?",
          {"Dustpan": "a dustpan", "Duster": "a duster", "Squeegee": "a squeegee",
           "Sponge (Tool)": "a sponge"}),
    group("What cleaning supplies are in this picture?",
          {"Household cleaning supply": "household cleaning supplies", "Cleaner": "a cleaner",
           "Window cleaner": "window cleaner", "Drain cleaner": "drain cleaner"}, MIX_NOTE),
    group("What towels are in this picture?",
          {"Kitchen towel": "a kitchen towel", "Paper towel holder": "a paper towel holder"}),
]


def build_open_images_cleaning(limit):
    """open_images_cleaning (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_cleaning", CLEANING_OI, limit, 9403), CLEANING_OI)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
HOUSEHOLD_PACKS = {
    "commons_cleaning_tools": (build_commons_cleaning_tools, COMMONS_LICENCE.format(
        what="broom, mop, sponge, duster, squeegee, glove, spray bottle, storage box, closet and pantry")),
    "open_images_cleaning": (build_open_images_cleaning, OI_LICENCE),
}
HOUSEHOLD_LIMITS = {
    "commons_cleaning_tools": 1000,   # 16 categories
    "open_images_cleaning": 800,      # 9 labels
}
HOUSEHOLD_COMMONS_KEYS = ("commons_cleaning_tools",)
HOUSEHOLD_SPECS = CLEANING_TOOLS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(HOUSEHOLD_PACKS, "Try a cleaning pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
