"""Self-test of the blind and low-vision living books (vision_living.py), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once under its request word (at most 256 jobs), in its own group, and
reaches sources.py; that every web guide has a licence the toolkit may repackage (the Orca help share-alike), a
notice, a description, a licence page and line, and a page pattern that matches its own addresses; that every key the
index names is a book of the library and every manual collection it names exists; that the index book is built from
those records alone (made-up keys are left out and said); that the APH reader takes only the museum's own
public-domain-marked articles; and that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_vision_living.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import vision_living as V  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_registered():
    assert V in more_refs.modules() and more_refs.MODULES.count("vision_living") == 1
    keys = sources.expand_keys(["vision-living"])
    assert keys == V.COLLECTION.expand_keys(["vision-living"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == set(V.COLLECTION.own_keys()) and "vision:index" in keys
    assert sources.GROUPS["vision"] == "Reference, blind and low-vision living"
    assert set(V.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED.get(V.PDM) == "open"


def test_every_guide():
    for g in V.COLLECTION.guides.values():
        assert g["group"] == V.GROUP, g["name"]
        short = B.licence_short(g["licence"])
        assert B.licence_kind(short, False), g["name"]
        assert g["notice"] and g["description"] and g["licence_page"] and g["licence_text"], g["name"]
        pattern = re.compile(g["pages"])
        for url in g.get("urls", []):
            assert pattern.match(url), (g["name"], url)
        assert pattern.match(g["source"]), g["name"]
    orca = V.COLLECTION.guides["orca_help"]
    assert B.licence_kind(B.licence_short(orca["licence"])) == "share-alike"
    assert "Share Alike 3" in orca["licence_text"].replace("\\", "") and "same licence" in orca["notice"]
    assert not re.match(orca["pages"], "https://help.gnome.org/orca/index.html.de")


def test_index_keys_are_real():
    import glob
    manuals = ""                     # the manual library's sources (not imported: its module names clash with ours)
    for path in glob.glob(os.path.join(REPO, "manuals", "*.py")):
        with open(path, encoding="utf-8") as f:
            manuals += f.read()
    for title, intro, entries in V.SECTIONS:
        assert title and intro.endswith("."), title
        for kind, what, words, *more in entries:
            assert kind in ("key", "manuals", "pack", "link") and words, (title, what)
            if kind == "key":
                assert V.key_exists(what), what
            elif kind == "manuals":
                assert f'CATEGORIES["{what}"]' in manuals or f'"{what}": dict(' in manuals, what
            elif kind == "link":
                assert what and words.startswith("https://") and more and more[0], (title, what)
    assert not V.key_exists("vision:no_such_book") and not V.key_exists("law:no_such_law")


def test_index_pack_keys_are_packs():
    sys.path.insert(0, os.path.join(REPO, "packs"))
    import build_packs  # noqa: F401 - loaded first, as the pack files expect
    for _t, _i, entries in V.SECTIONS:
        for kind, what, *_rest in entries:
            if kind == "pack":
                assert what in build_packs.PACKS, what


def test_index_book_from_records(monkeypatch, tmp_path):
    """The index is made from its records only: a made-up key is left out and said; nothing is fetched."""
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    monkeypatch.setattr(V, "SECTIONS", [("Made-up subject", "A made-up introduction.", [
        ("key", "atdoc:nvda_user_guide", "NVDA User Guide"), ("key", "vision:made_up", "nothing"),
        ("pack", "commons_braille_writing", "braille writers"),
        ("link", "A made-up site", "https://example.org/", "Copyright: link-only.")])])
    left_out = []
    book = V.index_book("index", str(tmp_path), None, left_out)
    assert len(book.pages) == 1 and "atdoc:nvda_user_guide" in book.pages[0].body
    assert "vision:made_up" not in book.pages[0].body and left_out[0]["title"] == "vision:made_up"
    assert "https://example.org/" in book.pages[0].body and book.licence == "CC0 1.0"


def test_aph_reader(monkeypatch, tmp_path):
    """Only the museum's own "museum-" articles by APH or its director, still marked, with a text file."""
    found = {"response": {"docs": [
        {"identifier": "museum-2022-01-01-made-up-writer", "title": "A made-up braille writer", "creator": "Mike Hudson",
         "date": "2022-01-01"},
        {"identifier": "museum-2022-01-02-unmarked", "title": "Unmarked now", "creator": "Mike Hudson"},
        {"identifier": "afb-slides-2005", "title": "Slides by someone else", "creator": "Mike Hudson"},
        {"identifier": "museum-2022-01-03-other", "title": "By another author", "creator": "Helen Keller"}]}}
    meta = {"museum-2022-01-01-made-up-writer": {"metadata": {"licenseurl": V.PDM_URL},
                                                 "files": [{"name": "x_djvu.txt"}]},
            "museum-2022-01-02-unmarked": {"metadata": {"licenseurl": ""}, "files": [{"name": "y_djvu.txt"}]}}

    def fake_fetch(url, cache=None, **_k):
        if url.startswith(V.IA_SEARCH):
            return json.dumps(found)
        if "/metadata/" in url:
            return json.dumps(meta[url.rsplit("/", 1)[1]])
        return "This made-up article tells how a braille writer of the museum was made and used. " * 3
    monkeypatch.setattr(B, "fetch", fake_fetch)
    monkeypatch.setattr(V.K, "readable", lambda url, cache=None: True)
    assert [i[0] for i in V.aph_items()] == ["museum-2022-01-01-made-up-writer", "museum-2022-01-02-unmarked"]
    left_out = []
    book = V.aph_book("aph_museum_articles", str(tmp_path), None, left_out)
    assert [p.title for p in book.pages] == ["A made-up braille writer"]
    assert left_out[0]["reason"].startswith("It no longer carries") and book.licence == V.PDM
    assert V.aph_own(["Mike Hudson"]) and not V.aph_own(["Mike Hudson", "John Macy"])


def test_pages_read_in_order(monkeypatch):
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    bep = V.COLLECTION.guides["bep_currency_access"]
    assert [u for u, _unit in D.crawl(bep, None)] == V.BEP_PAGES


def test_not_included():
    for row in V.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in V.NOT_INCLUDED)
    for words in ("JAWS", "VoiceOver", "BANA", "Hadley", "Perkins", "HathiTrust", "Helen Keller", "Red Book",
                  "Bookshare"):
        assert words in names, words
