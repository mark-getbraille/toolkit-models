"""Self-test of the small boats books (small_boats.py, boat:, group "Reference, small boats"), with MADE-UP data only:
nothing is downloaded.

It checks that the module is registered once under its request word (at most 256 jobs) and reaches sources.py with
its group, licence lines and NOT_INCLUDED rows (each with an address); that every book has a licence the toolkit may
repackage, a description and a notice with every boating safety note the owner asked for (life jacket, weather,
float plan, cold water, never under the influence, carbon monoxide), and the building and engine books the workshop
note (epoxy, solvents); that the military manuals are judged by the release rule and keep the builder's release
line; that the old books are dated before 1931 and say what is out of date; that the web guides' page lists match
their patterns; that the federal regulations are read through build_textbooks.lawdoc_book with the right parts
(tried with a made-up book); that the index is made offline, lists only keys the library has and links the knots,
wilderness first aid, trailer and engine collections; and that no book here is one of the Admiralty manuals whose US
copyright may have been restored (those are knots_military.py's, marked us_restoration_risk).

Run it from the repository's folder:   python3 -m pytest textbooks/test_small_boats.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import knots_military  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import small_boats as S  # noqa: E402
import sources  # noqa: E402

SAFETY = ("life jacket", "Check the weather", "float plan", "Cold water kills", "under the influence",
          "carbon monoxide", "VHF channel 16")
WORKSHOP = ("epoxy", "solvents", "respirator", "safety data sheet")


def entries():
    """Every web guide, PDF and regulation entry of the module."""
    return list(S.COLLECTION.guides.values()) + list(S.COLLECTION.pdfs.values()) + list(S.LAWS.values())


def test_registered_in_its_group():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert S in more_refs.modules() and prefixes.count("boat") == 1
    keys = sources.expand_keys(["small-boats"])
    assert 0 < len(keys) == len(set(keys)) <= 256 and set(keys) == set(S.COLLECTION.own_keys())
    assert sources.GROUPS["boats"] == "Reference, small boats" and S.GROUPS == {"boats": "Reference, small boats"}
    assert set(S.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in S.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_every_book_licence_and_safety():
    for g in entries():
        assert g["group"] == "boats" and g["description"] and g["notice"], g["name"]
        assert B.licence_kind(B.licence_short(g["licence"])) or B.licence_kind(g["licence"]), g["name"]
        for words in SAFETY:
            assert words in g["notice"], (g["name"], words)
        assert not g.get("us_restoration_risk") and not g.get("uk_crown_expired"), g["name"]
    for name in ("stephens_canoe_boat_building_1889", "miller_boys_book_canoeing_sailing_1917",
                 "slauson_motor_boat_1911", "army_fm_55_509_1_marine_electricity_1994"):
        for words in WORKSHOP:
            assert words in S.COLLECTION.pdfs[name]["notice"], (name, words)


def test_old_books_and_military_manuals():
    for name, p in S.COLLECTION.pdfs.items():
        if p.get("old_public_domain"):
            assert int(p["published"]) < 1931 and f"Published in {p['published']}" in p["description"], name
            assert p["archive"] and p["licence"] == "Public domain (published before 1931)", name
        elif p.get("archive"):
            assert p.get("military") or p.get("distribution_a"), name
            assert "front pages print" in p["notice"] and p["published"] and p["version"], name
        else:
            assert p["pdf"].startswith("https://nauticalcharts.noaa.gov/") and "not that official copy" in p["notice"]
    for name in ("army_fm_55_501_marine_crewman_1999", "army_fm_55_130_small_boats_1944",
                 "army_fm_55_502_watercraft_safety_1996", "army_fm_55_509_1_marine_electricity_1994"):
        p = S.COLLECTION.pdfs[name]
        assert p["distribution_a"] and not p.get("keep_parts"), name     # whole; only explosives parts are cut
    # the Admiralty manuals of 1951 to 1972 stay in knots_military.py, never repeated here
    crown = {p["archive"] for p in knots_military.COLLECTION.pdfs.values() if p.get("us_restoration_risk")}
    assert crown and not crown & {p.get("archive") for p in S.COLLECTION.pdfs.values()}


def test_military_book_keeps_the_release_line(monkeypatch):
    """The builder's notice (its truthful release line first) is not replaced by the entry's own notice."""
    def made_up_book(entry, work, cache=None, left_out=None):
        return K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], "https://archive.org/details/made-up",
                          entry["description"], "Made-up release line. " + entry["notice"])
    monkeypatch.setattr(B, "pdfdoc_book", made_up_book)
    monkeypatch.setattr(D, "ai_refused", lambda url, cache=None: False)
    book = S.COLLECTION.book_for("boat:uscg_bch_navigation_piloting", "work")
    assert book.notice.startswith("Made-up release line. The release line before this")
    old = S.COLLECTION.book_for("boat:frazar_practical_boat_sailing_1879", "work")
    assert old.notice == S.COLLECTION.pdfs["frazar_practical_boat_sailing_1879"]["notice"]


def test_web_guides_page_lists():
    for g in S.COLLECTION.guides.values():
        pattern = re.compile(g["pages"])
        assert g["urls"] and all(pattern.match(u) for u in g["urls"]), g["name"]
        assert not pattern.match("https://oceanservice.noaa.gov/facts/tides.html"), g["name"]
    nws = S.COLLECTION.guides["nws_marine_weather"]
    assert nws["licence_page"] == "https://www.weather.gov/disclaimer"
    assert re.search(nws["licence_text"], "National Weather Service (NWS) Web pages are in the public domain")


def test_regulations_read_through_lawdoc_book(monkeypatch):
    seen = []

    def made_up_lawdoc(entry, cache=None, left_out=None):
        seen.append(entry)
        book = K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], entry["source"], entry["description"],
                          entry["notice"])
        book.pages = [B.Page(f"p{i}", f"Made-up part {i}", "<p>Made up.</p>", i, "") for i in range(5)]
        return book
    monkeypatch.setattr(B, "lawdoc_book", made_up_lawdoc)
    book = S.COLLECTION.book_for("boat:cfr_inland_navigation_rules", "work", limit=2)
    assert len(book.pages) == 2 and book.name == "boat_cfr_inland_navigation_rules"
    assert [c["part"] for c in seen[0]["cfr"]] == [83, 84, 85, 86, 87, 88]
    parts = {(c["title"], c["part"]) for c in S.LAWS["cfr_recreational_boat_rules"]["cfr"]}
    assert parts == {(33, 175), (33, 183), (46, 25)}
    for entry in S.LAWS.values():
        assert entry["licence"] == K.US_GOV and entry["licence_page"] == K.GOVINFO_POLICY and entry["split"]


def test_index_offline_and_links(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    book_fn, sign_fn = S.COLLECTION.makers["index"]
    left_out = []
    book = book_fn("index", "work", None, left_out)
    assert book.pages and not left_out, left_out
    assert sign_fn("index") == K.sha(S.SECTIONS)
    text = " ".join(p.body for p in book.pages)
    for key in ("knot:index", "kmil:uscg_bch_seamanship_fundamentals", "wild:army_tb_med_508_cold",
                "wilderness-first-aid", "rvs:army_tm_m1101_trailer", "small_engines", "powersports",
                "outdoors:uscg_boating_safety", "pdf:noaa_us_chart_no_1", "commons_small_boats", "small_boats"):
        assert key in text, key
    own = set(S.COLLECTION.own_keys())
    for _part, _intro, items in S.SECTIONS:
        for kind, what, *_rest in items:
            if kind == "key" and what.startswith("boat:"):
                assert what in own, what
