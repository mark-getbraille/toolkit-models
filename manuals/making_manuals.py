"""Manual collections for HOME MANUFACTURING AND MAKING, under their own heading (the owner's request of 2026-11-22:
3D printers, cutting machines and heat presses, laser engravers and CNC machines, small lathes and mills, and moulding
and casting). categories.py adds them to CATEGORIES with the field "heading": "Home manufacturing and making"
(build_manuals.write puts it in the index and the manifest, so the toolkit can list them together).

  printers_3d         FDM (FFF) and resin 3D printers, their filament and resin: the Internet Archive's manuals
                      searched with PRINTER_WORDS, the makers' pages as links (Prusa, Bambu Lab, Creality, Elegoo,
                      Anycubic, UltiMaker and MakerBot, Formlabs, FlashForge, LulzBot, Sovol, Voron);
  heat_press_vinyl    heat presses, vinyl cutters and plotters, heat-transfer vinyl and sublimation printers (Roland
                      DGA, Graphtec, USCutter, Sawgrass, Siser, Stahls' Hotronix); Cricut, Silhouette, Brother
                      ScanNCut and Sizzix are linked by the arts and crafts collection craft_machines, not repeated;
  laser_cnc_making    diode, CO2 and fibre laser engravers, desktop CNC machines, their controllers (GRBL, LinuxCNC,
                      Mach3) and PCB milling (xTool, OMTech, Ortur, Atomstack, Snapmaker, LightBurn, Epilog,
                      Inventables, Onefinity, Avid CNC, SainSmart Genmitsu, BobsCNC); Glowforge and Carbide 3D
                      (Shapeoko) are linked by the woodshop collection woodshop_machines, not repeated;
  small_machining     mini lathes, mini mills, bench and watchmaker's lathes and their accessories (Sherline, Taig,
                      Little Machine Shop, Precision Matthews, Proxxon); full-size metal lathes, mills and the Army and
                      Navy machinist manuals are in metal_shop_welding, drill presses and bandsaws in
                      woodshop_machines, not repeated;
  moulding_casting    vacuum formers, small injection moulders and mould-making and casting supplies (Smooth-On,
                      Alumilite, Polytek, Mayku, Formech, APSX).

What each lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker, as in every
manual collection): by the owner's rule the makers' own manual libraries are LINK-ONLY, as in power_manuals.py:
nothing is read from their sites, their pages are listed for the person (or the personal assistant) to open or fetch
with Program Downloader. The Internet Archive words are new: no other collection searches them (woodshop_machines
already searches "cnc router", "laser engraver", "laser cutter", "drill press" and "wood lathe", metal_shop_welding
"metal lathe" and "milling machine", craft_machines "cricut", "silhouette cameo" and "die cutting", sewing_textile
"embroidery machine"); the self-test checks.

The safety notice of each category is written into its index, for the toolkit to say first: hot nozzles, fire and
fumes; resin on skin; laser eye safety, fire and never PVC or vinyl (chlorine gas); rotating machinery; heat presses;
molten metal and casting chemicals.
"""

HEADING = "Home manufacturing and making"

PRINTER_NOTICE = ("Read the safety section first. A 3D printer's nozzle and bed are hot enough to burn; never leave a "
                  "running printer where you cannot check it, keep it on a surface that does not burn with a smoke "
                  "alarm nearby, and print with fresh air (melting plastic gives off fumes and fine particles). "
                  "Liquid resin harms skin and eyes: wear nitrile gloves and eye protection, ventilate, and cure "
                  "resin waste before throwing it away.")
VINYL_NOTICE = ("Read the safety section first. A heat press's plate is hot enough to burn: keep hands clear when "
                "closing it and never leave it switched on alone. Cutter and weeding blades are very sharp. "
                "Sublimation inks and coatings need the ventilation their labels give.")
LASER_CNC_NOTICE = ("Read the safety section first. Never look into a laser beam or its reflection; wear eye "
                    "protection rated for the laser's wavelength (open-frame hobby lasers are usually Class 4: they "
                    "can blind in an instant and start fires); never leave a running laser, keep a fire extinguisher "
                    "close, and vent the fumes outdoors. Never cut or engrave PVC or vinyl: they give off chlorine "
                    "gas. A CNC spindle and its bit can throw chips and catch clothing: wear safety glasses and "
                    "hearing protection, keep hands away while it runs, and know where the emergency stop is.")
MACHINING_NOTICE = ("Read the safety section first. Wear safety glasses; no gloves, loose sleeves, jewellery or "
                    "untied long hair near a spinning chuck or cutter; take the chuck key out before starting, keep "
                    "the guards on, and stop the machine before measuring or clearing chips.")
CASTING_NOTICE = ("Read the safety section first. Molten metal burns and can explode when it meets water or a damp "
                  "mould: keep everything dry and wear face, foot and body protection. Casting resins and silicone "
                  "need nitrile gloves, eye protection and ventilation; read each product's safety data sheet. "
                  "Vacuum former heaters and hot plastic burn.")

PRINTER_WORDS = ["3d printer", "3d printing", "reprap", "makerbot", "ultimaker", "prusa", "creality",
                 "resin printer", "stereolithography", "fused deposition"]
VINYL_WORDS = ["heat press", "vinyl cutter", "cutting plotter", "vinyl plotter", "sublimation", "heat transfer vinyl",
               "graphtec"]
LASER_CNC_WORDS = ["co2 laser", "fiber laser", "diode laser", "laser engraving", "grbl", "linuxcnc", "mach3",
                   "cnc mill", "cnc machine", "desktop cnc", "pcb milling", "reflow oven"]
MACHINING_WORDS = ["mini lathe", "mini mill", "bench lathe", "watchmaker lathe", "sherline", "taig", "unimat",
                   "myford", "atlas lathe", "milling attachment", "dividing head", "rotary table"]
CASTING_WORDS = ["vacuum former", "vacuum forming", "injection molding", "injection moulding", "mold making",
                 "mould making", "silicone mold", "casting resin", "sand casting", "metal casting", "foundry"]

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is listed "
        "for the person to open or fetch with Program Downloader")


def _makers(category, prefix, documents, makers):
    """The makers of one category (all link-only), with the shared fields."""
    return [dict(category=category, prefix=prefix, types=[], documents=documents, access="link", reason=RULE, **m)
            for m in makers]


PRINTER_MAKERS = _makers("printers_3d", "p3", "manuals, assembly guides and knowledge bases", [
    dict(key="prusa", maker="Prusa Research (Original Prusa printers, PrusaSlicer, Knowledge Base)",
         type="3D printer", library="https://help.prusa3d.com/", site="help.prusa3d.com"),
    dict(key="bambu-lab", maker="Bambu Lab (Bambu Lab Wiki)", type="3D printer", library="https://wiki.bambulab.com/",
         site="wiki.bambulab.com"),
    dict(key="creality", maker="Creality (Ender and K series)", type="3D printer",
         library="https://www.creality.com/pages/download", site="creality.com"),
    dict(key="elegoo", maker="Elegoo (resin and FDM printers)", type="3D printer",
         library="https://www.elegoo.com/pages/download", site="elegoo.com"),
    dict(key="anycubic", maker="Anycubic (resin and FDM printers)", type="3D printer",
         library="https://www.anycubic.com/", site="anycubic.com"),
    dict(key="ultimaker", maker="UltiMaker (UltiMaker and MakerBot printers, Cura)", type="3D printer",
         library="https://ultimaker.com/", site="ultimaker.com"),
    dict(key="formlabs", maker="Formlabs (resin printers)", type="resin 3D printer",
         library="https://support.formlabs.com/", site="support.formlabs.com"),
    dict(key="flashforge", maker="FlashForge", type="3D printer", library="https://www.flashforge.com/",
         site="flashforge.com"),
    dict(key="lulzbot", maker="LulzBot (open-hardware printers)", type="3D printer", library="https://lulzbot.com/",
         site="lulzbot.com"),
    dict(key="sovol", maker="Sovol", type="3D printer", library="https://www.sovol3d.com/", site="sovol3d.com"),
    dict(key="voron", maker="Voron Design (open-source printer kits; build guides)", type="3D printer kit",
         library="https://docs.vorondesign.com/", site="docs.vorondesign.com"),
])
VINYL_MAKERS = _makers("heat_press_vinyl", "hv", "manuals and user guides", [
    dict(key="roland-dga", maker="Roland DGA (vinyl cutters and printer-cutters)", type="vinyl cutter",
         library="https://www.rolanddga.com/", site="rolanddga.com"),
    dict(key="graphtec", maker="Graphtec America (cutting plotters)", type="cutting plotter",
         library="https://www.graphtecamerica.com/", site="graphtecamerica.com"),
    dict(key="uscutter", maker="USCutter (vinyl cutters and heat presses)", type="vinyl cutter",
         library="https://www.uscutter.com/", site="uscutter.com"),
    dict(key="sawgrass", maker="Sawgrass (sublimation printers)", type="sublimation printer",
         library="https://www.sawgrassink.com/", site="sawgrassink.com"),
    dict(key="siser", maker="Siser (heat-transfer vinyl application guides)", type="heat-transfer vinyl",
         library="https://www.siserna.com/", site="siserna.com"),
    dict(key="stahls", maker="Stahls' (Hotronix heat presses)", type="heat press", library="https://www.stahls.com/",
         site="stahls.com"),
])
LASER_CNC_MAKERS = _makers("laser_cnc_making", "lc", "manuals, user guides and software documentation", [
    dict(key="xtool", maker="xTool (diode, CO2 and fibre laser engravers)", type="laser engraver",
         library="https://support.xtool.com/", site="support.xtool.com"),
    dict(key="omtech", maker="OMTech (CO2 and fibre lasers)", type="laser engraver",
         library="https://omtechlaser.com/", site="omtechlaser.com"),
    dict(key="ortur", maker="Ortur (diode laser engravers)", type="laser engraver", library="https://ortur.net/",
         site="ortur.net"),
    dict(key="atomstack", maker="Atomstack (diode laser engravers)", type="laser engraver",
         library="https://www.atomstack.com/", site="atomstack.com"),
    dict(key="snapmaker", maker="Snapmaker (3D printing, laser and CNC machines)", type="3-in-1 machine",
         library="https://www.snapmaker.com/", site="snapmaker.com"),
    dict(key="lightburn", maker="LightBurn Software (laser control program; copyright)", type="laser software",
         library="https://docs.lightburnsoftware.com/", site="docs.lightburnsoftware.com"),
    dict(key="epilog", maker="Epilog Laser", type="laser engraver", library="https://www.epiloglaser.com/",
         site="epiloglaser.com"),
    dict(key="inventables", maker="Inventables (X-Carve, Easel)", type="desktop CNC",
         library="https://www.inventables.com/", site="inventables.com"),
    dict(key="onefinity", maker="Onefinity CNC", type="desktop CNC", library="https://www.onefinitycnc.com/",
         site="onefinitycnc.com"),
    dict(key="avid-cnc", maker="Avid CNC", type="CNC router", library="https://www.avidcnc.com/", site="avidcnc.com"),
    dict(key="sainsmart", maker="SainSmart (Genmitsu desktop CNC and lasers)", type="desktop CNC",
         library="https://www.sainsmart.com/", site="sainsmart.com"),
    dict(key="bobscnc", maker="BobsCNC", type="desktop CNC", library="https://www.bobscnc.com/", site="bobscnc.com"),
])
MACHINING_MAKERS = _makers("small_machining", "sm", "manuals, instructions and accessory guides", [
    dict(key="sherline", maker="Sherline Products (miniature lathes and mills)", type="mini lathe and mill",
         library="https://www.sherline.com/", site="sherline.com"),
    dict(key="taig", maker="Taig Tools (micro lathes and mills)", type="mini lathe and mill",
         library="https://www.taigtools.com/", site="taigtools.com"),
    dict(key="little-machine-shop", maker="LittleMachineShop.com (mini lathe and mini mill guides and parts)",
         type="mini lathe and mill", library="https://www.littlemachineshop.com/", site="littlemachineshop.com"),
    dict(key="precision-matthews", maker="Precision Matthews (bench lathes and mills)", type="bench lathe and mill",
         library="https://www.precisionmatthews.com/", site="precisionmatthews.com"),
    dict(key="proxxon", maker="Proxxon (micro lathes, mills and bench tools)", type="micro lathe and mill",
         library="https://www.proxxon.com/", site="proxxon.com"),
])
CASTING_MAKERS = _makers("moulding_casting", "mc", "instructions, technical bulletins and safety data sheets", [
    dict(key="smooth-on", maker="Smooth-On (mould rubbers, casting resins)", type="mould making supplies",
         library="https://www.smooth-on.com/", site="smooth-on.com"),
    dict(key="alumilite", maker="Alumilite (casting resins and mould rubber)", type="casting resin",
         library="https://www.alumilite.com/", site="alumilite.com"),
    dict(key="polytek", maker="Polytek Development (mould rubbers and casting plastics)", type="mould making supplies",
         library="https://www.polytek.com/", site="polytek.com"),
    dict(key="mayku", maker="Mayku (desktop vacuum formers)", type="vacuum former", library="https://www.mayku.me/",
         site="mayku.me"),
    dict(key="formech", maker="Formech (vacuum forming machines)", type="vacuum former",
         library="https://www.formech.com/", site="formech.com"),
    dict(key="apsx", maker="APSX (desktop injection moulding machines)", type="injection moulding machine",
         library="https://www.apsx.com/", site="apsx.com"),
])

LICENCE = "CC0 (facts and links); each manual belongs to its maker; the guidance pages are their publishers'"
LASER_GUIDANCE = [
    dict(title="Laser products and their hazard classes (FDA; in the reference library: make:fda_laser_safety)",
         url="https://www.fda.gov/radiation-emitting-products/home-business-and-entertainment-products/laser-"
             "products-and-instruments", by="the US Food and Drug Administration"),
    dict(title="Laser hazards (OSHA; open it in a browser: it refuses programs)", url="https://www.osha.gov/"
                                                                                       "laser-hazards",
         by="the US Occupational Safety and Health Administration"),
]
MACHINE_GUIDANCE = [
    dict(title="Machine guarding (OSHA; open it in a browser: it refuses programs)",
         url="https://www.osha.gov/machine-guarding", by="the US Occupational Safety and Health Administration"),
    dict(title="Fundamentals of Machine Tools (TC 9-524; in the reference library: make:army_tc_9_524_machine_tools)",
         url="https://archive.org/details/tc9-524", by="the US Army"),
]
CATEGORIES = {
    "printers_3d": dict(
        name="3D printers, filament and resin printers (manuals)",
        description="FDM (FFF) and resin (SLA and MSLA) 3D printers, their filament, resin, wash and cure stations "
                    "and upgrades: the Internet Archive's manuals, the makers' pages as links (Prusa, Bambu Lab, "
                    "Creality, Elegoo, Anycubic, UltiMaker and MakerBot, Formlabs, FlashForge, LulzBot, Sovol and "
                    "Voron), and the guidance. The Klipper, FreeCAD and OpenSCAD documentation is in the reference "
                    "library (request word making).",
        kind="manuals", licence=LICENCE, any_year=True, ia=PRINTER_WORDS, makers=PRINTER_MAKERS,
        notice=PRINTER_NOTICE, heading=HEADING,
        ia_exclude=r"\b(sega|video game|game manual|lucas ?arts|3d glasses|3d television|3d tv)\b",
        guidance=[dict(title="Additive manufacturing (NIST; its own publications are in the reference library, "
                             "request word making)", url="https://www.nist.gov/additive-manufacturing",
                       by="the National Institute of Standards and Technology"),
                  dict(title="Indoor air quality (EPA)", url="https://www.epa.gov/indoor-air-quality-iaq",
                       by="the US Environmental Protection Agency")]),
    "heat_press_vinyl": dict(
        name="Heat presses, vinyl cutters and sublimation printers (manuals)",
        description="Heat presses (clamshell, swing-away, mug and hat presses), vinyl cutters and cutting plotters, "
                    "heat-transfer vinyl and sublimation printers: the Internet Archive's manuals and the makers' "
                    "pages as links (Roland DGA, Graphtec, USCutter, Sawgrass, Siser, Stahls' Hotronix). Cricut, "
                    "Silhouette, Brother ScanNCut and Sizzix are in Craft machines (craft_machines).",
        kind="manuals", licence=LICENCE, any_year=True, ia=VINYL_WORDS, makers=VINYL_MAKERS, notice=VINYL_NOTICE,
        heading=HEADING, ia_exclude=r"\b(sega|video game|game manual|printing press|offset press|press release)\b"),
    "laser_cnc_making": dict(
        name="Laser engravers, desktop CNC machines and their controllers (manuals)",
        description="Diode, CO2 and fibre laser engravers and cutters, desktop CNC routers and mills, their "
                    "controllers and programs (GRBL, LinuxCNC, Mach3, LightBurn) and PCB milling: the Internet "
                    "Archive's manuals, the makers' pages as links (xTool, OMTech, Ortur, Atomstack, Snapmaker, "
                    "LightBurn, Epilog, Inventables, Onefinity, Avid CNC, SainSmart Genmitsu, BobsCNC), and the laser "
                    "and machine guidance. Glowforge and Carbide 3D (Shapeoko) are in Woodshop machines "
                    "(woodshop_machines).",
        kind="manuals", licence=LICENCE, any_year=True, ia=LASER_CNC_WORDS, makers=LASER_CNC_MAKERS,
        notice=LASER_CNC_NOTICE, heading=HEADING,
        ia_exclude=r"\b(sega|video game|game manual|laser ?disc|laser printer|laserjet|laser tag|medical laser)\b",
        guidance=LASER_GUIDANCE + MACHINE_GUIDANCE[:1]),
    "small_machining": dict(
        name="Mini lathes, mini mills and bench machines for small machining (manuals)",
        description="Mini and micro lathes, mini mills, bench and watchmaker's lathes, and their accessories "
                    "(chucks, rotary tables, dividing heads, milling attachments): the Internet Archive's manuals "
                    "and the makers' pages as links (Sherline, Taig, LittleMachineShop.com, Precision Matthews, "
                    "Proxxon). Full-size metal lathes, mills and the Army and Navy machinist manuals are in Metal "
                    "shop machines and welding (metal_shop_welding); drill presses and bandsaws in Woodshop machines "
                    "(woodshop_machines).",
        kind="manuals", licence=LICENCE, any_year=True, ia=MACHINING_WORDS, makers=MACHINING_MAKERS,
        notice=MACHINING_NOTICE, heading=HEADING,
        ia_exclude=r"\b(sega|video game|game manual|taiga|rotary table ?game|dining table)\b",
        guidance=MACHINE_GUIDANCE),
    "moulding_casting": dict(
        name="Vacuum formers, injection moulders, mould making and casting (manuals)",
        description="Desktop vacuum formers, small injection moulding machines, and mould-making rubbers, casting "
                    "resins and metal casting: the Internet Archive's manuals and guides, and the makers' pages as "
                    "links (Smooth-On, Alumilite, Polytek, Mayku, Formech, APSX). Resin crafts supplies' safety data "
                    "sheets are in Art and craft supplies (art_craft_supplies).",
        kind="manuals", licence=LICENCE, any_year=True, ia=CASTING_WORDS, makers=CASTING_MAKERS,
        notice=CASTING_NOTICE, heading=HEADING, ia_exclude=r"\b(sega|video game|game manual|type ?foundry|font)\b"),
}
