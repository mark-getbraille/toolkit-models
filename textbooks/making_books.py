"""Home manufacturing and making for the reference library, in its own group "Reference, home manufacturing and
making" (the owner's request of 2026-11-22). Keys: making (every book), make:<name>.

What this module builds, in plain words:
  - make:index, a guide to the library on home manufacturing and making (the toolkit's own facts and links, CC0): 3D
    printers and their care, slicers, troubleshooting and firmware, 3D design for beginners and accessible 3D design
    for blind makers (OpenSCAD, which is code and so works with a screen reader), tactile graphics and 3D-printed
    tactile models, cutting machines and heat presses, laser cutters and engravers and their safety, CNC, small
    lathes and mills, moulding and casting, and electronics fabrication, with the books by key, the manual
    collections, the picture packs and the link-only sources (makers' documentation and copyright programs);
  - IN FULL, open documentation where its licence allows:
      the Klipper 3D printer firmware documentation (GNU GPL version 3, the licence of the Klipper repository that
      holds the documents; share-alike), every page;
      the FreeCAD user manual on the FreeCAD wiki (CC BY 3.0, "Content is available under Creative Commons
      Attribution unless otherwise noted", checked on every page), every chapter;
      the LinuxCNC documentation's getting-started, user, G-code, lathe, plasma and configuration chapters (GNU Free
      Documentation License 1.1 or later, no invariant sections; share-alike);
      Wikibooks' OpenSCAD User Manual, OpenSCAD Tutorial, 3D Printing and Blender 3D: Noob to Pro (CC BY-SA 4.0,
      share-alike);
      the FDA's laser product pages (laser hazard classes I to IV, laser toys and pointers; US government works);
      three NIST additive manufacturing publications by NIST's own staff (test artefacts for 3D printers, metal 3D
      printing defects, costs; US government works);
      three military machinist manuals, each judged at every build by the release rule (military_release.py): the
      Army's Fundamentals of Machine Tools (TC 9-524, 1996) and The Machinist (TM 10-445, 1941), and the Navy's
      Machinery Repairman (1993);
      nine old public-domain machining and pattern-making books (published before 1931; the builder checks each
      Internet Archive item's year at every build): Yates's Lathe Work for Beginners (1922), Goodrich's The
      Watchmaker's Lathe (1903), South Bend's How to Make an 8-inch Bench Lathe (1920), Turner and Perrigo's Machine
      Shop Work (1918), Palmateer's Elementary Machine Shop Practice (1920), Colvin and Stanley's American
      Machinists' Handbook (1914), Hammond's Production Milling (1921), Ritchey's Pattern Making (1908) and Hand's
      Pattern Making and Foundry Practice (1905). Each says what is out of date in it.
  Every book's notice ends with MAKING_SAFETY (the same rules the picture packs say: laser eyes and fire, fumes and
  no PVC or vinyl, resin on skin, hot nozzles, rotating machinery, molten metal).

Already in the library and not repeated (the index links them): the electronics books (electronics: soldering and
circuits), the woodworking and carpentry Wikibooks (building), the crafts books (craft:), the power and electrical
books, and the vision books on tactile graphics (vision-living).

Not built (NOT_INCLUDED, link-only for the owner's Program Downloader, each with its address): the RepRap wiki and the
Marlin documentation (their sites shut out AI readers or say ai-train=no), the Prusa Knowledge Base, LightBurn,
Cricut Design Space, Silhouette Studio, Tinkercad, Bambu Lab, Creality, Elegoo, Anycubic, Glowforge, xTool, Shapeoko,
Sherline, Taig and Grizzly (the makers' copyright), the GRBL wiki (GitHub's robots.txt), the Inkscape manual (not
reachable), LaserGRBL's pages (no licence stated), OSHA's laser and machine guarding pages (osha.gov refuses
programs) and the America Makes guides (members' copyright).

Run from the repository's folder:
  python3 textbooks/making_books.py make:fda_laser_safety --out build/textbooks --limit 5
  python3 textbooks/making_books.py --list making
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from electronics_books import wikibook  # noqa: E402

GROUP = "making"
GROUPS = {GROUP: "Reference, home manufacturing and making"}

# The safety notice every book carries (the picture packs say the same in packs/making_packs.py).
MAKING_SAFETY = ("Safety: never look into a laser beam or its reflection; wear eye protection rated for the laser's "
                 "wavelength, keep an enclosed laser's lid shut, never leave a laser or 3D printer running unwatched, "
                 "and keep a fire extinguisher close. Vent fumes outdoors, and never cut or engrave PVC or vinyl "
                 "(they give off chlorine gas). Liquid resin harms skin: wear nitrile gloves and eye protection. "
                 "Nozzles, beds, heat presses and soldering irons burn. Near lathes, mills and other spinning "
                 "machines wear safety glasses and no gloves, loose sleeves, jewellery or untied long hair. Molten "
                 "metal explodes on contact with water.")
OLD_MAKING_NOTE = ("Published in {year}: an old book. Its shop methods still explain how lathes, mills and patterns "
                   "work, but its machines are belt-driven and its safety practice is out of date (no guards, no eye "
                   "protection, lead and asbestos used freely): follow current machine guarding and the safety "
                   "notice instead. The machine-read text has the scanner's mistakes.")

# ====================================================================== Klipper (GNU GPL version 3)

KLIPPER = "https://www.klipper3d.org/"
GPL3_ONLY = "GPL-3.0"
GUIDES = [
    dict(K.guide(GROUP, "klipper_docs", "Klipper 3D printer firmware documentation", "3D printer firmware (Klipper)",
                 "The Klipper project (Kevin O'Connor and contributors)", KLIPPER + "Overview.html",
                 r"^https://www\.klipper3d\.org/[A-Za-z0-9_-]+\.html$",
                 "The Klipper documentation, every page: what Klipper is, installing it on a printer's board and a "
                 "small computer, configuration, the first checks, bed levelling and probes, measuring rotation "
                 "distance, pressure advance, resonance compensation (input shaping), slicers, the G-code commands, "
                 "config reference, TMC stepper drivers, frequently asked questions and the developer pages.",
                 f"The Klipper documentation, copyright Kevin O'Connor and the Klipper contributors, part of the "
                 f"Klipper repository, which is free software under the GNU General Public License version 3 (its "
                 f"COPYING file; share-alike: copies and changed versions keep the same licence); its pages made "
                 f"into chapters. {MAKING_SAFETY}", depth=1, limit=120,
                 units=[(r"/(Overview|Features|FAQ|Releases|Installation|OctoPrint|Config_checks|Bed_Level|"
                         r"Manual_Level|Rotation_Distance|Pressure_Advance|Resonance_Compensation|Slicers|"
                         r"Skew_Correction|Exclude_Object|Measuring_Resonances)\.html$", "Using Klipper"),
                        (r"/(Config_Reference|G-Codes|Command_Templates|Status_Reference|TMC_Drivers|"
                         r"Multi_MCU_Homing|Probe_Calibrate|BLTouch|Endstop_Phase|Bed_Mesh|Axis_Twist_Compensation)"
                         r"\.html$", "Reference"),
                        (r".", "More pages")]),
         country="International", licence=GPL3_ONLY, licence_url="https://www.gnu.org/licenses/gpl-3.0.html",
         licence_page="https://raw.githubusercontent.com/Klipper3d/klipper/master/COPYING",
         licence_text=r"GNU GENERAL PUBLIC LICENSE Version 3",
         content=(r'<article class="md-content__inner md-typeset">', r"</article>"),
         changes="every page of the documentation made into web pages, with the site's menus left out"),
]

# ====================================================================== FreeCAD user manual (CC BY 3.0)

FREECAD = "https://wiki.freecad.org/"
GUIDES.append(dict(
    K.guide(GROUP, "freecad_manual", "The FreeCAD manual (FreeCAD wiki)", "3D design (FreeCAD)",
            "FreeCAD wiki contributors (wiki.freecad.org)", FREECAD + "Manual:Introduction",
            r"^https://wiki\.freecad\.org/Manual:[^?#/]+$",
            "The FreeCAD user manual from the FreeCAD wiki, every chapter: installing FreeCAD, the interface, "
            "navigating in 3D, workbenches, traditional and parametric modelling, sketches and constraints, Part "
            "Design, preparing models for 3D printing (exporting STL meshes, slicing) and for CNC, technical "
            "drawings, BIM, Python scripting and the FreeCAD community.",
            f"From the FreeCAD wiki, written by its contributors: \"Content is available under Creative Commons "
            f"Attribution unless otherwise noted\" (CC BY 3.0); each page's history lists its authors. FreeCAD is "
            f"a graphical program; its keyboard and Python console can help screen reader users. {MAKING_SAFETY}",
            depth=1, limit=80, units=[(r"Manual:(Introduction|Installing|The_FreeCAD_Interface|Navigating|"
                                       r"Workbenches|Macros|Units|Getting_started)", "Getting started"),
                                      (r"Manual:(Creating|Traditional|Modeling|Preparing|Exporting|Generating|"
                                       r"BIM|Using_spreadsheets|Creating_FEM)", "Working with FreeCAD"),
                                      (r".", "Scripting and the community")]),
    country="International", licence="CC BY 3.0", licence_url="https://creativecommons.org/licenses/by/3.0/",
    licence_page=FREECAD + "Manual:Introduction", licence_text=r"Content is available under Creative Commons "
                                                               r"Attribution",
    page_mark=r"Content is available under", content=(r'<div id="mw-content-text"[^>]*>', r'<div class="printfooter"'),
    drop=K.DROP + [r'<span class="mw-editsection">.*?</span>\s*</span>', r'<div class="(?:docnav|languages|noprint)'
                   r'[^"]*".*?</div>'],
    changes="every chapter of the manual made into web pages, with the wiki's menus and edit links left out"))

# ====================================================================== LinuxCNC documentation (GFDL 1.1 or later)

LINUXCNC = "https://linuxcnc.org/docs/stable/html/"
GFDL = "GFDL 1.1 or later"
GUIDES.append(dict(
    K.guide(GROUP, "linuxcnc_docs", "LinuxCNC documentation: getting started, user, G-code, lathe, plasma and "
            "configuration", "CNC control (LinuxCNC)", "The LinuxCNC project (LinuxCNC.org)", LINUXCNC + "index.html",
            r"^https://linuxcnc\.org/docs/stable/html/(getting-started|user|gcode|lathe|plasma|config|install)/"
            r"[a-z0-9_-]+\.html$",
            "The LinuxCNC documentation's chapters for people who run a CNC machine: what LinuxCNC is, installing it, "
            "the user's introduction (machine coordinates, homing, jogging, touching off, tool tables), the G-code "
            "reference and overview (G, M and O codes, coordinate systems, cutter compensation), lathe user "
            "information, plasma cutting, and configuring a machine (stepper and servo configuration, the INI and HAL "
            "files).",
            f"The LinuxCNC documentation, copyright (c) 2000-2022 LinuxCNC.org: \"Permission is granted to copy, "
            f"distribute and/or modify this document under the terms of the GNU Free Documentation License, Version "
            f"1.1 or any later version ... with no Invariant Sections, no Front-Cover Texts, and no Back-Cover "
            f"Texts\" (share-alike; the licence's full text: {LINUXCNC}common/gpld-copyright.html). {MAKING_SAFETY}",
            depth=1, limit=120,
            units=[(r"/(getting-started|install)/", "Getting started"), (r"/user/", "Using LinuxCNC"),
                   (r"/gcode/", "G-code"), (r"/lathe/", "Lathes"), (r"/plasma/", "Plasma cutting"),
                   (r".", "Configuring a machine")]),
    country="International", licence=GFDL, licence_url="https://www.gnu.org/licenses/old-licenses/fdl-1.1.html",
    licence_page=LINUXCNC + "common/gpld-copyright.html",
    licence_text=r"GNU Free Documentation License, Version 1\.1 or any later version",
    content=(r'<div id="content">', r'<div id="footnotes">|<div id="footer">'),
    changes="the chapters' pages made into web pages, with the site's menus left out"))

# ====================================================================== Wikibooks (CC BY-SA 4.0)

GUIDES += [
    wikibook(GROUP, "wikibooks_openscad_user_manual", "OpenSCAD_User_Manual", "OpenSCAD User Manual (Wikibooks)",
             "3D design by code (OpenSCAD)",
             "Wikibooks' OpenSCAD User Manual, every page: the OpenSCAD language (values, variables, shapes, "
             "transformations, boolean operations, loops and modules), 2D and 3D primitives, extrusion, importing "
             "and exporting STL and other files, libraries, the command line, and tips. OpenSCAD models are plain "
             "text written in a code editor, so a blind maker can design 3D prints with a screen reader and check "
             "them by measurement.", MAKING_SAFETY),
    wikibook(GROUP, "wikibooks_openscad_tutorial", "OpenSCAD_Tutorial", "OpenSCAD Tutorial (Wikibooks)",
             "3D design by code (OpenSCAD)",
             "Wikibooks' step-by-step OpenSCAD tutorial: from a first cube to parameters, modules, loops and "
             "ready-to-print models such as a car and a box, every chapter.", MAKING_SAFETY),
    wikibook(GROUP, "wikibooks_3d_printing", "3D_Printing", "3D Printing (Wikibooks)", "3D printing",
             "Wikibooks' book on 3D printing: the kinds of printers (FDM/FFF, resin and others), materials, "
             "preparing models, slicing and printing.", MAKING_SAFETY),
    wikibook(GROUP, "wikibooks_blender_noob_to_pro", "Blender_3D:_Noob_to_Pro", "Blender 3D: Noob to Pro "
             "(Wikibooks)", "3D modelling (Blender)",
             "Wikibooks' long Blender course, every page: the interface, modelling with meshes, modifiers, "
             "materials, lighting and rendering, and animation. Blender is a mouse-driven program; this book is for "
             "learning its words and ideas, and for sighted helpers.", MAKING_SAFETY),
]

# ====================================================================== FDA laser products (public domain)

FDA = "https://www.fda.gov"
FDA_POLICY = FDA + "/about-fda/about-website/website-policies"
FDA_TEXT = r"are not copyrighted\. They are in the public domain"
FDA_PAGES = [FDA + "/radiation-emitting-products/home-business-and-entertainment-products/laser-products-and-"
                   "instruments",
             FDA + "/consumers/consumer-updates/laser-toys-how-keep-kids-safe",
             FDA + "/radiation-emitting-products/laser-products-and-instruments/important-information-laser-pointer-"
                   "manufacturers",
             FDA + "/radiation-emitting-products/home-business-and-entertainment-products/laser-light-shows"]
GUIDES.append(dict(X.page_list_book(
    GROUP, "fda_laser_safety", "Laser products and their hazard classes (FDA)", "Laser safety",
    "US Food and Drug Administration, Center for Devices and Radiological Health", FDA_PAGES,
    r"^https://www\.fda\.gov/(radiation-emitting-products|consumers/consumer-updates)/[a-z0-9/-]+$",
    "The FDA's pages on laser products: the benefits and risks of lasers, the four hazard classes (I to IV, with "
    "the matching IEC classes 1 to 4) and what each can do to eyes and skin (Class IV: an immediate eye and skin "
    "hazard from the direct or reflected beam, and a fire hazard), the rules for laser makers, laser toys and "
    "keeping children safe, laser pointers, and laser light shows.",
    f"From the US Food and Drug Administration: \"the contents of the FDA website ... are not copyrighted. They are "
    f"in the public domain\"; credit to the FDA. This copy does not suggest the FDA's endorsement. {MAKING_SAFETY}",
    content=(r'<article id="main-content"[^>]*>', r"</article>"),
    units=[(r"laser-products-and-instruments$", "Laser products and classes"), (r".", "Toys, pointers and shows")]),
    licence_page=FDA_POLICY, licence_text=FDA_TEXT))

# ====================================================================== NIST additive manufacturing (public domain)

NIST = "https://nvlpubs.nist.gov/nistpubs/"
NIST_NOTICE = ("A publication of the National Institute of Standards and Technology written by its own staff: a work "
               "of the US government, not subject to copyright in the United States. Written for industry and "
               "researchers; ")
PDFS = [
    K.us_pdf(GROUP, name="nist_ir_7858_test_artifacts", title="A Review of Test Artifacts for Additive "
             "Manufacturing (NISTIR 7858, 2012)", subject="3D printer testing and calibration",
             publisher="National Institute of Standards and Technology (Shawn Moylan and others)",
             pdf=NIST + "ir/2012/NIST.IR.7858.pdf", page="https://doi.org/10.6028/NIST.IR.7858", published="2012-04",
             version="NISTIR 7858, April 2012",
             description="NIST's review of test artefacts: the standard test parts printed to check a 3D printer's "
                         "accuracy, features, surface finish and repeatability, and what each one measures; the "
                         "ideas behind the calibration prints home makers use.",
             notice=NIST_NOTICE + "its ideas apply to home printers too. " + MAKING_SAFETY),
    K.us_pdf(GROUP, name="nist_ams_100_16_metal_am_defects", title="Literature Review of Metal Additive "
             "Manufacturing Defects (NIST AMS 100-16, 2018)", subject="3D printing defects",
             publisher="National Institute of Standards and Technology (Felix H. Kim and Shawn P. Moylan)",
             pdf=NIST + "ams/NIST.AMS.100-16.pdf", page="https://doi.org/10.6028/NIST.AMS.100-16", published="2018",
             version="NIST AMS 100-16",
             description="NIST's review of the defects of metal 3D printing (porosity, cracks, poor fusion, "
                         "surface roughness, distortion and residual stress) and their causes; many of the same "
                         "words describe plastic print faults.",
             notice=NIST_NOTICE + "about industrial metal printers. " + MAKING_SAFETY),
    K.us_pdf(GROUP, name="nist_sp_1176_am_costs", title="Costs and Cost Effectiveness of Additive Manufacturing (NIST "
             "SP 1176, 2014)", subject="3D printing costs", publisher="National Institute of Standards and "
             "Technology (Douglas S. Thomas and Stanley W. Gilbert)", pdf=NIST + "SpecialPublications/NIST.SP.1176.pdf",
             page="https://doi.org/10.6028/NIST.SP.1176", published="2014-12", version="NIST SP 1176",
             description="NIST's literature review of what 3D printing costs (machines, materials, energy, build "
                         "time) and when it is cheaper than other ways of making things.",
             notice=NIST_NOTICE + "its figures date from 2014. " + MAKING_SAFETY),
]

# ====================================================================== military machinist manuals (release rule)

MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "military machinists: its machines are shop machines and some are old. ")
PDFS += [
    K.us_pdf(GROUP, name="army_tc_9_524_machine_tools", title="Fundamentals of Machine Tools (TC 9-524, 1996)",
             subject="Machine tools: lathes, mills, drill presses and grinders",
             publisher="Headquarters, Department of the Army", archive="tc9-524", distribution_a=True,
             published="1996", version="TC 9-524, 1996 (Internet Archive item tc9-524)",
             description="The US Army's machine shop textbook: safety, measuring and layout, hand tools, drilling "
                         "machines, grinders, sawing machines, the lathe (set-up, turning, threading, tapers and "
                         "knurling), milling machines and indexing, metal properties and heat treatment, and tables "
                         "of cutting speeds and feeds.",
             work="a work of the US Army", notice=MIL_NOTICE + MAKING_SAFETY),
    K.us_pdf(GROUP, name="army_tm_10_445_machinist_1941", title="The Machinist (TM 10-445, 1941)",
             subject="Machine shop practice", publisher="War Department (US Army)", archive="TM10-445", military=True,
             published="1941-11-12", version="TM 10-445, 12 November 1941 (Internet Archive item TM10-445)",
             description="The Army's 1941 machinist's manual: bench work, measuring tools, lathes, shapers, milling "
                         "and drilling machines, grinding, and shop mathematics. A historical manual.",
             work="a work of the US Army", notice=MIL_NOTICE + MAKING_SAFETY),
    K.us_pdf(GROUP, name="navy_machinery_repairman_1993", title="Machinery Repairman (US Navy training manual, 1993)",
             subject="Machine shop practice", publisher="Naval Education and Training Program Management Support "
             "Activity (US Navy)", archive="machinery-repairman_20200118", military=True, published="1993-09",
             version="1993 (Internet Archive item machinery-repairman_20200118)",
             description="The Navy's rate training manual for machinery repairmen: shop safety, measuring, layout "
                         "and benchwork, cutting tools, drill presses, lathes (turning, threading, tapers), milling "
                         "machines, shapers, grinders, metal properties and heat treatment, and an introduction to "
                         "numerical control (CNC).",
             work="a work of the US Navy", notice=MIL_NOTICE + MAKING_SAFETY),
]

# ====================================================================== old public-domain books (before 1931)

OLD_BOOKS = [
    ("yates_lathe_work_beginners_1922", "Lathe Work for Beginners (Raymond F. Yates, 1922)", "Lathe work",
     "Raymond F. Yates (Norman W. Henley Publishing)", "latheworkforbegi00yate", 1922,
     "A practical treatise for beginners: the parts of a lathe, wood and metal turning, screw cutting, measuring "
     "tools, metal spinning, and building home-made lathes and their attachments."),
    ("goodrich_watchmakers_lathe_1903", "The Watchmaker's Lathe, its Use and Abuse (Ward L. Goodrich, 1903)",
     "Small precision lathes", "Ward L. Goodrich (Hazlitt & Walker)", "watchmakerslathe00good", 1903,
     "The small precision lathe: its forms, construction, chucks and attachments, and its proper uses for fine "
     "work."),
    ("south_bend_bench_lathe_1920", "How to Make an 8-inch Bench Lathe in the School Shop (South Bend Lathe Works, "
     "1920)", "Building a bench lathe", "South Bend Lathe Works", "howtomakeaninch00goog", 1920,
     "South Bend's guide for students building a small bench lathe from castings: the patterns, machining the "
     "parts and assembling the lathe."),
    ("turner_machine_shop_work_1918", "Machine Shop Work (Frederick W. Turner and others, 1918)", "Machine shop "
     "practice", "Frederick W. Turner, Charles O. E. Perrigo and Howard P. Fairfield (American Technical Society)",
     "machineshopworkc00turnrich", 1918,
     "A comprehensive manual of shop methods: hand and machine tools, the lathe, planer, shaper, drill press, "
     "milling machine and grinder, and their efficient use."),
    ("palmateer_elementary_machine_shop_1920", "Elementary Machine Shop Practice (Theron J. Palmateer, 1920)",
     "Machine shop practice", "Theron J. Palmateer (Manual Arts Press)", "elementarymachin00palmrich", 1920,
     "A school textbook of the machine shop: measuring, bench work, drilling, the lathe and simple jobs."),
    ("colvin_american_machinists_handbook_1914", "American Machinists' Handbook and Dictionary of Shop Terms (Fred "
     "H. Colvin and Frank A. Stanley, 1914)", "Machinists' reference", "Fred H. Colvin and Frank A. Stanley "
     "(McGraw-Hill)", "americanmachinis00colv", 1914,
     "A reference book of machine shop data: screw threads, taps and dies, gears, cutting speeds, tapers, "
     "measuring, shop mathematics and a dictionary of shop terms."),
    ("hammond_production_milling_1921", "Production Milling (Edward K. Hammond, 1921)", "Milling machines",
     "Edward K. Hammond (The Industrial Press)", "productionmillin00hammrich", 1921,
     "Milling machines and the methods American shops used with them: kinds of mills, cutters, fixtures, "
     "indexing and quantity work."),
    ("ritchey_pattern_making_1908", "Pattern Making (James Ritchey, 1908)", "Pattern making and moulding",
     "James Ritchey (American School of Correspondence)", "patternmakingman00ritcuoft", 1908,
     "Making the wooden patterns from which castings are moulded: woodworking tools and machines, simple and "
     "built-up patterns, core boxes and methods of moulding."),
    ("hand_pattern_making_foundry_1905", "Pattern Making and Foundry Practice (L. H. Hand, 1905)", "Pattern making "
     "and casting", "L. H. Hand (F. J. Drake & Co.)", "patternmakingfou00hand", 1905,
     "Wood pattern making as practised in pattern shops, sweep work, and notes on foundry practice."),
]
PDFS += [X.old_book(GROUP, name, title, subject, publisher, archive, year, description,
                    OLD_MAKING_NOTE.format(year=year))
         for name, title, subject, publisher, archive, year, description in OLD_BOOKS]
# The old books carry the safety notice too (after the scan notice).
for _p in PDFS:
    if _p.get("old_public_domain"):
        _p["notice"] = f"{_p['notice']} {MAKING_SAFETY}"

# ====================================================================== the index

SECTIONS = [
    ("3D printers and their care", "FDM (FFF) printers: frames, extruders, hot ends, beds, bed levelling and "
     "calibration; resin (SLA and MSLA) printers; filaments and resins by material (PLA, PETG, ABS, ASA, TPU, "
     "nylon); maintenance.", [
        ("key", "make:wikibooks_3d_printing", "3D Printing (Wikibooks): kinds of printers, materials, slicing"),
        ("key", "make:klipper_docs", "Klipper: bed levelling, probes, rotation distance and the first checks"),
        ("key", "make:nist_ir_7858_test_artifacts", "Test artefacts for checking a printer's accuracy (NIST)"),
        ("pack", "commons_3d_printing", "Printers, extruders, filament, resin, prints and failed prints"),
        ("manuals", "printers_3d", "3D printer, filament and resin printer manuals and makers' links"),
        ("link", "Prusa Knowledge Base (Prusa Research)", "https://help.prusa3d.com/",
         "copyright of Prusa Research; open it in a browser or fetch it with Program Downloader"),
        ("link", "RepRap wiki", "https://reprap.org/wiki/RepRap",
         "its robots.txt shuts out AI readers, so it is not copied; open it in a browser"),
        ("link", "Bambu Lab Wiki", "https://wiki.bambulab.com/", "the maker's copyright"),
        ("link", "Creality support", "https://www.creality.com/pages/download", "the maker's copyright"),
        ("link", "Elegoo and Anycubic downloads", "https://www.elegoo.com/pages/download",
         "the makers' copyright (Anycubic: https://www.anycubic.com/)")]),
    ("Slicers, troubleshooting and firmware", "Slicer settings (layer height, walls, infill, supports), STL and "
     "G-code, print problems (stringing, warping, layer shifts, clogs) and firmware (Marlin, Klipper, Prusa).", [
        ("key", "make:klipper_docs", "The Klipper firmware documentation, every page"),
        ("key", "make:nist_ams_100_16_metal_am_defects", "Print defects and their causes (NIST, metal printing)"),
        ("pack", "commons_3d_printing", "Failed 3D prints, for the picture describer"),
        ("link", "Marlin firmware documentation", "https://marlinfw.org/docs/basics/introduction.html",
         "its site says ai-train=no, so it is not copied; open it in a browser"),
        ("link", "PrusaSlicer and the Prusa print quality guides", "https://help.prusa3d.com/category/"
         "print-quality-troubleshooting_212", "copyright of Prusa Research"),
        ("link", "UltiMaker Cura documentation", "https://support.ultimaker.com/s/topic/0TO5b000000MYCTGA4/"
         "ultimaker-cura", "copyright of UltiMaker")]),
    ("3D design for beginners", "FreeCAD, OpenSCAD, Blender and Tinkercad; STL files.", [
        ("key", "make:freecad_manual", "The FreeCAD manual, every chapter (CC BY 3.0)"),
        ("key", "make:wikibooks_blender_noob_to_pro", "Blender 3D: Noob to Pro (Wikibooks)"),
        ("pack", "commons_3d_printing", "OpenSCAD, FreeCAD and Blender models, for the picture describer"),
        ("link", "Tinkercad", "https://www.tinkercad.com/learn", "Autodesk's copyright web program; open it in a "
                                                                "browser")]),
    ("Accessible 3D design for blind makers", "OpenSCAD describes a model as text (code) written in any editor, "
     "so a screen reader user can design, change and check 3D prints without a mouse, measuring the result instead "
     "of looking at it. Start here.", [
        ("key", "make:wikibooks_openscad_tutorial", "OpenSCAD Tutorial (Wikibooks): from a first cube to "
                                                    "printable models"),
        ("key", "make:wikibooks_openscad_user_manual", "OpenSCAD User Manual (Wikibooks): the whole language"),
        ("link", "OpenSCAD documentation and cheat sheet", "https://openscad.org/documentation.html",
         "the OpenSCAD project's own pages; open them in a browser")]),
    ("Tactile graphics and 3D-printed tactile models", "Raised drawings, maps and models to read by touch.", [
        ("key", "vision:index", "Blind and low-vision living: a guide to the library (tactile graphics, braille)"),
        ("word", "vision-living", "The blind and low-vision living books (request word)"),
        ("pack", "commons_tactile_access", "Tactile graphics and models, for the picture describer"),
        ("link", "BANA Guidelines and Standards for Tactile Graphics", "https://www.brailleauthority.org/",
         "copyright of the Braille Authority of North America; open it in a browser")]),
    ("Cutting machines and heat presses", "Cricut, Silhouette and other vinyl and paper cutters: materials, mats, "
     "blades, design software, weeding and transfer tape, heat-transfer vinyl, heat presses and sublimation.", [
        ("pack", "commons_cutting_lasers", "Vinyl cutters, plotters, heat presses and screen printing"),
        ("manuals", "craft_machines", "Cricut, Silhouette, Brother ScanNCut and Sizzix manuals (links)"),
        ("manuals", "heat_press_vinyl", "Heat presses, vinyl cutters and sublimation printers (links)"),
        ("link", "Cricut Design Space help", "https://help.cricut.com/", "copyright of Cricut; open it in a "
                                                                        "browser"),
        ("link", "Silhouette Studio manual", "https://www.silhouetteamerica.com/software", "copyright of "
                                                                                          "Silhouette America"),
        ("link", "Inkscape documentation", "https://inkscape.org/learn/", "Inkscape is free software (GPL); its "
         "learning pages are marked all rights reserved, so they are links")]),
    ("Laser cutters and engravers", "Diode, CO2 and fibre lasers; laser classes, eye protection, fire, ventilation "
     "and toxic fumes (never PVC or vinyl); focusing and alignment; LightBurn and open programs (LaserGRBL, "
     "Inkscape plug-ins); mirrors, lenses, air assist and chillers.", [
        ("key", "make:fda_laser_safety", "Laser hazard classes I to IV and laser safety (FDA)"),
        ("pack", "commons_cutting_lasers", "Laser cutting and engraving, CO2 and fibre lasers, goggles and signs"),
        ("manuals", "laser_cnc_making", "Laser engravers, CNC machines and their controllers (links)"),
        ("link", "LightBurn documentation", "https://docs.lightburnsoftware.com/", "copyright of LightBurn "
                                                                                   "Software"),
        ("link", "LaserGRBL", "https://lasergrbl.com/usage/", "free software (GPL); its pages state no licence, "
                                                              "so they are links"),
        ("link", "Laser hazards (OSHA)", "https://www.osha.gov/laser-hazards", "osha.gov refuses programs; open it "
                                                                             "in a browser"),
        ("link", "Glowforge and xTool support", "https://support.glowforge.com/", "the makers' copyright (xTool: "
                                                                                  "https://support.xtool.com/)")]),
    ("CNC machines", "CNC routers and mills, desktop CNC, spindles, bits and end mills, feeds and speeds, "
     "workholding, CAM, G-code, GRBL and LinuxCNC, and safety.", [
        ("key", "make:linuxcnc_docs", "LinuxCNC: getting started, G-code, lathes, plasma and configuration"),
        ("key", "make:army_tc_9_524_machine_tools", "Cutting speeds and feeds, milling and indexing (TC 9-524)"),
        ("pack", "commons_cnc_machining", "CNC machines, milling cutters, vises and rotary tables"),
        ("manuals", "laser_cnc_making", "Desktop CNC machines and controllers (links)"),
        ("manuals", "woodshop_machines", "CNC routers and laser cutters with the woodshop machines"),
        ("link", "GRBL wiki", "https://github.com/gnea/grbl/wiki", "GitHub's robots.txt does not allow programs "
                                                                   "to read wikis; open it in a browser"),
        ("link", "Shapeoko (Carbide 3D) support", "https://carbide3d.com/support", "the maker's copyright")]),
    ("Small lathes and mills", "Tabletop lathes and mini mills: setup, tooling, cutting speeds, threading and "
     "safety; drill presses and bandsaws are with the woodshop machines.", [
        ("key", "make:army_tc_9_524_machine_tools", "Fundamentals of Machine Tools (TC 9-524)"),
        ("key", "make:navy_machinery_repairman_1993", "Machinery Repairman (US Navy, 1993)"),
        ("key", "make:army_tm_10_445_machinist_1941", "The Machinist (TM 10-445, 1941)"),
        ("key", "make:yates_lathe_work_beginners_1922", "Lathe Work for Beginners (1922)"),
        ("key", "make:goodrich_watchmakers_lathe_1903", "The Watchmaker's Lathe (1903)"),
        ("key", "make:south_bend_bench_lathe_1920", "How to Make an 8-inch Bench Lathe (1920)"),
        ("key", "make:turner_machine_shop_work_1918", "Machine Shop Work (1918)"),
        ("key", "make:palmateer_elementary_machine_shop_1920", "Elementary Machine Shop Practice (1920)"),
        ("key", "make:colvin_american_machinists_handbook_1914", "American Machinists' Handbook (1914)"),
        ("key", "make:hammond_production_milling_1921", "Production Milling (1921)"),
        ("pack", "commons_cnc_machining", "Lathes, chucks, tailstocks, lathe tools and milling cutters"),
        ("manuals", "small_machining", "Mini lathes, mini mills and bench machines (links)"),
        ("manuals", "metal_shop_welding", "Metal shop machines and the Army and Navy machinist manuals"),
        ("link", "Sherline, Taig and Grizzly", "https://www.sherline.com/", "the makers' copyright (Taig: "
         "https://www.taigtools.com/, Grizzly: https://www.grizzly.com/)")]),
    ("Moulding, casting and other machines", "Embroidery machines, engraving, small injection moulding, vacuum "
     "forming, casting and mould making (resin and silicone: gloves, eye protection and ventilation).", [
        ("key", "make:ritchey_pattern_making_1908", "Pattern Making (1908)"),
        ("key", "make:hand_pattern_making_foundry_1905", "Pattern Making and Foundry Practice (1905)"),
        ("pack", "commons_moulding_casting", "Injection moulding, vacuum forming, moulds and casting"),
        ("pack", "commons_models_resin", "Resin casting and scale models (the crafts pack)"),
        ("manuals", "moulding_casting", "Vacuum formers, injection moulders and casting supplies (links)"),
        ("manuals", "sewing_textile", "Embroidery machines, with the sewing machines")]),
    ("Electronics fabrication", "PCB milling, solder-paste stencils and reflow, with the electronics books.", [
        ("word", "electronics", "The electronics books: soldering, circuits and repair (request word)"),
        ("pack", "commons_pcb_fabrication", "PCB manufacturing, milling, stencils and reflow"),
        ("key", "make:linuxcnc_docs", "LinuxCNC (for a CNC mill that makes circuit boards)")]),
]
INDEX = X.index_maker("make", GROUP, "Home manufacturing and making: a guide to the library",
                      "Home manufacturing and making",
                      "A guide to the library on home manufacturing and making: 3D printers, slicers and firmware, 3D "
                      "design and accessible design with OpenSCAD, tactile models, cutting machines and heat presses, "
                      "lasers and their safety, CNC, small lathes and mills, moulding and casting, and electronics "
                      "fabrication.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("make", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"making": lambda: ["make:index"] + [f"make:{g['name']}" for g in GUIDES + PDFS]})

# The licences these books use that sources.ALLOWED did not have (share-alike: copies keep the same licence).
ALLOWED = {GPL3_ONLY: "share-alike", "GFDL": "share-alike"}

LICENCE_LINES = {
    "making_klipper": "www.klipper3d.org: the documents of the Klipper repository, whose COPYING file (checked at "
                      "every build on raw.githubusercontent.com) is the GNU GPL version 3; robots.txt allows the "
                      "pages, no AI rules (checked 2026-11-22).",
    "making_freecad": "wiki.freecad.org: \"Content is available under Creative Commons Attribution unless otherwise "
                      "noted\" (CC BY 3.0), checked on every page; robots.txt allows the pages, no AI rules "
                      "(checked 2026-11-22).",
    "making_linuxcnc": "linuxcnc.org/docs/stable/html/common/gpld-copyright.html (checked at every build): GNU Free "
                       "Documentation License 1.1 or later, no invariant sections; robots.txt allows the pages, no "
                       "AI rules (checked 2026-11-22).",
    "making_wikibooks": "en.wikibooks.org: CC BY-SA 4.0 (its copyright page checked at every build).",
    "making_fda": "www.fda.gov/about-fda/about-website/website-policies (checked at every build): \"the contents of "
                  "the FDA website ... are not copyrighted. They are in the public domain\"; robots.txt allows the "
                  "pages, no AI rules (checked 2026-11-22).",
    "making_nist": "nvlpubs.nist.gov: NIST publications by NIST's own staff, works of the US government (17 U.S.C. "
                   "105, checked on govinfo.gov's policies page at every build); NIST notes they may be subject to "
                   "foreign copyright.",
    "making_military": "TC 9-524, TM 10-445 and Machinery Repairman: works of the US Army and Navy read from the "
                       "Internet Archive; the builder reads each one's front pages and follows the shared release "
                       "rule (military_release.py).",
    "making_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build); "
                        "archive.org's robots.txt allows the files; no AI rules (checked 2026-11-22).",
    "making_index": "The index (make:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("RepRap wiki (reprap.org)", "GNU FDL, but its robots.txt shuts out AI readers (GPTBot, ClaudeBot and others), "
     "so the builder does not read it. Link-only. Index: https://reprap.org/wiki/RepRap"),
    ("Marlin firmware documentation (marlinfw.org)", "GPL, but its robots.txt says \"ai-train=no\" and shuts out AI "
     "readers; not copied, not even from its GitHub repository. Link-only. Index: "
     "https://marlinfw.org/docs/basics/introduction.html"),
    ("Prusa Knowledge Base (help.prusa3d.com)", "\"(c) Prusa Research a.s.\" on every page; link-only for Program "
     "Downloader. Index: https://help.prusa3d.com/"),
    ("GRBL wiki (github.com/gnea/grbl/wiki)", "GitHub's robots.txt does not allow programs to read wiki pages, and "
     "the wiki states no licence of its own. Link-only. Index: https://github.com/gnea/grbl/wiki"),
    ("Inkscape manual (the Inkscape Beginners' Guide on Read the Docs, CC BY-SA, and Tavmjong Bah's manual)", "Not "
     "reachable on 2026-11-22 (Read the Docs answered 404, tavmjong.free.fr did not answer); the tutorials listed on "
     "inkscape.org/learn carry \"All Rights Reserved\" marks. Link-only. Index: https://inkscape.org/learn/"),
    ("LaserGRBL documentation (lasergrbl.com)", "The program is GPL, but its web pages state no licence; link-only. "
     "Index: https://lasergrbl.com/usage/"),
    ("OSHA laser hazards, machine guarding and hand and power tools pages", "Public domain, but www.osha.gov refuses "
     "programs (robots.txt and 403); OSHA's machine safeguarding booklets are in the manual collections. Link-only. "
     "Index: https://www.osha.gov/laser-hazards and https://www.osha.gov/machine-guarding"),
    ("America Makes guides and the DOE additive manufacturing pages", "America Makes' guides are its members' "
     "copyright (americamakes.us also refuses programs in its robots.txt); the Department of Energy's additive "
     "manufacturing pages were not looked at one by one in this version. Link-only. Index: "
     "https://www.americamakes.us/ and https://www.energy.gov/eere/ammto/additive-manufacturing"),
    ("NIST roadmaps prepared by outside authors (such as NIST AMS 100-2, \"Prepared for\" NIST \"by\" Joan "
     "Pellegrino and others)", "Prepared for NIST by authors outside NIST, so not plainly a US government work; "
     "NIST's own staff publications are built. Index: https://www.nist.gov/additive-manufacturing"),
    ("Makers' documentation (Cricut Design Space, Silhouette Studio, LightBurn, Tinkercad, Glowforge, xTool, Bambu "
     "Lab, Creality, Elegoo, Anycubic, Shapeoko, Sherline, Taig, Grizzly)", "The makers' copyright; listed as links "
     "in the index (make:index) and in the manual collections under the heading Home manufacturing and making, for "
     "the owner to fetch with Program Downloader. Index: https://help.cricut.com/ and "
     "https://docs.lightburnsoftware.com/"),
    ("Thingiverse, Printables and Instructables", "Each project under its maker's own licence (many non-commercial) "
     "and the sites' terms were not checked one by one; not built. Index: https://www.printables.com/"),
    ("Wikibooks Machining and Inkscape", "Their main pages list no chapters a reader can follow (checked 2026-11-22); "
     "not built. Index: https://en.wikibooks.org/wiki/Machining"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
