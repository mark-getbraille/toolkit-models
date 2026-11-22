"""SMALL BOATS for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made pack built in packs/small_boats_packs.py (group "permissive"; the kit downloads it with
    prepare_pack): commons_small_boats;
  - the sources looked at for these subjects and left out, with the reason (SMALL_BOATS_NOT_INCLUDED).

As in outdoors_sources.py, nothing here is re-shared by the kit's makers: the pack is downloaded by the kit on the
user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Wikimedia Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category names, with a plain line saying what the thing is, and end with the
boating, engine, line or workshop note that fits (life jacket, weather, float plan, cold water, never under the
influence, carbon monoxide, epoxy and solvents), the same words as the pack's (packs/test_small_boats.py checks).

Picture-making (SMALL_BOATS_PICTURE_MAKING_OK): none (boat photos often show the people aboard, and the
boatbuilders' photos show people at work: describing only).
Topics: the transport topic (Transport and travel), beside the boating and paddling pack.

    python -c "import sources, small_boats_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

# The notes, word for word as in packs/small_boats_packs.py.
BOAT_NOTE = ("Boating safety: wear a life jacket that fits, check the weather and file a float plan before you go; "
             "cold water kills, so dress for the water; never boat under the influence. In an emergency call 911 or "
             "the Coast Guard on VHF channel 16.")
ENGINE_NOTE = ("Engines make carbon monoxide: keep away from exhausts and the swim platform while an engine runs; "
               "wear the engine cut-off lanyard, and run the blower and check for fuel smell before starting an "
               "inboard engine.")
LINE_NOTE = "Lines under load can snap back and trap fingers: keep hands clear of cleats, fairleads and rowlocks."
WORKSHOP_NOTE = ("Workshop safety: epoxy, resins, solvents and old paints (many contain lead) need good ventilation, "
                 "gloves, eye protection and a respirator; wear a dust mask when sanding.")

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

SMALL_BOATS_SOURCES = [
    Source("commons_small_boats", "Small boats by type (rowboats, dinghies, dories, punts, jon boats, pontoon boats, "
                                  "inflatables, catamarans, sailboats, keelboats, motorboats, wooden boats, life "
                                  "rafts), their parts and fittings (cleats, rowlocks, oars, fairleads, keels, "
                                  "centreboards, sails, fenders, mooring lines) and boat engines, with boating "
                                  "safety notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
]
SMALL_BOATS_PICTURE_MAKING_OK = set()
SMALL_BOATS_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Kayaks, Canoes, Paddles, Stand-up paddleboards, Life "
        "jackets, Throw bags, Distress signals, Boat trailers and Slipways (outdoors_sources.py); buoys and markers "
        "(commons_water_trail_markers); Outboard motors (mechanical packs); Tillers, Blocks (sailing) and Shackles "
        "(hardware packs); Varnish and Caulking (chemical and home upkeep packs).",
    "Commons categories that do not exist (2026-11-22)": "Oarlocks, Boat anchors, Clinker-built boats, Lapstrake "
        "boats, Skiffs, Stitch and glue, Bilge pumps, Boat propellers, Capsized boats, Canoe building, Outboard "
        "engines, Navigation lights, Marine compasses, Transoms, Centreboards (Centerboards is used), Rowing shells "
        "(Racing shells is used).",
    "Commons categories with too few or mixed files": "Rowing boats and Boatbuilding (empty), Bass boats (2 files), "
        "Marinas and Boathouses (places more than boats), Rudders (4 files).",
    "Open Images boat labels": "Boat, Canoe, Kayak, Sailboat, Jet ski, Gondola and Barge are asked by other packs.",
    "NOAA, USCG and NPS photo galleries": "Their public-domain photos copied to Commons are reached through the "
        "Commons categories; the Coast Guard's own sites refuse programs (403).",
    "Boat makers' and boatbuilding schools' photos": "copyright; not used.",
}
