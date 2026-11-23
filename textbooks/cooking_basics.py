"""Cooking basics for the reference library, in the group "Reference, cookbooks and recipes" (the owner's request of
2026-11-23: fill the thin cooking basics area with practical how-to). Keys: cooking-basics (every book), cook:<name>,
and one request word per theme: cook-classics, cook-gov-recipes and cook-budget. A sibling of cookbooks.py, which
also uses the key prefix "cook:" (cookbooks.py hands the keys of this module to it: build_cookbooks and sign).

What this module builds, in plain words, each IN FULL:
  - cook:index, a guide to cooking in the library (the toolkit's own facts and links, CC0): for each theme the books
    here, the books already elsewhere in the library by key (cookbooks.py's heart-healthy, USDA and old cookbooks,
    the outdoor cooking, preserving and game books, the Army and Navy cooks' manuals, food safety), the manual and
    picture collections, and the sources that are links only, with the reason;
  - how to cook, the classics (cook-classics): Fannie Farmer's Boston Cooking-School Cook Book (1896, 1918 and 1927
    editions), Mrs. Lincoln's Boston Cook Book (1909), Mrs. Rorer's New Cook Book (1902), the Settlement Cook Book
    (1910), the White House Cook Book (1900), Janet McKenzie Hill's Practical Cooking and Serving (1919), Miss
    Parloa's Kitchen Companion (1887), and the USDA Bureau of Home Economics' Aunt Sammy's Radio Recipes (1931),
    Cooking Beef According to the Cut (1927) and Conserving Food Value in Cooking Vegetables (1933). Every one is
    marked HISTORICAL (OLD_COOK_NOTE): its food safety advice is out of date;
  - US government recipes and kitchen guides (cook-gov-recipes): the VA's healthy recipes (Veterans Health
    Administration Nutrition and Food Services, read from nutrition.va.gov: one page per recipe, by kind of dish),
    the USDA's Family Fare (1950) and Dry Beans, Peas, Lentils: Modern Cookery (1957), and the USDA and FDA food
    safety guides for older adults and for people with cancer (2006: safe cooking temperatures, storage, foods to
    avoid);
  - cooking for one or two, on a budget, with basic equipment (cook-budget): USDA's Recipes and Tips for Healthy,
    Thrifty Meals (2000), Money-Saving Main Dishes (1948), Family Meals at Low Cost (1962), Cooking for Two (1977),
    Food for Two (1951) and Food Guide for Older Folks (1972); and Leanne Brown's Good and Cheap (2014, CC BY-NC-SA:
    PERSONAL USE ONLY, kept apart and marked so).
  Every book carries FOOD_SAFETY (USDA safe minimum temperatures, the 2-hour rule, allergies) in its notice.

Already in the library and linked from the index, not repeated: cookbooks.py (cook:: NHLBI Keep the Beat and the
other heart-healthy cookbooks, Recipes for Healthy Kids, A Harvest of Recipes with USDA Foods, the FDA's kitchen
safety guide, the old bread, preserving, dairy and budget cookbooks, Fannie Farmer's Food and Cookery for the Sick,
the Army's TM 10-412 and TM 10-405), the Army and Marine Corps food service courses and the Armed Forces Recipe
Service (skill:), the Navy's Commissaryman and Culinary Specialist manuals (rate:, pdf:), outdoor and emergency
cooking (outcook:), preserving (preserve:), game and fish (gamefish:), the USDA Farmers' Bulletins on cooking
(pub:usda_farmers_bulletins), NIA's What's on Your Plate? (gpo:), the Dietary Guidelines (fit:) and the Nutrition
Facts label (fdc:label_guide).

Not built (NOT_INCLUDED, link-only): MyPlate Kitchen, SNAP-Ed Connection and What's Cooking? USDA Mixing Bowl (their
sites and the Wayback Machine did not answer the build machine), the USDA Food Buying Guide (a school-meal
purchasing tool), USDA FSIS's own pages (they refuse programs), the 1903 first Settlement Cook Book (no public scan),
and others listed below.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
old books published before 1931 (the builder checks each Internet Archive item's year at every build); Good and
Cheap under CC BY-NC-SA 4.0 (non-commercial: personal use only).

Run from the repository's folder:
  python3 textbooks/cooking_basics.py cook:index --out build/textbooks
  python3 textbooks/cooking_basics.py --list cooking-basics
"""

import os
import re
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "cookbooks"                    # "Reference, cookbooks and recipes" (cookbooks.py's group, in sources.GROUPS)
GROUPS = {}                            # the group is already named by sources.py

# ====================================================================== the notes every book carries

FOOD_SAFETY = ("Food safety (USDA): cook to a safe minimum internal temperature, checked with a food thermometer: "
               "145 F (63 C) for whole cuts of beef, pork, lamb and veal (with a 3-minute rest) and for fish, 160 F "
               "(71 C) for ground meat and egg dishes, 165 F (74 C) for poultry, leftovers and casseroles. Keep the "
               "refrigerator at 40 F (4 C) or colder; refrigerate food within 2 hours (1 hour above 90 F); wash "
               "hands, boards and knives after raw meat. Food allergies can be deadly: check every label for the "
               "nine major allergens (milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, soybeans, sesame). If "
               "you follow a special diet for a health condition, ask your doctor or a dietitian.")
OLD_COOK_NOTE = ("Historical (published in {year}): kept for its recipes, methods and history, but its food safety "
                 "advice is out of date. Do not follow its canning, curing, cooling or storage methods; cook meat, "
                 "poultry and eggs to today's safe temperatures; its oven heats, measures and ingredients may differ "
                 "from today's; some old recipes use raw or lightly cooked eggs, raw milk or preservatives now "
                 "banned; and its diet and health advice has been replaced.")
GOV_OLD_NOTE = ("Historical (published in {year}): a US government booklet of its time; its food safety, nutrition "
                "and storage advice has been replaced by today's guidance (see the safety note).")


def _keys(entries):
    """The keys of a list of entries."""
    return [f"cook:{e['name']}" for e in entries]


def _old(name, title, subject, publisher, archive, year, description):
    """One old public-domain cookbook of the Internet Archive (published before 1931), marked historical."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=OLD_COOK_NOTE,
                    notice=FOOD_SAFETY)


def _gov(name, title, subject, publisher, archive, published, description, old=False):
    """One US government publication read from its Internet Archive copy (public domain, 17 U.S.C. 105). old: an
    old booklet, marked historical in its description."""
    note = (" " + GOV_OLD_NOTE.format(year=published[:4])) if old else ""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description + note,
                    notice=f"A work of the US government ({publisher}): public domain, read from the Internet "
                           f"Archive's copy. {FOOD_SAFETY}")


USDA_BHE = "US Department of Agriculture, Bureau of Home Economics"

# ====================================================================== how to cook: the classics

CLASSICS = [
    _old("farmer_boston_cooking_school_1896", "The Boston Cooking-School Cook Book (Fannie Merritt Farmer, 1896, the "
         "first edition)", "How to cook", "Fannie Merritt Farmer (Little, Brown)", "bostoncookingsc00collgoog", 1896,
         "The book that brought level measurements to American cooking: how to measure, cooking methods (boiling, "
         "broiling, roasting, frying, braising), bread and breakfast dishes, soups, fish, meat and poultry, "
         "vegetables and potatoes, sauces, salads, eggs, puddings, pastry, cakes, cookies, ices and candy, with "
         "menus and cooking for the sick."),
    _old("farmer_boston_cooking_school_1918", "The Boston Cooking-School Cook Book (Fannie Merritt Farmer, 1918 "
         "edition)", "How to cook", "Fannie Merritt Farmer (Little, Brown)", "bostoncookingsc00farm", 1918,
         "The revised edition of Fannie Farmer's cook book (over 2,000 recipes), with the wartime additions on "
         "saving wheat, meat, fat and sugar: measuring, cooking methods, every kind of dish from bread to candy, "
         "menus, and the food values of the day."),
    _old("farmer_boston_cooking_school_1927", "The Boston Cooking-School Cook Book (Fannie Merritt Farmer, 1927 "
         "edition)", "How to cook", "Fannie Merritt Farmer, revised by Cora D. Perkins (Little, Brown)",
         "bostoncookingsch0000fann_a6z0", 1927,
         "The 1920s edition of Fannie Farmer's cook book: the same plain, measured method, with recipes for the "
         "gas and electric ranges and the iceboxes of its day, sandwiches, salads and many cakes and desserts."),
    _old("lincoln_boston_cook_book_1909", "Mrs. Lincoln's Boston Cook Book: What to Do and What Not to Do in Cooking "
         "(Mary J. Lincoln, 1909 edition)", "How to cook", "Mary J. Lincoln (Little, Brown)", "cu31924090146709",
         1909, "The Boston Cooking School's first principal's cook book: building and keeping a fire, measuring, "
         "the reasons behind each cooking method, bread, soups, fish, meat, vegetables, salads, puddings, pastry "
         "and cake, written as lessons for beginners."),
    _old("rorer_new_cook_book_1902", "Mrs. Rorer's New Cook Book: A Manual of Housekeeping (Sarah Tyson Rorer, 1902)",
         "How to cook", "Sarah Tyson Rorer (Arnold and Company)", "mrsrorersnewcook00roreuoft", 1902,
         "The Philadelphia Cooking School's director's large manual: kitchen equipment and its care, marketing, "
         "cooking methods, soups, fish, meats, vegetables, breads, desserts, preserves, foreign dishes and cooking "
         "for the sick, with menus."),
    _old("settlement_cook_book_1910", "The Settlement Cook Book (Mrs. Simon Kander, 1910 edition)", "How to cook",
         "Mrs. Simon Kander and Mrs. Henry Schoenfeld (The Settlement, Milwaukee)", "settlementcookbo0000unse_l2y2",
         1910, "Recipes first gathered for the cooking classes of a Milwaukee settlement house for immigrant "
         "families: plain, tested recipes for everyday meals, breads and coffee cakes, soups, meats, vegetables, "
         "preserving, and German and Jewish dishes, with household hints."),
    _old("white_house_cook_book_1900", "The White House Cook Book (F. L. Gillette and Hugo Ziemann, 1900 edition)",
         "How to cook", "Fanny Lemira Gillette and Hugo Ziemann (The Saalfield Publishing Company)",
         "whitehousecookbo00gill", 1900, "A household encyclopaedia of its time: cooking recipes from soups to "
         "desserts, carving, menus, dinner-giving and table etiquette, cooking for the sick, and household and "
         "toilet recipes (some of those use chemicals no longer thought safe)."),
    _old("hill_practical_cooking_serving_1919", "Practical Cooking and Serving: A Complete Manual of How to Select, "
         "Prepare, and Serve Food (Janet McKenzie Hill, 1919 edition)", "How to cook",
         "Janet McKenzie Hill (Doubleday, Page)", "cu31924003587965", 1919,
         "The Boston Cooking-School Magazine editor's manual: the principles of cooking each kind of food, then "
         "recipes, with laying the table, serving a meal with or without a maid, and planning menus."),
    _old("parloa_kitchen_companion_1887", "Miss Parloa's Kitchen Companion: A Guide for All Who Would Be Good "
         "Housekeepers (Maria Parloa, 1887)", "How to cook", "Maria Parloa (Estes and Lauriat)",
         "missparloaskitc00parlgoog", 1887,
         "A cooking teacher's large guide: furnishing and keeping the kitchen, marketing and choosing food, how to "
         "cook each kind of meat, fish and vegetable, bread, soups, sauces, desserts, preserving, and recipes for "
         "the sick."),
    _gov("usda_aunt_sammys_radio_recipes_1931", "Aunt Sammy's Radio Recipes, revised (USDA Bureau of Home Economics, "
         "1931)", "How to cook", USDA_BHE, "auntsammysradior1931unit", "1931",
         "The recipes of the USDA's radio programme \"Housekeepers' Chat\", where \"Aunt Sammy\" (Uncle Sam's wife) "
         "talked homemakers through planning and cooking meals: over 400 tested recipes for breads, soups, meat, "
         "fish, vegetables, salads and desserts, with menus.", old=True),
    _gov("usda_cooking_beef_according_to_cut_1927", "Cooking Beef According to the Cut (USDA Leaflet 17, 1927)",
         "How to cook", USDA_BHE, "cookingbeefaccor17alex", "1927",
         "Which beef cuts are tender and which need slow, moist cooking: roasting, broiling, pot-roasting, braising "
         "and stewing each cut, with recipes.", old=True),
    _gov("usda_conserving_food_value_vegetables_1933", "Conserving Food Value, Flavor, and Attractiveness in Cooking "
         "Vegetables (USDA Circular 265, 1933)", "How to cook", USDA_BHE, "conservingfoodva265mars", "1933",
         "How to cook vegetables so they keep their vitamins, colour and flavour: how much water, how long, and "
         "the best method for each kind of vegetable.", old=True),
]

# ====================================================================== US government recipes and kitchen guides

VA_SITE = "https://www.nutrition.va.gov"
VA_RECIPE_PAGES = [("Main dishes: beef", "Beef_Recipes"), ("Main dishes: lamb, goat and game", "Lamb_Goat_and_Game_"
                   "Meat_Recipes"), ("Main dishes: pork", "Pork_Recipes"), ("Main dishes: poultry", "Poultry_Recipes"),
                   ("Main dishes: seafood", "Seafood_Recipes"), ("Main dishes: vegetarian", "Vegetarian_Recipes"),
                   ("Main dishes: vegan", "Vegan_Recipes"), ("Soups and stews", "Soups_Stews_Recipes"),
                   ("Slow cooker", "Slow_Cooker_Recipes"), ("Pressure cooker", "Pressure_Cooker_Recipes"),
                   ("No-cook recipes", "No_Cook_Recipes"), ("Side dishes", "Sides"),
                   ("Breakfast", "Breakfast/index"), ("Snacks", "Snacks/index"), ("Desserts", "Desserts/index"),
                   ("Beverages", "Beverages/index"), ("Dressings, sauces and seasonings",
                                                      "DressingsSaucesSeasonings/index"),
                   ("Holidays and parties", "PartiesHolidays/index")]
VA_RECIPES = [(part, f"{VA_SITE}/NUTRITION/Recipes/{page}.asp") for part, page in VA_RECIPE_PAGES]
VA_PUBLISHER = "US Department of Veterans Affairs, Veterans Health Administration, Nutrition and Food Services"
VA_PDF_LINK = re.compile(r'<a\b[^>]*href="(/NUTRITION/docs/[^"#]+\.pdf)#?"[^>]*?(?:title="([^"]*)")?[^>]*>([^<]*)<',
                         re.I)


def va_pdf_links(page_html):
    """[(title, PDF address)] of the VA Nutrition and Food Services PDFs linked from one of its pages, in page order
    (each address once; the link's title attribute, else its text, names it)."""
    import html as _html
    out, seen = [], set()
    for path, title, text in VA_PDF_LINK.findall(page_html):
        url = urllib.parse.urljoin(VA_SITE, path)
        if url in seen:
            continue
        seen.add(url)
        name = " ".join(_html.unescape(title or text).split()) or path.rsplit("/", 1)[-1]
        out.append((name, url))
    return out


def va_pdf_maker(prefix, name, title, subject, description, notice, listing):
    """(book function, sign function) of a book made of the VA Nutrition and Food Services PDFs linked from listing
    [(part title, page address)]: each PDF is read whole by the builder's PDF reader (a scan without words is left
    out with its reason) and becomes one page (or one page per chapter) under its part; a PDF linked from two pages
    is read once, under the first. The licence line (17 U.S.C. 105 on govinfo.gov's policies page) is checked once
    per build. Also used by fitness_more.py for the VA's nutrition handouts."""

    def items(cache, left_out):
        """[(part, PDF title, PDF address, listing page)] of the listing (a page that cannot be read is said in
        left_out)."""
        import build_textbooks as B
        got, seen = [], set()
        for part, page in listing:
            if not K.readable(page, cache):
                left_out.append({"title": f"{title}: {part}", "reason": "The site's robots.txt does not allow it."})
                continue
            try:
                html_text = B.fetch(page, cache)
            except (urllib.error.URLError, OSError) as e:
                left_out.append({"title": f"{title}: {part}", "reason": f"Its page could not be read ({e})."})
                continue
            for pdf_title, url in va_pdf_links(html_text):
                if url not in seen:
                    seen.add(url)
                    got.append((part, pdf_title, url, page))
        return got

    def book_fn(key_name, work, cache=None, left_out=None, limit=None):
        """The book: one page per PDF (or per chapter of a longer PDF), grouped by part."""
        import build_textbooks as B
        left_out = left_out if left_out is not None else []
        words = " ".join(re.sub(r"<[^>]+>", " ", B.fetch(K.GOVINFO_POLICY, cache)).split())
        if not re.search(K.GOVINFO_TEXT, words):
            left_out.append({"title": title, "reason": "govinfo.gov's policies page no longer quotes 17 U.S.C. 105."})
            return None
        book = K.new_book(f"{prefix}_{name}", title, subject, GROUP if prefix == "cook" else "fitnessnutrition",
                          VA_PUBLISHER, K.US_GOV, K.US_GOV_URL, listing[0][1], description, notice,
                          changes="each PDF's text made into a web page, grouped as on the VA's own pages")
        chapter = 0
        for part, pdf_title, url, page in items(cache, left_out):
            if limit and len(book.pages) >= limit:
                break
            slug = re.sub(r"[^a-z0-9]+", "_", url.rsplit("/", 1)[-1].lower())[:60]
            one = K.us_pdf(book.group, name=f"{prefix}_{name}_{slug}", title=pdf_title, subject=subject,
                           publisher=VA_PUBLISHER, pdf=url, page=page, description=description, notice=notice)
            one.pop("licence_text")              # checked once above, not again for every PDF
            try:
                got = B.pdfdoc_book(one, work, cache, left_out)
            except Exception as e:  # noqa: BLE001 - said in left_out, the other PDFs are still read
                left_out.append({"title": pdf_title, "reason": f"It could not be read ({e})."})
                got = None
            if got is None or not got.pages:
                continue
            for i, p in enumerate(got.pages):
                chapter += 1
                head = pdf_title if len(got.pages) == 1 else f"{pdf_title}: {p.title}"
                book.pages.append(B.Page(f"{slug}-{i + 1}", head, p.body, chapter, part))
            book.originals.append(dict(got.original_pdf, kind="pdf"))
            local = os.path.join(work, f"{one['name']}.pdf")
            if os.path.exists(local) and not cache:
                os.remove(local)                 # a build without a cache folder keeps no copies of the PDFs
        book.published = ""
        return book

    def sign_fn(key_name):
        """The weekly sign: a fingerprint of the PDFs listed (a new or removed PDF rebuilds the book)."""
        return K.sha([(part, url) for part, _t, url, _p in items(None, [])])

    return book_fn, sign_fn


VA_RECIPES_BOOK = va_pdf_maker(
    "cook", "va_healthy_recipes", "Healthy recipes (VA Nutrition and Food Services)", "Healthy recipes",
    "The Veterans Health Administration's healthy recipes, every one listed on its recipe pages, one page per "
    "recipe, grouped by kind of dish: beef, lamb and game, pork, poultry, seafood, vegetarian and vegan main dishes, "
    "soups and stews, slow cooker, pressure cooker and no-cook recipes, side dishes, breakfasts, snacks, desserts, "
    "drinks, dressings and sauces, and holiday dishes. Each recipe gives its ingredients, steps, servings and "
    "nutrition facts, in the VA dietitians' own words.",
    f"From the US Department of Veterans Affairs (nutrition.va.gov): a US government work (public domain). Nutrition "
    f"facts are the VA's own. {FOOD_SAFETY}", VA_RECIPES)

GOV_RECIPES = [
    _gov("usda_family_fare_1950", "Family Fare: Food Management and Recipes (USDA Home and Garden Bulletin 1, 1950)",
         "Meal planning and recipes", "US Department of Agriculture, Bureau of Human Nutrition and Home Economics",
         "familyfarefoodma00unit", "1950",
         "The USDA's all-round family cook book: planning meals for good nutrition, buying and storing food, "
         "measuring, cooking terms, and about 300 recipes for breads, main dishes, vegetables, salads, soups, sauces "
         "and desserts.", old=True),
    _gov("usda_dry_beans_peas_lentils_1957", "Dry Beans, Peas, Lentils: Modern Cookery (USDA Leaflet 326, 1957)",
         "Cooking beans and lentils", "US Department of Agriculture, Agricultural Research Service",
         "drybeanspeaslent326unit_0", "1957",
         "How to soak and cook dry beans, peas and lentils, how much they swell, and recipes for soups, main "
         "dishes, salads and baked beans: cheap, filling protein.", old=True),
    _gov("fsis_food_safety_older_adults_2006", "Food Safety for Older Adults: A Need-to-Know Guide for Those 65 Years "
         "of Age and Older (USDA FSIS and FDA, 2006)", "Food safety", "US Department of Agriculture, Food Safety "
         "and Inspection Service, and the Food and Drug Administration", "CAT31102677", "2006",
         "Why older adults are more at risk from food poisoning; the four steps (clean, separate, cook, chill); safe "
         "cooking temperatures; foods to avoid or cook well (raw sprouts, soft cheeses made from raw milk, deli "
         "meats, raw eggs and shellfish); shopping, storing, eating out; and the signs of foodborne illness."),
    _gov("fsis_food_safety_people_with_cancer_2006", "Food Safety for People with Cancer: A Need-to-Know Guide (USDA "
         "FSIS and FDA, 2006)", "Food safety", "US Department of Agriculture, Food Safety and Inspection Service, "
         "and the Food and Drug Administration", "CAT31102678", "2006",
         "Food safety for people whose immune system is weakened by cancer or its treatment: the four steps, safe "
         "cooking temperatures, foods to avoid or cook well, and eating safely at home and away."),
]

# ====================================================================== cooking for one or two, on a budget

BUDGET = [
    _gov("usda_healthy_thrifty_meals_2000", "Recipes and Tips for Healthy, Thrifty Meals (USDA Center for Nutrition "
         "Policy and Promotion, 2000)", "Cooking on a budget", "US Department of Agriculture, Center for Nutrition "
         "Policy and Promotion", "CAT11091814", "2000",
         "Two weeks of low-cost menus built on the USDA Thrifty Food Plan, with their shopping lists and 40 easy "
         "recipes, and tips for planning, shopping, storing food and cooking healthy meals on a small budget."),
    _gov("usda_money_saving_main_dishes_1948", "Money-Saving Main Dishes: 150 Tested Recipes (USDA, 1948)",
         "Cooking on a budget", "US Department of Agriculture, Bureau of Human Nutrition and Home Economics",
         "moneysavingmaind289unit", "1948",
         "Main dishes that stretch meat, fish, eggs and cheese with grains, beans and vegetables: stews, "
         "casseroles, meat loaves, soups and one-dish meals, each tested in the USDA's kitchens.", old=True),
    _gov("usda_family_meals_at_low_cost_1962", "Family Meals at Low Cost (USDA Program Aid 472, 1962)",
         "Cooking on a budget", "US Department of Agriculture, Agricultural Marketing Service", "CAT31302926",
         "1962", "Planning a week of low-cost meals for a family, buying wisely, and simple recipes using plain "
         "foods.", old=True),
    _gov("usda_cooking_for_two_1977", "Cooking for Two (USDA Food and Nutrition Service, 1977)", "Cooking for one "
         "or two", "US Department of Agriculture, Food and Nutrition Service", "CAT78692531", "1977",
         "Shopping, storing and cooking for one or two people with simple equipment: small-quantity recipes, using "
         "leftovers, and keeping meals healthy and cheap.", old=True),
    _gov("usda_food_for_two_1951", "Food for Two (USDA Leaflet 306, 1951)", "Cooking for one or two",
         "US Department of Agriculture", "foodfortwo306unit", "1951",
         "A short guide to planning, buying and cooking meals for two without waste.", old=True),
    _gov("usda_food_guide_older_folks_1972", "Food Guide for Older Folks (USDA Home and Garden Bulletin 17, 1972)",
         "Cooking for one or two", "US Department of Agriculture, Agricultural Research Service", "CAT72348960",
         "1972", "Eating well in later life and when cooking for one: the daily food groups, easy meals, shopping "
         "and storing small amounts, and simple recipes.", old=True),
    dict(group=GROUP, name="good_and_cheap_2014", title="Good and Cheap: Eat Well on $4/Day (Leanne Brown, 2014)",
         subject="Cooking on a budget", publisher="Leanne Brown", archive="good-and-cheap", country="United States",
         licence="CC BY-NC-SA 4.0", licence_url="https://creativecommons.org/licenses/by-nc-sa/4.0/",
         personal_use=True, level="reference", published="2014", version="2014 first edition (Internet Archive item "
         "good-and-cheap)",
         description="A cookbook for people living on SNAP (food stamp) budgets: how to stock a pantry, shop and "
                     "cook well for about 4 dollars a day, with cheap, tasty recipes for breakfasts, soups, salads, "
                     "main dishes, snacks and sweets, and ideas for using what is left over.",
         notice=f"Copyright Leanne Brown, released under the Creative Commons Attribution-NonCommercial-ShareAlike "
                f"4.0 licence (CC BY-NC-SA 4.0), as the book itself says: PERSONAL USE ONLY, not for sale or any "
                f"commercial use; share copies under the same licence. Read from the Internet Archive's copy of the "
                f"free PDF (the author's own site now asks readers to sign up for her newsletter). {FOOD_SAFETY}"),
]

# ====================================================================== the index

SECTIONS = [
    ("How to cook: the classics", "Old American cook books that teach cooking from the start: measuring, cooking "
     "methods and every kind of dish. All are historical: " + OLD_COOK_NOTE.format(year="the year in each title"), [
        *[("key", f"cook:{e['name']}", e["title"]) for e in CLASSICS],
        ("key", "cook:old_food_and_cookery_for_the_sick_1904", "Food and Cookery for the Sick and Convalescent "
                                                               "(Fannie Farmer, 1904)"),
        ("key", "cook:old_fifty_two_sunday_dinners_1913", "Fifty-two Sunday Dinners (Hiller, 1913)"),
        ("key", "cook:old_bread_making_and_baking_1915", "Bread Making and Bread Baking (Brothers, 1915)"),
        ("key", "cook:army_cook_tm_10_405_1942", "The Army Cook, TM 10-405 (1942)"),
        ("key", "cook:army_recipes_tm_10_412_1946", "Army Recipes, TM 10-412 (1946)"),
        ("word", "pub:usda_farmers_bulletins", "USDA Farmers' Bulletins on cooking (bread, meat, eggs, vegetables, "
                                               "milk and more), by decade"),
        ("link", "Project Gutenberg cookery books (in the Kiwix library)", "https://www.gutenberg.org/ebooks/"
                 "bookshelf/419", "already in the Kiwix library as Project Gutenberg; not built again")]),
    ("US government recipes and kitchen guides", "Healthy recipes and kitchen guides from US government agencies. "
     + FOOD_SAFETY, [
        ("key", "cook:va_healthy_recipes", "Healthy recipes (VA Nutrition and Food Services)"),
        *[("key", f"cook:{e['name']}", e["title"]) for e in GOV_RECIPES],
        ("key", "cook:nhlbi_heart_healthy_recipes", "Heart-healthy recipes (NHLBI)"),
        ("key", "cook:nhlbi_keep_the_beat_dinners", "Keep the Beat: Deliciously Healthy Dinners (NHLBI)"),
        ("key", "cook:nhlbi_keep_the_beat_family", "Keep the Beat: Deliciously Healthy Family Meals (NHLBI)"),
        ("key", "cook:nhlbi_heart_healthy_home_cooking_african_american", "Heart Healthy Home Cooking African "
                                                                          "American Style (NHLBI)"),
        ("key", "cook:nhlbi_delicious_heart_healthy_latino_recipes", "Delicious Heart-Healthy Latino Recipes "
                                                                     "(NHLBI, English and Spanish)"),
        ("key", "cook:nhlbi_week_on_dash", "A Week with the DASH Eating Plan (NHLBI)"),
        ("key", "cook:usda_recipes_for_healthy_kids_homes", "Recipes for Healthy Kids: Cookbook for Homes (USDA)"),
        ("key", "cook:nhs_healthier_families_recipes", "Healthier Families recipes (NHS, UK)"),
        ("key", "cook:fda_food_safety_and_allergens", "Food safety and food allergies at home (FDA)"),
        ("key", "fdc:label_guide", "Reading the Nutrition Facts label (FDA)"),
        ("key", "gpo:nia_whats_on_your_plate_2019", "What's on Your Plate? Smart Food Choices for Healthy Aging "
                                                    "(NIA, with menus and recipes)"),
        ("key", "fit:dietary_guidelines_2025_2030", "Dietary Guidelines for Americans, 2025-2030"),
        ("key", "outcook:cdc_food_power_outage", "Food and water safety in a power outage (CDC)"),
        ("key", "skill:army_tm_10_412_armed_forces_recipe_service_2003", "Armed Forces Recipe Service (TM 10-412, "
                                                                         "2003): recipes for 100"),
        ("key", "skill:accp_qm0333_basic_food_preparation", "Basic Food Preparation (Army correspondence course)"),
        ("key", "rate:navy_commissaryman_1_c_1973", "Commissaryman 1 & C (US Navy, 1973)"),
        ("key", "pdf:navy_culinary_specialist", "Culinary Specialist (US Navy, NAVEDTRA 15008, 2010)"),
        ("word", "outdoor-cooking", "Emergency, camp and outdoor cooking books"),
        ("word", "preserving", "Home food preserving books"),
        ("word", "game-fish", "Game and fish: handling and food safety"),
        ("manuals", "small_kitchen", "Small kitchen appliance manuals (microwaves, pressure cookers, air fryers, "
                                     "slow cookers)"),
        ("manuals", "home_appliances", "Home appliance manuals (ranges, ovens, refrigerators)"),
        ("manuals", "kitchen_equipment", "Kitchen and food preparation equipment manuals"),
        ("link", "MyPlate Kitchen (USDA)", "https://www.myplate.gov/myplate-kitchen", "public domain, but the site "
                 "did not answer the build machine; open it in a browser"),
        ("link", "FoodSafety.gov: safe minimum internal temperatures", "https://www.foodsafety.gov/food-safety-"
                 "charts/safe-minimum-internal-temperatures", "public domain, but the site refuses programs; open "
                                                              "it in a browser"),
        ("link", "USDA FSIS: safe food handling and the FoodKeeper", "https://www.fsis.usda.gov/food-safety/"
                 "safe-food-handling-and-preparation", "public domain, but the site refuses programs; open it in a "
                                                       "browser")]),
    ("Cooking for one or two, on a budget", "Cheap, simple cooking with basic equipment. " + FOOD_SAFETY, [
        *[("key", f"cook:{e['name']}", e["title"]) for e in BUDGET],
        ("key", "cook:usda_harvest_of_recipes_usda_foods", "A Harvest of Recipes with USDA Foods (FDPIR)"),
        ("key", "cook:old_economical_cookery_1918", "Economical Cookery (Neil, 1918)"),
        ("key", "cook:old_corn_meal_for_breakfast_dinner_supper_1920", "Corn Meal for Breakfast, Dinner, Supper "
                                                                       "(1920)"),
        ("link", "SNAP-Ed Connection recipes (USDA)", "https://snaped.fns.usda.gov/", "the site did not answer the "
                                                                                      "build machine"),
        ("link", "Wikibooks Cookbook (CC BY-SA, in the Kiwix library)", "https://en.wikibooks.org/wiki/Cookbook:"
                 "Table_of_Contents", "already in the Kiwix library (wikibooks_en_all)")]),
    ("Cooking without sight", "Blind cooks' skills (labelling, measuring, safe knife and stove use) are in the blind "
     "and low-vision living collection; its guide lists them.", [
        ("key", "vision:index", "Blind and low-vision living: the guide"),
        ("link", "Hadley: cooking without sight (free courses)", "https://hadleyhelps.org/", "copyright of the Hadley "
                                                                                             "Institute; open it "
                                                                                             "in a browser")]),
]
INDEX = X.index_maker("cook", GROUP, "Cooking basics: a guide to the library", "Cooking basics",
                      "A guide to learning to cook in the library: the classic cook books, US government recipes "
                      "and kitchen guides, and cooking for one or two on a budget, with every cookbook, food "
                      "safety guide, manual collection and link-only source.", SECTIONS)
MAKERS = {"index": INDEX, "va_healthy_recipes": VA_RECIPES_BOOK}

PDFS = CLASSICS + GOV_RECIPES + BUDGET
THEMES = {"cook-classics": CLASSICS, "cook-gov-recipes": GOV_RECIPES, "cook-budget": BUDGET}
WORDS = {"cooking-basics": lambda: ["cook:index", "cook:va_healthy_recipes"] + _keys(PDFS),
         "cook-classics": lambda: ["cook:index"] + _keys(CLASSICS),
         "cook-gov-recipes": lambda: ["cook:index", "cook:va_healthy_recipes"] + _keys(GOV_RECIPES),
         "cook-budget": lambda: ["cook:index"] + _keys(BUDGET)}
COLLECTION = K.Collection("cook", GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "cookb_old_books": "The classic cook books (Farmer, Lincoln, Rorer, Kander, Gillette, Hill, Parloa) were published "
                       "in the United States before 1931; the builder checks each Internet Archive item's year at "
                       "every build and refuses a later one. archive.org's robots.txt allows the files; no AI rules "
                       "(checked 2026-11-23).",
    "cookb_us_gov": "The USDA, FSIS and FDA booklets (Internet Archive copies, most from the National Agricultural "
                    "Library's own scans) and the VA's recipes (nutrition.va.gov, which has no robots.txt and no AI "
                    "rules, checked 2026-11-23): works of the US government (17 U.S.C. 105, the line checked on "
                    "govinfo.gov's policies page at every build).",
    "cookb_good_and_cheap": "Good and Cheap (Leanne Brown, 2014): CC BY-NC-SA 4.0, as the book says; non-commercial, "
                            "so personal use only. Read from the Internet Archive's copy (item good-and-cheap, its "
                            "record also says CC BY-NC-SA 4.0), because leannebrown.com answers programs with a "
                            "bot check and gives the PDF only for a newsletter sign-up.",
    "cookb_index": "The cooking guide (cook:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("MyPlate Kitchen recipes, SNAP-Ed Connection and What's Cooking? USDA Mixing Bowl", "Public domain, but "
     "www.myplate.gov, snaped.fns.usda.gov and whatscooking.fns.usda.gov did not answer the build machine (checked "
     "again 2026-11-23), and the Wayback Machine (web.archive.org) refused the connection from it too. Link-only "
     "from cook:index. Index: https://www.myplate.gov/myplate-kitchen"),
    ("USDA Food Buying Guide for Child Nutrition Programs", "A purchasing tool for school and child-care meals "
     "(yields per 100 servings), not a cooking guide; its site sends programs to an error page. Index: "
     "https://foodbuyingguide.fns.usda.gov/"),
    ("USDA FSIS pages: safe minimum temperatures, the FoodKeeper storage times, leftovers, Kitchen Companion",
     "Public domain, but www.fsis.usda.gov refuses programs (\"403\", robots.txt included, checked again "
     "2026-11-23). The FSIS and FDA booklets for older adults and people with cancer are built from the Internet "
     "Archive (cook:fsis_food_safety_older_adults_2006), and the temperatures are in every book's safety note. "
     "Index: https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation"),
    ("NIH heart-healthy cookbooks (Keep the Beat, Deliciously Healthy family meals and dinners, the DASH week)",
     "Already built by cookbooks.py (cook:nhlbi_keep_the_beat_dinners and the others); not built twice. Index: "
     "https://www.nhlbi.nih.gov/health/heart-healthy-living/healthy-foods/healthy-eating-recipes"),
    ("CDC and NIDDK diabetes recipes", "CDC's diabetes recipes moved into its Diabetes Food Hub partnership with the "
     "American Diabetes Association (the association's copyright); NIDDK's diabetes eating pages are already built "
     "(homecare:niddk_diabetes_kidney_digestive) and it has no recipe book of its own. Index: "
     "https://www.cdc.gov/diabetes/healthy-eating/"),
    ("The Settlement Cook Book, first edition (1903), and the 1920 and 1930 editions", "No public scan of the 1903 "
     "edition was found (only 1984 and 1987 reprints, lent to print-disabled readers); the 1920 upload has no PDF "
     "and the 1930 scan is a lending copy. The 1910 edition is built. Index: "
     "https://archive.org/details/settlementcookbo0000unse_l2y2"),
    ("Mrs. Rorer's Philadelphia Cook Book (1886) and the 1918 Boston Cooking-School scan cookingscholbost00farmrich",
     "Their Internet Archive records give the year only as \"c1886\" and \"[c1918]\", which the builder cannot read "
     "as a year before 1931, so it would refuse them; Mrs. Rorer's New Cook Book (1902) and another 1918 Fannie "
     "Farmer scan are built instead. Index: https://archive.org/details/mrsrorersphilade00rorerich"),
    ("Aunt Sammy's Radio Recipes, 1926 and 1927 editions", "Replaced by the revised 1931 edition built here "
     "(cook:usda_aunt_sammys_radio_recipes_1931). Index: https://archive.org/details/auntsammysradior1927unit"),
    ("USDA Housekeepers' Chat radio scripts (Cooking for Two, Sunday Dishes for Two, Buying Food for Two and "
     "hundreds more, 1926 to 1944)", "Public domain, but each is a short radio script of two or three pages; the "
     "booklets that collect their advice (Aunt Sammy's Radio Recipes, Food for Two, Cooking for Two) are built. "
     "Index: https://archive.org/details/usda-housekeeperschat"),
    ("USDA \"in family meals\" leaflets on donated foods (dry beans, rice, cornmeal, nonfat dry milk, peanut butter, "
     "rolled oats, 1956 to 1965)", "Public domain but small demonstration leaflets for food distribution "
     "programmes; the larger Family Fare, Money-Saving Main Dishes and Dry Beans, Peas, Lentils are built. Index: "
     "https://archive.org/details/drybeansinfamily26unit"),
    ("Good and Cheap, second edition (2015, Workman) and its later books", "The 2015 edition sold by Workman "
     "Publishing is not under an open licence (the Internet Archive lends it only to print-disabled readers); the "
     "free 2014 edition (CC BY-NC-SA) is built for personal use. Index: https://www.leannebrown.com/"),
    ("Wikibooks Cookbook", "CC BY-SA; already in the Kiwix library (wikibooks_en_all) and linked from cook:index. "
     "Index: https://en.wikibooks.org/wiki/Cookbook:Table_of_Contents"),
    ("Blind cooking skills: Hadley, the National Federation of the Blind, VisionAware and RNIB guides", "Each "
     "organisation's copyright; left to the blind and low-vision living collection (vision:index). Index: "
     "https://hadleyhelps.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
