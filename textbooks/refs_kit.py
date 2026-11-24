"""The shared machinery of the reference sources added on 2026-11-22 (food data, FDA recalls, MedlinePlus, NVDA and
liblouis documentation, laws, legal help, emergency preparedness, money, transport, government help, disability and
employment, voting and housing). Each of those modules is mostly data: a Collection of books (web guides, PDFs and
books made by the module's own functions), and this module turns it into build keys, the weekly sign of change, the
books and their manifests, in the same shape as writing_business.py.

In plain words, for each key a Collection:
  - checks the site first: robots.txt must allow our reader, and a site that shuts out AI companies' readers or says
    "ai-train=no" is never read (directory_sources.ai_refused);
  - reads the book: a web guide page by page (directory_sources.guide_book, which checks the licence line at every
    build), an official PDF whole (build_textbooks.pdfdoc_book), or the module's own maker function (a data file);
  - sets the book's licence notice, "published" date (the publisher's), version (the edition read) and originals
    (every file or page read; the builder adds the licence and may_download to each);
  - writes the ZIM file and manifest-<key>.json, with the key and the fingerprint for the weekly update check.

Requests go one at a time with a pause (build_textbooks.fetch). Large bulk files are streamed to the cache folder
(download_file), never held whole in memory. Nothing here imports the builder at the top, because the builder imports
sources, which imports these modules at its end.
"""

import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The same names as in sources.py (these modules are imported at its end, so they cannot import it).
US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"
GOVINFO_POLICY = "https://www.govinfo.gov/about/policies"
GOVINFO_TEXT = r"Copyright protection under this title is not available for any work of the United States Government"
CC0 = "CC0 1.0"
CC0_URL = "https://creativecommons.org/publicdomain/zero/1.0/"

MAIN = (r"<main\b[^>]*>", r"</main>")
DROP = [r"<nav\b.*?</nav>", r"<aside\b.*?</aside>", r"<form\b.*?</form>", r"<button\b.*?</button>",
        r"<script\b.*?</script>", r"<style\b.*?</style>"]
WEB = dict(page_mark="", start=[], units="", sitemap="", unit_rules=[], content=MAIN, drop=DROP, level="reference")

NOT_LEGAL_ADVICE = ("This is general information, not legal advice. Laws vary by state and change; for advice about "
                    "your own situation, contact a lawyer or your local legal aid office.")


def us_web(group, **fields):
    """A US government web guide entry (public domain, the licence line checked on govinfo's quotation of 17 U.S.C.
    105 unless the entry names its own licence page)."""
    return dict(dict(WEB, group=group, country="United States", licence=US_GOV, licence_url=US_GOV_URL,
                     licence_page=GOVINFO_POLICY, licence_text=GOVINFO_TEXT), **fields)


def us_pdf(group, **fields):
    """A US government PDF entry (sources.PDF_DOCS fields, read whole by build_textbooks.pdfdoc_book)."""
    return dict(dict(group=group, country="United States", licence=US_GOV, licence_url=US_GOV_URL,
                     licence_page=GOVINFO_POLICY, licence_text=GOVINFO_TEXT, level="reference"), **fields)


def sha(*parts):
    """A short fingerprint of some values (lists and dicts are written as JSON first)."""
    h = hashlib.sha256()
    for p in parts:
        h.update((p if isinstance(p, str) else json.dumps(p, sort_keys=True, default=str)).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:32]


def readable(url, cache=None):
    """True when the builder may read url: robots.txt allows our reader and no AI-reader block or "ai-train=no"
    applies."""
    import build_textbooks as B
    import directory_sources as D
    return B.allowed_by_robots(url, cache) and not D.ai_refused(url, cache)


def download_file(url, cache, name=None, max_age_days=None):
    """The local path of url's file, downloaded once into the cache folder (streamed in pieces, so a file of several
    hundred megabytes is never held in memory). max_age_days: download again when the copy is older. The pause
    between requests to one site is kept (build_textbooks.PAUSE)."""
    import build_textbooks as B
    folder = os.path.join(cache or "build/textbooks-cache", "bulk")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name or re.sub(r"[^A-Za-z0-9._-]+", "_", url.rsplit("/", 1)[-1])[:120])
    if os.path.exists(path) and (max_age_days is None or
                                 time.time() - os.path.getmtime(path) < max_age_days * 86400):
        return path
    host = urllib.parse.urlsplit(url).hostname
    wait = B.PAUSE - (time.monotonic() - B._last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": B.USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r, open(path + ".part", "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    finally:
        B._last[host] = time.monotonic()
    os.replace(path + ".part", path)
    return path


def text_html(text):
    """Plain text as HTML paragraphs (blank lines part paragraphs; single line breaks are kept)."""
    import build_textbooks as B
    parts = [p.strip() for p in re.split(r"\n\s*\n", (text or "").replace("\r", "")) if p.strip()]
    return "".join(f"<p>{B.esc(p).replace(chr(10), '<br>')}</p>" for p in parts)


def rows_table(rows, head=None):
    """An HTML table of rows [(cell, ...)] (cells are text), with an optional header row."""
    import build_textbooks as B
    out = ["<table>"]
    if head:
        out.append("<tr>" + "".join(f"<th>{B.esc(str(c))}</th>" for c in head) + "</tr>")
    for row in rows:
        out.append("<tr>" + "".join(f"<td>{B.esc(str(c))}</td>" for c in row) + "</tr>")
    out.append("</table>")
    return "".join(out)


def dl(pairs):
    """A definition list of [(label, value)] (empty values left out)."""
    import build_textbooks as B
    items = [f"<dt>{B.esc(k)}</dt><dd>{B.esc(str(v))}</dd>" for k, v in pairs if v not in (None, "", [])]
    return "<dl>" + "".join(items) + "</dl>" if items else ""


class Collection:
    """The books of one module. prefix: its keys' prefix ("fdc"); group: the library group; words: {word: [keys]}
    the request words that stand for several keys (a function of nothing, so the list can depend on the date);
    guides, pdfs: entries as in writing_business.py; makers: {name: (make(name, work, cache, left_out, limit) ->
    Book or None, sign(name) -> str)} for a module's own books, where name may hold a piece ("2026-11");
    pieces: {base: function() -> [pieces]} for makers whose keys are "<prefix>:<base>:<piece>";
    current: function(key) -> True for a key rebuilt under one name until it is complete (this month's recalls),
    else every build is a new kept version."""

    def __init__(self, prefix, group, words=None, guides=(), pdfs=(), makers=None, pieces=None, current=None,
                 version_words=None):
        self.prefix, self.group = prefix, group
        self.words = words or {}
        self.guides = {g["name"]: g for g in guides}
        self.pdfs = {p["name"]: p for p in pdfs}
        self.makers = makers or {}
        self.pieces = pieces or {}
        self.current = current or (lambda key: False)
        self.version_words = version_words or {}

    # ---------------------------------------------------------------- keys

    def own_keys(self):
        """Every key of the guides, PDFs and makers (pieced makers with all their pieces)."""
        keys = [f"{self.prefix}:{n}" for n in self.guides] + [f"{self.prefix}:{n}" for n in self.pdfs]
        for name in self.makers:
            if name in self.pieces:
                keys += [f"{self.prefix}:{name}:{p}" for p in self.pieces[name]()]
            else:
                keys.append(f"{self.prefix}:{name}")
        return keys

    def expand_keys(self, words):
        """The keys the words stand for: a word of self.words, "<prefix>:<base>" of a pieced maker (all its pieces),
        or one key (kept as it is)."""
        keys = []
        for w in words:
            if w in self.words:
                keys += self.words[w]()
            elif w.startswith(self.prefix + ":") and w.split(":", 1)[1] in self.pieces:
                base = w.split(":", 1)[1]
                keys += [f"{self.prefix}:{base}:{p}" for p in self.pieces[base]()]
            else:
                keys.append(w)
        return list(dict.fromkeys(keys))

    def owns(self, key):
        """True when key is one of this collection's keys (by its prefix)."""
        return key.startswith(self.prefix + ":")

    # ---------------------------------------------------------------- signs

    def sign(self, key):
        """The weekly check's sign of change of one key ("" when it cannot be asked: then nothing is rebuilt)."""
        import directory_sources as D
        import updates
        name = key.split(":", 1)[1]
        base = name.split(":", 1)[0]
        try:
            if name in self.guides:
                return D.guide_sign(self.guides[name])
            if name in self.pdfs:
                return updates.pdf_sign(self.pdfs[name])
            if base in self.makers:
                return self.makers[base][1](name) or ""
        except (urllib.error.URLError, OSError, ValueError, KeyError, LookupError, StopIteration):
            return ""
        return ""

    # ---------------------------------------------------------------- books

    def book_for(self, key, work, cache=None, left_out=None, limit=None):
        """The Book of one key, or None (the reason in left_out)."""
        import build_textbooks as B
        import directory_sources as D
        left_out = left_out if left_out is not None else []
        name = key.split(":", 1)[1]
        base = name.split(":", 1)[0]
        if base in self.makers and name not in self.guides and name not in self.pdfs:
            book = self.makers[base][0](name, work, cache, left_out, limit)
            if book is not None:
                book.version = book.version or f"read {datetime.date.today().isoformat()}"
            return book
        entry = self.guides.get(name) or self.pdfs.get(name)
        if entry is None:
            left_out.append({"title": key, "reason": "Unknown key."})
            return None
        where = entry.get("pdf") or entry.get("page") or entry.get("source") or ""
        if entry.get("archive"):
            where = f"https://archive.org/metadata/{entry['archive']}"
        if where and D.ai_refused(where, cache):
            left_out.append({"title": entry["title"], "reason": "The site's robots.txt shuts out AI companies' "
                             "readers or says ai-train=no; it is not read."})
            return None
        if name in self.guides:
            if entry.get("crawl"):           # crawl once here, so an address with and without its last "/" is one
                found, seen = [], set()
                for url, unit in D.crawl(entry, cache, limit):
                    if url.rstrip("/") not in seen:
                        seen.add(url.rstrip("/"))
                        found.append((url, unit))
                entry = dict(entry, crawl=None, urls=found, sitemap="", start=[])
            book = D.guide_book(entry, cache, left_out, limit)
        else:
            book = B.pdfdoc_book(entry, work, cache, left_out)
            if book is not None and limit:
                book.pages = book.pages[:limit]
        if book is None:
            return None
        if not book.name.startswith(self.prefix + "_"):      # one name space per module: "mlp_health_topics"
            book.name = f"{self.prefix}_{book.name}"
        book.version = entry.get("version", "")
        if name in self.guides:              # a web guide: the edition is the day its pages were read
            book.version = (book.version + ", " if book.version else "") + \
                f"pages read {datetime.date.today().isoformat()}"
        for field in ("published", "notice", "region", "language"):
            if field == "notice" and (entry.get("military") or entry.get("distribution_a")):
                continue                     # the builder's notice starts with the truthful release line: kept
            if entry.get(field):
                setattr(book, field, entry[field])
        return book

    def build(self, keys, out_dir, cache=None, date=None, limit=None):
        """Build the books of keys into out_dir and write manifest-<key>.json for each; returns {key: manifest}.
        Every book is a new kept version (versioned file names), except a "current" key (this month's piece),
        which is rebuilt under one monthly name until its month is over. limit: a small test build (only so many
        pages; manifests named "..._sample")."""
        import build_textbooks as B
        manifests = {}
        work = os.path.join(cache or out_dir, "work")
        os.makedirs(out_dir, exist_ok=True)
        for key in self.expand_keys(keys):
            if not self.owns(key):
                print(f"Not a key of this module: {key}; skipped.")
                continue
            left_out, entries = [], []
            fingerprint = "" if limit else self.sign(key)
            try:
                book = self.book_for(key, work, cache, left_out, limit)
            except Exception as e:  # noqa: BLE001 - said in the manifest
                left_out.append({"title": key, "reason": f"It could not be built ({B.hide_keys(e)})."})
                book = None
            if book is not None and not book.pages:
                left_out.append({"title": book.title, "reason": "No pages could be read."})
                book = None
            if book is not None:
                current = self.current(key)
                entry = B.write_book(book, out_dir, date, versioned=not current)
                entry.update({"key": key, "fingerprint": "" if current else fingerprint, "release": "textbooks"})
                if current:
                    entry["complete"] = False
                print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, "
                      f"{entry['licence_text']}")
                entries.append(entry)
            failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
            manifest = {"key": key, "release": "textbooks", "books": entries, "left_out": left_out,
                        "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
            safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if limit else "")
            with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=1, ensure_ascii=False)
            manifests[key] = manifest
        return manifests


def new_book(name, title, subject, group, publisher, licence, licence_url, source, description, notice, **more):
    """A build_textbooks.Book with the fields every book of these modules carries."""
    import build_textbooks as B
    return B.Book(name=name, title=title, subject=subject, level=more.pop("level", "reference"), group=group,
                  publisher=publisher, country=more.pop("country", "United States"), licence=licence,
                  licence_url=licence_url, source=source, description=description, notice=notice, **more)


def main_for(collection, doc, argv=None):
    """The command line of a module: keys (or words) to build, --out, --cache, --limit (a small test build) and
    --list (only print the keys)."""
    import argparse
    p = argparse.ArgumentParser(description=doc.split("\n", 1)[0])
    p.add_argument("keys", nargs="+")
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many pages")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(collection.expand_keys(a.keys)))
        return 0
    collection.build(a.keys, a.out, a.cache, limit=a.limit)
    return 0


def split_html(text, level=2, start=None, end=None):
    """[(title, id, body HTML)] of one long HTML document split at its headings of level (the text before the first
    one, when it has words, is "Introduction"). start, end: regular expressions of where the document's content
    begins and ends (default: the <body>)."""
    import html as _html
    import re as _re
    m = _re.search(start or r"<body\b[^>]*>", text)
    text = text[m.end():] if m else text
    if end:
        m = _re.search(end, text)
        text = text[:m.start()] if m else text
    text = _re.sub(r"<h1\b.*?</h1>", "", text, count=1, flags=_re.S)
    parts = _re.split(rf"(<h{level}\b[^>]*>.*?</h{level}>)", text, flags=_re.S)
    out = []
    if _re.sub(r"<[^>]+>|\s", "", parts[0]):
        out.append(("Introduction", "introduction", parts[0]))
    for i in range(1, len(parts), 2):
        head = parts[i]
        title = " ".join(_html.unescape(_re.sub(r"<[^>]+>", " ", head)).split())
        hid = (_re.search(r'id="([^"]+)"', head) or [None, ""])[1]
        out.append((title, hid, parts[i + 1]))
    return out


def last_modified(url):
    """The server's Last-Modified date of url as "YYYY-MM-DD" ("" when it does not say)."""
    import build_textbooks as B
    import email.utils
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": B.USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            when = r.headers.get("Last-Modified")
    except (urllib.error.URLError, OSError):
        return ""
    finally:
        B._last[urllib.parse.urlsplit(url).hostname] = time.monotonic()
    return email.utils.parsedate_to_datetime(when).date().isoformat() if when else ""


def guide(group, name, title, subject, publisher, start, pages, description, notice, depth=1, follow=None,
          units=None, limit=200, **more):
    """A US government web guide read by crawling (directory_sources.crawl): start (one address or a list), the
    address pattern of its pages, the hub pages to follow (follow) for a depth of 2, its parts (units: [(pattern,
    part)]). A start address is given without its last "/" so the crawler does not add one to every link."""
    starts = [start] if isinstance(start, str) else list(start)
    return us_web(group, name=name, title=title, subject=subject, publisher=publisher, source=starts[0],
                  description=description, notice=notice, crawl=[(s.rstrip("/"), depth) for s in starts],
                  follow=follow, pages=pages, unit_rules=units or [], limit=limit, **more)
