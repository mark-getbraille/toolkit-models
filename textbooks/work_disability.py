"""Disability and employment for the reference library (the owner's request of 2026-11-22). Keys: work (every book),
work:<name>.

What this module builds, in plain words, each IN FULL:
  - the Office of Disability Employment Policy's topic pages (US Department of Labor): the ADA at work,
    accommodations and communications access, customized and integrated employment, apprenticeship, self-employment,
    employment supports, personal assistance services, transportation, technology, youth, veterans, older workers,
    federal employment, tax incentives for employers, and the programme areas and initiatives;
  - Ticket to Work (Social Security's free employment programme for people on disability benefits, at
    choosework.ssa.gov): how it works, work incentives, the ticket dictionary, the fact sheets (trial work period,
    Medicare and Medicaid supports), "Your Path to Work", federal employment (Schedule A, Section 503) and wage
    reporting.
The ADA National Network's fact sheets are in legal_help.py (legal:adata_factsheets).

Not built: the Job Accommodation Network (askjan.org; its robots.txt shuts out ClaudeBot, anthropic-ai and other AI
readers), the AbleData archive (the site was retired; no public-domain copy that programs may read was found) and
NIDILRR's grantees' guides (each has its own copyright): link-only in NOT_INCLUDED.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build). dol.gov and choosework.ssa.gov allow the pages in robots.txt; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/work_disability.py work:odep --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "disability"

GUIDES = [
    K.guide(GROUP, "odep", "Disability employment policy: ODEP's topics (US Department of Labor)",
            "Disability and employment", "Office of Disability Employment Policy, US Department of Labor",
            "https://www.dol.gov/agencies/odep",
            r"^https://www\.dol\.gov/agencies/odep/(topics|program-areas|initiatives|ada|publications/faqs)"
            r"(/[A-Za-z0-9-]+)*$",
            "Every topic page of the Office of Disability Employment Policy: the ADA at work and reasonable "
            "accommodations, communications access, customized and integrated employment, apprenticeship, "
            "self-employment and small business, employment supports, personal assistance services, healthcare, "
            "housing, transportation and technology, youth, veterans and older workers, federal employment, "
            "recruitment and retention, tax incentives for employers, stay-at-work and return-to-work, and ODEP's "
            "programme areas, initiatives (National Disability Employment Awareness Month) and questions.",
            "A work of the US Department of Labor (public domain).", depth=2,
            follow=r"^https://www\.dol\.gov/agencies/odep/(topics|program-areas)$",
            units=[(r"/topics/", "Topics"), (r"/program-areas/", "Programme areas"),
                   (r"/initiatives/", "Initiatives"), (r".", "About ODEP")], limit=150),
    K.guide(GROUP, "ticket_to_work", "Ticket to Work: Social Security's employment programme (choosework.ssa.gov)",
            "Disability benefits and work", "Social Security Administration, Ticket to Work Program",
            "https://choosework.ssa.gov/library",
            r"^https://choosework\.ssa\.gov/(about(/[a-z-]+)?|library/(?!videos|recent|success-stories)"
            r"[A-Za-z0-9-]+(/[a-z0-9-]+)*)$",
            "Ticket to Work's guides: how the programme works and who can use it, work incentives, the ticket "
            "dictionary and frequently asked questions, the fact sheets (trial work period, Medicare and Medicaid "
            "employment supports and the rest), \"Your Path to Work\" (ready to work, getting a job, managing your "
            "job), finding an employment network and assigning your ticket, federal employment (Schedule A, Section "
            "503 for federal contractors), timely progress reviews and reporting wages.",
            "A work of the Social Security Administration (public domain). Free help: the Ticket to Work Help Line, "
            "1-866-968-7842 (TTY 1-866-833-2967).", depth=2,
            follow=r"^https://choosework\.ssa\.gov/library/(fact-sheets|your-path-to-work|federal-employment-"
                   r"initiatives)$",
            content=(r'<div class="clearfix text-formatted field field--name-body[^>]*>', r"<footer"),
            units=[(r"/about", "About Ticket to Work"), (r"/library/your-path-to-work", "Your Path to Work"),
                   (r"/library/fact-sheet", "Fact sheets"), (r"/library/federal-employment", "Federal employment"),
                   (r".", "More guides")], limit=150),
]

COLLECTION = K.Collection("work", GROUP, guides=GUIDES,
                          words={"work": lambda: [f"work:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "odep_ticket_to_work": "dol.gov/agencies/odep and choosework.ssa.gov: works of the US government (17 U.S.C. "
                           "105, checked on govinfo.gov's policies page at every build). Their robots.txt files "
                           "allow the pages; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("Job Accommodation Network (askjan.org; funded by ODEP)", "Its robots.txt shuts out ClaudeBot, anthropic-ai, "
     "GPTBot and other AI readers (checked again 2026-11-22), and it is run by West Virginia University with no open "
     "licence. Link-only for the personal assistant. Index: https://askjan.org/a-to-z.cfm"),
    ("AbleData (assistive technology product database, ACL/NIDILRR)", "Retired in 2021; its public-domain records are "
     "not offered as a download that programs may read (abledata.acl.gov no longer answers). Link-only. Index: "
     "https://acl.gov/programs/assistive-technology/assistive-technology"),
    ("NIDILRR-funded guides (Model Systems Knowledge Translation Center and other grantees)", "Each grantee holds "
     "its own copyright; the ones checked state no open licence. Link-only. Index: https://msktc.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
