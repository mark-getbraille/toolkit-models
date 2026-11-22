"""A self-test of the light construction packs (packs/building_packs.py) and the kit's building collections
(training-kit/kit/building_sources.py), with made-up titles and labels only: nothing is downloaded.

It checks that a lumber size is said only when the file's own words name exactly one; that the concrete, fall,
permit and ramp notes follow their answers in the packs and the kit (the ramp note quoting the ADA Standards' 1 in 12
rule); that Open Images rows say only what the labels say; and that every pack is wired (build_packs, COMMONS_KEYS,
the workflows, the kit's sources, the machines topic, never for picture-making, the hidden imports). The shared
checks of Open Images labels and Commons categories are in packs/test_electronics.py.

Run it from the repository's folder:   python3 -m pytest packs/test_building.py
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import building_packs as b  # noqa: E402
from test_electronics import workflows  # noqa: E402


def test_lumber_size_only_from_the_files_own_words():
    rows = b.stated_lumber("File:Framing with 2x4 studs.jpg", "")
    assert rows and "2x4" in rows[0][1] and "nominal" in rows[0][1]
    assert b.stated_lumber("File:Deck joists, 2 by 10 lumber.jpg", "")[0][1].startswith(
        "The file's own words name the lumber size: 2x10")
    assert b.stated_lumber("File:Studs 2x4 and 2x6.jpg", "") == []              # two sizes: neither said
    assert b.stated_lumber("File:A 2x4 grid of photos.jpg", "") == []           # not about lumber
    assert b.stated_lumber("File:New deck.jpg", "A wooden deck.") == []


def test_notes_follow_their_answers():
    answers = {spec[0]: spec[2][0][1] for spec in b.BUILDING_SPECS}
    for category in ("Formwork", "Concrete pouring", "Bricklaying", "Tiling", "Tilers"):
        assert answers[category].endswith(b.CONCRETE_NOTE), category
    for category in ("Wooden ramps", "Ramps"):
        assert answers[category].endswith(b.RAMP_NOTE), category
    ramps = next(spec for spec in b.ACCESS if spec[0] == "Ramps")
    assert ramps[3].search("Wheelchair ramp at the library") and not ramps[3].search("Highway on-ramp")
    shoring = next(spec for spec in b.SAFETY if spec[0] == "Shoring")
    assert shoring[3].search("Trench shoring at a sewer dig") and not shoring[3].search("Shoring of a ship hull")
    for category in ("Wooden decks", "Garden sheds", "Wooden fences", "Wooden stairs"):
        assert answers[category].endswith(b.PERMIT_NOTE), category
    assert answers["Fall protection"].endswith(b.FALL_NOTE)
    assert "1 in 12" in b.RAMP_NOTE and "405.2" in b.RAMP_NOTE and "6 inches" in b.RAMP_NOTE
    assert "silica" in b.CONCRETE_NOTE and all(a.startswith("It shows ") for a in answers.values())
    import sources  # noqa: F401 - loaded first
    import building_sources as k
    assert (k.CONCRETE_NOTE, k.PERMIT_NOTE, k.RAMP_NOTE) == (b.CONCRETE_NOTE, b.PERMIT_NOTE, b.RAMP_NOTE)


def test_open_images_rows():
    rows = g.oi_gap_rows({"Shed": 1, "Fence": 0}, b.BUILDING_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What garden or yard building is this?"] == "I can see a shed. " + b.PERMIT_NOTE
    assert said["Is there a fence in this picture?"] == "No, I can't see a fence in this picture."


def test_wiring():
    packs_yml, build_yml, kit_yml = workflows()
    keys = set(b.BUILDING_PACKS)
    assert keys == set(b.BUILDING_LIMITS) and keys <= set(build_packs.PACKS)
    assert set(b.BUILDING_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(b.BUILDING_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    for key, limit in b.BUILDING_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import building_sources") == 2
    import sources
    import topics
    import building_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert set(k.BUILDING_PACK_KEYS) == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
    assert listed["building_commons_sa"].group == "share-alike"
    # building work and ramps are in the home topic, building-site safety in the machines topic (22 November 2026)
    placed = set(topics.find("machines").keys) | set(topics.find("home").keys)
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for s in k.BUILDING_SOURCES:
        assert s.key in placed and s.key in no_making, s.key
