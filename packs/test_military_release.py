"""A self-test of the shared release rule for US military publications (military_release.py), with made-up front
pages only: nothing is downloaded.

It checks that:
  - the four copies of military_release.py (packs, textbooks, manuals, training-kit/kit) are the same, word for word;
  - a missing Distribution Statement A, on a copy from the Internet Archive, a government site or a museum, comes in
    with a truthful line that never claims "approved for public release";
  - a printed Distribution Statement A is said as before;
  - a restricted marking comes in only when a government site publishes that copy openly (read from it, or a
    separate government address checked to answer without a login); from the Internet Archive or a museum it is
    personal use only; from a third-party site it is left out;
  - an old classification marking comes in only when declassified and released (a marking, a record naming the
    releasing agency, or a government site publishing it); live markings, leak sites and third-party copies are
    left out; "UNCLASSIFIED" is not taken for one;
  - a third-party copy keeps the old rule (Distribution Statement A needed);
  - the shifted cover font of some Army PDFs is read;
  - a login page is not taken for an open answer.

Run it from the repository's folder:   python3 -m pytest packs/test_military_release.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import military_release as M  # noqa: E402

ROOT = os.path.dirname(HERE)
IA = "https://archive.org/details/made-up-field-manual"
APD = "https://armypubs.army.mil/epubs/DR_pubs/made-up.pdf"
OTHER = "https://example.com/made-up.pdf"


def test_four_copies_are_the_same():
    """Each part of the repository keeps the same file."""
    copies = [os.path.join(ROOT, p, "military_release.py") for p in ("packs", "textbooks", "manuals",
                                                                     os.path.join("training-kit", "kit"))]
    texts = []
    for path in copies:
        with open(path, encoding="utf-8") as f:
            texts.append(f.read())
    assert all(t == texts[0] for t in texts), "copy packs/military_release.py to the other three places"


def test_missing_statement_comes_in_with_a_truthful_line():
    """No statement: in from the open hosts, never called approved for public release."""
    for source, words in ((IA, "the Internet Archive"), ("https://apps.dtic.mil/sti/pdfs/x.pdf", "DTIC"),
                          ("www.loc.gov", "Library of Congress"), ("https://www.si.edu/x", "Smithsonian")):
        rule = M.release_rule("FM 00-0 Made-up Field Manual. Headquarters, Department of the Army", source)
        assert rule.verdict == "public" and not rule.statement, source
        assert words in rule.release and "print no distribution statement" in rule.release
        assert "17 U.S.C. 105" in rule.release and "approved for public release" not in rule.release.lower()
    navy = M.release_rule("Made-up course", IA, work="a work of the US Navy")
    assert navy.release.startswith("A work of the US Navy")


def test_statement_a_is_said():
    """The printed statement is named as before, from any host."""
    for source in (IA, OTHER):
        rule = M.release_rule("DISTRIBUTION RESTRICTION: Approved for public release; distribution is unlimited.",
                              source)
        assert rule.verdict == "public" and rule.statement
        assert rule.release.startswith("Distribution Statement A: approved for public release")


def test_restricted_marking():
    """Open only when the government publishes that copy; else personal use (open hosts) or out."""
    front = "DISTRIBUTION STATEMENT C: Distribution authorized to U.S. Government agencies and their contractors."
    gov = M.release_rule(front, APD)
    assert gov.verdict == "public" and "DISTRIBUTION STATEMENT C" in gov.release
    assert f"publishes it openly at {APD}" in gov.release and "Army Publishing Directorate" in gov.release
    assert M.release_rule(front, APD, gov_answers=False).verdict == "personal"  # it no longer answers openly
    personal = M.release_rule(front, IA)
    assert personal.verdict == "personal" and personal.release.startswith("PERSONAL USE ONLY")
    assert personal.reason.startswith("prints a restricted marking (") and "personal use only, fetch it yourself" in \
        personal.reason
    checked = M.release_rule(front, IA, gov_address="https://www.loc.gov/item/made-up/", gov_answers=True)
    assert checked.verdict == "public" and "publishes it openly at https://www.loc.gov/item/made-up/" in \
        checked.release
    assert M.release_rule(front, IA, gov_address="https://www.loc.gov/item/made-up/").verdict == "personal"
    assert M.release_rule(front, IA, gov_address=OTHER, gov_answers=True).verdict == "personal"
    assert M.release_rule(front, OTHER).verdict == "out"
    for words in ("FOR OFFICIAL USE ONLY", "CUI", "NOFORN", "WARNING: This document contains technical data whose "
                  "export is restricted by the Arms Export Control Act", "Distribution is limited to U.S. "
                  "Government agencies only", "DISTRIBUTION D. Authorized to DoD"):
        assert M.release_rule(words, IA).verdict == "personal", words
    museum = M.release_rule("FOUO", "https://www.nationalww2museum.org/x.pdf")
    assert museum.verdict == "personal" and "museum" in museum.release


def test_classified_needs_declassification_or_a_government_release():
    """An old classification marking: in when declassified (a marking in its text, or its record naming the
    releasing agency) on an open host, or when a government reading room publishes it; out with live markings and
    no release evidence, and always from a leak site or a third-party host; UNCLASSIFIED is not a marking."""
    declassified = "SECRET. DECLASSIFIED Authority NND 000001 (made up). Made-up report."
    rule = M.release_rule(declassified, IA)
    assert rule.verdict == "public" and "Originally classified SECRET; declassified and released" in rule.release
    assert "DECLASSIFIED" in rule.release and "approved for public release" not in rule.release.lower()
    sanitized = M.release_rule("TOP SECRET Sanitized Copy Approved for Release 2010/01/01 (made up)", IA)
    assert sanitized.verdict == "public" and "TOP SECRET" in sanitized.release
    room = "https://www.cia.gov/readingroom/docs/made-up.pdf"
    rule = M.release_rule("CONFIDENTIAL. Made-up memorandum.", room)
    assert rule.verdict == "public" and "Originally classified CONFIDENTIAL" in rule.release and room in rule.release
    assert "Reading Room" in rule.release
    record = M.release_rule("SECRET. Made-up report.", IA, released_by="the National Archives (NARA)")
    assert record.verdict == "public" and "the National Archives (NARA)" in record.release
    checked = M.release_rule("SECRET. Made-up report.", IA, gov_address="https://www.archives.gov/x.pdf",
                             gov_answers=True)
    assert checked.verdict == "public" and "https://www.archives.gov/x.pdf" in checked.release
    for words in ("SECRET", "TOP SECRET//NOFORN", "CONFIDENTIAL", "Classified by: made-up"):
        for source in (IA, OTHER):
            rule = M.release_rule(words + " Approved for public release; distribution is unlimited", source)
            assert rule.verdict == "out" and "classified" in rule.reason, (words, source)
    for leak in ("https://wikileaks.org/made-up.pdf", "https://cryptome.org/made-up.pdf"):
        assert M.release_rule(declassified, leak).verdict == "out"
        assert M.release_rule(declassified, leak, released_by="NARA").verdict == "out"
    assert M.release_rule(declassified, OTHER).verdict == "out"
    assert M.release_rule("UNCLASSIFIED. The Secretary of the Army; keep it confidential.", IA).verdict == "public"
    assert M.level_of("CONFIDENTIAL SECRET TOP SECRET") == "TOP SECRET"


def test_third_party_host_keeps_the_old_rule():
    """A copy from any other site needs Distribution Statement A."""
    rule = M.release_rule("Made-up manual", OTHER)
    assert rule.verdict == "out" and "no Distribution Statement A" in rule.reason
    assert M.open_host(OTHER) == "" and not M.is_government(IA) and M.is_government(APD)


def test_shifted_font():
    """Some Army covers print every letter 29 places early; both forms are read."""
    shift = "".join(chr(ord(c) - 29) if c not in " " else c for c in "DISTRIBUTION STATEMENT C: AUTHORIZED")
    assert M.release_rule(shift, IA).verdict == "personal"


def test_answers_without_login():
    """200 from the address itself is open; a redirect to a login, a password form or an error is not."""
    assert M.answers_without_login(200, APD, "application/pdf")
    assert not M.answers_without_login(200, "https://login.made-up.mil/cac?next=x")
    assert not M.answers_without_login(200, APD, "text/html", '<form><input type="password" name="p"></form>')
    assert not M.answers_without_login(403, APD) and not M.answers_without_login(0)
