"""Pack builders for HOME HEALTH TESTS, read for blind users: COVID-19 and other rapid antigen (lateral flow) tests,
pregnancy and ovulation tests, and blood-glucose meter displays, with their result windows (control line, test line,
digital results). Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and
returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "child": true
where the words of a picture name a child. A picture with more than one question comes once with its JPEG and then
again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Why: these tests are read by looking at faint coloured lines in a small window, or a small display. A describer must
say what kind of test it is and, ONLY when the record says it, what the result is.

THE RESULT IS READ ONLY WHERE THE LABEL GIVES IT, and every result answer ends with RESULT_NOTE ("Faint lines can be
hard to read; follow the test's own instructions, retest if unsure, and contact a doctor or pharmacist."):
  - lfa_covid_tests: the researchers' own record of what was put on each test (no virus protein, or a known amount of
    the virus's N protein), said as the record, with what this kind of test's instructions say a negative or a positive
    test shows ("a negative test shows only the control line (C)"); never "I can see two lines".
  - commons_home_health_tests: the file's own title or description, only when it says the result ("positive",
    "negative", "invalid", "two lines", "one line") or a glucose reading with its unit ("112 mg/dL", "6.2 mmol/L"),
    and nothing when it says two different results.

The packs (all open, checked at the source in November 2026):
  lfa_covid_tests            "Images of COVID-19 Lateral Flow Assay Results" (Anne M. Davis and Asahi Tomitaka,
                             figshare collection 7581998, 2024; every item CC BY 4.0): smartphone photos of
                             commercial COVID-19 rapid antigen test cassettes beside a colour chart, after a known
                             amount of nucleocapsid (N) protein was added to the extraction buffer (0, 0.074, 0.18,
                             0.37, 0.74, 1.8, 3.7 and 7.4 ng; the item's title). Read through figshare's public API and
                             its own download server (ndownloader.figshare.com), gently.
  commons_home_health_tests  Wikimedia Commons: Category:COVID-19 rapid antigen tests, and files found with Commons
                             search for pregnancy tests, ovulation tests, rapid antigen and lateral flow tests and
                             glucose meter readings (files CC0, public domain or CC BY, each file's licence checked on
                             its own page; never BY-SA, NC or ND); captions CC0. Files in Category:Glucose meters
                             (home_packs commons_appliances shows those) are left out.

Looked at and not built (training-kit/kit/daily_access_sources.py has the reasons): the FDA's at-home test pages
(their pictures are the makers' packaging, small thumbnails, and the EUA instructions are the makers' own
documents, as with DailyMed's labels), the University of Birmingham lateral-flow set on Mendeley Data (hj9hmywh9c:
CC BY 4.0 but only two PDF documents, no pictures), the Kaggle lateral-flow test set (an account is needed) and the
REACT-2 image library (not released).

Safety (packs/SOURCE-RULES.md): no sexual content, no injuries or blood (a finger-prick photo whose words name blood
is left out, MEDICAL_HARM); rows whose words name a child are marked "child". The Commons photos may show people
(hands, faces): that pack is for describing only, never for picture-making. The figshare photos show only the test
and a colour chart, and may be used.

    python packs/health_test_packs.py lfa_covid_tests --limit 8      (a quick check)
"""

import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, ALT_TEXT, fetch_all

WHAT_Q = "What is this?"
RESULT_Q = "What is the result of this test?"
READING_Q = "What does the glucose meter show?"
RESULT_NOTE = ("Faint lines can be hard to read; follow the test's own instructions, retest if unsure, and contact a "
               "doctor or pharmacist.")
GLUCOSE_NOTE = "Follow your own care plan for this reading, and contact a doctor or pharmacist if unsure."

# ----------------------------------------------------------------- figshare: COVID-19 lateral flow photos

FIGSHARE_API = "https://api.figshare.com/v2/"
LFA_COLLECTION = 7581998
LFA_CREDIT = ("Images of COVID-19 Lateral Flow Assay Results, Anne M. Davis and Asahi Tomitaka, figshare collection "
              "7581998 (2024), item \"{title}\" ({doi}), CC BY 4.0, https://doi.org/{doi}")
LFA_WHAT = ("This is a COVID-19 rapid antigen test (a lateral flow test cassette), photographed after the result was "
            "ready, beside a colour chart. Its window has a control line mark (C) and a test line mark (T).")
AMOUNT = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*ng\s*$")


def lfa_result(title):
    """The answer to "What is the result of this test?" from a figshare item's title (the amount of N protein the
    researchers added), or "" when the title is not an amount."""
    m = AMOUNT.match(title or "")
    if not m:
        return ""
    amount = float(m.group(1))
    if amount == 0:
        return ("The researchers' record says no virus protein was added to this test: it is a negative sample. On "
                "this kind of test a negative result shows only the control line (C). " + RESULT_NOTE)
    faint = (" At an amount this small the test line may be very faint or not show at all." if amount < 1 else "")
    return (f"The researchers' record says {m.group(1)} ng of the virus's N protein was added to this test: it is a "
            f"positive sample. On this kind of test a positive result shows a test line (T) as well as the control "
            f"line (C), however faint.{faint} " + RESULT_NOTE)


def lfa_items(s, want):
    """[(file name, address, rows)] from the collection's items, an even share of each amount."""
    articles = s.get(f"{FIGSHARE_API}collections/{LFA_COLLECTION}/articles", params={"page_size": 100},
                     timeout=60).json()
    rng = pass_random(9308)
    per = max(1, -(-want // max(1, len(articles))))
    items = []
    for article in sorted(articles, key=lambda a: a["id"]):
        detail = s.get(f"{FIGSHARE_API}articles/{article['id']}", timeout=60).json()
        time.sleep(1)
        licence = (detail.get("license") or {}).get("name", "")
        answer = lfa_result(detail.get("title"))
        if licence != "CC BY 4.0" or not answer:
            say(f"  figshare {article['id']}: left out ({licence or 'no licence'}, title {detail.get('title')!r})")
            continue
        files = [f for f in detail.get("files") or [] if f["name"].lower().endswith((".jpg", ".jpeg", ".png"))]
        rng.shuffle(files)
        credit = LFA_CREDIT.format(title=detail["title"], doi=detail.get("doi", ""))
        for f in files[:per]:
            rows = [{"question": WHAT_Q, "answer": LFA_WHAT, "credit": credit},
                    {"question": RESULT_Q, "answer": answer, "credit": credit}]
            items.append((f"lfa-{article['id']}-{f['id']}.jpg", f["download_url"], rows))
        say(f"  figshare {detail['title']}: {min(per, len(files))} of {len(files)} photos")
    return items


def build_lfa_covid_tests(limit):
    """The lfa_covid_tests pack (see the module docstring)."""
    from food_packs import with_twins
    s = session()
    items = lfa_items(s, limit)
    pass_random(9309).shuffle(items)
    return with_twins(fetch_all(items[:limit], workers=2))


# ----------------------------------------------------------------- Commons: home tests

# (Commons search query, what the test is)
TEST_SEARCHES = (
    ('intitle:"pregnancy test"', "a home pregnancy test"),
    ('intitle:"ovulation test"', "an ovulation test"),
    ('intitle:"rapid antigen test"', "a rapid antigen test (a lateral flow test)"),
    ('intitle:"antigen test"', "a rapid antigen test (a lateral flow test)"),
    ('intitle:"lateral flow"', "a lateral flow test"),
    ('intitle:"rapid test"', "a rapid test (a lateral flow test)"),
    ('intitle:"self test" covid', "a COVID-19 self-test"),
    ('intitle:"glucose meter"', "a blood-glucose meter"),
    ('intitle:glucometer', "a blood-glucose meter"),
)
TEST_CATEGORY = ("COVID-19 rapid antigen tests", "a COVID-19 rapid antigen test (a lateral flow test)")
POSITIVE = re.compile(r"\b(positive|two (red |pink |purple )?lines|2 lines|both lines|pregnant)\b", re.I)
NEGATIVE = re.compile(r"\b(negative|one (red |pink |purple )?line|1 line|only (the )?control line|not pregnant)\b",
                      re.I)
INVALID = re.compile(r"\b(invalid|no control line|void)\b", re.I)
GLUCOSE = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d)?)\s?(mg/dl|mmol/l)\b", re.I)
MEDICAL_HARM = re.compile(r"\b(blood|bleed\w*|wounds?|injur\w*|dead|death|nude|naked|patients?)\b", re.I)
NOT_BLOOD = re.compile(r"\bblood[- ](glucose|sugar)\b", re.I)


def test_result(text):
    """The answer to "What is the result of this test?" when the file's own words state one result; "" otherwise."""
    text = text or ""
    found = {name for name, p in (("positive", POSITIVE), ("negative", NEGATIVE), ("invalid", INVALID))
             if p.search(text)}
    if "not pregnant" in text.lower():
        found.discard("positive")
    if len(found) != 1:
        return ""
    said = found.pop()
    lines = {"positive": " (a positive test shows a test line as well as the control line)",
             "negative": " (a negative test shows only the control line)",
             "invalid": " (an invalid test has no control line: it must be done again with a new test)"}[said]
    return f"The photo's own words say the result is {said}{lines}. {RESULT_NOTE}"


def glucose_reading(text):
    """The answer to "What does the glucose meter show?" when the file's own words give one reading with its unit."""
    found = {(m.group(1), m.group(2).lower()) for m in GLUCOSE.finditer(text or "")}
    if len(found) != 1:
        return ""
    value, unit = found.pop()
    unit = "mg/dL" if unit == "mg/dl" else "mmol/L"
    return f"The photo's own words say the meter reads {value} {unit}. {GLUCOSE_NOTE}"


def test_rows(what, title, text, credit):
    """The rows of one Commons file, or [] when its words name harm or nudity."""
    name = re.sub(r"^File:|\.(jpe?g|png|tiff?)$", "", title, flags=re.I).replace("_", " ")
    words = f"{name}. {text or ''}"
    if MEDICAL_HARM.search(NOT_BLOOD.sub(" ", words)):
        return []
    rows = [{"question": WHAT_Q, "answer": f"This is {what}.", "credit": credit}]
    if "glucose meter" in what:
        reading = glucose_reading(words)
        if reading:
            rows.append({"question": READING_Q, "answer": reading, "credit": credit})
    else:
        result = test_result(words)
        if result:
            rows.append({"question": RESULT_Q, "answer": result, "credit": credit})
    if text:
        rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
    return rows


def build_commons_home_health_tests(limit):
    """The commons_home_health_tests pack (see the module docstring)."""
    from food_packs import commons_get, commons_members, with_twins
    from home_packs import commons_fetch, file_name, home_entries, NUDE
    from expression_packs import mark_child
    s = session()
    found = {t: TEST_CATEGORY[1] for t in commons_members(s, TEST_CATEGORY[0], "file")}
    for query, what in TEST_SEARCHES:
        data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": 200,
                               "srsearch": f"{query} filetype:bitmap"})
        for r in (data.get("query") or {}).get("search") or []:
            found.setdefault(r["title"], what)
    shown = set(commons_members(s, "Glucose meters", "file"))
    titles = [t for t in found if t not in shown]
    pass_random(9310).shuffle(titles)
    say(f"Commons home health tests: {len(titles)} files found")
    items = []
    for title, url, credit, text in home_entries(s, titles):
        if NUDE.search(f"{title} {text}"):
            continue
        rows = [mark_child(r, f"{title} {text}") for r in test_rows(found[title], title, text, credit)]
        if rows:
            items.append((file_name("healthtest", title), url, rows))
    pass_random(9311).shuffle(items)
    return with_twins(commons_fetch(items[:int(limit * 1.15) + 2])[:limit])


# ----------------------------------------------------------------- the packs

HEALTH_TEST_PACKS = {
    "lfa_covid_tests": (build_lfa_covid_tests,
                        "Images of COVID-19 Lateral Flow Assay Results (Anne M. Davis and Asahi Tomitaka, figshare "
                        "collection 7581998, 2024), CC BY 4.0, https://figshare.com/collections/7581998; each item "
                        "credited below."),
    "commons_home_health_tests": (build_commons_home_health_tests,
                                  "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or "
                                  "CC BY (credited below) of COVID-19 rapid antigen tests, pregnancy and ovulation "
                                  "tests and glucose meters; captions CC0."),
}
HEALTH_TEST_LIMITS = {
    "lfa_covid_tests": 1200,              # 8 items, about 260 photos each (2 to 3 MB each: made smaller)
    "commons_home_health_tests": 400,     # one category and nine searches
}
HEALTH_TEST_COMMONS_KEYS = ("commons_home_health_tests",)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a home health test pack builder.")
    parser.add_argument("key", choices=sorted(HEALTH_TEST_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = HEALTH_TEST_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
