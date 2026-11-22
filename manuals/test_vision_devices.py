"""Self-test of the collection "Blind and low-vision living: braille writers, braille displays, magnifiers and talking
devices (manuals)" (manuals/vision_devices.py), with no downloads.

It checks that the category is listed under its key with its own heading, says the care notice first (do not force a
braille writer, the free NLS repair number, VA and state programmes), searches the Internet Archive with its own words
(none that another collection already searches), lists every maker as link-only with its reason and none that
assistive_tech_repair already lists, gives the Perkins maintenance guide as link-only, and links the programmes.

Run it from the repository's folder:   python3 -m pytest manuals/test_vision_devices.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import vision_devices as V  # noqa: E402


def test_category():
    cat = C.CATEGORIES["vision_devices"]
    assert cat is V.CATEGORY and cat["kind"] == "manuals"
    assert cat["name"].startswith("Blind and low-vision living")
    for words in ("do not force it", "1-888-657-7323", "VIST", "Assistive Technology Act"):
        assert words in cat["notice"], words
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "vision_devices" for w in c.get("ia") or []}
    assert not set(cat["ia"]) & taken and len(cat["ia"]) == len(set(cat["ia"]))
    urls = " ".join(g["url"] for g in cat["guidance"])
    for host in ("access-board.gov", "acl.gov", "va.gov", "loc.gov/nls"):
        assert host in urls, host


def test_makers_are_link_only():
    names = " ".join(m["maker"] for m in V.MAKERS)
    for brand in ("Perkins", "Freedom Scientific", "JAWS", "ZoomText", "Mountbatten", "ScripTalk"):
        assert brand in names, brand
    for m in V.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "vision_devices"
    keys = [m["key"] for m in V.MAKERS]
    assert len(keys) == len(set(keys))
    others = {m["library"] for m in C.CATEGORIES["assistive_tech_repair"]["makers"]}
    assert not others & {m["library"] for m in V.MAKERS}


def test_documents():
    perkins = [d for d in V.DOCUMENTS if d["product"] == "Perkins Brailler"]
    assert perkins and all(d["access"] == "link" and "no licence" in d["rights"] for d in perkins)
    for d in V.DOCUMENTS:
        assert d["access"] in ("link", "full") and d["reason"] and d["url"].startswith("https://"), d["key"]
        if d["access"] == "full":
            assert d["rights"] == V.US_GOV, d["key"]
