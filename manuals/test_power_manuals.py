"""Self-test of the power and electrical manual collections (manuals/power_manuals.py and their lines in
categories.py and build_manuals.write), with MADE-UP Internet Archive answers only: nothing is downloaded.

It checks that each category is listed under its key with a plain name, a kind, a licence, a notice said first (the
carbon monoxide, 20 feet, 911, back-feeding, transfer switch and licensed electrician words for generators; DC arcs,
roofs and batteries for solar; blades, towers and lightning for wind and water; shock first aid for the home), and
Internet Archive words no other collection searches; that every maker is link-only with its reason, an https address,
no manual-copying site and no id used twice, with the makers the owner named; that the Army generator manuals follow
the release rule (made-up items); that the heading "Power and electrical" is on these categories and the existing
electrical ones (keys unchanged) and is written into the index and the manifest.

Run it from the repository's folder:   python3 -m pytest manuals/test_power_manuals.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import power_manuals as P  # noqa: E402

KEYS = ("backup_generators", "solar_battery_power", "wind_hydro_power", "home_electrical")


def test_categories_listed():
    for key in KEYS:
        cat = C.CATEGORIES[key]
        assert cat is P.CATEGORIES[key] and cat["kind"] == "manuals" and cat["name"] and cat["licence"], key
        assert cat["notice"].startswith("Read the safety section first."), key
        assert cat["ia"] and len(cat["ia"]) == len(set(cat["ia"])), key
        for guide in cat.get("guidance", []):
            assert guide["url"].startswith("https://") and guide["title"] and guide["by"], key
    for words in ("only outdoors", "20 feet", "carbon monoxide", "911", "dryer outlet", "transfer switch",
                  "licensed electrician", "rotating parts"):
        assert words in P.GENERATOR_NOTICE, words
    for words in ("arc", "fall protection", "thermal runaway", "licensed electrician"):
        assert words in P.SOLAR_NOTICE, words
    for words in ("brake", "fall protection", "lightning", "water rights"):
        assert words in P.WIND_HYDRO_NOTICE, words
    assert "911" in P.HOME_ELECTRICAL_NOTICE and "tester" in P.HOME_ELECTRICAL_NOTICE


def test_words_are_new():
    theirs = {w.lower() for k, c in C.CATEGORIES.items() if k not in KEYS for w in c.get("ia") or []}
    mine = [w for key in KEYS for w in C.CATEGORIES[key]["ia"]]
    assert len(mine) == len(set(mine))
    assert not set(mine) & theirs, set(mine) & theirs


def test_makers_are_link_only():
    seen = set()
    for key in KEYS:
        for m in C.CATEGORIES[key].get("makers", []):
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key and m["types"] == []
            assert (m["prefix"], m["key"]) not in seen, m["key"]
            seen.add((m["prefix"], m["key"]))
            for site in B.NEVER_SITES:
                assert site not in str(m), m["key"]
    names = " ".join(m["maker"] for key in KEYS for m in C.CATEGORIES[key]["makers"])
    names += " ".join(m["maker"] for m in C.CATEGORIES["emergency_power"]["makers"])
    for brand in ("Renogy", "Victron", "EcoFlow", "Jackery", "Enphase", "SolarEdge",
                  "Tesla", "Battle Born", "Generac", "Honda", "Champion", "Westinghouse", "Kohler",
                  "Briggs & Stratton", "Pro Power Onboard", "F-150 Lightning", "GM Energy", "Hugh Piggott"):
        assert brand in names, brand


class FakeFetch:
    """Made-up Internet Archive metadata and text files."""

    def __init__(self, files, text):
        self.files, self.text_body, self.asked = files, text, []

    def json(self, url, headers=None, cache=True):
        self.asked.append(url)
        return {"files": self.files, "metadata": {}}

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        return self.text_body

    def size(self, url):
        return 1000


def test_army_generator_manuals_follow_the_release_rule():
    guides = C.CATEGORIES["backup_generators"]["public_guides"]
    assert len(guides) == 4 and all(g["military"] and g["by"] == "the US Army" for g in guides)
    assert not C.CATEGORIES["home_electrical"]["public_guides"][0]["military"]
    files = [{"name": "x.pdf", "format": "Text PDF", "size": "100"}, {"name": "x_djvu.txt", "format": "DjVuTXT"}]
    ok = FakeFetch(files, "TM 9-6115-641-10 ... DISTRIBUTION STATEMENT A. Approved for public release; distribution "
                          "is unlimited.")
    got, notes = B.public_guide_entries(ok, guides[:1], "backup_generators")
    assert len(got) == 1 and got[0]["manuals"][0]["release"].startswith("Distribution Statement A") and not notes
    restricted = FakeFetch(files, "TM 9-6115-639-13&P ... DISTRIBUTION STATEMENT C. Distribution authorized to U.S. "
                                  "Government agencies and their contractors.")
    got, notes = B.public_guide_entries(restricted, guides[:1], "backup_generators")
    assert got[0]["manuals"][0]["link_only"] and "personal use" in notes[0]


def test_heading():
    for key in KEYS + P.HEADING_KEYS:
        assert C.CATEGORIES[key]["heading"] == "Power and electrical", key
    assert not C.CATEGORIES["lawn_garden"].get("heading")


def test_the_index_has_its_heading_and_notice(tmp_path):
    entries, _ = B.maker_entries(FakeFetch({}, ""), C.CATEGORIES["solar_battery_power"]["makers"])
    manifest = B.write("solar_battery_power", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["heading"] == manifest["heading"] == "Power and electrical"
    assert index["notice"] == P.SOLAR_NOTICE
    assert {m["key"] for m in index["makers"]} >= {"renogy", "victron", "enphase", "solaredge", "tesla-energy"}
    assert "heading" not in B.write("lawn_garden", [], str(tmp_path))
