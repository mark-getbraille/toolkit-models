"""Picture packs for SCIENCE YOU CAN USE (the owner's request of 2026-11-22). Used by build_packs.py in the same way as
its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with
more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit
counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise the instruments of
everyday science: weather instruments (rain gauges, anemometers, barometers, hygrometers, weather vanes), seismometers,
telescopes, microscopes, globes, planispheres, orreries and armillary spheres, and laboratory things (test tubes,
Bunsen burners, glassware, magnets).

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no reading, make or magnification is named. Telescope answers end with SUN_NOTE and Bunsen burner and
glassware answers with LAB_NOTE (the kit uses the same words in science_use_sources.py).

The packs (SCIENCE_PACKS):
  commons_science_instruments  Wikimedia Commons (CC0, public domain or CC BY files only): the instruments above.
  open_images_science          Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                               telescopes, microscopes, globes, rain gauges and barometers. No label is asked twice
                               (packs/test_leisure_packs.py checks).

Not repeated here: the sky, cloud and weather packs (commons_sky_weather, ccsn_clouds, weather_images), NASA and ESO
pictures, the chemistry and lab hazard packs, and the Commons categories and Open Images labels other packs ask.

    python packs/science_packs.py commons_science_instruments --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from homestead_packs import thing

SUN_NOTE = ("Never point a telescope, binoculars or a finder at the Sun without a certified solar filter over the "
            "front: it blinds instantly.")
LAB_NOTE = "Lab safety: wear eye protection, keep flames away from anything that burns, and never taste chemicals."

INSTRUMENTS = [
    thing("Rain gauges", "a rain gauge, which collects and measures rainfall"),
    thing("Anemometers", "an anemometer, which measures wind speed (often with spinning cups)", deeper=True),
    thing("Barometers", "a barometer, which measures air pressure (falling pressure often means stormy weather)"),
    thing("Hygrometers", "a hygrometer, which measures humidity"),
    thing("Weather vanes", "a weather vane, which turns to show where the wind comes from"),
    thing("Seismometers", "a seismometer, which records ground shaking from earthquakes"),
    thing("Telescopes", "a telescope", SUN_NOTE),
    thing("Microscopes", "a microscope"),
    thing("Globes", "a globe, a model of the Earth (or another world)"),
    thing("Planispheres", "a planisphere, a turning star chart that shows the sky for any date and time"),
    thing("Orreries", "an orrery, a model of the planets moving around the Sun", deeper=True),
    thing("Armillary spheres", "an armillary sphere, a model of the sky made of rings"),
    thing("Test tubes", "test tubes", LAB_NOTE),
    thing("Bunsen burners", "a Bunsen burner, a gas burner used in laboratories", LAB_NOTE),
    thing("Laboratory glassware", "laboratory glassware", LAB_NOTE),
    thing("Magnets", "a magnet", "Keep strong magnets away from pacemakers, cards and small children (swallowed "
                                 "magnets are dangerous)."),
]


def build_commons_science_instruments(limit):
    """The commons_science_instruments pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(INSTRUMENTS, limit, "scinstr")


SCIENCE_OI = [
    group("What science instruments are in this picture?",
          {"Telescope": "a telescope", "Microscope": "a microscope", "Globe": "a globe", "Rain gauge": "a rain gauge",
           "Barometer": "a barometer"}),
]


def build_open_images_science(limit):
    """open_images_science (see the module docstring); a "yes, there is a telescope" answer adds SUN_NOTE."""
    out = []
    for name, data, row in build_oi_gap("open_images_science", SCIENCE_OI, limit, 9404):
        if "telescope" in row.get("answer", "") and not row["answer"].startswith("No"):
            row = dict(row, answer=f"{row['answer']} {SUN_NOTE}")
        out.append((name, data, row))
    return out


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
SCIENCE_PACKS = {
    "commons_science_instruments": (build_commons_science_instruments, COMMONS_LICENCE.format(
        what="weather instrument, seismometer, telescope, microscope, globe, orrery and laboratory")),
    "open_images_science": (build_open_images_science, OI_LICENCE),
}
SCIENCE_LIMITS = {
    "commons_science_instruments": 900,   # 16 categories; Telescopes has most files
    "open_images_science": 500,           # 5 labels
}
SCIENCE_COMMONS_KEYS = ("commons_science_instruments",)
SCIENCE_SPECS = INSTRUMENTS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a science pack builder.")
    parser.add_argument("key", choices=sorted(SCIENCE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = SCIENCE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
