"""The repositories of the reference-directory inventory (2026-11-21) that come in pieces by date or by subject,
added to the periodicals builder (periodicals.py: its SOURCES, DRIVERS, ALL_PIECES, LICENCE_LINES and NOT_INCLUDED)
when it is imported, like publications_more.py. Keys pub:<source>:<piece>; directory_sources.expand_keys("directory")
asks for their default pieces, and ALL_PIECES lists every piece back to the beginning.

  Open-access journals (CC BY; CC0), each article whole, from Europe PMC's official REST API (its full-text XML),
  filtered by the journal's ISSN and by each article's OWN licence (never a publisher's site: MDPI and BioMed Central
  refuse programs): the disability and assistive-technology journals (African Journal of Disability, JMIR
  Rehabilitation and Assistive Technologies, Disabilities, Journal of Rehabilitation and Assistive Technologies
  Engineering), the eye journals (Journal of Ophthalmic & Vision Research, Journal of Ophthalmology, BMC
  Ophthalmology), ageing and rehabilitation (JMIR Aging, Frontiers in Aging, Frontiers in Rehabilitation Sciences,
  Journal of Rehabilitation Medicine, Geriatrics), emergency medicine (Western Journal of Emergency Medicine), public
  health and nutrition (Frontiers in Public Health, PLOS Global Public Health, BMC Public Health, Journal of Patient
  Experience, Frontiers in Nutrition, International Journal of Behavioral Nutrition and Physical Activity). Pieces:
  journal and year (or quarter or month for the big ones, so a piece stays under 4 hours at Europe PMC's Crawl-delay
  of 10 seconds). Personal use only: the Indian Journal of Ophthalmology (CC BY-NC-SA), the same way.
  The Journal of Science Education for Students with Disabilities (CC BY), from RIT's OAI-PMH feed, each article's
  PDF made into one page.
  GovInfo (public domain): the Federal Register's final rules, one book a month, from govinfo's bulk data (the daily
  issues' XML); the Congressional Record, one book a month, every granule of every daily issue (govinfo's MODS records
  and text files); congressional hearings on disability, blindness and related subjects, one book a year (every
  hearing of the year's govinfo sitemap whose title or subjects name them).
  Wikinews in English (CC BY 2.5; public domain before 2005-09-25), one book a year, from the official XML dump
  (dumps.wikimedia.org): the wiki's own API is disallowed by its robots.txt and not used.
  Frontiers for Young Minds (CC BY), one book a year, from kids.frontiersin.org's article pages (its sitemap).
  The Internet Archive's text collections the inventory marked "include in full", chosen by subject: American
  Libraries, Canadian Libraries, the Library of Congress, California Digital Library, Boston Public Library and the
  New York Public Library (items published before 1931 only, in the US public domain, marked old), and FEDLINK,
  Democracy's Library and US Government Documents (US government works). Personal use only: the Medical Heritage
  Library, Wellcome Library, JSTOR Early Journal Content, Periodicals (before 1931), Internet Archive Books (before
  1931), Community Texts and Folkscanomy (items with an open licence address), the Canadian Government Publications
  Portal and the University of Toronto's government publications (Crown copyright: personal use).
  Personal use only, from the journals' own OAI-PMH feeds: Disability Studies Quarterly, the Canadian Journal of
  Disability Studies and Disability, CBR and Inclusive Development (CC BY-NC-ND: each article whole and unchanged),
  the Journal of Accessibility and Design for All (CC BY-NC) and the Developmental Disabilities Network Journal (CC
  BY-NC-SA).

Every request obeys the host's robots.txt (and its Crawl-delay) through build_textbooks.allowed_by_robots, and a
host whose robots.txt shuts out AI companies' readers or says ai-train=no is not read (directory_sources.ai_refused).
"""

import bz2
import calendar
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
import publications_more as PM  # noqa: E402

US_GOV, US_GOV_URL = P.US_GOV, P.US_GOV_URL
GOVINFO = "https://www.govinfo.gov"
EPMC_API = P.EPMC_API
IA = "https://archive.org"
CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
OLD_PD = "Public domain (published before 1931)"
# The Government of Canada's terms for its publications (canada.ca/en/transparency/terms.html: "Information on this
# site ... has been posted with the intent that it be readily available for personal and public non-commercial use and
# may be reproduced, in part or in whole and by any means, without charge or further permission"): a non-commercial
# licence for the builder (sources.ALLOWED), used only for the personal-use Canadian collections.
CROWN_NC = "Crown copyright (Canada), non-commercial reproduction"
OLD_NOTE = ("Old works (published before 1931): kept for their history and their words, but their facts, advice, "
            "laws, medicine and safety practices are out of date, and some of their language is offensive today. The "
            "text was read by a scanner (OCR) and has its mistakes.")


def _ai_refused(url, cache=None):
    import directory_sources                     # here, not at the top: directory_sources imports the builder
    return directory_sources.ai_refused(url, cache)


def _this_year(today=None):
    return (today or datetime.date.today()).year


def _months_back(first_year, today=None, skip_current=False):
    """"YYYY-MM" from this month (or last month) back to January of first_year, newest first."""
    t = today or datetime.date.today()
    y, m = t.year, t.month
    if skip_current:
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    out = []
    while y >= first_year:
        out.append(f"{y}-{m:02d}")
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return out


def _years_back(first_year, today=None, skip_current=False):
    """Years as strings from this year (or last year) back to first_year, newest first."""
    year = _this_year(today) - (1 if skip_current else 0)
    return [str(y) for y in range(year, first_year - 1, -1)]


def piece_dates(piece):
    """(first day, last day) of a piece: "2026" a year, "2026-q3" a quarter, "2026-11" a month."""
    m = re.fullmatch(r"(\d{4})(?:-(q[1-4]|\d\d))?", piece)
    if not m:
        raise ValueError(f"not a date piece: {piece}")
    year, part = int(m.group(1)), m.group(2)
    if not part:
        return f"{year}-01-01", f"{year}-12-31"
    if part.startswith("q"):
        q = int(part[1])
        first, last = 3 * q - 2, 3 * q
        return f"{year}-{first:02d}-01", f"{year}-{last:02d}-{calendar.monthrange(year, last)[1]:02d}"
    month = int(part)
    return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"


# ====================================================================== open-access journals through Europe PMC

# Each journal: (title, ISSNs, first year, splits, personal). splits: [(from year, "year" | "quarter" | "month")]:
# a piece is a year until the first split's year, then that unit (sized so a piece's articles are read in under 3.4
# hours at 10 seconds a request: about 1,200 articles at most).
JOURNALS = {
    "african_journal_of_disability": ("African Journal of Disability", ["2226-7220", "2223-9170"], 2012, [], False,
                                      "Disability"),
    "jmir_rehabilitation_assistive_tech": ("JMIR Rehabilitation and Assistive Technologies", ["2369-2529"], 2014, [],
                                           False, "Disability and assistive technology"),
    "disabilities_mdpi": ("Disabilities (MDPI)", ["2673-7272"], 2021, [], False, "Disability"),
    "jrate": ("Journal of Rehabilitation and Assistive Technologies Engineering", ["2055-6683"], 2014, [], False,
              "Disability and assistive technology"),
    "western_journal_emergency_medicine": ("Western Journal of Emergency Medicine", ["1936-9018", "1936-900X"],
                                           2007, [], False, "Emergency medicine"),
    "journal_ophthalmic_vision_research": ("Journal of Ophthalmic & Vision Research", ["2008-322X", "2008-2010"],
                                           2008, [], False, "Eye health"),
    "journal_of_ophthalmology": ("Journal of Ophthalmology", ["2090-0058", "2090-004X", "2412-8740"], 2009, [], False,
                                 "Eye health"),
    "bmc_ophthalmology": ("BMC Ophthalmology", ["1471-2415"], 2001, [(2020, "quarter")], False, "Eye health"),
    "journal_rehabilitation_medicine": ("Journal of Rehabilitation Medicine", ["1651-2081", "1650-1977"], 2001, [],
                                        False, "Rehabilitation"),
    "frontiers_rehabilitation_sciences": ("Frontiers in Rehabilitation Sciences", ["2673-6861"], 2020, [], False,
                                          "Rehabilitation"),
    "geriatrics_mdpi": ("Geriatrics (MDPI)", ["2308-3417"], 2016, [], False, "Ageing"),
    "jmir_aging": ("JMIR Aging", ["2561-7605"], 2018, [], False, "Ageing"),
    "frontiers_aging": ("Frontiers in Aging", ["2673-6217"], 2020, [], False, "Ageing"),
    "journal_patient_experience": ("Journal of Patient Experience", ["2374-3743", "2374-3735"], 2014, [], False,
                                   "Patient experience and health care"),
    "ijbnpa": ("International Journal of Behavioral Nutrition and Physical Activity", ["1479-5868"], 2004, [],
               False, "Nutrition and physical activity"),
    "plos_global_public_health": ("PLOS Global Public Health", ["2767-3375"], 2021, [(2021, "quarter")], False,
                                  "Public health"),
    "frontiers_nutrition": ("Frontiers in Nutrition", ["2296-861X"], 2014, [(2019, "quarter"), (2021, "month")],
                            False, "Nutrition"),
    "frontiers_public_health": ("Frontiers in Public Health", ["2296-2565"], 2013, [(2017, "quarter"),
                                                                                     (2020, "month")], False,
                                "Public health"),
    "bmc_public_health": ("BMC Public Health", ["1471-2458"], 2001, [(2008, "quarter"), (2016, "month")], False,
                          "Public health"),
    "indian_journal_ophthalmology": ("Indian Journal of Ophthalmology", ["1998-3689", "0301-4738"], 1953,
                                     [(2010, "quarter")], True, "Eye health"),
}


def journal_pieces(name, today=None):
    """Every piece of a journal, newest first ("2026", "2026-q3", "2026-11")."""
    _title, _issns, first, splits, _personal, _subject = JOURNALS[name]
    out = []
    for year in range(_this_year(today), first - 1, -1):
        unit = "year"
        for since, kind in splits:
            if year >= since:
                unit = kind
        if unit == "year":
            out.append(str(year))
        elif unit == "quarter":
            out += [f"{year}-q{q}" for q in (4, 3, 2, 1)]
        else:
            out += [f"{year}-{m:02d}" for m in range(12, 0, -1)]
    t = today or datetime.date.today()
    return [p for p in out if piece_dates(p)[0] <= t.isoformat()]


def journal_open(short):
    """True for an article licence an open journal book keeps: CC BY (any version) or CC0."""
    return P.open_enough(short)


def journal_personal(short):
    """True for an article licence a personal-use journal book keeps: CC BY, CC0, CC BY-NC, CC BY-NC-SA."""
    return P.open_enough(short) or bool(re.fullmatch(r"CC BY-NC(-SA)?( \d\.\d)?( IGO)?", short or ""))


def epmc_journal_items(spec, piece, cache, left_out, today):
    """Every article of one journal published in the piece's dates that Europe PMC holds in full text, each read
    from its JATS XML (periodicals.jats_article: the whole article, its references too) and kept only when its OWN
    licence is one this book may hold (journal_open, or journal_personal for a personal-use journal). Europe PMC's
    robots.txt asks 10 seconds between requests, which allowed_by_robots makes the builder keep."""
    title, issns, _first, _splits, personal, _subject = JOURNALS[spec["journal"]]
    first, last = piece_dates(piece)
    search = f"{EPMC_API}/search"
    if not B.allowed_by_robots(search, cache):
        left_out.append({"title": f"{title}, {piece}", "reason": "Europe PMC's robots.txt does not allow its API."})
        return []
    issn_q = " OR ".join(f'ISSN:"{x}"' for x in issns)
    query = f"({issn_q}) AND OPEN_ACCESS:y AND IN_EPMC:y AND FIRST_PDATE:[{first} TO {last}]"
    keep = journal_personal if personal else journal_open
    out, cursor, refused, seen = [], "*", 0, set()
    while len(out) < spec.get("limit", P.MAX_ITEMS):
        params = urllib.parse.urlencode({"query": query, "format": "json", "resultType": "lite", "pageSize": 100,
                                         "cursorMark": cursor, "sort": "P_PDATE_D desc"})
        data = json.loads(B.fetch(f"{search}?{params}", None))
        results = data.get("resultList", {}).get("result", [])
        for r in results:
            pmcid = r.get("pmcid")
            if not pmcid or pmcid in seen or len(out) >= spec.get("limit", P.MAX_ITEMS):
                continue
            seen.add(pmcid)
            try:
                art = P.jats_article(B.fetch(f"{EPMC_API}/{pmcid}/fullTextXML", cache))
            except (urllib.error.URLError, OSError, ET.ParseError):
                refused += 1
                continue
            if not keep(art["licence"]):
                refused += 1
                continue
            when, credit = P.epmc_credit(r, art)
            out.append(P.item(f"https://europepmc.org/article/PMC/{pmcid}", art["title"] or r.get("title", ""), when,
                              P.clean(art["body"], "https://europepmc.org/"), P.month_unit(when), byline=credit,
                              licence=art["licence"], licence_url=art["licence_url"] or
                              B._licence_address(art["licence"])))
        nxt = data.get("nextCursorMark")
        if not results or not nxt or nxt == cursor:
            break
        cursor = nxt
    if refused:
        left_out.append({"title": f"{title}, {piece}", "reason": f"{refused} articles were left out: their own "
                         "licence is not one this book may hold, or their text could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


def journal_spec(name):
    """The periodicals SOURCES entry of one journal."""
    title, issns, _first, _splits, personal, subject = JOURNALS[name]
    licence = "CC BY-NC-SA" if personal else "CC BY"
    return dict(
        group="journals", driver="dir_epmc_journal", journal=name, series_title=title, subject=subject,
        publisher=f"{title}: the articles' authors (from Europe PMC's open-access full texts)",
        country="International", licence=licence, licence_url=B._licence_address(licence + " 4.0") or CC_BY_4,
        source=f"https://europepmc.org/search?query=ISSN%3A%22{issns[0]}%22", personal_use=personal,
        description=f"Every article of {title} that Europe PMC holds in full text under "
                    + ("an open or non-commercial Creative Commons licence (CC BY, CC BY-NC, CC BY-NC-SA or CC0), for "
                       "personal use only" if personal else "a Creative Commons Attribution licence (CC BY) or CC0")
                    + ", each article whole (its abstract, text, tables, figure captions and references). Each "
                      "article's authors, date, DOI and own licence are on its page.",
        changes="each article's full-text XML made into a web page, the figures as their captions",
        pieces=lambda today, n=name: journal_pieces(n, today)[:2],
        piece_rule=r"^(19|20)\d\d(-(q[1-4]|0[1-9]|1[0-2]))?$", catalogue_note="Research articles written for "
        "specialists; the plain-language summary, where an article has one, comes first.")


# ====================================================================== bepress Digital Commons (OAI-PMH): JSESD

def oai_records(base, params, cache=None, limit=5000):
    """Every OAI-PMH record of a ListRecords request ({identifier, datestamp, metadata dict of lists}), following
    resumption tokens."""
    out, query = [], dict(params, verb="ListRecords")
    while len(out) < limit:
        text = B.fetch(f"{base}?{urllib.parse.urlencode(query)}", None)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]", "", text)      # characters XML forbids
        text = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)    # a bare "&"
        root = ET.fromstring(text.encode("utf-8"))
        for rec in root.iter("{http://www.openarchives.org/OAI/2.0/}record"):
            head = rec.find("{http://www.openarchives.org/OAI/2.0/}header")
            if head is None or head.get("status") == "deleted":
                continue
            meta = {}
            for el in rec.iter():
                if el.tag.startswith("{http://purl.org/dc/elements/1.1/}"):
                    meta.setdefault(el.tag.split("}")[1], []).append(" ".join((el.text or "").split()))
            out.append({"identifier": head.findtext("{http://www.openarchives.org/OAI/2.0/}identifier", ""),
                        "datestamp": head.findtext("{http://www.openarchives.org/OAI/2.0/}datestamp", ""),
                        "meta": meta})
        token = root.find(".//{http://www.openarchives.org/OAI/2.0/}resumptionToken")
        if token is None or not (token.text or "").strip():
            return out
        query = {"verb": "ListRecords", "resumptionToken": token.text.strip()}
    return out


def oai_licence(meta):
    """(short licence, address) from a record's dc:rights (a Creative Commons address or words), ("", "")."""
    for r in meta.get("rights", []):
        url = re.search(r"https?://creativecommons\.org/\S+", r)
        short = B.licence_short(r, url.group(0) if url else "")
        if short and short != r.strip() or url:
            return short, (url.group(0).replace("http://", "https://") if url else B._licence_address(short))
    return "", ""


def bepress_items(spec, piece, cache, left_out, today):
    """The articles of one bepress journal (spec["oai"], spec["set"]): each record's PDF (its dc:identifier ending
    in .pdf) made into one page, kept only when its dc:rights licence is one the book may hold (spec["allowed"]:
    "open" for CC BY, CC BY-SA and CC0; "personal" adds the non-commercial ones). Piece "all", or a year."""
    out, closed = [], 0
    for rec in oai_records(spec["oai"], {"metadataPrefix": "oai_dc", "set": spec["set"]}, cache):
        if len(out) >= spec.get("limit", P.MAX_ITEMS):
            break
        meta = rec["meta"]
        date = B.iso_date((meta.get("date") or [rec["datestamp"]])[0])
        if piece != "all" and not date.startswith(piece):
            continue
        licence, licence_url = oai_licence(meta)
        kind = B.licence_kind(licence)
        if kind not in (("open", "share-alike", "non-commercial") if spec.get("allowed") == "personal" else
                        ("open", "share-alike")):
            closed += 1
            continue
        pdf = next((u for u in meta.get("identifier", []) if u.lower().endswith(".pdf") or "viewcontent" in u), "")
        page = next((u for u in meta.get("identifier", []) if u.startswith("http") and u != pdf), pdf)
        title = (meta.get("title") or [page])[0]
        if not pdf:
            closed += 1
            continue
        body, _pages = PM.pdf_item_body(pdf, cache, left_out, title)
        if not body:
            continue
        intro = "".join(f"<p>{B.esc(d)}</p>" for d in meta.get("description", [])[:1])
        authors = "; ".join(meta.get("creator", []))
        out.append(P.item(page, title, date, intro + body, date[:4], byline=authors, licence=licence,
                          licence_url=licence_url))
    if closed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{closed} records have no licence "
                         "this book may hold, or no PDF: not taken."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


def jsesd_items(spec, piece, cache, left_out, today):
    """The JSESD articles: RIT's PDFs answer programs with a bot check (Cloudflare "Just a moment...", 403, although
    robots.txt allows them), so each article's licence is read from RIT's OAI-PMH record (dc:rights) and its PDF from
    ERIC's copy (files.eric.ed.gov, which has no robots.txt rules; ERIC's documented API finds the journal's
    articles). An article is kept only when its OAI record says CC BY (or its own PDF states a Creative Commons
    licence that allows changes)."""
    licences = {}
    for rec in oai_records(spec["oai"], {"metadataPrefix": "oai_dc", "set": spec["set"]}, cache):
        title = " ".join(((rec["meta"].get("title") or [""])[0]).lower().split())
        licences[re.sub(r"\W+", " ", title).strip()] = oai_licence(rec["meta"])
    query = urllib.parse.urlencode({"search": f'source:"{spec["series_title"]}" AND e_fulltextauth:1',
                                    "format": "json", "rows": 500, "fields": "id,title,author,publicationdateyear,"
                                                                           "description"})
    docs = (json.loads(B.fetch(f"{PM.ERIC_API}?{query}", None)).get("response") or {}).get("docs") or []
    out, closed = [], 0
    for doc in docs:
        if len(out) >= spec.get("limit", P.MAX_ITEMS):
            break
        year = str(doc.get("publicationdateyear") or "")
        if piece != "all" and year != piece:
            continue
        eid, title = str(doc.get("id") or ""), html.unescape(str(doc.get("title") or ""))
        url = f"{PM.ERIC_FILES}{eid}.pdf"
        licence, licence_url = licences.get(re.sub(r"\W+", " ", title.lower()).strip(), ("", ""))
        if B.licence_kind(licence) not in ("open", "share-alike"):
            words, _n, _d = PM.pdf_front_words(url, cache)
            licence, licence_url = PM.eric_licence(words)
            if B.licence_kind(licence) not in ("open", "share-alike"):
                closed += 1
                continue
        body, _pages = PM.pdf_item_body(url, cache, left_out, title)
        if not body:
            continue
        intro = f"<p>{B.esc(html.unescape(str(doc.get('description') or '')))}</p>\n" if doc.get("description") else ""
        out.append(P.item(f"https://eric.ed.gov/?id={eid}", title, year, intro + body, year,
                          byline="; ".join(doc.get("author") or []), licence=licence, licence_url=licence_url))
    if closed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{closed} articles have no licence "
                         "record or statement that allows sharing changed copies: not taken."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== GovInfo: the Federal Register (bulk data)

FR_HEADINGS = {"HED": 2, "HD1": 3, "HD2": 4, "HD3": 5, "HD4": 6, "HD5": 6, "HD6": 6}
FR_SKIP = {"PRTPAGE", "STARS", "GID", "BILCOD", "FILED"}


def fr_html(el, depth=2):
    """A Federal Register XML element (a RULE and its parts) as HTML: headings (HD by its SOURCE level), paragraphs
    (P, FP, AMDPAR), section numbers and subjects as headings, tables (GPOTABLE) as tables, emphasis (E) as <em>,
    page markers left out; words unchanged."""
    tag = el.tag
    if tag in FR_SKIP:
        return B.esc(el.tail or "") if el.tail and tag == "PRTPAGE" else ""

    def inner(x):
        parts = [B.esc(x.text or "")]
        for child in x:
            parts.append(fr_html(child, depth))
            if child.tag not in FR_SKIP or child.tag == "PRTPAGE":
                parts.append(B.esc(child.tail or "") if child.tag != "PRTPAGE" else "")
        return "".join(parts)
    if tag == "HD":
        level = FR_HEADINGS.get(el.get("SOURCE", "HD1"), 3)
        return f"<h{level}>{inner(el)}</h{level}>"
    if tag in ("P", "FP", "AMDPAR", "PSPACE", "FTNT", "NOTE", "EXTRACT", "SIG", "NAME", "TITLE", "DATED", "FRDOC",
               "AUTH", "SOURCE", "EDNOTE"):
        text = inner(el).strip()
        if not text:
            return ""
        return text if re.search(r"<(p|h\d|table|ul)\b", text) else f"<p>{text}</p>"
    if tag in ("SECTNO",):
        return f"<h3>{inner(el)}</h3>"
    if tag == "SUBJECT" and depth > 2:
        return f"<p><strong>{inner(el)}</strong></p>"
    if tag in ("AGENCY", "SUBAGY", "CFR", "DEPDOC", "RIN", "SUBJECT"):
        return f"<p>{inner(el)}</p>"
    if tag in ("AGY", "ACT", "SUM", "DATES", "EFFDATE", "ADD", "FURINF", "SUPLINF", "PREAMB", "REGTEXT", "SECTION",
               "LSTSUB", "PART", "SUBPART", "APPENDIX", "CONTENTS"):
        return inner(el)
    if tag == "E":
        return f"<em>{inner(el)}</em>"
    if tag == "GPOTABLE":
        title = el.findtext("TTITLE") or ""
        rows = []
        head = [" ".join("".join(c.itertext()).split()) for c in el.iter("CHED")]
        if head:
            rows.append("<tr>" + "".join(f"<th>{B.esc(h)}</th>" for h in head) + "</tr>")
        for row in el.iter("ROW"):
            rows.append("<tr>" + "".join(f"<td>{B.esc(' '.join(''.join(c.itertext()).split()))}</td>"
                                         for c in row if c.tag == "ENT") + "</tr>")
        return (f"<p><strong>{B.esc(title)}</strong></p>" if title.strip() else "") + \
            ("<table>" + "".join(rows) + "</table>" if rows else "")
    if tag == "GPH":
        return "<p>[A graphic is printed here in the Federal Register.]</p>"
    return inner(el)


def fr_rule_item(rule, day, issue):
    """One final rule as an item: its subject as the title, its agency as the byline and contents part, the
    document number's address at the Federal Register as its original."""
    pre = rule.find("PREAMB")
    words = lambda x: " ".join("".join(x.itertext()).split()) if x is not None else ""   # noqa: E731
    agency = words(pre.find("AGENCY")) if pre is not None else ""
    subject = words(pre.find("SUBJECT")) if pre is not None else ""
    frdoc = words(rule.find(".//FRDOC"))
    number = (re.search(r"(\d{4}-\d{4,6})", frdoc) or re.search(r"()", "")).group(1)
    url = f"https://www.federalregister.gov/d/{number}" if number else f"{GOVINFO}/app/details/{issue}"
    title = subject or "Rule"
    return P.item(url, title, day, fr_html(rule), agency.title() if agency.isupper() else agency,
                  byline=" ".join(x for x in (agency.title() if agency.isupper() else agency, frdoc) if x))


def fr_items(spec, piece, cache, left_out, today):
    """The final rules (the RULES section) of every Federal Register issue of one month, from govinfo's bulk data
    (www.govinfo.gov/bulkdata/FR/<year>/<month>/FR-<date>.xml, one file per issue); days without an issue
    (weekends, holidays) answer 404 and are passed over."""
    first, last = piece_dates(piece)
    day = datetime.date.fromisoformat(first)
    end = min(datetime.date.fromisoformat(last), today or datetime.date.today())
    out, failed = [], 0
    while day <= end:
        if day.weekday() < 5:
            issue = f"FR-{day.isoformat()}"
            url = f"{GOVINFO}/bulkdata/FR/{day.year}/{day.month:02d}/{issue}.xml"
            if B.allowed_by_robots(url, cache):
                try:
                    root = ET.fromstring(B.fetch(url, cache, binary=True))
                except urllib.error.HTTPError as e:
                    root = None
                    failed += e.code != 404
                except (urllib.error.URLError, OSError, ET.ParseError):
                    root, failed = None, failed + 1
                if root is not None:
                    for rule in root.iter("RULE"):
                        if len(out) < spec.get("limit", P.MAX_ITEMS):
                            out.append(fr_rule_item(rule, day.isoformat(), issue))
        day += datetime.timedelta(days=1)
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} issues could not be read."})
    return out


# ====================================================================== GovInfo: the Congressional Record (by month)

MODS = "{http://www.loc.gov/mods/v3}"
XLINK = "{http://www.w3.org/1999/xlink}"


def govinfo_packages(collection, year, cache=None):
    """The package ids of one year of a govinfo collection, from its own sitemap (listed in govinfo's robots.txt)."""
    try:
        return PM.govinfo_sitemap(collection, year, cache)
    except urllib.error.HTTPError:
        return []


def crec_items(spec, piece, cache, left_out, today):
    """Every granule (speech, debate, Extensions of Remarks, Daily Digest) of every daily issue of the
    Congressional Record in one month: the issue's MODS record lists the granules with their text files, each read
    whole (its <pre> text as paragraphs). The parts are the days and the sections (Senate, House, Extensions of
    Remarks, Daily Digest)."""
    year, month = piece[:4], piece[5:7]
    days = sorted(p for p in govinfo_packages("CREC", year, cache) if p.startswith(f"CREC-{year}-{month}-"))
    out, failed = [], 0
    for pkg in days:
        date = pkg[5:]
        try:
            mods = ET.fromstring(B.fetch(f"{GOVINFO}/metadata/pkg/{pkg}/mods.xml", cache).encode("utf-8"))
        except (urllib.error.URLError, OSError, ET.ParseError):
            failed += 1
            continue
        for rel in mods.findall(f"{MODS}relatedItem[@type='constituent']"):
            title = " ".join("".join(rel.find(f"{MODS}titleInfo/{MODS}title").itertext()).split()) \
                if rel.find(f"{MODS}titleInfo/{MODS}title") is not None else ""
            part = rel.findtext(f"{MODS}titleInfo/{MODS}partName") or ""
            link = next((o.get(f"{XLINK}href") for o in rel.findall(f"{MODS}relatedItem[@type='otherFormat']")
                         if str(o.get(f"{XLINK}href", "")).endswith(".htm")), "")
            if len(out) >= spec.get("limit", 20000):
                break
            if not link or not B.allowed_by_robots(link, cache):
                continue
            try:
                text = B.fetch(link, cache)
            except (urllib.error.URLError, OSError):
                failed += 1
                continue
            pre = re.search(r"<pre>(.*?)</pre>", text, re.S)
            body = PM.pre_html(pre.group(1) if pre else re.sub(r"<[^>]+>", " ", text))
            out.append(P.item(link, title or link.rsplit("/", 1)[-1], date, body,
                              f"{P.month_unit(date)[:-5]} {int(date[8:])}, {date[:4]}: {part}".strip(": ")))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} parts could not be read."})
    return out


# ====================================================================== GovInfo: hearings on disability and blindness

HEARING_TOPICS = re.compile(
    r"disab|blind|visual(ly)?[- ]impair|low vision|deaf|hard of hearing|hearing loss|accessib|americans with "
    r"disabilities|\bADA\b|special education|individuals with disabilities education|supplemental security income|"
    r"\bSSI\b|vocational rehabilitation|independent living|braille|guide dog|service (animal|dog)|wheelchair|paraly|"
    r"autism|developmental(ly)? disab|intellectual(ly)? disab|mental retardation|rehabilitation act|"
    r"assistive technolog|caregiv|long-term care|section 508|closed caption", re.I)


def chrg_items(spec, piece, cache, left_out, today):
    """The congressional hearings of one year (govinfo's CHRG sitemap of that year) whose title or subjects name
    disability, blindness, deafness, accessibility or a related subject (HEARING_TOPICS), each hearing's whole
    printed transcript (its text file)."""
    out, failed, read = [], 0, 0
    for pkg in govinfo_packages("CHRG", piece, cache)[:spec.get("scan", 100000)]:
        if len(out) >= spec.get("limit", P.MAX_ITEMS):
            break
        try:
            mods_text = B.fetch(f"{GOVINFO}/metadata/pkg/{pkg}/mods.xml", cache)
            mods = ET.fromstring(mods_text.encode("utf-8"))
        except (urllib.error.URLError, OSError, ET.ParseError):
            failed += 1
            continue
        read += 1
        title = " ".join("".join(mods.find(f"{MODS}titleInfo/{MODS}title").itertext()).split()) \
            if mods.find(f"{MODS}titleInfo/{MODS}title") is not None else pkg
        subjects = " ".join(" ".join(s.itertext()) for s in mods.iter(f"{MODS}subject"))
        if not HEARING_TOPICS.search(f"{title} {subjects}"):
            continue
        date = B.iso_date(mods.findtext(f"{MODS}originInfo/{MODS}dateIssued") or "") or piece
        committee = ", ".join(dict.fromkeys(
            " ".join((n.findtext(f"{MODS}namePart") or "").split()) for n in mods.iter(f"{MODS}name")
            if n.get("type") == "corporate" and "Publishing Office" not in (n.findtext(f"{MODS}namePart") or "")))
        url = f"{GOVINFO}/content/pkg/{pkg}/html/{pkg}.htm"
        if not B.allowed_by_robots(url, cache):
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        pre = re.search(r"<pre>(.*?)</pre>", text, re.S)
        out.append(P.item(f"{GOVINFO}/app/details/{pkg}", title.title() if title.isupper() else title, date,
                          PM.pre_html(pre.group(1) if pre else re.sub(r"<[^>]+>", " ", text)), P.month_unit(date),
                          byline=" ".join(committee.split())))
    if failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} hearings could not be "
                         "read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== Wikinews (the XML dump)

WIKINEWS_DUMP = "https://dumps.wikimedia.org/enwikinews/latest/enwikinews-latest-pages-articles.xml.bz2"
WIKINEWS_PD_UNTIL = "2005-09-25"          # articles before this day are in the public domain, later ones CC BY 2.5
_WIKINEWS = {}


def strip_templates(text, keep=None):
    """Wikitext without its {{templates}} (nested ones too); keep(name, body) may return text to put instead."""
    out, i, depth, start = [], 0, 0, 0
    while i < len(text):
        if text.startswith("{{", i):
            if depth == 0:
                out.append(text[start:i])
                start = i
            depth += 1
            i += 2
            continue
        if text.startswith("}}", i) and depth:
            depth -= 1
            i += 2
            if depth == 0:
                inner = text[start + 2:i - 2]
                name = inner.split("|", 1)[0].strip().lower()
                out.append(keep(name, inner) if keep else "")
                start = i
            continue
        i += 1
    out.append(text[start:] if depth == 0 else "")
    return "".join(out)


def template_args(inner):
    """{name: value} of a template's named arguments."""
    args = {}
    for part in inner.split("|")[1:]:
        if "=" in part:
            k, v = part.split("=", 1)
            args[k.strip().lower()] = v.strip()
    return args


def wiki_inline(text):
    """Wikitext inline markup as HTML: links as their words, bold and italics, external links as their words."""
    text = B.esc(text)
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[(https?://[^\s\]]+)\s+([^\]]+)\]", r"\2", text)
    text = re.sub(r"\[(https?://[^\s\]]+)\]", r"\1", text)
    text = re.sub(r"'''(.+?)'''", r"<strong>\1</strong>", text)
    text = re.sub(r"''(.+?)''", r"<em>\1</em>", text)
    return text


def wikinews_html(wikitext):
    """(date, HTML) of one Wikinews article from its wikitext: {{date|...}} gives the date; {{source|...}} templates
    become the sources list; other templates, tables, files, categories, comments and references' markup are left
    out; headings, paragraphs and lists kept."""
    date = ""

    def keep(name, inner):
        nonlocal date
        if name == "date" and not date:
            date = B.iso_date(inner.split("|", 1)[1] if "|" in inner else "")
            return ""
        if name in ("source", "cite web", "cite news"):
            a = template_args(inner)
            words = ", ".join(x for x in (a.get("title", ""), a.get("author", ""), a.get("pub", "") or
                                          a.get("publisher", ""), a.get("date", "")) if x)
            return f"\n* {words}" + (f" ({a['url']})" if a.get("url") else "") + "\n"
        return ""
    text = re.sub(r"<!--.*?-->", "", wikitext, flags=re.S)
    text = re.sub(r"<ref\b[^>]*/>|<ref\b[^>]*>.*?</ref>", "", text, flags=re.S | re.I)
    text = strip_templates(text, keep)
    text = re.sub(r"\{\|.*?\|\}", "", text, flags=re.S)
    text = re.sub(r"\[\[(?:File|Image|Category|w:Category|[a-z]{2,3}):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", text,
                  flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    out, items = [], []

    def flush():
        if items:
            out.append("<ul>" + "".join(f"<li>{wiki_inline(x)}</li>" for x in items) + "</ul>")
            items.clear()
    for block in re.split(r"\n\s*\n", text):
        lines = [x for x in block.split("\n") if x.strip()]
        para = []
        for line in lines:
            h = re.match(r"^(={2,6})\s*(.*?)\s*=+\s*$", line)
            if h:
                if para:
                    out.append(f"<p>{wiki_inline(' '.join(para))}</p>")
                    para = []
                flush()
                level = min(len(h.group(1)), 6)
                out.append(f"<h{level}>{wiki_inline(h.group(2))}</h{level}>")
            elif re.match(r"^[*#:;]+", line):
                if para:
                    out.append(f"<p>{wiki_inline(' '.join(para))}</p>")
                    para = []
                items.append(re.sub(r"^[*#:;]+\s*", "", line))
            else:
                flush()
                para.append(line.strip())
        if para:
            out.append(f"<p>{wiki_inline(' '.join(para))}</p>")
        flush()
    return date, "\n".join(out)


def wikinews_articles(work):
    """[(title, date, html)] of every published English Wikinews article in the dump (downloaded once per job into
    work; the dump is the official bulk export, listed with no robots.txt rules)."""
    if "all" in _WIKINEWS:
        return _WIKINEWS["all"]
    path = os.path.join(work, "wikinews", os.path.basename(WIKINEWS_DUMP))
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = B.fetch(WIKINEWS_DUMP, None, binary=True)
        with open(path, "wb") as f:
            f.write(data)
    out = []
    ns = ""
    title = text = page_ns = ""
    with bz2.open(path, "rb") as f:
        for event, el in ET.iterparse(f, events=("end",)):
            tag = el.tag.rsplit("}", 1)[-1]
            if not ns and "}" in el.tag:
                ns = el.tag.split("}")[0] + "}"
            if tag == "title":
                title = el.text or ""
            elif tag == "ns":
                page_ns = el.text or ""
            elif tag == "text":
                text = el.text or ""
            elif tag == "page":
                if page_ns == "0" and re.search(r"\{\{\s*publish(ed)?\s*\}\}|\[\[Category:Published\]\]", text, re.I) \
                        and not re.match(r"#redirect", text, re.I):
                    date, body = wikinews_html(text)
                    if date and body:
                        out.append((title, date, body))
                el.clear()
    _WIKINEWS["all"] = out
    return out


def wikinews_items(spec, piece, cache, left_out, today):
    """The published Wikinews articles of one year, each with its date, its words and its sources, and its own
    licence (public domain before 2005-09-25, CC BY 2.5 after)."""
    work = os.path.join(cache or "build", "work")
    out = []
    for title, date, body in wikinews_articles(work):
        if not date.startswith(piece):
            continue
        pd = date < WIKINEWS_PD_UNTIL
        url = "https://en.wikinews.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        out.append(P.item(url, title, date, body, P.month_unit(date), byline="Wikinews contributors",
                          licence="PD" if pd else "CC BY 2.5",
                          licence_url="https://creativecommons.org/publicdomain/mark/1.0/" if pd else
                          "https://creativecommons.org/licenses/by/2.5/"))
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== Frontiers for Young Minds

FYM = "https://kids.frontiersin.org"


def fym_items(spec, piece, cache, left_out, today):
    """The Frontiers for Young Minds articles of one year (their DOIs name the year: 10.3389/frym.2019.00012), from
    the site's sitemap, each article page whole: the article, its glossary, references and the young reviewers'
    names, with its own licence line checked on the page (CC BY)."""
    if _ai_refused(FYM + "/", cache):
        left_out.append({"title": spec["series_title"], "reason": "The site shuts out AI companies' readers."})
        return []
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", B.fetch(f"{FYM}/sitemap.xml", None))
    urls = [u for u in locs if re.search(rf"/articles/10\.3389/frym\.{piece}\.", u)]
    out, closed, failed = [], 0, 0
    for url in urls[:spec.get("limit", P.MAX_ITEMS)]:
        if not B.allowed_by_robots(url, cache):
            continue
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            failed += 1
            continue
        if not re.search(r"Creative Commons Attribution License \(CC BY\)", text):
            closed += 1
            continue
        art = P.div_inner(text, r"<article\b[^>]*>") or text
        m = re.search(r'<meta[^>]+(?:name="citation_title"|property="og:title")[^>]+content="([^"]+)"', text)
        title = html.unescape(m.group(1)).split(" \u00b7 ")[0].strip() if m else B.first_heading(text)
        date = B.iso_date((re.search(r"Published online:\s*([A-Za-z]+ \d{1,2}, \d{4})", text) or
                           re.search(r"()", "")).group(1)) or piece
        authors = re.search(r'<meta name="citation_author" content="[^"]*"', text)
        names = "; ".join(re.findall(r'<meta name="citation_author" content="([^"]*)"', text)) if authors else ""
        out.append(P.item(url, title, date, P.clean(art, url), P.month_unit(date), byline=names,
                          licence="CC BY 4.0", licence_url=CC_BY_4))
    if closed or failed:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{closed} pages did not carry the CC "
                         f"BY licence line; {failed} could not be read."})
    out.sort(key=lambda i: i["date"], reverse=True)
    return out


# ====================================================================== the Internet Archive's collections

# Subjects (piece names) and the words searched in an item's subject and title.
IA_SUBJECTS = {
    "cookery": ("Cookery and food", "cookery OR cooking OR recipes OR cookbook* OR baking OR canning OR "
                "\"preserving\""),
    "household": ("Household skills", "\"home economics\" OR housekeeping OR household OR sewing OR dressmaking OR "
                  "laundry OR \"domestic economy\""),
    "health": ("Health, hygiene and first aid", "hygiene OR \"first aid\" OR nursing OR \"public health\" OR "
               "sanitation OR \"health\""),
    "trades": ("Trades and handicrafts", "carpentry OR woodwork* OR handicraft* OR blacksmith* OR plumbing OR "
               "masonry OR \"manual training\" OR knitting OR weaving OR basketry OR \"trades\""),
    "gardening": ("Gardening and farming", "gardening OR horticulture OR \"vegetable gardening\" OR poultry OR "
                  "beekeeping OR dairying"),
    "blindness": ("Blindness, braille and the education of the blind", "blind OR blindness OR braille OR \"education "
                  "of the blind\" OR \"Perkins Institution\" OR \"deaf and dumb\" OR deafness"),
    "consumer": ("Consumer and money guides", "consumer OR \"consumer protection\" OR budget OR \"family finance\" "
                 "OR insurance OR \"social security\""),
    "veterans": ("Veterans", "veterans OR \"veterans administration\" OR pensions"),
    "disability": ("Disability and rehabilitation", "disability OR disabled OR handicapped OR rehabilitation OR "
                   "\"vocational rehabilitation\" OR blind"),
    "extension": ("Farm and home (agricultural extension)", "\"agricultural extension\" OR \"extension service\" OR "
                  "\"farmers' bulletin\" OR \"home demonstration\" OR \"4-H\""),
    "medicine": ("History of medicine", "medicine OR medical OR surgery OR anatomy OR disease*"),
    "science": ("Science and natural history", "science OR physics OR chemistry OR botany OR zoology OR astronomy"),
    "literature": ("Literature", "fiction OR poetry OR drama OR essays"),
    "periodicals": ("Periodicals", "periodicals OR magazine*"),
}
# Collection -> (title, subjects, rule): "old" = items published before 1931 only (US public domain), "usgov" = US
# government works, "open" = items whose licence address is Creative Commons or public domain; personal = personal
# use only.
IA_COLLECTIONS = {
    "americana": ("American Libraries", ["cookery", "household", "health", "trades", "gardening", "blindness"],
                  "old", False),
    "toronto": ("Canadian Libraries", ["cookery", "household", "health", "trades", "gardening", "blindness"], "old",
                False),
    "library_of_congress": ("The Library of Congress", ["cookery", "household", "health", "trades", "gardening",
                                                        "blindness"], "old", False),
    "cdl": ("California Digital Library", ["cookery", "household", "health", "trades", "gardening", "blindness"],
            "old", False),
    "bostonpubliclibrary": ("Boston Public Library", ["cookery", "household", "health", "trades", "gardening",
                                                      "blindness"], "old", False),
    "newyorkpubliclibrary": ("New York Public Library", ["cookery", "household", "health", "trades", "gardening",
                                                         "blindness"], "old", False),
    "fedlink": ("FEDLINK: United States Federal Collection", ["health", "consumer", "veterans", "disability",
                                                              "extension"], "usgov", False),
    "democracys-library": ("Democracy's Library", ["health", "consumer", "veterans", "disability", "extension"],
                           "usgov", False),
    "USGovernmentDocuments": ("US Government Documents", ["health", "consumer", "veterans", "disability",
                                                          "extension"], "usgov", False),
    # personal use only (the inventory's verdict)
    "medicalheritagelibrary": ("Medical Heritage Library", ["health", "medicine", "blindness"], "old", True),
    "wellcomelibrary": ("Wellcome Library", ["health", "medicine", "blindness"], "old", True),
    "jstor_ejc": ("JSTOR Early Journal Content", ["science", "health", "blindness"], "old", True),
    "periodicals": ("Periodicals", ["periodicals", "household", "health"], "old", True),
    "internetarchivebooks": ("Internet Archive Books", ["cookery", "household", "health", "trades", "blindness",
                                                        "literature"], "old", True),
    "opensource": ("Community Texts", ["cookery", "household", "health", "trades", "blindness", "disability"], "open",
                   True),
    "folkscanomy": ("Folkscanomy: A Library of Books", ["cookery", "household", "health", "trades", "blindness"],
                    "open", True),
    "governmentpublications": ("Canadian Government Publications Portal", ["health", "consumer", "veterans",
                                                                            "disability"], "any", True),
    "uoftgovpubs": ("University of Toronto Government Publications", ["health", "consumer", "veterans",
                                                                      "disability"], "any", True),
}
IA_PER_PIECE = 250               # items in one piece (a piece with more says how many more match)
US_GOV_WORDS = re.compile(r"United States|U\.\s?S\.|\bDept\.|Department of|Bureau of|Office of|National Institute|"
                          r"Veterans Administration|Government Printing Office|Public Health Service|Extension Service|"
                          r"Congress|Senate|House of Representatives", re.I)


def _first(value):
    return str(value[0] if isinstance(value, list) and value else value or "")


def ia_search(query, fields, cache=None, rows=500, limit=5000):
    """The records of an Internet Archive advancedsearch query (the documented search API), the most read first (so
    a book that holds only part of a large subject holds the items people use most)."""
    out, page = [], 1
    while len(out) < limit:
        q = urllib.parse.urlencode([("q", query), ("rows", rows), ("page", page), ("output", "json"),
                                    ("sort[]", "downloads desc")] + [("fl[]", f) for f in fields])
        data = json.loads(B.fetch(f"{IA}/advancedsearch.php?{q}", None))
        docs = (data.get("response") or {}).get("docs") or []
        out += docs
        if len(docs) < rows:
            break
        page += 1
    return out


def ia_query(collection, subject):
    """The advancedsearch query of one collection and subject (texts only; the year limit of an "old" collection)."""
    _title, _subjects, rule, _personal = IA_COLLECTIONS[collection]
    words = IA_SUBJECTS[subject][1]
    q = (f"collection:({collection}) AND mediatype:texts AND (subject:({words}) OR title:({words})) AND "
         f"language:(eng OR English OR \"en\")")
    if rule == "old":
        q += " AND date:[1000-01-01 TO 1930-12-31]"
    if rule == "open":
        q += " AND licenseurl:(*creativecommons* OR *publicdomain*)"
    return q


def ia_item_allowed(doc, rule):
    """(True, licence, licence address) when an item may be taken under the collection's rule, else (False, ...)."""
    year = _first(doc.get("year")) or _first(doc.get("date"))[:4]
    lic = _first(doc.get("licenseurl"))
    if rule == "old":
        return (year.isdigit() and int(year) < 1931), OLD_PD, "https://www.copyright.gov/help/faq/faq-duration.html"
    if rule == "usgov":
        words = " ".join(_first(doc.get(k)) for k in ("creator", "publisher", "rights", "licenseurl"))
        if US_GOV_WORDS.search(words):
            return True, US_GOV, US_GOV_URL
        if year.isdigit() and int(year) < 1931:
            return True, OLD_PD, "https://www.copyright.gov/help/faq/faq-duration.html"
        return "publicdomain" in lic, "PD", "https://creativecommons.org/publicdomain/mark/1.0/"
    if rule == "open":
        short = B.licence_short("", lic) if "creativecommons.org/licenses" in lic else ("PD" if "publicdomain" in lic
                                                                                         else "")
        return bool(short and B.licence_kind(short)), short, lic.replace("http://", "https://")
    return True, CROWN_NC, "https://www.canada.ca/en/transparency/terms.html"


def ia_items(spec, piece, cache, left_out, today):
    """The items of one collection and subject ("cookery", from spec["collection"]): each item's OCR text
    (its _djvu.txt file) whole, with its title, author, year and Internet Archive address; at most IA_PER_PIECE."""
    collection, rule = spec["collection"], IA_COLLECTIONS[spec["collection"]][2]
    subject, _, page = piece.partition("-")
    page = int(page or 1)
    docs = ia_search(ia_query(collection, subject), ["identifier", "title", "year", "date", "creator", "publisher",
                                                     "rights", "licenseurl"], cache, limit=IA_PER_PIECE * page * 3)
    out, failed, refused, skip = [], 0, 0, IA_PER_PIECE * (page - 1)
    for doc in docs:
        if len(out) >= spec.get("limit", IA_PER_PIECE):
            break
        ok, licence, licence_url = ia_item_allowed(doc, rule)
        if not ok:
            refused += 1
            continue
        if skip:                                 # the items of the pages before this one
            skip -= 1
            continue
        ident = _first(doc.get("identifier"))
        try:
            text = B.fetch(PM.ia_text_url(ident, cache), cache)
        except (urllib.error.URLError, OSError, ValueError, LookupError):
            failed += 1
            continue
        if len(text.split()) < 200:
            failed += 1
            continue
        year = _first(doc.get("year")) or _first(doc.get("date"))[:4]
        out.append(P.item(f"{IA}/details/{ident}", _first(doc.get("title")) or ident, B.iso_date(year) or year,
                          PM.pre_html(text), (year[:3] + "0s") if year[:3].isdigit() else "",
                          byline=_first(doc.get("creator")),
                          licence=licence if rule != "any" else "", licence_url=licence_url))
    more = max(0, len(docs) - refused - failed - len(out))
    if failed or refused or more:
        left_out.append({"title": f"{spec['series_title']}, {piece}", "reason": f"{failed} items have no readable "
                         f"text; {refused} do not meet the collection's rule ({rule}); {more} more match beyond the "
                         f"{IA_PER_PIECE} a book holds (they are in the pieces {subject}-{page + 1} and on)."})
    return out


def ia_spec(collection):
    """The periodicals SOURCES entry of one Internet Archive collection."""
    title, subjects, rule, personal = IA_COLLECTIONS[collection]
    licence = {"old": OLD_PD, "usgov": US_GOV, "open": "CC BY-NC-SA", "any": CROWN_NC}[rule]
    notice = {"old": OLD_NOTE, "usgov": "Works of the US government (17 U.S.C. 105). Old ones are out of date: their "
              "advice on health, food safety, chemicals and farming may be unsafe today.",
              "open": "Each item's own licence (from its Internet Archive record) is on its page. Uploaded by members "
              "of the public: personal use only.",
              "any": "Government publications under Crown copyright or their publisher's terms: personal use only."}
    return dict(
        group="history" if rule == "old" else "government", driver="dir_ia", collection=collection,
        series_title=f"Internet Archive: {title}", subject=f"{title} (chosen subjects)",
        publisher=f"The items' authors and publishers (scanned by the Internet Archive's partners, collection "
                  f"\"{collection}\")", country="United States" if rule in ("old", "usgov") else "International",
        licence=licence, licence_url=US_GOV_URL if rule == "usgov" else
        "https://www.copyright.gov/help/faq/faq-duration.html" if rule == "old" else
        "https://www.canada.ca/en/transparency/terms.html" if rule == "any" else
        "https://creativecommons.org/licenses/by-nc-sa/4.0/", source=f"{IA}/details/{collection}",
        personal_use=personal, unchanged=False,
        description=f"Books and documents of the Internet Archive's collection \"{title}\" on one subject, each "
                    "item's whole machine-read text. " + {"old": "Only items published before 1931 (in the US public "
                                                          "domain) are taken.",
                                                          "usgov": "Only US government works are taken.",
                                                          "open": "Only items whose record gives a Creative Commons or "
                                                                  "public-domain licence address are taken.",
                                                          "any": "For personal use only."}[rule],
        notice=notice[rule], changes="each item's OCR text made into a web page",
        pieces=lambda today, s=subjects: list(s), piece_rule=r"^(" + "|".join(subjects) + r")(-\d{1,2})?$")


# ====================================================================== the sources

def _spec(**fields):
    return dict(fields)


SOURCES = {f"jnl_{name}": journal_spec(name) for name in JOURNALS}
SOURCES.update({
    "jsesd": _spec(
        group="journals", driver="dir_jsesd", oai="https://repository.rit.edu/do/oai/", set="publication:jsesd",
        allowed="open", series_title="Journal of Science Education for Students with Disabilities",
        subject="Science and mathematics teaching for students with disabilities", country="United States",
        publisher="Rochester Institute of Technology (RIT Digital Institutional Repository) and the articles' authors",
        licence="CC BY", licence_url=CC_BY_4, source="https://repository.rit.edu/jsesd/",
        description="Every article of the Journal of Science Education for Students with Disabilities (STEM teaching "
                    "for blind, deaf and disabled students) that its repository gives under a Creative Commons "
                    "Attribution licence and ERIC holds in full text, each article's PDF made into one page.",
        changes="each article's PDF made into a web page (pictures left out)",
        pieces=lambda today: ["all"], piece_rule=r"^(all|(19|20)\d\d)$"),
    "federal_register_rules": _spec(
        group="law", driver="dir_fr", series_title="Federal Register: final rules", subject="New US federal rules",
        publisher="Office of the Federal Register, National Archives (from govinfo.gov bulk data)",
        country="United States", licence=US_GOV, licence_url=US_GOV_URL,
        source="https://www.govinfo.gov/bulkdata/FR", licence_page="https://www.govinfo.gov/about/policies",
        licence_text=P.sources.GOVINFO_TEXT,
        description="Every final rule published in the Federal Register in one month (the RULES section of each daily "
                    "issue), whole: the agency, the CFR parts changed, the summary, dates, the explanation and the "
                    "changed regulation text. New rules on accessibility, Social Security, Medicare, FDA, FCC, "
                    "transportation and everything else. One book a month.",
        notice="The Federal Register is the US government's official daily publication of rules; the Code of Federal "
               "Regulations (in this library as law: books) is the rules as they stand. A rule's effective date is in "
               "its DATES paragraph.", changes="each rule's XML made into a web page",
        pieces=lambda today: _months_back(_this_year(today) - 1, today)[:3], piece_rule=r"^(19|20)\d\d-(0[1-9]|1[0-2])$"),
    "congressional_record": _spec(
        group="history", driver="dir_crec", series_title="Congressional Record", subject="US Congress: debates and "
        "proceedings", publisher="US Congress (from govinfo.gov)", country="United States", licence=US_GOV,
        licence_url=US_GOV_URL, source="https://www.govinfo.gov/app/collection/crec",
        licence_page="https://www.govinfo.gov/about/policies", licence_text=P.sources.GOVINFO_TEXT,
        description="Every part of every daily issue of the Congressional Record in one month: the Senate and House "
                    "proceedings and debates, Extensions of Remarks and the Daily Digest, each part whole as "
                    "printed. One book a month.", changes="each part's text file made into a web page",
        pieces=lambda today: _months_back(_this_year(today) - 1, today, True)[:2],
        piece_rule=r"^(199[4-9]|20\d\d)-(0[1-9]|1[0-2])$"),
    "hearings_disability": _spec(
        group="history", driver="dir_chrg", series_title="Congressional hearings on disability, blindness and "
        "accessibility", subject="Disability rights and programmes in Congress", publisher="US Congress committees "
        "(from govinfo.gov)", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
        source="https://www.govinfo.gov/app/collection/chrg", licence_page="https://www.govinfo.gov/about/policies",
        licence_text=P.sources.GOVINFO_TEXT,
        description="Every printed congressional hearing of one year whose title or subjects name disability, "
                    "blindness, deafness, accessibility, special education, Supplemental Security Income, vocational "
                    "rehabilitation, independent living or a related subject, each transcript whole (testimony, "
                    "statements and questions). One book a year.",
        notice="A hearing may reprint material from witnesses and others, which keeps its own copyright.",
        changes="each hearing's text file made into a web page",
        pieces=lambda today: _years_back(_this_year(today) - 2, today), piece_rule=r"^(19[5-9]\d|20\d\d)$"),
    "wikinews": _spec(
        group="news", driver="dir_wikinews", series_title="Wikinews (English)", subject="World news 2004 to 2026",
        publisher="Wikinews contributors (Wikimedia Foundation; from the official XML dump)", country="International",
        licence="CC BY 2.5", licence_url="https://creativecommons.org/licenses/by/2.5/",
        source="https://en.wikinews.org/", description="Every published English Wikinews article of one year, with its "
        "date and its list of sources. Wikinews, the free-content news site written by volunteers, closed in 2026; "
        "its archive is not in the Kiwix library. One book a year.",
        notice="Text from Wikinews (https://en.wikinews.org), by Wikinews contributors, under the Creative Commons "
               "Attribution 2.5 licence; articles before 25 September 2005 are in the public domain. Each article's "
               "own address and licence are on its page.",
        changes="each article's wikitext made into a web page (templates, pictures and tables left out; its sources "
                "kept)", catalogue_note="News ages fast: these stories are kept for reference.",
        pieces=lambda today: _years_back(2004, today)[:3], piece_rule=r"^20\d\d$"),
    "frontiers_young_minds": _spec(
        group="journals", driver="dir_fym", series_title="Frontiers for Young Minds", subject="Science for young "
        "readers", publisher="Frontiers Media and the articles' authors and young reviewers", country="International",
        licence="CC BY 4.0", licence_url=CC_BY_4, source=FYM + "/",
        description="Science explained for children and new readers by the scientists who did it, every article "
                    "reviewed by young people: one book a year, each article whole with its glossary and references.",
        changes="each article's web page made into a book page (pictures left out, their descriptions kept)",
        grades="Ages 8 to 15 (written for young readers)",
        pieces=lambda today: _years_back(2013, today)[:2], piece_rule=r"^20\d\d$"),
})
SOURCES.update({f"ia_{c.lower().replace('-', '_')}": ia_spec(c) for c in IA_COLLECTIONS})
for _name, _spec_ in SOURCES.items():
    _spec_["name"] = _name

DRIVERS = {"dir_epmc_journal": epmc_journal_items, "dir_bepress": bepress_items, "dir_jsesd": jsesd_items,
           "dir_fr": fr_items,
           "dir_crec": crec_items, "dir_chrg": chrg_items, "dir_wikinews": wikinews_items, "dir_fym": fym_items,
           "dir_ia": ia_items}

ALL_PIECES = {f"jnl_{name}": (lambda t, n=name: journal_pieces(n, t)) for name in JOURNALS}
ALL_PIECES.update({
    "jsesd": lambda t: ["all"],
    "federal_register_rules": lambda t: _months_back(2000, t),
    "congressional_record": lambda t: _months_back(1994, t, True),
    "hearings_disability": lambda t: _years_back(1957, t),
    "wikinews": lambda t: _years_back(2004, t),
    "frontiers_young_minds": lambda t: _years_back(2013, t),
})
# Each subject's first four pages of IA_PER_PIECE items (the most read first); later pages by key (cookery-5 ...).
ALL_PIECES.update({f"ia_{c.lower().replace('-', '_')}": (lambda t, s=v[1]: [f"{x}-{n}" if n > 1 else x for n in
                                                                           range(1, 5) for x in s])
                   for c, v in IA_COLLECTIONS.items()})


def _month_sign(spec, piece):
    """A monthly refresh: the pieces of a list that grows (journals, Frontiers for Young Minds, the IA's subjects)."""
    return datetime.date.today().strftime("%Y-%m")


def _closed_sign(spec, piece):
    """A finished piece (a past month of the Federal Register or Congressional Record, a past year of hearings or
    Wikinews): never rebuilt unless it is the current one, which is rebuilt each week."""
    today = datetime.date.today()
    current = piece in (today.strftime("%Y-%m"), str(today.year))
    return today.isoformat() if current else "closed"


EXTRA_SIGNS = {"dir_epmc_journal": _month_sign, "dir_bepress": _month_sign, "dir_jsesd": _month_sign,
               "dir_fr": _closed_sign,
               "dir_crec": _closed_sign, "dir_chrg": _closed_sign, "dir_wikinews": lambda s, p: "closed",
               "dir_fym": _month_sign, "dir_ia": _month_sign}


def default_keys(personal=False, today=None):
    """The default piece keys of these sources (the open ones, or with personal=True the personal-use ones)."""
    keys = []
    for name, spec in SOURCES.items():
        if bool(spec.get("personal_use")) == personal:
            keys += [f"pub:{name}:{p}" for p in spec["pieces"](today)]
    return keys


def all_piece_keys(personal=False, today=None):
    """Every piece key of these sources back to their beginnings (open ones, or personal-use ones)."""
    keys = []
    for name, spec in SOURCES.items():
        if bool(spec.get("personal_use")) == personal:
            keys += [f"pub:{name}:{p}" for p in ALL_PIECES[name](today)]
    return keys


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "dir_journals": "Each article's own <license> in its Europe PMC full-text XML (for example \"This is an open-access "
                    "article distributed under the terms of the Creative Commons Attribution License (CC BY)\"); "
                    "articles under any other licence are left out (the Indian Journal of Ophthalmology, personal use "
                    "only, also keeps CC BY-NC and CC BY-NC-SA). The journals' own sites are never read. "
                    "www.ebi.ac.uk/robots.txt: \"User-agent: * Crawl-Delay: 10\" (obeyed).",
    "jsesd": "Each JSESD record's dc:rights in RIT's OAI-PMH feed (repository.rit.edu/do/oai/): "
             "\"http://creativecommons.org/licenses/by/4.0/\". robots.txt allows /do/oai/ and the PDFs, but RIT's PDFs "
             "answer programs with Cloudflare's bot check (403 \"Just a moment...\"), so the PDFs are ERIC's copies "
             "(files.eric.ed.gov, no robots.txt rules; found through ERIC's documented API).",
    "govinfo_fr_crec_chrg": "govinfo.gov/about/policies: 17 U.S.C. 105 (works of the US government are not under "
                            "copyright). govinfo's robots.txt disallows only Drupal's system folders and /search/; its "
                            "sitemaps list the CREC and CHRG packages; /bulkdata/ is GPO's Bulk Data Repository.",
    "wikinews": "en.wikinews.org: \"All text created after September 25, 2005 available under the terms of the "
                "Creative Commons Attribution 2.5 License\" (earlier text public domain). Read only from "
                "dumps.wikimedia.org (no robots.txt: 404), the official XML dump; the wiki's own /w/api.php is "
                "disallowed by its robots.txt and not used.",
    "frontiers_young_minds": "Every Frontiers for Young Minds article page: \"This is an open-access article "
                             "distributed under the terms of the Creative Commons Attribution License (CC BY)\" "
                             "(checked on each page); kids.frontiersin.org/robots.txt allows all and lists its "
                             "sitemap.",
    "ia_collections": "archive.org/robots.txt disallows only /control/ and /report/. American Libraries, Canadian "
                      "Libraries, the Library of Congress, CDL, Boston and New York Public Library: only items whose "
                      "year is before 1931 (US public domain, checked per item). FEDLINK, Democracy's Library and US "
                      "Government Documents: only items whose creator or publisher is a US government body (or with a "
                      "public-domain mark). Personal-use collections as the inventory judged them.",
}

NOT_INCLUDED = [
    ("Journal of Disability Research (ScienceOpen)", "CC BY, but www.scienceopen.com's robots.txt says ai-train=no "
     "and shuts out ClaudeBot and anthropic-ai, so it is not read; Europe PMC holds none of its articles in full text "
     "(searched by ISSN 2676-2633)."),
    ("International Journal of Disability and Social Justice (Pluto Journals)", "CC BY, but Pluto Journals publishes "
     "it on a shop site with no OAI-PMH feed or API, and Europe PMC holds none of its articles (ISSN 2732-4044); not "
     "built."),
    ("Social Inclusion (Cogitatio Press)", "CC BY; Europe PMC holds none of its articles in full text (ISSN "
     "2183-2803) and Cogitatio's site gives no OAI-PMH feed that answered on 2026-11-21; not built yet."),
    ("Scandinavian Journal of Disability Research", "CC BY, but sjdr.se's robots.txt disallows the site."),
    ("Federal Register notices and proposed rules", "Only the final rules are built (the inventory asked for new "
                                                     "rules); notices number tens of thousands a year."),
]


def register(module):
    """Add these sources to the periodicals builder (module: periodicals). They are NOT added to the hourly backfill
    order: the owner asks for them by key (directory_sources' "directory" word asks for the default pieces)."""
    module.sources.ALLOWED.setdefault(CROWN_NC, "non-commercial")
    for name, spec in SOURCES.items():
        module.SOURCES.setdefault(name, spec)
        module.GROUPS.setdefault(spec["group"], module.sources.GROUPS[spec["group"]])
    module.DRIVERS.update(DRIVERS)
    for name, pieces in ALL_PIECES.items():
        module.ALL_PIECES.setdefault(name, pieces)
    module.LICENCE_LINES.update(LICENCE_LINES)
    if not hasattr(module, "EXTRA_SIGNS"):
        module.EXTRA_SIGNS = {}
    module.EXTRA_SIGNS.update(EXTRA_SIGNS)
    for row in NOT_INCLUDED:
        if row not in module.NOT_INCLUDED:
            module.NOT_INCLUDED.append(row)


_old_make_book = P.make_book
_old_piece_label = P.piece_label


def make_book(name, piece, items):
    """periodicals.make_book, then the fields these sources add: personal use, grade level, the practice note's
    country, and the version (what was read and when)."""
    book = _old_make_book(name, piece, items)
    spec = P.SOURCES.get(name, {})
    if name in SOURCES:
        book.personal_use = bool(spec.get("personal_use"))
        book.grades = spec.get("grades", "")
        book.version = f"read {datetime.date.today().isoformat()} ({len(items)} items)"
        if spec.get("driver") == "dir_ia" and IA_COLLECTIONS[spec["collection"]][2] == "old":
            book.published = B.newest_date([i["date"] for i in items])
    return book


def piece_label(name, piece):
    """How a piece of these sources is named in its book's title."""
    if name.startswith("ia_") and name in SOURCES:
        subject, _, page = piece.partition("-")
        return IA_SUBJECTS.get(subject, (subject,))[0] + (f", part {page}" if page else "")
    if name in SOURCES and re.fullmatch(r"\d{4}-q[1-4]", piece):
        return f"{piece[:4]}, quarter {piece[-1]}"
    if name in SOURCES and re.fullmatch(r"\d{4}-\d\d", piece):
        y, m = piece.split("-")
        return f"{calendar.month_name[int(m)]} {y}"
    if name == "jsesd" and piece == "all":
        return "all articles"
    return _old_piece_label(name, piece)


if getattr(P.make_book, "__module__", "") != __name__:
    P.make_book = make_book
if getattr(P.piece_label, "__module__", "") != __name__:
    P.piece_label = piece_label
register(P)
