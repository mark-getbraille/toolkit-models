"""Arts and crafts equipment in the manual library (the owner's request of 2026-11-22; pottery and jewellery are
collections of their own, as the owner asked). categories.py adds the three collections; build_manuals.py builds
them. An INDEX of facts and links only: each manual belongs to its maker.

  pottery_kilns       pottery and glass kilns, kiln controllers and potter's wheels: Skutt, L&L, Paragon, Olympic,
                      Evenheat, Cone Art, Jen-Ken, Shimpo, Brent (AMACO), Speedball, Pacifica;
  jewellery_tools     jewellery and lapidary equipment: flexible-shaft motors, rolling mills, torches, ultrasonic
                      cleaners, rock tumblers, cabbing and faceting machines: Foredom, Durston, Pepetools, Smith
                      Equipment, Lortone, Covington, Diamond Pacific, Ultra Tec;
  craft_machines      cutting machines, die cutters, airbrushes, wood-burning tools and bookbinding presses: Cricut,
                      Silhouette, Brother ScanNCut, Sizzix, Iwata, Badger, Paasche, Walnut Hollow, Colwood.
All three, with the sewing, textile tool, art supply and heat press collections, are under the heading "Arts and
crafts" (HEADING, HEADING_KEYS). Every maker is LINK ONLY in this first version (their terms were not checked one by one, so nothing is read; each
library is listed for the person to open in a browser). The Internet Archive's manuals are searched with each
collection's words. The safety data sheets of glazes, paints, resins and soaps are in the collection
art_craft_supplies (chemicals.py), not here. Guidance: CPSC's page on art materials and the federal labelling law
(LHAMA), and NIOSH's page on kiln and ceramic hazards, linked for the person to open.
"""

# Arts and crafts is a heading of its own in the manual library (the owner's request of 22 November 2026: a top-level
# section). categories.py gives every collection in HEADING_KEYS the field "heading" (as power and making do); the
# keys do not change. Craft machines (Cricut, Silhouette) and heat presses and vinyl cutters (heat_press_vinyl) moved
# here from "Home manufacturing and making": heat presses, heat-transfer vinyl and sublimation are mostly used to
# decorate shirts, bags, mugs and signs, which is craft work, and Cricut's own heat presses are already in
# craft_machines; the laser engravers, CNC, 3D printers, woodshop and metal shop stay under making.
HEADING = "Arts and crafts"
HEADING_KEYS = ("sewing_textile", "textile_craft_tools", "art_craft_supplies", "pottery_kilns", "jewellery_tools",
                "craft_machines", "heat_press_vinyl")

INDEX_LICENCE = "CC0 (facts and links); each manual belongs to its maker"
LINK_REASON = ("listed for the person to open in a browser; nothing is read from its site in this first version "
               "(its terms were not checked one by one)")


def _makers(category, prefix, makers):
    """The makers of one collection, all link only, with the shared fields."""
    return [dict(prefix=prefix, types=[], documents="manuals", category=category, access="link", reason=LINK_REASON,
                 **m) for m in makers]


POTTERY_MAKERS = _makers("pottery_kilns", "pk", [
    dict(key="skutt", maker="Skutt", type="kiln and potter's wheel", library="https://skutt.com/"),
    dict(key="ll-kilns", maker="L&L Kiln", type="kiln", library="https://hotkilns.com/"),
    dict(key="paragon", maker="Paragon Industries", type="kiln", library="https://www.paragonweb.com/"),
    dict(key="olympic-kilns", maker="Olympic Kilns", type="kiln", library="https://greatkilns.com/"),
    dict(key="evenheat", maker="Evenheat", type="kiln (glass and ceramics)", library="https://www.evenheat-kiln.com/"),
    dict(key="cone-art", maker="Cone Art Kilns", type="kiln", library="https://www.coneartkilns.com/"),
    dict(key="jen-ken", maker="Jen-Ken Kilns", type="kiln", library="https://www.jenkenkilns.com/"),
    dict(key="shimpo", maker="Shimpo Ceramics", type="potter's wheel", library="https://www.shimpoceramics.com/"),
    dict(key="brent-amaco", maker="Brent (AMACO)", type="potter's wheel", library="https://www.amaco.com/"),
    dict(key="speedball", maker="Speedball", type="potter's wheel and art supplies",
         library="https://www.speedballart.com/"),
    dict(key="pacifica", maker="Pacifica (Laguna Clay)", type="potter's wheel", library="https://www.lagunaclay.com/"),
])
JEWELLERY_MAKERS = _makers("jewellery_tools", "jt", [
    dict(key="foredom", maker="Foredom", type="flexible-shaft motor", library="https://www.foredom.net/"),
    dict(key="durston", maker="Durston Tools", type="rolling mill", library="https://www.durston.co.uk/"),
    dict(key="pepetools", maker="Pepetools", type="jewellery press and tools", library="https://pepetools.com/"),
    dict(key="smith-equipment", maker="Smith Equipment (jewellers' torches)", type="torch",
         library="https://www.smithequipment.com/"),
    dict(key="lortone", maker="Lortone", type="rock tumbler", library="https://www.lortone.com/"),
    dict(key="covington", maker="Covington Engineering", type="lapidary machine", library="https://covington-engineering.com/"),
    dict(key="diamond-pacific", maker="Diamond Pacific", type="lapidary machine", library="https://www.diamondpacific.com/"),
    dict(key="ultra-tec", maker="Ultra Tec", type="faceting machine", library="https://www.ultratec-facet.com/"),
])
CRAFT_MAKERS = _makers("craft_machines", "cm", [
    dict(key="cricut", maker="Cricut", type="cutting machine", library="https://help.cricut.com/"),
    dict(key="silhouette", maker="Silhouette America", type="cutting machine",
         library="https://www.silhouetteamerica.com/"),
    dict(key="brother-scanncut", maker="Brother (ScanNCut)", type="cutting machine",
         library="https://support.brother.com/"),
    dict(key="sizzix", maker="Sizzix", type="die-cutting machine", library="https://www.sizzix.com/"),
    dict(key="iwata", maker="Iwata", type="airbrush", library="https://www.iwata-airbrush.com/"),
    dict(key="badger", maker="Badger Air-Brush", type="airbrush", library="https://www.badgerairbrush.com/"),
    dict(key="paasche", maker="Paasche", type="airbrush", library="https://www.paascheairbrush.com/"),
    dict(key="walnut-hollow", maker="Walnut Hollow", type="wood-burning tool", library="https://www.walnuthollow.com/"),
    dict(key="colwood", maker="Colwood", type="wood-burning tool", library="https://woodburning.com/"),
])

KILN_NOTICE = ("Read the safety section first. A kiln gets extremely hot and gives off fumes: install it with the "
               "clearances and ventilation its manual gives, on its own circuit as the manual says, away from anything "
               "that burns; never open it hot; wear heat-resistant gloves and eye protection. Dry clay and glaze dust "
               "contains silica: clean up wet.")
JEWELLERY_NOTICE = ("Read the safety section first. Torches, hot metal and pickling acid burn: work on a fireproof "
                    "surface with ventilation and eye protection; keep hair and sleeves away from spinning tools; "
                    "never use cyanide or mercury methods from old books.")
CRAFT_NOTICE = ("Read the safety section first. Cutting blades are very sharp; airbrush paints and solvents need "
                "ventilation and a respirator; wood-burning tips are hot enough to burn at a touch.")
GUIDANCE = [
    dict(title="Art materials and the labelling law (LHAMA) (US Consumer Product Safety Commission)",
         url="https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Art-Materials",
         by="the US Consumer Product Safety Commission"),
    dict(title="Silica and ceramics: workplace hazards (NIOSH)", url="https://www.cdc.gov/niosh/silica/",
         by="the US National Institute for Occupational Safety and Health"),
]

CATEGORIES = {
    "pottery_kilns": dict(
        name="Pottery: kilns, kiln controllers and potter's wheels (manuals)",
        description="Electric kilns for pottery and glass, kiln controllers and potter's wheels: Skutt, L&L, "
                    "Paragon, Olympic, Evenheat, Cone Art, Jen-Ken, Shimpo, Brent, Speedball and Pacifica (links), "
                    "with the Internet Archive's manuals.",
        kind="manuals", licence=INDEX_LICENCE, makers=POTTERY_MAKERS,
        ia=["kiln", "pottery wheel", "potter's wheel", "kiln controller", "kiln sitter", "glass kiln", "pug mill",
            "slab roller", "clay extruder"], guidance=GUIDANCE, notice=KILN_NOTICE),
    "jewellery_tools": dict(
        name="Jewellery making and lapidary equipment (manuals)",
        description="Flexible-shaft motors, rolling mills, jewellers' torches, ultrasonic cleaners, rock tumblers, "
                    "cabbing and faceting machines: Foredom, Durston, Pepetools, Smith, Lortone, Covington, Diamond "
                    "Pacific and Ultra Tec (links), with the Internet Archive's manuals.",
        kind="manuals", licence=INDEX_LICENCE, makers=JEWELLERY_MAKERS,
        ia=["rock tumbler", "lapidary", "faceting machine", "rolling mill", "flex shaft", "flexible shaft",
            "ultrasonic cleaner", "jewelry torch", "bead loom"], guidance=GUIDANCE[:1], notice=JEWELLERY_NOTICE),
    "craft_machines": dict(
        name="Craft machines: cutting machines, die cutters, airbrushes and wood-burning tools (manuals)",
        description="Electronic cutting machines, die cutters, airbrushes, wood-burning tools and bookbinding "
                    "presses: Cricut, Silhouette, Brother ScanNCut, Sizzix, Iwata, Badger, Paasche, Walnut Hollow "
                    "and Colwood (links), with the Internet Archive's manuals.",
        kind="manuals", licence=INDEX_LICENCE, makers=CRAFT_MAKERS,
        ia=["cricut", "silhouette cameo", "scanncut", "die cutting", "die cut machine", "airbrush", "wood burning",
            "woodburning", "pyrography", "book press"], guidance=GUIDANCE[:1], notice=CRAFT_NOTICE),
}
