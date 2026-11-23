"""Self-test of the government language books (languages_gov.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once, in the top-level group "Languages"; that each request word (lgov-fsi,
lgov-dli, lgov-dli-countries, lgov-military, lgov-other-gov, languages-gov) stands for at most 256 keys without
repeats; that no FSI course repeats one of languages.py and no Internet Archive item is used twice in the library;
that the DLI courses and War Department books are judged by the military release rule; that a course's audio is
listed (only its own folder) and never downloaded; that made-up survival kit pages (the older HTML kind and the newer
XML kind) become phrase tables, with mines and explosives parts and sign-in guides left out; that made-up TERMIUM Plus
rows are read, sorted and paged; and that every NOT_INCLUDED row says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_languages_gov.py
"""

import io
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import languages as L  # noqa: E402
import languages_gov as G  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402

WORDS = ("lgov-fsi", "lgov-dli", "lgov-dli-countries", "lgov-military", "lgov-other-gov", "languages-gov")


def test_registered_in_the_languages_section():
    assert more_refs.MODULES.count("languages_gov") == 1 and G in more_refs.modules()
    assert G.GROUP == L.GROUP == "languages" and sources.GROUPS["languages"] == "Languages"
    assert [m for m in more_refs.modules() if m.COLLECTION.prefix == "lgov"] == [G]
    for word in WORDS:
        keys = sources.expand_keys([word])
        assert keys and len(keys) == len(set(keys)) <= 256, word
        assert more_refs.module_for(word) is G
    every = set(sources.expand_keys(["languages-gov"]))
    assert every == {k for w in WORDS[:-1] if w != "lgov-dli-countries" for k in sources.expand_keys([w])}
    assert set(G.COLLECTION.own_keys()) == every | set(sources.expand_keys(["lgov-dli-countries"]))
    assert set(G.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for row in G.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]


def test_every_book_is_in_the_languages_group():
    for e in G.CIP_PDFS + G.MILITARY_PDFS + G.OTHER_US_PDFS:
        assert e["group"] == "languages" and e["licence"] == sources.US_GOV, e["name"]
    for c in G.FSI_COURSES:
        assert G.course_entry("fsi", c)["group"] == "languages" and not G.course_entry("fsi", c).get("military")
    for c in G.DLI_COURSES:
        entry = G.course_entry("dli", c)
        assert entry["military"] and entry["name"] == f"lgov_dli_{c['key']}", c["key"]
    assert all(e.get("military") for e in G.MILITARY_PDFS)


def test_no_course_or_item_twice():
    have = {c["text"][0][1] for c in L.COURSES}
    # an item may give two courses with different files (the Hungarian course and reader, the Thai course and grammar)
    parts = [(where, p) for c in G.FSI_COURSES + G.DLI_COURSES for kind, where, p in c["text"] if kind == "ia"]
    assert len(parts) == len(set(parts))
    items = list(dict.fromkeys(w for w, _p in parts)) + [e["archive"] for e in G.MILITARY_PDFS + G.OTHER_US_PDFS]
    assert len(items) == len(set(items)) and not have & set(items)
    others = {e.get("archive") for e in sources.PDF_DOCS} | {
        p.get("archive") for m in more_refs.modules() if m is not G for p in m.COLLECTION.pdfs.values()}
    assert not set(items) & others
    assert not {c["key"] for c in G.FSI_COURSES} & {c["key"] for c in L.COURSES}
    for language in ("Amharic", "Hausa", "Swahili", "Thai", "Turkish", "Twi", "Yoruba", "Persian", "Hindi", "Swedish",
                     "Serbo-Croatian", "Shona", "Lingala", "Kirundi", "Lao", "Hungarian", "Bulgarian", "Polish"):
        assert any(c["language"].startswith(language) for c in G.FSI_COURSES), language


def test_audio_listed_only_its_folder_and_never_downloaded(monkeypatch):
    links = [f"{G.YOJIK}/Lao/Basic/Volume%201/Unit%2001.mp3", f"{G.YOJIK}/Lao/Reading%20Lao/Lesson%2001.mp3"]
    monkeypatch.setattr(L, "page_links", lambda page, pattern, cache=None: links)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no download")))
    got = G.course_audio(G.FSI_COURSE["lao"], sizes=False)
    assert got == [{"url": links[0], "kind": "mp3", "size": 0}]


def test_survival_kit_html_and_xml():
    index = ('<a href="module1.html" class="css_link" title="GREETINGS &amp; INTRODUCTIONS">x</a>'
             '<a href="module2.html" class="css_link" title="MINE WARFARE TERMS">y</a>')
    assert G.lsk_index_modules(index) == [("module1.html", "GREETINGS & INTRODUCTIONS"),
                                          ("module2.html", "MINE WARFARE TERMS")]
    module = ('<tr><td class="css_cnt">Hello</td><td class="css_cnt">salaam</td><td dir="rtl" class="css_cnt">'
              '&#1587;&#1604;&#1575;&#1605;</td></tr><tr><td colspan="7">line</td></tr>')
    assert G.lsk_module_rows(module) == [("Hello", "salaam", "سلام")]
    cat = "﻿<dataroot><dbo_catID><categoryID>2</categoryID><categoryDesc>HELP</categoryDesc></dbo_catID>" \
          "<dbo_catID><categoryID>1</categoryID><categoryDesc>STOP &amp; GO</categoryDesc></dbo_catID></dataroot>"
    kit = "<dataroot>" + "".join(
        f"<dbo_langKit><catID>{c}</catID><phraseOrder>{o}</phraseOrder><englishPhrase>{e}</englishPhrase>"
        f"<romanized>{r} </romanized><unicode>{u}</unicode></dbo_langKit>"
        for c, o, e, r, u in [("1", "2", "Go", "ee-dee", "Іди"), ("1", "1", "Stop", "stee", "Стій"),
                              ("2", "1", "Help", "do-po-mo-ha", "Допомога")]) + "</dataroot>"
    assert G.lsk_xml_modules(cat, kit) == [("STOP & GO", [("Stop", "stee", "Стій"), ("Go", "ee-dee", "Іди")]),
                                           ("HELP", [("Help", "do-po-mo-ha", "Допомога")])]
    assert G.MINE_WORDS.search("MINE WARFARE TERMS") and not G.MINE_WORDS.search("GREETINGS & INTRODUCTIONS")
    listing = ("<div onmouseover='showLSK(this, \"conLSK7\")'>Arabic-Lebanese  .  Language Survival Kits</div>"
               "<div id='conLSK7' class='lsk'><div><a href='counter.aspx?i=12&t=language' target='_blank'>Basic "
               "Language Guide</a></div><div><a href='counter.aspx?i=13&t=language' target='_blank'>Weapons "
               "Language Guide</a></div></div>")
    assert G.lsk_guides(listing, "Arabic-Lebanese") == [("12", "Basic Language Guide"), ("13", "Weapons Language Guide")]
    assert G.lsk_guides(listing, "Uzbek") == []
    assert len(G.LSK_LANGUAGES) == len(G.LSK) == 89


def test_survival_kit_book_leaves_out_sign_in_and_mines(monkeypatch):
    pages = {
        G.DLIFLC_TERMS: "Information presented on this site is considered public information and may be distributed "
                        "or copied unless otherwise specified.",
        G.LSK_LIST: "<div onmouseover='showLSK(this, \"conLSK1\")'>Dari Language Survival Kits</div><div id='conLSK1' "
                    "class='lsk'><div><a href='counter.aspx?i=4&t=language' target='_blank'>Basic Language Guide</a>"
                    "</div><div><a href='counter.aspx?i=5&t=language' target='_blank'>Medical Language Guide</a></div>"
                    "</div></div>",
        f"{G.FIELD}/products/dari/pg_bc_LSK/": '<a href="module1.html" class="css_link" title="GREETINGS">g</a>'
                                               '<a href="module2.html" class="css_link" title="MINE TERMS">m</a>',
        f"{G.FIELD}/products/dari/pg_bc_LSK/module1.html": '<tr><td class="css_cnt">Hello</td><td class="css_cnt">'
                                                           'salaam</td><td class="css_cnt">x</td></tr>',
        f"{G.FIELD}/products/dari/pg_bc_LSK/module2.html": '<tr><td class="css_cnt">Mine</td><td class="css_cnt">'
                                                           'mayn</td><td class="css_cnt">y</td></tr>'}

    def fetch(url, cache=None, **k):
        """Made-up pages; the XML files are missing (the older kind of kit)."""
        if url in pages:
            return pages[url]
        raise G.urllib.error.HTTPError(url, 404, "Not Found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(G, "guide_address", lambda n: {"4": f"{G.FIELD}/products/dari/pg_bc_LSK",
                                                       "5": f"{G.FIELD}/products/secure/dari/pg_md_LSK"}[n])
    left = []
    book = G.lsk_book("lsk:dari", "/nonexistent", None, left)
    assert [p.title for p in book.pages] == ["Basic Language Guide: Greetings"]
    assert "salaam" in book.pages[0].body and "Mine" not in book.pages[0].body
    reasons = " ".join(x["reason"] for x in left)
    assert "sign-in" in reasons and "mines or explosives" in reasons
    assert book.group == "languages" and "17 U.S.C. 105" in book.notice and "Copyright DLIFLC" in book.notice


def test_termium_rows_sorted_and_paged():
    text = ("﻿SUBJECT_EN,TERM_EN,TERME_FR,TERME_TERM_ES,TERME_TERM_PT\n"
            "Agriculture,zucchini,courgette,calabacín,abobrinha\n"
            "Agriculture,Apple,pomme,manzana,\n"
            "Agriculture,orphan,,huérfano,\n"
            "Agriculture,Apple,pomme,manzana,\n")
    rows = G.termium_sorted(G.termium_rows(text))
    assert rows == [("Apple", "pomme", "manzana", "", "Agriculture"),
                    ("zucchini", "courgette", "calabacín", "abobrinha", "Agriculture")]
    pages = G.termium_pages("Agriculture", rows)
    assert len(pages) == 1 and pages[0][1] == "Apple to zucchini" and 'lang="fr">courgette' in pages[0][2]
    assert len(G.TERMIUM_SUBJECTS) == len(G.TERMIUM) == 23
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Agriculture_B.csv", text)
    assert zipfile.ZipFile(io.BytesIO(buf.getvalue())).namelist() == ["Agriculture_B.csv"]
    assert B.licence_kind("OGL-Canada") == "open"


def test_countries_in_perspective_entries():
    assert len(G.CIP_PDFS) == len(G.CIP_COUNTRIES) == 83
    for e in G.CIP_PDFS:
        assert e["page"].startswith(f"{G.FIELD}/products/cip/") and e["licence_page"] == G.DLIFLC_TERMS
        assert not e.get("military") and e["name"].startswith("cip_")
