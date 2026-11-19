"""Weekly update checks and kept versions for the textbooks release (the workflow's weekly schedule).

Two jobs, in plain words:

1. Has a source changed? fingerprint(key) asks each source cheaply for a sign of change: the newest commit of an
   OpenStax or Office of the Historian repository (git ls-remote), a DSpace record's "lastModified", the address and
   size of an official PDF (the Internet Archive's file checksum; a web server's ETag, Last-Modified and size), the
   newest govinfo edition of a law, the list of articles of a web guide or the newest "lastmod" of its sitemap, the
   newest report of a CRS year, and so on. Every book's catalogue entry keeps the key it was built from and the
   fingerprint at that time; changed_keys() compares them with today's and lists the keys to build again. News
   pieces (the daily refresh) and the VOA years (the backfill) are left to their own schedules; books whose entry has
   no fingerprint yet (built before this check existed) are rebuilt a few at a time, oldest first.

2. Keep every version. A book built again is written under a new file name (<name>.<YYYY-MM-DD>.zim, the day it was
   built) and the old file stays in the release. merge_versions() keeps, for every book in textbooks.json, a list
   "versions" ([{file, url, size, sha256, content_sha256, published, built, change_note}], newest first) with the
   newest also in the book's own fields, so the toolkit's present code goes on working. A rebuild whose text is the
   same as the newest version's (content_sha256: the pages, not the file, whose date and id always differ) adds no
   version. A GitHub release holds at most 1,000 files ("Up to 1000 release assets may be associated with a single
   release", GitHub's documentation); the periodicals have one release per source (periodicals.release_for), and
   archive_plan() moves the oldest kept versions of a release into yearly archive releases ("textbooks-archive-2026")
   when it passes ARCHIVE_AT files, and points their entries there.

Command line (used by .github/workflows/textbooks.yml):
  python textbooks/updates.py --changed textbooks.json [--limit 40]     the keys to build again, one per line
  python textbooks/updates.py --archive-plan textbooks.json --assets '{"textbooks": 950}'   the files to move
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
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import sources  # noqa: E402

ARCHIVE_AT = 900                 # move old versions out of the main release when it holds more files than this
ARCHIVE_TO = 800                 # ... until it holds this many
REBUILD_UNKNOWN = 25             # books without a fingerprint rebuilt per weekly run (oldest first)


# ====================================================================== fingerprints

def _sha(*parts):
    """A short checksum of some strings."""
    return hashlib.sha256("\n".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:24]


def git_head(url):
    """The newest commit of a public git repository ("" when it cannot be asked)."""
    try:
        out = subprocess.run(["git", "ls-remote", url, "HEAD"], capture_output=True, text=True, timeout=120)
        return out.stdout.split()[0] if out.stdout.strip() else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def head_signs(url):
    """A web file's ETag, Last-Modified and size, as one string ("" when the server says none of them)."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": B.USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as r:
            h = r.headers
            return "|".join(h.get(k) or "" for k in ("ETag", "Last-Modified", "Content-Length")).strip("|")
    except (urllib.error.URLError, OSError, ValueError):
        return ""


def page_words(url):
    """The words of a web page (scripts, styles and tags removed), read fresh."""
    text = B.fetch(url, None)
    text = re.sub(r"(?s)<(script|style|noscript)[^>]*>.*?</\1>", " ", text)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def guide_sign(entry):
    """A web guide's sign of change: the newest "lastmod" of its sitemap's pages, or the list of articles its
    contents pages link to (an added, removed or renamed article changes it) with their servers' dates."""
    if entry.get("sitemap"):
        found = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>\s*(?:<lastmod>\s*([^<\s]+))?", B.fetch(entry["sitemap"], None))
        pages = re.compile(entry["pages"])
        return _sha(sorted((u, d) for u, d in found if pages.match(html.unescape(u))))
    links = []
    for start in entry.get("start", []):
        links += [u for u in B.page_links(B.fetch(start, None), start) if re.match(entry["pages"], u)]
        links.append(head_signs(start))
    return _sha(*links)


def pdf_sign(entry):
    """An official PDF's sign of change: the Internet Archive's checksum of the item's PDF, or the address of the
    newest PDF on its page with the server's ETag, Last-Modified and size."""
    if entry.get("archive"):
        meta = json.loads(B.fetch(f"https://archive.org/metadata/{entry['archive']}", None))
        return _sha(*sorted(f.get("md5", "") for f in meta.get("files", []) if f.get("name", "").endswith(".pdf")))
    url = entry.get("pdf") or B.newest_pdf(B.fetch(entry["page"], None), entry["page"],
                                           entry.get("pdf_pattern", r"\.pdf$"))
    return _sha(url, head_signs(url))


def law_sign(entry):
    """A law's sign of change: the address of govinfo's newest edition of each part (its year is in it), or the
    words of its official pages."""
    parts = []
    cfr = entry.get("cfr") or []
    for spec in (cfr if isinstance(cfr, list) else [cfr]):
        parts.append(B.govinfo_edition("cfr", spec, None)[0])
    for spec in entry.get("usc", []):
        parts.append(B.govinfo_edition("usc", spec, None)[0])
    for url in entry.get("urls", []):
        parts.append(_sha(page_words(url)))
    return _sha(*parts)


def pub_sign(key):
    """A periodical piece's sign of change (periodicals.py): the repository's newest commit for the Office of the
    Historian, the CRS list's rows of that year, the sitemap's newest date for Amber Waves, the newest article of a
    Europe PMC search; "" (never rebuilt by the weekly check) for news, VOA and the historic newspapers."""
    import periodicals as P
    _pub, name, piece = key.split(":", 2)
    spec = P.SOURCES[name]
    driver = spec["driver"]
    if spec.get("daily") or driver in ("voa", "voa_history", "chronam"):
        return ""
    if driver in ("milestones", "frus"):
        return git_head(spec["repo"])
    if driver == "crs":
        rows = [r for r in B.fetch(P.CRS_SITE + "reports.csv", None).splitlines() if f",{piece}-" in r]
        return _sha(*sorted(rows))
    if driver == "amber_waves":
        found = []
        for page in range(1, 30):
            try:
                text = B.fetch(f"{P.ERS_SITE}/sitemap.xml?page={page}", None)
            except urllib.error.HTTPError:
                break
            locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>\s*(?:<lastmod>\s*([^<\s]+))?", text)
            if not locs:
                break
            found += [(u, d) for u, d in locs if "/amber-waves/" in u and f"/{piece[:3]}" in u]
        return _sha(*sorted(found))
    if driver in ("europepmc", "elife"):
        return datetime.date.today().strftime("%Y-%m")          # a monthly refresh is enough for these lists
    return ""


def fingerprint(key):
    """Today's sign of change of a build key ("" when the key is not checked weekly, or the source could not be
    asked: then nothing is rebuilt)."""
    try:
        if key.startswith("osbooks:"):
            return git_head(f"https://github.com/openstax/osbooks-{key[8:]}")
        if key == "siyavula":
            return _sha(*[_sha(*B.page_links(B.fetch(f"{B.SIYAVULA_SITE}/read/za/{s}/grade-{g}", None), ""))
                          for s, g, _t, _w in sources.SIYAVULA])
        if key == "dspace":
            return _sha(*[B.dspace_record(site, handle, None).get("lastModified", "")
                          for site, handle, *_rest in sources.DSPACE])
        kind, _, name = key.partition(":")
        if kind == "pdf":
            return pdf_sign(next(e for e in sources.PDF_DOCS if e["name"] == name))
        if kind in ("nonprofit", "guide"):
            return guide_sign(next(e for e in sources.NONPROFIT + sources.GOV_GUIDES if e["name"] == name))
        if kind == "law":
            return law_sign(next(e for e in sources.LAWS + sources.LAWS_MORE if e["name"] == name))
        if kind == "pub":
            return pub_sign(key)
    except (urllib.error.URLError, OSError, ValueError, LookupError, StopIteration, KeyError):
        return ""
    return ""


def changed_keys(catalogue, limit=40, sign=None):
    """The build keys whose source changed since their books were built (their entry's "fingerprint" differs from
    today's), then up to REBUILD_UNKNOWN keys of books without a fingerprint (oldest built first); at most limit.
    sign: the fingerprint function (for tests)."""
    sign = sign or fingerprint
    changed, unknown, seen = [], [], set()
    for b in sorted((catalogue or {}).get("books", []), key=lambda b: b.get("date", "")):
        key = b.get("key")
        if not key or key in seen:
            continue
        seen.add(key)
        if not b.get("fingerprint"):
            unknown.append(key)
            continue
        now = sign(key)
        if now and now != b["fingerprint"]:
            changed.append(key)
    return (changed + unknown[:REBUILD_UNKNOWN])[:limit]


# ====================================================================== kept versions

def version_of(entry, note=""):
    """The version record of a catalogue entry."""
    return {"file": entry["file"], "url": entry["url"], "size": entry["size"], "sha256": entry["sha256"],
            "content_sha256": entry.get("content_sha256", ""), "published": entry.get("published", ""),
            "built": entry.get("date", ""), "change_note": note}


def merge_versions(old, new):
    """The catalogue entry of a book after a build: the new entry's fields, with "versions" holding every version
    kept (newest first). Nothing is added when the new text is the same as the newest kept version's (then the old
    entry stays as it was); a file rebuilt under the same name (news pieces, VOA years) replaces its version."""
    if old is None:
        return dict(new, versions=[version_of(new, "First version")])
    versions = list(old.get("versions") or [version_of(old)])
    newest = versions[0]
    same_text = new.get("content_sha256") and new.get("content_sha256") == newest.get("content_sha256")
    if same_text and new["file"] != newest["file"]:
        return old                                       # nothing changed in the text: keep the old version
    note = "Rebuilt: the source changed" + (f" (published {new['published']})" if new.get("published") else "")
    versions = [v for v in versions if v["file"] != new["file"]]
    versions.insert(0, version_of(new, note if versions else "First version"))
    versions.sort(key=lambda v: (v.get("built", ""), v["file"]), reverse=True)
    main = new if versions[0]["file"] == new["file"] else old     # an older manifest never replaces the newest
    return dict(main, versions=versions)


def archive_plan(catalogue, counts, at=ARCHIVE_AT, to=ARCHIVE_TO):
    """(moves, catalogue) for the releases that hold too many files: counts is {release: files it holds now}; for
    each release past `at` files, the oldest kept versions in it (never a book's newest) move to the yearly archive
    release "<release>-archive-<year>" until it holds `to`; each move is {file, from, to}; the catalogue's version
    addresses point to the archive. ([], catalogue) when nothing needs to move."""
    base = B.RELEASE.rsplit("/", 1)[0]
    moves = []
    for release, assets in sorted(counts.items()):
        if assets <= at:
            continue
        old = []
        for b in catalogue.get("books", []):
            for v in (b.get("versions") or [])[1:]:
                if v.get("url", "").startswith(f"{base}/{release}/"):
                    old.append((v.get("built", ""), v["file"], v))
        old.sort(key=lambda x: (x[0], x[1]))
        for built, file, v in old[:max(0, assets - to)]:
            tag = f"{release}-archive-{(built or '0000')[:4]}"
            v["url"] = f"{base}/{tag}/{file}"
            moves.append({"file": file, "from": release, "to": tag})
    return moves, catalogue


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--changed", default=None, metavar="TEXTBOOKS_JSON")
    p.add_argument("--limit", type=int, default=40)
    p.add_argument("--archive-plan", default=None, metavar="TEXTBOOKS_JSON")
    p.add_argument("--assets", default="{}", help='JSON {release: how many files it holds now}')
    a = p.parse_args(argv)
    path = a.changed or a.archive_plan
    catalogue = {}
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            catalogue = json.load(f)
    if a.changed is not None:
        print("\n".join(changed_keys(catalogue, a.limit)))
    elif a.archive_plan is not None:
        moves, catalogue = archive_plan(catalogue, json.loads(a.assets))
        with open(a.archive_plan, "w", encoding="utf-8") as f:
            json.dump(catalogue, f, indent=1, ensure_ascii=False)
        print(json.dumps(moves))
    return 0


if __name__ == "__main__":
    sys.exit(main())
