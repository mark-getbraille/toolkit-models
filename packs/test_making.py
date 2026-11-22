"""A self-test of the home manufacturing and making packs (packs/making_packs.py) and the kit's collections
(training-kit/kit/making_sources.py), with made-up labels only: nothing is downloaded from the internet.

It checks that:
  - every answer about a machine carries its safety notes (3D printer heat, resin, laser eye safety and fumes,
    rotating machinery, blades, heat press, casting, soldering), in the packs and the kit alike, with the same words;
  - the notes say what the owner asked: never look into a laser beam, eyewear rated for the wavelength, never cut PVC
    or vinyl (chlorine gas), resin gloves, no gloves or loose clothing near spinning parts, fire;
  - Open Images rows say only what the labels say, and no label of this pack is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in the machines and home topics (the circuit board pack also in power, the cutting
    machine pack also in crafts), no topic of its own, and the guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_making.py
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import making_packs as m  # noqa: E402

REPO = os.path.dirname(HERE)
NOTE_NAMES = ("PRINTER_NOTE", "RESIN_NOTE", "LASER_NOTE", "FUME_NOTE", "MACHINE_NOTE", "BLADE_NOTE", "CUT_NOTE",
              "HEAT_NOTE", "CASTING_NOTE", "SOLDER_NOTE", "FORMING_NOTE", "PLASMA_NOTE", "FORGE_NOTE")


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    for words in ("never look into the beam", "rated for the laser's wavelength", "Class 4", "fire extinguisher"):
        assert words in m.LASER_NOTE, words
    assert "PVC" in m.FUME_NOTE and "vinyl" in m.FUME_NOTE and "chlorine gas" in m.FUME_NOTE
    assert "nitrile gloves" in m.RESIN_NOTE and "skin" in m.RESIN_NOTE
    assert "no gloves, loose sleeves, jewellery" in m.MACHINE_NOTE and "chuck key" in m.MACHINE_NOTE
    assert "hot enough to burn" in m.PRINTER_NOTE and "smoke alarm" in m.PRINTER_NOTE
    assert "water" in m.CASTING_NOTE and "explode" in m.CASTING_NOTE


def test_every_answer_carries_its_notes():
    notes = [getattr(m, name) for name in NOTE_NAMES]
    for category, answer in answers(m.MAKING_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
        first = answer.split(". ")[0]
        if re.search(r"makerspace|hackerspace|fab lab", first):
            continue                              # a room, not a machine
        if re.search(r"laser", first, re.I) and "sintering" not in first:
            assert m.LASER_NOTE in answer, category
        if re.search(r"laser (cutting|engraving)|CO2|fibre laser", first, re.I):
            assert m.FUME_NOTE in answer, category
        if re.search(r"3D printer|RepRap|Prusa|MakerBot|Ultimaker|Ender|Bambu|extruder|filament fabrication",
                     first) and "resin" not in first:
            assert m.PRINTER_NOTE in answer, category
        if re.search(r"resin|stereolithography|photopolymer", first, re.I):
            assert m.RESIN_NOTE in answer, category
        if re.search(r"lathe|CNC|grinder|milling|rotary table|indexing|machining|woodturning", first, re.I):
            assert m.MACHINE_NOTE in answer, category
        if re.search(r"casting|mould", first, re.I) and "makerspace" not in first:
            assert m.CASTING_NOTE in answer or m.FORMING_NOTE in answer, category
    for category, answer in answers(m.PCB_FABRICATION):
        assert m.SOLDER_NOTE in answer or m.MACHINE_NOTE in answer, category
    # no setting or temperature is made up: only the category's own names and the notes
    for _category, answer in answers(m.MAKING_SPECS):
        rest = answer
        for note in notes:
            rest = rest.replace(note, "")
        assert not re.search(r"\d+\s*(°|degrees|mm|watts?\b|W\b)", rest), answer
    # OpenSCAD is said to suit screen reader users (the owner asked for it to be stressed)
    assert "screen reader" in next(a for c, a in answers(m.PRINTING) if c == "OpenSCAD")


def test_word_filter():
    blender = next(s for s in m.PRINTING if s[0] == "Blender (software)")
    assert blender[3].search("Low-poly 3D model of a chair rendered in Blender")
    assert not blender[3].search("Big Buck Bunny poster")


def rows_of(labels):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, m.MAKING_OI, random.Random(1))


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in rows_of({"Metal lathe": 1, "Laser": 0})}
    assert said["What machine tools are in this picture?"] == f"I can see a metal lathe. {m.MACHINE_NOTE}"
    assert said["Is there a laser in this picture?"] == "No, I can't see a laser in this picture."
    said = {r["question"]: r["answer"] for r in rows_of({"Soldering iron": 1, "Calipers": 1})}
    assert said["What soldering things are in this picture?"] == f"I can see a soldering iron. {m.SOLDER_NOTE}"
    assert said["What measuring and holding tools are in this picture?"] == "I can see calipers."
    assert rows_of({"Workshop": 1, "Nudity": 1}) == []
    entries = [("a.jpg", b"x", {"question": "Is there a laser in this picture?",
                                 "answer": "Yes, there is a laser in this picture."}),
               (None, None, {"question": "Is there a workshop in this picture?",
                             "answer": "Yes, there is a workshop in this picture."})]
    got = [row["answer"] for _n, _d, row in m.with_yes_notes(entries, m.MAKING_OI)]
    assert got[0].endswith(m.LASER_NOTE) and got[1] == "Yes, there is a workshop in this picture."


def asked_elsewhere():
    """Every Open Images label another pack file asks about (the same reading as packs/test_outdoor_cooking.py)."""
    import glob
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name == m.__name__:
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


def test_no_open_images_label_is_asked_twice():
    mine = g.gap_labels(m.MAKING_OI)
    assert not mine & asked_elsewhere(), mine & asked_elsewhere()
    labels = [label for grp in m.MAKING_OI for label in grp["things"]]
    assert len(labels) == len(set(labels))
    for grp in m.MAKING_OI:
        assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    import glob
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(m.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in m.MAKING_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads making_sources at its end
    import making_sources as k
    for name in NOTE_NAMES:
        assert getattr(k, name) == getattr(m, name), name
    pack_answers = dict(answers(m.MAKING_SPECS))
    for category, _q, answer, _deeper in k.MAKING_SA:
        assert pack_answers[category] == answer, category
    assert all(reason for reason in k.MAKING_NOT_INCLUDED.values())


def test_wiring():
    keys = set(m.MAKING_PACKS)
    assert keys == set(m.MAKING_LIMITS) and len(keys) == 6
    assert keys <= set(build_packs.PACKS)
    assert set(m.MAKING_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(m.MAKING_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    workflows = os.path.join(REPO, ".github", "workflows")
    with open(os.path.join(workflows, "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(workflows, "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(workflows, "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in m.MAKING_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import making_sources") == 2
    import sources
    import topics
    import making_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert (key in no_making) == (key not in k.MAKING_PICTURE_MAKING_OK), key
    for s in k.MAKING_SOURCES:
        assert s.key in listed, s.key
        assert s.key in keys or s.group != "permissive", s.key
    assert listed["making_commons_sa"].group == "share-alike"
    assert "open_images_making" in no_making and "commons_moulding_casting" in no_making
    assert "commons_3d_printing" not in no_making
    # the topics: machines and home hold everything, power the circuit board pack, crafts the cutting machine pack;
    # no topic of its own
    for topic_id, topic_keys in k.MAKING_TOPICS.items():
        assert set(topic_keys) <= set(topics.find(topic_id).keys), topic_id
    assert set(k.MAKING_TOPICS) == {"machines", "home", "power", "crafts"}
    assert k.MAKING_TOPICS["crafts"] == ("commons_cutting_lasers",)        # craft cutters and heat presses
    for topic in topics.TOPICS:                                             # no other making pack elsewhere
        held = {s.key for s in k.MAKING_SOURCES} & set(topic.keys)
        assert held <= set(k.MAKING_TOPICS.get(topic.id, ())), topic.id
    assert not [t for t in topics.TOPICS if t.id in ("making", "manufacturing", "home_manufacturing")]
