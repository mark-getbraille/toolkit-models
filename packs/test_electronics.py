"""A self-test of the electronics repair and assistive-device packs (packs/electronics_packs.py) and the kit's
electronics collections (training-kit/kit/electronics_sources.py), with made-up titles and labels only: nothing is
downloaded from the internet.

It checks that:
  - a part's value or a battery's size is said only when the file's own words state exactly one, and never a guess;
  - lithium, mains, soldering and device-care notes follow the answers they belong to, in the packs and the kit;
  - Open Images rows say only what the labels say, and no label of these packs is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources ("permissive" packs, the share-alike entry), in the machines
    topic, never for picture-making unless the kit module says so, and the kit module listed twice as a hidden
    import.

Run it from the repository's folder:   python3 -m pytest packs/test_electronics.py
"""

import glob
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import electronics_packs as e  # noqa: E402

REPO = os.path.dirname(HERE)
OURS = ("electronics_packs", "building_packs", "crafts_packs")


def asked_elsewhere(ours=OURS):
    """Every Open Images label another pack file asks about (as packs/test_daily_access.py reads them)."""
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name in ours:
            continue
        mod = importlib.import_module(name)
        for var, value in vars(mod).items():
            if var.startswith("OI_") and isinstance(value, dict):
                elsewhere |= set(value)
            elif isinstance(value, list) and value and all(isinstance(x, dict) and "things" in x for x in value):
                elsewhere |= g.gap_labels(value)
            elif var == "OI_GROUP_QUESTIONS":
                for grp in value:
                    elsewhere |= set(grp[0])
    return elsewhere


def quoted_elsewhere(ours=OURS):
    """The text of every pack file but ours and the tests (for the Commons category check)."""
    text = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        name = os.path.basename(path)[:-3]
        if name not in ours and not name.startswith("test_"):
            with open(path, encoding="utf-8") as f:
                text += f.read()
    return text


def workflows():
    """(packs.yml, pack-build.yml, training-kit.yml) as text."""
    out = []
    for name in ("packs.yml", "pack-build.yml", "training-kit.yml"):
        with open(os.path.join(REPO, ".github", "workflows", name), encoding="utf-8") as f:
            out.append(f.read())
    return out


def test_values_only_from_the_files_own_words():
    assert e.stated_value("File:Carbon resistor 220 ohm.jpg") == "220 ohms"
    assert e.stated_value("4.7kΩ resistors in a row") == "4.7 kilohms"
    assert e.stated_value("SMD resistor marked 4k7") == "4.7 kilohms"
    assert e.stated_value("Electrolytic capacitor 1000 µF 25V") == "1000 microfarads"
    assert e.stated_value("100nF ceramic capacitor") == "100 nanofarads"
    assert e.stated_value("Glass fuse 5A, blown") == "5 amps"
    assert e.stated_value("Resistors of 10 ohm and 100 ohm") == ""              # two values: neither said
    assert e.stated_value("A brown, black and orange banded resistor") == ""      # never read from the bands
    assert e.stated_battery("CR2032 lithium coin cell") == "CR2032"
    assert e.stated_battery("AA and AAA batteries side by side") == ""
    assert e.stated_battery("PP3 battery") == "9V"
    rows = e.part_facts("File:Li-ion 18650 cell.jpg", "")
    assert rows == [(e.BATTERY_Q, "The file's own words give its size: 18650. " + e.LITHIUM_NOTE)]
    assert e.part_facts("File:Resistor.jpg", "A resistor on a board.") == []


def test_notes_follow_their_answers():
    answers = {spec[0]: spec[2][0][1] for spec in e.ELECTRONICS_SPECS}
    for category in ("Lithium-ion batteries", "18650 batteries", "Laptop batteries", "Disassembled smartphones"):
        assert answers[category].endswith(e.LITHIUM_NOTE), category
    for category in ("Vacuum tubes", "Cathode ray tubes", "Radio repair", "Vacuum tube radios"):
        assert answers[category].endswith(e.MAINS_NOTE), category
    for category in ("Soldering stations", "Desoldering", "Solder wires"):
        assert answers[category].endswith(e.SOLDER_NOTE), category
    assert answers["Burnt fuses"].endswith(e.FUSE_NOTE)
    for spec in e.ASSISTIVE:
        if spec[0] not in ("Monoculars", "Screen protectors", "Mobile phone cases", "Computer speakers"):
            assert spec[2][0][1].endswith(e.DEVICE_NOTE), spec[0]
    assert "NLS" in e.DEVICE_NOTE and "VIST" in e.DEVICE_NOTE
    assert all(a.startswith("This is ") for a in answers.values())
    assert "can kill" in e.MAINS_NOTE and "recycling" in e.LITHIUM_NOTE and "lead" in e.SOLDER_NOTE
    import sources  # noqa: F401 - loaded first: it loads electronics_sources at its end
    import electronics_sources as k
    assert (k.MAINS_NOTE, k.LITHIUM_NOTE, k.SOLDER_NOTE) == (e.MAINS_NOTE, e.LITHIUM_NOTE, e.SOLDER_NOTE)
    sa = {c: a for c, _q, a, _d in k.ELECTRONICS_SA}
    assert sa["Lithium-ion batteries"].endswith(k.LITHIUM_NOTE) and sa["Vacuum tubes"].endswith(k.MAINS_NOTE)


def test_open_images_rows():
    rows = g.oi_gap_rows({"Diode": 1, "Fuse": 1, "Electronics": 0}, e.ELECTRONICS_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What electronic parts are in this picture?"] == "I can see a diode and a fuse."
    assert said["Are there any electronics in this picture?"] == "No, I can't see any electronics in this picture."
    assert e.stated_value("A 5A plug") == ""                                  # amps only for a fuse
    rows = g.oi_gap_rows({"Solder": 1}, e.ELECTRONICS_OI, random.Random(1))
    assert rows[0]["answer"] == "I can see solder. " + e.SOLDER_NOTE
    assert g.oi_gap_rows({"Diode": 1, "Nudity": 1}, e.ELECTRONICS_OI, random.Random(1)) == []


def test_no_label_or_category_is_used_twice():
    elsewhere = asked_elsewhere()
    import building_packs as b
    import crafts_packs as c
    mine = [e.ELECTRONICS_OI, b.BUILDING_OI, c.CRAFTS_OI]
    for groups in mine:
        assert not g.gap_labels(groups) & elsewhere, g.gap_labels(groups) & elsewhere
        for grp in groups:
            assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())
    for i, a in enumerate(mine):
        for other in mine[i + 1:]:
            assert not g.gap_labels(a) & g.gap_labels(other)
    others = quoted_elsewhere()
    seen = set()
    for spec in e.ELECTRONICS_SPECS + b.BUILDING_SPECS + c.CRAFTS_SPECS:
        assert spec[0] not in seen, spec[0]
        seen.add(spec[0])
        assert f'"{spec[0]}"' not in others, f"{spec[0]} is used by another pack"


def test_wiring():
    packs_yml, build_yml, kit_yml = workflows()
    keys = set(e.ELECTRONICS_PACKS)
    assert keys == set(e.ELECTRONICS_LIMITS) and keys <= set(build_packs.PACKS)
    assert set(e.ELECTRONICS_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(e.ELECTRONICS_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    for key, limit in e.ELECTRONICS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import electronics_sources") == 2
    import sources
    import topics
    import electronics_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert set(k.ELECTRONICS_PACK_KEYS) == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
    assert listed["electronics_commons_sa"].group == "share-alike"
    machines = set(topics.find("machines").keys)
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for s in k.ELECTRONICS_SOURCES:
        assert s.key in machines, s.key
        assert (s.key in no_making) == (s.key not in k.ELECTRONICS_PICTURE_MAKING_OK), s.key
    assert "commons_assistive_devices" in no_making and "commons_electronic_parts" not in no_making
