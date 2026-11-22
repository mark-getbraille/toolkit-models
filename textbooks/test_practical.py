"""Self-test of the six practical life reference modules (driving.py, computer_basics.py, household.py,
knots_outdoor.py, pools_spas.py, motorcycles_rvs.py and their shared helpers in practical_index.py), with MADE-UP data
only: nothing is downloaded.

It checks that each module is registered once under its request words (at most 256 jobs each) and reaches sources.py
with its own group; that every web guide and PDF has a licence the toolkit may repackage, a notice with its safety
words, a description, a licence page and line, a page pattern that matches its own addresses, a published date and a
version; that the military publications are judged by the release rule, the old books by their year, the CDC books
kept whole with CDC's conditions and the EPA book personal use only; that each index book is made offline, lists only
keys the library has, and carries its links; that the Canadian index gets the Canadian practice note; and that every
row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_practical.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import practical_index as X  # noqa: E402
import computer_basics  # noqa: E402
import driving  # noqa: E402
import household  # noqa: E402
import knots_outdoor  # noqa: E402
import motorcycles_rvs  # noqa: E402
import pools_spas  # noqa: E402

# (module, its request words, its group, the words its safety notice must say)
MODULES = [
    (driving, ("driving", "driving-us", "driving-canada"), "driving", ("buckles up", "school bus", "white cane",
                                                                      "call 911")),
    (computer_basics, ("computer-basics",), "computer", ("restart it first", "back up", "official app store")),
    (household, ("household",), "household", ("never mix cleaning products", "ammonia", "1-800-222-1222")),
    (knots_outdoor, ("knots-outdoor",), "knots", ("rated gear", "eye protection", "fire restrictions")),
    (pools_spas, ("pools-spas",), "pools", ("never leave children alone", "drain covers",
                                            "never mix different pool chemicals", "Legionella")),
    (motorcycles_rvs, ("motorcycles-rvs",), "rvs", ("DOT-approved helmet", "tongue weight", "safety chains",
                                                    "carbon monoxide")),
]


def entries(m):
    """Every web guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered():
    seen_prefixes = set()
    for m, words, group, _safety in MODULES:
        assert m in more_refs.modules()
        assert m.COLLECTION.prefix not in seen_prefixes
        seen_prefixes.add(m.COLLECTION.prefix)
        for w in words:
            keys = sources.expand_keys([w])
            assert keys == m.COLLECTION.expand_keys([w]) and 0 < len(keys) == len(set(keys)) <= 256, w
            assert all(m.COLLECTION.owns(k) for k in keys), w
        assert set(sources.expand_keys([words[0]])) == set(m.COLLECTION.own_keys())
        assert sources.GROUPS[group] == m.GROUPS[group] and m.GROUPS[group].startswith("Reference, ")
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED.get(X.EPA_TERMS) == "non-commercial"
    assert set(sources.expand_keys(["driving"])) == set(sources.expand_keys(["driving-us"]) +
                                                        sources.expand_keys(["driving-canada"]))


def test_every_book():
    for m, _words, group, safety in MODULES:
        for g in entries(m):
            assert g["group"] == group and g["group"] in sources.GROUPS, g["name"]
            whole = bool(g.get("unchanged"))
            short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
            assert B.licence_kind(short, whole), g["name"]
            assert g["notice"] and g["description"], g["name"]
            assert g.get("old_public_domain") or (g["licence_page"] and g["licence_text"]), g["name"]
            for words in safety:
                assert words.lower() in g["notice"].lower(), (g["name"], words)
            if g["name"] in m.COLLECTION.guides:
                pattern = re.compile(g["pages"])
                for url in g.get("urls", []):
                    assert pattern.match(url if isinstance(url, str) else url[0]), (g["name"], url)
                if not g["source"].endswith("/site.html"):
                    assert pattern.match(g["source"]), g["name"]
            else:
                assert (g.get("archive") or g.get("pdf")) and g["published"] and g["version"], g["name"]
                if g.get("old_public_domain"):
                    assert int(g["published"]) < 1931 and "Published in" in g["description"], g["name"]
                if re.search(r"\b(Army|Navy|Department of the Navy)\b", g["publisher"]):
                    assert g.get("distribution_a") or g.get("military"), g["name"]
                    assert "front pages print" in g["notice"], g["name"]


def test_special_licences():
    cdc = [g for m, *_ in MODULES for g in entries(m) if g["publisher"] == X.CDC_PUBLISHER]
    assert len(cdc) == 2
    for g in cdc:
        assert g["unchanged"] and g["licence_page"] == X.CDC_TERMS, g["name"]
        for words in ("Source: CDC", "free of charge", "does not constitute its endorsement"):
            assert words in g["notice"], (g["name"], words)
    safer = household.COLLECTION.guides["epa_safer_choice"]
    assert safer["personal_use"] and "Personal use only" in safer["notice"]
    for name in ("libreoffice_getting_started", "libreoffice_writer_guide", "libreoffice_calc_guide"):
        lo = computer_basics.COLLECTION.guides[name]
        assert lo["licence"] == "CC BY 4.0" and "Creative Commons Attribution" in lo["notice"]
        sample = ("This document may be distributed and/or modified under the terms of either the GNU General Public "
                  "License ( https://www.gnu.org/licenses/gpl.html ), version 3 or later, or the Creative Commons "
                  "Attribution License ( https://creativecommons.org/licenses/by/4.0/ ), version 4.0 or later.")
        assert re.search(lo["licence_text"], sample)
        assert re.match(lo["pages"], lo["source"].replace(".html", "02-TextBasics.html"))
    fda = household.COLLECTION.guides["fda_kitchen_food_safety"]
    assert re.search(fda["licence_text"], "both text and graphics are not copyrighted. They are in the public domain")


def test_index_books_offline(monkeypatch):
    """Each index book is made without downloading anything; a key the library lacks is said in left_out."""
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for m, *_ in MODULES:
        for name, (book_fn, sign_fn) in m.COLLECTION.makers.items():
            left_out = []
            book = book_fn(name, "work", None, left_out)
            assert book.pages and book.licence == X.CC0_INDEX and book.name.endswith("_index"), name
            assert not left_out, (m.__name__, left_out)
            text = " ".join(p.body for p in book.pages)
            assert "<a href=\"https://" in text and sign_fn(name) == sign_fn(name)
    us = " ".join(p.body for p in driving.US_INDEX[0]("index_us", "work").pages)
    for state in ("Alabama", "District of Columbia", "Wyoming"):
        assert state in us, state
    canada = driving.CA_INDEX[0]("index_canada", "work")
    assert canada.country == "Canada" and "Ontario" in " ".join(p.body for p in canada.pages)
    assert "kilometres per hour" in sources.practice_note(canada.country, canada.subject, canada.title)
    assert len(driving.US_AGENCIES) == 51 and len(driving.CA_AGENCIES) == 13
    assert all(url.startswith("https://") for _s, _w, url in driving.US_AGENCIES + driving.CA_AGENCIES)


def test_index_key_check(monkeypatch):
    """key_exists: a made-up key is not in the library; the field manuals and other modules' keys are."""
    assert X.key_exists("pdf:army_fm_5_125_rigging") and X.key_exists("drive:mutcd_11th")
    assert not X.key_exists("pdf:made_up_book") and not X.key_exists("drive:made_up")


def test_not_included():
    for m, *_ in MODULES:
        assert m.NOT_INCLUDED, m.__name__
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for m, *_ in MODULES for r in m.NOT_INCLUDED)
    for words in ("handbooks", "NHTSA", "GCFGlobal", "Northstar", "Protect Your Move", "Ashley", "Pool Safely",
                  "Harley-Davidson"):
        assert words in names, words
