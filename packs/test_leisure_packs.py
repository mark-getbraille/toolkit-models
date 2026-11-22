"""A self-test of the leisure picture packs (the owner's requests of 2026-11-22): homestead_packs.py, outdoors_packs.py,
games_packs.py, science_packs.py, clothing_packs.py and plant_id_packs.py, and the kit's matching collections
(training-kit/kit/homestead_sources.py, outdoors_sources.py, games_sources.py, science_use_sources.py,
clothing_sources.py and plant_id_sources.py), with made-up labels only: nothing is downloaded from the internet.

It checks that:
  - the safety notes say what the owner asked (hand washing after poultry, bee stings, septic tanks, life jackets and
    cold water, ice, avalanche gear, the Sun and telescopes, small parts, poison plants, "never eat a wild mushroom
    unless an expert has identified it in person", Poison Control), and the kit uses the same words;
  - every Commons answer is "This is ..." with the notes that fit its subject, and no plant answer says a plant is safe
    to eat;
  - the word filter keeps egg candling and leaves out candle-making;
  - Open Images rows say only what the labels say, the "yes" answers carry their group's note, telescope answers the
    Sun note, and the clothing pack leaves out photos with swimwear or underwear labels whoever is in them;
  - no Open Images label of these packs is asked by another pack, nor twice here; no Commons category of these packs
    is named by another pack file, nor twice across them;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys each kit module allows, in its topic (home, nature, machines or documents), and each guarded kit module listed
    twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_leisure_packs.py
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
import clothing_packs as cl  # noqa: E402
import games_packs as gm  # noqa: E402
import homestead_packs as hs  # noqa: E402
import outdoors_packs as od  # noqa: E402
import plant_id_packs as pl  # noqa: E402
import science_packs as sc  # noqa: E402
from test_outdoor_cooking import asked_elsewhere  # noqa: E402

REPO = os.path.dirname(HERE)
# (pack module, packs, limits, Commons keys, specs, Open Images groups, kit module name, kit prefix)
MODULES = [
    (hs, hs.HOMESTEAD_PACKS, hs.HOMESTEAD_LIMITS, hs.HOMESTEAD_COMMONS_KEYS, hs.HOMESTEAD_SPECS, hs.HOMESTEAD_OI,
     "homestead_sources", "HOMESTEAD"),
    (od, od.OUTDOORS_PACKS, od.OUTDOORS_LIMITS, od.OUTDOORS_COMMONS_KEYS, od.OUTDOORS_SPECS, od.OUTDOORS_OI,
     "outdoors_sources", "OUTDOORS"),
    (gm, gm.GAMES_PACKS, gm.GAMES_LIMITS, gm.GAMES_COMMONS_KEYS, gm.GAMES_SPECS, gm.GAMES_OI, "games_sources", "GAMES"),
    (sc, sc.SCIENCE_PACKS, sc.SCIENCE_LIMITS, sc.SCIENCE_COMMONS_KEYS, sc.SCIENCE_SPECS, sc.SCIENCE_OI,
     "science_use_sources", "SCIENCE"),
    (cl, cl.CLOTHING_PACKS, cl.CLOTHING_LIMITS, cl.CLOTHING_COMMONS_KEYS, cl.CLOTHING_SPECS, cl.CLOTHING_OI,
     "clothing_sources", "CLOTHING"),
    (pl, pl.PLANT_ID_PACKS, pl.PLANT_ID_LIMITS, pl.PLANT_ID_COMMONS_KEYS, pl.PLANT_ID_SPECS, [], "plant_id_sources",
     "PLANT_ID"),
]
NOTES = {"homestead_sources": (hs, ("HANDLING_NOTE", "POULTRY_NOTE", "BEE_NOTE", "WELL_NOTE", "POWER_NOTE")),
         "outdoors_sources": (od, ("LIFE_JACKET_NOTE", "ICE_NOTE", "TRAIL_NOTE", "MARKER_NOTE", "AVALANCHE_NOTE",
                                   "HOOK_NOTE")),
         "games_sources": (gm, ("SMALL_PARTS_NOTE",)), "science_use_sources": (sc, ("SUN_NOTE", "LAB_NOTE")),
         "plant_id_sources": (pl, ("POISON_NOTE", "SKIN_NOTE", "MUSHROOM_NOTE", "FORAGE_NOTE"))}


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    assert "wash your hands" in hs.POULTRY_NOTE and "Salmonella" in hs.POULTRY_NOTE
    assert "allergic to stings" in hs.BEE_NOTE and "septic tank" in hs.WELL_NOTE
    assert "life jacket" in od.LIFE_JACKET_NOTE and "cold water" in od.LIFE_JACKET_NOTE
    assert "never go on ice" in od.ICE_NOTE and "transceiver, probe and shovel" in od.AVALANCHE_NOTE
    assert "solar filter" in sc.SUN_NOTE and "children under 3" in gm.SMALL_PARTS_NOTE
    assert "unless an expert has identified it in person" in pl.MUSHROOM_NOTE
    assert "unless an expert has confirmed it in person" in pl.FORAGE_NOTE
    assert "1-800-222-1222" in pl.POISON_NOTE and "death cap" in pl.MUSHROOM_NOTE


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads the leisure kit files at its end
    import importlib
    for kit_name, (pack_module, names) in NOTES.items():
        kit = importlib.import_module(kit_name)
        for name in names:
            assert getattr(kit, name) == getattr(pack_module, name), (kit_name, name)


def test_every_answer_carries_its_notes():
    for module, _p, _l, _c, specs, _oi, _k, _x in MODULES:
        for category, answer in answers(specs):
            assert answer.startswith("This ") and answer.endswith("."), category
    for category, answer in answers(hs.POULTRY_BEES):
        if re.search(r"hive|bee smoker|beekeeping suit|hive tool", answer.split(".")[0], re.I):
            assert hs.BEE_NOTE in answer, category
        if re.search(r"incubator|candling|chicken|nest box|duck", answer.split(".")[0], re.I):
            assert hs.POULTRY_NOTE in answer, category
    for category, answer in answers(od.BOATING):
        assert od.LIFE_JACKET_NOTE in answer or "towing" in answer, category
    for category, answer in answers(od.FISHING):
        assert od.HOOK_NOTE in answer, category
    for category, answer in answers(od.MARKERS):
        assert od.MARKER_NOTE in answer or od.TRAIL_NOTE in answer or od.AVALANCHE_NOTE in answer, category
    for category, answer in answers(pl.POISONOUS):
        assert pl.POISON_NOTE in answer, category
    for category, answer in answers(pl.MUSHROOMS):
        assert pl.MUSHROOM_NOTE in answer, category
    for category, answer in answers(pl.WILD_BARK):
        assert pl.FORAGE_NOTE in answer or category in ("Bark (botany)", "Leaf shapes"), category
    for category, answer in answers(pl.PLANT_ID_SPECS):
        assert not re.search(r"\b(safe to eat|is edible|you can eat)\b", answer, re.I), category
    telescope = next(a for c, a in answers(sc.INSTRUMENTS) if c == "Telescopes")
    assert telescope.endswith(sc.SUN_NOTE)


def test_word_filter():
    candling = next(s for s in hs.POULTRY_BEES if s[0] == "Candling")
    assert candling[3].search("Candling a hen's egg on day 7") and not candling[3].search("Candle making workshop")


def rows_of(labels, groups):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1))


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in rows_of({"Goat": 1, "Barn": 0}, hs.HOMESTEAD_OI)}
    assert said["What farm animals are in this picture?"] == f"I can see a goat. {hs.HANDLING_NOTE}"
    assert said["Is there a barn in this picture?"] == "No, I can't see a barn in this picture."
    said = {r["question"]: r["answer"] for r in rows_of({"Tartan": 1}, cl.CLOTHING_OI)}
    assert said["What pattern is on the clothes or fabric here?"] == "I can see tartan."
    entries = [("a.jpg", b"x", {"question": "Is there a life jacket in this picture?",
                                 "answer": "Yes, there is a life jacket in this picture."})]
    from outdoor_cooking_packs import with_yes_notes
    assert with_yes_notes(entries, od.OUTDOORS_OI)[0][2]["answer"].endswith(od.LIFE_JACKET_NOTE)
    assert rows_of({"Shirt": 1, "Nudity": 1}, cl.CLOTHING_OI) == []


def test_science_and_clothing_builders(monkeypatch):
    """The telescope answers get the Sun note; the clothing build leaves out swimwear photos and restores the shared
    exclusions afterwards (made-up rows, no download)."""
    seen = {}

    def fake_build(key, groups, limit, seed):
        seen[key] = set(g.LEAVE_OUT)
        return [("p.jpg", b"x", {"question": "Is there a telescope in this picture?",
                                  "answer": "Yes, there is a telescope in this picture."}),
                (None, None, {"question": "Is there a globe in this picture?",
                              "answer": "No, I can't see a globe in this picture."})]
    monkeypatch.setattr(sc, "build_oi_gap", fake_build)
    got = sc.build_open_images_science(5)
    assert got[0][2]["answer"].endswith(sc.SUN_NOTE) and not got[1][2]["answer"].endswith(sc.SUN_NOTE)
    before = set(g.LEAVE_OUT)
    monkeypatch.setattr(cl, "build_oi_gap", fake_build)
    cl.build_open_images_clothing(5)
    assert {"Swimwear", "Bikini", "Brassiere"} <= seen["open_images_clothing"]
    assert set(g.LEAVE_OUT) == before


def test_no_open_images_label_is_asked_twice():
    mine = [label for m in MODULES for grp in m[5] for label in grp["things"]]
    assert len(mine) == len(set(mine))
    names = {m[0].__name__ for m in MODULES}
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name in names:
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
    assert not set(mine) & elsewhere, set(mine) & elsewhere
    assert asked_elsewhere  # the outdoor cooking test's reader counts these packs' labels as asked by them
    for m in MODULES:
        for grp in m[5]:
            assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())


def test_no_commons_category_is_used_by_another_pack():
    mine = {os.path.abspath(m[0].__file__) for m in MODULES}
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) not in mine and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for m in MODULES for spec in m[4]]
    assert len(names) == len(set(names)), [n for n in names if names.count(n) > 1]
    for name in names:
        assert f'"{name}"' not in others, name


def test_wiring():
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    import importlib
    import sources
    import topics
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    every_topic = {t.id: set(t.keys) for t in topics.TOPICS}
    for module, packs, limits, commons, _specs, _oi, kit_name, prefix in MODULES:
        keys = set(packs)
        assert keys == set(limits) and keys <= set(build_packs.PACKS), module.__name__
        assert set(commons) <= build_packs.COMMONS_KEYS
        assert not (keys - set(commons)) & build_packs.COMMONS_KEYS
        for key, limit in limits.items():
            assert f'"{key}"' in packs_yml, key
            assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
        assert kit_yml.count(f"--hidden-import {kit_name} ") == 2, kit_name
        kit = importlib.import_module(kit_name)
        ok = getattr(kit, f"{prefix}_PICTURE_MAKING_OK")
        kit_sources = getattr(kit, f"{prefix}_SOURCES")
        assert all(reason for reason in getattr(kit, f"{prefix}_NOT_INCLUDED").values())
        for key in keys:
            assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
            assert (key in no_making) == (key not in ok), key
        for s in kit_sources:
            assert s.key in listed and any(s.key in t for t in every_topic.values()), s.key
            assert s.key in keys or s.group == "share-alike", s.key
    assert "commons_boating_paddling" in every_topic["transport"]
    assert "commons_water_trail_markers" in every_topic["documents"]
    assert "commons_poisonous_plants" in every_topic["nature"] and "open_images_homestead" in every_topic["nature"]
    assert "open_images_clothing" in every_topic["home"] and "commons_card_games" in every_topic["home"]
    assert "open_images_clothing" in no_making and "commons_mushrooms_id" not in no_making
