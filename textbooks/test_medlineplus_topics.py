"""Self-test of the MedlinePlus books (medlineplus_topics.py), with MADE-UP pages only: nothing is downloaded.

It checks that every book is a public-domain part of MedlinePlus with its own licence line and NLM's credit, that the
topic pages' address pattern leaves out the encyclopedia, drug information, lists and the XML files, that only the
"Summary" block of a topic page is kept, and that the copyrighted parts are said in NOT_INCLUDED with their index.

Run it from the repository's folder:   python3 -m pytest textbooks/test_medlineplus_topics.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import medlineplus_topics as M  # noqa: E402
import sources  # noqa: E402


def test_registered():
    keys = sources.expand_keys(["medlineplus"])
    assert keys == [f"mlp:{g['name']}" for g in M.GUIDES] and len(keys) == 6
    for g in M.GUIDES:
        assert g["licence_page"] == M.LICENCE_PAGE and g["notice"].startswith(M.CREDIT), g["name"]
        assert B.licence_kind(B.licence_short(g["licence"]), False) == "open"
        assert g.get("crawl") and g["pages"]
    assert all(row in sources.NOT_INCLUDED for row in M.NOT_INCLUDED)


def test_topic_addresses():
    pages = re.compile(M.GUIDES[0]["pages"])
    assert pages.match("https://medlineplus.gov/asthma.html")
    for url in ("https://medlineplus.gov/healthtopics_a.html", "https://medlineplus.gov/encyclopedia.html",
                "https://medlineplus.gov/ency/article/000141.htm", "https://medlineplus.gov/druginfo/meds/a1.html",
                "https://medlineplus.gov/xml/mplus_topics_2026-11-21.xml", "https://medlineplus.gov/sitemap.html",
                "https://medlineplus.gov/spanish/asma.html"):
        assert not pages.match(url), url
    assert re.compile(M.GUIDES[1]["pages"]).match("https://medlineplus.gov/spanish/asma.html")


def test_only_the_summary_is_kept():
    page = ('<h1>Asthma</h1><div id="encyclopedia-box">Licensed text</div>'
            '<div id="topic-summary" class="syndicate"><h3>What is asthma?</h3><p>A lung disease.</p></div>'
            '<section id="related-topics">Links</section>')
    body = B.article_content(page, M.GUIDES[0])
    assert "A lung disease." in body and "Licensed text" not in body and "Links" not in body
    for row in ("A.D.A.M. Medical Encyclopedia", "MedlinePlus drug information"):
        assert any(t.startswith(row) and "Index: https://" in r for t, r in M.NOT_INCLUDED), row
