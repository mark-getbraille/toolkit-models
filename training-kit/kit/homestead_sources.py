"""HOMESTEADING AND SMALL LIVESTOCK for the Picture Model Training Kit (the owner's request of 2026-11-22). This file
lists:
  - the ready-made packs built in packs/homestead_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_homestead_poultry_bees, commons_homestead_farmstead and open_images_homestead;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (HOMESTEAD_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it (the packs from the kit's own release),
only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say, and end with the handling, hygiene, bee, water and power notes
that fit, the same words as the packs' (packs/test_homestead.py checks).

Picture-making (HOMESTEAD_PICTURE_MAKING_OK): only the Commons equipment collections (things); sources.py puts every
other key in NOT_FOR_PICTURE_MAKING (the Open Images photos and beekeepers show people).
Topics: the equipment is in the home topic (Home and household), the farm animals of Open Images in the nature topic.

    python -c "import sources, homestead_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/homestead_packs.py.
HANDLING_NOTE = ("Handling animals: move calmly and quietly, keep an escape route, and never step between a mother "
                 "animal and her young; be careful around bucks, rams, boars and roosters.")
POULTRY_NOTE = ("Hygiene: wash your hands with soap and water after touching poultry, eggs, feeders or pens "
                "(Salmonella); children under 5 should not handle chicks or ducklings.")
BEE_NOTE = ("Bees: wear a veil and use a smoker when opening a hive; anyone allergic to stings should keep their "
            "emergency medicine with them and not work bees alone. For trouble breathing after a sting, call 911.")
WELL_NOTE = ("Water: test well water every year for bacteria and nitrates; never climb into a well, cistern, septic "
             "tank or manure pit, where gases can kill in minutes.")
POWER_NOTE = "Power: solar, battery, inverter and generator wiring is work for a qualified electrician."

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


# Categories of packs/homestead_packs.py, the same answers (the share-alike entry needs no word filter for these).
HOMESTEAD_SA = [
    gear("Chicken tractors", "a chicken tractor, a movable coop without a floor that lets hens graze fresh ground",
         POULTRY_NOTE),
    gear("Nest boxes", "a nest box, where hens or other birds lay their eggs", POULTRY_NOTE, True),
    gear("Beehives", "a beehive", BEE_NOTE),
    gear("Langstroth hives", "a Langstroth hive, a stack of boxes holding removable frames of comb", BEE_NOTE),
    gear("Top-bar hives", "a top-bar hive, a long box whose comb hangs from bars across the top", BEE_NOTE),
    gear("Bee smokers", "a bee smoker, a can with bellows that puffs cool smoke to calm bees", BEE_NOTE),
    gear("Honey extractors", "a honey extractor, a drum that spins frames of comb to fling the honey out"),
    gear("Cattle crushes", "a cattle crush (squeeze chute), a strong stall that holds an animal still for care",
         HANDLING_NOTE),
    gear("Water wells", "a water well", WELL_NOTE),
    gear("Composting toilets", "a composting toilet, which turns waste into compost without water", deeper=True),
    gear("Butter churns", "a butter churn, which shakes or beats cream until it turns into butter"),
    gear("Cream separators", "a cream separator, which spins milk to separate the cream"),
]


def prepare_homestead_commons_sa(source, data_dir, work, cap):
    """Commons homestead categories (poultry, bees, livestock handling, wells, dairy tools), files under CC BY-SA or
    GFDL."""
    items = commons_sa_items(HOMESTEAD_SA, cap, source.test, "homestead-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


HOMESTEAD_SOURCES = [
    Source("commons_homestead_poultry_bees", "Homestead poultry and bees: chicken tractors, nest boxes, duck houses, "
                                             "beehives, bee smokers, hive tools, honey extractors and honeycomb, with "
                                             "hygiene and bee sting notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("commons_homestead_farmstead", "The farmstead: cattle crushes, sheep pens, fences, wells, rainwater tanks, "
                                          "root cellars, off-grid homes, composting toilets, butter churns and cream "
                                          "separators (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("open_images_homestead", "Farm animals, beekeeping, barns, silos, coops, pastures, water wells, solar panels "
                                    "and wind turbines (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("homestead_commons_sa", "Wikimedia Commons: chicken tractors, nest boxes, beehives, smokers, honey "
                                   "extractors, cattle crushes, wells, composting toilets, butter churns and cream "
                                   "separators, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 10, prepare_homestead_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons equipment (things), never Open Images (people).
HOMESTEAD_PICTURE_MAKING_OK = {"commons_homestead_poultry_bees", "commons_homestead_farmstead", "homestead_commons_sa"}

HOMESTEAD_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Chicken coops, Egg cartons, Sheep shearing, Rabbit hutches, "
        "Hay bales, Electric fences, Ear tags, Hand pumps, Septic tanks, Fence posts and the chicken and duck breed "
        "categories (commons_breeds and the farm packs): not asked twice.",
    "Commons categories that do not exist or hold almost no files (November 2026)": "Egg incubators, Brooders, Egg "
        "candling, Poultry drinkers, Goat milking, Milking stands, Pigsties, Livestock trailers, Feed troughs, Hoof "
        "trimming, Windpumps, Woven wire fences, Goat sheds and Poultry feeders (3 files); the packs use Incubators "
        "(poultry), Incubators (eggs), Candling, Milking by hand and Wind pumps instead.",
    "Breed identification": "Chicken, duck, goat, sheep, rabbit and pig breeds are the breeds packs' (commons_breeds, "
                            "na_domestic_animals); this collection names equipment and the kind of animal only.",
    "USDA ARS and APHIS photo galleries": "www.aphis.usda.gov refused programs and the ARS image gallery has no "
                                          "listing a program can read by subject (2026-11-22); their public-domain "
                                          "photos copied to Commons are reached through the Commons categories.",
    "Extension and beekeeping club photos": "Each university's or club's copyright; not used.",
    "Roboflow Universe chicken, egg and bee sets": "Roboflow Universe's robots.txt disallows the dataset download "
                                                   "pages (see gaps_sources.py).",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the homestead share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in HOMESTEAD_SOURCES if s.key == "homestead_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="homestead-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
