"""Self-test of the FDA recall and drug shortage books (fda_recalls.py), with MADE-UP answers only: nothing is
downloaded.

It checks that:
  - the months run from June 2012 to this month, the words recalls and recalls-all expand to at most 256 keys, and
    the daily refresh (pub:daily) adds this month's recalls and the shortages, which are rebuilt under one monthly
    name while past months are kept versions;
  - a month's book holds one page per recall event in the three parts, with the class explained, and stops when the
    API's answer no longer names its public-domain licence;
  - the company announcements keep only titles, dates and links;
  - the shortage book has one page per medicine with its packages.

Run it from the repository's folder:   python3 -m pytest textbooks/test_fda_recalls.py
"""

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fda_recalls as R  # noqa: E402
import sources  # noqa: E402

META = {"license": "https://open.fda.gov/license/", "last_updated": "2026-11-11", "results": {"total": 2}}
ROWS = [{"event_id": "1", "recall_number": "F-1-2026", "recalling_firm": "Made Up Foods", "classification": "Class I",
         "status": "Ongoing", "product_description": "Peanut cookies, 8 oz. Net wt.", "code_info": "Lot 7",
         "reason_for_recall": "Undeclared peanuts.", "report_date": "20261014"},
        {"event_id": "1", "recall_number": "F-2-2026", "recalling_firm": "Made Up Foods", "classification": "Class I",
         "status": "Ongoing", "product_description": "Peanut bars", "reason_for_recall": "Undeclared peanuts."}]


def fake_api(answers):
    """api_get answering by path."""
    def get(path, params, cache=None):
        return answers.get(path, {})
    return get


def test_months_and_keys(monkeypatch):
    monkeypatch.setattr(R, "today", lambda: datetime.date(2026, 11, 22))
    assert R.months()[0] == "2012-06" and R.months()[-1] == "2026-11" and len(R.months()) == 174
    assert len(sources.expand_keys(["recalls-all"])) == 175 <= 256
    assert sources.expand_keys(["recalls"])[-2:] == ["fda:recalls:2026-11", "fda:shortages"]
    assert sources.expand_keys(["fda:recalls:2025-01"]) == ["fda:recalls:2025-01"]
    assert {"fda:recalls:2026-11", "fda:shortages"} <= set(sources.expand_keys(["pub:daily"]))
    assert R.current("fda:recalls:2026-11") and not R.current("fda:recalls:2026-10")
    assert R.month_range("2024-02") == "[20240201 TO 20240229]"


def test_month_book(monkeypatch):
    monkeypatch.setattr(R, "today", lambda: datetime.date(2026, 11, 22))
    monkeypatch.setattr(R, "api_get", fake_api({"food/enforcement": {"meta": META, "results": ROWS}}))
    book = R.recalls_book("recalls:2026-10", "/tmp/none", None, [])
    assert [p.unit for p in book.pages] == ["About", "Food and cosmetics"]
    page = book.pages[1]
    assert page.title == "Made Up Foods: Peanut cookies, 8 oz and 1 more (Class I)"
    assert "Class I: a dangerous product" in page.body and page.body.count("<h3>") == 2
    assert book.licence == "CC0 1.0" and "Do not rely on openFDA" in book.notice and book.published == "2026-11-11"
    assert len(book.originals) == 3 and book.version.startswith("openFDA enforcement data")
    monkeypatch.setattr(R, "api_get", fake_api({"food/enforcement": {"meta": dict(META, license="x"),
                                                                     "results": ROWS}}))
    left = []
    assert R.recalls_book("recalls:2026-10", "/tmp/none", None, left) is None and "licence" in left[0]["reason"]
    left = []
    assert R.recalls_book("recalls:2011-01", "/tmp/none", None, left) is None


def test_announcements_are_titles_only(monkeypatch):
    import build_textbooks as B
    rss = ("<item><title>Made Up Co. Recalls Tea</title><link>http://www.fda.gov/safety/x</link>"
           "<description>FOR IMMEDIATE RELEASE - long company text</description>"
           "<pubDate>Fri, 20 Nov 2026</pubDate></item>")
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: rss)
    monkeypatch.setattr(R.K, "readable", lambda url, cache=None: True)
    page = R.announcements_page()
    assert '<a href="https://www.fda.gov/safety/x">Made Up Co. Recalls Tea</a>' in page.body
    assert "long company text" not in page.body


def test_shortages(monkeypatch):
    rows = [{"generic_name": "madeupicillin injection", "package_ndc": "1", "availability": "Limited",
             "company_name": "Acme", "status": "Current", "therapeutic_category": ["Infectious disease"]},
            {"generic_name": "madeupicillin injection", "package_ndc": "2", "availability": "Unavailable"}]
    monkeypatch.setattr(R, "api_get", fake_api({"drug/shortages": {"meta": META, "results": rows}}))
    book = R.shortages_book("shortages", "/tmp/none", None, [])
    assert [p.title for p in book.pages] == ["About the drug shortage list", "Madeupicillin injection"]
    assert "<td>Unavailable</td>" in book.pages[1].body and "Infectious disease" in book.pages[1].body
