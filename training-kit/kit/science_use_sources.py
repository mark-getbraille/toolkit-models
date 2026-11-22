"""SCIENCE YOU CAN USE for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/science_packs.py (group "permissive"; the kit downloads them with
    prepare_pack);
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (SCIENCE_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it, only when the user ticks the matching
choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (no reading, make or magnification), and telescope and lab
answers end with SUN_NOTE and LAB_NOTE, the same words as the packs' (packs/test_leisure_packs.py checks).

Picture-making (SCIENCE_PICTURE_MAKING_OK): the Commons instruments (things); sources.py puts every other key in
NOT_FOR_PICTURE_MAKING.
Topics: in the nature topic (with the weather and sky collections).

    python -c "import sources, science_use_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The notes, word for word as in packs/science_packs.py.
SUN_NOTE = ("Never point a telescope, binoculars or a finder at the Sun without a certified solar filter over the "
            "front: it blinds instantly.")
LAB_NOTE = "Lab safety: wear eye protection, keep flames away from anything that burns, and never taste chemicals."

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


# Categories of packs/science_packs.py, the same answers.
SCIENCE_SA = [
    gear("Rain gauges", "a rain gauge, which collects and measures rainfall"),
    gear("Barometers", "a barometer, which measures air pressure (falling pressure often means stormy weather)"),
    gear("Weather vanes", "a weather vane, which turns to show where the wind comes from"),
    gear("Telescopes", "a telescope", SUN_NOTE),
    gear("Microscopes", "a microscope"),
    gear("Globes", "a globe, a model of the Earth (or another world)"),
    gear("Bunsen burners", "a Bunsen burner, a gas burner used in laboratories", LAB_NOTE),
]


def prepare_science_commons_sa(source, data_dir, work, cap):
    """Commons weather instrument, telescope, microscope, globe and Bunsen burner categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(SCIENCE_SA, cap, source.test, "science-commons-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SCIENCE_SOURCES = [
    Source("commons_science_instruments", "Science instruments: rain gauges, anemometers, barometers, hygrometers, weather vanes, seismometers, telescopes, microscopes, globes, planispheres, orreries and lab glassware (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("open_images_science", "Telescopes, microscopes, globes, rain gauges and barometers (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 500, 5, prepare_pack, "about 110 MB"),
    Source("science_commons_sa", "Wikimedia Commons: rain gauges, barometers, weather vanes, telescopes, microscopes, globes and Bunsen burners, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 400, 10, prepare_science_commons_sa, "about 100 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons instruments (things).
SCIENCE_PICTURE_MAKING_OK = {"commons_science_instruments", "science_commons_sa"}

SCIENCE_NOT_INCLUDED = {
    "Weather, sky and space pictures": "Already their own collections (commons_sky_weather, ccsn_clouds, "
        "weather_images, earth_observatory, the kit's nasa); this collection names instruments only.",
    "Commons categories that do not exist (November 2026)": "Amateur telescopes, Optical microscopes, Stevenson "
        "screens and Periodic tables; Beakers and Prisms hold no files.",
    "NOAA and NASA photo libraries": "Their public-domain photos copied to Commons are reached through the Commons "
        "categories; the NOAA Photo Library refused programs earlier (gaps_sources.py).",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the science you can use share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in SCIENCE_SOURCES if s.key == "science_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="science_-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
