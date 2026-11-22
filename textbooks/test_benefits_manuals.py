"""Self-test of the benefits and tax manuals added on 2026-11-22 (benefits_manuals.py), with MADE-UP pages only:
nothing is downloaded.

It checks that:
  - every book is registered once in the group "benefits", asked for by the keys benefits, group:benefits,
    ben:poms, ben:iom, ben:irm and one key each; the builder and the weekly check send ben: keys to this module
    through refs_common's registry;
  - the POMS books cover every chapter of their parts exactly once and stay small enough for one build job;
  - a POMS section page becomes a page with its effective date and transmittal, without empty links or doubled
    bullets, and links between sections point at the book's own pages;
  - a POMS book's weekly sign changes only when SSA's recent-changes list names one of its chapters;
  - a CMS manual page gives its chapter PDFs (crosswalks left out) and an IRM part gives its sections by chapter;
  - a site that shuts out AI readers is not read, and what was not built (KnowVA's M21-1, Medicaid.gov) is said.

Run it from the repository's folder:   python3 -m pytest textbooks/test_benefits_manuals.py
"""

import os
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benefits_manuals as BM  # noqa: E402
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import refs_common as R  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402


def use(monkeypatch, routes):
    """Answer every request from routes [(piece of address, answer)]; anything else (robots.txt included) is 404."""
    def fetch(url, cache=None, binary=False, tries=4):
        for piece, answer in routes:
            if piece in url:
                return answer.encode() if binary else answer
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(D, "_ai", {})


def test_registered_in_the_benefits_group():
    assert sources.GROUPS["benefits"] == "Reference, benefits and tax manuals"
    keys = BM.all_keys()
    assert len(keys) == len(set(keys)) == len(BM.POMS_BOOKS) + len(BM.IOMS) + len(BM.IRM_PARTS)
    assert sources.expand_keys(["benefits"]) == keys == sources.expand_keys(["group:benefits"])
    assert sources.expand_keys(["ben:irm"]) == [f"ben:irm:{n}" for n, _t in BM.IRM_PARTS]
    assert sources.expand_keys(["ben:poms:di-2"]) == ["ben:poms:di-2"]
    assert len(keys) <= 256                                     # one request line, one job each
    assert R.module_for("ben:iom:100-02") is BM
    assert set(BM.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in BM.NOT_INCLUDED)
    assert any("M21-1" in title for title, _why in BM.NOT_INCLUDED)
    assert any("medicaid.gov" in why.lower() for _t, why in BM.NOT_INCLUDED)


def test_builder_and_weekly_check_send_ben_keys_here(monkeypatch, tmp_path):
    monkeypatch.setattr(BM, "sign", lambda key: f"signed {key}")
    assert updates.fingerprint("ben:irm:4") == "signed ben:irm:4"
    called = []
    monkeypatch.setattr(BM, "build", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["ben:poms:vb"], str(tmp_path))
    assert called == [["ben:poms:vb"]]


def test_poms_books_cover_each_chapter_once():
    by_part = {}
    for b in BM.POMS_BOOKS:
        for part in BM.poms_parts(b):
            by_part.setdefault(part, []).append(b["chapters"])
    for part, ranges in by_part.items():
        ranges.sort()
        for (lo1, hi1), (lo2, hi2) in zip(ranges, ranges[1:]):
            assert hi1 < lo2, part                              # no chapter in two books
        assert ranges[0][0] == 0 and ranges[-1][1] == 999, part  # and none left out


CHAPTERS = ("<div class='chaptitletoc'>DI 101: <A HREF='/apps10/poms.nsf/subchapterlist!openview&restricttocategory="
            "04101'>Disability and Blindness Requirements</A><br></div><div class='chaptitletoc'>DI 245: <A HREF='/apps"
            "10/poms.nsf/subchapterlist!openview&restricttocategory=04245'>Medical Evaluation</A><br></div>")
SUBCHAPTERS = ('<div class="subchaptitle">&nbsp;DI 10105: Freeze<br></div><div class="sectionTitle">DI 10105.001: '
               "<A class=\"sectionTitle\" HREF='/apps10/poms.nsf/lnx/0410105001' target=\"_blank\">Period of "
               'Disability</A><br></div><div class="sectionTitle">DI 10105.005: <A class="sectionTitle" '
               "HREF='/apps10/poms.nsf/lnx/0410105005'>Eligibility for the &ldquo;Freeze&rdquo;</A><br></div>")


def section(number, other):
    """A made-up POMS section page linking to another section."""
    return ('<div class="breadcrumbs"><span class="floatl">Effective Dates:&nbsp;03/04/2025 - Present</span></div>'
            '<div class="poms"><p align="right" class="tninfo">TN 9 (03-25)</p><h1 class="sectitle">DI '
            f'{number}</h1><h2><a name="a"></a>A. Purpose</h2><ul><li><div class="poms-ul-mark">•</div><p>See '
            f'<a href="{other}">the other section</a>.</p></li></ul></div></div><!--divBody-->')


def test_poms_book(monkeypatch):
    use(monkeypatch, [("/robots.txt", "User-agent: *\nAllow: /poms.nsf/\nAllow: /apps10/\n"),
                      ("subchapterlist!openview&restricttocategory=04101", SUBCHAPTERS),
                      ("/chapterlist!openview&restricttocategory=04", CHAPTERS),
                      ("/lnx/0410105001", section("10105.001", "0410105005")),
                      ("/lnx/0410105005", section("10105.005", "0499999999"))])
    entry = dict(BM.POMS_BY_PIECE["di-1"])
    left_out = []
    book = BM.poms_book(entry, None, left_out)
    assert [p.path for p in book.pages] == ["0410105001", "0410105005"]
    first, second = book.pages
    assert first.title == "DI 10105.001 Period of Disability" and second.title == "DI 10105.005 Eligibility for " \
                                                                                    "the “Freeze”"
    assert first.unit == "DI 101: Disability and Blindness Requirements"
    assert "effective 2025-03-04, TN 9 (03-25)" in first.body
    assert '<a href="0410105005">the other section</a>' in first.body          # inside the book: its page
    assert "https://secure.ssa.gov/poms.nsf/lnx/0499999999" in second.body     # outside the book: the site
    assert "•" not in first.body and '<a href="https://secure.ssa.gov/poms.nsf/lnx/0410105001"></a>' not in first.body
    assert book.published == "2025-03-04" and book.licence.startswith("Public domain")
    assert len(book.originals) == 2 and not left_out


def test_poms_refused_when_ai_readers_are_shut_out(monkeypatch):
    use(monkeypatch, [("/robots.txt", "User-agent: ClaudeBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n")])
    left_out = []
    assert BM.poms_book(BM.POMS_BY_PIECE["vb"], None, left_out) is None
    assert "AI readers" in left_out[0]["reason"]


def test_poms_sign_follows_its_own_chapters(monkeypatch):
    changes = ("<td>DI 26510 TN 49 11/19/2026 Completion of Form</td><td>GN 02201 TN 88 11/04/2026 Overpayments"
               "</td>")
    use(monkeypatch, [("POMT", changes)])
    di2_before = BM.poms_sign(BM.POMS_BY_PIECE["di-2"])
    gn2_before = BM.poms_sign(BM.POMS_BY_PIECE["gn-2"])
    di1 = BM.poms_sign(BM.POMS_BY_PIECE["di-1"])
    use(monkeypatch, [("POMT", changes + "<td>DI 26510 TN 50 12/01/2026 Completion of Form</td>")])
    assert BM.poms_sign(BM.POMS_BY_PIECE["di-2"]) != di2_before           # DI 265 is in di-2
    assert BM.poms_sign(BM.POMS_BY_PIECE["gn-2"]) == gn2_before
    assert BM.poms_sign(BM.POMS_BY_PIECE["di-1"]) == di1


def test_cms_chapters_and_irm_sections():
    page = ('<nav><a href="/files/document/agent/broker-help-desks.pdf">Help desks</a></nav><main>'
            '<a href="/regulations-and-guidance/guidance/manuals/downloads/bp102c01.pdf">Chapter 1 - Inpatient</a>'
            '<a href="/regulations-and-guidance/guidance/manuals/downloads/bp102c01crosswalk.pdf">Chapter 1 '
            'Crosswalk</a><a href="/files/document/chapter-17-otps.pdf">Chapter 17 - Opioid Treatment</a></main>')
    got = BM.iom_chapters(page, "https://www.cms.gov/x/y")
    assert got == [("Chapter 1 - Inpatient",
                    "https://www.cms.gov/regulations-and-guidance/guidance/manuals/downloads/bp102c01.pdf"),
                   ("Chapter 17 - Opioid Treatment", "https://www.cms.gov/files/document/chapter-17-otps.pdf")]
    part = ("<h1>Part 4. Examining Process</h1><h2>Table of Contents</h2><button>4.1 Planning and Special Programs"
            '</button><a href="https://www.irs.gov/irm/part4/irm_04-001-001">4.1.1 Planning</a><button>4.2 General '
            'Examining Procedures</button><a href="https://www.irs.gov/irm/part4/irm_04-002-005r">4.2.5 Disclosure</a>')
    assert BM.irm_chapter_titles(part, 4) == {"4.1": "4.1 Planning and Special Programs",
                                              "4.2": "4.2 General Examining Procedures"}
    body, date = BM.irm_page('<article about="/irm/part4/irm_04-001-001"><div class="clearfix text-formatted field '
                             'field--name-body x"><p>4.1.1 Planning</p><p>Manual Transmittal</p><p>September 25, '
                             '2020</p></div></article>')
    assert date == "2020-09-25" and "4.1.1 Planning" in body
