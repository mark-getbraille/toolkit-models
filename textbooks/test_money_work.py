"""Self-test of the money, work and business books (money_work.py) and of the several-PDF book maker (pdf_set.py),
with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once under its request word "money-work" (at most 256 jobs) and reaches
sources.py with its group "Reference, money, work and business"; that every book has a licence the toolkit may
repackage, a notice ending with the not-advice line, a description, a licence page and line, and a page pattern
that takes its own addresses; that no IRS publication repeats one the library already has; that O*NET's database
address is found on a made-up download page and a made-up database is made into pages with its tasks, titles and Job
Zones, with O*NET's credit; that pdf_set joins made-up parts in order and leaves out a part that cannot be read; and
that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_money_work.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import money_work as M  # noqa: E402
import more_refs  # noqa: E402
import pdf_set  # noqa: E402
import sources  # noqa: E402
import thin_topics  # noqa: E402


def test_registered():
    assert "money_work" in more_refs.MODULES and M in more_refs.modules()
    assert sources.GROUPS["moneywork"] == "Reference, money, work and business"
    keys = sources.expand_keys(["money-work"])
    assert keys == M.COLLECTION.expand_keys(["money-work"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"mw:{n}" for n in list(M.COLLECTION.guides) + list(M.COLLECTION.pdfs)} | \
        {"mw:onet_occupations"}
    assert set(M.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in M.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_every_book():
    for g in M.GUIDES + M.PDFS:
        assert g["group"] == "moneywork", g["name"]
        assert B.licence_kind(B.licence_short(g["licence"])), g["name"]
        assert g["notice"].endswith(M.NOT_ADVICE), g["name"]
        assert g["description"] and g["licence_page"] and g["licence_text"], g["name"]
        if g in M.GUIDES:
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
    assert M.NOT_ADVICE == "General information, not tax or legal advice; check the current rules or ask a " \
                           "professional."


def test_irs_publications_not_repeated():
    have = {e["pdf"] for e in sources.PDF_DOCS if e.get("pdf")} | {e.get("pdf") for e in thin_topics.PDF_DOCS}
    for p in M.PDFS:
        assert p["pdf"].startswith("https://www.irs.gov/pub/irs-pdf/") and p["pdf"] not in have, p["name"]
    names = {p["name"] for p in M.PDFS}
    for n in ("503", "505", "523", "529", "583", "587"):
        assert f"irs_pub_{n}" in names, n
    assert "irs_i1040gi" in names and "irs_pub_535" not in names


def test_page_patterns():
    ebsa = re.compile(M.COLLECTION.guides["dol_ebsa_publications"]["pages"])
    base = "https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/resource-center/publications/"
    assert ebsa.match(base + "what-you-should-know-about-your-retirement-plan")
    assert not ebsa.match(base + "avoid-surprise-healthcare-expenses-es")
    assert not ebsa.match(base + "an-employees-guide-to-health-benefits-under-cobra-zh-sc")
    whd = re.compile(M.COLLECTION.guides["dol_whd_fact_sheets"]["pages"])
    assert whd.match("https://www.dol.gov/agencies/whd/fact-sheets/28-fmla")
    assert not whd.match("https://www.dol.gov/agencies/whd/fact-sheets/28-fmla/espanol")
    hc = re.compile(M.COLLECTION.guides["healthcare_gov_guides"]["pages"])
    assert hc.match("https://www.healthcare.gov/glossary/deductible/")
    assert not hc.match("https://www.healthcare.gov/help/how-to-apply/")


ONET_TABLES = {
    "Occupation Data.txt": "O*NET-SOC Code\tTitle\tDescription\n99-0001.00\tMade-up Tester\tTests made-up things.\n"
                           "98-0002.00\tSample Clerk\tKeeps sample records.\n",
    "Task Statements.txt": "O*NET-SOC Code\tTask ID\tTask\tTask Type\n99-0001.00\t1\tWrite a made-up test.\tSupplemental\n"
                           "99-0001.00\t2\tRun the made-up test.\tCore\n",
    "Sample of Reported Titles.txt": "O*NET-SOC Code\tReported Job Title\n99-0001.00\tTest Person\n",
    "Job Zones.txt": "O*NET-SOC Code\tJob Zone\n99-0001.00\t2\n",
    "Job Zone Reference.txt": "Job Zone\tName\n2\tSome Preparation Needed\n",
}


def test_onet_pages_from_made_up_tables():
    page = '<a href="/dl_files/database/db_77_1_excel.zip">Excel</a>'
    assert M.onet_zip_url(page) == "https://www.onetcenter.org/dl_files/database/db_77_1_text.zip"
    assert M.onet_zip_url("<p>nothing</p>") == ""
    pages = M.onet_pages(ONET_TABLES)
    assert [p[0] for p in pages] == ["group-98", "group-99"]
    body = pages[1][2]
    assert "Made-up Tester (99-0001.00)" in body and "Test Person" in body
    assert "Job Zone 2: Some Preparation Needed" in body
    assert body.index("Run the made-up test.") < body.index("Write a made-up test.")       # core tasks first
    credit = M.onet_credit("77.1")
    for words in ("O*NET 77.1 Database", "USDOL/ETA", "CC BY 4.0", "has modified", "not approved, endorsed"):
        assert words in credit, words


def test_pdf_set_joins_parts(monkeypatch, tmp_path):
    """Made-up parts are joined in order; a part that cannot be read is left out with its reason."""
    def fake(entry, work, cache=None, left_out=None):
        if "bad" in entry["pdf"]:
            left_out.append({"title": entry["title"], "reason": "made-up failure"})
            return None
        book = B.Book(name=entry["name"], title=entry["title"], subject="s", level="reference", group="moneywork",
                      publisher="p", country="United States", licence=sources.US_GOV, licence_url="u",
                      source=entry["page"], original_pdf={"url": entry["pdf"], "size": 3, "sha256": "abc"},
                      published="1999")
        book.pages = [B.Page("part-1-a", "A", "<p>a</p>", 1), B.Page("part-2-b", "B", "<p>b</p>", 2)]
        return book
    monkeypatch.setattr(B, "pdfdoc_book", fake)
    entry = dict(M.PDFS[0], name="mw_made_up", title="Made-up set", source="https://example.org/set")
    left_out = []
    book = pdf_set.pdf_set_book(entry, [("One", "https://example.org/1.pdf", "https://example.org/1"),
                                        ("Bad", "https://example.org/bad.pdf", "https://example.org/b"),
                                        ("Two", "https://example.org/2.pdf", "https://example.org/2")],
                                str(tmp_path), None, left_out)
    assert book.name == "mw_made_up" and book.title == "Made-up set" and book.source == "https://example.org/set"
    assert [(p.unit, p.chapter) for p in book.pages] == [("One", 1), ("One", 2), ("Two", 3), ("Two", 4)]
    assert [o["url"] for o in book.originals] == ["https://example.org/1.pdf", "https://example.org/2.pdf"]
    assert left_out and left_out[0]["reason"] == "made-up failure" and not book.original_pdf
