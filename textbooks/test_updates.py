"""Self-tests of the weekly update check and the kept versions (updates.py), with made-up catalogue entries only:
nothing is downloaded.

Run it from the repository's folder:   python3 -m pytest textbooks/test_updates.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import updates as U  # noqa: E402


def entry(name, file, built, content, key="pdf:x", sign="abc", published=""):
    """A made-up catalogue entry."""
    return {"name": name, "file": file, "url": f"{B.RELEASE}/{file}", "size": 10, "sha256": "s" + file,
            "content_sha256": content, "date": built, "published": published, "key": key, "fingerprint": sign,
            "title": name, "group": "reference"}


def test_unchanged_source_is_not_rebuilt():
    """A book whose source still gives the same sign is not built again; a changed one is; one built before the
    check existed (no fingerprint) is rebuilt a few at a time; news and VOA (empty sign) never."""
    catalogue = {"books": [entry("a", "a.2026-01-01.zim", "2026-01-01", "c1", key="pdf:a", sign="same"),
                           entry("b", "b.2026-01-01.zim", "2026-01-01", "c2", key="law:b", sign="old"),
                           entry("c", "c_2025-01.zim", "2025-01-01", "c3", key="dspace", sign=""),
                           entry("n", "n_2026-11.zim", "2026-11-18", "c4", key="pub:voa:recent", sign="x")]}
    signs = {"pdf:a": "same", "law:b": "new", "pub:voa:recent": ""}
    assert U.changed_keys(catalogue, sign=lambda k: signs.get(k, "")) == ["law:b", "dspace"]
    assert U.changed_keys(catalogue, limit=1, sign=lambda k: signs.get(k, "")) == ["law:b"]


def test_changed_source_keeps_old_version():
    """A rebuilt book gets a new file and the old one stays listed in "versions" (newest first), with the newest in
    the book's own fields; a rebuild with the same text adds nothing; an older manifest never replaces the newest."""
    first = U.merge_versions(None, entry("a", "a.2026-01-01.zim", "2026-01-01", "text1", published="2025"))
    assert first["versions"][0]["change_note"] == "First version" and first["file"] == "a.2026-01-01.zim"
    second = U.merge_versions(first, entry("a", "a.2026-06-01.zim", "2026-06-01", "text2", published="2026-05"))
    assert second["file"] == "a.2026-06-01.zim" and [v["file"] for v in second["versions"]] == [
        "a.2026-06-01.zim", "a.2026-01-01.zim"]
    assert second["versions"][0]["change_note"].startswith("Rebuilt: the source changed")
    same = U.merge_versions(second, entry("a", "a.2026-07-01.zim", "2026-07-01", "text2"))
    assert same is second                                        # same text: no new version
    stale = U.merge_versions(second, entry("a", "a.2026-01-01.zim", "2026-01-01", "text1"))
    assert stale["file"] == "a.2026-06-01.zim" and len(stale["versions"]) == 2
    legacy = {k: v for k, v in entry("a", "a_2025-03.zim", "2025-03-01", "").items()}
    kept = U.merge_versions(legacy, entry("a", "a.2026-01-01.zim", "2026-01-01", "text1"))
    assert [v["file"] for v in kept["versions"]] == ["a.2026-01-01.zim", "a_2025-03.zim"]   # the old file stays


def test_same_month_news_file_replaces_its_version():
    """A news piece rebuilt under the same monthly name replaces that version instead of adding one."""
    first = U.merge_versions(None, entry("n", "n_2026-11.zim", "2026-11-17", "t1", key="pub:voa:recent"))
    again = U.merge_versions(first, entry("n", "n_2026-11.zim", "2026-11-18", "t2", key="pub:voa:recent"))
    assert len(again["versions"]) == 1 and again["versions"][0]["built"] == "2026-11-18"


def test_archive_plan():
    """Past ARCHIVE_AT files, the oldest kept versions (never a book's newest) move to yearly archive releases and
    their addresses follow."""
    books = []
    for i in range(3):
        b = None
        for built in ("2025-02-01", "2026-03-01", "2026-09-01"):
            b = U.merge_versions(b, entry(f"b{i}", f"b{i}.{built}.zim", built, built))
        books.append(b)
    catalogue = {"books": books}
    assert U.archive_plan(catalogue, {"textbooks": 5}, at=10, to=8) == ([], catalogue)
    moves, catalogue = U.archive_plan(catalogue, {"textbooks": 12, "publications-frus": 3}, at=10, to=8)
    assert len(moves) == 4 and moves[0] == {"file": "b0.2025-02-01.zim", "from": "textbooks",
                                            "to": "textbooks-archive-2025"}
    assert all(not m["file"].endswith("2026-09-01.zim") for m in moves)
    assert catalogue["books"][0]["versions"][-1]["url"].endswith("/textbooks-archive-2025/b0.2025-02-01.zim")


def test_content_checksum_ignores_file_identity(tmp_path):
    """Two builds of the same text have the same content checksum though their files differ."""
    book = B.Book(name="tiny", title="Tiny", subject="S", level="reference", group="reference", publisher="P",
                  country="X", licence="CC BY 4.0", licence_url="https://creativecommons.org/licenses/by/4.0/",
                  source="https://example.org/", pages=[B.Page("p", "Page", "<p>Words.</p>")])
    import datetime
    one = B.write_book(book, str(tmp_path), datetime.date(2026, 1, 1), versioned=True)
    two = B.write_book(book, str(tmp_path), datetime.date(2026, 2, 1), versioned=True)
    assert one["file"] == "tiny.2026-01-01.zim" and two["file"] == "tiny.2026-02-01.zim"
    assert one["content_sha256"] == two["content_sha256"] and one["sha256"] != two["sha256"]
