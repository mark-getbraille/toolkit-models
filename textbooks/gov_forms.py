"""US federal government forms with their instructions, one book per form, for the reference library, in the group
"Reference, government forms" (the owner's request of 2026-11-22). Keys: gov-forms (every book), form:<name>.

What each book holds, in plain words:
  1. "What this form is for": the agency's own page about the form (the IRS's "About Form ..." page, Medicare's
     forms pages, VA's "About VA Form ..." page), its main part only, read at build time;
  2. the form itself, from the agency's official PDF address, its words as pages (the boxes and lines are read as
     their printed labels);
  3. its instructions: the separate instructions PDF when the agency publishes one (Form 1040's, Schedule C's,
     the 1099 instructions and so on); many forms (W-4, 4506-T, 8822, DS-11) print their instructions on their own
     pages, which are then part 2.
Made with pdf_set.pdf_set_book (each PDF read by build_textbooks.pdfdoc_book: robots.txt asked, the licence line
checked, a scan without words refused) and the agency page with refs_kit's reader.

Licence: every US federal form is a work of the US government (17 U.S.C. 105), not under copyright; the line is
checked on govinfo.gov's policies page at every build, as for the other US government books. robots.txt of irs.gov,
cms.gov, medicare.gov, va.gov, vba.va.gov, opm.gov and eforms.state.gov allows the files and pages, and none shuts
out AI readers (checked 2026-11-22).

Not built (NOT_INCLUDED, with the reason and the address, for the owner to fetch himself): the Social Security
Administration's forms (ssa.gov refuses programs, 403), USCIS's forms (uscis.gov refuses programs, 403), the FAFSA
(studentaid.gov does not answer programs), the Standard Form 50 (an agency's own personnel notice, not a form a person
fills in) and Optional Form 306 (opm.gov answered "not found").

The made-up filled-in SPECIMEN form pictures (laid out like a W-4, W-9, 1099-NEC and SS-5) are the picture pack
synthetic_gov_forms (packs/gov_forms_packs.py), never usable as real forms.

Run from the repository's folder:
  python3 textbooks/gov_forms.py form:irs_w4 --out build/textbooks --limit 3
  python3 textbooks/gov_forms.py --list gov-forms
"""

import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pdf_set  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "govforms"
GROUPS = {GROUP: "Reference, government forms"}

IRS_PDF = "https://www.irs.gov/pub/irs-pdf/"
IRS_ABOUT = "https://www.irs.gov/forms-pubs/about-"
CMS_PDF = "https://www.cms.gov/medicare/cms-forms/cms-forms/downloads/"
MEDICARE_FORMS = "https://www.medicare.gov/basics/forms-publications-mailings/forms/"
VA_ABOUT = "https://www.va.gov/forms/"
IRS = "Internal Revenue Service (IRS), US Department of the Treasury"
CMS = "Centers for Medicare & Medicaid Services (CMS), US Department of Health and Human Services"
VA = "US Department of Veterans Affairs (VA)"
STATE = "US Department of State, Bureau of Consular Affairs"
OPM = "US Office of Personnel Management (OPM)"

# Every book's notice: what the book is, and what to do with a real form.
FORM_NOTICE = ("A work of the US government (not under copyright). A reference copy, to read and understand the form: "
               "the agency changes its forms and instructions (tax forms every year), so file the current version "
               "from the agency's own site, or ask the agency for an accessible version (large print, braille, an "
               "accessible PDF) or for help filling it in. This is general information, not legal or tax advice. "
               "Never give your Social Security number or other private details to anyone who contacts you "
               "claiming to be from a government agency; contact the agency yourself.")


def form(name, title, subject, publisher, pdfs, about, description, about_main=None):
    """One form book: name, title, subject, publisher, pdfs [(part title, PDF address)], about (the agency's page
    about the form, "" when there is none a program may read), description, about_main (a regular expression pair
    of where the page's main part begins and ends, default <main>)."""
    return dict(name=name, title=title, subject=subject, publisher=publisher, pdfs=list(pdfs), about=about,
                description=description, about_main=about_main or K.MAIN)


def irs(name, number, title, files, about, description, subject="Taxes"):
    """An IRS form book: files ["fw4"] or ["f1040", "i1040gi"] (the form, then its instructions) at irs.gov/pub/irs-pdf;
    about the end of its "About ..." page address ("form-w-4")."""
    parts = [(("Instructions" if f.startswith("i") else f"The form ({number})"), f"{IRS_PDF}{f}.pdf") for f in files]
    return form(name, title, subject, IRS, parts, IRS_ABOUT + about, description)


FORMS = [
    # ------------------------------------------------------------------ IRS: the 1040 and its schedules
    irs("irs_1040", "Form 1040", "Form 1040, U.S. Individual Income Tax Return, and its instructions",
        ["f1040", "i1040gi"], "form-1040",
        "The yearly federal income tax return for individuals, with the IRS's line-by-line instructions and the tax "
        "tables."),
    irs("irs_1040_sr", "Form 1040-SR", "Form 1040-SR, U.S. Tax Return for Seniors", ["f1040sr"], "form-1040-sr",
        "The large-print version of Form 1040 for people 65 or older (its instructions are those of Form 1040)."),
    irs("irs_1040_schedule_1", "Schedule 1 (Form 1040)", "Schedule 1 (Form 1040), Additional Income and Adjustments "
        "to Income", ["f1040s1"], "schedule-1-form-1040",
        "The schedule for income not on Form 1040 itself (business, unemployment, alimony and others) and the "
        "adjustments (educator expenses, HSA, student loan interest); its instructions are in Form 1040's."),
    irs("irs_1040_schedule_2", "Schedule 2 (Form 1040)", "Schedule 2 (Form 1040), Additional Taxes", ["f1040s2"],
        "schedule-2-form-1040", "Additional taxes such as self-employment tax and the alternative minimum tax; its "
        "instructions are in Form 1040's."),
    irs("irs_1040_schedule_3", "Schedule 3 (Form 1040)", "Schedule 3 (Form 1040), Additional Credits and Payments",
        ["f1040s3"], "schedule-3-form-1040", "Credits and payments not on Form 1040 itself (foreign tax, child and "
        "dependent care, education, energy credits); its instructions are in Form 1040's."),
    irs("irs_1040_schedule_a", "Schedule A (Form 1040)", "Schedule A (Form 1040), Itemized Deductions, and its "
        "instructions", ["f1040sa", "i1040sca"], "schedule-a-form-1040",
        "Itemized deductions: medical and dental expenses, taxes, interest, gifts to charity, casualty losses."),
    irs("irs_1040_schedule_b", "Schedule B (Form 1040)", "Schedule B (Form 1040), Interest and Ordinary Dividends, "
        "and its instructions", ["f1040sb", "i1040sb"], "schedule-b-form-1040",
        "Listing interest and dividends over the limit, and foreign accounts and trusts."),
    irs("irs_1040_schedule_c", "Schedule C (Form 1040)", "Schedule C (Form 1040), Profit or Loss From Business, and "
        "its instructions", ["f1040sc", "i1040sc"], "schedule-c-form-1040",
        "The profit or loss of a business run as a sole proprietor or single-member LLC: income, expenses, cost of "
        "goods sold, car and home-office expenses."),
    irs("irs_1040_schedule_d", "Schedule D (Form 1040)", "Schedule D (Form 1040), Capital Gains and Losses, and its "
        "instructions", ["f1040sd", "i1040sd"], "schedule-d-form-1040",
        "Capital gains and losses from selling stocks, property and other capital assets."),
    irs("irs_1040_schedule_e", "Schedule E (Form 1040)", "Schedule E (Form 1040), Supplemental Income and Loss, and "
        "its instructions", ["f1040se", "i1040se"], "schedule-e-form-1040",
        "Income and loss from rental real estate, royalties, partnerships, S corporations, estates and trusts."),
    irs("irs_1040_schedule_se", "Schedule SE (Form 1040)", "Schedule SE (Form 1040), Self-Employment Tax, and its "
        "instructions", ["f1040sse", "i1040sse"], "schedule-se-form-1040",
        "Figuring the Social Security and Medicare tax of self-employed people."),
    irs("irs_1040_x", "Form 1040-X", "Form 1040-X, Amended U.S. Individual Income Tax Return, and its instructions",
        ["f1040x", "i1040x"], "form-1040-x", "Correcting a tax return already filed."),
    irs("irs_1040_es", "Form 1040-ES", "Form 1040-ES, Estimated Tax for Individuals", ["f1040es"], "form-1040-es",
        "Figuring and paying estimated tax on income without withholding (self-employment, interest, rent), with "
        "the worksheet and payment vouchers."),
    # ------------------------------------------------------------------ IRS: withholding, information returns, records
    irs("irs_w4", "Form W-4", "Form W-4, Employee's Withholding Certificate", ["fw4"], "form-w-4",
        "The form a worker gives an employer so the right federal income tax is withheld from pay; its "
        "instructions and worksheets are on its own pages."),
    irs("irs_w9", "Form W-9", "Form W-9, Request for Taxpayer Identification Number and Certification, and its "
        "instructions for the requester", ["fw9", "iw9"], "form-w-9",
        "The form a business or bank asks a person or company to fill in to give their taxpayer identification "
        "number (for 1099 reporting)."),
    irs("irs_1099_nec", "Form 1099-NEC", "Form 1099-NEC, Nonemployee Compensation, and the instructions for Forms "
        "1099-MISC and 1099-NEC", ["f1099nec", "i1099mec"], "form-1099-nec",
        "The form that reports payments to independent contractors and other people who are not employees."),
    irs("irs_1099_int", "Form 1099-INT", "Form 1099-INT, Interest Income, and its instructions",
        ["f1099int", "i1099int"], "form-1099-int", "The form banks and others send to report interest paid."),
    irs("irs_1099_div", "Form 1099-DIV", "Form 1099-DIV, Dividends and Distributions, and its instructions",
        ["f1099div", "i1099div"], "form-1099-div", "The form that reports dividends and capital gain distributions."),
    irs("irs_1099_r", "Form 1099-R", "Form 1099-R, Distributions From Pensions, Annuities, Retirement or "
        "Profit-Sharing Plans, IRAs, Insurance Contracts, etc., and its instructions", ["f1099r", "i1099r"],
        "form-1099-r", "The form that reports money paid out of pensions, annuities, IRAs and retirement plans."),
    irs("irs_1099_g", "Form 1099-G", "Form 1099-G, Certain Government Payments, and its instructions",
        ["f1099g", "i1099g"], "form-1099-g",
        "The form that reports unemployment compensation, state and local tax refunds and other government payments."),
    irs("irs_1099_k", "Form 1099-K", "Form 1099-K, Payment Card and Third Party Network Transactions, and its "
        "instructions", ["f1099k", "i1099k"], "form-1099-k",
        "The form payment card companies and payment apps send to report payments received for goods and services."),
    irs("irs_4506_t", "Form 4506-T", "Form 4506-T, Request for Transcript of Tax Return", ["f4506t"], "form-4506-t",
        "Asking the IRS for a free transcript of a past tax return or account (often asked for by lenders and "
        "colleges); its instructions are on its own pages."),
    irs("irs_8822", "Form 8822", "Form 8822, Change of Address", ["f8822"], "form-8822",
        "Telling the IRS about a new home address; its instructions are on its own pages."),
    # ------------------------------------------------------------------ Medicare (CMS)
    form("cms_40b", "Form CMS-40B, Application for Enrollment in Medicare Part B (Medical Insurance)",
         "Medicare", CMS, [("The form (CMS-40B) and its instructions", CMS_PDF + "cms40b-e.pdf")],
         MEDICARE_FORMS + "enrollment",
         "The form for signing up for Medicare Part B when you already have Part A, with its instructions."),
    form("cms_l564", "Form CMS-L564, Request for Employment Information", "Medicare", CMS,
         [("The form (CMS-L564) and its instructions", CMS_PDF + "cms-l564e.pdf")], MEDICARE_FORMS + "enrollment",
         "The employer's statement of group health coverage, given with the CMS-40B to sign up for Part B in a "
         "Special Enrollment Period without a late penalty."),
    form("cms_1763", "Form CMS-1763, Request for Termination of Premium Hospital and/or Supplementary Medical "
         "Insurance", "Medicare", CMS, [("The form (CMS-1763)", CMS_PDF + "cms1763.pdf")],
         MEDICARE_FORMS + "enrollment", "The form for ending premium Part A or Part B coverage."),
    form("cms_1490s", "Form CMS-1490S, Patient's Request for Medical Payment", "Medicare", CMS,
         [("The form (CMS-1490S) and its instructions", CMS_PDF + "cms1490s-english.pdf")], MEDICARE_FORMS + "other",
         "Filing a Medicare claim yourself when the doctor or supplier does not file it."),
    form("medicare_summary_notice", "The Medicare Summary Notice explained (with Enrolling in Medicare Part A & Part "
         "B)", "Medicare", CMS,
         [("Enrolling in Medicare Part A & Part B (CMS Product No. 11036)",
           "https://www.medicare.gov/publications/11036-enrolling-medicare-part-a-part-b.pdf")],
         "https://www.medicare.gov/basics/forms-publications-mailings/mailings/costs-and-coverage/"
         "medicare-summary-notice",
         "Medicare's own explanation of the Medicare Summary Notice (the statement people with Original Medicare get "
         "every 4 months listing the services billed, what Medicare paid and what you may owe), and Medicare's "
         "booklet on signing up for Parts A and B."),
    # ------------------------------------------------------------------ Veterans Affairs
    form("va_21_526ez", "VA Form 21-526EZ, Application for Disability Compensation and Related Compensation "
         "Benefits", "Veterans' benefits", VA,
         [("The form (21-526EZ) and its instructions", "https://www.vba.va.gov/pubs/forms/VBA-21-526EZ-ARE.pdf")],
         VA_ABOUT + "21-526ez/", "Applying for VA disability compensation, with the form's own instructions."),
    form("va_10_10ez", "VA Form 10-10EZ, Application for Health Benefits", "Veterans' benefits", VA,
         [("The form (10-10EZ) and its instructions", "https://www.va.gov/vaforms/medical/pdf/VA%20Form%2010-10EZ.pdf")],
         VA_ABOUT + "10-10ez/", "Applying for VA health care."),
    form("va_21_4138", "VA Form 21-4138, Statement in Support of Claim", "Veterans' benefits", VA,
         [("The form (21-4138)", "https://www.vba.va.gov/pubs/forms/VBA-21-4138-ARE.pdf")], VA_ABOUT + "21-4138/",
         "Giving VA more information in writing for a claim."),
    # ------------------------------------------------------------------ passports (State Department)
    form("state_ds_11", "Form DS-11, Application for a U.S. Passport", "Passports", STATE,
         [("The instructions and the form (DS-11)", "https://eforms.state.gov/Forms/ds11_pdf.pdf")], "",
         "Applying for a passport in person (first passport, child under 16, or when you cannot renew by mail): the "
         "State Department's instructions (who must apply in person, proof of citizenship and identity, the photo, "
         "fees) and the form. travel.state.gov refuses programs, so the form's own instruction pages are what this "
         "form is for."),
    form("state_ds_82", "Form DS-82, U.S. Passport Renewal Application for Eligible Individuals", "Passports", STATE,
         [("The instructions and the form (DS-82)", "https://eforms.state.gov/Forms/ds82_pdf.pdf")], "",
         "Renewing a passport by mail: who may renew by mail, the photo, fees and where to mail it, and the form."),
    # ------------------------------------------------------------------ federal jobs (OPM)
    form("opm_sf_15", "Standard Form 15, Application for 10-Point Veteran Preference", "Federal jobs", OPM,
         [("The form (SF-15) and its instructions", "https://www.opm.gov/forms/pdf_fill/sf15.pdf")], "",
         "Claiming 10-point veterans' preference in federal hiring (disabled veterans, Purple Heart recipients, and "
         "some spouses, widows and mothers of veterans), with its instructions and the documents to send."),
]
FORMS_BY_NAME = {f["name"]: f for f in FORMS}


def about_page(f, cache=None, left_out=None):
    """The "What this form is for" page (a build_textbooks.Page) from the agency's own page about the form, or None
    when there is none or a program may not read it."""
    import build_textbooks as B
    url = f["about"]
    if not url:
        return None
    if not K.readable(url, cache):
        left_out.append({"title": f"{f['title']}: the agency's page about it", "reason": "Its site's robots.txt does "
                         "not allow reading it."})
        return None
    text = B.fetch(url, cache)
    start, end = f["about_main"]
    m = re.search(start + r"(.*?)" + end, text, re.S)
    if not m:
        left_out.append({"title": f"{f['title']}: the agency's page about it", "reason": "Its main part was not "
                         "found."})
        return None
    body = m.group(1)
    for pattern in K.DROP:
        body = re.sub(pattern, "", body, flags=re.S)
    return B.Page("what-this-form-is-for", "What this form is for (from the agency's own page)",
                  B._Cleaner({}, url).clean(body), 0, "About this form")


def form_book(name, work, cache=None, left_out=None, limit=None):
    """The book of one form (FORMS): the agency's page about it, then the form and its instructions."""
    left_out = left_out if left_out is not None else []
    f = FORMS_BY_NAME.get(name)
    if f is None:
        left_out.append({"title": name, "reason": "Not a form of this module."})
        return None
    entry = K.us_pdf(GROUP, name=f"form_{name}", title=f["title"], subject=f["subject"], publisher=f["publisher"],
                     description=f["description"], notice=FORM_NOTICE, source=f["about"] or f["pdfs"][0][1])
    about = about_page(f, cache, left_out)
    parts = [(title, pdf, f["about"] or pdf) for title, pdf in f["pdfs"]]
    book = pdf_set.pdf_set_book(entry, parts, work, cache, left_out, limit) if parts else None
    if book is None and about is None:
        return None
    if book is None:                     # only the agency's page could be read
        book = K.new_book(f"form_{name}", f["title"], f["subject"], GROUP, f["publisher"], K.US_GOV, K.US_GOV_URL,
                          f["about"], f["description"], FORM_NOTICE)
    book.name, book.notice, book.description = f"form_{name}", FORM_NOTICE, f["description"]
    if about is not None:
        book.pages.insert(0, about)
        book.originals.insert(0, {"url": f["about"], "kind": "page"})
    book.version = f"the agency's current revision, read {datetime.date.today().isoformat()}"
    return book


def form_sign(name):
    """A form's weekly sign of change: the ETag, date and size of each of its PDFs (a new revision changes them)."""
    import updates
    f = FORMS_BY_NAME[name]
    return K.sha([updates.head_signs(pdf) for _t, pdf in f["pdfs"]], f["about"])


COLLECTION = K.Collection("form", GROUP, makers={f["name"]: (form_book, form_sign) for f in FORMS},
                          words={"gov-forms": lambda: [f"form:{f['name']}" for f in FORMS]})

LICENCE_LINES = {
    "gov_forms": "US federal forms and the agencies' pages about them (irs.gov, cms.gov, medicare.gov, va.gov, "
                 "vba.va.gov, eforms.state.gov, opm.gov): works of the US government (17 U.S.C. 105, the line checked "
                 "on govinfo.gov/about/policies at every build). robots.txt of each site allows the files and pages "
                 "and none shuts out AI readers (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("Social Security Administration forms: SSA-1 (application for retirement, survivors and disability "
     "information), SS-5 (Social Security card), SSA-827 (authorization to disclose), SSA-3368 (disability report, "
     "adult) and SSA-795 (statement of claimant)", "Public domain (US government works), but www.ssa.gov refuses "
     "programs (403 for every page and PDF, checked 2026-11-22), and no complete government or Internet Archive copy "
     "of the current forms was found. Link-only, for the owner to fetch himself (Program Downloader): "
     "https://www.ssa.gov/forms/ss-5.pdf, https://www.ssa.gov/forms/ssa-827.pdf, "
     "https://www.ssa.gov/forms/ssa-3368.pdf, https://www.ssa.gov/forms/ssa-795.pdf. Index: https://www.ssa.gov/forms/"),
    ("USCIS forms with their instructions: N-400 (naturalization), I-90 (replace a green card), I-130 (petition for a "
     "relative), I-765 (work permit) and I-131 (travel document)", "Public domain (US government works), but "
     "www.uscis.gov refuses programs (403, checked 2026-11-22); the Internet Archive holds only scattered perma.cc "
     "snapshots of old editions. Link-only: https://www.uscis.gov/sites/default/files/document/forms/n-400.pdf and "
     "the other forms' pages. The USCIS Policy Manual and guides are in the immigration books (immig:). Index: "
     "https://www.uscis.gov/forms/all-forms"),
    ("FAFSA, the Free Application for Federal Student Aid (studentaid.gov)", "studentaid.gov did not answer this "
     "build machine (the connection was dropped or timed out, checked 2026-11-22), and the FAFSA is filled in online "
     "(a PDF is mailed only on request). Link-only. Index: https://studentaid.gov/h/apply-for-aid/fafsa"),
    ("Standard Form 50 (Notification of Personnel Action) and Optional Form 306 (Declaration for Federal "
     "Employment)", "The SF-50 is the record an agency itself makes of a hiring or pay change, not a form a person "
     "fills in; opm.gov's addresses of the SF-50 and OF-306 answered with an error page and \"not found\" "
     "(checked 2026-11-22). Index: https://www.opm.gov/forms/standard-forms/"),
    ("Passport information pages of travel.state.gov", "travel.state.gov refuses programs (403); the DS-11 and DS-82 "
     "books use the forms' own instruction pages instead. Index: https://travel.state.gov/content/travel/en/"
     "passports.html"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
