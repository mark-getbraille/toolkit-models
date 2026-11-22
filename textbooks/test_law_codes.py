"""Self-test of the United States Code books (law_codes.py), with a MADE-UP title file only: nothing is downloaded.

It checks that every title (and appendix) has a key and the word us-code stays under 256 jobs, that the release
point is read from the download page, that a section page keeps its heading, text, source credit and footnotes but
not the editorial notes, and that the state and municipal codes not built are said with their index addresses.

Run it from the repository's folder:   python3 -m pytest textbooks/test_law_codes.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import law_codes as L  # noqa: E402
import sources  # noqa: E402

TITLE = """<!-- AUTHORITIES-LAWS-ENACTED-THROUGH:119-142 (11/10/2026) -->
<!-- documentid:1_ currentthrough:20261110_119-142 -->
<!-- expcite:TITLE 1-GENERAL PROVISIONS -->
<h1 class="usc-title-head">TITLE 1&mdash;GENERAL PROVISIONS</h1>
<!-- documentid:1_1 currentthrough:20261110_119-142 -->
<!-- expcite:TITLE 1-GENERAL PROVISIONS!@!CHAPTER 1-RULES OF CONSTRUCTION!@!Sec. 1 -->
<!-- field-start:head --><h3 class="section-head">&sect;1. Words denoting number</h3><!-- field-end:head -->
<!-- field-start:statute --><p class="statutory-body">Made-up law text.</p><!-- field-end:statute -->
<!-- field-start:sourcecredit --><p class="source-credit">(July 30, 1947.)</p><!-- field-end:sourcecredit -->
<!-- field-start:notes --><h4 class="note-head">Amendments</h4><p>Editorial note.</p><!-- field-end:notes -->
"""


def test_keys():
    keys = sources.expand_keys(["us-code"])
    assert len(keys) == len(L.TITLES) == 58 <= 256 and "code:usc:05A" in keys and "code:usc:53" not in keys
    assert sources.expand_keys(["code:usc"]) == keys
    assert all(row in sources.NOT_INCLUDED for row in L.NOT_INCLUDED)
    for title, reason in L.NOT_INCLUDED:
        assert "Index: https://" in reason, title


def test_release_point(monkeypatch):
    page = ('<a href="download/releasepoints/us/pl/119/142/htm_usc01@119-142.zip">x</a> The United States Code '
            'Online is current through Public Law 119-142 (November 10, 2026).')
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: page)
    point, through = L.release()
    assert point == "119/142" and through == "Public Law 119-142 (November 10, 2026)"
    assert L.title_url("05A", point).endswith("/119/142/htm_usc05A@119-142.zip")


def test_section_pages():
    pages = L.section_pages(TITLE)
    assert len(pages) == 1
    title, chapter, body = pages[0]
    assert title == "Section 1. Words denoting number" and chapter == "Chapter 1: Rules of construction"
    assert "Made-up law text." in body and "July 30, 1947" in body
    assert "Editorial note." not in body and "section-head" not in body
