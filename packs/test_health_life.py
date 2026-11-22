"""A self-test of the health and life picture packs (packs/mental_health_packs.py, fitness_nutrition_packs.py,
sexual_health_packs.py, aging_care_packs.py, wilderness_first_aid_packs.py) and the kit's lists of them
(training-kit/kit/*_sources.py of the same names), with made-up file words only: nothing is downloaded.

It checks that:
  - every answer ends with its health note, and each note has the same words as the reference books' notes
    (textbooks/mental_health.py and the others): not medical advice or a diagnosis, 911, and 988 (the wilderness
    note: the SOS of a messenger or PLB, not training, take a course);
  - the sexual health safety filter takes product and packaging files and refuses body parts, sexual words,
    demonstration models, worn or used products and children; the incontinence and rescue filters do the same;
  - no Commons category of these packs is named by another pack file, nor twice here;
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflows' known list and limit lines, in the
    kit's sources (permissive, prepare_pack), the guarded kit modules listed twice as hidden imports, no picture-making, the people packs in
    PEOPLE_AND_BODILY_PACK_KEYS, the sexual health pack in no topic,
    the food guides in the food topic and the others in the home topic.

Run it from the repository's folder:   python3 -m pytest packs/test_health_life.py
"""

import glob
import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(REPO, "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import mental_health_packs as MH  # noqa: E402
import fitness_nutrition_packs as FN  # noqa: E402
import sexual_health_packs as SH  # noqa: E402
import aging_care_packs as AC  # noqa: E402
import wilderness_first_aid_packs as WF  # noqa: E402

# (pack module, its packs, limits, Commons keys, specs, note, kit module name, kit prefix)
MODULES = [
    (MH, MH.MENTAL_HEALTH_PACKS, MH.MENTAL_HEALTH_LIMITS, MH.MENTAL_HEALTH_COMMONS_KEYS, MH.MENTAL_HEALTH_SPECS,
     MH.HEALTH_NOTE, "mental_health_sources", "MENTAL_HEALTH"),
    (FN, FN.FITNESS_NUTRITION_PACKS, FN.FITNESS_NUTRITION_LIMITS, FN.FITNESS_NUTRITION_COMMONS_KEYS,
     FN.FITNESS_NUTRITION_SPECS, FN.FIT_NOTE, "fitness_nutrition_sources", "FITNESS_NUTRITION"),
    (SH, SH.SEXUAL_HEALTH_PACKS, SH.SEXUAL_HEALTH_LIMITS, SH.SEXUAL_HEALTH_COMMONS_KEYS, SH.SEXUAL_HEALTH_SPECS,
     SH.SEX_NOTE, "sexual_health_sources", "SEXUAL_HEALTH"),
    (AC, AC.AGING_CARE_PACKS, AC.AGING_CARE_LIMITS, AC.AGING_CARE_COMMONS_KEYS, AC.AGING_CARE_SPECS, AC.AGING_NOTE,
     "aging_care_sources", "AGING_CARE"),
    (WF, WF.WILDERNESS_FIRST_AID_PACKS, WF.WILDERNESS_FIRST_AID_LIMITS, WF.WILDERNESS_FIRST_AID_COMMONS_KEYS,
     WF.WILDERNESS_FIRST_AID_SPECS, WF.WILD_NOTE, "wilderness_first_aid_sources", "WILDERNESS_FIRST_AID"),
]


def textbook_note(name, variable):
    """A note string of a module of the textbooks folder, read from its source without importing it (the textbooks
    have their own "sources" module, which must not replace the kit's here)."""
    import ast
    with open(os.path.join(REPO, "textbooks", f"{name}.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == variable for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(variable)


def test_notes_match_the_books():
    books = {MH: textbook_note("mental_health", "HEALTH_NOTE"), FN: textbook_note("fitness_nutrition", "NOTE"),
             SH: textbook_note("sexual_health", "NOTE"), WF: textbook_note("wilderness_first_aid", "NOTE")}
    for mod, note in books.items():
        mine = next(n for m, *_rest, n, _k, _p in MODULES if m is mod)
        assert mine == note, mod.__name__
    for mod, *_rest, note, _k, _p in MODULES:
        assert note.startswith("General information, not") and "call 911" in note, mod.__name__
        if mod is WF:
            assert "SOS" in note and "not training" in note and "wilderness first aid course" in note
        else:
            assert note.endswith("in a mental health crisis call or text 988."), mod.__name__
    assert "1-800-QUIT-NOW" in MH.QUIT_NOTE


def test_every_answer_ends_with_its_note():
    for mod, _p, _l, _c, specs, note, _k, _px in MODULES:
        for spec in specs:
            for question, answer in spec[2]:
                assert question.endswith("?") and answer.startswith("This is ") and answer.endswith(note), spec[0]
                assert "diagnos" not in answer.replace(note, ""), spec[0]
    nicotine = [a for s in MH.WELLBEING_AIDS if s[0].startswith("Nicotine") for _q, a in s[2]]
    assert nicotine and all(MH.QUIT_NOTE in a for a in nicotine)


def test_safety_filters():
    safe = SH.SAFE_WORDS
    for words in ("Durex condom box on a shelf", "Copper IUD (intrauterine device) package",
                  "Mirena IUD device on a table", "Tampons in their applicators", "OraQuick HIV self-test kit",
                  "Emergency contraception pill pack levonorgestrel", "Menstrual cup, silicone, washable"):
        assert safe.search(words), words
    for words in ("Condom demonstration on a penis model", "Condom on a banana", "Used tampon with blood",
                  "Menstrual cup inserted", "Woman wearing period underwear", "IUD in the uterus, ultrasound",
                  "Sex education poster with genitals", "Teen girl holding a condom", "Nude art with condom",
                  "Condoms\nsexual health clinic"):
        assert not safe.search(words), words
    for spec in SH.CONTRACEPTION_MENSTRUAL:
        assert spec[3] is SH.SAFE_WORDS, spec[0]
    pads = next(s for s in AC.DAILY_LIVING_AIDS if s[0] == "Incontinence pads")[3]
    assert pads.search("Incontinence pads in a pack") and not pads.search("Man wearing incontinence pad")
    guide = FN.GUIDE_ONLY
    assert guide.search("Foodpyramid.jpg") and guide.search("MyPlate icon, USDA graphic")
    assert not guide.search("Secretary Vilsack answers questions at the announcement of MyPlate")
    assert all(s[3] is guide for s in FN.FOOD_GUIDES)
    rescue = next(s for s in WF.WILDERNESS_RESCUE if s[0] == "Mountain rescue")[3]
    assert rescue.search("Mountain rescue team training with a stretcher")
    assert not rescue.search("Injured climber evacuated after accident") and not rescue.search("Body recovered")
    assert not rescue.search("Ouch (49350088282).jpg")              # a live build found this title on a rescue sled
    assert next(s for s in WF.WILDERNESS_RESCUE if s[0] == "Rescue sleds")[3] is rescue


def test_no_commons_category_is_used_by_another_pack():
    """No category of these packs is named (in quotes) by another pack file, nor twice here."""
    mine = {os.path.abspath(m.__file__) for m, *_r in MODULES}
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.abspath(path) not in mine and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    names = [spec[0] for _m, _p, _l, _c, specs, *_r in MODULES for spec in specs]
    assert len(names) == len(set(names))
    for name in names:
        assert f'"{name}"' not in others, name


def test_wiring():
    import sources
    import topics
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    listed = {s.key: s for s in sources.SOURCES}
    by_topic = {t.id: set(t.keys) for t in topics.TOPICS}
    every_topic = set().union(*by_topic.values())
    for mod, packs, limits, commons, _specs, _note, kit_name, prefix in MODULES:
        keys = set(packs)
        assert keys == set(limits) == set(commons), mod.__name__
        assert keys <= set(build_packs.PACKS) and keys <= build_packs.COMMONS_KEYS, mod.__name__
        assert kit_yml.count(f"--hidden-import {kit_name}") == 2, kit_name
        kit = importlib.import_module(kit_name)
        ok = getattr(kit, f"{prefix}_PICTURE_MAKING_OK")
        bodily = set(getattr(kit, f"{prefix}_BODILY_KEYS", ()))
        assert {s.key for s in getattr(kit, f"{prefix}_SOURCES")} == keys, kit_name
        assert all(reason for reason in getattr(kit, f"{prefix}_NOT_INCLUDED").values()), kit_name
        for key, limit in limits.items():
            assert f'"{key}"' in packs_yml, key
            assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
            assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
            assert listed[key].content == "", key                  # products and gear: never a content mark
            assert (key in sources.NOT_FOR_PICTURE_MAKING) == (key not in ok or key in bodily), key
            assert (key in sources.PEOPLE_AND_BODILY_PACK_KEYS) == (key in bodily), key
    assert MH.MENTAL_HEALTH_PACKS and set(FN.FITNESS_NUTRITION_PACKS) - {"commons_food_guides"} <= by_topic["home"]
    assert "commons_food_guides" in by_topic["food"]
    for key in ("commons_wellbeing_aids", "commons_daily_living_aids", "commons_wilderness_rescue"):
        assert key in by_topic["home"], key
    assert "commons_contraception_menstrual" not in every_topic          # the owner's choice: no topic
    for sensitive in ("nudity", "sexual"):
        assert not set(SH.SEXUAL_HEALTH_PACKS) & by_topic[sensitive]
