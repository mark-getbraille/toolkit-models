"""Self-test of the history books (history.py, hist:), the further travel books (travel_more.py, tripmore:), the
further education books (education_more.py, edumore:) and their shared helpers (govinfo_kit.py), with MADE-UP data
only: nothing is downloaded.

It checks that each module is registered once under its request words (each at most 256 jobs), reaches sources.py
with its group, licence lines and NOT_INCLUDED rows (each with an address); that the history request words by era and
region together hold every history book; that every book has a licence the toolkit may repackage, a description and
a notice; that the old books are dated before 1931 and are marked as historical; that the Center of Military History
books are judged by the military release rule and read whole but for explosives parts; that the Park Service
handbooks are the numbered series read from npshistory.com; that the Department of Education booklets must print
their publisher on their front pages; that no Internet Archive item is used twice or by another module; that every
key the history index lists is in the library; that govinfo's search is a sign-up entry (no key: said where to sign
up; with a made-up key and made-up results: the public PDFs are read, the key goes only to api.govinfo.gov); that the
Wayback books read pinned "id_" captures; that the presidential addresses are found in made-up MODS records; that the
Public Papers index and the Library of Congress sets are made from made-up data; and that a key reaches its module
through the builder.

Run it from the repository's folder:   python3 -m pytest textbooks/test_history_travel_edu.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import court_opinions as C  # noqa: E402
import education_help  # noqa: E402
import education_more as EM  # noqa: E402
import govinfo_kit as GK  # noqa: E402
import history as H  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402
import travel  # noqa: E402
import travel_more as TM  # noqa: E402

WORDS = {H: ["history"] + list(H.WORD_TAGS), TM: ["travel-more"], EM: ["education-more"]}
GROUP_NAMES = {H: ("history", "Reference, history"), TM: ("travel", "Reference, travel"),
               EM: ("k12", "Teaching and homeschooling")}       # the teaching section since 2026-11-23


def entries(m):
    """Every web guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


# ====================================================================== registration

def test_registered_with_groups_lines_and_rows():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    for m, words in WORDS.items():
        assert m.__name__ in more_refs.MODULES and more_refs.MODULES.count(m.__name__) == 1
        assert m in more_refs.modules() and prefixes.count(m.COLLECTION.prefix) == 1
        group, name = GROUP_NAMES[m]
        # (education_more names no group of its own: "k12" is named in sources.GROUPS, the school books' group)
        assert m.GROUPS in ({group: name}, {}) and sources.GROUPS[group] == name
        for word in words:
            keys = sources.expand_keys([word])
            assert 0 < len(keys) == len(set(keys)) <= 256, word
            assert set(keys) <= set(m.COLLECTION.own_keys()), word
            assert all(more_refs.module_for(k) is m for k in keys), word
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    # siblings share their groups, never their prefixes
    assert TM.GROUPS == travel.GROUPS and EM.GROUPS == education_help.GROUPS
    assert TM.COLLECTION.prefix not in ("trip", "travel") and EM.COLLECTION.prefix != "edu"
    assert "govinfo_kit" not in more_refs.MODULES          # a helper, not a source module


def test_history_words_cover_every_book():
    every = sources.expand_keys(["history"])
    assert set(every) == set(H.COLLECTION.own_keys()) and every[0] == "hist:index"
    by_era = set()
    for word in H.WORD_TAGS:
        by_era |= set(sources.expand_keys([word]))
    assert by_era | {"hist:index"} == set(every)
    people = sources.expand_keys(["history-people"])
    for key in ("hist:woodson_negro_in_our_history_1927", "hist:hodge_handbook_american_indians_v1_1907",
                "hist:stanton_anthony_gage_woman_suffrage_v1_1881", "hist:best_the_blind_1919",
                "hist:riis_how_the_other_half_lives_1890", "hist:cmh_11_4_1_employment_of_negro_troops"):
        assert key in people, key
    assert all(k.startswith("hist:state_") for k in sources.expand_keys(["history-states"])[1:])
    assert len(sources.expand_keys(["history-states"])) >= 20


# ====================================================================== the books

def test_every_book_licence_description_notice():
    for m in WORDS:
        for g in entries(m):
            assert g["group"] == GROUP_NAMES[m][0] and g["description"] and g["notice"], g["name"]
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short) or B.licence_kind(g["licence"]), g["name"]
            assert g.get("licence_page") or g.get("old_public_domain"), g["name"]
            if g.get("old_public_domain"):
                assert int(g["published"]) < 1931 and "Published in" in g["description"], g["name"]
                assert "historical" in g["description"], g["name"]
                assert g["archive"] and g["licence"] == "Public domain (published before 1931)", g["name"]


def test_military_history_release_rule_and_explosives_cut():
    cmh = [g for g in H.PDFS if g["name"].startswith("cmh_")]
    assert len(cmh) >= 40
    for g in cmh:
        assert g["distribution_a"] and g["archive"] and g["published"], g["name"]
        assert "front pages print" in g["notice"] and "explosives" in g["notice"], g["name"]
    assert B.NOT_FIELD_SAFE.search("Chapter 9: Mines and Booby Traps")
    assert not B.NOT_FIELD_SAFE.search("Chapter 9: The Battle of Normandy")


def test_park_service_handbooks():
    handbooks = [g for g in H.PDFS if g["name"].startswith("nps_handbook_")]
    assert [int(g["name"].split("_")[2]) for g in handbooks] == list(range(1, 41))
    for g in handbooks:
        assert g["pdf"].startswith("https://npshistory.com/handbooks/historical/") and g["pdf"].endswith(".pdf")
        assert g["licence"] == K.US_GOV and "National Park Service" in g["notice"] and int(g["published"]) < 1970
    rows = " ".join(r[0] + r[1] for r in H.NOT_INCLUDED)
    assert "outside authors" in rows and "Blassingame" in rows


def test_education_booklets_print_their_publisher():
    eric = [g for g in EM.PDFS if g.get("archive", "").startswith("ERIC_")]
    assert len(eric) >= 10
    for g in eric:
        assert g["pdf_licence_text"] == EM.ED_FRONT and g["licence"] == K.US_GOV, g["name"]
    assert re.search(EM.ED_FRONT, "U.S. Department of Education Office of Communications")
    assert re.search(EM.ED_FRONT, "National Institute for Literacy")
    assert "ERIC_ED583977" not in {g.get("archive") for g in EM.PDFS}       # its publisher is not stated
    fafsa = EM.COLLECTION.pdfs["fafsa_form_2026_27"]
    assert fafsa["pdf"] == f"https://web.archive.org/web/{EM.FAFSA_STAMP}id_/{EM.FAFSA}"
    assert EM.LEGAL in fafsa["notice"]


def test_no_internet_archive_item_twice():
    mine = [H, TM, EM]
    others = {e["archive"] for e in sources.PDF_DOCS if e.get("archive")}
    for m in more_refs.modules():
        if m not in mine:
            others |= {e["archive"] for e in m.COLLECTION.pdfs.values() if e.get("archive")}
    items = [e["archive"] for m in mine for e in m.COLLECTION.pdfs.values() if e.get("archive")]
    assert len(items) == len(set(items))
    assert not set(items) & others, set(items) & others


def test_history_index_keys_exist_and_index_is_made_offline():
    for _part, _intro, rows in H.SECTIONS:
        for kind, what, *_rest in rows:
            if kind == "key":
                assert X.key_exists(what), what
    left_out = []
    book = H.INDEX[0]("index", "work", None, left_out)
    assert len(book.pages) == len(H.SECTIONS) and not left_out and book.licence == "CC0 1.0"


def test_nara_milestone_documents():
    g = H.COLLECTION.guides["nara_milestone_documents"]
    assert len(H.NARA_DOCS) == len(set(H.NARA_DOCS)) == 96
    pattern = re.compile(g["pages"])
    assert all(pattern.match(u) for u in g["urls"]) and not pattern.match(f"{H.NARA}/list")
    rules = g["unit_rules"]
    assert re.search(rules[0][0], f"{H.NARA}/declaration-of-independence")
    assert re.search(rules[2][0], f"{H.NARA}/emancipation-proclamation")


# ====================================================================== govinfo's search: a sign-up entry

def test_govinfo_search_is_a_sign_up_entry(monkeypatch):
    monkeypatch.delenv(GK.GOVINFO_KEY_ENV, raising=False)
    monkeypatch.setattr(GK, "search", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no call")))
    for m, name in ((TM, "govinfo_travel_publications"), (EM, "govinfo_education_publications")):
        left_out = []
        assert m.COLLECTION.makers[name][0](name, "work", None, left_out) is None
        assert "sign-up entry" in left_out[0]["reason"] and GK.GOVINFO_KEY_ENV in left_out[0]["reason"]
        assert left_out[0]["fetch_yourself"] and left_out[0]["url"] == GK.GOVINFO_SIGNUP
    for m in (TM, EM):                                   # no key is ever written in the module
        text = open(m.__file__, encoding="utf-8").read()
        assert "api_key=" not in text and "DEMO_KEY" not in text


def test_govinfo_search_with_a_made_up_key(monkeypatch):
    sent = []

    class Answer:
        """A made-up HTTP answer."""

        def __init__(self, data):
            self.data = data

        def read(self):
            return json.dumps(self.data).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(url, secret_headers, data=None, headers=None, method=None, timeout=0):
        """A made-up api.govinfo.gov (in place of build_textbooks.keyed_urlopen): records what was sent and answers
        three made-up results."""
        sent.append((url, json.loads(data), secret_headers))
        return Answer({"results": [
            {"title": "Fly Rights: A Consumer Guide to Air Travel", "packageId": "GOVPUB-TD-made-up1",
             "collectionCode": "GOVPUB", "dateIssued": "2004-01-01"},
            {"title": "Annual budget tables", "packageId": "GOVPUB-TD-made-up2", "collectionCode": "GOVPUB"},
            {"title": "Fly Rights: A Consumer Guide to Air Travel", "packageId": "GOVPUB-TD-made-up1",
             "collectionCode": "GOVPUB"}]})

    monkeypatch.setenv(GK.GOVINFO_KEY_ENV, "made-up-key")
    monkeypatch.setattr(B, "keyed_urlopen", fake_urlopen)
    got = {}

    def fake_set(entry, parts, work, cache=None, left_out=None, limit=None):
        """A made-up pdf_set.pdf_set_book: keeps the parts and returns a one-page book."""
        got["parts"], got["entry"] = parts, entry
        book = B.Book(name=entry["name"], title=entry["title"], subject=entry["subject"], level="reference",
                      group=entry["group"], publisher=entry["publisher"], country=entry["country"],
                      licence=entry["licence"], licence_url=entry["licence_url"], source=entry["source"],
                      description=entry["description"])
        book.pages.append(B.Page("p1", "Page", "<p>made up</p>", 1, ""))
        return book

    import pdf_set
    monkeypatch.setattr(pdf_set, "pdf_set_book", fake_set)
    left_out = []
    book = TM.COLLECTION.makers["govinfo_travel_publications"][0]("govinfo_travel_publications", "work", None,
                                                                   left_out)
    assert book is not None and not left_out
    url, body, secret = sent[0]
    # the key goes in the X-Api-Key header, never in the address (which can end up in logs)
    assert url == f"{GK.GOVINFO_API}/search" and secret == {"X-Api-Key": "made-up-key"}
    assert "collection:GOVPUB" in body["query"]
    assert got["parts"] == [("Fly Rights: A Consumer Guide to Air Travel (2004-01-01)",
                             "https://www.govinfo.gov/content/pkg/GOVPUB-TD-made-up1/pdf/GOVPUB-TD-made-up1.pdf",
                             "https://www.govinfo.gov/app/details/GOVPUB-TD-made-up1")]
    assert book.published == "2004-01-01" and got["entry"]["licence"] == K.US_GOV
    assert GK.public_pdf("PPP-2009-book1", "PPP-2009-book1-doc-pg1") == \
        "https://www.govinfo.gov/content/pkg/PPP-2009-book1/pdf/PPP-2009-book1-doc-pg1.pdf"


# ====================================================================== the Wayback Machine's copies

def test_wayback_books_read_pinned_exact_captures():
    for g in TM.GUIDES:
        pattern = re.compile(g["pages"])
        assert g["urls"] and all(pattern.match(u) and "id_/https://" in u for u in g["urls"]), g["name"]
        stamps = [re.search(r"/web/(\d{14})id_/", u).group(1) for u in g["urls"]]
        assert all(s >= "20240101000000" for s in stamps), g["name"]           # nothing older than 2024
        assert g["published"] == GK.stamp_date(max(stamps)) and "Wayback Machine" in g["notice"], g["name"]
        assert g["licence"] == K.US_GOV and g["licence_page"] == K.GOVINFO_POLICY
    assert GK.capture("20261115231232", "https://www.transportation.gov/airconsumer/fly-rights") == \
        "https://web.archive.org/web/20261115231232id_/https://www.transportation.gov/airconsumer/fly-rights"


# ====================================================================== the Public Papers

MODS = """<mods xmlns="http://www.loc.gov/mods/v3">
<relatedItem type="constituent" ID="id-PPP-2009-book1-doc-pg1"><titleInfo><title>Inaugural Address</title>
</titleInfo><originInfo><dateIssued>2009-01-20</dateIssued></originInfo>
<identifier type="uri">https://www.govinfo.gov/app/details/PPP-2009-book1/PPP-2009-book1-doc-pg1</identifier>
<location><url displayLabel="PDF rendition" xlink:href="https://www.govinfo.gov/content/pkg/PPP-2009-book1/pdf/PPP-2009-book1-doc-pg1.pdf">x</url></location>
</relatedItem>
</mods>"""


def test_selected_addresses_from_made_up_records(monkeypatch):
    monkeypatch.setattr(C, "read_mods", lambda package, cache=None: MODS if package == "PPP-2009-book1" else "")
    got = {}

    def fake_set(entry, parts, work, cache=None, left_out=None, limit=None):
        """A made-up pdf_set.pdf_set_book: keeps the parts and returns a one-page book."""
        got["parts"] = parts
        book = B.Book(name=entry["name"], title=entry["title"], subject=entry["subject"], level="reference",
                      group=entry["group"], publisher=entry["publisher"], country=entry["country"],
                      licence=entry["licence"], licence_url=entry["licence_url"], source=entry["source"],
                      description=entry["description"])
        book.pages.append(B.Page("p1", "Page", "<p>made up</p>", 1, ""))
        return book

    import pdf_set
    monkeypatch.setattr(pdf_set, "pdf_set_book", fake_set)
    left_out = []
    book = H.PPP_BOOK[0]("ppp_selected_addresses", "work", None, left_out)
    assert got["parts"] == [("Inaugural Address (2009-01-20)", "https://www.govinfo.gov/content/pkg/PPP-2009-book1/"
                             "pdf/PPP-2009-book1-doc-pg1.pdf", "https://www.govinfo.gov/app/details/PPP-2009-book1/"
                             "PPP-2009-book1-doc-pg1")]
    assert book.published == "2009-01-20"
    assert len(left_out) == len(H.PPP_SELECTED) - 1          # the others have no record in this test
    assert all("no record" in x["reason"] for x in left_out)
    assert all(p.startswith("PPP-") and g.startswith(p + "-doc-") for p, g, _n in H.PPP_SELECTED)


def test_public_papers_index_made_offline():
    volumes = H.ppp_volumes()
    assert len(volumes) >= 120 and volumes[0][0] == "PPP-1929-book1"
    assert H.ppp_president(volumes[0][1]) == "Herbert Hoover"
    book = H.ppp_index_book("ppp_index", "work")
    names = [p.title for p in book.pages]
    assert names[0] == "Herbert Hoover" and "John F. Kennedy" in names and "Barack Obama" in names
    assert names[-1] == "The Compilation of Presidential Documents"
    kennedy = book.pages[names.index("John F. Kennedy")].body
    assert "https://www.govinfo.gov/content/pkg/PPP-1961-book1/pdf/PPP-1961-book1.pdf" in kennedy
    assert book.licence == "CC0 1.0" and H.ppp_index_sign("ppp_index") == H.ppp_index_sign("ppp_index")


# ====================================================================== the Library of Congress's sets

def test_library_of_congress_sets_from_made_up_answers(monkeypatch):
    listing = {"results": [
        {"title": "Made-up Set", "url": "https://www.loc.gov/classroom-materials/made-up-set/",
         "partof_type": ["primary source set"]},
        {"title": "A lesson", "url": "https://www.loc.gov/classroom-materials/a-lesson/",
         "partof_type": ["lesson plan"]}], "pagination": {"next": None}}
    one = {"era": ["The New Nation, 1783 to 1815"],
           "content": {"components": [{"html": "<nav><a href='#x'>Jump</a></nav><h2>Background</h2><p>Made up "
                                               "essay.</p><img src='x.jpg'>"}]},
           "set": [{"title": "A made-up letter\n", "link": "/resource/mss0001/"}]}

    def fake_fetch(url, cache=None, binary=False):
        """Made-up loc.gov and govinfo.gov answers."""
        if url.startswith(K.GOVINFO_POLICY):
            return "Copyright protection under this title is not available for any work of the United States " \
                   "Government"
        if "fa=partof_type" in url:
            return json.dumps(listing)
        assert "made-up-set" in url and url.endswith("fo=json")
        return json.dumps(one)

    monkeypatch.setattr(B, "fetch", fake_fetch)
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    book = H.loc_sets_book("loc_primary_source_sets", "work")
    assert [p.title for p in book.pages] == ["Made-up Set"]
    body = book.pages[0].body
    assert "Made up essay" in body and "<nav" not in body and "<img" not in body
    assert "https://www.loc.gov/resource/mss0001/" in body and "A made-up letter" in body
    assert book.pages[0].unit == "The New Nation, 1783 to 1815" and book.licence == K.US_GOV


def test_library_of_congress_listing_falls_back_when_search_is_empty(monkeypatch):
    answers = {H.LOC_SETS: {"results": [], "pagination": {"next": None}},
               H.LOC_ALL: {"results": [{"title": "Set A", "url": "https://www.loc.gov/classroom-materials/a/",
                                        "partof_type": ["primary source set"]},
                                       {"title": "Lesson B", "url": "https://www.loc.gov/classroom-materials/b/",
                                        "partof_type": ["lesson plan"]}], "pagination": {"next": None}}}
    seen = []

    def fake_fetch(url, cache=None, binary=False):
        """Made-up loc.gov and govinfo.gov answers."""
        seen.append(cache)
        return json.dumps(answers[url])

    monkeypatch.setattr(B, "fetch", fake_fetch)
    assert H.loc_set_list("some-cache") == [("Set A", "https://www.loc.gov/classroom-materials/a/")]
    assert seen == [None, None]                       # the listing is never read from the cache folder


# ====================================================================== wiring

def test_keys_reach_their_modules_through_the_builder(monkeypatch, tmp_path):
    for m, key in ((H, "hist:index"), (TM, "tripmore:tsa_wayback"), (EM, "edumore:fafsa_form_2026_27")):
        called = []
        monkeypatch.setattr(m.COLLECTION, "build", lambda keys, out, cache=None, date=None, c=called:
                            c.append(keys) or {})
        assert more_refs.owns(key) and more_refs.module_for(key) is m
        B.build([key], str(tmp_path))
        assert called == [[key]], key
