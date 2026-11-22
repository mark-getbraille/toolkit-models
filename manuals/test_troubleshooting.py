"""Self-test of the appliance troubleshooting and release-notes collections (manuals/troubleshooting.py, and
build_manuals.ia_any_entries, document_version, document_entries and the "link only" rule of entry_originals), with
MADE-UP answers only: nothing is downloaded from the internet.

It checks that:
  - both categories are listed, with their plain names, a licence and their sources;
  - every appliance maker is "link" with a reason and an address, and no manual-copying site is named anywhere;
  - every hand-entered page has an access decision ("full" or "link"), rights and a reason; the "full" ones are
    openly licensed (NVDA GPL, Orca and BRLTTY LGPL, Android CC BY, OpenWrt CC BY-SA, US government) and JAWS,
    Microsoft, Apple and iFixit are link only;
  - a link-only page is never marked for downloading, even where robots.txt allows; an openly licensed page is,
    when robots.txt allows; iFixit is never downloaded by a program;
  - the versions of NVDA (from its own page) and Orca (from GNOME's list) are read, and a failure is a note;
  - the Internet Archive search is one request for all the word groups, and each item gets its appliance kind;
  - the written index carries the notice and the documents' access decisions.

Run it from the repository's folder:   python3 -m pytest manuals/test_troubleshooting.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import troubleshooting as T  # noqa: E402


class FakeFetch:
    """Answers from dictionaries of made-up pages and JSON; records every address asked."""

    def __init__(self, pages=None, data=None):
        self.pages, self.data, self.asked, self.requests = pages or {}, data or {}, [], 0

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        if url not in self.pages:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.pages[url]

    def json(self, url, headers=None, cache=True):
        self.asked.append(url)
        for prefix, answer in self.data.items():
            if url.startswith(prefix):
                return answer
        raise RuntimeError(f"{url}: HTTP 404")


def test_categories_listed():
    """Both collections are in categories.CATEGORIES with a name, a licence and their sources."""
    for key in ("appliance_troubleshooting", "release_notes"):
        cat = C.CATEGORIES[key]
        assert cat["kind"] == "manuals" and cat["name"] and cat["licence"].startswith("CC0")
        assert cat["documents"]
    cat = C.CATEGORIES["appliance_troubleshooting"]
    assert cat["makers"] and cat["ia_any"] and cat["notice"]
    for word in ("washer", "dryer", "dishwasher", "oven", "refrigerator", "furnace", "heat pump", "water heater"):
        assert word in cat["ia_any"]["kinds"]
    for word in ("service", "error codes", "tech sheet", "troubleshooting"):
        assert word in cat["ia_any"]["documents"]


def test_makers_link_only():
    """Every appliance maker is link only, with a reason and an https address in its own category."""
    keys = set()
    for m in T.APPLIANCE_MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://")
        assert m["category"] == "appliance_troubleshooting" and m["key"] not in keys
        keys.add(m["key"])
    assert {"whirlpool", "ge", "lg", "samsung", "carrier", "rheem", "ao-smith"} <= keys


def test_no_copy_sites():
    """No manual-copying site's address is used in either collection."""
    urls = [m["library"] for m in T.APPLIANCE_MAKERS] + [d["url"] for d in T.APPLIANCE_DOCUMENTS + T.RELEASE_NOTES]
    for url in urls:
        assert not any(site in url for site in B.NEVER_SITES), url


def test_documents_decisions():
    """Every page has its decision; the full ones are openly licensed; the copyrighted ones are links."""
    docs = {d["key"]: d for d in T.APPLIANCE_DOCUMENTS + T.RELEASE_NOTES}
    assert len(docs) == len(T.APPLIANCE_DOCUMENTS) + len(T.RELEASE_NOTES)       # no key twice
    for d in docs.values():
        assert d["access"] in ("full", "link") and d["rights"] and d["reason"] and d["url"].startswith("https://")
        if d["access"] == "full":
            assert B.OPEN_RIGHTS.search(d["rights"]), d["key"]
    for key in ("nvda", "orca", "brltty", "android-security", "pixel-security", "openwrt"):
        assert docs[key]["access"] == "full"
    for key in ("jaws", "narrator", "voiceover", "windows", "macos", "ios", "netgear", "echo", "google-nest"):
        assert docs[key]["access"] == "link" and not B.OPEN_RIGHTS.search(docs[key]["rights"])
    assert all(d["access"] == "link" for k, d in docs.items() if k.startswith("ifixit-"))
    assert "BY-NC-SA" in docs["ifixit-washing_machine"]["rights"]


def test_link_only_never_downloaded():
    """A link-only page is never marked for downloading, even when its rights look open and robots.txt allows it;
    iFixit never; an openly licensed page when robots.txt allows it, and not when it does not."""
    entries, _ = B.document_entries(None, T.APPLIANCE_DOCUMENTS + T.RELEASE_NOTES, "x")
    by_id = {e["id"]: e for e in entries}

    def may(entry, allowed=True):
        return [o["may_download"] for o in B.entry_originals(entry, robots=lambda url: allowed)]

    assert may(by_id["doc-x-jaws"]) == [False]
    assert may(by_id["doc-x-ifixit-dryer"]) == [False]          # CC BY-NC-SA, but link only and no programs
    assert may(by_id["doc-x-nvda"]) == [True]
    assert may(by_id["doc-x-nvda"], allowed=False) == [False]
    assert may(by_id["doc-x-openwrt"]) == [True] and may(by_id["doc-x-energystar-maintenance"]) == [True]
    ok, why = B.download_permission("https://www.ifixit.com/Device/Dryer", T.IFIXIT_RIGHTS, lambda url: True)
    assert not ok and "API" in why
    assert by_id["doc-x-jaws"]["access_reason"] and by_id["doc-x-jaws"]["access"] == "link"


def test_versions_read():
    """NVDA's version comes from the first release heading of its page; Orca's from GNOME's list (the newest
    stable release, not a beta), with the address of that release's NEWS file. A failure is a note."""
    nvda = next(d for d in T.RELEASE_NOTES if d["key"] == "nvda")
    orca = next(d for d in T.RELEASE_NOTES if d["key"] == "orca")
    fetch = FakeFetch(pages={nvda["url"]: '<h1>What\'s New</h1><h2 id="202631">2026.3.1</h2><h2>2026.3</h2>'},
                      data={"https://download.gnome.org/sources/orca/cache.json": [4, {"orca": {
                          "50.2": {"news": "50/orca-50.2.news"}, "51.2": {"news": "51/orca-51.2.news"},
                          "51.10": {"news": "51/orca-51.10.news"}, "52.beta": {"news": "52/orca-52.beta.news"}}}]})
    entries, notes = B.document_entries(fetch, [nvda, orca], "release_notes")
    assert not notes
    assert entries[0]["version"] == "2026.3.1" and entries[0]["manuals"][0]["title"].endswith("(version 2026.3.1)")
    assert entries[1]["version"] == "51.10"
    assert entries[1]["page"] == "https://download.gnome.org/sources/orca/51/orca-51.10.news"
    assert entries[1]["manuals"][0]["kind"] == "txt"
    entries, notes = B.document_entries(FakeFetch(), [nvda], "release_notes")
    assert "version" not in entries[0] and entries[0]["page"] == nvda["url"] and "version not read" in notes[0]


def test_ia_any_one_search():
    """The Internet Archive is asked once (a kind AND a kind of paper); each item gets its kind; copy-site items and the
    category's exclusions are left out by the build."""
    cat = C.CATEGORIES["appliance_troubleshooting"]
    docs = [{"identifier": "Maytag_Top_Load_Washers_Service_Manual", "title": "Maytag Top Load Washers Service Manual"},
            {"identifier": "carrier-furnace-tech-sheet", "title": "Carrier Gas Furnace Tech Sheet"},
            {"identifier": "manualzz-id-1", "title": "Whirlpool Dryer Service Manual"}]
    fetch = FakeFetch(data={"https://archive.org/advancedsearch.php": {"response": {"docs": docs}}})
    notes = []
    got = B.ia_any_entries(fetch, "appliance_troubleshooting", cat, 50, notes)
    asked = B.urllib.parse.unquote_plus(fetch.asked[0])
    assert len(fetch.asked) == 1 and len(fetch.asked[0]) < 4000
    assert '"washer" OR' in asked and '"heat pump"' in asked and '"tech sheet"' in asked and ") AND (" in asked
    assert [e["kind"] for e in got] == ["washer", "furnace"]
    import re
    assert re.search(cat["ia_exclude"], "Sun Joe Pressure Washer Service Manual", re.I)
    assert re.search(cat["ia_exclude"], "Conair Hair Dryer Troubleshooting", re.I)
    assert not re.search(cat["ia_exclude"], "GE Electric Range Service Manual", re.I)
    assert re.search(cat["ia_exclude"], "Biotek ELx50 Automated Strip Washer", re.I)
    assert re.search(cat["ia_exclude"], "Kendro Ultra Low Temperature Upright Freezer", re.I)
    assert not re.search(cat["ia_exclude"], "Maytag Neptune Washer 16010061", re.I)


def test_index_written(tmp_path):
    """The index carries the safety notice, the makers' and the documents' access decisions, and every entry its
    originals."""
    entries, _ = B.document_entries(None, T.RELEASE_NOTES, "release_notes")
    B.write("release_notes", entries, str(tmp_path), robots=lambda url: True)
    name = next(n for n in os.listdir(tmp_path) if n.endswith(".json.gz"))
    index = json.loads(gzip.decompress((tmp_path / name).read_bytes()))
    assert {d["key"]: d["access"] for d in index["documents"]}["jaws"] == "link"
    assert all(e["originals"] for e in index["entries"])
    entries, _ = B.maker_entries(None, T.APPLIANCE_MAKERS)
    B.write("appliance_troubleshooting", entries, str(tmp_path), robots=lambda url: True)
    name = next(n for n in os.listdir(tmp_path) if n.startswith("manuals-appliance"))
    index = json.loads(gzip.decompress((tmp_path / name).read_bytes()))
    assert index["notice"].startswith("Unplug") and len(index["makers"]) == len(T.APPLIANCE_MAKERS)
    assert not any(o["may_download"] for e in index["entries"] for o in e["originals"])
