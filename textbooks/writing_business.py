"""Writing and business communication guides for the reference library, in the group "writing" ("Reference, writing
and business"), the owner's request of 2026-11-21. Keys: writing (every book here), wb:<name> (one book).

What this module builds, in plain words: official writing guides, style manuals and small-business and grant-writing
guides, each one IN FULL (every page of the web guide, or the whole PDF), read only from the publisher's own site, its
own public repository, or the Internet Archive's copy where the publisher's site shuts programs out. Every site's
robots.txt was read by hand on 2026-11-21 and is obeyed again at every build; a site whose robots.txt shuts out AI
companies' readers by name or says "ai-train=no" is never read (directory_sources.ai_refused). Requests go one at a
time with a pause (build_textbooks.fetch: at least a second, or the Crawl-delay a site asks for).

  Plain language (US government, public domain): the Federal Plain Language Guidelines (March 2011, revision 1 May
    2011: the PDF from the General Services Administration's own plainlanguage.gov repository on GitHub, as the old
    site now forwards to digital.gov); the plainlanguage.gov examples (before-and-after, award winners, letters,
    handbooks, regulations), from the same repository's pages; and digital.gov's plain language guide, which
    replaced the old site.
  Style and correspondence manuals (US government, public domain; military ones only with "Approved for public
    release; distribution unlimited"): the GPO Style Manual (2016, from govinfo), the Department of the Navy
    Correspondence Manual (SECNAV M-5216.5, 2010 edition) and the Air Force's Tongue and Quill (AFH 33-337, 2004
    edition), the last two from the Internet Archive's copies of the Defense Technical Information Center's records
    (the Navy's and Air Force's own publication sites refuse programs).
  Small business (public domain): the US Small Business Administration's business guide (plan, launch, manage and
    grow your business, with its marketing, business-plan and startup-cost sections).
  Grant writing (public domain): NIH's "Write your application" pages and NSF's Proposal and Award Policies and
    Procedures Guide (PAPPG 24-1).
  Workplace and HR (public domain): the US Office of Personnel Management's handbooks on measuring employee
    performance, structured interviews, assessment, position classification, the writing-and-editing grade guide and
    delegated examining.
  UK government (Open Government Licence v3.0): GOV.UK's content and publishing guidance "Writing to GOV.UK
    standards" (the A to Z style guide, the technical style guide, writing guidelines, planning and managing
    content), with the non-US note on spelling and style.

Every book has its licence and notice, "published" (the publisher's own date), "version" (the edition read), the key
and fingerprint for the weekly update check (sign()), and "originals" (the builder's originals_of: every page or
file read, with may_download from the licence and robots.txt). Nothing here is personal use only; the Canadian
government's writing tools, which would have been, cannot be read under the owner's rules (NOT_INCLUDED).

What was already in the library (the open business-communication textbooks, through LibreTexts' catalogue and
OpenStax), and what was looked at and not built, with the reason, are in NOT_INCLUDED.

sources.py imports this module at its end (adds GROUPS, LICENCE_LINES, NOT_INCLUDED and PRACTICE_SUBJECTS); the
builder (build_textbooks.build) sends the wb: keys here and the weekly check (updates.fingerprint) asks sign(). This
module imports the builder only inside its functions, because the builder imports sources. Run from the repository's
folder:
  python3 textbooks/writing_business.py wb:gpo_style_manual --out build/textbooks
  python3 textbooks/writing_business.py wb:sba_business_guide --out build/textbooks --limit 3     (a small test)
  python3 textbooks/writing_business.py --list writing
"""

import argparse
import datetime
import html
import json
import os
import re
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# These names are the same as in sources.py (this module is imported at its end, so it cannot import them).
US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"
GOVINFO_POLICY = "https://www.govinfo.gov/about/policies"
GOVINFO_TEXT = r"Copyright protection under this title is not available for any work of the United States Government"
OGL_UK_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

GROUP = "writing"
GROUPS = {GROUP: "Reference, writing and business"}

MAIN = (r"<main\b[^>]*>", r"</main>")
DROP = [r"<nav\b.*?</nav>", r"<aside\b.*?</aside>", r"<form\b.*?</form>", r"<button\b.*?</button>"]
US = dict(group=GROUP, country="United States", licence=US_GOV, licence_url=US_GOV_URL, licence_page=GOVINFO_POLICY,
          licence_text=GOVINFO_TEXT, level="reference")
WEB = dict(page_mark="", start=[], units="", sitemap="", unit_rules=[], content=MAIN, drop=DROP)
US_WEB = dict(US, **WEB)

# The words a Defense Technical Information Center record's report page (form SF 298) uses for a public-release
# document, allowing the machine-read text's slips ("distrihution") and with or without "is".
PUBLIC_RELEASE = r"(?i)approved\s+for\s+public\s+release\s*[;:,.]?\s*distri\w{4,8}\s+(?:is\s+)?unlimited"

PLG_REPO = "https://github.com/GSA/plainlanguage.gov"
PLG_RAW = "https://raw.githubusercontent.com/GSA/plainlanguage.gov/main"
PLG_LICENCE_TEXT = r"As a work of the United States Government, this project is in the\s+public domain"


# ====================================================================== web guides (read page by page)

GUIDES = [
    dict(US_WEB, name="digital_gov_plain_language", title="Plain language guide (digital.gov)",
         subject="Plain language writing", publisher="General Services Administration (GSA), digital.gov, with the "
         "Plain Language Action and Information Network (PLAIN)", source="https://digital.gov/guides/plain-language",
         description="The US government's current plain language guide, which replaced plainlanguage.gov: the "
                     "principles (write for your reader, organize, keep it short and simple, avoid jargon), writing "
                     "(clear and short, style, special cases), design (headings, lists, tables, links, visuals) and "
                     "testing (paraphrase testing, usability testing, comparative studies); every page.",
         notice="A work of the US General Services Administration (not under copyright in the United States).",
         sitemap="https://digital.gov/sitemap.xml", pages=r"^https://digital\.gov/guides/plain-language(/[a-z0-9-]+)*$",
         content=(r'id="content-start"[^>]*>', r'<div class="dg-guide__prev-next|</main>'),
         title_from=r"<title>\s*([^<|]+?)\s*\|",
         unit_rules=[(r"/principles", "Principles"), (r"/writing", "Writing"), (r"/design", "Design"),
                     (r"/test", "Testing"), (r".", "About the guide")],
         version="digital.gov guide as published", limit=40),
    dict(US_WEB, name="sba_business_guide", title="Small business guide: plan, launch, manage and grow your "
         "business (US Small Business Administration)", subject="Small business: business plans, marketing and "
         "management", publisher="US Small Business Administration (SBA)",
         source="https://www.sba.gov/counseling/",
         licence_page="https://www.sba.gov/about-sba/open-government/about-the-sba-gov-website/",
         licence_text=r"Government information on SBA\.gov is in the public domain",
         description="The SBA's business guide, every page of it: get started (assess your business, basic "
                     "requirements, size standards), plan your business (market research and competitive analysis, "
                     "writing a business plan, startup costs, business credit, funding, buying a business or "
                     "franchise), launch your business (location, structure, name, registration, tax IDs, licences "
                     "and permits, bank account), manage your business (finances, marketing and sales, hiring and "
                     "managing employees, taxes, insurance, cybersecurity, staying legally compliant), grow your "
                     "business, winning government contracts, and where to find free local help.",
         notice="Government information on SBA.gov is in the public domain; the SBA asks that it be acknowledged "
                "as the source. Information, not legal, tax or financial advice. The business plan templates the "
                "guide names are Word files on legacy.sba.gov, whose robots.txt does not allow programs to fetch "
                "them, so they are not in this book: open the links in a browser.",
         sitemap="https://www.sba.gov/page-sitemap.xml",
         pages=r"^https://www\.sba\.gov/counseling/(?!.*(?:-tool|-calculator|-lookup)/$)(get-started|plan-your-business|launch-your-business|"
               r"manage-your-business|grow-your-business|governing-rules-and-responsibilities|how-to-win-contracts|"
               r"prime-and-subcontracting|local-assistance|trade-tools-for-international-sales)(/[a-z0-9-]+)*/$",
         unit_rules=[(r"/get-started", "Get started"), (r"/plan-your-business", "Plan your business"),
                     (r"/launch-your-business", "Launch your business"),
                     (r"/manage-your-business|/governing-rules", "Manage your business"),
                     (r"/grow-your-business|/trade-tools", "Grow your business"),
                     (r"contracts|subcontracting", "Government contracting"), (r".", "Local help")],
         version="sba.gov business guide as published", limit=60),
    dict(US_WEB, name="nih_write_application", title="Write your application: NIH grant-writing guide",
         subject="Grant writing (research grants)", publisher="National Institutes of Health (NIH), Office of "
         "Extramural Research", source="https://grants.nih.gov/grants-process/write-application",
         description="NIH's guide to writing a grant application, every page: general grant-writing tips "
                     "(communicating your research's intent and value, tables, charts and figures), advice on the "
                     "application's sections (budget, reference letters), the How to Apply application guide (which "
                     "instructions to use, formatting attachments, page limits, rules for text fields), and sample "
                     "applications and annotated form sets. The forms themselves are listed, not included.",
         notice="A work of the National Institutes of Health (not under copyright in the United States). NIH's "
                "rules change: check the current notice of funding opportunity before you apply.",
         crawl=[("https://grants.nih.gov/grants-process/write-application", 2)],
         follow=r"^https://grants\.nih\.gov/grants-process/write-application(/(?!forms-directory)[a-z0-9-]+)?$",
         pages=r"^https://grants\.nih\.gov/grants-process/write-application(/(?!forms-directory/)[a-z0-9-]+)*$",
         unit_rules=[(r"/general-grant-writing-tips", "General grant-writing tips"),
                     (r"/advice-on-application-sections", "Advice on application sections"),
                     (r"/how-to-apply-application-guide", "How to Apply: the application guide"),
                     (r"/samples-applications", "Sample applications"), (r".", "Write your application")],
         version="grants.nih.gov pages as published", limit=80),
    dict(US_WEB, name="nsf_pappg", title="Proposal and Award Policies and Procedures Guide (NSF PAPPG 24-1)",
         subject="Grant writing (research proposals)", publisher="US National Science Foundation (NSF)",
         source="https://www.nsf.gov/policies/pappg/24-1",
         description="NSF's guide to preparing and submitting research proposals and managing awards, every "
                     "chapter: pre-submission, proposal preparation (the project summary, description, references, "
                     "biographical sketches, budget and budget justification, data management plan), processing and "
                     "review (the merit review criteria), declines and withdrawals, renewals, awards and their "
                     "administration, financial requirements, recipient standards, allowable costs and disputes, "
                     "with the summary of changes and the subject index.",
         notice="A work of the National Science Foundation (not under copyright in the United States). This is "
                "PAPPG 24-1, effective 20 May 2024, as NSF publishes it with its supplements; NSF says its Guidance "
                "on Financial Assistance will replace it in 2027, so check nsf.gov/policies/pappg for the version "
                "in effect when you apply.",
         start=["https://www.nsf.gov/policies/pappg/24-1"],
         pages=r"^https://www\.nsf\.gov/policies/pappg/24-1/[a-z0-9-]+$",
         published="2024-05-20", version="PAPPG 24-1 (NSF 24-1), effective 20 May 2024", limit=30),
    dict(WEB, name="govuk_writing_standards", title="Writing to GOV.UK standards: style guide and content design "
         "(Government Digital Service)", subject="Writing for government (GOV.UK style guide and content design)",
         group=GROUP, level="reference", country="United Kingdom",
         publisher="Government Digital Service (GDS), UK Government", licence="OGL-UK-3.0", licence_url=OGL_UK_URL,
         source="https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/",
         licence_page="https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/",
         licence_text=r"All content is available under the Open Government Licence v3\.0",
         description="GOV.UK's content and publishing guidance on writing, every page: the A to Z style guide "
                     "(abbreviations, capitals, dates, numbers, punctuation and hundreds of words), the technical "
                     "style guide, how to use the style guides, writing guidelines (plain English, writing for the "
                     "web, titles and summaries, accessible writing), planning and managing content, helping users "
                     "prepare for change, and tools and resources.",
         notice="Contains public sector information licensed under the Open Government Licence v3.0 (© Crown "
                "copyright). It follows UK spelling and style: see the note on this book's welcome page.",
         drop=DROP + [r'<a[^>]*href="#[^"]*"[^>]*>\s*Skip past section navigation\s*</a>'],
         crawl=[("https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/", 2)],
         follow=r"^https://guidance\.publishing\.service\.gov\.uk/writing-to-gov-uk-standards/[a-z0-9-]+/$",
         pages=r"^https://guidance\.publishing\.service\.gov\.uk/writing-to-gov-uk-standards/([a-z0-9-]+/)*$",
         unit_rules=[(r"/style-guides/", "Style guides"), (r"/writing-guidelines/", "Writing guidelines"),
                     (r"/plan-manage-content/", "Planning and managing content"),
                     (r"/help-users-prepare-change/", "Helping users prepare for change"),
                     (r"/find-tools-resources/", "Tools and resources"), (r".", "Writing to GOV.UK standards")],
         version="GOV.UK publishing guidance as published", limit=120),
]


# ====================================================================== official PDFs (read whole)

def _pdf(name, title, subject, publisher, description, published, version, **where):
    """One US government PDF of this group (sources.PDF_DOCS fields, read by build_textbooks.pdfdoc_book)."""
    return dict(US, name=name, title=title, subject=subject, publisher=publisher, description=description,
                published=published, version=version, **where)


OPM = "US Office of Personnel Management (OPM)"
OPM_SITE = "https://www.opm.gov/policy-data-oversight"
DTIC_NOTE = ("A Defense Technical Information Center (DTIC) record: its report page says \"Approved for public "
             "release; distribution unlimited\" (checked in the PDF at every build). ")

PDFS = [
    _pdf("plain_language_guidelines", "Federal Plain Language Guidelines (2011)", "Plain language writing",
         "Plain Language Action and Information Network (PLAIN), US federal government",
         "The federal government's plain language guidelines, the whole document with its before-and-after "
         "examples: think about your audience, organize the information, choose your words carefully (verbs, "
         "nouns and pronouns, jargon, definitions, the same terms), be concise, keep it conversational (active "
         "voice, \"must\" not \"shall\"), design for reading (headings, lists, tables, visuals), follow web "
         "standards and test your assumptions.", "2011-05", "March 2011, Revision 1, May 2011",
         pdf=f"{PLG_RAW}/media/FederalPLGuidelines.pdf", page=PLG_REPO, licence_page=f"{PLG_RAW}/LICENSE.md",
         licence_text=PLG_LICENCE_TEXT,
         notice="A work of the US government (public domain; the GSA repository adds the CC0 1.0 dedication "
                "worldwide). The guidelines have been followed since 2011 by digital.gov's plain language guide, "
                "also in this collection."),
    _pdf("gpo_style_manual", "GPO Style Manual (2016)", "Style manual (US government publishing)",
         "US Government Publishing Office (GPO)",
         "The official guide to the form and style of US federal government publishing, the whole book: "
         "capitalization, spelling and compound words, punctuation, abbreviations and letter symbols, signs and "
         "symbols, italic, numerals, tabular work, leaderwork, footnotes and indexes, the Congressional Record, "
         "and the useful tables (US states and their capitals, countries and their people, currency, the "
         "Government's departments), with the GPO's word lists.", "2016", "2016 edition (31st edition)",
         pdf="https://www.govinfo.gov/content/pkg/GPO-STYLEMANUAL-2016/pdf/GPO-STYLEMANUAL-2016.pdf",
         page="https://www.govinfo.gov/app/details/GPO-STYLEMANUAL-2016",
         notice="A work of the US Government Publishing Office (not under copyright in the United States). The "
                "Superintendent of Documents asks that any reprinted edition be labeled clearly as a copy of the "
                "authentic work: this is a copy, converted to an accessible format."),
    _pdf("navy_correspondence_manual", "Department of the Navy Correspondence Manual (SECNAV M-5216.5, 2010)",
         "Correspondence and letter writing (military)", "Secretary of the Navy (US Department of the Navy)",
         DTIC_NOTE + "The Navy's and Marine Corps' manual of correspondence, the whole manual: standard letters, "
         "multiple-address letters, endorsements, memorandums, business letters, executive correspondence, the "
         "parts of a letter, effective writing (plain language), addressing, signing, assembling and dispatching, "
         "and forms of address. This is the March 2010 edition; the Navy's newer edition (June 2015, changed 2018) "
         "is only on its own site, which refuses programs.", "2010-03",
         "SECNAV M-5216.5, March 2010 (DTIC record ADA549326)", archive="DTIC_ADA549326",
         pdf_licence_text=PUBLIC_RELEASE,
         notice="A work of the US Department of the Navy (not under copyright in the United States), approved for "
                "public release; distribution unlimited. An older edition: check the current SECNAV M-5216.5 "
                "before preparing official Navy correspondence."),
    _pdf("tongue_and_quill", "The Tongue and Quill (AFH 33-337, 2004)", "Writing and speaking (military)",
         "Air University and the Department of the Air Force",
         DTIC_NOTE + "The Air Force's handbook of communication, the whole book: the steps to effective "
         "communication (purpose and audience, research, supporting your ideas, organizing, drafting and "
         "editing), writing with focus, persuading, listening, meetings, briefings and speeches, electronic "
         "communication, the forms of Air Force writing (letters, memorandums, staff papers, bullet background "
         "papers, awards and decorations, performance reports, résumés) and the mechanics of writing "
         "(punctuation, capitalization, abbreviations, numbers). This is the August 2004 edition; the newer "
         "editions are only on the Air Force's publications site, which refuses programs.", "2004-08",
         "AFH 33-337, 1 August 2004 (DTIC record ADA521491)", archive="DTIC_ADA521491",
         pdf_licence_text=PUBLIC_RELEASE,
         notice="A work of the US Air Force (not under copyright in the United States), approved for public "
                "release; distribution unlimited. An older edition: check the current Tongue and Quill before "
                "preparing official Air Force correspondence."),
    _pdf("opm_measuring_employee_performance", "A Handbook for Measuring Employee Performance (OPM, 2017)",
         "Performance management and writing performance plans", OPM,
         "OPM's handbook on writing employee performance plans, the whole book: performance management, the "
         "eight steps to performance elements and standards (from the organization's goals to the measures), "
         "writing elements and standards that can be measured, individual and team accomplishments, and many "
         "worked examples.", "2017-03", "March 2017",
         pdf=f"{OPM_SITE}/performance-management/reference-materials/articles/employee_performance_handbook.pdf",
         page=f"{OPM_SITE}/performance-management/reference-materials/"),
    _pdf("opm_structured_interviews", "Structured Interviews: A Practical Guide (OPM, 2008)",
         "Hiring: structured interviews", OPM,
         "OPM's guide to planning and holding structured job interviews, the whole guide: why they work, choosing "
         "competencies, writing interview questions and rating scales, training interviewers, holding the "
         "interview and documenting it, with sample questions and benchmarks.", "2008-09", "September 2008",
         pdf=f"{OPM_SITE}/assessment-and-selection/structured-interviews/guide.pdf",
         page=f"{OPM_SITE}/assessment-and-selection/structured-interviews/"),
    _pdf("opm_assessment_decision_guide", "Assessment Decision Guide (OPM)", "Hiring: assessment methods", OPM,
         "OPM's guide to choosing ways of assessing job applicants, the whole guide: the principles of assessment "
         "(validity, reliability, fairness, the law), evaluating and putting assessment tools into practice, and "
         "a description of each method (structured interviews, work samples, writing samples, situational "
         "judgement tests, training and experience questionnaires, reference checking and others).", "2007-07",
         "2007", pdf=f"{OPM_SITE}/assessment-and-selection/reference-materials/assessmentdecisionguide.pdf",
         page=f"{OPM_SITE}/assessment-and-selection/reference-materials/"),
    _pdf("opm_writing_editing_grade_guide", "Writing and Editing Grade Evaluation Guide (OPM, TS-115, 1992)",
         "Writing and editing jobs (federal classification)", OPM,
         "OPM's guide for grading federal writing and editing positions (writers, editors, technical writers), the "
         "whole guide: what writing and editing work covers, and the factors used to grade it (the nature of the "
         "assignment, the level of responsibility) with their descriptions at each grade.", "1992-05",
         "TS-115, May 1992",
         pdf=f"{OPM_SITE}/classification-qualifications/classifying-general-schedule-positions/functional-guides/"
             "gswrited.pdf",
         page=f"{OPM_SITE}/classification-qualifications/classifying-general-schedule-positions/functional-guides/"),
    _pdf("opm_classifiers_handbook", "The Classifier's Handbook (OPM)", "Job classification and writing position "
         "descriptions", OPM,
         "OPM's handbook on classifying federal positions, the whole book: position descriptions and how to write "
         "and read them, classification standards, determining the title, series and grade, the Factor Evaluation "
         "System, and classification appeals.", "1991-08", "TS-107, August 1991",
         pdf=f"{OPM_SITE}/classification-qualifications/classifying-general-schedule-positions/classifierhandbook.pdf",
         page=f"{OPM_SITE}/classification-qualifications/classifying-general-schedule-positions/"),
    _pdf("opm_position_classification_intro", "Introduction to the Position Classification Standards (OPM)",
         "Job classification", OPM,
         "OPM's introduction to the federal position classification standards, the whole document: the "
         "classification system, how standards are written and used, the occupational series and grades, the "
         "Factor Evaluation System and the general classification principles.", "2009-07", "TS-134, July 1995, "
         "revised August 2009",
         pdf=f"{OPM_SITE}/classification-qualifications/classifying-general-schedule-positions/"
             "positionclassificationintro.pdf",
         page=f"{OPM_SITE}/classification-qualifications/classifying-general-schedule-positions/"),
    _pdf("opm_delegated_examining_handbook", "Delegated Examining Operations Handbook (OPM)",
         "Federal hiring (examining and job announcements)", OPM,
         "OPM's handbook for federal hiring through delegated examining, the whole book: workforce planning, job "
         "analysis, writing job announcements, accepting applications, assessment, veterans' preference, "
         "certificates, selection and the records to keep.", "2019-06", "June 2019",
         pdf=f"{OPM_SITE}/hiring-information/competitive-hiring/deo_handbook.pdf",
         page=f"{OPM_SITE}/hiring-information/competitive-hiring/"),
]
for _e in PDFS:
    if _e["publisher"] == OPM:
        _e.setdefault("notice", "A work of the US Office of Personnel Management (not under copyright in the United "
                                "States). Federal rules change: check opm.gov for the current guidance.")


# ====================================================================== the plainlanguage.gov examples (repository)

# The example pages of the old plainlanguage.gov site, in the order of its own menu, from GSA's public repository
# (github.com/GSA/plainlanguage.gov, last changed 23 September 2025, when the site was retired and forwarded to
# digital.gov). The repository is read file by file from raw.githubusercontent.com (no robots.txt rules); the old
# site's own robots.txt ("Disallow: /") is about the retired web host, which now only forwards.
EXAMPLE_PARTS = [
    ("before-and-after", "Before and after", [
        "index", "ambiguity", "application-due-date", "application-federal-assistance", "car-safety",
        "employment-assistance", "fungi-hazards", "lead-warning", "medicaid-eligibility", "medicaid-initiative",
        "monthly-due-date", "natural-disasters", "printer-recommendations", "register-pesticide", "use-less-water",
        "water-resources", "wordiness"]),
    ("awards", "Award winners (No Gobbledygook Awards)", [
        "index", "gore-speech"] + [f"award-{n}" for n in range(1, 14)]),
    ("brochures", "Reports and brochures", ["index", "hhs-brochure", "jury-instructions"]),
    ("handbooks", "Handbooks and manuals", [
        "index", "army-regulations", "bureau-of-land-management-draft-grazing-manual", "hhs-handbook",
        "johnson-space-center-manual-example-1", "johnson-space-center-manual-example-2",
        "johnson-space-center-manual-example-3"]),
    ("notices", "Letters and notices", [
        "index", "change-in-enrollment-status", "failure-to-provide-claim-information", "medicare-fraud-letter",
        "pension-medical-evidence"]),
    ("regulations", "Regulations", [
        "index", "airworthiness", "animal-care", "disaster-assistance", "disaster-regulation",
        "international-terrorism", "minerals-management-service", "model-preamble", "model-preamble-example",
        "plain-language-regulations", "quick-reference-card", "regulatory-preamble", "smoking-regulation",
        "student-loans"]),
]

EXAMPLES = dict(US, name="plain_language_examples", title="Plain language examples (plainlanguage.gov)",
                subject="Plain language writing (examples)", publisher="Plain Language Action and Information "
                "Network (PLAIN) and the General Services Administration (plainlanguage.gov)",
                source=f"{PLG_REPO}/tree/main/_pages/examples", licence_page=f"{PLG_RAW}/LICENSE.md",
                licence_text=PLG_LICENCE_TEXT,
                description="Every example page of plainlanguage.gov: before-and-after rewrites (side by side), "
                            "the Vice President's No Gobbledygook Award winners, reports and brochures, handbooks "
                            "and manuals, letters and notices (Medicare, veterans' pensions, student aid) and "
                            "regulations rewritten in plain language, each with its \"before\" and \"after\".",
                notice="A work of the US government (public domain; the GSA repository adds the CC0 1.0 dedication "
                       "worldwide). Some examples are decades old; the agencies' current letters may differ.",
                version="plainlanguage.gov repository (GSA), as retired on 23 September 2025")


def md_inline(text):
    """Kramdown inline marks as HTML: raw HTML (the "nomarkdown" parts and tags) kept for the builder's cleaner,
    links to outside sites kept, links within the old site and Jekyll's {% link %} tags turned into their words,
    pictures as "(Picture: description)", bold, italics, code; attribute lists ({: .class}) left out."""
    text = re.sub(r"\{\{[^}]*\}\}", "", text)          # Jekyll's {{ site.baseurl }} and {{ site.email }}
    text = re.sub(r"\{:[^}]*\}(?!/)", "", text.replace("{::nomarkdown}", "\x00").replace("{:/}", "\x01"))
    out = []
    for part in re.split(r"(\x00.*?\x01|<[a-zA-Z/][^>]*>)", text):
        if part.startswith("\x00"):
            out.append(part.strip("\x00\x01"))          # raw HTML
            continue
        if part.startswith("<"):
            out.append(part)
            continue
        s = html.escape(part, quote=False)
        s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", lambda m: f"(Picture: {m.group(1)})" if m.group(1).strip() else "", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)[^)]*\)", r'<a href="\2">\1</a>', s)
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"\{%[^%]*%\}", "", s)
        s = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
        s = re.sub(r"(?<![\w_])_(?![\s_])(.+?)(?<![\s_])_(?!\w)", r"<em>\1</em>", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        out.append(s)
    return "".join(out)


def front_matter(text):
    """({field: value}, the rest) of a Jekyll page: the simple "name: value" lines between its two "---" lines."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fields = {}
    for line in m.group(1).splitlines():
        f = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if f and f.group(2).strip() not in ("", ">-", "|"):
            fields[f.group(1)] = f.group(2).strip().strip("'\"")
    return fields, text[m.end():]


ITEM = re.compile(r"^(\s*)([*+-]|\d+\.)\s+(.*)$")
TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def md_html(text):
    """The HTML of a kramdown page body (what the plainlanguage.gov pages use): headings (one level below the page's
    own title), paragraphs (two spaces at a line's end: a line break), tables with a header row, bulleted and
    numbered lists whose items hold their own blocks (a "#### Before" heading and its paragraphs), quotations, and
    raw HTML."""
    lines = text.replace("\r", "").split("\n")
    out, para, i = [], [], 0

    def flush():
        if para:
            words = "".join(md_inline(x.strip()) + ("<br>" if x.endswith("  ") else " ") for x in para)
            out.append(f"<p>{words.strip()}</p>")
            para.clear()
    while i < len(lines):
        line = lines[i]
        if not line.strip() or re.match(r"^\s*\{:[^}]*\}\s*$", line):
            flush()
            i += 1
            continue
        h = re.match(r"^\s*(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if h:
            flush()
            level = min(len(h.group(1)) + 1, 6)
            out.append(f"<h{level}>{md_inline(h.group(2))}</h{level}>")
            i += 1
            continue
        if "|" in line and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1]):
            flush()
            cells = lambda row: [c.strip() for c in row.strip().strip("|").split("|")]   # noqa: E731
            rows = ["<tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in cells(line)) + "</tr>"]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cells(lines[i])) + "</tr>")
                i += 1
            out.append("<table>" + "".join(rows) + "</table>")
            continue
        m = ITEM.match(line)
        if m and len(m.group(1)) < 2:
            flush()
            tag = "ol" if m.group(2)[0].isdigit() else "ul"
            items = []
            while i < len(lines):
                m = ITEM.match(lines[i])
                if not (m and len(m.group(1)) < 2):
                    break
                block = [m.group(3)]
                i += 1
                while i < len(lines):           # the item's own lines: indented, or blank before an indented one
                    nxt = lines[i]
                    if nxt.startswith("  ") or (not nxt.strip() and i + 1 < len(lines) and
                                                lines[i + 1].startswith("  ")):
                        block.append(nxt[2:] if nxt.startswith("  ") else "")
                        i += 1
                    else:
                        break
                inner = md_html("\n".join(block))
                inner = re.sub(r"^<p>(.*)</p>$", r"\1", inner, flags=re.S) if inner.count("<p>") == 1 and \
                    inner.startswith("<p>") and inner.endswith("</p>") else inner
                items.append(f"<li>{inner}</li>")
                while i < len(lines) and not lines[i].strip() and i + 1 < len(lines) and ITEM.match(lines[i + 1]):
                    i += 1                         # a blank line between two items of the same list
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        if line.lstrip().startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote>{md_html(chr(10).join(quote))}</blockquote>")
            continue
        if line.strip().startswith("{::nomarkdown}") or re.match(r"^\s*<(div|table|ul|ol|p|h\d)\b", line):
            flush()
            out.append(md_inline(line))
            i += 1
            continue
        para.append(line)
        i += 1
    flush()
    return "\n".join(out)


def examples_book(cache=None, left_out=None, limit=None):
    """The Book of the plainlanguage.gov examples: the repository's licence file checked, then every example page of
    EXAMPLE_PARTS read from raw.githubusercontent.com, its front matter giving the page's title (and the agency, when
    it names one), its kramdown body made into HTML. limit: read only so many pages (a small test build)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    if not readable(EXAMPLES["licence_page"], cache) or \
            not re.search(EXAMPLES["licence_text"], B.fetch(EXAMPLES["licence_page"], cache)):
        left_out.append({"title": EXAMPLES["title"], "reason": "Its repository's licence file no longer states the "
                         "licence that was checked."})
        return None
    book = B.Book(name=EXAMPLES["name"], title=EXAMPLES["title"], subject=EXAMPLES["subject"], level="reference",
                  group=GROUP, publisher=EXAMPLES["publisher"], country=EXAMPLES["country"],
                  licence=EXAMPLES["licence"], licence_url=EXAMPLES["licence_url"], source=EXAMPLES["source"],
                  description=EXAMPLES["description"], notice=EXAMPLES["notice"], version=EXAMPLES["version"],
                  published="2025-09-23", changes="each example page's text made into a web page (its pictures "
                                                  "left out, their descriptions kept)")
    paths, read = set(), 0
    for folder, unit, names in EXAMPLE_PARTS:
        for name in names:
            if limit and read >= limit:
                break
            url = f"{PLG_RAW}/_pages/examples/{folder}/{name}.md"
            if not readable(url, cache):
                left_out.append({"title": f"{EXAMPLES['title']}: {url}", "reason": "Not allowed by robots.txt."})
                continue
            try:
                text = B.fetch(url, cache)
            except (urllib.error.URLError, OSError):
                left_out.append({"title": f"{EXAMPLES['title']}: {url}", "reason": "It could not be read."})
                continue
            read += 1
            fields, body = front_matter(text)
            title = html.unescape(fields.get("title") or name.replace("-", " ").capitalize())
            if name == "index":
                title = unit
            byline = f"<p>From: {B.esc(fields['author'])}.</p>" if fields.get("author") else ""
            page_html = B._Cleaner({}, url).clean(byline + md_html(body))
            if not re.sub(r"<[^>]+>", "", page_html).strip():
                continue                           # a part's index page whose list the old site made itself
            path = B.slug(f"{folder}-{name}", 60)
            while path in paths:
                path += "-2"
            paths.add(path)
            book.pages.append(B.Page(path, title, page_html, 0, unit))
            book.originals.append({"url": url, "kind": "markdown"})
    return book


# ====================================================================== reading, keys, signs, the build

def readable(url, cache=None):
    """True when the builder may read url: robots.txt allows our reader and no AI-reader block or "ai-train=no"
    applies (directory_sources.ai_refused)."""
    import build_textbooks as B
    import directory_sources as D
    return B.allowed_by_robots(url, cache) and not D.ai_refused(url, cache)


GUIDES_BY_NAME = {g["name"]: g for g in GUIDES}
PDFS_BY_NAME = {p["name"]: p for p in PDFS}


def all_keys():
    """Every build key of this module, in the order of the docstring."""
    return [f"wb:{p['name']}" for p in PDFS[:1]] + [f"wb:{EXAMPLES['name']}"] + \
        [f"wb:{g['name']}" for g in GUIDES] + [f"wb:{p['name']}" for p in PDFS[1:]]


def expand_keys(words):
    """The keys the words stand for: "writing" (every book of this module), "group:writing" (the same), or wb:<name>
    (one book, kept as it is)."""
    keys = []
    for w in words:
        if w in ("writing", f"group:{GROUP}"):
            keys += all_keys()
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change of one key ("" when it cannot be asked: then nothing is rebuilt): a web
    guide's list of pages (directory_sources.guide_sign, with the month), a PDF's checksum or its server's ETag,
    date and size (updates.pdf_sign), the repository's newest commit for the examples."""
    name = key.split(":", 1)[1] if ":" in key else key
    try:
        if name in GUIDES_BY_NAME:
            import directory_sources as D
            return D.guide_sign(GUIDES_BY_NAME[name])
        if name in PDFS_BY_NAME:
            import updates
            return updates.pdf_sign(PDFS_BY_NAME[name])
        if name == EXAMPLES["name"]:
            import updates
            return updates.git_head(PLG_REPO)
    except (urllib.error.URLError, OSError, ValueError, KeyError, LookupError):
        return ""
    return ""


def book_for(key, work, cache=None, left_out=None, limit=None):
    """The Book of one key, or None (the reason in left_out). A site that shuts out AI companies' readers is not
    read; a PDF's own licence check (pdf_licence_text, the public-release line) is the builder's."""
    import build_textbooks as B
    import directory_sources as D
    left_out = left_out if left_out is not None else []
    name = key.split(":", 1)[1]
    if name == EXAMPLES["name"]:
        return examples_book(cache, left_out, limit)
    entry = GUIDES_BY_NAME.get(name) or PDFS_BY_NAME.get(name)
    if entry is None:
        left_out.append({"title": key, "reason": "Unknown key."})
        return None
    where = entry.get("pdf") or entry.get("page") or entry.get("source") or ""
    if entry.get("archive"):
        where = f"https://archive.org/metadata/{entry['archive']}"
    if where and D.ai_refused(where, cache):
        left_out.append({"title": entry["title"], "reason": "The site's robots.txt shuts out AI companies' readers or "
                         "says ai-train=no; it is not read."})
        return None
    if name in GUIDES_BY_NAME:
        book = D.guide_book(entry, cache, left_out, limit)
    else:
        book = B.pdfdoc_book(entry, work, cache, left_out)
        if book is not None and limit:
            book.pages = book.pages[:limit]
    if book is None:
        return None
    book.version = entry.get("version", "")
    if name in GUIDES_BY_NAME:                   # a web guide: the edition is the day its pages were read
        book.version += f", pages read {datetime.date.today().isoformat()}"
    if entry.get("published"):
        book.published = entry["published"]
    if entry.get("notice"):
        book.notice = entry["notice"]
    return book


def build_writing(keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys into out_dir and write manifest-<key>.json for each (as build_textbooks.build does);
    returns {key: manifest}. Every book is a new version (versioned file names, kept by updates.merge_versions).
    limit: a small test build (only so many pages; manifests named "..._sample")."""
    import build_textbooks as B
    manifests = {}
    work = os.path.join(cache or out_dir, "work")
    os.makedirs(out_dir, exist_ok=True)
    for key in expand_keys(keys):
        if not key.startswith("wb:"):
            print(f"Not a key of this module: {key}; skipped.")
            continue
        left_out, entries = [], []
        fingerprint = "" if limit else sign(key)
        try:
            book = book_for(key, work, cache, left_out, limit)
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            book = None
        if book is not None and not book.pages:
            left_out.append({"title": book.title, "reason": "No pages could be read."})
            book = None
        if book is not None:
            entry = B.write_book(book, out_dir, date, versioned=True)
            entry.update({"key": key, "fingerprint": fingerprint, "release": "textbooks"})
            print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, {entry['licence_text']}")
            entries.append(entry)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": "textbooks", "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if limit else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


# ====================================================================== what was checked, and what was not built

# Where a UK book's practice differs (sources.practice_note; put first, so it wins for these subjects only).
PRACTICE_SUBJECTS = [
    (r"gov\.uk style|content design|writing for government", "spelling (British: organise, colour, centre, "
     "licence as a noun), punctuation and style (single quotation marks, no full stops in abbreviations, dates "
     "written \"21 November 2026\"), and UK government terms and law"),
]

LICENCE_LINES = {
    "plainlanguage_gov_repository": "github.com/GSA/plainlanguage.gov LICENSE.md (read 2026-11-21, checked again at "
                                    "every build): \"As a work of the United States Government, this project is in "
                                    "the public domain within the United States. Additionally, we waive copyright "
                                    "and related rights in the work worldwide through the CC0 1.0 Universal public "
                                    "domain dedication.\" raw.githubusercontent.com has no robots.txt rules.",
    "digital_gov_plain_language": "digital.gov (GSA): a work of the US government (17 U.S.C. 105; the line checked "
                                  "is govinfo.gov's quotation of it). robots.txt: \"User-agent: *\", Crawl-delay 10, "
                                  "only Drupal's system folders disallowed; no AI rules (checked 2026-11-21).",
    "sba_business_guide": "www.sba.gov/about-sba/open-government/about-the-sba-gov-website/: \"Government "
                          "information on SBA.gov is in the public domain. Public domain information may be freely "
                          "distributed and copied, but it is requested that in any subsequent use, SBA's information "
                          "be given appropriate acknowledgement.\" robots.txt disallows only /wp-admin/ and searches. "
                          "legacy.sba.gov's robots.txt disallows /sites/default/files/*, so its template files are "
                          "not fetched.",
    "nih_nsf_grants": "grants.nih.gov and www.nsf.gov: works of the US government (17 U.S.C. 105). Their robots.txt "
                      "files disallow only Drupal's system folders, searches and (NSF) listings; no AI rules "
                      "(checked 2026-11-21).",
    "gpo_style_manual": "govinfo.gov/about/policies quotes 17 U.S.C. 105; the Internet Archive's record of the same "
                        "book adds: \"The Superintendent of Documents of the U.S. Government Publishing Office "
                        "requests that any reprinted edition be labeled clearly as a copy of the authentic work\" "
                        "(said in the book's notice). govinfo's robots.txt allows /content/pkg/.",
    "dtic_military_manuals": "SECNAV M-5216.5 (2010) and AFH 33-337 (2004): the DTIC report page (SF 298) in each "
                             "PDF says \"Approved for public release; distribution unlimited\" (checked at every "
                             "build); works of the US government. archive.org's robots.txt allows the files. (The "
                             "Tongue and Quill's own \"Distribution F\" is the Air Force's internal code for how "
                             "printed copies were sent out, not a DoD restriction; the 1997 copy on the Internet "
                             "Archive has no public-release line and is not used.)",
    "opm_handbooks": "www.opm.gov: works of the US government (17 U.S.C. 105). robots.txt disallows only searches, "
                     "logins and print pages (checked 2026-11-21).",
    "govuk_writing_standards": "guidance.publishing.service.gov.uk footer (checked at every build): \"All content is "
                               "available under the Open Government Licence v3.0, except where otherwise stated\", "
                               "© Crown copyright. The site has no robots.txt (none to obey; no AI rules); "
                               "www.gov.uk/guidance/style-guide and /guidance/content-design forward to it.",
}

NOT_INCLUDED = [
    ("AR 25-50, Preparing and Managing Correspondence, and DA Pam 600-67, Effective Writing for Army Leaders (US "
     "Army)", "Already in the library through the Kiwix library's Army Publishing Directorate book "
     "(armypubs_en_all), which holds the Army's public-release publications. armypubs.army.mil's own robots.txt says "
     "\"Disallow: /\" for every program, and no Internet Archive copy was found, so they are not built here."),
    ("Department of the Navy Correspondence Manual, current edition (SECNAV M-5216.5, June 2015, change 1 2018)",
     "www.secnav.navy.mil answers programs with a bot-check script (robots.txt included), so the current edition "
     "cannot be read; the March 2010 edition is built from DTIC's public-release record instead "
     "(wb:navy_correspondence_manual). Index: https://www.secnav.navy.mil/doni/manuals-secnav.aspx"),
    ("The Tongue and Quill, current edition (AFH 33-337, 2015 and later changes)", "www.e-publishing.af.mil and "
     "static.e-publishing.af.mil refuse programs (\"Access Denied\", robots.txt included); the August 2004 edition is "
     "built from DTIC's public-release record instead (wb:tongue_and_quill). Index: "
     "https://www.e-publishing.af.mil/"),
    ("SBA business plan templates (Andrew's lean and traditional plans, Rebecca's plan) and the startup costs "
     "worksheet", "Public domain, but they are files on legacy.sba.gov, whose robots.txt disallows "
     "/sites/default/files/* for every program; the guide's own text about business plans is in "
     "wb:sba_business_guide. Index: https://legacy.sba.gov/document/support-andrews-business-plan-template-lean"),
    ("OPM's \"Write It Right\" webinar and its plain writing plan and compliance reports", "Left out: the webinar is "
     "the transcript of slides about occupational questionnaires, and the plan and reports describe OPM's own "
     "compliance with the Plain Writing Act; OPM's handbooks are built instead."),
    ("plainlanguage.gov's guideline pages (web edition)", "The same text as the Federal Plain Language Guidelines "
     "PDF (wb:plain_language_guidelines) and digital.gov's guide (wb:digital_gov_plain_language), both built; not "
     "added a third time."),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["writing"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many pages")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build_writing(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
