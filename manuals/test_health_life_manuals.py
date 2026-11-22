"""Self-test of the health and life manual collections (manuals/sleep_relaxation_manuals.py, fitness_manuals.py,
sexual_health_manuals.py, aging_manuals.py and wilderness_manuals.py, and their lines in categories.py), with no
downloads.

It checks that each category is listed under its key with a plain name, the kind "manuals", a licence, a notice said
first with its health note (911; 988 for the health ones; the SOS of a messenger or PLB for the wilderness one) and
Internet Archive words that no other collection already searches; that every maker is link-only with its reason, an
https address, no manual-copying site and no maker key used twice; and that the guidance links are https pages of
government sites, each naming its book in the reference library where there is one.

Run it from the repository's folder:   python3 -m pytest manuals/test_health_life_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402

KEYS = ("sleep_relaxation", "fitness_equipment", "contraceptive_products", "aging_in_place", "wilderness_first_aid")


def test_categories_listed():
    for key in KEYS:
        cat = C.CATEGORIES[key]
        assert cat["name"] and cat["kind"] == "manuals" and cat["licence"] and cat["description"], key
        notice = cat["notice"]
        assert "911" in notice and ("not medical advice" in notice or "not training" in notice), key
        if key == "wilderness_first_aid":
            assert "SOS" in notice and "personal locator beacon" in notice and "course" in notice
        else:
            assert "988" in notice, key
        assert cat["ia"] and len(cat["ia"]) == len(set(cat["ia"])), key
        for guide in cat["guidance"]:
            assert guide["url"].startswith("https://") and guide["title"] and guide["by"], key
            assert ".gov/" in guide["url"], (key, guide["url"])


def test_no_word_another_collection_searches():
    for key in KEYS:
        mine = {w.lower() for w in C.CATEGORIES[key]["ia"]}
        theirs = {w.lower() for k, c in C.CATEGORIES.items() if k != key for w in c.get("ia") or []}
        assert not mine & theirs, (key, mine & theirs)


def test_makers_are_link_only():
    seen = set()
    for key in KEYS:
        makers = C.CATEGORIES[key]["makers"]
        assert makers, key
        for m in makers:
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key and m["types"] == []
            assert (m["prefix"], m["key"]) not in seen, m["key"]
            seen.add((m["prefix"], m["key"]))
            for site in B.NEVER_SITES:
                assert site not in str(m), m["key"]
    radio = " ".join(str(c.get("makers", "")) for k, c in C.CATEGORIES.items() if k.startswith("radio"))
    assert "inreach" in radio.lower()            # the beacons and messengers stay in the radio section
    assert "inreach" not in str(C.CATEGORIES["wilderness_first_aid"]["makers"]).lower()
