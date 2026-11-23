"""More fitness and nutrition for the reference library, in the group "Reference, fitness and nutrition" (the owner's
request of 2026-11-23: fill the thin fitness and nutrition area with practical how-to). Keys: fitness-more (every
book), fit:<name>, and one request word per theme: fit-military, fit-older-adaptive, fit-diets and fit-classics. A
sibling of fitness_nutrition.py, which also uses the key prefix "fit:" (more_refs.module_for tells them apart by
their own keys).

What this module builds, in plain words, each IN FULL:
  - fit:index, a guide to fitness and nutrition in the library (the toolkit's own facts and links, CC0): for each
    theme the books here, the books already elsewhere by key (the Physical Activity and Dietary Guidelines, CDC,
    NHLBI, NIDDK and NIA guides, NCCIH's tai chi, yoga and qigong pages, MedlinePlus, the sports rule books), the
    manual and picture collections, and the sources that are links only, with the reason;
  - military fitness manuals (fit-military), each judged at every build by the release rule for military
    publications (military_release.py: the builder reads its front pages and says truthfully what they print about
    distribution): the Army's FM 7-22 Holistic Health and Fitness (2020) and the FM 7-22 Army Physical Readiness
    Training it replaced (2012), FM 21-20 Physical Fitness Training (1992) and Physical Training (1941), the Marine
    Corps' MCRP 3-02A Marine Physical Readiness Training for Combat, the Navy SEAL Physical Fitness Guide and the
    Navy's Physical Fitness Manual (1943);
  - exercise for older adults, people with disabilities and blind people (fit-older-adaptive): Physical Activity and
    Health, a Report of the Surgeon General (1996), the President's Council's Aqua Dynamics water exercise booklet
    (1980), NHLBI's Your Guide to Physical Activity and Your Heart (2006), the Children's Bureau's Recreation for
    Blind Children (1927), and old books on physical education, athletics and games for blind people (1906 to
    1923, from the American Printing House for the Blind's library), marked historical;
  - special diets (fit-diets): NHLBI's Your Guide to Lowering Your Blood Pressure with DASH (2006) and the VA's
    nutrition handouts (Veterans Health Administration Nutrition and Food Services: heart health and sodium,
    diabetes, fibre, healthy ageing, cancer, food safety and healthy eating), read from nutrition.va.gov;
  - old physical culture books before 1931 (fit-classics), marked historical: Walter Camp's Keeping Fit All the Way
    (1919, the "Daily Dozen"), the Army's Manual of Physical Training (1914) and Setting-up Exercises (1913), the
    Navy's Manual of Physical Drill (1898), Nils Posse's Handbook of School-Gymnastics of the Swedish System (1892)
    and Sandow on Physical Training (1894).
  Every book's notice ends with fitness_nutrition.NOTE (ask your doctor before a new exercise or eating plan; 911;
  988), and the exercise books with EXERCISE_SAFETY.

Already in the library and linked from the index, not repeated: fitness_nutrition.py (fit:: the Physical Activity
Guidelines, Move Your Way, the Dietary Guidelines, CDC, NHLBI sleep and DASH page, NIDDK weight, OWH), NIA's
Exercise and Physical Activity guide and What's on Your Plate? (gpo:), NIDDK's diabetes and kidney eating pages and
NHLBI's heart pages (homecare:), NCCIH's pages on tai chi, yoga, qigong and supplements (dir:nccih_health), FDA's
Nutrition Facts label guide (fdc:label_guide), the sports collection (sport:) and Stack Exchange's Physical Fitness
site (se:).

Not built (NOT_INCLUDED, link-only): the NIH Office of Dietary Supplements fact sheets (the site refuses programs),
the Air Force's fitness manuals (its publications site refuses programs), the Navy Operational Fitness and Fueling
Series and Go4Life (retired), NCHPAD and USABA (copyright), and others listed below.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page or NHLBI's
policy at every build); old books published before 1931 (the builder checks each Internet Archive item's year).

Run from the repository's folder:
  python3 textbooks/fitness_more.py fit:index --out build/textbooks
  python3 textbooks/fitness_more.py --list fitness-more
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cooking_basics as CB  # noqa: E402 - the VA PDF book maker
import fitness_nutrition as F  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = F.GROUP                        # "fitnessnutrition": the same group as fitness_nutrition.py
GROUPS = {}                            # named by fitness_nutrition.py
NOTE = F.NOTE                          # the fitness health note (doctor, 911, 988)

EXERCISE_SAFETY = ("Exercise safety: start slowly and build up; warm up and cool down; drink water; stop and get help "
                   "at once if you have chest pain or pressure, trouble breathing, dizziness or pain that does not go "
                   "away (call 911 for chest pain). Blind and low-vision exercisers: check the space for obstacles "
                   "first, use a guide, tether or handrail where it helps, and ask a trainer to describe or guide "
                   "each movement.")
OLD_FIT_NOTE = ("Historical (published in {year}): kept for its exercises and history. Some of its advice is out of "
                "date: today's guidelines (fit:physical_activity_guidelines) are the ones to follow, and some old "
                "exercises (deep knee bends, bouncing stretches, straight-leg sit-ups) are no longer advised.")
OLD_BLIND_NOTE = ("Historical (published in {year}): written by teachers of blind pupils of its time; its words for "
                  "blind people and some of its ideas are old-fashioned, but its games and exercises can still be "
                  "used.")
MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "soldiers, sailors and Marines: its tests and standards are military ones and may be out of date. ")
NHLBI_POLICY = "https://www.nhlbi.nih.gov/about/contact/trademark-branding-and-logo"   # as cookbooks.py
NHLBI_TEXT = r"Most of the information on the NHLBI website is in the public domain"
NHLBI = "National Heart, Lung, and Blood Institute (NHLBI), National Institutes of Health"


def _keys(entries):
    """The keys of a list of entries."""
    return [f"fit:{e['name']}" for e in entries]


def _mil(name, title, publisher, archive, published, description, work):
    """One US military fitness publication of the Internet Archive, judged at every build by the release rule
    (military=True: the builder reads its front pages and writes the truthful release line)."""
    return K.us_pdf(GROUP, name=name, title=title, subject="Military fitness training", publisher=publisher,
                    archive=archive, published=published,
                    version=f"{published or 'undated'} edition (Internet Archive item {archive})",
                    description=description, notice=f"{MIL_NOTICE}{EXERCISE_SAFETY} {NOTE}", military=True,
                    work=work)


def _gov(name, title, subject, publisher, archive, published, description, safety=EXERCISE_SAFETY, note=""):
    """One US government publication read from its Internet Archive copy (public domain, 17 U.S.C. 105)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description + (" " + note.format(year=published[:4]) if note else ""),
                    notice=f"A work of the US government ({publisher}): public domain, read from the Internet "
                           f"Archive's copy. {safety + ' ' if safety else ''}{NOTE}")


def _nhlbi(name, title, subject, pdf, published, description, safety=""):
    """One NHLBI guide read whole from its PDF on www.nhlbi.nih.gov (NHLBI's policy line checked at every build)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=NHLBI, pdf=pdf, page=pdf,
                    licence_page=NHLBI_POLICY, licence_text=NHLBI_TEXT, published=published,
                    version=f"{published} edition (the PDF on www.nhlbi.nih.gov)", description=description,
                    notice=f"A work of the National Institutes of Health (public domain): NHLBI says \"Most of the "
                           f"information on the NHLBI website is in the public domain\". {safety + ' ' if safety else ''}"
                           f"{NOTE}")


def _old(name, title, subject, publisher, archive, year, description, note=OLD_FIT_NOTE):
    """One old public-domain book of the Internet Archive (published before 1931), marked historical."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=f"{EXERCISE_SAFETY} {NOTE}")


ARMY = "Headquarters, Department of the Army"

# ====================================================================== military fitness manuals

MILITARY = [
    _mil("army_fm_7_22_holistic_health_fitness_2020", "Holistic Health and Fitness (FM 7-22, US Army, 2020)", ARMY,
         "fm-7-22-holistic-health-and-fitness-2020", "2020-10",
         "The Army's current fitness manual, the H2F system: physical readiness (strength, endurance, mobility, "
         "the training programme and its exercises, injury prevention and reconditioning), nutritional readiness "
         "(fuelling for training, hydration, supplements, weight), mental and spiritual readiness, and sleep "
         "readiness (how much sleep, naps, sleep in the field).", "a work of the US Army"),
    _mil("army_fm_7_22_physical_readiness_training_2012", "Army Physical Readiness Training (FM 7-22, US Army, 2012)",
         ARMY, "fm-7-22-army-physical-readiness-training-2012", "2012-10",
         "The Army's 2012 physical readiness training manual (replaced in 2020 by Holistic Health and Fitness, "
         "kept for its complete exercise drills): the principles of training, planning a programme, and every "
         "drill described step by step: preparation drills, conditioning drills, climbing drills, strength "
         "training circuits, running, recovery and the old Army Physical Fitness Test.", "a work of the US Army"),
    _mil("army_fm_21_20_physical_fitness_training_1992", "Physical Fitness Training (FM 21-20, US Army, 1992)",
         ARMY, "fm-21-20-physical-fitness-training-1992", "1992-09",
         "The Army's fitness manual of the 1990s: the components of fitness, the FITT principles (frequency, "
         "intensity, time, type), cardiorespiratory fitness, muscular endurance and strength, flexibility, "
         "body composition, circuit training and exercise drills, special programmes for soldiers who need extra "
         "help, and environmental hazards (heat, cold, altitude).", "a work of the US Army"),
    _mil("army_fm_21_20_physical_training_1941", "Physical Training (FM 21-20, US War Department, 1941)",
         "US War Department", "Fm21-20-nsia", "1941-03",
         "The Second World War Army physical training manual: setting-up exercises, rifle exercises, running, "
         "marching, grass drills, guerrilla exercises, combatives, games, swimming and tests. A historical "
         "manual: " + OLD_FIT_NOTE.format(year="1941"), "a work of the US Army"),
    _mil("usmc_mcrp_3_02a_physical_readiness_combat", "Marine Physical Readiness Training for Combat (MCRP 3-02A, US "
         "Marine Corps)", "Headquarters, US Marine Corps", "milmanual-mcrp-3-02a-marine-physical-readiness-training-"
         "for-combat", "",
         "The Marine Corps' physical training reference: the principles of conditioning, planning unit training, "
         "warm-up and cool-down, strength, endurance and flexibility exercises, conditioning hikes and runs, "
         "obstacle courses, aquatic training, and preventing injuries.", "a work of the US Marine Corps"),
    _mil("navy_seal_physical_fitness_guide", "The Navy SEAL Physical Fitness Guide (Naval Special Warfare Command)",
         "US Navy, Naval Special Warfare Command, and the Uniformed Services University of the Health Sciences",
         "US_Navy_SEAL_Physical_Fitness_Guide", "",
         "The Navy's fitness guide for SEALs, written by its sports medicine and physiology experts (edited by "
         "Patricia A. Deuster): cardiorespiratory conditioning, running, swimming, strength training, flexibility, "
         "calisthenics, circuit training, load-bearing, training in hot and cold climates and at altitude, and "
         "preventing and treating training injuries.", "a work of the US Navy"),
    _mil("navy_physical_fitness_manual_1943", "Physical Fitness Manual for the U.S. Navy (Bureau of Naval Personnel, "
         "1943)", "US Navy, Bureau of Naval Personnel, Training Division", "14321410R.nlm.nih.gov", "1943",
         "The Navy's Second World War fitness manual (the National Library of Medicine's copy): the conditioning "
         "programme, calisthenics, running, swimming, combatives, games and sports, and fitness tests. A historical "
         "manual: " + OLD_FIT_NOTE.format(year="1943"), "a work of the US Navy"),
]

# ====================================================================== older adults, disabilities and blind people

OLDER_ADAPTIVE = [
    _gov("surgeon_general_physical_activity_health_1996", "Physical Activity and Health: A Report of the Surgeon "
         "General (1996)", "Physical activity and health", "US Department of Health and Human Services, Centers "
         "for Disease Control and Prevention, and the President's Council on Physical Fitness and Sports",
         "micro_IA41153411_0310", "1996",
         "The landmark report on what regular physical activity does for health: its effects on the heart, "
         "lungs, muscles, bones, weight and mental health at every age and for people with disabilities, how much "
         "is enough, and how to help people become active. (Today's amounts are in the Physical Activity "
         "Guidelines.)"),
    _gov("pcpfs_aqua_dynamics_1980", "Aqua Dynamics: Physical Conditioning through Water Exercises (President's "
         "Council on Physical Fitness and Sports, 1980)", "Water exercise", "President's Council on Physical "
         "Fitness and Sports", "micro_IA41152939_0344", "1980",
         "Exercises done standing or holding the side of a pool, for people of all ages and abilities, including "
         "older adults and people who cannot exercise easily on land: warm-ups, exercises for each part of the "
         "body, water walking and jogging, and a conditioning programme.",
         safety=EXERCISE_SAFETY + " In the water: exercise where a lifeguard is on duty or with a partner, and stay "
                                  "where you can stand.",
         note=" Historical (published in {year}): check today's guidelines (fit:physical_activity_guidelines)."),
    _nhlbi("nhlbi_physical_activity_and_your_heart_2006", "Your Guide to Physical Activity and Your Heart (NHLBI, "
           "2006)", "Physical activity and heart health", "https://www.nhlbi.nih.gov/files/docs/public/heart/"
           "phy_active.pdf", "2006",
           "NHLBI's guide to becoming active safely, especially with heart disease or its risk factors: the benefits, "
           "how much activity, aerobic and strength activities, checking with your doctor, warming up and cooling "
           "down, staying motivated, and sample walking and jogging programmes.", safety=EXERCISE_SAFETY),
    _gov("childrens_bureau_recreation_blind_children_1927", "Recreation for Blind Children (Martha Travilla Speakman, "
         "US Children's Bureau, 1927)", "Games and exercise for blind children", "US Department of Labor, "
         "Children's Bureau", "recreationforbli00spea", "1927",
         "Play, games, sports, gymnastics, swimming, dancing, music and handwork for blind children, at home and in "
         "school, from the Children's Bureau's study of schools for the blind.", note=OLD_BLIND_NOTE),
    _old("allen_physical_education_blind_1906", "Physical Education of the Blind (E. E. Allen, 1906)",
         "Physical education for blind people", "Edward Ellis Allen (Perkins Institution)", "physicaleducatio00eeal",
         1906, "The Perkins Institution director on why blind pupils need exercise and how a school can provide it: "
         "gymnastics, free play, sports and outdoor work.", note=OLD_BLIND_NOTE),
    _old("baker_sightless_athlete_1908", "The Sightless Athlete: How the Blind Are Taught to Take Exercise (J. E. "
         "Baker, 1908)", "Physical education for blind people", "J. E. Baker", "sightlessathlete00jeba", 1908,
         "How blind pupils were taught running, jumping, rowing, swimming, wrestling and team games, with the "
         "guides and signals that made each sport possible.", note=OLD_BLIND_NOTE),
    _old("johnson_physical_culture_blind_1908", "Physical Culture for the Blind (Stanley Johnson, 1908)",
         "Physical education for blind people", "Stanley Johnson", "physicalculturef00stan", 1908,
         "What physical training did for blind pupils' health, confidence and independence, and the exercises "
         "used.", note=OLD_BLIND_NOTE),
    _old("molter_games_for_blind_1916", "Games for the Blind Which May Be Played Anywhere (Harold Molter, 1916)",
         "Games for blind people", "Harold Molter", "gamesforblindwhi00haro", 1916,
         "Active and quiet games that blind children and adults can play indoors or out, with how to set up each "
         "one and adapt it.", note=OLD_BLIND_NOTE),
    _old("montgomerie_group_games_blind_1923", "Group Games for the Blind (Edna B. Montgomerie, 1923)",
         "Games for blind people", "Edna B. Montgomerie", "groupgamesforbli00edna", 1923,
         "Group games for blind pupils, sorted by age, with the rules and the sound and touch cues each uses.",
         note=OLD_BLIND_NOTE),
]

# ====================================================================== special diets

VA_HANDOUT_PAGES = [("Heart health and sodium", "Heart_Health"), ("Diabetes", "Diabetes"), ("Fibre", "Fiber"),
                    ("Healthy ageing", "Healthy_Aging"), ("Cancer", "Nutrition_and_Cancer"),
                    ("Food safety", "Food_Safety"), ("Healthy eating and wellness", "Wellness_and_Healthy_Living"),
                    ("Intuitive eating", "Intuitive_Eating"), ("Food security", "Food_Insecurity")]
VA_HANDOUTS = [(part, f"{CB.VA_SITE}/NUTRITION/{page}.asp") for part, page in VA_HANDOUT_PAGES]
VA_HANDOUTS_BOOK = CB.va_pdf_maker(
    "fit", "va_nutrition_handouts", "Nutrition handouts for special diets (VA Nutrition and Food Services)",
    "Special diets", "The Veterans Health Administration dietitians' patient handouts, every one listed on its "
    "nutrition topic pages, one page each: heart health (the DASH eating plan, controlling sodium and reading "
    "labels, fats and oils, cholesterol), diabetes (carbohydrate counting, the plate method, blood sugar, SMART "
    "goals), fibre, healthy ageing and eating with dementia, nutrition during cancer treatment, food safety, healthy "
    "eating and anti-inflammatory eating, intuitive eating, and food on a tight budget.",
    f"From the US Department of Veterans Affairs (nutrition.va.gov): a US government work (public domain). {NOTE}",
    VA_HANDOUTS)

DIETS = [
    _nhlbi("nhlbi_dash_guide_2006", "Your Guide to Lowering Your Blood Pressure with DASH (NHLBI, 2006)",
           "Special diets: DASH and low sodium", "https://www.nhlbi.nih.gov/files/docs/public/heart/new_dash.pdf",
           "2006", "NHLBI's full DASH book (Dietary Approaches to Stop Hypertension): what DASH is and the research "
           "behind it, the DASH eating plan at different calorie levels, lowering sodium, reading labels, making "
           "the change step by step, a week of menus and recipes. (The DASH week of menus is also cook:nhlbi_week_on_"
           "dash.)", safety="Low-sodium diets: if you take blood pressure, heart or kidney medicines, ask your doctor "
                            "before cutting salt sharply or using salt substitutes (they contain potassium)."),
]

# ====================================================================== old physical culture

CLASSICS = [
    _old("camp_keeping_fit_all_the_way_1919", "Keeping Fit All the Way: How to Obtain and Maintain Health, Strength "
         "and Efficiency (Walter Camp, 1919)", "Physical culture", "Walter Camp (Harper and Brothers)",
         "07221040R.nlm.nih.gov", 1919,
         "The Yale coach's exercises for busy people, the \"Daily Dozen\" he gave to the Navy and the nation in the "
         "First World War: twelve short setting-up exercises for every day, with advice on walking, breathing, "
         "rest and food (the National Library of Medicine's copy)."),
    _old("army_manual_physical_training_1914", "Manual of Physical Training for Use in the United States Army (War "
         "Department, 1914)", "Physical culture", "US War Department (prepared by Herman J. Koehler)",
         "manualofphysical00unit", 1914,
         "The Army's physical training manual before the First World War: setting-up exercises, rifle exercises, "
         "dumb-bells and Indian clubs, jumping, climbing, running, swimming, games and athletics, with how to lead "
         "a class."),
    _old("army_setting_up_exercises_1913", "Setting-up Exercises (War Department, 1913)", "Physical culture",
         "US War Department", "settingupexercis00unit", 1913,
         "The Army's short daily setting-up drill: posture, arm, trunk and leg exercises done by count."),
    _old("navy_manual_physical_drill_1898", "A Manual of Physical Drill, or Setting-up Exercises, for Use in the Navy "
         "of the United States (W. O. Holway, 1898)", "Physical culture", "US Navy (W. O. Holway)",
         "manualofphysical00holw", 1898,
         "The Navy's setting-up drill for sailors: free exercises, exercises with the rifle and with dumb-bells, "
         "done by count."),
    _old("posse_swedish_school_gymnastics_1892", "Handbook of School-Gymnastics of the Swedish System (Baron Nils "
         "Posse, 1892)", "Physical culture", "Nils Posse (Lee and Shepard)", "handbookofschool00poss", 1892,
         "Ling's Swedish gymnastics for schools: 100 graded tables of free-standing exercises (posture, balance, "
         "arm, trunk and leg movements, marching and breathing), needing no apparatus."),
    _old("sandow_physical_training_1894", "Sandow on Physical Training: A Study in the Perfect Type of the Human Form "
         "(Eugen Sandow, 1894)", "Physical culture", "Eugen Sandow and G. Mercer Adam (J. Selwin Tait and Sons)",
         "sandowgetsphysicl00sanduoft", 1894,
         "The famous strongman's system: dumb-bell exercises for each muscle group, his training routine, and "
         "advice on food, bathing, sleep and dress."),
]

# ====================================================================== the index

SECTIONS = [
    ("Military fitness manuals", "Army, Marine Corps and Navy fitness manuals: complete exercise drills and training "
     "plans. " + EXERCISE_SAFETY, [
        *[("key", f"fit:{e['name']}", e["title"]) for e in MILITARY],
        ("word", "service-skills", "Military job manuals (the service skills collection)"),
        ("link", "Air Force fitness programme (DAFMAN 36-2905)", "https://www.e-publishing.af.mil/",
         "a US government work, but the Air Force publications site refuses programs; open it in a browser"),
        ("link", "Navy Operational Fitness and Fueling Series (NOFFS)", "https://www.mynavyhr.navy.mil/Support-"
         "Services/21st-Century-Sailor/Physical-Readiness/", "retired, and its videos and pages are not openly "
                                                             "downloadable")]),
    ("Exercise for older adults, people with disabilities and blind people", "Staying active at every age and "
     "ability. " + EXERCISE_SAFETY, [
        *[("key", f"fit:{e['name']}", e["title"]) for e in OLDER_ADAPTIVE],
        ("key", "fit:physical_activity_guidelines", "Physical Activity Guidelines for Americans, 2nd edition (with "
                                                    "older adults and people with disabilities)"),
        ("key", "fit:odphp_move_your_way", "Move Your Way: getting active the easy way (HHS)"),
        ("key", "fit:cdc_activity_nutrition_weight", "Physical activity, nutrition and healthy weight (CDC)"),
        ("key", "gpo:nia_exercise_physical_activity_2018", "Exercise and Physical Activity: Your Everyday Guide (NIA, "
                                                           "2018)"),
        ("word", "dir:nccih_health", "NCCIH's pages on tai chi, qigong, yoga and other mind and body practices"),
        ("key", "sport:index", "Sports: the guide, with blind sports (goalball, beep baseball) and rules"),
        ("key", "vision:index", "Blind and low-vision living: the guide"),
        ("manuals", "fitness_equipment", "Fitness equipment and activity tracker manuals"),
        ("manuals", "sports_equipment", "Sports equipment manuals"),
        ("pack", "commons_adaptive_sports", "Adaptive and para sports, for the picture describer"),
        ("pack", "commons_fitness_equipment", "Fitness equipment, for the picture describer"),
        ("link", "NCHPAD: adapted exercise videos and guides", "https://www.nchpad.org/", "copyright of the "
                                                                                          "University of Alabama "
                                                                                          "at Birmingham; open it "
                                                                                          "in a browser"),
        ("link", "US Association of Blind Athletes", "https://www.usaba.org/", "copyright; open it in a browser"),
        ("link", "National Institute on Aging: exercise and physical activity", "https://www.nia.nih.gov/health/"
                 "exercise-and-physical-activity", "public domain, but the site answers programs with a bot check; "
                                                   "open it in a browser")]),
    ("Special diets", "Eating plans for blood pressure, heart health, diabetes, kidney disease and more. Ask your "
     "doctor or a dietitian before starting a special diet.", [
        *[("key", f"fit:{e['name']}", e["title"]) for e in DIETS],
        ("key", "fit:va_nutrition_handouts", "Nutrition handouts for special diets (VA Nutrition and Food "
                                             "Services)"),
        ("key", "fit:nhlbi_sleep_dash", "NHLBI's DASH eating plan page (with sleep)"),
        ("key", "fit:dietary_guidelines_2025_2030", "Dietary Guidelines for Americans, 2025-2030"),
        ("key", "fit:niddk_weight_management", "Weight management, healthy eating and activity (NIDDK)"),
        ("key", "homecare:niddk_diabetes_kidney_digestive", "NIDDK: diabetes, kidney disease and digestive "
                                                            "problems, with eating for each (and celiac disease)"),
        ("key", "homecare:nhlbi_heart_lungs", "NHLBI: high blood pressure, heart attack and heart failure"),
        ("key", "cook:nhlbi_week_on_dash", "A Week with the DASH Eating Plan (NHLBI): menus and recipes"),
        ("key", "cook:nhlbi_heart_healthy_recipes", "Heart-healthy recipes (NHLBI)"),
        ("key", "cook:fda_food_safety_and_allergens", "Food allergies and gluten-free labelling (FDA)"),
        ("key", "fdc:label_guide", "Reading the Nutrition Facts label (FDA): sodium, sugars, serving sizes"),
        ("key", "gpo:nia_whats_on_your_plate_2019", "What's on Your Plate? Healthy eating as you age (NIA)"),
        ("word", "dir:nccih_health", "NCCIH: dietary supplements and herbs at a glance"),
        ("word", "cooking-basics", "Cooking basics: the guide to cooking in the library (cook:index)"),
        ("pack", "commons_food_guides", "Food guides (plates and pyramids), for the picture describer"),
        ("link", "NIH Office of Dietary Supplements fact sheets", "https://ods.od.nih.gov/factsheets/list-all/",
         "public domain, but the site refuses programs (403); open it in a browser"),
        ("link", "MyPlate (USDA)", "https://www.myplate.gov/", "public domain, but the site did not answer the build "
                                                               "machine; open it in a browser")]),
    ("Old physical culture books", "Exercise books from before 1931, for their drills and history. "
     + OLD_FIT_NOTE.format(year="the year in each title"), [
        *[("key", f"fit:{e['name']}", e["title"]) for e in CLASSICS],
        ("word", "sports", "The sports collection, with old public-domain rule books"),
        ("link", "Stack Exchange: Physical Fitness (in the Kiwix library)", "https://fitness.stackexchange.com/",
         "CC BY-SA, already in the Kiwix library; reading only")]),
]
INDEX = X.index_maker("fit", GROUP, "Fitness and nutrition: a guide to the library", "Fitness and nutrition",
                      "A guide to fitness and nutrition in the library: military fitness manuals, exercise for "
                      "older adults, people with disabilities and blind people, special diets, and old physical "
                      "culture books, with every guideline, manual collection, picture pack and link-only source.",
                      SECTIONS)
MAKERS = {"index": INDEX, "va_nutrition_handouts": VA_HANDOUTS_BOOK}

PDFS = MILITARY + OLDER_ADAPTIVE + DIETS + CLASSICS
WORDS = {"fitness-more": lambda: ["fit:index", "fit:va_nutrition_handouts"] + _keys(PDFS),
         "fit-military": lambda: ["fit:index"] + _keys(MILITARY),
         "fit-older-adaptive": lambda: ["fit:index"] + _keys(OLDER_ADAPTIVE),
         "fit-diets": lambda: ["fit:index", "fit:va_nutrition_handouts"] + _keys(DIETS),
         "fit-classics": lambda: ["fit:index"] + _keys(CLASSICS)}
COLLECTION = K.Collection("fit", GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "fitmore_military": "FM 7-22 (2020 and 2012), FM 21-20 (1992 and 1941), MCRP 3-02A, the Navy SEAL Physical "
                        "Fitness Guide and the 1943 Navy manual: works of the US armed forces read from the "
                        "Internet Archive (armypubs.army.mil and the Navy's sites refuse programs) and judged at "
                        "every build by the release rule (military_release.py): the builder reads the front pages "
                        "and says truthfully what they print about distribution; a restricted marking is never "
                        "republished.",
    "fitmore_us_gov": "The Surgeon General's report, the President's Council booklet and the Children's Bureau study "
                      "(Internet Archive copies) and the VA's handouts (nutrition.va.gov, no robots.txt, no AI rules, "
                      "checked 2026-11-23): works of the US government (17 U.S.C. 105, the line checked on "
                      "govinfo.gov's policies page at every build); NHLBI's two guides under NHLBI's own policy "
                      "line, checked at every build.",
    "fitmore_old_books": "The physical culture books and the books on physical education for blind people were "
                         "published before 1931; the builder checks each Internet Archive item's year at every "
                         "build. archive.org's robots.txt allows the files; no AI rules (checked 2026-11-23).",
    "fitmore_index": "The fitness guide (fit:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("NIH Office of Dietary Supplements fact sheets (vitamins, minerals, supplements)", "Public domain, but "
     "ods.od.nih.gov refuses programs (\"403\", robots.txt included, checked 2026-11-23). NCCIH's herbs and "
     "supplements pages are built (dir:nccih_health) and MedlinePlus's (mlp:). Link-only from fit:index. Index: "
     "https://ods.od.nih.gov/factsheets/list-all/"),
    ("Air Force fitness programme (DAFMAN 36-2905, the Air Force fitness assessment charts)", "A US government work, "
     "but static.e-publishing.af.mil refuses programs (\"403\", checked 2026-11-23) and no complete copy was found on "
     "the Internet Archive (only studies about the programme). Link-only. Index: https://www.e-publishing.af.mil/"),
    ("Navy Operational Fitness and Fueling Series (NOFFS) and the Navy Physical Readiness Program guides", "NOFFS was "
     "retired; its workout cards and videos were never published as one openly downloadable book, and the Navy's "
     "site refuses programs. The Navy SEAL guide and the 1943 Navy manual are built. Index: "
     "https://www.mynavyhr.navy.mil/Support-Services/21st-Century-Sailor/Physical-Readiness/"),
    ("Army Physical Readiness Training (TC 3-22.20, 2010) and Physical Training (FM 21-20, 1957)", "Replaced by the "
     "2012 FM 7-22 and kept close to it and to the 1941 and 1992 FM 21-20 built here; not built twice. Index: "
     "https://archive.org/details/DTIC_ADA531081"),
    ("Go4Life and NIA's Exercise: A Guide from the National Institute on Aging (2001), Fitness Over Fifty",
     "Go4Life was retired; the 2001 guide on the Internet Archive is a lending copy, and Fitness Over Fifty is a "
     "commercial reprint with its own additions. NIA's 2018 Everyday Guide is built (gpo:nia_exercise_physical_"
     "activity_2018). Index: https://www.nia.nih.gov/health/exercise-and-physical-activity"),
    ("Adult Physical Fitness (President's Council on Physical Fitness, 1963)", "A US government booklet, but the "
     "Internet Archive's only scan is a lending copy that cannot be downloaded. Index: "
     "https://archive.org/details/adultphysicalfit0000pres"),
    ("President's Council research digests (Exercise and Aging, 1977; Physical Activity and Fitness for Persons with "
     "Disabilities, 1999)", "Written by university authors for the Council, so not clearly works of the US "
     "government; left out. Index: https://archive.org/details/micro_IA41153435_0707"),
    ("NCHPAD, the US Association of Blind Athletes, IBSA and adaptive sports organisations", "Copyright, and USABA's "
     "robots.txt shuts out AI readers (as fitness_nutrition.py says); link-only from fit:index. Index: "
     "https://www.nchpad.org/"),
    ("NCCIH's tai chi, qigong and yoga pages", "Already built in NCCIH's health information book (dir:nccih_health); "
     "linked from fit:index, not built twice. Index: https://www.nccih.nih.gov/health/tai-chi-what-you-need-to-know"),
    ("The Navy SEAL Nutrition Guide (1994)", "The Internet Archive's only copy is a lending copy of a commercial "
     "reprint. Index: https://archive.org/details/navysealnutritio0000patr"),
    ("Walter Camp's The Daily Dozen (1925 book with records)", "No public scan was found; his 1919 Keeping Fit All the "
     "Way, which sets out the same twelve exercises, is built. Index: https://archive.org/details/07221040R.nlm.nih.gov"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
