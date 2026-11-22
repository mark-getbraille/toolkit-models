"""Picture packs for SMALL BOATS (the owner's request of 2026-11-22: a small boats collection of books, manuals and
pictures). Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)]. The limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to name small boats by type,
their parts and deck fittings, and boat engines, and to say the boating safety rules that go with them. The
reference books (textbooks/small_boats.py, boat:) carry the handling, rules, building and maintenance.

Answers say only what the Commons category names (with a plain line written here saying what the thing is), never
a guess at a make, size or colour, and every answer ends with the notes that fit (the reference books use the same
rules in BOAT_SAFETY and WORKSHOP_SAFETY):
  BOAT_NOTE      life jacket, weather, float plan, cold water, never under the influence, 911 and VHF channel 16.
  ENGINE_NOTE    carbon monoxide from engines, the engine cut-off switch, and fuel vapour.
  LINE_NOTE      lines under load: keep fingers clear of cleats, fairleads and rowlocks.
  WORKSHOP_NOTE  epoxy, resins, solvents, old lead paint and sanding dust.

The pack (SMALL_BOATS_PACKS):
  commons_small_boats  Wikimedia Commons (CC0, public domain or CC BY files only): boat types (rowboats, dinghies,
                       sailing dinghies, Optimist and Laser dinghies, dories, punts, jon boats, drift boats, racing
                       shells, pontoon boats, inflatable boats and RIBs, catamarans, sailboats, keelboats, motorboats,
                       wooden boats, life rafts), parts and fittings (cleats, rowlocks, oars, fairleads, keels,
                       centreboards, daggerboards, sails, boat hooks, fenders, mooring lines, gunwales), boat engines
                       (marine engines, sterndrives) and boatbuilders at work.

Not repeated here (a self-test checks): the Commons categories of the other packs (Kayaks, Canoes, Paddles,
Stand-up paddleboards, Life jackets, Throw bags, Distress signals, Boat trailers and Slipways of
commons_boating_paddling; Buoys, Daymarks and the other markers of commons_water_trail_markers; Outboard motors of
the mechanical packs; Tillers of the hardware packs, which are garden tillers there; Blocks (sailing) and Shackles of
the hardware packs; Varnish and Caulking of the chemical and home upkeep packs). Commons has no category named
Oarlocks, Boat anchors, Clinker-built boats, Lapstrake boats, Skiffs, Stitch and glue, Bilge pumps, Boat propellers,
Capsized boats, Canoe building, Outboard engines, Navigation lights or Transoms (checked 2026-11-22). What was looked
at and left out is in the kit's small_boats_sources.py.

    python packs/small_boats_packs.py commons_small_boats --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

ASK_WHAT = "What is this?"
BOAT_NOTE = ("Boating safety: wear a life jacket that fits, check the weather and file a float plan before you go; "
             "cold water kills, so dress for the water; never boat under the influence. In an emergency call 911 or "
             "the Coast Guard on VHF channel 16.")
ENGINE_NOTE = ("Engines make carbon monoxide: keep away from exhausts and the swim platform while an engine runs; "
               "wear the engine cut-off lanyard, and run the blower and check for fuel smell before starting an "
               "inboard engine.")
LINE_NOTE = "Lines under load can snap back and trap fingers: keep hands clear of cleats, fairleads and rowlocks."
WORKSHOP_NOTE = ("Workshop safety: epoxy, resins, solvents and old paints (many contain lead) need good ventilation, "
                 "gloves, eye protection and a respirator; wear a dust mask when sanding.")


def thing(category, words, notes, deeper=False):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)])."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}. {notes}")])


BOAT_TYPES = [
    thing("Rowboats", "a rowboat, a small boat moved with oars", BOAT_NOTE),
    thing("Dinghies", "a dinghy, a small open boat, often carried or towed by a larger boat", BOAT_NOTE),
    thing("Sailing dinghies", "a sailing dinghy, a small open sailing boat", BOAT_NOTE),
    thing("Optimist (dinghy)", "an Optimist, a small one-person sailing dinghy used to teach children to sail",
          BOAT_NOTE),
    thing("Laser (dinghy)", "a Laser (ILCA), a one-person racing dinghy", BOAT_NOTE),
    thing("Dories", "a dory, a narrow, flat-bottomed boat with high, flared sides", BOAT_NOTE),
    thing("Punts", "a punt, a flat-bottomed boat with a square bow, usually pushed along with a pole", BOAT_NOTE),
    thing("Jon boats", "a jon boat, a flat-bottomed boat used on rivers and lakes and for fishing", BOAT_NOTE),
    thing("Drift boats", "a drift boat, a rowing boat with a flat bottom and raised ends, used to fish rivers",
          BOAT_NOTE),
    thing("Racing shells", "a racing shell, a long, narrow rowing boat for racing", BOAT_NOTE),
    thing("Pontoon boats", "a pontoon boat, a flat deck carried on two or more floating tubes", f"{BOAT_NOTE} "
                                                                                                 f"{ENGINE_NOTE}"),
    thing("Inflatable boats", "an inflatable boat", BOAT_NOTE),
    thing("Rigid-hulled inflatable boats", "a rigid-hulled inflatable boat (RIB), a solid hull with inflatable tubes "
                                           "around it", f"{BOAT_NOTE} {ENGINE_NOTE}"),
    thing("Catamarans", "a catamaran, a boat with two hulls side by side", BOAT_NOTE),
    thing("Sailboats", "a sailboat (sailing boat)", BOAT_NOTE),
    thing("Keelboats", "a keelboat, a sailing boat with a fixed, weighted keel", BOAT_NOTE),
    thing("Motorboats", "a motorboat", f"{BOAT_NOTE} {ENGINE_NOTE}"),
    thing("Wooden boats", "a wooden boat", BOAT_NOTE),
    thing("Life rafts", "a life raft, an inflatable raft to get into when a boat must be abandoned", BOAT_NOTE),
]
BOAT_PARTS = [
    thing("Cleats", "a cleat, a fitting that a rope (line) is made fast to", LINE_NOTE),
    thing("Rowlocks", "a rowlock (oarlock), the fitting that holds an oar while rowing", LINE_NOTE),
    thing("Oars", "an oar, used to row a boat", BOAT_NOTE),
    thing("Fairleads", "a fairlead, a fitting that leads a line in the right direction", LINE_NOTE),
    thing("Keels", "the keel of a boat, the backbone along the bottom of the hull", BOAT_NOTE),
    thing("Centerboards", "a centreboard, a board that swings down from the hull of a sailing boat to stop it sliding "
                          "sideways", BOAT_NOTE),
    thing("Daggerboards", "a daggerboard, a board pushed straight down through the hull of a sailing boat to stop it "
                          "sliding sideways", BOAT_NOTE),
    thing("Sails", "a sail", BOAT_NOTE),
    thing("Boat hooks", "a boat hook, a pole with a hook for catching a line or a mooring and fending off",
          LINE_NOTE),
    thing("Fenders (nautical)", "a fender, a cushion hung over a boat's side to protect it from a dock or another "
                                "boat", LINE_NOTE),
    thing("Mooring lines", "a mooring line, a rope that ties a boat to a dock or a mooring", LINE_NOTE),
    thing("Gunwale", "a gunwale, the top edge of a boat's side", BOAT_NOTE),
    thing("Sterndrives", "a sterndrive, an inboard engine that turns a drive unit outside the stern", ENGINE_NOTE),
    thing("Marine engines", "a marine engine, an engine made to drive a boat", ENGINE_NOTE),
    thing("Boatbuilders", "boatbuilders at work, building or repairing a boat", WORKSHOP_NOTE),
]


def build_commons_small_boats(limit):
    """The commons_small_boats pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BOAT_TYPES + BOAT_PARTS, limit, "smallboats")


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
SMALL_BOATS_PACKS = {
    "commons_small_boats": (build_commons_small_boats, COMMONS_LICENCE.format(
        what="small boat type (rowboat, dinghy, dory, punt, jon boat, pontoon boat, inflatable, catamaran, sailboat, "
             "keelboat, motorboat, wooden boat, life raft), boat part and fitting, boat engine and boatbuilder")),
}
SMALL_BOATS_LIMITS = {
    "commons_small_boats": 900,            # 34 categories; Sailboats, Motorboats and Rowboats have most files
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
SMALL_BOATS_COMMONS_KEYS = ("commons_small_boats",)
# The Commons category specs of the packs (for the self-test).
SMALL_BOATS_SPECS = BOAT_TYPES + BOAT_PARTS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the small boats pack builder.")
    parser.add_argument("key", choices=sorted(SMALL_BOATS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = SMALL_BOATS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
