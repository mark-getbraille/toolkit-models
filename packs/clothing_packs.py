"""Picture packs for CLOTHING AND PERSONAL CARE (the owner's request of 2026-11-22). Used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a
picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same
picture. The limit counts pictures.

Why: the owner is blind and wants the picture describer to say what clothes, shoes and accessories are in a picture,
and the patterns of fabrics (tartan and plaid, polka dots, camouflage, floral, argyle, stripes), to help with choosing
and matching outfits.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed): colours
and patterns are named only when the label itself names them, never guessed. People in these photos are adults or
children in everyday clothes; no swimwear or underwear category is asked, and Open Images photos with a swimwear,
bikini, swim briefs, underwear, lingerie or brassiere label confirmed are left out whoever is in them
(NO_SWIMWEAR, added to gaps_oi_packs' own exclusions while this pack is built).

The packs (CLOTHING_PACKS):
  commons_clothing_more    Wikimedia Commons (CC0, public domain or CC BY files only): blazers, coats, blouses,
                           waistcoats, hats, belts, loafers, Oxford shoes and slippers, and the argyle and striped
                           patterns.
  open_images_clothing     Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                           clothing (shirts, T-shirts, skirts, suits, bow ties, baseball caps, blazers, cardigans,
                           hoodies, shorts, vests, ponchos, aprons, jerseys, sportswear, uniforms, formal wear, wedding
                           dresses, kimonos, saris, turbans, hijabs, headbands), shoes and accessories (sneakers,
                           flip-flops, clutch bags, duffel and tote bags, cufflinks, pocket watches, hair and fashion
                           accessories), eye shadow, and the tartan, plaid, polka dot, camouflage and floral patterns.
                           No label is asked twice (packs/test_leisure_packs.py checks).

Not repeated here: the clothing packs that exist (fashionpedia: garments and their patterns; clothing: Grigorev's
CC0 set; commons_us_streets), the hairstyles (commons_hairstyles_sa and the hair packs), makeup and grooming
(commons_personal: lipstick, mascara, nail polish, razors, combs, hairbrushes), jewellery (commons_jewellery_beading,
museum_jewellery), fabrics (commons_fabrics_fibres), the Met's Costume Institute (met_collection) and Cooper Hewitt,
the Commons clothing categories other packs ask (T-shirts, Jeans, Dresses, Skirts, Neckties, Hoodies, Sweaters,
Jackets, Socks, Handbags, Sunglasses, Boots, Sandals, Polka dots, Floral patterns, Houndstooth, Gingham, Camouflage
patterns and others) and the Open Images labels other packs ask (Dress, Jeans, Hat, Coat, Jacket, Footwear, Handbag,
Sunglasses, Necklace and others).

    python packs/clothing_packs.py commons_clothing_more --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
import gaps_oi_packs as g
from gaps_oi_packs import group, build_oi_gap, QUICK

ASK_WEAR = "What clothing or accessory is this?"
ASK_PATTERN = "What pattern is this?"


def wear(category, words, deeper=False):
    """A Commons spec: (category, deeper, [("What clothing or accessory is this?", "This is <words>.")])."""
    return (category, deeper, [(ASK_WEAR, f"This is {words}.")])


def pattern(category, words, deeper=False):
    """A Commons spec: (category, deeper, [("What pattern is this?", "This is <words>.")])."""
    return (category, deeper, [(ASK_PATTERN, f"This is {words}.")])


CLOTHING = [
    wear("Blazers", "a blazer, a tailored jacket"),
    wear("Coats", "a coat"),
    wear("Blouses", "a blouse"),
    wear("Waistcoats", "a waistcoat (vest), a sleeveless garment worn over a shirt"),
    wear("Hats", "a hat"),
    wear("Belts", "a belt"),
    wear("Loafers", "a pair of loafers, slip-on shoes without laces", True),
    wear("Oxford shoes", "Oxford shoes, laced shoes whose eyelet tabs are sewn under the front"),
    wear("Slippers", "slippers"),
    pattern("Argyle", "an argyle pattern: diamonds in a diagonal checkerboard, often with thin crossing lines"),
    pattern("Stripes", "a striped pattern"),
]


def build_commons_clothing_more(limit):
    """The commons_clothing_more pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CLOTHING, limit, "clothmore")


CLOTHING_OI = [
    group("What clothes is this person wearing?",
          {"Shirt": "a shirt", "T-shirt": "a T-shirt", "Skirt": "a skirt", "Suit": "a suit", "Bow tie": "a bow tie",
           "Baseball cap": "a baseball cap", "Blazer": "a blazer", "Cardigan": "a cardigan", "Hoodie": "a hoodie",
           "Shorts": "shorts", "Vest": "a vest", "Poncho": "a poncho", "Apron": "an apron", "Jersey": "a jersey",
           "Sportswear": "sportswear", "Uniform": "a uniform", "Formal wear": "formal wear",
           "Wedding dress": "a wedding dress", "Kimono": "a kimono", "Sari": "a sari", "Turban": "a turban",
           "Hijab": "a hijab", "Headband": "a headband"}),
    group("What shoes or accessories are in this picture?",
          {"Sneakers": "sneakers", "Flip-flops": "flip-flops", "Clutch": "a clutch bag", "Duffel bag": "a duffel bag",
           "Tote bag": "a tote bag", "Cufflink": "cufflinks", "Pocket watch": "a pocket watch",
           "Hair accessory": "a hair accessory", "Fashion accessory": "a fashion accessory",
           "Eye shadow": "eye shadow"}),
    group("What pattern is on the clothes or fabric here?",
          {"Tartan": "tartan", "Plaid": "plaid", "Polka dot": "polka dots", "Camouflage": "camouflage",
           "Floral design": "a floral design"}),
]
# Photos with these labels confirmed are left out of this pack whoever is in them (gaps_oi_packs leaves out swimwear
# only when a child is there).
NO_SWIMWEAR = {"Swimwear", "Bikini", "Swim briefs", "Swimming", "One-piece swimsuit", "Underpants", "Boxer shorts",
               "Panties", "Lingerie", "Undergarment", "Brassiere", "Nudity"}


def build_open_images_clothing(limit):
    """open_images_clothing (see the module docstring), with NO_SWIMWEAR added to gaps_oi_packs.LEAVE_OUT for this
    build only (restored afterwards)."""
    saved = g.LEAVE_OUT
    g.LEAVE_OUT = set(saved) | NO_SWIMWEAR
    try:
        return build_oi_gap("open_images_clothing", CLOTHING_OI, limit, 9405)
    finally:
        g.LEAVE_OUT = saved


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
CLOTHING_PACKS = {
    "commons_clothing_more": (build_commons_clothing_more, COMMONS_LICENCE.format(
        what="blazer, coat, blouse, waistcoat, hat, belt, shoe, slipper, argyle and stripe")),
    "open_images_clothing": (build_open_images_clothing, OI_LICENCE),
}
CLOTHING_LIMITS = {
    "commons_clothing_more": 800,      # 11 categories
    "open_images_clothing": 2000,      # 38 labels; shirts and T-shirts have most photos
}
CLOTHING_COMMONS_KEYS = ("commons_clothing_more",)
CLOTHING_SPECS = CLOTHING


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a clothing pack builder.")
    parser.add_argument("key", choices=sorted(CLOTHING_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = CLOTHING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
