"""A self-test of the garden and lawn packs (packs/garden_packs.py) and the kit's garden collections
(training-kit/kit/garden_sources.py), with made-up file words and labels only: nothing is downloaded.

It checks that:
  - a seed packet's or plant label's plant is named only from the file's own words, and only for seed packet and
    label pictures;
  - plant problems describe the symptom and end with the extension office note (the same words in the kit);
  - Open Images rows say only what the labels say; no label or Commons category is asked by another pack;
  - the packs are wired (build_packs, the workflows, the kit's sources, topics and picture-making rules).

Run it from the repository's folder:   python3 -m pytest packs/test_garden.py
"""

import random

import life_skills_checks as L
import garden_packs as gp
import gaps_oi_packs as g
import build_packs


def test_seed_plant_only_from_the_words():
    assert gp.seed_plant("Seed packet of Brandywine tomato, 1950s.") == "Brandywine tomato"
    assert gp.seed_plant("Burpee Golden Bantam seeds packet") == "Burpee Golden Bantam"
    assert gp.seed_plant("Plant label: Lavandula angustifolia 'Hidcote'") == "Lavandula angustifolia 'Hidcote'"
    assert gp.seed_plant("A packet on a table.") == "" and gp.seed_plant("Seed packet of DSC01234") == ""
    entries = [("a.jpg", b"x", {"question": gp.ASK_WHAT, "answer": "This is a seed packet: ...", "credit": "c"}),
               (None, None, {"question": build_packs.ALT_TEXT, "answer": "Seed packet of Cherokee Purple tomato.",
                             "credit": "c", "file": "pictures/a.jpg"}),
               ("b.jpg", b"y", {"question": gp.ASK_WHAT, "answer": "This is pruning: ...", "credit": "c"}),
               (None, None, {"question": build_packs.ALT_TEXT, "answer": "Seed packet of Kale lying by shears.",
                             "credit": "c", "file": "pictures/b.jpg"})]
    added = [e for e in gp.with_seed_plants(entries) if e[2]["question"] == gp.SEED_Q]
    assert len(added) == 1 and added[0][2]["file"] == "pictures/a.jpg"
    assert added[0][2]["answer"] == "It is for Cherokee Purple tomato, as the file's own words say."


def test_chlorosis_leaves_out_albino_plants():
    pattern = next(s for s in gp.PLANT_PROBLEMS if s[0] == "Chlorosis")[3]
    assert pattern.search("Iron chlorosis on a maple leaf") and not pattern.search("Albino milkweed")


def test_plant_problems():
    for category, _deeper, rows, *_pattern in gp.PLANT_PROBLEMS:
        assert rows[0][0] == gp.ASK_PLANT and rows[0][1].endswith(gp.PLANT_SAFETY), category
    import garden_sources as k
    assert k.PLANT_SAFETY == gp.PLANT_SAFETY
    assert all(a.endswith(k.PLANT_SAFETY) for _c, q, a, _d in k.GARDEN_SA if q == gp.ASK_PLANT)


def test_open_images_rows():
    rows = g.oi_gap_rows({"Basil": 1, "Rosemary": 1, "Dill": 0}, gp.GARDEN_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What herbs are in this picture?"] == "I can see basil and rosemary."
    rows = g.oi_gap_rows({"Plant pathology": 1}, gp.GARDEN_OI, random.Random(1))
    assert rows[0]["answer"] == f"I can see a plant disease. {gp.PLANT_SAFETY}"


def test_nothing_asked_twice():
    L.check_open_images([gp.GARDEN_OI], {"garden_packs"})
    L.check_categories([gp.GROWING, gp.CARE, gp.LAWN_CARE, gp.PLANT_PROBLEMS], {"garden_packs"})


def test_wiring():
    import garden_sources as k
    L.check_wiring(gp.GARDEN_PACKS, gp.GARDEN_LIMITS, gp.GARDEN_COMMONS_KEYS, "garden_sources", k.GARDEN_SOURCES,
                   k.GARDEN_PICTURE_MAKING_OK)
    import topics
    assert set(gp.GARDEN_PACKS) <= set(topics.find("nature").keys)
