"""Make textbooks/catalogues/otl.json: a snapshot of the Open Textbook Library's catalogue (open.umn.edu), for
textbooks/open_catalogues.py (keys cat:otl:<piece>).

Why a snapshot: the Open Textbook Library's robots.txt asks for two minutes between requests (Crawl-delay: 120) and
its JSON catalogue has about 205 pages, so reading it takes about seven hours: too long for each build job. This
script reads it once, page by page, 121 seconds apart, keeps each page in a folder so that a stopped run picks up
where it stopped, and writes only the fields the builder needs. Run it again a few times a year and commit the new
file; the weekly check then rebuilds the books whose entries changed.

Usage (from the repository's folder):
    python3 tools/snapshot_otl.py --pages build/otl-pages            (reads what is missing, then writes the file)
    python3 tools/snapshot_otl.py --pages build/otl-pages --no-fetch (only writes the file from the saved pages)
"""

import argparse
import datetime
import glob
import json
import os
import sys
import time
import urllib.request

API = "https://open.umn.edu/opentextbooks/textbooks.json?page={}"
PAUSE = 121                      # seconds between two requests (robots.txt: Crawl-delay: 120)
USER_AGENT = "DigitalAccessibilityToolkit-textbooks/1.0 (open textbooks for blind readers; " \
             "github.com/mark-getbraille/toolkit-models)"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "textbooks", "catalogues",
                   "otl.json")


def fetch_pages(folder):
    """Read every catalogue page not yet saved in folder, PAUSE seconds apart."""
    os.makedirs(folder, exist_ok=True)
    page = 1
    while True:
        path = os.path.join(folder, f"page-{page:04d}.json")
        if not os.path.exists(path):
            req = urllib.request.Request(API.format(page), headers={"User-Agent": USER_AGENT,
                                                                    "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            with open(path, "wb") as f:
                f.write(data)
            print(f"page {page}", flush=True)
            time.sleep(PAUSE)
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if page >= d["links"]["total_pages"] or not d["data"]:
            return
        page += 1


def trimmed(book):
    """The fields of one catalogue record the builder uses (the reviews and other fields are left out)."""
    return {"id": book["id"], "title": book.get("title") or "", "license": book.get("license") or "",
            "copyright_year": book.get("copyright_year"), "language": book.get("language") or "",
            "description": (book.get("description") or "")[:700],
            "contributors": [{"name": " ".join(filter(None, [c.get("first_name"), c.get("middle_name"),
                                                             c.get("last_name")])) or c.get("name", "")}
                             for c in book.get("contributors") or []][:6],
            "subjects": [{"name": s.get("name", "")} for s in book.get("subjects") or []],
            "publishers": [{"name": p.get("name", "")} for p in book.get("publishers") or []],
            "formats": [{"type": f.get("type", ""), "url": f.get("url", "")} for f in book.get("formats") or []]}


def write_snapshot(folder, out=OUT):
    """Write the trimmed catalogue of the saved pages to out; returns the number of books."""
    books = []
    for path in sorted(glob.glob(os.path.join(folder, "page-*.json"))):
        with open(path, encoding="utf-8") as f:
            books += [trimmed(b) for b in json.load(f)["data"]]
    books = list({b["id"]: b for b in books}.values())
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"source": "https://open.umn.edu/opentextbooks/textbooks.json", "read": datetime.date.today()
                   .isoformat(), "count": len(books), "books": books}, f, ensure_ascii=False, indent=0)
    return len(books)


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--pages", required=True, help="folder for the saved catalogue pages")
    p.add_argument("--no-fetch", action="store_true", help="only write the file from the saved pages")
    a = p.parse_args(argv)
    if not a.no_fetch:
        fetch_pages(a.pages)
    print(f"{write_snapshot(a.pages)} books written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
