"""A self-test of the packaged-goods parsers (packs/packaged_goods_packs.py and
training-kit/kit/packaged_goods_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - an ABO listing of a packaged good gets "What is this?" with its kind, brand, the name on its listing, and the
    package, size and flavour only where the listing says them; "What brand is this?" and "What size is this
    package?" only when known; supplements and medicines end with the pharmacist line;
  - a general type (toiletries, pet supplies) is used only when its name says a package or a size (and, for pet
    supplies, a food, treat or litter), so tweezers and dog beds are left out; sexual products are left out; a kind
    is said only when the listing's name says the same; "Amazon Brand - " is not part of the brand;
  - a listing with no English name is found for setting aside (needs_description), and no ABO type is in both
    abo_products and this pack;
  - the Open Images answer names the packaging people checked, the most specific label first, and what they saw
    with it; a photo with no packaging label gets no answer;
  - the kit's FDA recall reader takes the listing's cells, keeps packaged-goods recalls only, reads the product
    photos and their alt text from a page, and answers from the label's own words;
  - both packs are wired: in build_packs.PACKS (not in COMMONS_KEYS), in the workflows' known list and limit lines,
    in the kit's sources; the Open Images one and the FDA photos never for picture-making.

Run it from the repository's folder:   python3 -m pytest packs/test_packaged_goods.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import packaged_goods_packs as p  # noqa: E402
import things_packs  # noqa: E402

REPO = os.path.dirname(HERE)


def en(value, tag="en_US"):
    """An ABO language-tagged field with one value."""
    return [{"language_tag": tag, "value": value}]


def listing(kind, name, brand="", country="US", **more):
    """A made-up ABO listing."""
    out = {"product_type": [{"value": kind}], "item_name": en(name) if name else [], "country": country,
           "main_image_id": "81abcDEF+gL", "item_id": "B000TEST01", "domain_name": "amazon.com",
           "marketplace": "Amazon"}
    if brand:
        out["brand"] = en(brand)
    out.update(more)
    return out


# ----------------------------------------------------------------- ABO packaged goods

def test_grocery_answer_names_brand_name_package_and_size():
    """A jar of pasta sauce: the listing's name, its package and its size; the brand is in the name, so no "by"."""
    rows = p.pg_rows(listing("SAUCE", "Solimo Tomato Basil Pasta Sauce Jar, 24oz", brand="Amazon Brand - Solimo"))
    what = rows[0]
    assert what["question"] == "What is this?"
    assert what["answer"] == ("This is a packaged food (a sauce). The name on its listing: Solimo Tomato Basil Pasta "
                              "Sauce Jar, 24oz. Package: a jar. Size: 24 oz.")
    assert {"question": "What brand is this?", "answer": "The brand is Solimo."} in rows
    assert {"question": "What size is this package?", "answer": "Its listing gives the size as 24 oz."} in rows


def test_general_type_and_flavour():
    """GROCERY is "a grocery product"; a brand not in the name is said with "by"; the Whole Foods colour field is a
    flavour; units are written out plainly."""
    rows = p.pg_rows(listing("GROCERY", "Organic Cashews, 10 OZ", brand="365 Everyday Value",
                             marketplace="WholeFoods", color=en("Chai")))
    assert rows[0]["answer"] == ("This is a grocery product by 365 Everyday Value. The name on its listing: Organic "
                                 "Cashews, 10 OZ. Size: 10 oz. Flavour or variety: Chai.")
    # Elsewhere the colour field is a colour, not a flavour.
    other = p.pg_rows(listing("GROCERY", "Dal Combo, 1kg", brand="Vedaka", country="IN", color=en("White")))
    assert "Flavour" not in other[0]["answer"] and "Size: 1 kg." in other[0]["answer"]
    juice = p.pg_rows(listing("GROCERY", "365 EVERYDAY VALUE Organic Tomato Juice, 32 FZ"))
    assert "Size: 32 fl oz." in juice[0]["answer"]


def test_brand_already_in_name():
    """A brand whose words are in the name is not said again ("365 by Whole Foods Market")."""
    assert p.brand_in_name("365 by Whole Foods Market", "365 Everyday Value, Trail Mix, 16 Ounce")
    assert not p.brand_in_name("Wickedly Prime", "Kona Coffee Roasted Pecans, 1.5 oz")
    rows = p.pg_rows(listing("GROCERY", "365 Everyday Value, Trail Mix, 16 Ounce", brand="365 by Whole Foods Market"))
    assert rows[0]["answer"].startswith("This is a grocery product. The name")


def test_sizes_and_packs():
    """Sizes and pack counts from the name; a dose (mg) is not a package size; "Pack of 1" is not said."""
    assert p.pg_size("Turmeric 500mg - 60 Veg Capsules") == "60 capsules"
    assert p.pg_size("Sparkling Water (Pack of 12)") == "a pack of 12"
    assert p.pg_size("Roasted Cashews, 1.5 Ounce (Pack of 15)") == "1.5 oz, a pack of 15"
    assert p.pg_size("Hand Sanitizer, 8 Fl Oz (Pack of 1)") == "8 fl oz"
    assert p.pg_size("Laundry HE, Fresh Scent, 35ct") == "35 count"
    assert p.pg_size("Motor Oil - 5W-20 - 1 Quart - 6 Pack") == "1 quart, a pack of 6"
    assert p.pg_size("Organic Light Cream, 1 PT") == "1 pint"
    assert p.pg_size("Coffee Beans") == ""


def test_packages():
    """The package only when the name says it; tea bags are not a bag; "can" as a verb is not a can."""
    assert p.pg_package("Peanut Butter Jar, 16 oz") == "a jar"
    assert p.pg_package("Sparkling Water, 12 fl oz can (Pack of 12)") == "a can"
    assert p.pg_package("Green Tea, 20 Tea Bags") == ""
    assert p.pg_package("Dry Dog Food (5 lb. Bag)") == "a bag"
    assert p.pg_package("Glass Cleaner Kit with 2 Sprayer Bottles") == "a spray bottle"
    assert p.pg_package("You can use it daily, 4 oz") == ""
    assert p.pg_package("Allergy Relief Tablets, Blister Pack, 24 ct") == "a blister pack"


def test_medicine_line_and_kind_check():
    """Supplements end with the pharmacist line; "vitamins" is said only when the name says it."""
    rows = p.pg_rows(listing("VITAMIN", "Amazon Elements Prenatal Vitamins, 130 Tablets", brand="Amazon Elements"))
    assert rows[0]["answer"].startswith("This is a vitamin or dietary supplement (vitamins).")
    assert rows[0]["answer"].endswith("Check the packaging or ask a pharmacist to be sure.")
    other = p.pg_rows(listing("VITAMIN", "Iron 18mg, 195 Capsules"))
    assert other[0]["answer"].startswith("This is a vitamin or dietary supplement. The name")


def test_left_out():
    """Tweezers (no package or size), a dog bed, sexual products and listings with no English name are left out."""
    assert p.pg_rows(listing("HEALTH_PERSONAL_CARE", "Solimo Eyebrow Tweezer")) == []
    assert p.pg_rows(listing("PET_SUPPLIES", "Dog Bed, Large, 36 inches, 2 Pack")) == []
    assert p.pg_rows(listing("PET_SUPPLIES", "Silicone Can Lids for Pet Food Cans")) == []
    assert p.pg_rows(listing("PET_SUPPLIES", "Dry Dog Food, Chicken Recipe (5 lb. Bag)"))
    assert p.pg_rows(listing("HEALTH_PERSONAL_CARE", "Ultra Thin Condoms, 12 Count")) == []
    assert p.pg_rows(listing("CHAIR", "Office Chair, 1 Pack")) == []
    assert p.pg_rows(listing("HEALTH_PERSONAL_CARE", "100ml Ultrasonic Essential Oil Diffuser, White")) == []
    # A shape in the style field of a toiletry is not a flavour; quotes around a brand are not part of it.
    soap = p.pg_rows(listing("SKIN_CLEANING_AGENT", "Hand Soap, 12 fl oz", brand='"Solimo"', style=en("Oval")))
    assert soap[0]["answer"] == ("This is a toiletry, beauty or health product (a soap or cleanser) by Solimo. The "
                                 "name on its listing: Hand Soap, 12 fl oz. Size: 12 fl oz.")
    assert {"question": "What brand is this?", "answer": "The brand is Solimo."} in soap
    assert p.pg_rows(listing("GROCERY", "")) == []


def test_child_marked():
    """A product whose words name a child is marked "child" (never for picture-making)."""
    rows = p.pg_rows(listing("SKIN_CLEANING_WIPE", "Baby Wipes, Fragrance Free, 72 Count", brand="Mama Bear"))
    assert rows and all(r.get("child") for r in rows)


def test_foreign_names_set_aside():
    """A packaged-goods listing with no English name is found for setting aside, with its name and brand."""
    german = listing("GROCERY", "", country="DE",
                     item_name=[{"language_tag": "de_DE", "value": "Bio Haferflocken, 500 g"}])
    german["brand"] = [{"language_tag": "de_DE", "value": "Solimo"}]
    assert p.pg_foreign(german) == ("Bio Haferflocken, 500 g", "Solimo")
    assert p.pg_foreign(listing("GROCERY", "Oats, 500 g")) is None           # it has an English name
    assert p.pg_foreign(dict(german, product_type=[{"value": "PET_SUPPLIES"}])) is None


def test_no_type_in_both_abo_packs():
    """No ABO product type is in both abo_products and abo_packaged_goods."""
    assert not set(p.PG_TYPES) & (set(things_packs.ABO_TYPES) | set(things_packs.ABO_GENERAL))
    assert set(p.PG_LEADS) <= set(p.PG_TYPES)
    assert {group for _, group in p.PG_TYPES.values()} <= set(p.PG_GROUPS)


def test_abroad_share():
    """Shops outside the USA and Canada are held to their share of the pack; the types take turns."""
    import random
    candidates = [(listing("GROCERY", f"Item {i}, 1 oz", country="IN"), [{}]) for i in range(50)]
    candidates += [(listing("COFFEE", f"Coffee {i}, 12 oz", country="US"), [{}]) for i in range(50)]
    chosen = p.pg_queue(candidates, 20, random.Random(1))
    abroad = sum(1 for lst, _ in chosen if lst["country"] == "IN")
    assert len(chosen) == 24 and abroad <= p.PG_ABROAD_SHARE * 24


# ----------------------------------------------------------------- Open Images packaged goods

def test_open_images_answers():
    """The most specific packaging first, what people saw with it, and the shop; no packaging label, no answer."""
    assert p.oi_pg_answer({"Tin can": 1, "Aluminum can": 1, "Energy drink": 1, "Soft drink": 1}) == \
        "It shows an aluminium drink can, with an energy drink."
    assert p.oi_pg_answer({"Cardboard packaging": 1, "Packaging and labeling": 1, "Breakfast cereal": 1,
                           "Supermarket": 1, "Grocery store": 1}) == \
        "It shows cardboard packaging, with breakfast cereal, in a supermarket."
    assert p.oi_pg_answer({"Packaging and labeling": 1}) == ""          # gift wrap, posters: not enough
    assert p.oi_pg_answer({"Packaging and labeling": 1, "Snack": 1}) == "It shows product packaging, with snacks."
    assert p.oi_pg_answer({"Bottled water": 1, "Plastic bottle": 1}) == "It shows bottled water."
    assert p.oi_pg_answer({"Soft drink": 1, "Snack": 1}) == ""
    assert p.oi_pg_answer({"Tin can": 0, "Snack": 1}) == ""


# ----------------------------------------------------------------- the kit's FDA recall photos

FDA_ROW = ['<time datetime="2026-11-17T05:00:00Z">11/17/2026</time>\n',
           '<a href="/safety/recalls-market-withdrawals-safety-alerts/made-up-foods-recalls-tortelloni">Priano</a>',
           "Protein Carbonara Tortelloni", "Food &amp; Beverages, Foodborne Illness",
           "Potential to be contaminated with Clostridium botulinum.", "Made-Up Foods, Inc.", "", ""]
FDA_PAGE = ('<h2>Product Photos</h2><img loading="eager" src="/files/styles/recall_image_small/public/'
            'image_1_265.png?itok=yfb" width="298" alt="Priano Protein Carbonara Tortelloni, Net Wt. 9 oz, Best if '
            'used by 12/18/2026" class="img-responsive" /><img src="/files/styles/recall_image_small/public/'
            'image_2_207.png?itok=X" alt="Lot code" /><img src="/themes/custom/logo.svg" alt="FDA logo">')


def test_fda_listing_and_rows():
    """The listing's cells become a record; the page's product photos are read at full size with their alt text;
    the answer reads the label; a lot-code photo is named from the notice instead."""
    import sources  # noqa: F401 - loaded first, as the kit does (it imports this file itself)
    import packaged_goods_sources as k
    record = k.fda_listing([FDA_ROW])[0]
    assert record["url"] == ("https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts/"
                             "made-up-foods-recalls-tortelloni")
    assert record["brand"] == "Priano" and record["date"] == "2026-11-17"
    assert record["kinds"] == "Food & Beverages, Foodborne Illness"
    pictures = k.fda_pictures(FDA_PAGE)
    assert pictures[0][0] == "https://www.fda.gov/files/image_1_265.png" and len(pictures) == 2
    items = k.fda_rows(record, pictures)
    answers = [row["answer"] for _, _, row in items]
    assert answers[0] == "This is the recalled product: Priano Protein Carbonara Tortelloni, Net Wt. 9 oz, Best if " \
                         "used by 12/18/2026."
    assert answers[1] == ("It was recalled in the USA for this reason: Potential to be contaminated with Clostridium "
                          "botulinum.")
    assert answers[2] == "This is the recalled product: Priano Protein Carbonara Tortelloni."
    assert all(row["place"] == "United States" and "Made-Up Foods" in row["credit"] for _, _, row in items)


def test_fda_kinds():
    """Devices, biologics and tobacco are left out; medicines and supplements end with the pharmacist line."""
    import sources  # noqa: F401 - loaded first, as the kit does (it imports this file itself)
    import packaged_goods_sources as k
    record = k.fda_listing([FDA_ROW])[0]
    assert not k.fda_wanted(dict(record, kinds="Medical Devices"))
    assert not k.fda_wanted(dict(record, kinds="Drugs, Medical Devices"))
    assert not k.fda_wanted(dict(record, product="Male Enhancement Capsules", kinds="Drugs"))
    assert not k.fda_wanted(dict(record, reason="Contains undeclared tadalafil", kinds="Dietary Supplements"))
    assert k.fda_product("Image of side panel of OsteoDenx, 30 capsules", record) == \
        "side panel of OsteoDenx, 30 capsules"
    drug = k.fda_rows(dict(record, kinds="Drugs", product="Eye Drops"), [("https://www.fda.gov/files/a.png",
                                                                        "Eye Drops, 0.5 fl oz")])
    assert drug[0][2]["answer"].endswith("Check the packaging or ask a pharmacist to be sure.")
    assert "Brand: Priano." in drug[0][2]["answer"]


# ----------------------------------------------------------------- wiring

def test_wiring():
    """Both packs are in PACKS (not the Commons lane), the workflows know them and their limits, the kit lists them,
    and the Open Images pack and the FDA photos are never used for picture-making."""
    keys = set(p.PACKAGED_GOODS_PACKS)
    assert keys <= set(build_packs.PACKS)
    assert not keys & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in p.PACKAGED_GOODS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import packaged_goods_sources") == 2
    import sources
    import packaged_goods_sources as k
    listed = {s.key for s in sources.SOURCES}
    assert keys | {"fda_recall_photos"} <= listed
    assert {"open_images_packaged_goods", "fda_recall_photos"} <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert "abo_packaged_goods" not in sources.NOT_FOR_PICTURE_MAKING
    assert k.PACKAGED_GOODS_PICTURE_MAKING_OK == set()
    assert next(s for s in sources.SOURCES if s.key == "fda_recall_photos").group == "research"
