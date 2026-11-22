"""Self-test of the collection "Hair styling tools, shavers, trimmers and personal care appliances (manuals)"
(manuals/personal_care_manuals.py), with no downloads.

It checks that the category is listed under its key, says the safety notice first (water, hot tools, Poison Help),
searches the Internet Archive with its own words (none that another collection already searches), lists every maker
as link-only (nothing read from their sites) with its reason, and links the FDA's and CPSC's guidance.

Run it from the repository's folder:   python3 -m pytest manuals/test_personal_care_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import personal_care_manuals as M  # noqa: E402


def test_category():
    cat = C.CATEGORIES["personal_care_appliances"]
    assert cat is M.CATEGORY and cat["kind"] == "manuals"
    for words in ("sink, bath or shower", "unplug", "1-800-222-1222"):
        assert words in cat["notice"], words
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "personal_care_appliances" for w in c.get("ia") or []}
    assert not set(cat["ia"]) & taken and len(cat["ia"]) == len(set(cat["ia"]))
    urls = " ".join(g["url"] for g in cat["guidance"])
    for host in ("fda.gov", "cpsc.gov", "poisonhelp.hrsa.gov"):
        assert host in urls, host


def test_makers_are_link_only():
    names = " ".join(m["maker"] for m in M.MAKERS)
    for brand in ("Conair", "Remington", "Philips", "Braun", "Wahl"):
        assert brand in names, brand
    for m in M.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "personal_care_appliances"
    keys = [m["key"] for m in M.MAKERS]
    assert len(keys) == len(set(keys))
