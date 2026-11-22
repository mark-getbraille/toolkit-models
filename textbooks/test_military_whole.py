"""Self-test of the whole military manuals (military_whole.py, milw:), with MADE-UP part names only: nothing is
downloaded.

It checks the owner's rule of 22 November 2026: the manuals once left out by their title (evasion, SERE, Ranger,
combat, tactics) have keys and are read whole, judged by the release rule (distribution_a); only parts naming
explosives, demolition, mines, grenades or booby traps are cut; the restricted pack animal manuals go to left_out as
personal use and are never built; the request word stays under 256 jobs and every row not built says why with an
address.

Run it from the repository's folder:   python3 -m pytest textbooks/test_military_whole.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import military_whole as M  # noqa: E402
import radio_books  # noqa: E402
import sources  # noqa: E402


def test_keys_and_entries():
    keys = sources.expand_keys(["military-whole"])
    assert 0 < len(keys) == len(M.PDFS) <= 256
    for word in ("sere", "3_02h", "ranger", "seabee", "jungle", "desert", "mountain", "basic_military"):
        assert any(word in k for k in keys), word
    for e in M.PDFS:
        assert e["distribution_a"] is True and e["archive"] and e["group"] == "fieldmanual", e["name"]
        assert e["licence"] == sources.US_GOV and e["work"].startswith("a work of the US"), e["name"]
        assert e["notice"].startswith("The release line before this"), e["name"]
        assert "explosives" in e["notice"] and e["published"] and e["description"], e["name"]
    assert set(M.PERSONAL_USE) <= set(M.COLLECTION.pdfs)
    radio = sources.expand_keys(["radio"])
    assert "radio:army_fm_6_02_53_tactical_radio_2009" in radio and "radio:army_atp_6_02_53_tactical_radios_2025" in radio


def test_only_explosives_parts_are_cut():
    for title in ("Chapter 5: Demolitions", "Chapter 12: Hand Grenades, Land Mines, Trip Flares, And Booby Traps",
                  "Appendix C: Improvised Explosive Devices", "Chapter 9: Sabotage"):
        assert B.NOT_FIELD_SAFE.search(title), title
    for title in ("23. Evasion", "Chapter 8: Battle Drills", "Chapter 10: Machine Gun Employment",
                  "Chapter 3: Service Rifle And Pistol And Marksmanship", "4. The Psychological Aspects of SERE",
                  "Chapter 4. Maneuver", "Chapter 11: Urban Operations"):
        assert not B.NOT_FIELD_SAFE.search(title), title
    keep = M.COLLECTION.pdfs["navy_seabee_combat_handbook_v2_1996"]["keep_parts"]
    assert re.search(keep, "ch CHAPTER 5 COUNTER AMBUSH TECHNIQUES", re.I)
    assert not re.search(keep, "ch CHAPTER 7 LAND MINES AND BOOBY TRAPS", re.I)


def test_restricted_copy_goes_to_left_out(monkeypatch, tmp_path):
    """A made-up restricted front page: the builder puts the manual in left_out as personal use, never a book."""
    entry = dict(M.COLLECTION.pdfs["army_fm_31_27_pack_animals_2000"], licence_page="", licence_text="")
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: (
        "https://archive.org/download/made-up/made-up.pdf", "https://archive.org/details/made-up"))
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    (tmp_path / f"{entry['name']}.pdf").write_bytes(b"%PDF-1.4 made up")

    class Words:
        count = 4

        def __init__(self, path):
            pass

        def lines(self, n):
            return ["Made-up words about packing loads on mules and horses, long enough to count as a text layer."]

    monkeypatch.setattr(B, "PdfText", Words)
    monkeypatch.setattr(B, "front_text", lambda path, pages=12: "FM 31-27 DISTRIBUTION RESTRICTION: Distribution "
                        "restricted to United States (U.S.) Government agencies only.")
    left_out = []
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert left_out and left_out[0]["personal_use"] and left_out[0]["fetch_yourself"]


def test_notice_keeps_the_release_line(monkeypatch):
    import refs_kit as K

    def made_up_book(entry, work, cache=None, left_out=None):
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], "https://archive.org/details/made-up",
                          entry["description"], "Made-up release line. " + entry["notice"])
    monkeypatch.setattr(B, "pdfdoc_book", made_up_book)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    book = M.COLLECTION.book_for("milw:usaf_afh_10_644_sere_2017", "work")
    assert book.notice.startswith("Made-up release line. The release line before this")
    assert book.name.startswith("milw_")


def test_not_included_rows():
    for row in M.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED
        assert "Index: https://" in row[1], row[0]
    rows = " ".join(a + " " + b for a, b in M.NOT_INCLUDED)
    assert "personal use" in rows
    # The 1918 Bluejacket's Manual is no longer left out here: the owner chose to build it whole (knots_military.py).
    assert "bluejacketsmanua0000lieu" not in rows
    assert "kmil:bluejackets_manual_1918" in sources.expand_keys(["knots-military"])
