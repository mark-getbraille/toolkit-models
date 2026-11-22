"""Early childhood, pregnancy, newborn care and infant feeding for the reference library, in the group "Reference,
parenting and family" (the owner's second parenting request of 2026-11-22). Keys: early-childhood (every book),
early:<name>.

What this module builds, in plain words, each IN FULL (every page, read from the publisher's own site):
  - ChildCare.gov (the Office of Child Care, Administration for Children and Families): the consumer guides to
    finding, choosing and paying for quality child care, how child care is regulated, and each state's child care
    resources;
  - the Office on Women's Health (womenshealth.gov): its pregnancy guide (getting pregnant, prenatal care, stages of
    pregnancy, labour and birth, recovering from birth) and its breastfeeding guide;
  - CDC's pregnancy pages, infant and toddler nutrition (breastfeeding, formula feeding, starting solid foods,
    vitamins and minerals, mealtimes) and the vaccines in pregnancy pages, kept whole with their text unchanged as
    CDC's terms ask;
  - WIC (USDA's Special Supplemental Nutrition Program for Women, Infants, and Children): its programme pages
    (who can get it, how to apply, the benefits) and the whole WIC Breastfeeding Support site;
  - the NHS's pregnancy and baby guides (nhs.uk, Open Government Licence), with the non-US note.

Not built (NOT_INCLUDED): the Administration for Children and Families' own site (acf.gov: the Office of Child
Care, Early Childhood Development and the home visiting pages answer programs with a bot check), HRSA's Healthy
Start, the home visiting programme (MIECHV) and Poison Help (hrsa.gov refuses programs), LactMed (the NCBI
Bookshelf answers programs with a reCAPTCHA page), NHTSA's car seat guides (refused), the NHS's Best Start in Life
site (its terms reserve all rights), March of Dimes, ASL University (Lifeprint) and the baby sign language
books (copyright); open early childhood education textbooks are already in the library through LibreTexts.

Licences: works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build); the
Office on Women's Health says "All material contained on these pages are free of copyright restrictions"; CDC's
terms as in parenting.py; the NHS's terms release its content under the Open Government Licence v3.0, and the
notice carries the attribution its terms ask for.

Run from the repository's folder:
  python3 textbooks/early_childhood.py early:childcare_gov --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parenting as P  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = P.GROUP
OWH_TERMS = "https://www.womenshealth.gov/about-us/disclaimers"
OWH_TEXT = r"All material contained on these pages are free of copyright restrictions"
NHS_TERMS = "https://www.nhs.uk/our-policies/terms-and-conditions/"
NHS_TEXT = r"released free-of-charge under the current version of the Open Government Licence"
OGL_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
NOT_MEDICAL = "Health information, not medical advice: talk with your doctor, midwife or nurse."

GUIDES = [
    K.guide(GROUP, "childcare_gov", "Finding and choosing child care (ChildCare.gov)", "Child care",
            "Office of Child Care, Administration for Children and Families, US Department of Health and Human "
            "Services (ChildCare.gov)", "https://www.childcare.gov/consumer-education",
            r"^https://www\.childcare\.gov/(consumer-education(/[a-z0-9-]+)*|state-resources/[a-z-]+|"
            r"report-child-abuse-neglect|health-and-safety-reporting)$",
            "ChildCare.gov's consumer guides, every page: what your child care options are, how to find and choose "
            "quality child care (visiting, questions to ask, checking a provider's licence and inspection reports), "
            "how child care is regulated, paying for child care and help with its cost, partnering with your "
            "provider, supporting your child's health and development, and each state's and territory's child care "
            "resources (licensing offices, help paying, finding care).",
            "A work of the US Department of Health and Human Services (public domain).", depth=2,
            follow=r"^https://www\.childcare\.gov/consumer-education(/[a-z0-9-]+)?$",
            units=[(r"/state-resources/", "State resources"), (r".", "Choosing child care")], limit=150),
    dict(K.guide(GROUP, "owh_pregnancy_breastfeeding", "Pregnancy and breastfeeding (Office on Women's Health)",
                 "Pregnancy and breastfeeding", "Office on Women's Health, US Department of Health and Human Services",
                 ["https://www.womenshealth.gov/pregnancy", "https://www.womenshealth.gov/breastfeeding"],
                 r"^https://www\.womenshealth\.gov/(pregnancy|breastfeeding)(/[a-z0-9-]+)*$",
                 "The Office on Women's Health's pregnancy guide (before you get pregnant, prenatal care and tests, "
                 "stages of pregnancy, staying healthy and safe, getting ready for the baby, labour and birth, "
                 "recovering from birth) and its breastfeeding guide (learning to breastfeed, common challenges, "
                 "breastfeeding and going back to work, pumping and storing milk, breastfeeding in public), every "
                 "page.", "From the Office on Women's Health (womenshealth.gov): \"All material contained on these "
                 "pages are free of copyright restrictions\". " + NOT_MEDICAL + " The OWH Helpline: 1-800-994-9662.",
                 depth=3, follow=r"^https://www\.womenshealth\.gov/(pregnancy|breastfeeding)(/[a-z0-9-]+)?$",
                 units=[(r"/breastfeeding", "Breastfeeding"), (r".", "Pregnancy")], limit=200),
         licence_page=OWH_TERMS, licence_text=OWH_TEXT),
    P.cdc_book("cdc_pregnancy_infant_feeding", "Healthy pregnancy, vaccines in pregnancy and feeding babies and "
               "toddlers (CDC)", "Pregnancy and infant feeding",
               ["pregnancy", "vaccines-pregnancy", "infant-toddler-nutrition"],
               "CDC's pages on a healthy pregnancy (before, during and after pregnancy, what to avoid), on vaccines "
               "during pregnancy (flu, Tdap for whooping cough, COVID-19 and RSV), and on infant and toddler "
               "nutrition (breastfeeding and newborn basics, formula feeding and preparing formula safely, when, what "
               "and how to introduce solid foods, foods and drinks to limit, vitamins and minerals, mealtime "
               "routines), every page.",
               units=[(r"/pregnancy/", "Healthy pregnancy"), (r"/vaccines-pregnancy/", "Vaccines in pregnancy"),
                      (r".", "Feeding babies and toddlers")]),
    K.guide(GROUP, "wic_breastfeeding", "WIC and WIC Breastfeeding Support (USDA)", "WIC and breastfeeding",
            "US Department of Agriculture, Food and Nutrition Administration (formerly Food and Nutrition Service)",
            ["https://www.fna.usda.gov/wic", "https://wicbreastfeeding.fna.usda.gov/site-map"],
            r"^https://(www\.fna\.usda\.gov/wic(/[a-z0-9-]+)*|wicbreastfeeding\.fna\.usda\.gov/(?!site-map|"
            r"social-media|quiz-index|homepage|wic-staff|wic-partners)[a-z0-9-]+)$",
            "WIC's programme pages (who is eligible, how to apply, the foods and benefits, breastfeeding support and "
            "nutrition education) and every page of WIC Breastfeeding Support: breastfeeding basics and benefits, "
            "a good latch, the first days and weeks, low milk supply, expressing and pumping milk, going back to "
            "work or school, and pages for dads, grandparents, friends and family.",
            "A work of the US Department of Agriculture (public domain). USDA is an equal opportunity provider, "
            "employer and lender.", depth=1, units=[(r"wicbreastfeeding", "WIC Breastfeeding Support"),
                                                   (r".", "WIC")], limit=120),
    dict(K.guide(GROUP, "nhs_pregnancy_baby", "Pregnancy and baby guides (NHS)", "Pregnancy and baby care",
                 "NHS England (nhs.uk)", ["https://www.nhs.uk/pregnancy/", "https://www.nhs.uk/baby/"],
                 r"^https://www\.nhs\.uk/(pregnancy|baby)(/[a-z0-9-]+)*/$",
                 "The NHS's pregnancy guide (trying for a baby, finding out, your antenatal care, keeping well, "
                 "common symptoms, complications, labour and birth, mental health) and its baby guide (caring for a "
                 "newborn, breastfeeding and bottle feeding, weaning, sleep, crying, health and development, "
                 "safety), every page.",
                 "Information from the NHS website is licensed under the Open Government Licence v3.0; contains public "
                 "sector information licensed under the Open Government Licence v3.0. A UK source: the NHS services, "
                 "phone numbers and rules it names are those of England; in the US, ask your own doctor.",
                 depth=2, follow=r"^https://www\.nhs\.uk/(pregnancy|baby)/[a-z0-9-]+/$",
                 units=[(r"/baby/", "Baby"), (r".", "Pregnancy")], limit=400, country="United Kingdom"),
         licence="OGL-UK-3.0", licence_url=OGL_URL, licence_page=NHS_TERMS, licence_text=NHS_TEXT),
]

COLLECTION = K.Collection("early", GROUP, guides=GUIDES,
                          words={"early-childhood": lambda: [f"early:{g['name']}" for g in GUIDES]})

GROUPS = {}
# Where a UK book's practice differs (sources.PRACTICE_SUBJECTS; first match wins, so only these subjects' words).
PRACTICE_SUBJECTS = [
    (r"pregnancy and baby care|parenting \(canada\)", "health services and how to reach them (the NHS or provincial "
     "health care, not US insurance), vaccine schedules, car seat and product safety rules, parental leave and "
     "benefits, and spelling"),
]
LICENCE_LINES = {
    "early_childcare_wic": "childcare.gov, fna.usda.gov and wicbreastfeeding.fna.usda.gov: works of the US government "
                           "(17 U.S.C. 105, checked on govinfo.gov's policies page at every build); robots.txt allows "
                           "the pages; no AI rules (checked 2026-11-22).",
    "early_owh": "womenshealth.gov/about-us/disclaimers (checked at every build): \"All material contained on these "
                 "pages are free of copyright restrictions and may be copied, reproduced, or duplicated without "
                 "permission of the Office on Women's Health\"; robots.txt allows the pages; no AI rules.",
    "early_nhs": "nhs.uk/our-policies/terms-and-conditions (checked at every build): \"Copyright and database rights in "
                 "NHS Website Content are released free-of-charge under the current version of the Open Government "
                 "Licence\"; the notice carries the attribution the terms ask for, and the weekly check reads the "
                 "pages again (the terms ask for content refreshed at least every 7 days, or the standard OGL "
                 "attribution, which the notice gives). robots.txt allows /pregnancy/ and /baby/; no AI rules.",
}
NOT_INCLUDED = [
    ("Administration for Children and Families: Office of Child Care, Early Childhood Development and home visiting "
     "(acf.gov)", "Public domain, but acf.gov (and acf.hhs.gov) answers programs with a bot check (an empty \"202\" "
     "page from its firewall, checked 2026-11-22). ChildCare.gov, the Office of Child Care's consumer site, is built "
     "(early:childcare_gov). Link-only. Index: https://acf.gov/ecd and https://acf.gov/occ"),
    ("HRSA Healthy Start and the Maternal, Infant, and Early Childhood Home Visiting programme (mchb.hrsa.gov)",
     "Public domain, but mchb.hrsa.gov answers programs \"403 Forbidden\" (robots.txt included, checked 2026-11-22). "
     "Link-only. Index: https://mchb.hrsa.gov/programs-impact/healthy-start and "
     "https://mchb.hrsa.gov/programs-impact/programs/home-visiting"),
    ("Poison Help (HRSA, poisonhelp.hrsa.gov)", "Public domain, but poisonhelp.hrsa.gov answers programs \"403 "
     "Forbidden\" again (robots.txt included, checked 2026-11-22). Call Poison Help: 1-800-222-1222. Link-only. "
     "Index: https://poisonhelp.hrsa.gov/"),
    ("LactMed (Drugs and Lactation Database, NCBI Bookshelf)", "Public domain (National Library of Medicine), but "
     "www.ncbi.nlm.nih.gov answers programs with a reCAPTCHA \"Checking your browser\" page (checked again "
     "2026-11-22); NLM's bulk LactMed download is on the same Bookshelf. Link-only. Index: "
     "https://www.ncbi.nlm.nih.gov/books/NBK501922/"),
    ("NHTSA car seat guides (Parents Central, nhtsa.gov)", "Public domain, but www.nhtsa.gov refuses programs (403, "
     "as before; see also family_health). CDC's child passenger safety pages are built (parent:cdc_child_safety). "
     "Link-only. Index: https://www.nhtsa.gov/vehicle-safety/car-seats-and-booster-seats"),
    ("NHS Best Start in Life (formerly Start for Life, nhs.uk/best-start-in-life)", "Not under the Open Government "
     "Licence: its own terms (run by the Department of Health and Social Care) say \"All such rights are reserved\" "
     "and allow one printed copy for personal use (checked 2026-11-22). The NHS's own pregnancy and baby guides are "
     "built instead (early:nhs_pregnancy_baby). Link-only. Index: https://www.nhs.uk/best-start-in-life/"),
    ("March of Dimes pregnancy and newborn guides", "Copyright of March of Dimes; not openly licensed. Link-only. "
     "Index: https://www.marchofdimes.org/find-support/topics"),
    ("Baby sign language: ASL University (Lifeprint) and baby sign books", "Lifeprint's lessons are \"© Dr. William "
     "Vicars\" (copyright, free to view only); the Internet Archive's baby sign language books are in copyright "
     "(lending only), and no openly licensed baby sign guide was found (checked 2026-11-22). NIDCD's American Sign "
     "Language fact sheet is in the library's NIDCD book. Link-only. Index: https://www.lifeprint.com/"),
    ("Open early childhood education textbooks (LibreTexts ECE, College of the Canyons, Open Textbook Library)",
     "Already in the library: LibreTexts' early childhood and child development books (Child Growth and "
     "Development, Infant and Toddler Care and Development, Observation and Assessment in Early Childhood "
     "Education, Child, Family, and Community, Introduction to Curriculum for Early Childhood Education, Children "
     "with Differing Abilities and others, many first written at College of the Canyons) are built from the "
     "LibreTexts catalogue (course:libretexts:socialsci-0 to -5; non-commercial ones as personal use); the Open "
     "Textbook Library snapshot holds no further early childhood title, and OpenStax Lifespan Development is "
     "built (osbooks:lifespan-development). Index: https://commons.libretexts.org/ and "
     "https://open.umn.edu/opentextbooks/subjects/education"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
