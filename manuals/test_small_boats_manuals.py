"""Self-test of the small boats manual collection (manuals/small_boats_manuals.py, category key small_boats), with no
downloads.

It checks that the category is wired into categories.CATEGORIES under its key, says its safety notice first with
every note the owner asked for (life jacket, weather, float plan, cold water, never under the influence, carbon
monoxide, epoxy and solvents), searches the Internet Archive with its own words (none that another collection
already searches, none twice: outboards stay with powersports, kayaks and life jackets with outdoors), lists every
maker as link-only with its reason and an https address, and links the reference library's small boat books.

Run it from the repository's folder:   python3 -m pytest manuals/test_small_boats_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import small_boats_manuals as M  # noqa: E402

NOTICE_WORDS = ("life jacket", "weather", "float plan", "Cold water kills", "under the influence",
                "carbon monoxide", "Epoxy", "respirator", "VHF channel 16")


def test_wired_with_notice_first():
    cat = C.CATEGORIES["small_boats"]
    assert cat is M.CATEGORY and cat["kind"] == "manuals" and "CC0" in cat["licence"]
    assert cat["notice"].startswith("Read the safety section first")
    for words in NOTICE_WORDS:
        assert words in cat["notice"], words


def test_own_internet_archive_words():
    cat = C.CATEGORIES["small_boats"]
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "small_boats" for w in c.get("ia") or []}
    mine = [w.lower() for w in cat["ia"]]
    assert mine and len(mine) == len(set(mine))
    assert not set(mine) & taken, set(mine) & taken
    assert "outboard" in taken and "kayak" in taken and "life jacket" in taken   # searched by the other collections


def test_makers_link_only_and_guidance():
    keys = [m["key"] for m in M.MAKERS]
    assert keys and len(keys) == len(set(keys))
    for m in M.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "small_boats" and m["site"] and m["maker"], m["key"]
    names = " ".join(m["maker"] for m in M.MAKERS)
    for brand in ("Boston Whaler", "Mercury", "Yamaha", "Honda", "Volvo Penta", "West System"):
        assert brand in names, brand
    words = " ".join(g["title"] for g in M.GUIDANCE)
    for key in ("boat:noaa_navigation_rules", "outdoors:uscg_boaters_guide_federal_requirements",
                "boat:cfr_recreational_boat_rules", "boat:index"):
        assert key in words, key
    for g in M.GUIDANCE:
        assert g["url"].startswith("https://") and g["by"], g["title"]
