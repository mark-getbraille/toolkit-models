"""Self-test of oldbooks_life.py (old public-domain and open books for nine thin life-skills groups, the owner's
request of 2026-11-22), with MADE-UP data only: nothing is downloaded.

It checks that:
  - the module is registered once in more_refs.MODULES, reaches sources.py (its licence lines and not-included rows,
    each with an index address), and owns its request words, each at most 256 jobs, together covering every book;
  - every book is filed in an existing group of the library (the groups of household.py, instrument_care.py,
    gardening.py, outdoors.py, science_use.py, computer_basics.py, typing_skills.py, audio_media.py, genealogy.py
    and relationships.py) and the module makes no new group;
  - every book has a licence the toolkit may repackage, a description and a notice; every old Internet Archive book
    is marked old_public_domain with a year before 1931 and its item in its version, so the builder checks the
    item's own record; the newer Internet Archive books are US government works;
  - the safety and out-of-date notes the owner asked for are there: never mix bleach and ammonia on every household
    book, old pest remedies on the old gardening books, historical attitudes on the etiquette and letter books,
    Leave No Trace on the old camping books, never look at the Sun on the astronomy books, the typewriter note on
    the typing courses;
  - no Internet Archive item is used twice here or named by any other module of the library;
  - the LibreOffice guides and the GNOME help match their own page addresses, and the GNOME help leaves out the
    accessibility pages already built by a11y_community.py;
  - a made-up item whose record says 1931 is refused before anything is downloaded.

Run it from the repository's folder:   python3 -m pytest textbooks/test_oldbooks_life.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import oldbooks_life as O  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
GROUPS = {"household": "household", "instruments": "instruments", "garden": "garden", "outdoors": "outdoors",
          "science": "scienceuse", "media": "audiomedia", "genealogy": "genealogy", "relationships": "relationships"}


def books():
    """Every book entry of the module."""
    return [e for entries in O.AREAS.values() for e in entries]


def test_registered_and_wired():
    assert O in more_refs.modules() and more_refs.MODULES.count("oldbooks_life") == 1
    assert O.GROUPS == {}
    assert set(O.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in O.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    every = []
    for word in ["oldbooks-life"] + [f"oldbooks-life-{a}" for a in O.AREAS]:
        keys = sources.expand_keys([word])
        assert keys == O.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
        assert all(O.COLLECTION.owns(k) for k in keys), word
        every += keys
    names = {f"olife:{e['name']}" for e in books()}
    assert names == set(sources.expand_keys(["oldbooks-life"])) == set(O.COLLECTION.own_keys())
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert prefixes.count("olife") == 1


# The teachers' guides moved to "Teaching and homeschooling" (the owner's request of 2026-11-23).
TEACHERS_GUIDES = {"comstock_handbook_nature_study_1911", "nasa_exploring_the_moon_1994",
                   "nasa_space_based_astronomy_1994", "nasa_looking_at_earth_from_space_1995", "nasa_microgravity_1995",
                   "nasa_space_food_nutrition_1999", "nasa_plants_in_space_1997", "nasa_mars_exploration_water_2000"}


def test_books_in_existing_groups():
    for area, group in GROUPS.items():
        for e in O.AREAS[area]:
            # the teachers' guides are in "Teaching and homeschooling" (group key "k12") since 2026-11-23
            expected = O.TEACH if e["name"] in TEACHERS_GUIDES else group
            assert e["group"] == expected and expected in sources.GROUPS, e["name"]
    for e in O.AREAS["computer"]:
        assert e["group"] in ("computer", "typing"), e["name"]
    assert sources.GROUPS["computer"] == "Reference, computer and phone basics"
    assert sources.GROUPS["relationships"] == "Reference, communication and relationships"


def test_every_book_has_an_allowed_licence():
    for g in books():
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, bool(g.get("unchanged"))), (g["name"], short)
        assert g["description"] and g["notice"] and g["title"] and g["subject"], g["name"]
        if g.get("archive") and g["licence"].startswith("Public domain (published"):
            assert g.get("old_public_domain"), g["name"]
            assert int(g["published"][:4]) < 1931 and g["archive"] in g["version"], g["name"]
            assert g["published"] in g["title"] or g["published"] in g["version"], g["name"]
        elif g.get("archive"):
            assert g["licence"] == sources.US_GOV and g["licence_page"] and g["licence_text"], g["name"]
            assert 1931 <= int(g["published"]) and g["archive"] in g["version"], g["name"]
        else:
            assert g["licence_page"] and g["licence_text"], g["name"]


def test_notes():
    for g in O.HOUSEHOLD:
        assert "never mix" in g["notice"].lower() and "ammonia" in g["notice"], g["name"]
        if g.get("old_public_domain"):
            assert "out of date" in g["description"], g["name"]
    for g in O.GARDENING:
        if g.get("old_public_domain"):
            assert "now banned" in g["description"], g["name"]
        assert "label" in g["notice"], g["name"]
    for g in O.RELATIONSHIPS:
        assert "historical, not current advice" in g["description"], g["name"]
    for g in O.OUTDOORS:
        assert "life jacket" in g["notice"], g["name"]
        if "camp" in g["subject"].lower() or "hiking" in g["subject"].lower():
            assert "Leave No Trace" in g["description"], g["name"]
        if g["subject"].startswith("Birds"):
            assert "protected" in g["description"], g["name"]
    for g in O.SCIENCE:
        if re.search(r"astronom|stargazing|moon", g["subject"], re.I):
            assert O.SKY_SAFETY in g["notice"], g["name"]
    for g in O.TYPING:
        assert "typewriters" in g["description"], g["name"]
    for g in O.INSTRUMENTS:
        assert "unplug" in g["notice"], g["name"]
    for g in O.GENEALOGY:
        assert "check with the office" in g["notice"], g["name"]
    for g in O.MEDIA:
        assert "history" in g["description"] and "obsolete" in g["description"], g["name"]
    yearbooks = [g for g in books() if g.get("archive", "").startswith("yoa")]
    assert len(yearbooks) == 18 and all("Yearbook of Agriculture" in g["notice"] for g in yearbooks)
    assert {"yoa1948", "yoa1977"} <= {g["archive"] for g in yearbooks}
    post = O.COLLECTION.pdfs["post_etiquette_1922"]
    assert post["published"] == "1922" and post["old_public_domain"]
    carnegie = O.COLLECTION.pdfs["esenwein_carnegie_art_of_public_speaking_1915"]
    assert carnegie["published"] == "1915" and "Carnegie" in carnegie["publisher"]


def test_no_archive_item_twice_or_elsewhere():
    items = [g["archive"] for g in books() if g.get("archive")]
    assert len(items) == len(set(items)), [i for i in items if items.count(i) > 1]
    others = ""
    for name in os.listdir(HERE):
        if name.endswith(".py") and name not in ("oldbooks_life.py", "test_oldbooks_life.py"):
            with open(os.path.join(HERE, name), encoding="utf-8") as f:
                others += f.read()
    for item in items:
        assert f'"{item}"' not in others, item


def test_web_guide_patterns():
    impress = O.COLLECTION.guides["libreoffice_impress_guide"]
    assert re.match(impress["pages"], "https://books.libreoffice.org/en/IG262/IG26201-IntroducingImpress.html")
    assert impress["licence"] == "CC BY 4.0" and "IG262" in impress["licence_page"]
    draw = O.COLLECTION.guides["libreoffice_draw_guide"]
    assert re.match(draw["pages"], "https://books.libreoffice.org/en/DG262/DG262.html")
    assert not re.match(draw["pages"], "https://books.libreoffice.org/en/IG262/IG262.html")
    gnome = O.COLLECTION.guides["gnome_desktop_help"]
    assert gnome["licence"] == "CC BY-SA 3.0"
    assert B.licence_kind(B.licence_short(gnome["licence"]), False) == "share-alike"
    assert re.match(gnome["pages"], "https://help.gnome.org/gnome-help/files-browse.html")
    assert not re.match(gnome["pages"], "https://help.gnome.org/gnome-help/a11y-screen-reader.html")
    assert not re.match(gnome["pages"], "https://help.gnome.org/gnome-help/files.html.de")
    assert re.search(gnome["licence_text"], "licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported "
                                            "License.")


def test_old_book_refused_after_1930(monkeypatch, tmp_path):
    """A made-up item whose record says 1931 is refused before anything is downloaded."""
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                    "https://archive.org/details/x"))
    monkeypatch.setattr(B, "archive_year", lambda ident, cache=None: 1931)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    left_out = []
    entry = dict(O.COLLECTION.pdfs["post_etiquette_1922"], archive="madeupitem")
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert "before 1931" in left_out[0]["reason"]
