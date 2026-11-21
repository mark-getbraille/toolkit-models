"""HARDWARE, TOOLS AND SHOP EQUIPMENT for the Picture Model Training Kit: the collections that cannot be ready-made
packs because of their licence, and the ones that need a sign-up or were looked at and left out. The open ones
(Commons fasteners, door, cabinet and window hardware, building hardware, plumbing and electrical parts, building
materials, hand and trade tools, power tools, shop machines and welding, protective equipment, sewing and food
equipment; Amazon Berkeley Objects' hardware listings; the Smithsonian's historic locks, hinges and tools) are packs in
packs/hardware_packs.py.

As in street_scene_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit
on the user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.
Every licence was checked at its source in November 2026.

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia).

The collections (HARDWARE_SOURCES):
  share-alike
    hardware_commons_sa    Wikimedia Commons files under CC BY-SA or GFDL of the open packs' main categories
                           (screws by kind, head and drive, bolts, nuts, washers, nails, anchors, hinges, locks, door
                           and cabinet hardware, pipe fittings, outlets and switches, hand tools, power tools,
                           woodworking machines, welding, protective equipment). Captions CC0. "What is this?" ->
                           the category's own name ("These are Torx screws: their heads take a Torx (six-point star)
                           screwdriver or bit.").

Needing sign-up (HARDWARE_SIGN_UP) and looked at but not included (HARDWARE_NOT_INCLUDED, with the reason). No open
or non-commercial fastener or tool dataset with its own photos was found on Zenodo (searched November 2026: the one
fastener set, the Mechanical Parts Dataset 2022, is already mechanical_sources.py's mechanical_parts_2022).

    python kit/hardware_sources.py hardware_commons_sa --cap 8      (from the kit folder: a quick check)
"""

import json
import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source

WHAT_Q = "What is this?"
TOOL_Q = "What tool is this, and what is it used for?"


def spec(category, question, answer, deeper=True):
    """(category, question, answer, also one level of its subcategories) for home_sources.commons_sa_items."""
    return (category, question, answer, deeper)


HARDWARE_SA = [
    spec("Countersunk screws", WHAT_Q, "These are countersunk (flat head) screws: their heads sit flush with the "
                                       "surface."),
    spec("Pan head screws", WHAT_Q, "These are pan head screws: low heads with a flat top and rounded edges.", False),
    spec("Phillips screws", WHAT_Q, "These are Phillips screws: they take a Phillips (cross-shaped) screwdriver or "
                                    "bit."),
    spec("Torx", WHAT_Q, "These are Torx screws: they take a Torx (six-point star) screwdriver or bit."),
    spec("Pozidriv", WHAT_Q, "These are Pozidriv screws: a cross with extra small lines, for a Pozidriv bit."),
    spec("Wood screws", WHAT_Q, "These are wood screws: a sharp point and a coarse thread, for wood."),
    spec("Machine screws", WHAT_Q, "These are machine screws: a fine, even thread for a nut or a threaded hole.",
         False),
    spec("Carriage bolts", WHAT_Q, "This is a carriage bolt: a smooth domed head and a square neck that stops it "
                                   "turning in wood.", False),
    spec("Eye bolts", WHAT_Q, "This is an eye bolt: a bolt with a loop for a rope, chain or hook."),
    spec("Lag bolts", WHAT_Q, "This is a lag screw (lag bolt): a heavy wood screw with a hex head."),
    spec("Wing nuts", WHAT_Q, "This is a wing nut: a nut with two wings, tightened by hand."),
    spec("Nyloc nuts", WHAT_Q, "This is a nylon-insert lock nut: the nylon ring stops it working loose.", False),
    spec("Lock washers", WHAT_Q, "These are lock washers: they stop a nut or screw working loose."),
    spec("Plain washers", WHAT_Q, "These are flat washers: they spread the load under a nut or screw head."),
    spec("Metal nails", WHAT_Q, "These are nails: metal pins with a head, driven with a hammer."),
    spec("Wall plugs", WHAT_Q, "These are wall plugs (anchors): pushed into a drilled hole so a screw holds in "
                               "masonry or plasterboard."),
    spec("Hinges", WHAT_Q, "This is a hinge: a joint that lets a door, lid or gate swing."),
    spec("Padlocks", WHAT_Q, "This is a padlock: a lock with a shackle that loops through a hasp or chain."),
    spec("Door handles", WHAT_Q, "This is a door handle."),
    spec("Pipe fittings", WHAT_Q, "This is a pipe fitting: a piece that joins pipes."),
    spec("Light switches", WHAT_Q, "This is a light switch."),
    spec("Hammers", TOOL_Q, "This is a hammer, for driving nails and striking."),
    spec("Wrenches", TOOL_Q, "This is a wrench (spanner), for turning nuts and bolts."),
    spec("Pliers", TOOL_Q, "These are pliers, for gripping, bending and cutting."),
    spec("Power tools", TOOL_Q, "This is a power tool: a tool driven by a motor."),
    spec("Woodworking machines", TOOL_Q, "This is a woodworking machine, for cutting and shaping wood."),
    spec("Welding", TOOL_Q, "This is welding equipment, for joining metal by melting it."),
    spec("Respirators", WHAT_Q, "This is a respirator: a mask that filters the air you breathe. Check its label and "
                                "fit; it protects only when worn correctly."),
]


def prepare_hardware_commons_sa(source, data_dir, work, cap):
    """Commons hardware and tool categories, files under CC BY-SA or GFDL (adults only: workshop photos may show
    people)."""
    items = commons_sa_items(HARDWARE_SA, cap, source.test, "hardware-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
HARDWARE_SOURCES = [
    Source("hardware_commons_sa", "Wikimedia Commons: screws by head and drive, bolts, nuts, washers, nails, anchors, "
                                  "hinges, locks, pipe fittings, switches, hand and power tools, woodworking machines, "
                                  "welding and respirators, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2000, 20, prepare_hardware_commons_sa, "about 400 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
]

# The collections a picture-making model may learn from: none (workshop photos may show people).
HARDWARE_PICTURE_MAKING_OK = set()

HARDWARE_SIGN_UP = {
    "Roboflow Universe fastener, screw, bolt and tool sets":
        "each needs a free account and API key; most are photos re-uploaded from elsewhere under a new licence, so "
        "only a set whose page names its own photos and an open licence would do. Such a set, exported by folder, "
        "can go in the local-file sign-up entry signup_sources.fastener_sets.",
    "Kaggle fastener and tool sets (\"Screws and bolts\", \"Mechanical tools classification\", \"Hand tools\")":
        "behind a free Kaggle login (KAGGLE_USERNAME and KAGGLE_KEY); their licences are often 'unknown' or "
        "copied from web searches. Two checked in November 2026 ('The Fasteners', CC0; 'SortScrews', Apache 2.0, "
        "its makers' own 560 photos) are named in the local-file sign-up entry signup_sources.fastener_sets.",
}

HARDWARE_NOT_INCLUDED = {
    "McMaster-Carr, Grainger, Fastenal and other catalogues":
        "their product pictures and drawings are copyrighted, and their terms forbid copying. Not used.",
    "Open Images V7 hardware and tool classes (Nail, Screw, Bolt, Nut, Drill, Hammer, Wrench, Screwdriver, Chisel, "
    "Ladder, Door handle, Tap, Power plugs and sockets, Light switch)":
        "already asked about by the open everyday_packs and home_packs packs (open_images_objects, "
        "open_images_home). Not repeated.",
    "Cooper Hewitt, Smithsonian Design Museum (door knockers, locks, hinges, escutcheons)":
        "its pictures are not in the Smithsonian open-access bucket (the chsdm folder holds about 1.5 MB of "
        "records), and its own API needs a key. The National Museum of American History's CC0 records are the "
        "open nmah_hardware_tools pack.",
    "Manufacturers' product photos (Simpson Strong-Tie, Kwikset, DeWalt and others)":
        "copyrighted; their manuals and installation instructions are linked in the manuals library instead "
        "(manuals/hardware_tools.py).",
    "NIST and FEMA anchoring and connector photos":
        "fema.gov refuses programs and NIST's photos of connectors are inside reports, not a picture library; "
        "their guides are linked in the manuals library. Not built.",
    "Accessible tools (talking tape measures, tactile levels, click rules)":
        "no Commons category or open picture collection holds them (November 2026); the hand tools pack names any "
        "file whose category says 'talking tape' or 'tactile', and the makers' manuals are in the manuals "
        "category accessible_tools.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one hardware collection.")
    parser.add_argument("key", choices=[s.key for s in HARDWARE_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in HARDWARE_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="hardware-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
