"""A self-test of the home safety, food state and accessibility parsers (packs/home_safety_packs.py and
training-kit/kit/home_safety_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - the category rules give the right questions and safety notes, and two different answers to a one-state question
    (two ripeness or doneness categories) give no answer (never a guess);
  - an alarm's light, a meter's reading, a display's setting, a breaker's position, an extinguisher's gauge and a
    thermometer's temperature are read only from plain words with their unit, never from words that give two states
    or no unit;
  - a file of a category another pack already shows is kept only when this pack adds a new question;
  - USDA captions that are not about food safety are left out;
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflow's known list and limit lines, in the
    kit's sources, and the accessibility pack never for picture-making.

Run it from the repository's folder:   python3 -m pytest packs/test_home_safety.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import home_safety_packs as d  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"
REPO = os.path.dirname(HERE)


def test_rule_rows():
    """Category names give their questions, with safety notes; two states give nothing."""
    rows = d.rule_rows(["Distribution boards in Germany"])
    assert rows[0]["question"] == d.WHAT_Q and "electrical panel" in rows[0]["answer"]
    assert "electrician" in rows[0]["answer"]
    assert "rotten eggs" in d.rule_rows(["Gas meters"])[0]["answer"]
    assert "fresh air" in d.rule_rows(["Carbon monoxide detectors"])[0]["answer"]
    assert d.rule_rows(["Green bananas"])[0]["answer"].startswith("No: these bananas are green")
    mould = d.rule_rows(["Mouldy bread"])
    assert mould[0]["question"] == d.SAFE_Q and "Do not smell it" in mould[0]["answer"]
    assert "blue cheese" in d.rule_rows(["Moldy cheese"])[0]["answer"]
    # two doneness categories: no doneness answer
    assert not [r for r in d.rule_rows(["Rare steaks", "Well-done steaks"]) if r["question"] == d.DONE_Q]
    kinds = d.rule_rows(["Carbon dioxide fire extinguishers"], prefer=d.KIND_Q)
    assert kinds[0]["question"] == d.KIND_Q and "CO2" in kinds[0]["answer"]
    assert d.rule_rows(["Braille signage"])[0]["question"] == d.BRAILLE_Q
    assert d.rule_rows(["Bus stop signs in Ohio"])[0]["question"] == d.SIGN_Q
    assert d.rule_rows(["Fire extinguisher signs"]) == []
    assert d.rule_rows(["Kitchens"]) == []


def test_alarm_light_never_guessed():
    """A light's colour only from plain words; two colours give nothing."""
    assert "a blinking red light" in d.alarm_light("Smoke detector with the LED blinking red")
    assert "a steady green light" in d.alarm_light("CO alarm, steady green light")
    assert "a green light" in d.alarm_light("The green light is on")
    assert "check the label" in d.alarm_light("The green light is on")
    assert d.alarm_light("Red and green LEDs; the green light is on and the red light flashing") == ""
    assert d.alarm_light("A smoke detector on a white ceiling") == ""


def test_meter_reading_needs_a_unit():
    """A reading only with its unit; two readings or a bare number give nothing."""
    assert d.meter_reading("Electricity meter reading 04512 kWh") == \
        "The photo's own description gives the reading as 04512 kWh."
    assert "cubic metres" in d.meter_reading("The gas meter shows 1234.5 m3")
    assert d.meter_reading("Gas meter number 778812") == ""
    assert d.meter_reading("reads 100 kWh, later reads 200 kWh") == ""


def test_display_reading():
    """A setting or reading only with its unit or in quotes."""
    assert d.display_reading("Thermostat set to 72 degrees") == "The photo's own description says it shows 72 degrees."
    assert "12:45" in d.display_reading("Microwave display showing 12:45")
    assert "Normal" in d.display_reading("Washer dial is on 'Normal'")
    assert d.display_reading("A Honeywell thermostat model 8000") == ""
    assert d.display_reading("set to 68 degrees by day and set to 60 degrees at night") == ""


def test_breaker_and_gauge():
    """A breaker's position and a gauge's needle only where the words say them."""
    assert "tripped" in d.breaker_state("Panel with a tripped breaker")
    assert "switched off" in d.breaker_state("The breaker is switched off for the work")
    assert d.breaker_state("Breaker panel in a basement") == ""
    assert d.breaker_state("one breaker is off and the main breaker is on") == ""
    assert "charged" in d.gauge_state("Extinguisher with the gauge needle in the green")
    assert "recharged" in d.gauge_state("pressure gauge pointing to recharge")
    assert d.gauge_state("Fire extinguisher, red, 5 kg") == ""


def test_food_temperature():
    """A thermometer's temperature only where one is named with a thermometer word."""
    t = d.food_temperature("A food thermometer reads 165 °F in the chicken breast")
    assert t.startswith("The photo's own description gives the temperature as 165 F") and "USDA" in t
    assert d.food_temperature("Roast chicken at 165 °F") == ""                     # no thermometer word
    assert d.food_temperature("Safe temperatures: 145 °F for steaks, 165 °F for poultry, thermometer") == ""


def test_state_only_topics():
    """A category another pack shows: kept only with a new question; a new category keeps its rows."""
    t = d.topic("Smoke detectors", 2, d.LIGHT_Q, True, ("light",))
    assert d.file_rows("File:Smoke detector.jpg", CREDIT, "", "", "Smoke detectors", [], t) == []
    rows = d.file_rows("File:Smoke detector LED blinking red.jpg", CREDIT, "", "", "Smoke detectors", [], t)
    assert rows[0]["question"] == d.WHAT_Q and rows[1]["question"] == d.LIGHT_Q
    new = d.topic("Gas meters", 1, d.WHAT_Q, readers=("meter",))
    rows = d.file_rows("File:Gas meter.jpg", CREDIT, "A gas meter on the side of a house in Ohio.", "",
                       "Gas meters in the United States", [], new)
    assert [r["question"] for r in rows] == [d.WHAT_Q, d.DESCRIBE_Q]
    assert rows[0]["place"] == "USA" and rows[0]["facts"]["commons_category"] == "Gas meters in the United States"
    lift = d.topic("Elevator buttons", 1, d.BRAILLE_Q, True, ("braille",))
    assert d.file_rows("File:Lift.jpg", CREDIT, "", "", "Elevator buttons", [], lift) == []
    rows = d.file_rows("File:Lift buttons with braille.jpg", CREDIT, "", "", "Elevator buttons", [], lift)
    assert any(r["question"] == d.BRAILLE_Q for r in rows)
    assert d.file_rows("File:Lift.jpg", CREDIT, "", "Buttons without braille", "Elevator buttons", [], lift) == []


def test_harm_words():
    """Fire, injury and death words leave a file out."""
    assert d.HARM.search("House fire damage after the smoke alarm failed")
    assert d.HARM.search("Man electrocuted at a fuse box")
    assert not d.HARM.search("Fire extinguisher in a hallway")


def test_usda_rows():
    """Food safety captions only; the temperature where it is stated."""
    rows = d.usda_rows("A food thermometer reads 165 °F inside a turkey breast at a cooking class.", CREDIT)
    assert [r["question"] for r in rows] == [d.TEMP_Q, d.DESCRIBE_Q]
    assert d.usda_rows("Secretary Vilsack speaks about food safety at a press conference.", CREDIT) == []
    assert d.usda_rows("Farmers harvest corn in Iowa on a sunny day in July.", CREDIT) == []


def test_wiring():
    """Every pack is in PACKS and COMMONS_KEYS, the workflows know them, the kit lists them, the accessibility pack
    is never used for picture-making, and the kit's share-alike entry is there."""
    keys = set(d.HOME_SAFETY_PACKS)
    assert keys <= set(build_packs.PACKS)
    assert keys <= build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in d.HOME_SAFETY_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import home_safety_sources") == 2
    import sources
    import home_safety_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed) and "home_safety_commons_sa" in listed
    assert all(listed[key].group == "permissive" for key in keys)
    assert listed["home_safety_commons_sa"].group == "share-alike"
    assert "commons_access_features" in sources.PEOPLE_AND_BODILY_PACK_KEYS
    assert {"commons_access_features", "home_safety_commons_sa"} <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert k.HOME_SAFETY_PICTURE_MAKING_OK == set()
