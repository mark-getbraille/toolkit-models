"""A self-test of the sports packs (packs/sports_packs.py) and the kit's sports collections
(training-kit/kit/sports_sources.py), with made-up labels only: nothing is downloaded from the internet.

It checks that:
  - every answer about protective gear or a combat sport carries the concussion note, the kit's notes are the same
    words, and no answer names a brand, team or score;
  - the people packs keep adults only (a youth, school or age-group file is refused; Open Images photos with a child
    label are left out);
  - Open Images rows say only what the labels say, and no label of this pack is asked by another pack;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive", prepare_pack), picture-making only for the
    keys the kit module allows, in the sports topic (the venues also in places, athletes in action also in people), and
    the guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_sports.py
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
import sports_packs as sp  # noqa: E402

REPO = os.path.dirname(HERE)
GEAR_WORDS = re.compile(r"helmet|pads?\b|guard|goaltender|mask|boxing", re.I)


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def test_notes():
    assert "CDC HEADS UP" in sp.GEAR_NOTE and "see a doctor" in sp.GEAR_NOTE
    for category, answer in answers(sp.SPORTS_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
        if GEAR_WORDS.search(category):
            assert sp.GEAR_NOTE in answer, category
        assert not re.search(r"\b(Nike|Adidas|Wilson|Spalding|Rawlings|Yankees|Lakers|score[sd]?)\b", answer), answer
    for grp in sp.SPORTS_OI:
        if grp["question"] in ("What protective gear is in this picture?", "What combat sport is this?"):
            assert grp["note"] == sp.GEAR_NOTE


def test_people_packs_keep_adults_only():
    for spec in sp.SPORTS_ACTION:
        pattern = spec[3]
        assert pattern.search("Women's high jump final, 2019 World Championships, Doha")
        for words in ("U-17 football match", "High school volleyball", "Youth Olympic Games shot put",
                      "Junior hammer throw", "Little League game", "girls field hockey"):
            assert not pattern.search(words), (spec[0], words)
    entries = [("a.jpg", b"x", {"question": "q", "answer": "a"}),
               (None, None, {"question": "q2", "answer": "a2", "file": "pictures/a.jpg"}),
               ("b.jpg", b"x", {"question": "q", "answer": "a", "child": True}),
               (None, None, {"question": "q2", "answer": "a2", "file": "pictures/b.jpg"})]
    kept = sp.adults_only(entries)
    assert [sp.picture_of(n, r) for n, _d, r in kept] == ["a.jpg", "a.jpg"]


def rows_of(labels):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, sp.SPORTS_OI, random.Random(1))


def test_open_images_rows():
    said = {r["question"]: r["answer"] for r in rows_of({"Lacrosse": 1, "Football helmet": 1, "Netball": 0})}
    assert said["What sport is being played here?"] == "I can see lacrosse."
    assert said["What protective gear is in this picture?"] == f"I can see a football helmet. {sp.GEAR_NOTE}"
    assert said["Is there any netball in this picture?"].startswith("No, I can't see")
    assert rows_of({"Soccer": 1, "Nudity": 1}) == []
    assert all(r.get("child") for r in rows_of({"Soccer": 1, "Boy": 1}))


def asked_elsewhere():
    """Every Open Images label another pack file asks about (the same reading as packs/test_outdoor_cooking.py)."""
    import importlib
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name == sp.__name__:
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
    mine = g.gap_labels(sp.SPORTS_OI)
    assert not mine & asked_elsewhere(), mine & asked_elsewhere()
    labels = [label for grp in sp.SPORTS_OI for label in grp["things"]]
    assert len(labels) == len(set(labels))
    for grp in sp.SPORTS_OI:
        assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())


def test_no_commons_category_is_used_by_another_pack():
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) != os.path.abspath(sp.__file__) and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in sp.SPORTS_SPECS]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_kit_notes_and_lists():
    import sources  # noqa: F401 - loaded first: it loads sports_sources at its end
    import sports_sources as k
    assert k.GEAR_NOTE == sp.GEAR_NOTE and k.ICE_NOTE == sp.ICE_NOTE
    pack_categories = {spec[0] for spec in sp.EQUIPMENT + sp.GEAR + sp.VENUES}
    for category, _q, answer, _deeper in k.SPORTS_SA:
        assert category in pack_categories, category
        if GEAR_WORDS.search(category):
            assert k.GEAR_NOTE in answer, category
    assert all(reason for reason in k.SPORTS_NOT_INCLUDED.values())


def test_wiring():
    keys = set(sp.SPORTS_PACKS)
    assert keys == set(sp.SPORTS_LIMITS) and len(keys) == 5
    assert keys <= set(build_packs.PACKS)
    assert set(sp.SPORTS_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(sp.SPORTS_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in sp.SPORTS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import sports_sources") == 2
    import sources
    import topics
    import sports_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    sports = set(topics.find("sports").keys)
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert key in sports, key
        assert (key in no_making) == (key not in k.SPORTS_PICTURE_MAKING_OK), key
    for s in k.SPORTS_SOURCES:
        assert s.key in listed and s.key in sports, s.key
    assert listed["sports_commons_sa"].group == "share-alike"
    assert {"commons_sports_action", "open_images_sports"} <= no_making
    assert {"wikidata_sports", "commons_adaptive_sports"} <= sports
    assert "commons_sports_venues" in topics.find("places").keys
    assert "commons_sports_action" in topics.find("people").keys
    ids = [t.id for t in topics.TOPICS]
    assert ids.index("sports") == ids.index("crafts") + 1 == ids.index("art") + 2     # arts and crafts between
