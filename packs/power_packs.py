"""Picture packs for POWER AND ELECTRICAL: backup generators, solar panels and batteries, and small wind and water
power (the owner's request of 2026-11-22). Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes
once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

Why: the owner is blind, likes modern equipment and do-it-yourself projects, and wants the picture describer (and his
offline assistant) to recognise generators and their safety labels, solar panels, charge controllers and connectors,
battery banks, wind turbines, water wheels and water turbines, fuel and electrical things, and to say the safety rules
that go with each one.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no brand, model, wattage or voltage is named unless the category itself names it. Every answer about a
generator, fuel, solar panel, battery, turbine or wiring ends with the safety notes that fit it (the same words in the
kit's power_sources.py and the books' and manuals' notices):
  GENERATOR_NOTE  carbon monoxide: outdoors only, at least 20 feet from the house, exhaust away from windows, doors
                  and vents; a CO alarm; get out and call 911 if it sounds or anyone feels ill.
  BACKFEED_NOTE   never plug a generator into a wall or dryer outlet (back-feeding can kill utility line workers);
                  house wiring only through a transfer switch or interlock installed by a licensed electrician.
  FUEL_NOTE       engine off and cool before refuelling; approved containers stored away from the house.
  DIY_NOTE        home-made generators: guard belts and rotating parts, and never connect one to house wiring.
  SOLAR_NOTE      panels are live whenever light falls on them; DC wiring arcs and shocks; disconnects off before
                  touching wiring; roof work needs fall protection; house connection by a licensed electrician;
                  firefighters need the rapid shutdown switch.
  BATTERY_NOTE    short circuits, lithium fires (thermal runaway), hydrogen from lead-acid batteries, acid; fuse
                  every circuit, ventilate, eye protection, never charge a swollen or damaged battery.
  TURBINE_NOTE    blades and wheels can kill: stop and brake first; towers only with fall protection and a partner,
                  never in storms (lightning); intakes and penstocks hold strong currents.
  WIRING_NOTE     power off at the breaker and tested before touching wiring; a licensed electrician when in doubt.
  LINE_NOTE       10 feet from overhead lines; a downed line is live: keep away and call 911 and the power company.

The packs (POWER_PACKS):
  commons_generators_power   Wikimedia Commons (CC0, public domain or CC BY files only): engine generators (only files
                             whose own words name a portable, standby, diesel, gasoline, inverter or similar set),
                             Generac generators, the CPSC's required generator carbon monoxide danger labels (16 CFR
                             1407), dynamos, bicycle dynamos and hydroelectric generators.
  commons_solar_batteries    Commons: solar cells, building-integrated photovoltaics, solar trackers and carports,
                             solar-powered boats, solar panels in the United States, MC4 connectors, charge controllers,
                             lead-acid, VRLA (AGM and gel), deep-cycle and lithium iron phosphate batteries, battery
                             monitors, the Tesla Powerwall and battery storage stations.
  commons_wind_water_power   Commons: wind turbine towers and blades, Savonius turbines, wind pumps and American
                             windmills, water wheels (overshot, undershot, breastshot), Pelton wheels, cross-flow,
                             Kaplan and Francis turbines, penstocks and pico hydro.
  open_images_power          Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                             solar panels and solar power, solar chargers and solar vehicles, wind turbines and
                             windmills, fuel (gasoline, diesel, propane, fuel tanks), batteries, wall sockets, circuit
                             breakers, power supplies and electrical grounds, overhead power lines and line workers,
                             welders and carbon monoxide detectors. No label is asked twice (packs/test_power.py
                             checks).

Not repeated here: the preparedness packs' Mobile engine-generators, Emergency power system, Uninterruptible power
supply and Fuel containers (commons_emergency_kits_power) and the Open Images label Electric generator
(open_images_disasters); the lighting packs' portable power stations, battery banks, rechargeable and lithium
batteries (commons_emergency_lighting); land_industry_packs' Solar panels, Photovoltaic power stations and Wind
turbines; things_packs' Solar panels, lamps and chargers; mechanical_packs' Alternators, Engine-generators and
Portable electrical generators; hardware_packs' NEMA plugs, Portable generators and Circuit breakers; chemical_packs'
Jerrycans; and the Carbon monoxide detectors of the home safety packs. What was looked at and left out is in the kit's
power_sources.py (POWER_NOT_INCLUDED).

    python packs/power_packs.py commons_solar_batteries --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from outdoor_cooking_packs import with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

GENERATOR_NOTE = ("Carbon monoxide: run a generator only outdoors, at least 20 feet from the house with its exhaust "
                  "pointed away from windows, doors and vents, never in a home, garage, basement, crawl space or "
                  "shed, even with the door open. Have a working carbon monoxide alarm; if it sounds or anyone feels "
                  "dizzy, sick or weak, get out to fresh air and call 911.")
BACKFEED_NOTE = ("Never plug a generator into a wall or dryer outlet: back-feeding can kill utility line workers and "
                 "neighbours. Connect it to house wiring only through a transfer switch or interlock kit installed by "
                 "a licensed electrician; otherwise plug appliances into the generator with heavy-duty outdoor "
                 "extension cords.")
FUEL_NOTE = ("Fuel: turn the engine off and let it cool before refuelling, and store fuel in approved containers away "
             "from the house and any flame.")
DIY_NOTE = ("Home-made generators: guard belts, pulleys and other rotating parts, keep it dry, and never connect it "
            "to house wiring except through a transfer switch installed by a licensed electrician.")
SOLAR_NOTE = ("Solar safety: panels make electricity whenever light falls on them and DC wiring can arc and shock: "
              "turn off the disconnects before touching wiring, and use fall protection on roofs. Connecting to the "
              "house and the grid is work for a licensed electrician; firefighters need the system's rapid shutdown "
              "switch.")
BATTERY_NOTE = ("Battery safety: a short circuit across a large battery can melt tools and start a fire; a damaged or "
                "overheated lithium battery can catch fire (thermal runaway); lead-acid batteries hold acid and give "
                "off explosive hydrogen while charging. Fuse every battery circuit, ventilate lead-acid batteries, "
                "wear eye protection, and never charge a swollen or damaged battery.")
TURBINE_NOTE = ("Turbine safety: moving blades and wheels can kill; stop and brake the turbine before going near it. "
                "Climb a tower only with fall protection and a partner, never in a storm (lightning); water intakes "
                "and penstocks hold strong currents.")
WIRING_NOTE = ("Electrical safety: turn the power off at the breaker and check it is off with a tester before "
               "touching wiring; if in doubt, call a licensed electrician.")
LINE_NOTE = ("Power lines: stay at least 10 feet away from overhead lines; treat a fallen line as live, keep away, "
             "and call 911 and the power company.")

GEN_NOTES = f"{GENERATOR_NOTE} {BACKFEED_NOTE} {FUEL_NOTE}"
ASK_WHAT = "What is this?"
NOTES = (GENERATOR_NOTE, BACKFEED_NOTE, FUEL_NOTE, DIY_NOTE, SOLAR_NOTE, BATTERY_NOTE, TURBINE_NOTE, WIRING_NOTE,
         LINE_NOTE)


def thing(category, words, notes="", deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


# ----------------------------------------------------------------- Commons: generators

# "Electrical generators" also holds power-station machines and laboratory pieces: only files whose own words name
# the kind of generator a home, farm, camper or work site uses.
GEN_WORDS = re.compile(r"\b(portable|standby|back-?up|emergency|diesel|petrol|gasoline|propane|dual[- ]fuel|"
                       r"inverter|genset|generator set|generac|honda|kohler|champion|yamaha|onan|cummins|"
                       r"military|tactical|trailer|tractor|pto|welder|camping|caravan|rv)\b", re.I)
GENERATORS = [
    thing("Electrical generators", "an engine generator set that makes electricity", GEN_NOTES, pattern=GEN_WORDS),
    thing("Generac Power Systems", "a Generac generator (Generac makes portable and home standby generators)",
          GEN_NOTES),
    thing("16 CFR 1407 Generator safety labels", "the carbon monoxide danger label that US law (16 CFR 1407) requires "
          "on portable generators: using a generator indoors can kill you in minutes", GEN_NOTES),
    thing("Dynamos", "a dynamo, a machine that turns movement into direct-current electricity", DIY_NOTE, True),
    thing("Bicycle dynamos", "a bicycle dynamo, which makes electricity from the turning wheel for the bike's lights",
          deeper=True),
    thing("Hydroelectric generators", "a hydroelectric generator, which a water turbine turns to make electricity",
          TURBINE_NOTE, True),
]

# ----------------------------------------------------------------- Commons: solar panels and batteries

SOLAR_BATTERIES = [
    thing("Solar cells", "solar cells, the parts of a solar panel that turn light into electricity", SOLAR_NOTE,
          True),
    thing("Building-integrated photovoltaics", "solar panels built into a building's roof, walls or windows",
          SOLAR_NOTE, True),
    thing("Solar trackers", "a solar tracker, a mount that turns solar panels to follow the sun", SOLAR_NOTE, True),
    thing("Solar carports", "a solar carport, a car shelter roofed with solar panels", SOLAR_NOTE),
    thing("Solar-powered boats", "a solar-powered boat", f"{SOLAR_NOTE} {BATTERY_NOTE}", True),
    thing("Solar panels in the United States", "solar panels in the United States", SOLAR_NOTE, True),
    thing("MC4 connectors", "MC4 connectors, the push-together plugs that join solar panel cables; disconnect them "
                            "only with no current flowing", SOLAR_NOTE),
    thing("Charge controllers", "a charge controller, which controls how solar panels or a wind turbine charge a "
                                "battery", f"{SOLAR_NOTE} {BATTERY_NOTE}", True),
    thing("Solar charge controllers", "a solar charge controller, which controls how solar panels charge a battery",
          f"{SOLAR_NOTE} {BATTERY_NOTE}"),
    thing("Lead-acid batteries", "a lead-acid battery", BATTERY_NOTE, True),
    thing("VRLA batteries", "a sealed valve-regulated lead-acid (VRLA) battery, the AGM or gel kind", BATTERY_NOTE),
    thing("Deep cycle batteries", "a deep-cycle battery, made to be run down and recharged again and again, as in "
                                  "solar systems, campers and boats", BATTERY_NOTE),
    thing("Lithium iron phosphate batteries", "a lithium iron phosphate (LiFePO4) battery", BATTERY_NOTE),
    thing("Battery monitors", "a battery monitor, which shows a battery's voltage, current and charge", BATTERY_NOTE),
    thing("Tesla Powerwall", "a Tesla Powerwall, a home battery that stores electricity from solar panels or the "
                             "grid", f"{BATTERY_NOTE} Installation is work for a licensed electrician."),
    thing("Battery storage power stations", "a battery storage station, rows of large batteries that store "
                                            "electricity for the grid", BATTERY_NOTE, True),
]

# ----------------------------------------------------------------- Commons: wind and water power

WIND_WATER = [
    thing("Wind turbine towers", "a wind turbine tower", TURBINE_NOTE),
    thing("Wind turbine blades", "wind turbine blades", TURBINE_NOTE, True),
    thing("Savonius wind turbines", "a Savonius wind turbine, a vertical-axis turbine with curved scoops",
          TURBINE_NOTE, True),
    thing("Wind pumps", "a wind pump, a windmill that pumps water", TURBINE_NOTE, True),
    thing("Windmills in the United States", "a windmill in the United States", TURBINE_NOTE, True),
    thing("Water wheels", "a water wheel, turned by flowing or falling water", TURBINE_NOTE, True),
    thing("Overshot water wheels", "an overshot water wheel: the water falls onto the top of the wheel",
          TURBINE_NOTE, True),
    thing("Undershot water wheels", "an undershot water wheel: the stream pushes the bottom of the wheel",
          TURBINE_NOTE, True),
    thing("Breastshot water wheels", "a breastshot water wheel: the water meets the wheel about halfway up",
          TURBINE_NOTE, True),
    thing("Pelton wheels", "a Pelton wheel, a water turbine with cups that jets of water strike, used where water "
                           "falls from a height (high head)", TURBINE_NOTE, True),
    thing("Cross-flow turbines", "a cross-flow water turbine, in which water flows across a drum of curved blades",
          TURBINE_NOTE),
    thing("Kaplan turbines", "a Kaplan turbine, a propeller-type water turbine for low falls of water", TURBINE_NOTE,
          True),
    thing("Francis turbines", "a Francis turbine, a water turbine used in many hydroelectric plants", TURBINE_NOTE,
          True),
    thing("Penstocks", "a penstock, the pipe that carries water down to a water turbine", TURBINE_NOTE, True),
    thing("Pico hydro", "a pico hydro set, a very small water turbine and generator", f"{TURBINE_NOTE} {DIY_NOTE}"),
]


def build_commons_generators_power(limit):
    """The commons_generators_power pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(GENERATORS, limit, "powergen")


def build_commons_solar_batteries(limit):
    """The commons_solar_batteries pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(SOLAR_BATTERIES, limit, "solarbatt")


def build_commons_wind_water_power(limit):
    """The commons_wind_water_power pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(WIND_WATER, limit, "windwater")


# ----------------------------------------------------------------- Open Images

POWER_OI = [
    group("What solar power things are in this picture?",
          {"Solar panel": "a solar panel", "Solar power": "something to do with solar power",
           "Solar energy": "something to do with solar energy",
           "Solar charger": "a solar charger", "Solar vehicle": "a solar vehicle"}, SOLAR_NOTE),
    group("What wind power things are in this picture?",
          {"Wind turbine": "a wind turbine", "Windmill": "a windmill", "Turbine": "a turbine"}, TURBINE_NOTE),
    group("What fuel is in this picture?",
          {"Gasoline": "gasoline (petrol)", "Diesel fuel": "diesel fuel", "Propane": "propane",
           "Fuel tank": "a fuel tank", "Fuel": "fuel"}, FUEL_NOTE),
    group("What batteries are in this picture?",
          {"Multipurpose battery": "a battery", "Automotive battery": "a car battery"}, BATTERY_NOTE),
    group("What electrical things are in this picture?",
          {"Wall socket": "a wall socket", "Circuit breaker": "a circuit breaker", "Power supply": "a power supply",
           "Ground (electricity)": "an electrical ground (earth) connection", "Electricity": "something to do with electricity"},
          WIRING_NOTE),
    group("What power line things are in this picture?",
          {"Overhead power line": "overhead power lines", "Lineman": "a line worker (lineman)"},
          f"{LINE_NOTE} {BACKFEED_NOTE}"),
    group("Is there a welder in this picture?", {"Welder": "a welder"},
          "Welding safety: a welding helmet, gloves and fresh air; keep anything that can burn away."),
    group("Is there a carbon monoxide detector in this picture?",
          {"Carbon monoxide detector": "a carbon monoxide detector"}, GENERATOR_NOTE),
]


def build_open_images_power(limit):
    """open_images_power (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_power", POWER_OI, limit, 9321), POWER_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
POWER_PACKS = {
    "commons_generators_power": (build_commons_generators_power, COMMONS_LICENCE.format(
        what="engine generator, generator safety label, dynamo and hydroelectric generator")),
    "commons_solar_batteries": (build_commons_solar_batteries, COMMONS_LICENCE.format(
        what="solar cell, solar mount, connector, charge controller and battery")),
    "commons_wind_water_power": (build_commons_wind_water_power, COMMONS_LICENCE.format(
        what="wind turbine, wind pump, water wheel and water turbine")),
    "open_images_power": (build_open_images_power, OI_LICENCE),
}
POWER_LIMITS = {
    "commons_generators_power": 500,      # 6 categories; the generator files are filtered by their own words
    "commons_solar_batteries": 900,       # 16 categories, few files in some
    "commons_wind_water_power": 1200,     # 15 categories
    "open_images_power": 1500,            # 25 labels; Windmill and Electricity have most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
POWER_COMMONS_KEYS = ("commons_generators_power", "commons_solar_batteries", "commons_wind_water_power")
# The Commons category specs of the packs (for the self-test).
POWER_SPECS = GENERATORS + SOLAR_BATTERIES + WIND_WATER


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a power and electrical pack builder.")
    parser.add_argument("key", choices=sorted(POWER_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = POWER_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
