"""US patents for the Writing Kit (added on 22 November 2026 at the owner's request): technical writing in three
styles, the patent's abstract, its claims and its description. Kept in this one file so it is easy to merge with
other work on the kit. writing_sources.py adds SOURCES and NOT_USED from here, styles.py adds the style labels,
build_dataset.py reads a small sample, and build_patents.py downloads and builds the whole corpus year by year.

Two sources, one for each kind of download:

hupd_patents: the Harvard USPTO Patent Dataset (HUPD; Mirac Suzgun, Luke Melas-Kyriazi, Suproteem K. Sarkar, Scott
  Duke Kominers and Stuart M. Shieber, 2022): every English utility patent application filed with the USPTO from
  January 2004 to December 2018 (about 4.5 million), one JSON file each with its title, abstract, claims, background,
  summary and full description, dates, classes and the examiner's decision. On Hugging Face as HUPD/hupd, one file
  per filing year (data/2004.tar.gz ... data/2018.tar.gz), 61.76 GB in all (checked 22 November 2026; 2016 is the
  biggest, 5.57 GB; 2018 is small, 0.51 GB, because many 2018 applications were not yet published). Licence: the
  dataset card says CC BY-SA 4.0, so it is SHARE-ALIKE here (the patents themselves are public domain; the dataset's
  own licence is what the kit follows). Public, not gated, no key: huggingface.co's robots.txt allows programs. The
  kit downloads the year files the dataset's own loader uses, resumably, and lists them with their sizes and
  checksums through the Hugging Face file list.

uspto_patent_grants: the USPTO's own Patent Grant Full Text files (every granted patent, 1976 to the present, one file
  a week, issued on Tuesdays), public domain (data.gov lists the dataset with the Public Domain Mark; the USPTO's
  terms say "the text and drawings of a patent are typically not subject to copyright restrictions"). They come from
  the USPTO Open Data Portal's bulk data interface (api.uspto.gov/api/v1/datasets/products/...), which needs the
  owner's own free API key (made at data.uspto.gov, "API key management", after the USPTO's identity check) in the
  setting USPTO_ODP_API_KEY. The key is sent only to api.uspto.gov; when the portal sends the file from another
  address, the key is not sent there. Without the key the source is skipped with a plain message. The weekly files
  are XML (2002 on: version 2.5 until 2004, then version 4) or the old APS text format (1976 to 2001); the kit reads
  all three. Their sizes come from the portal's own list before anything is downloaded.

What the kit makes of each patent (both sources): up to three examples, one per style, when the patent has that part:
  patent_abstract      "Write the abstract of a US patent ... titled ...": the abstract
  patent_claims        "Write the claims of ...": every claim, numbered as filed
  patent_description   "Write the detailed description of ...": the whole description (background, summary and
                       detailed description)
A patent whose text carries a copyright or mask-work notice (37 CFR 1.71(d) and (e)) is left out, because that part
of its text may be under copyright. The text goes through the kit's usual scrub (under the owner's rule only Social
Security, card, bank and account numbers and passwords are masked). Each example also carries: year, decade,
application_number, patent_number, title, filing_date, grant_date, main_cpc, decision (HUPD's: accepted, rejected,
pending ...), section and word_count.
"""

import io
import json
import re
import tarfile
import urllib.error
import zipfile

import sources_more

HUPD_KEY = "hupd_patents"
HUPD_HOME = "https://huggingface.co/datasets/HUPD/hupd"
HUPD_TREE = "https://huggingface.co/api/datasets/HUPD/hupd/tree/main/data"
HUPD_FILE = "https://huggingface.co/datasets/HUPD/hupd/resolve/main/data/{name}"
HUPD_YEAR = re.compile(r"^(?:data/)?(\d{4})\.tar\.gz$")
HUPD_LICENCE = "CC BY-SA 4.0"
HUPD_LICENCE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
HUPD_SIZE_GB = 61.76
HUPD_CREDIT = ("The Harvard USPTO Patent Dataset (HUPD), by Mirac Suzgun, Luke Melas-Kyriazi, Suproteem K. Sarkar, Scott "
               "Duke Kominers and Stuart M. Shieber (2022, arXiv:2207.04043), made from USPTO patent applications")

USPTO_KEY = "uspto_patent_grants"
USPTO_KEY_ENV = "USPTO_ODP_API_KEY"
ODP = "https://api.uspto.gov/api/v1/"
ODP_SIGNUP = "https://data.uspto.gov/apis/getting-started"
USPTO_HOME = "https://data.uspto.gov/bulkdata/datasets/ptgrxml"
USPTO_LICENCE = "Public domain (US patent text: USPTO)"
USPTO_LICENCE_URL = "https://creativecommons.org/publicdomain/mark/1.0/"
USPTO_CREDIT = "United States Patent and Trademark Office, Patent Grant Full Text (bulk data)"
# The Open Data Portal's products for the full text of granted patents, looked for by these words in their titles
# (the product list is read at run time; the identifiers are not written into the kit).
GRANT_PRODUCT_WORDS = re.compile(r"(?i)patent grant full[- ]text")
GRANT_PRODUCT_NOT = re.compile(r"(?i)\b(with|embedded)\b.*\bimages?\b|\btiff\b")

OPT_IN = {HUPD_KEY, USPTO_KEY}            # off in the ordinary build unless named in --sources

STYLES = {"patent_abstract": "patent abstract (technical writing)",
          "patent_claims": "patent claims (technical and legal writing)",
          "patent_description": "patent description (technical writing)"}
FORMAL = set(STYLES)
CASUAL = set()
ASK = {"patent_abstract": ("abstract", "Write the abstract"), "patent_claims": ("claims", "Write the claims"),
       "patent_description": ("description", "Write the detailed description")}

COPYRIGHT_NOTICE = re.compile(r"(?i)(subject to (?:copyright|mask work) protection|copyright (?:owner|notice|"
                              r"protection)|mask work|©|\(c\)\s*(?:19|20)\d\d)")


# ====================================================================== the examples (both sources)

def clean(text):
    """Text with its spaces tidied but its paragraphs kept (blank lines between them)."""
    paragraphs = re.split(r"\n\s*\n", str(text or "").replace("\r", ""))
    return "\n\n".join(" ".join(p.split()) for p in paragraphs if p.split())


def plain_title(title):
    """A patent title as a plain title ("TACTILE DISPLAY" -> "Tactile display")."""
    title = " ".join(str(title or "").split()).rstrip(".")
    return title.capitalize() if title.isupper() else title


def patent_records(p, source_key):
    """The training records (build_dataset "text" records) of one patent p: {title, abstract, claims, description,
    application_number, patent_number, filing_date, grant_date, main_cpc, decision, kind ("application" or
    "granted patent")}; [] when it carries a copyright or mask-work notice."""
    whole = " ".join(str(p.get(k) or "") for k in ("abstract", "claims", "description"))
    if COPYRIGHT_NOTICE.search(whole):
        return []
    title = plain_title(p.get("title"))
    kind = p.get("kind") or "patent"
    date = p.get("grant_date") or p.get("filing_date") or ""
    year = int(date[:4]) if str(date)[:4].isdigit() else 0
    about = f'a US {kind}' + (f' titled "{title}"' if title else "")
    when = (f", granted {p['grant_date']}" if p.get("grant_date") else
            (f", filed {p['filing_date']}" if p.get("filing_date") else ""))
    cpc = f" (main CPC class {p['main_cpc']})" if p.get("main_cpc") else ""
    out = []
    for style, field in (("patent_abstract", "abstract"), ("patent_claims", "claims"),
                         ("patent_description", "description")):
        text = clean(p.get(field))
        if len(text.split()) < 5:
            continue
        what, ask = ASK[style]
        instruction = f"{ask} of {about}{when}{cpc}. Write it in the formal, precise style of a US patent."
        extra = {"year": year, "decade": f"{year // 10 * 10}s" if year else "",
                 "application_number": p.get("application_number", ""), "patent_number": p.get("patent_number", ""),
                 "title": title, "filing_date": p.get("filing_date", ""), "grant_date": p.get("grant_date", ""),
                 "main_cpc": p.get("main_cpc", ""), "decision": p.get("decision", ""), "section": field,
                 "word_count": len(text.split())}
        out.append(sources_more.text_record(str(year or "patents"), style, what, "patent", "formal technical style",
                                            "patent examiners and engineers", instruction, text, extra=extra))
    return out


# ====================================================================== HUPD (Hugging Face year files)

def hupd_year_files(listing):
    """[{"year", "name", "size", "sha256", "url"}] in year order from the Hugging Face file list of data/."""
    items = json.loads(listing) if isinstance(listing, (str, bytes)) else listing
    out = []
    for item in items:
        path = str(item.get("path", ""))
        m = HUPD_YEAR.match(path)
        if m and item.get("type", "file") == "file":
            lfs = item.get("lfs") or {}
            name = path.rsplit("/", 1)[-1]
            out.append({"year": int(m.group(1)), "name": name, "size": int(lfs.get("size") or item.get("size") or 0),
                        "sha256": lfs.get("oid", ""), "url": HUPD_FILE.format(name=name)})
    return sorted(out, key=lambda f: f["year"])


def hupd_patent(data):
    """One HUPD application (its JSON already read) in the shared shape (see patent_records)."""
    description = data.get("full_description") or "\n\n".join(
        str(data.get(k) or "") for k in ("background", "summary") if data.get(k))
    return {"title": data.get("title", ""), "abstract": data.get("abstract", ""), "claims": data.get("claims", ""),
            "description": description, "application_number": str(data.get("application_number", "")),
            "patent_number": str(data.get("patent_number") or "").replace("None", ""),
            "filing_date": _iso(data.get("filing_date")) or str(data.get("filing_date") or "")[:10], "grant_date": "",
            "main_cpc": data.get("main_cpc_label", ""), "decision": data.get("decision", ""),
            "kind": "patent application"}


def hupd_records(stream, limit=None):
    """Records for the applications of one HUPD year file (an open binary stream of the .tar.gz, read as it
    arrives), up to limit applications (None: all)."""
    n = 0
    with tarfile.open(fileobj=stream, mode="r|gz") as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith(".json"):
                continue
            try:
                data = json.loads(tar.extractfile(member).read().decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(data, dict):
                yield from patent_records(hupd_patent(data), HUPD_KEY)
                n += 1
                if limit and n >= limit:
                    return


# ====================================================================== the USPTO's weekly full-text files

def xml_text(fragment):
    """The plain words of an XML fragment (tags dropped, entities read, spaces tidied)."""
    import html
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment or "")).split())


def _iso(yyyymmdd):
    d = re.sub(r"\D", "", str(yyyymmdd or ""))[:8]
    return f"{d[:4]}-{d[4:6]}-{d[6:]}" if len(d) == 8 else ""


def grant_v4(doc):
    """One granted patent of the version 4 XML (2005 on: <us-patent-grant>) in the shared shape."""
    pub = re.search(r"<publication-reference\b.*?<doc-number>(.*?)</doc-number>.*?<date>(\d{8})</date>", doc, re.S)
    app = re.search(r"<application-reference\b.*?<doc-number>(.*?)</doc-number>.*?<date>(\d{8})</date>", doc, re.S)
    title = re.search(r"<invention-title\b[^>]*>(.*?)</invention-title>", doc, re.S)
    abstract = re.search(r"<abstract\b[^>]*>(.*?)</abstract>", doc, re.S)
    claims = [xml_text(c) for c in re.findall(r"<claim\b[^>]*>(.*?)</claim>", doc, re.S)]
    desc = re.search(r"<description\b[^>]*>(.*?)</description>", doc, re.S)
    paragraphs = [xml_text(b) for _k, b in re.findall(r"<(heading|p)\b[^>]*>(.*?)</\1>", desc.group(1) if desc else "",
                                                      re.S)]
    cpc = re.search(r"<classification-cpc\b.*?<section>(\w)</section>\s*<class>(\d+)</class>\s*<subclass>(\w)"
                    r"</subclass>\s*<main-group>(\w+)</main-group>\s*<subgroup>(\w+)</subgroup>", doc, re.S)
    return {"title": xml_text(title.group(1)) if title else "",
            "abstract": "\n\n".join(xml_text(p) for p in re.findall(r"<p\b[^>]*>(.*?)</p>", abstract.group(1), re.S))
            if abstract else "",
            "claims": "\n\n".join(c for c in claims if c), "description": "\n\n".join(p for p in paragraphs if p),
            "application_number": app.group(1) if app else "", "patent_number": pub.group(1).lstrip("0") if pub
            else "", "filing_date": _iso(app.group(2)) if app else "", "grant_date": _iso(pub.group(2)) if pub
            else "", "main_cpc": "{}{}{}{}/{}".format(*cpc.groups()) if cpc else "", "decision": "granted",
            "kind": "patent"}


def grant_v25(doc):
    """One granted patent of the version 2.5 XML (2002 to 2004: <PATDOC>) in the shared shape."""
    def first(pattern):
        m = re.search(pattern, doc, re.S)
        return xml_text(m.group(1)) if m else ""
    number = first(r"<B110>.*?<DNUM>(.*?)</DNUM>")
    claims = [xml_text(c) for c in re.findall(r"<CLM\b[^>]*>(.*?)</CLM>", doc, re.S)]
    desc = re.search(r"<SDODE\b[^>]*>(.*?)</SDODE>", doc, re.S)
    paragraphs = [xml_text(p) for p in re.findall(r"<(?:PARA|H)\b[^>]*>(.*?)</(?:PARA|H)>", desc.group(1) if desc
                                                  else "", re.S)]
    return {"title": first(r"<B540>(.*?)</B540>"), "abstract": first(r"<SDOAB\b[^>]*>(.*?)</SDOAB>"),
            "claims": "\n\n".join(c for c in claims if c), "description": "\n\n".join(p for p in paragraphs if p),
            "application_number": first(r"<B210>.*?<DNUM>(.*?)</DNUM>"), "patent_number": number.lstrip("0"),
            "filing_date": _iso(first(r"<B220>.*?<DATE>(.*?)</DATE>")),
            "grant_date": _iso(first(r"<B140>.*?<DATE>(.*?)</DATE>")), "main_cpc": "", "decision": "granted",
            "kind": "patent"}


def grant_docs(text):
    """The patents of one weekly XML file (many XML documents one after another), each in the shared shape."""
    for doc in re.split(r"(?=<\?xml\b)", text):
        if "<us-patent-grant" in doc:
            yield grant_v4(doc)
        elif "<PATDOC" in doc:
            yield grant_v25(doc)


# The APS section names: the fields after one of these belong to that section until the next.
APS_SECTIONS = {"ABST", "BSUM", "DETD", "CLMS", "DRWD", "INVT", "ASSG", "UREF", "FREF", "OREF", "LREP", "PCTA", "PRIR",
                "RLAP", "REIS", "GOVT", "PARN", "DCLM", "CLAS"}


def aps_docs(text):
    """The patents of one weekly APS text file (1976 to 2001: records that start with "PATN", each line a
    four-letter field name and its value, longer values continued on lines that start with spaces), each in the
    shared shape."""
    for block in re.split(r"(?m)^PATN\s*$", text.replace("\r", "")):
        if "TTL " not in block:
            continue
        section, fields, last = "", [], None
        for line in block.split("\n"):
            head = line[:4]
            if re.fullmatch(r"[A-Z][A-Z0-9]{2}[A-Z0-9 ]", head) and line[4:5] in (" ", ""):
                name, value = head.strip(), line[5:].strip()
                if name in APS_SECTIONS:
                    section = name
                    continue
                fields.append([section, name, value])
                last = fields[-1]
            elif line.startswith("     ") and last is not None:
                last[2] += " " + line.strip()
        top = lambda name: next((v for s, n, v in fields if s == "" and n == name), "")
        claims, current = [], []
        for s, n, v in fields:
            if s != "CLMS":
                continue
            if n == "NUM" and current:
                claims.append(" ".join(current))
                current = []
            if n in ("NUM", "PAR", "PAL", "PA1", "PA2", "PA3", "PA4", "PA5"):
                current.append(v if n != "NUM" or v.endswith(".") else f"{v}.")
        if current:
            claims.append(" ".join(current))
        description = [v for s, n, v in fields if s in ("BSUM", "DETD") and n in ("PAR", "PAC", "PA1", "PA2", "PA3",
                                                                                   "PA4", "PA5", "PAL")]
        yield {"title": top("TTL"), "abstract": "\n\n".join(v for s, n, v in fields if s == "ABST" and n.startswith("PA")),
               "claims": "\n\n".join(claims), "description": "\n\n".join(description),
               # WKU is nine characters: a leading 0, the seven-digit number and a check digit ("039300014")
               "application_number": top("APN"), "patent_number": re.sub(r"^0+", "", top("WKU")[1:8]),
               "filing_date": _iso(top("APD")), "grant_date": _iso(top("ISD")), "main_cpc": "",
               "decision": "granted", "kind": "patent"}


def documents(lines, marker):
    """The documents of a weekly file read line by line (lines: text lines), each one string, split where a line
    starts with marker ("<?xml" for the XML files, "PATN" for the APS text files). Only one document is held at a
    time, so a weekly file of several hundred megabytes is never read into memory whole."""
    current = []
    for line in lines:
        if line.startswith(marker) and current:
            yield "".join(current)
            current = []
        current.append(line)
    if current:
        yield "".join(current)


def weekly_records(path_or_bytes, limit=None):
    """Records for the patents of one weekly zip file (XML or APS text inside), up to limit patents."""
    source = io.BytesIO(path_or_bytes) if isinstance(path_or_bytes, bytes) else path_or_bytes
    n = 0
    with zipfile.ZipFile(source) as z:
        for name in z.namelist():
            if not re.search(r"(?i)\.(xml|txt|sgm)$", name):
                continue
            with z.open(name) as raw:
                lines = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")
                first = lines.readline()
                xml = first.startswith("<?xml") or "<" in first[:5]
                rest = (line for part in ([first], lines) for line in part)
                for doc in documents(rest, "<?xml" if xml else "PATN"):
                    for p in (grant_docs(doc) if xml else aps_docs(doc)):
                        yield from patent_records(p, USPTO_KEY)
                        n += 1
                        if limit and n >= limit:
                            return


# ====================================================================== the Open Data Portal's file lists

def odp_files(product_json, year=None):
    """[{"name", "size", "url", "date"}] of a product's files (the portal's JSON, as text or read), only those of
    year when given (by the date in the file, or the year in its name)."""
    data = json.loads(product_json) if isinstance(product_json, (str, bytes)) else product_json
    products = data.get("bulkDataProductBag") or [data]
    out = []
    for prod in products:
        bag = prod.get("productFileBag") or {}
        files = bag.get("fileDataBag", []) if isinstance(bag, dict) else bag
        for f in files:
            name = str(f.get("fileName") or "")
            date = str(f.get("fileDataFromDate") or f.get("fileDate") or f.get("fileReleaseDate") or "")[:10]
            # the year in the name: pftaps19760106 (four digits), ipg300105 or pg030107 (two digits)
            m = re.search(r"pftaps(\d{4})", name) or re.search(r"(?:ipg|pg)(\d{2})\d{4}", name)
            guess = ""
            if m:
                digits = m.group(1)
                guess = digits if len(digits) == 4 else ("20" if int(digits) < 70 else "19") + digits
            when = date[:4] or guess
            if not name.lower().endswith(".zip") or (year and when != str(year)):
                continue
            out.append({"name": name, "size": int(f.get("fileSize") or 0), "date": date,
                        "url": str(f.get("fileDownloadURI") or f"{ODP}datasets/products/{prod.get('productIdentifier')}"
                                   f"/files/{name}")})
    return sorted(out, key=lambda f: f["name"])


def grant_products(search_json):
    """The identifiers of the Open Data Portal's products for granted patents' full text without images (from the
    product search's JSON)."""
    data = json.loads(search_json) if isinstance(search_json, (str, bytes)) else search_json
    out = []
    for prod in data.get("bulkDataProductBag") or []:
        title = str(prod.get("productTitleText") or "")
        if GRANT_PRODUCT_WORDS.search(title) and not GRANT_PRODUCT_NOT.search(title):
            out.append(str(prod.get("productIdentifier") or ""))
    return [p for p in out if p]


# ====================================================================== the sample read by the ordinary build

def read_hupd(fetcher, say=print, patent_folder="patents", per_year=20, sample_years=("2016",), **_):
    """Records for a SAMPLE build (build_dataset.py --sources hupd_patents): up to per_year applications from each
    HUPD year file already downloaded by build_patents.py, or else from the start of the January 2016 sample file
    read straight from Hugging Face (nothing is saved). The whole corpus is built by build_patents.py."""
    import os
    folder = os.path.join(patent_folder, HUPD_KEY)
    local = sorted(n for n in (os.listdir(folder) if os.path.isdir(folder) else []) if HUPD_YEAR.match(n))
    if local:
        for name in local:
            with open(os.path.join(folder, name), "rb") as f:
                got = 0
                for record in hupd_records(f, per_year):
                    got += 1
                    yield record
            say(f"  HUPD {name}: {got} examples read.")
        return
    url = "https://huggingface.co/datasets/HUPD/hupd/resolve/main/data/sample-jan-2016.tar.gz"
    try:
        resp = fetcher.open_stream(url)
    except urllib.error.HTTPError as err:
        say(f"  HUPD sample: not read ({err}).")
        return
    got = 0
    try:
        for record in hupd_records(resp, per_year * 3):
            got += 1
            yield record
    finally:
        resp.close()
    say(f"  HUPD: {got} examples from the start of {url}.")


def read_uspto_grants(fetcher, say=print, **_):
    """The USPTO grants are read only by build_patents.py (they need the owner's key and whole weekly files); the
    ordinary build says so and reads nothing."""
    say("  USPTO patent grants: read by build_patents.py --source uspto (it needs the USPTO_ODP_API_KEY setting); "
        "nothing is read in the ordinary build.")
    return iter(())


# ====================================================================== the Source entries and the sources not used

def sources(Source, OPEN, SHARE_ALIKE, PERSONAL):
    """The Source entries for writing_sources.SOURCES."""
    return [
        Source(key=HUPD_KEY, name="Harvard USPTO Patent Dataset (HUPD): US patent applications 2004 to 2018, "
               "abstracts, claims and descriptions (Hugging Face)", licence=HUPD_LICENCE, licence_class=SHARE_ALIKE,
               licence_url=HUPD_LICENCE_URL, credit=HUPD_CREDIT, home=HUPD_HOME, reader="read_hupd",
               notes="15 year files, 61.76 GB in all, downloaded by build_patents.py (resumable; years and a size "
                     "cap can be chosen). Three styles: patent_abstract, patent_claims, patent_description. "
                     "Applications with a copyright or mask-work notice are left out. Off in the ordinary build "
                     "unless named in --sources, which reads a small sample."),
        Source(key=USPTO_KEY, name="USPTO Patent Grant Full Text: every granted US patent, 1976 to now (Open Data "
               "Portal bulk files)", licence=USPTO_LICENCE, licence_class=OPEN, licence_url=USPTO_LICENCE_URL,
               credit=USPTO_CREDIT, home=USPTO_HOME, reader="read_uspto_grants",
               notes="Weekly files read by build_patents.py --source uspto, year by year (resumable). Needs the "
                     "owner's own free key in USPTO_ODP_API_KEY (data.uspto.gov, API key management); sent only to "
                     "api.uspto.gov. Patents with a copyright or mask-work notice are left out."),
    ]


NOT_USED = [
    ("Google Patents and Google's patent datasets on BigQuery",
     "Google's terms forbid scraping its pages, and BigQuery needs a Google Cloud account and billing. The USPTO's "
     "own files are used (uspto_patent_grants), and HUPD."),
    ("BIGPATENT (Hugging Face big_patent)",
     "CC BY 4.0, but only the descriptions and abstracts of 1.3 million patents, already covered by the USPTO's own "
     "full text; not added."),
    ("PatentsView (search.patentsview.org)",
     "Paused on 20 March 2026 while it moves into the USPTO Open Data Portal."),
]
