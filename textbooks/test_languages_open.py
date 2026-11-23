"""Self-test of the open language resources (languages_open.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once (more_refs.MODULES) and that every request word reaches sources.py with
at most 256 jobs and no key twice; that nothing repeats what the library already has (Internet Archive items of
other modules, languages.py's Tatoeba languages, the African Storybook's languages); that licences are kept apart
(CC BY stories in the main reader, CC BY-NC stories in a personal-use book; GNU GPL dictionaries share-alike;
non-commercial and Wiktionary-made dictionaries refused; old books checked for a year before 1931); that World Braille
Usage is link-only; and that each reader (grammar sites, WordPress courses, Global Storybooks, FreeDict's TEI) turns
made-up pages into the right book pages.

Run it from the repository's folder:   python3 -m pytest textbooks/test_languages_open.py
"""

import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import languages as L  # noqa: E402
import languages_open as O  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402

WORDS = ["lopen-textbooks", "lopen-readers", "lopen-dictionaries", "lopen-classical", "lopen-sign", "lopen-braille"]


def test_registered_words_and_sizes():
    assert more_refs.MODULES.count("languages_open") == 1 and O in more_refs.modules()
    assert O.GROUP == "languages" and O.GROUPS == {}          # languages.py's group; no new group here
    everything = sources.expand_keys(["lang-open"])
    assert len(everything) == len(set(everything)) <= 256
    for word in WORDS:
        keys = sources.expand_keys([word])
        assert keys == O.COLLECTION.expand_keys([word]), word
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        assert set(keys) <= set(everything), word
        assert all(k.startswith("lopen:") for k in keys), word
    assert "lopen:index" in everything and "lopen:braille_index" in sources.expand_keys(["lopen-braille"])
    assert set(O.COLLECTION.own_keys()) == set(everything)
    assert set(O.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in O.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_no_duplicates_with_the_library():
    mine = {p["archive"] for p in O.PDFS}
    assert len(mine) == len(O.PDFS)
    others = {e.get("archive") for e in sources.PDF_DOCS}
    for m in more_refs.modules():
        if m is not O:
            others |= {e.get("archive") for e in m.COLLECTION.pdfs.values()}
    assert not mine & others
    assert not set(O.TATOEBA_MORE) & set(L.TATOEBA_LANGUAGES)
    assert not {"fr", "pt", "sw", "so", "en", "zu", "xh"} & set(O.GSB_LANGUAGES)    # read_aloud.py's languages
    assert len(O.FREEDICT_NAMES) == len(set(O.FREEDICT_NAMES))
    names = [p["name"] for p in O.PDFS]
    assert len(names) == len(set(names))


def test_old_books_are_checked_public_domain():
    for p in O.PDFS:
        assert p["licence"] == "Public domain (published before 1931)" and p["old_public_domain"], p["name"]
        assert int(p["published"]) < 1931 and p["group"] == "languages", p["name"]
        assert B.licence_kind(p["licence"]) == "open"
    for p in O.SIGN:
        assert "historical" in p["description"] or "historical" in p["subject"], p["name"]
    for p in O.BRAILLE:
        assert "NOT the current ones" in p["description"], p["name"]


def test_world_braille_usage_is_link_only():
    assert not any("gpo38772" in json.dumps(p) for p in O.PDFS)
    row = next(r for r in O.NOT_INCLUDED if r[0].startswith("World Braille Usage"))
    assert "UNESCO" in row[1] and "link-only" in row[1]
    links = [e for part in O.BRAILLE_SECTIONS for e in part[2] if e[0] == "link"]
    assert any("gpo38772" in e[2] and "UNESCO" in e[3] for e in links)


def test_freedict_licences_from_made_up_headers():
    gpl = ('<teiHeader><availability status="free"><p>Available under the terms of the <ref target='
           '"https://www.gnu.org/licenses/gpl-2.0.html">GNU General Public License ver. 2.0 and any later version</ref>'
           '.</p></availability></teiHeader>')
    assert O.tei_licence(gpl)[0] == O.GPL2 and B.licence_kind(O.GPL2) == "share-alike"
    only2 = '<availability><p><ref target="https://www.gnu.org/licenses/gpl.html">GNU GENERAL PUBLIC LICENSE, version 2.0'
    assert O.tei_licence(only2 + "</ref></p></availability>")[0] == O.GPL2_ONLY
    cc_by = "<availability><p>Available under the terms of the Creative Commons Attribution 3.0 Unported License.</p>" \
            "</availability>"
    assert O.tei_licence(cc_by)[0] == "CC BY 3.0"
    nc = '<availability><p><ref target="https://creativecommons.org/licenses/by-nc/3.0/">x</ref></p></availability>'
    assert O.tei_licence(nc)[0] == ""
    wik = '<availability><p><ref target="https://creativecommons.org/licenses/by-sa/3.0/">x</ref></p></availability>' \
          '<sourceDesc>Made from Wiktionary</sourceDesc>'
    assert O.tei_licence(wik) == ("", "Made from Wiktionary, which is already in the Kiwix library.")
    assert O.tei_licence("<availability><p>All rights reserved.</p></availability>")[0] == ""


def test_tei_entries_and_dictionary_pages(monkeypatch):
    tei = ('<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>'
           '<entry><form><orth>canis</orth><pron>ˈka.nis</pron></form><gramGrp><pos>n</pos></gramGrp>'
           '<sense><cit type="trans"><quote>dog</quote></cit><cit type="trans"><quote>hound</quote></cit></sense></entry>'
           '<entry><form><orth>aqua</orth></form><sense><cit type="trans"><quote>water</quote></cit></sense></entry>'
           '<entry><form><orth>Bellum</orth></form><sense><def>war</def></sense></entry>'
           '</body></text></TEI>').encode()
    entries = O.tei_entries(io.BytesIO(tei))
    assert entries[0] == ("canis", "[ˈka.nis] (n)", "dog; hound")
    monkeypatch.setattr(O, "ENTRIES_PER_PAGE", 2)
    pages = O.dictionary_pages(entries)
    assert [p[1] for p in pages] == ["aqua to Bellum", "canis to canis"]
    assert "<dt>canis [ˈka.nis] (n)</dt><dd>dog; hound</dd>" in pages[1][2]


README = ("Story # | Story title | View | License\n-------- | --- | --- | ---\n"
          "0001 | Un hombre muy alto | <a href=\"x\">Slideshow</a> · [Plain HTML](https://global-asp.github.io/stories/"
          "es/0001_un-hombre-muy-alto.html) | [CC-BY](https://creativecommons.org/licenses/by/3.0/)\n"
          "0002 | Mira a los animales | · [Plain HTML](https://global-asp.github.io/stories/es/0002_mira-a-los-animales"
          ".html) | [CC-BY-NC](http://creativecommons.org/licenses/by-nc/3.0/)\n"
          "0004 | La Cabra | · [Plain HTML](https://global-asp.github.io/stories/es/0004_la-cabra.html) | "
          "[CC-BY](https://creativecommons.org/licenses/by/4.0/)\n")
EN_README = ("Story ID | Title | License\n-------- | ----- | -------\n"
             "0001 | [A very tall man](http://a) | [CC-BY](https://creativecommons.org/licenses/by/3.0/)\n"
             "0004 | [Goat, Dog, and Cow](http://b) | [CC-BY](https://creativecommons.org/licenses/by/3.0/)\n")
STORIES = {
    "es/0001_un-hombre-muy-alto.md": "# Un hombre muy alto\n\n##\nSu azadón era corto.\n\n##\nSu cama era corta.\n\n"
                                     "##\n* License: [CC-BY]\n* Text: A. Writer\n* Translation: B. Translator\n",
    "es/0002_mira-a-los-animales.md": "# Mira a los animales\n\n##\nMira.\n\n##\n* License: [CC-BY-NC]\n",
    "es/0004_la-cabra.md": "# La Cabra\n\n##\nUno.\n\n##\nDos.\n\n##\nTres.\n\n##\n* License: [CC-BY]\n",
    "en/0001_a-very-tall-man.md": "# A very tall man\n\n##\nHis hoe was short.\n\n##\nHis bed was short.\n\n"
                                  "##\n* License: [CC-BY]\n",
    "en/0004_goat-dog-and-cow.md": "# Goat, Dog, and Cow\n\n##\nOne.\n\n##\n* License: [CC-BY]\n",
}


def fake_storybooks(url, cache=None, **kw):
    """Made-up answers for the Global Storybooks reader."""
    import urllib.error
    import urllib.parse
    if url == f"{O.GASP_RAW}/es/README.md":
        return README
    if url == f"{O.ASP_RAW}/en/README.md":
        return EN_README
    for path, text in STORIES.items():
        folder, name = path.split("/")
        base = O.ASP_RAW if folder == "en" else O.GASP_RAW
        if urllib.parse.unquote(url) == f"{base}/{folder}/{name}":
            return text
    raise urllib.error.HTTPError(url, 404, "not found", {}, None)


def test_storybook_rows_and_sections():
    rows = O.gsb_rows(README)
    assert [(r[0], r[2], r[3]) for r in rows] == [("0001", "0001_un-hombre-muy-alto", "CC BY 3.0"),
                                                  ("0002", "0002_mira-a-los-animales", "CC BY-NC 3.0"),
                                                  ("0004", "0004_la-cabra", "CC BY 4.0")]
    assert O.english_rows(EN_README) == {"0001": "0001_a-very-tall-man", "0004": "0004_goat-dog-and-cow"}
    assert O.story_slug("Goat, Dog, and Cow") == "goat-dog-and-cow"
    title, pages, meta = O.story_sections(STORIES["es/0001_un-hombre-muy-alto.md"])
    assert title == "Un hombre muy alto" and pages == ["Su azadón era corto.", "Su cama era corta."]
    assert meta["license"] == "CC-BY" and meta["translation"] == "B. Translator"


def test_storybook_licences_kept_apart(monkeypatch):
    monkeypatch.setattr(B, "fetch", fake_storybooks)
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    open_book = O.gsb_book("gsb:es", "work", None, [], None)
    assert [p.path for p in open_book.pages] == ["story-0001", "story-0004"]
    assert not open_book.personal_use and open_book.licence == "CC BY 3.0 and 4.0"
    assert B.licence_kind(open_book.licence) == "open"
    first = open_book.pages[0].body
    assert '<td lang="es">Su azadón era corto.</td><td lang="en">His hoe was short.</td>' in first
    assert "In English: Goat, Dog, and Cow" in open_book.pages[1].body      # page counts differ: one after the other
    nc_book = O.gsb_book("gsbnc:es", "work", None, [], None)
    assert [p.path for p in nc_book.pages] == ["story-0002"] and nc_book.personal_use
    assert B.licence_kind(nc_book.licence) == "non-commercial" and "personal use only" in nc_book.title
    left = []
    assert O.gsb_book("gsb:xx", "work", None, left, None) is None and left


def test_grammar_site_reader():
    spec = O.GRAMMARS["tex_french"]
    index = '<a href="adj1.html">a</a><a href="help.html">h</a><a href="index.html">i</a><a href="noun2.html">n</a>'
    import urllib.parse
    links = []
    orig = B.fetch
    try:
        B.fetch = lambda url, cache=None, **kw: index
        links = O.grammar_links(spec)
    finally:
        B.fetch = orig
    assert links == [urllib.parse.urljoin(spec["index"], "adj1.html"), urllib.parse.urljoin(spec["index"],
                                                                                            "noun2.html")]
    page = ("<html><title>adj1: introduction to adjectives</title><body><div>menu</div><!-- content -->"
            "<p>An adjective describes a noun.</p><!-- note --><!-- END content --><div>footer</div></body></html>")
    title, body = O.grammar_page(spec, links[0], page)
    assert title == "introduction to adjectives"
    assert "An adjective describes a noun." in body and "menu" not in body and "footer" not in body
    grimm = O.GRAMMARS["grimm_german"]
    assert O.grammar_links.__doc__ and grimm["print_view"] == "../pr/"


def test_wordpress_course_reader(monkeypatch):
    spec = O.WP_COURSES["kiche"]
    catalogue = "<p>Chqeta'maj</p><p>Language: K’iche’ Format: Language Curriculum License: CC-BY</p>"
    pages = [{"id": 1, "slug": "the-language", "link": f"{spec['site']}/the-language/", "modified": "2025-01-02",
              "title": {"rendered": "The language"}, "content": {"rendered": "<p>K'iche' is a Mayan language.</p>"}}]
    posts = [{"id": 3, "slug": "u2", "link": f"{spec['site']}/u2/", "modified": "2025-03-01",
              "title": {"rendered": "Tïjonïk 2 (Unit 2) Family"}, "content": {"rendered": "<p>Family words.</p>"}},
             {"id": 4, "slug": "u1", "link": f"{spec['site']}/u1/", "modified": "2025-02-01",
              "title": {"rendered": "Tïjonïk 1 (Unit 1) Sounds"}, "content": {"rendered": "<p>The sounds.</p>"}},
             {"id": 5, "slug": "u1es", "link": f"{spec['site']}/es/u1/", "modified": "2025-02-01",
              "title": {"rendered": "Tïjonïk 1 (Unidad 1)"}, "content": {"rendered": "<p>Los sonidos.</p>"}}]

    def fake(url, cache=None, **kw):
        if url == spec["licence_page"]:
            return catalogue
        if "/wp/v2/pages" in url:
            return json.dumps(pages if "page=1&" in url else [])
        if "/wp/v2/posts" in url:
            return json.dumps(posts if "page=1&" in url else [])
        raise AssertionError(url)
    monkeypatch.setattr(B, "fetch", fake)
    monkeypatch.setattr(K, "readable", lambda url, cache=None: True)
    book = O.wp_course_book("wpcourse:kiche", "work", None, [], None)
    assert [p.title for p in book.pages] == ["The language", "Tïjonïk 1 (Unit 1) Sounds", "Tïjonïk 2 (Unit 2) Family"]
    assert book.licence == "CC BY 4.0" and book.published == "2025-03-01"
    left = []
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, **kw: "License: CC-BY-NC" if url == spec["licence_page"]
                        else fake(url))
    assert O.wp_course_book("wpcourse:kiche", "work", None, left, None) is None and "licence" in left[0]["reason"]


def test_index_books_offline(monkeypatch):
    import practical_index as X
    monkeypatch.setattr(X, "key_exists", lambda key: True)
    for maker, name in ((O.INDEX, "lopen_index"), (O.BRAILLE_INDEX, "lopen_braille_index")):
        book = maker[0]("index", "work", None, [], None)
        assert book.name == name and book.licence == "CC0 1.0" and book.pages
    braille = O.BRAILLE_INDEX[0]("braille_index", "work", None, [], None)
    text = " ".join(p.body for p in braille.pages)
    assert "World Braille Usage" in text and "UNESCO" in text and "liblouis" in text
