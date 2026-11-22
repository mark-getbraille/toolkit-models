"""Picture packs for EMERGENCY AND BACKUP LIGHTING: flashlights, emergency lights, glow sticks and batteries; fuel
lanterns and lamps (modern pressure lanterns such as Coleman, Petromax and Tilley, kerosene and hurricane lamps, gas
lamps, mantles and wicks); candles, holders and snuffers (the coordinator's addition of 2026-11-22, beside emergency
heating, to the owner's home repair and upkeep request; the owner wants modern battery, electric and fuel lights in
depth, and nothing from before 1900, so antique and museum lamps are left out). Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes
once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

Already in other packs, and so NOT repeated (packs/test_home_crafts.py checks the Commons categories and the Open
Images labels): solar lamps and solar chargers, AA, AAA, C, D, 9-volt and button batteries and battery chargers
(home_packs commons_connectors and others), exit signs (events_safety_packs), kerosene and lamp oil in their
containers (chemical_packs), tactical lights (drug_firearm_packs), car headlamps (mechanical_packs), diyas
(culture_packs), and Open Images' Flashlight, Lantern, Candle, Lamp, Battery, Battery charger, Chandelier and Light
bulb labels.

Answers say only what the source says (a Commons category's name, with one short line written here on what that kind
of light is, or an Open Images label people confirmed); no run time, brightness or fuel capacity is ever made up.
EVERY answer about a fuel lantern or lamp ends with FUEL_LIGHT_NOTE (fire and carbon monoxide: outdoors or well
ventilated as the maker says, never refuel while hot or lit, only the fuel the lamp is made for, away from children,
pets and curtains, battery lights are safer indoors); every candle answer with CANDLE_NOTE (never unattended, a
sturdy holder, 1 foot from anything that can burn; battery lights during a power cut, as the CDC, FEMA and the Red
Cross advise); battery answers with BATTERY_NOTE (storage and leak clean-up).

The packs (all open: CC0, public domain or CC BY, checked file by file; Open Images labels CC BY 4.0):
  commons_emergency_lighting  Wikimedia Commons: flashlights and LED flashlights, emergency lighting, glow sticks,
                              portable power stations, battery banks and packs, rechargeable, lithium and alkaline
                              batteries; kerosene and hurricane lamps, lanterns (fuel, camping, solar, battery and
                              candle lanterns only), Petromax and Tilley
                              pressure lamps, Coleman lanterns, gas mantles and wicks; candles, tealights, pillar
                              candles, candle holders, candle lanterns and candle snuffers.
  open_images_emergency_lighting  Open Images V7: headlamps, oil lamps, candle holders and matches.

The share-alike Commons files and what was left out are in training-kit/kit/home_crafts_sources.py.

    python packs/lighting_packs.py commons_emergency_lighting --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

# ----------------------------------------------------------------- the safety notes (fixed sentences)

FUEL_LIGHT_NOTE = ("Fuel lamp safety: fuel lanterns and lamps can start fires and make carbon monoxide, which can "
                   "kill. Use them outdoors or with good ventilation, as the maker says; never refuel one that is hot "
                   "or lit; use only the fuel the lamp is made for; keep it away from children, pets and curtains. "
                   "Battery lights are safer indoors during a power cut.")
CANDLE_NOTE = ("Candle safety: never leave a candle burning unattended or while you sleep; use a sturdy holder and keep "
               "it at least 1 foot (30 cm) from anything that can burn and away from children and pets. During a "
               "power cut, use battery lights instead of candles (CDC, FEMA and Red Cross advice).")
BATTERY_NOTE = ("Store batteries cool and dry, in their packaging, and take them out of lights stored for a long time. "
                "A leaking battery's crust can burn skin and eyes: wear gloves to clean it up and recycle the battery.")
MATCH_NOTE = "Keep matches and lighters where children cannot reach them."

ASK_WHAT = "What is this?"
ASK_LIGHT = "What kind of light is this?"
# Lanterns: only files whose own words make them a light for use (not paper festival or architectural lanterns).
# The owner wants modern lights, nothing from before 1900: files whose own words give an 18th- or 19th-century year
# or call the lamp antique, Victorian or a museum piece are left out of the fuel lamp categories (NOT_OLD), and so are
# street lamps (gas lamps and lanterns).
_OLD = r"1[78]\d\d|antique|antik\w*|museum|museo|victorian|ancient|roman|medieval"
_STREET = r"street|streets|road|avenue|lamppost|lamp post|gaslight district|strasse|straße|gaslaterne"
NOT_OLD = re.compile(rf"^(?!.*\b({_OLD})\b)", re.I | re.S)
NOT_OLD_OR_STREET = re.compile(rf"^(?!.*\b({_OLD}|{_STREET})\b)", re.I | re.S)
# Lanterns: only files whose own words make them a light for use (not paper festival or architectural lanterns), and
# not old. Coleman's category also holds its coolers and stoves: only its lanterns and lamps.
_LANTERN = (r"kerosene|paraffin|gas|camping|storm|hurricane|led|electric|battery|candle|coleman|petromax|tilley|dietz|"
            r"feuerhand|pressure|propane|butane|dual[- ]fuel|white gas|mantles?|solar|rechargeable")
LANTERN_WORDS = re.compile(rf"^(?!.*\b({_OLD})\b)(?=.*\b({_LANTERN})\b)", re.I | re.S)
LAMP_WORDS = re.compile(rf"^(?!.*\b({_OLD})\b)(?=.*\b(lanterns?|lamps?|laterne|lampe)\b)", re.I | re.S)
GLOW_WORDS = re.compile(r"\b(glow ?sticks?|light ?sticks?|chem ?lights?|cyalume|glowsticks?)\b", re.I)


def light(category, words, note="", deeper=False, must=None, question=ASK_LIGHT):
    """A Commons spec for home_packs.build_commons_topic: "<question>" -> "This is <words>." and the note; must: only
    files whose title or words match this pattern."""
    spec = (category, deeper, [(question, f"This is {words}." + (f" {note}" if note else ""))])
    return spec + (must,) if must is not None else spec


EMERGENCY_LIGHTING = [
    # battery and electric
    light("Flashlights", "a flashlight (torch)"),
    light("LED flashlights", "an LED flashlight (torch)", deeper=True),
    light("Emergency lighting", "emergency lighting, which comes on by itself when the power fails", deeper=True),
    light("Chemiluminescence", "a glow stick (light stick): bend it to break the glass inside and it glows for hours "
                               "without heat or flame", deeper=True, must=GLOW_WORDS),
    light("Portable power stations", "a portable power station: a large rechargeable battery with sockets and USB "
                                     "ports, often charged by solar panels, that can run lights and small devices",
          BATTERY_NOTE, deeper=True, question=ASK_WHAT),
    light("Battery banks", "a battery bank: batteries joined to store power", BATTERY_NOTE, question=ASK_WHAT),
    # The battery packs category is asked by packs/electronics_packs.py (with the lithium note), so it is not repeated.
    light("Rechargeable batteries", "rechargeable batteries", BATTERY_NOTE, question=ASK_WHAT),
    light("Lithium batteries", "lithium batteries", BATTERY_NOTE + " Never put lithium batteries in a fire.",
          question=ASK_WHAT),
    light("Alkaline batteries", "alkaline batteries", BATTERY_NOTE, question=ASK_WHAT),
    # fuel lanterns and lamps
    light("Kerosene lamps", "a kerosene lamp, with a wick and a glass chimney", FUEL_LIGHT_NOTE, deeper=True,
          must=NOT_OLD),
    light("Hurricane lamps", "a hurricane lamp (storm lantern): a wick lamp with a glass globe that keeps the flame "
                             "out of the wind", FUEL_LIGHT_NOTE, deeper=True, must=NOT_OLD),
    light("Lanterns", "a lantern", FUEL_LIGHT_NOTE + " (If it runs on batteries, none of the fuel warnings apply.)",
          must=LANTERN_WORDS),
    light("Petromax lamps", "a Petromax pressure lantern: a kerosene lantern that is pumped up to pressure and burns "
                            "its fuel as gas in a glowing mantle", FUEL_LIGHT_NOTE, must=NOT_OLD),
    light("Tilley lamps", "a Tilley lamp, a kerosene (paraffin) pressure lamp with a mantle", FUEL_LIGHT_NOTE,
          deeper=True, must=NOT_OLD),
    light("Coleman Company", "a Coleman lantern or lamp", FUEL_LIGHT_NOTE, must=LAMP_WORDS),
    light("Gas mantles", "a gas mantle: a small fabric bag fitted to a gas or pressure lantern; after its first "
                         "burning it is a fragile ash shell that glows brightly", FUEL_LIGHT_NOTE, deeper=True,
          question=ASK_WHAT, must=NOT_OLD),
    light("Wicks", "a lamp or candle wick", FUEL_LIGHT_NOTE, deeper=True, question=ASK_WHAT, must=NOT_OLD),
    light("Candles", "a candle", CANDLE_NOTE),
    light("Tealights", "a tealight, a small candle in a metal or plastic cup", CANDLE_NOTE, deeper=True),
    light("Pillar candles", "a pillar candle, a thick candle that stands on its own", CANDLE_NOTE),
    light("Candle holders", "a candle holder", CANDLE_NOTE, question=ASK_WHAT, must=NOT_OLD),
    light("Candle lanterns", "a candle lantern: a candle inside a glass or metal case", CANDLE_NOTE, deeper=True,
          must=NOT_OLD),
    light("Candle snuffers", "a candle snuffer, a small cup on a handle for putting out a candle", CANDLE_NOTE,
          deeper=True, question=ASK_WHAT, must=NOT_OLD),
]


def build_commons_emergency_lighting(limit):
    """The commons_emergency_lighting pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(EMERGENCY_LIGHTING, limit, "emlight")


LIGHTING_OI = [
    group("What lights are in this picture?", {"Headlamp": "a headlamp (a head torch)"}),
    group("What fuel lamps are in this picture?", {"Oil lamp": "an oil lamp"}, FUEL_LIGHT_NOTE),
    group("What candle things are in this picture?", {"Candle holder": "a candle holder"}, CANDLE_NOTE),
    group("Are there matches in this picture?", {"Match": "matches"}, MATCH_NOTE),
]


def build_open_images_emergency_lighting(limit):
    """open_images_emergency_lighting (see the module docstring)."""
    return build_oi_gap("open_images_emergency_lighting", LIGHTING_OI, limit, 9304)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of flashlight, battery, lantern, lamp, mantle, wick and candle categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
LIGHTING_PACKS = {
    "commons_emergency_lighting": (build_commons_emergency_lighting, COMMONS_LICENCE),
    "open_images_emergency_lighting": (build_open_images_emergency_lighting, OI_LICENCE),
}
LIGHTING_LIMITS = {
    "commons_emergency_lighting": 1200,       # 25 categories
    "open_images_emergency_lighting": 800,    # 4 labels
}
LIGHTING_COMMONS_KEYS = ("commons_emergency_lighting",)
LIGHTING_SPECS = EMERGENCY_LIGHTING


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an emergency lighting pack builder.")
    parser.add_argument("key", choices=sorted(LIGHTING_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = LIGHTING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
