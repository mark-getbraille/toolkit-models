"""Government help in plain language for the reference library (the owner's request of 2026-11-22): benefits,
housing, jobs, scams, Medicare and digital government. Keys: gov-help (every book), help:<name>.

What this module builds, in plain words, each IN FULL:
  - USA.gov's plain-language pages on benefits (food, health insurance, utility bills, welfare, disability,
    Social Security, death benefits, government checks), housing help (rental programmes, Section 8 vouchers,
    tenant rights, eviction and foreclosure, emergency housing, repairs), jobs and unemployment, money, and scams and
    identity theft (the benefit finder that replaced Benefits.gov is an interactive tool and is not copied);
  - Medicare & You, the official Medicare handbook (the whole current edition, PDF), and Medicare.gov's guides
    (the basics, signing up, the parts of Medicare and their costs, what Medicare covers, health and drug plans,
    Medigap, and providers and services);
  - digital.gov's guides for people who build government websites and services (accessibility for teams, human-
    centred design, mobile principles, search, site scanning, web analytics, public participation and the Paperwork
    Reduction Act); its plain language guide is already in the library (wb:digital_gov_plain_language).

Not built: SSA's publications (ssa.gov refuses programs), Benefits.gov (now forwarded to USA.gov's benefit finder),
and GCFGlobal's technology lessons (copyrighted by Goodwill Community Foundation): link-only in NOT_INCLUDED.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build). robots.txt: usa.gov asks a 10-second pause (kept by the builder), medicare.gov and digital.gov allow the
pages; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/gov_help.py help:usa_gov --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "consumer"
USA = "https://www.usa.gov"
USA_HUBS = ["benefits", "housing-help", "scams-and-fraud", "jobs-and-unemployment", "money", "health-insurance",
            "disability-services", "food-help", "government-checks-payments", "welfare-and-financial-assistance",
            "social-security", "help-with-utility-bills", "tenant-rights", "identity-theft"]
NAV = ("about|about-the-us|accessibility-policy|agency-index|blog|branches-of-government|partner-with-usagov|phone|"
       "privacy-security|site-issue-report-form|website-analytics|immigration-and-citizenship|travel|"
       "voting-and-elections|benefit-finder|espanol|contact|search|life-events|state-governments|"
       "federal-agencies|holidays|presidents|tribes|local-governments|elected-officials|forms|laws-and-regulations")

GUIDES = [
    K.guide(GROUP, "usa_gov", "USA.gov: benefits, housing, jobs, money and scams in plain language",
            "Government benefits and help", "USAGov, General Services Administration (USA.gov)",
            [f"{USA}/{h}" for h in USA_HUBS], rf"^https://www\.usa\.gov/(?!(?:{NAV})$)[a-z0-9-]+$",
            "USA.gov's plain-language pages: government benefits (food help, health insurance, help with utility "
            "bills, welfare and cash assistance, disability services, Social Security, death benefits, government "
            "checks), housing help (rental programmes, Section 8 vouchers, tenant rights, eviction and "
            "foreclosure, emergency housing, buying and repairing a home), jobs and unemployment, money (credit, "
            "debt, unclaimed money, taxes) and scams and identity theft (imposter scams, where to report a scam).",
            "A work of the US government (USAGov, General Services Administration; public domain). Programmes and "
            "rules change: check the agency's own site before you apply.",
            units=[(r"/(benefits|food|health-insurance|welfare|disability|social-security|government-checks|"
                    r"government-death|utility)", "Benefits"),
                   (r"/(housing|rental|tenant|eviction|emergency-housing|buying-home|repairing-home|native-american-"
                    r"housing|change-address)", "Housing"),
                   (r"/(job|unemployment|work)", "Jobs and unemployment"),
                   (r"/(scam|identity|imposter|where-report|fraud)", "Scams and identity theft"),
                   (r".", "Money and other help")], limit=250),
    K.guide(GROUP, "medicare_guides", "Medicare.gov guides: the basics, coverage and plans",
            "Medicare", "Centers for Medicare & Medicaid Services (Medicare.gov)",
            ["https://www.medicare.gov/basics/get-started-with-medicare", "https://www.medicare.gov/coverage",
             "https://www.medicare.gov/health-drug-plans"],
            r"^https://www\.medicare\.gov/(basics|coverage|health-drug-plans)(/[a-z0-9-]+)*$",
            "Medicare.gov's guides: getting started (before and after 65, other paths), signing up and when, the "
            "parts of Medicare and what they cost, your coverage options (Original Medicare, Medicare Advantage, "
            "drug plans, Medigap), what Medicare covers (every service and supply page), end-stage renal disease, "
            "and health and drug plans.",
            "A work of the Centers for Medicare & Medicaid Services (public domain). Costs change each year: check "
            "Medicare.gov or call 1-800-MEDICARE.", depth=2,
            follow=r"^https://www\.medicare\.gov/(basics/get-started-with-medicare|coverage|health-drug-plans)"
                   r"(/[a-z0-9-]+)?$",
            units=[(r"/basics", "The basics"), (r"/coverage", "What Medicare covers"),
                   (r"/health-drug-plans", "Health and drug plans")], limit=500),
    K.guide(GROUP, "digital_gov_guides", "digital.gov guides for building government services",
            "Digital government (accessibility, design, analytics)", "General Services Administration (digital.gov)",
            "https://digital.gov/guides/", r"^https://digital\.gov/guides/(?!plain-language)[a-z0-9-]+(/[a-z0-9-]+)*$",
            "digital.gov's guides for teams who build government websites and services, every page: accessibility "
            "for teams, human-centred design, mobile principles, search, site scanning, the Digital Analytics "
            "Program and web analytics playbook, public participation, research collaboration and the Paperwork "
            "Reduction Act.", "A work of the US General Services Administration (public domain).",
            depth=2, follow=r"^https://digital\.gov/guides/[a-z0-9-]+$",
            units=[(r"/guides/accessibility", "Accessibility for teams"), (r"/guides/hcd", "Human-centred design"),
                   (r"/guides/mobile", "Mobile principles"), (r"/guides/(dap|web-analytics)", "Analytics"),
                   (r".", "Other guides")], limit=300),
]

PDFS = [
    K.us_pdf(GROUP, name="medicare_and_you", title="Medicare & You: the official US government Medicare handbook",
             subject="Medicare", publisher="Centers for Medicare & Medicaid Services (CMS)",
             description="The whole official handbook mailed to every Medicare household: what's new, signing up, "
                         "Part A and Part B, Medicare Advantage and other plans, Medigap, drug coverage (Part D), "
                         "help paying costs, your rights and protections (appeals), getting help, and the "
                         "definitions.",
             pdf="https://www.medicare.gov/publications/10050-medicare-and-you.pdf",
             page="https://www.medicare.gov/publications", version="The current yearly edition (publication 10050)",
             notice="A work of the Centers for Medicare & Medicaid Services (public domain). This is the edition "
                    "current when the book was made; a new one comes out each autumn."),
]

COLLECTION = K.Collection("help", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"gov-help": lambda: ["help:usa_gov", "help:medicare_and_you", "help:medicare_guides",
                                                      "help:digital_gov_guides"]})

GROUPS = {}
LICENCE_LINES = {
    "usa_gov_medicare_digital_gov": "usa.gov, medicare.gov and digital.gov: works of the US government (17 U.S.C. "
                                    "105, checked on govinfo.gov's policies page at every build). robots.txt: usa.gov "
                                    "Crawl-delay 10 (kept), medicare.gov and digital.gov allow the pages; no AI rules "
                                    "(checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("Social Security Administration publications (ssa.gov/pubs)", "Public domain, but www.ssa.gov answers programs "
     "\"403 Forbidden\" (robots.txt included, checked again 2026-11-22). Link-only. Index: https://www.ssa.gov/pubs/"),
    ("Benefits.gov", "It now forwards to USA.gov's benefit finder, an interactive questionnaire; USA.gov's benefit "
     "pages are built instead (help:usa_gov). Index: https://www.usa.gov/benefit-finder"),
    ("GCFGlobal technology and computer lessons (Goodwill Community Foundation)", "Copyright GCFGlobal; its terms do "
     "not allow copying. Link-only for the personal assistant. Index: https://edu.gcfglobal.org/en/topics/tech/"),
    ("Medicare & You in other formats (large print, braille, audio, Spanish)", "Not copied separately: the large print "
     "and Spanish PDFs and EPUB have the same text as the built edition; braille and audio copies can be ordered free "
     "from 1-800-MEDICARE. Index: https://www.medicare.gov/publications"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
