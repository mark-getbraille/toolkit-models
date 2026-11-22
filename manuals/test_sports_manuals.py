"""Self-test of the sports equipment manual collection (manuals/sports_manuals.py, category sports_equipment, heading
"Sports"), with no downloads: it is wired into categories.CATEGORIES with its heading, says its safety notice first
(anchoring goals, trampolines, helmets, concussion, 911), searches the Internet Archive with its own words (none that
another collection already searches, none twice), lists every maker as link-only with its reason and a https address,
and links the reference library's sports guide and the CDC's HEADS UP pages.

Run it from the repository's folder:   python3 -m pytest manuals/test_sports_manuals.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import categories as C  # noqa: E402
import sports_manuals as S  # noqa: E402


def test_wired_with_heading_and_notice():
    cat = C.CATEGORIES["sports_equipment"]
    assert cat is S.CATEGORY and cat["kind"] == "manuals" and cat["heading"] == "Sports"
    assert cat["notice"].startswith("Read the safety section first")
    for words in ("anchor", "tips over", "Trampolines", "helmet", "HEADS UP", "911"):
        assert words in cat["notice"], words


def test_own_internet_archive_words():
    taken = {w.lower() for k, c in C.CATEGORIES.items() if k != "sports_equipment" for w in c.get("ia") or []}
    assert not set(S.IA_WORDS) & taken and len(S.IA_WORDS) == len(set(S.IA_WORDS))
    assert "fitness tracker" not in S.IA_WORDS and "treadmill" not in S.IA_WORDS


def test_makers_link_only_and_guidance():
    keys = [m["key"] for m in S.MAKERS]
    assert len(keys) == len(set(keys))
    other = {m.get("key") for k, c in C.CATEGORIES.items() if k != "sports_equipment" for m in c.get("makers") or []}
    assert not set(keys) & other
    for m in S.MAKERS:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] == "sports_equipment"
    links = " ".join(g["title"] + " " + g["url"] for g in S.GUIDANCE)
    assert "sport:index" in links and "firstaid:cdc_seizures_concussion" in links and "fitness_equipment" in links
    assert all(g["url"].startswith("https://") and g["by"] for g in S.GUIDANCE)
