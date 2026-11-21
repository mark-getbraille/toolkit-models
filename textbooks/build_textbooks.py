"""Build the textbooks of the Digital Accessibility Toolkit as ZIM files (one per book) and their catalogue entries.

The toolkit's Offline libraries window lists them in the collection "Textbooks" (its "Get more" list reads
textbooks.json from this repository's release "textbooks"), downloads the chosen ones, checks their SHA-256 and
size, and reads and searches them without the internet, like the Kiwix books. The files are ordinary ZIM files, so
the free Kiwix apps open them too.

What is built (sources.py lists every book, the licence lines checked by hand, and what was left out and why):
  osbooks    OpenStax textbooks (Rice University), from the openstax/osbooks-* repositories on GitHub (CNXML)
  siyavula   Siyavula's South African school textbooks (mathematics, physical and natural sciences), from its
             online reader
  dspace     reference works of international bodies (WHO, World Bank, FAO) from their open repositories (PDF)
  pdf        official PDF documents (sources.PDF_DOCS): US military field manuals with Distribution Statement A
             (survival, first aid, map reading, knots, hygiene, cold weather, mountaineering; key fieldmanuals) and
             Alberta's publications under its Open Government Licence (key government), US Navy nonresident
             training courses with Distribution Statement A (key courses) and UK Maritime and Coastguard Agency and
             Ministry of Defence guidance under the Open Government Licence v3.0; key pdf:<name> builds one
  nonprofit  reference works of non-profit organisations published as openly licensed web guides (sources.NONPROFIT:
             the EFF's Surveillance Self-Defense, People's Law School, the W3C WAI Curricula); key nonprofit:<name>
             builds one
  guide      government web guides in the public domain or under the Open Government Licence (sources.GOV_GUIDES:
             Section508.gov, ADA.gov, Ask CFPB, NIDDK, FDA, NCI, the NHS Health A to Z, GOV.UK, the Highway Code);
             key guides, or guide:<name>
  law        laws and regulations (sources.LAWS): US Code chapters and CFR parts from govinfo.gov (public domain),
             Canada's federal laws from Justice Laws (Reproduction of Federal Law Order), British Columbia's from BC
             Laws (King's Printer Licence) and UK acts from legislation.gov.uk (Open Government Licence); one book
             per law; key laws, laws-more (sources.LAWS_MORE: larger regulations), or law:<name>
  group:<g>  every guide, PDF and law of one group (group:health, group:disability, group:consumer, group:law)
  med        medicines (medications.py): the official US labels of prescription and over-the-counter medicines
             (one book per first letter) and of pet and farm animal medicines, from DailyMed; key medicines, or
             med:rx:<letters>, med:otc:<letters>, med:animal
Every book records "published": when the publisher published or last revised it (the toolkit ranks newer ones
higher).
Each book's licence is read again from its source while building; a book whose licence is not allowed
(sources.ALLOWED: never NoDerivatives) is left out and listed in the manifest's "left_out".

How a book is made accessible:
  - one page (article) per chapter and section, with the section's number and title as its heading ("27.3 Anatomy
    of the Kidney") and the book's own headings below it; an index page (the welcome page) lists every unit,
    chapter and section with links, and says the title, authors' credit, licence and where the original is;
  - figures: their number, title, the publisher's own description (alt text) and the caption, as text; the pictures
    themselves only with --pictures (the books are much smaller without them);
  - math as readable linear text (mathtext.py), which the toolkit's reader, Send to braille, DAISY and TTS keep;
  - tables as tables with their caption; notes, examples, exercises and glossaries with headings or labels;
  - teacher-only notes are left out (they are not part of the student edition).

The ZIM files are written by zimwrite.py (our own writer, from the openZIM format description, no GPL code); the
original PDFs are never copied here: only their official addresses (and size) are recorded, for the toolkit's
"Download the original PDF".

Usage:
  python textbooks/build_textbooks.py osbooks:physics --out build/textbooks
  python textbooks/build_textbooks.py siyavula --out build/textbooks --cache build/textbooks-cache
  python textbooks/build_textbooks.py dspace --out build/textbooks
  python textbooks/build_textbooks.py nonprofit:eff_surveillance_self_defense --out build/textbooks
  python textbooks/build_textbooks.py --local-osbooks path/to/osbooks-repo --out build/textbooks   (no network)
Each run writes <id>.zim for each book and manifest-<key>.json (the books' catalogue entries and the left-out
ones). Keys: see sources.expand_keys (osbooks, osbooks:<repository>, siyavula, dspace, nonprofit, nonprofit:<name>,
fieldmanuals, government, courses, pdf:<name>, guides, guide:<name>, laws, laws-more, law:<name>, group:<g>, medicines,
med:<piece>, all).
"""

import argparse
import datetime
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mathtext  # noqa: E402
import sources  # noqa: E402
from zimwrite import ZimWriter  # noqa: E402

RELEASE = "https://github.com/mark-getbraille/toolkit-models/releases/download/textbooks"
USER_AGENT = "DigitalAccessibilityToolkit-textbooks/1.0 (open textbooks for blind readers; " \
             "github.com/mark-getbraille/toolkit-models)"
PAUSE = 1.0                      # seconds between two requests to the same site
CNX = "{http://cnx.rice.edu/cnxml}"
COL = "{http://cnx.rice.edu/collxml}"
MD = "{http://cnx.rice.edu/mdml}"
MATHML = "{http://www.w3.org/1998/Math/MathML}"
STYLE = """body{font-family:Georgia,serif;max-width:46em;margin:auto;padding:1em;line-height:1.5}
figure,.note,.example,.exercise{border:1px solid #999;padding:.5em;margin:1em 0}
table{border-collapse:collapse}td,th{border:1px solid #999;padding:.2em .4em}
.math{font-family:Cambria Math,serif}.pagenum{color:#555}nav{margin-top:2em;border-top:1px solid #999}"""


# ====================================================================== the book being built

@dataclass
class Page:
    """One article: its path in the ZIM file ("27-3-anatomy-of-the-kidney"), title, body HTML (below the <h1>),
    and its place: the chapter number (0 for front and back matter) and the unit's title ("" for none)."""
    path: str
    title: str
    body: str
    chapter: int = 0
    unit: str = ""


@dataclass
class Book:
    """A book ready to be written: its catalogue fields and pages (see manifest_entry for the fields)."""
    name: str                    # stable id without date ("openstax_physics")
    title: str
    subject: str
    level: str                   # "school", "college" or "reference"
    group: str                   # "textbooks", "reference", "nonprofit", "government", "university", "fieldmanual",
                                 # "course", or a reference group of sources.GROUPS ("law", "consumer", "health",
                                 # "disability", "science", "books", "historical")
    publisher: str               # "OpenStax, Rice University"
    country: str                 # "United States", "South Africa", "International"
    licence: str                 # "CC BY 4.0"
    licence_url: str
    source: str                  # the web page of the book
    language: str = "eng"
    description: str = ""
    authors: str = ""
    pages: list = field(default_factory=list)
    resources: dict = field(default_factory=dict)   # "media/x.jpg" -> (bytes, mimetype)
    original_pdf: dict = field(default_factory=dict)
    original_epub: dict = field(default_factory=dict)
    flavour: str = "nopic"
    changes: str = ""            # what was changed, for the credit line ("" for the textbooks' usual words)
    published: str = ""          # when the publisher published (or last revised) this edition: "2025-04-10",
                                 # "2025-04" or "2025" ("" when the source does not say); newer ranks higher
    region: str = ""             # the state or province a law or guide applies to ("California", "Ontario"; "" for
                                 # a whole country)
    notice: str = ""             # a statement the licence asks to show with the work (on the welcome page)
    unchanged: bool = False      # kept whole with its text unchanged, only its format converted (a NoDerivatives or
                                 # other no-changes licence allows that: sources.WHOLE_AND_UNCHANGED)
    redirects: list = field(default_factory=list)  # [(path, title, target path)]: more titles that lead to a page
                                 # (a medicine's brand names, medications.py), found by the title search


def licence_short(text, url=""):
    """A licence in its short form ("Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International" ->
    "CC BY-NC-SA 4.0"; "CC BY NC SA 3.0 IGO" -> "CC BY-NC-SA 3.0 IGO"), from its words or its address."""
    words = f"{text} {url}".lower()
    if "publicdomain/zero" in words or "cc0" in words:
        return "CC0 1.0"
    if "open government licence" in words or "open-government-licence" in words:
        return "OGL"
    m = re.search(r"licenses/([a-z-]+)/(\d\.\d)(/igo)?", words)
    if m:
        kind, version, igo = m.group(1), m.group(2), " IGO" if m.group(3) else ""
        return f"CC {kind.upper()} {version}{igo}"
    parts = []
    if "attribution" in words or re.search(r"\bcc[ -]by\b", words):
        parts.append("BY")
    if "noncommercial" in words or "non-commercial" in words or re.search(r"\bnc\b", words):
        parts.append("NC")
    if "noderiv" in words or re.search(r"\bnd\b", words):
        parts.append("ND")
    if "sharealike" in words or "share-alike" in words or re.search(r"\bsa\b", words):
        parts.append("SA")
    if not parts:
        return text.strip()
    version = re.search(r"(\d\.\d)", words)
    igo = " IGO" if "igo" in words else ""
    return "CC " + "-".join(parts) + (f" {version.group(1)}" if version else "") + igo


UNCHANGED = "Converted to an accessible format; the text is unchanged."


def licence_kind(short, whole=False):
    """"open", "share-alike", "non-commercial", or "" when it is not allowed (unknown, or NoDerivatives for a book
    that is rearranged). With whole=True (a work kept whole with its text unchanged, only its format converted:
    see sources.WHOLE_AND_UNCHANGED) a NoDerivatives licence, or a no-changes licence of sources.NO_CHANGES, gives
    "no-changes" ("non-commercial-no-changes" for CC BY-NC-ND)."""
    if short in sources.NO_CHANGES:
        return sources.NO_CHANGES[short] if whole else ""
    base = re.sub(r"\s+\d\.\d.*$", "", short).strip()
    if "ND" in base.split("-") or "-ND" in base:
        if not whole:
            return ""
        kind = sources.ALLOWED.get(base.replace("-ND", ""), "")
        return {"open": "no-changes", "non-commercial": "non-commercial-no-changes"}.get(kind, "")
    return sources.ALLOWED.get(base, "")


def licence_words(short, whole=False):
    """The licence as the toolkit shows it: "CC BY-NC-SA 4.0, not for commercial use" for the non-commercial
    ones, "CC BY-ND 4.0, no changes allowed" for a whole and unchanged work under a no-changes licence."""
    kind = licence_kind(short, whole)
    return short + (", not for commercial use" if kind.startswith("non-commercial") else "") + \
        (", no changes allowed" if kind.endswith("no-changes") else "")


def slug(text, limit=60):
    """A path part from a title ("Anatomy of the Kidney" -> "anatomy-of-the-kidney")."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].strip("-") or "page"


def esc(text):
    """HTML-escaped text."""
    return html.escape(text or "", quote=True)


# ====================================================================== publication dates ("published")

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                      "dec"], 1)}


def iso_date(text):
    """A date written in any of the usual ways as "YYYY-MM-DD" ("YYYY-MM" or "YYYY" when that is all it says), ""
    when no date is found: "2025-04-10T16:00:15+00:00", "D:20250410...", "20240103", "07 April 2025", "April 7, 2025",
    "OCT 29, 2026", "November 2024", "2018"."""
    t = " ".join((text or "").split())
    m = re.search(r"(?<!\d)(19\d\d|20\d\d)-(0[1-9]|1[0-2])(?:-(0[1-9]|[12]\d|3[01]))?(?!\d)", t)
    if m:
        return "-".join(x for x in m.groups() if x)
    m = re.search(r"D:(19\d\d|20\d\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])", t) or \
        re.search(r"(?<!\d)(19\d\d|20\d\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?!\d)", t)
    if m:
        return "-".join(m.groups())
    m = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(19\d\d|20\d\d)\b", t)
    if m and m.group(2)[:3].lower() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(2)[:3].lower()]:02d}-{int(m.group(1)):02d}"
    m = re.search(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(19\d\d|20\d\d)\b", t)
    if m and m.group(1)[:3].lower() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(1)[:3].lower()]:02d}-{int(m.group(2)):02d}"
    m = re.search(r"\b([A-Za-z]{3,9})\.?,?\s+(19\d\d|20\d\d)\b", t)
    if m and m.group(1)[:3].lower() in MONTHS:
        return f"{m.group(2)}-{MONTHS[m.group(1)[:3].lower()]:02d}"
    m = re.search(r"(?<!\d)(19\d\d|20\d\d)(?!\d)", t)
    return m.group(1) if m else ""


# Where web pages say when they were written or last reviewed, most trusted first.
PAGE_DATES = [
    r'"dateModified"\s*:\s*"([^"]+)"',
    r'<meta name="govuk:public-updated-at" content="([^"]+)"',
    r'<meta[^>]+(?:property|name)="(?:article:modified_time|dcterms\.modified|DC\.date\.modified|last-modified)"'
    r'[^>]*content="([^"]+)"',
    r'<meta[^>]+content="([^"]+)"[^>]*(?:property|name)="(?:article:modified_time|dcterms\.modified)"',
    r'(?:Page last reviewed|Last reviewed|Page last updated|Last updated|Last modified|Updated|Reviewed)\s*(?:on)?'
    r'\s*:?\s*(?:<[^>]+>\s*)*([A-Za-z0-9 ,.-]{6,30})',
    r'"datePublished"\s*:\s*"([^"]+)"',
    r'<meta[^>]+(?:property|name)="(?:article:published_time|dcterms\.created|DC\.date)"[^>]*content="([^"]+)"',
    r'<time\b[^>]*datetime="([^"]+)"',
]


def page_date(page_html_text):
    """When a web page says it was last reviewed or written ("YYYY-MM-DD", or "" when it does not say)."""
    for pattern in PAGE_DATES:
        m = re.search(pattern, page_html_text or "", re.I)
        if m:
            found = iso_date(m.group(1))
            if found:
                return found
    return ""


def newest_date(dates):
    """The newest of a list of iso_date values ("" when there is none)."""
    dates = [d for d in dates if d]
    return max(dates) if dates else ""


def pdf_date(pdf_path):
    """When a PDF was made, from its own information (its modification or creation date), "" when not said."""
    try:
        from pypdf import PdfReader
        info = PdfReader(pdf_path).metadata or {}
        return iso_date(str(info.get("/ModDate") or info.get("/CreationDate") or ""))
    except Exception:  # noqa: BLE001 - a PDF without readable information
        return ""


def page_html(book, page, previous=None, following=None):
    """The whole web page of an article: its title, the book's style sheet, the <h1>, the body, then the links to
    the previous and next pages and the contents, and the credit line."""
    nav = ['<nav><p>']
    if previous is not None:
        nav.append(f'Previous: <a href="{esc(previous.path)}">{esc(previous.title)}</a>. ')
    if following is not None:
        nav.append(f'Next: <a href="{esc(following.path)}">{esc(following.title)}</a>. ')
    nav.append(f'<a href="index">Contents of {esc(book.title)}</a>.</p>')
    nav.append(f'<p>{esc(credit_line(book))}</p></nav>')
    return (f'<!DOCTYPE html>\n<html lang="{esc(two_letters(book.language))}"><head><meta charset="utf-8">'
            f'<title>{esc(page.title)}</title><link rel="stylesheet" href="style.css"></head><body>'
            f'<h1>{esc(page.title)}</h1>\n{page.body}\n{"".join(nav)}</body></html>')


def two_letters(code):
    """"eng" -> "en" (for the lang attribute)."""
    return {"eng": "en", "spa": "es", "fra": "fr", "por": "pt"}.get(code, code[:2])


def credit_line(book):
    """"From Physics by OpenStax, Rice University, CC BY 4.0 (https://...). Original: https://openstax.org/..."."""
    if book.unchanged:
        return (f"From {book.title} by {book.publisher}, {licence_words(book.licence, True)} ({book.licence_url}). "
                f"Original: {book.source}. {UNCHANGED}")
    changes = book.changes or "made into web pages, with the formulas written as text"
    return (f"From {book.title} by {book.publisher}, {licence_words(book.licence)} ({book.licence_url}). "
            f"Original: {book.source}. Changed: {changes}.")


def index_page(book):
    """The welcome page: what the book is, its credit and licence, the original PDF, and the contents."""
    out = [f"<p>{esc(book.description)}</p>" if book.description else ""]
    out.append(f"<p>Publisher: {esc(book.publisher)}. {('Authors: ' + esc(book.authors) + '. ') if book.authors else ''}"
               f"Licence: {esc(licence_words(book.licence))} "
               f'(<a href="{esc(book.licence_url)}">{esc(book.licence_url)}</a>). '
               f'Original: <a href="{esc(book.source)}">{esc(book.source)}</a>.</p>')
    if book.published:
        out.append(f"<p>Published (or last revised): {esc(book.published)}.</p>")
    if book.notice:
        out.append(f"<p>{esc(book.notice)}</p>")
    if book.original_pdf.get("url"):
        out.append(f'<p>The publisher\'s original PDF: <a href="{esc(book.original_pdf["url"])}">'
                   f'{esc(book.original_pdf["url"])}</a>.</p>')
    out.append("<h2>Contents</h2>")
    unit, chapter_open = None, False
    out.append("<ul>")
    for p in book.pages:
        if p.unit != unit:
            if chapter_open:
                out.append("</ul></li>")
                chapter_open = False
            unit = p.unit
            if unit:
                out.append(f"</ul><h3>{esc(unit)}</h3><ul>")
        is_chapter = p.path.startswith("chapter-")
        if is_chapter:
            if chapter_open:
                out.append("</ul></li>")
            out.append(f'<li><a href="{esc(p.path)}">{esc(p.title)}</a><ul>')
            chapter_open = True
        elif chapter_open and p.chapter:
            out.append(f'<li><a href="{esc(p.path)}">{esc(p.title)}</a></li>')
        else:
            if chapter_open:
                out.append("</ul></li>")
                chapter_open = False
            out.append(f'<li><a href="{esc(p.path)}">{esc(p.title)}</a></li>')
    if chapter_open:
        out.append("</ul></li>")
    out.append("</ul>")
    return re.sub(r"<ul></ul>", "", "\n".join(out))


def content_sha256(book):
    """A checksum of a book's text (title, licence, pages and pictures), the same for two builds of the same text
    although their ZIM files differ (each file has its own id and date): updates.merge_versions keeps a new version
    only when this changed."""
    h = hashlib.sha256()
    for part in (book.title, book.licence, book.notice, book.description):
        h.update((part or "").encode("utf-8") + b"\0")
    for p in book.pages:
        h.update(f"{p.path}\0{p.title}\0{p.unit}\0{p.body}\0".encode("utf-8"))
    for path, title, target in book.redirects:
        h.update(f"{path}\0{title}\0{target}\0".encode("utf-8"))
    for path in sorted(book.resources):
        h.update(path.encode("utf-8") + hashlib.sha256(book.resources[path][0]).digest())
    return h.hexdigest()


def write_book(book, out_dir, date=None, versioned=False):
    """Write book in out_dir and return its catalogue entry (manifest_entry). The file is <name>.<YYYY-MM-DD>.zim
    with versioned=True (a kept version: every rebuild is a new file and the old ones stay, see updates.py), else
    <name>_<YYYY-MM>.zim (replaced by the next build in the same month: news pieces, VOA years)."""
    date = date or datetime.date.today()
    file_id = f"{book.name}.{date:%Y-%m-%d}" if versioned else f"{book.name}_{date:%Y-%m}"
    w = ZimWriter()
    pages = book.pages
    for i, p in enumerate(pages):
        w.add(p.path, p.title, page_html(book, p, pages[i - 1] if i else None,
                                         pages[i + 1] if i + 1 < len(pages) else None), "text/html", front=True)
    index = Page("index", book.title, index_page(book))
    w.add("index", book.title, page_html(book, index), "text/html", front=True)
    w.add("style.css", "", STYLE, "text/css")
    for path, (data, mimetype) in book.resources.items():
        w.add(path, "", data, mimetype)
    for path, title, target in book.redirects:
        if not w.has(path):
            w.redirect(path, title, target)
    w.metadata({
        "Name": book.name, "Title": book.title[:30] if len(book.title) > 30 else book.title,
        "Language": book.language, "Creator": book.publisher, "Publisher": "GetBraille.com (toolkit-models)",
        "Date": date.isoformat(), "Description": (book.description or f"{book.subject} textbook")[:80],
        "LongDescription": (book.description or "")[:4000], "License": f"{book.licence} {book.licence_url}",
        "Source": book.source, "Flavour": book.flavour,
        "Tags": f"_category:{book.group};_pictures:{'yes' if book.flavour != 'nopic' else 'no'};_ftindex:no;"
                f"{slug(book.subject)}",
    })
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, file_id + ".zim")
    count = w.write(path, main="index")
    entry = manifest_entry(book, file_id, path, count, date)
    entry["content_sha256"] = content_sha256(book)
    return entry


def file_sha256(path):
    """The SHA-256 of a file (read in pieces)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_entry(book, file_id, path, count, date):
    """The catalogue entry of a written book (textbooks.json "books"): id (file name without .zim), name (the same
    in every release), title, subject, level, group, publisher, credit, country, licence (short), licence_url,
    licence_kind, licence_text (as shown), language, flavour, date (when the ZIM file was made), published (when the
    publisher published or last revised the work: "YYYY-MM-DD", "YYYY-MM" or "YYYY", "" when unknown), region (state
    or province, "" for a whole country), size, sha256, article_count, file, url, description, source, original_pdf and
    original_epub ({url, size, sha256} or {}), and unchanged (true for a work kept whole with its text unchanged)."""
    return {
        "id": file_id, "name": book.name, "title": book.title, "subject": book.subject, "level": book.level,
        "group": book.group, "publisher": book.publisher, "credit": book.publisher, "country": book.country,
        "licence": book.licence, "licence_url": book.licence_url,
        "licence_kind": licence_kind(book.licence, book.unchanged),
        "licence_text": licence_words(book.licence, book.unchanged), "unchanged": book.unchanged,
        "language": book.language, "flavour": book.flavour,
        "date": date.isoformat(), "published": book.published, "region": book.region,
        "size": os.path.getsize(path), "sha256": file_sha256(path),
        "article_count": count, "file": os.path.basename(path), "url": f"{RELEASE}/{os.path.basename(path)}",
        "description": book.description, "source": book.source, "authors": book.authors,
        "original_pdf": book.original_pdf, "original_epub": book.original_epub,
    }


# ====================================================================== polite downloads

_last = {}
CRAWL_DELAY = {}                 # {host: seconds} a site's robots.txt asks for between requests (allowed_by_robots)


def fetch(url, cache=None, binary=False, tries=4):
    """The body of url (text, or bytes with binary=True): one request at a time, PAUSE seconds between two
    requests to the same site (or the Crawl-delay its robots.txt asks for), a few tries on errors, compressed answers
    unpacked, kept in the cache folder when one is given."""
    key = hashlib.sha256(url.encode()).hexdigest()[:40]
    cached = os.path.join(cache, key) if cache else None
    if cached and os.path.exists(cached):
        with open(cached, "rb") as f:
            data = f.read()
        return data if binary else data.decode("utf-8", "replace")
    host = urllib.parse.urlsplit(url).hostname
    for attempt in range(tries):
        wait = max(PAUSE, CRAWL_DELAY.get(host, 0)) - (time.monotonic() - _last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*",
                                                       "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
                if (r.headers.get("Content-Encoding") or "").lower() == "gzip":
                    # Asked for: some services (the eCFR's) answer only compressed.
                    import gzip
                    data = gzip.decompress(data)
            break
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410) or attempt == tries - 1:
                raise
        except (urllib.error.URLError, OSError):
            if attempt == tries - 1:
                raise
        finally:
            _last[host] = time.monotonic()
        time.sleep(10 * (attempt + 1))
    if cached:
        os.makedirs(cache, exist_ok=True)
        with open(cached, "wb") as f:
            f.write(data)
    return data if binary else data.decode("utf-8", "replace")


def head_size(url):
    """The size in bytes of the file at url (a HEAD request), 0 when it is not said."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length") or 0)
    except (urllib.error.URLError, OSError, ValueError):
        return 0


# ====================================================================== OpenStax (CNXML)

SECTION_NAMES = {
    "summary": "Section Summary", "key-equations": "Key Equations", "review-questions": "Review Questions",
    "critical-thinking": "Critical Thinking Questions", "interactive-exercise": "Interactive Link Questions",
    "multiple-choice": "Multiple Choice", "free-response": "Free Response", "problems-exercises": "Problems",
    "conceptual-questions": "Conceptual Questions", "section-exercises": "Section Exercises",
    "references": "References", "short-answer": "Short Answer", "key-concepts": "Key Concepts",
    "practice": "Practice", "check-understanding": "Check Your Understanding", "performance-task": "Performance Task",
}


def _text(el):
    """All the text inside el, without tags, on one line."""
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def _local(el):
    """The tag of el without its namespace ("para", "m:math" -> "math")."""
    return el.tag.rsplit("}", 1)[-1] if isinstance(el.tag, str) else ""


SUBSCRIPTS = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")
SUPERSCRIPTS = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")


def small_text(text, sup):
    """A subscript or superscript as text: Unicode small digits when it is only digits and signs ("H₂O", "10⁻³"),
    else "^(...)" or "_(...)"."""
    t = text.strip()
    if re.fullmatch(r"[0-9+\-=()" + ("n" if sup else "") + "]+", t):
        return t.translate(SUPERSCRIPTS if sup else SUBSCRIPTS)
    return ("^" if sup else "_") + (t if len(t) == 1 else f"({t})")


class OpenStaxBook:
    """One OpenStax book from its repository folder (see the module docstring). repo: the repository folder;
    collection: its collection file; cms: the book's record from OpenStax's own catalogue (or {})."""

    def __init__(self, repo, collection, pictures=False, cms=None):
        """Read the collection and every module it uses."""
        self.repo, self.pictures, self.cms = repo, pictures, cms or {}
        self.col = ET.parse(collection).getroot()
        meta = self.col.find(f"{COL}metadata") if self.col.find(f"{COL}metadata") is not None \
            else self.col.find("{http://cnx.rice.edu/collxml}metadata")
        if meta is None:
            meta = next(iter(self.col))
        self.title = _text(meta.find(f"{MD}title"))
        self.slug = _text(meta.find(f"{MD}slug")) or slug(self.title)
        lic = meta.find(f"{MD}license")
        self.licence = licence_short(_text(lic), lic.get("url", "") if lic is not None else "")
        self.licence_url = (lic.get("url", "") if lic is not None else "").replace("http://", "https://")
        self.language = _text(meta.find(f"{MD}language")) or "en"
        self.authors = self.col.get("authors", "").strip().rstrip(",")
        self.modules = {}            # module id -> parsed document
        self.where = {}              # module id -> page path
        self.labels = {}             # element id -> (page path, label such as "Figure 27.3")
        self.footnotes = []
        self.resources = {}

    # -- the structure

    def _module(self, mid):
        """The parsed CNXML document of module mid (None when it is missing)."""
        if mid not in self.modules:
            path = os.path.join(self.repo, "modules", mid, "index.cnxml")
            try:
                self.modules[mid] = ET.parse(path).getroot()
            except (OSError, ET.ParseError):
                self.modules[mid] = None
        return self.modules[mid]

    def _walk(self, content, unit, plan):
        """Fill plan with (kind, module id or title, unit, chapter title) in reading order."""
        for item in content:
            tag = _local(item)
            if tag == "module":
                plan.append(("module", item.get("document"), unit, None))
            elif tag == "subcollection":
                title = _text(item.find(f"{MD}title"))
                inner = item.find(f"{COL}content")
                if inner is None:
                    continue
                if any(_local(x) == "module" for x in inner):
                    plan.append(("chapter", title, unit, title))
                    for m in inner:
                        if _local(m) == "module":
                            plan.append(("module", m.get("document"), unit, title))
                        elif _local(m) == "subcollection":
                            self._walk([m], unit, plan)
                else:
                    self._walk(list(inner), title, plan)

    def plan(self):
        """[(path, title, module id or None, chapter number, unit)] of every page, and the numbers of figures and
        tables (self.labels)."""
        raw = []
        self._walk(list(self.col.find(f"{COL}content")), "", raw)
        out, chapter, section, appendix = [], 0, 0, 0
        current_chapter = None
        seen_chapters = False
        for kind, value, unit, chapter_title in raw:
            if kind == "chapter":
                chapter += 1
                section = 0
                current_chapter = value
                seen_chapters = True
                continue
            doc = self._module(value)
            if doc is None:
                continue
            title = _text(doc.find(f"{CNX}title")) or value
            classes = (doc.get("class") or "").split()
            if chapter_title is None:
                if seen_chapters:
                    appendix += 1
                    letter = chr(ord("A") + appendix - 1)
                    path, page_title, number = f"appendix-{letter.lower()}-{slug(title)}", \
                        f"Appendix {letter}: {title}", 0
                else:
                    path, page_title, number = slug(title), title, 0
            elif "introduction" in classes or (section == 0 and title.lower().startswith("introduction")):
                path, page_title, number = f"chapter-{chapter}", f"Chapter {chapter}: {current_chapter}", chapter
            else:
                section += 1
                path, page_title, number = f"{chapter}-{section}-{slug(title)}", f"{chapter}.{section} {title}", \
                    chapter
            out.append((path, page_title, value, number, unit))
            self.where[value] = path
        self._number(out)
        return out

    def _number(self, plan):
        """Number the figures and tables per chapter ("Figure 27.3", "Table 4.1"), as the printed book does."""
        counts = {}
        for path, _title, mid, chapter, _unit in plan:
            doc = self._module(mid)
            for el in doc.iter():
                tag = _local(el)
                if tag not in ("figure", "table") or not el.get("id"):
                    continue
                classes = (el.get("class") or "").split()
                if "splash" in classes or "unnumbered" in classes:
                    continue
                key = (chapter, tag)
                counts[key] = counts.get(key, 0) + 1
                word = "Figure" if tag == "figure" else "Table"
                label = f"{word} {chapter}.{counts[key]}" if chapter else f"{word} {counts[key]}"
                self.labels[el.get("id")] = (path, label)
            for el in doc.iter():
                if el.get("id") and el.get("id") not in self.labels:
                    self.labels[el.get("id")] = (path, "")

    # -- the pages

    def pages(self):
        """[Page] of the whole book."""
        out = []
        for path, title, mid, chapter, unit in self.plan():
            doc = self._module(mid)
            self.footnotes = []
            self.exercise = 0
            self.current = path
            body = []
            abstract = doc.find(f"{CNX}metadata/{MD}abstract")
            if abstract is not None and _text(abstract):
                body.append('<div class="objectives"><h2>Learning Objectives</h2>' + self.inner(abstract, 2) +
                            "</div>")
            content = doc.find(f"{CNX}content")
            if content is not None:
                body.append(self.inner(content, 1))
            glossary = doc.find(f"{CNX}glossary")
            if glossary is not None:
                body.append("<h2>Key Terms</h2>" + self.inner(glossary, 2))
            if self.footnotes:
                body.append("<h2>Notes</h2><ol>" + "".join(f'<li id="note-{i}">{t}</li>'
                                                            for i, t in enumerate(self.footnotes, 1)) + "</ol>")
            out.append(Page(path, title, "\n".join(body), chapter, unit))
        return out

    def inner(self, el, depth):
        """The HTML of el's text and children (not el's own tag)."""
        parts = [esc(el.text)] if el.text else []
        for child in el:
            parts.append(self.convert(child, depth))
            if child.tail:
                parts.append(esc(child.tail))
        return "".join(parts)

    def _id(self, el):
        """' id="..."' for an element with an id, else ""."""
        return f' id="{esc(el.get("id"))}"' if el.get("id") else ""

    def _title(self, el):
        """The HTML of el's <title> child ("" when none)."""
        t = el.find(f"{CNX}title")
        return self.inner(t, 9).strip() if t is not None else ""

    def convert(self, el, depth):
        """The HTML of one CNXML element (see the class docstring and the module docstring)."""
        tag = _local(el)
        ns = el.tag.split("}")[0][1:] if "}" in el.tag else ""
        if ns == MATHML[1:-1]:
            if tag != "math":
                return ""
            text = mathtext.mathml_text(el)
            block = el.get("display") == "block"
            elem = "div" if block else "span"
            return f'<{elem} class="math" role="math" aria-label="{esc(text)}">{esc(text)}</{elem}>'
        if ns == MD[1:-1] or tag in ("title", "label", "metadata"):
            return ""
        classes = (el.get("class") or "").split()
        if any("teacher" in c for c in classes) or el.get("type") == "teacher":
            return ""
        if tag == "para":
            title = self._title(el)
            return f"<p{self._id(el)}>" + (f"<strong>{title}</strong> " if title else "") + \
                self.inner(el, depth) + "</p>\n"
        if tag == "section":
            title = self._title(el) or next((esc(SECTION_NAMES[c]) for c in classes if c in SECTION_NAMES), "")
            if any(c in SECTION_NAMES for c in classes) or el.find(f"{CNX}exercise") is not None:
                self.exercise = 0
            level = min(6, depth + 1)
            head = f"<h{level}{self._id(el)}>{title}</h{level}>\n" if title else ""
            return f"<section>{head}{self.inner(el, depth + 1)}</section>\n"
        if tag == "note":
            title = self._title(el) or esc(" ".join(c.replace("-", " ") for c in classes).capitalize())
            level = min(6, depth + 2)
            head = f"<h{level}>{title}</h{level}>" if title else ""
            return f'<div class="note"{self._id(el)}>{head}{self.inner(el, depth + 1)}</div>\n'
        if tag == "example":
            title = self._title(el)
            return f'<div class="example"{self._id(el)}><p><strong>Example{": " + title if title else ""}' \
                   f'</strong></p>{self.inner(el, depth + 1)}</div>\n'
        if tag == "exercise":
            self.exercise += 1
            return f'<div class="exercise"{self._id(el)}><p><strong>Question {self.exercise}</strong></p>' \
                   f'{self.inner(el, depth + 1)}</div>\n'
        if tag == "solution":
            return f'<div class="solution"><p><strong>Answer</strong></p>{self.inner(el, depth)}</div>\n'
        if tag in ("problem", "commentary", "statement", "proof", "rule", "content", "div"):
            title = self._title(el)
            return (f"<p><strong>{title}</strong></p>" if title else "") + f"<div{self._id(el)}>" + \
                self.inner(el, depth) + "</div>\n"
        if tag == "list":
            ordered = el.get("list-type") == "enumerated"
            style = {"lower-alpha": "a", "upper-alpha": "A", "lower-roman": "i", "upper-roman": "I"}.get(
                el.get("number-style", ""), "")
            title = self._title(el)
            elem = "ol" if ordered else "ul"
            attrs = f' type="{style}"' if ordered and style else ""
            return (f"<p><strong>{title}</strong></p>" if title else "") + \
                f"<{elem}{attrs}{self._id(el)}>{self.inner(el, depth)}</{elem}>\n"
        if tag == "item":
            return f"<li>{self.inner(el, depth)}</li>\n"
        if tag == "emphasis":
            effect = el.get("effect", "bold")
            elem = {"italics": "em", "underline": "u", "smallcaps": "span"}.get(effect, "strong")
            return f"<{elem}>{self.inner(el, depth)}</{elem}>"
        if tag == "term":
            return f"<strong>{self.inner(el, depth)}</strong>"
        if tag in ("sub", "sup"):
            return esc(small_text(_text(el), tag == "sup"))
        if tag == "newline":
            return "<br>"
        if tag == "space":
            return " "
        if tag in ("code", "preformat"):
            if tag == "preformat" or el.get("display") == "block":
                return f"<pre>{esc(''.join(el.itertext()))}</pre>\n"
            return f"<code>{esc(''.join(el.itertext()))}</code>"
        if tag == "quote":
            if el.get("display") == "block":
                return f"<blockquote>{self.inner(el, depth)}</blockquote>\n"
            return f"<q>{self.inner(el, depth)}</q>"
        if tag in ("cite", "cite-title"):
            return f"<cite>{self.inner(el, depth)}</cite>"
        if tag == "foreign":
            return f"<span>{self.inner(el, depth)}</span>"
        if tag == "footnote":
            self.footnotes.append(self.inner(el, depth))
            n = len(self.footnotes)
            return f'<sup><a href="#note-{n}">[note {n}]</a></sup>'
        if tag == "link":
            return self.link(el, depth)
        if tag == "figure":
            return self.figure(el, depth)
        if tag == "subfigure":
            return self.figure(el, depth, sub=True)
        if tag == "media":
            return self.media(el)
        if tag == "table":
            return self.table(el, depth)
        if tag == "equation":
            return f'<div class="equation"{self._id(el)}>{self.inner(el, depth)}</div>\n'
        if tag == "definition":
            term = el.find(f"{CNX}term")
            meanings = el.findall(f"{CNX}meaning")
            return f"<dt{self._id(el)}>{self.inner(term, depth) if term is not None else ''}</dt>" + \
                "".join(f"<dd>{self.inner(m, depth)}</dd>" for m in meanings) + "\n"
        if tag == "glossary":
            return f"<dl>{self.inner(el, depth)}</dl>"
        if tag in ("meaning", "seealso"):
            return self.inner(el, depth)
        if tag == "caption":
            return ""
        return self.inner(el, depth)

    def link(self, el, depth):
        """A link: to the internet (url), to another page of the book (document), or within the page (target-id);
        an empty link gets the label of what it points to ("Figure 27.3")."""
        words = self.inner(el, depth).strip()
        url = el.get("url")
        if url:
            return f'<a href="{esc(url)}">{words or esc(url)}</a>'
        target, document = el.get("target-id"), el.get("document")
        page = self.where.get(document, self.current) if document else self.current
        found = self.labels.get(target, (page, "")) if target else (page, "")
        page = found[0] if target and target in self.labels else page
        if not words:
            words = esc(found[1]) if found[1] else esc(self._page_title(page))
        href = ("" if page == self.current else page) + (f"#{target}" if target else "")
        return f'<a href="{esc(href or "#")}">{words}</a>'

    def _page_title(self, path):
        """The title of the page at path (its module's title)."""
        for mid, p in self.where.items():
            if p == path:
                doc = self._module(mid)
                return _text(doc.find(f"{CNX}title")) if doc is not None else path
        return path

    def figure(self, el, depth, sub=False):
        """A figure: its number and title, then the publisher's description of the picture and the caption."""
        label = self.labels.get(el.get("id"), ("", ""))[1]
        title = self._title(el)
        head = " ".join(x for x in (f"<strong>{esc(label)}</strong>" if label else "", title) if x)
        inside = "".join(self.convert(c, depth) for c in el if _local(c) not in ("title", "caption"))
        caption = el.find(f"{CNX}caption")
        cap = self.inner(caption, depth).strip() if caption is not None else ""
        figcaption = " ".join(x for x in (head, cap) if x)
        return f'<figure{self._id(el)}>{inside}' + (f"<figcaption>{figcaption}</figcaption>" if figcaption else "") + \
            "</figure>\n"

    def media(self, el):
        """A picture (its description; the picture itself with --pictures) or an online video (a link)."""
        alt = " ".join((el.get("alt") or "").split())
        image = el.find(f"{CNX}image")
        if image is not None:
            src = image.get("src", "")
            name = os.path.basename(src)
            if self.pictures and name:
                path = os.path.join(self.repo, "media", name)
                if os.path.exists(path):
                    kind = image.get("mime-type") or "image/jpeg"
                    kind = "image/jpeg" if kind in ("image/jpg",) else kind
                    with open(path, "rb") as f:
                        self.resources[f"media/{name}"] = (f.read(), kind)
                    return f'<img src="media/{esc(name)}" alt="{esc(alt)}">'
            return f'<p class="picture">Picture: {esc(alt)}</p>' if alt else ""
        for kind in ("iframe", "video", "flash", "object", "audio"):
            other = el.find(f"{CNX}{kind}")
            if other is not None:
                src = other.get("src", "")
                return f'<p>Online {"video" if kind != "audio" else "audio"}' + \
                    (f" ({esc(alt)})" if alt else "") + f': <a href="{esc(src)}">{esc(src)}</a></p>'
        return f"<p>{esc(alt)}</p>" if alt else ""

    def table(self, el, depth):
        """A table with its number, title and caption, its heading rows as heading cells."""
        label = self.labels.get(el.get("id"), ("", ""))[1]
        title = self._title(el)
        caption = el.find(f"{CNX}caption")
        cap = " ".join(x for x in (f"<strong>{esc(label)}</strong>" if label else "", title,
                                   self.inner(caption, depth).strip() if caption is not None else "") if x)
        rows = []
        for group in el.iter():
            part = _local(group)
            if part not in ("thead", "tbody", "tfoot"):
                continue
            cell = "th" if part == "thead" else "td"
            for row in group:
                if _local(row) != "row":
                    continue
                cells = "".join(f"<{cell}>{self.inner(e, depth)}</{cell}>" for e in row if _local(e) == "entry")
                rows.append(f"<tr>{cells}</tr>")
        return f'<table{self._id(el)}>' + (f"<caption>{cap}</caption>" if cap else "") + "".join(rows) + \
            "</table>\n"


def openstax_catalogue(cache=None):
    """{slug: record} of OpenStax's own list of books (openstax.org's CMS: subject, level, the original PDF), or
    {} when it cannot be read."""
    url = ("https://openstax.org/apps/cms/api/v2/pages/?type=books.Book&limit=250&fields=title,book_state,"
           "license_name,license_url,pdf_url,high_resolution_pdf_url,book_subjects,k12book_subjects,"
           "description,publish_date,authors")
    try:
        data = json.loads(fetch(url, cache))
    except Exception as e:  # noqa: BLE001 - built without the extra facts
        print(f"OpenStax's catalogue could not be read ({e}); building without it.")
        return {}
    return {item["meta"]["slug"]: item for item in data.get("items", [])}


def clone_osbooks(repo_name, work, pictures=False):
    """A shallow copy of github.com/openstax/osbooks-<repo_name> in work (without the pictures unless pictures)."""
    dest = os.path.join(work, f"osbooks-{repo_name}")
    if os.path.isdir(os.path.join(dest, ".git")):
        return dest
    url = f"https://github.com/openstax/osbooks-{repo_name}"
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", url, dest], check=True,
                   env=env)
    paths = ["LICENSE", "META-INF", "collections", "modules"] + (["media"] if pictures else [])
    subprocess.run(["git", "-C", dest, "checkout", "HEAD", "--"] + paths, check=True, env=env)
    return dest


def plain(html_text):
    """Text of a bit of HTML (OpenStax's descriptions), on one line."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", html_text or "")).split())


def osbooks_books(repo, pictures=False, catalogue=None, left_out=None):
    """[Book] of an OpenStax repository folder (every book its META-INF/books.xml lists). A book whose licence is
    not allowed is added to left_out instead."""
    left_out = left_out if left_out is not None else []
    container = ET.parse(os.path.join(repo, "META-INF", "books.xml")).getroot()
    out = []
    for item in container:
        href = item.get("href", "")
        collection = os.path.normpath(os.path.join(repo, "META-INF", href))
        ob = OpenStaxBook(repo, collection, pictures, (catalogue or {}).get(item.get("slug", "")))
        cms = ob.cms
        cms_licence = licence_short(cms.get("license_name", ""), cms.get("license_url", "")) if cms else ""
        licence = ob.licence
        if cms_licence and cms_licence != licence and licence_kind(licence) and licence_kind(cms_licence):
            # They disagree: the stricter one (non-commercial over share-alike over open) is used.
            order = ["open", "share-alike", "non-commercial"]
            if order.index(licence_kind(cms_licence)) > order.index(licence_kind(licence)):
                licence = cms_licence
        if not licence_kind(licence):
            left_out.append({"title": f"OpenStax {ob.title}", "reason": f"Its licence ({licence}) is not one the "
                             "toolkit may repackage (NoDerivatives or unknown)."})
            continue
        if cms.get("book_state") in ("retired", "deprecated"):
            left_out.append({"title": f"OpenStax {ob.title}", "reason": "OpenStax has retired this edition."})
            continue
        subjects = [s.get("subject_name", "") for s in cms.get("book_subjects", [])] if cms else []
        k12 = bool(cms.get("k12book_subjects")) if cms else False
        pdf = cms.get("high_resolution_pdf_url") or cms.get("pdf_url") or ""
        authors = ", ".join(a.get("value", {}).get("name", "") for a in cms.get("authors", [])
                            if a.get("value", {}).get("senior_author")) if cms else ob.authors
        book = Book(
            name=f"openstax_{ob.slug.replace('-', '_')}", title=f"OpenStax {ob.title}",
            subject=subjects[0] if subjects else "General", level="school" if k12 else "college",
            group="textbooks", publisher="OpenStax, Rice University", country="United States", licence=licence,
            licence_url=ob.licence_url or (cms.get("license_url") or ""),
            source=f"https://openstax.org/details/books/{ob.slug}", language="eng",
            description=plain(cms.get("description", ""))[:600] if cms else "", authors=authors or ob.authors,
            original_pdf={"url": pdf, "size": head_size(pdf), "sha256": ""} if pdf else {},
            flavour="maxi" if pictures else "nopic", published=iso_date(cms.get("publish_date") or ""))
        book.pages = ob.pages()
        book.resources = ob.resources
        out.append(book)
    return out


# ====================================================================== Siyavula (online reader)

SIYAVULA_SITE = "https://www.siyavula.com"
KEEP_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "li", "table", "thead", "tbody", "tr", "td", "th",
             "caption", "figure", "figcaption", "dl", "dt", "dd", "strong", "em", "b", "i", "sub", "sup", "br",
             "blockquote", "pre", "code", "a", "img", "section", "div", "span"}
DROP_TAGS = {"script", "style", "button", "input", "form", "select", "textarea", "iframe", "noscript", "svg",
             "nav", "video", "audio", "object", "template"}


def latex_spans(text):
    """\\( ... \\) and \\[ ... \\] formulas in HTML text replaced by their readable text (mathtext.latex_text)."""
    def inline(m):
        """One inline formula."""
        t = mathtext.latex_text(html.unescape(m.group(1)))
        return f'<span class="math" role="math" aria-label="{esc(t)}">{esc(t)}</span>'

    def block(m):
        """One displayed formula."""
        t = mathtext.latex_text(html.unescape(m.group(1)))
        return f'<div class="math" role="math" aria-label="{esc(t)}">{esc(t)}</div>'
    text = re.sub(r"\\\[(.+?)\\\]", block, text, flags=re.S)
    return re.sub(r"\\\((.+?)\\\)", inline, text, flags=re.S)


class _Cleaner:
    """Keeps only the plain structure of a web page's HTML (KEEP_TAGS, without classes and styles), drops what is
    not the text (DROP_TAGS), pictures without a real description, and the "shortcode" marks; links within the book
    are pointed at its pages (links: {address: page path})."""

    def __init__(self, links, base):
        """links: {absolute address: page path}; base: the page's own address."""
        from html.parser import HTMLParser

        cleaner = self

        class Parser(HTMLParser):
            """The parser that calls the cleaner."""

            def handle_starttag(self, tag, attrs):
                """An opening tag."""
                cleaner.start(tag, dict(attrs))

            def handle_startendtag(self, tag, attrs):
                """A tag closed at once (<br/>)."""
                cleaner.start(tag, dict(attrs))
                if tag not in ("br", "img"):
                    cleaner.end(tag)

            def handle_endtag(self, tag):
                """A closing tag."""
                cleaner.end(tag)

            def handle_data(self, data):
                """Text."""
                cleaner.data(data)
        self.parser = Parser(convert_charrefs=True)
        self.links, self.base, self.out, self.skip = links, base, [], []

    def start(self, tag, a):
        """Keep, drop or skip an opening tag."""
        classes = (a.get("class") or "").split()
        if self.skip:
            if tag == self.skip[-1][0]:
                self.skip[-1][1] += 1
            return
        if tag in DROP_TAGS or "shortcode" in classes or "hidden" in a or "sv-hidden" in classes:
            if tag not in ("br", "img", "input"):
                self.skip.append([tag, 1])
            return
        if tag not in KEEP_TAGS:
            return
        if tag == "img":
            alt = " ".join((a.get("alt") or "").split())
            if alt and not re.fullmatch(r"[\w-]+\.(png|jpe?g|gif|svg)", alt, re.I):
                self.out.append(f"<p>Picture: {esc(alt)}</p>")
            return
        if tag == "a":
            href = urllib.parse.urljoin(self.base, a.get("href") or "")
            target = self.links.get(href.split("#")[0])
            if target:
                href = target + ("#" + href.split("#", 1)[1] if "#" in href else "")
            self.out.append(f'<a href="{esc(href)}">')
            return
        ident = f' id="{esc(a["id"])}"' if a.get("id") else ""
        self.out.append(f"<{tag}{ident}>" if tag != "br" else "<br>")

    def end(self, tag):
        """Close a kept tag."""
        if self.skip:
            if tag == self.skip[-1][0]:
                self.skip[-1][1] -= 1
                if not self.skip[-1][1]:
                    self.skip.pop()
            return
        if tag in KEEP_TAGS and tag not in ("br", "img"):
            self.out.append(f"</{tag}>")

    def data(self, text):
        """Text (escaped again)."""
        if not self.skip:
            self.out.append(esc(text))

    def clean(self, text):
        """The cleaned HTML of text."""
        self.parser.feed(text)
        self.parser.close()
        out = "".join(self.out)
        out = re.sub(r"<(span|div)>\s*</\1>", "", out)
        out = re.sub(r"<li>\s*<p>((?:(?!</?p>).)*)</p>\s*</li>", r"<li>\1</li>", out, flags=re.S)
        return re.sub(r"\n\s*\n+", "\n", out)


def siyavula_book(subject, grade, title, subject_words, cache=None, left_out=None):
    """The Book of one Siyavula textbook from its online reader (www.siyavula.com/read/za/<subject>/grade-<n>),
    or None when its reader page or its licence line is missing (then it is added to left_out)."""
    left_out = left_out if left_out is not None else []
    toc_url = f"{SIYAVULA_SITE}/read/za/{subject}/grade-{grade}"
    toc = fetch(toc_url, cache)
    if "Creative Commons Attribution License" not in toc:
        left_out.append({"title": f"Siyavula {title}", "reason": "Its reader page no longer states the Creative "
                         "Commons Attribution licence."})
        return None
    chapters = re.findall(r'<a href="(/read/za/[^"]+)" class="chapter-title">\s*([^<]+)', toc)
    sections = re.findall(r'<a href="(/read/za/%s/grade-%d/[^"/]+/[^"]+)">' % (re.escape(subject), grade), toc)
    epub = re.search(r'href="(/downloads/books/[^"]+CC-BY\.epub)"', toc)
    pdf = re.search(r'href="(/downloads/books/[^"]+CC-BY[^"]*\.pdf)"', toc) or \
        re.search(r'href="(/downloads/books/[^"]+\.pdf)"', toc)
    book = Book(name=f"siyavula_{slug(subject).replace('-', '_')}_grade_{grade}", title=f"Siyavula {title}",
                subject=subject_words, level="school", group="textbooks", publisher="Siyavula Education",
                country="South Africa", licence="CC BY 4.0", licence_url="https://creativecommons.org/licenses/by/4.0/",
                source=toc_url, description=f"{title}, a South African school textbook (CAPS curriculum) by Siyavula "
                "Education, with worked examples and exercises.")
    if pdf:
        url = SIYAVULA_SITE + pdf.group(1)
        book.original_pdf = {"url": url, "size": head_size(url), "sha256": ""}
    if epub:
        url = SIYAVULA_SITE + epub.group(1)
        book.original_epub = {"url": url, "size": head_size(url), "sha256": ""}
    links, order = {}, []
    for number, (chapter_href, chapter_title) in enumerate(chapters, 1):
        chapter_title = " ".join(html.unescape(chapter_title).split())
        chapter_title = re.sub(r"^Chapter \d+:\s*", "", chapter_title)
        mine = [s for s in sections if s.startswith(chapter_href + "/")]
        mine = list(dict.fromkeys(mine))
        chapter_path = f"chapter-{number}"
        order.append((chapter_path, f"Chapter {number}: {chapter_title}", None, number))
        links[SIYAVULA_SITE + chapter_href] = chapter_path
        for k, href in enumerate(mine, 1):
            path = f"{number}-{k}-{slug(href.rsplit('/', 1)[-1])}"
            links[SIYAVULA_SITE + href] = path
            order.append((path, "", href, number))
    for path, page_title, href, number in order:
        if href is None:
            items = [(p, h) for p, _t, h, n in order if n == number and h]
            book.pages.append(Page(path, page_title, "<p>The sections of this chapter:</p><ul>" + "".join(
                f'<li><a href="{esc(p)}">{esc(p)}</a></li>' for p, _h in items) + "</ul>", number))
            continue
        page = fetch(SIYAVULA_SITE + href, cache)
        inner = page.split("<body>", 2)
        body = inner[2] if len(inner) > 2 else (inner[1] if len(inner) > 1 else page)
        body = body.split("</body>", 1)[0]
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S) or re.search(r"<h[1-4][^>]*>(.*?)</h[1-4]>", body, re.S)
        words = re.sub(r"<span class=\"shortcode\">.*?</span>", "", heading.group(1), flags=re.S) if heading else \
            f"Section {number}.{path.split('-')[1]}"
        page_title = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", words)).split())
        body = re.sub(r"<h2[^>]*>.*?</h2>", "", body, count=1, flags=re.S)
        cleaned = _Cleaner(links, SIYAVULA_SITE + href).clean(latex_spans(body))
        book.pages.append(Page(path, page_title or path, cleaned, number))
    titles = {p.path: p.title for p in book.pages}
    for p in book.pages:
        if p.path.startswith("chapter-"):
            p.body = re.sub(r'<li><a href="([^"]+)">[^<]*</a></li>',
                            lambda m: f'<li><a href="{m.group(1)}">{esc(titles.get(m.group(1), m.group(1)))}</a></li>',
                            p.body)
    return book


# ====================================================================== reference works (DSpace repositories, PDF)

def dspace_record(site, handle, cache=None):
    """The DSpace item JSON of handle at site (its /server/api/pid/find address leads to it)."""
    return json.loads(fetch(f"{site}/server/api/pid/find?id={urllib.parse.quote(handle, safe='/')}", cache))


def dspace_meta(item, *keys):
    """The first value of the first of keys in a DSpace item's metadata ("" when none)."""
    meta = item.get("metadata", {})
    for key in keys:
        values = meta.get(key) or []
        if values:
            return values[0].get("value", "")
    return ""


def pdf_pages_html(pdf_path):
    """[(title, html, first page, last page)] of a PDF, one per chapter of its bookmarks (one per ten pages when it
    has none): its text page by page, with "[Page 12]" marks so the toolkit can say where a passage is."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    total = len(reader.pages)

    def flat(items, level=0):
        """[(level, title, page index)] of the bookmarks."""
        out = []
        for it in items:
            if isinstance(it, list):
                out += flat(it, level + 1)
                continue
            try:
                out.append((level, str(it.title).strip(), reader.get_destination_page_number(it)))
            except Exception:  # noqa: BLE001 - a bookmark without a page
                continue
        return out
    try:
        marks = flat(reader.outline)
    except Exception:  # noqa: BLE001
        marks = []
    tops = [(t, p) for lvl, t, p in marks if lvl == 0 and t]
    tops = sorted({p: (t, p) for t, p in tops}.values(), key=lambda x: x[1])
    if len(tops) < 2:
        tops = [(f"Pages {i + 1} to {min(total, i + 10)}", i) for i in range(0, total, 10)]
    elif tops[0][1] > 0:
        tops.insert(0, ("Front matter", 0))
    subs = {}
    for lvl, t, p in marks:
        if lvl == 1 and t:
            subs.setdefault(p, []).append(t)
    out = []
    for i, (title, start) in enumerate(tops):
        end = tops[i + 1][1] if i + 1 < len(tops) else total
        parts = []
        for n in range(start, max(start + 1, end)):
            for heading in subs.get(n, []):
                parts.append(f"<h2>{esc(heading)}</h2>")
            parts.append(f'<p class="pagenum" id="page-{n + 1}">[Page {n + 1}]</p>')
            try:
                text = reader.pages[n].extract_text() or ""
            except Exception:  # noqa: BLE001 - a page that cannot be read
                text = ""
            for para in re.split(r"\n\s*\n", text):
                line = " ".join(para.split())
                if line:
                    parts.append(f"<p>{esc(line)}</p>")
        out.append((title, "\n".join(parts), start + 1, max(start + 1, end)))
    return out


def dspace_book(entry, work, cache=None, left_out=None):
    """The Book of one reference work (a sources.DSPACE entry): its record, licence check, original PDF (downloaded
    only to read its text; the release links the official address, never a copy) and a page per chapter."""
    site, handle, name, title, subject, body, expected = entry
    left_out = left_out if left_out is not None else []
    item = dspace_record(site, handle, cache)
    licence = licence_short(dspace_meta(item, "dc.rights", "dc.rights.license"), dspace_meta(item, "dc.rights.uri"))
    if not licence_kind(licence):
        left_out.append({"title": title, "reason": f"Its record's licence ({licence or 'none'}) is not one the "
                         "toolkit may repackage."})
        return None
    if licence_short(expected) != licence:
        print(f"Note: {title}: the record says {licence}, the source list {expected}; the record is used.")
    bundles = json.loads(fetch(item["_links"]["bundles"]["href"], cache))["_embedded"]["bundles"]
    original = next((b for b in bundles if b.get("name") == "ORIGINAL"), None)
    if original is None:
        left_out.append({"title": title, "reason": "Its record has no original file."})
        return None
    streams = json.loads(fetch(original["_links"]["bitstreams"]["href"], cache))["_embedded"]["bitstreams"]
    pdfs = [s for s in streams if s.get("name", "").lower().endswith(".pdf")]
    if not pdfs:
        left_out.append({"title": title, "reason": "Its record has no PDF."})
        return None
    pdfs.sort(key=lambda s: (("eng" not in s["name"].lower() and "en." not in s["name"].lower()),
                             -int(s.get("sizeBytes") or 0)))
    stream = pdfs[0]
    content = stream["_links"]["content"]["href"]
    os.makedirs(work, exist_ok=True)
    local = os.path.join(work, f"{name}.pdf")
    if not os.path.exists(local):
        with open(local, "wb") as f:
            f.write(fetch(content, None, binary=True))
    page_url = f"{site}/bitstreams/{stream['uuid']}/download"
    language = dspace_meta(item, "dc.language.iso", "dc.language").lower()
    book = Book(name=name, title=title, subject=subject, level="reference", group="reference", publisher=body,
                country="International", licence=licence,
                licence_url=dspace_meta(item, "dc.rights.uri") or _licence_address(licence),
                source=f"{site}/handle/{handle}", language="eng" if language.startswith("en") or not language else
                language[:3], description=f"{dspace_meta(item, 'dc.title')} ({body}, "
                f"{dspace_meta(item, 'dc.date.issued')[:4]}).",
                authors=dspace_meta(item, "dc.contributor.author"),
                published=iso_date(dspace_meta(item, "dc.date.issued")),
                original_pdf={"url": page_url, "size": os.path.getsize(local), "sha256": file_sha256(local)})
    for i, (chapter_title, body_html, first, last) in enumerate(pdf_pages_html(local), 1):
        if chapter_title.startswith("Pages "):
            page_title = chapter_title if last > first else f"Page {first}"
        else:
            page_title = f"{chapter_title} (pages {first} to {last})" if last > first else f"{chapter_title} (page {first})"
        book.pages.append(Page(f"part-{i}-{slug(chapter_title, 40)}", page_title, body_html, i))
    return book


def _licence_address(short):
    """The Creative Commons address of a short licence name ("CC BY-NC-SA 3.0 IGO" -> its deed)."""
    m = re.match(r"CC ([A-Z-]+) (\d\.\d)( IGO)?", short)
    if not m:
        return ""
    return f"https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}/" + ("igo/" if m.group(3) else "")


# ====================================================================== non-profit web guides (sources.NONPROFIT)

_robots = {}


def allowed_by_robots(url, cache=None):
    """True when the site's robots.txt lets our USER_AGENT read url (a site without a robots.txt allows it). The
    robots.txt of each site is read once per run."""
    import urllib.robotparser
    parts = urllib.parse.urlsplit(url)
    site = f"{parts.scheme}://{parts.netloc}"
    if site not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.parse(fetch(site + "/robots.txt", cache).splitlines())
        except urllib.error.HTTPError as e:
            rp.parse([] if e.code in (404, 410) else ["User-agent: *", "Disallow: /"])
        except (urllib.error.URLError, OSError):
            rp.parse(["User-agent: *", "Disallow: /"])
        _robots[site] = rp
        try:
            delay = float(rp.crawl_delay(USER_AGENT) or 0)
        except (TypeError, ValueError):
            delay = 0
        if delay:
            CRAWL_DELAY[parts.hostname] = min(delay, 60.0)
    return _robots[site].can_fetch(USER_AGENT, url)


def page_links(page_html_text, base):
    """The absolute addresses linked from a web page, in order, without "#..." parts and repeats."""
    out = []
    for href in re.findall(r'<a\b[^>]*?\bhref="([^"]+)"', page_html_text, re.I):     # old pages write <A HREF=
        url = urllib.parse.urljoin(base, html.unescape(href)).split("#")[0]
        if url not in out:
            out.append(url)
    return out


def drop_hidden(text):
    """The HTML without what screen readers are told to skip (aria-hidden="true": anchor marks, icons). A hidden part
    that holds paragraphs, lists, tables or headings is kept: that is a collapsed section ("accordion") whose text
    is only hidden until it is opened. A heading's toggle button keeps its words as the heading."""
    text = re.sub(r'(<h[1-6]\b[^>]*>)\s*<button\b[^>]*>(.*?)</button>', r"\1\2", text, flags=re.S)
    text = re.sub(r'<img\b[^>]*\baria-hidden="true"[^>]*>', "", text)

    def small(m):
        """"" for a hidden mark or icon, the whole text for a collapsed section."""
        return m.group(0) if re.search(r"<(p|ul|ol|table|h[1-6]|dl|blockquote)\b", m.group(0)) else ""
    return re.sub(r'<(\w+)\b[^>]*\baria-hidden="true"[^>]*>(?:(?!<\1\b).)*?</\1>', small, text, flags=re.S)


def first_heading(page_html_text):
    """The words of a web page's first <h1> (or its <title>), "" when it has neither."""
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", page_html_text, re.S) or \
        re.search(r"<title\b[^>]*>(.*?)</title>", page_html_text, re.S)
    if not m:
        return ""
    words = re.sub(r"<small\b[^>]*>.*?</small>", " ", m.group(1), flags=re.S)     # a subtitle, not the title
    words = re.sub(r'<span class="in-resource-sub">.*$', " ", words, flags=re.S)   # W3C's "in <the resource>"
    words = re.sub(r"<br\b[^>]*>", " ", words)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", words)).split())


def article_content(page_html_text, entry):
    """The article's own HTML: between entry["content"]'s start and end marks, without its first <h1> (the page
    gets its own), the parts entry["drop"] names, and what is hidden from screen readers."""
    start, end = entry["content"]
    m = re.search(start, page_html_text)
    body = page_html_text[m.end():] if m else page_html_text
    m = re.search(end, body)
    body = body[:m.start()] if m else body
    body = re.sub(r"<h1\b[^>]*>.*?</h1>", "", body, count=1, flags=re.S)
    for pattern in entry.get("drop", []):
        body = re.sub(pattern, "", body, flags=re.S)
    return drop_hidden(body)


def webguide_plan(entry, cache=None):
    """[(article address, part name)] of a non-profit guide, in reading order: the articles linked from its part
    pages (entry["units"]) or contents pages (entry["start"]), or listed in its sitemap (sorted into parts by
    entry["unit_rules"]); at most entry["limit"]."""
    plan, seen = [], set()
    pages = re.compile(entry["pages"])

    def add(url, unit):
        """Add one article once."""
        if pages.match(url) and url not in seen:
            seen.add(url)
            plan.append((url, unit))
    for start in entry.get("start", []):
        text = fetch(start, cache)
        links = page_links(text, start)
        units = [u for u in links if entry.get("units") and re.match(entry["units"], u)]
        for unit_url in units:
            if not allowed_by_robots(unit_url, cache):
                continue
            unit_text = fetch(unit_url, cache)
            unit = first_heading(unit_text)
            for url in page_links(unit_text, unit_url):
                add(url, unit)
        for url in links:
            add(url, "")
    if entry.get("sitemap"):
        found = [html.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", fetch(entry["sitemap"], cache))]
        for sub in [u for u in found if re.search(r"sitemap[^/]*$|\.xml(\.gz)?$", u)][:50]:
            # A sitemap index: the sitemaps it lists hold the pages.
            try:
                found += [html.unescape(u) for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", fetch(sub, cache))]
            except (urllib.error.URLError, OSError):
                continue
        rules = entry.get("unit_rules") or [(r".", "")]
        for _pattern, unit in rules:              # the parts in the order of the rules
            for url in found:
                if next((u for p, u in rules if re.search(p, url)), None) == unit:
                    add(url, unit)
    return plan[:entry.get("limit", 500)]


def webguide_book(entry, cache=None, left_out=None):
    """The Book of one web guide (a sources.NONPROFIT or sources.GUIDES entry), or None when its licence page no
    longer says what was checked (then it is added to left_out). Pages robots.txt does not allow, and pages without
    the guide's licence line (entry["page_mark"]), are left out and said in left_out. Each article keeps its
    headings, lists, tables and links; a picture is kept as "Picture: " and its description (alt text), pictures
    without one are left out; every page ends with the credit and licence line.
    Optional entry fields: group (default "nonprofit"), region, notice (a statement the licence asks to show),
    changes (for the credit line), published (else the newest "last reviewed" date of its pages), fetch_as
    ((regular expression, replacement): the address actually read for an article, such as a guide's one-page
    "/print" version)."""
    left_out = left_out if left_out is not None else []
    title = entry["title"]
    licence_html = fetch(entry["licence_page"], cache) if allowed_by_robots(entry["licence_page"], cache) else ""
    if not (re.search(entry["licence_text"], licence_html) or re.search(
            entry["licence_text"], " ".join(html.unescape(re.sub(r"<[^>]+>", " ", licence_html)).split()))):
        left_out.append({"title": title, "reason": f"Its licence page ({entry['licence_page']}) no longer states "
                         "the licence that was checked."})
        return None
    whole = bool(entry.get("unchanged"))       # a no-changes licence: every page whole, its text unchanged
    licence = entry["licence"] if entry["licence"] in sources.NO_CHANGES else licence_short(entry["licence"])
    if not licence_kind(licence, whole):
        left_out.append({"title": title, "reason": f"Its licence ({licence}) is not one the toolkit may repackage."})
        return None
    book = Book(name=entry["name"], title=title, subject=entry["subject"], level="reference",
                group=entry.get("group", "nonprofit"), publisher=entry["publisher"], country=entry["country"],
                licence=licence, licence_url=entry["licence_url"], source=entry["source"], unchanged=whole,
                description=entry["description"], region=entry.get("region", ""), notice=entry.get("notice", ""),
                changes=entry.get("changes") or "made into web pages with the site's menus and pictures left out "
                                                 "(their descriptions kept)")
    dates = []
    plan = webguide_plan(entry, cache)
    paths, skipped = {}, 0
    for url, _unit in plan:
        path = slug(urllib.parse.urlsplit(url).path.strip("/").rsplit("/", 1)[-1] or "page", 50)
        while path in paths.values() or path in ("index", "style-css"):
            path += "-2"
        paths[url] = path
    for number, (url, unit) in enumerate(plan, 1):
        read = re.sub(entry["fetch_as"][0], entry["fetch_as"][1], url) if entry.get("fetch_as") else url
        if not allowed_by_robots(read, cache) or not allowed_by_robots(url, cache):
            skipped += 1
            continue
        try:
            try:
                text = fetch(read, cache)
            except urllib.error.HTTPError:
                if read == url:
                    raise
                text = fetch(url, cache)              # a page without a one-page version
        except (urllib.error.URLError, OSError):
            skipped += 1
            continue
        if entry.get("page_mark") and not re.search(entry["page_mark"], text):
            left_out.append({"title": f"{title}: {url}", "reason": "This page does not carry the guide's licence "
                             "line."})
            continue
        dates.append(page_date(text))
        body = _Cleaner(paths, url).clean(article_content(text, entry))
        body = re.sub(r'<a href="[^"]*#top">.*?</a>', "", body, flags=re.S)        # "Back to Top" links
        body = re.sub(r'<a href="[^"]*">\s*</a>', "", body)                        # links without words
        if whole:                                 # the licence asks for each document's address and notice
            body += (f'<p class="original">Original: <a href="{esc(url)}">{esc(url)}</a>. '
                     f'{esc(entry.get("notice", ""))} {UNCHANGED}</p>')
        book.pages.append(Page(paths[url], first_heading(text) or paths[url], body, 0, unit))
    if skipped:
        left_out.append({"title": title, "reason": f"{skipped} pages could not be read or are not allowed by the "
                         "site's robots.txt."})
    book.published = entry.get("published") or newest_date(dates)
    return book


# ====================================================================== official PDF documents (sources.PDF_DOCS)

# Distribution Statement A, as US military publications print it ("DISTRIBUTION RESTRICTION: Approved for public
# release; distribution is unlimited."), and the words of every other (restricted) marking.
DISTRIBUTION_A = re.compile(r"approved\s+for\s+public\s+release\s*[;:,.]?\s*distribution\s+is\s+unlimited", re.I)
RESTRICTED = re.compile(r"distribution\s+(statement\s+)?[B-F]\b|distribution\s+authorized\s+to|authorized\s+to\s+U\.?\s?"
                        r"S\.?\s+Government\s+agencies|for\s+official\s+use\s+only|\bFOUO\b|controlled\s+unclassified"
                        r"|\bCUI\b|\bNOFORN\b|export[- ]controlled", re.I)
# Part titles that are never kept from a field manual: weapons, tactics, combat and anything meant to harm.
NOT_FIELD_SAFE = re.compile(r"\b(weapons?|small\s+arms|ammunition|firing|marksmanship|ambush\w*|combat\s+operations?|"
                            r"tactic\w*|camouflage|evasion|resistance|escape|explosives?|demolitions?|mines?|"
                            r"grenades?|booby|sniper|patrol\w*|raids?|assault|interrogation|captivity|"
                            r"mountain\s+warfare|offensive|defensive\s+operations)\b", re.I)
FIGURE_LINE = re.compile(r"^\s*(Figure\s+[A-Z]?-?\d+(?:-\d+)?[a-z]?\.?)(?:\s*[\u2014\u2013]\s*|\s+)(.{2,200}?)\s*$")


class PdfText:
    """The words of a PDF's pages: read with pypdfium2 (BSD/Apache) when it is installed, which keeps words whole
    where pypdf sometimes spaces out letters ("a f t e r"), else with pypdf. Lines are cleaned: a page's garbled
    running head (made of control characters) is dropped, and the Wingdings bullet a manual's lists start with
    ("z Look for ...") becomes "•"."""

    def __init__(self, path):
        """Open the PDF at path."""
        try:
            import pypdfium2 as pdfium
            self._doc, self._pypdf = pdfium.PdfDocument(path), None
            self.count = len(self._doc)
        except ImportError:
            from pypdf import PdfReader
            self._doc, self._pypdf = None, PdfReader(path)
            self.count = len(self._pypdf.pages)

    def raw(self, n):
        """The text of page n as the library gives it ("" when it cannot be read)."""
        try:
            if self._doc is not None:
                return self._doc[n].get_textpage().get_text_range()
            return self._pypdf.pages[n].extract_text() or ""
        except Exception:  # noqa: BLE001 - a page that cannot be read
            return ""

    def lines(self, n):
        """The cleaned lines of page n."""
        out = []
        for line in self.raw(n).replace("\r", "").split("\n"):
            if re.search(r"[\x00-\x08\x0e-\x1f]", line):
                continue
            line = re.sub(r"^\s*[z\uf06e\uf0b7\uf0a7]\s+(?=[A-Z0-9(])", "• ", line).strip()
            if line:
                out.append(line)
        return out


def archive_pdf(identifier, cache=None):
    """(download address, item page) of the PDF of an Internet Archive item (its metadata lists the files; the
    "Text PDF", the one with the words, is preferred)."""
    meta = json.loads(fetch(f"https://archive.org/metadata/{identifier}", cache))
    files = [f for f in meta.get("files", []) if f.get("name", "").lower().endswith(".pdf")]
    if not files:
        raise ValueError("the item has no PDF")
    files.sort(key=lambda f: (f.get("format") != "Text PDF", -int(f.get("size") or 0)))
    name = files[0]["name"]
    return (f"https://archive.org/download/{identifier}/{urllib.parse.quote(name)}",
            f"https://archive.org/details/{identifier}")


def newest_pdf(page_text, base, pattern=r"\.pdf$"):
    """The newest PDF linked from an official publication page: the one whose address has the latest year and month
    ("...-2026-10.pdf"), else the last one listed. "" when the page links none."""
    pdfs = [urllib.parse.urljoin(base, html.unescape(h)) for h in re.findall(r'href="([^"]+\.pdf)"', page_text)]
    pdfs = list(dict.fromkeys(u for u in pdfs if re.search(pattern, u, re.I)))
    if not pdfs:
        return ""

    def when(url):
        """(year, month) found in the address, (0, 0) when none."""
        m = re.findall(r"(?<!\d)(19\d\d|20\d\d)(?:[-_](0[1-9]|1[0-2]))?(?!\d)", url.rsplit("/", 1)[-1])
        return max(((int(y), int(mo or 0)) for y, mo in m), default=(0, 0))
    return max(enumerate(pdfs), key=lambda x: (when(x[1]), x[0]))[1]


def front_text(pdf_path, pages=12):
    """The words of the first pages of a PDF (where the title page, the distribution statement and the copyright
    lines are), in one line."""
    text = PdfText(pdf_path)
    return " ".join(" ".join(text.raw(n) for n in range(min(pages, text.count))).split())


def without_page_number(title):
    """A part title without the printed page number at its end ("Licensing Information 19" -> "Licensing
    Information"); a bare label such as "Chapter 3" or "Appendix A" is kept as it is."""
    title = " ".join(title.split())
    if re.fullmatch(r"(chapter|appendix|part|section|annex)\s+\S+", title, re.I):
        return title
    return re.sub(r"(?<=\D)\s*\.*\s*\d+$", "", title) or title


def manual_parts(pdf_path):
    """[(title, first page index, last page index + 1)] of a manual: its top bookmarks (or the bookmarks under a
    single top one); without useful bookmarks, the pages that begin with "CHAPTER 3" or "APPENDIX A" and the title
    on the next line. A bookmark that only says "Chapter 3" gets the title printed on its page."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    total = len(reader.pages)

    text = PdfText(pdf_path)

    def lines(n):
        """The first lines of page n."""
        return text.lines(n)[:12]

    def printed_title(n, label):
        """The title printed after "Chapter 3" (or "APPENDIX A") on page n, "" when it is not found."""
        got = lines(n)
        for i, line in enumerate(got):
            if re.fullmatch(re.escape(label) + r"\.?", line, re.I) and i + 1 < len(got):
                return got[i + 1].title() if got[i + 1].isupper() else got[i + 1]
            m = re.match(re.escape(label) + r"\.?\s+(.{3,80})$", line, re.I)
            if m:
                return m.group(1).title() if m.group(1).isupper() else m.group(1)
        return ""

    marks = []
    try:
        outline = reader.outline
        tops = [o for o in outline if not isinstance(o, list)]
        if len(tops) == 1 and len(outline) > 1 and isinstance(outline[1], list):
            tops = [o for o in outline[1] if not isinstance(o, list)]
        else:
            # A Navy course groups its chapters under bookmarks without a page ("CHAPTERS", "APPENDIX"), next to
            # lists of every figure and page ("FIGURES", "PAGES"): the groups' entries are taken, those lists not.
            grouped, heading = [], None
            for o in outline:
                if isinstance(o, list):
                    if heading is not None and not re.match(r"(figures?|pages?|tables?|assignments?)$",
                                                            str(heading.title).strip(), re.I):
                        grouped += [x for x in o if not isinstance(x, list)]
                    heading = None
                    continue
                try:
                    has_page = reader.get_destination_page_number(o) is not None
                except Exception:  # noqa: BLE001
                    has_page = False
                if has_page:
                    grouped.append(o)
                    heading = None
                else:
                    heading = o
            if len(grouped) > len(tops):
                tops = grouped
        for o in tops:
            try:
                page = reader.get_destination_page_number(o)
                if page is not None:
                    marks.append((without_page_number(str(o.title)), page))
            except Exception:  # noqa: BLE001 - a bookmark without a page
                continue
    except Exception:  # noqa: BLE001
        marks = []
    if len({t.casefold() for t, _p in marks}) < max(2, len(marks) // 2):
        marks = []                                # no bookmarks, or the same title on all of them
        for n in range(total):
            for line in lines(n)[:4]:
                m = re.match(r"^(?:\d+-1\s+)?(CHAPTER|APPENDIX)\s+(\d+|[A-Z]|[IVX]+)\b\.?\s*(.*)$", line, re.I)
                if m and not re.match(r"[,;(]|[a-z]|.*\bpages?\s+\d", m.group(3)):   # not "chapter 12, pages ..."
                    label = f"{m.group(1).title()} {m.group(2)}"
                    title = m.group(3).strip()
                    title = title.title() if title.isupper() else title
                    marks.append((without_page_number(f"{label}: {title}") if title else label, n))
                    break
        last = {}
        for title, n in marks:                    # a label seen twice: the first was the table of contents
            last[title.split(":")[0]] = (title, n)
        marks = sorted(last.values(), key=lambda x: x[1])
    if marks and min(n for _t, n in marks) > 0:
        marks.insert(0, ("Front matter", 0))      # the pages before the first part are kept too
    marks = sorted({p: (t.title() if t.isupper() else t, p) for t, p in marks}.values(), key=lambda x: x[1])
    out = []
    for i, (title, start) in enumerate(marks):
        m = re.fullmatch(r"(Chapter|Appendix)\s+(\d+|[A-Z])", title, re.I)
        if m:
            words = printed_title(start, title)
            title = f"{m.group(1).title()} {m.group(2)}: {words}" if words else title
        end = marks[i + 1][1] if i + 1 < len(marks) else total
        out.append((title, start, max(start + 1, end)))
    if not out:
        out = [(f"Pages {i + 1} to {min(total, i + 10)}", i, min(total, i + 10)) for i in range(0, total, 10)]
    return out


def part_html(text, start, end):
    """The text of pages start..end-1 as HTML paragraphs, with "[Page 12]" marks, and every figure's caption line
    ("Figure 4-12. Square knot") as a paragraph of its own marked as a figure, so the reader hears which drawing the
    text speaks of (the drawings themselves are not in the book)."""
    return lines_html([(n, i, line) for n in range(start, end) for i, line in enumerate(text.lines(n) or [""])])


def lines_html(items, headings=None):
    """The HTML of a run of a PDF's lines [(page index, line number on the page, line)], as part_html describes: a
    "[Page 12]" mark before each page's first line, paragraphs, list items and figure captions. headings: {position
    in items: level} of lines that are headings (sections_of_pdf); they become <h2>/<h3> with their words unchanged."""
    parts, para = [], []

    def close():
        """End the open paragraph."""
        if para:
            parts.append(f"<p>{esc(' '.join(' '.join(para).split()))}</p>")
            para.clear()
    for k, (n, i, line) in enumerate(items):
        if i == 0:
            close()
            parts.append(f'<p class="pagenum" id="page-{n + 1}">[Page {n + 1}]</p>')
        if headings and k in headings:
            close()
            parts.append(f"<h{headings[k]}>{esc(line)}</h{headings[k]}>")
            continue
        if line.startswith("• ") and para:            # a list item starts a paragraph of its own
            close()
        m = FIGURE_LINE.match(line)
        if m and not re.search(r"\.{4,}|\s\d+-\d+\s*$", line) and not re.match(
                r"(shows?|illustrates?|is|are|gives|lists|depicts|contains|and|in|on|of|as|for|to)\b",
                m.group(2), re.I):                    # not a list-of-figures line nor a sentence about it
            close()
            parts.append(f'<p class="figure" role="note"><strong>{esc(m.group(1))}</strong> '
                         f'{esc(m.group(2))} (a drawing in the original)</p>')
        elif line.strip():
            para.append(line)
        if k + 1 == len(items) or items[k + 1][0] != n:
            close()                                   # a paragraph ends with its page, as before
    close()
    return "\n".join(parts)


def sections_of_pdf(text):
    """A rulebook's own numbered headings, found in its text in order: "Section 1: Introduction", then "1.1
    Definition of braille", "1.2 ...", "Section 2: ...", and "Appendix 1: ...". A line counts only when it is the next
    number expected (so contents lines, running heads and cross-references such as "Section 3.17 for the ..." are not
    taken). Returns (items, headings, titles): every line of the PDF [(page index, line number, line)], {position:
    level} and [(position, title)] of the headings."""
    items = [(n, i, line) for n in range(text.count) for i, line in enumerate(text.lines(n) or [""])]
    headings, titles = {}, []
    section, sub, appendix = 0, 0, 0
    for k, (_n, _i, line) in enumerate(items):
        if "...." in line:
            continue
        m = re.fullmatch(r"Section (\d+): (\S.*)", line)
        if m and int(m.group(1)) == section + 1:
            section, sub = section + 1, 0
            headings[k] = 2
            titles.append((k, line))
            continue
        m = re.fullmatch(r"(\d{1,2})\.(\d{1,2}) (\S.*)", line)
        if m and section and int(m.group(1)) == section and int(m.group(2)) == sub + 1:
            sub += 1
            headings[k] = 3
            titles.append((k, line))
            continue
        m = re.fullmatch(r"Appendix (\d+): (\S.*)", line)
        if m and section and int(m.group(1)) == appendix + 1:
            appendix += 1
            headings[k] = 2
            titles.append((k, line))
    return items, headings, titles


def section_pages(text):
    """[Page] of a rulebook split at its own numbered headings (sections_of_pdf): what comes before the first
    section ("Front matter"), then one page per section and per numbered part of a section, then the appendices.
    Only the places where pages begin change: every line stays, in order, so the pages read one after another are the
    whole text (only format and navigation, which a no-changes licence allows)."""
    items, headings, titles = sections_of_pdf(text)
    starts = [0] + [k for k, _t in titles if k] if titles else [0]
    names = dict(titles)
    pages = []
    for number, (a, b) in enumerate(zip(starts, starts[1:] + [len(items)]), 1):
        if a == b:
            continue
        title = names.get(a, "Front matter")
        first, last = items[a][0] + 1, items[b - 1][0] + 1
        label = f"{title} (pages {first} to {last})" if last > first else f"{title} (page {first})"
        part = {k - a: lvl for k, lvl in headings.items() if a <= k < b}
        pages.append(Page(f"part-{number}-{slug(title, 40)}", label, lines_html(items[a:b], part), number))
    return pages


def pdfdoc_book(entry, work, cache=None, left_out=None):
    """The Book of one official PDF (a sources.PDF_DOCS entry): the PDF is found (an Internet Archive item, the
    official address in entry["pdf"], or the newest PDF on an official publication page), its licence checked (the
    licence line of its page or of entry["licence_page"], such as an agency's copyright policy, or for a US military
    manual Distribution Statement A in its own front matter and no restricted marking), then made into one page per
    chapter; for a field manual, parts about weapons, tactics or harm (NOT_FIELD_SAFE) are left out. None when it is
    not allowed (said in left_out). Its "published" is entry["published"], else the date in the PDF's own
    information."""
    left_out = left_out if left_out is not None else []
    title = entry["title"]
    licence_page = entry.get("licence_page") or (entry.get("page") if not entry.get("archive") else "")
    if licence_page and entry.get("licence_text"):
        if not allowed_by_robots(licence_page, cache):
            left_out.append({"title": title, "reason": "The site's robots.txt does not allow reading its page."})
            return None
        words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fetch(licence_page, cache))).split())
        if not re.search(entry["licence_text"], words):
            left_out.append({"title": title, "reason": f"Its page ({licence_page}) no longer states the licence that "
                             "was checked."})
            return None
    if entry.get("archive"):
        pdf_url, page = archive_pdf(entry["archive"], cache)
    elif entry.get("pdf"):
        pdf_url, page = entry["pdf"], entry.get("page") or entry["pdf"]
    else:
        page = entry["page"]
        if not allowed_by_robots(page, cache):
            left_out.append({"title": title, "reason": "The site's robots.txt does not allow reading its page."})
            return None
        pdf_url = newest_pdf(fetch(page, cache), page, entry.get("pdf_pattern", r"\.pdf$"))
        if not pdf_url:
            left_out.append({"title": title, "reason": "Its page links no PDF."})
            return None
    if not allowed_by_robots(pdf_url, cache):
        left_out.append({"title": title, "reason": "The site's robots.txt does not allow reading its PDF."})
        return None
    os.makedirs(work, exist_ok=True)
    local = os.path.join(work, f"{entry['name']}.pdf")
    if not os.path.exists(local):
        with open(local, "wb") as f:
            f.write(fetch(pdf_url, None, binary=True))
    text = PdfText(local)
    sample = range(0, text.count, max(1, text.count // 40))
    with_words = sum(1 for n in sample if len(" ".join(text.lines(n))) > 80)
    if with_words < 0.5 * len(sample):
        left_out.append({"title": title, "reason": "Most of its pages are scanned pictures without their words (no "
                         "text layer), so it cannot be read aloud from this copy."})
        return None
    front = front_text(local)
    if entry.get("pdf_licence_text") and not re.search(entry["pdf_licence_text"], " ".join(front.split())):
        left_out.append({"title": title, "reason": "Its PDF no longer states the licence that was checked."})
        return None
    if entry.get("distribution_a"):
        bad = RESTRICTED.search(front)
        if not DISTRIBUTION_A.search(front) or bad:
            left_out.append({"title": title, "reason": "Its front matter does not show Distribution Statement A "
                             f"(approved for public release; distribution is unlimited){' but ' + bad.group(0) if bad else ''}."})
            return None
    licence = entry["licence"]
    whole = bool(entry.get("unchanged"))         # a no-changes licence: the whole PDF, its text unchanged
    if not licence_kind(licence_short(licence), whole) and not licence_kind(licence, whole):
        left_out.append({"title": title, "reason": f"Its licence ({licence}) is not one the toolkit may repackage."})
        return None
    book = Book(name=entry["name"], title=title, subject=entry["subject"], level="reference", group=entry["group"],
                publisher=entry["publisher"], country=entry["country"], licence=licence,
                licence_url=entry["licence_url"], source=page, description=entry["description"],
                original_pdf={"url": pdf_url, "size": os.path.getsize(local), "sha256": file_sha256(local)},
                published=entry.get("published") or pdf_date(local), region=entry.get("region", ""),
                notice=entry.get("notice", ""), unchanged=whole,
                changes="its text made into web pages, one per chapter, with each drawing's caption kept as text"
                        + ("; parts about weapons and tactics left out" if entry.get("distribution_a") else ""))
    skipped = []
    if entry.get("split_sections"):              # one page per numbered section of its own text (sections_of_pdf)
        book.pages += section_pages(text)
        return book
    for i, (part_title, start, end) in enumerate(manual_parts(local), 1):
        if entry.get("distribution_a") and NOT_FIELD_SAFE.search(part_title):
            if part_title not in skipped:
                skipped.append(part_title)
            continue
        label = f"{part_title} (pages {start + 1} to {end})" if end - start > 1 else f"{part_title} (page {start + 1})"
        book.pages.append(Page(f"part-{i}-{slug(part_title, 40)}", label, part_html(text, start, end), i))
    if skipped:
        book.description += " Left out: " + "; ".join(skipped) + "."
    return book


# ====================================================================== laws and regulations (sources.LAWS)

def cfr_xml_html(xml_text, subpart=""):
    """The HTML of one part of the US Code of Federal Regulations from govinfo's annual edition (its "CFRGRANULE"
    XML): every subpart as <h2 class="cfr-subpart">, every section and appendix as <h3 class="cfr-section"> ("§
    382.1 What is the purpose of this part?"), its own headings as <h4>, paragraphs, tables with their title, and
    the authority and source notes. The part's table of contents and printed page numbers are left out. subpart:
    only that subpart ("F"), for a part of which only one subpart is wanted."""
    root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    out = []

    def inline(el):
        """The text of el with italics kept, escaped."""
        parts = [esc(el.text or "")]
        for child in el:
            if child.tag in ("PRTPAGE", "FTREF"):
                pass
            elif child.tag in ("E", "I"):
                parts.append(f"<em>{inline(child)}</em>")
            elif child.tag == "SU":
                parts.append(esc(small_text(_text(child), True)))
            else:
                parts.append(inline(child))
            parts.append(esc(child.tail or ""))
        return " ".join("".join(parts).split())

    def block(el):
        """Write el and what it holds."""
        tag = el.tag
        if tag in ("FDSYS", "CONTENTS", "PRTPAGE", "EAR", "STARS", "RESERVED"):
            return
        if tag == "SUBPART":
            hd = el.find("HD")
            if subpart and not (hd is not None and re.match(rf"Subpart {re.escape(subpart)}\b", _text(hd))):
                return
            if hd is not None:
                out.append(f'<h2 class="cfr-subpart">{inline(hd)}</h2>')
            for child in el:
                if child is not hd:
                    block(child)
            return
        if tag == "SECTION":
            number, subject = _text(el.find("SECTNO")), _text(el.find("SUBJECT"))
            out.append(f'<h3 class="cfr-section">{esc(number)} {esc(subject)}</h3>')
            for child in el:
                if child.tag not in ("SECTNO", "SUBJECT"):
                    block(child)
            return
        if tag == "APPENDIX":
            hd = el.find("HD")
            out.append(f'<h3 class="cfr-section">{inline(hd) if hd is not None else "Appendix"}</h3>')
            for child in el:
                if child is not hd:
                    block(child)
            return
        if tag == "HD":
            if el.get("SOURCE") != "HED" or out:
                out.append(f"<h4>{inline(el)}</h4>")
            return
        if tag in ("P", "FP", "PSPACE", "NOTE", "CITA", "EFFDNOTP", "EDNOTE", "SECAUTH", "FTNT", "EXAMPLE"):
            if len(el) and all(c.tag in ("P", "FP", "HD", "PSPACE") for c in el) and not (el.text or "").strip():
                for child in el:
                    block(child)
            else:
                text = inline(el)
                if text:
                    out.append(f"<p>{text}</p>")
            return
        if tag in ("AUTH", "SOURCE"):
            out.append("<p>" + " ".join(inline(c) for c in el) + "</p>")
            return
        if tag == "GPOTABLE":
            caption = el.find("TTITLE")
            rows = ["<table>" + (f"<caption>{inline(caption)}</caption>" if caption is not None else "")]
            heads = [inline(c) for c in el.iter("CHED")]
            if heads:
                rows.append("<tr>" + "".join(f"<th>{h}</th>" for h in heads) + "</tr>")
            for row in el.iter("ROW"):
                rows.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row.findall("ENT")) + "</tr>")
            out.append("".join(rows) + "</table>")
            return
        if tag in ("GPH", "MATH"):
            out.append("<p>(A drawing or formula in the printed edition.)</p>")
            return
        for child in el:
            block(child)
        if not len(el) and (el.text or "").strip() and tag not in ("DATE", "VOL", "TITLE", "CFRTITLE"):
            out.append(f"<p>{inline(el)}</p>")

    for el in root:
        block(el)
    return "\n".join(out)


def govinfo_edition(kind, spec, cache=None):
    """(address, text) of the newest annual edition on govinfo.gov of a part of the CFR (kind "cfr", spec {title,
    volume, part}) or a chapter of the US Code (kind "usc", spec {title, file}); the editions of this year and the
    four before are tried, newest first (a volume number may move by one between editions). Raises LookupError
    when none is found."""
    year = datetime.date.today().year
    tried = []
    for y in range(year, year - 5, -1):
        if kind == "cfr":
            t, v, p = spec["title"], spec["volume"], spec["part"]
            urls = [f"https://www.govinfo.gov/content/pkg/CFR-{y}-title{t}-vol{vol}/xml/CFR-{y}-title{t}-vol{vol}-"
                    f"part{p}.xml" for vol in (v, v + 1, v - 1) if vol > 0]
        else:
            t, f = spec["title"], spec["file"]
            urls = [f"https://www.govinfo.gov/content/pkg/USCODE-{y}-title{t}/html/USCODE-{y}-title{t}-{f}.htm"]
        for url in urls:
            tried.append(url)
            try:
                text = fetch(url, cache)
            except urllib.error.HTTPError as e:
                if e.code not in (403, 404, 410):
                    raise
                continue
            # govinfo answers a missing package with its "not found" web page (status 200): only the real text counts.
            if ("<CFRGRANULE" in text) if kind == "cfr" else ("currentthrough:" in text or "section-head" in text):
                return url, text
    raise LookupError(f"no edition found (tried {len(tried)} addresses, the last {tried[-1]})")


def law_pages(page_html_text, entry, base=""):
    """[(unit, title, body HTML)] of a law's full text: it is cut where entry["split"] matches (a section or part
    heading: one page each, titled with that heading's words) and where entry["unit"] matches (a subpart or chapter
    heading: the pages after it are listed under it in the contents; its own words, if any, become a page). The
    text before the first cut is the "Introduction" page when it says anything. entry["content"] (start, end) marks
    the law's text on the page, entry["drop"] parts left out (editorial notes, menus) and entry["rewrite"]
    [(regular expression, replacement)] tidies the publisher's HTML (number-only headings made plain text)."""
    text = page_html_text
    start, end = entry.get("content") or ("", "")
    m = re.search(start, text) if start else None
    text = text[m.end():] if m else text
    m = re.search(end, text) if end else None
    text = text[:m.start()] if m else text
    for pattern in entry.get("drop", []):
        text = re.sub(pattern, "", text, flags=re.S)
    for pattern, replacement in entry.get("rewrite", []):
        text = re.sub(pattern, replacement, text, flags=re.S)
    text = drop_hidden(text)
    cuts = [(m.start(), "page") for m in re.finditer(entry["split"], text)]
    if entry.get("unit"):
        cuts += [(m.start(), "unit") for m in re.finditer(entry["unit"], text)]
    cuts.sort()
    pieces = [(0, "intro")] + cuts + [(len(text), "end")]
    out, unit = [], ""

    def words(fragment):
        """The plain words of some HTML."""
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())

    def clean(fragment):
        """The fragment's HTML with only plain structure (its loose <div>, <span> and <section> tags dropped, as a
        cut can leave them unbalanced; links kept as their words)."""
        body = _Cleaner({}, base).clean(fragment)
        body = re.sub(r"</?(div|span|section|a)\b[^>]*>", "", body)      # links to other laws are not in the book
        body = re.sub(r"<(p|h[2-6]|li)>\s*</\1>", "", body)
        return body.strip()

    for (pos, kind), (nxt, _k) in zip(pieces, pieces[1:]):
        chunk = text[pos:nxt]
        heading = re.match(r"\s*(?:<[^>]+>\s*)*?<(h[1-6])\b[^>]*>(.*?)</\1>", chunk, re.S)
        title = words(heading.group(2)) if heading and kind != "intro" else ""
        if not title and kind != "intro":
            title = words(chunk)[:80]
        rest = chunk[heading.end():] if heading and kind != "intro" else chunk
        if kind == "unit":
            unit = title
            if len(words(rest)) > 40:
                out.append((unit, title, clean(rest)))
            continue
        if kind == "intro":
            if len(words(rest)) > 80:
                out.append(("", "Introduction", clean(rest)))
            continue
        out.append((unit, title or "Section", clean(rest)))
    return out


def lawdoc_book(entry, cache=None, left_out=None):
    """The Book of one law or regulation (a sources.LAWS entry), or None when its licence page no longer says what
    was checked or its text cannot be found (said in left_out). Where the text comes from:
      cfr   {title, volume, part, subpart?} (or a list of them): parts of the US Code of Federal Regulations,
            govinfo's newest annual edition (the eCFR's own robots.txt shuts out automated readers of its full-text
            services)
      usc   [{title, file}]: chapters of the US Code, govinfo's newest annual edition (HTML)
      urls  the official full-text pages of the law (Justice Laws Canada, legislation.gov.uk, BC Laws)
    The pages are cut by law_pages (entry["split"], entry["unit"]). Its "published" is entry["published"], else
    the edition's own date (the CFR's revision date, the US Code's "current through" date) or the first match of
    entry["date_pattern"] in the text ("last amended on 2023-04-27")."""
    left_out = left_out if left_out is not None else []
    title = entry["title"]
    page = entry["licence_page"]
    if not allowed_by_robots(page, cache):
        left_out.append({"title": title, "reason": f"The site's robots.txt does not allow reading {page}."})
        return None
    words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fetch(page, cache))).split())
    if not re.search(entry["licence_text"], words):
        left_out.append({"title": title, "reason": f"Its licence page ({page}) no longer states the licence that was "
                         "checked."})
        return None
    licence = entry["licence"]
    if not licence_kind(licence) and not licence_kind(licence_short(licence)):
        left_out.append({"title": title, "reason": f"Its licence ({licence}) is not one the toolkit may repackage."})
        return None
    texts, published = [], ""
    cfr = entry.get("cfr") or []
    for spec in (cfr if isinstance(cfr, list) else [cfr]):
        url, xml_text = govinfo_edition("cfr", spec, cache)
        m = re.search(r"<DATE>([0-9-]+)</DATE>", xml_text)
        published = newest_date([published, m.group(1) if m else ""])
        texts.append((url, cfr_xml_html(xml_text, spec.get("subpart", ""))))
    for spec in entry.get("usc", []):
        url, text = govinfo_edition("usc", spec, cache)
        m = re.search(r"currentthrough:(\d{8})", text)
        published = newest_date([published, iso_date(m.group(1)) if m else ""])
        texts.append((url, text))
    for url in entry.get("urls", []):
        if not allowed_by_robots(url, cache):
            left_out.append({"title": title, "reason": f"The site's robots.txt does not allow reading {url}."})
            return None
        texts.append((url, fetch(url, cache)))
    if not texts:
        left_out.append({"title": title, "reason": "No text address is given."})
        return None
    if entry.get("date_pattern"):
        m = re.search(entry["date_pattern"], texts[0][1], re.I)
        published = newest_date([published, iso_date(m.group(1)) if m else ""])
    book = Book(name=entry["name"], title=title, subject=entry["subject"], level="reference",
                group=entry.get("group", "law"), publisher=entry["publisher"], country=entry["country"],
                region=entry.get("region", ""), licence=licence, licence_url=entry["licence_url"],
                source=entry["source"], description=entry["description"], notice=entry.get("notice", ""),
                published=entry.get("published") or published,
                changes=entry.get("changes") or "made into web pages, one per section or part, with editorial notes "
                                                 "and the site's menus left out; not an official version")
    paths = set()
    for url, text in texts:
        for unit, page_title, body in law_pages(text, entry, url):
            path = slug(page_title, 50)
            while path in paths or path in ("index", "style-css"):
                path += "-2"
            paths.add(path)
            book.pages.append(Page(path, page_title, body, 0, unit))
    return book


# ====================================================================== the run

def build(keys, out_dir, cache=None, pictures=False, local_osbooks=None, date=None):
    """Build the books of keys (see the module docstring) into out_dir and write manifest-<key>.json for each key.
    Returns {key: manifest}."""
    work = os.path.join(cache or out_dir, "work")
    manifests = {}
    catalogue = None
    plan = sources.expand_keys(keys) if keys else []
    if local_osbooks:
        plan = [f"local:{local_osbooks}"]
    for key in plan:
        if key.startswith("med:"):               # medicines: human and veterinary drug labels (medications.py)
            import medications                   # here, not at the top: medications imports this module
            manifests.update(medications.build_medicines([key], out_dir, cache, date))
            continue
        if key.startswith("pub:"):               # periodicals, journals, reports, news, history (periodicals.py)
            import periodicals                   # here, not at the top: periodicals imports this module
            # "pub:voa:recent+pub:voa:2026": pieces built one after another in this one job
            manifests.update(periodicals.build_periodicals(key.split("+"), out_dir, cache, date))
            continue
        books, left_out = [], []
        import updates                           # here, not at the top: updates imports this module
        sign = updates.fingerprint(key)          # the source's sign of change now, kept in the catalogue
        try:
            if key.startswith("osbooks:") or key.startswith("local:"):
                if catalogue is None:
                    catalogue = openstax_catalogue(cache) if not key.startswith("local:") else {}
                repo = key[6:] if key.startswith("local:") else clone_osbooks(key[8:], work, pictures)
                books = osbooks_books(repo, pictures, catalogue, left_out)
            elif key == "siyavula":
                for subject, grade, title, words in sources.SIYAVULA:
                    try:
                        b = siyavula_book(subject, grade, title, words, cache, left_out)
                    except Exception as e:  # noqa: BLE001 - one book's failure does not stop the others
                        left_out.append({"title": f"Siyavula {title}", "reason": f"It could not be read ({e})."})
                        b = None
                    if b is not None:
                        books.append(b)
            elif key == "dspace":
                for entry in sources.DSPACE:
                    try:
                        b = dspace_book(entry, work, cache, left_out)
                    except Exception as e:  # noqa: BLE001
                        left_out.append({"title": entry[3], "reason": f"It could not be read ({e})."})
                        b = None
                    if b is not None:
                        books.append(b)
            elif key.startswith("pdf:"):
                entry = next((e for e in sources.PDF_DOCS if e["name"] == key[4:]), None)
                if entry is None:
                    print(f"Unknown key {key}; skipped.")
                    continue
                try:
                    b = pdfdoc_book(entry, work, cache, left_out)
                except Exception as e:  # noqa: BLE001 - said in the manifest
                    left_out.append({"title": entry["title"], "reason": f"It could not be read ({e})."})
                    b = None
                if b is not None:
                    books.append(b)
            elif key.startswith("law:"):
                entry = next((e for e in sources.LAWS + sources.LAWS_MORE if e["name"] == key[4:]), None)
                if entry is None:
                    print(f"Unknown key {key}; skipped.")
                    continue
                try:
                    b = lawdoc_book(entry, cache, left_out)
                except Exception as e:  # noqa: BLE001 - said in the manifest
                    left_out.append({"title": entry["title"], "reason": f"It could not be read ({e})."})
                    b = None
                if b is not None:
                    books.append(b)
            elif key.startswith("nonprofit:") or key.startswith("guide:"):
                entry = next((e for e in sources.NONPROFIT + sources.GOV_GUIDES
                              if e["name"] == key.split(":", 1)[1]), None)
                if entry is None:
                    print(f"Unknown key {key}; skipped.")
                    continue
                try:
                    b = webguide_book(entry, cache, left_out)
                except Exception as e:  # noqa: BLE001 - said in the manifest
                    left_out.append({"title": entry["title"], "reason": f"It could not be read ({e})."})
                    b = None
                if b is not None:
                    books.append(b)
            else:
                print(f"Unknown key {key}; skipped.")
                continue
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
        entries = []
        for book in books:
            if not book.pages:
                left_out.append({"title": book.title, "reason": "No pages could be read."})
                continue
            entry = write_book(book, out_dir, date, versioned=True)
            entry["key"] = key                   # what to build again when its source changes (updates.py)
            entry["fingerprint"] = sign
            print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, {entry['licence']}")
            entries.append(entry)
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower().split("/")[-1])
        manifest = {"key": key, "release": "textbooks", "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "done": [key]}
        os.makedirs(out_dir, exist_ok=True)      # a key that built no book (a retired edition) still writes its manifest
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


def merge(manifest_paths, existing=None):
    """The catalogue textbooks.json from the manifests: the newest release of each book, the left-out books,
    sources.NOT_INCLUDED and the names of the groups (sources.GROUPS: group key -> collection name). existing:
    the textbooks.json published before (books it has that no manifest built again are kept)."""
    import updates                               # here, not at the top: updates imports this module
    books, done = {}, set((existing or {}).get("pieces_done", []))
    failed = dict((existing or {}).get("pieces_failed", {}))
    for old in (existing or {}).get("books", []):
        books[old["name"]] = old
    left = []
    for path in manifest_paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data.get("books", []):
            books[entry["name"]] = updates.merge_versions(books.get(entry["name"]), entry)   # every version kept
        left += data.get("left_out", [])
        done |= set(data.get("done", []))
        for k in data.get("failed", []):
            failed[k] = failed.get(k, 0) + 1
    seen = set()
    left = [x for x in left if not (x["title"] in seen or seen.add(x["title"]))]
    import periodicals                           # here, not at the top: periodicals imports this module
    import medications                           # (the same)
    return {"built": datetime.date.today().isoformat(), "release": RELEASE,
            "books": sorted(books.values(), key=lambda b: (b["group"], b["title"].casefold())),
            "left_out": left, "not_included": [{"title": t, "reason": r} for t, r in sources.NOT_INCLUDED +
                                               periodicals.NOT_INCLUDED + medications.NOT_INCLUDED],
            "licence_lines": {**sources.LICENCE_LINES, **periodicals.LICENCE_LINES, **medications.LICENCE_LINES},
            "groups": sources.GROUPS, "group_notes": {**periodicals.GROUP_NOTES, **medications.GROUP_NOTES},
            "pieces_done": sorted(done),
            "pieces_failed": {k: n for k, n in sorted(failed.items()) if k not in done}}


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["all"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--pictures", action="store_true", help="put the pictures in the books (much larger)")
    p.add_argument("--local-osbooks", default=None, help="build the books of an OpenStax repository folder")
    p.add_argument("--merge", nargs="*", default=None, help="merge these manifests into textbooks.json")
    p.add_argument("--existing", default=None, help="the textbooks.json published before (with --merge)")
    a = p.parse_args(argv)
    if a.merge is not None:
        existing = None
        if a.existing and os.path.exists(a.existing):
            with open(a.existing, encoding="utf-8") as f:
                existing = json.load(f)
        data = merge(a.merge, existing)
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "textbooks.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        print(f"textbooks.json: {len(data['books'])} books")
        return 0
    build(a.keys, a.out, a.cache, a.pictures, a.local_osbooks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
