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
  python textbooks/build_textbooks.py --local-osbooks path/to/osbooks-repo --out build/textbooks   (no network)
Each run writes <id>.zim for each book and manifest-<key>.json (the books' catalogue entries and the left-out
ones). Keys: osbooks (every repository), osbooks:<repository>, siyavula, dspace, or all.
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
    group: str                   # "textbooks" or "reference"
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


def licence_kind(short):
    """"open", "share-alike", "non-commercial", or "" when it is not allowed (any ND, or unknown)."""
    if "ND" in short.split("-") or "-ND" in short:
        return ""
    base = re.sub(r"\s+\d\.\d.*$", "", short).strip()
    return sources.ALLOWED.get(base, "")


def licence_words(short):
    """The licence as the toolkit shows it: "CC BY-NC-SA 4.0, not for commercial use" for the non-commercial
    ones."""
    return short + (", not for commercial use" if licence_kind(short) == "non-commercial" else "")


def slug(text, limit=60):
    """A path part from a title ("Anatomy of the Kidney" -> "anatomy-of-the-kidney")."""
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].strip("-") or "page"


def esc(text):
    """HTML-escaped text."""
    return html.escape(text or "", quote=True)


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
    return (f"From {book.title} by {book.publisher}, {licence_words(book.licence)} ({book.licence_url}). "
            f"Original: {book.source}. Changed: made into web pages, with the formulas written as text.")


def index_page(book):
    """The welcome page: what the book is, its credit and licence, the original PDF, and the contents."""
    out = [f"<p>{esc(book.description)}</p>" if book.description else ""]
    out.append(f"<p>Publisher: {esc(book.publisher)}. {('Authors: ' + esc(book.authors) + '. ') if book.authors else ''}"
               f"Licence: {esc(licence_words(book.licence))} "
               f'(<a href="{esc(book.licence_url)}">{esc(book.licence_url)}</a>). '
               f'Original: <a href="{esc(book.source)}">{esc(book.source)}</a>.</p>')
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


def write_book(book, out_dir, date=None):
    """Write book as <name>_<YYYY-MM>.zim in out_dir and return its catalogue entry (manifest_entry)."""
    date = date or datetime.date.today()
    file_id = f"{book.name}_{date:%Y-%m}"
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
    return manifest_entry(book, file_id, path, count, date)


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
    licence_kind, licence_text (as shown), language, flavour, date, size, sha256, article_count, file, url,
    description, source, original_pdf and original_epub ({url, size, sha256} or {})."""
    return {
        "id": file_id, "name": book.name, "title": book.title, "subject": book.subject, "level": book.level,
        "group": book.group, "publisher": book.publisher, "credit": book.publisher, "country": book.country,
        "licence": book.licence, "licence_url": book.licence_url, "licence_kind": licence_kind(book.licence),
        "licence_text": licence_words(book.licence), "language": book.language, "flavour": book.flavour,
        "date": date.isoformat(), "size": os.path.getsize(path), "sha256": file_sha256(path),
        "article_count": count, "file": os.path.basename(path), "url": f"{RELEASE}/{os.path.basename(path)}",
        "description": book.description, "source": book.source, "authors": book.authors,
        "original_pdf": book.original_pdf, "original_epub": book.original_epub,
    }


# ====================================================================== polite downloads

_last = {}


def fetch(url, cache=None, binary=False, tries=4):
    """The body of url (text, or bytes with binary=True): one request at a time, PAUSE seconds between two
    requests to the same site, a few tries on errors, kept in the cache folder when one is given."""
    key = hashlib.sha256(url.encode()).hexdigest()[:40]
    cached = os.path.join(cache, key) if cache else None
    if cached and os.path.exists(cached):
        with open(cached, "rb") as f:
            data = f.read()
        return data if binary else data.decode("utf-8", "replace")
    host = urllib.parse.urlsplit(url).hostname
    for attempt in range(tries):
        wait = PAUSE - (time.monotonic() - _last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
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
            flavour="maxi" if pictures else "nopic")
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


# ====================================================================== the run

def build(keys, out_dir, cache=None, pictures=False, local_osbooks=None, date=None):
    """Build the books of keys (see the module docstring) into out_dir and write manifest-<key>.json for each key.
    Returns {key: manifest}."""
    work = os.path.join(cache or out_dir, "work")
    manifests = {}
    catalogue = None
    plan = []
    for key in keys:
        if key == "all":
            plan += [f"osbooks:{r}" for r in sources.OSBOOKS] + ["siyavula", "dspace"]
        elif key == "osbooks":
            plan += [f"osbooks:{r}" for r in sources.OSBOOKS]
        else:
            plan.append(key)
    if local_osbooks:
        plan = [f"local:{local_osbooks}"]
    for key in plan:
        books, left_out = [], []
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
            entry = write_book(book, out_dir, date)
            print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, {entry['licence']}")
            entries.append(entry)
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower().split("/")[-1])
        manifest = {"key": key, "books": entries, "left_out": left_out, "files": [e["file"] for e in entries]}
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


def merge(manifest_paths, existing=None):
    """The catalogue textbooks.json from the manifests: the newest release of each book, the left-out books and
    sources.NOT_INCLUDED. existing: the textbooks.json published before (books it has that no manifest built
    again are kept)."""
    books = {}
    for old in (existing or {}).get("books", []):
        books[old["name"]] = old
    left = []
    for path in manifest_paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data.get("books", []):
            if entry["name"] not in books or entry["date"] >= books[entry["name"]]["date"]:
                books[entry["name"]] = entry
        left += data.get("left_out", [])
    seen = set()
    left = [x for x in left if not (x["title"] in seen or seen.add(x["title"]))]
    return {"built": datetime.date.today().isoformat(), "release": RELEASE,
            "books": sorted(books.values(), key=lambda b: (b["group"], b["title"].casefold())),
            "left_out": left, "not_included": [{"title": t, "reason": r} for t, r in sources.NOT_INCLUDED],
            "licence_lines": sources.LICENCE_LINES}


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
