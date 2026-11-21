"""Picture packs for DRINKS: alcoholic drinks (wine, beer, spirits, cocktails), glassware, bar equipment and serving
formats, brewing, winemaking and distilling, and every other drink (soft drinks, energy drinks, juices, waters,
coffee and tea drinks, plant milks, mixes and syrups, mocktails). Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than
one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

The owner's request of 2026-11-21. The alcohol packs and the other drink packs have separate keys
(DRINKS_ALCOHOL_KEYS, DRINKS_SOFT_KEYS), so a training can leave the alcohol packs out on their own. The soft drinks
are in the kit's food topic; the alcohol packs are in no topic (the owner's ten topics are unchanged), so a topic
add-on never learns alcohol by chance.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed, a Europeana
record's title and description), never a guess: no alcohol content, vintage or caffeine amount is ever made up (the
sources give none, so none is said unless a file's own caption states it). Notes:
  ALCOHOL_NOTE        after every answer about an alcoholic drink: "Contains alcohol. Not for people under the legal
                      drinking age, during pregnancy, or before driving."
  CAFFEINE_NOTE       after every answer about an energy drink or a drink people labelled caffeinated.
  DISTILLING_WARNING  BEFORE every answer about a still or moonshine (home distilling): in the US it is illegal
                      without federal permits (26 U.S.C. 5601), unlike home brewing and winemaking; laws differ (New
                      Zealand allows home distilling); methanol, fire and pressure risks. Pictures of licensed
                      distilleries (warehouses, casks, spirit safes) get the shorter DISTILLERY_NOTE after.

The packs:
  alcohol (DRINKS_ALCOHOL_KEYS)
    commons_alcoholic_drinks   Wikimedia Commons (CC0, public domain or CC BY files only): wine bottles and labels
                               and wines by region, wine in the glass by colour, beer bottles, cans, labels and beer
                               styles, whisky, bourbon, vodka, gin, rum, tequila, brandy, liqueurs, absinthe, sake,
                               cider, mead and cocktails by name. "What drink is shown here?" -> "It shows wine from
                               Bordeaux, France. Contains alcohol. ..."
    commons_bar_glassware      Commons: glassware (wine, beer, champagne, shot, pint, cocktail glasses, snifters,
                               steins, decanters), bar tools (shakers, jiggers, bar spoons, corkscrews, bottle
                               openers) and serving formats (kegs, beer taps and engines, draught beer, growlers,
                               bag-in-box wine, wine barrels and cellars).
    commons_brewing_winemaking Commons: home and commercial brewing (homebrewing, brew kettles, fermenters and
                               fermentation tanks, airlocks, hydrometers, carboys, breweries), winemaking (grape
                               crushers, wine presses, riddling racks, vineyards, grape harvest, wineries) and the
                               ingredients (barley, malt, hops, hop kilns).
    commons_distilling         Commons: pot stills, distillation apparatus, distilleries and their equipment, with
                               DISTILLING_WARNING first on still pictures.
    open_images_bar_drinks     Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or Public Domain Mark): wine by
                               colour, beer styles, spirits and cocktails, glassware and bar things, kegs, taps and
                               barrels, bars, pubs, breweries, wineries and vineyards, brewing ingredients. No label
                               is asked twice (none another pack asks: packs/test_drinks.py checks).
    europeana_drinks_history   Europeana: English records with CC0, Public Domain Mark or CC BY rights of historic
                               wine and beer bottles, decanters, tankards, wine presses, breweries and distilleries.
  other drinks (DRINKS_SOFT_KEYS)
    commons_soft_drinks        Commons: soft drink cans and bottles, colas, energy drinks (with CAFFEINE_NOTE), fruit
                               juices, sports drinks, bottled and sparkling waters, iced tea and canned coffee,
                               kombucha, plant milks, smoothies, milkshakes, lemonade, root beer, ginger ale and
                               tonic, drink mixes and syrups, mocktails and non-alcoholic beer.
    open_images_soft_drinks    Open Images: colas and sodas, juices, smoothies, milkshakes, plant milks, coffee and tea
                               drinks, mineral water, drink mixes and syrups.

Not repeated here: abo_packaged_goods (Amazon Berkeley Objects already names packaged drinks, wine and spirits by
their listings), open_images_food_more (Cocktail, Cocktail shaker, Beer, Wine, Whisky, Champagne, Shot glass) and
open_images_packaged_goods (drink cans, bottles, bottled water, energy drinks, soft drinks). What was looked at and
left out (Open Food Facts, the TTB COLA registry and others) is in the kit's drinks_sources.py.

    python packs/drinks_packs.py commons_distilling --limit 8      (prints a few rows: a quick check)
"""

import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, pass_random, first_sentences
from gaps_oi_packs import group, build_oi_gap, QUICK

ALCOHOL_NOTE = "Contains alcohol. Not for people under the legal drinking age, during pregnancy, or before driving."
CAFFEINE_NOTE = ("High in caffeine; not recommended for children, during pregnancy, or for people sensitive to "
                 "caffeine.")
DISTILLING_WARNING = ("Legal and safety notes first: in the US, distilling spirits at home is illegal without federal "
                      "permits, even for personal use (26 U.S.C. 5601), unlike home brewing and winemaking, which "
                      "federal law allows for adults within limits; laws differ by state and country (New Zealand, "
                      "for example, allows home distilling). Distilling carries real risks: methanol poisoning from "
                      "improper cuts, fire and explosion from ethanol vapour, and pressure.")
DISTILLERY_NOTE = "Distilleries like this one work under licence; distilling at home without federal permits is " \
                  "illegal in the US (26 U.S.C. 5601)."
ASK_DRINK = "What drink is shown here?"
ASK_WHAT = "What is this?"


def drink(category, thing, note=ALCOHOL_NOTE, deeper=True, question=ASK_DRINK):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, answer)]), the answer being
    "It shows <thing>." and the note."""
    return (category, deeper, [(question, f"It shows {thing}." + (f" {note}" if note else ""))])


def thing(category, words, note="", deeper=True):
    """A Commons spec for a thing, not a drink: "What is this?" -> "This is <words>." and the note after."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {note}" if note else ""))])


def still(category, words, deeper=True):
    """A Commons spec for a still: the distilling warning FIRST, then what it is."""
    return (category, deeper, [(ASK_WHAT, f"{DISTILLING_WARNING} This is {words}.")])


# ----------------------------------------------------------------- Commons: alcoholic drinks

ALCOHOLIC_DRINKS = [
    drink("Wine bottles", "a bottle of wine"),
    drink("Wine labels", "a wine label"),
    drink("Wines of Bordeaux", "wine from Bordeaux, France"),
    drink("Wines of France", "wine from France"),
    drink("Wines of Italy", "wine from Italy"),
    drink("Chianti", "Chianti, a red wine from Tuscany, Italy"),
    drink("Wines of Spain", "wine from Spain"),
    drink("Wines of Portugal", "wine from Portugal"),
    drink("Port wine", "port, a sweet fortified wine from Portugal"),
    drink("Wines of Germany", "wine from Germany"),
    drink("Wines of California", "wine from California"),
    drink("Wines of Oregon", "wine from Oregon"),
    drink("Wines of Washington (state)", "wine from Washington State"),
    drink("Wines of Australia", "wine from Australia"),
    drink("Wines of New Zealand", "wine from New Zealand"),
    drink("Wines of Chile", "wine from Chile"),
    drink("Wines of Argentina", "wine from Argentina"),
    drink("Wines of South Africa", "wine from South Africa"),
    drink("Glasses of red wine", "a glass of red wine"),
    drink("Glasses of white wine", "a glass of white wine"),
    drink("Red wine", "red wine"),
    drink("White wine", "white wine"),
    drink("Rosé wine", "rosé wine, a pink wine"),
    drink("Sparkling wine", "sparkling wine, a wine with bubbles"),
    drink("Beer bottles", "a bottle of beer"),
    drink("Beer cans", "a can of beer"),
    drink("Beer labels", "a beer label"),
    drink("Glasses of beer", "a glass of beer"),
    drink("Pilsner", "pilsner, a pale golden lager"),
    drink("Stout", "stout, a very dark, almost black beer"),
    drink("Wheat beers", "wheat beer, often pale and cloudy"),
    drink("Draught beer", "draught beer, poured from a tap"),
    drink("Whisky", "whisky, a spirit distilled from grain"),
    drink("Whisky bottles", "a bottle of whisky"),
    drink("Bourbon whiskey", "bourbon, an American whiskey made mostly from corn"),
    drink("Vodkas", "vodka"),
    drink("Vodka bottles", "a bottle of vodka"),
    drink("Gin", "gin, a spirit flavoured with juniper"),
    drink("Rum", "rum, a spirit made from sugar cane"),
    drink("Rum bottles", "a bottle of rum"),
    drink("Tequila", "tequila, a Mexican spirit made from blue agave"),
    drink("Tequila bottles", "a bottle of tequila"),
    drink("Brandy", "brandy, a spirit distilled from wine or fruit"),
    drink("Liqueurs", "a liqueur, a sweetened, flavoured spirit"),
    drink("Absinthe", "absinthe, a strong anise-flavoured spirit"),
    drink("Sake", "sake, a Japanese rice wine"),
    drink("Sake bottles", "a bottle of sake"),
    drink("Cider", "cider, a drink made from fermented apples"),
    drink("Mead", "mead, a drink made from fermented honey"),
    drink("Cocktails", "a cocktail, a mixed drink"),
    drink("Martini (cocktail)", "a martini cocktail"),
    drink("Margarita (cocktail)", "a margarita cocktail"),
    drink("Mojito", "a mojito cocktail"),
    drink("Negroni", "a negroni cocktail"),
    drink("Manhattan (cocktail)", "a Manhattan cocktail"),
    drink("Bloody Mary", "a Bloody Mary cocktail"),
]

# ----------------------------------------------------------------- Commons: glassware, bar tools, serving formats

BAR_GLASSWARE = [
    thing("Wine glasses", "a wine glass"),
    thing("Beer glasses", "a beer glass"),
    thing("Champagne glasses", "a champagne glass (a flute or coupe)"),
    thing("Shot glasses", "a shot glass"),
    thing("Pint glasses", "a pint glass"),
    thing("Cocktail glasses", "a cocktail glass"),
    thing("Snifters", "a snifter, a short-stemmed glass for brandy"),
    thing("Beer steins", "a beer stein, a large mug for beer"),
    thing("Decanters", "a decanter, a glass vessel for serving wine or spirits"),
    thing("Cocktail shakers", "a cocktail shaker"),
    thing("Jiggers", "a jigger, a small measure for spirits"),
    thing("Bar spoons", "a bar spoon, a long spoon for stirring drinks"),
    thing("Corkscrews", "a corkscrew"),
    thing("Bottle openers", "a bottle opener"),
    thing("Beer kegs", "a beer keg, a metal barrel for beer"),
    thing("Kegs", "a keg"),
    thing("Beer taps", "a beer tap, for pouring draught beer"),
    thing("Beer engines", "a beer engine, a hand pump for cask ale"),
    thing("Growlers", "a growler, a jug for carrying draught beer"),
    thing("Bag-in-box", "a bag-in-box container (boxed wine and other drinks come in these)"),
    thing("Wine barrels", "a wine barrel"),
    thing("Wine cellars", "a wine cellar"),
    thing("Wine tasting", "a wine tasting", ALCOHOL_NOTE),
]

# ----------------------------------------------------------------- Commons: brewing and winemaking

HOME_LEGAL = ("In the US, adults may brew beer and make wine at home for personal use, within federal limits "
              "(27 CFR 25.205 and 24.75).")
BREWING_WINEMAKING = [
    thing("Homebrewing", "home brewing: making beer at home", HOME_LEGAL),
    thing("Brew kettles", "a brew kettle, where the wort is boiled with hops"),
    thing("Fermenters", "a fermenter, where yeast turns wort into beer"),
    thing("Fermentation tanks", "a fermentation tank"),
    thing("Airlocks", "an airlock (fermentation lock), which lets gas out of a fermenter and keeps air out"),
    thing("Fermentation locks", "a fermentation lock (airlock)"),
    thing("Hydrometers", "a hydrometer, which measures how much sugar is in a liquid"),
    thing("Carboys", "a carboy, a large glass or plastic jug used for fermenting"),
    thing("Breweries", "a brewery"),
    thing("Brewing", "brewing"),
    thing("Malting", "malting: sprouting and drying grain to make malt"),
    thing("Barley", "barley, the grain most beer is made from"),
    thing("Malt", "malt: sprouted and dried grain for brewing"),
    thing("Hops", "hops, the flowers that give beer its bitterness and aroma"),
    thing("Hop kilns", "a hop kiln (oast house), where hops are dried"),
    thing("Grape crushers", "a grape crusher, which breaks the grapes before pressing"),
    thing("Wine presses", "a wine press"),
    thing("Riddling racks", "a riddling rack, which holds sparkling wine bottles neck down"),
    thing("Vineyards", "a vineyard"),
    thing("Grape harvest", "the grape harvest"),
    thing("Wineries", "a winery"),
]

# ----------------------------------------------------------------- Commons: distilling

DISTILLING = [
    still("Pot stills", "a pot still, a copper still for making spirits such as whisky"),
    still("Distillation apparatus", "distillation apparatus"),
    thing("Distilleries", "a distillery", DISTILLERY_NOTE),
]

# ----------------------------------------------------------------- Commons: soft drinks and other drinks

# Brand categories hold logos, adverts and sponsored teams too: only files whose own words say can, bottle or drink.
DRINK_WORDS = re.compile(r"\b(cans?|bottles?|drinks?|beverages?)\b", re.I)

SOFT_DRINKS = [
    drink("Soft drink cans", "a can of soft drink", ""),
    drink("Soft drink bottles", "a bottle of soft drink", ""),
    drink("Soft drinks", "a soft drink", ""),
    drink("Energy drinks", "an energy drink", CAFFEINE_NOTE),
    drink("Energy drinks by brand", "an energy drink", CAFFEINE_NOTE) + (DRINK_WORDS,),
    drink("Coca-Cola bottles", "a bottle of Coca-Cola, a cola soft drink", ""),
    drink("Grape juice", "grape juice", ""),
    drink("Cranberry juice", "cranberry juice", ""),
    drink("Tomato juice", "tomato juice", ""),
    drink("Rice milk", "rice milk", ""),
    drink("Bubble tea", "bubble tea, a sweet tea drink with chewy tapioca pearls", ""),
    drink("Kool-Aid", "Kool-Aid, a drink mix", ""),
    thing("Soda fountains", "a soda fountain, which pours soft drinks"),
    thing("Beverage vending machines", "a drinks vending machine"),
    drink("Fruit juices", "fruit juice", ""),
    drink("Orange juice", "orange juice", ""),
    drink("Apple juice", "apple juice", ""),
    drink("Sports drinks", "a sports drink", ""),
    drink("Bottled water", "bottled water", ""),
    drink("Carbonated water", "sparkling (carbonated) water", ""),
    drink("Iced tea", "iced tea", ""),
    drink("Canned coffee", "canned coffee", ""),
    drink("Iced coffee", "iced coffee", ""),
    drink("Kombucha", "kombucha, a fermented tea drink", ""),
    drink("Soy milk", "soy milk", ""),
    drink("Almond milk", "almond milk", ""),
    drink("Oat milk", "oat milk", ""),
    drink("Smoothies", "a smoothie", ""),
    drink("Milkshakes", "a milkshake", ""),
    drink("Lemonade", "lemonade", ""),
    drink("Root beer", "root beer, a sweet fizzy drink without alcohol", ""),
    drink("Ginger ale", "ginger ale", ""),
    drink("Tonic water", "tonic water", ""),
    drink("Coconut water", "coconut water", ""),
    drink("Syrups", "a syrup", ""),
    drink("Mocktails", "a mocktail, a mixed drink without alcohol", ""),
]


def build_commons_alcoholic_drinks(limit):
    """The commons_alcoholic_drinks pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(ALCOHOLIC_DRINKS, limit, "alcdrink", adults_only=True)


def build_commons_bar_glassware(limit):
    """The commons_bar_glassware pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BAR_GLASSWARE, limit, "barglass", adults_only=True)


def build_commons_brewing_winemaking(limit):
    """The commons_brewing_winemaking pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BREWING_WINEMAKING, limit, "brewwine", adults_only=True)


def build_commons_distilling(limit):
    """The commons_distilling pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(DISTILLING, limit, "distil", adults_only=True)


def build_commons_soft_drinks(limit):
    """The commons_soft_drinks pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(SOFT_DRINKS, limit, "softdrink")


# ----------------------------------------------------------------- Open Images: alcoholic drinks and the bar

BAR_DRINKS = [
    group("What alcoholic drinks are in this picture?",
          {"Red wine": "red wine", "White wine": "white wine", "Rosé": "rosé wine", "Sparkling wine": "sparkling wine",
           "Lager": "lager", "Stout": "stout", "Ale": "ale", "Wheat beer": "wheat beer", "Cider": "cider",
           "Mead": "mead", "Sake": "sake", "Vodka": "vodka", "Rum": "rum", "Gin": "gin", "Tequila": "tequila",
           "Brandy": "brandy", "Cognac": "cognac", "Bourbon whiskey": "bourbon", "Liqueur": "a liqueur",
           "Distilled beverage": "a spirit", "Martini": "a martini", "Margarita": "a margarita",
           "Mojito": "a mojito", "Sangria": "sangria", "Mulled wine": "mulled wine",
           "Alcoholic beverage": "an alcoholic drink"}, ALCOHOL_NOTE),
    group("What glasses or bar things are in this picture?",
          {"Beer glass": "a beer glass", "Pint glass": "a pint glass", "Beer stein": "a beer stein",
           "Champagne stemware": "champagne glasses", "Highball glass": "a highball glass",
           "Old fashioned glass": "an old fashioned glass", "Decanter": "a decanter", "Flask": "a flask",
           "Barware": "barware", "Shaker": "a shaker", "Cocktail garnish": "a cocktail garnish", "Cork": "a cork",
           "Wine bottle": "a wine bottle", "Wine rack": "a wine rack"}),
    group("How are drinks served or stored here?",
          {"Beer tap": "a beer tap", "Keg": "a keg", "Barrel": "a barrel", "Wine cellar": "a wine cellar"}),
    group("What kind of place is this?",
          {"Bar": "a bar", "Pub": "a pub", "Drinking establishment": "a bar or pub", "Brewery": "a brewery",
           "Winery": "a winery", "Vineyard": "a vineyard", "Liquor store": "a liquor store",
           "Wine tasting": "a wine tasting"}),
    group("What brewing or winemaking ingredients are in this picture?",
          {"Hops": "hops", "Malt": "malt", "Barley": "barley", "Yeast": "yeast", "Grapevine family": "grapevines"}),
]

SOFT = [
    group("What soft drinks are in this picture?",
          {"Cola": "cola", "Ginger ale": "ginger ale", "Root beer": "root beer", "Carbonated water": "sparkling water",
           "Mineral water": "mineral water", "Lemonade": "lemonade", "Iced tea": "iced tea",
           "Sports drink": "a sports drink", "Kombucha": "kombucha", "Non-alcoholic beverage": "a non-alcoholic drink",
           "Drink": "a drink"}),
    group("Is this a caffeinated drink?", {"Caffeinated drink": "a caffeinated drink"}, CAFFEINE_NOTE),
    group("What juices are in this picture?",
          {"Juice": "juice", "Orange juice": "orange juice", "Apple juice": "apple juice", "Grape juice": "grape juice",
           "Cranberry juice": "cranberry juice", "Grapefruit juice": "grapefruit juice",
           "Tomato juice": "tomato juice", "Vegetable juice": "vegetable juice", "Lemon juice": "lemon juice",
           "Lime juice": "lime juice", "Coconut water": "coconut water"}),
    group("What milky or blended drinks are in this picture?",
          {"Smoothie": "a smoothie", "Milkshake": "a milkshake", "Almond milk": "almond milk", "Soy milk": "soy milk",
           "Plant milk": "a plant milk", "Milk": "milk", "Chocolate milk": "chocolate milk",
           "Coffee milk": "coffee milk", "Hot chocolate": "hot chocolate"}),
    group("What coffee or tea drinks are in this picture?",
          {"Iced coffee": "iced coffee", "Latte": "a latte", "Cappuccino": "a cappuccino", "Espresso": "an espresso",
           "Frappé coffee": "a frappé coffee", "Tea": "tea"}),
    group("What drink mixes or syrups are in this picture?",
          {"Drink mix": "a drink mix", "Syrup": "a syrup", "Powdered milk": "powdered milk", "Ice cube": "ice cubes"}),
]


def without_children(entries, limit):
    """entries without any picture that has a child row (alcohol pictures never show a child): the picture and
    every row naming it (its twins carry "file": "pictures/<name>") are left out; at most limit pictures."""
    def picture_of(entry):
        """The picture file name an entry belongs to."""
        return entry[0] or entry[2].get("file", "").replace("pictures/", "", 1)
    child = {picture_of(e) for e in entries if e[2].get("child")}
    kept = [e for e in entries if picture_of(e) not in child]
    pictures = [e[0] for e in kept if e[0]][:limit]
    return [e for e in kept if picture_of(e) in set(pictures)]


def build_open_images_bar_drinks(limit):
    """open_images_bar_drinks (see the module docstring); photos with a child label are left out."""
    return without_children(build_oi_gap("open_images_bar_drinks", BAR_DRINKS, int(limit * 1.1) + 2, 9201), limit)


def build_open_images_soft_drinks(limit):
    """open_images_soft_drinks (see the module docstring)."""
    return build_oi_gap("open_images_soft_drinks", SOFT, limit, 9202)


# ----------------------------------------------------------------- Europeana: historic bottles and drink-making

EUROPEANA_DRINK_SEARCHES = {
    "wine bottle": re.compile(r"\bwine[- ]bottles?\b", re.I), "beer bottle": re.compile(r"\bbeer[- ]bottles?\b", re.I),
    "bottle of beer": re.compile(r"\bbottles? of beer\b", re.I), "decanter": re.compile(r"\bdecanters?\b", re.I),
    "tankard": re.compile(r"\btankards?\b", re.I), "wine glass": re.compile(r"\bwine[- ]glass(es)?\b", re.I),
    "wine press": re.compile(r"\bwine[- ]press(es)?\b", re.I), "cider press": re.compile(r"\bcider[- ]press", re.I),
    "brewing": re.compile(r"\bbrew(ing|ery|eries|house)\b", re.I),
    "distillery": re.compile(r"\bdistill?(ery|eries|ing|ation)\b|\bstills?\b", re.I),
}
DISTILL_WORDS = re.compile(r"\bdistill?(ery|eries|ing|ation)\b|\bstills?\b", re.I)


def europeana_drink_item(record, search, pattern):
    """(name, picture address, rows) for one Europeana record found by a drinks search, or None: English, CC0, the
    Public Domain Mark or CC BY, its own words naming what was searched for, and passing the content rules."""
    from medical_packs import tidy_record_text
    from documentary_packs import tidy, usable
    from gaps_collection_packs import EUROPEANA_FREE, marked_rows, ASK_DESCRIBE
    rights = " ".join(record.get("rights") or [])
    picture = (record.get("edmIsShownBy") or [""])[0]
    title = clean((record.get("title") or [""])[0])
    if not EUROPEANA_FREE.search(rights) or re.search(r"by-(sa|nc|nd)", rights) or not picture or not title \
            or (record.get("language") or []) != ["en"]:
        return None
    description = tidy_record_text(first_sentences(clean((record.get("dcDescription") or [""])[0]), 60))
    text = title if not description or description.lower() in title.lower() else f"{title.rstrip('.')}. {description}"
    if not pattern.search(text):
        return None
    answer = tidy(text)
    if not usable(answer):
        return None
    if DISTILL_WORDS.search(answer):
        answer = f"{DISTILLING_WARNING} {answer}"
    provider = clean((record.get("dataProvider") or ["Europeana"])[0])
    credit = f"{provider} via Europeana (search \"{search}\"), \"{title[:150]}\", {rights}, " \
             f"https://www.europeana.eu/item{record['id']}"
    rows = marked_rows([{"question": ASK_DESCRIBE, "answer": answer, "credit": credit}], title)
    if not rows:
        return None
    return "eudrink-" + re.sub(r"\W+", "_", record["id"]).strip("_")[:80] + ".jpg", picture, rows


def europeana_drink_items(want, s=None):
    """(name, picture address, rows) from the drinks searches, English records with free rights, each search taking
    turns; Europeana's public test key unless the build has its own (EUROPEANA_KEY)."""
    import os
    from museum_general_packs import get_json
    from gaps_collection_packs import EUROPEANA
    s = s or session()
    key = os.environ.get("EUROPEANA_KEY") or "api2demo"
    items, seen = [], set()
    for search, pattern in EUROPEANA_DRINK_SEARCHES.items():
        cursor, found = "*", 0
        while cursor and found < want and not build_packs.listing_out_of_time():
            time.sleep(0.5)
            data = get_json(s, EUROPEANA, params={"wskey": key, "query": search, "cursor": cursor,
                                                  "qf": ["TYPE:IMAGE", "LANGUAGE:en"], "reusability": "open",
                                                  "rows": 100, "profile": "rich"}) or {}
            for record in data.get("items") or []:
                got = europeana_drink_item(record, search, pattern)
                if got and got[0] not in seen:
                    seen.add(got[0])
                    items.append(got)
                    found += 1
            cursor = data.get("nextCursor")
        say(f"  Europeana \"{search}\": {found} usable")
    pass_random(5201).shuffle(items)
    return items[:want]


def build_europeana_drinks_history(limit):
    """The europeana_drinks_history pack (see the module docstring)."""
    from gaps_collection_packs import shared_finish
    return shared_finish("europeana_drinks_history", europeana_drink_items(int(limit * 1.2) + 2), limit, workers=4,
                         pause=0.2)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
DRINKS_PACKS = {
    "commons_alcoholic_drinks": (build_commons_alcoholic_drinks, COMMONS_LICENCE.format(
        what="wine, beer, spirit, cider, mead, sake and cocktail")),
    "commons_bar_glassware": (build_commons_bar_glassware, COMMONS_LICENCE.format(
        what="glassware, bar tool and drink serving")),
    "commons_brewing_winemaking": (build_commons_brewing_winemaking, COMMONS_LICENCE.format(
        what="brewing, winemaking and ingredient")),
    "commons_distilling": (build_commons_distilling, COMMONS_LICENCE.format(what="still and distillery")),
    "open_images_bar_drinks": (build_open_images_bar_drinks, OI_LICENCE),
    "europeana_drinks_history": (build_europeana_drinks_history,
                                 "Europeana (https://www.europeana.eu): records whose own rights are CC0, the Public "
                                 "Domain Mark or CC BY, each credited below."),
    "commons_soft_drinks": (build_commons_soft_drinks, COMMONS_LICENCE.format(
        what="soft drink, juice, water, coffee and tea drink, plant milk and syrup")),
    "open_images_soft_drinks": (build_open_images_soft_drinks, OI_LICENCE),
}
DRINKS_LIMITS = {
    "commons_alcoholic_drinks": 3000,      # 56 categories, an even share each
    "commons_bar_glassware": 1500,         # 23 categories
    "commons_brewing_winemaking": 1500,    # 21 categories
    "commons_distilling": 300,             # 3 categories, few open files
    "open_images_bar_drinks": 3000,        # 57 labels
    "europeana_drinks_history": 400,       # 10 searches, few English open records each
    "commons_soft_drinks": 1800,           # 36 categories
    "open_images_soft_drinks": 2500,       # 42 labels
}
# The alcohol packs and the other drink packs (kept apart so the alcohol packs can be left out on their own).
DRINKS_ALCOHOL_KEYS = ("commons_alcoholic_drinks", "commons_bar_glassware", "commons_brewing_winemaking",
                       "commons_distilling", "open_images_bar_drinks", "europeana_drinks_history")
DRINKS_SOFT_KEYS = ("commons_soft_drinks", "open_images_soft_drinks")
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
DRINKS_COMMONS_KEYS = ("commons_alcoholic_drinks", "commons_bar_glassware", "commons_brewing_winemaking",
                       "commons_distilling", "commons_soft_drinks")


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a drinks pack builder.")
    parser.add_argument("key", choices=sorted(DRINKS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = DRINKS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
