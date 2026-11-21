"""A self-test of the drinks packs (packs/drinks_packs.py) and the kit's drinks collections (training-kit/kit/
drinks_sources.py), with made-up labels and records only: nothing is downloaded from the internet.

It checks that:
  - alcohol answers end with the responsible-drinking note, energy drink answers with the caffeine note, and still
    answers START with the legal and safety notes on home distilling (in the packs and the kit alike);
  - no answer states an alcohol content, a proof or a caffeine amount (the sources give none);
  - Open Images rows say only what the labels say, and the bar pack leaves out every photo with a child;
  - no Open Images label of these packs is asked by another pack, nor by both drinks packs;
  - Europeana records must be English, open and name what was searched for; distilling records get the warning first;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS, in the workflows' known list and
    limit lines, in the kit's sources (open ones "permissive"), the alcohol keys apart from the soft drink keys, the
    alcohol packs never for picture-making, two topics, the guarded kit module listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_drinks.py
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import drinks_packs as d  # noqa: E402
import gaps_oi_packs as g  # noqa: E402

REPO = os.path.dirname(HERE)
NUMBERS = re.compile(r"\d+(\.\d+)?\s*(%|percent|proof|mg|milligrams|abv)", re.I)


def answers(specs):
    """Every answer of Commons specs."""
    return [a for spec in specs for _q, a in spec[2]]


def test_notes_in_commons_answers():
    for a in answers(d.ALCOHOLIC_DRINKS):
        assert a.endswith(d.ALCOHOL_NOTE) and a.startswith("It shows "), a
    for spec in d.DISTILLING:
        a = spec[2][0][1]
        assert a.startswith(d.DISTILLING_WARNING) or a.endswith(d.DISTILLERY_NOTE), a
    assert all(spec[2][0][1].startswith(d.DISTILLING_WARNING) for spec in d.DISTILLING
               if re.search(r"\bstills?\b|apparatus", spec[0], re.I))
    energy = [a for a in answers(d.SOFT_DRINKS) if "energy drink" in a]
    assert energy and all(a.endswith(d.CAFFEINE_NOTE) for a in energy)
    assert not any(d.ALCOHOL_NOTE in a for a in answers(d.SOFT_DRINKS))
    for a in answers(d.ALCOHOLIC_DRINKS + d.BAR_GLASSWARE + d.BREWING_WINEMAKING + d.SOFT_DRINKS):
        assert not NUMBERS.search(a.replace("26 U.S.C. 5601", "").replace("25.205 and 24.75", "")), a
    for text in (d.DISTILLING_WARNING, ):
        assert "26 U.S.C. 5601" in text and "New Zealand" in text and "methanol" in text and "pressure" in text
    apparatus = next(spec for spec in d.DISTILLING if spec[0] == "Distillation apparatus")
    assert apparatus[3].search("Copper whisky still") and not apparatus[3].search(
        "Automotive fractionating columns used for final purification of hydrocarbons")
    # the brand categories only keep files whose words say can, bottle or drink
    brand = next(spec for spec in d.SOFT_DRINKS if spec[0] == "Energy drinks by brand")
    assert brand[3].search("Red Bull can") and not brand[3].search("Red Bull Racing car")


def rows_of(labels, groups):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1))


def test_open_images_rows():
    rows = rows_of({"Red wine": 1, "Lager": 1, "Gin": 0}, d.BAR_DRINKS)
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What alcoholic drinks are in this picture?"] == f"I can see red wine and lager. {d.ALCOHOL_NOTE}"
    assert said["Is there any gin in this picture?"] == "No, I can't see any gin in this picture."
    rows = rows_of({"Caffeinated drink": 1}, d.SOFT)
    assert rows[0]["answer"] == f"I can see a caffeinated drink. {d.CAFFEINE_NOTE}"
    assert rows_of({"Barware": 1, "Nudity": 1}, d.BAR_DRINKS) == []


def test_bar_pack_leaves_out_children():
    entries = [("a.jpg", b"x", {"question": "q", "answer": "a"}),
               (None, None, {"question": "q2", "answer": "a2", "file": "pictures/a.jpg"}),
               ("b.jpg", b"y", {"question": "q", "answer": "a", "child": True}),
               (None, None, {"question": "q2", "answer": "a2", "child": True, "file": "pictures/b.jpg"}),
               ("c.jpg", b"z", {"question": "q", "answer": "a"})]
    kept = d.without_children(entries, 10)
    assert [e[0] for e in kept] == ["a.jpg", None, "c.jpg"]
    assert [e[0] for e in d.without_children(entries, 1)] == ["a.jpg", None]


def test_no_label_is_asked_twice():
    """Every Open Images label of the drinks packs is new: no other pack asks about it, and the two drinks packs
    share none."""
    import everyday_packs
    import home_packs
    import food_packs
    import culture_packs
    elsewhere = set(everyday_packs.OI_HOME) | set(food_packs.OI_FOOD) | set(culture_packs.OI_CULTURE)
    for grp in home_packs.OI_GROUP_QUESTIONS:
        elsewhere |= set(grp[0])
    import things_packs, packaged_goods_packs, med_vet_packs, people_activity_packs, disability_packs  # noqa: E401
    import world_life_packs, street_scene_packs  # noqa: E401
    for mod in (things_packs, packaged_goods_packs, med_vet_packs, people_activity_packs, disability_packs,
                world_life_packs, street_scene_packs):
        for name, value in vars(mod).items():
            if name.startswith("OI_") and isinstance(value, dict):
                elsewhere |= set(value)
    for groups in (g.PUBLIC_HOME, g.OUTINGS, g.FOOD_MORE, g.CARDS):
        elsewhere |= g.gap_labels(groups)
    for groups in (d.BAR_DRINKS, d.SOFT):
        assert not g.gap_labels(groups) & elsewhere, g.gap_labels(groups) & elsewhere
        for grp in groups:
            assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())
    assert not g.gap_labels(d.BAR_DRINKS) & g.gap_labels(d.SOFT)


def test_europeana_records():
    record = {"id": "/1/abc", "rights": ["http://creativecommons.org/publicdomain/zero/1.0/"], "language": ["en"],
              "title": ["Post Medieval Wine Bottle"], "edmIsShownBy": ["https://x/1.jpg"], "dataProvider": ["PAS"],
              "dcDescription": ["A complete dark green glass onion wine bottle of the late 17th century."]}
    pattern = d.EUROPEANA_DRINK_SEARCHES["wine bottle"]
    name, picture, rows = d.europeana_drink_item(record, "wine bottle", pattern)
    assert rows[0]["answer"].startswith("Post Medieval Wine Bottle. A complete dark green glass onion wine bottle")
    assert "search \"wine bottle\"" in rows[0]["credit"] and picture == "https://x/1.jpg"
    assert d.europeana_drink_item(dict(record, language=["nl"]), "wine bottle", pattern) is None
    assert d.europeana_drink_item(dict(record, rights=["http://creativecommons.org/licenses/by-nc/4.0/"]),
                                  "wine bottle", pattern) is None
    assert d.europeana_drink_item(dict(record, title=["A teapot"], dcDescription=["Silver."]), "wine bottle",
                                  pattern) is None
    still = dict(record, title=["Whisky distillery at Campbeltown"],
                 dcDescription=["A view of the still house of a Scottish whisky distillery, about 1890."])
    got = d.europeana_drink_item(still, "distillery", d.EUROPEANA_DRINK_SEARCHES["distillery"])
    assert got[2][0]["answer"].startswith(d.DISTILLING_WARNING)


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads drinks_sources at its end (and home_sources needs it)
    import drinks_sources as k
    assert (k.ALCOHOL_NOTE, k.CAFFEINE_NOTE, k.DISTILLING_WARNING) == (d.ALCOHOL_NOTE, d.CAFFEINE_NOTE,
                                                                       d.DISTILLING_WARNING)
    for category, _q, answer, _deeper in k.DRINKS_ALCOHOL_SA:
        assert answer.endswith(k.ALCOHOL_NOTE) or answer.startswith("This is") or \
            answer.startswith(k.DISTILLING_WARNING), category
    assert next(a for c, _q, a, _x in k.DRINKS_ALCOHOL_SA if c == "Pot stills").startswith(k.DISTILLING_WARNING)
    assert next(a for c, _q, a, _x in k.DRINKS_SOFT_SA if c == "Energy drinks").endswith(k.CAFFEINE_NOTE)
    assert "Open Food Facts (alcoholic beverages and every other drink category)" in k.DRINKS_NOT_INCLUDED


def test_wiring():
    keys = set(d.DRINKS_PACKS)
    assert keys == set(d.DRINKS_LIMITS) == set(d.DRINKS_ALCOHOL_KEYS) | set(d.DRINKS_SOFT_KEYS) and len(keys) == 8
    assert not set(d.DRINKS_ALCOHOL_KEYS) & set(d.DRINKS_SOFT_KEYS)
    assert keys <= set(build_packs.PACKS)
    assert set(d.DRINKS_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(d.DRINKS_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in d.DRINKS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import drinks_sources") == 2
    import sources
    import topics
    import drinks_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed) and all(listed[key].group == "permissive" for key in keys)
    assert {s.key for s in k.DRINKS_SOURCES} <= set(listed)
    assert all(listed[s.key].group == "share-alike" for s in k.DRINKS_SOURCES)
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    assert set(d.DRINKS_ALCOHOL_KEYS) <= no_making and "drinks_alcohol_commons_sa" in no_making
    assert "commons_soft_drinks" not in no_making and "drinks_soft_commons_sa" not in no_making
    assert "open_images_soft_drinks" in no_making
    # The soft drinks are in the food topic; the alcohol collections are in no topic (the owner's ten topics stay as
    # they are), so a topic add-on never learns alcohol by chance.
    in_topics = {key for t in topics.TOPICS for key in t.keys}
    assert set(d.DRINKS_SOFT_KEYS) | set(k.DRINKS_SOFT_KIT_KEYS) <= set(topics.find("food").keys)
    assert not (set(d.DRINKS_ALCOHOL_KEYS) | set(k.DRINKS_ALCOHOL_KIT_KEYS)) & in_topics
