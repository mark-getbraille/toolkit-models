"""OUTDOOR RECREATION for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/outdoors_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_water_trail_markers, commons_boating_paddling, commons_fishing_tackle, commons_outdoor_gear
    and open_images_outdoors;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (OUTDOORS_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it, only when the user ticks the matching
choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say, and end with the life jacket, ice, trail, marker, avalanche and
fishing notes that fit, the same words as the packs' (packs/test_outdoors.py checks). Firearms are not in these
collections; the firearms collections keep their own safety line.

Picture-making (OUTDOORS_PICTURE_MAKING_OK): only the Commons gear, tackle and marker collections (things); sources.py
puts every other key in NOT_FOR_PICTURE_MAKING (boats, paddling and Open Images photos show people).
Topics: the gear and tackle are in the home topic, the boats and paddling gear in the machines topic, the buoys,
markers, trail blazes and avalanche signs in the documents topic (signs), and the Open Images outdoor photos in the
home topic.

    python -c "import sources, outdoors_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/outdoors_packs.py.
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

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def gear(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# Categories of packs/outdoors_packs.py, the same answers.
OUTDOORS_SA = [
    gear("Buoys", "a buoy, a floating marker on the water", MARKER_NOTE),
    gear("Mooring buoys", "a mooring buoy, where a boat can tie up", MARKER_NOTE),
    gear("Life jackets", "a life jacket (personal flotation device)", LIFE_JACKET_NOTE, True),
    gear("Kayaks", "a kayak", LIFE_JACKET_NOTE),
    gear("Canoes", "a canoe", LIFE_JACKET_NOTE),
    gear("Fishing rods", "a fishing rod", HOOK_NOTE),
    gear("Fishing reels", "a fishing reel", HOOK_NOTE, True),
    gear("Fishing floats", "a fishing float (bobber), which holds the bait up and shows when a fish bites", HOOK_NOTE),
    gear("Hiking boots", "hiking boots", TRAIL_NOTE),
    gear("Snowshoes", "snowshoes", TRAIL_NOTE),
    gear("Crampons", "crampons, metal spikes strapped to boots for walking on ice", AVALANCHE_NOTE),
    gear("Avalanche transceivers", "an avalanche transceiver (beacon)", AVALANCHE_NOTE),
]

def prepare_outdoors_commons_sa(source, data_dir, work, cap):
    """Commons buoy, life jacket, kayak, canoe, fishing and hiking gear categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(OUTDOORS_SA, cap, source.test, "outdoors-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)

OUTDOORS_SOURCES = [
    Source("commons_water_trail_markers", "Buoys, lateral and cardinal marks, mooring buoys, leading lights, trail "
                                          "blazes and avalanche warning signs (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 130 MB"),
    Source("commons_boating_paddling", "Life jackets, throw bags, kayaks, canoes, paddles, boat trailers and boat "
                                       "ramps, with life jacket notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("commons_fishing_tackle", "Fishing rods, reels, lures, hooks, fly fishing, floats, line and ice fishing "
                                     "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 5, prepare_pack, "about 130 MB"),
    Source("commons_outdoor_gear", "Hiking boots, trekking poles, sleeping pads, snowshoes, crampons, ice axes, "
                                   "climbing harnesses, avalanche transceivers, touring bicycles and panniers, "
                                   "handcycles, sit-skis and bird hides (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 170 MB"),
    Source("open_images_outdoors", "Fishing lures, reels, nets and bait, fly fishing, life jackets, trails, hiking "
                                   "and climbing, mountain bikes and snow sports (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1200, 15, prepare_pack, "about 250 MB"),
    Source("outdoors_commons_sa", "Wikimedia Commons: buoys, life jackets, kayaks, canoes, fishing rods, reels and "
                                  "floats, hiking boots, snowshoes, crampons and avalanche transceivers, files under CC "
                                  "BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 10, prepare_outdoors_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons markers, tackle and gear (things); never the
# boating and paddling or Open Images collections, which show people.
OUTDOORS_PICTURE_MAKING_OK = {"commons_water_trail_markers", "commons_fishing_tackle", "commons_outdoor_gear",
                              "outdoors_commons_sa"}

OUTDOORS_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Lifebuoys, Carabiners and Tandem bicycles: not asked twice.",
    "Commons categories that do not exist or hold no files (November 2026)": "Daybeacons, Personal flotation devices, "
        "Stand up paddle boards, Boat anchors, Bilge pumps, Distress flares, Spinning, Baitcasting and Fly reels, "
        "Artificial flies, Fishing sinkers, Tackle boxes, Landing nets, "
        "Adaptive skiing, Blaze orange, Tree stands, Trail markers, Cairns and Accessible trails; the packs use Daymarks, "
        "Stand-up paddleboards, Distress signals, Fishing lure, Fishing hooks, Sit-ski and Panniers (bicycle).",
    "Fish and bird species": "The species packs already name fish and birds (noaa_fisheries_species, na_herps_fish, "
                             "na_birds, inaturalist); this collection names gear only.",
    "Hunting and firearms pictures": "Guns, bows and hunting with weapons are left to the firearms collections and "
                                     "their safety line; no weapons are in these packs.",
    "USCG navigation aid pictures (navcen.uscg.gov)": "Public domain, but the Navigation Center refuses programs "
                                                      "(403, robots.txt included, 2026-11-22); Commons holds copies.",
    "NPS and USFS photo galleries": "Their public-domain photos copied to Commons are reached through the Commons "
                                    "categories; npgallery is already its own collection (npgallery).",
    "Open Images labels asked elsewhere": "Kayak, Canoe, Paddle, Personal flotation device, Fishing rod, Fishing, "
        "Binoculars, Compass, Hiking, Climbing, Ski, Snowboard, Ice skate, Tent, Boat and others: asked by other packs.",
    "Roboflow Universe fishing and buoy sets": "Roboflow Universe's robots.txt disallows the dataset download pages "
                                               "(see gaps_sources.py).",
}

def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the outdoor recreation share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in OUTDOORS_SOURCES if s.key == "outdoors_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="outdoors-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
