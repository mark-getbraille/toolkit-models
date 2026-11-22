"""Books to read aloud to children, in the group "Reference, parenting and family" (the owner's request of
2026-11-22). Keys: read-aloud (the English books and the nursery rhymes), readaloud:<source> (every piece of one
source), readaloud:<source>:<piece> (one language and reading level), readaloud:nursery_rhymes.

What this module builds, in plain words:
  - openly licensed picture books (CC BY 4.0), one book per language and reading level, one page per story with its
    words, author, illustrator credit and publisher, from the official offline packages their publishers put in
    Learning Equality's Kolibri Studio public library:
      Book Dash (South Africa: picture books for reading aloud to children up to about age six, in English and
      the South African languages);
      the African Storybook (Saide, South Africa: stories in more than 150 African languages, English and French,
      at five reading levels, from first words to read-aloud stories).
    The stories come as PDFs, which carry no picture descriptions, so the pictures are left out; a story's words
    are kept page by page. Pratham Books' StoryWeaver and the Global Digital Library are already in the library
    (directory_sources.py: dir:storyweaver, dir:gdl) and are not repeated.
  - "Nursery rhymes, lullabies and fairy tales to read aloud": old public-domain books (published before 1931,
    checked on each Internet Archive record at every build), one part per book: The Real Mother Goose (1916),
    Halliwell's Nursery Rhymes of England (1886), lullabies and cradle songs, Joseph Jacobs's English Fairy Tales,
    Andrew Lang's Blue Fairy Book, the Brothers Grimm and Hans Christian Andersen. The scanned books' text was read
    by a machine (OCR) and has its mistakes; some words and ideas in old books are out of date or offensive today.

Not built (NOT_INCLUDED): Let's Read (The Asia Foundation; a JavaScript reading application with no published
download or catalogue route), Bloom Library (its catalogue is reached only through the site's own application
keys; its robots.txt refuses /player/ and /readBook/), and Project Gutenberg's and Wikisource's copies (already in
the Kiwix library).

Run from the repository's folder:
  python3 textbooks/read_aloud.py readaloud:bookdash:english-0 --out build/textbooks --limit 5
  python3 textbooks/read_aloud.py --list read-aloud
"""

import datetime
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "parenting"
STUDIO = "https://studio.learningequality.org"
CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
TIME_BUDGET = 3.4 * 3600         # seconds one key may take (a build job's limit is 4 hours)

# Learning Equality's Kolibri Studio public channels of the publishers (studio.learningequality.org/api/public/v1/
# channels): each is a SQLite file of topics and stories with each story's licence and files. Both are CC BY
# throughout (checked 2026-11-22: every resource's license_name is "CC BY"; Book Dash 681 stories in 21 language
# folders, the African Storybook 5,165 stories by language and level).
CHANNELS = {
    "bookdash": dict(id="2d7b056d668a58ee9244ccf76108cbdb", title="Book Dash", country="South Africa",
                     publisher="Book Dash (South Africa), from its Kolibri Studio channel",
                     source="https://bookdash.org/"),
    "african_storybook": dict(id="f9d3e0e46ea25789bbed672ff6a399ed", title="African Storybook",
                              country="South Africa", source="https://www.africanstorybook.org/",
                              publisher="African Storybook Initiative (Saide, South Africa), from its Kolibri Studio "
                                        "channel"),
}
# The reading levels: the African Storybook's own five; Book Dash's books have none (all read-aloud picture books).
LEVELS = {"0": "Read-aloud picture books (about ages 2 to 6)",
          "1": "Level 1: first words (the African Storybook's reading level)",
          "2": "Level 2: first sentences", "3": "Level 3: first paragraphs", "4": "Level 4: longer paragraphs",
          "5": "Level 5: longer stories to read aloud"}
STORY_NOTICE = ("Each story is under the Creative Commons Attribution 4.0 licence; its own credits (author, "
                "illustrator, translator, publisher) are on its page. Pictures are left out: the stories' PDFs carry "
                "no picture descriptions.")


def channel_db(name, work):
    """An open connection to a channel's SQLite file (downloaded into work once per channel version)."""
    import courses                               # here, not at the top: courses imports the builder
    spec = CHANNELS[name]
    return courses.kolibri_db(spec, work, str(courses.kolibri_channel_info(spec).get("version") or ""))


def story_rows(db):
    """[(node id, title, description, author, licence, owner, language, level)] of every story: a channel's tree is
    channel / language / story (Book Dash) or channel / language / "Level n" / story (the African Storybook)."""
    nodes = {r[0]: r[1:] for r in db.execute("select id, title, parent_id, kind, description, author, license_name, "
                                             "license_owner from content_contentnode")}
    out = []
    for node_id, (title, parent, kind, desc, author, lic, owner) in nodes.items():
        if kind == "topic":
            continue
        chain, q = [], parent
        while q:
            chain.append(nodes[q][0])
            q = nodes[q][1]
        chain.reverse()                          # root first: [channel, language, (level)]
        language = chain[1] if len(chain) > 1 else ""
        level = next((re.sub(r"\D", "", c) for c in chain if re.fullmatch(r"Level \d", c or "")), "0")
        out.append((node_id, title or "", desc or "", author or "", lic or "", owner or "", language, level))
    return out


def pieces_of(name, work=None):
    """Every piece ("english-1": a language and a reading level) of a channel, English first."""
    import build_textbooks as B
    work = work or os.path.join("build", "textbooks-cache", "work")
    rows = story_rows(channel_db(name, work))
    found = sorted({(B.slug(r[6]), r[7]) for r in rows if r[6]}, key=lambda p: (p[0] != "english", p))
    return [f"{lang}-{level}" for lang, level in found]


def picture_book(name, piece, work, cache=None, left_out=None, limit=None):
    """The Book of one piece of a channel: every CC BY story of one language at one level, one page per story (its
    PDF's words, page by page), with its credits; a story listed twice is read once. limit: so many stories."""
    import build_textbooks as B
    import courses                               # here, not at the top: courses imports the builder
    left_out = left_out if left_out is not None else []
    spec = CHANNELS[name]
    url = f"{STUDIO}/content/databases/{spec['id']}.sqlite3"
    if not K.readable(url, cache):
        left_out.append({"title": spec["title"], "reason": "robots.txt does not allow Kolibri Studio's channel file."})
        return None
    db = channel_db(name, work)
    info = courses.kolibri_channel_info(spec)
    lang_slug, _, level = piece.rpartition("-")
    rows = sorted((r for r in story_rows(db) if B.slug(r[6]) == lang_slug and r[7] == level), key=lambda r: r[1])
    if not rows:
        left_out.append({"title": f"{spec['title']}: {piece}", "reason": "The channel has no stories for this piece."})
        return None
    language = rows[0][6]
    seen, pages, counts, originals = set(), [], {}, []
    start = time.monotonic()
    for node_id, title, desc, author, lic, owner, _lang, _lvl in rows:
        if (title, author) in seen or (limit and len(seen) >= limit):
            continue
        seen.add((title, author))
        if lic != "CC BY":
            counts[f"stories under \"{lic or 'no licence'}\""] = counts.get(f"stories under \"{lic or 'no licence'}\"",
                                                                             0) + 1
            continue
        if time.monotonic() - start > TIME_BUDGET:
            counts["stories not read this time (the time for one build ran out)"] = \
                counts.get("stories not read this time (the time for one build ran out)", 0) + 1
            continue
        pdfs = [(c, e) for c, e, _l in courses.kolibri_files(db, node_id).get("document", []) if e == "pdf"]
        if not pdfs:
            counts["stories without a PDF"] = counts.get("stories without a PDF", 0) + 1
            continue
        checksum, ext = pdfs[0]
        file_url = courses.kolibri_file_url(checksum, ext)
        local = courses.download(file_url, os.path.join(work, "kolibri", "files", f"{checksum}.pdf"))
        got = courses.pdf_pages_as_pages(local, f"s-{node_id[:12]}", " ".join(title.split()), 0, LEVELS.get(level, ""),
                                         split=200)
        os.remove(local)
        if not got:
            counts["stories without readable words"] = counts.get("stories without readable words", 0) + 1
            continue
        credit = " ".join(x for x in (f"By {author}." if author.strip() else "",
                                      f"Published by {owner}." if owner.strip() else "", "Licence: CC BY 4.0.") if x)
        got[0].body = (f"<p>{B.esc(' '.join(desc.split()))}</p>" if desc.strip() else "") + \
            f"<p>{B.esc(credit)}</p>" + got[0].body
        pages += got
        originals.append({"url": file_url, "kind": "pdf"})
    if not pages:
        left_out.append({"title": f"{spec['title']}: {piece}", "reason": "No story could be read."})
        return None
    meta = db.execute("select version, last_updated from content_channelmetadata").fetchone() or (None, None)
    words = LEVELS.get(level, "")
    book = K.new_book(
        f"readaloud_{name}_{B.slug(piece, 50).replace('-', '_')}",
        f"{spec['title']}: stories in {language}" + (f", level {level}" if level != "0" else ", picture books to read "
                                                      "aloud"),
        "Children's picture books to read aloud", GROUP, spec["publisher"], "CC BY 4.0", CC_BY_4, spec["source"],
        f"Children's picture stories in {language} from {spec['title']} ({words.split(' (')[0]}): every story of the "
        "channel at this level, one page each, with its words and credits, for reading aloud to a child or with a "
        "beginning reader." + (" Left out: " + "; ".join(f"{n} {what}" for what, n in sorted(counts.items())) + "."
                               if counts else ""),
        STORY_NOTICE, country=spec["country"], level="school", grades=words,
        language=__import__("directory_sources").two_to_three(language),
        published=B.iso_date(info.get("last_published") or str(meta[1] or "")),
        version=f"Kolibri Studio channel \"{spec['title']}\" version {info.get('version') or meta[0]}",
        changes="each story's PDF made into a web page of its words (pictures left out)")
    book.pages = pages
    book.originals = [{"url": url, "kind": "sqlite"}] + originals[:300]
    return book


def channel_sign(name):
    """The weekly sign of a channel: its version in Kolibri Studio's public list."""
    import courses
    return lambda piece: str(courses.kolibri_channel_info(CHANNELS[name]).get("version") or "")


# ====================================================================== nursery rhymes, lullabies and fairy tales

OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"
# (Internet Archive identifier, title, year): items found with the Internet Archive's advanced search (2026-11-22),
# the most read copy with a text layer of each book.
OLD_BOOKS = [
    ("realmothergoosewrig", "The Real Mother Goose (illustrated by Blanche Fisher Wright)", 1916),
    ("nurseryrhymesofe00hall", "The Nursery Rhymes of England (James Orchard Halliwell)", 1886),
    ("lullabiesslumber00hullrich", "Lullabies and Slumber Songs, with a few other child verses", 1901),
    ("bookoflullabies00smit", "A Book of Lullabies (Elva S. Smith)", 1925),
    ("englishfairytale1902jaco", "English Fairy Tales (Joseph Jacobs)", 1902),
    ("bluefairybook00langiala", "The Blue Fairy Book (Andrew Lang)", 1889),
    ("fairytalesofbrot00grim", "The Fairy Tales of the Brothers Grimm", 1916),
    ("fairytalesfromha00ande3", "Fairy Tales from Hans Christian Andersen", 1899),
]
OLD_NOTICE = ("Old public-domain books (published before 1931): their words were read from scanned pages by a machine "
              "(OCR) and have its mistakes, and some words and ideas in them are out of date or offensive today. "
              "Pictures are left out; their captions are kept as text.")


def nursery_book(name, work, cache=None, left_out=None, limit=None):
    """One book of the old nursery rhyme, lullaby and fairy tale books, one part per book (each read whole from its
    Internet Archive PDF by build_textbooks.pdfdoc_book, which checks the publication year on the item's record)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    book = K.new_book("readaloud_nursery_rhymes", "Nursery rhymes, lullabies and fairy tales to read aloud",
                      "Nursery rhymes and fairy tales", GROUP, "Internet Archive copies of old public-domain books",
                      OLD_LICENCE, OLD_URL, "https://archive.org/",
                      "Mother Goose and the old nursery rhymes, lullabies and cradle songs, and the classic fairy "
                      "tales (Jacobs's English Fairy Tales, Lang's Blue Fairy Book, the Brothers Grimm, Hans Christian "
                      "Andersen), each old book whole as one part, for reading aloud to children.", OLD_NOTICE,
                      level="school", grades="Read aloud to young children",
                      changes="each scanned book's machine-read text made into web pages, one per chapter or ten "
                              "pages at a time")
    years = []
    for identifier, title, year in OLD_BOOKS[:limit or None]:
        entry = dict(name=f"readaloud_{identifier}", title=title, subject=book.subject, group=GROUP,
                     country="United States", publisher=f"published {year}", licence=OLD_LICENCE,
                     licence_url=OLD_URL, archive=identifier, old_public_domain=True, description=title,
                     published=str(year))
        part = B.pdfdoc_book(entry, work, cache, left_out)
        if part is None:
            continue
        for page in part.pages[:limit * 3 if limit else None]:
            page.unit = title
            page.title = f"{title.split(' (')[0]}: {page.title}"
            page.path = f"{identifier[:20]}-{page.path}"
            book.pages.append(page)
        book.originals.append({"url": part.original_pdf.get("url") or part.source, "kind": "pdf"})
        years.append(year)
    if not book.pages:
        return None
    book.published = str(max(years))
    book.version = "Internet Archive items " + ", ".join(i for i, _t, _y in OLD_BOOKS[:limit or None])
    return book


COLLECTION = K.Collection(
    "readaloud", GROUP,
    makers={"bookdash": (lambda name, work, cache, left_out, limit: picture_book(
                "bookdash", name.split(":", 1)[1], work, cache, left_out, limit), lambda name: channel_sign(
                "bookdash")(name)),
            "african_storybook": (lambda name, work, cache, left_out, limit: picture_book(
                "african_storybook", name.split(":", 1)[1], work, cache, left_out, limit), lambda name: channel_sign(
                "african_storybook")(name)),
            "nursery_rhymes": (nursery_book, lambda name: K.sha([i for i, _t, _y in OLD_BOOKS]))},
    pieces={"bookdash": lambda: pieces_of("bookdash"), "african_storybook": lambda: pieces_of("african_storybook")},
    words={"read-aloud": lambda: [f"readaloud:{n}:{p}" for n in CHANNELS for p in pieces_of(n)
                                  if p.startswith("english-")] + ["readaloud:nursery_rhymes"]})

GROUPS = {}
LICENCE_LINES = {
    "readaloud_kolibri": "Book Dash and the African Storybook through Learning Equality's Kolibri Studio public "
                         "channels (studio.learningequality.org/api/public/v1/channels; each channel's SQLite file "
                         "gives every story's license_name, \"CC BY\" for all 681 Book Dash and 5,165 African "
                         "Storybook stories, checked 2026-11-22 and again for each story at every build). "
                         "studio.learningequality.org's robots.txt allows the channel files; no AI rules.",
    "readaloud_old_books": "The nursery rhyme and fairy tale books: published before 1931 (public domain in the US), "
                           "the year checked on each Internet Archive item's record at every build; archive.org's "
                           "robots.txt allows /metadata/ and /download/ (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("Let's Read (The Asia Foundation, letsreadasia.org)", "CC BY 4.0 picture books, but the site is a JavaScript "
     "reading application (its pages come to programs empty) with no published download, catalogue or open data "
     "route, and it is not in Kolibri Studio's public library (checked 2026-11-22). Link-only. Index: "
     "https://www.letsreadasia.org/"),
    ("Bloom Library (SIL, bloomlibrary.org)", "Many books are CC BY (each book's own licence), but the catalogue is a "
     "JavaScript application reached only through the site's own application keys (no public API or bulk "
     "download), and its robots.txt refuses /player/ and /readBook/ (checked 2026-11-22). Link-only. Index: "
     "https://bloomlibrary.org/"),
    ("Pratham Books' StoryWeaver and the Global Digital Library", "Already in the library (directory_sources.py: "
     "dir:storyweaver and dir:gdl, by language and reading level); not repeated. Index: https://storyweaver.org.in/ "
     "and https://digitallibrary.io/"),
    ("Project Gutenberg and Wikisource nursery rhymes and fairy tales", "Already in the Kiwix library (Project "
     "Gutenberg and Wikisource collections); the read-aloud book is made from the Internet Archive's copies instead. "
     "Index: https://www.gutenberg.org/ebooks/bookshelf/22 (Children's Picture Books)"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
