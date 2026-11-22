"""The master guide to the owner's whole library: one readable book, made from the code and the published catalogues
every time it is built, so it never goes stale (the owner's request of 22 November 2026: "see and trust the whole
library"). Key: libguide:my_library (not "guide:", which the government web guides of sources.GOV_GUIDES use in
the builder and the weekly check). Request word: library-guide. Group: "Reference, my library guide".

What the book holds, one page per area (each page has headings for a screen reader's heading keys, and a start page
links to every page):
  - Reference books: every group of the reference library (sources.GROUPS), each on its own page, with every book:
    its title, what it covers in one line, its size when the published catalogue (textbooks.json) lists it, and its
    licence class (open, share-alike, personal use, link-only). Books the code lists but no build has published yet
    are listed too, marked "not built yet". The books that were checked and NOT built (NOT_INCLUDED) have a page of
    their own, with the reason.
  - Manual collections: every heading and category (manuals/categories.py) with its description, and the number of
    entries the published manuals.json lists.
  - Training kit topic add-ons: every topic (training-kit/kit/topics.py) with its collections: title, licence class
    and whether a picture-making model may learn from it.
  - Picture packs: every pack (packs/build_packs.py PACKS) with its subject and its size and picture count from the
    published packs.json, grouped by the topic add-on that uses it.
  - Writing Kit: every source of the writing-kit branch's writing-kit/kit/writing_sources.py (and its sources_*.py
    files), read as text from GitHub: name, writing style, size where its notes state one, licence class.
  - Program Downloader's folders on B: (Data packs, Original sources, Software, Kiwix, AI models, Radio) and what
    each holds; and where each part of the library lands on the B: drive.
  - The size plan (tools/size_plan.py) and the build health check (tools/health_check.py): read from a folder named
    by the environment variable LIBRARY_REPORTS_DIR when set (reports made just before), else from the release
    "library-reports" when the Library reports workflow has published them, otherwise worked out at build time.
The code of each part is read by tools/library_inventory.py in a separate Python process (the training kit has its
own sources.py, which must not mix with this folder's). Only public sources are read: the GitHub releases and API
(unauthenticated, or with the GitHub Actions run's own token) and raw.githubusercontent.com. If one part cannot be
read, its page says so plainly and the rest of the book is still built.

Run from the repository's folder:
  python3 textbooks/library_guide.py library-guide --out build/textbooks
  python3 textbooks/library_guide.py libguide:my_library --out build/textbooks --limit 3      (a small test build)
"""

import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
import refs_kit as K  # noqa: E402

KEY = "libguide:my_library"
WORD = "library-guide"
GROUP = "libguide"
GROUPS = {GROUP: "Reference, my library guide"}
REPO_URL = "https://github.com/mark-getbraille/toolkit-models"
NOTICE = ("Made by the toolkit-models build from its own code and the catalogues published in its GitHub releases on "
          "the day shown. Counts and sizes change with every build; build this guide again (request word "
          "library-guide) for the newest picture.")
LICENCE_LINES = {
    "libguide_my_library": "Written by the toolkit-models build itself from the repository's code and its own "
                           "published catalogues (titles, one-line descriptions, sizes and licence classes are facts); "
                           "given to the public domain under CC0 1.0.",
}
NOT_INCLUDED = []           # nothing was left out: every part of the library is described

# Program Downloader's folders on the B: drive (the owner's plan of 22 November 2026). Data packs and Original sources
# are in Program Downloader 1.4 (downloader/paths.py, backup.py, originals.py); the other four folders are being added
# to it, so their words here follow the plan and should be checked against the program's own guide when they ship.
FOLDERS = [
    ("Data packs", "B:\\Data packs",
     "Every data release of the owner's repositories, every version kept (Back up all data): the picture packs "
     "(training-data, needs-description), the reference books as ZIM files (textbooks and the other book releases), "
     "the manual collection indexes (manuals), the converted AI models (engine-models) and the place packs (maps). "
     "Laid out as <repository>\\<release>\\<files>, with each release's list (packs.json, textbooks.json, "
     "manuals.json) kept beside them, and a dated copy each time it changes."),
    ("Original sources", "B:\\Original sources",
     "The publishers' own files behind the books and manuals, where the licence and the site's robots.txt allow a "
     "program to download them: <textbooks or manuals>\\<group or category>\\<title>\\<file>. Every version kept. "
     "The ones that may not be downloaded are listed in \"Links to open yourself.html\" at the top of the folder; "
     "print-disabled books from the Internet Archive go in its printdisabled folder, marked personal use only."),
    ("Software", "B:\\Software",
     "Offline installers, every version kept and checked against each project's checksum (Program Downloader 1.5): "
     "NVDA first, then eSpeak NG, the public JAWS and ZoomText installers, 7-Zip, Firefox ESR, Python 3.12, "
     "LibreOffice, VLC, Audacity, Thorium Reader, Tesseract OCR, Kiwix, llama.cpp, CHIRP, Meshtastic, OpenSCAD, "
     "FreeCAD, Inkscape, OsmAnd, and the owner's own programs. README.txt gives the install order for a fresh "
     "computer; add more in \"My extra software.txt\"."),
    ("Kiwix", "B:\\Data packs\\Kiwix",
     "The Kiwix offline libraries (.zim files) chosen in Program Downloader's list: Wikipedia with pictures, "
     "Wiktionary, Wikivoyage, Wikibooks, Wikisource, Project Gutenberg, Khan Academy and every library the toolkit's "
     "catalogue names (the Stack Exchange sites are for reading only). The newest and the previous file of each."),
    ("AI models", "B:\\AI models",
     "The Qwen3-VL model files (4B and 8B) the toolkit and the topic add-ons run on, the same files the toolkit "
     "downloads, so the AI works without the internet."),
    ("Radio", "B:\\Radio",
     "Personal use: the FCC's weekly amateur licence database with \"Look up a call sign.cmd\" for offline call-sign "
     "lookup, and repeater lists from frequency coordinators that publish free lists (add more in \"Coordinator "
     "sites.txt\"). RepeaterBook exports and the ARRL directory are on the To do yourself list."),
]

# Where each part of the library lands on B: (release tags are matched by their first words).
LANDS = [
    ("Picture packs (training data)", "B:\\Data packs\\toolkit-models\\training-data\\",
     "one zip per pack (big ones in numbered parts), with packs.json"),
    ("Pictures that need a description", "B:\\Data packs\\toolkit-models\\needs-description\\",
     "needs-<pack>.v<N>.zip, with needs-manifest.json"),
    ("Reference books", "B:\\Data packs\\toolkit-models\\textbooks\\ (and one folder per book release: "
     "libretexts-..., courses-..., publications-..., medicines, textbooks-archive-...)",
     "one ZIM file per book, every version kept, with textbooks.json"),
    ("Personal-use book releases", "B:\\Data packs\\toolkit-models\\personal-...\\",
     "ZIM files for the owner's own use only"),
    ("Manual collections", "B:\\Data packs\\toolkit-models\\manuals\\",
     "one index file per category (manuals-<key>.json.gz), with manuals.json"),
    ("The manuals themselves and the books' original files", "B:\\Original sources\\",
     "textbooks\\<group>\\<title>\\ and manuals\\<category>\\<title>\\, plus Links to open yourself.html"),
    ("Converted AI models", "B:\\Data packs\\toolkit-models\\engine-models\\", "zips, big ones in numbered parts"),
    ("Original AI models", "B:\\AI models\\", "one folder per Hugging Face model"),
    ("Place packs (maps)", "B:\\Data packs\\place-packs\\<release>\\", ".osmpack files"),
    ("Kiwix libraries", "B:\\Data packs\\Kiwix\\", ".zim files"),
    ("Software installers", "B:\\Software\\", "every version, with README.txt"),
    ("Radio data", "B:\\Radio\\", "FCC licence database and repeater lists (personal use)"),
    ("Writing Kit data", "the folder you choose when you run the Writing Kit (for example B:\\Writing data\\)",
     "the newspapers alone need about 340 GB to download and about 190 GB for the built data"),
]


# ====================================================================== reading everything (at build time)

REPORTS_ENV = "LIBRARY_REPORTS_DIR"     # a folder holding size-plan.json and health-check.json made just now (optional)


def local_report(name):
    """A report made on this computer (in the folder named by the environment variable LIBRARY_REPORTS_DIR), read
    before the published one; None when there is none."""
    import json
    folder = os.environ.get(REPORTS_ENV, "")
    path = os.path.join(folder, name)
    if folder and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def collect():
    """Everything the guide shows, read now: the code (library_inventory, one process per part), the catalogues,
    the Writing Kit's sources, the size plan and health check reports. A part that cannot be read is
    {"error": "..."} (its page says so)."""
    import library_common as C
    import library_inventory as L
    data = {"date": datetime.date.today().isoformat()}
    for part in ("books", "packs", "kit", "manuals"):
        try:
            data[part] = L.inventory(part)
        except Exception as e:  # noqa: BLE001 - said on the page
            data[part] = {"error": str(e)}
    data["catalogues"] = C.catalogues()
    try:
        data["writing"] = C.parse_writing_sources(C.writing_kit_texts())
    except Exception as e:  # noqa: BLE001 - said on the page
        data["writing"] = {"error": str(e)}
    for field, name in (("size_plan", "size-plan.json"), ("health", "health-check.json")):
        data[field] = local_report(name) or C.release_file_json("library-reports", name)
    if data["health"] is None:
        try:
            import health_check
            inv = {p: data[p] for p in ("books", "packs", "kit", "manuals")}
            data["health"] = health_check.run_check(cats=data["catalogues"], inv=inv, logs=0)
            data["health"]["date"] = data["date"] + " (worked out while this guide was built)"
        except Exception as e:  # noqa: BLE001 - said on the page
            data["health"] = {"error": str(e)}
    if data["size_plan"] is None:
        try:
            import size_plan
            data["size_plan"] = size_plan.gather()
            data["size_plan"]["date"] = data["date"] + " (worked out while this guide was built)"
        except Exception as e:  # noqa: BLE001 - said on the page
            data["size_plan"] = {"error": str(e)}
    return data


# ====================================================================== small helpers for the pages

def esc(text):
    """HTML-escaped text."""
    import html
    return html.escape(str(text or ""), quote=True)


def size_words(n):
    """A size in words ("1.2 GB"), or "" when it is not known."""
    import library_common as C
    return C.size_words(n) if n else ""


def slug(text):
    """A page address part from a name ("Reference, knots" -> "reference-knots")."""
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60] or "page"


def class_of_book(b):
    """The licence class of a published book (textbooks.json entry)."""
    import library_common as C
    return C.licence_class(b.get("licence_kind") or b.get("licence", ""), bool(b.get("personal_use")),
                           bool(b.get("link_only")))


def kit_class(group):
    """The licence class of a training kit collection group."""
    return {"permissive": "open", "share-alike": "share-alike", "noncommercial": "personal use",
            "research": "personal use"}.get(group, group or "unknown")


def error_part(data, part):
    """The paragraph saying a part could not be read, or "" when it was."""
    d = data.get(part)
    if isinstance(d, dict) and d.get("error"):
        return f"<p>This part could not be read when the guide was built: {esc(d['error'][:400])}</p>"
    if d is None:
        return "<p>This part is not published yet.</p>"
    return ""


CLASS_ORDER = ["open", "share-alike", "personal use", "link-only", "unknown", "not built yet"]
CLASS_HELP = {
    "open": "Open: may be used and shared by anyone, with credit.",
    "share-alike": "Share-alike: may be shared; whatever is made from it keeps the same licence.",
    "personal use": "Personal use: for your own computer only; never shared or sold.",
    "link-only": "Link-only: not copied by the builds; you open it or fetch it yourself with Program Downloader.",
    "unknown": "Licence class not recorded in the code.",
}


# ====================================================================== the pages

def page(path, title, body):
    """A build_textbooks.Page."""
    import build_textbooks as B
    return B.Page(path, title, body)


def book_rows(data):
    """{group key: [{"title", "about", "size", "class", "built"}]} of every book: the published ones from
    textbooks.json, then the code's books no build has published yet. Also returns {group key: group name}."""
    books = data.get("books") if isinstance(data.get("books"), dict) and not data["books"].get("error") else {}
    cat = (data.get("catalogues") or {}).get("textbooks") or {}
    names = dict(cat.get("groups") or {})
    names.update(books.get("groups") or {})
    rows, keys_built = {}, set()
    for b in cat.get("books", []):
        keys_built.add(b.get("key"))
        rows.setdefault(b.get("group") or "reference", []).append(
            {"title": b.get("title") or b.get("name", ""), "about": b.get("description", ""),
             "size": b.get("size"), "class": class_of_book(b), "built": True, "key": b.get("key", "")})
    keys_built |= set(cat.get("pieces_done") or [])
    for e in books.get("books", []):
        if e["key"] in keys_built:
            continue
        rows.setdefault(e.get("group") or "reference", []).append(
            {"title": e.get("title") or e["key"], "about": e.get("description", ""), "size": None,
             "class": e.get("class") or "unknown", "built": False, "key": e["key"]})
    for g in rows:
        rows[g].sort(key=lambda r: (r["title"] or "").lower())
    return rows, names


def reference_pages(data):
    """The Reference books page and one page per group (and the page of books checked and not built)."""
    rows, names = book_rows(data)
    order = sorted(rows, key=lambda g: names.get(g, g).lower())
    body = [error_part(data, "books"),
            "<p>Every group of the reference library, with how many books it has, how many are built and their total "
            "size. Each group has its own page listing every book. Licence classes:</p><ul>"]
    body += [f"<li>{esc(v)}</li>" for k, v in CLASS_HELP.items() if k != "unknown"]
    body.append("</ul><h2>The groups</h2><ul>")
    pages = []
    for g in order:
        rs = rows[g]
        built = [r for r in rs if r["built"]]
        total = sum(r["size"] or 0 for r in built)
        name = names.get(g, g)
        path = f"books-{slug(g)}"
        body.append(f'<li><a href="{path}">{esc(name)}</a>: {len(rs)} books, {len(built)} built'
                    f'{(", " + size_words(total)) if total else ""}.</li>')
        gb = [f"<p>{len(rs)} books, {len(built)} of them built"
              f"{(', ' + size_words(total) + ' in all') if total else ''}. "
              f"The books are listed under their licence class, A to Z.</p>"]
        for cls in CLASS_ORDER:
            these = [r for r in rs if (r["class"] if r["built"] else "not built yet") == cls]
            if not these:
                continue
            gb.append(f"<h2>{esc(cls.capitalize())} ({len(these)})</h2>")
            if cls in CLASS_HELP:
                gb.append(f"<p>{esc(CLASS_HELP[cls])}</p>")
            elif cls == "not built yet":
                gb.append("<p>Listed in the code but not yet published by a build (still to come, still building or "
                          "failed: see the build health check page).</p>")
            gb.append("<ul>")
            for r in these:
                bits = [esc(r["title"])]
                if r["about"]:
                    bits.append(esc(r["about"]))
                if r["size"]:
                    bits.append(esc(size_words(r["size"])))
                if not r["built"] and r["class"] not in ("", "unknown"):
                    bits.append(f"licence class {esc(r['class'])}")
                gb.append("<li>" + ". ".join(b.rstrip(".") for b in bits) + ".</li>")
            gb.append("</ul>")
        pages.append(page(path, f"Books: {name}", "".join(gb)))
    body.append('</ul><h2>Checked and not built</h2><p><a href="books-not-built">Sources that were checked and not '
                'built</a>, each with the reason (copyright, a site that refuses programs, and so on).</p>')
    pages.insert(0, page("reference-books", "Reference books", "".join(body)))
    pages.append(not_built_page(data))
    return pages


def not_built_page(data):
    """The sources checked and not built, from the code (NOT_INCLUDED) and the catalogue (not_included)."""
    books = data.get("books") if isinstance(data.get("books"), dict) else {}
    cat = (data.get("catalogues") or {}).get("textbooks") or {}
    seen, rows = set(), []
    for r in list(books.get("not_included", [])) + list(cat.get("not_included", [])):
        title = r.get("title", "")
        if title and title not in seen:
            seen.add(title)
            rows.append(r)
    rows.sort(key=lambda r: r["title"].lower())
    body = [f"<p>{len(rows)} sources were looked at and not built. Link-only ones can be fetched for your own use "
            f"with Program Downloader (its To do yourself list).</p><ul>"]
    body += [f"<li>{esc(r['title'])}: {esc(r.get('reason', ''))}</li>" for r in rows]
    body.append("</ul>")
    return page("books-not-built", "Books checked and not built", "".join(body))


def manuals_page(data):
    """Every manual heading and category, with its description and the published entries."""
    cats = data.get("manuals") if isinstance(data.get("manuals"), dict) else {}
    pub = ((data.get("catalogues") or {}).get("manuals") or {}).get("collections") or {}
    if isinstance(pub, list):
        pub = {c.get("key"): c for c in pub}
    by_heading = {}
    for c in cats.get("categories", []):
        by_heading.setdefault(c.get("heading") or "", []).append(c)
    body = [error_part(data, "manuals"),
            f"<p>{len(cats.get('categories', []))} manual collections. Each is an index of products with the "
            f"addresses of their makers' manuals (the manuals stay the makers' and are fetched for your own use), or, "
            f"for a few, instructions published in full. Collections without a heading of their own are in the main "
            f"list.</p>"]
    for heading in sorted(by_heading, key=lambda h: (h != "", h.lower())):
        items = sorted(by_heading[heading], key=lambda c: c["name"].lower())
        body.append(f"<h2>{esc(heading or 'The main list')} ({len(items)})</h2>")
        for c in items:
            p = pub.get(c["key"]) or {}
            state = (f"{p.get('entries', 0):,} entries, {p.get('manual_count', 0):,} manuals"
                     f"{(', ' + size_words(p.get('manuals_size'))) if p.get('manuals_size') else ''}, built "
                     f"{p.get('built', '')}") if p else "not built yet"
            body.append(f"<h3>{esc(c['name'])}</h3><p>{esc(c.get('description', ''))} Licence of the index: "
                        f"{esc(c.get('licence', ''))}. {esc(state)}.</p>")
    return page("manuals", "Manual collections", "".join(body))


def kit_page(data):
    """Every training kit topic add-on with its collections (title, licence class, picture-making allowed)."""
    kit = data.get("kit") if isinstance(data.get("kit"), dict) else {}
    cols = kit.get("collections", {})
    body = [error_part(data, "kit"),
            "<p>Each topic add-on teaches the picture describer one subject. For each collection: its title, its "
            "licence class, and whether a picture-making model may learn from it (never from people's bodies, "
            "children, graphic or sexual pictures, or personal-use collections whose terms do not allow it).</p>"]
    for t in kit.get("topics", []):
        body.append(f"<h2>{esc(t['title'])}</h2><p>{esc(t['description'])}"
                    f"{' Sensitive: only loaded when you choose it.' if t.get('sensitive') else ''}"
                    f"{' Always personal use only.' if t.get('personal_only') else ''}</p><ul>")
        for key in t.get("keys", []):
            c = cols.get(key)
            if not c:
                body.append(f"<li>{esc(key)}: not in the kit's list of collections.</li>")
                continue
            body.append(f"<li>{esc(c['name'])}. Licence class {esc(kit_class(c['group']))}. Picture-making "
                        f"{'allowed' if c['picture_making'] else 'not allowed'}.</li>")
        body.append("</ul>")
    return page("training-kit", "Training kit topic add-ons", "".join(body))


def packs_page(data):
    """Every picture pack with its subject, pictures and size, grouped by the topic add-on that uses it."""
    packs = data.get("packs") if isinstance(data.get("packs"), dict) else {}
    kit = data.get("kit") if isinstance(data.get("kit"), dict) else {}
    cols = kit.get("collections", {})
    pub = (data.get("catalogues") or {}).get("packs") or {}
    topic_of = {}
    for t in kit.get("topics", []):
        for k in t.get("keys", []):
            topic_of.setdefault(k, t["title"])
    groups = {}
    for p in packs.get("packs", []):
        groups.setdefault(topic_of.get(p["key"], "Packs not in a topic add-on"), []).append(p)
    total = sum((v or {}).get("size", 0) or 0 for v in pub.values())
    body = [error_part(data, "packs"),
            f"<p>{len(packs.get('packs', []))} picture packs in the code; {len(pub)} published"
            f"{(', ' + size_words(total) + ' in all') if total else ''}. Grouped by the topic add-on that uses each "
            f"pack (a pack used by several topics is under the first).</p>"]
    for g in sorted(groups, key=lambda g: (g.startswith("Packs not"), g.lower())):
        body.append(f"<h2>{esc(g)} ({len(groups[g])})</h2><ul>")
        for p in sorted(groups[g], key=lambda p: (cols.get(p["key"], {}).get("name") or p["key"]).lower()):
            c = cols.get(p["key"], {})
            v = pub.get(p["key"])
            state = (f"{v.get('rows', v.get('pictures', 0)):,} pictures, {size_words(v.get('size'))}" if v
                     else "not published yet")
            body.append(f"<li>{esc(c.get('name') or p.get('about') or p['key'])} ({esc(p['key'])}). {esc(state)}. "
                        f"Licence class {esc(kit_class(c.get('group', '')))}.</li>")
        body.append("</ul>")
    return page("picture-packs", "Picture packs", "".join(body))


def writing_page(data):
    """The Writing Kit's sources: name, style, size, licence class."""
    w = data.get("writing")
    if isinstance(w, dict):
        return page("writing-kit", "Writing Kit sources", error_part(data, "writing"))
    body = [f"<p>{len(w or [])} sources of the Writing Kit (read from its branch, writing-kit). The style is the "
            f"kind of writing it teaches; \"several\" means each example gets its own. Sizes are given where the "
            f"kit's notes state one.</p>"]
    for cls in ("open", "share-alike", "personal use only"):
        these = [s for s in w or [] if s.get("class") == cls]
        if not these:
            continue
        body.append(f"<h2>{esc(cls.capitalize())} ({len(these)})</h2><ul>")
        for s in sorted(these, key=lambda s: s["name"].lower()):
            body.append(f"<li>{esc(s['name'])} ({esc(s['key'])}). Style: {esc(s.get('style') or 'several')}."
                        f"{(' Size: ' + esc(s['size']) + '.') if s.get('size') else ''}</li>")
        body.append("</ul>")
    return page("writing-kit", "Writing Kit sources", "".join(body))


def folders_page():
    """Program Downloader's folders on the B: drive."""
    body = ["<p>Program Downloader puts everything into these folders on the big B: drive.</p>"]
    for name, where, what in FOLDERS:
        body.append(f"<h2>{esc(name)}</h2><p>Folder: {esc(where)}. {esc(what)}</p>")
    return page("program-downloader", "Program Downloader folders", "".join(body))


def drive_page(data):
    """Where each part of the library lands on B:, with the releases published now."""
    body = ["<p>Where each part of the library goes on the B: drive.</p>"]
    for what, where, files in LANDS:
        body.append(f"<h2>{esc(what)}</h2><p>{esc(where)}: {esc(files)}.</p>")
    plan = data.get("size_plan") or {}
    rows = [r for r in plan.get("rows", []) if ": " in r.get("item", "") and r.get("area") not in
            ("Kiwix libraries", "Writing Kit corpora", "AI models (originals on Hugging Face)")]
    if rows:
        body.append("<h2>The data releases published now</h2><ul>")
        for r in sorted(rows, key=lambda r: r["item"]):
            repo, tag = r["item"].split(": ", 1)
            body.append(f"<li>B:\\Data packs\\{esc(repo)}\\{esc(tag)}\\: {r['files']} files, "
                        f"{esc(size_words(r['all']))}.</li>")
        body.append("</ul>")
    return page("b-drive", "Where things land on B:", "".join(body))


def size_page(data):
    """The size plan as a page."""
    plan = data.get("size_plan")
    if not isinstance(plan, dict) or plan.get("error"):
        return page("size-plan", "Size plan", error_part(data, "size_plan") or
                    "<p>The size plan is not published yet: run the Library reports workflow.</p>")
    import size_plan
    lines = size_plan.report_lines(plan, plan.get("date", ""))
    return page("size-plan", "Size plan", lines_html(lines[1:]))


def health_page(data):
    """The build health check as a page."""
    h = data.get("health")
    if not isinstance(h, dict) or h.get("error"):
        return page("health-check", "Build health check", error_part(data, "health") or
                    "<p>The health check is not published yet: run the Library reports workflow.</p>")
    import health_check
    return page("health-check", "Build health check", lines_html(health_check.report_lines(h, h.get("date", ""))[1:]))


def lines_html(lines):
    """A plain-text report as HTML: a line in capitals becomes a heading (level 2, or 3 when indented), indented
    lines under it become list items, other lines paragraphs."""
    out, in_list = [], False
    for line in lines:
        text = line.strip()
        if not text:
            continue
        indent = len(line) - len(line.lstrip())
        heading = text.upper() == text and re.search(r"[A-Z]{3}", text) and not text.endswith(".")
        if heading or (indent and text.startswith("Cause:")):
            if in_list:
                out.append("</ul>")
                in_list = False
            level = 2 if indent == 0 else 3
            out.append(f"<h{level}>{esc(text[:1] + text[1:].lower() if heading else text)}</h{level}>")
        elif indent:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{esc(text)}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{esc(text)}</p>")
    if in_list:
        out.append("</ul>")
    return "".join(out)


def start_page(data, pages):
    """The start page: what the guide is, how to move around, and a link to every page."""
    cat = data.get("catalogues") or {}
    t = (cat.get("textbooks") or {}).get("books", [])
    p = cat.get("packs") or {}
    m = ((cat.get("manuals") or {}).get("collections")) or {}
    plan = data.get("size_plan") or {}
    import library_common as C
    body = [f"<p>This guide describes your whole library as it was on {esc(data.get('date', ''))}: the reference "
            f"books, the manual collections, the picture packs and topic add-ons, the Writing Kit, and where each "
            f"of them goes on your B: drive. It is made from the code and the published catalogues every time it is "
            f"built, so it does not go out of date: build it again with the request word library-guide.</p>",
            "<p>Each page uses headings: your screen reader's heading keys (H, or 2 and 3 for a level) move between "
            "them, and the links at the bottom of every page go to the previous and next pages and the contents.</p>",
            "<h2>At a glance</h2><ul>",
            f"<li>Reference books published: {len(t):,}.</li>",
            f"<li>Picture packs published: {len(p):,}.</li>",
            f"<li>Manual collections published: {len(m):,}.</li>"]
    if plan.get("total_all"):
        body.append(f"<li>The whole library needs about {esc(C.size_words(plan['total_all']))} with every version "
                    f"kept. {esc(plan.get('recommendation', ''))}</li>")
    body.append("</ul><h2>The pages</h2><ul>")
    body += [f'<li><a href="{esc(pg.path)}">{esc(pg.title)}</a></li>' for pg in pages
             if not pg.path.startswith("books-") or pg.path == "books-not-built"]
    body.append("</ul>")
    return page("start", "Start here", "".join(body))


def build_pages(data):
    """Every page of the guide, in reading order, from the collected data (collect(); tests give made-up data)."""
    pages = []
    ref = reference_pages(data)
    pages.append(ref[0])
    pages += [manuals_page(data), kit_page(data), packs_page(data), writing_page(data), folders_page(),
              drive_page(data), size_page(data), health_page(data)]
    pages += ref[1:]
    return [start_page(data, pages)] + pages


# ====================================================================== the book and its key

def make_guide(name, work, cache, left_out, limit=None, data=None):
    """The guide as a build_textbooks.Book (refs_kit maker). data: the collected data (None: read now)."""
    data = data if data is not None else collect()
    pages = build_pages(data)
    if limit:
        pages = pages[:limit]
    return K.new_book("libguide_my_library", "My library: the master guide", "Guide to the whole library", GROUP,
                      "GetBraille.com (toolkit-models)", K.CC0, K.CC0_URL, REPO_URL,
                      "One readable guide to the owner's whole library: every reference book group and book, every "
                      "manual collection, every training kit topic and picture pack, the Writing Kit's sources, "
                      "Program Downloader's folders on B:, the size plan and the build health check.",
                      NOTICE, pages=pages, published=data.get("date", ""), country="International")


def sign_guide(name):
    """The weekly check's sign of change: a fingerprint of what the code lists and the dates of the catalogues and
    reports, so the guide is built again when any of them changes ("" when nothing can be read)."""
    import library_common as C
    import library_inventory as L
    parts = []
    for part in ("books", "packs", "kit", "manuals"):
        try:
            parts.append(L.inventory(part))
        except Exception:  # noqa: BLE001 - that part is left out of the sign
            parts.append(None)
    cats = C.catalogues()
    parts.append({k: (v or {}).get("built") if isinstance(v, dict) else None for k, v in cats.items()})
    parts.append(len(cats.get("packs") or {}))
    if not any(parts[:4]):
        return ""
    return K.sha(*parts)


COLLECTION = K.Collection("libguide", GROUP, makers={"my_library": (make_guide, sign_guide)},
                          words={WORD: lambda: [KEY]})


if __name__ == "__main__":
    sys.exit(K.main_for(COLLECTION, __doc__))
