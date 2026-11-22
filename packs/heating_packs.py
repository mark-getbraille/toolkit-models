"""Picture packs for EMERGENCY AND SECONDARY HEATING: fireplaces, wood, coal and pellet stoves, tiled stoves (masonry
heaters), gas, kerosene, oil and electric space heaters, patio heaters (outdoor only), chimney and stove parts, ash,
fuel, firewood and the tools for splitting it (the coordinator's addition of 2026-11-22 to the owner's home repair and
upkeep request). Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and
returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes once with its JPEG and then
as (None, None, row) rows naming the same picture. The limit counts pictures.

Already in other packs, and so NOT repeated (packs/test_heating.py checks that no Commons category here is named by
another pack file and no Open Images label is asked twice): wood-burning and pellet stoves, space heaters, electric
and fan heaters, radiators, furnaces and boilers (device_packs, home_safety_packs and others), carbon monoxide and
smoke alarms, fire extinguishers and fire blankets (home_safety_packs and chemical_packs), propane cylinders,
jerrycans, kerosene and charcoal in their containers (chemical_packs), log splitters (hardware_packs), axes (things
packs), heaters too close to things (household_hazard_packs), the emerald ash borer (na_animal_packs and home_packs),
chimneys and chimney sweeps (home_upkeep_packs), and Open Images' Fireplace, Stove, Heater, Space heater, Chimney,
Boiler, Smoke detector and Fire extinguisher labels.

Answers say only what the source says (a Commons category's name, with one short line written here on what that
kind of heater or tool is, or an Open Images label people confirmed); no heat output, clearance in inches for a
particular model, or fuel grade is ever made up. EVERY answer about a heater, stove, fireplace, fuel, chimney or
ash ends with HEAT_SAFETY (carbon monoxide can kill: a CO alarm, never outdoor heaters, grills or generators indoors,
get out and call 911 if the alarm sounds or anyone feels ill; keep things 3 feet away; gas work for a qualified
professional), with the fuel's own note before it where there is one (KEROSENE_NOTE: 1-K only, never gasoline;
refuel outdoors when cool; ASH_NOTE: a metal can with a lid, outside; CHIMNEY_NOTE: a yearly inspection and
sweeping, and what to do in a chimney fire; ELECTRIC_NOTE: straight into a wall socket, tip-over switch; OUTDOOR_ONLY:
patio heaters and grills). Answers about firewood and its tools end with FIREWOOD_NOTE (season it, keep it 3 feet
from the stove, and "don't move firewood": the emerald ash borer, USDA APHIS) or SPLITTING_NOTE.

The packs (all open: CC0, public domain or CC BY, checked file by file; Open Images labels CC BY 4.0):
  commons_home_heating     Wikimedia Commons: fireplaces, electric fireplaces, heating stoves, Franklin and potbelly
                           stoves, coal stoves, tiled stoves (masonry heaters), gas heaters, kerosene, oil, convection
                           and catalytic heaters, patio heaters (outdoor only), fireplace tools, chimney and stove
                           dampers, stovepipes, fire bricks, chimney fires, creosote and soot in chimneys, ash
                           buckets, wood pellets, anthracite and coal scuttles.
  commons_firewood         Commons: firewood, woodpiles, splitting mauls, splitting wedges, firewood processors and
                           wood moisture meters.
  open_images_home_heating Open Images V7: wood-burning stoves, hearths, fire screens and bellows; coal; splitting
                           mauls and sawhorses; barbecue grills (outdoor only).

The share-alike Commons files and what was left out are in training-kit/kit/home_crafts_sources.py.

    python packs/heating_packs.py commons_home_heating --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

# ----------------------------------------------------------------- the safety notes (fixed sentences)

HEAT_SAFETY = ("Heating safety: keep anything that can burn at least 3 feet (1 metre) away. Stoves, fireplaces and "
               "fuel-burning heaters make carbon monoxide, which can kill: have a working carbon monoxide alarm, "
               "never use outdoor heaters, grills or generators indoors, and if the alarm sounds or anyone feels ill "
               "(headache, dizziness, nausea), get everyone out and call 911. Gas lines, gas appliances and stove "
               "installation are work for a qualified professional.")
KEROSENE_NOTE = ("Use only clear 1-K grade kerosene, never gasoline or other fuels; refuel outdoors, only when the "
                 "heater is off and cool, and store kerosene in a blue can marked for kerosene.")
ASH_NOTE = ("Put ashes in a metal can with a tight lid and keep it outside, away from the house: ashes can stay hot "
            "for days.")
CHIMNEY_NOTE = ("Have the chimney and flue inspected and swept every year by a certified chimney sweep: creosote "
                "builds up and can catch fire. In a chimney fire (a roaring sound, flames or sparks from the top), "
                "get everyone out and call 911.")
ELECTRIC_NOTE = ("Plug an electric heater straight into a wall socket, never an extension cord or power strip; choose "
                 "one with a tip-over switch and turn it off when you leave the room or go to sleep.")
GAS_HEATER_NOTE = ("A gas heater needs fresh air: vented heaters must vent outdoors, and vent-free heaters need the "
                   "ventilation their maker requires and an oxygen depletion sensor.")
OUTDOOR_ONLY = ("This is for outdoors only: never use it inside a home, garage, tent or porch.")
FIREWOOD_NOTE = ("Burn only dry, seasoned wood and keep the woodpile at least 3 feet from the stove. Don't move "
                 "firewood: buy or gather it near where you burn it, so pests such as the emerald ash borer are not "
                 "spread (USDA APHIS).")
SPLITTING_NOTE = ("Splitting wood: wear eye protection and sturdy boots, keep people well back, and split on a solid, "
                  "level block.")

ASK_WHAT = "What is this?"
ASK_HEAT = "What kind of heating is this?"
# Categories whose name is used for other things too (dampers in air ducts and pianos, creosote as a wood preservative,
# soot from engines, moisture meters for walls): only files whose own words speak of a chimney, stove or fireplace
# (or, for moisture meters, of wood).
HEARTH_WORDS = re.compile(r"\b(chimneys?|flues?|stoves?|stove ?pipes?|fireplaces?|hearths?|wood ?burn\w*|firebox|"
                          r"kachel\w*|po[eê]les?|ofen|kamin\w*)\b", re.I)
WOOD_WORDS = re.compile(r"\b(wood|firewood|timber|lumber|logs?|holz)\b", re.I)


def heater(category, words, note="", deeper=False, must=None, question=ASK_HEAT):
    """A Commons spec for home_packs.build_commons_topic: "<question>" -> "This is <words>." then the note and
    HEAT_SAFETY; must: only files whose title or words match this pattern."""
    answer = f"This is {words}." + (f" {note}" if note else "") + f" {HEAT_SAFETY}"
    spec = (category, deeper, [(question, answer)])
    return spec + (must,) if must is not None else spec


def wood(category, words, note=FIREWOOD_NOTE, deeper=False, must=None):
    """A Commons spec for firewood or its tools: "What is this?" -> "This is <words>." and the note."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}. {note}")])
    return spec + (must,) if must is not None else spec


# ----------------------------------------------------------------- Commons: heaters, stoves, fireplaces and their parts

HOME_HEATING = [
    heater("Fireplaces", "a fireplace", CHIMNEY_NOTE),
    heater("Electric fireplaces", "an electric fireplace, which looks like a fire but heats with electricity",
           ELECTRIC_NOTE, deeper=True),
    heater("Heating stoves", "a heating stove, which burns wood, coal or another fuel to heat a room", CHIMNEY_NOTE,
           deeper=True),
    heater("Franklin stoves", "a Franklin stove, an open-fronted cast-iron stove", CHIMNEY_NOTE),
    heater("Potbelly stoves", "a potbelly stove, a round cast-iron wood or coal stove", CHIMNEY_NOTE, deeper=True),
    heater("Coal stoves", "a coal stove", CHIMNEY_NOTE, deeper=True),
    heater("Tiled stoves", "a tiled stove (a masonry heater or Kachelofen): a big stove of brick and tile that stores "
                           "the heat of a short, hot fire and gives it off for hours", CHIMNEY_NOTE, deeper=True),
    heater("Gas heaters", "a gas heater", GAS_HEATER_NOTE, deeper=True),
    heater("Kerosene heaters", "a kerosene heater", KEROSENE_NOTE),
    heater("Oil heaters", "an oil heater", deeper=True),
    heater("Convection heaters", "a convection heater, which warms the air of a room", deeper=True),
    heater("Catalytic heaters", "a catalytic heater, which burns gas without a flame", GAS_HEATER_NOTE),
    heater("Patio heaters", "a patio heater, a tall gas heater for outdoor seating", OUTDOOR_ONLY, deeper=True),
    heater("Fireplace tools", "fireplace tools: a poker, tongs, a shovel and a brush for tending a fire", ASH_NOTE,
           deeper=True, question=ASK_WHAT),
    heater("Dampers", "a chimney or stove damper, a plate that opens and closes the flue", CHIMNEY_NOTE, deeper=True,
           must=HEARTH_WORDS, question=ASK_WHAT),
    heater("Stovepipes", "a stovepipe, the metal pipe that carries smoke from a stove to the chimney", CHIMNEY_NOTE,
           deeper=True, question=ASK_WHAT),
    heater("Fire bricks", "fire bricks, which line a firebox and stand great heat", question=ASK_WHAT),
    heater("Chimney fires", "a chimney fire", CHIMNEY_NOTE, question="What is happening here?"),
    heater("Creosote", "creosote, the tar that builds up inside chimneys and stovepipes from wood smoke",
           CHIMNEY_NOTE, deeper=True, must=HEARTH_WORDS, question=ASK_WHAT),
    heater("Soot", "soot in a chimney, flue or stove", CHIMNEY_NOTE, deeper=True, must=HEARTH_WORDS,
           question=ASK_WHAT),
    heater("Ash buckets", "an ash bucket, a metal bucket for carrying ashes from a stove or fireplace", ASH_NOTE,
           question=ASK_WHAT),
    heater("Wood pellets", "wood pellets, the fuel of a pellet stove", "Store pellet bags dry, off the floor.",
           deeper=True, question=ASK_WHAT),
    heater("Anthracite", "anthracite, a hard coal that burns hot and clean in a coal stove", deeper=True,
           question=ASK_WHAT),
    heater("Coal scuttles", "a coal scuttle, a bucket for carrying coal to a stove or fire", deeper=True,
           question=ASK_WHAT),
]

# ----------------------------------------------------------------- Commons: firewood and splitting tools

FIREWOOD = [
    wood("Firewood", "firewood"),
    wood("Woodpiles", "a woodpile: firewood stacked to dry", deeper=True),
    wood("Splitting mauls", "a splitting maul, a heavy axe with a wedge-shaped head for splitting logs",
         SPLITTING_NOTE),
    wood("Splitting wedges", "a splitting wedge, driven into a log with a sledgehammer to split it", SPLITTING_NOTE),
    wood("Firewood processors", "a firewood processor, a machine that cuts and splits logs", SPLITTING_NOTE),
    wood("Moisture meters", "a moisture meter, which shows how dry wood is (firewood is ready to burn below about 20 "
                            "percent)", must=WOOD_WORDS, deeper=True),
]


def build_commons_home_heating(limit):
    """The commons_home_heating pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(HOME_HEATING, limit, "heating")


def build_commons_firewood(limit):
    """The commons_firewood pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FIREWOOD, limit, "firewood")


# ----------------------------------------------------------------- Open Images

HEATING_OI = [
    group("What heating things are in this picture?",
          {"Wood-burning stove": "a wood-burning stove", "Hearth": "a hearth", "Fire screen": "a fire screen",
           "Bellows": "bellows"}, HEAT_SAFETY),
    group("What fuel is in this picture?", {"Coal": "coal"}, HEAT_SAFETY),
    group("What firewood tools are in this picture?", {"Splitting maul": "a splitting maul", "Sawhorse": "a sawhorse"},
          SPLITTING_NOTE),
    group("Is there a grill in this picture?", {"Barbecue grill": "a barbecue grill"},
          "Grills are for outdoors only: never use a grill inside a home, garage, tent or porch, because carbon "
          "monoxide can kill."),
]


def build_open_images_home_heating(limit):
    """open_images_home_heating (see the module docstring)."""
    return build_oi_gap("open_images_home_heating", HEATING_OI, limit, 9303)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
HEATING_PACKS = {
    "commons_home_heating": (build_commons_home_heating, COMMONS_LICENCE.format(
        what="fireplace, stove, space heater, chimney part, ash and fuel")),
    "commons_firewood": (build_commons_firewood, COMMONS_LICENCE.format(what="firewood and splitting tool")),
    "open_images_home_heating": (build_open_images_home_heating, OI_LICENCE),
}
HEATING_LIMITS = {
    "commons_home_heating": 1000,       # 25 categories, few files in some
    "commons_firewood": 400,            # 6 categories
    "open_images_home_heating": 800,    # 8 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
HEATING_COMMONS_KEYS = ("commons_home_heating", "commons_firewood")
# Every Commons spec of these packs (for the self-test).
HEATING_SPECS = HOME_HEATING + FIREWOOD


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a home heating pack builder.")
    parser.add_argument("key", choices=sorted(HEATING_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = HEATING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
