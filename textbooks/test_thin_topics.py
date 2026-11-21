"""Self-tests of the thin-topic books (textbooks/thin_topics.py, through sources.py), with made-up data only: nothing
is downloaded.

They check that every thin topic got at least three new books (braille: what could be found, with the reasons
recorded); that the keys thin and thin:<topic> expand to pdf:<name> keys the builder knows; that every old book is
from before 1931, is checked as old by the builder and says what is out of date; that the US government books have a
licence line to check and an official address or an Internet Archive copy; that snake books start with the safety
note and navigation books say not to navigate by them; that no name is used twice; that a non-US book gets a
practice notice; and that an old book whose Internet Archive record shows 1931 or later is left out.

Run from the repository's folder:   python3 -m pytest textbooks/test_thin_topics.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import sources  # noqa: E402
import thin_topics as T  # noqa: E402


def test_every_thin_topic_filled():
    for key, (name, before, books) in T.THIN.items():
        assert before <= 3, key
        assert len(books) >= (1 if key == "braille" else 3), key
    assert any("Braille" in title for title, _ in T.NOT_INCLUDED)


def test_keys_expand_to_known_books():
    names = {e["name"] for e in sources.PDF_DOCS}
    keys = sources.expand_keys(["thin"])
    assert len(keys) == len(T.PDF_DOCS) and all(k.startswith("pdf:") and k[4:] in names for k in keys)
    assert sources.expand_keys(["thin:birds"]) == [f"pdf:{e['name']}" for e in T.BIRDS]
    assert "pdf:irs_pub_501" in sources.expand_keys(["all"])
    assert len(names) == len(sources.PDF_DOCS)                      # no name twice


def test_entries_are_complete():
    for e in T.PDF_DOCS:
        assert e["group"] in sources.GROUPS, e["name"]
        assert e.get("archive") or e.get("pdf") or (e.get("page") and e.get("pdf_pattern")), e["name"]
        assert B.licence_kind(B.licence_short(e["licence"])) == "open" or B.licence_kind(e["licence"]) == "open"
        if e.get("old_public_domain"):
            assert int(e["published"]) < 1931 and "an old book" in e["description"], e["name"]
            assert e["archive"] and e["licence"] == T.OLD_LICENCE
        else:
            assert e["licence"] == T.US_GOV and e["licence_page"] == T.GOVINFO_POLICY and e["licence_text"]


def test_safety_and_navigation_notes():
    for e in T.REPTILES:
        if "snake" in e["subject"].lower() or "Reptiles" == e["subject"]:
            assert e["description"].startswith(T.SNAKE_NOTE)
    for e in T.MAPS:
        if "chart" in e["title"].lower() or "Navigator" in e["title"]:
            assert e["description"].endswith(T.NAV_NOTE)
    for e in T.BOATING:
        assert "never use it for navigation" in e["description"]
    for e in T.TAXES:
        assert e["pdf"].startswith("https://www.irs.gov/pub/irs-pdf/p") and "not tax advice" in e["description"]


def test_practice_note_for_british_sailing_books():
    kemp = next(e for e in T.BOATING if e["name"] == "kemp_manual_yacht_boat_sailing_1900")
    assert sources.practice_note(kemp["country"], kemp["subject"], kemp["title"]).startswith("UK source:")


def test_old_book_after_1930_left_out(monkeypatch):
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                     "https://archive.org/details/x"))
    monkeypatch.setattr(B, "archive_year", lambda ident, cache=None: 1933)
    left = []
    assert B.pdfdoc_book(T.BIRDS[0], "unused", left_out=left) is None
    assert "before 1931" in left[0]["reason"]
