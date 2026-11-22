"""Self-test of the travel books (travel.py) and the citizenship and civics books (civics.py), with MADE-UP data only:
nothing is downloaded.

It checks that both modules are registered once under their request words "travel" and "civics" (at most 256 jobs
each), with their own key prefixes ("trip", never transport_rights.py's "travel:") and groups; that every book has a
licence the toolkit may repackage, a notice, a description, a licence page and line, and a page pattern that takes
its own addresses and leaves out other topics; that every civics book's notice ends with the not-advice line; that
the USCIS PDFs are read from the Wayback Machine's exact copies ("id_") of their official addresses; that Discover
Canada is personal use with its non-US note; that the Supreme Court cases are official United States Reports
addresses with the later history of overruled cases said; and that every row of NOT_INCLUDED says where to find the
source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_travel_civics.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import civics as C  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import transport_rights  # noqa: E402
import travel as T  # noqa: E402


def test_registered():
    for mod, word, prefix, group, name in ((T, "travel", "trip", "travel", "Reference, travel"),
                                           (C, "civics", "civ", "civics", "Reference, citizenship and civics")):
        assert mod.__name__ in more_refs.MODULES and mod in more_refs.modules()
        assert sources.GROUPS[group] == name
        keys = sources.expand_keys([word])
        assert keys == mod.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
        assert all(k.startswith(prefix + ":") for k in keys)
        assert set(mod.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        for row in mod.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    assert transport_rights.COLLECTION.prefix == "travel" and T.COLLECTION.prefix == "trip"
    assert more_refs.module_for("travel") is T and more_refs.module_for("travel:access_board_ada_guide") is \
        transport_rights


def test_every_book():
    for mod in (T, C):
        for g in list(mod.COLLECTION.guides.values()) + list(mod.COLLECTION.pdfs.values()):
            short = B.licence_short(g["licence"])
            assert B.licence_kind(short) or g.get("personal_use"), g["name"]
            assert g["notice"] and g["description"] and g["licence_page"] and g["licence_text"], g["name"]
            assert g["group"] in sources.GROUPS, g["name"]
            if mod is C:
                assert g["notice"].endswith(C.NOT_ADVICE), g["name"]
            if g["name"] in mod.COLLECTION.guides:
                pattern = re.compile(g["pages"])
                for url in g.get("urls", []):
                    assert pattern.match(url), (g["name"], url)


def test_page_patterns():
    usa = re.compile(T.COLLECTION.guides["usa_gov_travel"]["pages"])
    assert usa.match("https://www.usa.gov/passport-renewal") and not usa.match("https://www.usa.gov/benefits")
    faa = re.compile(T.COLLECTION.guides["faa_packsafe"]["pages"])
    assert faa.match("https://www.faa.gov/hazmat/packsafe/airline-passengers-and-batteries")
    assert not faa.match("https://www.faa.gov/hazmat/safecargo")
    gov = re.compile(C.COLLECTION.guides["usa_gov_government_voting"]["pages"])
    assert gov.match("https://www.usa.gov/how-to-vote") and not gov.match("https://www.usa.gov/travel")
    ben = re.compile(C.COLLECTION.guides["bens_guide"]["pages"])
    assert ben.match("https://bensguide.gpo.gov/a-how-made") and not ben.match("https://bensguide.gpo.gov/games")
    assert "uscourts_jury_service" not in C.COLLECTION.guides          # already dir:uscourts_self_help


def test_uscis_pdfs_from_wayback_copies():
    for name in ("uscis_civics_test_2025", "uscis_civics_test_100", "uscis_guide_to_naturalization",
                 "uscis_welcome_new_immigrants"):
        p = C.COLLECTION.pdfs[name]
        m = re.match(r"^https://web\.archive\.org/web/(\d{14})id_/(https://www\.uscis\.gov/.+\.pdf)$", p["pdf"])
        assert m and p["version"][-10:].replace("-", "") == m.group(1)[:8], name
        assert m.group(2) in p["version"] and p["page"].endswith(m.group(2)), name
        assert p["licence"] == sources.US_GOV and "Internet Archive" in p["notice"], name
    assert C.COLLECTION.pdfs["uscis_civics_flash_cards"]["archive"]


def test_discover_canada_personal_use():
    dc = C.COLLECTION.pdfs["discover_canada"]
    assert dc["personal_use"] and dc["country"] == "Canada" and "not US" in dc["notice"]
    assert B.licence_kind(B.licence_short(dc["licence"])) == "non-commercial"


def test_supreme_court_cases():
    parts = C.case_parts()
    assert len(parts) == len(C.CASES) == len({p[1] for p in parts})
    for (title, pdf, page), (name, vol, first, year) in zip(parts, C.CASES):
        assert pdf == f"https://www.govinfo.gov/content/pkg/USREPORTS-{vol}/pdf/USREPORTS-{vol}-{first}.pdf"
        assert title.startswith(name) and f"{vol} U.S. {first}, {year}" in title
    for words in ("Roe v. Wade was overruled by Dobbs", "Plessy v. Ferguson", "Thirteenth and Fourteenth"):
        assert words in C.CASES_ENTRY["description"], words
    assert C.cases_sign("supreme_court_cases") == C.cases_sign("supreme_court_cases")
