"""A self-test of the emergency cooking, camp cooking, and grills and smokers packs (packs/outdoor_cooking_packs.py)
and the kit's collections (training-kit/kit/outdoor_cooking_sources.py), with made-up labels only: nothing is
downloaded from the internet.

It checks that:
  - every answer about a stove, grill, smoker, fire, fuel, food or water carries its safety notes (carbon monoxide,
    fire, propane leak test, hot surfaces, USDA temperatures, safe water), in the packs and the kit alike, with the
    same words;
  - the notes say what the owner asked: grills, camp stoves, charcoal and generators never indoors, get out and call
    911, soapy water and no flame, the USDA temperatures;
  - Open Images rows say only what the labels say, and no label of this pack is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in the home or food topic, and the guarded kit module listed twice as a hidden
    import.

Run it from the repository's folder:   python3 -m pytest packs/test_outdoor_cooking.py
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
import outdoor_cooking_packs as o  # noqa: E402

REPO = os.path.dirname(HERE)
STOVE_WORDS = re.compile(r"stove|grill|kamado|smokehouse|barbecue|campfire|charcoal|sterno|chimney starter|"
                         r"Campingaz|Coleman|Trangia|Esbit|storm kettle|Primus|Optimus|Svea", re.I)


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    assert "never use grills, camp stoves, charcoal or generators indoors" in o.CO_NOTE
    assert "call 911" in o.CO_NOTE and "CO alarm" in o.CO_NOTE
    assert "soapy water" in o.PROPANE_NOTE and "never with a flame" in o.PROPANE_NOTE
    for words in ("145 F", "160 F", "165 F", "3-minute rest", "food thermometer"):
        assert words in o.TEMP_NOTE
    assert "drown" in o.CAMPFIRE_NOTE and "restrictions" in o.CAMPFIRE_NOTE
    assert "1 minute" in o.WATER_NOTE and "when in doubt, throw it out" in o.OUTAGE_NOTE


def test_every_answer_carries_its_notes():
    for category, answer in answers(o.OUTDOOR_COOKING_SPECS):
        assert answer.startswith(("This is ", "It shows ")) and answer.endswith("."), category
        if answer.startswith("This is ") and STOVE_WORDS.search(category + " " + answer.split(".")[0]):
            assert o.CO_NOTE in answer or o.CAMPFIRE_NOTE in answer or o.FIRE_NOTE in answer, category
        if re.search(r"propane|LPG|gas cartridge", answer.split(". ")[0], re.I):
            assert o.PROPANE_NOTE in answer, category
        if re.search(r"canteen|water filter|purif|water barrel|LifeStraw", category + answer.split(".")[0], re.I):
            assert o.WATER_NOTE in answer, category
    for category, answer in answers(o.BARBECUE_FOOD):
        assert o.TEMP_NOTE in answer, category
    for category, answer in answers(o.GRILLS_SMOKERS):
        assert o.HOT_NOTE in answer or o.PROPANE_NOTE in answer, category
    # no brand or temperature is made up: only the category's own names, the notes and the USDA figures
    for _category, answer in answers(o.OUTDOOR_COOKING_SPECS):
        rest = answer
        for note in (o.CO_NOTE, o.FIRE_NOTE, o.CAMPFIRE_NOTE, o.PROPANE_NOTE, o.HOT_NOTE, o.TEMP_NOTE, o.WATER_NOTE):
            rest = rest.replace(note, "")
        assert not re.search(r"\d+\s*(°|degrees)", rest), answer


def test_word_filters():
    canteens = next(s for s in o.CAMP_COOKING if s[0] == "Canteens")
    assert canteens[3].search("US Army M1910 canteen") and not canteens[3].search("Staff restaurant, Hamburg")
    kamado = next(s for s in o.GRILLS_SMOKERS if s[0] == "Kamado")
    assert kamado[3].search("Kamado Joe grill on a patio") and not kamado[3].search("Kamado-M1685.jpg the stove in a "
                                                                                   "traditional kitchen of Japan")
    coolers = next(s for s in o.CAMP_COOKING if s[0] == "Coolers")
    assert coolers[3].search("Igloo cooler at a picnic") and not coolers[3].search("Evaporative air conditioner")


def rows_of(labels):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, o.OUTDOOR_OI, random.Random(1))


def test_open_images_rows():
    rows = rows_of({"Grilling": 1, "Campfire": 0})
    said = {r["question"]: r["answer"] for r in rows}
    assert said["Is someone grilling in this picture?"] == f"I can see grilling, cooking food on a grill. " \
                                                           f"{o.GRILL_NOTES}"
    assert said["Is there a campfire in this picture?"] == "No, I can't see a campfire in this picture."
    rows = rows_of({"Brisket": 1, "Cooler": 1})
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What grilled or smoked foods are in this picture?"] == f"I can see brisket. {o.TEMP_NOTE}"
    assert said["What camp kitchen things are in this picture?"] == "I can see a cooler."
    assert rows_of({"Grilling": 1, "Nudity": 1}) == []
    entries = [("a.jpg", b"x", {"question": "Is there a lighter in this picture?",
                                 "answer": "Yes, there is a lighter in this picture."}),
               (None, None, {"question": "Are there any marshmallows in this picture?",
                             "answer": "Yes, there are marshmallows in this picture."}),
               (None, None, {"question": "Is there a cooler in this picture?",
                             "answer": "Yes, there is a cooler in this picture."})]
    got = [row["answer"] for _n, _d, row in o.with_yes_notes(entries)]
    assert got[0].endswith(o.FIRE_NOTE) and o.CO_NOTE in got[0] and got[1].endswith(o.CAMPFIRE_NOTE)
    assert got[2] == "Yes, there is a cooler in this picture."
    assert all(r.get("child") for r in rows_of({"Marshmallow": 1, "Boy": 1}))


def asked_elsewhere():
    """Every Open Images label another pack file asks about (the same reading as packs/test_daily_access.py)."""
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name == o.__name__:
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
    mine = g.gap_labels(o.OUTDOOR_OI)
    assert not mine & asked_elsewhere(), mine & asked_elsewhere()
    for grp in o.OUTDOOR_OI:
        assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())
    labels = [label for grp in o.OUTDOOR_OI for label in grp["things"]]
    assert len(labels) == len(set(labels))


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(o.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in o.OUTDOOR_COOKING_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads outdoor_cooking_sources at its end
    import outdoor_cooking_sources as k
    for name in ("CO_NOTE", "FIRE_NOTE", "CAMPFIRE_NOTE", "PROPANE_NOTE", "HOT_NOTE", "TEMP_NOTE", "WATER_NOTE"):
        assert getattr(k, name) == getattr(o, name), name
    pack_categories = {spec[0] for spec in o.OUTDOOR_COOKING_SPECS}
    for category, _q, answer, _deeper in k.OUTDOOR_COOKING_SA:
        assert category in pack_categories, category
        if STOVE_WORDS.search(category):
            assert k.CO_NOTE in answer or k.CAMPFIRE_NOTE in answer or k.FIRE_NOTE in answer, category
    assert next(a for c, _q, a, _d in k.OUTDOOR_COOKING_SA if c.startswith("Liquefied")).endswith(k.PROPANE_NOTE)
    assert all(reason for reason in k.OUTDOOR_COOKING_NOT_INCLUDED.values())


def test_wiring():
    keys = set(o.OUTDOOR_COOKING_PACKS)
    assert keys == set(o.OUTDOOR_COOKING_LIMITS) and len(keys) == 5
    assert keys <= set(build_packs.PACKS)
    assert set(o.OUTDOOR_COOKING_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(o.OUTDOOR_COOKING_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in o.OUTDOOR_COOKING_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import outdoor_cooking_sources") == 2
    import sources
    import topics
    import outdoor_cooking_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    # The gear in the home topic (Home and household) and the barbecue food in the food topic.
    topic = set(topics.find("home").keys) | set(topics.find("food").keys)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert key in topic, key
        assert (key in no_making) == (key not in k.OUTDOOR_COOKING_PICTURE_MAKING_OK), key
    for s in k.OUTDOOR_COOKING_SOURCES:
        assert s.key in listed and s.key in topic, s.key
        assert s.key in keys or s.group != "permissive", s.key
    assert listed["outdoor_cooking_commons_sa"].group == "share-alike"
    assert "open_images_outdoor_cooking" in no_making and "commons_barbecue_food" in no_making
    assert "commons_grills_smokers" not in no_making
    assert "commons_barbecue_food" in topics.find("food").keys and "commons_grills_smokers" in topics.find("home").keys
