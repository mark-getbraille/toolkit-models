"""Picture packs for OUTDOOR RECREATION (the owner's request of 2026-11-22). Used by build_packs.py in the same way as
its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with
more than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit
counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise outdoor gear,
fishing tackle, boats and paddling gear, and the markers that guide people on the water and the trail (buoys, day
marks, leading lights, trail blazes, avalanche signs), and to say the safety rules that go with them.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed), never a
guess: no colour, number or meaning of a buoy is named unless the category itself names it. Answers end with the
safety notes that fit (the same words in the kit's outdoors_sources.py):
  LIFE_JACKET_NOTE  wear a life jacket that fits; cold water.
  ICE_NOTE          never on ice unless it is known to be thick enough, never alone.
  TRAIL_NOTE        tell someone your plan; carry water, a light and a whistle or phone.
  MARKER_NOTE       buoys and markers: use a current chart; the Coast Guard's Boater's Guide explains them.
  AVALANCHE_NOTE    avalanche terrain: transceiver, probe, shovel, training and the forecast.
  HOOK_NOTE         hooks and line: eye protection, and the state's fishing rules.

The packs (OUTDOORS_PACKS):
  commons_water_trail_markers  Wikimedia Commons (CC0, public domain or CC BY files only): buoys, lateral and
                               cardinal marks, daymarks, mooring buoys, leading lights, trail blazes and avalanche warning signs.
  commons_boating_paddling     Commons: life jackets, throw bags, kayaks, canoes, stand-up paddleboards, paddles,
                               distress signals, boat trailers and slipways
                               (boat ramps).
  commons_fishing_tackle       Commons: fishing rods, fishing reels, lures, hooks, fly fishing, floats (bobbers),
                               fishing line and ice fishing.
  commons_outdoor_gear         Commons: hiking boots, trekking poles, sleeping pads, snowshoes, crampons, ice axes,
                               climbing harnesses, avalanche transceivers, touring bicycles and panniers, handcycles
                               and sit-skis (adaptive cycling and skiing) and bird hides.
  open_images_outdoors         Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark):
                               fishing (lures, reels, nets, bait, fly fishing), life jackets, trails and trail gear
                               (trekking poles, hiking boots, rock climbing, mountain bikes, bicycle helmets) and snow
                               sports (skiing, snowboarding, snowshoes, sleds). No label is asked twice
                               (packs/test_outdoors.py checks).

Not repeated here: the fish species packs (noaa_fisheries_species, na_herps_fish), the bird packs (na_birds, birding
pictures), the boat and lighthouse pictures of other packs, the camp cooking and camping gear (outdoor_cooking_packs,
Tent, Sleeping bag), the firearms packs (their own safety rules), and the Commons categories and Open Images labels
other packs ask (Lifebuoys, Carabiners, Tandem bicycles, Kayak, Canoe, Paddle, Fishing rod, Binoculars, Compass and
others). What was looked at and left out is in the kit's outdoors_sources.py (OUTDOORS_NOT_INCLUDED).

    python packs/outdoors_packs.py commons_fishing_tackle --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from homestead_packs import thing
from outdoor_cooking_packs import with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

LIFE_JACKET_NOTE = ("Water safety: wear a life jacket that fits whenever you are on the water; cold water can stop "
                    "you swimming within minutes. In an emergency call 911 or the Coast Guard on VHF channel 16.")
ICE_NOTE = "Ice safety: never go on ice unless it is known to be thick enough, never alone, and carry ice picks."
TRAIL_NOTE = ("Trail safety: tell someone where you are going and when you will be back; carry water, a light and a "
              "whistle or phone.")
MARKER_NOTE = ("Buoys and markers guide boats: check a current nautical chart, and keep well clear of them and of "
               "shallow water; the Coast Guard's Boater's Guide explains the US system.")
AVALANCHE_NOTE = ("Avalanche terrain: carry a transceiver, probe and shovel, know how to use them, check the avalanche "
                  "forecast and never go alone.")
HOOK_NOTE = ("Fishing: hooks and lures are sharp: wear eye protection and keep them covered; check your state's "
             "fishing licence and rules.")

# ----------------------------------------------------------------- Commons

MARKERS = [
    thing("Buoys", "a buoy, a floating marker on the water", MARKER_NOTE),
    thing("Lateral buoys", "a lateral buoy, which marks one side of a channel", MARKER_NOTE, True),
    thing("Lateral marks", "a lateral mark, which shows one side of a channel", MARKER_NOTE, True),
    thing("Cardinal marks", "a cardinal mark, which shows on which side (north, south, east or west) the safe water "
                            "lies", MARKER_NOTE, True),
    thing("Daymarks", "a daymark, an unlit sign or tower that marks a channel or hazard by day", MARKER_NOTE, True),
    thing("Mooring buoys", "a mooring buoy, where a boat can tie up", MARKER_NOTE),
    thing("Leading lights", "a leading light (range light): two lights that line up to show the safe course",
          MARKER_NOTE),
    thing("Trail blazes", "a trail blaze, a painted mark or sign that shows the way on a trail", TRAIL_NOTE, True),
    thing("Avalanche warning signs", "an avalanche warning sign", AVALANCHE_NOTE, True),
]
BOATING = [
    thing("Life jackets", "a life jacket (personal flotation device)", LIFE_JACKET_NOTE, True),
    thing("Throw bags", "a throw bag, a bag of floating rope to throw to someone in the water", LIFE_JACKET_NOTE),
    thing("Kayaks", "a kayak", LIFE_JACKET_NOTE),
    thing("Canoes", "a canoe", LIFE_JACKET_NOTE),
    thing("Stand-up paddleboards", "a stand-up paddleboard", LIFE_JACKET_NOTE + " Wear a leash.", True),
    thing("Distress signals", "a distress signal (flares, a signal flag or another sign that a boat needs help)",
          LIFE_JACKET_NOTE + " Flares are hot and bright: never point one at anyone.", True),
    thing("Paddles", "a paddle", LIFE_JACKET_NOTE),
    thing("Boat trailers", "a boat trailer", "Check the hitch, safety chains and lights before towing."),
    thing("Slipways", "a slipway (boat ramp), where boats are launched into the water", LIFE_JACKET_NOTE),
]
FISHING = [
    thing("Fishing rods", "a fishing rod", HOOK_NOTE),
    thing("Fishing reels", "a fishing reel", HOOK_NOTE, True),
    thing("Fishing lure", "a fishing lure, an artificial bait made to look or move like prey", HOOK_NOTE),
    thing("Fishing hooks", "a fishing hook", HOOK_NOTE),
    thing("Fly fishing", "fly fishing, casting a light artificial fly with a long rod and heavy line", HOOK_NOTE),
    thing("Fishing floats", "a fishing float (bobber), which holds the bait up and shows when a fish bites", HOOK_NOTE),
    thing("Fishing line", "fishing line", f"{HOOK_NOTE} Take old line home: it traps birds and animals.", True),
    thing("Ice fishing", "ice fishing", f"{ICE_NOTE} {HOOK_NOTE}", True),
]
GEAR = [
    thing("Hiking boots", "hiking boots", TRAIL_NOTE),
    thing("Trekking poles", "trekking poles", TRAIL_NOTE),
    thing("Sleeping pads", "a sleeping pad, a mat that keeps you warm and off the ground in a tent"),
    thing("Snowshoes", "snowshoes", TRAIL_NOTE),
    thing("Crampons", "crampons, metal spikes strapped to boots for walking on ice", AVALANCHE_NOTE),
    thing("Ice axes", "an ice axe", AVALANCHE_NOTE),
    thing("Climbing harnesses", "a climbing harness", "Climbing: check every knot and buckle, and climb with a "
                                                     "trained partner."),
    # avalanche transceivers are in the wilderness rescue pack (packs/health_life*.py)
    thing("Touring bicycles", "a touring bicycle, built to carry bags on long rides",
          "Cycling: wear a helmet and use lights and reflectors."),
    thing("Handcycles", "a handcycle, a bicycle pedalled with the hands, used in adaptive cycling",
          "Cycling: wear a helmet and use lights and a flag to be seen."),
    thing("Sit-ski", "a sit-ski, a seat on skis used in adaptive (sit) skiing",
          "Winter safety: dress in layers, and watch for signs of frostbite and hypothermia."),
    thing("Panniers (bicycle)", "bicycle panniers, bags that hang on a rack beside the wheel for touring"),
    thing("Bird hides", "a bird hide (blind), a shelter for watching birds without disturbing them"),
]


def build_commons_water_trail_markers(limit):
    """The commons_water_trail_markers pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MARKERS, limit, "odmarkers")


def build_commons_boating_paddling(limit):
    """The commons_boating_paddling pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BOATING, limit, "odboating")


def build_commons_fishing_tackle(limit):
    """The commons_fishing_tackle pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FISHING, limit, "odfishing")


def build_commons_outdoor_gear(limit):
    """The commons_outdoor_gear pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(GEAR, limit, "odgear")


# ----------------------------------------------------------------- Open Images

OUTDOORS_OI = [
    group("What fishing gear is in this picture?",
          {"Fishing lure": "a fishing lure", "Fishing reel": "a fishing reel", "Fishing net": "a fishing net",
           "Fishing bait": "fishing bait", "Fly fishing": "fly fishing"}, HOOK_NOTE),
    group("Is anyone wearing a life jacket?", {"Life jacket": "a life jacket"}, LIFE_JACKET_NOTE),
    group("What trail things are in this picture?",
          {"Trail": "a trail", "Trekking pole": "a trekking pole", "Hiking boot": "a hiking boot",
           "Rock climbing": "rock climbing", "Mountain bike": "a mountain bike", "Bicycle helmet": "a bicycle helmet"},
          TRAIL_NOTE),
    group("What snow sports are in this picture?",
          {"Skiing": "skiing", "Snowboarding": "snowboarding", "Snowshoe": "a snowshoe", "Sled": "a sled"},
          "Winter safety: dress in layers, and watch for signs of frostbite and hypothermia."),
]


def build_open_images_outdoors(limit):
    """open_images_outdoors (see the module docstring); every "yes" answer carries its group's note too."""
    return with_yes_notes(build_oi_gap("open_images_outdoors", OUTDOORS_OI, limit, 9402), OUTDOORS_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
OUTDOORS_PACKS = {
    "commons_water_trail_markers": (build_commons_water_trail_markers, COMMONS_LICENCE.format(
        what="buoy, lateral and cardinal mark, leading light, trail blaze and avalanche sign")),
    "commons_boating_paddling": (build_commons_boating_paddling, COMMONS_LICENCE.format(
        what="life jacket, throw bag, kayak, canoe, paddle, boat trailer and slipway")),
    "commons_fishing_tackle": (build_commons_fishing_tackle, COMMONS_LICENCE.format(
        what="fishing rod, reel, lure, hook, fly fishing, float, line and ice fishing")),
    "commons_outdoor_gear": (build_commons_outdoor_gear, COMMONS_LICENCE.format(
        what="hiking, snow, climbing, avalanche, touring and adaptive cycling and birding gear")),
    "open_images_outdoors": (build_open_images_outdoors, OI_LICENCE),
}
OUTDOORS_LIMITS = {
    "commons_water_trail_markers": 600,    # 9 categories
    "commons_boating_paddling": 800,       # 9 categories; Kayaks and Canoes have most files
    "commons_fishing_tackle": 600,         # 8 categories
    "commons_outdoor_gear": 800,           # 13 categories
    "open_images_outdoors": 1200,          # 16 labels
}
OUTDOORS_COMMONS_KEYS = ("commons_water_trail_markers", "commons_boating_paddling", "commons_fishing_tackle",
                         "commons_outdoor_gear")
OUTDOORS_SPECS = MARKERS + BOATING + FISHING + GEAR


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an outdoor recreation pack builder.")
    parser.add_argument("key", choices=sorted(OUTDOORS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = OUTDOORS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
