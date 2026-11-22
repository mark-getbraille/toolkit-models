"""The United States Code in full, and what was checked for state codes and municipal codes, for the reference library
(the owner's request of 2026-11-22). Keys: us-code (every title), code:usc:<title> (one title: "1", "26", "05A" for
an appendix).

What this module builds, in plain words: every title of the United States Code (54 titles and their appendices),
one book per title, from the Office of the Law Revision Counsel's current release point (the official per-title
downloads at uscode.house.gov/download.html, "current through Public Law ..." of the release). Each section is one
page with its heading, its full text and its source credit (the laws it comes from), grouped by chapter. The
editorial notes the Law Revision Counsel adds after a section (amendments history, effective dates, cross references)
are left out to keep the books readable; the law's text itself is whole.

The library already had a few chapters of the Code (the ADA, the Rehabilitation Act, IDEA, the Fair Housing Act,
consumer credit, Social Security benefits: sources.LAWS, from govinfo.gov's annual editions); these whole titles are
the current text and include them.

Licence: a work of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page). robots.txt of
uscode.house.gov refuses only Yahoo's "Slurp" reader (checked 2026-11-22). One zip per title is read (about 6 MB for
title 1, 14 MB for title 42), once per release.

State codes and municipal codes: state statutes are not copyrightable (Georgia v. Public.Resource.Org, 2020), but
each site's terms and robots.txt decide whether a program may read them; what was checked is in NOT_INCLUDED, with
the index addresses (link-only for the personal assistant). Municipal codes on American Legal Publishing and
Municode are on copyrighted platforms whose terms forbid copying: link-only.

Run from the repository's folder:
  python3 textbooks/law_codes.py code:usc:1 --out build/textbooks
  python3 textbooks/law_codes.py --list us-code
"""

import html
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "law"
SITE = "https://uscode.house.gov"
DOWNLOAD = f"{SITE}/download.html"
PUBLISHER = "Office of the Law Revision Counsel, US House of Representatives (United States Code)"

# Every title file of the Code, as the download page names them (an appendix has a letter: 05A, 11a, 18a, 28a, 50A).
TITLES = [f"{n:02d}" for n in range(1, 55)] + ["05A", "11a", "18a", "28a", "50A"]
TITLES.remove("53")                      # title 53 is reserved (it has no sections)


def release(cache=None):
    """(release point path "119/142", "Public Law 119-142 (November 10, 2026)") from the download page."""
    import build_textbooks as B
    text = B.fetch(DOWNLOAD, None)
    m = re.search(r"releasepoints/us/pl/(\d+/\d+[a-z]?)/htm_usc01@", text)
    words = re.search(r"current through (Public Law [^<.]+?\))", text)
    if not m:
        raise LookupError("no release point on the download page")
    return m.group(1), words.group(1) if words else ""


def title_url(title, point):
    """The address of one title's HTML zip at a release point."""
    return f"{SITE}/download/releasepoints/us/pl/{point}/htm_usc{title}@{point.replace('/', '-')}.zip"


DOC = re.compile(r"<!-- documentid:")
KEEP = ("head", "statute", "sourcecredit", "footnote")


def section_pages(text):
    """[(title, chapter, body HTML)] of one title's HTML: each document that is a section (it has a section head),
    with only its heading, text, source credit and footnotes; the chapter is from its "expcite" path."""
    out = []
    for doc in DOC.split(text)[1:]:
        if 'class="section-head"' not in doc:
            continue
        expcite = html.unescape((re.search(r"<!-- expcite:(.*?) -->", doc) or [None, ""])[1])
        path = expcite.split("!@!")
        chapter = next((p for p in reversed(path[:-1]) if re.match(r"(CHAPTER|SUBCHAPTER|PART|SUBTITLE)\b", p)),
                       path[1] if len(path) > 1 else path[0])
        chapter = next((p for p in path if p.startswith("CHAPTER")), chapter)
        parts = []
        for field in KEEP:
            parts += re.findall(rf"<!-- field-start:{field} -->(.*?)<!-- field-end:{field} -->", doc, re.S)
        body = "\n".join(parts)
        head = re.search(r'<h3 class="section-head">(.*?)</h3>', body, re.S)
        title = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", head.group(1))).split()) if head else path[-1]
        body = re.sub(r'<h3 class="section-head">.*?</h3>', "", body, count=1, flags=re.S)
        out.append((title.replace("§", "Section "), chapter.title() if chapter.isupper() else chapter, body))
    return out


def title_book(name, work, cache=None, left_out=None, limit=None):
    """One title of the Code (name "usc:26")."""
    import build_textbooks as B
    title = name.split(":", 1)[1] if ":" in name else ""
    if title not in TITLES:
        left_out.append({"title": name, "reason": "Not a title of the United States Code."})
        return None
    if not re.search(K.GOVINFO_TEXT, B.fetch(K.GOVINFO_POLICY, cache)):
        left_out.append({"title": name, "reason": "govinfo.gov's policies page no longer quotes 17 U.S.C. 105."})
        return None
    point, through = release(cache)
    url = title_url(title, point)
    if not K.readable(url, cache):
        left_out.append({"title": name, "reason": "Not allowed by robots.txt."})
        return None
    path = K.download_file(url, cache)
    with zipfile.ZipFile(path) as z:
        text = z.read(z.namelist()[0]).decode("utf-8", "replace")
    name_words = html.unescape((re.search(r"AUTHORITIES-USC-TITLE-NAME:(.*?) -->", text) or [None, f"TITLE {title}"])[1])
    positive = "positive-law" in (re.search(r"AUTHORITIES-USC-TITLE-STATUS:(.*?) -->", text) or [None, ""])[1]
    nice = re.sub(r"^TITLE (\w+) - ", r"Title \1: ", name_words)
    nice = nice[:7] + nice[7:].title() if nice.startswith("Title") else nice
    book = K.new_book(f"code_usc_title_{title.lower()}", f"United States Code, {nice}",
                      "Law (United States Code)", GROUP, PUBLISHER, K.US_GOV, K.US_GOV_URL,
                      f"{SITE}/browse/prelim@title{title.lstrip('0')}",
                      f"The whole of {nice} of the United States Code as the Law Revision Counsel publishes it, "
                      f"{through or 'at its current release point'}: one page per section with its full text and "
                      "source credit, by chapter. " + ("This title is positive law (the title itself was enacted). "
                                                      if positive else "This title is not positive law: it is prima "
                                                      "facie evidence of the law, whose text is in the Statutes at Large. "),
                      "A work of the US government (not under copyright). This is not the official print edition; "
                      "the Law Revision Counsel's notes after each section (amendment history, effective dates, "
                      "cross references) are left out: see uscode.house.gov for them. Not legal advice.",
                      changes="one page per section; the editorial notes left out")
    book.version = f"Release point {point.replace('/', '-')}" + (f", current through {through}" if through else "")
    m = re.search(r"AUTHORITIES-LAWS-ENACTED-THROUGH:\S+ \((\d\d)/(\d\d)/(\d{4})\)", text)
    book.published = f"{m.group(3)}-{m.group(1)}-{m.group(2)}" if m else ""
    book.originals.append({"url": url, "kind": "zip"})
    paths = set()
    for sec_title, chapter, body in section_pages(text):
        if limit and len(book.pages) >= limit:
            break
        p = B.slug(sec_title[:60], 60)
        while p in paths or p in ("index", "style-css"):
            p += "-2"
        paths.add(p)
        book.pages.append(B.Page(p, sec_title, B._Cleaner({}, url).clean(body), 0, chapter))
    return book


def title_sign(name):
    """A title's sign: its zip's size and date at the current release point (a changed title changes them)."""
    import updates
    point, _through = release()
    return K.sha(updates.head_signs(title_url(name.split(":", 1)[1], point)))


COLLECTION = K.Collection("code", GROUP, makers={"usc": (title_book, title_sign)},
                          pieces={"usc": lambda: list(TITLES)},
                          words={"us-code": lambda: [f"code:usc:{t}" for t in TITLES]})

GROUPS = {}
LICENCE_LINES = {
    "us_code_olrc": "uscode.house.gov (Office of the Law Revision Counsel): works of the US government (17 U.S.C. "
                    "105, the line checked on govinfo.gov/about/policies at every build). robots.txt refuses only "
                    "\"User-agent: Slurp\" (checked 2026-11-22). The per-title HTML zips of the current release point "
                    "are read from uscode.house.gov/download.html.",
}
NOT_INCLUDED = [
    ("Texas Constitution and Statutes", "statutes.capitol.texas.gov is now a JavaScript application without a "
     "readable download page for programs (checked 2026-11-22). Link-only. Index: https://statutes.capitol.texas.gov/"),
    ("Other state codes (for example Oregon, Virginia, Utah, Ohio, Minnesota, North Carolina, Iowa, Massachusetts)",
     "Their robots.txt files allow programs (checked 2026-11-22), but each site's terms, and whether it claims "
     "copyright in its compilation, were not checked one by one in this pass; Idaho's and Alaska's robots.txt shut "
     "out AI readers. State statutes are not copyrightable (Georgia v. Public.Resource.Org, 2020); add a state only "
     "after reading its terms. Link-only for now. Index: https://www.ncsl.org/about-state-legislatures/"
     "state-legislative-websites-directory"),
    ("Public.Resource.Org bulk state codes (law.resource.org)", "Its robots.txt shuts out ClaudeBot, GPTBot, CCBot "
     "and other AI readers. Index: https://law.resource.org/pub/us/code/"),
    ("Open States bill text (openstates.org)", "Its API needs a sign-up key, and no key is in the owner's settings "
     "or the repository's secrets. Index: https://open.pluralpolicy.com/data/"),
    ("Municipal codes on American Legal Publishing (codelibrary.amlegal.com) and Municode (library.municode.com)",
     "Copyrighted platforms whose terms forbid copying their code pages. Link-only for the personal assistant. "
     "Index: https://codelibrary.amlegal.com/ and https://library.municode.com/"),
    ("Washington, New York, California and Florida statutes", "Said already (sources.REFERENCE_NOT_INCLUDED): "
     "app.leg.wa.gov disallows everything, New York's Open Legislation needs a key, California refuses programs, "
     "Florida claims copyright in its compilation. Index: https://app.leg.wa.gov/rcw/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
