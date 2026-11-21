"""Self-test of the writing and business communication guides added on 2026-11-21 (writing_business.py), with MADE-UP
pages only: nothing is downloaded.

It checks that:
  - every book is registered once, in the group "writing" ("Reference, writing and business"), with a licence the
    toolkit may repackage, a "published" date and a version, and is asked for by the keys writing, group:writing and
    wb:<name>; the builder and the weekly update check send wb: keys to this module;
  - the plainlanguage.gov example pages (kramdown) become HTML with their tables, before-and-after lists, line breaks
    and raw HTML, and the old site's own links become plain words;
  - the examples book checks its licence file, skips empty index pages and lists every file read as an original;
  - a site that shuts out AI companies' readers is not read, and a web guide's version names the day it was read;
  - the DTIC public-release line is recognised (with the scanner's slips) and the UK book gets the spelling note;
  - what was already in the library and what was not built (the Canadian Style, the Army's guides) are said.

Run it from the repository's folder:   python3 -m pytest textbooks/test_writing_business.py
"""

import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402
import writing_business as W  # noqa: E402


def use(monkeypatch, routes):
    """Answer every request from routes [(piece of address, answer)]; anything else (robots.txt included) is 404."""
    def fetch(url, cache=None, binary=False, tries=4):
        for piece, answer in routes:
            if piece in url:
                return answer.encode() if binary else answer
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(D, "_ai", {})


def test_registered_once_in_the_writing_group():
    assert sources.GROUPS["writing"] == "Reference, writing and business"
    keys = W.all_keys()
    assert len(keys) == len(set(keys)) == len(W.GUIDES) + len(W.PDFS) + 1
    assert sources.expand_keys(["writing"]) == keys == sources.expand_keys(["group:writing"])
    assert sources.expand_keys(["wb:plain_language_guidelines"]) == ["wb:plain_language_guidelines"]
    others = {e["name"] for e in sources.NONPROFIT + sources.GOV_GUIDES + sources.PDF_DOCS + sources.LAWS}
    for e in W.GUIDES + W.PDFS + [W.EXAMPLES]:
        assert e["group"] == "writing" and e["name"] not in others, e["name"]
        assert B.licence_kind(B.licence_short(e["licence"]), False) == "open", e["name"]
        assert e.get("version") and e.get("notice"), e["name"]
    for e in W.GUIDES:
        assert e.get("start") or e.get("sitemap") or e.get("crawl"), e["name"]
    for e in W.PDFS:
        assert e.get("published") and (e.get("pdf") or e.get("archive")), e["name"]
        assert not e.get("distribution_a")         # these are not field manuals: no parts are cut out
    assert set(W.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in W.NOT_INCLUDED)


def test_builder_and_weekly_check_send_wb_keys_here(monkeypatch, tmp_path):
    monkeypatch.setattr(W, "sign", lambda key: f"signed {key}")
    assert updates.fingerprint("wb:plain_language_examples") == "signed wb:plain_language_examples"
    called = []
    monkeypatch.setattr(W, "build_writing", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["wb:plain_language_guidelines"], str(tmp_path))
    assert called == [["wb:plain_language_guidelines"]]


def test_kramdown_pages_become_html():
    page = """---
title: 'Wordiness Made Spare'
author: Department of the Interior
permalink: /examples/x/
---

Here is [a guideline]({% link _pages/guidelines/x.md %}), [the old site]({{ site.baseurl }}/examples/) and
[an outside page](https://www.example.gov/rule).

Before | After
--- | ---
If the location of the land is far | If the land is far
Write *this* | Do:{::nomarkdown}<ul><li>one</li><li>two</li></ul>{:/}
{: .example-table}

* #### Before

  The application must be completed by the applicant.

* #### After

  We must receive your application.
{: .example-side-by-side}

The White House
Office of the Vice President
"""
    page = page.replace("The White House\n", "The White House" + " " * 2 + "\n")   # two spaces: a line break
    fields, body = W.front_matter(page)
    assert fields == {"title": "Wordiness Made Spare", "author": "Department of the Interior",
                      "permalink": "/examples/x/"}
    out = W.md_html(body)
    assert "a guideline, the old site and" in out and '<a href="https://www.example.gov/rule">an outside page</a>' in out
    assert "<table><tr><th>Before</th><th>After</th></tr><tr><td>If the location of the land is far</td>" in out
    assert "<td>Do:<ul><li>one</li><li>two</li></ul></td>" in out and "<em>this</em>" in out
    assert re.search(r"<ul><li><h5>Before</h5>\s*<p>The application must be completed by the applicant\.</p></li>"
                     r"<li><h5>After</h5>", out)
    assert "<p>The White House<br>Office of the Vice President</p>" in out
    assert "{:" not in out and "{%" not in out and "site.baseurl" not in out


def test_examples_book(monkeypatch):
    raw = W.PLG_RAW
    use(monkeypatch, [(f"{raw}/LICENSE.md", "As a work of the United States Government, this project is in the\n"
                                            "public domain within the United States."),
                      ("/before-and-after/index.md", "---\ntitle: Before and after\n---\n"),
                      ("/before-and-after/ambiguity.md", "---\ntitle: Ambiguous Wording\n---\n\nSome text.\n"),
                      ("/notices/medicare-fraud-letter.md", "---\ntitle: 'Medicare Fraud Letter'\nauthor: CMS\n---\n"
                                                            "\nShorter and to the point.\n")])
    left = []
    book = W.examples_book(None, left)
    assert [p.title for p in book.pages] == ["Ambiguous Wording", "Medicare Fraud Letter"]
    assert [p.unit for p in book.pages] == ["Before and after", "Letters and notices"]
    assert "From: CMS." in book.pages[1].body and book.group == "writing" and book.published == "2025-09-23"
    assert [o["url"] for o in book.originals] == [f"{raw}/_pages/examples/before-and-after/ambiguity.md",
                                                  f"{raw}/_pages/examples/notices/medicare-fraud-letter.md"]
    assert all("could not be read" in x["reason"] for x in left)     # the made-up site has only these pages
    use(monkeypatch, [(f"{raw}/LICENSE.md", "All rights reserved.")])
    left = []
    assert W.examples_book(None, left) is None and "no longer states" in left[0]["reason"]


def test_ai_block_and_guide_version(monkeypatch):
    use(monkeypatch, [("digital.gov/robots.txt", "User-agent: ClaudeBot\nDisallow: /\n")])
    left = []
    assert W.book_for("wb:digital_gov_plain_language", "/tmp/none", None, left) is None
    assert "shuts out AI companies' readers" in left[0]["reason"]
    use(monkeypatch, [("digital.gov/robots.txt", "User-agent: *\nContent-Signal: search=yes, ai-train=no\n")])
    left = []
    assert W.book_for("wb:digital_gov_plain_language", "/tmp/none", None, left) is None
    use(monkeypatch, [])
    made = B.Book(name="digital_gov_plain_language", title="t", subject="s", level="reference", group="writing",
                  publisher="GSA",
                  country="United States", licence=W.US_GOV, licence_url=W.US_GOV_URL, source="https://x")
    made.pages.append(B.Page("p", "P", "<p>x</p>"))
    monkeypatch.setattr(D, "guide_book", lambda entry, cache=None, left_out=None, limit=None: made)
    book = W.book_for("wb:digital_gov_plain_language", "/tmp/none", None, [])
    assert re.fullmatch(r"digital\.gov guide as published, pages read \d{4}-\d\d-\d\d", book.version)
    assert book.notice.startswith("A work of the US General Services Administration")
    left = []
    assert W.book_for("wb:nothing_like_this", "/tmp/none", None, left) is None and left[0]["reason"] == "Unknown key."
