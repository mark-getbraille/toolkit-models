"""Self-test of the leisure collections of the reference library (the owner's request of 2026-11-22):
homestead.py, outdoors.py, games_hobbies.py, sacred_texts.py, science_use.py and literature.py, with MADE-UP data only:
nothing is downloaded.

It checks that:
  - each module is registered once in more_refs.MODULES, reaches sources.py (its group, licence lines and
    not-included rows) and owns its request words, each at most 256 jobs, with keys matching its books;
  - every book has a group the library knows, a licence the toolkit may repackage, a description and a notice, and
    every old Internet Archive book is marked old_public_domain with a year before 1931, so the builder checks the
    item's own record;
  - every web guide's page pattern matches its own addresses, and its licence page and line are set;
  - the safety notes say what the owner asked (life jackets, the firearm line, hand washing after poultry, septic
    tanks, never looking at the Sun) and each book of those collections carries its collection's note;
  - the sacred texts are only public-domain translations, presented with the respectful notice, the World English
    Bible's licence is checked on eBible.org's page, and the Wikipedia introductions are share-alike and keep only
    each article's opening section (tested on a made-up page);
  - the literature genres split the collection under 256 jobs each, no Internet Archive item is used twice across the
    six modules, nothing is repeated from the read-aloud fairy tales, and the gathering index is made from the
    module's own lists (made-up check, no download);
  - every NOT_INCLUDED row says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_leisure_books.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import games_hobbies  # noqa: E402
import homestead  # noqa: E402
import literature  # noqa: E402
import outdoors  # noqa: E402
import read_aloud  # noqa: E402
import sacred_texts  # noqa: E402
import science_use  # noqa: E402

MODULES = {homestead: ["homestead"], outdoors: ["outdoors"], games_hobbies: ["games-hobbies"],
           sacred_texts: ["sacred-texts"], science_use: ["science-use"],
           literature: ["literature"] + [w for w, _s, _r in literature.GENRES]}


def books(m):
    """Every guide and PDF entry of a module."""
    return list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())


def test_registered_and_wired():
    loaded = more_refs.modules()
    for m, words in MODULES.items():
        assert m in loaded and more_refs.MODULES.count(m.__name__) == 1, m.__name__
        assert set(m.GROUPS) <= set(sources.GROUPS), m.__name__
        assert set(m.LICENCE_LINES) <= set(sources.LICENCE_LINES), m.__name__
        for row in m.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], (m.__name__, row[0])
        for word in words:
            keys = sources.expand_keys([word])
            assert keys == m.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
            assert all(m.COLLECTION.owns(k) for k in keys), word
        everything = sources.expand_keys([words[0]])
        names = {f"{m.COLLECTION.prefix}:{b['name']}" for b in books(m)}
        assert names <= set(everything), m.__name__
    prefixes = [m.COLLECTION.prefix for m in MODULES]
    assert len(prefixes) == len(set(prefixes))
    assert sources.GROUPS["sacred"] == "Reference, sacred and philosophical texts"
    assert sources.GROUPS["literature"] == "Reference, literature and culture"
    assert sources.ALLOWED.get(homestead.EPA_TERMS) == "non-commercial"


def test_every_book_has_an_allowed_licence():
    for m in MODULES:
        for g in books(m):
            assert g["group"] in sources.GROUPS and g["group"] in m.GROUPS, g["name"]
            short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
            assert B.licence_kind(short, bool(g.get("unchanged"))), (g["name"], short)
            assert g["description"] and g["notice"] and g["title"] and g["subject"], g["name"]
            if g.get("archive"):
                assert g.get("old_public_domain") or g.get("distribution_a"), g["name"]
                assert int(g["published"][:4]) < 1931 and g["archive"] in g["version"], g["name"]
                assert g["licence"] == "Public domain (published before 1931)", g["name"]
            elif g["name"] in m.COLLECTION.guides:
                assert g["licence_page"] and g["licence_text"], g["name"]
                pattern = re.compile(g["pages"])
                for url in g.get("urls", []):
                    assert pattern.match(url if isinstance(url, str) else url[0]), (g["name"], url)
                if not g.get("sitemap"):
                    starts = [s for s, _d in g.get("crawl", [])]
                    assert starts or g.get("urls"), g["name"]
            else:
                assert g.get("pdf") and g.get("page"), g["name"]


def test_no_internet_archive_item_twice():
    items = [g["archive"] for m in MODULES for g in books(m) if g.get("archive")]
    assert len(items) == len(set(items)), [i for i in items if items.count(i) > 1]
    told = {i for i, _t, _y in read_aloud.OLD_BOOKS}
    assert not told & set(items)


def test_safety_notes():
    assert "life jacket" in outdoors.SAFETY and outdoors.GUN_LINE in outdoors.SAFETY and "blaze orange" in \
        outdoors.SAFETY
    assert outdoors.GUN_LINE == "Treat every gun as loaded, and keep your fingers away from the trigger."
    for words in ("Wash your hands", "Salmonella", "septic tank", "qualified electrician", "bee stings"):
        assert words in homestead.SAFETY, words
    for m, note in ((homestead, homestead.SAFETY), (outdoors, outdoors.SAFETY)):
        for g in books(m):
            assert note in g["notice"], g["name"]
    sky = science_use.COLLECTION.guides["nasa_skywatching"]
    assert "Never look at the Sun" in sky["notice"] and "not subject to copyright" in sky["licence_text"]
    assert "drop, cover and hold on" in science_use.QUAKE_SAFETY


def test_sacred_texts():
    for g in books(sacred_texts):
        assert sacred_texts.RESPECT in g["notice"] or g["licence"].startswith("CC BY-SA"), g["name"]
        assert g["subject"].startswith(("Sacred texts:", "Philosophy:")) or "introductions" in g["subject"]
    traditions = {g["subject"] for g in sacred_texts.PDFS}
    for words in ("Christianity", "Judaism", "Islam", "Hinduism", "Buddhism", "Taoism", "Confucianism", "Sikhism",
                  "Latter Day Saint", "Bahá'í", "Philosophy"):
        assert any(words in t for t in traditions), words
    web = sacred_texts.COLLECTION.pdfs["world_english_bible"]
    assert web["licence"] in sources.ALLOWED and web["licence_page"].startswith("https://ebible.org/")
    assert re.search(web["licence_text"], "The World English Bible is a Public Domain translation of the Holy Bible")
    names = " ".join(r[0] for r in sacred_texts.NOT_INCLUDED)
    assert "Yusuf Ali" in names and "NIV" in names


def test_wikipedia_introductions_keep_only_the_opening():
    g = sacred_texts.COLLECTION.guides["wikipedia_introductions"]
    assert B.licence_kind(B.licence_short(g["licence"])) == "share-alike"
    page = ('<html><body><main><div class="mw-content-ltr mw-parser-output" lang="en">'
            '<div class="shortdescription">Ancient text</div><table class="infobox"><tr><td>'
            '<table class="infobox-subbox"><tr><td>x</td></tr></table></td></tr></table>'
            "<p data-mw='{\"a\":\"<b>\"}'>The Made-up Text is an old book.<sup>[1]</sup></p>"
            '<meta property="mw:PageProp/toc" /><div class="mw-heading mw-heading2"><h2>History</h2></div>'
            '<p>Long history.</p></div></main></body></html>')
    body = B.article_content(page, g)
    words = " ".join(re.sub(r"<[^>]+>", " ", body).split())
    assert words == "The Made-up Text is an old book.", words
    for url in sacred_texts.INTRO_URLS:
        assert re.match(g["pages"], url), url
    assert D.unit_of(sacred_texts.WIKI + "Quran", g["unit_rules"]) == "Islam"


def test_literature_index_and_genres():
    keys = sources.expand_keys(["literature"])
    assert keys[0] == "lit:index" and len(keys) == len(literature.PDFS) + 1 <= 256
    by_genre = [k for w, _s, _r in literature.GENRES for k in sources.expand_keys([w])]
    assert sorted(by_genre) == sorted(keys[1:])
    book = literature.index_book("index", "/nonexistent")
    assert len(book.pages) == len(literature.GENRES) + 1 and book.licence == "CC0 1.0"
    assert "lit:fitzgerald_great_gatsby" in book.pages[0].body and "Kiwix" in book.pages[-1].body
    for _w, _s, rows in literature.GENRES:
        for row in rows:
            assert row[4] < 1931 and len(row) == 7, row[0]


def test_tests_cover_old_books_helper():
    from old_ia_books import old_book
    entry = old_book("literature", "made_up", "A Made-up Book (1920)", "Literature", "Made-up Press", "madeup00", 1920,
                     "A made-up book.", note="Published in {year}.", notice="Be kind.")
    assert entry["old_public_domain"] and entry["published"] == "1920" and "madeup00" in entry["version"]
    assert entry["description"].endswith("Published in 1920.") and entry["notice"].endswith("Be kind.")
