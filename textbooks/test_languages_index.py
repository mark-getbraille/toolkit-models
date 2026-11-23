"""Self-test of the Languages section's guide (languages_index.py) and of Languages as a top-level section (the
owner's request of 23 November 2026), with MADE-UP data only: nothing is downloaded.

It checks that the group "languages" is titled "Languages" and every language module files its books there; that
lang:index is registered under its request word languages-index and is routed to this module although languages.py
shares the "lang:" prefix; that the index lists every book of languages.py, languages_gov.py and languages_open.py,
once, with lopen:index and lopen:braille_index and the request words of the collections still being added
(peace-corps-languages, lang-open); that every key, pack and manual collection it names exists; that its pages are one
per language, A to Z; that the Internet Archive's foreign-language topic moved into the section; and that the library
guide names the section's guide.

Run it from the repository's folder:   python3 -m pytest textbooks/test_languages_index.py
"""

import collections
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import languages as L  # noqa: E402
import languages_gov as G  # noqa: E402
import languages_index as I  # noqa: E402
import languages_open as O  # noqa: E402
import library_guide  # noqa: E402
import more_refs  # noqa: E402
import open_catalogues as OC  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def entries(kind):
    """Every (what, words) the index lists of one kind."""
    return [(what, words) for _p, _i, rows in I.SECTIONS for k, what, words, *_r in rows if k == kind]


def test_top_level_section_and_registration():
    assert sources.GROUPS["languages"] == "Languages"
    assert L.GROUP == G.GROUP == O.GROUP == I.GROUP == "languages"
    assert more_refs.MODULES.count("languages_index") == 1 and I in more_refs.modules()
    assert sources.expand_keys(["languages-index"]) == ["lang:index"]
    assert more_refs.module_for("lang:index") is I and more_refs.module_for("languages-index") is I
    assert more_refs.module_for("lang:fsi:japanese") is L and more_refs.module_for("lang:wikivoyage_phrasebooks") is L
    assert set(I.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert OC.IA_TOPICS["languages"][1] == "languages" and OC.IA_TOPICS["english"][1] == "reference"
    assert ("lang:index", "Languages", "languages-index") in library_guide.SECTION_GUIDES


def test_index_lists_every_language_book_once():
    keys = [k for k, _w in entries("key")]
    assert len(keys) == len(set(keys)), [k for k, c in collections.Counter(keys).items() if c > 1]
    every = set(L.COLLECTION.own_keys()) | set(G.COLLECTION.own_keys()) | set(O.COLLECTION.own_keys())
    assert every - {"lopen:index"} - {"lopen:braille_index"} <= set(keys) | {"lopen:index"}
    assert {"lopen:index", "lopen:braille_index"} <= set(keys)
    assert set(keys) <= every
    words = [w for w, _t in entries("word")]
    assert I.PEACE_CORPS_WORD == "peace-corps-languages" and {"peace-corps-languages", "lang-open"} <= set(words)
    for key in keys:
        assert X.key_exists(key), key


def test_one_page_per_language_a_to_z():
    titles = [t for t, _i, _e in I.SECTIONS]
    languages = titles[:len(I.language_sections())]
    assert languages == sorted(languages, key=str.lower) and len(languages) == len(set(languages))
    for language in ("Spanish", "Amharic", "Twi", "Navajo", "Latin", "Esperanto", "Dari", "Chinese", "Tok Pisin"):
        assert language in languages, language
    assert titles[-5:] == ["Many languages", "Sign languages", "Braille in other languages",
                           "Terminology: English and French", "Countries and cultures"]
    assert I.base_language("Chinese (Mandarin)") == "Chinese" and I.base_language("Language learning: Latin") == "Latin"
    assert not [t for t, _i, rows in I.SECTIONS if not rows], "a part with nothing in it"


def listed_names(folder, code):
    """The names a small program prints in another folder of the repository (its modules share names with this
    folder's, so they are read in their own process)."""
    out = subprocess.run([sys.executable, "-c", code], cwd=os.path.join(HERE, "..", folder), capture_output=True,
                         text=True, check=True, timeout=300).stdout
    return set(out.split())


def test_packs_and_manuals_exist():
    packs = listed_names("packs", "import build_packs; print(' '.join(build_packs.PACKS))")
    manuals = listed_names("manuals", "import categories; print(' '.join(categories.CATEGORIES))")
    assert {p for p, _w in entries("pack")} <= packs
    assert {m for m, _w in entries("manuals")} <= manuals
