"""Self-test of the parenting and family modules (parenting.py, early_childhood.py, read_aloud.py), with MADE-UP data
only: nothing is downloaded.

It checks that each book is registered once under its request word and reaches sources.py with its group "Reference,
parenting and family"; that every web guide has a licence the toolkit may repackage, a notice, a description, a
licence page and line and a working page pattern; that CDC's books are kept whole with CDC's conditions in the
notice; that the non-US and personal-use books say so; that every row of NOT_INCLUDED says where to find the source;
and that the picture-book and nursery-rhyme makers build their books from made-up channel and archive data.

Run it from the repository's folder:   python3 -m pytest textbooks/test_parenting.py
"""

import os
import re
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

NAMES = ("parenting", "early_childhood", "read_aloud")


def modules():
    """The parenting modules that exist."""
    return [m for m in more_refs.modules() if m.__name__ in NAMES]


def test_all_three_registered():
    assert {m.__name__ for m in modules()} == set(NAMES)
    assert sources.GROUPS["parenting"] == "Reference, parenting and family"


@pytest.mark.parametrize("m", [m for m in modules() if m.__name__ != "read_aloud"], ids=lambda m: m.__name__)
def test_guides_registered(m):
    c = m.COLLECTION
    word = next(iter(c.words))
    keys = sources.expand_keys([word])
    assert keys == c.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"{c.prefix}:{n}" for n in list(c.guides) + list(c.pdfs)}
    for g in list(c.guides.values()) + list(c.pdfs.values()):
        # the special education guides are in "Teaching and homeschooling" (group key "k12") since 2026-11-23
        assert g["group"] == ("k12" if g["name"] == "cpir_parent_guides" else "parenting"), g["name"]
        whole = bool(g.get("unchanged"))
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, whole), g["name"]
        assert g["notice"] and g["description"] and g["licence_page"] and g["licence_text"], g["name"]
        if g["name"] in c.guides:
            assert g.get("crawl") or g.get("urls"), g["name"]
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
        if g.get("country", "United States") != "United States":
            assert re.search(r"UK source|Canadian|Canada", g["notice"]), g["name"]
    assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in m.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_read_aloud_rows_reach_sources():
    import read_aloud as R
    assert set(R.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in R.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_cdc_books_whole_with_conditions():
    import early_childhood as E
    import parenting as P
    cdc = [g for g in P.GUIDES + E.GUIDES if g["publisher"] == P.CDC_PUBLISHER]
    assert len(cdc) == 5
    for g in cdc:
        assert g["unchanged"] and g["licence_page"] == P.CDC_TERMS, g["name"]
        for words in ("Source: CDC", "free of charge", "does not constitute its endorsement"):
            assert words in g["notice"], (g["name"], words)
        # every page of a CDC site except its Spanish copies, media files and the site index
        pattern = re.compile(g["pages"])
        site = g["crawl"][0][0].rsplit("/", 1)[0]
        assert pattern.match(site + "/index.html") and not pattern.match(site + "/site.html")
        assert not pattern.match(site + "/es/index.html")


def test_page_patterns():
    import early_childhood as E
    import parenting as P
    cpir = next(g for g in P.GUIDES if g["name"] == "cpir_parent_guides")
    pattern = re.compile(cpir["pages"])
    assert pattern.match("https://www.parentcenterhub.org/visualimpairment/")
    assert not pattern.match("https://www.parentcenterhub.org/buzz-may2023-issue2/")
    assert not pattern.match("https://www.parentcenterhub.org/login/")
    assert cpir["page_mark"] == P.CPIR_TEXT and cpir["licence"] == P.PD_DEDICATED
    assert B.licence_kind(P.PD_DEDICATED) == "open"
    nhs = next(g for g in E.GUIDES if g["name"] == "nhs_pregnancy_baby")
    assert nhs["country"] == "United Kingdom" and nhs["licence"] == "OGL-UK-3.0"
    assert "Open Government Licence v3.0" in nhs["notice"]
    assert re.match(nhs["pages"], "https://www.nhs.uk/baby/caring-for-a-newborn/")
    assert not re.match(nhs["pages"], "https://www.nhs.uk/best-start-in-life/")
    wic = next(g for g in E.GUIDES if g["name"] == "wic_breastfeeding")
    assert re.match(wic["pages"], "https://wicbreastfeeding.fna.usda.gov/low-milk-supply")
    assert not re.match(wic["pages"], "https://wicbreastfeeding.fna.usda.gov/site-map")


def test_practice_note_for_uk_books():
    assert "NHS" in sources.practice_note("United Kingdom", "Pregnancy and baby care", "Pregnancy and baby guides")


def _channel(path):
    """A made-up Kolibri channel file: one language folder with two stories (one under another licence) and a
    story listed twice."""
    db = sqlite3.connect(path)
    db.executescript("""
        create table content_contentnode (id text, title text, parent_id text, kind text, description text,
                                          author text, license_name text, license_owner text);
        create table content_file (contentnode_id text, preset text, local_file_id text, lang_id text,
                                   priority int);
        create table content_localfile (id text, extension text);
        create table content_channelmetadata (version int, last_updated text);
        insert into content_channelmetadata values (7, '2026-01-02');
        insert into content_contentnode values ('root', 'Made-up Books', null, 'topic', '', '', '', '');
        insert into content_contentnode values ('en', 'English', 'root', 'topic', '', '', '', '');
        insert into content_contentnode values ('aaaaaaaaaaaaaa1', 'The Red Kite', 'en', 'document',
                                                'A kite flies high.', 'A. Writer', 'CC BY', 'Made-up Press');
        insert into content_contentnode values ('aaaaaaaaaaaaaa2', 'Closed Story', 'en', 'document', '', 'B. Writer',
                                                'All Rights Reserved', 'Other Press');
        insert into content_contentnode values ('aaaaaaaaaaaaaa3', 'Blue Bird', 'en', 'document', '', 'C. Writer',
                                                'CC BY', 'Made-up Press');
        insert into content_file values ('aaaaaaaaaaaaaa1', 'document', 'abc123', 'en', 1);
        insert into content_localfile values ('abc123', 'pdf');
        insert into content_file values ('aaaaaaaaaaaaaa3', 'epub', 'def456', 'en', 1);
        insert into content_localfile values ('def456', 'epub');
    """)
    db.commit()
    return db


def test_picture_book(monkeypatch, tmp_path):
    import courses
    import read_aloud as R
    db = _channel(str(tmp_path / "c.sqlite3"))
    monkeypatch.setitem(R.CHANNELS, "madeup", dict(id="0" * 32, title="Made-up Books", country="South Africa",
                                                   publisher="Made-up Press", source="https://example.org/"))
    monkeypatch.setattr(R, "channel_db", lambda name, work: db)
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(courses, "kolibri_channel_info", lambda spec, cache=None: {"version": 7,
                                                                                   "last_published": "2026-01-02"})

    def fake_download(url, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()
        return path
    monkeypatch.setattr(courses, "download", fake_download)
    monkeypatch.setattr(courses, "pdf_pages_as_pages", lambda local, prefix, title, number, unit="", split=60:
                        [B.Page(prefix, title, "<p>The red kite flies over the hill.</p>", number, unit)])
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False, tries=4: b"epub bytes")
    monkeypatch.setattr(courses, "epub_html", lambda data: "<div>A blue bird sings.</div><p>Picture: A small blue "
                        "bird on a branch.</p>")
    assert R.pieces_of("madeup", str(tmp_path)) == ["english-0"]
    left_out = []
    book = R.picture_book("madeup", "english-0", str(tmp_path), None, left_out)
    assert [p.title for p in book.pages] == ["Blue Bird", "The Red Kite"]
    assert "Picture: A small blue bird" in book.pages[0].body and "By C. Writer." in book.pages[0].body
    book.pages = book.pages[1:]
    body = book.pages[0].body
    assert "A kite flies high." in body and "By A. Writer." in body and "Licence: CC BY 4.0." in body
    assert "red kite flies" in body and "1 stories under \"All Rights Reserved\"" in book.description
    assert book.licence == "CC BY 4.0" and book.group == "k12" and book.published == "2026-01-02"   # teaching
    assert book.grades.startswith("Read-aloud") and book.version.endswith("version 7")
    assert [o["kind"] for o in book.originals] == ["sqlite", "epub", "pdf"]


def test_read_aloud_keys(monkeypatch):
    import read_aloud as R
    monkeypatch.setattr(R, "pieces_of", lambda name, work=None: ["english-0", "english-1", "zulu-0"])
    keys = R.COLLECTION.expand_keys(["read-aloud"])
    assert "readaloud:nursery_rhymes" in keys and "readaloud:bookdash:english-0" in keys
    assert not any(k.endswith("zulu-0") for k in keys)
    assert "readaloud:african_storybook:zulu-0" in R.COLLECTION.expand_keys(["readaloud:african_storybook"])


def test_nursery_book(monkeypatch):
    import read_aloud as R
    asked = []

    def fake_pdfdoc(entry, work, cache=None, left_out=None):
        asked.append(entry)
        if entry["archive"] == "nurseryrhymesofe00hall":
            left_out.append({"title": entry["title"], "reason": "made-up refusal"})
            return None
        book = B.Book(name=entry["name"], title=entry["title"], subject="s", level="school", group="parenting",
                      publisher="p", country="United States", licence=entry["licence"],
                      licence_url=entry["licence_url"], source="https://archive.org/details/" + entry["archive"],
                      description="d", original_pdf={"url": "https://archive.org/download/x.pdf"})
        book.pages = [B.Page("chapter-1", "Chapter 1", "<p>Hey diddle diddle</p>", 1)]
        return book
    monkeypatch.setattr(B, "pdfdoc_book", fake_pdfdoc)
    left_out = []
    book = R.nursery_book("nursery_rhymes", "/tmp/none", None, left_out)
    assert all(e["old_public_domain"] and e["licence"] == R.OLD_LICENCE for e in asked)
    assert len(book.pages) == len(R.OLD_BOOKS) - 1 and left_out[0]["reason"] == "made-up refusal"
    assert book.pages[0].unit == R.OLD_BOOKS[0][1] and book.pages[0].path.startswith("realmothergoosewrig")
    assert book.published == "1925" and "OCR" in book.notice and book.licence == R.OLD_LICENCE
