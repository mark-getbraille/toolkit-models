"""Midwifery, birth and postpartum care for the reference library, in the group "Reference, home health care and
first aid" (the owner's request of 2026-11-22). Keys: midwifery (every book), birth:<name>.

What already exists and is NOT repeated (textbooks/parenting.py, early_childhood.py, family_health.py): the Office on
Women's Health pregnancy and breastfeeding guides, CDC's pregnancy, vaccines in pregnancy and infant feeding pages,
WIC and WIC Breastfeeding Support, the NHS's pregnancy and baby guides (labour and birth, caring for a newborn,
feeding, crying, sleep), NICHD's Safe to Sleep and CDC's child passenger safety pages. This module adds, each IN
FULL from the publisher's own site:
  - CDC's Hear Her campaign: the urgent maternal warning signs during and after pregnancy (headache that will not go
    away, dizziness, vision changes, fever, extreme swelling, thoughts of harming yourself or the baby, trouble
    breathing, chest pain or fast heartbeat, severe belly pain, severe nausea, the baby moving less, bleeding or
    leaking fluid, swelling or pain in a leg, overwhelming tiredness), and what to say to a doctor, kept whole;
  - CDC's maternal and infant health pages (postpartum depression, pregnancy complications, preterm birth, maternal
    deaths and their prevention, safe sleep and sudden infant death), kept whole;
  - the NHS's pages on pre-eclampsia, mastitis, jaundice in newborn babies, postnatal depression and postpartum
    psychosis, with the non-US note;
  - the civil defence guide "Emergency Childbirth" is in first_aid.py (firstaid:emergency_childbirth_self_help).

Every book starts with the birth note: call 911 (or your local emergency number) for heavy bleeding, chest pain,
trouble breathing, a seizure or thoughts of harming yourself or the baby; the National Maternal Mental Health Hotline
is 1-833-852-6262 (call or text) and 988 is the Suicide and Crisis Lifeline; general information, not medical advice
or a diagnosis; ask your midwife or doctor.

The official positions on planned home birth differ: the American College of Obstetricians and Gynecologists says
hospitals and accredited birth centres are the safest settings while respecting a woman's right to decide, the
American College of Nurse-Midwives supports home birth for healthy women with low-risk pregnancies attended by a
qualified midwife, and NICE (UK) advises that home or a midwife-led unit is suitable for many low-risk women. Their
documents are copyright (link-only, in NOT_INCLUDED); this library presents them side by side without taking sides.

Licences: CDC's terms with their conditions in the notice; the NHS's Open Government Licence v3.0.

Run from the repository's folder:
  python3 textbooks/midwifery.py birth:cdc_hear_her --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import first_aid as F  # noqa: E402 - the helpers of the home health modules

GROUP = F.GROUP
NOTE = ("Call 911 (or your local emergency number) for heavy bleeding, chest pain, trouble breathing, a seizure, or "
        "thoughts of harming yourself or your baby. The National Maternal Mental Health Hotline is 1-833-852-6262 "
        "(call or text, any time) and 988 is the Suicide and Crisis Lifeline. This is general information, not "
        "medical advice or a diagnosis: ask your midwife or doctor.")

GUIDES = [
    F.cdc_book(GROUP, "cdc_hear_her", "Hear Her: urgent maternal warning signs (CDC)", "Pregnancy and after the "
               "birth", ["hearher"],
               "CDC's Hear Her campaign, every page: the urgent warning signs during pregnancy and in the year "
               "after birth that need medical care right away, what to say to a doctor or nurse, and the stories "
               "of women who lived through pregnancy complications; for pregnant and postpartum women, their "
               "partners, families and friends.", units=[(r".", "Hear Her")], note=NOTE),
    F.cdc_book(GROUP, "cdc_maternal_infant_health", "Maternal and infant health: postpartum depression, "
               "complications and safe sleep (CDC)", "Pregnancy and after the birth", ["maternal-infant-health"],
               "CDC's maternal and infant health pages, every page: depression during and after pregnancy, "
               "pregnancy complications, high blood pressure in pregnancy, preterm birth, preventing maternal "
               "deaths, and sudden unexpected infant death and safe sleep.", units=[(r".", "Maternal and infant "
                                                                                        "health")], note=NOTE),
    F.nhs_book(GROUP, "nhs_after_birth", "Pre-eclampsia, mastitis, newborn jaundice and postnatal mental health "
               "(NHS)", "After the birth (UK)",
               ["conditions/pre-eclampsia", "conditions/mastitis", "conditions/jaundice-in-babies",
                "mental-health/conditions/postnatal-depression", "mental-health/conditions/post-partum-psychosis"],
               "The NHS's pages, each whole: pre-eclampsia (its warning signs during and after pregnancy), mastitis "
               "(breast pain and infection while breastfeeding, and what helps), jaundice in newborn babies (the "
               "signs and when to call), postnatal depression (baby blues, symptoms, getting help) and postpartum "
               "psychosis (a medical emergency: its warning signs).", note=NOTE),
]

COLLECTION = K.Collection("birth", GROUP, guides=GUIDES,
                          words={"midwifery": lambda: [f"birth:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "birth_cdc_nhs": "CDC's \"Use of Agency Materials\" and the NHS's terms (Open Government Licence v3.0), both "
                     "checked at every build, as in first_aid.py; robots.txt of www.cdc.gov and www.nhs.uk allows "
                     "the pages; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("ACOG, ACNM, MANA and AWHONN position statements and patient pages (planned home birth, midwifery care)",
     "Copyright of each college or association (checked 2026-11-22). Link-only, side by side: ACOG Committee "
     "Opinion 697 \"Planned Home Birth\", ACNM's position statement on planned home birth, MANA's core competencies. "
     "Index: https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2017/04/planned-home-birth , "
     "https://www.midwife.org/position-statements and https://mana.org/"),
    ("NICE guideline NG235, Intrapartum care (UK)", "NICE's content may be read and printed for personal use, but "
     "reuse needs a licence (its terms, checked 2026-11-22). Link-only. Index: "
     "https://www.nice.org.uk/guidance/ng235"),
    ("WHO recommendations on intrapartum and postnatal care", "Mostly CC BY-NC-SA (personal use), and www.who.int's "
     "robots.txt shuts out AI companies' readers (checked 2026-11-22). Link-only. Index: "
     "https://www.who.int/publications/i/item/9789240045989"),
    ("Hesperian: A Book for Midwives and Where Women Have No Doctor", "Free for non-commercial use (personal use "
     "only), but hesperian.org offers no PDF address a program can find (checked 2026-11-22). Link-only. Index: "
     "https://hesperian.org/"),
    ("Global Health Media Project birth and newborn care videos", "Free to use for education with credit, but "
     "videos (no text to read) and their terms forbid changes. Link-only. Index: https://globalhealthmedia.org/"),
    ("State midwifery licensing pages", "Each state's health or licensing board publishes its own rules; they "
     "change often and are linked from the Big Push for Midwives and MANA maps (copyright). Link-only. Index: "
     "https://www.pushformidwives.org/"),
    ("HRSA Maternal and Child Health pages", "Public domain, but www.hrsa.gov refuses programs (checked "
     "2026-11-22). Link-only. Index: https://mchb.hrsa.gov/"),
    ("OpenStax Maternal-Newborn Nursing", "Its source is not published on GitHub (OpenStax's public nursing bundle, "
     "nursing-external-bundle, already in the library, holds only Pharmacology, Nutrition and Population Health; "
     "checked 2026-11-22), and openstax.org's reader is a JavaScript application. Link-only. Index: "
     "https://openstax.org/subjects/nursing"),
    ("ACOG, Mayo Clinic, BabyCenter and What to Expect pages", "Copyright (checked 2026-11-22). Link-only. Index: "
     "https://www.acog.org/womens-health and https://www.whattoexpect.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
