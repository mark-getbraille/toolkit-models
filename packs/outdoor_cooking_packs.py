"""Picture packs for EMERGENCY COOKING, CAMP COOKING, and GRILLS AND SMOKERS (the owner's request of 2026-11-22). Used
by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row)
rows naming the same picture. The limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise camp stoves and their
fuel, grills, smokers, Dutch ovens, coolers, water filters and solar cookers, and to say the safety rules that go with
each one. He prefers modern equipment, so nothing here is chosen for being old.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no brand, model, temperature or fuel is named unless the category itself names it. Every answer about a stove,
grill, smoker, fire, fuel, food or water ends with the safety notes that fit it (the same words in the kit's
outdoor_cooking_sources.py):
  CO_NOTE       carbon monoxide: grills, camp stoves, charcoal and generators only outdoors; get out and call 911
                if a CO alarm sounds or anyone feels ill.
  FIRE_NOTE     fire: away from tents, buildings and branches, never left alone, water or an extinguisher near.
  CAMPFIRE_NOTE fire restrictions, and drown, stir and feel the ashes until they are cold (US Forest Service).
  PROPANE_NOTE  leak test with soapy water, never a flame; cylinders upright, outdoors, valve closed.
  HOT_NOTE      hot surfaces stay hot long after cooking.
  TEMP_NOTE     USDA safe minimum internal temperatures, checked with a food thermometer.
  WATER_NOTE    boil water 1 minute (3 above 6,500 feet) when unsure (CDC).
  OUTAGE_NOTE   food in a fridge or freezer after a power cut, "when in doubt, throw it out" (USDA).

The packs (OUTDOOR_COOKING_PACKS):
  commons_camp_cooking        Wikimedia Commons (CC0, public domain or CC BY files only): camp and backpacking stoves
                              (Primus, Optimus, Svea, Trangia, Esbit, cassette gas stoves, Campingaz), mess
                              kits, billycans and canteens, coolers, Dutch ovens and cast-iron cookware, campfire
                              cooking and cooking cranes, campfires, and portable water filters and purification
                              tablets.
  commons_emergency_cooking   Commons: solar cookers, hayboxes (fireless cookers), chafing dishes and Sterno canned
                              heat, beverage-can (alcohol) stoves, field kitchens, water barrels, canned food and
                              lightweight water purifiers.
  commons_grills_smokers      Commons: grills, charcoal and kettle grills (Weber), kamado grills (Big Green Egg),
                              pellet grills, smokehouses, griddles, chimney starters, disposable barbecues, outdoor
                              kitchens and propane (LPG) cylinders.
  commons_barbecue_food       Commons: barbecue as a cooking method, grilled meats, smoked meat, pork and sausages,
                              pulled pork, ribs, burnt ends, Texas barbecue, Argentine asado and parrillas.
  open_images_outdoor_cooking Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                              grilling, campfires and bonfires, charcoal and lighters, camp kitchen things
                              (cooler, vacuum flask, picnic table, tongs, foil, cookware, cast iron, Dutch oven,
                              griddle, canteen), campfire treats, grilled and smoked foods, and water and food
                              storage. No label is asked twice (packs/test_outdoor_cooking.py checks).

Not repeated here: device_packs (Gas grills, Barbecues), chemical_packs (Propane cylinders, Charcoal briquettes, Gas
cylinders), things_packs (Rocket stoves, Kerosene and Charcoal stoves), home_packs and home_safety_packs (Meat
thermometers, Boiling water), us_modern_packs (Barbecue in the United States), and the Open Images labels other packs
ask (Barbecue, Tent, Sleeping bag, Lantern, Match, Camping, Backpacking, Thermometer, Skewer, Kebab and others).
Heating stoves, firewood, lanterns and the Commons Coleman Company category (its lanterns) belong to the heating and lighting
packs. What was looked at and left out is in the kit's
outdoor_cooking_sources.py (OUTDOOR_COOKING_NOT_INCLUDED).

    python packs/outdoor_cooking_packs.py commons_grills_smokers --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

CO_NOTE = ("Carbon monoxide: use it only outdoors, never inside a home, garage, tent or camper, even with a door "
           "open; never use grills, camp stoves, charcoal or generators indoors. If a CO alarm sounds or anyone feels "
           "dizzy, sick or sleepy, get out to fresh air and call 911.")
FIRE_NOTE = ("Fire: keep it well away from tents, buildings and overhanging branches, never leave it alone, and keep "
             "water or a fire extinguisher close.")
CAMPFIRE_NOTE = ("Fire: check local fire restrictions first; keep the fire small, in a fire ring, and never leave it; "
                 "to put it out, drown it with water, stir, and feel the ashes until they are cold (US Forest "
                 "Service).")
PROPANE_NOTE = ("Propane: check the connections for leaks with soapy water (growing bubbles mean a leak), never with a "
                "flame; keep cylinders upright, outdoors and away from heat, and close the valve when you finish.")
HOT_NOTE = "Hot surfaces: it stays hot long after cooking; use long tools and heat-proof gloves."
TEMP_NOTE = ("Food safety (USDA): check with a food thermometer: beef, pork, lamb and veal steaks, chops and roasts "
             "145 F (63 C) with a 3-minute rest, ground meat 160 F (71 C), poultry 165 F (74 C), fish 145 F (63 C); "
             "keep raw meat away from cooked food.")
WATER_NOTE = ("Water safety (CDC): if you are not sure water is safe, bring it to a rolling boil for 1 minute (3 "
              "minutes above 6,500 feet), or treat it as the product's own directions say.")
OUTAGE_NOTE = ("Power cuts (USDA): a closed fridge keeps food cold for about 4 hours and a full freezer about 48 "
               "hours; throw out perishable food above 40 F (4 C) for 2 hours or more: when in doubt, throw it out.")

STOVE_NOTES = f"{CO_NOTE} {FIRE_NOTE}"
GRILL_NOTES = f"{CO_NOTE} {HOT_NOTE} {TEMP_NOTE}"
ASK_WHAT = "What is this?"
ASK_FOOD = "What food is shown here?"


def thing(category, words, notes="", deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


def food(category, words, deeper=False):
    """A Commons spec for barbecue food: "It shows <words>." and the USDA temperatures."""
    return (category, deeper, [(ASK_FOOD, f"It shows {words}. {TEMP_NOTE}")])


# ----------------------------------------------------------------- Commons: camp cooking

# "Canteens" also holds staff restaurants and "Coolers" air coolers: only files whose own words say what we want.
BOTTLE_WORDS = re.compile(r"\b(canteens?|water bottles?|flasks?|bottles?|military|army|soldiers?|M1910|"
                          r"feldflasche)\b", re.I)
COOLER_WORDS = re.compile(r"\b(coolers?|cool ?box(es)?|ice ?chests?|ice ?box(es)?|igloo|yeti|coleman|camping|picnic)\b",
                          re.I)
CAMP_COOKING = [
    thing("Primus stoves", "a Primus stove, a small camp stove that burns pressurised liquid fuel", STOVE_NOTES),
    thing("Optimus AB", "an Optimus camp stove (a Swedish maker of liquid-fuel stoves)", STOVE_NOTES),
    thing("Svea 123", "a Svea 123, a small brass backpacking stove that burns white gas", STOVE_NOTES),
    thing("Trangia", "a Trangia, a camp cook set with an alcohol (spirit) burner and windshield", STOVE_NOTES),
    thing("Esbit portable stoves", "an Esbit stove, a folding stove for solid fuel tablets", STOVE_NOTES),
    thing("Cassette gas stoves", "a cassette gas stove, a tabletop stove that runs on a butane cartridge",
          STOVE_NOTES),
    thing("Campingaz", "Campingaz camping gear (gas cartridges and stoves)", f"{STOVE_NOTES} {PROPANE_NOTE}"),
    thing("Storm kettles", "a storm kettle (Kelly kettle), a kettle with a chimney that boils water over a small "
                           "fire inside it", STOVE_NOTES),
    thing("Mess kits", "a mess kit: nesting pots, a pan and a plate for eating in camp or in the field"),
    thing("Military mess kits", "a military mess kit", deeper=True),
    thing("Billycans", "a billycan, a light metal pot for boiling water or cooking over a fire", HOT_NOTE),
    thing("Canteens", "a canteen, a water bottle for hiking, camping or the field", WATER_NOTE, True, BOTTLE_WORDS),
    thing("Coolers", "a cooler (cool box) for keeping food cold: keep it at 40 F (4 C) or colder with plenty of "
                     "ice, raw meat sealed at the bottom", "", True, COOLER_WORDS),
    thing("Dutch ovens", "a Dutch oven, a heavy lidded pot; camp Dutch ovens have legs and a rimmed lid for coals on "
                         "top", HOT_NOTE, True),
    thing("Cast iron cookware", "cast-iron cookware: keep it seasoned with a thin coat of oil, and dry it straight "
                                "after washing so it does not rust", HOT_NOTE, True),
    thing("Campfire cooking", "cooking over a campfire", f"{CAMPFIRE_NOTE} {TEMP_NOTE}"),
    thing("Camp Cooking Cranes", "a camp cooking crane, a stand for hanging a pot over a fire", CAMPFIRE_NOTE),
    thing("Campfires", "a campfire", CAMPFIRE_NOTE),
    thing("LifeStraw", "a LifeStraw, a personal water filter you drink through", WATER_NOTE),
    thing("Water purification tablets", "water purification tablets: follow the product's own directions and "
                                        "waiting time", WATER_NOTE),
]

# ----------------------------------------------------------------- Commons: emergency cooking

EMERGENCY_COOKING = [
    thing("Solar cookers", "a solar cooker, which cooks with sunlight reflected onto a dark pot; it needs full sun",
          f"{HOT_NOTE} {TEMP_NOTE}", True),
    thing("Hayboxes", "a haybox (fireless or retained-heat cooker): food brought to the boil keeps cooking in the "
                      "insulated box", "Keep the food above 140 F (60 C) while it cooks; bring it back to the boil "
                                       "if it cools below that."),
    thing("Chafing dishes", "a chafing dish, which keeps food warm over a small burner or canned heat",
          f"{FIRE_NOTE} Keep hot food at 140 F (60 C) or above.", True),
    thing("Sterno", "Sterno canned heat (chafing fuel), a can of jellied alcohol for warming food",
          f"{FIRE_NOTE} Use it only where there is fresh air, never as a heater, and put the lid on to put it out."),
    thing("Beverage can stoves", "a beverage-can stove, a small alcohol stove made from drink cans", STOVE_NOTES),
    thing("Field kitchens", "a field kitchen, a kitchen set up outdoors or in a trailer to feed many people",
          deeper=True),
    thing("Water barrels", "a water barrel for storing water: store at least 1 gallon per person per day for several "
                           "days, in clean food-grade containers (Ready.gov)", WATER_NOTE, True),
    thing("Canned food", "canned food: keep a supply of foods that need no cooking; throw away cans that are "
                         "bulging, leaking or badly dented", "", True),
    thing("Lightweight Water Purifier", "a lightweight water purifier, a portable unit that makes water safe to "
                                        "drink", WATER_NOTE),
]

# ----------------------------------------------------------------- Commons: grills and smokers

# Commons "Kamado" is mostly the traditional Japanese kitchen stove, and "Charcoal grills" holds charcoal itself and
# Japanese braziers: only files whose own words name a grill, barbecue or smoker.
GRILL_WORDS = re.compile(r"\b(grill(s|ing)?|bbq|barbecues?|braai|kettle|weber|green egg|kamado joe|smokers?)\b", re.I)
GRILLS_SMOKERS = [
    thing("Grills", "a grill for cooking food over heat", GRILL_NOTES, pattern=GRILL_WORDS),
    thing("Charcoal grills", "a charcoal grill; for a two-zone fire, pile the coals on one side and cook slowly on "
                             "the other; open the vents for more heat and close them to cool it", GRILL_NOTES, True,
          GRILL_WORDS),
    thing("Weber grills", "a Weber grill (Weber makes kettle charcoal grills and gas grills)", GRILL_NOTES),
    thing("Kamado", "a kamado grill, a thick ceramic egg-shaped grill and smoker", GRILL_NOTES, True, GRILL_WORDS),
    thing("Big Green Egg", "a Big Green Egg, a ceramic kamado grill and smoker", GRILL_NOTES),
    thing("Wood pellets barbecues", "a pellet grill: an auger feeds wood pellets to a fire pot lit by a hot rod, and "
                                    "a controller keeps the temperature", GRILL_NOTES),
    thing("Smokehouses", "a smokehouse, where food is cured and flavoured with smoke",
          f"{FIRE_NOTE} {HOT_NOTE} {TEMP_NOTE} Cold smoking does not cook food.", True),
    thing("Griddles", "a griddle, a flat cooking plate (a flat-top grill)",
          f"If it runs on propane or charcoal: {CO_NOTE} {HOT_NOTE} {TEMP_NOTE}", True),
    thing("Chimney starters", "a chimney starter, a metal tube for lighting charcoal with newspaper instead of "
                              "lighter fluid; the coals are ready when they are covered in grey ash", GRILL_NOTES),
    thing("Disposable barbecues", "a disposable barbecue, a small foil tray of charcoal",
          f"{GRILL_NOTES} Never put it on grass, wood or a table that can burn; let it cool fully before you throw "
          f"it away."),
    thing("Outdoor kitchens", "an outdoor kitchen with a grill", GRILL_NOTES, True),
    thing("Liquefied petroleum gas cylinders", "a propane (LPG) gas cylinder: cylinders have an overfill prevention "
                                               "device (OPD) valve; exchange or refill them at a dealer", PROPANE_NOTE,
          True),
]

# ----------------------------------------------------------------- Commons: barbecue food

BARBECUE_FOOD = [
    ("Barbecue (cooking technique)", False, [(ASK_WHAT, "This is barbecue: food cooked slowly with smoke and indirect "
                                                        f"heat. {GRILL_NOTES}")]),
    food("Grilled meats", "grilled meat", True),
    food("Smoked meat", "smoked meat"),
    food("Smoked pork", "smoked pork"),
    food("Smoked sausages", "smoked sausages", True),
    food("Pulled pork", "pulled pork, pork shoulder smoked until it is tender and pulled apart", True),
    food("Ribs (food)", "ribs", True),
    food("Burnt ends", "burnt ends, the crusty smoked pieces from the point of a beef brisket"),
    food("Barbecue in Texas", "Texas barbecue", True),
    food("Asado", "asado, the Argentine and South American way of grilling meat over wood or charcoal", True),
    food("Parrillas", "a parrilla, an Argentine grill, and the meat cooked on it", True),
]


def build_commons_camp_cooking(limit):
    """The commons_camp_cooking pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CAMP_COOKING, limit, "campcook")


def build_commons_emergency_cooking(limit):
    """The commons_emergency_cooking pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(EMERGENCY_COOKING, limit, "emergcook")


def build_commons_grills_smokers(limit):
    """The commons_grills_smokers pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(GRILLS_SMOKERS, limit, "grillsmoke")


def build_commons_barbecue_food(limit):
    """The commons_barbecue_food pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BARBECUE_FOOD, limit, "bbqfood")


# ----------------------------------------------------------------- Open Images

OUTDOOR_OI = [
    group("Is someone grilling in this picture?", {"Grilling": "grilling, cooking food on a grill"}, GRILL_NOTES),
    group("What fire is in this picture?", {"Campfire": "a campfire", "Bonfire": "a bonfire"}, CAMPFIRE_NOTE),
    group("What fire-lighting things are in this picture?",
          {"Charcoal": "charcoal", "Lighter (Device)": "a lighter"}, f"{CO_NOTE} {FIRE_NOTE}"),
    group("What camp kitchen things are in this picture?",
          {"Cooler": "a cooler", "Vacuum flask": "a vacuum flask (thermos)", "Picnic table": "a picnic table",
           "Tongs": "tongs", "Aluminium foil": "aluminium foil", "Cookware and bakeware": "cookware",
           "Cast iron": "cast iron", "Dutch oven": "a Dutch oven", "Griddle": "a griddle", "Canteen": "a canteen"}),
    group("What campfire treats are in this picture?", {"Marshmallow": "marshmallows", "S'more": "s'mores"},
          CAMPFIRE_NOTE),
    group("What grilled or smoked foods are in this picture?",
          {"Barbecue chicken": "barbecue chicken", "Brisket": "brisket", "Smoked salmon": "smoked salmon",
           "Yakitori": "yakitori (grilled chicken skewers)"}, TEMP_NOTE),
    group("What water or food storage is in this picture?",
          {"Water tank": "a water tank", "Drinking water": "drinking water", "Water filter": "a water filter",
           "Canning": "home canning", "Mason jar": "a mason jar", "Food storage containers": "food storage "
                                                                                           "containers"}),
]


def with_yes_notes(entries, groups=None):
    """entries with each group's safety note added to the "Yes, there is ..." answers too (gaps_oi_packs adds it
    only to the group's own question), so every answer that names a grill, a fire, fuel or food says its note."""
    notes = {f"Yes, there {verb} {words} in this picture.": grp["note"] for grp in groups or OUTDOOR_OI if grp["note"]
             for words in grp["things"].values() for verb in ("is", "are")}
    out = []
    for name, data, row in entries:
        note = notes.get(row.get("answer"))
        out.append((name, data, dict(row, answer=f"{row['answer']} {note}") if note else row))
    return out


def build_open_images_outdoor_cooking(limit):
    """open_images_outdoor_cooking (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_outdoor_cooking", OUTDOOR_OI, limit, 9301))


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
OUTDOOR_COOKING_PACKS = {
    "commons_camp_cooking": (build_commons_camp_cooking, COMMONS_LICENCE.format(
        what="camp stove, mess kit, canteen, cooler, Dutch oven, cast iron, campfire and water filter")),
    "commons_emergency_cooking": (build_commons_emergency_cooking, COMMONS_LICENCE.format(
        what="solar cooker, haybox, chafing dish, canned heat, can stove, field kitchen and water storage")),
    "commons_grills_smokers": (build_commons_grills_smokers, COMMONS_LICENCE.format(
        what="grill, kamado, pellet grill, smokehouse, griddle, chimney starter and propane cylinder")),
    "commons_barbecue_food": (build_commons_barbecue_food, COMMONS_LICENCE.format(
        what="barbecue, grilled and smoked meat")),
    "open_images_outdoor_cooking": (build_open_images_outdoor_cooking, OI_LICENCE),
}
OUTDOOR_COOKING_LIMITS = {
    "commons_camp_cooking": 900,           # 20 categories, few files in some
    "commons_emergency_cooking": 500,      # 9 categories
    "commons_grills_smokers": 900,         # 12 categories
    "commons_barbecue_food": 900,          # 11 categories
    "open_images_outdoor_cooking": 1200,   # 31 labels; Grilling has most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
OUTDOOR_COOKING_COMMONS_KEYS = ("commons_camp_cooking", "commons_emergency_cooking", "commons_grills_smokers",
                                "commons_barbecue_food")
# The Commons category specs of the packs (for the self-test).
OUTDOOR_COOKING_SPECS = CAMP_COOKING + EMERGENCY_COOKING + GRILLS_SMOKERS + BARBECUE_FOOD


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an outdoor cooking pack builder.")
    parser.add_argument("key", choices=sorted(OUTDOOR_COOKING_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = OUTDOOR_COOKING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
