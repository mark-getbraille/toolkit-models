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
    assert "pub:state_milestones:all" in P.expand_keys(["pub:history"], TODAY)
    voa = [k for k in keys if k.startswith("pub:voa:")]
    assert voa == ["pub:voa:recent", "pub:voa:2026", "pub:voa:2025", "pub:voa:2024"]          # older years by key
    assert "pub:voa_history:1975-01" in keys and "pub:voa_learning:2026" in keys
    assert P.expand_keys(["pub:voa:2001", "pub:voa:1994", "pub:voa:1996", "pub:voa_history:1940s"], TODAY) == \
        ["pub:voa:2001", "pub:voa:1996", "pub:voa_history:1940s"]
    assert P.expand_keys(["pub:the_conversation:us-2015", "pub:europepmc_reviews:vision-2010"], TODAY) == \
        ["pub:the_conversation:us-2015", "pub:europepmc_reviews:vision-2010"]
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


def test_elife_from_europepmc(monkeypatch):
    """eLife digests come from Europe PMC (eLife's own API host disallows all robots): only the digest of each
    CC BY paper, with the paper's credit; papers without a digest, or under another licence, are left out."""
    with_digest = jats('<license xlink:href="http://creativecommons.org/licenses/by/4.0/"><license-p>Open'
                       '</license-p></license>').replace('abstract-type="summary"><title>Author summary',
                                                         'abstract-type="plain-language-summary"><title>eLife digest')
    no_digest = jats('<license xlink:href="http://creativecommons.org/licenses/by/4.0/"><license-p>Open'
                     '</license-p></license>').replace('<abstract abstract-type="summary"><title>Author summary'
                                                       '</title><p>Plain summary.</p></abstract>', '')
    search = json.dumps({"resultList": {"result": [
        {"pmcid": "PMC7", "firstPublicationDate": "2025-06-01"},
        {"pmcid": "PMC8", "firstPublicationDate": "2025-05-01"}]},
        "nextCursorMark": "*"})
    use(monkeypatch, [("/search?", search), ("/PMC7/fullTextXML", with_digest), ("/PMC8/fullTextXML", no_digest)])
    assert "elifesciences" not in json.dumps(P.SOURCES["elife_digests"], default=str)
    items = P.elife_digest_items(P.SOURCES["elife_digests"], "2025", None, [], TODAY)
    assert len(items) == 1 and items[0]["licence"] == "CC BY 4.0" and items[0]["date"] == "2025-06-01"
    assert "Plain summary." in items[0]["body"] and "Eyes need light" not in items[0]["body"]
    assert items[0]["byline"].startswith("Digest of: Jan Doe. Seeing Well. Made-up Journal")
    assert any("eLife's own API" in t and "disallows all" in r for t, r in P.NOT_INCLUDED)


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
    assert "1 stories with news-agency or partner material" in left[0]["reason"]


ARTICLE = ("<p>First paragraph, with a <a href='https://x.example/'>link</a>.</p><h2>A heading with nothing under "
           "it</h2><h2>Second part</h2><p>Second paragraph &amp; more.</p><ul><li>One</li><li>Two</li></ul>"
           "<figure><img src='p.jpg' alt='A described photo'><figcaption>Photo: Someone</figcaption></figure>"
           "<p>Last words.</p><img src='https://counter.theconversation.com/content/1/count.gif' "
           "alt='The Conversation' width='1'>")
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
    original = words(ARTICLE.split("<img src='https://counter")[0])
    assert in_order(original, words(page)), "a whole-and-unchanged article lost words"
    assert "counter.theconversation.com" not in page and "Picture: The Conversation" not in page   # the pixel
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
    assert "Picture: The Conversation" in P.clean(ARTICLE, "https://x.example/", whole=True)   # dropped by atom
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
    assert "permission" in P.catalogue_extra(book)["note"]                 # commercial use needs KFF's permission


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


def test_chronicling_america_slow_down(monkeypatch):
    """When loc.gov answers 429 (too many requests), the piece stops politely and says so."""
    def busy(url):
        """Always too busy."""
        raise urllib.error.HTTPError(url, 429, "Too Many Requests", {}, None)
    use(monkeypatch, [("chronicling-america/?", busy)])
    left = []
    assert P.chronam_items(P.SOURCES["chronicling_america"], "vermont-1920s", None, left, TODAY) == []
    assert left and "slow down" in left[0]["reason"] and len(left) == 1
    assert B.CRAWL_DELAY["www.loc.gov"] >= P.LOC_PAUSE


def test_voa_year_archive(monkeypatch, tmp_path):
    """A VOA year: every story whose address has that year's date (older stories) or whose last change is in that
    year, its date from the address when there is one; what was read is kept as small records in the cache, so a run
    that stops at its time limit (book marked not complete) goes on from there next time."""
    sitemap = gzip.compress(
        b'<urlset><url><loc>https://www.voanews.com/a/a-13-2008-05-31-voa7/1.html</loc><lastmod>2009-11-01'
        b'</lastmod></url><url><loc>https://www.voanews.com/a/new/2.html</loc><lastmod>2008-07-01</lastmod></url>'
        b'<url><loc>https://www.voanews.com/a/video/3.html</loc><lastmod>2008-02-01</lastmod></url>'
        b'<url><loc>https://www.voanews.com/a/other/4.html</loc><lastmod>2019-02-01</lastmod></url></urlset>')
    reads = []

    def page(url):
        """A made-up story (the video page has no written story)."""
        reads.append(url)
        if "video" in url:
            return "<h1>A video</h1><div>player</div>"
        ld = json.dumps({"@type": "NewsArticle", "author": [{"name": "VOA"}], "datePublished": "2009-11-01 00:00:00Z"})
        return (f'<script type="application/ld+json">{ld}</script><h1>Story {url[-6]}</h1>'
                f'<div class="wsw"><p>Text of {url[-6]}.</p></div>')
    use(monkeypatch, [("voanews.com/sitemap.xml", "<sitemapindex><sitemap><loc>https://www.voanews.com/"
                       "sitemap_1_1.xml.gz</loc></sitemap></sitemapindex>"), ("sitemap_1_1.xml.gz", sitemap),
                      ("/a/", page)])
    cache = str(tmp_path / "cache")
    left = []
    items = P.voa_items(P.SOURCES["voa"], "2008", cache, left, TODAY)
    assert [(i["title"], i["date"]) for i in items] == [("Story 2", "2009-11-01"), ("Story 1", "2008-05-31")]
    assert "1 addresses are not written stories" in left[0]["reason"]
    name, data = P.SIDE_FILES[("voa", "2008")]                       # the records, published next to the book
    assert name == "voa_2008.records.json.xz"
    monkeypatch.setattr(B, "fetch", fake_fetch([(f"{P.release_url('voa')}/{name}", data)] + [
        ("voanews.com/sitemap.xml", "<sitemapindex><sitemap><loc>https://www.voanews.com/sitemap_1_1.xml.gz</loc>"
                                    "</sitemap></sitemapindex>"), ("sitemap_1_1.xml.gz", sitemap), ("/a/", page)]))
    reads.clear()
    assert len(P.voa_items(P.SOURCES["voa"], "2008", None, [], TODAY)) == 2 and reads == []   # from the records
    out = tmp_path / "out"
    P.SIDE_FILES[("voa", "2008")] = (name, data)
    monkeypatch.setattr(P, "books_for_key", lambda key, cache, left, today: [])
    manifest = P.build_periodicals(["pub:voa:2008"], str(out), today=TODAY)["pub:voa:2008"]
    assert manifest["files"] == [name] and (out / name).exists()      # uploaded with the manifest's files
    spec = dict(P.SOURCES["voa"], budget_minutes=0)
    left = []
    P.voa_items(spec, "2019", None, left, TODAY)
    assert P.INCOMPLETE[("voa", "2019")] == (0, 1) and "Not finished in this run" in left[0]["reason"]
    book = P.make_book("voa", "2019", [P.item("https://www.voanews.com/a/x/9.html", "X", "2019-02-01", "<p>x</p>")])
    assert P.catalogue_extra(book)["complete"] is False and "Not complete yet" in book.description
    P.INCOMPLETE.clear()


def test_voa_learning_english(monkeypatch):
    """VOA Learning English uses the same reader on its own site."""
    sitemap = gzip.compress(b'<urlset><url><loc>https://learningenglish.voanews.com/a/lesson/5.html</loc>'
                            b'<lastmod>2021-03-01</lastmod></url></urlset>')
    ld = json.dumps({"@type": "NewsArticle", "author": [{"name": "Anna Teacher"}],
                     "datePublished": "2021-03-01 00:00:00Z"})
    use(monkeypatch, [("learningenglish.voanews.com/sitemap.xml", "<sitemapindex><sitemap><loc>https://"
                       "learningenglish.voanews.com/sitemap_2_1.xml.gz</loc></sitemap></sitemapindex>"),
                      ("sitemap_2_1.xml.gz", sitemap),
                      ("/a/lesson/5.html", f'<script type="application/ld+json">{ld}</script><h1>Lesson Five</h1>'
                                           f'<div class="wsw"><p>Slow words.</p></div>')])
    items = P.voa_items(P.SOURCES["voa_learning"], "2021", None, [], TODAY)
    assert [(i["title"], i["date"], i["byline"]) for i in items] == [("Lesson Five", "2021-03-01", "By Anna Teacher")]


def test_voa_history_scripts(monkeypatch):
    """VOA radio scripts from the Internet Archive: only public-domain items credited to the Voice of America, each
    with its OCR text and broadcast date; a decade without scripts says so."""
    def meta(url):
        """Two made-up items: one public domain, one without the mark."""
        ok = "script-a" in url
        return json.dumps({"metadata": {"title": "Corn Belt (VOA Radio Script)", "date": "1976-03-18",
                                        "creator": "Rod Writer, Voice of America",
                                        "licenseurl": "https://creativecommons.org/publicdomain/mark/1.0/" if ok
                                        else ""},
                           "files": [{"name": "a b#1_djvu.txt", "format": "DjVuTXT"}]})
    use(monkeypatch, [("advancedsearch.php", lambda u: json.dumps({"response": {"docs": (
        [{"identifier": "script-a", "date": "1976-03-18"}, {"identifier": "script-b", "date": "1976-04-01"}]
        if "1970" in u else [])}})), ("/metadata/", meta),
        ("/download/script-a/a%20b%231_djvu.txt", "BACKGROUNDER NO. 1\nCORN BELT\n\nVOICE: SOME AREAS")])
    left = []
    items = P.voa_history_items(P.SOURCES["voa_history"], "1970s", None, left, TODAY)
    assert [(i["title"], i["date"], i["byline"]) for i in items] == [("Corn Belt", "1976-03-18",
                                                                       "By Rod Writer, Voice of America")]
    assert "CORN BELT" in items[0]["body"] and "1 items were left out" in left[0]["reason"]
    left = []
    assert P.voa_history_items(P.SOURCES["voa_history"], "1950s", None, left, TODAY) == []
    assert "only the 1970s" in left[0]["reason"]


def test_daily_and_backfill():
    """The daily refresh rebuilds the current pieces (VOA's joined into one key, one request at a time); the backfill
    picks Learning English years newest first, then voanews.com years, skipping complete ones."""
    keys = P.expand_keys(["pub:daily"], TODAY)
    assert keys[0] == "pub:voa:recent+pub:voa:2026+pub:voa_learning:2026"
    for k in ("pub:crs:2026", "pub:global_voices:2026", "pub:nasa_news:2026", "pub:kff_health_news:2026",
              "pub:the_conversation:uk", "pub:uk_hansard:2026", "pub:oireachtas_debates:2026",
              "pub:govuk_speeches:2026"):
        assert k in keys
    assert P.expand_keys(["pub:voa:recent+pub:voa:2026"], TODAY) == ["pub:voa:recent+pub:voa:2026"]
    assert P.expand_keys(["pub:voa:recent+pub:nothing:1"], TODAY) == []
    pieces = {name: [] for name in P.BACKFILL_ORDER}
    pieces.update({"voa_history": ["1970s", "1960s"], "voa_learning": ["2025", "2024"], "voa": ["2025", "1996"]})
    assert P.BACKFILL_ORDER.index("voa_learning") < P.BACKFILL_ORDER.index("voa") < \
        P.BACKFILL_ORDER.index("chronicling_america")                        # small and quick first
    assert P.next_backfill({"books": []}, TODAY, pieces) == "pub:voa_history:1970s"
    catalogue = {"pieces_done": ["pub:voa_history:1970s", "pub:voa_history:1960s"],   # 1960s: found empty
                 "books": [{"name": "voa_learning_2025", "key": "pub:voa_learning:2025", "complete": False}]}
    assert P.next_backfill(catalogue, TODAY, pieces) == "pub:voa_learning:2025"       # not complete: go on
    catalogue["books"][0]["complete"] = True
    catalogue["pieces_done"] += ["pub:voa_learning:2024", "pub:voa:2025"]
    assert P.next_backfill(catalogue, TODAY, pieces) == "pub:voa:1996"
    catalogue["pieces_failed"] = {"pub:voa:1996": 3}                  # a site that stopped answering: skipped
    assert P.next_backfill(catalogue, TODAY, pieces) == ""
    catalogue["pieces_failed"] = {}
    catalogue["pieces_done"].append("pub:voa:1996")
    every = catalogue
    assert P.next_backfill(every, TODAY, pieces) == ""


def test_uk_hansard(monkeypatch):
    """UK Hansard: each sitting day's main debates, one page each with the speakers' names, dated by the day."""
    tree = json.dumps([{"SectionTreeItems": [
        {"Id": 1, "ParentId": None, "Title": "Commons Chamber", "ExternalId": "root"},
        {"Id": 2, "ParentId": 1, "Title": "House of Commons", "ExternalId": "hdg", "HRSTag": "hs_3MainHdg"},
        {"Id": 3, "ParentId": 1, "Title": "Made-up Statement", "ExternalId": "deb-3", "HRSTag": "hs_2cStatement"}]}])
    debate = json.dumps({"Overview": {"Title": "Made-up Statement", "Location": "Commons Chamber"}, "Items": [
        {"ItemType": "Contribution", "HRSTag": "hs_ColumnNumber", "Value": "<span></span>"},
        {"ItemType": "Contribution", "AttributedTo": "Mr Speaker", "Value": "Order, order."}],
        "ChildDebates": [{"Overview": {"Title": "Part Two"}, "Items": [
            {"ItemType": "Contribution", "AttributedTo": "A Member", "Value": "I agree."}]}]})
    use(monkeypatch, [("sectiontrees.json?date=2026-01-05&house=Commons", tree),
                      ("sectiontrees.json", "[]"), ("/debates/debate/deb-3.json", debate)])
    items = P.uk_hansard_items(P.SOURCES["uk_hansard"], "2026", None, [], datetime.date(2026, 1, 10))
    assert [(i["title"], i["date"], i["unit"]) for i in items] == [
        ("Made-up Statement (Commons Chamber, 2026-01-05)", "2026-01-05", "January 2026")]
    assert "<strong>Mr Speaker:</strong> Order, order." in items[0]["body"] and "<h3>Part Two</h3>" in items[0]["body"]


def test_oireachtas(monkeypatch):
    """Oireachtas debates: one page per chamber and sitting day, with the speakers' names (CC BY 4.0)."""
    listing = json.dumps({"results": [{"debateRecord": {"date": "2026-11-18", "chamber": {"showAs": "Dáil Éireann"},
                                                        "formats": {"xml": {"uri": "https://data.oireachtas.ie/akn/ie/"
                                                                            "debateRecord/dail/2026-11-18/debate/"
                                                                            "mul@/main.xml"}}}}]})
    akn = ('<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"><debate><meta>x</meta><debateBody>'
           '<debateSection><heading>Topical Issues</heading><speech><from>Deputy A<recordedTime/></from>'
           '<p>A question.</p></speech></debateSection></debateBody></debate></akomaNtoso>')
    use(monkeypatch, [("/v1/debates?", listing), ("main.xml", akn)])
    items = P.oireachtas_items(P.SOURCES["oireachtas_debates"], "2026", None, [], TODAY)
    assert items[0]["title"] == "Dáil Éireann debates, 2026-11-18" and items[0]["date"] == "2026-11-18"
    assert "<h3>Topical Issues</h3>" in items[0]["body"] and "<strong>Deputy A:</strong>" in items[0]["body"]
    assert items[0]["url"] == "https://www.oireachtas.ie/en/debates/debate/dail/2026-11-18"


def test_govuk_speeches(monkeypatch):
    """GOV.UK speeches: each speech as published, with speaker, department and the day it was delivered."""
    search = json.dumps({"results": [{"link": "/government/speeches/a-speech", "public_timestamp": "2026-11-10"}]})
    content = json.dumps({"title": "A Speech", "first_published_at": "2026-11-10T19:43:00+00:00", "details": {
        "body": "<p>Thank you all.</p>", "delivered_on": "2026-11-09T18:40:00+00:00",
        "speech_type_explanation": "Transcript of the speech, exactly as it was delivered"},
        "links": {"speaker": [{"title": "A Minister"}], "organisations": [{"title": "Cabinet Office"}]}})
    use(monkeypatch, [("/api/search.json?", search), ("/api/content/government/speeches/a-speech", content)])
    items = P.govuk_speeches_items(P.SOURCES["govuk_speeches"], "2026", None, [], TODAY)
    assert [(i["title"], i["date"]) for i in items] == [("A Speech", "2026-11-09")]
    assert items[0]["byline"].startswith("A Minister; Cabinet Office; Transcript")
    assert "Thank you all." in items[0]["body"]


def test_voa_before_2001_from_the_wayback_machine(monkeypatch):
    """VOA before 2001: pages of its old sites captured by the Wayback Machine (CDX API), English only, written
    stories only, wire copy left out, dated by their own DATE= line."""
    long_text = " ".join(["word"] * 130)
    cdx = json.dumps([["timestamp", "original"],
                      ["19980601000000", "http://www.voa.gov:80/news/story1.html"],
                      ["19980602000000", "http://www.voa.gov:80/chinese/story2.html"],
                      ["19980603000000", "http://www.voa.gov:80/news/wire.html"],
                      ["19980604000000", "http://www.voa.gov:80/menu.html"],
                      ["19980605000000", "http://www.voa.gov:80/logo.gif"]])
    use(monkeypatch, [("/cdx/search/cdx?url=www.voa.gov", cdx), ("/cdx/search/cdx", "[]"),
                      ("story1.html", f"<html><title>Made-up Story</title><body><p>DATE=5/31/98</p><p>{long_text}"
                                      f"</p></body></html>"),
                      ("wire.html", f"<body><p>{long_text} (AP)</p></body>"), ("menu.html", "<body>Home News</body>")])
    left = []
    items = P.voa_items(P.SOURCES["voa"], "1998", None, left, TODAY)
    assert [(i["title"], i["date"]) for i in items] == [("Made-up Story", "1998-05-31")]
    assert items[0]["url"].startswith("https://web.archive.org/web/19980601000000/")
    assert "1 pages with news-agency material" in left[0]["reason"] and "1 captured pages are not" in left[0]["reason"]
    assert P.SIDE_FILES.pop(("voa", "1998"))[0] == "voa_1998.records.json.xz"


def test_conversation_year_archive(monkeypatch):
    """The Conversation's older years: the edition's yearly archive sitemap, each article kept whole."""
    use(monkeypatch, [("/us/sitemap_archive_2015.xml", "<urlset><url><loc>https://theconversation.com/a-1</loc>"
                                                        "</url></urlset>"),
                      ("theconversation.com/a-1", '<h1>Old Article</h1><time datetime="2015-12-23T11:14:13Z">x</time>'
                                                  '<a class="author-name" href="/p">Dr B</a>'
                                                  '<div itemprop="articleBody">'
                                                  '<p>Every word.</p><h2>Empty</h2></div><div>Related</div>'),
                      ("republishing-guidelines", "publish all our work under a Creative Commons licence")])
    book = P.books_for_key("pub:the_conversation:us-2015", None, [], TODAY)[0]
    assert book.title == "The Conversation, United States edition, 2015" and book.unchanged
    page = book.pages[0]
    assert page.title == "Old Article" and "<h2>Empty</h2>" in page.body and "Related" not in page.body
    assert "By Dr B" in page.body and "2015-12-23" in page.body


def test_finished_pieces_are_recorded(monkeypatch, tmp_path):
    """A piece built completely, or found empty, is listed as done in its manifest (and merged into the catalogue's
    pieces_done), so the backfill moves on; a piece cut short by its time limit is not."""
    monkeypatch.setattr(P, "books_for_key", lambda key, cache, left, today: [])
    m = P.build_periodicals(["pub:voa_history:1950s"], str(tmp_path), today=TODAY)["pub:voa_history:1950s"]
    assert m["done"] == ["pub:voa_history:1950s"]
    P.INCOMPLETE[("voa", "2019")] = (5, 10)
    m = P.build_periodicals(["pub:voa:2019"], str(tmp_path), today=TODAY)["pub:voa:2019"]
    assert m["done"] == []
    P.INCOMPLETE.clear()
    data = B.merge([str(tmp_path / "manifest-pub_voa_history_1950s.json")], {"pieces_done": ["pub:x:1"]})
    assert data["pieces_done"] == ["pub:voa_history:1950s", "pub:x:1"]


def test_joined_key_is_built_piece_by_piece(monkeypatch, tmp_path):
    """The daily refresh's joined VOA key is built as its pieces, one after another, each with its own manifest."""
    built = []
    monkeypatch.setattr(P, "books_for_key", lambda key, cache, left, today: built.append(key) or [])
    manifests = B.build(["pub:voa:recent+pub:voa_learning:2026"], str(tmp_path))
    assert built == ["pub:voa:recent", "pub:voa_learning:2026"] and set(manifests) == set(built)


def test_voa_months_skip_years_already_built():
    """VOA's 1970s are built a month at a time; a year built whole before the change is not built again."""
    pieces = {name: [] for name in P.BACKFILL_ORDER}
    pieces["voa_history"] = ["1975-01", "1975-02", "1976-01"]
    catalogue = {"pieces_done": ["pub:voa_history:1975"]}
    assert P.next_backfill(catalogue, TODAY, pieces) == "pub:voa_history:1976-01"
    assert P.expand_keys(["pub:voa_history:1976-03"], TODAY) == ["pub:voa_history:1976-03"]
