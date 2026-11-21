"""Self-tests of courses.py (open courses, K-12 books and personal-use courses) and of the K-12 web books, with
made-up data only: nothing is downloaded (every fetch is replaced by a small fake).

Run it from the repository's folder:   python3 -m pytest textbooks/test_courses.py
"""

import io
import json
import os
import sqlite3
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import courses  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402


# ---------------------------------------------------------------------- licences, grades, pieces

def test_licence_helpers():
    """The strictest licence wins; non-commercial and no-derivatives books are personal use only."""
    assert courses.strictest(["CC BY", "CC BY-SA"]) == "CC BY-SA"
    assert courses.strictest(["CC BY", "CC BY-NC"]) == "CC BY-NC"
    assert courses.strictest(["CC BY-SA", "CC BY-NC"]) == "CC BY-NC-SA"
    assert courses.strictest([]) == ""
    assert courses.is_personal("CC BY-NC-SA 4.0") and courses.is_personal("CC BY-ND 4.0")
    assert not courses.is_personal("CC BY 4.0") and not courses.is_personal("PD")
    assert courses.licence_address("CC BY-NC-SA 3.0") == "https://creativecommons.org/licenses/by-nc-sa/3.0/"
    assert courses.licence_address("CC BY") == "https://creativecommons.org/licenses/by/4.0/"
    assert B.licence_words("CC BY-NC 4.0", personal=True) == "CC BY-NC 4.0, not for commercial use, personal use only"


def test_grades_of_titles():
    """Grades are read from the words of a title."""
    assert courses.grades_of("Grade 3 Mathematics") == "3"
    assert courses.grades_of("Math by grade: 4th grade") == "4"
    assert courses.grades_of("Kindergarten English Language Arts") == "K"
    assert courses.grades_of("Prekindergarten Mathematics") == "PreK"
    assert courses.grades_of("Algebra I") == "9-12"
    assert courses.grades_of("CKLA Ancillary Materials, Sixth Grade") == "6"
    assert courses.grades_of("Basic HVAC") == ""


def test_pieces_are_stable_and_complete():
    """Every LibreTexts book and every OpenCourseWare course falls in exactly one piece, always the same one."""
    books = [{"bookID": f"{lib}-{n}", "library": lib} for lib in courses.LT_BUCKETS for n in range(200)]
    pieces = [p.split(":", 1)[1] for p in courses.lt_pieces()]
    for b in books:
        assert sum(courses.lt_in_piece(b, p) for p in pieces) == 1
    assert courses.bucket("chem-123", 7) == courses.bucket("chem-123", 7)
    ocw = [p.split(":", 1)[1] for p in courses.ocw_pieces()]
    for c in ["18-06-linear-algebra-spring-2010", "6-001-structure-fall-2005", "zz-9-unknown-dept-2020"]:
        assert sum(courses.ocw_in_piece(c, p) for p in ocw) == 1
    assert len(courses.expand_keys(["opencourses"])) == sum(courses.LT_BUCKETS.values()) + 1
    personal = courses.expand_keys(["personaluse"])
    assert "course:khan:math" in personal and "course:ocw:18-1" in personal and "course:bccampus" not in personal
    assert len(personal) + len(courses.expand_keys(["opencourses"])) < 256   # one workflow run's matrix limit
    k12 = sources.expand_keys(["k12"])
    assert "k12:im_grade_6_math" in k12 and "pdf:utah_science_6thgrade" in k12 and "course:engageny:grade-3-mathematics" \
        in k12 and "siyavula" in k12 and "course:khan:math-by-grade" in k12


def test_khan_academy_only_offline():
    """Khan Academy is read only from Kolibri Studio (or named in the Kiwix labels), never from khanacademy.org."""
    import re
    code = open(courses.__file__, encoding="utf-8").read()
    fetched = re.findall(r'"(https?://[^"]+)"', code)
    assert not [u for u in fetched if "khanacademy.org" in u and "read only through" not in u]
    assert courses.KOLIBRI["khan"]["personal"] and courses.KIWIX_LABELS["khanacademy_en_all"] == sources.PERSONAL_USE
    assert courses.SOURCES["khan"]["release"]("math").startswith("personal-")


# ---------------------------------------------------------------------- LibreTexts

def test_libretexts_licence_and_pages():
    """A LibreTexts book's licence comes from the catalogue; its PDF is cut into the online book's pages."""
    entry = {"bookID": "workforce-1", "license": "ccby", "libraryTags": ["licenseversion:40"]}
    assert courses.lt_licence(entry) == ("CC BY 4.0", "")
    assert courses.lt_licence({"license": "mixed"})[0] == ""
    assert "no licence" in courses.lt_licence({"license": ""})[1]
    pages = ["Fundamentals\nLicensing\nTable of contents 1.1: Fractions 1.2: Decimals " + "x " * 200,
             "1.1: Fractions\nA fraction is part of a whole.\nThis page titled 1.1: Fractions is shared under a CC BY "
             "license and was authored, remixed, and/or curated by Ann Author.",
             "1.1.2 https://workforce.libretexts.org/@go/page/7086\n1.2: Decimals\nA decimal has a point.\nThis page "
             "titled 1.2: Decimals is shared under a CC BY-SA license and was authored, remixed, and/or curated by "
             "Bo Writer.",
             "Index\n" + "word 1 " * 100]
    got = courses.lt_pages(pages)
    assert [g[0] for g in got] == ["Front matter", "1.1: Fractions", "1.2: Decimals", "Back matter"]
    assert got[2][1] == "CC BY-SA" and got[2][2] == "Bo Writer"
    assert "A decimal has a point." in got[2][3] and "@go/page" not in got[2][3]
    assert "[Page 3]" in got[2][3]
    assert courses.lt_country({"affiliation": "BC Campus"}) == "Canada"
    assert courses.lt_country({"affiliation": "De Anza College"}) == "United States"


# ---------------------------------------------------------------------- Kolibri

def make_channel(path):
    """A made-up Kolibri channel file: a book topic with a video (English subtitles), a web page and an exercise."""
    db = sqlite3.connect(path)
    db.executescript("""
    create table content_contentnode (id text, title text, kind text, description text, author text,
        license_name text, license_owner text, parent_id text, level int, lft int, rght int, tree_id int,
        sort_order real);
    create table content_file (id text, preset text, local_file_id text, contentnode_id text, lang_id text,
        priority int);
    create table content_localfile (id text, extension text, file_size int);
    create table content_channelmetadata (version int, last_updated text);
    insert into content_channelmetadata values (7, '2025-03-14');
    insert into content_contentnode values ('root', 'Made-up channel', 'topic', '', '', '', '', null, 0, 1, 14, 1, 0);
    insert into content_contentnode values ('top', 'Math by grade', 'topic', '', '', '', '', 'root', 1, 2, 13, 1, 1);
    insert into content_contentnode values ('book', '3rd grade', 'topic', '', '', '', '', 'top', 2, 3, 12, 1, 1);
    insert into content_contentnode values ('unit', 'Fractions', 'topic', '', '', '', '', 'book', 3, 4, 11, 1, 1);
    insert into content_contentnode values ('vid1', 'Halves', 'video', 'What a half is.', 'Sal', 'CC BY-NC-SA',
        'Khan Academy', 'unit', 4, 5, 6, 1, 1);
    insert into content_contentnode values ('web1', 'Fractions (Flexbook)', 'html5', '', '', 'CC BY', 'Maker',
        'unit', 4, 7, 8, 1, 2);
    insert into content_contentnode values ('ex1', 'Practice', 'exercise', '', '', 'Special Permissions', 'Maker',
        'unit', 4, 9, 10, 1, 3);
    insert into content_file values ('f1', 'video_subtitle', 'aa11', 'vid1', 'en', 1);
    insert into content_file values ('f2', 'html5_zip', 'bb22', 'web1', '', 1);
    insert into content_localfile values ('aa11', 'vtt', 10);
    insert into content_localfile values ('bb22', 'zip', 10);
    """)
    db.commit()
    db.close()


def test_kolibri_book(tmp_path, monkeypatch):
    """A Kolibri topic becomes a book: transcripts and web pages kept, exercises and unlicensed items counted."""
    make_channel(str(tmp_path / "chan.sqlite3"))
    channel = (tmp_path / "chan.sqlite3").read_bytes()
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as z:
        z.writestr("index.html", "<html><body><p>A fraction names part of a whole. " + "More words. " * 30 +
                   'The sum is <span class="x-ck12-mathEditor" data-tex="1%2F2%20%2B%201%2F2%20%3D%201"></span>.'
                   "</p></body></html>")
    vtt = b"WEBVTT\n\n00:00.000 --> 00:02.000\nA half is one of two equal parts.\n\n00:02.000 --> 00:04.000\n" \
          b"A half is one of two equal parts.\n"
    spec = dict(courses.KOLIBRI["khan"], id="0123456789abcdef")
    monkeypatch.setitem(courses.KOLIBRI, "made", spec)

    def fake_fetch(url, cache=None, binary=False, tries=4):
        """The made-up channel, subtitle and web page."""
        if url.endswith("robots.txt"):
            raise B.urllib.error.HTTPError(url, 404, "none", {}, None)
        data = {"databases": channel, "aa11.vtt": vtt, "bb22.zip": zbuf.getvalue(),
                "channels": json.dumps([{"id": spec["id"], "version": 7,
                                         "last_published": "2025-03-14T10:00:00Z"}]).encode()}
        key = next(k for k in data if k in url)
        return data[key] if binary else data[key].decode()
    monkeypatch.setattr(B, "fetch", fake_fetch)
    monkeypatch.setattr(B, "_robots", {})
    courses._MEMO.clear()
    left = []
    items, make, label = courses.kolibri_books("made", "math-by-grade", str(tmp_path / "work"), None, left)
    assert [i[1] for i in items] == ["3rd grade"]
    book = make(items[0])
    assert book.group == "k12" and book.grades == "3" and book.personal_use
    assert book.licence == "CC BY-NC-SA" and book.version.endswith("version 7") and book.published == "2025-03-14"
    titles = [p.title for p in book.pages]
    assert titles == ["Halves (video transcript)", "Fractions (Flexbook)"]
    assert all(p.unit == "Fractions" for p in book.pages)
    assert book.pages[0].body.count("A half is one of two equal parts.") == 1
    assert "1/2 + 1/2 = 1" in book.pages[1].body
    assert "Special Permissions" in book.description
    entry = B.write_book(book, str(tmp_path / "out"), versioned=True)
    assert entry["personal_use"] and entry["licence_text"].endswith("personal use only")


# ---------------------------------------------------------------------- MIT OpenCourseWare

def test_ocw_book(tmp_path, monkeypatch):
    """An OpenCourseWare course's offline zip becomes a book of its pages and video transcripts."""
    zbuf = io.BytesIO()
    lic = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
    with zipfile.ZipFile(zbuf, "w") as z:
        z.writestr("data.json", json.dumps({"course_title": "Made-up Algebra", "primary_course_number": "18.999",
                                            "term": "Fall", "year": "2020", "level": ["Undergraduate"],
                                            "instructors": [{"title": "Prof. A. Teacher"}],
                                            "topics": [["Mathematics", "Algebra"]],
                                            "course_description": "A made-up course."}))
        z.writestr("pages/syllabus/data.json", json.dumps({"title": "Syllabus", "license": lic,
                                                           "content": "<p>Read chapter one every week.</p>"}))
        z.writestr("resources/lecture-1/data.json", json.dumps({
            "title": "Lecture 1: Groups", "resourcetype": "Video", "parent_title": "Video Lectures", "license": lic,
            "video_files": {"video_captions_resources": [{"file": "/courses/x/ab_L1.vtt", "language": "en"}]}}))
        z.writestr("resources/l1cap/data.json", json.dumps({"title": "3play caption file", "resourcetype": "Other",
                                                            "license": lic, "file": "/courses/x/ab_L1.vtt"}))
        z.writestr("static_resources/ab_L1.vtt", "WEBVTT\n\n00:00.000 --> 00:01.000\nToday: groups.\n")
    pages = {"download/": '<a href="made.zip">Download course</a>'}

    def fake_fetch(url, cache=None, binary=False, tries=4):
        """The made-up download page and zip."""
        if url.endswith(".zip"):
            return zbuf.getvalue()
        return next(v for k, v in pages.items() if url.endswith(k))
    monkeypatch.setattr(B, "fetch", fake_fetch)
    monkeypatch.setattr(B, "head_size", lambda url: 1000)
    book = courses.ocw_book("18-999-made-up-algebra-fall-2020", str(tmp_path), None, [])
    assert book.title == "MIT 18.999 Made-up Algebra (Fall 2020)" and book.personal_use and book.group == "course"
    assert book.licence == "CC BY-NC-SA 4.0" and book.grades == "College (undergraduate)" and book.published == "2020"
    assert [p.title for p in book.pages] == ["Course home", "Syllabus", "Lecture 1: Groups (video transcript)"]
    assert "Today: groups." in book.pages[2].body


# ---------------------------------------------------------------------- K-12 web books and PDFs

def test_k12_entries():
    """Every K-12 web book and PDF has its grades, group, licence check and (for non-commercial ones) the personal
    use mark; OpenStax's high school books and Siyavula go to the K-12 group."""
    for e in sources.K12_GUIDES + [d for d in sources.PDF_DOCS if d["group"] == "k12"]:
        assert e["group"] == "k12" and e["grades"] and e["level"] == "school", e["name"]
        assert e.get("licence_text") or e.get("pdf_licence_text"), e["name"]
        kind = B.licence_kind(B.licence_short(e["licence"]))
        assert kind, e["name"]
        assert bool(e.get("personal_use")) == kind.startswith("non-commercial"), e["name"]
    assert sources.GROUPS["k12"] and "physics" in sources.OPENSTAX_HIGH_SCHOOL
    assert {"introduction-python-programming", "nursing-external-bundle"} <= set(sources.OSBOOKS)
    assert ("mathematics", 7, "Mathematics Grade 7", "Mathematics") in sources.SIYAVULA


def test_webguide_school_options(monkeypatch):
    """The options of a school web book: practice pages made from each lesson's address, titles from the page,
    paths from the address, formulas as text, the personal-use mark and grades."""
    site = "https://example.org/MS/students/1"
    lesson = ('<html><body><main><h1 class="x">Lesson 1</h1><p class="im-c-heading y">Tiling</p>'
              "<p>Area is \\(3 \\times 4\\) square units. Description: &lt;p&gt;A grid.&lt;/p&gt;</p></main>"
              "<footer>Licensed under the Creative Commons Attribution 4.0 International License</footer></body></html>")
    pages = {f"{site}/index.html": f'<a href="{site}/1/index.html">Unit 1</a> Licensed under the Creative Commons '
                                   "Attribution 4.0 International License",
             f"{site}/1/index.html": f'<h1>Unit 1: Area</h1><a href="{site}/1/1/index.html">Lesson 1</a>',
             f"{site}/1/1/index.html": lesson, f"{site}/1/1/practice.html": lesson.replace("Area is", "Find")}
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, binary=False: pages[url])
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    entry = sources._im("made_up", "Made-up Grade 6", "6", "MS", 1, "A made-up book.")
    entry = {k: (v.replace(sources.IM_SITE, "https://example.org") if isinstance(v, str) else v)
             for k, v in entry.items()}
    entry["start"] = [f"{site}/index.html"]
    entry["units"] = r"^https://example\.org/MS/students/1/\d+/index\.html$"
    entry["pages"] = r"^https://example\.org/MS/students/1/(\d+/\d+/index|glossary)\.html$"
    entry["personal_use"] = True
    left = []
    book = B.webguide_book(entry, None, left)
    assert not left
    assert [(p.path, p.title, p.unit) for p in book.pages] == [
        ("1-1", "Lesson 1: Tiling", "Unit 1: Area"), ("1-1-practice", "Lesson 1: Tiling (practice problems)",
                                                      "Unit 1: Area")]
    assert "3 × 4" in book.pages[0].body and "&lt;p&gt;" not in book.pages[0].body
    assert book.grades == "6" and book.group == "k12" and book.personal_use
    index = B.index_page(book)
    assert "Grade level: 6." in index and "Personal use only" in index


def test_mathml_as_text():
    """MathML formulas (Open Up Resources) are written as text."""
    out = B.mathml_spans('<p>Area <math xmlns="http://www.w3.org/1998/Math/MathML"><mn>5</mn><mo>×</mo>'
                         "<msup><mi>x</mi><mn>2</mn></msup></math></p>")
    assert 'aria-label="5 × x^2"' in out and "<math" not in out
    # A formula LaTeX cannot read (a stray backslash, as in a CK-12 page) is kept as written, not a crash.
    assert 'class="math"' in B.latex_spans("<p>\\(\\\\\\)</p>")


# ---------------------------------------------------------------------- weekly check, catalogue

def test_weekly_check_and_catalogue(monkeypatch, tmp_path):
    """The weekly check asks courses.py for a course key's sign and the web guide sign for a K-12 key; the catalogue
    names the groups, the left-out sources and the Kiwix labels."""
    monkeypatch.setattr(courses, "sign", lambda key: f"sign-of-{key}")
    assert updates.fingerprint("course:khan:math") == "sign-of-course:khan:math"
    seen = []
    monkeypatch.setattr(updates, "guide_sign", lambda entry: seen.append(entry["name"]) or "g")
    assert updates.fingerprint("k12:im_grade_6_math") == "g" and seen == ["im_grade_6_math"]
    data = B.merge([str(tmp_path / "none.json")])
    assert data["groups"]["k12"] == "School books (K-12)"
    assert any("SkillsCommons" in x["title"] for x in data["not_included"])
    assert data["kiwix_labels"]["khanacademy_en_all"] == sources.PERSONAL_USE
    assert "libretexts" in data["licence_lines"] and "k12" in data["group_notes"]


def test_vtt_text():
    """Subtitles become plain sentences without times and repeats."""
    words = courses.vtt_text("WEBVTT\n\n1\n00:00.000 --> 00:01.000\n<c>Hello there.</c>\n\n2\n00:01.000 --> "
                             "00:02.000\nHello there.\n\n3\n00:02.000 --> 00:03.000\nToday we add.\n")
    assert words == "Hello there. Today we add."
