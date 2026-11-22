"""Self-test of the manual collections for home upkeep, emergency heating and lighting, and the textile crafts
(manuals/home_crafts_manuals.py), with no downloads.

It checks that the five categories are listed under their keys and are not already other categories, say their
safety notice first, search the Internet Archive with their own words (none of them a word another category already
searches, so a manual is not listed twice), list every maker as link-only with its reason and an https address, and
that their makers' keys are unique.

Run it from the repository's folder:   python3 -m pytest manuals/test_home_crafts_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import home_crafts_manuals as M  # noqa: E402


def test_categories_listed():
    for key, cat in M.CATEGORIES.items():
        assert C.CATEGORIES[key] is cat, key
        assert cat["notice"] and cat["name"] and cat["description"].endswith(".") and cat["kind"] == "manuals"
    assert "carbon monoxide" in M.ENGINE_NOTICE and "helmet" in M.BIKE_NOTICE and "Unplug" in M.CRAFT_NOTICE
    assert set(M.CATEGORIES) == {"bicycles", "small_engines", "textile_craft_tools", "home_heating",
                                 "emergency_lighting"}
    for words in ("carbon monoxide", "3 feet", "911", "qualified professional", "1-K", "never gasoline"):
        assert words in M.HEAT_NOTICE, words
    for words in ("carbon monoxide", "ventilation", "never refuel", "hot or lit", "candle"):
        assert words in M.LIGHT_NOTICE, words
    import re
    assert re.search(M.CATEGORIES["emergency_lighting"]["ia_exclude"], "Magic Candle 3 The (Extras)", re.I)
    assert not re.search(M.CATEGORIES["emergency_lighting"]["ia_exclude"], "Dietz Lantern", re.I)


def test_words_are_new():
    """No Internet Archive word of these categories is searched by another category."""
    others = {w.lower() for k, cat in C.CATEGORIES.items() if k not in M.CATEGORIES for w in cat.get("ia") or []}
    for key, cat in M.CATEGORIES.items():
        words = [w.lower() for w in cat["ia"]]
        assert len(words) == len(set(words)) and not set(words) & others, (key, set(words) & others)


def test_makers_are_link_only():
    keys = []
    for key, cat in M.CATEGORIES.items():
        for m in cat["makers"]:
            assert m["access"] == "link" and m["reason"] == M.RULE and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key and m["maker"] and m["type"]
            keys.append(m["key"])
    assert len(keys) == len(set(keys))
    for cat in M.CATEGORIES.values():
        for g in cat.get("guidance") or []:
            assert g["url"].startswith("https://") and g["title"] and g["by"]
