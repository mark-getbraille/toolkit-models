"""Self-tests of periodicals.py (reports, journals, news, magazines and history) with made-up answers only: nothing
is downloaded. Every document, article and API answer here is invented for the test.

Run it from the repository's folder:   python3 -m pytest textbooks/test_periodicals.py
"""

import datetime
import gzip
import json
import os
import re
import struct
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import periodicals as P  # noqa: E402

TODAY = datetime.date(2026, 11, 18)


def fake_fetch(routes):
    """A stand-in for build_textbooks.fetch: the answer of the first (piece of address, answer) whose piece is in the
    address; robots.txt and anything else answer 404 (a site without robots.txt allows everything)."""
    def fetch(url, cache=None, binary=False, tries=4):
        """The made-up answer for url."""
        for piece, answer in routes:
            if piece in url:
                if callable(answer):
                    answer = answer(url)
                if binary:
                    return answer if isinstance(answer, bytes) else answer.encode()
                return answer.decode() if isinstance(answer, bytes) else answer
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    return fetch


def use(monkeypatch, routes):
    """Answer every request from routes, with fresh robots.txt records."""
    monkeypatch.setattr(B, "fetch", fake_fetch(routes))
    monkeypatch.setattr(B, "_robots", {})


def words(html_text):
    """The words of some HTML, in order (tags removed, entities read)."""
    import html
    return html.unescape(re.sub(r"<[^>]+>", " ", html_text)).split()


def in_order(needles, haystack):
    """True when every word of needles is in haystack in the same order (nothing left out)."""
    pos = 0
    for w in needles:
        try:
            pos = haystack.index(w, pos) + 1
        except ValueError:
            return False
    return True


# ---------------------------------------------------------------- keys

def test_keys():
    """Words become one key per piece; unknown pieces and sources are ignored; the newspapers have no default
    pieces (they are huge) but can be asked for by state and decade."""
    keys = P.expand_keys(["pub:all"], TODAY)
    assert "pub:crs:2026" in keys and "pub:crs:2023" in keys and "pub:crs:2022" not in keys
    assert "pub:europepmc_reviews:vision" in keys and "pub:voa:recent" in keys
    assert not any(k.startswith("pub:chronicling_america") for k in keys)
    assert P.expand_keys(["pub:news"], TODAY)[0].startswith("pub:global_voices")
    assert P.expand_keys(["pub:history"], TODAY)[0] == "pub:state_milestones:all"
    assert P.expand_keys(["pub:crs:1999x", "pub:nothing", "pub:chronicling_america:vermont-1910s"], TODAY) == \
        ["pub:chronicling_america:vermont-1910s"]
    for spec in P.SOURCES.values():
        assert spec["group"] in P.GROUPS and spec["licence_url"].startswith("https://")
        licence = P.LICENCE_ALIASES.get(spec["licence"], spec["licence"])
        assert B.licence_kind(licence, bool(spec.get("unchanged")))
        if "ND" in licence:
            assert spec.get("unchanged"), "a NoDerivatives source must be kept whole and unchanged"


# ---------------------------------------------------------------- reports: CRS

CRS_CSV = ("number,url,sha1,latestPubDate,title,latestPDF,latestHTML\n"
           "IF00001,reports/IF00001.json,x,2026-11-17,Made-up Brief on Ferries,f.pdf,files/if1.html\n"
           "R00002,reports/R00002.json,x,2026-03-02,Made-up Report on Libraries,f.pdf,files/r2.html\n"
           "R00003,reports/R00003.json,x,2025-12-31,Older Report,f.pdf,files/r3.html\n")
CRS_ROUTES = [
    ("everycrsreport.com/reports.csv", CRS_CSV),
    ("files/if1.html", "<div><div>Made-up Brief on Ferries</div><div>Updated November 17, 2026</div></div>"
                       "<p>Ferries carry people.</p><img src='x.png' alt=''><script>bad()</script>"),
    ("files/r2.html", "<h1>Summary</h1><p>Libraries lend books.</p>"),
]


def test_crs_book(monkeypatch, tmp_path):
    """CRS reports of one year: one page per report under its kind, the date on every page, no scripts, the title
    not repeated; the piece is written as a ZIM file with a catalogue entry in the textbooks' shape."""
    use(monkeypatch, CRS_ROUTES)
    manifests = P.build_periodicals(["pub:crs:2026"], str(tmp_path), today=TODAY, date=TODAY)
    entry = manifests["pub:crs:2026"]["books"][0]
    assert entry["group"] == "reports" and entry["group_name"] == "Reference, government reports"
    assert entry["items"] == 2 and entry["newest"] == "2026-11-17" and entry["oldest"] == "2026-03-02"
    assert entry["published"] == "2026-11-17" and entry["licence_kind"] == "open" and not entry["unchanged"]
    for field in ("id", "name", "title", "licence", "licence_text", "size", "sha256", "article_count", "file",
                  "url", "date", "source"):
        assert field in entry
    path = os.path.join(str(tmp_path), entry["file"])
    with open(path, "rb") as f:
        assert struct.unpack("<I", f.read(4))[0] == 72173914
    assert os.path.exists(os.path.join(str(tmp_path), "manifest-pub_crs_2026.json"))
    book = P.books_for_key("pub:crs:2026", None, [], TODAY)[0]
    first = book.pages[0]
    assert first.unit == "In Focus (two-page briefs)" and book.pages[1].unit == "Reports"
    assert 'Published: <time datetime="2026-11-17">' in first.body and "Ferries carry people." in first.body
    assert "bad()" not in first.body and "<h2>Summary</h2>" in book.pages[1].body
    assert first.body.count("Made-up Brief on Ferries") == 0       # the title is the page's own heading
    assert "not subject to copyright" in book.notice


# ---------------------------------------------------------------- journals: eLife and Europe PMC

ELIFE = json.dumps({"total": 2, "items": [
    {"id": "1", "title": "Made-up digest", "published": "2026-05-01T00:00:00Z", "impactStatement": "In short.",
     "subjects": [{"name": "Neuroscience"}], "relatedContent": [{"id": "1", "title": "Paper", "authorLine": "A et al.",
                                                                  "doi": "10.0/x"}],
     "content": [{"type": "paragraph", "text": "Plain words."},
                 {"type": "image", "image": {"alt": ""}, "caption": [{"type": "paragraph", "text": "A mouse."}]},
                 {"type": "section", "title": "More", "content": [{"type": "paragraph", "text": "Inside."}]}]},
    {"id": "2", "title": "Closed digest", "published": "2026-04-01T00:00:00Z", "content": []},
    {"id": "3", "title": "Old digest", "published": "2025-04-01T00:00:00Z", "content": []}]})


def test_elife(monkeypatch):
    """eLife digests of one year: each digest's article licence is checked; pictures become their caption."""
    use(monkeypatch, [("/digests?", ELIFE),
                      ("/articles/1", json.dumps({"copyright": {"license": "CC-BY-4.0"}, "title": "Paper"})),
                      ("/articles/2", json.dumps({"copyright": {"license": "all-rights-reserved"}}))])
    left = []
    items = P.elife_items(P.SOURCES["elife_digests"], "2026", None, left, TODAY)
    assert [i["title"] for i in items] == ["Made-up digest"] and items[0]["licence"] == "CC BY 4.0"
    body = items[0]["body"]
    assert "<em>In short.</em>" in body and "Picture: A mouse." in body and "<h2>More</h2>" in body
    assert "1 digests were left out" in left[0]["reason"]


def jats(licence_xml, extra=""):
    """A made-up JATS article with the given <license>."""
    return (f'<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><journal-meta><journal-title-group>'
            f'<journal-title>Made-up Journal</journal-title></journal-title-group></journal-meta><article-meta>'
            f'<article-id pub-id-type="doi">10.1/abc</article-id><title-group><article-title>Seeing Well'
            f'</article-title></title-group><contrib-group><contrib contrib-type="author"><name><surname>Doe</surname>'
            f'<given-names>Jan</given-names></name></contrib></contrib-group><pub-date><day>3</day><month>4</month>'
            f'<year>2026</year></pub-date><permissions>{licence_xml}</permissions>'
            f'<abstract><p>Technical abstract.</p></abstract>'
            f'<abstract abstract-type="summary"><title>Author summary</title><p>Plain summary.</p></abstract>'
            f'</article-meta></front><body><sec><title>Introduction</title><p>Eyes need light '
            f'<inline-formula><math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi><mo>+</mo><mn>1</mn>'
            f'</math></inline-formula>.</p><fig><label>Figure 1</label><caption><p>An eye.</p></caption>'
            f'<graphic/></fig>{extra}</sec><sec><title>References</title><ref-list><ref>Old paper</ref></ref-list>'
            f'</sec></body></article>')


def test_jats_and_europepmc(monkeypatch):
    """Europe PMC reviews: only CC BY and CC0 articles (checked in each article's own text), the plain-language
    summary first, formulas as text, figures as their caption, references left out."""
    open_one = jats('<license xlink:href="http://creativecommons.org/licenses/by/4.0/"><license-p>Open'
                    '</license-p></license>')
    nc_one = jats('<license><license-p>Creative Commons Attribution-NonCommercial 4.0 License</license-p>'
                  '</license>')
    search = json.dumps({"resultList": {"result": [
        {"pmcid": "PMC1", "firstPublicationDate": "2026-04-02", "title": "Seeing Well"},
        {"pmcid": "PMC2", "firstPublicationDate": "2026-03-01", "title": "Not open"}]}, "nextCursorMark": "*"})
    use(monkeypatch, [("/search?", search), ("/PMC1/fullTextXML", open_one), ("/PMC2/fullTextXML", nc_one)])
    art = P.jats_article(open_one)
    assert art["licence"] == "CC BY 4.0" and art["authors"] == "Jan Doe" and art["date"] == "2026-04-03"
    assert art["body"].index("Plain summary.") < art["body"].index("Technical abstract.")
    assert "x + 1" in art["body"] and "Figure: Figure 1 An eye." in art["body"] and "Old paper" not in art["body"]
    assert P.open_enough("CC BY 4.0") and P.open_enough("CC0 1.0") and not P.open_enough("CC BY-NC 4.0")
    left = []
    items = P.europepmc_items(P.SOURCES["europepmc_reviews"], "vision", None, left, TODAY)
    assert len(items) == 1 and items[0]["date"] == "2026-04-02" and "Made-up Journal" in items[0]["byline"]
    assert "<h2>References</h2>" not in items[0]["body"]                  # its empty heading is dropped too
    assert "not CC BY or CC0" in left[0]["reason"]


# ---------------------------------------------------------------- news: WordPress, VOA, whole-and-unchanged sources

def wp_posts(*posts):
    """A made-up WordPress REST answer."""
    return json.dumps([{"id": n, "date": d, "link": f"https://news.example.org/{n}", "title": {"rendered": t},
                        "content": {"rendered": c}, "_embedded": {"author": [{"name": "Ana Writer"}]}}
                       for n, (d, t, c) in enumerate(posts, 1)])


def test_global_voices(monkeypatch):
    """Global Voices: the site's licence line is checked; articles republished from partners are left out."""
    use(monkeypatch, [("globalvoices.org/wp-json", wp_posts(
        ("2026-11-02T10:00:00", "Our own story", "<p>Written for us.</p>"),
        ("2026-10-01T10:00:00", "Partner story", "<p>Text.</p><p>This article was originally published by X.</p>"))),
        ("globalvoices.org/", "This site is licensed as "
                              "<a href='https://creativecommons.org/licenses/by/3.0/'>CC</a>")])
    left = []
    books = P.books_for_key("pub:global_voices:2026", None, left, TODAY)
    assert [p.title for p in books[0].pages] == ["Our own story"] and books[0].pages[0].unit == "November 2026"
    assert "By Ana Writer, Global Voices." in books[0].pages[0].body and "partner" in left[0]["reason"]
    assert "News ages fast" in books[0].notice


def test_licence_page_gone(monkeypatch):
    """When a source's licence page no longer says what was checked, the piece is left out."""
    use(monkeypatch, [("globalvoices.org/", "All rights reserved.")])
    left = []
    assert P.books_for_key("pub:global_voices:2026", None, left, TODAY) == []
    assert "no longer states" in left[0]["reason"]


def test_voa(monkeypatch):
    """VOA: only stories of the last 60 days from its sitemaps, without any that names a news agency."""
    sitemap = gzip.compress(
        b'<urlset><url><loc>https://www.voanews.com/a/own/1.html</loc><lastmod>2026-11-10T00:00:00Z</lastmod></url>'
        b'<url><loc>https://www.voanews.com/a/wire/2.html</loc><lastmod>2026-11-11T00:00:00Z</lastmod></url>'
        b'<url><loc>https://www.voanews.com/a/old/3.html</loc><lastmod>2025-01-01T00:00:00Z</lastmod></url></urlset>')

    def story(author, text):
        """A made-up VOA story page."""
        ld = json.dumps({"@type": "NewsArticle", "author": [{"name": author}], "datePublished": "2026-11-10 08:00:00Z"})
        return (f'<script type="application/ld+json">{ld}</script><h1>Headline {author}</h1>'
                f'<div class="wsw"><p>{text}</p><div class="inner"><p>More.</p></div></div><div>Related</div>')
    use(monkeypatch, [("voanews.com/sitemap.xml", "<sitemapindex><sitemap><loc>https://www.voanews.com/"
                       "sitemap_1_1.xml.gz</loc></sitemap></sitemapindex>"),
                      ("sitemap_1_1.xml.gz", sitemap), ("/a/own/1.html", story("Jo Reporter", "Our report.")),
                      ("/a/wire/2.html", story("Jo Reporter", "Some information came from Reuters.")),
                      ("voanews.com/p/5338.html",
                       "produced exclusively by the Voice of America is in the public domain")])
    left = []
    items = P.voa_items(P.SOURCES["voa"], "recent", None, left, TODAY)
    assert [i["title"] for i in items] == ["Headline Jo Reporter"] and items[0]["date"] == "2026-11-10"
    assert "More." in items[0]["body"] and "Related" not in items[0]["body"] and items[0]["byline"] == "By Jo Reporter"
    assert "1 stories with news-agency material" in left[0]["reason"]


ARTICLE = ("<p>First paragraph, with a <a href='https://x.example/'>link</a>.</p><h2>A heading with nothing under "
           "it</h2><h2>Second part</h2><p>Second paragraph &amp; more.</p><ul><li>One</li><li>Two</li></ul>"
           "<figure><img src='p.jpg' alt='A described photo'><figcaption>Photo: Someone</figcaption></figure>"
           "<p>Last words.</p><img src='https://counter.example/c.gif' alt='The Conversation' width='1'>")
FEED = ('<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>An unchanged article</title>'
        '<link rel="alternate" href="https://theconversation.com/an-article-1"/>'
        '<published>2026-11-17T09:00:00Z</published><author><name>Dr A, University of B</name></author>'
        '<content type="html">' + ARTICLE.replace("&", "&amp;").replace("<", "&lt;") + '</content>'
        '<rights>Licensed as Creative Commons – attribution, no derivatives.</rights></entry>'
        '<entry><title>Other licence</title><link rel="alternate" href="https://theconversation.com/x-2"/>'
        '<published>2026-11-16T09:00:00Z</published><content type="html">Hi</content>'
        '<rights>All rights reserved.</rights></entry></feed>')


def test_whole_and_unchanged_never_trimmed(monkeypatch, tmp_path):
    """A NoDerivatives source (The Conversation, CC BY-ND) is kept whole: every word of the article is on its page
    in the same order (even a heading with nothing under it), with the credit, the licence's name and address, the
    original address and "Converted to an accessible format; the text is unchanged."; an entry under another
    licence is left out whole; the catalogue says no-changes."""
    use(monkeypatch, [("theconversation.com/us/articles.atom", FEED),
                      ("republishing-guidelines", "We believe in the free flow of information and publish all our "
                                                  "work under a <a href='/x'>Creative Commons</a> licence")])
    left = []
    book = P.books_for_key("pub:the_conversation:us", None, left, TODAY)[0]
    assert book.unchanged and len(book.pages) == 1 and "1 articles were left out" in left[0]["reason"]
    page = B.page_html(book, book.pages[0])
    original = [w for w in words(ARTICLE)]
    assert in_order(original, words(page)), "a whole-and-unchanged article lost words"
    assert "Picture: A described photo" in page and "A heading with nothing under it" in page
    assert "This article is republished from The Conversation under a Creative Commons license." in page
    assert "CC BY-ND 4.0, no changes allowed" in page and "https://creativecommons.org/licenses/by-nd/4.0/" in page
    assert B.UNCHANGED in page and "https://theconversation.com/an-article-1" in page
    entry = P.build_periodicals(["pub:the_conversation:us"], str(tmp_path), today=TODAY,
                                date=TODAY)["pub:the_conversation:us"]["books"][0]
    assert entry["unchanged"] is True and entry["licence_kind"] == "no-changes"
    assert entry["licence_text"] == "CC BY-ND 4.0, no changes allowed"


def test_clean_keeps_words_when_whole():
    """The cleaner never drops words in whole mode; outside it, only empty headings go."""
    assert in_order(words(ARTICLE)[:-2], words(P.clean(ARTICLE, "https://x.example/", whole=True)))
    assert "nothing under" not in P.clean(ARTICLE, "https://x.example/")


def test_kff_whole_posts(monkeypatch):
    """KFF Health News (CC BY-NC-ND): stories marked "All Rights Reserved" are left out whole, the others kept
    whole with the tagline."""
    tagline = "KFF Health News is a national newsroom that produces in-depth journalism about health issues."
    use(monkeypatch, [("kffhealthnews.org/wp-json", wp_posts(
        ("2026-11-03T05:00:00", "Open story", f"<p>Story text.</p><h3>Empty</h3><p><em>{tagline}</em></p>"),
        ("2026-11-02T05:00:00", "Closed story", "<p>Text.</p><p>All Rights Reserved</p>"))),
        ("kffhealthnews.org/syndication/", "Attribution-NonCommercial-NoDerivatives 4.0 International "
                                           "(CC BY-NC-ND 4.0) license")])
    left = []
    book = P.books_for_key("pub:kff_health_news:2026", None, left, TODAY)[0]
    assert [p.title for p in book.pages] == ["Open story"] and tagline in book.pages[0].body
    assert "<h3>Empty</h3>" in book.pages[0].body and B.UNCHANGED in book.pages[0].body
    assert "This story was produced by KFF Health News." in book.pages[0].body          # the tagline it asks for
    assert "not for commercial use, no changes allowed" in book.pages[0].body
    assert "All Rights Reserved" in left[0]["reason"]


# ---------------------------------------------------------------- history

MILESTONE = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt>
<title type="short">1961–1968</title></titleStmt></fileDesc><revisionDesc><listChange>
<change when="2013-10-31" target="#foreword #made-up-crisis"/></listChange></revisionDesc></teiHeader>
<text><body><div type="section" xml:id="made-up-crisis"><head>The Made-up Crisis<note>A note.</note></head>
<p>It began <persName>somewhere</persName>.<note>Source: invented.</note></p><figure><graphic url="x.jpg"/></figure>
</div></body></text></TEI>"""
FRUS = """<TEI xmlns="http://www.tei-c.org/ns/1.0" xmlns:frus="http://history.state.gov/frus/ns/1.0"><teiHeader>
<fileDesc><titleStmt><title type="complete">Foreign Relations of the United States, Made-up Volume</title>
</titleStmt><publicationStmt><date type="publication-date" when="2020-11-25T16:45:06.000Z"/></publicationStmt>
</fileDesc></teiHeader><text><front><div type="section" subtype="preface" xml:id="preface"><head>Preface</head>
<p>About the volume.</p></div></front><body><div type="compilation"><div type="chapter" xml:id="ch1"><head>A Chapter
</head><div type="document" subtype="historical-document" xml:id="d1" frus:doc-dateTime-min="1962-10-01T00:00:00">
<head>1. Briefing Paper<note type="source">Source: A box.</note></head><opener><dateline><placeName>Washington
</placeName>, <date when="1962-10-01">October 1, 1962</date>.</dateline></opener><list type="subject"><head>SUBJECT
</head><item>Sites</item></list><p>Fifteen sites.<pb n="5"/></p></div></div></div></body></text></TEI>"""


def test_history_tei(monkeypatch, tmp_path):
    """The Office of the Historian's TEI: Milestones essays dated by their revision; FRUS documents dated by their
    own date, under their chapter, with the source note; the volume's title and publication date for the book."""
    repo = tmp_path / "repo"
    (repo / "chapters").mkdir(parents=True)
    (repo / "volumes").mkdir()
    (repo / "chapters" / "1961-1968.xml").write_text(MILESTONE, encoding="utf-8")
    (repo / "volumes" / "frus-madeup.xml").write_text(FRUS, encoding="utf-8")
    monkeypatch.setattr(P, "git_checkout", lambda url, paths, work: str(repo))
    items = P.milestones_items(P.SOURCES["state_milestones"], "all", None, [], TODAY)
    assert items[0]["title"] == "The Made-up Crisis" and items[0]["date"] == "2013-10-31"
    assert items[0]["unit"] == "1961–1968" and "Source: invented." in items[0]["body"]
    assert "A note." not in items[0]["body"].split("<h2>Notes</h2>")[0]
    left = []
    book = P.books_for_key("pub:frus:frus-madeup", None, left, TODAY)[0]
    assert book.title.endswith("Foreign Relations of the United States, Made-up Volume")
    assert book.published == "2020-11-25"
    assert [(p.unit, p.title) for p in book.pages] == [("About this volume", "Preface"),
                                                        ("A Chapter", "1. Briefing Paper")]
    doc = book.pages[1].body
    assert 'Dated: <time datetime="1962-10-01">' in doc and "Source: A box." in doc and "[Page 5]" in doc
    assert "SUBJECT" in doc and "Fifteen sites." in doc


def test_chronicling_america(monkeypatch):
    """Historic newspapers: a sample per year of one state and decade, every page's OCR text, only issues published
    more than 95 years ago and stated to be in the public domain."""
    rights = ["The Library of Congress believes that the newspapers in Chronicling America are in the public domain."]

    def search(url):
        """Two made-up issues a year."""
        year = re.search(r"dates=(\d{4})", url).group(1)
        return json.dumps({"results": [
            {"date": f"{year}-01-05", "title": f"The Made-up Gazette, January 5, {year}",
             "resources": [{"url": f"https://www.loc.gov/resource/sn1/{year}-01-05/ed-1/"}],
             "url": f"https://www.loc.gov/item/sn1/{year}-01-05/ed-1/"}]})

    def resource(url):
        """A two-page issue."""
        n = int(re.search(r"sp=(\d+)", url).group(1))
        return json.dumps({"pagination": {"total": 2}, "item": {"rights": rights},
                           "resource": {"fulltext_file": f"https://tile.loc.gov/text?page={n}"}})
    use(monkeypatch, [("chronicling-america/?", search), ("/resource/", resource),
                      ("tile.loc.gov/text", lambda u: json.dumps({"x": {"full_text": f"PAGE {u[-1]} LINE ONE\n"
                                                                                       "line two\n\nNext para"}}))])
    items = P.chronam_items(P.SOURCES["chronicling_america"], "vermont-1920s", None, [], TODAY)
    assert [i["date"][:4] for i in items] == [str(y) for y in range(1920, 1930)]
    assert "PAGE 1 LINE ONE<br>" in items[0]["body"] and "[Page 2]" in items[0]["body"]
    later = P.chronam_items(P.SOURCES["chronicling_america"], "vermont-1930s", None, [], TODAY)
    assert [i["date"][:4] for i in later] == ["1930"]               # 1931 and after are not yet public domain
    assert P.piece_label("chronicling_america", "new-york-1890s") == "New York, the 1890s"
