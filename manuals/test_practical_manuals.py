"""Self-test of the six practical life manual collections (manuals/practical_manuals.py and its files: driver
handbooks, computer basics, cleaning machines, outdoor tools, pools and spas, RVs, trailers and motorcycle gear), with
no downloads.

It checks that each category is listed under its key in categories.py, says its safety notice first with the words
the owner asked for, searches the Internet Archive with its own words (none that another collection already
searches), lists every maker as link-only (nothing read from their sites) with its reason and an https address, and
links its guidance; and that the state and provincial agencies are the same list as the reference library's index
(textbooks/driving.py), read as data without importing it.

Run it from the repository's folder:   python3 -m pytest manuals/test_practical_manuals.py
"""

import ast
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import categories as C  # noqa: E402
import driving_manuals as D  # noqa: E402
import practical_manuals as P  # noqa: E402

NOTICE_WORDS = {
    "driving_handbooks": ("buckles up", "school buses", "white cane"),
    "computer_basics": ("restart it first", "official app store", "password"),
    "household_cleaning": ("Never mix cleaning products", "ammonia"),
    "outdoor_tools": ("eye protection", "rated gear"),
    "pools_spas": ("Never leave children alone", "drain covers", "Never mix different pool chemicals"),
    "motorcycles_rvs": ("tongue weight", "safety chains", "carbon monoxide", "DOT-approved helmet"),
}


def test_categories_registered_with_notices():
    assert set(P.CATEGORIES) == set(NOTICE_WORDS)
    for key, cat in P.CATEGORIES.items():
        assert C.CATEGORIES[key] is cat and cat["kind"] == "manuals", key
        assert cat["name"] and cat["description"] and "CC0" in cat["licence"], key
        for words in NOTICE_WORDS[key]:
            assert words in cat["notice"], (key, words)


def test_internet_archive_words_are_their_own():
    for key, cat in P.CATEGORIES.items():
        taken = {w.lower() for k, c in C.CATEGORIES.items() if k != key for w in c.get("ia") or []}
        mine = [w.lower() for w in cat["ia"]]
        assert mine and len(mine) == len(set(mine)), key
        assert not set(mine) & taken, (key, set(mine) & taken)


def test_makers_link_only_and_guidance():
    for key, cat in P.CATEGORIES.items():
        keys = [m["key"] for m in cat["makers"]]
        assert keys and len(keys) == len(set(keys)), key
        for m in cat["makers"]:
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), (key, m["key"])
            assert m["category"] == key and m["site"] and m["maker"], (key, m["key"])
        for g in cat["guidance"]:
            assert g["title"] and g["url"].startswith("https://") and g["by"], (key, g["title"])
    names = " ".join(m["maker"] for m in P.CATEGORIES["motorcycles_rvs"]["makers"])
    for brand in ("Harley-Davidson", "Honda", "Airstream", "Winnebago", "Dometic"):
        assert brand in names, brand


def test_agencies_match_the_library_index():
    """Every state and DC, and every province and territory, the same as textbooks/driving.py's lists."""
    path = os.path.join(HERE, "..", "textbooks", "driving.py")
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    lists = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
             if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("US_AGENCIES", "CA_AGENCIES")}
    assert lists["US_AGENCIES"] == D.US_AGENCIES and lists["CA_AGENCIES"] == D.CA_AGENCIES
    assert len(D.US_AGENCIES) == 51 and len(D.CA_AGENCIES) == 13
    assert len({s for s, _w, _u in D.US_AGENCIES}) == 51
    assert len(D.MAKERS) == 64
