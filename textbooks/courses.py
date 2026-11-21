"""Open courses, school books and personal-use courses as ZIM books (keys course:<source>:<piece>).

The textbooks builder (build_textbooks.py) makes the books; this module adds the sources that come as large
catalogues, each read through its own official download route (never by crawling a website):

  libretexts     LibreTexts (University of California, Davis, and partners): every book of its Commons catalogue
                 (commons.libretexts.org/api/v1/commons/catalog, about 4,150 books in 14 libraries) whose licence
                 is one the toolkit may repackage. Each book is read from its official full PDF
                 (downloads.libretexts.org), which LibreTexts makes for every book; the PDF's pages are split back
                 into the book's own pages at the line LibreTexts prints under each one ("This page titled 2.1:
                 Understanding Decimals is shared under a CC BY license and was authored, remixed, and/or curated
                 by ..."), so every page keeps its own title, licence and authors. The library sites themselves
                 (bio.libretexts.org ...) ask for 5 seconds between requests and forbid their API (/@api) in
                 robots.txt, so they are not read.
  kolibri        Learning Equality's Kolibri Studio public channels (studio.learningequality.org): the packages
                 Kolibri, the offline learning program, imports. A channel is one SQLite file
                 (/content/databases/<channel id>.sqlite3) listing its topics and resources with each one's licence
                 and files (/content/storage/<a>/<b>/<checksum>.<ext>). Documents (PDF) become text, videos their
                 subtitles (a transcript), web pages ("html5" zips such as CK-12's FlexBook lessons) their text;
                 exercises and interactive H5P items are left out (said in the book). Channels: BCcampus Open
                 Textbooks (open), and for personal use only Khan Academy (English, US curriculum: the only route to
                 Khan Academy here; khanacademy.org itself is never read), CK-12 and EngageNY.
  ocw            MIT OpenCourseWare (personal use only: CC BY-NC-SA 4.0): every course, read from the course's
                 own offline download (ocw.mit.edu/courses/<course>/download/ -> <course>.zip, made by MIT for
                 offline use), whose data.json files give each page and resource with its licence: the course's
                 pages (syllabus, readings, calendar ...), its PDFs (lecture notes, problem sets, exams) as text and
                 its video transcripts.
  coreknowledge  Core Knowledge Foundation (personal use only: CC BY-NC-SA 4.0): every free resource of its library
                 (www.coreknowledge.org/free-resource/..., listed in its library sitemaps): the PDFs of each one as a
                 book (Core Knowledge Language Arts, history and geography, science), with the licence read from the
                 PDF's own copyright page.

Every book records its licence (and "personal use only" where the licence is non-commercial: sources.PERSONAL_USE),
the grade level where known, the practice notice for a non-US source (sources.practice_note, from its country and
subject), "published" (the publisher's own date) and "version", and the key and fingerprint for the weekly update
check (sign()). Books are grouped as "course" (college and career courses), "textbooks" (LibreTexts bookshelves)
and "k12" (school books).

Pieces: no build job may run longer than 4 hours, so big sources are split into pieces that stay well under it:
LibreTexts by library and a stable bucket of book ids (LT_BUCKETS), OpenCourseWare by department and a stable bucket
of course names (OCW_BUCKETS), Kolibri channels by top-level topic, Core Knowledge by bucket. A piece that still runs
out of time (TIME_BUDGET) stops, keeps the books it finished, and says which ones are left in "left_out".

What was looked at and not built, and why, is in NOT_INCLUDED; the Kiwix library's own books that cover some of the
same sources are named in KIWIX_LABELS (with "personal use only" where it applies), for the toolkit to label.

Keys:
  opencourses                  every open-course piece (LibreTexts, BCcampus)
  k12                          (with sources.expand_keys) the K-12 web books and PDFs, plus CK-12, EngageNY, Core
                               Knowledge and Khan Academy's maths by grade
  personaluse                  every personal-use piece (Khan Academy, CK-12, EngageNY, OpenCourseWare, Core Knowledge)
  course:<source>              every piece of one source (course:libretexts, course:ocw, course:khan ...)
  course:<source>:<piece>      one piece (course:libretexts:chem-3, course:ocw:18-2, course:khan:math, ...)

Use from the command line (the workflow calls it through build_textbooks.py):
  python textbooks/courses.py course:libretexts:workforce-0 --out build/textbooks --cache build/textbooks-cache
  python textbooks/courses.py course:libretexts:workforce-0 --only workforce-7065   (a small test build)
  python textbooks/courses.py --list opencourses
"""

import argparse
import datetime
import hashlib
import html
import io
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import zipfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import sources  # noqa: E402

TIME_BUDGET = 3.4 * 3600         # seconds one piece may take before it stops (the job's limit is 4 hours)
MAX_PDF_PAGES = 3000             # a PDF longer than this is not read (a guard against a wrong file)

# ====================================================================== licences

# Kolibri's and LibreTexts' licence names -> (short licence, its address); "" for one the toolkit may not repackage.
CC = "https://creativecommons.org/licenses/{}/4.0/"
KOLIBRI_LICENCES = {
    "CC BY": ("CC BY", CC.format("by")), "CC BY-SA": ("CC BY-SA", CC.format("by-sa")),
    "CC BY-NC": ("CC BY-NC", CC.format("by-nc")), "CC BY-NC-SA": ("CC BY-NC-SA", CC.format("by-nc-sa")),
    "Public Domain": ("PD", "https://creativecommons.org/publicdomain/mark/1.0/"),
}
LIBRETEXTS_LICENCES = {"ccby": "CC BY", "ccbysa": "CC BY-SA", "ccbync": "CC BY-NC", "ccbyncsa": "CC BY-NC-SA",
                       "publicdomain": "PD"}
KIND_ORDER = ["open", "share-alike", "non-commercial"]


def strictest(licences):
    """The strictest of some short licences (non-commercial over share-alike over open; "CC BY-NC-SA" when both
    a share-alike and a non-commercial one are among them), "" for none."""
    kinds = {B.licence_kind(x) for x in licences if B.licence_kind(x)}
    if not kinds:
        return ""
    if "non-commercial" in kinds:
        nc = [x for x in licences if B.licence_kind(x) == "non-commercial"]
        return "CC BY-NC-SA" if ("share-alike" in kinds or any("SA" in x for x in nc)) else nc[0]
    if "share-alike" in kinds:
        return next(x for x in licences if B.licence_kind(x) == "share-alike")
    return next(x for x in licences if B.licence_kind(x) == "open")


def licence_address(short):
    """The address of a short licence ("CC BY-NC-SA 4.0" -> its deed; "PD" -> the public domain mark)."""
    if short.startswith("PD"):
        return "https://creativecommons.org/publicdomain/mark/1.0/"
    m = re.match(r"CC ([A-Z-]+)(?: (\d\.\d))?", short)
    return f"https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2) or '4.0'}/" if m else ""


def is_personal(short):
    """True for a licence that makes a book "personal use only" (non-commercial or no-derivatives: the owner's rule
    for the sources added on 2026-11-21)."""
    return B.licence_kind(short, True) in ("non-commercial", "non-commercial-no-changes", "no-changes")


def grades_of(text):
    """The school grades a title names ("Grade 3 Mathematics" -> "3", "Kindergarten" -> "K", "Algebra I" ->
    "9-12", "Prekindergarten" -> "PreK"), "" when it names none."""
    t = text.lower()
    if re.search(r"\bpre-?k(indergarten)?\b|\bpreschool\b", t):
        return "PreK"
    if re.search(r"\bkindergarten\b", t):
        return "K"
    m = re.search(r"\bgrades?\s*(\d{1,2})(?:\s*(?:-|–|to)\s*(\d{1,2}))?\b", t) or \
        re.search(r"\b(\d{1,2})(?:st|nd|rd|th)\s+grade\b", t)
    if m:
        a = m.group(1)
        b = m.group(2) if m.lastindex and m.lastindex > 1 else None
        return f"{a}-{b}" if b else a
    if re.search(r"\b(algebra (i|ii|1|2)|geometry|precalculus|high school|ap®?|biology|chemistry|physics)\b", t):
        return "9-12"
    m = re.search(r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth)\s+grade\b", t)
    if m:
        return str(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"].index(m.group(1)) + 1)
    return ""


def bucket(text, n):
    """A stable bucket number (0 .. n-1) of a name: the same name always falls in the same piece."""
    return zlib.crc32(text.encode("utf-8")) % max(1, n)


# ====================================================================== shared helpers

_MEMO = {}


def memo_fetch(url, cache=None, binary=False):
    """B.fetch, remembered for this run (a catalogue read by many pieces or by the weekly check is read once)."""
    key = (url, binary)
    if key not in _MEMO:
        _MEMO[key] = B.fetch(url, cache, binary=binary)
    return _MEMO[key]


def download(url, path):
    """Download url to path once (a file already there is used); returns path."""
    if not os.path.exists(path) or not os.path.getsize(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = B.fetch(url, None, binary=True)
        with open(path + ".part", "wb") as f:
            f.write(data)
        os.replace(path + ".part", path)
    return path


def pdf_text_pages(path):
    """[text of each page] of a PDF (B.PdfText: pypdfium2 or pypdf), or [] when it cannot be read or is too long."""
    try:
        text = B.PdfText(path)
    except Exception:  # noqa: BLE001 - a damaged PDF
        return []
    if text.count > MAX_PDF_PAGES:
        return []
    return ["\n".join(text.lines(n)) for n in range(text.count)]


def paragraphs_html(text, page_number=None):
    """Plain text as HTML paragraphs (lines joined, blank lines between paragraphs), with a "[Page n]" mark first
    when page_number is given."""
    out = [f'<p class="pagenum">[Page {page_number}]</p>'] if page_number else []
    for para in re.split(r"\n\s*\n|\n(?=[••-]\s)", text or ""):
        line = " ".join(para.split())
        if line:
            out.append(f"<p>{B.esc(line)}</p>")
    return "\n".join(out)


def pdf_pages_as_pages(path, prefix, title, number, unit="", split=60):
    """[B.Page] of one PDF: one page when it is short, else one per chapter of its bookmarks (B.pdf_pages_html),
    each with "[Page n]" marks. [] when it has no readable words."""
    pages = pdf_text_pages(path)
    if not pages or sum(len(p) for p in pages) < 40:
        return []
    if len(pages) <= split:
        body = "\n".join(paragraphs_html(t, n) for n, t in enumerate(pages, 1))
        return [B.Page(prefix, title, body, number, unit)]
    out = []
    try:
        parts = B.pdf_pages_html(path)
    except Exception:  # noqa: BLE001 - read page by page instead
        parts = [(f"Pages {i + 1} to {min(len(pages), i + 10)}", "\n".join(
            paragraphs_html(pages[n], n + 1) for n in range(i, min(len(pages), i + 10))), i + 1, i + 10)
            for i in range(0, len(pages), 10)]
    for k, (part, body, first, last) in enumerate(parts, 1):
        out.append(B.Page(f"{prefix}-{k}", f"{title}: {part}" if part else f"{title} ({first} to {last})", body,
                          number, unit))
    return out


def vtt_text(data):
    """The words of a subtitle file (WebVTT or SRT), without times, numbers, tags and repeated lines."""
    text = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    out = []
    for line in text.replace("\r", "").split("\n"):
        line = line.strip()
        if not line or line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:", "STYLE")) or "-->" in line or \
                re.fullmatch(r"\d+", line):
            continue
        line = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
        if line and (not out or out[-1] != line):
            out.append(line)
    words = " ".join(out)
    sentences = re.split(r"(?<=[.?!])\s+(?=[A-Z])", words)
    paras, cur = [], []
    for s in sentences:
        cur.append(s)
        if len(cur) == 5:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras)


def html_text_page(raw, base="", latex=False):
    """The cleaned HTML of a web page's body (B._Cleaner), with CK-12's data-tex formulas and \\( \\) LaTeX written
    as text when latex is True, and MathML formulas as text."""
    body = re.search(r"<body\b[^>]*>(.*)</body>", raw, re.S | re.I)
    body = body.group(1) if body else raw
    if latex:
        body = re.sub(r'<span\b[^>]*\bdata-tex="([^"]*)"[^>]*>\s*</span>',
                      lambda m: "\\(" + B.esc(urllib.parse.unquote(html.unescape(m.group(1)))) + "\\)", body)
        body = B.latex_spans(body)
    body = B.mathml_spans(body)
    return B._Cleaner({}, base).clean(body)


# ====================================================================== LibreTexts

LT_CATALOGUE = "https://commons.libretexts.org/api/v1/commons/catalog?limit=10000"
LT_LIBRARIES = {"bio": "Biology", "biz": "Business", "chem": "Chemistry", "eng": "Engineering",
                "espanol": "Spanish-language books", "geo": "Geosciences", "human": "Humanities", "k12": "K-12",
                "math": "Mathematics", "med": "Medicine", "phys": "Physics", "socialsci": "Social sciences",
                "stats": "Statistics", "workforce": "Workforce (trades and careers)"}
# Buckets per library (2026-11-21: about 25,000 LibreTexts pages of allowed books per bucket, so one bucket's PDFs
# are read in well under the time budget). Keep these numbers: a book stays in its bucket while they stay.
LT_BUCKETS = {"bio": 3, "biz": 3, "chem": 7, "eng": 2, "espanol": 1, "geo": 2, "human": 8, "k12": 1, "math": 6,
              "med": 4, "phys": 2, "socialsci": 6, "stats": 1, "workforce": 1}
LT_PAUSE = 40.0                  # seconds between two PDF downloads (100 an hour are allowed)
PAGE_END = re.compile(r"This page titled\s+(.+?)\s+is shared under an?\s+(.+?)\s+license(?: and was authored, remixed,"
                      r" and/or curated by\s+(.+?)\s*(?:\.\s|\.$|\(|$))?", re.S)
RUNNING_HEAD = re.compile(r"^\s*(?:\d+(?:\.\d+)*\.\d+\s+)?https://\w+\.libretexts\.org/@go/page/\d+\s*$", re.M)


def lt_catalogue():
    """Every book of the LibreTexts Commons catalogue ([dict]), read fresh once per run (never from the cache
    folder, which the workflow keeps between runs)."""
    return json.loads(memo_fetch(LT_CATALOGUE)).get("books", [])


def lt_licence(book):
    """(short licence with version, or "", reason) of a LibreTexts catalogue entry."""
    kind = LIBRETEXTS_LICENCES.get(book.get("license") or "")
    if not kind:
        why = {"": "LibreTexts states no licence for it", "mixed": "its pages have mixed licences",
               "multiple": "its pages have several licences", "arr": "all rights reserved",
               "ck12": "CK-12's own licence", "gnufdl": "GNU Free Documentation License (not repackaged here)",
               "gnu": "a GNU licence (not repackaged here)", "ccbynd": "no derivatives",
               "ccbyncnd": "no derivatives"}.get(book.get("license") or "", f"licence \"{book.get('license')}\"")
        return "", why
    version = next((t.split(":", 1)[1] for t in book.get("libraryTags") or [] if t.startswith("licenseversion:")), "")
    version = f"{version[0]}.{version[1:]}" if re.fullmatch(r"\d\d", version) else ""
    return (f"{kind} {version}".strip() if kind != "PD" else "PD"), ""


def lt_pieces():
    """Every LibreTexts piece key ("libretexts:chem-3")."""
    return [f"libretexts:{lib}-{k}" for lib, n in LT_BUCKETS.items() for k in range(n)]


def lt_in_piece(book, piece):
    """True when a catalogue entry belongs to piece ("chem-3")."""
    lib, _, k = piece.rpartition("-")
    return book.get("library") == lib and bucket(book["bookID"], LT_BUCKETS.get(lib, 1)) == int(k)


def lt_pages(text_pages):
    """[(title, licence words, authors, body html)] of a LibreTexts full PDF's text (one string per PDF page): each
    page of the online book ends with the line "This page titled <title> is shared under a <licence> license and was
    authored, remixed, and/or curated by <authors>", and starts with its title, so the text is cut there. What comes
    before the first page is "Front matter" (title page, licensing, contents), what follows the last is "Back
    matter" (index, glossary, detailed licensing). A PDF without those lines is cut every ten PDF pages."""
    offsets, joined, pos = [], [], 0
    for n, t in enumerate(text_pages, 1):
        t = RUNNING_HEAD.sub("", t)
        offsets.append((pos, n))
        joined.append(t)
        pos += len(t) + 2
    text = "\n\n".join(joined)

    def body(start, end):
        """HTML of the text between start and end, with a [Page n] mark where each PDF page starts in it."""
        out = []
        for i, (s, number) in enumerate(offsets):
            e = offsets[i + 1][0] if i + 1 < len(offsets) else len(text)
            a, b = max(s, start), min(e, end)
            if a < b:
                out.append(paragraphs_html(text[a:b], number if a == s or not out else None))
        return "\n".join(x for x in out if x)
    marks = list(PAGE_END.finditer(text))
    if not marks:
        return [(f"Pages {i + 1} to {min(len(text_pages), i + 10)}", "", "",
                 "\n".join(paragraphs_html(text_pages[n], n + 1) for n in range(i, min(len(text_pages), i + 10))))
                for i in range(0, len(text_pages), 10)]
    out, previous_end = [], 0
    for i, m in enumerate(marks):
        title = " ".join(m.group(1).split())
        begin = text.rfind(title, previous_end, m.start())
        if begin < 0:                                          # the title is written another way: start where the
            begin = previous_end                               # previous page ended
        if begin - previous_end > 300:
            if i == 0:
                out.append(("Front matter", "", "", body(previous_end, begin)))
            elif out:
                t, lic, who, prev = out[-1]
                out[-1] = (t, lic, who, prev + "\n" + body(previous_end, begin))
        out.append((title, " ".join(m.group(2).split()), " ".join((m.group(3) or "").split()), body(begin, m.end())))
        previous_end = m.end()
    if len(text) - previous_end > 300:
        out.append(("Back matter", "", "", body(previous_end, len(text))))
    return out


# Words in a LibreTexts book's affiliation or title that show where it was written (for the practice notice).
LT_COUNTRIES = [
    (r"\bBC ?campus\b|British Columbia|\bOntario\b|\bAlberta\b|Manitoba|Saskatchewan|Qu[eé]bec|Nova Scotia|"
     r"New Brunswick|Newfoundland|\bCanad|Kwantlen|Douglas College|Camosun|Langara|Thompson Rivers|Vancouver|"
     r"Toronto|Ryerson|Toronto Metropolitan|Simon Fraser|Saskatoon|Calgary|Winnipeg|Halifax|Okanagan|Selkirk|"
     r"Fanshawe|Seneca|Humber|Conestoga|Algonquin College|Mohawk College|Sheridan College|George Brown", "Canada"),
    (r"\bAustralia|\bTAFE\b|Queensland|New South Wales|Victoria University|Monash|Melbourne|Sydney", "Australia"),
    (r"New Zealand|Aotearoa|Auckland|Wellington|Otago", "New Zealand"),
    (r"United Kingdom|\bUK\b|England|Scotland|Wales|Open University", "United Kingdom"),
    (r"\bIreland\b|Dublin|Galway|Limerick", "Ireland"),
    (r"South Africa|Cape Town|Johannesburg|Pretoria", "South Africa"),
]


def lt_country(entry):
    """The country a LibreTexts book was written in, from its affiliation and title ("United States" by default)."""
    words = f"{entry.get('affiliation') or ''} {entry.get('title') or ''} {entry.get('author') or ''}"
    return next((c for pattern, c in LT_COUNTRIES if re.search(pattern, words, re.I)), "United States")


def libretexts_book(entry, work, cache=None, left_out=None):
    """The Book of one LibreTexts catalogue entry, or None (said in left_out)."""
    left_out = left_out if left_out is not None else []
    title = " ".join((entry.get("title") or entry["bookID"]).split())
    licence, why = lt_licence(entry)
    if not licence or not B.licence_kind(licence):
        left_out.append({"title": f"LibreTexts: {title}", "reason": f"Not repackaged: {why or licence}."})
        return None
    pdf_url = (entry.get("links") or {}).get("pdf") or \
        f"https://downloads.libretexts.org/api/v1/download/{entry['bookID']}/pdf"
    if not B.allowed_by_robots(pdf_url, cache):
        left_out.append({"title": f"LibreTexts: {title}", "reason": "robots.txt does not allow its PDF."})
        return None
    local = download(pdf_url, os.path.join(work, "libretexts", f"{entry['bookID']}.pdf"))
    text_pages = pdf_text_pages(local)
    if not text_pages:
        left_out.append({"title": f"LibreTexts: {title}", "reason": "Its PDF could not be read."})
        return None
    library = entry.get("library", "")
    campus = (entry.get("shelfPath") or "").startswith("Courses/") or entry.get("location") == "campus"
    group = "k12" if library == "k12" else ("course" if campus else "textbooks")
    who = ", ".join(x for x in (entry.get("author"), entry.get("affiliation")) if x)
    book = B.Book(
        name=f"libretexts_{entry['bookID'].replace('-', '_')}", title=f"{title} (LibreTexts)",
        subject=entry.get("subject") or LT_LIBRARIES.get(library, "General"),
        level="school" if library == "k12" else "college", group=group,
        publisher="LibreTexts" + (f" ({entry.get('affiliation')})" if entry.get("affiliation") else ""),
        country=lt_country(entry), licence=licence, licence_url=licence_address(licence),
        source=(entry.get("links") or {}).get("online") or "https://commons.libretexts.org/",
        language="spa" if library == "espanol" else "eng", authors=entry.get("author") or "",
        description=(" ".join((entry.get("summary") or "").split())[:600] or
                     f"A LibreTexts {'course' if campus else 'textbook'} in {LT_LIBRARIES.get(library, library)}") +
                    (f" By {who}." if who else ""),
        original_pdf={"url": pdf_url, "size": os.path.getsize(local), "sha256": B.file_sha256(local)},
        grades="K-12" if library == "k12" else "College", personal_use=is_personal(licence),
        published=B.iso_date(entry.get("lastUpdated") or ""),
        version=f"LibreTexts build of {B.iso_date(entry.get('lastUpdated') or '') or 'unknown date'}",
        changes="its full PDF made into web pages again, one per page of the online book, each with its own licence "
                "line")
    for i, (page_title, page_licence, authors, body) in enumerate(lt_pages(text_pages), 1):
        book.pages.append(B.Page(f"p{i}-{B.slug(page_title, 40)}", page_title, body, 0))
    return book


def libretexts_books(piece, work, cache=None, left_out=None, only=None, deadline=None):
    """The Books of one LibreTexts piece ("chem-3")."""
    if not B.allowed_by_robots(LT_CATALOGUE, cache):
        left_out.append({"title": "LibreTexts", "reason": "robots.txt does not allow its catalogue."})
        return [], None, None
    # downloads.libretexts.org allows 100 requests an hour (its x-ratelimit headers): one book every 40 seconds.
    B.CRAWL_DELAY["downloads.libretexts.org"] = LT_PAUSE
    chosen = [b for b in lt_catalogue() if lt_in_piece(b, piece) and (not only or b["bookID"] in only)]
    chosen.sort(key=lambda b: b["bookID"])
    return chosen, (lambda e: libretexts_book(e, work, cache, left_out)), \
        (lambda e: " ".join((e.get("title") or e["bookID"]).split()))


# ====================================================================== Kolibri Studio public channels

STUDIO = "https://studio.learningequality.org"
STUDIO_CHANNELS = STUDIO + "/api/public/v1/channels?keyword=&language=en"
# Each channel: its id, the books' group, country, publisher, the licences allowed from it, whether its books are
# personal use only, and its pieces (top-level topic titles, "" for the whole channel in one piece); book_level 1:
# each top-level topic is a book; 2: each topic below a top-level one is a book.
KOLIBRI = {
    "bccampus": dict(short="BCcampus", id="d288129b13ce437f9e5150ad72d7b476", title="BCcampus Open Textbooks", group="course",
                     country="Canada", publisher="BCcampus (British Columbia, Canada)", personal=False,
                     pieces=[""], book_level=1, level="college",
                     source="https://collection.bccampus.ca/"),
    "khan": dict(short="Khan Academy", id="c9d7f950ab6b5a1199e3d6c10d7f0103", title="Khan Academy (English - US curriculum)",
                 group="course", country="United States", publisher="Khan Academy", personal=True,
                 pieces=["Math", "Math by grade", "Science & Engineering", "Economics", "Arts and humanities",
                         "English Language Arts", "Life skills", "Khan for Educators"], book_level=2,
                 k12_topics=["Math by grade", "English Language Arts"],
                 level="school", source="https://www.khanacademy.org/ (read only through Kolibri Studio)"),
    "ck12": dict(short="CK-12", id="1d8f6d84618153c18c695d85074952a7", title="CK-12", group="k12", country="United States",
                 publisher="CK-12 Foundation", personal=True, pieces=["Math", "Science", "English"], book_level=2,
                 level="school", source="https://www.ck12.org/ (read only through Kolibri Studio)"),
    "engageny": dict(short="EngageNY", id="d6e3b856125f5e6aa5fb40c8b112d5e9", title="EngageNY (en)", group="k12",
                     country="United States", publisher="New York State Education Department (EngageNY)",
                     personal=True, pieces=None, book_level=1, level="school",
                     source="https://www.nysed.gov/curriculum-instruction (read through Kolibri Studio)"),
}
ENGAGENY_PIECES = (["Prekindergarten", "Kindergarten"] + [f"Grade {g}" for g in range(1, 13)])
ENGAGENY_TOPICS = [f"{g} English Language Arts" for g in ENGAGENY_PIECES] + \
    [f"{g} Mathematics" for g in ENGAGENY_PIECES[:10]] + ["Algebra I", "Geometry", "Algebra II",
                                                         "Precalculus and Advanced Topics"]
KOLIBRI["engageny"]["pieces"] = ENGAGENY_TOPICS


def kolibri_pieces(name=None):
    """Every Kolibri piece key ("khan:math", "bccampus"), of one channel when name is given."""
    out = []
    for key, spec in KOLIBRI.items():
        if name and key != name:
            continue
        for topic in spec["pieces"]:
            out.append(f"{key}:{B.slug(topic)}" if topic else key)
    return out


def kolibri_db(spec, work, version=""):
    """An open connection to the channel's SQLite file (downloaded into work once for each channel version)."""
    url = f"{STUDIO}/content/databases/{spec['id']}.sqlite3"
    path = os.path.join(work, "kolibri", f"{spec['id']}-v{version}.sqlite3" if version else
                        f"{spec['id']}-{datetime.date.today():%Y-%m-%d}.sqlite3")
    download(url, path)
    return sqlite3.connect(path)


def kolibri_channel_info(spec, cache=None):
    """The channel's entry in Studio's public list ({version, last_published, ...}), {} when not listed."""
    try:
        channels = json.loads(memo_fetch(STUDIO_CHANNELS))
    except (urllib.error.URLError, OSError, ValueError):
        return {}
    return next((c for c in channels if c.get("id") == spec["id"]), {})


def kolibri_file_url(checksum, ext):
    """The address of a file in Studio's storage."""
    return f"{STUDIO}/content/storage/{checksum[0]}/{checksum[1]}/{checksum}.{ext}"


def kolibri_files(db, node_id):
    """{preset: [(checksum, extension, language)]} of one resource."""
    out = {}
    for preset, checksum, ext, lang in db.execute(
            "select f.preset, f.local_file_id, l.extension, f.lang_id from content_file f join content_localfile l "
            "on l.id = f.local_file_id where f.contentnode_id = ? order by f.priority", (node_id,)):
        out.setdefault(preset, []).append((checksum, ext, lang or ""))
    return out


def kolibri_resource_pages(db, node, work, number, unit, counts, cache=None):
    """[B.Page] of one Kolibri resource (node: id, title, kind, description, author, licence), counting what was
    left out in counts."""
    node_id, title, kind, description, author = node[:5]
    files = kolibri_files(db, node_id)
    path = f"r-{node_id[:12]}"
    intro = f"<p>{B.esc(' '.join((description or '').split()))}</p>" if description else ""
    if author:
        intro += f"<p>By {B.esc(author)}.</p>"
    if kind == "document":
        for checksum, ext, _lang in files.get("document", []) + files.get("epub", []):
            if ext == "pdf":
                local = download(kolibri_file_url(checksum, ext), os.path.join(work, "kolibri", "files",
                                                                               f"{checksum}.pdf"))
                pages = pdf_pages_as_pages(local, path, title, number, unit)
                os.remove(local)
                if pages:
                    pages[0].body = intro + pages[0].body
                    return pages
            if ext == "epub":
                data = B.fetch(kolibri_file_url(checksum, ext), None, binary=True)
                body = epub_html(data)
                if body:
                    return [B.Page(path, title, intro + body, number, unit)]
        counts["unreadable documents"] = counts.get("unreadable documents", 0) + 1
        return []
    if kind == "video":
        subs = files.get("video_subtitle", [])
        sub = next((s for s in subs if s[2].startswith("en")), subs[0] if subs else None)
        if not sub:
            counts["videos without subtitles"] = counts.get("videos without subtitles", 0) + 1
            return []
        words = vtt_text(B.fetch(kolibri_file_url(sub[0], sub[1]), cache, binary=True))
        if not words:
            counts["videos without subtitles"] = counts.get("videos without subtitles", 0) + 1
            return []
        return [B.Page(path, f"{title} (video transcript)", intro + "<h2>Transcript</h2>" + paragraphs_html(words),
                       number, unit)]
    if kind == "html5" and re.search(r"\((PLIX|Simulation|Interactive)\)\s*$", title or ""):
        counts["interactive pages without text"] = counts.get("interactive pages without text", 0) + 1
        return []                                  # CK-12's PLIX: a picture to drag and a question, no reading text
    if kind == "html5":
        for checksum, ext, _lang in files.get("html5_zip", []):
            data = B.fetch(kolibri_file_url(checksum, ext), None, binary=True)
            try:
                z = zipfile.ZipFile(io.BytesIO(data))
                names = [n for n in z.namelist() if n.lower().endswith((".html", ".htm"))]
                main = "index.html" if "index.html" in names else (names[0] if names else "")
                raw = z.read(main).decode("utf-8", "replace") if main else ""
            except (zipfile.BadZipFile, KeyError):
                raw = ""
            body = html_text_page(raw, "", latex=True) if raw else ""
            if len(re.sub(r"<[^>]+>", "", body).strip()) > 200:
                return [B.Page(path, title, intro + body, number, unit)]
        counts["interactive pages without text"] = counts.get("interactive pages without text", 0) + 1
        return []
    counts[{"exercise": "exercises", "h5p": "interactive H5P items"}.get(kind, f"{kind} items")] = \
        counts.get({"exercise": "exercises", "h5p": "interactive H5P items"}.get(kind, f"{kind} items"), 0) + 1
    return []


def epub_html(data):
    """The cleaned text of an EPUB's chapters (in its spine order), "" when it cannot be read."""
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        container = z.read("META-INF/container.xml").decode("utf-8", "replace")
        opf_path = re.search(r'full-path="([^"]+)"', container).group(1)
        opf = z.read(opf_path).decode("utf-8", "replace")
        items = {}
        for tag in re.findall(r"<item\b[^>]*>", opf):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', tag))
            if attrs.get("id") and attrs.get("href"):
                items[attrs["id"]] = attrs["href"]
        spine = re.findall(r'<itemref\b[^>]*\bidref="([^"]+)"', opf)
        base = os.path.dirname(opf_path)
        parts = []
        for ref in spine:
            href = items.get(ref)
            if href:
                raw = z.read(os.path.normpath(os.path.join(base, urllib.parse.unquote(href))).replace("\\", "/"))
                parts.append(html_text_page(raw.decode("utf-8", "replace")))
        return "\n".join(parts)
    except (zipfile.BadZipFile, KeyError, AttributeError):
        return ""


def kolibri_books(name, topic_slug, work, cache=None, left_out=None, only=None):
    """(items, make, label) of one Kolibri piece: items are the book topics, make(item) builds one Book."""
    spec = KOLIBRI[name]
    url = f"{STUDIO}/content/databases/{spec['id']}.sqlite3"
    if not B.allowed_by_robots(url, cache):
        left_out.append({"title": spec["title"], "reason": "robots.txt does not allow Kolibri Studio's channel file."})
        return [], None, None
    info = kolibri_channel_info(spec, cache)
    db = kolibri_db(spec, work, str(info.get("version") or ""))
    meta = db.execute("select version, last_updated from content_channelmetadata").fetchone() or (None, None)
    version = info.get("version") or meta[0]
    published = B.iso_date(info.get("last_published") or str(meta[1] or ""))
    root = db.execute("select id from content_contentnode where parent_id is null").fetchone()[0]
    tops = db.execute("select id, title from content_contentnode where parent_id = ? and kind = 'topic' order by "
                      "sort_order", (root,)).fetchall()
    if topic_slug:
        tops = [t for t in tops if B.slug(t[1]) == topic_slug]
        if not tops:
            left_out.append({"title": f"{spec['title']}: {topic_slug}", "reason": "The channel no longer has this "
                             "topic."})
            return [], None, None
    if spec["book_level"] == 2:
        items = []
        for top_id, top_title in tops:
            items += [(i, t, top_title) for i, t in db.execute(
                "select id, title from content_contentnode where parent_id = ? and kind = 'topic' order by sort_order",
                (top_id,))]
    else:
        items = [(i, t, "") for i, t in tops]
    if only:
        items = [x for x in items if any(o.lower() in x[1].lower() for o in only)]

    def make(item):
        """The Book of one topic of the channel."""
        node_id, title, parent_title = item
        lft, rght, tree = db.execute("select lft, rght, tree_id from content_contentnode where id = ?",
                                     (node_id,)).fetchone()
        rows = db.execute(
            "select id, title, kind, description, author, license_name, license_owner, parent_id, level from "
            "content_contentnode where tree_id = ? and lft > ? and rght < ? order by lft", (tree, lft, rght)).fetchall()
        level0 = db.execute("select level from content_contentnode where id = ?", (node_id,)).fetchone()[0]
        topics = {r[0]: r[1] for r in rows if r[2] == "topic"}
        parents = {r[0]: r[7] for r in rows}
        counts, licences, owners, pages = {}, [], set(), []
        originals = [{"url": f"{STUDIO}/content/databases/{spec['id']}.sqlite3", "kind": "sqlite"}]
        number = 0
        for r in rows:
            if r[2] == "topic":
                if r[8] == level0 + 1:
                    number += 1
                continue
            short = KOLIBRI_LICENCES.get(r[5] or "", ("", ""))[0]
            if not short:
                counts[f"items under \"{r[5] or 'no licence'}\""] = counts.get(
                    f"items under \"{r[5] or 'no licence'}\"", 0) + 1
                continue
            unit_id = r[7]                                     # the topic just below the book's own topic
            while parents.get(unit_id) not in (node_id, None):
                unit_id = parents[unit_id]
            unit = topics.get(unit_id, "")
            got = kolibri_resource_pages(db, r, work, max(number, 1), unit, counts, cache)
            if got:
                pages += got
                files = kolibri_files(db, r[0])           # the resource's own files are its originals
                originals.extend({"url": kolibri_file_url(c, ext), "kind": ext}
                                 for preset in ("document", "epub", "html5") for c, ext, _l in files.get(preset, []))
                licences.append(short)
                if r[6]:
                    owners.add(r[6])
        full = f"{parent_title}: {title}" if parent_title and parent_title != title else title
        licence = strictest(licences) or "CC BY"
        book = B.Book(
            name=f"kolibri_{name}_{B.slug(full, 50).replace('-', '_')}",
            title=f"{spec.get('short') or spec['publisher'].split(' (')[0]}: {full}", subject=parent_title or title, level=spec["level"],
            group="k12" if (spec["group"] == "k12" or parent_title in spec.get("k12_topics", [])) else
            spec["group"], publisher=spec["publisher"], country=spec["country"], licence=licence,
            licence_url=KOLIBRI_LICENCES.get(licence, ("", licence_address(licence)))[1] or licence_address(licence),
            source=spec["source"], personal_use=spec["personal"] or is_personal(licence),
            grades=grades_of(full) or grades_of(parent_title), published=published,
            version=f"Kolibri Studio channel \"{spec['title']}\" version {version}" if version else "",
            description=f"{full}, from the Kolibri Studio public channel \"{spec['title']}\" (Learning Equality's "
                        "offline package of the publisher's material). Documents are given as text, videos as their "
                        "transcripts." + (" Left out: " + "; ".join(f"{n} {what}" for what, n in sorted(counts.items()))
                                          + "." if counts else ""),
            notice=("Rights holders named in the channel: " + ", ".join(sorted(owners)) + ".") if owners else "",
            changes="its documents, transcripts and web pages made into web pages, one per resource")
        book.originals = originals
        book.pages = pages
        return book
    return items, make, (lambda item: f"{spec['title']}: {item[1]}")


# ====================================================================== MIT OpenCourseWare

OCW = "https://ocw.mit.edu"
OCW_SITEMAP = OCW + "/sitemap.xml"
OCW_MAX_ZIP = 4 * 10**9          # bytes: a course zip larger than this (one with its videos) is not read
# Buckets per department (2026-11-21: about 30 courses per bucket). Departments not named here are in "other".
OCW_BUCKETS = {"6": 8, "15": 6, "11": 6, "18": 6, "res": 5, "21l": 4, "2": 4, "12": 4, "21g": 3, "4": 3, "21h": 3,
               "17": 3, "9": 3, "24": 2, "8": 2, "14": 2, "1": 2, "16": 2, "21m": 2, "21a": 2, "3": 2, "hst": 2,
               "sts": 2, "22": 2, "mas": 2, "21w": 1, "5": 1, "20": 1, "esd": 1, "cms": 1, "es": 1, "7": 1, "10": 1,
               "wgs": 1, "ec": 1, "pe": 1, "ids": 1, "cc": 1}


def ocw_courses(cache=None):
    """Every course name of OpenCourseWare ("18-06-linear-algebra-spring-2010"), from its sitemap."""
    return re.findall(r"<loc>https://ocw\.mit\.edu/courses/([^/<]+)/sitemap\.xml</loc>", memo_fetch(OCW_SITEMAP))


def ocw_department(course):
    """The department part of a course name ("18", "21l", "res"); "other" for one not in OCW_BUCKETS."""
    dept = course.split("-")[0].lower()
    return dept if dept in OCW_BUCKETS else "other"


def ocw_pieces():
    """Every OpenCourseWare piece key ("ocw:18-2", "ocw:other-0")."""
    return [f"ocw:{d}-{k}" for d, n in OCW_BUCKETS.items() for k in range(n)] + ["ocw:other-0"]


def ocw_in_piece(course, piece):
    """True when a course belongs to piece ("18-2")."""
    dept, _, k = piece.rpartition("-")
    return ocw_department(course) == dept and bucket(course, OCW_BUCKETS.get(dept, 1)) == int(k)


OCW_ZIPS = {}                    # {course: the address of its offline zip}, filled by ocw_zip


def ocw_zip(course, work, cache=None):
    """The local copy of a course's offline zip (its download page names it), or "" when it has none."""
    page = f"{OCW}/courses/{course}/download/"
    m = re.search(r'href="([^"]+\.zip)"', B.fetch(page, None))          # fresh: the zip's name changes
    if not m:
        return ""
    url = urllib.parse.urljoin(page, m.group(1))
    OCW_ZIPS[course] = url                     # its address, for the book's "originals"
    if B.head_size(url) > OCW_MAX_ZIP:
        return "too big"
    return download(url, os.path.join(work, "ocw", f"{course}.zip"))


def ocw_book(course, work, cache=None, left_out=None):
    """The Book of one OpenCourseWare course, or None (said in left_out)."""
    path = ocw_zip(course, work, cache)
    if path == "too big":
        left_out.append({"title": f"MIT OpenCourseWare {course}", "reason": "Its offline zip is larger than "
                         f"{OCW_MAX_ZIP // 10**9} GB (it holds its videos), more than a build machine can hold."})
        return None
    if not path:
        left_out.append({"title": f"MIT OpenCourseWare {course}", "reason": "Its download page names no zip."})
        return None
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        left_out.append({"title": f"MIT OpenCourseWare {course}", "reason": "Its zip could not be opened."})
        return None
    names = set(z.namelist())
    root = next((n.rsplit("data.json", 1)[0] for n in sorted(names, key=len) if n.endswith("data.json")), "")
    meta = json.loads(z.read(root + "data.json"))
    title = " ".join((meta.get("course_title") or course).split())
    number = meta.get("primary_course_number", "")
    term = " ".join(x for x in (meta.get("term"), meta.get("year")) if x)
    full = f"MIT {number} {title}" + (f" ({term})" if term else "")
    instructors = ", ".join(i.get("title", "") for i in meta.get("instructors", []))
    topics = [t[-1] for t in meta.get("topics", []) if t]
    licences, pages, counts = [], [], {}

    def allowed(lic):
        """The short licence of a resource's licence address, "" when not allowed."""
        short = B.licence_short("", lic or "https://creativecommons.org/licenses/by-nc-sa/4.0/")
        return short if B.licence_kind(short) else ""
    home = f"<p>{B.esc(' '.join((meta.get('course_description') or '').split()))}</p>"
    if instructors:
        home += f"<p>Instructors: {B.esc(instructors)}.</p>"
    if topics:
        home += f"<p>Topics: {B.esc(', '.join(topics))}.</p>"
    pages.append(B.Page("course-home", "Course home", home, 1, ""))
    page_dirs = sorted({n.split("/")[-2] for n in names if re.match(re.escape(root) + r"pages/[^/]+/data\.json$", n)})
    for d in page_dirs:
        data = json.loads(z.read(f"{root}pages/{d}/data.json"))
        short = allowed(data.get("license"))
        if not short:
            counts["pages under another licence"] = counts.get("pages under another licence", 0) + 1
            continue
        body = B._Cleaner({}, f"{OCW}/courses/{course}/").clean(B.mathml_spans(data.get("content") or ""))
        body = re.sub(r"\{\{[%<].*?[%>]\}\}", "", body)                # Hugo shortcodes left in the text
        if len(re.sub(r"<[^>]+>", "", body).strip()) < 20:
            continue
        licences.append(short)
        pages.append(B.Page(f"page-{B.slug(d, 40)}", data.get("title") or d, body, 2, "Course pages"))
    resources = []
    for n in sorted(names):
        if re.match(re.escape(root) + r"resources/[^/]+/data\.json$", n):
            data = json.loads(z.read(n))
            resources.append((data.get("parent_title") or "Resources", data.get("title") or n.split("/")[-2], n, data))
    resources.sort(key=lambda r: (r[0], [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", r[1])]))
    for k, (parent, rtitle, n, data) in enumerate(resources, 1):
        short = allowed(data.get("license"))
        if not short:
            counts["resources under another licence"] = counts.get("resources under another licence", 0) + 1
            continue
        if re.match(r"3play\b", rtitle or "", re.I):
            continue                                   # a video's caption or transcript file: read with its video
        file = (data.get("file") or "").rsplit("/", 1)[-1]
        local = f"{root}static_resources/{file}" if file else ""
        described = " ".join((data.get("description") or "").split())
        if re.match(r"This resource is (a|the) transcript", described, re.I):
            continue                                   # the same words as its video's captions, read with the video
        short_words = re.sub(r"^This (resource|file) (contains|includes|is)\s+(information related to\s+)?", "",
                             described, flags=re.I).rstrip(".")
        heading = (short_words[:1].upper() + short_words[1:]) if short_words and len(short_words) < 120 else \
            os.path.splitext(rtitle)[0]
        if data.get("resourcetype") == "Document" and local in names and file.lower().endswith(".pdf"):
            tmp = os.path.join(work, "ocw", "tmp.pdf")
            with open(tmp, "wb") as f:
                f.write(z.read(local))
            got = pdf_pages_as_pages(tmp, f"res-{k}", heading, 3, parent)
            if got:
                licences.append(short)
                pages += got
            else:
                counts["scanned or empty PDFs"] = counts.get("scanned or empty PDFs", 0) + 1
            continue
        if data.get("resourcetype") == "Video":
            vf = data.get("video_files") or {}
            cands = [(x.get("file") or "") for x in (vf.get("video_captions_resources") or [])
                     if (x.get("language") or "en").startswith("en")] + [vf.get("video_captions_file") or ""] + \
                [(x.get("file") or "") for x in (vf.get("video_transcript_resources") or [])
                 if (x.get("language") or "en").startswith("en")] + [vf.get("video_transcript_file") or ""]
            words = ""
            for cand in [c.rsplit("/", 1)[-1] for c in cands if c]:
                full_name = f"{root}static_resources/{cand}" if cand else ""
                if full_name in names and cand.lower().endswith((".vtt", ".srt", ".webvtt")):
                    words = vtt_text(z.read(full_name))
                    break
                if full_name in names and cand.lower().endswith(".pdf"):
                    tmp = os.path.join(work, "ocw", "tmp.pdf")
                    with open(tmp, "wb") as f:
                        f.write(z.read(full_name))
                    words = "\n\n".join(pdf_text_pages(tmp))
                    break
            if words:
                licences.append(short)
                pages.append(B.Page(f"res-{k}", f"{rtitle} (video transcript)",
                                    (f"<p>{B.esc(described)}</p>" if described else "") + paragraphs_html(words), 3,
                                    parent))
            else:
                counts["videos without a transcript"] = counts.get("videos without a transcript", 0) + 1
    licence = strictest(licences) or "CC BY-NC-SA 4.0"
    if licence == "CC BY-NC-SA":
        licence = "CC BY-NC-SA 4.0"
    level = ", ".join(meta.get("level") or [])
    book = B.Book(
        name=f"mit_ocw_{B.slug(course, 70).replace('-', '_')}", title=full, subject=topics[0] if topics else title,
        level="college", group="course", publisher="MIT OpenCourseWare, Massachusetts Institute of Technology",
        country="United States", licence=licence, licence_url=licence_address(licence),
        source=f"{OCW}/courses/{course}/", authors=instructors, personal_use=True,
        grades=f"College ({level.lower()})" if level else "College", published=str(meta.get("year") or ""),
        version="MIT OpenCourseWare course zip of %04d-%02d-%02d" % z.getinfo(root + "data.json").date_time[:3],
        description=f"{full}: the course's pages, lecture notes, assignments and exams as text, and its video "
                    f"transcripts. {' '.join((meta.get('course_description') or '').split())[:400]}" +
                    (" Left out: " + "; ".join(f"{v} {w}" for w, v in sorted(counts.items())) + "." if counts else ""),
        notice="MIT OpenCourseWare material is licensed CC BY-NC-SA 4.0 unless a resource says otherwise; "
               "third-party material in a course is the copyright of its owners.",
        changes="the course's offline pages and PDFs made into web pages, with formulas and transcripts as text")
    if OCW_ZIPS.get(course):                    # the course's own offline zip is its original
        book.originals.append({"url": OCW_ZIPS[course], "kind": "zip", "size": os.path.getsize(path),
                               "sha256": B.file_sha256(path)})
    book.pages = pages
    return book


def ocw_books(piece, work, cache=None, left_out=None, only=None):
    """(items, make, label) of one OpenCourseWare piece ("18-2")."""
    if not B.allowed_by_robots(OCW_SITEMAP, cache):
        left_out.append({"title": "MIT OpenCourseWare", "reason": "robots.txt does not allow its pages."})
        return [], None, None
    items = [c for c in ocw_courses(cache) if ocw_in_piece(c, piece) and (not only or any(o in c for o in only))]
    return items, (lambda c: ocw_book(c, work, cache, left_out)), (lambda c: f"MIT OpenCourseWare {c}")


# ====================================================================== Core Knowledge

CKF = "https://www.coreknowledge.org"
CKF_SITEMAPS = [f"{CKF}/library-sitemap{n}.xml" for n in (1, 2, 3)]
CKF_BUCKETS = 15
CKF_LICENCE = re.compile(r"Creative\s+Commons\s+Attribution\s*-?\s*Non\s*-?\s*Commercial\s*-?\s*Share\s*-?\s*Alike"
                         r"\s*(\d\.\d)?", re.I)


def ckf_resources(cache=None):
    """[(address, lastmod)] of every free resource of the Core Knowledge library (its library sitemaps)."""
    out = []
    for sm in CKF_SITEMAPS:
        try:
            text = memo_fetch(sm)
        except urllib.error.HTTPError:
            continue
        out += re.findall(r"<loc>\s*(https://www\.coreknowledge\.org/free-resource/[^<\s]+)\s*</loc>\s*"
                          r"(?:<lastmod>\s*([^<\s]+))?", text)
    return out


def ckf_pieces():
    """Every Core Knowledge piece key ("coreknowledge:3")."""
    return [f"coreknowledge:{k}" for k in range(CKF_BUCKETS)]


def ckf_book(item, work, cache=None, left_out=None):
    """The Book of one Core Knowledge free resource (its page and PDFs), or None (said in left_out)."""
    url, lastmod = item
    if not B.allowed_by_robots(url, cache):
        left_out.append({"title": url, "reason": "robots.txt does not allow the page."})
        return None
    page = B.fetch(url, None)
    m = re.search(r'<meta property="og:title" content="([^"]+)"', page) or re.search(r"<title>([^<]+)", page)
    title = re.sub(r"\s*[-|–]\s*Core Knowledge Foundation\s*$", "", " ".join(html.unescape(m.group(1)).split())) \
        if m else url.rstrip("/").rsplit("/", 1)[-1]
    pdfs = list(dict.fromkeys(u for u in re.findall(r'href="(https://www\.coreknowledge\.org/wp-content/uploads/[^"]+'
                                                    r'\.pdf)"', page)))
    if not pdfs:
        left_out.append({"title": f"Core Knowledge: {title}", "reason": "Its page links no PDF."})
        return None
    pages, version, checked, originals = [], "", None, []
    for k, pdf in enumerate(pdfs, 1):
        local = download(pdf, os.path.join(work, "coreknowledge", hashlib.sha256(pdf.encode()).hexdigest()[:24] +
                                           ".pdf"))
        front = " ".join(" ".join(pdf_text_pages(local)[:8]).split())
        m = CKF_LICENCE.search(front)
        if not m:
            left_out.append({"title": f"Core Knowledge: {title}: {pdf.rsplit('/', 1)[-1]}", "reason": "Its PDF does "
                             "not state the Creative Commons Attribution-NonCommercial-ShareAlike licence."})
            os.remove(local)
            continue
        checked = m.group(1) or checked or "4.0"
        version = B.pdf_date(local) or version
        name = os.path.splitext(urllib.parse.unquote(pdf.rsplit("/", 1)[-1]))[0].replace("_", " ")
        pages += pdf_pages_as_pages(local, f"pdf-{k}", name, k, "")
        originals.append({"url": pdf, "kind": "pdf", "size": os.path.getsize(local), "sha256": B.file_sha256(local)})
        os.remove(local)
    if not pages:
        return None
    licence = f"CC BY-NC-SA {checked}"
    book = B.Book(
        name=f"core_knowledge_{B.slug(url.rstrip('/').rsplit('/', 1)[-1], 60).replace('-', '_')}",
        title=f"Core Knowledge: {title}", subject="Language arts" if re.search(r"ckla|language arts|reading", title,
                                                                                re.I) else "History, geography and science",
        level="school", group="k12", publisher="Core Knowledge Foundation", country="United States",
        licence=licence, licence_url=licence_address(licence), source=url, personal_use=True,
        grades=grades_of(title), published=B.iso_date(lastmod or "") or version, version=version and f"PDF of {version}",
        description=f"{title}: the Core Knowledge Foundation's free materials ({len(pdfs)} PDF files) as text; "
                    "personal use only.",
        notice="Core Knowledge materials are licensed under a Creative Commons Attribution-NonCommercial-ShareAlike "
               "licence; Core Knowledge®, Core Knowledge Curriculum Series™ and CKLA are trademarks of the Core "
               "Knowledge Foundation.")
    book.originals = originals
    book.pages = pages
    return book


def ckf_books(piece, work, cache=None, left_out=None, only=None):
    """(items, make, label) of one Core Knowledge piece."""
    items = [r for r in ckf_resources(cache) if bucket(r[0], CKF_BUCKETS) == int(piece) and
             (not only or any(o in r[0] for o in only))]
    return items, (lambda r: ckf_book(r, work, cache, left_out)), (lambda r: r[0])


# ====================================================================== keys, signs, the build

SOURCES = {
    "libretexts": dict(title="LibreTexts", release=lambda piece: f"libretexts-{piece.rpartition('-')[0]}"),
    "bccampus": dict(title="BCcampus Open Textbooks (Kolibri)", release=lambda piece: "courses-bccampus"),
    "khan": dict(title="Khan Academy (Kolibri)", release=lambda piece: "personal-khan-academy"),
    "ck12": dict(title="CK-12 (Kolibri)", release=lambda piece: "personal-ck12"),
    "engageny": dict(title="EngageNY (Kolibri)", release=lambda piece: "personal-engageny"),
    "ocw": dict(title="MIT OpenCourseWare", release=lambda piece: f"personal-ocw-{piece.rpartition('-')[0]}"),
    "coreknowledge": dict(title="Core Knowledge", release=lambda piece: "personal-core-knowledge"),
}
OPEN = ["libretexts", "bccampus"]
PERSONAL = ["khan", "ck12", "engageny", "ocw", "coreknowledge"]
GROUP_NOTES = {"course": "Courses: open college and career courses (LibreTexts, BCcampus, the US Navy's training "
                         "courses) and, marked \"personal use only\", MIT OpenCourseWare and Khan Academy.",
               "k12": "School books from kindergarten to grade 12. Those marked \"personal use only\" are under a "
                      "non-commercial licence: for your own reading and study."}


def source_pieces(name):
    """Every piece key of one source ("libretexts:chem-3", "bccampus", "khan:math")."""
    if name == "libretexts":
        return lt_pieces()
    if name == "ocw":
        return ocw_pieces()
    if name == "coreknowledge":
        return ckf_pieces()
    return kolibri_pieces(name)


def expand_keys(words):
    """The build keys (course:...) the words stand for: opencourses, personaluse, k12 (the K-12 pieces of this
    module only: CK-12, EngageNY, Core Knowledge, Khan Academy's maths by grade), course:<source> or
    course:<source>:<piece>."""
    keys = []
    for w in words:
        if w == "opencourses":
            names = OPEN
        elif w == "personaluse":
            names = PERSONAL
        elif w == "k12":
            keys += [f"course:{p}" for p in source_pieces("ck12") + source_pieces("engageny") +
                     source_pieces("coreknowledge")] + ["course:khan:math-by-grade"]
            continue
        elif w.startswith("course:") and w.count(":") == 1:
            names = [w[7:]]
        else:
            keys.append(w)
            continue
        for name in names:
            keys += [f"course:{p}" for p in source_pieces(name)]
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change of a key ("" when it cannot be asked: then nothing is rebuilt): the
    LibreTexts books of the piece with their dates of last change; the Kolibri channel's version; the courses of an
    OpenCourseWare piece (and the quarter of the year, so every course is read again four times a year); the Core
    Knowledge resources of the piece with their sitemap dates."""
    parts = key.split(":")
    name, piece = parts[1], (parts[2] if len(parts) > 2 else "")
    try:
        if name == "libretexts":
            rows = sorted((b["bookID"], b.get("lastUpdated", ""), b.get("license", "")) for b in lt_catalogue()
                          if lt_in_piece(b, piece))
            return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:24]
        if name in KOLIBRI:
            info = kolibri_channel_info(KOLIBRI[name])
            return f"kolibri-{info['version']}" if info.get("version") else ""
        if name == "ocw":
            today = datetime.date.today()
            rows = sorted(c for c in ocw_courses() if ocw_in_piece(c, piece))
            return hashlib.sha256(json.dumps([rows, f"{today.year}-Q{(today.month - 1) // 3 + 1}"]).encode()
                                  ).hexdigest()[:24]
        if name == "coreknowledge":
            rows = sorted(r for r in ckf_resources() if bucket(r[0], CKF_BUCKETS) == int(piece))
            return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:24]
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return ""
    return ""


def books_plan(key, work, cache=None, left_out=None, only=None):
    """(items, make, label) of one key: the things to make books of, the function that makes one, and its name."""
    parts = key.split(":")
    name, piece = parts[1], (parts[2] if len(parts) > 2 else "")
    if name == "libretexts":
        return libretexts_books(piece, work, cache, left_out, only)
    if name == "ocw":
        return ocw_books(piece, work, cache, left_out, only)
    if name == "coreknowledge":
        return ckf_books(piece, work, cache, left_out, only)
    if name in KOLIBRI:
        return kolibri_books(name, piece, work, cache, left_out, only)
    raise KeyError(f"unknown course source {name}")


def build_courses(keys, out_dir, cache=None, date=None, only=None):
    """Build the books of keys into out_dir, write manifest-<key>.json for each (as build_textbooks.build does) and
    return {key: manifest}. Every book is a new version (versioned file names); only: just these items (book ids,
    course names, topic words), a test build whose manifest is named "..._sample"."""
    manifests = {}
    os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(cache or out_dir, "work")
    for key in expand_keys(keys):
        name = key.split(":")[1]
        piece = key.split(":")[2] if key.count(":") > 1 else ""
        release = SOURCES.get(name, {}).get("release", lambda p: "textbooks")(piece)
        left_out, entries = [], []
        start = time.monotonic()
        fingerprint = sign(key) if not only else ""
        try:
            items, make, label = books_plan(key, work, cache, left_out, only)
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            items, make, label = [], None, None
        for n, item in enumerate(items):
            if time.monotonic() - start > TIME_BUDGET:
                rest = [label(x) for x in items[n:]]
                left_out.append({"title": key, "reason": f"The time for one build ran out; not built this time "
                                 f"({len(rest)}): " + "; ".join(rest[:50]) + ("..." if len(rest) > 50 else "")})
                break
            try:
                book = make(item)
            except Exception as e:  # noqa: BLE001 - one book's failure does not stop the others
                left_out.append({"title": label(item), "reason": f"It could not be read ({e})."})
                book = None
            if book is None:
                continue
            if len(book.pages) < 1:
                left_out.append({"title": book.title, "reason": "No pages could be read."})
                continue
            entry = B.write_book(book, out_dir, date, versioned=True)
            entry.update({"key": key, "fingerprint": fingerprint, "release": release,
                          "url": f"{B.RELEASE.rsplit('/', 1)[0]}/{release}/{entry['file']}"})
            print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, {entry['licence_text']}")
            entries.append(entry)
            if name == "libretexts" or name == "ocw":
                for f in os.listdir(os.path.join(work, name)) if os.path.isdir(os.path.join(work, name)) else []:
                    os.remove(os.path.join(work, name, f))        # keep the build machine's disk free
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": release, "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if only else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "libretexts": "LibreTexts' Commons catalogue gives each book's licence (\"license\": \"ccby\", with "
                  "\"licenseversion:40\" in its tags), and every page of its PDF ends \"This page titled ... is shared "
                  "under a CC BY license and was authored, remixed, and/or curated by ...\"; books with no licence, "
                  "mixed licences, all rights reserved, CK-12's licence, GNU licences or no-derivatives licences are "
                  "left out. downloads.libretexts.org has no robots.txt (all allowed); commons.libretexts.org's "
                  "robots.txt allows all.",
    "kolibri": "Kolibri Studio's public channel files give each resource's licence (\"license_name\": \"CC BY\", "
               "\"CC BY-NC-SA\" ...; \"Special Permissions\" and no-derivatives items are left out). "
               "studio.learningequality.org has no robots.txt. BCcampus Open Textbooks: CC BY, CC BY-NC and CC "
               "BY-NC-SA per book. Khan Academy: videos CC BY-NC-SA (exercises \"Special Permissions\": left out). "
               "CK-12: CC BY-NC. EngageNY: CC BY-NC-SA.",
    "mit_ocw": "Each OpenCourseWare resource's data.json: \"license\": \"https://creativecommons.org/licenses/by-nc-sa/"
               "4.0/\"; ocw.mit.edu/robots.txt: \"User-Agent: * Allow: /\".",
    "core_knowledge": "Each Core Knowledge PDF's copyright page: \"This work is licensed under a Creative Commons "
                      "Attribution-NonCommercial-ShareAlike 4.0 International License\" (checked in every PDF); its "
                      "robots.txt disallows only /CK/, /CKproto2/ and shop addresses.",
}

# The Kiwix library's own books that cover sources of this module (the toolkit lists them from the Kiwix catalogue):
# {Kiwix book name: label}, for the toolkit to show "personal use only" beside them.
KIWIX_LABELS = {
    "khanacademy_en_all": sources.PERSONAL_USE, "crashcourse_en_all": sources.PERSONAL_USE,
    "phet_en_all": "open (CC BY 4.0)",
    **{f"libretexts.org_en_{lib}": "licence differs per book (see LibreTexts' own pages)"
       for lib in ("bio", "biz", "chem", "eng", "geo", "human", "k12", "math", "med", "phys", "socialsci", "stats",
                   "workforce")},
}

NOT_INCLUDED = [
    ("SkillsCommons (US Department of Labor TAACCCT, CC BY)", "Its site (www.skillscommons.org, partner."
     "skillscommons.org) could not be reached with a verified secure connection from the build machine (its "
     "certificate could not be checked), so neither its robots.txt nor its licences could be read; tried again on "
     "2026-11-21."),
    ("BCcampus Open Textbooks website (opentextbc.ca, collection.bccampus.ca)", "Its robots.txt shuts out the "
     "automated readers of AI companies (ClaudeBot, anthropic-ai, Claude-Web, GPTBot and others) and its Content-"
     "Signal says ai-train=no, so the site is not read. The same books come from BCcampus' own Kolibri Studio "
     "channel (course:bccampus), which is a package made for offline use."),
    ("eCampusOntario Open Library books (ecampusontario.pressbooks.pub)", "The Pressbooks site that holds the books "
     "refuses automated requests (403, robots.txt included) and shuts out AI companies' readers; the catalogue "
     "site (openlibrary.ecampusontario.ca) links only there."),
    ("Washington State Open Course Library (opencourselibrary.org, CC BY 3.0)", "Its licence is stated (\"licensed "
     "under a Creative Commons Attribution 3.0 Unported License\"), but every course's files are in Google Drive "
     "folders, which can only be listed with Google's API key or a browser; not fetched."),
    ("OER Commons (all subjects, CTE, state K-12 hubs such as Oregon's and Washington OSPI's)", "www.oercommons.org "
     "refuses automated requests (403), robots.txt included, and shuts out AI companies' readers. Items it lists "
     "are added from their own hosts where those allow it (Illustrative Mathematics, Open Up Resources, Utah)."),
    ("Saylor Academy courses (learn.saylor.org, Saylor's own pages CC BY 3.0)", "Beyond each course's syllabus, the "
     "course pages are shown only to signed-in learners, and its course list is filled in by scripts; its older "
     "textbook copies (saylordotorg.github.io) are gone (404)."),
    ("TED-Ed (ed.ted.com, Kolibri channel \"TED-Ed Lessons\")", "ed.ted.com's robots.txt shuts out AI companies' "
     "readers (ClaudeBot, GPTBot); the Kolibri channel has the videos without subtitles and short quizzes only, "
     "under CC BY-NC-ND. TED's talks are in the Kiwix library (its TED collections)."),
    ("PhET Interactive Simulations (CC BY 4.0)", "Simulations, not text: already in the Kiwix library (phet_en_all), "
     "so nothing is built here."),
    ("OpenLearn and OpenLearn Create (The Open University)", "www.open.edu refuses automated requests (403) and "
     "shuts out AI companies' readers; no Kiwix book or Kolibri channel of it was found."),
    ("CK-12 website (www.ck12.org)", "Its robots.txt refuses automated readers (403) and shuts out AI companies' "
     "readers; CK-12 comes only from its Kolibri Studio channel (course:ck12), personal use only."),
    ("EngageNY website (www.nysed.gov)", "nysed.gov could not be reached with a verified secure connection from the "
     "build machine; EngageNY comes from its Kolibri Studio channel (course:engageny), personal use only."),
    ("Khan Academy website (khanacademy.org)", "Never read (its terms limit automated access): Khan Academy comes "
     "only from Learning Equality's Kolibri Studio channel (course:khan) and the Kiwix library's khanacademy_en_all, "
     "both personal use only. Its exercises are \"Special Permissions\" in the channel and are left out."),
    ("Open Up Resources: EL Education K-8, Bookworms, Odell HS Literacy, K-5 Math, Humanizing PreK-5 Math",
     "Each has its own licence (most CC BY-NC 4.0) and its own page layout; Open Up HS Math (personal use only) and "
     "its 6-8 Math (through Illustrative Mathematics, CC BY) are built. The others can be added to "
     "sources.K12_GUIDES one by one after their pages are checked."),
    ("Illustrative Mathematics K-5 student workbooks", "Published in print only; their family materials (CC BY) are "
     "built."),
    ("Open Polytechnic of New Zealand (Te Pūkenga)", "Its course material is for enrolled learners; no openly "
     "licensed course collection was found on its site (robots.txt read)."),
    ("Ako Aotearoa (New Zealand)", "Its resources are for tertiary teachers, mostly reports and guides with their "
     "own copyright; no openly licensed course books were found."),
    ("TAFE and other Australian open courses (CAUL OER Collective)", "TAFE course material is copyright; CAUL's "
     "Pressbooks site refuses automated requests (403) and shuts out AI companies' readers."),
    ("Irish and Scottish open resources (National Forum, Scoilnet, Scotland's colleges)", "No openly licensed course "
     "or school book collection with an automated download was found (Scoilnet and NCCA: no open licence)."),
    ("British Columbia K-12 resources", "BC's curriculum site publishes curriculum documents, not textbooks; BC "
     "Open Government Licence material found was not course books. BCcampus' adult upgrading books (course:"
     "bccampus) cover adult basic education."),
    ("State CTE curriculum centres (Oklahoma CareerTech, Texas CTE resource centre)", "Copyright (sold or for "
     "member schools); no open licence."),
    ("LibreTexts books without a usable licence", "About 1,100 of LibreTexts' 4,150 books state no licence, mixed or "
     "several licences, all rights reserved, CK-12's licence, a GNU licence or a no-derivatives licence; each is "
     "named in its piece's left_out."),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["opencourses"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--only", default="", help="build only these items (book ids, course names, topic words)")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    only = [x.strip() for x in a.only.split(",") if x.strip()] or None
    build_courses(a.keys, a.out, a.cache, only=only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
