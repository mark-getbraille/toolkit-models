"""Self-test of the language learning books (languages.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once under its request word "languages" (at most 256 jobs) and reaches
sources.py with its group "Reference, language learning"; that the courses cover the languages the owner asked for
first; that the volumes of a made-up Internet Archive item are picked one per volume with the words (the "Text PDF",
else the "_text" PDF), and named by volume; that a made-up course's audio is listed as originals with its sizes and
never downloaded; that the Wikivoyage phrasebooks are share-alike with a pattern that takes each phrasebook; that
made-up Tatoeba files become pairs, shortest first, with each sentence's number; and that every row of NOT_INCLUDED
says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_languages.py
"""

import bz2
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import languages as L  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402


def test_registered():
    assert "languages" in more_refs.MODULES and L in more_refs.modules()
    assert sources.GROUPS["languages"] == "Reference, language learning"
    keys = sources.expand_keys(["languages"])
    assert keys == L.COLLECTION.expand_keys(["languages"]) and len(keys) == len(set(keys)) <= 256
    assert {f"lang:fsi:{c['key']}" for c in L.COURSES} <= set(keys)
    assert {f"lang:tatoeba:{c}" for c in L.TATOEBA_LANGUAGES} <= set(keys)
    assert sources.expand_keys(["lang:fsi"]) == [f"lang:fsi:{c['key']}" for c in L.COURSES]
    assert set(L.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in L.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_languages_asked_for_first():
    have = " ".join(c["language"] for c in L.COURSES)
    for language in ("Spanish", "French", "German", "Italian", "Portuguese", "Mandarin", "Japanese", "Korean",
                     "Russian", "Arabic", "Vietnamese", "Tagalog"):
        assert language in have, language
    phrase = " ".join(L.PHRASEBOOKS)
    assert "Haitian_Creole" in phrase and "hat" in L.TATOEBA_LANGUAGES
    for c in L.COURSES:
        entry = L.course_entry(c)
        assert entry["licence"] == sources.US_GOV and "audio recordings are listed" in entry["notice"], c["key"]
        assert entry["name"] == f"lang_fsi_{c['key']}" and entry["group"] == "languages"


def test_pick_pdfs_and_part_titles():
    files = [{"name": "Course-Volume1-StudentText.pdf", "format": "Image Container PDF"},
             {"name": "Course-Volume1-StudentText_text.pdf", "format": "Additional Text PDF"},
             {"name": "Course-Volume2-StudentText.pdf", "format": "Text PDF"},
             {"name": "Course-Volume2-InstructorsManual.pdf", "format": "Text PDF"},
             {"name": "notes.txt", "format": "Text"}]
    got = L.pick_pdfs(files, r"StudentText(_text)?\.pdf$")
    assert got == ["Course-Volume1-StudentText_text.pdf", "Course-Volume2-StudentText.pdf"]
    assert [L.part_title(n) for n in got] == ["Volume 1", "Volume 2"]
    assert L.part_title("FSI-StandardChinese-Module03MON-StudentText.pdf") == "Module 3 (MON)"


def test_audio_listed_never_downloaded(monkeypatch):
    made_up = [{"name": "Unit01.mp3", "source": "original", "size": "1234"},
               {"name": "Unit01_64kb.mp3", "source": "derivative", "size": "99"},
               {"name": "cover.jpg", "source": "original", "size": "5"}]
    monkeypatch.setattr(L, "ia_files", lambda item, cache=None: made_up)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    course = dict(L.COURSE["korean"], audio=[("ia", "madeupitem")])
    got = L.course_audio(course)
    assert got == [{"url": "https://archive.org/download/madeupitem/Unit01.mp3", "kind": "mp3", "size": 1234}]


def test_wikivoyage_phrasebooks():
    g = L.COLLECTION.guides["wikivoyage_phrasebooks"]
    assert g["licence"] == "CC BY-SA 4.0" and B.licence_kind(B.licence_short(g["licence"])) == "share-alike"
    assert "share-alike" in g["notice"] and g["licence_page"].endswith("Wikivoyage:Copyleft")
    pattern = re.compile(g["pages"])
    for url in g["urls"]:
        assert pattern.match(url), url
    assert not pattern.match("https://en.wikivoyage.org/wiki/Spain")


def test_tatoeba_pairs_from_made_up_files(tmp_path):
    def bz(name, lines):
        path = tmp_path / name
        with bz2.open(path, "wt", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return str(path)
    foreign = L.tatoeba_sentences(bz("spa.bz2", ["1\tspa\tHola.", "2\tspa\tBuenos días, señora.", "3\tspa\tSí."]))
    links = L.tatoeba_links(bz("links.bz2", ["1\t10", "1\t11", "2\t12", "3\t13", "9\t14"]), foreign)
    assert links == {"1": "10", "2": "12", "3": "13"}
    english = L.tatoeba_sentences(bz("eng.bz2", ["10\teng\tHello.", "11\teng\tHi.", "12\teng\tGood morning, madam.",
                                                 "13\teng\tYes.", "99\teng\tUnused."]), set(links.values()))
    assert "99" not in english
    pairs = L.tatoeba_pairs(links, foreign, english)
    assert [p[1] for p in pairs] == ["Sí.", "Hola.", "Buenos días, señora."]
    pages = L.tatoeba_pages("spa", pairs)
    assert len(pages) == 1 and pages[0][1] == "Sentences 1 to 3"
    assert "Good morning, madam." in pages[0][2] and "2, 12" in pages[0][2] and 'lang="spa"' in pages[0][2]
    assert B.licence_kind(B.licence_short("CC BY 2.0 FR")) == "open"
