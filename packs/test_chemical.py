"""A self-test of the household chemicals parsers (packs/chemical_packs.py, the safety notes of
packs/packaged_goods_packs.py and training-kit/kit/chemical_sources.py), with made-up records only: nothing is
downloaded from the internet.

It checks that:
  - the category rules name the product, the more particular rule first ("Bleach bottles" before "Bleach"), and add
    the right safety note, also asked on its own ("How do I handle this safely?");
  - look-alike categories are not taken for products or finishes (vacuum cleaners, the Rust Belt, rust fungi,
    Rust-Oleum's cans, kerosene heaters);
  - a brand is said only from the brand's own category AND when another rule said what the product is;
  - a symbol's meaning comes only from its own title or category, never when it names two classes; the nine GHS
    drawings of safety_signs are not taken again;
  - harm words (poisonings, drug labs, explosives, weapons) and nudity leave a file out;
  - abo_packaged_goods gives the safety notes to hazardous household listings only (not to food);
  - every pack is wired: in build_packs.PACKS and COMMONS_KEYS, in the workflows' known list and limit lines, in the
    kit's sources with the right groups and picture-making marks, and in the kit's topics.

Run it from the repository's folder:   python3 -m pytest packs/test_chemical.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import chemical_packs as c  # noqa: E402
import packaged_goods_packs as pg  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"
REPO = os.path.dirname(HERE)


def made_up(title="File:X.jpg", cats=(), text=""):
    """A made-up file as events_safety_packs.commons_files gives it."""
    return {"title": title, "url": "u", "credit": CREDIT, "licence": "CC BY 4.0", "categories": list(cats),
            "text": text}


def answers(rows):
    """{question: answer} of rows."""
    return {r["question"]: r["answer"] for r in rows}


def test_products_and_their_safety_notes():
    """The particular rule wins, and the safety note is added and asked on its own."""
    got = answers(c.rule_rows(["Bleach bottles", "Bleach"], c.RULES))
    assert got[c.WHAT_Q].startswith("This is a bottle of bleach. Keep it away from children")
    assert "Never mix bleach with ammonia" in got[c.SAFE_Q]
    got = answers(c.rule_rows(["Laundry detergent pods"], c.RULES))
    assert got[c.WHAT_Q].startswith("These are laundry detergent pods") and "look like sweets" in got[c.SAFE_Q]
    got = answers(c.rule_rows(["Propane cylinders in Canada"], c.RULES))
    assert "propane cylinder" in got[c.WHAT_Q] and "never store or use it indoors" in got[c.SAFE_Q]
    got = answers(c.rule_rows(["Carbon dioxide fire extinguishers"], c.RULES))
    assert "flammable liquid fires and electrical fires" in got[c.CLASS_Q] and c.SAFE_Q not in got
    got = answers(c.rule_rows(["Button cells"], c.RULES))
    assert "two hours" in got[c.SAFE_Q]
    assert answers(c.rule_rows(["Grass seed"], c.RULES)) == {c.WHAT_Q: "This is grass seed, for sowing a lawn."}
    # A general topic says "a picture of": the category holds the product, its container and its use.
    assert "a picture of a weed killer" in answers(c.rule_rows(["Herbicides"], c.RULES))[c.WHAT_Q]


def test_look_alike_categories():
    """Vacuum cleaners, the Rust Belt, rust fungi, Rust-Oleum and kerosene heaters are not what they sound like."""
    assert c.rule_rows(["Vacuum cleaners"], c.RULES) == []
    assert c.rule_rows(["Rust Belt"], c.FINISH_RULES) == []
    assert c.rule_rows(["Rust (fungus)"], c.FINISH_RULES) == []
    assert c.rule_rows(["Rust-Oleum"], c.FINISH_RULES) == []
    assert c.rule_rows(["Kerosene heaters"], c.RULES) == []
    assert "oil lamp" in answers(c.rule_rows(["Kerosene lamps"], c.RULES))[c.WHAT_Q]
    assert "rust" in answers(c.rule_rows(["Rusty cars"], c.FINISH_RULES))[c.SURFACE_Q]
    assert c.SKIP.search("Ball-and-stick models of acetone") and c.SKIP.search("Plant diseases caused by rust fungi")


def test_finishes():
    """Finishes and surfaces, with the oily-rag note for drying oils."""
    got = answers(c.rule_rows(["Linseed oil"], c.FINISH_RULES))
    assert "drying oil finish" in got[c.FINISH_Q] and "catch fire by themselves" in got[c.SAFE_Q]
    assert "zinc" in answers(c.rule_rows(["Hot-dip galvanizing"], c.FINISH_RULES))[c.FINISH_Q]
    assert "mirror-bright" in answers(c.rule_rows(["Chrome plating"], c.FINISH_RULES))[c.FINISH_Q]
    assert "lead" in answers(c.rule_rows(["Peeling paint"], c.FINISH_RULES))[c.SURFACE_Q]
    assert "smells musty" in answers(c.rule_rows(["Mold on walls"], c.FINISH_RULES))[c.SURFACE_Q]


def test_brand_only_from_its_category_and_with_a_product():
    """A brand needs its own category and a product rule; a brand category alone (a logo, a shop) gives nothing."""
    rows = c.file_rows(made_up(cats=["WD-40"]), "WD-40", c.RULES)
    got = answers(rows)
    assert got[c.BRAND_Q] == "The brand is WD-40." and "spray lubricant" in got[c.WHAT_Q]
    assert all(r["credit"] == CREDIT and r["facts"]["commons_category"] == "WD-40" for r in rows)
    assert c.brand_rows(["Clorox"], []) == []
    assert answers(c.file_rows(made_up(cats=["Clorox", "Bleach bottles"]), "Bleach bottles", c.RULES))[c.BRAND_Q] \
        == "The brand is Clorox."
    assert c.file_rows(made_up(cats=["Clorox"]), "Clorox", c.RULES) == []


def test_caption_row():
    """The file's own English caption is said; first-person stories and camera records are not."""
    rows = c.file_rows(made_up(text="A plastic jug of bleach on a laundry room shelf."), "Bleach bottles", c.RULES)
    assert answers(rows)[c.DESCRIBE_Q] == "A plastic jug of bleach on a laundry room shelf."
    assert c.caption_row("I bought this at my local store.") == []
    assert c.caption_row("IMG1234 camera model Canon") == []
    assert c.caption_row("Description NFPA 704 F4 S_none Author Borislav Mitev Programs ISIS/Draw 2.5 and MS Paint.") \
        == []
    assert c.caption_row("Original file description is/was here .") == []


def test_symbols():
    """Meanings from the file's own title or category only; never for two classes; GHS drawings left out."""
    rows = answers(c.symbol_rows(made_up("File:WHMIS Class B.svg", ["WHMIS symbols"]), "WHMIS symbols"))
    assert rows[c.SYMBOL_Q].startswith("This is the WHMIS 1988 symbol for Class B, flammable")
    assert "Canada" in rows[c.SYMBOL_KIND_Q]
    rows = answers(c.symbol_rows(made_up("File:WHMIS Class D-2.svg", ["WHMIS"]), "WHMIS"))
    assert "Class D2" in rows[c.SYMBOL_Q]
    assert c.SYMBOL_Q not in answers(c.symbol_rows(made_up("File:WHMIS Class A and B.svg", ["WHMIS"]), "WHMIS"))
    rows = answers(c.symbol_rows(made_up("File:Hazmat Class 3 Flammable Liquid placard.svg", ["Hazmat placards"]),
                                 "Hazmat placards"))
    assert rows[c.SYMBOL_Q] == "This is the hazardous materials placard for hazard class 3, flammable liquids."
    rows = answers(c.symbol_rows(made_up("File:Dangclass8.svg", ["Hazard placards"]), "Hazard placards"))
    assert "class 8, corrosive" in rows[c.SYMBOL_Q]
    assert c.SYMBOL_Q not in answers(c.symbol_rows(made_up("File:Placard class 3 and class 8.svg",
                                                           ["Hazmat placards"]), "Hazmat placards"))
    assert "fire diamond" in answers(c.symbol_rows(made_up("File:NFPA 704.svg", ["NFPA 704"]), "NFPA 704"))[
        c.SYMBOL_Q]
    assert c.symbol_rows(made_up("File:Some sign.svg", ["Signs"]), "Signs") == []
    assert c.GHS_DRAWINGS.search("File:GHS-pictogram-flamme.svg")
    rows = answers(c.symbol_rows(made_up("File:GHS05 corrosive label.jpg", ["GHS pictograms"]), "GHS pictograms"))
    assert rows[c.SYMBOL_Q].startswith("This is the GHS hazard pictogram GHS05: corrosive.")
    assert c.symbol_rows(made_up("File:GHS02 and GHS07 label.jpg", ["GHS pictograms"]), "GHS pictograms") == []
    assert c.SYMBOL_SKIP.search("GHS pictograms (Vector drawings)")
    # NFPA ratings only from the numbers in the file's own name; WHMIS classes from the words of the name.
    assert c.nfpa_rating("Nfpa_f4_none") == ("The flammability (red) square shows 4: it catches fire very easily and "
                                             "burns fiercely.")
    assert c.nfpa_rating("Nfpa_f0_w").endswith("it reacts dangerously with water.")
    assert c.nfpa_rating("NFPA diamonds comparison") == "" and c.nfpa_rating("NFPA 704") == ""
    rows = answers(c.symbol_rows(made_up("File:Nfpa_h2.svg", ["NFPA 704 images"]), "NFPA 704 images"))
    assert "health (blue) square shows 2" in rows[c.RATING_Q] and "fire diamond" in rows[c.SYMBOL_Q]
    rows = answers(c.symbol_rows(made_up("File:Dangerously Reactive 4585453038 .jpg", ["WHMIS hazard symbols"]),
                                 "WHMIS hazard symbols"))
    assert "Class F, dangerously reactive" in rows[c.SYMBOL_Q]


def test_harm_and_nudity_leave_a_file_out():
    """Everyday packs: no poisonings, drug labs, explosives, weapons or nudity."""
    assert c.refused("Meth lab chemicals seized") and c.refused("Fertilizer bomb")
    assert c.refused("Chemical weapons storage") and c.refused("Nude model with paint")
    assert c.refused("Child poisoning from detergent") and not c.refused("Bottle of bleach on a shelf")


def test_abo_safety_notes():
    """Hazardous household listings get a note; food and toiletries without hazard words do not."""
    assert "Never mix bleach" in pg.pg_hazard("CLEANING_AGENT", "household", "Presto! Bleach, 121 Fl Oz")
    assert "corrosive" in pg.pg_hazard("HEALTH_PERSONAL_CARE", "personal", "Presto! Toilet Cleaner, 500 Ml")
    assert "sweets" in pg.pg_hazard("LAUNDRY_DETERGENT", "household", "Solimo Laundry Detergent Pacs, 120 count")
    assert "recycling point" in pg.pg_hazard("AUTO_OIL", "household", "AmazonBasics Motor Oil 5W-30, 1 Quart")
    assert pg.pg_hazard("COFFEE", "drink", "Bleach Blonde Roast Coffee, 12 oz") == ""
    assert pg.pg_hazard("SHAMPOO", "personal", "Solimo Coconut Oil Shampoo, 13 fl oz") == ""


def test_wiring():
    """Every pack is in PACKS and COMMONS_KEYS, the workflows know them, the kit lists them with the right groups,
    the photo packs are never used for picture-making, and the topics hold them."""
    keys = set(c.CHEMICAL_PACKS)
    assert keys == set(c.CHEMICAL_LIMITS)
    assert keys <= set(build_packs.PACKS) and keys <= build_packs.COMMONS_KEYS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, limit in c.CHEMICAL_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import chemical_sources") == 2
    import sources
    import topics
    import chemical_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert keys | {"chemical_commons_sa"} <= set(listed)
    assert all(listed[key].group == "permissive" for key in keys)
    assert listed["chemical_commons_sa"].group == "share-alike"
    photo = {"commons_household_chemicals", "commons_finishes_in_use"}
    assert photo <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS) and photo <= set(sources.NOT_FOR_PICTURE_MAKING)
    assert "commons_hazard_symbols" not in sources.NOT_FOR_PICTURE_MAKING
    assert "chemical_commons_sa" in sources.NOT_FOR_PICTURE_MAKING and k.CHEMICAL_PICTURE_MAKING_OK == set()
    by_id = {t.id: set(t.keys) for t in topics.TOPICS}
    assert photo | {"chemical_commons_sa"} <= by_id["machines"] and "commons_hazard_symbols" in by_id["documents"]


def test_kit_share_alike_drops_harm(monkeypatch):
    """The kit's share-alike entry drops files whose words name harm."""
    import sources  # noqa: F401 - the kit's table first
    import chemical_sources as k
    made = [("chem-sa-Bleach.jpg", "u", {"question": "What is this?", "answer": "This is a bottle of bleach."}),
            ("chem-sa-Meth_lab_bleach.jpg", "u", {"question": "What is this?", "answer": "This is bleach."})]
    monkeypatch.setattr(k, "commons_sa_items", lambda *a, **kw: list(made))
    assert [i[0] for i in k.sa_items([], 10, 0, "chem-sa")] == ["chem-sa-Bleach.jpg"]
