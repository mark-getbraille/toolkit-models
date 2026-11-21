"""A guard: no code of the packs or the kit fetches the Open Food Facts family of websites.

Why: world.openfoodfacts.org and its country sites, static and images.openfoodfacts.org, Open Beauty Facts, Open
Products Facts and Open Pet Food Facts share one robots.txt that shuts out GPTBot, anthropic-ai, ClaudeBot and
Claude-Web ("Disallow: /") and disallows /api and /cgi to every robot; search.openfoodfacts.org disallows every robot
(checked 2026-11-21). The owner's rule is that such blocks are obeyed. Open Food Facts is read instead through the
routes it publishes for bulk reuse, which are not blocked (kit/off_dump.py): its product database on Hugging Face
(openfoodfacts/product-database, ODbL) and its photos on AWS Open Data (the openfoodfacts-images bucket, CC BY-SA).
Open Beauty, Products and Pet Food Facts have no open route for their photos, so their entries are not built
(home_sources.HOME_BLOCKED_SOURCES; the code is kept and stops at once).

It checks that:
  - no Python file of the packs, the kit, tools or scripts has an address on those sites in its code (comments and
    docstrings may name them, to explain why they are not used), except the ones shown to people and never fetched:
    a site's home page and terms page and a product's page ("https://world.openfoodfacts.org/product/{code}") in a
    credit line. A bare host name in a sentence ("search.openfoodfacts.org disallows every robot") is not an address.
    Test files (test_*.py) are not looked at: they hold made-up records. The manuals folder is not looked at either:
    manuals/build_manuals.py has its own Open Food Facts reader, outside the packs and the kit (the owner was told it
    reads the same blocked hosts);
  - no workflow, command or shell script has an address on those sites;
  - the kit's reader builds photo addresses on AWS only, keeps the photo licence (share-alike) and the data's ODbL
    credit, and the code kept for the blocked sites stops before it reads anything;
  - the Open Beauty, Products and Pet Food Facts entries are not offered by the kit, and say why.

Run it from the training-kit folder:   xvfb-run -a python3 -m pytest -q tests/test_no_off_sites.py
"""

import ast
import gzip
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit")
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, KIT)
import off_dump  # noqa: E402

# Every host of the family, with or without "https://" and a path after it.
ADDRESS = re.compile(r"(https?://)?(?:[a-z0-9-]+\.)*open(?:food|beauty|products|petfood)facts\.org(/[^\s'\"),;]*)?",
                     re.I)
# The addresses code may hold: shown to people (a home page, the terms page, a product's page), never fetched.
SHOWN = re.compile(r"^(https://)?world\.open(food|beauty|products|petfood)facts\.org(/terms-of-use|/product/(\{code\})?)?/?$",
                   re.I)
# Folders not looked at (see the module docstring).
SKIP_DIRS = {".git", "__pycache__", "node_modules", "manuals"}


def python_files():
    """Every Python file of the repository except the tests (test_*.py) and the skipped folders."""
    for top, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py") and not f.startswith("test_"):
                yield os.path.join(top, f)


def code_strings(path):
    """[(line, text)] of the string constants in a Python file's code, leaving out docstrings (which may explain why
    the sites are not read). The pieces of an f-string are included."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body \
                and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            docs.add(id(node.body[0].value))
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs]


def bad_addresses(text):
    """The addresses in a text that could be fetched: with "https://" or a path, and not one that is only shown."""
    out = []
    for m in ADDRESS.finditer(text):
        if (m.group(1) or m.group(2)) and not SHOWN.match(m.group(0).rstrip(".")):
            out.append(m.group(0))
    return out


def test_the_rule_itself():
    """Fetchable addresses are caught; the shown ones and bare host names in sentences are not."""
    assert bad_addresses("https://search.openfoodfacts.org/search")
    assert bad_addresses("https://world.openfoodfacts.org/api/v2/product/")
    assert bad_addresses("https://images.openbeautyfacts.org/images/products/")
    assert bad_addresses("static.openfoodfacts.org/data/openfoodfacts-products.jsonl.gz")
    assert bad_addresses("https://world.openpetfoodfacts.org/api/v2/search")
    assert not bad_addresses("Open Food Facts contributors, https://world.openfoodfacts.org/product/{code}")
    assert not bad_addresses("Photos CC BY-SA 3.0 (world.openfoodfacts.org/terms-of-use)")
    assert not bad_addresses("https://world.openbeautyfacts.org")
    assert not bad_addresses("its robots.txt (images.openfoodfacts.org, search.openfoodfacts.org) blocks them")


def test_no_code_fetches_the_off_sites():
    """No fetchable address on the Open ... Facts websites in the code of the packs, the kit, tools or scripts."""
    problems = []
    for path in python_files():
        for line, text in code_strings(path):
            for address in bad_addresses(text):
                problems.append(f"{os.path.relpath(path, REPO)}:{line}: {address}")
    assert not problems, "Code that could fetch the Open Food Facts websites:\n" + "\n".join(problems)


def test_no_script_names_the_sites():
    """No workflow, Windows command or shell script has an address on the Open ... Facts websites."""
    problems = []
    for top, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for f in files:
            if f.endswith((".yml", ".yaml", ".cmd", ".bat", ".sh", ".ps1")):
                path = os.path.join(top, f)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    if bad_addresses(fh.read()):
                        problems.append(os.path.relpath(path, REPO))
    assert not problems, problems


def test_photos_come_from_aws_open_data():
    """A product's chosen photo is the uploaded photo of that number in the AWS Open Data bucket."""
    images = {"front_en": {"imgid": 3, "rev": 9}, "ingredients_fr": {"imgid": 5, "rev": 2}}
    aws = "https://openfoodfacts-images.s3.eu-west-3.amazonaws.com/data/"
    assert off_dump.photo_url("4012359114303", images, "front") == aws + "401/235/911/4303/3.jpg"
    assert off_dump.photo_url("20065034", images, "front") == aws + "20065034/3.jpg"
    assert off_dump.photo_url("4012359114303", images, "ingredients") == ""
    assert off_dump.photo_url("4012359114303", images, "ingredients", "fr").endswith("/4303/5.jpg")
    assert off_dump.photo_url("4012359114303", {"front_en": {"rev": 9}}, "front") == ""
    assert off_dump.front_photo({"code": "4012359114303", "images": images}, ("de", "en")).endswith("/3.jpg")


def test_a_database_row_is_kept_in_the_old_shape():
    """A Hugging Face row becomes the record the kit's entries read: names, English categories, chosen photos."""
    row = {"code": "0011161160410", "brands": "Brand", "quantity": "430 g", "lang": "en", "unique_scans_n": None,
           "product_name": [{"lang": "main", "text": "Oats"}, {"lang": "en", "text": "Oats"}],
           "countries_tags": ["en:united-states"], "categories_tags": ["en:breakfast-cereals", "fr:avoine", "en:null"],
           "images": [{"key": "1", "imgid": None, "rev": None}, {"key": "front_en", "imgid": 1, "rev": 4},
                      {"key": "packaging_en", "imgid": 2, "rev": 5}]}
    hit = off_dump.slim(row, 7)
    assert hit["product_name"] == hit["product_name_en"] == "Oats" and hit["unique_scans_n"] == 0
    assert hit["categories_tags"] == ["en:breakfast-cereals"] and hit["group"] == 7
    assert hit["images"] == {"front_en": {"imgid": 1, "rev": 4}}
    assert off_dump.slim(dict(row, categories_tags=["en:null"]), 7) is None
    assert off_dump.slim(dict(row, images=[]), 7) is None
    assert off_dump.slim(dict(row, product_name=[]), 7) is None
    assert off_dump.texts([{"lang": "en", "text": '<span class="allergen">MILK</span>, sugar'}]) == \
        {"en": "MILK, sugar"}
    assert off_dump.nutriments([{"name": "fat", "100g": 3.5}, {"name": "salt", "100g": None}]) == {"fat_100g": 3.5}


def test_the_most_scanned_products_of_each_label(tmp_path):
    """top_by_label reads the slim copy and keeps the most scanned of each label (ties by barcode)."""
    folder = tmp_path / off_dump.CACHE / "abc"
    folder.mkdir(parents=True)
    rows = [{"code": f"{n:013d}", "unique_scans_n": n % 4, "categories_tags": ["en:teas" if n % 2 else "en:jams"],
             "images": {"front_en": {"imgid": 1}}, "group": 0} for n in range(10)]
    with gzip.open(folder / "part-0000.jsonl.gz", "wt", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in rows))
    (folder / "complete").write_text("ok\n")
    best = off_dump.top_by_label(str(tmp_path), lambda h: [t[3:] for t in h["categories_tags"]], 2)
    assert [h["code"][-1] for h in best["teas"]] == ["3", "7"]
    assert [h["code"][-1] for h in best["jams"]] == ["2", "6"]


def test_the_slim_copy_and_details_from_a_parquet_file(tmp_path, monkeypatch):
    """build_cache reads the light columns of every row group (here a small local Parquet file standing in for the
    Hugging Face one), and details reads the ingredients and nutrition of chosen products only."""
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    fsspec = pytest.importorskip("fsspec")
    rows = [{"code": f"{n:013d}", "brands": "B", "quantity": "1 kg", "lang": "en", "unique_scans_n": n,
             "product_name": [{"lang": "main", "text": f"Product {n}"}],
             "countries_tags": ["en:canada"], "categories_tags": ["en:teas"],
             "images": [{"key": "front_en", "imgid": 1, "rev": 2}] if n % 3 else [],
             "ingredients_text": [{"lang": "en", "text": "tea leaves"}],
             "nutriments": [{"name": "fat", "100g": 0.5}]} for n in range(9)]
    pq.write_table(pa.Table.from_pylist(rows), str(tmp_path / "food.parquet"), row_group_size=3)
    monkeypatch.setattr(off_dump, "revision", lambda: "0123456789abcdef")
    monkeypatch.setattr(off_dump, "open_file", lambda rev: (fsspec.filesystem("file"), str(tmp_path / "food.parquet")))
    monkeypatch.setattr(off_dump, "PART", 2)
    work = str(tmp_path / "work")
    kept = list(off_dump.products(work))
    assert sorted(h["code"][-1] for h in kept) == ["1", "2", "4", "5", "7", "8"]
    assert {h["group"] for h in kept} == {0, 1, 2}
    assert off_dump.cache_folder(work).endswith("0123456789ab")
    facts = off_dump.details(work, [h for h in kept if h["code"].endswith("4")])
    assert facts == {"0000000000004": {"ingredients_text_en": "tea leaves", "ingredients_text": "",
                                       "nutriments": {"fat_100g": 0.5}}}


def test_entries_keep_their_licences():
    """The Open Food Facts entries stay share-alike (CC BY-SA photos) and credit the ODbL data and the product."""
    import sources
    for key in ("openfoodfacts", "openfoodfacts_labels", "openfacts_us", "openfacts_ca", "openfacts_supplements"):
        source = next(s for s in sources.SOURCES if s.key == key)
        assert source.group == "share-alike" and "CC BY-SA 3.0" in source.licence and "ODbL" in source.licence
    import extra_sources
    assert "ODbL" in extra_sources.OFF_CREDIT and "/product/{code}" in extra_sources.OFF_CREDIT


def test_blocked_sites_are_not_built():
    """Open Beauty, Products and Pet Food Facts are not offered, say why, and their kept code stops at once."""
    import home_sources
    import sources
    blocked = {s.key for s in home_sources.HOME_BLOCKED_SOURCES}
    assert blocked == {"openbeautyfacts", "openbeautyfacts_labels", "openproductsfacts", "openproductsfacts_labels",
                       "openpetfoodfacts", "openpetfoodfacts_labels"}
    offered = {s.key for s in sources.SOURCES}
    assert not blocked & offered and not blocked & {s.key for s in home_sources.HOME_SOURCES}
    assert all(not site[1] for site in home_sources.FACT_SITES.values())
    for name, why in home_sources.HOME_NOT_INCLUDED.items():
        if "Facts" in name:
            assert why.startswith("Not built: the source blocks AI crawlers")
    assert off_dump.NOT_BUILT.startswith("not built: the source blocks AI crawlers")
    with pytest.raises(RuntimeError, match="not built: the source blocks AI crawlers"):
        home_sources.facts_products("beauty", "shampoos", 5)
    with pytest.raises(RuntimeError, match="blocks AI crawlers"):
        home_sources.facts_image("petfood", "0000000000001", {"front_en": {"rev": 1}}, "front", "en")
    import canada_sources
    import us_sources
    with pytest.raises(RuntimeError, match="blocks AI crawlers"):
        us_sources.us_site_items("beauty", 5)
    with pytest.raises(RuntimeError, match="blocks AI crawlers"):
        canada_sources.ca_site_items("products", 5)
