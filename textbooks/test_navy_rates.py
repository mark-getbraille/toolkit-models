"""Self-test of the US Navy rate training manuals (textbooks/navy_rates.py, rate:), with MADE-UP data only: nothing is
downloaded.

It checks the wiring (the module is registered once with its own group and prefix, and its request words reach
sources.py, each at most 256 jobs, the overall word holding every trade's books); that no Internet Archive item or key
is used twice, here or elsewhere in the library; that every book is judged by the military release rule
(distribution_a, the work of the US Navy) and has a notice naming the Navy, its number, its edition year, public
domain and the copy's source, with its trade's safety note (medicine: "follow current medical guidance"); that only
explosives parts are cut, using made-up part titles; that a made-up restricted front page sends a book to left_out as
personal use, never into a book; that the index links only keys the library has; and that every row of NOT_INCLUDED
says where to look.

Run it from the repository's folder:   python3 -m pytest textbooks/test_navy_rates.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import navy_rates as N  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402


def test_wiring_and_request_words():
    assert more_refs.MODULES.count("navy_rates") == 1 and N in more_refs.modules()
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert prefixes.count("rate") == 1
    assert sources.GROUPS[N.GROUP] == "Reference, Navy rate training manuals"
    assert set(N.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    every = sources.expand_keys([N.WORD])
    assert every[0] == "rate:index" and len(every) == len(set(every)) <= 256
    assert set(every) == {"rate:index"} | {f"rate:{e['name']}" for e in N.PDFS}
    seen = set()
    for trade in N.TRADE_IDS:
        keys = sources.expand_keys([N.TRADE_WORDS[trade]])
        assert keys[0] == "rate:index" and 1 < len(keys) == len(set(keys)) <= 256, trade
        assert set(keys) <= set(every)
        seen |= set(keys)
    assert seen == set(every)
    assert more_refs.module_for("rate:navy_damage_controlman_3_2_1986") is N


def test_every_trade_group_has_books():
    counts = {t: sum(1 for x in N.TRADE_OF.values() if x == t) for t in N.TRADE_IDS}
    assert all(counts.values()), counts
    titles = " ".join(e["title"] for e in N.PDFS)
    for rating in ("Quartermaster", "Signalman", "Damage Controlman", "Machinist's Mate", "Engineman",
                   "Electrician's Mate", "IC Electrician", "Boilerman", "Gas Turbine", "Machinery Repairman",
                   "Opticalman", "Instrumentman", "Builder", "Steelworker", "Utilitiesman", "Equipment Operator",
                   "Construction Electrician", "Engineering Aid", "Construction Mechanic", "Seabee Combat Handbook",
                   "Hospital Corpsman", "Dental", "Standard First Aid", "Mess Management", "Ship's Serviceman",
                   "Storekeeper", "Yeoman", "Journalist", "Draftsman", "Lithographer", "Aviation Machinist's Mate",
                   "Aviation Structural Mechanic", "Aviation Electrician's Mate", "Aviation Boatswain's Mate",
                   "Aerographer's Mate", "Aircrew Survival Equipmentman", "Aviation Support Equipment",
                   "Electronics Technician", "Fire Controlman", "Radioman", "Electronics Installation and Maintenance",
                   "Tools and Their Uses", "Basic Machines", "Fluid Power", "Blueprint", "Mathematics",
                   "Basic Electricity", "Engineering Administration", "Gunner's Mate"):
        assert rating in titles, rating


def test_nothing_used_twice():
    names = [e["name"] for e in N.PDFS]
    archives = [e["archive"] for e in N.PDFS]
    assert len(names) == len(set(names)) and len(archives) == len(set(archives))
    other = set()
    for m in more_refs.modules():
        if m is N:
            continue
        for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values()):
            if g.get("archive"):
                other.add(g["archive"])
    other |= {g["archive"] for g in sources.PDF_DOCS if g.get("archive")}
    assert not set(archives) & other, set(archives) & other
    assert not [a for a in archives if a.startswith("manualzilla")]


def test_release_rule_and_notices():
    for e in N.PDFS:
        assert e["distribution_a"] is True and e["work"] == "a work of the US Navy", e["name"]
        assert e["licence"] == sources.US_GOV and e["group"] == N.GROUP and e["archive"], e["name"]
        notice = e["notice"]
        assert notice.startswith(N.NOTICE_START), e["name"]
        assert f"US Navy, {e['number']}, {e['published']} edition" in notice, e["name"]
        assert "public domain (17 U.S.C. 105)" in notice and "Copy: " in notice and e["archive"] in notice, e["name"]
        assert re.fullmatch(r"(19[2-9]\d|20[0-2]\d)", str(e["published"])), e["name"]
        assert e["description"] and e["title"] and e["subject"], e["name"]
        if N.TRADE_OF[e["name"]] == "medical":
            assert "follow current medical guidance" in notice.lower(), e["name"]
    assert "follow current medical guidance" in N.SAFETY["medical"].lower()
    for words in ("lock out", "safe working load", "1-800-222-1222", "FDA Food Code", "FAA", "911"):
        assert any(words in note for note in N.SAFETY.values()), words
    assert "ERIC document ED132263" in N.COLLECTION.pdfs["navy_quartermaster_3_2_1976"]["notice"]


def test_only_explosives_parts_are_cut():
    for title in ("Chapter 1: Explosives And Pyrotechnics", "Chapter 7: Hand Grenades, Land Mines, And Booby Traps",
                  "Chapter 12: Demolitions", "Appendix C: Improvised Explosive Devices", "Chapter 9: Sabotage"):
        assert B.NOT_FIELD_SAFE.search(title), title
    for title in ("Chapter 6: Gun Mounts", "Chapter 3: Small Arms", "Chapter 4: Fundamentals of Firefighting",
                  "Chapter 7: Lathes and Attachments", "Chapter 5: Wire Rope", "Chapter 9: Diets and Messing",
                  "Chapter 4: Service Rifle and Pistol and Marksmanship", "Chapter 11: Patrols and Ambush"):
        assert not B.NOT_FIELD_SAFE.search(title), title
    keep = N.COLLECTION.pdfs["navy_seabee_combat_handbook_1989"]["keep_parts"]
    assert re.search(keep, "Chapter 15: Land Navigation", re.I)
    assert not re.search(keep, "Chapter 7: Hand Grenades, Land Mines, and Booby Traps", re.I)


def _made_up_pdf(monkeypatch, tmp_path, entry, front):
    """Make the builder read a made-up PDF with the given front pages for entry (nothing is downloaded)."""
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: (
        "https://archive.org/download/made-up/made-up.pdf", "https://archive.org/details/made-up"))
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    (tmp_path / f"{entry['name']}.pdf").write_bytes(b"%PDF-1.4 made up")

    class Words:
        count = 4

        def __init__(self, path):
            pass

        def lines(self, n):
            return ["Made-up words about servicing radar sets and power supplies, long enough to count as text."]

        def raw(self, n):
            return " ".join(self.lines(n))

    monkeypatch.setattr(B, "PdfText", Words)
    monkeypatch.setattr(B, "front_text", lambda path, pages=12: front)
    monkeypatch.setattr(B, "manual_parts", lambda path: [("Chapter 1: Explosives and Pyrotechnics", 0, 2),
                                                         ("Chapter 2: Gun Mounts", 2, 4)])
    monkeypatch.setattr(B, "part_html", lambda text, start, end: "<p>Made-up page.</p>")
    monkeypatch.setattr(B, "file_sha256", lambda path: "0" * 64)
    monkeypatch.setattr(B, "pdf_date", lambda path: "")
    return dict(entry, licence_page="", licence_text="")


def test_restricted_copy_goes_to_left_out(monkeypatch, tmp_path):
    entry = _made_up_pdf(monkeypatch, tmp_path, N.COLLECTION.pdfs["navy_eimb_radar_1974"],
                         "NAVSHIPS 0967-000-0020 FOR OFFICIAL USE ONLY Electronics Installation and Maintenance Book")
    left_out = []
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert left_out and left_out[0]["personal_use"] and left_out[0]["fetch_yourself"]


def test_open_copy_is_built_whole_but_for_explosives(monkeypatch, tmp_path):
    entry = _made_up_pdf(monkeypatch, tmp_path, N.COLLECTION.pdfs["navy_gunners_mate_3_2_1996"],
                         "NONRESIDENT TRAINING COURSE Gunner's Mate 3 & 2 NAVEDTRA 14109 DISTRIBUTION STATEMENT A: "
                         "Approved for public release; distribution is unlimited.")
    left_out = []
    book = B.pdfdoc_book(entry, str(tmp_path), None, left_out)
    assert book is not None and not left_out
    assert [p.title for p in book.pages] == ["Chapter 2: Gun Mounts (pages 3 to 4)"]
    assert "Left out: Chapter 1: Explosives and Pyrotechnics." in book.description
    assert book.notice.startswith("Distribution Statement A") and "NAVEDTRA 14109, 1996 edition" in book.notice


def test_notice_keeps_the_release_line(monkeypatch):
    import refs_kit as K

    def made_up_book(entry, work, cache=None, left_out=None):
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], "https://archive.org/details/made-up",
                          entry["description"], "Made-up release line. " + entry["notice"])
    monkeypatch.setattr(B, "pdfdoc_book", made_up_book)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    book = N.COLLECTION.book_for("rate:navy_mess_management_specialist_3_2_1976", "work")
    assert book.notice.startswith("Made-up release line. " + N.NOTICE_START)
    assert book.name.startswith("rate_") and "Food Code" in book.notice


def test_index_links_existing_books():
    keys = [e[1] for _part, _intro, items in N.SECTIONS for e in items if e[0] == "key"]
    assert keys and all(X.key_exists(k) for k in keys), [k for k in keys if not X.key_exists(k)]
    assert {f"rate:{e['name']}" for e in N.PDFS} <= set(keys)
    linked = " ".join(e[1] for _p, _i, items in N.SECTIONS for e in items)
    for key in ("pdf:navy_neets_module_01", "pdf:navy_basic_machines", "pdf:navy_hospital_corpsman",
                "pdf:navy_culinary_specialist", "build:navy_builder_3_2_1981", "gpo:navy_construction_mechanic_3_2_1978",
                "milw:navy_seabee_combat_handbook_v1_1993", "milw:navy_basic_military_requirements_1992",
                "make:navy_machinery_repairman_1993", "photo:navy_navedtra_14209_photography_basic",
                "kmil:navy_boatswains_mate_2c_1944", "elec:navy_neets_module_18"):
        assert key in linked, key
    words = [e[1] for _p, _i, items in N.SECTIONS for e in items if e[0] == "word"]
    assert N.WORD in words and set(N.TRADE_WORDS.values()) <= set(words)
    for _p, _i, items in N.SECTIONS:
        for e in items:
            if e[0] == "link":
                assert e[2].startswith(("https://", "http://")) and e[3], e
    book, _sign = N.INDEX
    built = book("index", "work", None, [], None)
    assert len(built.pages) == len(N.SECTIONS) == len(N.TRADES) + 1 and built.licence == "CC0 1.0"


def test_not_included():
    for row in N.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    rows = " ".join(a + " " + b for a, b in N.NOT_INCLUDED)
    for words in ("Lending-library", "manualzilla", "CONFIDENTIAL", "Mineman", "netc.navy.mil"):
        assert words in rows, words
