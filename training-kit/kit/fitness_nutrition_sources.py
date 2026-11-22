"""FITNESS AND NUTRITION for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/fitness_nutrition_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_fitness_equipment, commons_adaptive_sports and commons_food_guides;
  - the sources looked at for these subjects and left out, with the reason (FITNESS_NUTRITION_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category names, with a plain line, and every answer ends with the note
(general information, not medical advice or a diagnosis; ask your doctor before a new exercise or eating plan if you have a health condition; 911; 988), the same words as the packs' (packs/test_health_life.py checks).

Picture-making (FITNESS_NUTRITION_PICTURE_MAKING_OK): only the food guide pictures (drawings and charts); the equipment photos show people exercising and the adaptive sports pack shows athletes (FITNESS_NUTRITION_BODILY_KEYS, describing only).
Topics: the equipment and adaptive sports in the home topic, the food guides in the food topic.

    python -c "import sources, fitness_nutrition_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

FITNESS_NUTRITION_SOURCES = [
    Source("commons_fitness_equipment", "Home exercise equipment: rowing machines, resistance bands, balance boards, "
                                        "medicine and exercise balls, weight plates, ab wheels, push-up bars, "
                                        "suspension trainers, pedometers and heart rate monitors (Wikimedia Commons, "
                                        "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 5, prepare_pack, "about 100 MB"),
    Source("commons_adaptive_sports", "Adaptive and blind sports: running with a guide, blind cricket, torball, "
                                      "sitting volleyball, boccia, tandem para-cycling and Nordic walking (Wikimedia "
                                      "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 5, prepare_pack, "about 90 MB"),
    Source("commons_food_guides", "Food guide pictures: MyPlate and food pyramids (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 150, 5, prepare_pack, "about 20 MB"),
]
FITNESS_NUTRITION_PICTURE_MAKING_OK = {"commons_food_guides"}
# The packs that show people (describing only; added to sources.PEOPLE_AND_BODILY_PACK_KEYS).
FITNESS_NUTRITION_BODILY_KEYS = ("commons_fitness_equipment", "commons_adaptive_sports")
FITNESS_NUTRITION_NOT_INCLUDED = {
    "Open Images labels for this subject": "Kettlebell, Medicine ball, Yoga mat, Resistance band, Foam roller, "
        "Elliptical trainer, Goalball, Pedometer, Heart rate monitor, Tandem bicycle, Nordic walking and Weight "
        "training have no or almost no human-checked photos in Open Images V7 (counted 2026-11-22); Plank is mostly "
        "wooden planks; Exercise, Physical fitness, Yoga and the exercise equipment group are asked by other packs.",
    "Commons categories already used by other packs": "Dumbbells, Kettlebells, Yoga mats, Jump ropes "
        "(everyday_extras_packs), Treadmills, Stationary bicycles, Activity trackers (device_packs), Goalball, Blind "
        "football, wheelchair sports and Paralympic sports (disability_packs), Weight training (people_activity_"
        "packs), Stretching (expression_packs), Kitchen scales and Measuring cups (home_packs, things_packs).",
    "Commons categories that do not exist or hold no files (2026-11-22)": "Elliptical trainers, Pull-up bars, Power "
        "racks, Gymnastic rings, Foam rollers, Battle ropes, Beep baseball, Blind running, Showdown (sport), Blind "
        "tennis, Para judo, Blind skiing, Para swimming, Para athletics, Food groups, Portion sizes, Nutrition facts "
        "labels.",
    "USABA, IBSA, NCHPAD and the National Beep Baseball Association photos": "copyright (and usaba.org's robots.txt "
        "shuts out AI readers); not used.",
    "MyPlate.gov graphics": "myplate.gov could not be reached; the MyPlate graphics on Commons (USDA, public domain) "
        "are used instead.",
}
