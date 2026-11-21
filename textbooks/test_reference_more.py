"""Self-test of the reference books added on 2026-11-21 (reference_more.py, through sources.py) and of the robots.txt
reading they rely on, with MADE-UP data only: nothing is downloaded.

It checks that:
  - robots.txt rules with "*" and "$" are obeyed (GOV.UK's "Disallow: /*/print$"), a longer Allow rule still wins,
    and "Crawl-delay: 10 seconds" is read;
  - the FAA handbooks, Navy rate manuals, Army manuals and NIST handbooks are PDF_DOCS entries with an official
    address, a US government licence line to check, and (for military manuals) the Distribution Statement A check;
  - no weapon or combat manual is chosen;
  - the new CFR parts are laws with the right title, volume and parts;
  - the UK National Archives' teaching resources are a guide under the Open Government Licence, the GOV.UK guides no
    longer read the "/print" pages robots.txt refuses, and non-US books get a specific practice notice;
  - the canada.ca notes say precisely that the web pages are non-commercial and the open.canada.ca publications
    are not.

Run it from the repository's folder:   python3 -m pytest textbooks/test_reference_more.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import reference_more as R  # noqa: E402
import sources  # noqa: E402

GOVUK_ROBOTS = """User-agent: *
Disallow: /*/print$
Disallow: /search/all*
Allow: /core/*.css$
Disallow: /core/*

User-agent: deepcrawl
Disallow: /
"""


def test_robots_wildcards(monkeypatch):
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(B, "_robot_patterns", {})
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: GOVUK_ROBOTS)
    assert not B.allowed_by_robots("https://www.gov.uk/browse/benefits/print")
    assert B.allowed_by_robots("https://www.gov.uk/browse/benefits")
    assert not B.allowed_by_robots("https://www.gov.uk/search/all?keywords=x")
    assert B.allowed_by_robots("https://www.gov.uk/core/site.css")          # the longer Allow rule wins
    assert not B.allowed_by_robots("https://www.gov.uk/core/site.js")


def test_crawl_delay_in_words(monkeypatch):
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(B, "_robot_patterns", {})
    monkeypatch.setattr(B, "CRAWL_DELAY", {})
    text = "User-agent: *\nContent-Signal: ai-train=no, search=yes, ai-input=yes\nCrawl-delay: 10 seconds\n" \
           "Disallow: /search/\n"
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: text)
    assert B.allowed_by_robots("https://www.nationalarchives.gov.uk/education/teaching-resources/x/")
    assert B.CRAWL_DELAY["www.nationalarchives.gov.uk"] == 10.0


def test_pdf_entries():
    names = [e["name"] for e in sources.PDF_DOCS]
    assert len(names) == len(set(names))
    for e in R.PDF_DOCS:
        assert e in sources.PDF_DOCS
        assert e["licence"] == sources.US_GOV and e["country"] == "United States"
        assert e.get("pdf", "").startswith("https://") or e.get("archive"), e["name"]
        assert e.get("licence_page") or e.get("distribution_a"), e["name"]
        assert e["group"] in sources.GROUPS and e["description"] and e["subject"]
        assert not re.search(r"gunner|combat|weapon|rifle|pistol|sniper|ranger", e["title"], re.I), e["title"]
    for e in R.NAVY_RATE_MANUALS + R.ARMY_MANUALS:
        assert e["distribution_a"] is True
    assert all(e["pdf"].startswith("https://www.faa.gov/") for e in R.FAA_HANDBOOKS)
    assert len(R.FAA_HANDBOOKS) >= 15
    keys = sources.expand_keys(["courses", "fieldmanuals", "government"])
    assert "pdf:navy_quartermaster_1_c" in keys and "pdf:army_fm_21_10_field_hygiene_2000" in keys
    assert "pdf:faa_aviation_weather_handbook" in keys and "pdf:nist_handbook_44_2025" in keys


def test_cfr_parts():
    laws = {e["name"]: e for e in sources.LAWS}
    more = {e["name"]: e for e in sources.LAWS_MORE}
    assert laws["cfr_16_453_funeral_rule"]["cfr"] == dict(title=16, volume=1, part=453, subpart="")
    assert [p["part"] for p in laws["cfr_16_700_warranties"]["cfr"]] == [700, 701, 702, 703]
    assert more["cfr_21_201_drug_labeling"]["cfr"]["volume"] == 4
    assert [p["part"] for p in more["cfr_49_390_fmcsa_drivers"]["cfr"]] == [390, 391, 392, 395, 396]
    assert {"cfr_42_410_medicare_part_b", "cfr_42_423_medicare_part_d"} <= set(more)
    assert "law:cfr_16_310_telemarketing" in sources.expand_keys(["laws"])


def test_guides_and_notices():
    tna = next(e for e in sources.GOV_GUIDES if e["name"] == "uk_national_archives_teaching_resources")
    assert tna["licence"] == "OGL-UK-3.0" and tna["group"] == "history"
    assert re.match(tna["pages"], "https://www.nationalarchives.gov.uk/education/teaching-resources/apartheid-in-"
                                  "south-africa/")
    assert not re.match(tna["pages"], "https://www.nationalarchives.gov.uk/education/resources/old-lesson/")
    for e in sources.GOV_GUIDES:
        assert "print" not in str(e.get("fetch_as", "")), e["name"]
    assert sources.practice_note("United Kingdom", "History").startswith("UK source: history")
    assert "benefits and pensions" in sources.practice_note("United Kingdom", "State Pension")
    assert "tenancy" in sources.practice_note("United Kingdom", "Housing and renting")
    assert "transport rules" in sources.practice_note("Canada", "Transport and boating safety")
    assert sources.practice_note("United States", "Aviation") == ""


def test_canada_notes_are_precise():
    import periodicals
    texts = [r for _t, r in sources.NOT_INCLUDED + periodicals.NOT_INCLUDED if "canada.ca" in r]
    assert texts
    for r in texts:
        if "non-commercial" in r:
            assert "open.canada.ca" in r and "web pages" in r, r
