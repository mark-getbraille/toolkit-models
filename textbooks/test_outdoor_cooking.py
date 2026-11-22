"""Self-test of the emergency, camp and outdoor cooking books (outdoor_cooking.py), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once under its request word (at most 256 jobs) and reaches sources.py; that
every web guide has a licence the toolkit may repackage, a notice with the safety words (carbon monoxide, 911, soapy
water, USDA temperatures), a description, a licence page and line, and a page pattern that matches its own addresses;
that CDC's books are kept whole with CDC's conditions in the notice; that the EPA book is personal use only; that the
Army manuals are checked for Distribution Statement A; that pages are read in the order listed; and that every row of
NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_outdoor_cooking.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import outdoor_cooking as O  # noqa: E402


def test_registered():
    assert O in more_refs.modules()
    keys = sources.expand_keys(["outdoor-cooking"])
    assert keys == O.COLLECTION.expand_keys(["outdoor-cooking"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"outcook:{n}" for n in list(O.COLLECTION.guides) + list(O.COLLECTION.pdfs)}
    assert set(O.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED.get(O.EPA_TERMS) == "non-commercial"


def test_safety_notice_says_what_the_owner_asked():
    for words in ("never use grills, camp stoves, charcoal or generators indoors", "call 911", "soapy water",
                  "145 F", "160 F", "165 F", "When in doubt, throw it out"):
        assert words in O.SAFETY, words


def test_every_book():
    for g in list(O.COLLECTION.guides.values()) + list(O.COLLECTION.pdfs.values()):
        assert g["group"] in sources.GROUPS, g["name"]
        whole = bool(g.get("unchanged"))
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, whole), g["name"]
        assert g["notice"] and g["description"] and g["licence_page"] and g["licence_text"], g["name"]
        assert O.SAFETY in g["notice"], g["name"]
        if g["name"] in O.COLLECTION.guides:
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
            if not g["source"].endswith("/site.html"):
                assert pattern.match(g["source"]), g["name"]
        else:
            assert g["archive"] and g["distribution_a"] and g["published"] and g["version"], g["name"]
    epa = O.COLLECTION.guides["epa_emergency_water"]
    assert epa["personal_use"] and "Personal use only" in epa["notice"]


def test_cdc_books_whole_with_conditions():
    cdc = [g for g in O.GUIDES if g["publisher"] == O.CDC_PUBLISHER]
    assert len(cdc) == 3
    for g in cdc:
        assert g["unchanged"] and g["licence_page"] == O.CDC_TERMS, g["name"]
        for words in ("Source: CDC", "free of charge", "does not constitute its endorsement"):
            assert words in g["notice"], (g["name"], words)
    water = O.COLLECTION.guides["cdc_emergency_water"]
    pattern = re.compile(water["pages"])
    assert pattern.match("https://www.cdc.gov/water-emergency/about/how-to-create-and-store-an-emergency-water-"
                         "supply.html")
    assert not pattern.match("https://www.cdc.gov/water-emergency/site.html")
    assert not pattern.match("https://www.cdc.gov/water-emergency/es/index.html")
    assert not pattern.match("https://www.cdc.gov/water-emergency/hcp/toolkit/index.html")


def test_pages_read_in_order(monkeypatch):
    """A fixed-list guide is read in the order listed, its first page first, and nothing else is fetched."""
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    ready = O.COLLECTION.guides["ready_food_water_power"]
    found = [u for u, _unit in D.crawl(ready, None)]
    assert found == O.READY_PAGES
    assert [unit for _u, unit in D.crawl(ready, None)][:3] == ["Emergency food and supplies", "Water", "Water"]


def test_not_included():
    for row in O.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in O.NOT_INCLUDED)
    for words in ("FSIS", "NFPA", "Leave No Trace", "Smokey Bear", "Extension", "Coleman", "Wikibooks"):
        assert words in names, words
