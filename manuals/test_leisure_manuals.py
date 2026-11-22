"""Self-test of the leisure manual collections (the owner's request of 2026-11-22): homestead
(manuals/homestead_manuals.py), outdoors (outdoors_manuals.py), games_hobbies (games_manuals.py), science_instruments
(science_manuals.py) and plant_id (plant_id_manuals.py), with no downloads.

It checks that each category is wired into categories.CATEGORIES under its key, says its safety notice first (the
words the owner asked for), searches the Internet Archive with its own words (none that another collection already
searches, none twice, no firearm or bow words), lists every maker as link-only with its reason and a https address,
with keys unique across them, and links the reference library's books that hold the government guides in full.

Run it from the repository's folder:   python3 -m pytest manuals/test_leisure_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import games_manuals  # noqa: E402
import homestead_manuals  # noqa: E402
import outdoors_manuals  # noqa: E402
import plant_id_manuals  # noqa: E402
import science_manuals  # noqa: E402

MINE = {"homestead": homestead_manuals, "outdoors": outdoors_manuals, "games_hobbies": games_manuals,
        "science_instruments": science_manuals, "plant_id": plant_id_manuals}
NOTICE_WORDS = {"homestead": ("Salmonella", "septic tank", "qualified electrician", "bee stings"),
                "outdoors": ("life jacket", "ice", "safety harness", "Treat every gun as loaded"),
                "games_hobbies": ("publisher", "choking hazard"),
                "science_instruments": ("solar filter", "Sun"),
                "plant_id": ("expert", "1-800-222-1222", "lookalikes")}


def test_wired_with_notice_first():
    for key, mod in MINE.items():
        cat = C.CATEGORIES[key]
        assert cat is mod.CATEGORY and cat["kind"] == "manuals", key
        assert cat["notice"].startswith(("Read the safety section first", "Rules belong", "Read this first")), key
        for words in NOTICE_WORDS[key]:
            assert words in cat["notice"], (key, words)


def test_own_internet_archive_words():
    for key, mod in MINE.items():
        cat = C.CATEGORIES[key]
        taken = {w.lower() for k, c in C.CATEGORIES.items() if k != key for w in c.get("ia") or []}
        assert not set(cat["ia"]) & taken, (key, set(cat["ia"]) & taken)
        assert len(cat["ia"]) == len(set(cat["ia"])), key
        assert not {"crossbow", "compound bow", "rifle", "pistol", "shotgun", "ammunition"} & set(cat["ia"]), key


def test_makers_link_only():
    keys = []
    for key, mod in MINE.items():
        for m in mod.MAKERS:
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key
            keys.append(m["key"])
    assert len(keys) == len(set(keys))
    names = " ".join(m["maker"] for m in outdoors_manuals.MAKERS)
    for brand in ("PENN", "Old Town", "Stearns", "Garmin"):
        assert brand in names, brand


def test_guidance_points_to_the_library():
    links = {key: " ".join(g["title"] + " " + g["url"] for g in mod.GUIDANCE) for key, mod in MINE.items()}
    assert "homestead:epa_private_wells_septic" in links["homestead"]
    assert "outdoors:uscg_boaters_guide_federal_requirements" in links["outdoors"]
    assert "games-hobbies" in links["games_hobbies"] and "science:nasa_skywatching" in links["science_instruments"]
    for mod in MINE.values():
        assert all(g["url"].startswith("https://") and g["by"] for g in mod.GUIDANCE)
