"""Self-test of the cooking basics and more fitness and nutrition books (cooking_basics.py and fitness_more.py), with
MADE-UP data only: nothing is downloaded.

It checks that both modules are registered under their request words (each at most 256 jobs) and reach sources.py;
that they share their key prefixes (cook: with cookbooks.py, fit: with fitness_nutrition.py) without a name used
twice, and that each key goes to its own module (the builder, the weekly sign and the index's key check); that every
book has a licence the toolkit may repackage, a notice with its safety note, and a description; that the old books
are marked historical and checked for their year; that Good and Cheap is personal use only; that the military
manuals go through the release rule; that no Internet Archive item or PDF is used twice in the library; that the
indexes are built offline and link every book; that the VA PDF books read made-up pages and PDFs as they should; and
that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_cooking_fitness.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import cookbooks  # noqa: E402
import cooking_basics as C  # noqa: E402
import fitness_more as F  # noqa: E402
import fitness_nutrition as FN  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

COOK_WORDS = ("cooking-basics", "cook-classics", "cook-gov-recipes", "cook-budget")
FIT_WORDS = ("fitness-more", "fit-military", "fit-older-adaptive", "fit-diets", "fit-classics")


def entries(m):
    """Every PDF entry of a module."""
    return list(m.COLLECTION.pdfs.values())


def test_registered_words():
    for m, words, prefix in ((C, COOK_WORDS, "cook"), (F, FIT_WORDS, "fit")):
        assert m in more_refs.modules()
        everything = set(sources.expand_keys([words[0]]))
        assert everything == set(m.COLLECTION.own_keys())
        for word in words:
            keys = sources.expand_keys([word])
            assert keys == m.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
            assert f"{prefix}:index" in keys and set(keys) <= everything, word
        themes = set().union(*(sources.expand_keys([w]) for w in words[1:]))
        assert themes == everything, words[0]        # every book is in one theme
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_shared_prefixes_kept_apart():
    mine = set(C.COLLECTION.own_keys())
    assert not {k.split(":", 1)[1] for k in mine} & set(cookbooks.BY_NAME)
    assert not set(F.COLLECTION.own_keys()) & set(FN.COLLECTION.own_keys())
    # cookbooks.py's own words and keys stay its own; cooking_basics' keys are handed over
    assert sources.expand_keys(["cookbooks"]) == cookbooks.expand_keys(["cookbooks"])
    assert not set(sources.expand_keys(["cookbooks"])) & mine
    assert sources.expand_keys(["cook:index"]) == ["cook:index"]
    for key in ("fit:index", "fit:army_fm_7_22_holistic_health_fitness_2020"):
        assert more_refs.module_for(key) is F, key
    assert more_refs.module_for("fit:cdc_sleep") is FN
    # the index's key check knows both modules' books
    for key in ("cook:nhlbi_week_on_dash", "cook:farmer_boston_cooking_school_1896", "fit:cdc_sleep", "fit:index"):
        assert X.key_exists(key), key
    assert not X.key_exists("cook:made_up_book")


def test_cookbooks_hands_over_its_keys(monkeypatch, tmp_path):
    """build_cookbooks and cookbooks.sign hand cooking_basics' keys to its collection (the builder and the weekly
    check send every cook: key to cookbooks.py)."""
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    manifests = cookbooks.build_cookbooks(["cook:index"], str(tmp_path))
    assert manifests["cook:index"]["books"] and not manifests["cook:index"]["failed"]
    with open(tmp_path / "manifest-cook_index.json", encoding="utf-8") as f:
        assert json.load(f)["key"] == "cook:index"
    assert cookbooks.sign("cook:index") == C.COLLECTION.sign("cook:index") != ""
    assert cookbooks.sign("cook:made_up_book") == ""


def test_every_book():
    for m in (C, F):
        for e in entries(m):
            assert e["group"] in sources.GROUPS, e["name"]
            kind = B.licence_kind(B.licence_short(e["licence"]))
            assert kind, e["name"]
            assert e["notice"] and e["description"] and e["title"] and e["subject"], e["name"]
            assert e.get("archive") or e.get("pdf"), e["name"]
            if m is C:
                assert C.FOOD_SAFETY in e["notice"], e["name"]
            else:
                assert F.NOTE in e["notice"], e["name"]
            if e.get("old_public_domain"):
                assert int(e["published"]) < 1931 and "Historical" in e["description"], e["name"]
            elif e["licence"] == K.US_GOV:
                assert e["licence_page"] and e["licence_text"], e["name"]
            if kind == "non-commercial":
                assert e.get("personal_use") and "PERSONAL USE ONLY" in e["notice"], e["name"]
    good = C.COLLECTION.pdfs["good_and_cheap_2014"]
    assert good["licence"] == "CC BY-NC-SA 4.0" and good["personal_use"]
    for e in F.MILITARY:
        assert e["military"] and e["work"].startswith("a work of the US"), e["name"]
        assert F.EXERCISE_SAFETY in e["notice"], e["name"]
    for e in C.CLASSICS:
        assert "Historical" in e["description"], e["name"]
    for e in F.CLASSICS:
        assert "Historical" in e["description"] and F.EXERCISE_SAFETY in e["notice"], e["name"]
    for words in ("145 F", "160 F", "165 F", "2 hours", "allergens", "sesame"):
        assert words in C.FOOD_SAFETY, words
    for words in ("911", "988", "doctor"):
        assert words in F.NOTE, words


def test_no_address_used_twice_in_the_library():
    mine = [e.get("archive") or e.get("pdf") for m in (C, F) for e in entries(m)]
    assert len(mine) == len(set(mine))
    elsewhere = set()
    for m in more_refs.modules():
        if m in (C, F):
            continue
        for e in list(m.COLLECTION.pdfs.values()) + list(m.COLLECTION.guides.values()):
            elsewhere.update(x for x in (e.get("archive"), e.get("pdf")) if x)
    elsewhere.update(x for e in sources.PDF_DOCS + cookbooks.BOOKS for x in (e.get("archive"), e.get("pdf")) if x)
    assert not set(mine) & elsewhere, set(mine) & elsewhere


def test_old_book_refused_after_1930(monkeypatch, tmp_path):
    """A made-up item whose record says 1931 is refused before anything is downloaded."""
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                    "https://archive.org/details/x"))
    monkeypatch.setattr(B, "archive_year", lambda ident, cache=None: 1931)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    for entry in (C.COLLECTION.pdfs["farmer_boston_cooking_school_1896"],
                  F.COLLECTION.pdfs["camp_keeping_fit_all_the_way_1919"]):
        left_out = []
        assert B.pdfdoc_book(dict(entry, archive="madeupitem"), str(tmp_path), None, left_out) is None
        assert "before 1931" in left_out[0]["reason"]


def test_indexes_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for m, prefix in ((C, "cook"), (F, "fit")):
        book_fn, sign_fn = m.MAKERS["index"]
        left_out = []
        book = book_fn("index", "work", None, left_out)
        assert book.pages and book.licence == X.CC0_INDEX and not left_out, left_out
        body = " ".join(p.body for p in book.pages)
        assert '<a href="https://' in body
        assert sign_fn("index") == sign_fn("index")
        linked = {e[1] for _p, _i, items in m.SECTIONS for e in items}
        assert set(m.COLLECTION.own_keys()) - {f"{prefix}:index"} <= linked     # every book is in its index
    cook_body = " ".join(p.body for p in C.MAKERS["index"][0]("index", "work", None, []).pages)
    assert "cook:nhlbi_keep_the_beat_dinners" in cook_body and "outdoor-cooking" in cook_body
    fit_body = " ".join(p.body for p in F.MAKERS["index"][0]("index", "work", None, []).pages)
    assert "gpo:nia_exercise_physical_activity_2018" in fit_body and "dir:nccih_health" in fit_body


MADE_UP_LISTING = """<main><ul>
<li><a href="/NUTRITION/docs/Recipes/MainDishes/Made-Up-Stew.pdf#" target="_blank" title="Made-Up Stew">Made-Up
Stew</a></li>
<li><a href="/NUTRITION/docs/Recipes/MainDishes/Pretend-Pasta.pdf" target="_blank">Pretend &amp; Pasta</a></li>
<li><a href="/NUTRITION/docs/Recipes/MainDishes/Made-Up-Stew.pdf#" title="Made-Up Stew">Made-Up Stew</a></li>
<li><a href="/NUTRITION/Recipes/Sides.asp">Side dishes</a></li>
</ul></main>"""


def test_va_pdf_links():
    links = C.va_pdf_links(MADE_UP_LISTING)
    base = "https://www.nutrition.va.gov/NUTRITION/docs/Recipes/MainDishes/"
    assert links == [("Made-Up Stew", base + "Made-Up-Stew.pdf"), ("Pretend & Pasta", base + "Pretend-Pasta.pdf")]


def test_va_book_from_made_up_pages(monkeypatch, tmp_path):
    """The VA book reads each listing page once, each PDF once (under the first part that lists it), checks the
    licence line once, and keeps each PDF's title as its page title."""
    fetched, read = [], []

    def made_up_fetch(url, cache=None, binary=False, tries=4):
        fetched.append(url)
        if url == K.GOVINFO_POLICY:
            return "<p>Copyright protection under this title is not available for any work of the United States " \
                   "Government</p>"
        return MADE_UP_LISTING

    def made_up_pdf(entry, work, cache=None, left_out=None):
        read.append(entry["pdf"])
        assert "licence_text" not in entry             # checked once, not for every PDF
        book = K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], entry["page"], entry["description"],
                          entry["notice"])
        book.pages.append(B.Page("p1", "Pages 1 to 1", "<p>Made-up recipe text.</p>", 1, ""))
        book.original_pdf = {"url": entry["pdf"], "size": 10, "sha256": "0" * 64}
        return book

    monkeypatch.setattr(B, "fetch", made_up_fetch)
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "pdfdoc_book", made_up_pdf)
    listing = [("Main dishes", "https://www.nutrition.va.gov/NUTRITION/Recipes/Beef_Recipes.asp"),
               ("Side dishes", "https://www.nutrition.va.gov/NUTRITION/Recipes/Sides.asp")]
    book_fn, sign_fn = C.va_pdf_maker("cook", "made_up", "Made-up recipes", "Recipes", "Made-up description.",
                                      "Made-up notice.", listing)
    left_out = []
    book = book_fn("made_up", str(tmp_path), None, left_out)
    assert not left_out, left_out
    assert [p.title for p in book.pages] == ["Made-Up Stew", "Pretend & Pasta"]
    assert {p.unit for p in book.pages} == {"Main dishes"}
    assert len(read) == 2 and len(book.originals) == 2
    assert fetched.count(K.GOVINFO_POLICY) == 1
    assert book.name == "cook_made_up" and book.licence == K.US_GOV and book.group == C.GROUP
    assert sign_fn("made_up") == sign_fn("made_up")
    fit_book_fn, _sign = F.VA_HANDOUTS_BOOK
    assert F.MAKERS["va_nutrition_handouts"][0] is fit_book_fn


def test_va_book_refused_without_licence_line(monkeypatch, tmp_path):
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: "<p>Nothing here.</p>")
    monkeypatch.setattr(B, "pdfdoc_book", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no PDF")))
    left_out = []
    assert C.VA_RECIPES_BOOK[0]("va_healthy_recipes", str(tmp_path), None, left_out) is None
    assert "17 U.S.C. 105" in left_out[0]["reason"]


def test_not_included():
    for m in (C, F):
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    cook_rows = " ".join(r[0] for r in C.NOT_INCLUDED)
    for words in ("MyPlate", "Food Buying Guide", "FSIS", "Keep the Beat", "Settlement", "Wikibooks"):
        assert words in cook_rows, words
    fit_rows = " ".join(r[0] for r in F.NOT_INCLUDED)
    for words in ("Dietary Supplements", "Air Force", "NOFFS", "Go4Life", "NCHPAD", "tai chi"):
        assert words in fit_rows, words
