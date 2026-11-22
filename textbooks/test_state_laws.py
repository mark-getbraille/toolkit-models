"""Self-test of the state law books (state_laws.py, statelaw:), with MADE-UP pages and records only: nothing is
downloaded.

It checks the keys and request words (state-laws, its batches of at most 256 jobs, state-law:<state>), that a chapter
page keeps its text and title without scripts and in its own character set, that chapters are found in the index's
order once each, that South Dakota's chapters come from its title record's links, that the New York sign-up entry
adds nothing without the owner's key and never keeps the key in a book, that every notice says the as-of date and
"not legal advice", and that every state not built is said with its address.

Run it from the repository's folder:   python3 -m pytest textbooks/test_state_laws.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402
import state_laws as S  # noqa: E402


def test_keys_and_words():
    keys = sources.expand_keys(["state-laws"])
    assert keys == S.all_keys() and len(keys) == len(set(keys))
    batches = S.batches()
    assert all(0 < len(v) <= 256 for v in batches.values())
    assert sum((sources.expand_keys([w]) for w in batches), []) == keys
    assert "statelaw:nevada" in keys and "statelaw:georgia:v7a" in keys and "statelaw:new_york" in keys
    assert sources.expand_keys(["state-law:iowa"]) == ["statelaw:iowa"]
    assert sources.expand_keys(["state-law:georgia"]) == sources.expand_keys(["statelaw:georgia"])
    assert sources.GROUPS["statelaw"] == "Reference, state laws"
    assert B.licence_kind(S.STATE_LAW) == "open"
    for s in S.STATES:
        assert s["terms"] and s["site"].startswith("https://") and s["kind"] in ("html", "pdf", "sd_api", "archive",
                                                                                   "nysenate")


def test_html_chapter_and_links(monkeypatch):
    index = ('<a href="NRS-001.html">1</a> <a href="NRS-002.html">2</a> <a href="NRS-001.html">again</a> '
             '<a href="other.html">x</a>')
    chapter = ('<html><head><meta charset="windows-1252"><title>NRS: CHAPTER 1 - MADE-UP COURTS</title></head><body>'
               '<script>junk()</script><p>NRS 1.010 Made-up courts \u2026 shall sit.</p></body></html>').encode("cp1252")

    def fake(url, cache=None, binary=False, tries=4):
        data = chapter if url.endswith("NRS-001.html") else index.encode()
        return data if binary else data.decode("utf-8", "replace")
    monkeypatch.setattr(B, "fetch", fake)
    s = S.STATES_BY_KEY["nevada"]
    assert S.chapter_links(s) == ["https://www.leg.state.nv.us/NRS/NRS-001.html",
                                  "https://www.leg.state.nv.us/NRS/NRS-002.html"]
    title, body = S.html_chapter("https://www.leg.state.nv.us/NRS/NRS-001.html")
    assert title == "CHAPTER 1 - MADE-UP COURTS" and "Made-up courts … shall sit" in body and "junk" not in body


def test_south_dakota_chapters(monkeypatch):
    title = {"Html": '<a href="https://sdlegislature.gov/Statutes/1-1">01</a>'
                     '<a href="https://sdlegislature.gov/Statutes/1-2">02</a>'}
    chapters = {"1-1": {"Html": "<html><body><style>p{}</style><p>1-1-1. Made-up sovereignty.</p></body></html>",
                        "CatchLine": "STATE SOVEREIGNTY", "Repealed": False},
                "1-2": {"Html": "<p>gone</p>", "CatchLine": "REPEALED", "Repealed": True}}

    def fake(url, cache=None, binary=False, tries=4):
        part = url.rsplit("/", 1)[-1]
        return json.dumps(title if part == "1" else chapters[part])
    monkeypatch.setattr(B, "fetch", fake)
    out = S.sd_chapters(dict(S.STATES_BY_KEY["south_dakota"], titles=["1"]), None, [])
    assert [t for t, _b, _u in out] == ["Chapter 1-1. State Sovereignty"]
    assert "Made-up sovereignty" in out[0][1] and "p{}" not in out[0][1]


def test_new_york_sign_up_entry(monkeypatch):
    s = S.STATES_BY_KEY["new_york"]
    monkeypatch.delenv("NYSENATE_API_KEY", raising=False)
    left_out = []
    assert S.ny_laws(s, None, left_out) == [] and "sign" in left_out[0]["reason"] and left_out[0]["fetch_yourself"]
    assert S.state_book("new_york", "work", None, []) is None
    monkeypatch.setenv("NYSENATE_API_KEY", "made-up-key")
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    laws = {"result": {"items": [{"lawId": "ABC", "name": "Made-Up Law"}]}}
    tree = {"result": {"documents": {"docType": "CHAPTER", "title": "Made-Up Law", "documents": {"items": [
        {"docType": "ARTICLE", "docLevelId": "1", "title": "General provisions",
         "documents": {"items": [{"docType": "SECTION", "docLevelId": "1", "text": "Section 1. Made-up words."}]}}]}}}}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4:
                        json.dumps(tree if "/ABC" in url else laws))
    book = S.state_book("new_york", "work", None, [])
    assert book.pages[0].title == "Made-Up Law: Article 1 General provisions"
    assert "Made-up words." in book.pages[0].body
    assert "made-up-key" not in json.dumps(book.originals) and "made-up-key" not in book.source


def test_notice_and_not_included():
    s = S.STATES_BY_KEY["iowa"]
    words = S.notice_for(s, "2026-11-22")
    assert "read 2026-11-22" in words and "not legal advice" in words and "Georgia v. Public.Resource.Org" in words
    rows = " ".join(a + " " + b for a, b in S.NOT_INCLUDED)
    for name in ("Alaska", "Virginia", "Washington", "California", "New York", "Texas", "Florida", "Illinois",
                 "District of Columbia", "Puerto Rico"):
        assert name in rows, name
    for row in S.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
