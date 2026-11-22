"""PERSONAL CARE AND BEAUTY PRODUCTS for the Picture Model Training Kit (the owner's request of 2026-11-22). This
file lists:
  - the ready-made packs built in packs/personal_care_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_personal_care_products, commons_historic_cosmetics, met_historic_cosmetics and
    open_images_personal_care;
  - the share-alike Commons files of the plainest product categories (group "share-alike": only with the
    share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (PERSONAL_CARE_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, only when the user ticks the matching choice. Every licence was checked at its source
in November 2026.

Answers say only what the source's own labels say, with the safety notes of the US Food and Drug Administration's
public-domain cosmetics pages and Poison Help (the same words as the packs; packs/test_gaps_pictures.py checks).
Products only: files whose words name a person (or a child) and Open Images photos with a confirmed face, person or
child are left out. Oral care is linked to the dental packs (commons_dental_care), feminine care to
commons_contraception_menstrual, and hairstyles to commons_hairstyles and commons_hairstyles_sa.

Picture-making: none of these keys (sources.py puts them all in NOT_FOR_PICTURE_MAKING): a picture-making model need
not learn branded packaging. Topic: "home" (Home and household).

    python -c "import sources, personal_care_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/personal_care_packs.py.
COSMETIC_NOTE = ("Cosmetics safety (FDA): stop using a product that gives you a rash, redness, itching or swelling; "
                 "never share eye makeup; throw away a product whose colour or smell has changed.")
HAIR_DYE_NOTE = ("Hair dye (FDA): do the skin patch test the label describes before every use, follow the "
                 "directions, and never use hair dye on eyebrows or eyelashes: it can hurt the eyes and even blind.")
FLAME_NOTE = ("Fire: sprays, perfumes and nail polish remover can catch fire: keep them away from flames, cigarettes "
              "and heat.")
BLADE_NOTE = "Sharp blades: handle by the handle, and throw used blades away in a closed container."
POISON_NOTE = ("Keep cosmetics, perfume, mouthwash and nail products out of children's reach; if one is swallowed, "
               "call Poison Help at 1-800-222-1222.")

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


def product(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# Product categories of packs/personal_care_packs.py whose files are things on their own (no word filter is needed;
# files whose words name a child are left out all the same).
PERSONAL_CARE_SA = [
    product("Hair dyes", "hair dye", f"{HAIR_DYE_NOTE} {POISON_NOTE}", True),
    product("Hair rollers", "hair rollers (curlers)"),
    product("Straight razors", "a straight razor", BLADE_NOTE, True),
    product("Shaving soap", "shaving soap", "", True),
    product("Razor blades", "razor blades", BLADE_NOTE, True),
    product("Perfumes", "perfume", f"{FLAME_NOTE} {POISON_NOTE}", True),
    product("Toothpaste tubes", "a tube of toothpaste", POISON_NOTE),
    product("Nail scissors", "nail scissors", BLADE_NOTE),
    product("Bath bombs", "a bath bomb", COSMETIC_NOTE),
]


def prepare_personal_care_commons_sa(source, data_dir, work, cap):
    """Commons personal care product categories, files under CC BY-SA or GFDL, none whose words name a child."""
    items = commons_sa_items(PERSONAL_CARE_SA, cap, source.test, "pcare-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


PERSONAL_CARE_SOURCES = [
    Source("commons_personal_care_products", "Personal care products: kohl, bronzer, false eyelashes, nail art, skin "
                                             "care, petroleum jelly, bath bombs and salts, hair gel, wax, dyes, "
                                             "rollers, pins and ties, straight razors, shaving brushes and soap, "
                                             "perfumes and colognes, with FDA safety notes (Wikimedia Commons, "
                                             "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 10, prepare_pack, "about 250 MB"),
    Source("commons_historic_cosmetics", "Historic cosmetics: ancient Egyptian cosmetics, unguentaria, aryballoi, "
                                         "alabastra and perfume burners (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    Source("met_historic_cosmetics", "Historic cosmetics at the Met: kohl tubes, cosmetic boxes and jars, perfume and "
                                     "scent bottles, answered from the museum's records (ready-made pack)",
           MET_OPEN, MET_CREDIT, "permissive", 600, 5, prepare_pack, "about 150 MB"),
    Source("open_images_personal_care", "Lip gloss, face powder, makeup brushes and mirrors, nail care, hair ties "
                                        "and irons, shavers, shaving cream, soaps, lotion, shampoo and sunscreen; "
                                        "photos of faces left out (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("personal_care_commons_sa", "Wikimedia Commons: hair dyes, hair rollers, straight razors, shaving soap, "
                                       "razor blades, perfumes, toothpaste tubes, nail scissors and bath bombs, files "
                                       "under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 400, 5, prepare_personal_care_commons_sa,
           "about 90 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# No key of this file is for picture-making (see the module docstring).
PERSONAL_CARE_PICTURE_MAKING_OK = set()

PERSONAL_CARE_NOT_INCLUDED = {
    "Open Beauty Facts": "its site blocks AI crawlers (robots.txt), so the kit's openbeautyfacts collection is not "
                         "built and nothing is read from it.",
    "Commons categories already used by other packs": "Shampoo, Hair conditioners, Toothpaste, Deodorants, Shower "
        "gels, Soap bars, Liquid soap, Sunscreen, Lipsticks, Mascara, Nail polish, Face powder, Hairbrushes, Razors "
        "(commons_personal), Cosmetics, Eye shadow, Foundation, Concealer, Lip gloss, Lip balm, Makeup brushes, Nail "
        "files, Combs, Curling irons, Electric shavers, Shaving cream, Safety razors, Tweezers, Cotton swabs, Hair "
        "clips, Toothbrushes, Dental floss, Mouthwash (commons_makeup_grooming), Hairdryers, Hair irons and Hair "
        "clippers (other packs), Interdental brushes, Oral irrigators and Tongue scrapers (commons_dental_care), "
        "Tampons and Menstrual cups (commons_contraception_menstrual): not asked twice.",
    "Commons categories that do not exist under the names tried (November 2026)": "Eyeshadow palettes, Makeup "
        "palettes, Blush, Eyeliners, Eyebrow pencils, Lip liners, Powder compacts, Cosmetic packaging, Moisturizers, "
        "Lotions, Hand creams, Face creams, Cold cream, Facial masks, Hair dryers, Antiperspirants, Deodorant sticks, "
        "Aftershave, Disposable razors, Shaving kits, Nail clippers, Cuticle pushers, Manicure sets, Face wash, "
        "Makeup removers, Sanitary pads and Panty liners; Hair straighteners and Perfume bottles exist but hold no "
        "files. Commons \"Flat irons\" is about clothes irons, \"Atomizers\" about medical ones, \"Headbands\" "
        "shows people wearing them, and \"Baby powder\" files would all be left out by the child rule.",
    "Open Images labels asked elsewhere or about people": "Cosmetics, Lipstick, Eye shadow, Mascara, Nail polish, "
        "Perfume, Deodorant, Comb, Hair dryer, Razor, Toothbrush, Toothpaste, Mouthwash, Dental floss, Manicure, "
        "Wig, Hairbrush, Tweezers and Cotton swab are asked by other packs; Eyelash, Hair coloring, Hair care, Lace "
        "wig and Beauty salon are photos of people, and Hair gel, Tampon and Foundation (makeup) have almost no "
        "checked photos (counted 2026-11-22).",
    "FDA cosmetics photos and makers' product photos": "the FDA's pages are built as a book (the reference library's "
        "personal-care word); the makers' product photos (L'Oreal, Estee Lauder, Procter & Gamble, Unilever, "
        "Conair, Philips) are their copyright: not used.",
    "Smithsonian and Cooper Hewitt cosmetics": "api.si.edu refused automated requests (service_packs.py notes); "
        "the Met's CC0 records are used instead.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the personal care share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PERSONAL_CARE_SOURCES if s.key == "personal_care_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="pcare-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
