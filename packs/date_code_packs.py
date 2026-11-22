"""A picture pack for DATE CODES ON PACKAGING: best-before, use-by and expiry dates, lot and batch numbers and date
codes. Used by build_packs.py in the same way as its own PACKS: build_<key>(limit) returns [(file name, JPEG bytes
or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row) rows
naming the same picture. The limit counts pictures.

The owner's request of 2026-11-21. A date is said ONLY where the file's own words give it right after the words that
name it ("Best before 03/2021", "expiry date: 12 May 2019"): "What is the best-before date on this package?" -> "The
best-before date shown is 03/2021." Otherwise the answer says only what kind of mark it is ("It shows a best-before
date."), from the words of the file. No date is ever read from the picture by a program.

The pack:
  commons_date_codes  Wikimedia Commons (CC0, public domain or CC BY files only): the category "Expiration dates" and
                      Commons' own search for "best before", "use by", "expiry date",
                      "expiration date", "best by", "lot number", "batch number" and "date code" (files only),
                      each file kept only when its own title or words name one of these marks (and no passport,
                      card, licence, ticket or other document; only files whose words name a pack or product,
                      and no photos of people checking shelves).

Already in the kit, not repeated: food_packaging (big_sources.py: Food Packaging OCR, the use-by date of about 350
packs), and food_packs.py's Commons food pack ("Expiration dates": "It shows an expiry date"; this pack adds the
date itself where the file says it, and the other marks). What was looked at and left out (ExpDate, whose Google
Drive download robots may not fetch; Open Food Facts, whose dates are not tied to a photo) is in the kit's
picture_reading_sources.py.

    python packs/date_code_packs.py commons_date_codes --limit 6      (prints a few rows: a quick check)
"""

import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import say
from described_commons import build_described, file_words, own_caption_row

ASK_MARK = "What does this label show?"
MONTH = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sept?(?:ember)?|"
         r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?")
# A date as packs print it: 12/05/2019, 05.2019, 2019-05-12, 12 MAY 2019, MAY 2019, 12 MAY 19.
DATE = (rf"(?:\d{{1,2}}[./-]\d{{1,2}}[./-]\d{{2,4}}|\d{{1,2}}[./-]\d{{4}}|\d{{4}}-\d{{1,2}}-\d{{1,2}}|"
        rf"(?:\d{{1,2}}\s*)?{MONTH}\s*\d{{2,4}}|\d{{1,2}}\s*{MONTH})")
# (name for the answer, the question, the words that name the mark), the most specific first.
MARKS = [
    ("best-before date", "What is the best-before date on this package?",
     r"best[\s-]*before|\bBBE\b|mindestens haltbar bis"),
    ("best-by date", "What is the best-by date on this package?",
     r"best-by|best[\s-]*(?:if[\s-]*used[\s-]*)?by(?=\s*(?:date|:|\d))"),
    ("use-by date", "What is the use-by date on this package?", r"use-by|use[\s-]*by(?=\s*(?:date|:|\d))"),
    ("expiry date", "What is the expiry date on this package?",
     r"expiry|expiration\s*date|expir(?:es|ation)(?=\s*(?:on|:|\d))|\bEXP(?=\s*[:.]?\s*\d)"),
    ("sell-by date", "What is the sell-by date on this package?",
     r"sell-by|sell[\s-]*by(?=\s*(?:date|:|\d))|display[\s-]*until"),
    ("lot number", "What is the lot number on this package?", r"\blot\s*(?:number|no\.?|code|:)"),
    ("batch number", "What is the batch number on this package?", r"\bbatch\s*(?:number|no\.?|code|:)"),
    ("date code", "What does the date code on this package say?", r"date[\s-]*codes?"),
]
# Documents and cards have expiry dates too (and are private): only packaging is wanted here.
NOT_PACKAGING = re.compile(r"\b(passports?|credit cards?|debit cards?|bank cards?|licen[cs]es?|ID cards?|identity|"
                           r"visas?|certificates?|tickets?|permits?|domain names?|patents?|copyrights?|"
                           r"software|certificate|SSL|subscriptions?|membership)\b", re.I)
# The file must be about a pack or a product's label, not a person checking shelves or a chip's date code.
PACKAGING = re.compile(r"\b(packag\w*|packs?|labels?|cartons?|cans?|tins?|bottles?|jars?|boxe?s?|wrappers?|"
                       r"bags?|tubs?|pots?|sachets?|blister\w*|containers?|food|milk|yog(h)?urt|cheese|meat|bread|"
                       r"medicines?|drugs?|tablets?|pills?|vaccines?|cosmetics?|groceries|grocery|products?)\b", re.I)
PEOPLE_AT_WORK = re.compile(r"\b(check(s|ing|ed)?|inspect\w*|sgt|sergeant|airman|airmen|sailors?|soldiers?|"
                            r"specialists?|technicians?|staff|volunteers?|workers?|employees?|codex|manuscripts?|"
                            r"auction\w*|circuits?|chips?|IC)\b", re.I)
CODE = r"[A-Z0-9][A-Z0-9 ./-]{1,14}[A-Z0-9]"


def mark_of(words):
    """The first mark (name, question, pattern) whose words appear in words, or None."""
    for name, question, pattern in MARKS:
        if re.search(pattern, words, re.I):
            return name, question, pattern
    return None


def stated_value(text, name, pattern):
    """The date (or, for a lot or batch number, the code) that the text gives right after the mark's words
    ("Best before: 03/2021" -> "03/2021"), or "". Only in the file's own caption or description, never its title
    (a title's numbers are often an upload date or a catalogue number)."""
    value = CODE if name in ("lot number", "batch number") else DATE
    m = re.search(rf"(?:{pattern})\s*(?:date|on|is|of|:|-|=)?\s*[:\"'“]?\s*({value})\b", text or "", re.I)
    if not m:
        return ""
    found = m.group(1).strip(" .-")
    if name in ("lot number", "batch number") and not re.search(r"\d", found):
        return ""
    return found


def date_rows(title, text):
    """The rows of one file: what kind of mark it is, and its date or code where the file's own words state it;
    [] when neither its title nor its words name such a mark."""
    words = f"{file_words(title)} {text or ''}"
    if NOT_PACKAGING.search(words) or PEOPLE_AT_WORK.search(words) or not PACKAGING.search(words):
        return []
    mark = mark_of(words)
    if not mark:
        return []
    name, question, pattern = mark
    rows = [(ASK_MARK, f"It shows {'an' if name[0] in 'aei' else 'a'} {name}.")]
    value = stated_value(text, name, pattern)
    if value:
        rows.append((question, f"The {name} shown is {value}."))
    return rows


DATE_SPECS = [
    ("Expiration dates", True, date_rows),
    ("search:\"best before\"", False, date_rows),
    ("search:\"use by\" date", False, date_rows),
    ("search:\"expiry date\"", False, date_rows),
    ("search:\"expiration date\"", False, date_rows),
    ("search:\"best by\" date", False, date_rows),
    ("search:\"lot number\"", False, date_rows),
    ("search:\"batch number\" package", False, date_rows),
    ("search:\"date code\"", False, date_rows),
]


def caption_row(title, text, category):
    """The file's own caption, when it is a real one in English (described_commons.own_caption_row)."""
    return own_caption_row(title, text, category)


def build_commons_date_codes(limit):
    """The commons_date_codes pack (see the module docstring)."""
    return build_described(DATE_SPECS, limit, "datecode", adults_only=True, extra_row=caption_row)


DATE_CODE_PACKS = {
    "commons_date_codes": (build_commons_date_codes, "Wikimedia Commons (https://commons.wikimedia.org): files CC0, "
                                                     "public domain or CC BY (credited below); captions CC0."),
}
DATE_CODE_LIMITS = {"commons_date_codes": 400}
DATE_CODE_COMMONS_KEYS = ("commons_date_codes",)


def main(argv=None):
    """Run the builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try the date code pack builder.")
    parser.add_argument("key", choices=sorted(DATE_CODE_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    entries = DATE_CODE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
