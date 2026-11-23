"""Running a small business and taxes for the reference library (the owner's request of 2026-11-23), in the group
"Reference, money, work and business" (money_work.py's group). Keys: biz:<name>. Request words (each well under 256
jobs):
  biz-irs           the IRS publications and form instructions the library did not have yet, and the IRS's small
                    business and self-employed pages
  biz-sba-ftc       the FTC's business guides (from the Wayback Machine), the USDA's farmers' cooperative business
                    bulletin (1925) and an old book on running a shop
  biz-bookkeeping   old public-domain bookkeeping and accounting books
  business-tax      every book of this module, with the index

What this module builds, in plain words, each IN FULL:
  - the IRS publications not yet in the library, each the IRS's newest PDF from its official address
    (www.irs.gov/pub/irs-pdf/, robots.txt allows it): Publication 3 (Armed Forces' Tax Guide), 15-A and 15-B (the employer's supplemental and fringe benefits guides), 509 (Tax
    Calendars), 538 (Accounting Periods and Methods), 544 (Sales and Other Dispositions of Assets), 551 (Basis of
    Assets), 926 (Household Employer's Tax Guide), 936 (Home Mortgage Interest), 550 (Investment Income and Expenses),
    4681 (Canceled Debts, Foreclosures, Repossessions, and Abandonments), 527 (Residential Rental Property), 925
    (Passive Activity and At-Risk Rules), 1635 (Understanding Your EIN), 1779 (Independent Contractor or Employee),
    4591 (Small Business Federal Tax Responsibilities), 5 (Your Appeal Rights), 1546 (The Taxpayer Advocate Service)
    and 4134 (Low Income Taxpayer Clinic List); and the instructions for the main business forms: Forms 941 and 940
    (employment taxes), W-2 and W-3, 1065 (partnerships), 1120-S (S corporations), 4562 (depreciation), 8829
    (business use of the home), 8995 (the qualified business income deduction) and SS-4 (applying for an EIN);
  - the IRS's small business and self-employed pages (the tax centre, starting, operating and closing a business,
    business structures, sole proprietorships, recordkeeping, the home office deduction, employee or contractor,
    hiring employees, getting an EIN, self-employment tax and estimated taxes), each page whole;
  - the Federal Trade Commission's business guides, read from the Internet Archive's Wayback Machine copies (the FTC's
    own site refuses programs): its small business page, the advertising FAQs for small business, the Made in USA
    standard, the endorsement guides, the mail, internet and telephone order rule, protecting personal information,
    Start with Security and scams that target small businesses;
  - old public-domain books from the Internet Archive (published before 1931; the builder reads each item's record
    at every build): the USDA's Development and Present Status of Farmers' Cooperative Business Organizations
    (Bulletin 1302, 1925), David's Retail Store Management Problems (1922), and the bookkeeping books: Geijsbeek's
    Ancient Double-Entry Bookkeeping (Pacioli's treatise of 1494 in English, 1914), McKinsey's Bookkeeping and
    Accounting (1920), Day's Elementary Bookkeeping (1901), Koopman's Fundamentals of Accounting (1921), Bell's
    Accounting Principles (1921), Hatfield's Modern Accounting (1922), and the farm account books of Bexell (1911)
    and Goodyear (1911);
  - biz:index, "Running a small business and taxes: a guide to the library" (facts and links, CC0): every business
    and tax book here and elsewhere by key (IRS publications and forms, the SBA guide, the Peace Corps business
    manuals, OpenStax's business and accounting textbooks, OSHA's small business handbook, patents), and the
    link-only sources with the reason.
  Every book's notice ends with NOT_ADVICE: general information, not tax, legal or accounting advice.

Already in the library and not repeated: IRS Publications 17, 501, 502, 525, 526, 554, 590-A, 590-B, 596, 907, 915,
970 and 334 (sources.py and thin:taxes), 524 (blind:irs_pub_524), 1, 15, 463, 503, 505, 523, 529, 560, 583, 587,
594 and 946 (money_work.py),
the Form 1040 family, W-4, W-9 and the 1099s with their instructions (gov_forms.py), the SBA's business guide
(wb:sba_business_guide) and disaster loans (ready:sba_disaster_loans), the Peace Corps small enterprise and
microbusiness accounting manuals (pc-business), OpenStax Principles of Accounting, Introduction to Business,
Entrepreneurship and Principles of Finance (osbooks), OSHA's small business handbook (trade:), the NIST cybersecurity
guides for small business (privacy:) and the patents collection (pat:).

Not built (NOT_INCLUDED, link-only): IRS Publication 535 (discontinued after 2022), the SBA's own site pages beyond its
business guide and its 1973 "Starting and Managing a Small Business of Your Own" (the Internet Archive's copy is
lending-library only), SCORE (copyright), USDA Rural Development's cooperative reports and the Census Bureau's business
pages (both sites refuse programs), and the US Patent and Trademark Office's trademark basics (already in pat:'s
links).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
the old books by the pre-1931 year check.

Run from the repository's folder:
  python3 textbooks/business_tax.py biz:irs_pub_3 --out build/textbooks --limit 5
  python3 textbooks/business_tax.py --list business-tax
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import govinfo_kit as GK  # noqa: E402 - capture(), the Wayback Machine's exact copy of a page
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

PREFIX = "biz"
GROUP = "moneywork"                     # "Reference, money, work and business" (defined in money_work.py)
GROUPS = {}

# The line every book's notice ends with (the owner's rule for taxes, the law and money).
NOT_ADVICE = "General information, not tax, legal or accounting advice; check the current rules or ask a professional."
TAX_NOTE = ("Tax laws change every year: this is the IRS's newest edition (the weekly check rebuilds it when the IRS "
            "changes it). ")
IRS = "Internal Revenue Service (IRS), US Department of the Treasury"
IRS_PDF = "https://www.irs.gov/pub/irs-pdf/"


def irs_pdf(file, title, description, about):
    """One IRS publication or form instructions: its newest PDF at www.irs.gov/pub/irs-pdf/<file>.pdf; about: the
    end of its IRS "About ..." page address (None for a short publication the IRS gives no such page: then its page
    is the PDF itself)."""
    name = f"irs_pub_{file[1:]}" if file.startswith("p") else f"irs_{file}"
    return K.us_pdf(GROUP, name=name, title=title, subject="Taxes", publisher=IRS, pdf=f"{IRS_PDF}{file}.pdf",
                    page=f"https://www.irs.gov/forms-pubs/about-{about}" if about else f"{IRS_PDF}{file}.pdf",
                    description=description,
                    notice=f"A work of the Internal Revenue Service (public domain). {TAX_NOTE}{NOT_ADVICE}",
                    version="the newest revision at irs.gov when built (its revision date is on its first page)")


# ====================================================================== IRS publications and instructions

IRS_PUBS = [
    irs_pdf("p3", "Armed Forces' Tax Guide (IRS Publication 3)", "Tax rules for members of the armed forces: "
            "which military pay is taxed, combat zone exclusions, moving expenses, the extended deadlines and the "
            "credits.", "publication-3"),
    irs_pdf("p15a", "Employer's Supplemental Tax Guide (IRS Publication 15-A)", "Supplemental rules for employers: "
            "who is an employee or an independent contractor, sick pay, pensions and annuities, and other special "
            "kinds of pay.", "publication-15-a"),
    irs_pdf("p15b", "Employer's Tax Guide to Fringe Benefits (IRS Publication 15-B)", "Which fringe benefits are "
            "taxed and which are not (health plans, transport, meals, education assistance, achievement awards) and "
            "how employers withhold and report them.", "publication-15-b"),
    irs_pdf("p509", "Tax Calendars (IRS Publication 509)", "The year's tax calendars: the dates for filing returns, "
            "paying estimated tax, depositing employment taxes and sending information returns.", "publication-509"),
    irs_pdf("p538", "Accounting Periods and Methods (IRS Publication 538)", "Tax years (calendar and fiscal), the "
            "cash and accrual methods of accounting, inventories, and how to change a period or method.",
            "publication-538"),
    irs_pdf("p544", "Sales and Other Dispositions of Assets (IRS Publication 544)", "Selling, exchanging or giving "
            "up property: gains and losses, like-kind exchanges, capital and ordinary assets, and how to report them.",
            "publication-544"),
    irs_pdf("p551", "Basis of Assets (IRS Publication 551)", "How to work out the basis of property (what it cost "
            "you, adjusted over time) for depreciation, gains and losses.", "publication-551"),
    irs_pdf("p926", "Household Employer's Tax Guide (IRS Publication 926)", "The taxes owed when you employ someone "
            "in your home (a housekeeper, nanny, caregiver or personal assistant): Social Security and Medicare, "
            "federal unemployment tax, withholding and Schedule H.", "publication-926"),
    irs_pdf("p936", "Home Mortgage Interest Deduction (IRS Publication 936)", "Which home mortgage interest and "
            "points can be deducted, the limits, and how to figure them.", "publication-936"),
    irs_pdf("p550", "Investment Income and Expenses (IRS Publication 550)", "How interest, dividends, capital gains "
            "and losses and other investment income are taxed, and which investment expenses count.",
            "publication-550"),
    irs_pdf("p4681", "Canceled Debts, Foreclosures, Repossessions, and Abandonments (IRS Publication 4681)",
            "When a canceled or forgiven debt is taxable income, the exclusions (insolvency, bankruptcy, a main "
            "home), and the tax effects of foreclosure and repossession.", "publication-4681"),
    irs_pdf("p527", "Residential Rental Property (IRS Publication 527)", "Renting out a house, apartment or room: "
            "rental income and expenses, depreciation, personal use of a rental, and how to report it.",
            "publication-527"),
    irs_pdf("p925", "Passive Activity and At-Risk Rules (IRS Publication 925)", "The limits on deducting losses from "
            "rental property and businesses you do not take part in, and the at-risk rules.", "publication-925"),
    irs_pdf("p1635", "Understanding Your EIN (IRS Publication 1635)", "The employer identification number: who needs "
            "one, how to apply, and how to use and protect it.", None),
    irs_pdf("p1779", "Independent Contractor or Employee (IRS Publication 1779)", "The IRS's short guide to whether "
            "a worker is an employee or an independent contractor (behavioural control, financial control and the "
            "relationship), and what to do if you are not sure.", None),
    irs_pdf("p4591", "Small Business Federal Tax Responsibilities (IRS Publication 4591)", "A short checklist of the "
            "federal tax duties of a small business: the business structure, EIN, records, the taxes owed and the "
            "forms.", None),
    irs_pdf("p5", "Your Appeal Rights and How To Prepare a Protest If You Disagree (IRS Publication 5)", "How to "
            "appeal an IRS decision you disagree with: the IRS Independent Office of Appeals, writing a protest, and "
            "going to court.", None),
    irs_pdf("p1546", "The Taxpayer Advocate Service of the IRS (IRS Publication 1546)", "The Taxpayer Advocate "
            "Service, an independent office in the IRS that helps people whose tax problems are causing hardship or "
            "are not being solved, and how to reach it.", None),
    irs_pdf("p4134", "Low Income Taxpayer Clinic List (IRS Publication 4134)", "Every Low Income Taxpayer Clinic in "
            "the US by state, with contact details: clinics that help people with lower incomes in disputes with "
            "the IRS, free or for a small fee.", None),
]
IRS_INSTRUCTIONS = [
    irs_pdf("i941", "Instructions for Form 941, Employer's Quarterly Federal Tax Return (IRS)", "How employers report "
            "income tax withheld and Social Security and Medicare taxes every quarter, line by line.", "form-941"),
    irs_pdf("i940", "Instructions for Form 940, Employer's Annual Federal Unemployment (FUTA) Tax Return (IRS)",
            "How employers figure and report the yearly federal unemployment tax, line by line.", "form-940"),
    irs_pdf("iw2w3", "General Instructions for Forms W-2 and W-3 (IRS)", "How employers fill in and file the W-2 wage "
            "statement for each employee and the W-3 summary, box by box.", "form-w-2"),
    irs_pdf("i1065", "Instructions for Form 1065, U.S. Return of Partnership Income (IRS)", "How a partnership "
            "reports its income, deductions and each partner's share (Schedule K-1).", "form-1065"),
    irs_pdf("i1120s", "Instructions for Form 1120-S, U.S. Income Tax Return for an S Corporation (IRS)", "How an S "
            "corporation reports its income and each shareholder's share.", "form-1120-s"),
    irs_pdf("i4562", "Instructions for Form 4562, Depreciation and Amortization (IRS)", "How to claim depreciation, "
            "the section 179 deduction and amortization, and report listed property such as cars.", "form-4562"),
    irs_pdf("i8829", "Instructions for Form 8829, Expenses for Business Use of Your Home (IRS)", "How the "
            "self-employed figure the deduction for the business use of their home.", "form-8829"),
    irs_pdf("i8995", "Instructions for Form 8995, Qualified Business Income Deduction Simplified Computation (IRS)",
            "How owners of sole proprietorships, partnerships and S corporations figure the qualified business "
            "income deduction.", "form-8995"),
    irs_pdf("iss4", "Instructions for Form SS-4, Application for Employer Identification Number (IRS)", "How to "
            "apply for an EIN for a business, line by line.", "form-ss-4"),
]

SBSE = "https://www.irs.gov/businesses/small-businesses-self-employed"
SBSE_PAGES = [SBSE] + [f"{SBSE}/{p}" for p in (
    "self-employed-individuals-tax-center", "checklist-for-starting-a-business", "starting-a-business",
    "operating-a-business", "closing-a-business", "business-structures", "sole-proprietorships", "recordkeeping",
    "what-kind-of-records-should-i-keep", "how-long-should-i-keep-records", "home-office-deduction",
    "independent-contractor-self-employed-or-employee", "hiring-employees", "get-an-employer-identification-number",
    "self-employment-tax-social-security-and-medicare-taxes", "estimated-taxes")]
IRS_GUIDES = [
    X.page_list_book(
        GROUP, "irs_small_business_pages", "Small business and self-employed: the IRS's pages for starting, running "
        "and closing a business", "Small business taxes", IRS, SBSE_PAGES,
        r"^https://www\.irs\.gov/businesses/small-businesses-self-employed(/[a-z0-9-]+)?$",
        "The IRS's pages for small businesses and the self-employed, each whole: the self-employed individuals tax "
        "centre, the checklist for starting a business, starting, operating and closing a business, business "
        "structures and sole proprietorships, recordkeeping (what records to keep and for how long), the home "
        "office deduction, whether a worker is an employee or an independent contractor, hiring employees, getting "
        "an employer identification number, self-employment tax and estimated taxes.",
        f"A work of the Internal Revenue Service (public domain). {TAX_NOTE}{NOT_ADVICE}",
        units=[(r"start|structures|sole|employer-identification", "Starting a business"),
               (r"record", "Records"), (r"hiring|contractor", "Workers and employees"),
               (r"self-employ|estimated|home-office", "Self-employed"), (r".", "Running a business")]),
]

# ====================================================================== FTC business guides (Wayback Machine copies)

FTC = "https://www.ftc.gov/business-guidance/"
# (capture stamp, official address): the Wayback Machine's captures found with its availability API on 2026-11-23.
FTC_PAGES = [
    ("20261102004802", FTC + "small-businesses"),
    ("20261105114737", FTC + "resources/advertising-faqs-guide-small-business"),
    ("20261105113251", FTC + "resources/complying-made-usa-standard"),
    ("20261031154923", FTC + "resources/ftcs-endorsement-guides-what-people-are-asking"),
    ("20261031020125", FTC + "resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule"),
    ("20261102044157", FTC + "resources/protecting-personal-information-guide-business"),
    ("20261106220656", FTC + "resources/start-security-guide-business"),
    ("20261031073540", FTC + "resources/scams-your-small-business-guide-business"),
]
FTC_NEWEST = max(GK.stamp_date(s) for s, _u in FTC_PAGES)
FTC_OLDEST = min(GK.stamp_date(s) for s, _u in FTC_PAGES)
FTC_GUIDES = [
    X.page_list_book(
        GROUP, "ftc_business_guides_wayback", "Business guides from the Federal Trade Commission: advertising, Made "
        "in USA, online selling, data security and scams", "Small business: consumer protection rules",
        "Federal Trade Commission (FTC), Bureau of Consumer Protection", [GK.capture(s, u) for s, u in FTC_PAGES],
        r"^https://web\.archive\.org/web/\d{14}id_/https://www\.ftc\.gov/business-guidance/",
        "The FTC's guides for businesses, each whole: its small business page, the advertising FAQs for small "
        "business (truth in advertising, evidence for claims, free offers, guarantees), complying with the Made in "
        "USA standard, the endorsement guides (reviews, influencers and testimonials), the mail, internet and "
        "telephone order rule (shipping on time, delays and refunds), protecting personal information (a guide for "
        "business), Start with Security (lessons from the FTC's cases) and scams that target small businesses.",
        f"A work of the Federal Trade Commission (public domain). Read from the Internet Archive's Wayback Machine "
        f"copies of the FTC's own pages (captured {FTC_OLDEST} to {FTC_NEWEST}) because www.ftc.gov refuses "
        f"programs; the rules may have changed since: check www.ftc.gov/business-guidance. {NOT_ADVICE}",
        units=[(r"advertising|endorsement|made-usa", "Advertising and labels"), (r"order", "Selling by mail and "
               "online"), (r"personal-information|security", "Data security"), (r"scams", "Scams"),
               (r".", "Small business")],
        content=(r"<main\b[^>]*>", r"</main>"), version=f"Wayback Machine copies captured {FTC_OLDEST} to "
        f"{FTC_NEWEST}", published=FTC_NEWEST),
]

# ====================================================================== old books

OLD_BUSINESS = ("Published in {year}: an old book; its prices, laws and tax rules are long out of date, but its "
                "principles of running a business are still taught.")
OLD_BOOKS = ("Published in {year}: an old book; its methods of double entry and the accounts still work, but its "
             "forms, tax rules and prices are of its time, and today's books are kept with software.")
OLD_PDFS = [
    old_book(GROUP, "usda_farmers_cooperative_business_1925", "Development and Present Status of Farmers' "
             "Cooperative Business Organizations (USDA Bulletin 1302, 1925)", "Cooperatives",
             "R. H. Elsworth, US Department of Agriculture", "developmentprese1302elsw", 1925,
             "The USDA's survey of farmers' cooperatives in the 1920s: how cooperative marketing and purchasing "
             "associations began and grew, the kinds of products they handled, how they were organised and their "
             "numbers state by state.", note=OLD_BUSINESS + " A work of the US government.", notice=NOT_ADVICE),
    old_book(GROUP, "david_retail_store_management_1922", "Retail Store Management Problems (Donald K. David, 1922)",
             "Running a shop", "Donald Kirk David (A. W. Shaw)", "cu31924013822824", 1922,
             "Cases from real shops on the problems of running a retail store: buying and stock control, pricing and "
             "mark-up, selling and advertising, credit and collections, staff, and keeping expenses down.",
             note=OLD_BUSINESS, notice=NOT_ADVICE),
]
BOOKKEEPING_PDFS = [
    old_book(GROUP, "geijsbeek_ancient_double_entry_1914", "Ancient Double-Entry Bookkeeping: Lucas Pacioli's "
             "Treatise of 1494 (John B. Geijsbeek, 1914)", "Bookkeeping: history", "John B. Geijsbeek",
             "cu31924030162147", 1914,
             "The first printed book on double-entry bookkeeping, Luca Pacioli's treatise of 1494, translated into "
             "English, with the early English, Dutch and other followers: the journal, the ledger and the "
             "inventory, as merchants kept them.", note=OLD_BOOKS, notice=NOT_ADVICE),
    old_book(GROUP, "mckinsey_bookkeeping_accounting_1920", "Bookkeeping and Accounting (James O. McKinsey, 1920)",
             "Bookkeeping", "James O. McKinsey (South-Western Publishing)", "bookkeepingaccou01mckiuoft", 1920,
             "A complete course in bookkeeping: the accounts, debits and credits, the journal and ledger, the trial "
             "balance, adjusting and closing entries, financial statements, and the books of a business.",
             note=OLD_BOOKS, notice=NOT_ADVICE),
    old_book(GROUP, "day_elementary_bookkeeping_1901", "Elementary Bookkeeping (W. G. Day, 1901)", "Bookkeeping",
             "W. G. Day (Gee and Co.)", "elementarybookke00daywrich", 1901,
             "A first course in bookkeeping by double entry: cash books, day books, the ledger, the trial balance and "
             "the balance sheet, with exercises.", note=OLD_BOOKS, notice=NOT_ADVICE, country="United Kingdom"),
    old_book(GROUP, "koopman_fundamentals_accounting_1921", "Fundamentals of Accounting: Principles and Practice of "
             "Bookkeeping (Sietse B. Koopman, 1921)", "Bookkeeping", "Sietse Bernard Koopman (Ronald Press)",
             "fundamentalsofac01koopiala", 1921,
             "The principles and practice of bookkeeping: the balance sheet and profit and loss statement, accounts "
             "and their classification, books of original entry, controlling accounts, and the accounting cycle.",
             note=OLD_BOOKS, notice=NOT_ADVICE),
    old_book(GROUP, "bell_accounting_principles_1921", "Accounting Principles: Their Use in Business Management "
             "(Spurgeon Bell, 1921)", "Accounting", "Spurgeon Bell (Macmillan)", "accountingprinci00belliala", 1921,
             "Accounting for the business manager: what the balance sheet and income statement show, costs, "
             "depreciation, reserves, and how to use accounts to run a business.", note=OLD_BOOKS, notice=NOT_ADVICE),
    old_book(GROUP, "hatfield_modern_accounting_1922", "Modern Accounting: Its Principles and Some of Its Problems "
             "(Henry Rand Hatfield, 1922 printing)", "Accounting", "Henry Rand Hatfield (D. Appleton)",
             "modernaccounting00hatfuoft", 1922,
             "A classic text on the principles of accounting: valuing assets, depreciation, capital and surplus, "
             "reserves and the balance sheet, explained with their reasons.", note=OLD_BOOKS, notice=NOT_ADVICE),
    old_book(GROUP, "bexell_farm_accounting_1911", "Farm Accounting and Business Methods (J. A. Bexell, 1911)",
             "Bookkeeping: farm accounts", "J. A. Bexell (The Home Correspondence School)", "farmaccountingbu00bexerich",
             1911,
             "Bookkeeping for the farm: inventories, cash and crop accounts, livestock records, cost accounts, and "
             "business methods for buying and selling.", note=OLD_BOOKS, notice=NOT_ADVICE),
    old_book(GROUP, "goodyear_farm_accounting_1911", "Farm Accounting for the Practical Farmer (Lloyd E. Goodyear, "
             "1911)", "Bookkeeping: farm accounts", "Lloyd E. Goodyear (Goodyear-Marshall)", "farmaccountingfo00goodrich",
             1911,
             "A simple system of farm accounts for the working farmer: the cash book, the ledger, inventories and "
             "finding the profit of each crop and animal.", note=OLD_BOOKS, notice=NOT_ADVICE),
]

PDFS = IRS_PUBS + IRS_INSTRUCTIONS + OLD_PDFS + BOOKKEEPING_PDFS
GUIDES = IRS_GUIDES + FTC_GUIDES


def keys_of(entries):
    """The build keys of some entries of this module."""
    return [f"{PREFIX}:{e['name']}" for e in entries]


# ====================================================================== the index

INDEX_SECTIONS = [
    ("Taxes: the IRS's publications and forms", "Every IRS publication and form book in the library. Tax laws change "
     "every year: each book is the IRS's newest edition when built.",
     [("key", k, e["title"]) for k, e in zip(keys_of(IRS_GUIDES + IRS_PUBS + IRS_INSTRUCTIONS),
                                              IRS_GUIDES + IRS_PUBS + IRS_INSTRUCTIONS)] +
     [("key", "pdf:irs_pub_17_your_federal_income_tax", "Your Federal Income Tax (IRS Publication 17)"),
      ("key", "pdf:irs_pub_907_tax_highlights_disabilities", "Tax Highlights for Persons With Disabilities (IRS "
                                                             "Publication 907)"),
      ("key", "pdf:irs_pub_554_tax_guide_seniors", "Tax Guide for Seniors (IRS Publication 554)"),
      ("word", "thin:taxes", "IRS Publications 501, 502, 525, 526, 590-A, 590-B, 596, 915, 970 and 334 (Tax Guide "
                             "for Small Business)"),
      ("word", "money-work", "IRS Publications 1, 15, 463, 503, 505, 523, 529, 560, 583 (Starting a Business and "
                             "Keeping Records), 587, 594 and 946, the Form 1040 instructions and the states' tax "
                             "sites, with the Department of Labor's pages"),
      ("word", "gov-forms", "the federal forms with their instructions: Form 1040 and its schedules (C and SE for "
                            "the self-employed), W-4, W-9, the 1099s, 4506-T and 8822"),
      ("key", "blind:irs_pub_524", "Credit for the Elderly or the Disabled (IRS Publication 524)"),
      ("key", "aging:irs_deceased_person", "Taxes after someone dies (IRS)"),
      ("key", "power:irs_form_5695_instructions", "Instructions for Form 5695, Residential Energy Credits")]),
    ("Starting and running a business", "Guides to starting, running and protecting a small business.",
     [("key", k, e["title"]) for k, e in zip(keys_of(FTC_GUIDES + OLD_PDFS), FTC_GUIDES + OLD_PDFS)] +
     [("word", "wb:sba_business_guide", "the SBA's business guide: plan, launch, manage and grow your business"),
      ("key", "ready:sba_disaster_loans", "SBA disaster loans for homeowners, renters and businesses"),
      ("word", "pc-business", "the Peace Corps' small enterprise, management consulting and microbusiness manuals"),
      ("word", "osbooks:introduction-business", "OpenStax Introduction to Business (a college textbook)"),
      ("word", "osbooks:entrepreneurship", "OpenStax Entrepreneurship (a college textbook)"),
      ("word", "osbooks:principles-finance", "OpenStax Principles of Finance (a college textbook)"),
      ("key", "trade:osha_2209_small_business_handbook", "OSHA Handbook for Small Businesses"),
      ("key", "privacy:nist_ir_7621_small_business", "Small Business Information Security (NIST IR 7621)"),
      ("key", "privacy:nist_sp_1300_csf_small_business", "NIST Cybersecurity Framework: Small Business Quick-Start "
                                                         "Guide"),
      ("word", "patents", "the patents collection (famous patents, assistive and household patents)"),
      ("key", "olife:johnston_new_business_letter_writer_1920", "The New Business Letter Writer (1920)"),
      ("manuals", "money_devices", "money counters and cash registers"),
      ("manuals", "office_equipment", "printers, copiers and other office equipment")]),
    ("Bookkeeping and accounting", "Old bookkeeping books (the method of double entry has not changed) and the open "
     "accounting textbooks.",
     [("key", k, e["title"]) for k, e in zip(keys_of(BOOKKEEPING_PDFS), BOOKKEEPING_PDFS)] +
     [("key", "pc:accounting_microbusiness_1982", "Accounting for the Microbusiness (Peace Corps, 1982)"),
      ("word", "osbooks:principles-accounting-bundle", "OpenStax Principles of Accounting, Volumes 1 and 2 "
                                                       "(financial and managerial; CC BY-NC-SA, personal use)"),
      ("key", "skill:usmc_mci_personal_finance_1985", "Personal Finance (Marine Corps Institute, 1985)"),
      ("word", "emath-practical", "business arithmetic books (interest, discounts, payroll) in the everyday maths "
                                  "collection")]),
    ("Links only", "Sources that are not built, with the reason; open them in a browser.",
     [("link", "SCORE business mentoring and templates", "https://www.score.org/resource-library",
       "Copyright of SCORE; link-only."),
      ("link", "SBA Learning Center and its pages beyond the business guide", "https://www.sba.gov/sba-learning-"
       "platform", "The SBA's business guide is built (wb:sba_business_guide); its learning platform address now "
       "leads to that guide."),
      ("link", "USDA Rural Development: cooperative publications", "https://www.rd.usda.gov/resources/publications",
       "Public domain, but www.rd.usda.gov refuses programs; open it in a browser."),
      ("link", "Census Bureau business data and guides", "https://www.census.gov/topics/business-economy.html",
       "Data tools, not books; open them in a browser."),
      ("link", "USPTO trademark basics", "https://www.uspto.gov/trademarks/basics", "Public domain web pages; see "
       "the patents collection (pat:) for the USPTO's own sources."),
      ("link", "IRS Publication 535 (Business Expenses)", "https://www.irs.gov/forms-pubs/guide-to-business-expense-"
       "resources", "Discontinued by the IRS after its 2022 edition; Publications 334, 463, 587 and 946 cover the "
       "same ground.")]),
]

INDEX_BOOK, INDEX_SIGN = X.index_maker(
    PREFIX, GROUP, "Running a small business and taxes: a guide to the library", "Small business and taxes",
    "A guide to the library's books on running a small business and on taxes: the IRS's publications and forms, "
    "starting and running a business, bookkeeping and accounting, with the key of each book and the sources that "
    "are links only.", INDEX_SECTIONS)

WORDS = {
    "biz-irs": lambda: keys_of(IRS_GUIDES + IRS_PUBS + IRS_INSTRUCTIONS),
    "biz-sba-ftc": lambda: keys_of(FTC_GUIDES + OLD_PDFS),
    "biz-bookkeeping": lambda: keys_of(BOOKKEEPING_PDFS),
    "business-tax": lambda: [f"{PREFIX}:index"] + keys_of(GUIDES + PDFS),
}
COLLECTION = K.Collection(PREFIX, GROUP, guides=GUIDES, pdfs=PDFS, makers={"index": (INDEX_BOOK, INDEX_SIGN)},
                          words=WORDS)

LICENCE_LINES = {
    "biz_irs": "www.irs.gov/pub/irs-pdf/ and the www.irs.gov small business pages: works of the US government (17 "
               "U.S.C. 105, checked on govinfo.gov's policies page at every build); robots.txt allows /pub/ and the "
               "pages; no AI rules (checked 2026-11-23).",
    "biz_ftc_wayback": "web.archive.org: the Wayback Machine's exact copies (\"id_\") of the FTC's business guidance "
                       "pages, works of the US government (17 U.S.C. 105); www.ftc.gov itself answers programs "
                       "\"403\" (checked 2026-11-23).",
    "biz_old_books": "archive.org (its robots.txt allows the files): books published before 1931 are in the US public "
                     "domain; the builder checks each item's year on the Internet Archive's record at every build. "
                     "USDA Bulletin 1302 (1925) is also a work of the US government.",
    "biz_index": "The index (biz:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("Starting and Managing a Small Business of Your Own (Wendell O. Metcalf, SBA, 1973)", "A US government work, "
     "but the Internet Archive's copy is lending-library only (checked 2026-11-23). Link-only. Index: "
     "https://archive.org/details/startingmanaging00metc"),
    ("USDA Rural Development cooperative publications (Cooperative Information Reports)", "Public domain, but "
     "www.rd.usda.gov answers programs \"Access Denied\" (robots.txt included, checked 2026-11-23); the 1925 USDA "
     "bulletin on farmers' cooperatives is built (biz:usda_farmers_cooperative_business_1925). Index: "
     "https://www.rd.usda.gov/resources/publications"),
    ("FTC Franchise Rule guides (A Consumer's Guide to Buying a Franchise)", "No recent Wayback Machine copy was "
     "found (checked 2026-11-23); www.ftc.gov refuses programs. Index: https://www.ftc.gov/business-guidance/"
     "resources/consumer-guide-buying-franchise"),
    ("Census Bureau business pages and data guides (census.gov/topics/business-economy)", "Data tools and tables "
     "rather than books; not built. Index: https://www.census.gov/topics/business-economy.html"),
    ("Department of Education LINCS and SBA Learning Center courses", "LINCS refuses programs (\"403\", checked "
     "2026-11-23); the SBA's learning platform now leads to its business guide (wb:sba_business_guide). Index: "
     "https://lincs.ed.gov/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
