"""Court opinions for the reference library (the owner's request of 2026-11-22): every opinion of the Supreme Court
of the United States, volume by volume, and landmark federal cases by subject (disability rights, consumer law,
housing, employment and family law), each with its court, date and citation. Keys: court:<name> and
court:usreports:<volume>. Request words: court-opinions (the index and the five subject books) and
court-opinions-scotus-1, court-opinions-scotus-2 and court-opinions-scotus-3 (the United States Reports, volumes 2
to 201, 202 to 401 and 402 to 586, so each word stays under 256 jobs). Groups: "Reference, court opinions" and
"Reference, court opinions: Supreme Court (United States Reports)".

Where the opinions come from, in plain words: govinfo.gov, the Government Publishing Office's official site. It
publishes the United States Reports (the Court's official reports, collection USREPORTS) with one PDF for each case
("granule" USREPORTS-<volume>-<first page>), and opinions of the federal courts of appeals and district courts
(collection USCOURTS, one PDF for each opinion or order of a case). Both are works of the US government (17 U.S.C.
105, the line checked on govinfo.gov's policies page at every build). For each volume the builder reads the
volume's MODS record (https://www.govinfo.gov/metadata/pkg/USREPORTS-<volume>/mods.xml): every case in it with its
name, citation ("347 U.S. 483") and decision date, and its PDF; front matter, indexes and tables are left out.
govinfo's robots.txt allows /metadata/ and /content/ and has no AI rules (checked 2026-11-22). The volumes listed
here are those of govinfo's USREPORTS sitemaps on 2026-11-22: 2 to 586, except 465 (not on govinfo then); volume 1
(Dallas's reports of Pennsylvania cases) is not in the collection.

What each book holds:
  - court:usreports:<volume>: every case of one volume of the United States Reports, each case one part titled with
    govinfo's case name, citation and decision date, its pages read whole from the official PDF (the syllabus, the
    Court's opinion and every concurring and dissenting opinion, as printed). Old volumes are scans whose text has
    the scanner's mistakes;
  - court:landmark_<subject>: landmark Supreme Court cases on one subject (from the same official PDFs) and, for
    disability rights, landmark federal court of appeals and district court opinions on accessibility for blind and
    deaf people (from govinfo's USCOURTS PDFs). Each part names the court, the decision date and the citation; the
    builder reads govinfo's record first and leaves out (in the manifest) any case whose record is not found or
    whose date does not match;
  - court:index: a guide to court opinions and case law in the library (CC0).
The landmark cases already in civics.py's book (civ:supreme_court_cases: Loving v. Virginia, Obergefell v. Hodges,
Olmstead v. L. C., Board of Education v. Rowley and others) are not repeated here; the subject books say so.

Not built (NOT_INCLUDED, with the reason): state court opinions (CourtListener's site and the Caselaw Access
Project's static site refuse programs in robots.txt; CourtListener's bulk opinions file is one 55 GB file, which the
Writing Kit downloads on the owner's own computer instead), Supreme Court volumes not yet on govinfo (such as 590,
Bostock v. Clayton County), and Oyez (CC BY-NC).

Run from the repository's folder:
  python3 textbooks/court_opinions.py court:usreports:347 --out build/textbooks --limit 5
  python3 textbooks/court_opinions.py --list court-opinions-scotus-2
"""

import datetime
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "court_opinions"
GROUP_SCOTUS = "court_opinions_scotus"
GROUPS = {GROUP: "Reference, court opinions",
          GROUP_SCOTUS: "Reference, court opinions: Supreme Court (United States Reports)"}

GOVINFO = "https://www.govinfo.gov"
NOT_ADVICE = K.NOT_LEGAL_ADVICE
SCAN_NOTE = "Old volumes are scans whose machine-read text has the scanner's mistakes."
SYLLABUS_NOTE = ("The syllabus printed at the head of a Supreme Court case is not part of the opinion; it is prepared "
                 "by the Reporter of Decisions for the reader's convenience.")
OPINION_NOTICE = ("Opinions of US courts, from the official PDFs on govinfo.gov (Government Publishing Office): works of "
                  "the US government (public domain). ")

# The volumes of the United States Reports on govinfo.gov (its USREPORTS sitemaps, read 2026-11-22): 2 to 586
# except 465. Volume 1 is Dallas's reports, mostly of Pennsylvania courts, and is not in the collection.
MISSING_VOLUMES = {465}
VOLUMES = [v for v in range(2, 587) if v not in MISSING_VOLUMES]
# The three request words for the volumes, each under the 256-job limit of a request word (sources.expand_keys).
SCOTUS_WORDS = {"court-opinions-scotus-1": (2, 201), "court-opinions-scotus-2": (202, 401),
                "court-opinions-scotus-3": (402, 586)}


# ====================================================================== govinfo's MODS records

def mods_url(package):
    """The address of a govinfo package's MODS record (its parts, names, dates and PDFs)."""
    return f"{GOVINFO}/metadata/pkg/{package}/mods.xml"


def _text(fragment):
    """The plain words of an XML fragment (tags dropped, entities read, spaces tidied)."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment or "")).split())


def granules(mods):
    """[{id, title, citation, date, kind, pdf, page, topics}] of the parts ("granules") in a govinfo MODS record, in
    the record's order. kind is govinfo's granuleClass ("CASE" for a case of the United States Reports; "" when the
    record does not say, as for court opinions)."""
    out = []
    pattern = r'<relatedItem type="constituent"[^>]*ID="id-([^"]+)"[^>]*>(.*?)(?=<relatedItem type="constituent"|</mods>)'
    for gid, body in re.findall(pattern, mods or "", re.S):
        title = re.search(r"<title>(.*?)</title>", body, re.S)
        pdf = re.search(r'xlink:href="([^"]+\.pdf)"', body)
        page = re.search(r'<identifier type="uri">([^<]+)</identifier>', body)
        cite = re.search(r'<identifier type="United States Reports citation">([^<]+)<', body) or \
            re.search(r"<usCitation>([^<]+)<", body)
        date = re.search(r"<decisionDate>([^<]+)<", body) or re.search(r"<dateIssued>([^<]+)<", body)
        kind = re.search(r"<granuleClass>([^<]+)<", body)
        topics = []
        for t in re.findall(r"<topic>([^<]+)</topic>", body):
            t = _text(t)
            if t and t not in topics:
                topics.append(t)
        out.append({"id": gid, "title": _text(title.group(1)) if title else gid,
                    "citation": _text(cite.group(1)) if cite else "", "date": date.group(1).strip() if date else "",
                    "kind": kind.group(1).strip() if kind else "", "pdf": pdf.group(1) if pdf else "",
                    "page": page.group(1).strip() if page else "", "topics": topics})
    return out


def read_mods(package, cache=None):
    """The MODS record of a package as text, or "" when govinfo does not have the package (it then sends its error
    page instead) or robots.txt does not allow reading it."""
    import build_textbooks as B
    url = mods_url(package)
    if not K.readable(url, cache):
        return ""
    text = B.fetch(url, cache)
    return text if "<mods" in text[:2000] else ""


def volume_cases(volume, cache=None):
    """The cases (granules of class CASE) of one volume of the United States Reports, in the volume's order."""
    return [g for g in granules(read_mods(f"USREPORTS-{volume}", cache)) if g["kind"].upper() == "CASE" and g["pdf"]]


def case_part(g):
    """(part title, PDF address, page address) of one case: govinfo's name and citation, and the decision date."""
    when = f", decided {date_words(g['date'])}" if g.get("date") else ""
    return f"{g['title']}{when}", g["pdf"], g["page"] or g["pdf"]


def date_words(iso):
    """"1954-05-17" -> "17 May 1954" (the text as given when it is not a date)."""
    try:
        d = datetime.date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso)
    return f"{d.day} {d.strftime('%B')} {d.year}"


# ====================================================================== the United States Reports, volume by volume

def volume_entry(volume, year=""):
    """The book entry of one volume (a US government PDF entry for pdf_set.pdf_set_book)."""
    return K.us_pdf(
        GROUP_SCOTUS, name=f"court_usreports_{volume}",
        title=f"United States Reports, volume {volume}" + (f" ({year})" if year else "") + ": every case",
        subject="Supreme Court opinions", publisher="Supreme Court of the United States (United States Reports, "
        "published by the Government Publishing Office on govinfo.gov)",
        source=f"{GOVINFO}/app/details/USREPORTS-{volume}",
        description=f"Every case in volume {volume} of the United States Reports, the official reports of the Supreme "
                    "Court of the United States, each read whole from its official PDF: the syllabus, the opinion of "
                    "the Court and every concurring and dissenting opinion, as printed. Each part is titled with the "
                    "case's name, its citation and the date it was decided.",
        notice=f"{OPINION_NOTICE}{SYLLABUS_NOTE} {SCAN_NOTE} {NOT_ADVICE}",
        version=f"United States Reports volume {volume} on govinfo.gov")


def usreports_book(name, work, cache=None, left_out=None, limit=None):
    """The book of one volume ("usreports:347"): every case, read with pdf_set.pdf_set_book."""
    import pdf_set
    left_out = left_out if left_out is not None else []
    volume = name.split(":", 1)[1]
    cases = volume_cases(volume, cache)
    if not cases:
        left_out.append({"title": f"United States Reports, volume {volume}", "reason": "govinfo.gov has no case "
                         "record for this volume now (or robots.txt does not allow reading it).",
                         "url": f"{GOVINFO}/app/collection/usreports"})
        return None
    year = cases[-1]["date"][:4]
    book = pdf_set.pdf_set_book(volume_entry(volume, year), [case_part(g) for g in cases], work, cache, left_out,
                                limit)
    if book is not None:
        book.published = cases[-1]["date"][:10]
        book.version = f"United States Reports volume {volume} on govinfo.gov, read {datetime.date.today().isoformat()}"
    return book


def usreports_sign(name):
    """The weekly sign of a volume: its number (a printed volume does not change)."""
    return K.sha("usreports", name)


# ====================================================================== landmark cases by subject

# A Supreme Court case: ("usr", volume, first page, note). A federal court opinion: ("usc", govinfo package, granule
# number, decision date, court, citation, note). The builder takes the case's name and date from govinfo's record;
# the court and citation given here are checked against nothing online, so only well-known citations are listed.
USR, USC = "usr", "usc"
LANDMARKS = {
    "disability": ("Disability rights", "Landmark cases on the rights of disabled people: the Rehabilitation Act "
                   "of 1973, the Americans with Disabilities Act (ADA) and the Individuals with Disabilities Education "
                   "Act (IDEA), including accessible websites, money, ballots and streaming for blind and deaf "
                   "people. Olmstead v. L. C. (1999) and Board of Education v. Rowley (1982) are in the civics "
                   "book (civ:supreme_court_cases).", [
        (USR, 442, 397, ""), (USR, 468, 883, ""), (USR, 469, 287, ""), (USR, 473, 432, ""), (USR, 480, 273, ""),
        (USR, 484, 305, ""), (USR, 524, 624, ""),
        (USR, 527, 471, "Later history: Congress rejected this decision's narrow reading of \"disability\" in the ADA "
                        "Amendments Act of 2008."),
        (USR, 531, 356, ""), (USR, 532, 661, ""),
        (USR, 534, 184, "Later history: Congress rejected this decision's narrow reading of \"disability\" in the ADA "
                        "Amendments Act of 2008."),
        (USR, 541, 509, ""), (USR, 546, 49, ""), (USR, 557, 230, ""), (USR, 580, 154, ""), (USR, 580, 386, ""),
        (USC, "USCOURTS-dcd-1_02-cv-00864", 0, "2006-11-28", "US District Court for the District of Columbia",
         "American Council of the Blind v. Paulson, 463 F. Supp. 2d 51 (D.D.C. 2006)",
         "The ruling that US paper money that blind people cannot tell apart denies them meaningful access under "
         "the Rehabilitation Act."),
        (USC, "USCOURTS-dcd-1_02-cv-00864", 2, "2008-10-03", "US District Court for the District of Columbia",
         "American Council of the Blind v. Paulson, 581 F. Supp. 2d 1 (D.D.C. 2008)",
         "The court's order on the remedy: the Treasury must provide a way for blind people to tell bills apart."),
        (USC, "USCOURTS-cand-3_06-cv-01802", 0, "2006-09-06", "US District Court for the Northern District of "
         "California", "National Federation of the Blind v. Target Corp., 452 F. Supp. 2d 946 (N.D. Cal. 2006)",
         "The ruling that the ADA claim about Target's inaccessible website could go forward."),
        (USC, "USCOURTS-mad-3_11-cv-30168", 2, "2012-06-19", "US District Court for the District of Massachusetts",
         "National Association of the Deaf v. Netflix, Inc., 869 F. Supp. 2d 196 (D. Mass. 2012)",
         "Captions for streamed films: the ruling that the ADA can apply to a web-only business."),
        (USC, "USCOURTS-ca4-14-02001", 0, "2016-02-09", "US Court of Appeals for the Fourth Circuit",
         "National Federation of the Blind v. Lamone, 813 F.3d 494 (4th Cir. 2016)",
         "Accessible absentee ballots for blind voters in Maryland."),
        (USC, "USCOURTS-ca9-17-55504", 0, "2019-01-15", "US Court of Appeals for the Ninth Circuit",
         "Robles v. Domino's Pizza, LLC, 913 F.3d 898 (9th Cir. 2019)",
         "A blind customer's ADA claim about a pizza company's website and app."),
        (USC, "USCOURTS-ca11-17-13467", 0, "2021-04-07", "US Court of Appeals for the Eleventh Circuit",
         "Gil v. Winn-Dixie Stores, Inc., 993 F.3d 1266 (11th Cir. 2021)",
         "A blind customer's ADA claim about a grocery chain's website. Later history: the court later vacated "
         "this opinion because the case had become moot."),
    ]),
    "consumer": ("Consumer law", "Landmark Supreme Court cases on consumers: debt collection, credit reports, "
                 "arbitration clauses, advertising, product safety and repossession.", [
        (USR, 380, 374, ""), (USR, 395, 337, ""), (USR, 407, 67, ""), (USR, 425, 748, ""), (USR, 517, 559, ""),
        (USR, 552, 312, ""), (USR, 555, 555, ""), (USR, 559, 573, ""), (USR, 563, 333, ""), (USR, 578, 330, ""),
        (USR, 582, 79, ""),
    ]),
    "housing": ("Housing", "Landmark Supreme Court cases on housing: fair housing and discrimination, zoning, "
                "public housing, eviction and taking land for public use.", [
        (USR, 245, 60, ""), (USR, 272, 365, ""), (USR, 334, 1, ""), (USR, 392, 409, ""), (USR, 405, 56, ""),
        (USR, 409, 205, ""), (USR, 429, 252, ""), (USR, 455, 363, ""), (USR, 514, 725, ""), (USR, 535, 125, ""),
        (USR, 545, 469, ""), (USR, 576, 519, ""),
    ]),
    "employment": ("Employment", "Landmark Supreme Court cases on work: wages and hours, unions, discrimination "
                   "and harassment at work, pregnancy and reasonable accommodation.", [
        (USR, 198, 45, ""), (USR, 208, 412, ""), (USR, 300, 379, ""), (USR, 301, 1, ""), (USR, 312, 100, ""),
        (USR, 401, 424, ""), (USR, 411, 792, ""), (USR, 477, 57, ""), (USR, 490, 228, ""), (USR, 510, 17, ""),
        (USR, 523, 75, ""), (USR, 524, 742, ""), (USR, 524, 775, ""), (USR, 535, 391, ""),
        (USR, 550, 618, "Later history: Congress changed the time limit this decision applied, in the Lilly "
                        "Ledbetter Fair Pay Act of 2009."),
        (USR, 575, 206, ""),
    ]),
    "family": ("Family law", "Landmark Supreme Court cases on the family: marriage, parents' rights, custody, "
               "child support, adoption and the state's duty to children. Loving v. Virginia (1967) and Obergefell v. "
               "Hodges (2015) are in the civics book (civ:supreme_court_cases).", [
        (USR, 262, 390, ""), (USR, 268, 510, ""), (USR, 381, 479, ""), (USR, 405, 645, ""), (USR, 406, 205, ""),
        (USR, 431, 494, ""), (USR, 434, 374, ""), (USR, 436, 84, ""), (USR, 440, 268, ""), (USR, 455, 745, ""),
        (USR, 466, 429, ""), (USR, 489, 189, ""), (USR, 491, 110, ""), (USR, 530, 57, ""), (USR, 564, 431, ""),
        (USR, 570, 744, ""),
    ]),
}


def landmark_parts(subject, cache=None, left_out=None):
    """[(part title, PDF address, page address)] of one subject's cases, from govinfo's records; a case whose record
    is not found (or whose date does not match) is said in left_out and skipped."""
    left_out = left_out if left_out is not None else []
    _title, _intro, cases = LANDMARKS[subject]
    parts, volumes = [], {}
    for case in cases:
        if case[0] == USR:
            _kind, volume, page, note = case
            if volume not in volumes:
                volumes[volume] = {g["id"]: g for g in granules(read_mods(f"USREPORTS-{volume}", cache))}
            g = volumes[volume].get(f"USREPORTS-{volume}-{page}")
            if not g or not g["pdf"]:
                left_out.append({"title": f"{volume} U.S. {page}", "reason": "govinfo.gov has no record of this case "
                                 "now.", "url": f"{GOVINFO}/app/details/USREPORTS-{volume}"})
                continue
            title, pdf, address = case_part(g)
            title = f"{title}, Supreme Court of the United States"
        else:
            _kind, package, number, date, court, citation, note = case
            found = {g["id"]: g for g in granules(read_mods(package, cache))}
            g = found.get(f"{package}-{number}")
            if not g or not g["pdf"] or g["date"][:10] != date:
                left_out.append({"title": citation, "reason": "govinfo.gov's record of this opinion was not found, or "
                                 "its date is not the one listed.", "url": f"{GOVINFO}/app/details/{package}"})
                continue
            title, pdf, address = f"{citation}, {court}, decided {date_words(date)}", g["pdf"], g["page"] or g["pdf"]
        parts.append((title + (f". {note}" if note else ""), pdf, address))
    return parts


def landmark_entry(subject):
    """The book entry of one subject's landmark cases."""
    title, intro, cases = LANDMARKS[subject]
    return K.us_pdf(
        GROUP, name=f"court_landmark_{subject}", title=f"Landmark court cases: {title.lower()}",
        subject=f"Court opinions: {title.lower()}", publisher="Supreme Court of the United States and the federal "
        "courts (official PDFs published by the Government Publishing Office on govinfo.gov)",
        source=f"{GOVINFO}/app/collection/usreports",
        description=f"{intro} Each case is read whole from its official PDF, and each part names the court, the date "
                    "it was decided and its citation; a case's later history is said where it changed the law.",
        notice=f"{OPINION_NOTICE}{SYLLABUS_NOTE} {SCAN_NOTE} {NOT_ADVICE}",
        version="the official PDFs on govinfo.gov")


def landmark_maker(subject):
    """(book function, sign function) of one subject's landmark book."""

    def book_fn(name, work, cache=None, left_out=None, limit=None):
        """The subject's book: its cases' official PDFs one after another (pdf_set.pdf_set_book)."""
        import pdf_set
        left_out = left_out if left_out is not None else []
        parts = landmark_parts(subject, cache, left_out)
        if not parts:
            return None
        book = pdf_set.pdf_set_book(landmark_entry(subject), parts, work, cache, left_out, limit)
        if book is not None:
            book.published = ""
            book.version = f"official PDFs on govinfo.gov, read {datetime.date.today().isoformat()}"
        return book

    def sign_fn(name):
        """The weekly sign: the subject's list of cases (the opinions themselves do not change)."""
        return K.sha(LANDMARKS[subject])

    return book_fn, sign_fn


# ====================================================================== the index

SECTIONS = [
    ("Supreme Court opinions", "Every opinion of the Supreme Court of the United States in its official reports, "
     "volume by volume, and the landmark cases most often taught.", [
        ("word", "court-opinions-scotus-1", "United States Reports, volumes 2 to 201 (1790s to 1906)"),
        ("word", "court-opinions-scotus-2", "United States Reports, volumes 202 to 401 (1906 to 1971)"),
        ("word", "court-opinions-scotus-3", "United States Reports, volumes 402 to 586 (1971 to 2019)"),
        ("key", "civ:supreme_court_cases", "Landmark Supreme Court cases on the Constitution (civics)"),
        ("link", "Recent opinions (slip opinions) of the Supreme Court", "https://www.supremecourt.gov/opinions/"
         "slipopinion/24", "public domain, but not yet in the bound reports on govinfo.gov; open them in a browser")]),
    ("Landmark cases by subject", "Landmark cases on the subjects people meet in daily life.", [
        ("key", "court:landmark_disability", "Disability rights: Rehabilitation Act, ADA and IDEA, accessible "
                                             "websites, money, ballots and captions"),
        ("key", "court:landmark_consumer", "Consumer law: debt collection, credit reports, arbitration, advertising"),
        ("key", "court:landmark_housing", "Housing: fair housing, zoning, public housing, eviction"),
        ("key", "court:landmark_employment", "Employment: wages, unions, discrimination and harassment at work"),
        ("key", "court:landmark_family", "Family law: marriage, parents' rights, custody, child support")]),
    ("Laws and legal help", "The laws the courts apply, and plain-language legal help.", [
        ("word", "us-code", "The United States Code"),
        ("word", "state-laws", "State statutes and codes"),
        ("word", "legal-help", "Plain-language legal help guides"),
        ("link", "CourtListener (Free Law Project): federal and state court opinions", "https://www.courtlistener.com/",
         "its site refuses programs (robots.txt); its bulk data (public domain mark) is downloaded by the Writing "
         "Kit on the owner's own computer"),
        ("link", "Caselaw Access Project (Harvard Law School Library): historical state and federal reports",
         "https://case.law/", "its static download site refuses programs (robots.txt); open it in a browser")]),
]
INDEX = X.index_maker("court", GROUP, "Court opinions: a guide to the library", "Court opinions",
                      "A guide to court opinions in the library: the Supreme Court's official reports volume by volume, "
                      "landmark cases by subject, the laws they apply and where to find state court opinions.",
                      SECTIONS)

MAKERS = {"index": INDEX, "usreports": (usreports_book, usreports_sign)}
MAKERS.update({f"landmark_{s}": landmark_maker(s) for s in LANDMARKS})


def volume_keys(first=2, last=586):
    """The keys of the volumes from first to last (those on govinfo.gov)."""
    return [f"court:usreports:{v}" for v in VOLUMES if first <= v <= last]


WORDS = {"court-opinions": lambda: ["court:index"] + [f"court:landmark_{s}" for s in LANDMARKS]}
WORDS.update({w: (lambda a=a, b=b: volume_keys(a, b)) for w, (a, b) in SCOTUS_WORDS.items()})

COLLECTION = K.Collection("court", GROUP, makers=MAKERS, words=WORDS,
                          pieces={"usreports": lambda: [str(v) for v in VOLUMES]})

LICENCE_LINES = {
    "court_govinfo": "govinfo.gov (Government Publishing Office): the United States Reports (USREPORTS) and the "
                     "federal courts' opinions (USCOURTS), works of the US government (17 U.S.C. 105, checked on "
                     "govinfo.gov's policies page at every build); robots.txt allows /metadata/ and /content/, no AI "
                     "rules (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("State court opinions (landmark state cases on consumer, housing, employment and family law, such as "
     "MacPherson v. Buick Motor Co., Henningsen v. Bloomfield Motors, Javins v. First National Realty, Marvin v. "
     "Marvin)", "Court opinions are public domain, but no source here allows programs: courtlistener.com's "
     "robots.txt disallows every program except search engines and shuts out AI companies' readers, and the Caselaw "
     "Access Project's static download site (static.case.law) disallows every program. CourtListener's bulk data "
     "(\"free of known copyright restrictions\", public domain mark) is one 55 GB opinions file updated quarterly, "
     "too big for a library build: the Writing Kit downloads it on the owner's own computer (Build Court Opinion "
     "Data.cmd). Link-only. Index: https://www.courtlistener.com/"),
    ("Supreme Court volumes not yet on govinfo.gov (volume 465, and volumes 587 onwards, such as Bostock v. Clayton "
     "County, 590 U.S. 644, 2020)", "Public domain; govinfo's USREPORTS collection did not have them on 2026-11-22. "
     "The Court's own slip opinions are on supremecourt.gov. Link-only until they reach govinfo. Index: "
     "https://www.govinfo.gov/app/collection/usreports"),
    ("Federal court of appeals and district court opinions before 2004 (such as Williams v. Walker-Thomas Furniture "
     "Co., D.C. Cir. 1965, and Javins v. First National Realty Corp., D.C. Cir. 1970)", "govinfo's USCOURTS "
     "collection starts in 2004; older federal opinions are in CourtListener's bulk data (see above). Link-only. "
     "Index: https://www.govinfo.gov/app/collection/uscourts"),
    ("Oyez case summaries and Justia case pages", "Oyez is CC BY-NC (personal use); Justia's pages are its own "
     "copyright. The Court's own opinions are built here. Link-only. Index: https://www.oyez.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
