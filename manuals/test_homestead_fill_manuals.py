"""Self-test of the homestead skills manual collection (manuals/homestead_fill_manuals.py, category key
homestead_skills, the owner's request of 2026-11-23), with no downloads.

It checks that the category is wired into categories.CATEGORIES under its key, says its safety notice first (boiling
water, a filter's own claims, the Sun through a sextant, hot metal and galvanised fumes), searches the Internet Archive
with its own words (none that another collection already searches, none twice), lists every maker as link-only with
its reason and a https address, and links the reference library's books that hold the guides in full.

Run it from the repository's folder:   python3 -m pytest manuals/test_homestead_fill_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import homestead_fill_manuals as M  # noqa: E402


def test_wired_with_notice_first():
    cat = C.CATEGORIES["homestead_skills"]
    assert cat is M.CATEGORY and cat["kind"] == "manuals" and cat["notice"].startswith("Read the safety section first")
    for words in ("rolling boil for 1 minute", "6,500 feet", "viruses only if its maker says", "Sun shades",
                  "galvanised", "metal fume fever"):
        assert words in cat["notice"], words


def test_own_internet_archive_words():
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "homestead_skills" for w in c.get("ia") or []}
    assert not set(M.IA_WORDS) & taken, set(M.IA_WORDS) & taken
    assert len(M.IA_WORDS) == len(set(M.IA_WORDS)) and all(w == w.lower() for w in M.IA_WORDS)


def test_makers_link_only():
    keys = [m["key"] for m in M.MAKERS]
    assert len(keys) == len(set(keys))
    others = {m.get("key") for k, c in C.CATEGORIES.items() if k != "homestead_skills" for m in c.get("makers") or []}
    assert not set(keys) & others
    for m in M.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "homestead_skills"
    names = " ".join(m["maker"] for m in M.MAKERS)
    for brand in ("Sawyer", "Katadyn", "Davis", "Centaur"):
        assert brand in names, brand


def test_guidance_points_to_the_library():
    text = " ".join(g["title"] + " " + g["url"] for g in M.GUIDANCE)
    for key in ("hfill:index", "skill:army_tb_med_577_field_water_supplies_2010", "outcook:cdc_emergency_water"):
        assert key in text, key
    assert all(g["url"].startswith("https://") and g["by"] for g in M.GUIDANCE)
