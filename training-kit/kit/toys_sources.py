"""TOYS AND CHILDREN'S PRODUCTS for the Picture Model Training Kit (the owner's request of 2026-11-22). This file
lists:
  - the ready-made packs built in packs/toys_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_toys_by_type, commons_ride_ons_playgrounds, commons_nursery_more, commons_museum_toys,
    met_toys and open_images_toys;
  - the share-alike Commons files of the toy categories (group "share-alike": only with the share-alike choice,
    --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (TOYS_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, only when the user ticks the matching choice. Every licence was checked at its source
in November 2026.

Products only, never a child in the photo: Commons files whose words name a child or say someone is playing are left
out, and Open Images photos with a confirmed child, person or face. Answers say only what the source's own labels
say, with the US Consumer Product Safety Commission's published advice as safety notes (the same words as the packs;
packs/test_gaps_pictures.py checks): small parts and choking, magnets, button batteries, riding toys, playgrounds,
baby walkers and recalls. cpsc.gov refuses programs, so its pages are links only; the reference library's
parent:cpsc_child_safety and the recall books (recalls:*) and the kit's cpsc_recalls hold the rest.

Picture-making: none of these keys (sources.py puts them all in NOT_FOR_PICTURE_MAKING): children's products are
kept to describing. Topic: "home" (Home and household).

    python -c "import sources, toys_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/toys_packs.py.
SMALL_PARTS_NOTE = ("Choking (CPSC): toys with small parts are not for children under 3; follow the age on the "
                    "label, and keep small balls, marbles and balloons away from young children.")
MAGNET_NOTE = ("Magnets (CPSC): strong magnets that are swallowed can pull together inside the body and cause "
               "serious harm: get emergency medical care at once.")
BATTERY_NOTE = ("Button batteries (CPSC): keep battery doors screwed shut and spare batteries out of reach; a "
                "swallowed button or coin battery can burn the throat in as little as two hours: go to the emergency "
                "room at once.")
RIDE_NOTE = ("Riding toys (CPSC): wear a helmet, and keep riding toys away from cars, streets, stairs and swimming "
             "pools.")
RECALL_NOTE = "Recalls: check SaferProducts.gov for recalls, and register the product with its maker."
TOY_NOTES = f"{SMALL_PARTS_NOTE} {RECALL_NOTE}"

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
MET_OPEN = "CC0 (The Metropolitan Museum of Art Open Access, each object's isPublicDomain checked)"
MET_CREDIT = "The Metropolitan Museum of Art, https://www.metmuseum.org (each object credited in CREDITS.txt)"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def toy(category, words, notes=TOY_NOTES, deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# Toy categories of packs/toys_packs.py that hold things on their own; files whose words name a child are left out.
TOYS_SA = [
    toy("Toy vehicles", "a toy vehicle", deeper=True),
    toy("Toy robots", "a toy robot", f"{SMALL_PARTS_NOTE} {BATTERY_NOTE} {RECALL_NOTE}", True),
    toy("Wooden blocks", "wooden blocks", deeper=True),
    toy("Dollhouses", "a dollhouse", deeper=True),
    toy("Tin toys", "a tin toy (a toy made of metal sheet)", deeper=True),
    toy("Kaleidoscopes", "a kaleidoscope: you look through it and turn it to see coloured patterns", deeper=True),
    toy("Rocking horses", "a rocking horse", RECALL_NOTE, True),
    toy("Pedal cars", "a pedal car", f"{RIDE_NOTE} {RECALL_NOTE}", True),
    toy("Toy pianos", "a toy piano", deeper=True),
]


def prepare_toys_commons_sa(source, data_dir, work, cap):
    """Commons toy categories, files under CC BY-SA or GFDL, none whose words name a child."""
    items = commons_sa_items(TOYS_SA, cap, source.test, "toys-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


TOYS_SOURCES = [
    Source("commons_toys_by_type", "Toys by type: toy vehicles, blocks, rag and Barbie dolls, dollhouses, plush "
                                   "toys, tin and wind-up toys, kaleidoscopes, puppets, construction sets, wooden "
                                   "puzzles, pull toys and educational toys, with CPSC safety notes; no children "
                                   "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("commons_ride_ons_playgrounds", "Ride-on toys and play equipment: rocking horses, tricycles, wagons, "
                                           "pedal cars, slides, swings, seesaws, jungle gyms and sandboxes, with "
                                           "CPSC safety notes; no children (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 10, prepare_pack, "about 280 MB"),
    Source("commons_nursery_more", "More nursery items: baby walkers, changing tables, cradles, diapers, diaper bags "
                                   "and toy chests, with CPSC notes; no babies in the photos (Wikimedia Commons, "
                                   "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    Source("commons_museum_toys", "Antique toys and toys in museums (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    Source("met_toys", "Toys at the Met: dolls, toys, rattles, tops and marbles, answered from the museum's records "
                       "(ready-made pack)",
           MET_OPEN, MET_CREDIT, "permissive", 500, 5, prepare_pack, "about 120 MB"),
    Source("open_images_toys", "LEGO and construction sets, toy vehicles, action and animal figures, dolls, plush, "
                               "baby and bath toys, puppets, dollhouses, educational toys, marbles, kaleidoscopes "
                               "and nursery furniture; photos with children left out (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2500, 20, prepare_pack, "about 500 MB"),
    Source("toys_commons_sa", "Wikimedia Commons: toy vehicles and robots, wooden blocks, dollhouses, tin toys, "
                              "kaleidoscopes, rocking horses, pedal cars and toy pianos, files under CC BY-SA or GFDL "
                              "(share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 5, prepare_toys_commons_sa,
           "about 110 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# No key of this file is for picture-making (see the module docstring).
TOYS_PICTURE_MAKING_OK = set()

TOYS_NOT_INCLUDED = {
    "CPSC toy safety pages, recalls and photos": "www.cpsc.gov refuses programs (403, robots.txt included, "
        "22 November 2026): its advice is said in the safety notes as the CPSC's, its pages are links only (the "
        "reference library's toys word lists them), and recalls are in the library's recall books and the kit's "
        "cpsc_recalls.",
    "Smithsonian toy collections (National Museum of American History)": "CC0 where marked, but api.si.edu "
        "refused automated requests (service_packs.py notes); not used.",
    "The Strong National Museum of Play": "no open licence was found for its online collection images (checked "
        "22 November 2026); link-only: https://www.museumofplay.org/",
    "V&A Museum of Childhood (Young V&A)": "the V&A's collection images are for non-commercial use only (the kit's "
        "vam collection, personal use); its toys come through vam when that box is ticked.",
    "Commons categories already used by other packs": "Teddy bears, Stuffed toys, Dolls, Action figures, Toy "
        "trains, Lego, Building blocks, Jigsaw puzzles, Rubik's Cube, Yo-yos, Kites, Spinning tops, Board games, "
        "Dice, Dominoes (commons_toys_sports_music), Wooden toys, Fidget spinners and Fidget toys (the games "
        "packs), and the baby products pack's bottles, car seats, cribs, high chairs, playpens, monitors, "
        "pacifiers and teething rings: not asked twice.",
    "Commons categories that do not exist or are left out": "Toy cars, Model cars, Balance bikes, Climbing frames, "
        "Swing sets, Sandpits, Matryoshka dolls, Marbles (toys), Tops (toys), Toy airplanes, Model trains, Night "
        "lights and Nappies do not exist or hold no files (November 2026); Puppets and Marionettes are mostly "
        "puppet shows with people, Soap bubbles shows people blowing them, and Commons \"Marbles\" mixes toy "
        "marbles with marble stone, so they are left out.",
    "Sports equipment": "another collection (the sports packs), not repeated here.",
    "Open Images labels asked elsewhere or about children": "Toy, Doll, Teddy bear, Stuffed toy, Toy block, "
        "Jigsaw puzzle, Kite, Playground, Playground slide, Tricycle, Kick scooter, Baby rattle, Infant bed and "
        "Diaper are asked by other packs; Figurine is mostly ornaments; photos with Child, Boy, Girl, Baby, Toddler "
        "or a person confirmed are left out of open_images_toys.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the toys share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in TOYS_SOURCES if s.key == "toys_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="toys-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
