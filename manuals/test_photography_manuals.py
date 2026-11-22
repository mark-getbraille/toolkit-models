"""Self-test of the photography manual collections (manuals/photography_manuals.py: film_cameras_darkroom and
digital_cameras), with no downloads: they are wired into categories.CATEGORIES under the "Arts and crafts" heading
together with the darkroom chemicals collection photo_chemicals; the safety notice is said first (darkroom chemicals,
batteries, flash capacitors, nitrate film); each searches the Internet Archive with its own words (none another
collection already searches, none twice); every maker is link-only with its reason and a https address (Mike Butkus's
library among them); the Army equipment manuals are US government works judged by the military release rule; and
the guidance links the reference library's photography guide and the chemicals collection.

Run it from the repository's folder:   python3 -m pytest manuals/test_photography_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import photography_manuals as P  # noqa: E402

MINE = ("film_cameras_darkroom", "digital_cameras")


def test_wired_with_heading_and_notice():
    for key in MINE:
        cat = C.CATEGORIES[key]
        assert cat is P.CATEGORIES[key] and cat["kind"] == "manuals" and cat["heading"] == "Arts and crafts"
        assert cat["notice"].startswith("Read the safety section first")
    for words in ("ventilation", "nitrile gloves", "never mix", "used fixer", "photo_chemicals", "lithium battery",
                  "capacitor", "nitrate"):
        assert words in P.NOTICE, words
    assert C.CATEGORIES["photo_chemicals"]["heading"] == "Arts and crafts"


def test_own_internet_archive_words():
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k not in MINE for w in c.get("ia") or []}
    for words in (P.FILM_WORDS, P.DIGITAL_WORDS):
        assert not set(words) & taken and len(words) == len(set(words))
    assert not set(P.FILM_WORDS) & set(P.DIGITAL_WORDS)
    for word in ("film camera", "35mm", "digital camera", "trail camera", "security camera"):
        assert word not in P.FILM_WORDS + P.DIGITAL_WORDS, word


def test_makers_link_only_and_guides():
    makers = P.FILM_MAKERS + P.DIGITAL_MAKERS
    keys = [m["key"] for m in makers]
    assert len(keys) == len(set(keys))
    other = {m.get("key") for k, c in C.CATEGORIES.items() if k not in MINE for m in c.get("makers") or []}
    assert not set(keys) & other
    for m in makers:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] in MINE
    assert "butkus" in keys and any("Butkus" in m["maker"] for m in P.FILM_MAKERS)
    for g in P.ARMY_GUIDES:
        assert g["military"] and g["by"] == "the US Army" and g["year"] < 1950 and g["ia"].startswith("TM11-")
    links = " ".join(g["title"] + " " + g["url"] for g in P.GUIDANCE)
    assert "photo:index" in links and "photo_chemicals" in links
    assert all(g["url"].startswith("https://") and g["by"] for g in P.GUIDANCE)
