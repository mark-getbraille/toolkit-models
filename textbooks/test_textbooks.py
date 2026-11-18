"""Self-tests of the textbooks builder with a made-up book only (sample_book.py): nothing is downloaded.

Run it from the repository's folder:   python3 -m pytest textbooks/test_textbooks.py
"""

import json
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
        assert B.licence_kind(B.licence_short(e["licence"])) and e["content"] and e["licence_text"]
    for e in sources.PDF_DOCS:
        assert e["group"] in ("fieldmanual", "government", "university", "course")
        assert B.licence_kind(e["licence"]) == "open"
        assert e.get("archive") or (e.get("page") and e.get("licence_text"))
        if e.get("archive"):
            assert e["distribution_a"] and not B.NOT_FIELD_SAFE.search(e["title"])
