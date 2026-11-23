"""A self-test of the homestead skills picture packs (packs/homestead_fill_packs.py) and the kit's matching collections
(training-kit/kit/homestead_fill_sources.py), with made-up titles only: nothing is downloaded from the internet.

It checks that:
  - the safety notes say what the owner asked (hot metal and galvanised fumes, trap laws, tanning poisons, USDA meat
    temperatures, boiling water, treated seed, fishing gear rules, the Sun through a sextant), and the kit uses the
    same words;
  - every Commons answer is "This is ..." and ends with the note of its skill;
  - the trap category keeps only historic traps in museums and never a caught, dead or bleeding animal, and the
    tanning category keeps leather and leaves out sun tanning (made-up file titles);
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflows' known list and limit lines, in the
    kit's sources (packs "permissive", prepare_pack), picture-making only for the keys the kit module allows, in its
    topics, and the kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_homestead_fill.py
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import homestead_fill_packs as hf  # noqa: E402

REPO = os.path.dirname(HERE)
NOTES = ("FORGE_NOTE", "HORSE_NOTE", "TRAP_NOTE", "TANNING_NOTE", "MEAT_NOTE", "KNIFE_NOTE", "WATER_NOTE",
         "SEED_NOTE", "NET_NOTE", "SUN_NOTE", "NAV_NOTE")


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    assert "treat all metal" in hf.FORGE_NOTE and "galvanised" in hf.FORGE_NOTE and "metal fume fever" in hf.FORGE_NOTE
    assert "licences, trapper education, seasons and legal traps" in hf.TRAP_NOTE
    assert "arsenic" in hf.TANNING_NOTE and "gloves" in hf.TANNING_NOTE
    assert "145 F" in hf.MEAT_NOTE and "160 F" in hf.MEAT_NOTE and "165 F" in hf.MEAT_NOTE
    assert "1 minute" in hf.WATER_NOTE and "6,500 feet" in hf.WATER_NOTE
    assert "treated" in hf.SEED_NOTE and "fishing licence and gear rules" in hf.NET_NOTE
    assert "sextant" in hf.SUN_NOTE and "solar filter" in hf.SUN_NOTE


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads homestead_fill_sources at its end
    import homestead_fill_sources as k
    for name in NOTES:
        assert getattr(k, name) == getattr(hf, name), name


def test_every_answer_carries_its_notes():
    for category, answer in answers(hf.HOMESTEAD_FILL_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
    rules = [(hf.FORGE_TRAPS_TANNING, r"blacksmith|hardy|swage", hf.FORGE_NOTE),
             (hf.FORGE_TRAPS_TANNING, r"horseshoe|farriery", hf.HORSE_NOTE),
             (hf.FORGE_TRAPS_TANNING, r"leghold", hf.TRAP_NOTE),
             (hf.FORGE_TRAPS_TANNING, r"fish trap|lobster", hf.NET_NOTE),
             (hf.FORGE_TRAPS_TANNING, r"tann", hf.TANNING_NOTE),
             (hf.HOMESTEAD_STORES, r"seed", hf.SEED_NOTE),
             (hf.HOMESTEAD_STORES, r"net\b", hf.NET_NOTE),
             (hf.HOMESTEAD_STORES, r"sausage", hf.MEAT_NOTE),
             (hf.HOMESTEAD_STORES, r"cleaver|knife", hf.KNIFE_NOTE),
             (hf.HOMESTEAD_STORES, r"water", hf.WATER_NOTE),
             (hf.STARS_NAVIGATION, r"sextant|octant", hf.SUN_NOTE),
             (hf.STARS_NAVIGATION, r"sextant|octant|chronometer|celestial navigation", hf.NAV_NOTE)]
    for specs, pattern, note in rules:
        matched = [(c, a) for c, a in answers(specs) if re.search(pattern, a.split(".")[0], re.I)]
        assert matched, pattern
        for category, answer in matched:
            assert note in answer, (category, pattern)


def test_trap_and_tanning_filters():
    trap = next(s for s in hf.FORGE_TRAPS_TANNING if s[0] == "Leghold traps")[3]
    for kept in ("Wolf kapkan - Bashkortostan National Museum.jpg", "Iron gin rat trap, England, 1750-1900 Wellcome",
                 "Tellereisen Silvaplana, 19. Jh..jpeg", "Fur trade museum traps.jpg"):
        assert trap.search(kept), kept
    for left in ("Leghold trap IMG 20180706 105204220.jpg", "Fox caught in a leghold trap, museum photo 1910",
                 "Dead coyote in trap, historic photograph", "Chuck Jones - Merrie Melodies - Fox Pop (1942) - 02m",
                 "A trap set by the trail in 2018"):
        assert not trap.search(left), left
    tanning = next(s for s in hf.FORGE_TRAPS_TANNING if s[0] == "Tanning")[3]
    assert tanning.search("Hides drying at the tannery in Fez") and tanning.search("Vegetable tanned leather")
    assert not tanning.search("Sunbed at a tanning salon")
    sizes = {s[0]: s[1] for s in hf.HOMESTEAD_FILL_SPECS}
    assert sizes["Leghold traps"] is False          # never its subcategory "Animals in leghold traps"


def test_no_commons_category_is_used_by_another_pack():
    mine = os.path.abspath(hf.__file__)
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != mine and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in hf.HOMESTEAD_FILL_SPECS]
    assert len(names) == len(set(names)), [n for n in names if names.count(n) > 1]
    for name in names:
        assert f'"{name}"' not in others, name
    for gone in ("Animals in leghold traps", "Bear traps", "Mole traps", "Meat processing"):
        assert gone not in names


def test_wiring():
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    import sources
    import topics
    import homestead_fill_sources as k
    keys = set(hf.HOMESTEAD_FILL_PACKS)
    assert keys == set(hf.HOMESTEAD_FILL_LIMITS) and len(keys) == 3 and keys <= set(build_packs.PACKS)
    assert set(hf.HOMESTEAD_FILL_COMMONS_KEYS) == keys and keys <= build_packs.COMMONS_KEYS
    for key, limit in hf.HOMESTEAD_FILL_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import homestead_fill_sources ") == 2
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    every_topic = {t.id: set(t.keys) for t in topics.TOPICS}
    assert {s.key for s in k.HOMESTEAD_FILL_SOURCES} == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert listed[key].cap == hf.HOMESTEAD_FILL_LIMITS[key], key
        assert (key in no_making) == (key not in k.HOMESTEAD_FILL_PICTURE_MAKING_OK), key
        assert any(key in t for t in every_topic.values()), key
    assert "commons_stars_navigation" in every_topic["documents"]
    assert {"commons_forge_traps_tanning", "commons_homestead_stores"} <= every_topic["home"]
    assert "commons_forge_traps_tanning" in every_topic["crafts"]
    assert "commons_homestead_stores" in no_making
    assert all(reason for reason in k.HOMESTEAD_FILL_NOT_INCLUDED.values())
