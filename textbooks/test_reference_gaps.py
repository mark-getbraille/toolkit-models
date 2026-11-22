"""Self-test of the eight reference-gap collections (the owner's request of 2026-11-22), each in its own module and
group: world geography (geography.py, geo:), pet care (pet_care.py, pet:), genealogy (genealogy.py, gen:), audio and
media production (audio_media.py, media:), typing and keyboard skills (typing_skills.py, typing:), recycling and waste
(recycling.py, recycle:), game and fish processing (game_fish.py, gamefish:) and holidays and observances
(holiday_observances.py, holiday:). With MADE-UP data only: nothing is downloaded.

It checks that each module is registered once under its request word (at most 256 jobs) with its own group, and
reaches sources.py with its licence lines and NOT_INCLUDED rows (each with an address); that every book has a licence
the toolkit may repackage, a description, a notice with the module's safety or records note, and a licence page and
line; that page patterns match their own addresses and leave out what they should; that the EPA and Canadian books
are personal use only and the share-alike books (OSARA, Wikipedia) say so; that the old books are dated before 1931
and say what is out of date; that the index books are made offline with keys the library has; and that the World
Factbook book is made from made-up pages, with its index by continent, the map in words and the military section
kept, and refused when its licence lines are gone.

Run it from the repository's folder:   python3 -m pytest textbooks/test_reference_gaps.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import audio_media  # noqa: E402
import game_fish  # noqa: E402
import genealogy  # noqa: E402
import geography  # noqa: E402
import holiday_observances  # noqa: E402
import pet_care  # noqa: E402
import recycling  # noqa: E402
import typing_skills  # noqa: E402

MODULES = [(geography, "geography", "geo"), (pet_care, "pet-care", "pet"), (genealogy, "genealogy", "gen"),
           (audio_media, "audio-media", "media"), (typing_skills, "typing", "typing"),
           (recycling, "recycling", "recycle"), (game_fish, "game-fish", "gamefish"),
           (holiday_observances, "holidays", "holiday")]


def entries(m):
    """Every web guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered_each_in_its_own_group():
    groups = set()
    for m, word, prefix in MODULES:
        assert m in more_refs.modules(), m.__name__
        keys = sources.expand_keys([word])
        assert keys == m.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
        assert set(keys) == set(m.COLLECTION.own_keys()), word
        assert all(k.startswith(prefix + ":") for k in keys) and f"{prefix}:index" in keys, word
        assert len(m.GROUPS) == 1 and m.COLLECTION.group in m.GROUPS, word
        assert sources.GROUPS[m.COLLECTION.group] == m.GROUPS[m.COLLECTION.group], word
        groups.add(m.COLLECTION.group)
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES), word
    assert len(groups) == len(MODULES)
    names = [sources.GROUPS[g] for g in groups]
    for title in ("Reference, world geography", "Reference, pet care", "Reference, genealogy",
                  "Reference, audio and media production", "Reference, typing and keyboard skills",
                  "Reference, recycling and waste", "Reference, game and fish processing",
                  "Reference, holidays and observances"):
        assert title in names, title


def test_every_book_has_an_allowed_licence_and_its_note():
    notes = {pet_care: pet_care.NOTE, genealogy: genealogy.NOTE, recycling: recycling.NOTE, game_fish: game_fish.NOTE}
    for m, word, _prefix in MODULES:
        for g in entries(m):
            assert g["group"] == m.COLLECTION.group, g["name"]
            whole = bool(g.get("unchanged"))
            short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
            assert B.licence_kind(short, whole), (g["name"], g["licence"])
            assert g["notice"] and g["description"], g["name"]
            if not g.get("old_public_domain"):
                assert g["licence_page"] and g["licence_text"], g["name"]
            if m in notes:
                assert notes[m] in g["notice"], g["name"]
            for url in g.get("urls") or []:
                assert re.match(g["pages"], url), (g["name"], url)


def test_safety_words():
    assert "Treat every gun as loaded" in game_fish.NOTE and "chronic wasting disease" in game_fish.NOTE
    assert "hunter education" in game_fish.NOTE and "fish advisories" in game_fish.NOTE
    assert "veterinarian" in pet_care.NOTE and "poison control" in pet_care.NOTE
    assert "Lithium" in recycling.NOTE and "never mix cleaning products" in recycling.NOTE
    assert "check with the office" in genealogy.NOTE


def test_personal_use_and_share_alike():
    personal = {(m.__name__, g["name"]) for m, _w, _p in MODULES for g in entries(m) if g.get("personal_use")}
    assert personal == {("recycling", "epa_recycling_household_waste"), ("game_fish", "epa_fish_advisories"),
                        ("holiday_observances", "canada_public_holidays")}
    for m, _w, _p in MODULES:
        for g in entries(m):
            if g.get("personal_use"):
                assert "ersonal use only" in g["notice"], g["name"]
    osara = audio_media.COLLECTION.guides["osara_guide"]
    assert osara["licence"] == "GPL-2.0" and "share-alike" in osara["notice"]
    wiki = holiday_observances.COLLECTION.guides["wikipedia_observances"]
    assert wiki["licence"] == "CC BY-SA 4.0" and "share-alike" in wiki["notice"]
    assert audio_media.COLLECTION.guides["wai_media_accessibility"]["unchanged"]
    for name in ("cdc_where_to_write_vital_records",):
        assert genealogy.COLLECTION.guides[name]["unchanged"]


def test_old_books():
    for m, _w, _p in MODULES:
        for p in m.COLLECTION.pdfs.values():
            if p.get("old_public_domain"):
                assert int(p["published"]) < 1931 and p["archive"], p["name"]
                assert "out of date" in p["description"] or "do not apply" in p["description"] or \
                    "views of its time" in p["description"], p["name"]
    crs = holiday_observances.COLLECTION.pdfs["crs_federal_holidays_evolution"]
    assert crs["archive"] == "crs-r41990.11" and crs["licence"] == sources.US_GOV


def test_page_patterns():
    fda = re.compile(pet_care.COLLECTION.guides["fda_pet_health"]["pages"])
    assert fda.match("https://www.fda.gov/animal-veterinary/animal-health-literacy/paws-xylitol-toxic-dogs")
    assert not fda.match("https://www.fda.gov/animal-veterinary/animal-health-literacy/cvm-kids-page")
    aud = re.compile(audio_media.COLLECTION.guides["audacity_manual"]["pages"])
    assert aud.match("https://manual.audacityteam.org/man/recording.html")
    assert not aud.match("https://manual.audacityteam.org/man/license.html")
    nara = re.compile(genealogy.COLLECTION.guides["nara_genealogy"]["pages"])
    for url in ("https://www.archives.gov/research/census/1950", "https://www.archives.gov/research/military/ww2",
                "https://www.archives.gov/veterans/military-service-records/about-service-records.html"):
        assert nara.match(url), url
    assert not nara.match("https://www.archives.gov/research/jfk")
    w2w = re.compile(genealogy.COLLECTION.guides["cdc_where_to_write_vital_records"]["pages"])
    assert w2w.match("https://www.cdc.gov/nchs/w2w/american_samoa.htm")
    epa = re.compile(recycling.COLLECTION.guides["epa_recycling_household_waste"]["pages"])
    assert epa.match("https://www.epa.gov/recycle/composting-home")
    assert not epa.match("https://www.epa.gov/recycle/forms/contact-us-about-reduce-reuse-recycle")
    cdc = re.compile(game_fish.COLLECTION.guides["cdc_wild_game_diseases"]["pages"])
    assert cdc.match("https://www.cdc.gov/trichinellosis/prevention/index.html")
    assert not cdc.match("https://www.cdc.gov/brucellosis/hcp/clinical-overview/index.html")


def test_index_books_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for m, _w, _p in MODULES:
        book_fn, _sign_fn = m.COLLECTION.makers["index"]
        left_out = []
        book = book_fn("index", "work", None, left_out)
        assert book.pages and book.licence == X.CC0_INDEX and not left_out, (m.__name__, left_out)
        assert '<a href="https://' in " ".join(p.body for p in book.pages), m.__name__
    single = set(sources.expand_keys(["cookbooks"])) | {"med:animal"}   # book keys named as words
    for m, _w, _p in MODULES:                 # every request word named in an index is one the library knows
        for _part, _intro, items in m.SECTIONS:
            for kind, what, *_rest in items:
                if kind == "word":
                    assert what in single if ":" in what else sources.expand_keys([what]) != [what], what


def test_index_links():
    linked = {e[1] for m, _w, _p in MODULES for _part, _intro, items in m.SECTIONS for e in items}
    for key in ("vision:index", "home:aphis_pets", "med:animal", "commons_breeds", "pet_livestock_supplies",
                "atdoc:nvda_key_commands", "audio_gear", "geo:factbook", "garden:nrcs_soil_health",
                "outdoors:fws_hunting_fishing", "firearms", "commons_us_holidays", "holidays"):
        assert key in linked, key


def test_not_included():
    for m, _w, _p in MODULES:
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], (m.__name__, row[0])


# ====================================================================== the World Factbook (made-up pages)

FAKE_COUNTRY = {
    "Introduction": {"Background": {"text": "Made-up land is a <strong>made-up</strong> country."}},
    "Geography": {"Location": {"text": "Western Made-up Sea, between A and B"},
                  "Geographic coordinates": {"text": "1 00 N, 2 00 E"},
                  "Area - comparative": {"text": "slightly smaller than Delaware"},
                  "Land boundaries": {"total": {"text": "10 km"}, "border countries (1)": {"text": "Other land 10 km"}}},
    "Government": {"Country name": {"conventional short form": {"text": "Madeupland"}},
                   "Capital": {"name": {"text": "Testville"}}},
    "Military and Security": {"Military and security forces": {"text": "Made-up Defence Force (2025)"}},
}


def fake_fetch(readme="offers free country profiles in the public domain", licence="CC0 1.0 Universal"):
    """A made-up fetch: the read-me, the licence file and two country pages; any other address gives nothing."""
    def get(url):
        if url.endswith("/README.md"):
            return readme
        if url.endswith("/LICENSE.md"):
            return licence
        if url.endswith("/africa/ag.json") or url.endswith("/europe/fr.json"):
            return json.dumps(FAKE_COUNTRY)
        return ""
    return get


def test_factbook_regions():
    assert sum(len(v) for v in geography.REGION_CODES.values()) == 261
    assert {f for f, _r, _c in geography.REGIONS} == set(geography.REGION_CODES)
    assert geography.REGION_CODES["north-america"]["us"] == "United States"
    assert len(geography.FB_COMMIT) == 40 and geography.FB_COMMIT in geography.FB_RAW


def test_factbook_book_from_made_up_pages():
    left_out = []
    book = geography.factbook_book("factbook", "work", None, left_out, fetch=fake_fetch())
    titles = [p.title for p in book.pages]
    assert titles[:2] == ["Index: Africa", "Index: Europe"] and titles.count("Madeupland") == 2
    page = book.pages[2]
    assert page.unit == "Africa" and page.path == "africa-ag-madeupland"
    for words in ("The map in words", "slightly smaller than Delaware", "border countries (1): Other land 10 km",
                  "Testville", "Military and Security", "Made-up Defence Force", "<strong>made-up</strong>"):
        assert words in page.body, words
    assert 'href="africa-ag-madeupland"' in book.pages[0].body
    assert len(left_out) == 259 and book.licence == sources.US_GOV and "retired" in book.notice
    assert book.version.startswith("factbook.json commit 144d697")


def test_factbook_refused_without_its_licence_lines():
    for get in (fake_fetch(readme="all rights reserved"), fake_fetch(licence="MIT License")):
        left_out = []
        assert geography.factbook_book("factbook", "work", None, left_out, fetch=get) is None
        assert "not built" in left_out[0]["reason"]


def test_factbook_clean_keeps_only_simple_tags():
    assert geography.clean('<a href="x">link</a> <strong>b</strong><script>x</script>') == \
        "link <strong>b</strong>x"
