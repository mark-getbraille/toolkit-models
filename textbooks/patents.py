"""Patents for the reference library: "how things work" in the inventors' own words (the owner's request of
2026-11-22). Keys: pat:<name>. Request word: patents. Group: "Reference, patents".

What this module builds, in plain words:
  - pat:famous_us_patents: famous historical US patents (the Wright brothers' flying machine, Bose's wireless
    detector, typewriters, locomotives and others), each the patent's own text as transcribed on Wikisource, with
    its number, inventor, date, its description ("specification") and its claims. The patents themselves are public
    domain (US patents are not under copyright); the Wikisource pages are under CC BY-SA 4.0, so this book is
    share-alike and kept apart. The list is the members of Wikisource's "United States patents" category, read at
    every build;
  - pat:assistive_technology: patents for assistive technology: braille displays and braille writers, reading
    machines and other aids for blind and deaf people (CPC class G09B21), canes and walking aids for blind people
    (A61H3/061) and devices that replace sight with another sense (A61F9/08);
  - pat:household_inventions: patents for household machines: coffee makers and other drink makers (A47J31),
    dishwashers and vacuum cleaners (A47L), washing machines (D06F) and refrigerators (F25D).
    These two are SIGN-UP entries: they are read from the USPTO's Open Data Portal (api.uspto.gov), the USPTO's own
    channel for programs, which needs the owner's own free API key (made at data.uspto.gov, "API key management";
    the USPTO asks for an identity check) in the environment variable USPTO_ODP_API_KEY (a workflow secret or his
    own computer's setting; never in the repository; the key is sent only to api.uspto.gov). Without it the build
    says where to sign up. Each patent is one page: its title, number, inventors, grant date, abstract, claims and
    description, from the patent's full-text XML. A patent with a copyright or mask-work notice (37 CFR 1.71(d)
    and (e)) is left out. The USPTO says "the text and drawings of a patent are typically not subject to copyright
    restrictions" (its terms of use);
  - pat:index: a guide to patents and how-things-work books in the library (CC0).

Not built (NOT_INCLUDED): Google Patents (its terms forbid scraping), the USPTO's Patent Public Search (not meant
for bulk use), the full-text bulk files (gigabytes a week: the Writing Kit downloads them on the owner's computer)
and the scanned images of patents before 1976 (no text layer).

Run from the repository's folder:
  python3 textbooks/patents.py pat:famous_us_patents --out build/textbooks --limit 5
  python3 textbooks/patents.py --list patents
"""

import datetime
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "patents"
GROUPS = {GROUP: "Reference, patents"}

# ====================================================================== famous historical patents (Wikisource)

WIKISOURCE = "https://en.wikisource.org/wiki"
CATEGORY = f"{WIKISOURCE}/Category:United_States_patents"
CC_BY_SA = "CC BY-SA 4.0"
CC_BY_SA_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
GUIDES = [
    dict(group=GROUP, country="United States", licence=CC_BY_SA, licence_url=CC_BY_SA_URL,
         publisher="The inventors (United States Patent Office), transcribed by Wikisource contributors "
                   "(en.wikisource.org)", name="famous_us_patents",
         title="Famous historical US patents in the inventors' own words (Wikisource)",
         subject="Patents: how things work", source=CATEGORY,
         description="Famous historical United States patents, each the patent's own text: its number, the "
                     "inventor, the date, the specification (how the invention is made and works, referring to its "
                     "drawings) and the claims. Among them: the Wright brothers' flying machine (821,393, 1906), "
                     "Jagadish Chandra Bose's wireless detector (755,840), locomotives, typewriters and other "
                     "machines. The drawings are not included; where a page shows them, only their captions are "
                     "kept. The list is Wikisource's category of United States patents, read at every build.",
         notice="The patents themselves are public domain (US patents are not under copyright; the USPTO's terms). "
                "The transcriptions are from Wikisource (en.wikisource.org), written by its contributors, CC BY-SA "
                "4.0 (share-alike: anything made from it keeps the same licence); each page's history lists its "
                "authors. Old patents use the words and units of their day.",
         licence_page=f"{WIKISOURCE}/Wikisource:Copyright_policy",
         licence_text=r"Creative Commons Attribution-ShareAlike", page_mark=r"Creative Commons Attribution-ShareAlike",
         sitemap="", unit_rules=[], level="reference", start=[], units="", crawl=[(CATEGORY, 1)],
         pages=r"^https://en\.wikisource\.org/wiki/(?:United_States_patent_|US_Patent_)[^/:?#]+$",
         content=(r'<div id="mw-content-text"[^>]*>', r'<div class="printfooter"'),
         drop=[r'<span class="mw-editsection">.*?</span>\s*</span>', r'<div class="(?:navbox|noprint)[^"]*".*?</div>',
               r'<table class="[^"]*(?:ambox|metadata|navbox)[^"]*".*?</table>', r'<div class="ws-noexport.*?</div>'],
         limit=120, changes="each patent's Wikisource page made into a web page, with the site's menus, headers, "
                            "edit links and page-scan markers left out"),
]

# ====================================================================== patents from the USPTO Open Data Portal

USPTO_KEY_ENV = "USPTO_ODP_API_KEY"
ODP = "https://api.uspto.gov/api/v1/"
ODP_SIGNUP = "https://data.uspto.gov/apis/getting-started"
PATENT_TERMS = "https://www.uspto.gov/terms-use-uspto-websites"
PATENT_LICENCE = "Public domain (US patent text)"
# The licence of the patents' text, added to the toolkit's allowed licences (more_refs.allowed).
ALLOWED = {PATENT_LICENCE: "open"}
PATENT_NOTICE = ("The text of a US patent, from the USPTO's Open Data Portal. The USPTO's terms: \"Subject to limited "
                 "exceptions reflected in 37 CFR 1.71(d) & (e) and 1.84(s), the text and drawings of a patent are "
                 "typically not subject to copyright restrictions\"; any patent with a copyright or mask-work notice "
                 "is left out. A patent describes an invention as its inventors claimed it; it does not say the "
                 "product was made, works as described or is safe. The drawings are not included.")
COPYRIGHT_NOTICE = re.compile(r"(?i)(copyright|mask work|©|\(c\)\s*\d{4})")
PAUSE = 1.0                                   # seconds between calls to the Open Data Portal
MOST = 200                                    # patents in one book at most
XML_MOST = 20_000_000                         # bytes: a bigger "full text" is a weekly bulk file, not one patent

# Each book: (title, subject, description, [(CPC search, class prefixes the patent must carry, how many)]).
ODP_BOOKS = {
    "assistive_technology": (
        "Patents for assistive technology: braille, reading machines, canes and aids for blind and deaf people",
        "Patents: assistive technology",
        "US patents granted for assistive technology, newest first: braille displays, braille writers and embossers, "
        "reading machines and other aids for blind, deaf and deafblind people (CPC class G09B21), canes and walking "
        "aids for blind people (A61H3/061) and devices that turn what a camera sees into sound or touch (A61F9/08). "
        "Each page gives the patent's title, number, inventors and grant date, then its abstract, its claims and its "
        "description, in the inventors' own words.",
        [(r"G09B21*", ("G09B21",), 110), (r"A61H3\/061*", ("A61H3/061",), 45), (r"A61F9\/08*", ("A61F9/08",), 45)]),
    "household_inventions": (
        "Patents for household machines: coffee makers, dishwashers, vacuum cleaners, washing machines and "
        "refrigerators", "Patents: household machines",
        "US patents granted for household machines, newest first: coffee makers and other drink makers (CPC class "
        "A47J31), dishwashers and vacuum cleaners and other cleaning machines (A47L), washing machines and dryers "
        "(D06F) and refrigerators and freezers (F25D). Each page gives the patent's title, number, inventors and "
        "grant date, then its abstract, its claims and its description, in the inventors' own words.",
        [(r"A47J31*", ("A47J31",), 50), (r"A47L*", ("A47L",), 50), (r"D06F*", ("D06F",), 50),
         (r"F25D*", ("F25D",), 50)]),
}


def xml_text(fragment):
    """The plain words of an XML fragment (tags dropped, entities read, spaces tidied)."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment or "")).split())


def patent_parts(xml):
    """{number, date, title, inventors, abstract, claims: [text], description: [(heading or "", paragraph)]} of one
    US patent's full-text XML (us-patent-grant, version 4)."""
    xml = xml or ""
    pub = re.search(r"<publication-reference\b.*?<doc-number>(.*?)</doc-number>.*?<date>(\d{8})</date>", xml, re.S)
    title = re.search(r"<invention-title\b[^>]*>(.*?)</invention-title>", xml, re.S)
    abstract = re.search(r"<abstract\b[^>]*>(.*?)</abstract>", xml, re.S)
    names = []
    for who in re.findall(r"<(inventor|us-applicant|applicant)\b[^>]*>(.*?)</\1>", xml, re.S):
        first = xml_text("".join(re.findall(r"<first-name>(.*?)</first-name>", who[1], re.S)))
        last = xml_text("".join(re.findall(r"<last-name>(.*?)</last-name>", who[1], re.S)))
        name = f"{first} {last}".strip()
        if last and name not in names and who[0] == "inventor":
            names.append(name)
    claims = [xml_text(c) for c in re.findall(r"<claim\b[^>]*>(.*?)</claim>", xml, re.S)]
    description = []
    m = re.search(r"<description\b[^>]*>(.*?)</description>", xml, re.S)
    for kind, body in re.findall(r"<(heading|p)\b[^>]*>(.*?)</\1>", m.group(1) if m else "", re.S):
        words = xml_text(body)
        if words:
            description.append((kind, words))
    date = pub.group(2) if pub else ""
    return {"number": pub.group(1).lstrip("0D") if pub else "", "date": f"{date[:4]}-{date[4:6]}-{date[6:]}" if date
            else "", "title": xml_text(title.group(1)) if title else "", "inventors": names,
            "abstract": xml_text(abstract.group(1)) if abstract else "", "claims": [c for c in claims if c],
            "description": description}


def patent_page_html(p):
    """The HTML of one patent's page: its facts, abstract, claims and description."""
    import build_textbooks as B
    facts = K.dl([("Patent number", f"US {int(p['number']):,}" if p["number"].isdigit() else p["number"]),
                  ("Inventors", ", ".join(p["inventors"])), ("Granted", p["date"])])
    out = [facts]
    if p["abstract"]:
        out.append(f"<h2>Abstract</h2><p>{B.esc(p['abstract'])}</p>")
    if p["claims"]:
        items = [re.sub(r"^\d+\s*\.\s*", "", c) for c in p["claims"]]   # the claim's own number is the list's
        out.append("<h2>Claims</h2><ol>" + "".join(f"<li>{B.esc(c)}</li>" for c in items) + "</ol>")
    if p["description"]:
        out.append("<h2>Description</h2>")
        for kind, words in p["description"]:
            out.append(f"<h3>{B.esc(words)}</h3>" if kind == "heading" else f"<p>{B.esc(words)}</p>")
    return "".join(out)


def odp_call(key, url, body=None):
    """One call to the Open Data Portal with the key (sent only to api.uspto.gov), pausing politely; (status, bytes).
    A POST when body (a dict) is given."""
    import build_textbooks as B
    if not url.startswith(ODP):
        raise ValueError(f"not an Open Data Portal address: {url}")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Accept": "*/*", "User-Agent": B.USER_AGENT}
    if data is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(4):
        time.sleep(PAUSE)
        try:
            # keyed_urlopen: the key goes only to api.uspto.gov, also when the portal answers "moved".
            with B.keyed_urlopen(url, {"X-API-KEY": key}, data=data, headers=headers, timeout=120) as r:
                return r.status, r.read(XML_MOST + 1)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            return e.code, b""
        except (urllib.error.URLError, OSError):
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    return 0, b""


def odp_search(key, query, prefixes, offset=0, limit=100):
    """One page of granted utility patents whose CPC classes match query: [(patent number, title, grant date, full
    text address)], newest grants first; None when the key is refused."""
    body = {"q": f"applicationMetaData.cpcClassificationBag:{query}",
            "filters": [{"name": "applicationMetaData.applicationTypeLabelName", "value": ["Utility"]}],
            "sort": [{"field": "applicationMetaData.grantDate", "order": "desc"}],
            "pagination": {"offset": offset, "limit": limit}}
    status, data = odp_call(key, ODP + "patent/applications/search", body)
    if status in (401, 403):
        return None
    try:
        found = json.loads(data.decode("utf-8")) if status == 200 else {}
    except ValueError:
        found = {}
    rows = []
    for x in found.get("patentFileWrapperDataBag") or []:
        md = x.get("applicationMetaData") or {}
        number = str(md.get("patentNumber") or "").strip()
        codes = [re.sub(r"\s+", "", str(c)).upper() for c in md.get("cpcClassificationBag") or []]
        url = str((x.get("grantDocumentMetaData") or {}).get("fileLocationURI") or "")
        if number and url and any(c.startswith(p.upper()) for c in codes for p in prefixes):
            rows.append((number, str(md.get("inventionTitle") or ""), str(md.get("grantDate") or ""), url))
    return rows


def grant_xml(key, url):
    """The full-text XML of one granted patent ("" when it cannot be read, or is a bulk file of many patents)."""
    status, data = odp_call(key, url)
    if status != 200 or len(data) > XML_MOST:
        return ""
    if data[:2] == b"PK":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                names = [n for n in z.namelist() if n.lower().endswith(".xml")]
                data = z.read(names[0]) if names else b""
        except zipfile.BadZipFile:
            return ""
    text = data.decode("utf-8", "replace")
    return text if text.count("<us-patent-grant") == 1 else ""


def odp_maker(book_name):
    """(book function, sign function) of one Open Data Portal book (a sign-up entry)."""
    title, subject, description, families = ODP_BOOKS[book_name]

    def book_fn(name, work, cache=None, left_out=None, limit=None):
        """The book: up to MOST patents, newest grants first, shared among the classes searched."""
        import build_textbooks as B
        left_out = left_out if left_out is not None else []
        key = os.environ.get(USPTO_KEY_ENV, "").strip()
        if not key:
            left_out.append({"title": title, "reason": f"A sign-up entry: it needs the owner's own free USPTO Open "
                             f"Data Portal API key (sign up at {ODP_SIGNUP}, then set {USPTO_KEY_ENV} in the build's "
                             "settings, never in the repository).", "url": ODP_SIGNUP, "fetch_yourself": True})
            return None
        book = K.new_book(f"pat_{book_name}", title, subject, GROUP, "United States Patent and Trademark Office "
                          "(the inventors' own words)", PATENT_LICENCE, PATENT_TERMS, "https://data.uspto.gov/",
                          description, PATENT_NOTICE,
                          changes="each patent's full-text XML made into one web page (drawings left out)")
        seen, chapter = set(), 0
        for query, prefixes, most in families:
            got, offset = 0, 0
            while got < most and offset < 1000 and not (limit and len(book.pages) >= limit):
                rows = odp_search(key, query, prefixes, offset)
                if rows is None:
                    left_out.append({"title": title, "reason": f"The Open Data Portal refused the key in "
                                     f"{USPTO_KEY_ENV}; check it at data.uspto.gov (API key management)."})
                    return None
                if not rows:
                    break
                offset += 100
                for number, short, _date, url in rows:
                    if got >= most or number in seen or (limit and len(book.pages) >= limit):
                        continue
                    seen.add(number)
                    xml = grant_xml(key, url)
                    if not xml:
                        left_out.append({"title": f"US {number}: {short}", "reason": "Its full text could not be "
                                         "read."})
                        continue
                    if COPYRIGHT_NOTICE.search(xml_text(xml)):
                        left_out.append({"title": f"US {number}: {short}", "reason": "The patent carries a "
                                         "copyright or mask-work notice (37 CFR 1.71(d)/(e)), so it is not free to "
                                         "use."})
                        continue
                    p = patent_parts(xml)
                    chapter += 1
                    got += 1
                    head = f"US {p['number'] or number}: {(p['title'] or short).capitalize()}"
                    book.pages.append(B.Page(f"us-{number}", head, patent_page_html(p), chapter, query.split("*")[0]
                                             .replace("\\", "")))
                    book.originals.append({"url": url, "kind": "xml", "title": head})
        book.published = ""
        book.version = f"USPTO Open Data Portal, read {datetime.date.today().isoformat()}"
        return book if book.pages else None

    def sign_fn(name):
        """The weekly sign: the week (new patents are granted every Tuesday)."""
        return K.sha(book_name, datetime.date.today().isocalendar()[:2])

    return book_fn, sign_fn


# ====================================================================== the index

SECTIONS = [
    ("Patents: how things work", "Inventions described by their inventors.", [
        ("key", "pat:famous_us_patents", "Famous historical US patents (Wikisource, share-alike)"),
        ("key", "pat:assistive_technology", "Assistive technology patents: braille, reading machines, canes "
                                            "(sign-up entry: the owner's USPTO key)"),
        ("key", "pat:household_inventions", "Household machine patents (sign-up entry: the owner's USPTO key)"),
        ("link", "USPTO Patent Public Search (every US patent, with drawings)", "https://ppubs.uspto.gov/pubwebapp/",
         "the USPTO's search for people; not meant for bulk downloads, so open it in a browser")]),
    ("Books on how things work", "Old and new books that explain machines, tools and electronics.", [
        ("word", "electronics", "Electronics repair and assistive-technology care"),
        ("word", "building", "Light construction"),
        ("link", "Google Patents", "https://patents.google.com/", "Google's terms forbid scraping; open it in a "
                                                                   "browser")]),
]
INDEX = X.index_maker("pat", GROUP, "Patents: a guide to the library", "Patents",
                      "A guide to patents and how-things-work books in the library.", SECTIONS)

MAKERS = {"index": INDEX}
MAKERS.update({n: odp_maker(n) for n in ODP_BOOKS})

COLLECTION = K.Collection("pat", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"patents": lambda: ["pat:index", "pat:famous_us_patents"] +
                                 [f"pat:{n}" for n in ODP_BOOKS]})

LICENCE_LINES = {
    "patents_wikisource": "en.wikisource.org: the patents are public domain; the transcriptions are under CC BY-SA "
                          "4.0 (Wikisource:Copyright_policy, the licence line checked at every build), share-alike; "
                          "robots.txt allows /wiki/ pages, no AI rules (checked 2026-11-22).",
    "patents_uspto": "api.uspto.gov (USPTO Open Data Portal): the USPTO's terms (www.uspto.gov/terms-use-uspto-"
                     "websites) say the text and drawings of a patent are typically not subject to copyright, except "
                     "a copyright or mask-work notice (37 CFR 1.71(d)/(e)), and such patents are left out; needs the "
                     "owner's own key (USPTO_ODP_API_KEY), a sign-up entry (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("Google Patents (patents.google.com)", "Its robots.txt allows only single patent pages and Google's terms forbid "
     "scraping content that is not the user's own; no permission for programs. Link-only. Index: "
     "https://patents.google.com/"),
    ("USPTO Patent Public Search (ppubs.uspto.gov) and the scanned patents before 1976", "The USPTO's terms say its "
     "search systems are not meant for bulk downloads; patents before 1976 are page images without a text layer, so "
     "the builder cannot read them (famous old patents come from Wikisource's transcriptions instead). Link-only. "
     "Index: https://ppubs.uspto.gov/pubwebapp/"),
    ("USPTO full-text bulk files (Patent Grant Full Text, 1976 to the present, weekly XML)", "Public domain mark, "
     "but each week's file is about 1 GB zipped and the Open Data Portal needs the owner's key: too big for a "
     "library book. The Writing Kit downloads them by year on the owner's own computer (Build Patent Data.cmd). "
     "Index: https://data.uspto.gov/bulkdata/datasets/ptgrxml"),
    ("Harvard USPTO Patent Dataset (HUPD, patent applications 2004 to 2018)", "CC BY-SA 4.0 on Hugging Face, 62 GB in "
     "yearly files: a training corpus, not a library book; the Writing Kit uses it (share-alike). Index: "
     "https://huggingface.co/datasets/HUPD/hupd"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
