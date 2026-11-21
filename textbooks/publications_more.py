"""More reference sources built in pieces, from the reference inventory's top 50 (2026-11-21), added to the
periodicals builder (periodicals.py: its SOURCES, DRIVERS, ALL_PIECES, LICENCE_LINES and NOT_INCLUDED):

  canada_ogl          Government of Canada publications released under the Open Government Licence - Canada on
                      open.canada.ca (its documented CKAN API): Health Canada and the Public Health Agency, Transport
                      Canada and the Transportation Safety Board, Veterans Affairs Canada, and Justice Canada; one
                      book per subject (pub:canada_ogl:health), or per subject and year (pub:canada_ogl:health-2019)
  gao_reports         US Government Accountability Office reports and decisions in govinfo.gov's GAOREPORTS collection
                      (1989 to 2008; public domain), one book per year, read from govinfo's own sitemaps and the
                      reports' text files (pub:gao_reports:2005)
  us_government_manual  The United States Government Manual (what each federal agency does, with its addresses),
                      govinfo.gov's GOVMAN collection, one book per edition (pub:us_government_manual:2025)
  eric_open           ERIC full texts whose OWN text says they are in the public domain or under an open Creative
                      Commons licence (no "NoDerivatives"), on blindness and visual impairment, braille, assistive
                      technology, deafblindness and adult basic and vocational education (pub:eric_open:braille)
  govuk_guides        GOV.UK guides on caring and power of attorney, pensions and Access to Work, housing and renting,
                      tax and debt, and driving (GOV.UK's search and content APIs; Open Government Licence)
  uk_safety_alerts    The MHRA's Drug Safety Update, its medicine and device alerts, and the UK's product safety
                      alerts and recalls (GOV.UK's search and content APIs; Open Government Licence), one book per
                      kind and year (pub:uk_safety_alerts:drug-2026)
  usda_farmers_bulletins  USDA Farmers' Bulletins (home canning, gardening, livestock, household), public domain,
                      from the Internet Archive's copies, one book per decade, with a strong notice that old advice
                      can be unsafe today (pub:usda_farmers_bulletins:1940s)

Every source's licence was checked by hand on 2026-11-21 (LICENCE_LINES) and every request obeys the site's
robots.txt (build_textbooks.allowed_by_robots, which also reads "*" and "$" rules and a Crawl-delay in words) with
one request at a time and the builder's pause. Each non-US book carries its specific practice notice (the
builder's practice_note_of, with the subjects added in reference_more.PRACTICE_SUBJECTS).
"""

import datetime
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_textbooks as B  # noqa: E402
import periodicals as P  # noqa: E402

US_GOV, US_GOV_URL = P.US_GOV, P.US_GOV_URL
OGL_CANADA_URL = "https://open.canada.ca/en/open-government-licence-canada"
OGL_UK_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
GOVINFO = "https://www.govinfo.gov"
CKAN = "https://open.canada.ca/data/api/action/package_search"
GOVUK = "https://www.gov.uk"
ERIC_API = "https://api.ies.ed.gov/eric/"
ERIC_FILES = "https://files.eric.ed.gov/fulltext/"
IA = "https://archive.org"
PDF_MAX_BYTES = 80_000_000       # a publication larger than this is left out (said in the catalogue)
PDF_MAX_PAGES = 400              # pages of one publication kept (the rest said on its page)


def _years_between(first, last):
    """Years as strings, newest first."""
    return [str(y) for y in range(last, first - 1, -1)]


def _this_year(today=None):
    return (today or datetime.date.today()).year


# ====================================================================== shared helpers

def pdf_item_body(url, cache, left_out, label):
    """(HTML of a PDF's text, pages) for one publication, or ("", 0) when it is too big, not allowed by robots.txt,
    or a scan without words (the reason added to left_out)."""
    if not B.allowed_by_robots(url, cache):
        left_out.append({"title": label, "reason": "The site's robots.txt does not allow reading its PDF."})
        return "", 0
    try:
        data = B.fetch(url, cache, binary=True)
    except (urllib.error.URLError, OSError) as e:
        left_out.append({"title": label, "reason": f"Its PDF could not be read ({e})."})
        return "", 0
    if len(data) > PDF_MAX_BYTES or not data.startswith(b"%PDF"):
        left_out.append({"title": label, "reason": "Its file is not a PDF, or larger than this builder takes."})
        return "", 0
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(data)
        path = f.name
    try:
        text = B.PdfText(path)
        count = text.count
        sample = range(0, count, max(1, count // 20))
        if sum(1 for n in sample if len(" ".join(text.lines(n))) > 80) < 0.5 * len(sample):
            left_out.append({"title": label, "reason": "A scan without its words (no text layer)."})
            return "", 0
        body = B.part_html(text, 0, min(count, PDF_MAX_PAGES))
        if count > PDF_MAX_PAGES:
            body += f"<p>Only the first {PDF_MAX_PAGES} of its {count} pages are here; the whole PDF is at the original."
            body += "</p>"
        return body, count
    finally:
        os.unlink(path)


def pdf_front_words(url, cache, pages=4):
    """The words of a PDF's first pages and last page (where licence statements are printed), and the PdfText's
    page count; ("", 0) when it cannot be read."""
    import tempfile
    try:
        data = B.fetch(url, cache, binary=True)
    except (urllib.error.URLError, OSError):
        return "", 0, b""
    if not data.startswith(b"%PDF") or len(data) > PDF_MAX_BYTES:
        return "", 0, b""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(data)
        path = f.name
    try:
        text = B.PdfText(path)
        wanted = list(range(min(pages, text.count))) + ([text.count - 1] if text.count > pages else [])
        return " ".join(" ".join(text.lines(n)) for n in wanted), text.count, data
    finally:
        os.unlink(path)


def pre_html(text):
    """Plain text (a <pre> block of govinfo's text files, an Internet Archive OCR text) as HTML paragraphs: lines
    joined into paragraphs at blank lines, words unchanged."""
    out = []
    for para in re.split(r"\n\s*\n", html.unescape(text or "")):
        words = " ".join(para.split())
        if words:
            out.append(f"<p>{B.esc(words)}</p>")
    return "\n".join(out)


# ====================================================================== Canada: Open Government Licence publications

# The subjects (piece names) and the CKAN filter of each. Only records of the "publication" collection whose licence
# is the Open Government Licence - Canada (license_id ca-ogl-lgo) are read.
CANADA_TOPICS = {
    "health": ("Health and safety (Health Canada and the Public Health Agency of Canada)",
               "subject:health_and_safety AND (organization:hc-sc OR organization:phac-aspc)"),
    "transport": ("Transport and transportation safety (Transport Canada and the Transportation Safety Board)",
                  "subject:transport"),
    "veterans": ("Veterans and their families (Veterans Affairs Canada)", "organization:vac-acc"),
    "law": ("Law and justice (Justice Canada)", "organization:jus"),
}
# Which files are taken: the PDF document files of a publication record, on a Government of Canada host. The
# record's licence (the Open Government Licence - Canada, which allows commercial use) covers the publication. Web
# pages (HTML) are NOT taken: the canada.ca web pages and the departments' sites are under their own terms, which
# allow only non-commercial reproduction. Copies in web archives are not taken either.
CANADA_HOST = re.compile(r"(^|\.)(canada\.ca|gc\.ca)$")
CANADA_NOT_HOST = re.compile(r"wayback|webarchive|archive")


def canada_files(record):
    """[(address, name)] of the English PDF document files of an open.canada.ca publication record, on Government of
    Canada hosts (relative addresses are files deposited on open.canada.ca)."""
    out = []
    for r in record.get("resources") or []:
        url = str(r.get("url") or "")
        if str(r.get("format", "")).upper() != "PDF" or "en" not in str(r.get("language", "")):
            continue
        if url.startswith("/"):
            url = "https://open.canada.ca" + url
        host = urllib.parse.urlsplit(url).hostname or ""
        if not url.startswith("https://") or not CANADA_HOST.search(host) or CANADA_NOT_HOST.search(host):
            continue
        out.append((url, str(r.get("name") or "")))
    return out


def _translated(value, lang="en"):
    """The English text of a CKAN translated field (a dict, or its str() form, or a plain string)."""
    if isinstance(value, dict):
        return str(value.get(lang) or "")
    if isinstance(value, str) and value.startswith("{"):
        m = re.search(r"'" + lang + r"':\s*(['\"])(.*?)\1", value)
        return m.group(2) if m else ""
    return str(value or "")


def canada_records(fq, cache):
    """Every open.canada.ca publication record matching fq under the Open Government Licence - Canada, newest
    first (CKAN package_search, 100 a page)."""
    out, start = [], 0
    while True:
        query = urllib.parse.urlencode({"fq": f"collection:publication AND license_id:ca-ogl-lgo AND ({fq})",
                                        "rows": 100, "start": start, "sort": "date_published desc"})
        data = json.loads(B.fetch(f"{CKAN}?{query}", None)).get("result") or {}     # the list: fresh each time
        rows = data.get("results") or []
        out += rows
        start += len(rows)
        if len(rows) < 100 or start >= int(data.get("count") or 0) or start >= 10000:
            return out


def canada_ogl_items(spec, piece, cache, left_out, today):
    """The publications of one subject (and year, "health-2019"): each record's licence checked (ca-ogl-lgo), its
    first English PDF read into one page with the publisher, the date and the record's address."""
    topic, _, year = piece.partition("-")
    _name, fq = CANADA_TOPICS[topic]
    out, skipped = [], 0
    for rec in canada_records(fq, cache):
        if rec.get("license_id") != "ca-ogl-lgo":
            continue
        date = B.iso_date(str(rec.get("date_published") or "")[:10])
        if year and not date.startswith(year):
            continue
        files = canada_files(rec)
        if not files:
            skipped += 1                     # web pages only: not taken (see CANADA_HOST)
            continue
        if len(out) >= spec.get("limit", P.MAX_ITEMS):
            break
        title = _translated(rec.get("title_translated")) or str(rec.get("title") or "")
        body, _pages = pdf_item_body(files[0][0], cache, left_out, title)
        if not body:
            continue
        org = rec.get("organization") or {}
        publisher = _translated(rec.get("org_title_at_publication")) or str(org.get("title", "")).split("|")[0].strip()
        notes = _translated(rec.get("notes_translated")) or str(rec.get("notes") or "")
        intro = f"<p>{B.esc(' '.join(notes.split()))}</p>\n" if notes.strip() else ""
        intro += f'<p>File: <a href="{B.esc(files[0][0])}">{B.esc(files[0][1] or files[0][0])}</a>.</p>\n'
        out.append(P.item(f"https://open.canada.ca/data/en/dataset/{rec.get('id')}", title, date, intro + body,
                          P.month_unit(date)[-4:] if date else "", byline=publisher))
    if skipped:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{skipped} records link only web "
                         "pages (under the terms of the canada.ca web pages, non-commercial only), so they are not "
                         "taken."})
    return out


# ====================================================================== GAO reports (govinfo GAOREPORTS)

def govinfo_sitemap(collection, year, cache):
    """The package ids of one year of a govinfo collection, from its own sitemap (robots.txt lists these)."""
    text = B.fetch(f"{GOVINFO}/sitemap/{collection}_{year}_sitemap.xml", cache)
    return re.findall(r"<loc>\s*https://www\.govinfo\.gov/app/details/([A-Za-z0-9._-]+)\s*</loc>", text)


def gao_items(spec, piece, cache, left_out, today):
    """The GAO reports and decisions of one year: each package's text file (title, date, report number and the
    whole report as published)."""
    out, failed = [], 0
    for pkg in govinfo_sitemap("GAOREPORTS", piece, cache)[:spec.get("limit", P.MAX_ITEMS)]:
        url = f"{GOVINFO}/content/pkg/{pkg}/html/{pkg}.htm"
        if not B.allowed_by_robots(url, cache):
            failed += 1
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        title = html.unescape(re.sub(r"<[^>]+>", "", (re.search(r"<title>(.*?)</title>", text, re.S) or
                                                         re.search(r"()", "")).group(1))).strip() or pkg
        pre = re.search(r"<pre>(.*?)</pre>", text, re.S)
        body_text = pre.group(1) if pre else re.sub(r"<[^>]+>", " ", text)
        m = re.search(r"^DATE:\s*(.+)$", body_text, re.M)
        date = B.iso_date(m.group(1)) if m else piece
        body_text = re.sub(r"^\*{20,}\s*$", "", body_text, flags=re.M)
        number = (re.search(r"^(?:BNUMBER|REPORTNUMBER):\s*(.+)$", body_text, re.M) or re.search(r"()", "")).group(1)
        out.append(P.item(f"{GOVINFO}/app/details/{pkg}", title, date, pre_html(body_text), P.month_unit(date),
                          byline=f"US Government Accountability Office{', ' + number.strip() if number else ''}"))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} reports could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== the United States Government Manual (GOVMAN)

MODS = "{http://www.loc.gov/mods/v3}"
XLINK = "{http://www.w3.org/1999/xlink}"
# GOVMAN XML elements read as headings, and those left out (internal ids, sort orders, empty footers).
GOVMAN_HEADINGS = {"AgencyName": 2, "Heading": 3, "Title": 3, "Name": 4, "SubHeading": 4}
GOVMAN_SKIP = {"accessId", "EntityType", "SortOrder", "FooterDetails", "Footer"}


def govman_html(xml_text):
    """One agency's entry of the Government Manual (its XML) as HTML: its name and headings as headings, every
    paragraph and address line as a paragraph, in the order of the file (words unchanged)."""
    root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    parts = []

    def walk(el):
        tag = el.tag.split("}")[-1]
        if tag in GOVMAN_SKIP:
            return
        own = " ".join((el.text or "").split())
        if own and len(el) == 0:
            level = GOVMAN_HEADINGS.get(tag)
            if level:
                parts.append(f"<h{level}>{B.esc(own)}</h{level}>")
            elif tag in ("WebAddress", "Email") and re.match(r"(https?://|www\.)", own):
                href = own if own.startswith("http") else "https://" + own
                parts.append(f'<p><a href="{B.esc(href)}">{B.esc(own)}</a></p>')
            else:
                parts.append(f"<p>{B.esc(own)}</p>")
        for child in el:
            walk(child)
    walk(root)
    return "\n".join(parts)


def govman_package(year, cache):
    """The package id of the newest Government Manual edition of a year ("GOVMAN-2025-12-31"), from govinfo's
    sitemap of that year; "" when there is none."""
    try:
        ids = govinfo_sitemap("GOVMAN", year, cache)
    except urllib.error.HTTPError:
        return ""
    return sorted(ids)[-1] if ids else ""


def govman_items(spec, piece, cache, left_out, today):
    """The entries (agencies, offices, boards) of one edition of the Government Manual, in the manual's order, each
    from its XML granule listed in the edition's MODS record."""
    pkg = govman_package(piece, cache)
    if not pkg:
        return []
    mods = ET.fromstring(B.fetch(f"{GOVINFO}/metadata/pkg/{pkg}/mods.xml", cache).encode("utf-8"))
    date = B.iso_date(pkg[7:]) or piece
    out, failed = [], 0
    for rel in mods.findall(f"{MODS}relatedItem[@type='constituent']"):
        title = " ".join("".join(rel.find(f"{MODS}titleInfo/{MODS}title").itertext()).split()) \
            if rel.find(f"{MODS}titleInfo/{MODS}title") is not None else ""
        xml_url = next((o.get(f"{XLINK}href") for o in rel.findall(f"{MODS}relatedItem[@type='otherFormat']")
                        if str(o.get(f"{XLINK}href", "")).endswith(".xml")), "")
        if not xml_url:
            continue                        # the Declaration and the Constitution: PDFs only (in the Kiwix library)
        try:
            body = govman_html(B.fetch(xml_url, cache))
        except (urllib.error.URLError, OSError, ET.ParseError):
            failed += 1
            continue
        category = (re.search(r"<p>(Legislative Branch|Judicial Branch|Executive Branch|Executive Departments|"
                              r"Independent [^<]*|Boards[^<]*|Quasi-Official[^<]*|International[^<]*)</p>", body)
                    or re.search(r"()", "")).group(1)
        out.append(P.item(xml_url.replace("/xml/", "/html/").replace(".xml", ".htm"), title or xml_url, date, body,
                          category))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} entries could not be read."})
    P.PUBLISHED[("us_government_manual", piece)] = date
    return out


# ====================================================================== ERIC: open full texts

ERIC_TOPICS = {
    "vision": ("Blindness and visual impairment", 'subject:"Visual Impairments" OR subject:Blindness OR '
               'subject:"Partial Vision"'),
    "braille": ("Braille", "subject:Braille"),
    "assistive": ("Assistive technology", 'subject:"Assistive Technology" OR subject:"Screen Readers" OR '
                  'subject:"Accessibility (for Disabled)"'),
    "deafblind": ("Deafblindness", 'subject:"Deaf Blind"'),
    "adult_education": ("Adult basic and vocational education", 'subject:"Adult Basic Education" OR '
                        'subject:"Adult Literacy" OR subject:"Vocational Education"'),
}
# A licence statement printed in the document itself: public domain (US Department of Education and other federal
# reports print "This report is in the public domain"), or Creative Commons without NoDerivatives.
PUBLIC_DOMAIN_LINE = re.compile(r"\b(?:this|the)\s+(?:report|publication|document|guide|brief|book|paper|product)\s+is"
                                r"\s+in\s+the\s+public\s+domain", re.I)
CC_LINE = re.compile(r"Creative\s+Commons\s+(?:Attribution|CC[-\s]BY)[^.;]{0,80}|\bCC[-\s]BY(?:[-\s](?:NC|SA)){0,2}"
                     r"(?:[-\s]\d\.\d)?\b|\bCC0\b|Creative\s+Commons\s+Zero", re.I)


def eric_licence(words):
    """(licence short name, address) of a document from the licence statement in its own words, or ("", "") when it
    states none we may use (NoDerivatives licences, "all rights reserved" alone, or nothing)."""
    words = " ".join(words.split())
    if PUBLIC_DOMAIN_LINE.search(words):
        return US_GOV if re.search(r"U\.?\s?S\.?\s+Department|Institute of Education Sciences|National Center for "
                                   r"Education|federal", words, re.I) else "PD", US_GOV_URL
    m = CC_LINE.search(words)
    if not m:
        return "", ""
    around = words[max(0, m.start() - 40):m.end() + 80]
    if re.search(r"no\s*-?\s*deriv|\bND\b", around, re.I):
        return "", ""
    if re.search(r"CC0|Zero", m.group(0), re.I):
        return "CC0", "https://creativecommons.org/publicdomain/zero/1.0/"
    nc = bool(re.search(r"non\s*-?\s*commercial|\bNC\b", around, re.I))
    sa = bool(re.search(r"share\s*-?\s*alike|\bSA\b", around, re.I))
    version = (re.search(r"\b([1-4]\.0)\b", around) or re.search(r"()", "")).group(1) or "4.0"
    kind = "by" + ("-nc" if nc else "") + ("-sa" if sa else "")
    return f"CC {kind.upper()} {version}", f"https://creativecommons.org/licenses/{kind}/{version}/"


def eric_candidates(topic_query, cache, want):
    """ERIC records (newest first) with full text in ERIC (e_fulltextauth:1), English, matching the topic."""
    out, start = [], 0
    while len(out) < want:
        query = urllib.parse.urlencode({"search": f"({topic_query}) AND e_fulltextauth:1 AND language:English",
                                        "format": "json", "rows": 200, "start": start,
                                        "fields": "id,title,author,publisher,publicationdateyear,source,"
                                                  "publicationtype,description"})
        data = json.loads(B.fetch(f"{ERIC_API}?{query}", None)).get("response") or {}
        docs = data.get("docs") or []
        out += docs
        start += len(docs)
        if len(docs) < 200 or start >= int(data.get("numFound") or 0):
            break
    out.sort(key=lambda d: int(d.get("publicationdateyear") or 0), reverse=True)
    return out[:want]


def eric_items(spec, piece, cache, left_out, today):
    """The ERIC full texts of one topic whose own text states a licence we may use (eric_licence): each document's
    PDF from files.eric.ed.gov, kept whole, with its authors, source, year and its own licence on its page."""
    _name, query = ERIC_TOPICS[piece]
    out, closed = [], 0
    for doc in eric_candidates(query, cache, spec.get("candidates", 800)):
        if len(out) >= spec.get("limit", 400):
            break
        eid = str(doc.get("id") or "")
        url = f"{ERIC_FILES}{eid}.pdf"
        if not re.match(r"^E[DJ]\d+$", eid) or not B.allowed_by_robots(url, cache):
            continue
        words, _count, _data = pdf_front_words(url, cache)
        licence, licence_url = eric_licence(words)
        if not licence:
            closed += 1                       # ERIC may show it, but it is not openly licensed: not taken
            continue
        body, _pages = pdf_item_body(url, cache, left_out, str(doc.get("title") or eid))
        if not body:
            continue
        year = str(doc.get("publicationdateyear") or "")
        authors = "; ".join(doc.get("author") or [])
        source = str(doc.get("source") or str(doc.get("publisher") or "").split(".")[0])
        desc = str(doc.get("description") or "")
        intro = f"<p>{B.esc(html.unescape(desc))}</p>\n" if desc else ""
        out.append(P.item(f"https://eric.ed.gov/?id={eid}", html.unescape(str(doc.get("title") or eid)), year,
                          intro + body,
                          year[:3] + "0s" if year else "", byline="; ".join(x for x in (authors, source) if x),
                          licence=licence, licence_url=licence_url))
    if closed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{closed} documents state no open "
                         "licence in their own text (ERIC may show them, but that is not a licence to repackage): "
                         "not taken."})
    return out


# ====================================================================== GOV.UK guides and UK safety alerts

GOVUK_TOPICS = {
    "carers": ("Caring for someone and power of attorney",
               ["benefits/looking-after-someone", "births-deaths-marriages/lasting-power-attorney",
                "births-deaths-marriages/death"]),
    "pensions": ("State Pension, workplace pensions and Access to Work",
                 ["working/state-pension", "working/workplace-personal-pensions", "disabilities/work"]),
    "housing": ("Housing, renting and council services",
                ["housing-local-services/renting-property", "housing-local-services/council-housing-association",
                 "housing-local-services/council-tax", "housing-local-services/repossessions-evictions",
                 "housing-local-services/household-energy", "housing-local-services/buying-owning-property"]),
    "tax_debt": ("Personal tax and debt",
                 ["tax/income-tax", "tax/national-insurance", "tax/self-assessment", "tax/dealing-with-hmrc",
                  "tax/court-claims-debt-bankruptcy", "tax/inheritance-tax"]),
    "driving": ("Driving: licences, health conditions and the Blue Badge",
                ["driving/disability-health-condition", "driving/driving-licences", "driving/learning-to-drive",
                 "driving/vehicle-tax-mot-insurance", "driving/penalty-points-fines-bans",
                 "driving/parking-public-transport-environment"]),
}
GOVUK_SKIP_TYPES = {"transaction", "local_transaction", "simple_smart_answer", "smart_answer", "place",
                    "completed_transaction", "licence", "finder", "special_route", "redirect"}


def govuk_body(d):
    """The HTML of a GOV.UK content item: its body, or each part of a multi-part guide with the part's title as a
    heading, or a start page's introduction and more information."""
    det = d.get("details") or {}
    if det.get("parts"):
        return "\n".join(f"<h2>{B.esc(p.get('title', ''))}</h2>\n{p.get('body', '')}" for p in det["parts"])
    pieces = [det.get(k, "") for k in ("introduction", "introductory_paragraph", "body", "more_information",
                                       "other_ways_to_apply", "what_you_need_to_know")]
    return "\n".join(x if isinstance(x, str) else "" for x in pieces)


def govuk_search(params, cache):
    """Every result of a GOV.UK search API query (1,000 a page)."""
    out, start = [], 0
    while True:
        query = urllib.parse.urlencode(dict(params, count=1000, start=start))
        data = json.loads(B.fetch(f"{GOVUK}/api/search.json?{query}", None))      # the list: fresh each time
        rows = data.get("results") or []
        out += rows
        start += len(rows)
        if len(rows) < 1000:
            return out


def govuk_content(link, cache):
    """The content API record of a GOV.UK page (its address path), or None when robots.txt refuses it or it
    cannot be read."""
    url = f"{GOVUK}/api/content{link}"
    if not B.allowed_by_robots(url, cache) or not B.allowed_by_robots(f"{GOVUK}{link}", cache):
        return None
    try:
        return json.loads(B.fetch(url, cache))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def govuk_guides_items(spec, piece, cache, left_out, today):
    """The GOV.UK guides of one topic: the pages listed under its browse pages (search API, filtered by browse page),
    each from the content API (whole multi-part guides, never the "/print" pages robots.txt refuses), grouped by
    browse page. Start pages of online services keep only their explanation."""
    _name, browse = GOVUK_TOPICS[piece]
    out, seen, failed = [], set(), 0
    for page in browse:
        unit = page.split("/")[-1].replace("-", " ").capitalize()
        rows = govuk_search({"filter_mainstream_browse_pages": page, "fields": "link,title,format"}, cache)
        for r in rows:
            link = r.get("link", "")
            if not link.startswith("/") or link in seen or r.get("format") in GOVUK_SKIP_TYPES:
                continue
            seen.add(link)
            d = govuk_content(link, cache)
            if d is None:
                failed += 1
                continue
            body = P.clean(govuk_body(d), f"{GOVUK}{link}")
            if not body:
                continue
            when = B.iso_date(d.get("public_updated_at") or d.get("first_published_at") or "")
            out.append(P.item(f"{GOVUK}{link}", d.get("title", link), when, body, unit))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} pages could not be read."})
    return out


UK_ALERT_KINDS = {
    "drug": ("Drug Safety Update (MHRA)", "drug_safety_update"),
    "medical": ("Medicine and medical device alerts (MHRA)", "medical_safety_alert"),
    "product": ("Product safety alerts, reports and recalls (Office for Product Safety and Standards)",
                "product_safety_alert_report_recall"),
}


def uk_alerts_items(spec, piece, cache, left_out, today):
    """The alerts of one kind published in one year ("drug-2026"): each alert's record from the content API, its
    text as published, newest first."""
    kind, _, year = piece.partition("-")
    _name, doc_type = UK_ALERT_KINDS[kind]
    rows = govuk_search({"filter_content_store_document_type": doc_type, "order": "-public_timestamp",
                         "filter_public_timestamp": f"from:{year}-01-01,to:{year}-12-31",
                         "fields": "link,title,public_timestamp"}, None)
    out, failed = [], 0
    for r in rows[:spec.get("limit", P.MAX_ITEMS)]:
        link = r.get("link", "")
        d = govuk_content(link, cache) if link.startswith("/") else None
        if d is None:
            failed += 1
            continue
        det = d.get("details") or {}
        meta = det.get("metadata") or {}
        when = B.iso_date(meta.get("issued_date") or d.get("first_published_at") or r.get("public_timestamp", ""))
        facts = "; ".join(f"{k.replace('_', ' ')}: {v if isinstance(v, str) else ', '.join(map(str, v))}"
                          for k, v in meta.items() if v and k not in ("bulk_published",))
        body = (f"<p>{B.esc(facts)}</p>\n" if facts else "") + P.clean(det.get("body", ""), f"{GOVUK}{link}")
        out.append(P.item(f"{GOVUK}{link}", d.get("title", link), when, body, P.month_unit(when)))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} alerts could not be read."})
    return out


# ====================================================================== USDA Farmers' Bulletins (Internet Archive)

def ia_collection_docs(collection, first, last, cache):
    """The texts of an Internet Archive collection published from year first to last (advancedsearch.php)."""
    out, page = [], 1
    while True:
        query = urllib.parse.urlencode([("q", f"collection:{collection} AND mediatype:texts AND year:[{first} TO "
                                              f"{last}]"), ("rows", 500), ("page", page), ("output", "json"),
                                        ("sort[]", "year asc")] +
                                       [("fl[]", f) for f in ("identifier", "title", "year", "date", "creator",
                                                              "rights", "licenseurl")])
        docs = (json.loads(B.fetch(f"{IA}/advancedsearch.php?{query}", None)).get("response") or {}).get("docs") or []
        out += docs
        if len(docs) < 500:
            return out
        page += 1


def _first(value):
    return str(value[0] if isinstance(value, list) and value else value or "")


def usda_public_domain(doc):
    """True when an Internet Archive record shows a USDA (US government) work or the holder's "not in copyright"
    statement."""
    words = " ".join(_first(doc.get(k)) for k in ("creator", "rights", "licenseurl"))
    return bool(re.search(r"Department of Agriculture|United States|not in copyright|publicdomain|public domain",
                          words, re.I))


def ia_text_url(ident, cache):
    """The address of an Internet Archive item's OCR text (its "_djvu.txt" file, whose name often differs from the
    item's: "farmbul0031_djvu.txt" in item CAT31124818), from the item's file list. Raises LookupError without one."""
    meta = json.loads(B.fetch(f"{IA}/metadata/{urllib.parse.quote(ident)}", cache))
    name = next((f.get("name", "") for f in meta.get("files") or [] if str(f.get("name", "")).endswith("_djvu.txt")), "")
    if not name:
        raise LookupError(f"{ident} has no OCR text")
    return f"{IA}/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(name)}"


def farmers_bulletin_items(spec, piece, cache, left_out, today):
    """The Farmers' Bulletins of one decade ("1940s"): each bulletin's OCR text from the Internet Archive."""
    first = int(piece[:4])
    out, failed, not_pd = [], 0, 0
    for doc in ia_collection_docs(spec["collection"], first, first + 9, cache)[:spec.get("limit", P.MAX_ITEMS)]:
        ident = str(doc.get("identifier") or "")
        if not usda_public_domain(doc):
            not_pd += 1
            continue
        try:
            text = B.fetch(ia_text_url(ident, cache), cache)
        except (urllib.error.URLError, OSError, ValueError, LookupError):
            failed += 1
            continue
        if len(text.split()) < 50:
            failed += 1
            continue
        year = _first(doc.get("year")) or _first(doc.get("date"))[:4]
        out.append(P.item(f"{IA}/details/{ident}", _first(doc.get("title")) or ident, B.iso_date(year) or year,
                          pre_html(text), year, byline=_first(doc.get("creator"))))
    if failed or not_pd:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} bulletins have no readable "
                         f"text; {not_pd} records do not show a US government work or public domain."})
    return out


# ====================================================================== the sources

SOURCES = {
    "canada_ogl": dict(
        group="government", driver="canada_ogl", series_title="Government of Canada publications (Open Government "
        "Licence)", subject="Government of Canada guides and reports", publisher="Government of Canada departments "
        "(from open.canada.ca)", country="Canada", licence="OGL-Canada", licence_url=OGL_CANADA_URL,
        source="https://open.canada.ca/en/search/ogp", licence_page=OGL_CANADA_URL,
        licence_text=r"Open Government Licence\s*[-\u2013\u2014]\s*Canada",
        description="Publications that Government of Canada departments released on open.canada.ca under the Open "
                    "Government Licence - Canada (commercial and non-commercial use allowed): their PDF documents, "
                    "one page each. The canada.ca web pages themselves are under other terms (non-commercial only) "
                    "and are not included.",
        notice="Contains information licensed under the Open Government Licence - Canada.",
        changes="each publication's PDF made into one web page (pictures left out)",
        pieces=lambda today: list(CANADA_TOPICS),
        piece_rule=r"^(" + "|".join(CANADA_TOPICS) + r")(-(19|20)\d\d)?$", limit=600),
    "gao_reports": dict(
        group="reports", driver="gao", series_title="GAO reports and decisions", subject="US government programs "
        "and spending", publisher="US Government Accountability Office (from govinfo.gov)", country="United States",
        licence=US_GOV, licence_url=US_GOV_URL, source="https://www.govinfo.gov/app/collection/gaoreports",
        licence_page="https://www.govinfo.gov/about/policies", licence_text=P.sources.GOVINFO_TEXT,
        description="The reports, testimonies and legal decisions of the Government Accountability Office, the "
                    "auditors of the US Congress, on Social Security, Medicare, veterans, education, defense and "
                    "every other federal program, as published in govinfo.gov's GAO Reports collection (1989 to "
                    "2008). One book per year.",
        notice="GAO reports are works of the US government, not under copyright in the United States; a report may "
               "reproduce third-party material, which keeps its own copyright.",
        changes="each report's text file made into a web page",
        pieces=lambda today: _years_between(2004, 2008), piece_rule=r"^(19[89]\d|200\d)$"),
    "us_government_manual": dict(
        group="government", driver="govman", series_title="The United States Government Manual",
        subject="US government agencies", publisher="Office of the Federal Register (from govinfo.gov)",
        country="United States", licence=US_GOV, licence_url=US_GOV_URL,
        source="https://www.govinfo.gov/app/collection/govman", licence_page="https://www.govinfo.gov/about/policies",
        licence_text=P.sources.GOVINFO_TEXT,
        description="The official handbook of the US federal government: what each branch, department, agency, "
                    "board and commission does, who leads it, and its addresses, phone numbers and websites.",
        changes="each entry's XML made into a web page",
        pieces=lambda today: [str(_this_year(today) - 1)], piece_rule=r"^(199[5-9]|20\d\d)$"),
    "eric_open": dict(
        group="journals", driver="eric", series_title="ERIC open full texts", subject="Education and disability",
        publisher="The documents' authors and publishers (from ERIC, the Education Resources Information Center, US "
        "Department of Education)", country="United States", licence="CC BY-NC",
        licence_url="https://creativecommons.org/licenses/by-nc/4.0/",
        source="https://eric.ed.gov/",
        description="Reports, guides and articles from ERIC whose own text says they are in the public domain or "
                    "under a Creative Commons licence that allows sharing changed copies (never NoDerivatives). "
                    "Each document's licence, authors and year are on its page: most are public domain or CC BY; the "
                    "book as a whole is marked not for commercial use because some of its documents are CC BY-NC.",
        changes="each document's PDF made into one web page (pictures left out)",
        pieces=lambda today: list(ERIC_TOPICS), piece_rule=r"^(" + "|".join(ERIC_TOPICS) + r")$",
        candidates=800, limit=400),
    "govuk_guides": dict(
        group="consumer", driver="govuk_guides", series_title="GOV.UK guides", subject="UK government guides", publisher="UK Government (GOV.UK)", country="United Kingdom",
        licence="OGL-UK-3.0", licence_url=OGL_UK_URL, source=f"{GOVUK}/browse",
        licence_page=f"{GOVUK}/help/terms-conditions", licence_text=r"Open Government Licence",
        description="GOV.UK's guides on one topic, every page whole (each part of a multi-part guide): caring and "
                    "power of attorney, pensions and Access to Work, housing and renting, tax and debt, or driving.",
        notice="Contains public sector information licensed under the Open Government Licence v3.0.",
        changes="made into web pages from GOV.UK's content API",
        pieces=lambda today: list(GOVUK_TOPICS), piece_rule=r"^(" + "|".join(GOVUK_TOPICS) + r")$"),
    "uk_safety_alerts": dict(
        group="health", driver="uk_alerts", series_title="UK safety alerts",
        subject="UK safety alerts", publisher="Medicines and Healthcare products "
        "Regulatory Agency and Office for Product Safety and Standards (GOV.UK)", country="United Kingdom",
        licence="OGL-UK-3.0", licence_url=OGL_UK_URL, source=f"{GOVUK}/drug-device-alerts",
        licence_page=f"{GOVUK}/help/terms-conditions", licence_text=r"Open Government Licence",
        description="The MHRA's Drug Safety Update articles, its medicine recalls and medical device alerts, and the "
                    "UK's product safety alerts and recalls, as published on GOV.UK. One book per kind and year.",
        notice="Contains public sector information licensed under the Open Government Licence v3.0. Safety alerts "
               "go out of date: check GOV.UK for the current advice.",
        changes="made into web pages from GOV.UK's content API",
        pieces=lambda today: [f"{k}-{y}" for k in UK_ALERT_KINDS for y in
                              (str(_this_year(today)), str(_this_year(today) - 1))],
        piece_rule=r"^(" + "|".join(UK_ALERT_KINDS) + r")-20\d\d$"),
    "usda_farmers_bulletins": dict(
        group="science", driver="farmers_bulletins", collection="usda-farmersbulletin",
        series_title="USDA Farmers' Bulletins", subject="Farming, gardening, food preservation and household skills",
        publisher="US Department of Agriculture (from the Internet Archive's copies, National Agricultural Library)",
        country="United States", licence=US_GOV, licence_url=US_GOV_URL,
        source=f"{IA}/details/usda-farmersbulletin",
        description="The USDA's practical booklets for farm and home: crops and gardens, livestock and poultry, "
                    "food preservation, cooking, sewing, building and household skills. One book per decade.",
        notice="These bulletins are old. Their advice on canning, food safety, pesticides, medicines and machinery is "
               "often UNSAFE by today's standards: never follow their canning times or chemical advice; use the "
               "USDA Complete Guide to Home Canning and current extension advice instead.",
        changes="each bulletin's machine-read (OCR) text made into a web page",
        pieces=lambda today: ["1950s", "1940s", "1930s"], piece_rule=r"^(18|19)\d0s$"),
}
for _name, _spec in SOURCES.items():
    _spec["name"] = _name

DRIVERS = {"canada_ogl": canada_ogl_items, "gao": gao_items, "govman": govman_items, "eric": eric_items,
           "govuk_guides": govuk_guides_items, "uk_alerts": uk_alerts_items, "farmers_bulletins": farmers_bulletin_items}

ALL_PIECES = {
    "canada_ogl": lambda t: list(CANADA_TOPICS),
    "gao_reports": lambda t: _years_between(1989, 2008),
    "us_government_manual": lambda t: [str(_this_year(t) - 1)],
    "eric_open": lambda t: list(ERIC_TOPICS),
    "govuk_guides": lambda t: list(GOVUK_TOPICS),
    "uk_safety_alerts": lambda t: [f"{k}-{y}" for y in _years_between(2007, _this_year(t)) for k in UK_ALERT_KINDS],
    "usda_farmers_bulletins": lambda t: [f"{d}s" for d in range(1990, 1880, -10)],
}

LICENCE_LINES = {
    "canada_ogl": "open.canada.ca/en/open-government-licence-canada: \"You are encouraged to use the Information that "
                  "is available under this licence with only a few conditions\" ... \"use for any lawful purpose\", "
                  "commercial included; attribution \"Contains information licensed under the Open Government "
                  "Licence – Canada.\" Every record read has license_id ca-ogl-lgo (checked for each). The canada.ca "
                  "web pages' own terms (canada.ca/en/transparency/terms.html) allow non-commercial reproduction "
                  "only, so their HTML pages are not taken. open.canada.ca's robots.txt does not restrict /data/api/.",
    "gao_reports": "govinfo.gov/about/policies: 17 U.S.C. 105 (works of the US government are not under copyright). "
                   "govinfo's robots.txt lists the GAOREPORTS sitemaps; /content/pkg/ is not disallowed.",
    "us_government_manual": "govinfo.gov/about/policies (17 U.S.C. 105); robots.txt lists the GOVMAN sitemaps.",
    "eric_open": "Each document's own licence statement, read from its PDF by the builder: \"This report is in the "
                 "public domain\" (US Department of Education reports) or a Creative Commons licence without "
                 "NoDerivatives. ERIC's full-text permission (e_fulltextauth) lets ERIC show a document; it is not a "
                 "licence to repackage it, so documents without their own open statement are not taken. "
                 "eric.ed.gov/robots.txt: \"User-agent: * Disallow:\"; files.eric.ed.gov has no robots.txt (404); "
                 "api.ies.ed.gov (the documented ERIC API) answers /robots.txt with 403 \"Missing Authentication "
                 "Token\" (no robots file: RFC 9309 treats an unavailable robots.txt as no rules).",
    "govuk_guides": "www.gov.uk/help/terms-conditions: \"Most content on GOV.UK is subject to Crown copyright "
                    "protection and is published under the Open Government Licence (OGL)\". GOV.UK's search and "
                    "content APIs are public; robots.txt disallows only the \"/print\" pages and site search.",
    "uk_safety_alerts": "The same GOV.UK terms (Open Government Licence v3.0) and APIs as govuk_guides.",
    "usda_farmers_bulletins": "archive.org collection usda-farmersbulletin (National Agricultural Library): items by "
                              "the US Department of Agriculture, rights \"The contributing institution believes that "
                              "this item is not in copyright\" (checked for each record).",
}

NOT_INCLUDED = [
    ("Canadian publication records that link only web pages (canada.ca, the departments' sites, the Transportation "
     "Safety Board's report pages)", "The web pages are under their sites' own terms (non-commercial reproduction "
     "only); only the PDF documents of Open Government Licence records are taken."),
    ("ERIC documents without their own open licence statement (for example the Journal of Visual Impairment & "
     "Blindness articles)", "ERIC is allowed to show them, which is not a licence to repackage them."),
    ("GAO reports after 2008", "govinfo.gov's GAO Reports collection ends in 2008; gao.gov itself was not checked "
     "for programs in this pass."),
    ("NASA Special Publications and Tech Briefs (NTRS)", "Not built in this pass (public domain, but NTRS marks "
     "third-party material per record; to be checked record by record)."),
]


# ====================================================================== registration in periodicals.py

def register(module):
    """Add these sources to the periodicals builder (module: periodicals). They are NOT added to the hourly backfill
    order: the owner asks for them by key (pub:canada_ogl, pub:gao_reports:2005 ...)."""
    for name, spec in SOURCES.items():
        module.SOURCES.setdefault(name, spec)
        # Their groups ("government", "consumer", "health", "science") join the periodicals' own (pub:<group> keys).
        module.GROUPS.setdefault(spec["group"], module.sources.GROUPS[spec["group"]])
    module.DRIVERS.update(DRIVERS)
    for name, pieces in ALL_PIECES.items():
        module.ALL_PIECES.setdefault(name, pieces)
    module.LICENCE_LINES.update(LICENCE_LINES)
    for row in NOT_INCLUDED:
        if row not in module.NOT_INCLUDED:
            module.NOT_INCLUDED.append(row)


_old_piece_label = P.piece_label


def piece_label(name, piece):
    """How a piece of these sources is named in its book's title ("Health and safety (...)", "drug alerts, 2026")."""
    if name == "canada_ogl":
        topic, _, year = piece.partition("-")
        return CANADA_TOPICS[topic][0] + (f", {year}" if year else "")
    if name == "eric_open":
        return ERIC_TOPICS[piece][0]
    if name == "govuk_guides":
        return GOVUK_TOPICS[piece][0]
    if name == "uk_safety_alerts":
        kind, _, year = piece.partition("-")
        return f"{UK_ALERT_KINDS[kind][0]}, {year}"
    if name == "us_government_manual":
        return f"{piece} edition"
    return _old_piece_label(name, piece)


if P.piece_label is not piece_label and getattr(P.piece_label, "__module__", "") != __name__:
    P.piece_label = piece_label
register(P)
