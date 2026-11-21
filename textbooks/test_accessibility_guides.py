"""Self-test of the WCAG and accessibility guides added on 2026-11-21 (accessibility_guides.py, through sources.py),
with MADE-UP pages only: nothing is downloaded.

It checks that:
  - every new guide is registered (NONPROFIT for the W3C documents, GOV_GUIDES for the others), in the "disability"
    group, with a licence the toolkit may repackage (the W3C ones kept whole and unchanged), and asked for by key;
  - the books already in the library (WCAG 2.2, Understanding WCAG 2.2, the WAI tutorials) are not added twice;
  - a one-page W3C Technical Report is read from its own address, and a guide of many pages from its contents page;
  - a non-US accessibility book gets the accessibility practice notice;
  - copyrighted guides (AAArdvark's "WCAG in Plain English", WebAIM, BANA ...) are in NOT_INCLUDED with their index or
    sitemap address.

Run it from the repository's folder:   python3 -m pytest textbooks/test_accessibility_guides.py
"""

import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import accessibility_guides as A  # noqa: E402
import build_textbooks as B  # noqa: E402
import sources  # noqa: E402

W3C_NAMES = ["w3c_wcag21", "w3c_techniques_wcag22", "w3c_aria_apg", "w3c_wcag22_quickref", "w3c_easy_checks",
             "w3c_accessibility_fundamentals", "w3c_wai_policies", "w3c_atag20", "w3c_uaag20", "w3c_epub_a11y_11",
             "w3c_wcag2ict_22"]


def use(monkeypatch, routes):
    """Answer every request from routes [(piece of address, answer)]; anything else (robots.txt included) is 404."""
    def fetch(url, cache=None, binary=False, tries=4):
        for piece, answer in routes:
            if piece in url:
                return answer.encode() if binary else answer
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})


def test_registered_once_in_the_disability_group():
    nonprofit = {e["name"]: e for e in sources.NONPROFIT}
    guides = {e["name"]: e for e in sources.GOV_GUIDES}
    for name in W3C_NAMES:
        e = nonprofit[name]
        assert e["group"] == "disability" and e["unchanged"] and B.licence_kind(e["licence"], True) == "no-changes"
        assert re.match(e["pages"], (e.get("urls") or e["start"])[0]) or e.get("start"), name
    for e in A.GOV_GUIDES:
        assert guides[e["name"]] is e and e["group"] == "disability", e["name"]
        licence = e["licence"] if e["licence"] in sources.NO_CHANGES else B.licence_short(e["licence"])
        assert B.licence_kind(licence, False) == "open", e["name"]
    names = [e["name"] for e in sources.NONPROFIT + sources.GOV_GUIDES]
    assert len(names) == len(set(names))                                    # nothing added twice
    for old in ("w3c_wcag22", "w3c_understanding_wcag22", "w3c_wai_tutorials", "section508_gov", "ada_gov_guidance"):
        assert old in names
    keys = sources.expand_keys(["nonprofit:w3c_aria_apg", "guide:nls_informational_publications"])
    assert keys == ["nonprofit:w3c_aria_apg", "guide:nls_informational_publications"]
    assert set(A.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_one_page_report_and_contents_page(monkeypatch):
    wcag21 = next(e for e in sources.NONPROFIT if e["name"] == "w3c_wcag21")
    use(monkeypatch, [("/TR/WCAG21/", "<html><body><h1>WCAG 2.1</h1></body></html>")])
    assert B.webguide_plan(wcag21) == [("https://www.w3.org/TR/WCAG21/", "")]
    apg = next(e for e in sources.NONPROFIT if e["name"] == "w3c_aria_apg")
    use(monkeypatch, [("/apg/patterns/", '<main><a href="accordion/">Accordion</a><a href="/WAI/ARIA/apg/about/">'
                                         'About</a><a href="tabs/">Tabs</a></main>'),
                      ("/apg/practices/", '<main><a href="landmark-regions/">Landmarks</a></main>')])
    assert [u for u, _ in B.webguide_plan(apg)] == ["https://www.w3.org/WAI/ARIA/apg/patterns/accordion/",
                                                     "https://www.w3.org/WAI/ARIA/apg/patterns/tabs/",
                                                     "https://www.w3.org/WAI/ARIA/apg/practices/landmark-regions/"]
    nls = next(e for e in sources.GOV_GUIDES if e["name"] == "nls_informational_publications")
    base = "https://www.loc.gov/nls/services-and-resources/informational-publications/"
    use(monkeypatch, [("/informational-publications/", f'<a href="{base}about-braille/">Braille</a>'
                                                       f'<a href="https://www.loc.gov/nls/how-to-enroll/">Enroll</a>')])
    assert [u for u, _ in B.webguide_plan(nls)] == [base + "about-braille/"]


def test_practice_notice_and_apache_licence():
    note = sources.practice_note("International", "Web accessibility")
    assert note.startswith("International source: accessibility laws") and "Section 508" in note
    assert sources.practice_note("United States", "Web accessibility") == ""
    assert B.licence_kind(B.licence_short(A.APACHE), False) == "open"


def test_not_included_with_addresses():
    rows = {t: r for t, r in sources.NOT_INCLUDED}
    for name in ("AAArdvark", "WebAIM", "Braille Authority", "BBC GEL", "Deque", "National Federation"):
        title = next(t for t in rows if t.startswith(name))
        assert re.search(r"(Index|Sitemap): https?://", rows[title]), title
    assert "wcag-plain-english" in rows[next(t for t in rows if t.startswith("AAArdvark"))]


def test_robots_rule_ending_in_question_mark(monkeypatch):
    # www.w3.org's robots.txt has "Disallow: /TR/?": only addresses starting "/TR/?" are refused, not all of /TR/
    # (Python's own parser drops the "?" and refused every W3C Technical Report).
    use(monkeypatch, [("/robots.txt", "User-agent: *\nDisallow: /TR/?\nDisallow: /blog/*?\n")])
    assert B.allowed_by_robots("https://www.w3.org/TR/WCAG21/")
    assert not B.allowed_by_robots("https://www.w3.org/TR/?tag=accessibility")
    assert not B.allowed_by_robots("https://www.w3.org/blog/2020/x/?a=1")
    assert B.allowed_by_robots("https://www.w3.org/blog/2020/x/")
