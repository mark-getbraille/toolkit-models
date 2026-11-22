"""Self-test of the master guide book (library_guide.py, key libguide:my_library, request word library-guide), with
MADE-UP data only: nothing is downloaded.

It checks the wiring (registered once in more_refs.MODULES, its request word gives its one key, the government
web guides' "guide:<name>" keys stay with the builder, its group, licence line and the weekly
check reach the shared files), and that the pages made from made-up code inventories, catalogues and reports have
the parts the owner asked for: one page per area with headings, an index of links, every book group with its books,
sizes and licence classes, books not built yet, every manual heading and category, every topic add-on with its
collections' licence class and picture-making answer, every pack with its size, the Writing Kit's sources, the B:
folders, the size plan and the health check. A whole small book is written to a ZIM file too.

Run it from the repository's folder:   python3 -m pytest textbooks/test_library_guide.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import library_guide as G  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402

GB = 10 ** 9


def made_up_data():
    """Made-up inventories, catalogues, Writing Kit sources and reports."""
    return {
        "date": "2026-11-22",
        "books": {"groups": {"madeup": "Reference, made-up things", "empty": "Reference, nothing yet"},
                  "books": [{"key": "mu:built_one", "title": "Built book", "description": "Already built.",
                             "group": "madeup", "class": "open"},
                            {"key": "mu:waiting", "title": "Waiting book", "description": "Not built yet.",
                             "group": "madeup", "class": "share-alike"},
                            {"key": "mu:later", "title": "Later book", "description": "", "group": "empty",
                             "class": ""}],
                  "not_included": [{"title": "Closed site", "reason": "Refuses programs (403). Link-only."}],
                  "keys": ["mu:built_one", "mu:waiting", "mu:later"]},
        "packs": {"packs": [{"key": "mu_pack", "licence": "CC0", "about": ""},
                            {"key": "mu_unpublished", "licence": "CC BY", "about": "Made-up pictures"}]},
        "kit": {"topics": [{"id": "food", "title": "Made-up food topic", "description": "Food pictures.",
                            "keys": ["mu_pack", "mu_people"], "sensitive": False, "personal_only": False}],
                "collections": {"mu_pack": {"name": "Made-up food pack", "group": "permissive",
                                            "picture_making": True},
                                "mu_people": {"name": "Made-up people", "group": "research",
                                              "picture_making": False},
                                "mu_unpublished": {"name": "Made-up unpublished pack", "group": "share-alike",
                                                   "picture_making": True}}},
        "manuals": {"categories": [{"key": "mu_toasters", "name": "Made-up toasters (manuals)",
                                    "description": "Toasters.", "licence": "CC0 (facts and links)", "heading": ""},
                                   {"key": "mu_lasers", "name": "Made-up lasers (manuals)", "description": "Lasers.",
                                    "licence": "CC0", "heading": "Home manufacturing and making"}]},
        "catalogues": {
            "textbooks": {"books": [{"key": "mu:built_one", "title": "Built book", "group": "madeup",
                                     "description": "Already built.", "size": 2_500_000, "licence_kind": "open"},
                                    {"key": "mu:nc", "title": "Personal book", "group": "madeup",
                                     "description": "For you only.", "size": 1_000_000,
                                     "licence_kind": "non-commercial", "personal_use": True}],
                          "groups": {"madeup": "Reference, made-up things"}, "pieces_done": ["mu:built_one"],
                          "not_included": [{"title": "Closed site", "reason": "duplicate"}]},
            "packs": {"mu_pack": {"rows": 1234, "size": 3 * GB}},
            "manuals": {"collections": {"mu_toasters": {"entries": 57, "manual_count": 12, "manuals_size": 9_000_000,
                                                        "built": "2026-11-20"}}}},
        "writing": [{"key": "mu_letters", "name": "Made-up letters", "class": "open", "style": "letter_personal",
                     "size": "2.5 GB"},
                    {"key": "mu_chat", "name": "Made-up chat", "class": "personal use only", "style": "",
                     "size": ""}],
        "size_plan": {"rows": [{"area": "Reference books", "item": "toolkit-models: textbooks", "files": 3,
                                "all": 9 * GB, "newest": 5 * GB},
                               {"area": "Kiwix libraries", "item": "Kiwix, English: 2 libraries, one file each",
                                "files": 2, "all": 200 * GB, "newest": 120 * GB}],
                      "areas": [{"area": "Reference books", "all": 9 * GB, "newest": 5 * GB, "items": 1},
                                {"area": "Kiwix libraries", "all": 200 * GB, "newest": 120 * GB, "items": 1}],
                      "total_all": 209 * GB, "total_newest": 125 * GB, "growth": 1.5, "drive_tb": 4,
                      "drives_per_copy": 1, "recommendation": "Buy two 4 TB drives: one as your B: drive and one "
                      "as a second copy (a backup), kept apart from the first.", "notes": ["A made-up note."],
                      "kiwix": {}, "date": "2026-11-22"},
        "health": {"packs": [{"key": "mu_unpublished", "title": "Made-up unpublished pack", "status": "failed",
                              "detail": "its last build failed", "cause": "refused by the site (403)", "job": 1}],
                   "books": [], "manuals": [], "left_out": {}, "notes": [], "published": {"packs": 1, "books": 2,
                                                                                          "manuals": 1},
                   "expected": {"packs": 2, "books": 3, "manuals": 2}, "date": "2026-11-22"},
    }


def pages_by_path(data=None):
    """{path: page} of the guide made from the made-up data."""
    return {p.path: p for p in G.build_pages(data or made_up_data())}


# ====================================================================== wiring

def test_wiring():
    assert more_refs.MODULES.count("library_guide") == 1 and G in more_refs.modules()
    assert sources.expand_keys(["library-guide"]) == ["libguide:my_library"]
    assert more_refs.owns("libguide:my_library") and more_refs.module_for("libguide:my_library") is G
    for e in sources.GOV_GUIDES:                       # the government web guides stay with the builder
        assert not more_refs.owns(f"guide:{e['name']}"), e["name"]
    assert sources.GROUPS[G.GROUP] == "Reference, my library guide"
    assert set(G.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert len(G.COLLECTION.expand_keys([G.WORD])) <= 256
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert prefixes.count("libguide") == 1


def test_weekly_check_and_build_go_to_the_guide(monkeypatch, tmp_path):
    monkeypatch.setattr(G, "sign_guide", lambda name: "signed")
    monkeypatch.setitem(G.COLLECTION.makers, "my_library", (G.make_guide, lambda name: "signed"))
    assert updates.fingerprint("libguide:my_library") == "signed"
    called = []
    monkeypatch.setattr(G.COLLECTION, "build", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["libguide:my_library"], str(tmp_path))
    assert called == [["libguide:my_library"]]


# ====================================================================== the pages

def test_one_page_per_area_and_an_index_of_links():
    pages = G.build_pages(made_up_data())
    paths = [p.path for p in pages]
    assert paths[0] == "start"
    for area in ("reference-books", "manuals", "training-kit", "picture-packs", "writing-kit", "program-downloader",
                 "b-drive", "size-plan", "health-check", "books-not-built", "books-madeup", "books-empty"):
        assert area in paths, area
    start = pages[0].body
    for area in ("reference-books", "manuals", "training-kit", "picture-packs", "writing-kit", "program-downloader",
                 "b-drive", "size-plan", "health-check", "books-not-built"):
        assert f'href="{area}"' in start, area
    assert "Reference books published: 2." in start and "Buy two 4 TB drives" in start
    for p in pages:                                     # every page has headings or is the start page's links
        assert "<h2>" in p.body or p.path.startswith("books-"), p.path
        assert len(set(re.findall(r'href="([^"]+)"', p.body)) - set(paths)) == 0, p.path


def test_reference_groups_books_sizes_and_classes():
    pages = pages_by_path()
    ref = pages["reference-books"].body
    assert 'href="books-madeup"' in ref and "Reference, made-up things" in ref and "3 books, 2 built" in ref
    group = pages["books-madeup"].body
    assert "<h2>Open (1)</h2>" in group and "Built book. Already built. 2.5 MB." in group
    assert "<h2>Personal use (1)</h2>" in group and "Personal book. For you only. 1.0 MB." in group
    assert "<h2>Not built yet (1)</h2>" in group and "Waiting book. Not built yet. licence class share-alike." in group
    assert "Later book" in pages["books-empty"].body
    nb = pages["books-not-built"].body
    assert nb.count("Closed site") == 1 and "Refuses programs (403)" in nb      # the code's reason, once


def test_manuals_kit_packs_and_writing():
    pages = pages_by_path()
    m = pages["manuals"].body
    assert "<h2>The main list (1)</h2>" in m and "<h2>Home manufacturing and making (1)</h2>" in m
    assert "<h3>Made-up toasters (manuals)</h3>" in m and "57 entries, 12 manuals, 9.0 MB" in m
    assert "Made-up lasers (manuals)" in m and "not built yet" in m
    k = pages["training-kit"].body
    assert "<h2>Made-up food topic</h2>" in k
    assert "Made-up food pack. Licence class open. Picture-making allowed." in k
    assert "Made-up people. Licence class personal use. Picture-making not allowed." in k
    p = pages["picture-packs"].body
    assert "<h2>Made-up food topic (1)</h2>" in p and "1,234 pictures, 3.0 GB" in p
    assert "<h2>Packs not in a topic add-on (1)</h2>" in p and "not published yet" in p
    w = pages["writing-kit"].body
    assert "<h2>Open (1)</h2>" in w and "Made-up letters (mu_letters). Style: letter_personal. Size: 2.5 GB." in w
    assert "<h2>Personal use only (1)</h2>" in w and "Style: several." in w


def test_folders_drive_size_and_health():
    pages = pages_by_path()
    f = pages["program-downloader"].body
    for name in ("Data packs", "Original sources", "Software", "Kiwix", "AI models", "Radio"):
        assert f"<h2>{name}</h2>" in f
    d = pages["b-drive"].body
    assert "B:\\Data packs\\toolkit-models\\textbooks\\: 3 files, 9.0 GB." in d
    s = pages["size-plan"].body
    assert "You need about 209 GB" in s and "<h2>What to buy</h2>" in s and "A made-up note." in s
    h = pages["health-check"].body
    assert "<h2>Summary</h2>" in h and "Cause: refused by the site (403)" in h and "Made-up unpublished pack" in h


def test_a_part_that_cannot_be_read_is_said():
    data = made_up_data()
    data["kit"] = {"error": "made-up failure"}
    data["writing"] = {"error": "no branch"}
    data["size_plan"] = {"error": "no network"}
    pages = pages_by_path(data)
    assert "could not be read when the guide was built: made-up failure" in pages["training-kit"].body
    assert "no branch" in pages["writing-kit"].body and "no network" in pages["size-plan"].body
    assert "Made-up food pack" not in pages["picture-packs"].body               # names come from the kit
    assert "mu_pack" in pages["picture-packs"].body


def test_book_and_zim_file(monkeypatch, tmp_path):
    book = G.make_guide("my_library", str(tmp_path), None, [], data=made_up_data())
    assert book.name == "libguide_my_library" and book.group == G.GROUP and book.licence == "CC0 1.0"
    assert book.pages[0].path == "start" and book.published == "2026-11-22"
    assert len(G.make_guide("my_library", str(tmp_path), None, [], limit=2, data=made_up_data()).pages) == 2
    monkeypatch.setattr(G, "collect", made_up_data)
    monkeypatch.setitem(G.COLLECTION.makers, "my_library", (G.make_guide, lambda name: "sig"))
    monkeypatch.setattr(B, "robots_for_originals", lambda url: True)
    manifests = G.COLLECTION.build(["library-guide"], str(tmp_path / "out"), cache=str(tmp_path / "cache"))
    entry = manifests["libguide:my_library"]["books"][0]
    assert entry["key"] == "libguide:my_library" and entry["file"].endswith(".zim") and entry["licence_kind"] == "open"
    assert os.path.exists(tmp_path / "out" / entry["file"])
    assert entry["article_count"] >= 12


def test_reports_made_here_are_read_first(monkeypatch, tmp_path):
    import json
    (tmp_path / "size-plan.json").write_text(json.dumps({"total_all": 7}), encoding="utf-8")
    monkeypatch.setenv(G.REPORTS_ENV, str(tmp_path))
    assert G.local_report("size-plan.json") == {"total_all": 7}
    assert G.local_report("health-check.json") is None
    monkeypatch.delenv(G.REPORTS_ENV)
    assert G.local_report("size-plan.json") is None


def test_lines_html_headings_and_lists():
    html = G.lines_html(["SUMMARY", "  Packs: 3 published.", "", "PICTURE PACKS", "  FAILED (1)",
                         "    Cause: refused (1)", "      Pack x: failed.", "A plain line."])
    assert "<h2>Summary</h2>" in html and "<h2>Picture packs</h2>" in html and "<h3>Failed (1)</h3>" in html
    assert "<h3>Cause: refused (1)</h3>" in html and "<li>Pack x: failed.</li>" in html
    assert "<p>A plain line.</p>" in html
