"""Picture packs for DRIVING AND ROAD RULES (the owner's request of 2026-11-22). Used by build_packs.py in the same
way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture
with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The
limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to tell him what is in a photo
of a car's controls or a road, and to say the safety rule that goes with it: the pedals and gear stick, the seat
belt, a learner driver's sign, a school bus, a crossing guard, a roundabout or a rumble strip, and the accessible
taxis and paratransit vans a blind passenger rides in.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no make, model, place or speed is named unless the category itself names it. Answers about driving end with
the safety notes that fit (the same words in the kit's practical_sources.py):
  DRIVE_NOTE       seat belt for everyone, no phone, never drive impaired; the state's handbook has the rules.
  SCHOOL_BUS_NOTE  stop for a school bus with red lights flashing and its stop arm out (the state's handbook says
                   when traffic going the other way must stop too).
  PEDESTRIAN_NOTE  drivers must yield to people in crosswalks; a white cane or guide dog means a blind pedestrian.
  PASSENGER_NOTE   a blind or low-vision passenger: buckle up, confirm the vehicle and driver before getting in.

The packs (DRIVING_PACKS):
  commons_driving        Wikimedia Commons (CC0, public domain or CC BY files only): steering wheels, driver's
                         seats, ignition switches, car pedals, gear sticks, cruise control and seat belts; learner
                         driver signs and driving schools; road markings, roundabouts, rumble strips, speed bumps
                         and ramp meters; school buses and crossing guards; paratransit and wheelchair-accessible
                         taxis.
  open_images_driving    Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark): the
                         driver's seat (steering parts, automobile pedals, seat belt),
                         the road (lane, road shoulder, dirt road, traffic circle, traffic congestion, parking lot,
                         parking meter). No label is asked twice (packs/test_practical.py checks).

Not repeated here: the road sign packs (us_road_signs, ca_road_signs), the street scene packs (crossings, pedestrian
signals, traffic lights), car care (commons_car_care, commons_dashboard_lights: warning lights, tyres, jacks), baby
products (Child safety seats) and the vehicle packs (makes and models). What was looked at and left out is in the
kit's practical_sources.py (PRACTICAL_NOT_INCLUDED).

    python packs/driving_packs.py commons_driving --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap
from outdoor_cooking_packs import thing, with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

DRIVE_NOTE = ("Driving safety: everyone buckles up, the phone stays put away, and never drive after drinking or "
              "using drugs or when drowsy; your state's or province's driver handbook has the rules of the road.")
SCHOOL_BUS_NOTE = ("School buses: when a school bus stops with its red lights flashing and its stop arm out, traffic "
                   "must stop and wait until the lights stop flashing; your state's driver handbook says when "
                   "traffic going the other way must stop too.")
PEDESTRIAN_NOTE = ("Pedestrians: drivers must yield to people in crosswalks; a person with a white cane or a guide "
                   "dog is blind or has low vision, and drivers must stop for them.")
PASSENGER_NOTE = ("Passengers: buckle up, and before getting in, confirm the vehicle and the driver (a rideshare app "
                  "or the dispatcher gives the driver's name and the plate number).")


# ----------------------------------------------------------------- Commons: the driver's seat and the road

DRIVING = [
    thing("Steering wheels", "a steering wheel", DRIVE_NOTE),
    thing("Automobile pedals", "a car's pedals: in an automatic car the brake is on the left and the accelerator on "
                               "the right; a manual car also has a clutch pedal at the far left", DRIVE_NOTE),
    thing("Driver's seats", "a driver's seat; set it so the pedals are reached with knees slightly bent and the "
                            "steering wheel is at least 10 inches (25 cm) from the chest, for the airbag", DRIVE_NOTE),
    thing("Ignition switches", "an ignition switch, where the key turns or the start button is pressed to start the "
                               "engine", DRIVE_NOTE),
    thing("Gear sticks", "a gear stick (gear lever) for changing gears", DRIVE_NOTE),
    thing("Cruise control", "cruise control, which keeps the car at a speed the driver sets", DRIVE_NOTE),
    thing("Seat belts", "a seat belt", f"{DRIVE_NOTE} The lap belt goes low across the hips and the shoulder belt "
                                       f"across the chest, never behind the back.", True),
    thing("Learner driver signs", "a learner driver sign (an L plate or student driver sign) on a car driven by "
                                  "someone learning to drive", DRIVE_NOTE),
    thing("Driving schools", "a driving school or its car", DRIVE_NOTE),
    thing("Roundabouts", "a roundabout: traffic goes round one way and drivers entering it yield to traffic "
                         "already in it", f"{DRIVE_NOTE} {PEDESTRIAN_NOTE}"),
    thing("Road markings", "road markings: painted lines and symbols on the road (lane lines, stop lines, "
                           "crosswalks, arrows)", f"{DRIVE_NOTE} {PEDESTRIAN_NOTE}", True),
    thing("Rumble strips", "rumble strips: grooves or bumps in the road that make a loud rumble under the tyres, to "
                           "warn a driver who drifts off the lane or nears a stop", DRIVE_NOTE, True),
    thing("Speed bumps", "a speed bump, a raised hump across the road that makes drivers slow down", DRIVE_NOTE),
    thing("Ramp meters", "a ramp meter, a traffic light on a motorway on-ramp that lets cars on one at a time",
          DRIVE_NOTE),
    thing("School buses", "a school bus", SCHOOL_BUS_NOTE, True),
    thing("Crossing guards", "a crossing guard, who stops traffic so people, often children, can cross the road",
          f"{PEDESTRIAN_NOTE} Drivers must obey a crossing guard's stop sign.", True),
    thing("Paratransit", "a paratransit vehicle, a door-to-door ride service for people who cannot use buses and "
                         "trains", PASSENGER_NOTE, True),
    thing("Wheelchair accessible taxis", "a wheelchair-accessible taxi, with a ramp or lift", PASSENGER_NOTE),
]


def build_commons_driving(limit):
    """The commons_driving pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(DRIVING, limit, "driving")


# ----------------------------------------------------------------- Open Images

DRIVING_OI = [
    group("What car controls are in this picture?",
          {"Steering part": "a steering part", "Automobile pedal": "a car pedal", "Seat belt": "a seat belt"},
          DRIVE_NOTE),
    group("What kind of road is in this picture?",
          {"Lane": "a traffic lane", "Shoulder (Road)": "a road shoulder", "Dirt road": "a dirt road",
           "Traffic circle": "a traffic circle (roundabout)", "Traffic congestion": "a traffic jam"}, DRIVE_NOTE),
    group("What parking things are in this picture?",
          {"Parking lot": "a parking lot", "Parking meter": "a parking meter"}),
]


def build_open_images_driving(limit):
    """open_images_driving (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_driving", DRIVING_OI, limit, 9401), DRIVING_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
DRIVING_PACKS = {
    "commons_driving": (build_commons_driving, COMMONS_LICENCE.format(
        what="car control, learner driver, roundabout, rumble strip, school bus, crossing guard and paratransit")),
    "open_images_driving": (build_open_images_driving, OI_LICENCE),
}
DRIVING_LIMITS = {
    "commons_driving": 900,         # 18 categories
    "open_images_driving": 1500,    # 10 labels; roads have the most photos
}
DRIVING_COMMONS_KEYS = ("commons_driving",)
DRIVING_SPECS = DRIVING


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(DRIVING_PACKS, "Try a driving pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
