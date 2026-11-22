"""Money, work and business in depth for the reference library, in the group "Reference, money, work and business"
(the owner's request of 2026-11-22). Keys: money-work (every book), mw:<name>.

What this module builds, in plain words, each IN FULL:
  - the IRS publications the library did not have yet, each the IRS's newest PDF read from its official address
    (www.irs.gov/pub/irs-pdf/, robots.txt allows it): Publication 503 (Child and Dependent Care Expenses), 505 (Tax
    Withholding and Estimated Tax), 523 (Selling Your Home), 529 (Miscellaneous Deductions), 583 (Starting a Business
    and Keeping Records), 587 (Business Use of Your Home), 1 (Your Rights as a Taxpayer), 15 (Employer's Tax Guide,
    Circular E), 463 (Travel, Gift, and Car Expenses), 946 (How To Depreciate Property), 560 (Retirement Plans for
    Small Business), 594 (The IRS Collection Process), and the Form 1040 instructions;
  - the IRS's list of every state's tax agency (the state tax basics are link-only by the owner's rule: each state's
    own site, one link per state, from this IRS page);
  - the CFPB's "Buying a House" (Owning a Home) guide, every page;
  - the Department of Labor: every Wage and Hour Division fact sheet (minimum wage, overtime, child labor, family and
    medical leave, tipped workers ...), the Employee Benefits Security Administration's consumer publications (your
    retirement plan, COBRA, health benefits, what to do when you lose your job) and the unemployment insurance page;
  - the National Labor Relations Board's pages on employees' rights (forming a union, concerted activity, strikes,
    how to enforce your rights);
  - HealthCare.gov's guides (the quick guide to the Marketplace, coverage, lowering costs, Medicaid and CHIP,
    applying and enrolling, and the health insurance glossary);
  - the O*NET database (US Department of Labor, CC BY 4.0): every occupation with its description, its tasks, the
    titles people in it report and its Job Zone (how much preparation it needs), one page per occupation group.
  Every book's notice ends with NOT_ADVICE ("General information, not tax or legal advice; check the current rules or
  ask a professional.").

Already in the library and not repeated (extended, never duplicated): IRS Publications 17, 501, 502, 525, 526, 554,
590-A, 590-B, 596, 907, 915, 970 and 334 (sources.py and thin:taxes), the Internal Revenue Manual (benefits), the
CFPB's consumer guides and "Your Money, Your Goals" and the FDIC's Money Smart (money), USA.gov's benefits, housing,
jobs and money pages (help:usa_gov), the EEOC's workers' pages (legal:eeoc_workers), the SBA's business guide
(wb:sba_business_guide), disability employment (work), the US Code and the CFR.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): Investor.gov, SSA, OSHA, BLS's Occupational
Outlook Handbook and CareerOneStop (all refuse programs), FINRA, NAIC, SCORE and the state insurance departments and
attorneys general (copyright or one site each), HUD's topic pages (their text sits in tab panels), and IRS
Publication 535 (discontinued by the IRS after 2022).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
O*NET's CC BY 4.0 line checked on its licence page at every build. robots.txt of irs.gov, consumerfinance.gov,
dol.gov, nlrb.gov, healthcare.gov and onetcenter.org allow the pages read; none has AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/money_work.py mw:irs_pub_505 --out build/textbooks --limit 5
  python3 textbooks/money_work.py --list money-work
"""

import datetime
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "moneywork"
GROUPS = {GROUP: "Reference, money, work and business"}

# The line every answer about taxes or the law ends with (the owner's rule), in every book's notice.
NOT_ADVICE = "General information, not tax or legal advice; check the current rules or ask a professional."
TAX_NOTE = ("Tax laws change every year: this is the IRS's newest edition (the weekly check rebuilds it when the IRS "
            "changes it). ")


def web_list(name, title, subject, publisher, urls, pages, description, notice, units=(), **more):
    """A web guide of a fixed list of pages (no crawl beyond them): the first address is its source."""
    return K.us_web(GROUP, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=f"{notice} {NOT_ADVICE}", crawl=[(urls[0], 0)], urls=list(urls),
                    pages=pages, unit_rules=list(units), limit=len(urls) + 5, **more)


def crawl_guide(name, title, subject, publisher, start, pages, description, notice, **more):
    """A web guide found by crawling from start (refs_kit.guide), its notice ending with NOT_ADVICE."""
    return K.guide(GROUP, name, title, subject, publisher, start, pages, description, f"{notice} {NOT_ADVICE}",
                   **more)


# ====================================================================== IRS publications (PDF)

IRS = "Internal Revenue Service (IRS), US Department of the Treasury"


def irs_pdf(file, title, description, page=None):
    """One IRS publication or instructions: its newest PDF at www.irs.gov/pub/irs-pdf/<file>.pdf."""
    number = file[1:] if file.startswith("p") else file
    return K.us_pdf(GROUP, name=f"irs_{'pub_' + number if file.startswith('p') else file}", title=title,
                    subject="Taxes", publisher=IRS, pdf=f"https://www.irs.gov/pub/irs-pdf/{file}.pdf",
                    page=page or f"https://www.irs.gov/forms-pubs/about-publication-{number}",
                    description=description,
                    notice=f"A work of the Internal Revenue Service (public domain). {TAX_NOTE}{NOT_ADVICE}",
                    version="the newest revision at irs.gov when built (its revision date is on its first page)")


PDFS = [
    irs_pdf("p503", "Child and Dependent Care Expenses (IRS Publication 503)",
            "Who can take the credit for child and dependent care expenses, the care and work tests, which expenses "
            "count, and how to figure the credit, with the worksheets."),
    irs_pdf("p505", "Tax Withholding and Estimated Tax (IRS Publication 505)",
            "How federal income tax is withheld from pay, pensions and other income (Form W-4), when you must pay "
            "estimated tax, how to figure and pay it, and the penalty for paying too little."),
    irs_pdf("p523", "Selling Your Home (IRS Publication 523)",
            "The tax rules when you sell your main home: whether you can exclude the gain, figuring the gain or "
            "loss, what to report, and the worksheets."),
    irs_pdf("p529", "Miscellaneous Deductions (IRS Publication 529)",
            "The miscellaneous itemized deductions: which ones you can still take, including impairment-related "
            "work expenses of people with disabilities, and which ones you cannot."),
    irs_pdf("p583", "Starting a Business and Keeping Records (IRS Publication 583)",
            "Basic federal tax information for people starting a business: the forms of business, employer "
            "identification numbers, the taxes a business may owe, and how to keep records."),
    irs_pdf("p587", "Business Use of Your Home (IRS Publication 587)",
            "Who can deduct expenses for business use of a home (including day-care providers), how to figure the "
            "deduction, the simplified method, and the records to keep."),
    irs_pdf("p1", "Your Rights as a Taxpayer (IRS Publication 1)",
            "The Taxpayer Bill of Rights and the IRS's processes for examinations, appeals, collections and refunds."),
    irs_pdf("p15", "Employer's Tax Guide, Circular E (IRS Publication 15)",
            "What employers must do: withholding, depositing and reporting income tax, Social Security and Medicare "
            "taxes and federal unemployment tax, with the withholding tables."),
    irs_pdf("p463", "Travel, Gift, and Car Expenses (IRS Publication 463)",
            "Which business travel, meal, gift and car expenses can be deducted, and the records needed."),
    irs_pdf("p946", "How To Depreciate Property (IRS Publication 946)",
            "Depreciation of business property: what can be depreciated, the section 179 deduction, the special "
            "depreciation allowance and MACRS."),
    irs_pdf("p560", "Retirement Plans for Small Business (IRS Publication 560)",
            "Retirement plans a small business or self-employed person can set up: SEP, SIMPLE and qualified plans, "
            "how much can be put in and deducted."),
    irs_pdf("p594", "The IRS Collection Process (IRS Publication 594)",
            "What happens when you owe tax: the bills, payment plans and other ways to pay, liens and levies, and "
            "your rights to appeal."),
    irs_pdf("i1040gi", "Form 1040 and 1040-SR Instructions", "The IRS's line-by-line instructions for the US "
            "individual income tax return (Forms 1040 and 1040-SR), with the tax tables.",
            page="https://www.irs.gov/forms-pubs/about-form-1040"),
]

# ====================================================================== web guides

CFPB = "https://www.consumerfinance.gov"
DOL = "https://www.dol.gov"
EBSA_PUBS = f"{DOL}/agencies/ebsa/about-ebsa/our-activities/resource-center/publications"
# EBSA's publications come in many languages, each its own page ending in a language code: English only here.
EBSA_OTHER_LANGUAGES = r"-(?:es|ar|zh-sc|zh-tc|fr|ht|ko|pl|pt|ru|tl|vi|spanish|chinese|korean|vietnamese)$"
NLRB = "https://www.nlrb.gov/about-nlrb/rights-we-protect"
HCGOV = "https://www.healthcare.gov"
HCGOV_PARTS = "quick-guide|coverage|lower-costs|medicaid-chip|apply-and-enroll|immigrants|young-adults|glossary"

GUIDES = [
    web_list("irs_state_tax_agencies", "State government tax websites (IRS): where to find each state's tax rules",
             "State taxes (links)", IRS,
             ["https://www.irs.gov/businesses/small-businesses-self-employed/state-government-websites"],
             r"^https://www\.irs\.gov/businesses/small-businesses-self-employed/state-government-websites$",
             "The IRS's list of every state's (and the District of Columbia's) tax agency website, for state income, "
             "sales and business taxes. Each state's own rules are link-only: open your state's site for its forms "
             "and rates.", "A work of the Internal Revenue Service (public domain). State tax rules differ from "
                           "state to state and change every year."),
    crawl_guide("cfpb_buying_a_house", "Buying a House: tools and resources for home buyers (CFPB)",
                "Buying a home and mortgages", "Consumer Financial Protection Bureau (CFPB)",
                f"{CFPB}/owning-a-home/",
                r"^https://www\.consumerfinance\.gov/owning-a-home(/[a-z0-9-]+)*/?$",
                "Every page of the CFPB's Buying a House guide: preparing to shop, the steps of buying a home, "
                "explore interest rates, loan options (conventional, FHA, VA, USDA), the Loan Estimate and Closing "
                "Disclosure explained line by line, closing, and the mortgage glossary.",
                "A work of the Consumer Financial Protection Bureau (public domain).", depth=2,
                follow=r"^https://www\.consumerfinance\.gov/owning-a-home/[a-z0-9-]+/$",
                units=[(r"/loan-estimate/", "Your Loan Estimate"), (r"/closing-disclosure/", "Your Closing Disclosure"),
                       (r"/loan-options/", "Loan options"), (r".", "Buying a house")], limit=200),
    crawl_guide("dol_whd_fact_sheets", "Wage and Hour Division fact sheets: minimum wage, overtime, child labor and "
                "family leave (US Department of Labor)", "Wages, hours and leave at work",
                "Wage and Hour Division, US Department of Labor", f"{DOL}/agencies/whd/fact-sheets",
                r"^https://www\.dol\.gov/agencies/whd/fact-sheets/\d+[a-z0-9-]*$",
                "Every English fact sheet of the Labor Department's Wage and Hour Division: who the Fair Labor "
                "Standards Act covers, the minimum wage and overtime pay, tipped employees, hours worked, breaks, "
                "child labor rules, the Family and Medical Leave Act, workers with disabilities paid special "
                "minimum wages, farm workers, home care, and the rules for each kind of business.",
                "A work of the US Department of Labor (public domain). States may have higher minimum wages and "
                "more protections.", units=[(r"/fact-sheets/28", "Family and Medical Leave Act"),
                                            (r"child-labor", "Child labor"), (r".", "Fact sheets")], limit=300),
    crawl_guide("dol_ebsa_publications", "Your retirement and health benefits at work: consumer publications "
                "(Employee Benefits Security Administration, US Department of Labor)", "Retirement and health benefits",
                "Employee Benefits Security Administration (EBSA), US Department of Labor", EBSA_PUBS,
                rf"^https://www\.dol\.gov/agencies/ebsa/about-ebsa/our-activities/resource-center/publications/"
                rf"(?![a-z0-9-]*{EBSA_OTHER_LANGUAGES})[a-z0-9-]+$",
                "Every English consumer publication of EBSA: what you should know about your retirement plan, top "
                "ways to save for retirement, taking the mystery out of retirement planning, an employee's guide to "
                "health benefits under COBRA, filing a claim for health benefits, life changes and health choices, "
                "what to do when you lose your job, and avoiding surprise health care expenses.",
                "A work of the US Department of Labor (public domain).", limit=150),
    web_list("dol_unemployment_insurance", "Unemployment insurance: how it works (US Department of Labor)",
             "Unemployment insurance", "Employment and Training Administration, US Department of Labor",
             [f"{DOL}/general/topic/unemployment-insurance"],
             r"^https://www\.dol\.gov/general/topic/unemployment-insurance$",
             "The Labor Department's page on unemployment insurance: who may get it, how state programmes work, "
             "and where to apply. Each state runs its own programme: apply to your state (its site is link-only "
             "here).", "A work of the US Department of Labor (public domain). Apply to the unemployment "
                       "insurance programme of the state where you worked."),
    crawl_guide("nlrb_employee_rights", "Employees' rights under the National Labor Relations Act (NLRB)",
                "Workers' rights: unions and concerted activity", "National Labor Relations Board (NLRB)", NLRB,
                r"^https://www\.nlrb\.gov/about-nlrb/rights-we-protect(/[a-z0-9-]+)*$",
                "The NLRB's pages on the rights the law protects: your rights as an employee, acting together with "
                "co-workers (concerted activity) even without a union, forming a union, collective bargaining, "
                "strikes and pickets, union dues, social media, and how to enforce your rights.",
                "A work of the National Labor Relations Board (public domain).", depth=2,
                follow=r"^https://www\.nlrb\.gov/about-nlrb/rights-we-protect(/[a-z-]+)?$", limit=80),
    crawl_guide("healthcare_gov_guides", "HealthCare.gov: the Marketplace, coverage, lower costs and the health "
                "insurance glossary", "Health insurance", "Centers for Medicare & Medicaid Services (HealthCare.gov)",
                [f"{HCGOV}/{p}/" for p in HCGOV_PARTS.split("|")],
                rf"^https://www\.healthcare\.gov/({HCGOV_PARTS})(/[a-z0-9-]+)*/?$",
                "HealthCare.gov's guides: the quick guide to the Health Insurance Marketplace, dates and deadlines, "
                "what Marketplace plans cover (preventive care, mental health, pregnancy, pre-existing conditions), "
                "lowering your costs (premium tax credits, cost-sharing reductions), Medicaid and CHIP, applying and "
                "enrolling, coverage for immigrants and young adults, and every entry of the health insurance "
                "glossary (deductible, copayment, coinsurance, out-of-pocket maximum ...).",
                "A work of the Centers for Medicare & Medicaid Services (public domain). Dates, prices and rules "
                "change every year: check HealthCare.gov or call 1-800-318-2596.", depth=1,
                units=[(r"/glossary/", "Health insurance glossary"), (r"/quick-guide/", "Quick guide"),
                       (r"/lower-costs/", "Lower costs"), (r"/medicaid-chip/", "Medicaid and CHIP"),
                       (r".", "Coverage and enrolling")], limit=400),
]

# ====================================================================== O*NET occupations (CC BY 4.0)

ONET = "https://www.onetcenter.org"
ONET_DB_PAGE = f"{ONET}/database.html"
ONET_LICENCE_PAGE = f"{ONET}/license_db.html"
ONET_LICENCE_TEXT = r"licensed under a Creative Commons Attribution 4\.0 International License"
ONET_FILES = ("Occupation Data.txt", "Task Statements.txt", "Sample of Reported Titles.txt", "Job Zones.txt",
              "Job Zone Reference.txt")
# The major groups of the Standard Occupational Classification (the first two digits of an O*NET-SOC code).
SOC_GROUPS = {
    "11": "Management", "13": "Business and financial operations", "15": "Computer and mathematical",
    "17": "Architecture and engineering", "19": "Life, physical and social science",
    "21": "Community and social service", "23": "Legal", "25": "Educational instruction and library",
    "27": "Arts, design, entertainment, sports and media", "29": "Healthcare practitioners and technical",
    "31": "Healthcare support", "33": "Protective service", "35": "Food preparation and serving",
    "37": "Building and grounds cleaning and maintenance", "39": "Personal care and service", "41": "Sales",
    "43": "Office and administrative support", "45": "Farming, fishing and forestry",
    "47": "Construction and extraction", "49": "Installation, maintenance and repair", "51": "Production",
    "53": "Transportation and material moving", "55": "Military specific"}


def onet_credit(version):
    """The credit O*NET's licence page asks for when its information is edited (here: arranged into pages)."""
    return (f"This book includes information from the O*NET {version} Database by the U.S. Department of Labor, "
            f"Employment and Training Administration (USDOL/ETA). Used under the CC BY 4.0 license. O*NET® is a "
            f"trademark of USDOL/ETA. GetBraille.com's Digital Accessibility Toolkit has modified all or some of this "
            f"information (arranged into one page per occupation group; no words of a record changed). USDOL/ETA has "
            f"not approved, endorsed, or tested these modifications.")


def onet_zip_url(page_text):
    """The address of the newest O*NET database's tab-separated text files ("db_31_0_text.zip") on its download
    page, from the address of its Excel files listed there; "" when the page names none."""
    m = re.search(r'/dl_files/database/(db_(\d+)_(\d+))_(?:excel|text|mysql)\.zip', page_text)
    return f"{ONET}/dl_files/database/{m.group(1)}_text.zip" if m else ""


def onet_rows(text):
    """The rows of one O*NET tab-separated text file as dicts (its first line names the columns)."""
    lines = text.replace("\r", "").split("\n")
    head = lines[0].split("\t")
    return [dict(zip(head, line.split("\t"))) for line in lines[1:] if line.strip()]


def onet_pages(tables, limit=None):
    """[(path, title, body HTML, unit)] of the occupations in tables ({file name: text}), one page per major group:
    each occupation's title, code, description, Job Zone, reported job titles and tasks (core tasks first)."""
    import build_textbooks as B
    tasks, titles, zones = {}, {}, {}
    for r in onet_rows(tables["Task Statements.txt"]):
        tasks.setdefault(r["O*NET-SOC Code"], []).append((r.get("Task Type") != "Core", r["Task"]))
    for r in onet_rows(tables["Sample of Reported Titles.txt"]):
        titles.setdefault(r["O*NET-SOC Code"], []).append(r["Reported Job Title"])
    names = {r["Job Zone"]: r["Name"] for r in onet_rows(tables["Job Zone Reference.txt"])}
    for r in onet_rows(tables["Job Zones.txt"]):
        zones[r["O*NET-SOC Code"]] = f"Job Zone {r['Job Zone']}: {names.get(r['Job Zone'], '')}".rstrip(": ")
    groups = {}
    for r in onet_rows(tables["Occupation Data.txt"]):
        groups.setdefault(r["O*NET-SOC Code"][:2], []).append(r)
    pages = []
    for code in sorted(groups):
        if limit and len(pages) >= limit:
            break
        parts = []
        for r in sorted(groups[code], key=lambda r: r["Title"]):
            soc = r["O*NET-SOC Code"]
            parts.append(f"<h2>{B.esc(r['Title'])} ({B.esc(soc)})</h2><p>{B.esc(r['Description'])}</p>")
            if soc in zones:
                parts.append(f"<p>{B.esc(zones[soc])}.</p>")
            if titles.get(soc):
                parts.append(f"<p>Job titles people in it report: {B.esc(', '.join(titles[soc]))}.</p>")
            if tasks.get(soc):
                parts.append("<h3>Tasks</h3><ul>" + "".join(f"<li>{B.esc(t)}</li>" for _o, t in sorted(tasks[soc]))
                             + "</ul>")
        group = SOC_GROUPS.get(code, f"Group {code}")
        pages.append((f"group-{code}", f"{group} occupations", "".join(parts), "Occupations by group"))
    return pages


def onet_book(name, work, cache=None, left_out=None, limit=None):
    """The O*NET occupations book (see the module docstring): the licence line checked, the newest database's text
    files read from O*NET's download page."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    words = " ".join(re.sub(r"<[^>]+>", " ", B.fetch(ONET_LICENCE_PAGE, cache)).split())
    if not re.search(ONET_LICENCE_TEXT, words):
        left_out.append({"title": "O*NET occupations", "reason": "O*NET's licence page no longer says CC BY 4.0."})
        return None
    url = onet_zip_url(B.fetch(ONET_DB_PAGE, cache))
    if not url or not K.readable(url, cache):
        left_out.append({"title": "O*NET occupations", "reason": "O*NET's download page names no database file the "
                         "builder may read."})
        return None
    version = re.search(r"db_(\d+)_(\d+)_", url)
    version = f"{version.group(1)}.{version.group(2)}"
    path = K.download_file(url, cache)
    with zipfile.ZipFile(path) as z:
        tables = {}
        for member in z.namelist():
            base = member.rsplit("/", 1)[-1]
            if base in ONET_FILES:
                tables[base] = z.read(member).decode("utf-8", "replace")
    book = K.new_book(f"mw_{name}", f"Occupations: what each job does, its tasks and preparation (O*NET {version})",
                      "Jobs and careers", GROUP, "National Center for O*NET Development, for the US Department of "
                      "Labor, Employment and Training Administration", "CC BY 4.0",
                      "https://creativecommons.org/licenses/by/4.0/", ONET_DB_PAGE,
                      "Every occupation in the O*NET database, one page per occupation group: what the job does, the "
                      "job titles people in it report, its Job Zone (how much education, training and experience it "
                      "takes) and its tasks, core tasks first. For job hunting and choosing a career.",
                      onet_credit(version) + " Job details change: O*NET OnLine and My Next Move have the newest.",
                      changes="the database's occupation, task, title and Job Zone files arranged into one page per "
                              "occupation group; no words of a record changed")
    book.version = f"O*NET {version} Database (read {datetime.date.today().isoformat()})"
    book.published = K.last_modified(url)
    book.originals.append({"url": url, "kind": "zip", "size": os.path.getsize(path)})
    for path_, title, body, unit in onet_pages(tables, limit):
        book.pages.append(B.Page(path_, title, body, 0, unit))
    return book


def onet_sign(name):
    """O*NET's sign of change: the address of the newest database file (its version is in it) with its size."""
    import build_textbooks as B
    import updates
    url = onet_zip_url(B.fetch(ONET_DB_PAGE, None))
    return K.sha(url, updates.head_signs(url)) if url else ""


COLLECTION = K.Collection("mw", GROUP, guides=GUIDES, pdfs=PDFS,
                          makers={"onet_occupations": (onet_book, onet_sign)},
                          words={"money-work": lambda: [f"mw:{g['name']}" for g in PDFS + GUIDES] +
                                 ["mw:onet_occupations"]})

LICENCE_LINES = {
    "mw_irs": "www.irs.gov/pub/irs-pdf/ and www.irs.gov pages: works of the US government (17 U.S.C. 105, checked on "
              "govinfo.gov's policies page at every build); robots.txt allows /pub/ and the pages; no AI rules "
              "(checked 2026-11-22). Publication 535 is no longer published (its address now leads to the IRS's "
              "guide to business expense resources).",
    "mw_dol_nlrb_cms_cfpb": "www.dol.gov, www.nlrb.gov, www.healthcare.gov and www.consumerfinance.gov: works of the "
                            "US government (17 U.S.C. 105); robots.txt allows the pages read (healthcare.gov keeps "
                            "/help/, /es/ and its application pages out, which the builder obeys); no AI rules "
                            "(checked 2026-11-22).",
    "mw_onet": "www.onetcenter.org/license_db.html (checked at every build): \"the content of the O*NET 31.0 Database "
               "is licensed under a Creative Commons Attribution 4.0 International License\"; the credit for "
               "modified information and the trademark line are in the book's notice. robots.txt allows "
               "/dl_files/ (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("State tax departments' own guides (each state's income, sales and property tax basics)", "Link-only by the "
     "owner's rule: each state's site has its own terms. The IRS's list of every state's tax site is built "
     "(mw:irs_state_tax_agencies). Index: https://www.irs.gov/businesses/small-businesses-self-employed/"
     "state-government-websites"),
    ("IRS Publication 535, Business Expenses", "The IRS stopped publishing it after its 2022 edition; its address "
     "now leads to the IRS's guide to business expense resources. Publications 334, 463, 587 and 946 are built. "
     "Index: https://www.irs.gov/forms-pubs/guide-to-business-expense-resources"),
    ("Investor.gov (SEC investor education: saving and investing basics, compound interest, fraud)", "Public domain, "
     "but investor.gov answers programs \"403\" (robots.txt included, checked again 2026-11-22). Link-only. Index: "
     "https://www.investor.gov/introduction-investing"),
    ("FINRA investor insights and BrokerCheck", "Copyright of the Financial Industry Regulatory Authority; "
     "link-only. Index: https://www.finra.org/investors"),
    ("Social Security Administration publications (retirement benefits, how work affects benefits)", "Public "
     "domain, but www.ssa.gov answers programs \"403\" (checked 2026-11-22). Link-only. Index: "
     "https://www.ssa.gov/pubs/"),
    ("OSHA's workers' rights pages and OSHA 3021 (Workers' Rights)", "Public domain, but www.osha.gov answers "
     "programs \"403\", robots.txt included (checked 2026-11-22). Link-only. Index: https://www.osha.gov/workers"),
    ("Occupational Outlook Handbook (Bureau of Labor Statistics)", "Public domain, but www.bls.gov answers programs "
     "\"403\" (checked 2026-11-22); the Internet Archive's copies of recent editions are lending-library scans. "
     "O*NET's occupations are built instead (mw:onet_occupations). Index: https://www.bls.gov/ooh/"),
    ("CareerOneStop (job search, résumés, interviews, unemployment benefits finder; US Department of Labor)", "Its "
     "robots.txt shuts out programs (see the directory sources). Link-only. Index: https://www.careeronestop.org/"
     "JobSearch/job-search.aspx"),
    ("State unemployment insurance programmes (how to apply in each state)", "Each state's own site; link-only. "
     "Index: https://www.careeronestop.org/LocalHelp/UnemploymentBenefits/find-unemployment-benefits.aspx"),
    ("NAIC consumer insurance guides (home, car, life insurance) and the state insurance departments", "Copyright "
     "of the National Association of Insurance Commissioners; each state department is its own site. Link-only. "
     "Index: https://content.naic.org/consumer and https://content.naic.org/state-insurance-departments"),
    ("HUD's buying a home and tenant rights topic pages, and the state attorneys general's tenant guides", "HUD's "
     "topic pages keep their text in tab panels the builder cannot read whole; USA.gov's housing and tenant pages "
     "(help:usa_gov), the CFPB's Buying a House (mw:cfpb_buying_a_house) and the Fair Housing Act books "
     "(civic) are built. The attorneys general's guides are each state's own. Link-only. Index: "
     "https://www.hud.gov/topics/rental_assistance/tenantrights"),
    ("SCORE business mentoring and templates", "Copyright of SCORE; link-only. The SBA's guide is built "
     "(wb:sba_business_guide). Index: https://www.score.org/resource-library"),
    ("SBA Learning Platform courses", "The address now leads to the SBA's business guide, already built "
     "(wb:sba_business_guide). Index: https://www.sba.gov/sba-learning-platform"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
