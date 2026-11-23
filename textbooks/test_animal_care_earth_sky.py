"""Self-test of the animal care and veterinary books (animal_care.py, vet:) and the weather, rocks and sky books
(earth_sky.py, earth:), with MADE-UP data only: nothing is downloaded.

It checks that each module is registered once in more_refs.py with its own group, that its request words reach
sources.py with at most 256 keys each (the overall word holds every key, each theme word only its own books and the
index), and that its licence lines and NOT_INCLUDED rows (each with an address) are there; that every book has a
licence the toolkit may repackage, a description and a notice with the safety note of its theme (diseases from
animals and bites; lightning, floods and storm spotting; mine shafts and prospecting; never look at the Sun); that the
old books are dated before 1931 and the old veterinary books say "ask a veterinarian; old treatments may be harmful";
that the military manuals are judged by the release rule and keep the builder's truthful release line; that no
Internet Archive item, PDF or page address is read twice in the library (FM 1-230 is the service skills book's, and
CDC sites already read elsewhere are not read again); that the address patterns keep the right pages (tried on
made-up addresses); that an item whose record says 1931 is refused before anything is downloaded; and that the two
index books are made offline with keys the library has.

Run it from the repository's folder:   python3 -m pytest textbooks/test_animal_care_earth_sky.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animal_care as A  # noqa: E402
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import earth_sky as E  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES = [(A, "animal-care", ("vet-livestock", "vet-pets", "vet-classics")),
           (E, "earth-sky", ("earth-weather", "earth-rocks", "earth-night-sky"))]


def entries(m):
    """Every web guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered_once_with_words_under_256():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    for m, word, themes in MODULES:
        assert m in more_refs.modules() and prefixes.count(m.COLLECTION.prefix) == 1
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256 and set(keys) == set(m.COLLECTION.own_keys()), word
        for theme in themes:
            some = sources.expand_keys([theme])
            assert 1 < len(some) <= 256 and set(some) <= set(keys), theme
            assert some[0] == f"{m.COLLECTION.prefix}:index", theme
        assert set(m.GROUPS) == {m.GROUP} and sources.GROUPS[m.GROUP] == m.GROUPS[m.GROUP]
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    # every book of the themes together is the whole section
    for m, word, themes in MODULES:
        together = set()
        for theme in themes:
            together |= set(sources.expand_keys([theme]))
        assert together == set(sources.expand_keys([word])), word


def test_every_book_licence_description_and_safety():
    for m, _word, _themes in MODULES:
        for g in entries(m):
            assert g["group"] == m.GROUP and g["description"] and g["notice"], g["name"]
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short) or B.licence_kind(g["licence"]), g["name"]
            if m is A:
                assert A.VET_NOTE in g["notice"], g["name"]
            else:
                assert any(s in g["notice"] for s in (E.WEATHER_SAFETY, E.ROCK_SAFETY, E.SKY_SAFETY)), g["name"]
            if g.get("old_public_domain"):
                assert int(g["published"]) < 1931 and "Published in" in g["description"], g["name"]
            if g.get("military"):
                assert "front pages print" in g["notice"] and g["work"].startswith("a work of the US"), g["name"]
                assert g["archive"] and g["published"] and g["version"], g["name"]
    for words in ("zoonoses", "wash your hands", "bite", "state veterinarian"):
        assert words in A.VET_NOTE, words
    for words in ("thunder roars", "flood water", "safe place"):
        assert words in E.WEATHER_SAFETY, words
    for words in ("mine shafts", "eye protection", "Mercury and cyanide"):
        assert words in E.ROCK_SAFETY, words
    assert "Never look at the Sun" in E.SKY_SAFETY and "eclipse" in E.SKY_SAFETY


def test_old_veterinary_books_are_history():
    for p in A.PDFS:
        if p.get("old_public_domain") or p.get("military"):
            assert "old treatments may be harmful" in p["description"], p["name"]
            assert "ask a veterinarian" in p["description"].lower(), p["name"]
    names = {p["name"] for p in A.PDFS}
    assert {f"law_text_book_veterinary_medicine_v{n}" for n in range(1, 6)} <= names
    law = [p for p in A.PDFS if p["name"].startswith("law_text_book")]
    assert [p["archive"] for p in law] == [f"b2812120x_000{n}" for n in range(1, 6)]
    british = {p["name"] for p in A.PDFS + E.WEATHER + E.ROCKS if p.get("country") == "United Kingdom"}
    for name in ("hayes_veterinary_notes_horse_owners_1915", "war_office_animal_management_1923",
                 "met_office_cloud_forms_1918", "anderson_prospectors_handbook_1911"):
        assert name in british, name
    # the guide dog books are left to the blind-living helper; nothing here is about guide dogs
    assert not any("guide_dog" in k for k in sources.expand_keys(["animal-care"]))


def test_nothing_read_twice_in_the_library():
    mine = []
    for m in (A, E):
        for e in entries(m):
            mine += [x for x in (e.get("archive"), e.get("pdf")) if x]
            mine += [u for u in e.get("urls", []) if isinstance(u, str)]
    assert len(mine) == len(set(mine))
    elsewhere = set()
    for m in more_refs.modules():
        if m in (A, E):
            continue
        for e in entries(m):
            elsewhere.update(x for x in (e.get("archive"), e.get("pdf"), e.get("source")) if x)
            elsewhere.update(u if isinstance(u, str) else u[0] for u in e.get("urls", []))
    for e in sources.PDF_DOCS + sources.GOV_GUIDES:
        elsewhere.update(x for x in (e.get("archive"), e.get("pdf"), e.get("source")) if x)
    assert not set(mine) & elsewhere, set(mine) & elsewhere
    # no other file names these items (each module's own tests look for theirs the same way)
    text = ""
    for name in os.listdir(HERE):
        if name.endswith(".py") and name not in ("animal_care.py", "earth_sky.py", "test_animal_care_earth_sky.py"):
            with open(os.path.join(HERE, name), encoding="utf-8") as f:
                text += f.read()
    for m in (A, E):
        for p in m.COLLECTION.pdfs.values():
            if p.get("archive"):
                assert f'"{p["archive"]}"' not in text, p["archive"]
    # FM 1-230 is built in the service skills books and only linked here
    assert not [x for x in mine if x.endswith("doctrine-fm1_230")]
    assert X.key_exists("skill:army_fm_1_230_meteorology_for_army_aviators_1982")
    # CDC sites another book reads already are not read again
    cdc_elsewhere = set()
    for m in more_refs.modules():
        if m is A:
            continue
        for g in m.COLLECTION.guides.values():
            for start, _depth in g.get("crawl") or []:
                hit = re.match(r"https://www\.cdc\.gov/([a-z0-9-]+)/site\.html", start)
                if hit:
                    cdc_elsewhere.add(hit.group(1))
    assert not set(A.CDC_SITES) & cdc_elsewhere, set(A.CDC_SITES) & cdc_elsewhere


def test_address_patterns_on_made_up_addresses():
    rocks = re.compile(E.COLLECTION.guides["usgs_rocks_minerals_gold"]["pages"])
    assert rocks.match("https://pubs.usgs.gov/gip/fossils/made-up.html")
    assert not rocks.match("https://pubs.usgs.gov/gip/fossils/")          # the bare folder: its index again
    assert not rocks.match("https://pubs.usgs.gov/gip/dynamic/made-up.html")   # This Dynamic Earth is elsewhere
    volcanoes = re.compile(E.COLLECTION.guides["usgs_volcanoes_earthquakes"]["pages"])
    assert volcanoes.match("https://pubs.usgs.gov/gip/deserts/dunes/")
    assert volcanoes.match("https://pubs.usgs.gov/gip/msh/madeup.html")
    assert not volcanoes.match("https://pubs.usgs.gov/gip/msh/picture.jpg")
    aphis = re.compile(A.COLLECTION.guides["aphis_livestock_poultry_disease"]["pages"])
    assert aphis.match("https://www.aphis.usda.gov/livestock-poultry-disease/avian/made-up-disease")
    assert not aphis.match("https://www.aphis.usda.gov/livestock-poultry-disease/cervid/chronic-wasting")
    eclipses = re.compile(E.COLLECTION.guides["nasa_eclipses"]["pages"])
    assert eclipses.match("https://science.nasa.gov/eclipses/safety/")
    assert not eclipses.match("https://science.nasa.gov/skywatching/made-up/")      # Skywatching is science:
    for name in ("nasa_planet_facts", "nasa_planetary_fact_sheets", "blm_mining_claims", "fda_food_producing_animals"):
        g = E.COLLECTION.guides.get(name) or A.COLLECTION.guides[name]
        assert all(re.match(g["pages"], u) for u in g["urls"]), name


def test_old_book_refused_after_1930(monkeypatch, tmp_path):
    """A made-up item whose record says 1931 is refused before anything is downloaded."""
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                    "https://archive.org/details/x"))
    monkeypatch.setattr(B, "archive_year", lambda ident, cache=None: 1931)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    for entry in (A.COLLECTION.pdfs["craig_diseases_of_swine_1906"], E.COLLECTION.pdfs["martin_friendly_stars_1907"]):
        left_out = []
        assert B.pdfdoc_book(dict(entry, archive="madeupitem"), str(tmp_path), None, left_out) is None
        assert "before 1931" in left_out[0]["reason"], entry["name"]


def test_military_book_keeps_the_release_line(monkeypatch):
    """The builder's notice (its truthful release line first) is not replaced by the entry's own notice; an old
    book's notice is the entry's."""
    def made_up_book(entry, work, cache=None, left_out=None):
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], "https://archive.org/details/made-up",
                          entry["description"], "Made-up release line. " + entry["notice"])
    monkeypatch.setattr(B, "pdfdoc_book", made_up_book)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    book = A.COLLECTION.book_for("vet:army_tm_10_396_war_dogs_1943", "work")
    assert book.notice.startswith("Made-up release line. The release line before this")
    book = E.COLLECTION.book_for("earth:usaf_afh_11_203_v1_weather_for_aircrews_1997", "work")
    assert book.notice.startswith("Made-up release line.") and book.name.startswith("earth_")
    old = A.COLLECTION.book_for("vet:salmon_diseases_of_poultry_1899", "work")
    assert old.notice == A.COLLECTION.pdfs["salmon_diseases_of_poultry_1899"]["notice"]


def test_index_books_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for m in (A, E):
        book_fn, sign_fn = m.COLLECTION.makers["index"]
        left_out = []
        book = book_fn("index", "work", None, left_out)
        assert book.pages and book.licence == X.CC0_INDEX and not left_out, (m.__name__, left_out)
        assert len(book.pages) == len(m.SECTIONS) and sign_fn("index")
        assert '<a href="https://' in " ".join(p.body for p in book.pages)
        linked = {e[1] for _p, _i, items in m.SECTIONS for e in items if e[0] == "key"}
        own = {k for k in m.COLLECTION.own_keys() if not k.endswith(":index")}
        assert own <= linked, own - linked                 # every book of the module is in its index
        for _part, _intro, items in m.SECTIONS:
            for kind, what, *_rest in items:
                if kind == "word":
                    assert sources.expand_keys([what]), what
    linked = {e[1] for _p, _i, items in A.SECTIONS for e in items}
    for key in ("pet:index", "pet:fda_pet_health", "home:aphis_pets", "firstaid:cdc_bites_ticks",
                "pub:usda_farmers_bulletins", "service-skills-veterinary", "commons_breeds"):
        assert key in linked, key
    linked = {e[1] for _p, _i, items in E.SECTIONS for e in items}
    for key in ("prep:nws_safety", "radio:nws_weather_spotters_field_guide_2011", "science:nasa_skywatching",
                "guide:usgs_this_dynamic_earth", "commons_sky_weather", "commons_rocks_fossils",
                "rate:navy_aerographers_mate_3_2_1976"):
        assert key in linked, key
