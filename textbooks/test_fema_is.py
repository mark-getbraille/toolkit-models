"""Self-test of the FEMA Independent Study course books (fema_is.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once (request word fema-is and one word per theme, each at most 256 jobs)
and reaches sources.py; that every course has a unique number and key, a theme, a way to be read, a course date and
plain words on what it teaches, and that every built course is in exactly one theme; that the books the index links
to exist in the library and that no other module builds FEMA's course pages; that a newer lesson file and an older
lesson's table of contents and screens are read as they should be (classroom-only screens, hidden elements,
repeats, the player's help screens and the final exam left out; knowledge checks with their right answers); that a
screen with someone else's copyright notice is left out and a restricted marking stops a course; that a course book's
notice says FEMA, the course number, its date, public domain, its source and the exam; and that the index lists every
course.

Run it from the repository's folder:   python3 -m pytest textbooks/test_fema_is.py
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402
import fema_is as F  # noqa: E402


def test_registered():
    assert F in more_refs.modules() and more_refs.MODULES.count("fema_is") == 1
    keys = sources.expand_keys(["fema-is"])
    assert keys == F.COLLECTION.expand_keys(["fema-is"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == set(F.COLLECTION.own_keys()) and keys[0] == "fema:index"
    assert F.GROUP in sources.GROUPS and set(F.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    themed = []
    for word, _title, _subject in F.THEMES.values():
        part = sources.expand_keys([word])
        assert part == F.COLLECTION.expand_keys([word]) and 0 < len(part) == len(set(part)) <= 256, word
        themed += part
    assert len(themed) == len(set(themed)) and set(themed) | {"fema:index"} == set(keys)


def test_courses():
    codes = [c["code"] for c in F.COURSES]
    names = [c["name"] for c in F.COURSES]
    assert len(codes) == len(set(codes)) and len(names) == len(set(names))
    assert not set(names) & {d["name"] for d in F.DOCS} and "index" not in names
    for c in F.COURSES:
        assert re.fullmatch(r"IS-\d+(\.[a-z]|\.\d+)?", c["code"]), c["code"]
        assert c["theme"] in F.THEMES and c["via"] in ("sm", "web", "old", "link"), c["code"]
        assert c["teaches"].endswith(".") and len(c["teaches"]) > 40, c["code"]
        assert c["date"] == "" or re.fullmatch(r"\d{4}-\d\d-\d\d", c["date"]), c["code"]
        if c["via"] == "link":
            assert c["why"] and c["link"].startswith("https://"), c["code"]
        elif c["via"] == "sm":
            assert c.get("pdf") or (c.get("zip") and c.get("member")), c["code"]
        else:
            assert c["folder"] and not c["folder"].endswith("/"), c["code"]
    for code in ("IS-100.c", "IS-200.c", "IS-700.b", "IS-800.d", "IS-230.e", "IS-240.c", "IS-241.c", "IS-242.c",
                 "IS-244.b", "IS-317.a", "IS-366.a", "IS-405.a", "IS-505", "IS-909", "IS-907", "IS-5.a", "IS-10.a",
                 "IS-11.a", "IS-120.c", "IS-559", "IS-1300.a"):
        assert code in codes, code
    assert F.key_of("IS-100.c") == "is100c" and F.key_of("IS-246.25") == "is246_25" and F.key_of("IS-13") == "is13"
    assert "retired" in F.BY_NAME["is907"]["note"]


def test_related_books_exist_and_nothing_duplicated():
    library = set()
    for word in ("preparedness", "gpo-ready", "disasters"):
        library |= set(sources.expand_keys([word]))
    for key, _title, _what in F.RELATED:
        assert key in library, key
    for m in more_refs.modules():
        if m is F:
            continue
        c = m.COLLECTION
        for entry in list(c.guides.values()) + list(c.pdfs.values()):
            where = " ".join(str(entry.get(k) or "") for k in ("source", "pdf", "page", "crawl", "urls"))
            assert "emilms.fema.gov" not in where and "training.fema.gov" not in where, (m.__name__, entry["name"])


def test_not_included():
    for row in F.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in F.NOT_INCLUDED)
    for words in ("IS-800.d", "IS-324.a", "IS-271.a", "IS-368", "IS-394.a"):
        assert words in names, words


# ---------------------------------------------------------------------- a made-up newer lesson file

def el(kind, meta="", **more):
    """One made-up lesson element."""
    return dict(elementtype=kind, meta=meta, **more)


PRINT = [{"title": "Student Guide"}]
STRUCTURE = {"modules": [{"objects": [
    {"eodesc": "Lesson 1: Floods", "subeos": [
        {"page": {"title": "Flood Basics", "groups": [{"elements": [
            el("htm", "Flood Basics"),
            el("htm", "<p>Floods are the most common&nbsp;hazard.</p>"),
            el("htm", "<p>Floods are the most common hazard.</p>", publish_filters=PRINT),
            el("htm", "<p>FLOODS are the most common hazard.</p>"),
            el("image", description="A flooded street with cars"),
            el("image", description="clock"),
            el("htm", "<p>Hidden at every size.</p>", parameters={"responsive": {"layout": {
                "small": {"hidden": True}, "large": {"hidden": True}}}}),
            el("callout", "", elements=[el("htm", "Turn around, don't drown.")]),
        ]}]}},
        {"page": {"title": "Flood Discussion PRINT ONLY", "groups": [{"elements": [el("htm", "<p>Talk.</p>")]}]}},
        {"page": {"title": "Knowledge Check", "groups": [{"elements": [
            el("multipleChoiceQuestion", "Knowledge Check 1", txt="Is it safe to drive through floodwater?",
               elements=[el("questionOption", "Yes", parameters={"config": {"correct": False}}),
                         el("questionOption", "No", parameters={"config": {"correct": True}})]),
        ]}]}},
        {"page": {"title": "Using the Course Player", "groups": [{"elements": [el("htm", "<p>Buttons.</p>")]}]}},
    ]},
    {"eodesc": "Instructor notes", "publish_filters": PRINT, "subeos": [
        {"page": {"title": "Notes", "groups": [{"elements": [el("htm", "<p>Secret notes.</p>")]}]}}]},
]}]}
STRUCTURE_JS = "var courseStructure = " + json.dumps(STRUCTURE) + ";"


def test_web_lessons():
    lessons = F.web_lessons(STRUCTURE_JS)
    assert [lesson for lesson, _s in lessons] == ["Lesson 1: Floods"]
    screens = lessons[0][1]
    assert [t for t, _b in screens] == ["Flood Basics", "Knowledge Check"]
    basics = screens[0][1]
    assert basics.count("most common") == 1 and "Picture: A flooded street with cars" in basics
    assert "clock" not in basics.lower() and "Hidden" not in basics and "Turn around" in basics
    check = screens[1][1]
    assert "Knowledge check" in check and "floodwater" in check
    assert "<li>No (correct answer)</li>" in check and "<li>Yes</li>" in check


def test_newer_player_shows_tagged_items():
    """The newer player (typed filters) shows items tagged for the printed guides too, as EMI's lesson does when
    opened without a filter; repeats are still left out; a table is kept as a table."""
    typed = [{"title": "Student Guide", "type": 1, "culture_code": ""}]
    data = {"crslanguage": "en-US", "modules": [{"objects": [{"eodesc": "Lesson 1", "subeos": [{"page": {
        "title": "Shelters", "groups": [{"elements": [
            el("htm", "<p>Shelters open when officials say.</p>", publish_filters=typed),
            el("htm", "<p>Shelters open when officials say.</p>"),
            el("htm", "<table><tr><th>Item</th></tr><tr><td>Cot</td></tr></table>"),
            el("btn", "Next"), el("multiChoiceOption", "", txt="Option1"),
            el("videoembed", '<iframe title="Shelter video" src="https://example.org/v"></iframe>')]}]}}]}]}]}
    lessons = F.web_lessons("var courseStructure = " + json.dumps(data) + ";")
    body = lessons[0][1][0][1]
    assert body.count("Shelters open") == 1 and "<table>" in body and "<td>Cot</td>" in body
    assert "Next" not in body and "Option1" not in body and "Video (online only): Shelter video" in body
    assert F._filtered(typed, "") is False and F._filtered([{"title": "x", "type": 2}], "") is True
    assert F._filtered([{"title": "Instructor Guide"}]) is True and F._filtered([]) is False


def fake_fetch(pages):
    """A fetch that answers from a dict of made-up pages and fails for anything else."""
    def fetch(url, cache=None, binary=False, tries=4):
        if url not in pages:
            raise AssertionError(f"unexpected fetch {url}")
        return pages[url]
    return fetch


GOVINFO = "<p>" + K.GOVINFO_TEXT + "</p>"


def test_web_course_book(monkeypatch, tmp_path):
    c = F.BY_NAME["is10a"]
    url = F.EMILMS.format(folder=c["folder"]) + "courseStructure.js"
    monkeypatch.setattr(B, "fetch", fake_fetch({url: STRUCTURE_JS, K.GOVINFO_POLICY: GOVINFO}))
    monkeypatch.setattr(K, "last_modified", lambda u: "2025-03-17")
    left_out = []
    book = F.course_book("is10a", str(tmp_path), None, left_out)
    assert left_out == [] and book.name == "fema_is10a" and book.group == F.GROUP
    assert [p.title for p in book.pages] == ["Lesson 1: Floods"] and "<h2>Flood Basics</h2>" in book.pages[0].body
    for words in ("FEMA Emergency Management Institute", "IS-10.a", "course date 2015-10-02", "public domain",
                  "https://emilms.fema.gov/is_0010a/", "courseoverview.aspx?code=IS-10.a", "training.fema.gov",
                  "Student Identification number", "911"):
        assert words in book.notice, words
    assert book.licence == K.US_GOV and book.published == "2015-10-02" and "2025-03-17" in book.version
    assert book.originals == [{"url": url, "kind": "json"}]


def test_third_party_and_restricted(monkeypatch, tmp_path):
    c = F.BY_NAME["is10a"]
    left_out = []
    lessons = [("Lesson 1", [("Ours", "<p>FEMA's own words.</p>"),
                             ("Theirs", "<p>Photo © 2015 Someone Else. All rights reserved.</p>")])]
    book = F.lessons_book(c, lessons, "x", "y", left_out)
    assert "Theirs" not in book.pages[0].body and "Ours" in book.pages[0].body
    assert left_out and "copyright notice" in left_out[0]["reason"]
    left_out = []
    assert F.lessons_book(c, [("L", [("S", "<p>FOR OFFICIAL USE ONLY</p>")])], "x", "y", left_out) is None
    assert "FOR OFFICIAL USE ONLY" in left_out[0]["reason"]
    # The words "official use" in ordinary lesson text are not a marking.
    assert F.lessons_book(c, [("L", [("S", "<p>Keep forms for official use only when asked.</p>")])], "x", "y",
                          []) is not None


# ---------------------------------------------------------------------- a made-up older lesson

TREE = {"type": 5, "label": "IS-9999: Test", "children": [{"type": 4, "label": "IS-9999", "children": [
    {"type": 3, "label": "Lesson 1: Basics", "children": [{"type": 2, "label": "Lesson 1: Basics", "children": [
        {"type": 11, "label": "Welcome", "children": [{"type": 1, "contentType": 2, "label": "Welcome"}]},
        {"type": 11, "label": "Screen Features [Official]", "children": [{"type": 1, "contentType": 2,
                                                                           "label": "x"}]},
        {"type": 11, "label": "Safety [Official]", "children": [{"type": 1, "contentType": 2, "label": "Safety"}]},
    ]}]},
    {"type": 3, "label": "Lesson 2: More", "children": [{"type": 2, "label": "Lesson 2: More", "children": [
        {"type": 11, "label": "Going on", "children": [{"type": 1, "contentType": 2, "label": "Going on"}]},
        {"type": 11, "label": "Final Exam", "children": [{"type": 1, "contentType": 18, "label": "Call ShowExam"}]},
    ]}]},
]}]}
CURRICULUM = ("<html><script>\nde.addObject(" + json.dumps(TREE) + ");\nvar mapURL = de.urlMap;\n"
              + "".join(f'mapURL[{i}] = "../groups/{i + 2}.html";\n' for i in range(5)) + "</script></html>")


def screen(title, words, extra=""):
    """A made-up screen page of the older player."""
    return ('<html><body><div class="layout_container"><div id="G1" class="group_container"><style>x</style>'
            f'<div class="content_container"><div class="title_container"><span class="title">{title}</span></div>'
            f'<table><tr><td><span class="maintext"><P>{words}</P></span></td></tr></table></div>'
            '<img alt="Print" src="../media/1.gif"/><img alt="A shelter cot" src="../media/2.jpg"/>'
            "<a href=\"javascript: NewGrouping('X')\">Click this link to access a printable version</a>"
            f"{extra}</div></div></body></html>")


def test_old_plan_and_screens(monkeypatch, tmp_path):
    base = "https://emilms.fema.gov/is_0909/"
    plan = F.old_plan(CURRICULUM, base)
    assert plan == [("Lesson 1: Basics", [("Welcome", base + "groups/2.html"), ("Safety", base + "groups/4.html")]),
                    ("Lesson 2: More", [("Going on", base + "groups/5.html")])]
    body = F.old_screen(screen("Welcome", "Get a kit."), base + "groups/2.html")
    assert "<h3>Welcome</h3>" in body and "<p>Get a kit.</p>" in body and "Picture: A shelter cot" in body
    assert "Print" not in body and "printable" not in body and "<table" not in body and "<div" not in body
    assert F.old_screen("<html>Not found</html>", base) == ""
    pages = {base + "curriculum/1.html": CURRICULUM, K.GOVINFO_POLICY: GOVINFO,
             base + "groups/2.html": screen("Welcome", "Get a kit."),
             base + "groups/4.html": screen("Safety", "Stay safe."),
             base + "groups/5.html": screen("Going on", "Make a plan.")}
    monkeypatch.setattr(B, "fetch", fake_fetch(pages))
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    monkeypatch.setattr(K, "last_modified", lambda u: "2021-03-19")
    left_out = []
    book = F.course_book("is909", str(tmp_path), None, left_out)
    assert left_out == [] and [p.title for p in book.pages] == ["Lesson 1: Basics", "Lesson 2: More"]
    first = book.pages[0].body
    assert first.startswith("<h2>Welcome</h2>") and "<h3>Welcome</h3>" not in first and "<h2>Safety</h2>" in first
    assert len(book.originals) == 4 and "IS-909" in book.notice and "course date 2013-10-31" in book.notice


def test_old_knowledge_check():
    """An older screen's question comes from its script: the choices with the right one marked, then the
    explanation without the player's own words."""
    page = ('<div class="group_container"><form><span class="questiontext">ignored form copy</span></form>'
            '<script>var c = q1 = new Practice100(); c.description = "Which plan comes first?\\n<br \\/>Pick one.";'
            'c.formName = "F"; c.answers = [{"feedback":"","correct":true,"text":"The family plan"},'
            '{"feedback":"","correct":false,"text":"None"}];\n'
            'q1.remediation = {"always":[],"correct":["<p><span>Correct.</span> Review the feedback below. When you '
            'are ready to proceed, click on the Next button.</p><p>Plans start at home.</p>"]};\n</script></div>')
    body = F.old_screen(page, "https://emilms.fema.gov/is_0909/groups/9.html")
    assert "Which plan comes first?" in body and "<li>The family plan (correct answer)</li>" in body
    assert "<li>None</li>" in body and "Plans start at home." in body and "Explanation" in body
    assert "ignored form copy" not in body and "Next button" not in body and "Review the feedback" not in body


def test_link_course_is_not_built(monkeypatch, tmp_path):
    monkeypatch.setattr(B, "fetch", fake_fetch({K.GOVINFO_POLICY: GOVINFO}))
    left_out = []
    assert F.course_book("is800d", str(tmp_path), None, left_out) is None and "www.fema.gov" in left_out[0]["reason"]
    assert "fema:is800d" not in F.all_keys() and "fema:is324a" not in F.all_keys()


def test_index_book():
    book = F.index_book("index", None)
    text = " ".join(p.body for p in book.pages)
    for c in F.COURSES:
        assert html_has(text, c["code"]), c["code"]
        if c["via"] != "link":
            assert f"fema:{c['name']}" in text, c["code"]
    for key, _t, _w in F.RELATED:
        assert key in text, key
    for d in F.DOCS:
        assert f"fema:{d['name']}" in text
    assert "Student Identification number" in text and "training.fema.gov" in text
    assert book.licence == K.CC0 and book.pages[0].title.startswith("About")


def html_has(text, words):
    """True when the HTML holds the words (as escaped or not)."""
    return words in text or words.replace("&", "&amp;") in text


def test_docs():
    for d in F.DOCS:
        assert d["pdf"].startswith("https://training.fema.gov/") and d["licence"] == K.US_GOV
        assert d["description"] and "public domain" in d["notice"] and d["group"] == F.GROUP
