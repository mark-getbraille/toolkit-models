"""Benefits and tax manuals for the reference library, in the group "benefits" ("Reference, benefits and tax
manuals"), the owner's request of 2026-11-22. Keys: benefits (every book here), ben:poms (all of the POMS),
ben:iom (all of the CMS manuals), ben:irm (all of the Internal Revenue Manual), and one book each:
ben:poms:<piece>, ben:iom:<publication>, ben:irm:<part>.

What this module builds, in plain words, each IN FULL (every section the agency publishes), all of them works of the
US government and so in the public domain:

  The Social Security Administration's Program Operations Manual System (POMS), the manual SSA's own staff use to
    decide claims for retirement, survivors, disability (SSDI) and Supplemental Security Income (SSI), with HALLEX
    (the hearings and appeals manual) and the legal opinion precedents. Read section by section from SSA's public
    policy site, secure.ssa.gov/poms.nsf (its robots.txt allows /poms.nsf/ and /apps10/; no AI rules). It is split
    by part, and the biggest parts (GN, DI) by chapter, so that each build job reads fewer than about 2,000
    sections (one request a second: well under the four hours a job may take).
  The Centers for Medicare & Medicaid Services' Internet-Only Manuals (IOMs): the Medicare manuals (general
    information and eligibility, benefit policy, national coverage determinations, claims processing, secondary
    payer, financial management, program integrity, managed care, prescription drugs and the rest), the State
    Operations Manual and the Medicaid Program Integrity Manual. One book per manual, one part per chapter (its PDF,
    read from www.cms.gov, whose robots.txt allows the manual pages and their Downloads folder), one page per
    section of the chapter's bookmarks.
  The Internal Revenue Service's Internal Revenue Manual (IRM), the IRS's own procedures (examinations, collection,
    taxpayer advocate, customer accounts, penalties and more): one book per part, one page per IRM section, read
    from www.irs.gov/irm (robots.txt allows /irm/; no AI rules).

Not built, with the reason and the index address for the owner's Program Downloader (NOT_INCLUDED): the VA's
M21-1 Adjudication Procedures Manual (KnowVA is a script-only site behind a gateway that answers no robots.txt and
offers no public data service), Medicaid.gov's guidance (the site refuses programs), and the old State Medicaid
Manual (old Word files).

Every book has its licence and notice, "published" (the newest effective or transmittal date read), "version" (what
was read and when), the key and fingerprint for the weekly update check (sign()), and "originals" (every page or
PDF read, with may_download from the licence and robots.txt). Requests go one at a time with a pause
(build_textbooks.fetch: at least a second, or the Crawl-delay a site asks for).

refs_common.REGISTRY sends the ben: keys here (the builder, the weekly check and sources.py ask it). This module
imports the builder only inside its functions, because the builder imports sources. Run from the repository's folder:
  python3 textbooks/benefits_manuals.py ben:poms:vb --out build/textbooks
  python3 textbooks/benefits_manuals.py ben:irm:4 --out build/textbooks --limit 3      (a small test)
  python3 textbooks/benefits_manuals.py --list benefits
"""

import argparse
import datetime
import hashlib
import html
import os
import re
import sys
import time
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_common as R  # noqa: E402

US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"

GROUP = "benefits"
GROUPS = {GROUP: "Reference, benefits and tax manuals"}
WORDS = ("benefits", f"group:{GROUP}", "ben:poms", "ben:iom", "ben:irm")


def _book(name, title, subject, publisher, source, description, notice):
    """A new Book of this group (US government, public domain)."""
    import build_textbooks as B
    return B.Book(name=name, title=title, subject=subject, level="reference", group=GROUP, publisher=publisher,
                  country="United States", licence=US_GOV, licence_url=US_GOV_URL, source=source,
                  description=description, notice=notice)


def _date(mdy):
    """"05/12/2009" or "September 25, 2020" -> "2009-05-12" ("" when it is not a date)."""
    for fmt in ("%m/%d/%Y", "%B %d, %Y", "%m-%d-%Y"):
        try:
            return datetime.datetime.strptime(mdy.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return ""


# ====================================================================== SSA POMS

POMS_SITE = "https://secure.ssa.gov"
POMS_APP = f"{POMS_SITE}/apps10/poms.nsf"
POMS_HOME = f"{POMS_APP}/partlist!OpenView"
POMS_CHANGES = f"{POMS_SITE}/apps10/reference.nsf/instructiontypecode!openview&restricttocategory=POMT"
SSA = "US Social Security Administration (SSA)"
POMS_NOTICE = ("A work of the US Social Security Administration (not under copyright in the United States). The POMS "
               "is SSA's internal instruction to its staff; it changes often (each section shows its effective "
               "dates), and the law and regulations come first: check the section's current text at "
               "secure.ssa.gov/poms.nsf before relying on it.")

# Each book: its key piece, the POMS part's category number and code, the chapters it holds (first and last chapter
# number, both included) and its title. The section counts (2026-11-22) are in the comments: at most about 2,000 a
# book, so that each build job ends well within its four hours.
POMS_BOOKS = [
    dict(piece="rm", part="01", code="RM", chapters=(0, 999), title="Records Maintenance (RM)"),            # 674
    dict(piece="gn-1", part="02", code="GN", chapters=(0, 16), title="General (GN), chapters 001 to 016: "
         "evidence, filing, representation, claims and benefit payments"),                                   # 1,254
    dict(piece="gn-2", part="02", code="GN", chapters=(17, 22), title="General (GN), chapters 017 to 022: "
         "overpayments, underpayments, appeals and the Social Security number"),                             # 1,412
    dict(piece="gn-3", part="02", code="GN", chapters=(23, 999), title="General (GN), chapters 023 to 060: "
         "reviews, hearings, disclosure, international and other general instructions"),                     # 1,495
    dict(piece="rs", part="03", code="RS", chapters=(0, 999), title="Retirement and Survivors Insurance (RS)"),  # 1,667
    dict(piece="di-1", part="04", code="DI", chapters=(0, 230), title="Disability Insurance (DI), chapters 001 to "
         "230: requirements, substantial gainful activity, claims, appeals, continuing disability and case "
         "development"),                                                                                     # 1,195
    dict(piece="di-2", part="04", code="DI", chapters=(231, 340), title="Disability Insurance (DI), chapters 235 "
         "to 340: medical evaluation, vocational issues, the sequential evaluation and DDS procedures"),      # 1,054
    dict(piece="di-3", part="04", code="DI", chapters=(341, 999), title="Disability Insurance (DI), chapters 341 "
         "to 900: the listings of impairments, quality review, the work incentives and other DI topics"),    # 1,324
    dict(piece="si", part="05", code="SI", chapters=(0, 999), title="Supplemental Security Income (SI)"),   # 1,690
    dict(piece="hi", part="06", code="HI", chapters=(0, 999), title="Health Insurance (HI): Medicare"),     # 922
    dict(piece="nl", part="09", code="NL", chapters=(0, 999), title="Notices, Letters and Paragraphs (NL)"),  # 1,076
    dict(piece="vb", part="14", code="VB", chapters=(0, 999), title="Special Veterans Benefits (VB)"),      # 254
    dict(piece="pr", part="15", code="PR", chapters=(0, 999), title="Title II Legal Opinion Precedents (PR)"),  # 1,761
    dict(piece="ps", part="16", code="PS", chapters=(0, 999), title="Title XVI Legal Opinion Precedents (PS)"),  # 309
    dict(piece="sl", part="19", code="SL", chapters=(0, 999), title="State and Local Coverage Handbook (SL)"),  # 153
    dict(piece="ha", part="25", code="HA", chapters=(0, 999), title="HALLEX: Hearings, Appeals and Litigation Law "
         "Manual (HA)"),                                                                                     # 758
    dict(piece="other", part=("08", "12", "13", "23", "24"), code="SM PM QR MS DX", chapters=(0, 999),
         title="Systems and Methods (SM), Program Management (PM), Quality Review (QR), Modernized Systems (MS) and "
               "Data Exchange (DX)"),                                                                       # 65
]
POMS_BY_PIECE = {b["piece"]: b for b in POMS_BOOKS}

CHAPTER_ROW = re.compile(r"class='chaptitletoc'>\s*([A-Z]{2}) (\d+):\s*<A HREF='[^']*restricttocategory=(\d+)'>([^<]*)",
                         re.I)
SUBLIST_ROW = re.compile(r"class=\"(subchaptitle|sectionTitle)\">(.*?)<br>", re.I | re.S)


def poms_parts(entry):
    """The part category numbers of a POMS book (one, or several for the book of small parts)."""
    return list(entry["part"]) if isinstance(entry["part"], tuple) else [entry["part"]]


def poms_chapters(entry, cache=None):
    """[(code, chapter number, category, chapter title)] of a POMS book: its parts' chapter lists, kept to its
    chapters."""
    import build_textbooks as B
    out = []
    lo, hi = entry["chapters"]
    for part in poms_parts(entry):
        text = B.fetch(f"{POMS_APP}/chapterlist!openview&restricttocategory={part}", cache)
        for code, number, category, title in CHAPTER_ROW.findall(text):
            if lo <= int(number) <= hi:
                out.append((code.upper(), int(number), category, html.unescape(title).strip()))
    return out


def poms_sections(chapter_list_html):
    """[(subchapter title, section code, section title, lnx id)] of one chapter's subchapter list, in order."""
    out, sub = [], ""
    for kind, inner in SUBLIST_ROW.findall(chapter_list_html):
        words = R.page_text(inner)
        if kind.lower() == "subchaptitle":
            sub = words
            continue
        m = re.search(r"/lnx/(\d+)", inner)
        code = re.match(r"([A-Z]{2} \d+\.\d+)", words)
        if m:
            title = words[len(code.group(1)):].lstrip(": ").strip() if code else words
            out.append((sub, code.group(1) if code else "", title, m.group(1)))
    return out


def poms_page(text):
    """(body HTML, effective-from date "YYYY-MM-DD", transmittal "TN 11 (01-22)") of one POMS section page."""
    m = re.search(r'<div class="poms">(.*?)</div>\s*<!--divBody-->', text, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r'<p[^>]*class="tninfo"[^>]*>.*?</p>', "", body, flags=re.S)
    body = re.sub(r"<h1\b.*?</h1>", "", body, count=1, flags=re.S)        # the section's title is the page's title
    body = re.sub(r'<a name="[^"]*">\s*</a>', "", body)                    # empty anchors: no empty links
    body = re.sub(r'<div class="poms-ul-mark">[^<]*</div>', "", body)      # the list's own bullet, said once
    eff = re.search(r"Effective Dates:(?:&nbsp;|\s)*(\d\d/\d\d/\d{4})", text)
    tn = re.search(r'class="tninfo">\s*([^<]+)<', text)
    return body, _date(eff.group(1)) if eff else "", (tn.group(1).strip() if tn else "")


def poms_book(entry, cache=None, left_out=None, limit=None):
    """The Book of one POMS piece: its chapters (one part each), every section a page (with its effective dates and
    transmittal), links between sections pointed at the book's own pages."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    if not R.readable(POMS_HOME, cache):
        left_out.append({"title": entry["title"], "reason": "secure.ssa.gov's robots.txt no longer allows reading "
                         "the POMS (or shuts out AI readers)."})
        return None
    book = _book(f"ssa_poms_{entry['piece'].replace('-', '_')}", f"SSA POMS: {entry['title']}",
                 "Social Security benefits: SSA's program operations manual", SSA,
                 f"{POMS_APP}/partlist!OpenView",
                 f"The Social Security Administration's Program Operations Manual System (POMS), {entry['title']}: "
                 "every section, in the manual's order, with its effective dates. The POMS is what SSA staff follow "
                 "to decide claims; it is public so claimants and their helpers can read the same rules.",
                 POMS_NOTICE)
    book.changes = "each section's web page made into a page of this book (the site's menus left out)"
    plan = []
    for n, (code, number, category, ctitle) in enumerate(poms_chapters(entry, cache), 1):
        listing = B.fetch(f"{POMS_APP}/subchapterlist!openview&restricttocategory={category}", cache)
        unit = f"{code} {number:03d}: {ctitle}"
        for sub, scode, stitle, lnx in poms_sections(listing):
            plan.append((n, unit, scode, stitle, lnx))
    if limit:
        plan = plan[:limit]
    links = {}
    for *_x, lnx in plan:
        for base in (f"{POMS_SITE}/poms.nsf/lnx/", f"{POMS_APP}/lnx/", "http://policy.ssa.gov/poms.nsf/lnx/",
                     "https://policy.ssa.gov/poms.nsf/lnx/"):
            links[base + lnx] = lnx
    dates, read = [], 0
    for n, unit, scode, stitle, lnx in plan:
        url = f"{POMS_SITE}/poms.nsf/lnx/{lnx}"
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            left_out.append({"title": f"{book.title}: {scode}", "reason": "It could not be read."})
            continue
        body, effective, tn = poms_page(text)
        if not R.page_text(body):
            continue
        facts = ", ".join(x for x in (f"effective {effective}" if effective else "", tn) if x)
        head = f"<p>{B.esc(scode)}{' (' + B.esc(facts) + ')' if facts else ''}. Source: <a href=\"{url}\">{url}</a></p>"
        book.pages.append(B.Page(lnx, f"{scode} {stitle}".strip(), head + B._Cleaner(links, url).clean(body), n, unit))
        book.originals.append({"url": url, "kind": "html"})
        dates.append(effective)
        read += 1
    book.published = B.newest_date([d for d in dates if d]) if any(dates) else ""
    book.version = f"POMS as published at secure.ssa.gov, {read} sections read {datetime.date.today().isoformat()}"
    return book


def poms_sign(entry):
    """The weekly check's sign of one POMS book: the rows of SSA's "POMS Recent Changes" list that fall in its
    chapters (instruction id, transmittal and date), so only the books that changed are rebuilt."""
    import build_textbooks as B
    text = R.page_text(B.fetch(POMS_CHANGES, None))
    codes = entry["code"].split()
    lo, hi = entry["chapters"]
    rows = []
    for code, sub, rest in re.findall(r"\b([A-Z]{2}) (\d{5}) ((?:TN \d+|BASIC) \d\d/\d\d/\d{4})", text):
        if code in codes and lo <= int(sub[:3]) <= hi:
            rows.append(f"{code} {sub} {rest}")
    return hashlib.sha256("\n".join(sorted(rows)).encode()).hexdigest()[:24] if rows else \
        hashlib.sha256(f"none {entry['piece']}".encode()).hexdigest()[:24]


# ====================================================================== CMS Internet-Only Manuals

CMS_SITE = "https://www.cms.gov"
CMS_IOM_INDEX = f"{CMS_SITE}/medicare/regulations-guidance/manuals/internet-only-manuals-ioms"
CMS = "Centers for Medicare & Medicaid Services (CMS), US Department of Health and Human Services"
CMS_NOTICE = ("A work of the Centers for Medicare & Medicaid Services (not under copyright in the United States). "
              "CMS revises its manuals through transmittals; check the chapter's current PDF at cms.gov before "
              "relying on it. CPT codes and descriptions that some chapters quote are © American Medical "
              "Association and are not CMS's to give: they are left as CMS printed them, for reference only.")
IOM_ITEMS = f"{CMS_SITE}/regulations-and-guidance/guidance/manuals/internet-only-manuals-ioms-items"

# (publication number, item page id, title). 100-12, 100-13 and 100-23 are "under development" and 100-19, 100-20
# and 100-21 hold no manual chapters (demonstrations, one-time notices, reserved): left out.
IOMS = [
    ("100-01", "cms050111", "Medicare General Information, Eligibility and Entitlement Manual"),
    ("100-02", "cms012673", "Medicare Benefit Policy Manual"),
    ("100-03", "cms014961", "Medicare National Coverage Determinations (NCD) Manual"),
    ("100-04", "cms018912", "Medicare Claims Processing Manual"),
    ("100-05", "cms019017", "Medicare Secondary Payer Manual"),
    ("100-06", "cms019018", "Medicare Financial Management Manual"),
    ("100-07", "cms1201984", "State Operations Manual"),
    ("100-08", "cms019033", "Medicare Program Integrity Manual"),
    ("100-09", "cms019034", "Medicare Contractor Beneficiary and Provider Communications Manual"),
    ("100-10", "cms019035", "Quality Improvement Organization Manual"),
    ("100-11", "cms019036", "Programs of All-Inclusive Care for the Elderly (PACE) Manual"),
    ("100-15", "cms1238527", "Medicaid Program Integrity Manual"),
    ("100-16", "cms019326", "Medicare Managed Care Manual"),
    ("100-17", "cms019466", "CMS/Business Partners Systems Security Manual"),
    ("100-18", "cms050485", "Medicare Prescription Drug Benefit Manual"),
    ("100-22", "cms1236946", "Medicare Quality Reporting Incentive Programs Manual"),
    ("100-24", "cms019212", "State Payment of Medicare Premiums"),
    ("100-25", "cms1248023", "Information Security Acceptable Risk Safeguards Manual"),
]
IOMS_BY_PUB = {pub: (pub, item, title) for pub, item, title in IOMS}
PDF_LINK = re.compile(r'<a\b[^>]*href="([^"]+\.pdf)"[^>]*>(.*?)</a>', re.I | re.S)


def iom_chapters(page_html, base):
    """[(chapter title, PDF address)] of a manual's page: its chapter PDFs in order (crosswalks, transmittal lists and
    the site's menu files left out)."""
    m = re.search(r"<main\b.*?</main>", page_html, re.S)
    main = m.group(0) if m else page_html
    out, seen = [], set()
    for href, label in PDF_LINK.findall(main):
        title = R.page_text(label)
        url = urllib.parse.urljoin(base, href)
        low = (title + " " + href).lower()
        if url in seen or "crosswalk" in low or "/agent/" in href or not re.search(r"chapter|appendix|exhibit|"
                                                                                    r"table of contents", low):
            continue
        seen.add(url)
        out.append((title, url))
    return out


def iom_book(pub, work, cache=None, left_out=None, limit=None):
    """The Book of one CMS manual: its page's chapter PDFs, each a part of the book, one page per section of the
    chapter's bookmarks (build_textbooks.pdf_pages_html, with "[Page n]" marks)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    pub, item, title = IOMS_BY_PUB[pub]
    page = f"{IOM_ITEMS}/{item}"
    if not R.readable(page, cache):
        left_out.append({"title": title, "reason": "www.cms.gov's robots.txt does not allow reading its page."})
        return None
    chapters = iom_chapters(B.fetch(page, cache), page)
    if limit:
        chapters = chapters[:max(1, limit // 10 or 1)]
    book = _book(f"cms_iom_{pub.replace('-', '_')}", f"{title} (CMS Pub. {pub})",
                 "Medicare and Medicaid: CMS program manuals", CMS, page,
                 f"CMS Publication {pub}, the {title}, one of the Internet-Only Manuals in which the Centers for "
                 "Medicare & Medicaid Services state Medicare and Medicaid policy and procedure: every chapter, "
                 "one part each, with the page numbers of the official PDF.", CMS_NOTICE)
    book.changes = "each chapter's PDF made into text pages, one per section (its pictures and layout left out)"
    folder = os.path.join(work, "cms")
    os.makedirs(folder, exist_ok=True)
    pdf_dates = []
    for n, (ctitle, url) in enumerate(chapters, 1):
        if not R.readable(url, cache):
            left_out.append({"title": f"{title}: {ctitle}", "reason": "Not allowed by robots.txt."})
            continue
        try:
            data = B.fetch(url, cache, binary=True)
        except (urllib.error.URLError, OSError):
            left_out.append({"title": f"{title}: {ctitle}", "reason": "Its PDF could not be read."})
            continue
        path = os.path.join(folder, f"{pub}-{n:02d}.pdf")
        with open(path, "wb") as f:
            f.write(data)
        try:
            parts = B.pdf_pages_html(path)
            pdf_dates.append(B.pdf_date(path))
        except Exception:  # noqa: BLE001 - a PDF that cannot be read
            left_out.append({"title": f"{title}: {ctitle}", "reason": "Its PDF could not be read as text."})
            continue
        for i, (stitle, body, first, last) in enumerate(parts, 1):
            if limit and len(book.pages) >= limit:
                break
            where = f"<p>{B.esc(ctitle)}, PDF pages {first} to {last}: <a href=\"{url}\">{url}</a></p>"
            book.pages.append(B.Page(B.slug(f"ch{n:02d}-{i:03d}-{stitle}", 70), stitle or ctitle, where + body, n,
                                     ctitle))
        book.originals.append({"url": url, "kind": "pdf", "size": len(data),
                               "sha256": hashlib.sha256(data).hexdigest()})
    book.published = B.newest_date([d for d in pdf_dates if d]) if any(pdf_dates) else ""
    book.version = f"chapter PDFs as published at cms.gov, read {datetime.date.today().isoformat()}"
    return book


def iom_sign(pub):
    """The weekly check's sign of one CMS manual: the list of its chapter PDFs and each PDF's ETag, date and size."""
    import build_textbooks as B
    import updates
    pub, item, _t = IOMS_BY_PUB[pub]
    page = f"{IOM_ITEMS}/{item}"
    parts = []
    for title, url in iom_chapters(B.fetch(page, None), page):
        time.sleep(B.PAUSE)
        parts.append(f"{title}|{url}|{updates.head_signs(url)}")
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()[:24]


# ====================================================================== IRS Internal Revenue Manual

IRM_INDEX = "https://www.irs.gov/irm"
IRS = "Internal Revenue Service (IRS), US Department of the Treasury"
IRM_NOTICE = ("A work of the Internal Revenue Service (not under copyright in the United States). The IRM is the "
              "IRS's instruction to its own employees; it is not law and cannot be cited as authority. Each section "
              "names its manual transmittal date; check irs.gov/irm for the current text.")
# The parts of the IRM (www.irs.gov/irm, read 2026-11-22) with their titles.
IRM_PARTS = [
    (1, "Organization, Finance and Management"), (2, "Information Technology"),
    (3, "Submission Processing"), (4, "Examining Process"), (5, "Collecting Process"),
    (6, "Human Resources Management"), (7, "Rulings and Agreements"), (8, "Appeals"),
    (9, "Criminal Investigation"), (10, "Security, Privacy and Assurance"), (11, "Communications and Liaison"),
    (13, "Taxpayer Advocate Service"), (20, "Penalty and Interest"), (21, "Customer Account Services"),
    (22, "Taxpayer Education and Assistance"), (25, "Special Topics"), (30, "Administrative"),
    (31, "Guiding Principles"), (32, "Published Guidance and Other Guidance to Taxpayers"), (33, "Legal Advice"),
    (34, "Litigation in District Court, Bankruptcy Court, Court of Federal Claims, and State Courts"),
    (35, "Tax Court Litigation"), (36, "Appellate Litigation and Actions on Decision"),
    (37, "Disclosure and Privacy Law"), (38, "General Legal Services"), (39, "Fiscal Law"),
]
IRM_BY_PART = {str(n): (n, t) for n, t in IRM_PARTS}


def irm_chapter_titles(part_html, part):
    """{"4.1": "4.1 Planning and Special Programs"} from a part page's lines (the chapter headings between links)."""
    out = {}
    plain = re.sub(r"<a\b.*?</a>", "\n", part_html, flags=re.S)
    plain = re.sub(r"<[^>]+>", "\n", plain)
    for line in html.unescape(plain).split("\n"):
        m = re.match(rf"^\s*({part}\.\d+) (\S.*?)\s*$", line)
        if m:
            out[m.group(1)] = f"{m.group(1)} {m.group(2)}"
    return out


def irm_page(text):
    """(body HTML, manual transmittal date "YYYY-MM-DD") of one IRM section page: the text of its article."""
    i = text.find('<article about="/irm/')
    j = text.find("</article>", i)
    body = text[i:j] if i >= 0 and j > i else ""
    m = re.search(r'<div class="clearfix text-formatted field field--name-body.*?>(.*)$', body, re.S)
    body = m.group(1) if m else body
    words = R.page_text(body[:20000])
    d = re.search(r"Manual Transmittal\s+([A-Z][a-z]+ \d{1,2}, \d{4})", words)
    return body, _date(d.group(1)) if d else ""


def irm_book(part, cache=None, left_out=None, limit=None):
    """The Book of one IRM part: every section listed on its page (www.irs.gov/irm/part<n>), one page each, grouped
    by chapter, with its manual transmittal date."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    number, ptitle = IRM_BY_PART[str(part)]
    page = f"{IRM_INDEX}/part{number}"
    if not R.readable(page, cache):
        left_out.append({"title": f"IRM Part {number}", "reason": "www.irs.gov's robots.txt does not allow reading "
                         "the IRM (or shuts out AI readers)."})
        return None
    part_html = B.fetch(page, cache)
    titles = irm_chapter_titles(part_html, number)
    links = re.findall(rf'href="((?:https://www\.irs\.gov)?/irm/part{number}/irm_[0-9a-z-]+)"[^>]*>([^<]*)', part_html)
    plan, seen = [], set()
    for href, label in links:
        url = urllib.parse.urljoin(IRM_INDEX, href)
        if url in seen:
            continue
        seen.add(url)
        label = html.unescape(label).strip()
        chap = ".".join(label.split(" ", 1)[0].split(".")[:2])
        plan.append((titles.get(chap, f"Chapter {chap}"), url, label))
    if limit:
        plan = plan[:limit]
    book = _book(f"irs_irm_part_{number:02d}", f"Internal Revenue Manual, Part {number}: {ptitle}",
                 "Federal taxes: the IRS's procedures (Internal Revenue Manual)", IRS, page,
                 f"Part {number} of the Internal Revenue Manual, {ptitle}: every section the IRS publishes, grouped "
                 "by chapter, each with its manual transmittal (the date of its last revision). The IRM is the "
                 "IRS's official compilation of its own policies and procedures.", IRM_NOTICE)
    book.changes = "each section's web page made into a page of this book (the site's menus left out)"
    link_map = {url: B.slug(url.rsplit("/", 1)[-1], 60) for _c, url, _t in plan}
    chapters, dates = {}, []
    for chapter, url, label in plan:
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            left_out.append({"title": f"IRM {label}", "reason": "It could not be read."})
            continue
        body, transmittal = irm_page(text)
        if not R.page_text(body):
            continue
        n = chapters.setdefault(chapter, len(chapters) + 1)
        head = (f"<p>IRM {B.esc(label)}{', manual transmittal ' + transmittal if transmittal else ''}. Source: "
                f"<a href=\"{url}\">{url}</a></p>")
        book.pages.append(B.Page(link_map[url], f"IRM {label}", head + B._Cleaner(link_map, url).clean(body), n,
                                 chapter))
        book.originals.append({"url": url, "kind": "html"})
        dates.append(transmittal)
    book.published = B.newest_date([d for d in dates if d]) if any(dates) else ""
    book.version = f"IRM Part {number} as published at irs.gov, read {datetime.date.today().isoformat()}"
    return book


def irm_sign(part):
    """The weekly check's sign of one IRM part: its page's list of sections (a new or revised section gets a new
    address, such as "irm_04-001-010r"), with the month, so a part is read again at least monthly."""
    import build_textbooks as B
    import directory_sources as D
    text = B.fetch(f"{IRM_INDEX}/part{part}", None)
    links = re.findall(rf'/irm/part{part}/irm_[0-9a-z-]+', text)
    return hashlib.sha256(("\n".join(links) + D.month_token()).encode()).hexdigest()[:24]


# ====================================================================== keys, signs, the build

def all_keys():
    """Every build key of this module, in the order of the docstring."""
    return [f"ben:poms:{b['piece']}" for b in POMS_BOOKS] + [f"ben:iom:{p}" for p, _i, _t in IOMS] + \
        [f"ben:irm:{n}" for n, _t in IRM_PARTS]


def knows(word):
    """True when word is one of this module's request words or keys."""
    return word in WORDS or word.startswith("ben:")


def expand_keys(words):
    """The keys the words stand for: "benefits" or "group:benefits" (every book), "ben:poms", "ben:iom", "ben:irm"
    (one manual's books), or one key (kept as it is)."""
    keys = []
    for w in words:
        if w in ("benefits", f"group:{GROUP}"):
            keys += all_keys()
        elif w in ("ben:poms", "ben:iom", "ben:irm"):
            keys += [k for k in all_keys() if k.startswith(w + ":")]
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change of one key ("" when it cannot be asked: then nothing is rebuilt)."""
    parts = key.split(":")
    try:
        if parts[1] == "poms" and parts[2] in POMS_BY_PIECE:
            return poms_sign(POMS_BY_PIECE[parts[2]])
        if parts[1] == "iom" and parts[2] in IOMS_BY_PUB:
            return iom_sign(parts[2])
        if parts[1] == "irm" and parts[2] in IRM_BY_PART:
            return irm_sign(parts[2])
    except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError):
        return ""
    return ""


def books_for(key, work, cache=None, left_out=None, limit=None):
    """The Books of one key (a list: one book here), or [] (the reason in left_out)."""
    left_out = left_out if left_out is not None else []
    parts = key.split(":")
    book = None
    if len(parts) == 3 and parts[1] == "poms" and parts[2] in POMS_BY_PIECE:
        book = poms_book(POMS_BY_PIECE[parts[2]], cache, left_out, limit)
    elif len(parts) == 3 and parts[1] == "iom" and parts[2] in IOMS_BY_PUB:
        book = iom_book(parts[2], work, cache, left_out, limit)
    elif len(parts) == 3 and parts[1] == "irm" and parts[2] in IRM_BY_PART:
        book = irm_book(parts[2], cache, left_out, limit)
    else:
        left_out.append({"title": key, "reason": "Unknown key."})
    return [book] if book is not None else []


def build(keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys into out_dir with one manifest per key (refs_common.build_keys)."""
    return R.build_keys(R._module("benefits_manuals"), keys, out_dir, cache, date, limit)  # (also when run as a script)


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "ssa_poms": "secure.ssa.gov (POMS): works of the US government (17 U.S.C. 105). robots.txt (read 2026-11-22): "
                "\"User-agent: *\" with \"Allow: /apps10/\", \"Allow: /poms/\", \"Allow: /poms.nsf/\"; no AI rules, "
                "no Crawl-delay. www.ssa.gov itself refuses programs and is not read.",
    "cms_iom": "www.cms.gov (Internet-Only Manuals): works of the US government (17 U.S.C. 105). robots.txt (read "
               "2026-11-22) disallows /media/, /node/, addresses with \"?\" and system folders; the manual pages and "
               "their /regulations-and-guidance/guidance/manuals/downloads/ PDFs are allowed; no AI rules.",
    "irs_irm": "www.irs.gov/irm: works of the US government (17 U.S.C. 105). robots.txt (read 2026-11-22) "
               "disallows searches, logins and system folders only; no AI rules.",
}

NOT_INCLUDED = [
    ("VA M21-1 Adjudication Procedures Manual (KnowVA)", "Public domain, but not readable under the owner's rules: "
     "KnowVA (www.knowva.ebenefits.va.gov) is a script-only site whose pages are drawn by a program in the browser; "
     "its robots.txt address answers \"Missing Authentication Token\" from a gateway, and the VA publishes no data "
     "service or bulk copy of the M21-1 (checked 2026-11-22). For personal use, the owner's Program Downloader can "
     "open it in a browser. Index: https://www.knowva.ebenefits.va.gov/system/templates/selfservice/va_ssnew/help/"
     "customer/locale/en-US/portal/554400000001018/topic/554400000004049/M21-1-Adjudication-Procedures-Manual"),
    ("Medicaid.gov guidance (State Medicaid Director letters, CMCS informational bulletins, the Medicaid and CHIP "
     "eligibility and benefits pages)", "Public domain, but www.medicaid.gov answers every program, its robots.txt "
     "included, with \"Access Denied\" (checked 2026-11-22). The Medicaid Program Integrity Manual (CMS Pub. 100-15) "
     "is built from cms.gov instead (ben:iom:100-15). Index for the Program Downloader: "
     "https://www.medicaid.gov/federal-policy-guidance/index.html"),
    ("State Medicaid Manual (CMS Pub. 45, paper-based)", "Public domain, but CMS publishes it only as zip files of "
     "old Word 97 documents (p45_01.zip and the rest, 2000 and later), which the builder cannot read as text. Index: "
     "https://www.cms.gov/regulations-and-guidance/guidance/manuals/paper-based-manuals-items/cms021927"),
    ("CMS IOM publications 100-12, 100-13, 100-19, 100-20, 100-21 and 100-23", "Not manuals (yet): 100-12 and 100-13 "
     "are \"under development\" (CMS says to use the paper State Medicaid Manual), 100-19 and 100-20 are lists of "
     "demonstration and one-time-notice transmittals, 100-21 is reserved and 100-23 is under development. Index: "
     "https://www.cms.gov/medicare/regulations-guidance/manuals/internet-only-manuals-ioms"),
    ("POMS archives, emergency messages and transmittals (secure.ssa.gov reference.nsf)", "Left out: the archives "
     "are superseded versions and the messages are short-lived instructions; the current POMS is built in full. "
     "Index: https://secure.ssa.gov/apps10/pomsarchive.nsf/partlistsorted!OpenView"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["benefits"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many pages")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
