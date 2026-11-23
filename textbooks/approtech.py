"""Appropriate technology and village skills for the reference library (the owner's request of 2026-11-23: practical
how-to knowledge for life without modern supply chains). Keys: approtech (every book), apt:<name>, and the themes
apt-water, apt-building, apt-farming, apt-energy-tools and apt-health. Its own group, "Reference, appropriate
technology and village skills".

What this module builds, in plain words:
  - apt:index, a guide in plain words (the toolkit's own facts and links, CC0): water and wells, sanitation, building
    with earth, bamboo and concrete, farming, fish, bees and small animals, trees, energy and stoves, food drying,
    tools and the farm shop. It links the books other modules already have (homestead, building, power, garden,
    preserving, foraging and preparedness) by key instead of repeating them, and the copyright works (VITA, CODEL,
    the Appropriate Technology Library) as links only;
  - Peace Corps Information Collection and Exchange (ICE) manuals on the themes this module was given (water, wells,
    sanitation, irrigation, soil conservation, fish ponds, bees, small animals, trees, building, energy and food
    drying), read whole from the Internet Archive's copies of ERIC's scans. The peace-corps helper (pc:) takes the
    other Peace Corps manuals, and the list of ids used here is shared with it (notes/approtech-peace-corps-ids.txt);
  - US government works: USGS well and ground-water books (pubs.usgs.gov) and USDA Farmers' Bulletins on farm water,
    privies, sewage, rammed earth, adobe, concrete, windmills and fish ponds (Internet Archive copies of the National
    Agricultural Library's scans);
  - old public-domain books (published before 1931; the builder checks each item's year at every build): Cobleigh's
    Handy Farm Devices, Drew's Farm Blacksmithing, Shearer's Farm Mechanics, Brace and Mayne's Farm Shop Work,
    Chapman's Treatise on Ropemaking, Mechanics for Young America, Isler's Well-Boring, Hutton's Country Plumbing,
    Seaton's Concrete Construction for Rural Communities and Dobson's treatise on bricks and tiles.

Licences, truthfully (each book's notice says which applies):
  - NO_NOTICE: a Peace Corps (or HUD) publication printed with no copyright notice before 1 March 1989. Works of US
    government employees are public domain (17 U.S.C. 105); a manual written for the Peace Corps under contract is not
    such a work by itself, but a work published in the US without a copyright notice before 1989 lost its copyright
    unless it was registered within five years and the notice added (17 U.S.C. 405, checked on the Copyright Office's
    page at every build); the Peace Corps kept reprinting these manuals without a notice. The builder also reads the
    front pages of each copy at every build and refuses it if they claim a copyright or a "Peace Corps use only"
    permission (PC_FRONT);
  - PC_FREE: the copy prints the Peace Corps' own line "This manual may be reproduced and/or translated in part or in
    full without payment or royalty" (checked in the PDF at every build);
  - US_GOV: written by US government staff (USDA, USGS);
  - old books: public domain in the US as published before 1931.
  Link-only (NOT_INCLUDED): the joint Peace Corps/VITA manuals ((c) VITA, reproduction allowed only "for official
  U.S. Government purposes"), VITA's technical papers and the CODEL/VITA guidelines (copyright), reprints "for Peace
  Corps use only", an author's own book, a Philippine co-publication, Peace Corps manuals of 1989 and later without
  the reproduction line, and the Army's well-drilling manuals (left to the service-skills helper).

Safety notes on every book: wells and confined spaces (bad air, cave-ins, falling objects, covers), water testing and
treatment, cement and lime burns, tools and fire, bees and animals, and biogas. A well manual's dynamite appendix is
left out (cut_explosives), and the index says never to use explosives.

Run from the repository's folder:
  python3 textbooks/approtech.py apt:pc_wells_construction_1982 --out build/textbooks --limit 3
  python3 textbooks/approtech.py --list approtech
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "approtech"
GROUPS = {GROUP: "Reference, appropriate technology and village skills"}

# ====================================================================== licences

NO_NOTICE = "Public domain (US government publication without a copyright notice, before 1989)"
NO_NOTICE_URL = "https://www.copyright.gov/title17/92chap4.html#405"
NO_NOTICE_PAGE = "https://www.copyright.gov/title17/92chap4.html"
NO_NOTICE_TEXT = r"Omission of notice on certain copies"
PC_FREE = "Free to reproduce and translate (the Peace Corps' notice)"
ALLOWED = {NO_NOTICE: "open", PC_FREE: "open"}

# The front pages of a Peace Corps copy must name the Peace Corps and must not claim a copyright or a permission for
# Peace Corps use only (checked at every build by build_textbooks.pdfdoc_book on the PDF's first twelve pages).
PC_FRONT = (r"(?is)^(?!.*(?:copyright\s*(?:©|\(c\))?\s*(?:19\d\d|by)|(?:[©@]|\(c\))\s*VITA|"
            r"reprinted\s+with\s+permission|for\s+peace\s+corps\s+use\s+only)).*peace\s*corps")
PC_FREE_TEXT = r"(?i)without\s+payment\s+(?:of|or)\s+royalty"

NO_NOTICE_WORDS = ("Published by the Peace Corps, a US government agency, with no copyright notice. Works of US "
                   "government employees are public domain (17 U.S.C. 105), and a work published in the US without a "
                   "copyright notice before 1 March 1989 lost its copyright unless it was registered within five "
                   "years and the notice added (17 U.S.C. 405); the Peace Corps kept reprinting it without one. ")
PC_FREE_WORDS = ("Published by the Peace Corps, a US government agency; the manual itself says it \"may be reproduced "
                 "and/or translated in part or in full without payment or royalty\" and asks for the standard "
                 "acknowledgement: from the Peace Corps, Information Collection and Exchange. ")
SCAN_WORDS = ("Read from the Internet Archive's copy of ERIC's scan: the machine-read text has the scanner's mistakes, "
              "and its drawings are described only by their captions. It was written for Peace Corps Volunteers in "
              "the 1970s and 1980s, mostly in Africa, Asia and Latin America: prices, addresses and some health "
              "advice are out of date. ")

# ====================================================================== safety notes

WELL_SAFETY = ("Well safety: never climb into a well, pit or tank until the air has been tested or blown fresh: wells "
               "collect gases that cannot be seen or smelled and kill quickly, and rescuers die too. Use a harness "
               "and lifeline with a helper at the top who never goes down alone, line or shore the sides against "
               "cave-ins, keep tools and stones away from the edge, wear a hard hat, and cover every well and pit so "
               "no child or animal can fall in. Never use explosives. ")
WATER_SAFETY = ("Water safety: have well and spring water tested before drinking it and again after floods or "
                "repairs; keep wells uphill and at least the local rule's distance (often 15 to 30 metres or 50 to "
                "100 feet) from latrines, septic systems and animal pens; boil, chlorinate or filter water you are not "
                "sure of; and follow your local health department's rules. ")
CEMENT_SAFETY = ("Cement safety: wet cement and lime burn the skin and eyes (they are strongly alkaline), "
                 "sometimes without pain at first: wear gloves, long sleeves and eye protection, wash skin with "
                 "clean water at once, and flush eyes for 15 minutes; wear a dust mask when cutting or mixing dry "
                 "materials (silica dust); and have walls and roofs checked against local building codes. ")
FARM_SAFETY = ("Farm safety (bees, animals and chemicals): anyone allergic to stings must keep away from hives "
               "and carry their medicine; wear a veil and gloves; animals kick, bite and carry diseases (wash "
               "hands); and old manuals name pesticides and medicines that are banned or restricted now: follow "
               "today's labels and local advice. ")
TOOL_SAFETY = ("Tool and fire safety: wear eye protection at the forge, grinder and anvil, keep water at hand, "
               "guard moving belts, shafts and blades, and never work under a load that is not blocked. Biogas and "
               "smoke: methane burns and can explode, gas pits and closed rooms can suffocate, and stoves need "
               "ventilation against carbon monoxide. ")
OLD_NOTE = ("Published in {year}: an old book. Its methods are those of its day: lead pipes and lead paint, asbestos, "
            "old wiring, no guards on machines, and old remedies, pesticides and sanitation are out of date or not "
            "allowed today. Follow current codes and safety rules.")

# ====================================================================== Peace Corps ICE manuals


def _pc(name, title, subject, archive, year, number, made_by, description, notice, licence=NO_NOTICE, **more):
    """One Peace Corps ICE manual read whole from its Internet Archive copy (see the module docstring): number is the
    ICE number ("Manual M-9"), made_by who wrote it (and the contract, when one is printed)."""
    entry = K.us_pdf(GROUP, name=name, title=title, subject=subject, archive=archive, published=str(year),
                     publisher=f"Peace Corps, Information Collection and Exchange ({number})",
                     version=f"{year} printing ({number}; Internet Archive item {archive})",
                     description=description + f" Written by {made_by}.", **more)
    if licence == NO_NOTICE:
        entry.update(licence=NO_NOTICE, licence_url=NO_NOTICE_URL, licence_page=NO_NOTICE_PAGE,
                     licence_text=NO_NOTICE_TEXT, pdf_licence_text=PC_FRONT,
                     notice=NO_NOTICE_WORDS + SCAN_WORDS + notice)
    elif licence == PC_FREE:
        entry.update(licence=PC_FREE, licence_url=f"https://archive.org/details/{archive}", licence_page="",
                     licence_text="", pdf_licence_text=PC_FREE_TEXT, notice=PC_FREE_WORDS + SCAN_WORDS + notice)
    else:                                      # US_GOV: written by government staff (the us_pdf defaults)
        entry.update(notice="A work of the US government (public domain), reprinted by the Peace Corps. " +
                     SCAN_WORDS + notice)
    return entry


PEACE_CORPS = [
    # ---------------------------------------------------------------- water, wells and sanitation
    _pc("pc_wells_construction_1982", "Wells Construction: Hand Dug and Hand Drilled (Peace Corps Manual M-9, 1982)",
        "Wells", "ERIC_ED241770", 1982, "Manual M-9; ACTION Pamphlet 4200.35",
        "Richard E. Brush (no contractor is named)",
        "How to plan and build a well for a village's drinking water: planning a well and the kinds of wells, hand-dug "
        "wells (design, supplies, lowering and raising workers and equipment, digging, lining, the middle and bottom "
        "sections), drilled wells (hand rotary, hand percussion, sludger, driven and jetted wells, casing and the "
        "bottom section), with appendices on conversion tables, plants as signs of ground water, cement, levelling "
        "and plumbing a mould, pipe, pumps, water treatment in wells and rope strength. Its appendix on dynamite is "
        "left out.", WELL_SAFETY + WATER_SAFETY + CEMENT_SAFETY, cut_explosives=True),
    _pc("pc_water_sanitation_technologies_1985", "Water and Sanitation Technologies: A Trainer's Manual (Peace Corps "
        "Training Manual T-32, 1985)", "Water supply and sanitation", "micro_IA41153301_0080", 1985,
        "Training Manual T-32", "Bradley D. Hanson (no contractor is named)",
        "A training course for Volunteers who work on village water and sanitation: water sources, springs and spring "
        "boxes, wells, pumps, water storage and treatment, latrines and other sanitation, and working with a "
        "community, set out session by session with handouts.", WATER_SAFETY + WELL_SAFETY + CEMENT_SAFETY),
    _pc("pc_water_purification_sewage_1979", "Water Purification, Distribution and Sewage Disposal (Peace Corps "
        "Reprint R-29, 1969, reprinted 1979)", "Water supply and sanitation", "ERIC_ED243656", 1979,
        "Reprint R-29", "Volunteers for International Technical Assistance, Inc. (VITA), under Peace Corps contract "
        "PC-25-1709, 1969 (this copy prints no copyright notice)",
        "A training manual and field reference in nine units: water supply sources, water treatment, planning a "
        "distribution system, what makes a system adequate, construction, operating and maintaining distribution and "
        "treatment, sewage disposal projects, the privy for excreta disposal in a village, and water-carried sewage "
        "systems.", WATER_SAFETY + WELL_SAFETY),
    _pc("pc_irrigation_principles_practices_1982", "Irrigation Principles and Practices (Peace Corps Reprint R-5, "
        "1969, reprinted 1982)", "Irrigation", "ERIC_ED242880", 1982, "Reprint R-5",
        "Development and Resources Corporation under Peace Corps contract PC-25-1703, 1969",
        "A practical irrigation handbook for a generalist, built from Volunteers' work: irrigation principles, "
        "measuring water (weirs and flumes, with flow tables), controlling irrigation water, drainage, planning, and "
        "growing irrigated crops, with home-made field tools (buck scraper, float, A-frame, ridger, V-ditcher).",
        WATER_SAFETY, licence=PC_FREE),
    _pc("pc_small_scale_irrigation_systems_1983", "Small Scale Irrigation Systems for Peace Corps Volunteers (1983)",
        "Irrigation", "ERIC_ED307464", 1983, "Information Collection and Exchange",
        "Development Planning and Research Associates, Inc. under Peace Corps contract PC-282-1009",
        "Irrigation design in thirteen sections: concepts of irrigation design, the soil as a reservoir, water and "
        "plants, measuring soil moisture, water requirements, rainfall and irrigation needs, topographic mapping and "
        "surveying, developing a water source, distributing water, field irrigation systems, drainage and economic "
        "evaluation.", WATER_SAFETY),
    _pc("pc_small_scale_irrigation_training_1983", "Small Scale Irrigation Systems: A Training Manual (Peace Corps, "
        "1983)", "Irrigation", "ERIC_ED307481", 1983, "Information Collection and Exchange",
        "Development Planning and Research Associates, Inc. for the Peace Corps",
        "A two-week workshop on planning, building, running and maintaining small irrigation systems: 33 sessions "
        "(soil classification, irrigation safety and health, topographic surveying and mapping, sizing and designing "
        "ditches, measuring water sources and more) and the teaching units behind them.", WATER_SAFETY),
    _pc("pc_wind_systems_pumping_water_1984", "Wind Systems for Pumping Water: A Training Manual (Peace Corps Training "
        "Manual T-25, 1984)", "Wind pumps", "micro_IA41153345_0710", 1984, "Training Manual T-25",
        "Willis Eschenbach with Domestic Technology International and the Denver Research Institute, under Peace "
        "Corps contract PC-283-1007",
        "A training course on windmills that pump water: judging the wind and the water need, choosing, building "
        "and siting a wind pump, towers, pumps and storage, and keeping them running.",
        WATER_SAFETY + TOOL_SAFETY + "Climb towers only with a harness, with the rotor stopped and tied. "),
    # ---------------------------------------------------------------- soil conservation
    _pc("pc_manual_conservation_soil_water_1985", "A Manual on Conservation of Soil and Water (US Department of "
        "Agriculture; Peace Corps Reprint R-38, 1985)", "Soil and water conservation", "ERIC_ED308074", 1985,
        "Reprint R-38", "the US Department of Agriculture",
        "The USDA's handbook on soil erosion and how to stop it, for officials, technicians and farmers anywhere: what "
        "soil erosion is, classifying land capability, preventing and controlling gullies, woodland improvement, "
        "terracing, strip-cropping, cover crops, soil-building crops, pasture and rangeland improvement, and using "
        "rainfall and irrigation water well.", FARM_SAFETY, licence="US_GOV",
        pdf_licence_text=r"(?i)Department\s+of\s+Agriculture"),
    _pc("pc_soil_conservation_hillside_farms_1986", "Soil Conservation Techniques for Hillside Farms: A Guide for "
        "Peace Corps Volunteers (Peace Corps Honduras, 1986)", "Soil and water conservation", "ERIC_ED288044", 1986,
        "Information Collection and Exchange", "Carl Crozier, illustrated by Kimball Koch (no contractor is named)",
        "Field techniques for farming steep land without losing the soil: contour lines with an A-frame level, live "
        "and dead barriers, terraces, ditches, replanting native vegetation, and working with farmers.", FARM_SAFETY),
    # ---------------------------------------------------------------- fish, bees and small animals
    _pc("pc_aquaculture_training_manual_1990", "Peace Corps Aquaculture Training Manual (Training Manual T0057, 1990)",
        "Fish ponds", "micro_IA41152945_0293", 1990, "Training Manual T0057",
        "the Peace Corps from two manuals made under contract by the University of Oklahoma (PC-284-1006) and the "
        "University of South Carolina (PC-287-1005)",
        "The Peace Corps' fish-culture training course (the \"Clemens model\"): building and managing fish ponds by "
        "hand, stocking, feeding and fertilizing, harvesting, and working with fish farmers, session by session.",
        "Ponds drown children: fence them and keep rescue gear at hand. " + FARM_SAFETY, licence=PC_FREE),
    _pc("pc_small_scale_beekeeping_1982", "Small Scale Beekeeping (Peace Corps Manual M-17, 1982)", "Beekeeping",
        "ERIC_ED241775", 1982, "Manual M-17", "Curtis Gentry under Peace Corps contract 81-043-1028",
        "Beekeeping as a tool for development: bees and people, planning a project, kinds and habits of bees, the "
        "essence of beekeeping, bee space and hives, intermediate-technology beekeeping (top-bar hives), high-tech "
        "beekeeping, hive products, and diseases, pests and insecticides, with hive and equipment plans, uses of "
        "beeswax and making an artificial swarm.", FARM_SAFETY),
    _pc("pc_beekeeping_trainers_manual_1983", "A Manual for Trainers of Small Scale Beekeeping Development Workers "
        "(Peace Corps, 1983)", "Beekeeping", "ERIC_ED242921", 1983, "Information Collection and Exchange",
        "Curtis Gentry, Michael E. Wilburn, Robert C. Rice and Charlotte Sommer of CHP International, Inc. under "
        "Peace Corps contract PC-282-1011",
        "The course that trains Volunteers in beekeeping, session by session: handling bees, building top-bar and "
        "Langstroth hives, finding and moving colonies, managing them through the seasons, harvesting, and teaching "
        "beekeepers.", FARM_SAFETY),
    _pc("pc_beekeeping_lesson_plans_philippines_1981", "Lesson Plans for Beekeeping in the Philippines (Peace Corps "
        "Reprint R-32, 1981)", "Beekeeping", "ERIC_ED241781", 1981, "Reprint R-32",
        "Diana Sammataro for a bee training seminar in the Philippines, 1978 (no contractor is named)",
        "Eight lesson plans for teaching beekeeping, with plans for hives and equipment: making beekeeping "
        "equipment, getting bees, handling bees, colony management through the seasons, the colony and races of "
        "bees, problems of beekeeping in the Philippines, raising queens, and marketing hive products.", FARM_SAFETY),
    _pc("pc_practical_poultry_raising_1981", "Practical Poultry Raising (Peace Corps Manual M-11, 1981)", "Poultry",
        "ERIC_ED241771", 1981, "Manual M-11",
        "Kenneth M. French for the TransCentury Corporation under Peace Corps contract 79-043-1029",
        "Starting or improving small-scale poultry keeping: local chickens, husbandry, housing and equipment, keeping "
        "chickens healthy, feed and nutrition (with a feed formulation chart), marketing and money, poultry other "
        "than chickens, and a glossary.", FARM_SAFETY),
    _pc("pc_animal_traction_1982", "Animal Traction (Peace Corps Manual M-12, 1982)", "Draft animals",
        "ERIC_ED241772", 1982, "Manual M-12",
        "Peter R. Watson for the TransCentury Corporation under Peace Corps contract 79-043-0129",
        "Using oxen, donkeys, horses and other draft animals for ploughing, carting and lifting water: choosing and "
        "training animals, feeding and care, harnesses and yokes, implements, and starting an animal traction "
        "programme. A few drawings and a table were reprinted by permission from other books; they belong to their "
        "publishers.", FARM_SAFETY),
    _pc("pc_livestock_training_manual_1982", "Agricultural Development Workers Training Manual, Volume IV: Livestock "
        "(Peace Corps, 1982)", "Small livestock", "ERIC_ED242886", 1982, "Information Collection and Exchange",
        "A. L. Nellum and Associates, Inc. under Peace Corps contract PC-282-1004",
        "The livestock part of the Peace Corps' agriculture course: lesson plans on livestock development, pigs, "
        "rabbits, poultry and goats, and over 120 technical information sheets (housing, feeding, breeding, health "
        "and records).", FARM_SAFETY),
    # ---------------------------------------------------------------- trees
    _pc("pc_agroforestry_inservice_training_1984", "Agroforestry In-Service Training: A Training Aid for Asia and the "
        "Pacific Islands (Peace Corps, 1984)", "Agroforestry", "ERIC_ED307483", 1984,
        "Information Collection and Exchange",
        "Jacob Fillion and Julius Weeks of the Peace Corps' Forestry and Natural Resources Sector",
        "A workshop held in the Solomon Islands in 1983 for Volunteers and their counterparts: agroforestry systems, "
        "nurseries, tree crops with field crops (such as Leucaena with corn), soil conservation with trees, costs "
        "and benefits, and extension.", FARM_SAFETY),
    _pc("pc_forestry_training_manual_africa_1984", "Forestry Training Manual for Africa Region (Peace Corps, 1984)",
        "Forestry and reforestation", "micro_IA41153301_0076", 1984, "Information Collection and Exchange",
        "George Mehaffey, Jacob Fillion and Julius Weeks of the Peace Corps' Forestry and Natural Resource "
        "Conservation Sector (Peace Corps/USAID Forestry Initiative)",
        "The training course for forestry Volunteers in Africa: tree nurseries, seed collection, planting, "
        "windbreaks, woodlots, agroforestry, soil conservation and working with villages, session by session.",
        FARM_SAFETY + TOOL_SAFETY),
    _pc("pc_volunteer_notes_reforestation_1982", "Volunteer Notes on Reforestation (Peace Corps Reprint R-45, 1982)",
        "Forestry and reforestation", "ERIC_ED242564", 1982, "Reprint R-45",
        "Peace Corps Volunteers in Chad, Ivory Coast, Upper Volta and Niger (no contractor is named)",
        "Reforestation projects in the Sahel as Volunteers described them: Borassus palms, village nurseries, sand "
        "dune stabilization, Acacia albida trees in grain fields and protecting natural regrowth, with the 1977 "
        "Peace Corps forestry conference's reports on windbreaks and direct seeding.", FARM_SAFETY),
    # ---------------------------------------------------------------- building
    _pc("pc_handbook_building_homes_of_earth_1981", "Handbook for Building Homes of Earth (Department of Housing and "
        "Urban Development for AID; Peace Corps Reprint R-34, 1981)", "Earth building", "ERIC_ED242877", 1981,
        "Reprint R-34", "Lyle A. Wolfskill, Wayne A. Dunlap and Bob M. Callaway of the Texas Transportation Institute "
        "for the Agency for International Development, published by HUD's Office of International Affairs",
        "How to build houses of earth: the kinds of soil and what each can do, soil stabilizers, site preparation, "
        "rammed earth, adobe and pressed blocks, simple tests the builder can make, walls, floors, roofs and "
        "finishes.", CEMENT_SAFETY),
    _pc("pc_bamboo_building_material_1981", "Bamboo as a Building Material (F. A. McClure, US Department of "
        "Agriculture, 1953; Peace Corps Reprint R-33, 1981)", "Bamboo building", "ERIC_ED242878", 1981,
        "Reprint R-33", "F. A. McClure of the USDA Foreign Agricultural Service",
        "Building with bamboo: the parts of a house bamboo suits, bamboo reinforcement of concrete, where bamboos "
        "grow and how species differ, shortcomings and how to overcome them, preserving bamboo, skills and tools "
        "needed, and collecting specimens for identification.", CEMENT_SAFETY + TOOL_SAFETY, licence="US_GOV",
        pdf_licence_text=r"(?i)Department\s+of\s+Agriculture"),
    # ---------------------------------------------------------------- energy and food drying
    _pc("pc_improved_cookstove_training_1984", "Improved Cookstove Training Manual (Peace Corps Training Manual T-40, "
        "1984)", "Cookstoves", "micro_IA41153345_0711", 1984, "Training Manual T-40",
        "Domestic Technology International under subcontract to the Denver Research Institute",
        "A training course on fuel-saving cookstoves: why stoves matter, how fire and heat transfer work, testing "
        "stoves, designing and building mud, clay and metal stoves, and spreading them in a community.",
        TOOL_SAFETY),
    _pc("pc_solar_energy_conserving_food_1984", "Solar and Energy Conserving Food Technologies: A Training Manual "
        "(Peace Corps Training Manual T-17, 1984)", "Solar cooking and food drying", "ERIC_ED307484", 1984,
        "Training Manual T-17", "the Farallones Institute under Peace Corps contract PC-184-1024",
        "An in-service course on solar and energy-saving food technologies: solar dryers, solar cookers, "
        "fuel-saving stoves and haybox cooking, and storing food.", TOOL_SAFETY),
    _pc("pc_appropriate_community_technology_1982", "Appropriate Community Technology: A Training Manual (Peace Corps "
        "Training Manual T-28, 1982)", "Appropriate technology", "ERIC_ED307485", 1982, "Training Manual T-28",
        "Donna Clavaud and others of the Farallones Institute under Peace Corps contract 81-042-1012",
        "A long training course in appropriate technology for the community: water and sanitation, solar energy, "
        "food drying and storage, fuel-saving cooking, simple tools and wheels, and working with people to choose "
        "technologies.", TOOL_SAFETY + WATER_SAFETY + CEMENT_SAFETY),
    _pc("pc_preserving_food_by_drying_1982", "Preserving Food by Drying: A Math/Science Teaching Manual (Peace Corps "
        "Manual M-10, 1982)", "Food drying", "ERIC_ED242558", 1982, "Manual M-10",
        "Program Designs for Educators for the Peace Corps",
        "Science and mathematics taught through food drying: how the sun heats air and water (evaporation, "
        "condensation, radiation, conduction and convection), building the best solar food dryer from local "
        "materials, and experiments with drying food and planning balanced meals.",
        "Dried food must be dried fully and stored dry and covered; low-acid foods are not made safe by drying "
        "alone. " + TOOL_SAFETY),
    _pc("pc_improved_food_drying_storage_1983", "Improved Food Drying and Storage Training Manual (Peace Corps, 1983)",
        "Food drying", "ERIC_ED242920", 1983, "Information Collection and Exchange",
        "Peter R. Zweig, Tom Gardiner and Charlotte Sommer of CHP International under Peace Corps contract "
        "PC-382-1013",
        "A 30-session course on drying and storing food: solar dryers, assessing a community, storage, smoke tests, "
        "rainy-season drying, pest control in stores, natural cooling and teaching adults.",
        "Dried food must be dried fully and stored dry and covered; never use pesticides on stored food except as "
        "today's labels allow. " + TOOL_SAFETY),
]

# ====================================================================== USGS and USDA (US government works)

USGS = "US Geological Survey (USGS), US Department of the Interior"
USGS_PAGE = "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits"
USGS_TEXT = r"the content of most USGS websites is in the U\.S\. Public Domain"


def _usgs(name, title, subject, year, pdf, page, description, notice):
    """One USGS publication read whole from pubs.usgs.gov (a US government work)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=USGS, pdf=pdf, page=page,
                    published=str(year), version=f"{year} edition ({page})", licence_page=USGS_PAGE,
                    licence_text=USGS_TEXT, description=description,
                    notice="From the US Geological Survey: a US government work (public domain). " + notice)


def _usda(name, title, subject, archive, year, number, author, description, notice):
    """One USDA Farmers' Bulletin or technical paper from the Internet Archive's copy of the National Agricultural
    Library's scan (a US government work)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, archive=archive, published=str(year),
                    publisher=f"US Department of Agriculture ({number})",
                    version=f"{year} edition ({number}; Internet Archive item {archive})",
                    description=description + f" By {author}.",
                    notice=("A work of the US Department of Agriculture (public domain), read from the National "
                            "Agricultural Library's scan on the Internet Archive: the machine-read text has the "
                            "scanner's mistakes. It is an old bulletin: check its advice against today's rules. "
                            + notice))


GOVERNMENT = [
    _usgs("usgs_well_drilling_methods_1911", "Well-Drilling Methods (Isaiah Bowman, USGS Water-Supply Paper 257, 1911)",
          "Well drilling", 1911, "https://pubs.usgs.gov/wsp/0257/report.pdf",
          "https://pubs.usgs.gov/publication/wsp257",
          "The USGS's survey of how water wells were made: ground water and where it lies, and every drilling method "
          "of the day, from earth augers, driven and jetted wells to hand-power and steam percussion (cable-tool) "
          "and diamond drills, with casing, screens, pumping and the troubles drillers meet.",
          WELL_SAFETY + WATER_SAFETY),
    _usgs("usgs_underground_waters_farm_use_1910", "Underground Waters for Farm Use (Myron L. Fuller, USGS "
          "Water-Supply Paper 255, 1910)", "Ground water", 1910, "https://pubs.usgs.gov/wsp/0255/report.pdf",
          "https://pubs.usgs.gov/publication/wsp255",
          "Ground water for the farm: where it comes from, springs and wells, how to find water, kinds of wells and "
          "how to make them, and keeping the water pure.", WELL_SAFETY + WATER_SAFETY),
    _usgs("usgs_ground_water_rural_homeowner_1988", "Ground Water and the Rural Homeowner (Roger M. Waller, USGS, "
          "1988)", "Ground water and private wells", 1988, "https://pubs.usgs.gov/gip/7000053/report.pdf",
          "https://pubs.usgs.gov/publication/7000053",
          "A plain booklet for people with their own well: what ground water is, how wells are made, water quality "
          "and contamination, wells going dry, and protecting the well and the water.",
          WATER_SAFETY + WELL_SAFETY),
    _usda("usda_farmstead_water_supply_1925", "Farmstead Water Supply (George M. Warren, USDA Farmers' Bulletin 1448, "
          "1925)", "Farm water supply", "CAT87203105", 1925, "Farmers' Bulletin 1448", "George M. Warren",
          "Water for the farm home: sources (wells, springs and cisterns), protecting them from pollution, pumps, "
          "windmills, hydraulic rams and tanks, and piping water to the house and barn.", WATER_SAFETY + WELL_SAFETY),
    _usda("usda_water_systems_farm_homes_1918", "Water Systems for Farm Homes (George M. Warren, USDA Farmers' "
          "Bulletin 941, 1918)", "Farm water supply", "CAT87202481", 1918, "Farmers' Bulletin 941", "George M. Warren",
          "Running water for farm houses: gravity systems from springs, pneumatic and elevated tanks, hand, wind, "
          "engine and ram pumps, pipes and fixtures, and planning a system.", WATER_SAFETY),
    _usda("usda_safe_water_for_the_farm_1948", "Safe Water for the Farm (H. L. Garver, USDA Farmers' Bulletin 1978, "
          "1948)", "Safe drinking water", "CAT87204952", 1948, "Farmers' Bulletin 1978", "H. L. Garver",
          "Making a farm water supply safe: locating and building wells, springs and cisterns so they stay clean, "
          "pumps and pressure systems, and disinfecting and treating water.", WATER_SAFETY + WELL_SAFETY),
    _usda("usda_water_supply_plumbing_sewage_country_homes_1914", "Water Supply, Plumbing, and Sewage Disposal for "
          "Country Homes (R. W. Trullinger, USDA Bulletin 57, 1914)", "Water supply and sanitation",
          "watersupplyplumb57trul", 1914, "Department Bulletin 57", "R. W. Trullinger",
          "Water supply, household plumbing and sewage disposal for country homes: sources and pumping, piping and "
          "fixtures, and septic tanks, cesspools and other ways of disposing of sewage.", WATER_SAFETY),
    _usda("usda_sanitary_privy_1911", "The Sanitary Privy (C. W. Stiles, USDA Farmers' Bulletin 463, 1911)",
          "Latrines", "CAT87202664", 1911, "Farmers' Bulletin 463", "C. W. Stiles of the Public Health and Marine "
          "Hospital Service",
          "Why the open privy spreads hookworm, typhoid and dysentery, and how to build and keep a sanitary privy.",
          WATER_SAFETY + "Clean or empty a privy only with gloves, and wash well; never enter a closed pit or tank. "),
    _usda("usda_sewage_garbage_disposal_farm_1946", "Sewage and Garbage Disposal on the Farm (J. W. Rockey, USDA "
          "Farmers' Bulletin 1950, 1946)", "Sewage and septic systems", "CAT87205382", 1946, "Farmers' Bulletin 1950",
          "J. W. Rockey",
          "Septic tanks and their care, disposal fields, privies and cesspools, and getting rid of garbage on the "
          "farm.",
          WATER_SAFETY + "Septic tanks hold deadly gases: never lean into or enter one. "),
    _usda("usda_rammed_earth_walls_1926", "Rammed Earth Walls for Buildings (M. C. Betts and T. A. H. Miller, USDA "
          "Farmers' Bulletin 1500, 1926)", "Earth building", "CAT87204481", 1926, "Farmers' Bulletin 1500",
          "M. C. Betts and T. A. H. Miller",
          "Building walls of rammed earth: choosing and testing the soil, forms, ramming, foundations, openings, "
          "roofs and finishing, and how such walls have lasted.", CEMENT_SAFETY),
    _usda("usda_adobe_sun_dried_brick_1934", "Adobe or Sun-Dried Brick for Farm Buildings (T. A. H. Miller, USDA "
          "Farmers' Bulletin 1720, 1934)", "Earth building", "CAT87204700", 1934, "Farmers' Bulletin 1720",
          "T. A. H. Miller",
          "Making and building with adobe: suitable soils, mixing and moulding bricks, curing, foundations, laying "
          "walls, protecting them from water, and plastering.", CEMENT_SAFETY),
    _usda("usda_concrete_livestock_farm_1912", "Concrete Construction on the Livestock Farm (USDA Farmers' Bulletin "
          "481, 1912)", "Concrete", "CAT87202468", 1912, "Farmers' Bulletin 481", "the USDA Bureau of Animal Industry",
          "Mixing and placing concrete for farm use: floors, feeding floors, troughs, tanks, walls, posts and silos.",
          CEMENT_SAFETY),
    _usda("usda_windmills_irrigation_1917", "The Use of Windmills in Irrigation in the Semiarid West (P. E. Fuller, "
          "USDA Farmers' Bulletin 866, 1917)", "Windmills and irrigation", "CAT87202797", 1917, "Farmers' Bulletin 866",
          "P. E. Fuller",
          "Irrigating a small farm or garden with windmill power: how much a windmill pumps, wells and pumps, storage "
          "reservoirs, and costs.", WATER_SAFETY + TOOL_SAFETY),
    _usda("usda_holding_water_farm_ponds_1956", "Holding Water in Farm Ponds (H. N. Holton, Soil Conservation Service "
          "SCS-TP-93, 1956)", "Farm ponds", "holdingwaterinfa93holt", 1956, "SCS Technical Paper 93", "H. N. Holton",
          "Why farm ponds leak and how to seal them: soils, compaction, clay blankets and other treatments.",
          "Ponds drown children: fence them and keep rescue gear at hand; a dam can fail, so have bigger dams designed "
          "by an engineer and follow local rules. "),
    _usda("usda_fish_for_food_farm_ponds_1944", "Fish for Food from Farm Ponds (Verne E. Davison, USDA Farmers' "
          "Bulletin 1938, 1944)", "Fish ponds", "CAT85826350", 1944, "Farmers' Bulletin 1938", "Verne E. Davison",
          "Raising fish for the table in farm ponds: building the pond, stocking bass and bream, fertilizing, "
          "controlling weeds and fishing it right.",
          "Ponds drown children: fence them and keep rescue gear at hand. " + FARM_SAFETY),
    _usda("usda_warm_water_ponds_fishing_1965", "Warm-Water Ponds for Fishing (William W. Neely, USDA Farmers' "
          "Bulletin 2210, 1965)", "Fish ponds", "CAT87205122", 1965, "Farmers' Bulletin 2210", "William W. Neely",
          "Building and managing a warm-water fishing pond: the site, the dam and spillway, stocking, fertilizing, "
          "weed control and harvest.", "Ponds drown children: fence them and keep rescue gear at hand. " + FARM_SAFETY),
]

# ====================================================================== old public-domain books


def _old(name, title, subject, publisher, archive, year, description, notice, country="United States"):
    """One old public-domain book (old_ia_books.old_book) with its safety notes."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=OLD_NOTE, notice=notice,
                    country=country)


OLD_BOOKS = [
    _old("cobleigh_handy_farm_devices_1910", "Handy Farm Devices and How to Make Them (Rolfe Cobleigh, 1910)",
         "Home-made farm equipment", "Rolfe Cobleigh (Orange Judd Company)", "handyfarmdevices00cobl", 1910,
         "Hundreds of things a farmer can make himself: the farm workshop, benches and tool racks, gates and fences, "
         "sawhorses, ladders, wagons, sleds and carts, devices for lifting and moving, hog, poultry and stock "
         "equipment, ice houses, water and drainage devices, and repairs.", TOOL_SAFETY),
    _old("drew_farm_blacksmithing_1904", "Farm Blacksmithing (James M. Drew, 1904 printing)", "Blacksmithing",
         "James M. Drew (Webb Publishing)", "farmblacksmithin00drew", 1904,
         "A textbook of blacksmithing for the farm shop: the forge and fire, tools, drawing out, upsetting, bending, "
         "welding, punching, making hooks, rings, chains and clevises, and tempering and hardening tools.",
         TOOL_SAFETY),
    _old("shearer_farm_mechanics_1918", "Farm Mechanics: Machinery and Its Use to Save Hand Labor on the Farm "
         "(Herbert A. Shearer, 1918)", "Farm mechanics", "Herbert A. Shearer (Frederick J. Drake)",
         "farmmechanics00shea", 1918,
         "Tools and machines for the farm: the farm shop, carpentry, rope work, belts and pulleys, pumps, engines, "
         "harness repair, soldering, painting and the care of farm machines.", TOOL_SAFETY),
    _old("brace_mayne_farm_shop_work_1915", "Farm Shop Work: Practical Manual Training (George M. Brace and D. D. "
         "Mayne, 1915)", "Farm shop", "George M. Brace and Dexter D. Mayne (American Book Company)",
         "cu31924003595026", 1915,
         "Woodworking and metalworking for farm boys and girls: tools and their care, joints, building farm "
         "appliances, concrete work, forging, and rope work.", TOOL_SAFETY + CEMENT_SAFETY),
    _old("chapman_treatise_ropemaking_1869", "A Treatise on Ropemaking, as Practised in Private and Public Ropeyards "
         "(Robert Chapman, 1869 American edition)", "Rope making", "Robert Chapman (Philadelphia)",
         "treatiseonropema00chap", 1869,
         "How rope was made by hand in the ropewalk: hemp and other fibres, hackling, spinning yarn, tarring, laying "
         "strands and ropes, cables and cordage, and testing strength.", TOOL_SAFETY, country="United Kingdom"),
    _old("mechanics_for_young_america_1905", "Mechanics for Young America: How to Build Boats, Water Motors, Wind "
         "Mills and More (Popular Mechanics, 1905)", "Simple machines and models", "Popular Mechanics Company",
         "mechanicsforyoun00chic", 1905,
         "Things to build at home from Popular Mechanics: boats, water motors, windmills, searchlights, electric "
         "lights, telephones and other devices.", TOOL_SAFETY),
    _old("isler_well_boring_1902", "Well-Boring for Water, Brine and Oil: A Manual of Current Practice (C. Isler, "
         "1902)", "Well drilling", "C. Isler (E. and F. N. Spon, London)", "wellboringforwat00islerich", 1902,
         "A manual of boring wells: the geology of water, hand and machine boring tools, percussion and rotary "
         "boring, lining tubes, and the troubles of the work.", WELL_SAFETY + WATER_SAFETY, country="United Kingdom"),
    _old("hutton_country_plumbing_1914", "Country Plumbing Practice: Design, Installation and Repair of Systems of "
         "Water Supply and Sewage Disposal (William Hutton, 1914)", "Country plumbing",
         "William Hutton (David Williams Company)", "countryplumbingp00huttrich", 1914,
         "Plumbing away from town mains: water supply from wells, springs and cisterns, pumps, rams, windmills and "
         "tanks, house plumbing, and septic tanks and other sewage disposal.", WATER_SAFETY + TOOL_SAFETY),
    _old("seaton_concrete_rural_communities_1916", "Concrete Construction for Rural Communities (Roy A. Seaton, 1916)",
         "Concrete", "Roy A. Seaton (McGraw-Hill)", "concreconstruct00seatrich", 1916,
         "Concrete work for farms and small towns: cement, sand, stone and water, proportioning and mixing, forms, "
         "reinforcing, and building walks, floors, walls, tanks, troughs, posts and small bridges.", CEMENT_SAFETY),
    _old("dobson_bricks_and_tiles_1850", "A Rudimentary Treatise on the Manufacture of Bricks and Tiles (Edward "
         "Dobson, 1850)", "Brick making", "Edward Dobson (John Weale, London)", "gri_33125007133560", 1850,
         "How bricks and tiles were made: brick earths and clays, preparing the clay, moulding by hand and machine, "
         "drying, burning in clamps and kilns, and tile making.", CEMENT_SAFETY + TOOL_SAFETY,
         country="United Kingdom"),
]

PDFS = PEACE_CORPS + GOVERNMENT + OLD_BOOKS

# ====================================================================== themes (request words)

THEMES = {
    "apt-water": [
        "pc_wells_construction_1982", "pc_water_sanitation_technologies_1985", "pc_water_purification_sewage_1979",
        "pc_irrigation_principles_practices_1982", "pc_small_scale_irrigation_systems_1983",
        "pc_small_scale_irrigation_training_1983", "pc_wind_systems_pumping_water_1984",
        "usgs_well_drilling_methods_1911", "usgs_underground_waters_farm_use_1910",
        "usgs_ground_water_rural_homeowner_1988", "usda_farmstead_water_supply_1925",
        "usda_water_systems_farm_homes_1918", "usda_safe_water_for_the_farm_1948", "usda_windmills_irrigation_1917",
        "usda_holding_water_farm_ponds_1956", "isler_well_boring_1902", "hutton_country_plumbing_1914"],
    "apt-building": [
        "pc_handbook_building_homes_of_earth_1981", "pc_bamboo_building_material_1981", "usda_rammed_earth_walls_1926",
        "usda_adobe_sun_dried_brick_1934", "usda_concrete_livestock_farm_1912",
        "seaton_concrete_rural_communities_1916", "dobson_bricks_and_tiles_1850"],
    "apt-farming": [
        "pc_manual_conservation_soil_water_1985", "pc_soil_conservation_hillside_farms_1986",
        "pc_aquaculture_training_manual_1990", "pc_small_scale_beekeeping_1982", "pc_beekeeping_trainers_manual_1983",
        "pc_beekeeping_lesson_plans_philippines_1981", "pc_practical_poultry_raising_1981", "pc_animal_traction_1982",
        "pc_livestock_training_manual_1982", "pc_agroforestry_inservice_training_1984",
        "pc_forestry_training_manual_africa_1984", "pc_volunteer_notes_reforestation_1982",
        "pc_preserving_food_by_drying_1982", "pc_improved_food_drying_storage_1983",
        "usda_fish_for_food_farm_ponds_1944", "usda_warm_water_ponds_fishing_1965"],
    "apt-energy-tools": [
        "pc_improved_cookstove_training_1984", "pc_solar_energy_conserving_food_1984",
        "pc_appropriate_community_technology_1982", "pc_wind_systems_pumping_water_1984",
        "cobleigh_handy_farm_devices_1910", "drew_farm_blacksmithing_1904", "shearer_farm_mechanics_1918",
        "brace_mayne_farm_shop_work_1915", "chapman_treatise_ropemaking_1869", "mechanics_for_young_america_1905"],
    "apt-health": [
        "pc_water_sanitation_technologies_1985", "pc_water_purification_sewage_1979", "usda_sanitary_privy_1911",
        "usda_sewage_garbage_disposal_farm_1946", "usda_safe_water_for_the_farm_1948",
        "usda_water_supply_plumbing_sewage_country_homes_1914", "hutton_country_plumbing_1914"],
}

# ====================================================================== the index

SECTIONS = [
    ("Start here", "What this collection is: practical skills for a village or a farm without shops or mains. The "
     "Peace Corps manuals were written for Volunteers in Africa, Asia and Latin America in the 1970s and 1980s; the "
     "USDA bulletins and old books for American farms. Each book says what is out of date. Safety first: never go "
     "down a well or into a pit or tank until the air is tested, never use explosives, test drinking water, and "
     "protect skin and eyes from wet cement and lime.", [
        ("word", "approtech", "Every appropriate technology book (request word)"),
        ("word", "apt-water", "Water, wells, pumps and irrigation (request word)"),
        ("word", "apt-building", "Building with earth, bamboo, brick and concrete (request word)"),
        ("word", "apt-farming", "Soil, trees, fish, bees, small animals and food drying (request word)"),
        ("word", "apt-energy-tools", "Stoves, sun and wind, hand tools, the forge and rope (request word)"),
        ("word", "apt-health", "Safe water, latrines and sewage (request word)")]),
    ("Water and wells", "Finding water, digging and drilling wells, pumps, springs and keeping water clean.", [
        ("key", "apt:pc_wells_construction_1982", "Wells Construction: hand-dug and hand-drilled wells (Peace Corps)"),
        ("key", "apt:usgs_well_drilling_methods_1911", "Well-Drilling Methods (USGS, 1911)"),
        ("key", "apt:isler_well_boring_1902", "Well-Boring for Water (Isler, 1902)"),
        ("key", "apt:usgs_underground_waters_farm_use_1910", "Underground Waters for Farm Use (USGS, 1910)"),
        ("key", "apt:usgs_ground_water_rural_homeowner_1988", "Ground Water and the Rural Homeowner (USGS)"),
        ("key", "apt:usda_farmstead_water_supply_1925", "Farmstead Water Supply (USDA, 1925)"),
        ("key", "apt:usda_water_systems_farm_homes_1918", "Water Systems for Farm Homes (USDA, 1918)"),
        ("key", "apt:pc_wind_systems_pumping_water_1984", "Wind Systems for Pumping Water (Peace Corps)"),
        ("key", "homestead:epa_private_wells_septic", "Private wells and septic systems (EPA, personal use)"),
        ("manuals", "water_treatment", "Water filters and treatment equipment makers' manuals")]),
    ("Safe water and sanitation", "Latrines, septic tanks and treating water so it does not make people ill.", [
        ("key", "apt:pc_water_sanitation_technologies_1985", "Water and Sanitation Technologies (Peace Corps)"),
        ("key", "apt:pc_water_purification_sewage_1979", "Water Purification, Distribution and Sewage Disposal"),
        ("key", "apt:usda_sanitary_privy_1911", "The Sanitary Privy (USDA, 1911)"),
        ("key", "apt:usda_sewage_garbage_disposal_farm_1946", "Sewage and Garbage Disposal on the Farm (USDA)"),
        ("key", "apt:usda_safe_water_for_the_farm_1948", "Safe Water for the Farm (USDA, 1948)"),
        ("key", "apt:usda_water_supply_plumbing_sewage_country_homes_1914",
         "Water Supply, Plumbing, and Sewage Disposal for Country Homes (USDA, 1914)"),
        ("key", "apt:hutton_country_plumbing_1914", "Country Plumbing Practice (Hutton, 1914)"),
        ("word", "preparedness", "Emergency preparedness books: storing and treating water"),
        ("word", "first-aid", "First aid books")]),
    ("Irrigation, ponds and soil", "Watering crops, small dams and ponds, and stopping erosion.", [
        ("key", "apt:pc_irrigation_principles_practices_1982", "Irrigation Principles and Practices (Peace Corps)"),
        ("key", "apt:pc_small_scale_irrigation_systems_1983", "Small Scale Irrigation Systems (Peace Corps)"),
        ("key", "apt:pc_small_scale_irrigation_training_1983", "Small Scale Irrigation: a training manual"),
        ("key", "apt:usda_windmills_irrigation_1917", "Windmills in irrigation (USDA, 1917)"),
        ("key", "apt:usda_holding_water_farm_ponds_1956", "Holding Water in Farm Ponds (Soil Conservation Service)"),
        ("key", "apt:pc_manual_conservation_soil_water_1985", "A Manual on Conservation of Soil and Water (USDA)"),
        ("key", "apt:pc_soil_conservation_hillside_farms_1986", "Soil Conservation for Hillside Farms (Peace Corps)"),
        ("key", "garden:nrcs_soil_health", "Soil health (USDA NRCS)")]),
    ("Building", "Houses of earth, adobe, rammed earth, bamboo, brick and concrete.", [
        ("key", "apt:pc_handbook_building_homes_of_earth_1981", "Handbook for Building Homes of Earth"),
        ("key", "apt:usda_rammed_earth_walls_1926", "Rammed Earth Walls for Buildings (USDA, 1926)"),
        ("key", "apt:usda_adobe_sun_dried_brick_1934", "Adobe or Sun-Dried Brick (USDA, 1934)"),
        ("key", "apt:pc_bamboo_building_material_1981", "Bamboo as a Building Material (USDA)"),
        ("key", "apt:dobson_bricks_and_tiles_1850", "The Manufacture of Bricks and Tiles (Dobson, 1850)"),
        ("key", "apt:seaton_concrete_rural_communities_1916", "Concrete Construction for Rural Communities (1916)"),
        ("key", "apt:usda_concrete_livestock_farm_1912", "Concrete Construction on the Livestock Farm (USDA)"),
        ("key", "build:army_fm_5_428_concrete_masonry", "Concrete and Masonry (Army FM 5-428)"),
        ("key", "build:army_fm_5_426_carpentry", "Carpentry (Army FM 5-426)"),
        ("word", "building", "The building and light construction books (request word)"),
        ("manuals", "home_construction", "Building material and tool makers' manuals")]),
    ("Farming, fish, bees and small animals", "Fish ponds, beekeeping, poultry, rabbits, goats and draft animals.", [
        ("key", "apt:pc_aquaculture_training_manual_1990", "Peace Corps Aquaculture Training Manual"),
        ("key", "apt:usda_fish_for_food_farm_ponds_1944", "Fish for Food from Farm Ponds (USDA)"),
        ("key", "apt:usda_warm_water_ponds_fishing_1965", "Warm-Water Ponds for Fishing (USDA)"),
        ("key", "apt:pc_small_scale_beekeeping_1982", "Small Scale Beekeeping (Peace Corps)"),
        ("key", "apt:pc_beekeeping_trainers_manual_1983", "A Manual for Trainers of Beekeeping Workers"),
        ("key", "apt:pc_beekeeping_lesson_plans_philippines_1981", "Lesson Plans for Beekeeping in the Philippines"),
        ("key", "apt:pc_practical_poultry_raising_1981", "Practical Poultry Raising (Peace Corps)"),
        ("key", "apt:pc_livestock_training_manual_1982", "Livestock: pigs, rabbits, poultry and goats (Peace Corps)"),
        ("key", "apt:pc_animal_traction_1982", "Animal Traction: oxen and donkeys at work (Peace Corps)"),
        ("word", "homestead", "Homesteading books: old bee, poultry, goat, rabbit and pig books (request word)"),
        ("word", "gardening", "Gardening books (request word)"),
        ("manuals", "farm_equipment", "Farm equipment makers' manuals")]),
    ("Trees", "Nurseries, reforestation, windbreaks and growing trees with crops.", [
        ("key", "apt:pc_agroforestry_inservice_training_1984", "Agroforestry In-Service Training (Peace Corps)"),
        ("key", "apt:pc_forestry_training_manual_africa_1984", "Forestry Training Manual for Africa (Peace Corps)"),
        ("key", "apt:pc_volunteer_notes_reforestation_1982", "Volunteer Notes on Reforestation (Peace Corps)"),
        ("key", "build:fpl_wood_handbook", "Wood Handbook (Forest Products Laboratory)")]),
    ("Food drying and storage", "Drying food in the sun and keeping it from pests.", [
        ("key", "apt:pc_preserving_food_by_drying_1982", "Preserving Food by Drying (Peace Corps)"),
        ("key", "apt:pc_improved_food_drying_storage_1983", "Improved Food Drying and Storage (Peace Corps)"),
        ("key", "apt:pc_solar_energy_conserving_food_1984", "Solar and Energy Conserving Food Technologies"),
        ("word", "preserving", "Home food preserving books: canning, drying, salting (request word)"),
        ("word", "foraging", "Edible wild plants and foraging (request word)")]),
    ("Energy and stoves", "Fuel-saving stoves, sun, wind and water power.", [
        ("key", "apt:pc_improved_cookstove_training_1984", "Improved Cookstove Training Manual (Peace Corps)"),
        ("key", "apt:pc_appropriate_community_technology_1982", "Appropriate Community Technology (Peace Corps)"),
        ("key", "power:powell_windmills_wind_motors_1910", "Windmills and Wind Motors (Powell, 1910)"),
        ("key", "power:murphy_the_windmill_1901", "The Windmill (USGS, 1901)"),
        ("key", "power:anderson_electricity_for_the_farm_1915",
         "Electricity for the Farm, from the water wheel (1915)"),
        ("key", "power:doe_small_wind", "Small wind systems (US Department of Energy)"),
        ("key", "power:doe_hydropower_basics", "How hydropower works (US Department of Energy)"),
        ("word", "solar", "Solar power books (request word)"),
        ("word", "backup-power", "Backup power and generator books (request word)"),
        ("manuals", "wind_hydro_power", "Wind and small hydro makers' manuals")]),
    ("Tools, the forge and rope", "Making farm devices, blacksmithing, the farm shop and rope making.", [
        ("key", "apt:cobleigh_handy_farm_devices_1910", "Handy Farm Devices and How to Make Them (1910)"),
        ("key", "apt:drew_farm_blacksmithing_1904", "Farm Blacksmithing (Drew)"),
        ("key", "apt:shearer_farm_mechanics_1918", "Farm Mechanics (Shearer, 1918)"),
        ("key", "apt:brace_mayne_farm_shop_work_1915", "Farm Shop Work (Brace and Mayne, 1915)"),
        ("key", "apt:chapman_treatise_ropemaking_1869", "A Treatise on Ropemaking (Chapman, 1869)"),
        ("key", "apt:mechanics_for_young_america_1905", "Mechanics for Young America (1905)"),
        ("key", "build:army_tm_9_243_hand_tools", "Use and Care of Hand Tools (Army TM 9-243)"),
        ("word", "knots-outdoor", "Knots, rope, axes and saws (request word)"),
        ("manuals", "hand_tools", "Hand tool makers' manuals")]),
    ("Links only (copyright)", "These are not built: open them in a browser, or fetch them for your own use.", [
        ("link", "VITA technical papers and manuals (Volunteers in Technical Assistance)",
         "https://archive.org/search?query=%22Volunteers+in+Technical+Assistance%22",
         "copyright of VITA (for example \"(c) 1984, Volunteers in Technical Assistance\")"),
        ("link", "Freshwater Fish Pond Culture and Management (Peace Corps/VITA, 1976)",
         "https://archive.org/details/ERIC_ED242565",
         "(c) VITA 1976; reproduction allowed only for official US government purposes"),
        ("link", "Small Farm Grain Storage (Peace Corps/VITA, 1976)", "https://archive.org/details/ERIC_ED241766",
         "a joint Peace Corps/VITA manual of the VITA-copyright series"),
        ("link", "Reforestation in Arid Lands (Peace Corps/VITA, 1977)", "https://archive.org/details/ERIC_ED242563",
         "(c) VITA 1977; reproduction allowed only for official US government purposes"),
        ("link", "Self-Help Construction of 1-Story Buildings (Peace Corps/VITA, 1977)",
         "https://archive.org/details/ERIC_ED241769", "a joint Peace Corps/VITA manual of the VITA-copyright series"),
        ("link", "Environmentally Sound Small-Scale Projects: guidelines for planning (CODEL and VITA, 1979 to 1986)",
         "https://archive.org/details/micro_IA41152934_0614", "copyright of the Mohonk Trust and CODEL"),
        ("link", "The Appropriate Technology Library (Village Earth)", "https://villageearth.org/",
         "a mixed collection, mostly in copyright; open it in a browser")]),
]
INDEX = X.index_maker("apt", GROUP, "Appropriate technology and village skills: a guide to the library",
                      "Appropriate technology and village skills",
                      "A guide in plain words to the library's appropriate technology books: water and wells, "
                      "sanitation, irrigation and soil, building, farming, fish, bees and small animals, trees, food "
                      "drying, energy and stoves, and tools, with the copyright works as links.", SECTIONS)
MAKERS = {"index": INDEX}


def _keys(names):
    """The apt: keys of a list of entry names."""
    return [f"apt:{n}" for n in names]


WORDS = {word: (lambda names=names: _keys(names)) for word, names in THEMES.items()}
WORDS["approtech"] = lambda: ["apt:index"] + _keys(p["name"] for p in PDFS)

COLLECTION = K.Collection("apt", GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "apt_peace_corps": "Peace Corps ICE manuals (Internet Archive copies of ERIC's scans; archive.org's robots.txt "
                       "allows the files, no AI rules, checked 2026-11-23): built when printed with no copyright "
                       "notice before 1 March 1989 (17 U.S.C. 405; the Copyright Office's chapter 4 page is checked "
                       "at every build, and each PDF's front pages must name the Peace Corps and claim no copyright "
                       "or Peace Corps-only permission), or when the copy prints \"may be reproduced and/or "
                       "translated in part or in full without payment or royalty\" (checked in the PDF at every "
                       "build). The USDA reprints (R-33, R-38) are US government works.",
    "apt_us_gov": "USGS (pubs.usgs.gov; the USGS copyright page is checked at every build; robots.txt allows all but "
                  "/archive/) and USDA Farmers' Bulletins (the National Agricultural Library's scans on the Internet "
                  "Archive): works of the US government (17 U.S.C. 105).",
    "apt_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build). "
                     "Chapman, Isler and Dobson are British books: public domain in the US as published before 1931.",
    "apt_index": "The index (apt:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Joint Peace Corps/VITA manuals: Freshwater Fish Pond Culture and Management (M-1B, 1976), Small Farm Grain "
     "Storage (M-2, 1976), Reforestation in Arid Lands (M-5, 1977), Self-Help Construction of 1-Story Buildings "
     "(M-6, 1977)", "The fish pond and reforestation volumes print \"(c) VITA\" with reproduction allowed only "
     "\"for official U.S. Government purposes\"; the grain storage and construction volumes belong to the same "
     "joint series. Copyright: link-only from the index. Index: https://archive.org/details/ERIC_ED242565"),
    ("VITA technical papers (such as Understanding Solar Food Dryers, 1984) and the CODEL/VITA Environmentally Sound "
     "Small-Scale Projects guidelines (1979 to 1986)", "Copyright of Volunteers in Technical Assistance, the Mohonk "
     "Trust and CODEL (their own notices). Link-only. Index: "
     "https://archive.org/details/understanding-solar-food-dryers-technical-paper-15"),
    ("A Complete Handbook on Backyard and Commercial Rabbit Production (Peace Corps Reprint, 1982)", "Printed "
     "\"Reprinted with permission for Peace Corps use only\": copyright of its Philippine authors. Link-only. Index: "
     "https://archive.org/details/ERIC_ED241783"),
    ("Irrigation Training Manual and Irrigation Reference Manual (Peace Corps T0076 and T0077, 1994)", "Written "
     "under contract by Agro Engineering, Inc. and published after 1 March 1989 without the Peace Corps' "
     "reproduction line, so the old notice rule does not apply. Link-only. Index: "
     "https://archive.org/details/ERIC_ED378400"),
    ("The Biogas/Biofertilizer Business Handbook (Peace Corps Reprint R-48, 1985) and the Chinese Biogas Digester "
     "(Reprint R-51, 1985)", "The first is its author's own book (\"not for sale\", its sources under their "
     "copyrights); the second a Philippine co-publication (PRRM and German Agro-Action), so the US notice rule does "
     "not settle it. Link-only. Index: https://archive.org/details/ERIC_ED309038"),
    ("Remote Areas Development Manual (Community Development Counselling Service, 1964; Peace Corps Reprint R-36)",
     "Compiled by a private company from many sources, not checked one by one. Link-only. Index: "
     "https://archive.org/details/ERIC_ED242881"),
    ("Peace Corps health, nutrition, education, business, crops and training manuals, translations, and the language "
     "courses", "Taken by the peace-corps and peace-corps-lang helpers (pc:), by the owner's division of 23 November "
     "2026; the ids used here are in notes/approtech-peace-corps-ids.txt. Index: "
     "https://archive.org/search?query=creator%3A%22Information+Collection+and+Exchange%22"),
    ("Army well-drilling manuals: TM 5-297 Well Drilling Operations, FM 5-166 (1975) and FM 5-484 (1994)", "Left to "
     "the service-skills helper, who takes the Army technical manuals, so no address is used twice. Index: "
     "https://archive.org/details/FM_5_484_M_P_W_D_O_1994"),
    ("Village Technology Handbook (VITA) and the Appropriate Technology Library (Village Earth)", "The Internet "
     "Archive's copy of the handbook is a lending-library scan; the library is a mixed collection, mostly in "
     "copyright. Link-only. Index: https://villageearth.org/"),
    ("FAO manuals on small dams, fish ponds and irrigation", "FAO's publications are CC BY-NC-SA 3.0 IGO (personal "
     "use) or all rights reserved; not built in this open collection. Index: "
     "https://www.fao.org/publications/en/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
