"""A self-test of the car care packs (packs/car_care_packs.py) and the kit's car care collections (training-kit/kit/
car_care_sources.py), with made-up file words and labels only: nothing is downloaded from the internet.

It checks that:
  - a dashboard light's meaning is said only when its file's own words name one light (none for a file naming two
    different lights, or none), its colour only when the words give one colour, and files of the ISO 7000 pack are
    left out;
  - jacks, hot fluids, batteries, breakdowns and charging plugs carry their safety notes (the same words in the kit);
  - Open Images rows say only what the labels say; no label or Commons category is asked by another pack;
  - the packs are wired (build_packs, the workflows, the kit's sources, topics and picture-making rules).

Run it from the repository's folder:   python3 -m pytest packs/test_car_care.py
"""

import random

import life_skills_checks as L
import car_care_packs as c
import gaps_oi_packs as g


def test_dashboard_light_meanings_only_from_the_words():
    rows = c.light_rows("File:Car tire pressure warning light.svg", "", "credit")
    assert rows[0]["answer"].startswith("This is the tyre pressure warning light") and len(rows) == 1
    rows = c.light_rows("File:Oil pressure telltale red.png", "Red oil pressure warning lamp on a car dashboard.", "c")
    assert "oil pressure" in rows[0]["answer"] and "Its file says it is red" in rows[0]["answer"]
    assert rows[1]["question"] == c.ALT_TEXT
    assert c.light_rows("File:Dashboard warning light.jpg", "A car dashboard at night.", "c") == []
    assert c.light_rows("File:Car ABS and airbag warning lights.jpg", "", "c") == []      # two lights: no meaning
    assert c.light_rows("File:Tire pressure warning light.svg", "", "c") == []           # no road vehicle named
    assert c.light_rows("File:Brake warning light.jpg", "Brake warning light in an aircraft cockpit.", "c") == []
    assert c.light_rows("File:ISO 7000 - 0248 oil pressure warning light.svg", "", "c") == []
    assert "flashes" in c.light_meaning("check engine light")
    assert c.light_meaning("malfunction indicator lamp").startswith("the check-engine light")
    assert c.light_meaning("EV turtle mode light").startswith("the reduced power")
    assert c.light_meaning("already parked") == ""
    assert c.light_colour("amber or orange light") == "amber" and c.light_colour("red and green lights") == ""
    assert c.light_meaning("hazard warning light and turn signal").startswith("the turn signal")


def test_safety_notes():
    answers = {spec[0]: spec[2][0][1] for spec in c.CAR_CARE + c.EV_CHARGING}
    for category in ("Scissor jacks", "Lug wrenches", "Spare tires"):
        assert answers[category].endswith(c.JACK_NOTE), category
    assert answers["Vehicle breakdowns"].endswith(c.ROADSIDE_NOTE) and answers["Tow trucks"].endswith(c.ROADSIDE_NOTE)
    assert all(a.endswith(c.CHARGING_NOTE) for k, a in answers.items() if k in {s[0] for s in c.EV_CHARGING})
    assert "jack stands" in c.JACK_NOTE and "911" in c.ROADSIDE_NOTE and "acid" in c.BATTERY_NOTE
    import car_care_sources as k
    assert (k.JACK_NOTE, k.HOT_NOTE, k.BATTERY_NOTE, k.ROADSIDE_NOTE, k.CHARGING_NOTE) == (
        c.JACK_NOTE, c.HOT_NOTE, c.BATTERY_NOTE, c.ROADSIDE_NOTE, c.CHARGING_NOTE)


def test_open_images_rows():
    rows = g.oi_gap_rows({"Tire": 1, "Hubcap": 1, "Tow truck": 0}, c.CAR_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What car parts or car care things are in this picture?"] == "I can see a tyre and a hubcap."
    assert said["Is there a tow truck in this picture?"] == "No, I can't see a tow truck in this picture."


def test_nothing_asked_twice():
    L.check_open_images([c.CAR_OI], {"car_care_packs"})
    L.check_categories([c.CAR_CARE, c.EV_CHARGING], {"car_care_packs"})


def test_wiring():
    import car_care_sources as k
    L.check_wiring(c.CAR_CARE_PACKS, c.CAR_CARE_LIMITS, c.CAR_CARE_COMMONS_KEYS, "car_care_sources",
                   k.CAR_CARE_SOURCES, k.CAR_CARE_PICTURE_MAKING_OK)
    import topics
    assert set(c.CAR_CARE_PACKS) <= set(topics.find("machines").keys)


def test_connector_photos_name_a_plug():
    for spec in c.EV_CHARGING:
        if spec[2][0][0] == c.ASK_CONNECTOR:
            assert spec[3].search("CHAdeMO charging plug") and not spec[3].search("Tesla Model S at Geneva Motor "
                                                                                 "Show 2014"), spec[0]
