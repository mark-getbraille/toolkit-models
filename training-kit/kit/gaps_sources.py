"""THE PICTURE CATEGORY GAPS for the Picture Model Training Kit: the collection that cannot be a ready-made pack
because of its licence, and the sources the November 2026 inventory of picture categories pointed to that were looked
at and left out, with the reason. The open ones are packs: packs/gaps_oi_packs.py (Open Images: washroom fixtures,
baby furniture, luggage, carts and bins, pools, office and exercise things, outings and rides, more foods and drinks,
cards and papers) and packs/gaps_collection_packs.py (the Art Institute of Chicago and Cleveland museums, the
WordPress Photo Directory, Library of Congress maps, Europeana fashion and archaeology, CDC PHIL health behaviours
and algae blooms, Commons rocks, minerals, fossils and NARA aerial photographs).

As in chemical_sources.py, nothing here is re-shared by the kit's makers: the collection is downloaded by the kit on
the user's own computer, straight from Wikimedia Commons, only when the user ticks the share-alike choice. Every
licence was checked at its source in November 2026.

The collection (GAPS_SOURCES):
  share-alike
    gaps_rocks_commons_sa  Wikimedia Commons files under CC BY-SA or GFDL of the rocks, minerals and fossils pack's
                           categories (quartz, pyrite, granite, obsidian, ammonites, trilobites, petrified wood ...).
                           Captions CC0.

Looked at and not included (GAPS_NOT_INCLUDED, with the reason) and ideas for later packs (GAPS_CANDIDATES).

    python -c "import sources, gaps_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source


def spec(category, thing, deeper=True):
    """(category, question, answer, also one level of its subcategories) for home_sources.commons_sa_items."""
    return (category, "What is this?", f"This is {thing}.", deeper)


GAPS_ROCKS_SA = [
    spec("Quartz", "quartz, a common mineral"), spec("Amethyst", "amethyst, a purple kind of quartz"),
    spec("Pyrite", "pyrite (fool's gold), a brassy yellow mineral"), spec("Calcite", "calcite, a common mineral"),
    spec("Fluorite", "fluorite, a mineral that grows in cubes"), spec("Malachite", "malachite, a green copper mineral"),
    spec("Gemstones", "a gemstone"), spec("Meteorites", "a meteorite, a rock that fell from space"),
    spec("Granite", "granite, an igneous rock"), spec("Basalt", "basalt, a dark volcanic rock"),
    spec("Obsidian", "obsidian, natural volcanic glass"), spec("Sandstone", "sandstone, a sedimentary rock"),
    spec("Limestone", "limestone, a sedimentary rock"), spec("Fossils", "a fossil"),
    spec("Ammonite fossils", "an ammonite fossil"), spec("Trilobite fossils", "a trilobite fossil"),
    spec("Petrified wood", "petrified wood: wood turned to stone"), spec("Amber", "amber, fossil tree resin"),
]


def prepare_gaps_rocks_commons_sa(source, data_dir, work, cap):
    """Commons rocks, minerals and fossils categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(GAPS_ROCKS_SA, cap, source.test, "rocks-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
GAPS_SOURCES = [
    Source("gaps_rocks_commons_sa", "Wikimedia Commons: minerals, gemstones, meteorites, rocks and fossils by name, "
                                    "files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 800, 10, prepare_gaps_rocks_commons_sa, "about 180 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
]

# The collections a picture-making model may learn from: the rocks and fossils (no people).
GAPS_PICTURE_MAKING_OK = {"gaps_rocks_commons_sa"}

GAPS_CANDIDATES = {
    "Other open museums: Walters Art Museum (CC0), Brooklyn Museum, Museums Victoria and Auckland Museum (CC BY items)":
        "open, with good records; not built in this pass (two general museums were). Museums Victoria is already a "
        "personal-use collection of the kit (museums_victoria) for its non-commercial items.",
    "Visible jobs and roles (teacher, referee, dancer, drummer, clown) from Open Images people labels":
        "possible, but the labels judge people by role; left for a pass with its own people rules.",
}

GAPS_NOT_INCLUDED = {
    "LVIS (urinal, crib, highchair, awning, telephone pole, dumpster, condiments, kitchen tools)":
        "its annotations are CC BY 4.0, but the only official download host (dl.fbaipublicfiles.com) disallows all "
        "robots in its robots.txt, so it is not downloaded. The same kinds of things come from Open Images instead.",
    "Objects365":
        "an idea list only: its photos come without their own open licence.",
    "ImageNet-21k":
        "an idea list only: its photos are not openly licensed.",
    "Nappy (nappy.co, CC0 photos of Black and brown people)":
        "the photos are CC0, but the site's terms forbid robots, scrapers and other automated access, and ask that "
        "the photos not be reposted elsewhere; its Openverse copies are behind Openverse's robots block. Not "
        "downloaded. A person may still choose photos there by hand for their own use.",
    "Roboflow 100 sets (washroom, wine labels, fish market and others, CC BY 4.0)":
        "Roboflow Universe's robots.txt disallows the dataset download and export pages, and its API needs an "
        "account key. Not downloaded.",
    "Smithsonian NMNH minerals and fossils, and National Postal Museum stamps":
        "the records are CC0, but every Smithsonian picture is served by ids.si.edu, whose robots.txt disallows all "
        "robots. Rocks, minerals and fossils come from Wikimedia Commons instead (commons_rocks_fossils); US and "
        "Canadian stamps are already in commons_mail_parcels.",
    "NARA catalogue (aerial, agricultural, wildlife and occupation photo series)":
        "the catalogue blocks this program's robots; the aerial photographs come from their Wikimedia Commons copies "
        "(commons_nara_aerial).",
    "NASA Image and Video Library (planets, rockets, astronauts)":
        "already the kit's nasa collection.",
    "Body parts in photos (Open Images 'Human arm', 'Human ear' ...)":
        "people photos whose labels say only that an arm or an ear is in the picture; left out.",
    "Openverse and DPLA":
        "their robots.txt blocks this program; the sources they gather are read directly where they allow it.",
    "Kaggle datasets":
        "sign-in needed for every download.",
}


def main(argv=None):
    """Prepare the collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the gaps share-alike collection.")
    parser.add_argument("key", choices=[s.key for s in GAPS_SOURCES])
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in GAPS_SOURCES if s.key == args.key)
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="gaps-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
