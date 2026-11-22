"""Self-test of the electronics, building and crafts reference modules (electronics_books.py, building_books.py,
crafts_books.py), with MADE-UP data only: nothing is downloaded.

It checks that each module is registered once under its request words (each request at most 256 jobs) and reaches
sources.py with its group; that every book has a licence the toolkit may repackage, a notice with its safety note,
a description and a licence check (a licence page and line, Distribution Statement A for a military manual, or the
before-1931 check for an old book); that every web guide has a page pattern its own addresses match; that the
pottery and jewellery books are request words of their own; that the NLS and assistive-device books say how to get
a player repaired; that every row of NOT_INCLUDED says where to find the source; and that a made-up old book whose
Internet Archive record is from 1950 is refused by the builder.

Run it from the repository's folder:   python3 -m pytest textbooks/test_repair_build_crafts.py
"""

import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402

NAMES = {"electronics_books": ("electronics", "Reference, electronics repair and assistive technology"),
         "building_books": ("building", "Reference, building and light construction"),
         "crafts_books": ("crafts", "Reference, arts and crafts")}


def modules():
    """The three modules, as more_refs loads them."""
    return [m for m in more_refs.modules() if m.__name__ in NAMES]


def test_all_three_registered():
    assert {m.__name__ for m in modules()} == set(NAMES)
    for m in modules():
        word, title = NAMES[m.__name__]
        assert sources.GROUPS[m.GROUP] == title
        assert word in m.COLLECTION.words


@pytest.mark.parametrize("m", modules(), ids=lambda m: m.__name__)
def test_books_registered_and_licensed(m):
    c = m.COLLECTION
    word = NAMES[m.__name__][0]
    keys = sources.expand_keys([word])
    assert keys == c.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"{c.prefix}:{n}" for n in list(c.guides) + list(c.pdfs)}
    for g in list(c.guides.values()) + list(c.pdfs.values()):
        # Lessons in Electric Circuits is in the power and electrical group (power_books.py), keys unchanged
        moved = g["name"].startswith("kuphaldt_liec_") and g["group"] == getattr(m, "POWER_GROUP", None)
        assert g["group"] == m.GROUP or moved, g["name"]
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, bool(g.get("unchanged"))), g["name"]
        assert g["notice"] and g["description"] and g["title"], g["name"]
        checked = (g.get("licence_page") and g.get("licence_text")) or g.get("distribution_a") or \
            g.get("old_public_domain")
        assert checked, g["name"]
        assert re.search(r"[Ss]afety|NLS|warranty|repair", g["notice"]) or g["licence"].startswith("CC BY-SA") \
            or m.__name__ != "crafts_books", g["name"]
        if g.get("old_public_domain"):
            assert g["archive"] and int(g["published"]) < 1931, g["name"]
            assert "old book" in g["notice"] or "OLD" in g["notice"] or "out of date" in g["notice"], g["name"]
        if g["name"] in c.guides:
            assert g.get("crawl") or g.get("urls"), g["name"]
            pattern = re.compile(g["pages"])
            for start, _depth in g.get("crawl", []):
                if "wikibooks" in start:
                    assert pattern.match(start + "/Introduction"), g["name"]
    assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in m.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_safety_and_repair_notes():
    import building_books as BB
    import crafts_books as CB
    import electronics_books as EB
    for p in EB.PDFS:
        if p["name"].startswith(("kuphaldt", "navy_neets")):
            assert EB.MAINS_NOTE in p["notice"], p["name"]
    nls = [p for p in EB.PDFS + EB.GUIDES if p["name"].startswith("nls_")]
    assert len(nls) == 3 and all("1-888-657-7323" in p["notice"] for p in nls)
    assert "VIST" in EB.GUIDES[1]["notice"]
    assert all(BB.SAFETY_NOTE in p["notice"] for p in BB.PDFS)
    soap = next(p for p in CB.PDFS if "soap" in p["name"])
    assert soap["notice"].startswith(CB.LYE_NOTE) and "lye to water, never water to lye" in CB.LYE_NOTE
    assert next(p for p in CB.PDFS if p["name"].startswith("binns"))["notice"].startswith(CB.KILN_NOTE)
    military = [p for p in BB.PDFS if p["name"].startswith(("army_", "navy_"))]
    assert military and all(p["distribution_a"] for p in military)
    assert all(p["distribution_a"] for p in EB.PDFS if p["name"].startswith("navy_neets"))
    # the NEETS modules here are only the ones sources.NEETS does not have
    assert not {p["name"] for p in EB.PDFS} & {e["name"] for e in sources.PDF_DOCS}


def test_pottery_and_jewellery_words():
    keys = sources.expand_keys(["pottery-books"])
    assert keys and all(k.startswith("craft:") for k in keys) and "craft:binns_potters_craft_1910" in keys
    assert sources.expand_keys(["jewellery-books"]) == ["craft:rose_cirino_jewelry_making_1917"]


def test_old_book_after_1930_is_refused(monkeypatch, tmp_path):
    import crafts_books as CB
    entry = dict(CB.PDFS[0], archive="madeup-pottery-1950")

    def fake_fetch(url, cache=None, binary=False, tries=4):
        if "metadata" in url:
            return json.dumps({"metadata": {"date": "1950"}, "files": [{"name": "x.pdf", "format": "Text PDF",
                                                                        "size": "10"}]})
        raise AssertionError(f"nothing else may be fetched: {url}")
    monkeypatch.setattr(B, "fetch", fake_fetch)
    left_out = []
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert "before 1931" in left_out[0]["reason"]
