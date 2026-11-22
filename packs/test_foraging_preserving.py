"""A self-test of the foraging and home preserving packs (packs/foraging_preserving_packs.py) and the kit's collections
(training-kit/kit/foraging_preserving_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - the notes say what the owner asked ("never eat a wild mushroom unless an expert has confirmed it", Poison Control,
    tested recipes, pressure canner, altitude, botulism), in the packs and the kit alike, with the same words;
  - every answer says what the thing is and ends with its note (mushrooms the mushroom note, poisonous lookalikes the
    poison note, preserved food the preserving note), and no answer says a wild plant or mushroom is safe to eat;
  - no Commons category of these packs, nor any iNaturalist species, is named by another pack file, nor twice here;
  - the iNaturalist builder reads only GBIF's records and the Open Dataset's photos, keeps only open photos, and
    gives each picture the species, its warning and its credit (made-up records);
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, the wild plants in the nature topic and the preserved food in the food topic, and the
    guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_foraging_preserving.py
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import foraging_preserving_packs as f  # noqa: E402

REPO = os.path.dirname(HERE)
NOTES = ("FORAGE_NOTE", "MUSHROOM_NOTE", "POISON_NOTE", "PRESERVE_NOTE")


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    assert "never eat a wild mushroom unless an expert has confirmed it" in f.MUSHROOM_NOTE
    assert "1-800-222-1222" in f.MUSHROOM_NOTE and "1-800-222-1222" in f.POISON_NOTE
    assert "never eat a wild plant unless an expert has confirmed it" in f.FORAGE_NOTE
    for words in ("tested, current recipes", "pressure canner", "altitude", "botulism", "without tasting"):
        assert words in f.PRESERVE_NOTE, words


def test_every_answer_carries_its_note():
    notes = [getattr(f, n) for n in NOTES]
    for category, answer in answers(f.FORAGING_PRESERVING_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
        assert any(answer.endswith(n) for n in notes), category
        rest = answer
        for n in notes:
            rest = rest.replace(n, "")
        assert not re.search(r"safe to eat|is edible|good to eat", rest, re.I), answer
    for category, answer in answers(f.MUSHROOMS):
        assert answer.endswith(f.MUSHROOM_NOTE), category
    for category, answer in answers(f.PRESERVING):
        assert answer.endswith(f.PRESERVE_NOTE), category
    for category, answer in answers(f.WILD_FOOD):
        if re.search(r"poisonous;|deadly;|poisonous to eat", answer.split(". ")[0]):
            assert answer.endswith(f.POISON_NOTE), category
    for latin, words, note in f.INAT_WILD:
        answer = f.inat_answer(latin, words, note)
        name = re.split(r"[,;]", words)[0]
        assert answer.startswith(f"This is {name} ({latin})") and answer.endswith(note) and words[len(name):] in answer
        if re.search(r"deadly|poisonous[,;]|, poisonous$", words) and note is not f.MUSHROOM_NOTE:
            assert note is f.POISON_NOTE, latin


def test_no_commons_category_or_species_is_used_by_another_pack():
    """No category or iNaturalist species of these packs is named (in quotes) by another pack file, nor twice here."""
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(f.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as fh:
                others += fh.read()
    names = [spec[0] for spec in f.FORAGING_PRESERVING_SPECS]
    assert len(names) == len(set(names))
    species = [latin for latin, _w, _n in f.INAT_WILD]
    assert len(species) == len(set(species))
    for name in names + species:
        assert f'"{name}"' not in others, name


def test_inat_builder_reads_gbif_and_open_photos_only(monkeypatch):
    import na_animal_packs as na
    open_photo = {"type": "StillImage", "license": "http://creativecommons.org/licenses/by/4.0/",
                  "identifier": "https://inaturalist-open-data.s3.amazonaws.com/photos/111/original.jpg",
                  "creator": "Made Up"}
    closed_photo = dict(open_photo, license="http://creativecommons.org/licenses/by-nc/4.0/",
                        identifier="https://inaturalist-open-data.s3.amazonaws.com/photos/222/original.jpg")
    records = [{"key": 1, "media": [open_photo]}, {"key": 2, "media": [closed_photo]}]
    asked = []
    monkeypatch.setattr(f, "INAT_WILD", f.INAT_WILD[:1])
    monkeypatch.setattr(na, "inat_taxon", lambda s, name: {"taxonKey": 99})
    monkeypatch.setattr(na, "inat_pages", lambda s, params, rng, pages, limit=300: asked.append(params) or records)
    monkeypatch.setattr(f, "session", lambda: None)
    monkeypatch.setattr(f, "fetch_all", lambda items, workers=8, pause=0.0: [(n, b"jpeg", rows) for n, _u, rows in
                                                                              items])
    entries = f.build_inat_wild_edibles(5)
    assert asked and asked[0]["country"] == ["US", "CA"] and asked[0]["taxonKey"] == 99
    assert [e[0] for e in entries] == ["inat-wild-111.jpg"]
    latin, words, note = f.INAT_WILD[0]
    row = entries[0][2]
    assert row["answer"] == f.inat_answer(latin, words, note) and "CC BY 4.0" in row["credit"]
    assert "gbif.org/occurrence/1" in row["credit"]


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads foraging_preserving_sources at its end
    import foraging_preserving_sources as k
    for name in NOTES:
        assert getattr(k, name) == getattr(f, name), name
    assert all(reason for reason in k.FORAGING_PRESERVING_NOT_INCLUDED.values())


def test_wiring():
    keys = set(f.FORAGING_PRESERVING_PACKS)
    assert keys == set(f.FORAGING_PRESERVING_LIMITS) and len(keys) == 4
    assert keys <= set(build_packs.PACKS)
    assert set(f.FORAGING_PRESERVING_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(f.FORAGING_PRESERVING_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as fh:
        packs_yml = fh.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as fh:
        build_yml = fh.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as fh:
        kit_yml = fh.read()
    for key, limit in f.FORAGING_PRESERVING_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import foraging_preserving_sources") == 2
    import sources
    import topics
    import foraging_preserving_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert (key in no_making) == (key not in k.FORAGING_PRESERVING_PICTURE_MAKING_OK), key
    assert {s.key for s in k.FORAGING_PRESERVING_SOURCES} == keys
    nature, food = set(topics.find("nature").keys), set(topics.find("food").keys)
    assert {"commons_wild_food_plants", "commons_wild_mushrooms", "inat_wild_edibles"} <= nature
    assert "commons_home_preserving" in food
    assert "inat_wild_edibles" in no_making
