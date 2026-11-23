"""Self-test of the craft trade books (craft_trades.py: beekeeping, glass blowing and glass work, leather working,
clothing making and repair), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once (more_refs.MODULES) and reaches sources.py; that each request word (one
per trade and craft-trades for all four) is at most 256 jobs, has no key twice, and together they cover every book;
that the beekeeping books are in the homesteading group and the others in the arts and crafts group; that every book
has a licence the toolkit may repackage, a description, a notice that starts with today's safety note for its trade,
and a licence check (the before-1931 check, a government licence page and line, or the military release rule); that no
Internet Archive item is used twice here or by any other book of the library; that the arts and crafts guide lists
every book; that every row of NOT_INCLUDED says where to find the source; and that a made-up old book whose record
says 1950 is refused by the builder.

Run it from the repository's folder:   python3 -m pytest textbooks/test_craft_trades.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arts_crafts_index as A  # noqa: E402
import build_textbooks as B  # noqa: E402
import craft_trades as CT  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402

WORDS = ("ctrade-bees", "ctrade-glass", "ctrade-leather", "ctrade-clothing", "craft-trades")


def entries():
    """Every book entry of the module (web guides and PDFs)."""
    return list(CT.COLLECTION.guides.values()) + list(CT.COLLECTION.pdfs.values())


def test_registered_once():
    assert CT in more_refs.modules() and more_refs.MODULES.count("craft_trades") == 1
    assert [m for m in more_refs.modules() if m.COLLECTION.prefix == "ctrade"] == [CT]
    assert set(CT.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.GROUPS[CT.GROUP] == "Reference, arts and crafts"
    assert sources.GROUPS[CT.BEE_GROUP] == "Reference, homesteading"


def test_request_words():
    every = {f"ctrade:{e['name']}" for e in entries()}
    seen = []
    for word in WORDS:
        keys = sources.expand_keys([word])
        assert keys == CT.COLLECTION.expand_keys([word]), word
        assert keys and len(keys) == len(set(keys)) <= 256, word
        assert more_refs.module_for(word) is CT, word
        if word != "craft-trades":
            seen += keys
    assert len(seen) == len(set(seen)), "a book in two trades"
    assert set(seen) == every == set(sources.expand_keys(["craft-trades"]))
    for area, word in CT.AREAS.items():
        assert len(CT.area_keys(area)) >= 10, area     # each trade has a real shelf of books


def test_groups_and_areas():
    for e in entries():
        assert e["area"] in CT.AREAS, e["name"]
        assert e["group"] == (CT.BEE_GROUP if e["area"] == "bees" else CT.GROUP), e["name"]


def test_every_book_licensed_with_safety_first():
    notes = {"bees": CT.BEE_NOTE, "glass": CT.GLASS_NOTE, "leather": CT.LEATHER_NOTE, "clothing": CT.CLOTHING_NOTE}
    for e in entries():
        short = e["licence"] if e["licence"] in sources.NO_CHANGES else B.licence_short(e["licence"])
        assert B.licence_kind(short, bool(e.get("unchanged"))), e["name"]
        assert e["title"] and e["description"] and e["notice"], e["name"]
        checked = (e.get("licence_page") and e.get("licence_text")) or e.get("distribution_a") or \
            e.get("old_public_domain")
        assert checked, e["name"]
        if e["name"] in CT.COLLECTION.pdfs:
            assert e["archive"] and e["published"] and e["version"], e["name"]
            if e.get("distribution_a"):          # the builder puts the release line first; the notice is the safety
                assert e["notice"] in (CT.LEATHER_NOTE, CT.CANVAS_NOTE), e["name"]
                continue
            safety = CT.STAINED_NOTE if "stained" in e["subject"].lower() else notes[e["area"]]
            if e.get("old_public_domain"):
                assert e["notice"].startswith(safety), e["name"]
            else:                                # a government work: where the copy is from, then the safety note
                assert e["notice"].startswith("A work of") and e["notice"].endswith(safety), e["name"]
        if e.get("old_public_domain"):
            assert int(e["published"]) < 1931 and "out of date" in e["description"], e["name"]
            assert "scanner's mistakes" in e["notice"], e["name"]
    for e in CT.COLLECTION.guides.values():
        assert e["licence"] == "CC BY-SA 4.0" and "wikibooks.org" in e["source"], e["name"]


def test_safety_notes_say_what_matters():
    for words in ("sting", "911", "smoker", "veil", "foulbrood"):
        assert words in CT.BEE_NOTE, words
    for words in ("didymium", "sodium flare", "ventilation", "asbestos", "mercury"):
        assert words in CT.GLASS_NOTE, words
    for words in ("knives", "solvents", "arsenic", "acids"):
        assert words in CT.LEATHER_NOTE, words
    for words in ("iron", "arsenic", "mercury"):
        assert words in CT.CLOTHING_NOTE, words


def test_military_manuals_judged_by_the_release_rule():
    army = [e for e in CT.PDFS if e["name"].startswith("army_")]
    assert len(army) == 3
    assert all(e["distribution_a"] and e["licence"] == sources.US_GOV for e in army)


def test_no_internet_archive_item_twice():
    mine = [e["archive"] for e in CT.PDFS]
    assert len(mine) == len(set(mine))
    others = {e["archive"] for e in sources.PDF_DOCS if e.get("archive")}
    for m in more_refs.modules():
        if m is not CT:
            others |= {e["archive"] for e in m.COLLECTION.pdfs.values() if e.get("archive")}
    assert not set(mine) & others, set(mine) & others


def test_not_already_on_the_homestead_shelf():
    """homestead.py's Langstroth (1913) and Root (1905) are other editions: listed on the index, not built here."""
    import homestead as HS
    theirs = {p["archive"] for p in HS.PDFS if p.get("archive")}
    assert not theirs & {e["archive"] for e in CT.PDFS}
    assert CT.COLLECTION.pdfs["langstroth_hive_honey_bee_1853"]["published"] == "1853"


def test_index_lists_every_book():
    listed = {what for _p, _i, rows in A.SECTIONS for kind, what, *_r in rows if kind == "key"}
    assert {f"ctrade:{e['name']}" for e in entries()} <= listed
    words = {what for _p, _i, rows in A.SECTIONS for kind, what, *_r in rows if kind == "word"}
    assert set(CT.AREAS.values()) <= words
    titles = [t for t, _i, _r in A.SECTIONS]
    for page in ("Beekeeping", "Glass blowing and glass work", "Leather working", "Clothing making and repair"):
        assert page in titles, page


def test_not_included():
    for row in CT.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in CT.NOT_INCLUDED)
    for words in ("Extension", "Peace Corps", "blacksmithing", "Parachute Rigger", "makers' manuals"):
        assert words in names, words


def test_old_book_after_1930_is_refused(monkeypatch, tmp_path):
    entry = dict(CT.COLLECTION.pdfs["frary_laboratory_glass_blowing_1914"], archive="madeup-glass-1950")

    def fake_fetch(url, cache=None, binary=False, tries=4):
        """A made-up Internet Archive record from 1950; nothing else may be fetched."""
        if "metadata" in url:
            return json.dumps({"metadata": {"date": "1950"}, "files": [{"name": "x.pdf", "format": "Text PDF",
                                                                        "size": "10"}]})
        raise AssertionError(f"nothing else may be fetched: {url}")
    monkeypatch.setattr(B, "fetch", fake_fetch)
    left_out = []
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert "before 1931" in left_out[0]["reason"]
