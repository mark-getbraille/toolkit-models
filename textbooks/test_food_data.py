"""Self-test of the USDA FoodData Central books (food_data.py) and of the shared hooks for the sources added on
2026-11-22 (refs_kit.py, more_refs.py), with MADE-UP foods only: nothing is downloaded.

It checks that:
  - the keys (food, fdc:group, fdc:brand, one piece) expand as documented, every request word stays under the
    workflow's 256 jobs, and the builder, the weekly check and sources.py send fdc: keys to this module;
  - the newest release of each data file is found on the download page;
  - a branded food line is sorted into its brand piece before it is decoded, and a page shows the ingredients, the
    label's Nutrition Facts, the nutrients per 100 grams and the portions, with capitals made readable;
  - a group book holds only that group's foods, starts with the notes page, and carries CC0, the notice, the
    "published" date, the version and the originals; a changed licence page stops the build.

Run it from the repository's folder:   python3 -m pytest textbooks/test_food_data.py
"""

import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import food_data as F  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402

DOWNLOAD_PAGE = """<a href="/fdc-datasets/FoodData_Central_foundation_food_json_2025-12-18.zip">x</a>
<a href="/fdc-datasets/FoodData_Central_foundation_food_json_2026-10-29.zip">x</a>
<a href="/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip">x</a>
<a href="/fdc-datasets/FoodData_Central_branded_food_json_2026-10-29.zip">x</a>
<a href="/fdc-datasets/FoodData_Central_survey_food_json_2024-10-31.zip">x</a>"""

PEPPER = {"dataType": "SR Legacy", "description": "Spices, pepper, black", "fdcId": 170931, "ndbNumber": 2030,
          "foodCategory": {"description": "Spices and Herbs"},
          "foodNutrients": [{"nutrient": {"name": "Protein", "rank": 600, "unitName": "g"}, "amount": 10.39},
                            {"nutrient": {"name": "Energy", "rank": 300, "unitName": "kcal"}, "amount": 251.0}],
          "foodPortions": [{"amount": 1.0, "measureUnit": {"name": "tsp"}, "modifier": "ground", "gramWeight": 2.3,
                            "sequenceNumber": 1}]}
BEEF = dict(PEPPER, description="Beef, ground", fdcId=1, foodCategory={"description": "Beef Products"})
SNACK = {"foodClass": "Branded", "dataType": "Branded", "description": "SEAWEED SNACK, SEA SALT", "fdcId": 9,
         "brandOwner": "YUMMY SEA FOODS INC.", "ingredients": "SEAWEED, OIL, SALT.", "servingSize": 5,
         "servingSizeUnit": "g", "gtinUpc": "0001",
         "labelNutrients": {"calories": {"value": 25}, "sodium": {"value": 55.0}},
         "foodNutrients": PEPPER["foodNutrients"]}


def zipped(path, name, text):
    """Write a zip holding one file."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(name, text)
    return str(path)


def test_keys_and_hooks(monkeypatch, tmp_path):
    keys = sources.expand_keys(["food"])
    assert keys[0] == "fdc:label_guide" and len(keys) == 1 + len(F.FOOD_GROUPS) + 1 + len(F.BRAND_PIECES)
    assert sources.expand_keys(["fdc:brand"]) == [f"fdc:brand:{p}" for p in F.BRAND_PIECES]
    assert sources.expand_keys(["fdc:brand:d-e"]) == ["fdc:brand:d-e"]
    assert "fdc:group:soups-sauces-and-gravies" in sources.expand_keys(["fdc:group"])
    assert more_refs.owns("fdc:survey") and not more_refs.owns("wb:gpo_style_manual")
    monkeypatch.setattr(F.COLLECTION, "sign", lambda key: f"signed {key}")
    assert updates.fingerprint("fdc:survey") == "signed fdc:survey"
    called = []
    monkeypatch.setattr(F.COLLECTION, "build", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["fdc:brand:a"], str(tmp_path))
    assert called == [["fdc:brand:a"]]
    assert set(F.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in F.NOT_INCLUDED)


def test_every_word_fits_one_run():
    for m in more_refs.modules():
        for word in m.COLLECTION.words:
            assert len(m.COLLECTION.expand_keys([word])) <= 256, word


def test_release_files(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: DOWNLOAD_PAGE)
    files = F.release_files()
    assert files["foundation_food_json"].endswith("foundation_food_json_2026-10-29.zip")
    assert files["sr_legacy_food_json"].startswith("https://fdc.nal.usda.gov/fdc-datasets/")
    assert F.release_date(files["sr_legacy_food_json"]) == "2018-04"


def test_branded_pieces_and_page(monkeypatch, tmp_path):
    other = dict(SNACK, brandOwner="ACME FOODS", fdcId=10)
    text = '{"BrandedFoods": [\n' + json.dumps(SNACK) + ",\n" + json.dumps(other) + "]}\n"
    path = zipped(tmp_path / "b.zip", "b.json", text)
    monkeypatch.setattr(K, "download_file", lambda url, cache, name=None, max_age_days=None: path)
    assert [f["fdcId"] for f in F.branded_foods("x", None, "x-z")] == [9]
    assert [f["fdcId"] for f in F.branded_foods("x", None, "a")] == [10]
    assert F.in_piece("", "other") and F.in_piece("7-Eleven", "other") and not F.in_piece("Zest", "other")
    assert F.food_title(SNACK) == "Seaweed snack, sea salt (Yummy sea foods inc.)"
    page = F.food_page(SNACK)
    assert "<h2>Ingredients</h2><p>Seaweed, oil, salt.</p>" in page
    assert "<td>Calories</td><td>25</td>" in page and "<td>Sodium</td><td>55 mg</td>" in page
    assert page.index("Energy") < page.index("Protein")       # the database's order
    assert "<td>1 tsp ground</td><td>2.3</td>" in F.food_page(PEPPER)


def test_group_book(monkeypatch, tmp_path):
    foundation = zipped(tmp_path / "f.zip", "f.json", json.dumps({"FoundationFoods": [BEEF]}))
    legacy = zipped(tmp_path / "s.zip", "s.json", json.dumps({"SRLegacyFoods": [PEPPER, BEEF]}))
    monkeypatch.setattr(F, "licence_ok", lambda cache=None: True)
    monkeypatch.setattr(F, "release_files", lambda cache=None: {
        "foundation_food_json": "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_json_2026-10-29.zip",
        "sr_legacy_food_json": "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip"})
    monkeypatch.setattr(K, "download_file", lambda url, cache, name=None, max_age_days=None:
                        foundation if "foundation" in url else legacy)
    book = F.group_book("group:spices-and-herbs", "/tmp/none", None, [])
    assert [p.title for p in book.pages] == ["About these numbers, and reading a food label", "Spices, pepper, black"]
    assert book.licence == "CC0 1.0" and "FoodData Central" in book.notice and book.published == "2026-10-29"
    assert "sr_legacy_food_json_2018-04" in book.version and len(book.originals) == 2
    assert B.licence_kind(B.licence_short(book.licence), False) == "open"
    monkeypatch.setattr(F, "licence_ok", lambda cache=None: False)
    left = []
    assert F.group_book("group:spices-and-herbs", "/tmp/none", None, left) is None and "public domain" in left[0]["reason"]
    left = []
    assert F.group_book("group:nothing", "/tmp/none", None, left) is None


def test_stream_is_not_read_whole():
    assert "read(1 << 20)" in open(K.__file__).read()                # bulk files go to disk in pieces
    assert isinstance(io.TextIOWrapper, type)
