"""Picture packs for LIGHT CONSTRUCTION AROUND THE HOME: framing, decks, sheds, fences, concrete and masonry basics,
tiling, insulation, stairs and railings, wheelchair ramps and other home accessibility modifications as they are
built, measuring and layout tools the hardware packs do not ask about, and construction safety (fall protection,
guardrails, trench shoring, scaffold and ladder use as OSHA shows it). Used by build_packs.py in the same way as its
own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more
than one question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit
counts pictures.

The owner's request of 2026-11-22 (with packs/electronics_packs.py and packs/crafts_packs.py; the Commons builder,
build_commons_facts, is electronics_packs'). Home repair and maintenance (plumbing, outlets and panels, drywall,
painting, caulking, roofs and gutters, floors, doors, windows and locks) is another collection's, not this one.

WHAT THE ANSWERS SAY. A fixed sentence from the Commons category a file sits in (a file in "Platform framing" shows
platform framing), with one short plain line on what it is, and the file's own description; never a measurement,
a load rating or a code judgement read from the picture. A dimension is said only where the file's own title states
exactly one in a standard lumber form ("2x4", "2 by 6") as "The file's own words name the lumber size: 2x4."
(stated_lumber). Safety notes follow the drinks distilling warning's style:
  CONCRETE_NOTE   wet concrete, mortar and grout are caustic; cutting them makes silica dust;
  FALL_NOTE       working at height (framing, roofs of sheds, decks being built, scaffolds): fall protection;
  LADDER_LINE     hardware_packs' line, after ladder use;
  RAMP_NOTE       after ramps: the ADA Standards' rule for public buildings (no steeper than 1 in 12, a level landing
                  at the top and bottom, handrails on both sides when it rises more than 6 inches: ADA Standards
                  405.2, 405.7 and 405.8), and that local codes and permits apply at home;
  PERMIT_NOTE     after decks, sheds, fences, stairs and structural work: local building codes and permits;
  POWER_TOOL_NOTE after saws and nailers in use.

The packs (BUILDING_PACKS; Commons files CC0, public domain (OSHA, FEMA and other US government photos among them)
or CC BY, checked file by file; Open Images labels CC BY 4.0 and photos CC BY, CC0 or the Public Domain Mark):
  commons_light_construction   framing (timber framing, roof trusses), decks, sheds, fences by kind, concrete
                               (pouring, formwork, slabs, concrete construction), masonry (bricklaying and
                               bricklayers, stone and dry stone walls, retaining walls, concrete block walls,
                               paving), tiling and tilers, insulation (spray foam, cellulose), stairs (wooden stairs,
                               stringers, handrails, balusters, railings).
  commons_home_access_building ramps and home accessibility modifications as built: wooden ramps, access ramps (only
                               files whose own words say wheelchair or access), grab bars, accessible kitchens
                               (wheelchair ramps, accessible bathrooms and toilets, wheelchair and stair lifts are
                               disability_packs' and not repeated).
  commons_construction_safety  fall protection, guardrails, safety vests, trench shoring (only files whose words name
                               a trench or dig), construction workers and carpenters at work, building permits,
                               layout tools (plumb bobs, chalk lines, speed squares).
  open_images_building         Open Images labels no other pack asks about: fences by kind, sheds, decks, concrete
                               slabs and reinforced concrete, particle board, welded wire mesh, tile flooring,
                               mortar, concrete saws, framing hammers and hard hats.

Not repeated here: hardware_packs (nails, screws, bolts, anchors, joist hangers and connectors, lumber, plywood, OSB,
pressure-treated wood, drywall, hand and power tools, ladders and scaffolding, tape measures, spirit levels, PPE),
things_packs (bricks, concrete blocks, roof tiles, rebar, glass wool, ceramic tiles), disability_packs (ramps, lifts,
grab rails), street_scene_packs (kerbs and sidewalks). What was looked at and left out is in the kit's
building_sources.py.

    python packs/building_packs.py commons_light_construction --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK
from electronics_packs import build_commons_facts

WHAT_Q = "What is this?"

CONCRETE_NOTE = ("Safety: wet concrete, mortar and grout are caustic and can burn skin and eyes: wear gloves, eye "
                 "protection and long sleeves, and wash splashes off with water. Cutting or grinding concrete, brick "
                 "or tile makes silica dust: cut wet, or wear a respirator.")
FALL_NOTE = ("Safety: falls are the leading cause of death in construction. Work at height only with guardrails, a "
             "harness or a properly set-up scaffold, and never alone.")
RAMP_NOTE = ("For public buildings the ADA Standards say a ramp may be no steeper than 1 in 12 (one inch of rise for "
             "every twelve inches of length), with a level landing at the top and bottom and handrails on both sides "
             "when it rises more than 6 inches (sections 405.2, 405.7 and 405.8); at home, local codes and permits "
             "apply.")
PERMIT_NOTE = "Decks, sheds, fences, stairs and structural work usually need a building permit: check local codes."
POWER_TOOL_NOTE = ("Safety: wear eye and hearing protection, keep guards in place, and unplug or remove the battery "
                   "before changing a blade or clearing a jam.")
TRENCH_NOTE = ("Safety: a trench can collapse without warning: never enter one deeper than about 5 feet without "
               "shoring or a trench box.")
ACCESS_WORDS = re.compile(r"\b(wheelchairs?|accessib\w*|disab\w*|handicap\w*|barrier[- ]free|mobility)\b", re.I)
TRENCH_WORDS = re.compile(r"\b(trench\w*|excavat\w*|dig\w*)\b", re.I)
LADDER_LINE = ("Read the ladder's safety labels: they give its weight rating and how to set it up; never stand on the "
               "top step or cap.")


def thing(category, words, note="", deeper=True):
    """A Commons spec: "What is this?" -> "It shows <words>." and the note after."""
    return (category, deeper, [(WHAT_Q, f"It shows {words}." + (f" {note}" if note else ""))])


# A lumber size in a file's own words: "2x4", "2 x 6", "4 by 4", "2×10".
LUMBER = re.compile(r"\b([12468])\s?(?:x|×|by)\s?(2|3|4|6|8|10|12)\b", re.I)


def stated_lumber(title, text):
    """[("What size is the lumber?", "The file's own words name the lumber size: 2x4.")] when the file's title or
    description names exactly one standard lumber size, else []."""
    words = f"{title.split(':', 1)[-1].rsplit('.', 1)[0]} {text or ''}"
    if not re.search(r"\b(lumber|timber|stud|joist|board|post|plank|rafter|beam)s?\b", words, re.I):
        return []
    sizes = {f"{a}x{b}" for a, b in LUMBER.findall(words)}
    return [("What size is the lumber?", f"The file's own words name the lumber size: {sizes.pop()} (a nominal "
             "size: the board is a little smaller than it says).")] if len(sizes) == 1 else []


# ----------------------------------------------------------------- Commons: framing, decks, sheds, fences, masonry

CONSTRUCTION = [
    thing("Timber framing", "timber framing, heavy timbers joined with wooden joints and pegs"),
    thing("Roof trusses", "roof trusses, factory-made triangles of lumber that hold up a roof", FALL_NOTE),
    thing("Wooden decks", "a wooden deck", PERMIT_NOTE),
    thing("Sheds", "a shed", PERMIT_NOTE, deeper=False),
    thing("Garden sheds", "a garden shed", PERMIT_NOTE),
    thing("Wooden fences", "a wooden fence", PERMIT_NOTE),
    thing("Picket fences", "a picket fence, a low fence of evenly spaced upright boards"),
    thing("Chain-link fences", "a chain-link fence, woven steel wire on metal posts"),
    thing("Formwork", "formwork, the moulds that hold wet concrete until it sets", CONCRETE_NOTE),
    thing("Concrete pouring", "concrete being poured", CONCRETE_NOTE),
    thing("Concrete slabs", "a concrete slab"),
    thing("Bricklaying", "bricklaying: laying bricks in mortar", CONCRETE_NOTE),
    thing("Bricklayers", "a bricklayer at work", CONCRETE_NOTE),
    thing("Stone walls", "a stone wall"),
    thing("Dry stone walls", "a dry stone wall, built of stones fitted together without mortar"),
    thing("Retaining walls", "a retaining wall, which holds back the earth of a slope"),
    thing("Concrete block walls", "a concrete block wall", CONCRETE_NOTE),
    thing("Paving stones", "paving stones (pavers)"),
    thing("Tiling", "tiling: tiles being set in adhesive", CONCRETE_NOTE),
    thing("Spray foam insulation", "spray foam insulation", "Safety: spray foam gives off harmful fumes while it is "
                                                            "applied: only with a respirator and ventilation."),
    thing("Cellulose insulation", "cellulose insulation, made from shredded paper"),
    thing("Wooden stairs", "wooden stairs", PERMIT_NOTE),
    thing("Stair stringers", "stair stringers, the notched boards that carry the steps of a staircase"),
    thing("Handrails", "a handrail"),
    thing("Balusters", "balusters, the upright posts that hold up a stair or deck railing"),
    thing("Railings", "a railing", deeper=False),
    thing("Decks (architecture)", "a deck", PERMIT_NOTE, deeper=False),
    thing("Concrete construction", "concrete construction", CONCRETE_NOTE),
    thing("Tilers", "a tiler at work, setting tiles", CONCRETE_NOTE),
]

# ----------------------------------------------------------------- Commons: home accessibility modifications

ACCESS = [
    thing("Wooden ramps", "a wooden ramp", RAMP_NOTE),
    thing("Grab bars", "grab bars, strong rails fixed to the wall (into the studs or with special anchors) to hold "
                       "on to"),
    thing("Accessible kitchens", "an accessible kitchen, with lower counters and space under them for a "
                                 "wheelchair"),
    # Commons' "Ramps" holds road, loading and skate ramps too: only files whose own words say they are for
    # wheelchairs or access.
    thing("Ramps", "a ramp for wheelchair access", RAMP_NOTE, deeper=False) + (ACCESS_WORDS,),
]

# ----------------------------------------------------------------- Commons: construction safety and layout tools

SAFETY = [
    thing("Fall protection", "fall protection", FALL_NOTE),
    thing("Guardrails", "a guardrail", deeper=False),
    thing("Safety vests", "a high-visibility safety vest"),
    thing("Construction workers", "construction workers at work", deeper=False),
    thing("Carpenters", "a carpenter at work", deeper=False),
    thing("Building permits", "a building permit", PERMIT_NOTE),
    thing("Plumb bobs", "a plumb bob, a pointed weight on a string that hangs straight down"),
    thing("Chalk lines", "a chalk line, a chalky string snapped to mark a straight line"),
    thing("Speed squares", "a speed square, a triangle for marking square and angled cuts"),
    # "Shoring" holds the shoring of buildings and ships too: only files whose own words name a trench or dig.
    thing("Shoring", "trench shoring, supports that stop a trench's walls from caving in", TRENCH_NOTE,
          deeper=False) + (TRENCH_WORDS,),
]


def build_commons_light_construction(limit):
    """The commons_light_construction pack (see the module docstring)."""
    return build_commons_facts(CONSTRUCTION, limit, "build", facts=stated_lumber)


def build_commons_home_access_building(limit):
    """The commons_home_access_building pack (see the module docstring)."""
    return build_commons_facts(ACCESS, limit, "homeaccess")


def build_commons_construction_safety(limit):
    """The commons_construction_safety pack (see the module docstring)."""
    return build_commons_facts(SAFETY, limit, "buildsafe")


# ----------------------------------------------------------------- Open Images

BUILDING_OI = [
    group("What kind of fence is this?",
          {"Fence": "a fence", "Picket fence": "a picket fence", "Split-rail fence": "a split-rail fence",
           "Wire fencing": "wire fencing", "Welded wire mesh": "welded wire mesh", }),
    group("What garden or yard building is this?",
          {"Shed": "a shed", "Deck (Building)": "a deck"}, PERMIT_NOTE),
    group("What building materials are in this picture?",
          {"Concrete slab": "a concrete slab", "Reinforced concrete": "reinforced concrete",
           "Particle board": "particle board", "Mortar (Construction)": "mortar", "Tile flooring": "tile flooring",
           "Hardwood": "hardwood", }),
    group("What building tools are in this picture?",
          {"Concrete saw": "a concrete saw",
                                 "Framing hammer": "a framing hammer", }),
    group("What safety gear is in this picture?", {"Hard hat": "a hard hat"}),
]


def build_open_images_building(limit):
    """open_images_building (see the module docstring)."""
    return build_oi_gap("open_images_building", BUILDING_OI, limit, 9302)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain (US government photos "
                   "among them) or CC BY (credited below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
BUILDING_PACKS = {
    "commons_light_construction": (build_commons_light_construction, COMMONS_LICENCE.format(
        what="framing, deck, shed, fence, concrete, masonry, tiling, insulation and stair")),
    "commons_home_access_building": (build_commons_home_access_building, COMMONS_LICENCE.format(
        what="ramp and home accessibility modification")),
    "commons_construction_safety": (build_commons_construction_safety, COMMONS_LICENCE.format(
        what="construction safety, inspection and layout tool")),
    "open_images_building": (build_open_images_building, OI_LICENCE),
}
BUILDING_LIMITS = {
    "commons_light_construction": 2000,      # 29 categories, an even share each
    "commons_home_access_building": 200,     # 4 categories, few open files
    "commons_construction_safety": 500,      # 10 categories
    "open_images_building": 1500,            # 16 labels; fences and sheds have many photos
}
BUILDING_COMMONS_KEYS = ("commons_light_construction", "commons_home_access_building", "commons_construction_safety")
BUILDING_SPECS = CONSTRUCTION + ACCESS + SAFETY


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a building pack builder.")
    parser.add_argument("key", choices=sorted(BUILDING_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = BUILDING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
