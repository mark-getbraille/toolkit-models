"""Self-test of the home repair, pest control and textile crafts books (home_crafts.py), with MADE-UP data only:
nothing is downloaded.

It checks that every book is registered once under its request word "home-crafts" (at most 256 jobs) and reaches
sources.py with its group "Reference, home repair, pests and handcrafts"; that every book has a licence the toolkit
may repackage, a notice, a description and a licence page and line (the old books: the before-1931 check instead);
that the EPA books are personal use only with the pesticide safety note; that every old book says what is out of
date in it, and the ones naming chemicals or finishes warn about them; that the web guides' page patterns take their
own pages and leave out forms; that no Internet Archive item is already a book of another module; that every row of
NOT_INCLUDED says where to find the source; and that a made-up old book is refused when its record's year is 1931 or
later.

Run it from the repository's folder:   python3 -m pytest textbooks/test_home_crafts.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import home_crafts as H  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def test_registered():
    assert "home_crafts" in more_refs.MODULES and H in more_refs.modules()
    assert sources.GROUPS["homecraft"] == "Reference, home repair, pests and handcrafts"
    keys = sources.expand_keys(["home-crafts"])
    c = H.COLLECTION
    assert keys == c.expand_keys(["home-crafts"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"craft:{n}" for n in list(c.guides) + list(c.pdfs)}
    assert set(H.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in H.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_every_book_has_its_licence_and_notice():
    for g in H.GUIDES + H.PDFS:
        assert g["group"] == "homecraft", g["name"]
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, bool(g.get("unchanged"))), g["name"]
        assert g["notice"] and g["description"] and g["title"] and g["subject"], g["name"]
        assert g.get("published") or g["name"] in H.COLLECTION.guides, g["name"]
        if g.get("old_public_domain"):
            assert g["archive"] and g["licence"] == H.OLD_LICENCE and int(g["published"]) < 1931, g["name"]
            assert "Published in " in g["description"] and "scanner" in g["notice"], g["name"]
        else:
            assert g["licence_page"] and g["licence_text"], g["name"]


def test_epa_books_personal_use_with_safety_notes():
    for g in H.GUIDES:
        assert g["personal_use"] and g["licence"] == H.EPA_TERMS and g["licence_page"] == H.EPA_DISCLAIMER
        assert B.licence_kind(B.licence_short(g["licence"])) == "non-commercial"
        assert "Personal use only" in g["notice"]
    pest = H.COLLECTION.guides["epa_safe_pest_control"]
    assert H.PESTICIDE_SAFETY in pest["notice"] and "1-800-222-1222" in pest["notice"]
    leak = H.COLLECTION.guides["epa_fix_a_leak"]
    assert "shut-off valve" in leak["notice"] and "licensed" in leak["notice"]


def test_page_patterns():
    pest = re.compile(H.COLLECTION.guides["epa_safe_pest_control"]["pages"])
    assert pest.match("https://www.epa.gov/bedbugs/do-it-yourself-bed-bug-control")
    assert pest.match("https://www.epa.gov/safepestcontrol")
    assert not pest.match("https://www.epa.gov/bedbugs/forms/contact-us-about-bed-bugs")
    assert not pest.match("https://www.epa.gov/mold/mold-cleanup")          # already home:epa_home_health
    leak = re.compile(H.COLLECTION.guides["epa_fix_a_leak"]["pages"])
    assert leak.match("https://www.epa.gov/watersense/fix-leak-week")
    assert not leak.match("https://www.epa.gov/watersense/media-room")
    for g in H.GUIDES:
        pattern = re.compile(g["pages"])
        for url in g.get("urls", []):
            assert pattern.match(url), (g["name"], url)


def test_old_book_notes():
    chemical = {"mairet_vegetable_dyes_1916", "leland_manual_of_mending_1896"}
    for g in H.PDFS:
        if g["name"] in chemical:
            assert "poisonous or are banned" in g["description"], g["name"]
        if re.search(r"Upholstery|Shoe repair|Leatherwork|Spinning", g["subject"]):
            assert "out of date" in g["description"], g["name"]
    stains = H.COLLECTION.pdfs["usda_removing_stains_1965"]
    assert "never mix bleach with ammonia" in stains["description"] and stains["licence"] == sources.US_GOV


def test_no_archive_item_is_another_modules_book():
    """No Internet Archive item of this module is named by another textbooks module (thin:sewing and the others)."""
    others = ""
    for name in os.listdir(HERE):
        if name.endswith(".py") and name != "home_crafts.py" and not name.startswith("test_"):
            with open(os.path.join(HERE, name), encoding="utf-8") as f:
                others += f.read()
    for g in H.PDFS:
        assert f'"{g["archive"]}"' not in others, g["name"]


def test_old_book_refused_after_1930(monkeypatch, tmp_path):
    """A made-up item whose record says 1931 is refused before anything is downloaded."""
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                    "https://archive.org/details/x"))
    monkeypatch.setattr(B, "archive_year", lambda ident, cache=None: 1931)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    left_out = []
    entry = dict(H.COLLECTION.pdfs["webster_quilts_1915"], archive="madeupitem")
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert "before 1931" in left_out[0]["reason"]
