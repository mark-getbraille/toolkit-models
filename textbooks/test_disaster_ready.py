"""Self-test of the emergency preparedness and disaster books (disaster_ready.py), with MADE-UP data only: nothing is
downloaded.

It checks that every book is registered once under its request word "disasters" (at most 256 jobs) and reaches
sources.py with its group "Reference, emergency preparedness and disasters", without repeating the four books of
emergency_prep.py ("preparedness"); that every book has a licence the toolkit may repackage, a notice with the safety
words (local officials, generators 20 feet away and carbon monoxide, floodwater, power lines, 911) and a description;
that the EPA book is personal use only; that the page patterns take Ready.gov's own pages and leave out translations,
business, kids, toolkits and webinars; that the potassium iodide words say "only when officials tell you"; that the
"Where to find more" book is made from the list, records no originals (nothing was read from those sites, so none may
be marked downloadable) and names the Church's guides as link-only for its terms; and that every row of NOT_INCLUDED
says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_disaster_ready.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import disaster_ready as D  # noqa: E402
import emergency_prep as E  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402


def test_registered():
    assert "disaster_ready" in more_refs.MODULES and D in more_refs.modules()
    assert sources.GROUPS["emergency"] == "Reference, emergency preparedness and disasters"
    keys = sources.expand_keys(["disasters"])
    assert keys == D.COLLECTION.expand_keys(["disasters"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"ready:{n}" for n in D.COLLECTION.guides} | {"ready:where_to_find_more"}
    assert not set(keys) & set(sources.expand_keys(["preparedness"]))
    assert set(D.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in D.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_licences_and_safety_notes():
    for words in ("local officials", "20 feet", "carbon monoxide", "911", "turn around, don't drown",
                  "downed power lines"):
        assert words in D.SAFETY_NOTE, words
    assert "1-800-985-5990" in D.RECOVERY_NOTE and "988" in D.RECOVERY_NOTE
    for g in D.GUIDES:
        assert g["group"] == "emergency", g["name"]
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short), g["name"]
        assert g["notice"] and g["description"] and g["title"] and g["subject"], g["name"]
        assert g["licence_page"] and g["licence_text"], g["name"]
        if g["name"] != "cisa_active_shooter":
            assert D.SAFETY_NOTE in g["notice"], g["name"]
        else:
            assert "911" in g["notice"]
    epa = D.COLLECTION.guides["epa_disasters_smoke"]
    assert epa["personal_use"] and "Personal use only" in epa["notice"]
    assert B.licence_kind(B.licence_short(epa["licence"])) == "non-commercial"
    nrc = D.COLLECTION.guides["nrc_radiological_emergencies"]
    assert "only when your state or local" in nrc["notice"]
    assert D.RECOVERY_NOTE in D.COLLECTION.guides["ready_gov"]["notice"]
    assert D.RECOVERY_NOTE in D.COLLECTION.guides["sba_disaster_loans"]["notice"]


def test_page_patterns():
    ready = re.compile(D.READY_PAGES)
    for slug in ("plan", "kit", "hurricanes", "power-outages", "people-disabilities", "older-adults", "pets",
                 "financial-preparedness", "shelter", "evacuation", "recovering-disaster", "radiation", "cert"):
        assert ready.match(f"https://www.ready.gov/{slug}"), slug
    for slug in ("es/kit", "kids/games", "business/emergency-plans", "hurricane-toolkit", "collection/build-a-kit",
                 "community-preparedness-webinar-series-pets-2011", "2026-national-preparedness-month-partner-toolkit",
                 "terms-and-conditions", "today-ohio", "radiological-dispersion-device-old"):
        assert not ready.match(f"https://www.ready.gov/{slug}"), slug
    for part, slugs in D.READY_PARTS:
        for slug in slugs:
            assert ready.match(f"https://www.ready.gov/{slug}"), slug
    nrc = re.compile(D.COLLECTION.guides["nrc_radiological_emergencies"]["pages"])
    assert nrc.match("https://www.nrc.gov/about-nrc/emerg-preparedness/in-radiological-emerg")
    assert nrc.match("https://www.nrc.gov/about-nrc/emerg-preparedness.html")
    assert not nrc.match("https://www.nrc.gov/about-nrc/emerg-preparedness/rulemaking-for-emergency")
    aspr = re.compile(D.COLLECTION.guides["aspr_at_risk_empower"]["pages"])
    assert aspr.match("https://aspr.hhs.gov/at-risk/Pages/service_animals.aspx")
    assert not aspr.match("https://aspr.hhs.gov/at-risk/Pages/elderly_disabled_spanish.aspx")
    assert aspr.match("https://empowerprogram.hhs.gov/about.html")
    epa = re.compile(D.COLLECTION.guides["epa_disasters_smoke"]["pages"])
    assert epa.match("https://www.epa.gov/natural-disasters/flooding")
    assert epa.match("https://www.epa.gov/emergencies-iaq/create-clean-room-protect-indoor-air-quality-during-wildfire")
    assert not epa.match("https://www.epa.gov/natural-disasters/forms/contact-epa-about-natural-disasters")
    for g in D.GUIDES:
        pattern = re.compile(g["pages"])
        for url in g.get("urls", []):
            assert pattern.match(url if isinstance(url, str) else url[0]), (g["name"], url)


def test_links_book():
    book = D.links_book("where_to_find_more", "/tmp/none", None, [])
    assert len(book.pages) == len(D.LINK_ONLY) and book.licence == "CC0 1.0"
    assert book.originals == [] and "toolkit-models" in book.source
    assert D.SAFETY_NOTE in book.notice
    church = [row for row in D.LINK_ONLY if "Latter-day Saints" in row[0] + row[1]]
    assert len(church) >= 3 and all("fetch" in row[2] for row in church)
    assert all(row[3].startswith("https://") for row in church)
    first = book.pages[0]
    assert "<dt>Address</dt>" in first.body and D.LINK_ONLY[0][3] in first.body
    assert any("LDS Preparedness Manual" in title for title, _r in D.NOT_INCLUDED)
    # nothing of the excluded hosts is read: no guide or PDF of this module points at them
    for g in D.GUIDES:
        assert not re.search(r"churchofjesuschrist|redcross|usu\.edu|byu\.edu", g["source"] + g["pages"])


def test_no_book_repeats_emergency_prep():
    mine = {g["source"] for g in D.GUIDES}
    theirs = {g["source"] for g in E.GUIDES}
    assert not mine & theirs
