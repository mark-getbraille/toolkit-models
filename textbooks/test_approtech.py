"""Self-test of the appropriate technology books (approtech.py, apt:), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once (more_refs.MODULES) with its own group, that every request word reaches
sources.expand_keys with at most 256 jobs and that approtech holds every key; that its licences are ones the toolkit
may repackage, each Peace Corps manual with the check that fits its licence (the no-notice rule with the front-page
check, or the Peace Corps' reproduction line), and every book a description and a notice with the safety notes; that
the front-page check refuses made-up pages that claim a copyright, a VITA copyright or a Peace Corps-only permission
and accepts plain ones; that the well manual cuts its explosives part (build_textbooks.pdfdoc_book on a made-up PDF);
that no Internet Archive item or PDF address is used twice in the library, nor any of the link-only items; that the
index is made offline with keys the library has; and that the licence lines and NOT_INCLUDED rows (each with an
address) reach sources.py.

Run it from the repository's folder:   python3 -m pytest textbooks/test_approtech.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approtech as A  # noqa: E402
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402

WORDS = ["approtech", "apt-water", "apt-building", "apt-farming", "apt-energy-tools", "apt-health"]


def test_registered_with_its_own_group():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert A in more_refs.modules() and prefixes.count("apt") == 1
    assert sources.GROUPS["approtech"] == "Reference, appropriate technology and village skills"
    every = sources.expand_keys(["approtech"])
    assert set(every) == set(A.COLLECTION.own_keys()) and len(every) == len(set(every))
    for word in WORDS:
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        assert set(keys) <= set(every), word
    themed = {k for w in WORDS[1:] for k in sources.expand_keys([w])}
    assert themed | {"apt:index"} == set(every)          # every book is in at least one theme
    assert set(A.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in A.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    assert sources.ALLOWED[A.NO_NOTICE] == "open" and sources.ALLOWED[A.PC_FREE] == "open"


def test_every_book_licence_and_safety():
    names = set()
    for e in A.PDFS:
        assert e["name"] not in names and e["group"] == "approtech", e["name"]
        names.add(e["name"])
        assert e["description"] and e["notice"] and e["published"] and e["version"], e["name"]
        assert B.licence_kind(B.licence_short(e["licence"])) or B.licence_kind(e["licence"]), e["name"]
        assert re.search(r"[Ss]afety|[Nn]ever|fence them|stored dry", e["notice"]), e["name"]
        if e.get("old_public_domain"):
            assert int(e["published"]) < 1931 and "Published in" in e["description"], e["name"]
        if e["licence"] == A.NO_NOTICE:
            assert e["pdf_licence_text"] == A.PC_FRONT and int(e["published"]) < 1989, e["name"]
            assert e["licence_page"] == A.NO_NOTICE_PAGE and "17 U.S.C. 405" in e["notice"], e["name"]
            assert "Written by" in e["description"], e["name"]
        elif e["licence"] == A.PC_FREE:
            assert e["pdf_licence_text"] == A.PC_FREE_TEXT and "without payment or royalty" in e["notice"], e["name"]
    wells = A.COLLECTION.pdfs["pc_wells_construction_1982"]
    assert wells["cut_explosives"] and "dynamite is left out" in wells["description"]
    for words in ("air has been tested", "harness", "cave-ins", "Never use explosives"):
        assert words in wells["notice"], words
    assert "alkaline" in A.COLLECTION.pdfs["usda_adobe_sun_dried_brick_1934"]["notice"]
    assert "Have well and spring water tested".lower() in A.WATER_SAFETY.lower()


def test_front_page_check_on_made_up_pages():
    good = ("ERIC PERMISSION TO REPRODUCE THIS MATERIAL HAS BEEN GRANTED BY Peace Corps Information Collection and "
            "Exchange Manual M-99 Made-up Wells written by A. Nobody")
    assert re.search(A.PC_FRONT, good)
    for bad in ("Peace Corps Made-up Ponds (c) VITA, 1976 May be reproduced for official U.S. Government purposes",
                "Peace Corps Made-up Ponds @ VITA, 1976", "Copyright 1981 by A. Nobody. Peace Corps reprint",
                "Made-up Rabbits. Reprinted with permission for Peace Corps use only.",
                "A made-up manual of another agency"):
        assert not re.search(A.PC_FRONT, bad), bad
    assert re.search(A.PC_FREE_TEXT, "This manual may be reproduced and/br_ translated in part or in full without "
                                     "payment of royalty.")
    assert not re.search(A.PC_FREE_TEXT, "Peace Corps, all rights reserved")
    assert re.search(A.NO_NOTICE_TEXT, "405. Notice of copyright: Omission of notice on certain copies")


def test_well_manual_cuts_explosives(monkeypatch, tmp_path):
    """pdfdoc_book leaves out a part whose title names explosives when the entry says cut_explosives (made-up PDF)."""
    entry = dict(A.COLLECTION.pdfs["pc_wells_construction_1982"], licence_page="", licence_text="",
                 pdf_licence_text="")
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                      "https://archive.org/details/x"))
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    work = tmp_path / "work"
    work.mkdir()
    (work / f"{entry['name']}.pdf").write_bytes(b"%PDF-made-up")

    class FakeText:
        """Made-up pages, every one with words."""
        count = 30

        def __init__(self, path):
            pass

        def lines(self, n):
            return ["Made-up words about digging a well safely, lining it and covering it, " * 2]

    monkeypatch.setattr(B, "PdfText", FakeText)
    monkeypatch.setattr(B, "front_text", lambda path, pages=12: "Peace Corps made-up front")
    monkeypatch.setattr(B, "file_sha256", lambda path: "0" * 64)
    monkeypatch.setattr(B, "part_html", lambda text, start, end: "<p>Made up.</p>")
    monkeypatch.setattr(B, "manual_parts", lambda path: [("Section Two: Hand Dug Wells", 0, 10),
                                                         ("Appendix C: Uses of Dynamite in Hand Dug Wells", 10, 20),
                                                         ("Appendix D: Cement", 20, 30)])
    left_out = []
    book = B.pdfdoc_book(entry, str(work), None, left_out)
    titles = [p.title for p in book.pages]
    assert len(titles) == 2 and not any("Dynamite" in t for t in titles), titles
    assert "explosives" in book.changes and "Dynamite" in book.description and not left_out


def test_no_address_used_twice_in_the_library():
    mine = [e.get("archive") or e.get("pdf") for e in A.PDFS]
    assert len(mine) == len(set(mine))
    elsewhere = set()
    for m in more_refs.modules():
        if m is A:
            continue
        for e in list(m.COLLECTION.pdfs.values()) + list(m.COLLECTION.guides.values()):
            elsewhere.update(x for x in (e.get("archive"), e.get("pdf")) if x)
    elsewhere.update(x for e in sources.PDF_DOCS for x in (e.get("archive"), e.get("pdf")) if x)
    assert not set(mine) & elsewhere, set(mine) & elsewhere
    linked_only = {"ERIC_ED242565", "ERIC_ED241766", "ERIC_ED242563", "ERIC_ED241769", "ERIC_ED241783",
                   "ERIC_ED378400", "ERIC_ED309038", "micro_IA41152941_0223", "ERIC_ED242881"}
    assert not linked_only & set(mine) and not linked_only & elsewhere
    rows = " ".join(r[0] + " " + r[1] for r in A.NOT_INCLUDED)
    for words in ("VITA", "Peace Corps use only", "TM 5-297", "service-skills", "peace-corps", "CC BY-NC-SA",
                  "1 March 1989"):
        assert words in rows, words


def test_index_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    book_fn, sign_fn = A.COLLECTION.makers["index"]
    left_out = []
    book = book_fn("index", "work", None, left_out)
    assert book.pages and book.licence == X.CC0_INDEX and not left_out, left_out
    body = " ".join(p.body for p in book.pages)
    assert '<a href="https://' in body and "never use explosives" in body.lower()
    assert "homestead:epa_private_wells_septic" in body and "power:powell_windmills_wind_motors_1910" in body
    assert sign_fn("index") == sign_fn("index")
    linked = {e[1] for _p, _i, items in A.SECTIONS for e in items}
    assert set(WORDS) <= linked
    assert {f"apt:{e['name']}" for e in A.PDFS} <= linked             # every book is in the index
