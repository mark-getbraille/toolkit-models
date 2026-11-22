"""A self-test of the small boats picture pack (packs/small_boats_packs.py) and the kit's list of it
(training-kit/kit/small_boats_sources.py), with made-up data only: nothing is downloaded from the internet.

It checks that:
  - the notes say what the owner asked (life jacket, weather, float plan, cold water, never under the influence,
    carbon monoxide, epoxy and solvents) and the kit uses the same words;
  - every answer is "This is ..." and ends with the note that fits its subject (engines the carbon monoxide note,
    deck fittings the line note, boatbuilders the workshop note, every boat the boating note);
  - no Commons category of the pack is named by another pack file (the existing boating packs included), nor twice
    here;
  - the pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflows' known list and limit line, in the
    kit's sources (group "permissive", prepare_pack, never for picture-making), in the machines topic, and the kit
    file listed twice as a hidden import;
  - the builder hands the specs to home_packs.build_commons_topic (tried with a made-up builder).

Run it from the repository's folder:   python3 -m pytest packs/test_small_boats.py
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import small_boats_packs as sb  # noqa: E402

REPO = os.path.dirname(HERE)


def answers():
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in sb.SMALL_BOATS_SPECS for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    for words in ("life jacket", "check the weather", "float plan", "cold water kills", "under the influence",
                  "VHF channel 16"):
        assert words in sb.BOAT_NOTE, words
    assert "carbon monoxide" in sb.ENGINE_NOTE and "cut-off" in sb.ENGINE_NOTE
    assert "epoxy" in sb.WORKSHOP_NOTE and "solvents" in sb.WORKSHOP_NOTE and "respirator" in sb.WORKSHOP_NOTE


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads the kit files at its end
    import small_boats_sources as kit
    for name in ("BOAT_NOTE", "ENGINE_NOTE", "LINE_NOTE", "WORKSHOP_NOTE"):
        assert getattr(kit, name) == getattr(sb, name), name


def test_every_answer_carries_its_note():
    for category, answer in answers():
        assert answer.startswith("This is ") and answer.endswith("."), category
        assert any(n in answer for n in (sb.BOAT_NOTE, sb.ENGINE_NOTE, sb.LINE_NOTE, sb.WORKSHOP_NOTE)), category
        if re.search(r"engine|motorboat|sterndrive|RIB", answer.split(".")[0]):
            assert sb.ENGINE_NOTE in answer, category
    said = dict(answers())
    for category in ("Cleats", "Rowlocks", "Fairleads", "Mooring lines"):
        assert said[category].endswith(sb.LINE_NOTE), category
    assert said["Boatbuilders"].endswith(sb.WORKSHOP_NOTE)
    for spec in sb.BOAT_TYPES:
        assert sb.BOAT_NOTE in spec[2][0][1], spec[0]


def test_no_commons_category_is_used_by_another_pack():
    mine = os.path.abspath(sb.__file__)
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != mine and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in sb.SMALL_BOATS_SPECS]
    assert len(names) == len(set(names)), [n for n in names if names.count(n) > 1]
    for name in names:
        assert f'"{name}"' not in others, name
    import outdoors_packs
    assert not set(names) & {spec[0] for spec in outdoors_packs.OUTDOORS_SPECS}


def test_builder_hands_over_the_specs(monkeypatch):
    import home_packs
    seen = {}

    def made_up(specs, limit, prefix, adults_only=False):
        seen.update(specs=specs, limit=limit, prefix=prefix)
        return [("a.jpg", b"x", {"question": "What is this?", "answer": specs[0][2][0][1]})]
    monkeypatch.setattr(home_packs, "build_commons_topic", made_up)
    rows = sb.build_commons_small_boats(5)
    assert seen["specs"] == sb.SMALL_BOATS_SPECS and seen["limit"] == 5 and seen["prefix"] == "smallboats"
    assert rows[0][2]["answer"].startswith("This is ")


def test_wiring():
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    import sources
    import topics
    import small_boats_sources as kit
    keys = set(sb.SMALL_BOATS_PACKS)
    assert keys == set(sb.SMALL_BOATS_LIMITS) and keys <= set(build_packs.PACKS)
    assert set(sb.SMALL_BOATS_COMMONS_KEYS) == keys and keys <= build_packs.COMMONS_KEYS
    for key, limit in sb.SMALL_BOATS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import small_boats_sources ") == 2
    listed = {s.key: s for s in sources.SOURCES}
    transport = {t.id: set(t.keys) for t in topics.TOPICS}["transport"]
    for s in kit.SMALL_BOATS_SOURCES:
        assert s.key in keys and listed[s.key].group == "permissive" and listed[s.key].prepare is sources.prepare_pack
        assert s.key in sources.NOT_FOR_PICTURE_MAKING and s.key not in kit.SMALL_BOATS_PICTURE_MAKING_OK
        assert s.key in transport, s.key
        assert s.cap == sb.SMALL_BOATS_LIMITS[s.key], s.key
    assert all(reason for reason in kit.SMALL_BOATS_NOT_INCLUDED.values())
