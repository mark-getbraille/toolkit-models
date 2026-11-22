"""A self-test of the home repair, pest control, heating and textile crafts packs (packs/home_upkeep_packs.py,
packs/heating_packs.py and packs/textile_crafts_packs.py) and the kit's collections for them
(training-kit/kit/home_crafts_sources.py), with made-up labels and records only: nothing is downloaded from the
internet.

It checks that:
  - answers about roofs, gutters and chimneys carry the ladder and roof note, engines the engine note, poisons and
    traps the pesticide and trap notes, wasps the sting note, power strips and wiring the electrical note, boilers the
    gas note, old paint and finishes the lead note, damp the mould note (the same words in the packs and the kit);
  - every heater, stove, fireplace, fuel, chimney and ash answer ends with the carbon monoxide, 3-feet and
    gas-professional note, kerosene answers say 1-K only and never gasoline, patio heaters and grills say outdoors
    only, and firewood answers carry the don't-move-firewood note;
  - the pest pack leaves out files whose words speak of dissection, blood or a carcass;
  - Open Images rows say only what the labels say, and no label of these packs is asked by another pack, nor by both;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - a made-up Smithsonian record is named from its own fields, and costumes, prints and records without a CC0
    picture are left out;
  - every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS (and only those), in the workflows'
    known list and limit lines, in the kit's sources (packs "permissive" with prepare_pack), never for picture-making
    unless the kit module says so, in the topics the kit module names, and the guarded kit module listed twice as a
    hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_home_crafts.py
"""

import glob
import importlib
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import heating_packs as w  # noqa: E402
import lighting_packs as li  # noqa: E402
import home_upkeep_packs as h  # noqa: E402
import textile_crafts_packs as t  # noqa: E402

REPO = os.path.dirname(HERE)
# Each pack file: (module, its packs, its limits, its Commons keys, its Commons specs, its Open Images groups).
MODULES = [
    (h, h.HOME_UPKEEP_PACKS, h.HOME_UPKEEP_LIMITS, h.HOME_UPKEEP_COMMONS_KEYS, h.HOME_UPKEEP_SPECS, [h.UPKEEP_OI]),
    (t, t.TEXTILE_CRAFTS_PACKS, t.TEXTILE_CRAFTS_LIMITS, t.TEXTILE_CRAFTS_COMMONS_KEYS, t.TEXTILE_CRAFTS_SPECS,
     [t.TEXTILE_OI]),
    (w, w.HEATING_PACKS, w.HEATING_LIMITS, w.HEATING_COMMONS_KEYS, w.HEATING_SPECS, [w.HEATING_OI]),
    (li, li.LIGHTING_PACKS, li.LIGHTING_LIMITS, li.LIGHTING_COMMONS_KEYS, li.LIGHTING_SPECS, [li.LIGHTING_OI]),
]


def answer_of(specs, category):
    """The first answer of a category's Commons spec."""
    return next(spec[2][0][1] for spec in specs if spec[0] == category)


def oi_rows(labels, groups):
    """oi_gap_rows with a fixed random order."""
    return g.oi_gap_rows(labels, groups, random.Random(1))


# ----------------------------------------------------------------- safety notes

def test_safety_notes_in_commons_answers():
    for category in ("Roofing", "Slate roofs", "Metal roofs", "Rain gutters", "Gutter guards", "Chimney sweeps",
                     "Window cleaning"):
        assert answer_of(h.HOME_REPAIR, category).endswith(h.LADDER_NOTE), category
    for category in ("Two-stroke engines", "Four-stroke engines", "Briggs & Stratton engines"):
        assert answer_of(h.LOCKS_ENGINES_BIKES, category).endswith(h.ENGINE_NOTE), category
    assert answer_of(h.HOME_REPAIR, "Power strips").endswith(h.POWER_STRIP_NOTE)
    assert answer_of(h.HOME_REPAIR, "Lead pipe plumbing").endswith(h.LEAD_PIPE_NOTE)
    assert answer_of(h.HOME_REPAIR, "Sanding").endswith(h.LEAD_PAINT_NOTE)
    assert answer_of(h.HOME_REPAIR, "Damp").endswith(h.MOULD_NOTE)
    rodenticide = answer_of(h.PEST_CONTROL, "Rodenticides")
    assert h.PESTICIDE_NOTE in rodenticide and rodenticide.endswith(h.TRAP_NOTE)
    for category in ("Rat traps", "Glue traps"):
        assert answer_of(h.PEST_CONTROL, category).endswith(h.TRAP_NOTE)
    assert answer_of(h.PEST_CONTROL, "Fumigation").endswith(h.FUMIGATION_NOTE)
    for category in ("Vespula vulgaris", "Polistes dominula"):
        assert answer_of(h.PEST_CONTROL, category).endswith(h.STING_NOTE)
    for text in (h.PESTICIDE_NOTE, ):
        assert "label" in text and "1-800-222-1222" in text
    assert "911" in h.GAS_NOTE and "carbon monoxide" in h.ENGINE_NOTE and "1978" in h.LEAD_PAINT_NOTE
    for category in ("Furniture restoration", "Varnishing"):
        assert answer_of(t.UPHOLSTERY_LEATHER_SHOES, category).endswith(t.FINISH_NOTE)
    assert "lead" in t.FINISH_NOTE


def test_open_images_notes_and_rows():
    said = {r["question"]: r["answer"] for r in oi_rows({"Electrical wiring": 1, "Switch": 1}, h.UPKEEP_OI)}
    assert said["What electrical things are in this picture?"] == ("I can see electrical wiring and a switch. "
                                                                   f"{h.ELECTRICAL_NOTE}")
    said = {r["question"]: r["answer"] for r in oi_rows({"Boiler": 1, "Snow blower": 1, "Lock": 0}, h.UPKEEP_OI)}
    assert said["What heating equipment is in this picture?"] == f"I can see a boiler. {h.GAS_NOTE}"
    assert said["What machines with engines are in this picture?"] == f"I can see a snow blower. {h.ENGINE_NOTE}"
    assert said["Is there a lock in this picture?"] == "No, I can't see a lock in this picture."
    said = {r["question"]: r["answer"] for r in oi_rows({"Embroidery": 1, "Lace": 1}, t.TEXTILE_OI)}
    assert said["What needlework or textile craft is in this picture?"] == "I can see embroidery and lace."
    assert oi_rows({"Quilt": 1, "Nudity": 1}, t.TEXTILE_OI) == []


def test_heating_notes():
    for spec in w.HOME_HEATING:
        answer = spec[2][0][1]
        assert answer.endswith(w.HEAT_SAFETY), spec[0]
    for words in ("carbon monoxide", "3 feet", "911", "grills or generators indoors", "qualified professional"):
        assert words in w.HEAT_SAFETY, words
    kerosene = answer_of(w.HOME_HEATING, "Kerosene heaters")
    assert w.KEROSENE_NOTE in kerosene and "1-K" in w.KEROSENE_NOTE and "never gasoline" in w.KEROSENE_NOTE
    assert w.OUTDOOR_ONLY in answer_of(w.HOME_HEATING, "Patio heaters")
    assert w.ASH_NOTE in answer_of(w.HOME_HEATING, "Ash buckets") and "metal can" in w.ASH_NOTE
    assert w.CHIMNEY_NOTE in answer_of(w.HOME_HEATING, "Chimney fires")
    assert w.ELECTRIC_NOTE in answer_of(w.HOME_HEATING, "Electric fireplaces")
    for category in ("Firewood", "Woodpiles", "Moisture meters"):
        assert answer_of(w.FIREWOOD, category).endswith(w.FIREWOOD_NOTE), category
    assert "emerald ash borer" in w.FIREWOOD_NOTE and "APHIS" in w.FIREWOOD_NOTE
    for category in ("Splitting mauls", "Splitting wedges"):
        assert answer_of(w.FIREWOOD, category).endswith(w.SPLITTING_NOTE)
    # the word filters keep hearth files and leave out pianos, ducts and wood preservative
    damper = next(spec for spec in w.HOME_HEATING if spec[0] == "Dampers")[3]
    assert damper.search("Cast iron chimney damper") and not damper.search("Piano damper felt")
    creosote = next(spec for spec in w.HOME_HEATING if spec[0] == "Creosote")[3]
    assert creosote.search("Creosote build-up in a stovepipe")
    assert not creosote.search("Creosote-treated railway sleepers")
    said = {r["question"]: r["answer"] for r in oi_rows({"Wood-burning stove": 1, "Barbecue grill": 1}, w.HEATING_OI)}
    assert said["What heating things are in this picture?"] == f"I can see a wood-burning stove. {w.HEAT_SAFETY}"
    assert "outdoors only" in said["Is there a grill in this picture?"]


def test_lighting_notes():
    """Every fuel lamp answer ends with the fuel note (or carries it), every candle answer with the candle note."""
    fuel = re.compile(r"\b(kerosene|hurricane|gas|carbide|safety lamp|oil lamp|lantern|wick|Betty|whale|Argand)",
                      re.I)
    for spec in li.EMERGENCY_LIGHTING:
        answer = spec[2][0][1]
        if re.search(r"candle|tealight", spec[0], re.I):
            assert answer.endswith(li.CANDLE_NOTE), spec[0]
        elif fuel.search(spec[0]):
            assert li.FUEL_LIGHT_NOTE in answer, spec[0]
        elif re.search(r"batter", spec[0], re.I):
            assert li.BATTERY_NOTE in answer, spec[0]
    for words in ("carbon monoxide", "ventilation", "never refuel", "hot or lit", "only the fuel"):
        assert words in li.FUEL_LIGHT_NOTE, words
    assert "unattended" in li.CANDLE_NOTE and "battery lights" in li.CANDLE_NOTE
    lantern = next(spec for spec in li.EMERGENCY_LIGHTING if spec[0] == "Lanterns")[3]
    assert lantern.search("Old kerosene lantern") and not lantern.search("Red paper lanterns at the Lantern Festival")
    glow = next(spec for spec in li.EMERGENCY_LIGHTING if spec[0] == "Chemiluminescence")[3]
    assert glow.search("Green glow sticks") and not glow.search("Luminol reaction in a flask")
    # nothing from before 1900, and no street lamps
    assert li.NOT_OLD.search("Petromax HK500 kerosene pressure lantern, lit")
    for words in ("Antique kerosene lamp", "Oil lamp, 1865", "Roman oil lamp in a museum"):
        assert not li.NOT_OLD.search(words), words
    assert not li.NOT_OLD_OR_STREET.search("Gas lamps on a street in London")
    assert not any(spec[0] in ("Gas lanterns", "Gas lamps") for spec in li.EMERGENCY_LIGHTING)    # street lamps
    assert not lantern.search("Victorian storm lantern")
    coleman = next(spec for spec in li.EMERGENCY_LIGHTING if spec[0] == "Coleman Company")[3]
    assert coleman.search("Coleman dual fuel lantern") and not coleman.search("Coleman cooler")
    assert not any(re.search(r"carbide|whale|betty|argand", spec[0], re.I) for spec in li.EMERGENCY_LIGHTING)
    said = {r["question"]: r["answer"] for r in oi_rows({"Oil lamp": 1}, li.LIGHTING_OI)}
    assert said["What fuel lamps are in this picture?"] == f"I can see an oil lamp. {li.FUEL_LIGHT_NOTE}"


def test_kit_heating_notes_match():
    import sources  # noqa: F401
    import home_crafts_sources as k
    assert (k.HEAT_SAFETY, k.FIREWOOD_NOTE) == (w.HEAT_SAFETY, w.FIREWOOD_NOTE)
    assert (k.FUEL_LIGHT_NOTE, k.CANDLE_NOTE) == (li.FUEL_LIGHT_NOTE, li.CANDLE_NOTE)
    # the reference books say the same heating words
    sys.path.insert(2, os.path.join(REPO, "textbooks"))
    import home_crafts as books
    assert books.HEAT_SAFETY == w.HEAT_SAFETY
    for category, _q, answer, _d in k.HOME_HEATING_SA:
        assert answer.endswith(k.HEAT_SAFETY) or answer.endswith(k.FIREWOOD_NOTE), category


def test_pest_pack_leaves_out_gore():
    weevil = next(spec for spec in h.PEST_CONTROL if spec[0] == "Sitophilus oryzae")
    pattern = weevil[3]
    assert pattern.search("Rice weevil on a grain of rice, close-up")
    for words in ("Dissected rat showing organs", "Dead rat in a gutter", "Flea full of blood", "Rat carcass"):
        assert not pattern.search(words), words
    assert all(spec[2][0][1].startswith("This looks like ") for spec in h.PEST_CONTROL if len(spec) > 3)


def test_no_numbers_or_sizes_made_up():
    """No answer states a size, count, fibre content or percentage (the sources give none); the notes' own numbers
    (the year 1978, 10 square feet, the phone numbers) are the only ones."""
    allowed = re.compile(r"1978|10 square feet|1-800-222-1222|911")
    for spec in h.HOME_UPKEEP_SPECS + t.TEXTILE_CRAFTS_SPECS:
        for _q, answer in spec[2]:
            assert not re.search(r"\d", allowed.sub("", answer)), answer


# ----------------------------------------------------------------- the Smithsonian textiles

def record(object_name, title, access="CC0", maker="Mary Smith", extra_label="Object Name"):
    """A made-up NMAH record in the shape of the Smithsonian open-access metadata."""
    return {"title": title, "content": {
        "freetext": {"objectType": [{"label": extra_label, "content": object_name}],
                     "name": [{"label": "maker", "content": maker}],
                     "date": [{"label": "date made", "content": "ca 1880"}],
                     "place": [{"label": "place made", "content": "United States: Ohio, Lancaster"}],
                     "physicalDescription": [{"label": "Physical Description",
                                              "content": "cotton (overall material)"},
                                             {"label": "Physical Description", "content": "silk (thread material)"}]},
        "descriptiveNonRepeating": {"record_ID": "nmah_1", "guid": "http://n2t.net/ark:/65665/ng1",
                                    "online_media": {"media": [{"type": "Images", "content": "https://ids.si.edu/x",
                                                                "usage": {"access": access}}]}}}}


def test_nmah_rows():
    url, rows = t.nmah_textile_row(record("quilt", "Log Cabin Quilt"))
    assert url == "https://ids.si.edu/x&max=2048"
    assert rows[0]["answer"] == ("This is a quilt (its record calls it \"Log Cabin Quilt\"), made by Mary Smith in "
                                 "Ohio, Lancaster, ca 1880. Its record gives its materials: cotton, silk (thread).")
    assert rows[1]["question"] == "What is it made of?" and "CC0" in rows[0]["credit"]
    _url, rows = t.nmah_textile_row(record("sewing machine patent model", "Wheeler Sewing Machine Patent Model"))
    assert rows[0]["answer"].startswith("This is a sewing machine (a patent model)")
    assert t.nmah_textile_row(record("quilt", "Quilt", access="Usage conditions apply")) is None
    assert t.nmah_textile_row(record("costume", "Embroidered dress")) is None
    assert t.nmah_textile_row(record("print", "Quilting party")) is None
    assert t.nmah_textile_row(record("teapot", "Teapot")) is None
    _url, rows = t.nmah_textile_row(record("sampler", "Sampler", maker="Unknown"))
    assert "made by" not in rows[0]["answer"] and ", made in Ohio" in rows[0]["answer"]


# ----------------------------------------------------------------- shared checks

def asked_elsewhere():
    """Every Open Images label another pack file asks about: the keys of its OI_... dictionaries, the labels of its
    gaps_oi_packs-style groups, and home_packs' group questions (every *_packs.py file but those of MODULES)."""
    ours = {m[0].__name__ for m in MODULES}
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


def test_no_open_images_label_is_asked_twice():
    elsewhere = asked_elsewhere()
    mine = [groups for m in MODULES for groups in m[5]]
    for groups in mine:
        assert not g.gap_labels(groups) & elsewhere, g.gap_labels(groups) & elsewhere
        for grp in groups:
            assert grp["question"].endswith("?") and all(w and w == w.strip() for w in grp["things"].values())
    for i, a in enumerate(mine):
        for b in mine[i + 1:]:
            assert not g.gap_labels(a) & g.gap_labels(b)
    # trades that judge people by their work are never asked
    assert not {"Electrician", "Roofer", "Handyman", "Bicycle mechanic", "Cobbler"} & set().union(
        *(g.gap_labels(x) for x in mine))


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    ours = {os.path.abspath(m[0].__file__) for m in MODULES}
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) not in ours and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    seen = set()
    for m in MODULES:
        for spec in m[4]:
            category = spec[0]
            assert category not in seen, category
            seen.add(category)
            assert f'"{category}"' not in others, f"{category} is used by another pack"


def test_kit_notes_match():
    import sources  # noqa: F401 - loaded first: it loads home_crafts_sources at its end
    import home_crafts_sources as k
    for name in ("LADDER_NOTE", "ENGINE_NOTE", "PESTICIDE_NOTE", "TRAP_NOTE", "MOULD_NOTE"):
        assert getattr(k, name) == getattr(h, name), name
    sa = {c: a for c, _q, a, _d in k.HOME_UPKEEP_SA}
    assert sa["Rain gutters"].endswith(k.LADDER_NOTE) and sa["Two-stroke engines"].endswith(k.ENGINE_NOTE)
    assert sa["Rat traps"].endswith(k.TRAP_NOTE) and k.PESTICIDE_NOTE in sa["Rodenticides"]
    # every share-alike category is one of the packs' own categories
    pack_categories = {spec[0] for m in MODULES for spec in m[4]}
    for category, _q, _a, _d in k.HOME_UPKEEP_SA + k.TEXTILE_CRAFTS_SA + k.HOME_HEATING_SA + k.EMERGENCY_LIGHTING_SA:
        assert category in pack_categories, category
    assert "Ravelry (patterns, yarns and project photos)" in k.HOME_CRAFTS_NOT_INCLUDED
    assert "Pinterest" in k.HOME_CRAFTS_NOT_INCLUDED


def test_wiring():
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    assert kit_yml.count("--hidden-import home_crafts_sources") == 2
    import sources
    import topics
    import home_crafts_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    all_keys = set()
    for _mod, packs, limits, commons_keys, _specs, _groups in MODULES:
        keys = set(packs)
        assert keys == set(limits) and not keys & all_keys
        all_keys |= keys
        assert keys <= set(build_packs.PACKS)
        assert set(commons_keys) <= keys and set(commons_keys) <= build_packs.COMMONS_KEYS
        assert not (keys - set(commons_keys)) & build_packs.COMMONS_KEYS
        for key, limit in limits.items():
            assert f'"{key}"' in packs_yml, key
            assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
            assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
            assert listed[key].cap == limit, key
            assert (key in no_making) == (key not in k.HOME_CRAFTS_PICTURE_MAKING_OK), key
    kit_keys = {s.key for s in k.HOME_CRAFTS_SOURCES}
    assert all_keys <= kit_keys
    for s in k.HOME_CRAFTS_SOURCES:
        assert s.key in listed
        assert (s.group == "permissive") == (s.key in all_keys), s.key
    assert {"home_upkeep_commons_sa", "textile_crafts_commons_sa", "home_heating_commons_sa",
            "emergency_lighting_commons_sa"} <= kit_keys
    assert listed["home_upkeep_commons_sa"].group == "share-alike"
    # the topics: exactly as the kit module says, and every collection in at least one
    in_topics = set()
    for topic_id, keys in k.HOME_CRAFTS_TOPICS.items():
        topic = topics.find(topic_id)
        assert set(keys) <= set(topic.keys), (topic_id, set(keys) - set(topic.keys))
        in_topics |= set(keys)
    assert kit_keys == in_topics
    mine = kit_keys
    for topic in topics.TOPICS:
        assert {key for key in topic.keys if key in mine} <= set(k.HOME_CRAFTS_TOPICS.get(topic.id, ())), topic.id
    # pests and poisons, people at work and Open Images photos are never for picture-making
    assert {"commons_pest_control", "open_images_home_upkeep", "open_images_textile_crafts",
            "commons_home_repair", "commons_home_heating", "open_images_home_heating"} <= no_making
    assert "commons_fabrics_fibres" not in no_making
