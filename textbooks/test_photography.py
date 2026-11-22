"""Self-test of the photography books (textbooks/photography.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once under its request word photography (at most 256 jobs) with its own group
"Reference, photography" and reaches sources.py, and that the arts and crafts guide names the same word; that every
book has a licence the toolkit may repackage, a description and a notice with the safety words (darkroom chemicals,
mercury and cyanide as history, UV, nitrate film, Poison Control); that every old book is from before 1931 and says
what is out of date, the historic process books saying HISTORY ONLY; that the military manuals are judged by the
release rule; that web guides' page patterns match their own addresses; that no Internet Archive item or source is
used by another module of the library; that the index lists only keys the library has (and links the vision section,
the archiving and formats books, the Kiwix references and the manual collections); and that every row of
NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_photography.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import photography as P  # noqa: E402


def entries():
    """Every guide and PDF entry of the module."""
    return list(P.COLLECTION.guides.values()) + list(P.COLLECTION.pdfs.values())


def test_registered_with_own_group():
    assert P in more_refs.modules()
    keys = sources.expand_keys(["photography"])
    assert keys == P.COLLECTION.expand_keys(["photography"]) and len(keys) == len(set(keys)) <= 256
    assert keys[0] == "photo:index"
    assert set(keys) == {"photo:index"} | {f"photo:{e['name']}" for e in entries()}
    assert sources.GROUPS["photography"] == "Reference, photography"
    assert set(P.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    import arts_crafts_index
    assert arts_crafts_index.PHOTOGRAPHY_WORD == "photography"


def test_safety_words():
    for words in ("ventilation", "nitrile gloves", "never mix", "used fixer", "safety data sheet", "mercury",
                  "potassium cyanide", "history only", "expert training", "UV", "cellulose nitrate",
                  "1-800-222-1222"):
        assert words in P.PHOTO_SAFETY, words
    assert "f/16" in P.SUNNY_16 and "ISO" in P.SUNNY_16


def test_every_book():
    for g in entries():
        assert g["group"] == P.GROUP, g["name"]
        whole = bool(g.get("unchanged"))
        short = B.licence_short(g["licence"])
        assert B.licence_kind(short, whole) or B.licence_kind(g["licence"], whole), g["name"]
        assert g["description"] and P.PHOTO_SAFETY in g["notice"], g["name"]
        if g.get("old_public_domain"):
            assert int(g["published"]) < 1931 and g["archive"], g["name"]
            assert P.OLD_NOTE in g["description"], g["name"]
        if g["name"] in P.COLLECTION.guides:
            assert g["licence_page"] and g["licence_text"], g["name"]
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
    for g in P.OLD:
        if g["subject"] == P.HISTORY or "printing processes" in g["subject"].lower() or "History" in g["subject"]:
            assert "HISTORY ONLY" in g["description"], g["name"]
    for g in P.PDFS:
        if g["name"].startswith(("navy_", "army_", "air_corps_")):
            assert g["military"] and g["archive"] and g["notice"].startswith(P.MIL_NOTICE), g["name"]
    darktable = P.COLLECTION.guides["darktable_user_manual"]
    assert re.match(darktable["pages"], "https://docs.darktable.org/usermanual/5.6/en/darkroom/masks/")
    assert not re.match(darktable["pages"], "https://docs.darktable.org/usermanual/5.6/en/contributing/workflow/")
    for name in ("darktable_user_manual", "gimp_user_manual"):
        assert P.EDIT_NOTE in P.COLLECTION.guides[name]["description"]


def test_nothing_used_twice_in_the_library():
    mine = {g["archive"] for g in entries() if g.get("archive")}
    mine_sources = {g.get("pdf") or g.get("source") or g.get("page") for g in entries()} - {None}
    assert len(mine) == len([g for g in entries() if g.get("archive")])
    other = set()
    other_sources = set()
    for m in more_refs.modules():
        if m is P:
            continue
        for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values()):
            if g.get("archive"):
                other.add(g["archive"])
            other_sources.add(g.get("pdf") or g.get("source") or g.get("page"))
    for g in sources.PDF_DOCS:
        if g.get("archive"):
            other.add(g["archive"])
    assert not mine & other, mine & other
    assert not mine_sources & other_sources, mine_sources & other_sources


def test_index_links_existing_books():
    keys = [e[1] for _part, _intro, items in P.SECTIONS for e in items if e[0] == "key"]
    assert keys and all(X.key_exists(k) for k in keys), [k for k in keys if not X.key_exists(k)]
    for _part, _intro, items in P.SECTIONS:
        for e in items:
            if e[0] == "link":
                assert e[2].startswith(("https://", "http://")) and e[3], e
    linked = " ".join(e[1] for _p, _i, items in P.SECTIONS for e in items)
    for key in ("vision:index", "describe:index", "pcb:loc_personal_digital_archiving", "media:loc_av_formats",
                "se:index", "photo_chemicals", "film_cameras_darkroom", "digital_cameras", "nmah_photography"):
        assert key in linked, key
    book, _sign = P.INDEX
    built = book("index", "work", None, [], None)
    assert len(built.pages) == len(P.SECTIONS) and built.licence == "CC0 1.0"


def test_not_included():
    for row in P.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in P.NOT_INCLUDED)
    for words in ("Lightroom", "RawPedia", "Kodak publications of 1931-1963", "Butkus", "Smithsonian", "Wikibooks",
                  "NASA"):
        assert words in names, words
