"""Self-test of the four health and life reference modules (mental_health.py, fitness_nutrition.py, sexual_health.py,
aging_end_of_life.py), with MADE-UP data only: nothing is downloaded.

It checks that each module is registered once under its request word and its own group, that every request stays at
256 jobs or fewer, that every web guide and PDF has a licence the toolkit may repackage, a notice, a description, a
licence page and line and a page pattern that matches its own addresses; that every notice ends with its health note
(general information, not medical advice or a diagnosis, 911 and 988); that CDC's books are kept whole with CDC's
conditions and leave out the Spanish and professional pages; that no book repeats a book another module already
builds (NIMH's brochures, NIDA for parents, NICHD, Medicare, CDC caregiving); that the help lines pages state only the
numbers whose words were found on the official page (made-up pages); and that every NOT_INCLUDED row says where to
find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_health_life.py
"""

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import mental_health as M  # noqa: E402
import fitness_nutrition as F  # noqa: E402
import sexual_health as S  # noqa: E402
import aging_end_of_life as A  # noqa: E402

WORDS = {M: ("mental-health", "mind", "mentalhealth", "Reference, mental health and wellbeing"),
         F: ("fitness-nutrition", "fit", "fitnessnutrition", "Reference, fitness and nutrition"),
         S: ("sexual-health", "sexhealth", "sexualhealth", "Reference, sexual and reproductive health"),
         A: ("aging-end-of-life", "aging", "agingeol", "Reference, aging and end of life")}
NOTES = {M: M.HEALTH_NOTE, F: F.NOTE, S: S.NOTE, A: A.NOTE}


def books(m):
    """Every web guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered():
    total = 0
    for m, (word, prefix, group, title) in WORDS.items():
        assert m in more_refs.modules() and more_refs.MODULES.count(m.__name__) == 1
        keys = sources.expand_keys([word])
        assert keys == m.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
        c = m.COLLECTION
        assert set(keys) == {f"{prefix}:{n}" for n in list(c.guides) + list(c.pdfs) + list(c.makers)}
        assert c.prefix == prefix and c.group == group and sources.GROUPS[group] == title
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
        total += len(keys)
    assert total <= 256


def test_notes_say_what_the_owner_asked():
    assert M.HEALTH_NOTE == ("General information, not medical advice or a diagnosis. In an emergency call 911; in a "
                             "mental health crisis call or text 988.")
    for m, note in NOTES.items():
        assert note.startswith("General information, not medical") and "call 911" in note, m.__name__
        assert note.endswith("in a mental health crisis call or text 988."), m.__name__


@pytest.mark.parametrize("m", list(WORDS), ids=lambda m: m.__name__)
def test_every_book(m):
    for g in books(m):
        whole = bool(g.get("unchanged"))
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, whole) == "open", g["name"]
        assert g["notice"] and g["description"] and g["group"] == m.COLLECTION.group, g["name"]
        assert g["licence_page"] and g["licence_text"], g["name"]
        assert NOTES[m] in g["notice"], g["name"]
        assert g.get("country", "United States") == "United States", g["name"]
        if g["name"] in m.COLLECTION.guides:
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
            for start, _depth in g.get("crawl") or []:
                assert start.startswith("https://"), g["name"]
        else:
            assert g["pdf"].startswith("https://") and g["version"], g["name"]


def test_cdc_books_whole_with_conditions():
    cdc = [g for m in WORDS for g in books(m) if g["publisher"] == M.CDC_PUBLISHER]
    assert len(cdc) == 7
    for g in cdc:
        assert g["unchanged"] and g["licence_page"] == M.CDC_TERMS, g["name"]
        for words in ("Source: CDC", "free of charge", "does not constitute its endorsement"):
            assert words in g["notice"], (g["name"], words)
        pattern = re.compile(g["pages"])
        site = g["crawl"][0][0].rsplit("/", 1)[0]
        assert pattern.match(site + "/index.html") and pattern.match(site + "/about/what-to-do.html")
        for bad in ("/es/index.html", "/site.html", "/hcp/clinical/index.html", "/php/data/index.html"):
            assert not pattern.match(site + bad), (g["name"], bad)


def test_page_patterns():
    nimh = re.compile(M.COLLECTION.guides["nimh_health_topics"]["pages"])
    assert nimh.match("https://www.nimh.nih.gov/health/topics/depression")
    assert not nimh.match("https://www.nimh.nih.gov/health/topics/espanol/prevencion-del-suicidio")
    nida = re.compile(M.COLLECTION.guides["nida_drug_topics"]["pages"])
    assert nida.match("https://nida.nih.gov/research-topics/fentanyl")
    assert not nida.match("https://nida.nih.gov/research-topics/parents-educators")     # parent:nida_parents_teens
    ptsd = re.compile(M.COLLECTION.guides["va_ptsd"]["pages"])
    assert ptsd.match("https://www.ptsd.va.gov/PTSD/understand_tx/talk_therapy.asp")
    assert not ptsd.match("https://www.ptsd.va.gov/PTSD/professional/assessment/overview/index.asp")
    grief = re.compile(M.COLLECTION.guides["nci_grief_caregivers"]["pages"])
    end = re.compile(A.COLLECTION.guides["nci_end_of_life"]["pages"])
    caregivers = "https://www.cancer.gov/about-cancer/advanced-cancer/caregivers/planning/bereavement-pdq"
    assert grief.match(caregivers) and not end.match(caregivers)       # each page in one book only
    assert end.match("https://www.cancer.gov/about-cancer/advanced-cancer/care-choices")
    assert end.match("https://www.cancer.gov/about-cancer/managing-care/advance-directives")
    smoke = re.compile(M.COLLECTION.guides["smokefree_gov"]["pages"])
    assert smoke.match("https://smokefree.gov/challenges-when-quitting/cravings-triggers/how-manage-cravings")
    assert not smoke.match("https://smokefree.gov/privacy-policy")
    ltc = re.compile(A.COLLECTION.guides["acl_long_term_care"]["pages"])
    assert ltc.match("https://acl.gov/ltc/legal-steps/will-i-need-lawyer") and not ltc.match("https://acl.gov/programs")
    owh = re.compile(S.COLLECTION.guides["owh_periods_menopause_relationships"]["pages"])
    assert owh.match("https://www.womenshealth.gov/menopause/menopause-treatment")
    assert not owh.match("https://www.womenshealth.gov/pregnancy")      # early:owh_pregnancy_breastfeeding


def test_no_repeats_of_other_modules():
    """No book here reads the same pages as a book another module builds."""
    mine = {m.__name__ for m in WORDS}
    others = [g for m in more_refs.modules() if m.__name__ not in mine
              for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())]
    their_sources = ({g.get("source") for g in others} | {g.get("pdf") for g in others}) - {None, ""}
    their_patterns = [re.compile(g["pages"]) for g in others if g.get("pages")]
    for m in WORDS:
        for g in books(m):
            assert not {g.get("source"), g.get("pdf")} & their_sources, g["name"]
            for url in g.get("urls", []):
                assert not any(p.match(url) for p in their_patterns), (g["name"], url)
    # the pages others build: NIMH's brochures, NIDA for parents, ACL programmes, Medicare, CDC caregiving and falls
    for url in ("https://www.nimh.nih.gov/health/publications/depression",
                "https://nida.nih.gov/research-topics/parents-educators/conversation-starters",
                "https://acl.gov/programs/support-caregivers", "https://www.medicare.gov/coverage/hospice-care",
                "https://www.cdc.gov/falls/about/index.html", "https://www.nichd.nih.gov/health/topics/infertility"):
        for m in WORDS:
            for g in m.COLLECTION.guides.values():
                assert not re.match(g["pages"], url), (g["name"], url)


def test_help_lines_say_only_what_is_checked(tmp_path):
    """A line whose words are on its made-up page is stated; one whose page lost them points to the page instead."""
    pages = {M.CDC_HELP: "<p>Call 988 and press 1 Crisis Chat or text 838255</p><p>Call 1-800-662-HELP (4357)</p>",
             "https://www.crisistextline.org/": "<p>Need to vent? Text HOME to 741741 to connect</p>"}
    book = M.help_lines_book("mind", M.GROUP, "help_lines", "Help lines", "Help", M.HELP_CHECKS, "In danger, call 911.",
                             "d", M.HEALTH_NOTE, fetch=lambda url: pages.get(url, ""))
    body = book.pages[0].body
    assert "741741" in body and "838255" in body and "1-800-662-HELP" in body
    assert "985-5990" not in body and "MY-RESET" not in body                           # their pages did not say so
    assert "could not be checked" in body and "ncpgambling.org" in body
    assert book.licence == "CC0" and book.version.startswith("checked ") and "3 of 6" in book.version
    assert {o["url"] for o in book.originals} == {M.CDC_HELP, M.CDC + "/tobacco/about/how-to-quit.html"}
    assert book.source == M.CDC_HELP                    # never a private site's page offered as a file
    for m in (S, A):
        book = M.help_lines_book(m.COLLECTION.prefix, m.GROUP, "help_lines", "T", "s", m.HELP_CHECKS, "i", "d",
                                 m.NOTE, fetch=lambda url: "")
        assert "could not be checked" in book.pages[0].body and m.NOTE in book.notice
    sample = M.text_of('800-799-SAFE (7233) Text "START" to 88788 ... 800-656-HOPE (4673) ... 1-888-373-7888')
    assert all(re.search(must, sample) for _h, _u, must, _w in S.HELP_CHECKS)
    fraud = M.text_of("National Elder Fraud Hotline 1-833-FRAUD-11 ( 833-372-8311 ) 10 a.m.")
    assert re.search(A.HELP_CHECKS[1][2], fraud)


def test_not_included():
    for m in WORDS:
        assert m.NOT_INCLUDED, m.__name__
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for m in WORDS for r in m.NOT_INCLUDED)
    for words in ("SAMHSA", "Rethinking Drinking", "Surgeon General", "MyPlate", "NCHPAD", "Blind Athletes",
                  "HIV.gov", "Planned Parenthood", "National Institute on Aging", "organdonor.gov",
                  "advance directive"):
        assert words in names, words
