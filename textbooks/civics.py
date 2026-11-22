"""Citizenship and civics for the reference library, in the group "Reference, citizenship and civics" (the owner's
request of 2026-11-22). Keys: civics (every book), civ:<name>.

What this module builds, in plain words, each IN FULL:
  - the National Archives' transcriptions of the founding documents: the Constitution, the Bill of Rights, the
    Amendments 11 to 27 and the Declaration of Independence;
  - the naturalisation test (USCIS, public domain): the 2025 civics test's 128 questions and answers, the 2008
    test's 100 questions and answers, the civics flash cards (M-623), A Guide to Naturalization (M-476) and Welcome
    to the United States: A Guide for New Immigrants (M-618). www.uscis.gov refuses programs, so each is read from
    the Internet Archive's Wayback Machine copy of the official PDF (its capture time is in the address) or, for the
    flash cards, from the Government Publishing Office's copy in the Internet Archive;
  - how government works: USA.gov's pages on the branches of government, how laws are made, voting and elections,
    contacting elected officials and citizenship; and Ben's Guide to the US Government (GPO), every page;
  - jury service: the US Courts' pages (qualifications, exemptions and excuses, selection, pay, scams);
  - landmark Supreme Court cases, each the Court's own opinion as printed in the United States Reports (govinfo.gov,
    public domain), with its syllabus (the plain summary printed at its head); a case later overruled says so in
    the book's description;
  - Canada's citizenship study guide, Discover Canada (Immigration, Refugees and Citizenship Canada), for personal
    use (canada.ca's terms allow non-commercial copies), with a note that it is Canadian, not US, material.
  Every book about the law ends its notice with NOT_ADVICE.

Already in the library and not repeated: the EAC's voter guide and accessible voting (civic:eac_voters), the US
Code (us-code), the CFR (laws), the United States Government Manual (pub:us_government_manual), the government group
(group:government), and Project Gutenberg's Federalist Papers in the Kiwix library.

Not built (NOT_INCLUDED, link-only): Vote.gov, uscis.gov's web pages and Oyez (refuse programs, or CC BY-NC: Oyez's
plain-word case summaries are for personal use, so link-only), the Constitution Annotated (constitution.congress.gov,
whose congress.gov family shuts out AI companies' readers), and the Federalist Papers (in the Kiwix library).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
canada.ca's terms line checked at every build for Discover Canada. robots.txt of archives.gov (10 seconds between
pages), usa.gov (10 seconds), bensguide.gpo.gov, uscourts.gov, govinfo.gov and archive.org allow the pages; none has
AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/civics.py civ:archives_founding_documents --out build/textbooks --limit 5
  python3 textbooks/civics.py --list civics
"""

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from parenting import CROWN_NC, CANADA_TERMS, CANADA_TEXT  # noqa: E402 - the same canada.ca terms, checked there too

GROUP = "civics"
GROUPS = {GROUP: "Reference, citizenship and civics"}
NOT_ADVICE = "General information, not tax or legal advice; check the current rules or ask a professional."
USCIS = "US Citizenship and Immigration Services (USCIS), US Department of Homeland Security"
USCIS_NOTICE = ("A work of US Citizenship and Immigration Services (public domain), read from the Internet Archive's "
                "copy of the official PDF because uscis.gov refuses programs. Check uscis.gov for which test version "
                "applies to you and for any updated answers (some answers, such as the names of officials, change "
                "with elections).")
WAYBACK = "https://web.archive.org/web"


def wayback_pdf(name, title, subject, captured, original, description, published=""):
    """A USCIS PDF read from the Wayback Machine's capture of its official address ("id_": the file exactly as
    captured)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=USCIS,
                    pdf=f"{WAYBACK}/{captured}id_/{original}", page=f"{WAYBACK}/{captured}/{original}",
                    description=description, notice=f"{USCIS_NOTICE} {NOT_ADVICE}", published=published,
                    version=f"the official PDF {original} as the Wayback Machine captured it on {captured[:4]}-"
                            f"{captured[4:6]}-{captured[6:8]}")


UQA = "https://www.uscis.gov/sites/default/files/document/questions-and-answers"
PDFS = [
    wayback_pdf("uscis_civics_test_2025", "2025 Civics Test: 128 questions and answers (USCIS)",
                "The naturalisation civics test", "20261025233601",
                f"{UQA}/2025-Civics-Test-128-Questions-and-Answers.pdf",
                "The 128 civics questions of the 2025 version of the naturalisation test, with their answers: American "
                "government (principles of democracy, the system of government, rights and responsibilities) and "
                "American history (the colonial period and independence, the 1800s, recent history) and symbols and "
                "holidays."),
    wayback_pdf("uscis_civics_test_100", "100 civics questions and answers, 2008 version (USCIS)",
                "The naturalisation civics test", "20261101123208", f"{UQA}/100q.pdf",
                "The 100 civics questions and answers of the 2008 version of the naturalisation test (still used for "
                "some applicants), with the questions people 65 and older who have lived in the US 20 years study."),
    wayback_pdf("uscis_guide_to_naturalization", "A Guide to Naturalization (USCIS, M-476)", "Becoming a US citizen",
                "20241011015042", "https://www.uscis.gov/sites/default/files/document/guides/M-476.pdf",
                "USCIS's guide to becoming a US citizen: who is eligible, the application (Form N-400), the "
                "interview, the English and civics tests, exceptions and accommodations for people with "
                "disabilities, and the oath ceremony."),
    wayback_pdf("uscis_welcome_new_immigrants", "Welcome to the United States: A Guide for New Immigrants (USCIS, "
                "M-618)", "Life in the US for new immigrants", "20261019194008",
                "https://www.uscis.gov/sites/default/files/document/guides/M-618.pdf",
                "USCIS's guide for new permanent residents: your rights and responsibilities, getting settled "
                "(Social Security number, housing, jobs, money, health care, education), learning about the United "
                "States and how government works, and becoming a citizen."),
    K.us_pdf(GROUP, name="uscis_civics_flash_cards", title="Civics flash cards for the naturalization test (USCIS, "
             "M-623, 2012)", subject="The naturalisation civics test", publisher=USCIS,
             archive="civics-flash-cards-for-the-new-naturalization-test-m-623-rev.-0212-hs-8.2f-6122012-flash-cards",
             published="2012-02",
             version="M-623 (rev. 02/12), the Government Publishing Office's copy in the Internet Archive",
             description="USCIS's flash cards for the 2008 version of the civics test: each card's question with its "
                         "answer on the other side, read here card by card.",
             notice=f"A work of US Citizenship and Immigration Services (public domain), from the Government "
                    f"Publishing Office's copy (SuDoc HS 8.2:F 61/2/2012). 2012 edition: answers naming officials "
                    f"are out of date; check uscis.gov. {NOT_ADVICE}"),
    dict(K.us_pdf(GROUP, name="discover_canada", title="Discover Canada: The Rights and Responsibilities of "
                  "Citizenship (Canada's citizenship study guide)", subject="Canadian citizenship (not US)",
                  publisher="Immigration, Refugees and Citizenship Canada", country="Canada",
                  pdf="https://www.canada.ca/content/dam/ircc/migration/ircc/english/pdf/pub/discover.pdf",
                  page="https://www.canada.ca/en/immigration-refugees-citizenship/corporate/publications-manuals/"
                       "discover-canada.html",
                  description="Canada's official study guide for its citizenship test: the oath, rights and "
                              "responsibilities, who Canadians are, Canada's history, government, elections, the "
                              "justice system, symbols, economy and regions.",
                  notice=f"Canadian, not US, material: it describes Canada's citizenship test and government. "
                         f"Crown copyright (Canada); personal use only under canada.ca's terms, which allow copies "
                         f"\"for non-commercial purposes\". Source: Immigration, Refugees and Citizenship Canada. "
                         f"{NOT_ADVICE}", version="the edition at canada.ca when built"),
         licence=CROWN_NC, licence_url=CANADA_TERMS, licence_page=CANADA_TERMS, licence_text=CANADA_TEXT,
         personal_use=True),
]

# ====================================================================== web guides

ARCHIVES = "https://www.archives.gov/founding-docs"
FOUNDING = [f"{ARCHIVES}/{p}" for p in ("constitution-transcript", "bill-of-rights-transcript", "amendments-11-27",
                                        "declaration-transcript")]
USA = "https://www.usa.gov"
USA_CIVICS_HUBS = ["branches-of-government", "how-laws-are-made", "voting-and-elections", "elected-officials",
                   "immigration-and-citizenship"]
USA_NOT_CIVICS = ("about|about-the-us|accessibility-policy|agency-index|benefits|blog|money|partner-with-usagov|"
                  "phone|privacy-security|site-issue-report-form|espanol|contact|search|life-events|travel|"
                  "housing-help|scams-and-fraud|jobs-and-unemployment|health-insurance|disability-services|"
                  "website-analytics|benefit-finder|passport|real-id|holidays")
BEN = "https://bensguide.gpo.gov"
BEN_NOT = ("about-ben-and-gpo|about-this-site|feedback-suggestions|for-parents-and-educators|games|legal|"
           "ben-libraries")
COURTS = "https://www.uscourts.gov/court-programs/jury-service"

GUIDES = [
    dict(K.us_web(GROUP, name="archives_founding_documents", title="The Constitution, the Bill of Rights, the "
                  "Amendments and the Declaration of Independence (National Archives transcriptions)",
                  subject="The founding documents", publisher="National Archives and Records Administration",
                  source=FOUNDING[0],
                  description="The National Archives' transcriptions of the Constitution of the United States (as "
                              "signed in 1787), the Bill of Rights (the first ten amendments), the Amendments 11 to "
                              "27, and the Declaration of Independence, with the Archives' notes on parts later "
                              "changed by amendments.",
                  notice=f"From the National Archives (archives.gov): works of the US government (public domain). "
                         f"{NOT_ADVICE}", crawl=[(FOUNDING[0], 0)], urls=list(FOUNDING),
                  pages=r"^https://www\.archives\.gov/founding-docs/(constitution-transcript|bill-of-rights-transcript|"
                        r"amendments-11-27|declaration-transcript)$",
                  content=(r'<div id="main-col"[^>]*>', r'<div id="sidebar"'),
                  unit_rules=[(r"declaration", "Declaration of Independence"), (r".", "The Constitution")], limit=6),
         published="1787"),
    K.guide(GROUP, "usa_gov_government_voting", "How the US government works: branches, laws, voting, elected "
            "officials and citizenship (USA.gov)", "How government works", "USAGov, General Services Administration "
            "(USA.gov)", [f"{USA}/{h}" for h in USA_CIVICS_HUBS],
            rf"^https://www\.usa\.gov/(?!(?:{USA_NOT_CIVICS})$)[a-z0-9-]+$",
            "USA.gov's pages on the three branches of government, how laws are made, voting and elections (who can "
            "vote, registering, absentee voting, election results, the Electoral College), finding and contacting "
            "your elected officials, and citizenship and immigration (becoming a citizen, green cards, proving "
            "citizenship).", f"A work of the US government (USAGov, General Services Administration; public "
                             f"domain). {NOT_ADVICE}",
            units=[(r"/(branches|how-laws|legislative|executive|judicial|federal-courts|congress)", "Branches of "
                    "government and laws"), (r"/(vot|elect|register|absentee|midterm|primary)", "Voting and "
                    "elections"), (r"/(citizen|green-card|immigra|naturaliz)", "Citizenship"),
                   (r".", "Government and officials")], limit=120),
    K.guide(GROUP, "bens_guide", "Ben's Guide to the US Government (GPO)", "How government works (for all ages)",
            "US Government Publishing Office (GPO)", [BEN, f"{BEN}/learning-adventures-14more", f"{BEN}/citizenship",
                                                      f"{BEN}/glossary"],
            rf"^https://bensguide\.gpo\.gov/(?!(?:{BEN_NOT})(?:/|$))[a-z0-9-]+$",
            "Every page of Ben's Guide, the Government Publishing Office's plain guide to how the US government "
            "works: the branches of government, how laws are made, federal and state government, elections, "
            "citizenship, historic documents (the Declaration of Independence, the Constitution, the Bill of "
            "Rights) and the glossary.", f"A work of the US Government Publishing Office (public domain). "
                                         f"{NOT_ADVICE}", depth=2,
            follow=rf"^https://bensguide\.gpo\.gov/(?!(?:{BEN_NOT})(?:/|$))[a-z0-9-]+$", limit=150),
    K.guide(GROUP, "uscourts_jury_service", "Jury service: qualifications, excuses, selection and pay (US Courts)",
            "Jury duty", "Administrative Office of the US Courts (uscourts.gov)", COURTS,
            r"^https://www\.uscourts\.gov/court-programs/jury-service(/[a-z0-9-]+)*$",
            "The federal courts' pages on jury service: who may serve, exemptions and excuses (including how to ask "
            "for one), how jurors are chosen, grand and trial juries, what to expect when summoned, juror pay and "
            "jury scams (courts never ask for money or personal details by phone or email).",
            f"A work of the federal judiciary (public domain). State courts have their own jury rules: read your "
            f"summons. {NOT_ADVICE}", depth=2, follow=r"^https://www\.uscourts\.gov/court-programs/jury-service"
                                                      r"(/[a-z0-9-]+)?$", limit=30),
]

# ====================================================================== landmark Supreme Court cases (United States Reports)

GOVINFO = "https://www.govinfo.gov"
# (case name, volume, first page, year): the citation in the United States Reports, govinfo's granule
# USREPORTS-<volume>-<page>.
CASES = [
    ("Marbury v. Madison", 5, 137, 1803), ("McCulloch v. Maryland", 17, 316, 1819), ("Gibbons v. Ogden", 22, 1, 1824),
    ("Dred Scott v. Sandford", 60, 393, 1857), ("Plessy v. Ferguson", 163, 537, 1896),
    ("Brown v. Board of Education of Topeka", 347, 483, 1954), ("Mapp v. Ohio", 367, 643, 1961),
    ("Engel v. Vitale", 370, 421, 1962), ("Gideon v. Wainwright", 372, 335, 1963),
    ("New York Times Co. v. Sullivan", 376, 254, 1964), ("Reynolds v. Sims", 377, 533, 1964),
    ("Heart of Atlanta Motel v. United States", 379, 241, 1964), ("Miranda v. Arizona", 384, 436, 1966),
    ("Loving v. Virginia", 388, 1, 1967), ("Tinker v. Des Moines Independent Community School District", 393, 503, 1969),
    ("New York Times Co. v. United States", 403, 713, 1971), ("Roe v. Wade", 410, 113, 1973),
    ("United States v. Nixon", 418, 683, 1974), ("Regents of the University of California v. Bakke", 438, 265, 1978),
    ("Board of Education v. Rowley", 458, 176, 1982), ("Texas v. Johnson", 491, 397, 1989),
    ("Olmstead v. L. C.", 527, 581, 1999), ("Bush v. Gore", 531, 98, 2000),
    ("District of Columbia v. Heller", 554, 570, 2008), ("Shelby County v. Holder", 570, 529, 2013),
    ("Obergefell v. Hodges", 576, 644, 2015)]
# Cases whose holding no longer stands, said in the book's description (facts of later decisions and amendments).
CASE_NOTES = ("Later history: Dred Scott v. Sandford was superseded by the Thirteenth and Fourteenth Amendments; "
              "Plessy v. Ferguson's \"separate but equal\" was rejected by Brown v. Board of Education (1954); Roe v. "
              "Wade was overruled by Dobbs v. Jackson Women's Health Organization (2022).")
CASES_ENTRY = K.us_pdf(
    GROUP, name="civ_supreme_court_cases", title="Landmark Supreme Court cases: the Court's own opinions (United "
    "States Reports)", subject="The Supreme Court and the Constitution", publisher="Supreme Court of the United "
    "States (United States Reports, published by the Government Publishing Office on govinfo.gov)",
    source=f"{GOVINFO}/app/collection/usreports",
    description="The Supreme Court's opinions in landmark cases, each read whole from the official United States "
                "Reports, with the syllabus (the plain summary printed at its head) and every opinion: " +
                "; ".join(f"{n} ({v} U.S. {p}, {y})" for n, v, p, y in CASES) + ". " + CASE_NOTES,
    notice="Opinions of the Supreme Court of the United States, from the official United States Reports on "
           "govinfo.gov: works of the US government (public domain). The syllabus is not part of the opinion; "
           "it is prepared for the reader's convenience. Old volumes are scans whose text has the scanner's "
           f"mistakes. {NOT_ADVICE}", version="the official United States Reports volumes on govinfo.gov")


def case_parts():
    """[(part title, PDF address, page address)] of the cases, oldest first."""
    return [(f"{n} ({v} U.S. {p}, {y})", f"{GOVINFO}/content/pkg/USREPORTS-{v}/pdf/USREPORTS-{v}-{p}.pdf",
             f"{GOVINFO}/app/details/USREPORTS-{v}/USREPORTS-{v}-{p}") for n, v, p, y in CASES]


def cases_book(name, work, cache=None, left_out=None, limit=None):
    """The landmark cases book: every case's opinion read with pdf_set.pdf_set_book."""
    import pdf_set
    book = pdf_set.pdf_set_book(CASES_ENTRY, case_parts(), work, cache, left_out, limit)
    if book is not None:
        book.version = f"United States Reports on govinfo.gov, read {datetime.date.today().isoformat()}"
    return book


def cases_sign(name):
    """The cases book's sign of change: its list of cases (the printed reports themselves do not change)."""
    return K.sha(CASES)


COLLECTION = K.Collection("civ", GROUP, guides=GUIDES, pdfs=PDFS,
                          makers={"supreme_court_cases": (cases_book, cases_sign)},
                          words={"civics": lambda: [f"civ:{g['name']}" for g in GUIDES + PDFS] +
                                 ["civ:supreme_court_cases"]})

LICENCE_LINES = {
    "civ_us_gov": "archives.gov, usa.gov, bensguide.gpo.gov, uscourts.gov and govinfo.gov: works of the US government "
                  "(17 U.S.C. 105, checked on govinfo.gov's policies page at every build); archives.gov and usa.gov "
                  "ask 10 seconds between pages, which the builder keeps; no AI rules (checked 2026-11-22).",
    "civ_uscis_wayback": "USCIS's PDFs: works of the US government, read from the Wayback Machine's captures of their "
                         "official addresses (uscis.gov answers programs \"403\", checked 2026-11-22); the flash "
                         "cards from the GPO's copy in the Internet Archive.",
    "civ_canada": "Discover Canada: canada.ca/en/transparency/terms.html (checked at every build): \"you may reproduce "
                  "the materials in whole or in part for non-commercial purposes\": personal use only.",
}

NOT_INCLUDED = [
    ("Vote.gov (registering to vote in each state)", "Public domain, but vote.gov answers programs \"403\" (checked "
     "2026-11-22). The EAC's voter guide (civic:eac_voters) and USA.gov's voting pages (civ:usa_gov_government_voting) "
     "are built. Link-only. Index: https://vote.gov/"),
    ("uscis.gov's citizenship web pages (study materials, the reading and writing vocabulary, the N-400)", "Public "
     "domain, but www.uscis.gov answers programs \"403\" (checked 2026-11-22); its PDFs are built from Wayback Machine "
     "copies. Link-only. Index: https://www.uscis.gov/citizenship/find-study-materials-and-resources"),
    ("Oyez: plain-language summaries and audio of Supreme Court cases", "CC BY-NC 4.0 (non-commercial): personal use "
     "only, so link-only; the Court's own opinions with their syllabus are built (civ:supreme_court_cases). Index: "
     "https://www.oyez.org/"),
    ("Supreme Court opinions on supremecourt.gov (recent terms, such as Dobbs v. Jackson Women's Health Organization, "
     "2022)", "Public domain; volumes not yet in the bound United States Reports on govinfo.gov are not read here. "
     "Link-only. Index: https://www.supremecourt.gov/opinions/slipopinion/21"),
    ("Constitution Annotated (constitution.congress.gov)", "Public domain, but its congress.gov family's robots.txt "
     "shuts out AI companies' readers, so it is not read. The Constitution itself is built "
     "(civ:archives_founding_documents). Index: https://constitution.congress.gov/"),
    ("The Federalist Papers", "Public domain; already in the Kiwix library (Project Gutenberg, eBook 1404), so not "
     "built again. Index: https://www.gutenberg.org/ebooks/1404"),
    ("State and local government guides (contacting state legislators, local elections)", "Each state's own site; "
     "link-only. Index: https://www.usa.gov/state-governments"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
