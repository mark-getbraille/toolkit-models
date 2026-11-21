"""A self-test of the food ripeness and quality packs (packs/food_quality_packs.py), with made-up file names and a
made-up spreadsheet only: nothing is downloaded. It checks that:
  - the avocado stage comes only from the makers' spreadsheet (its header found by name), and stages outside 1 to 5
    are left out; the small .xlsx reader reads shared strings and numbers;
  - the banana stage comes only from the folder of the ORIGINAL ripeness photos (never the augmented copies);
  - the FruitNet fruit and quality come from its folders (the "Lemon" folder of the mixed part is the lime), and a
    folder whose quality word disagrees with its part is left out;
  - take_even gives an even share of each group;
  - the packs are wired: build_packs.PACKS (not the Commons lane), the workflows' known list and limit lines, and the
    training kit's sources and food topic.

Run it from the repository's folder:   python3 -m pytest packs/test_food_quality.py
"""

import io
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(REPO, "training-kit", "kit"))
import build_packs  # noqa: E402 - loaded first, as the builders expect
import food_quality_packs as fq  # noqa: E402


def made_up_xlsx(rows):
    """A tiny .xlsx (bytes) whose first sheet holds rows: text cells as shared strings, numbers as numbers."""
    strings, xml_rows = [], []
    for r, row in enumerate(rows, 1):
        cells = []
        for c, value in enumerate(row, 1):
            ref = f"{fq.col_letters(c)}{r}"
            if isinstance(value, (int, float)):
                cells.append(f'<c r="{ref}"><v>{value}</v></c>')
            else:
                strings.append(value)
                cells.append(f'<c r="{ref}" t="s"><v>{len(strings) - 1}</v></c>')
        xml_rows.append(f'<row r="{r}">{"".join(cells)}</row>')
    ns = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("xl/sharedStrings.xml", f'<sst {ns}>' + "".join(f"<si><t>{t}</t></si>" for t in strings) + "</sst>")
        z.writestr("xl/worksheets/sheet1.xml", f'<worksheet {ns}><sheetData>{"".join(xml_rows)}</sheetData></worksheet>')
    return out.getvalue()


def test_xlsx_reader_and_avocado_stages():
    data = made_up_xlsx([["File Name", "Time Stamp", "Storage Group", "Ripening Index Classification"],
                         ["T20_d01_001_a_1", "2022-04-04", "T20", 1],
                         ["T20_d09_001_a_4", "2022-04-12", "T20", 4],
                         ["T20_d20_001_a_9", "2022-04-23", "T20", 9],
                         ["", "2022-04-23", "T20", 2]])
    rows = fq.xlsx_rows(data)
    assert rows[1] == ["T20_d01_001_a_1", "2022-04-04", "T20", "1"]
    assert fq.avocado_stages(rows) == {"T20_d01_001_a_1": "1", "T20_d09_001_a_4": "4"}
    assert fq.avocado_stages([["Name", "Stage"], ["x", "1"]]) == {}
    assert fq.AVOCADO_STAGES["4"].startswith("Yes: it is ripe") and "end of its shelf life" in fq.AVOCADO_STAGES["4"]
    assert fq.col_number("AA") == 27 and fq.col_letters(27) == "AA"


def test_banana_stage_only_from_original_photos():
    assert fq.banana_stage("Banana Ripeness Detection Dataset/Semi-ripe/a.jpg") == "semi-ripe"
    assert fq.banana_stage("Banana Ripeness Detection Dataset/Overripe/b.jpg") == "overripe"
    assert fq.banana_stage("Augmented Banana Ripeness Detection Dataset/Ripe/c.jpg") == ""
    assert fq.banana_stage("Banana Classification Dataset/Sagor Kola/d.jpg") == ""


def test_fruitnet_labels_and_answers():
    assert fq.fruitnet_label("Bad Quality_Fruits/Apple_Bad/IMG1.jpg") == ("apple", "bad")
    assert fq.fruitnet_label("Good Quality_Fruits/Pomegranate_Good/IMG2.jpg") == ("pomegranate", "good")
    assert fq.fruitnet_label("Mixed Qualit_Fruits/Lemon/IMG3.jpg") == ("lime", "mixed")
    assert fq.fruitnet_label("Good Quality_Fruits/Apple_Bad/IMG4.jpg") is None
    assert fq.fruitnet_label("Bad Quality_Fruits/Mango_Bad/IMG5.jpg") is None
    assert fq.fruitnet_answer("apple", "good") == "This is an apple of good quality, as the dataset's makers sorted it."
    assert "rotten or mouldy" in fq.fruitnet_answer("guava", "bad") and "a guava" in fq.fruitnet_answer("guava", "bad")
    assert "mixed quality" in fq.fruitnet_answer("lime", "mixed")


def test_take_even():
    got = fq.take_even({"a": list(range(10)), "b": [100, 101], "c": list(range(200, 210))}, 9, 1)
    assert len(got) == 9 and {100, 101} <= set(got)
    assert abs(sum(1 for x in got if x < 10) - sum(1 for x in got if x >= 200)) <= 1


def test_wiring():
    keys = set(fq.FOOD_QUALITY_PACKS)
    assert keys == set(fq.FOOD_QUALITY_LIMITS)
    assert keys <= set(build_packs.PACKS) and not keys & build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    for key, limit in fq.FOOD_QUALITY_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    import sources
    import topics
    listed = {s.key: s for s in sources.SOURCES}
    assert all(listed[k].group == "permissive" for k in keys)
    assert keys <= {k for t in topics.TOPICS if t.id == "food" for k in t.keys}
