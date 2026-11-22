"""Veterans' benefits, health and transition for the reference library, in its own group "Reference, veterans" (the
owner's request of 2026-11-22). Keys: veterans (every book), veteran:<name>.

What this module builds, in plain words, each IN FULL:
  - "Federal Benefits for Veterans, Dependents and Survivors" (the VA's benefits booklet, 2020 edition: the last one
    the VA published; read whole from its Internet Archive copy because va.gov no longer hosts it): health care,
    disability compensation, pensions, education and training (the GI Bill), vocational rehabilitation, home loans,
    life insurance, burial benefits, dependents' and survivors' benefits, appeals, and other federal benefits;
  - the VA's homeless programmes (department.va.gov/homeless): the National Call Center for Homeless Veterans
    (877-424-3838), HUD-VASH housing vouchers, Supportive Services for Veteran Families, domiciliary care, health
    care for homeless veterans, legal services, dental care and food security;
  - VA mental health (mentalhealth.va.gov): getting care, PTSD, depression, anxiety, substance use, suicide
    prevention, military sexual trauma, traumatic brain injury, transitioning from service, women, older veterans
    and families;
  - the Veterans Crisis Line's own pages (veteranscrisisline.net): call 988 then press 1, text 838255, chat, the
    Military Crisis Line, what happens when you call, and how to help a veteran in crisis;
  - the National Center for PTSD (ptsd.va.gov): understanding PTSD and its treatment, getting help, and help for
    families and friends;
  - the Department of Labor's Veterans' Employment and Training Service (DOL VETS): USERRA (job rights after military
    service), the Transition Assistance Program's employment part, the Homeless Veterans' Reintegration Program,
    disabled veterans' employment, apprenticeships and veterans' preference;
  - the VA's discharge upgrade instructions and its pages on accredited representatives (who may help with a claim).
  Every book's notice says how to reach the Veterans Crisis Line (CRISIS) and ends with LEGAL ("General information,
  not legal advice; check the current rules or ask an accredited representative or lawyer.").

Already in the library and not repeated (linked by name): VA.gov's benefit guides, every page (dir:va_benefits:
health care, disability compensation, the PACT Act and toxic exposures, education and the GI Bill, pension, home
loans, life insurance, burials, family and caregiver benefits, records), VA decision reviews and appeals
(legal:va_decision_reviews), the VA Caregiver Support Program (homecare:va_caregiver_support), Military OneSource for
military families (dir:military_onesource), the VA Blind Rehabilitation Service (the vision collection and
eyes:va_blind_rehabilitation), the VA's benefit rules in the CFR and US Code (law: keys), and Social Security's
disability benefits (the benefits collection).

Not built (NOT_INCLUDED, link-only): DoD TAP's site (a script application), veteran service organisations (each
its own copyright), and newer editions of the benefits booklet (none was published after 2020).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); the 2020 booklet's Internet Archive copy is marked with the Public Domain Mark. robots.txt allows every page
read; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/veterans.py veteran:va_mental_health --out build/textbooks --limit 5
  python3 textbooks/veterans.py --list veterans
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "veterans"
GROUPS = {GROUP: "Reference, veterans"}

# The line every legal or benefits book of these collections ends with (the owner's words of 2026-11-22).
LEGAL = "General information, not legal advice; check the current rules or ask an accredited representative or lawyer."
# How to reach the Veterans Crisis Line, in every book (as VA says it on veteranscrisisline.net).
CRISIS = ("Veterans Crisis Line: dial 988 then press 1, text 838255, or chat at VeteransCrisisLine.net; deaf and hard "
          "of hearing callers can use their preferred relay service or dial 711 then 988. In an emergency call 911.")
VA = "US Department of Veterans Affairs (VA)"
VA_NOTICE = f"A work of the US Department of Veterans Affairs (public domain). {CRISIS} {LEGAL}"

GUIDES = [
    K.guide(GROUP, "va_homeless", "Homeless veterans programmes (US Department of Veterans Affairs)",
            "Help for homeless veterans", VA + ", Homeless Programs Office", "https://department.va.gov/homeless",
            r"^https://department\.va\.gov/homeless(/[a-z0-9-]+)*/?$",
            "The VA's programmes for veterans who are homeless or at risk: the National Call Center for Homeless "
            "Veterans (877-424-3838, every hour of every day), HUD-VASH housing vouchers with VA case management, "
            "Supportive Services for Veteran Families (help to keep or find housing), Grant and Per Diem transitional "
            "housing, domiciliary care, health care for homeless veterans, the homeless veterans dental programme, "
            "legal services, employment help and food security, every page.",
            f"{VA_NOTICE} Homeless or at risk: call the National Call Center for Homeless Veterans, 877-424-3838.",
            depth=2, follow=r"^https://department\.va\.gov/homeless/[a-z0-9-]+/?$",
            units=[(r".", "Homeless programmes")], limit=150),
    K.guide(GROUP, "va_mental_health", "VA mental health: getting care, PTSD, depression, suicide prevention and more",
            "Veterans' mental health", VA + ", Veterans Health Administration (mentalhealth.va.gov)",
            "https://www.mentalhealth.va.gov/MENTALHEALTH/index.asp",
            r"^https://www\.mentalhealth\.va\.gov/(?i:mentalhealth)/(?!healthcare-providers|student-faculty|search|"
            r"site-map|spread-the-word)[a-z0-9_/-]+\.asp$",
            "The VA's mental health pages for veterans and families, every page: how to get mental health care "
            "(eligibility, same-day care, Vet Centers, local care, residential rehabilitation), PTSD, depression, "
            "anxiety, bipolar disorder, schizophrenia, substance use and quitting tobacco, suicide prevention, "
            "military sexual trauma, traumatic brain injury, transitioning from service, women veterans, older "
            "veterans, and support for families.", VA_NOTICE, depth=2,
            follow=r"^https://www\.mentalhealth\.va\.gov/(?i:mentalhealth)/[a-z0-9_-]+/index\.asp$",
            units=[(r"(?i)/get-help/", "Getting care"), (r"(?i)/suicide_prevention/", "Suicide prevention"),
                   (r"(?i)/families/", "Families"), (r".", "Conditions and groups")], limit=250),
]

VCL = "https://www.veteranscrisisline.net"
VCL_PAGES = [VCL + p for p in ("/", "/get-help-now/call/", "/get-help-now/text/", "/get-help-now/chat/",
                               "/get-help-now/military-crisis-line/", "/about/how-it-works/", "/about/what-is-988/",
                               "/about/about-us/", "/veteran-support/", "/how-you-can-help/", "/local-resources/")]
GUIDES.append(K.us_web(
    GROUP, name="veterans_crisis_line", title="Veterans Crisis Line: how to reach it and what happens (VA)",
    subject="Veterans Crisis Line", publisher=VA + ", Veterans Crisis Line", source=VCL_PAGES[0],
    crawl=[(VCL_PAGES[0], 0)], urls=list(VCL_PAGES), pages=r"^https://www\.veteranscrisisline\.net/[a-z0-9/-]*$",
    description="The Veterans Crisis Line's own pages: calling 988 and pressing 1, texting 838255 and chatting "
                "online, the Military Crisis Line for service members, what happens when you reach out, what 988 is, "
                "support for veterans, how to help someone in crisis, and finding local resources.",
    notice=VA_NOTICE, unit_rules=[(r"get-help-now", "Get help now"), (r".", "About the Crisis Line")],
    limit=len(VCL_PAGES) + 5))
GUIDES.append(K.guide(
    GROUP, "ptsd_national_center", "PTSD: understanding it, treatment, getting help and helping a family member "
    "(VA National Center for PTSD)", "PTSD", VA + ", National Center for PTSD",
    ["https://www.ptsd.va.gov/understand/index.asp", "https://www.ptsd.va.gov/gethelp/index.asp",
     "https://www.ptsd.va.gov/family/index.asp"],
    r"^https://www\.ptsd\.va\.gov/(PTSD/)?(understand|understand_tx|gethelp|family|living)/[a-z0-9_/-]+\.asp$",
    "The National Center for PTSD's pages for veterans and the public, every page: what PTSD is, its symptoms, "
    "common reactions after trauma, related problems (sleep, anger, substance use, moral injury), the treatments "
    "that work (talk therapies and medicines) and how to choose one, how to get help, self-help and coping, and how "
    "family members and friends can help and look after themselves.", VA_NOTICE, depth=2,
    follow=r"^https://www\.ptsd\.va\.gov/(PTSD/)?(understand|understand_tx|gethelp|family|living)/index\.asp$",
    units=[(r"/understand_tx/", "Treatment"), (r"/understand/", "Understanding PTSD"),
           (r"/family/", "Family and friends"), (r".", "Getting help and living with PTSD")], limit=250))

DOL = "https://www.dol.gov/agencies/vets"
GUIDES.append(K.guide(
    GROUP, "dol_vets", "Veterans' employment, USERRA job rights and the Transition Assistance Program (US Department "
    "of Labor, VETS)", "Veterans' employment and job rights", "US Department of Labor, Veterans' Employment and "
    "Training Service (VETS)", [DOL + "/programs", DOL + "/disabled-veterans", DOL + "/apprenticeship"],
    r"^https://www\.dol\.gov/agencies/vets/(programs|disabled-veterans|apprenticeship|veterans)(/[a-z0-9-]+)*$",
    "The Department of Labor's pages for veterans, every page: USERRA (the Uniformed Services Employment and "
    "Reemployment Rights Act: getting your civilian job back after military service, health plans and pensions, "
    "and how to file a complaint), the Transition Assistance Program's employment workshops, employment help for "
    "disabled veterans, the Homeless Veterans' Reintegration Program, Jobs for Veterans State Grants (veterans' "
    "employment representatives at American Job Centers), apprenticeships, and veterans' preference.",
    f"From the US Department of Labor: a US government work (public domain). {CRISIS} {LEGAL}", depth=2,
    follow=r"^https://www\.dol\.gov/agencies/vets/(programs|disabled-veterans)/[a-z0-9-]+$",
    units=[(r"/userra", "USERRA job rights"), (r"/tap", "Transition Assistance Program"),
           (r"/disabled-veterans", "Disabled veterans"), (r"/hvrp|/hvmp", "Homeless veterans"),
           (r".", "More programmes")], limit=150))

DISCHARGE_PAGES = ["https://www.va.gov/discharge-upgrade-instructions/", "https://www.va.gov/ogc/accreditation.asp",
                   "https://www.va.gov/resources/va-accredited-representative-faqs/"]
GUIDES.append(K.us_web(
    GROUP, name="va_discharge_representatives", title="Discharge upgrades and accredited representatives (VA)",
    subject="Discharge upgrades and help with claims", publisher=VA, source=DISCHARGE_PAGES[0],
    crawl=[(DISCHARGE_PAGES[0], 0)], urls=list(DISCHARGE_PAGES),
    pages=r"^https://www\.va\.gov/(discharge-upgrade-instructions/|ogc/accreditation\.asp|resources/"
          r"va-accredited-representative-faqs/)$",
    description="How to ask for a discharge upgrade or correction (which board to apply to and how), and the VA's "
                "pages on accreditation: who may help you prepare and present a VA claim (accredited attorneys, "
                "claims agents and veterans service organisation representatives), that accredited representatives "
                "may not charge for help with an initial claim, and how to check that someone is accredited.",
    notice=f"{VA_NOTICE} Check that anyone who helps with a VA claim is accredited, with the VA's accreditation "
           f"search on va.gov.", unit_rules=[(r"discharge", "Discharge upgrades"), (r".", "Accredited "
                                                                                       "representatives")],
    limit=len(DISCHARGE_PAGES) + 2))

PDFS = [
    K.us_pdf(GROUP, name="va_federal_benefits_2020", title="Federal Benefits for Veterans, Dependents and Survivors "
             "(VA, 2020 edition)", subject="Veterans' benefits", publisher=VA + ", Office of Public and "
             "Intergovernmental Affairs", archive="federal-benefits-for-veterans-2020-ocr", published="2020",
             version="2020 edition (Internet Archive item federal-benefits-for-veterans-2020-ocr)",
             description="The VA's benefits handbook, every chapter: VA health care (eligibility, enrolment, "
                         "priority groups, copays, women veterans, mental health), disability compensation, "
                         "pensions, education and training (the Post-9/11 GI Bill and others), vocational "
                         "rehabilitation and employment, home loans, life insurance, burial and memorial benefits, "
                         "dependents' and survivors' benefits, transition and appeals, and other federal benefits "
                         "for veterans.",
             notice=f"A work of the US Department of Veterans Affairs (public domain; the Internet Archive copy "
                    f"carries the Public Domain Mark), read from a scan whose machine-read text has the scanner's "
                    f"mistakes. 2020 edition, the last the VA published: payment rates, copays and rules have "
                    f"changed since, and it predates the PACT Act of 2022 (toxic exposures): check VA.gov or the "
                    f"library's VA benefits guides (dir:va_benefits). {CRISIS} {LEGAL}"),
]

COLLECTION = K.Collection("veteran", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"veterans": lambda: [f"veteran:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "veterans_us": "department.va.gov, www.va.gov, www.mentalhealth.va.gov, www.ptsd.va.gov, "
                   "www.veteranscrisisline.net and www.dol.gov: works of the US government (17 U.S.C. 105, the line "
                   "checked on govinfo.gov's policies page at every build); robots.txt allows the pages read and "
                   "none names an AI company's reader or says ai-train=no (checked 2026-11-22).",
    "veterans_booklet": "Federal Benefits for Veterans, Dependents and Survivors (2020): a VA publication (17 U.S.C. "
                        "105), read from the Internet Archive item federal-benefits-for-veterans-2020-ocr (Public "
                        "Domain Mark) because www.va.gov/opa/publications/benefits_book.asp now redirects to "
                        "department.va.gov and the PDFs answer 404 (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("DoD Transition Assistance Program (dodtap.mil)", "A script application: the site's pages come to programs "
     "as an empty frame (dodtap.mil/dodtap/app), so there is no text to read (checked 2026-11-22). DOL VETS's TAP "
     "pages and Military OneSource's transition pages (dir:military_onesource) are built. Link-only. Index: "
     "https://www.dodtap.mil/"),
    ("Veteran service organisations: DAV, The American Legion, VFW, AMVETS, Paralyzed Veterans of America, Vietnam "
     "Veterans of America, Blinded Veterans Association, Wounded Warrior Project", "Each organisation's own "
     "copyright; link-only. Their accredited representatives help with VA claims free of charge (check "
     "accreditation with the VA's search). Index: https://www.va.gov/ogc/apps/accreditation/index.asp and "
     "https://www.dav.org/ https://www.legion.org/ https://www.vfw.org/ https://bva.org/"),
    ("Newer editions of Federal Benefits for Veterans, Dependents and Survivors", "None found: the VA's booklet page "
     "now redirects to department.va.gov and the 2021 to 2024 PDF addresses answer 404 (checked 2026-11-22); the "
     "2020 edition is built with a note, and VA.gov's current guides are in the library (dir:va_benefits). Index: "
     "https://department.va.gov/get-started/"),
    ("Army, Navy, Air Force, Marine Corps and Coast Guard discharge review boards and boards for correction of "
     "military records", "Each service's own site; the VA's discharge upgrade instructions (built) say which board "
     "to use. Link-only. Index: https://arba.army.pentagon.mil/ and https://www.secnav.navy.mil/mra/bcnr/"),
    ("National Veterans Legal Services Program's Veterans Benefits Manual", "Copyright (LexisNexis); link-only. Index: "
     "https://www.nvlsp.org/"),
    ("VA benefit guides, decision reviews, caregiver support and Military OneSource", "Already in the library: "
     "dir:va_benefits, legal:va_decision_reviews, homecare:va_caregiver_support and dir:military_onesource; not "
     "repeated. Index: https://www.va.gov/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
