"""Self-test of the five "people" collections of the reference library (the owner's request of 2026-11-22):
disability_life.py (dis:), veterans.py (veteran:), education_help.py (edu:), relationships.py (relate:) and
immigration.py (immig:), with MADE-UP data only: nothing is downloaded.

It checks that:
  - each module is registered once under its request word (disability, veterans, education, relationships,
    immigration), each word stays at 256 jobs or fewer, and the words reach sources.expand_keys;
  - the groups exist ("Reference, disability and accessibility", "Reference, veterans", "Reference, education",
    "Reference, communication and relationships", "Reference, immigration") and the licence lines and left-out
    rows reach sources.py;
  - every book has a licence the toolkit may repackage, a description, a notice, a licence page and line, and a
    page pattern that matches its own fixed addresses; CDC books are kept whole with CDC's conditions;
  - every legal or benefits book ends its notice with the owner's line ("General information, not legal advice;
    ..."), every veterans book names the Veterans Crisis Line (988 then press 1), and every relationships book
    names the hotlines;
  - the Canadian book is personal use only, from Canada, with its non-US words;
  - no book reads the same start address as a book already in the library (extend, never duplicate);
  - a fixed-list guide is read in the order listed (made-up robots answers, no download);
  - every left-out row says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_people.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import disability_life as DIS  # noqa: E402
import education_help as EDU  # noqa: E402
import immigration as IMM  # noqa: E402
import relationships as REL  # noqa: E402
import veterans as VET  # noqa: E402

LEGAL = "General information, not legal advice; check the current rules or ask an accredited representative or lawyer."
MODULES = {"disability": DIS, "veterans": VET, "education": EDU, "relationships": REL, "immigration": IMM}
GROUP_NAMES = {"disability": "Reference, disability and accessibility", "veterans": "Reference, veterans",
               "education": "Reference, education", "relationships": "Reference, communication and relationships",
               "immigration": "Reference, immigration"}


def books(module):
    """Every guide and PDF entry of a module."""
    c = module.COLLECTION
    return list(c.guides.values()) + list(c.pdfs.values())


def test_registered_and_job_counts():
    for word, m in MODULES.items():
        assert m in more_refs.modules(), word
        assert more_refs.module_for(word) is m, word
        keys = sources.expand_keys([word])
        assert keys == m.COLLECTION.expand_keys([word]), word
        assert len(keys) == len(set(keys)) <= 256, word
        assert set(keys) == {f"{m.COLLECTION.prefix}:{b['name']}" for b in books(m)}, word
        assert getattr(m, "LEGAL", LEGAL) == LEGAL, word
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES), word
    prefixes = [m.COLLECTION.prefix for m in MODULES.values()]
    assert len(prefixes) == len(set(prefixes))


def test_groups():
    for word, m in MODULES.items():
        groups = {b["group"] for b in books(m)}
        assert groups == {m.GROUP}, word
        assert sources.GROUPS[m.GROUP] == GROUP_NAMES[word], word


def test_every_book():
    for word, m in MODULES.items():
        for g in books(m):
            whole = bool(g.get("unchanged"))
            short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
            assert B.licence_kind(short, whole), g["name"]
            for field in ("notice", "description", "licence_page", "licence_text", "title", "subject", "publisher"):
                assert g.get(field), (g["name"], field)
            if g["name"] in m.COLLECTION.guides:
                pattern = re.compile(g["pages"])
                for url in g.get("urls", []):
                    url = url[0] if isinstance(url, tuple) else url
                    assert pattern.match(url), (g["name"], url)
                if not g["source"].endswith("/site.html") and "table-of-contents" not in g["source"]:
                    assert pattern.match(g["source"]) or g.get("crawl"), g["name"]
            else:
                assert g.get("archive") or g.get("pdf"), g["name"]
                assert g.get("version"), g["name"]
                if g.get("archive"):
                    assert g.get("published"), g["name"]
            if g.get("licence_page") == DIS.CDC_TERMS:
                assert whole and "Source: CDC" in g["notice"] and "does not constitute its endorsement" in \
                    g["notice"], g["name"]


def test_owner_lines():
    for m in (VET, IMM, EDU):
        for g in books(m):
            assert g["notice"].rstrip().endswith(LEGAL) or LEGAL in g["notice"], g["name"]
    assert LEGAL in DIS.COLLECTION.pdfs["ocr_students_postsecondary"]["notice"]
    for g in books(VET):
        assert VET.CRISIS in g["notice"], g["name"]
    assert "988 then press 1" in VET.CRISIS and "838255" in VET.CRISIS
    for g in books(REL):
        assert REL.HOTLINES in g["notice"], g["name"]
    assert "1-800-799-7233" in REL.HOTLINES and "911" in REL.HOTLINES
    for g in books(DIS):
        assert DIS.NOT_MEDICAL in g["notice"] or LEGAL in g["notice"], g["name"]


def test_canada_is_personal_use_with_the_non_us_note():
    ca = IMM.COLLECTION.guides["canada_newcomers"]
    assert ca["personal_use"] and ca["country"] == "Canada" and ca["licence"] == IMM.CROWN_NC
    assert sources.ALLOWED.get(IMM.CROWN_NC) == "non-commercial"
    assert "Canadian source, personal use only" in ca["notice"] and "not the United States'" in ca["notice"]
    for g in books(IMM):
        if g["name"] != "canada_newcomers":
            assert g.get("country") == "United States" and not g.get("personal_use"), g["name"]


def test_welcome_guide_editions():
    names = [p["name"] for p in IMM.PDFS]
    assert len(names) == len(set(names)) == len(IMM.M618_EDITIONS)
    for p in IMM.PDFS:
        assert re.match(r"^https://www\.uscis\.gov/sites/default/files/document/guides/M-618(_[A-Za-z]+)?\.pdf$",
                        p["pdf"]), p["name"]
        assert len(p["language"]) == 3, p["name"]
    assert not any(code in ("_hc", "_t") for code, _l, _i in IMM.M618_EDITIONS)


def test_policy_manual_parts():
    pm = IMM.COLLECTION.guides["uscis_policy_manual"]
    pattern = re.compile(pm["pages"])
    assert pattern.match("https://www.uscis.gov/policy-manual/volume-7-part-a-chapter-1")
    assert pattern.match("https://www.uscis.gov/policy-manual/volume-12-part-d")
    assert not pattern.match("https://www.uscis.gov/policy-manual/volume-7")          # the volume menus come first
    assert not pattern.match("https://www.uscis.gov/es/policy-manual/volume-7-part-a")
    unit = D.unit_of("https://www.uscis.gov/policy-manual/volume-12-part-a-chapter-1", pm["unit_rules"])
    assert unit == "Volume 12: Citizenship and Naturalization"
    assert D.unit_of("https://www.uscis.gov/policy-manual/volume-1-part-b", pm["unit_rules"]).startswith("Volume 1:")


def test_guide_patterns_keep_out_what_they_should():
    uscis = re.compile(IMM.COLLECTION.guides["uscis_immigration_guides"]["pages"])
    assert uscis.match("https://www.uscis.gov/humanitarian/temporary-protected-status")
    assert not uscis.match("https://www.uscis.gov/citizenship/learn-about-citizenship")   # citizenship: elsewhere
    mh = re.compile(VET.COLLECTION.guides["va_mental_health"]["pages"])
    assert mh.match("https://www.mentalhealth.va.gov/MENTALHEALTH/ptsd/index.asp")
    assert not mh.match("https://www.mentalhealth.va.gov/mentalhealth/healthcare-providers/index.asp")
    fsa = re.compile(EDU.COLLECTION.guides["fsa_handbook"]["pages"])
    assert fsa.match(f"{EDU.FSA}/vol7/ch2-calculating-pell-grants")
    assert not fsa.match("https://fsapartners.ed.gov/knowledge-center/fsa-handbook/pdf/2019-2020")
    cdc = re.compile(DIS.COLLECTION.guides["cdc_autism"]["pages"])
    assert cdc.match("https://www.cdc.gov/autism/signs-symptoms/index.html")
    assert not cdc.match("https://www.cdc.gov/autism/hcp/diagnosis/index.html")
    assert not cdc.match("https://www.cdc.gov/autism/site.html")


def library_starts():
    """The start addresses of every web guide already in the library outside these five modules."""
    starts = set()
    for m in more_refs.modules():
        if m in MODULES.values():
            continue
        for g in m.COLLECTION.guides.values():
            starts.add(g.get("source", "").rstrip("/"))
            starts |= {s.rstrip("/") for s, _d in g.get("crawl") or []}
    for g in list(D.GUIDES) + list(sources.GOV_GUIDES):
        starts.add(g.get("source", "").rstrip("/"))
        starts |= {s.rstrip("/") for s, _d in g.get("crawl") or []}
    return starts - {""}


def test_nothing_already_in_the_library_is_read_again():
    taken = library_starts()
    for m in MODULES.values():
        for g in m.COLLECTION.guides.values():
            mine = {s.rstrip("/") for s, _d in g.get("crawl") or []} | {g["source"].rstrip("/")}
            assert not mine & taken, (g["name"], mine & taken)
    # the CDC sites read here are read by no other CDC book
    other_sites = set()
    for m in more_refs.modules():
        if m in MODULES.values():
            continue
        for g in m.COLLECTION.guides.values():
            other_sites |= set(re.findall(r"https://www\.cdc\.gov/([a-z0-9-]+)/site\.html",
                                          " ".join(s for s, _d in g.get("crawl") or [])))
    for m in (DIS, REL):
        for g in m.COLLECTION.guides.values():
            for site in re.findall(r"https://www\.cdc\.gov/([a-z0-9-]+)/site\.html",
                                   " ".join(s for s, _d in g.get("crawl") or [])):
                assert site not in other_sites, (g["name"], site)


def test_pages_read_in_order(monkeypatch):
    """A fixed-list guide is read in the order listed, its first page first, and nothing else is fetched."""
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    for guide, pages in ((VET.COLLECTION.guides["veterans_crisis_line"], VET.VCL_PAGES),
                         (IMM.COLLECTION.guides["eoir_court_legal_help"], IMM.EOIR_PAGES),
                         (DIS.COLLECTION.guides["fda_hearing_aids"], DIS.FDA_PAGES)):
        found = [u for u, _unit in D.crawl(guide, None)]
        assert found == pages, guide["name"]
    units = [unit for _u, unit in D.crawl(VET.COLLECTION.guides["veterans_crisis_line"], None)]
    assert units[1] == "Get help now" and units[0] == "About the Crisis Line"


def test_not_included():
    for word, m in MODULES.items():
        assert m.NOT_INCLUDED, word
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    said = " ".join(r[0] + r[1] for m in MODULES.values() for r in m.NOT_INCLUDED)
    for words in ("FCC", "GED", "StudentAid.gov", "LINCS", "DoD Transition Assistance", "veteran service",
                  "Surgeon General", "State Department", "Office of Refugee Resettlement", "notario"):
        assert words.lower() in said.lower(), words
