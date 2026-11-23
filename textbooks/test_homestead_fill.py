"""Self-test of the homestead skills books (homestead_fill.py, hfill:), with MADE-UP data only: nothing is downloaded.

It checks that:
  - the module is registered once (more_refs.MODULES), reaches sources.py with the homestead group, its licence lines
    and its NOT_INCLUDED rows (each with an address), and that every request word (homestead-fill and one per area)
    stays at or under 256 jobs and covers exactly the module's keys;
  - every book has a licence the toolkit may repackage, a description and the safety note of its area (food safety
    for meat, trap laws, forge burns and fumes, navigation, water, seed and fibre notes say what the owner asked);
  - the old books are dated before 1931 and say what is out of date, and the basketry books carry the note on their
    outdated views; the military manuals are judged by the release rule and keep the builder's release line;
  - the USDA AMS meat specifications are read from ams.usda.gov's own files; no Internet Archive item is used twice
    or by another module (extend, never duplicate);
  - a made-up item whose record says 1931 is refused before anything is downloaded;
  - the index is made offline, every key it lists exists in the library, and it links the packs of this collection.

Run it from the repository's folder:   python3 -m pytest textbooks/test_homestead_fill.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import homestead_fill as M  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

SAFETY_OF = {"seed-saving": M.SEED_SAFETY, "butchering": M.MEAT_SAFETY, "trapping-tanning": M.TRAP_SAFETY,
             "blacksmithing": M.FORGE_SAFETY, "star-navigation": M.NAV_SAFETY, "water-purification": M.WATER_SAFETY,
             "fibre-crafts": M.FIBRE_SAFETY}


def test_registered():
    assert M in more_refs.modules() and more_refs.MODULES.count("homestead_fill") == 1
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert prefixes.count("hfill") == 1
    every = sources.expand_keys(["homestead-fill"])
    assert 0 < len(every) == len(set(every)) <= 256 and set(every) == set(M.COLLECTION.own_keys())
    for word, pdfs in M.AREAS.items():
        keys = sources.expand_keys([word])
        assert keys == ["hfill:index"] + [f"hfill:{p['name']}" for p in pdfs] and len(keys) <= 256, word
    assert sum(len(p) for p in M.AREAS.values()) == len(M.PDFS)
    assert sources.GROUPS["homestead"] == "Reference, homesteading" and M.GROUP == "homestead"
    assert set(M.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in M.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_safety_notes_say_what_the_owner_asked():
    for words in ("145 F", "160 F", "165 F", "tested recipe", "inspection", "banned"):
        assert words in M.MEAT_SAFETY, words
    for words in ("licence", "trapper education", "seasons", "illegal", "Best Management Practices", "arsenic"):
        assert words in M.TRAP_SAFETY, words
    for words in ("hot metal", "safety glasses", "carbon monoxide", "galvanised", "metal fume fever"):
        assert words in M.FORGE_SAFETY, words
    for words in ("not for navigation by itself", "current Nautical or Air Almanac", "Never look at the Sun"):
        assert words in M.NAV_SAFETY, words
    for words in ("rolling boil for 1 minute", "6,500 feet", "do not remove chemicals"):
        assert words in M.WATER_SAFETY, words
    assert "treated" in M.SEED_SAFETY and "mercury" in M.SEED_SAFETY
    assert "fishing licence and gear rules" in M.FIBRE_SAFETY


def test_every_book_licence_and_safety():
    for word, pdfs in M.AREAS.items():
        for g in pdfs:
            assert g["group"] == "homestead" and g["description"] and g["notice"], g["name"]
            assert SAFETY_OF[word] in g["notice"], (g["name"], word)
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short) or B.licence_kind(g["licence"]), g["name"]
            assert g["version"] and (g.get("published") or g.get("pdf")), g["name"]   # an AMS file: its own date
            if g.get("old_public_domain"):
                assert int(g["published"]) < 1931 and "Published in" in g["description"], g["name"]
                assert g["licence"] == "Public domain (published before 1931)", g["name"]
            elif g.get("military"):
                assert g["notice"].startswith(M.MIL_NOTICE) and g["work"], g["name"]
            else:
                assert g["licence"] == K.US_GOV and "public domain" in g["notice"], g["name"]
                assert g.get("archive") or g.get("pdf"), g["name"]
    for name in ("mason_aboriginal_american_basketry_1904",):
        assert "outdated and offensive" in M.COLLECTION.pdfs[name]["description"]
    assert M.COLLECTION.pdfs["watt_leather_manufacture_1906"]["country"] == "United Kingdom"


def test_meat_specifications_read_from_ams():
    imps = [p for p in M.MEAT_PDFS if p["name"].startswith("ams_imps_")]
    assert len(imps) == 6
    for p in imps:
        assert p["pdf"].startswith("https://www.ams.usda.gov/sites/default/files/media/") and p["pdf"].endswith(".pdf")
        assert p["page"] == M.IMPS_PAGE and "Agricultural Marketing Service" in p["publisher"]
        assert not p.get("archive"), p["name"]


def test_no_internet_archive_item_twice_or_elsewhere():
    items = [p["archive"] for p in M.PDFS if p.get("archive")]
    assert len(items) == len(set(items))
    others = {e["archive"] for e in sources.PDF_DOCS if e.get("archive")}
    for m in more_refs.modules():
        if m is not M:
            others |= {e["archive"] for e in m.COLLECTION.pdfs.values() if e.get("archive")}
    assert not set(items) & others, set(items) & others
    text = ""
    for name in os.listdir(HERE):
        if name.endswith(".py") and name not in ("homestead_fill.py", "test_homestead_fill.py"):
            with open(os.path.join(HERE, name), encoding="utf-8") as f:
                text += f.read()
    for item in items:
        assert f'"{item}"' not in text, item


def test_old_book_refused_after_1930(monkeypatch, tmp_path):
    """A made-up item whose record says 1931 is refused before anything is downloaded."""
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: ("https://archive.org/download/x/x.pdf",
                                                                    "https://archive.org/details/x"))
    monkeypatch.setattr(B, "archive_year", lambda ident, cache=None: 1931)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    left_out = []
    entry = dict(M.COLLECTION.pdfs["drew_farm_blacksmithing_1910"], archive="madeupitem")
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert "before 1931" in left_out[0]["reason"]


def test_military_book_keeps_the_release_line(monkeypatch):
    """The builder's notice (its truthful release line first) is not replaced by the entry's own notice; an old
    book's notice is the entry's."""
    def made_up_book(entry, work, cache=None, left_out=None):
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], "https://archive.org/details/made-up",
                          entry["description"], "Made-up release line. " + entry["notice"])
    monkeypatch.setattr(B, "pdfdoc_book", made_up_book)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    book = M.COLLECTION.book_for("hfill:army_tm_5_700_field_water_supply_1961", "work")
    assert book.notice.startswith("Made-up release line. The release line before this")
    old = M.COLLECTION.book_for("hfill:olcott_star_lore_1911", "work")
    assert old.notice == M.COLLECTION.pdfs["olcott_star_lore_1911"]["notice"]


def test_index_made_offline_with_keys_the_library_has(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for _part, _intro, rows in M.SECTIONS:
        for kind, what, *_rest in rows:
            if kind == "key":
                assert X.key_exists(what), what
    left_out = []
    book = M.INDEX[0]("index", "work", None, left_out)
    assert len(book.pages) == len(M.SECTIONS) == 7 and not left_out and book.licence == X.CC0_INDEX
    body = " ".join(p.body for p in book.pages)
    for words in ("commons_forge_traps_tanning", "commons_homestead_stores", "commons_stars_navigation",
                  "pub:usda_farmers_bulletins:1970s", "olife:usda_yearbook_1961_seeds", '<a href="https://'):
        assert words in body, words
    listed = {row[1] for _p, _i, rows in M.SECTIONS for row in rows if row[0] == "key"}
    assert {f"hfill:{p['name']}" for p in M.PDFS} <= listed     # every book of the module is in the index
    assert M.INDEX[1]("index") == M.INDEX[1]("index")


def test_not_included_rows():
    rows = " ".join(r[0] + " " + r[1] for r in M.NOT_INCLUDED)
    for words in ("FSIS", "Extension", "trapper education", "msi.nga.mil", "Nautical Almanac", "remote medicine",
                  "service skills", "skill:army_tb_med_577_field_water_supplies_2010", "pub:usda_farmers_bulletins", "SODIS"):
        assert words in rows, words
    assert not re.search(r"\bhfill:(?!index|usfs_woody)", rows)    # nothing listed as left out is also built
