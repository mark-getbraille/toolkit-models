"""A self-test of the power and electrical packs (packs/power_packs.py) and the kit's collections for them
(training-kit/kit/power_sources.py), with made-up labels only: nothing is downloaded from the internet.

It checks that:
  - the safety notes say what the owner asked: generators outdoors only, 20 feet from the house, get out and call 911
    if a CO alarm sounds; never back-feed (a transfer switch or interlock installed by a licensed electrician); DC
    arcs, roof falls and rapid shutdown; lithium fires and hydrogen; rotating blades, towers and lightning;
  - every answer about a generator, solar panel, battery, turbine or wire carries its notes, in the packs and the kit
    alike, with the same words, and no wattage, voltage or brand is made up;
  - Open Images rows say only what the labels say, and no label of this pack is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in exactly the topics the kit module names (the new "power" topic right after
    "home"), the existing electrical collections in the power topic too, and the guarded kit module listed twice as a
    hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_power.py
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
import power_packs as p  # noqa: E402

REPO = os.path.dirname(HERE)
GEN = re.compile(r"^(Electrical generators|Generac|16 CFR)")
SOLAR = re.compile(r"solar|photovoltaic|MC4|charge controller", re.I)
BATTERY = re.compile(r"batter|Powerwall", re.I)
TURBINE = re.compile(r"turbine|wheel|windmill|wind pump|penstock|hydro", re.I)
NOTE_NAMES = ("GENERATOR_NOTE", "BACKFEED_NOTE", "FUEL_NOTE", "DIY_NOTE", "SOLAR_NOTE", "BATTERY_NOTE",
              "TURBINE_NOTE", "WIRING_NOTE", "LINE_NOTE")


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    for words in ("only outdoors", "20 feet", "carbon monoxide alarm", "call 911", "garage"):
        assert words in p.GENERATOR_NOTE, words
    for words in ("dryer outlet", "line workers", "transfer switch", "interlock", "licensed electrician"):
        assert words in p.BACKFEED_NOTE, words
    for words in ("arc", "disconnects", "fall protection", "licensed electrician", "rapid shutdown"):
        assert words in p.SOLAR_NOTE, words
    for words in ("thermal runaway", "hydrogen", "Fuse every", "swollen"):
        assert words in p.BATTERY_NOTE, words
    for words in ("brake", "fall protection", "lightning"):
        assert words in p.TURBINE_NOTE, words
    assert "never connect it to house wiring" in p.DIY_NOTE and "rotating parts" in p.DIY_NOTE
    assert "10 feet" in p.LINE_NOTE and "911" in p.LINE_NOTE and "tester" in p.WIRING_NOTE


def test_every_answer_carries_its_notes():
    for category, answer in answers(p.POWER_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
        if GEN.search(category):
            assert p.GENERATOR_NOTE in answer and p.BACKFEED_NOTE in answer, category
        if SOLAR.search(category):
            assert p.SOLAR_NOTE in answer, category
        if BATTERY.search(category):
            assert p.BATTERY_NOTE in answer, category
        if TURBINE.search(category):
            assert p.TURBINE_NOTE in answer, category
        if "dynamo" in category.lower() and "Bicycle" not in category:
            assert p.DIY_NOTE in answer, category
    # nothing made up: no watts, volts or amps outside the notes
    for _category, answer in answers(p.POWER_SPECS):
        rest = answer
        for note in p.NOTES:
            rest = rest.replace(note, "")
        assert not re.search(r"\d+\s*(W|kW|V|A|Ah|watts?|volts?|amps?)\b", rest), answer


def test_generator_word_filter():
    gens = next(s for s in p.GENERATORS if s[0] == "Electrical generators")
    assert gens[3].search("Honda EU2200i portable generator at a campsite")
    assert gens[3].search("Diesel generator set behind a farm shed")
    assert not gens[3].search("Turbo generator in the Itaipu power plant")


def rows_of(labels):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, p.POWER_OI, random.Random(1))


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in rows_of({"Solar panel": 1, "Wind turbine": 0})}
    assert said["What solar power things are in this picture?"] == f"I can see a solar panel. {p.SOLAR_NOTE}"
    assert said["Is there a wind turbine in this picture?"] == "No, I can't see a wind turbine in this picture."
    said = {r["question"]: r["answer"] for r in rows_of({"Lineman": 1, "Gasoline": 1})}
    assert said["What power line things are in this picture?"] == \
        f"I can see a line worker (lineman). {p.LINE_NOTE} {p.BACKFEED_NOTE}"
    assert said["What fuel is in this picture?"] == f"I can see gasoline (petrol). {p.FUEL_NOTE}"
    assert rows_of({"Solar panel": 1, "Nudity": 1}) == []
    entries = [("a.jpg", b"x", {"question": "Is there a car battery in this picture?",
                                 "answer": "Yes, there is a car battery in this picture."}),
               (None, None, {"question": "Is there a wall socket in this picture?",
                             "answer": "Yes, there is a wall socket in this picture."})]
    got = [row["answer"] for _n, _d, row in p.with_yes_notes(entries, p.POWER_OI)]
    assert got[0].endswith(p.BATTERY_NOTE) and got[1].endswith(p.WIRING_NOTE)


def test_no_open_images_label_is_asked_twice():
    mine = g.gap_labels(p.POWER_OI)
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name == p.__name__:
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
    assert not mine & elsewhere, mine & elsewhere
    labels = [label for grp in p.POWER_OI for label in grp["things"]]
    assert len(labels) == len(set(labels))
    assert "Electric generator" not in mine and "Uninterruptible power supply" not in mine


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(p.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in p.POWER_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads power_sources at its end
    import power_sources as k
    for name in NOTE_NAMES:
        assert getattr(k, name) == getattr(p, name), name
    pack_specs = {spec[0]: spec for spec in p.POWER_SPECS}
    for category, _q, answer, deeper in k.POWER_SA:
        assert category in pack_specs and len(pack_specs[category]) == 3, category     # no word filter
        assert answer == pack_specs[category][2][0][1] and deeper == pack_specs[category][1], category
    assert all(reason for reason in k.POWER_NOT_INCLUDED.values())


def test_wiring():
    keys = set(p.POWER_PACKS)
    assert keys == set(p.POWER_LIMITS) and len(keys) == 4
    assert keys <= set(build_packs.PACKS)
    assert set(p.POWER_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(p.POWER_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in p.POWER_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import power_sources") == 2
    import sources
    import topics
    import power_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
    assert listed["power_commons_sa"].group == "share-alike"
    for s in k.POWER_SOURCES:
        assert s.key in listed, s.key
        assert (s.key in no_making) == (s.key not in k.POWER_PICTURE_MAKING_OK), s.key
    assert "open_images_power" in no_making
    # the topics: exactly as the kit module says
    mine = {s.key for s in k.POWER_SOURCES}
    in_topics = set()
    for topic_id, tkeys in k.POWER_TOPICS.items():
        assert set(tkeys) <= set(topics.find(topic_id).keys), topic_id
        in_topics |= set(tkeys)
    assert in_topics == mine
    for topic in topics.TOPICS:
        assert {key for key in topic.keys if key in mine} <= set(k.POWER_TOPICS.get(topic.id, ())), topic.id
    # the power topic: right after home, with the existing electrical collections too
    ids = [t.id for t in topics.TOPICS]
    assert ids[ids.index("home") + 1] == "power"
    power = topics.find("power")
    assert power.title == "Power and electrical" and len(power.description) < 300
    assert set(k.POWER_TOPIC_EXISTING) <= set(power.keys) and set(power.keys) == mine | set(k.POWER_TOPIC_EXISTING)
    for key in k.POWER_TOPIC_EXISTING:
        assert key in listed, key
