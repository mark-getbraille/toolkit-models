"""State laws: each state's statutes as books, from the state's own official site or bulk download, for the reference
library, in the group "Reference, state laws" (the owner's request of 2026-11-22). Keys: statelaw:<state> (one book
per state), or statelaw:<state>:<volume> for a state published in volumes (Georgia); request words state-laws (every
state), state-laws-1, state-laws-2, ... (the same keys in batches of at most 256 jobs) and state-law:<state> (one
state's keys).

Why these may be copied: since Georgia v. Public.Resource.Org, 590 U.S. 255 (2020), state statutes and the official
annotations a legislature makes are not under copyright (the "government edicts" doctrine). Each site was still
checked one by one (2026-11-22): its robots.txt allows our reader and does not shut out AI readers or say
ai-train=no, and its terms or disclaimer claim no copyright in the statutes. Every build asks robots.txt again.

What each book holds, in plain words: the state's code as the state publishes it that day, one page per chapter (or
per volume for Georgia), in the code's own order, each page with the chapter's whole text
as printed (section numbers, headings, history lines). The notice says the day it was read ("as of"), that the law
changes after every legislative session, and that this is not legal advice. The states built:
  - Nevada: the Nevada Revised Statutes (NRS), one HTML page per chapter, from www.leg.state.nv.us/NRS/;
  - North Carolina: the General Statutes, one HTML page per chapter, from www.ncleg.gov;
  - North Dakota: the North Dakota Century Code, one PDF per chapter, from ndlegis.gov;
  - Iowa: the Iowa Code (the current year's official edition), one PDF per chapter, from www.legis.iowa.gov;
  - South Dakota: the South Dakota Codified Laws, one HTML page per chapter, from the Legislature's own data service
    (sdlegislature.gov/api/Statutes, the same data its web pages show);
  - Georgia: the Official Code of Georgia Annotated, current as of August 2024, as the State of Georgia supplied it
    to Public.Resource.Org under the Open Records Act and the Internet Archive publishes it (item gov.ga.ocga.2024,
    marked public domain): one book per bound volume (statelaw:georgia:<volume>), since the official site is
    LexisNexis's, whose terms forbid copying.
  - New York: a SIGN-UP entry (statelaw:new_york): the Senate's Open Legislation API needs the owner's own free key
    (NYSENATE_API_KEY in the build's settings, never in the repository); without it the build says where to sign up.
Every other state, DC and Puerto Rico is in NOT_INCLUDED with what was found and what is needed.

Requests go one at a time with the builder's pause (build_textbooks.fetch, refs_kit.download_file); chapter PDFs are
kept in the cache folder.

Run from the repository's folder:
  python3 textbooks/state_laws.py statelaw:nevada --out build/textbooks --limit 3
  python3 textbooks/state_laws.py --list state-laws
"""

import datetime
import html
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "statelaw"
GROUPS = {GROUP: "Reference, state laws"}
STATE_LAW = "Public domain (state law: Georgia v. Public.Resource.Org, 2020)"
STATE_LAW_URL = "https://www.supremecourt.gov/opinions/19pdf/18-1150_7m58.pdf"
ALLOWED = {STATE_LAW: "open"}
BATCH = 256                                  # at most so many jobs in one request word

# Words every state book's notice ends with.
LAW_NOTE = ("State statutes are not under copyright (Georgia v. Public.Resource.Org, 2020). The law changes after "
            "every legislative session and courts interpret it: this is not legal advice; check the current law on "
            "the state's own site and, for your own situation, ask a lawyer or your local legal aid office.")


def state(key, name, code, publisher, kind, site, terms, **more):
    """One state: key ("north_carolina"), its name, the code's name, the publisher, the kind of source ("html",
    "pdf", "sd_api" or "archive"), the site's address and what its terms say (checked 2026-11-22); more: index (the
    page or pages listing the chapters), link (a regular expression whose first group is a chapter's address),
    content (where a chapter page's text begins and ends), and for "archive" the Internet Archive item."""
    return dict(dict(key=key, name=name, code=code, publisher=publisher, kind=kind, site=site, terms=terms,
                     index=[], link="", content=None), **more)


STATES = [
    state("nevada", "Nevada", "Nevada Revised Statutes (NRS)", "Legislative Counsel Bureau, Nevada Legislature", "html",
          "https://www.leg.state.nv.us/NRS/", "No copyright claim on the NRS pages or the site (checked 2026-11-22).",
          index=["https://www.leg.state.nv.us/NRS/"], link=r'href="(NRS-[0-9A-Z]+\.html)"'),
    state("north_carolina", "North Carolina", "General Statutes of North Carolina",
          "North Carolina General Assembly", "html", "https://www.ncleg.gov/Laws/GeneralStatutesTOC",
          "The site's disclaimer claims copyright only in some photographs and graphics, not in the statutes "
          "(www.ncleg.gov/Home/Disclaimer, checked 2026-11-22).",
          index=["https://www.ncleg.gov/Laws/GeneralStatutesTOC"],
          link=r'href="(/EnactedLegislation/Statutes/HTML/ByChapter/Chapter_[^"]+\.html)"'),
    state("north_dakota", "North Dakota", "North Dakota Century Code", "North Dakota Legislative Council", "pdf",
          "https://ndlegis.gov/general-information/north-dakota-century-code/index.html",
          "The site's disclaimer claims no copyright (ndlegis.gov/disclaimer, checked 2026-11-22).",
          index=["https://ndlegis.gov/general-information/north-dakota-century-code/index.html"],
          link=r'href="(/cencode/t[0-9a-z.\-]+c[0-9a-z.\-]+\.pdf)'),
    state("iowa", "Iowa", "Iowa Code (official edition)", "Legislative Services Agency, Iowa General Assembly", "pdf",
          "https://www.legis.iowa.gov/law/iowaCode",
          "The site's disclaimer says it holds official editions of legal publications as PDFs and claims no "
          "copyright (www.legis.iowa.gov/law/disclaimer, checked 2026-11-22).",
          index=["https://www.legis.iowa.gov/law/iowaCode"], hubs=r'href="(/law/iowaCode/chapters\?title=[A-Z]+&(?:amp;)?year=\d{4})"',
          link=r'href="(/docs/code/\d{4}/[0-9A-Za-z.]+\.pdf)"'),
    state("south_dakota", "South Dakota", "South Dakota Codified Laws", "South Dakota Legislative Research Council",
          "sd_api", "https://sdlegislature.gov/Statutes",
          "No copyright claim on the statutes; the data service is the one the Legislature's own pages read "
          "(checked 2026-11-22).", titles=[str(n) for n in range(1, 63)]),
    state("georgia", "Georgia", "Official Code of Georgia Annotated (OCGA), current as of August 2024",
          "State of Georgia (supplied to Public.Resource.Org under the Open Records Act; Internet Archive copy)",
          "archive", "https://archive.org/details/gov.ga.ocga.2024",
          "The very code of Georgia v. Public.Resource.Org: the Internet Archive item says \"The data is available for "
          "use without restriction per the order of the U.S. Supreme Court\" and is marked public domain; the "
          "official site (LexisNexis) forbids copying, so it is not read (checked 2026-11-22).",
          archive="gov.ga.ocga.2024"),
    # A SIGN-UP entry: built only when the owner has his own free Open Legislation key in the build's environment
    # (NYSENATE_API_KEY, a secret of the workflow or his own computer's settings; never in the repository). Without
    # it the build says where to sign up and adds nothing.
    state("new_york", "New York", "Consolidated and Unconsolidated Laws of New York",
          "New York State Senate (Open Legislation)", "nysenate", "https://legislation.nysenate.gov/",
          "Open Legislation is the Senate's open data service for the laws of New York; it needs a free key "
          "(sign up at https://legislation.nysenate.gov/); robots.txt allows programs (checked 2026-11-22).",
          key_variable="NYSENATE_API_KEY"),
]
STATES_BY_KEY = {s["key"]: s for s in STATES}


# ---------------------------------------------------------------------------------------------- finding chapters

def chapter_links(s, cache=None):
    """[address] of every chapter of a state with an index (kinds "html" and "pdf"), in the index's order: the index
    pages, or the hub pages they link (s["hubs"]), are read and every link matching s["link"] is taken once."""
    import build_textbooks as B
    pages = list(s["index"])
    if s.get("hubs"):
        hubs = []
        for page in pages:
            for h in re.findall(s["hubs"], B.fetch(page, cache)):
                hubs.append(urllib.parse.urljoin(page, html.unescape(h)))
        pages = list(dict.fromkeys(hubs))
    out = []
    for page in pages:
        for h in re.findall(s["link"], B.fetch(page, cache)):
            out.append(urllib.parse.urljoin(page, html.unescape(h)))
    return list(dict.fromkeys(out))


def archive_volumes(s, cache=None):
    """[(piece name, file name)] of the PDFs of a state's Internet Archive item ("v1", "C01 US Const (V1) 2007.pdf"),
    in the item's order; the piece is the volume number printed in the name."""
    import build_textbooks as B
    meta = json.loads(B.fetch(f"https://archive.org/metadata/{s['archive']}", cache))
    out = []
    for f in meta.get("files", []):
        if f.get("format") == "Text PDF":
            m = re.search(r"\(V(\d+[A-Z]?)\)", f["name"])
            out.append(((f"v{m.group(1)}" if m else re.sub(r"\W+", "_", f["name"])[:30]).lower(), f["name"]))
    return out


# Georgia's volumes, as read on 2026-11-22 (the weekly check reads the item again; a new volume appears there).
GEORGIA_VOLUMES = ["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v7a", "v8", "v9", "v10", "v11", "v12", "v13", "v13a",
                   "v14", "v14b", "v14a", "v15", "v16", "v17", "v17a", "v18", "v19", "v20", "v20a", "v21", "v22",
                   "v23", "v23a", "v24", "v25", "v26", "v27", "v28", "v28a", "v29", "v29a", "v30", "v30a", "v31",
                   "v32", "v33", "v34", "v35", "v36", "v37", "v37a", "v38", "v38a", "v39", "v40"]


# ---------------------------------------------------------------------------------------------- reading chapters

def html_chapter(url, cache=None):
    """(title, body HTML) of one chapter page: its <title> (with the chapter's name from its first lines when the
    title is only "Chapter 1"), and its body without scripts and styles, cleaned by the builder."""
    import build_textbooks as B
    data = B.fetch(url, cache, binary=True)
    charset = re.search(rb"charset=[\"']?([A-Za-z0-9_-]+)", data[:3000])
    try:
        text = data.decode(charset.group(1).decode("ascii") if charset else "utf-8", "replace")
    except LookupError:
        text = data.decode("utf-8", "replace")
    title = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", (re.search(r"<title>(.*?)</title>", text, re.S | re.I)
                                                             or [None, ""])[1])).split())
    body = (re.search(r"<body\b[^>]*>(.*)</body>", text, re.S | re.I) or [None, text])[1]
    for pattern in K.DROP:
        body = re.sub(pattern, "", body, flags=re.S | re.I)
    if re.fullmatch(r"Chapter\s+\S+", title or ""):
        words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", body[:4000])).split())
        m = re.search(r"Chapter\s+\S+\.\s+(.{3,120}?)\.", words)
        if m:
            title = f"{title}. {m.group(1)}"
    title = re.sub(r"^NRS:\s*", "", title or url.rsplit("/", 1)[-1])
    return title, B._Cleaner({}, url).clean(body)


def pdf_chapter(url, cache=None):
    """(title, body HTML) of one chapter PDF: its first printed line that names the chapter ("CHAPTER 1-01
    GENERAL PROVISIONS"), and its text with "[Page n]" marks (build_textbooks.part_html)."""
    import build_textbooks as B
    path = K.download_file(url, cache, name=re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.urlsplit(url).path)[-120:])
    text = B.PdfText(path)
    first = [line for n in range(min(2, text.count)) for line in text.lines(n)][:12]
    name = next((line for line in first if re.match(r"(?i)chapter\s+\S+", line)), "")
    i = first.index(name) if name in first else -1
    if name and re.fullmatch(r"(?i)chapter\s+\S+", name) and 0 <= i < len(first) - 1:
        name = f"{name} {first[i + 1]}"
    title = (name.title() if name.isupper() else name) or os.path.basename(urllib.parse.urlsplit(url).path)
    return title, B.part_html(text, 0, text.count)


def sd_chapters(s, cache=None, left_out=None, limit=None):
    """[(title, body HTML, address)] of South Dakota's chapters, one page per chapter, from the Legislature's data
    service: each title's record (sdlegislature.gov/api/Statutes/Statute/<title>) lists its chapters as links, and
    each chapter's record holds the chapter's whole text ("Html"). Repealed chapters are left out."""
    import build_textbooks as B
    out = []
    for t in s["titles"]:
        if limit and len(out) >= limit:
            break
        try:
            title = json.loads(B.fetch(f"{SD_API}{t}", cache))
        except (ValueError, OSError) as e:
            left_out.append({"title": f"South Dakota title {t}", "reason": f"It could not be read ({e})."})
            continue
        chapters = re.findall(r'href="https://sdlegislature\.gov/Statutes/(\d+[A-Z]?-\d+[A-Z]?(?:\.\d+)?)"',
                              title.get("Html") or "")
        for c in dict.fromkeys(chapters):
            if limit and len(out) >= limit:
                break
            url = f"{SD_API}{c}"
            try:
                data = json.loads(B.fetch(url, cache))
            except (ValueError, OSError) as e:
                left_out.append({"title": f"South Dakota chapter {c}", "reason": f"It could not be read ({e})."})
                continue
            if not data.get("Html") or data.get("Repealed"):
                continue
            body = (re.search(r"<body\b[^>]*>(.*)</body>", data["Html"], re.S | re.I) or [None, data["Html"]])[1]
            body = re.sub(r"(?s)<style\b.*?</style>", "", body)
            name = f"Chapter {c}. {str(data.get('CatchLine') or '').strip().title()}".strip(". ")
            out.append((name, B._Cleaner({}, url).clean(body), url))
    return out


SD_API = "https://sdlegislature.gov/api/Statutes/Statute/"
NY_API = "https://legislation.nysenate.gov/api/3/laws"


def ny_text(node):
    """The words of one node of an Open Legislation law tree and of every node under it, in order (its title first
    when the node has one)."""
    parts = []
    if node.get("title") and node.get("docType") not in ("SECTION",):
        parts.append(f"{node.get('docType', '').title()} {node.get('docLevelId', '')}. {node['title']}".strip())
    if node.get("text"):
        parts.append(node["text"])
    for child in (node.get("documents") or {}).get("items", []):
        parts.append(ny_text(child))
    return "\n\n".join(p for p in parts if p)


def ny_laws(s, cache=None, left_out=None, limit=None):
    """[(title, body HTML, address without the key)] of New York's laws, one page per article (or other top part) of
    each law, from Open Legislation; [] with a "sign up" line in left_out when the owner's key is not set."""
    import build_textbooks as B
    key = os.environ.get(s["key_variable"], "")
    if not key:
        left_out.append({"title": s["code"], "reason": f"A sign-up entry: it needs the owner's own free Open "
                         f"Legislation key (sign up at {s['site']}, then set {s['key_variable']} in the build's "
                         "settings, never in the repository).", "url": s["site"], "fetch_yourself": True})
        return []
    out = []
    laws = json.loads(B.fetch(f"{NY_API}?limit=1000&key={key}", None))["result"]["items"]
    for law in laws:
        if limit and len(out) >= limit:
            break
        law_id = law["lawId"]
        try:
            tree = json.loads(B.fetch(f"{NY_API}/{law_id}?full=true&key={key}", None))["result"]["documents"]
        except (ValueError, OSError, KeyError) as e:
            left_out.append({"title": f"New York {law.get('name', law_id)}", "reason": f"It could not be read "
                             f"({type(e).__name__})."})
            continue
        for part in (tree.get("documents") or {}).get("items", []) or [tree]:
            if limit and len(out) >= limit:
                break
            name = f"{law.get('name', law_id)}: {part.get('docType', '').title()} {part.get('docLevelId', '')} " \
                   f"{part.get('title', '')}".strip()
            out.append((" ".join(name.split()), K.text_html(ny_text(part)), f"{NY_API}/{law_id}"))
    return out


# ---------------------------------------------------------------------------------------------- the books

def notice_for(s, as_of):
    """A state book's notice: whose text it is, as of when, the terms checked, and the law note."""
    return (f"The {s['code']} as published by the {s['publisher']}, read {as_of}: later changes are not in it. "
            f"{s['terms']} {LAW_NOTE}")


def state_book(name, work, cache=None, left_out=None, limit=None):
    """The book of one state ("nevada"), or of one volume of a state in volumes ("georgia:v7a")."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    key, _, piece = name.partition(":")
    s = STATES_BY_KEY.get(key)
    if s is None:
        left_out.append({"title": name, "reason": "Not a state of this module."})
        return None
    as_of = datetime.date.today().isoformat()
    if s["kind"] == "archive":
        return archive_book(s, piece, work, cache, left_out, limit)
    start = s["index"][0] if s["index"] else s["site"]
    if not K.readable(start, cache):
        left_out.append({"title": s["code"], "reason": "Its site's robots.txt does not allow reading it, or shuts "
                         "out AI readers."})
        return None
    book = K.new_book(f"statelaw_{key}", f"{s['name']}: {s['code']}", f"Law ({s['name']} statutes)", GROUP,
                      s["publisher"], STATE_LAW, STATE_LAW_URL, s["site"],
                      f"The whole {s['code']} as the state publishes it on {as_of}, one page per chapter, in the "
                      "code's own order.",
                      notice_for(s, as_of), region=s["name"], changes="one page per chapter; the text as published")
    book.version, book.published = f"as of {as_of}", as_of
    if s["kind"] in ("sd_api", "nysenate"):
        read = sd_chapters if s["kind"] == "sd_api" else ny_laws
        for i, (title, body, url) in enumerate(read(s, cache, left_out, limit), 1):
            book.pages.append(B.Page(f"chapter-{i}-{B.slug(title, 40)}", title, body, i))
            book.originals.append({"url": url, "kind": "json"})
        return book if book.pages else None
    links = chapter_links(s, cache)
    if not links:
        left_out.append({"title": s["code"], "reason": "Its index lists no chapters (the site may have changed)."})
        return None
    read = html_chapter if s["kind"] == "html" else pdf_chapter
    paths = set()
    for i, url in enumerate(links, 1):
        if limit and len(book.pages) >= limit:
            break
        if not K.readable(url, cache):
            left_out.append({"title": url, "reason": "Not allowed by robots.txt."})
            continue
        try:
            title, body = read(url, cache)
        except Exception as e:  # noqa: BLE001 - one chapter is left out with its reason, the others are kept
            left_out.append({"title": url, "reason": f"It could not be read ({e})."})
            continue
        path = B.slug(title[:60], 60) or f"chapter-{i}"
        while path in paths or path in ("index", "style-css"):
            path += "-2"
        paths.add(path)
        book.pages.append(B.Page(path, title, body, i))
        book.originals.append({"url": url, "kind": s["kind"]})
    return book


def archive_book(s, piece, work, cache, left_out, limit=None):
    """One volume of a state published in volumes on the Internet Archive (Georgia), read by the builder's PDF reader
    (build_textbooks.pdfdoc_book: robots.txt, the text layer, one page per bookmarked part)."""
    import build_textbooks as B
    volumes = dict(archive_volumes(s, cache))
    if piece not in volumes:
        left_out.append({"title": f"{s['code']}, volume {piece}", "reason": "The Internet Archive item has no such "
                         "volume now."})
        return None
    file = volumes[piece]
    entry = dict(name=f"statelaw_{s['key']}_{piece}", title=f"{s['name']}: {s['code']}, {file.rsplit('.', 1)[0]}",
                 subject=f"Law ({s['name']} statutes)", group=GROUP, publisher=s["publisher"],
                 country="United States", licence=STATE_LAW, licence_url=STATE_LAW_URL, level="reference",
                 pdf=f"https://archive.org/download/{s['archive']}/{urllib.parse.quote(file)}", page=s["site"],
                 region=s["name"], published="2024-08",
                 description=f"Volume {piece.upper()[1:]} of the {s['code']} ({file.rsplit('.', 1)[0]}): the "
                             "statutes with the official annotations, as the State of Georgia supplied them.",
                 notice=(f"The {s['code']}, as the State of Georgia supplied it to Public.Resource.Org; each volume's "
                         "own year is in its name, and it is current only as of August 2024. " + s["terms"] + " "
                         + LAW_NOTE))
    book = B.pdfdoc_book(entry, work, cache, left_out)
    if book is not None:
        book.version = f"Internet Archive item {s['archive']}, file {file}"
        book.pages = book.pages[:limit] if limit else book.pages
    return book


def state_sign(name):
    """A state's weekly sign of change: the index page's (or the item's) date and size, with the quarter, so each
    state is read again at least every three months (statutes change after each session)."""
    import updates
    key = name.split(":", 1)[0]
    s = STATES_BY_KEY[key]
    today = datetime.date.today()
    quarter = f"{today.year}-q{(today.month - 1) // 3 + 1}"
    where = f"https://archive.org/metadata/{s['archive']}" if s["kind"] == "archive" else (s["index"] or [s["site"]])[0]
    return K.sha(updates.head_signs(where), quarter, name)


# ---------------------------------------------------------------------------------------------- keys and words

def state_keys(key):
    """The keys of one state: statelaw:<state>, or statelaw:<state>:<volume> for each volume."""
    if key == "georgia":
        return [f"statelaw:georgia:{v}" for v in GEORGIA_VOLUMES]
    return [f"statelaw:{key}"]


def all_keys():
    """Every state's keys, in the order of STATES."""
    return [k for s in STATES for k in state_keys(s["key"])]


def batches():
    """{"state-laws-1": [keys], ...}: every key in batches of at most BATCH jobs."""
    keys = all_keys()
    return {f"state-laws-{i // BATCH + 1}": keys[i:i + BATCH] for i in range(0, len(keys), BATCH)}


WORDS = {"state-laws": all_keys}
WORDS.update({word: (lambda keys=keys: list(keys)) for word, keys in batches().items()})
WORDS.update({f"state-law:{s['key']}": (lambda k=s["key"]: state_keys(k)) for s in STATES})

COLLECTION = K.Collection("statelaw", GROUP, makers={s["key"]: (state_book, state_sign) for s in STATES},
                          pieces={"georgia": lambda: list(GEORGIA_VOLUMES)}, words=WORDS)

LICENCE_LINES = {
    "state_laws": "State statutes and official annotations are not under copyright (Georgia v. Public.Resource.Org, "
                  "590 U.S. 255 (2020)). Sites checked 2026-11-22: www.leg.state.nv.us, www.ncleg.gov, ndlegis.gov, "
                  "www.legis.iowa.gov and sdlegislature.gov (robots.txt allows our reader and names no AI reader; "
                  "their terms or disclaimers claim no copyright in the statutes); the Georgia code from the "
                  "Internet Archive item gov.ga.ocga.2024 (marked public domain, \"available for use without "
                  "restriction per the order of the U.S. Supreme Court\").",
}

# What was checked for the other states, DC and Puerto Rico (2026-11-22), and what is needed.
NOT_INCLUDED = [
    ("Alaska Statutes", "www.akleg.gov's robots.txt says \"Content-Signal: ai-train=no\" and shuts out ClaudeBot "
     "and other AI readers: never read. Index: https://www.akleg.gov/basis/statutes.asp"),
    ("Virginia: Code of Virginia", "law.lis.virginia.gov's robots.txt shuts out GPTBot (an AI reader), so by the "
     "toolkit's rule it is not read, though its download and API are otherwise open. Index: "
     "https://law.lis.virginia.gov/"),
    ("Washington: Revised Code of Washington", "app.leg.wa.gov's robots.txt disallows everything. Index: "
     "https://app.leg.wa.gov/rcw/"),
    ("California codes", "leginfo.legislature.ca.gov refuses programs (403); its bulk database download "
     "(downloads.leginfo.legislature.ca.gov) was not checked. Index: https://leginfo.legislature.ca.gov/"),
    ("New York: Consolidated Laws (Open Legislation API)", "A SIGN-UP entry (statelaw:new_york): the Senate's Open "
     "Legislation API serves every law as JSON but needs a free key, and no key is in the repository or the build's "
     "settings. The owner signs up at https://legislation.nysenate.gov/ and sets NYSENATE_API_KEY (a workflow "
     "secret or his own computer's setting, never in the repository); until then the build says so and adds "
     "nothing. Index: https://legislation.nysenate.gov/"),
    ("Texas Constitution and Statutes", "statutes.capitol.texas.gov is a JavaScript application: every address, the "
     "zip downloads too, answers with the same empty page to a program (checked 2026-11-22). Index: "
     "https://statutes.capitol.texas.gov/"),
    ("Florida Statutes", "www.leg.state.fl.us claims copyright in its compilation of the statutes; not read until "
     "the owner decides (state statutes themselves are not copyrightable). Index: http://www.leg.state.fl.us/statutes/"),
    ("Illinois Compiled Statutes", "www.ilga.gov did not answer this build machine (no connection, checked "
     "2026-11-22). Index: https://www.ilga.gov/legislation/ilcs/ilcs.asp"),
    ("Ohio Revised Code", "codes.ohio.gov's robots.txt says \"User-agent: * Disallow: /\". Index: https://codes.ohio.gov/"),
    ("District of Columbia Code", "code.dccouncil.gov's robots.txt says ai-train=no and shuts out ClaudeBot. The DC "
     "Council also publishes the code as open XML on GitHub (DCCouncil/law-xml), which was not checked in this pass. "
     "Index: https://code.dccouncil.gov/"),
    ("Puerto Rico: Laws of Puerto Rico", "bvirtualogp.pr.gov (the official virtual library) did not answer this build "
     "machine, and no Internet Archive copy of the current official laws was found (only an 1899 translation). Index: "
     "https://bvirtualogp.pr.gov/"),
    ("Hawaii Revised Statutes", "www.capitol.hawaii.gov refuses programs (403). Index: https://www.capitol.hawaii.gov/"),
    ("Arkansas Code", "www.arkleg.state.ar.us shuts out ChatGPT readers in its robots.txt; the code itself is "
     "published by LexisNexis, whose terms forbid copying. Index: https://www.arkleg.state.ar.us/"),
    ("Nebraska Revised Statutes", "Its pages carry \"Copyright © Nebraska Legislature, all rights reserved\" (in the "
     "page's code); not read until the owner decides. Index: https://nebraskalegislature.gov/laws/browse-statutes.php"),
    ("Oregon Revised Statutes", "Allowed by robots.txt, but its chapter pages (www.oregonlegislature.gov/bills_laws/"
     "ors/ors001.html) are SharePoint pages whose text is mixed with page data; a reader for them is still to be "
     "written. Index: https://www.oregonlegislature.gov/bills_laws/Pages/ORS.aspx"),
    ("Colorado Revised Statutes", "The legislature's page links the statutes on LexisNexis (terms forbid copying); "
     "the yearly CRS PDFs on content.leg.colorado.gov were not found in this pass. Index: "
     "https://leg.colorado.gov/colorado-revised-statutes"),
    ("Utah Code", "le.utah.gov's code pages are drawn by JavaScript; its XML downloads were not found in this pass. "
     "Index: https://le.utah.gov/xcode/code.html"),
    ("Minnesota Statutes", "Allowed by robots.txt; the Revisor's copyright statement was not checked in this pass. "
     "Index: https://www.revisor.mn.gov/statutes/"),
    ("Kansas, Missouri, Delaware, Maine, Massachusetts, Montana, Rhode Island and Kentucky", "Their sites allow "
     "programs (robots.txt checked 2026-11-22) and publish the statutes by chapter or section, but their terms and "
     "page layouts were not checked one by one in this pass: next to add. Index: "
     "https://www.ncsl.org/about-state-legislatures/state-legislative-websites-directory"),
    ("Idaho Statutes", "legislature.idaho.gov's robots.txt shuts out AI readers (found by the earlier check of "
     "law_codes.py): never read. Index: https://legislature.idaho.gov/statutesrules/idstat/"),
    ("Wyoming, Arizona, Indiana, Michigan, Wisconsin, Connecticut, New Hampshire, Vermont, Pennsylvania, New Jersey, "
     "Maryland, Louisiana, Oklahoma, New Mexico, South Carolina, Tennessee, Alabama, Mississippi and West Virginia",
     "Not built in this pass: several did not answer this build machine (Connecticut, New Hampshire, Vermont, "
     "Wisconsin, West Virginia, Pennsylvania), New Mexico's and Tennessee's codes are on publishers' platforms with "
     "their own terms, Wyoming's download page is drawn by JavaScript, and the rest need their terms and layouts "
     "read. Index: https://www.ncsl.org/about-state-legislatures/state-legislative-websites-directory"),
    ("State administrative codes (regulations)", "Not built in this pass; each state's register and administrative "
     "code has its own site and terms. Index: https://www.administrativerules.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
