"""Light construction around the home for the reference library, in the group "Reference, building and light
construction" (the owner's request of 2026-11-22). Keys: building (every book), build:<name>.

What this module builds, each IN FULL (US government works and Wikibooks, read whole):
  - the US Army's Carpentry (FM 5-426, 1995: lumber, framing, floors, walls, roofs, stairs, doors and windows,
    decks and wood structures) and Concrete and Masonry (FM 5-428, 1998: concrete mixing, forms, placing and
    finishing, brick, block and stone masonry), and Use and Care of Hand Tools and Measuring Tools (TM 9-243, 1983:
    rules and tapes, squares, levels, plumb bobs and every hand tool), from the Internet Archive's copies, each kept
    only when its own front matter says Distribution Statement A (checked at every build);
  - the US Navy's Blueprint Reading and Sketching (NAVEDTRA 14040: reading building and machine drawings, lines,
    symbols, dimensions and scales), with the same check;
  - OSHA's A Guide to Scaffold Use in the Construction Industry (OSHA 3150) and Fall Protection in Construction
    (OSHA 3146), from the Defense Technical Information Center's copies on the Internet Archive (osha.gov refuses
    programs);
  - the Forest Products Laboratory's Wood Handbook: Wood as an Engineering Material (2010), the reference on lumber
    species, grades, strength, moisture, fasteners and decay;
  - Wikibooks' Carpentry and Woodworking (CC BY-SA 4.0, share-alike), every page.
The ramp and accessibility rules are already in the library (the 2010 ADA Standards, the Access Board's guide to
them with its chapter on ramps and curb ramps, and HUD and DOJ's joint statement on reasonable modifications), so
they are not repeated here.

Safety: every book's notice ends with SAFETY_NOTE (permits, falls, power tools, concrete).

Run from the repository's folder:
  python3 textbooks/building_books.py build:army_fm_5_426_carpentry --out build/textbooks --limit 5
  python3 textbooks/building_books.py --list building
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from electronics_books import wikibook  # noqa: E402

GROUP = "construction"
GROUPS = {GROUP: "Reference, building and light construction"}

SAFETY_NOTE = ("Safety: building work usually needs a permit and must meet local codes; use fall protection when "
               "working at height, eye and hearing protection with power tools, and gloves and eye protection with "
               "wet concrete, which burns skin.")
ARMY = "Headquarters, Department of the Army"
NAVY = "Naval Education and Training Professional Development and Technology Center (US Navy)"
OSHA = "US Occupational Safety and Health Administration (OSHA)"
MILITARY_NOTICE = "A work of the US armed forces (public domain), approved for public release; distribution is " \
                  "unlimited. " + SAFETY_NOTE


def military(name, title, subject, publisher, archive, published, description):
    """A US military manual from the Internet Archive, kept only with Distribution Statement A in its front matter."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    distribution_a=True, published=published, version=f"{published} edition",
                    description=description, notice=MILITARY_NOTICE)


PDFS = [
    military("army_fm_5_426_carpentry", "Carpentry (FM 5-426, 1995)", "Carpentry and framing", ARMY,
             "fm-5-426-carpentry-1995", "1995",
             "The US Army's carpentry manual: lumber and its sizes, fasteners, plans and specifications, layout, "
             "foundations, floor, wall and roof framing, roofing, stairs, doors and windows, interior finish, decks "
             "and wood bridges, and the hand and power tools used."),
    military("army_fm_5_428_concrete_masonry", "Concrete and Masonry (FM 5-428, 1998)", "Concrete and masonry",
             ARMY, "fm-5-428-concrete-and-masonry-1998", "1998",
             "The US Army's concrete and masonry manual: cement, aggregates and mixing, forms, placing, finishing "
             "and curing concrete, reinforcement, precast concrete, concrete block, brick and stone masonry, and "
             "repairs."),
    military("army_tm_9_243_hand_tools", "Use and Care of Hand Tools and Measuring Tools (TM 9-243, 1983)",
             "Hand and measuring tools", ARMY, "use-and-care-of-hand-tools-and-measuring-tools-1983", "1983",
             "The US Army's guide to every common hand tool and measuring tool: rules and tape measures, squares, "
             "levels, plumb bobs, calipers and gauges, hammers, saws, chisels, files, wrenches and screwdrivers, how "
             "to use each, care and safety."),
    military("navy_blueprint_reading", "Blueprint Reading and Sketching (US Navy, NAVEDTRA 14040)",
             "Reading plans and drawings", NAVY, "US_Navy_Training_Course_-_Blueprint_Reading_and_Sketching", "1994",
             "The US Navy's course on reading drawings: blueprints, lines and views, dimensions, tolerances and "
             "scales, symbols, sketching, and building, electrical and piping drawings."),
    K.us_pdf(GROUP, name="osha_3150_scaffold_use", title="A Guide to Scaffold Use in the Construction Industry (OSHA "
             "3150)", subject="Scaffold safety", publisher=OSHA, archive="DTIC_ADA400342", published="2001",
             version="OSHA 3150 (2001)",
             description="OSHA's guide to scaffolds: the kinds of scaffold (supported and suspended), capacity, "
                         "platforms, access, the competent person, guardrails and fall protection, falling objects, "
                         "and inspection.",
             notice="A work of the US Occupational Safety and Health Administration (public domain), from the "
                    "Defense Technical Information Center's copy. " + SAFETY_NOTE),
    K.us_pdf(GROUP, name="osha_3146_fall_protection", title="Fall Protection in Construction (OSHA 3146)",
             subject="Fall protection", publisher=OSHA, archive="DTIC_ADA400348", published="1998",
             version="OSHA 3146 (1998)",
             description="OSHA's guide to fall protection on building sites: when it is needed, guardrails, safety "
                         "nets, personal fall arrest systems, covers for holes, and training.",
             notice="A work of the US Occupational Safety and Health Administration (public domain), from the "
                    "Defense Technical Information Center's copy. " + SAFETY_NOTE),
    K.us_pdf(GROUP, name="fpl_wood_handbook", title="Wood Handbook: Wood as an Engineering Material (Forest Products "
             "Laboratory, 2010)", subject="Wood and lumber", publisher="Forest Products Laboratory, US Forest "
             "Service (USDA)", archive="wood-handbook", published="2010-04", version="centennial edition (FPL-GTR-190)",
             description="The Forest Products Laboratory's reference on wood: the structure and properties of each "
                         "commercial species, lumber grades and sizes, moisture and shrinkage, strength, fastenings "
                         "(nails, screws, bolts and connectors), glued and engineered wood, finishing, decay and how "
                         "to prevent it.",
             notice="A work of the US Forest Service (public domain). " + SAFETY_NOTE),
]

GUIDES = [
    wikibook(GROUP, "wikibooks_carpentry", "Carpentry", "Carpentry (Wikibooks)", "Carpentry and framing",
             "Wikibooks' open book on carpentry: tools, lumber, joints, framing, stairs and finish carpentry.",
             SAFETY_NOTE),
    wikibook(GROUP, "wikibooks_woodworking", "Woodworking", "Woodworking (Wikibooks)", "Woodworking",
             "Wikibooks' open book on woodworking: wood, hand and power tools, joinery, gluing, sanding and "
             "finishing, and projects.", SAFETY_NOTE),
]

COLLECTION = K.Collection("build", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"building": lambda: [f"build:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "building_military": "US Army field and technical manuals and US Navy training courses: works of the US "
                         "government (17 U.S.C. 105), each kept only when its own front matter says \"Approved for "
                         "public release; distribution is unlimited\" (checked in the PDF at every build); the "
                         "Internet Archive's copies (armypubs.army.mil's robots.txt shuts out automated readers).",
    "building_osha_fpl": "OSHA's guides (the Defense Technical Information Center's copies on the Internet Archive; "
                         "osha.gov refuses programs) and the Forest Products Laboratory's Wood Handbook "
                         "(research.fs.usda.gov's robots.txt disallows everything, so the Internet Archive's copy): "
                         "works of the US government (17 U.S.C. 105).",
}
NOT_INCLUDED = [
    ("US Navy Builder 3 and 2 (rate training manual, 1981; ERIC ED210471)", "A US Navy course, but the Internet "
     "Archive's copy shows no Distribution Statement A in its front matter (the builder refused it on 2026-11-22), so "
     "it is not built; the Army's Carpentry and Concrete and Masonry manuals cover the same work. Index: "
     "https://archive.org/details/ERIC_ED210471"),
    ("NIOSH construction, falls, ladder safety and silica pages (cdc.gov/niosh)", "Public domain, but www.cdc.gov "
     "answered this build machine \"403 Forbidden\" for every page on 2026-11-22 (it answered before); try again in a "
     "later build. Link-only for now. Index: https://www.cdc.gov/niosh/construction/ and "
     "https://www.cdc.gov/niosh/falls/"),
    ("OSHA's construction eTools and web pages (osha.gov)", "Public domain, but osha.gov refuses programs (as the "
     "manual library found on 2026-11-21); its guides are built from DTIC's copies. Link-only. Index: "
     "https://www.osha.gov/construction"),
    ("FEMA building science guides (Home Builder's Guide to Coastal Construction, Wind Retrofit Guide)", "Public "
     "domain, but fema.gov refuses programs and no Internet Archive copy with its words was found (checked "
     "2026-11-22). Link-only. Index: https://www.fema.gov/emergency-managers/risk-management/building-science"),
    ("HUD rehabilitation guides (Residential Rehabilitation Inspection Guide)", "Public domain, but HUD's pages give "
     "programs only an empty frame and no Internet Archive copy was found (checked 2026-11-22). Link-only. Index: "
     "https://www.huduser.gov/portal/publications/destech/inspect.html"),
    ("DOE insulation guides (Energy Saver)", "energy.gov's Energy Saver pages answer \"not found\" (as the manual "
     "library found on 2026-11-21). Link-only. Index: https://www.energy.gov/energysaver/insulation"),
    ("ADA Standards and the Access Board's ramp guidance", "Already in the library (law and guide keys "
     "ada_2010_standards_accessible_design and access_board_ada_guide, whose chapter 4 covers ramps and curb ramps); "
     "not repeated. Index: https://www.access-board.gov/ada/guides/chapter-4-ramps-and-curb-ramps/"),
    ("The International Residential Code and other model building codes", "Copyright of the International Code "
     "Council (free to read online only). Link-only. Index: https://codes.iccsafe.org/"),
    ("This Old House, Family Handyman, Instructables and YouTube", "Copyright; their terms forbid copying by "
     "program. Index: https://www.instructables.com/workshop/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
