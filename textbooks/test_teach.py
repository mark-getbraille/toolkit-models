"""Self-test of the "Teaching and homeschooling" section (teach_index.py, teach_states.py and the books that moved into
the group, the owner's request of 23 November 2026), with MADE-UP data only: nothing is downloaded.

It checks that both modules are registered in the group "Teaching and homeschooling" (group key "k12") with their
request words (each at most 256 jobs, no key twice); that their prefixes clash with no other module; that every key,
pack and request word the guide names exists (other helpers' words only when their module is here); that the moved
books carry the group and keep their keys and words; that the state table has every state, DC and the five
territories, once each, with a law, an official page and a search result; that the law books read only official
addresses; that the curriculum books' licences are open or marked personal use; and that the index and law books are
made from made-up pages.

Run it from the repository's folder:   python3 -m pytest textbooks/test_teach.py
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import education_help as EDU  # noqa: E402
import education_more as EDM  # noqa: E402
import library_guide as LG  # noqa: E402
import more_refs  # noqa: E402
import oldbooks_life as OL  # noqa: E402
import open_catalogues as OC  # noqa: E402
import parenting as P  # noqa: E402
import practical_index as X  # noqa: E402
import read_aloud as RA  # noqa: E402
import sources  # noqa: E402
import teach_index as T  # noqa: E402
import teach_states as TS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

STATES_50 = {"alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
             "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
             "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana",
             "nebraska", "nevada", "new_hampshire", "new_jersey", "new_mexico", "new_york", "north_carolina",
             "north_dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode_island", "south_carolina",
             "south_dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington", "west_virginia",
             "wisconsin", "wyoming"}
TERRITORIES = {"puerto_rico", "guam", "us_virgin_islands", "american_samoa", "northern_mariana_islands"}


def listed_names(folder, code):
    """The names a small program prints in another folder of the repository (read in its own process)."""
    out = subprocess.run([sys.executable, "-c", code], cwd=os.path.join(HERE, "..", folder), capture_output=True,
                         text=True, check=True, timeout=300).stdout
    return set(out.split())


# ---------------------------------------------------------------------------------------------- wiring

def test_registered_in_the_teaching_group():
    assert sources.GROUPS["k12"] == "Teaching and homeschooling" == T.GROUP_NAME
    for m, prefix in ((T, "teach"), (TS, "tstate")):
        assert m in more_refs.modules() and more_refs.MODULES.count(m.__name__) == 1
        assert m.GROUP == m.COLLECTION.group == "k12"
        assert [o for o in more_refs.modules() if o.COLLECTION.prefix == prefix] == [m]
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert more_refs.module_for("teach:index") is T and more_refs.module_for("tstate:index") is TS
    assert TS.STATE_LAW in sources.ALLOWED


def test_request_words_and_sizes():
    words = ["teach-section", "homeschool", "teach-us", "tstate-laws", "tstate-curriculum", "tstate-northeast",
             "tstate-midwest", "tstate-south", "tstate-west", "tstate-territories"]
    for w in words:
        keys = sources.expand_keys([w])
        assert keys and len(keys) == len(set(keys)) <= 256, w
    us = set(sources.expand_keys(["teach-us"]))
    assert set(sources.expand_keys(["tstate-laws"])) | set(sources.expand_keys(["tstate-curriculum"])) == us
    regions = set()
    for r in TS.REGIONS:
        regions |= set(sources.expand_keys([f"tstate-{r}"]))
    assert regions == us
    assert set(TS.COLLECTION.own_keys()) == us
    assert "tstate:index" in sources.expand_keys(["teach-section"])
    for key in sources.expand_keys(["teach-section"]):
        assert X.key_exists(key), key


# ---------------------------------------------------------------------------------------------- the guide

def test_guide_names_only_things_that_exist():
    packs = listed_names("packs", "import build_packs; print(' '.join(build_packs.PACKS))")
    k12 = set(sources.expand_keys(["k12"]))
    ia = set(sources.expand_keys(["cat:ia"]))
    for _part, _intro, entries in T.SECTIONS:
        assert entries
        for kind, what, *_rest in entries:
            if kind == "key":
                assert X.key_exists(what), what
            elif kind == "pack":
                assert what in packs, what
            elif kind == "word" and what in T.OTHER_WORDS:
                answered = sources.expand_keys([what]) != [what]
                assert answered or more_refs.module_for(what) is None, what   # another helper's word, not here yet
            elif kind == "word":
                keys = sources.expand_keys([what])
                assert keys, what
                if what.startswith(("k12:", "osbooks:")):
                    assert what in k12, what
                if what.startswith("cat:"):
                    assert what in ia, what
            else:
                assert kind == "link" and _rest[0].startswith("https://"), what


def test_guide_covers_grades_subjects_and_braille():
    titles = " | ".join(t for t, _i, _e in T.SECTIONS).lower()
    for word in ("homeschooling", "early childhood", "elementary", "middle school", "high school", "reading",
                 "mathematics", "science", "history", "geography", "arts and music", "physical education",
                 "life skills", "special education", "braille"):
        assert word in titles, word
    words = {what for _p, _i, entries in T.SECTIONS for kind, what, *_r in entries if kind == "word"}
    assert {"teach-world", "pc-teaching", "lang-open", "languages-gov", "tstate-laws"} <= words
    keys = {what for _p, _i, entries in T.SECTIONS for kind, what, *_r in entries if kind == "key"}
    assert "tworld:index" in keys and sources.expand_keys(["teach-world"]) != ["teach-world"]


def test_guide_book_is_made(monkeypatch, tmp_path):
    real = X.key_exists
    monkeypatch.setattr(X, "key_exists", lambda key: key != "geo:factbook" and real(key))
    book_fn, sign_fn = T.INDEX
    left = []
    book = book_fn("index", str(tmp_path), None, left)
    assert len(book.pages) == len(T.SECTIONS) and any(r["title"] == "geo:factbook" for r in left)
    assert book.group == "k12" and sign_fn("index") == sign_fn("index")


def test_homeschool_booklets_are_federal_and_checked():
    for e in T.PDFS:
        assert e["group"] == "k12" and e["archive"].startswith("ERIC_ED") and e["pdf_licence_text"]
        assert e["licence"] == T.K.US_GOV and e["country"] == "United States"
    assert len({e["archive"] for e in T.PDFS}) == len(T.PDFS)


def test_library_guide_lists_the_section():
    assert LG.SECTIONS["k12"] == ("Teaching and homeschooling", "teach:index")
    for g, (_name, guide) in LG.SECTIONS.items():
        assert g in sources.GROUPS and X.key_exists(guide), g


# ---------------------------------------------------------------------------------------------- what moved

def test_moved_books_keep_keys_and_words():
    assert EDU.GROUP == EDM.GROUP == "k12" and EDU.GROUPS == {} and EDM.GROUPS == {}
    assert len(sources.expand_keys(["education"])) == len(EDU.GUIDES + EDU.PDFS)
    assert all(e["group"] == "k12" for e in EDU.GUIDES + EDU.PDFS + EDM.PDFS)
    teach = [e for e in OL.GUIDES + OL.PDFS if e.get("group") == "k12"]
    assert {e["name"] for e in teach} >= {"comstock_handbook_nature_study_1911", "nasa_exploring_the_moon_1994"}
    assert all(f"olife:{e['name']}" in sources.expand_keys(["oldbooks-life-science"]) for e in teach)
    cpir = [e for e in P.GUIDES if e["name"] == "cpir_parent_guides"]
    assert cpir[0]["group"] == "k12" and "parent:cpir_parent_guides" in sources.expand_keys(["parenting"])
    assert RA.TEACH_GROUP == "k12" and RA.GROUP == "parenting"
    assert OC.IA_TOPICS["teaching"][1] == "k12" and "cat:ia:old-teaching" in sources.expand_keys(["cat:ia"])
    for key in T.moved_keys():
        assert X.key_exists(key), key


def test_picture_books_are_teaching_and_rhymes_stay():
    """The levelled picture books get the teaching group; the nursery rhymes keep parenting."""
    src = open(os.path.join(HERE, "read_aloud.py"), encoding="utf-8").read()
    assert '"Children\'s picture books to read aloud", TEACH_GROUP' in src
    assert '"Nursery rhymes and fairy tales", GROUP' in src


# ---------------------------------------------------------------------------------------------- the state table

def test_every_state_dc_and_territory_once():
    keys = [s["key"] for s in TS.STATES]
    assert len(keys) == len(set(keys)) == 56
    assert set(keys) == STATES_50 | TERRITORIES | {"district_of_columbia"}
    assert {s["key"] for s in TS.STATES if s["region"] == "territories"} == TERRITORIES
    for s in TS.STATES:
        assert s["region"] in TS.REGIONS and s["law"] and s["says"].endswith(".") and s["result"] in TS.RESULTS
        assert s["page"].startswith("https://") and s["found"], s["key"]
        for kind, words, where in s["found"]:
            assert kind in ("built", "personal", "library", "link", "none") and words
            if kind in ("built", "personal"):
                assert where in TS.COLLECTION.own_keys(), where
            if kind == "library":
                assert X.key_exists(where) or sources.expand_keys([where]) != [where], where
            if kind == "link":
                assert where.startswith("https://"), where
        if s["result"] in ("built", "personal"):
            assert any(k == s["result"] for k, _w, _x in s["found"]), s["key"]


def test_law_books_read_only_official_addresses():
    blocked = ("justia", "findlaw", "casetext", "law.cornell", "lexis", "hslda", "responsiblehomeschooling",
               "public.law", "codes.findlaw")
    for s in TS.STATES:
        for url in s["statutes"]:
            assert url.startswith("https://") and not any(b in url for b in blocked), url
            assert any(part in url for part in (".gov", "legmt", "legislature", "ncleg", "ndlegis", "rilegislature",
                                                "scstatehouse", "wvlegislature", "legis.", "lis.virginia",
                                                "malegislature", "nebraskalegislature", "oksenate", "pa.gov",
                                                "nysed", "cga.ct", "ilga", "revisor", "codes.ohio", "app.leg.wa",
                                                "leg.state.")), url
    assert set(TS.law_regions()) == {"northeast", "midwest", "south", "west"}


def test_curriculum_books_are_open_or_marked_personal():
    for e in TS.PDFS:
        assert e["group"] == "k12" and e["pdf"].startswith("https://")
        kind = B.licence_kind(B.licence_short(e["licence"]))
        if e.get("personal_use"):
            assert kind.startswith("non-commercial"), e["name"]
        else:
            assert kind == "open", e["name"]
            assert e.get("pdf_licence_text") or e.get("licence_text"), e["name"]
    assert TS.STI_ENTRY["licence"] == "CC BY 4.0" and TS.STI_ENTRY["licence_text"]


def test_index_book_from_the_table(tmp_path):
    book = TS.index_book("index", str(tmp_path))
    assert [p.title for p in book.pages][0] == "The whole table" and len(book.pages) == 1 + len(TS.REGIONS)
    whole = book.pages[0].body
    for s in TS.STATES:
        assert s["name"] in whole, s["name"]
    assert "not searched in depth" in whole and "open, built here" in whole
    west = next(p for p in book.pages if p.path == "region-west").body
    assert "Washington" in west and "tstate:wa_since_time_immemorial" in west


def test_law_book_from_made_up_pages(monkeypatch, tmp_path):
    """The law book of a region: a page per state with an official address; a refused site is said in left_out."""
    import directory_sources as D
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: "refuse" not in url)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    monkeypatch.setattr(TS, "law_text", lambda url, cache=None: ("Section 1. Home school", "<p>A made-up law.</p>"))
    fake = [TS.S("alpha", "Alpha", "west", "Alpha Code 1", "https://example.gov/home", "Made up.",
                 ["https://example.gov/law"]),
            TS.S("beta", "Beta", "west", "Beta Code 2", "https://example.gov/b", "Made up.",
                 ["https://example.gov/refuse"]),
            TS.S("gamma", "Gamma", "west", "Gamma Code 3", "https://example.gov/g", "Made up.")]
    monkeypatch.setattr(TS, "STATES", fake)
    left = []
    book = TS.laws_book("homeschool_laws:west", str(tmp_path), None, left)
    assert [p.title for p in book.pages] == ["Alpha"] and "A made-up law." in book.pages[0].body
    assert any("Beta" in r["title"] for r in left)
    assert book.licence == TS.STATE_LAW


def test_since_time_immemorial_parts_from_made_up_pages(monkeypatch):
    """The unit pages' curriculum PDFs are found in order, each once, without the Spanish copies."""
    level = ('<a href="/student-success/resources-subject-area/john-mccoy-lulilas-time-immemorial-tribal-sovereignty-'
             'washington-state/elementary-curriculum/unit-1">Unit 1</a>')
    unit = ('<h1>Elementary Unit 1</h1><main><a href="/sites/default/files/u1-level1.pdf">Level 1 Curriculum</a>'
            '<a href="/sites/default/files/u1-level1-sv.pdf">Level 1 Curriculum</a>'
            '<a href="/sites/default/files/map.pdf">Map</a>'
            '<a href="/sites/default/files/u1-level1.pdf">Level 1</a></main>')

    def fake_fetch(url, cache=None, **kw):
        return unit if url.endswith("unit-1") else (level if "elementary" in url else "")
    monkeypatch.setattr(B, "fetch", fake_fetch)
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    parts = TS.sti_parts()
    assert parts == [("Elementary Unit 1: Level 1 Curriculum", "https://ospi.k12.wa.us/sites/default/files/u1-level1.pdf",
                      TS.STI + "/elementary-curriculum/unit-1")]
