"""Self-tests of the textbooks builder with a made-up book only (sample_book.py): nothing is downloaded.

Run it from the repository's folder:   python3 -m pytest textbooks/test_textbooks.py
"""

import json
import re
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import sources  # noqa: E402
import mathtext  # noqa: E402
from sample_book import make_sample_repo  # noqa: E402


def test_math_as_text():
    """Formulas become linear text a screen reader and liblouis can read."""
    assert mathtext.latex_text(r"\frac{1 + \sqrt{5}}{2}") == "(1 + sqrt(5))/2"
    assert mathtext.latex_text(r"x^{2} - 4 \ne 0") == "x^2 − 4 ≠ 0"
    assert mathtext.latex_text(r"\text{0,}\dot{3}") == "0,3 recurring"


def test_licences():
    """Licences are read from words and addresses; NoDerivatives is never allowed."""
    assert B.licence_short("Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International") == \
        "CC BY-NC-SA 4.0"
    assert B.licence_short("", "http://creativecommons.org/licenses/by/4.0/") == "CC BY 4.0"
    assert B.licence_short("CC BY NC SA 3.0 IGO") == "CC BY-NC-SA 3.0 IGO"
    assert B.licence_kind("CC BY-ND 4.0") == "" and B.licence_kind("CC BY 4.0") == "open"
    # NoDerivatives only for a work kept whole with its text unchanged (sources.WHOLE_AND_UNCHANGED)
    assert B.licence_kind("CC BY-ND 4.0", whole=True) == "no-changes"
    assert B.licence_kind("CC BY-NC-ND 2.5 AU", whole=True) == "non-commercial-no-changes"
    assert B.licence_kind("W3C Document License") == "" and B.licence_kind("W3C Document License", True)
    assert B.licence_words("CC BY-NC-ND 4.0", True) == "CC BY-NC-ND 4.0, not for commercial use, no changes allowed"
    assert B.licence_words("CC BY-NC-SA 4.0") == "CC BY-NC-SA 4.0, not for commercial use"


def test_sample_book(tmp_path):
    """The made-up book becomes a ZIM file with chapter and section pages, numbered figures, text math, no teacher
    notes, an index page, and a manifest entry with size and SHA-256."""
    repo = make_sample_repo(str(tmp_path / "repo"))
    out = str(tmp_path / "out")
    manifests = B.build([], out, local_osbooks=repo)
    entry = list(manifests.values())[0]["books"][0]
    assert entry["licence"] == "CC BY 4.0" and entry["credit"] == "OpenStax, Rice University"
    path = os.path.join(out, entry["file"])
    assert entry["size"] == os.path.getsize(path) and len(entry["sha256"]) == 64
    assert "published" in entry and "region" in entry
    with open(path, "rb") as f:
        assert struct.unpack("<I", f.read(4))[0] == 72173914
    book = B.osbooks_books(repo)[0]
    titles = [p.title for p in book.pages]
    assert titles == ["Preface", "Chapter 1: The Urinary System", "1.1 The Kidney", "Chapter 2: The Heart",
                      "2.1 The Heart"]
    kidney = book.pages[2].body
    assert "Figure 1.1" in kidney and "A bean-shaped organ" in kidney and "v = d/t" in kidney and "H₂O" in kidney
    assert "SECRET TEACHER TEXT" not in kidney and "Everyday Connection" in kidney
    assert "Table 1.1" in kidney and "Question 1" in kidney and "The nephron." in kidney
    assert 'href="1-1-the-kidney#fig-kidney">Figure 1.1' in book.pages[4].body
    data = B.merge([os.path.join(out, n) for n in os.listdir(out) if n.startswith("manifest-")])
    assert data["books"][0]["name"] == "openstax_tiny_science" and data["not_included"]
    json.dumps(data)


def test_openstax_pinned_to_cc_by_and_personal_use(tmp_path):
    """OpenStax's 2026 change to CC BY-NC-SA: a pinned repository is built from its last CC BY 4.0 commit with that
    commit as its version (openstax.org's catalogue, which describes the newest version, does not change its
    licence); a version under CC BY-NC-SA (in its collection, its LICENSE file or openstax.org's catalogue) is
    labelled personal use only."""
    repo = make_sample_repo(str(tmp_path / "osbooks-tiny"))
    cms = {"tiny-science": {"license_name": "Creative Commons Attribution-NonCommercial-ShareAlike License",
                            "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
                            "book_state": "deprecated", "pdf_url": ""}}
    pin = ("a" * 40, "2026-02-01", "b" * 40, "2026-03-19")
    book = B.osbooks_books(repo, catalogue=cms, pin=pin)[0]
    assert book.licence == "CC BY 4.0" and not book.personal_use and book.version.startswith("GitHub commit aaaa")
    assert book.originals[0]["url"] == f"https://github.com/openstax/osbooks-tiny/archive/{'a' * 40}.zip"
    assert "2026-03-19" in book.description and book.published == "2026-02-01" and not book.original_pdf
    cms["tiny-science"]["book_state"] = "live"
    newest = B.osbooks_books(repo, catalogue=cms)[0]          # the newest version: openstax.org's stricter licence
    assert newest.licence == "CC BY-NC-SA 4.0" and newest.personal_use
    assert newest.licence_url == "https://creativecommons.org/licenses/by-nc-sa/4.0/"
    assert B.licence_words(newest.licence, False, newest.personal_use) == \
        "CC BY-NC-SA 4.0, not for commercial use, personal use only"
    assert B.osbooks_books(repo, only=["another-book"]) == []
    with open(os.path.join(repo, "LICENSE"), "w") as f:      # the repository's own LICENSE file counts too
        f.write("Attribution-NonCommercial-ShareAlike 4.0 International\n\n=====\n")
    assert B.repository_licence(repo) == "CC BY-NC-SA 4.0"
    assert B.osbooks_books(repo)[0].personal_use


def test_openstax_pins_recorded():
    """Every pinned OpenStax repository is one the library builds, with full commit ids and the dates; the weekly
    check does not rebuild a pinned repository; nothing reads openstax.org's archive or book files."""
    import updates
    assert set(sources.OSBOOKS_PINS) <= set(sources.OSBOOKS) and set(sources.OSBOOKS_NEWER) <= set(sources.OSBOOKS_PINS)
    for repo, (commit, date, change, change_date) in sources.OSBOOKS_PINS.items():
        assert re.fullmatch(r"[0-9a-f]{40}", commit) and re.fullmatch(r"[0-9a-f]{40}", change), repo
        assert date < change_date and change_date.startswith("2026-"), repo
    assert updates.fingerprint("osbooks:biology-bundle") == sources.OSBOOKS_PINS["biology-bundle"][0]
    assert "osbooks-new:principles-finance" in sources.expand_keys(["osbooks"])
    here = os.path.dirname(os.path.abspath(__file__))
    for name in os.listdir(here):
        if name.endswith(".py") and not name.startswith("test_"):
            with open(os.path.join(here, name), encoding="utf-8") as f:
                code = f.read()
            assert not re.search(r"openstax\.org/(apps/archive|books/|contents|resources)", code), name


# ---------------------------------------------------------------- non-profit guides and official PDFs (made-up pages)

GUIDE_PAGES = {
    "https://guide.example.org/robots.txt": "User-agent: *\nDisallow: /private/\n",
    "https://guide.example.org/licence": "<p>All our guides are under the Creative Commons Attribution 4.0 "
                                         "International License.</p>",
    "https://guide.example.org/": '<a href="/part/basics">Basics</a> <a href="/private/x">Hidden</a>',
    "https://guide.example.org/part/basics": '<h1>The Basics</h1><a href="/guide/passwords">Passwords</a> '
                                             '<a href="/guide/phishing">Phishing</a> '
                                             '<a href="/private/secret">Secret</a> <a href="/guide/unmarked">U</a>',
    "https://guide.example.org/guide/passwords": (
        '<nav>MENU</nav><div id="main-content"><h1>Strong <small>a subtitle</small>Passwords</h1>'
        '<p class="crumbs">Home &gt; Basics</p>'
        '<h2>Use a manager <a href="#use" aria-hidden="true">#</a></h2><p>See <a href="/guide/phishing">phishing'
        '</a>.</p><img src="dice.png" alt="Five dice showing 6, 2, 4, 1 and 5"><img src="icon.png" alt="">'
        '<a href="#top">Back to Top</a></div><footer>Copyright (CC BY)</footer>'),
    "https://guide.example.org/guide/phishing": '<div id="main-content"><h1>Phishing</h1><p>Check the sender.</p>'
                                                 '<h3><button aria-expanded="false"><span aria-hidden="true">v</span>'
                                                 'If you clicked</button></h3><div id="p"><div aria-hidden="true">'
                                                 '<p>Change your password.</p></div></div>'
                                                 '</div><footer>Copyright (CC BY)</footer>',
    "https://guide.example.org/guide/unmarked": '<div id="main-content"><h1>Unmarked</h1><p>No licence here.</p>'
                                                 '</div><footer>All rights reserved</footer>',
}
GUIDE = {
    "name": "example_guide", "title": "Example Guide", "subject": "Safety", "publisher": "Example Charity",
    "country": "International", "licence": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/",
    "source": "https://guide.example.org/", "description": "A made-up guide.",
    "licence_page": "https://guide.example.org/licence",
    "licence_text": r"Creative Commons Attribution 4\.0 International License", "page_mark": r"Copyright \(CC BY\)",
    "start": ["https://guide.example.org/"], "units": r"^https://guide\.example\.org/part/[a-z]+$",
    "pages": r"^https://guide\.example\.org/(guide|private)/[a-z]+$", "sitemap": "", "unit_rules": [],
    "content": (r'id="main-content"[^>]*>', r"<footer"), "drop": [r'<p class="crumbs">.*?</p>'], "limit": 20,
}


def _fake_fetch(pages):
    """A stand-in for build_textbooks.fetch that answers from a dict (404 for anything else)."""
    import urllib.error

    def fetch(url, cache=None, binary=False, tries=4):
        """The made-up page of url."""
        if url not in pages:
            raise urllib.error.HTTPError(url, 404, "not found", {}, None)
        return pages[url].encode() if binary else pages[url]
    return fetch


def test_webguide_book(monkeypatch):
    """A non-profit guide: parts from its contents page, robots.txt obeyed, pages without the licence line left out,
    menus, hidden marks and "Back to Top" dropped, picture descriptions kept, links pointed at the book's pages, and
    the credit and licence on every page."""
    monkeypatch.setattr(B, "fetch", _fake_fetch(GUIDE_PAGES))
    monkeypatch.setattr(B, "_robots", {})
    left = []
    book = B.webguide_book(GUIDE, None, left)
    assert book.group == "nonprofit" and book.licence == "CC BY 4.0"
    assert [(p.unit, p.title) for p in book.pages] == [("The Basics", "Strong Passwords"), ("The Basics", "Phishing")]
    body = book.pages[0].body
    assert "MENU" not in body and "crumbs" not in body and "Home &gt;" not in body and ">#<" not in body
    assert "Back to Top" not in body and "a subtitle" not in body
    assert "Picture: Five dice showing 6, 2, 4, 1 and 5" in body and 'href="phishing"' in body
    assert any("unmarked" in x["title"] for x in left) and not any("secret" in x["title"] for x in left)
    assert "<h3>If you clicked</h3>" in book.pages[1].body and "Change your password." in book.pages[1].body
    assert "CC BY 4.0" in B.page_html(book, book.pages[1]) and "menus and pictures left out" in B.credit_line(book)
    index = B.index_page(book)
    assert "<h3>The Basics</h3>" in index


def test_webguide_licence_gone(monkeypatch):
    """When the licence page no longer says what was checked, the whole guide is left out."""
    pages = dict(GUIDE_PAGES)
    pages["https://guide.example.org/licence"] = "<p>All rights reserved.</p>"
    monkeypatch.setattr(B, "fetch", _fake_fetch(pages))
    monkeypatch.setattr(B, "_robots", {})
    left = []
    assert B.webguide_book(GUIDE, None, left) is None and "no longer states" in left[0]["reason"]


def test_field_manual_rules():
    """Distribution Statement A is recognised in its printed forms; restricted markings and unsafe parts are not
    allowed; the newest official PDF is chosen."""
    assert B.DISTRIBUTION_A.search("DISTRIBUTION RESTRICTION: Approved for public release; distribution is unlimited.")
    assert B.DISTRIBUTION_A.search("Approved for public release: distribution is unlimited")
    assert B.RESTRICTED.search("DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government agencies")
    assert B.RESTRICTED.search("FOR OFFICIAL USE ONLY") and not B.RESTRICTED.search("DESTRUCTION NOTICE: Destroy")
    assert B.NOT_FIELD_SAFE.search("Chapter 4: Small Arms and Ammunition")
    assert not B.NOT_FIELD_SAFE.search("Chapter 8: Knot Tying and Rope Management")
    page = ('<a href="/d/1/download/guide-2023-04.pdf">old</a><a href="/d/2/download/guide-2026-10.pdf">new</a>'
            '<a href="/d/3/download/guide-2025-03.pdf">x</a>')
    assert B.newest_pdf(page, "https://open.example.ca/p") == "https://open.example.ca/d/2/download/guide-2026-10.pdf"
    assert B.licence_kind(sources.US_GOV) == "open" and B.licence_kind("OGL-Alberta") == "open"
    assert B.without_page_number("Chapter 1: Licensing Information 19") == "Chapter 1: Licensing Information"
    assert B.without_page_number("Chapter 3") == "Chapter 3"


def test_reference_sources():
    """Every non-profit guide and official PDF has a unique name, an allowed licence (never NoDerivatives) and the
    fields the builder needs; field manuals are checked for Distribution Statement A."""
    import sources
    names = [e["name"] for e in sources.NONPROFIT + sources.PDF_DOCS] + [d[2] for d in sources.DSPACE]
    assert len(names) == len(set(names))
    for e in sources.NONPROFIT:
        whole = bool(e.get("unchanged"))         # a no-changes licence, kept whole and unchanged
        licence = e["licence"] if e["licence"] in sources.NO_CHANGES else B.licence_short(e["licence"])
        assert B.licence_kind(licence, whole) and e["content"] and e["licence_text"]
        assert not whole or (B.licence_kind(licence) == "" and not e["drop"])
    for e in sources.PDF_DOCS:
        assert e["group"] in sources.GROUPS
        if e.get("unchanged"):
            assert B.licence_kind(e["licence"], True).endswith("no-changes") and e.get("pdf_licence_text")
            continue
        # Open, or non-commercial and marked personal use only (the K-12 PDFs of 2026-11-21: Utah's science books)
        assert B.licence_kind(e["licence"]) == "open" or (
            B.licence_kind(B.licence_short(e["licence"])) == "non-commercial" and e.get("personal_use"))
        assert e.get("archive") or (e.get("page") and e.get("licence_text"))
        if e.get("archive") and e.get("old_public_domain"):
            assert e["licence"] == "Public domain (published before 1931)" and int(e["published"]) < 1931
        elif e.get("archive"):
            assert e["distribution_a"] and not B.NOT_FIELD_SAFE.search(e["title"])
        if e.get("pdf"):
            assert e["pdf"].startswith("https://") and e.get("licence_page") and e.get("licence_text")


# ---------------------------------------------------------------- publication dates, laws and government guides


def test_dates():
    """Dates written in the usual ways become "YYYY-MM-DD" (or "YYYY-MM", "YYYY"); a web page's own "last reviewed"
    or modified date is found; the newest of several is chosen."""
    assert B.iso_date("2025-04-10T16:00:15+00:00") == "2025-04-10"
    assert B.iso_date("D:20250410120000Z") == "2025-04-10" and B.iso_date("20240103") == "2024-01-03"
    assert B.iso_date("07 April 2025") == "2025-04-07" and B.iso_date("OCT 29, 2026") == "2026-10-29"
    assert B.iso_date("November 2024") == "2024-11" and B.iso_date("(FM 5-125, 1995)") == "1995"
    assert B.iso_date("no date here") == ""
    assert B.page_date('<p>Page last reviewed: 07 April 2025</p>') == "2025-04-07"
    assert B.page_date('<meta name="govuk:public-updated-at" content="2024-11-06T10:53:35+00:00">') == "2024-11-06"
    assert B.page_date('{"dateModified": "2026-05-05T12:00:00Z"}') == "2026-05-05"
    assert B.newest_date(["2024", "", "2025-01-02", "2024-12"]) == "2025-01-02"


CFR_XML = """<?xml version="1.0"?><CFRGRANULE><FDSYS><CFRTITLE>99</CFRTITLE><DATE>2025-07-01</DATE></FDSYS>
<PART><EAR>Pt. 900</EAR><HD SOURCE="HED">PART 900—MADE-UP RULES FOR TESTING</HD>
<CONTENTS><SUBPART><HD SOURCE="HED">Subpart A—General</HD><SECTNO>900.1</SECTNO><SUBJECT>TOC ONLY</SUBJECT>
</SUBPART></CONTENTS>
<AUTH><HD SOURCE="HED">Authority:</HD><P>99 U.S.C. 1.</P></AUTH>
<SUBPART><HD SOURCE="HED">Subpart A—General</HD>
<SECTION><SECTNO>§ 900.1</SECTNO><SUBJECT>What is this part for?</SUBJECT>
<P>(a) It tests the <E T="03">builder</E>.</P><PRTPAGE P="12"/></SECTION>
<SECTION><SECTNO>§ 900.2</SECTNO><SUBJECT>Definitions.</SUBJECT><P>A word means a word.</P>
<GPOTABLE><TTITLE>Table 1—Sizes</TTITLE><BOXHD><CHED>Item</CHED><CHED>Size</CHED></BOXHD>
<ROW><ENT>Cane</ENT><ENT>1 m</ENT></ROW></GPOTABLE></SECTION></SUBPART>
<SUBPART><HD SOURCE="HED">Subpart F—Relay Services</HD>
<SECTION><SECTNO>§ 900.601</SECTNO><SUBJECT>Relay.</SUBJECT><P>Relay text.</P></SECTION></SUBPART>
<APPENDIX><HD SOURCE="HED">Appendix A to Part 900—Forms</HD><P>A form.</P><GPH><GID>X</GID></GPH></APPENDIX>
</PART></CFRGRANULE>"""

LAW_PAGES = {
    "https://law.example.gov/robots.txt": "User-agent: *\nDisallow: /private/\n",
    "https://law.example.gov/policy": "<p>Anyone may copy our laws without charge.</p>",
    "https://law.example.gov/act/full": (
        "<nav>MENU</nav><div id='doc'><p>Act current to 2026-10-29 and last amended on 2024-03-01.</p>"
        "<h1>Made-up Access Act</h1><p>An Act to test the builder, with an introduction long enough to keep as a "
        "page of its own, because it says what the Act is for and who it applies to.</p>"
        "<h2 class='Part'>PART 1 Interpretation</h2><p class='MarginalNote'>Definitions</p><p><strong>1</strong> "
        "In this Act, <a href='#x'>barrier</a> means anything that hinders.</p><div class='note'>EDITORIAL</div>"
        "<h2 class='Part'>PART 2 Duties</h2><h3>(1) Plans</h3><p><strong>2</strong> Everyone must plan.</p>"
        "</div><footer>footer</footer>"),
}
LAW = {
    "name": "madeup_access_act", "title": "Made-up Access Act", "subject": "Disability rights", "group": "law",
    "publisher": "Made-up Justice Department", "country": "Canada", "region": "Testland", "licence": "PD",
    "licence_url": "https://law.example.gov/policy", "licence_page": "https://law.example.gov/policy",
    "licence_text": r"Anyone may copy our laws", "source": "https://law.example.gov/act/full",
    "description": "A made-up law.", "notice": "This copy is not the official version.",
    "urls": ["https://law.example.gov/act/full"], "content": (r"<div id='doc'>", r"<footer"),
    "split": r"<h2 class='Part'", "drop": [r"<div class='note'>.*?</div>"],
    "rewrite": [(r"<h3>(\(\d+\))\s*([^<]*)</h3>", r"<p>\1 \2</p>")],
    "date_pattern": r"last amended on (\d{4}-\d\d-\d\d)",
}


def test_cfr_xml():
    """A CFR part from govinfo's XML: subparts and sections become headings (the table of contents and printed page
    numbers are left out), italics, tables with their title, the authority note and a drawing's place are kept;
    one subpart can be taken alone; the pages are one per section, listed under their subpart."""
    body = B.cfr_xml_html(CFR_XML)
    assert "TOC ONLY" not in body and "Pt. 900" not in body and "MADE-UP RULES" not in body
    assert '<h2 class="cfr-subpart">Subpart A—General</h2>' in body
    assert '<h3 class="cfr-section">§ 900.1 What is this part for?</h3>' in body and "<em>builder</em>" in body
    assert "<caption>Table 1—Sizes</caption>" in body and "<th>Item</th>" in body and "<td>1 m</td>" in body
    assert "Authority: 99 U.S.C. 1." in body and "drawing or formula" in body
    only_f = B.cfr_xml_html(CFR_XML, "F")
    assert "Relay text." in only_f and "900.1" not in only_f
    pages = B.law_pages(body, {"split": r'<h3 class="cfr-section"', "unit": r'<h2 class="cfr-subpart"'})
    titles = [(u, t) for u, t, _b in pages]
    assert ("Subpart A—General", "§ 900.2 Definitions.") in titles
    assert ("Subpart F—Relay Services", "§ 900.601 Relay.") in titles
    assert titles[-1][1].startswith("Appendix A to Part 900")


def test_govinfo_edition(monkeypatch):
    """The newest annual edition is found: missing years (404) are skipped and a volume number one off is tried."""
    import datetime
    year = datetime.date.today().year - 1
    url = f"https://www.govinfo.gov/content/pkg/CFR-{year}-title99-vol3/xml/CFR-{year}-title99-vol3-part900.xml"
    monkeypatch.setattr(B, "fetch", _fake_fetch({url: CFR_XML}))
    assert B.govinfo_edition("cfr", {"title": 99, "volume": 2, "part": 900}) == (url, CFR_XML)
    import pytest
    with pytest.raises(LookupError):
        B.govinfo_edition("usc", {"title": 99, "file": "chap1"})


def test_lawdoc_book(monkeypatch):
    """A law from its official full-text page: the licence page is checked, menus, editorial notes and links are
    left out, one page per part with an introduction, the publication date and region recorded, and the licence's
    notice on the welcome page."""
    monkeypatch.setattr(B, "fetch", _fake_fetch(LAW_PAGES))
    monkeypatch.setattr(B, "_robots", {})
    left = []
    book = B.lawdoc_book(LAW, None, left)
    assert not left and book.group == "law" and book.region == "Testland" and book.published == "2024-03-01"
    assert [p.title for p in book.pages] == ["Introduction", "PART 1 Interpretation", "PART 2 Duties"]
    part1 = book.pages[1].body
    assert "EDITORIAL" not in part1 and "MENU" not in part1 and "<a" not in part1 and "barrier" in part1
    assert "<p>(1) Plans</p>" in book.pages[2].body
    assert "not the official version" in B.index_page(book) and "Published (or last revised): 2024-03-01" in \
        B.index_page(book)
    assert "not an official version" in B.credit_line(book)


def test_lawdoc_licence_gone(monkeypatch):
    """A law whose licence page no longer says what was checked is left out."""
    pages = dict(LAW_PAGES)
    pages["https://law.example.gov/policy"] = "<p>All rights reserved.</p>"
    monkeypatch.setattr(B, "fetch", _fake_fetch(pages))
    monkeypatch.setattr(B, "_robots", {})
    left = []
    assert B.lawdoc_book(LAW, None, left) is None and "no longer states" in left[0]["reason"]


def test_government_guide(monkeypatch):
    """A government guide: its group is its own, pages are found through a sitemap index, a guide's one-page
    "/print" version is read when there is one (else the page itself), and its newest page date is recorded."""
    pages = {
        "https://gov.example.gov/robots.txt": "User-agent: *\nDisallow:\n",
        "https://gov.example.gov/policy": "<p>Our content is in the public domain.</p>",
        "https://gov.example.gov/sitemap.xml": "<sitemapindex><sitemap><loc>https://gov.example.gov/sitemap-1.xml</loc>"
                                               "</sitemap></sitemapindex>",
        "https://gov.example.gov/sitemap-1.xml": "<urlset><url><loc>https://gov.example.gov/help/benefits</loc></url>"
                                                 "<url><loc>https://gov.example.gov/help/taxes</loc></url></urlset>",
        "https://gov.example.gov/help/benefits/print": '<main><h1>Benefits</h1><p>All parts.</p></main>'
                                                       '<p>Page last reviewed: 07 April 2025</p>',
        "https://gov.example.gov/help/taxes": '<main><h1>Taxes</h1><p>One part.</p></main>'
                                              '<meta name="govuk:public-updated-at" content="2026-01-02T00:00:00Z">',
    }
    entry = dict(GUIDE, name="gov_guide", group="consumer", region="", licence="PD",
                 licence_page="https://gov.example.gov/policy", licence_text=r"in the public domain", page_mark="",
                 start=[], units="", pages=r"^https://gov\.example\.gov/help/[a-z]+$",
                 sitemap="https://gov.example.gov/sitemap.xml", content=(r"<main>", r"</main>"),
                 fetch_as=(r"$", "/print"))
    monkeypatch.setattr(B, "fetch", _fake_fetch(pages))
    monkeypatch.setattr(B, "_robots", {})
    left = []
    book = B.webguide_book(entry, None, left)
    assert book.group == "consumer" and [p.title for p in book.pages] == ["Benefits", "Taxes"]
    assert "All parts." in book.pages[0].body and book.published == "2026-01-02"


def test_new_sources():
    """Every law and government guide has a unique name, an allowed licence, a group the toolkit knows, a licence
    page and line to check at every build, and where its text is; the keys expand as the workflow expects."""
    names = [e["name"] for e in sources.NONPROFIT + sources.PDF_DOCS + sources.GOV_GUIDES + sources.LAWS +
             sources.LAWS_MORE] + [d[2] for d in sources.DSPACE]
    assert len(names) == len(set(names))
    for e in sources.LAWS + sources.LAWS_MORE:
        assert e["group"] in sources.GROUPS and B.licence_kind(e["licence"]) == "open"
        assert e["licence_page"].startswith("https://") and e["licence_text"] and e["split"]
        assert e.get("cfr") or e.get("usc") or e.get("urls")
    for e in sources.GOV_GUIDES:
        assert e["group"] in sources.GROUPS
        assert B.licence_kind(e["licence"]) or B.licence_kind(B.licence_short(e["licence"]))
        assert e["licence_page"] and e["licence_text"] and e["content"]
    keys = sources.expand_keys(["all"])
    assert "law:us_code_ada" in keys and "guide:cfpb_ask_cfpb" in keys
    assert not any(k == f"law:{e['name']}" for e in sources.LAWS_MORE for k in keys)
    assert "law:cfr_12_1026_regulation_z" in sources.expand_keys(["laws-more"])
    assert "pdf:medicare_and_you" in sources.expand_keys(["group:health"])


class _FakePdfText:
    """A stand-in for build_textbooks.PdfText: pages of made-up lines."""

    def __init__(self, pages):
        """pages: a list of lists of lines."""
        self.pages, self.count = pages, len(pages)

    def lines(self, n):
        """The lines of page n."""
        return list(self.pages[n])


def test_rulebook_sections():
    """A rulebook kept whole and unchanged is split at its own numbered headings only (contents lines, running heads
    and cross-references are not taken), and its pages read one after another are exactly the whole text."""
    text = _FakePdfText([
        ["Rules of Made-up Braille", "Contents", "Section 1: Introduction ........ 1", "1.1 Basics ......... 1"],
        ["Preface words.", "Section 11: Technical Material summarises things."],
        ["Section 1: Introduction", "1.1 Basics", "Basic rule text.", "• a list item", "1.2 More rules",
         "See Section 2.1 for more."],
        ["Running head 2: Signs", "Section 2: Signs", "2.1 Arrows", "Arrow text.", "3.1 Not a heading yet"],
        ["Appendix 1: Word List", "word one", "Appendix 1: Word List", "word two"],
    ])
    pages = B.section_pages(text)
    titles = [p.title for p in pages]
    assert titles == ["Front matter (pages 1 to 2)", "Section 1: Introduction (page 3)", "1.1 Basics (page 3)",
                      "1.2 More rules (pages 3 to 4)", "Section 2: Signs (page 4)", "2.1 Arrows (page 4)",
                      "Appendix 1: Word List (page 5)"]

    def words(h):
        """The words of some HTML."""
        import html as h2
        return h2.unescape(re.sub(r"<[^>]+>", " ", h)).split()
    whole = words(B.part_html(text, 0, text.count))
    assert words(" ".join(p.body for p in pages)) == whole
    assert "<h3>1.1 Basics</h3>" in pages[2].body and "[Page 3]" in pages[1].body


def test_north_american_animal_sources(monkeypatch):
    """The animal references: NOAA's species directory is a science guide; the old field guides are Internet Archive
    items published before 1931, and one whose record says a later year is left out; no animal drug labels."""
    keys = sources.expand_keys(["group:science"])
    assert "guide:noaa_fisheries_species_directory" in keys and "pdf:reed_bird_guide_land_birds_1909" in keys
    old = [e for e in sources.PDF_DOCS if e.get("old_public_domain")]
    assert len(old) >= 8 and all(e["archive"] and "out of date" in e["description"] for e in old)
    assert not any("dailymed" in str(e).lower() for e in sources.PDF_DOCS + sources.GOV_GUIDES)
    pages = {"https://archive.org/metadata/a": json.dumps({"metadata": {"date": "1909"}}),
             "https://archive.org/metadata/b": json.dumps({"metadata": {"year": ["1952"]}}),
             "https://archive.org/metadata/c": json.dumps({"metadata": {}})}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False: pages[url])
    assert (B.archive_year("a"), B.archive_year("b"), B.archive_year("c")) == (1909, 1952, 0)
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/b/b.pdf",
                                                                     "https://archive.org/details/b"))
    left = []
    entry = dict(old[0], archive="b")
    assert B.pdfdoc_book(entry, "unused", left_out=left) is None
    assert "before 1931" in left[0]["reason"]


def test_practice_notes():
    """A non-US book gets a notice specific to its subject; a US book gets none; every candidate course has the
    fields the gap report and the next session need."""
    assert sources.practice_note("United States", "Electrical wiring") == ""
    note = sources.practice_note("Canada", "Electrical wiring")
    assert note.startswith("Canadian source: wiring rules") and note.endswith("may differ from US practice.")
    assert "medicine names" in sources.practice_note("United Kingdom", "First aid")
    assert "side of the road" in sources.practice_note("Australia", "Automotive service")
    assert "point of view" in sources.practice_note("United Kingdom", "History")
    assert "units (metric)" in sources.practice_note("Ireland", "Music")
    book = B.Book(name="x", title="Physical Sciences Grade 10", subject="Physics and chemistry", level="school",
                  group="textbooks", publisher="P", country="South Africa", licence="CC BY 4.0", licence_url="u",
                  source="s", grades="Grade 10 (South Africa)")
    assert B.practice_note_of(book).startswith("South African source: metric units")
    assert B.practice_note_of(book) in B.index_page(book)
    assert all(len(c) == 6 for c in sources.OPEN_COURSE_CANDIDATES)
    assert all(len(c) == 7 for c in sources.K12_CANDIDATES)


def test_personal_use_labels():
    """Every non-commercial or no-derivatives candidate is labelled personal use only; Khan Academy is never reached
    through its website."""
    for name, licence, route, label, _ in sources.PERSONAL_USE_CANDIDATES:
        if "NC" in licence or "ND" in licence:
            assert label == sources.PERSONAL_USE, name
    khan = next(c for c in sources.PERSONAL_USE_CANDIDATES if c[0].startswith("Khan"))
    assert "khanacademy.org" not in khan[2]
