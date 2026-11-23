"""Self-test of the remote and long-term-care medicine books (remote_medicine.py, rmed:), with MADE-UP data only:
nothing is downloaded.

It checks that the module is registered once, in its own group, under its overall request word and its four theme
words (each at most 256 jobs, together exactly every key); that every book has a licence the toolkit may repackage, a
description and a notice with the owner's words ("For when no professional help is available ...") and its edition's
date and what may be out of date; that web guides' page patterns match their own addresses; that the military
publications go through the release rule (military=True) without claiming a release line themselves, and that a
made-up Joint Trauma System list picks the newest guideline of each name (never the unexploded ordnance one); that
the NCTSN field guides are kept whole, unchanged and personal use only, with their permission line checked in the
PDF; that nothing repeats another module's pages, sites or Internet Archive items; that the index is made offline
with keys the library has; and that every NOT_INCLUDED row says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_remote_medicine.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import military_release  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import remote_medicine as R  # noqa: E402
import sources  # noqa: E402

THEMES = ("rmed-ship", "rmed-austere", "rmed-pfa", "rmed-nursing")


def books():
    """Every web guide and PDF entry of the module."""
    return list(R.COLLECTION.guides.values()) + list(R.COLLECTION.pdfs.values())


def test_registered_with_theme_words():
    assert R in more_refs.modules() and more_refs.MODULES.count("remote_medicine") == 1
    assert [m.COLLECTION.prefix for m in more_refs.modules()].count("rmed") == 1
    every = sources.expand_keys(["remote-medicine"])
    assert every == R.COLLECTION.expand_keys(["remote-medicine"]) and len(every) == len(set(every)) <= 256
    assert set(every) == set(R.COLLECTION.own_keys())
    union = set()
    for word in THEMES:
        keys = sources.expand_keys([word])
        assert 1 < len(keys) == len(set(keys)) <= 256 and keys[0] == "rmed:index", word
        union |= set(keys)
    assert union == set(every)
    assert sources.GROUPS["remotemed"] == "Reference, remote and long-term care medicine"
    assert set(R.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.NO_CHANGES[R.NCTSN_LICENCE] == "non-commercial-no-changes"


def test_notice_says_what_the_owner_asked():
    assert R.REMOTE_NOTE.startswith("For when no professional help is available; follow current medical guidance "
                                    "and get professional care as soon as possible")
    for words in ("call 911", "VHF channel 16", "personal locator beacon", "not medical training"):
        assert words in R.REMOTE_NOTE, words


def test_every_book():
    for g in books():
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, bool(g.get("unchanged"))) or B.licence_kind(g["licence"]), g["name"]
        assert g["group"] == R.GROUP and g["description"] and R.REMOTE_NOTE in g["notice"], g["name"]
        if g.get("old_public_domain"):              # an old book: its description says its year and what is old
            assert re.search(r"Published in \d{4}|Edition of \d{4}", g["description"] + g["notice"]), g["name"]
            assert int(g["published"]) < 1931, g["name"]
        else:                                       # the edition's date (or the day web pages were read)
            assert re.search(r"Edition( of \d{4}| of the newest|:)", g["notice"]), g["name"]
        if g["name"] in R.COLLECTION.guides:
            assert g["licence_page"] and g["licence_text"], g["name"]
            pattern = re.compile(g["pages"])
            starts = [s for s, _d in g.get("crawl") or [] if not s.endswith("/site.html")]   # a CDC site index
            for url in g.get("urls", []) + starts:                                           # is not a page
                assert pattern.match(url), (g["name"], url)
        elif g["licence"] == R.NCTSN_LICENCE:
            assert g["pdf_licence_text"] and g["archive"], g["name"]
        else:
            assert ((g.get("licence_page") or g.get("page")) and g.get("licence_text")) or g.get("old_public_domain"), \
                g["name"]
            assert g.get("archive") or g.get("page"), g["name"]


def test_military_books_follow_the_release_rule():
    military = [g for g in books() if g.get("military")]
    names = {g["name"] for g in military}
    assert {"army_emergency_war_surgery_2004", "socom_sof_medical_handbook_2001", "usariem_cold_weather_1992",
            "jts_prolonged_casualty_care", "jts_forward_mental_health"} <= names
    for g in military:
        assert "approved for public release" not in g["notice"].lower(), g["name"]
        assert not g.get("distribution_a") and g.get("work"), g["name"]
    # A copy read from the Joint Trauma System's own .mil site, printing no statement, is public with a true line.
    rule = military_release.release_rule("JOINT TRAUMA SYSTEM CLINICAL PRACTICE GUIDELINE Made-up care guideline",
                                         R.JTS + "/assets/docs/cpgs/Made_Up_PFC_01_Jan_2026.pdf",
                                         "a work of the US Department of Defense")
    assert rule.verdict == "public" and "jts.health.mil" in rule.release
    assert "approved for public release" not in rule.release.lower()


def test_jts_list_picks_the_newest_and_never_explosives():
    page = "".join(f'<a href="/assets/docs/cpgs/{f}">x</a>' for f in (
        "Prolonged_Casualty_Care_Guidelines_21_Dec_2021_ID91.pdf",
        "Prolonged_Casualty_Care_Guidelines_09_Jan_2027_ID91v2.pdf",
        "Eye_Trauma_Initial_Care_01_Jun_2021_ID03.pdf", "Eye_Trauma_Initial_Care_Infographic_21_Apr_2026.pdf",
        "Unexploded_Ordnance_(UXO)_Management_14_Mar_2017_ID41.pdf", "K9_Hypothermia_CPG_C10_22_June_2026.pdf",
        "Hypothermia_Prevention_Treatment_07_Jun_2023_ID23.pdf"))
    pdfs = R.COLLECTION.pdfs
    assert B.newest_pdf(page, R.JTS_PAGE, pdfs["jts_prolonged_casualty_care"]["pdf_pattern"]).endswith("2027_ID91v2.pdf")
    assert B.newest_pdf(page, R.JTS_PAGE, pdfs["jts_eye_trauma_initial_care"]["pdf_pattern"]).endswith("ID03.pdf")
    assert B.newest_pdf(page, R.JTS_PAGE, pdfs["jts_hypothermia"]["pdf_pattern"]).endswith("ID23.pdf")
    for g in pdfs.values():
        if g.get("pdf_pattern"):
            assert not re.search(g["pdf_pattern"], R.JTS + "/assets/docs/cpgs/Unexploded_Ordnance_(UXO)_Management_"
                                 "14_Mar_2017_ID41.pdf"), g["name"]
            assert not re.search(g["pdf_pattern"], R.JTS + "/assets/docs/cpgs/K9_Hypothermia_CPG_C10_22_June_2026"
                                 ".pdf"), g["name"]


def test_nctsn_guides_whole_unchanged_personal_use():
    guides = [g for g in books() if g["licence"] == R.NCTSN_LICENCE]
    assert len(guides) == 3
    made_up = ("Copyright (c) 2099 Made-up Authors. All rights reserved. You are welcome to copy or redistribute this "
               "material in print or electronically provided the text is not modified.")
    for g in guides:
        assert g["personal_use"] and g["unchanged"] and "PERSONAL USE ONLY" in g["notice"], g["name"]
        assert B.licence_kind(g["licence"], True) == "non-commercial-no-changes" and not B.licence_kind(g["licence"])
        assert re.search(g["pdf_licence_text"], made_up) and not re.search(g["pdf_licence_text"], "All rights "
                                                                                                  "reserved.")
        assert "personal use only" in B.licence_words(g["licence"], True, True)


def test_ship_and_ogl_books():
    pdfs = R.COLLECTION.pdfs
    years = {pdfs[n]["published"] for n in ("ships_medicine_chest_1904", "ships_medicine_chest_1929",
                                            "ships_medicine_chest_1940", "ships_medicine_chest_2003")}
    assert years == {"1904", "1929", "1940", "2003"}
    msn = pdfs["uk_mca_msn_1905_ships_medical_stores"]
    assert re.search(msn["pdf_pattern"], "https://assets.publishing.service.gov.uk/media/x/MSN_1905__M+F__Amendment_6"
                                         ".pdf")
    assert msn["licence"] == "OGL-UK-3.0" and re.search(msn["licence_text"], "the Open Government Licence v3.0")
    mgn = R.COLLECTION.guides["uk_mca_medical_notices_at_sea"]
    assert mgn["licence"] == "OGL-UK-3.0" and mgn["licence_page"] == mgn["urls"][0]
    assert mgn["country"] == "United Kingdom"


def test_cdc_and_fda_books():
    cdc = R.COLLECTION.guides["cdc_outbreak_diseases"]
    pattern = re.compile(cdc["pages"])
    assert pattern.match("https://www.cdc.gov/cholera/prevention/index.html")
    assert not pattern.match("https://www.cdc.gov/cholera/hcp/case-definition/index.html")     # pages for doctors
    assert not pattern.match("https://www.cdc.gov/cholera/es/index.html")                      # Spanish copies
    assert cdc["unchanged"] and "Source: CDC" in cdc["notice"]
    fda = R.COLLECTION.guides["fda_using_medicines_safely"]
    assert re.search(fda["licence_text"], "They are in the public domain and may be republished, reprinted and "
                                          "otherwise used freely by anyone")


def test_no_repeats_of_other_modules():
    """No page, starting address or Internet Archive item here is another module's, and no CDC site is read twice."""
    others = [g for m in more_refs.modules() if m is not R
              for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())]
    others += sources.PDF_DOCS
    their_urls = {u if isinstance(u, str) else u[0] for g in others for u in g.get("urls", [])}
    their_starts = {s for g in others for s, _d in g.get("crawl") or []}
    their_archives = {g.get("archive") for g in others} - {None}
    their_pdfs = {g.get("pdf") for g in others} - {None}
    for g in books():
        assert not set(g.get("urls", [])) & their_urls, g["name"]
        assert not {s for s, _d in g.get("crawl") or []} & their_starts, g["name"]
        assert g.get("archive") not in their_archives, g["name"]
        assert g.get("pdf") not in their_pdfs, g["name"]
    for site in R.OUTBREAK_SITES:
        start = f"https://www.cdc.gov/{site}/site.html"
        assert start not in their_starts, site


def test_index_book_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    book_fn, sign_fn = R.COLLECTION.makers["index"]
    left_out = []
    book = book_fn("index", "work", None, left_out)
    assert book.licence == X.CC0_INDEX and not left_out, left_out
    assert len(book.pages) == len(R.SECTIONS) and sign_fn("index")
    text = " ".join(p.body for p in book.pages)
    assert '<a href="https://' in text and "Psychological first aid" in " ".join(p.title for p in book.pages)
    linked = {e[1] for _p, _i, items in R.SECTIONS for e in items}
    for key in [f"rmed:{n}" for n in list(R.COLLECTION.guides) + list(R.COLLECTION.pdfs)]:
        assert key in linked or key.startswith("rmed:jts_"), key       # every book but the many JTS ones by name
    for key in ("firstaid:cdc_yellow_book", "wild:army_tb_med_508_cold", "homecare:va_caregiver_support",
                "gpo:samhsa_trouble_coping_after_disaster_2007", "first-aid", "wilderness-first-aid", "rmed-austere"):
        assert key in linked, key
    for _p, _i, items in R.SECTIONS:
        for kind, what, *_rest in items:
            if kind == "key":
                assert X.key_exists(what), what


def test_not_included():
    for row in R.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in R.NOT_INCLUDED)
    for words in ("International Medical Guide for Ships", "Ship Captain's Medical Guide", "Borden Institute",
                  "Open RN", "Tactical Combat Casualty Care", "Navy Diving Manual"):
        assert words in names, words
