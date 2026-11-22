"""Self-test of the foraging (foraging.py) and home food preserving (preserving.py) books, with MADE-UP data only:
nothing is downloaded.

It checks that each module is registered once under its request word (at most 256 jobs) with its own group and reaches
sources.py; that every book has a licence the toolkit may repackage, a description, a licence page and line, and a
notice with its safety words (the foraging rule "never eat a wild mushroom unless an expert has confirmed it", Poison
Control; the preserving rules: tested recipes, pressure canner, botulism, altitude); that every old book says what is
out of date (old preserving methods are history only); that the Kerr book of 1945 states the evidence that its
copyright was not renewed; that web guides' page patterns match their own addresses; that the index lists only keys
the library has (the plant identification books, survival manuals and cookbooks are linked, not repeated); and that
every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_foraging_preserving.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import foraging as F  # noqa: E402
import preserving as P  # noqa: E402

MODULES = ((F, "foraging", "forage", "Reference, foraging and edible wild plants", F.FORAGE_SAFETY),
           (P, "preserving", "preserve", "Reference, home food preserving", P.PRESERVE_SAFETY))


def entries(m):
    """Every guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered_with_own_group():
    for m, word, prefix, group_name, _safety in MODULES:
        assert m in more_refs.modules()
        keys = sources.expand_keys([word])
        assert keys == m.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
        assert keys[0] == f"{prefix}:index"
        assert set(keys) == {f"{prefix}:index"} | {f"{prefix}:{e['name']}" for e in entries(m)}
        assert sources.GROUPS[m.GROUP] == group_name
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED.get(P.NOT_RENEWED) == "open"


def test_safety_words():
    for words in ("never eat a wild mushroom unless an expert has confirmed it", "1-800-222-1222", "Never taste",
                  "permission", "protected", "sprayed"):
        assert words in F.FORAGE_SAFETY, words
    for words in ("tested, current recipes", "pressure canner", "botulism", "altitude", "1,000 feet", "call 911",
                  "bulging"):
        assert words in P.PRESERVE_SAFETY, words
    for words in ("HISTORY ONLY", "open-kettle", "oven canning", "paraffin", "boiling-water bath",
                  "current USDA guidance"):
        assert words in P.OLD_PRESERVE, words


def test_every_book():
    for m, _word, _prefix, _group, safety in MODULES:
        for g in entries(m):
            assert g["group"] == m.GROUP, g["name"]
            whole = bool(g.get("unchanged"))
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short, whole) or B.licence_kind(g["licence"], whole), g["name"]
            assert g["description"] and safety in g["notice"], g["name"]
            if g.get("old_public_domain"):
                assert int(g["published"]) < 1931 and g["archive"], g["name"]
            if g["name"] in m.COLLECTION.guides:
                assert g["licence_page"] and g["licence_text"], g["name"]
                pattern = re.compile(g["pages"])
                for url in g.get("urls", []):
                    assert pattern.match(url), (g["name"], url)
    for g in P.PDFS:                      # every old preserving book is history only
        assert "HISTORY ONLY" in g["description"], g["name"]
    for g in F.PDFS:
        if g.get("old_public_domain") and "Mushroom" in g["subject"]:
            assert "never use it to decide what to eat" in g["description"], g["name"]


def test_kerr_not_renewed_with_evidence():
    kerr = P.COLLECTION.pdfs["kerr_home_canning_book_1945"]
    assert kerr["licence"] == P.NOT_RENEWED and not kerr.get("old_public_domain")
    assert "Stanford Copyright Renewal Database" in kerr["notice"] and kerr["published"] == "1945"


def test_uk_books_are_ogl_with_non_us_note():
    for g in (F.COLLECTION.guides["fsa_safe_foraging_uk"], P.COLLECTION.guides["fsa_food_preservation_uk"]):
        assert g["licence"] == "OGL-UK-3.0" and g["country"] == "United Kingdom"
        assert "Open Government Licence v3.0" in g["notice"] and "non-US source" in g["notice"]


def test_index_links_existing_books(monkeypatch):
    for m in (F, P):
        keys = [e[1] for _part, _intro, items in m.SECTIONS for e in items if e[0] == "key"]
        assert keys and all(X.key_exists(k) for k in keys), [k for k in keys if not X.key_exists(k)]
        for _part, _intro, items in m.SECTIONS:
            for e in items:
                if e[0] == "link":
                    assert e[2].startswith("https://") and e[3], e
    linked = " ".join(e[1] for _p, _i, items in F.SECTIONS for e in items)
    for key in ("plantid:saunders_useful_wild_plants", "pdf:army_atp_3_50_21_survival", "plant-id", "cookbooks"):
        assert key in linked, key
    book, _sign = F.INDEX
    built = book("index", "work", None, [], None)
    assert len(built.pages) == len(F.SECTIONS) and built.licence == "CC0 1.0"


def test_not_included():
    for m in (F, P):
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in F.NOT_INCLUDED)
    for words in ("Medsger", "Fernald", "Gibbons", "PLANTS", "iNaturalist", "extension"):
        assert words in names, words
    names = " ".join(r[0] for r in P.NOT_INCLUDED)
    for words in ("Ball Blue Book", "Kerr", "National Center for Home Food Preservation", "extension", "Health Canada",
                  "FAO", "Complete Guide"):
        assert words in names, words
