"""Self-test of three collections of the owner's request of 2026-11-23: learning music (music_learning.py,
musiclearn:), running a small business and taxes (business_tax.py, biz:) and everyday maths (everyday_maths.py,
emath:), with MADE-UP data only: nothing is downloaded.

It checks that each module is registered once and its request words reach sources.expand_keys, each at most 256 jobs
and without duplicates; that every book is in a library group, has a licence the toolkit may repackage (the two open
music theory textbooks share-alike and kept apart; everything else open), a licence check made at build time (the
licence line of its page, or the pre-1931 year check for an old book, or the shared military rule for an Army manual),
a description and a notice; that the notices say what each kind of book needs (printed notation in the music books,
the out-of-date braille code in the braille music books, "not tax, legal or accounting advice" in the business
books, machine-read maths in the maths books); that no Internet Archive item, official PDF or web page is listed twice
here or elsewhere in the library; that each index lists only books the library has and every link-only row says why;
that the licence lines match made-up page text; that the IRS and Wayback page lists match their own page patterns;
and that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_music_business_maths.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import business_tax as BZ  # noqa: E402
import everyday_maths as EM  # noqa: E402
import more_refs  # noqa: E402
import music_learning as ML  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402

MODULES = {
    "music_learning": (ML, "musiclearn", ["music-theory", "music-methods", "music-braille-history", "music-learning"],
                       "music-learning"),
    "business_tax": (BZ, "biz", ["biz-irs", "biz-sba-ftc", "biz-bookkeeping", "business-tax"], "business-tax"),
    "everyday_maths": (EM, "emath", ["emath-practical", "emath-measure-money", "everyday-maths"], "everyday-maths"),
}


def entries(module):
    """Every PDF and web guide entry of a module."""
    return list(module.COLLECTION.pdfs.values()) + list(module.COLLECTION.guides.values())


def test_registered_and_word_sizes():
    for name, (module, prefix, words, every) in MODULES.items():
        assert more_refs.MODULES.count(name) == 1 and module in more_refs.modules(), name
        for word in words:
            keys = sources.expand_keys([word])
            assert keys == module.COLLECTION.expand_keys([word]), word
            assert keys and len(keys) == len(set(keys)) <= 256, word
            assert all(k.startswith(prefix + ":") for k in keys), word
        assert set(sources.expand_keys([every])) == set(module.COLLECTION.own_keys()), name
        assert f"{prefix}:index" in sources.expand_keys([every])
        assert module.GROUP in sources.GROUPS
        assert set(module.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in module.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED
    # the theme words together cover every book of each module (the index is in the overall word only)
    for module, prefix, words, every in MODULES.values():
        themed = set().union(*(sources.expand_keys([w]) for w in words if w != every))
        assert themed | {f"{prefix}:index"} == set(module.COLLECTION.own_keys())
    # "music:" stays the sheet music collection's prefix
    assert more_refs.module_for("music:index").__name__ == "sheet_music"
    assert more_refs.module_for("musiclearn:index") is ML


def test_every_book_has_an_allowed_licence_and_check():
    for module, _prefix, _words, _every in MODULES.values():
        for e in entries(module):
            assert e["group"] == module.GROUP, e["name"]
            assert e["description"] and e["notice"] and e["title"] and e["subject"], e["name"]
            kind = B.licence_kind(B.licence_short(e["licence"]))
            if e["name"] in ML.COLLECTION.guides:
                assert kind == "share-alike" and "share-alike" in e["notice"], e["name"]
            else:
                assert kind == "open", e["name"]
            assert not e.get("personal_use"), e["name"]
            if e.get("old_public_domain"):
                assert e.get("archive") and re.fullmatch(r"1[5-9]\d\d", e["published"]), e["name"]
                assert int(e["published"]) < 1931, e["name"]
            elif e.get("archive"):
                assert e.get("distribution_a") and e["licence"] == sources.US_GOV, e["name"]
            else:
                assert e["licence_text"] and (e.get("licence_page") or e.get("page")), e["name"]


def test_notices_say_what_each_kind_of_book_needs():
    for e in ML.THEORY_PDFS + ML.METHOD_PDFS + ML.ARMY_PDFS:
        if e["name"] not in ("elson_music_dictionary_1905", "guilbert_how_to_sing_a_song_1919"):
            assert ML.NOTATION in e["notice"] or ML.NOTATION in e["description"], e["name"]
    for e in ML.GUIDES:
        assert ML.NOTATION in e["description"], e["name"]
    for e in ML.BRAILLE_PDFS:
        assert "Music Braille Code 2015" in e["description"] and "OUT OF DATE" in e["description"], e["name"]
    for e in entries(BZ):
        assert e["notice"].endswith(BZ.NOT_ADVICE), e["name"]
    for e in entries(EM):
        assert EM.SCANNED_MATHS in e["notice"], e["name"]


def test_no_duplicates_in_the_library():
    ours_archives, ours_pdfs, ours_starts, names = [], [], [], []
    for module, prefix, _words, _every in MODULES.values():
        for e in entries(module):
            names.append(f"{prefix}:{e['name']}")
            if e.get("archive"):
                ours_archives.append(e["archive"])
            if e.get("pdf"):
                ours_pdfs.append(e["pdf"])
            if e.get("source") and not e.get("archive") and not e.get("pdf"):
                ours_starts.append(e["source"])
    for group in (ours_archives, ours_pdfs, ours_starts, names):
        assert len(group) == len(set(group))
    archives, pdfs, starts = set(), set(), set()
    for m in more_refs.modules():
        if m in (ML, BZ, EM):
            continue
        for e in entries(m):
            archives.add(e.get("archive"))
            pdfs.add(e.get("pdf"))
            starts.add(e.get("source"))
    for e in sources.PDF_DOCS:
        archives.add(e.get("archive"))
        pdfs.add(e.get("pdf"))
    assert not set(ours_archives) & archives
    assert not set(ours_pdfs) & pdfs
    assert not set(ours_starts) & starts
    # the books other collections already have are linked, never built again
    assert "harmonyitsthe00prouuoft" not in ours_archives and "exercisesinmelod00goet" not in ours_archives
    assert "braillemusicnota00unse" not in ours_archives
    built = {f.rsplit("/", 1)[1] for f in ours_pdfs}
    for already in ("p17.pdf", "p334.pdf", "p583.pdf", "p587.pdf", "p15.pdf", "p463.pdf", "p505.pdf", "p970.pdf",
                    "p907.pdf", "p501.pdf"):
        assert already not in built, already


def test_index_books(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for module, prefix, _words, _every in MODULES.values():
        left_out = []
        book = module.INDEX_BOOK("index", "/nonexistent", None, left_out)
        assert book.licence == "CC0 1.0" and book.group == module.GROUP and book.name == f"{prefix}_index"
        assert len(book.pages) == len(module.INDEX_SECTIONS)
        assert left_out == [], left_out
        assert module.INDEX_SIGN("index") == module.INDEX_SIGN("index")
        for _part, intro, rows in module.INDEX_SECTIONS:
            assert intro
            for kind, what, words, *more in rows:
                assert kind in ("key", "word", "manuals", "link"), what
                if kind == "key":
                    assert X.key_exists(what), what
                if kind == "word":
                    assert sources.expand_keys([what]), what
                if kind == "link":
                    assert words.startswith("https://") and more and more[0], what
        # every book of the module is in its own index
        listed = {what for _p, _i, rows in module.INDEX_SECTIONS for kind, what, *_r in rows if kind == "key"}
        assert set(module.COLLECTION.own_keys()) - {f"{prefix}:index"} <= listed


def test_licence_lines_match_made_up_page_text():
    omt, mt21c = ML.COLLECTION.guides["open_music_theory"], ML.COLLECTION.guides["music_theory_21st_century_classroom"]
    footer = "© 2022 Hybrid Pedagogy Publishing. CC BY–SA 4.0. Powered by Jekyll"
    assert re.search(omt["licence_text"], footer)
    colophon = ("Website ©2017 Robert Hutchinson Permission is granted to copy, distribute and/or modify this document "
                "under the terms of the GNU Free Documentation License, Version 1.2 or any later version published")
    assert re.search(mt21c["licence_text"], colophon)
    assert not re.search(mt21c["licence_text"], "Licensed under CC BY-NC-ND 4.0")
    page = '<header>menu</header><article class="wrap post"><h1>Triads</h1><p>Words.</p></article><footer>'
    m = re.search(omt["content"][0], page)
    assert m and re.search(omt["content"][1], page[m.end():])
    page = '<main class="ptx-main"><section><p>Pitch.</p></section></main>'
    assert re.search(mt21c["content"][0], page) and re.search(mt21c["content"][1], page)


def test_page_lists_match_their_patterns():
    irs = BZ.COLLECTION.guides["irs_small_business_pages"]
    assert len(irs["urls"]) == len(set(irs["urls"]))
    for url in irs["urls"]:
        assert re.match(irs["pages"], url), url
    ftc = BZ.COLLECTION.guides["ftc_business_guides_wayback"]
    for url in ftc["urls"]:
        assert re.match(ftc["pages"], url) and "id_/https://www.ftc.gov/" in url, url
    assert ftc["published"] == BZ.FTC_NEWEST and BZ.FTC_OLDEST <= BZ.FTC_NEWEST
    assert "Wayback Machine" in ftc["notice"] and "travel" not in ftc["notice"]
    for module in (ML,):
        for e in module.GUIDES:
            assert re.match(e["pages"], e["source"]), e["name"]


def test_irs_entries():
    for e in BZ.IRS_PUBS + BZ.IRS_INSTRUCTIONS:
        assert re.fullmatch(r"https://www\.irs\.gov/pub/irs-pdf/[a-z0-9]+\.pdf", e["pdf"]), e["name"]
        assert e["page"].startswith("https://www.irs.gov/"), e["name"]
        assert e["subject"] == "Taxes" and e["licence"] == sources.US_GOV
    names = {e["name"] for e in BZ.IRS_PUBS}
    assert {"irs_pub_3", "irs_pub_524", "irs_pub_15a", "irs_pub_15b"} <= names
    assert "irs_pub_535" not in names                     # discontinued: in NOT_INCLUDED instead
    assert any("535" in row[0] for row in sources.NOT_INCLUDED)


def test_old_years_are_readable_by_the_builder(monkeypatch):
    """The builder's year check reads a plain year; "c1906" is not read (so such items were left out)."""
    import json
    record = {"metadata": {"date": "c1906"}}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, **k: json.dumps(record))
    assert B.archive_year("made-up-item") == 0
    record["metadata"]["date"] = "[1897]"
    assert B.archive_year("made-up-item") == 1897


def test_not_included_rows_say_where():
    for module, _prefix, _words, _every in MODULES.values():
        assert module.NOT_INCLUDED
        for title, reason in module.NOT_INCLUDED:
            assert title and reason and "Index: https://" in reason, title
