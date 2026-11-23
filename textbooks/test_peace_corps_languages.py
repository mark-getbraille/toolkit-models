"""Self-test of the Peace Corps language courses (peace_corps_languages.py, pclang:), with MADE-UP data only: nothing
is downloaded.

It checks that the module is registered once with its prefix and reaches sources.py in the group "Reference,
language learning", with its licence lines and NOT_INCLUDED rows (each with an address); that every request word
(peace-corps-languages and the five regions) is at most 256 jobs, the regions together give every course once, and
each starts with the index; that no course, source file or ERIC document is used twice, here or by any other module
(extend, never duplicate: the Tagalog course of languages.py stays there); that every course names a language of the
index, a Peace Corps office, a US government licence and a truthful notice (its scan notes and its audio line); that a
made-up archive folder list gives the right files and sizes, and recordings are listed, never downloaded; that the
parts of a course are named and numbered; and that the index is made offline, one page per region, with where each
language is spoken, its keys, its recordings and its links only.

Run it from the repository's folder:   python3 -m pytest textbooks/test_peace_corps_languages.py
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import languages  # noqa: E402
import more_refs  # noqa: E402
import peace_corps_languages as P  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REGION_WORDS = ["pclang-africa", "pclang-asia-pacific", "pclang-europe-asia", "pclang-americas", "pclang-mena"]

FOLDER = """<table><tr><th><a href="?C=N;O=D">Name</a></th></tr>
<tr><td><a href="/languages/">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td></tr>
<tr><td><a href="XX_Madeup_Language_Lessons.pdf">XX_Madeup_Language_Lessons.pdf</a></td>
<td align="right">2020-01-01 10:00  </td><td align="right">254K</td></tr>
<tr><td><a href="XX_Madeup_Lesson_1.mp3">XX_Madeup_Lesson_1.mp3</a></td>
<td align="right">2020-01-01 10:00  </td><td align="right">2.6M</td></tr>
<tr><td><a href="YY_Other_Lesson_1.mp3">YY_Other_Lesson_1.mp3</a></td>
<td align="right">2020-01-01 10:00  </td><td align="right">1.0M</td></tr>
<tr><td><a href="Made%20up%20course.pdf">Made up course.pdf</a></td>
<td align="right">2020-01-01 10:00  </td><td align="right">1.2M</td></tr>
<tr><td><a href="audios/">audios/</a></td><td align="right">2020-01-01 10:00  </td><td align="right">  - </td></tr>
</table>"""


def test_registered_in_the_language_group():
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert "peace_corps_languages" in more_refs.MODULES and P in more_refs.modules()
    assert prefixes.count("pclang") == 1
    assert P.GROUPS == languages.GROUPS and sources.GROUPS["languages"] == "Languages"
    assert set(P.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in P.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_request_words_and_their_sizes():
    every = sources.expand_keys(["peace-corps-languages"])
    assert every == P.COLLECTION.expand_keys(["peace-corps-languages"])
    assert 0 < len(every) == len(set(every)) <= 256 and set(every) == set(P.COLLECTION.own_keys())
    assert every[0] == "pclang:index"
    seen = []
    for word in REGION_WORDS:
        keys = sources.expand_keys([word])
        assert 1 < len(keys) == len(set(keys)) <= 256 and keys[0] == "pclang:index", word
        seen += keys[1:]
    general = [f"pclang:{c['key']}" for c in P.COURSES if P.region_of(c) == "general"]
    assert len(seen) == len(set(seen)) and set(seen) | set(general) == set(every) - {"pclang:index"}
    assert sources.expand_keys(["pclang:swahili_tanzania_1994"]) == ["pclang:swahili_tanzania_1994"]


def test_no_course_or_source_twice():
    keys = [c["key"] for c in P.COURSES]
    assert len(keys) == len(set(keys)) and "index" not in keys
    places = [(t[1], t[2]) for c in P.COURSES for t in c["text"]]
    assert len(places) == len(set(places))
    audio = [(a[1], a[2]) for c in P.COURSES for a in c["audio"]]
    assert len(audio) == len(set(audio))
    # the Peace Corps Tagalog course of languages.py is not built again
    tagalog = languages.COURSE["tagalog"]["text"][0][1]
    assert tagalog not in {t[1] for c in P.COURSES for t in c["text"]}


def test_no_other_module_reads_the_same_documents():
    mine = open(os.path.join(HERE, "peace_corps_languages.py"), encoding="utf-8").read()
    erics = set(re.findall(r'eric\("(ED\d{6})"', mine))
    files = {t[2].strip("/$").replace("\\", "") for c in P.COURSES for t in c["text"] if t[0] == "page"}
    assert len(erics) > 80 and len(files) > 50
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.basename(path) in ("peace_corps_languages.py", "test_peace_corps_languages.py"):
            continue
        text = open(path, encoding="utf-8").read()
        for number in erics:
            assert number not in text, (number, path)
        assert "languages/PeaceCorps" not in text, path


def test_every_course_is_a_truthful_peace_corps_book():
    regions = set(P.REGIONS)
    for c in P.COURSES:
        assert c["language"] in P.LANGS and P.LANGS[c["language"]][0] in regions, c["key"]
        assert c["text"] and c["description"] and c["office"].startswith("Peace Corps") and c["country"], c["key"]
        assert re.fullmatch(r"(19[6-9]\d|20[01]\d)?", c["year"]), c["key"]
        entry = P.course_entry(c)
        assert entry["licence"] == sources.US_GOV and entry["group"] == "languages", c["key"]
        assert entry["name"] == f"pclang_{c['key']}" and c["office"] in entry["notice"], c["key"]
        assert "a work of the US government (public domain)" in entry["notice"], c["key"]
        if c["audio"]:
            assert "recordings (MP3) are listed as originals" in entry["notice"], c["key"]
        else:
            assert "No recordings" in entry["notice"], c["key"]
        if c["ocr"] == "poor":
            assert "Poor scan" in entry["notice"], c["key"]
        elif c["ocr"] in ("script", "font"):
            assert c["script"] and c["script"] in entry["notice"], c["key"]
        else:
            assert c["ocr"] == "" and not c["script"], c["key"]
        for kind, where, pattern, _part in c["text"]:
            assert (kind == "ia" and re.fullmatch(r"ERIC_ED\d{6}", where)) or \
                (kind == "page" and where.startswith(P.YOJIK_PC + "/") and where.endswith("/")), c["key"]
            re.compile(pattern)
        for kind, where, pattern in c["audio"]:
            assert kind == "page" and where.startswith(P.YOJIK_PC + "/") and pattern.endswith(r"\.mp3$"), c["key"]
    for lang, title, url, why in P.LINKS:
        assert lang in P.LANGS and title and url.startswith("https://") and why, title


def test_folder_list_and_audio_never_downloaded(monkeypatch):
    calls = []

    def fake_fetch(url, cache=None, binary=False):
        calls.append(url)
        assert not url.endswith(".mp3"), "a recording must never be downloaded"
        return FOLDER
    monkeypatch.setattr(B, "fetch", fake_fetch)
    page = P.folder("Made up")
    assert page == f"{P.YOJIK_PC}/Made%20up/"
    got = P.folder_files(page, r"/XX_Madeup_Lesson[^/]*\.mp3$")
    assert got == [(f"{P.YOJIK_PC}/Made%20up/XX_Madeup_Lesson_1.mp3", 2600000)]
    made_up = P.course("madeup_test", "Swahili (Kiswahili)", "A Made-up Course", "1999", "course",
                       "Peace Corps Nowhere", [P.yj("Made up", r"Made up course\.pdf")], "Made up.",
                       audio=[P.mp3("Made up", r"XX_Madeup_Lesson[^/]*\.mp3"), P.mp3("Made up")], country="Nowhere")
    audio = P.course_audio(made_up)
    assert [a["url"].rsplit("/", 1)[1] for a in audio] == ["XX_Madeup_Lesson_1.mp3", "XX_Madeup_Lesson_1.mp3",
                                                           "YY_Other_Lesson_1.mp3"]
    assert all(a["kind"] == "mp3" and a["size"] > 0 for a in audio)
    parts = P.course_parts(made_up)
    assert parts == [("A Made-up Course", f"{P.YOJIK_PC}/Made%20up/Made%20up%20course.pdf", page)]
    assert all(u == page for u in calls)


def test_eric_parts_named_and_numbered(monkeypatch):
    files = {"ERIC_ED000001": [{"name": "ERIC_ED000001.pdf", "format": "Image Container PDF"},
                               {"name": "ERIC_ED000001_text.pdf", "format": "Additional Text PDF"},
                               {"name": "ERIC_ED000001_djvu.txt", "format": "DjVuTXT"}],
             "ERIC_ED000002": [{"name": "ERIC_ED000002.pdf", "format": "Text PDF"},
                               {"name": "ERIC_ED000002b.pdf", "format": "Text PDF"}]}
    monkeypatch.setattr(P.L, "ia_files", lambda item, cache=None: files[item])
    made_up = P.course("madeup_two", "Guarani", "Made-up Basic Course", "1968", "course", "Peace Corps Nowhere",
                       [P.eric("ED000001", "Part I"), P.eric("ED000002", "Part II")], "Made up.", country="Nowhere")
    parts = P.course_parts(made_up)
    assert [p[0] for p in parts] == ["Part I", "Part II (1)", "Part II (2)"]
    assert parts[0][1] == "https://archive.org/download/ERIC_ED000001/ERIC_ED000001_text.pdf"
    assert parts[0][2] == "https://archive.org/details/ERIC_ED000001"
    assert "ERIC document ED000001" in P.course_notice(made_up)


def test_index_made_offline(monkeypatch):
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    book = P.index_book("index", "unused")
    titles = [p.title for p in book.pages]
    assert len(book.pages) == 1 + len(P.REGIONS)
    assert titles[1:] == [t for _w, t, _c in P.REGIONS.values()]
    assert book.licence == "CC0 1.0" and book.group == "languages"
    every = " ".join(p.body for p in book.pages)
    for c in P.COURSES:
        assert f"pclang:{c['key']}" in every, c["key"]
    assert "lang:fsi:tagalog" in every and "recordings listed" in every and "no recordings" in every
    for lang in {c["language"] for c in P.COURSES}:
        assert f"<h2>{B.esc(lang)}</h2>" in every and B.esc(P.LANGS[lang][1]) in every, lang
    for _lang, title, url, _why in P.LINKS:
        assert B.esc(title) in every and B.esc(url) in every, title
    for word in REGION_WORDS + ["peace-corps-languages"]:
        assert word in every
    assert P.index_sign("index") == P.index_sign("index")


def test_counts_cover_every_region():
    counts = {r: len(P.keys_of(r)) for r in P.REGIONS}
    assert counts["africa"] > 50 and counts["asia-pacific"] > 20 and counts["europe-asia"] > 20
    assert counts["americas"] >= 5 and counts["mena"] >= 5 and counts["general"] >= 1
    with_audio = [c for c in P.COURSES if c["audio"]]
    assert len(with_audio) > 30 and all(c["level"] in ("introduction", "course") for c in with_audio)
