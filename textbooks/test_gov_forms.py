"""Self-test of the US federal forms books (gov_forms.py, form:), with MADE-UP pages only: nothing is downloaded.

It checks that every form has a key under the request word gov-forms (under 256 jobs) in the group "Reference,
government forms", that every PDF and agency page is on the agency's own .gov address, that a book puts the agency's
"What this form is for" page first and then the form's PDFs, with the notice that says to file the current version
and that it is not advice, and that the forms not built (SSA, USCIS, FAFSA) are said with their addresses.

Run it from the repository's folder:   python3 -m pytest textbooks/test_gov_forms.py
"""

import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import gov_forms as G  # noqa: E402
import pdf_set  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402


def test_keys_group_and_addresses():
    keys = sources.expand_keys(["gov-forms"])
    assert len(keys) == len(G.FORMS) <= 256 and len(set(keys)) == len(keys)
    assert sources.GROUPS["govforms"] == "Reference, government forms"
    for want in ("form:irs_1040", "form:irs_w4", "form:irs_w9", "form:irs_1099_nec", "form:irs_4506_t",
                 "form:irs_8822", "form:cms_40b", "form:cms_l564", "form:medicare_summary_notice",
                 "form:va_21_526ez", "form:va_10_10ez", "form:va_21_4138", "form:state_ds_11", "form:state_ds_82"):
        assert want in keys, want
    for f in G.FORMS:
        for _title, pdf in f["pdfs"]:
            host = urllib.parse.urlsplit(pdf).hostname
            assert pdf.startswith("https://") and host.endswith(".gov") and pdf.lower().endswith(".pdf"), pdf
        if f["about"]:
            assert urllib.parse.urlsplit(f["about"]).hostname.endswith(".gov"), f["about"]
        assert f["description"] and f["subject"] and f["publisher"]
    assert "not legal or tax advice" in G.FORM_NOTICE and "current version" in G.FORM_NOTICE


def test_book_puts_the_agency_page_first(monkeypatch):
    page = ("<html><body><nav>menu</nav><main><h1>About Form W-4</h1><p>Complete Form W-4 so that your employer can "
            "withhold the correct federal income tax from your pay.</p><form>search</form></main></body></html>")
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: page)
    asked = []

    def made_up_set(entry, parts, work, cache=None, left_out=None, limit=None):
        asked.append((entry, parts))
        book = K.new_book(entry["name"], entry["title"], entry["subject"], entry["group"], entry["publisher"],
                          entry["licence"], entry["licence_url"], parts[0][2], entry["description"], "x")
        book.pages.append(B.Page("1-part-1", "Made-up form page", "<p>Step 1</p>", 1, parts[0][0]))
        return book
    monkeypatch.setattr(pdf_set, "pdf_set_book", made_up_set)
    left_out = []
    book = G.form_book("irs_w4", "work", None, left_out)
    assert book.name == "form_irs_w4" and book.group == "govforms" and not left_out
    assert book.pages[0].path == "what-this-form-is-for" and "withhold the correct" in book.pages[0].body
    assert "menu" not in book.pages[0].body and "search" not in book.pages[0].body
    assert book.pages[1].title == "Made-up form page" and book.notice == G.FORM_NOTICE
    assert asked[0][1][0][1] == "https://www.irs.gov/pub/irs-pdf/fw4.pdf"
    assert G.form_book("no_such_form", "work", None, left_out) is None and left_out


def test_not_included_rows():
    rows = " ".join(a + " " + b for a, b in G.NOT_INCLUDED)
    for words in ("SS-5", "SSA-827", "SSA-3368", "N-400", "I-765", "FAFSA", "403"):
        assert words in rows, words
    for row in G.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: https://" in row[1], row[0]
