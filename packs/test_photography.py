"""A self-test of the photography packs (packs/photography_packs.py) and the kit's collections
(training-kit/kit/photography_sources.py), with made-up records and labels only: nothing is downloaded.

It checks that:
  - the safety notes say what the owner asked (ventilation, gloves, never mix, disposal; mercury and cyanide as
    history; UV; nitrate film; flash powder), in the packs and the kit alike, with the same words;
  - darkroom, historic process and alternative process answers carry their notes, and no answer names a setting;
  - the historic process files are filtered against post-mortem and memorial portraits;
  - the NMAH reader answers from the record's own words, only for CC0 pictures, and leaves out films and patent
    models (made-up records);
  - Open Images rows say only what the labels say, and no label of this pack is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in the art and crafts topics (equipment also in machines), no new topic, and the kit
    module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_photography.py
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
import photography_packs as p  # noqa: E402

REPO = os.path.dirname(HERE)
NOTE_NAMES = ("DARKROOM_NOTE", "HISTORIC_NOTE", "UV_NOTE", "NITRATE_NOTE", "FLASH_NOTE")


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes_say_what_the_owner_asked():
    for words in ("ventilation", "nitrile gloves", "never mix", "used fixer", "collection site"):
        assert words in p.DARKROOM_NOTE, words
    for words in ("mercury", "potassium cyanide", "history only", "expert training"):
        assert words in p.HISTORIC_NOTE, words
    assert "UV" in p.UV_NOTE and "eyes and skin" in p.UV_NOTE
    assert "cellulose nitrate" in p.NITRATE_NOTE and "conservator" in p.NITRATE_NOTE
    assert "explosive" in p.FLASH_NOTE and "never make" in p.FLASH_NOTE


def test_every_answer_carries_its_notes():
    for category, answer in answers(p.PHOTOGRAPHY_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
        first = answer.split(". ")[0]
        if re.search(r"darkroom|enlarger|safelight", first, re.I):
            assert p.DARKROOM_NOTE in answer, category
        if re.search(r"daguerreotype,|ambrotype,|tintype|wet collodion|daguerreotype camera", first) and \
                "case" not in category:
            assert p.HISTORIC_NOTE in answer, category
        if re.search(r"cyanotype|platinum|gum bichromate|salt print", first):
            assert p.UV_NOTE in answer, category
        if re.search(r"flashbulb|flash powder", first):
            assert p.FLASH_NOTE in answer, category
        if "nitrate" in first:
            assert p.NITRATE_NOTE in answer, category
        rest = answer
        for name in NOTE_NAMES:
            rest = rest.replace(getattr(p, name), "")
        assert not re.search(r"\bf/\d|\d+\s*(seconds?|mm lens|ISO)\b", rest), answer


def test_historic_files_are_filtered():
    for spec in p.HISTORIC_PROCESSES:
        assert len(spec) == 4 and spec[3] is p.NOT_MEMORIAL, spec[0]
    assert p.NOT_MEMORIAL.search("Daguerreotype of a man in a frock coat, about 1850")
    assert not p.NOT_MEMORIAL.search("Post-mortem daguerreotype of a child")
    assert not p.NOT_MEMORIAL.search("Tintype, memorial portrait")


def nmah_record(name, title, access="CC0", maker="Eastman Kodak Company"):
    """A made-up NMAH open-access record."""
    return {"title": title, "content": {
        "freetext": {"objectType": [{"label": "Object Name", "content": name}],
                     "name": [{"label": "maker", "content": maker}],
                     "date": [{"label": "date made", "content": "1925"}],
                     "place": [{"label": "place made", "content": "United States: New York, Rochester"}],
                     "physicalDescription": [{"label": "Physical Description", "content": "wood (overall material)"},
                                             {"label": "Physical Description", "content": "leather (part: bellows "
                                                                                          "material)"}]},
        "descriptiveNonRepeating": {"record_ID": "nmah_000001", "guid": "http://n2t.net/ark:/65665/made-up",
                                    "online_media": {"media": [{"type": "Images", "content": "https://ids.si.edu/x",
                                                                "usage": {"access": access}}]}}}}


def test_nmah_rows():
    url, rows = p.nmah_photo_row(nmah_record("camera, folding", "No. 3A Folding Pocket Kodak"))
    answer = rows[0]["answer"]
    assert url.endswith("&max=2048") and answer.startswith("This is a camera")
    assert "Eastman Kodak Company" in answer and "1925" in answer and "Rochester" in answer
    assert "wood" in answer and "(bellows)" in answer and "CC0" in rows[0]["credit"]
    url, rows = p.nmah_photo_row(nmah_record("daguerreotype", "Portrait of a woman", maker="unidentified"))
    assert rows[0]["answer"].startswith("This is a daguerreotype") and p.HISTORIC_NOTE in rows[0]["answer"]
    assert "unidentified" not in rows[0]["answer"]
    assert p.nmah_photo_row(nmah_record("camera", "Kodak", access="Usage conditions apply")) is None
    assert p.nmah_photo_row(nmah_record("camera, motion picture", "Cine-Kodak")) is None
    assert p.nmah_photo_row(nmah_record("patent model", "Camera shutter patent model")) is None
    assert p.nmah_photo_row(nmah_record("daguerreotype", "Post-mortem portrait")) is None


def rows_of(labels):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, p.PHOTOGRAPHY_OI, random.Random(1))


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in rows_of({"Enlarger": 1, "Box camera": 0})}
    assert said["What darkroom or film things are in this picture?"] == f"I can see an enlarger. {p.DARKROOM_NOTE}"
    assert said["Is there a box camera in this picture?"] == "No, I can't see a box camera in this picture."
    assert rows_of({"Lens hood": 1, "Nudity": 1}) == []


def asked_elsewhere():
    """Every Open Images label another pack file asks about (the same reading as packs/test_making.py)."""
    import glob
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name == p.__name__:
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
    mine = g.gap_labels(p.PHOTOGRAPHY_OI)
    assert not mine & asked_elsewhere(), mine & asked_elsewhere()
    labels = [label for grp in p.PHOTOGRAPHY_OI for label in grp["things"]]
    assert len(labels) == len(set(labels))
    assert not {"Nude photography", "Photographer", "Portrait", "Camera", "Digital camera"} & set(labels)


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    import glob
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(p.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in p.PHOTOGRAPHY_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads photography_sources at its end
    import photography_sources as k
    for name in NOTE_NAMES:
        assert getattr(k, name) == getattr(p, name), name
    pack_answers = dict(answers(p.PHOTOGRAPHY_SPECS))
    for category, _q, answer, _deeper in k.PHOTOGRAPHY_SA:
        assert pack_answers[category] == answer, category
    assert all(reason for reason in k.PHOTOGRAPHY_NOT_INCLUDED.values())


def test_wiring():
    keys = set(p.PHOTOGRAPHY_PACKS)
    assert keys == set(p.PHOTOGRAPHY_LIMITS) and len(keys) == 7
    assert keys <= set(build_packs.PACKS)
    assert set(p.PHOTOGRAPHY_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(p.PHOTOGRAPHY_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    workflows = os.path.join(REPO, ".github", "workflows")
    with open(os.path.join(workflows, "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(workflows, "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(workflows, "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in p.PHOTOGRAPHY_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import photography_sources") == 2
    import sources
    import topics
    import photography_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert (key in no_making) == (key not in k.PHOTOGRAPHY_PICTURE_MAKING_OK), key
    assert listed["photography_commons_sa"].group == "share-alike"
    assert "commons_historic_processes" in no_making and "open_images_photography" in no_making
    assert "nmah_photography" in no_making and "commons_cameras_by_type" not in no_making
    for topic_id, topic_keys in k.PHOTOGRAPHY_TOPICS.items():
        assert set(topic_keys) <= set(topics.find(topic_id).keys), topic_id
    assert set(k.PHOTOGRAPHY_TOPICS) == {"art", "crafts", "machines"}
    assert not [t for t in topics.TOPICS if t.id in ("photography", "photo", "cameras")]
