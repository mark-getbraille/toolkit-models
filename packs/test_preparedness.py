"""A self-test of the emergency preparedness and disaster packs (packs/preparedness_packs.py) and the kit's collections
for them (training-kit/kit/preparedness_sources.py), with made-up labels and records only: nothing is downloaded.

It checks that:
  - every generator and fuel answer ends with the generator note (outdoors only, 20 feet, carbon monoxide, get out and
    call 911, never back-feed: a transfer switch by a licensed electrician), every flood answer carries "turn around,
    don't drown", potassium iodide says "only when officials tell you", ice storms and wind damage carry the power line
    note, the shelters the shelter note, and the safety words are the same in the packs, the kit and the books;
  - every Commons category leaves out files whose own words speak of the dead, bodies, casualties, the injured or
    blood, and the word filters keep what they should (storm shutters, not decorative ones; wildfire haze, not city
    haze);
  - no answer states a number of its own beyond the fixed notes' (20 feet, a gallon, 911 and the helplines);
  - Open Images rows say only what the labels say, and no label of these packs is asked by another pack, nor twice;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive" with prepare_pack, the same cap), never for
    picture-making unless the kit module says so, in the topics the kit module names, and the kit module listed twice
    as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_preparedness.py
"""

import glob
import importlib
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(REPO, "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import preparedness_packs as p  # noqa: E402


def answer_of(category):
    """The first answer of a category's Commons spec."""
    return next(spec[2][0][1] for spec in p.PREPAREDNESS_SPECS if spec[0] == category)


def must_of(category):
    """The word pattern of a category's Commons spec."""
    return next(spec[3] for spec in p.PREPAREDNESS_SPECS if spec[0] == category)


def oi_rows(labels, groups):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1))


# ----------------------------------------------------------------- safety notes

def test_safety_notes():
    for words in ("outdoors", "20 feet", "carbon monoxide", "911", "wall socket", "back-feeding", "transfer switch",
                  "licensed electrician"):
        assert words in p.GENERATOR_NOTE, words
    for category in ("Mobile engine-generators", "Emergency power system"):
        assert answer_of(category).endswith(p.GENERATOR_NOTE), category
    assert p.GENERATOR_NOTE in answer_of("Fuel containers")
    assert "turn around, don't drown" in p.FLOOD_NOTE and "local officials" in p.FLOOD_NOTE
    for category in ("Floodgates", "Levees", "Stilt houses", "Flash floods", "Hurricane preparations"):
        assert p.FLOOD_NOTE in answer_of(category), category
    assert p.KI_NOTE in answer_of("Potassium iodide") and "only when" in p.KI_NOTE
    for category in ("Ice storms", "Wind damage", "Derechos"):
        assert p.POWER_LINE_NOTE in answer_of(category), category
    for category in ("Tornado shelters", "Storm cellars", "Safe rooms", "Warning sirens"):
        assert answer_of(category).endswith(p.SHELTER_NOTE), category
    assert p.SMOKE_NOTE in answer_of("Haze") and "N95" in p.SMOKE_NOTE
    assert p.MASK_NOTE in answer_of("Particulate respirators") and "carbon monoxide" in p.MASK_NOTE
    for words in ("local officials", "20 feet", "carbon monoxide", "911", "turn around, don't drown",
                  "downed power lines"):
        assert words in p.SAFETY_NOTE, words


def test_notes_match_books_and_kit():
    import sources  # noqa: F401 - loaded first: it loads preparedness_sources at its end
    import preparedness_sources as k
    sys.path.insert(2, os.path.join(REPO, "textbooks"))
    import disaster_ready as books
    assert p.SAFETY_NOTE == books.SAFETY_NOTE == k.SAFETY_NOTE
    assert (k.GENERATOR_NOTE, k.KIT_NOTE, k.SHELTER_NOTE) == (p.GENERATOR_NOTE, p.KIT_NOTE, p.SHELTER_NOTE)
    pack_categories = {spec[0] for spec in p.PREPAREDNESS_SPECS}
    for category, _q, answer, _d in k.PREPAREDNESS_SA:
        assert category in pack_categories, category
    gen = next(a for c, _q, a, _d in k.PREPAREDNESS_SA if c == "Mobile engine-generators")
    assert gen.endswith(k.GENERATOR_NOTE)


def test_no_harm_and_word_filters():
    for spec in p.PREPAREDNESS_SPECS:
        pattern = spec[3]
        for words in ("Dead bodies after the tsunami", "Injured man carried from rubble", "Casualties of the flood",
                      "Blood on the floor of the shelter", "Victims of the earthquake"):
            assert not pattern.search(words), (spec[0], words)
    assert must_of("Volcanic eruptions").search("Eruption of Kilauea, 2018, seen from the air")
    shutters = must_of("Shutters")
    assert shutters.search("Hurricane shutters on a house in Florida")
    assert not shutters.search("Green wooden shutters on a farmhouse in Provence")
    haze = must_of("Haze")
    assert haze.search("Wildfire smoke haze over Seattle")
    assert not haze.search("Morning haze over the hills")


def test_no_numbers_made_up():
    """No answer states a number of its own: only the fixed notes' numbers (20 feet, a gallon per person, 911, the
    helplines, 1-800 numbers, the N95 mask's name) and the category's own words."""
    allowed = re.compile(r"20 feet|911|1-800-\d{3}-\d{4}|N95")
    for spec in p.PREPAREDNESS_SPECS:
        for _q, answer in spec[2]:
            assert not re.search(r"\d", allowed.sub("", answer)), answer


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in oi_rows({"Flood": 1, "Electric generator": 1, "Tornado": 0},
                                                        p.DISASTERS_OI)}
    assert said["What kind of disaster or severe weather is in this picture?"] == f"I can see a flood. {p.SAFETY_NOTE}"
    assert said["Is there a generator in this picture?"] == f"I can see an electric generator. {p.GENERATOR_NOTE}"


# ----------------------------------------------------------------- shared checks

def asked_elsewhere(ours):
    """Every Open Images label another pack file asks about (every *_packs.py file but ours)."""
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


def test_no_open_images_label_is_asked_twice():
    elsewhere = asked_elsewhere({"preparedness_packs"})
    assert not g.gap_labels(p.DISASTERS_OI) & elsewhere, g.gap_labels(p.DISASTERS_OI) & elsewhere
    for grp in p.DISASTERS_OI:
        assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())


def test_no_commons_category_is_used_by_another_pack():
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.basename(path) != "preparedness_packs.py" and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    seen = set()
    for spec in p.PREPAREDNESS_SPECS:
        assert spec[0] not in seen, spec[0]
        seen.add(spec[0])
        assert f'"{spec[0]}"' not in others, f"{spec[0]} is used by another pack"


def check_wiring(module_name, packs, limits, commons_keys, kit_name, kit_sources, picture_ok, kit_topics):
    """The wiring checks shared by the preparedness and radio self-tests."""
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    assert kit_yml.count(f"--hidden-import {kit_name} ") == 2, kit_name
    import sources
    import topics
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    keys = set(packs)
    assert keys == set(limits) and keys <= set(build_packs.PACKS)
    assert set(commons_keys) <= keys and set(commons_keys) <= build_packs.COMMONS_KEYS
    assert not (keys - set(commons_keys)) & build_packs.COMMONS_KEYS
    for key, limit in limits.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert listed[key].cap == limit, key
        assert (key in no_making) == (key not in picture_ok), key
    kit_keys = {s.key for s in kit_sources}
    assert keys <= kit_keys
    for s in kit_sources:
        assert s.key in listed and (s.group == "permissive") == (s.key in keys), s.key
    in_topics = set()
    for topic_id, tkeys in kit_topics.items():
        topic = topics.find(topic_id)
        assert set(tkeys) <= set(topic.keys), (topic_id, set(tkeys) - set(topic.keys))
        in_topics |= set(tkeys)
    assert kit_keys == in_topics
    for topic in topics.TOPICS:
        assert {k for k in topic.keys if k in kit_keys} <= set(kit_topics.get(topic.id, ())), topic.id
        assert len(topic.description) < 300


def test_wiring():
    import sources  # noqa: F401
    import preparedness_sources as k
    check_wiring("preparedness_packs", p.PREPAREDNESS_PACKS, p.PREPAREDNESS_LIMITS, p.PREPAREDNESS_COMMONS_KEYS,
                 "preparedness_sources", k.PREPAREDNESS_SOURCES, k.PREPAREDNESS_PICTURE_MAKING_OK,
                 k.PREPAREDNESS_TOPICS)
    import sources as s
    no_making = set(s.NOT_FOR_PICTURE_MAKING)
    assert {"commons_disaster_types", "commons_warnings_shelters", "open_images_disasters"} <= no_making
    assert "commons_emergency_signs_maps" not in no_making
    assert {"home", "nature", "documents"} == set(k.PREPAREDNESS_TOPICS)
    assert "Pictures of injured or dead people" in k.PREPAREDNESS_NOT_INCLUDED
