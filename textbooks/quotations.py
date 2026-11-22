"""Quotations, proverbs, idioms and phrases for the reference library, in the group "Reference, quotations and
proverbs" (the owner's request of 2026-11-22). Keys: quote:<name> and quote:wikiquote:<letter>. Request word:
quotations.

What this module builds, in plain words:
  - the classic dictionaries of quotations, proverbs, idioms and phrases that are in the US public domain (published
    before 1931), each read whole from its Internet Archive scan (old_ia_books.old_book: the builder checks the
    item's record shows a year before 1931 at every build): Bartlett's Familiar Quotations (the tenth edition, this
    printing 1919), Hoyt's New Cyclopedia of Practical Quotations (1922), Brewer's Dictionary of Phrase and Fable
    (1898) and his Reader's Handbook (1904), Benham's Book of Quotations, Proverbs and Household Words (1907), Wood's
    and Dalbiac's dictionaries of quotations, Riley's Latin and Greek quotations (1891), Bohn's Hand-Book of Proverbs
    (Ray's collection, 1855), Apperson's English Proverbs and Proverbial Phrases (1929), Inwards' Weather Lore
    (1898) and De Bekker's Desk Book of Idioms and Idiomatic Phrases (1923);
  - Wikiquote (en.wikiquote.org), the whole English site, as share-alike books (CC BY-SA 4.0), one for each first
    letter of the page titles (quote:wikiquote:a to quote:wikiquote:z, and quote:wikiquote:other for titles that
    start with a digit or another sign): every article (people, works, films, television, themes and proverbs) with
    its quotations and their sources. They are read from Wikimedia's official XML dump
    (dumps.wikimedia.org/enwikiquote, about 220 MB, downloaded once per build into the cache folder), not from the
    site page by page. Kiwix's own Wikiquote file (wikiquote_en_all) is labelled for the toolkit's Kiwix library
    (KIWIX_LABELS), but download.kiwix.org's robots.txt turns programs away, so the builder does not read it;
  - quote:index: a guide to quotations, proverbs, idioms and phrases in the library (CC0).
Old books of quotations reflect the attitudes of their time; each one's description says so.

Not built (NOT_INCLUDED): later editions of Bartlett, Hoyt and Brewer (still in copyright), the Internet Archive's
Project Gutenberg copy of Bartlett (no PDF to read; the scan is built), and books whose record gives no year.

Run from the repository's folder:
  python3 textbooks/quotations.py quote:wikiquote:q --out build/textbooks --limit 5
  python3 textbooks/quotations.py --list quotations
"""

import bz2
import datetime
import os
import re
import string
import sys
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "quotations"
GROUPS = {GROUP: "Reference, quotations and proverbs"}

OLD_NOTE = ("Published in {year}: a book of its time, whose choices, sources and wording reflect the attitudes of its "
            "day, some of them outdated or offensive now.")

# ====================================================================== the old public-domain dictionaries

PDFS = [
    old_book(GROUP, "bartlett_familiar_quotations_1919", "Familiar Quotations (John Bartlett, tenth edition, revised "
             "by Nathan Haskell Dole, 1919 printing)", "Quotations", "John Bartlett and Nathan Haskell Dole (Little, "
             "Brown and Company)", "familiarquotatio00bart_1", 1919,
             "The classic American book of quotations: passages, phrases and proverbs traced to their sources in "
             "ancient and modern literature, arranged by author from the oldest to the newest, with an index of "
             "authors and a large index of words, so a half-remembered line can be found by any word in it.",
             note=OLD_NOTE),
    old_book(GROUP, "hoyt_new_cyclopedia_quotations_1922", "Hoyt's New Cyclopedia of Practical Quotations (1922)",
             "Quotations", "Jehiel Keeler Hoyt and Kate Louise Roberts (Funk and Wagnalls Company)",
             "cu31924027665557", 1922,
             "More than 21,000 quotations from the speech and literature of all nations, arranged by subject (from "
             "Ability to Zeal), each with its author and source, with an index of authors and a concordance of the "
             "key words of every quotation; foreign quotations are given with their translations.", note=OLD_NOTE),
    old_book(GROUP, "brewer_dictionary_phrase_fable_1898", "Dictionary of Phrase and Fable (E. Cobham Brewer, 1898 "
             "edition)", "Phrases, idioms and their origins", "E. Cobham Brewer (Cassell and Company, London)",
             "dli.bengal.10689.11410", 1898,
             "Brewer's famous dictionary of the derivation, source or origin of common phrases, allusions and words "
             "that have a tale to tell: idioms and sayings, characters of myth and fiction, nicknames, customs, "
             "superstitions and proverbial expressions, from A to Z.", note=OLD_NOTE, country="United Kingdom"),
    old_book(GROUP, "brewer_readers_handbook_1904", "The Reader's Handbook of Famous Names in Fiction, Allusions, "
             "References, Proverbs, Plots, Stories and Poems (E. Cobham Brewer, 1904)", "Allusions and references",
             "E. Cobham Brewer (J. B. Lippincott Company)", "readershand00brew", 1904,
             "A dictionary of the names, allusions, proverbs, plots and stories that readers meet in literature: who "
             "a character is, where a phrase comes from and what a story is about, with the books they come from.",
             note=OLD_NOTE),
    old_book(GROUP, "benham_book_of_quotations_1907", "A Book of Quotations, Proverbs and Household Words (W. Gurney "
             "Benham, 1907)", "Quotations and proverbs", "W. Gurney Benham (J. B. Lippincott Company)",
             "cu31924027664907", 1907,
             "Quotations from English and American authors, then from Greek, Latin and modern languages with "
             "translations, proverbs, and the familiar phrases and household words of everyday speech, with a full "
             "index of words.", note=OLD_NOTE),
    old_book(GROUP, "wood_dictionary_of_quotations_1893", "Dictionary of Quotations from Ancient and Modern, English "
             "and Foreign Sources (James Wood, 1893)", "Quotations", "James Wood (Frederick Warne and Co.)",
             "dictionaryofquot00woodrich", 1893,
             "About 30,000 quotations, proverbs and phrases, English and foreign, arranged alphabetically by their "
             "first words, each with its source and, for foreign ones, a translation, with a subject index.",
             note=OLD_NOTE, country="United Kingdom"),
    old_book(GROUP, "dalbiac_dictionary_quotations_english_1908", "Dictionary of Quotations (English) (Philip Hugh "
             "Dalbiac, 1908)", "Quotations", "Philip Hugh Dalbiac (Swan Sonnenschein and Co.)",
             "dictionaryofquot00dalb", 1908,
             "Quotations from English literature arranged alphabetically by their first words, with an index of "
             "authors and an index of subjects.", note=OLD_NOTE, country="United Kingdom"),
    old_book(GROUP, "riley_latin_greek_quotations_1891", "Dictionary of Latin and Greek Quotations, Proverbs, Maxims "
             "and Mottos (Henry T. Riley, 1891)", "Latin and Greek quotations",
             "Henry T. Riley (George Bell and Sons)", "dictionaryoflati1891rileuoft", 1891,
             "Latin and Greek quotations, proverbs, maxims and mottos, classical and medieval, with law terms and "
             "phrases, each with its English translation and source, and an index of English words.", note=OLD_NOTE,
             country="United Kingdom"),
    old_book(GROUP, "bohn_handbook_of_proverbs_1855", "A Hand-Book of Proverbs: Ray's Collection of English Proverbs "
             "(Henry G. Bohn, 1855)", "Proverbs", "Henry G. Bohn (Henry G. Bohn, London)",
             "ahandbookprover01raygoog", 1855,
             "John Ray's classic collection of English proverbs, reprinted whole with additions, and an alphabetical "
             "index of the proverbs.", note=OLD_NOTE, country="United Kingdom"),
    old_book(GROUP, "apperson_english_proverbs_1929", "English Proverbs and Proverbial Phrases: A Historical "
             "Dictionary (G. L. Apperson, 1929)", "Proverbs", "G. L. Apperson (J. M. Dent and Sons)",
             "in.ernet.dli.2015.147398", 1929,
             "A historical dictionary of English proverbs and proverbial phrases, alphabetically by their key words, "
             "each traced through its uses in print with the dates and sources.", note=OLD_NOTE,
             country="United Kingdom"),
    old_book(GROUP, "inwards_weather_lore_1898", "Weather Lore: A Collection of Proverbs, Sayings and Rules "
             "Concerning the Weather (Richard Inwards, 1898)", "Proverbs: weather sayings",
             "Richard Inwards (Elliot Stock, London)", "weatherlorecolle00inwa", 1898,
             "Weather proverbs, sayings and rules from many countries, arranged by subject (times and seasons, the "
             "sun, moon and stars, clouds, wind, rain, animals and plants), with notes on which have a basis.",
             note=OLD_NOTE + " Weather sayings are not forecasts: use the National Weather Service.",
             country="United Kingdom"),
    old_book(GROUP, "de_bekker_desk_book_idioms_1923", "A Desk Book of Idioms and Idiomatic Phrases in English Speech "
             "and Literature (Leander J. De Bekker, 1923)", "Idioms", "Leander J. De Bekker",
             "in.ernet.dli.2015.88808", 1923,
             "English idioms and idiomatic phrases, alphabetically by their key words, each explained in plain "
             "words, often with an example of its use.", note=OLD_NOTE),
]

# ====================================================================== Wikiquote (CC BY-SA 4.0, from the XML dump)

WIKIQUOTE = "https://en.wikiquote.org/wiki"
WIKIQUOTE_DUMP = "https://dumps.wikimedia.org/enwikiquote/latest/enwikiquote-latest-pages-articles.xml.bz2"
WIKIQUOTE_LICENCE_PAGE = f"{WIKIQUOTE}/Wikiquote:Copyrights"
WIKIQUOTE_LICENCE_TEXT = r"Creative Commons Attribution-ShareAlike"
CC_BY_SA = "CC BY-SA 4.0"
CC_BY_SA_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
LETTERS = list(string.ascii_lowercase) + ["other"]
# Labels for the toolkit's Kiwix library (build_textbooks gathers them through more_refs.kiwix_labels).
KIWIX_LABELS = {"wikiquote_en_all": "CC BY-SA (share-alike)"}


def letter_of(title):
    """The piece a page title belongs to: its first letter ("a" to "z"), or "other"."""
    first = (title or " ")[0].lower()
    return first if first in string.ascii_lowercase else "other"


def wikiquote_pages(path, letter):
    """[(title, wikitext)] of the articles (namespace 0, not redirects) of the dump at path whose titles belong to
    letter, in title order."""
    out, title, text, page_ns = [], "", "", ""
    with bz2.open(path, "rb") as f:
        for _event, el in ET.iterparse(f, events=("end",)):
            tag = el.tag.rsplit("}", 1)[-1]
            if tag == "title":
                title = el.text or ""
            elif tag == "ns":
                page_ns = el.text or ""
            elif tag == "text":
                text = el.text or ""
            elif tag == "page":
                if page_ns == "0" and letter_of(title) == letter and not re.match(r"\s*#redirect", text, re.I):
                    out.append((title, text))
                el.clear()
    return sorted(out, key=lambda p: p[0].casefold())


def wikiquote_html(wikitext):
    """The HTML of one Wikiquote article: its headings, quotations (lists) and paragraphs, with templates, tables,
    files, categories and references' markup left out (directory_pubs.wikinews_html)."""
    import directory_pubs
    return directory_pubs.wikinews_html(wikitext)[1]


def wikiquote_book(name, work, cache=None, left_out=None, limit=None):
    """The Wikiquote book of one letter ("wikiquote:q"): every article whose title starts with it."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    letter = name.split(":", 1)[1]
    if not K.readable(WIKIQUOTE_LICENCE_PAGE, cache) or \
            not re.search(WIKIQUOTE_LICENCE_TEXT, B.fetch(WIKIQUOTE_LICENCE_PAGE, cache)):
        left_out.append({"title": "Wikiquote", "reason": "Its licence line (CC BY-SA) was not found on "
                         f"{WIKIQUOTE_LICENCE_PAGE}; not built."})
        return None
    path = K.download_file(WIKIQUOTE_DUMP, cache, max_age_days=20)
    shown = letter.upper() if letter != "other" else "digits and other signs"
    book = K.new_book(f"quote_wikiquote_{letter}", f"Wikiquote: pages starting with {shown}", "Quotations",
                      GROUP, "Wikiquote contributors (en.wikiquote.org)", CC_BY_SA, CC_BY_SA_URL,
                      f"{WIKIQUOTE}/Main_Page",
                      f"Every English Wikiquote article whose title starts with {shown}: quotations from people, "
                      "books, films, television programmes and themes, and proverbs, each quotation with its source "
                      "where Wikiquote gives one. Read from Wikimedia's official dump of the site.",
                      "From Wikiquote (en.wikiquote.org), written by its contributors, CC BY-SA 4.0 (share-alike: "
                      "anything made from it keeps the same licence); each page's history lists its authors. "
                      "Wikiquote checks its sources but makes mistakes; a quotation's own source is the authority.",
                      country="International",
                      changes="each article's wikitext made into a web page, with templates, tables, pictures, "
                              "categories and reference markup left out")
    for chapter, (title, text) in enumerate(wikiquote_pages(path, letter), 1):
        if limit and len(book.pages) >= limit:
            break
        body = wikiquote_html(text)
        if not re.sub(r"<[^>]+>|\s", "", body):
            continue
        url = f"{WIKIQUOTE}/{urllib.parse.quote(title.replace(' ', '_'))}"
        book.pages.append(B.Page(f"{B.slug(title, 50)}-{chapter}", title, f'{body}<p>Source: <a href="{B.esc(url)}">'
                                 f"{B.esc(url)}</a></p>", chapter, title[:2].upper()))
    book.originals.append({"url": WIKIQUOTE_DUMP, "kind": "xml.bz2", "title": "English Wikiquote dump"})
    book.published = ""
    book.version = f"Wikimedia dump of English Wikiquote, read {datetime.date.today().isoformat()}"
    return book if book.pages else None


def wikiquote_sign(name):
    """The weekly sign: the dump's date (Last-Modified), so a letter is rebuilt when a new dump is out."""
    return K.last_modified(WIKIQUOTE_DUMP)


# ====================================================================== the index

SECTIONS = [
    ("Dictionaries of quotations", "Find who said something, and where.", [
        ("key", "quote:bartlett_familiar_quotations_1919", "Bartlett's Familiar Quotations (1919): by author, with an "
                                                           "index of words"),
        ("key", "quote:hoyt_new_cyclopedia_quotations_1922", "Hoyt's New Cyclopedia of Practical Quotations (1922): by "
                                                             "subject"),
        ("key", "quote:benham_book_of_quotations_1907", "Benham's Book of Quotations, Proverbs and Household Words"),
        ("key", "quote:wood_dictionary_of_quotations_1893", "Wood's Dictionary of Quotations (by first words)"),
        ("key", "quote:dalbiac_dictionary_quotations_english_1908", "Dalbiac's Dictionary of Quotations (English)"),
        ("key", "quote:riley_latin_greek_quotations_1891", "Latin and Greek quotations and mottos, translated"),
        ("key", "quote:wikiquote:a", "Wikiquote, the whole English site, one book per first letter (quote:wikiquote:a "
                                     "to quote:wikiquote:z and quote:wikiquote:other; share-alike)")]),
    ("Proverbs and sayings", "Proverbs, proverbial phrases and weather sayings.", [
        ("key", "quote:apperson_english_proverbs_1929", "English proverbs traced through history (Apperson)"),
        ("key", "quote:bohn_handbook_of_proverbs_1855", "Ray's collection of English proverbs (Bohn)"),
        ("key", "quote:inwards_weather_lore_1898", "Weather proverbs and sayings (Inwards)"),
        ("key", "quote:wikiquote:e", "Wikiquote's proverb pages are named by language: English proverbs under E "
                                     "(Russian proverbs under R, and so on)")]),
    ("Idioms, phrases and allusions", "What a phrase means and where it comes from.", [
        ("key", "quote:brewer_dictionary_phrase_fable_1898", "Brewer's Dictionary of Phrase and Fable (1898)"),
        ("key", "quote:brewer_readers_handbook_1904", "Brewer's Reader's Handbook: names, allusions and plots"),
        ("key", "quote:de_bekker_desk_book_idioms_1923", "A Desk Book of Idioms and Idiomatic Phrases (1923)"),
        ("link", "Wiktionary (idioms and phrases)", "https://en.wiktionary.org/wiki/Category:English_idioms",
         "in the toolkit's Kiwix library (CC BY-SA); open it there or in a browser")]),
]
INDEX = X.index_maker("quote", GROUP, "Quotations and proverbs: a guide to the library", "Quotations",
                      "A guide to quotations, proverbs, idioms and phrases in the library.", SECTIONS)

MAKERS = {"index": INDEX, "wikiquote": (wikiquote_book, wikiquote_sign)}

COLLECTION = K.Collection("quote", GROUP, pdfs=PDFS, makers=MAKERS,
                          pieces={"wikiquote": lambda: list(LETTERS)},
                          words={"quotations": lambda: ["quote:index"] + [f"quote:{p['name']}" for p in PDFS] +
                                 [f"quote:wikiquote:{x}" for x in LETTERS]})

LICENCE_LINES = {
    "quotations_old_books": "Internet Archive scans of books published before 1931 (US public domain; the builder "
                            "checks each item's year at every build); archive.org's robots.txt allows the files, no "
                            "AI rules (checked 2026-11-22).",
    "quotations_wikiquote": "Wikiquote: CC BY-SA 4.0, share-alike (the licence line checked on Wikiquote:Copyrights "
                            "at every build); read from dumps.wikimedia.org (no robots.txt: 404), Wikimedia's "
                            "official dump; en.wikiquote.org's robots.txt has no AI rules (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("Later editions of Bartlett's Familiar Quotations, Hoyt's and Brewer's (1931 and later)", "Still in copyright "
     "(for example Bartlett's 11th edition of 1937 and every later one). The public-domain editions are built. "
     "Link-only. Index: https://archive.org/search?query=bartlett+familiar+quotations"),
    ("Project Gutenberg's copy of Bartlett's Familiar Quotations (ebook 27889)", "Public domain, but its Internet "
     "Archive copy has no PDF for the builder to read, and Project Gutenberg's books are in the toolkit's Kiwix "
     "library; the 1919 scan is built. Index: https://www.gutenberg.org/ebooks/27889"),
    ("English Idioms (James Main Dixon, Nelson)", "Its Internet Archive record gives no year (\"[19--?]\"), so the "
     "builder cannot show it was published before 1931; not built. Index: "
     "https://archive.org/details/englishidioms00dixouoft"),
    ("Kiwix's Wikiquote file (wikiquote_en_all)", "download.kiwix.org's robots.txt turns programs away; the same "
     "site is built from Wikimedia's dump (quote:wikiquote:a and the others), and the Kiwix file is labelled CC BY-SA "
     "for the toolkit's Kiwix library. Index: https://library.kiwix.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
