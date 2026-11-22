"""Self-test of the web-guide modules added on 2026-11-22 (legal_help.py and the modules after it), with MADE-UP
data only: nothing is downloaded.

For every module it checks that each book is registered once under its request word, has a licence the toolkit may
repackage (a no-changes permission only for a book kept whole and unchanged), a notice, a description and a crawl
with a working page pattern; that the books and NOT_INCLUDED reach sources.py; that every row of NOT_INCLUDED says
where to find the source (its index address); and that a crawled address with and without its last "/" is read once.

Run it from the repository's folder:   python3 -m pytest textbooks/test_guide_sources.py
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

GUIDE_MODULES = [m for m in ("legal_help", "money_help", "transport_rights", "gov_help", "work_disability",
                             "civic_help", "family_health", "pets_home", "home_tests")
                 if m in more_refs.MODULES]


def modules():
    """The guide modules that exist."""
    return [m for m in more_refs.modules() if m.__name__ in GUIDE_MODULES]


@pytest.mark.parametrize("m", modules(), ids=lambda m: m.__name__)
def test_books_registered(m):
    c = m.COLLECTION
    word = next(iter(c.words))
    keys = sources.expand_keys([word])
    assert keys == c.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
    for g in c.guides.values():
        whole = bool(g.get("unchanged"))
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, whole), g["name"]
        assert g["notice"] and g["description"] and g["licence_page"] and g["licence_text"], g["name"]
        assert g.get("crawl") or g.get("urls") or g.get("sitemap"), g["name"]
        re.compile(g["pages"])
    assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in m.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_legal_notice_and_permission():
    import legal_help as L
    for g in L.GUIDES:
        assert "not legal advice" in g["notice"] and "vary by state" in g["notice"], g["name"]
    adata = next(g for g in L.GUIDES if g["name"] == "adata_factsheets")
    assert adata["unchanged"] and B.licence_kind(adata["licence"], True) == "no-changes"
    assert not B.licence_kind(adata["licence"], False)
    assert re.search(adata["page_mark"], "May be reproduced and distributed freely with attribution to ADA\n"
                                         "National Network (adata.org)")


def test_crawl_read_once(monkeypatch):
    c = K.Collection("t", "law", guides=[K.guide("law", "x", "X", "s", "p", "https://www.example.gov/a/",
                                                 r"^https://www\.example\.gov/a(/[a-z]+)?/?$", "d", "n")])
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    monkeypatch.setattr(D, "crawl", lambda entry, cache=None, limit=None: [
        ("https://www.example.gov/a", ""), ("https://www.example.gov/a/", ""), ("https://www.example.gov/a/b", "")])
    seen = []
    monkeypatch.setattr(D, "guide_book", lambda entry, cache=None, left_out=None, limit=None:
                        seen.append([u for u, _ in entry["urls"]]))
    c.book_for("t:x", "/tmp/none", None, [])
    assert seen == [["https://www.example.gov/a", "https://www.example.gov/a/b"]]


def test_crisis_lines_are_checked(monkeypatch):
    import family_health as F
    pages = {"https://988lifeline.org/help-yourself/for-deaf-hard-of-hearing/":
             "<p>For TTY Users: Use your preferred relay service or dial 711 then 988.</p><p>text 838255</p>",
             "https://988.ca/": "<p>Old page without the number</p>"}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: pages[url])
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    book = F.crisis_book("crisis_lines", "/tmp/none", None, [])
    body = book.pages[0].body
    assert "call 911" in body and "dial 711 then 988" in body and "text 838255" in body
    assert "could not be checked" in body and "988.ca" in body and "9-8-8 Suicide Crisis Helpline" not in body
    assert book.licence == "CC0" and "Canada not confirmed" in book.version


def test_cdc_books_are_whole_with_cdc_conditions():
    import family_health as F
    cdc = next(g for g in F.GUIDES if g["name"] == "cdc_act_early")
    assert cdc["unchanged"] and cdc["licence_page"] == F.CDC_TERMS
    for words in ("Source: CDC", "free of charge", "does not constitute its endorsement"):
        assert words in cdc["notice"], words
