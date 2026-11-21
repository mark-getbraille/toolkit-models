"""Open Images packs for the GAPS the picture category inventory found (November 2026): everyday things in public
places and at home, more foods and drinks, and the cards and papers people need read. Used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)];
a picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same
picture (food_packs.with_twins). The limit counts pictures.

Why: the inventory of open picture sources (Open Images, LVIS, Objects365, ImageNet and others, checked against the
real packs) found everyday things no pack asks about: public washroom fixtures, baby furniture, luggage, shopping carts
and big bins, pools, billboards, exercise equipment, office supplies, pastries, seafood, sauces, cocktails, serving
ware, trophies, fairground rides, headstones, business cards and tickets. Every label used here was checked by hand
against the Open Images labels the other packs ask about (OI_ASKED_ELSEWHERE in the self-test): none is asked twice.

The packs (OI_GAPS_PACKS), all from Google Open Images V7, the labels people checked by hand on the train, validation
and test sets (labels CC BY 4.0; each photo's OWN licence checked, CC BY, CC0 or the Public Domain Mark, photographer
named; photos that need turning are left out):
  open_images_public_home   Washroom fixtures (urinal, bidet, hand dryer, tissue holder), bathroom
                            cabinets and towels, baby furniture (infant bed, baby carriage, car seat), seating and
                            bedside furniture (loveseat, studio couch, sofa bed, nightstand), office and school
                            supplies, exercise equipment, bags and luggage, shopping carts and bins, swimming pools
                            and hot tubs, street obstacles (billboards, scaffolding, posters on poles), pet furniture
                            and lighting (chandeliers, lampshades). "What washroom fixtures are in this picture?" ->
                            "I can see a urinal and a hand dryer."; "Is there a shopping cart in this picture?"
  open_images_outings       Outings, celebrations and ceremonies: cakes and wreaths, outdoor and hiking gear
                            (binoculars, compass, fishing rod, tent), hats and coats the clothing packs miss (sombrero,
                            tiara, raincoat, trench coat), event objects (trophy, medal, podium, megaphone), fairground
                            and playground rides (Ferris wheel, roller coaster, carousel, slide, swing, trampoline) and
                            cemeteries (headstones, graves). People are in many of these photos.
  open_images_food_more     Baked goods (bagel, muffin, croissant, cupcake, tart, pastry, doughnut, pretzel, waffle,
                            pancake, cookie, pie), sauces and spreads (guacamole, ketchup, mayonnaise, mustard, gravy,
                            honey, pesto), meats (sausage, hot dog, bacon, salami, meatballs, kebab), seafood (shrimp,
                            prawns, lobster, crab, oysters, mussels, clams, scallops, squid, octopus) with an allergy
                            note, drinks (cocktail, beer, wine, whisky), Mexican dishes (burrito, taco, nachos),
                            serving ware (platter, serving tray, cake stand, teacup) and kitchen tools (strainer,
                            skewer, toothpick, funnel).
  open_images_cards_documents  Cards and papers people need read, answered ONLY with what kind of thing it is
                            (business card, greeting card, postcard, ticket, receipt, menu, calendar, coupon, badge).
                            Never what is written on it. Identity documents, driving licences and passports are kept
                            only when the photo's own Flickr title says it is a sample or specimen (no real person's
                            papers), and the answer never reads them.

Answers say only what the labels say: a label people confirmed ("I can see ..."), or a label people checked and found
absent ("No, I can't see ..."), never a guess. Photos with nudity or underwear labels are left out, as are swimwear
photos with a child; rows of photos with a child label are marked "child" (the picture-making trainer leaves them
out). The two people-heavy packs (open_images_outings, open_images_public_home) are never used for picture-making
(training-kit sources.py PEOPLE_AND_BODILY_PACK_KEYS); food and cards may show hands and faces too, and are listed
there as well.

Not here, and why (see the kit's gaps_sources.py for the full list): LVIS (its only download host,
dl.fbaipublicfiles.com, disallows all robots), Objects365 (photos without their own open licence: an idea list only),
body parts (people photos whose labels say only that an arm or ear is there).

    python packs/gaps_oi_packs.py open_images_food_more --limit 8 --quick   (validation and test sets only)
"""

import csv
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, fetch_all, say, pass_random
from food_packs import listed, with_twins, oi_lines, oi_licence_name, OI_CLASSES, OI_PICTURE
from expression_packs import OI_CHILD, OI_TRAIN_LABELS
from bodily_packs import OI_BOXABLE

OI = "https://storage.googleapis.com/openimages/"
OI_GAP_LABELS = (OI_TRAIN_LABELS, OI + "v7/oidv7-val-annotations-human-imagelabels.csv",
                 OI + "v7/oidv7-test-annotations-human-imagelabels.csv")
OI_GAP_IMAGES = (OI + "v6/oidv6-train-images-with-labels-with-rotation.csv",
                 OI + "2018_04/validation/validation-images-with-rotation.csv",
                 OI + "2018_04/test/test-images-with-rotation.csv")
QUICK = {"on": False}                # main(--quick): the validation and test sets only (a small live check)
CREDIT = "Photo by {author}{page}, {licence}; labels from Open Images V7 (Google), CC BY 4.0"

# Labels that leave a photo out wherever they are confirmed, and those that leave it out when a child is there.
LEAVE_OUT = {"Nudity", "Lingerie", "Undergarment", "Brassiere"}
LEAVE_OUT_WITH_CHILD = {"Swimwear", "Bikini", "Swim briefs", "Swimming", "Bathtub"}


def group(question, things, note=""):
    """One question and its labels: {label: the words the answer uses}; note is added after a "yes" answer."""
    return {"question": question, "things": things, "note": note}


# ----------------------------------------------------------------- the four packs' labels

PUBLIC_HOME = [
    group("What washroom fixtures are in this picture?",
          {"Urinal": "a urinal", "Bidet": "a bidet", "Hand dryer": "a hand dryer",
           "Facial tissue holder": "a tissue holder", "Plumbing fixture": "a plumbing fixture",
           "Bathroom accessory": "bathroom accessories", "Bathroom cabinet": "a bathroom cabinet"}),
    group("What baby things are in this picture?",
          {"Infant bed": "a cot (infant bed)", "Baby carriage": "a pram (baby carriage)", "Car seat": "a car seat"}),
    group("What furniture is in this picture?",
          {"Loveseat": "a loveseat (a small two-seat sofa)", "Studio couch": "a studio couch",
           "Sofa bed": "a sofa bed", "Nightstand": "a nightstand (bedside table)",
           "Filing cabinet": "a filing cabinet", "Hammock": "a hammock"}),
    group("What office or school supplies are in this picture?",
          {"Eraser": "an eraser", "Pencil case": "a pencil case", "Pencil sharpener": "a pencil sharpener",
           "Crayon": "crayons", "Bulletin board": "a bulletin board", "Ring binder": "a ring binder",
           "Paper clip": "paper clips", "Rubber band": "rubber bands", "Post-it note": "sticky notes",
           "Whiteboard": "a whiteboard", "Paper cutter": "a paper cutter", "Office supplies": "office supplies"}),
    group("What exercise equipment is in this picture?",
          {"Dumbbell": "a dumbbell", "Barbell": "a barbell", "Training bench": "a training bench",
           "Punching bag": "a punching bag", "Treadmill": "a treadmill", "Stationary bicycle": "an exercise bike",
           "Indoor rower": "a rowing machine", "Horizontal bar": "a horizontal bar", "Balance beam": "a balance beam"}),
    group("What bags or luggage are in this picture?",
          {"Briefcase": "a briefcase", "Luggage and bags": "luggage", "Luggage": "luggage", "Satchel": "a satchel",
           "Picnic basket": "a picnic basket"}),
    group("Is there a cart or a big bin here?",
          {"Shopping cart": "a shopping cart", "Cart": "a cart", "Recycling bin": "a recycling bin",
           "Dumpster": "a dumpster (a large rubbish skip)"}),
    group("Is there a pool or hot tub here?",
          {"Swimming pool": "a swimming pool", "Jacuzzi": "a hot tub"},
          "Pool edges can be hard to find without sight."),
    group("What street things are in this picture?",
          {"Billboard": "a billboard", "Awning": "an awning", "Poster": "a poster",
           "Post box": "a post box (mailbox)"}),
    group("What pet things are in this picture?",
          {"Dog bed": "a dog bed", "Cat furniture": "cat furniture (a cat tree or scratching post)",
           "Kennel": "a kennel", "Aquarium": "an aquarium", "Birdhouse": "a birdhouse"}),
    group("What lights are in this picture?",
          {"Chandelier": "a chandelier", "Lampshade": "a lampshade", "Lantern": "a lantern",
           "Wind chime": "a wind chime"}),
]

OUTINGS = [
    group("What celebration things are in this picture?",
          {"Cake": "a cake", "Wreath": "a wreath", "Christmas tree": "a Christmas tree",
           "Christmas decoration": "Christmas decorations", "Gift wrapping": "wrapped presents",
           "Confetti": "confetti", "Fireworks": "fireworks"}),
    group("What outdoor gear is in this picture?",
          {"Binoculars": "binoculars", "Compass": "a compass", "Hiking equipment": "hiking equipment",
           "Fishing rod": "a fishing rod", "Tent": "a tent", "Personal flotation device": "a life jacket",
           "Sleeping bag": "a sleeping bag"}),
    group("What hats or coats are in this picture?",
          {"Sombrero": "a sombrero", "Tiara": "a tiara", "Crown": "a crown", "Raincoat": "a raincoat",
           "Trench coat": "a trench coat", "Overcoat": "an overcoat", "Waistcoat": "a waistcoat"}),
    group("What ceremony things are in this picture?",
          {"Trophy": "a trophy", "Medal": "a medal", "Podium": "a podium", "Megaphone": "a megaphone",
           "Flag": "a flag"}),
    group("What rides are in this picture?",
          {"Ferris wheel": "a Ferris wheel", "Roller coaster": "a roller coaster", "Carousel": "a carousel",
           "Playground slide": "a slide", "Water slide": "a water slide", "Swing (Seat)": "a swing",
           "Trampoline": "a trampoline", "Playground": "a playground"}),
    group("Is this a cemetery?",
          {"Headstone": "a headstone", "Grave": "a grave", "Cemetery": "a cemetery"}),
]

SEAFOOD_NOTE = "Shellfish and fish are common allergens: check with the cook if allergies matter."
FOOD_MORE = [
    group("What baked goods are in this picture?",
          {"Bagel": "a bagel", "Muffin": "a muffin", "Croissant": "a croissant", "Cupcake": "a cupcake",
           "Tart": "a tart", "Pastry": "pastry", "Doughnut": "a doughnut", "Pretzel": "a pretzel",
           "Waffle": "a waffle", "Pancake": "pancakes", "Cookie": "cookies", "Biscuit": "biscuits",
           "Pie": "a pie", "Baguette": "a baguette"}),
    group("What sauces or spreads are in this picture?",
          {"Guacamole": "guacamole", "Ketchup": "ketchup", "Mayonnaise": "mayonnaise",
           "Mustard (Food)": "mustard", "Gravy": "gravy", "Honey": "honey", "Pesto": "pesto", "Sauce": "a sauce",
           "Tomato sauce": "tomato sauce"}),
    group("What meat is in this picture?",
          {"Sausage": "sausages", "Hot dog": "a hot dog", "Bacon": "bacon", "Salami": "salami",
           "Meatball": "meatballs", "Kebab": "a kebab", "Pork": "pork"}),
    group("What seafood is in this picture?",
          {"Shrimp": "shrimp", "Prawn": "prawns", "Lobster": "lobster", "Crab": "crab", "Oyster": "oysters",
           "Mussel": "mussels", "Clam": "clams", "Scallops": "scallops", "Squid": "squid", "Octopus": "octopus",
           "Shellfish": "shellfish"}, SEAFOOD_NOTE),
    group("What drinks are in this picture?",
          {"Cocktail": "a cocktail", "Cocktail shaker": "a cocktail shaker", "Beer": "beer", "Wine": "wine",
           "Whisky": "whisky", "Champagne": "champagne", "Shot glass": "a shot glass"}),
    group("What Mexican food is in this picture?",
          {"Burrito": "a burrito", "Taco": "tacos", "Nachos": "nachos"}),
    group("What serving dishes are in this picture?",
          {"Platter": "a platter", "Serving tray": "a serving tray", "Tray": "a tray", "Cake stand": "a cake stand",
           "Teacup": "a teacup", "Placemat": "a placemat"}),
    group("What kitchen tools are in this picture?",
          {"Strainer": "a strainer", "Skewer": "skewers", "Toothpick": "toothpicks", "Funnel": "a funnel"}),
]

CARDS = [
    group("What kind of card or paper is this?",
          {"Business card": "a business card", "Greeting card": "a greeting card", "Postcard": "a postcard",
           "Ticket": "a ticket", "Receipt": "a receipt", "Menu": "a menu", "Calendar": "a calendar",
           "Coupon": "a coupon", "Badge": "a badge", "Identity document": "an identity document (a sample)",
           "Driver's license": "a driving licence (a sample)", "Passport": "a passport (a sample)"}),
]
# Kinds that hold a real person's details: only photos whose own title says they are a sample or specimen.
PERSONAL_PAPERS = {"Identity document", "Driver's license", "Passport"}
SAMPLE_TITLE = re.compile(r"\b(samples?|specimens?|muster|exemplar|mock-?up|dummy)\b", re.I)


def gap_labels(groups):
    """Every label of a pack's groups."""
    return {label for g in groups for label in g["things"]}


MASS_ENDING_S = {"octopus", "hummus", "asparagus", "hiking equipment", "luggage"}


def a_thing(words):
    """ "a urinal" stays; "luggage" becomes "any luggage" (for "Is there ...?" / "I can't see ...")."""
    return words if re.match(r"^(a|an|the)\s", words) else f"any {words}"


def plural(words):
    """True for words that name many things ("pancakes", "paper clips"), not one thing or a mass ("luggage")."""
    return not re.match(r"^(a|an|the)\s", words) and words.endswith("s") and not words.endswith("ss") \
        and words not in MASS_ENDING_S


def is_there(words):
    """ "Is there a urinal in this picture?" or "Are there any pancakes in this picture?"."""
    return f"{'Are there' if plural(words) else 'Is there'} {a_thing(words)} in this picture?"


def yes_there(words):
    """ "Yes, there is a urinal in this picture." or "Yes, there are pancakes in this picture."."""
    return f"Yes, there {'are' if plural(words) else 'is'} {words} in this picture."


def oi_gap_rows(labels, groups, rng, title=""):
    """Rows for one photo from its {label: 1 (confirmed) or 0 (checked, not there)}: each group with a confirmed
    label ("I can see a urinal and a hand dryer."), one "Is there ...?" yes from a confirmed label and one no from a
    label people found absent; [] when the photo has nothing for this pack or is left out."""
    yes = {n for n, c in labels.items() if c == 1}
    no = {n for n, c in labels.items() if c == 0}
    child = bool(yes & set(OI_CHILD))
    if yes & LEAVE_OUT or (child and yes & LEAVE_OUT_WITH_CHILD):
        return []
    if yes & PERSONAL_PAPERS and not SAMPLE_TITLE.search(title or ""):
        yes -= PERSONAL_PAPERS                       # a real person's papers: never asked about
    rows, said = [], []
    for g in groups:
        things = list(dict.fromkeys(words for label, words in g["things"].items() if label in yes))
        if not things:
            continue
        said += [label for label in g["things"] if label in yes]
        answer = f"I can see {listed(things[:6])}."
        if g is CARDS[0]:
            answer = f"It looks like {listed(things[:3])}. I can only say what kind it is, not what it says."
        if g["note"]:
            answer += " " + g["note"]
        rows.append({"question": g["question"], "answer": answer})
    if not rows:
        return []
    things = {label: words for g in groups for label, words in g["things"].items()}
    pick = rng.choice(sorted(said))
    if pick not in PERSONAL_PAPERS:
        rows.append({"question": is_there(things[pick]), "answer": yes_there(things[pick])})
    absent = sorted(n for n in no if n in things and n not in PERSONAL_PAPERS
                    and things[n] not in {things[s] for s in said})
    if absent:
        n = rng.choice(absent)
        rows.append({"question": is_there(things[n]),
                     "answer": f"No, I can't see {a_thing(things[n])} in this picture."})
    return [dict(r, child=True) if child else r for r in rows]


def oi_gap_labels(s, mids, quick=False):
    """{image id: {label: 1, 0 or None (people disagreed)}} for the wanted labels, read as the label lists download
    (the train list is about 2.7 GB); quick reads only the validation and test lists."""
    labels = {}
    for url in OI_GAP_LABELS[1:] if quick else OI_GAP_LABELS:
        for cells in csv.reader(oi_lines(s, url)):
            if len(cells) != 4 or cells[2] not in mids:
                continue
            try:
                value = round(float(cells[3]))
            except ValueError:
                continue
            found = labels.setdefault(cells[0], {})
            name = mids[cells[2]]
            found[name] = value if found.get(name, value) == value else None
        say(f"  Open Images: {len(labels)} photos with a wanted label after {url.rsplit('/', 1)[-1]}")
    return labels


def oi_gap_photos(s, wanted, quick=False):
    """{image id: (address, licence, author, page, title)} for the wanted photos whose own licence is free and that
    need no turning. Training photos Google did not copy to its own store (all but the "boxable" ones) are fetched
    from the original Flickr address the dataset gives."""
    boxable = set() if quick else {r["ImageID"] for r in csv.DictReader(oi_lines(s, OI_BOXABLE))
                                   if r["ImageID"] in wanted}
    photos = {}
    for url in OI_GAP_IMAGES[1:] if quick else OI_GAP_IMAGES:
        subset = "train" if "train" in url else "validation" if "validation" in url else "test"
        for r in csv.DictReader(oi_lines(s, url)):
            image_id = r["ImageID"]
            if image_id not in wanted:
                continue
            licence = oi_licence_name(r.get("License") or "", image_id)
            if not licence or (r.get("Rotation") or "0") not in ("0", "0.0", ""):
                continue
            address = OI_PICTURE.format(subset=subset, image_id=image_id) \
                if subset != "train" or image_id in boxable else r.get("OriginalURL") or ""
            if address:
                photos[image_id] = (address, licence, clean(r.get("Author")) or "an unnamed photographer",
                                    r.get("OriginalLandingURL") or "", clean(r.get("Title")))
    return photos


def build_oi_gap(key, groups, limit, seed):
    """One gap pack: the wanted labels' photos, each with rows from oi_gap_rows; the rarest label first, so a bidet
    or an infant bed is not crowded out by cakes, and photos in Google's own store before Flickr ones."""
    s, rng = session(), pass_random(seed)
    wanted = gap_labels(groups) | set(OI_CHILD) | LEAVE_OUT | LEAVE_OUT_WITH_CHILD
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2 and line[1] in wanted:
            mids.setdefault(line[0], line[1])
    asked = gap_labels(groups)
    say(f"Open Images {key}: {len(set(mids.values()) & asked)} of {len(asked)} labels found in the class list")
    labels = oi_gap_labels(s, mids, QUICK["on"])
    labels = {i: v for i, v in labels.items() if any(c == 1 and n in asked for n, c in v.items())}
    photos = oi_gap_photos(s, set(labels), QUICK["on"])
    counts = {}
    for v in labels.values():
        for n, c in v.items():
            if c == 1 and n in asked:
                counts[n] = counts.get(n, 0) + 1
    say(f"Open Images {key}: {len(labels)} photos with a label confirmed, {len(photos)} free; by label: " +
        ", ".join(f"{n} {c}" for n, c in sorted(counts.items(), key=lambda x: -x[1])))
    items = []
    for image_id in sorted(labels):
        if image_id not in photos:
            continue
        address, licence, author, page, title = photos[image_id]
        rows = oi_gap_rows(labels[image_id], groups, rng, title)
        if not rows:
            continue
        credit = CREDIT.format(author=author, page=f" ({page})" if page else "", licence=licence)
        rarest = min(counts.get(n, 10 ** 7) for n, c in labels[image_id].items() if c == 1 and n in asked)
        items.append(((rarest + rng.random(), "flickr" in address), image_id, f"{key.replace('_', '-')}-{image_id}.jpg",
                      address, [dict(r, credit=credit) for r in rows]))
    # Each label gets at most a fair share, so the common ones (cakes, posters) do not fill the pack.
    share = max(20, int(limit * 1.2) // max(1, len(counts)))
    taken, chosen = {}, []
    for _, image_id, name, address, rows in sorted(items, key=lambda x: x[0]):
        first = min((n for n, c in labels[image_id].items() if c == 1 and n in asked), key=lambda n: counts.get(n, 0))
        if taken.get(first, 0) >= share:
            continue
        taken[first] = taken.get(first, 0) + 1
        chosen.append((name, address, rows))
    chosen.sort(key=lambda x: "flickr" in x[1])
    chosen = chosen[:int(limit * 1.15) + 2]
    say(f"Open Images {key}: {len(chosen)} photos chosen of {len(items)}")
    return with_twins(fetch_all(chosen, workers=8)[:limit])


def build_open_images_public_home(limit):
    """open_images_public_home (see the module docstring)."""
    return build_oi_gap("open_images_public_home", PUBLIC_HOME, limit, 9101)


def build_open_images_outings(limit):
    """open_images_outings (see the module docstring)."""
    return build_oi_gap("open_images_outings", OUTINGS, limit, 9102)


def build_open_images_food_more(limit):
    """open_images_food_more (see the module docstring)."""
    return build_oi_gap("open_images_food_more", FOOD_MORE, limit, 9103)


def build_open_images_cards_documents(limit):
    """open_images_cards_documents (see the module docstring)."""
    return build_oi_gap("open_images_cards_documents", CARDS, limit, 9104)


OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
OI_GAPS_PACKS = {
    "open_images_public_home": (build_open_images_public_home, OI_LICENCE),
    "open_images_outings": (build_open_images_outings, OI_LICENCE),
    "open_images_food_more": (build_open_images_food_more, OI_LICENCE),
    "open_images_cards_documents": (build_open_images_cards_documents, OI_LICENCE),
}
OI_GAPS_LIMITS = {
    "open_images_public_home": 4000,      # 61 labels; train, validation and test sets
    "open_images_outings": 3000,          # 37 labels
    "open_images_food_more": 4000,        # 61 labels
    "open_images_cards_documents": 800,   # 12 labels, few photos each
}


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an Open Images gap pack builder.")
    parser.add_argument("key", choices=sorted(OI_GAPS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = OI_GAPS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:300])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
