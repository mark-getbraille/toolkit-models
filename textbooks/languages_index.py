"""The guide to the "Languages" section of the reference library: one index book, lang:index, in the group
"Languages" (group key "languages"), the owner's request of 23 November 2026: "Make a new top level section for
languages". Keys: lang:index; request word languages-index (the index alone: the books it lists are asked for by their
own request words, languages, languages-gov, lang-open and the others, which together are far more than 256 keys).

What this module builds, in plain words:
  - lang:index, the toolkit's own facts and links (CC0, nothing downloaded): one page per LANGUAGE, A to Z, listing
    every book the library has for learning it, by key, made from the language modules themselves, so a book added
    there is listed here too:
      languages.py (FSI and Peace Corps courses, Tatoeba sentences),
      languages_gov.py (the other FSI courses, DLI courses, Language Survival Kits, War Department guides and
        dictionaries, Native American dictionaries and grammars),
      languages_open.py (COERLL grammars and courses, Global Storybooks readers, FreeDict dictionaries, more Tatoeba
        sentences, old Latin, Greek, Hebrew, Sanskrit, Old English and Esperanto books);
    then pages for what is not one language: phrasebooks for many languages, sign languages, braille in other
    languages, terminology (Canada's TERMIUM Plus), countries and cultures (DLI's Countries in Perspective), the
    translator devices' manuals, and the collections still being added, named by their request words
    (peace-corps-languages: every Peace Corps language course, from another helper's branch, not merged yet; and
    lang-open, with lopen:index and lopen:braille_index, the open resources' own guides).

The key prefix "lang:" is shared with languages.py: more_refs.module_for gives "lang:index" to this module (the
only one whose own keys hold it). The index's left_out names any listed key the library no longer has
(practical_index.index_maker).

Run from the repository's folder:
  python3 textbooks/languages_index.py lang:index --out build/textbooks
  python3 textbooks/languages_index.py --list languages-index
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import languages as L  # noqa: E402
import languages_gov as G  # noqa: E402
import languages_open as O  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = L.GROUP                      # "languages": the top-level section "Languages" (named in languages.py's GROUPS)
GROUPS = {}

# The Peace Corps language courses' request word (the peace-corps-lang branch; named here until it is merged).
PEACE_CORPS_WORD = "peace-corps-languages"
OPEN_WORD = "lang-open"


def base_language(name):
    """The language a book is filed under: the name before any bracket or "(historical)" ("Chinese (Mandarin)" ->
    "Chinese", "Language learning: Latin" -> "Latin")."""
    name = re.sub(r"^Language learning:\s*", "", name).strip()
    return name.split(" (")[0].strip()


def language_books():
    """{language: [("key", key, title)]} of every one-language book of the three language modules."""
    out = {}

    def add(language, key, title):
        """File one book under its language."""
        out.setdefault(base_language(language), []).append(("key", key, title))

    for c in L.COURSES:
        add(c["language"], f"lang:fsi:{c['key']}", f"{c['title']} ({c['language']})")
    for code, language in L.TATOEBA_LANGUAGES.items():
        add(language, f"lang:tatoeba:{code}", f"{language} sentences with English translations (Tatoeba)")
    for c in G.FSI_COURSES + G.DLI_COURSES:
        base = "fsi" if c in G.FSI_COURSES else "dli"
        add(c["language"], f"lgov:{base}:{c['key']}", f"{c['title']} ({c['language']})")
    for key, _label, language in G.LSK_LANGUAGES:
        add(language, f"lgov:lsk:{key}", f"Language Survival Kits: {language} (Defense Language Institute)")
    for e in G.MILITARY_PDFS + G.OTHER_US_PDFS:
        add(e["language_name"], f"lgov:{e['name']}", e["title"])
    for key, spec in list(O.GRAMMARS.items()) + list(O.WP_COURSES.items()):
        base = "grammar" if key in O.GRAMMARS else "wpcourse"
        add(spec["language"], f"lopen:{base}:{key}", spec["title"])
    for code, language in O.GSB_LANGUAGES.items():
        add(language, f"lopen:gsb:{code}", f"Global Storybooks: {language} stories with English")
        add(language, f"lopen:gsbnc:{code}", f"Global Storybooks: {language} stories with English (personal use only)")
    for name in O.FREEDICT_NAMES:
        a, b = name.split("-")
        other = b if a == "eng" else a
        add(O.LANG3.get(other, other), f"lopen:freedict:{name}",
            f"{O.LANG3.get(a, a)}-{O.LANG3.get(b, b)} dictionary (FreeDict)")
    for code, language in O.TATOEBA_MORE.items():
        add(language, f"lopen:tatoeba:{code}", f"{language} sentences with English translations (Tatoeba)")
    for e in O.CLASSICAL:
        add(e["subject"], f"lopen:{e['name']}", e["title"])
    return out


def language_sections():
    """One index part per language, A to Z: (part title, intro, entries)."""
    books = language_books()
    return [(language, f"Books in the library for learning {language}.", books[language])
            for language in sorted(books, key=str.lower)]


def other_sections():
    """The parts that are not one language."""
    return [
        ("Many languages", "Phrasebooks and readers in many languages at once, and the collections still being added.", [
            ("key", "lang:wikivoyage_phrasebooks", "Wikivoyage's phrasebooks for travellers (share-alike)"),
            ("word", PEACE_CORPS_WORD, "The Peace Corps's language courses (being added)"),
            ("word", OPEN_WORD, "Open language resources: university courses, readers, dictionaries, old grammars"),
            ("key", "lopen:index", "Open language resources: a guide to the library"),
            ("manuals", "travel_devices", "Translators and travel gear: manuals")]),
        ("Sign languages", "Sign languages: old books that describe each sign in words, and pictures of signing.", [
            ("key", f"lopen:{e['name']}", e["title"]) for e in O.SIGN] + [
            ("pack", "commons_sign_language", "Manual alphabets, fingerspelled letters, signs and interpreters")]),
        ("Braille in other languages", "How braille and Moon type are written for other languages.", [
            ("key", "lopen:braille_index", "Braille in other languages: the guide")] + [
            ("key", f"lopen:{e['name']}", e["title"]) for e in O.BRAILLE]),
        ("Terminology: English and French", "Canada's terminology bank, TERMIUM Plus: terms in English and French, with "
                                            "Spanish and Portuguese where given, one book per subject.", [
            ("key", f"lgov:termium:{k}", f"TERMIUM Plus: {s}") for k, s, _f in G.TERMIUM_SUBJECTS]),
        ("Countries and cultures", "The Defense Language Institute's Countries in Perspective: each country's "
                                   "geography, history, economy and society (request word lgov-dli-countries).", [
            ("key", f"lgov:{e['name']}", e["title"]) for e in G.CIP_PDFS]),
    ]


def sections():
    """Every part of the index, the languages first."""
    return language_sections() + other_sections()


SECTIONS = sections()
INDEX = X.index_maker("lang", GROUP, "Languages: a guide to the library", "Languages",
                      "A guide to the library for learning languages: one page per language, A to Z, with every course, "
                      "phrase guide, dictionary, reader and sentence book for it, then phrasebooks, sign languages, "
                      "braille in other languages, terminology and countries and cultures.", SECTIONS)

COLLECTION = K.Collection("lang", GROUP, makers={"index": INDEX}, words={"languages-index": lambda: ["lang:index"]})

LICENCE_LINES = {
    "lang_index": "The languages index (lang:index) is the toolkit's own facts and links, CC0; each book it lists has "
                  "its own licence, shown in that book.",
}
NOT_INCLUDED = []


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
