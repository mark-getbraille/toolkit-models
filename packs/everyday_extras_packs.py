"""Pack builders for EVERYDAY THINGS a blind person asks a picture describer about, starting with money. They are
used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name,
JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" where the source names one,
"child": true where the words of a picture name a child, and "facts" (the Commons category and file title it came
from). A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose
"file" names the same picture (food_packs.with_twins). The limit counts pictures.

Answers are fixed sentences written here from each source's own labels (a Commons category's name, the side and date
in a file's own title), never by an AI model. The money answers add the published facts of the US Mint, the US
Currency Education Program (uscurrency.gov) and the Bank of Canada about how a coin or note can be told by touch or
with low vision; those facts are about the denomination and series, and are said as such.

The packs (all open: CC0, public domain or CC BY, checked file by file at the source, November 2026):
  commons_money_sides   Wikimedia Commons, US coins by design (Lincoln cents, Jefferson and Buffalo nickels,
                        Roosevelt and Mercury dimes, Washington quarters and the state, park and women quarters,
                        Kennedy and Franklin halves, Sacagawea, Susan B. Anthony, Eisenhower and Presidential dollars),
                        US Federal Reserve Notes $1 to $100, and Canadian coins and banknotes by value. Only files whose
                        own title says which side they show (obverse, front, face, heads; reverse, back, tails) are
                        used. "What money is this?" (the value, the side and the date in the title), "What is on this
                        side?" (the design, where it is certain for that coin and date) and "How can someone tell
                        this by touch or with low vision?" (size and edge of the coin; for US bills that all are one
                        size with no raised marks, and the large numeral on the back of newer $5 to $100 bills; for
                        Canadian notes the Bank of Canada's six-dot tactile symbols, large high-contrast numbers and
                        colours).

BANKNOTE PICTURES AND THE LAW. US law (18 U.S.C. 504, 31 CFR 411.1) allows colour pictures of US paper money only when
one-sided and less than three-quarters or more than one and a half times the real size; Canada's Criminal Code (s. 457)
has a like rule, and the Bank of Canada asks written permission for ITS OWN banknote pictures (bankofcanada.ca terms,
section 2.1), so none of theirs are used. So banknote files showing both sides are left out (NOTE_BOTH), and every
banknote picture is made at most NOTE_SIDE pixels long (at a screen's 96 dots an inch a $20 bill then shows at under
three-quarters of its 6.14 inches). Coins have no such rule.

Not repeated (they exist): commons_us_money and commons_ca_money (the same Commons categories by value only, every file; this pack
takes the ones whose title names the side and adds the design and touch facts), banknotes, bd_taka, ghana_money.
The Smithsonian's National Numismatic Collection (CC0) was looked at: in the open-access bulk files only 2 of 5,434
of its records carry a picture, and api.si.edu refused automated requests (service_packs.py notes), so it is not used.

Safety (packs/SOURCE-RULES.md): no sexual content (NUDE, us_packs.NOT_SHOWN); every row whose words name a child is
marked "child". A free photo that has no answer here is simply not used.

    python packs/everyday_extras_packs.py commons_money_sides --limit 8      (prints a few rows: a quick check)
"""

import collections
import io
import json
import random
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, say, considered, listing_out_of_time
from food_packs import with_twins, count_pictures, commons_members
from home_packs import commons_fetch, file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count
from mechanical_packs import mech_entries, in_english, JUST_A_RECORD, NOT_A_CHILD
from us_packs import NOT_SHOWN, file_categories
from places import where

DESCRIBE_Q = "Describe this picture."
MONEY_Q = "What money is this?"
SIDE_Q = "What is on this side?"
TOUCH_Q = "How can someone tell this by touch or with low vision?"
USA, CANADA = "USA", "Canada"

# Files that are not pictures of the thing itself, whatever pack (each pack adds its own words).
NOT_A_PICTURE = re.compile(r"\b(logos?|icons?|emoji|clip ?art|maps?|videos?|audio|animations?|animated|patents?|"
                           r"\.(svg|gif|webm|ogg|ogv|pdf|tiff?|djvu|stl|mp3|wav))\b", re.I)


# ----------------------------------------------------------------- a small Commons engine

ONLY = ()              # a quick check (main --only): only the categories whose names hold one of these words


def spec(category, info=None, depth=0, place=""):
    """One Commons category of a pack: what it is (info, read by the pack's rows function), how deep to look (0: the
    category itself; 1: and its subcategories) and the place it names."""
    return {"category": category, "info": info, "depth": depth, "place": place}


def category_files(s, one, skip, most_subcategories=40):
    """[(file title, the category it came from)] of a spec, files and subcategories named by skip left out."""
    category = one["category"]
    found = {t: category for t in commons_members(s, category, "file") if not skip.search(t)}
    if one["depth"]:
        subs = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
        subs = [c for c in subs if not skip.search(c)]
        random.Random(category).shuffle(subs)
        for sub in subs[:most_subcategories]:
            if listing_out_of_time():
                break
            for t in commons_members(s, sub, "file"):
                if not skip.search(t):
                    found.setdefault(t, sub)
    return list(found.items())


def extras_commons(specs, limit, prefix, rows_for, skip=NOT_A_PICTURE, drawings=False):
    """[(file name, picture address, rows)] from Commons categories, taking turns so each gets an even share.
    rows_for(title, caption, categories, spec, sub) gives a file's rows (questions and answers) or []; a file with
    none is left out, and one with rows gets "Describe this picture." too when it has a real, respectful English
    caption. Every file's licence is checked by mech_entries (CC0, public domain or CC BY only)."""
    s, items, seen = session(), [], set()
    order = [one for one in specs if not ONLY or any(w.lower() in one["category"].lower() for w in ONLY)]
    random.Random(prefix).shuffle(order)
    share = max(3, -(-int(limit * 1.15) // max(1, len(order))))
    want = int(limit * 1.15) + 2
    queues = [[one, None] for one in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            if listing_out_of_time():
                say(f"  {prefix}: stopped looking at half the time limit")
                queues = []
                break
            one, files = q
            if files is None:
                try:
                    files = [(t, sub) for t, sub in category_files(s, one, skip) if t not in seen]
                except RuntimeError as e:      # Commons kept refusing: keep what was found and stop asking
                    say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                    queues = []
                    break
                random.Random(one["category"]).shuffle(files)
                say(f"Commons {one['category']}: {len(files)} files")
            batch, q[1] = files[:share * 2], files[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            subs = dict(batch)
            try:
                entries = mech_entries(s, [t for t, _ in batch], drawings=drawings)
                cats = file_categories(s, [e[0] for e in entries])
            except RuntimeError as e:
                say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                queues = []
                break
            got = 0
            for title, url, credit, text, _ in entries:
                if got >= share or title in seen:
                    continue
                words = NOT_A_CHILD.sub(" ", f"{title} {text} {' '.join(cats.get(title, []))}")
                if NUDE.search(words) or NOT_SHOWN.search(words):
                    considered(title, url, "its words are about nudity, underwear or swimwear")
                    continue
                bare = title.split(":", 1)[-1].rsplit(".", 1)[0]
                rows = rows_for(bare, text or "", cats.get(title, []), one, subs.get(title) or one["category"])
                if not rows:
                    considered(title, url, "no answer: its title and categories do not say what this pack asks")
                    continue
                place = where(one["place"], "origin") if one["place"] else {}
                facts = {"commons_category": subs.get(title) or one["category"], "commons_title": bare}
                rows = [dict(r, credit=credit, facts=facts, **place) for r in rows]
                text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
                if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
                    rows.append({"question": DESCRIBE_Q, "answer": text, "credit": credit, **place})
                seen.add(title)
                items.append((file_name(prefix, title), url, [mark_child(r, words) for r in rows]))
                got += 1
            if not q[1]:
                queues.remove(q)
    random.Random(prefix + "-order").shuffle(items)
    return items[:want]


def shrink(data, side):
    """JPEG bytes made at most side pixels on the long side."""
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img.thumbnail((side, side))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=90)
    return out.getvalue()


# ----------------------------------------------------------------- commons_money_sides

NOTE_SIDE = 400        # banknote pictures at most this many pixels long (18 U.S.C. 504; Criminal Code s. 457)
# A side named in a file title (camel case split first: "$20HawaiiBack" -> "$20 Hawaii Back").
FRONT = re.compile(r"\b(obverse|obv|front|face|avers|averse|avers[eo]|anverso|dritto|vorderseite|recto|heads)\b", re.I)
BACK = re.compile(r"\b(reverse|rev|back|revers|rovescio|reverso|r[uü]ckseite|verso|tails)\b", re.I)
# Coin files named "1964-USA-half-dollar-Kennedy-d" (d: obverse, r: reverse), as the National Numismatic Collection's
# photos on Commons are.
CODED_SIDE = re.compile(r"-(d|r)$")
NOTE_BOTH = re.compile(r"\b(both sides|front and back|obverse and reverse|face and back|recto verso|"
                       r"bothsides)\b", re.I)
# Titles that are about something else (a coin beside a part for scale, a sandwich price, a fake).
NOT_MONEY = re.compile(r"\b(scale|comparison|for size|size of|resistor|processor|chip|sparkfun|arduino|cartridge|"
                       r"shell|bullet|insect|footlong|sandwich|fake|replica|counterfeit|play money|prop money|"
                       r"fantasy|imitation|specimen|pattern|mule|error|errors|elongated|jewel\w*|necklace|pendant|"
                       r"cufflinks?|token|medal|art|painting|drawing)\b", re.I)
YEAR = re.compile(r"(?<!\d)(17[89]\d|18\d\d|19\d\d|20[0-2]\d)(?!\d)")
COIN_WORDS = re.compile(r"\b(coins?|cents?|penny|pennies|nickels?|dimes?|quarters?|half|dollars?|loonie|toonie|"
                        r"münze|moneda|monnaie|pièce|moneta|érme|érmé|munt|mynt)\b|¢|\b\d+ ?c\b", re.I)
NOTE_WORDS = re.compile(r"\b(dollars?|notes?|bills?|banknotes?|billets?|currency|bank of canada|federal reserve|"
                        r"series)\b|\$", re.I)

# The coin designs: (category, money key, design words that must not contradict the file, first year, last year,
# front, back). front and back are what that side shows; None where it changes too often to say.
US_COINS = [
    ("Lincoln Memorial cent", "us_cent", 1959, 2008, "Abraham Lincoln's head", "the Lincoln Memorial"),
    ("Lincoln Shield cent", "us_cent", 2010, 2030, "Abraham Lincoln's head", "a shield (the union shield)"),
    ("Lincoln Wheat cent", "us_cent", 1909, 1958, "Abraham Lincoln's head", "two ears of wheat"),
    ("Lincoln Bicentennial cent", "us_cent", 2009, 2009, "Abraham Lincoln's head",
     "one of four scenes from Lincoln's life"),
    ("Jefferson nickel", "us_nickel", 1938, 2030, "Thomas Jefferson's head", "Monticello, Jefferson's house"),
    ("Westward Journey nickels", "us_nickel", 2004, 2005, "Thomas Jefferson", "a Westward Journey design (the "
                                                                              "Lewis and Clark expedition)"),
    ("Buffalo nickels", "us_nickel", 1913, 1938, "the head of a Native American man", "an American bison"),
    ("Roosevelt dimes", "us_dime", 1946, 2030, "Franklin D. Roosevelt's head",
     "a torch between an olive branch and an oak branch"),
    ("Mercury dimes", "us_dime", 1916, 1945, "Liberty wearing a winged cap", "a bundle of rods (fasces) and an "
                                                                              "olive branch"),
    ("Obverses of Washington quarters", "us_quarter", 1932, 2030, "George Washington's head", None),
    ("Washington quarter", "us_quarter", 1932, 2030, "George Washington's head", None),
    ("50 State Quarters", "us_quarter", 1999, 2008, "George Washington's head", "a design for one of the states"),
    ("America the Beautiful Quarters", "us_quarter", 2010, 2021, "George Washington's head",
     "a national park or other national site"),
    ("American Women quarters", "us_quarter", 2022, 2025, "George Washington's head", "a famous American woman"),
    ("Kennedy half dollar", "us_half", 1964, 2030, "John F. Kennedy's head", None),
    ("Franklin half dollar", "us_half", 1948, 1963, "Benjamin Franklin's head", "the Liberty Bell"),
    ("Sacagawea dollar", "us_golden", 2000, 2030, "Sacagawea carrying her baby son", None),
    ("Presidential $1 Coin Program", "us_golden", 2007, 2020, "a president's head", "the Statue of Liberty"),
    ("Susan B. Anthony dollar", "us_sba", 1979, 1999, "Susan B. Anthony's head", "an eagle landing on the Moon"),
    ("Eisenhower dollar", "us_ike", 1971, 1978, "Dwight D. Eisenhower's head", None),
]
CA_COINS = [
    ("One cent coins of Canada", "ca_cent"), ("Nickel (Canadian coin)", "ca_nickel"),
    ("Ten cent coins of Canada", "ca_dime"), ("Twenty five cent coins of Canada", "ca_quarter"),
    ("Fifty-cent coins of Canada", "ca_fifty"), ("One dollar coins of Canada", "ca_dollar"),
    ("Two dollar coins of Canada", "ca_toonie"),
]
# What each coin is called, and how it feels (US Mint and Royal Canadian Mint specifications).
COIN_NAMES = {
    "us_cent": "a US one-cent coin (a penny)", "us_nickel": "a US five-cent coin (a nickel)",
    "us_dime": "a US ten-cent coin (a dime)", "us_quarter": "a US 25-cent coin (a quarter)",
    "us_half": "a US half-dollar coin (50 cents)", "us_golden": "a US one-dollar coin (a golden dollar)",
    "us_sba": "a US one-dollar coin (the Susan B. Anthony dollar)", "us_ike": "a US one-dollar coin (the "
                                                                             "Eisenhower dollar)",
    "ca_cent": "a Canadian one-cent coin (a penny)", "ca_nickel": "a Canadian five-cent coin (a nickel)",
    "ca_dime": "a Canadian ten-cent coin (a dime)", "ca_quarter": "a Canadian 25-cent coin (a quarter)",
    "ca_fifty": "a Canadian fifty-cent coin", "ca_dollar": "a Canadian one-dollar coin",
    "ca_toonie": "a Canadian two-dollar coin (a toonie)",
}
COIN_FEEL = {
    "us_cent": "A US cent is 19 mm (three-quarters of an inch) across, with a smooth edge.",
    "us_nickel": "A US nickel is 21 mm across, thicker than a cent or a dime, with a smooth edge.",
    "us_dime": "A US dime is the smallest US coin, 18 mm across, with a ridged (reeded) edge: that ridged edge "
               "tells it from a cent, which is about the same size but smooth.",
    "us_quarter": "A US quarter is 24 mm (nearly an inch) across, with a ridged (reeded) edge.",
    "us_half": "A US half dollar is large, 31 mm (about an inch and a quarter) across, with a ridged (reeded) edge.",
    "us_golden": "A golden dollar is 26.5 mm across and gold-coloured; its edge is smooth (Sacagawea dollars of 2000 "
                 "to 2008) or has lettering on it (later dollars and all Presidential dollars).",
    "us_sba": "The Susan B. Anthony dollar is 26.5 mm across, silver-coloured, with a ridged edge and an "
              "eleven-sided border inside the rim; it is easily taken for a quarter.",
    "us_ike": "The Eisenhower dollar is very large, 38 mm (an inch and a half) across, with a ridged edge.",
    "ca_cent": "A Canadian cent is 19 mm across with a smooth edge; Canada stopped making cents in 2012.",
    "ca_dime": "A Canadian dime is the smallest Canadian coin, 18 mm across, with a ridged (reeded) edge.",
    "ca_quarter": "A Canadian quarter is 24 mm (nearly an inch) across, with a ridged (reeded) edge.",
    "ca_fifty": "A Canadian fifty-cent coin is 27 mm across; few are seen in everyday use.",
    "ca_toonie": "The toonie is 28 mm across, the largest coin in everyday use in Canada, with two colours: a "
                 "silver-coloured ring around a gold-coloured centre.",
}
# The back of Canadian coins from 1937 (usual designs; special issues differ).
CA_BACKS = {"ca_cent": "two maple leaves", "ca_nickel": "a beaver", "ca_dime": "the schooner Bluenose",
            "ca_quarter": "a caribou's head", "ca_fifty": "the coat of arms of Canada", "ca_toonie": "a polar bear"}

DOLLAR_WORDS = {1: "one-dollar", 2: "two-dollar", 5: "five-dollar", 10: "ten-dollar", 20: "twenty-dollar",
                50: "fifty-dollar", 100: "hundred-dollar", 1000: "thousand-dollar"}
# US Federal Reserve Notes: (front, back) of the small notes from 1928 (the $1 FRN from 1963, the $2 FRN from 1976),
# and the first series with the large numeral on the back for people with low vision (uscurrency.gov).
US_NOTES = {1: ("George Washington", "the Great Seal of the United States (the pyramid and the eagle)", None),
            2: ("Thomas Jefferson", "the signing of the Declaration of Independence", None),
            5: ("Abraham Lincoln", "the Lincoln Memorial", 1999),
            10: ("Alexander Hamilton", "the US Treasury Building", 1999),
            20: ("Andrew Jackson", "the White House", 1996),
            50: ("Ulysses S. Grant", "the US Capitol", 1996),
            100: ("Benjamin Franklin", "Independence Hall", 1996)}
US_NOTE_TOUCH = ("Every US bill since 1929, whatever its value, is the same size (6.14 by 2.61 inches) and has no "
                 "raised marks, so bills cannot be told apart by touch; the US Currency Reader Program gives free "
                 "bill readers to people who are blind or have low vision.")
# The Bank of Canada's tactile feature: symbols of six raised dots (two columns of three), not braille.
CA_DOTS = {5: "one symbol", 10: "two symbols", 20: "three symbols", 50: "four symbols",
           100: "two symbols with a wider smooth space between them than on the $10"}
CA_COLOURS = {5: "blue", 10: "purple", 20: "green", 50: "red", 100: "brown"}


def split_camel(title):
    """ "$20HawaiiBack" -> "$20 Hawaii Back", and underscores as spaces."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", title.replace("_", " "))


def side_of(title, categories=(), coded=False):
    """ "front", "back", "both" or "" from a file's own title (and "Obverses of ..."/"Reverses of ..." categories):
    coded: also the "-d"/"-r" ending of coin photo names."""
    words = split_camel(title)
    if NOTE_BOTH.search(words):
        return "both"
    front, back = bool(FRONT.search(words)), bool(BACK.search(words))
    for c in categories:
        front |= c.lower().startswith("obverses of")
        back |= c.lower().startswith("reverses of")
    if coded and not (front or back):
        m = CODED_SIDE.search(title)
        front, back = bool(m and m.group(1) == "d"), bool(m and m.group(1) == "r")
    return "both" if front and back else "front" if front else "back" if back else ""


def year_of(title):
    """The one year in a title, or None (none, or two different ones)."""
    years = set(YEAR.findall(title))
    return int(years.pop()) if len(years) == 1 else None


def coin_rows(key, side, year, front=None, back=None, first=1700, last=2100):
    """The rows of one coin picture: what money, what is on the side shown (where certain), and how it feels."""
    name = COIN_NAMES[key]
    dated = f", dated {year}" if year else ""
    shows = {"front": "the front (heads side)", "back": "the back (tails side)", "both": "both sides"}[side]
    rows = [{"question": MONEY_Q, "answer": f"This is {shows} of {name}{dated}."}]
    if year and not first <= year <= last:
        front = back = None                    # a date outside the design's years: say nothing of the design
    said = []
    if side in ("front", "both") and front:
        said.append(f"The front shows {front}.")
    if side in ("back", "both") and back:
        said.append(f"The back shows {back}.")
    if said:
        rows.append({"question": SIDE_Q, "answer": " ".join(said)})
    feel = COIN_FEEL.get(key)
    if key == "ca_nickel":
        feel = ("A Canadian nickel is 21 mm across with a smooth edge" + (
            "; nickels of 1942 to 1962 like this one have twelve sides." if year and 1942 <= year <= 1962 else
            "; it is round, except those of 1942 to 1962, which have twelve sides." if not year else "."))
    elif key == "ca_dollar":
        feel = ("Since 1987 Canada's one-dollar coin is the loonie: 26.5 mm across, gold-coloured, with eleven sides."
                if not year or year >= 1987 else "This is one of the large one-dollar coins Canada made before the "
                                                 "gold-coloured eleven-sided loonie of 1987.")
    if feel:
        rows.append({"question": TOUCH_Q, "answer": feel})
    return rows


def us_coin_rows(title, categories, info):
    """Rows for a US coin file, or [] when its title does not name a side or is about something else."""
    _, key, first, last, front, back = info
    if not COIN_WORDS.search(title) and not re.search(r"\b(lincoln|jefferson|roosevelt|washington|kennedy|franklin|"
                                                      r"sacagawea|anthony|eisenhower|buffalo|mercury)\b", title, re.I):
        return []
    side = side_of(title, categories, coded=True)
    if not side or NOT_MONEY.search(title):
        return []
    year = year_of(title)
    if key == "us_nickel" and year in (2004, 2005) and "Westward" not in info[0]:
        back = None                            # the Westward Journey years: not Monticello
    if info[0] == "Kennedy half dollar" and year:
        back = ("Independence Hall (the bicentennial design)" if year == 1976 else
                "the presidential coat of arms (an eagle with a shield)")
    if key == "us_golden" and info[0] == "Sacagawea dollar" and year:
        back = "an eagle in flight" if year <= 2008 else "a Native American design (a different one each year)"
    return coin_rows(key, side, year, front, back, first, last)


def ca_coin_rows(title, categories, key):
    """Rows for a Canadian coin file: the front shows the monarch; the back's usual design only from 1937 on."""
    if not COIN_WORDS.search(title) and not re.search(r"canad", title, re.I):
        return []
    side = side_of(title, categories, coded=True)
    if not side or NOT_MONEY.search(title):
        return []
    year = year_of(title)
    back = CA_BACKS.get(key) if year and year >= 1937 else None
    if key == "ca_dollar" and year and year >= 1987:
        back = "a loon"
    if back and key in ("ca_nickel", "ca_quarter", "ca_dollar", "ca_toonie"):
        back = f"usually {back} (some years have special designs)"
    front = "the head of the King or Queen of the time" if year else None
    return coin_rows(key, side, year, front, back)


def note_value(category):
    """The value of a banknote category ("20 dollar Federal Reserve Note" -> 20)."""
    return int(re.match(r"\d+", category).group())


def us_note_rows(title, categories, value):
    """Rows for a US Federal Reserve Note file: one side only (a file of both sides is left out)."""
    side = side_of(title, categories)
    if side in ("", "both") or NOT_MONEY.search(title) or not NOTE_WORDS.search(title) and str(value) not in title:
        return []
    year = year_of(title)
    word = DOLLAR_WORDS[value]
    dated = f", series {year}" if year else ""
    shows = "the front" if side == "front" else "the back"
    rows = [{"question": MONEY_Q, "answer": f"This is {shows} of a US {word} bill (a Federal Reserve Note){dated}."}]
    portrait, vignette, big = US_NOTES[value]
    if not year or year >= 1928:
        what = f"a portrait of {portrait}" if side == "front" else vignette
        said = f"the {side} of the US {word} bill shows {what}."
        rows.append({"question": SIDE_Q, "answer": f"Since 1928, {said}" if not year else said[0].upper() + said[1:]})
    touch = US_NOTE_TOUCH if not year or year >= 1928 else "This is one of the larger US bills made before 1929."
    if big and (not year or year >= 1928):
        if year and year >= big:
            touch += f" This design has a large numeral {value} on the back to help people with low vision."
        elif not year:
            touch += (f" Designs from series {big} on have a large numeral {value} on the back to help people with "
                      f"low vision.")
    rows.append({"question": TOUCH_Q, "answer": touch})
    return rows


def ca_note_touch(value, year):
    """How a Canadian note can be told by touch or with low vision (the Bank of Canada's facts)."""
    if value in (1, 2, 1000):
        stop = {1: "replaced by the loonie coin in 1989", 2: "replaced by the toonie coin in 1996",
                1000: "stopped in 2000"}[value]
        return f"Canada no longer issues the ${value} note ({stop}); it has no tactile dots."
    features = (f"a tactile feature you can feel, {CA_DOTS[value]} of six raised dots in two columns of three (it "
                f"is not braille), large high-contrast numbers {value} on both sides, and the colour "
                f"{CA_COLOURS[value]}")
    if year and year >= 2001:
        return f"This note has {features}."
    if year:
        return (f"This older note has no tactile dots. Canadian ${value} notes in use today (paper from 2001, "
                f"polymer from 2011) have {features}.")
    return f"Canadian ${value} notes in use today (paper from 2001, polymer from 2011) have {features}."


def ca_note_rows(title, categories, value):
    """Rows for a Canadian banknote file: one side only."""
    side = side_of(title, categories)
    if side in ("", "both") or NOT_MONEY.search(title) or not NOTE_WORDS.search(title) and str(value) not in title:
        return []
    year = year_of(title)
    dated = f" from {year}" if year else ""
    shows = "the front (face)" if side == "front" else "the back"
    return [{"question": MONEY_Q, "answer": f"This is {shows} of a Canadian {DOLLAR_WORDS[value]} bill (a "
                                            f"{value}-dollar banknote){dated}."},
            {"question": TOUCH_Q, "answer": ca_note_touch(value, year)}]


def money_specs():
    """The commons_money_sides categories."""
    specs = [spec(c[0], ("us_coin", c), 0, USA) for c in US_COINS]
    specs += [spec(c, ("ca_coin", key), 0, CANADA) for c, key in CA_COINS]
    specs += [spec(f"{v} dollar Federal Reserve Note", ("us_note", v), 0, USA) for v in US_NOTES]
    specs += [spec(f"{v} Canadian dollar banknotes", ("ca_note", v), 0, CANADA) for v in DOLLAR_WORDS]
    return specs


def money_rows(title, caption, categories, one, sub):
    """The rows of one money file by its spec's kind."""
    kind, info = one["info"]
    if kind == "us_coin":
        return us_coin_rows(title, categories, info)
    if kind == "ca_coin":
        return ca_coin_rows(title, categories, info)
    if kind == "us_note":
        return us_note_rows(title, categories, info)
    return ca_note_rows(title, categories, info)


def is_note(rows):
    """True for the rows of a banknote picture."""
    return any(r["question"] == MONEY_Q and " bill " in r["answer"] for r in rows)


def build_commons_money_sides(limit):
    """The Commons US and Canadian money by side pack; banknote pictures made at most NOTE_SIDE pixels long."""
    items = extras_commons(money_specs(), limit, "money", money_rows)
    fetched = commons_fetch(items)
    fetched = [(name, shrink(data, NOTE_SIDE) if is_note(rows) else data, rows) for name, data, rows in fetched]
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- the packs

MONEY_FACTS = ("Touch and low-vision facts: US Mint coin specifications; U.S. Currency Education Program, "
               "https://www.uscurrency.gov (US government work); Bank of Canada, Resources for the blind and partially "
               "sighted, https://www.bankofcanada.ca/banknotes/audience-specific-resources/blind-and-partially-"
               "sighted/ (reproduced with attribution under the Bank of Canada's terms; changes: shortened and "
               "reworded). No banknote picture comes from the Bank of Canada.")
COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
EVERYDAY_EXTRAS_PACKS = {
    "commons_money_sides": (build_commons_money_sides, COMMONS_CREDIT.format(
        what="categories of US coins by design, US Federal Reserve Notes and Canadian coins and banknotes by value "
             "(only files whose title names the side; US coin and currency designs are US government work; "
             "banknote pictures one-sided and made small, as 18 U.S.C. 504 and Canada's Criminal Code s. 457 "
             "require)") + " " + MONEY_FACTS),
}

# The packs that show people (worn clothes, players, instruments being played): never used for picture-making (the
# kit's PEOPLE_AND_BODILY_PACK_KEYS).
PEOPLE_PACKS = ()

# How many pictures a full build takes from each (Commons answers about one picture a second).
EVERYDAY_EXTRAS_LIMITS = {
    "commons_money_sides": 700,   # 49 categories, about 2,100 files, about a third with the side in the title
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one everyday extras pack builder.")
    parser.add_argument("key", choices=sorted(EVERYDAY_EXTRAS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--only", action="append", default=[],
                        help="look only at the categories whose names hold this word (may be given again)")
    args = parser.parse_args(argv)
    global ONLY
    ONLY = tuple(args.only)
    entries = EVERYDAY_EXTRAS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    questions = collections.Counter(row["question"] for _, _, row in entries)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        "questions: " + ", ".join(f"{q} {n}" for q, n in questions.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
