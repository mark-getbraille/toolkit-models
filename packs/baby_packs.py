"""Pack builders for BABY AND YOUNG CHILD PRODUCTS, for blind parents: bottles and nipples, formula, baby food, wipes,
car seats, strollers, cribs, bassinets, high chairs, playpens, baby gates, monitors, bouncers and swings, pacifiers,
teethers, sippy cups, children's toothbrushes, outlet covers, oral syringes and medicine droppers. Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" where the source gives a country
and "child": true where the words of a picture name a child (a baby product's own name, "baby bottle", does not count:
PRODUCT_WORDS). A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Answers name the product and its key features FROM THE RECORD ONLY: a Commons category's name, the file's own words,
an Amazon listing's own name, a label people checked by hand (Open Images). A car seat is called rear-facing,
forward-facing, infant or convertible, a formula powder or ready-to-feed, a diaper's size or a pacifier's age stage
given, only where the record's words say so (FEATURES); a thermometer's reading or a syringe's measurement only where
the words state it with its unit (MEASURE). A short safety note follows where it fits (NOTES: safe sleep for cribs,
bassinets and playpens; the label's weight and height limits for car seats; ...).

The packs (all open, checked at the source in November 2026):
  commons_baby_products       Wikimedia Commons categories (BABY_SPECS) and Commons search for the products with no
                              category (BABY_SEARCHES: baby gates, strollers, bassinets, bouncers, swings, oral
                              syringes, medicine droppers, children's toothbrushes); files CC0, public domain or CC BY
                              (each file's licence checked on its own page); captions CC0.
  open_images_baby_products   Google Open Images V7: photos where people checked by hand whether a baby gate, bib,
                              baby food, infant formula, baby monitor, cradle, child safety seat, pram, baby carrier,
                              baby mobile or rattle is there (labels CC BY 4.0; each photo's own licence checked,
                              photographer named). Labels other packs ask (baby bottle, pacifier, diaper, infant bed,
                              baby carriage, car seat: gaps_oi_packs, everyday_packs) are not asked again.
  abo_baby_products           Amazon Berkeley Objects (Amazon.com and UC Berkeley, CC BY 4.0): the catalogue photos of
                              the product types no other pack reads (BABY_PRODUCT, BABY_BOTTLE, PACIFIER, STROLLER, and
                              THERMOMETER listings whose name says baby, infant or child), with the listing's own name.

Not built, with the reasons in training-kit/kit/daily_access_sources.py: the CPSC recall photos (the recalling firms'
own pictures: "any other use of photographs ... may require permission from a copyright holder"; already the kit's
personal-use entry us_sources.cpsc_recalls). Diapers, baby baths and changing tables are not taken from Commons (their
photos often show an undressed baby); ABO's diaper and wipe listings are abo_packaged_goods'.

Safety (packs/SOURCE-RULES.md): children only in everyday clothed scenes. Commons files whose words name bathing,
nudity, undressing, nappy or diaper changing, swimming, illness or injury (UNCLOTHED), a person or a child, or that
are old prints, posters or museum pieces are left out (left_out): that pack shows the products themselves, only
categories' own files (their subcategories strayed into camping trips and festivals). Open Images rows of photos
where people checked a child is there are marked "child". All three packs are for describing only, never for
picture-making.

    python packs/baby_packs.py commons_baby_products --limit 8      (a quick check)
"""

import collections
import csv
import gzip
import io
import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, ALT_TEXT, fetch_all
from gaps_oi_packs import group, build_oi_gap, QUICK

WHAT_Q = "What is this?"
FEATURE_Q = "What does its record say about it?"
MEASURE_Q = "What reading or measurement does it show?"

SLEEP_NOTE = ("Always place a baby on their back to sleep, on a firm, flat surface with no soft bedding, pillows, "
              "bumpers or toys.")
CAR_SEAT_NOTE = ("Check the car seat's label for the child's weight and height limits, and keep the harness snug with "
                 "the chest clip at armpit level.")
GATE_NOTE = "Use a gate that screws into the wall at the top of stairs; pressure-mounted gates are for doorways only."
BOTTLE_NOTE = "Test the milk's temperature on the inside of your wrist before feeding."
FORMULA_NOTE = "Measure with the scoop that comes in the container and follow its own mixing instructions exactly."
MEDICINE_NOTE = ("Measure children's medicine only with the syringe or dropper made for it, and check the dose with a "
                 "pharmacist or doctor.")
PACIFIER_NOTE = "Check it for cracks or tears before each use, and never tie it around a baby's neck."
OUTLET_NOTE = "Covers keep small fingers and objects out of sockets; check they fit tightly and cannot be pulled out."
HIGH_CHAIR_NOTE = "Always use the waist and crotch straps, and never leave a child alone in it."
STROLLER_NOTE = "Use the harness and put the brake on whenever you stop."
THERMOMETER_NOTE = "For a baby under 3 months, a temperature of 100.4 F (38 C) or higher needs a doctor straight away."

# Commons categories: (category, deeper, what it is, note).
BABY_SPECS = [
    ("Baby bottles", False, "a baby bottle (feeding bottle)", BOTTLE_NOTE),
    ("Feeding bottles", False, "a feeding bottle", BOTTLE_NOTE),
    ("Infant formula", False, "infant formula (baby milk)", FORMULA_NOTE),
    ("Baby food", False, "baby food", ""),
    ("Wet wipes", False, "wet wipes", ""),
    ("Child safety seats", False, "a child car seat", CAR_SEAT_NOTE),
    ("Cribs", False, "a crib (cot)", SLEEP_NOTE),
    ("High chairs", False, "a high chair", HIGH_CHAIR_NOTE),
    ("Playpens", False, "a playpen (play yard)", SLEEP_NOTE),
    ("Baby monitors", False, "a baby monitor", ""),
    ("Pacifiers", False, "a pacifier (dummy)", PACIFIER_NOTE),
    ("Teething rings", False, "a teething ring (teether)", ""),
    ("Sippy cups", False, "a sippy cup", ""),
    ("Outlet covers", False, "an outlet cover (socket cover)", OUTLET_NOTE),
]
# Commons searches for products with no category of their own: (query, what it is, note).
BABY_SEARCHES = [
    ('intitle:"baby gate"', "a baby gate (safety gate)", GATE_NOTE),
    ('intitle:"stair gate"', "a stair gate (safety gate)", GATE_NOTE),
    ('intitle:stroller', "a stroller (pushchair)", STROLLER_NOTE),
    ('intitle:pushchair', "a pushchair (stroller)", STROLLER_NOTE),
    ('intitle:bassinet', "a bassinet", SLEEP_NOTE),
    ('intitle:"moses basket"', "a Moses basket", SLEEP_NOTE),
    ('intitle:"baby bouncer"', "a baby bouncer", "Use it on the floor only, never on a table or a soft surface."),
    ('intitle:"baby swing"', "a baby swing", "A baby who falls asleep in it should be moved to a flat crib."),
    ('intitle:"oral syringe"', "an oral syringe for medicine", MEDICINE_NOTE),
    ('intitle:"medicine dropper"', "a medicine dropper", MEDICINE_NOTE),
    ('intitle:"medicine syringe"', "an oral syringe for medicine", MEDICINE_NOTE),
    ('intitle:"children\'s toothbrush"', "a children's toothbrush", ""),
    ('intitle:"kids toothbrush"', "a children's toothbrush", ""),
    ('intitle:"outlet cover"', "an outlet cover (socket cover)", OUTLET_NOTE),
    ('intitle:"socket cover"', "a socket cover (outlet cover)", OUTLET_NOTE),
]
# Product words that contain a child word but name a product, not a child in the picture.
PRODUCT_WORDS = re.compile(r"\b(bab(y|ies)['’]?s?|infants?['’]?|child(ren)?['’]?s?|kids?['’]?|"
                           r"toddlers?['’]?)\s+"
                           r"(bottles?|food|formula|milk|gates?|monitors?|products?|wipes?|carriers?|bouncers?|"
                           r"swings?|walkers?|cribs?|cots?|seats?|car seats?|safety seats?|toothbrush\w*|cups?|"
                           r"spoons?|bowls?|pacifiers?|dummies|teethers?|thermometers?|syringes?|droppers?|gates?|"
                           r"proofing|safety|beds?|bassinets?|strollers?|buggies|pushchairs?|high ?chairs?|"
                           r"playpens?|sleeping bags?|blankets?|bibs?|nipples?|teats?)\b|\bchild safety\b|"
                           r"\bchildproof\w*\b", re.I)
# Words that leave a file out: an undressed child, bathing, changing, swimming, illness, injury.
UNCLOTHED = re.compile(r"\b(nude|naked|undress\w*|bath(s|ing|tub)?|bathe\w*|nappy chang\w*|diaper chang\w*|"
                       r"changing (table|mat)|topless|swim\w*|breastfeed\w*|nursing|sick|ill|injur\w*|hospital|"
                       r"wounds?|dead|death|recall(ed)? (deaths?|injur\w*))\b", re.I)
# Features said only where the words name them (pattern, the words used).
FEATURES = [
    (r"\brear[- ]facing\b", "rear-facing"), (r"\bforward[- ]facing\b", "forward-facing"),
    (r"\binfant (car )?seats?\b", "an infant car seat"), (r"\bconvertible\b", "convertible"),
    (r"\bbooster\b", "a booster seat"), (r"\b(5|five)[- ]point harness\b", "a five-point harness"),
    (r"\bchest clip\b", "a chest clip"), (r"\bISOFIX|LATCH\b", "ISOFIX or LATCH anchors"),
    (r"\bpowder(ed)?\b", "powder"), (r"\bready[- ]to[- ]feed\b", "ready to feed"),
    (r"\bliquid concentrate\b", "liquid concentrate"), (r"\bscoops?\b", "a scoop"),
    (r"\bstage ?\d\b", None), (r"\b\d{1,2}\s?-\s?\d{1,2}\s?(m|months?)\b", None), (r"\bsize \d\b", None),
    (r"\bnewborn\b", "newborn size"), (r"\bbpa[- ]free\b", "BPA free"), (r"\bslow flow\b", "slow flow"),
    (r"\bmedium flow\b", "medium flow"), (r"\bfast flow\b", "fast flow"),
    (r"\bpressure[- ]mounted\b", "pressure-mounted"), (r"\bhardware[- ]mounted|screw[- ]mounted\b",
                                                       "screwed to the wall"),
]
FEATURES = [(re.compile(p, re.I), w) for p, w in FEATURES]
MEASURE = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,2})?)\s?(°\s?[CF]|degrees? [CF]\w*|ml|mL|cc|teaspoons?|tsp)\b",
                     re.I)


def features_said(text):
    """The product features the words name, in FEATURES' order, each once ("rear-facing", "Stage 2", "0-6 months")."""
    out = []
    for pattern, words in FEATURES:
        m = pattern.search(text or "")
        if m:
            said = words or re.sub(r"\s+", " ", m.group(0)).replace("m)", " months)").strip()
            if re.fullmatch(r"\d{1,2}\s?-\s?\d{1,2}\s?(m|months?)", said, re.I):
                said = re.sub(r"\s?(m|months?)$", " months", said.replace(" ", ""), flags=re.I)
            if said.lower() not in (o.lower() for o in out):
                out.append(said)
    return out


def measure_said(text):
    """ "38.2 °C" when the words state one reading or measurement with its unit, else ""."""
    found = {(m.group(1), re.sub(r"\s", "", m.group(2))) for m in MEASURE.finditer(text or "")}
    if len(found) != 1:
        return ""
    value, unit = found.pop()
    return f"{value} {unit}"


def is_child(words):
    """True when the words name a child, not counting a baby product's own name."""
    from expression_packs import CHILD
    return bool(CHILD.search(PRODUCT_WORDS.sub(" ", words or "")))


# More words that leave a Commons file out: prints, lithographs and museum pieces (the products must be current), and
# a named or described person (the pack shows the products; a child is never the subject).
NOT_PRODUCT = re.compile(r"\b(lithograph\w*|engraving|etching|dessinateur|museum|DPLA|catalog(ue)?er|portrait\w*|"
                         r"festival|camping|wedding|family|holiday|place|rue|street|avenue|square|park|referee|"
                         r"umpire|tennis|rituals?|evacuees?)\b", re.I)
# The words a file's own title or description must use for each kind of product (a Commons category or search also
# holds tennis umpires' chairs, streets named Bassinet and photos of a sleeping baby).
MUST = [(re.compile(p, re.I), re.compile(w, re.I)) for p, w in (
    (r"bottle", r"\b(bottles?|biberons?|teats?|nipples?)\b"), (r"formula", r"\b(formula|milk powder|infant milk)\b"),
    (r"baby food", r"\b(baby food|pur[ée]e|jars?|pouch(es)?|cereal)\b"), (r"wipes", r"\bwipes?\b"),
    (r"car seat", r"\b(car ?seats?|safety seats?|booster)\b"), (r"crib", r"\b(cribs?|cots?)\b"),
    (r"high chair", r"\bhigh ?chairs?\b"), (r"playpen", r"\b(playpens?|play ?yards?|play ?pens?)\b"),
    (r"monitor", r"\bmonitors?\b"), (r"pacifier", r"\b(pacifiers?|dumm(y|ies)|soothers?)\b"),
    (r"teething", r"\bteeth\w*\b"), (r"sippy", r"\bsippy\b"), (r"outlet|socket", r"\b(outlet|socket)s? (covers?|plugs?|protectors?|caps?)\b"),
    (r"gate", r"\bgates?\b"), (r"stroller|pushchair", r"\b(strollers?|pushchairs?|prams?|buggies|buggy)\b"),
    (r"bassinet", r"\bbassinets?\b"), (r"moses", r"\bmoses baskets?\b"), (r"bouncer", r"\bbouncers?\b"),
    (r"swing", r"\bswings?\b"), (r"syringe", r"\bsyringes?\b"), (r"dropper", r"\bdroppers?\b"),
    (r"toothbrush", r"\btoothbrush\w*\b"))]


def names_product(what, words):
    """True when the words use the product's own word (MUST); kinds without an entry pass."""
    for kind, must in MUST:
        if kind.search(what):
            return bool(must.search(words or ""))
    return True


def left_out(words):
    """True when a Commons file's words name an undressed child, bathing, illness or injury (UNCLOTHED), something
    old or a museum piece (med_vet_packs.is_old), a drawing, poster or advertisement (mechanical_packs.NOT_A_PHOTO,
    NOT_PRODUCT), or a person or child (device_packs.PERSON, is_child: not counting a product's own name such as
    "baby bottle")."""
    from med_vet_packs import is_old
    from mechanical_packs import NOT_A_PHOTO
    from device_packs import PERSON
    return bool(UNCLOTHED.search(words) or is_old(words) or NOT_A_PHOTO.search(words) or NOT_PRODUCT.search(words)
                or PERSON.search(PRODUCT_WORDS.sub(" ", words)) or is_child(words))


def product_rows(what, note, words, text, credit):
    """The rows of one Commons file (what it is, the features and the measurement its words state, its own
    description), or [] when it is left out by its words (left_out)."""
    if left_out(words) or not names_product(what, words):
        return []
    rows = [{"question": WHAT_Q, "answer": f"This is {what}." + (f" {note}" if note else ""), "credit": credit}]
    feats = features_said(words)
    if feats:
        rows.append({"question": FEATURE_Q, "answer": "Its record says: " + ", ".join(feats) + ".", "credit": credit})
    measure = measure_said(words) if re.search(r"thermometer|syringe|dropper", what) else ""
    if measure:
        extra = THERMOMETER_NOTE if "°" in measure or "degree" in measure else MEDICINE_NOTE
        rows.append({"question": MEASURE_Q, "answer": f"The photo's own words say {measure}. {extra}",
                     "credit": credit})
    if text:
        rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
    child = is_child(words)
    return [dict(r, child=True) if child else r for r in rows]


def build_commons_baby_products(limit):
    """The commons_baby_products pack (see the module docstring)."""
    from food_packs import commons_get, commons_members, with_twins
    from home_packs import commons_fetch, file_name, home_entries, category_files, NUDE
    s, rng = session(), pass_random(9312)
    found = {}                                      # title -> (what, note)
    for category, deeper, what, note in BABY_SPECS:
        titles = category_files(s, category, deeper)
        rng.shuffle(titles)
        for t in titles[:max(20, limit // 10)]:
            found.setdefault(t, (what, note))
    for query, what, note in BABY_SEARCHES:
        data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": 60,
                               "srsearch": f"{query} filetype:bitmap"})
        for r in (data.get("query") or {}).get("search") or []:
            found.setdefault(r["title"], (what, note))
    titles = list(found)
    rng.shuffle(titles)
    say(f"Commons baby products: {len(titles)} files to check")
    items = []
    for title, url, credit, text in home_entries(s, titles):
        words = f"{title.split(':', 1)[-1].rsplit('.', 1)[0].replace('_', ' ')}. {text}"
        if NUDE.search(words):
            continue
        rows = product_rows(*found[title], words, text, credit)
        if rows:
            items.append((file_name("baby", title), url, rows))
        if len(items) >= int(limit * 1.15) + 2:
            break
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- Open Images

BABY_OI = [
    group("What baby things are in this picture?",
          {"Bib": "a bib", "Baby food": "baby food", "Infant formula": "infant formula",
           "Baby monitor": "a baby monitor",
           "Pram": "a pram", "Baby carrier": "a baby carrier", "Baby mobile": "a baby mobile",
           "Baby rattle": "a baby rattle"}),
    group("Is there a baby gate here?", {"Baby gate": "a baby gate"}, GATE_NOTE),
    group("Is there a cradle here?", {"Cradle": "a cradle"}, SLEEP_NOTE),
    group("Is there a child car seat here?", {"Child safety seat": "a child car seat"}, CAR_SEAT_NOTE),
]


def build_open_images_baby_products(limit):
    """open_images_baby_products (see the module docstring)."""
    return build_oi_gap("open_images_baby_products", BABY_OI, limit, 9313)


# ----------------------------------------------------------------- Amazon Berkeley Objects

ABO_BABY_TYPES = {"BABY_PRODUCT": "a baby product", "BABY_BOTTLE": "a baby bottle or bottle part",
                  "PACIFIER": "a pacifier (dummy)", "STROLLER": "a stroller accessory", "THERMOMETER": "a thermometer"}
ABO_NOTES = [(re.compile(p, re.I), n) for p, n in (
    (r"\b(crib|cot|bassinet|sleeping bag|sleep sack|mattress|play ?yard|playpen)\b", SLEEP_NOTE),
    (r"\bcar seat\b", CAR_SEAT_NOTE), (r"\b(gate)\b", GATE_NOTE), (r"\b(pacifier|dummy|soother)\b", PACIFIER_NOTE),
    (r"\b(bottle|nipple|teat)\b", BOTTLE_NOTE), (r"\b(outlet|socket) (cover|plug)s?\b", OUTLET_NOTE),
    (r"\bhigh ?chair\b", HIGH_CHAIR_NOTE), (r"\bthermometer\b", THERMOMETER_NOTE),
    (r"\b(syringe|dropper)\b", MEDICINE_NOTE))]
ABO_CREDIT = ("Amazon Berkeley Objects: data and images by Amazon.com; dataset by Matthieu Guillaumin, Thomas "
              "Dideriksen, Kenan Deng, Himanshu Arora, Arnab Dhua, Xi Zhang, Tomas Yago-Vicente, Jasmine Collins, "
              "Shubham Goyal and Jitendra Malik, CC BY 4.0, https://amazon-berkeley-objects.s3.amazonaws.com/ "
              "(listing {item}, {domain})")


def abo_baby_rows(listing):
    """The rows of one ABO listing of this pack's types, or [] (another type, no English name, a thermometer not for
    babies, or words that name an undressed child)."""
    from things_packs import abo_value
    code = ((listing.get("product_type") or [{}])[0] or {}).get("value", "")
    if code not in ABO_BABY_TYPES:
        return []
    country = listing.get("country") or ""
    name = abo_value(listing.get("item_name"), country)
    if not name or not listing.get("main_image_id") or UNCLOTHED.search(name):
        return []
    if code == "THERMOMETER" and not re.search(r"\b(bab(y|ies)|infants?|child(ren)?|kids?)\b", name, re.I):
        return []
    brand = abo_value(listing.get("brand"), country)
    by = f" by {brand}" if brand and brand.lower() not in name.lower() else ""
    note = next((n for p, n in ABO_NOTES if p.search(name)), "")
    rows = [{"question": WHAT_Q, "answer": f"This is {ABO_BABY_TYPES[code]}{by}. Its listing calls it: "
                                            f"{name.rstrip('.')}." + (f" {note}" if note else "")}]
    feats = features_said(name)
    if feats:
        rows.append({"question": FEATURE_Q, "answer": "Its listing says: " + ", ".join(feats) + "."})
    return rows


def build_abo_baby_products(limit):
    """The ABO baby products pack: reads the 16 listing files and the image list, keeps this pack's types, takes the
    types in turn, then fetches the catalogue photos."""
    from food_packs import with_twins
    from things_packs import ABO_LISTINGS, ABO_IMAGES, ABO_PICTURE
    from places import where, country_named
    s, rng = session(), pass_random(9314)
    by_type, seen = collections.defaultdict(list), set()
    for part in "0123456789abcdef":
        r = s.get(ABO_LISTINGS.format(part), timeout=600)
        r.raise_for_status()
        for line in gzip.decompress(r.content).decode("utf-8").splitlines():
            try:
                listing = json.loads(line)
            except ValueError:
                continue
            rows = abo_baby_rows(listing)
            image = listing.get("main_image_id")
            if rows and image not in seen:
                seen.add(image)
                by_type[listing["product_type"][0]["value"]].append((listing, rows))
    say("ABO baby products: " + ", ".join(f"{k} {len(v)}" for k, v in sorted(by_type.items())))
    r = s.get(ABO_IMAGES, timeout=600)
    r.raise_for_status()
    paths = {row["image_id"]: row["path"] for row in csv.DictReader(io.StringIO(gzip.decompress(r.content)
                                                                                .decode("utf-8")))
             if row["image_id"] in seen}
    queues = []
    for code in sorted(by_type):
        rng.shuffle(by_type[code])
        queues.append(by_type[code])
    want, items = int(limit * 1.1) + 2, []
    while len(items) < want and any(queues):
        for queue in queues:
            if queue and len(items) < want:
                listing, rows = queue.pop()
                path = paths.get(listing["main_image_id"])
                if not path:
                    continue
                credit = ABO_CREDIT.format(item=listing.get("item_id", ""), domain=listing.get("domain_name", ""))
                place = where(country_named("GB" if listing.get("country") == "UK" else listing.get("country", "")),
                              "market")
                items.append((f"abo-baby-{listing['main_image_id']}.jpg".replace("+", "_"), ABO_PICTURE.format(path),
                              [dict(r, credit=credit, **place) for r in rows]))
    return with_twins(fetch_all(items, workers=8)[:limit])


# ----------------------------------------------------------------- the packs

BABY_PACKS = {
    "commons_baby_products": (build_commons_baby_products,
                              "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY "
                              "(credited below) of baby and young child product categories and searches; captions "
                              "CC0."),
    "open_images_baby_products": (build_open_images_baby_products,
                                  "Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): "
                                  "labels CC BY 4.0; each photo under its own licence (CC BY, CC0 or the Public Domain "
                                  "Mark, checked photo by photo), photographer credited below."),
    "abo_baby_products": (build_abo_baby_products,
                          "Amazon Berkeley Objects (Amazon.com and UC Berkeley), CC BY 4.0, "
                          "https://amazon-berkeley-objects.s3.amazonaws.com/ (each listing credited below)."),
}
BABY_LIMITS = {
    "commons_baby_products": 800,      # 14 categories and 15 searches
    "open_images_baby_products": 1500,  # 11 labels
    "abo_baby_products": 80,           # about 80 listings with an English name and their own photo
}
BABY_COMMONS_KEYS = ("commons_baby_products",)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try a baby products pack builder.")
    parser.add_argument("key", choices=sorted(BABY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = BABY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
