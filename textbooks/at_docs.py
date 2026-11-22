"""Screen reader and braille software documentation, and open assistive technology guides, for the reference library
(the owner's request of 2026-11-22). Keys: at-docs (every book), atdoc:<name>.

What this module builds, in plain words, each IN FULL:
  - NVDA (NV Access, GNU GPL version 2 or later): the User Guide, the Commands Quick Reference, What's New (every
    release's changes) and the Developer Guide, as NV Access publishes them for the current release
    (download.nvaccess.org/documentation/), one page per section (per release for What's New);
  - NVDA add-ons: every add-on in NV Access's Add-on Store (its data are public domain, ODC-PDDL) whose licence is
    open, with the store's description and the add-on's own documentation (the read-me of its source repository on
    GitHub), in two books: the GPL version 2 add-ons, and the others with open licences (GPL version 3, MIT,
    Apache); an add-on whose licence is not open is listed by name only;
  - liblouis (GNU LGPL): the User's and Programmer's Manual (every page of liblouis.io/documentation/liblouis/), the
    liblouisutdml manual, and a list of every liblouis braille table with its metadata (name, language, type,
    contraction, grade, braille system and copyright lines), read from the tables' own headers;
  - the National Center on Accessible Educational Materials (AEM Center at CAST; funded by the US Department of
    Education; "web content is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License"):
    every page of its guides (acquiring accessible formats, creating accessible documents, EPUB, video, websites
    and math, using accessible formats, NIMAS and NIMAC, coordinating in K-12, higher education and workforce).

Not built (NOT_INCLUDED, with the index addresses): the US Department of Education's and OSERS' assistive technology
pages (www.ed.gov and sites.ed.gov answer programs "403 Forbidden", robots.txt included), the AT Act programs'
guides at the AT3 Center (at3center.net refuses programs), and the NVDA add-on documentation site
addons.nvda-project.org (its robots.txt says "ai-train=no").

Licence checks at every build: NVDA's copying.txt (raw.githubusercontent.com/nvaccess/nvda) still says GPL version 2
or later; the liblouis manual's source still carries its LGPL "copying" block; the add-on store data's read-me still
says ODC-PDDL; the AEM Center's footer still says CC BY-SA 4.0 (every page is checked for it).

Run from the repository's folder:
  python3 textbooks/at_docs.py atdoc:nvda_user_guide --out build/textbooks
  python3 textbooks/at_docs.py atdoc:nvda_addons_gpl2 --out build/textbooks --limit 5
"""

import json
import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "disability"                     # "Reference, disability and accessibility"
NVDA_DOCS = "https://download.nvaccess.org/documentation"
NVDA_COPYING = "https://raw.githubusercontent.com/nvaccess/nvda/master/copying.txt"
NVDA_COPYING_TEXT = r"NVDA is available under the GNU General Public License version 2 or later"
GPL2 = "GPL-2.0-or-later"
GPL2_URL = "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html"
GPL3 = "GPL-3.0-or-later"
GPL3_URL = "https://www.gnu.org/licenses/gpl-3.0.html"
LGPL = "LGPL-2.1-or-later"
LGPL_URL = "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html"
STORE = "https://addonstore.nvaccess.org/en/all/latest.json"
STORE_README = "https://raw.githubusercontent.com/nvaccess/addon-datastore/master/README.md"
STORE_LICENCE_TEXT = r"distributed under the \[ODC-PDDL\]"
LIBLOUIS_TEXI = "https://raw.githubusercontent.com/liblouis/liblouis/master/doc/liblouis.texi"
LIBLOUIS_TEXT = r"GNU Lesser \(or library\) General Public License"
TABLES = "https://raw.githubusercontent.com/liblouis/liblouis/master/tables"

# The licences the toolkit may repackage that these books use (added to sources.ALLOWED): the GNU licences are
# copyleft, like CC BY-SA ("share-alike": a changed copy keeps the same licence).
ALLOWED = {GPL2: "share-alike", GPL3: "share-alike", LGPL: "share-alike", "GPL-2.0": "share-alike"}

NVDA_NOTICE = ("NVDA documentation, copyright NV Access Limited and the NVDA contributors, licensed under the GNU "
               "General Public License version 2 or later (github.com/nvaccess/nvda, copying.txt). This copy is "
               "converted to an accessible format; the current version is at download.nvaccess.org/documentation/.")
NVDA_DOCS_LIST = [
    ("nvda_user_guide", "userGuide", "NVDA User Guide", "Screen reader (NVDA): user guide",
     "NV Access's complete User Guide for the NVDA screen reader, one page per chapter: getting started, installing "
     "and portable copies, using NVDA with the keyboard, touch and braille, navigating with the system focus, review "
     "and object navigation, browse mode on the web, reading maths, braille, vision, content recognition, specific "
     "applications, the Add-on Store, extra tools, every setting, and the supported speech synthesizers and braille "
     "displays.", 2),
    ("nvda_key_commands", "keyCommands", "NVDA Commands Quick Reference", "Screen reader (NVDA): keyboard commands",
     "NV Access's quick reference of every NVDA command for desktop and laptop keyboard layouts, touch gestures and "
     "braille displays, by chapter of the User Guide.", 2),
    ("nvda_whats_new", "changes", "What's New in NVDA (every release)", "Screen reader (NVDA): release notes",
     "NV Access's change log: one page per NVDA release, newest first, with its new features, changes, bug fixes "
     "and changes for developers.", 2),
    ("nvda_developer_guide", "developerGuide", "NVDA Developer Guide", "Screen reader (NVDA): developer guide",
     "NV Access's guide for developers: translating NVDA, writing plugins (app modules, global plugins, drivers), "
     "packaging code as NVDA add-ons, the Python console, remote Python console and the extension points.", 2),
]


# ====================================================================== NVDA's own documents

def nvda_doc_book(name, work, cache=None, left_out=None, limit=None):
    """One NVDA document (one HTML file) split into a page per chapter."""
    import build_textbooks as B
    row = next(r for r in NVDA_DOCS_LIST if r[0] == name)
    _name, file, title, subject, description, level = row
    if not re.search(NVDA_COPYING_TEXT, B.fetch(NVDA_COPYING, cache)):
        left_out.append({"title": title, "reason": "NVDA's copying.txt no longer says GPL version 2 or later."})
        return None
    url = f"{NVDA_DOCS}/{file}.html"
    if not K.readable(url, cache):
        left_out.append({"title": title, "reason": "Not allowed by robots.txt."})
        return None
    text = B.fetch(url, None)                 # fresh: it changes with each release
    version = " ".join(B.html.unescape(re.sub(r"<[^>]+>", " ", (re.search(r"<h1\b.*?</h1>", text, re.S) or
                                                                [""])[0])).split())
    book = K.new_book(f"atdoc_{name}", title, subject, GROUP, "NV Access Limited and the NVDA contributors", GPL2,
                      GPL2_URL, url, description, NVDA_NOTICE, country="International",
                      changes="split into one page per chapter")
    book.version = version or "current release"
    book.published = K.last_modified(url)
    book.originals.append({"url": url, "kind": "html"})
    paths = set()
    for head, hid, body in K.split_html(text, level):
        if limit and len(book.pages) >= limit:
            break
        path = B.slug(hid or head, 60)
        while path in paths or path in ("index", "style-css"):
            path += "-2"
        paths.add(path)
        book.pages.append(B.Page(path, head, B._Cleaner({}, url).clean(body), 0, ""))
    return book


def nvda_doc_sign(name):
    """An NVDA document's sign: the file's Last-Modified date and its first heading (the release)."""
    import build_textbooks as B
    file = next(r[1] for r in NVDA_DOCS_LIST if r[0] == name)
    url = f"{NVDA_DOCS}/{file}.html"
    return K.sha(K.last_modified(url), (re.search(r"<h1\b.*?</h1>", B.fetch(url, None), re.S) or [""])[0])


# ====================================================================== NVDA add-ons

def licence_family(words):
    """"gpl2" (GPL version 2, or 2 or later), "open" (GPL version 3, MIT, Apache, BSD), or "" (not known to be
    open) for an add-on's licence words."""
    w = (words or "").lower().replace("-", " ")
    if re.search(r"\bgpl\s*v?\s*2|general public license v(ersion)?\s*2|gpl 2\.0|gnu gpl v2", w) and "lesser" not in w:
        return "gpl2"
    if re.search(r"gpl|general public license", w) and re.search(r"\b3\b|v3", w):
        return "open"
    if re.search(r"\bmit\b|apache|\bbsd\b|unlicense|\bcc0\b", w):
        return "open"
    return ""


def readme_urls(source):
    """The raw addresses where a GitHub repository's English read-me may be (tried in order)."""
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+)", source or "")
    if not m:
        return []
    raw = f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2).removesuffix('.git')}/HEAD"
    return [f"{raw}/readme.md", f"{raw}/README.md", f"{raw}/addon/doc/en/readme.md", f"{raw}/Readme.md"]


def addons_book(name, work, cache=None, left_out=None, limit=None):
    """The add-ons of one licence family, one page per add-on (newest stable version's entry)."""
    import build_textbooks as B
    import directory_sources as D
    family = "gpl2" if name == "nvda_addons_gpl2" else "open"
    if not re.search(STORE_LICENCE_TEXT, B.fetch(STORE_README, cache)):
        left_out.append({"title": name, "reason": "The add-on store data's read-me no longer says ODC-PDDL."})
        return None
    store = json.loads(B.fetch(STORE, None))
    newest = {}
    for a in store:
        if a.get("channel") not in ("stable", None):
            continue
        old = newest.get(a["addonId"])
        if old is None or a.get("submissionTime", 0) > old.get("submissionTime", 0):
            newest[a["addonId"]] = a
    chosen = sorted((a for a in newest.values() if licence_family(a.get("license")) == family),
                    key=lambda a: a.get("displayName", "").lower())
    if family == "gpl2":
        book = K.new_book("atdoc_nvda_addons_gpl2", "NVDA add-ons (GPL version 2): descriptions and documentation",
                          "Screen reader (NVDA): add-ons", GROUP, "The add-ons' authors; NV Access Add-on Store",
                          GPL2, GPL2_URL, "https://www.nvaccess.org/addonstore-legacy/",
                          "Every stable NVDA add-on in NV Access's Add-on Store licensed under the GNU GPL version 2 "
                          "(or 2 or later): one page per add-on with the store's description, author, version, the "
                          "NVDA versions it works with, its source and its own documentation (the read-me of its "
                          "repository).", "Each add-on's documentation is by its authors, under the GNU GPL version "
                          "2 (as each add-on's store entry says); the store's data are public domain (ODC-PDDL). "
                          "Install add-ons from NVDA's own Add-on Store (NVDA menu, Tools).", country="International",
                          changes="each add-on's read-me made into a web page")
    else:
        book = K.new_book("atdoc_nvda_addons_open", "NVDA add-ons (GPL version 3, MIT, Apache): descriptions and "
                          "documentation", "Screen reader (NVDA): add-ons", GROUP,
                          "The add-ons' authors; NV Access Add-on Store", GPL3, GPL3_URL,
                          "https://www.nvaccess.org/addonstore-legacy/",
                          "Every stable NVDA add-on in NV Access's Add-on Store under another open licence (GNU GPL "
                          "version 3, MIT, Apache or BSD): one page per add-on with the store's description and its "
                          "own documentation.", "Each add-on's documentation is by its authors under the licence its "
                          "page names (GPL version 3, or the MIT, Apache or BSD licence, which may be combined under "
                          "the GPL version 3); the store's data are public domain (ODC-PDDL).",
                          country="International", changes="each add-on's read-me made into a web page")
    book.originals.append({"url": STORE, "kind": "json"})
    book.version = f"Add-on Store data read {__import__('datetime').date.today().isoformat()}"
    newest_time, paths = 0, set()
    for a in chosen:
        if limit and len(book.pages) >= limit:
            break
        newest_time = max(newest_time, a.get("submissionTime", 0))
        facts = K.dl([("Author", a.get("publisher")), ("Version", a.get("addonVersionName")),
                      ("Works with NVDA", "{0[major]}.{0[minor]} to {1[major]}.{1[minor]}".format(
                          a.get("minNVDAVersion") or {"major": "?", "minor": "?"},
                          a.get("lastTestedVersion") or {"major": "?", "minor": "?"})),
                      ("Licence", a.get("license")), ("Home page", a.get("homepage")),
                      ("Source", a.get("sourceURL")), ("Add-on ID", a.get("addonId"))])
        body = f"<p>{B.esc(a.get('description', ''))}</p>{facts}"
        for url in readme_urls(a.get("sourceURL")):
            if not K.readable(url, cache):
                continue
            try:
                text = B.fetch(url, cache)
            except (urllib.error.URLError, OSError):
                continue
            body += "<h2>Documentation (the add-on's read-me)</h2>" + B._Cleaner({}, url).clean(D.markdown_html(text))
            book.originals.append({"url": url, "kind": "markdown"})
            break
        path = B.slug(a["addonId"], 60)
        while path in paths:
            path += "-2"
        paths.add(path)
        book.pages.append(B.Page(path, a.get("displayName") or a["addonId"], body, 0, ""))
    if newest_time:
        import datetime
        book.published = datetime.datetime.fromtimestamp(newest_time / 1000, datetime.timezone.utc).date().isoformat()
    return book


def addons_sign(name):
    """The add-ons' sign: the ids and versions of the store's entries of that family."""
    import build_textbooks as B
    family = "gpl2" if name == "nvda_addons_gpl2" else "open"
    store = json.loads(B.fetch(STORE, None))
    return K.sha(sorted((a["addonId"], a.get("addonVersionName", "")) for a in store
                        if licence_family(a.get("license")) == family))


# ====================================================================== liblouis

LIBLOUIS_NOTICE = ("Liblouis documentation, copyright the BRLTTY Team, ViewPlus Technologies, Abilitiessoft, the "
                   "Swiss Library for the Blind, Visually Impaired and Print Disabled (SBS) and the liblouis "
                   "contributors, licensed under the GNU Lesser General Public License (version 3 or later for the "
                   "manual; the tables 2.1 or later).")


def liblouis_licence_ok(cache=None):
    """True when the manual's source still carries its LGPL copying block."""
    import build_textbooks as B
    return bool(re.search(LIBLOUIS_TEXT, B.fetch(LIBLOUIS_TEXI, cache)))


def utdml_book(name, work, cache=None, left_out=None, limit=None):
    """The liblouisutdml manual (one HTML file) split into a page per chapter."""
    import build_textbooks as B
    url = "https://liblouis.io/documentation/liblouisutdml.html"
    if not liblouis_licence_ok(cache) or not K.readable(url, cache):
        left_out.append({"title": "liblouisutdml manual", "reason": "Its licence or robots.txt no longer allows it."})
        return None
    text = B.fetch(url, None)
    book = K.new_book("atdoc_liblouisutdml_manual", "liblouisutdml User's and Programmer's Manual",
                      "Braille translation software (liblouisutdml)", GROUP, "The liblouis project (liblouis.io)",
                      LGPL, LGPL_URL, url, "The whole manual of liblouisutdml, the liblouis companion that "
                      "translates XML, HTML and text documents into formatted braille: the file2brl program, "
                      "configuration files and settings, semantic action files, and the programming interface.",
                      LIBLOUIS_NOTICE, country="International", changes="split into one page per chapter")
    book.published, book.version = K.last_modified(url), "liblouis.io as published"
    book.originals.append({"url": url, "kind": "html"})
    for i, (head, hid, body) in enumerate(K.split_html(text, 2)):
        if limit and len(book.pages) >= limit:
            break
        book.pages.append(B.Page(B.slug(hid or head, 50) + f"-{i}", head, B._Cleaner({}, url).clean(body), 0, ""))
    return book


META = re.compile(r"^#\s*([+-][a-z-]+)\s*:\s*(.*?)\s*$", re.M)


def table_list(cache=None):
    """The table file names from the tables folder's Makefile.am (the project's own list)."""
    import build_textbooks as B
    text = B.fetch(f"{TABLES}/Makefile.am", None)
    return re.findall(r"^\s+([A-Za-z0-9_.+-]+\.(?:ctb|utb|tbl|dis|uti|cti|dic|mod))\b", text, re.M)


def tables_book(name, work, cache=None, left_out=None, limit=None):
    """Every liblouis table with its metadata and copyright lines (its header only, not its rules)."""
    import build_textbooks as B
    if not liblouis_licence_ok(cache):
        left_out.append({"title": "liblouis tables", "reason": "The liblouis manual no longer carries its LGPL block."})
        return None
    book = K.new_book("atdoc_liblouis_tables", "liblouis braille tables: the complete list with their metadata",
                      "Braille translation tables (liblouis)", GROUP, "The liblouis project (liblouis.io)", LGPL,
                      LGPL_URL, "https://github.com/liblouis/liblouis/tree/master/tables",
                      "Every braille table of liblouis (the translation library used by NVDA, JAWS's partners, "
                      "BRLTTY, Orca and many embossers), one page per table file: its name and display name, "
                      "language, type (literary or computer), contraction, grade, dots, braille system, and its "
                      "copyright and licence lines, from the table's own header. The tables' rules themselves are "
                      "not copied.", LIBLOUIS_NOTICE, country="International",
                      changes="each table's header made into a web page")
    book.version = "liblouis master branch, read " + __import__("datetime").date.today().isoformat()
    book.originals.append({"url": f"{TABLES}/Makefile.am", "kind": "txt"})
    names = table_list(cache)
    for file in names:
        if limit and len(book.pages) >= limit:
            break
        url = f"{TABLES}/{file}"
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            left_out.append({"title": file, "reason": "It could not be read."})
            continue
        head = text[:6000]
        meta = META.findall(head)
        rights = re.findall(r"^#\s*(Copyright.*?)\s*$", head, re.M | re.I)
        first = next((ln.lstrip("# ").strip() for ln in head.splitlines() if ln.startswith("#") and
                      ln.lstrip("# ").strip() and not META.match(ln)), "")
        words = {"-name": "Name", "-index-name": "Index name", "-display-name": "Display name", "+language": "Language",
                 "+type": "Type", "+contraction": "Contraction", "+grade": "Grade", "+dots": "Dots",
                 "+system": "Braille system", "+direction": "Direction", "+region": "Region", "+variant": "Variant"}
        pairs = [("File", file), ("Description", first)] + [(words.get(k, k.lstrip("+-")), v) for k, v in meta]
        body = K.dl(pairs)
        if rights:
            body += "<h2>Copyright</h2><ul>" + "".join(f"<li>{B.esc(r)}</li>" for r in rights) + "</ul>"
        lic = re.search(r"GNU Lesser General Public License.*?version\s+([\d.]+)", head, re.S)
        if lic:
            body += f"<p>Licence: GNU Lesser General Public License, version {lic.group(1)} or later.</p>"
        language = dict(meta).get("+language", "")
        display = dict(meta).get("-display-name") or dict(meta).get("-name") or file
        book.pages.append(B.Page(B.slug(file, 60), f"{display} ({file})" if display != file else file, body, 0,
                                 f"Language: {language}" if language else "Tables without a language (shared parts)"))
        book.originals.append({"url": url, "kind": "txt"})
    book.pages.sort(key=lambda p: (p.unit.startswith("Tables without"), p.unit, p.title.lower()))
    return book


LIBLOUIS_MANUAL = dict(
    K.WEB, name="liblouis_manual", title="Liblouis User's and Programmer's Manual", group=GROUP,
    country="International", subject="Braille translation software (liblouis)",
    publisher="The liblouis project (liblouis.io)", licence=LGPL, licence_url=LGPL_URL,
    source="https://liblouis.io/documentation/liblouis/", licence_page=LIBLOUIS_TEXI, licence_text=LIBLOUIS_TEXT,
    description="The whole liblouis manual, every page: how to write translation tables (every opcode: character "
                "definitions, braille indicators, emphasis, special symbols, translation, the context and multipass "
                "opcodes, swap and match), table metadata, how tables are found, testing tables, notes on "
                "back-translation, programming with liblouis (every function), the Python bindings and the indexes.",
    notice=LIBLOUIS_NOTICE, crawl=[("https://liblouis.io/documentation/liblouis/", 1)],
    pages=r"^https://liblouis\.io/documentation/liblouis/([A-Za-z0-9_.-]+\.html)?$",
    content=(r"<body\b[^>]*>", r"</body>"), drop=K.DROP + [r'<div class="nav-panel">.*?</div>'],
    version="liblouis.io as published", limit=200)

AEM = dict(
    K.WEB, name="aem_center", title="National Center on Accessible Educational Materials (AEM Center, CAST): guides",
    group=GROUP, country="United States", subject="Accessible educational materials",
    publisher="National Center on Accessible Educational Materials at CAST (funded by the US Department of Education)",
    licence="CC BY-SA 4.0", licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    source="https://aem.cast.org/", licence_page="https://aem.cast.org/",
    licence_text=r"web content is licens\w+ under a Creative Commons Attribution-ShareAlike 4\.0",
    page_mark=r"creativecommons\.org/licenses/by-sa/4\.0",
    description="Every guide page of the AEM Center: getting started with accessibility, acquiring accessible "
                "formats (braille, large print, audio, digital text) and vetting accessibility, creating accessible "
                "documents, EPUB, social media, video, websites and STEM materials, using accessible formats and "
                "personalising reading and writing, NIMAS and NIMAC, and coordinating accessible materials in early "
                "childhood, K-12, higher education and the workforce.",
    notice="The National Center on Accessible Educational Materials (CAST), CC BY-SA 4.0 except where otherwise "
           "noted. Developed under a cooperative agreement with the US Department of Education, #H327Z190004; the "
           "contents do not necessarily represent the policy of the US Department of Education.",
    crawl=[("https://aem.cast.org/", 2)],
    follow=r"^https://aem\.cast\.org/(about|acquire|coordinate|create|get-started|nimas-nimac|use|policies)(/[a-z0-9-]+)?/?$",
    pages=r"^https://aem\.cast\.org/(about|acquire|coordinate|create|get-started|nimas-nimac|use|policies)"
          r"(/[a-z0-9-]+)+/?$",
    unit_rules=[(r"/get-started", "Get started"), (r"/acquire", "Acquire"), (r"/create", "Create"),
                (r"/use", "Use"), (r"/coordinate", "Coordinate"), (r"/nimas-nimac", "NIMAS and NIMAC"),
                (r"/policies", "Policies"), (r".", "About the AEM Center")],
    version="aem.cast.org as published", limit=250)

MAKERS = {r[0]: (nvda_doc_book, nvda_doc_sign) for r in NVDA_DOCS_LIST}
MAKERS.update({"nvda_addons_gpl2": (addons_book, addons_sign), "nvda_addons_open": (addons_book, addons_sign),
               "liblouisutdml_manual": (utdml_book, lambda name: K.last_modified(
                   "https://liblouis.io/documentation/liblouisutdml.html")),
               "liblouis_tables": (tables_book, lambda name: K.sha(table_list()))})

COLLECTION = K.Collection(
    "atdoc", GROUP, guides=[LIBLOUIS_MANUAL, AEM], makers=MAKERS,
    words={"at-docs": lambda: [f"atdoc:{r[0]}" for r in NVDA_DOCS_LIST] +
           ["atdoc:nvda_addons_gpl2", "atdoc:nvda_addons_open", "atdoc:liblouis_manual",
            "atdoc:liblouisutdml_manual", "atdoc:liblouis_tables", "atdoc:aem_center"]})

GROUPS = {}
LICENCE_LINES = {
    "nvda_documentation": "raw.githubusercontent.com/nvaccess/nvda/master/copying.txt (checked at every build): "
                          "\"NVDA is available under the GNU General Public License version 2 or later, with two "
                          "special exceptions\"; the user documentation is part of that repository (user_docs). "
                          "download.nvaccess.org has no robots.txt rules; www.nvaccess.org's robots.txt has no AI "
                          "rules (checked 2026-11-22).",
    "nvda_addon_store": "github.com/nvaccess/addon-datastore README (checked at every build): \"The data hosted here "
                        "is distributed under the ODC-PDDL license\" (public domain); each add-on's documentation is "
                        "kept only when its store entry names an open licence (GPL, MIT, Apache, BSD). The add-ons' "
                        "read-me files are read from raw.githubusercontent.com (no robots.txt rules).",
    "liblouis_documentation": "liblouis/doc/liblouis.texi copying block (checked at every build): \"This file is free "
                              "software; you can redistribute it and/or modify it under the terms of the GNU Lesser "
                              "(or library) General Public License (LGPL) ... either version 3, or (at your option) any "
                              "later version\"; the tables say LGPL 2.1 or later. liblouis.io's robots.txt lists only "
                              "its sitemap.",
    "aem_center_cast": "aem.cast.org footer (checked at every build and on every page): \"Except where otherwise noted, "
                       "the National Center on Accessible Educational Materials web content is licensed under a "
                       "Creative Commons Attribution-ShareAlike 4.0 International License\". robots.txt disallows only "
                       "searches and the cohort pages; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("US Department of Education and OSERS assistive technology guides (for example \"Myths and Facts Surrounding "
     "Assistive Technology Devices and Services\", 2024)", "Public domain, but www.ed.gov and sites.ed.gov answer "
     "programs \"403 Forbidden\" (robots.txt included, checked 2026-11-22), and no Internet Archive item of them was "
     "found. Link-only. Index: https://sites.ed.gov/idea/idea-files/"),
    ("AT Act state program guides (AT3 Center)", "at3center.net refuses programs (403, checked 2026-11-22). Link-only. "
     "Index: https://at3center.net/state-at-programs/"),
    ("NVDA add-on documentation site (addons.nvda-project.org)", "Its robots.txt says \"Content-Signal: "
     "ai-train=no\", so it is not read; the same add-ons' documentation is read from their own repositories "
     "(atdoc:nvda_addons_gpl2, atdoc:nvda_addons_open). Index: https://addons.nvda-project.org/"),
    ("NVDA add-ons without an open licence in their store entry", "Listed in the store but not copied: their "
     "licence is not one the toolkit may repackage. Index: https://www.nvaccess.org/addonstore-legacy/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
