"""HOME REPAIR, UPKEEP AND THE TEXTILE CRAFTS for the Picture Model Training Kit (the owner's request of
2026-11-22). This file lists:
  - the ready-made packs built in packs/ (group "permissive"; the kit downloads them with prepare_pack):
      home_upkeep_packs.py     commons_home_repair, commons_locks_engines_bikes, commons_pest_control,
                               open_images_home_upkeep
      textile_crafts_packs.py  commons_knit_crochet_lace, commons_quilt_embroidery_weaving, commons_sewing_mending,
                               commons_upholstery_leather_shoes, commons_fabrics_fibres, open_images_textile_crafts,
                               nmah_textiles_sewing
      heating_packs.py         commons_home_heating, commons_firewood, open_images_home_heating (emergency and
                               secondary heating, added to the request the same day)
      lighting_packs.py        commons_emergency_lighting, open_images_emergency_lighting (emergency and backup
                               lighting, added the same day)
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sign-up collections and the sources looked at and left out, with the reason (HOME_CRAFTS_SIGN_UP,
    HOME_CRAFTS_NOT_INCLUDED).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked, a museum
record); the safety notes on electrical work, gas, ladders and roofs, engines, pesticides and traps, stings, lead and
mould are the same words as in packs/home_upkeep_packs.py.

Picture-making (HOME_CRAFTS_PICTURE_MAKING_OK): only the fabrics and fibres (cloth and fibre close up), the
Smithsonian's museum textiles and tools, and the share-alike textile files may be used; sources.py puts every other
key in NOT_FOR_PICTURE_MAKING (people work, craft or sew in many of the photos; pests and poisons are not for making).

    python -c "import sources, home_crafts_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

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

# The same words as packs/home_upkeep_packs.py (the self-test checks they match).
LADDER_NOTE = ("Ladder and roof safety: falls from ladders and roofs cause serious injuries; set a ladder on firm, "
               "level ground, keep three points of contact, stay off wet or steep roofs, and have someone with you.")
ENGINE_NOTE = ("Engine safety: run petrol engines only outdoors (their exhaust carbon monoxide can kill), let them "
               "cool before refuelling, and disconnect the spark plug before working on a blade.")
PESTICIDE_NOTE = ("Pesticide safety: read and follow the whole label (the label is the law), keep the product away "
                  "from children and pets, and store it in its original container. Poison Control: 1-800-222-1222 "
                  "in the US.")
TRAP_NOTE = ("Set traps and bait stations where children and pets cannot reach them. Do not sweep or vacuum rodent "
             "droppings dry: wear gloves, wet them with disinfectant first, then wipe them up (CDC advice).")
MOULD_NOTE = ("Fix the source of the moisture first; the EPA advises that mould covering more than about 10 square "
              "feet is best cleaned up by a professional.")

HEAT_SAFETY = ("Heating safety: keep anything that can burn at least 3 feet (1 metre) away. Stoves, fireplaces and "
               "fuel-burning heaters make carbon monoxide, which can kill: have a working carbon monoxide alarm, "
               "never use outdoor heaters, grills or generators indoors, and if the alarm sounds or anyone feels ill "
               "(headache, dizziness, nausea), get everyone out and call 911. Gas lines, gas appliances and stove "
               "installation are work for a qualified professional.")
FIREWOOD_NOTE = ("Burn only dry, seasoned wood and keep the woodpile at least 3 feet from the stove. Don't move "
                 "firewood: buy or gather it near where you burn it, so pests such as the emerald ash borer are not "
                 "spread (USDA APHIS).")
FUEL_LIGHT_NOTE = ("Fuel lamp safety: fuel lanterns and lamps can start fires and make carbon monoxide, which can "
                   "kill. Use them outdoors or with good ventilation, as the maker says; never refuel one that is hot "
                   "or lit; use only the fuel the lamp is made for; keep it away from children, pets and curtains. "
                   "Battery lights are safer indoors during a power cut.")
CANDLE_NOTE = ("Candle safety: never leave a candle burning unattended or while you sleep; use a sturdy holder and keep "
               "it at least 1 foot (30 cm) from anything that can burn and away from children and pets. During a "
               "power cut, use battery lights instead of candles (CDC, FEMA and Red Cross advice).")

def thing(category, words, note="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the note."""
    return (category, "What is this?", f"This is {words}." + (f" {note}" if note else ""), deeper)


def fabric(category, words, deeper=False):
    """(category, question, answer, deeper) for a fabric: "What fabric is this?" -> "It is <words>."."""
    return (category, "What fabric is this?", f"It is {words}.", deeper)


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

# The main categories of packs/home_upkeep_packs.py (the broad scene categories are left out: the share-alike entry
# has no word filter).
HOME_UPKEEP_SA = [
    thing("Toilet tanks", "a toilet tank (cistern), which holds the water for the flush", deeper=True),
    thing("Faucet aerators", "a tap (faucet) aerator"),
    thing("Draught excluders", "a draught excluder, which stops cold air coming in under or around a door"),
    thing("Rain gutters", "a rain gutter, which carries rain from the edge of the roof to the downspout",
          LADDER_NOTE),
    thing("Slate roofs", "a slate roof", LADDER_NOTE),
    thing("Laminate flooring", "laminate flooring", deeper=True),
    thing("Linoleum", "linoleum flooring"),
    thing("Damp", "damp in a building: moisture and the stains or mould it brings", MOULD_NOTE, deeper=True),
    thing("Pin tumbler locks", "a pin tumbler lock", deeper=True),
    thing("Key blanks", "key blanks: uncut keys that a locksmith cuts to fit a lock"),
    thing("Two-stroke engines", "a two-stroke engine", ENGINE_NOTE),
    thing("Bicycle pumps", "a bicycle pump", deeper=True),
    thing("Chain tools", "a chain tool, which pushes a pin out to break or join a bicycle chain", deeper=True),
    thing("Rat traps", "a rat trap", TRAP_NOTE, deeper=True),
    thing("Rodenticides", "rat or mouse poison (a rodenticide)", PESTICIDE_NOTE + " " + TRAP_NOTE),
    thing("Bat houses", "a bat house, a box where bats can roost instead of in a building", deeper=True),
]

# The main categories of packs/textile_crafts_packs.py.
TEXTILE_CRAFTS_SA = [
    thing("Knitting needles", "a pair of knitting needles", deeper=True),
    thing("Crochet hooks", "a crochet hook", deeper=True),
    thing("Granny squares", "a granny square: a crocheted square of rounds"),
    thing("Lace bobbins", "lace bobbins, which hold the threads for bobbin lace"),
    thing("Quilts", "a quilt", deeper=True),
    thing("Patchwork quilts", "a patchwork quilt", deeper=True),
    thing("Embroidery hoops", "an embroidery hoop, two rings that hold fabric taut for stitching"),
    thing("Spinning wheels", "a spinning wheel, for twisting fibre into yarn", deeper=True),
    thing("Drop spindles", "a drop spindle, a weighted stick for spinning yarn by hand", deeper=True),
    thing("Weaving shuttles", "a weaving shuttle, which carries the weft thread across the loom", deeper=True),
    thing("Skeins", "a skein of yarn", deeper=True),
    thing("Darning mushrooms", "a darning mushroom, held inside a sock or sleeve while it is darned"),
    thing("Snap fasteners", "a snap fastener (press stud)", deeper=True),
    thing("Upholstery tools", "an upholstery tool", deeper=True),
    fabric("Seersucker", "seersucker: a thin cotton cloth with puckered stripes", deeper=True),
    fabric("Calico", "calico: a plain-woven cotton cloth", deeper=True),
    fabric("Brocade", "brocade: a rich woven fabric with a raised pattern"),
    fabric("Fabric swatches", "a fabric swatch: a small sample of cloth"),
]


# The main categories of packs/heating_packs.py (the ones needing a word filter are left out).
HOME_HEATING_SA = [
    thing("Fireplaces", "a fireplace", HEAT_SAFETY),
    thing("Heating stoves", "a heating stove, which burns wood, coal or another fuel to heat a room", HEAT_SAFETY,
          deeper=True),
    thing("Coal stoves", "a coal stove", HEAT_SAFETY, deeper=True),
    thing("Tiled stoves", "a tiled stove (a masonry heater or Kachelofen)", HEAT_SAFETY, deeper=True),
    thing("Gas heaters", "a gas heater", HEAT_SAFETY, deeper=True),
    thing("Stovepipes", "a stovepipe, the metal pipe that carries smoke from a stove to the chimney", HEAT_SAFETY,
          deeper=True),
    thing("Firewood", "firewood", FIREWOOD_NOTE),
    thing("Woodpiles", "a woodpile: firewood stacked to dry", FIREWOOD_NOTE, deeper=True),
]

# The main categories of packs/lighting_packs.py (the ones needing a word filter are left out).
EMERGENCY_LIGHTING_SA = [
    thing("Flashlights", "a flashlight (torch)"),
    thing("Kerosene lamps", "a kerosene lamp, with a wick and a glass chimney", FUEL_LIGHT_NOTE, deeper=True),
    thing("Hurricane lamps", "a hurricane lamp (storm lantern)", FUEL_LIGHT_NOTE, deeper=True),
    thing("Gas mantles", "a gas mantle for a gas or pressure lantern", FUEL_LIGHT_NOTE, deeper=True),
    thing("Petromax lamps", "a Petromax pressure lantern", FUEL_LIGHT_NOTE),
    thing("Candles", "a candle", CANDLE_NOTE),
    thing("Candle holders", "a candle holder", CANDLE_NOTE),
]

def prepare_home_upkeep_commons_sa(source, data_dir, work, cap):
    """Commons home repair, lock, engine, bicycle tool and pest control categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(HOME_UPKEEP_SA, cap, source.test, "upkeep-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_textile_crafts_commons_sa(source, data_dir, work, cap):
    """Commons knitting, crochet, lace, quilting, embroidery, spinning, weaving, notion and fabric categories, files
    under CC BY-SA or GFDL."""
    items = commons_sa_items(TEXTILE_CRAFTS_SA, cap, source.test, "textile-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)



def prepare_home_heating_commons_sa(source, data_dir, work, cap):
    """Commons fireplace, stove, gas heater, stovepipe and firewood categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(HOME_HEATING_SA, cap, source.test, "heating-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_emergency_lighting_commons_sa(source, data_dir, work, cap):
    """Commons flashlight, kerosene and hurricane lamp, mantle, pressure lantern and candle categories, files under
    CC BY-SA or GFDL."""
    items = commons_sa_items(EMERGENCY_LIGHTING_SA, cap, source.test, "light-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)

# ----------------------------------------------------------------- the table

HOME_CRAFTS_SOURCES = [
    # ---- ready-made packs (packs/home_upkeep_packs.py)
    Source("commons_home_repair", "Home repair and upkeep: building repairs, patched pipes, plumbing tools, toilet "
                                  "tanks, drains, caulking, draught excluders, roofs and gutters, floors, floor "
                                  "sanding, glaziers, chimney sweeps, damp and cleaning, with safety notes (Wikimedia "
                                  "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 270 MB"),
    Source("commons_locks_engines_bikes", "Locks and locksmithing, key blanks and smart locks, small engines (with the "
                                          "engine safety note) and bicycle repair tools: pumps, chain tools, tyre "
                                          "levers and patches, truing stands (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_pest_control", "Pest control: rat and glue traps, rodenticides and pesticide labels (with the "
                                   "safety notes), bug zappers, fumigation, IPM, bat houses, and pantry beetles, "
                                   "woodworm, rats, fleas, dust mites, earwigs, centipedes, carpet beetles, wasps, "
                                   "ants and cockroaches by name (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 270 MB"),
    Source("open_images_home_upkeep", "Roofs, gutters, chimneys, attics and basements, flooring, plumbing and sinks, "
                                      "boilers, wiring and switches, locks and hinges, wood stain and varnish, mowers "
                                      "and snow blowers, bicycle parts, and pests and wildlife (Open Images, "
                                      "ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2500, 25, prepare_pack, "about 500 MB"),
    # ---- ready-made packs (packs/textile_crafts_packs.py)
    Source("commons_knit_crochet_lace", "Knitting, crochet, amigurumi, granny squares, tatting, bobbin and needle lace, "
                                        "macramé, knitting needles, crochet hooks, yarn and skeins (Wikimedia Commons, "
                                        "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 270 MB"),
    Source("commons_quilt_embroidery_weaving", "Quilts and patchwork, embroidery, needlepoint, smocking and sashiko, "
                                               "looms and weaving, spinning wheels and spindles, natural dyes, "
                                               "tie-dye, batik, shibori and felting (Wikimedia Commons, ready-made "
                                               "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("commons_sewing_mending", "Sewing patterns, dress forms, buttons, buttonholes, zips, snaps, hems, seams, "
                                     "thread and safety pins, mending and darning, sewing boxes and treadle machines "
                                     "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 270 MB"),
    Source("commons_upholstery_leather_shoes", "Upholstery, leatherwork, shoemaking and shoe repair, shoe polish, "
                                               "furniture restoration, cane seats and varnishing, with the finishing "
                                               "safety note (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 700, 10, prepare_pack, "about 160 MB"),
    Source("commons_fabrics_fibres", "Fabrics and fibres by name: linen, silk, tweed, taffeta, muslin, calico, jersey, "
                                     "organza, damask, brocade, chintz, seersucker, twill, nylon, rayon, wool, mohair, "
                                     "alpaca, merino, roving and swatches (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 220 MB"),
    Source("open_images_textile_crafts", "Crochet, cross-stitch, embroidery, quilts, patchwork, lace and tapestry, "
                                         "looms, thread, needles, zips and knots, and fabrics: wool, leather, denim, "
                                         "silk, velvet, satin, linen (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2000, 20, prepare_pack, "about 400 MB"),
    Source("nmah_textiles_sewing", "Museum quilts, coverlets, samplers, lace and needlework, and historic sewing "
                                   "machines, spinning wheels, looms, knitting needles and thimbles, named from each "
                                   "record (Smithsonian National Museum of American History, ready-made pack)",
           "CC0 (Smithsonian Open Access)", "National Museum of American History, Smithsonian Institution, CC0, "
           "https://www.si.edu/openaccess", "permissive", 1000, 10, prepare_pack, "about 250 MB"),
    # ---- ready-made packs (packs/heating_packs.py)
    Source("commons_home_heating", "Emergency and secondary heating: fireplaces, wood, coal and tiled stoves, gas, "
                                   "kerosene, oil and patio heaters, dampers, stovepipes, fire bricks, chimney fires, "
                                   "creosote, ash buckets, pellets and coal, each with the carbon monoxide and "
                                   "3-feet safety note (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 230 MB"),
    Source("commons_firewood", "Firewood, woodpiles, splitting mauls and wedges, firewood processors and moisture "
                               "meters, with the don't-move-firewood note (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 5, prepare_pack, "about 90 MB"),
    Source("open_images_home_heating", "Wood-burning stoves, hearths, fire screens, bellows, coal, splitting mauls, "
                                       "sawhorses and grills (outdoors only), with the safety notes (Open Images, "
                                       "ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 800, 10, prepare_pack, "about 160 MB"),
    # ---- ready-made packs (packs/lighting_packs.py)
    Source("commons_emergency_lighting", "Emergency and backup lighting: flashlights, emergency lights, glow sticks, "
                                         "power stations and batteries, Coleman, Petromax and Tilley pressure lanterns, "
                                         "kerosene, hurricane and gas lamps, mantles and wicks, candles and holders, with "
                                         "the fire, carbon monoxide and candle safety notes (Wikimedia Commons, "
                                         "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 270 MB"),
    Source("open_images_emergency_lighting", "Headlamps, oil lamps, candle holders and matches, with the safety notes "
                                             "(Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 800, 10, prepare_pack, "about 160 MB"),
    # ---- share-alike
    Source("home_upkeep_commons_sa", "Wikimedia Commons: toilet tanks, aerators, gutters, roofs, floors, damp, locks, "
                                     "key blanks, small engines, bicycle tools, rat traps, rodenticides and bat houses, "
                                     "files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_home_upkeep_commons_sa, "about 180 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
    Source("textile_crafts_commons_sa", "Wikimedia Commons: knitting needles, crochet hooks, lace bobbins, quilts, "
                                        "embroidery hoops, spinning wheels, spindles, shuttles, skeins, darning "
                                        "mushrooms, snaps, upholstery tools and fabrics, files under CC BY-SA or GFDL "
                                        "(share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 1000, 10, prepare_textile_crafts_commons_sa,
           "about 220 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
    Source("home_heating_commons_sa", "Wikimedia Commons: fireplaces, heating, coal and tiled stoves, gas heaters, "
                                      "stovepipes, firewood and woodpiles, with the safety notes, files under CC BY-SA "
                                      "or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 5, prepare_home_heating_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
    Source("emergency_lighting_commons_sa", "Wikimedia Commons: flashlights, kerosene and hurricane lamps, gas mantles, "
                                            "Petromax lanterns, candles and candle holders, with the safety notes, files "
                                            "under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 400, 5, prepare_emergency_lighting_commons_sa,
           "about 90 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: cloth and fibre close up and the museum's textiles and tools
# (things only); never the repair, lock, engine, pest or craft photos (people at work, poisons and pests), nor Open
# Images (people).
HOME_CRAFTS_PICTURE_MAKING_OK = {"commons_fabrics_fibres", "nmah_textiles_sewing", "textile_crafts_commons_sa"}

# The kit topics each collection belongs to (topics.py lists them; the self-test checks they match): the house,
# locks, engines, bicycles and sewing things go with household equipment ("machines"), the pests with nature, the
# crafts, quilts and fabrics with art and museum objects.
HOME_CRAFTS_TOPICS = {
    # the home and household topic gathers every collection here (the owner's decision of 22 November 2026); the
    # textile crafts are also in art and the household pests also in nature
    "home": ("commons_home_repair", "commons_locks_engines_bikes", "open_images_home_upkeep", "commons_pest_control",
             "commons_home_heating", "commons_firewood", "open_images_home_heating", "commons_emergency_lighting",
             "open_images_emergency_lighting", "commons_sewing_mending", "commons_upholstery_leather_shoes",
             "commons_knit_crochet_lace", "commons_quilt_embroidery_weaving", "commons_fabrics_fibres",
             "open_images_textile_crafts", "nmah_textiles_sewing", "home_upkeep_commons_sa", "home_heating_commons_sa",
             "emergency_lighting_commons_sa", "textile_crafts_commons_sa"),
    "nature": ("commons_pest_control", "open_images_home_upkeep", "home_upkeep_commons_sa"),
    "art": ("commons_knit_crochet_lace", "commons_quilt_embroidery_weaving", "commons_fabrics_fibres",
            "open_images_textile_crafts", "nmah_textiles_sewing", "textile_crafts_commons_sa"),
}

HOME_CRAFTS_SIGN_UP = {
    "Kaggle and Roboflow Universe fabric, stain, rodent and insect-trap sets":
        "https://www.kaggle.com and https://universe.roboflow.com : several sets of fabric defects, stains on cloth, "
        "sticky-trap insects and rodents exist, some under CC BY 4.0, but each needs a free account and API key to "
        "download, and where their photos come from is often not stated. Check each set's licence and sources before "
        "using it in the own-pictures folder.",
    "Bugwood Image Database (insectimages.org, ipmimages.org; University of Georgia)":
        "tens of thousands of pest, insect and damage photos by experts; each image's page gives its licence, most "
        "CC BY-NC 3.0 US (non-commercial). No documented public listing route was found (api.bugwood.org answered "
        "500 to a subject search on 2026-11-22; its robots.txt asks for a 2-second crawl delay and does not refuse "
        "AI readers). A non-commercial entry can be added once a listing route is confirmed; until then the owner "
        "can save photos by hand into the own-pictures folder for personal use.",
}

HOME_CRAFTS_NOT_INCLUDED = {
    "Ravelry (patterns, yarns and project photos)":
        "its terms of service do not allow collecting its content (the owner's rule: Ravelry is not used); its "
        "photos belong to its members. Not read.",
    "Pinterest":
        "its robots.txt refuses every robot ('User-agent: *' 'Disallow: /', checked 2026-11-22) and its pins are "
        "other people's photos. Not read.",
    "Instructables (Autodesk)":
        "most projects are CC BY-NC-SA, but its robots.txt disallows /file/ and /image/ (the pictures) to every "
        "robot (checked 2026-11-22). Not read.",
    "Cooper Hewitt and V&A textile collections":
        "Cooper Hewitt's metadata is CC0 but its pictures are not in the Smithsonian open-access bucket (as found "
        "for hardware); the V&A is already the kit's non-commercial entry vam (its textiles included). Not repeated.",
    "The Met, Art Institute of Chicago and Cleveland quilts, samplers and lace (CC0)":
        "already reachable through met_collection, aic_collection and cleveland_collection, which read every "
        "department; the Smithsonian's NMAH textiles are the new museum pack (nmah_textiles_sewing).",
    "CDC PHIL rodent, flea, louse and mosquito photos":
        "CDC PHIL is read by cdc_medical, cdc_phil_supplies and the pest packs already; its pest photos that people "
        "copied to Commons are found by commons_pests and commons_pest_control. Not repeated.",
    "USDA ARS image gallery and university extension pest photos":
        "the ARS gallery has no listing a program can read by subject that was confirmed (as in drinks_sources.py), "
        "and extension photos are each under their own university's copyright (no open licence confirmed).",
    "iNaturalist pest observations":
        "already read through GBIF and the iNaturalist open-data bucket by na_insects, na_invertebrates and the "
        "iNaturalist packs (never the inaturalist.org site). Not repeated.",
    "Open Images labels left out":
        "trades that judge people by their work (Electrician, Roofer, Handyman, Bicycle mechanic, Cobbler); "
        "labels with another common meaning (Spinning, also an exercise class; Stitch, also a cartoon character; "
        "Button, Pin, Pattern, Painting, Engine, Chain, Cotton, the plant); painting, adhesive and bead labels "
        "(Paint, Paint brush, Adhesive, Bead: the arts-and-crafts packs' subjects); and labels already asked by "
        "another pack (Sewing, Knitting, Weaving, Tailor, Sewing machine, Scissors, Ladder, Toilet, Tap, Pipe, Mouse, "
        "Rat, Cockroach, Ant, Bed bug, Termite, Mold and others), never asked twice.",
    "Commons categories that do not exist under the names tried (November 2026)":
        "Stain removal, Laundry stains, Shoe repair, Furniture refinishing, Wood finishing, French polishing, Paint "
        "stripping, Drywall repair, Roof repair, Water leaks, Clogged drains, GFCI outlets, HVAC filters, Furnace "
        "filters, Appliance repair, Lock picking, Key cutting, Mouse droppings, Rodent droppings, Termite damage, "
        "Bait stations, Pantry pests, Bed bug detection, Cross-stitch, Macramé (the spelling Macrame is used), "
        "Upholstery fabrics, Leathercraft, Saddlery, Visible mending, Appliqué, Bias tape and Fabric stores. Stain "
        "removal and laundry stains are covered in words by the reference books (craft: and the laundry guides), "
        "not by pictures.",
    "Commons categories already asked by another pack":
        "Plumbing, Plungers, Stopcocks, Water meters, Septic tanks, Sump pumps, Electrical wiring, Light switches, "
        "Circuit breakers, Distribution boards, Fuse boxes, House painting, Paint rollers, Masking tape, Peeling "
        "paint, Caulking guns, Air filters, Gas furnaces, Heat pumps, Air conditioners, Ductwork, Radiators, "
        "Thermostats, Dehumidifiers, Small engines, Carburetors, Spark plugs, Lawn mowers, Snow blowers, Bicycle "
        "repair, Bicycle repair stands, Bicycle chains, Bicycle tires, Flat tires, Bicycle brakes, Mousetraps, "
        "Insecticides, Pesticides, Pesticide application, Insect traps, Knitting, Sewing, Weaving, Knots, Thimbles, "
        "Tape measures, Singer sewing machines, Satin, Shoeshiners, Deadbolts: not repeated.",
    "Heating pictures not found as open categories (November 2026)":
        "Commons has no category for fireplace inserts, gas fireplaces, multi-fuel or pellet stoves beyond Pellet "
        "stoves (already device_packs'), masonry heaters by that name (Tiled stoves is used), outdoor wood boilers, "
        "propane, infrared or diesel heaters, oil-filled radiators, firewood racks, log carriers, kerosene cans or "
        "chimney liners; Open Images has no Kerosene heater, Pellet stove or Woodpile label people checked (Kerosene, "
        "Firewood, Patio heater and Carbon monoxide detector are labels without checked boxes). The EPA's Burn Wise, "
        "CPSC and NIST photo pages were not read: CPSC answers this machine 403, and the EPA's Burn Wise pictures are "
        "few and mixed with makers' product photos.",
    "Open Images Fire, Flame, Ash, Charcoal, Poker, Bonfire, Campfire and Lumberjack (for heating)":
        "left out: Fire and Flame cover every fire (and Flame is already used by home_packs to tell a lit burner), "
        "Ash is also the tree, Charcoal also the drawing stick, Poker the card game, bonfires and campfires are "
        "outdoor fires, and Lumberjack judges a person by trade.",
    "Lighting pictures not found as open categories or labels (November 2026)":
        "Commons has no category for head torches, LED, solar or camping lanterns, hand-crank or dynamo lights, night "
        "lights, power banks (the category is empty), Coleman products (Coleman Company is used for its lanterns), "
        "Dietz or Feuerhand lanterns, Aladdin or mantle lamps, lamp "
        "chimneys, leaking batteries, emergency or taper candles, white gas or Coleman fuel; Open Images' Flashlight, "
        "Lantern, Candle, Lamp, Battery and Chandelier are asked by other packs, and Emergency light, Tealight and "
        "Votive candle have no checked boxes. Lamps from before 1900 (carbide, whale oil, Betty and Argand lamps, "
        "antique oil lamps and museum pieces) are left out by the owner's choice; Commons' Gas lanterns and Gas "
        "lamps hold street lamps (checked in a live build), so they are not used. Solar lamps, solar chargers, battery sizes and exit signs are other "
        "packs' (not repeated). FEMA's and CPSC's photo libraries were not read (CPSC answers this machine 403; "
        "FEMA's photos on Commons are found by category).",
    "Woodworking, woodcarving, tiling, insulation and light construction":
        "covered by another helper's packs (the building and arts-and-crafts collection), so not built here.",
}
