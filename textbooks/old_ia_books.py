"""A small shared helper for the leisure collections of the reference library (the owner's request of 2026-11-22:
homesteading, outdoor recreation, games and hobbies, sacred and philosophical texts, science you can use, literature
and culture). Each of those modules lists old public-domain books of the Internet Archive; this file makes one PDF
entry from each, in the same shape as home_crafts.py's old books, so the six modules do not each repeat it.

In plain words, an entry made here:
  - names the Internet Archive item ("archive"), so build_textbooks.pdfdoc_book reads its PDF with the text layer;
  - says old_public_domain=True, so the builder reads the item's own record at every build and refuses the book when
    the record does not show it was published before 1931 (a later reprint may still be in copyright in the US);
  - carries the licence "Public domain (published before 1931)", the published year, the edition read (version),
    a description (with a note on what is out of date when the caller gives one) and the notice that the text was
    machine-read from scanned pages.
The builder adds the "originals" list (the PDF's address, kind, size, SHA-256, licence, may_download and why) itself.
"""

OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"
OLD_NOTICE = ("An old book in the US public domain (published before 1931), read from its Internet Archive scan: the "
              "machine-read text has the scanner's mistakes, and its pictures are described only by their captions.")
OLD_CHANGES = ("its scanned pages' machine-read text (with the scanner's mistakes) made into web pages, ten pages at a "
               "time or one per chapter")


def old_book(group, name, title, subject, publisher, archive, year, description, note="", notice="",
             country="United States", level="reference"):
    """One old public-domain book of the Internet Archive as a PDF entry (see the module docstring). note: words
    added to the description (what is out of date); notice: words added after the standard notice (a safety note)."""
    return dict(group=group, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                country=country, licence=OLD_LICENCE, licence_url=OLD_URL, old_public_domain=True, level=level,
                published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                description=description + (" " + note.format(year=year) if note else ""),
                notice=OLD_NOTICE + (" " + notice if notice else ""), changes=OLD_CHANGES)
