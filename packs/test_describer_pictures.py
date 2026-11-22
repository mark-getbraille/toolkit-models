"""A self-test of the picture-describer packs of the owner's request of 2026-11-22: restaurant menus
(packs/menus_packs.py), maths and science notation (packs/math_notation_packs.py), computer and phone screens
(packs/screens_packs.py), public-domain film stills (packs/film_stills_packs.py) and Golden Age comics
(packs/comics_packs.py), with the kit's files (training-kit/kit/menus_sources.py, math_notation_sources.py,
screens_sources.py, film_stills_sources.py, comics_sources.py). Only made-up records are used and only a few small
pictures are drawn; nothing is downloaded.

It checks that:
  - screens are read in order with the default and focused button exactly as drawn, use only made-up names, .example
    addresses and 555-01xx numbers, carry the scam pack's own safety notes, and every kind and look is made;
  - a formula's LaTeX and spoken reading come from the same tree ("x squared plus 2 x plus 1"), every row carries the
    exact LaTeX, and the named formulas all typeset;
  - chemical rows give the formula and counts RDKit works out, and the SMILES;
  - NYPL menu rows say only what the records say (dishes in reading order with their prices, the place and date),
    menus after 1930 are used only with an open NYPL rights statement, and the token is never written anywhere;
  - made-up menus answer from their own facts, with the allergy note;
  - film stills: only Prelinger films with a public-domain mark, NPS films with the mark and NASA films are used;
    civil defense films, home movies and racist caricature are left out;
  - comics: only files with evidence of US public domain (not renewed, no notice, expired), never racist caricature,
    and a file with too little record is set aside, never answered;
  - every pack is wired: build_packs.PACKS, COMMONS_KEYS (the Wikimedia readers only), the workflows' known list
    and limit lines, the kit's sources (permissive, prepare_pack), the topics the coordinator set, picture-making
    only where the kit file allows, and each kit file listed twice as a hidden import.

Run it from the repository's folder:   python3 -m pytest packs/test_describer_pictures.py
"""

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import comics_packs as cp  # noqa: E402
import film_stills_packs as fs  # noqa: E402
import math_notation_packs as mn  # noqa: E402
import menus_packs as mp  # noqa: E402
import screens_packs as sp  # noqa: E402
import synthetic_scams_packs as scams  # noqa: E402
from synthetic_documents import seeded  # noqa: E402

REPO = os.path.dirname(HERE)
PHONE = re.compile(r"\(?\d{3}\)?[ -]?\d{3}-\d{4}")


# ----------------------------------------------------------------- screens

def test_screens_read_in_order_and_exact():
    looks, kinds = set(), set()
    for n in range(60):
        rng = seeded(sp.SEED, n)
        kind = sp.KINDS[n % len(sp.KINDS)]
        d = sp.details(kind, sp.style_for(kind, rng), rng)
        looks.add(d["style"])
        kinds.add(kind)
        rows = sp.screen_rows(d)
        said = {r["question"]: r["answer"] for r in rows}
        assert all(r["synthetic"] and r["credit"] == sp.CREDIT for r in rows)
        read = said[sp.READ_Q]
        # the title first, the buttons last, in the order drawn
        if d["buttons"]:
            labels = [b["label"] for b in d["buttons"]]
            assert read.endswith(sp.button_words(d))
            at = read.rindex("Button")
            for label in labels:                 # each label found after the one before it
                at = read.index(label, at) + len(label)
            assert said[sp.BUTTONS_Q].count(":") >= len(labels)
            if d["default"] is not None:
                assert d["buttons"][d["default"]]["label"] in said[sp.SELECTED_Q]
            if d["focus"] is not None:
                assert "Keyboard focus" in said[sp.SELECTED_Q]
                assert d["style"] in ("windows", "mac")
        for text in said.values():
            for phone in PHONE.findall(text):
                assert "555-01" in phone, phone
            for site in re.findall(r"\b[\w-]+\.(com|org|net)\b", text):
                pytest.fail(f"a real-looking web address: {site}")
        if kind == "two_factor":
            assert said["What is the code for?"].endswith(scams.CODE_NOTE)
        if kind == "sign_in":
            assert said["Is it safe to sign in here?"].endswith(scams.PADLOCK_NOTE)
        if kind == "captcha":
            assert sp.CAPTCHA_NOTE in said["How do I get past this CAPTCHA?"]
        if kind == "settings":
            on = [p[1] for p in d["parts"] if p[2]]
            assert all(name in said["Which settings are turned on?"] for name in on)
    assert looks == set(sp.STYLES) and kinds == set(sp.KINDS)


def test_screen_picture():
    name, data, rows = sp.make_screen(1)
    assert data[:2] == b"\xff\xd8" and name.startswith("screen-save-")


# ----------------------------------------------------------------- formulas and structures

def test_formula_latex_and_speech_agree():
    x = mn.V("x")
    tree = ("=", ("+", ("+", mn.P(x, 2), ("*", mn.N(2), x)), mn.N(1)), mn.N(0))
    assert mn.latex(tree) == "x^{2} + 2x + 1 = 0"
    assert mn.spoken(tree) == "x squared plus 2 x plus 1 equals zero" or \
        mn.spoken(tree) == "x squared plus 2 x plus 1 equals 0"
    assert mn.spoken(("/", mn.N(1), mn.N(2))) == "one half"
    assert mn.latex(("sqrt", mn.V("theta"))) == "\\sqrt{\\theta}"
    assert mn.spoken(("d", x, ("+", mn.P(x, 3), x))).startswith("the derivative with respect to x of open bracket")
    assert mn.latex(("d", x, ("+", mn.P(x, 3), x))) == "\\frac{d}{dx} \\left(x^{3} + x\\right)"
    assert mn.chem_spoken("2H_2 + O_2 \\rightarrow 2H_2O") == "2 H 2 plus O 2 gives 2 H 2 O"
    rows = mn.formula_rows(tree, "a test", "(1.2)")
    assert all(r["latex"] == "x^{2} + 2x + 1 = 0" and r["synthetic"] for r in rows)
    said = {r["question"]: r["answer"] for r in rows}
    assert said[mn.LATEX_Q] == "x^{2} + 2x + 1 = 0" and "(1.2)" in said[mn.SAY_Q]
    for n in range(40):                        # the made-up grammar always gives LaTeX and speech
        made = mn.made_up(seeded(mn.SEED, n))
        assert mn.latex(made) and mn.spoken(made)
    assert len({name for name, _ in mn.NAMED_FORMULAS}) == len(mn.NAMED_FORMULAS)


def test_formulas_typeset():
    pytest.importorskip("matplotlib")
    for _name, tree in mn.NAMED_FORMULAS:
        assert mn.typeset(mn.latex(tree), "cm", 20, "#111111") is not None, _name
    name, data, rows = mn.make_formula(0)
    assert data[:2] == b"\xff\xd8" and rows[0]["question"] == mn.NAME_Q


def test_chemical_structures():
    pytest.importorskip("rdkit")
    facts = mn.structure_facts("CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
    assert facts["formula"] == "C8H10N4O2" and facts["rings"] == 2 and facts["aromatic"] == 2
    assert facts["atoms"] == [("C", 8), ("N", 4), ("O", 2)]
    rows = mn.chem_rows("caffeine", "Q60235", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", facts)
    said = {r["question"]: r["answer"] for r in rows}
    assert "caffeine (Wikidata Q60235)" in said[mn.CHEM_NAME_Q] and "C 8 H 10 N 4 O 2" in said[mn.CHEM_FORMULA_Q]
    assert said[mn.CHEM_SMILES_Q] == facts["canonical"] and all(r["smiles"] == facts["canonical"] for r in rows)
    assert mn.structure_facts("not a smiles") is None
    entries = mn.build_chem_structures(2, [("ethanol", "Q153", "CCO"), ("nothing", "Q1", "xx(")])
    assert sum(1 for _n, d, _r in entries if d) == 2 and all("Q153" in r["credit"] for _n, _d, r in entries)


# ----------------------------------------------------------------- menus

def made_up_dump():
    """The four CSV files of a tiny made-up NYPL dump."""
    menus = ("id,name,sponsor,event,venue,place,physical_description,occasion,notes,call_number,keywords,language,"
             "date,location,location_type,currency,currency_symbol,status,page_count,dish_count\n"
             "1,,HOTEL EXAMPLE,DINNER,COMMERCIAL,\"SPRINGFIELD, IL\",CARD; ILLUS; COL; 5X8;,EASTER;,,c1,,,1905-04-23,"
             "Hotel Example,,Dollars,$,complete,1,3\n"
             "2,,LATE CAFE,LUNCH,,,,,,c2,,,1950-01-01,Late Cafe,,Dollars,$,complete,1,3\n"
             "3,,NO DATE INN,,,,,,,c3,,,,No Date Inn,,,,complete,1,3\n")
    pages = ("id,menu_id,page_number,image_id,full_height,full_width,uuid\n"
             "10,1,1,111,100,100,uuid-a\n20,2,1,222,100,100,uuid-b\n30,3,1,333,100,100,uuid-c\n")
    items = "id,menu_page_id,price,high_price,dish_id,created_at,updated_at,xpos,ypos\n"
    for page in (10, 20, 30):
        items += (f"{page}1,{page},0.4,,1,,,0.6,0.5\n{page}2,{page},,,2,,,0.1,0.2\n{page}3,{page},1.25,,3,,,0.1,0.5\n")
    dishes = "id,name,description\n1,Roast Turkey.,\n2,Consomme,\n3,Lobster Salad,\n"
    return {"Menu.csv": menus, "MenuPage.csv": pages, "MenuItem.csv": items, "Dish.csv": dishes}


def test_nypl_menus(monkeypatch):
    chosen = mp.menu_pages(made_up_dump(), 10)
    assert [m["id"] for m, _p, _i, _b in chosen] == ["1"]          # 1950 and undated: left out without a token
    menu, page, items, basis = chosen[0]
    assert [i["dish"] for i in items] == ["Consomme", "Lobster Salad", "Roast Turkey"]   # top to bottom, then across
    assert "1905" in basis
    rows = {r["question"]: r["answer"] for r in mp.page_rows(menu, page, items, "credit")}
    assert rows[mp.READ_Q].endswith("Consomme; Lobster Salad, $1.25; Roast Turkey, $0.40.")
    assert rows[mp.FROM_Q] == ("It is from Hotel Example, Springfield, Il, a dinner menu for Easter, dated April 23, "
                               "1905 (from the New York Public Library's catalogue record).")
    assert "card; illustrated; colour" in rows[mp.LOOK_Q]
    assert any(q.startswith("How much is the ") for q in rows)
    monkeypatch.setattr(mp, "rights_ok", lambda s, uuid, token: uuid == "uuid-b")
    chosen = mp.menu_pages(made_up_dump(), 10, token="made-up-token")
    assert sorted(m["id"] for m, _p, _i, _b in chosen) == ["1", "2"]
    assert mp.OPEN_RIGHTS.search("No Known U.S. Copyright Restrictions") and not mp.OPEN_RIGHTS.search("Undetermined")
    assert mp.price_words("0.4", "", "") == "0.4 (as recorded; no currency given)"


def test_no_token_in_the_repository():
    for path in ("menus_packs.py",):
        with open(os.path.join(HERE, path), encoding="utf-8") as f:
            text = f.read()
        assert 'os.environ.get("NYPL_API_TOKEN"' in text
        assert not re.search(r'Token token="[0-9a-f]{16,}', text)


def test_synthetic_menus():
    for n in range(10):
        d = mp.menu_details(n, seeded(mp.SEED, n))
        rows = {r["question"]: r["answer"] for r in mp.menu_rows(d)}
        assert d["site"].endswith(".example") and "555-01" in d["phone"]
        if d["layout"] == "specials":
            assert all(dish in rows["What are today's specials?"] for dish, _p in d["specials"])
            continue
        for section, dishes in d["sections"]:
            assert section in rows[mp.READ_Q]
            for dish, _about, _marks, price in dishes:
                assert f"${price}" in rows[mp.READ_Q]
        assert rows["What vegetarian dishes are there?"].endswith(mp.ALLERGY_NOTE)
        assert rows["Which dishes are gluten-free?"].endswith(mp.ALLERGY_NOTE)
    name, data, _rows = mp.make_menu(2)
    assert data[:2] == b"\xff\xd8" and "pictures" in name


# ----------------------------------------------------------------- film stills

def test_film_kinds():
    pd = "http://creativecommons.org/licenses/publicdomain/"
    assert fs.film_kind({"title": "Wise Use of Credit", "collection": ["prelinger"], "licenseurl": pd})[0] == \
        "prelinger"
    assert fs.film_kind({"title": "A Film", "collection": ["prelinger"]})[0] == ""
    assert fs.film_kind({"title": "River Safety", "creator": "National Park Service",
                         "licenseurl": "https://creativecommons.org/publicdomain/mark/1.0/"})[0] == "nps"
    assert fs.film_kind({"title": "Apollo 11 launch", "creator": "NASA"})[0] == "nasa"
    assert fs.film_kind({"title": "Duck and Cover", "description": "civil defense", "collection": ["prelinger"],
                         "licenseurl": pd})[0] == ""
    assert fs.film_kind({"title": "Home Movie: Picnic", "collection": ["prelinger"], "licenseurl": pd})[0] == ""
    assert fs.film_kind({"title": "Minstrel Days", "collection": ["prelinger"], "licenseurl": pd})[0] == ""
    assert fs.lead({"title": "Wise Use of Credit", "date": "1950", "creator": "Coronet"}, "prelinger") == \
        "A still from the 1950 film 'Wise Use of Credit', made by Coronet (the Prelinger Archives, on the Internet " \
        "Archive)."


# ----------------------------------------------------------------- comics

def comic_info(categories, licence="Public domain", description="Cover of Example Comics #3, 1947, Example "
                                                                "Publications."):
    """A made-up Commons imageinfo."""
    return {"mime": "image/jpeg", "thumburl": "https://upload.example/c.jpg",
            "extmetadata": {"LicenseShortName": {"value": licence}, "Categories": {"value": categories},
                            "ImageDescription": {"value": description}, "Artist": {"value": "Example Artist"}}}


def test_comics_need_evidence():
    kind, got = cp.comic_entry("File:Example 3.jpg", comic_info("Golden Age|PD US not renewed"), "")
    assert kind == "use"
    said = {r["question"]: r["answer"] for r in got[1]}
    assert "Example Comics #3" in said[cp.FROM_Q] and "not renewed" in said[cp.PD_Q]
    assert cp.comic_entry("File:x.jpg", comic_info("Golden Age|Public domain"), "")[0] == "out"
    assert cp.comic_entry("File:x.jpg", comic_info("PD US no notice", licence="CC BY-SA 4.0"), "")[0] == "out"
    assert cp.comic_entry("File:x.jpg", comic_info("PD US no notice", description="A racist caricature of ..."),
                          "")[0] == "out"
    kind, hints = cp.comic_entry("File:x.jpg", comic_info("PD-US-expired", description="Page"), "")
    assert kind == "needs" and "expired" in hints["licence"]


# ----------------------------------------------------------------- wiring

PACKS = {"nypl_menus": (mp.MENUS_LIMITS, ("food", "documents")),
         "synthetic_menus": (mp.MENUS_LIMITS, ("food", "documents")),
         "synthetic_formulas": (mn.MATH_LIMITS, ("documents",)),
         "chem_structures": (mn.MATH_LIMITS, ("documents",)),
         "synthetic_screens": (sp.SCREENS_LIMITS, ("screens",)),
         "pd_film_stills": (fs.FILM_STILLS_LIMITS, ("art", "people")),
         "commons_golden_age_comics": (cp.COMICS_LIMITS, ("art",))}
COMMONS = {"chem_structures", "commons_golden_age_comics"}
KIT_FILES = ("menus_sources", "math_notation_sources", "screens_sources", "film_stills_sources", "comics_sources")


def test_wiring():
    assert set(PACKS) <= set(build_packs.PACKS)
    assert {k for k in PACKS if k in build_packs.COMMONS_KEYS} == COMMONS
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        kit_yml = f.read()
    for key, (limits, _topics) in PACKS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limits[key]} ;;$", build_yml, re.M), key
    assert "NYPL_API_TOKEN: ${{ secrets.NYPL_API_TOKEN }}" in build_yml
    for name in KIT_FILES:
        assert kit_yml.count(f"--hidden-import {name} ") == 2, name
    import sources
    import topics
    listed = {s.key: s for s in sources.SOURCES}
    ok = set()
    for name in KIT_FILES:
        module = __import__(name)
        prefix = {"menus_sources": "MENUS", "math_notation_sources": "MATH", "screens_sources": "SCREENS",
                  "film_stills_sources": "FILM_STILLS", "comics_sources": "COMICS"}[name]
        ok |= getattr(module, f"{prefix}_PICTURE_MAKING_OK")
        assert all(getattr(module, f"{prefix}_NOT_INCLUDED").values())
        for s in getattr(module, f"{prefix}_SOURCES"):
            assert s.key in listed
            assert s.key in PACKS or s.group != "permissive", s.key
    for key, (limits, wanted) in PACKS.items():
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
        assert listed[key].cap == limits[key], key
        for topic in wanted:
            assert key in topics.find(topic).keys, (key, topic)
        assert (key in sources.NOT_FOR_PICTURE_MAKING) == (key not in ok), key
    assert ok == {"synthetic_menus", "synthetic_formulas", "chem_structures"}
    assert listed["im2latex_formulas"].group == "research" and "im2latex_formulas" in sources.NOT_FOR_PICTURE_MAKING
    assert "im2latex_formulas" in topics.find("documents").keys


def test_im2latex_lists():
    import math_notation_sources as k
    formulas = k.im2latex_formulas("a^2\n\\frac{1}{2}\n\n")
    got = k.im2latex_lists([("train", "0 abc basic\n2 empty basic\n"), ("test", "1 def basic\nbad line\n")], formulas)
    assert got == {"abc": ("train", "a^2"), "def": ("test", "\\frac{1}{2}")}
