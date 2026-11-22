"""Shared checks for the self-tests of the life-skills pack files (packs/test_car_care.py, test_garden.py,
test_home_health.py, test_instrument_care.py), with nothing downloaded: each test file calls these with its own
pack file's tables.

  asked_elsewhere(ours)            every Open Images label the OTHER pack files ask about
  check_open_images(groups, ours)  no label of these groups is asked by another pack file or twice here
  check_categories(specs, ours)    no Commons category of these specs is named (in quotes) by another pack file
  check_wiring(...)                the packs are in build_packs.PACKS, the Commons ones in COMMONS_KEYS, in the
                                   workflows' known list and limit lines, in the kit's sources (permissive, read with
                                   prepare_pack), in a topic, never for picture-making unless the kit module says so,
                                   and the kit module listed twice as a hidden import
"""

import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
KIT = os.path.join(REPO, "training-kit", "kit")
if KIT not in sys.path:
    sys.path.insert(1, KIT)
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import sources  # noqa: E402,F401 - the kit's: loaded before any kit module (it loads them at its end)


def asked_elsewhere(ours):
    """Every Open Images label another pack file asks about (the keys of its OI_... dictionaries, the labels of its
    gaps_oi_packs-style groups, home_packs' group questions); ours: the module names to skip."""
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


def check_open_images(group_lists, ours):
    """Asserts that no label of group_lists is asked elsewhere (any letter case) nor twice among them, and that the
    groups are well formed."""
    elsewhere = {x.lower() for x in asked_elsewhere(ours)}
    seen = set()
    for groups in group_lists:
        labels = {x.lower() for x in g.gap_labels(groups)}
        assert not labels & elsewhere, labels & elsewhere
        assert not labels & seen, labels & seen
        seen |= labels
        for grp in groups:
            assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())


def check_categories(spec_lists, ours):
    """Asserts that no Commons category of spec_lists is named (in quotes) by a pack file other than ours (module
    names), nor twice among them."""
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        name = os.path.basename(path)[:-3]
        if name not in ours and not name.startswith("test_") and name != "life_skills_checks":
            with open(path, encoding="utf-8") as f:
                others += f.read()
    seen = set()
    for specs in spec_lists:
        for spec in specs:
            category = spec[0]
            assert category not in seen, category
            seen.add(category)
            assert f'"{category}"' not in others, f"{category} is used by another pack"


def check_wiring(packs, limits, commons_keys, kit_module, kit_sources, picture_ok, bodily=()):
    """The wiring checks (see the module docstring); kit_module: the kit file's name, kit_sources its list of
    Sources, picture_ok its *_PICTURE_MAKING_OK, bodily its keys that show people's bodies."""
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    assert kit_yml.count(f"--hidden-import {kit_module} ") == 2, kit_module
    import sources
    import topics
    keys = set(packs)
    assert keys == set(limits) and keys <= set(build_packs.PACKS)
    assert set(commons_keys) <= keys and set(commons_keys) <= build_packs.COMMONS_KEYS
    assert not (keys - set(commons_keys)) & build_packs.COMMONS_KEYS
    listed = {s.key: s for s in sources.SOURCES}
    in_topics = {key for t in topics.TOPICS for key in t.keys}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for key, limit in limits.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
    for s in kit_sources:
        assert s.key in listed and (s.key in in_topics) == (s.content == ""), s.key   # medical: no topic
        assert (s.group == "permissive") == (s.key in keys), s.key
        assert (s.key in no_making) == (s.key not in picture_ok or s.key in bodily), s.key
    assert keys <= {s.key for s in kit_sources}
    assert set(bodily) <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS) and set(bodily) <= keys
