"""Self-test of the NVDA, NVDA add-on, liblouis and AEM Center books (at_docs.py), with MADE-UP files only: nothing
is downloaded.

It checks that the GNU licences are allowed as share-alike, an NVDA document is split into a page per chapter with
its release as the version, an add-on's licence words are sorted into the right book (and a closed one into none),
its read-me addresses are tried on raw.githubusercontent.com, a liblouis table's header becomes its page (metadata
and copyright, not its rules), and the sites not read are said with their index addresses.

Run it from the repository's folder:   python3 -m pytest textbooks/test_at_docs.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import at_docs as A  # noqa: E402
import build_textbooks as B  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402


def test_registered_and_licences():
    keys = sources.expand_keys(["at-docs"])
    assert len(keys) == 10 and "atdoc:liblouis_tables" in keys and "atdoc:aem_center" in keys
    for short in (A.GPL2, A.GPL3, A.LGPL):
        assert B.licence_kind(short, False) == "share-alike", short
    assert B.licence_kind("CC BY-SA 4.0", False) == "share-alike"
    assert all(row in sources.NOT_INCLUDED for row in A.NOT_INCLUDED)
    assert any("ai-train=no" in r for _t, r in A.NOT_INCLUDED)


def test_nvda_document_split(monkeypatch):
    doc = ('<html><body><h1 id="nvda-1">NVDA 2026.3.1 User Guide</h1><p>Intro words.</p>'
           '<h2 id="intro">1. Introduction</h2><p>NVDA is a screen reader.</p>'
           '<h2 id="start">2. Getting started</h2><p>Press control+alt+n.</p></body></html>')
    answers = {A.NVDA_COPYING: "NVDA is available under the GNU General Public License version 2 or later, with",
               f"{A.NVDA_DOCS}/userGuide.html": doc}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: answers[url])
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(K, "last_modified", lambda url: "2026-11-01")
    book = A.nvda_doc_book("nvda_user_guide", "/tmp/none", None, [])
    assert [p.title for p in book.pages] == ["Introduction", "1. Introduction", "2. Getting started"]
    assert book.version == "NVDA 2026.3.1 User Guide" and book.published == "2026-11-01"
    assert book.licence == A.GPL2 and "GNU General Public License" in book.notice
    answers[A.NVDA_COPYING] = "All rights reserved"
    left = []
    assert A.nvda_doc_book("nvda_user_guide", "/tmp/none", None, left) is None and left


def test_addon_licences_and_readmes():
    assert A.licence_family("GPL v2") == A.licence_family("GNU General Public License v2.0 or later") == "gpl2"
    assert A.licence_family("GPL v3") == A.licence_family("MIT license") == A.licence_family("Apache v2") == "open"
    assert A.licence_family("Freeware") == "" and A.licence_family("LGPL 2.1") == ""
    assert A.readme_urls("https://github.com/someone/myAddon.git")[0] == \
        "https://raw.githubusercontent.com/someone/myAddon/HEAD/readme.md"
    assert A.readme_urls("https://www.nvda.it/x") == []


def test_table_page(monkeypatch):
    table = ("# liblouis: Made-up braille (grade 1)\n#\n#-name: Made-up braille\n#-display-name: Made-up "
             "uncontracted\n#+language:xx\n#+type:literary\n#+grade:1\n#\n#  Copyright (C) 2026 Nobody\n#\n"
             "#  under the terms of the GNU Lesser General Public License as\n#  published by the Free Software "
             "Foundation, either version 2.1 of the\nsign a 1\n")
    answers = {A.LIBLOUIS_TEXI: "GNU Lesser (or library) General Public License",
               f"{A.TABLES}/Makefile.am": "table_files = \\\n\txx-g1.utb \\\n\txx-chars.uti\n",
               f"{A.TABLES}/xx-g1.utb": table, f"{A.TABLES}/xx-chars.uti": "sign b 12\n"}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: answers[url])
    book = A.tables_book("liblouis_tables", "/tmp/none", None, [])
    first = book.pages[0]
    assert first.title == "Made-up uncontracted (xx-g1.utb)" and first.unit == "Language: xx"
    assert "<dd>literary</dd>" in first.body and "Copyright (C) 2026 Nobody" in first.body
    assert "version 2.1 or later" in first.body and "sign a 1" not in first.body
    assert book.pages[1].unit.startswith("Tables without a language")


def test_split_html():
    parts = K.split_html("<body><h1>T</h1><h2 id='a'>A</h2><p>x</p><h2>B</h2><p>y</p></body>")
    assert [(t, i) for t, i, _b in parts] == [("A", ""), ("B", "")] or [t for t, _i, _b in parts] == ["A", "B"]
