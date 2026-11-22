"""Self-test of the court opinions (court_opinions.py, court:), patents (patents.py, pat:) and quotations
(quotations.py, quote:) books, with MADE-UP data only: nothing is downloaded.

It checks that each module is registered once under its request words (each at most 256 jobs), reaches sources.py
with its group, licence lines and NOT_INCLUDED rows (each with an address); that govinfo's MODS records are read
right (made-up volume and court records: cases kept, front matter left out, dates and citations taken from the
record) and that a landmark whose record is missing or whose date differs is left out with its reason; that a volume
book is made of its cases' PDFs (pdf_set, with a made-up reader); that a patent's full-text XML (made up) gives its
title, number, inventors, date, abstract, claims and description, that a patent with a copyright notice is left out,
and that the USPTO books are sign-up entries that say where to sign up when the key is missing; that the old
quotation books are dated before 1931 and say they reflect their day; that Wikiquote is read from a made-up dump by
first letter, skipping redirects and other namespaces; that the index books are made offline with keys the library
has; and that Wikiquote's Kiwix label reaches the builder.

Run it from the repository's folder:   python3 -m pytest textbooks/test_court_patents_quotes.py
"""

import bz2
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import court_opinions as C  # noqa: E402
import more_refs  # noqa: E402
import patents as P  # noqa: E402
import practical_index as X  # noqa: E402
import quotations as Q  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

WORDS = {C: ["court-opinions", "court-opinions-scotus-1", "court-opinions-scotus-2", "court-opinions-scotus-3"],
         P: ["patents"], Q: ["quotations"]}


# ====================================================================== registration

def test_registered_with_groups_lines_and_rows():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    for m, words in WORDS.items():
        assert m in more_refs.modules() and prefixes.count(m.COLLECTION.prefix) == 1, m.__name__
        every = []
        for word in words:
            keys = sources.expand_keys([word])
            assert 0 < len(keys) == len(set(keys)) <= 256, word
            every += keys
        assert set(every) == set(m.COLLECTION.own_keys()), m.__name__
        for group, name in m.GROUPS.items():
            assert sources.GROUPS[group] == name
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    assert sources.GROUPS["court_opinions"] == "Reference, court opinions"
    assert sources.GROUPS["patents"] == "Reference, patents"
    assert sources.GROUPS["quotations"] == "Reference, quotations and proverbs"


def test_every_supreme_court_volume_once():
    keys = [k for w in WORDS[C][1:] for k in sources.expand_keys([w])]
    assert len(keys) == len(set(keys)) == len(C.VOLUMES) == 584
    assert "court:usreports:347" in keys and "court:usreports:465" not in keys and "court:usreports:1" not in keys


def test_landmarks_not_repeating_civics():
    import civics
    civics_cases = {(v, p) for _n, v, p, _y in civics.CASES}
    seen = set()
    for subject, (_title, intro, cases) in C.LANDMARKS.items():
        assert intro and cases, subject
        for case in cases:
            if case[0] == C.USR:
                assert (case[1], case[2]) not in civics_cases, case
                assert (case[1], case[2]) not in seen, case
                seen.add((case[1], case[2]))
            else:
                _k, package, number, date, court, citation, _note = case
                assert package.startswith("USCOURTS-") and court.startswith("US ") and " v. " in citation
                assert len(date) == 10 and date[:4] in citation


# ====================================================================== govinfo records (made up)

VOLUME_MODS = """<mods xmlns="http://www.loc.gov/mods/v3">
<relatedItem type="constituent" ID="id-USREPORTS-999-FrontMatter"><titleInfo><title>Table of Cases</title>
<partName>Front Matter</partName></titleInfo>
<relatedItem type="otherFormat" xlink:href="https://www.govinfo.gov/content/pkg/USREPORTS-999/pdf/USREPORTS-999-FrontMatter.pdf"/>
<extension><granuleClass>FRONTMATTER</granuleClass></extension></relatedItem>
<relatedItem type="constituent" ID="id-USREPORTS-999-1"><titleInfo><title>Doe v. Made-Up Town, 999 U.S. 1 (2031)</title>
</titleInfo><identifier type="uri">https://www.govinfo.gov/app/details/USREPORTS-999/USREPORTS-999-1</identifier>
<identifier type="United States Reports citation">999 U.S. 1</identifier>
<relatedItem type="otherFormat" xlink:href="https://www.govinfo.gov/content/pkg/USREPORTS-999/pdf/USREPORTS-999-1.pdf"/>
<subject><topic>Housing</topic><topic>Housing</topic></subject>
<extension><granuleClass>CASE</granuleClass><decisionDate>2031-03-02</decisionDate></extension></relatedItem>
<relatedItem type="constituent" ID="id-USREPORTS-999-20"><titleInfo><title>Roe &amp; Co. v. State, 999 U.S. 20 (2031)</title>
</titleInfo><identifier type="uri">https://www.govinfo.gov/app/details/USREPORTS-999/USREPORTS-999-20</identifier>
<relatedItem type="otherFormat" xlink:href="https://www.govinfo.gov/content/pkg/USREPORTS-999/pdf/USREPORTS-999-20.pdf"/>
<extension><granuleClass>CASE</granuleClass><decisionDate>2031-06-30</decisionDate></extension></relatedItem>
</mods>"""

COURT_MODS = """<mods xmlns="http://www.loc.gov/mods/v3">
<relatedItem type="constituent" ID="id-USCOURTS-cand-1_00-cv-00001-0"><titleInfo><title>Made-Up Council v. Shop</title>
</titleInfo><originInfo><dateIssued>2030-01-05</dateIssued></originInfo>
<relatedItem type="otherFormat" xlink:href="https://www.govinfo.gov/content/pkg/USCOURTS-cand-1_00-cv-00001/pdf/USCOURTS-cand-1_00-cv-00001-0.pdf"/>
</relatedItem>
<relatedItem type="constituent" ID="id-USCOURTS-cand-1_00-cv-00001-1"><titleInfo><title>Made-Up Council v. Shop</title>
</titleInfo><originInfo><dateIssued>2030-09-09</dateIssued></originInfo>
<relatedItem type="otherFormat" xlink:href="https://www.govinfo.gov/content/pkg/USCOURTS-cand-1_00-cv-00001/pdf/USCOURTS-cand-1_00-cv-00001-1.pdf"/>
</relatedItem>
</mods>"""


def test_granules_of_made_up_records():
    parts = C.granules(VOLUME_MODS)
    assert [g["id"] for g in parts] == ["USREPORTS-999-FrontMatter", "USREPORTS-999-1", "USREPORTS-999-20"]
    case = parts[1]
    assert case["kind"] == "CASE" and case["citation"] == "999 U.S. 1" and case["date"] == "2031-03-02"
    assert case["topics"] == ["Housing"] and case["pdf"].endswith("USREPORTS-999-1.pdf")
    assert parts[2]["title"] == "Roe & Co. v. State, 999 U.S. 20 (2031)"
    assert C.case_part(case) == ("Doe v. Made-Up Town, 999 U.S. 1 (2031), decided 2 March 2031", case["pdf"],
                                 case["page"])
    court = C.granules(COURT_MODS)
    assert [g["date"] for g in court] == ["2030-01-05", "2030-09-09"] and court[0]["kind"] == ""


def test_volume_book_from_its_cases(monkeypatch):
    import pdf_set
    monkeypatch.setattr(C, "read_mods", lambda package, cache=None: VOLUME_MODS if package == "USREPORTS-999" else "")
    seen = {}

    def made_up_set(entry, parts, work, cache=None, left_out=None, limit=None):
        seen["entry"], seen["parts"] = entry, parts
        book = K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], entry["source"], entry["description"],
                          entry["notice"])
        book.pages = [B.Page("1-1", "Made-up page", "<p>Made up.</p>", 1, parts[0][0])]
        return book
    monkeypatch.setattr(pdf_set, "pdf_set_book", made_up_set)
    book = C.usreports_book("usreports:999", "work")
    assert [p[0] for p in seen["parts"]] == ["Doe v. Made-Up Town, 999 U.S. 1 (2031), decided 2 March 2031",
                                             "Roe & Co. v. State, 999 U.S. 20 (2031), decided 30 June 2031"]
    assert seen["entry"]["group"] == C.GROUP_SCOTUS and seen["entry"]["licence"] == K.US_GOV
    assert book.title == "United States Reports, volume 999 (2031): every case" and book.published == "2031-06-30"
    assert "not legal advice" in book.notice and "syllabus" in book.notice
    left_out = []
    assert C.usreports_book("usreports:998", "work", None, left_out) is None and "no case record" in \
        left_out[0]["reason"]


def test_landmark_parts_checked_against_the_record(monkeypatch):
    records = {"USREPORTS-999": VOLUME_MODS, "USCOURTS-cand-1_00-cv-00001": COURT_MODS}
    monkeypatch.setattr(C, "read_mods", lambda package, cache=None: records.get(package, ""))
    monkeypatch.setitem(C.LANDMARKS, "made_up", ("Made up", "Made-up cases.", [
        (C.USR, 999, 20, "Later history: made up."), (C.USR, 999, 55, ""),
        (C.USC, "USCOURTS-cand-1_00-cv-00001", 1, "2030-09-09", "US District Court for Made-Up County",
         "Made-Up Council v. Shop, 1 F. Supp. 9 (2030)", ""),
        (C.USC, "USCOURTS-cand-1_00-cv-00001", 0, "2030-02-02", "US District Court for Made-Up County",
         "Made-Up Council v. Shop, 1 F. Supp. 1 (2030)", "")]))
    left_out = []
    parts = C.landmark_parts("made_up", None, left_out)
    assert parts[0][0] == ("Roe & Co. v. State, 999 U.S. 20 (2031), decided 30 June 2031, Supreme Court of the United "
                           "States. Later history: made up.")
    assert parts[1][0] == ("Made-Up Council v. Shop, 1 F. Supp. 9 (2030), US District Court for Made-Up County, "
                           "decided 9 September 2030") and parts[1][1].endswith("-1.pdf")
    assert len(parts) == 2 and [x["title"] for x in left_out] == ["999 U.S. 55", "Made-Up Council v. Shop, 1 F. "
                                                                                  "Supp. 1 (2030)"]


def test_index_books_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for m in (C, P, Q):
        book_fn, _sign = m.COLLECTION.makers["index"]
        left_out = []
        book = book_fn("index", "work", None, left_out)
        assert book.pages and book.licence == X.CC0_INDEX and not left_out, (m.__name__, left_out)


# ====================================================================== patents (made-up XML)

PATENT_XML = """<?xml version="1.0"?><us-patent-grant><us-bibliographic-data-grant>
<publication-reference><document-id><country>US</country><doc-number>09999999</doc-number><kind>B2</kind>
<date>20300312</date></document-id></publication-reference>
<invention-title id="t1">REFRESHABLE TACTILE MADE-UP DISPLAY</invention-title>
<us-parties><inventors><inventor sequence="001"><addressbook><last-name>Example</last-name><first-name>Ann</first-name>
</addressbook></inventor><inventor sequence="002"><addressbook><last-name>Sample</last-name><first-name>Bo</first-name>
</addressbook></inventor></inventors></us-parties></us-bibliographic-data-grant>
<abstract id="abstract"><p>A made-up display raises pins to form &amp; show braille cells.</p></abstract>
<description id="description"><heading>BACKGROUND</heading><p>Made-up background words.</p>
<heading>DETAILED DESCRIPTION</heading><p>Pins are moved by made-up actuators.</p></description>
<claims id="claims"><claim id="CLM-00001" num="00001"><claim-text>1. A made-up display comprising pins.</claim-text>
</claim><claim id="CLM-00002" num="00002"><claim-text>2. The display of claim 1, wherein the pins are round.</claim-text>
</claim></claims></us-patent-grant>"""


def test_patent_parts_and_page():
    p = P.patent_parts(PATENT_XML)
    assert p["number"] == "9999999" and p["date"] == "2030-03-12" and p["inventors"] == ["Ann Example", "Bo Sample"]
    assert p["title"] == "REFRESHABLE TACTILE MADE-UP DISPLAY" and p["abstract"].endswith("show braille cells.")
    assert p["claims"][1].startswith("2. The display of claim 1")
    assert p["description"] == [("heading", "BACKGROUND"), ("p", "Made-up background words."),
                                ("heading", "DETAILED DESCRIPTION"), ("p", "Pins are moved by made-up actuators.")]
    page = P.patent_page_html(p)
    assert "US 9,999,999" in page and "<h2>Claims</h2><ol><li>A made-up display comprising pins.</li>" in page
    assert "<h3>BACKGROUND</h3>" in page and "Ann Example, Bo Sample" in page
    assert not P.COPYRIGHT_NOTICE.search(P.xml_text(PATENT_XML))
    assert P.COPYRIGHT_NOTICE.search("A portion of the disclosure contains material subject to copyright protection")


def test_uspto_books_are_sign_up_entries(monkeypatch):
    with pytest.raises(ValueError):             # the key is only ever sent to api.uspto.gov
        P.odp_call("made-up-key", "https://example.org/not-the-uspto")
    monkeypatch.delenv(P.USPTO_KEY_ENV, raising=False)
    monkeypatch.setattr(P, "odp_call", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no call")))
    for name in P.ODP_BOOKS:
        left_out = []
        assert P.COLLECTION.makers[name][0](name, "work", None, left_out) is None
        assert "sign-up entry" in left_out[0]["reason"] and P.USPTO_KEY_ENV in left_out[0]["reason"]
        assert left_out[0]["fetch_yourself"] and left_out[0]["url"] == P.ODP_SIGNUP
    assert sources.ALLOWED[P.PATENT_LICENCE] == "open"


def test_uspto_book_with_a_made_up_portal(monkeypatch):
    monkeypatch.setenv(P.USPTO_KEY_ENV, "made-up-key")
    monkeypatch.setattr(P, "PAUSE", 0)
    found = {"patentFileWrapperDataBag": [
        {"applicationMetaData": {"patentNumber": "9999999", "inventionTitle": "Made-up display",
                                 "cpcClassificationBag": ["G09B 21/004"], "grantDate": "2030-03-12"},
         "grantDocumentMetaData": {"fileLocationURI": P.ODP + "made-up/9999999.xml"}},
        {"applicationMetaData": {"patentNumber": "8888888", "inventionTitle": "Off-topic",
                                 "cpcClassificationBag": ["B60K 1/00"]},
         "grantDocumentMetaData": {"fileLocationURI": P.ODP + "made-up/8888888.xml"}}]}
    import json

    def made_up_call(key, url, body=None):
        assert key == "made-up-key"
        if url.endswith("search"):
            return 200, json.dumps(found if body["pagination"]["offset"] == 0 else {}).encode()
        return 200, PATENT_XML.encode()
    monkeypatch.setattr(P, "odp_call", made_up_call)
    monkeypatch.setitem(P.ODP_BOOKS, "assistive_technology", P.ODP_BOOKS["assistive_technology"][:3] +
                        ([(r"G09B21*", ("G09B21",), 5)],))
    book_fn, _sign = P.odp_maker("assistive_technology")
    book = book_fn("assistive_technology", "work", None, [])
    assert [p.title for p in book.pages] == ["US 9999999: Refreshable tactile made-up display"]
    assert book.licence == P.PATENT_LICENCE and "37 CFR 1.71" in book.notice


# ====================================================================== quotations

def test_old_quotation_books():
    for p in Q.PDFS:
        assert p["old_public_domain"] and int(p["published"]) < 1931 and p["group"] == Q.GROUP, p["name"]
        assert "attitudes of its day" in p["description"] and p["archive"], p["name"]
        assert B.licence_kind(p["licence"]) == "open"
    names = {p["name"] for p in Q.PDFS}
    for want in ("bartlett_familiar_quotations_1919", "hoyt_new_cyclopedia_quotations_1922",
                 "brewer_dictionary_phrase_fable_1898"):
        assert want in names
    archives = [p["archive"] for p in Q.PDFS]
    assert len(archives) == len(set(archives))
    for e in sources.PDF_DOCS:
        assert e.get("archive") not in archives, e["name"]


def made_up_dump(path):
    """A tiny made-up Wikiquote dump (bz2 XML) with articles, a redirect and a talk page."""
    pages = [("Quokka sayings", "0", "== Sayings ==\n* A made-up quokka saying.\n** Made-up source, 2030"),
             ("Quiet", "0", "#REDIRECT [[Silence]]"),
             ("Talk:Quiet", "1", "* talk"),
             ("Apple proverbs", "0", "* An apple a made-up day."),
             ("42 (made up)", "0", "* Forty-two made-up words.")]
    xml = ['<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/">']
    for title, ns, text in pages:
        xml.append(f"<page><title>{title}</title><ns>{ns}</ns><revision><text>{text}</text></revision></page>")
    xml.append("</mediawiki>")
    with bz2.open(path, "wt", encoding="utf-8") as f:
        f.write("".join(xml))


def test_wikiquote_by_letter(tmp_path, monkeypatch):
    path = str(tmp_path / "dump.xml.bz2")
    made_up_dump(path)
    assert [t for t, _ in Q.wikiquote_pages(path, "q")] == ["Quokka sayings"]
    assert [t for t, _ in Q.wikiquote_pages(path, "other")] == ["42 (made up)"]
    assert Q.letter_of("Ébène") == "other" and Q.letter_of("apple") == "a"
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, **k: "Creative Commons Attribution-ShareAlike License")
    monkeypatch.setattr(K, "download_file", lambda url, cache, name=None, max_age_days=None: path)
    book = Q.wikiquote_book("wikiquote:q", "work")
    assert [p.title for p in book.pages] == ["Quokka sayings"] and book.licence == "CC BY-SA 4.0"
    assert "A made-up quokka saying." in book.pages[0].body and "en.wikiquote.org/wiki/Quokka_sayings" in \
        book.pages[0].body
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, **k: "All rights reserved")
    left_out = []
    assert Q.wikiquote_book("wikiquote:q", "work", None, left_out) is None and "licence line" in \
        left_out[0]["reason"]


def test_wikiquote_kiwix_label():
    assert more_refs.kiwix_labels()["wikiquote_en_all"] == "CC BY-SA (share-alike)"
    assert len(Q.COLLECTION.expand_keys(["quote:wikiquote"])) == 27
