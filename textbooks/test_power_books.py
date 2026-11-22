"""Self-test of the power and electrical books (power_books.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once under its two request words (each at most 256 jobs, together every key
once) and reaches sources.py with its group "Reference, power and electrical"; that every book has a licence the
toolkit may repackage, a notice with the safety words (carbon monoxide, 20 feet, 911, back-feeding, transfer switch,
licensed electrician, lithium, rotating parts, fall protection), a description, a licence page and line, and a page
pattern that matches its own addresses; that the Army manuals go through the release rule (and the restricted one is
only a link); that the old books are checked for their year and say they are out of date; that the Wikibooks books
are share-alike; that the books moved into the group keep their keys; that pages are read in the order listed; and
that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_power_books.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import electronics_books as E  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import power_books as P  # noqa: E402


def test_registered():
    assert P in more_refs.modules() and more_refs.MODULES.count("power_books") == 1
    backup = sources.expand_keys(["backup-power"])
    solar = sources.expand_keys(["solar"])
    for keys in (backup, solar):
        assert len(keys) == len(set(keys)) <= 256
    assert not set(backup) & set(solar)
    every = {f"power:{n}" for n in list(P.COLLECTION.guides) + list(P.COLLECTION.pdfs)}
    assert set(backup) | set(solar) == every
    assert "power:doe_homeowners_guide_solar" in solar and "power:irs_form_5695_instructions" in solar
    assert "power:doe_small_wind" in backup and "power:army_fm_5_424_electrical_systems_1997" in backup
    assert sources.GROUPS["power"] == "Reference, power and electrical"
    assert set(P.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_safety_notice_says_what_the_owner_asked():
    for words in ("only outdoors", "20 feet", "carbon monoxide", "call 911", "back-feed", "dryer outlet",
                  "line workers", "transfer switch", "licensed electrician", "DC can arc", "lithium",
                  "rotating parts", "fall protection", "National Electrical Code"):
        assert words in P.SAFETY, words


def test_every_book():
    for g in list(P.COLLECTION.guides.values()) + list(P.COLLECTION.pdfs.values()):
        assert g["group"] == "power" and g["group"] in sources.GROUPS, g["name"]
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, bool(g.get("unchanged"))), g["name"]
        assert g["notice"] and g["description"], g["name"]
        assert P.SAFETY in g["notice"], g["name"]
        if g.get("old_public_domain"):
            assert int(g["published"]) < 1931 and "out of date" in g["notice"] and g["archive"], g["name"]
        elif g["name"] in P.COLLECTION.guides:
            assert g["licence_page"] and g["licence_text"], g["name"]
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
            assert pattern.match(g["source"]) or g["name"].startswith("wikibooks_"), g["name"]
        else:
            assert g["licence_page"] and g["licence_text"] and (g.get("archive") or g.get("pdf")), g["name"]
    wiki = [g for g in P.GUIDES if g["name"].startswith("wikibooks_")]
    assert len(wiki) == 2 and all(g["licence"] == "CC BY-SA 4.0" for g in wiki)


def test_army_manuals_follow_the_release_rule():
    army = [p for p in P.PDFS if p["name"].startswith("army_")]
    assert len(army) == 4
    for p in army:
        assert p["archive"] and (p.get("military") or p.get("distribution_a")) and p["work"] == "a work of the US Army"
        assert p["published"] and p["version"], p["name"]
    restricted = next(r for r in P.NOT_INCLUDED if "9-6115-639" in r[0])
    assert "Distribution Statement C" in restricted[1] and "personal use" in restricted[1]


def test_moved_books_keep_their_keys():
    docs = {d["name"]: d for d in sources.PDF_DOCS}
    for name in P.MOVED_TO_POWER:
        assert docs[name]["group"] == "power", name
    assert docs["navy_neets_module_06"]["group"] == "course"
    kuphaldt = [p for p in E.PDFS if p["name"].startswith("kuphaldt_liec_")]
    assert len(kuphaldt) == 6 and all(p["group"] == "power" for p in kuphaldt)
    assert "elec:kuphaldt_liec_dc" in sources.expand_keys(["electronics"])
    assert all(p["group"] == "electronics" for p in E.PDFS if p["name"].startswith("navy_neets_module_1"))


def test_pages_read_in_order(monkeypatch):
    """A fixed-list guide is read in the order listed, its first page first, and nothing else is fetched."""
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    wind = P.COLLECTION.guides["doe_small_wind"]
    found = [u for u, _unit in D.crawl(wind, None)]
    assert found == P.WINDEXCHANGE_PAGES
    assert [unit for _u, unit in D.crawl(wind, None)][:2] == ["The Small Wind Guidebook", "The Small Wind Guidebook"]


def test_not_included():
    for row in P.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in P.NOT_INCLUDED)
    for words in ("NREL", "Sandia", "National Electrical Code", "OSHA", "Open Source Ecology", "Hugh Piggott",
                  "Practical Action", "Florida Solar Energy Center", "Instructables", "Ford Pro Power Onboard",
                  "Victron"):
        assert words in names, words
