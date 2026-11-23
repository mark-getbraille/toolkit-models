"""Cookbooks and recipes as ZIM books for the offline reference library (keys "cookbooks" and cook:<name>).

The owner asked (2026-11-21) for cookbooks and recipes in the library, in full wherever the licence allows: everyday
cooking, baking and bread, smoking and barbecue, preserving (canning, pickling, fermenting, drying, freezing), cheese,
yogurt and other dairy, sausage and charcuterie, meal planning, cooking on a budget, special diets (diabetes, heart-
healthy, gluten-free, allergies) and kitchen safety. The textbooks builder (build_textbooks.py) writes the books;
this module says which books there are and makes the recipe books.

What is built (every source checked by hand on 2026-11-21; the lines quoted are in LICENCE_LINES):
  Recipe collections, one page per recipe, read from the publisher's own recipe pages, with an "A to Z recipe index"
  page and the recipes grouped by kind of dish. Each recipe keeps its ingredient list (with its own groups, such as
  "Marinade"), its steps (with the publisher's tips), its times and servings, and its nutrition facts, all in the
  publisher's own words and units (cups and ounces in the US books, grams and millilitres in the UK one).
    nhlbi_heart_healthy_recipes   NHLBI (National Heart, Lung, and Blood Institute) healthy eating recipes: public
                                  domain (NHLBI: "Most of the information on the NHLBI website is in the public
                                  domain and can be used without restriction").
    nhs_healthier_families_recipes  NHS Better Health "Healthier Families" recipes: Open Government Licence v3.0,
                                  with the UK practice note (metric measures, Celsius and gas marks, UK names).
  Cookbooks published as PDF files, made into one page per chapter by build_textbooks.pdfdoc_book (the PDF's own
  table of contents and index pages are kept as text):
    NHLBI "Keep the Beat" and other heart-healthy cookbooks and the DASH week of menus (public domain);
    USDA Food and Nutrition Administration (formerly FNS): "Recipes for Healthy Kids: Cookbook for Homes" (Team
    Nutrition) and "A Harvest of Recipes with USDA Foods" (FDPIR, cooking on a budget) (US government works);
    the US Army's recipe book TM 10-412 (1946, the Armed Forces Recipe Service's forerunner) and "The Army Cook"
    TM 10-405 (1942), from the Internet Archive (US government works, public domain mark);
    old cookbooks in the US public domain (published before 1931) from the Internet Archive's scans: bread and
    baking, canning, drying and preserving, a fish smokehouse, cheese making, butter, meat curing and sausage
    making, cooking on a budget, cooking for the sick, and a book of planned Sunday dinners. Each says it is OLD:
    food safety advice has changed (OLD_NOTE).
  A kitchen safety guide: the FDA's consumer pages on safe food handling, food allergies, gluten-free labelling and
  foodborne illness (public domain), read by build_textbooks.webguide_book.
  A LINKS-ONLY book: the National Center for Home Food Preservation's tested recipes (University of Georgia,
  "Copyright ... All rights reserved"), one page per method (canning, pickling, fermenting, drying, freezing, jams
  and jellies, curing and smoking, storing) listing each recipe's name and its address, nothing copied.
  A library guide (cook:guide): which cookbook covers which topic, the Kiwix library's own cooking books (the USDA
  Complete Guide to Home Canning, Wikibooks with its Cookbook, Project Gutenberg's cookery books, Public Domain
  Recipes and others) and the safety notices, so a reader can find the right book.

Safety: every preserving, smoking, curing and cheese-making book carries SAFETY_NOTICES on its welcome page, and every
old book OLD_NOTE (for example, open-kettle and oven canning, and canning vegetables or meat in a boiling-water bath,
are now known to be unsafe). Every site's robots.txt is obeyed, and a site that shuts out AI companies' readers by
name or says "ai-train=no" (Content-Signal) is not read at all (ai_refused). Requests go one at a time, with the
builder's pause (or the site's Crawl-delay).

What was looked at and not built, and why (MyPlate Kitchen, SNAP-Ed Connection, FSIS, CDC, Health Canada, the Food
Standards Agency, extension publications, Recipe1M and others), is in NOT_INCLUDED.

Keys: cookbooks (every book), cook:<name> (one book: the names in BOOKS). Run from the repository's folder:
  python3 textbooks/build_textbooks.py cookbooks --out build/textbooks --cache build/textbooks-cache
  python3 textbooks/cookbooks.py cook:nhlbi_heart_healthy_recipes --out build/textbooks --limit 5   (a small test)
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.robotparser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import sources  # noqa: E402

GROUP = "cookbooks"
GROUP_NAME = "Reference, cookbooks and recipes"
OGL_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
PD_MARK = "https://creativecommons.org/publicdomain/mark/1.0/"

# The topics the owner asked for: key -> the name shown (the book's subject is "Cooking: <name>").
TOPICS = {
    "everyday": "everyday cooking", "baking": "baking and bread", "smoking": "smoking and barbecue",
    "preserving": "preserving (canning, pickling, fermenting, drying, freezing)",
    "dairy": "cheese, yogurt and other dairy", "sausage": "sausage, curing and charcuterie",
    "mealplan": "meal planning", "budget": "cooking on a budget",
    "diets": "special diets (diabetes, heart-healthy, gluten-free, allergies)", "safety": "kitchen and food safety",
    "guide": "library guide",
}

# ====================================================================== notices

SAFETY_NOTICES = {
    "preserving": "Food safety: home canning, pickling, fermenting and drying can cause serious illness, including "
                  "botulism, if done wrongly. Use current tested methods and processing times: the USDA Complete "
                  "Guide to Home Canning (in the Kiwix library as \"USDA Guide to Home Canning\") and the National "
                  "Center for Home Food Preservation (nchfp.uga.edu). Low-acid foods (vegetables, meat, poultry, "
                  "fish, beans) must be processed in a pressure canner, never a boiling-water bath; adjust times for "
                  "your altitude; do not invent or change canning recipes.",
    "smoking": "Food safety: smoke and cook meat, poultry and fish to safe internal temperatures, checked with a food "
               "thermometer (USDA: beef, pork, lamb and veal steaks, chops and roasts 145 °F (63 °C) with a 3-minute "
               "rest; ground meats 160 °F (71 °C); poultry 165 °F (74 °C); fish 145 °F (63 °C)). Cold smoking does "
               "not cook food. Keep the smoker between 225 and 300 °F (107 to 149 °C) for hot smoking, and keep raw "
               "meat cold until it goes in. For jerky, heat meat to 160 °F (poultry 165 °F) before or after drying.",
    "sausage": "Food safety: curing and sausage making need exact amounts of curing salt (sodium nitrite, \"Prague "
               "powder\" or \"pink curing salt\"), cold temperatures and clean equipment; too little cure risks "
               "botulism and too much is poisonous. Use current tested recipes and cook fresh sausage to 160 °F "
               "(71 °C), poultry sausage to 165 °F (74 °C).",
    "dairy": "Food safety: make cheese, yogurt and butter from pasteurised milk, or pasteurise raw milk first; raw "
             "milk can carry listeria, E. coli, salmonella and other germs. Keep everything clean and use current "
             "tested methods for ripening and storing cheese.",
}
OLD_NOTE = ("Old book (published in {year}): kept for its recipes and history, but food safety advice has changed "
            "since. Do not follow its canning, curing, smoking or storage methods without checking current guidance: "
            "for example, open-kettle and oven canning, and canning vegetables, meat or fish in a boiling-water bath, "
            "are now known to be unsafe; some old recipes use preservatives that are now banned (borax, boric or "
            "salicylic acid, formaldehyde); safe cooking temperatures for meat, poultry and eggs are higher now; and "
            "its diet advice is out of date. The text was read by a scanner and has its mistakes.")
UK_NOTE = ("UK source: measures are metric (grams, millilitres), oven temperatures are in Celsius (a fan oven about "
           "20 degrees lower) and gas marks, a tablespoon is 15 ml, and some ingredients have UK names (courgette is "
           "zucchini, aubergine is eggplant, coriander is cilantro, mince is ground meat, single and double cream are "
           "light and heavy cream, plain flour is all-purpose flour, caster sugar is superfine sugar); food safety "
           "rules and nutrition labels may differ from US practice.")
NUTRITION_NOTE = "Nutrition facts are the publisher's own, per serving as stated; they are not medical advice."

# ====================================================================== the books

NHLBI_SITE = "https://www.nhlbi.nih.gov"
NHLBI_RECIPES = NHLBI_SITE + "/health/heart-healthy-living/healthy-foods/healthy-eating-recipes"
NHLBI_POLICY = NHLBI_SITE + "/about/contact/trademark-branding-and-logo"
NHLBI_TEXT = r"Most of the information on the NHLBI website is in the public domain"
NHS_SITE = "https://www.nhs.uk"
NHS_RECIPES = NHS_SITE + "/healthier-families/recipes/"
NHS_POLICY = "https://www.nhs.uk/our-policies/terms-and-conditions/"
NHS_TEXT = r"released free-of-charge under the current version of the Open Government Licence"
FDA_POLICY = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished"
FNA_SITE = "https://www.fna.usda.gov"
NCHFP = "https://nchfp.uga.edu"
NCHFP_METHODS = [("can", "Canning"), ("pickle", "Pickling"), ("ferment", "Fermenting"), ("dry", "Drying"),
                 ("freeze", "Freezing"), ("make-jam-jelly", "Jams and jellies"), ("cure-smoke", "Curing and smoking"),
                 ("store", "Storing")]

NHLBI_PDF = dict(kind="pdf", group=GROUP, country="United States", licence=sources.US_GOV,
                 licence_url=sources.US_GOV_URL, licence_page=NHLBI_POLICY, licence_text=NHLBI_TEXT,
                 publisher="National Heart, Lung, and Blood Institute (NHLBI), National Institutes of Health")
FNA_PDF = dict(kind="pdf", group=GROUP, country="United States", licence=sources.US_GOV,
               licence_url=sources.US_GOV_URL, licence_page=sources.GOVINFO_POLICY, licence_text=sources.GOVINFO_TEXT,
               publisher="US Department of Agriculture, Food and Nutrition Administration (formerly Food and "
                         "Nutrition Service)")
ARMY = dict(kind="pdf", group=GROUP, country="United States", licence=sources.US_GOV, licence_url=sources.US_GOV_URL,
            publisher="US War Department (Quartermaster Corps)", old=True)
OLD = dict(kind="pdf", group=GROUP, country="United States", licence="Public domain (published before 1931)",
           licence_url="https://www.copyright.gov/help/faq/faq-duration.html", old_public_domain=True, old=True,
           changes="its scanned pages' machine-read text (with the scanner's mistakes) made into web pages, one per "
                   "chapter or ten pages at a time")


def _nhlbi(name, title, topic, resource, published, description):
    """One NHLBI cookbook PDF, found on its resource page."""
    return dict(NHLBI_PDF, name=name, title=title, topic=topic, page=f"{NHLBI_SITE}/resources/{resource}",
                published=published, description=description)


def _old(name, title, topic, archive, year, publisher, description):
    """One old public-domain cookbook from the Internet Archive."""
    return dict(OLD, name=name, title=title, topic=topic, archive=archive, published=str(year), publisher=publisher,
                description=description + " Published in " + str(year) + ": an old book; food safety advice has "
                "changed since (see its welcome page).")


BOOKS = [
    dict(kind="recipes", site="nhlbi", name="nhlbi_heart_healthy_recipes", topic="diets",
         title="Heart-healthy recipes (NHLBI)", source=NHLBI_RECIPES, licence=sources.US_GOV,
         licence_url=sources.US_GOV_URL, licence_page=NHLBI_POLICY, licence_text=NHLBI_TEXT,
         country="United States", publisher=NHLBI_PDF["publisher"],
         description="The NHLBI's healthy eating recipes, low in sodium and saturated fat, from its heart-healthy "
                     "cookbooks: each recipe's ingredients, directions, times, servings and nutrition facts."),
    dict(kind="recipes", site="nhs", name="nhs_healthier_families_recipes", topic="everyday",
         title="Healthier Families recipes (NHS)", source=NHS_RECIPES, licence="OGL-UK-3.0", licence_url=OGL_URL,
         licence_page=NHS_POLICY, licence_text=NHS_TEXT, country="United Kingdom",
         publisher="NHS England, Better Health - Healthier Families (nhs.uk)",
         description="The NHS's healthy family recipes for breakfast, lunch, dinner, snacks and puddings, many from "
                     "Caribbean, African and South Asian kitchens: ingredients, method, tips, times, servings and "
                     "nutrition per serving, in metric measures."),
    _nhlbi("nhlbi_keep_the_beat_dinners", "Keep the Beat Recipes: Deliciously Healthy Dinners (NHLBI)", "diets",
           "keep-beat-recipes-deliciously-healthy-dinners", "2010",
           "NHLBI's heart-healthy cookbook of dinner recipes from around the world, with nutrition facts and tips."),
    _nhlbi("nhlbi_keep_the_beat_family", "Keep the Beat Recipes: Deliciously Healthy Family Meals (NHLBI)", "diets",
           "keep-beat-recipes-deliciously-healthy-family-meals", "2010",
           "NHLBI's heart-healthy cookbook of family meals, with tips for cooking with children and nutrition facts."),
    _nhlbi("nhlbi_heart_healthy_home_cooking_african_american", "Heart Healthy Home Cooking African American Style "
           "(NHLBI)", "diets", "heart-healthy-home-cooking-african-american-style", "2021",
           "NHLBI's cookbook of traditional African American dishes made lower in fat, salt and calories."),
    _nhlbi("nhlbi_delicious_heart_healthy_latino_recipes", "Delicious Heart-Healthy Latino Recipes (NHLBI)", "diets",
           "delicious-heart-healthy-latino-recipes-book-platillos-latinos-sabrosos-y-saludables", "2024",
           "NHLBI's bilingual (English and Spanish) cookbook of heart-healthy Latino dishes, with nutrition facts."),
    _nhlbi("nhlbi_when_delicious_meets_nutritious", "When Delicious Meets Nutritious: Recipes for Heart Health "
           "(NHLBI)", "diets", "when-delicious-meets-nutritious-recipes-heart-health", "2015",
           "NHLBI's collection of heart-healthy recipes with nutrition facts."),
    _nhlbi("nhlbi_week_on_dash", "A Week with the DASH Eating Plan (NHLBI)", "mealplan", "week-dash-eating-plan",
           "2019", "Seven days of DASH (Dietary Approaches to Stop Hypertension) menus with recipes, for lowering "
           "blood pressure: a ready-made week of meal planning."),
    dict(FNA_PDF, name="usda_recipes_for_healthy_kids_homes", title="Recipes for Healthy Kids: Cookbook for Homes "
         "(USDA Team Nutrition)", topic="everyday", page=FNA_SITE + "/tn/recipes-healthy-kids-cookbook-homes",
         pdf_pattern=r"cookbook-homes", description="USDA Team Nutrition's family-size versions of the winning "
         "recipes of the Recipes for Healthy Kids Challenge: whole grains, dark green and orange vegetables, beans "
         "and peas, with nutrition facts."),
    dict(FNA_PDF, name="usda_harvest_of_recipes_usda_foods", title="A Harvest of Recipes with USDA Foods (FDPIR)",
         topic="budget", page=FNA_SITE + "/fdpir/harvest-recipes-usda-foods", pdf_pattern=r"HarvestofRecipes",
         description="Recipes made with the foods of the USDA Food Distribution Program on Indian Reservations "
                     "(canned, dried and frozen USDA Foods): cooking well on a small budget, with nutrition facts."),
    dict(kind="guide", name="fda_food_safety_and_allergens", title="Food safety and food allergies at home (FDA)",
         topic="safety", subject="Cooking: kitchen and food safety", group=GROUP,
         publisher="US Food and Drug Administration (FDA)", country="United States", licence=sources.US_GOV,
         licence_url=sources.US_GOV_URL, source="https://www.fda.gov/food/consumers/buy-store-serve-safe-food",
         description="The FDA's consumer guides to safe food in the kitchen: cleaning, separating, cooking and "
                     "chilling, eggs, produce, seafood, flour, juice and raw milk, power cuts and floods, foodborne "
                     "illness and who is most at risk, food allergies (the nine major allergens, sesame), "
                     "gluten-free labelling, and reading the Nutrition Facts label.",
         licence_page=FDA_POLICY, licence_text=FDA_TEXT, page_mark="", units="", sitemap="", unit_rules=[],
         start=["https://www.fda.gov/food/buy-store-serve-safe-food/food-facts-consumers",
                "https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies",
                "https://www.fda.gov/food/resources-you-food/consumers"],
         pages=r"^https://www\.fda\.gov/food/(buy-store-serve-safe-food|consumers|food-allergies|"
               r"nutrition-education-resources-materials|nutrition-food-labeling-and-critical-foods)/"
               r"(?!.*(social-media|manipulacion|toolkit|survey|world-food-safety-day|education-month))[a-z0-9-]+$",
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>", r"<aside\b.*?</aside>"], limit=80),
    dict(kind="links", name="nchfp_preserving_links", topic="preserving",
         title="Tested home preserving recipes: links (National Center for Home Food Preservation)",
         source=NCHFP + "/", country="United States",
         publisher="National Center for Home Food Preservation (University of Georgia)",
         description="A list of the National Center for Home Food Preservation's tested recipes and instructions "
                     "for canning, pickling, fermenting, drying, freezing, jams and jellies, curing and smoking, and "
                     "storing food: each recipe's name and its web address. The recipes themselves are not copied "
                     "(the Center's site is \"All rights reserved\"); open them on its website."),
    dict(ARMY, name="army_recipes_tm_10_412_1946", title="Army Recipes, TM 10-412 (US War Department, 1946)",
         topic="everyday", archive="TM10-4121946", published="1946",
         description="The US Army's book of standard recipes for 100 servings (the forerunner of today's Armed Forces "
                     "Recipe Service): meats, poultry, fish, vegetables, salads, soups, breads, cakes and pies, with "
                     "baking and cooking guides. Quantities are for large groups."),
    dict(ARMY, name="army_cook_tm_10_405_1942", title="The Army Cook, TM 10-405 (US War Department, 1942)",
         topic="everyday", archive="1942TM10-405", published="1942",
         description="The US Army's manual for cooks: kitchen management, food values, meats and cutting, cooking "
                     "methods, baking, field cooking and sanitation."),
    _old("old_bread_making_and_baking_1915", "Bread Making and Bread Baking (Minnie E. Brothers, 1915)", "baking",
         "breadmakingbread00brot", 1915, "Minnie E. Brothers", "Yeast breads, rolls and quick breads at home."),
    _old("old_peerless_pastry_book_1910", "The Peerless Pastry Book (John Blitzner, 1910)", "baking",
         "peerlesspastrybo00blit", 1910, "John Blitzner (editor)", "Recipes for baking and pastry work: cakes, "
         "cookies, pies, puff pastry and icings."),
    _old("old_leavening_agents_1914", "Leavening Agents: Yeast, Leaven, Salt-Rising Fermentation, Baking Powder "
         "(Richard N. Hart, 1914)", "baking", "leaveningagentsy00hartrich", 1914, "Richard N. Hart",
         "How breads rise: yeast, sourdough leaven, salt-rising bread, baking powder and other raising agents."),
    _old("old_everywomans_canning_book_1918", "Everywoman's Canning Book (Mary B. Hughes, 1918)", "preserving",
         "everywomanscanni00hughrich", 1918, "Mary Catherine Burke Hughes", "Home canning and preserving of fruit, "
         "vegetables and meat, jellies and pickles (its methods are old: see the safety notice)."),
    _old("old_preservation_of_food_1919", "Preservation of Food: Home Canning, Preserving, Jelly-Making, Pickling, "
         "Drying (Olive E. Hayes, 1919)", "preserving", "preservationoffo00hayerich", 1919, "Olive Elliot Hayes",
         "Home canning, preserves, jellies, pickles and drying."),
    _old("old_home_drying_manual_1917", "Home Drying Manual for Vegetables and Fruits (National War Garden "
         "Commission, 1917)", "preserving", "homedryingmanual00nati", 1917, "National War Garden Commission",
         "Drying vegetables and fruits at home in the sun, the oven and simple driers."),
    _old("old_practical_small_smokehouse_for_fish_1918", "A Practical Small Smokehouse for Fish (US Bureau of "
         "Fisheries, 1918)", "smoking", "practicalsmall00unit", 1918, "US Bureau of Fisheries",
         "How to build and run a small smokehouse and smoke fish."),
    _old("old_secrets_of_meat_curing_1922", "Secrets of Meat Curing and Sausage Making (B. Heller and Company, 1922)",
         "sausage", "secretsofmeatcur00bhelrich", 1922, "B. Heller and Company", "Curing hams, bacon and corned "
         "beef, smoking meat, and making many kinds of sausage (it advertises the maker's own curing products, "
         "some of which are no longer allowed)."),
    _old("old_cheese_making_decker_1905", "Cheese Making: Cheddar, Swiss, Brick, Limburger, Edam, Cottage (John W. "
         "Decker, 1905)", "dairy", "cheesemakingched00deck", 1905, "John Wright Decker",
         "How to make the common cheeses, from milk and rennet to pressing and curing."),
    _old("old_cheese_making_sammis_1918", "Cheese Making (John L. Sammis, 1918)", "dairy", "cheesemakingbook00samm",
         1918, "John Langley Sammis", "A book for practical cheese makers: milk, starters, rennet, Cheddar and "
         "other cheeses, curing and judging."),
    _old("old_book_of_butter_1923", "The Book of Butter (Edward S. Guthrie, 1923)", "dairy", "bookofbuttertext00guth",
         1923, "Edward Sewall Guthrie", "Cream, ripening, churning, working and storing butter, and buttermilk."),
    _old("old_economical_cookery_1918", "Economical Cookery (Marion Harris Neil, 1918)", "budget",
         "economicalcooker00neil", 1918, "Marion Harris Neil", "Wartime recipes for cooking well on little money: "
         "using cheaper cuts, leftovers, beans, cereals and less sugar and fat."),
    _old("old_corn_meal_for_breakfast_dinner_supper_1920", "Corn Meal for Breakfast, Dinner, Supper (Bessie R. "
         "Murphy, 1920)", "budget", "cornmealforbreak00murp", 1920, "Bessie R. Murphy",
         "Cheap and filling corn meal recipes: breads, mush, muffins and main dishes."),
    _old("old_food_and_cookery_for_the_sick_1904", "Food and Cookery for the Sick and Convalescent (Fannie Merritt "
         "Farmer, 1904)", "diets", "foodcookeryforsi00farm", 1904, "Fannie Merritt Farmer",
         "Cooking for people who are ill or getting better: broths, gruels, light meals and invalid diets."),
    _old("old_fifty_two_sunday_dinners_1913", "Fifty-two Sunday Dinners (Elizabeth O. Hiller, 1913)", "mealplan",
         "cu31924090143029", 1913, "Elizabeth O. Hiller", "A planned menu with recipes for every Sunday of the "
         "year: meal planning, one week at a time."),
    dict(kind="library", name="cookbooks_library_guide", topic="guide", title="Cookbooks and recipes: library guide",
         source="https://github.com/mark-getbraille/toolkit-models", country="United States",
         publisher="GetBraille.com (toolkit-models)", licence="CC0 1.0",
         licence_url="https://creativecommons.org/publicdomain/zero/1.0/",
         description="Which book of the library to open for each kind of cooking (everyday cooking, baking, "
                     "preserving, smoking, dairy, sausage, meal planning, budget, special diets, kitchen safety), "
                     "the cooking books in the Kiwix library, a recipe index of the recipe books, and the safety "
                     "notices."),
]
BY_NAME = {b["name"]: b for b in BOOKS}

# ====================================================================== polite reading

_ai = {}
AI_AGENTS = ("ClaudeBot", "anthropic-ai", "Claude-Web", "GPTBot", "CCBot")


def ai_refused(url, cache=None):
    """True when the site's robots.txt shuts out AI companies' readers from url (a group for ClaudeBot,
    anthropic-ai, Claude-Web, GPTBot or CCBot that disallows it) or says "ai-train=no" in a Content-Signal line:
    the owner's rule is not to read such sites at all. A missing robots.txt refuses nothing."""
    parts = urllib.parse.urlsplit(url)
    site = f"{parts.scheme}://{parts.netloc}"
    if site not in _ai:
        try:
            text = B.fetch(site + "/robots.txt", cache)
        except (urllib.error.URLError, OSError):
            text = ""
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(text.splitlines())
        signal = bool(re.search(r"^\s*content-signal\s*:.*ai-train\s*=\s*no", text, re.I | re.M))
        named = [a for a in AI_AGENTS if re.search(rf"^\s*user-agent\s*:\s*{re.escape(a)}\s*$", text, re.I | re.M)]
        _ai[site] = (rp, signal, named)
    rp, signal, named = _ai[site]
    return signal or any(not rp.can_fetch(a, url) for a in named)


def readable(url, cache=None):
    """True when the builder may read url: robots.txt allows our reader and no AI-reader block applies."""
    return B.allowed_by_robots(url, cache) and not ai_refused(url, cache)


def licence_still_stated(page, pattern, cache=None):
    """True when the licence page still says what was checked (its words, tags removed, match pattern)."""
    if not readable(page, cache):
        return False
    words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", B.fetch(page, cache))).split())
    return bool(re.search(pattern, words))


# ====================================================================== cleaning a recipe's HTML

KEEP = {"h2", "h3", "h4", "p", "ul", "ol", "li", "strong", "em", "b", "i", "br", "sup", "sub"}


def words_of(fragment):
    """Plain text of an HTML fragment: tags dropped, entities read, spaces tidied."""
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment or "", flags=re.S | re.I)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def table_lists(fragment, heading=""):
    """Each <table> as a heading and a list ("Prep Time: 10 minutes"): a table whose head has one cell
    ("Nutritional Facts") takes that as its heading, else heading (when given)."""
    def one(m):
        """One table as <h2> and <ul>."""
        table = m.group(0)
        head = re.search(r"<thead\b.*?</thead>", table, re.S)
        title = words_of(head.group(0)) if head else heading
        rows = []
        for row in re.findall(r"<tr\b.*?</tr>", re.sub(r"<thead\b.*?</thead>", "", table, flags=re.S), re.S):
            cells = [words_of(c) for c in re.findall(r"<t[hd]\b.*?</t[hd]>", row, re.S)]
            cells = [c for c in cells if c]
            if cells:
                rows.append(": ".join(cells) if len(cells) == 2 else " | ".join(cells))
        items = "".join(f"<li>{B.esc(r)}</li>" for r in rows)
        return (f"<h2>{B.esc(title)}</h2>" if title else "") + (f"<ul>{items}</ul>" if items else "")
    return re.sub(r"<table\b.*?</table>", one, fragment, flags=re.S)


def clean_fragment(fragment):
    """A recipe's HTML kept to headings, paragraphs, lists and emphasis, without attributes, pictures, scripts,
    forms or the site's buttons; "visually hidden" labels such as "Information:" become "Tip:"."""
    text = re.sub(r"<(script|style|svg|button|form|figure|noscript|iframe)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    text = re.sub(r"<span[^>]*visually-hidden[^>]*>\s*Information:\s*</span>", "Tip: ", text)
    text = re.sub(r"<summary\b[^>]*>(.*?)</summary>", r"<h2>\1</h2>", text, flags=re.S)
    text = re.sub(r"<img\b[^>]*>", "", text)

    def tag(m):
        """One tag kept bare, or dropped."""
        name = m.group(2).lower()
        if name not in KEEP:
            return " "
        return f"<{m.group(1)}{name}>" if name != "br" else "<br>"
    text = re.sub(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>", tag, text)
    text = re.sub(r"&(?!amp;|lt;|gt;|quot;)#?[a-zA-Z0-9]+;", lambda m: html.unescape(m.group(0)), text)
    text = re.sub(r"\s+", " ", text)
    for _ in range(3):
        text = re.sub(r"<(p|li|ul|ol|h2|h3|h4|strong|em)>\s*</\1>", "", text)
    text = re.sub(r"\s*(</?(?:p|ul|ol|li|h2|h3|h4)>)\s*", r"\1", text)
    return text.replace("<li><p>", "<li>").replace("</p></li>", "</li>").replace("</p><p>Tip:", " Tip:") \
        .replace("</p>Tip:<p>", " Tip: ").strip()


# Kinds of dish, for grouping recipes whose site gives no category: (words in the title, group), first match wins.
DISH_RULES = [
    (r"breakfast|pancake|waffle|oatmeal|porridge|omelet|granola|french toast|scrambl", "Breakfast"),
    (r"smoothie|shake|lemonade|punch|\btea\b|drink|cooler|spritzer", "Drinks"),
    (r"soup|stew|chili|chowder|gumbo|broth|bisque", "Soups and stews"),
    (r"salad|slaw", "Salads"),
    (r"cake|cookie|\bpie\b|crumble|cobbler|pudding|dessert|brownie|tart|crisp|parfait|sorbet|muffin|bread|"
     r"scone|bar\b|bars\b", "Baking and desserts"),
    (r"fish|salmon|tuna|shrimp|\bcod\b|snapper|tilapia|crab|seafood|catfish|scallop|trout", "Fish and seafood"),
    (r"chicken|turkey", "Chicken and turkey"),
    (r"beef|pork|lamb|\bham\b|steak|meatball|mince|sausage|jambalaya", "Meat"),
    (r"dip|salsa|sauce|dressing|snack|wrap|sandwich|quesadilla|pizza|burrito|taco", "Snacks, sandwiches and sauces"),
    (r"bean|lentil|rice|potato|greens|squash|spinach|asparagus|vegetable|carrot|broccoli|corn|pasta|noodle|"
     r"tofu|veggie", "Vegetables, grains and beans"),
]


def dish_group(title):
    """The kind of dish a recipe's title names ("Baked Salmon Dijon" -> "Fish and seafood"); "Other dishes"."""
    t = title.lower()
    return next((g for pattern, g in DISH_RULES if re.search(pattern, t)), "Other dishes")


def recipe_ld(page):
    """The schema.org Recipe a page declares in JSON-LD ({} when none)."""
    for block in re.findall(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", page, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for item in data if isinstance(data, list) else data.get("@graph", [data]):
            if isinstance(item, dict) and "Recipe" in str(item.get("@type", "")):
                return item
    return {}


def nhlbi_recipe(page, url):
    """One NHLBI recipe page as {"title", "group", "body", "url", "ingredients"} (None when it is not a recipe):
    the description, the cookbook it comes from, ingredients, directions, then the times and servings and the
    nutrition facts from the page's two tables."""
    m = re.search(r"<article\b.*?</article>", page, re.S)
    if not m or "Ingredients" not in m.group(0):
        return None
    art = m.group(0)
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", art, re.S)
    title = words_of(h1.group(1)) if h1 else ""
    art = re.sub(r"<h1\b.*?</h1>", "", art, flags=re.S)
    art = re.sub(r'(<table\b[^>]*cooking-facts[^>]*>)', r'\1<thead><tr><th>Time and servings</th></tr></thead>', art)
    body = clean_fragment(table_lists(art, "Nutrition facts"))
    body = body.replace("<h2>Nutritional Facts</h2>", "<h2>Nutrition facts (per serving)</h2>")
    if not title or "<h2>Ingredients</h2>" not in body:
        return None
    ingredients = re.search(r"<h2>Ingredients</h2><ul>(.*?)</ul>", body)
    return {"title": title, "group": dish_group(title), "body": body, "url": url,
            "ingredients": words_of(ingredients.group(1)) if ingredients else ""}


def nhs_recipe(page, url):
    """One NHS Healthier Families recipe page as {"title", "group", "body", "url", "ingredients"} (None for a
    category page): the description, times and servings, nutrition per serving, ingredients (with their groups) and
    method (with the tips), from the page's main part up to "More recipes"."""
    ld = recipe_ld(page)
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", page, re.S)
    if not ld or not m:
        return None
    title = re.sub(r"\s+recipe$", "", words_of(m.group(1)), flags=re.I)
    rest = page[m.end():]
    stop = re.search(r"<h2[^>]*>\s*More recipes|<script[^>]*application/ld\+json|</main>", rest)
    body = clean_fragment(rest[:stop.start() if stop else None])
    body = re.sub(r"<h2>\s*Nutritional information\s*</h2>", "<h2>Nutritional information</h2>", body)
    if "<h2>Ingredients</h2>" not in body:
        return None
    categories = ld.get("recipeCategory") or []
    categories = [categories] if isinstance(categories, str) else categories
    group = categories[0].strip().capitalize() if categories else dish_group(title)
    return {"title": title[:1].upper() + title[1:], "group": group, "body": body, "url": url,
            "ingredients": "; ".join(ld.get("recipeIngredient") or [])}


def nhlbi_links(cache=None):
    """The addresses of every NHLBI recipe page, from the recipe list's pages (?page=0, 1, ... until a page adds
    none)."""
    links, n = [], 0
    while n < 100:
        page = B.fetch(f"{NHLBI_RECIPES}?page={n}", cache)
        found = [urllib.parse.urljoin(NHLBI_SITE, h) for h in
                 re.findall(r'href="(/health/heart-healthy-living/healthy-foods/healthy-eating-recipes/[a-z0-9-]+)"',
                            page)]
        new = [u for u in dict.fromkeys(found) if u not in links]
        if not new:
            break
        links += new
        n += 1
    return links


def nhs_links(cache=None):
    """The addresses linked from the NHS recipe list (recipes and category pages; category pages are passed over
    when read, because they declare no recipe)."""
    page = B.fetch(NHS_RECIPES, cache)
    found = [urllib.parse.urljoin(NHS_SITE, h) for h in re.findall(r'href="(/healthier-families/recipes/[a-z0-9-]+/)"',
                                                                    page)]
    return list(dict.fromkeys(found))


SITES = {"nhlbi": (nhlbi_links, nhlbi_recipe), "nhs": (nhs_links, nhs_recipe)}


def recipe_index(recipes):
    """The "A to Z recipe index" page body: every recipe by name, with its kind of dish, under its first letter."""
    out, letter = [], None
    for r in sorted(recipes, key=lambda r: r["title"].casefold()):
        first = r["title"][:1].upper() if r["title"][:1].isalpha() else "#"
        if first != letter:
            out.append(("</ul>" if letter else "") + f"<h2>{B.esc(first)}</h2><ul>")
            letter = first
        out.append(f'<li><a href="{B.esc(r["path"])}">{B.esc(r["title"])}</a> ({B.esc(r["group"])})</li>')
    return "<p>Every recipe of this book in alphabetical order. The contents page lists them by kind of dish.</p>" + \
        "".join(out) + ("</ul>" if letter else "")


def about_recipes(entry):
    """The "About this book" page of a recipe book: what it holds, how a recipe page reads, the licence line."""
    out = [f"<p>{B.esc(entry['description'])}</p>",
           "<p>Each recipe page reads in the publisher's order: a short description, then the ingredients, the steps "
           "(with the publisher's tips), the times and servings and the nutrition facts. Measures are as the "
           "publisher gives them.</p>", f"<p>{B.esc(NUTRITION_NOTE)}</p>",
           f"<p>Licence: {B.esc(LICENCE_LINES[entry['name']])}</p>"]
    return "".join(out)


def recipes_book(entry, cache=None, left_out=None, limit=None):
    """The Book of one recipe collection (entry["site"]: "nhlbi" or "nhs"), or None when its licence page no longer
    says what was checked or robots.txt refuses it. Pages: "About this book", "A to Z recipe index", then one page
    per recipe grouped by kind of dish. limit: read only the first so many recipes (a test build)."""
    left_out = left_out if left_out is not None else []
    if not readable(entry["source"], cache):
        left_out.append({"title": entry["title"], "reason": "robots.txt (or a block on AI readers) does not allow it."})
        return None
    if not licence_still_stated(entry["licence_page"], entry["licence_text"], cache):
        left_out.append({"title": entry["title"], "reason": f"Its licence page ({entry['licence_page']}) no longer "
                         "states the licence that was checked."})
        return None
    links, parse = SITES[entry["site"]]
    recipes, skipped = [], 0
    for url in links(cache):
        if limit and len(recipes) >= limit:
            break
        if not readable(url, cache):
            skipped += 1
            continue
        try:
            recipe = parse(B.fetch(url, cache), url)
        except (urllib.error.URLError, OSError):
            skipped += 1
            continue
        if recipe:
            recipes.append(recipe)
    if skipped:
        left_out.append({"title": entry["title"], "reason": f"{skipped} recipe pages could not be read or are not "
                         "allowed by robots.txt."})
    book = make_book(entry)
    used = {"index", "style-css", "about-this-book", "recipe-index"}
    for r in recipes:
        path = B.slug(r["title"], 50)
        while path in used:
            path += "-2"
        used.add(path)
        r["path"] = path
    groups = sorted({r["group"] for r in recipes}, key=lambda g: (g == "Other dishes", g))
    book.pages = [B.Page("about-this-book", "About this book", about_recipes(entry)),
                  B.Page("recipe-index", "A to Z recipe index", recipe_index(recipes))] if recipes else []
    for g in groups:
        for r in sorted((x for x in recipes if x["group"] == g), key=lambda x: x["title"].casefold()):
            body = r["body"] + (f'<p>Original recipe: <a href="{B.esc(r["url"])}">{B.esc(r["url"])}</a>.</p>')
            book.pages.append(B.Page(r["path"], r["title"], body, 0, g))
    book.recipes = recipes
    return book


def make_book(entry, **more):
    """A Book from an entry of BOOKS (the group, subject, notices and practice note this module gives every
    cookbook)."""
    changes = more.pop("changes", None) or entry.get("changes") or (
        "each recipe page made into a book page with the site's menus and pictures left out; the recipe's words and "
        "measures unchanged")
    notice = " ".join(x for x in [SAFETY_NOTICES.get(entry["topic"], ""),
                                  OLD_NOTE.format(year=entry.get("published", "")) if entry.get("old") else ""] if x)
    return B.Book(name=entry["name"], title=entry["title"], subject=subject_of(entry), level="reference", group=GROUP,
                  publisher=entry["publisher"], country=entry["country"], licence=entry.get("licence", ""),
                  licence_url=entry.get("licence_url", ""), source=entry.get("source") or entry.get("page") or entry.get("archive", ""),
                  description=entry["description"],
                  notice=notice, practice_note=UK_NOTE if entry["country"] == "United Kingdom" else "",
                  published=entry.get("published", ""),
                  changes=changes, **more)


def subject_of(entry):
    """The book's subject: "Cooking: <topic>"."""
    return entry.get("subject") or f"Cooking: {TOPICS[entry['topic']]}"


# ====================================================================== the links-only book (NCHFP)

def nchfp_book(entry, cache=None, left_out=None):
    """The links-only book of the National Center for Home Food Preservation: one page per method (NCHFP_METHODS),
    each listing the recipe and instruction pages its method page links to (their names and addresses only, grouped
    by the part of the site they are in, such as "Canning fruits and fruit products"). Nothing of the recipes is
    copied: the site says "All rights reserved"."""
    left_out = left_out if left_out is not None else []
    book = make_book(dict(entry, licence="CC0 1.0", licence_url="https://creativecommons.org/publicdomain/zero/1.0/",
                          publisher="GetBraille.com (toolkit-models): a list of the pages of the National Center for "
                                    "Home Food Preservation (University of Georgia)"),
                     changes="only the names and web addresses of the Center's pages, listed by method; no text "
                             "of the recipes is copied")
    pages = [B.Page("about-this-book", "About this book",
                    f"<p>{B.esc(entry['description'])}</p><p>{B.esc(LICENCE_LINES['nchfp_links'])}</p>"
                    f"<p>{B.esc(SAFETY_NOTICES['preserving'])}</p>")]
    for slug_, name in NCHFP_METHODS:
        url = f"{NCHFP}/how/{slug_}"
        if not readable(url, cache):
            left_out.append({"title": f"NCHFP {name}", "reason": "robots.txt does not allow it."})
            continue
        try:
            page = B.fetch(url, cache)
        except (urllib.error.URLError, OSError) as e:
            left_out.append({"title": f"NCHFP {name}", "reason": f"It could not be read ({e})."})
            continue
        parts = {}
        for href, text in re.findall(rf'<a[^>]*href="(/how/{re.escape(slug_)}/[^"#]+)"[^>]*>(.*?)</a>', page, re.S):
            words = words_of(text)
            pieces = href.strip("/").split("/")
            if not words or len(pieces) < 3:
                continue
            part = pieces[2].replace("-", " ").capitalize() if len(pieces) > 3 else name
            link = urllib.parse.urljoin(NCHFP, href)
            if all(link != u for u, _w in parts.get(part, [])):
                parts.setdefault(part, []).append((link, words))
        if not parts:
            continue
        body = [f'<p>The Center\'s page on {B.esc(name.lower())}: <a href="{B.esc(url)}">{B.esc(url)}</a>. Each name '
                "below is a link to the Center's own page.</p>"]
        for part, links in parts.items():
            body.append(f"<h2>{B.esc(part)}</h2><ul>" + "".join(
                f'<li><a href="{B.esc(u)}">{B.esc(w)}</a> ({B.esc(u)})</li>' for u, w in links) + "</ul>")
        pages.append(B.Page(B.slug(name), name, "".join(body), 0, "Methods"))
    book.pages = pages if len(pages) > 1 else []
    return book


# ====================================================================== the library guide

KIWIX_COOKING = [
    ("usda-2015_en", "USDA Guide to Home Canning", "the USDA Complete Guide to Home Canning (2015), public domain: "
     "the tested canning method and processing times; use it for all canning"),
    ("wikibooks_en_all", "Wikibooks", "Wikibooks' Cookbook: thousands of recipes, ingredients and techniques (CC "
     "BY-SA)"),
    ("gutenberg_en_lcc-t", "Project Gutenberg Library: Technology", "Project Gutenberg's old cookery books (class TX, "
     "home economics); old, so their food safety advice is out of date"),
    ("publicdomainrecipes.com_en_all", "Public Domain Recipes", "a recipe collection released into the public domain"),
    ("based.cooking_en_all", "based.cooking", "short, simple recipes submitted by readers (public domain)"),
    ("foss.cooking_en_all", "FOSS cooking", "recipes from an open cooking site"),
    ("grimgrains_en_all", "GrimGrains Recipes", "plant-based recipes"),
    ("cooking.stackexchange.com_en_all", "Cooking Q&A (Seasoned Advice)", "questions and answers on cooking (CC "
     "BY-SA); for reading and looking things up only, not for AI training (Stack Exchange's terms)"),
    ("zimgit-food-preparation_en", "Food for Preppers", "recipes and techniques for preparing and storing food"),
    ("canadian-prepper_en_preppingfood", "Canadian prepper: Prepping Food", "long-term food storage and survival "
     "meals (videos)"),
]


def library_book(entry, recipe_books=(), cache=None, left_out=None):
    """The library guide: for each topic, the books of this module (by title) and the Kiwix library's cooking books
    that cover it; a recipe index of the recipe books built in this run (recipe name and the book it is in); the
    safety notices; and what could not be included, with the reason. It is written by this project (CC0)."""
    book = make_book(entry, changes="written for this library")
    pages = []
    for topic, name in TOPICS.items():
        if topic == "guide":
            continue
        ours = [b for b in BOOKS if b["topic"] == topic and b["kind"] != "library"]
        body = ["<ul>"] + [f"<li>{B.esc(b['title'])}: {B.esc(b['description'])}</li>" for b in ours] + ["</ul>"]
        if topic in SAFETY_NOTICES:
            body.append(f"<p>{B.esc(SAFETY_NOTICES[topic])}</p>")
        if topic == "preserving":
            body.append("<p>Also in the Kiwix library: the USDA Guide to Home Canning (usda-2015_en).</p>")
        pages.append(B.Page(B.slug(name, 40), name[:1].upper() + name[1:], "".join(body), 0, "Topics"))
    kiwix = "".join(f"<li>{B.esc(t)} ({B.esc(n)}): {B.esc(d)}.</li>" for n, t, d in KIWIX_COOKING)
    pages.append(B.Page("kiwix-cooking-books", "Cooking books in the Kiwix library",
                        "<p>These come from the Kiwix library, which the toolkit lists too; they are not built "
                        f"again here.</p><ul>{kiwix}</ul>", 0, "More"))
    rows = sorted(((r["title"], b.title) for b in recipe_books for r in getattr(b, "recipes", [])),
                  key=lambda x: x[0].casefold())
    if rows:
        items = "".join(f"<li>{B.esc(t)}: in {B.esc(bt)}</li>" for t, bt in rows)
        pages.append(B.Page("recipe-index", "Recipe index (all recipe books)",
                            f"<p>{len(rows)} recipes, A to Z, with the book each one is in.</p><ul>{items}</ul>", 0,
                            "More"))
    notes = "".join(f"<h2>{B.esc(TOPICS[k][:1].upper() + TOPICS[k][1:])}</h2><p>{B.esc(v)}</p>"
                    for k, v in SAFETY_NOTICES.items())
    pages.append(B.Page("safety-notices", "Safety notices", notes + "<h2>Old books</h2><p>" +
                        B.esc(OLD_NOTE.format(year="the year on its title page")) + "</p>", 0, "More"))
    left = "".join(f"<li>{B.esc(n)}: {B.esc(r)}</li>" for n, r in NOT_INCLUDED)
    pages.append(B.Page("not-included", "Not in the library, and why", f"<ul>{left}</ul>", 0, "More"))
    book.pages = pages
    return book


# ====================================================================== the build

def make(entry, work, cache=None, left_out=None, limit=None):
    """The Book of one entry of BOOKS (None when it may not be built now; the reason is in left_out)."""
    left_out = left_out if left_out is not None else []
    kind = entry["kind"]
    if kind == "recipes":
        return recipes_book(entry, cache, left_out, limit)
    if kind == "links":
        return nchfp_book(entry, cache, left_out)
    if kind == "library":
        return library_book(entry, (), cache, left_out)
    spec = dict(entry, subject=subject_of(entry))
    first = spec.get("page") or (spec.get("start") or [""])[0] or \
        (f"https://archive.org/metadata/{spec['archive']}" if spec.get("archive") else "")
    if first and ai_refused(first, cache):
        left_out.append({"title": entry["title"], "reason": "The site shuts out AI companies' readers."})
        return None
    if kind == "guide":
        if limit:
            spec["limit"] = limit
        book = B.webguide_book(spec, cache, left_out)
    else:
        book = B.pdfdoc_book(spec, work, cache, left_out)
    if book is None:
        return None
    ours = make_book(dict(entry, published=book.published or entry.get("published", "")))
    book.group, book.subject = GROUP, ours.subject
    book.notice = " ".join(x for x in [book.notice, ours.notice] if x)
    book.practice_note = ours.practice_note
    if entry.get("old") and limit:
        book.pages = book.pages[:limit]
    return book


def expand_keys(words):
    """The keys (cook:<name>) the words stand for: "cookbooks" (every book) or cook:<name>."""
    keys = []
    for w in words:
        if w == "cookbooks":
            keys += [f"cook:{b['name']}" for b in BOOKS]
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change of one key ("" when it cannot be asked): the recipe list's addresses for a
    recipe book (a new or removed recipe rebuilds it), the PDF's checksum or headers for a PDF book
    (updates.pdf_sign), the guide's pages for a web guide (updates.guide_sign), the method pages' links for the
    NCHFP book; the library guide follows this module's book list."""
    import updates                               # here, not at the top: updates imports the builder
    entry = BY_NAME.get(key.split(":", 1)[1])
    if entry is None:
        import cooking_basics                    # the cooking basics books share the prefix cook: (cooking_basics.py)
        return cooking_basics.COLLECTION.sign(key) if key in cooking_basics.COLLECTION.own_keys() else ""
    try:
        if entry["kind"] == "recipes":
            return hashlib.sha256(json.dumps(SITES[entry["site"]][0]()).encode()).hexdigest()[:24]
        if entry["kind"] == "pdf":
            return updates.pdf_sign(entry)
        if entry["kind"] == "guide":
            return updates.guide_sign(entry)
        if entry["kind"] == "links":
            return hashlib.sha256("".join(B.fetch(f"{NCHFP}/how/{m}") for m, _n in NCHFP_METHODS).encode()
                                  ).hexdigest()[:24]
        if entry["kind"] == "library":
            return hashlib.sha256(json.dumps([b["name"] for b in BOOKS]).encode()).hexdigest()[:24]
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return ""
    return ""


def build_cookbooks(keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys into out_dir and write manifest-<key>.json for each (as build_textbooks.build does);
    returns {key: manifest}. Every book is a new version (versioned file names). limit: a small test build (only
    that many recipes, pages or chapters; manifests named "..._sample")."""
    manifests = {}
    work = os.path.join(cache or out_dir, "work")
    os.makedirs(out_dir, exist_ok=True)
    recipe_books = []
    plan = expand_keys(keys)
    import cooking_basics                        # the cooking basics books share the prefix cook: (cooking_basics.py)
    theirs = [k for k in plan if k in cooking_basics.COLLECTION.own_keys()]
    if theirs:
        manifests.update(cooking_basics.COLLECTION.build(theirs, out_dir, cache, date, limit))
        plan = [k for k in plan if k not in theirs]
    plan.sort(key=lambda k: k.endswith("cookbooks_library_guide"))     # the guide last: it lists the recipes built
    for key in plan:
        entry = BY_NAME.get(key.split(":", 1)[1]) if key.startswith("cook:") else None
        left_out, entries = [], []
        if entry is None:
            print(f"Unknown key {key}; skipped.")
            continue
        fingerprint = "" if limit else sign(key)
        try:
            if entry["kind"] == "library":
                book = library_book(entry, recipe_books, cache, left_out)
            else:
                book = make(entry, work, cache, left_out, limit)
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": entry["title"], "reason": f"It could not be built ({e})."})
            book = None
        if book is not None and not book.pages:
            left_out.append({"title": entry["title"], "reason": "No pages could be read."})
            book = None
        if book is not None:
            if entry["kind"] == "recipes":
                recipe_books.append(book)
            out = B.write_book(book, out_dir, date, versioned=True)
            out.update({"key": key, "fingerprint": fingerprint, "topic": entry["topic"]})
            print(f"{out['file']}: {out['article_count']} pages, {out['size']:,} bytes, {out['licence_text']}")
            entries.append(out)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": "textbooks", "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if limit else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "nhlbi_heart_healthy_recipes": "NHLBI (www.nhlbi.nih.gov/about/contact/trademark-branding-and-logo, read "
                                   "2026-11-21, checked again at every build): \"Most of the information on the NHLBI "
                                   "website is in the public domain and can be used without restriction.\" robots.txt "
                                   "allows the recipe pages.",
    "nhs_healthier_families_recipes": "NHS website terms (www.nhs.uk/our-policies/terms-and-conditions/, checked at "
                                      "every build): \"Copyright and database rights in NHS Website Content are "
                                      "released free-of-charge under the current version of the Open Government "
                                      "Licence (\"OGL\"), except where specified\". The recipes' pictures are not "
                                      "copied. robots.txt allows /healthier-families/.",
    "fna_cookbooks": "USDA Food and Nutrition Administration (www.fna.usda.gov, formerly fns.usda.gov) publications are "
                     "works of the US government (17 U.S.C. 105, as quoted on govinfo.gov's policy page, checked at "
                     "every build); its robots.txt allows /sites/default/files/.",
    "fda_food": "FDA website policies (checked at every build): \"They are in the public domain and may be "
                "republished, reprinted and otherwise used freely\".",
    "army_recipes": "TM 10-412 (1946) and TM 10-405 (1942) are US War Department manuals (US government works); the "
                    "Internet Archive marks both with the Public Domain Mark.",
    "old_cookbooks": "The old cookbooks were published in the United States before 1931 (more than 95 years ago), so "
                     "they are in the US public domain; the builder checks each Internet Archive item's year at every "
                     "build and leaves it out when it is 1931 or later.",
    "nchfp_links": "National Center for Home Food Preservation (nchfp.uga.edu, University of Georgia): every page says "
                   "\"Copyright © 2026 National Center for Home Food Preservation, All rights reserved\", so only the "
                   "names and addresses of its pages are listed (robots.txt: \"Allow: /\"). Its USDA-funded recipes "
                   "are still the Center's copyright on its site; the USDA Complete Guide to Home Canning itself is in "
                   "the Kiwix library (usda-2015_en).",
}

KIWIX_LABELS = {"usda-2015_en": "public domain (USDA)", "publicdomainrecipes.com_en_all": "public domain",
                "based.cooking_en_all": "public domain", "wikibooks_en_all": "CC BY-SA",
                "cooking.stackexchange.com_en_all": "CC BY-SA"}

GROUP_NOTES = {GROUP: "Cookbooks and recipes: heart-healthy and family recipes (NHLBI, NHS), USDA cookbooks, kitchen "
                      "safety, preserving links, US Army recipes, and old public-domain cookbooks (marked old: food "
                      "safety advice has changed)."}

NOT_INCLUDED = [
    ("USDA MyPlate Kitchen recipes (www.myplate.gov)", "Public domain, but www.myplate.gov could not be reached from "
     "the build machine (the connection is refused upstream, 502), again on 2026-11-21, and no bulk download or API "
     "of the recipe database was found on catalog.data.gov or the National Agricultural Library. The USDA Team "
     "Nutrition and FDPIR cookbooks from fna.usda.gov are built instead."),
    ("SNAP-Ed Connection recipes (snaped.fns.usda.gov)", "Could not be reached from the build machine (502), like "
     "MyPlate; its recipes moved into MyPlate Kitchen."),
    ("USDA FSIS food safety guides (smoking meat, safe temperatures, jerky)", "Public domain, but www.fsis.usda.gov "
     "refuses automated requests (403, robots.txt included). The safe temperatures and smoking advice are summed up "
     "in the smoking and sausage books' safety notices; FDA's kitchen safety pages are built."),
    ("CDC diabetes recipes and the CDC's food safety pages", "Public domain, but www.cdc.gov refuses automated "
     "requests (403)."),
    ("NIDDK diet and nutrition pages", "Already in the library (guide:niddk_health_information); NIDDK has no "
     "recipe collection of its own now."),
    ("USDA Complete Guide to Home Canning", "Already in the Kiwix library (usda-2015_en), so it is not built again."),
    ("National Center for Home Food Preservation recipes (text)", "The site is \"All rights reserved\" (University "
     "of Georgia), so its recipes are listed as links only (cook:nchfp_preserving_links). \"So Easy to Preserve\" "
     "is a book sold by the University of Georgia."),
    ("Armed Forces Recipe Service today (quartermaster.army.mil, TM 10-412 recipe cards)", "The Army's Joint "
     "Culinary Center site could not be reached from the build machine; the 1946 TM 10-412 and the 1942 Army Cook "
     "from the Internet Archive are built. The 1957 to 1962 TM 10-412 parts on the Internet Archive are incomplete "
     "scans and are not built."),
    ("Health Canada and Canada's Food Guide recipes (food-guide.canada.ca, canada.ca)", "food-guide.canada.ca now "
     "sends readers to www.canada.ca, which could not be reached from the build machine (its connection is closed), "
     "and canada.ca's terms allow non-commercial reproduction only; open.canada.ca lists no recipe publication under "
     "the Open Government Licence (searched 2026-11-21). Could be added later, personal use only."),
    ("UK Food Standards Agency", "The FSA's pages moved to GOV.UK (Open Government Licence v3.0); they are food "
     "safety and allergy guidance, not recipes. Its consumer allergy advice could be added as a GOV.UK guide later."),
    ("University extension cooking, preserving and cheese-making publications", "Each university's copyright (some "
     "\"may be reproduced for non-commercial educational use\", some CC BY-NC-ND); none was checked one by one in "
     "this pass. The tested preserving recipes are reached through the NCHFP links book."),
    ("Recipe1M and RecipeNLG datasets", "Non-commercial (personal use) but both need an account or a signed form to "
     "download, and their recipes were copied from recipe websites whose own copyright is unclear; not built."),
    ("Diabetic Cookery (Rebecca Oppenheimer, 1917) and the Ryzon Baking Book (1917)", "Believed to be in Project "
     "Gutenberg (in the Kiwix library); Gutenberg's catalogue could not be reached to check, so they are left out to "
     "avoid a copy. The 1917 diabetic diet came before insulin and is not safe advice today."),
    ("Accessible cooking for blind people", "No openly licensed material was found: the Hadley Institute's cooking "
     "courses, the National Federation of the Blind's and the American Foundation for the Blind's (VisionAware) "
     "kitchen articles, and RNIB's guides are each the organisation's copyright. They are free to read on their own "
     "sites."),
    ("Project Gutenberg and Wikibooks Cookbook", "Already in the Kiwix library (gutenberg_en_lcc-t, wikibooks_en_all); "
     "not built again."),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["cookbooks"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many recipes or pages")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build_cookbooks(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
