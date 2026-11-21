"""Self-tests of the whole open catalogues (textbooks/open_catalogues.py), with MADE-UP records only: nothing is
downloaded.

They check that: licences are read right (NoDerivatives and GNU refused, non-commercial ones personal use only);
titles are made comparable across editions; an Open Book Publishers book is read from its Internet Archive copy
and a NoDerivatives one is left out; an Open Textbook Library book on LibreTexts or a Pressbooks site is left out
and one with its own PDF is taken; Internet Archive items are taken only as checked (a Creative Commons item needs
an author, a year and its licence in its own first pages; an old one a year before 1931; a government one a US
government publisher; catalogues and magazines never); the keys expand to every piece and stay under the workflow's
256 jobs per source; a book whose host shuts out AI readers is not read; and the weekly sign is "" when the source
cannot be asked.

Run from the repository's folder:   python3 -m pytest textbooks/test_open_catalogues.py
"""

import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import open_catalogues as O  # noqa: E402
import sources  # noqa: E402


def test_licences():
    assert O.cc_short("https://creativecommons.org/licenses/by/4.0/") == "CC BY 4.0"
    assert O.cc_short("http://creativecommons.org/licenses/by-nc-sa/3.0/") == "CC BY-NC-SA 3.0"
    assert O.cc_short("https://creativecommons.org/licenses/by-nc-nd/4.0/") == ""
    assert O.cc_short("https://creativecommons.org/publicdomain/zero/1.0/") == "CC0 1.0"
    assert O.cc_short("Attribution-ShareAlike") == "CC BY-SA"
    assert O.cc_short("Free Documentation License (GNU)") == "" and O.cc_short("Attribution-NoDerivs") == ""
    assert O.personal("CC BY-NC 4.0") and not O.personal("CC BY-SA 4.0") and not O.personal("CC0 1.0")
    for short in ("CC BY 4.0", "CC BY-SA", "CC0 1.0", "CC BY-NC-SA 3.0"):
        assert B.licence_kind(B.licence_short(short)) in ("open", "share-alike", "non-commercial")
    assert O.licence_url("CC BY-NC 4.0") == "https://creativecommons.org/licenses/by-nc/4.0/"


def test_titles_across_editions():
    same = ["Introduction to Sociology 3e", "Introduction to Sociology (Second Edition): A Canadian view",
            "OpenStax Introduction to Sociology", "Introduction to Sociology, 2nd edition"]
    assert {O.norm_title(t) for t in same} == {"introduction to sociology"}
    assert O.norm_title("The Art of Knitting") == "art of knitting"
    assert O.is_duplicate("TM 10-412 Army Recipes 1944", O.title_keys("Army Recipes, TM 10-412"))
    assert not O.is_duplicate("Army Recipes for Camps", O.title_keys("Army Recipes, TM 10-412"))


def test_cc_statement_in_pdf():
    assert re.search(O.CC_IN_PDF, "This work is licensed under a Creative Commons Attribution 4.0 International "
                                  "License (CC BY 4.0).")
    assert not re.search(O.CC_IN_PDF, "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0")
    assert not re.search(O.CC_IN_PDF, "Copyright 2013 American Psychiatric Association. All rights reserved.")


def work(licence="https://creativecommons.org/licenses/by/4.0/", platform="INTERNET_ARCHIVE", title="A Book"):
    """A made-up Thoth work."""
    return {"workId": "11111111-2222-3333-4444-555555555555", "fullTitle": title, "license": licence,
            "publicationDate": "2024-05-01", "doi": "https://doi.org/10.11647/obp.0123", "landingPage": "https://x",
            "longAbstract": "<p>What it is about.</p>", "languages": [{"languageCode": "SPA", "mainLanguage": True}],
            "subjects": [{"subjectType": "KEYWORD", "subjectCode": "history", "subjectOrdinal": 1}],
            "contributions": [{"fullName": "Ann Author", "contributionType": "AUTHOR", "contributionOrdinal": 1}],
            "publications": [{"publicationType": "PDF", "locations": [
                {"fullTextUrl": "https://archive.org/download/abc/abc.pdf", "landingPage":
                 "https://archive.org/details/abc", "locationPlatform": platform}]}]}


def test_obp_entries():
    entry, why = O.obp_entry(work())
    assert entry["name"] == "obp_0123" and entry["pdf"] == "https://archive.org/download/abc/abc.pdf"
    assert entry["licence"] == "CC BY 4.0" and not entry["personal_use"] and entry["language"] == "spa"
    assert entry["pdf_licence_text"] == O.CC_IN_PDF and "Ann Author" in entry["title"]
    nc, _ = O.obp_entry(work("https://creativecommons.org/licenses/by-nc/4.0/"))
    assert nc["personal_use"]
    assert O.obp_entry(work("https://creativecommons.org/licenses/by-nc-nd/4.0/"))[0] is None
    none, why = O.obp_entry(work(platform="ZENODO"))
    assert none is None and "Internet Archive" in why


def test_obp_newest_edition_and_dedup(monkeypatch):
    old = dict(work(title="A Book: First Edition"), workId="a", publicationDate="2010-01-01")
    new = dict(work(title="A Book (Second Edition)"), workId="b", publicationDate="2020-01-01")
    other = dict(work(title="Already Here"), workId="c")
    monkeypatch.setattr(O, "obp_works", lambda: [old, new, other])
    monkeypatch.setattr(O, "bucket", lambda text, n: 0)
    entries, left = O.obp_items("0", O.title_keys("Already Here"))
    assert [e["title"].split(" (")[0] for e in entries] == ["A Book"] and entries[0]["published"] == "2020-01-01"
    assert left[0]["reason"].startswith("Already in the library")


def otl(formats, licence="Attribution"):
    """A made-up Open Textbook Library record."""
    return {"id": 77, "title": "Plain Physics", "license": licence, "copyright_year": 2019, "description": "d",
            "contributors": [{"name": "Pat"}], "subjects": [{"name": "Physics"}], "publishers": [{"name": "U"}],
            "formats": formats}


def test_otl_entries():
    pdf = {"type": "PDF", "url": "https://example.edu/books/plain-physics.pdf"}
    entry, _ = O.otl_entry(otl([pdf]))
    assert entry["pdf"] == pdf["url"] and entry["licence"] == "CC BY" and entry["name"] == "otl_77"
    assert O.otl_entry(otl([pdf], "Attribution-NoDerivs"))[0] is None
    assert O.otl_entry(otl([pdf], "Free Documentation License (GNU)"))[0] is None
    lt = {"type": "Online", "url": "https://phys.libretexts.org/Bookshelves/x"}
    assert "LibreTexts" in O.otl_entry(otl([pdf, lt]))[1]
    pb = {"type": "PDF", "url": "https://open.pressbooks.pub/x/open/download?type=pdf"}
    assert O.otl_entry(otl([pb]))[0] is None
    assert O.otl_entry(otl([pdf], "Attribution-NonCommercial-ShareAlike"))[0]["personal_use"]


def test_ia_entries():
    doc = {"identifier": "abc123", "title": "Garden Book", "date": "1909", "creator": "Smith, J.",
           "publisher": "Doubleday", "licenseurl": "", "downloads": 9}
    old, _ = O.ia_entry(doc, "gardening", "old")
    assert old["old_public_domain"] and old["licence"] == O.OLD_LICENCE and "out of date" in old["description"]
    assert O.ia_entry(dict(doc, date="1950"), "gardening", "old")[0] is None
    cc = dict(doc, date="2015", licenseurl="https://creativecommons.org/licenses/by-sa/4.0/")
    entry, _ = O.ia_entry(cc, "gardening", "cc")
    assert entry["licence"] == "CC BY-SA 4.0" and entry["pdf_licence_text"] == O.CC_IN_PDF
    assert O.ia_entry(dict(cc, creator=""), "gardening", "cc")[0] is None        # no author: not taken
    assert O.ia_entry(dict(cc, licenseurl="http://creativecommons.org/publicdomain/mark/1.0/"), "gardening",
                      "cc")[0] is None                                           # an uploader's PD mark
    gov = dict(doc, date="1944", publisher="U.S. Govt. Print. Off.")
    entry, _ = O.ia_entry(gov, "cooking", "usgov")
    assert entry["licence"] == sources.US_GOV and entry["licence_page"] == sources.GOVINFO_POLICY
    assert O.ia_entry(dict(gov, publisher="Doubleday"), "cooking", "usgov")[0] is None
    for bad in (dict(doc, title="Seed catalogue 1909"), dict(doc, volume="12"),
                dict(doc, collection=["americana", "serials"])):
        assert O.ia_entry(bad, "gardening", "old")[0] is None


def test_keys_and_job_counts():
    keys = sources.expand_keys(["catalogues"])
    assert all(k.startswith("cat:") for k in keys) and len(keys) == len(set(keys))
    for name in O.SOURCES:
        assert 0 < len(sources.expand_keys([f"cat:{name}"])) <= 256
    assert sources.expand_keys(["cat:ia:old-birds"]) == ["cat:ia:old-birds"]
    assert O.SOURCES["otl"]["release"]("37") == "catalogue-otl-3"


def test_ai_blocked_host_not_read(monkeypatch):
    import cookbooks
    monkeypatch.setattr(cookbooks, "readable", lambda url, cache=None: False)
    monkeypatch.setattr(B, "pdfdoc_book", lambda *a, **k: (_ for _ in ()).throw(AssertionError("read")))
    left = []
    assert O.make_book({"title": "T", "pdf": "https://x.example/b.pdf"}, "unused", left_out=left) is None
    assert "AI companies" in left[0]["reason"]


def test_sign_when_source_cannot_be_asked(monkeypatch):
    def down():
        raise urllib.error.URLError("no network")
    monkeypatch.setattr(O, "obp_works", down)
    assert O.sign("cat:obp:3") == ""
