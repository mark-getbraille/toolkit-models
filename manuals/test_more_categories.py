"""Self-test of the collections added from the reference inventory of 2026-11-21 (manuals/more_categories.py and
build_manuals.ia_collection_entries), with MADE-UP Internet Archive answers only: nothing is downloaded.

It checks that:
  - the new categories are listed with plain names, a kind, a licence and Internet Archive sources, and the old
    categories keep everything they had;
  - every one of the 141 collections the inventory found missing is mapped to a category;
  - a collection whose every item belongs to a category is listed without title words; a mixed collection is
    searched with the category's words; collections outside the Manual Library (DLARC) are searched by name;
  - old items are kept only for the categories that ask for it (any_year);
  - the firearms collection never lets in what FIREARMS_EXCLUDE forbids or a military manual.

Run it from the repository's folder:   python3 -m pytest manuals/test_more_categories.py
"""

import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import more_categories as M  # noqa: E402

NEW = ("baby_gear", "home_medical", "ham_radio", "musical_instruments", "video_games", "powersports",
       "marine_electronics", "farm_equipment", "camping_outdoor", "software", "vintage_computers")


class FakeArchive:
    """Answers advancedsearch.php with made-up items per collection; records each query."""

    def __init__(self, items):
        self.items, self.queries, self.requests = items, [], 0

    def json(self, url, headers=None, cache=True):
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))["q"]
        self.queries.append(q)
        docs = []
        for coll, items in self.items.items():
            if f"collection:{coll}" in q:
                docs += items
        return {"response": {"docs": docs}}


def test_new_categories_are_complete():
    for key in NEW:
        cat = C.CATEGORIES[key]
        assert cat["kind"] == "manuals" and cat["name"] and cat["description"] and "CC0" in cat["licence"]
        assert cat.get("ia") or cat.get("ia_whole"), key
    assert len(C.CATEGORIES) >= 62 + len(NEW)
    assert "firearmsmanuals" in C.CATEGORIES["firearms"]["ia_whole"]
    assert C.CATEGORIES["firearms"]["makers"]                       # the makers are kept
    assert "lanco-safety-data-sheets" in C.CATEGORIES["chemical_safety"]["ia_whole"]


def test_every_missing_collection_is_mapped():
    assert len(set(M.MISSING_IN_INVENTORY)) == 141
    for coll in M.MISSING_IN_INVENTORY:
        assert M.COLLECTION_MAP.get(coll), coll
        for key, how in M.COLLECTION_MAP[coll]:
            assert key in C.CATEGORIES and how in ("whole", "words", "through synthmanuals")
    assert all(c.startswith("synthmanuals-") for c, v in M.COLLECTION_MAP.items()
               if v == [("musical_instruments", "through synthmanuals")])
    assert "synthmanuals" in C.CATEGORIES["musical_instruments"]["ia_whole"]


def test_generic_words_are_not_used():
    # Words that would pull other categories' products in (kitchen mixers, computer keyboards, DVD discs ...).
    for key, bad in (("musical_instruments", {"keyboard", "mixer", "recorder", "tuner"}),
                     ("farm_equipment", {"disc", "loader", "operator's manual"}),
                     ("camping_outdoor", {"cooler"}), ("software", {"office", "user's guide"})):
        assert not bad & set(C.CATEGORIES[key]["ia"]), key


def test_whole_mixed_and_outside_collections():
    old = {"identifier": "colecovision-donkey-kong", "title": "Donkey Kong (1982)(Coleco)", "year": "1982"}
    items = {"colecovisionmanuals": [old],
             "dlarc-manuals": [{"identifier": "dlarc-ic-730", "title": "Icom IC-730 instruction manual",
                                "year": "1981"}, {"identifier": "dlarc-cat", "title": "Ham radio catalog 1975"}],
             "manuals_graco": [{"identifier": "graco-seat", "title": "Graco 44164 Car Seat User Manual"}]}
    fetch = FakeArchive(items)
    notes = []
    cat = dict(ia=[], ia_whole={"colecovisionmanuals": "ColecoVision game manual"}, any_year=True)
    got = B.ia_collection_entries(fetch, "video_games", cat, 50, notes, set())
    assert [e["kind"] for e in got] == ["ColecoVision game manual"]          # 1982 kept: any_year
    assert "title:" not in fetch.queries[-1]                                 # whole: no title words
    got = B.ia_collection_entries(fetch, "video_games", dict(cat, any_year=False), 50, notes, set())
    assert got == []                                                         # without any_year: before 1990, out
    fetch = FakeArchive(items)
    cat = C.CATEGORIES["baby_gear"]
    got = B.ia_collection_entries(fetch, "baby_gear", dict(cat, ia_whole={}), 50, notes, set())
    q = next(q for q in fetch.queries if "collection:manuals_graco" in q)
    assert '("car" AND "seat")' in q and " OR " in q
    assert got[0]["name"] and got[0]["collection"] == "manuals_graco"
    fetch = FakeArchive(items)
    ham = C.CATEGORIES["ham_radio"]
    got = B.ia_collection_entries(fetch, "ham_radio", ham, 100, notes, set())
    assert any("collection:dlarc-manuals" in q for q in fetch.queries)
    kept = [e for e in got if not B.ia_excluded(e, ham["ia_exclude"])]
    assert {e["id"] for e in kept} >= {"ia-dlarc-ic-730"} and "ia-dlarc-cat" not in {e["id"] for e in kept}


def test_firearms_collection_rule():
    rule = C.CATEGORIES["firearms"]["ia_exclude"]
    entry = lambda t: {"name": t, "manuals": [{"title": t}]}          # noqa: E731
    assert not B.ia_excluded(entry("Ruger 10/22 Instruction Manual"), rule)
    for bad in ("TM 9-1005-319-10 Rifle M16A2 operator's manual", "Department of the Army field manual rifle",
                "Solvent trap baffle kit instructions", "Auto sear installation", "Glock switch",
                "Winchester catalog 1990", "Reloading manual 9mm", "Armorer's manual"):
        assert B.ia_excluded(entry(bad), rule), bad


def test_word_search_unchanged_for_old_categories():
    fetch = FakeArchive({"manuals": [{"identifier": "x", "title": "Toaster T1 manual", "year": "1985"}]})
    assert B.ia_search(fetch, "toaster", ("manuals",), 10) == []              # before 1990: left out, as before
    assert 'title:("toaster")' in fetch.queries[-1]
