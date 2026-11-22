"""Home treatment of common illnesses, wound and skin care, managing long-term conditions at home, and home nursing
and caregiving, for the reference library, in the group "Reference, home health care and first aid" (the owner's
request of 2026-11-22). Keys: home-health (every book), homecare:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the NHS's pages on common illnesses and what to do at home, with when to get help (colds, flu, COVID-19, fever in
    children, sore throats, earache, coughs, diarrhoea and vomiting, dehydration, constipation, heartburn, headaches
    and migraine, back pain, rashes, eczema, sunburn, head lice, scabies, athlete's foot, warts, cold sores,
    conjunctivitis, styes, hiccups, motion sickness, urinary tract infections, thrush, period pain, hay fever and
    allergies, insomnia, panic and anxiety), and on wounds and skin (blisters, ingrown toenails, cellulitis, Lyme
    disease), with the non-US note;
  - CDC's pages on common illnesses and staying well at home: antibiotics and the illnesses they do not help (colds,
    sore throats, ear and sinus infections), flu, COVID-19, norovirus (stomach bugs), pink eye, head lice, scabies,
    and clean hands, kept whole as CDC's terms ask;
  - CDC's pages on long-term conditions: diabetes, asthma, COPD, high blood pressure, cholesterol, arthritis and
    kidney disease, kept whole;
  - NIDDK's health information on diabetes (checking blood sugar, insulin, foot care, low blood sugar), kidney disease
    (diet basics) and digestive diseases (constipation, acid reflux, diarrhoea), every page;
  - NHLBI's pages on heart attack, high blood pressure (home monitoring), heart failure, asthma and COPD;
  - the NHS's pages on diabetes, high blood pressure and other long-term conditions, with the non-US note;
  - caring for someone at home: CDC's caregiving, falls prevention (older adults) and Alzheimer's and dementia pages,
    and the VA Caregiver Support Program's pages (tips and tools, caring by diagnosis, self-care for caregivers).
  (MedlinePlus's health topic summaries are mlp:health_topics, NIMH's brochures fam:nimh_publications and the crisis
  lines fam:crisis_lines: not repeated. Medicines' own labels are the med: books.)

Every book starts with the emergency note: call 911 (or your local emergency number) in an emergency; Poison Help
1-800-222-1222 (US); general information, not medical advice or a diagnosis; ask a doctor, nurse or pharmacist.
Medicine doses are only those the official source states.

Not built (NOT_INCLUDED): AHRQ (its robots.txt shuts out AI readers), the National Institute on Aging and NIAMS
(refuse programs), the NIH Clinical Center's patient education (no licence line found), the Merck Manual and Mayo
Clinic (copyright), OpenStax nursing books (already reached through course:openstax where their licence allows).

Licences: as first_aid.py (CDC's terms with their conditions, US government works, the NHS's Open Government
Licence v3.0), and the VA's pages: works of the US government.

Run from the repository's folder:
  python3 textbooks/home_health.py homecare:nhs_common_illnesses --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import first_aid as F  # noqa: E402 - the helpers and notes of the home health modules

GROUP = F.GROUP
NOTE = F.EMERGENCY

GUIDES = [
    F.nhs_book(GROUP, "nhs_common_illnesses", "Common illnesses and what to do at home (NHS)", "Home treatment (UK)",
               ["conditions/common-cold", "conditions/flu", "conditions/covid-19", "symptoms/fever-in-children",
                "symptoms/sore-throat", "symptoms/earache", "symptoms/cough", "symptoms/diarrhoea-and-vomiting",
                "conditions/dehydration", "conditions/constipation", "conditions/heartburn-and-acid-reflux",
                "symptoms/headaches", "conditions/migraine", "conditions/back-pain",
                "symptoms/rashes-babies-and-children", "conditions/atopic-eczema", "conditions/sunburn",
                "conditions/head-lice-and-nits", "conditions/scabies", "conditions/athletes-foot",
                "conditions/warts-and-verrucas", "conditions/cold-sores", "conditions/conjunctivitis",
                "conditions/stye", "symptoms/hiccups", "conditions/motion-sickness",
                "conditions/urinary-tract-infections-utis", "conditions/thrush-in-men-and-women",
                "symptoms/period-pain", "conditions/hay-fever", "conditions/allergies", "conditions/insomnia",
                "mental-health/conditions/panic-disorder", "mental-health/conditions/generalised-anxiety-disorder-gad",
                "conditions/blisters", "conditions/ingrown-toenail", "conditions/cellulitis",
                "conditions/lyme-disease"],
               "The NHS's pages on common illnesses, each whole: what each one is, how to look after yourself or "
               "your child at home, which pharmacy remedies can help, and when to get help (urgent signs to call 999 "
               "or 111, or 911 in the US): colds, flu, COVID-19, fever in children, sore throats, earache, coughs, "
               "diarrhoea and vomiting, dehydration, constipation, heartburn, headaches, migraine, back pain, rashes "
               "in children, eczema, sunburn, head lice, scabies, athlete's foot, warts, cold sores, conjunctivitis, "
               "styes, hiccups, motion sickness, urinary tract infections, thrush, period pain, hay fever and "
               "allergies, insomnia, panic disorder and anxiety; and the skin: blisters, ingrown toenails, "
               "cellulitis (a spreading skin infection) and Lyme disease (after a tick bite)."),
    F.cdc_book(GROUP, "cdc_common_illnesses", "Common illnesses, stomach bugs, lice and clean hands (CDC)",
               "Home treatment", ["antibiotic-use", "flu", "covid", "norovirus", "conjunctivitis", "lice", "scabies",
                                  "clean-hands"],
               "CDC's pages on common illnesses, every page: antibiotics and the common illnesses they do not help "
               "(colds, sore throats, ear and sinus infections, bronchitis) and how to feel better at home; flu and "
               "COVID-19 (symptoms, caring for someone sick at home, when to seek emergency care); norovirus "
               "(vomiting and diarrhoea, preventing dehydration, cleaning up); pink eye; head lice and scabies; and "
               "hand washing and hand sanitiser.",
               units=[(r"/antibiotic-use/", "Common illnesses and antibiotics"), (r"/flu/", "Flu"),
                      (r"/covid/", "COVID-19"), (r"/norovirus/", "Stomach bugs (norovirus)"),
                      (r"/conjunctivitis/", "Pink eye"), (r"/lice/|/scabies/", "Lice and scabies"),
                      (r".", "Clean hands")], limit=500),
    F.cdc_book(GROUP, "cdc_long_term_conditions", "Diabetes, asthma, COPD, blood pressure, arthritis and kidney "
               "disease (CDC)", "Long-term conditions", ["diabetes", "asthma", "copd", "high-blood-pressure",
                                                         "cholesterol", "arthritis", "kidney-disease"],
               "CDC's pages on living with long-term conditions, every page: diabetes (managing blood sugar, low "
               "blood sugar, foot care, sick days, healthy eating), asthma (action plans, triggers, inhalers), COPD, "
               "high blood pressure and cholesterol (measuring at home, medicines, lowering them), arthritis "
               "(physical activity, managing pain) and chronic kidney disease.",
               units=[(r"/diabetes/", "Diabetes"), (r"/asthma/", "Asthma"), (r"/copd/", "COPD"),
                      (r"/high-blood-pressure/|/cholesterol/", "Blood pressure and cholesterol"),
                      (r"/arthritis/", "Arthritis"), (r".", "Kidney disease")], limit=600),
    K.guide(GROUP, "niddk_diabetes_kidney_digestive", "Diabetes, kidney disease and digestive problems (NIDDK)",
            "Long-term conditions", "National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), "
            "National Institutes of Health",
            ["https://www.niddk.nih.gov/health-information/diabetes",
             "https://www.niddk.nih.gov/health-information/kidney-disease",
             "https://www.niddk.nih.gov/health-information/digestive-diseases"],
            r"^https://www\.niddk\.nih\.gov/health-information/(diabetes|kidney-disease|digestive-diseases)"
            r"(/[a-z0-9-]+){0,3}$",
            "NIDDK's health information, every page: diabetes (types, managing it, checking blood sugar, insulin "
            "and other medicines, low blood sugar, preventing problems with the feet, eyes, kidneys and heart, "
            "eating and physical activity), kidney disease (chronic kidney disease, eating right, dialysis, kidney "
            "stones) and digestive diseases (constipation, diarrhoea, acid reflux and heartburn, irritable bowel "
            "syndrome, haemorrhoids, gas, and others).",
            NOTE + " A work of the National Institutes of Health (public domain).", depth=2,
            follow=r"^https://www\.niddk\.nih\.gov/health-information/(diabetes|kidney-disease|digestive-diseases)"
                   r"(/[a-z0-9-]+)?$",
            units=[(r"/diabetes", "Diabetes"), (r"/kidney-disease", "Kidney disease"), (r".", "Digestive problems")],
            limit=600),
    K.guide(GROUP, "nhlbi_heart_lungs", "Heart attack, high blood pressure, heart failure, asthma and COPD (NHLBI)",
            "Long-term conditions", "National Heart, Lung, and Blood Institute (NHLBI), National Institutes of Health",
            [f"https://www.nhlbi.nih.gov/health/{t}" for t in ("heart-attack", "high-blood-pressure",
                                                                "heart-failure", "asthma", "copd")],
            r"^https://www\.nhlbi\.nih\.gov/health/(heart-attack|high-blood-pressure|heart-failure|asthma|copd)"
            r"(/[a-z0-9-]+)?$",
            "NHLBI's pages on five heart and lung conditions, every page of each (what it is, causes and risk "
            "factors, symptoms, diagnosis, treatment, living with it and recovery): heart attack, high blood "
            "pressure (checking it at home), heart failure (daily weights, salt and fluids), asthma (an action "
            "plan, inhalers and peak flow) and COPD (inhalers, oxygen therapy and its safety).",
            NOTE + " A work of the National Institutes of Health (public domain).", depth=1,
            units=[(r"/heart-attack", "Heart attack"), (r"/high-blood-pressure", "High blood pressure"),
                   (r"/heart-failure", "Heart failure"), (r"/asthma", "Asthma"), (r".", "COPD")], limit=80),
    F.nhs_book(GROUP, "nhs_long_term_conditions", "Diabetes, blood pressure, COPD, heart failure, arthritis, kidney "
               "disease and stomas (NHS)",
               "Long-term conditions (UK)",
               ["conditions/diabetes", "conditions/type-2-diabetes", "conditions/high-blood-pressure",
                "conditions/chronic-obstructive-pulmonary-disease-copd", "conditions/heart-failure",
                "conditions/arthritis", "conditions/osteoarthritis", "conditions/kidney-disease",
                "tests-and-treatments/colostomy", "tests-and-treatments/ileostomy"],
               "The NHS's pages on long-term conditions, each whole: diabetes and type 2 diabetes (symptoms, living "
               "with it, food, checking blood sugar, foot care), high blood pressure (checking it, lowering it, its "
               "medicines), COPD, heart failure, arthritis and osteoarthritis, kidney disease, and living with a "
               "colostomy or an ileostomy (stoma care, bags, diet)."),
    F.cdc_book(GROUP, "cdc_caregiving_older_adults", "Caregiving, falls prevention and dementia (CDC)",
               "Home nursing and caregiving", ["caregiving", "falls", "alzheimers-dementia"],
               "CDC's pages for caregivers and older adults, every page: caregiving (caring for yourself as a "
               "caregiver, resources), preventing falls (what causes them, making the home safer, exercise, "
               "medicines that raise the risk, STEADI materials for older adults) and Alzheimer's disease and "
               "dementia (the warning signs, caring for someone with dementia).",
               units=[(r"/falls/", "Preventing falls"), (r"/alzheimers-dementia/", "Alzheimer's and dementia"),
                      (r".", "Caregiving")]),
    K.guide(GROUP, "va_caregiver_support", "Caregiver Support: tips, tools and caring by diagnosis (VA)",
            "Home nursing and caregiving", "VA Caregiver Support Program, US Department of Veterans Affairs",
            ["https://www.caregiver.va.gov/CAREGIVER/Tips_Tools.asp",
             "https://www.caregiver.va.gov/CAREGIVER/Tips_by_Diagnosis/Index.asp"],
            r"^https://www\.caregiver\.va\.gov/CAREGIVER/(Tips_Tools|Self_Care_Activities|Care_Caregivers|"
            r"Care_Veterans|Emergency_Preparedness|Suicide_Prevention_Toolkit|Tips_by_Diagnosis/[A-Za-z_-]+|"
            r"Support_[A-Za-z_]+)\.asp$",
            "The VA Caregiver Support Program's pages for family caregivers, every page: tips and tools (managing "
            "medicines, daily care, keeping track of appointments), caring by diagnosis (ALS, Alzheimer's and "
            "dementia, diabetes, multiple sclerosis, Parkinson's, PTSD, traumatic brain injury), caring for "
            "yourself as a caregiver, emergency preparedness and suicide prevention.",
            NOTE + " A work of the US Department of Veterans Affairs (public domain). The VA Caregiver Support Line "
                   "is 1-855-260-3274.", depth=1,
            units=[(r"Tips_by_Diagnosis", "Caring by diagnosis"), (r".", "Caregiver tips and support")], limit=80),
]

COLLECTION = K.Collection("homecare", GROUP, guides=GUIDES,
                          words={"home-health": lambda: [f"homecare:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "homecare_nih_va": "www.niddk.nih.gov, www.nhlbi.nih.gov and www.caregiver.va.gov: works of the US government "
                       "(17 U.S.C. 105, checked on govinfo.gov's policies page at every build); robots.txt allows the "
                       "pages; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("AHRQ patient and consumer guides (ahrq.gov)", "Public domain, but www.ahrq.gov's robots.txt shuts out AI "
     "companies' readers (checked 2026-11-22). Link-only. Index: https://www.ahrq.gov/patients-consumers/index.html"),
    ("National Institute on Aging and NIAMS (arthritis, skin, bones) health information", "Public domain, but "
     "www.nia.nih.gov answers programs with a bot check (\"405\") and www.niams.nih.gov with \"403\" (checked "
     "2026-11-22). Link-only. Index: https://www.nia.nih.gov/health and https://www.niams.nih.gov/health-topics"),
    ("Merck Manual Consumer Version and Mayo Clinic's symptom and condition pages", "Copyright (checked "
     "2026-11-22). Link-only. Index: https://www.merckmanuals.com/home and https://www.mayoclinic.org/"),
    ("Home nursing, ostomy and catheter care guides", "No openly licensed or US government guide on ostomy and "
     "catheter care at home was found beyond the NHS and CDC pages built here (the United Ostomy Associations' and "
     "the makers' guides are copyright, checked 2026-11-22). Link-only. Index: https://www.ostomy.org/"),
    ("OpenStax and LibreTexts nursing books (fundamentals of nursing, clinical nursing skills)", "OpenStax's public "
     "nursing bundle (Pharmacology, Nutrition, Population Health) is already built (osbooks); its other nursing books' "
     "sources are not published on GitHub (checked 2026-11-22). LibreTexts' nursing shelf is reached through "
     "course:libretexts. Index: https://openstax.org/subjects/nursing"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
