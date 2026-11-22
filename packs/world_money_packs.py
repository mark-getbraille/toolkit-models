"""Picture packs for FOREIGN BANKNOTES AND COINS (the owner's request of 2026-11-22): the money of Japan, Mexico,
the United Kingdom, China, India, Australia, the euro countries before the euro (Germany, France, Italy, Spain) and
other common countries, for travel, sorting and collections. Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more
than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit
counts pictures.

THE REPRODUCTION RULES, AND WHY ONLY OLD MONEY IS TAKEN FROM COMMONS. Many central banks restrict pictures of their
money beyond copyright: the Reserve Bank of Australia consents to electronic banknote images only below
three-quarters size, at 72 dpi or less, with every copy destroyed after use; the European Central Bank's rules
(Decision ECB/2013/10) set sizes and resolutions; the Bank of Canada asks for written permission for its own
notes; the Bank of England, the Bank of Japan, the Banco de Mexico, the People's Bank of China and the Reserve Bank
of India have their own reproduction rules, not checked for this use; and modern coins are often the state's
copyright (Crown copyright in the United Kingdom and Australia). A training collection kept and shared for years
cannot meet "destroy every copy", and the other rules are unclear for this use. So, as the owner asked ("where
reproduction rules are unclear, leave it out and record why"), the Commons pack takes ONLY money whose own file
title gives a date of 1930 or earlier (OLD_UNTIL): money that old is in the US public domain by age and is not the
current money those rules protect. The modern notes and coins of each country are recorded as left
out in the kit's world_money_sources.py (WORLD_MONEY_NOT_INCLUDED). US money is already in the money packs
(commons_us_money, commons_money_sides) and Canada's in commons_ca_money and commons_money_sides.

Even so, banknote files showing both sides are left out and every banknote picture is made at most NOTE_SIDE pixels
long (everyday_extras_packs' rule for US and Canadian notes), and the Open Images money photos too.

Answers name the country, the denomination and the side ONLY as the source says: the country from the Commons
category ("Coins of Japan"), the denomination only from a subcategory that names it ("1 yen coins"), the side and
the date only from the file's own title (obverse, front, reverse, back ...; the Smithsonian's photos end in -d for
the front and -r for the back). How a country's current notes can be told apart by touch (the euro's raised lines,
Australia's raised bumps and lengths, Canada's raised dots) is in the reference library's world-money book, from the
central banks' own pages.

The packs (WORLD_MONEY_PACKS):
  commons_world_money   Wikimedia Commons (CC0, public domain or CC BY files only), old coins and banknotes (1930
                        or earlier) of Japan, Mexico, the United Kingdom, China, India, Australia, Switzerland, South
                        Korea, Brazil, Hong Kong, Sweden, Norway, Denmark, Poland, Turkey, the Philippines,
                        Thailand, Russia, Germany, France, Italy and Spain, and of the Smithsonian's National
                        Numismatic Collection (CC0 photos on Commons).
  met_world_coins       The Metropolitan Museum of Art (CC0): coins (tetradrachms, denarii, staters, dinars ...)
                        named so in the object's own record, answered from the record.
  open_images_money     Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                        currency, cash, money and money handling, dollars, nickels, dimes, Japanese yen, coin
                        purses and piggy banks, made small. No label is asked twice (packs/test_gaps_pictures.py).

Not repeated: commons_us_money, commons_ca_money, commons_money_sides, banknotes (Indian and Thai banknotes, CC BY),
bd_taka, ghana_money, synthetic_bills, and the Open Images labels other packs ask (Banknote, Coin, Wallet).

    python packs/world_money_packs.py commons_world_money --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from everyday_extras_packs import (spec, extras_commons, side_of, year_of, shrink, NOTE_SIDE, NOT_MONEY, MONEY_Q,
                                   NOTE_BOTH)

OLD_UNTIL = 1930           # only money whose file title gives a date up to this year (see the module docstring)

# (Commons category, the country as the answer names it).
COUNTRIES = [("Japan", "Japan"), ("Mexico", "Mexico"), ("the United Kingdom", "the United Kingdom"),
             ("India", "India"), ("Australia", "Australia"), ("Switzerland", "Switzerland"),
             ("South Korea", "South Korea"), ("Brazil", "Brazil"), ("Hong Kong", "Hong Kong"), ("Sweden", "Sweden"),
             ("Norway", "Norway"), ("Denmark", "Denmark"), ("Poland", "Poland"), ("Turkey", "Turkey"),
             ("the Philippines", "the Philippines"), ("Thailand", "Thailand"), ("Russia", "Russia"),
             ("Germany", "Germany"), ("France", "France")]
COINS_ONLY = [("Italy", "Italy"), ("Spain", "Spain")]
NNC = "National Numismatic Collection"
# A subcategory that names a denomination: "1 yen coins", "10 sen coins (Japan)", "5 Mark banknotes".
DENOMINATION = re.compile(r"^(\d[\d,.]*\s?[A-Za-zÀ-ÿ]+(?: [a-z]+)?)\s(coins?|banknotes?|notes?)\b")
COIN_WORD = re.compile(r"\b(coins?|münzen?|monedas?|monnaies?|pièces?|monete|moneta|mynt|munt|yen|sen|rin|"
                       r"pence|penny|shillings?|florins?|crowns?|sovereigns?|farthings?|rupees?|annas?|pice|"
                       r"pesos?|centavos?|reales?|francs?|centimes?|rappen|marks?|pfennigs?|kroner?|kronor|öre|øre|"
                       r"złot\w*|groszy|kuru[sş]|para|kopeks?|rubles?|roubles?|lire|centesimi|pesetas?|céntimos?|"
                       r"won|baht|satang|cents?|dollars?|obverse|reverse)\b", re.I)


def money_specs():
    """The commons_world_money categories: each country's coins and banknotes (with their subcategories) and the
    National Numismatic Collection."""
    specs = []
    for name, country in COUNTRIES:
        specs.append(spec(f"Coins of {name}", ("coin", country), 1))
        specs.append(spec(f"Banknotes of {name}", ("note", country), 1))
    specs.append(spec("Coins of the People's Republic of China", ("coin", "China"), 1))
    specs.append(spec("Banknotes of the People's Republic of China", ("note", "China"), 1))
    for name, country in COINS_ONLY:
        specs.append(spec(f"Coins of {name}", ("coin", country), 1))
    specs.append(spec(NNC, ("coin", ""), 1))
    return specs


def denomination(sub):
    """ "1 yen" from a subcategory named "1 yen coins" ("" when the name gives none)."""
    m = DENOMINATION.match(sub or "")
    return m.group(1) if m else ""


def world_money_rows(title, caption, categories, one, sub):
    """The rows of one money file: [] unless its title gives one date of OLD_UNTIL or earlier and is about money; a
    banknote file must show one side. "What money is this?" names the side, denomination and country as the title
    and categories say."""
    kind, country = one["info"]
    year = year_of(title)
    if not year or year > OLD_UNTIL or NOT_MONEY.search(title):
        return []
    side = side_of(title, categories, coded=True)
    if kind == "note" and (side == "both" or NOTE_BOTH.search(title)):
        return []
    if kind == "coin" and not country and not COIN_WORD.search(title) and not side:
        return []
    shows = {"front": "the front (obverse) of ", "back": "the back (reverse) of ", "both": "both sides of ",
             "": ""}[side]
    word = "coin" if kind == "coin" else "banknote"
    den = denomination(sub)
    what = f"{den} {word}" if den else word
    article = "an" if what[0].lower() in "aeiou8" or what.startswith(("11 ", "18 ")) else "a"
    where = f" of {country}" if country else " from the Smithsonian's National Numismatic Collection"
    answer = f"This is {shows}{article} {what}{where}, dated {year}."
    return [{"question": MONEY_Q, "answer": answer[0].upper() + answer[1:]}]


def is_note(rows):
    """True for the rows of a banknote picture."""
    return any(r["question"] == MONEY_Q and " banknote " in r["answer"] for r in rows)


def build_commons_world_money(limit):
    """The commons_world_money pack: old money only; banknote pictures made at most NOTE_SIDE pixels long."""
    from food_packs import with_twins
    from home_packs import commons_fetch
    items = extras_commons(money_specs(), limit, "worldmoney", world_money_rows)
    fetched = commons_fetch(items)
    fetched = [(name, shrink(data, NOTE_SIDE) if data and is_note(rows) else data, rows)
               for name, data, rows in fetched]
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- the Met (CC0)

MET_SEARCHES = ("coin", "tetradrachm", "denarius", "stater", "dinar", "solidus")
MET_WORDS = re.compile(r"\b(coins?|tetradrachms?|didrachms?|drachms?|denarii|denarius|staters?|dinars?|dirhams?|"
                       r"solidus|solidi|aurei|aureus|obols?|sestertius|ducats?|florins?|thalers?)\b", re.I)


def met_themed(o):
    """True when a Met object belongs to met_world_coins (museum_general_packs leaves it to this pack)."""
    return bool(MET_WORDS.search(o.get("objectName") or ""))


def build_met_world_coins(limit):
    """The met_world_coins pack (see the module docstring)."""
    from archive_packs import finish_marked
    from personal_care_packs import met_search_items
    items = met_search_items(MET_SEARCHES, met_themed, int(limit * 1.2) + 2, "met-coins")
    return finish_marked("met_world_coins", items, limit, workers=4, pause=0.2)


# ----------------------------------------------------------------- Open Images

MONEY_OI = [
    group("What money is in this picture?",
          {"Currency": "money (currency)", "Money": "money", "Cash": "cash", "Dollar": "dollars",
           "Japanese yen": "Japanese yen", "Nickel": "a nickel", "Dime": "a dime"}),
    group("Is someone handling money in this picture?", {"Money handling": "someone handling money"}),
    group("What is money kept in here?", {"Coin purse": "a coin purse", "Piggy bank": "a piggy bank"}),
]


def build_open_images_money(limit):
    """open_images_money (see the module docstring): every picture made at most NOTE_SIDE pixels long."""
    entries = build_oi_gap("open_images_money", MONEY_OI, limit, 9431)
    return [(name, shrink(data, NOTE_SIDE) if data else data, row) for name, data, row in entries]


# ----------------------------------------------------------------- the packs

WORLD_MONEY_PACKS = {
    "commons_world_money": (build_commons_world_money,
                            "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY "
                            "(credited below) of the coin and banknote categories of 21 countries and of the "
                            "Smithsonian's National Numismatic Collection; only money dated 1930 or earlier (central "
                            "banks restrict pictures of current money), banknotes one side and small."),
    "met_world_coins": (build_met_world_coins,
                        "The Metropolitan Museum of Art, Open Access (CC0, https://www.metmuseum.org/about-the-met/"
                        "policies-and-documents/open-access): public-domain coins, each credited below."),
    "open_images_money": (build_open_images_money,
                          "Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels "
                          "CC BY 4.0; each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked "
                          "photo by photo), photographer credited below; pictures made small."),
}
WORLD_MONEY_LIMITS = {
    "commons_world_money": 1500,   # 43 categories with their subcategories; old money only
    "met_world_coins": 800,        # the Met's coins
    "open_images_money": 1500,     # 10 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
WORLD_MONEY_COMMONS_KEYS = ("commons_world_money",)
# The Commons categories of the pack (for the self-test).
WORLD_MONEY_CATEGORIES = [one["category"] for one in money_specs()]


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a world money pack builder.")
    parser.add_argument("key", choices=sorted(WORLD_MONEY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = WORLD_MONEY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
