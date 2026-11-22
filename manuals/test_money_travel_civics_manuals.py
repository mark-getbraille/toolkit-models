"""Self-test of the manual collections of the money, travel and civics request (manuals/money_devices.py,
travel_devices.py and voting_equipment.py), with no downloads.

It checks that each category is listed under its key with its notice first, searches the Internet Archive with its
own words (none that another collection already searches), lists its makers as link-only (nothing read from their
sites) with the reason, gives the government documents in full only when they are US government works and as links
where the site refuses programs, and links its guidance pages.

Run it from the repository's folder:   python3 -m pytest manuals/test_money_travel_civics_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals  # noqa: E402,F401 - the builder's checks import cleanly with the new categories
import categories as C  # noqa: E402
import money_devices  # noqa: E402
import travel_devices  # noqa: E402
import voting_equipment  # noqa: E402

MODULES = {"money_devices": money_devices, "travel_devices": travel_devices, "voting_equipment": voting_equipment}


def test_categories():
    for key, mod in MODULES.items():
        cat = C.CATEGORIES[key]
        assert cat is mod.CATEGORY and cat["kind"] == "manuals" and cat["notice"] and cat["description"]
        taken = {w.lower() for k, c in C.CATEGORIES.items() if k != key for w in c.get("ia") or []}
        assert not set(cat["ia"]) & taken and len(cat["ia"]) == len(set(cat["ia"])), key
        for g in cat["guidance"]:
            assert g["url"].startswith("https://") and g["title"] and g["by"], key


def test_makers_are_link_only():
    keys = []
    for key, mod in MODULES.items():
        for m in mod.MAKERS:
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key
            keys.append((key, m["key"]))
    assert len(keys) == len(set(keys))
    assert "Cassida" in [m["maker"] for m in money_devices.MAKERS]
    taken = {m["maker"] for k, c in C.CATEGORIES.items() if k not in MODULES for m in c.get("makers") or []}
    assert not {m["maker"] for mod in MODULES.values() for m in mod.MAKERS} & taken


def test_documents():
    for key, mod in MODULES.items():
        for d in mod.DOCUMENTS:
            assert d["access"] in ("full", "link") and d["reason"] and d["rights"] and d["url"].startswith("https://")
            if d["access"] == "full":
                assert d["rights"] == "a US government work (public domain)", d["key"]
            if "tsa.gov" in d["url"]:
                assert d["access"] == "link" and "403" in d["reason"], d["key"]
    assert "Help America Vote Act" in voting_equipment.NOTICE and "carry-on" in travel_devices.NOTICE
