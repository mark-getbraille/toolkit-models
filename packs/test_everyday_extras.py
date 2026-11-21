"""A self-test of the everyday extras pack parsers (packs/everyday_extras_packs.py), with made-up file titles only:
nothing is downloaded from the internet.

It checks that:
  - a money file's side is read only from its own title ("obverse", "Back", "-d"/"-r" coin photo names, camel case)
    or an "Obverses of ..." category, and a file with no side, or about something else, gets no rows;
  - a banknote file showing both sides is left out (US law allows colour pictures of paper money only one-sided);
  - coin designs are said only for dates within the design's years, and the touch facts match the coin;
  - US bill answers say the large numeral only for series that have it, and Canadian note answers give the Bank of
    Canada's tactile symbols for the value, and say an older note has none;
  - banknote pictures are made at most NOTE_SIDE pixels long;
  - the fixed-answer packs leave out art of a thing, storm damage (sky) and files naming private data (mail), and a
    garment's colour or pattern comes from its own categories only when they name one alone;
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflow's known list and limit lines, and in
    the kit's sources.

Run it from the repository's folder:   python3 -m pytest packs/test_everyday_extras.py
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import everyday_extras_packs as e  # noqa: E402

COIN = {c[0]: c for c in e.US_COINS}


def answers(rows):
    """{question: answer} of rows."""
    return {r["question"]: r["answer"] for r in rows}


def test_side_of():
    assert e.side_of("1994-P Washington quarter obverse") == "front"
    assert e.side_of("$20HawaiiBack") == "back"
    assert e.side_of("$20HawaiiBothSides") == "both"
    assert e.side_of("1964-USA-half-dollar-Kennedy-d", coded=True) == "front"
    assert e.side_of("1964-USA-half-dollar-Kennedy-r", coded=True) == "back"
    assert e.side_of("1964-USA-half-dollar-Kennedy-r") == ""            # the coded ending only for coins
    assert e.side_of("1932 Washington quarter", ["Obverses of Washington quarters"]) == "front"
    assert e.side_of("1962 penny") == ""
    assert e.year_of("1959-2008-ig nyomott") is None and e.year_of("1937 20 bank of canada back") == 1937


def test_us_coins():
    got = answers(e.us_coin_rows("1994-P Washington quarter obverse", [], COIN["Obverses of Washington quarters"]))
    assert got[e.MONEY_Q] == "This is the front (heads side) of a US 25-cent coin (a quarter), dated 1994."
    assert got[e.SIDE_Q] == "The front shows George Washington's head."
    assert "ridged" in got[e.TOUCH_Q]
    assert e.us_coin_rows("1962 penny", [], COIN["Lincoln Memorial cent"]) == []                  # no side
    assert e.us_coin_rows("17720-SparkFun MicroMod RP2040 Processor-04A", ["Obverses of Washington quarters"],
                          COIN["Obverses of Washington quarters"]) == []                          # not money
    assert e.us_coin_rows("Quarter obverse for scale", [], COIN["Washington quarter"]) == []
    # a date outside the design's years: nothing said about the design
    got = answers(e.us_coin_rows("1955 Lincoln cent reverse", [], COIN["Lincoln Memorial cent"]))
    assert e.SIDE_Q not in got and "smooth" in got[e.TOUCH_Q]
    got = answers(e.us_coin_rows("1976 Kennedy half dollar reverse", [], COIN["Kennedy half dollar"]))
    assert "Independence Hall" in got[e.SIDE_Q]
    got = answers(e.us_coin_rows("1960 Franklin half dollar reverse", [], COIN["Franklin half dollar"]))
    assert got[e.SIDE_Q] == "The back shows the Liberty Bell."
    got = answers(e.us_coin_rows("2004 Jefferson nickel reverse", [], COIN["Jefferson nickel"]))
    assert e.SIDE_Q not in got                                          # a Westward Journey year
    got = answers(e.us_coin_rows("2005 Sacagawea dollar reverse", [], COIN["Sacagawea dollar"]))
    assert got[e.SIDE_Q] == "The back shows an eagle in flight."


def test_canadian_coins():
    got = answers(e.ca_coin_rows("1950 Canada 5 cents obverse", [], "ca_nickel"))
    assert "twelve sides" in got[e.TOUCH_Q] and "King or Queen" in got[e.SIDE_Q]
    got = answers(e.ca_coin_rows("1990 Canada dollar reverse", [], "ca_dollar"))
    assert "a loon" in got[e.SIDE_Q] and "eleven sides" in got[e.TOUCH_Q]
    got = answers(e.ca_coin_rows("1970 Canadian nickel dollar reverse", [], "ca_dollar"))
    assert e.SIDE_Q not in got and "before" in got[e.TOUCH_Q]
    assert e.ca_coin_rows("Canadian penny", [], "ca_cent") == []


def test_us_notes():
    assert e.us_note_rows("$20HawaiiBothSides", [], 20) == []
    got = answers(e.us_note_rows("$20HawaiiBack", [], 20))
    assert got[e.MONEY_Q] == "This is the back of a US twenty-dollar bill (a Federal Reserve Note)."
    assert got[e.SIDE_Q].startswith("Since 1928,") and "White House" in got[e.SIDE_Q]
    assert "Designs from series 1996 on" in got[e.TOUCH_Q]
    got = answers(e.us_note_rows("Series 2004 20 dollar note front", [], 20))
    assert got[e.SIDE_Q] == "The front of the US twenty-dollar bill shows a portrait of Andrew Jackson."
    assert "This design has a large numeral 20" in got[e.TOUCH_Q]
    got = answers(e.us_note_rows("Series 1985 one dollar bill obverse", [], 1))
    assert "large numeral" not in got[e.TOUCH_Q] and "same size" in got[e.TOUCH_Q]
    got = answers(e.us_note_rows("Series 1914 5 dollar note back", [], 5))
    assert e.SIDE_Q not in got and "before 1929" in got[e.TOUCH_Q]
    assert e.us_note_rows("Play money 20 dollar note front", [], 20) == []


def test_canadian_notes():
    got = answers(e.ca_note_rows("1937 20 bank of canada back", [], 20))
    assert got[e.MONEY_Q] == "This is the back of a Canadian twenty-dollar bill (a 20-dollar banknote) from 1937."
    assert got[e.TOUCH_Q].startswith("This older note has no tactile dots.") and "three symbols" in got[e.TOUCH_Q]
    assert "the colour green" in got[e.TOUCH_Q]
    assert "wider smooth space" in e.ca_note_touch(100, 2012) and e.ca_note_touch(100, 2012).startswith("This note")
    assert "no tactile dots" in e.ca_note_touch(2, 1986)
    assert e.ca_note_rows("$20 E", [], 20) == []


def test_note_pictures_made_small():
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (1280, 545), "green").save(out, "JPEG")
    small = Image.open(io.BytesIO(e.shrink(out.getvalue(), e.NOTE_SIDE)))
    assert max(small.size) <= e.NOTE_SIDE
    assert e.is_note(e.us_note_rows("$20HawaiiBack", [], 20))
    assert not e.is_note(e.us_coin_rows("1994-P Washington quarter obverse", [], COIN["Washington quarter"]))


def run_rows(monkeypatch, specs, titles, **kw):
    """The rows build_fixed gives each made-up title of the first spec (nothing downloaded)."""
    got = {}

    def fake(specs, limit, prefix, rows):
        one = specs[0]
        for title in titles:
            got[title] = rows(title, "", [], one, one["category"])
        return []
    monkeypatch.setattr(e, "extras_commons", fake)
    monkeypatch.setattr(e, "commons_fetch", lambda items: items)
    e.build_fixed(specs, 5, "test", **kw)
    return got


def test_fixed_packs(monkeypatch):
    got = run_rows(monkeypatch, [e.fixed("Tornadoes", "It is a tornado.", e.SKY_Q)],
                   ["Painting of a tornado", "Tornado damage in Joplin", "Tornado near Dodge City"], harm=True)
    assert got["Painting of a tornado"] == [] and got["Tornado damage in Joplin"] == []
    assert got["Tornado near Dodge City"] == [{"question": e.SKY_Q, "answer": "It is a tornado."}]
    got = run_rows(monkeypatch, e.MAIL_SPECS[:1], ["Envelope with return address", "Brown envelope"], private=True)
    assert got["Envelope with return address"] == [] and got["Brown envelope"][0]["answer"] == "It is an envelope."
    tee = e.CLOTHING_SPECS[0]
    rows = answers(e.clothing_rows("x", "", ["Red T-shirts", "Striped T-shirts", "Men wearing T-shirts"], tee, ""))
    assert rows == {e.CLOTHING_Q: "There is a T-shirt in this picture.",
                    e.COLOUR_Q: "There is red clothing in this picture.", e.PATTERN_Q: "It has stripes."}
    assert answers(e.clothing_rows("x", "", ["Red T-shirts", "Blue T-shirts"], tee, "")) == {
        e.CLOTHING_Q: "There is a T-shirt in this picture."}
    # Commons files a photo under "Basketballs" when a ball is merely in it: say what is in the picture
    said = {one["category"]: one["info"][0] for one in e.TOYS_SPORTS_MUSIC_SPECS + e.GROOMING_SPECS}
    assert said["Basketballs"] == (e.IN_PICTURE_Q, "There is a basketball in this picture.")
    assert said["Dice"] == (e.IN_PICTURE_Q, "There are dice in this picture.")
    assert said["Lego"][1] == "There is LEGO in this picture: toy plastic bricks that fit together."
    assert said["Violins"] == (e.INSTRUMENT_Q, "There is a violin in this picture.")
    assert said["Curling irons"][1] == "There is a curling iron in this picture: it curls hair and gets very hot."
    assert e.instrument_name("Violins") == "a violin" and e.instrument_name("Grand pianos") == "a grand piano"
    for specs in (e.MAIL_SPECS, e.CLOTHING_SPECS, e.GROOMING_SPECS, e.TOYS_SPORTS_MUSIC_SPECS, e.SKY_SPECS,
                  e.SCREEN_SPECS):
        names = [one["category"] for one in specs]
        assert len(names) == len(set(names))
        assert all(a.endswith(".") and q.endswith("?") for one in specs for q, a in one["info"])


def test_wiring():
    """Every pack is in PACKS and COMMONS_KEYS, the workflows know it and the kit lists it."""
    keys = set(e.EVERYDAY_EXTRAS_PACKS)
    assert keys == set(e.EVERYDAY_EXTRAS_LIMITS)
    assert keys <= set(build_packs.PACKS)
    assert keys <= build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    for key, limit in e.EVERYDAY_EXTRAS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    import sources
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed)
    assert all(listed[key].group == "permissive" for key in keys)
    assert set(e.PEOPLE_PACKS) <= keys and set(e.PEOPLE_PACKS) <= set(sources.NOT_FOR_PICTURE_MAKING)
