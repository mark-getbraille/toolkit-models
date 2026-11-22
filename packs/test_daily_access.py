"""A self-test of the everyday-access packs (packs/indoor_packs.py and the pack files listed in MODULES) and the kit's
everyday-access collections (training-kit/kit/daily_access_sources.py), with made-up labels and records only:
nothing is downloaded from the internet.

It checks that:
  - sign text is read only where a source labels it (a room number only from a "<number> (room number)" category);
  - Open Images rows say only what the labels say, and no label of these packs is asked by another pack, nor by two
    of these packs;
  - no Commons category of these packs is named by another pack file (so the same photos are not asked twice);
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive"), never for picture-making unless the kit
    module says so, in a topic, and the guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_daily_access.py
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
import indoor_packs as indoor  # noqa: E402
import appliance_controls_packs as appl  # noqa: E402
import health_test_packs as health  # noqa: E402
import medication_label_packs as med  # noqa: E402
import synthetic_bills_packs as bills  # noqa: E402

REPO = os.path.dirname(HERE)
# Each pack file of this group: (module, its packs, its limits, its Commons keys, its Commons specs, its Open Images
# groups).
MODULES = [
    (indoor, indoor.INDOOR_PACKS, indoor.INDOOR_LIMITS, indoor.INDOOR_COMMONS_KEYS, indoor.INDOOR_SPECS,
     [indoor.INDOOR_OI]),
    (appl, appl.APPLIANCE_CONTROLS_PACKS, appl.APPLIANCE_CONTROLS_LIMITS, appl.APPLIANCE_CONTROLS_COMMONS_KEYS,
     appl.CONTROL_SPECS, [appl.CONTROLS_OI]),
    (health, health.HEALTH_TEST_PACKS, health.HEALTH_TEST_LIMITS, health.HEALTH_TEST_COMMONS_KEYS,
     [(health.TEST_CATEGORY[0], False, [])], []),
    (med, med.MEDICATION_PACKS, med.MEDICATION_LIMITS, med.MEDICATION_COMMONS_KEYS, [], []),
    (bills, bills.SYNTHETIC_BILLS_PACKS, bills.SYNTHETIC_BILLS_LIMITS, bills.SYNTHETIC_BILLS_COMMONS_KEYS, [], []),
]


def oi_rows(labels, groups):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1))


# ----------------------------------------------------------------- indoor

def test_room_numbers_only_from_the_category():
    specs = indoor.room_number_specs(["Category:102 (room number)", "Category:12B (room number)",
                                      "Category:Room numbers in Germany", "Category:Room 5 doors"])
    assert [s[0] for s in specs] == ["102 (room number)", "12B (room number)"]
    assert specs[0][2] == [(indoor.ROOM_Q, "Room number 102 is shown here.")]
    assert specs[1][2][0][1] == "Room number 12B is shown here."


def test_indoor_answers():
    for category, _deeper, rows in indoor.INDOOR_SPECS:
        for question, answer in rows:
            assert question in (indoor.PLACE_Q, indoor.WHAT_Q, indoor.SIGN_Q), category
            assert answer.endswith(".") and answer[0].isupper(), category
            assert not re.search(r"\d", answer), category          # no number is read off a sign here
    toilet = {c: rows[0][1] for c, _d, rows in indoor.INDOOR_SPECS if "toilet signs" in c}
    assert "men's" in toilet["Men's toilet signs"] and "women's" in toilet["Women's toilet signs"]
    assert "all-gender" in toilet["Unisex toilet signs"]
    stairs = next(rows for c, _d, rows in indoor.INDOOR_SPECS if c == "Stairwells")
    assert stairs[0][1].endswith(indoor.STAIRS_NOTE)


def test_indoor_open_images_rows():
    rows = oi_rows({"Waiting room": 1, "Lobby": 1, "Revolving door": 0}, indoor.INDOOR_OI)
    said = {r["question"]: r["answer"] for r in rows}
    assert said[indoor.PLACE_Q] == "I can see a lobby and a waiting room."
    assert said["Is there a revolving door in this picture?"] == "No, I can't see a revolving door in this picture."
    rows = oi_rows({"Signage": 1}, indoor.INDOOR_OI)
    assert rows[0]["answer"] == "I can see signs. I can say that signs are there, not what they say."
    assert oi_rows({"Lobby": 1, "Nudity": 1}, indoor.INDOOR_OI) == []
    assert all(r.get("child") for r in oi_rows({"Lobby": 1, "Child": 1}, indoor.INDOOR_OI))


# ----------------------------------------------------------------- appliance controls

def test_appliance_settings_only_where_stated():
    alt = build_packs.ALT_TEXT
    entries = [("a.jpg", b"x", {"question": appl.WHAT_Q, "answer": "This is a rotary switch.", "credit": "c"}),
               (None, None, {"question": alt, "answer": "The oven dial is set to 180 °C.", "credit": "c",
                             "file": "pictures/a.jpg"}),
               ("b.jpg", b"y", {"question": appl.WHAT_Q, "answer": "This is a timer.", "credit": "c"}),
               (None, None, {"question": alt, "answer": "A kitchen timer on the counter.", "credit": "c",
                             "file": "pictures/b.jpg"}),
               ("c.jpg", b"z", {"question": appl.WHAT_Q, "answer": "This is a cooktop.", "credit": "c"}),
               (None, None, {"question": alt, "answer": "Set to 3, then set to 5 for boiling.", "credit": "c",
                             "file": "pictures/c.jpg"})]
    out = appl.with_settings(entries)
    added = [e for e in out if e[2]["question"] == appl.DISPLAY_Q]
    assert len(added) == 1 and added[0][2]["file"] == "pictures/a.jpg" and "180" in added[0][2]["answer"]
    assert all(e[2]["question"] != appl.DISPLAY_Q for e in out if e[2].get("file") != "pictures/a.jpg")


def test_appliance_specs():
    for spec in appl.CONTROL_SPECS:
        assert spec[2][0][1].endswith(appl.CONTROLS_NOTE) and not re.search(r"\d", spec[2][0][1])
    broad = {s[0]: s[3] for s in appl.CONTROL_SPECS if len(s) > 3}
    assert set(broad) == {"Rotary switches", "Control panels", "Push buttons", "Touchscreens", "Timers"}
    assert broad["Control panels"].search("Control panel of a Bosch washing machine")
    assert not broad["Control panels"].search("Elevator control panel in an office tower")
    rows = oi_rows({"Control knob": 1, "Led display": 1}, appl.CONTROLS_OI)
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What kind of display is in this picture?"].endswith("not what it shows.")
    assert not any(re.search(r"\d", r["answer"]) for r in rows)


# ----------------------------------------------------------------- synthetic bills

def test_synthetic_bills_are_made_up_and_exact():
    for n in range(16):
        d = bills.details(n)
        assert sum(c for _, c in d["lines"]) == d["amount"] > 0
        assert all(".example" in w or "555-01" in w or "stub" in w or "automatic" in w or "card" in w
                   for w in d["ways"])
        assert d["account"].startswith("****") and d["due"] > d["issued"]
    name, data, rows = bills.make_document(3)
    assert (name, data) == bills.make_document(3)[:2]
    assert all(r["synthetic"] for r in rows) and "made-up" in rows[0]["credit"]
    said = {r["question"]: r["answer"] for r in rows}
    d = bills.details(3)
    assert said[bills.KIND_Q].endswith("(a made-up company).")
    if d["kind"] not in ("bank", "pharmacy"):
        assert bills.money(d["amount"]) in said[bills.AMOUNT_Q] and bills.long_date(d["due"]) in said[bills.DUE_Q]
        assert said[bills.PAY_Q].startswith("The page says you can pay ")
    assert bills.money(128407) == "$1,284.07" and bills.page_part(1000, 100, 1240, 1754) == "near the top right"


# ----------------------------------------------------------------- medication labels

def test_medicine_name_and_strength_only_from_the_words():
    got = med.name_and_strength
    assert got("File:Ibuprofen 400 mg tablets.jpg") == ("ibuprofen", "400 mg", "tablets")
    assert got("File:Lantus 100 units/ml insulin pen.jpg") == ("Lantus (insulin glargine)", "100 units/ml",
                                                               "insulin pen")
    assert got("File:Ventolin inhaler 100mcg per dose.JPG") == ("Ventolin (salbutamol)", "100 mcg/dose", "inhaler")
    assert got("File:Timolol 0,5% eye drops.jpg") == ("timolol", "0.5%", "eye drops")
    assert got("File:Aspirin bottle.jpg") is None                         # no strength: no answer
    assert got("File:Paracetamol 500mg and ibuprofen 200mg.jpg") is None  # two medicines
    assert got("File:Amoxicillin 500 mg 250 mg.jpg") is None             # two strengths
    assert got("File:Lithium battery 2000 mAh.jpg") is None
    rows = med.medicine_rows("File:Metformin 850mg.jpg", "", "c")
    assert rows[0]["answer"] == ("This looks like metformin 850 mg, going by the photo's own title. "
                                 + med.PHARMACIST_NOTE)
    assert "pharmacist" in med.PHARMACIST_NOTE
    rows = med.medicine_rows("File:IMG_2041.jpg", "A box of Sertraline 50 mg tablets on a table.", "c")
    assert "going by the photo's own description" in rows[0]["answer"] and "sertraline 50 mg" in rows[0]["answer"]
    assert med.medicine_rows("File:Pills.jpg", "Some pills.", "c") == []


# ----------------------------------------------------------------- home health tests

def test_health_results_only_from_the_record():
    negative = health.lfa_result("0.0 ng")
    assert "no virus protein" in negative and "only the control line (C)" in negative
    assert negative.endswith(health.RESULT_NOTE)
    small = health.lfa_result("0.074 ng")
    assert "positive sample" in small and "may be very faint or not show" in small
    assert "may be very faint" not in health.lfa_result("7.4 ng") and health.lfa_result("Read me") == ""
    assert health.RESULT_NOTE == ("Faint lines can be hard to read; follow the test's own instructions, retest if "
                                  "unsure, and contact a doctor or pharmacist.")
    assert "positive" in health.test_result("Rapid antigen test, positive result")
    assert health.test_result("A rapid antigen test on a table.") == ""
    assert health.test_result("Positive control and negative sample side by side") == ""     # two results
    assert "negative" in health.test_result("Pregnancy test: not pregnant, one line")
    assert "invalid" in health.test_result("Invalid result: no control line")
    assert "112 mg/dL" in health.glucose_reading("The glucose meter reads 112 mg/dl.")
    assert health.glucose_reading("Readings of 98 mg/dL and 140 mg/dL") == ""
    rows = health.test_rows("a home pregnancy test", "File:Pregnancy test positive.jpg", "", "c")
    assert rows[1]["question"] == health.RESULT_Q and rows[1]["answer"].endswith(health.RESULT_NOTE)
    assert health.test_rows("a blood-glucose meter", "File:Glucose meter.jpg", "Blood on a finger.", "c") == []
    assert len(health.test_rows("a blood-glucose meter", "File:Glucose meter.jpg", "Blood glucose 6.2 mmol/L.",
                                "c")) == 3


# ----------------------------------------------------------------- shared checks

def asked_elsewhere():
    """Every Open Images label another pack file asks about: the keys of its OI_... dictionaries, the labels of its
    gaps_oi_packs-style groups, and home_packs' group questions (every *_packs.py file but those of MODULES)."""
    import importlib
    ours = {m[0].__name__ for m in MODULES}
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
    elsewhere = asked_elsewhere()
    mine = [groups for m in MODULES for groups in m[5]]
    for groups in mine:
        assert not g.gap_labels(groups) & elsewhere, g.gap_labels(groups) & elsewhere
        for grp in groups:
            assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())
    for i, a in enumerate(mine):
        for b in mine[i + 1:]:
            assert not g.gap_labels(a) & g.gap_labels(b)


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    ours = {os.path.abspath(m[0].__file__) for m in MODULES}
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) not in ours and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    seen = set()
    for m in MODULES:
        for spec in m[4]:
            category = spec[0]
            assert category not in seen, category
            seen.add(category)
            assert f'"{category}"' not in others, f"{category} is used by another pack"


def test_wiring():
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    assert kit_yml.count("--hidden-import daily_access_sources") == 2
    import sources
    import topics
    import daily_access_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    in_topics = {key for t in topics.TOPICS for key in t.keys}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    all_keys = set()
    for _mod, packs, limits, commons_keys, _specs, _groups in MODULES:
        keys = set(packs)
        assert keys == set(limits) and not keys & all_keys
        all_keys |= keys
        assert keys <= set(build_packs.PACKS)
        assert set(commons_keys) <= keys and set(commons_keys) <= build_packs.COMMONS_KEYS
        assert not (keys - set(commons_keys)) & build_packs.COMMONS_KEYS
        for key, limit in limits.items():
            assert f'"{key}"' in packs_yml, key
            assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
            assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
            assert key in in_topics, key
            assert (key in no_making) == (key not in k.DAILY_ACCESS_PICTURE_MAKING_OK), key
    for s in k.DAILY_ACCESS_SOURCES:
        assert s.key in listed
        assert s.group == "permissive" and s.key in all_keys or s.group != "permissive", s.key
        assert s.key in in_topics, s.key
    assert {"indoor_commons_sa"} <= set(listed) and listed["indoor_commons_sa"].group == "share-alike"
    assert set(indoor.INDOOR_PACKS) <= no_making
    assert "commons_appliance_controls" not in no_making and "open_images_appliance_controls" in no_making
    assert listed["appliance_commons_sa"].group == "share-alike"
    assert "commons_home_health_tests" in no_making and "lfa_covid_tests" not in no_making
    assert {"lfa_covid_tests", "commons_home_health_tests"} <= set(topics.find("medicines").keys)
    assert "commons_medication_labels" in no_making and "commons_medication_labels" in topics.find("medicines").keys
    assert "synthetic_bills" in no_making and "synthetic_bills" in topics.find("documents").keys
