"""POWER AND ELECTRICAL for the Picture Model Training Kit (the owner's request of 2026-11-22: backup generators, solar
and battery power, small wind and water power, and electrical things). This file lists:
  - the ready-made packs built in packs/power_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_generators_power, commons_solar_batteries, commons_wind_water_power and open_images_power;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (POWER_NOT_INCLUDED);
  - which topic add-ons hold them (POWER_TOPICS), and the existing electrical collections the "power" topic also
    holds (POWER_TOPIC_EXISTING: wiring, outlets, panels, plugs, cables, circuits, batteries and backup power).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked), and every
answer about a generator, fuel, solar panel, battery, turbine or wiring ends with the safety notes that fit it:
carbon monoxide (generators outdoors only, 20 feet from the house; get out and call 911 if a CO alarm sounds), never
back-feed (a transfer switch or interlock installed by a licensed electrician), fuel, DC arcs and roof falls, battery
fires, rotating blades and wheels, and wiring. The notes are the same words as the packs' (packs/test_power.py
checks).

Picture-making (POWER_PICTURE_MAKING_OK): the Commons generators, solar and battery, and wind and water collections
(things); sources.py puts every other key in NOT_FOR_PICTURE_MAKING (the Open Images photos show people).
Topics: everything here is in the "power" topic (Power and electrical); the generators, solar panels and batteries are
also in "home", and the generators and turbines also in "machines".

    python -c "import sources, power_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/power_packs.py.
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


# The categories of packs/power_packs.py whose files need no word filter (the share-alike entry has none; the
# filtered "Electrical generators" category is left out here).
POWER_SA = [
    gear("Generac Power Systems", "a Generac generator (Generac makes portable and home standby generators)",
         GEN_NOTES),
    gear("Dynamos", "a dynamo, a machine that turns movement into direct-current electricity", DIY_NOTE, True),
    gear("Solar cells", "solar cells, the parts of a solar panel that turn light into electricity", SOLAR_NOTE, True),
    gear("Solar trackers", "a solar tracker, a mount that turns solar panels to follow the sun", SOLAR_NOTE, True),
    gear("MC4 connectors", "MC4 connectors, the push-together plugs that join solar panel cables; disconnect them "
                           "only with no current flowing", SOLAR_NOTE),
    gear("Charge controllers", "a charge controller, which controls how solar panels or a wind turbine charge a "
                               "battery", f"{SOLAR_NOTE} {BATTERY_NOTE}", True),
    gear("Lead-acid batteries", "a lead-acid battery", BATTERY_NOTE, True),
    gear("Lithium iron phosphate batteries", "a lithium iron phosphate (LiFePO4) battery", BATTERY_NOTE),
    gear("Wind turbine towers", "a wind turbine tower", TURBINE_NOTE),
    gear("Wind pumps", "a wind pump, a windmill that pumps water", TURBINE_NOTE, True),
    gear("Water wheels", "a water wheel, turned by flowing or falling water", TURBINE_NOTE, True),
    gear("Pelton wheels", "a Pelton wheel, a water turbine with cups that jets of water strike, used where water "
                          "falls from a height (high head)", TURBINE_NOTE, True),
    gear("Penstocks", "a penstock, the pipe that carries water down to a water turbine", TURBINE_NOTE, True),
]


def prepare_power_commons_sa(source, data_dir, work, cap):
    """Commons generator, solar, battery, wind and water power categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(POWER_SA, cap, source.test, "power-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

POWER_SOURCES = [
    Source("commons_generators_power", "Generators: engine generator sets, Generac generators, the carbon monoxide "
                                       "danger labels on portable generators, dynamos and hydroelectric generators, "
                                       "with carbon monoxide and back-feeding notes (Wikimedia Commons, ready-made "
                                       "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 5, prepare_pack, "about 110 MB"),
    Source("commons_solar_batteries", "Solar and batteries: solar cells, panels on buildings, trackers and carports, "
                                      "MC4 connectors, charge controllers, lead-acid, AGM and gel, deep-cycle and "
                                      "LiFePO4 batteries, battery monitors and home batteries, with solar and "
                                      "battery safety notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_wind_water_power", "Wind and water power: wind turbine towers and blades, vertical-axis "
                                       "turbines, wind pumps and windmills, water wheels, Pelton, cross-flow, Kaplan "
                                       "and Francis turbines, penstocks and pico hydro (Wikimedia Commons, "
                                       "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 12, prepare_pack, "about 260 MB"),
    Source("open_images_power", "Solar panels and solar power, wind turbines and windmills, fuel, batteries, wall "
                                "sockets, circuit breakers, power lines and line workers, welders and carbon "
                                "monoxide detectors (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("power_commons_sa", "Wikimedia Commons: Generac generators, dynamos, solar cells and trackers, MC4 "
                               "connectors, charge controllers, lead-acid and LiFePO4 batteries, wind turbine "
                               "towers, wind pumps, water wheels, Pelton wheels and penstocks, files under CC BY-SA "
                               "or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 600, 10, prepare_power_commons_sa, "about 130 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons things; never the Open Images photos (people).
POWER_PICTURE_MAKING_OK = {"commons_generators_power", "commons_solar_batteries", "commons_wind_water_power",
                           "power_commons_sa"}

# The topic add-ons (topics.py) that hold each collection of this file (packs/test_power.py checks they match).
POWER_TOPICS = {
    "power": tuple(s.key for s in POWER_SOURCES),
    "home": ("commons_generators_power", "commons_solar_batteries", "open_images_power", "power_commons_sa"),
    "machines": ("commons_generators_power", "commons_wind_water_power"),
}

# The kit's existing collections about electricity, wiring, outlets, panels, plugs, cables, circuits, batteries and
# backup power that the "power" topic also holds (the owner's decision of 22 November 2026; they stay in their own
# topics too).
POWER_TOPIC_EXISTING = (
    "commons_home_repair",            # home repair, with power strips and the electrical note
    "open_images_home_upkeep",        # electrical wiring, supplies and switches
    "home_upkeep_commons_sa",         # its share-alike Commons files
    "commons_plumbing_electrical",    # outlets, switches, wire nuts, boxes, breakers, cables and NEMA plug types
    "commons_connectors",             # mains plugs and sockets, connectors and battery sizes
    "commons_electronic_parts",       # fuses, relays, switches, batteries and other parts
    "commons_cables_connectors",      # cables and connectors
    "commons_circuit_diagrams",       # circuit diagrams and symbols
    "open_images_electronics",        # electronic and electrical things
    "commons_emergency_lighting",     # portable power stations, battery banks and batteries
    "commons_emergency_kits_power",   # backup power: mobile generators, emergency power and UPS units
    "commons_pcb_fabrication",        # circuit board making: PCB milling, stencils and reflow (making_sources.py)
)

POWER_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Mobile engine-generators, Emergency power system, "
        "Uninterruptible power supply and Fuel containers (preparedness_packs), Engine-generators, Diesel generators, "
        "Portable electrical generators and Alternators (mechanical_packs), Portable generators, NEMA connectors and "
        "Circuit breakers (hardware_packs), Solar panels, Photovoltaic power stations and Wind turbines "
        "(land_industry_packs, things_packs), Portable power stations, Battery banks and the battery categories "
        "(lighting_packs, electronics_packs), Jerrycans (chemical_packs) and Carbon monoxide detectors (the home "
        "safety packs): not asked twice.",
    "Commons categories that do not exist or hold no files under the names tried (November 2026)": "Inverter "
        "generators, Standby generators, Transfer switches, Automatic transfer switches, Interlock kits, Power "
        "inlets, Power take-off generators, Welder generators, Truck-mounted generators, Tactical Quiet Generators, "
        "Solar inverters, Power inverters, Microinverters, Maximum power point trackers, Off-grid solar, Rooftop "
        "photovoltaic installations, Monocrystalline and Polycrystalline solar panels, Thin-film solar cells, Solar "
        "water pumps, Solar electric fences, Home batteries, Small wind turbines, Vertical axis wind turbines, Micro "
        "hydro, Turgo turbines, Pedal generators, Hub dynamos; NEMA TT-30, NEMA 14-30, NEMA 14-50 and NEMA 5-20 "
        "exist but hold no files. The packs use the categories that hold files.",
    "Open Images labels asked elsewhere or with too few checked photos": "Electric generator and Uninterruptible "
        "power supply (preparedness packs), Battery, Battery charger, Extension cord, Electrical wiring, Fuse, Plug "
        "and Power plugs and sockets (other packs) are never asked twice; Power inverter (7 checked photos), "
        "Electricity meter (5), Fuel cell (3) and Voltmeter (1) have almost no human-checked photos in Open Images V7 "
        "(counted 2026-11-22); Recreational vehicle (RV), Caravan and Power station show the vehicle or the power "
        "plant, not power equipment, so they are not asked.",
    "NREL (now the National Laboratory of the Rockies) Image Gallery": "images.nrel.gov and www.nrel.gov did not "
        "answer this build machine (2026-11-22), and the laboratory's disclaimer says its documents \"may be "
        "subject to U.S. and foreign Copyright Laws\" (it is run by a contractor, so its work is not automatically "
        "public domain). NREL photos that people copied to Commons under an open licence are reached through the "
        "Commons categories.",
    "DOE, FEMA and OSHA photo libraries": "www.fema.gov and www.osha.gov answer programs \"403\" (2026-11-22); "
        "energy.gov has no photo listing a program can read by subject. Their public-domain photos copied to "
        "Commons are reached through the Commons categories.",
    "Open Source Ecology (Power Cube and solar designs)": "CC BY-SA, but wiki.opensourceecology.org's robots.txt "
        "says ai-train=no and shuts out AI companies' crawlers (checked 2026-11-22); not read.",
    "Makers' product photos (Generac, Honda, Champion, Westinghouse, Kohler, EcoFlow, Jackery, Goal Zero, Renogy, "
    "Victron, Enphase, SolarEdge, Tesla, Battle Born)": "the makers' copyright; not used. Their manuals are linked "
        "in the manual collections of the Power and electrical heading.",
    "Roboflow Universe and Kaggle solar panel defect and dust sets": "Roboflow Universe's robots.txt disallows the "
        "dataset download pages, and the Kaggle sets need an account and often do not say where their photos come "
        "from (see gaps_sources.py).",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the power share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in POWER_SOURCES if s.key == "power_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="power-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
