"""Picture packs for FITNESS AND NUTRITION (the owner's request of 2026-11-22). Used by build_packs.py in the same way
as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]. The limit
counts pictures.

Why: the owner is blind and wants his offline assistant to recognise home exercise equipment and activity trackers,
the sports blind and other disabled athletes play (running with a guide, blind cricket, torball, tandem cycling,
sitting volleyball, boccia), and the food guide pictures (MyPlate and food pyramids) that the Dietary Guidelines
books explain.

Answers say only what the Commons category names (with a plain line written here), and every answer ends with the
fitness note (the owner's health note, adapted):
  FIT_NOTE  "General information, not medical advice or a diagnosis: if you have a health condition, ask your doctor
            before you start a new exercise or eating plan. In an emergency call 911; in a mental health crisis call
            or text 988."
The words are the same as the reference books' (textbooks/fitness_nutrition.py NOTE; packs/test_health_life.py
checks).

The packs (FITNESS_NUTRITION_PACKS), all Wikimedia Commons (CC0, public domain or CC BY files only):
  commons_fitness_equipment  indoor rowers (rowing machines), resistance bands, balance boards, medicine balls,
                             exercise (Swiss) balls, weight plates, ab wheels, push-up bars, suspension trainers,
                             pedometers and heart rate monitors.
  commons_adaptive_sports    running with a guide, blind cricket, torball, sitting volleyball, boccia, para-cycling
                             (blind riders on tandems with a sighted pilot) and Nordic walking. People are in these
                             photos (describing only).
  commons_food_guides        MyPlate and food pyramids (the USDA's and other countries' food guide pictures); in the
                             food topic.

Not repeated here: dumbbells, kettlebells, yoga mats and jump ropes (everyday_extras_packs), treadmills, exercise
bikes and activity trackers (device_packs), Open Images exercise equipment (gaps_oi_packs), goalball, blind football,
wheelchair sports and Paralympic sports (disability_packs), weight training and stretching (people_activity_packs,
expression_packs), kitchen scales, measuring cups and the Nutrition Facts label (home_packs, things_packs,
packaged_goods_packs). Open Images was counted on 2026-11-22: Kettlebell, Medicine ball, Yoga mat, Resistance band,
Goalball, Pedometer, Heart rate monitor and the other free labels have almost no human-checked photos, so there is
no Open Images pack. What was looked at and left out is in the kit's fitness_nutrition_sources.py.

    python packs/fitness_nutrition_packs.py commons_food_guides --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

FIT_NOTE = ("General information, not medical advice or a diagnosis: if you have a health condition, ask your doctor "
            "before you start a new exercise or eating plan. In an emergency call 911; in a mental health crisis call "
            "or text 988.")
ASK_WHAT = "What is this?"
ASK_SPORT = "What sport is this?"


def thing(category, words, deeper=False, question=ASK_WHAT):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, "This is <words>." and the
    fitness note)])."""
    return (category, deeper, [(question, f"This is {words}. {FIT_NOTE}")])


FITNESS_EQUIPMENT = [
    thing("Indoor rowers", "an indoor rower (rowing machine), which works the legs, back and arms", True),
    thing("Rowing machines", "a rowing machine (indoor rower)"),
    thing("Resistance bands", "a resistance band, a stretchy band for strength exercises"),
    thing("Balance boards", "a balance board, a board on a rounded base for practising balance"),
    thing("Medicine balls", "a medicine ball, a heavy ball for strength exercises", True),
    thing("Exercise balls", "an exercise ball (a Swiss or stability ball), a large inflatable ball for balance, "
                            "stretching and strength exercises", True),
    thing("Weight plates", "a weight plate, a disc of metal or rubber-coated weight that slides onto a barbell"),
    thing("Ab wheels", "an ab wheel (ab roller), a small wheel with handles for strengthening the stomach muscles"),
    thing("Push-up bars", "push-up bars, a pair of handles for doing push-ups"),
    thing("Suspension training", "suspension training: exercises with straps hung from an anchor overhead, using "
                                 "the body's own weight"),
    thing("Pedometers", "a pedometer, a step counter", True),
    thing("Heart rate monitors", "a heart rate monitor, which measures the heartbeat during exercise", True),
]

ADAPTIVE_SPORTS = [
    thing("Guide runners", "running with a guide: a blind or partially sighted runner and a sighted guide run side "
                           "by side, often holding a short tether between them", question=ASK_SPORT),
    thing("Blind cricket", "blind cricket, cricket for blind and partially sighted players, played with a ball that "
                           "rattles so it can be heard, bowled underarm", question=ASK_SPORT),
    thing("Torball", "torball, a team sport for blind and partially sighted players, who roll a ball with bells "
                     "inside under strings stretched across the court", question=ASK_SPORT),
    thing("Sitting volleyball", "sitting volleyball, a Paralympic kind of volleyball played sitting on the floor, "
                                "with a lower net", True, ASK_SPORT),
    thing("Boccia", "boccia, a Paralympic ball sport: players throw, kick or roll leather balls, using a ramp if "
                    "they need one, as close as they can to a white target ball", True, ASK_SPORT),
    thing("Para-cycling", "para-cycling, cycling for athletes with disabilities; blind and partially sighted riders "
                          "race on tandem bicycles with a sighted pilot in front", True, ASK_SPORT),
    thing("Nordic walking", "Nordic walking, brisk walking with two poles", True, ASK_SPORT),
]

FOOD_GUIDES = [
    thing("MyPlate", "MyPlate, the US Department of Agriculture's food guide picture (2011): a plate divided into "
                     "fruits, vegetables, grains and protein foods, with a cup beside it for dairy", True),
    thing("Food pyramids", "a food pyramid, a picture that shows the kinds of food to eat more of (at the wide "
                           "bottom) and less of (at the narrow top); the USDA's Food Guide Pyramid (1992) was "
                           "replaced by MyPyramid (2005) and then by MyPlate (2011)", True),
]


def build_commons_fitness_equipment(limit):
    """The commons_fitness_equipment pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FITNESS_EQUIPMENT, limit, "fitequip")


def build_commons_adaptive_sports(limit):
    """The commons_adaptive_sports pack (see the module docstring); rows of files naming a child are marked so."""
    from home_packs import build_commons_topic
    return build_commons_topic(ADAPTIVE_SPORTS, limit, "adaptsport")


def build_commons_food_guides(limit):
    """The commons_food_guides pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FOOD_GUIDES, limit, "foodguide")


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
FITNESS_NUTRITION_PACKS = {
    "commons_fitness_equipment": (build_commons_fitness_equipment, COMMONS_LICENCE.format(
        what="rowing machine, resistance band, balance board, exercise ball, weight plate, pedometer and heart rate "
             "monitor")),
    "commons_adaptive_sports": (build_commons_adaptive_sports, COMMONS_LICENCE.format(
        what="guide running, blind cricket, torball, sitting volleyball, boccia, para-cycling and Nordic walking")),
    "commons_food_guides": (build_commons_food_guides, COMMONS_LICENCE.format(what="MyPlate and food pyramid")),
}
FITNESS_NUTRITION_LIMITS = {
    "commons_fitness_equipment": 500,      # 12 categories, about 400 files
    "commons_adaptive_sports": 400,        # 7 categories, about 300 files
    "commons_food_guides": 150,            # 2 categories, about 90 files
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
FITNESS_NUTRITION_COMMONS_KEYS = ("commons_fitness_equipment", "commons_adaptive_sports", "commons_food_guides")
# The Commons category specs of the packs (for the self-test).
FITNESS_NUTRITION_SPECS = FITNESS_EQUIPMENT + ADAPTIVE_SPORTS + FOOD_GUIDES


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a fitness and nutrition pack builder.")
    parser.add_argument("key", choices=sorted(FITNESS_NUTRITION_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = FITNESS_NUTRITION_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
