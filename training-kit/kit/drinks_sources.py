"""DRINKS for the Picture Model Training Kit: the collections that cannot be ready-made packs because of their
licence, and the drink sources that were looked at and left out, with the reason. The open ones are packs:
packs/drinks_packs.py (Commons alcoholic drinks, glassware and bar things, brewing and winemaking, distilling and soft
drinks; Open Images bar drinks and soft drinks; Europeana historic bottles and drink-making).

The alcohol collections and the other drink collections have separate keys, so the alcohol ones can be left out on
their own (the soft drinks are in the kit's food topic; the alcohol ones in no topic). Answers say only what the Commons category or the file's own
caption says; no alcohol content or caffeine amount is ever guessed. Alcohol answers end with ALCOHOL_NOTE, energy
drink answers with CAFFEINE_NOTE, and still answers START with DISTILLING_WARNING (the same words as the packs).

As in gaps_sources.py, nothing here is re-shared by the kit's makers: the collections are downloaded by the kit on
the user's own computer, straight from Wikimedia Commons, only when the user ticks the share-alike choice. Every
licence was checked at its source in November 2026.

The collections (DRINKS_SOURCES), share-alike:
  drinks_alcohol_commons_sa  Commons files under CC BY-SA or GFDL of the alcohol packs' main categories (wine, beer,
                             spirits, cocktails, glassware, brewing, winemaking, stills). Never for picture-making.
  drinks_soft_commons_sa     Commons files under CC BY-SA or GFDL of the soft drink pack's categories (soft drinks,
                             energy drinks, juices, waters, iced tea and coffee, plant milks, smoothies, syrups).

Looked at and not included: DRINKS_NOT_INCLUDED (with the reason).

    python -c "import sources, drinks_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source

ALCOHOL_NOTE = "Contains alcohol. Not for people under the legal drinking age, during pregnancy, or before driving."
CAFFEINE_NOTE = ("High in caffeine; not recommended for children, during pregnancy, or for people sensitive to "
                 "caffeine.")
DISTILLING_WARNING = ("Legal and safety notes first: in the US, distilling spirits at home is illegal without federal "
                      "permits, even for personal use (26 U.S.C. 5601), unlike home brewing and winemaking, which "
                      "federal law allows for adults within limits; laws differ by state and country (New Zealand, "
                      "for example, allows home distilling). Distilling carries real risks: methanol poisoning from "
                      "improper cuts, fire and explosion from ethanol vapour, and pressure.")


def drink(category, thing, note=ALCOHOL_NOTE, deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "It shows <thing>." and the note."""
    return (category, "What drink is shown here?", f"It shows {thing}." + (f" {note}" if note else ""), deeper)


def thing(category, words, note="", deeper=True):
    """(category, question, answer, deeper) for a thing: "This is <words>." and the note."""
    return (category, "What is this?", f"This is {words}." + (f" {note}" if note else ""), deeper)


DRINKS_ALCOHOL_SA = [
    drink("Wine bottles", "a bottle of wine"), drink("Red wine", "red wine"), drink("White wine", "white wine"),
    drink("Rosé wine", "rosé wine, a pink wine"), drink("Sparkling wine", "sparkling wine, a wine with bubbles"),
    drink("Beer bottles", "a bottle of beer"), drink("Beer cans", "a can of beer"),
    drink("Glasses of beer", "a glass of beer"), drink("Whisky", "whisky, a spirit distilled from grain"),
    drink("Gin", "gin, a spirit flavoured with juniper"), drink("Rum", "rum, a spirit made from sugar cane"),
    drink("Tequila", "tequila, a Mexican spirit made from blue agave"), drink("Sake", "sake, a Japanese rice wine"),
    drink("Cider", "cider, a drink made from fermented apples"), drink("Cocktails", "a cocktail, a mixed drink"),
    thing("Wine glasses", "a wine glass"), thing("Beer glasses", "a beer glass"),
    thing("Beer taps", "a beer tap, for pouring draught beer"), thing("Wine barrels", "a wine barrel"),
    thing("Homebrewing", "home brewing: making beer at home"), thing("Hops", "hops, the flowers that give beer its "
                                                                         "bitterness and aroma"),
    thing("Wine presses", "a wine press"), thing("Vineyards", "a vineyard"),
    ("Pot stills", "What is this?", f"{DISTILLING_WARNING} This is a pot still, a copper still for making spirits "
                                    "such as whisky.", True),
]
DRINKS_SOFT_SA = [
    drink("Soft drink cans", "a can of soft drink", ""), drink("Soft drink bottles", "a bottle of soft drink", ""),
    drink("Energy drinks", "an energy drink", CAFFEINE_NOTE), drink("Fruit juices", "fruit juice", ""),
    drink("Orange juice", "orange juice", ""), drink("Bottled water", "bottled water", ""),
    drink("Iced tea", "iced tea", ""), drink("Iced coffee", "iced coffee", ""),
    drink("Kombucha", "kombucha, a fermented tea drink", ""), drink("Soy milk", "soy milk", ""),
    drink("Smoothies", "a smoothie", ""), drink("Milkshakes", "a milkshake", ""), drink("Lemonade", "lemonade", ""),
    drink("Syrups", "a syrup", ""), drink("Mocktails", "a mocktail, a mixed drink without alcohol", ""),
]


def prepare_drinks_alcohol_commons_sa(source, data_dir, work, cap):
    """Commons alcohol, glassware, brewing and still categories, files under CC BY-SA or GFDL; no files naming a
    child."""
    items = commons_sa_items(DRINKS_ALCOHOL_SA, cap, source.test, "alcohol-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_drinks_soft_commons_sa(source, data_dir, work, cap):
    """Commons soft drink, juice, water and plant milk categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(DRINKS_SOFT_SA, cap, source.test, "softdrink-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
DRINKS_SOURCES = [
    Source("drinks_alcohol_commons_sa", "Wikimedia Commons: wine, beer, spirits, cocktails, glassware, brewing, "
                                        "winemaking and stills, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1200, 10, prepare_drinks_alcohol_commons_sa, "about 280 MB of pictures", terms=SA_TERMS,
           terms_summary=SA_SUMMARY),
    Source("drinks_soft_commons_sa", "Wikimedia Commons: soft drinks, energy drinks, juices, waters, iced tea and "
                                     "coffee, plant milks, smoothies and syrups, files under CC BY-SA or GFDL "
                                     "(share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 800, 10, prepare_drinks_soft_commons_sa, "about 180 MB of pictures", terms=SA_TERMS,
           terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the soft drinks (products), never alcohol.
DRINKS_PICTURE_MAKING_OK = {"drinks_soft_commons_sa"}
# The alcohol collections and the others (so a training can leave the alcohol ones out on their own).
DRINKS_ALCOHOL_KIT_KEYS = ("drinks_alcohol_commons_sa",)
DRINKS_SOFT_KIT_KEYS = ("drinks_soft_commons_sa",)

DRINKS_NOT_INCLUDED = {
    "Open Food Facts (alcoholic beverages and every other drink category)":
        "its photos are CC BY-SA and its data ODbL, but its robots.txt (world, static and images.openfoodfacts.org, "
        "checked 2026-11-21) shuts out AI crawlers by name (GPTBot, anthropic-ai, ClaudeBot: 'Disallow: /'), "
        "disallows /api to every robot, and search.openfoodfacts.org disallows every robot. Under the owner's rule "
        "(AI-crawler blocks are obeyed) its websites are not read. Its bulk-reuse routes (the product database on "
        "Hugging Face and the photos on AWS Open Data, off_dump.py) are not blocked and now feed the kit's Open Food "
        "Facts entries (openfoodfacts, openfoodfacts_labels, openfacts_us, openfacts_ca, openfacts_supplements); a "
        "drinks entry could be added the same way later. The Open Beauty, Products and Pet Food Facts entries are "
        "not built (no open route for their photos).",
    "US TTB COLAs Online public registry (approved label images)":
        "ttbonline.gov refused this machine's connections on 2026-11-21, so its robots.txt and terms could not be "
        "checked; it has no official API or bulk download, and the label images are the companies' own artwork "
        "(personal use at most). Not read.",
    "Amazon Berkeley Objects grocery drinks":
        "already in abo_packaged_goods (coffee, tea, juice, water, flavoured drinks, plant milks, wine and spirits "
        "by their listings); not repeated.",
    "Open Images drink labels already asked elsewhere (Cocktail, Beer, Wine, Whisky, Champagne, Shot glass, Wine "
    "glass, Beer bottle, Bottle, Soft drink, Energy drink, Bottled water, Drinking straw, cans and bottles)":
        "asked by open_images_food_more, open_images_packaged_goods and the home packs; never asked twice.",
    "Open Images people labels (Bartender, Sommelier, Brewmaster, Barista, Beer pong)":
        "they judge people by role or show drinking games; left out.",
    "Roboflow wine label sets":
        "Roboflow Universe's robots.txt disallows the dataset download pages (see gaps_sources.py).",
    "Museum CC0 collections (the Met, Art Institute of Chicago, Cleveland)":
        "their historic bottles, decanters and drinking vessels are already reachable through met_collection, "
        "aic_collection and cleveland_collection; Europeana's open records give the historic drinks pack.",
    "USDA ARS image gallery and extension service photos":
        "not read in this pass: the ARS gallery has no listing a program can read by subject that was confirmed, "
        "and extension photos are each under their own university's copyright (no open licence confirmed).",
    "Commons categories that do not exist under the names tried (Lager, India pale ale, Spirit safes, "
    "Rickhouses, Column stills, Alembics, Plant milks, Non-alcoholic beer, Mineral water bottles)":
        "the packs use the categories that exist and hold files (checked 2026-11-21).",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try a drinks share-alike collection.")
    parser.add_argument("key", choices=[s.key for s in DRINKS_SOURCES])
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in DRINKS_SOURCES if s.key == args.key)
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="drinks-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
