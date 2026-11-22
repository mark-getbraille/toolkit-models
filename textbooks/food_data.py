"""USDA FoodData Central for the reference library (the owner's request of 2026-11-22): nutrition facts and
ingredients of foods, as searchable books by food group and by brand, with notes on reading the numbers and labels.
Keys: food (every book), fdc:group (the food-group books), fdc:group:<group>, fdc:survey, fdc:brand (the branded-food
books), fdc:brand:<letters>, fdc:label_guide.

What this module builds, in plain words:
  - one book per food group (25 groups: dairy and eggs, fruits, vegetables, beef, baked products, ...): every food of
    FoodData Central's Foundation Foods (the newest laboratory analyses, with their sample details) and SR Legacy (the
    final 2018 edition of the USDA National Nutrient Database for Standard Reference), one page per food with every
    nutrient per 100 grams and the household portions (a cup, a slice) with their weights;
  - one book of the foods "as eaten" in the national dietary survey (FNDDS, What We Eat in America), by its food
    categories;
  - books of branded foods (about 430,000 packaged foods sold in the US, from the labels companies send to the Global
    Branded Food Products Database), by the brand owner's first letter: one page per product with its ingredients,
    the Nutrition Facts as on the label (per serving), nutrients per 100 grams, serving size and UPC;
  - the FDA's own pages on reading the Nutrition Facts label (fdc:label_guide);
  - in every book, a first page "About these numbers" (written for this library): per 100 grams and per serving,
    percent Daily Value, what the data types mean, and that brands change recipes.

Licence: FoodData Central's API guide (fdc.nal.usda.gov/api-guide, checked at every build): "USDA FoodData Central
data are in the public domain and they are not copyrighted. They are published under CC0 1.0 Universal (CC0 1.0)";
USDA asks that FoodData Central be listed as the source (said on every book). robots.txt: "User-agent: *" with nothing
disallowed (checked 2026-11-22). The data are the official bulk downloads (fdc.nal.usda.gov/download-datasets), read
whole: the newest release of each kind is found on that page at every build; the 196 MB branded-food zip is streamed
to the cache folder and read one food at a time, never held whole in memory.

Weekly check: a book's sign is the name of the newest release of its data file (FoodData Central publishes twice a
year), so a new release builds every book again as a new version.

Run from the repository's folder:
  python3 textbooks/food_data.py fdc:group:dairy-and-egg-products --out build/textbooks
  python3 textbooks/food_data.py fdc:brand:q --out build/textbooks --limit 50       (a small test)
  python3 textbooks/food_data.py --list food
"""

import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"                        # "Reference, health and safety" (food and nutrition sit there already)
SITE = "https://fdc.nal.usda.gov"
DOWNLOADS = f"{SITE}/download-datasets/"
LICENCE_PAGE = f"{SITE}/api-guide"
LICENCE_TEXT = r"USDA FoodData Central data are in the public domain and they are not copyrighted"
PUBLISHER = "US Department of Agriculture, Agricultural Research Service (FoodData Central)"
NOTICE = ("Data from USDA FoodData Central (fdc.nal.usda.gov), Agricultural Research Service, US Department of "
          "Agriculture: public domain, published under CC0 1.0; USDA asks that FoodData Central be listed as the "
          "source. Nutrition information only, not medical advice; for allergies always read the package itself.")

# The 25 food groups of SR Legacy (Foundation Foods uses the same names), in the database's own order.
FOOD_GROUPS = [
    "Dairy and Egg Products", "Spices and Herbs", "Baby Foods", "Fats and Oils", "Poultry Products",
    "Soups, Sauces, and Gravies", "Sausages and Luncheon Meats", "Breakfast Cereals", "Fruits and Fruit Juices",
    "Pork Products", "Vegetables and Vegetable Products", "Nut and Seed Products", "Beef Products", "Beverages",
    "Finfish and Shellfish Products", "Legumes and Legume Products", "Lamb, Veal, and Game Products",
    "Baked Products", "Sweets", "Cereal Grains and Pasta", "Fast Foods", "Meals, Entrees, and Side Dishes", "Snacks",
    "American Indian/Alaska Native Foods", "Restaurant Foods"]

# The branded-food books, by the brand owner's first letter (about 15,000 to 47,000 products each); "other" holds
# owners starting with a digit or sign, and products whose owner is not given.
BRAND_PIECES = ["a", "b", "c", "d-e", "f", "g", "h", "i-j", "k", "l", "m", "n-o", "p-q", "r", "s", "t", "u-v", "w",
                "x-z", "other"]


def group_slug(name):
    """"Soups, Sauces, and Gravies" -> "soups-sauces-and-gravies"."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


GROUP_BY_SLUG = {group_slug(g): g for g in FOOD_GROUPS}


# ====================================================================== the data files

def release_files(cache=None):
    """{kind: newest file address} from the download page: kinds foundation_food_json, sr_legacy_food_json,
    survey_food_json, branded_food_json (the newest date in each file name wins)."""
    import build_textbooks as B
    text = B.fetch(DOWNLOADS, None)
    found = {}
    for path, kind, when in re.findall(r"(/fdc-datasets/FoodData_Central_([a-z_]+_json)_(\d{4}-\d\d(?:-\d\d)?)\.zip)",
                                       text):
        if kind not in found or when > found[kind][1]:
            found[kind] = (SITE + path, when)
    return {k: v[0] for k, v in found.items()}


def release_date(url):
    """The release date in a data file's name ("2026-10-29", or "2018-04")."""
    m = re.search(r"_(\d{4}-\d\d(?:-\d\d)?)\.zip$", url)
    return m.group(1) if m else ""


def licence_ok(cache=None):
    """True when the API guide still says the data are public domain (CC0)."""
    import build_textbooks as B
    page = B.fetch(LICENCE_PAGE, cache)
    return bool(re.search(LICENCE_TEXT, " ".join(re.sub(r"<[^>]+>", " ", page).split())))


def load_foods(url, cache=None):
    """The foods of a small data file (Foundation, SR Legacy, survey: up to 210 MB unpacked), as a list."""
    path = K.download_file(url, cache)
    with zipfile.ZipFile(path) as z:
        data = json.load(z.open(z.namelist()[0]))
    return next(iter(data.values()))


OWNER = re.compile(r'"brandOwner":\s*"((?:[^"\\]|\\.)*)"')


def branded_foods(url, cache=None, piece=None):
    """The branded foods of the big file one at a time (each line holds one food), only those of the brand piece
    when given (the owner is read from the line before the whole food is decoded)."""
    path = K.download_file(url, cache)
    decoder = json.JSONDecoder()
    with zipfile.ZipFile(path) as z, z.open(z.namelist()[0]) as raw:
        for line in io.TextIOWrapper(raw, encoding="utf-8"):
            line = line.strip()
            if not line.startswith('{"foodClass"'):
                continue
            if piece:
                m = OWNER.search(line)
                owner = json.loads(f'"{m.group(1)}"') if m else ""
                if not in_piece(owner, piece):
                    continue
            yield decoder.raw_decode(line)[0]


def in_piece(owner, piece):
    """True when a brand owner belongs to the book of letters piece ("d-e"); "other": no letter first, or none."""
    first = (owner.strip()[:1] or "~").lower()
    if not ("a" <= first <= "z"):
        return piece == "other"
    if piece == "other":
        return False
    low, _, high = piece.partition("-")
    return low <= first <= (high or low)


# ====================================================================== pages

def readable_case(text):
    """A name in capitals as a sentence ("GRANOLA, CINNAMON" -> "Granola, cinnamon"), so screen readers do not spell
    it; mixed-case names are kept."""
    text = " ".join((text or "").split())
    if text.isupper():
        text = text.lower()
        text = text[:1].upper() + text[1:]
    return text


def number(value):
    """A nutrient amount without needless zeros (3.0 -> "3", 0.140 -> "0.14")."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return f"{value:.3f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))
    return str(value)


def nutrients_table(food):
    """The table of every nutrient per 100 grams, in the database's order (energy, protein, fat, ... vitamins)."""
    rows = []
    for n in sorted(food.get("foodNutrients") or [], key=lambda n: (n.get("nutrient") or {}).get("rank") or 999999):
        nut = n.get("nutrient") or {}
        if n.get("amount") is None or not nut.get("name"):
            continue
        rows.append((nut["name"], number(n["amount"]), nut.get("unitName", "")))
    return K.rows_table(rows, ("Nutrient", "Amount per 100 grams", "Unit")) if rows else ""


def portions_table(food):
    """The household portions with their weights ("1 cup, chopped: 150 grams")."""
    rows = []
    for p in sorted(food.get("foodPortions") or [], key=lambda p: p.get("sequenceNumber") or 0):
        unit = (p.get("measureUnit") or {}).get("name", "")
        words = p.get("portionDescription") or " ".join(
            x for x in (number(p.get("amount") or p.get("value")), "" if unit == "undetermined" else unit,
                        p.get("modifier") or "") if x)
        if words and p.get("gramWeight"):
            rows.append((words, number(p["gramWeight"])))
    return K.rows_table(rows, ("Portion", "Grams")) if rows else ""


LABEL_ORDER = [("calories", "Calories", ""), ("fat", "Total fat", "g"), ("saturatedFat", "Saturated fat", "g"),
               ("transFat", "Trans fat", "g"), ("cholesterol", "Cholesterol", "mg"), ("sodium", "Sodium", "mg"),
               ("carbohydrates", "Total carbohydrate", "g"), ("fiber", "Dietary fiber", "g"),
               ("sugars", "Total sugars", "g"), ("addedSugar", "Added sugars", "g"), ("protein", "Protein", "g"),
               ("vitaminD", "Vitamin D", ""), ("calcium", "Calcium", "mg"), ("iron", "Iron", "mg"),
               ("potassium", "Potassium", "mg")]


def label_table(food):
    """The Nutrition Facts as on the package (per serving), from the label values the company sent."""
    label = food.get("labelNutrients") or {}
    rows = []
    for key, name, unit in LABEL_ORDER:
        v = (label.get(key) or {}).get("value")
        if v is not None:
            rows.append((name, f"{number(v)} {unit}".strip()))
    return K.rows_table(rows, ("Nutrition Facts (per serving, as on the label)", "Amount")) if rows else ""


def food_page(food):
    """The body HTML of one food's page."""
    import build_textbooks as B
    branded = food.get("dataType") == "Branded"
    facts = [("Food group", (food.get("foodCategory") or {}).get("description")),
             ("Category", food.get("brandedFoodCategory") or
              (food.get("wweiaFoodCategory") or {}).get("wweiaFoodCategoryDescription")),
             ("Brand owner", readable_case(food.get("brandOwner"))),
             ("Brand", readable_case(food.get("brandName"))), ("Sub-brand", readable_case(food.get("subbrandName"))),
             ("Serving size", f"{number(food.get('servingSize'))} {food.get('servingSizeUnit', '')}".strip()
              if food.get("servingSize") else ""),
             ("Household serving", readable_case(food.get("householdServingFullText"))), ("Package weight", food.get("packageWeight")),
             ("UPC or GTIN (bar code number)", food.get("gtinUpc")), ("Sold in", food.get("marketCountry")),
             ("Data type", food.get("dataType")), ("FoodData Central ID", food.get("fdcId")),
             ("Old NDB number", food.get("ndbNumber")), ("Survey food code", food.get("foodCode")),
             ("Published", food.get("publicationDate")), ("Label last changed", food.get("modifiedDate")),
             ("Discontinued", food.get("discontinuedDate"))]
    out = []
    if food.get("ingredients"):
        out.append(f"<h2>Ingredients</h2><p>{B.esc(readable_case(food['ingredients']))}</p>")
    if branded and label_table(food):
        out.append("<h2>Nutrition Facts</h2>" + label_table(food))
    out.append("<h2>About this food</h2>" + K.dl(facts))
    if food.get("footnote"):
        out.append(f"<p>Note: {B.esc(food['footnote'])}</p>")
    if portions_table(food):
        out.append("<h2>Portions and their weights</h2>" + portions_table(food))
    table = nutrients_table(food)
    if table:
        out.append("<h2>Nutrients per 100 grams</h2>" + table)
    inputs = [readable_case(i.get("foodDescription") or (i.get("inputFood") or {}).get("description", ""))
              for i in food.get("inputFoods") or []]
    inputs = [i for i in dict.fromkeys(inputs) if i]
    if inputs:
        heading = "Ingredients used in the survey's recipe" if food.get("foodCode") else "Samples analysed"
        out.append(f"<h2>{heading}</h2><ul>" + "".join(f"<li>{B.esc(i)}</li>" for i in inputs[:60]) + "</ul>")
    out.append(f'<p>Source: USDA FoodData Central, <a href="{SITE}/food-details/{food.get("fdcId")}/nutrients">'
               f'food {food.get("fdcId")}</a>.</p>')
    return "\n".join(out)


NOTES = """<p>These pages come from USDA FoodData Central, the US Department of Agriculture's food composition
database. Each page is one food.</p>
<h2>Per 100 grams and per serving</h2>
<p>The table "Nutrients per 100 grams" gives every amount for 100 grams of the food (about 3.5 ounces), so foods can
be compared with each other. To find the amount in what you eat, use the table "Portions and their weights": for
example, if 1 cup weighs 240 grams, multiply the amount per 100 grams by 2.4.</p>
<p>A branded food's page also has its "Nutrition Facts" as printed on the package, per serving. The serving size is
the company's, set by FDA rules from the amount people usually eat; it is not a recommendation.</p>
<h2>Reading a Nutrition Facts label</h2>
<ul>
<li>Start with the serving size and the number of servings in the package: every number on the label is for one
serving.</li>
<li>Calories are the energy in one serving.</li>
<li>Percent Daily Value (%DV) shows how much one serving gives of the amount most people need, or should not go over,
in a day, based on 2,000 calories. As a rule of thumb, 5% DV or less is low and 20% DV or more is high.</li>
<li>Get less of: saturated fat, sodium and added sugars. Get more of: dietary fiber, vitamin D, calcium, iron and
potassium.</li>
<li>Ingredients are listed by weight, the most first. The major food allergens (milk, eggs, fish, shellfish, tree
nuts, peanuts, wheat, soybeans and sesame) must be named on the package.</li>
</ul>
<h2>What the data types mean</h2>
<ul>
<li>Foundation Foods: the newest laboratory analyses of basic foods, with details of the samples analysed.</li>
<li>SR Legacy: the final edition (April 2018) of the National Nutrient Database for Standard Reference, the classic
reference values for thousands of foods; no longer updated.</li>
<li>Survey (FNDDS): foods as people eat them, used for What We Eat in America, the national dietary survey; mixed
dishes are worked out from recipes.</li>
<li>Branded: the labels companies send to the Global Branded Food Products Database. Companies change recipes:
always check the package you have, especially for allergies.</li>
</ul>
<h2>Units</h2>
<p>g is grams, mg is milligrams (thousandths of a gram), µg is micrograms (millionths of a gram), kcal is calories,
kJ is kilojoules, IU is international units.</p>
<p>This is nutrition information, not medical advice. The FDA's own guide to the label is in the book "Reading the
Nutrition Facts label (FDA)" of this library.</p>"""


def notes_page():
    """The first page of every book: the hand-written notes on the numbers and on reading labels."""
    import build_textbooks as B
    return B.Page("about-these-numbers", "About these numbers, and reading a food label", NOTES, 0,
                  "About these numbers")


def food_title(food):
    """A food's page title: its description, with the brand for a branded food."""
    title = readable_case(food.get("description") or f"Food {food.get('fdcId')}")
    brand = food.get("brandName") or food.get("brandOwner")
    if food.get("dataType") == "Branded" and brand:
        title += f" ({readable_case(brand)})"
    return title


def add_food(book, food, unit, paths):
    """Add one food's page (a unique path made from its name and FoodData Central ID)."""
    import build_textbooks as B
    path = B.slug(f"{food.get('description', '')[:50]}-{food.get('fdcId')}", 70)
    while path in paths:
        path += "-2"
    paths.add(path)
    book.pages.append(B.Page(path, food_title(food), food_page(food), 0, unit))


# ====================================================================== books

def base_book(name, title, subject, description, sources_used):
    """A FoodData Central book with its licence, notice and originals (the data files read)."""
    book = K.new_book(name, title, subject, GROUP, PUBLISHER, K.CC0, K.CC0_URL, DOWNLOADS, description, NOTICE,
                      changes="each food's record made into a web page")
    book.originals = [{"url": u, "kind": "zip"} for u in sources_used]
    book.published = max(release_date(u) for u in sources_used)
    book.version = "; ".join(f"{os.path.basename(u)[:-4]}" for u in sources_used)
    book.pages.append(notes_page())
    return book


def group_book(name, work, cache=None, left_out=None, limit=None):
    """One food group: its Foundation Foods, then its SR Legacy foods, alphabetical."""
    slug = name.split(":", 1)[1] if ":" in name else ""
    group = GROUP_BY_SLUG.get(slug)
    if not group:
        left_out.append({"title": name, "reason": "Unknown food group."})
        return None
    if not licence_ok(cache):
        left_out.append({"title": group, "reason": f"{LICENCE_PAGE} no longer says the data are public domain."})
        return None
    files = release_files(cache)
    used = [files[k] for k in ("foundation_food_json", "sr_legacy_food_json") if k in files]
    book = base_book(f"fdc_{slug.replace('-', '_')}", f"Food facts: {group} (USDA FoodData Central)",
                     f"Nutrition facts: {group.lower()}",
                     f"Every food of the group \"{group}\" in USDA FoodData Central: the Foundation Foods (newest "
                     "laboratory analyses) and SR Legacy (the 2018 Standard Reference), one page per food with every "
                     "nutrient per 100 grams and the household portions with their weights.", used)
    paths = set()
    for url in used:
        unit = "SR Legacy (Standard Reference, 2018)" if "sr_legacy" in url else "Foundation Foods (newest analyses)"
        foods = [f for f in load_foods(url, cache) if (f.get("foodCategory") or {}).get("description") == group]
        for food in sorted(foods, key=lambda f: f.get("description", "").lower()):
            if limit and len(book.pages) > limit:
                break
            add_food(book, food, unit, paths)
    return book


def survey_book(name, work, cache=None, left_out=None, limit=None):
    """The survey foods (FNDDS) by their What We Eat in America category."""
    if not licence_ok(cache):
        left_out.append({"title": name, "reason": f"{LICENCE_PAGE} no longer says the data are public domain."})
        return None
    url = release_files(cache)["survey_food_json"]
    book = base_book("fdc_survey_foods", "Foods as eaten: the national dietary survey's foods (USDA FNDDS)",
                     "Nutrition facts: foods and dishes as eaten",
                     "Every food and mixed dish of the Food and Nutrient Database for Dietary Studies (FNDDS), used for "
                     "What We Eat in America: one page per food with its nutrients per 100 grams, its portions and the "
                     "recipe ingredients, by survey food category.", [url])
    foods = load_foods(url, cache)
    unit_of = lambda f: (f.get("wweiaFoodCategory") or {}).get("wweiaFoodCategoryDescription") or "Other"  # noqa
    paths = set()
    for food in sorted(foods, key=lambda f: (unit_of(f).lower(), f.get("description", "").lower())):
        if limit and len(book.pages) > limit:
            break
        add_food(book, food, unit_of(food), paths)
    return book


def brand_book(name, work, cache=None, left_out=None, limit=None):
    """The branded foods of one piece of brand owners, by owner then product."""
    piece = name.split(":", 1)[1] if ":" in name else ""
    if piece not in BRAND_PIECES:
        left_out.append({"title": name, "reason": "Unknown piece of brands."})
        return None
    if not licence_ok(cache):
        left_out.append({"title": name, "reason": f"{LICENCE_PAGE} no longer says the data are public domain."})
        return None
    url = release_files(cache)["branded_food_json"]
    words = "brand owners not starting with a letter, or not given" if piece == "other" else \
        f"brand owners {piece.upper().replace('-', ' to ')}"
    book = base_book(f"fdc_branded_{piece.replace('-', '_')}", f"Branded food labels: {words} (USDA FoodData "
                     "Central)", "Nutrition facts and ingredients: branded foods",
                     f"Every packaged food of USDA's Global Branded Food Products Database whose {words}: one page "
                     "per product with its ingredients, the Nutrition Facts as on the label, nutrients per 100 grams, "
                     "serving size and UPC, grouped by brand owner.", [url])
    foods = []
    for food in branded_foods(url, cache, piece):
        foods.append(food)
        if limit and len(foods) >= limit:
            break
    owner = lambda f: (f.get("brandOwner") or "").strip() or "Brand owner not given"  # noqa: E731
    paths = set()
    for food in sorted(foods, key=lambda f: (owner(f).lower(), f.get("description", "").lower(), f.get("fdcId", 0))):
        add_food(book, food, owner(food), paths)
    return book


def data_sign(kind):
    """A sign function: the newest release file of one kind (a new release changes it)."""
    return lambda name: K.sha(release_files(None).get(kind, ""))


LABEL_GUIDE = K.us_web(
    GROUP, name="label_guide", title="Reading the Nutrition Facts label (FDA)",
    subject="Nutrition Facts label", publisher="US Food and Drug Administration (FDA)",
    source="https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label",
    licence_page="https://www.fda.gov/about-fda/about-website/website-policies",
    licence_text=r"They are in the public domain and may be republished",
    description="The FDA's guides to the Nutrition Facts label, every page of its section: how to understand and "
                "use the label (serving size, calories, percent Daily Value, nutrients), the changes to the label, "
                "added sugars, the Daily Value lows and highs, sodium, dietary fiber, and the label for older adults "
                "and for people with diabetes.",
    notice="A work of the US Food and Drug Administration (public domain: FDA website policies).",
    crawl=[("https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label", 1)],
    pages=r"^https://www\.fda\.gov/food/nutrition-facts-label/(?!como-|la-etiqueta|social-media)[a-z0-9-]+$",
    content=(r"<main\b[^>]*>", r"</main>"), limit=40)

COLLECTION = K.Collection(
    "fdc", GROUP, guides=[LABEL_GUIDE],
    makers={"group": (group_book, data_sign("foundation_food_json")),
            "survey": (survey_book, data_sign("survey_food_json")),
            "brand": (brand_book, data_sign("branded_food_json"))},
    pieces={"group": lambda: [group_slug(g) for g in FOOD_GROUPS], "brand": lambda: list(BRAND_PIECES)},
    words={"food": lambda: ["fdc:label_guide"] + [f"fdc:group:{group_slug(g)}" for g in FOOD_GROUPS] +
           ["fdc:survey"] + [f"fdc:brand:{p}" for p in BRAND_PIECES]})

GROUPS = {}
LICENCE_LINES = {
    "usda_fooddata_central": "fdc.nal.usda.gov/api-guide (read 2026-11-22, checked at every build): \"USDA FoodData "
                             "Central data are in the public domain and they are not copyrighted. They are published "
                             "under CC0 1.0 Universal (CC0 1.0). No permission is needed for their use, but we request "
                             "that users list FoodData Central as the source of the data.\" robots.txt: \"User-agent: "
                             "*\" with an empty Disallow (nothing refused); no AI rules.",
}
NOT_INCLUDED = [
    ("FoodData Central's experimental foods and the older Food and Nutrient Database releases", "Left out: the "
     "experimental foods are research records without household portions; each older FNDDS and branded release is "
     "replaced by the newest one, which is built (the old ones stay on fdc.nal.usda.gov). Index: "
     "https://fdc.nal.usda.gov/download-datasets/"),
    ("USDA FoodData Central API (api.nal.usda.gov)", "Not used: it needs a data.gov key and the bulk downloads hold "
     "the same data, so they are read instead."),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
