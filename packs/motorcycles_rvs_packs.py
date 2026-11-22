"""Picture packs for MOTORCYCLES, RVS AND TRAILERS (the owner's request of 2026-11-22). Used by build_packs.py in the
same way as its own PACKS (build_<key>(limit) returns [(file name, JPEG bytes or None, row)]).

Why: the owner wants the picture describer to name what a photo of a trailer hitch, an RV or a motorcycle shows (the
coupling and tow bar, the dump station, a travel trailer, teardrop or truck camper, a motorcycle's
handlebars, mirrors and lights, the helmet and protective clothing) and to say the safety rules that go with them:
towing and trailer safety, RV propane and carbon monoxide, and motorcycle helmets.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed); no make or
model is named unless the category names it. Answers end with the notes that fit (the same words as the kit's
practical_sources.py):
  TOW_NOTE    ratings matched, tongue weight about 10 to 15 percent, safety chains crossed, lights and breakaway
              checked, slower driving (NHTSA's towing advice).
  RV_NOTE     smoke, carbon monoxide and propane alarms, propane off when driving and refuelling, generator exhaust.
  DUMP_NOTE   gloves; black tank first, then grey; fresh-water hose apart from the sewer hose.
  MOTO_NOTE   a DOT-approved helmet (FMVSS 218), eye protection and protective clothing; training and a licence.

The packs (MOTORCYCLES_RVS_PACKS):
  commons_trailers_rvs     Wikimedia Commons (CC0, public domain or CC BY files only): trailer couplings and tow
                           bars, travel trailers, teardrop trailers, truck campers, campervans,
                           recreational vehicles, RV parks and sanitary dump stations.
  commons_motorcycle_gear  Commons: motorcycle handlebars, mirrors and lights, helmets, protective clothing, gloves and
                           boots, motorcycle safety and training, and sidecars.
  open_images_motorcycles_rvs  Open Images V7 (labels CC BY 4.0; photos CC BY, CC0 or the Public Domain Mark): RVs and
                           trailers (recreational vehicle, travel trailer, caravan, trailer, horse trailer, bicycle
                           trailer), motorcycle kinds (cruiser, enduro, moped, motorized scooter) and
                           motorcycle gear (helmet, protective clothing, boots, suit, fairing). No label is asked
                           twice (packs/test_practical.py checks).

Not repeated here: mechanical_packs (motorcycle engines, exhausts, brakes, wheels, tyres, chains, dashboards, final
drives and repairs), culture_packs (Motorhomes), na_animal_packs (Horse trailers, Commons), the car care packs (tow
trucks), another pack's Commons Wheel chocks and Open Images Scooter, and the power helper's plug and
socket packs (NEMA TT-30 and 14-50 RV plugs are theirs). Boat trailers belong to the leisure (boating) collections.

    python packs/motorcycles_rvs_packs.py commons_trailers_rvs --limit 8
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap
from outdoor_cooking_packs import thing, with_yes_notes

TOW_NOTE = ("Towing safety: match the hitch, ball and coupler ratings to the loaded trailer's weight; keep the "
            "tongue weight at about 10 to 15 percent of the trailer's weight; cross the safety chains under the "
            "tongue; connect and check the lights and the breakaway brake before every trip; and drive slower, "
            "leaving more room to stop.")
RV_NOTE = ("RV safety: keep working smoke, carbon monoxide and propane alarms; turn the propane off while driving "
           "and refuelling; and never run a generator where its exhaust can drift into a window, vent or door.")
DUMP_NOTE = ("At the dump station: wear disposable gloves, empty the black (toilet) tank first and then the grey "
             "tank, and keep the fresh-water hose well apart from the sewer hose.")
MOTO_NOTE = ("Motorcycle safety: wear a DOT-approved helmet (it meets the US standard FMVSS 218), eye protection, "
             "and a protective jacket, gloves, trousers and boots; take a rider course and hold the motorcycle "
             "licence or endorsement your state requires.")

TRAILERS_RVS = [
    thing("Trailer couplings", "a trailer coupling (hitch), which joins a trailer to the vehicle that tows it",
          TOW_NOTE, True),
    thing("Tow bars", "a tow bar, the bar on a vehicle that a trailer or caravan is hitched to", TOW_NOTE),
    thing("Travel trailers", "a travel trailer (caravan), a camper towed behind a car or truck", f"{TOW_NOTE} "
                                                                                                f"{RV_NOTE}"),
    thing("Teardrop trailers", "a teardrop trailer, a small, light camping trailer shaped like a teardrop",
          TOW_NOTE),
    thing("Truck campers", "a truck camper, a camper carried on the bed of a pickup truck", RV_NOTE),
    thing("Campervans", "a campervan, a van fitted out for sleeping and cooking", RV_NOTE),
    thing("Recreational vehicles", "a recreational vehicle (RV)", RV_NOTE),
    thing("RV parks", "an RV park (campground) with hookups for water, power and sewer", RV_NOTE),
    thing("Sanitary dump stations", "a sanitary dump station, where RVs empty their waste water tanks", DUMP_NOTE),
]
MOTORCYCLE_GEAR = [
    thing("Motorcycle handlebars", "motorcycle handlebars: the throttle is the right grip, the front brake lever is "
                                   "on the right and the clutch lever on the left", MOTO_NOTE),
    thing("Motorcycle mirrors", "a motorcycle mirror", MOTO_NOTE),
    thing("Motorcycle lights", "a motorcycle light", MOTO_NOTE, True),
    thing("Motorcycle helmets", "a motorcycle helmet", MOTO_NOTE, True),
    thing("Motorcycle protective clothing", "motorcycle protective clothing", MOTO_NOTE, True),
    thing("Motorcycle gloves", "motorcycle gloves", MOTO_NOTE),
    thing("Motorcycle boots", "motorcycle boots", MOTO_NOTE, True),
    thing("Motorcycle safety", "motorcycle safety", MOTO_NOTE, True),
    thing("Motorcycle training", "motorcycle rider training", MOTO_NOTE, True),
    thing("Sidecars", "a motorcycle with a sidecar, a one-wheeled car attached to its side for a passenger",
          MOTO_NOTE),
]


def build_commons_trailers_rvs(limit):
    """The commons_trailers_rvs pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(TRAILERS_RVS, limit, "trailerrv")


def build_commons_motorcycle_gear(limit):
    """The commons_motorcycle_gear pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MOTORCYCLE_GEAR, limit, "motogear")


MOTO_RV_OI = [
    group("What RV or trailer is in this picture?",
          {"Recreational vehicle (RV)": "a recreational vehicle (RV)", "Travel trailer": "a travel trailer",
           "Caravan": "a caravan", "Trailer": "a trailer", "Horse trailer": "a horse trailer",
           "Bicycle trailer": "a bicycle trailer"}, TOW_NOTE),
    group("What kind of motorcycle or scooter is in this picture?",
          {"Cruiser (Motorcycle)": "a cruiser motorcycle", "Enduro (Motorcycle)": "an enduro (off-road) motorcycle",
           "Moped": "a moped", "Motorized scooter": "a motor scooter"}, MOTO_NOTE),
    group("What motorcycle gear is in this picture?",
          {"Motorcycle helmet": "a motorcycle helmet", "Motorcycle protective clothing": "motorcycle protective "
           "clothing", "Motorcycle boot": "motorcycle boots", "Motorcycle suit": "a motorcycle suit",
           "Motorcycle fairing": "a motorcycle fairing"}, MOTO_NOTE),
]


def build_open_images_motorcycles_rvs(limit):
    """open_images_motorcycles_rvs (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_motorcycles_rvs", MOTO_RV_OI, limit, 9406), MOTO_RV_OI)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
MOTORCYCLES_RVS_PACKS = {
    "commons_trailers_rvs": (build_commons_trailers_rvs, COMMONS_LICENCE.format(
        what="trailer coupling, tow bar, travel trailer, truck camper, campervan, RV and dump station")),
    "commons_motorcycle_gear": (build_commons_motorcycle_gear, COMMONS_LICENCE.format(
        what="motorcycle handlebar, mirror, light, helmet, protective clothing, safety, training and sidecar")),
    "open_images_motorcycles_rvs": (build_open_images_motorcycles_rvs, OI_LICENCE),
}
MOTORCYCLES_RVS_LIMITS = {
    "commons_trailers_rvs": 900,           # 9 categories
    "commons_motorcycle_gear": 900,        # 10 categories
    "open_images_motorcycles_rvs": 1500,   # 15 labels
}
MOTORCYCLES_RVS_COMMONS_KEYS = ("commons_trailers_rvs", "commons_motorcycle_gear")
MOTORCYCLES_RVS_SPECS = TRAILERS_RVS + MOTORCYCLE_GEAR


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(MOTORCYCLES_RVS_PACKS, "Try a motorcycle, RV or trailer pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
