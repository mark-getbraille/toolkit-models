"""Self-test of the home food preserving manual collection (manuals/preserving_manuals.py, category key
canning_preserving), with no downloads.

It checks that the category is wired into categories.CATEGORIES under its key, says its safety notice first with every
note the owner asked for (tested recipes, pressure canner for low-acid foods, altitude, gauge testing, botulism and
911), searches the Internet Archive with its own words (none that another collection already searches, none twice:
dehydrators and vacuum sealers stay with kitchen_equipment, pressure cookers with small_kitchen), lists every maker as
link-only with its reason and an https address, indexes the USDA Complete Guide as a public-domain guide, and links
the reference library's preserving books.

Run it from the repository's folder:   python3 -m pytest manuals/test_preserving_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import preserving_manuals as M  # noqa: E402

NOTICE_WORDS = ("tested, current recipes", "pressure canner", "altitude", "dial gauge", "botulism", "call 911",
                "never open a pressure canner")


def test_wired_with_notice_first():
    cat = C.CATEGORIES["canning_preserving"]
    assert cat is M.CATEGORY and cat["kind"] == "manuals" and "CC0" in cat["licence"]
    assert cat["notice"].startswith("Read the safety section first")
    for words in NOTICE_WORDS:
        assert words in cat["notice"], words


def test_own_internet_archive_words():
    cat = C.CATEGORIES["canning_preserving"]
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "canning_preserving" for w in c.get("ia") or []}
    mine = [w.lower() for w in cat["ia"]]
    assert mine and len(mine) == len(set(mine))
    assert not set(mine) & taken, set(mine) & taken
    assert "dehydrator" in taken and "vacuum sealer" in taken and "pressure cooker" in taken


def test_makers_link_only_guides_and_guidance():
    keys = [m["key"] for m in M.MAKERS]
    assert keys and len(keys) == len(set(keys))
    for m in M.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "canning_preserving" and m["site"] and m["maker"], m["key"]
    names = " ".join(m["maker"] for m in M.MAKERS)
    for brand in ("Presto", "All American", "Ball", "Harvest Right", "Excalibur", "FoodSaver"):
        assert brand in names, brand
    assert [g["ia"] for g in M.GUIDES] == ["usda-complete-guide-to-home-canning-2015-revision"]
    assert all(not g.get("military") and g["year"] and g["by"] for g in M.GUIDES)
    words = " ".join(g["title"] for g in M.GUIDANCE)
    for key in ("preserve:index", "preserve:cdc_botulism", "preserve:fsa_food_preservation_uk",
                "cook:nchfp_preserving_links"):
        assert key in words, key
    for g in M.GUIDANCE:
        assert g["url"].startswith("https://") and g["by"], g["title"]
