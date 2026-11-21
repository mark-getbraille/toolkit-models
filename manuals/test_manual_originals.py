"""Self-tests of the "originals" field of the manual collection indexes (build_manuals.entry_originals and write),
with made-up entries only: nothing is downloaded (robots.txt answers are given by the test).

It checks that a maker's manual (it belongs to its maker) is never downloadable, that a US government manual and its
text file are downloadable only when robots.txt allows them, that the product page and an openly licensed
thumbnail's source are listed, that each address is listed once, and that write() gives every entry the field and
counts the originals in the manifest.

Run it from the repository's folder:   python3 -m pytest manuals/test_manual_originals.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as M  # noqa: E402

FIELDS = {"url", "kind", "size", "sha256", "licence", "may_download", "why"}

MAKER = {"id": "fa-maker-1", "brand": "Made-up Arms", "name": "Model 1 manual", "page": "https://maker.example.com/lib",
         "manuals": [{"title": "Model 1", "url": "https://maker.example.com/m1.pdf",
                      "page": "https://maker.example.com/lib", "kind": "pdf", "size": 500,
                      "rights": "belongs to its maker (Made-up Arms); fetched from the maker for the owner's own use"}]}
PUBLIC = {"id": "guide-x-tm1", "brand": "US Army", "name": "Made-up field guide",
          "page": "https://archive.org/details/tm1",
          "manuals": [{"title": "Made-up field guide", "url": "https://archive.org/download/tm1/tm1.pdf",
                       "page": "https://archive.org/details/tm1", "kind": "pdf", "size": 2000,
                       "text_url": "https://archive.org/download/tm1/tm1_djvu.txt",
                       "rights": "a US government work (public domain)"}]}
FOOD = {"id": "off-1", "name": "Soup", "page": "https://world.openfoodfacts.org/product/1",
        "licence": "ODbL (facts); CC BY-SA (texts and photos)", "manuals": [],
        "thumb": {"data": "", "licence": "CC BY-SA 4.0", "source": "https://upload.wikimedia.org/x/Soup.jpg"}}


def test_maker_manuals_are_links_only():
    got = M.entry_originals(MAKER, lambda url: True)
    assert [o["url"] for o in got] == ["https://maker.example.com/m1.pdf", "https://maker.example.com/lib"]
    assert all(set(o) == FIELDS for o in got)
    assert got[0]["kind"] == "pdf" and got[0]["size"] == 500 and got[1]["kind"] == "html"
    assert not any(o["may_download"] for o in got) and "do not allow copying" in got[0]["why"]


def test_public_domain_manuals_follow_robots():
    got = M.entry_originals(PUBLIC, lambda url: "details" not in url)
    by_url = {o["url"]: o for o in got}
    assert by_url["https://archive.org/download/tm1/tm1.pdf"]["may_download"]
    assert by_url["https://archive.org/download/tm1/tm1_djvu.txt"]["kind"] == "txt"
    assert by_url["https://archive.org/download/tm1/tm1_djvu.txt"]["may_download"]
    assert not by_url["https://archive.org/details/tm1"]["may_download"]
    assert "robots.txt of archive.org does not allow" in by_url["https://archive.org/details/tm1"]["why"]
    assert len(got) == 3                                   # the page is listed once
    assert not any(o["may_download"] for o in M.entry_originals(PUBLIC))       # robots.txt not checked


def test_open_data_pages_and_thumbnails():
    got = M.entry_originals(FOOD, lambda url: True)
    assert [o["kind"] for o in got] == ["html", "jpg"] and all(o["may_download"] for o in got)
    nc = M.download_permission("https://a.org/x.pdf", "CC BY-NC 4.0", lambda url: True)
    assert nc[0] and "personal use only" in nc[1]
    assert M.robots_for_originals(None)("https://a.org/x") is None


def test_write_adds_originals(tmp_path, monkeypatch):
    key = next(iter(M.C.CATEGORIES))
    manifest = M.write(key, [dict(MAKER), dict(PUBLIC)], str(tmp_path), robots=lambda url: True)
    index = json.loads(gzip.decompress(open(os.path.join(tmp_path, manifest["file"]), "rb").read()))
    assert all("originals" in e for e in index["entries"])
    assert manifest["original_count"] == 5 and manifest["downloadable_count"] == 3
