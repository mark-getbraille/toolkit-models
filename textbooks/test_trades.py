"""Self-test of the trades and workplace safety books (trades.py, trade:), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once with its own group and request words (each at most 256 jobs, the five
themes together making up "trades" with no key in two themes), that its licence lines and NOT_INCLUDED rows (each
with an address) reach sources.py, and that no book repeats a file already in the library; that every book has a
licence the toolkit may repackage, a description and a notice ending with the trade safety words; that the OSHA
booklets say they are older editions from DTIC's copies, the 2025-removed ones name their file in the Internet
Archive item, the old trade books are dated before 1931 and say what is out of date, and the Spanish books are marked
Spanish; that a NIOSH page's own PDF is chosen over its translations and cover letters; that the OSHA standards are
read only from the right CFR volume (made-up govinfo answers) and cut into one page per section; that a NIOSH shelf
finds each part's PDF and leaves out a page without one; and that the index is made offline with keys the library has.

Run it from the repository's folder:   python3 -m pytest textbooks/test_trades.py
"""

import os
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import pdf_set  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402
import thin_topics  # noqa: E402
import trades as T  # noqa: E402

THEMES = ["trade-construction", "trade-industry", "trade-farm", "trade-apprentice", "trade-texts"]


def entries():
    """Every web guide and PDF entry of the module."""
    return list(T.COLLECTION.guides.values()) + list(T.COLLECTION.pdfs.values())


def test_registered_with_its_group_and_words():
    assert more_refs.MODULES.count("trades") == 1 and T in more_refs.modules()
    assert [m for m in more_refs.modules() if m.COLLECTION.prefix == "trade"] == [T]
    assert sources.GROUPS["trades"] == "Reference, trades and workplace safety" == T.GROUPS[T.GROUP]
    everything = sources.expand_keys(["trades"])
    assert 0 < len(everything) == len(set(everything)) <= 256
    assert set(everything) == set(T.COLLECTION.own_keys())
    seen = []
    for word in THEMES:
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        seen += keys
    assert sorted(seen) == sorted(everything)                   # every key in exactly one theme
    assert more_refs.module_for("trade:index") is T and more_refs.module_for("trade-farm") is T
    assert "trade:index" in sources.expand_keys(["trade-apprentice"])
    assert "trade:cfr_29_1926_construction" in sources.expand_keys(["trade-construction"])


def test_records_reach_sources():
    assert set(T.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in T.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    said = " ".join(r[0] + " " + r[1] for r in T.NOT_INCLUDED)
    for words in ("osha.gov", "Outreach", "Susan Harwood", "ai-train=no", "Apprenticeship.gov", "Job Corps",
                  "bls.gov", "Spanish", "no text layer"):
        assert words in said, words


def test_nothing_already_in_the_library_is_repeated():
    have = set()
    for m in more_refs.modules():
        if m is T:
            continue
        for e in m.COLLECTION.pdfs.values():
            have |= {e.get("pdf") or "", e.get("archive") or ""}
    for e in list(sources.PDF_DOCS) + list(thin_topics.PDF_DOCS):
        have |= {e.get("pdf") or "", e.get("archive") or ""}
    have.discard("")
    mine = [e.get("pdf") or e.get("archive") or (e["page"], e["pdf_pattern"]) for e in T.PDFS]
    assert len(mine) == len(set(mine))
    assert not [m for m in mine if m in have]
    for kept_elsewhere in ("DTIC_ADA400342", "DTIC_ADA400348", "DTIC_ADA400134"):   # build: and power: books
        assert kept_elsewhere not in mine


def test_every_book_licence_description_and_safety():
    for g in entries():
        assert g["group"] == "trades" and g["description"] and g["notice"], g["name"]
        short = B.licence_short(g["licence"])
        assert B.licence_kind(short) or B.licence_kind(g["licence"]), g["name"]
        if g["name"] != "bls_occupational_outlook_handbook_2012":    # a careers book: no safety words
            assert T.TRADE_SAFETY in g["notice"], g["name"]
        if g.get("archive", "").startswith("DTIC_ADA"):
            assert "older edition" in g["notice"] or "old edition" in g["notice"], g["name"]
            assert "Defense Technical Information Center" in g["notice"], g["name"]
        if T.REMOVED in (g.get("pdf") or ""):
            assert g["page"] == f"https://archive.org/details/{T.REMOVED}" and "early 2025" in g["notice"], g["name"]
        if g.get("old_public_domain"):
            assert int(g["published"]) < 1931 and "Published in" in g["description"], g["name"]
        if g["name"] in T.COLLECTION.pdfs:
            assert g["published"] and g["version"], g["name"]
        if g.get("licence_page") == T.X.CDC_TERMS:
            assert g["page"].startswith("https://www.cdc.gov/niosh/") and g["pdf_pattern"], g["name"]
    assert T.COLLECTION.guides["wikibooks_welding"]["licence"] == "CC BY-SA 4.0"
    for spec in T.CFR_BOOKS.values():
        assert T.TRADE_SAFETY in spec["notice"] and "not an official version" in spec["notice"]
    spanish = [e["name"] for e in entries() if e.get("language") == "spa"]
    assert sorted(spanish) == ["niosh_2022_102_proteccion_respiratoria_es", "osha_4396_salud_mental_lugar_de_trabajo"]
    electric = T.COLLECTION.pdfs["croft_american_electricians_handbook_1913"]
    assert T.ELECTRICAL_NOTE in electric["notice"]


def test_niosh_page_chooses_its_own_pdf():
    page = ("<a href='x'>x</a>"
            '<a href="/niosh/docs/2010-114/pdfs/2010-114.pdf">English</a>'
            '<a href="/niosh/media/pdfs/2026/04/2010-114hat.pdf">Kreyol</a>'
            '<a href="/niosh/media/pdfs/2026/04/2010-114vie.pdf">Tieng Viet</a>')
    base = T.NIOSH_PAGE.format("2010-114")
    assert B.newest_pdf(page, base, T.niosh_pattern("2010-114")) == \
        "https://www.cdc.gov/niosh/docs/2010-114/pdfs/2010-114.pdf"
    spanish = ('<a href="/niosh/docs/2022-102/pdfs/2022-102revised022022.pdf">a</a>'
               '<a href="/niosh/docs/2022-102/pdfs/2022-102revised022022_SP.pdf">b</a>')
    assert B.newest_pdf(spanish, base, T.niosh_pattern("2022-102")).endswith("2022-102revised022022.pdf")
    entry = T.COLLECTION.pdfs["niosh_2022_102_proteccion_respiratoria_es"]
    assert B.newest_pdf(spanish, base, entry["pdf_pattern"]).endswith("_SP.pdf")
    letter = ('<a href="/niosh/docs/2011-202/pdfs/2011-202.pdf">guide</a>'
              '<a href="/niosh/docs/2011-202/pdfs/NIOSH-OSHA-Nail-Guns-Cover-Letter.pdf">letter</a>')
    assert B.newest_pdf(letter, base, T.niosh_pattern("2011-202")).endswith("/2011-202.pdf")
    for number, name in (("98-126", "CriteriaDoc_98-126.pdf"), ("94-110", "94-110_2021-revision.pdf"),
                         ("2022-123", "2022-123-508.pdf"), ("2015-161", "2015-161Revised022026.pdf")):
        assert B.newest_pdf(f'<a href="/niosh/docs/x/{name}">p</a>', base, T.niosh_pattern(number)), name


# A made-up CFR volume: two sections of a made-up part, the first numbered as the volume's start.
def made_up_cfr(first):
    """The XML of a made-up CFR volume starting at section first."""
    return (f'<?xml version="1.0"?><CFRGRANULE><FDSYS><DATE>2025-07-01</DATE></FDSYS><PART><HD SOURCE="HED">PART '
            f'9999</HD><SUBPART><HD SOURCE="HED">Subpart A-Made-up rules</HD><SECTION><SECTNO>{first}</SECTNO>'
            f'<SUBJECT>Purpose.</SUBJECT><P>Made-up words.</P></SECTION><SECTION><SECTNO>{first}1</SECTNO>'
            f'<SUBJECT>Scope.</SUBJECT><P>More made-up words.</P></SECTION></SUBPART></PART></CFRGRANULE>')


def test_cfr_edition_takes_only_the_right_volume(monkeypatch):
    import datetime
    spec = dict(part=1910, volume=6, first="1910.1000")
    answers = {T.CFR_URL.format(y=2025, v=6, p=1910): made_up_cfr("1910.1"),      # the wrong half of the part
               T.CFR_URL.format(y=2024, v=6, p=1910): made_up_cfr("1910.1000")}

    def fake_fetch(url, cache=None, binary=False, tries=4):
        """govinfo's made-up answers: 404 for a missing edition."""
        if url not in answers:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        return answers[url]
    monkeypatch.setattr(B, "fetch", fake_fetch)
    today = datetime.date(2026, 11, 23)
    url, text = T.cfr_edition(spec, today=today)
    assert url == T.CFR_URL.format(y=2024, v=6, p=1910) and T.first_section(text) == "1910.1000"
    assert T.first_section(made_up_cfr("§ 1926.1")) == "1926.1" and T.first_section("<x/>") == ""
    answers.clear()
    try:
        T.cfr_edition(spec, today=today)
        raise AssertionError("no edition should be found")
    except LookupError:
        pass


def test_cfr_book_one_page_per_section(monkeypatch):
    spec = T.CFR_BOOKS["cfr_29_1928_agriculture"]

    def fake_fetch(url, cache=None, binary=False, tries=4):
        """The made-up licence page and one made-up volume."""
        if url == spec["licence_page"]:
            return "<p>Copyright protection under this title is not available for any work of the United States " \
                   "Government</p>"
        if url == T.CFR_URL.format(y=datetime_year(), v=8, p=1928):
            return made_up_cfr("1928.1")
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    monkeypatch.setattr(B, "fetch", fake_fetch)
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    make, _sign = T.MAKERS["cfr_29_1928_agriculture"]
    left_out = []
    book = make("cfr_29_1928_agriculture", "work", None, left_out)
    assert not left_out and book.name == "trade_cfr_29_1928_agriculture" and book.published == "2025-07-01"
    assert [p.title for p in book.pages] == ["1928.1 Purpose.", "1928.11 Scope."]
    assert book.pages[0].unit.startswith("Subpart A") and book.originals[0]["url"].endswith("part1928.xml")


def datetime_year():
    """This year (the CFR maker tries this year's edition first)."""
    import datetime
    return datetime.date.today().year


def test_shelf_finds_each_part(monkeypatch):
    shelf = dict(T.SHELVES["niosh_farm_safety"])
    pages = {T.NIOSH_PAGE.format("2026-114"): '<a href="/niosh/media/pdfs/2026/08/2026-114.pdf">x</a>',
             T.NIOSH_PAGE.format("2012-167"): '<a href="/niosh/docs/2012-167/pdfs/2012-167.pdf">x</a>',
             T.NIOSH_PAGE.format("2008-144"): "<p>No PDF on this made-up page.</p>"}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: pages[url])
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    left_out = []
    parts = T.shelf_parts(shelf, None, left_out)
    assert [p[1] for p in parts] == ["https://www.cdc.gov/niosh/media/pdfs/2026/08/2026-114.pdf",
                                     "https://www.cdc.gov/niosh/docs/2012-167/pdfs/2012-167.pdf"]
    assert parts[0][0].endswith("(NIOSH 2026-114)") and parts[0][2] == T.NIOSH_PAGE.format("2026-114")
    assert left_out == [{"title": "NIOSH 2008-144", "reason": "Its page links no PDF of it."}]
    got = {}

    def made_up_set(entry, parts, work, cache=None, left_out=None, limit=None):
        """Records what the shelf asks pdf_set for and returns a made-up book."""
        got.update(entry=entry, parts=parts)
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], entry["source"], entry["description"],
                          entry["notice"])
    monkeypatch.setattr(pdf_set, "pdf_set_book", made_up_set)
    make, _sign = T.MAKERS["niosh_farm_safety"]
    book = make("niosh_farm_safety", "work", None, [])
    assert book.name == "trade_niosh_farm_safety" and len(got["parts"]) == 2 and "2 NIOSH" in book.version
    assert got["entry"]["licence_page"] == T.X.CDC_TERMS and T.TRADE_SAFETY in got["entry"]["notice"]
    for name, shelf in T.SHELVES.items():
        numbers = [n for n, _part in shelf["parts"]]
        assert len(numbers) == len(set(numbers)) and shelf["description"], name


def test_index_offline():
    book_fn, sign_fn = T.COLLECTION.makers["index"]
    left_out = []
    book = book_fn("index", "work", None, left_out)
    assert left_out == [], left_out                              # every listed key is in the library
    assert book.licence == "CC0 1.0" and len(book.pages) == len(T.SECTIONS)
    text = " ".join(p.title + " " + p.body for p in book.pages)
    for trade in ("Carpentry", "Electrical", "Plumbing", "HVAC", "Welding", "Masonry", "Roofing", "diesel",
                  "heavy equipment", "Landscaping", "Culinary", "Cosmetology"):
        assert trade in text, trade
    for key in ("build:osha_3150_scaffold_use", "power:osha_controlling_electrical_hazards_1997",
                "edu:apprenticeship_gov", "mw:onet_occupations", "trade:niosh_2009_113_electrical_trades"):
        assert key in text, key
    assert sign_fn("index") == K.sha(T.SECTIONS)
