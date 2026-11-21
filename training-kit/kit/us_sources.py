"""United States picture collections for the Picture Model Training Kit (American houses and rooms, streets, cars,
wild plants and animals by state, money and road signs, and packaged products) that cannot be ready-made packs
because of their licence: share-alike, non-commercial, or research use. The open ones (the Historic American
Buildings Survey houses, Commons CC0, public domain and CC BY US homes, streets, cars, money, road signs and
packaging, and iNaturalist CC0 and CC BY photos by state) are packs in packs/us_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link is in each entry).

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA, ODbL and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained
                   with them is CC BY-SA.
  "noncommercial"  CC BY-NC, BY-NC-SA and BY-NC-ND: personal use only (--personal-noncommercial).
  "research"       terms that allow copying but leave other uses to the owners, or no terms stated: personal use only
                   (--personal-research with --accept-research-terms).

Answers are fixed sentences from each source's own records (a Commons category's name, a product's name, brand and
size as people typed them into Open Food Facts, an iNaturalist community identification, a recall notice's product
name, photo caption and hazard), never written by an AI model. Nobody is named.

Safety (packs/SOURCE-RULES.md): no sexual content (files and records whose words name nudity, underwear, swimwear or
sexual products are left out); children only in everyday clothed scenes, and every row whose words name a child is
marked "child". Recall photos of children's clothing and sleepwear are left out.

The collections (US_SOURCES):
  share-alike
    commons_us_sa          Wikimedia Commons: the US house, house-style, room, street, money, road-sign and packaging
                           categories of the open packs, files under CC BY-SA or GFDL, with the category's question and
                           the file's own caption. "What kind of house is this?" -> "It is a Victorian house ..."
    openfacts_us           Open Food Facts (photos CC BY-SA 3.0, data ODbL 1.0;
                           https://world.openfoodfacts.org/terms-of-use): front photos of products sold in the
                           United States (countries_tags en:united-states) with a US barcode (a UPC, GS1 prefixes
                           000 to 139, so European products also sold there are left out), with the name, brand and
                           size people typed in: "What product is this?" -> "This is Honey Nut Cheerios by General
                           Mills, 10.8 oz." Read through off_dump.py (the product database on Hugging Face, the
                           photos on AWS Open Data), never Open Food Facts' websites, which block AI crawlers; Open
                           Beauty Facts and Open Products Facts are no longer read (same block, no open photo
                           route). The world-wide entry openfoodfacts takes the most scanned products of every
                           country; a product in both is saved once under the same file name in each.
    inaturalist_us_sa      iNaturalist research-grade observations in each US state whose photo is CC BY-SA (through
                           GBIF and the iNaturalist Open Dataset, inat_gbif.py; such photos are few).
  noncommercial
    inaturalist_us_nc      The same, photos under CC BY-NC, BY-NC-SA or BY-NC-ND (most of iNaturalist's photos).
  research
    cpsc_recalls           US Consumer Product Safety Commission recall notices (saferproducts.gov Recalls API): the
                           photos of recalled products, with the product's name from the photo's own caption, the
                           maker, and the hazard the notice gives. "What product is this?" -> "This is the Black
                           Diamond Vision Harness." / "Why was this product recalled?" CPSC's privacy and website
                           policy (https://www.cpsc.gov/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy)
                           says "You may freely copy and distribute recall notices, including photographs of recalled
                           items, without permission. Any other use of photographs found in recall notices and
                           elsewhere on CPSC websites may require permission from a copyright holder." Many recall
                           photos come from the firms, so training on them is personal use only until CPSC (or each
                           firm) agrees; CPSC is also in US_PERMISSION_CANDIDATES.
    freiburg_groceries     Freiburg Groceries Dataset (Jund, Abdo, Eitel and Burgard, University of Freiburg, 2016;
                           github.com/PhilJd/freiburg_groceries_dataset): 5,000 phone photos of packaged groceries on
                           shelves and in homes, in 25 kinds (pasta, coffee, cereal, juice, milk, tea ...). No
                           licence is stated. "What kind of product is this?" -> "It is a packet of pasta."

Needing sign-up (US_SIGN_UP has the links), looked at and not included (US_NOT_INCLUDED, with the reason of each),
and the owners of big product-photo and house-photo collections to ask for permission (US_PERMISSION_CANDIDATES:
the organisation, what they have, their terms line and contact page; nothing here downloads from them).

US_PICTURE_MAKING_OK holds the collections without people: openfacts_us and freiburg_groceries (product photos). Not
the Commons entry (street photos), iNaturalist (some photos show people's hands) or the recall photos (some show
children's products in use).

    python kit/us_sources.py cpsc_recalls --cap 8     (a quick check; prints a few rows)
"""

import collections
import json
import os
import random
import re
import time

from extra_sources import get_json, off_name, per_label, research, save, say, stream_tar
from home_sources import commons_sa_items, facts_image, kind_rows, FACT_SITES, FACTS_FIELDS, FACTS_CREDIT
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import Source, clean

WHAT_Q = "What is this?"
HOUSE_Q = "What kind of house is this?"
ROOM_Q = "What room is this?"
PLACE_Q = "What kind of place is this?"
MONEY_Q = "What money is this?"
SIGN_Q = "What does this road sign mean?"
PRODUCT_Q = "What product is this?"
KIND_Q = "What kind of product is this?"
# Words that leave a record out: nudity, underwear, swimwear and sexual products (the safety rules).
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|bathing suits?|underwear|lingerie|bras?|briefs|nude|naked|topless|"
                       r"sexy|sexual\w*|erotic\w*|adult toys?|vibrators?|condoms?|lubricants?)\b"
                       # criminal-investigation evidence photos (FBI photos of the Epstein properties are filed in
                       # Commons room categories)
                       r"|epstein|\bEFTA\d+|crime scenes?|evidence photo\w*|mug ?shots?|\bautops\w*", re.I)
CHILD_CLOTHES = re.compile(r"\b(sleepwear|pajamas|pyjamas|nightgowns?|robes?|garments?|clothing|onesies?|"
                           r"bodysuits?|hoodies?|sweatshirts?|jackets?|dresses|costumes?)\b", re.I)
STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
          "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
          "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
          "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
          "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
          "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]


def a_or_an(word):
    """ "a" or "an" before a word."""
    return "an" if word[:1].lower() in "aeiou" else "a"


# ----------------------------------------------------------------- share-alike: Commons US categories

# The categories of packs/us_packs.py (the car categories are not here: their answers come from each file's model
# category, which this simpler share-alike reader does not look at).
US_SA = (
    [(f"Houses in {state}", WHAT_Q, f"This is a house in {state}, USA.", True) for state in STATES]
    + [("Victorian houses in the United States", HOUSE_Q, "It is a Victorian house.", True),
       ("Colonial Revival houses in the United States", HOUSE_Q, "It is a Colonial Revival house.", True),
       ("Greek Revival houses in the United States", HOUSE_Q, "It is a Greek Revival house.", True),
       ("Tudor Revival houses in the United States", HOUSE_Q, "It is a Tudor Revival house.", True),
       ("Italianate houses in the United States", HOUSE_Q, "It is an Italianate house.", True),
       ("Federal style houses in the United States", HOUSE_Q, "It is a Federal-style house.", True),
       ("Log cabins in the United States", HOUSE_Q, "It is a log cabin.", True),
       ("Mobile homes in the United States", HOUSE_Q, "It is a mobile home (a manufactured home).", True),
       ("Townhouses in the United States", HOUSE_Q, "It is a townhouse (a row house).", True),
       ("Shotgun houses", HOUSE_Q, "It is a shotgun house: a narrow house one room wide.", True),
       ("Farmhouses in the United States", HOUSE_Q, "It is a farmhouse.", True),
       ("Home kitchens in the United States", ROOM_Q, "This is a kitchen.", True),
       ("Living rooms in the United States", ROOM_Q, "This is a living room.", True),
       ("Bedrooms in the United States", ROOM_Q, "This is a bedroom.", True),
       ("Bathrooms in the United States", ROOM_Q, "This is a bathroom.", True),
       ("Dining rooms in the United States", ROOM_Q, "This is a dining room.", True),
       ("Streets in New York City", PLACE_Q, "This is a street in New York City, USA.", True),
       ("Streets in Chicago", PLACE_Q, "This is a street in Chicago, USA.", True),
       ("Streets in San Francisco", PLACE_Q, "This is a street in San Francisco, USA.", True),
       ("Streets in Los Angeles", PLACE_Q, "This is a street in Los Angeles, USA.", True),
       ("Streets in Boston", PLACE_Q, "This is a street in Boston, USA.", True),
       ("Streets in Seattle", PLACE_Q, "This is a street in Seattle, USA.", True),
       ("Streets in New Orleans", PLACE_Q, "This is a street in New Orleans, USA.", True),
       ("Streets in Washington, D.C.", PLACE_Q, "This is a street in Washington, D.C., USA.", True),
       ("1 United States dollar banknotes", MONEY_Q, "This is a US one-dollar bill.", True),
       ("5 United States dollar banknotes", MONEY_Q, "This is a US five-dollar bill.", True),
       ("10 United States dollar banknotes", MONEY_Q, "This is a US ten-dollar bill.", True),
       ("20 United States dollar banknotes", MONEY_Q, "This is a US twenty-dollar bill.", True),
       ("50 United States dollar banknotes", MONEY_Q, "This is a US fifty-dollar bill.", True),
       ("100 United States dollar banknotes", MONEY_Q, "This is a US hundred-dollar bill.", True),
       ("United States cents", MONEY_Q, "This is a US one-cent coin (a penny).", True),
       ("United States nickels", MONEY_Q, "This is a US five-cent coin (a nickel).", True),
       ("United States dimes", MONEY_Q, "This is a US ten-cent coin (a dime).", True),
       ("United States quarters", MONEY_Q, "This is a US 25-cent coin (a quarter).", True),
       ("Stop signs in the United States", SIGN_Q, "It is a stop sign: stop completely, then go on when it is "
                                                   "safe.", True),
       ("Yield signs in the United States", SIGN_Q, "It is a yield sign: give way to traffic on the road you are "
                                                    "joining.", True),
       ("Speed limit signs in the United States", SIGN_Q, "It is a speed limit sign: the highest speed allowed, "
                                                          "in miles per hour.", True),
       ("Pedestrian crossing signs in the United States", SIGN_Q, "It is a pedestrian crossing sign.", True),
       ("Packaged food", WHAT_Q, "This is packaged food.", True),
       ("Beverage cans", WHAT_Q, "This is a drink can.", True),
       ("Egg cartons", WHAT_Q, "This is an egg carton.", True),
       ("Milk retail containers", WHAT_Q, "This is a milk container.", True),
       ("Cardboard food boxes", WHAT_Q, "This is a cardboard food box.", True),
       ("Candy packaging", WHAT_Q, "This is sweets (candy) packaging.", True),
       ("Blister packs", WHAT_Q, "This is a blister pack.", True),
       ("Supermarket shelves", WHAT_Q, "This is a supermarket shelf, stocked with products.", True),
       ("Supermarkets in the United States", PLACE_Q, "This is a supermarket in the USA.", True),
       ("Grocery stores in the United States", PLACE_Q, "This is a grocery store in the USA.", True)])


def prepare_commons_us_sa(source, data_dir, work, cap):
    """Wikimedia Commons US categories, files under CC BY-SA or GFDL (home_sources.commons_sa_items: the categories
    share the cap; rows whose words name a child are marked "child"; files whose words name nudity are left out).
    Files whose words name swimwear or underwear are left out too."""
    items = commons_sa_items(US_SA, cap, source.test, "us-sa")
    left_out = {i[0] for i in items if NOT_SHOWN.search(f"{i[0]} {i[2]['answer']}")}    # every row of that file
    items = [i for i in items if i[0] not in left_out]
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: Open ... Facts, sold in the USA

# Grocery categories common in US shops (Open Food Facts tags).
US_FOOD_CATEGORIES = ("breakfast-cereals", "cookies", "crackers", "chips-and-fries", "candies", "chocolates",
                      "peanut-butters", "jams", "sodas", "fruit-juices", "coffees", "teas", "pastas",
                      "pasta-sauces", "canned-soups", "canned-vegetables", "canned-beans", "rices", "breads",
                      "cheeses", "yogurts", "milks", "plant-based-milks", "ice-creams", "frozen-pizzas",
                      "frozen-meals", "condiments", "salad-dressings", "snack-bars", "nuts", "spices", "sugars",
                      "flours", "baby-foods", "pet-foods", "energy-drinks", "waters", "popcorn")
US_FACTS_CREDIT = "Open Food Facts contributors, product {code}: photos CC BY-SA 3.0, data ODbL 1.0, " \
                  "https://world.openfoodfacts.org/product/{code}"


def us_barcode(code):
    """True when a product's barcode is a US or Canadian one (a UPC: GS1 prefixes 000 to 139), so a product sold in
    the USA but made for Europe ("Confiture Abricot by Bonne Maman", tagged as sold in the USA too) is left out."""
    code = str(code or "")
    return code.isdigit() and len(code) in (12, 13) and code.zfill(13)[:3] <= "139"


def off_us_front(code, images):
    """The AWS Open Data address of an Open Food Facts product's chosen English front photo, or "" (off_dump)."""
    import off_dump
    return off_dump.photo_url(code, images, "front", "en")


def us_food_items(work, want):
    """[(file name, address, row)] for Open Food Facts products sold in the USA with a US barcode (us_barcode), the
    most scanned of each grocery category first, an even share of each. Read from the product database's slim copy
    (off_dump), never from Open Food Facts' websites."""
    import off_dump
    per = per_label(want, len(US_FOOD_CATEGORIES))
    wanted = {f"en:{c}": c for c in US_FOOD_CATEGORIES}

    def labels(hit):
        """The grocery categories of a product sold in the USA with a US barcode, an English front photo and a
        name that is not left out."""
        if "en:united-states" not in hit["countries_tags"] or not us_barcode(hit["code"]) \
                or not off_us_front(hit["code"], hit["images"]):
            return ()
        answer = off_name(hit)
        if not answer or NOT_SHOWN.search(answer):
            return ()
        return [wanted[t] for t in hit["categories_tags"] if t in wanted]

    best = off_dump.top_by_label(work, labels, per)
    items = []
    for category in US_FOOD_CATEGORIES:
        hits = best.get(category, [])
        for hit in hits:
            items.append((f"off-front-{hit['code']}.jpg", off_us_front(hit["code"], hit["images"]),
                          {"question": PRODUCT_Q, "answer": off_name(hit), "split": "",
                           "credit": US_FACTS_CREDIT.format(code=hit["code"]), "place": "USA",
                           "place_kind": "market"}))
        say(f"  Open Food Facts (USA) {category}: {len(hits)} products")
    return items


def us_site_items(site, want):
    """[(file name, address, row)] for Open Beauty Facts or Open Products Facts products sold in the USA: "What
    product is this?" and the "What kind of product is this?" and "Is this A or B?" rows its categories allow.
    Not used: those sites block AI crawlers (off_dump.NOT_BUILT), so this stops at once; the code is kept."""
    import off_dump
    off_dump.refuse(f"Open {site.capitalize()} Facts (USA)")
    base, _, name, _ = FACT_SITES[site]
    hits, page = [], 1
    while len(hits) < want * 2 and page <= 10:
        try:
            data = get_json(f"{base}/api/v2/search", {"countries_tags_en": "united-states", "page_size": 100,
                                                      "page": page, "sort_by": "unique_scans_n",
                                                      "fields": FACTS_FIELDS})
        except RuntimeError:
            break
        batch = data.get("products") or []
        hits += batch
        time.sleep(1)
        if len(batch) < 100:
            break
        page += 1
    items = []
    for hit in hits:
        if len({i[0] for i in items}) >= want:
            break
        url = facts_image(site, hit.get("code") or "", hit.get("images") or {}, "front", "en") \
            if us_barcode(hit.get("code")) else ""
        answer = off_name(hit)
        if not url or not answer or NOT_SHOWN.search(answer):
            continue
        extra = {"credit": FACTS_CREDIT.format(site=name, code=hit["code"], base=base), "split": "",
                 "place": "USA", "place_kind": "market"}
        file_name = f"{site}-front-{hit['code']}.jpg"
        items.append((file_name, url, dict(extra, question=PRODUCT_Q, answer=answer)))
        items += [(file_name, url, dict(extra, **row)) for row in kind_rows(site, hit)]
    say(f"  {name} (USA): {len({i[0] for i in items})} products")
    return items


def prepare_openfacts_us(source, data_dir, work, cap):
    """Front photos of Open Food Facts products sold in the USA, with their name, brand and size; the USA as the
    place of sale. Open Beauty Facts and Open Products Facts (us_site_items) used to give a quarter: they block AI
    crawlers and have no open bulk route for their photos, so the food products now fill the entry."""
    want = int((cap + source.test) * 1.15)
    items = us_food_items(work, want)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- iNaturalist, US states, other licences

INAT_GROUPS = [("Plantae", "What plant is this?"), ("Fungi", "What mushroom or fungus is this?"),
               ("Insecta", "What insect is this?"), ("Aves", "What bird is this?"), ("Mammalia", "What animal is this?"),
               ("Reptilia", "What animal is this?"), ("Amphibia", "What animal is this?"),
               ("Arachnida", "What is this creature?"), ("Mollusca", "What is this creature?"),
               ("Actinopterygii", "What fish is this?")]
INAT_LICENCES = {"cc-by-sa": "CC BY-SA", "cc-by-nc": "CC BY-NC", "cc-by-nc-sa": "CC BY-NC-SA",
                 "cc-by-nc-nd": "CC BY-NC-ND"}


def inat_us_rows(source, data_dir, licences, prefix):
    """Rows for iNaturalist research-grade observations in each US state whose photo's own licence is one of
    licences: the states and groups take turns, one page each. The state is the place. The records come from GBIF
    and the photos from the iNaturalist Open Dataset (inat_gbif.py); iNaturalist's website and API are never read."""
    import inat_gbif
    want = int((source.cap + source.test) * 1.1)
    states = inat_gbif.regions("US", STATES)
    items = inat_gbif.region_items("US", states, INAT_GROUPS, licences, want, prefix, lambda s: f"{s}, USA")
    say(f"  iNaturalist on GBIF (USA, {', '.join(INAT_LICENCES[x] for x in licences)}): {len(items) // 2} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


def prepare_inaturalist_us_sa(source, data_dir, work, cap):
    """iNaturalist US photos under CC BY-SA."""
    return inat_us_rows(source, data_dir, ("cc-by-sa",), "inatus-sa")


def prepare_inaturalist_us_nc(source, data_dir, work, cap):
    """iNaturalist US photos under CC BY-NC, BY-NC-SA or BY-NC-ND."""
    return inat_us_rows(source, data_dir, ("cc-by-nc", "cc-by-nc-sa", "cc-by-nc-nd"), "inatus-nc")


# ----------------------------------------------------------------- research: CPSC recall photos

CPSC_API = "https://www.saferproducts.gov/RestWebServices/Recall"
CPSC_TERMS = "https://www.cpsc.gov/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy"
# Captions that show only a part, a label or a code, not the product.
CPSC_DETAIL = re.compile(r"\b(label|lot|code|number|location|date|tag|stamp|close-?up|detail|serial|upc|barcode|"
                         r"underside|bottom of|back of|inside of|affected|warning|packaging only)\b", re.I)


def cpsc_product(caption, record):
    """The product's name from a photo's own caption ("Recalled Black Diamond Vision Harness" -> "the Black Diamond
    Vision Harness"), else the record's first product name; ""."""
    text = clean(re.sub(r"^\s*(the\s+)?recalled\s+", "", caption or "", flags=re.I)).strip(" .")
    if not text:
        text = clean(((record.get("Products") or [{}])[0] or {}).get("Name")).strip(" .")
    return f"the {text}" if text and not text.lower().startswith(("the ", "a ", "an ")) else text


def cpsc_maker(record):
    """ "BMC Switzerland AG, of Switzerland" -> "BMC Switzerland AG"; "" when the notice names no maker."""
    for group in ("Manufacturers", "Importers", "Distributors"):
        for m in record.get(group) or []:
            name = clean(m.get("Name")).split(", of ")[0].strip(" .,")
            if name:
                return name
    return ""


def cpsc_year_items(year, want):
    """[(file name, address, row)] from one year's CPSC recall notices: each photo whose caption names the product
    (not a label or a lot number), with "What product is this?" and "Why was this product recalled?"."""
    items = []
    try:
        records = get_json(CPSC_API, {"format": "json", "RecallDateStart": f"{year}-01-01",
                                      "RecallDateEnd": f"{year}-12-31"})
    except RuntimeError:
        return items
    random.Random(year).shuffle(records)
    for record in records:
        if len({i[0] for i in items}) >= want:
            break
        words = " ".join([clean(record.get("Title")), clean(record.get("Description"))])
        if NOT_SHOWN.search(words):
            continue
        child = bool(CHILD_WORDS.search(words))
        if child and CHILD_CLOTHES.search(words):        # children's clothing and sleepwear: left out
            continue
        hazard = clean(((record.get("Hazards") or [{}])[0] or {}).get("Name"))
        maker = cpsc_maker(record)
        origin = clean(((record.get("ManufacturerCountries") or [{}])[0] or {}).get("Country"))
        origin = "USA" if origin.lower() in ("united states", "united states of america", "usa", "us") else origin
        credit = (f"US Consumer Product Safety Commission recall {record.get('RecallNumber')}: "
                  f"{clean(record.get('Title'))[:120]}, {record.get('URL')}")
        for n, image in enumerate((record.get("Images") or [])[:3]):
            caption, url = clean(image.get("Caption")), image.get("URL") or ""
            product = cpsc_product(caption, record)
            if not url or not product or CPSC_DETAIL.search(caption) or NOT_SHOWN.search(caption):
                continue
            answer = f"This is {product}" + (f", made by {maker}" if maker and maker.lower() not in
                                             product.lower() else "") + "."
            base = {"split": "", "credit": credit, **({"child": True} if child else {}),
                    **({"place": origin, "place_kind": "origin"} if origin else {})}
            name = f"cpsc-{record.get('RecallNumber')}-{n}.jpg"
            items.append((name, url, dict(base, question=PRODUCT_Q, answer=answer)))
            if hazard:
                items.append((name, url, dict(base, question="Why was this product recalled?",
                                              answer=f"It was recalled in the USA because {hazard[:1].lower()}{hazard[1:].rstrip('.')}.")))
    return items


def prepare_cpsc_recalls(source, data_dir, work, cap):
    """CPSC recall photos from the last ten years, an even share of each year, gently (one request a year)."""
    want = int((cap + source.test) * 1.2)
    this_year = time.gmtime().tm_year
    items = []
    for year in range(this_year - 9, this_year + 1):
        found = cpsc_year_items(year, per_label(want, 10))
        say(f"  CPSC recalls {year}: {len({i[0] for i in found})} photos")
        items += found
        time.sleep(2)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=3)


# ----------------------------------------------------------------- research: Freiburg Groceries

FREIBURG = ("http://aisdatasets.informatik.uni-freiburg.de/freiburg_groceries_dataset/"
            "freiburg_groceries_dataset.tar.gz")
FREIBURG_CREDIT = ("The Freiburg Groceries Dataset (Philipp Jund, Nichola Abdo, Andreas Eitel and Wolfram Burgard, "
                   "University of Freiburg, 2016), https://github.com/PhilJd/freiburg_groceries_dataset; no licence "
                   "stated")
FREIBURG_KINDS = {"BEANS": "a tin of beans", "CAKE": "a packaged cake", "CANDY": "a bag of sweets (candy)",
                  "CEREAL": "a box of breakfast cereal", "CHIPS": "a bag of crisps (chips)",
                  "CHOCOLATE": "a bar of chocolate", "COFFEE": "a packet of coffee", "CORN": "a tin of sweetcorn",
                  "FISH": "a tin of fish", "FLOUR": "a bag of flour", "HONEY": "a jar of honey",
                  "JAM": "a jar of jam", "JUICE": "a carton or bottle of juice", "MILK": "a carton of milk",
                  "NUTS": "a bag of nuts", "OIL": "a bottle of cooking oil", "PASTA": "a packet of pasta",
                  "RICE": "a packet of rice", "SODA": "a can or bottle of soft drink (soda)",
                  "SPICES": "a jar or packet of spices", "SUGAR": "a packet of sugar", "TEA": "a box of tea",
                  "TOMATO_SAUCE": "a jar or tin of tomato sauce", "VINEGAR": "a bottle of vinegar",
                  "WATER": "a bottle of water"}


def prepare_freiburg_groceries(source, data_dir, work, cap):
    """The Freiburg Groceries photos, read straight from its 540 MB archive (images/<KIND>/<KIND>0001.png): an even
    share of each of the 25 kinds. "What kind of product is this?" -> "It is a packet of pasta." """
    per = per_label(cap + source.test, len(FREIBURG_KINDS))
    got = collections.Counter()
    target = os.path.join(data_dir, source.key)
    rows = []

    def take(member, tar):
        """Keep a photo when its kind still needs some; True once every kind has enough."""
        parts = member.name.split("/")
        kind = parts[-2].upper() if len(parts) >= 2 else ""
        if member.isfile() and kind in FREIBURG_KINDS and got[kind] < per \
                and member.name.lower().endswith((".png", ".jpg")):
            path = save(f"freiburg-{kind.lower()}-{parts[-1].rsplit('.', 1)[0]}", tar.extractfile(member).read(),
                        target)
            if path:
                got[kind] += 1
                rows.append({"picture": path, "question": KIND_Q, "answer": f"It is {FREIBURG_KINDS[kind]}.",
                             "split": "", "credit": FREIBURG_CREDIT})
        return all(got[k] >= per for k in FREIBURG_KINDS)

    stream_tar(FREIBURG, take, "the Freiburg Groceries archive (540 MB)")
    say(f"  Freiburg Groceries: {len(rows)} photos")
    return rows


# ----------------------------------------------------------------- the table

US_SOURCES = [
    # ---- share-alike
    Source("commons_us_sa", "Wikimedia Commons: US houses and rooms, streets, money, road signs and packaging, files "
                            "under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 3000, 30, prepare_commons_us_sa, "about 400 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("openfacts_us", "Open Food Facts: products sold in the USA, their name, brand and size (share-alike)",
           "Photos CC BY-SA 3.0, database ODbL 1.0 (https://world.openfoodfacts.org/terms-of-use)",
           "Open Food Facts contributors, photos CC BY-SA 3.0, data ODbL 1.0, each product credited in its row, "
           "https://world.openfoodfacts.org", "share-alike", 3000, 30,
           prepare_openfacts_us, "about 450 MB of product records (read once, shared by the Open Food Facts "
           "entries) and 1.2 GB of photos", terms="https://world.openfoodfacts.org/terms-of-use",
           terms_summary="CC BY-SA 3.0 photos and an ODbL database: use with credit, and anything made from them "
                         "keeps the same licence."),
    Source("inaturalist_us_sa", "iNaturalist: wild plants and animals in each US state, photos under CC BY-SA "
                                "(share-alike)",
           "Each photo CC BY-SA (its observation page; https://www.inaturalist.org/pages/terms)",
           "iNaturalist contributors, CC BY-SA, each credited in its row, https://www.inaturalist.org",
           "share-alike", 1000, 10, prepare_inaturalist_us_sa, "about 150 MB",
           terms="https://www.inaturalist.org/pages/terms",
           terms_summary="CC BY-SA: use with credit, and anything made from it keeps the same licence."),
    # ---- non-commercial
    Source("inaturalist_us_nc", "iNaturalist: wild plants and animals in each US state, photos under CC BY-NC "
                                "(personal use)",
           "Each photo CC BY-NC, BY-NC-SA or BY-NC-ND (its observation page)",
           "iNaturalist contributors, CC BY-NC (and NC-SA, NC-ND), each credited in its row, "
           "https://www.inaturalist.org", "noncommercial", 5000, 30, prepare_inaturalist_us_nc, "about 700 MB",
           terms="https://www.inaturalist.org/pages/terms",
           terms_summary="CC BY-NC: use with credit, not for commercial purposes."),
    # ---- research
    Source("cpsc_recalls", "US product recall photos (Consumer Product Safety Commission): which product, and why it "
                           "was recalled (personal use)",
           "Recall notices and their photos may be copied and distributed freely; other uses of the photos may need "
           "the copyright holder's permission (CPSC website policy)",
           "US Consumer Product Safety Commission recall notices (saferproducts.gov Recalls API), each recall "
           "credited in its row, https://www.cpsc.gov/Recalls", "research", 3000, 30, prepare_cpsc_recalls,
           "about 600 MB", terms=CPSC_TERMS,
           terms_summary=research("CPSC: 'You may freely copy and distribute recall notices, including photographs "
                                  "of recalled items, without permission. Any other use of photographs found in "
                                  "recall notices and elsewhere on CPSC websites may require permission from a "
                                  "copyright holder.' Many photos come from the recalling firms.")),
    Source("freiburg_groceries", "Freiburg Groceries: 25 kinds of packaged groceries (personal use)",
           "No licence stated (github.com/PhilJd/freiburg_groceries_dataset)", FREIBURG_CREDIT, "research", 2500,
           25, prepare_freiburg_groceries, "540 MB (read straight from the archive)",
           terms="https://github.com/PhilJd/freiburg_groceries_dataset",
           terms_summary=research("No licence is stated for the photos.")),
]

# The collections a picture-making model may learn from: product photos without people.
US_PICTURE_MAKING_OK = {"openfacts_us", "freiburg_groceries"}

US_SIGN_UP = {
    "RPC, Retail Product Checkout (Megvii, 2019; CC BY-NC-SA 4.0 as published)":
        "https://rpc-dataset.github.io : download from Kaggle (diyer22/retail-product-checkout-dataset, a Kaggle "
        "account) or Baidu; 83,739 photos of 200 kinds of packaged product on checkout trays, boxed (already listed "
        "in personal_sources.py).",
    "RP2K, Retail Product 2K (Pinlan, 2020)":
        "https://www.pinlandata.com/rp2k_dataset : 500,000 shelf crops of 2,000 products from Chinese shops; the "
        "download page asks for a form, and no licence for the photos is stated (research).",
    "Locount (Institute of Software, Chinese Academy of Sciences)":
        "https://isrc.iscas.ac.cn/gitlab/research/locount-dataset : 50,394 shelf photos with products counted; the "
        "README asks people to write to the authors (libo@iscas.ac.cn).",
    "Unitail (University of Pittsburgh, 2022)":
        "https://unitedretail.github.io : 1.8 million product boxes on 12,244 shelf photos, with product text; "
        "downloaded through a request form; no licence stated (research).",
    "Products-10K (JD.com and Peking University, 2020)":
        "https://products-10k.github.io : 150,000 photos of 10,000 JD.com products; the download needs a form, "
        "and the labels are product numbers only.",
    "MVTec D2S, Densely Segmented Supermarket (CC BY-NC-SA 4.0)":
        "https://www.mvtec.com/company/research/datasets/mvtec-d2s : a download form; 21,000 photos of 60 kinds of "
        "packaged groceries, outlined.",
    "Roboflow Universe retail-shelf and grocery sets":
        "https://universe.roboflow.com : a free Roboflow account and API key (search 'grocery', 'retail shelf', "
        "'SKU'); check each set's licence and where its photos came from.",
    "GS1 US Data Hub and product-content syndicators (Syndigo, 1WorldSync, Salsify)":
        "Product photos with names, brands and sizes from the makers themselves; a paid business account, and the "
        "images are licensed to retailers only. Also in US_PERMISSION_CANDIDATES.",
    "Flickr US government photostreams (US Forest Service, BLM, USFWS, NPS, NOAA)":
        "https://www.flickr.com/services/api : a free Flickr API key; most of these photos are US government work "
        "(public domain). Already listed in documentary_sources.py.",
}

US_NOT_INCLUDED = {
    "Walmart, Target, Kroger, Costco, Amazon, Home Depot, Lowe's, Best Buy, Instacart (product photos)":
        "the owner asked; declined: these shops' terms forbid scraping and copying their pages, and the product "
        "photos are the makers' or the shops' copyright. Target's terms, for example, forbid users to 'Make any use "
        "of data extraction, scraping, mining or other data gathering tools' and to 'create a database by "
        "systematically downloading or storing Site content' (https://www.target.com/c/terms-conditions/-/N-4sr7l). "
        "Amazon's own open photos are already the abo_products pack (Amazon Berkeley Objects, CC BY 4.0). The shops "
        "are in US_PERMISSION_CANDIDATES.",
    "Zillow, Redfin, Realtor.com, Trulia (house listings)":
        "the owner asked; declined: their terms forbid scraping, the listing photos belong to the photographers and "
        "estate agents, and the interiors are people's private homes. The open house photos come from the Historic "
        "American Buildings Survey and Commons instead.",
    "SKU-110K (Trax, CVPR 2019)":
        "'The dataset is provided for the exclusive use by the recipient and solely for academic and non-commercial "
        "purposes' (github.com/eg4000/SKU110K_CVPR19); 11,762 shelf photos (13 GB) with boxes only, no product "
        "names; personal_sources.py already leaves it out for that reason.",
    "GroZi-120 and GroZi-3.2k (UC San Diego)": "their download sites do not answer (as in personal_sources.py).",
    "HoloSelecta": "a small set of vending-machine shelves whose download link no longer answers.",
    "PACO (Meta, parts and attributes of common objects)":
        "its photos are LVIS (COCO) and Ego4D frames, not packaged products; COCO's open photos are already used "
        "elsewhere and Ego4D needs a signed licence.",
    "Open Images 'Packaged goods', 'Box', 'Bottle' labels":
        "already taken by open_images_objects and open_images_tech (the labels are not repeated here).",
    "US Fish and Wildlife Service National Digital Library and NOAA Photo Library (public domain)":
        "public domain, but fws.gov/search/images has no public search service and www.noaa.gov/digital-library "
        "refused this machine (403) again in November 2026, as documentary_packs.py notes; their Flickr copies are "
        "in US_SIGN_UP.",
    "USDA PLANTS database images": "its image service (plantsservices.sc.egov.usda.gov) did not answer (504) in "
                                   "November 2026, and many of its photos are credited to outside photographers "
                                   "with their own copyright; usda_ars already has the USDA's own photos.",
    "US Mint coin images and Bureau of Engraving and Printing banknote images (public domain)":
        "usmint.gov refused this machine (403); US coins and banknotes come from Commons instead (commons_us_money).",
    "FHWA MUTCD sign images (public domain)": "the same MUTCD signs are on Commons with their numbers "
                                             "(us_road_signs), which a program can list; the FHWA site has only PDF "
                                             "and a few web pages.",
    "Smithsonian NMNH (National Museum of Natural History) open-access images (CC0)":
        "nearly all are museum specimens (pressed plants, skins, jars), not living things; the smithsonian pack "
        "takes the other museums, and the living-things photos come from iNaturalist.",
    "Smithsonian NMAH and Library of Congress packaging and advertising":
        "already in the smithsonian pack (NMAH records with their own descriptions) and loc_highsmith; no separate "
        "list of packaging records with a description a program can read.",
    "FDA recall photos (fda.gov)": "the photos in FDA recall notices are supplied by the recalling companies, who "
                                   "keep their rights; FDA's site has no list of them a program can read.",
    "USDA FoodData Central and Energy Star product finder": "product data only, no product photos.",
    "UPCitemdb, Barcode Lookup and other barcode sites": "their terms forbid copying their data and images in bulk.",
}

# Owners of big product-photo and house-photo collections whose terms do not allow this use: candidates for a
# permission letter (as permission_sources.py). Nothing here downloads anything. Checked November 2026.
US_PERMISSION_CANDIDATES = {
    "US Consumer Product Safety Commission (CPSC)":
        "Has: about 10,000 recall notices with photos of the products, their names, makers and hazards "
        "(saferproducts.gov Recalls API; the kit's cpsc_recalls entry). Terms line (https://www.cpsc.gov/About-"
        "CPSC/Policies-Statements-and-Directives/Privacy-Policy): 'You may freely copy and distribute recall "
        "notices, including photographs of recalled items, without permission. Any other use of photographs found "
        "in recall notices and elsewhere on CPSC websites may require permission from a copyright holder.' Ask "
        "(whether describing the photos for blind people, as training data, is fine, and which photos are CPSC's "
        "own): https://www.cpsc.gov/About-CPSC/Contact-Information (Office of Communications).",
    "Target Corporation":
        "Has: product photos of hundreds of thousands of products with names, brands and sizes. Terms line "
        "(https://www.target.com/c/terms-conditions/-/N-4sr7l): users may not 'Make any use of data extraction, "
        "scraping, mining or other data gathering tools' or 'create a database by systematically downloading or "
        "storing Site content'. Ask: Target corporate communications, https://corporate.target.com/press (media "
        "contact form), or Guest Relations, https://www.target.com/guest-services.",
    "Walmart Inc.":
        "Has: product photos with names, brands and sizes (walmart.com) and Walmart's open-source teams. Terms: "
        "https://www.walmart.com/help/article/walmart-com-terms-of-use/3b75080af40340d6bbd596f116fae5a0 (the page "
        "answered this machine only with a robot check, so its exact line is not quoted here; it is known to forbid "
        "robots, scraping and copying content). Ask: https://corporate.walmart.com/news/media-contacts or the "
        "Walmart Accessibility Center of Excellence through https://corporate.walmart.com/purpose/belonging/"
        "accessibility.",
    "Zillow Group":
        "Has: millions of house photos, outside and inside, with the kind of house and its rooms. Terms: "
        "https://www.zillow.com/z/corp/terms/ (the page refused this machine, 403, so its exact line is not quoted "
        "here; it forbids scraping, and the listing photos belong to agents and photographers and show private "
        "homes). Ask: https://www.zillow.com/corp/About.htm (press and partnerships); Zillow's own photos of "
        "show homes only, never private listings.",
    "The Kroger Co.":
        "Has: product photos with names, brands and sizes (kroger.com) and the 84.51° product data. Terms: "
        "https://www.kroger.com/i/terms (not read from this machine; to check before writing). Ask: "
        "https://www.thekrogerco.com/contact-us/.",
    "Amazon (beyond the Amazon Berkeley Objects set)":
        "Has: product photos and listings. Terms (https://www.amazon.com/gp/help/customer/display.html?nodeId="
        "508088, Conditions of Use): no 'use of data mining, robots, or similar data gathering and extraction "
        "tools' (to check the wording before writing). The open part is already the abo_products pack. Ask: "
        "Amazon Science (https://www.amazon.science/contact) about a wider Amazon Berkeley Objects release.",
    "Syndigo, 1WorldSync and GS1 US (product-content syndicators)":
        "Have: the makers' own product photos (front of pack, nutrition and ingredient panels) for most US grocery "
        "and household products. Terms: licensed to retailers and brand owners only (business contracts). Ask: "
        "https://www.syndigo.com/contact-us/, https://1worldsync.com/contact-us/, https://www.gs1us.org/contact-us "
        "(an accessibility or research licence).",
    "Procter & Gamble, General Mills, Kraft Heinz, PepsiCo, Unilever (makers' press kits)":
        "Have: high-resolution product and packaging photos in their newsrooms, for editorial use only (each press "
        "page says the images are for media use). Ask each newsroom's media contact for permission to use the "
        "pack shots to teach a describer for blind people.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one US collection.")
    parser.add_argument("key", choices=[s.key for s in US_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in US_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="us-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
