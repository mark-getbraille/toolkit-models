"""Shared helpers for the six PRACTICAL LIFE reference modules (the owner's request of 2026-11-22): driving.py,
computer_basics.py, household.py, knots_outdoor.py, pools_spas.py and motorcycles_rvs.py. Not a source module itself
(it is not in more_refs.MODULES).

What it gives them, in plain words:
  - index_maker(): the "index" book each module has: a guide to everything in the library on its subject, one page
    per part, listing the books by key (with what each holds), the manual collections, the picture packs, and the
    sources that are links only (with the address and the reason). It is the toolkit's own list of facts and links
    (CC0), made from the module's SECTIONS; nothing is downloaded. A listed key the library no longer has is left
    out and said in the manifest's left_out.
  - page_list_book(): a web guide made of a fixed list of pages (no crawl beyond them), as in outdoor_cooking.py.
  - old_book(): an old public-domain book on the Internet Archive (published before 1931; the builder checks the
    item's year at every build), with a note on what is out of date in it.
  - the CDC helper cdc_site_book() and the shared licence names.

The index's weekly sign of change is a fingerprint of its sections (it changes only when the module's list does).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

CC0_INDEX = "CC0 1.0"
TOOLKIT_REPO = "https://github.com/mark-getbraille/toolkit-models"

OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"
OLD_NOTICE = ("An old book in the US public domain (published before 1931), read from its Internet Archive scan: the "
              "machine-read text has the scanner's mistakes, and its pictures are described only by their captions.")

# CDC's terms (as in outdoor_cooking.py): checked at every build, kept whole, credit and no-endorsement notice.
CDC = "https://www.cdc.gov"
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
CDC_PUBLISHER = "Centers for Disease Control and Prevention (CDC)"

# The EPA's terms (the same names as pets_home.py, which adds EPA_TERMS to sources.ALLOWED as non-commercial).
EPA_TERMS = "EPA website copyright statement"
EPA_DISCLAIMER = "https://www.epa.gov/web-policies-and-procedures/epa-disclaimers"
EPA_TEXT = r"These documents may be freely distributed and used for non-commercial, scientific and educational purposes"


def cdc_site_book(group, name, title, subject, sites, description, notice, units, limit=200):
    """A CDC web guide made of whole CDC sites, each read from its own site index ("site.html", which lists every
    page of the site), kept whole under CDC's terms. A site that does not answer adds no pages."""
    alt = "|".join(sites)
    pages = rf"^https://www\.cdc\.gov/({alt})/(?!es/|media/|site\.html|php/|hcp/)[a-z0-9-]+(/[a-z0-9-]+)*\.html$"
    entry = K.guide(group, name, title, subject, CDC_PUBLISHER, [f"{CDC}/{s}/site.html" for s in sites], pages,
                    description, f"{CDC_NOTICE} {notice}", depth=1, units=units, limit=limit)
    return dict(entry, licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True)


def page_list_book(group, name, title, subject, publisher, urls, pages, description, notice, units=(), **more):
    """A web guide of a fixed list of pages (no crawl beyond them): the first address is its source."""
    return K.us_web(group, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=notice, crawl=[(urls[0], 0)], urls=list(urls), pages=pages,
                    unit_rules=list(units), limit=len(urls) + 5, **more)


def old_book(group, name, title, subject, publisher, archive, year, description, note, country="United States"):
    """One old public-domain book of the Internet Archive (published before 1931) as a PDF entry; note says what is
    out of date in it."""
    return dict(group=group, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                country=country, licence=OLD_LICENCE, licence_url=OLD_URL, old_public_domain=True, level="reference",
                published=str(year), version=f"{year} edition", description=f"{description} {note}",
                notice=OLD_NOTICE, changes="its scanned pages' machine-read text (with the scanner's mistakes) made "
                                           "into web pages, ten pages at a time or one per chapter")


def key_exists(key):
    """True when key is a book key of the library (a sources.py record or a key of a more_refs module). Imported here,
    not at the top: sources imports the modules at its end."""
    import more_refs
    import sources
    prefix, _, name = key.partition(":")
    tables = {"guide": sources.GOV_GUIDES, "law": sources.LAWS + sources.LAWS_MORE, "pdf": sources.PDF_DOCS,
              "nonprofit": sources.NONPROFIT}
    if prefix in tables:
        return any(e["name"] == name for e in tables[prefix])
    if prefix == "tech":                    # the computer help books (tech_kb.py, through refs_common)
        return key in sources.expand_keys(["techdocs"])
    if prefix == "cook":                    # cookbooks.py's own books (cooking_basics.py shares the prefix)
        import cookbooks
        if name in cookbooks.BY_NAME:
            return True
    m = more_refs.module_for(key)
    return bool(m) and key in m.COLLECTION.own_keys()


def index_maker(prefix, group, title, subject, description, sections, country="United States"):
    """(book function, sign function) of a module's index book (its maker "index"), from sections:
    [(part title, intro, entries)], each entry one of
      ("key", "<book key>", "what it holds")             a book of the library
      ("manuals", "<category>", "what it holds")          a manual collection
      ("pack", "<pack key>", "what it shows")             a picture pack
      ("word", "<request word>", "what it holds")         another collection's books, asked for by its request word
      ("link", "<name>", "<address>", "why link-only")   a source the owner opens or fetches himself."""

    def book_fn(name, work, cache=None, left_out=None, limit=None):
        """The index book: one page per part (see index_maker)."""
        import build_textbooks as B
        left_out = left_out if left_out is not None else []
        book = K.new_book(f"{prefix}_index", title, subject, group, "Digital Accessibility Toolkit (an index of the "
                          "library)", CC0_INDEX, K.CC0_URL, TOOLKIT_REPO, description,
                          "Facts and links only (CC0). Each book listed has its own licence, shown in that book; each "
                          "link-only source belongs to its publisher.", country=country,
                          changes="an index written for the toolkit")
        for number, (part, intro, entries) in enumerate(sections, 1):
            if limit and len(book.pages) >= limit:
                break
            books, manuals, packs, links = [], [], [], []
            for kind, what, words, *more in entries:
                if kind == "key":
                    if not key_exists(what):
                        left_out.append({"title": what, "reason": "The library has no book with this key now."})
                        continue
                    books.append(f"<li>{B.esc(words)} (key {B.esc(what)})</li>")
                elif kind == "manuals":
                    manuals.append(f"<li>{B.esc(words)} (manual collection {B.esc(what)})</li>")
                elif kind == "pack":
                    packs.append(f"<li>{B.esc(words)} (picture pack {B.esc(what)})</li>")
                elif kind == "word":
                    books.append(f"<li>{B.esc(words)} (request word {B.esc(what)})</li>")
                else:
                    links.append(f'<li>{B.esc(what)}: <a href="{B.esc(words)}">{B.esc(words)}</a>. '
                                 f"{B.esc(more[0])}</li>")
            body = f"<p>{B.esc(intro)}</p>"
            for head, items in (("Books in the library", books), ("Manual collections", manuals),
                                ("Picture packs (for the picture describer)", packs),
                                ("Links only (open them in a browser or with Program Downloader)", links)):
                if items:
                    body += f"<h2>{head}</h2><ul>{''.join(items)}</ul>"
            book.pages.append(B.Page(f"part-{number}-{B.slug(part, 40)}", part, body, number, ""))
        book.published = ""
        return book

    def sign_fn(name):
        """The weekly sign of the index: a fingerprint of its sections."""
        return K.sha(sections)

    return book_fn, sign_fn
