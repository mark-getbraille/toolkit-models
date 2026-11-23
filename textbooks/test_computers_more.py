"""Self-test of the computers, phones and programming books (computers_more.py) and the two Microsoft books added to
tech_kb.py for them, with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once with its six request words (each at most 256 jobs, every key one the
library has); that every web guide and PDF has a licence the toolkit may repackage, of the kind the module's
docstring says (open, share-alike, or personal use only, the last marked so in its notice), a notice with the computer
and command line safety words, a licence page and line, and a page pattern that matches its own fixed addresses; that
The Linux Command Line is kept whole and unchanged; that no book repeats an address the library already reads; that
the guide comp:index is made offline and lists the Kiwix library's Stack Exchange and Wikibooks entries; that the GNU
manuals' Info reader turns a made-up Info file into pages, links and headings, picks the newest source package from a
made-up folder listing, and keeps ftp.gnu.org's 60-second pause; and that every row of NOT_INCLUDED says where to find
the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_computers_more.py
"""

import io
import os
import re
import sys
import tarfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import tech_kb  # noqa: E402
import computers_more as C  # noqa: E402

WORDS = ("comp-linux", "comp-programming", "comp-windows-basics", "comp-repair-network", "comp-phones", "computers")
OPEN = {"tldp_bash_beginners", "tldp_intro_linux", "tldp_advanced_bash_scripting", "freebsd_handbook",
        "python_tutorial", "python_library", "python_language_howto", "sqlite_docs", "rust_book", "go_docs"}
SHARE_ALIKE = {"debian_administrators_handbook", "debian_installation_guide", "debian_reference",
               "openwrt_user_guide"}
PERSONAL = {"think_python_2e", "automate_boring_stuff_3e", "eloquent_javascript_4e", "pro_git_2e",
            "linux_command_line"}


def entries():
    """Every web guide and PDF entry of the module."""
    return list(C.COLLECTION.guides.values()) + list(C.COLLECTION.pdfs.values())


def test_registered():
    assert C in more_refs.modules() and more_refs.MODULES.count("computers_more") == 1
    assert C.GROUP in sources.GROUPS and set(C.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for name, kind in C.ALLOWED.items():
        assert sources.ALLOWED.get(name) == kind, name
    for w in WORDS:
        keys = sources.expand_keys([w])
        assert keys == C.COLLECTION.expand_keys([w]) and 0 < len(keys) == len(set(keys)) <= 256, w
        assert keys[0] == "comp:index", w
        for key in keys:
            assert X.key_exists(key) or key in C.COLLECTION.own_keys(), (w, key)
    every = set(sources.expand_keys(["computers"]))
    assert set(C.COLLECTION.own_keys()) <= every
    assert {"pcb:libreoffice_writer_guide", "tech:ms_windows_commands", "se:index"} <= every
    assert set(sources.expand_keys(["comp-linux"])) >= {"comp:gnu_bash_manual", "comp:linux_command_line"}
    assert "comp:python_tutorial" in sources.expand_keys(["comp-programming"])
    assert "comp:openwrt_user_guide" in sources.expand_keys(["comp-repair-network"])
    assert "privacy:security_in_a_box" in sources.expand_keys(["comp-phones"])


def test_every_book_licence_and_notice():
    names = {e["name"] for e in entries()}
    assert names == OPEN | SHARE_ALIKE | PERSONAL
    for e in entries():
        whole = bool(e.get("unchanged"))
        kind = B.licence_kind(B.licence_short(e["licence"]), whole)
        if e["name"] in OPEN:
            assert kind == "open" and not e.get("personal_use"), e["name"]
        elif e["name"] in SHARE_ALIKE:
            assert kind == "share-alike" and "keeps that licence" in e["notice"], e["name"]
        else:
            assert kind.startswith("non-commercial") and e["personal_use"], e["name"]
            assert e["notice"].startswith(C.PERSONAL), e["name"]
        assert e["group"] == C.GROUP and e["description"] and e["title"] and e["subject"], e["name"]
        assert e["licence_page"] and e["licence_text"] and e["licence_url"].startswith("https://"), e["name"]
        for words in ("restart it first", "official app store", "as administrator", "keep a backup"):
            assert words in e["notice"], (e["name"], words)
        if e["name"] in C.COLLECTION.guides:
            pattern = re.compile(e["pages"])
            for url in e.get("urls", []):
                assert pattern.match(url), (e["name"], url)
            # the source is a page of the book, or the contents page the crawl starts from
            assert pattern.match(e["source"]) or e["source"] == e["crawl"][0][0], e["name"]
    for name in C.GNU_MANUALS:
        assert f"comp:{name[0]}" in C.COLLECTION.own_keys()


def test_linux_command_line_whole_and_unchanged():
    tlcl = C.COLLECTION.pdfs["linux_command_line"]
    assert tlcl["unchanged"] and tlcl["archive"] and tlcl["pdf_licence_text"]
    assert B.licence_kind(tlcl["licence"], whole=True) == "non-commercial-no-changes"
    assert B.licence_kind(tlcl["licence"]) == ""          # never rearranged
    made_up = ("This work is licensed under the Creative Commons Attribution￾Noncommercial-No Derivative Works "
               "3.0 United States License.")
    assert re.search(tlcl["pdf_licence_text"], made_up)


def test_licence_lines_match_made_up_pages():
    """Each licence line matches the wording its site prints (made-up copies of the sentences)."""
    samples = {
        "tldp_bash_beginners": "* Copyright (c) 2002-2007, Machtelt Garrels * All rights reserved. * Redistribution "
                               "and use in source and binary forms, with or without * modification, are permitted",
        "freebsd_handbook": "Redistribution and use in source (AsciiDoc) and 'compiled' forms (HTML, PDF, EPUB and so "
                            "forth) with or without modification, are permitted",
        "python_tutorial": "Python software and documentation are licensed under the Python Software Foundation "
                           "License Version 2.",
        "go_docs": "Except as noted , the contents of this site are licensed under the Creative Commons Attribution "
                   "4.0 License , and code",
        "openwrt_user_guide": "Except where otherwise noted, content on this wiki is licensed under the following "
                              "license: CC Attribution-Share Alike 4.0 International",
    }
    for name, words in samples.items():
        assert re.search(C.COLLECTION.guides[name]["licence_text"], words), name


def test_no_duplicates_in_the_library():
    ours = {e.get("source") for e in entries()} | {u for e in entries() for u in e.get("urls", [])}
    starts = {s for e in entries() for s, _d in e.get("crawl", [])}
    elsewhere = set()
    for m in more_refs.modules():
        if m is C:
            continue
        for e in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values()):
            elsewhere |= {e.get("source"), e.get("page"), e.get("pdf")} | set(e.get("urls") or [])
            elsewhere |= {s for s, _d in e.get("crawl") or []}
    for e in sources.NONPROFIT + sources.PDF_DOCS + sources.GOV_GUIDES:
        elsewhere |= {e.get("source"), e.get("page"), e.get("pdf")}
    elsewhere.discard(None)
    assert not (ours | starts) & elsewhere
    archives = {e.get("archive") for m in more_refs.modules() if m is not C
                for e in m.COLLECTION.pdfs.values()} | {e.get("archive") for e in sources.PDF_DOCS}
    assert C.COLLECTION.pdfs["linux_command_line"]["archive"] not in archives
    tech_names = [b["name"] for b in tech_kb.BOOKS]
    assert len(tech_names) == len(set(tech_names))
    assert {"ms_windows_commands", "ms_windows_terminal"} <= set(tech_names)


def test_index_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    book_fn, sign_fn = C.COLLECTION.makers["index"]
    left_out = []
    book = book_fn("index", "work", None, left_out)
    assert not left_out and book.licence == X.CC0_INDEX and book.name == "comp_index"
    assert len(book.pages) == len(C.SECTIONS)
    text = " ".join(p.body for p in book.pages)
    for words in ("se:index", "wikibooks_en_all", "developer.mozilla.org_en_all", "archlinux_en_all",
                  "comp:linux_command_line", "tech:ms_windows_commands", "personal use only", "TalkBack"):
        assert words in text, words
    assert sign_fn("index") == sign_fn("index")


MADE_UP_INFO = ("This is demo.info, produced by makeinfo version 7.2 from demo.texi.\n\n"
                "     Permission is granted to copy, distribute and/or modify this\n"
                "     document under the terms of the GNU Free Documentation License,\n"
                "     Version 1.3 or any later version published by the Free Software\n     Foundation.\n"
                "INFO-DIR-SECTION Demo\n\n\x1f\n"
                "File: demo.info,  Node: Top,  Next: Starting,  Up: (dir)\n\nDemo tool\n*********\n\n"
                "The demo tool counts sheep.\n\n* Menu:\n\n* Starting::      How to start it.\n"
                "* Ending: Stopping.  How to stop it.\n\n\x1f\n"
                "File: demo.info,  Node: Starting,  Next: Stopping,  Prev: Top,  Up: Top\n\n1 Starting\n"
                "==========\n\nType this:\n\n     demo --count 3\n     demo --help\n\n"
                "*Note Stopping:: for the other end.\n\n\x1f\n"
                "File: demo.info,  Node: Stopping,  Prev: Starting,  Up: Top\n\n2 Stopping\n==========\n\n"
                "Press Control C.\n\n\x1f\n"
                "File: demo.info,  Node: Index,  Up: Top\n\n\x00\x08[index\x00\x08]\n* Menu:\n\n"
                "* sheep:  Starting.  (line 3)\n\x1f\nTag Table:\nNode: Top\x7f100\n\x1f\nEnd Tag Table\n")


def test_info_reader():
    nodes = C.info_nodes(MADE_UP_INFO)
    assert [n for n, _u, _b in nodes] == ["Top", "Starting", "Stopping"]      # the index node left out
    assert nodes[1][1] == "Top"
    names = {n for n, _u, _b in nodes}
    top = C.info_html(nodes[0][2], names)
    assert "<h2>Demo tool</h2>" in top
    assert '<a href="node-starting">Starting</a> How to start it.' in top
    assert '<a href="node-stopping">Ending</a> How to stop it.' in top
    start = C.info_html(nodes[1][2], names)
    assert "<pre>demo --count 3\ndemo --help</pre>" in start
    assert 'see <a href="node-stopping">Stopping</a>' in start
    assert re.search(C.GNU_LICENCE_TEXT, " ".join(MADE_UP_INFO.split("\x1f", 1)[0].split()))


def test_info_files_from_a_made_up_package(tmp_path):
    """The Info manual is read from the package's doc/ folder, its split parts joined in order."""
    path = tmp_path / "demo-1.0.tar.gz"
    parts = {"demo-1.0/doc/demo.info": "MAIN", "demo-1.0/doc/demo.info-2": "TWO", "demo-1.0/doc/demo.info-1": "ONE",
             "demo-1.0/src/demo.info": "NOT THIS"}
    with tarfile.open(path, "w:gz") as tf:
        for name, text in parts.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    assert C.info_files(str(path), "demo.info") == "MAINONETWO"
    assert C.info_files(str(path), "other.info") == ""


def test_newest_tarball_and_pause(monkeypatch):
    listing = ('<a href="sed-4.8.tar.gz">x</a> <a href="sed-4.10.tar.gz">x</a> <a href="sed-4.10.tar.xz">x</a> '
               '<a href="sed-4.9.tar.xz">x</a> <a href="sed-4.10.tar.xz.sig">x</a>')
    assert C.newest_tarball(listing, "sed") == "sed-4.10.tar.xz"
    assert C.newest_tarball("<a href=\"other-1.0.tar.gz\">", "sed") == ""
    slept, now = [], [1000.0]
    monkeypatch.setattr(C.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(C.time, "sleep", lambda s: slept.append(s))
    monkeypatch.setattr(C, "_gnu_last", [0.0])
    C.gnu_wait()
    now[0] += 5
    C.gnu_wait()
    assert slept == [C.GNU_WAIT - 5] and C.GNU_WAIT >= 60


def test_gnu_book_checks_the_licence(monkeypatch, tmp_path):
    """A package whose Info manual does not carry the GFDL line is left out with the reason (made-up package)."""
    path = tmp_path / "grep-9.9.tar.xz"
    data = MADE_UP_INFO.replace("GNU Free Documentation License", "Some Other License").encode()
    with tarfile.open(path, "w:xz") as tf:
        info = tarfile.TarInfo("grep-9.9/doc/grep.info")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
    monkeypatch.setattr(C.K, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(C, "gnu_listing", lambda package: '<a href="grep-9.9.tar.xz">')
    monkeypatch.setattr(C, "gnu_wait", lambda: None)
    monkeypatch.setattr(C.K, "download_file", lambda url, cache, name=None, max_age_days=None: str(path))
    left_out = []
    assert C.gnu_book("gnu_grep_manual", "work", None, left_out) is None
    assert "no longer states the licence" in left_out[0]["reason"]
    good = tmp_path / "grep-9.9.tar.gz"
    with tarfile.open(good, "w:gz") as tf:
        raw = MADE_UP_INFO.encode()
        info = tarfile.TarInfo("grep-9.9/doc/grep.info")
        info.size = len(raw)
        tf.addfile(info, io.BytesIO(raw))
    monkeypatch.setattr(C.K, "download_file", lambda url, cache, name=None, max_age_days=None: str(good))
    book = C.gnu_book("gnu_grep_manual", "work", None, [], limit=10)
    assert book.licence == C.GFDL and [p.title for p in book.pages][1:] == ["Top", "Starting", "Stopping"]
    assert book.pages[2].unit == "Starting" and C.SAFETY in book.notice


def test_not_included():
    for row in C.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in C.NOT_INCLUDED)
    for words in ("Ubuntu", "Raspberry Pi", "HOWTOs", "Emacs", "MDN", "Apple", "Cisco", "Be Connected",
                  "Open Textbook Library"):
        assert words in names, words
