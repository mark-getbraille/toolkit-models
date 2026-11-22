"""Picture packs for HOME MANUFACTURING AND MAKING (the owner's request of 2026-11-22): 3D printers and their prints,
cutting machines and heat presses, laser cutters and engravers, CNC machines, tabletop lathes and mills with their
tooling, moulding and casting, and electronics fabrication. Used by build_packs.py in the same way as its own PACKS:
each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one
question comes once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts
pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise a 3D printer, a
failed print, a vinyl cutter, a laser engraver, a lathe chuck or a mould, and to say the safety rules that go with
each machine. Answers say only what the source says (a Commons category's name, an Open Images label people
confirmed), never a guess: no brand, model, material or setting is named unless the category itself names it. Every
answer about a machine ends with the safety notes that fit it (the same words in the kit's making_sources.py):
  PRINTER_NOTE   3D printers: hot nozzle and bed, watched, on a surface that does not burn, smoke alarm, ventilation.
  RESIN_NOTE     resin printing and casting resin: skin allergy, nitrile gloves, eye protection, cure waste first.
  LASER_NOTE     laser eye safety: never look into the beam, eyewear rated for the wavelength, Class 4, lid shut,
                 never left running, extinguisher close.
  FUME_NOTE      fumes: exhaust outdoors; never cut or engrave PVC or vinyl (chlorine gas).
  MACHINE_NOTE   rotating machinery: safety glasses; no gloves, loose sleeves, jewellery or long hair near spinning
                 parts; chuck key out, guards on, stop before measuring.
  BLADE_NOTE     cutting machines: sharp blades, fingers clear of the moving carriage.
  HEAT_NOTE      heat presses: hot platen, gloves, never left on alone.
  CASTING_NOTE   molten metal and water, protective gear; resins and silicone need gloves and ventilation.
  SOLDER_NOTE    soldering and reflow: hot, fume extractor, wash hands after solder.
  FORMING_NOTE, PLASMA_NOTE and FORGE_NOTE  hot plastic; plasma cutting; hot metal at the forge and anvil.

The packs (MAKING_PACKS):
  commons_3d_printing       Wikimedia Commons (CC0, public domain or CC BY files only): 3D printers (RepRap, Prusa i3,
                            MakerBot, Ultimaker, Creality Ender 3, Bambu Lab, Formlabs), fused filament fabrication,
                            stereolithography and selective laser sintering, extruders, filament, photopolymer resins,
                            3D printed objects and failed prints, 3D scanning, and 3D design (OpenSCAD, FreeCAD,
                            Blender, STL models).
  commons_cutting_lasers    Commons: vinyl cutters, plotters and cutting machines, heat presses, screen printing,
                            sign making and machine embroidery; laser cutting and engraving, CO2 and fibre lasers,
                            laser goggles, laser warning signs and laser safety; engraving machines and tools, and
                            plasma cutting.
  commons_cnc_machining     Commons: computer numerical control (CNC), metalworking lathes (Myford), watchmaker's
                            lathes, lathe chucks, dogs, tailstocks, steady rests and lathe tools, centre drills,
                            knurling, milling tools, machine vises, rotary tables and indexing heads, tool and cutter
                            grinders, grinding machines, machining and woodturning.
  commons_moulding_casting  Commons: injection moulding, thermoforming and vacuum forming, moulds, sand and investment
                            casting, blacksmithing, and makerspaces, hackerspaces and fab labs.
  commons_pcb_fabrication   Commons: printed circuit board manufacturing, PCB milling, solder-paste stencil printing
                            and reflow soldering (electronics fabrication; the parts and soldering tools are the
                            electronics packs').
  open_images_making        Open Images V7 (labels CC BY 4.0; each photo CC BY, CC0 or the Public Domain Mark): 3D
                            modelling, machine tools, metal lathes, tool and cutter grinders, ironworkers, riveting
                            and combination machines, drill presses, bandsaws, vises, calipers, rotary tools, routers
                            and router bits, workshops and toolrooms, cutting mats and cutting tools, casting and
                            resin, lasers, anvils, forges, welding helmets, metalworking hand tools, soldering irons
                            and screen printing. No label is asked twice (packs/test_making.py checks).

Not repeated here (linked instead): hardware_packs' woodshop and metal shop machines (CNC routers, Laser cutters,
Milling machines, Drill presses, Router bits, Anvils, Forges, Taps and dies, Drill chucks, Dremel and the others),
land_industry_packs' Lathes, work_farm_mech_packs' Milling machines and Machine shops, textile_crafts_packs'
Embroidery machines, crafts_packs' Resin casting and Lost-wax casting (commons_models_resin), things_packs'
Breadboards and Raspberry Pi, the electronics packs' soldering tools, and vision_packs' tactile graphics and models
(commons_tactile_access). The Open Images labels other packs ask (Lathe, Welding, Welder, Printed circuit board,
Solder, Mold, Clamp, Power tool, Printer and others) are not asked again. What was looked at and left out is in the
kit's making_sources.py (MAKING_NOT_INCLUDED).

    python packs/making_packs.py commons_3d_printing --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap
from outdoor_cooking_packs import thing, with_yes_notes

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

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
NOTES = (PRINTER_NOTE, RESIN_NOTE, LASER_NOTE, FUME_NOTE, MACHINE_NOTE, BLADE_NOTE, HEAT_NOTE, CASTING_NOTE,
         SOLDER_NOTE, FORMING_NOTE, PLASMA_NOTE, FORGE_NOTE)

# ----------------------------------------------------------------- Commons: 3D printing and 3D design

# Commons "Blender (software)" and "STL files" hold renders of every kind: only files whose own words name a model,
# a print, a mesh or the program itself.
MODEL_WORDS = re.compile(r"\b(3d|stl|mesh|models?|render(ed|ing)?|print(ed|ing|able)?|blender|cad|parts?)\b", re.I)
PRINTING = [
    thing("3D printers", "a 3D printer, a machine that builds an object layer by layer from a computer model",
          PRINTER_NOTE),
    thing("RepRap", "a RepRap, an open-source 3D printer designed to print many of its own parts", PRINTER_NOTE, True),
    thing("Prusa i3", "a Prusa i3, an open-source 3D printer design of the RepRap family", PRINTER_NOTE, True),
    thing("MakerBot", "a MakerBot 3D printer or its prints", PRINTER_NOTE, True),
    thing("Ultimaker", "an Ultimaker 3D printer", PRINTER_NOTE, True),
    thing("Creality Ender 3", "a Creality Ender 3, a 3D printer of the Prusa i3 kind", PRINTER_NOTE),
    thing("Bambu Lab", "a Bambu Lab 3D printer", PRINTER_NOTE, True),
    thing("Formlabs", "a Formlabs resin (stereolithography) 3D printer", RESIN_NOTE, True),
    thing("Fused filament fabrication", "fused filament fabrication (FFF): 3D printing by melting plastic filament "
                                        "and laying it down layer by layer", PRINTER_NOTE, True),
    thing("Stereolithography", "stereolithography (SLA): 3D printing that hardens liquid resin layer by layer with "
                               "light", RESIN_NOTE, True),
    thing("Selective laser sintering", "selective laser sintering (SLS): 3D printing that fuses powder with a laser",
          LASER_NOTE),
    thing("3D printer extruders", "a 3D printer extruder, the part that pushes the filament into the hot nozzle",
          PRINTER_NOTE, True),
    thing("3D printing filament", "3D printing filament: plastic wire on a spool, fed into the printer; keep it dry "
                                  "in a sealed bag or box", "", True),
    thing("Photopolymers", "a photopolymer: a liquid resin that hardens under light, as used in resin printers",
          RESIN_NOTE),
    thing("Failed 3D prints", "a failed 3D print", PRINTER_NOTE),
    thing("3D printed objects", "a 3D printed object"),
    thing("3D printing", "3D printing", PRINTER_NOTE),
    thing("3D scanning", "3D scanning: measuring a real object's shape to make a computer model of it", "", True),
    thing("OpenSCAD", "OpenSCAD, a free program in which you design 3D models by writing code, which suits screen "
                      "reader users, or a model made with it", deeper=True),
    thing("FreeCAD", "FreeCAD, a free 3D design (CAD) program, or a model made with it", deeper=True),
    thing("Blender (software)", "Blender, a free 3D modelling and animation program, or a model made with it",
          pattern=MODEL_WORDS),
    thing("STL files", "a 3D model of the kind saved as an STL file, which a slicer turns into printer instructions "
                       "(G-code)", pattern=MODEL_WORDS),
]

# ----------------------------------------------------------------- Commons: cutting machines, heat presses and lasers

# Commons "Plotters" is mostly old pen plotters and "Cutting machines" mostly factory machines: the answer says only
# what the category says.
CUTTING_LASERS = [
    thing("Vinyl cutters", "a vinyl cutter, a computer-driven machine whose small blade cuts shapes and letters from "
                           "vinyl or paper", BLADE_NOTE),
    thing("Plotters", "a plotter, a computer-driven machine that draws or cuts on sheets", BLADE_NOTE),
    thing("Cutting machines", "a cutting machine", MACHINE_NOTE),
    thing("Heat press", "a heat press, which presses transfers, heat-transfer vinyl or sublimation prints onto "
                        "fabric and other things", HEAT_NOTE),
    thing("Screen printing", "screen printing: ink pressed through a stencil on a mesh screen onto paper or fabric",
          "", True),
    thing("Sign making", "sign making", "", True),
    thing("Machine embroidery", "machine embroidery: stitching done by an embroidery machine following a design",
          deeper=True),
    thing("Laser cutting", "laser cutting: a laser beam cuts wood, acrylic, paper or metal along a path", LASER_NOTES,
          True),
    thing("Laser engraving", "laser engraving: a laser marks a picture or text into a surface", LASER_NOTES, True),
    thing("CO2 lasers", "a CO2 (carbon dioxide) laser, the kind used in many laser cutters", LASER_NOTES, True),
    thing("Fiber lasers", "a fibre laser, a laser used for marking and cutting metal", LASER_NOTES),
    thing("Laser goggles", "laser safety goggles: they protect only against the wavelengths printed on them",
          LASER_NOTE),
    thing("Laser warning signs", "a laser warning sign", LASER_NOTE, True),
    thing("Laser safety", "laser safety equipment or signs", LASER_NOTE, True),
    thing("Engraving machines", "an engraving machine", MACHINE_NOTE),
    thing("Engraving tools", "an engraving tool", "", True),
    thing("Plasma cutting", "plasma cutting: an electric arc and gas jet cut metal", PLASMA_NOTE),
]

# ----------------------------------------------------------------- Commons: CNC, small lathes and mills, tooling

CNC_MACHINING = [
    thing("Computer numerical control", "a CNC (computer numerical control) machine, which moves its tool along a "
                                        "path written in G-code", MACHINE_NOTE),
    thing("Metalworking lathes", "a metalworking lathe: it spins metal work against a cutting tool", MACHINE_NOTE),
    thing("Myford", "a Myford lathe, a small metalworking lathe made in England", MACHINE_NOTE),
    thing("Watchmaker's lathes", "a watchmaker's lathe, a very small precision lathe", MACHINE_NOTE),
    thing("Lathe chucks", "a lathe chuck, the jaws that grip the work on a lathe", MACHINE_NOTE, True),
    thing("Lathe dogs", "a lathe dog, a clamp that turns work held between centres", MACHINE_NOTE),
    thing("Tailstocks", "a tailstock, the end of a lathe that holds a centre or a drill", MACHINE_NOTE),
    thing("Steady rests", "a steady rest, which supports long work on a lathe", MACHINE_NOTE),
    thing("Lathe tools", "a lathe tool (cutting tool for a lathe)", MACHINE_NOTE, True),
    thing("Center drills", "a centre drill, a short drill for starting holes and for lathe centres", MACHINE_NOTE),
    thing("Knurling", "knurling: a pattern of ridges rolled or cut into metal for grip", MACHINE_NOTE, True),
    thing("Milling tools", "a milling cutter, such as an end mill, for a milling machine or CNC", MACHINE_NOTE, True),
    thing("Machine vises", "a machine vise, which holds work on a drill press or milling table", MACHINE_NOTE, True),
    thing("Rotary tables", "a rotary table, which turns work by measured angles on a milling machine", MACHINE_NOTE),
    thing("Indexing heads", "an indexing (dividing) head, which turns work by exact divisions for milling",
          MACHINE_NOTE),
    thing("Tool and cutter grinders", "a tool and cutter grinder, which sharpens milling cutters and lathe tools",
          MACHINE_NOTE),
    thing("Grinding machines", "a grinding machine", MACHINE_NOTE),
    thing("Machining", "machining: cutting metal to shape on machine tools", MACHINE_NOTE),
    thing("Woodturning", "woodturning: shaping wood as it spins on a lathe", MACHINE_NOTE, True),
]

# ----------------------------------------------------------------- Commons: moulding, casting and makerspaces

MOULDING_CASTING = [
    thing("Injection moulding", "injection moulding: melted plastic forced into a mould", FORMING_NOTE),
    thing("Thermoforming", "thermoforming: a heated plastic sheet shaped over a mould", FORMING_NOTE),
    thing("Vacuum forming", "vacuum forming: a heated plastic sheet sucked down over a shape", FORMING_NOTE),
    thing("Moulds", "a mould, the hollow shape that cast or moulded material fills", CASTING_NOTE),
    thing("Sand casting", "sand casting: molten metal poured into a mould made of sand", CASTING_NOTE, True),
    thing("Investment casting", "investment casting: metal poured into a ceramic mould made around a wax pattern",
          CASTING_NOTE),
    thing("Blacksmithing", "blacksmithing: shaping hot iron and steel with hammer and anvil", FORGE_NOTE, True),
    thing("Makerspaces", "a makerspace, a shared workshop where people use 3D printers, lasers and tools together",
          deeper=True),
    thing("Hackerspaces", "a hackerspace, a shared workshop for electronics, computers and making"),
    thing("Fab labs", "a fab lab (fabrication laboratory), a shared digital workshop", deeper=True),
]

# ----------------------------------------------------------------- Commons: electronics fabrication

PCB_FABRICATION = [
    thing("Printed circuit board manufacturing", "printed circuit board (PCB) manufacturing", SOLDER_NOTE),
    thing("Printed circuit board milling", "PCB milling: a CNC mill cuts away copper to make a circuit board",
          MACHINE_NOTE),
    thing("Stencil printing", "solder-paste stencil printing: paste spread through a stencil onto a circuit board",
          SOLDER_NOTE),
    thing("Reflow soldering", "reflow soldering: a board with solder paste heated until the solder melts",
          SOLDER_NOTE),
]


def build_commons_3d_printing(limit):
    """The commons_3d_printing pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PRINTING, limit, "make3d")


def build_commons_cutting_lasers(limit):
    """The commons_cutting_lasers pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CUTTING_LASERS, limit, "makecut")


def build_commons_cnc_machining(limit):
    """The commons_cnc_machining pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CNC_MACHINING, limit, "makecnc")


def build_commons_moulding_casting(limit):
    """The commons_moulding_casting pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MOULDING_CASTING, limit, "makemould")


def build_commons_pcb_fabrication(limit):
    """The commons_pcb_fabrication pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PCB_FABRICATION, limit, "makepcb")


# ----------------------------------------------------------------- Open Images

# Labels with human-checked photos in Open Images V7 (counted 2026-11-22 on the train, validation and test sets).
MAKING_OI = [
    group("Is there 3D modelling in this picture?", {"3d modeling": "3D modelling"}),
    group("What machine tools are in this picture?",
          {"Machine tool": "a machine tool", "Metal lathe": "a metal lathe",
           "Tool and cutter grinder": "a tool and cutter grinder", "Ironworker (Machine)": "an ironworker machine",
           "Riveting machine": "a riveting machine", "Combination machine": "a combination machine"}, MACHINE_NOTE),
    group("What bench tools are in this picture?",
          {"Drill press": "a drill press", "Bandsaw": "a bandsaw", "Rotary tool": "a rotary tool",
           "Router (Tool)": "a router", "Router bit": "a router bit"}, MACHINE_NOTE),
    group("What measuring and holding tools are in this picture?", {"Calipers": "calipers", "Vise": "a vise"}),
    group("What kind of workroom is this?", {"Workshop": "a workshop", "Toolroom": "a toolroom"}),
    group("What cutting things are in this picture?", {"Cutting mat": "a cutting mat", "Cutting tool": "a cutting tool"},
          BLADE_NOTE),
    group("Is there casting or resin in this picture?", {"Casting": "casting", "Resin": "resin"}, CASTING_NOTE),
    group("Is there a laser in this picture?", {"Laser": "a laser"}, LASER_NOTE),
    group("What metalworking things are in this picture?",
          {"Anvil": "an anvil", "Forge": "a forge", "Welding helmet": "a welding helmet",
           "Metalworking hand tool": "a metalworking hand tool"}, FORGE_NOTE),
    group("What soldering things are in this picture?",
          {"Soldering iron": "a soldering iron", "Soldering iron tip": "a soldering iron tip"}, SOLDER_NOTE),
    group("Is there screen printing in this picture?", {"Screen-printing": "screen printing"}),
]


def build_open_images_making(limit):
    """open_images_making (see the module docstring); each group's safety note is added to its "yes" answers too."""
    return with_yes_notes(build_oi_gap("open_images_making", MAKING_OI, limit, 9511), MAKING_OI)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
MAKING_PACKS = {
    "commons_3d_printing": (build_commons_3d_printing, COMMONS_LICENCE.format(
        what="3D printer, extruder, filament, resin, 3D print, 3D scanning and 3D design")),
    "commons_cutting_lasers": (build_commons_cutting_lasers, COMMONS_LICENCE.format(
        what="vinyl cutter, plotter, heat press, screen printing, laser cutting and engraving, laser safety and "
             "plasma cutting")),
    "commons_cnc_machining": (build_commons_cnc_machining, COMMONS_LICENCE.format(
        what="CNC, metalworking lathe, lathe tooling, milling tool, rotary table, grinder and woodturning")),
    "commons_moulding_casting": (build_commons_moulding_casting, COMMONS_LICENCE.format(
        what="injection moulding, thermoforming, vacuum forming, mould, casting, blacksmithing and makerspace")),
    "commons_pcb_fabrication": (build_commons_pcb_fabrication, COMMONS_LICENCE.format(
        what="printed circuit board manufacturing, PCB milling, stencil printing and reflow soldering")),
    "open_images_making": (build_open_images_making, OI_LICENCE),
}
MAKING_LIMITS = {
    "commons_3d_printing": 1200,       # 22 categories; 3D printed objects, STL files and OpenSCAD have most files
    "commons_cutting_lasers": 900,     # 17 categories
    "commons_cnc_machining": 900,      # 19 categories
    "commons_moulding_casting": 700,   # 10 categories
    "commons_pcb_fabrication": 120,    # 4 small categories
    "open_images_making": 1500,        # 27 labels; Machine tool, Toolroom, Workshop and Laser have most photos
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
MAKING_COMMONS_KEYS = ("commons_3d_printing", "commons_cutting_lasers", "commons_cnc_machining",
                       "commons_moulding_casting", "commons_pcb_fabrication")
# The Commons category specs of the packs (for the self-test).
MAKING_SPECS = PRINTING + CUTTING_LASERS + CNC_MACHINING + MOULDING_CASTING + PCB_FABRICATION


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(MAKING_PACKS, "Try a home manufacturing and making pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
