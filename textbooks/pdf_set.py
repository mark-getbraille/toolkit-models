"""One book made of SEVERAL official PDFs (the money, language, travel and civics collections of 2026-11-22): the
volumes of a Foreign Service Institute course, or a shelf of Supreme Court opinions. Each PDF is read with the
builder's own PDF reader (build_textbooks.pdfdoc_book: licence line checked, robots.txt asked, a scan without words
refused), and its pages are put one after another into one book, each PDF as one part ("unit") of it.

In plain words, for a list of parts [(part title, PDF address, page address)]:
  - every part is read like any single official PDF, so a scanned volume without a text layer is left out with its
    reason (the others are kept);
  - the pages keep their chapter numbers in reading order, under the part's title;
  - every PDF read is listed in the book's "originals" with its size and SHA-256 (the builder adds the licence and
    whether it may be downloaded).

Nothing here imports the builder at the top (the builder imports sources, which imports these modules at its end).
"""

import os


def pdf_set_book(entry, parts, work, cache=None, left_out=None, limit=None):
    """The Book of entry (a PDF_DOCS-like entry: name, title, subject, group, publisher, country, licence,
    licence_url, licence_page, licence_text, description, notice and so on) made of parts [(part title, pdf address,
    page address)], or None when no part could be read (each reason in left_out). limit: stop after about so many
    pages (a small test build)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    book, chapter = None, 0
    for i, (part, pdf, page) in enumerate(parts, 1):
        if limit and book is not None and len(book.pages) >= limit:
            break
        one = dict(entry, name=f"{entry['name']}_part{i}", title=f"{entry['title']}: {part}", pdf=pdf, page=page)
        one.pop("archive", None)
        local = os.path.join(work, f"{one['name']}.pdf")
        try:
            got = B.pdfdoc_book(one, work, cache, left_out)
        except Exception as e:  # noqa: BLE001 - said in left_out, the other parts are still read
            left_out.append({"title": one["title"], "reason": f"It could not be read ({e})."})
            got = None
        if got is None:
            continue
        got_pages = list(got.pages)              # kept apart: the first part's Book becomes the whole book
        got_pdf = dict(got.original_pdf, kind="pdf")
        if book is None:
            book = got
            book.name, book.title, book.pages = entry["name"], entry["title"], []
            book.source = entry.get("source") or page
            book.description = entry["description"]
            book.published = entry.get("published") or got.published
            book.original_pdf = {}
        for p in got_pages:
            chapter += 1
            book.pages.append(B.Page(f"{i}-{p.path}", p.title, p.body, chapter, part))
            if limit and len(book.pages) >= limit:
                break
        book.originals.append(got_pdf)
        if os.path.exists(local) and not cache:
            os.remove(local)                     # a build without a cache folder keeps no copies of the PDFs
    if book is not None:
        book.changes = ("each PDF's text made into web pages, one per chapter, the PDFs one after another as the "
                        "parts of one book, with each drawing's caption kept as text")
    return book
