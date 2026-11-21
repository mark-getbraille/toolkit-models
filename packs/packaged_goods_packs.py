"""Pack builders for MODERN PACKAGED GOODS: food and drink, household cleaning products, toiletries, medicines and
vitamins, and pet products, in their boxes, cans, bottles, jars, bags and blister packs. Used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus "place" where the source states one and "child": true where
the product's words name a child. A picture with more than one question comes once with its JPEG and then again as
(None, None, row) rows whose "file" names the same picture (food_packs.with_twins), so the zip holds each picture only
once. The limit counts pictures.

Every answer is a fixed sentence written here from the source's own record: a product listing's type, brand, name,
flavour and size; a label people checked by hand. The answers name the kind of product, the brand and the product's
name where the record states them, the package (a jar, a bottle, a box ...) and the size or flavour where the
listing's own name says so. Nothing is written by an AI model, and nothing is guessed: a package or a size is said
only when the listing's name says it.

The packs (both open, checked at the source in November 2026):
  abo_packaged_goods         Amazon Berkeley Objects (Amazon.com and UC Berkeley, CC BY 4.0): catalogue photos of
                             the packaged goods that abo_products leaves out (groceries, drinks, coffee and tea,
                             vitamins and supplements, medicines, toiletries and beauty products, cleaning products,
                             laundry detergent, motor oil, pet food and cat litter), mostly sold in the USA and
                             Canada (Amazon, Amazon Fresh and Whole Foods Market's own brands), some in other
                             countries. "What is this?" -> "This is a drink (coffee). The name on its listing:
                             Allegro Coffee Decaf Organic French Roast Ground Coffee, 12 oz. Size: 12 oz.";
                             "What brand is this?" and "What size is this package?" where the listing says. A listing
                             with no English name is set aside for a description (needs_description).
  open_images_packaged_goods Google Open Images V7 validation and test photos (labels CC BY 4.0; each photo CC BY 2.0
                             with its photographer named, checked photo by photo) with a packaging label people
                             checked by hand: tin cans, drink cans, plastic bottles, bottled water, cardboard
                             packaging, nutrition facts labels, ready meals, with what people saw in them (soft
                             drinks, energy drinks, cereal, snacks, sweets, cosmetics, pet food). "What packaged goods
                             are in this picture?" -> "It shows an aluminium drink can, with an energy drink."
                             "Packaging and labeling" alone (often gift wrap) is not enough. Rows of photos where
                             people checked a child are marked "child"; the kit never uses this pack for
                             picture-making (its photos often show people).

  abo_pet_supplies           Amazon Berkeley Objects again: the ANIMAL CARE PRODUCTS abo_packaged_goods leaves out
                             (it takes pet food, treats, litter and care products in packages): leashes, collars,
                             harnesses and muzzles, crates and carriers, beds, bowls, feeders and fountains, toys,
                             grooming brushes, clippers and nail trimmers, litter boxes and scoops, flea and tick
                             collars, spot-ons and chewables, dewormers and pill pockets, aquarium filters, heaters,
                             water conditioners and tanks, terrariums and UVB lamps, bird cages and perches,
                             small-animal cages, bedding and hay, pet doors, waste bags and training pads, horse
                             tack, incubators and livestock supplies, and pet first aid kits. "What is this?" ->
                             "This is an animal care product: a harness by PetSafe. The name on its listing: ..."
                             The kinds take turns; listings in the USA and Canada first.

Looked at and not built here (the reasons are in training-kit/kit/packaged_goods_sources.py, with the personal-use
FDA recall photos): recall photos of the CPSC, FDA, USDA FSIS and Health Canada (the recalling firms' own photos, so
not public domain), Smithsonian NMAH (its CC0 pictures hold almost no modern packaging), Te Papa (packaging pictures
CC BY-NC-ND or all rights reserved), museums whose robots.txt says "ai-train=no" or refuses robots (Ingenium, RISD,
the Science Museum Group, Powerhouse), and datasets under non-commercial, NoDerivatives or research-only terms.

    python packs/packaged_goods_packs.py abo_packaged_goods --limit 8      (prints a few rows: a quick check)
"""

import collections
import csv
import gzip
import io
import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, fetch_all, say, needs_description
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from food_packs import listed, with_twins, oi_lines, oi_licence_name, OI_LABELS, OI_CLASSES, OI_IMAGES, OI_PICTURE
from things_packs import (ABO_LISTINGS, ABO_IMAGES, ABO_PICTURE, ABO_CREDIT, ABO_TYPES, ABO_GENERAL, abo_value,
                          abo_name_says, oi_credit)
from expression_packs import mark_child, OI_CHILD
from pill_packs import SAFETY
from places import where, country_named

WHAT_Q = "What is this?"
BRAND_Q = "What brand is this?"
SIZE_Q = "What size is this package?"
PACKAGED_Q = "What packaged goods are in this picture?"

# Words that leave a product out (the safety rules): sexual products, and intimate products.
NOT_SHOWN = re.compile(r"\b(condoms?|lubricants?|lube|sexual\w*|sexy|erotic\w*|adult toys?|vibrators?|intimate|"
                       r"lingerie|nude|naked|pregnancy tests?|ovulation)\b", re.I)


# ----------------------------------------------------------------- abo_packaged_goods (Amazon Berkeley Objects)

# The ABO product types of packaged goods (none of them is in things_packs.ABO_TYPES or ABO_GENERAL, so no listing is
# in both packs): {type: (the kind in plain words, or "" when the type is too general, the group)}. The kind is said
# only when the listing's own name says the same (abo_name_says), as in abo_products; the group is always said.
PG_TYPES = {
    # food
    "GROCERY": ("", "food"), "PANTRY": ("", "food"), "HERB": ("herbs or spices", "food"),
    "LEGUME": ("beans or lentils", "food"), "BREAD": ("bread", "food"), "EDIBLE_OIL_VEGETABLE": ("cooking oil", "food"),
    "SAUCE": ("a sauce", "food"), "DAIRY_BASED_CHEESE": ("cheese", "food"), "NOODLE": ("noodles or pasta", "food"),
    "SNACK_MIX": ("a snack mix", "food"), "COOKIE": ("biscuits (cookies)", "food"),
    "BREAKFAST_CEREAL": ("breakfast cereal", "food"), "SNACK_CHIP_AND_CRISP": ("crisps (chips)", "food"),
    "CAKE": ("cake", "food"), "PACKAGED_SOUP_AND_STEW": ("soup", "food"), "CRACKER": ("crackers", "food"),
    "SUGAR": ("sugar", "food"), "NUT_BUTTER": ("nut butter", "food"), "SALAD_DRESSING": ("salad dressing", "food"),
    "SNACK_FOOD_BAR": ("snack bars", "food"), "HONEY": ("honey", "food"), "FLOUR": ("flour", "food"),
    "FRUIT_SNACK": ("fruit snacks", "food"), "NUTS": ("nuts", "food"), "DAIRY_BASED_CREAM": ("cream", "food"),
    "CHOCOLATE_CANDY": ("chocolate", "food"), "VINEGAR": ("vinegar", "food"), "POPCORN": ("popcorn", "food"),
    "CANDY": ("sweets (candy)", "food"), "PASTRY": ("pastries", "food"), "BAKING_MIX": ("a baking mix", "food"),
    "PRETZEL": ("pretzels", "food"), "RICE_MIX": ("rice", "food"), "DAIRY_BASED_BUTTER": ("butter", "food"),
    "DAIRY_BASED_ICE_CREAM": ("ice cream", "food"),
    # drinks
    "COFFEE": ("coffee", "drink"), "TEA": ("tea", "drink"), "DAIRY_BASED_DRINK": ("a milk drink", "drink"),
    "JUICE_AND_JUICE_DRINK": ("juice", "drink"), "WATER": ("water", "drink"),
    "DRINK_FLAVORED": ("a flavoured drink", "drink"), "MILK_SUBSTITUTE": ("a plant milk", "drink"),
    "WINE": ("wine", "alcohol"), "SPIRITS": ("spirits", "alcohol"),
    # vitamins, supplements and medicines (answers end with pill_packs.SAFETY)
    "VITAMIN": ("vitamins", "supplement"), "NUTRITIONAL_SUPPLEMENT": ("", "supplement"),
    "HERBAL_SUPPLEMENT": ("", "supplement"), "MINERAL_SUPPLEMENT": ("", "supplement"),
    "PROTEIN_SUPPLEMENT_POWDER": ("protein powder", "supplement"), "MEDICATION": ("", "medicine"),
    "WOUND_DRESSING": ("plasters or wound dressings", "first aid"),
    # toiletries, beauty and health
    "HEALTH_PERSONAL_CARE": ("", "personal"), "ABIS_DRUGSTORE": ("", "personal"),
    "PROFESSIONAL_HEALTHCARE": ("", "personal"), "BEAUTY": ("", "personal"), "ABIS_BEAUTY": ("", "personal"),
    "SKIN_CLEANING_AGENT": ("a soap or cleanser", "personal"), "SKIN_MOISTURIZER": ("a moisturiser", "personal"),
    "SKIN_CLEANING_WIPE": ("wipes", "personal"), "SHAMPOO": ("shampoo", "personal"),
    "CONDITIONER": ("conditioner", "personal"), "HAIR_CLEANER_CONDITIONER": ("shampoo or conditioner", "personal"),
    "SUNSCREEN": ("sunscreen", "personal"), "MOUTHWASH": ("mouthwash", "personal"),
    "BATHWATER_ADDITIVE": ("a bath product", "personal"), "TOOTHBRUSH": ("toothbrushes", "personal"),
    "RAZOR_BLADE_CARTRIDGE": ("razor blades", "personal"), "HAIR_STYLING_AGENT": ("a hair styling product", "personal"),
    "BODY_DEODORANT": ("deodorant", "personal"), "ESSENTIAL_OIL": ("an essential oil", "personal"),
    "HAIR_REMOVAL_AGENT": ("a hair removal product", "personal"), "SKIN_EXFOLIANT": ("a scrub", "personal"),
    "LIP_COLOR": ("lipstick", "personal"),
    # household
    "CLEANING_AGENT": ("a cleaner", "household"), "LAUNDRY_DETERGENT": ("laundry detergent", "household"),
    "DISHWASHER_DETERGENT": ("dishwasher detergent", "household"), "FACIAL_TISSUE": ("tissues", "household"),
    "PAPER_PRODUCT": ("", "household"), "AUTO_OIL": ("motor oil", "household"),
    # pets
    "PET_SUPPLIES": ("", "pet"), "ANIMAL_LITTER": ("cat litter", "pet"),
    "PET_PEST_CONTROL": ("a flea and tick treatment", "pet"),
}
# What the answer calls a listing of a general type (the group's words would say too much: Whole Foods files juice,
# essential oils and sleep aids as GROCERY, and maca powder as HEALTH_PERSONAL_CARE).
PG_LEADS = {"GROCERY": "a grocery product", "PANTRY": "a grocery product",
            "HEALTH_PERSONAL_CARE": "a health or personal care product",
            "ABIS_DRUGSTORE": "a health or personal care product",
            "PROFESSIONAL_HEALTHCARE": "a health care product", "BEAUTY": "a beauty product",
            "ABIS_BEAUTY": "a beauty product", "NUTRITIONAL_SUPPLEMENT": "a dietary supplement",
            "HERBAL_SUPPLEMENT": "a herbal supplement", "MINERAL_SUPPLEMENT": "a mineral supplement"}
PG_GROUPS = {"food": "a packaged food", "drink": "a drink", "alcohol": "an alcoholic drink",
             "supplement": "a vitamin or dietary supplement", "medicine": "a medicine",
             "first aid": "a first aid product", "personal": "a toiletry, beauty or health product",
             "household": "a household product", "pet": "a pet product"}
# Groups whose answer ends with pill_packs.SAFETY ("Check the packaging or ask a pharmacist to be sure.").
PG_SAFETY_GROUPS = {"supplement", "medicine"}
# Groups where only a listing whose name says a package or a size is used: their types (HEALTH_PERSONAL_CARE, PET_SUPPLIES
# ...) also hold tweezers, scales, dog beds and cat trees, which are not packaged goods.
PG_NEEDS_PACKAGE = {"personal", "household", "pet", "first aid"}
# PET_SUPPLIES also holds bowls, beds, toys and can lids: only listings whose name says a food, treat, litter or care
# product are used.
PG_PET_GOODS = re.compile(r"\b(food|treats?|chews?|biscuits?|kibble|jerky|litter|shampoo|wipes|spray|supplements?|"
                          r"dental sticks?|pads)\b", re.I)
PG_PET_NOT_GOODS = re.compile(r"\b(lids?|covers?|bowls?|scoops?|mats?|feeders?|dispensers?|containers?|storage|"
                              r"beds?|toys?|crates?|carriers?|leash\w*|collars?|harness\w*|litter (box|pan|tray)\w*)\b",
                              re.I)
# Devices and tools filed under the general types (an essential-oil diffuser with "100ml" in its name): left out.
PG_DEVICES = re.compile(r"\b(diffusers?|humidifiers?|machines?|scales?|thermometers?|massagers?|devices?|monitors?|"
                        r"tweezers?|clippers?|trimmers?|shavers?|dryers?|straighteners?|curling|lamps?|lights?|"
                        r"electric|rechargeable|batter(y|ies)|chargers?|holders?|organi[sz]ers?|stands?)\b", re.I)
PG_NORTH_AMERICA = {"US", "CA"}
PG_ABROAD_SHARE = 0.3          # at most this share of the pack from shops outside the USA and Canada

# The package, from the listing's own name: (pattern, what it is called). The first that matches is said.
PACKAGES = [
    (r"\bblister", "a blister pack"), (r"\bk-?cups?\b|\bpods?\b|\bcapsules?\b(?=.*\b(coffee|espresso|nespresso)\b)",
                                      "single-serve coffee pods"),
    (r"\bspray bottles?\b|\bsprayer\b|\btrigger spray\b", "a spray bottle"), (r"\bpump bottles?\b", "a pump bottle"),
    (r"\bjars?\b", "a jar"), (r"\bjugs?\b", "a jug"), (r"\bbottles?\b", "a bottle"), (r"\bcartons?\b", "a carton"),
    (r"\bcans\b|\bcanned\b|\bcan\b(?=\s*(\)|,|$|-|\(|pack))|\b\d+(\.\d+)?\s*(fl\.?\s*)?oz\.?\s*can\b", "a can"),
    (r"\btins?\b(?! foil)", "a tin"), (r"\btubes?\b", "a tube"), (r"\btubs?\b", "a tub"),
    (r"\bpouch(es)?\b", "a pouch"), (r"\b(sachets?|packets?)\b", "a packet"),
    (r"(?<!tea )(?<!trash )(?<!garbage )(?<!storage )(?<!zipper )(?<!freezer )(?<!sandwich )\bbags?\b", "a bag"),
    (r"\bbox(es)?\b", "a box"), (r"\brolls?\b", "rolls"),
]
PACKAGES = [(re.compile(p, re.I), said) for p, said in PACKAGES]
# A size or amount in the listing's name: "24oz", "1 PT", "5 lb.", "500 ml", "35ct", "130 Tablets", "Pack of 6".
# (Not "mg" or "mcg": those are the dose of a tablet, not the size of the package.)
UNITS = (r"fl\.?\s*oz|fz|fluid ounces?|oz|ounces?|lbs?|pounds?|kg|g|grams?|ml|cl|l|lt|litres?|liters?|pt|pints?|qt|"
         r"quarts?|gal|gallons?|ct|count|tablets?|caplets?|capsules?|softgels?|gummies|lozenges|pods?|k-cups?|"
         r"wipes|sheets|rolls|bags|loads|pieces|pcs|sticks|bars|servings")
# (A word may stand between the number and the unit: "60 Veg Capsules", "120 Liquid Softgels".)
SIZE = re.compile(rf"(?<![\w.])(\d+(?:[.,]\d+)?)\s*-?\s*(?:(?:veg|veggie|vegetarian|vegan|liquid|soft|chewable|"
                  rf"coated|easy[- ]to[- ]swallow|quick[- ]dissolve|delayed[- ]release)\s+)?({UNITS})\.?(?![\w])",
                  re.I)
PACK_OF = re.compile(r"\b(?:pack of|set of|case of)\s*(\d+)\b|\b(\d+)[\s-]*(?:pack|pk)\b", re.I)
UNIT_WORDS = {"oz": "oz", "fl oz": "fl oz", "fz": "fl oz", "fl. oz": "fl oz", "ounce": "oz", "ounces": "oz", "lb": "lb", "lbs": "lb",
              "pound": "lb", "pounds": "lb", "pt": "pint", "qt": "quart", "gal": "gallon", "ct": "count",
              "l": "litre", "lt": "litre", "liter": "litre", "liters": "litres", "pcs": "pieces"}
NOT_A_FLAVOUR = re.compile(rf"^(n/?a|none|other|assorted|multi\w*|original|regular|standard|default|pack of \d+|"
                           rf"\d+(\.\d+)?\s*({UNITS})\b.*|\d+.*|.*\bpack\b.*|.*\bcount\b.*|.*\bounce\b.*)$", re.I)
NOT_A_BRAND = re.compile(r"^(generic|unbranded|unknown|n/?a|none|no brand)$", re.I)
AMAZON_BRAND = re.compile(r"^amazon brand\s*[-–:]\s*", re.I)


def pg_brand(listing, country):
    """The listing's brand ("Amazon Brand - Solimo" -> "Solimo"), or "" when it gives none or "Generic"."""
    brand = AMAZON_BRAND.sub("", abo_value(listing.get("brand"), country).strip(" \"'“”")).strip()
    return "" if NOT_A_BRAND.match(brand) else brand


def brand_in_name(brand, name):
    """True when the listing's name already says the brand (one of its words of three letters or more, or a number):
    "365 by Whole Foods Market" is in "365 Everyday Value, Trail Mix", so "by ..." is not added."""
    words = [w for w in re.findall(r"[\w']+", brand.lower()) if (len(w) >= 3 or w.isdigit())
             and w not in ("the", "and", "brand")] or [brand.lower()]
    low = name.lower()
    return any(re.search(rf"\b{re.escape(w)}\b", low) for w in words)


def unit_word(unit):
    """The plain word for a unit as a name writes it ("OZ" -> "oz", "ct" -> "count")."""
    low = re.sub(r"\s+", " ", unit.lower().replace(".", ". ").replace(" .", ".")).strip()
    low = low.replace(". ", " ").replace(".", "").strip()
    return UNIT_WORDS.get(low, low)


def pg_size(name):
    """The size or amount the listing's name gives ("24 oz", "a pack of 6", "130 tablets"), or ""."""
    parts = []
    m = SIZE.search(name)
    if m:
        amount, unit = m.group(1).replace(",", "."), unit_word(m.group(2))
        parts.append(f"{amount} {unit}")
    p = PACK_OF.search(name)
    if p:
        count = p.group(1) or p.group(2)
        if count and count != "1":
            parts.append(f"a pack of {count}")
    return ", ".join(parts)


def pg_package(name):
    """The package the listing's name says ("a jar", "a bottle" ...), or ""."""
    for pattern, said in PACKAGES:
        if pattern.search(name):
            return said
    return ""


def pg_flavour(listing, country, name, group):
    """The listing's flavour or variety ("Chai", "Dark Roast") for food, drinks and supplements, from its style field
    (and, for Whole Foods Market's, its colour field, where Whole Foods writes the flavour; elsewhere the colour field
    is a colour) when that is a word the name does not already hold, else "". Toiletries, household and pet products
    get none (their style field is a shape or a pack: "Oval")."""
    if group not in ("food", "drink", "alcohol", "supplement"):
        return ""
    fields = ("flavor", "style", "color") if listing.get("marketplace") == "WholeFoods" else ("flavor", "style")
    for field in fields:
        value = abo_value(listing.get(field), country)
        if value and len(value) <= 40 and not NOT_A_FLAVOUR.match(value) and value.lower() not in name.lower():
            return value
    return ""


def sentence_end(text):
    """Text ending with a full stop (not doubled)."""
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else text + "."


def pg_kind(listing):
    """(type code, kind, group) of an ABO listing, or ("", "", "") when it is not a packaged-goods type."""
    code = ((listing.get("product_type") or [{}])[0] or {}).get("value", "")
    if code not in PG_TYPES:
        return "", "", ""
    kind, group = PG_TYPES[code]
    return code, kind, group


def pg_rows(listing):
    """The rows for one ABO listing of a packaged good, or [] when it is not one this pack uses (not a packaged-goods
    type, no English name, words about sexual products, or a general type whose name says no package or size)."""
    code, kind, group = pg_kind(listing)
    country = listing.get("country") or ""
    name = abo_value(listing.get("item_name"), country)
    if not code or not name or not listing.get("main_image_id") or NOT_SHOWN.search(name):
        return []
    package, size = pg_package(name), pg_size(name)
    if group in PG_NEEDS_PACKAGE and not (package or size):
        return []
    if code == "PET_SUPPLIES" and (not PG_PET_GOODS.search(name) or PG_PET_NOT_GOODS.search(name)):
        return []
    if group in PG_NEEDS_PACKAGE and PG_DEVICES.search(name):
        return []
    brand = pg_brand(listing, country)
    if kind and not abo_name_says(kind, name):
        kind = ""
    flavour = pg_flavour(listing, country, name, group)
    by = f" by {brand}" if brand and not brand_in_name(brand, name) else ""
    first = f"This is {PG_LEADS.get(code) or PG_GROUPS[group]}" + (f" ({kind})" if kind else "") + by + "."
    answer = f"{first} The name on its listing: {sentence_end(name)}"
    if package:
        answer += f" Package: {package}."
    if size:
        answer += f" Size: {size}."
    if flavour:
        answer += f" Flavour or variety: {flavour}."
    if group in PG_SAFETY_GROUPS:
        answer += f" {SAFETY}"
    rows = [{"question": WHAT_Q, "answer": answer}]
    if brand:
        rows.append({"question": BRAND_Q, "answer": f"The brand is {brand}."})
    if size:
        rows.append({"question": SIZE_Q, "answer": f"Its listing gives the size as {size}."})
    return [mark_child(r, name) for r in rows]


def pg_foreign(listing):
    """(the name in another language, its brand) of a packaged-goods listing with no English name, for setting the
    picture aside for a description; None when it has an English name, is not a packaged good, or names something
    left out."""
    code, _, group = pg_kind(listing)
    country = listing.get("country") or ""
    if not code or abo_value(listing.get("item_name"), country) or not listing.get("main_image_id"):
        return None
    names = [clean(v.get("value")) for v in listing.get("item_name") or [] if isinstance(v, dict) and v.get("value")]
    if not names or NOT_SHOWN.search(" ".join(names)):
        return None
    if group in PG_NEEDS_PACKAGE and (not (pg_size(names[0]) or pg_package(names[0])) or PG_DEVICES.search(names[0])):
        return None
    if code == "PET_SUPPLIES":
        return None                     # pet supplies are mostly not packaged goods, and these words cannot tell
    brands = [clean(v.get("value")) for v in listing.get("brand") or [] if isinstance(v, dict) and v.get("value")]
    return names[0], (brands[0] if brands else "")


def pg_queue(candidates, limit, rng):
    """The order to fetch: the product types in turn (each shuffled), with shops outside the USA and Canada held to
    PG_ABROAD_SHARE of the pack. candidates: [(listing, rows)]."""
    by_kind = collections.defaultdict(list)
    for listing, rows in candidates:
        by_kind[pg_kind(listing)[0]].append((listing, rows))
    lists = []
    for code in sorted(by_kind):
        items = by_kind[code]
        rng.shuffle(items)
        lists.append(items)
    rng.shuffle(lists)
    order = []
    while any(lists):
        for items in lists:
            if items:
                order.append(items.pop())
    want, abroad, out = int(limit * 1.1) + 2, 0, []
    for listing, rows in order:
        if len(out) >= want:
            break
        if (listing.get("country") or "") not in PG_NORTH_AMERICA:
            if abroad + 1 > PG_ABROAD_SHARE * want:
                continue
            abroad += 1
        out.append((listing, rows))
    return out


def abo_place(listing):
    """{"place": the country of the shop, "place_kind": "market"} for an ABO listing (as abo_products does)."""
    country = listing.get("country") or ""
    return where(country_named("GB" if country == "UK" else country), "market")


def abo_listings(s):
    """Every listing of ABO's 16 listing files (about 85 MB), one dict at a time."""
    for part in "0123456789abcdef":
        r = s.get(ABO_LISTINGS.format(part), timeout=600)
        r.raise_for_status()
        for line in gzip.decompress(r.content).decode("utf-8").splitlines():
            try:
                yield json.loads(line)
            except ValueError:
                continue


def build_abo_packaged_goods(limit):
    """The ABO packaged-goods pack: reads the 16 listing files (about 85 MB) and the image list (6 MB), keeps the
    packaged-goods types above that have an English name and a main photo, sets aside those whose only name is in
    another language (needs_description), takes the product types in turn (the USA and Canada first), then fetches
    the catalogue photos."""
    s, rng = session(), pass_random(97)
    candidates, foreign, seen_images = [], [], set()
    for listing in abo_listings(s):
        image = listing.get("main_image_id")
        if not image or image in seen_images:           # the same product in several shops: once only
            continue
        rows = pg_rows(listing)
        if rows:
            seen_images.add(image)
            candidates.append((listing, rows))
            continue
        other = pg_foreign(listing)
        if other:
            seen_images.add(image)
            foreign.append((listing, other))
    say(f"ABO packaged goods: {len(candidates)} usable listings, {len(foreign)} with no English name")
    paths = {}
    r = s.get(ABO_IMAGES, timeout=600)
    r.raise_for_status()
    for row in csv.DictReader(io.StringIO(gzip.decompress(r.content).decode("utf-8"))):
        if row["image_id"] in seen_images:
            paths[row["image_id"]] = row["path"]
    items = []
    for listing, rows in pg_queue(candidates, limit, rng):
        path = paths.get(listing["main_image_id"])
        if not path:
            continue
        credit = ABO_CREDIT.format(item=listing.get("item_id", ""), domain=listing.get("domain_name", ""))
        items.append((f"abo-pg-{listing['main_image_id']}.jpg".replace("+", "_"), ABO_PICTURE.format(path),
                      [dict(row, credit=credit, **abo_place(listing)) for row in rows]))
    counts = collections.Counter(item[2][0].get("place", "not stated") for item in items)
    say("ABO packaged goods, countries: " + ", ".join(f"{c} {n}" for c, n in counts.most_common()))
    # Listings whose name is only in another language: set aside for a description (the picture passed every other
    # check: an open licence, a packaged-goods type, nothing left out by its words).
    rng.shuffle(foreign)
    for listing, (other_name, brand) in foreign:
        path = paths.get(listing["main_image_id"])
        if not path:
            continue
        code = pg_kind(listing)[0]
        place = abo_place(listing)
        needs_description(f"abo-pg-{listing['main_image_id']}.jpg".replace("+", "_"), ABO_PICTURE.format(path),
                          ABO_CREDIT.format(item=listing.get("item_id", ""), domain=listing.get("domain_name", "")),
                          "CC BY 4.0", "open", text=other_name, title=other_name,
                          reason="its listing has no English name", place=place.get("place", ""),
                          place_kind=place.get("place_kind", ""),
                          extra={"brand": brand, "product type": PG_LEADS.get(code) or PG_GROUPS[PG_TYPES[code][1]]},
                          page_url=f"https://{listing.get('domain_name') or 'www.amazon.com'}/dp/"
                                   f"{listing.get('item_id', '')}")
    fetched = fetch_all(items, workers=8)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- open_images_packaged_goods (Open Images V7)

# The packaging labels (one must be checked present), with the words an answer names them by.
OI_PG_PACKAGING = {
    "Aluminum can": "an aluminium drink can", "Beverage can": "a drink can", "Tin can": "a tin can",
    "Plastic bottle": "a plastic bottle", "Bottled water": "bottled water",
    "Cardboard packaging": "cardboard packaging", "Nutrition facts label": "a nutrition facts label",
    "Prepackaged meal": "a ready meal (a prepackaged meal)", "Packaging and labeling": "product packaging",
}
# What people saw with them (said after the packaging).
OI_PG_CONTENTS = {
    "Energy drink": "an energy drink", "Carbonated soft drinks": "a fizzy soft drink", "Soft drink": "a soft drink",
    "Beer bottle": "a beer bottle", "Breakfast cereal": "breakfast cereal", "Chocolate bar": "a chocolate bar",
    "Candy": "sweets (candy)", "Snack": "snacks", "Convenience food": "convenience food", "Cat food": "cat food",
    "Dog food": "dog food", "Pet food": "pet food", "Cosmetics": "cosmetics (make-up)",
    "Household paper product": "household paper products", "Dairy Product": "a dairy product",
}
OI_PG_PLACES = {"Supermarket": "in a supermarket", "Grocery store": "in a grocery store"}
# A general label is left out when a more specific one is there ("a drink can", not "a drink can and a tin can").
OI_PG_COVERED_BY = {
    "Tin can": {"Aluminum can", "Beverage can"}, "Beverage can": {"Aluminum can"},
    "Packaging and labeling": set(OI_PG_PACKAGING) - {"Packaging and labeling"},
    "Plastic bottle": {"Bottled water"}, "Soft drink": {"Carbonated soft drinks", "Energy drink"},
    "Pet food": {"Cat food", "Dog food"}, "Snack": {"Candy", "Chocolate bar"}, "Candy": {"Chocolate bar"},
    "Grocery store": {"Supermarket"},
}


def oi_pg_named(table, present):
    """The words for the labels of table that are present, leaving out those a more specific present label covers."""
    return [words for label, words in table.items()
            if label in present and not (OI_PG_COVERED_BY.get(label, set()) & present)]


def oi_pg_answer(labels):
    """The answer for one photo from its {label: 1 (checked present) or 0 (checked absent) or None}, or "" when no
    packaging label is checked present. "Packaging and labeling" alone (gift-wrapped presents, posters) is not
    enough: it is said only with a product people saw (cereal, a soft drink ...)."""
    present = {n for n, c in labels.items() if c == 1}
    packaging = oi_pg_named(OI_PG_PACKAGING, present)
    if not packaging or (packaging == [OI_PG_PACKAGING["Packaging and labeling"]]
                         and not oi_pg_named(OI_PG_CONTENTS, present)):
        return ""
    contents = oi_pg_named(OI_PG_CONTENTS, present)
    places = oi_pg_named(OI_PG_PLACES, present)
    answer = f"It shows {listed(packaging[:4])}"
    if contents:
        answer += f", with {listed(contents[:4])}"
    if places:
        answer += f", {places[0]}"
    return answer + "."


def build_open_images_packaged_goods(limit):
    """The Open Images packaged-goods pack: reads the labels people checked on the validation and test sets (about
    120 MB of lists), keeps photos with a packaging label checked present whose own licence is free and that need no
    turning, and fetches them (in random order)."""
    s = session()
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = set(OI_PG_PACKAGING) | set(OI_PG_CONTENTS) | set(OI_PG_PLACES) | set(OI_CHILD)
    names = {mids[n]: n for n in wanted if n in mids}
    say(f"Open Images: {len(names)} of {len(wanted)} packaged-goods labels found in the class list")
    labels = {}
    for url in OI_LABELS:
        for cells in csv.reader(oi_lines(s, url)):
            if len(cells) == 4 and cells[2] in names:
                try:
                    confidence = round(float(cells[3]))
                except ValueError:
                    continue
                picture = labels.setdefault(cells[0], {})
                name = names[cells[2]]
                picture[name] = confidence if picture.get(name, confidence) == confidence else None
    answers = {image_id: oi_pg_answer(picture) for image_id, picture in labels.items()}
    answers = {image_id: answer for image_id, answer in answers.items() if answer}
    say(f"Open Images: {len(answers)} pictures with a packaging label checked present")
    photos = {}
    for url in OI_IMAGES:
        for r in csv.DictReader(oi_lines(s, url)):
            image_id = r["ImageID"]
            if image_id not in answers:
                continue
            licence = oi_licence_name(r.get("License") or "", image_id)
            if licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[image_id] = (r["Subset"], licence, clean(r.get("Author")) or "an unnamed photographer",
                                    r.get("OriginalLandingURL") or "")
    items = []
    for image_id, answer in answers.items():
        if image_id not in photos:
            continue
        subset = photos[image_id][0]
        row = {"question": PACKAGED_Q, "answer": answer, "credit": oi_credit(photos[image_id])}
        if any(labels[image_id].get(c) == 1 for c in OI_CHILD):      # a child checked present: marked "child"
            row["child"] = True
        items.append((f"oi-pg-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id), row))
    pass_random(43).shuffle(items)
    say(f"Open Images: {len(items)} packaged-goods photos with a free licence")
    return fetch_all(items[:int(limit * 1.1) + 2], workers=8)[:limit]


# ----------------------------------------------------------------- abo_pet_supplies (animal care products)

# What an animal care product is, from the words of its listing's name, most specific first: (pattern, the kind said
# in the answer). The flea, tick and worm treatments, pet food, treats and litter in packages are
# abo_packaged_goods'; this pack takes the supplies that pack leaves out (PG_PET_NOT_GOODS) and the care products
# whose name says no package or size.
PET_SUPPLY_KINDS = [
    (r"\bflea (and|&) tick collar|\b(flea|tick) collar", "a flea and tick collar"),
    (r"\b(flea|tick)\b.*\b(spot[- ]on|topical|drops)\b|\bspot[- ]on\b", "a spot-on flea and tick treatment"),
    (r"\b(flea|tick)\b.*\bshampoo\b", "a flea and tick shampoo"),
    (r"\b(flea|tick)\b.*\b(chewables?|tablets?)\b", "a chewable flea and tick treatment"),
    (r"\b(de-?wormer|worm(er|ing))\b", "a dewormer"),
    (r"\bpill pockets?\b|\bpill (wrap|treat)s?\b", "pill pockets (treats to hide a pill in)"),
    (r"\bfirst aid kit\b", "a pet first aid kit"),
    (r"\b(poop|waste) bags?\b", "dog waste bags"), (r"\b(training|pee|puppy) pads?\b", "training pads"),
    (r"\bmuzzles?\b", "a muzzle"),
    (r"\bharness\w*", "a harness"), (r"\bleash\w*|\blead\b", "a leash"), (r"\bcollars?\b", "a collar"),
    (r"\bcrates?\b|\bkennels?\b", "a crate"), (r"\bcarriers?\b", "a pet carrier"),
    (r"\bbeds?\b", "a pet bed"), (r"\bcat trees?\b|\bscratch\w* posts?\b|\bscratchers?\b", "a cat tree or scratcher"),
    (r"\blitter (box|pan|tray)\w*", "a litter box"), (r"\blitter scoops?\b|\bscoops?\b", "a litter scoop"),
    (r"\b(water )?fountains?\b", "a pet water fountain"), (r"\bautomatic feeders?\b|\bfeeders?\b", "a pet feeder"),
    (r"\bbowls?\b|\bdish(es)?\b", "a pet bowl"), (r"\btoys?\b|\bballs?\b|\bchew toys?\b", "a pet toy"),
    (r"\bnail (clippers?|trimmers?|grinders?)\b", "a pet nail trimmer"),
    (r"\bclippers?\b|\btrimmers?\b", "pet clippers"), (r"\bbrush(es)?\b|\bcombs?\b|\bdeshedd\w*", "a grooming brush"),
    (r"\baquarium filters?\b|\bfilter cartridges?\b|\bcanister filters?\b", "an aquarium filter"),
    (r"\baquarium heaters?\b|\bheaters?\b", "an aquarium or terrarium heater"),
    (r"\buvb\b|\breptile (lamp|bulb|light)s?\b|\bbasking (lamp|bulb)s?\b", "a UVB or basking lamp for reptiles"),
    (r"\bwater conditioner\b|\bdechlorinator\b", "an aquarium water conditioner"),
    (r"\baquariums?\b|\bfish tanks?\b", "an aquarium"), (r"\bterrariums?\b|\bvivariums?\b", "a terrarium"),
    (r"\bbird ?cages?\b|\bperch(es)?\b", "a bird cage or perch"),
    (r"\b(hamster|small animal|rabbit|guinea pig) (cage|hutch|habitat)s?\b|\bhutch(es)?\b", "a small-animal cage"),
    (r"\btimothy hay\b|\bhay\b", "hay for rabbits and small animals"),
    (r"\bbedding\b", "small-animal bedding"),
    (r"\bpet (doors?|gates?)\b|\bdog doors?\b", "a pet door or gate"),
    (r"\b(pet|dog) (ramps?|stairs|steps)\b", "pet stairs or a ramp"),
    (r"\bsaddles?\b|\bbridles?\b|\bhalters?\b|\bhorse (blankets?|sheets?)\b|\bhoof\b", "horse tack or care"),
    (r"\b(incubators?|brooders?)\b", "an egg incubator or brooder"),
    (r"\b(waterers?|mineral blocks?|salt licks?|ear tags?)\b", "a livestock supply"),
]
PET_SUPPLY_KINDS = [(re.compile(p, re.I), kind) for p, kind in PET_SUPPLY_KINDS]
# Names that say the product is for an animal (a "collar" or "bed" alone could be anything in a general type).
FOR_AN_ANIMAL = re.compile(r"\b(pets?|dogs?|puppy|puppies|cats?|kittens?|kitty|birds?|parrots?|fish|aquarium|"
                           r"reptiles?|turtles?|rabbits?|bunny|hamsters?|guinea pigs?|ferrets?|horses?|equine|"
                           r"chickens?|poultry|livestock|cattle|goats?|sheep|terrarium|litter|flea|tick)\b", re.I)
PET_SUPPLY_Q = "What is this?"
# Things with an animal on them that are not for an animal (wall art, clothes for people, mugs ...).
NOT_A_PET_SUPPLY = re.compile(r"\b(wall art|art print|prints?|posters?|frames?|framed|canvas|t-?shirts?|shirts?|"
                              r"hoodies?|sweatshirts?|mugs?|stickers?|decals?|figurines?|ornaments?|pillow covers?|"
                              r"throw pillows?|signs?|necklaces?|earrings?|jewel\w*|socks|pajamas|phone cases?|"
                              r"wallpaper|calendars?|books?|puzzles?|bird feeders?|birdhouses?)\b", re.I)


def ps_kind(name):
    """The kind of animal care product a listing's name says ("a dog leash" -> "a leash"), or ""."""
    return next((kind for pattern, kind in PET_SUPPLY_KINDS if pattern.search(name)), "")


def ps_rows(listing):
    """The rows of one ABO listing of an animal care product: a PET_ type, or another type whose name says it is for
    an animal, with a kind PET_SUPPLY_KINDS can name; [] for everything else and for what abo_packaged_goods already
    takes (pg_rows)."""
    code = ((listing.get("product_type") or [{}])[0] or {}).get("value", "")
    country = listing.get("country") or ""
    name = abo_value(listing.get("item_name"), country)
    if not name or not listing.get("main_image_id") or NOT_SHOWN.search(name) or pg_rows(listing) \
            or NOT_A_PET_SUPPLY.search(name):
        return []
    if not (code.startswith(("PET_", "ANIMAL_")) or FOR_AN_ANIMAL.search(name)):
        return []
    if not FOR_AN_ANIMAL.search(name) and code not in ("PET_SUPPLIES", "PET_PEST_CONTROL", "ANIMAL_LITTER"):
        return []
    kind = ps_kind(name)
    if not kind:
        return []
    brand = pg_brand(listing, country)
    by = f" by {brand}" if brand and not brand_in_name(brand, name) else ""
    answer = f"This is an animal care product: {kind}{by}. The name on its listing: {sentence_end(name)}"
    rows = [{"question": PET_SUPPLY_Q, "answer": answer}]
    if brand:
        rows.append({"question": BRAND_Q, "answer": f"The brand is {brand}."})
    return [mark_child(r, name) for r in rows]


def build_abo_pet_supplies(limit):
    """The ABO animal care pack: pet and livestock supplies (leashes, collars, harnesses, muzzles, crates, carriers,
    beds, bowls, feeders, fountains, toys, grooming tools, litter boxes, flea and tick collars and spot-ons,
    dewormers, pill pockets, aquarium and terrarium supplies, bird cages, small-animal bedding and hay, horse tack,
    incubators and first aid kits), the kinds taken in turn, the USA and Canada first."""
    s, rng = session(), pass_random(98)
    by_kind, seen_images = collections.defaultdict(list), set()
    for listing in abo_listings(s):
        image = listing.get("main_image_id")
        if not image or image in seen_images:
            continue
        rows = ps_rows(listing)
        if rows:
            seen_images.add(image)
            by_kind[ps_kind(abo_value(listing.get("item_name"), listing.get("country") or ""))].append(
                (listing, rows))
    say("ABO animal care: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(by_kind.items())))
    paths = {}
    r = s.get(ABO_IMAGES, timeout=600)
    r.raise_for_status()
    for row in csv.DictReader(io.StringIO(gzip.decompress(r.content).decode("utf-8"))):
        if row["image_id"] in seen_images:
            paths[row["image_id"]] = row["path"]
    lists = []
    for kind in sorted(by_kind):
        group = sorted(by_kind[kind], key=lambda c: (c[0].get("country") or "") not in PG_NORTH_AMERICA)
        head = [c for c in group if (c[0].get("country") or "") in PG_NORTH_AMERICA]
        tail = group[len(head):]
        rng.shuffle(head)
        rng.shuffle(tail)
        lists.append(head + tail)
    items = []
    while any(lists) and len(items) < limit * 1.15:
        for group in lists:
            if group and len(items) < limit * 1.15:
                listing, rows = group.pop(0)
                path = paths.get(listing["main_image_id"])
                if not path:
                    continue
                credit = ABO_CREDIT.format(item=listing.get("item_id", ""), domain=listing.get("domain_name", ""))
                items.append((f"abo-ps-{listing['main_image_id']}.jpg".replace("+", "_"), ABO_PICTURE.format(path),
                              [dict(row, credit=credit, **abo_place(listing)) for row in rows]))
    say(f"ABO animal care: {len(items)} listings queued")
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=8)[:limit])


# ----------------------------------------------------------------- the table

ABO_PG_CREDIT = ("Amazon Berkeley Objects (Amazon.com and UC Berkeley), CC BY 4.0: data and catalogue images by "
                 "Amazon.com; dataset by Matthieu Guillaumin, Thomas Dideriksen, Kenan Deng, Himanshu Arora, Jasmine "
                 "Collins and Jitendra Malik. https://amazon-berkeley-objects.s3.amazonaws.com/index.html (each "
                 "listing credited below)")
PACKAGED_GOODS_PACKS = {
    "abo_packaged_goods": (build_abo_packaged_goods, ABO_PG_CREDIT),
    "abo_pet_supplies": (build_abo_pet_supplies, ABO_PG_CREDIT),
    "open_images_packaged_goods": (build_open_images_packaged_goods,
                                   "Google Open Images V7: labels CC BY 4.0 (https://storage.googleapis.com/"
                                   "openimages/web/index.html); each photo CC BY 2.0, its photographer credited "
                                   "below."),
}

# The limits of the workflow (pack-build.yml), from the sizes found in November 2026.
PACKAGED_GOODS_LIMITS = {
    "abo_packaged_goods": 6000,           # about 9,200 usable listings (7,350 of them in the USA and Canada)
    "open_images_packaged_goods": 500,    # 443 validation and test photos with a packaging label (before licences)
    "abo_pet_supplies": 400,              # about 350 ABO pet and animal care listings beyond packaged goods
}


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one packaged-goods pack builder.")
    parser.add_argument("key", choices=sorted(PACKAGED_GOODS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = PACKAGED_GOODS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False))
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows; "
          f"{len(build_packs.NEEDS)} set aside for a description")
    return 0


if __name__ == "__main__":
    sys.exit(main())
