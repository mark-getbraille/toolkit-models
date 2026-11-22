"""LIGHT CONSTRUCTION AROUND THE HOME for the Picture Model Training Kit (the owner's request of 2026-11-22). This file
lists:
  - the ready-made packs built in packs/building_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): framing, decks, sheds, fences, concrete, masonry, tiling, insulation and stairs; ramps and home
    accessibility modifications as built; construction safety and layout tools; Open Images fences, sheds, decks and
    building materials;
  - the share-alike Commons files of the main categories (group "share-alike": only with --with-wikipedia);
  - what was looked at and left out, with the reason (BUILDING_NOT_INCLUDED).

Nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the user's own computer,
only when the user ticks its choice. Answers say only what the Commons category or the file's own words say; a
lumber size only where the file's own words name exactly one. Safety notes (concrete, falls, permits, the ADA ramp
rule) are the packs' own words.

Picture-making (BUILDING_PICTURE_MAKING_OK): none of these (construction photos show workers, houses and streets).

    python -c "import sources, building_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

COMMONS_OPEN = ("Pictures CC0, public domain (US government photos among them) or CC BY (credited in CREDITS.txt); "
                "captions CC0")
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"

CONCRETE_NOTE = ("Safety: wet concrete, mortar and grout are caustic and can burn skin and eyes: wear gloves, eye "
                 "protection and long sleeves, and wash splashes off with water. Cutting or grinding concrete, brick "
                 "or tile makes silica dust: cut wet, or wear a respirator.")
PERMIT_NOTE = "Decks, sheds, fences, stairs and structural work usually need a building permit: check local codes."
RAMP_NOTE = ("For public buildings the ADA Standards say a ramp may be no steeper than 1 in 12 (one inch of rise for "
             "every twelve inches of length), with a level landing at the top and bottom and handrails on both sides "
             "when it rises more than 6 inches (sections 405.2, 405.7 and 405.8); at home, local codes and permits "
             "apply.")


def thing(category, words, note="", deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "It shows <words>." and the note."""
    return (category, "What is this?", f"It shows {words}." + (f" {note}" if note else ""), deeper)


BUILDING_SA = [
    thing("Timber framing", "timber framing, heavy timbers joined with wooden joints and pegs"),
    thing("Decks (architecture)", "a deck", PERMIT_NOTE, deeper=False),
    thing("Roof trusses", "roof trusses"),
    thing("Wooden decks", "a wooden deck", PERMIT_NOTE),
    thing("Garden sheds", "a garden shed", PERMIT_NOTE),
    thing("Wooden fences", "a wooden fence", PERMIT_NOTE),
    thing("Formwork", "formwork, the moulds that hold wet concrete until it sets", CONCRETE_NOTE),
    thing("Bricklaying", "bricklaying: laying bricks in mortar", CONCRETE_NOTE),
    thing("Dry stone walls", "a dry stone wall, built of stones fitted together without mortar"),
    thing("Wooden stairs", "wooden stairs", PERMIT_NOTE),
    thing("Wooden ramps", "a wooden ramp", RAMP_NOTE),
    thing("Grab bars", "grab bars, strong rails fixed to the wall to hold on to"),
]


def prepare_building_commons_sa(source, data_dir, work, cap):
    """Commons framing, deck, shed, fence, concrete, masonry, stair and ramp categories, files under CC BY-SA or
    GFDL."""
    items = commons_sa_items(BUILDING_SA, cap, source.test, "building-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


BUILDING_SOURCES = [
    Source("commons_light_construction", "Light construction: framing, decks, sheds, fences, concrete and formwork, "
                                         "bricklaying and stone walls, tiling, insulation and stairs, a lumber size "
                                         "only where the file names it, with safety and permit notes (Wikimedia "
                                         "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 2000, 20, prepare_pack, "about 450 MB"),
    Source("commons_home_access_building", "Ramps and home accessibility modifications as built: wooden ramps, access "
                                           "ramps, grab bars and accessible kitchens, with the ADA ramp rule "
                                           "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 200, 5, prepare_pack, "about 45 MB"),
    Source("commons_construction_safety", "Construction safety and layout: fall protection, guardrails, safety vests, "
                                          "trench shoring, building permits, workers at work, plumb bobs, chalk lines "
                                          "and speed squares (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 500, 10, prepare_pack, "about 110 MB"),
    Source("open_images_building", "Fences, sheds and decks, concrete slabs, particle board, mortar, tile flooring, "
                                   "concrete saws and hard hats (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("building_commons_sa", "Wikimedia Commons: framing, decks, sheds, fences, formwork, bricklaying, stone "
                                  "walls, stairs, ramps and grab bars, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_building_commons_sa, "about 170 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]
BUILDING_PACK_KEYS = ("commons_light_construction", "commons_home_access_building", "commons_construction_safety",
                      "open_images_building")
BUILDING_PICTURE_MAKING_OK = set()

BUILDING_NOT_INCLUDED = {
    "OSHA and NIOSH photo galleries (osha.gov, cdc.gov/niosh, their Flickr streams)":
        "public domain, but osha.gov refuses programs (HTTP 403, as the manual library found) and Flickr's API terms "
        "do not allow storing; the agencies' photos copied to Commons are found by the Commons categories, each "
        "file's licence checked.",
    "FEMA and HUD photo libraries":
        "fema.gov refuses programs; HUD's pages give programs an empty frame (textbooks directory_sources.py); "
        "their photos on Commons are used where the categories reach them.",
    "Instructables, Houzz, This Old House, Family Handyman and Pinterest":
        "their terms forbid copying their pictures by program; not read.",
    "Hardware, tools and materials already asked about":
        "hardware_packs (nails, screws, bolts, anchors, joist hangers, lumber, plywood, OSB, pressure-treated wood, "
        "drywall, ladders, scaffolding, tape measures, spirit levels, PPE), things_packs (bricks, concrete blocks, "
        "rebar, glass wool, ceramic tiles) and disability_packs (wheelchair ramps, wheelchair and stair lifts, grab "
        "rails, accessible bathrooms): not repeated.",
    "Open Images construction labels with no checked photos (November 2026)":
        "Spirit level, Laser level, Masonry trowel, Masonry tool, Fence Post, Ceramic tile cutter, Concrete grinder, "
        "Wire saw, Pipe insulation, Wood veneer: no human-checked labels in Open Images, so left out. Bricklayer, "
        "Carpenter and Electrician judge people by their trade and are left out.",
    "Commons categories that do not exist under the names tried (November 2026)":
        "Wood and platform framing, Houses under construction, Rafters, Floor joists, House wrap, Deck construction, "
        "Composite decking, Concrete finishing and footings, House foundations, Grout, Fiberglass and polystyrene "
        "insulation, Modular, threshold and portable ramps, Accessible entrances, Roll-in showers, Lever door handles, "
        "Stairlifts, Platform lifts, Home modifications, Fall arrest, Trench shoring, Construction safety, Building "
        "inspection, Framing hammers and nailers, Laser levels and Carpenter's squares; the packs use the categories "
        "that exist (Timber framing, Decks (architecture), Concrete construction, Tilers, Ramps, Shoring ...).",
    "Building codes (the International Residential Code and the like)":
        "the ICC's codes are copyrighted (read free online only); the reference library has the ADA Standards and "
        "the Access Board's guide.",
}
