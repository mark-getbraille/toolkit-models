"""Self-test of the radio communications books (radio_books.py), with MADE-UP data only: nothing is downloaded.

It checks that every book is registered once under its request word "radio" (at most 256 jobs) in its own group
"Reference, radio communications" (not the preparedness group); that every book has a licence the toolkit may
repackage (the NCVEC public-domain release and Meshtastic's GPL-3.0 are added to ALLOWED) and a notice with the radio
safety words (power lines, towers, lightning and grounding, RF exposure, transmit only where licensed, no encryption
on amateur frequencies); that a made-up NCVEC page gives its FIRST pool PDF (the newest release); that the owner's
military publication rule is followed on made-up front pages (Distribution A said; no statement kept with the truthful
words; a restricted marking personal use; a classified marking out unless declassified); that the link book records no
originals; that no Internet Archive item is already a book of another module; and that every row of NOT_INCLUDED says
where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_radio_books.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import radio_books as R  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def test_registered():
    assert "radio_books" in more_refs.MODULES and R in more_refs.modules()
    assert sources.GROUPS["radio"] == "Reference, radio communications"
    keys = sources.expand_keys(["radio"])
    assert keys == R.all_keys() and len(keys) == len(set(keys)) <= 256
    assert all(k.startswith("radio:") for k in keys)
    assert not set(keys) & set(sources.expand_keys(["disasters"]) + sources.expand_keys(["preparedness"]))
    assert set(R.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in R.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    for name in ("radio:cfr_47_97_amateur", "radio:ncvec_technician_pool", "radio:meshtastic_docs",
                 "radio:usmc_mcrp_3_40_3c_antenna_handbook", "radio:links_to_fetch_yourself"):
        assert name in keys


def test_safety_words_and_licences():
    for words in ("power lines", "tower", "lightning", "Ground", "RF exposure", "licensed", "encryption", "911"):
        assert words in R.RADIO_SAFETY, words
    for entry in R.GUIDES + R.PDFS + [R.pool_entry(p[0]) for p in R.POOLS] + R.MILITARY_MANUALS:
        assert entry["group"] == "radio", entry["name"]
        assert R.RADIO_SAFETY in entry["notice"], entry["name"]
        short = B.licence_short(entry["licence"])
        assert B.licence_kind(short) or B.licence_kind(entry["licence"]), entry["name"]
        assert entry["licence_page"] and entry["licence_text"] and entry["description"], entry["name"]
    assert sources.ALLOWED[R.NCVEC_PD] == "open" and sources.ALLOWED["GPL-3.0"] == "share-alike"
    mesh = R.COLLECTION.guides["meshtastic_docs"]
    pattern = re.compile(mesh["pages"])
    assert pattern.match("https://meshtastic.org/docs/configuration/radio/channels/")
    assert not pattern.match("https://meshtastic.org/docs/2.7/configuration/radio/channels/")
    assert not pattern.match("https://meshtastic.org/docs/development/firmware/build/")
    assert "share-alike" in mesh["notice"] and "902 to 928 MHz" in mesh["description"]


def test_first_pool_pdf():
    page = ('<p><a href="http://ncvec.org/downloads/General Class Pool and Syllabus 2023-2027 Public Release with 6th '
            'Errata Feb 4 2026.pdf">new</a> <a href="http://ncvec.org/downloads/General Class Pool and Syllabus '
            '2023-2027 Public Release with 5th Errata Nov 8 2024.pdf">old</a> <a href="/downloads/G7-1.pdf">x</a>')
    pdf = R.first_pdf(page, "https://www.ncvec.org/index.php/x", R.POOLS[1][4])
    assert "6th%20Errata" in pdf and " " not in pdf
    assert R.first_pdf("<p>none</p>", "https://www.ncvec.org/", R.POOLS[1][4]) == ""
    text = "The NCVEC Question Pool Committee hereby releases into public domain the 2023-2027 General pool."
    assert re.search(R.NCVEC_TEXT, text)
    text = "The NCVEC Question Pool Committee (QPC) hereby releases the 2026-2030 Technician Class (Element 2) " \
           "Question Pool into the public domain."
    assert re.search(R.NCVEC_TEXT, text)


def test_military_rule():
    assert R.military_verdict("FM 1 DISTRIBUTION RESTRICTION: Approved for public release; distribution is "
                              "unlimited.") == "public"
    assert R.military_verdict("MCRP 3-40.3C Antenna Handbook U.S. Marine Corps PCN 144") == "none"
    restricted = ("DISTRIBUTION RESTRICTION: Distribution authorized to U.S. Government agencies and their "
                  "contractors only")
    assert R.military_verdict(restricted) == "restricted"
    assert R.military_verdict("SECRET Radio Set handbook") == "out"
    assert R.military_verdict("CONFIDENTIAL Declassified by order of the Secretary") == "declassified"
    assert "print no distribution statement" in R.military_notice("none", "")
    assert "approved for public release" not in R.military_notice("none", "").lower()
    assert R.military_notice("restricted", restricted).startswith("PERSONAL USE ONLY")
    assert "Distribution Statement A" in R.military_notice("public", "")
    for m in R.MILITARY_MANUALS:
        assert m["military"] and m["archive"] and m["licence"] == sources.US_GOV, m["name"]


def test_military_book_marks_restricted_personal(monkeypatch, tmp_path):
    """A made-up manual whose front page prints a restricted marking is kept as personal use, with its explosives part
    left out; a classified one is refused."""
    book = B.Book(name="radio_x", title="X", subject="s", level="reference", group="radio", publisher="p",
                  country="United States", licence=sources.US_GOV, licence_url="u", source="s", description="d")
    book.pages = [B.Page("a", "Chapter 1 Antennas", "<p>x</p>"), B.Page("b", "Chapter 2 Demolitions", "<p>y</p>")]
    monkeypatch.setattr(B, "pdfdoc_book", lambda entry, work, cache=None, left_out=None: book)
    monkeypatch.setattr(B, "front_text", lambda path: "Distribution authorized to DoD components only")
    out = R.military_book("usmc_mcrp_3_40_3c_antenna_handbook", str(tmp_path), None, [])
    assert out.personal_use and out.notice.startswith("PERSONAL USE ONLY") and len(out.pages) == 1
    monkeypatch.setattr(B, "front_text", lambda path: "SECRET")
    left = []
    assert R.military_book("usmc_mcrp_3_40_3c_antenna_handbook", str(tmp_path), None, left) is None and left


def test_links_book():
    book = R.links_book("links_to_fetch_yourself", "/tmp/none", None, [])
    assert len(book.pages) == len(R.LINK_ONLY) and book.originals == [] and R.RADIO_SAFETY in book.notice
    titles = " ".join(t for t, _w, _x, _u in R.LINK_ONLY)
    for words in ("ARRL", "AREDN", "Reticulum", "JS8Call", "Winlink", "APRS", "CHIRP", "Briar", "MeshCore",
                  "goTenna", "inReach", "HaLow", "NTIA", "ISED", "FCC"):
        assert words in titles, words


def test_no_archive_item_is_another_modules_book():
    others = ""
    for name in os.listdir(HERE):
        if name.endswith(".py") and name != "radio_books.py" and not name.startswith("test_"):
            with open(os.path.join(HERE, name), encoding="utf-8") as f:
                others += f.read()
    for entry in R.PDFS + R.MILITARY_MANUALS:
        if entry.get("archive"):
            assert f'"{entry["archive"]}"' not in others, entry["name"]
