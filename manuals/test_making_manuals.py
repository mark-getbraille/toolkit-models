"""Self-test of the home manufacturing and making manual collections (manuals/making_manuals.py and their lines in
categories.py and build_manuals.write), with MADE-UP data only: nothing is downloaded.

It checks that each category is listed under its key with a plain name, a kind, a licence and a notice said first
(hot nozzles and resin for printers; heat press and blades; laser eyes, Class 4, fire and never PVC or vinyl for
lasers; spinning chucks and no gloves for lathes and mills; molten metal and water for casting); that its Internet
Archive words are ones no other collection searches; that every maker is link-only with its reason, an https address,
no manual-copying site, no id used twice, and no maker another collection already links (Cricut, Silhouette,
Glowforge, Carbide 3D, Grizzly, Tormach stay where they are); that the heading "Home manufacturing and making" is on
these categories only (the craft, woodshop and metal shop collections keep their keys and no heading) and is written
into the index and the manifest.

Run it from the repository's folder:   python3 -m pytest manuals/test_making_manuals.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import making_manuals as M  # noqa: E402

KEYS = ("printers_3d", "heat_press_vinyl", "laser_cnc_making", "small_machining", "moulding_casting")


def test_categories_listed():
    assert set(M.CATEGORIES) == set(KEYS)
    for key in KEYS:
        cat = C.CATEGORIES[key]
        assert cat is M.CATEGORIES[key] and cat["kind"] == "manuals" and cat["name"] and cat["licence"], key
        assert cat["notice"].startswith("Read the safety section first."), key
        assert cat["ia"] and len(cat["ia"]) == len(set(cat["ia"])), key
        for guide in cat.get("guidance", []):
            assert guide["url"].startswith("https://") and guide["title"] and guide["by"], key
    for words in ("hot enough to burn", "smoke alarm", "nitrile gloves", "resin"):
        assert words in M.PRINTER_NOTICE, words
    for words in ("Never look into a laser beam", "rated for the laser's wavelength", "Class 4", "fire extinguisher",
                  "PVC or vinyl", "chlorine gas", "emergency stop"):
        assert words in M.LASER_CNC_NOTICE, words
    for words in ("no gloves, loose sleeves, jewellery", "chuck key", "guards"):
        assert words in M.MACHINING_NOTICE, words
    assert "water" in M.CASTING_NOTICE and "safety data sheet" in M.CASTING_NOTICE
    assert "heat press" in M.VINYL_NOTICE and "blades" in M.VINYL_NOTICE


def test_words_are_new():
    theirs = {w.lower() for k, c in C.CATEGORIES.items() if k not in KEYS for w in c.get("ia") or []}
    mine = [w for key in KEYS for w in C.CATEGORIES[key]["ia"]]
    assert len(mine) == len(set(mine))
    assert not set(mine) & theirs, set(mine) & theirs


def test_makers_are_link_only_and_not_repeated():
    seen = set()
    for key in KEYS:
        for m in C.CATEGORIES[key].get("makers", []):
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key and m["types"] == []
            assert (m["prefix"], m["key"]) not in seen, m["key"]
            seen.add((m["prefix"], m["key"]))
            for site in B.NEVER_SITES:
                assert site not in str(m), m["key"]
    mine = {m["key"] for key in KEYS for m in C.CATEGORIES[key]["makers"]}
    elsewhere = {m["key"] for k, c in C.CATEGORIES.items() if k not in KEYS for m in c.get("makers") or []}
    assert not mine & elsewhere, mine & elsewhere
    names = " ".join(m["maker"] for key in KEYS for m in C.CATEGORIES[key]["makers"])
    for brand in ("Prusa", "Bambu Lab", "Creality", "Elegoo", "Anycubic", "xTool", "LightBurn", "Sherline", "Taig",
                  "Smooth-On"):
        assert brand in names, brand
    # the makers other collections link stay there
    assert {"cricut", "silhouette"} <= {m["key"] for m in C.CATEGORIES["craft_machines"]["makers"]}
    assert {"glowforge", "carbide3d"} <= {m["key"] for m in C.CATEGORIES["woodshop_machines"]["makers"]}


def test_heading():
    for key in KEYS:
        assert C.CATEGORIES[key]["heading"] == "Home manufacturing and making", key
    for key in ("craft_machines", "woodshop_machines", "metal_shop_welding", "sewing_textile"):
        assert C.CATEGORIES[key].get("heading") != "Home manufacturing and making", key


class FakeFetch:
    """No network: the link-only makers need none."""

    def json(self, url, headers=None, cache=True):
        raise AssertionError("nothing is read from a link-only maker")

    def text(self, url, headers=None, cache=True):
        raise AssertionError("nothing is read from a link-only maker")


def test_the_index_has_its_heading_and_notice(tmp_path):
    entries, _ = B.maker_entries(FakeFetch(), C.CATEGORIES["laser_cnc_making"]["makers"])
    manifest = B.write("laser_cnc_making", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["heading"] == manifest["heading"] == "Home manufacturing and making"
    assert index["notice"] == M.LASER_CNC_NOTICE
    assert {m["key"] for m in index["makers"]} >= {"xtool", "lightburn", "inventables"}
