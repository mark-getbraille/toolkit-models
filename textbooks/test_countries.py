"""Self-test of the countries of the world and maps (countries.py, ctry:), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once, in the world geography group, with its request words (each at most 256
jobs, every key in "countries", each continent word holding only books about its part of the world); that every book
has a licence the toolkit may repackage, its edition year, a description that says its facts are dated (or that it is
historical) and a notice; that the Library of Congress country studies are the 80 books of the Library's collection
(and Greece), checked against the Library's rights statement and the release rule for military publications; that the
older handbooks are from before 1978 and their front pages are checked for a copyright notice (tried on made-up
pages); that no Internet Archive item is built twice or by another module; that the copyrighted editions are link-only;
that the index finds other modules' books by country (made-up keys) and is made offline; that the World Bank and
several-PDF books are put together right (made-up books); and that the geography guide links the new books.

Run it from the repository's folder:   python3 -m pytest textbooks/test_countries.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import countries as C  # noqa: E402
import geography as G  # noqa: E402
import more_refs  # noqa: E402
import pdf_set  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

WORDS = [f"ctry-{w}" for w, _t in C.CONTINENTS] + ["ctry-maps", "countries"]


def test_registered_with_its_words():
    assert C in more_refs.modules()
    assert [m.COLLECTION.prefix for m in more_refs.modules()].count("ctry") == 1
    assert C.GROUP == "geography" and sources.GROUPS["geography"] == "Reference, world geography"
    for word in WORDS:
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        assert all(more_refs.module_for(k) is C for k in keys), word
        assert "ctry:index" in keys, word
    assert set(sources.expand_keys(["countries"])) == set(C.COLLECTION.own_keys())
    for word, _title in C.CONTINENTS:
        for key in sources.expand_keys([f"ctry-{word}"])[1:]:
            entry = C.COLLECTION.pdfs[key.split(":", 1)[1]]
            assert any(C.PLACES[p][1] == word for p in entry["places"]), (word, key)
    assert set(sources.expand_keys(["ctry-maps"])) == {"ctry:index"} | set(C.MAP_KEYS)
    assert set(C.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in C.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_every_book():
    for e in C.PDFS:
        assert e["group"] == C.GROUP and e["description"] and e["notice"] and e["published"], e["name"]
        assert B.licence_kind(e["licence"]) == "open", e["name"]
        assert re.fullmatch(r"[a-z0-9_]+", e["name"]), e["name"]
        if e.get("archive"):
            assert e["archive"] in e["version"], e["name"]
        if e in C.STUDY_PDFS + C.OLD_PDFS + C.BGN_PDFS:
            assert "Dated" in e["description"], e["name"]
            assert e["published"][:4] in e["title"] or C.month_words(e["published"]) in e["title"], e["name"]
            assert e["places"] and all(p in C.PLACES for p in e["places"]), e["name"]
    for e in C.OLD_GEO:
        assert e["old_public_domain"] and int(e["published"]) < 1931 and "Historical" in e["description"], e["name"]
    for e in C.BGN_PDFS:
        assert 1982 <= int(e["published"][:4]) <= 1990 and e["licence"] == K.US_GOV, e["name"]
    assert C.month_words("1986-07") == "July 1986"


def test_country_studies_are_the_library_of_congress_collection():
    assert len(C.STUDIES) == 81
    with_record = [s for s in C.STUDIES if s[4]]
    assert len(with_record) == 80                     # the 80 books of the Library's online collection
    assert [s[0] for s in C.STUDIES if not s[4]] == ["greece"]
    for e in C.STUDY_PDFS:
        assert e["military"] and "Library of Congress" in e["work"], e["name"]
        assert 1988 <= int(e["published"]) <= 2015, e["name"]
        if e["source"].startswith("https://www.loc.gov/item/"):
            assert e["licence_page"] == C.LOC_RIGHTS and e["licence_text"] == C.LOC_TEXT, e["name"]
            assert e["gov"].startswith("https://www.loc.gov/item/") and e["gov"].endswith("?fo=json"), e["name"]
            assert "public domain" in e["notice"] and "Secretary of the Army" in e["notice"], e["name"]
    assert re.search(C.LOC_TEXT, "Several of the books ... All other text and graphics are in the public domain.")
    # the countries that no longer exist are listed under today's countries
    pdfs = C.COLLECTION.pdfs
    assert {"Russia", "Ukraine", "Kazakhstan"} <= set(pdfs["cs_soviet_union"]["places"])
    assert set(pdfs["cs_czechoslovakia"]["places"]) == {"Czech Republic", "Slovakia"}
    assert pdfs["cs_zaire"]["places"] == ["Congo DR"]


def test_older_handbooks_front_pages_checked():
    front = C.OLD_FRONT
    good = ("AREA HANDBOOK for MADE-UP LAND Research completed 1970 For sale by the Superintendent of Documents, "
            "U.S. Government Printing Office FOREWORD This volume is one of a series of handbooks prepared by Foreign "
            "Area Studies (FAS) of The American University")
    assert re.search(front, good)
    assert re.search(front, "AREA HANDBOOK DA Pam 550-99 For sale by the Su\"erinteadent or Document.")  # misread
    assert not re.search(front, good + " Copyright (c) 1984 United States Government as represented by the Secretary")
    assert not re.search(front, "PERMISSION TO REPRODUCE THIS COPY- RIGHTED MATERIAL " + good)
    assert not re.search(front, good + " Distribution authorized to U.S. Government agencies only")
    assert not re.search(front, "A made-up book with no publisher line at all")
    for e in C.OLD_PDFS:
        assert int(e["published"]) < 1978 and e["pdf_licence_text"] == C.OLD_FRONT, e["name"]
        assert e["licence"] == C.AT.NO_NOTICE and "before 1978" in e["notice"], e["name"]
        assert "Historical" in e["description"], e["name"]
    # only for countries without a later edition the library may build
    built = {p for e in C.STUDY_PDFS for p in e["places"]}
    for e in C.OLD_PDFS:
        assert not set(e["places"]) & built, e["name"]


def test_nothing_built_twice():
    items = [e["archive"] for e in C.PDFS if e.get("archive")]
    assert len(items) == len(set(items))
    names = [e["name"] for e in C.PDFS] + list(C.MAKERS)
    assert len(names) == len(set(names))
    elsewhere = {e.get("archive") for e in sources.PDF_DOCS}
    for m in more_refs.modules():
        if m is not C:
            elsewhere |= {e.get("archive") for e in list(m.COLLECTION.pdfs.values()) + list(m.COLLECTION.guides.values())}
    assert not set(items) & elsewhere
    link_only = {item for _p, _t, item, _y, _w in C.LINK_ONLY}
    assert not link_only & set(items)
    assert all(p in C.PLACES for p, *_r in C.LINK_ONLY)


def test_places_named_by_made_up_keys():
    assert C.places_named("pclang:wolof_gambia_tape") == ["The Gambia"]
    assert C.places_named("hist:made_up_new_guinea_campaign") == ["Papua New Guinea"]
    assert set(C.places_named("pclang:kanuri_niger_chad_1966")) == {"Niger", "Chad"}
    assert C.places_named("hist:state_georgia_1908") == []
    assert C.places_named("hist:made_up_south_sudan_1990") == ["South Sudan"]
    assert C.places_named("lgov:cip_congo") == ["Congo DR"]
    assert C.places_named("lgov:cip_cote_divoire") == ["Cote d'Ivoire"]
    assert C.places_named("pclang:made_up_nigeria_1970") == ["Nigeria"]
    assert C.places_named("pc:made_up_united_states_guide") == []


def test_index_made_offline(monkeypatch):
    related = {"Chad": [("lgov:cip_chad", "Defense Language Institute", "Chad in Perspective")],
               "Niger": [("pc:made_up_missing", "Peace Corps", "A book that is not there")]}
    monkeypatch.setattr(C, "related_books", lambda: related)
    monkeypatch.setattr(X, "key_exists", lambda key: key != "pc:made_up_missing")
    left_out = []
    book = C.index_book("index", "work", None, left_out)
    titles = [p.title for p in book.pages]
    assert titles[0] == "How to use this guide" and titles[-1] == "Links only"
    assert [t for _w, t in C.CONTINENTS] == titles[1:7]
    africa = book.pages[1].body
    assert "<h2>Chad</h2>" in africa and "ctry:cs_chad" in africa and "lgov:cip_chad" in africa
    assert "geo:factbook" in africa and "Index: Africa" in africa
    assert "DTIC_ADA147503" in africa and "Link only" in africa                # the copyrighted Kenya edition
    assert "<h2>Niger</h2>" in africa and "pc:made_up_missing" not in africa
    assert left_out == [{"title": "pc:made_up_missing", "reason": "The library has no book with this key now."}]
    assert "contour lines" in book.pages[7].body and "ctry:usgs_exploring_maps" in book.pages[7].body
    assert book.group == C.GROUP and book.licence == X.CC0_INDEX
    assert len(C.index_book("index", "work", None, [], limit=2).pages) == 2


def test_index_keys_exist_in_the_library():
    for kind, what, *_rest in C.MAP_ENTRIES + C.WORLD_ENTRIES:
        if kind == "key":
            assert X.key_exists(what), what
    for word in ("lgov-dli-countries", "pub:history", "travel"):
        assert sources.expand_keys([word]), word


def test_world_bank_and_pdf_set_books(monkeypatch):
    def made_up_dspace(entry, work, cache=None, left_out=None):
        _site, handle, name, title, subject, body, licence = entry
        return K.new_book(name, title, subject, "reference", body, licence, "https://creativecommons.org/",
                          f"https://openknowledge.worldbank.org/handle/{handle}", "Made-up record.", "",
                          country="International", pages=[B.Page("p1", "One", "<p>x</p>"), B.Page("p2", "Two", "")])
    monkeypatch.setattr(B, "dspace_book", made_up_dspace)
    book = C.COLLECTION.book_for("ctry:wb_little_data_book_2016", "work", limit=1)
    assert book.group == C.GROUP and book.name == "ctry_wb_little_data_book_2016" and len(book.pages) == 1
    assert "CC BY 3.0 IGO" in book.notice and "World Bank" in book.notice and "10986/23968" in book.version

    seen = {}

    def made_up_set(entry, parts, work, cache=None, left_out=None, limit=None):
        seen["parts"] = parts
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], entry["source"], entry["description"], "",
                          pages=[B.Page("1-a", "A", "<p>a</p>")])
    monkeypatch.setattr(pdf_set, "pdf_set_book", made_up_set)
    garm = C.COLLECTION.book_for("ctry:census_garm", "work")
    assert garm.name == "ctry_census_garm" and garm.notice == C.CENSUS_GARM["notice"]
    assert len(seen["parts"]) == 17 and seen["parts"][1][1] == C.GARM_BASE + "Ch1GARM.pdf"
    basics = C.COLLECTION.book_for("ctry:usgs_map_basics", "work")
    assert basics.name == "ctry_usgs_map_basics" and len(seen["parts"]) == 4
    assert all(p[1].startswith("https://pubs.usgs.gov/") for p in seen["parts"])


def test_geography_guide_links_the_new_books():
    keys = {what for _p, _i, entries in G.SECTIONS for kind, what, *_r in entries if kind == "key"}
    assert {"ctry:index", "ctry:usgs_exploring_maps", "ctry:census_garm"} <= keys
    rows = " ".join(r[0] + r[1] for r in G.NOT_INCLUDED)
    assert "too old" not in rows and "ctry:bgn_" in rows
