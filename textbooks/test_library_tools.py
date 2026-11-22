"""Self-test of the library tools (tools/library_common.py, tools/size_plan.py, tools/health_check.py), with MADE-UP
data only: nothing is downloaded. It lives here so the textbooks tests (run by CI) run it.

It checks the small helpers (sizes in words, file stems and newest versions, licence classes, failure causes, job
names), the Writing Kit reader on a made-up source file, the size plan's parts (made-up releases, a made-up Kiwix
listing, made-up Hugging Face and CourtListener answers) and its drive advice, and the health check's sorting of
packs, books and manual collections into failed, still building, nearly empty and not built yet.

Run it from the repository's folder:   python3 -m pytest textbooks/test_library_tools.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import health_check as H  # noqa: E402
import library_common as C  # noqa: E402
import size_plan as S  # noqa: E402

GB = 10 ** 9


# ====================================================================== library_common

def test_size_words_and_parse():
    assert C.size_words(950) == "950 bytes"
    assert C.size_words(1_200_000) == "1.2 MB"
    assert C.size_words(3_400_000_000_000) == "3.4 TB"
    assert C.size_words(None) == "size not known"
    assert C.parse_size("115G") == 115 * GB
    assert C.parse_size("1.7 GB") == int(1.7 * GB)
    assert C.parse_size("about 330 MB of text") == 330 * 10 ** 6
    assert C.parse_size("no size here") is None


def test_stems_and_newest_versions():
    assert C.file_stem("nasa_news.2026-11-19.zim") == C.file_stem("nasa_news.2026-11-22.zim") == "nasa_news.zim"
    assert C.file_stem("loc_fsa.pass2.zip.003") == "loc_fsa.zip"
    assert C.file_stem("voa_learning_1978-04.zim") != C.file_stem("voa_learning_1978-05.zim")    # monthly pieces
    assert C.file_stem("manuals-toasters.2026-11-21.json.gz") == "manuals-toasters.json.gz"
    assert C.tag_stem("packs-detail-20261112") == C.tag_stem("packs-detail-20261122") == "packs-detail"
    files = [{"name": "made_up_book.2026-11-01.zim", "size": 10},
             {"name": "made_up_book.2026-11-20.zim", "size": 12},
             {"name": "pack.zip.001", "size": 5}, {"name": "pack.zip.002", "size": 6},
             {"name": "pack.pass2.zip.001", "size": 7}, {"name": "pack.pass2.zip.002", "size": 8},
             {"name": "packs.json", "size": 1}]
    newest = {f["name"] for f in C.newest_only(files)}
    assert newest == {"made_up_book.2026-11-20.zim", "pack.pass2.zip.001", "pack.pass2.zip.002", "packs.json"}
    # the same file name in two dated releases of one series: only the later release's copy
    series = [{"name": "region.osmpack", "size": 3, "release": "packs-detail-20261112"},
              {"name": "region.osmpack", "size": 4, "release": "packs-detail-20261122"},
              {"name": "other.osmpack", "size": 5, "release": "packs-detail-20261112"}]
    assert sorted(f["size"] for f in C.newest_only(series)) == [4, 5]


def test_licence_classes():
    assert C.licence_class("open") == C.licence_class("no-changes") == "open"
    assert C.licence_class("share-alike") == C.licence_class("CC BY-SA 4.0") == "share-alike"
    assert C.licence_class("non-commercial") == C.licence_class("CC BY-NC-SA 4.0") == "personal use"
    assert C.licence_class("research") == "personal use"
    assert C.licence_class("open", personal=True) == "personal use"
    assert C.licence_class("open", link_only=True) == C.licence_class("") == "link-only"


def test_causes():
    assert C.cause_of("RuntimeError: the site kept refusing requests (429)").startswith("too many requests")
    assert C.cause_of("Its site refuses automated requests (403).").startswith("refused by the site")
    assert C.cause_of("It could not be read (HTTP Error 404: Not Found).").startswith("not found")
    assert C.cause_of("Not repackaged: no derivatives.") == "licence does not allow it"
    assert C.cause_of("something odd") == C.OTHER_CAUSE
    log = ("2026-11-22T10:00:00Z Reading page 3\n2026-11-22T10:00:01Z HTTP Error 429: Too Many Requests\n"
           "2026-11-22T10:00:02Z RuntimeError: gave up\n2026-11-22T10:00:03Z ##[error]Process completed with exit "
           "code 1.\n2026-11-22T10:00:04Z Cleaning up orphan processes")
    assert C.log_cause(log).startswith("too many requests")
    assert C.failure_line(log) == "RuntimeError: gave up"
    assert C.failure_line("no error line\nCleaning up orphan processes") == ""
    assert C.log_cause("ModuleNotFoundError: No module named 'made_up'").startswith("a program part was missing")


def test_job_names_and_states():
    assert C.job_key("build / build (loc_world)") == ["loc_world"]
    assert C.job_key("build (pub:voa:recent+pub:voa:2026)") == ["pub:voa:recent", "pub:voa:2026"]
    assert C.job_key("build (loc_fsa+)") == ["loc_fsa"] and C.job_key("build (loc_fsa?)") == ["loc_fsa"]
    assert C.job_key("plan") == []
    jobs = [{"name": "build (a)", "status": "completed", "conclusion": "failure", "started_at": "2026-11-22T09:00",
             "id": 1},
            {"name": "build (a)", "status": "completed", "conclusion": "cancelled", "started_at": "2026-11-22T11:00",
             "id": 2},
            {"name": "build (b)", "status": "in_progress", "started_at": "2026-11-22T10:00", "id": 3},
            {"name": "build (c)", "status": "queued", "created_at": "2026-11-22T10:00", "id": 4},
            {"name": "build (c)", "status": "completed", "conclusion": "success", "started_at": "2026-11-21T10:00",
             "id": 5}]
    st = C.job_states(jobs, "packs.yml")
    assert st["a"]["state"] == "failed" and st["a"]["id"] == 1          # the cancelled newer job does not count
    assert st["b"]["state"] == "building" and st["c"]["state"] == "queued"


def test_data_releases():
    assert C.is_data_release({"tag_name": "training-data", "assets": []})
    assert C.is_data_release({"tag_name": "made-up", "assets": [{"name": "x.zim"}, {"name": "notes.txt"}]})
    assert C.is_data_release({"tag_name": "v1", "assets": [{"name": "a.zip"}, {"name": "list.json"}]})
    assert not C.is_data_release({"tag_name": "v1.4", "assets": [{"name": "Program Setup.exe"}]})


WRITING_FILE = '''
from dataclasses import dataclass
OPEN, SHARE_ALIKE, PERSONAL = "open", "share-alike", "personal use only"
MADE_UP_LICENCE = "CC BY 4.0"
SOURCES = [
    Source(key="madeup_letters", name="Made-up letters", licence=MADE_UP_LICENCE, licence_class=OPEN,
           licence_url="x", credit="x", home="x", reader="read_x", notes="One official file, 2.5 GB in all."),
    Source(key="madeup_chat", name="Made-up chat", licence="none", licence_class=PERSONAL, licence_url="x",
           credit="x", home="x", reader="read_y", notes="Small."),
]
def sources(Source, OPEN, SHARE_ALIKE, PERSONAL):
    return [Source(key="madeup_wiki", name="Made-up wiki", licence="CC BY-SA", licence_class=SHARE_ALIKE,
                   licence_url="x", credit="x", home="x", reader="r", style="news")]
'''
STYLES_FILE = 'BY_SOURCE = {"madeup_letters": "letter_personal", "madeup_chat": "chat"}\n'


def test_writing_kit_reader_parses_without_running():
    found = {s["key"]: s for s in C.parse_writing_sources({"writing_sources.py": WRITING_FILE,
                                                             "styles.py": STYLES_FILE,
                                                             "broken.py": "this is not ( python"})}
    assert set(found) == {"madeup_letters", "madeup_chat", "madeup_wiki"}
    assert found["madeup_letters"]["class"] == "open" and found["madeup_letters"]["style"] == "letter_personal"
    assert found["madeup_letters"]["size"] == "2.5 GB" and found["madeup_letters"]["size_bytes"] == int(2.5 * GB)
    assert found["madeup_chat"]["class"] == "personal use only" and found["madeup_chat"]["size"] == ""
    assert found["madeup_wiki"]["class"] == "share-alike" and found["madeup_wiki"]["style"] == "news"


# ====================================================================== size_plan

def made_up_releases(repo):
    """Two made-up repositories' releases."""
    if repo.endswith("toolkit-models"):
        return [{"tag_name": "textbooks", "assets": [
                    {"name": "made_up_book.2026-11-01.zim", "size": 4 * GB},
                    {"name": "made_up_book.2026-11-20.zim", "size": 5 * GB},
                    {"name": "textbooks.json", "size": 1}]},
                {"tag_name": "training-data", "assets": [{"name": "pack.zip", "size": 100 * GB},
                                                         {"name": "packs.json", "size": 1}]},
                {"tag_name": "library-reports", "assets": [{"name": "size-plan.json", "size": 9}]},
                {"tag_name": "maps-20261101", "assets": [{"name": "a.osmpack", "size": 2 * GB},
                                                        {"name": "b.osmpack", "size": 1 * GB}]},
                {"tag_name": "maps-20261120", "assets": [{"name": "a.osmpack", "size": 3 * GB}]},
                {"tag_name": "v2", "assets": [{"name": "Setup.exe", "size": 3 * GB}]},
                {"tag_name": "draft-data", "draft": True, "assets": [{"name": "x.zim", "size": 1}]}]
    return []


def test_github_rows_count_every_version_and_newest():
    rows, unread = S.github_rows(["o/toolkit-models", "o/place-packs"], made_up_releases)
    assert unread == ["o/place-packs"]
    by = {r["item"]: r for r in rows}
    assert set(by) == {"toolkit-models: textbooks", "toolkit-models: training-data",     # program, own reports out
                       "toolkit-models: maps-20261101, maps-20261120"}
    maps = by["toolkit-models: maps-20261101, maps-20261120"]
    assert maps["all"] == 6 * GB and maps["newest"] == 4 * GB          # a.osmpack from the later release, and b
    assert by["toolkit-models: textbooks"]["all"] == 9 * GB + 1
    assert by["toolkit-models: textbooks"]["newest"] == 5 * GB + 1
    assert by["toolkit-models: training-data"]["area"] == "Picture packs (training data)"


TOP = '<a href="?C=N;O=D">Name</a> <a href="/kiwix/">Parent</a> <a href="wikipedia/">wikipedia/</a> ' \
      '<a href="other/">other/</a>'
WIKI = """<img> <a href="wikipedia_en_all_maxi_2026-02.zim">wikipedia_en_all_maxi_2026-02.zim</a>   2026-02-26 03:08  115G
<img> <a href="wikipedia_en_all_maxi_2026-08.zim">wikipedia_en_all_maxi_2026-08.zim</a>   2026-09-08 20:38  119G
<img> <a href="wikipedia_en_all_nopic_2026-08.zim">wikipedia_en_all_nopic_2026-08.zim</a>   2026-09-08 20:38  60G
<img> <a href="wikipedia_fr_all_maxi_2026-08.zim">wikipedia_fr_all_maxi_2026-08.zim</a>   2026-09-08 20:38  40G
"""
OTHER = '<img> <a href="madeup_en_all_2026-10.zim">madeup_en_all_2026-10.zim</a>   2026-10-01 10:00  1.5G \n'


def fake_get(url):
    """Made-up answers of the Kiwix mirror and the CourtListener bucket."""
    if url == S.KIWIX_MIRROR:
        return TOP
    if url.endswith("wikipedia/"):
        return WIKI
    if url.endswith("other/"):
        return OTHER
    if "courtlistener" in url:
        return ("<Contents><Key>bulk-data/opinions-2025-01-31.csv.bz2</Key><Size>40000000000</Size></Contents>"
                "<Contents><Key>bulk-data/opinions-2026-10-31.csv.bz2</Key><Size>52000000000</Size></Contents>")
    raise OSError("not made up: " + url)


def test_kiwix_listing_and_choices():
    files = S.kiwix_files(fake_get)
    assert len(files) == 5 and files[0]["book"] == "wikipedia_en_all_maxi"
    rows, notes = S.kiwix_rows(files)
    # English, one file per library: the newest maxi (119G, not also the nopic) and madeup (1.5G)
    assert rows[0]["newest"] == 119 * GB + int(1.5 * GB) and notes["english_books"] == 2
    assert rows[0]["all"] == 115 * GB + 119 * GB + int(1.5 * GB)        # every dated copy the mirror keeps
    assert notes["every_language_newest"] == rows[0]["newest"] + 40 * GB
    rows_all, _ = S.kiwix_rows(files, all_languages=True)
    assert rows_all[0]["newest"] == notes["every_language_newest"]


def fake_json(url):
    """Made-up Hugging Face answers."""
    if "made/model-a" in url:
        return {"siblings": [{"rfilename": "a.safetensors", "size": 8 * GB}, {"rfilename": "README.md", "size": 5}]}
    if "AmericanStories" in url:
        return {"siblings": [{"size": 300 * GB}, {"size": 40 * GB}]}
    return None


def test_models_and_writing_corpora():
    rows, unread = S.hf_rows([("made/model-a", "abc"), ("made/missing", "def")], fake_json)
    assert rows[0]["all"] == 8 * GB + 5 and unread == ["made/missing"]
    writing = [{"key": "enron", "size_bytes": 2 * GB}, {"key": "american_stories_newspapers", "size_bytes": 1},
               {"key": "small", "size_bytes": None}]
    w, notes = S.writing_rows(fake_get, fake_json, writing)
    by = {r["item"]: r for r in w}
    assert by["Historical newspapers (American Stories), download"]["all"] == 340 * GB
    assert by["Historical newspapers, the built writing data (estimate)"]["all"] == 190 * GB
    assert by["Court opinions (CourtListener bulk file opinions-2026-10-31.csv.bz2)"]["all"] == 52 * GB
    assert any("enron" in item and r["all"] == 2 * GB for item, r in by.items())
    assert any("Patents" in n for n in notes)


def test_drive_advice():
    tb, n, words = S.recommend(9 * 10 ** 12)                      # 9 TB, with room to grow 13.5 TB -> 14 TB
    assert (tb, n) == (14, 1) and "two 14 TB drives" in words
    tb, n, words = S.recommend(50 * 10 ** 12)                     # 75 TB: three 32 TB drives per copy
    assert (tb, n) == (32, 3) and "6 drives of 32 TB" in words


def test_whole_plan_and_report():
    plan = S.gather(releases_of=made_up_releases, get=fake_get, get_json=fake_json, models=[("made/model-a", "x")],
                    writing=[])
    areas = {a["area"] for a in plan["areas"]}
    assert {"Reference books", "Kiwix libraries", "AI models (originals on Hugging Face)",
            "Writing Kit corpora"} <= areas
    assert plan["total_all"] >= plan["total_newest"] > 0
    text = "\n".join(S.report_lines(plan, "2026-11-22"))
    assert "WHAT TO BUY" in text and "You need about" in text and "Buy two" in text
    assert "in every language" in text                                  # the other Kiwix choice
    assert "Private repositories" in text and "place-packs" in text      # what could not be read is said


# ====================================================================== health_check

def made_up_inventory():
    """A made-up code inventory: three packs, three book keys, three manual categories."""
    return {"packs": {"packs": [{"key": "pack_ok"}, {"key": "pack_small"}, {"key": "pack_missing"},
                                {"key": "pack_building"}, {"key": "pack_new"}]},
            "kit": {"collections": {"pack_ok": {"name": "Made-up pack"}}},
            "books": {"keys": ["b:one", "b:two", "b:three", "b:four"], "groups": {"g": "Made-up group"},
                      "books": [{"key": "b:one", "title": "Book one", "group": "g"},
                                {"key": "b:two", "title": "Book two", "group": "g"}]},
            "manuals": {"categories": [{"key": "m_ok", "name": "Manuals OK"}, {"key": "m_small", "name": "Small"},
                                       {"key": "m_missing", "name": "Missing"}]}}


def made_up_catalogues():
    """Made-up packs.json, textbooks.json and manuals.json."""
    return {"packs": {"pack_ok": {"rows": 500, "size": 9}, "pack_small": {"rows": 4, "size": 1}},
            "textbooks": {"books": [{"key": "b:one", "title": "Book one", "article_count": 40},
                                    {"key": "b:x", "title": "Thin book", "article_count": 1, "file": "thin.zim"}],
                          "pieces_done": ["b:one"], "pieces_failed": {"b:two": 2},
                          "left_out": [{"title": "A", "reason": "It could not be read (HTTP Error 404: Not Found)."},
                                       {"title": "B", "reason": "Its site refuses automated requests (403)."}]},
            "manuals": {"collections": {"m_ok": {"entries": 500}, "m_small": {"entries": 3}}}}


def made_up_jobs():
    """Made-up newest jobs of the build workflows."""
    return {"packs": {"pack_missing": {"state": "failed", "when": "2026-11-22 10:00", "id": 11, "workflow": "p"},
                      "pack_building": {"state": "building", "when": "2026-11-22 11:00", "id": 12, "workflow": "p"}},
            "textbooks": {"b:three": {"state": "queued", "when": "2026-11-22 12:00", "id": 13, "workflow": "t"}},
            "manuals": {}}


def test_health_check_sorts_everything():
    logs = {11: "Reading\nHTTP Error 429: Too Many Requests\nRuntimeError: Commons kept refusing (429)\n"
                "##[error]Process completed with exit code 1."}
    r = H.run_check(made_up_catalogues(), made_up_inventory(), made_up_jobs(), read_log=lambda i: logs.get(i, ""))
    packs = {it["key"]: it for it in r["packs"]}
    assert packs["pack_small"]["status"] == H.NEARLY_EMPTY
    assert packs["pack_missing"]["status"] == H.FAILED and packs["pack_missing"]["cause"].startswith("too many")
    assert "kept refusing" in packs["pack_missing"]["detail"]
    assert packs["pack_building"]["status"] == H.BUILDING and packs["pack_new"]["status"] == H.NOT_YET
    assert "pack_ok" not in packs
    books = {it["key"]: it for it in r["books"]}
    assert books["b:two"]["status"] == H.FAILED and books["b:three"]["status"] == H.BUILDING
    assert books["b:four"]["status"] == H.NOT_YET and books["b:x"]["status"] == H.NEARLY_EMPTY
    assert "b:one" not in books
    manuals = {it["key"]: it for it in r["manuals"]}
    assert manuals["m_small"]["status"] == H.NEARLY_EMPTY and manuals["m_missing"]["status"] == H.NOT_YET
    assert set(r["left_out"]) == {C.cause_of("404 not found"), C.cause_of("refuses automated requests (403)")}
    text = "\n".join(H.report_lines(r, "2026-11-22"))
    assert "SUMMARY" in text and "Cause: too many requests" in text and "STILL BUILDING (1)" in text
    assert "other (1): b:four." in text
    summary = "\n".join(H.summary_lines(r))
    assert "Picture packs: 2 published; the code lists 5 packs. Failed 1, still building 1, nearly empty 1" in summary


def test_health_check_says_what_it_could_not_read():
    r = H.run_check({"packs": None, "textbooks": None, "manuals": None}, made_up_inventory(),
                    {"packs": None, "textbooks": None, "manuals": None}, logs=0)
    assert any("packs catalogue is not published" in n for n in r["notes"])
    assert any("cannot be told apart" in n for n in r["notes"])
    assert all(it["status"] == H.NOT_YET for it in r["packs"])
