"""Self-tests of directory_sources.py and directory_pubs.py (the reference-directory repositories) with made-up
pages and records only: nothing is downloaded (build_textbooks.fetch is replaced by a dictionary of made-up answers).
They check that a site blocking AI companies' readers (by name, Claude-User included, or with ai-train=no) is never
read; that links are found in any element's href and pages are grouped into parts; that the Federal Register's XML,
Wikinews' wikitext, Raspberry Pi's Markdown and the Global Digital Library's H5P books become plain HTML with their
words unchanged; that a volume of the Encyclopaedia Britannica is cut into pages and carries the old-book and non-US
notes; that the journals' pieces stay small enough; that OAI-PMH licences, the Internet Archive's rules and the
personal-use marks are right; that the keys reach the builder and the weekly check; and that all 80 personal-use
repositories are accounted for.

Run it from the repository's folder:   python3 -m pytest textbooks/test_directory_sources.py
"""

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import periodicals as P  # noqa: E402
import directory_pubs as DP  # noqa: E402
import sources  # noqa: E402


def fake_fetch(pages):
    """A stand-in for build_textbooks.fetch that answers from a dictionary (404 for anything else)."""
    import urllib.error

    def fetch(url, cache=None, binary=False, tries=4):
        if url not in pages:
            raise urllib.error.HTTPError(url, 404, "not found", {}, None)
        data = pages[url]
        if binary:
            return data if isinstance(data, bytes) else data.encode("utf-8")
        return data if isinstance(data, str) else data.decode("utf-8")
    return fetch


def test_ai_refused_by_name_and_signal(monkeypatch):
    monkeypatch.setattr(D, "_ai", {})
    monkeypatch.setattr(B, "fetch", fake_fetch({
        "https://a.example/robots.txt": "User-agent: *\nAllow: /\n\nUser-agent: Claude-User\nDisallow: /\n",
        "https://b.example/robots.txt": "User-agent: *\nContent-Signal: search=yes,ai-train=no\nAllow: /\n",
        "https://c.example/robots.txt": "User-agent: *\nContent-Signal: search=yes,ai-train=yes\nDisallow: /admin\n",
        "https://d.example/robots.txt": "<html><body>Not a robots file</body></html>"}))
    assert D.ai_refused("https://a.example/page")             # CareerOneStop's kind of block
    assert D.ai_refused("https://b.example/page")             # ai-train=no
    assert not D.ai_refused("https://c.example/page")
    assert not D.ai_refused("https://d.example/page")         # a web page instead of robots.txt: no rules
    assert not D.ai_refused("https://e.example/page")         # no robots.txt at all


def test_any_links_and_crawl(monkeypatch):
    hub = ('<a href="/benefits/one/">One</a><va-link href="/benefits/two/" text="Two"></va-link>'
           '<a href="/benefits/apply-for-form-1/">Form</a><a href="https://other.example/x">Away</a>')
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", fake_fetch({"https://www.example.gov/benefits/": hub}))
    links = D.any_links(hub, "https://www.example.gov/benefits/")
    assert "https://www.example.gov/benefits/two/" in links          # a web component's href is a link too
    entry = dict(pages=r"^https://www\.example\.gov/benefits/(?![a-z0-9/-]*form)[a-z0-9/-]*$",
                 crawl=[("https://www.example.gov/benefits/", 1)], follow=r"$^",
                 unit_rules=[(r"/two/", "Second part"), (r".", "First part")], urls=[], limit=10)
    found = D.crawl(entry)
    assert ("https://www.example.gov/benefits/two/", "Second part") in found
    assert all("form" not in u for u, _ in found)


def test_guides_are_complete():
    for g in D.GUIDES:
        for field in ("name", "title", "subject", "group", "publisher", "country", "licence", "licence_url", "source",
                      "description", "licence_page", "licence_text", "pages", "content"):
            assert g.get(field), (g["name"], field)
        assert g["group"] in sources.GROUPS
        assert g.get("sitemap") or g.get("crawl") or g.get("urls")
    assert D.GUIDES_BY_NAME["nei_eye_health_spanish"]["language"] == "spa"


def test_fr_rule_html():
    xml = """<FEDREG><RULES><RULE><PREAMB><AGENCY TYPE="S">DEPARTMENT OF TRANSPORTATION</AGENCY>
    <CFR>14 CFR Part 382</CFR><SUBJECT>Accessible Air Travel</SUBJECT><SUM><HD SOURCE="HED">SUMMARY:</HD>
    <P>This rule makes <E T="03">lavatories</E> accessible.</P></SUM></PREAMB><SUPLINF><HD SOURCE="HD1">Background</HD>
    <P>Text<PRTPAGE P="123"/> goes on.</P><GPOTABLE><TTITLE>Costs</TTITLE><BOXHD><CHED>Year</CHED><CHED>Cost</CHED>
    </BOXHD><ROW><ENT>2026</ENT><ENT>$1</ENT></ROW></GPOTABLE></SUPLINF>
    <FRDOC>[FR Doc. 2026-12345 Filed 11-19-26; 8:45 am]</FRDOC></RULE></RULES></FEDREG>"""
    import xml.etree.ElementTree as ET
    rule = ET.fromstring(xml).find(".//RULE")
    item = DP.fr_rule_item(rule, "2026-11-20", "FR-2026-11-20")
    assert item["title"] == "Accessible Air Travel" and item["url"] == "https://www.federalregister.gov/d/2026-12345"
    assert item["unit"] == "Department Of Transportation"
    body = item["body"]
    assert "<h2>SUMMARY:</h2>" in body and "<em>lavatories</em>" in body and "<h3>Background</h3>" in body
    assert "<th>Year</th>" in body and "<td>$1</td>" in body and "Text goes on." in body


def test_wikinews_html():
    text = ("{{date|March 3, 2010}}\n{{Wikinewsie}}\n'''Rome''' — A [[w:Pope|pope]] spoke [http://x.org today].\n\n"
            "== Sources ==\n{{source|url=http://news.example/a|title=Pope speaks|pub=Example News|date=2010-03-03}}\n"
            "[[Category:Italy]]\n{{publish}}")
    date, html = DP.wikinews_html(text)
    assert date == "2010-03-03"
    assert "<strong>Rome</strong> — A pope spoke today." in html
    assert "<h2>Sources</h2>" in html and "Pope speaks, Example News, 2010-03-03 (http://news.example/a)" in html
    assert "Category" not in html and "Wikinewsie" not in html


def test_markdown_html():
    md = ("## Make it move\n\nUse **Python** and [the guide](https://x.org){:target=\"_blank\"}.\n\n--- task ---\n"
          "Add the code:\n--- code ---\n---\nlanguage: python\n---\nprint('hi')\n--- /code ---\n--- /task ---\n"
          "![A green circle](images/c.png)\n")
    html = D.markdown_html(md)
    assert "<h3>Make it move</h3>" in html and "<strong>Python</strong>" in html
    assert '<a href="https://x.org">the guide</a>.' in html and "{:" not in html
    assert "<p><strong>Task:</strong></p>" in html and "<pre>print(&#x27;hi&#x27;)</pre>" in html
    assert "language: python" not in html and "(Picture: A green circle)" in html


def test_h5p_text():
    import io
    import zipfile
    content = {"chapters": [{"metadata": {"title": "Page 1"}, "params": {"content": [
        {"content": {"params": {"file": {"path": "a.jpg"}, "alt": "A boy reads"}}},
        {"content": {"params": {"text": "<p>I like to read.</p>"}}}]}}]}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("content/content.json", json.dumps(content))
    pages = D.h5p_text(buf.getvalue())
    assert pages and pages[0][0] == "Page 1" and "I like to read." in pages[0][1] and "A boy reads" in pages[0][1]


def test_eb_volume_pages_and_notes():
    text = "\n\n".join(["ABACUS, an instrument for counting. " * 2000, "BABEL, a tower. " * 400])
    pages = D.eb_volume_pages(text, "Volume 1, A-B", 1, "Volume 1, A-B")
    assert len(pages) >= 2 and pages[0].title.startswith("Volume 1, A-B, part 1 (from Abacus")
    assert "out of date" in D.EB_NOTE and "OCR" in D.EB_NOTE


def test_journal_pieces_are_small():
    today = datetime.date(2026, 11, 21)
    pieces = DP.journal_pieces("frontiers_public_health", today)
    assert pieces[0] == "2026-11" and "2019-q4" in pieces and "2014" in pieces
    assert DP.piece_dates("2026-q3") == ("2026-07-01", "2026-09-30")
    assert DP.piece_dates("2024-02") == ("2024-02-01", "2024-02-29")
    assert all(p <= "2026-11" for p in pieces)


def test_licences_and_rules():
    assert DP.oai_licence({"rights": ["http://creativecommons.org/licenses/by/4.0/"]})[0] == "CC BY 4.0"
    assert DP.journal_open("CC BY 4.0") and not DP.journal_open("CC BY-NC 4.0")
    assert DP.journal_personal("CC BY-NC-SA 4.0") and not DP.journal_personal("CC BY-NC-ND 4.0")
    assert DP.ia_item_allowed({"year": "1925"}, "old")[0] and not DP.ia_item_allowed({"year": "1931"}, "old")[0]
    ok, lic, _ = DP.ia_item_allowed({"creator": "United States. Veterans Administration", "year": "1960"}, "usgov")
    assert ok and lic == sources.US_GOV
    ok, lic, _ = DP.ia_item_allowed({"creator": "A private author", "year": "1960"}, "usgov")
    assert not ok
    ok, lic, _ = DP.ia_item_allowed({"licenseurl": "http://creativecommons.org/licenses/by-nd/4.0/"}, "open")
    assert not ok                                             # no-derivatives items are not taken
    assert B.licence_kind(DP.CROWN_NC) == "non-commercial"


def test_personal_marks():
    assert P.SOURCES["dsq"]["personal_use"] and P.SOURCES["dsq"]["unchanged"]
    assert P.SOURCES["jnl_indian_journal_ophthalmology"]["personal_use"]
    assert not P.SOURCES["jnl_bmc_public_health"].get("personal_use")
    assert P.SOURCES["ia_wellcomelibrary"]["personal_use"] and not P.SOURCES["ia_americana"]["personal_use"]
    book = P.make_book("dsq", "2026", [P.item("https://dsq-sds.org/article/id/1/", "A", "2026-01-02", "<p>x</p>",
                                              "January 2026", licence="CC BY-NC-ND 4.0",
                                              licence_url="https://creativecommons.org/licenses/by-nc-nd/4.0/")])
    assert book.personal_use and book.unchanged
    assert "personal use only" in B.licence_words(book.licence, book.unchanged, book.personal_use)


def test_keys_reach_the_builder(monkeypatch):
    keys = sources.expand_keys(["directory"])
    assert len(keys) <= 256                                     # one workflow run
    assert "dir:nei_eye_health" in keys and "dir:storyweaver:english-1" in keys
    assert "pub:federal_register_rules:" + DP._months_back(2025)[0] in keys
    assert any(k.startswith("pub:jnl_bmc_public_health:") for k in keys)
    assert not any(k.startswith("pub:dsq:") for k in keys)       # personal use only: asked for separately
    monkeypatch.setattr(D, "oyc_courses", lambda cache=None: ["https://oyc.yale.edu/astronomy/astr-160"])
    personal = sources.expand_keys(["directory-personal"])
    assert "dir:open_yale_courses:astr-160" in personal and any(k.startswith("pub:dsq:") for k in personal)
    assert sources.expand_keys(["dir:encyclopaedia_britannica"])[0] == "dir:encyclopaedia_britannica:eb-1"
    assert P.expand_keys(["pub:ia_americana:cookery-2"]) == ["pub:ia_americana:cookery-2"]
    import updates
    monkeypatch.setattr(D, "sign", lambda key: "sign-of-" + key)
    assert updates.fingerprint("dir:oeis:3") == "sign-of-dir:oeis:3"
    assert updates.pub_sign("pub:federal_register_rules:2001-05") == "closed"


def test_personal_list_is_complete():
    assert len(D.PERSONAL) == 80
    built = [row for row in D.PERSONAL if row[2].startswith("Built")]
    assert len(built) >= 12 and all(":" in row[2] for row in built)
    assert any("Print Disabilities" in n for n, _w in D.OWNER_NOTES)
    names = [n for n, _r in DP.NOT_INCLUDED + D.NOT_INCLUDED]
    assert any("AHRQ" in n for n in names) and any("CareerOneStop" in n for n in names)


def test_directory_all_chunks():
    keys = sources.expand_keys(["directory-all:federal_register_rules:1"])
    assert len(keys) == 200 and keys[0].startswith("pub:federal_register_rules:")
    rest = sources.expand_keys(["directory-all:federal_register_rules:2"])
    assert rest and not set(rest) & set(keys) and rest[-1] == "pub:federal_register_rules:2000-01"
    assert sources.expand_keys(["directory-all:oeis"])[-1] == "dir:oeis:39"
