"""Immigration beyond citizenship for the reference library, in its own group "Reference, immigration" (the owner's
request of 2026-11-22). Keys: immigration (every book), immig:<name>.

What this module builds, in plain words, each IN FULL (every page or every page of the PDF):
  - the USCIS Policy Manual: U.S. Citizenship and Immigration Services' official immigration policy, every volume,
    part and chapter (general policies, nonimmigrants, humanitarian protection and parole, refugees and asylees,
    adoptions, immigrants, adjustment of status, admissibility, waivers, employment authorization, travel and identity
    documents, citizenship and naturalisation), read in the order of its table of contents;
  - USCIS's own guides: green cards (every eligibility category, adjustment of status, after the green card is
    granted, replacing a card, travelling as a permanent resident), family-based immigration, working in the United
    States (permanent and temporary workers, work permits: the Employment Authorization Document), humanitarian
    programmes (refugees and asylum, Temporary Protected Status, DACA, parole, T and U visas, abused spouses and
    children), travel documents, and avoiding immigration scams ("notarios" and other people who are not allowed to
    give immigration legal help);
  - "Welcome to the United States: A Guide for New Immigrants" (USCIS M-618), the PDF in English and in eleven of
    its translations (Arabic, Chinese traditional and simplified, French, Korean, Portuguese, Russian, Somali,
    Spanish, Urdu, Vietnamese);
  - the Executive Office for Immigration Review (EOIR, the immigration courts, US Department of Justice): finding
    legal help (the list of free legal service providers, recognised organisations and accredited representatives),
    immigration court information, and the EOIR Policy Manual (with the Immigration Court Practice Manual and the
    Board of Immigration Appeals Practice Manual);
  - Canada's newcomer pages (Immigration, Refugees and Citizenship Canada, canada.ca "Settle in Canada"): personal
    use only (the Government of Canada's terms allow non-commercial reproduction), with the non-US note.
  Every book's notice ends with LEGAL: "General information, not legal advice; check the current rules or ask an
  accredited representative or lawyer."

Not repeated (other collections): citizenship and naturalisation, the naturalisation test and civics (the money and
world helper's collection, key prefix of its own); the Immigration and Nationality Act is in the US Code (code:usc:8);
US passports and travel abroad (the travel books).

Not built (NOT_INCLUDED): the State Department's refugee admissions pages (state.gov refuses programs), the Office of
Refugee Resettlement (acf.hhs.gov answers programs with an empty bot check), the FTC's notario-fraud pages (refuses
programs), the M-618 in Haitian Creole and Tagalog (see the reason), and the non-profit immigration guides
(copyright).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
the canada.ca terms checked at every build. robots.txt allows every page read; USCIS asks for 10 seconds between
pages (Crawl-delay), which the builder keeps.

Run from the repository's folder:
  python3 textbooks/immigration.py immig:uscis_immigration_guides --out build/textbooks --limit 5
  python3 textbooks/immigration.py --list immigration
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "immigration"
GROUPS = {GROUP: "Reference, immigration"}

# The line every legal or benefits book of these collections ends with (the owner's words of 2026-11-22).
LEGAL = "General information, not legal advice; check the current rules or ask an accredited representative or lawyer."

USCIS = "https://www.uscis.gov"
USCIS_PUBLISHER = "U.S. Citizenship and Immigration Services (USCIS), US Department of Homeland Security"
USCIS_NOTICE = ("From U.S. Citizenship and Immigration Services (uscis.gov): a US government work (public domain). "
                "Immigration rules, fees, forms and processing change often: check the date on each page and the "
                "current version on uscis.gov, and file only on uscis.gov (never pay anyone who promises special "
                f"access). {LEGAL}")

# The twelve volumes of the Policy Manual, for its parts ("Volume 7: Adjustment of Status").
PM_VOLUMES = {1: "General Policies and Procedures", 2: "Nonimmigrants", 3: "Humanitarian Protection and Parole",
              4: "Refugees and Asylees", 5: "Adoptions", 6: "Immigrants", 7: "Adjustment of Status",
              8: "Admissibility", 9: "Waivers and Other Forms of Relief", 10: "Employment Authorization",
              11: "Travel and Identity Documents", 12: "Citizenship and Naturalization"}

GUIDES = [
    K.guide(GROUP, "uscis_policy_manual", "USCIS Policy Manual: every volume, part and chapter (U.S. Citizenship and "
            "Immigration Services)", "Immigration policy (USCIS Policy Manual)", USCIS_PUBLISHER,
            USCIS + "/policy-manual/table-of-contents",
            r"^https://www\.uscis\.gov/policy-manual/volume-\d+-part-[a-z](-chapter-\d+)?$",
            "The USCIS Policy Manual, USCIS's official immigration policies, every chapter in the order of its "
            "table of contents: general policies and procedures (fee waivers, biometrics, interviews, accommodations "
            "for people with disabilities), nonimmigrant visas, humanitarian protection and parole, refugees and "
            "asylees, adoptions, immigrants (family and employment based), adjustment of status (applying for a "
            "green card from inside the United States), admissibility and public charge, waivers, employment "
            "authorization, travel and identity documents, and citizenship and naturalisation.",
            USCIS_NOTICE, depth=1,
            units=[(rf"/volume-{n}(-|$)", f"Volume {n}: {name}") for n, name in sorted(PM_VOLUMES.items(),
                                                                                      reverse=True)],
            limit=700),
]

# USCIS's guides: green cards, family, working, humanitarian programmes, travel documents and scams. Citizenship
# pages are left to the citizenship collection.
USCIS_HUBS = ["green-card", "family", "working-in-the-united-states", "humanitarian",
              "scams-fraud-and-misconduct/avoid-scams", "employment-authorization",
              "green-card/green-card-processes-and-procedures/travel-documents"]
GUIDES.append(K.guide(
    GROUP, "uscis_immigration_guides", "Green cards, family and work visas, work permits, humanitarian programmes "
    "and scams: the USCIS guides", "Immigration guides (USCIS)", USCIS_PUBLISHER,
    [f"{USCIS}/{hub}" for hub in USCIS_HUBS],
    r"^https://www\.uscis\.gov/(green-card|family|working-in-the-united-states|humanitarian|"
    r"scams-fraud-and-misconduct|employment-authorization|DACA)(/[a-z0-9-]+)*$",
    "USCIS's guides to staying in the United States: green cards (every eligibility category: family, employment, "
    "special immigrants, refugees and asylees, human trafficking and crime victims, registry and others; how to "
    "apply, adjustment of status, while the application is pending, after the decision, replacing or renewing a "
    "card, international travel as a permanent resident), family of US citizens and of permanent residents, working "
    "in the United States (permanent workers, temporary workers and their visa categories, the Employment "
    "Authorization Document or work permit), humanitarian programmes (refugees and asylum, Temporary Protected "
    "Status, Deferred Action for Childhood Arrivals (DACA), humanitarian parole, T and U visas, abused spouses, "
    "children and parents, special immigrant juveniles), travel documents (re-entry permits, refugee travel "
    "documents, advance parole), and how to avoid immigration scams and find real legal help.",
    USCIS_NOTICE, depth=2,
    follow=r"^https://www\.uscis\.gov/(green-card|family|working-in-the-united-states|humanitarian)(/[a-z0-9-]+)?$",
    units=[(r"/scams-fraud", "Avoiding scams and finding legal help"), (r"/humanitarian|/DACA", "Humanitarian "
            "programmes: refugees, asylum, TPS, DACA, parole"), (r"/working-in|/employment-authorization",
                                                                 "Working in the United States and work permits"),
           (r"/family", "Family of US citizens and permanent residents"), (r"travel-documents|international-travel",
                                                                           "Travel documents"),
           (r".", "Green cards")], limit=650))

# The Executive Office for Immigration Review (the immigration courts).
EOIR = "https://www.justice.gov/eoir"
EOIR_PUBLISHER = "Executive Office for Immigration Review (EOIR), US Department of Justice"
EOIR_NOTICE = ("From the Executive Office for Immigration Review, US Department of Justice (justice.gov/eoir): a US "
               "government work (public domain). If you have a hearing, never miss it: check your case with EOIR's "
               f"automated case information (1-800-898-7180) or online. {LEGAL}")
EOIR_PAGES = [f"{EOIR}/{p}" for p in (
    "find-legal-representation", "list-pro-bono-legal-service-providers-map", "recognition-and-accreditation-program",
    "recognition-and-accreditation-program-frequently-asked-questions", "recognition-accreditation-roster-reports",
    "immigration-court-information", "find-immigration-court-and-access-internet-based-hearings",
    "eoir-case-information", "pa-fact-sheets", "types-appeals-motions-and-required-fees",
    "board-of-immigration-appeals", "public-resources-program", "model-hearing-program", "access-eoir")]
GUIDES.append(K.us_web(
    GROUP, name="eoir_court_legal_help", title="Immigration court basics and finding free legal help (EOIR, US "
    "Department of Justice)", subject="Immigration court and legal help", publisher=EOIR_PUBLISHER,
    source=EOIR_PAGES[0], crawl=[(EOIR_PAGES[0], 0)], urls=list(EOIR_PAGES),
    pages=r"^https://www\.justice\.gov/eoir/[a-z0-9-]+$",
    description="The immigration courts' pages for the public: how to find legal representation (the list of free "
                "legal service providers, recognised organisations and accredited representatives, and how to "
                "check that a representative is allowed to help), immigration court information and how to find "
                "your court and join an internet-based hearing, your case information, the fact sheets for the "
                "public, appeals and motions, the Board of Immigration Appeals, and EOIR's self-help and model "
                "hearing programmes.", notice=EOIR_NOTICE,
    unit_rules=[(r"legal-representation|pro-bono|recognition|public-resources", "Finding legal help"),
                (r".", "Immigration court")], limit=len(EOIR_PAGES) + 5))
GUIDES.append(K.guide(
    GROUP, "eoir_policy_manual", "EOIR Policy Manual: the Immigration Court and Board of Immigration Appeals Practice "
    "Manuals (US Department of Justice)", "Immigration court practice", EOIR_PUBLISHER, EOIR + "/policy-manual-eoir",
    r"^https://www\.justice\.gov/eoir/policy-manual-eoir(/part-[IVX]+(/[a-z]+)?(/chapter-[0-9-]+)?)?$",
    "EOIR's Policy Manual, every chapter: the general policies (Part I), the Immigration Court Practice Manual "
    "(Part II: filing, hearings, motions, appeals, the rules people without a lawyer must follow too), the Board of "
    "Immigration Appeals Practice Manual (Part III) and the Office of the Chief Administrative Hearing Officer's "
    "manual.", EOIR_NOTICE, depth=1,
    units=[(r"/part-III", "Board of Immigration Appeals Practice Manual"), (r"/part-II", "Immigration Court "
            "Practice Manual"), (r"/part-I", "General policies"), (r".", "More")], limit=500))

# Canada (personal use): the Government of Canada's terms (as in parenting.py, checked at every build) allow
# non-commercial reproduction only, so the book is personal use only. No newcomer guide was found on open.canada.ca
# under the Open Government Licence - Canada (searched 2026-11-22).
CROWN_NC = "Crown copyright (Canada), canada.ca terms for personal and public use"
ALLOWED = {CROWN_NC: "non-commercial"}
CANADA_TERMS = "https://www.canada.ca/en/transparency/terms.html"
CANADA_TEXT = r"you may reproduce the materials in whole or in part for non-commercial purposes"
SETTLE = "https://www.canada.ca/en/immigration-refugees-citizenship/services/settle-canada"
GUIDES.append(dict(K.guide(
    GROUP, "canada_newcomers", "Settle in Canada: newcomers' guide (Immigration, Refugees and Citizenship Canada)",
    "Newcomers to Canada", "Immigration, Refugees and Citizenship Canada (Government of Canada, canada.ca)",
    SETTLE + ".html", r"^https://www\.canada\.ca/en/immigration-refugees-citizenship/services/(settle-canada"
                      r"(/[a-z0-9-]+)*|protect-fraud/newcomers)\.html$",
    "Canada's guide for new permanent residents and refugees, every page: free newcomer services and who may use "
    "them, preparing before arrival, crossing the border, carrying identification, choosing a city, housing, money "
    "and banking, finding a job, language classes, education, health care, driving, laws and human rights, "
    "government, the land and climate, and protecting yourself from immigration fraud.",
    "Canadian source, personal use only: reproduced under the Government of Canada's terms for non-commercial "
    "reproduction; a copy of the version on canada.ca (the address of each page is at its end), not the official "
    "version, made without the Government of Canada's endorsement. The laws, services and programmes named are "
    f"Canada's, not the United States'. {LEGAL}", depth=1, units=[(r".", "Settling in Canada")], limit=80,
    country="Canada"), licence=CROWN_NC, licence_url=CANADA_TERMS, licence_page=CANADA_TERMS,
    licence_text=CANADA_TEXT, personal_use=True))

# "Welcome to the United States: A Guide for New Immigrants" (M-618): the English PDF and its translations, as USCIS
# publishes them. (code, language name, ISO 639-3 code). Haitian Creole (M-618_hc) and Tagalog (M-618_t) are left
# out: see NOT_INCLUDED.
M618 = USCIS + "/sites/default/files/document/guides/M-618{}.pdf"
M618_PAGE = USCIS + "/citizenship/civic-assimilation/settling-in-the-us"
M618_EDITIONS = [("", "English", "eng"), ("_sp", "Spanish", "spa"), ("_a", "Arabic", "ara"),
                 ("_c", "Chinese, traditional characters", "zho"), ("_cs", "Chinese, simplified characters", "zho"),
                 ("_fr", "French", "fra"), ("_k", "Korean", "kor"), ("_p", "Portuguese", "por"),
                 ("_r", "Russian", "rus"), ("_SOM", "Somali", "som"), ("_u", "Urdu", "urd"),
                 ("_v", "Vietnamese", "vie")]


def welcome_guide(code, language, iso):
    """The PDF entry of one edition of the M-618 guide (read whole by the builder)."""
    suffix = "" if not code else "_" + code.strip("_").lower()
    return K.us_pdf(GROUP, name="uscis_welcome_guide" + suffix,
                    title=f"Welcome to the United States: A Guide for New Immigrants (USCIS M-618, {language})",
                    subject="Settling in the United States", publisher=USCIS_PUBLISHER, pdf=M618.format(code),
                    page=M618_PAGE, language=iso, version=f"M-618{code} as published on uscis.gov",
                    description=f"USCIS's guide for new permanent residents ({language}): your rights and "
                                "responsibilities as a permanent resident, getting settled (a Social Security "
                                "number, housing, a job, money and taxes, education and child care, health care, "
                                "emergencies), how the US government works, and becoming a citizen.",
                    notice=USCIS_NOTICE)


PDFS = [welcome_guide(*e) for e in M618_EDITIONS]

COLLECTION = K.Collection("immig", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"immigration": lambda: [f"immig:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "immigration_us": "www.uscis.gov and www.justice.gov/eoir: works of the US government (17 U.S.C. 105, the line "
                      "checked on govinfo.gov's policies page at every build). robots.txt of both allows the pages "
                      "read (uscis.gov asks for Crawl-delay: 10, which the builder keeps); neither names an AI "
                      "company's reader or says ai-train=no (checked 2026-11-22).",
    "immigration_canada": "www.canada.ca/en/transparency/terms.html (checked at every build): non-commercial "
                          "reproduction allowed with the title, author and address of the original; the book is "
                          "personal use only. robots.txt allows /en/immigration-refugees-citizenship/ (checked "
                          "2026-11-22).",
}
NOT_INCLUDED = [
    ("Refugee admissions (US Department of State, Bureau of Population, Refugees, and Migration)", "Public domain, "
     "but www.state.gov refuses programs (\"403\", robots.txt included, checked 2026-11-22). USCIS's refugee pages "
     "and Policy Manual volume 4 are built. Link-only. Index: https://www.state.gov/refugee-admissions/"),
    ("Office of Refugee Resettlement (ORR, US Department of Health and Human Services)", "Public domain, but "
     "www.acf.hhs.gov answers programs with an empty page (\"202\", a bot check), checked 2026-11-22. Link-only. "
     "Index: https://www.acf.hhs.gov/orr"),
    ("FTC: immigration help scams and notarios", "Public domain, but consumer.ftc.gov refuses programs (403). USCIS's "
     "own scam pages are built (immig:uscis_immigration_guides). Link-only. Index: "
     "https://consumer.ftc.gov/articles/getting-legal-help-your-immigration-status"),
    ("Welcome to the United States (M-618) in Haitian Creole and Tagalog", "The builder writes each page's "
     "language for screen readers from the first two letters of the language code, which would mark Haitian "
     "Creole (hat) as Hausa and Tagalog (tgl) as Tajik; link-only until the builder knows those codes. Index: "
     "https://www.uscis.gov/sites/default/files/document/guides/M-618_hc.pdf and "
     "https://www.uscis.gov/sites/default/files/document/guides/M-618_t.pdf"),
    ("EOIR fact sheets and the pro bono providers list as PDF files", "The pages that link them are built "
     "(immig:eoir_court_legal_help); the PDF files themselves change every quarter and are linked from those pages. "
     "Index: https://www.justice.gov/eoir/list-pro-bono-legal-service-providers-map"),
    ("Immigration Advocates Network legal directory, CLINIC, ILRC and ImmigrationLawHelp.org guides", "Copyright of "
     "each non-profit; link-only for the owner. Index: https://www.immigrationadvocates.org/legaldirectory/ and "
     "https://www.immigrationlawhelp.org/"),
    ("Citizenship, naturalisation and the civics test", "Covered by the citizenship and civics collection (another "
     "part of the library); not repeated here. Index: https://www.uscis.gov/citizenship"),
    ("Canada's newcomer guides under the Open Government Licence - Canada", "None was found on open.canada.ca "
     "(searched for IRCC's newcomer and welcome guides, 2026-11-22); the canada.ca pages are built for personal use "
     "instead (immig:canada_newcomers). Index: https://open.canada.ca/data/en/dataset?organization=cic"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
