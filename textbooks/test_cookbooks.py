"""Self-tests of cookbooks.py (the cookbooks and recipes books) with made-up pages only: nothing is downloaded. They
check that a recipe page of each site is read into its ingredients (with their groups), steps (with tips), times
and servings and nutrition facts; that category pages are passed over; that the recipe book has an A to Z index and
groups by kind of dish; that the UK practice note, the safety notices and the old-book note are on the right
books; that a site blocking AI readers is not read; that the links-only book copies no recipe text; and that the
keys reach the builder.

Run it from the repository's folder:   python3 -m pytest textbooks/test_cookbooks.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import cookbooks as C  # noqa: E402
import sources  # noqa: E402

NHLBI_PAGE = """<main><article class="node node--type-recipe"><h1><span>Made-up Bean Soup</span></h1>
<div class="field"><p><strong>A warm soup for cold days.</strong></p><p>Recipe Source: <em>Test Cookbook</em></p>
<h2>Ingredients</h2><ul><li>1 C dry beans</li><li>&frac14; tsp salt</li></ul><h2>Directions</h2>
<ol><li>Soak the beans.</li><li>Simmer for 1 hour.</li></ol></div>
<table class="cooking-facts"><tbody><tr><th>Prep Time</th><td><div>10 minutes</div></td></tr>
<tr><th>Yields</th><td><div>4 servings</div></td></tr></tbody></table>
<table class="health-facts"><thead><tr><th colspan="2">Nutritional Facts</th></tr></thead><tbody>
<tr><th>Calories</th><td><div>120</div></td></tr><tr><th>Sodium</th><td><div>150 mg</div></td></tr></tbody></table>
</article></main>"""

NHS_PAGE = """<main><h1>Made-up courgette bake recipe</h1><div><p>A tasty bake.</p><p>Prep: 10 mins<br/>Serves 2</p>
</div><details><summary><span>Nutritional information</span></summary><div><p>Per serving</p><ul><li>200kcal</li>
</ul></div></details><figure><img src="x.png" alt=""></figure><h2>Ingredients</h2><h3>Topping</h3><ul>
<li>50g cheese</li></ul><h3>Bake</h3><ul><li>1 courgette</li></ul><h2>Method</h2><ol><li><p>Slice the courgette.</p>
<div class="nhsuk-inset-text"><span class="nhsuk-u-visually-hidden">Information: </span><p>Leave the skin on.</p>
</div></li><li><p>Bake at 180C, gas mark 4.</p></li></ol><h2>More recipes</h2><h3>Other bake</h3></main>
<script type="application/ld+json">{"@type": "Recipe", "name": "x", "recipeCategory": ["Dinner"],
"recipeIngredient": ["50g cheese", "1 courgette"]}</script>"""


def test_nhlbi_recipe():
    r = C.nhlbi_recipe(NHLBI_PAGE, "https://www.nhlbi.nih.gov/x")
    assert r["title"] == "Made-up Bean Soup" and r["group"] == "Soups and stews"
    body = r["body"]
    assert "<h2>Ingredients</h2><ul><li>1 C dry beans</li><li>¼ tsp salt</li></ul>" in body
    assert "<ol><li>Soak the beans.</li><li>Simmer for 1 hour.</li></ol>" in body
    assert "<h2>Time and servings</h2><ul><li>Prep Time: 10 minutes</li><li>Yields: 4 servings</li></ul>" in body
    assert "<h2>Nutrition facts (per serving)</h2><ul><li>Calories: 120</li><li>Sodium: 150 mg</li></ul>" in body
    assert "Recipe Source: <em>Test Cookbook</em>" in body and "class=" not in body
    assert C.nhlbi_recipe("<main><article><h1>News</h1><p>No recipe</p></article></main>", "u") is None


def test_nhs_recipe():
    r = C.nhs_recipe(NHS_PAGE, "https://www.nhs.uk/healthier-families/recipes/x/")
    assert r["title"] == "Made-up courgette bake" and r["group"] == "Dinner"
    body = r["body"]
    assert "<h2>Nutritional information</h2><p>Per serving</p><ul><li>200kcal</li></ul>" in body
    assert "<h3>Topping</h3><ul><li>50g cheese</li></ul><h3>Bake</h3>" in body
    assert "<li>Slice the courgette. Tip: Leave the skin on.</li>" in body
    assert "gas mark 4" in body and "More recipes" not in body and "Other bake" not in body and "<img" not in body
    assert C.nhs_recipe("<main><h1>Breakfast</h1><p>Category page</p></main>", "u") is None


def test_dish_groups():
    assert C.dish_group("Baked Salmon Dijon") == "Fish and seafood"
    assert C.dish_group("20-Minute Chicken Creole") == "Chicken and turkey"
    assert C.dish_group("Apple Coffee Cake") == "Baking and desserts"
    assert C.dish_group("Mystery") == "Other dishes"


def fake_site(monkeypatch, pages, robots=""):
    """B.fetch answers from pages (robots.txt from robots), and our reader is allowed everywhere."""
    def fetch(url, cache=None, **kw):
        if url.endswith("/robots.txt"):
            return robots
        return pages[url]
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    C._ai.clear()


def test_recipe_book(monkeypatch, tmp_path):
    entry = C.BY_NAME["nhlbi_heart_healthy_recipes"]
    base = C.NHLBI_RECIPES
    listing = f'<a href="/health/heart-healthy-living/healthy-foods/healthy-eating-recipes/bean-soup">x</a>' \
              f'<a href="/health/heart-healthy-living/healthy-foods/healthy-eating-recipes/baked-fish">y</a>'
    fish = NHLBI_PAGE.replace("Made-up Bean Soup", "Baked Fish")
    fake_site(monkeypatch, {f"{base}?page=0": listing, f"{base}?page=1": listing,
                            f"{base}/bean-soup": NHLBI_PAGE, f"{base}/baked-fish": fish,
                            C.NHLBI_POLICY: "<p>Most of the information on the NHLBI website is in the public domain "
                                            "and can be used without restriction.</p>"})
    left = []
    book = C.recipes_book(entry, None, left)
    assert [(p.unit, p.title) for p in book.pages] == [
        ("", "About this book"), ("", "A to Z recipe index"), ("Fish and seafood", "Baked Fish"),
        ("Soups and stews", "Made-up Bean Soup")]
    index = book.pages[1].body
    assert index.index("Baked Fish") < index.index("Made-up Bean Soup") and "<h2>B</h2>" in index
    assert book.group == "cookbooks" and book.subject.startswith("Cooking: special diets")
    assert "Original recipe: <a href" in book.pages[2].body and not left
    entry_out = B.write_book(book, str(tmp_path), versioned=True)
    assert entry_out["licence_kind"] == "open" and entry_out["article_count"] >= 5
    guide = C.library_book(C.BY_NAME["cookbooks_library_guide"], [book])
    rows = next(p for p in guide.pages if p.path == "recipe-index").body
    assert "Baked Fish: in Heart-healthy recipes (NHLBI)" in rows
    assert any("usda-2015_en" in p.body for p in guide.pages)


def test_licence_gone_and_ai_block(monkeypatch):
    entry = C.BY_NAME["nhs_healthier_families_recipes"]
    fake_site(monkeypatch, {C.NHS_POLICY: "<p>All rights reserved.</p>"})
    left = []
    assert C.recipes_book(entry, None, left) is None and "no longer states" in left[0]["reason"]
    fake_site(monkeypatch, {}, robots="User-agent: ClaudeBot\nDisallow: /\n")
    left = []
    assert C.recipes_book(entry, None, left) is None and "AI" in left[0]["reason"]
    fake_site(monkeypatch, {}, robots="User-agent: *\nContent-Signal: search=yes, ai-train=no\nAllow: /\n")
    assert C.ai_refused("https://example.org/x")
    fake_site(monkeypatch, {}, robots="User-agent: *\nAllow: /\n")
    assert not C.ai_refused("https://example.org/x")


def test_notices():
    uk = C.make_book(C.BY_NAME["nhs_healthier_families_recipes"])
    assert "gas marks" in B.practice_note_of(uk) and "courgette is zucchini" in B.index_page(uk)
    us = C.make_book(C.BY_NAME["nhlbi_heart_healthy_recipes"])
    assert B.practice_note_of(us) == "" and us.notice == ""
    canning = C.make_book(C.BY_NAME["old_everywomans_canning_book_1918"])
    assert "pressure canner" in canning.notice and "published in 1918" in canning.notice
    assert "open-kettle" in canning.notice and B.esc(canning.notice) in B.index_page(canning)
    smoke = C.make_book(C.BY_NAME["old_practical_small_smokehouse_for_fish_1918"])
    assert "165 °F" in smoke.notice and "Old book" in smoke.notice
    assert "pasteurised" in C.make_book(C.BY_NAME["old_cheese_making_decker_1905"]).notice
    assert "curing salt" in C.make_book(C.BY_NAME["old_secrets_of_meat_curing_1922"]).notice
    army = C.make_book(C.BY_NAME["army_recipes_tm_10_412_1946"])
    assert "published in 1946" in army.notice


def test_links_book_copies_nothing(monkeypatch):
    page = ('<h1>Canning</h1><p>Some copyright text about canning.</p>'
            '<a href="/how/can/canning-fruits-and-fruit-products/applesauce/">Applesauce</a>'
            '<a href="/how/can/general-information/for-safetys-sake/">For Safety\'s Sake</a>')
    pages = {f"{C.NCHFP}/how/{m}": (page if m == "can" else "<p>nothing</p>") for m, _n in C.NCHFP_METHODS}
    fake_site(monkeypatch, pages)
    book = C.nchfp_book(C.BY_NAME["nchfp_preserving_links"])
    can = next(p for p in book.pages if p.title == "Canning")
    assert '<a href="https://nchfp.uga.edu/how/can/canning-fruits-and-fruit-products/applesauce/">Applesauce</a>' in can.body
    assert "<h2>Canning fruits and fruit products</h2>" in can.body and "Some copyright text" not in can.body
    assert B.licence_kind(book.licence) == "open" and "pressure canner" in book.notice


def test_books_and_keys():
    names = [b["name"] for b in C.BOOKS]
    assert len(names) == len(set(names)) and all(b["topic"] in C.TOPICS for b in C.BOOKS)
    for b in C.BOOKS:
        if b["kind"] == "pdf" and b.get("old_public_domain"):
            assert int(b["published"]) < 1931 and "old book" in b["description"]
        assert B.licence_kind(B.licence_short(b.get("licence", "CC0 1.0"))) or \
            B.licence_kind(b.get("licence", "CC0 1.0")), b["name"]
    covered = {b["topic"] for b in C.BOOKS}
    assert {"everyday", "baking", "smoking", "preserving", "dairy", "sausage", "mealplan", "budget", "diets",
            "safety"} <= covered
    keys = sources.expand_keys(["cookbooks"])
    assert keys == [f"cook:{n}" for n in names] and sources.expand_keys(["cook:nhlbi_week_on_dash"]) == \
        ["cook:nhlbi_week_on_dash"]
    assert "cookbooks" in sources.GROUPS
    merged = B.merge([])
    assert any("MyPlate" in x["title"] for x in merged["not_included"]) and "nchfp_links" in merged["licence_lines"]
    assert merged["kiwix_labels"]["usda-2015_en"].startswith("public domain")
