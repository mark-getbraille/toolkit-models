"""CLOTHING AND PERSONAL CARE for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/clothing_packs.py (group "permissive"; the kit downloads them with
    prepare_pack);
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (CLOTHING_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it, only when the user ticks the matching
choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say: colours and patterns are named only when the label names them.
No swimwear or underwear category is asked, and Open Images photos with such a label are left out whoever is in them.

Picture-making (CLOTHING_PICTURE_MAKING_OK): none; clothes are photographed on people (sources.py puts every key in
NOT_FOR_PICTURE_MAKING).
Topics: in the home topic (Home and household).

    python -c "import sources, clothing_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# No safety notes: clothing answers name the garment or pattern only.

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


# Categories of packs/clothing_packs.py, the same answers.
CLOTHING_SA = [
    ("Blazers", "What clothing or accessory is this?", "This is a blazer, a tailored jacket.", False),
    ("Coats", "What clothing or accessory is this?", "This is a coat.", False),
    ("Waistcoats", "What clothing or accessory is this?", "This is a waistcoat (vest), a sleeveless garment worn "
                                                          "over a shirt.", False),
    ("Hats", "What clothing or accessory is this?", "This is a hat.", False),
    ("Argyle", "What pattern is this?", "This is an argyle pattern: diamonds in a diagonal checkerboard, often with "
                                        "thin crossing lines.", False),
    ("Stripes", "What pattern is this?", "This is a striped pattern.", False),
]


def prepare_clothing_commons_sa(source, data_dir, work, cap):
    """Commons blazer, coat, waistcoat, hat, argyle and stripe categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(CLOTHING_SA, cap, source.test, "clothing-commons-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


CLOTHING_SOURCES = [
    Source("commons_clothing_more", "Clothes: blazers, coats, blouses, waistcoats, hats, belts, loafers, Oxford shoes and slippers, and argyle and striped patterns (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("open_images_clothing", "What people wear: shirts, skirts, suits, caps, hoodies, uniforms, formal wear, kimonos, saris, turbans and hijabs, sneakers and bags, and tartan, plaid, polka dot, camouflage and floral patterns (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2000, 20, prepare_pack, "about 400 MB"),
    Source("clothing_commons_sa", "Wikimedia Commons: blazers, coats, waistcoats, hats, and argyle and striped patterns, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 400, 10, prepare_clothing_commons_sa, "about 100 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# Clothes are shown on people: no collection here is for picture-making.
CLOTHING_PICTURE_MAKING_OK = set()

CLOTHING_NOT_INCLUDED = {
    "Collections that exist": "fashionpedia (garments and their patterns, CC BY labels), clothing (Grigorev, CC0), "
        "commons_personal (makeup and grooming), commons_hairstyles_sa, the jewellery and fabric packs, met_collection "
        "(the Costume Institute) and cooper_hewitt: not repeated.",
    "DeepFashion and DeepFashion2": "A signed agreement for non-commercial research only: the sign-up collection "
        "deepfashion (signup_sources.py), personal use.",
    "Fashionpedia's other photos": "Its labels are CC BY 4.0 but its photos are the Flickr authors'; the fashionpedia "
        "pack keeps only CC BY and public-domain photos. Photos under other licences are research use only and are "
        "not added here.",
    "Open Beauty Facts": "Its robots.txt blocks AI crawlers: left out (as the kit's openbeautyfacts note says).",
    "Swimwear and underwear": "Not asked, by the owner's rule; Open Images photos with those labels are left out.",
    "Commons categories already used by other packs": "T-shirts, Jeans, Dresses, Skirts, Neckties, Bow ties, Hoodies, "
        "Sweaters, Cardigans, Jackets, Raincoats, Shorts, Trousers, Polo shirts, Dress shirts, Scarves, Gloves, "
        "Baseball caps, Socks, Handbags, Wallets, Sunglasses, Boots, Sandals, Polka dots, Floral patterns, "
        "Houndstooth, Gingham, Camouflage patterns, Striped clothing, Combs, Hairbrushes, Razors and makeup.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the clothing and personal care share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in CLOTHING_SOURCES if s.key == "clothing_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="clothing-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
