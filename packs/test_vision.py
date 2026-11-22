"""A self-test of the blind and low-vision living packs (packs/vision_packs.py) and the kit's collections and topic
(training-kit/kit/vision_sources.py, topics.py "vision"), with made-up records only: nothing is downloaded from the
internet.

It checks that:
  - every braille writer answer ends with the care note, in the packs and the kit alike, with the same words, and
    that answers start "This is" and name nothing beyond the category (no made-up numbers or parts);
  - the NMAH reader takes only records whose own words say they are for blind people, names the object as its
    record does and adds the care note only to braille writers;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in the topic "vision" with the packs gathered from other files, and the guarded kit
    module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_vision.py
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import vision_packs as v  # noqa: E402

REPO = os.path.dirname(HERE)


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_answers_and_care_note():
    assert "do not force it" in v.BRAILLER_NOTE and "repair" in v.BRAILLER_NOTE
    for category, answer in answers(v.VISION_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
        if re.search(r"braille typewriter|embosser|Moon writer", category, re.I):
            assert answer.endswith(v.BRAILLER_NOTE), category
        rest = answer.replace(v.BRAILLER_NOTE, "").replace(v.MOBILITY_NOTE, "")
        assert not re.search(r"\b\d+\s*(mm|cm|inch|kg|g|lb|dots? per)\b", rest), answer
    perkins = next(a for c, a in answers(v.BRAILLE_WRITING) if c == "Perkins braille typewriters")
    assert "Perkins Brailler" in perkins
    # people are in the mobility photos: they are asked what is happening, not "what is this"
    assert all(q == v.ASK_DOING for spec in v.MOBILITY_DEAFBLIND[:3] for q, _a in spec[2])


def record(object_name, title, notes="", access="CC0", maker="", date="", place=""):
    """A made-up NMAH open-access record."""
    free = {"objectType": [{"label": "Object Name", "content": object_name}],
            "notes": [{"label": "General History", "content": notes}] if notes else [],
            "name": [{"label": "maker", "content": maker}] if maker else [],
            "date": [{"label": "date made", "content": date}] if date else [],
            "place": [{"label": "place made", "content": place}] if place else []}
    return {"title": title, "content": {"freetext": free, "descriptiveNonRepeating": {
        "record_ID": "nmah_0001", "guid": "http://n2t.net/ark:/65665/ng0000",
        "online_media": {"media": [{"type": "Images", "content": "https://ids.si.edu/ids/deliveryService?id=X",
                                    "usage": {"access": access}}]}}}}


def test_nmah_reader():
    got = v.nmah_vision_row(record("braillewriter", "Perkins Brailler", maker="Howe Press", date="1951",
                                   place="United States: Massachusetts, Watertown"))
    assert got and got[0].endswith("&max=2048")
    answer = got[1][0]["answer"]
    assert answer.startswith("This is a braille writer") and "Howe Press" in answer and "1951" in answer
    assert "Massachusetts, Watertown" in answer and answer.endswith(v.BRAILLER_NOTE)
    slate = v.nmah_vision_row(record("slate", "Braille slate and stylus"))
    assert slate and "braille slate" in slate[1][0]["answer"] and v.BRAILLER_NOTE not in slate[1][0]["answer"]
    # a walking cane with no word about blind people, a window blind, and a picture that is not CC0: left out
    assert v.nmah_vision_row(record("cane", "Walking cane")) is None
    assert v.nmah_vision_row(record("window blind", "Venetian blinds")) is None
    assert v.nmah_vision_row(record("braillewriter", "Perkins Brailler", access="Usage conditions apply")) is None
    assert v.nmah_vision_row(record("cane", "Cane", notes="A long cane used by a blind traveller.")) is not None


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(v.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in v.VISION_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads vision_sources at its end
    import vision_sources as k
    assert k.BRAILLER_NOTE == v.BRAILLER_NOTE
    pack = {spec[0]: spec for spec in v.VISION_SPECS}
    for category, _q, answer, deeper in k.VISION_SA:
        assert category in pack, category
        assert answer == pack[category][2][0][1], category
    assert all(reason for reason in k.VISION_NOT_INCLUDED.values())


def test_wiring():
    keys = set(v.VISION_PACKS)
    assert keys == set(v.VISION_LIMITS) and len(keys) == 5
    assert keys <= set(build_packs.PACKS)
    assert set(v.VISION_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(v.VISION_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in v.VISION_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import vision_sources") == 2
    import sources
    import topics
    import vision_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    topic = topics.find("vision")
    assert topic and topic.title == "Blind and low-vision living" and not topic.sensitive
    ids = [t.id for t in topics.TOPICS]
    assert ids.index("vision") == ids.index("nudity") - 1
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert key in topic.keys, key
        assert (key in no_making) == (key not in k.VISION_PICTURE_MAKING_OK), key
    for s in k.VISION_SOURCES:
        assert s.key in listed and s.key in topic.keys, s.key
    for key in k.VISION_TOPIC_KEYS_ELSEWHERE:
        assert key in listed and key in topic.keys, key
    assert listed["vision_commons_sa"].group == "share-alike"
    assert "commons_mobility_deafblind" in no_making and "commons_tactile_access" in no_making
    assert "aph_museum_objects" in no_making


def test_aph_museum_rows():
    """The APH reader names the item by its own title, quotes the museum's subtitles without the greeting, and needs
    a real picture (not a thumbnail)."""
    assert v.aph_title("Museum 2022 02 21 Russian Braillewriter") == "Russian Braillewriter"
    assert v.aph_title("2022-04-05 Possum Moon Writer") == "Possum Moon Writer"
    assert v.aph_title("Museum 2022 01 11 2022-01-11 Early 1900s Paperweight") == "Early 1900s Paperweight"
    srt = ("1\n00:00:00,000 --> 00:00:03,000\nHi I'm Mike Hudson, Director of the Museum of the American Printing "
           "House for the Blind.\n\n2\n00:00:03,000 --> 00:00:09,000\nOur mystery object today is a made-up "
           "braillewriter with six keys and a space bar, built long ago for a school.\n")
    got = v.aph_row("museum-x", "Museum 2022 02 21 Russian Braillewriter",
                    ["thing_thumb.jpg", "x.thumbs/a.jpg", "Russian braillewriter.jpg"], srt)
    assert got and got[0].endswith("Russian%20braillewriter.jpg")
    assert got[1][0]["answer"] == ("It is a picture from the Museum of the American Printing House for the Blind "
                                   "(APH)'s item \"Russian Braillewriter\" (its own title for it).")
    assert got[1][1]["answer"].startswith("Our mystery object today is a made-up braillewriter")
    assert "Hudson" not in got[1][1]["answer"]
    assert v.aph_row("museum-y", "No picture", ["a_thumb.jpg", "b.mp4"]) is None
