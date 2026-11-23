"""Self-test of the craft trades' manual collection (manuals/craft_trades_manuals.py), with no downloads.

It checks that the collection is listed under its key, under the "Arts and crafts" heading, and is not already
another collection; that it says its safety notice first; that it searches the Internet Archive with its own words
(none of them a word another collection already searches, so a manual is not listed twice); that every maker is
link-only with its reason and an https address; that the makers' keys are unique; and that its index and manifest
carry the heading.

Run it from the repository's folder:   python3 -m pytest manuals/test_craft_trades_manuals.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import craft_trades_manuals as M  # noqa: E402


def test_listed_under_arts_and_crafts():
    assert set(M.CATEGORIES) == {"craft_trades_tools"}
    cat = C.CATEGORIES["craft_trades_tools"]
    assert cat["heading"] == "Arts and crafts" and cat["kind"] == "manuals"
    assert cat["notice"] == M.NOTICE and cat["name"] and cat["description"].endswith(".")
    for words in ("safety section first", "soapy water", "eye protection", "unplug"):
        assert words in M.NOTICE, words


def test_words_are_new():
    """No Internet Archive word of this collection is searched by another collection."""
    others = {w.lower() for k, cat in C.CATEGORIES.items() if k not in M.CATEGORIES for w in cat.get("ia") or []}
    words = [w.lower() for w in M.CRAFT_TRADES_WORDS]
    assert len(words) == len(set(words)) and not set(words) & others, set(words) & others
    assert "beekeeping" not in words and "kiln" not in words      # homestead's and pottery_kilns' own


def test_makers_are_link_only():
    keys = [m["key"] for m in M.MAKERS]
    assert len(keys) == len(set(keys)) == 7
    all_keys = [m["key"] for k, cat in C.CATEGORIES.items() if k != "craft_trades_tools"
                for m in cat.get("makers") or []]
    assert not set(keys) & set(all_keys)
    for m in M.MAKERS:
        assert m["access"] == "link" and m["reason"] == M.RULE and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "craft_trades_tools" and m["maker"] and m["type"]


def test_heading_in_index_and_manifest(tmp_path):
    manifest = B.write("craft_trades_tools", [], str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["heading"] == manifest["heading"] == "Arts and crafts"
