"""CAR CARE BASICS for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/car_care_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_car_care, commons_ev_charging, commons_dashboard_lights, open_images_car_care;
  - the share-alike Commons files of the same car care categories (car_care_commons_sa: group "share-alike", only
    with the share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (CAR_CARE_NOT_INCLUDED).

Already in the kit and not repeated: car parts by name, engine bays and dashboards (commons_car_parts,
commons_engine_bays), the ISO 7000 symbols and the main tell-tales (iso_machine_symbols), the share-alike dashboard
symbols (dashboard_symbols_sa) and the Roboflow dashboard warning icons (dashboard_warning_icons, personal use), tyre
and spark plug condition, NHTSA recalls in the reference library (textbooks/recalls.py).

Answers say only what the source says. The safety notes are the same words as the packs' (JACK_NOTE, HOT_NOTE,
BATTERY_NOTE, ROADSIDE_NOTE, CHARGING_NOTE). As in drinks_sources.py, nothing here is re-shared by the kit's makers:
each collection is downloaded by the kit on the user's own computer, only when the user ticks its choice. Every
licence was checked at its source in November 2026.

Picture-making (CAR_CARE_PICTURE_MAKING_OK): the Commons car care things, EV connectors and dashboard symbols may be
used (things and drawings); the Open Images photos may not (people and number plates).

    python -c "import sources, car_care_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

JACK_NOTE = ("Safety: never get under a car held up only by a jack; use jack stands on firm, level ground, set the "
             "parking brake and chock the wheels.")
HOT_NOTE = ("Safety: never open the radiator or coolant cap of a hot engine; hot coolant can spray out and scald. "
            "Let the engine cool first.")
BATTERY_NOTE = ("Safety: car batteries hold acid that burns and give off explosive gas; wear eye protection, keep "
                "flames and sparks away, and follow the car's handbook for the order of the jump leads.")
ROADSIDE_NOTE = ("Safety: if your car breaks down, get as far off the road as you can, turn on the hazard lights, "
                 "stay away from traffic and call for help (911 in an emergency).")
CHARGING_NOTE = "Use only undamaged, certified charging equipment, as the car's maker says."

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


def thing(category, words, note="", deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the note."""
    return (category, "What car part or car care item is this?", f"This is {words}." + (f" {note}" if note else ""),
            deeper)


# The main categories of packs/car_care_packs.py (the ones with many share-alike files).
CAR_CARE_SA = [
    thing("Windscreen wipers", "a windscreen wiper (windshield wiper), which clears rain from the glass"),
    thing("Motor oil", "motor oil (engine oil), which keeps the engine's moving parts from wearing", HOT_NOTE),
    thing("Car jacks", "a car jack, for lifting a car to change a wheel", JACK_NOTE),
    thing("Spare tires", "a spare tyre", JACK_NOTE),
    thing("Snow chains", "snow chains, fitted over tyres for grip on snow and ice"),
    thing("Wheel chocks", "a wheel chock, a wedge put against a wheel so the car cannot roll"),
    thing("Warning triangles", "a warning triangle, set up behind a broken-down car to warn other drivers",
          ROADSIDE_NOTE),
    thing("Vehicle breakdowns", "a broken-down vehicle", ROADSIDE_NOTE),
    thing("AdBlue", "diesel exhaust fluid (AdBlue), a liquid that some diesel vehicles need topped up in its own tank, "
                    "never in the fuel tank"),
    thing("CHAdeMO", "a CHAdeMO connector, a round fast-charging plug used mostly by older Japanese electric cars",
          CHARGING_NOTE),
    thing("Tesla Supercharger", "a Tesla Supercharger, a fast charging post", CHARGING_NOTE),
    thing("IEC 62196", "an IEC 62196 electric car charging plug or socket (Type 1, Type 2 or CCS)", CHARGING_NOTE),
    thing("Wallboxes", "a wallbox, a home charging unit for an electric car", CHARGING_NOTE),
]


def prepare_car_care_commons_sa(source, data_dir, work, cap):
    """Commons car care and charging categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(CAR_CARE_SA, cap, source.test, "carcare-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


CAR_CARE_SOURCES = [
    Source("commons_car_care", "Car care: wipers, bulbs, motor oil and washer fluid, coolant and brake fluid "
                               "reservoirs, jump starters, tyre valves, sidewall markings and wear bars, snow chains, "
                               "jacks, jack stands and wheel chocks, spare tyres, warning triangles, flares and "
                               "breakdowns, with safety notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1800, 20, prepare_pack, "about 400 MB"),
    Source("commons_ev_charging", "Electric car charging connectors and ports: J1772, CCS, CHAdeMO, NACS (Tesla), "
                                  "Type 2, cables and wallboxes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 130 MB"),
    Source("commons_dashboard_lights", "Dashboard warning lights, each meaning taken from the symbol file's own words "
                                       "(about 45 lights: tyre pressure, oil, coolant, battery, brakes, check engine, "
                                       "traction control, AdBlue, EV turtle mode and more), with what to do (Wikimedia "
                                       "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 10, prepare_pack, "about 30 MB"),
    Source("open_images_car_care", "Tyres, treads, rims and hubcaps, car lights, motor oil and antifreeze, gauges, "
                                   "steering wheels and gear levers, electric cars, tow trucks, car washes and traffic "
                                   "cones (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2500, 25, prepare_pack, "about 500 MB"),
    Source("car_care_commons_sa", "Wikimedia Commons: wipers, motor oil, jacks, spare tyres, snow chains, wheel "
                                  "chocks, warning triangles, breakdowns, AdBlue and EV charging connectors, files "
                                  "under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_car_care_commons_sa, "about 180 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# Things and drawings may be used for picture-making; the Open Images photos may not (people, number plates).
CAR_CARE_PICTURE_MAKING_OK = {"commons_car_care", "commons_ev_charging", "commons_dashboard_lights",
                              "car_care_commons_sa"}

CAR_CARE_NOT_INCLUDED = {
    "NHTSA's pictures and consumer pages (nhtsa.gov: tyre safety, recalls, car seats)":
        "www.nhtsa.gov answers programs \"403 Forbidden\", robots.txt included (checked 2026-11-22), so nothing is "
        "read from it. Its recalls already reach the reference library through NHTSA's API (textbooks/recalls.py); "
        "its tyre safety guide is linked from the manual library's car_care category.",
    "FMCSA (fmcsa.dot.gov) pictures":
        "fmcsa.dot.gov answers programs \"403 Forbidden\" (checked 2026-11-22); its material is for commercial "
        "drivers.",
    "FuelEconomy.gov (DOE/EPA) pictures and maintenance pages":
        "its robots.txt does not allow this builder's reader on /feg/ (checked 2026-11-22); not read.",
    "Owner's manual pictures (makers' handbooks)":
        "copyright of the car makers; their manuals are LINKED by the manual library (category cars), never copied.",
    "Commons categories that do not exist or hold no files under the names tried (November 2026)":
        "Dashboard warning lights, Automobile warning lights, Check engine lights, ISO 2575 symbols, ISO 2575, "
        "Tire changing, Tire pressure monitoring systems, Tire inflators, Tire repair kits, Car emergency kits, "
        "Broken down vehicles, Engine coolant, Car batteries, Floor jacks, Jack stands (empty), SAE J1772 (empty), "
        "Combined Charging System (empty), Type 2 connector, Electric vehicle charging cables and Charging ports of "
        "electric vehicles; the dashboard lights are found by their file titles instead "
        "(commons_dashboard_lights), and the charging plugs through IEC 62196's subcategories.",
    "Open Images labels already asked elsewhere or missing":
        "Car, Wheel, Vehicle and the car brands are asked by other packs; Open Images has no label for windscreen "
        "wipers, jumper cables, car jacks, spare tyres, warning triangles, charging stations or dashboards.",
    "YouTube car care videos, Instructables, Pinterest, Reddit and car forums":
        "not read: their terms forbid scraping or the pictures are their users' own (the owner's rule).",
    "Roboflow Universe car dashboard and tyre sets":
        "Roboflow Universe's robots.txt disallows the dataset download pages (see gaps_sources.py); the dashboard "
        "warning icons set is already the personal-use entry dashboard_warning_icons.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the car care share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in CAR_CARE_SOURCES if s.key == "car_care_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="carcare-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
