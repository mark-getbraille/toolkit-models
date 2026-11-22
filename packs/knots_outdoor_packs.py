"""Picture packs for KNOTS, ROPE AND PRACTICAL OUTDOOR SKILLS (the owner's request of 2026-11-22). Used by
build_packs.py in the same way as its own PACKS (build_<key>(limit) returns [(file name, JPEG bytes or None, row)]).

Why: the owner wants the picture describer to name a knot in a photo or diagram (bowline, clove hitch, square knot,
sheet bend, figure eight, taut-line hitch, trucker's hitch and many more), to say what it is used for, and to name
the outdoor tools that go with rope work: compasses, axes and hatchets, crosscut and bow saws, sharpening stones and
small shelters.

Answers say only what the source says: the knot's name is the Commons category's own name (each category holds only
that knot), and the use given is the knot's standard use as the public-domain knot books in the library describe it
(Verrill's Knots, Splices and Rope Work, the Army's FM 5-125). No brand is named. Knots that hold people or loads,
and the cutting tools, end with ROPE_NOTE or TOOL_NOTE (the same words as the kit's practical_sources.py).

The packs (KNOTS_OUTDOOR_PACKS):
  commons_knots            Wikimedia Commons (CC0, public domain or CC BY files only): about forty-five knots by
                           name (loops, hitches, bends, stoppers, binding knots, splices and whippings), each in its
                           own Commons category, and (since 2026-11-22) lashings (only files whose words name one),
                           the diamond hitch, seizings, the long splice, the sailmaker's whipping and wall and crown
                           knots.
  commons_outdoor_skills   Commons: baseplate, lensatic and magnetic compasses; felling axes and hatchets; crosscut
                           and bow saws; whetstones and knife sharpeners; bivouac shelters; and (since 2026-11-22)
                           marlinespikes, fids, ropewalks and rope making (only files whose words name rope).
  open_images_knots_outdoor Open Images V7 (labels CC BY 4.0; photos CC BY, CC0 or the Public Domain Mark): wire
                           rope, carabiners, tarpaulins, saws (bow saw, crosscut saw, two-man saw,
                           hatchet) and sharpening (sharpening stone, knife sharpener). No label is asked twice
                           (packs/test_practical.py checks).

Not repeated here: hardware_packs (the Commons Ropes and Knots categories and their first level: rope as hardware),
home_packs (Open Images Axe), another pack's Commons Splitting mauls, the textile crafts pack (Open Images Knot),
the outings pack (Open Images Compass), the outdoor cooking packs (campfires) and the preparedness packs (survival
kits, water). Hangman's nooses and other knots in BDSM or punishment categories are left out. Diagrams under CC BY-SA are in the kit's share-alike collection knots_commons_sa.

    python packs/knots_outdoor_packs.py commons_knots --limit 8
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap
from outdoor_cooking_packs import thing, with_yes_notes

ROPE_NOTE = ("Rope safety: a knot weakens a rope, and some knots slip or jam; for climbing, lifting or rescue use "
             "rated gear and learn the knot from a qualified instructor, and check a rope for cuts, wear and "
             "stiffness before trusting it.")
TOOL_NOTE = ("Sharp tools: cut away from your body, keep people at least two tool lengths away, wear eye protection "
             "and sturdy boots, and keep the blade covered when it is not in use.")
ASK_KNOT = "What knot is this?"


def knot(category, words, notes="", deeper=False):
    """A Commons spec for one knot: (category, deeper, [("What knot is this?", "This is <words>." and the notes)])."""
    return (category, deeper, [(ASK_KNOT, f"This is {words}." + (f" {notes}" if notes else ""))])


# ----------------------------------------------------------------- Commons: knots by name

KNOTS = [
    # loops
    knot("Bowlines", "a bowline, a fixed loop at the end of a rope that does not slip and is easy to untie",
         ROPE_NOTE),
    knot("Bowline on a bight", "a bowline on a bight, a double fixed loop tied in the middle of a rope", ROPE_NOTE),
    knot("Figure-eight loops", "a figure-eight loop (figure eight on a bight), a strong fixed loop used in climbing",
         ROPE_NOTE),
    knot("Alpine butterfly knots", "an alpine butterfly, a fixed loop in the middle of a rope that can be pulled in "
                                   "any direction", ROPE_NOTE),
    knot("Overhand loop", "an overhand loop, a simple fixed loop that is hard to untie after a load"),
    # hitches
    knot("Clove hitches", "a clove hitch, two turns round a post or rail; quick to tie, but it can slip if the pull "
                          "changes direction"),
    knot("Half hitches", "a half hitch; two half hitches fasten a rope to a post or ring"),
    knot("Taut-line hitches", "a taut-line hitch, an adjustable loop that holds under tension, used for tent guy "
                              "lines"),
    knot("Trucker's hitches", "a trucker's hitch, which pulls a rope tight with a loop that works like a pulley, used "
                              "for tying down loads", ROPE_NOTE),
    knot("Timber hitches", "a timber hitch, for dragging or lifting a log or pole"),
    knot("Rolling hitches", "a rolling hitch, which grips a pole or another rope against a pull along it"),
    knot("Cow hitches", "a cow hitch (lark's head), a quick loop round a ring, post or another rope"),
    knot("Prusik knots", "a Prusik knot, a loop of cord wrapped round a rope that grips when loaded and slides when "
                         "not, used in climbing and rescue", ROPE_NOTE),
    knot("Munter hitches", "a Munter hitch, a friction hitch on a carabiner used to lower or belay a climber",
         ROPE_NOTE),
    knot("Cleat knots", "a cleat hitch, the way a rope is made fast to a cleat on a dock or boat"),
    knot("Anchor bends", "an anchor bend, which ties a rope to a ring or an anchor"),
    knot("Marline hitches", "a marline hitch, a row of hitches that binds a rolled bundle such as a tarp"),
    # bends (joining two ropes)
    knot("Square knots", "a square knot (reef knot), which ties the two ends of one cord round a bundle; it is not "
                         "safe for joining two ropes that will carry weight"),
    knot("Granny knots", "a granny knot, a square knot tied wrongly, which slips or jams"),
    knot("Sheet bends", "a sheet bend, which joins two ropes, even of different thickness"),
    knot("Double sheet bends", "a double sheet bend, a more secure sheet bend with an extra turn"),
    knot("Fisherman's knots", "a fisherman's knot, which joins two lines with two overhand knots"),
    knot("Double fisherman's knots", "a double fisherman's knot, used to join the ends of climbing cord into a loop",
         ROPE_NOTE),
    knot("Water knots", "a water knot (ring bend), which joins the ends of flat webbing", ROPE_NOTE),
    knot("Carrick bends", "a carrick bend, which joins two heavy ropes"),
    knot("Zeppelin bends", "a zeppelin bend, a secure knot that joins two ropes and stays easy to untie"),
    # stoppers and binding knots
    knot("Overhand knots", "an overhand knot, the simplest knot, often used as a stopper"),
    knot("Double overhand knots", "a double overhand knot, a bulkier stopper knot"),
    knot("Figure-eight knots", "a figure-eight knot, a stopper knot that keeps a rope's end from running through a "
                               "hole or pulley"),
    knot("Constrictor knots", "a constrictor knot, a binding knot that grips very tightly, used to close a bag or "
                              "hold a rope before cutting it"),
    knot("Monkey's fists", "a monkey's fist, a ball-shaped knot that weights the end of a throwing line"),
    knot("Sheepshank", "a sheepshank, which shortens a rope; it can fall apart when the rope goes slack"),
    # splices and whippings
    knot("Eye splices", "an eye splice, a lasting loop made by weaving a rope's strands back into itself"),
    knot("Short splices", "a short splice, which joins two ropes by weaving their strands together"),
    knot("Back splices", "a back splice, which stops a rope's end from unravelling"),
    knot("Common whippings", "a common whipping, thin cord bound round a rope's end so it does not fray"),
    # lashings, seizings and more splices (added 2026-11-22 with the military and bushcraft books; the Commons has
    # no separate categories for the square, diagonal, shear or tripod lashings, so their files are in Lashing knots)
    # Lashing knots also holds baskets, museum pieces and book pages, so only files whose own words name a lashing
    # are taken (Kreuzbund, Bund and amarra are the German and Spanish words). Spanish windlasses is not used: it
    # also holds surgical tourniquets.
    knot("Lashing knots", "a lashing, rope or cord wound tightly round poles or other things to bind them together, "
                          "as in the square, diagonal, shear and tripod lashings used for camp structures")
    + (re.compile(r"lash|bund\b|kreuzbund|amarra|brelage|sjorring|surliure", re.I),),
    knot("Diamond hitches", "a diamond hitch, the hitch packers use to tie a load onto a pack saddle"),
    knot("Seizings", "a seizing, turns of thin line that bind two ropes, or two parts of one rope, together",
         deeper=True),
    knot("Long splices", "a long splice, which joins two ropes without making them much thicker, so the rope still "
                         "runs through a block"),
    knot("Sailmaker's whippings", "a sailmaker's whipping, a lasting whipping stitched through a rope's end"),
    knot("Wall and crown knots", "a wall knot or a crown knot, the knots worked with a rope's own strands that "
                                 "start many stopper knots and the back splice"),
]


def build_commons_knots(limit):
    """The commons_knots pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(KNOTS, limit, "knots")


# ----------------------------------------------------------------- Commons: outdoor skills

COMPASS_NOTE = ("Navigation: a compass needle points to magnetic north, which differs from true north by the "
                "declination printed on the map; keep it away from metal and magnets when taking a bearing.")
OUTDOOR_SKILLS = [
    thing("Baseplate compasses", "a baseplate (orienteering) compass, a compass on a clear plate with a direction "
                                 "arrow, used with a map", COMPASS_NOTE),
    thing("Lensatic compasses", "a lensatic compass, a folding compass with a sighting lens", COMPASS_NOTE),
    thing("Magnetic compasses", "a magnetic compass", COMPASS_NOTE),
    thing("Felling axes", "a felling axe, for cutting down trees and chopping logs", TOOL_NOTE),
    thing("Hatchets", "a hatchet, a small one-handed axe", TOOL_NOTE),
    thing("Crosscut saws", "a crosscut saw, a long saw for cutting across logs, often worked by two people",
          TOOL_NOTE),
    thing("Bow saws", "a bow saw, a saw with a thin blade held tight in a bent frame", TOOL_NOTE),
    thing("Whetstones", "a whetstone (sharpening stone) for sharpening blades", TOOL_NOTE),
    thing("Knife sharpeners", "a knife sharpener", TOOL_NOTE),
    thing("Bivouac shelters", "a bivouac shelter, a small simple shelter for a night outdoors"),
    # rope tools and rope making (added 2026-11-22)
    thing("Marline spikes", "a marlinespike, a pointed tool for opening the strands of a rope when splicing and for "
                            "loosening knots"),
    thing("Fids", "a fid, a tapered tool for opening a rope's strands or passing braided rope through itself when "
                  "splicing"),
    thing("Ropewalks", "a ropewalk, a long building or path where rope was made by twisting strands along its "
                       "length"),
    thing("Ropemaking", "rope making: fibres or yarns being twisted into rope", pattern=re.compile(
        r"rope|seil|corde|touw|cordage|reep|twist|yarn", re.I)),
]


def build_commons_outdoor_skills(limit):
    """The commons_outdoor_skills pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(OUTDOOR_SKILLS, limit, "outskills")


KNOTS_OI = [
    group("What rope or knot is in this picture?",
          {"Wire rope": "a wire rope", "Carabiner": "a carabiner"}, ROPE_NOTE),
    group("Is there a tarp in this picture?", {"Tarpaulin": "a tarpaulin (tarp)"}),
    group("What cutting tools are in this picture?",
          {"Bow saw": "a bow saw", "Crosscut saw": "a crosscut saw", "Two-man saw": "a two-man saw",
           "Hatchet": "a hatchet"}, TOOL_NOTE),
    group("What sharpening tools are in this picture?",
          {"Sharpening stone": "a sharpening stone", "Knife sharpener": "a knife sharpener"}, TOOL_NOTE),
]


def build_open_images_knots_outdoor(limit):
    """open_images_knots_outdoor (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_knots_outdoor", KNOTS_OI, limit, 9404), KNOTS_OI)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
KNOTS_OUTDOOR_PACKS = {
    "commons_knots": (build_commons_knots, COMMONS_LICENCE.format(what="knot (by name), lashing, seizing, splice and "
                                                                        "whipping")),
    "commons_outdoor_skills": (build_commons_outdoor_skills, COMMONS_LICENCE.format(
        what="compass, axe, hatchet, crosscut and bow saw, whetstone, knife sharpener, bivouac shelter, marlinespike, "
             "fid, ropewalk and rope making")),
    "open_images_knots_outdoor": (build_open_images_knots_outdoor, OI_LICENCE),
}
KNOTS_OUTDOOR_LIMITS = {
    "commons_knots": 1500,               # 43 knots and lashings, most with 10 to 120 files
    "commons_outdoor_skills": 700,       # 14 categories
    "open_images_knots_outdoor": 800,    # 9 labels
}
KNOTS_OUTDOOR_COMMONS_KEYS = ("commons_knots", "commons_outdoor_skills")
KNOTS_OUTDOOR_SPECS = KNOTS + OUTDOOR_SKILLS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(KNOTS_OUTDOOR_PACKS, "Try a knots and outdoor skills pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
