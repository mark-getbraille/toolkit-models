"""Practical home-life picture collections for the Picture Model Training Kit that cannot be ready-made packs because
of their licence (share-alike, research-only, or no terms written at all): household products (which bottle is
shampoo and which is conditioner, which box is cat food), Commons home pictures under CC BY-SA, and fabric patterns.
The open ones (clock times, seven-segment displays, the Open Images home labels, and the Commons pests, appliances,
plugs, laundry symbols, tools, personal care, hairstyles and kitchen packs) are in packs/home_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py): "share-alike" (only with the share-alike choice; an add-on trained with them
is CC BY-SA), "research" (research or educational terms, or no terms stated at all: personal use only, after
agreeing to the terms).

Answers are fixed sentences from each source's own records (a product's name, brand, size, categories and the
ingredient list people typed in; a Commons category; a texture class), never written by an AI model.

The collections (HOME_SOURCES):
  share-alike
    openbeautyfacts            Open Beauty Facts: front photos of toiletries and cosmetics (shampoo, conditioner,
                               shower gel, toothpaste, deodorant, sunscreen, creams, soap, mouthwash, make-up, hair
                               dye, perfume ...). "What product is this?", "What kind of product is this?" and
                               "Is this shampoo or conditioner?"-style questions where the product's categories say so.
    openbeautyfacts_labels     Open Beauty Facts: ingredient-list photos, read out ("Read the ingredients on this
                               label.").
    openproductsfacts          Open Products Facts: household goods (laundry detergent, fabric softener, washing-up
                               liquid, dishwasher tablets, cleaners, air fresheners, toilet paper, bin bags,
                               batteries, nappies, sanitary pads, toothbrushes). "Is this laundry detergent or fabric
                               softener?" ...
    openproductsfacts_labels   Open Products Facts: ingredient-list photos, read out (few household goods have their
                               ingredients typed in English: about 1 in 80, so this one is small).
    openpetfoodfacts           Open Pet Food Facts: cat, dog, bird, rodent, rabbit and fish food. "Is this cat food or
                               dog food?" and "Is this dry food or wet food?"
    openpetfoodfacts_labels    Open Pet Food Facts: ingredient-list photos, read out.
    commons_home_sa            Wikimedia Commons home categories (pests and mould, appliance displays, plugs by
                               country, connectors and batteries, laundry tags, tools and hardware, toiletries and
                               jewellery, the kitchen): files under CC BY-SA or GFDL.
    commons_hairstyles_sa      Wikimedia Commons hairstyle categories: files under CC BY-SA or GFDL; adults only.
  research
    dtd_patterns               Describable Textures Dataset (Cimpoi et al., 2014, Oxford VGG): the patterns and
                               textures of fabrics and surfaces (striped, chequered, polka-dotted, paisley, knitted,
                               lace-like ...) ("made available ... for research purposes").

All three Open ... Facts sites run on the Open Food Facts software, and are read here the way extra_sources.py reads
Open Food Facts (openfoodfacts and openfoodfacts_labels), with its helpers (get_json, off_name, looks_english,
per_label): the most scanned products of each category, an equal share per category and, within a category, the
countries of sale in turn, so that no single country fills it. Each row's "place" is the country of sale it was picked
for (the product's record lists where it is sold; the photo was taken there by a shopper).

Needing sign-up (cannot be downloaded automatically; get them yourself, then put the pictures in the own-pictures
folder with your own descriptions, as the user guide says):
  Roboflow Universe display, meter and      https://universe.roboflow.com : a free Roboflow account and API key are
  clock sets                                needed. Found: Analog-Clock-Reader (huy-v4lfd/analog-clock-reader-uv0hp,
                                            CC BY 4.0, 696 images), Seven Segment Digits
                                            (reynier-rodriguez-socarras-wqs34/seven-segment-digits-5hkzn, CC BY 4.0),
                                            7-Segment_Display (yolo-fhux7/7-segment_display), Scale 7 segment digit
                                            (numbers-dzwss/scale-7-segment-digit-ey4gr) and others; each set shows its
                                            own licence, and many hold photos copied from the web.
  Edge Impulse seven-segment project        https://studio.edgeimpulse.com/public/436849/live (Apache-2.0): an Edge
                                            Impulse account is needed to export the data.
  MVTec Screws (CC BY-NC-SA 4.0)            https://www.mvtec.com/company/research/datasets/mvtec-screws : 384 photos
                                            of 13 kinds of screws and nuts; fill in the form to download; personal use
                                            only.
  K-Hairstyle (Korean hairstyles)           https://psh01087.github.io/K-Hairstyle/ : through AI Hub Korea, which
                                            needs an account (and limits use outside Korea).
  DeepFashion and DeepFashion2              https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html : a signed
                                            agreement; non-commercial research only.
  Kaggle sets (battery types, tools,        https://www.kaggle.com : a Kaggle account is needed; check each set's
  hairstyles, clothing tags)                licence and where its pictures came from.

Looked at and not included (the reason of each is in HOME_NOT_INCLUDED).

    python -c "import sources, home_sources"      (from the kit folder: checks the file loads)
"""

import collections
import os
import random
import re
import time

import sources
from extra_sources import (NUDE, commons_file_name, commons_members, commons_sa_entries, commons_session, get_json,
                           looks_english, off_name, per_label, say, stream_tar, save)
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import Source, clean

ALT_TEXT = sources.ALT_TEXT


# ----------------------------------------------------------------- share-alike: the Open ... Facts sites

FACT_SITES = {
    "beauty": ("https://world.openbeautyfacts.org", "https://images.openbeautyfacts.org/images/products/",
               "Open Beauty Facts", "openbeautyfacts.org"),
    "products": ("https://world.openproductsfacts.org", "https://images.openproductsfacts.org/images/products/",
                 "Open Products Facts", "openproductsfacts.org"),
    "petfood": ("https://world.openpetfoodfacts.org", "https://images.openpetfoodfacts.org/images/products/",
                "Open Pet Food Facts", "openpetfoodfacts.org"),
}
FACTS_CREDIT = "{site} contributors, product {code}: photos CC BY-SA 3.0, data ODbL 1.0, {base}/product/{code}"
FACTS_FIELDS = "code,product_name,product_name_en,brands,quantity,lang,images,countries_tags,categories_tags," \
               "ingredients_text,ingredients_text_en"

# Each site's categories: (category tag, the plain name of such a product, as said after "It is").
BEAUTY_KINDS = [("shampoos", "shampoo"), ("hair-conditioners", "conditioner"), ("shower-gels", "shower gel"),
                ("toothpastes", "toothpaste"), ("deodorants", "deodorant"), ("sunscreen", "sunscreen"),
                ("hand-creams", "hand cream"), ("facial-creams", "face cream"), ("body-creams", "body cream"),
                ("body-milks", "body lotion"), ("lip-balms", "lip balm"), ("liquid-soaps", "liquid soap"),
                ("bar-soaps", "a bar of soap"), ("mouthwash", "mouthwash"), ("hair-dyes", "hair dye"),
                ("hair-masks", "a hair mask"), ("hair-gel", "hair gel"), ("nail-polishes", "nail polish"),
                ("mascara", "mascara"), ("perfumes", "perfume"), ("shaving", "a shaving product"),
                ("baby-wipes", "baby wipes"), ("cleansing-waters", "micellar cleansing water")]
PRODUCT_KINDS = [("laundry-detergents", "laundry detergent"),
                 ("fabric-softeners-dryer-sheets", "fabric softener"),
                 ("dish-detergent-soap", "washing-up liquid"), ("dishwasher-cleaners", "dishwasher detergent"),
                 ("hard-surface-cleaning-products", "a surface cleaner"),
                 ("cleaning-and-disinfecting-solutions", "a cleaning and disinfecting product"),
                 ("home-fragrances", "an air freshener"), ("toilet-papers", "toilet paper"),
                 ("garbage-bags", "bin bags"), ("batteries", "batteries"), ("diapers", "nappies"),
                 ("sanitary-napkins", "sanitary pads"), ("toothbrushes", "a toothbrush"),
                 ("incontinence-aids", "incontinence pads")]
PETFOOD_KINDS = [("dry-cat-food", "dry cat food"), ("wet-cat-food", "wet cat food"),
                 ("dry-dog-food", "dry dog food"), ("wet-dog-food", "wet dog food"), ("dog-biscuit", "dog biscuits"),
                 ("cat-biscuits", "cat treats"), ("bird-food", "bird food"), ("rodent-food", "food for small rodents"),
                 ("rabbit-food", "rabbit food"), ("fish-food", "fish food")]
SITE_KINDS = {"beauty": BEAUTY_KINDS, "products": PRODUCT_KINDS, "petfood": PETFOOD_KINDS}
# "Is this A or B?": asked when the product's categories hold exactly one of the two (never both).
SITE_PAIRS = {
    "beauty": [("shampoos", "hair-conditioners", "Is this shampoo or conditioner?", "It is shampoo.",
                "It is conditioner."),
               ("shower-gels", "shampoos", "Is this shower gel or shampoo?", "It is shower gel.", "It is shampoo."),
               ("toothpastes", "hand-creams", "Is this toothpaste or hand cream?", "It is toothpaste.",
                "It is hand cream."),
               ("sunscreen", "body-creams", "Is this sun cream or ordinary body cream?", "It is sun cream.",
                "It is ordinary body cream.")],
    "products": [("laundry-detergents", "fabric-softeners-dryer-sheets",
                  "Is this laundry detergent or fabric softener?", "It is laundry detergent.",
                  "It is fabric softener."),
                 ("dish-detergent-soap", "dishwasher-cleaners", "Is this washing-up liquid or dishwasher detergent?",
                  "It is washing-up liquid (for washing by hand).", "It is dishwasher detergent.")],
    "petfood": [("cat-food", "dog-food", "Is this cat food or dog food?", "It is cat food.", "It is dog food."),
                ("dry-pet-food", "wet-pet-food", "Is this dry food or wet food?", "It is dry food.",
                 "It is wet food.")],
}
# Products sold "everywhere" are not given a country.
COUNTRY_NAMES = {"united-states": "USA", "united-kingdom": "UK", "czech-republic": "Czechia",
                 "united-arab-emirates": "United Arab Emirates", "saudi-arabia": "Saudi Arabia",
                 "south-africa": "South Africa", "new-zealand": "New Zealand", "south-korea": "South Korea",
                 "turkiye": "Turkey", "türkiye": "Turkey"}
# Ingredient lists in INCI (cosmetics' international ingredient names, the same in every country).
INCI = re.compile(r"\b(aqua|sodium|glycerin|parfum|fragrance|alcohol|cetearyl|dimethicone|citric acid|tocopher\w*|"
                  r"benzoate|limonene|linalool|edta|polyquaternium|cocamid\w*|betaine|paraffinum|butyrospermum)\b",
                  re.I)


def country_name(tag):
    """ "en:united-kingdom" -> "UK", "en:france" -> "France"; "" for "en:world" and tags in other languages."""
    if not tag.startswith("en:") or tag in ("en:world", "en:europe"):
        return ""
    key = tag[3:].lower()
    return COUNTRY_NAMES.get(key) or " ".join(w.capitalize() for w in key.split("-"))


def facts_image(site, code, images, kind, lang):
    """The full-size address of a product's chosen photo of a kind ("front", "ingredients") in a language, or ""."""
    chosen = images.get(f"{kind}_{lang}") or {}
    if not chosen.get("rev"):
        return ""
    path = "/".join([code[:3], code[3:6], code[6:9], code[9:]]) if len(code) > 8 else code
    return f"{FACT_SITES[site][1]}{path}/{kind}_{lang}.{chosen['rev']}.full.jpg"


def front_image(site, hit):
    """The product's front photo: in English, else in the product's own language, else any; ""."""
    images = hit.get("images") or {}
    for lang in ("en", hit.get("lang") or "", *sorted(k[6:] for k in images if k.startswith("front_"))):
        url = facts_image(site, hit["code"], images, "front", lang) if lang else ""
        if url:
            return url
    return ""


def facts_products(site, category, want):
    """Up to want products of a category on a site, the most scanned first, the countries of sale taking turns:
    [(country, hit)]. Reads at most five pages of 100, a second apart (the sites ask for gentle use)."""
    base = FACT_SITES[site][0]
    hits = []
    for page in range(1, 6):
        try:
            data = get_json(f"{base}/api/v2/search", {"categories_tags_en": category, "page_size": 100,
                                                      "page": page, "sort_by": "unique_scans_n",
                                                      "fields": FACTS_FIELDS})
        except RuntimeError:
            break
        batch = data.get("products") or []
        hits += batch
        time.sleep(1)
        if len(batch) < 100 or len(hits) >= want * 4:
            break
    by_country = collections.OrderedDict()
    for hit in hits:
        countries = [c for c in (country_name(t) for t in hit.get("countries_tags") or []) if c]
        key = countries[0] if countries else ""
        by_country.setdefault(key, []).append(hit)
    picked, rng = [], random.Random(f"{site}-{category}")
    queues = list(by_country.items())
    rng.shuffle(queues)
    while len(picked) < want and any(q for _, q in queues):
        for country, queue in queues:
            if queue and len(picked) < want:
                picked.append((country, queue.pop(0)))
    return picked


def kind_rows(site, hit):
    """The "What kind of product is this?" and "Is this A or B?" rows a product's categories allow."""
    tags = {t[3:] for t in hit.get("categories_tags") or [] if t.startswith("en:")}
    rows = []
    kinds = [name for tag, name in SITE_KINDS[site] if tag in tags]
    if site == "beauty" and "2-in-1-shampoos" in tags:
        kinds = ["a 2-in-1 shampoo and conditioner"]
    if len(kinds) == 1:
        rows.append({"question": "What kind of product is this?", "answer": f"It is {kinds[0]}."})
    for a, b, question, answer_a, answer_b in SITE_PAIRS[site]:
        if site == "beauty" and "2-in-1-shampoos" in tags:
            continue
        if (a in tags) != (b in tags):
            rows.append({"question": question, "answer": answer_a if a in tags else answer_b})
    return rows


def prepare_facts_fronts(site, source, data_dir, cap):
    """Front photos of a site's products: "What product is this?" (the name, brand and size people typed in), "What
    kind of product is this?" and the "Is this A or B?" questions its categories answer; place = country of sale."""
    name, base = FACT_SITES[site][2], FACT_SITES[site][0]
    kinds = SITE_KINDS[site]
    items = []
    for category, _ in kinds:
        chosen = facts_products(site, category, per_label(int((cap + source.test) * 1.2), len(kinds)))
        for country, hit in chosen:
            url, answer = front_image(site, hit), off_name(hit)
            if not url or not answer:
                continue
            code = hit["code"]
            extra = {"credit": FACTS_CREDIT.format(site=name, code=code, base=base), "split": "",
                     **sources.place_fields({"place": country})}
            file_name = f"{site}-front-{code}.jpg"
            items.append((file_name, url, dict(extra, question="What product is this?", answer=answer)))
            for row in kind_rows(site, hit):
                items.append((file_name, url, dict(extra, **row)))
        say(f"  {name} {category}: {len(chosen)} products")
    say(f"  Fetching the {name} front photos.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


def ingredients_text(site, hit):
    """(language, ingredient list) people typed for a product, in English or (for cosmetics) in INCI names, when
    it is 120 words or fewer; (None, "") otherwise."""
    for lang, text in (("en", hit.get("ingredients_text_en")), (hit.get("lang") or "", hit.get("ingredients_text"))):
        text = clean(re.sub(r"_", "", text or ""))
        if not text or not lang or len(text.split()) > 120:
            continue
        if looks_english(text) or (site == "beauty" and len(INCI.findall(text)) >= 2):
            return lang, text
    return None, ""


def prepare_facts_labels(site, source, data_dir, cap):
    """Ingredient-list photos of a site's products, with the list people typed from them: "Read the ingredients on
    this label." Only lists in English, or cosmetics' INCI names (the same in every language)."""
    name, base = FACT_SITES[site][2], FACT_SITES[site][0]
    kinds = SITE_KINDS[site]
    items = []
    for category, _ in kinds:
        chosen = facts_products(site, category, per_label(int((cap + source.test) * 2.5), len(kinds)))
        got = 0
        for country, hit in chosen:
            lang, text = ingredients_text(site, hit)
            url = facts_image(site, hit["code"], hit.get("images") or {}, "ingredients", lang) if lang else ""
            if not url:
                continue
            code = hit["code"]
            items.append((f"{site}-ingredients-{code}.jpg", url,
                          {"question": "Read the ingredients on this label.",
                           "answer": f"The ingredients are: {text.rstrip('.')}.", "split": "",
                           "credit": FACTS_CREDIT.format(site=name, code=code, base=base),
                           **sources.place_fields({"place": country})}))
            got += 1
        say(f"  {name} {category}: {got} ingredient photos")
    return sources.fetch_pictures(items, os.path.join(data_dir, source.key), workers=4, pause=0.2)


def prepare_openbeautyfacts(source, data_dir, work, cap):
    """Open Beauty Facts front photos (photos CC BY-SA 3.0, data ODbL 1.0)."""
    return prepare_facts_fronts("beauty", source, data_dir, cap)


def prepare_openbeautyfacts_labels(source, data_dir, work, cap):
    """Open Beauty Facts ingredient photos, read out."""
    return prepare_facts_labels("beauty", source, data_dir, cap)


def prepare_openproductsfacts(source, data_dir, work, cap):
    """Open Products Facts front photos of household goods."""
    return prepare_facts_fronts("products", source, data_dir, cap)


def prepare_openproductsfacts_labels(source, data_dir, work, cap):
    """Open Products Facts ingredient photos, read out."""
    return prepare_facts_labels("products", source, data_dir, cap)


def prepare_openpetfoodfacts(source, data_dir, work, cap):
    """Open Pet Food Facts front photos."""
    return prepare_facts_fronts("petfood", source, data_dir, cap)


def prepare_openpetfoodfacts_labels(source, data_dir, work, cap):
    """Open Pet Food Facts ingredient photos, read out."""
    return prepare_facts_labels("petfood", source, data_dir, cap)


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

# (category, question, answer, deeper): the same subjects as the open packs in packs/home_packs.py.
COMMONS_HOME = [
    ("Cimex lectularius", "Is there a bed bug in this picture?", "Yes: this looks like a bed bug (Cimex "
                                                                 "lectularius).", True),
    ("Blattella germanica", "What pest is this?", "This looks like a German cockroach.", True),
    ("Periplaneta americana", "What pest is this?", "This looks like an American cockroach.", True),
    ("Reticulitermes flavipes", "What pest is this?", "This looks like a termite.", True),
    ("Wood damaged by termites", "What has damaged this wood?", "Termites have damaged this wood.", True),
    ("Vespula nests", "What is this?", "This is a wasp nest. Keep away from it: wasps sting to defend it.", True),
    ("Ixodes ricinus", "What pest is this?", "This looks like a castor bean tick (sheep tick).", True),
    ("Ixodes scapularis", "What pest is this?", "This looks like a deer tick (black-legged tick).", True),
    ("Aedes albopictus", "What pest is this?", "This looks like an Asian tiger mosquito.", True),
    ("Culex pipiens", "What pest is this?", "This looks like a common house mosquito.", True),
    ("Tineola bisselliella", "What pest is this?", "This looks like a common clothes moth.", True),
    ("Stachybotrys chartarum", "What is this?", "This is black mould (Stachybotrys chartarum).", False),
    ("Water damage", "What is wrong here?", "This shows water damage: stains, peeling or rot from a leak or damp.",
     True),
    ("Thermostats", "What is this?", "This is a thermostat.", True),
    ("Microwave ovens", "What is this?", "This is a microwave oven.", True),
    ("Kitchen scales", "What is this?", "This is a kitchen scale.", True),
    ("Glucose meters", "What is this?", "This is a blood-glucose meter.", True),
    ("Electronic arm blood pressure monitor", "What is this?", "This is a blood-pressure monitor.", False),
    ("Elevator buttons", "What is this?", "These are a lift's buttons (elevator buttons).", True),
    ("Automatic teller machines", "What is this?", "This is a cash machine (ATM).", False),
    ("BS 1363", "What kind of plug is this, and where is it used?", "This is a Type G plug or socket (BS 1363), "
     "with three rectangular pins. It is used in the UK, Ireland, Malta, Cyprus, Malaysia, Singapore, Hong Kong and "
     "the Gulf states.", True),
    ("Schuko connectors", "What kind of plug is this, and where is it used?", "This is a Type F plug or socket "
     "(Schuko), with two round pins and earth clips at the sides. It is used in Germany, Austria, the Netherlands, "
     "Sweden, Spain, Russia, South Korea and most of continental Europe.", True),
    ("AS/NZS 3112", "What kind of plug is this, and where is it used?", "This is a Type I plug or socket "
     "(AS/NZS 3112), with two flat pins in a V shape. It is used in Australia, New Zealand, China and Argentina.",
     True),
    ("SN 441011", "What kind of plug is this, and where is it used?", "This is a Type J plug or socket (SEV 1011), "
     "with three round pins. It is used in Switzerland and Liechtenstein.", True),
    ("NEMA 5–15", "What kind of plug is this, and where is it used?", "This is a Type B plug or socket (NEMA 5-15), "
     "with two flat pins and a round earth pin. It is used in the USA, Canada and Mexico.", True),
    ("USB-C", "What kind of connector is this?", "This is a USB-C connector.", True),
    ("HDMI connectors", "What kind of connector is this?", "This is an HDMI connector.", True),
    ("AA batteries", "What size of battery is this?", "This is an AA battery.", True),
    ("Button cells", "What size of battery is this?", "This is a button cell (a coin battery).", True),
    ("Laundry tags", "What is this?", "This is a clothing care label.", True),
    ("Claw hammers", "What tool is this?", "This is a claw hammer.", True),
    ("Screwdrivers", "What tool is this?", "This is a screwdriver.", True),
    ("Adjustable wrenches", "What tool is this?", "This is an adjustable spanner (wrench).", True),
    ("Cordless drills", "What tool is this?", "This is a cordless drill.", True),
    ("Tape measures", "What tool is this?", "This is a tape measure.", True),
    ("Wood screws", "What is this?", "These are wood screws.", True),
    ("Bolts", "What is this?", "These are bolts.", True),
    ("Secateurs", "What tool is this?", "This is a pair of secateurs (pruning shears).", True),
    ("Shampoo", "What is this?", "This is shampoo.", True),
    ("Toothpaste", "What is this?", "This is toothpaste.", True),
    ("Lipsticks", "What is this?", "This is a lipstick.", True),
    ("Rings (jewellery)", "What is this?", "This is a ring.", True),
    ("Wristwatches", "What is this?", "This is a wristwatch.", False),
    ("Spectacles", "What is this?", "This is a pair of glasses.", False),
    ("Gas stoves", "What is this?", "This is a gas cooker.", True),
    ("Boiling water", "Is it boiling?", "Yes, the water is boiling.", True),
    ("Table settings", "What is on the table?", "The table is set for a meal, with plates, cutlery and glasses.",
     True),
    ("Kitchenware", "What is this?", "This is kitchenware.", False),
]
COMMONS_HAIR = [
    ("Braids", "Their hair is in braids."), ("Cornrows", "Their hair is in cornrows."),
    ("Dreadlocks", "Their hair is in dreadlocks (locs)."), 
    ("Ponytails", "Their hair is tied back in a ponytail."), 
    ("Crew cuts", "They have a crew cut."), ("Shaved heads", "Their head is shaved."),
    ("Gray hair", "They have grey hair."),
]
# Drawings, art and microscope pictures are left out, except the care labels (photos of printed symbols).
HOME_NOT_PHOTO = re.compile(r"\b(drawings?|illustrations?|paintings?|logos?|icons?|emoji|cartoons?|diagrams?|in art|"
                            r"heraldry|stamps?|maps?|advertis\w*|videos?|audio|microscop\w*|micrographs?)\b", re.I)
NOT_RESPECTFUL = re.compile(r"\b(ugly|weird|freak\w*|bad hair|messy|unkempt|ghetto|nappy|savage|exotic)\b", re.I)


def commons_sa_items(specs, cap, test, prefix, adults_only=False):
    """[(file name, address, row)] for Commons files under CC BY-SA or GFDL from specs [(category, question, answer,
    deeper)]: the category's question, and the file's own caption or description too when it is real and
    respectful. The categories share the cap. adults_only: files whose words name a child are left out (else such
    rows are marked "child")."""
    s, items, seen = commons_session(), [], set()
    per_category = per_label(int((cap + test) * 0.9), len(specs))
    for category, question, answer, deeper in specs:
        titles = commons_members(s, category, "file")
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                if not HOME_NOT_PHOTO.search(sub):
                    titles += commons_members(s, sub.split(":", 1)[-1], "file")
        titles = [t for t in dict.fromkeys(titles) if t not in seen and not HOME_NOT_PHOTO.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 3]):
            words = f"{title} {text}"
            if found >= per_category or NUDE.search(words) or (adults_only and CHILD_WORDS.search(words)):
                continue
            seen.add(title)
            child = {"child": True} if CHILD_WORDS.search(words) else {}
            name = commons_file_name(prefix, title)
            items.append((name, url, {"question": question, "answer": answer, "split": "", "credit": credit,
                                      **child}))
            if text and not NOT_RESPECTFUL.search(text):
                items.append((name, url, {"question": ALT_TEXT, "answer": text, "split": "", "credit": credit,
                                          **child}))
            found += 1
        say(f"  Commons {category}: {found} files")
    return items


def prepare_commons_home_sa(source, data_dir, work, cap):
    """Wikimedia Commons home categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(COMMONS_HOME, cap, source.test, "home-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_commons_hairstyles_sa(source, data_dir, work, cap):
    """Wikimedia Commons hairstyle categories, files under CC BY-SA or GFDL; adults only."""
    specs = [(c, "What hairstyle does this person have?", a, True) for c, a in COMMONS_HAIR]
    items = commons_sa_items(specs, cap, source.test, "hair-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- research: Describable Textures Dataset

DTD_URL = "https://thor.robots.ox.ac.uk/dtd/dtd-r1.0.1.tar.gz"
# DTD's classes that describe fabric and surface patterns, with the plain words for them.
DTD_PATTERNS = {"striped": "a striped pattern", "chequered": "a chequered (checked) pattern",
                "polka-dotted": "a polka-dot pattern", "dotted": "a dotted pattern", "paisley": "a paisley pattern",
                "zigzagged": "a zigzag pattern", "banded": "a banded (broad-striped) pattern",
                "lined": "a pattern of thin lines", "grid": "a grid pattern", "crosshatched": "a crosshatched pattern",
                "swirly": "a swirly pattern", "spiralled": "a spiral pattern", "flecked": "a flecked pattern",
                "marbled": "a marbled pattern", "knitted": "a knitted texture", "woven": "a woven texture",
                "lacelike": "a lace pattern", "braided": "a braided texture", "pleated": "pleats",
                "frilly": "frills", "gauzy": "a thin, see-through (gauzy) fabric", "wrinkled": "wrinkles",
                "stained": "stains", "meshed": "a mesh", "studded": "studs",
                "interlaced": "an interlaced pattern", "matted": "a matted texture", "fibrous": "a fibrous texture"}


def prepare_dtd_patterns(source, data_dir, work, cap):
    """Describable Textures Dataset (research use): the fabric and surface pattern classes in DTD_PATTERNS, an equal
    share of each, read from its 625 MB archive only until every class has its share. "What pattern is this?" """
    quota, counts, rows = per_label(cap + source.test, len(DTD_PATTERNS)), collections.Counter(), []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep the picture when its class still needs one; True when every class is full."""
        parts = member.name.split("/")
        if member.isfile() and member.name.endswith(".jpg") and len(parts) >= 3 and parts[-2] in DTD_PATTERNS:
            kind = parts[-2]
            if counts[kind] < quota:
                path = save(f"dtd-{parts[-1][:-4]}", tar.extractfile(member).read(), folder)
                if path:
                    counts[kind] += 1
                    rows.append({"picture": path, "question": "What pattern is this?",
                                 "answer": f"It has {DTD_PATTERNS[kind]}.", "split": ""})
        return len(counts) >= len(DTD_PATTERNS) and min(counts.values()) >= quota

    stream_tar(DTD_URL, take, "the Describable Textures Dataset (625 MB at most)")
    say(f"  {len(rows)} pattern pictures of {len(counts)} kinds.")
    return rows


# ----------------------------------------------------------------- the collections

FACTS_LICENCE = "Photos CC BY-SA 3.0, database ODbL 1.0, contents DbCL 1.0 ({site}/terms-of-use)"
FACTS_CREDIT_LINE = "{name} contributors, photos CC BY-SA 3.0, data ODbL 1.0, {site}"
HOME_SOURCES = [
    # ---- share-alike
    Source("openbeautyfacts", "Open Beauty Facts: toiletries and cosmetics, which product and what kind "
                              "(share-alike)",
           FACTS_LICENCE.format(site="world.openbeautyfacts.org"),
           FACTS_CREDIT_LINE.format(name="Open Beauty Facts", site="https://world.openbeautyfacts.org"),
           "share-alike", 1500, 20, prepare_openbeautyfacts, "about 600 MB of photos"),
    Source("openbeautyfacts_labels", "Open Beauty Facts: ingredient lists of toiletries, read out (share-alike)",
           FACTS_LICENCE.format(site="world.openbeautyfacts.org"),
           FACTS_CREDIT_LINE.format(name="Open Beauty Facts", site="https://world.openbeautyfacts.org"),
           "share-alike", 1000, 20, prepare_openbeautyfacts_labels, "about 500 MB of photos"),
    Source("openproductsfacts", "Open Products Facts: household goods, which product and what kind (share-alike)",
           FACTS_LICENCE.format(site="world.openproductsfacts.org"),
           FACTS_CREDIT_LINE.format(name="Open Products Facts", site="https://world.openproductsfacts.org"),
           "share-alike", 1000, 20, prepare_openproductsfacts, "about 400 MB of photos"),
    Source("openproductsfacts_labels", "Open Products Facts: ingredient lists of household goods, read out "
                                       "(share-alike)",
           FACTS_LICENCE.format(site="world.openproductsfacts.org"),
           FACTS_CREDIT_LINE.format(name="Open Products Facts", site="https://world.openproductsfacts.org"),
           "share-alike", 100, 5, prepare_openproductsfacts_labels, "about 50 MB of photos"),
    Source("openpetfoodfacts", "Open Pet Food Facts: pet food, cat or dog, dry or wet (share-alike)",
           FACTS_LICENCE.format(site="world.openpetfoodfacts.org"),
           FACTS_CREDIT_LINE.format(name="Open Pet Food Facts", site="https://world.openpetfoodfacts.org"),
           "share-alike", 1000, 20, prepare_openpetfoodfacts, "about 400 MB of photos"),
    Source("openpetfoodfacts_labels", "Open Pet Food Facts: ingredient lists of pet food, read out (share-alike)",
           FACTS_LICENCE.format(site="world.openpetfoodfacts.org"),
           FACTS_CREDIT_LINE.format(name="Open Pet Food Facts", site="https://world.openpetfoodfacts.org"),
           "share-alike", 500, 10, prepare_openpetfoodfacts_labels, "about 250 MB of photos"),
    Source("commons_home_sa", "Wikimedia Commons: home life (pests, appliances, plugs, tools, toiletries, kitchen), "
                              "files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 20, prepare_commons_home_sa, "about 150 MB"),
    Source("commons_hairstyles_sa", "Wikimedia Commons: hairstyles of adults, files under CC BY-SA or GFDL "
                                    "(share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 600, 10, prepare_commons_hairstyles_sa, "about 60 MB"),
    # ---- research
    Source("dtd_patterns", "Describable Textures Dataset: fabric and surface patterns (research only; personal use)",
           "Made available for research purposes (robots.ox.ac.uk/~vgg/data/dtd); no licence named",
           "Describable Textures Dataset (Mircea Cimpoi, Subhransu Maji, Iasonas Kokkinos, Sammy Mohamed and Andrea "
           "Vedaldi, CVPR 2014), https://www.robots.ox.ac.uk/~vgg/data/dtd/", "research", 1500, 20,
           prepare_dtd_patterns, "up to 625 MB, read once",
           terms="https://www.robots.ox.ac.uk/~vgg/data/dtd/",
           terms_summary="Made available to the computer vision community for research purposes; no licence is "
                         "named, so personal, non-commercial use only. Photos are from Flickr."),
]

# The collections a picture-making model may learn from: objects without people (products, pet food and patterns).
# Never the hairstyles, nor the Commons home files (some show people using the things).
HOME_PICTURE_MAKING_OK = {"openbeautyfacts", "openbeautyfacts_labels", "openproductsfacts",
                          "openproductsfacts_labels", "openpetfoodfacts", "openpetfoodfacts_labels", "dtd_patterns"}

HOME_NOT_INCLUDED = {
    "Blood-glucose and blood-pressure monitor photos (Finnegan et al., Oxford, 2019)":
        "the download (cameralab.eng.ox.ac.uk/data/bp_bg_meters.zip) now only leads back to the lab's home page; "
        "no licence was ever stated (only 'please cite'). Ask the authors (eng.ox.ac.uk/lcmt).",
    "It's About Time: Clock Movies": "frames of films and of 'The Clock' (scraped from a fan wiki); the authors say "
                                     "they may not be released because of copyright. The COCO and Open Images clock "
                                     "times from the same work are the open clock_times pack.",
    "IP102 insect pests": "'free for academic usage' (research), but it is about 102 crop pests in fields, not "
                          "household pests, and is shared as a Google Drive folder the kit cannot read without a "
                          "file address. The household pests come from Commons and Open Images instead.",
    "Figaro-1k hair textures": "its host (projects.i-ctm.eu) no longer answers.",
    "CelebA hair attributes": "celebrity photos taken from the web without the people's consent; the owner's rule "
                              "for hairstyles is open datasets of consenting adults.",
    "EPIC-KITCHENS (CC BY-NC 4.0)": "videos of kitchens filmed from the cook's head (over 700 GB); no labels of "
                                    "whether a burner is on or a pot is boiling. Too big for what it would add.",
    "Commons 'Laundry symbols' ISO 7000 and IEC 60417 files": "their file names give only a number, not a meaning, "
                                                              "so no answer can be written from them.",
}
