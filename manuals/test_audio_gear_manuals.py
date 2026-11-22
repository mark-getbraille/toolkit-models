"""Self-test of the audio recorders and recording gear manual collection (manuals/audio_gear_manuals.py and its line in
categories.py), with no downloads.

It checks that the category is listed under its key with a plain name, the kind "manuals", a licence and a notice
said first (hearing, batteries, asking before recording people); that its Internet Archive words are unique and that
no other collection already searches them, nor a word inside one of them (so a manual is not listed twice); that
every maker is link-only with its reason, an https address, no manual-copying site and a unique key; that the
guidance links name their books in the reference library (textbooks/audio_media.py); and that pet supplies stay in
the existing pet_livestock_supplies collection (no second pet collection).

Run it from the repository's folder:   python3 -m pytest manuals/test_audio_gear_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402


def test_category_listed():
    cat = C.CATEGORIES["audio_gear"]
    assert cat["name"] and cat["kind"] == "manuals" and cat["licence"] and cat["description"]
    for words in ("volume down", "batteries", "recording laws"):
        assert words in cat["notice"], words
    assert cat["ia"] and len(cat["ia"]) == len(set(cat["ia"]))


def test_no_word_another_collection_searches():
    mine = {w.lower() for w in C.CATEGORIES["audio_gear"]["ia"]}
    theirs = {w.lower() for k, c in C.CATEGORIES.items() if k != "audio_gear" for w in c.get("ia") or []}
    assert not mine & theirs, mine & theirs
    assert not [(a, b) for a in mine for b in theirs if a in b or b in a]
    assert "microphone" in C.CATEGORIES["musical_instruments"]["ia"]     # microphones stay there


def test_makers_are_link_only():
    makers = C.CATEGORIES["audio_gear"]["makers"]
    keys = [m["key"] for m in makers]
    assert makers and len(keys) == len(set(keys))
    for m in makers:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "audio_gear" and m["prefix"] == "ag"
        for site in B.NEVER_SITES:
            assert site not in str(m), m["key"]


def test_guidance_names_the_books():
    for guide in C.CATEGORIES["audio_gear"]["guidance"]:
        assert guide["url"].startswith("https://") and guide["title"] and guide["by"]
        assert "media:" in guide["title"], guide["title"]


def test_pet_supplies_not_repeated():
    assert "pet_livestock_supplies" in C.CATEGORIES
    pets = [k for k, c in C.CATEGORIES.items() if "pet" in c.get("name", "").lower()]
    assert pets == ["pet_livestock_supplies"], pets
