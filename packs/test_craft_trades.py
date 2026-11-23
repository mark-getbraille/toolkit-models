"""A self-test of the craft trades picture pack (packs/craft_trades_packs.py) and the kit's craft trades collection
(training-kit/kit/craft_trades_sources.py), with made-up data only: nothing is downloaded.

It checks that every answer says what the category is and ends with its trade's safety note where one fits (the same
words in the pack and the kit); that no Commons category is named twice here or by any other pack file; that the
pack is built from its specs; and that it is wired (build_packs and COMMONS_KEYS, the workflows' pack list and limit,
the kit's sources as a permissive ready-made pack, the "crafts" topic only, never used for picture-making, the two
hidden imports).

Run it from the repository's folder:   python3 -m pytest packs/test_craft_trades.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import craft_trades_packs as t  # noqa: E402
from test_electronics import quoted_elsewhere, workflows  # noqa: E402


def answers():
    """{category: its one answer} of the pack's specs."""
    return {spec[0]: spec[2][0][1] for spec in t.CRAFT_TRADES_SPECS}


def test_answers_and_notes():
    a = answers()
    for spec in t.CRAFT_TRADES_SPECS:
        (question, answer), = spec[2]
        assert question == "What is this?" and answer.startswith("This is "), spec[0]
    for category in ("Queen excluders", "Hive frames", "Feeding bees", "Personal protective equipment for beekeeping"):
        assert a[category].endswith(t.BEE_NOTE), category
    for spec in t.GLASSWORK:
        assert a[spec[0]].endswith(t.GLASS_NOTE), spec[0]
    for spec in t.LEATHERWORK:
        assert a[spec[0]].endswith(t.LEATHER_NOTE), spec[0]
    assert "911" in t.BEE_NOTE and "eye protection" in t.GLASS_NOTE and "solvents" in t.LEATHER_NOTE
    import sources  # noqa: F401 - loaded first
    import craft_trades_sources as k
    assert (k.BEE_NOTE, k.GLASS_NOTE, k.LEATHER_NOTE) == (t.BEE_NOTE, t.GLASS_NOTE, t.LEATHER_NOTE)


def test_no_category_twice_or_elsewhere():
    """No category is named twice here, and none is named (in quotes) by any other pack file; the parent category
    Beekeeping equipment is not read whole (it holds the homestead pack's categories), and nothing is read deeper."""
    others = quoted_elsewhere(("craft_trades_packs",))
    seen = set()
    for spec in t.CRAFT_TRADES_SPECS:
        assert spec[0] not in seen, spec[0]
        seen.add(spec[0])
        assert f'"{spec[0]}"' not in others, f"{spec[0]} is used by another pack"
        assert spec[1] is False, spec[0]
    assert "Beekeeping equipment" not in seen and "Tailoring" not in seen and "Lampworking" not in seen
    assert len(seen) == 27


def test_pack_is_built_from_its_specs(monkeypatch):
    import home_packs
    calls = []
    monkeypatch.setattr(home_packs, "build_commons_topic",
                        lambda specs, limit, prefix, adults_only=False: calls.append((specs, limit, prefix)) or [])
    assert t.build_commons_craft_trades(5) == []
    assert calls == [(t.CRAFT_TRADES_SPECS, 5, "crafttrades")]


def test_wiring():
    packs_yml, build_yml, kit_yml = workflows()
    keys = set(t.CRAFT_TRADES_PACKS)
    assert keys == set(t.CRAFT_TRADES_LIMITS) == set(t.CRAFT_TRADES_COMMONS_KEYS) == {"commons_craft_trades"}
    assert keys <= set(build_packs.PACKS) and keys <= build_packs.COMMONS_KEYS
    for key, limit in t.CRAFT_TRADES_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import craft_trades_sources") == 2
    import sources
    import topics
    import craft_trades_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert set(k.CRAFT_TRADES_PACK_KEYS) == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert listed[key].cap == t.CRAFT_TRADES_LIMITS[key], key
        assert key in sources.NOT_FOR_PICTURE_MAKING and key not in sources.PERSONAL_PICTURE_MAKING_OK, key
    for topic in topics.TOPICS:
        held = keys & set(topic.keys)
        assert held == set(k.CRAFT_TRADES_TOPICS.get(topic.id, ())), topic.id
    assert k.CRAFT_TRADES_NOT_INCLUDED and not k.CRAFT_TRADES_PICTURE_MAKING_OK
