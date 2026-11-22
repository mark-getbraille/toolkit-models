"""Self-tests of the "originals" field of textbooks.json (build_textbooks.originals_of and its helpers), with
made-up books only: nothing is downloaded (robots.txt answers are given by the test).

It checks that every book lists its original PDF, EPUB, the files its driver recorded and its source page, each with
its kind, size, SHA-256, licence and may_download; that may_download is true only when the licence allows copying,
the site's terms do not forbid programs and robots.txt allows it (and false, with the reason, otherwise); that the
welcome page lists the originals with links; that write_book puts them in the catalogue entry next to original_pdf
and original_epub; that merge() gives the field to books built before it existed; and that the README documents
the field and where the catalogues are.

Run it from the repository's folder:   python3 -m pytest textbooks/test_originals.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import sources  # noqa: E402

FIELDS = {"url", "kind", "size", "sha256", "licence", "may_download", "why"}


def made_up_book(**kw):
    """A small made-up book with an original PDF, an EPUB, one extra original and a source page."""
    fields = dict(name="madeup_book", title="Made-up Book", subject="Science", level="school", group="textbooks",
                  publisher="Made-up Press", country="United States", licence="CC BY 4.0",
                  licence_url="https://creativecommons.org/licenses/by/4.0/", source="https://books.example.org/madeup",
                  original_pdf={"url": "https://books.example.org/madeup.pdf", "size": 1234, "sha256": "ab" * 32},
                  original_epub={"url": "https://books.example.org/madeup.epub", "size": 99, "sha256": ""},
                  originals=[{"url": "https://books.example.org/madeup-src.zip", "kind": "zip"},
                             {"url": "https://books.example.org/madeup.pdf"}])         # listed once only
    fields.update(kw)
    book = B.Book(**fields)
    book.pages = [B.Page("chapter-1", "Chapter 1: Light", "<p>Light is fast.</p>", 1)]
    return book


def test_kinds():
    assert B.original_kind("https://x.org/a/book.PDF") == "pdf"
    assert B.original_kind("https://downloads.libretexts.org/api/v1/download/123/pdf") == "pdf"
    assert B.original_kind("https://x.org/course.zip") == "zip" and B.original_kind("https://x.org/a.mp3") == "mp3"
    assert B.original_kind("https://x.org/db/abc.sqlite3") == "sqlite"
    assert B.original_kind("https://x.org/guide/") == "html" and B.original_kind("https://x.org/p.htm") == "html"
    assert B.source_address("https://www.ck12.org/ (read only through Kolibri Studio)") == "https://www.ck12.org/"
    assert B.source_address("not an address") == ""


def test_permission_rules():
    yes = lambda url: True        # noqa: E731
    no = lambda url: False        # noqa: E731
    may, why = B.download_permission("https://a.org/x.pdf", True, "CC BY 4.0", yes)
    assert may and "allows copying" in why and "robots.txt of a.org allows" in why
    may, why = B.download_permission("https://a.org/x.pdf", True, "CC BY-NC 4.0, not for commercial use, personal "
                                     "use only", yes)
    assert may and "for personal use" in why
    assert B.download_permission("https://a.org/x.pdf", False, "All rights reserved", yes) == \
        (False, "The licence (All rights reserved) does not allow copying; open the link in a browser to read it.")
    may, why = B.download_permission("https://a.org/x.pdf", True, "CC BY 4.0", no)
    assert not may and "robots.txt of a.org does not allow" in why and "browser" in why
    may, why = B.download_permission("https://a.org/x.pdf", True, "CC BY 4.0", None)
    assert not may and "not checked" in why
    may, why = B.download_permission("https://www.khanacademy.org/math", True, "CC BY-NC-SA", yes)
    assert not may and why.startswith(sources.NO_AUTOMATED_DOWNLOAD["www.khanacademy.org"])


def test_copy_allowed():
    """Every licence a built book may have allows copying the original unchanged, NoDerivatives ones included."""
    for licence in ("CC BY 4.0", "CC BY-SA 4.0", "CC BY-NC-SA 4.0", "CC BY-ND 4.0", "CC BY-NC-ND 2.5",
                    sources.US_GOV, "OGL-UK-3.0", "W3C Document License", "Public domain (US drug labeling)"):
        assert B.copy_allowed(licence), licence
    assert not B.copy_allowed("All rights reserved")


def test_originals_of_a_book():
    book = made_up_book()
    got = B.originals_of(book, lambda url: "blocked" not in url)
    assert [o["url"] for o in got] == ["https://books.example.org/madeup.pdf", "https://books.example.org/madeup.epub",
                                       "https://books.example.org/madeup-src.zip", "https://books.example.org/madeup"]
    assert all(set(o) == FIELDS for o in got)
    assert [o["kind"] for o in got] == ["pdf", "epub", "zip", "html"]
    assert got[0]["size"] == 1234 and got[0]["sha256"] == "ab" * 32 and got[2]["size"] == 0
    assert all(o["licence"] == "CC BY 4.0" and o["may_download"] for o in got)
    personal = B.originals_of(made_up_book(licence="CC BY-NC-SA 4.0", personal_use=True), lambda url: True)
    assert personal[0]["licence"].endswith("personal use only") and personal[0]["may_download"]
    unchecked = B.originals_of(book)                       # no robots answer: never downloadable
    assert not any(o["may_download"] for o in unchecked)


def test_welcome_page_and_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: not url.endswith(".epub"))
    book = made_up_book()
    entry = B.write_book(book, str(tmp_path), versioned=True)
    assert entry["original_pdf"]["url"] == "https://books.example.org/madeup.pdf"      # kept for compatibility
    assert entry["original_epub"]["url"] == "https://books.example.org/madeup.epub"
    by_url = {o["url"]: o for o in entry["originals"]}
    assert by_url["https://books.example.org/madeup.pdf"]["may_download"]
    assert not by_url["https://books.example.org/madeup.epub"]["may_download"]
    json.dumps(entry)                                      # plain JSON
    page = B.index_page(book)
    assert "<h2>Originals</h2>" in page
    for url in by_url:
        assert f'<a href="{url}">' in page
    assert "may be downloaded" in page and "open it in a browser" in page


def test_robots_errors_are_not_checked(monkeypatch):
    def broken(url, cache=None):
        raise KeyError(url)
    monkeypatch.setattr(B, "allowed_by_robots", broken)
    assert B.robots_for_originals("https://a.org/x") is None


def test_merge_gives_old_books_their_originals(tmp_path):
    old = {"books": [{"name": "old_book", "group": "textbooks", "title": "Old Book", "licence": "CC BY 4.0",
                      "licence_text": "CC BY 4.0", "source": "https://old.example.org/book",
                      "original_pdf": {"url": "https://old.example.org/book.pdf", "size": 5, "sha256": ""},
                      "original_epub": {}}]}
    data = B.merge([], old)
    book = data["books"][0]
    assert [o["url"] for o in book["originals"]] == ["https://old.example.org/book.pdf", "https://old.example.org/book"]
    assert not book["originals"][0]["may_download"] and "not checked" in book["originals"][0]["why"]
    again = B.merge([], old, robots=lambda url: True)
    assert all(o["may_download"] for o in again["books"][0]["originals"])
    kept = B.merge([], {"books": [dict(old["books"][0], originals=[])]})
    assert kept["books"][0]["originals"] == []             # a field already there is left as it is


def test_drivers_record_their_originals():
    """The drivers that know more original files record them (read from the code, so nothing is downloaded)."""
    here = os.path.dirname(os.path.abspath(__file__))
    code = {n: open(os.path.join(here, n), encoding="utf-8").read()
            for n in ("build_textbooks.py", "periodicals.py", "medications.py", "courses.py", "animal_sounds.py")}
    assert "/archive/\"" in code["build_textbooks.py"] and "'HEAD'}.zip" in code["build_textbooks.py"]  # OpenStax
    # repositories: the pinned commit's zip, or HEAD's
    assert 'book.originals.append({"url": url, "kind": "html"})' in code["build_textbooks.py"]   # web guides
    assert "book.originals = [{\"url\": url}" in code["build_textbooks.py"]   # laws
    assert "reports.csv" in code["periodicals.py"] and "MAX_ORIGINALS" in code["periodicals.py"]
    assert "/spls/{lab.setid}.xml" in code["medications.py"]
    assert "OCW_ZIPS[course]" in code["courses.py"] and ".sqlite3\", \"kind\": \"sqlite\"" in code["courses.py"]
    assert '"kind": "mp3"' in code["animal_sounds.py"]


def test_readme_documents_originals():
    readme = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "README.md"), encoding="utf-8").read()
    assert "https://github.com/mark-getbraille/toolkit-models/releases/download/textbooks/textbooks.json" in readme
    assert "https://github.com/mark-getbraille/toolkit-models/releases/download/manuals/manuals.json" in readme
    assert "manuals-<key>.<YYYY-MM-DD>.json.gz" in readme and "B:\\Original sources" in readme
    for field in FIELDS:
        assert f"`{field}`" in readme, field
