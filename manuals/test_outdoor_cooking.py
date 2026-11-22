"""Self-test of the collection "Grills, smokers, camp stoves and emergency cookers (manuals)" (manuals/
outdoor_cooking.py), with no downloads.

It checks that the category is listed under its key, says the safety notice first (carbon monoxide, 911, soapy water,
USDA temperatures), searches the Internet Archive with its own words (none that another collection already
searches), lists every maker the owner named as link-only (nothing read from their sites) with its reason, and
links the government guidance pages.

Run it from the repository's folder:   python3 -m pytest manuals/test_outdoor_cooking.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import outdoor_cooking as O  # noqa: E402


def test_category():
    cat = C.CATEGORIES["outdoor_cooking"]
    assert cat is O.CATEGORY and cat["kind"] == "manuals"
    for words in ("carbon monoxide", "911", "soapy water", "165 F"):
        assert words in cat["notice"], words
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "outdoor_cooking" for w in c.get("ia") or []}
    assert not set(cat["ia"]) & taken and len(cat["ia"]) == len(set(cat["ia"]))
    urls = " ".join(g["url"] for g in cat["guidance"])
    for host in ("cpsc.gov", "usfa.fema.gov", "cdc.gov", "ready.gov", "fsis.usda.gov"):
        assert host in urls, host


def test_makers_are_link_only():
    names = " ".join(m["maker"] for m in O.MAKERS)
    for brand in ("Coleman", "Weber", "Traeger", "Lodge"):
        assert brand in names, brand
    for m in O.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "outdoor_cooking"
    keys = [m["key"] for m in O.MAKERS]
    assert len(keys) == len(set(keys))
