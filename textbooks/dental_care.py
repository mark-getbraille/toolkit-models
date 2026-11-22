"""Dental care at home for the reference library, in the group "Reference, home health care and first aid" (the
owner's request of 2026-11-22). Keys: dental-care (every book), dental:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - NIDCR's health information (National Institute of Dental and Craniofacial Research): oral hygiene, tooth decay,
    gum disease, dry mouth, canker sores and fever blisters, teeth grinding (bruxism), fluoride, sealants, fillings,
    oral cancer, burning mouth, TMJ, diabetes and oral health, finding low-cost dental care, every page;
  - CDC's oral health and community water fluoridation pages (brushing, flossing, children's teeth and sealants,
    oral health in pregnancy, for older adults and with diabetes, tobacco), kept whole as CDC's terms ask;
  - the NHS's dental pages (toothache, gum disease, mouth ulcers, dental abscess, dry mouth, bad breath, wisdom tooth
    removal and its aftercare, tooth decay, jaw pain (TMD), teeth grinding and mouth cancer), with the non-US note;
  - "Oral Health in America: Advances and Challenges" (NIDCR, 2021), the national report on oral health, whole.
  (Children's teething and first teeth are in the parenting and NHS baby books already: early:nhs_pregnancy_baby.)

Every book starts with the dental note: for a knocked-out tooth, a swollen face or jaw, a fever with toothache, or
bleeding that will not stop, see a dentist today or go to the emergency room; call 911 if breathing or swallowing
is hard; general information, not a diagnosis; ask your dentist.

Not built (NOT_INCLUDED): the American Dental Association's MouthHealthy (copyright), Hesperian's "Where There Is No
Dentist" (non-commercial, no PDF address for programs), the Indian Health Service (refuses programs), HRSA's oral
health pages (refuses programs).

Licences: US government works (NIDCR; the report is NIH Publication No. 21-3375); CDC's terms with their conditions
in the notice; the NHS's Open Government Licence v3.0.

Run from the repository's folder:
  python3 textbooks/dental_care.py dental:nidcr_health_info --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import first_aid as F  # noqa: E402 - the helpers of the home health modules

GROUP = F.GROUP
NOTE = ("For a knocked-out tooth, a swollen face or jaw, a fever with toothache, or bleeding that will not stop, see "
        "a dentist today or go to the emergency room; call 911 (or your local emergency number) if breathing or "
        "swallowing is hard. This is general information, not a diagnosis: ask your dentist.")

GUIDES = [
    K.guide(GROUP, "nidcr_health_info", "Oral health information (NIDCR)", "Dental care",
            "National Institute of Dental and Craniofacial Research (NIDCR), National Institutes of Health",
            "https://www.nidcr.nih.gov/health-info",
            r"^https://www\.nidcr\.nih\.gov/health-info/(?!publications)[a-z0-9-]+(/[a-z0-9-]+){0,2}$",
            "NIDCR's health information, every page: keeping your mouth healthy (brushing, flossing, fluoride, "
            "sealants, fillings), tooth decay, gum disease, dry mouth, canker sores and cold sores (fever blisters), "
            "teeth grinding (bruxism), burning mouth, TMJ disorders, oral cancer, mouth problems during cancer "
            "treatment, diabetes and HIV and the mouth, opioids after dental surgery, and finding low-cost dental "
            "care.", NOTE + " A work of the National Institutes of Health (public domain).", depth=2,
            follow=r"^https://www\.nidcr\.nih\.gov/health-info/[a-z0-9-]+$", limit=200),
    F.cdc_book(GROUP, "cdc_oral_health", "Oral health and fluoride (CDC)", "Dental care",
               ["oral-health", "fluoridation"],
               "CDC's oral health pages and its community water fluoridation pages, every page: brushing and "
               "flossing, children's oral health and dental sealants, oral health in pregnancy, for older adults, "
               "with diabetes and for people who use tobacco, gum disease, cavities, and fluoride in water and "
               "toothpaste.", units=[(r"/fluoridation/", "Fluoride"), (r".", "Oral health")], note=NOTE),
    F.nhs_book(GROUP, "nhs_dental", "Toothache, gum disease, mouth ulcers and other dental problems (NHS)",
               "Dental care (UK)",
               ["symptoms/toothache", "conditions/gum-disease", "conditions/mouth-ulcers", "conditions/dental-abscess",
                "symptoms/dry-mouth", "symptoms/bad-breath", "tests-and-treatments/wisdom-tooth-removal",
                "conditions/tooth-decay", "conditions/temporomandibular-disorder-tmd", "symptoms/teeth-grinding",
                "conditions/mouth-cancer"],
               "The NHS's dental pages, each whole: toothache (what you can do yourself and when to see a dentist "
               "urgently), gum disease, mouth ulcers, dental abscesses, dry mouth, bad breath, wisdom tooth removal "
               "and recovering from it (including dry socket), tooth decay, jaw pain (temporomandibular disorder), "
               "teeth grinding, and the warning signs of mouth cancer.", note=NOTE),
]
PDFS = [
    K.us_pdf(GROUP, name="nidcr_oral_health_in_america", title="Oral Health in America: Advances and Challenges "
             "(NIDCR, 2021)", subject="Dental care", publisher="National Institute of Dental and Craniofacial "
             "Research, National Institutes of Health",
             pdf="https://www.nidcr.nih.gov/sites/default/files/2021-12/Oral-Health-in-America-Advances-and-"
                 "Challenges.pdf",
             page="https://www.nidcr.nih.gov/research/oralhealthinamerica", published="2021-12",
             version="NIH Publication No. 21-3375 (December 2021)",
             description="The national report on oral health, twenty years after the Surgeon General's report of "
                         "2000: oral health across life (children, adolescents, adults, older adults), its links "
                         "with diabetes, heart disease and pregnancy, tobacco and oral cancer, access to dental "
                         "care, and what has changed.", notice=NOTE + " A work of the National Institutes of Health "
                                                                      "(public domain)."),
]

COLLECTION = K.Collection("dental", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"dental-care": lambda: [f"dental:{g['name']}" for g in GUIDES + PDFS]})

GROUPS = {}
LICENCE_LINES = {
    "dental_nidcr": "www.nidcr.nih.gov: works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies "
                    "page at every build); robots.txt allows /health-info/ and /sites/default/files/; no AI rules "
                    "(checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("American Dental Association: MouthHealthy (mouthhealthy.org)", "\"© American Dental Association\": copyright "
     "(checked 2026-11-22). Link-only. Index: https://www.mouthhealthy.org/"),
    ("Hesperian: Where There Is No Dentist", "Free for non-commercial use (personal use only), but hesperian.org "
     "offers no PDF address a program can find (checked 2026-11-22). Link-only. Index: https://hesperian.org/"),
    ("Indian Health Service and HRSA oral health pages", "Public domain, but www.ihs.gov did not answer and "
     "www.hrsa.gov refuses programs (checked 2026-11-22). Link-only. Index: https://www.ihs.gov/doh/ and "
     "https://www.hrsa.gov/oral-health"),
    ("Surgeon General's report Oral Health in America (2000)", "Its PDF at the NIDCR is a scan in parts; the 2021 "
     "report that follows it is built (dental:nidcr_oral_health_in_america). Index: "
     "https://www.nidcr.nih.gov/research/data-statistics/surgeon-general"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
