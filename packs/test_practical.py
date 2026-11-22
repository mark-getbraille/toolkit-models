"""A self-test of the practical life packs (packs/practical_packs.py and its six files: driving, computer basics,
cleaning, knots and outdoor skills, pool equipment, motorcycles, RVs and trailers) and the kit's collections
(training-kit/kit/practical_sources.py), with made-up labels only: nothing is downloaded from the internet.

It checks that:
  - the safety notes say what the owner asked (seat belts and never driving impaired, stopping for school buses,
    never mixing bleach with ammonia, drowning prevention and never mixing pool chemicals, rope and sharp tools,
    towing, RV propane and carbon monoxide, DOT helmets) and are the same words in the packs and the kit;
  - every answer carries the note that fits its subject;
  - the pool pack is equipment only (no swimming or swimwear category, no Hot tubs, adults only) and its word filter
    keeps pool files only; the knot pack has no noose or BDSM category;
  - Open Images rows say only what the labels say, and no label of these packs is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in the machines or home topic, and the guarded kit module listed twice as a hidden
    import.

Run it from the repository's folder:   python3 -m pytest packs/test_practical.py
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
import practical_packs as p  # noqa: E402
import computer_basics_packs as pc  # noqa: E402
import driving_packs as dr  # noqa: E402
import household_packs as hh  # noqa: E402
import knots_outdoor_packs as kn  # noqa: E402
import motorcycles_rvs_packs as mr  # noqa: E402
import pools_spas_packs as po  # noqa: E402

REPO = os.path.dirname(HERE)
MODULES = (dr, pc, hh, kn, po, mr)
MINE = {m.__name__ for m in MODULES} | {p.__name__}


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    assert "buckles up" in dr.DRIVE_NOTE and "never drive after drinking" in dr.DRIVE_NOTE
    assert "stop arm" in dr.SCHOOL_BUS_NOTE and "white cane" in dr.PEDESTRIAN_NOTE
    assert "bleach mixed with ammonia" in hh.MIX_NOTE and "1-800-222-1222" in hh.MIX_NOTE
    assert "never leave children alone" in po.DROWNING_NOTE and "self-latching gate" in po.DROWNING_NOTE
    assert "drain covers" in po.DROWNING_NOTE and "CPR" in po.DROWNING_NOTE
    assert "Never mix different pool chemicals" in po.POOL_CHEM_NOTE
    assert "rated gear" in kn.ROPE_NOTE and "eye protection" in kn.TOOL_NOTE
    assert "10 to 15 percent" in mr.TOW_NOTE and "safety chains" in mr.TOW_NOTE and "breakaway" in mr.TOW_NOTE
    assert "carbon monoxide" in mr.RV_NOTE and "propane off" in mr.RV_NOTE
    assert "DOT-approved helmet" in mr.MOTO_NOTE and "FMVSS 218" in mr.MOTO_NOTE
    assert "restart it first" in pc.TECH_NOTE and "official app store" in pc.TECH_NOTE
    # The pool chemical note is the household chemical packs' own words.
    import chemical_packs
    assert po.POOL_CHEM_NOTE == chemical_packs.SAFETY["pool"]


def test_every_answer_carries_its_note():
    for category, answer in answers(p.PRACTICAL_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
    for category, answer in answers(dr.DRIVING):
        assert any(n in answer for n in (dr.DRIVE_NOTE, dr.SCHOOL_BUS_NOTE, dr.PEDESTRIAN_NOTE,
                                         dr.PASSENGER_NOTE)), category
    for category, answer in answers(hh.CLEANING_TOOLS):
        if re.search(r"mop|sponge|toilet|glove|spray", category, re.I):
            assert hh.MIX_NOTE in answer, category
    for category, answer in answers(kn.KNOTS):
        if re.search(r"climb|rescue|loads|belay", answer.split(". ")[0], re.I):
            assert kn.ROPE_NOTE in answer, category
    for category, answer in answers(kn.OUTDOOR_SKILLS):
        if re.search(r"axe|hatchet|saw|whetstone|sharpener", category, re.I):
            assert kn.TOOL_NOTE in answer, category
    for category, answer in answers(po.POOL_EQUIPMENT):
        assert po.DROWNING_NOTE in answer, category
        if re.search(r"pump|filter|equipment", category, re.I):
            assert po.POOL_CHEM_NOTE in answer, category
    for category, answer in answers(mr.TRAILERS_RVS):
        assert any(n in answer for n in (mr.TOW_NOTE, mr.RV_NOTE, mr.DUMP_NOTE)), category
    for category, answer in answers(mr.MOTORCYCLE_GEAR):
        assert mr.MOTO_NOTE in answer, category


def test_pools_equipment_only_and_knots_wanted():
    names = " ".join(spec[0] for spec in po.POOL_EQUIPMENT).lower()
    for word in ("swimwear", "bikini", "swimmer", "bather", "hot tub", "swimming in"):
        assert word not in names, word
    sand = next(s for s in po.POOL_EQUIPMENT if s[0] == "Sand filters")
    assert sand[3].search("Sand filter of a swimming pool") and not sand[3].search("Rapid sand filter, water works")
    crook = next(s for s in po.POOL_EQUIPMENT if s[0] == "Shepherd's crooks")
    assert crook[3].search("Lifeguard rescue hook by the pool") and not crook[3].search("Shepherd with crook and sheep")
    for spec in kn.KNOTS:
        assert not re.search(r"noose|bdsm|shibari|hangman", spec[0], re.I), spec[0]
        assert spec[2][0][0] == kn.ASK_KNOT


def rows_of(labels, groups):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1))


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in rows_of({"Seat belt": 1, "Parking meter": 0}, dr.DRIVING_OI)}
    assert said["What car controls are in this picture?"] == f"I can see a seat belt. {dr.DRIVE_NOTE}"
    assert said["Is there a parking meter in this picture?"] == "No, I can't see a parking meter in this picture."
    said = {r["question"]: r["answer"] for r in rows_of({"Motorcycle helmet": 1}, mr.MOTO_RV_OI)}
    assert said["What motorcycle gear is in this picture?"] == f"I can see a motorcycle helmet. {mr.MOTO_NOTE}"
    said = {r["question"]: r["answer"] for r in rows_of({"Drain cleaner": 1}, hh.CLEANING_OI)}
    assert said["What cleaning supplies are in this picture?"] == f"I can see drain cleaner. {hh.MIX_NOTE}"
    assert rows_of({"Bow saw": 1, "Nudity": 1}, kn.KNOTS_OI) == []
    entries = [("a.jpg", b"x", {"question": "Is there a travel trailer in this picture?",
                                 "answer": "Yes, there is a travel trailer in this picture."}),
               (None, None, {"question": "Is there a mousepad in this picture?",
                             "answer": "Yes, there is a mousepad in this picture."})]
    got = [row["answer"] for _n, _d, row in mr.with_yes_notes(entries, mr.MOTO_RV_OI)]
    assert got[0].endswith(mr.TOW_NOTE)
    got = [row["answer"] for _n, _d, row in pc.with_yes_notes(entries, pc.COMPUTER_OI)]
    assert got[1] == "Yes, there is a mousepad in this picture."
    assert all(r.get("child") for r in rows_of({"School bus": 0, "Lane": 1, "Boy": 1}, dr.DRIVING_OI))


def asked_elsewhere():
    """Every Open Images label another pack file asks about (the same reading as packs/test_outdoor_cooking.py)."""
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name in MINE:
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
    mine = g.gap_labels(p.PRACTICAL_OI_GROUPS)
    assert not mine & asked_elsewhere(), mine & asked_elsewhere()
    labels = [label for grp in p.PRACTICAL_OI_GROUPS for label in grp["things"]]
    assert len(labels) == len(set(labels))
    for grp in p.PRACTICAL_OI_GROUPS:
        assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        name = os.path.basename(path)[:-3]
        if name not in MINE and not name.startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in p.PRACTICAL_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads practical_sources at its end
    import practical_sources as k
    for name in k.NOTE_NAMES:
        mine = [getattr(m, name) for m in MODULES if hasattr(m, name)]
        assert mine and all(x == getattr(k, name) for x in mine), name
    knot_answers = {spec[0]: spec[2][0][1] for spec in kn.KNOTS}
    for category, question, answer, _deeper in k.KNOTS_SA:
        assert knot_answers[category] == answer and question == kn.ASK_KNOT, category
    assert all(reason for reason in k.PRACTICAL_NOT_INCLUDED.values())


def test_wiring():
    keys = set(p.PRACTICAL_PACKS)
    assert keys == set(p.PRACTICAL_LIMITS) and len(keys) == 13
    assert keys <= set(build_packs.PACKS)
    assert set(p.PRACTICAL_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(p.PRACTICAL_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    assert all(k.startswith("commons_") for k in p.PRACTICAL_COMMONS_KEYS)
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in p.PRACTICAL_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import practical_sources") == 2
    import sources
    import topics
    import practical_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert (key in no_making) == (key not in k.PRACTICAL_PICTURE_MAKING_OK), key
    for topic_id, topic_keys in k.PRACTICAL_TOPICS.items():
        assert set(topic_keys) <= set(topics.find(topic_id).keys), topic_id
    in_topics = {key for topic_keys in k.PRACTICAL_TOPICS.values() for key in topic_keys}
    assert in_topics == {s.key for s in k.PRACTICAL_SOURCES}
    for s in k.PRACTICAL_SOURCES:
        assert s.key in listed, s.key
        assert s.key in keys or s.group != "permissive", s.key
    assert listed["knots_commons_sa"].group == "share-alike"
    assert "commons_driving" in no_making and "open_images_cleaning" in no_making
    assert "commons_knots" not in no_making and "commons_pool_equipment" not in no_making
