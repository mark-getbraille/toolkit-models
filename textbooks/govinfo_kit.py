"""Shared helpers for the history, travel and education collections of 2026-11-22 (history.py, travel_more.py and
education_more.py): books read from govinfo.gov (the Government Publishing Office) and from the Internet Archive's
copies of government pages that refuse programs on their own sites. Not a source module itself (it is not in
more_refs.MODULES).

What it gives them, in plain words:
  - govinfo_search_maker(): a SIGN-UP ENTRY. govinfo's search API (https://api.govinfo.gov/search) needs a free
    api.data.gov key. The key is read from the environment variable GOVINFO_API_KEY at build time and is never
    written into the repository; without it the book is not built and the manifest's left_out says where to sign
    up (https://api.data.gov/signup/), marked fetch_yourself for the owner's Program Downloader list. With the key,
    the builder searches govinfo for the entry's query (only the collections named, such as GOVPUB, the federal
    agencies' own publications), keeps the results whose title matches the entry's title pattern, and reads each
    one's PUBLIC PDF (https://www.govinfo.gov/content/pkg/...), which needs no key, whole into one book;
  - wayback_book(): a fixed list of an agency's pages read from the Wayback Machine's exact copies ("id_": the page
    as captured, without the Wayback Machine's own menus) of their official addresses, for agencies whose own sites
    answer programs "403" (the Department of Transportation, TSA, Customs and Border Protection, the State
    Department's travel site). Each capture is pinned (its date is in the address), so the book is the same every
    build until the list is changed; the notice says the date of the copy, and that rules may have changed since;
  - granule_maker(): a book of chosen documents from govinfo packages (such as the Public Papers of the
    Presidents), each found by its granule identifier in the package's MODS record, read from its public PDF.

govinfo.gov's robots.txt allows /content/ and /metadata/ (only its search pages, /app/search/, are closed to
robots) and has no AI rules (checked 2026-11-22). Nothing here imports the builder at the top (the builder imports
sources, which imports the modules at its end).
"""

import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GOVINFO = "https://www.govinfo.gov"
GOVINFO_API = "https://api.govinfo.gov"
GOVINFO_KEY_ENV = "GOVINFO_API_KEY"
GOVINFO_SIGNUP = "https://api.data.gov/signup/"
WAYBACK = "https://web.archive.org/web"


# ====================================================================== govinfo search (a sign-up entry)

def public_pdf(package, granule=""):
    """The public address of a govinfo package's (or one granule's) PDF: it answers without a key."""
    return f"{GOVINFO}/content/pkg/{package}/pdf/{granule or package}.pdf"


def search(key, query, collections, page_size=100):
    """[{title, package, granule, collection, date}] of govinfo's search for query in the collections (["GOVPUB"]),
    first page of results only, or None when the key is refused. The key goes in the X-Api-Key header (govinfo
    takes it there as well as in the address), never in the address, so it is not written to any log; and only to
    api.govinfo.gov, also when it answers "moved" (build_textbooks.keyed_urlopen)."""
    import build_textbooks as B
    q = query + (" AND (" + " OR ".join(f"collection:{c}" for c in collections) + ")" if collections else "")
    body = json.dumps({"query": q, "pageSize": page_size, "offsetMark": "*",
                       "sorts": [{"field": "score", "sortOrder": "DESC"}]}).encode("utf-8")
    try:
        with B.keyed_urlopen(f"{GOVINFO_API}/search", {"X-Api-Key": key}, data=body, method="POST",
                             headers={"User-Agent": B.USER_AGENT, "Content-Type": "application/json"},
                             timeout=120) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return None
        raise
    out = []
    for row in data.get("results", []):
        if not row.get("packageId"):
            continue
        out.append({"title": " ".join(str(row.get("title", "")).split()), "package": row["packageId"],
                    "granule": row.get("granuleId") or "", "collection": row.get("collectionCode", ""),
                    "date": row.get("dateIssued", "")})
    return out


def chosen_results(rows, title_pattern, most):
    """The results whose title matches title_pattern (case ignored), each package or granule once, at most most."""
    pattern, seen, out = re.compile(title_pattern, re.I), set(), []
    for row in rows:
        ident = row["granule"] or row["package"]
        if ident in seen or not pattern.search(row["title"]):
            continue
        seen.add(ident)
        out.append(row)
        if len(out) >= most:
            break
    return out


def govinfo_search_maker(prefix, group, name, title, subject, description, notice, query, title_pattern,
                         collections=("GOVPUB",), most=40):
    """(book function, sign function) of a sign-up entry: govinfo's search for query (see the module docstring)."""

    def book_fn(_name, work, cache=None, left_out=None, limit=None):
        """The book of the search's chosen results, each read whole from its public PDF."""
        import pdf_set
        left_out = left_out if left_out is not None else []
        key = os.environ.get(GOVINFO_KEY_ENV, "").strip()
        if not key:
            left_out.append({"title": title, "reason": f"A sign-up entry: it needs the owner's own free api.data.gov "
                             f"key for govinfo's search (sign up at {GOVINFO_SIGNUP}, then set {GOVINFO_KEY_ENV} in "
                             "the build's settings, never in the repository).", "url": GOVINFO_SIGNUP,
                             "fetch_yourself": True})
            return None
        rows = search(key, query, list(collections))
        if rows is None:
            left_out.append({"title": title, "reason": f"govinfo refused the key in {GOVINFO_KEY_ENV}; check it at "
                             f"{GOVINFO_SIGNUP}."})
            return None
        rows = chosen_results(rows, title_pattern, most)
        if not rows:
            left_out.append({"title": title, "reason": f"govinfo's search found no publication for \"{query}\" now.",
                             "url": f"{GOVINFO}/app/search"})
            return None
        parts = [(f"{r['title']}" + (f" ({r['date'][:10]})" if r["date"] else ""),
                  public_pdf(r["package"], r["granule"]),
                  f"{GOVINFO}/app/details/{r['package']}" + (f"/{r['granule']}" if r["granule"] else ""))
                 for r in rows]
        entry = K.us_pdf(group, name=f"{prefix}_{name}", title=title, subject=subject,
                         publisher="US government agencies, from govinfo.gov (Government Publishing Office)",
                         source=f"{GOVINFO}/app/search", description=description, notice=notice,
                         version=f"govinfo search \"{query}\"")
        book = pdf_set.pdf_set_book(entry, parts, work, cache, left_out, limit)
        if book is not None:
            book.published = max((r["date"][:10] for r in rows if r["date"]), default="")
            book.version = f"govinfo search \"{query}\", read {datetime.date.today().isoformat()}"
        return book

    def sign_fn(_name):
        """The weekly sign: the query and the month (a search can find new publications)."""
        import directory_sources as D
        return K.sha(query, title_pattern, D.month_token())

    return book_fn, sign_fn


# ====================================================================== the Wayback Machine's copies of pages

def capture(stamp, url):
    """The Wayback Machine's exact copy ("id_") of url captured at stamp ("20261115231232")."""
    return f"{WAYBACK}/{stamp}id_/{url}"


def stamp_date(stamp):
    """"20261115231232" -> "2026-11-15"."""
    return f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"


def wayback_book(group, name, title, subject, publisher, captures, description, notice, units=(), content=None,
                 **more):
    """A fixed list of an agency's pages [(capture stamp, official address)] read from the Wayback Machine's exact
    copies (see the module docstring). Its "published" is the newest capture's date."""
    urls = [capture(s, u) for s, u in captures]
    newest = max(stamp_date(s) for s, _u in captures)
    oldest = min(stamp_date(s) for s, _u in captures)
    when = newest if newest == oldest else f"{oldest} to {newest}"
    entry = X.page_list_book(
        group, name, title, subject, publisher, urls, r"^https://web\.archive\.org/web/\d{14}id_/https://",
        description, f"{notice} Read from the Internet Archive's Wayback Machine copies of the official pages "
        f"(captured {when}) because the agency's own site refuses programs; the rules may have changed since: "
        f"check the agency's site before you travel.", units=units,
        version=f"Wayback Machine copies captured {when}", published=newest, **more)
    if content:
        entry["content"] = content
    return entry


# ====================================================================== chosen documents of govinfo packages

def granule_maker(prefix, group, name, title, subject, publisher, description, notice, documents):
    """(book function, sign function) of a book of chosen documents: documents [(package, granule, note)], each
    found in its package's MODS record (court_opinions.granules), its title and date taken from govinfo, read whole
    from its public PDF. A document whose record is not found is said in left_out."""

    def book_fn(_name, work, cache=None, left_out=None, limit=None):
        """The book: one part per document, in the order listed."""
        import court_opinions as C
        import pdf_set
        left_out = left_out if left_out is not None else []
        records, parts, dates = {}, [], []
        for package, granule, note in documents:
            if package not in records:
                records[package] = {g["id"]: g for g in C.granules(C.read_mods(package, cache))}
            g = records[package].get(granule)
            if not g or not g["pdf"]:
                left_out.append({"title": granule, "reason": "govinfo.gov has no record of this document now.",
                                 "url": f"{GOVINFO}/app/details/{package}"})
                continue
            year = package.split("-")[1] if "-" in package else ""
            head = g["title"] + (f" ({g['date'][:10]})" if g["date"] else (f" ({year})" if year else ""))
            parts.append((head + (f". {note}" if note else ""), g["pdf"], g["page"] or g["pdf"]))
            dates.append(g["date"][:10] if g["date"] else year)
            if limit and len(parts) >= limit:
                break
        if not parts:
            return None
        entry = K.us_pdf(group, name=f"{prefix}_{name}", title=title, subject=subject, publisher=publisher,
                         source=f"{GOVINFO}/app/collection/ppp", description=description, notice=notice,
                         version="govinfo.gov")
        book = pdf_set.pdf_set_book(entry, parts, work, cache, left_out, limit)
        if book is not None:
            book.published = max(dates)
            book.version = f"govinfo.gov, read {datetime.date.today().isoformat()}"
        return book

    def sign_fn(_name):
        """The weekly sign: the list of documents (printed papers do not change)."""
        return K.sha(documents)

    return book_fn, sign_fn
