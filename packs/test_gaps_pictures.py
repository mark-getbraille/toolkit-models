"""A self-test of the personal care, toys and world money packs (packs/personal_care_packs.py, packs/toys_packs.py,
packs/world_money_packs.py) and the kit's collections (training-kit/kit/personal_care_sources.py, toys_sources.py,
world_money_sources.py), with made-up titles and labels only: nothing is downloaded from the internet.

It checks that:
  - the safety notes say what the owner asked (FDA: patch test, never dye eyebrows or eyelashes; Poison Help; CPSC:
    small parts, button batteries, magnets, ride-ons, playgrounds, baby walkers, recalls) and every answer that
    names such a thing carries its note, in the packs and the kit alike, with the same words;
  - the word filters keep products and leave out people (personal care) and children (toys, nursery: a baby
    walker is kept, a baby is not);
  - the money answers name only what the category and the file's title say, take only money dated 1930 or earlier,
    and leave out banknote files showing both sides;
  - Open Images: no label of these packs is asked by another pack nor twice here, and photos with a leave-out label
    (a child, a face) are dropped as the label lists are read;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: build_packs.PACKS, COMMONS_KEYS (the Commons ones only), the workflows' known list and limit
    lines, the kit's sources (packs "permissive", prepare_pack; the share-alike entries "share-alike"), never for
    picture-making, in the home or documents topic, the guarded kit modules listed twice as hidden imports, and the
    Met themed objects left to these packs by met_collection.

Run it from the repository's folder:   python3 -m pytest packs/test_gaps_pictures.py
"""

import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import personal_care_packs as pc  # noqa: E402
import toys_packs as ty  # noqa: E402
import world_money_packs as wm  # noqa: E402

REPO = os.path.dirname(HERE)
MINE = (pc, ty, wm)


def answers(specs):
    """(category, answer) of every Commons spec."""
    return [(spec[0], a) for spec in specs for _q, a in spec[2]]


def answer_of(specs, category):
    """The answer of one category."""
    return next(a for c, a in answers(specs) if c == category)


# ----------------------------------------------------------------- the notes

def test_notes_say_what_the_owner_asked():
    assert "patch test" in pc.HAIR_DYE_NOTE and "eyebrows or eyelashes" in pc.HAIR_DYE_NOTE
    assert "1-800-222-1222" in pc.POISON_NOTE and "FDA" in pc.COSMETIC_NOTE
    assert "under 3" in ty.SMALL_PARTS_NOTE and "two hours" in ty.BATTERY_NOTE and "emergency" in ty.MAGNET_NOTE
    assert "helmet" in ty.RIDE_NOTE and "surfacing" in ty.PLAYGROUND_NOTE and "stairs" in ty.WALKER_NOTE
    assert "SaferProducts.gov" in ty.RECALL_NOTE


def test_every_answer_carries_its_notes():
    for category, answer in answers(pc.PERSONAL_CARE_SPECS) + answers(ty.TOYS_SPECS):
        assert answer.startswith("This is ") and answer.endswith("."), category
    assert pc.HAIR_DYE_NOTE in answer_of(pc.PRODUCTS, "Hair dyes")
    for category in ("Straight razors", "Razor blades", "Nail scissors"):
        assert pc.BLADE_NOTE in answer_of(pc.PRODUCTS, category), category
    for category in ("Perfumes", "Eau de Cologne", "Colognes", "Chanel No. 5", "Nail art"):
        assert pc.FLAME_NOTE in answer_of(pc.PRODUCTS, category), category
    for category, answer in answers(ty.TOYS):
        assert ty.RECALL_NOTE in answer or "not food" in answer, category
    assert ty.BATTERY_NOTE in answer_of(ty.TOYS, "Toy robots")
    for category, answer in answers(ty.RIDE_ONS):
        if re.search(r"tricycle|ride-on|wagon|pedal", answer.split(".")[0], re.I):
            assert ty.RIDE_NOTE in answer, category
        if re.search(r"playground|swing|slide|seesaw|jungle", answer.split(".")[0], re.I):
            assert ty.PLAYGROUND_NOTE in answer, category
    assert ty.WALKER_NOTE in answer_of(ty.NURSERY, "Baby walkers")
    assert ty.SLEEP_NOTE in answer_of(ty.NURSERY, "Cradles")
    # answers name no brand the category does not, and no made-up figure
    for _category, answer in answers(pc.PERSONAL_CARE_SPECS):
        rest = answer
        for note in (pc.COSMETIC_NOTE, pc.HAIR_DYE_NOTE, pc.HEAT_NOTE, pc.FLAME_NOTE, pc.BLADE_NOTE, pc.POISON_NOTE):
            rest = rest.replace(note, "")
        assert not re.search(r"\d", rest.replace("Chanel No. 5", "")), answer


def test_word_filters():
    keep, out = pc.NO_PERSON.search, lambda words: not pc.NO_PERSON.search(words)
    assert keep("Vintage perfume bottle on a shelf") and keep("Straight razor with an ivory handle")
    assert out("Woman applying lipstick") and out("Portrait of a model") and out("Kid with bubble bath")
    assert ty.NO_PLAYING.search("Wooden toy truck, 1950s") and not ty.NO_PLAYING.search("Boys playing with blocks")
    assert not ty.NO_PLAYING.search("Family on a seesaw")
    assert ty.NO_CHILD.search("Baby walker from the 1970s") and ty.NO_CHILD.search("Old wooden cradle")
    assert not ty.NO_CHILD.search("Baby sleeping in a cradle") and not ty.NO_CHILD.search("Toddler in a walker")
    for spec in pc.PERSONAL_CARE_SPECS:
        assert spec[3] is pc.NO_PERSON, spec[0]
    for spec in ty.TOYS + ty.RIDE_ONS + ty.MUSEUM_TOYS:
        assert spec[3] is ty.NO_PLAYING, spec[0]
    for spec in ty.NURSERY:
        assert spec[3] is ty.NO_CHILD, spec[0]


def test_met_themes():
    assert pc.met_themed({"objectName": "Kohl tube"}) and pc.met_themed({"objectName": "Perfume bottle"})
    assert ty.met_themed({"objectName": "Doll"}) and ty.met_themed({"objectName": "Rattle"})
    assert wm.met_themed({"objectName": "Coin"}) and wm.met_themed({"objectName": "Tetradrachm"})
    assert not any(m.met_themed({"objectName": "Painting"}) for m in MINE)
    import museum_general_packs as mg
    record = {"isPublicDomain": True, "primaryImage": "x.jpg", "objectName": "Coin", "title": "Stater", "tags": []}
    assert mg.met_excluded(record).startswith("a themed object")
    assert mg.met_excluded(dict(record, objectName="Bowl")) == ""


# ----------------------------------------------------------------- money

def rows(title, kind="coin", country="Japan", sub="", categories=()):
    """world_money_rows of a made-up file."""
    return wm.world_money_rows(title, "", list(categories), {"info": (kind, country)}, sub)


def test_money_rows():
    got = rows("1920 Japan 1 yen obverse", sub="1 yen coins")
    assert got == [{"question": wm.MONEY_Q, "answer": "This is the front (obverse) of a 1 yen coin of Japan, dated "
                                                      "1920."}]
    assert rows("1990 Japan 5 yen reverse", sub="5 yen coins") == []          # modern money is left out
    assert rows("Japan 5 yen reverse", sub="5 yen coins") == []               # no date: left out
    assert rows("1985 and 1920 coins") == []                                  # two dates: left out
    note = rows("Mexico 1915 10 pesos banknote front", "note", "Mexico", "Banknotes of Mexico")
    assert note and note[0]["answer"] == "This is the front (obverse) of a banknote of Mexico, dated 1915."
    assert rows("Mexico 1915 10 pesos banknote front and back", "note", "Mexico") == []
    assert rows("1915 fake banknote front", "note", "Mexico") == []
    nnc = rows("1795-USA-half-dime-r", "coin", "", wm.NNC)
    assert nnc[0]["answer"] == ("This is the back (reverse) of a coin from the Smithsonian's National Numismatic "
                                "Collection, dated 1795.")
    assert rows("1800 eight reales coin", sub="8 reales coins")[0]["answer"].startswith("This is an 8 reales coin")
    assert wm.is_note(note) and not wm.is_note(nnc)
    assert wm.OLD_UNTIL == 1930


# ----------------------------------------------------------------- Open Images

def asked_elsewhere():
    """Every Open Images label another pack file asks about (as packs/test_outdoor_cooking.py reads them)."""
    mine = {m.__name__ for m in MINE}
    elsewhere = set()
    for path in sorted(glob.glob(os.path.join(HERE, "*_packs.py"))):
        name = os.path.basename(path)[:-3]
        if name in mine:
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
    groups = pc.CARE_OI + ty.TOYS_OI + wm.MONEY_OI
    labels = [label for grp in groups for label in grp["things"]]
    assert len(labels) == len(set(labels))
    assert not set(labels) & asked_elsewhere(), set(labels) & asked_elsewhere()
    for grp in groups:
        assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())
    assert not set(labels) & set(pc.PEOPLE_LABELS) and not set(labels) & set(ty.NO_PEOPLE_LABELS)


def test_leave_out_labels_are_dropped_while_reading(monkeypatch):
    """oi_gap_labels with extra labels: a photo whose labels are all extra ones is not kept; one with a wanted
    label keeps its extra labels (so build_oi_gap can leave it out)."""
    lines = ["ImageID,Source,LabelName,Confidence", "a1,human,/m/lego,1", "a1,human,/m/person,1",
             "b2,human,/m/person,1", "b2,human,/m/face,1", "c3,human,/m/lego,1"]
    monkeypatch.setattr(g, "oi_lines", lambda s, url: iter(lines))
    got = g.oi_gap_labels(None, {"/m/lego": "Lego", "/m/person": "Person", "/m/face": "Human face"}, quick=True,
                          extra={"Person", "Human face"})
    assert got == {"a1": {"Lego": 1, "Person": 1}, "c3": {"Lego": 1}}


# ----------------------------------------------------------------- Commons categories

def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    mine = {os.path.abspath(m.__file__) for m in MINE}
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) not in mine and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for spec in pc.PERSONAL_CARE_SPECS + ty.TOYS_SPECS] + wm.WORLD_MONEY_CATEGORIES
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


# ----------------------------------------------------------------- the kit

def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads the kit modules at its end
    import personal_care_sources as kp
    import toys_sources as kt
    import world_money_sources as kw
    for name in ("COSMETIC_NOTE", "HAIR_DYE_NOTE", "FLAME_NOTE", "BLADE_NOTE", "POISON_NOTE"):
        assert getattr(kp, name) == getattr(pc, name), name
    for name in ("SMALL_PARTS_NOTE", "MAGNET_NOTE", "BATTERY_NOTE", "RIDE_NOTE", "RECALL_NOTE", "TOY_NOTES"):
        assert getattr(kt, name) == getattr(ty, name), name
    pack_categories = {spec[0] for spec in pc.PERSONAL_CARE_SPECS}
    for category, _q, _a, _d in kp.PERSONAL_CARE_SA:
        assert category in pack_categories, category
    toy_categories = {spec[0] for spec in ty.TOYS_SPECS}
    for category, _q, _a, _d in kt.TOYS_SA:
        assert category in toy_categories, category
    for table in (kp.PERSONAL_CARE_NOT_INCLUDED, kt.TOYS_NOT_INCLUDED, kw.WORLD_MONEY_NOT_INCLUDED):
        assert table and all(reason for reason in table.values())
    assert "Open Beauty Facts" in kp.PERSONAL_CARE_NOT_INCLUDED
    assert any("Strong" in k for k in kt.TOYS_NOT_INCLUDED) and any("V&A" in k for k in kt.TOYS_NOT_INCLUDED)
    assert any("Australian" in k for k in kw.WORLD_MONEY_NOT_INCLUDED)


def test_wiring():
    packs = {**pc.PERSONAL_CARE_PACKS, **ty.TOYS_PACKS, **wm.WORLD_MONEY_PACKS}
    limits = {**pc.PERSONAL_CARE_LIMITS, **ty.TOYS_LIMITS, **wm.WORLD_MONEY_LIMITS}
    commons = set(pc.PERSONAL_CARE_COMMONS_KEYS) | set(ty.TOYS_COMMONS_KEYS) | set(wm.WORLD_MONEY_COMMONS_KEYS)
    keys = set(packs)
    assert keys == set(limits) and len(keys) == 13
    assert keys <= set(build_packs.PACKS)
    assert commons <= build_packs.COMMONS_KEYS and not (keys - commons) & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in limits.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    for module in ("personal_care_sources", "toys_sources", "world_money_sources"):
        assert kit_yml.count(f"--hidden-import {module} ") == 2, module
    import sources
    import topics
    import personal_care_sources as kp
    import toys_sources as kt
    import world_money_sources as kw
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    home, documents = set(topics.find("home").keys), set(topics.find("documents").keys)
    for s in kp.PERSONAL_CARE_SOURCES + kt.TOYS_SOURCES + kw.WORLD_MONEY_SOURCES:
        assert s.key in listed and s.key in no_making, s.key
        assert s.key in keys or s.group == "share-alike", s.key
        if s.key in keys:
            assert s.group == "permissive" and s.prepare is sources.prepare_pack, s.key
    for s in kp.PERSONAL_CARE_SOURCES + kt.TOYS_SOURCES:
        assert s.key in home, s.key
    for s in kw.WORLD_MONEY_SOURCES:
        assert s.key in documents, s.key
    assert not (kp.PERSONAL_CARE_PICTURE_MAKING_OK or kt.TOYS_PICTURE_MAKING_OK or kw.WORLD_MONEY_PICTURE_MAKING_OK)
