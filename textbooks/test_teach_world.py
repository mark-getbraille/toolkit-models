"""Self-test of teaching and homeschooling outside the US (teach_world.py), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once and its request words reach sources.expand_keys, each at most 256 jobs
and without duplicates; that every book is in the teaching group with a licence the toolkit may repackage, a
licence line checked at build time (or the pre-1931 year check for the old books), a description and a notice; that
no Internet Archive item or official page is listed twice here or elsewhere in the library; that the index has a
table row for every Canadian province and territory and that every link-only row says why; that Oak's sign-up entry
needs a key and is never built without one, its bulk data is turned into units and lessons with restricted
transcripts left out, and French, German and Spanish are left to the language collections; that ACARA's page reader
keeps the text blocks and leaves out the "On this page" list and the footer; and that every row of NOT_INCLUDED says
where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_teach_world.py
"""

import io
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import teach_world as T  # noqa: E402

WORDS = ["teach-world", "tworld-canada", "tworld-uk", "tworld-oak", "tworld-oak-primary", "tworld-oak-secondary",
         "tworld-ireland", "tworld-australia", "tworld-nz", "tworld-africa-asia", "tworld-ngo", "tworld-classics"]


def test_registered_and_word_sizes():
    assert more_refs.MODULES.count("teach_world") == 1 and T in more_refs.modules()
    for word in WORDS:
        keys = sources.expand_keys([word])
        assert keys == T.COLLECTION.expand_keys([word]), word
        assert keys and len(keys) == len(set(keys)) <= 256, word
        assert all(k.startswith("tworld:") for k in keys), word
    every = set(sources.expand_keys(["teach-world"]))
    assert every == set(T.COLLECTION.own_keys())
    assert T.GROUP in sources.GROUPS and set(T.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in T.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED


def test_every_book_has_an_allowed_licence_and_check():
    for e in list(T.COLLECTION.pdfs.values()) + list(T.COLLECTION.guides.values()):
        assert e["group"] == T.GROUP, e["name"]
        assert B.licence_kind(B.licence_short(e["licence"])) == "open", e["name"]      # no share-alike or NC here
        assert e["description"] and e["notice"] and e["title"] and e["subject"], e["name"]
        if e.get("archive"):
            assert e["old_public_domain"] and int(e["published"]) < 1931, e["name"]
        else:
            assert e["licence_text"] and (e.get("licence_page") or e.get("page")), e["name"]
            assert not e.get("personal_use"), e["name"]


def test_no_duplicates_in_the_library():
    ours = list(T.COLLECTION.pdfs.values())
    archives = [e["archive"] for e in ours if e.get("archive")]
    assert len(archives) == len(set(archives))
    pages = [(e.get("page"), e.get("pdf_pattern")) for e in ours if e.get("page")]
    assert len(pages) == len(set(pages))
    names = [e["name"] for e in ours] + list(T.COLLECTION.guides)
    assert len(names) == len(set(names))
    elsewhere = set()
    for m in more_refs.modules():
        if m is T:
            continue
        for e in list(m.COLLECTION.pdfs.values()) + list(m.COLLECTION.guides.values()):
            if e.get("archive"):
                elsewhere.add(e["archive"])
    elsewhere |= {e["archive"] for e in sources.PDF_DOCS if e.get("archive")}
    assert not set(archives) & elsewhere
    assert "in.ernet.dli.2015.150785" not in archives          # The Montessori Method is education_more.py's
    alberta = {e.get("page") for e in sources.PDF_DOCS if e.get("licence") == "OGL-Alberta"}
    assert not alberta & {e["page"] for e in T.ALBERTA_PDFS}


def test_every_province_and_territory_has_a_row():
    places = {row[0] for row in T.CANADA_ROWS}
    assert len(T.PROVINCES) == 13
    for p in T.PROVINCES:
        assert p in places, p
    for _part, _intro, rows in T.INDEX_SECTIONS:
        for place, what, url, status, _lib in rows:
            assert place and what and status, what
            assert url.startswith("https://"), url
    assert any("Oak" in r[1] for r in T.UK_ROWS) and any("ACARA" in r[1] for r in T.AUSTRALIA_ROWS)


def test_licences_kept_apart():
    """Built books are open (OGL, CC BY, public domain); non-commercial and copyright sources are links only and
    say so."""
    for _part, _intro, rows in T.INDEX_SECTIONS:
        for _place, what, _url, status, _lib in rows:
            if re.search(r"NC|non-commercial|personal use", status):
                assert "link-only" in status or "already" in status, what
            if "all rights reserved" in status.lower():
                assert "link-only" in status, what


def test_index_book(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    book = T.index_book("index", "/nonexistent")
    assert book.licence == "CC0 1.0" and book.group == T.GROUP
    assert len(book.pages) == len(T.INDEX_SECTIONS) + 1
    assert "<table>" in book.pages[0].body and "Nunavut" in book.pages[0].body
    assert T.index_sign("index") == T.index_sign("index")


def _bulk(piece):
    """A made-up Oak bulk JSON for one piece."""
    return {"sequenceSlug": piece, "subjectTitle": "Maths", "lessons": [
        {"lessonSlug": "counting-to-ten", "lessonTitle": "Counting to ten", "pupilLessonOutcome": "I can count.",
         "keyLearningPoints": [{"keyLearningPoint": "Numbers have an order."}],
         "lessonKeywords": [{"keyword": "count", "description": "say numbers in order"}],
         "misconceptionsAndCommonMistakes": [{"misconception": "Skipping seven.", "response": "Count slowly."}],
         "teacherTips": [{"teacherTip": "Use fingers."}], "contentGuidance": None, "supervisionLevel": None,
         "transcript_sentences": "One, two, three.", "restricted": False,
         "canonicalUrl": "https://example.org/lessons/counting-to-ten"},
        {"lessonSlug": "a-song", "lessonTitle": "A counting song", "restricted": True,
         "transcript_sentences": "Words of another owner."},
        {"lessonSlug": "loose", "lessonTitle": "A lesson no unit lists"}],
        "sequence": [{"unitSlug": "numbers", "unitTitle": "Numbers to ten", "year": "1", "keyStageSlug": "ks1",
                      "description": "Counting.", "threads": [{"title": "Number"}],
                      "priorKnowledgeRequirements": ["Saying some numbers."], "nationalCurriculumContent": ["Count"],
                      "unitLessons": [{"lessonSlug": "a-song", "lessonTitle": "A counting song", "lessonOrder": 2},
                                      {"lessonSlug": "counting-to-ten", "lessonTitle": "Counting to ten",
                                       "lessonOrder": 1},
                                      {"lessonSlug": "later", "lessonTitle": "Later", "lessonOrder": 3,
                                       "state": "new"}]}]}


def test_oak_pieces_and_languages():
    pieces = T.oak_pieces()
    assert len(pieces) == 27 and len(set(pieces)) == 27 and "citizenship-secondary" in pieces
    assert "citizenship-primary" not in pieces
    assert not any(p.split("-")[0] in T.OAK_LANGUAGES for p in pieces)
    assert sources.expand_keys(["tworld-oak-primary"]) + sources.expand_keys(["tworld-oak-secondary"]) and \
        set(sources.expand_keys(["tworld-oak"])) == set(sources.expand_keys(["tworld-oak-primary"]) +
                                                        sources.expand_keys(["tworld-oak-secondary"]))


def test_oak_needs_a_key(monkeypatch):
    monkeypatch.delenv(T.OAK_KEY_ENV, raising=False)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    left = []
    assert T.oak_book("oak:maths-primary", "/nonexistent", None, left) is None
    assert left[0]["fetch_yourself"] and T.OAK_KEY_ENV in left[0]["reason"]
    left = []
    assert T.oak_book("oak:french-primary", "/nonexistent", None, left) is None and left


def test_oak_book_from_made_up_bulk():
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as z:
        z.writestr("maths-primary.json", json.dumps(_bulk("maths-primary")))
        z.writestr("other.json", json.dumps(_bulk("science-primary")))
    doc = T.oak_json_from_zip(data.getvalue(), "maths-primary")
    book = T.oak_book_from_json(doc, "maths-primary")
    assert book.licence == "OGL-UK-3.0" and "Open Government Licence v3.0" in book.notice
    assert [p.title for p in book.pages] == ["Numbers to ten (1)", "Other lessons"]
    unit = book.pages[0].body
    assert unit.index("Counting to ten") < unit.index("A counting song")            # lesson order kept
    assert "One, two, three." in unit and "Words of another owner." not in unit    # restricted: no transcript
    assert "Skipping seven." in unit and "Count slowly." in unit and "Not published yet." in unit
    assert "A lesson no unit lists" in book.pages[1].body


def test_acara_reader():
    page = ('<title>Science | V9 Australian Curriculum</title>'
            '<div data-cmp-data-layer="{&#34;x&#34;:1}" id="text-1" class="cmp-text "><p>On this page</p></div>'
            '<div data-cmp-data-layer="{}" id="text-2" class="cmp-text "><p><a href="#a">Rationale</a></p>'
            '<p><a href="#b">Aims</a></p></div>'
            '<div data-cmp-data-layer="{&#34;y&#34;:&#34;&lt;h6>Rationale&lt;/h6>&#34;}" id="rationale" '
            'class="cmp-text "><h6>Rationale</h6></div>'
            '<div data-cmp-data-layer="{}" id="text-3" class="cmp-text "><p style="x">Science is <b>made up</b>'
            '&nbsp;here.</p></div>'
            '<div data-cmp-data-layer="{}" id="footer-copyright" class="cmp-text "><p>Copyright</p></div>')
    title, body = T.acara_html(page)
    assert title == "Science"
    assert body == "<h2>Rationale</h2><p>Science is <b>made up</b> here.</p>"
    assert len(T.ACARA_PAGES) == len(set(T.ACARA_PAGES)) and T.ACARA_PAGES[0].startswith(T.ACARA)


def test_not_included_says_where():
    for title, reason in T.NOT_INCLUDED:
        assert "Index: http" in reason, title
    names = " ".join(r[0] for r in T.NOT_INCLUDED)
    for words in ("Ontario", "Ireland", "Wales", "NCERT", "Philosophy of Education", "French"):
        assert words in names, words
