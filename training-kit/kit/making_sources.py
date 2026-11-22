"""HOME MANUFACTURING AND MAKING for the Picture Model Training Kit (the owner's request of 2026-11-22: 3D printing,
cutting machines and heat presses, laser cutters and engravers, CNC, tabletop lathes and mills, moulding and casting,
and electronics fabrication). This file lists:
  - the ready-made packs built in packs/making_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_3d_printing, commons_cutting_lasers, commons_cnc_machining, commons_moulding_casting,
    commons_pcb_fabrication and open_images_making;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (MAKING_NOT_INCLUDED);
  - which topic add-ons hold them (MAKING_TOPICS).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked), and every
answer about a machine ends with the safety notes that fit it: hot 3D printer nozzles and beds, resin skin contact,
laser eye safety and fire, fumes (never cut or engrave PVC or vinyl: chlorine gas), rotating machinery, sharp blades,
heat presses, molten metal and soldering. The notes are the same words as the packs' (packs/test_making.py checks).

Picture-making (MAKING_PICTURE_MAKING_OK): the Commons machine, tooling and circuit board collections (things);
sources.py puts every other key in NOT_FOR_PICTURE_MAKING (makerspaces, blacksmithing and the Open Images photos
show people). Topics: no topic add-on of its own; everything is in "machines" (Machines, tools and devices) and
"home" (Home and household), the circuit board fabrication pack also in "power" (Power and electrical), and the
cutting machine pack (vinyl cutters, Cricut-style cutting machines, heat presses, screen printing and machine
embroidery, which are mostly craft use; its lasers and engravers stay in machines and home) also in "crafts" (Arts and
crafts). 3D printing, CNC, moulding and casting stay with machines and home.

    python -c "import sources, making_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The safety notes, word for word as in packs/making_packs.py.
PRINTER_NOTE = ("3D printer safety: the nozzle and the heated bed are hot enough to burn and stay hot after printing; "
                "keep a running printer where it can be checked, on a surface that does not burn, with a smoke alarm "
                "nearby, and print with fresh air (melting plastic gives off fine particles and fumes, ABS and ASA "
                "more than PLA).")
RESIN_NOTE = ("Resin safety: liquid (uncured) resin can cause skin allergies and burns: wear nitrile gloves and eye "
              "protection, work with ventilation, never touch it with bare skin, keep it from children and pets, and "
              "cure leftover resin and used washing liquid in sunlight or UV light before throwing them away as "
              "local rules say.")
LASER_NOTE = ("Laser safety: never look into the beam or its reflection; wear eye protection rated for the laser's "
              "wavelength; open-frame hobby lasers are usually Class 4, which can blind in an instant and set things "
              "on fire, and an enclosed machine is safe only with its lid shut; never leave a running laser, and keep "
              "a fire extinguisher close.")
FUME_NOTE = ("Fumes: run the exhaust or fume extractor and vent it outdoors; never cut or engrave PVC, vinyl or "
             "other plastics that contain chlorine (they give off chlorine gas that harms you and ruins the "
             "machine), nor materials you cannot identify.")
MACHINE_NOTE = ("Rotating machinery: wear safety glasses; no gloves, loose sleeves, jewellery or untied long hair "
                "near spinning parts; take the chuck key out before starting, keep the guards on, and stop the "
                "machine before measuring or clearing chips.")
BLADE_NOTE = ("Blades: cutting-machine and weeding blades are very sharp: change them with care and keep fingers "
              "clear of the carriage while it moves.")
CUT_NOTE = "Sharp edges: cutting tools are sharp: cut away from yourself and keep your other hand behind the blade."
HEAT_NOTE = ("Heat press: the plate is hot enough to burn: keep hands clear when closing it, use heat-resistant "
             "gloves, and never leave it switched on alone.")
CASTING_NOTE = ("Casting: molten metal burns and can explode when it meets water or a damp mould: keep everything "
                "dry and wear face, foot and body protection; resins and silicone need gloves, eye protection and "
                "ventilation.")
SOLDER_NOTE = ("Soldering: the iron and reflowed boards are hot enough to burn; use a fume extractor or fresh air, "
               "work on a surface that does not burn, and wash your hands after handling solder.")

FORMING_NOTE = ("Hot plastic: the heater and the softened sheet are hot enough to burn: use heat-resistant gloves and "
                "never leave the heater on alone.")
PLASMA_NOTE = ("Plasma cutting: wear a welding helmet or the lens shade the cutter's manual says, leather gloves and "
               "clothing that does not melt; keep anything that burns away, and ventilate.")
FORGE_NOTE = ("Hot metal: it burns and looks the same as cold, so treat all metal at the forge or anvil as hot; wear "
              "safety glasses, leather gloves, apron and boots, and keep water and a fire extinguisher close.")

LASER_NOTES = f"{LASER_NOTE} {FUME_NOTE}"

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


# The main categories of packs/making_packs.py whose files need no word filter (the share-alike entry has none):
# printers, extruders, filament, failed prints, OpenSCAD, vinyl cutters, laser cutting and engraving, CNC, lathes and
# their chucks, milling tools, moulding and circuit board making. The answers are the packs' own words.
MAKING_SA = [
    gear("3D printers", "a 3D printer, a machine that builds an object layer by layer from a computer model",
         PRINTER_NOTE),
    gear("RepRap", "a RepRap, an open-source 3D printer designed to print many of its own parts", PRINTER_NOTE, True),
    gear("Prusa i3", "a Prusa i3, an open-source 3D printer design of the RepRap family", PRINTER_NOTE, True),
    gear("3D printer extruders", "a 3D printer extruder, the part that pushes the filament into the hot nozzle",
         PRINTER_NOTE, True),
    gear("3D printing filament", "3D printing filament: plastic wire on a spool, fed into the printer; keep it dry "
                                 "in a sealed bag or box", "", True),
    gear("Failed 3D prints", "a failed 3D print", PRINTER_NOTE),
    gear("OpenSCAD", "OpenSCAD, a free program in which you design 3D models by writing code, which suits screen "
                     "reader users, or a model made with it", deeper=True),
    gear("Vinyl cutters", "a vinyl cutter, a computer-driven machine whose small blade cuts shapes and letters from "
                          "vinyl or paper", BLADE_NOTE),
    gear("Laser cutting", "laser cutting: a laser beam cuts wood, acrylic, paper or metal along a path", LASER_NOTES,
         True),
    gear("Laser engraving", "laser engraving: a laser marks a picture or text into a surface", LASER_NOTES, True),
    gear("Computer numerical control", "a CNC (computer numerical control) machine, which moves its tool along a "
                                       "path written in G-code", MACHINE_NOTE),
    gear("Metalworking lathes", "a metalworking lathe: it spins metal work against a cutting tool", MACHINE_NOTE),
    gear("Lathe chucks", "a lathe chuck, the jaws that grip the work on a lathe", MACHINE_NOTE, True),
    gear("Milling tools", "a milling cutter, such as an end mill, for a milling machine or CNC", MACHINE_NOTE, True),
    gear("Injection moulding", "injection moulding: melted plastic forced into a mould", FORMING_NOTE),
    gear("Vacuum forming", "vacuum forming: a heated plastic sheet sucked down over a shape", FORMING_NOTE),
    gear("Printed circuit board manufacturing", "printed circuit board (PCB) manufacturing", SOLDER_NOTE),
]


def prepare_making_commons_sa(source, data_dir, work, cap):
    """Commons 3D printer, laser, CNC, lathe, moulding and circuit board categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(MAKING_SA, cap, source.test, "making-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

MAKING_SOURCES = [
    Source("commons_3d_printing", "3D printing: FDM and resin printers (RepRap, Prusa i3, MakerBot, Ultimaker, Ender "
                                  "3, Bambu Lab, Formlabs), extruders, filament, resin, 3D prints and failed prints, "
                                  "3D scanning and 3D design (OpenSCAD, FreeCAD, Blender), with hot-nozzle and resin "
                                  "safety notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 260 MB"),
    Source("commons_cutting_lasers", "Cutting machines and lasers: vinyl cutters, plotters, heat presses, screen "
                                     "printing, machine embroidery, laser cutting and engraving, CO2 and fibre "
                                     "lasers, laser goggles and warning signs, engraving machines and plasma "
                                     "cutting, with laser eye-safety and fume notes (Wikimedia Commons, ready-made "
                                     "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_cnc_machining", "CNC and small machining: CNC machines, metalworking and watchmaker's lathes, "
                                    "chucks, tailstocks, steady rests, lathe tools, knurling, milling cutters, "
                                    "machine vises, rotary tables, indexing heads, cutter grinders and woodturning, "
                                    "with rotating-machinery notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_moulding_casting", "Moulding, casting and makerspaces: injection moulding, thermoforming and "
                                       "vacuum forming, moulds, sand and investment casting, blacksmithing, "
                                       "makerspaces, hackerspaces and fab labs (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 700, 10, prepare_pack, "about 150 MB"),
    Source("commons_pcb_fabrication", "Electronics fabrication: printed circuit board manufacturing, PCB milling, "
                                      "solder-paste stencils and reflow soldering (Wikimedia Commons, ready-made "
                                      "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 120, 5, prepare_pack, "about 25 MB"),
    Source("open_images_making", "Machine tools, metal lathes, cutter grinders, drill presses, bandsaws, vises, "
                                 "calipers, rotary tools, routers, workshops and toolrooms, cutting mats, casting and "
                                 "resin, lasers, anvils, forges, welding helmets, soldering irons, screen printing "
                                 "and 3D modelling (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 320 MB"),
    Source("making_commons_sa", "Wikimedia Commons: 3D printers, RepRap and Prusa i3, extruders, filament, failed "
                                "prints, OpenSCAD, vinyl cutters, laser cutting and engraving, CNC, metalworking "
                                "lathes and chucks, milling cutters, injection moulding, vacuum forming and circuit "
                                "board making, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 700, 10, prepare_making_commons_sa,
           "about 150 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons machines, tooling and circuit boards (things);
# never the moulding and casting pack (makerspaces and blacksmiths at work) or the Open Images photos, which show
# people.
MAKING_PICTURE_MAKING_OK = {"commons_3d_printing", "commons_cutting_lasers", "commons_cnc_machining",
                            "commons_pcb_fabrication", "making_commons_sa"}

# Which topic add-ons hold each collection (topics.py lists the same keys; packs/test_making.py checks). No topic of
# its own: the owner's rule is to add a topic only when needed.
MAKING_TOPICS = {
    "machines": tuple(s.key for s in MAKING_SOURCES),
    "home": tuple(s.key for s in MAKING_SOURCES),
    "power": ("commons_pcb_fabrication",),
    # vinyl cutters, cutting machines, heat presses, screen printing and machine embroidery: mostly craft use
    "crafts": ("commons_cutting_lasers",),
}

MAKING_NOT_INCLUDED = {
    "Commons categories already used by other packs": "CNC routers, Laser cutters, Milling machines, Drill presses, "
        "Router bits, Drill chucks, Anvils, Forges, Taps and dies, Surface grinders, Bench grinders, Plasma cutters "
        "and Dremel (hardware_packs), Lathes (land_industry_packs), Milling machines and Machine shops "
        "(work_farm_mech_packs), Embroidery machines (textile_crafts_packs), Resin casting and Lost-wax casting "
        "(crafts_packs, commons_models_resin), Breadboards and Raspberry Pi (things_packs), Stepper motors "
        "(mechanical_packs), the soldering tools (electronics_packs) and Tactile graphics and tactile models "
        "(vision_packs): not asked twice.",
    "Commons categories that do not exist under the names tried (November 2026)": "Heat presses, Heat transfer vinyl, "
        "Dye-sublimation printing, Cricut, Silhouette Cameo, Cutting plotters, Laser engravers, Glowforge, Laser "
        "safety glasses, CNC machines, CNC milling machines, Desktop CNC, End mills, Shapeoko, X-Carve, GRBL, "
        "LinuxCNC, Mini lathes, Sherline, Taig lathe, Unimat, Collets, Threading (manufacturing), Hotends, Heated "
        "beds, Resin 3D printers, Elegoo, PLA filament, G-code, PrusaSlicer, Ultimaker Cura, 3D printed tactile "
        "models, Mold making, Silicone molds, Pick-and-place machines, Solder paste and Reflow ovens; Tactile models, "
        "Injection molding and Band saws exist but hold no files. The packs use the categories that hold files.",
    "Commons Tinkercad, Pantographs, Lasers, Casting, Workshops, Embroidery and Engraving": "Tinkercad is a company's "
        "web program (its screenshots are left out: the owner's rule makes it link-only); Pantographs are mostly "
        "train current collectors; Lasers, Casting, Workshops, Embroidery and Engraving are too general (light "
        "shows, sculpture, rooms of every trade, hand embroidery, printmaking): the packs use their narrower "
        "categories.",
    "Open Images labels with ambiguous meanings": "Milling (grain mills too), Molding (architectural trim too), "
        "Laser printing and Inkjet printing (office printers), Machine (too general) and Machinist (6 photos): not "
        "asked.",
    "Open Images labels asked elsewhere": "Lathe, Welding, Welder, Printed circuit board, Solder, Mold, Clamp, "
        "Power tool, Printer, Printer consumable, Embroidery, Sewing machine, Drill (Tool), Hand tool, Chisel, Tool, "
        "Toolbox and Circular saw: asked by other packs, never twice.",
    "NIST, DOE and America Makes photo galleries": "not built in this version: NIST's and the Department of "
        "Energy's own photo pages (public domain) were not checked for a subject listing a program may read; the "
        "photos people copied to Commons come through the Commons categories. America Makes' pictures are its "
        "members' copyright.",
    "Makers' product photos (Cricut, Silhouette, Glowforge, xTool, Bambu Lab, Creality, Elegoo, Anycubic, Prusa, "
    "Shapeoko, Sherline, Taig, Grizzly)": "the makers' copyright; not used. Their manuals are listed as links in the "
        "manual collections under the heading Home manufacturing and making.",
    "Thingiverse, Printables and MyMiniFactory models and photos": "each model under its maker's own licence (many "
        "non-commercial) and the sites' terms were not checked one by one; not used.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the home manufacturing and making share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in MAKING_SOURCES if s.key == "making_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="making-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
