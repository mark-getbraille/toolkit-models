"""Self-test of the Kiwix references, sheet music, historical newspapers and old-time radio collections (the owner's
request of 2026-11-22): stack_exchange.py (se:), a11y_community.py (a11yc:), sheet_music.py (music:), newspapers.py
(news:) and old_radio.py (otr:), with MADE-UP data only: nothing is downloaded.

It checks that each module is registered once in more_refs, its request word gives at most 256 jobs, its groups,
licence lines and NOT_INCLUDED rows (each with an address) reach sources.py; that the Stack Exchange books are marked
reference only everywhere (every site, every Kiwix label, the textbooks.json lists, the built catalogue entry) with
the owner's notice; that the share-alike books stay share-alike and every book's licence is one the toolkit may
repackage; that Mutopia licences are sorted into the right book and the NLS catalogue lines are matched under the
right composer; that the newspapers keep only issues more than 95 years old and say OCR errors are expected, and the
index names the writing kit's complete collection; that the radio books take only US government items; and that the
index books are made offline with keys the library has.

Run it from the repository's folder:   python3 -m pytest textbooks/test_kiwix_music_news.py
"""

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a11y_community  # noqa: E402
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import newspapers  # noqa: E402
import old_radio  # noqa: E402
import practical_index as X  # noqa: E402
import sheet_music  # noqa: E402
import sources  # noqa: E402
import stack_exchange  # noqa: E402

MODULES = [(stack_exchange, "stack-exchange"), (a11y_community, "a11y-community"), (sheet_music, "sheet-music"),
           (newspapers, "newspapers"), (old_radio, "old-radio")]


def no_fetch(monkeypatch):
    """Make any download fail the test."""
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))


def test_registered():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    for m, word in MODULES:
        assert m in more_refs.modules() and prefixes.count(m.COLLECTION.prefix) == 1, m.__name__
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        assert set(keys) <= set(m.COLLECTION.own_keys()) | {k for k in keys if k.startswith("news:state:")}
        for group, label in m.GROUPS.items():
            assert sources.GROUPS[group] == label and label.startswith("Reference, ")
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    assert sources.GROUPS["sheetmusic"] == "Reference, sheet music"
    assert sources.GROUPS["newspapers"] == "Reference, historical newspapers"
    assert sources.GROUPS["oldradio"] == "Reference, old-time radio"
    assert sources.expand_keys(["newspapers-front"]) == ["news:index", "news:front_pages"]
    assert len(sources.expand_keys(["newspapers"])) == 2 + len(newspapers.STATES)


def test_stack_exchange_is_reference_only():
    notice = "For reading and looking things up only; not for AI training (Stack Exchange's terms)."
    assert stack_exchange.REFERENCE_ONLY_NOTICE == notice
    names = [s["kiwix"] for s in stack_exchange.SITES]
    assert len(names) == len(set(names)) >= 40
    for s in stack_exchange.SITES:
        assert s["reference_only"] is True and s["notice"] == notice and "CC BY-SA" in s["licence"]
        assert s["kiwix"].endswith("_en_all") and any(h in s["kiwix"] for h in stack_exchange.SE_HOSTS)
    for site in ("diy", "cooking", "gardening", "bicycles", "outdoors", "electronics", "ham", "mechanics", "pets",
                 "sustainability", "woodworking", "crafts", "3dprinting", "money", "law", "travel", "parenting",
                 "lifehacks", "softwarerecs", "apple", "android"):
        assert f"{site}.stackexchange.com_en_all" in names, site
    for site in ("superuser.com_en_all", "askubuntu.com_en_all", "medicalsciences.stackexchange.com_en_all"):
        assert site in names
    assert set(stack_exchange.KIWIX_REFERENCE_ONLY) == set(names)
    assert all(notice in label for label in stack_exchange.KIWIX_LABELS.values())
    rows = " ".join(r[0] for r in stack_exchange.NOT_INCLUDED)
    assert "Accessibility Stack Exchange" in rows and "Health" in rows


def test_merged_catalogue_marks_reference_only(tmp_path):
    data = B.merge([], None, lambda url, cache=None: True)
    assert set(stack_exchange.KIWIX_REFERENCE_ONLY) <= set(data["kiwix_reference_only"])
    label = data["kiwix_labels"]["cooking.stackexchange.com_en_all"]
    assert stack_exchange.REFERENCE_ONLY_NOTICE in label             # wins over the cookbooks' plain label


def test_index_books_offline(monkeypatch, tmp_path):
    no_fetch(monkeypatch)
    for m in (stack_exchange, a11y_community, sheet_music, newspapers, old_radio):
        book_fn = m.COLLECTION.makers["index"][0]
        left_out = []
        book = book_fn("index", str(tmp_path), None, left_out)
        assert book.pages and book.licence == X.CC0_INDEX and not left_out, (m.__name__, left_out)
        assert '<a href="https://' in " ".join(p.body for p in book.pages)
    se = stack_exchange.COLLECTION.makers["index"][0]("index", str(tmp_path))
    assert all(B.esc(stack_exchange.REFERENCE_ONLY_NOTICE) in p.body for p in se.pages[:-1])


def test_stack_exchange_build_marks_entries(monkeypatch, tmp_path):
    no_fetch(monkeypatch)
    out = tmp_path / "out"
    manifests = stack_exchange.COLLECTION.build(["stack-exchange"], str(out), str(tmp_path / "cache"),
                                                datetime.date(2026, 11, 22), limit=2)
    entry = manifests["se:index"]["books"][0]
    assert entry["reference_only"] is True and entry["reference_only_notice"] == stack_exchange.REFERENCE_ONLY_NOTICE
    saved = json.loads((out / "manifest-se_index_sample.json").read_text())
    assert saved["books"][0]["reference_only"] is True


def test_licences():
    for m, _word in MODULES:
        for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values()):
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short) or B.licence_kind(g["licence"]), g["name"]
            assert g["description"] and g["notice"], g["name"]
    guides = a11y_community.COLLECTION.guides
    for name, licence in (("gnome_help_accessibility", "CC BY-SA 3.0"), ("arch_wiki_accessibility",
                                                                         "GFDL-1.3-or-later"),
                          ("kde_userbase_accessibility", "CC BY-SA 4.0")):
        assert guides[name]["licence"] == licence and B.licence_kind(B.licence_short(licence)) == "share-alike"
    assert sources.ALLOWED["GFDL-1.3-or-later"] == "share-alike"
    for lane, (_n, _t, licence, _u) in sheet_music.LANES.items():
        assert B.licence_kind(B.licence_short(licence)) == {"pd": "open", "by": "open", "sa": "share-alike"}[lane]


def test_mutopia_licence_lanes_and_fields():
    assert sheet_music.lane_of("Public Domain") == "pd"
    assert sheet_music.lane_of("Creative Commons Attribution 3.0") == "by"
    assert sheet_music.lane_of("Creative Commons Attribution 4.0") == "by"
    assert sheet_music.lane_of("Creative Commons Attribution-ShareAlike 2.5") == "sa"
    assert sheet_music.lane_of("Creative Commons Attribution-NonCommercial 3.0") == ""
    assert sheet_music.lane_of("") == ""
    rdf = ("<rdf:Description><mp:title>Made-up Prelude</mp:title><mp:composer>MadeUpA</mp:composer>"
           "<mp:for>Piano</mp:for><mp:licence>Public Domain</mp:licence><mp:lyFile>p.ly</mp:lyFile>"
           "</rdf:Description>")
    assert sheet_music.rdf_fields(rdf) == {"title": "Made-up Prelude", "composer": "MadeUpA", "for": "Piano",
                                           "licence": "Public Domain", "lyFile": "p.ly"}
    paths = [o[0] for o in sheet_music.OPUS]
    assert len(paths) == len(set(paths)) and all(o[4] in sheet_music.FAMILIES for o in sheet_music.OPUS)
    assert all(o[2] in sheet_music.COMPOSER_PAGES for o in sheet_music.OPUS)


def test_nls_matches_on_made_up_catalogue():
    lines = ["Bach, Carl Philipp Emanuel, 1714-1788", "Made-up Invention BRM 1111",
             "Bach, Johann Sebastian, 1685-1750", "Fugues, BWV 944. Fugue in A minor BRM 2222",
             "Jesu, Joy of Man's Desiring", "Inventions (Two part). BWV 772-786 BRM 3333", "Peters. bob. HC",
             "Toccata and Fugue in D minor", "Made-up publisher", "BRM 4444",
             "Beethoven, Ludwig van, 1770-1827", "Inventions of a made-up kind BRM 5555"]
    found = sheet_music.nls_matches(lines, "Bach, Johann Sebastian", r"invention")
    assert found == [("Inventions (Two part). BWV 772-786 BRM 3333", "BRM3333")]
    assert sheet_music.nls_matches(lines, "Bach, Johann Sebastian", r"toccata") == \
        [("Toccata and Fugue in D minor", "BRM4444")]
    assert sheet_music.nls_matches(lines, "Bach, Johann Sebastian", "") == []
    page = "<html><main><h2>Bach, Johann Sebastian</h2><p>Made-up &amp; work</p></main><footer>x</footer></html>"
    assert sheet_music.catalogue_lines(page) == ["Bach, Johann Sebastian", "Made-up & work"]


def test_score_page_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, **k: "\\version \"2.24\" { c'4 d' e' f' }")
    score = dict(composer="Made-up Composer", work="Made-up Work", family="keyboard", nls=r"made-up work",
                 nls_composer="Composer, Made-up", folder="https://www.mutopiaproject.org/ftp/X/Y/z/",
                 files=["z.ly", "z-a4.pdf", "z-let.pdf", "z.mid", "z.rdf", "z-preview.png"],
                 rdf={"title": "Made-up Work", "licence": "Public Domain", "lyFile": "z.ly"})
    catalogues = {"https://example.gov/cat": ["Composer, Made-up", "Made-up Work, op. 1 BRM 9999"]}
    page, originals = sheet_music.score_page(score, catalogues)
    assert "BRM9999" in page.body and "LilyPond text" in page.body and "c&#x27;4" in page.body
    assert {o["kind"] for o in originals} == {"ly", "pdf", "midi"} and len(originals) == 4
    assert page.unit == "Piano and keyboard"
    assert "no matching entry" in sheet_music.nls_note(dict(score, nls="other"), catalogues)


def test_newspapers_age_rule_and_notes(monkeypatch):
    assert newspapers.last_year(datetime.date(2026, 11, 22)) == 1930
    assert all(int(e[2][:4]) <= 1930 for e in newspapers.built_events(datetime.date(2026, 11, 22)))
    assert all(int(e[2][:4]) > 1930 for e in newspapers.LATER_EVENTS)
    assert {e[0] for e in newspapers.EVENTS} >= {"lincoln-1865", "maine-1898", "san-francisco-1906",
                                                 "armistice-1918", "crash-1929"}
    assert {e[0] for e in newspapers.LATER_EVENTS} >= {"pearl-harbor-1941", "ve-day-1945", "kennedy-1963"}
    assert "OCR" in newspapers.OCR_NOTE and "mistakes" in newspapers.NOTICE
    url = newspapers.search_url("1906-04-18", "1906-04-24", "new york")
    assert "location_state%3Anew+york" in url and "fo=json" in url and "dates=1906-04-18%2F1906-04-24" in url
    index = newspapers.index_book("index", "work")
    text = " ".join(p.body for p in index.pages)
    assert "american_stories_newspapers" in text and "dell-research-harvard/AmericanStories" in text
    answer = {"results": [
        {"date": "1906", "title": "Made-up Gazette (Town, Calif.) 1890-1910", "resources": []},
        {"date": "1906-04-19", "title": "Made-up Gazette (Town, Calif.), April 19, 1906",
         "resources": [{"url": "https://www.loc.gov/resource/sn000/1906-04-19/ed-1/"}],
         "location_state": ["california"]},
        {"date": "1906-04-20", "title": "Made-up Gazette (Town, Calif.), April 20, 1906",
         "resources": [{"url": "https://www.loc.gov/resource/sn000/1906-04-20/ed-1/"}]}]}
    monkeypatch.setattr(newspapers, "loc_json", lambda url, cache=None: answer)
    found = newspapers.issues("1906-04-18", "1906-04-24", "california")
    assert len(found) == 1 and found[0]["state"] == "California" and found[0]["date"] == "1906-04-19"


def test_newspaper_pages_keep_only_public_domain(monkeypatch):
    def made_up_page(issue, number, cache=None):
        rights = "" if "norights" in issue else "believed to be in the public domain"
        return f"MADE-UP OCR TEXT {number}", f"{issue}?sp={number}", 2, rights
    monkeypatch.setattr(newspapers, "page_text", made_up_page)
    found = [{"title": "A", "newspaper": "A", "date": "1906-04-19", "issue": "https://loc/a/", "state": "Ohio"},
             {"title": "B", "newspaper": "B", "date": "1906-04-19", "issue": "https://loc/norights/", "state": "Ohio"},
             {"title": "C", "newspaper": "C", "date": "1941-12-08", "issue": "https://loc/c/", "state": "Ohio"}]
    left = []
    body = newspapers.pages_html(found, "Made-up event", 4, None, left)
    assert "MADE-UP OCR TEXT 2" in body and "https://loc/a/?sp=1" in body and "Page 2" in body
    assert "norights" not in body and "loc/c" not in body and len(left) == 2


def test_radio_takes_only_government_items():
    gov = {"creator": ["United States. Department of Agriculture", "Writer, Made-up"],
           "rights": "The contributing institution believes that this item is not in copyright."}
    assert old_radio.government_item(gov)
    assert not old_radio.government_item(dict(gov, creator="Made-up Network", publisher="Made-up Press"))
    assert not old_radio.government_item(dict(gov, rights="All rights reserved"))
    assert old_radio.government_item({"creator": "United States. Office of War Information",
                                      "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/"})
    for p in old_radio.COLLECTION.pdfs.values():
        assert p["licence"] == "Public domain (US government work)" and p["archive"], p["name"]
    keys = sources.expand_keys(["old-radio"])
    assert "otr:usda_farm_home_hour:1928-1931" in keys and "otr:index" in keys
    rows = " ".join(r[0] + r[1] for r in old_radio.NOT_INCLUDED)
    assert "Generic Radio Workshop" in rows and "copyright of their respective owners" in rows
    assert "speech" in old_radio.__doc__ and "TEXT ONLY" in old_radio.__doc__
