"""Pack builders for food pictures, used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}.
A picture that has more than one question comes once with its JPEG and then again as (None, None, row) rows whose
"file" names the same picture (as build_packs.add_translations does), so the zip holds each picture only once. The
limit counts pictures.

  open_images_food  Google Open Images V7 (validation and test sets): food photos with the labels people checked by
                    hand (labels CC BY 4.0; each photo CC BY 2.0 with its photographer named). "What food is in this
                    picture?", and where people checked it: "How is this egg cooked?", "Is this food frozen?" and
                    "Is there mould on this food?".
  grocery_store     The Grocery Store Dataset (Klasson, Zhang and Kjellstrom, 2019, MIT licence): photos the authors
                    took in Swedish shops of fruit, vegetables and cartons, made with visually impaired shoppers in
                    mind (only these natural photos, not the downloaded "iconic" product pictures). "What is this?"
  fish_eyes         The Freshness of the Fish Eyes dataset (Prasetyo et al., Mendeley Data xzyx7pbr3w, CC BY 4.0):
                    close photos of the eyes of eight kinds of fish on days 1-2, 3-4 and 5-6. "How fresh is this
                    fish?"
  commons_food      Wikimedia Commons categories of eggs cooked in different ways, rice, toast, frozen food, steaks,
                    spoiled food and expiry dates: pictures CC0, public domain or CC BY (author credited). A question
                    the category answers ("How is this egg cooked?" "It is fried."), and the file's English caption
                    or description where it is a real description.

    python packs/food_packs.py grocery_store --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import json
import random
import re
import sys
import time

from build_packs import (session, clean, smaller, fetch_all, first_sentences, say, article,  # noqa: F401
                         ALT_TEXT, COMMONS_API, COMMONS_FREE, LONG_SIDE)


# ----------------------------------------------------------------- shared helpers

def sentence(text):
    """Text starting with a capital letter and ending with a full stop."""
    text = text.strip()
    if not text:
        return text
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".!?" else text + "."


def listed(words):
    """Words joined in plain English: "a", "a and b", "a, b and c"."""
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def with_twins(fetched):
    """Fetched pictures whose row is a list of rows, as pack entries: the first row with the picture, the others as
    (None, None, row) pointing at the same picture."""
    out = []
    for name, data, rows in fetched:
        out.append((name, data, rows[0]))
        out += [(None, None, dict(r, file=f"pictures/{name}")) for r in rows[1:]]
    return out


def count_pictures(entries):
    """How many entries carry a picture."""
    return sum(1 for _, data, _ in entries if data is not None)


# ----------------------------------------------------------------- Open Images V7 (Google)

OI = "https://storage.googleapis.com/openimages/"
OI_LABELS = (OI + "v7/oidv7-val-annotations-human-imagelabels.csv", OI + "v7/oidv7-test-annotations-human-imagelabels.csv")
OI_CLASSES = OI + "v7/oidv7-class-descriptions.csv"
OI_IMAGES = (OI + "2018_04/validation/validation-images-with-rotation.csv",
             OI + "2018_04/test/test-images-with-rotation.csv")
OI_PICTURE = "https://open-images-dataset.s3.amazonaws.com/{subset}/{image_id}.jpg"    # subset: validation or test
# The licences a photo may have to be used (Open Images lists all as CC BY 2.0, but each is checked).
OI_FREE = re.compile(r"creativecommons\.org/(licenses/by/(\d\.\d)/?$|publicdomain/(zero|mark)/)")

# The food labels, most specific first, with the plain words used in the answer. Open Images' "Fish" is the animal
# (an aquarium fish is labelled "Fish" too), so it is named only on pictures that other labels show to be food.
OI_FOOD = {
    "Fried egg": "a fried egg", "Poached egg": "a poached egg", "Boiled egg": "a boiled egg",
    "Scrambled eggs": "scrambled eggs", "Omelette": "an omelette",
    "Sirloin steak": "sirloin steak", "Roast beef": "roast beef", "Chicken meat": "chicken",
    "Hamburger": "a hamburger", "Pizza": "pizza", "Sushi": "sushi", "Pasta": "pasta", "French fries": "French fries",
    "Steamed rice": "steamed rice", "White rice": "white rice", "Toast": "toast", "Salmon (Food)": "salmon",
    "Apple": "apples", "Banana": "bananas", "Orange (fruit)": "oranges", "Mandarin orange": "mandarins",
    "Lemon (plant)": "lemons", "Lime (Fruit)": "limes", "Grapefruit": "grapefruit", "Strawberry": "strawberries",
    "Raspberry": "raspberries", "Blueberry": "blueberries", "Blackberry (Plant)": "blackberries", "Cherry": "cherries",
    "Grape": "grapes", "Pear": "pears", "Peach": "peaches", "Apricot": "apricots", "Mango": "mangoes",
    "Pineapple": "pineapple", "Watermelon": "watermelon", "Cantaloupe": "cantaloupe melon", "Melon": "melon",
    "Papaya": "papaya", "Kiwifruit": "kiwi fruit", "Pomegranate": "pomegranates", "Avocado": "avocados",
    "Olive": "olives",
    "Tomato": "tomatoes", "Carrot": "carrots", "Broccoli": "broccoli", "Cauliflower": "cauliflower",
    "Cabbage": "cabbage", "Brussels sprout": "Brussels sprouts", "Lettuce": "lettuce", "Spinach": "spinach",
    "Cucumber": "cucumbers", "Zucchini": "courgettes (zucchini)", "Eggplant": "aubergines (eggplants)",
    "Bell pepper": "bell peppers", "Chili pepper": "chilli peppers", "Potato": "potatoes",
    "Sweet potato": "sweet potatoes", "Onion": "onions", "Garlic": "garlic", "Leek": "leeks",
    "Asparagus": "asparagus", "Green bean": "green beans", "Pea": "peas", "Common bean": "beans",
    "Corn": "sweetcorn", "Pumpkin": "pumpkins", "Mushroom": "mushrooms", "Radish": "radishes",
    "Beetroot": "beetroot", "Artichoke": "artichokes",
    "Salad": "salad", "Steak": "steak", "Beef": "beef", "Red meat": "red meat", "Rice": "rice",
    "Fish (Food)": "fish", "Fish": "fish", "Bread": "bread", "Barbecue": "barbecued food", "Leftovers": "leftovers",
    "Egg": "eggs", "Frozen food": "frozen food", "Seafood": "seafood", "Meat": "meat", "Baked goods": "baked goods",
    "Fruit": "fruit", "Vegetable": "vegetables", "Fast food": "fast food", "Food": "food",
}
OI_FRUIT = {"Apple", "Banana", "Orange (fruit)", "Mandarin orange", "Lemon (plant)", "Lime (Fruit)", "Grapefruit",
            "Strawberry", "Raspberry", "Blueberry", "Blackberry (Plant)", "Cherry", "Grape", "Pear", "Peach",
            "Apricot", "Mango", "Pineapple", "Watermelon", "Cantaloupe", "Melon", "Papaya", "Kiwifruit",
            "Pomegranate", "Avocado", "Olive"}
OI_VEGETABLES = {"Tomato", "Carrot", "Broccoli", "Cauliflower", "Cabbage", "Brussels sprout", "Lettuce", "Spinach",
                 "Cucumber", "Zucchini", "Eggplant", "Bell pepper", "Chili pepper", "Potato", "Sweet potato", "Onion",
                 "Garlic", "Leek", "Asparagus", "Green bean", "Pea", "Common bean", "Corn", "Pumpkin", "Mushroom",
                 "Radish", "Beetroot", "Artichoke"}
OI_EGG_STYLES = {"Fried egg": "It is fried.", "Boiled egg": "It is boiled.", "Poached egg": "It is poached.",
                 "Scrambled eggs": "It is scrambled.", "Omelette": "It is made into an omelette."}
OI_MEATS = {"Sirloin steak", "Roast beef", "Steak", "Beef", "Red meat", "Chicken meat"}
# A general label is left out of the answer when a more specific one is there ("sirloin steak", not "sirloin steak,
# steak, beef and meat"); "Food" is left out when anything else is named.
OI_COVERED_BY = {
    "Steak": {"Sirloin steak"}, "Beef": {"Sirloin steak", "Roast beef", "Steak"},
    "Red meat": {"Sirloin steak", "Roast beef", "Steak", "Beef"}, "Meat": OI_MEATS | {"Hamburger"},
    "Rice": {"Steamed rice", "White rice"}, "White rice": {"Steamed rice"},
    "Bread": {"Toast"}, "Baked goods": {"Bread", "Toast", "Pizza", "Hamburger"},
    "Fish": {"Salmon (Food)", "Fish (Food)"}, "Fish (Food)": {"Salmon (Food)"},
    "Seafood": {"Fish", "Fish (Food)", "Salmon (Food)", "Sushi"}, "Egg": set(OI_EGG_STYLES),
    "Fruit": OI_FRUIT, "Vegetable": OI_VEGETABLES | {"Salad"}, "Fast food": {"Hamburger", "French fries", "Pizza"},
}
# Labels that show a picture is of food (one must be verified present). A fruit or vegetable label alone is not
# enough: "Cherry" is also given to cherry trees in blossom.
OI_IS_FOOD = {"Food", "Fast food", "Baked goods", "Fruit", "Vegetable", "Dish", "Cuisine", "Meal", "Produce"}
# Frozen desserts: a picture of ice cream is not asked "Is this food frozen?" (its "Frozen food" label means packs
# of frozen food, so "no" would be wrong).
OI_FROZEN_DESSERTS = {"Ice cream", "Gelato", "Frozen yogurt", "Sorbet", "Semifreddo", "Frozen dessert", "Ice pop"}
OI_ASK_FOOD = "What food is in this picture?"
OI_ASK_EGG = "How is this egg cooked?"
OI_ASK_FROZEN = "Is this food frozen?"
OI_ASK_MOULD = "Is there mould on this food?"


def oi_lines(s, url):
    """The lines of a large CSV file, read as it downloads."""
    with s.get(url, timeout=600, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if line:
                yield line


def oi_licence_name(url):
    """ "CC BY 2.0" (and so on) for a Creative Commons address."""
    m = OI_FREE.search(url)
    if not m:
        return ""
    if m.group(2):
        return f"CC BY {m.group(2)}"
    return "CC0" if m.group(3) == "zero" else "Public Domain Mark"


def oi_food_answer(present):
    """ "It shows a fried egg, toast and salad." for the verified-present food labels, or "" when only "Food" (or
    nothing) is there."""
    named = [n for n in OI_FOOD if n in present and not (OI_COVERED_BY.get(n, set()) & present)]
    if "Food" in named and len(named) > 1:
        named.remove("Food")
    words = []
    for n in named:
        if OI_FOOD[n] not in words:
            words.append(OI_FOOD[n])
    if not words or words == ["food"]:
        return ""
    return f"It shows {listed(words[:6])}."


def oi_rows(labels):
    """The rows for one picture from its {label name: 1 (verified present) or 0 (verified absent)}: [] when it is
    not a picture of food."""
    present = {n for n, c in labels.items() if c == 1}
    absent = {n for n, c in labels.items() if c == 0}
    if not (present & OI_IS_FOOD) or "Food" in absent:
        return []
    rows = []
    answer = oi_food_answer(present)
    if answer:
        rows.append({"question": OI_ASK_FOOD, "answer": answer})
    styles = [n for n in OI_EGG_STYLES if n in present]
    if len(styles) == 1:
        rows.append({"question": OI_ASK_EGG, "answer": OI_EGG_STYLES[styles[0]]})
    if "Frozen food" in present:
        rows.append({"question": OI_ASK_FROZEN, "answer": "Yes, it is frozen."})
    elif "Frozen food" in absent and not (present & OI_FROZEN_DESSERTS):
        rows.append({"question": OI_ASK_FROZEN, "answer": "No, it is not frozen."})
    if "Mold" in present:
        rows.append({"question": OI_ASK_MOULD, "answer": "Yes, there is mould on it: do not eat it."})
    elif "Mold" in absent:
        rows.append({"question": OI_ASK_MOULD, "answer": "No, there is no mould on it."})
    return rows


def build_open_images_food(limit):
    """The Open Images food pack's pictures: [(name, JPEG or None, row)]. Reads the labels people checked on the
    validation and test sets (about 120 MB of lists), keeps food photos whose own licence is free and that need no
    turning, and fetches the photos: first every one with an egg, frozen or mould question, then others at random."""
    s = session()
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = set(OI_FOOD) | OI_IS_FOOD | OI_FROZEN_DESSERTS | {"Mold"}
    names = {mids[n]: n for n in wanted if n in mids}
    say(f"Open Images: {len(names)} of {len(wanted)} food labels found in the class list")
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
                # Two checks that disagree make the label unknown (None).
                picture[name] = confidence if picture.get(name, confidence) == confidence else None
    say(f"Open Images: {len(labels)} pictures with a food label checked")
    photos = {}
    for url in OI_IMAGES:
        for r in csv.DictReader(oi_lines(s, url)):
            licence = oi_licence_name(r.get("License") or "")
            if r["ImageID"] in labels and licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[r["ImageID"]] = (r["Subset"], licence, clean(r.get("Author")) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
    items, special = [], []
    counts = {}
    for image_id, picture in labels.items():
        if image_id not in photos:
            continue
        rows = oi_rows(picture)
        if not rows:
            continue
        subset, licence, author, page = photos[image_id]
        credit = (f"Photo by {author}" + (f" ({page})" if page else "") + f", {licence}; labels from Open Images V7 "
                  f"(Google), CC BY 4.0")
        rows = [dict(r, credit=credit) for r in rows]
        for r in rows:
            counts[(r["question"], r["answer"])] = counts.get((r["question"], r["answer"]), 0) + 1
        item = (f"oi-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id), rows)
        (special if any(r["question"] != OI_ASK_FOOD for r in rows) else items).append(item)
    for (question, answer), n in sorted(counts.items()):
        if question != OI_ASK_FOOD:
            say(f"  {question} {answer}: {n}")
    say(f"Open Images: {len(special)} pictures with an egg, frozen or mould question, {len(items)} more with "
        f"'{OI_ASK_FOOD}' only")
    random.Random(41).shuffle(special)
    random.Random(42).shuffle(items)
    chosen = (special + items)[:int(limit * 1.1) + 2]
    fetched = fetch_all(chosen, workers=8)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Grocery Store Dataset (Klasson et al.)

GROCERY = "https://raw.githubusercontent.com/marcusklasson/GroceryStoreDataset/master/dataset/"
GROCERY_SPLITS = ("train.txt", "val.txt", "test.txt")    # the natural photos only (the iconic ones are not listed)
# A readable answer for each of the 81 fine classes. Fruit and vegetables were photographed on shop displays, mostly
# in piles, so they are named in the plural; packages were mostly photographed one at a time, held in the hand.
GROCERY_ANSWERS = {
    "Golden-Delicious": "These are Golden Delicious apples.", "Granny-Smith": "These are Granny Smith apples.",
    "Pink-Lady": "These are Pink Lady apples.", "Red-Delicious": "These are Red Delicious apples.",
    "Royal-Gala": "These are Royal Gala apples.", "Avocado": "These are avocados.", "Banana": "These are bananas.",
    "Kiwi": "These are kiwi fruit.", "Lemon": "These are lemons.", "Lime": "These are limes.",
    "Mango": "These are mangoes.", "Cantaloupe": "These are cantaloupe melons.", "Galia-Melon": "These are Galia melons.",
    "Honeydew-Melon": "These are honeydew melons.", "Watermelon": "These are watermelons.",
    "Nectarine": "These are nectarines.", "Orange": "These are oranges.", "Papaya": "These are papayas.",
    "Passion-Fruit": "These are passion fruit.", "Peach": "These are peaches.", "Anjou": "These are Anjou pears.",
    "Conference": "These are Conference pears.", "Kaiser": "These are Kaiser pears.",
    "Pineapple": "These are pineapples.", "Plum": "These are plums.", "Pomegranate": "These are pomegranates.",
    "Red-Grapefruit": "These are red grapefruit.", "Satsumas": "These are satsumas.",
    "Bravo-Apple-Juice": "This is a carton of Bravo apple juice.",
    "Bravo-Orange-Juice": "This is a carton of Bravo orange juice.",
    "God-Morgon-Apple-Juice": "This is a carton of God Morgon apple juice.",
    "God-Morgon-Orange-Juice": "This is a carton of God Morgon orange juice.",
    "God-Morgon-Orange-Red-Grapefruit-Juice": "This is a carton of God Morgon orange and red grapefruit juice.",
    "God-Morgon-Red-Grapefruit-Juice": "This is a carton of God Morgon red grapefruit juice.",
    "Tropicana-Apple-Juice": "This is a carton of Tropicana apple juice.",
    "Tropicana-Golden-Grapefruit": "This is a carton of Tropicana golden grapefruit juice.",
    "Tropicana-Juice-Smooth": "This is a carton of Tropicana Smooth orange juice.",
    "Tropicana-Mandarin-Morning": "This is a carton of Tropicana Mandarin Morning juice.",
    "Arla-Ecological-Medium-Fat-Milk": "This is a carton of Arla organic medium-fat milk.",
    "Arla-Lactose-Medium-Fat-Milk": "This is a carton of Arla lactose-free medium-fat milk.",
    "Arla-Medium-Fat-Milk": "This is a carton of Arla medium-fat milk.",
    "Arla-Standard-Milk": "This is a carton of Arla standard milk.",
    "Garant-Ecological-Medium-Fat-Milk": "This is a carton of Garant organic medium-fat milk.",
    "Garant-Ecological-Standard-Milk": "This is a carton of Garant organic standard milk.",
    "Oatly-Natural-Oatghurt": "This is a carton of Oatly natural oatgurt (oat yoghurt).",
    "Oatly-Oat-Milk": "This is a carton of Oatly oat milk.",
    "Arla-Ecological-Sour-Cream": "This is a carton of Arla organic sour cream.",
    "Arla-Sour-Cream": "This is a carton of Arla sour cream.",
    "Arla-Sour-Milk": "This is a carton of Arla sour milk.",
    "Alpro-Blueberry-Soyghurt": "This is a pack of Alpro blueberry soya yoghurt.",
    "Alpro-Vanilla-Soyghurt": "This is a pack of Alpro vanilla soya yoghurt.",
    "Alpro-Fresh-Soy-Milk": "This is a carton of Alpro fresh soya milk.",
    "Alpro-Shelf-Soy-Milk": "This is a carton of Alpro long-life soya milk.",
    "Arla-Mild-Vanilla-Yoghurt": "This is a carton of Arla mild vanilla yoghurt.",
    "Arla-Natural-Mild-Low-Fat-Yoghurt": "This is a carton of Arla natural mild low-fat yoghurt.",
    "Arla-Natural-Yoghurt": "This is a carton of Arla natural yoghurt.",
    "Valio-Vanilla-Yoghurt": "This is a carton of Valio vanilla yoghurt.",
    "Yoggi-Strawberry-Yoghurt": "This is a carton of Yoggi strawberry yoghurt.",
    "Yoggi-Vanilla-Yoghurt": "This is a carton of Yoggi vanilla yoghurt.",
    "Asparagus": "This is asparagus.", "Aubergine": "These are aubergines (eggplants).",
    "Cabbage": "These are cabbages.", "Carrots": "These are carrots.", "Cucumber": "These are cucumbers.",
    "Garlic": "This is garlic.", "Ginger": "This is ginger root.", "Leek": "These are leeks.",
    "Brown-Cap-Mushroom": "These are brown cap mushrooms.", "Yellow-Onion": "These are yellow onions.",
    "Green-Bell-Pepper": "These are green bell peppers.", "Orange-Bell-Pepper": "These are orange bell peppers.",
    "Red-Bell-Pepper": "These are red bell peppers.", "Yellow-Bell-Pepper": "These are yellow bell peppers.",
    "Floury-Potato": "These are floury potatoes.", "Solid-Potato": "These are firm (waxy) potatoes.",
    "Sweet-Potato": "These are sweet potatoes.", "Red-Beet": "These are beetroots.",
    "Beef-Tomato": "These are beef tomatoes.", "Regular-Tomato": "These are tomatoes.",
    "Vine-Tomato": "These are vine tomatoes.", "Zucchini": "These are courgettes (zucchini).",
}


def grocery_answer(fine, coarse):
    """The answer for a fine class; a class missing from GROCERY_ANSWERS is named from its class names."""
    if fine in GROCERY_ANSWERS:
        return GROCERY_ANSWERS[fine]
    words = fine.replace("-", " ")
    kind = coarse.replace("-", " ").lower()
    return sentence(f"this is {words}" + ("" if kind in words.lower() else f" ({kind})"))


def build_grocery_store(limit):
    """The Grocery Store pack's pictures: [(name, JPEG, row)]. Reads the class list and the train, validation and
    test lists (paths of the natural photos with their fine and coarse class), then fetches the photos."""
    s, items = session(), []
    classes = {}
    for r in csv.reader(s.get(GROCERY + "classes.csv", timeout=60).text.splitlines()[1:]):
        if len(r) >= 4:
            classes[int(r[1])] = (r[0].strip(), r[2].strip())
    for split in GROCERY_SPLITS:
        for line in s.get(GROCERY + split, timeout=60).text.splitlines():
            cells = [c.strip() for c in line.split(",")]
            if len(cells) < 3 or "iconic" in cells[0].lower() or not cells[0].lower().endswith(".jpg"):
                continue
            fine, coarse = classes.get(int(cells[1]), (cells[0].split("/")[-2], ""))
            items.append((f"grocery-{cells[0].replace('/', '-')}", GROCERY + cells[0],
                          {"question": "What is this?", "answer": grocery_answer(fine, coarse),
                           "credit": "Grocery Store Dataset (Klasson, Zhang and Kjellstrom, 2019), MIT licence, "
                                     "https://github.com/marcusklasson/GroceryStoreDataset"}))
    say(f"Grocery Store Dataset: {len(items)} natural photos in {len(classes)} classes")
    random.Random(43).shuffle(items)
    return fetch_all(items[:int(limit * 1.05) + 2], workers=8)[:limit]


# ----------------------------------------------------------------- Freshness of the Fish Eyes (Mendeley Data)

FISH_EYES = "xzyx7pbr3w"
FISH_API = f"https://data.mendeley.com/public-api/datasets/{FISH_EYES}"
# The eight species (folder names use the Latin name) with their common English names.
FISH_SPECIES = {
    "chanos chanos": ("milkfish", "Chanos chanos"),
    "johnius trachycephalus": ("leaftail croaker", "Johnius trachycephalus"),
    "nibea albiflora": ("yellow drum", "Nibea albiflora"),
    "rastrelliger faughni": ("island mackerel", "Rastrelliger faughni"),
    "upeneus moluccensis": ("goldband goatfish", "Upeneus moluccensis"),
    "eleutheronema tetradactylum": ("fourfinger threadfin", "Eleutheronema tetradactylum"),
    "oreochromis mossambicus": ("Mozambique tilapia", "Oreochromis mossambicus"),
    "oreochromis niloticus": ("Nile tilapia", "Oreochromis niloticus"),
}
# The dataset's three classes (days 1-2, 3-4 and 5-6), judged from the fish's eye.
FISH_ANSWERS = {
    "highly fresh": "This {fish} looks very fresh: its eye is clear and bright.",
    "fresh": "This {fish} looks fairly fresh: its eye is no longer at its brightest, so eat it soon.",
    "not fresh": "This {fish} is no longer fresh: do not eat it.",
}


def fish_class(folder):
    """(species key, freshness key) from a folder name such as "Nibea Albiflora -  Highly Fresh", or None."""
    m = re.match(r"(.+?)\s*-\s*(highly fresh|not fresh|fresh)\s*$", " ".join(folder.lower().split()))
    if not m or m.group(1) not in FISH_SPECIES:
        return None
    return m.group(1), m.group(2)


def build_fish_eyes(limit):
    """The fish eyes pack's pictures: [(name, JPEG, row)]. The dataset's files are single photos, each in a folder
    named "<species> - <Highly Fresh | Fresh | Not Fresh>"; the folders come from the API's folders/<version>
    list."""
    s = session()
    record = s.get(FISH_API, timeout=60).json()
    licence = (record.get("data_licence") or {}).get("short_name", "")
    if licence != "CC BY 4.0":
        raise SystemExit(f"Fish eyes dataset: licence is now {licence!r}, not CC BY 4.0; check it before building.")
    version = record.get("version", 1)
    folders = {f["id"]: f["name"] for f in s.get(f"{FISH_API}/folders/{version}", timeout=60).json()}
    items = []
    for f in record.get("files") or []:
        got = fish_class(folders.get(f.get("folder_id"), ""))
        url = (f.get("content_details") or {}).get("download_url")
        if not got or not url or not f.get("filename", "").lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        species, freshness = got
        common, latin = FISH_SPECIES[species]
        items.append((f"fisheye-{f['id']}.jpg", url,
                      {"question": "How fresh is this fish?",
                       "answer": FISH_ANSWERS[freshness].format(fish=f"{common} ({latin})"),
                       "credit": "The Freshness of the Fish Eyes Dataset (Prasetyo, Purbaningtyas, Adityo, Suciati "
                                 "and Fatichah), Mendeley Data xzyx7pbr3w, CC BY 4.0"}))
    say(f"Fish eyes: {len(items)} photos in {len(folders)} folders")
    random.Random(44).shuffle(items)
    return fetch_all(items[:int(limit * 1.05) + 2], workers=4, pause=0.1)[:limit]


# ----------------------------------------------------------------- Wikimedia Commons food categories

# Each category with the question it answers for every picture in it, and whether one level of its subcategories
# is used too.
COMMONS_FOOD = {
    "Fried eggs": ("How is this egg cooked?", "It is fried.", True),
    "Boiled eggs": ("How is this egg cooked?", "It is boiled.", False),
    "Soft-boiled eggs": ("How is this egg cooked?", "It is soft-boiled.", True),
    "Raw eggs": ("How is this egg cooked?", "It is not cooked: it is raw.", False),
    "Scrambled eggs": ("How is this egg cooked?", "It is scrambled.", True),
    "Poached eggs": ("How is this egg cooked?", "It is poached.", True),
    "Cooked rice": ("Is this rice cooked?", "Yes, it is cooked.", False),
    "Toast": ("Is this bread toasted?", "Yes, it is toasted.", False),
    "Frozen food": ("Is this food frozen?", "Yes, it is frozen.", True),
    "Frozen fish": ("Is this food frozen?", "Yes, it is frozen.", False),
    "Frozen vegetables": ("Is this food frozen?", "Yes, it is frozen.", False),
    "Steaks": ("What food is this?", "This is a steak.", False),
    "Beef steaks": ("What food is this?", "This is a beef steak.", False),
    "Steak tartare": ("Is this meat cooked?", "No: this is steak tartare, raw minced beef.", False),
    "Spoiled food": ("Is this food safe to eat?", "No: it is spoiled (mouldy).", True),
    "Rhizopus stolonifer": ("Is this food safe to eat?", "No: it is spoiled (mouldy).", False),
    "Expiration dates": ("What does this label show?", "It shows an expiry date (a best-before or use-by date).",
                         False),
}
# Subcategories that are about pictures of food, not drawings, signs or dishes in art.
COMMONS_NOT_FOOD = re.compile(r"\b(art|drawings?|illustrations?|paintings?|logos?|icons?|emoji|sculptures?|"
                              r"signs?|advertis\w*|toys?|models?|in literature|people|videos?|audio|"
                              r"microscop\w*|diagrams?)\b", re.I)
# Rhizopus stolonifer pictures must show food (the category also holds microscope pictures of the mould itself).
COMMONS_ON_FOOD = re.compile(r"bread|fruit|food|strawberr|tomato|peach|grape|berry|apple|potato|vegetable|loaf|"
                             r"cake|meal|cheese|onion|pepper|melon|banana|plum|citrus|orange|lemon", re.I)


def commons_get(s, params, tries=8):
    """A Commons API answer (JSON), waiting and trying again politely when the server asks to slow down (429, 503,
    "maxlag"): it waits as long as the server says, or 5, 10, 20 ... seconds up to two minutes."""
    params = dict(params, format="json", maxlag=5)
    wait = 5
    for _ in range(tries):
        try:
            r = s.get(COMMONS_API, params=params, timeout=60)
            if r.status_code == 200:
                data = r.json()
                if (data.get("error") or {}).get("code") != "maxlag":
                    return data
            elif r.status_code not in (429, 500, 502, 503, 504):
                r.raise_for_status()
            after = r.headers.get("Retry-After", "")
            pause = int(after) if after.isdigit() else wait
        except ValueError:                             # not JSON (an error page): wait and try again
            pause = wait
        except Exception:  # noqa: BLE001 - network trouble: wait and try again
            pause = wait
        say(f"  Commons asked to slow down: waiting {min(pause, 120)} seconds")
        time.sleep(min(pause, 120))
        wait = min(wait * 2, 120)
    raise RuntimeError("Wikimedia Commons kept refusing requests (429); try again later.")


def commons_members(s, category, kind):
    """The titles of a category's members of one kind ("file" or "subcat")."""
    titles, params = [], {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                          "cmtype": kind, "cmlimit": 500}
    while True:
        data = commons_get(s, params)
        titles += [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])]
        if "continue" not in data:
            return titles
        params.update(data["continue"])
        time.sleep(1)


def commons_description(caption, description):
    """The file's English caption, or else the first sentences of its description, when it is a real description
    (5 words or more), as a sentence; or ""."""
    for text in (clean(caption), first_sentences(re.sub(r"^\s*English\s*:\s*", "", clean(description)), 60)):
        if len(text.split()) >= 5 and not re.match(r"^[\d\W]", text) and not text.lower().startswith("file:"):
            return sentence(text)
    return ""


def commons_entries(s, titles):
    """[(title, picture address, credit, caption or description)] for files whose picture is CC0, public domain
    or CC BY (never BY-SA or NC), 50 files a request."""
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": LONG_SIDE,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription",
                               "iiextmetadatalanguage": "en"})
        pages = [p for p in ((data.get("query") or {}).get("pages") or {}).values() if p.get("pageid")]
        captions = {}
        if pages:
            entities = commons_get(s, {"action": "wbgetentities", "ids": "|".join(f"M{p['pageid']}" for p in pages),
                                       "props": "labels", "languages": "en"}).get("entities", {})
            captions = {k: ((v.get("labels") or {}).get("en") or {}).get("value", "") for k, v in entities.items()}
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            upper = licence.upper()
            if not COMMONS_FREE.match(licence) or "SA" in upper or "NC" in upper or "ND" in upper \
                    or info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            credit = f"{p['title']} by {artist}, {licence}, {page}"
            text = commons_description(captions.get(f"M{p['pageid']}"), (meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], credit, text))
        time.sleep(1)
    return out


def build_commons_food(limit):
    """The Commons food pack's pictures: [(name, JPEG, row)]. For each category: its files (and those of its
    subcategories where COMMONS_FOOD says so, leaving out drawings, signs and art), the free ones, each with the
    category's question and, when the file has a real caption or description, "Write a short description ...".
    The categories share the limit, so no single category fills the pack."""
    s, items, seen = session(), [], set()
    per_category = max(10, limit // len(COMMONS_FOOD) * 2)
    for category, (question, answer, deeper) in COMMONS_FOOD.items():
        titles = commons_members(s, category, "file")
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                if not COMMONS_NOT_FOOD.search(sub):
                    titles += commons_members(s, sub.split(":", 1)[-1], "file")
        titles = [t for t in dict.fromkeys(titles) if t not in seen]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_entries(s, titles[:per_category * 3]):
            if category == "Rhizopus stolonifer" and not COMMONS_ON_FOOD.search(f"{title} {text}"):
                continue
            seen.add(title)
            rows = [{"question": question, "answer": answer, "credit": credit}]
            if text:
                rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
            name = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
            items.append((f"commons-food-{name}.jpg", url, rows))
            found += 1
            if found >= per_category:
                break
        say(f"Commons {category}: {found} free pictures ({len(titles)} files)")
    random.Random(45).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- the packs

FOOD_PACKS = {
    "open_images_food": (build_open_images_food, "Open Images V7 (Google): image-level labels verified by people, CC BY "
                                                 "4.0, https://storage.googleapis.com/openimages/web/index.html. Each "
                                                 "photo is CC BY 2.0 (checked photo by photo), credited below with its "
                                                 "photographer and Flickr page."),
    "grocery_store": (build_grocery_store, "Grocery Store Dataset (Marcus Klasson, Cheng Zhang and Hedvig Kjellstrom, "
                                           "'A Hierarchical Grocery Store Image Dataset with Visual and Semantic "
                                           "Labels', WACV 2019), MIT licence, Copyright (c) 2019 Marcus Klasson. "
                                           "https://github.com/marcusklasson/GroceryStoreDataset (its natural photos "
                                           "only)."),
    "fish_eyes": (build_fish_eyes, "The Freshness of the Fish Eyes Dataset (Eko Prasetyo, Rani Purbaningtyas, Raden "
                                   "Dimas Adityo, Nanik Suciati and Chastine Fatichah), Mendeley Data xzyx7pbr3w, "
                                   "https://doi.org/10.17632/xzyx7pbr3w.1, CC BY 4.0. Article: Information Processing "
                                   "in Agriculture, 2022, https://doi.org/10.1016/j.inpa.2022.01.002."),
    "commons_food": (build_commons_food, "Wikimedia Commons food categories: captions CC0; pictures CC0, public "
                                         "domain or CC BY, each with its author and file page below. "
                                         "https://commons.wikimedia.org"),
}

# How many pictures a full build takes from each collection (about what each offers after the licence and label
# checks).
FOOD_LIMITS = {
    "open_images_food": 10000,        # of about 14,800 usable food photos (every egg, frozen and mould one first)
    "grocery_store": 5421,
    "fish_eyes": 4390,
    "commons_food": 1500,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one food pack builder.")
    parser.add_argument("key", choices=sorted(FOOD_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = FOOD_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
