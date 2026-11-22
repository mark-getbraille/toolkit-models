"""Plain-language legal help guides for the reference library (the owner's request of 2026-11-22). Keys: legal-help
(every book), legal:<name>.

What this module builds, in plain words, each IN FULL, every book with the notice "This is general information, not
legal advice. Laws vary by state and change ...":
  - disability rights: the ADA.gov guides of the US Department of Justice (the ADA guide for small businesses,
    service animals, effective communication, the Title II and Title III primers, web accessibility guidance,
    parents' rights, voting, law enforcement, testing accommodations and the rest), every page of ADA.gov's
    resources;
  - the ADA National Network's fact sheets (adata.org; funded by NIDILRR): kept whole with their text unchanged,
    as their permission says "May be reproduced and distributed freely with attribution to ADA National Network";
  - job discrimination: the EEOC's pages for workers (each kind of discrimination, harassment, retaliation, how to
    file a charge, mediation, what happens next, filing a lawsuit);
  - benefits appeals: the VA's decision reviews and appeals (supplemental claim, higher-level review, Board appeal)
    and Medicare's appeals pages.
Tenants' rights and fair housing are in civic_help.py (HUD), consumer debt in money_help.py (CFPB). Every book is
national (federal law); state rules differ, as the notice says.

Legal aid organisations' own guides (the LawHelp.org network and the state sites) were checked one by one: none
offers its guides under an open licence ("All rights reserved"), and several shut out AI readers, so they are
link-only for the personal assistant, each with its state label and address in NOT_INCLUDED.

Licences: the federal guides are works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's
policies page at every build); the ADA National Network's permission line is checked on every fact sheet.

Run from the repository's folder:
  python3 textbooks/legal_help.py legal:ada_gov --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "law"
NOTICE = K.NOT_LEGAL_ADVICE
ADANN = "ADA National Network permission (reproduce and distribute freely with attribution)"
NO_CHANGES = {ADANN: "no-changes"}
ADANN_TEXT = r"May\s+be\s+reproduced\s+and\s+distributed\s+freely\s+with\s+attribution\s+to\s+ADA\s+National\s+Network"

GUIDES = [
    K.guide(GROUP, "ada_gov", "ADA.gov: guides to the Americans with Disabilities Act (US Department of Justice)",
            "Disability rights (ADA)", "Civil Rights Division, US Department of Justice (ADA.gov)",
            "https://www.ada.gov/resources/", r"^https://www\.ada\.gov/(resources|topics)/(?!.*nprm)[a-z0-9&;-]+/?$",
            "Every guide in ADA.gov's resources: the ADA's requirements for state and local governments and for "
            "businesses (the Title II and Title III primers and manuals), service animals, effective communication, "
            "web accessibility, medical care, child care, lodging, parking, pools, voting and polling places, "
            "testing accommodations, law enforcement, parents with disabilities, HIV and opioid use disorder, tax "
            "incentives, and how to file a complaint.",
            "A work of the US Department of Justice (public domain). " + NOTICE,
            follow=r"^https://www\.ada\.gov/topics/?$", depth=2, limit=150),
    K.guide(GROUP, "eeoc_workers", "Job discrimination: what workers need to know (EEOC)",
            "Employment discrimination", "US Equal Employment Opportunity Commission (EEOC)",
            "https://www.eeoc.gov/employees",
            r"^https://www\.eeoc\.gov/(age-discrimination|disability-discrimination[a-z-]*|equal-paycompensation-"
            r"discrimination|genetic-information-discrimination|harassment|national-origin-discrimination|"
            r"pregnancy-discrimination|race-color-discrimination|religious-discrimination|retaliation|"
            r"sex-based-discrimination|sexual-harassment|sexual-orientation-and-gender-identity-sogi-discrimination|"
            r"filing-charge-discrimination|how-file-charge-employment-discrimination|after-you-have-filed-charge|"
            r"mediation|filing-lawsuit|time-limits-filing-charge|employees/[a-z-]+|employees-job-applicants"
            r"(/[a-z-]+)?|coverage|confidentiality|prohibited-employment-policiespractices)$",
            "The EEOC's pages for workers and job applicants: each kind of discrimination the federal laws forbid "
            "(age, disability, equal pay, genetic information, national origin, pregnancy, race and colour, religion, "
            "sex, sexual orientation and gender identity), harassment and retaliation, who is covered, the time "
            "limits, how to file a charge, mediation, what happens after you file, and filing a lawsuit.",
            "A work of the US Equal Employment Opportunity Commission (public domain). " + NOTICE, limit=80),
    K.guide(GROUP, "va_decision_reviews", "VA decision reviews and appeals (US Department of Veterans Affairs)",
            "Benefits appeals (veterans)", "US Department of Veterans Affairs (VA.gov)",
            "https://www.va.gov/decision-reviews/",
            r"^https://www\.va\.gov/(decision-reviews(/[a-z-]+)*|resources/(choosing-a-decision-review-option|"
            r"decision-reviews-faqs))/?$",
            "VA.gov's guide to disagreeing with a VA decision: choosing a decision review option, the supplemental "
            "claim, higher-level review and Board appeal, legacy appeals, clinical and insurance appeals, contested "
            "claims, the family caregiver program reviews, what happens after you ask, and the questions people ask.",
            "A work of the US Department of Veterans Affairs (public domain). Accredited representatives help for "
            "free. " + NOTICE, limit=40),
    K.guide(GROUP, "medicare_appeals", "Medicare claims, appeals and complaints (Medicare.gov)",
            "Benefits appeals (Medicare)", "Centers for Medicare & Medicaid Services (Medicare.gov)",
            "https://www.medicare.gov/providers-services/claims-appeals-complaints",
            r"^https://www\.medicare\.gov/providers-services/claims-appeals-complaints(/[a-z0-9-]+)*$",
            "Medicare.gov's pages on claims, appeals and complaints: checking your claims, filing an appeal in "
            "Original Medicare, Medicare Advantage and drug plans, the levels of appeal, fast appeals when a hospital "
            "or other service ends, and filing a complaint or grievance.",
            "A work of the Centers for Medicare & Medicaid Services (public domain). " + NOTICE,
            follow=r"^https://www\.medicare\.gov/providers-services/claims-appeals-complaints/[a-z-]+$", depth=2,
            limit=60),
    dict(K.guide(GROUP, "adata_factsheets", "ADA National Network fact sheets", "Disability rights (ADA)",
                 "ADA National Network (adata.org), funded by NIDILRR", "https://adata.org/",
                 r"^https://adata\.org/factsheet/[a-z0-9-]+/?$",
                 "Every fact sheet of the ADA National Network: an ADA overview and its definitions, knowing your "
                 "rights, reasonable accommodations and modifications, service animals, wheelchairs and other "
                 "mobility devices, parking, accessible health care and medical equipment, schools from K-12 to "
                 "college, employment for veterans, leave from work, religious entities, food service, ground "
                 "transportation, fire alarms, customer service tips and enforcing the ADA.",
                 "© ADA National Network. \"May be reproduced and distributed freely with attribution to ADA National "
                 "Network (adata.org).\" Kept whole with its text unchanged. The contents do not necessarily represent "
                 "the policy of NIDILRR, ACL or HHS. " + NOTICE, limit=80),
         licence=ADANN, licence_url="https://adata.org/grant-disclaimer", licence_page="https://adata.org/factsheet/"
         "ada-overview/", licence_text=ADANN_TEXT, page_mark=ADANN_TEXT, unchanged=True),
]

COLLECTION = K.Collection("legal", GROUP, guides=GUIDES,
                          words={"legal-help": lambda: [f"legal:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "federal_legal_guides": "ADA.gov, eeoc.gov, va.gov and medicare.gov: works of the US government (17 U.S.C. 105, "
                            "checked on govinfo.gov's policies page at every build). Their robots.txt files allow "
                            "the pages read and have no AI rules (checked 2026-11-22).",
    "adata_factsheets": "adata.org fact sheets (checked on every page): \"© Copyright ADA National Network. All Rights "
                        "Reserved. May be reproduced and distributed freely with attribution to ADA National Network "
                        "(adata.org).\" A permission to copy and distribute that says nothing of changes: the fact "
                        "sheets are kept whole with their text unchanged (sources.NO_CHANGES). robots.txt disallows "
                        "only /wp-admin/.",
}
NOT_INCLUDED = [
    ("LawHelp.org network guides (national directory)", "www.lawhelp.org closes the connection to programs (checked "
     "2026-11-22). Link-only. Index: https://www.lawhelp.org/"),
    ("Illinois Legal Aid Online (Illinois)", "Its robots.txt shuts out AI readers (checked 2026-11-22). Link-only. "
     "Index: https://www.illinoislegalaid.org/legal-information"),
    ("WashingtonLawHelp.org (Washington)", "Its robots.txt says \"ai-train=no\" and shuts out ClaudeBot. Link-only. "
     "Index: https://www.washingtonlawhelp.org/"),
    ("Michigan Legal Help (Michigan)", "Its terms say its content is the property of Michigan Legal Help, \"All Rights "
     "Reserved\"; no open licence. Link-only. Index: https://michiganlegalhelp.org/resources"),
    ("TexasLawHelp.org (Texas), LawHelpNY (New York), Ohio Legal Help (Ohio), Oregon Law Help (Oregon), AZLawHelp "
     "(Arizona), LawHelpMN (Minnesota)", "Each says \"All Rights Reserved\" (TexasLawHelp.org; Pro Bono Net; Ohio "
     "Legal Help; the Oregon State Bar; the Arizona Bar Foundation; the Minnesota Legal Services Coalition), checked "
     "2026-11-22. Link-only. Index: https://texaslawhelp.org/ , https://www.lawhelpny.org/ , "
     "https://www.ohiolegalhelp.org/ , https://oregonlawhelp.org/ , https://azlawhelp.org/ , "
     "https://www.lawhelpmn.org/"),
    ("Alaska Law Help (Alaska)", "Its robots.txt shuts out AI readers. Link-only. Index: https://www.alaskalawhelp.org/"),
    ("LawHelpCA (California) and LawHelpNC (North Carolina)", "LawHelpCA closes the connection to programs; LawHelpNC "
     "did not answer. Link-only. Index: https://www.lawhelpca.org/ and https://lawhelpnc.org/"),
    ("Legal Services Corporation (lsc.gov)", "LSC is a private non-profit corporation funded by Congress, not a "
     "government agency: its site says \"© Legal Services Corporation\"; no open licence. Link-only. Index: "
     "https://www.lsc.gov/about-lsc/what-legal-aid/get-legal-help"),
    ("Maryland People's Law Library, Massachusetts Legal Help, Legal Aid at Work, California Courts Self-Help Guide",
     "No open licence found on their pages or terms (checked 2026-11-22). Link-only. Index: "
     "https://www.peoples-law.org/ , https://www.masslegalhelp.org/ , https://legalaidatwork.org/ , "
     "https://selfhelp.courts.ca.gov/"),
    ("Nolo's legal encyclopedia", "Copyright Nolo, and nolo.com refuses programs (403). Link-only. Index: "
     "https://www.nolo.com/legal-encyclopedia"),
    ("Social Security disability appeals (ssa.gov)", "ssa.gov refuses programs (403). Link-only. Index: "
     "https://www.ssa.gov/benefits/disability/appeal.html"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
