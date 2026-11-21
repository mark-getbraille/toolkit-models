"""Self-test of the sources added to the periodicals builder on 2026-11-21 (publications_more.py), with MADE-UP data
only: nothing is downloaded.

It checks that:
  - the sources are registered in periodicals.py (keys, pieces, drivers, licence lines) without changing the hourly
    backfill order, and every piece rule accepts its own pieces;
  - only the PDF documents of Open Government Licence - Canada records on Government of Canada hosts are taken,
    never web pages or web-archive copies, and a record under another licence is skipped;
  - a GAO report's text file becomes one item with its title, date and number;
  - the Government Manual's XML becomes headings and paragraphs, with the web address as a link;
  - an ERIC document is taken only when its own text states public domain or a Creative Commons licence without
    NoDerivatives, and keeps that licence on its page;
  - GOV.UK guides keep every part of a multi-part guide; the UK alerts are one book per kind and year;
  - Farmers' Bulletins are kept only when their record shows a US government work, with the old-advice notice;
  - each non-US source gets its specific practice notice.

Run it from the repository's folder:   python3 -m pytest textbooks/test_publications_more.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import periodicals as P  # noqa: E402
import publications_more as M  # noqa: E402
import sources  # noqa: E402


def test_registered():
    for name in M.SOURCES:
        assert P.SOURCES[name] is M.SOURCES[name] and name not in P.BACKFILL_ORDER
        spec = P.SOURCES[name]
        assert spec["driver"] in P.DRIVERS and spec["group"] in sources.GROUPS
        for piece in spec["pieces"](None) + M.ALL_PIECES[name](None):
            assert re.match(spec["piece_rule"], piece), (name, piece)
        assert name in P.LICENCE_LINES
        assert B.licence_kind(P.LICENCE_ALIASES.get(spec["licence"], spec["licence"]), False), name
    keys = P.expand_keys(["pub:canada_ogl", "pub:gao_reports:1999", "pub:eric_open:braille", "pub:nonsense:1"])
    assert "pub:canada_ogl:health" in keys and "pub:gao_reports:1999" in keys and "pub:eric_open:braille" in keys
    assert not any(k.startswith("pub:nonsense") for k in keys)
    assert P.piece_label("uk_safety_alerts", "drug-2026").endswith(", 2026")
    assert P.piece_label("crs", "2026") == "2026"                       # the old sources keep their labels


def test_canada_files_only_documents_on_government_hosts():
    record = {"resources": [
        {"format": "HTML", "language": "['en']", "url": "https://www.canada.ca/en/health-canada/x.html"},
        {"format": "PDF", "language": "['fr']", "url": "/data/dataset/1/resource/2/download/fr.pdf"},
        {"format": "PDF", "language": "['en']", "url": "https://webarchiveweb.wayback.bac-lac.canada.ca/x.pdf"},
        {"format": "PDF", "language": "['en']", "url": "https://example.com/x.pdf"},
        {"format": "PDF", "language": "['en']", "url": "/data/dataset/1/resource/3/download/en.pdf", "name": "Guide"},
        {"format": "PDF", "language": "['en', 'fr']", "url": "https://www.canada.ca/content/dam/hc/guide.pdf"}]}
    assert M.canada_files(record) == [("https://open.canada.ca/data/dataset/1/resource/3/download/en.pdf", "Guide"),
                                      ("https://www.canada.ca/content/dam/hc/guide.pdf", "")]


def test_canada_items_check_the_licence(monkeypatch):
    records = [{"id": "a", "license_id": "ca-ogl-lgo", "date_published": "2019-04-04 00:00:00",
                "title_translated": "{'en': 'Living with vision loss', 'fr': 'x'}", "notes": "A guide.",
                "organization": {"title": "Veterans Affairs Canada | Anciens Combattants Canada"},
                "resources": [{"format": "PDF", "language": "['en']", "url": "/data/x/en.pdf"}]},
               {"id": "b", "license_id": "other", "date_published": "2019-01-01", "title": "Closed",
                "resources": [{"format": "PDF", "language": "['en']", "url": "/data/y/en.pdf"}]},
               {"id": "c", "license_id": "ca-ogl-lgo", "date_published": "2018-01-01", "title": "Web only",
                "resources": [{"format": "HTML", "language": "['en']", "url": "https://www.veterans.gc.ca/x"}]}]
    monkeypatch.setattr(M, "canada_records", lambda fq, cache: records)
    asked = []
    monkeypatch.setattr(M, "pdf_item_body", lambda url, cache, left, label: (asked.append(url) or "<p>Text</p>", 1))
    left = []
    items = M.canada_ogl_items(M.SOURCES["canada_ogl"], "veterans", None, left, None)
    assert [i["title"] for i in items] == ["Living with vision loss"] and asked == ["https://open.canada.ca/data/x/en.pdf"]
    assert items[0]["byline"] == "Veterans Affairs Canada" and items[0]["date"] == "2019-04-04"
    assert "web pages" in left[0]["reason"]
    assert M.canada_ogl_items(M.SOURCES["canada_ogl"], "veterans-2018", None, [], None) == []


GAO_TEXT = """<html><head><title>B-310780, Federal Vacancies Reform Act of 1998, June 13, 2008</title></head>
<body><pre>TITLE: B-310780, Federal Vacancies Reform Act of 1998, June 13, 2008
BNUMBER: B-310780
DATE: June 13, 2008
*****************************************************************************
   The Honorable Richard J. Durbin
   United States Senate

   By letter dated April 16, 2008, you requested our
   opinion.
</pre></body></html>"""


def test_gao_items(monkeypatch):
    pages = {f"{M.GOVINFO}/sitemap/GAOREPORTS_2008_sitemap.xml":
             "<urlset><url><loc>https://www.govinfo.gov/app/details/GAOREPORTS-B-310780</loc></url></urlset>",
             f"{M.GOVINFO}/content/pkg/GAOREPORTS-B-310780/html/GAOREPORTS-B-310780.htm": GAO_TEXT}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: pages[url])
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    items = M.gao_items(M.SOURCES["gao_reports"], "2008", None, [], None)
    assert len(items) == 1 and items[0]["date"] == "2008-06-13" and "B-310780" in items[0]["byline"]
    assert "<p>By letter dated April 16, 2008, you requested our opinion.</p>" in items[0]["body"]
    assert "*****" not in items[0]["body"]


def test_govman_html():
    xml = ("<GovernmentManual><accessId>GOVMAN-1</accessId><Entity><EntityType>Parent</EntityType>"
           "<Category>Legislative Branch</Category><AgencyName>Congress</AgencyName><Addresses><Address>"
           "<FooterDetails><WebAddress>http://www.congress.gov</WebAddress></FooterDetails>"
           "<Address>ONE HUNDRED AND NINETEENTH CONGRESS</Address></Address></Addresses><MissionStatement>"
           "<Record><Paragraph>The Congress was created by Article I.</Paragraph></Record></MissionStatement>"
           "</Entity></GovernmentManual>")
    out = M.govman_html(xml)
    assert "<h2>Congress</h2>" in out and "<p>The Congress was created by Article I.</p>" in out
    assert "GOVMAN-1" not in out and "Parent" not in out and "<p>Legislative Branch</p>" in out


def test_eric_licence():
    assert M.eric_licence("This report is in the public domain. Authorization to reproduce it in whole or in part is "
                          "granted. U.S. Department of Education")[0] == sources.US_GOV
    assert M.eric_licence("This work is licensed under a Creative Commons Attribution 4.0 International License.") \
        == ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/")
    assert M.eric_licence("licensed under a Creative Commons Attribution-ShareAlike 4.0 International license")[0] \
        == "CC BY-SA 4.0"
    assert M.eric_licence("Creative Commons Attribution-NonCommercial 4.0")[0] == "CC BY-NC 4.0"
    assert M.eric_licence("Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International") == ("", "")
    assert M.eric_licence("CC BY-NC-ND 4.0") == ("", "")
    assert M.eric_licence("Copyright 2019 American Foundation for the Blind. All rights reserved.") == ("", "")


def test_eric_items_keep_each_licence(monkeypatch):
    docs = [{"id": "ED1", "title": "Open &amp; free", "publicationdateyear": 2022, "author": ["A, B"]},
            {"id": "EJ2", "title": "Closed", "publicationdateyear": 2021}]
    monkeypatch.setattr(M, "eric_candidates", lambda q, cache, want: docs)
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    words = {"ED1": "This work is licensed under a Creative Commons Attribution 4.0 International License.",
             "EJ2": "Copyright 2021 the publisher. All rights reserved."}
    monkeypatch.setattr(M, "pdf_front_words", lambda url, cache: (words[url.rsplit("/", 1)[1][:-4]], 3, b""))
    monkeypatch.setattr(M, "pdf_item_body", lambda url, cache, left, label: ("<p>Text</p>", 3))
    left = []
    items = M.eric_items(M.SOURCES["eric_open"], "braille", None, left, None)
    assert [(i["title"], i["licence"]) for i in items] == [("Open & free", "CC BY 4.0")]
    assert "1 documents state no open licence" in left[0]["reason"]


def test_govuk_body_keeps_every_part():
    d = {"details": {"parts": [{"title": "Overview", "body": "<p>One</p>"}, {"title": "Eligibility",
                                                                           "body": "<p>Two</p>"}]}}
    out = M.govuk_body(d)
    assert "<h2>Overview</h2>" in out and "<p>Two</p>" in out
    assert "<p>Start</p>" in M.govuk_body({"details": {"introductory_paragraph": "<p>Start</p>"}})


def test_uk_alert_pieces():
    pieces = M.SOURCES["uk_safety_alerts"]["pieces"](None)
    assert {p.split("-")[0] for p in pieces} == set(M.UK_ALERT_KINDS) and all(re.search(r"-20\d\d$", p) for p in pieces)


def test_farmers_bulletins(monkeypatch):
    docs = [{"identifier": "CAT1", "title": "Home canning", "year": 1946, "creator": "United States. Department of "
             "Agriculture"}, {"identifier": "X2", "title": "Someone else's", "year": 1947, "creator": "A company"}]
    monkeypatch.setattr(M, "ia_collection_docs", lambda c, first, last, cache: docs)
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: "word " * 60 + "\n\nmore words")
    left = []
    items = M.farmers_bulletin_items(M.SOURCES["usda_farmers_bulletins"], "1940s", None, left, None)
    assert [i["title"] for i in items] == ["Home canning"] and "1 records do not show" in left[0]["reason"]
    assert "UNSAFE" in M.SOURCES["usda_farmers_bulletins"]["notice"]


def test_practice_notices():
    for name in ("canada_ogl", "govuk_guides", "uk_safety_alerts"):
        spec = M.SOURCES[name]
        for piece in spec["pieces"](None):
            note = sources.practice_note(spec["country"], spec["subject"],
                                         f"{spec['series_title']}, {P.piece_label(name, piece)}")
            assert note.endswith("may differ from US practice."), (name, piece)
    assert "transport rules" in sources.practice_note("Canada", "x", P.piece_label("canada_ogl", "transport"))
    assert "benefits and pensions" in sources.practice_note("Canada", "x", P.piece_label("canada_ogl", "veterans"))
    assert "medicine names" in sources.practice_note("Canada", "x", P.piece_label("canada_ogl", "health"))
    assert "vehicle standards" in sources.practice_note("United Kingdom", "UK government guides",
                                                        P.piece_label("govuk_guides", "driving"))
    assert "tax and debt" in sources.practice_note("United Kingdom", "UK government guides",
                                                   P.piece_label("govuk_guides", "tax_debt"))
    title = f"{M.SOURCES['uk_safety_alerts']['series_title']}, {P.piece_label('uk_safety_alerts', 'drug-2026')}"
    assert "medicine names" in sources.practice_note("United Kingdom", "UK safety alerts", title)
    assert "recall" in sources.practice_note("United Kingdom", "UK safety alerts",
                                             P.piece_label("uk_safety_alerts", "product-2026"))
    assert sources.practice_note("United States", "GAO") == ""
