"""EMERGENCY COOKING, CAMP COOKING, AND GRILLS AND SMOKERS for the Picture Model Training Kit (the owner's request of
2026-11-22). This file lists:
  - the ready-made packs built in packs/outdoor_cooking_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_camp_cooking, commons_emergency_cooking, commons_grills_smokers, commons_barbecue_food and
    open_images_outdoor_cooking;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (OUTDOOR_COOKING_NOT_INCLUDED).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked), and every
answer about a stove, grill, smoker, fire, fuel, food or water ends with the safety notes that fit it: carbon
monoxide (never use grills, camp stoves, charcoal or generators indoors; get out and call 911 if a CO alarm sounds or
anyone feels ill), fire, propane leaks (soapy water, never a flame), hot surfaces, USDA safe minimum internal
temperatures and safe water. The notes are the same words as the packs' (packs/test_outdoor_cooking.py checks).

Picture-making (OUTDOOR_COOKING_PICTURE_MAKING_OK): only the Commons camp gear and grills (things); sources.py puts
every other key in NOT_FOR_PICTURE_MAKING (field kitchens, barbecues and the Open Images photos show people).
Topics: the gear is in the machines topic (household equipment), the barbecue food in the food topic.

    python -c "import sources, outdoor_cooking_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/outdoor_cooking_packs.py.
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
STOVE_NOTES = f"{CO_NOTE} {FIRE_NOTE}"
GRILL_NOTES = f"{CO_NOTE} {HOT_NOTE} {TEMP_NOTE}"

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


# The main categories of packs/outdoor_cooking_packs.py whose files need no word filter (the share-alike entry has
# none): camp stoves and cookware, emergency cookers, smokehouses, chimney starters and propane cylinders. (Commons
# "Kamado" and "Charcoal grills" hold Japanese kitchen stoves and charcoal too, so they are left out here.)
OUTDOOR_COOKING_SA = [
    gear("Primus stoves", "a Primus stove, a small camp stove that burns pressurised liquid fuel", STOVE_NOTES),
    gear("Trangia", "a Trangia, a camp cook set with an alcohol (spirit) burner and windshield", STOVE_NOTES),
    gear("Cassette gas stoves", "a cassette gas stove, a tabletop stove that runs on a butane cartridge",
         STOVE_NOTES),
    gear("Mess kits", "a mess kit: nesting pots, a pan and a plate for eating in camp or in the field"),
    gear("Dutch ovens", "a Dutch oven, a heavy lidded pot; camp Dutch ovens have legs and a rimmed lid for coals on "
                        "top", HOT_NOTE, True),
    gear("Cast iron cookware", "cast-iron cookware: keep it seasoned with a thin coat of oil, and dry it straight "
                               "after washing so it does not rust", HOT_NOTE, True),
    gear("Campfire cooking", "cooking over a campfire", f"{CAMPFIRE_NOTE} {TEMP_NOTE}"),
    gear("Solar cookers", "a solar cooker, which cooks with sunlight reflected onto a dark pot; it needs full sun",
         f"{HOT_NOTE} {TEMP_NOTE}", True),
    gear("Hayboxes", "a haybox (fireless or retained-heat cooker): food brought to the boil keeps cooking in the "
                     "insulated box"),
    gear("Smokehouses", "a smokehouse, where food is cured and flavoured with smoke",
         f"{FIRE_NOTE} {HOT_NOTE} {TEMP_NOTE} Cold smoking does not cook food.", True),
    gear("Chimney starters", "a chimney starter, a metal tube for lighting charcoal with newspaper instead of "
                             "lighter fluid", GRILL_NOTES),
    gear("Liquefied petroleum gas cylinders", "a propane (LPG) gas cylinder", PROPANE_NOTE, True),
]


def prepare_outdoor_cooking_commons_sa(source, data_dir, work, cap):
    """Commons camp stove, cookware, solar cooker, grill, smoker and propane categories, files under CC BY-SA or
    GFDL."""
    items = commons_sa_items(OUTDOOR_COOKING_SA, cap, source.test, "outcook-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

OUTDOOR_COOKING_SOURCES = [
    Source("commons_camp_cooking", "Camp cooking: camp and backpacking stoves, gas cartridges, mess kits, canteens, "
                                   "coolers, Dutch ovens and cast iron, campfire cooking and portable water filters, "
                                   "with carbon monoxide and fire notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_emergency_cooking", "Emergency cooking: solar cookers, hayboxes, chafing dishes and canned heat, "
                                        "can stoves, field kitchens, water barrels and purifiers, canned food "
                                        "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 5, prepare_pack, "about 110 MB"),
    Source("commons_grills_smokers", "Grills and smokers: charcoal and kettle grills, kamados, pellet grills, "
                                     "smokehouses, griddles, chimney starters, disposable barbecues and propane "
                                     "cylinders, with safety and USDA temperature notes (Wikimedia Commons, "
                                     "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_barbecue_food", "Barbecue food: grilled and smoked meat, pulled pork, ribs, burnt ends, Texas "
                                    "barbecue and asado, with USDA safe temperatures (Wikimedia Commons, ready-made "
                                    "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("open_images_outdoor_cooking", "Grilling, campfires, charcoal, coolers, vacuum flasks, Dutch ovens, "
                                          "griddles, campfire treats, grilled foods and water storage (Open Images, "
                                          "ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1200, 15, prepare_pack, "about 250 MB"),
    Source("outdoor_cooking_commons_sa", "Wikimedia Commons: camp stoves, mess kits, Dutch ovens and cast iron, "
                                         "campfire cooking, solar cookers, hayboxes, "
                                         "smokehouses, chimney starters and propane cylinders, files under CC BY-SA or "
                                         "GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 600, 10, prepare_outdoor_cooking_commons_sa,
           "about 130 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons camp gear and grills (things); never the
# emergency (field kitchens), barbecue food or Open Images collections, which show people.
OUTDOOR_COOKING_PICTURE_MAKING_OK = {"commons_camp_cooking", "commons_grills_smokers", "outdoor_cooking_commons_sa"}

OUTDOOR_COOKING_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Gas grills and Barbecues (device_packs), Propane cylinders, "
        "Charcoal briquettes and Gas cylinders (chemical_packs), Rocket stoves, Kerosene stoves and Charcoal stoves "
        "(things_packs), Meat thermometers and Boiling water (home_packs, home_safety_packs), Barbecue in the United "
        "States (us_modern_packs): not asked twice.",
    "Commons categories that do not exist under the names tried (November 2026)": "Camping stoves, Coleman stoves, "
        "Alcohol stoves, Butane stoves, Gas cartridges, Jetboil, MSR stoves, Hobo stoves, Bear canisters, "
        "Bear-resistant food containers, Thermal cookers, Wonderbag, Meals Ready-to-Eat, Pellet grills, Traeger, "
        "Smokers, Offset smokers, Electric smokers, Flat-top grills, Rotisseries, Propane tanks, Gas regulators, "
        "Brisket, Kansas City and Memphis barbecue; Bear boxes, Solar ovens, Military rations and Barbecue exist but "
        "hold no files. The packs use the categories that hold files.",
    "Hibachi and Braziers on Commons": "Japanese hibachi and braziers are mostly room heaters; heating belongs to "
                                       "another collection, so they are left out.",
    "Open Images labels with no or almost no checked photos": "Barbecue grill, Outdoor grill, Portable stove, "
        "Propane, Rotisserie, Cooking thermometer, Solar dish, Camp, Camp furniture, Pulled pork, Ribs and others "
        "have no human-checked photos in Open Images V7 (counted 2026-11-22), so they are not asked.",
    "Open Images labels asked elsewhere": "Barbecue, Tent, Sleeping bag, Lantern, Camping, Backpacking, Hiking "
        "equipment, Thermometer, Infrared thermometer, Skewer, Kebab, Sausage, Hot dog, Hamburger, Picnic, Picnic "
        "basket, Fireplace, Water bottle, Frying pan, Stock pot, Kettle, Coffee percolator, Stove, Gas stove, Steak, "
        "Meat, Bottled water: asked by other packs, never twice. Fire, Flame and Smoke are too general (house fires) "
        "and are left out.",
    "USDA FSIS, USDA ARS and USFS photo galleries": "fsis.usda.gov refuses programs (403, robots.txt included); the "
        "ARS gallery has no listing a program can read by subject; the Forest Service's and Park Service's own "
        "public-domain photos that people copied to Commons are reached through the Commons categories.",
    "Coleman, Weber, Traeger, Lodge, Camp Chef and other makers' product photos": "the makers' copyright; not "
        "used. Their manuals are listed as links in the manual collection outdoor_cooking.",
    "Smokey Bear artwork": "the character is protected by federal law (18 U.S.C. 711) and the campaign art is the "
                           "Ad Council's and the Forest Service's licensed material; not used.",
    "Roboflow Universe grill and food-doneness sets": "Roboflow Universe's robots.txt disallows the dataset "
                                                      "download pages (see gaps_sources.py).",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the outdoor cooking share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in OUTDOOR_COOKING_SOURCES if s.key == "outdoor_cooking_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="outcook-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
