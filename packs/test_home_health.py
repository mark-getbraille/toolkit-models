"""A self-test of the home health packs (packs/home_health_packs.py) and the kit's home health collections
(training-kit/kit/home_health_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - every Commons and Open Images answer ends with one of the four notes (emergency, dental, eye, birth), the same
    words in the kit;
  - SCIN answers say only what the dermatologists named, never as a diagnosis, leave out photos of the genitals,
    groin or buttocks, front-of-torso photos that are not close up and the "Inflicted skin lesions" label, and are
    marked medical;
  - DenPAR answers name the teeth only from the dataset's table (FDI numbers), and nothing when a number is unknown;
  - no Open Images label or Commons category is asked by another pack; and the wiring, the people and bodily packs
    being describing only.

Run it from the repository's folder:   python3 -m pytest packs/test_home_health.py
"""

import random

import life_skills_checks as L
import home_health_packs as h
import gaps_oi_packs as g

SPECS = [h.FIRST_AID, h.FIRST_AID_SKILLS, h.DENTAL, h.EYE, h.BIRTH]


def test_every_answer_ends_with_a_note():
    for specs in SPECS:
        for spec in specs:
            assert spec[2][0][1].endswith(h.NOTES), spec[0]
    assert all(s[2][0][1].endswith(h.DENTAL_NOTE) for s in h.DENTAL)
    assert all(s[2][0][1].endswith(h.EYE_NOTE) for s in h.EYE)
    assert all(s[2][0][1].endswith(h.BIRTH_NOTE) for s in h.BIRTH)
    for grp in h.HOME_HEALTH_OI:
        assert grp["note"] in h.NOTES
    for note in h.NOTES:
        assert "911" in note and ("not a diagnosis" in note or "or a diagnosis" in note)
    import home_health_sources as k
    assert (k.EMERGENCY_NOTE, k.DENTAL_NOTE, k.EYE_NOTE, k.BIRTH_NOTE) == h.NOTES
    assert all(a.endswith(h.NOTES) for _c, _q, a, _d in k.HOME_HEALTH_SA)


def test_scin_labels_and_exclusions():
    answer = h.scin_answer("{'Eczema': 0.41, 'Allergic Contact Dermatitis': 0.32, 'Psoriasis': 0.27}")
    assert answer.startswith("The dermatologists who reviewed this photo most often named eczema (also: allergic "
                             "contact dermatitis, psoriasis). This is not a diagnosis")
    assert answer.endswith(h.EMERGENCY_NOTE)
    assert h.scin_answer("{'Inflicted skin lesions': 0.5, 'Eczema': 0.5}") == "" and h.scin_answer("") == ""
    cases = [{"case_id": "-1", "image_1_path": "dataset/images/1.png", "image_1_shot_type": "CLOSE_UP",
              "image_2_path": "dataset/images/2.png", "image_2_shot_type": "AT_DISTANCE",
              "body_parts_torso_front": "YES"},
             {"case_id": "2", "image_1_path": "dataset/images/3.png", "image_1_shot_type": "CLOSE_UP",
              "body_parts_genitalia_or_groin": "YES"},
             {"case_id": "3", "image_1_path": "dataset/images/4.png", "image_1_shot_type": "AT_AN_ANGLE"}]
    labels = [{"case_id": c["case_id"], "weighted_skin_condition_label": "{'Tinea': 1.0}"} for c in cases]
    items = h.scin_items(cases, labels, 10)
    assert sorted(i[1].rsplit("/", 1)[-1] for i in items) == ["1.png", "4.png"]
    assert all(i[2][0]["content"] == "medical" and "SCIN" in i[2][0]["credit"] for i in items)


def test_denpar_teeth_from_the_table():
    rows = h.denpar_rows("Lower", "Right", "44,45,46")
    assert rows[0]["answer"].startswith("The dataset says it shows the lower right teeth: the lower right first "
                                        "premolar (44), the lower right second premolar (45) and the lower right "
                                        "first molar (46).")
    assert rows[0]["answer"].endswith(h.DENTAL_NOTE) and rows[1]["question"] == h.KIND_Q
    assert h.fdi_name("18") == "upper right third molar (wisdom tooth)" and h.fdi_name("55") == ""
    assert h.denpar_rows("Upper", "Anterior", "11,21,59") == []          # an unknown number: nothing said
    assert h.denpar_rows("Upper", "Left", "") == []
    # the table's own arch and side are not used: the teeth's numbers say where they are
    assert h.denpar_rows("Lower", "Left", "46,47")[0]["answer"].startswith("The dataset says it shows the lower "
                                                                             "right teeth: the lower right first molar")
    assert "upper front teeth" in h.denpar_rows("Upper", "Anterior", "12,11,21")[0]["answer"]


def test_open_images_rows():
    rows = g.oi_gap_rows({"Dentures": 1, "Mouthwash": 0}, h.HOME_HEALTH_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What dental care things are in this picture?"] == f"I can see dentures. {h.DENTAL_NOTE}"


def test_nothing_asked_twice():
    L.check_open_images([h.HOME_HEALTH_OI], {"home_health_packs"})
    L.check_categories(SPECS, {"home_health_packs"})


def test_wiring():
    import home_health_sources as k
    assert set(h.HOME_HEALTH_BODILY_KEYS) == set(k.HOME_HEALTH_BODILY_KEYS)
    L.check_wiring(h.HOME_HEALTH_PACKS, h.HOME_HEALTH_LIMITS, h.HOME_HEALTH_COMMONS_KEYS, "home_health_sources",
                   k.HOME_HEALTH_SOURCES, k.HOME_HEALTH_PICTURE_MAKING_OK, k.HOME_HEALTH_BODILY_KEYS)
    import sources
    import topics
    listed = {s.key: s for s in sources.SOURCES}
    assert listed["scin_skin_conditions"].content == "medical"
    assert set(h.HOME_HEALTH_PACKS) - {"scin_skin_conditions", "denpar_dental_xrays"} <= set(topics.find("home").keys)
    assert "denpar_dental_xrays" in topics.find("medicines").keys
