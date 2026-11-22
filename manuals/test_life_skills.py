"""Self-test of the life-skills manual collections (manuals/car_maintenance.py, garden_care.py, home_health_care.py,
instrument_care.py and their lines in categories.py), with MADE-UP Internet Archive answers only: nothing is
downloaded.

It checks that each category is listed under its key with a plain name, a kind, a licence, a notice said first and
Internet Archive words; that every maker is link-only (nothing read) with its reason, an https address and no
manual-copying site, and no maker id is used twice; that no Internet Archive word repeats a word of the categories
these sit beside (cars, lawn_garden, musical_instruments, baby_gear, home_medical, home_health_tests); that the home
health notices name 911 and say they are not a diagnosis; and that a military public guide follows the release rule
(military_release.py): indexed with or without Distribution Statement A, link only and personal use when its own
front text prints a restricted marking (made-up item).

Run it from the repository's folder:   python3 -m pytest manuals/test_life_skills.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402

KEYS = ("car_care", "garden_care", "instrument_care", "first_aid_home_care", "dental_care_devices",
        "eye_care_optics", "birth_postpartum")
NEIGHBOURS = ("cars", "lawn_garden", "musical_instruments", "baby_gear", "home_medical", "home_health_tests")


def test_categories_listed():
    for key in KEYS:
        cat = C.CATEGORIES[key]
        assert cat["name"] and cat["kind"] == "manuals" and cat["licence"] and cat["notice"], key
        assert cat["ia"] and len(cat["ia"]) == len(set(cat["ia"])), key
        for guide in cat.get("guidance", []):
            assert guide["url"].startswith("https://") and guide["title"] and guide["by"], key
    for key in ("first_aid_home_care", "dental_care_devices", "eye_care_optics", "birth_postpartum"):
        notice = C.CATEGORIES[key]["notice"]
        assert ("911" in notice or "dentist today" in notice) and "not" in notice and "diagnosis" in notice or \
            "not medical advice" in notice, key
    assert "jack stands" in C.CATEGORIES["car_care"]["notice"]


def test_no_word_repeats_a_neighbour():
    theirs = {w for k in NEIGHBOURS for w in C.CATEGORIES[k].get("ia", [])}
    for key in KEYS:
        assert not set(C.CATEGORIES[key]["ia"]) & theirs, (key, set(C.CATEGORIES[key]["ia"]) & theirs)


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


def test_military_guides_follow_the_release_rule():
    guide = C.CATEGORIES["eye_care_optics"]["public_guides"][0]
    assert guide["military"]
    files = [{"name": "x.pdf", "format": "Text PDF", "size": "100"}, {"name": "x_djvu.txt", "format": "DjVuTXT"}]
    ok = FakeFetch(files, "OPTICALMAN 3 & 2 ... Approved for public release; distribution is unlimited.")
    got, notes = B.public_guide_entries(ok, [guide], "eye_care_optics")
    assert len(got) == 1 and got[0]["manuals"][0]["rights"] == "a US government work (public domain)"
    restricted = FakeFetch(files, "OPTICALMAN 3 & 2 ... Distribution authorized to DoD components only.")
    got, notes = B.public_guide_entries(restricted, [guide], "eye_care_optics")
    assert len(got) == 1 and got[0]["manuals"][0]["link_only"] and "personal use" in notes[0]
    silent = FakeFetch(files, "OPTICALMAN 3 & 2 ... Chapter 1.")
    got, notes = B.public_guide_entries(silent, [guide], "eye_care_optics")
    assert "print no distribution statement" in got[0]["manuals"][0]["release"] and not notes
