"""Fitness and nutrition for the reference library, in its own group "Reference, fitness and nutrition" (the owner's
request of 2026-11-22). Keys: fitness-nutrition (every book), fit:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the Physical Activity Guidelines for Americans, 2nd edition (HHS, 2018), the whole PDF: how much activity
    adults, older adults, children, pregnant women and people with disabilities or chronic conditions need,
    aerobic, muscle-strengthening and balance activities, and staying safe;
  - Move Your Way (HHS's plain-language pages for the guidelines: getting active, the activity planner, kids);
  - the Dietary Guidelines for Americans, 2025-2030 (USDA and HHS), the whole PDF, with its daily serving sizes
    table (the guidelines' own site; the old MyPlate site could not be reached);
  - CDC's physical activity, nutrition and healthy weight pages (activity for adults and older adults, balance
    and strength, water and healthier drinks, losing weight and keeping it off), kept whole as CDC's terms ask;
  - CDC's sleep pages and NHLBI's sleep pages (how sleep works, sleep deprivation, insomnia, sleep apnoea), with
    NHLBI's DASH eating plan page (diets for high blood pressure; DASH menus are already a cookbook,
    cookbooks' nhlbi_week_on_dash);
  - NIDDK's weight management pages (healthy eating and physical activity for life, weight loss and its
    treatments; NIDDK's diabetes eating pages are already homecare:niddk_diabetes_kidney_digestive);
  - the Office on Women's Health's getting active, healthy eating and healthy weight pages.

Every book's notice ends with the fitness health note: general information, not medical advice or a diagnosis; ask
your doctor before a new exercise or eating plan if you have a health condition; in an emergency call 911; in a
mental health crisis call or text 988.

Not built (NOT_INCLUDED, link-only): MyPlate.gov (could not be reached), the National Institute on Aging's exercise
guide (bot check), NCHPAD, the US Association of Blind Athletes and IBSA (copyright, and USABA's robots.txt shuts
out AI readers), Go4Life (retired), and the makers' fitness equipment guides (the manual collection
fitness_equipment lists them as links).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's terms and the Office on Women's Health's disclaimer are checked at every build.

Run from the repository's folder:
  python3 textbooks/fitness_nutrition.py fit:cdc_sleep --out build/textbooks --limit 5
  python3 textbooks/fitness_nutrition.py --list fitness-nutrition
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared helpers and notes of the four new health modules

GROUP = "fitnessnutrition"
GROUPS = {GROUP: "Reference, fitness and nutrition"}
NOTE = ("General information, not medical advice or a diagnosis: if you have a health condition, ask your doctor "
        "before you start a new exercise or eating plan. In an emergency call 911; in a mental health crisis call or "
        "text 988.")

ODPHP = "https://odphp.health.gov"
REALFOOD = "https://www.realfood.gov"

GUIDES = [
    K.guide(GROUP, "odphp_move_your_way", "Move Your Way: getting active the easy way (HHS)", "Physical activity",
            "Office of Disease Prevention and Health Promotion (ODPHP), US Department of Health and Human Services",
            f"{ODPHP}/moveyourway", r"^https://odphp\.health\.gov/moveyourway(/[a-z0-9-]+){0,2}$",
            "HHS's Move Your Way pages, the plain-language version of the Physical Activity Guidelines: how much "
            "activity adults, older adults, kids and pregnant women need, ideas for getting active, the activity "
            "planner, and stories of people who found their move.",
            f"A work of the US Department of Health and Human Services (public domain). {NOTE}", depth=1,
            units=[(r"kids", "Kids"), (r"stories", "Stories"), (r".", "Getting active")], limit=40),
    M.cdc_book(GROUP, "cdc_activity_nutrition_weight", "Physical activity, nutrition and healthy weight (CDC)",
               "Physical activity and nutrition", ["physical-activity-basics", "nutrition", "healthy-weight-growth"],
               "CDC's pages on physical activity, nutrition and healthy weight, every page: how much activity adults, "
               "older adults and children need, aerobic, muscle-strengthening and balance activities, activity for "
               "people with disabilities and chronic conditions; healthy eating, water and healthier drinks, "
               "fruits and vegetables, sodium, added sugars, vitamins and minerals; healthy weight, body mass "
               "index, losing weight and keeping it off.",
               units=[(r"/physical-activity-basics/", "Physical activity"), (r"/nutrition/", "Nutrition"),
                      (r".", "Healthy weight")], note=NOTE, limit=400),
    M.cdc_book(GROUP, "cdc_sleep", "Sleep and sleep hygiene (CDC)", "Sleep", ["sleep"],
               "CDC's sleep pages, every page: how much sleep people need at each age, tips for better sleep (sleep "
               "hygiene), sleep and chronic disease, drowsy driving, and sleep disorders.",
               units=[(r".", "Sleep")], note=NOTE),
    K.guide(GROUP, "nhlbi_sleep_dash", "Sleep, sleep problems and the DASH eating plan (NHLBI)", "Sleep and diet",
            "National Heart, Lung, and Blood Institute (NHLBI), National Institutes of Health",
            [f"https://www.nhlbi.nih.gov/{p}" for p in ("health/sleep", "health/sleep-deprivation",
                                                        "health/insomnia", "health/sleep-apnea",
                                                        "education/dash-eating-plan")],
            r"^https://www\.nhlbi\.nih\.gov/(health/(sleep|sleep-deprivation|insomnia|sleep-apnea)(/[a-z0-9-]+)?|"
            r"education/dash-eating-plan)$",
            "NHLBI's pages on sleep, every page of each: how sleep works and why it matters, sleep deprivation and "
            "deficiency, insomnia, sleep apnoea (its signs, CPAP and other treatments, living with it); and the "
            "DASH eating plan (Dietary Approaches to Stop Hypertension: what to eat, how it lowers blood pressure, "
            "servings by food group).",
            f"A work of the National Institutes of Health (public domain). {NOTE}", depth=1,
            units=[(r"dash", "The DASH eating plan"), (r".", "Sleep")], limit=60),
    K.guide(GROUP, "niddk_weight_management", "Weight management, healthy eating and activity (NIDDK)",
            "Weight management", "National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), National "
            "Institutes of Health", "https://www.niddk.nih.gov/health-information/weight-management",
            r"^https://www\.niddk\.nih\.gov/health-information/weight-management(/[a-z0-9-]+){0,3}$",
            "NIDDK's weight management pages, every page: healthy eating and physical activity for life, tips for "
            "getting active, physical activity for people with overweight, healthy eating at every age, "
            "understanding overweight and obesity, weight-loss medicines and surgery, choosing a weight-loss "
            "programme, and changing your habits.",
            f"A work of the National Institutes of Health (public domain). {NOTE}", depth=2,
            follow=r"^https://www\.niddk\.nih\.gov/health-information/weight-management(/[a-z0-9-]+)?$", limit=120),
    M.owh_book(GROUP, "owh_active_eating_weight", "Getting active, healthy eating and healthy weight (Office on "
               "Women's Health)", "Physical activity and nutrition", ["getting-active", "healthy-eating",
                                                                     "healthy-weight"],
               "The Office on Women's Health's pages, every page: getting active (how much, safely, at every age and "
               "with a disability), healthy eating (food groups, vitamins and minerals, heart-healthy eating, eating "
               "on a budget) and healthy weight (body mass index, losing weight safely, keeping it off).", NOTE),
]

PDFS = [
    K.us_pdf(GROUP, name="physical_activity_guidelines", title="Physical Activity Guidelines for Americans, 2nd "
             "edition (HHS, 2018)", subject="Physical activity", publisher="US Department of Health and Human "
             "Services", pdf=f"{ODPHP}/sites/default/files/2019-09/Physical_Activity_Guidelines_2nd_edition.pdf",
             page=f"{ODPHP}/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines",
             published="2018", version="2nd edition (2018), the current edition when read",
             description="The whole official guidelines: what physical activity does for health, how much "
                         "preschool children, children and teens, adults and older adults need (150 to 300 minutes "
                         "a week of moderate aerobic activity for adults, muscle-strengthening on 2 days, balance "
                         "training for older adults), activity in pregnancy and after birth, for adults with chronic "
                         "conditions and disabilities, and staying safe while active.",
             notice=f"A work of the US Department of Health and Human Services (public domain). {NOTE}"),
    K.us_pdf(GROUP, name="dietary_guidelines_2025_2030", title="Dietary Guidelines for Americans, 2025-2030 (USDA and "
             "HHS)", subject="Nutrition", publisher="US Department of Agriculture and US Department of Health and "
             "Human Services", pdf=f"{REALFOOD}/documents/DGA.pdf", page=f"{REALFOOD}/",
             published="2026-01", version="2025-2030 edition (the current edition when read)",
             description="The whole official Dietary Guidelines for Americans: eating patterns built on whole, "
                         "nutrient-dense foods (protein, dairy, vegetables, fruits, healthy fats and whole grains), "
                         "limiting highly processed foods, added sugars, sodium and alcohol, and advice for every "
                         "life stage.",
             notice=f"A work of the US Department of Agriculture and the US Department of Health and Human Services "
                    f"(public domain). {NOTE}"),
    K.us_pdf(GROUP, name="dietary_guidelines_serving_sizes", title="Daily Serving Sizes (Dietary Guidelines for "
             "Americans, 2025-2030)", subject="Nutrition", publisher="US Department of Agriculture and US "
             "Department of Health and Human Services", pdf=f"{REALFOOD}/documents/Daily%20Serving%20Sizes.pdf",
             page=f"{REALFOOD}/", version="2025-2030 edition",
             description="The guidelines' table of daily servings by food group and calorie level, and what counts "
                         "as one serving.",
             notice=f"A work of the US Department of Agriculture and the US Department of Health and Human Services "
                    f"(public domain). {NOTE}"),
]

COLLECTION = K.Collection("fit", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"fitness-nutrition": lambda: [f"fit:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "fit_odphp_realfood": "odphp.health.gov and www.realfood.gov (the Physical Activity Guidelines, Move Your Way and "
                          "the Dietary Guidelines): works of the US government (17 U.S.C. 105, checked on "
                          "govinfo.gov's policies page at every build); robots.txt allows them; no AI rules (checked "
                          "2026-11-22).",
    "fit_cdc_nih_owh": "CDC's terms (as mind_cdc), www.nhlbi.nih.gov and www.niddk.nih.gov (US government works) and "
                       "OWH's disclaimer (as mind_owh), checked at every build.",
}
NOT_INCLUDED = [
    ("MyPlate.gov (food groups, MyPlate Plan, life stages)", "Public domain, but www.myplate.gov could not be reached "
     "from the build machine (no answer, checked again 2026-11-22) and the Internet Archive's Wayback copies did not "
     "answer either. The Dietary Guidelines are built, and FDA's \"using the label with MyPlate\" page is in "
     "fdc:label_guide. Link-only. Index: https://www.myplate.gov/"),
    ("Dietary Guidelines for Americans, 2020-2025", "Replaced by the 2025-2030 edition (fit:dietary_guidelines_2025_"
     "2030); the old edition stays on its site. Index: https://www.dietaryguidelines.gov/about-dietary-guidelines/"
     "previous-editions"),
    ("National Institute on Aging: Exercise and Physical Activity (Your Everyday Guide), Go4Life, and its healthy "
     "eating pages for older adults", "Public domain, but www.nia.nih.gov answers programs with a bot check "
     "(\"405\"; checked again 2026-11-22); Go4Life was retired and the Internet Archive holds only class videos. "
     "Link-only. Index: https://www.nia.nih.gov/health/exercise-and-physical-activity"),
    ("NCHPAD (the National Center on Health, Physical Activity and Disability): adapted exercise videos and guides",
     "Copyright of the University of Alabama at Birmingham, not openly licensed (checked 2026-11-22). Link-only. "
     "Index: https://www.nchpad.org/"),
    ("US Association of Blind Athletes (USABA), the International Blind Sports Federation (IBSA), the National Beep "
     "Baseball Association and United States Blind Golf", "Copyright, and www.usaba.org's robots.txt shuts out AI "
     "companies' readers (checked 2026-11-22). Link-only for goalball, beep baseball, tandem cycling and running "
     "with a guide. Index: https://www.usaba.org/ , https://ibsasport.org/ and https://www.nbba.org/"),
    ("FDA: reading the Nutrition Facts label", "Already built: fdc:label_guide (every page of FDA's label guide) "
     "and the drinks book fda_drink_labels_and_caffeine; not repeated. Index: https://www.fda.gov/food/"
     "nutrition-facts-label/how-understand-and-use-nutrition-facts-label"),
    ("NIDDK and NHLBI diabetes and heart-healthy eating pages", "Already built: homecare:niddk_diabetes_kidney_"
     "digestive and homecare:nhlbi_heart_lungs; the DASH week of menus is the cookbook nhlbi_week_on_dash. Index: "
     "https://www.niddk.nih.gov/health-information/diabetes/overview/diet-eating-physical-activity"),
    ("Makers' fitness equipment and tracker guides (Peloton, NordicTrack, Bowflex, Concept2, Garmin, Fitbit ...)",
     "The makers' copyright; listed as links in the manual collection fitness_equipment. Index: "
     "https://www.concept2.com/support"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
