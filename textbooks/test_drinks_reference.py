"""Self-tests of the drinks reference books (textbooks/drinks_reference.py and the group "drinks" of sources.py), with
made-up PDFs only: nothing is downloaded.

They check that the guide puts the legal and safety notes first and never tells a reader to guess an alcohol content;
that every distilling book's description starts with the legal and safety notes; that the old books are before 1931
and say they are old and keep their units; that the keys expand to every drinks book; that the TTB wine manual's
chapters are joined in order; and that a non-US drinks book gets a drinks practice note.

Run from the repository's folder:   python3 -m pytest textbooks/test_drinks_reference.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import drinks_reference as D  # noqa: E402
import sources  # noqa: E402


def test_guide_puts_safety_first():
    book = D.guide_book()
    assert book.group == "drinks" and B.licence_kind(B.licence_short(book.licence)) == "open"
    assert [p.title for p in book.pages][:2] == ["About this book", "Safety and the law first"]
    first = book.pages[1].body
    assert D.ALCOHOL_NOTE in first and D.CAFFEINE_NOTE in first and "26 U.S.C. 5601" in first
    assert "New Zealand" in first and "methanol" in first and "25.205" in first and "24.75" in first
    words = " ".join(p.body for p in book.pages)
    assert "never guess an alcohol content" in words and "51 percent corn" in words
    assert "Contains __ percent juice" in words
    spirits = next(p for p in book.pages if p.title == "Spirits").body
    assert D.DISTILLING_WARNING.split(":")[0] in spirits


def test_drinks_sources():
    drinks = [e for e in sources.PDF_DOCS + sources.GOV_GUIDES + sources.LAWS + sources.LAWS_MORE + sources.NONPROFIT
              if e.get("group") == "drinks"]
    assert "drinks" in sources.GROUPS and len(drinks) >= 35
    old = [e for e in drinks if e.get("old_public_domain")]
    assert len(old) >= 20
    for e in old:
        assert int(e["published"]) < 1931 and "out of date" in e["description"] and "nothing converted" in \
            e["description"]
    distilling = [e for e in old if "distill" in e["subject"].lower() or "Spirits" in e["subject"]]
    assert distilling and all(e["description"].startswith("Legal and safety notes first") for e in distilling)
    for e in sources.NONPROFIT:
        if e.get("group") == "drinks":
            assert e["licence"] == "CC BY-SA 4.0" and B.licence_kind(B.licence_short(e["licence"])) == "share-alike"
    cfr = {e["cfr"]["part"] for e in sources.LAWS + sources.LAWS_MORE if e.get("cfr") and e["group"] == "drinks"}
    assert {4, 5, 7, 16, 19, 24, 25, 120, 146} <= cfr
    fda = next(e for e in sources.GOV_GUIDES if e["name"] == "fda_drink_labels_and_caffeine")
    assert len(fda["urls"]) == 5 and all(__import__("re").match(fda["pages"], u) for u in fda["urls"])
    assert any("BJCP" in name for name, _ in sources.DRINKS_NOT_INCLUDED)
    assert any("Open Food Facts" in name for name, _ in sources.DRINKS_NOT_INCLUDED)


def test_keys_expand():
    keys = sources.expand_keys(["drinks"])
    assert keys[:2] == ["drinks:guide", "drinks:ttb_wine_bam"]
    for key in ("law:cfr_27_5_distilled_spirits_labeling", "law:cfr_27_25_beer", "law:cfr_21_101_food_labeling",
                "law:us_code_26_ch51_distilled_spirits_wines_beer", "guide:ttb_beverage_alcohol_guidance",
                "nonprofit:wikibooks_brewing", "pdf:wahl_henius_handy_book_brewing_1901",
                "pdf:ttb_bam_distilled_spirits"):
        assert key in keys, key
    assert "law:cfr_27_19_distilled_spirits_plants" not in sources.expand_keys(["all"])   # a large part: laws-more


def test_fixed_article_list(monkeypatch):
    entry = dict(next(e for e in sources.GOV_GUIDES if e["name"] == "fda_drink_labels_and_caffeine"))
    plan = B.webguide_plan(entry)
    assert [u for u, _ in plan] == entry["urls"]


def test_wine_manual_chapters_joined(monkeypatch):
    def fake(entry, work, cache=None, left_out=None):
        """A one-page book per chapter; chapter 3 cannot be read."""
        if entry["name"].endswith("_c3"):
            left_out.append({"title": entry["title"], "reason": "no"})
            return None
        book = B.Book(name=entry["name"], title=entry["title"], subject="s", level="reference", group="drinks",
                      publisher="p", country="United States", licence=entry["licence"], licence_url="u",
                      source=entry["page"])
        book.pages = [B.Page("p", f"Pages of {entry['pdf'].rsplit('/', 1)[-1]}", "<p>words</p>", 1)]
        return book
    monkeypatch.setattr(B, "pdfdoc_book", fake)
    left = []
    book = D.wine_bam_book("unused", left_out=left)
    assert book.name == "ttb_bam_wine" and len(book.pages) == 9 and len(left) == 1
    assert book.pages[0].unit == "Chapter 1: Mandatory label information"
    assert book.pages[-1].title == "Pages of c10-sample-wine-labels.pdf" and book.pages[-1].chapter == 10
    assert D.drinks_book("nothing", "unused", left_out=left) is None


def test_practice_note_for_drinks():
    note = sources.practice_note("United Kingdom", "Beer (home brewing)")
    assert note.startswith("UK source: drinking ages") and "New Zealand" in note
    assert "medicine names" in sources.practice_note("United Kingdom", "First aid")
