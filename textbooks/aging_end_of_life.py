"""Aging and end-of-life planning for the reference library, in its own group "Reference, aging and end of life"
(the owner's request of 2026-11-22). Keys: aging-end-of-life (every book), aging:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the Administration for Community Living's long-term care guide (what long-term care is, who needs it, the
    costs and who pays, Medicare, Medicaid and VA benefits, staying in your home and avoiding falls, living in a
    facility, and the legal steps: advance care plans, powers of attorney, wills);
  - the VA's Geriatrics and Extended Care pages (home and community care, nursing homes, paying for long-term care,
    memory loss, hospice and palliative care, advance care planning and completing an advance directive);
  - NCI's pages on advanced illness and the end of life (choices for care, hospice, talking with family, feelings,
    planning, finding meaning, advance directives);
  - NIDCD's hearing pages (age-related hearing loss, hearing aids and over-the-counter hearing aids, assistive
    devices, captions, tinnitus, balance);
  - when someone dies: the IRS's pages on a deceased person's taxes, and the VA's burial and memorial benefits
    (National Cemetery Administration and va.gov);
  - the Justice Department's Elder Justice Initiative pages for the public (kinds of elder abuse, the red flags,
    scams against older people, guardianship, finding help and reporting abuse);
  - "Help lines": a page written for this library with the Eldercare Locator, the National Elder Fraud Hotline and
    1-800-MEDICARE, each checked on an official page at every build.
  (Already in the library and not repeated: Medicare & You and Medicare.gov's guides, hospice coverage included
  (help:medicare_and_you, help:medicare_guides), Medicare appeals (legal:medicare_appeals), ACL's programme pages
  and elder rights (fam:acl_aging_caregiving), CDC's caregiving, falls (STEADI) and dementia pages and the VA
  Caregiver Support pages (homecare:), the CFPB's guides for managing someone else's money (money:cfpb_consumer_
  tools), USA.gov's death benefits pages (help:usa_gov), the FTC Funeral Rule (law:cfr_16_453_funeral_rule) and
  NCI's grief pages (mind:nci_grief_caregivers).)

Every book's notice ends with the aging note: general information, not medical, legal or financial advice; the
Eldercare Locator; in an emergency call 911; in a mental health crisis call or text 988.

Not built (NOT_INCLUDED, link-only): the National Institute on Aging and Alzheimers.gov (bot check), organdonor.gov,
SSA and the FTC's consumer pages (refuse programs), state advance directive forms (each state's own terms), and the
copyright guides (AARP, the Alzheimer's Association, CaringInfo, Five Wishes, Nolo).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); NCI's reuse policy is checked at every build and its credit given.

Run from the repository's folder:
  python3 textbooks/aging_end_of_life.py aging:help_lines --out build/textbooks
  python3 textbooks/aging_end_of_life.py --list aging-end-of-life
"""

import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared helpers and notes of the four new health modules

GROUP = "agingeol"
GROUPS = {GROUP: "Reference, aging and end of life"}
NOTE = ("General information, not medical, legal or financial advice or a diagnosis: ask your doctor, a lawyer or "
        "legal aid office, or your local Area Agency on Aging (the Eldercare Locator, 1-800-677-1116). In an "
        "emergency call 911; in a mental health crisis call or text 988.")

HELP_CHECKS = [
    ("Older adults and caregivers", M.CDC_HELP, r"Eldercare Locator.{0,120}1-800-677-1116",
     "Eldercare Locator, which connects older adults and their families to local services (meals, transport, "
     "caregiver support, Area Agencies on Aging): call 1-800-677-1116; TTY users can dial 711 and ask for "
     "1-800-677-1116."),
    ("Abuse, neglect and scams", "https://www.justice.gov/elderjustice/find-help-or-report-abuse",
     r"National Elder Fraud Hotline 1-833-FRAUD-11 \( ?833-372-8311 ?\)",
     "National Elder Fraud Hotline (US Department of Justice), for older people who were scammed or financially "
     "exploited: call 1-833-FRAUD-11 (1-833-372-8311), 10 a.m. to 6 p.m. Eastern Time, Monday to Friday. For abuse "
     "or neglect happening now, call 911."),
    ("Medicare", "https://www.medicare.gov/talk-to-someone", r"1-800-MEDICARE.{0,20}1-800-633-4227",
     "Medicare: call 1-800-MEDICARE (1-800-633-4227), 24 hours a day."),
]


def help_book(name, work, cache=None, left_out=None, limit=None):
    """The aging help lines page, its numbers checked on the official pages now."""
    return M.help_lines_book("aging", GROUP, name, "Help lines: the Eldercare Locator, elder fraud and Medicare (US)",
                             "Help lines for older adults", HELP_CHECKS,
                             "If someone is in danger right now, call 911.", "The US help lines for local services "
                             "for older adults, elder fraud and abuse, and Medicare, each checked on an official page "
                             "when the book was made.", NOTE, cache=cache)


NCI = "https://www.cancer.gov/about-cancer"
VA_GER = "https://www.va.gov/geriatrics/pages/"
NIDCD = "https://www.nidcd.nih.gov/health/"
EJI = "https://www.justice.gov/elderjustice/"

GUIDES = [
    K.guide(GROUP, "acl_long_term_care", "Long-term care: planning, paying and the legal steps (Administration for "
            "Community Living)", "Long-term care", "Administration for Community Living (ACL), US Department of "
            "Health and Human Services", "https://acl.gov/ltc", r"^https://acl\.gov/ltc(/[a-z0-9-]+){1,3}$",
            "ACL's long-term care guide (what was LongTermCare.gov), every page: what long-term care is, who needs "
            "it and how much, who provides it and where, planning ahead at every age, care for people with dementia "
            "and for LGBT adults; the costs and who pays (paying privately, long-term care insurance, Medicare, "
            "Medicaid and its estate recovery, VA benefits, other state programmes); staying in your home and "
            "avoiding a fall, living in a facility; and the legal steps (advance care plans, health care and "
            "financial powers of attorney, wills and whether you need a lawyer).",
            f"A work of the US Department of Health and Human Services (public domain). {NOTE}", depth=2,
            follow=r"^https://acl\.gov/ltc/[a-z0-9-]+(/[a-z0-9-]+)?$",
            units=[(r"/costs-and-who-pays|/medicare-medicaid", "Costs and who pays"), (r"/housing", "Housing"),
                   (r"/legal-steps", "The legal steps"), (r".", "Basic needs and planning")], limit=80,
            content=(r'role="main" id="main-content">|<main\b[^>]*>', r'<footer\b')),
    K.guide(GROUP, "va_geriatrics", "Geriatrics, long-term care, hospice and advance care planning (VA)",
            "Long-term care and end-of-life planning", "Geriatrics and Extended Care, US Department of Veterans "
            "Affairs",
            [VA_GER + p for p in ("advance_care_planning_topics.asp", "Home_and_Community_Based_Services.asp",
                                  "Nursing_Home_and_Residential_Services.asp", "Paying_for_Long_Term_Care.asp",
                                  "memory_loss_and_brain_health.asp", "Hospice_Care.asp",
                                  "Health_Fitness_Rehabilitation.asp")],
            r"^https://www\.va\.gov/geriatrics/pages/[A-Za-z_]+\.asp$",
            "The VA's Geriatrics and Extended Care pages, every page: home and community based services (home health "
            "aides, adult day care, respite care, home-based primary care), nursing homes and residential care, "
            "paying for long-term care, memory loss and brain health, hospice and palliative care, health, fitness "
            "and rehabilitation, and advance care planning (making health care decisions, completing an advance "
            "directive, engaging your support team). Most of it applies to anyone, not only veterans.",
            f"A work of the US Department of Veterans Affairs (public domain). {NOTE}", depth=1,
            units=[(r"acp_|advance_care|decisions", "Advance care planning"), (r"Hospice|Palliative", "Hospice and "
                   "palliative care"), (r".", "Long-term care")], limit=80, content=M.VA_CONTENT),
    dict(K.guide(GROUP, "nci_end_of_life", "Advanced illness, hospice and planning for the end of life (NCI)",
                 "End-of-life care", "National Cancer Institute (NCI), National Institutes of Health",
                 f"{NCI}/advanced-cancer",
                 r"^https://www\.cancer\.gov/about-cancer/(advanced-cancer(/(?!caregivers)[a-z0-9-]+){1,2}|"
                 r"managing-care/advance-directives)$",
                 "NCI's pages on advanced illness and the end of life, every page: choices for care (treatment, "
                 "palliative care, hospice and where to receive it), talking with family and the care team, "
                 "feelings and coping, planning (advance directives, living wills and health care proxies, legal "
                 "and financial matters), finding purpose and meaning, and the questions to ask. Written for people "
                 "with cancer; most of it applies to any serious illness.",
                 f"{M.NCI_CREDIT} {NOTE} NCI's Contact Center: 1-800-4-CANCER (1-800-422-6237).", depth=2,
                 follow=r"^https://www\.cancer\.gov/about-cancer/advanced-cancer/(?!caregivers)[a-z0-9-]+$",
                 units=[(r"care-choices", "Choices for care"), (r"planning|advance-directives", "Planning ahead"),
                        (r".", "Living with advanced illness")], limit=60),
         licence_page=M.NCI_TERMS, licence_text=M.NCI_TEXT),
    M.pages_book(GROUP, "nidcd_hearing", "Hearing loss, hearing aids and balance (NIDCD)", "Hearing loss",
                 "National Institute on Deafness and Other Communication Disorders (NIDCD), National Institutes of "
                 "Health",
                 [NIDCD + p for p in ("age-related-hearing-loss", "hearing-aids", "over-counter-hearing-aids",
                                      "who-can-i-turn-help-my-hearing-loss", "adult-hearing-health-care",
                                      "assistive-devices-people-hearing-voice-speech-or-language-disorders",
                                      "captions-deaf-and-hard-hearing-viewers", "telecomm", "tinnitus",
                                      "sudden-deafness", "menieres-disease", "balance", "how-do-we-hear")],
                 r"^https://www\.nidcd\.nih\.gov/health/[a-z0-9-]+$",
                 "NIDCD's pages on hearing, each whole (FDA's hearing aid pages are dis:fda_hearing_aids): age-related hearing loss, hearing aids (styles, how they "
                 "work, getting used to them) and over-the-counter hearing aids, who can help with hearing loss, "
                 "adult hearing health care, assistive devices (hearing loops, alerting devices, amplified phones), "
                 "captions, telecommunications relay services, tinnitus, sudden deafness, Meniere's disease, "
                 "balance disorders, and how we hear.",
                 f"A work of the National Institutes of Health (public domain). {NOTE}",
                 units=[(r"aids|assistive|captions|telecomm", "Hearing aids and devices"),
                        (r"balance|menieres", "Balance"), (r".", "Hearing loss")]),
    M.pages_book(GROUP, "irs_deceased_person", "Taxes after someone dies (IRS)", "When someone dies: taxes",
                 "Internal Revenue Service (IRS), US Department of the Treasury",
                 ["https://www.irs.gov/individuals/deceased-person",
                  "https://www.irs.gov/individuals/file-the-final-income-tax-returns-of-a-deceased-person",
                  "https://www.irs.gov/individuals/request-deceased-persons-information"],
                 r"^https://www\.irs\.gov/individuals/(deceased-person|file-the-final-income-tax-returns-of-a-"
                 r"deceased-person|request-deceased-persons-information)$",
                 "The IRS's pages for survivors and executors: what to do about a deceased person's taxes, filing the "
                 "final income tax returns (who files, which forms, refunds and payments due), and requesting a "
                 "deceased person's tax information.",
                 f"A work of the Internal Revenue Service (public domain). {NOTE}"),
    K.guide(GROUP, "va_burial_benefits", "Burial and memorial benefits for veterans (VA)", "When someone dies: burial",
            "National Cemetery Administration, US Department of Veterans Affairs",
            ["https://www.cem.va.gov/burial-memorial-benefits/Veterans.asp", "https://www.va.gov/burials-memorials/"],
            r"^https://www\.(cem\.va\.gov/burial-memorial-benefits/(?!index)[A-Za-z_-]+\.asp|va\.gov/"
            r"burials-memorials(/[a-z0-9-]+){0,2}/?)$",
            "The VA's burial and memorial benefits, every page: burial in a VA national cemetery, eligibility, "
            "planning ahead (pre-need eligibility), headstones, markers and medallions, burial flags, Presidential "
            "Memorial Certificates, burial allowances (help with funeral costs), and what funeral directors and "
            "families need to do.",
            f"A work of the US Department of Veterans Affairs (public domain). {NOTE} To schedule a burial: the "
            f"National Cemetery Scheduling Office, 1-800-535-1117.", depth=1, limit=60, content=M.VA_CONTENT),
    M.pages_book(GROUP, "doj_elder_justice", "Elder abuse, scams and getting help (Justice Department Elder Justice "
                 "Initiative)", "Elder abuse", "Elder Justice Initiative, US Department of Justice",
                 [EJI + p for p in ("about-elder-abuse", "physical-abuse", "psychological-abuse",
                                    "financial-exploitation", "neglect-abandonment", "sexual-abuse",
                                    "red-flags-elder-abuse", "senior-scam-alert", "guardianship", "victim-services",
                                    "find-help-or-report-abuse")],
                 r"^https://www\.justice\.gov/elderjustice/[a-z0-9-]+$",
                 "The Elder Justice Initiative's pages for older people and families, each whole: what elder abuse "
                 "is and its kinds (physical, psychological, financial exploitation, neglect and abandonment, sexual "
                 "abuse), the red flags, current scams against older people, guardianship, help for victims, and how "
                 "to find help or report abuse (Adult Protective Services, the National Elder Fraud Hotline).",
                 f"A work of the US Department of Justice (public domain). {NOTE}"),
]

COLLECTION = K.Collection("aging", GROUP, guides=GUIDES,
                          makers={"help_lines": (help_book, lambda name: datetime.date.today().strftime("%Y-%m"))},
                          words={"aging-end-of-life": lambda: [f"aging:{g['name']}" for g in GUIDES] +
                                 ["aging:help_lines"]})

LICENCE_LINES = {
    "aging_us_gov": "acl.gov, www.va.gov, www.cem.va.gov, www.nidcd.nih.gov, www.irs.gov and www.justice.gov: works "
                    "of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build); "
                    "robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "aging_nci": "NCI's reuse policy (as mind_nci), checked at every build; credit to NCI in the notice.",
}
NOT_INCLUDED = [
    ("National Institute on Aging and its Alzheimer's and related Dementias Education and Referral (ADEAR) Center: "
     "advance care planning, end of life, caregiving, memory, falls, hearing, Medicare and long-term care guides",
     "Public domain, but www.nia.nih.gov and www.alzheimers.gov answer programs with a bot check (\"405 Human "
     "Verification\"; checked again 2026-11-22), and the Internet Archive holds none of the current booklets. "
     "Link-only. Index: https://www.nia.nih.gov/health/advance-care-planning and https://www.alzheimers.gov/"),
    ("Organ donation (organdonor.gov, HRSA)", "Public domain, but www.organdonor.gov refuses programs (\"Access "
     "Denied\" even for robots.txt; checked 2026-11-22). Link-only. Index: https://www.organdonor.gov/learn/process"),
    ("Social Security survivors benefits and what to do when someone dies (ssa.gov)", "Public domain, but www.ssa.gov "
     "refuses programs (\"Access Denied\" even for robots.txt; checked 2026-11-22). SSA's own rules are the POMS "
     "(ben:poms) and USA.gov's death benefits pages are help:usa_gov. Link-only. Index: https://www.ssa.gov/survivor"),
    ("FTC consumer pages on funerals, wills and estate scams (consumer.ftc.gov)", "Public domain, but "
     "consumer.ftc.gov answers programs \"403\" (\"The request resembles an abusive automated request\"; checked "
     "2026-11-22). The Funeral Rule itself is law:cfr_16_453_funeral_rule. Link-only. Index: "
     "https://consumer.ftc.gov/articles/shopping-funeral-services"),
    ("State advance directive, living will and health care proxy forms", "Each state's own form; state government "
     "works are not all free of copyright, and many states' forms come from their bar associations or hospital "
     "associations under their own terms, so none is copied. Ask the state attorney general's office, the local Area "
     "Agency on Aging, or a hospital. The VA's own form (VA Form 10-0137) is explained in aging:va_geriatrics. Index: "
     "https://acl.gov/ltc/legal-steps/advance-care-plan-considerations and https://www.va.gov/find-forms/about-form-"
     "10-0137/"),
    ("Wills, trusts and estate planning guides", "No current US government consumer guide on writing a will was "
     "found that the builder may read (the FTC's refuses programs; state court self-help pages carry their own "
     "terms). ACL's legal steps pages (aging:acl_long_term_care) and the CFPB's guides are built. Link-only. Index: "
     "https://www.usa.gov/estate-planning"),
    ("AARP, the Alzheimer's Association, CaringInfo (NHPCO), Five Wishes, PREPARE for Your Care and Nolo",
     "Copyright, not openly licensed (checked 2026-11-22). Link-only. Index: https://www.aarp.org/caregiving/ , "
     "https://www.alz.org/ and https://www.caringinfo.org/"),
    ("Medicaid.gov long-term services and supports pages", "Written for state programmes rather than families "
     "(waivers, grants, reports); ACL's long-term care guide explains Medicaid for families instead. Index: "
     "https://www.medicaid.gov/medicaid/long-term-services-supports"),
    ("National Center on Elder Abuse (ncea.acl.gov)", "The site did not answer (no connection, 2026-11-22); the "
     "Justice Department's Elder Justice Initiative pages are built. Link-only. Index: https://ncea.acl.gov/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
