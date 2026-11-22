"""Self-test of the military knot and rope manuals (knots_military.py, kmil:) and the bushcraft books (bushcraft.py,
bush:), the siblings of knots_outdoor.py in the group "Reference, knots and outdoor skills", with MADE-UP data only:
nothing is downloaded.

It checks that each module is registered once under its request word (at most 256 jobs), reaches sources.py with the
shared group, and that its licence lines and NOT_INCLUDED rows (each with an address) are there; that every book has
a licence the toolkit may repackage, a description and a notice with every safety note the owner asked for (rope
loads, climbing training, sharp tools, fire safety and local rules on fires and cutting); that the military manuals are
judged by the release rule and keep only their safe chapters (keep_parts, build_textbooks.kept_part, tried on made-up
pages); that a military book keeps the builder's truthful release line (refs_kit.Collection.book_for); that the old
books are dated before 1931 and say what is out of date, Seton's and Baden-Powell's with the note on their offensive
portrayals; that the New Zealand pages' licence and titles are read as checked; that the index books are made offline
with keys the library has; and that the knot index links the new books.

Run it from the repository's folder:   python3 -m pytest textbooks/test_knots_bushcraft.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import bushcraft  # noqa: E402
import directory_sources as D  # noqa: E402
import knots_military  # noqa: E402
import knots_outdoor  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

MODULES = [(knots_military, "knots-military"), (bushcraft, "bushcraft")]
SAFETY = ("working load", "rated gear", "proper training", "eye protection", "fire restrictions",
          "local rules on fires and cutting")


def entries(m):
    """Every web guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered_in_the_shared_group():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    for m, word in MODULES:
        assert m in more_refs.modules() and prefixes.count(m.COLLECTION.prefix) == 1
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256 and set(keys) == set(m.COLLECTION.own_keys()), word
        assert m.GROUPS == knots_outdoor.GROUPS and sources.GROUPS["knots"] == "Reference, knots and outdoor skills"
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_every_book_licence_and_safety():
    for m, _word in MODULES:
        for g in entries(m):
            assert g["group"] == "knots" and g["description"] and g["notice"], g["name"]
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short) or B.licence_kind(g["licence"]), g["name"]
            for words in SAFETY:
                assert words in g["notice"], (g["name"], words)
            if g.get("old_public_domain"):
                assert int(g["published"]) < 1931 and "Published in" in g["description"], g["name"]
            elif g["name"] in m.COLLECTION.pdfs:
                assert g.get("military") or g.get("distribution_a"), g["name"]
                assert "front pages print" in g["notice"] and g["published"] and g["version"], g["name"]
    assert "safety" in knots_outdoor.OUTDOOR_SAFETY.lower()


def test_old_book_notes_and_exclusions():
    pdfs = bushcraft.COLLECTION.pdfs
    for name in ("seton_book_of_woodcraft_1912", "baden_powell_scouting_for_boys_1915"):
        assert "outdated and offensive" in pdfs[name]["description"], name
    assert pdfs["baden_powell_scouting_for_boys_1915"]["country"] == "United Kingdom"
    keys = " ".join(sources.expand_keys(["bushcraft"]) + sources.expand_keys(["knots-military"]))
    for left_out in ("pig", "sticking", "evasion", "10_644", "3_02h", "31_27", "3_05_213", "seamanship_1951", "seamanship_1964", "seamanship_1972"):
        assert left_out not in keys, left_out
    rows = " ".join(r[0] + " " + r[1] for r in knots_military.NOT_INCLUDED + bushcraft.NOT_INCLUDED)
    for words in ("1 January 1996", "Pig-Sticking", "Kochanski", "Evasion", "FM 31-27", "Down But Not Out",
                  "Australia", "New Zealand"):
        assert words in rows, words


class FakeText:
    """Made-up pages for build_textbooks.kept_part: {page number: [lines]}."""

    def __init__(self, pages):
        self.pages = pages

    def lines(self, n):
        return self.pages.get(n, [])


def test_kept_parts_on_made_up_pages():
    text = FakeText({0: ["CHAPTER 11", "SNOW SHELTERS", "Basic characteristics for shelters"],
                     5: ["CHAPTER 10 SKIBORNE FIRING POSITIONS", "Made-up words"],
                     9: ["CHAPTER 4 ROPE MANAGEMENT, KNOTS, AND ANCHORS"]})
    assert B.kept_part(knots_military.WINTER_PARTS, "Chapter_", text, 0) == (True, "Chapter 11 Snow Shelters")
    kept, name = B.kept_part(knots_military.WINTER_PARTS, "Chapter_", text, 5)
    assert not kept and name == "Chapter 10 Skiborne Firing Positions"
    assert B.kept_part(knots_military.MOUNTAIN_PARTS, "Chapter 4: Rope Management", text, 9)[0]
    for title in ("Chapter 1: Intelligence In Mountainous Terrain", "Chapter 3: Maneuver Planning Considerations",
                  "Chapter 9: Security In A Mountainous Environment", "Chapter 12: Fires In A Mountainous Environment",
                  "Chapter 14: Force Protection", "Appendix F: Warfighting Load Requirements"):
        assert not B.kept_part(knots_military.MOUNTAIN_PARTS, title, FakeText({}), 0)[0], title
    for title in ("Chapter 2 Winter Tracking", "Chapter 7 Ice Mobility And Countermobility", "Chapter 12 Training"):
        assert not B.kept_part(knots_military.WINTER_PARTS, title, FakeText({}), 0)[0], title
    assert not B.kept_part(knots_military.PACK_PARTS, "Chapter 6: Hanger And Adapter Loads", FakeText({}), 0)[0]
    assert B.kept_part(knots_military.PACK_PARTS, "Chapter 5: Lashed Loads", FakeText({}), 0)[0]
    pdfs = knots_military.COLLECTION.pdfs
    for name in ("usmc_mcrp_12_10a3_mountain_rope_work", "usmc_mcrp_12_10a2_winter_operations",
                 "army_fm_25_7_pack_transportation_1944"):
        # read whole since 22 November 2026 (the owner's decision); only explosives parts are cut (distribution_a)
        assert not pdfs[name].get("keep_parts") and pdfs[name]["distribution_a"], name


def test_military_book_keeps_the_release_line(monkeypatch):
    """The builder's notice (its truthful release line first) is not replaced by the entry's own notice."""
    def made_up_book(entry, work, cache=None, left_out=None):
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], "https://archive.org/details/made-up",
                          entry["description"], "Made-up release line. " + entry["notice"])
    monkeypatch.setattr(B, "pdfdoc_book", made_up_book)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    book = knots_military.COLLECTION.book_for("kmil:uscg_bch_seamanship_fundamentals", "work")
    assert book.notice.startswith("Made-up release line. The release line before this")
    old = bushcraft.COLLECTION.book_for("bush:nessmuk_woodcraft_1900", "work")
    assert old.notice == bushcraft.COLLECTION.pdfs["nessmuk_woodcraft_1900"]["notice"]


def test_new_zealand_pages():
    g = bushcraft.COLLECTION.guides["nz_doc_outdoor_safety"]
    assert g["licence"] == "CC BY 4.0" and g["country"] == "New Zealand" and "credited" in g["notice"]
    sample = ("Unless identified as having third party copyright or other licence, the material on this website is "
              "Crown Copyright and can be reused under the terms of the Creative Commons Attribution 4.0 "
              "International Licence (CC BY 4.0).")
    assert re.search(g["licence_text"], sample)
    pattern = re.compile(g["pages"])
    assert all(pattern.match(u) for u in g["urls"]) and pattern.match(g["source"])
    assert not pattern.match("https://www.doc.govt.nz/parks-and-recreation/things-to-do/hunting/")
    m = re.search(g["title_from"], "<html><title>River crossing safety: Know before you go</title>", re.S)
    assert m.group(1) == "River crossing safety"


def test_index_books_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for m in (bushcraft, knots_outdoor):
        book_fn, _sign_fn = m.COLLECTION.makers["index"]
        left_out = []
        book = book_fn("index", "work", None, left_out)
        assert book.pages and book.licence == X.CC0_INDEX and not left_out, (m.__name__, left_out)
        assert '<a href="https://' in " ".join(p.body for p in book.pages)
    linked = {e[1] for _p, _i, items in knots_outdoor.SECTIONS for e in items}
    for key in ("kmil:uscg_bch_seamanship_fundamentals", "kmil:usmc_mcrp_12_10a3_mountain_rope_work", "bush:index",
                "knot:burgess_knots_ties_splices_1884", "knots-military", "bushcraft"):
        assert key in linked, key
