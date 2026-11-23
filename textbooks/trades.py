"""Trades, apprenticeship and workplace safety for the reference library, in the group "Reference, trades and
workplace safety" (the owner's request of 2026-11-23: practical trade skills and safety knowledge). Keys: trades (every
book), trade:<name>, and one request word per theme: trade-construction, trade-industry, trade-farm,
trade-apprentice and trade-texts.

What this module builds, in plain words:
  - OSHA's booklets (US Department of Labor, public domain) from the Defense Technical Information Center's copies on
    the Internet Archive (osha.gov refuses programs: it answered this build machine "403" on 2026-11-23): lockout and
    tagout, confined spaces, excavations, ground-fault protection, crane platforms, concrete and masonry, asbestos,
    hazard communication, HAZWOPER, hearing conservation, respirators, protective equipment, hand and power tools,
    machine guarding, amputations, woodworking, grain handling, rim wheels, longshoring, job hazard analysis,
    workers' and employers' rights and others. They are older editions (1988 to 2001): every notice says so;
  - OSHA publications taken off osha.gov in early 2025, from the copy a private uploader saved on the Internet Archive
    (item 2025-removed-osha): recommended practices for construction, the respiratory protection guides, ergonomics
    for grocery stores, shipyards and nursing homes, and workplace mental health in English and in Spanish;
  - the OSHA standards themselves: 29 CFR 1926 (construction), 29 CFR 1910 (general industry, in two books: parts
    1910.1 to 1910.999, and Subpart Z, toxic and hazardous substances, 1910.1000 onward, with Hazard Communication)
    and 29 CFR 1928 (agriculture), each from govinfo.gov's newest annual edition (cfr_maker checks that the volume
    read really starts with the expected section);
  - NIOSH publications (CDC, public domain under CDC's terms, read from www.cdc.gov at every build): the Pocket Guide
    to Chemical Hazards, the electrical trades student manual, Simple Solutions for construction and farm workers,
    the lifting equation and manual material handling, noise, heat and welding criteria documents, respirator
    guides, nail gun safety, forklifts, hand tools, the Talking Safety curriculum for young workers, and "shelves"
    (one book made of several short NIOSH publications, pdf_set.py): construction toolbox talks, construction
    hazards, heat stress, hearing, respirators, farm safety, young workers, chemicals in the trades, and drivers;
  - MSHA's instructor guides and training reference guide for mine trainers (msha.gov); the Department of Energy's
    Electrical Safety handbook (DOE-HDBK-1092-2013) and Hoisting and Rigging standard (DOE-STD-1090-2020)
    (energy.gov); the Forest Service's Chain Saw Training Guide (1978, the National Agricultural Library's scan);
  - the Bureau of Labor Statistics' Occupational Outlook Handbook, 2012-13 edition (Bulletin 2800), read from
    Claitor's reprint on the Internet Archive (bls.gov refuses programs; Claitor's claims copyright only in its format);
  - trade texts: Wikibooks' Welding (CC BY-SA 4.0, share-alike, kept separate) and old public-domain trade books
    (published before 1931: plumbing, steam and hot-water heating, masonry and bricklaying, carpentry, sheet metal,
    welding, electrical work, machine shop, blacksmithing, auto repair, barbering), each with a note on what is out
    of date;
  - trade:index, the guide to every trade (carpentry, electrical, plumbing, HVAC, welding, masonry, roofing, auto,
    diesel, heavy equipment, landscaping, culinary, cosmetology and more): what to read, by key, across the library.

Already in the library and not repeated (the index links them): OSHA's scaffold and fall protection guides
(build:osha_3150_scaffold_use, build:osha_3146_fall_protection), Controlling Electrical Hazards
(power:osha_controlling_electrical_hazards_1997), the Army and Navy carpentry, masonry, machinist and builder manuals
(build:, make:), Apprenticeship.gov and Job Corps (edu:apprenticeship_gov, edu:job_corps), O*NET (mw:onet_occupations),
the Forest Service's crosscut saw books (knot:), the NIOSH Pocket Guide's chemical index in the manual collection
"chemical_safety" (here it is the whole book), and the whole Open Textbook Library (cat:otl) and BCcampus Kolibri
channel, where the openly licensed trade textbooks are. Military trade manuals are not added here.

Safety: every notice but the careers handbook's ends with TRADE_SAFETY (current standards, training, protective
equipment, asking first); the old electrical books add ELECTRICAL_NOTE.

Run from the repository's folder:
  python3 textbooks/trades.py trade:osha_3120_lockout_tagout --out build/textbooks --limit 3
  python3 textbooks/trades.py --list trades
"""

import datetime
import os
import re
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from electronics_books import wikibook  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "trades"
GROUPS = {GROUP: "Reference, trades and workplace safety"}

TRADE_SAFETY = ("Safety: follow the current OSHA standards (or your state plan's), your employer's safety program and "
                "the maker's instructions; get trained before you use a tool, machine or vehicle, wear the protective "
                "equipment the job calls for, and ask your supervisor or a safety professional when unsure.")
OSHA = "US Occupational Safety and Health Administration (OSHA), US Department of Labor"
OSHA_DTIC_NOTICE = ("A work of the US Occupational Safety and Health Administration (public domain, 17 U.S.C. 105), "
                    "from the Defense Technical Information Center's copy on the Internet Archive (osha.gov refuses "
                    "programs). An older edition: OSHA's standards and advice have changed since; check osha.gov for "
                    "the current edition and standard. ")
REMOVED = "2025-removed-osha"
OSHA_REMOVED_NOTICE = ("A work of the US Occupational Safety and Health Administration (public domain, 17 U.S.C. 105), "
                       "from the copy a private uploader saved on the Internet Archive (item 2025-removed-osha) after "
                       "OSHA took it off osha.gov in early 2025: it may no longer be OSHA's current guidance. ")
NIOSH = "National Institute for Occupational Safety and Health (NIOSH), CDC"
NIOSH_PAGE = "https://www.cdc.gov/niosh/publications/numbered/{}.html"
MSHA = "Mine Safety and Health Administration (MSHA), US Department of Labor"
MSHA_PAGE = "https://www.msha.gov/training/instructor-materials"
MSHA_NOTICE = ("A work of the Mine Safety and Health Administration (US Department of Labor), public domain (17 U.S.C. "
               "105), read from msha.gov. Mine operators follow 30 CFR parts 46 and 48 and MSHA's current rules. ")
DOE = "US Department of Energy, Office of Environment, Health, Safety and Security"
DOE_NOTICE = "A work of the US Department of Energy (public domain, 17 U.S.C. 105), read from energy.gov. "
OLD_TRADE_NOTE = ("Published in {year}: its methods, materials (such as lead, asbestos and old wiring) and safety "
                  "practices are those of its day; follow today's codes, licensing rules and safety standards.")
ELECTRICAL_NOTE = ("Electrical work can kill: old wiring methods in this book are not safe or legal today; follow the "
                   "current National Electrical Code and local rules, and leave mains wiring to a licensed "
                   "electrician.")


def osha(name, title, subject, archive, published, description, number=""):
    """One OSHA booklet from DTIC's copy on the Internet Archive (see OSHA_DTIC_NOTICE)."""
    edition = f"{number}, {published}" if number else published
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=OSHA, archive=archive,
                    published=published, version=f"{edition} edition (DTIC's copy, Internet Archive item {archive})",
                    description=description, notice=OSHA_DTIC_NOTICE + TRADE_SAFETY)


def osha_removed(name, title, subject, filename, published, description, language=""):
    """One OSHA publication from the Internet Archive item of publications taken off osha.gov in 2025: the item holds
    many PDFs, so the file is named (pdf) and the item's page is its source (page)."""
    entry = K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=OSHA,
                     pdf=f"https://archive.org/download/{REMOVED}/{urllib.parse.quote(filename)}",
                     page=f"https://archive.org/details/{REMOVED}", published=published,
                     version=f"{published} edition (Internet Archive item {REMOVED}, file {filename})",
                     description=description, notice=OSHA_REMOVED_NOTICE + TRADE_SAFETY)
    if language:
        entry["language"] = language
    return entry


def niosh_pattern(number):
    """The address pattern of a NIOSH publication's own PDF on its page (the page may also link translations, cover
    letters and appendices): "<number>.pdf", optionally with "-508", "revised<date>" or "_2021-revision"."""
    return rf"(?:/|_){re.escape(number)}(?:-508|_?[Rr]evised[0-9]*|_\d{{4}}-revision)?\.pdf$"


def niosh(name, number, title, subject, published, description, pattern=None, language=""):
    """One NIOSH numbered publication: its page on www.cdc.gov is read at every build and its PDF found there
    (niosh_pattern), under CDC's terms (checked at every build)."""
    entry = K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=NIOSH, page=NIOSH_PAGE.format(number),
                     pdf_pattern=pattern or niosh_pattern(number), published=published,
                     version=f"NIOSH publication {number}", description=description,
                     notice=f"{X.CDC_NOTICE} A NIOSH publication, number {number}. {TRADE_SAFETY}",
                     licence_page=X.CDC_TERMS, licence_text=X.CDC_TEXT)
    if language:
        entry["language"] = language
    return entry


def msha(name, title, subject, pattern, published, description):
    """One MSHA training publication, its PDF found on MSHA's instructor materials page at every build."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=MSHA, page=MSHA_PAGE,
                    pdf_pattern=pattern, published=published, version=f"{published} revision (msha.gov)",
                    description=description, notice=MSHA_NOTICE + TRADE_SAFETY)


def doe(name, title, subject, page, pattern, published, description):
    """One Department of Energy technical standard or handbook, its PDF found on its energy.gov page."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=DOE, page=page, pdf_pattern=pattern,
                    published=published, version=f"{published} (energy.gov)", description=description,
                    notice=DOE_NOTICE + TRADE_SAFETY)


def old_trade(name, title, subject, publisher, archive, year, description, notice="", country="United States"):
    """One old public-domain trade book (published before 1931; the builder checks the item's year at every build),
    with the note on what is out of date and the trade safety words."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=OLD_TRADE_NOTE,
                    notice=(notice + " " if notice else "") + TRADE_SAFETY, country=country)


# ====================================================================== construction (trade-construction)

CONSTRUCTION = [
    osha("osha_3100_crane_suspended_platforms", "Crane or Derrick Suspended Personnel Platforms (OSHA 3100, 1993)",
         "Cranes and personnel platforms", "DTIC_ADA400132", "1993",
         "OSHA's guide to hoisting workers on platforms hung from cranes and derricks: when it is allowed, the crane "
         "and the platform, rigging, trial lifts and proof testing, inspections, the pre-lift meeting and safe "
         "work practices.", "OSHA 3100"),
    osha("osha_2202_construction_industry_digest", "Construction Industry Digest (OSHA 2202, 1998)",
         "Construction safety standards", "DTIC_ADA400138", "1998",
         "OSHA's plain summary of the construction standards (29 CFR 1926), topic by topic from access to medical "
         "records to welding: excavations, electrical, fall protection, ladders, scaffolds, cranes, concrete and "
         "masonry, steel erection, demolition, tools, protective equipment, fire protection and more.",
         "OSHA 2202"),
    osha("osha_3106_concrete_masonry", "Concrete and Masonry Construction (OSHA 3106, 1998)",
         "Concrete and masonry safety", "DTIC_ADA400146", "1998",
         "OSHA's guide to the hazards of concrete and masonry work and the rules for them: formwork and shoring, "
         "precast and lift-slab construction, masonry walls and their limited access zone, reinforcing steel, "
         "equipment and tools, and protecting workers.", "OSHA 3106"),
    osha("osha_3096_asbestos_construction", "Asbestos Standard for the Construction Industry (OSHA 3096, 1995)",
         "Asbestos in construction", "DTIC_ADA400234", "1995",
         "OSHA's explanation of the asbestos rules for building work, renovation and demolition: the classes of "
         "asbestos work, exposure limits, regulated areas, work practices, respirators, protective clothing, "
         "hygiene, training and medical surveillance.", "OSHA 3096"),
    osha("osha_100_most_cited_construction_1991", "The 100 Most Frequently Cited OSHA Construction Standards in 1991",
         "Construction safety standards", "DTIC_ADA400334", "1995",
         "OSHA's guide to the construction rules most often broken in 1991 and how to correct each hazard: "
         "scaffolds, fall protection, ladders, excavations, electrical, hazard communication, tools and the "
         "others, each with the standard's words and the fix."),
    osha("osha_3007_ground_fault_protection", "Ground-Fault Protection on Construction Sites (OSHA 3007, 1998)",
         "Electrical safety on site", "DTIC_ADA400339", "1998",
         "OSHA's booklet on protecting workers from electric shock on building sites: ground-fault circuit "
         "interrupters (GFCIs), the assured equipment grounding conductor program, extension cords and tools.",
         "OSHA 3007"),
    osha("osha_2226_excavations", "Excavations (OSHA 2226, 2000)", "Trenching and excavation", "DTIC_ADA400347",
         "2000",
         "OSHA's guide to trench and excavation safety: soil types and how to test them, sloping and benching, "
         "shoring and shields, the competent person, getting in and out, water, hazardous atmospheres and "
         "inspections.", "OSHA 2226"),
    osha_removed("osha_3886_recommended_practices_construction", "Recommended Practices for Safety and Health "
                 "Programs in Construction (OSHA 3886, 2016)", "Construction safety programs",
                 "2016-reccomended-practices-for-safety-and-health-in-construction-OSHA-3886.pdf", "2016",
                 "OSHA's guide to running a safety and health program on construction jobs: management leadership, "
                 "worker participation, finding and fixing hazards, education and training, multi-employer sites "
                 "and checking that the program works."),
    niosh("niosh_2009_113_electrical_trades", "2009-113", "Electrical Safety: Safety and Health for Electrical Trades, "
          "Student Manual (NIOSH 2009-113)", "Electrical safety for the trades", "2009",
          "NIOSH's training course for electrical apprentices and workers: electrical hazards and how electricity "
          "hurts the body, burns and arc flash, overhead power lines, grounding and GFCIs, lockout and tagout, safe "
          "work practices, protective equipment, and case studies of real accidents."),
    niosh("niosh_2007_122_simple_solutions_construction", "2007-122", "Simple Solutions: Ergonomics for "
          "Construction Workers (NIOSH 2007-122)", "Ergonomics in construction", "2007",
          "NIOSH's practical ways to cut strains and sprains on the job: tools and methods for overhead drilling, "
          "lifting and handling heavy materials, tying rebar, working at floor level and finishing drywall and "
          "concrete, each with what it costs and how it helps."),
    niosh("niosh_2011_202_nail_gun_safety", "2011-202", "Nail Gun Safety: A Guide for Construction Contractors "
          "(NIOSH and OSHA, 2011-202)", "Nail guns", "2011",
          "NIOSH and OSHA's guide to nail gun injuries and how to prevent them: how triggers work (full sequential "
          "and contact triggers), the six main risk factors, training, protective equipment and first aid."),
    niosh("niosh_2012_176_engineering_controls_construction", "2012-176", "Engineering Controls in Construction: "
          "Silica, Asphalt and Noise (NIOSH 2012-176)", "Dust and noise controls", "2012",
          "NIOSH's summary of the engineering controls for the commonest health hazards on building sites, such as "
          "water spray and local exhaust for silica dust when cutting and grinding, asphalt paving fume controls and "
          "quieter equipment."),
    niosh("niosh_2022_123_respirators_construction", "2022-123", "Respirator Selection Guide for the Construction "
          "Industry (NIOSH 2022-123)", "Respirators in construction", "2022",
          "NIOSH's guide to choosing respirators for construction tasks: the hazards (silica, lead, asbestos, "
          "welding fume, solvents), the kinds of respirator and their protection factors, fit testing and the "
          "respiratory protection program."),
    niosh("niosh_2002_129_silica", "2002-129", "Health Effects of Occupational Exposure to Respirable Crystalline "
          "Silica (NIOSH Hazard Review 2002-129)", "Silica dust", "2002",
          "NIOSH's review of what breathing silica dust does (silicosis, lung cancer, kidney disease), who is "
          "exposed (sandblasting, cutting stone and concrete, foundries), and how to control it."),
    osha_removed("osha_3384_respiratory_small_entity", "Small Entity Compliance Guide for the Respiratory Protection "
                 "Standard (OSHA 3384, 2011)", "Respirators", "2011-small-entity-compliance-guide-for-the-"
                 "respiratory-protection-standard-OSHA-3384-09.pdf", "2011",
                 "OSHA's step-by-step guide to the respirator standard for small businesses: the written program, "
                 "choosing respirators, medical evaluation, fit testing, use, cleaning and maintenance, air quality "
                 "for supplied-air respirators, training and records."),
    osha_removed("osha_3352_assigned_protection_factors", "Assigned Protection Factors for the Revised Respiratory "
                 "Protection Standard (OSHA 3352, 2009)", "Respirators", "2009-assigned-protection-factors-for-the-"
                 "revised-respiratory-protection-standard-OSHA-3352-02.pdf", "2009",
                 "OSHA's explanation of assigned protection factors (how much protection each class of respirator "
                 "gives) and maximum use concentrations, with the table of factors and worked examples."),
]

# ====================================================================== general industry (trade-industry)

INDUSTRY = [
    osha("osha_3120_lockout_tagout", "Control of Hazardous Energy: Lockout/Tagout (OSHA 3120, 1997)",
         "Lockout and tagout", "DTIC_ADA400137", "1997",
         "OSHA's guide to locking out and tagging out machines before servicing them: hazardous energy, the energy "
         "control program, procedures, lockout and tagout devices, training, periodic inspection, group lockout "
         "and shift changes.", "OSHA 3120"),
    osha("osha_3138_confined_spaces", "Permit-Required Confined Spaces (OSHA 3138, 1998)", "Confined spaces",
         "DTIC_ADA400246", "1998",
         "OSHA's guide to tanks, vaults, pits, silos and other confined spaces: when a permit is needed, testing the "
         "air, ventilation, attendants and entrants, the entry permit, rescue and training.", "OSHA 3138"),
    osha("osha_3080_hand_power_tools", "Hand and Power Tools (OSHA 3080, 1998)", "Hand and power tool safety",
         "DTIC_ADA400353", "1998",
         "OSHA's booklet on the safe use of hand tools and electric, pneumatic, fuel-powered, hydraulic and "
         "powder-actuated tools: guards, switches, abrasive wheels, jacks and protective equipment.", "OSHA 3080"),
    osha("osha_3067_machine_safeguarding", "Concepts and Techniques of Machine Safeguarding (OSHA 3067, 1992)",
         "Machine guarding", "DTIC_ADA400219", "1992",
         "OSHA's manual of machine guarding: where machine hazards are (the point of operation, power transmission, "
         "moving parts), the kinds of guards and devices, feeding and ejection, robots, maintenance and training."),
    osha("osha_amputations_safeguarding", "Safeguarding Equipment and Protecting Workers from Amputations (OSHA, 2001)",
         "Machine guarding", "DTIC_ADA400603", "2001",
         "OSHA's guide to preventing amputations at machines such as presses, saws, conveyors, shears and food "
         "slicers: recognising the hazards, guards and safeguarding devices, lockout and training."),
    osha("osha_3157_woodworking", "A Guide for Protecting Workers from Woodworking Hazards (OSHA 3157, 1999)",
         "Woodworking machines", "DTIC_ADA400640", "1999",
         "OSHA's guide to woodworking machine safety: table, radial-arm, band and other saws, jointers, shapers, "
         "planers and sanders, kickback, wood dust, noise, fire and explosion, with safeguards for each."),
    osha("osha_3077_personal_protective_equipment", "Personal Protective Equipment (OSHA 3077, 1998)",
         "Personal protective equipment", "DTIC_ADA400548", "1998",
         "OSHA's booklet on protective equipment: assessing the hazards, eye and face, head, foot, hand and body "
         "protection, hearing protection, and training workers to use and care for it."),
    osha("osha_3151_ppe_small_business", "Assessing the Need for Personal Protective Equipment: A Guide for Small "
         "Business Employers (OSHA 3151, 2000)", "Personal protective equipment", "DTIC_ADA400241", "2000",
         "OSHA's workbook for small businesses on protective equipment: walking through the workplace to find "
         "hazards, choosing eye, face, head, hand, foot and hearing protection, and training.", "OSHA 3151"),
    osha("osha_3079_respiratory_protection", "Respiratory Protection (OSHA, 1998)", "Respirators",
         "DTIC_ADA400590", "1998",
         "OSHA's booklet on respirators at work: when they are needed, the kinds of respirator, the written "
         "program, medical evaluation, fit testing, use, maintenance and training."),
    osha("osha_3074_hearing_conservation", "Hearing Conservation (OSHA 3074, 1995)", "Noise and hearing",
         "DTIC_ADA400367", "1995",
         "OSHA's booklet on the noise standard: how loud is too loud, monitoring noise, audiometric testing, "
         "hearing protectors, training and records.", "OSHA 3074"),
    osha("osha_3111_hazard_communication", "Hazard Communication Guidelines for Compliance (OSHA 3111, 2000)",
         "Hazard communication", "DTIC_ADA400369", "2000",
         "OSHA's guide to the hazard communication (right-to-know) standard as it stood in 2000: the written "
         "program, labels, material safety data sheets and training (the 2012 standard added the GHS pictograms "
         "and safety data sheets: see 29 CFR 1910.1200 in trade:cfr_29_1910_subpart_z).", "OSHA 3111"),
    osha("osha_3114_hazwoper", "Hazardous Waste Operations and Emergency Response (OSHA 3114, 1997)",
         "HAZWOPER", "DTIC_ADA400370", "1997",
         "OSHA's booklet on the HAZWOPER standard: who it covers (cleanup sites, waste facilities, emergency "
         "responders), the safety and health program, site characterisation, training hours, medical "
         "surveillance, protective equipment, decontamination and emergency response.", "OSHA 3114"),
    osha("osha_3095_asbestos_general_industry", "Asbestos Standard for General Industry (OSHA 3095, 1995)",
         "Asbestos at work", "DTIC_ADA400231", "1995",
         "OSHA's explanation of the asbestos rules outside construction (such as brake and clutch repair): "
         "exposure limits, monitoring, regulated areas, methods of compliance, respirators, hygiene, training "
         "and medical surveillance.", "OSHA 3095"),
    osha("osha_3144_methylene_chloride", "Methylene Chloride (OSHA 3144, 1997)", "Paint strippers and solvents",
         "DTIC_ADA400438", "1997",
         "OSHA's booklet on methylene chloride, the solvent of paint strippers, degreasers and adhesives used in "
         "furniture refinishing and other trades: its health effects, the exposure limits, controls, respirators "
         "and medical surveillance.", "OSHA 3144"),
    osha("osha_3086_rim_wheels", "Servicing Single-Piece and Multi-Piece Rim Wheels (OSHA 3086, 1998)",
         "Tyre and wheel servicing", "DTIC_ADA400357", "1998",
         "OSHA's booklet for truck and heavy equipment tyre servicing: the dangers of rim wheels, restraining "
         "devices (cages), the charts, training and safe operating procedures.", "OSHA 3086"),
    osha("osha_3125_ergonomics", "Ergonomics: The Study of Work (OSHA 3125, 2000)", "Ergonomics",
         "DTIC_ADA400232", "2000",
         "OSHA's introduction to ergonomics: musculoskeletal disorders, the risk factors (force, repetition, "
         "awkward postures, vibration), and how to fit the job to the worker.", "OSHA 3125"),
    osha("osha_3071_job_hazard_analysis", "Job Hazard Analysis (OSHA 3071, 1998)", "Job hazard analysis",
         "DTIC_ADA400421", "1998",
         "OSHA's guide to breaking a job into steps, finding the hazards of each and choosing controls: which jobs "
         "to analyse first, involving workers, the hierarchy of controls and keeping the analysis up to date.",
         "OSHA 3071"),
    osha("osha_2232_longshoring", "Longshoring Industry (OSHA 2232, 2001)", "Longshoring and marine terminals",
         "DTIC_ADA400382", "2001",
         "OSHA's book of the safety and health rules for longshoring and marine terminals: cargo handling gear, "
         "hatches, ladders, vehicles, containers, hazardous cargo, personal protection and first aid, with the "
         "standards' text.", "OSHA 2232"),
    osha("osha_safety_guide_meatpacking_1988", "Safety and Health Guide for the Meatpacking Industry (OSHA, 1988)",
         "Meat cutting and packing", "DTIC_ADA400600", "1988",
         "OSHA's guide for meat cutters and packing plant workers: knives and cuts, machine guarding, slips and "
         "falls, ergonomics and repetitive motion, ammonia refrigeration, noise and sanitation."),
    osha("osha_2209_small_business_handbook", "OSHA Handbook for Small Businesses (OSHA 2209, 1996)",
         "Running a safe small business", "DTIC_ADA400356", "1996",
         "OSHA's handbook for small employers: the law, a safety and health program, self-inspection checklists "
         "for many workplace hazards, record keeping, posters and where to get help.", "OSHA 2209"),
    osha("osha_3021_workers_rights", "OSHA: Employee Workplace Rights (OSHA 3021, 2000)", "Workers' rights",
         "DTIC_ADA400141", "2000",
         "OSHA's booklet on what workers may ask for under the law: information and training, a safe workplace, "
         "filing a complaint, an inspection, protection from retaliation and the right to refuse dangerous work "
         "in some cases.", "OSHA 3021"),
    osha("osha_2056_all_about_osha", "All About OSHA (OSHA 2056, 2000)", "OSHA and the law", "DTIC_ADA400181",
         "2000",
         "OSHA's own guide to the agency: the OSH Act, standards, inspections, citations and penalties, appeals, "
         "state plans, consultation, voluntary programs, training and record keeping.", "OSHA 2056"),
    osha("osha_3000_employer_rights_inspection", "Employer Rights and Responsibilities Following an OSHA Inspection "
         "(OSHA 3000, 1999)", "OSHA inspections", "DTIC_ADA400130", "1999",
         "OSHA's booklet on what happens after an inspection: citations and penalties, the informal conference, "
         "contesting, correcting the hazards and abatement.", "OSHA 3000"),
    osha("osha_3148_workplace_violence_health_care", "Guidelines for Preventing Workplace Violence for Health Care "
         "and Social Service Workers (OSHA 3148, 1998)", "Workplace violence", "DTIC_ADA400388", "1998",
         "OSHA's guidelines for hospitals, clinics, home care and social services: risk factors, management "
         "commitment, worksite analysis, prevention and controls, training and record keeping.", "OSHA 3148"),
    dict(osha("osha_hazardous_waste_site_manual_1985", "Occupational Safety and Health Guidance Manual for Hazardous "
              "Waste Site Activities (NIOSH, OSHA, Coast Guard and EPA, 1985)", "Hazardous waste sites",
              "DTIC_ADA400646", "1985",
              "The four agencies' joint manual for cleanup workers: planning and organisation, training, medical "
              "programs, site characterisation, air monitoring, protective equipment, site control, "
              "decontamination, handling drums and containers, and emergency procedures."),
         publisher="NIOSH, OSHA, US Coast Guard and US Environmental Protection Agency",
         notice="A joint work of four US government agencies (NIOSH, OSHA, the US Coast Guard and the EPA), public "
                "domain (17 U.S.C. 105), from the Defense Technical Information Center's copy on the Internet "
                "Archive. An old edition (1985): the HAZWOPER standard (29 CFR 1910.120) came later; follow the "
                "current rules. " + TRADE_SAFETY),
    osha_removed("osha_3192_grocery_ergonomics", "Guidelines for Retail Grocery Stores: Ergonomics for the "
                 "Prevention of Musculoskeletal Disorders (OSHA 3192, 2004)", "Ergonomics in retail",
                 "2004-guidelines-for-retail-grocery-stores-OSHA-3192-05N.pdf", "2004",
                 "OSHA's ergonomics guidelines for grocery work: checkout, stocking, bakery, deli, meat and produce "
                 "departments, with the problems and solutions for each."),
    osha_removed("osha_3341_shipyard_ergonomics", "Guidelines for Shipyards: Ergonomics for the Prevention of "
                 "Musculoskeletal Disorders (OSHA 3341, 2008)", "Ergonomics in shipyards",
                 "2008-guidelines-for-shipyards-ergonomics-for-the-prevention-of-musculoskeletal-disorders-OSHA-"
                 "3341-03N.pdf", "2008",
                 "OSHA's ergonomics guidelines for shipbuilding and repair: welding, grinding, blasting, painting, "
                 "pipefitting and material handling, with practical solutions."),
    osha_removed("osha_nursing_home_ergonomics", "Guidelines for Nursing Homes: Ergonomics for the Prevention of "
                 "Musculoskeletal Disorders (OSHA, 2003)", "Ergonomics in care work",
                 "2003-ergonomics-for-the-prevention-of-musculoskeletal-disorders-guidelines-for-nursing-homes.pdf",
                 "2003",
                 "OSHA's guidelines for nursing assistants and other care staff: lifting and repositioning residents "
                 "safely, lift equipment, and a program to prevent back and shoulder injuries."),
    osha_removed("osha_4395_workplace_mental_health", "Workplace Mental Health (OSHA 4395, 2024)",
                 "Workplace stress and mental health", "2024-english-workplace-mental-health-OSHA 4395-01.pdf", "2024",
                 "OSHA's short guide to workplace stress and mental health: what workers and employers can do, and "
                 "where to find help, such as the 988 Suicide and Crisis Lifeline."),
    osha_removed("osha_4396_salud_mental_lugar_de_trabajo", "Salud mental en el lugar de trabajo (OSHA 4396, 2024, en "
                 "español)", "Salud mental en el trabajo", "2024-spanish-workplace-mental-health-OSHA 4396-01.pdf",
                 "2024",
                 "OSHA's Spanish guide to workplace stress and mental health (the Spanish edition of OSHA 4395): what "
                 "workers and employers can do and where to find help.", language="spa"),
    niosh("niosh_2005_149_pocket_guide", "2005-149", "NIOSH Pocket Guide to Chemical Hazards (NIOSH 2005-149, third "
          "printing)", "Chemical hazards", "2007",
          "The NIOSH Pocket Guide, the whole book: for each of about 680 chemicals its synonyms and identifiers, "
          "exposure limits (NIOSH, OSHA) and the level immediately dangerous to life or health, physical "
          "properties, incompatibilities, how it enters the body, symptoms, target organs, protective clothing, "
          "first aid and respirator recommendations."),
    niosh("niosh_2007_131_manual_material_handling", "2007-131", "Ergonomic Guidelines for Manual Material Handling "
          "(NIOSH 2007-131)", "Lifting and carrying", "2007",
          "NIOSH's illustrated guide to lifting, carrying, pushing and pulling at work with less strain: ways to "
          "lighten loads, carts, lift tables, hoists and better work layout."),
    niosh("niosh_94_110_lifting_equation", "94-110", "Applications Manual for the Revised NIOSH Lifting Equation "
          "(NIOSH 94-110, 2021 revision)", "Lifting and carrying", "2021",
          "NIOSH's manual for judging lifting jobs: the recommended weight limit, the lifting index, the factors "
          "(distance, height, twisting, frequency and grip) and worked examples."),
    niosh("niosh_2004_164_hand_tools", "2004-164", "Easy Ergonomics: A Guide to Selecting Non-Powered Hand Tools "
          "(NIOSH 2004-164)", "Hand tools", "2004",
          "NIOSH's guide to choosing pliers, screwdrivers, knives, hammers and other hand tools that fit the hand "
          "and the job and cause fewer injuries."),
    niosh("niosh_2001_109_forklifts", "2001-109", "Preventing Injuries and Deaths of Workers Who Operate or Work Near "
          "Forklifts (NIOSH Alert 2001-109)", "Forklifts", "2001",
          "NIOSH's alert on forklift accidents: overturns, workers struck or crushed, falls from forklifts, case "
          "reports, and what employers and operators should do."),
    niosh("niosh_96_110_preventing_hearing_loss", "96-110", "Preventing Occupational Hearing Loss: A Practical Guide "
          "(NIOSH 96-110)", "Noise and hearing", "1996",
          "NIOSH's practical guide to a hearing loss prevention program: noise surveys, engineering and "
          "administrative controls, hearing tests, hearing protectors, training and record keeping."),
    niosh("niosh_98_126_noise_criteria", "98-126", "Criteria for a Recommended Standard: Occupational Noise Exposure "
          "(NIOSH 98-126)", "Noise and hearing", "1998",
          "NIOSH's recommended noise limit (85 dBA over eight hours, with a 3 dB exchange rate) and the science "
          "behind it, with hearing protection, audiometry and hearing loss prevention programs."),
    niosh("niosh_2016_106_heat_criteria", "2016-106", "Criteria for a Recommended Standard: Occupational Exposure to "
          "Heat and Hot Environments (NIOSH 2016-106)", "Heat stress", "2016",
          "NIOSH's recommendations for working in heat: heat illnesses and first aid, acclimatisation, work and "
          "rest schedules, water, medical monitoring, training and protective clothing."),
    niosh("niosh_88_110_welding_criteria", "88-110", "Criteria for a Recommended Standard: Welding, Brazing, and "
          "Thermal Cutting (NIOSH 88-110)", "Welding hazards", "1988", "NIOSH's review of welding, brazing and "
          "cutting hazards: fumes and gases, radiation, noise, fire, electric shock, and controls such as "
          "ventilation, respirators and eye protection.", pattern=r"/88-110\.pdf$"),
    niosh("niosh_87_116_respiratory_protection", "87-116", "A Guide to Industrial Respiratory Protection (NIOSH "
          "87-116)", "Respirators", "1987",
          "NIOSH's classic guide to respirators: the hazards, the kinds of respirator, choosing them, fit testing, "
          "use, maintenance and a respirator program."),
    niosh("niosh_2005_100_respirator_selection_logic", "2005-100", "NIOSH Respirator Selection Logic 2004 (NIOSH "
          "2005-100)", "Respirators", "2004",
          "NIOSH's step-by-step logic for choosing the right respirator class for a chemical or dust, with "
          "assigned protection factors."),
    niosh("niosh_2022_102_proteccion_respiratoria_es", "2022-102", "Protección respiratoria: charla de seguridad "
          "(NIOSH 2022-102, en español)", "Protección respiratoria", "2022",
          "NIOSH's Spanish toolbox talk on respiratory protection: when a respirator is needed, fit, seal checks "
          "and care.", pattern=r"2022-102[^/]*_SP\.pdf$", language="spa"),
    msha("msha_ig_37_part_46_instructors_guide", "30 CFR Part 46 Instructors Guide with Lesson Plans (MSHA IG 37, "
         "revised 2016)", "Training mine workers", r"IG(?:%20|-| )37\.pdf$", "2016",
         "MSHA's guide for training workers at surface sand, gravel, stone and other Part 46 mines: new miner, "
         "newly hired experienced miner, task and annual refresher training, with lesson plans."),
    msha("msha_ig_24a_instructor_workshop_part_48", "Instructor Training Workshop: Part 48 (MSHA IG 24a, revised "
         "2022)", "Training mine workers", r"IG(?:%20|-| )24a\.pdf$", "2022",
         "MSHA's workshop for people who teach miners under Part 48: how adults learn, planning lessons, teaching "
         "methods, training aids, and evaluating training."),
    msha("msha_ig_24b_instructor_workshop_part_46", "Instructor Training Workshop: Part 46 (MSHA IG 24b, revised "
         "2022)", "Training mine workers", r"IG(?:%20|-| )24b\.pdf$", "2022",
         "MSHA's workshop for people who teach miners under Part 46: how adults learn, planning lessons, teaching "
         "methods and evaluating training."),
    msha("msha_ot_56_parts_46_48_reference", "Parts 46 and 48 Reference Guide (MSHA OT 56)", "Training mine workers",
         r"OT(?:%20| )56[^/]*\.pdf$", "2017",
         "MSHA's reference guide to the mine training rules of 30 CFR parts 46 and 48 side by side: who must be "
         "trained, the kinds of training, hours, records and the training plan."),
    doe("doe_hdbk_1092_electrical_safety", "Electrical Safety (DOE-HDBK-1092-2013)", "Electrical safety",
        "https://www.energy.gov/ehss/articles/doe-hdbk-1092-2013", r"DOE-HDBK-1092-2013\.pdf$", "2013",
        "The Department of Energy's electrical safety handbook: the electrical safety program, the hazards of shock, "
        "arc flash and blast, approach boundaries, protective equipment, work on or near energised equipment, "
        "lockout and tagout, grounding, portable tools, research and laboratory equipment, and overhead lines."),
    doe("doe_std_1090_hoisting_rigging", "Hoisting and Rigging (DOE-STD-1090-2020)", "Cranes, hoists and rigging",
        "https://www.energy.gov/ehss/articles/doe-std-1090-2020", r"doe-std-1090-2020\.pdf$", "2020",
        "The Department of Energy's hoisting and rigging standard, used as a training text in many trades: "
        "qualified operators and riggers, critical lifts, inspection and testing of cranes, hoists and forklifts, "
        "wire rope, slings, rigging hardware, below-the-hook lifting devices and hand signals."),
]

# ====================================================================== farm and forest (trade-farm)

FARM = [
    osha("osha_3103_grain_handling", "Grain Handling (OSHA 3103, 1996)", "Grain bins and elevators",
         "DTIC_ADA400349", "1996",
         "OSHA's booklet on grain bins, silos and elevators: engulfment and suffocation, entering bins, lockout of "
         "augers, dust explosions, falls, and the grain handling standard.", "OSHA 3103"),
    niosh("niosh_2001_111_simple_solutions_farm", "2001-111", "Simple Solutions: Ergonomics for Farm Workers (NIOSH "
          "2001-111)", "Ergonomics on the farm", "2001",
          "NIOSH's low-cost ways to cut back and arm injuries in farm work: tools and methods for harvesting, "
          "carrying, nursery and vegetable work, with the cost and benefit of each."),
    niosh("niosh_2010_137_worker_safety_farm", "2010-137", "Worker Safety on the Farm (NIOSH 2010-137)",
          "Farm safety", "2010",
          "NIOSH's farm safety guide: tractors and rollover protection, machinery, animals, chemicals, confined "
          "spaces such as silos and manure pits, heat, noise and young workers."),
    K.us_pdf(GROUP, name="usfs_chain_saw_training_guide_1978", title="Chain Saw Training Guide (US Forest Service, "
             "Wallowa-Whitman National Forest, 1978)", subject="Chain saws and tree felling",
             publisher="US Forest Service (USDA), Wallowa-Whitman National Forest", archive="CAT79725283",
             published="1978", version="1978 edition (the National Agricultural Library's scan, Internet Archive "
                                       "item CAT79725283)",
             description="The Forest Service's chain saw training course of 1978: the saw and its parts, "
                         "maintenance and sharpening, protective clothing, starting and handling, felling, limbing "
                         "and bucking, binds and spring poles, and safety rules.",
             notice="A work of the US Forest Service (public domain, 17 U.S.C. 105), from the National Agricultural "
                    "Library's scan on the Internet Archive, which marks it a historic document whose content may "
                    "not reflect current practice; take a current chain saw course (such as the Forest Service's or "
                    "a state forestry course) before felling trees. " + TRADE_SAFETY),
    old_trade("drew_farm_blacksmithing_1904", "Farm Blacksmithing (James M. Drew, 1904)", "Farm blacksmithing",
              "James M. Drew (Webb Publishing)", "farmblacksmithin00drew", 1904,
              "A textbook for farm boys and agricultural schools: the forge and tools, fire, drawing out, bending, "
              "upsetting and welding iron, making hooks, links and clevises, and simple farm repairs."),
]

# ====================================================================== apprenticeship and careers (trade-apprentice)

APPRENTICE = [
    K.us_pdf(GROUP, name="bls_occupational_outlook_handbook_2012", title="Occupational Outlook Handbook, 2012-13 "
             "Edition (US Bureau of Labor Statistics, Bulletin 2800)", subject="Careers and occupations",
             publisher="US Bureau of Labor Statistics, US Department of Labor (reprinted by Claitor's Publishing "
                       "Division)", archive="isbn_9781598046502", published="2012-04",
             version="2012-13 edition, Bulletin 2800 (Claitor's reprint, Internet Archive item isbn_9781598046502)",
             description="The Bureau of Labor Statistics' guide to hundreds of occupations, the trades among them "
                         "(construction and extraction, installation, maintenance and repair, production, "
                         "transportation, food preparation and personal care): what each worker does, the work "
                         "environment, how to become one (education, training, apprenticeship and licences), pay, "
                         "job outlook and where to learn more. Its pay and outlook figures are those of 2010 to "
                         "2020; the current handbook is at bls.gov/ooh.",
             notice="A work of the US Bureau of Labor Statistics (public domain, 17 U.S.C. 105), read from Claitor's "
                    "Publishing Division's reprint on the Internet Archive (bls.gov refuses programs). Claitor's "
                    "page says \"Material in the text prepared by the U.S. Department of Labor is not copyrighted "
                    "except for format and where modified by Claitor's\": the Bureau's text is made into the "
                    "toolkit's own pages, not Claitor's format."),
    niosh("niosh_2015_161_talking_safety", "2015-161", "Youth@Work: Talking Safety, a curriculum for young workers "
          "(NIOSH 2015-161)", "Safety for young workers", "2015",
          "NIOSH's free course in job safety for teenagers and new workers: finding hazards, making the job safer, "
          "emergencies, workers' rights and responsibilities, and speaking up, with lesson plans and handouts."),
    osha("osha_2254_training_requirements", "Training Requirements in OSHA Standards and Training Guidelines (OSHA "
         "2254, 1998)", "Safety training", "DTIC_ADA400516", "1998",
         "OSHA's list of the training each standard requires, for general industry, construction, maritime and "
         "agriculture, with OSHA's voluntary guidelines for planning, running and evaluating training (useful to "
         "apprentices, trainers and supervisors).", "OSHA 2254"),
]

# ====================================================================== trade texts (trade-texts)

TEXT_GUIDES = [
    wikibook(GROUP, "wikibooks_welding", "Welding", "Welding (Wikibooks)", "Welding",
             "Wikibooks' open book on welding: an overview of the techniques, oxy-fuel welding and cutting, shielded "
             "metal arc (stick) welding, gas tungsten arc (TIG) welding, history and safety.",
             "Welding safety: protect your eyes and skin from the arc, ventilate fumes, keep fire watch, and get "
             "hands-on training. " + TRADE_SAFETY),
]

TEXTS = [
    old_trade("starbuck_standard_practical_plumbing_1910", "Standard Practical Plumbing (R. M. Starbuck, 1910)",
              "Plumbing", "R. M. Starbuck (Norman W. Henley)", "standardpractica00starrich", 1910,
              "An exhaustive treatise of its day on plumbing: tools, wiping joints, soil and waste pipes, traps and "
              "venting, fixtures, water supply, hot-water boilers and tanks, drainage and the plumbing of whole "
              "buildings."),
    old_trade("audel_plumbers_steam_fitters_guide_1925", "Audels Plumbers and Steam Fitters Guide (Frank D. Graham, "
              "1925)", "Plumbing and steam fitting", "Theo. Audel and Company", "gri_33125009689510", 1925,
              "One of the classic Audels trade guides, in questions and answers: plumbing tools and materials, pipe "
              "and fittings, soldering and wiping, drainage and venting, fixtures, water supply, gas fitting, and "
              "steam and hot-water heating."),
    old_trade("king_steam_hot_water_heating_1908", "Practical Steam and Hot Water Heating and Ventilation (Alfred G. "
              "King, 1908)", "Heating and ventilation (HVAC)", "Alfred G. King (Norman W. Henley)",
              "practicalsteam00kingrich", 1908,
              "A practical work of its day on steam and hot-water heating: boilers, radiators, piping systems, "
              "estimating heat loss, vapour and vacuum systems, fittings and valves, ventilation, and installing "
              "and running a plant."),
    old_trade("hodgson_cyclopedia_bricklaying_1920", "Cyclopedia of Bricklaying, Stone Masonry, Concretes, Stuccos "
              "and Plasters (Fred T. Hodgson, 1920)", "Bricklaying and masonry", "Fred T. Hodgson (Frederick J. "
              "Drake)", "CyclopediaOfBricklayingStoneMasonryConcretesStuccosAndPlasters", 1920,
              "A practical cyclopedia for bricklayers, stone masons and plasterers: bonds and walls, arches, "
              "chimneys and fireplaces, stone cutting and setting, concrete, stucco and plaster work."),
    old_trade("purchase_practical_masonry_1904", "Practical Masonry (William R. Purchase, 1904)", "Stone masonry",
              "William R. Purchase (Crosby Lockwood)", "practicalmasonry00purciala", 1904,
              "A guide to the art of stone cutting: setting out, geometry for masons, arches, vaults, stairs, "
              "domes, and the stonemason's tools and methods.", country="United Kingdom"),
    old_trade("hasluck_cassells_carpentry_joinery_1907", "Cassell's Carpentry and Joinery (Paul N. Hasluck, 1907)",
              "Carpentry and joinery", "Paul N. Hasluck (Cassell and Company)", "cassellscarpentr00hasl", 1907,
              "A big illustrated handbook of carpentry and joinery: timber, tools, joints, floors, roofs, partitions, "
              "doors, windows, stairs, panelling and shop fittings.", country="United Kingdom"),
    old_trade("ics_building_trades_pocketbook_1905", "The Building Trades Pocketbook (International Correspondence "
              "Schools, 1905)", "Building trades reference", "International Correspondence Schools (Scranton)",
              "buildingtradespo00inteuoft", 1905,
              "The ICS's pocket reference for the building trades: arithmetic and geometry for builders, strength of "
              "materials, masonry, carpentry, roofing, plumbing, heating, estimating and tables."),
    old_trade("ics_concrete_engineers_handbook_1912", "The Concrete Engineer's Handbook (International "
              "Correspondence Schools, 1912)", "Concrete work", "International Correspondence Schools (Scranton)",
              "concreteengineer00inteuoft", 1912,
              "The ICS's handbook for concrete work: cement and aggregates, proportioning and mixing, forms, placing "
              "and finishing, reinforcement, and tables."),
    old_trade("broemel_sheet_metal_workers_manual_1918", "Sheet Metal Workers' Manual (L. Broemel, 1918)",
              "Sheet metal work", "L. Broemel (Frederick J. Drake)", "sheetmetalworker00broe", 1918,
              "A complete instruction book of its day for the sheet metal trade: tools and machines, pattern "
              "drafting, soldering, riveting, cornice, roofing and ductwork, and oxy-acetylene welding."),
    old_trade("miller_oxy_acetylene_welding_1916", "Oxy-Acetylene Welding (S. W. Miller, 1916)", "Welding (gas)",
              "Samuel Wylie Miller (Industrial Press)", "oxyacetyleneweld00millrich", 1916,
              "A comprehensive treatise of its day on gas welding: oxygen and acetylene, torches and regulators, "
              "preparing the work, and welding cast iron, malleable iron, steel, copper, brass, bronze and aluminium "
              "by the oxy-acetylene method."),
    old_trade("lincoln_electric_arc_welding_1918", "Electric Arc Welding (Lincoln Electric Company, 1918)",
              "Welding (arc)", "The Lincoln Electric Company", "electricarcweldi00linc", 1918,
              "Lincoln Electric's early booklet on arc welding: the welding arc, equipment, electrodes, preparing "
              "joints and welding methods for repair and manufacturing work.", notice=ELECTRICAL_NOTE),
    old_trade("croft_american_electricians_handbook_1913", "American Electricians' Handbook (Terrell Croft, 1913)",
              "Electrical work", "Terrell Croft (McGraw-Hill)", "americanelectri00crofgoog", 1913,
              "The first edition of the electrician's classic handbook: electrical principles, conductors, wiring "
              "methods, motors and generators, transformers, lighting, batteries and tables for the practical "
              "electrician.", notice=ELECTRICAL_NOTE),
    old_trade("rose_modern_machine_shop_practice_1901", "Modern Machine-Shop Practice, Volume 1 (Joshua Rose, 1901)",
              "Machine shop", "Joshua Rose (Charles Scribner's Sons)", "modernmachinesho01roseuoft", 1901,
              "A large illustrated treatise on the machinist's trade of its day: lathes, cutting tools, boring, "
              "planing, shaping, milling, gear cutting, measuring, filing and fitting."),
    old_trade("richardson_practical_blacksmithing_1889", "Practical Blacksmithing, Volume 1 (M. T. Richardson, editor, "
              "1889)", "Blacksmithing", "M. T. Richardson (editor)", "practicalblacksm01richuoft", 1889,
              "A collection of articles by working smiths: the history of the trade, forges and chimneys, anvils, "
              "tongs and other tools, and many shop methods."),
    old_trade("page_automobile_repairing_made_easy_1918", "Automobile Repairing Made Easy (Victor W. Pagé, 1918)",
              "Auto repair", "Victor W. Pagé (Norman W. Henley)", "automobilerepai00paggoog", 1918,
              "A complete treatise of its day on repairing cars: the shop and its tools, engines, carburettors, "
              "ignition, transmissions, axles, brakes, tyres and bodies, with methods of finding and fixing faults."),
    old_trade("moler_manual_on_barbering_1906", "The Manual on Barbering, Hairdressing, Manicuring, Facial Massage "
              "(A. B. Moler, 1906)", "Barbering and hairdressing", "A. B. Moler (Moler System of Colleges)",
              "manualonbarberin01mole", 1906,
              "A textbook of the Moler barber colleges: shaving, hair cutting, hairdressing, manicuring, facial "
              "massage, shampooing, the care of tools and sanitation as it was taught then (today's licensing "
              "rules and sanitation standards differ)."),
]


# ====================================================================== the OSHA standards (29 CFR), makers

CFR_FIELDS = dict(group=GROUP, country="United States", licence=K.US_GOV, licence_url=K.US_GOV_URL,
                  licence_page=K.GOVINFO_POLICY, licence_text=K.GOVINFO_TEXT,
                  publisher="Office of the Federal Register (Code of Federal Regulations, annual edition from "
                            "govinfo.gov)", split=r'<h3 class="cfr-section"', unit=r'<h2 class="cfr-subpart"')
CFR_NOTICE = ("A US government work (public domain), from govinfo.gov's annual edition of the Code of Federal "
              "Regulations; not an official version. States with their own OSHA-approved plans may have stricter "
              "rules. ")
CFR_URL = "https://www.govinfo.gov/content/pkg/CFR-{y}-title29-vol{v}/xml/CFR-{y}-title29-vol{v}-part{p}.xml"

CFR_BOOKS = {
    "cfr_29_1926_construction": dict(
        CFR_FIELDS, name="trade_cfr_29_1926_construction", title="Safety and Health Regulations for Construction (29 "
        "CFR part 1926, the OSHA construction standards)", subject="OSHA construction standards",
        part=1926, volume=8, first="1926.1", source="https://www.ecfr.gov/current/title-29/part-1926",
        description="The OSHA construction standards in full, subpart by subpart: general safety and health, "
                    "protective equipment, fire protection, signs, materials handling, tools, welding and cutting, "
                    "electrical, scaffolds, fall protection, cranes and hoists, motor vehicles and equipment, "
                    "excavations, concrete and masonry, steel erection, demolition, blasting (as law), stairways and "
                    "ladders, confined spaces, toxic substances such as silica, lead and asbestos, and the rest.",
        notice=CFR_NOTICE + TRADE_SAFETY),
    "cfr_29_1910_general_industry": dict(
        CFR_FIELDS, name="trade_cfr_29_1910_general_industry", title="Occupational Safety and Health Standards: "
        "General Industry (29 CFR part 1910, sections 1910.1 to 1910.999)", subject="OSHA general industry standards",
        part=1910, volume=5, first="1910.1", source="https://www.ecfr.gov/current/title-29/part-1910",
        description="The OSHA general industry standards from the start of part 1910 to Subpart S: walking and "
                    "working surfaces and fall protection, exits and emergency plans, ventilation, noise, radiation, "
                    "hazardous materials, protective equipment, sanitation, confined spaces, lockout and tagout, "
                    "medical and first aid, fire protection, compressed gas, materials handling and forklifts, "
                    "machinery and machine guarding, hand and portable power tools, welding, cutting and brazing, "
                    "special industries (such as sawmills, logging, telecommunications and electric power), and "
                    "electrical. Subpart Z (toxic substances and hazard communication) is its own book.",
        notice=CFR_NOTICE + TRADE_SAFETY),
    "cfr_29_1910_subpart_z": dict(
        CFR_FIELDS, name="trade_cfr_29_1910_subpart_z", title="Toxic and Hazardous Substances and Hazard "
        "Communication (29 CFR part 1910, Subpart Z, from section 1910.1000)", subject="OSHA toxic substances",
        part=1910, volume=6, first="1910.1000", source="https://www.ecfr.gov/current/title-29/part-1910/subpart-Z",
        description="The second half of the general industry standards, Subpart Z: the exposure limit tables (Z-1, "
                    "Z-2 and Z-3), and the standards for asbestos, lead, silica, benzene, cadmium, chromium, "
                    "formaldehyde, methylene chloride, bloodborne pathogens and other substances, Hazard "
                    "Communication (1910.1200: labels, pictograms and safety data sheets) and laboratories.",
        notice=CFR_NOTICE + TRADE_SAFETY),
    "cfr_29_1928_agriculture": dict(
        CFR_FIELDS, name="trade_cfr_29_1928_agriculture", title="Occupational Safety and Health Standards for "
        "Agriculture (29 CFR part 1928)", subject="OSHA agriculture standards",
        part=1928, volume=8, first="1928.1", source="https://www.ecfr.gov/current/title-29/part-1928",
        description="The OSHA standards for farm work: roll-over protective structures for tractors and their "
                    "seat belts, guarding of farm field equipment, farmstead equipment and cotton gins, and field "
                    "sanitation (drinking water, toilets and hand washing for farm workers).",
        notice=CFR_NOTICE + TRADE_SAFETY),
}


def first_section(xml_text):
    """The number of the first section in a CFR volume's XML ("1910.1000"), "" when it has none."""
    m = re.search(r"<SECTNO>\s*(?:§+\s*)?([0-9]+\.[0-9]+)", xml_text)
    return m.group(1) if m else ""


def cfr_edition(spec, cache=None, today=None):
    """(address, XML text) of govinfo's newest annual edition of one CFR part in one volume, checked to start with
    the expected section (spec["first"]): govinfo publishes the volumes of a year at different times, so an edition
    is used only when it is the right volume (build_textbooks.govinfo_edition would take the neighbouring volume of
    a newer year). Raises LookupError when none of this year's and the four years before is found."""
    import build_textbooks as B
    year = (today or datetime.date.today()).year
    for y in range(year, year - 5, -1):
        url = CFR_URL.format(y=y, v=spec["volume"], p=spec["part"])
        try:
            text = B.fetch(url, cache)
        except urllib.error.HTTPError as e:
            if e.code not in (403, 404, 410):
                raise
            continue
        if "<CFRGRANULE" in text and first_section(text) == spec["first"]:
            return url, text
    raise LookupError(f"no edition of 29 CFR {spec['part']} (volume {spec['volume']}) found")


def cfr_maker(spec):
    """(make, sign) of one book of the OSHA standards (see CFR_BOOKS): the licence line is checked on govinfo's
    policy page at every build, then the newest right edition is read (cfr_edition) and cut into one page per
    section (build_textbooks.law_pages), with the subparts as its parts."""

    def make(name, work, cache=None, left_out=None, limit=None):
        """The book of the standards, or None (the reason in left_out)."""
        import build_textbooks as B
        left_out = left_out if left_out is not None else []
        page = spec["licence_page"]
        if not B.allowed_by_robots(page, cache):
            left_out.append({"title": spec["title"], "reason": f"The site's robots.txt does not allow reading {page}."})
            return None
        words = " ".join(B.html.unescape(re.sub(r"<[^>]+>", " ", B.fetch(page, cache))).split())
        if not re.search(spec["licence_text"], words):
            left_out.append({"title": spec["title"], "reason": f"Its licence page ({page}) no longer states the "
                             "licence that was checked."})
            return None
        try:
            url, text = cfr_edition(spec, cache)
        except LookupError as e:
            left_out.append({"title": spec["title"], "reason": f"govinfo.gov has {e}."})
            return None
        m = re.search(r"<DATE>([0-9-]+)</DATE>", text)
        book = K.new_book(spec["name"], spec["title"], spec["subject"], GROUP, spec["publisher"], spec["licence"],
                          spec["licence_url"], spec["source"], spec["description"], spec["notice"],
                          published=m.group(1) if m else "",
                          changes="made into web pages, one per section, with the subparts as parts; not an official "
                                  "version")
        book.originals = [{"url": url}]
        paths = set()
        for unit, page_title, body in B.law_pages(B.cfr_xml_html(text), spec, url):
            path = B.slug(page_title, 50)
            while path in paths or path in ("index", "style-css"):
                path += "-2"
            paths.add(path)
            book.pages.append(B.Page(path, page_title, body, 0, unit))
            if limit and len(book.pages) >= limit:
                break
        book.version = f"govinfo.gov annual edition read from {url}"
        return book

    def sign(name):
        """The weekly sign of change: the address of the newest right edition (its year is in it)."""
        return K.sha(cfr_edition(spec)[0])

    return make, sign


# ====================================================================== NIOSH shelves (several short publications)

SHELVES = {
    "niosh_construction_toolbox_talks": dict(
        title="NIOSH Construction Toolbox Talks (NIOSH, 2022 to 2026)", subject="Toolbox talks for construction",
        description="NIOSH's short toolbox talks for the start of a shift on a building site, each a true story, "
                    "the hazard and questions for the crew: aerial lifts, electrical safety and arc welding, "
                    "biohazards, carbon monoxide, repetitive motion, cold, crane stability, falling objects, "
                    "equipment maintenance, eye protection, welding fires, roofing asphalt fumes, buried utilities, "
                    "drywall handling, power, wiring and extension cords, getting on and off equipment, holes and "
                    "guardrails, forklifts, boom trucks, confined spaces, overhead power lines, scaffolds, skid steer "
                    "loaders, fire safety, noise, lifting and carrying, and lockout, tagout and tryout.",
        parts=[("2022-127", "Aerial lifts"), ("2022-128", "Electrical safety and arc welding"),
               ("2022-129", "Biohazards"), ("2022-130", "Carbon monoxide poisoning"),
               ("2022-131", "Repetitive motion: carpal tunnel syndrome"), ("2022-132", "Cold environments"),
               ("2022-133", "Crane safety: stability and tipping"), ("2022-134", "Preventing falling objects"),
               ("2022-135", "Equipment safety: maintenance"), ("2022-136", "Eye protection"),
               ("2022-137", "Arc welding and fire safety"), ("2022-138", "Asphalt fumes: roofing"),
               ("2022-139", "Buried utilities"), ("2022-140", "Materials handling: drywall"),
               ("2022-141", "Electrical safety: power"), ("2022-142", "Electrical safety: wiring"),
               ("2022-143", "Electrical safety: extension cords"), ("2022-144", "Getting on and off equipment"),
               ("2022-145", "Preventing falls through holes"), ("2022-146", "Preventing falls: guardrails"),
               ("2022-147", "Equipment safety: forklifts"), ("2026-108", "Boom trucks"),
               ("2026-109", "Confined spaces"), ("2026-110", "Overhead power lines"), ("2026-111", "Scaffolds"),
               ("2026-112", "Skid steer loaders"), ("2026-117", "Fire safety"),
               ("2026-118", "Noise and hearing protection"), ("2026-119", "Lifting and carrying"),
               ("2026-120", "Lockout, tagout and tryout")]),
    "niosh_construction_hazards": dict(
        title="Construction Hazards: NIOSH Guides for Workers and Employers", subject="Construction safety",
        description="NIOSH's guides to the deadliest and commonest hazards of building work: falls from roofs, "
                    "ladders and scaffolds, translucent roof panels, trench cave-ins, backing vehicles and dump "
                    "trucks, excavator quick couplers, skid-steer loaders, forklifts, drywall installation, concrete "
                    "grinding dust, silica and cement roof tiles, roofing asphalt fumes, taking lead home, and a "
                    "pamphlet on construction workers' safety and health.",
        parts=[("2019-128", "Preventing falls from roofs, ladders and scaffolds"),
               ("2012-142", "Construction falls prevention fact sheet"),
               ("2016-110", "Translucent corrugated roof panels"), ("2011-208", "Trench cave-ins"),
               ("2014-125", "Backing construction vehicles and equipment"), ("2023-137", "Dump trucks"),
               ("2024-102", "Excavator quick coupler attachments"), ("2011-128", "Skid-steer loaders"),
               ("2006-147", "Installing drywall"), ("2009-115", "Dust when grinding concrete"),
               ("2004-108", "Silicosis: learn the facts"), ("2006-110", "Cement roofing tiles and silica"),
               ("2003-112", "Asphalt fumes in roofing"), ("2024-101", "Leave lead at work"),
               ("2023-115", "Safety and health at work: construction workers")]),
    "niosh_heat_stress": dict(
        title="Heat Stress at Work: NIOSH Fact Sheets and Guides", subject="Heat stress",
        description="NIOSH's and OSHA's short guides to working in the heat: protecting yourself, heat illness, "
                    "outdoor workers, acclimatisation, risk factors, drinking water, work schedules, first aid for "
                    "heat illness and an overview of heat stress.",
        parts=[("2010-114", "Protecting yourself from heat stress"), ("2011-174", "Protecting workers from heat "
               "illness (OSHA and NIOSH)"), ("2013-143", "Outdoor workers"), ("2016-151", "Preventing heat-related "
               "illness"), ("2017-123", "Overview"), ("2017-124", "Acclimatization"), ("2017-125", "Risk factors"),
               ("2017-126", "Hydration"), ("2017-127", "Work schedules"), ("2018-116", "Risk factors, prevention "
               "and treatment"), ("2024-100", "First aid for heat illness")]),
    "niosh_hearing": dict(
        title="Hearing Loss at Work: NIOSH Guides", subject="Noise and hearing",
        description="NIOSH's guides to preventing hearing loss on the job: protecting your ears, farm noise, buying "
                    "quiet tools and machines, hearing loss from chemicals and noise together, and fit-testing "
                    "hearing protectors.",
        parts=[("2007-175", "They're your ears: protect them"), ("2007-176", "Farm noise"),
               ("2014-128", "Hearing loss is preventable"), ("2014-129", "Buy quiet"),
               ("2018-124", "Hearing loss from chemicals and noise"), ("2025-104", "Fit-testing hearing "
               "protectors")]),
    "niosh_respirators": dict(
        title="Respirators at Work: NIOSH Guides", subject="Respirators",
        description="NIOSH's guides to respirators: air-purifying and atmosphere-supplying respirators, questions "
                    "and answers on reuse, fit testing and seal checks, putting on and taking off a disposable "
                    "respirator, a respiratory protection toolbox talk, escape hoods and gas masks, shelf life and "
                    "counterfeit respirators.",
        parts=[("2018-176", "Air-purifying respirators"), ("2019-174", "Atmosphere-supplying respirators"),
               ("2018-128", "Reuse and extended use"), ("2018-129", "Fit testing"), ("2018-130", "User seal check"),
               ("2010-131", "Putting on and taking off a disposable respirator"), ("2022-102", "Respiratory "
               "protection toolbox talk"), ("2003-144", "Escape hoods, gas masks and other respirators"),
               ("2023-128", "Shelf life of filtering facepiece respirators"), ("2025-105", "Counterfeit "
               "respirators")]),
    "niosh_farm_safety": dict(
        title="Farm and Grounds Work: NIOSH Guides", subject="Farm safety",
        description="NIOSH's guides for farm and grounds workers: fires and explosions in oxygen-limiting silos, "
                    "all-terrain vehicles at work, and fatal injuries among landscape services workers.",
        parts=[("2026-114", "Fires and explosions in oxygen-limiting silos"), ("2012-167", "ATV safety at work"),
               ("2008-144", "Landscape services workers")]),
    "niosh_young_workers": dict(
        title="Young Workers: NIOSH Guides", subject="Safety for young workers",
        description="NIOSH's guides for teenagers starting work and their employers and parents: are you a teen "
                    "worker, and keeping young drivers safe on the job.",
        parts=[("2012-130", "Are you a teen worker?"), ("2017-207", "Young drivers in the workplace"),
               ("2013-153", "Young drivers: what employers should know")]),
    "niosh_trade_chemicals": dict(
        title="Chemicals in the Trades: NIOSH Guides", subject="Chemical hazards in the trades",
        description="NIOSH's guides to chemical hazards in particular trades: artificial fingernails in nail "
                    "salons, cleaning chemicals for custodians and housekeepers, skin contact with chemicals, "
                    "spray-on truck bed liners (isocyanates) in auto shops, and respirators for chimney sweeps.",
        parts=[("99-112", "Artificial fingernails (nail salons)"), ("2012-125", "Cleaning chemicals and your health"),
               ("2012-126", "Protecting workers who use cleaning chemicals"), ("2011-200", "Skin contact with "
               "chemicals"), ("2006-149", "Spray-on truck bed liners"), ("2024-122", "Chimney sweeps")]),
    "niosh_drivers_vehicles": dict(
        title="Drivers and Vehicles at Work: NIOSH Guides", subject="Work driving and powered trucks",
        description="NIOSH's guides for people who drive or run vehicles at work: preventing work-related crashes, "
                    "sleep tips for truck drivers, and the daily inspection of forklifts and other powered "
                    "industrial trucks.",
        parts=[("2015-111", "Preventing work-related motor vehicle crashes"), ("2014-150", "Sleep tips for truck "
               "drivers"), ("2022-100", "Daily inspection of powered industrial trucks")]),
}


def shelf_entry(name, shelf):
    """The pdf_set entry of one NIOSH shelf (its licence checked on CDC's terms page for every part)."""
    numbers = ", ".join(n for n, _part in shelf["parts"])
    return K.us_pdf(GROUP, name=f"trade_{name}", title=shelf["title"], subject=shelf["subject"], publisher=NIOSH,
                    source=NIOSH_PAGE.format(shelf["parts"][0][0]), description=shelf["description"],
                    notice=f"{X.CDC_NOTICE} NIOSH publications {numbers}, one after another. {TRADE_SAFETY}",
                    licence_page=X.CDC_TERMS, licence_text=X.CDC_TEXT, published="")


def shelf_parts(shelf, cache=None, left_out=None):
    """[(part title, PDF address, page address)] of a shelf: each publication's page is read and its own PDF found
    (niosh_pattern); a page that cannot be read or links no PDF is left out (said in left_out)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    parts = []
    for number, part in shelf["parts"]:
        page = NIOSH_PAGE.format(number)
        try:
            if not B.allowed_by_robots(page, cache):
                left_out.append({"title": f"NIOSH {number}", "reason": "The site's robots.txt does not allow it."})
                continue
            pdf = B.newest_pdf(B.fetch(page, cache), page, niosh_pattern(number))
        except (urllib.error.URLError, OSError, ValueError) as e:
            left_out.append({"title": f"NIOSH {number}", "reason": f"Its page could not be read ({e})."})
            continue
        if not pdf:
            left_out.append({"title": f"NIOSH {number}", "reason": "Its page links no PDF of it."})
            continue
        parts.append((f"{part} (NIOSH {number})", pdf, page))
    return parts


def shelf_maker(name, shelf):
    """(make, sign) of one NIOSH shelf: one book of several short NIOSH publications (pdf_set.pdf_set_book)."""

    def make(key_name, work, cache=None, left_out=None, limit=None):
        """The shelf's book, or None when no part could be read (each reason in left_out)."""
        import pdf_set
        left_out = left_out if left_out is not None else []
        parts = shelf_parts(shelf, cache, left_out)
        if not parts:
            left_out.append({"title": shelf["title"], "reason": "No publication of the shelf could be found."})
            return None
        book = pdf_set.pdf_set_book(shelf_entry(name, shelf), parts, work, cache, left_out, limit)
        if book is not None:
            book.version = f"{len(parts)} NIOSH publications read {datetime.date.today().isoformat()}"
        return book

    def sign(key_name):
        """The weekly sign: the addresses of the shelf's PDFs (a new edition gets a new address or date)."""
        return K.sha([p[1] for p in shelf_parts(shelf)])

    return make, sign


# ====================================================================== the index of trades (trade:index)

SECTIONS = [
    ("How to use this guide", "Each part below is one trade or a safety subject: the books to read, by key (ask for "
     "a key or a request word with the Program Downloader), the manual collections, picture packs and links. Start "
     "with the safety books for your trade and the OSHA standard that covers it (construction: 29 CFR 1926; "
     "factories, shops and most other work: 29 CFR 1910; farms: 29 CFR 1928). The trades books are listed under the "
     "request words trade-construction, trade-industry, trade-farm, trade-apprentice and trade-texts (all of them: "
     "trades).", [
        ("key", "trade:cfr_29_1926_construction", "The OSHA construction standards (29 CFR 1926)"),
        ("key", "trade:cfr_29_1910_general_industry", "The OSHA general industry standards (29 CFR 1910)"),
        ("key", "trade:cfr_29_1910_subpart_z", "Toxic substances and hazard communication (29 CFR 1910 Subpart Z)"),
        ("key", "trade:cfr_29_1928_agriculture", "The OSHA agriculture standards (29 CFR 1928)"),
        ("key", "trade:osha_2056_all_about_osha", "All About OSHA: the law, inspections and your rights"),
        ("key", "trade:osha_3021_workers_rights", "Workers' rights under OSHA"),
        ("key", "mw:nlrb_employee_rights", "Employee rights at work (National Labor Relations Board)"),
        ("key", "mw:dol_whd_fact_sheets", "Wage and hour fact sheets (Department of Labor)"),
        ("link", "OSHA (current standards, publications and the OSHA 10 and 30 hour courses)", "https://www.osha.gov/",
         "osha.gov refuses programs; open it in a browser")]),
    ("Becoming an apprentice: careers, training and pay", "What each trade does, how to train (apprenticeship, "
     "trade school, Job Corps), pay and outlook.", [
        ("key", "trade:bls_occupational_outlook_handbook_2012", "Occupational Outlook Handbook, 2012-13 (every "
         "occupation: duties, training, pay, outlook)"),
        ("key", "mw:onet_occupations", "O*NET occupations: tasks, skills and tools of each job"),
        ("key", "edu:apprenticeship_gov", "Apprenticeship.gov: what registered apprenticeship is and finding one"),
        ("key", "edu:job_corps", "Job Corps: free career training for ages 16 to 24"),
        ("key", "trade:osha_2254_training_requirements", "The training each OSHA standard requires"),
        ("key", "trade:niosh_2015_161_talking_safety", "Talking Safety: a job safety course for young workers"),
        ("key", "trade:niosh_young_workers", "Young workers and young drivers (NIOSH)"),
        ("link", "Occupational Outlook Handbook (current edition)", "https://www.bls.gov/ooh/",
         "bls.gov refuses programs; open it in a browser"),
        ("link", "Apprenticeship occupations and work process schedules", "https://www.apprenticeship.gov/"
         "apprenticeship-occupations", "a JavaScript search; open it in a browser")]),
    ("Carpentry and woodworking", "Framing, finish carpentry, cabinet and joinery work, and woodworking machines.", [
        ("key", "build:army_fm_5_426_carpentry", "Carpentry (Army FM 5-426)"),
        ("key", "build:navy_builder_3_2_1981", "Builder 3 and 2 (Navy Seabee course)"),
        ("key", "build:wikibooks_carpentry", "Carpentry (Wikibooks)"),
        ("key", "build:wikibooks_woodworking", "Woodworking (Wikibooks)"),
        ("key", "build:fpl_wood_handbook", "Wood Handbook (Forest Products Laboratory)"),
        ("key", "build:navy_blueprint_reading", "Blueprint Reading and Sketching (Navy)"),
        ("key", "trade:hasluck_cassells_carpentry_joinery_1907", "Cassell's Carpentry and Joinery (1907)"),
        ("key", "trade:osha_3157_woodworking", "Woodworking machine hazards (OSHA)"),
        ("key", "trade:niosh_2011_202_nail_gun_safety", "Nail gun safety (NIOSH and OSHA)"),
        ("manuals", "woodshop_machines", "Saw, jointer, planer and router makers' manuals"),
        ("manuals", "trade_tools", "Trade tool makers' manuals")]),
    ("Electrical", "Electricians and electrical apprentices: electrical theory, wiring and electrical safety. Mains "
     "work needs a licence in most places.", [
        ("key", "trade:niosh_2009_113_electrical_trades", "Electrical Safety for the Electrical Trades: student "
         "manual (NIOSH)"),
        ("key", "trade:doe_hdbk_1092_electrical_safety", "Electrical Safety handbook (DOE-HDBK-1092)"),
        ("key", "power:osha_controlling_electrical_hazards_1997", "Controlling Electrical Hazards (OSHA 3075)"),
        ("key", "trade:osha_3007_ground_fault_protection", "Ground-fault protection on construction sites (OSHA)"),
        ("key", "power:army_fm_5_424_electrical_systems_1997", "Theater of Operations Electrical Systems (Army FM "
         "5-424)"),
        ("key", "elec:kuphaldt_liec_ac", "Lessons in Electric Circuits: AC (Kuphaldt)"),
        ("key", "elec:kuphaldt_liec_dc", "Lessons in Electric Circuits: DC (Kuphaldt)"),
        ("key", "trade:croft_american_electricians_handbook_1913", "American Electricians' Handbook (1913, history)"),
        ("word", "electronics", "The electronics books (request word)"),
        ("manuals", "electrical_devices", "Switch, outlet and breaker makers' manuals"),
        ("manuals", "home_electrical", "Home electrical makers' manuals"),
        ("link", "National Electrical Code (NFPA 70), free to read online", "https://www.nfpa.org/codes-and-standards/"
         "nfpa-70-standard-development/70", "copyright of the NFPA; read free online after signing up")]),
    ("Plumbing and pipefitting", "Water supply, drainage, venting, fixtures, gas and steam piping.", [
        ("key", "trade:starbuck_standard_practical_plumbing_1910", "Standard Practical Plumbing (1910)"),
        ("key", "trade:audel_plumbers_steam_fitters_guide_1925", "Audels Plumbers and Steam Fitters Guide (1925)"),
        ("key", "craft:epa_fix_a_leak", "Fixing leaks (EPA WaterSense)"),
        ("key", "trade:cfr_29_1926_construction", "Trenching, confined spaces and other rules for pipe work (29 CFR "
         "1926)"),
        ("manuals", "plumbing_fittings", "Plumbing fixture and fitting makers' manuals"),
        ("link", "Uniform Plumbing Code (IAPMO), free to read online", "https://epubs.iapmo.org/",
         "copyright of IAPMO; read free online")]),
    ("Heating, ventilation and air conditioning (HVAC)", "Boilers, furnaces, ductwork, refrigeration and "
     "ventilation.", [
        ("key", "trade:king_steam_hot_water_heating_1908", "Practical Steam and Hot Water Heating and Ventilation "
         "(1908)"),
        ("key", "trade:broemel_sheet_metal_workers_manual_1918", "Sheet Metal Workers' Manual: ductwork (1918)"),
        ("key", "craft:usfa_home_heating_fire_safety", "Home heating fire safety (US Fire Administration)"),
        ("manuals", "home_heating", "Furnace, boiler and heater makers' manuals"),
        ("link", "EPA Section 608 refrigerant technician certification", "https://www.epa.gov/section608",
         "the certification rules for technicians who handle refrigerants; open it in a browser")]),
    ("Welding and metal work", "Arc, gas and other welding, cutting, sheet metal, machining and blacksmithing.", [
        ("key", "trade:wikibooks_welding", "Welding (Wikibooks)"),
        ("key", "trade:niosh_88_110_welding_criteria", "Welding, brazing and thermal cutting hazards (NIOSH)"),
        ("key", "trade:osha_3341_shipyard_ergonomics", "Shipyard work: welding, grinding and fitting (OSHA)"),
        ("key", "trade:miller_oxy_acetylene_welding_1916", "Oxy-Acetylene Welding (1916)"),
        ("key", "trade:lincoln_electric_arc_welding_1918", "Electric Arc Welding (Lincoln Electric, 1918)"),
        ("key", "trade:broemel_sheet_metal_workers_manual_1918", "Sheet Metal Workers' Manual (1918)"),
        ("key", "trade:rose_modern_machine_shop_practice_1901", "Modern Machine-Shop Practice (1901)"),
        ("key", "trade:richardson_practical_blacksmithing_1889", "Practical Blacksmithing (1889)"),
        ("key", "make:army_tc_9_524_machine_tools", "Fundamentals of Machine Tools (Army TC 9-524)"),
        ("word", "making", "Machining, CNC and 3D printing books (request word)"),
        ("manuals", "metal_shop_welding", "Welder and metal shop makers' manuals"),
        ("manuals", "welding_gases", "Welding gas safety data")]),
    ("Masonry, concrete and plastering", "Brick, block and stone, concrete forming and finishing, plaster and stucco.",
     [
        ("key", "build:army_fm_5_428_concrete_masonry", "Concrete and Masonry (Army FM 5-428)"),
        ("key", "trade:osha_3106_concrete_masonry", "Concrete and masonry construction safety (OSHA)"),
        ("key", "trade:hodgson_cyclopedia_bricklaying_1920", "Cyclopedia of Bricklaying, Stone Masonry, Concretes, "
         "Stuccos and Plasters (1920)"),
        ("key", "trade:purchase_practical_masonry_1904", "Practical Masonry: stone cutting (1904)"),
        ("key", "trade:ics_concrete_engineers_handbook_1912", "The Concrete Engineer's Handbook (1912)"),
        ("key", "trade:niosh_2002_129_silica", "Silica dust: health effects and controls (NIOSH)"),
        ("manuals", "concrete_masonry", "Concrete and masonry product safety data"),
        ("manuals", "masonry_paint_drywall", "Masonry, paint and drywall tool makers' manuals")]),
    ("Roofing", "Roofing work and its hazards: falls, heat and asphalt fumes.", [
        ("key", "build:osha_3146_fall_protection", "Fall Protection in Construction (OSHA 3146)"),
        ("key", "trade:niosh_construction_hazards", "Falls from roofs, roof panels, asphalt fumes and cement roof "
         "tiles (NIOSH)"),
        ("key", "trade:niosh_heat_stress", "Heat stress (NIOSH)"),
        ("manuals", "roofing_insulation", "Roofing and insulation product safety data")]),
    ("General construction safety", "For every building trade: falls, scaffolds, ladders, trenches, cranes, "
     "electricity, silica and lead.", [
        ("key", "trade:osha_2202_construction_industry_digest", "Construction Industry Digest (OSHA)"),
        ("key", "trade:osha_3886_recommended_practices_construction", "Safety and health programs in construction "
         "(OSHA)"),
        ("key", "build:osha_3150_scaffold_use", "A Guide to Scaffold Use (OSHA 3150)"),
        ("key", "trade:osha_2226_excavations", "Excavations (OSHA)"),
        ("key", "trade:osha_3100_crane_suspended_platforms", "Crane-suspended personnel platforms (OSHA)"),
        ("key", "trade:doe_std_1090_hoisting_rigging", "Hoisting and Rigging (DOE-STD-1090)"),
        ("key", "trade:osha_100_most_cited_construction_1991", "The most cited construction standards and their "
         "fixes (OSHA)"),
        ("key", "trade:niosh_construction_toolbox_talks", "Construction toolbox talks (NIOSH)"),
        ("key", "trade:niosh_2007_122_simple_solutions_construction", "Simple Solutions: ergonomics for construction "
         "workers (NIOSH)"),
        ("key", "trade:niosh_2022_123_respirators_construction", "Respirator selection for construction (NIOSH)"),
        ("key", "trade:osha_3096_asbestos_construction", "Asbestos in construction (OSHA)"),
        ("pack", "commons_construction_safety", "Construction safety photos, for the picture describer"),
        ("manuals", "ladders_handling", "Ladder and material handling makers' manuals"),
        ("manuals", "safety_ppe", "Safety and protective equipment makers' manuals")]),
    ("Auto, diesel and heavy equipment", "Car and truck repair, diesel engines, tyres, and running heavy "
     "equipment.", [
        ("key", "trade:page_automobile_repairing_made_easy_1918", "Automobile Repairing Made Easy (1918)"),
        ("word", "car-care", "Car care books (request word)"),
        ("key", "trade:osha_3086_rim_wheels", "Servicing truck and equipment rim wheels (OSHA)"),
        ("key", "trade:osha_3095_asbestos_general_industry", "Asbestos in brake and clutch work (OSHA)"),
        ("key", "trade:niosh_trade_chemicals", "Spray-on truck bed liners and other chemicals in the trades (NIOSH)"),
        ("key", "trade:niosh_construction_hazards", "Skid-steer loaders, dump trucks, excavators and backing "
         "vehicles (NIOSH)"),
        ("key", "trade:niosh_drivers_vehicles", "Driving at work and forklift inspections (NIOSH)"),
        ("key", "trade:niosh_2001_109_forklifts", "Forklift injuries and deaths (NIOSH)"),
        ("key", "drive:index_us", "Driver's and commercial driver's handbooks by state"),
        ("manuals", "automotive_shop", "Automotive shop equipment makers' manuals"),
        ("manuals", "small_engines", "Small engine makers' manuals"),
        ("manuals", "farm_equipment", "Tractor and farm equipment makers' manuals")]),
    ("Factories, shops and maintenance", "Machine operators, maintenance mechanics and millwrights.", [
        ("key", "trade:osha_3120_lockout_tagout", "Lockout and tagout (OSHA)"),
        ("key", "trade:osha_3067_machine_safeguarding", "Machine safeguarding (OSHA)"),
        ("key", "trade:osha_amputations_safeguarding", "Preventing amputations (OSHA)"),
        ("key", "trade:osha_3080_hand_power_tools", "Hand and power tools (OSHA)"),
        ("key", "trade:osha_3138_confined_spaces", "Confined spaces (OSHA)"),
        ("key", "trade:osha_3071_job_hazard_analysis", "Job hazard analysis (OSHA)"),
        ("key", "trade:osha_3111_hazard_communication", "Hazard communication (OSHA)"),
        ("key", "trade:niosh_2005_149_pocket_guide", "NIOSH Pocket Guide to Chemical Hazards"),
        ("key", "trade:osha_2209_small_business_handbook", "OSHA Handbook for Small Businesses"),
        ("manuals", "chemical_safety", "The NIOSH Pocket Guide's chemicals, one by one, with CAMEO and PubChem "
         "links"),
        ("manuals", "power_tools", "Power tool makers' manuals")]),
    ("Protective equipment, noise, heat and lifting", "Respirators, hearing, heat stress and lifting: for every "
     "trade.", [
        ("key", "trade:osha_3077_personal_protective_equipment", "Personal protective equipment (OSHA)"),
        ("key", "trade:osha_3151_ppe_small_business", "Assessing the need for protective equipment (OSHA)"),
        ("key", "trade:niosh_respirators", "Respirators (NIOSH guides)"),
        ("key", "trade:osha_3384_respiratory_small_entity", "The respirator standard, step by step (OSHA)"),
        ("key", "trade:niosh_hearing", "Hearing loss at work (NIOSH guides)"),
        ("key", "trade:niosh_96_110_preventing_hearing_loss", "Preventing occupational hearing loss (NIOSH)"),
        ("key", "trade:niosh_heat_stress", "Heat stress (NIOSH guides)"),
        ("key", "trade:niosh_2016_106_heat_criteria", "Working in heat: NIOSH's recommendations"),
        ("key", "trade:niosh_2007_131_manual_material_handling", "Manual material handling (NIOSH)"),
        ("key", "trade:niosh_94_110_lifting_equation", "The NIOSH lifting equation"),
        ("key", "trade:niosh_2004_164_hand_tools", "Choosing hand tools (NIOSH)")]),
    ("Landscaping, tree work and farming", "Grounds keeping, tree felling, farm work, grain and silos.", [
        ("key", "trade:cfr_29_1928_agriculture", "The OSHA agriculture standards"),
        ("key", "trade:osha_3103_grain_handling", "Grain handling (OSHA)"),
        ("key", "trade:niosh_2010_137_worker_safety_farm", "Worker safety on the farm (NIOSH)"),
        ("key", "trade:niosh_2001_111_simple_solutions_farm", "Simple Solutions: ergonomics for farm workers"),
        ("key", "trade:niosh_farm_safety", "Silo fires, ATVs and landscape workers (NIOSH)"),
        ("key", "trade:usfs_chain_saw_training_guide_1978", "Chain Saw Training Guide (Forest Service, 1978)"),
        ("key", "knot:usfs_crosscut_saw_manual", "Crosscut Saw Manual (Forest Service)"),
        ("key", "trade:drew_farm_blacksmithing_1904", "Farm Blacksmithing (1904)"),
        ("word", "gardening", "Gardening and lawn books (request word)"),
        ("word", "homestead", "Homesteading and small livestock books (request word)"),
        ("manuals", "lawn_garden", "Lawn and garden equipment makers' manuals"),
        ("pack", "farm_commons_equipment", "Farm equipment photos, for the picture describer")]),
    ("Culinary and food work", "Cooks, bakers, butchers and grocery workers.", [
        ("word", "cookbooks", "Cookbooks and the Army's cook and baker manuals (request word)"),
        ("key", "trade:osha_safety_guide_meatpacking_1988", "Safety and health in meat cutting and packing (OSHA)"),
        ("key", "trade:osha_3192_grocery_ergonomics", "Ergonomics in grocery stores (OSHA)"),
        ("manuals", "kitchen_equipment", "Commercial kitchen equipment makers' manuals"),
        ("link", "FDA Food Code", "https://www.fda.gov/food/retail-food-protection/fda-food-code",
         "the model code for restaurants and food stores; open it in a browser")]),
    ("Cosmetology, barbering and nail care", "Hair, skin and nail work and its chemical hazards. Licensing rules "
     "are set by each state's board.", [
        ("key", "trade:moler_manual_on_barbering_1906", "The Manual on Barbering, Hairdressing and Manicuring (1906, "
         "history)"),
        ("key", "trade:niosh_trade_chemicals", "Artificial fingernails and other chemicals (NIOSH)"),
        ("key", "pcare:index", "Personal care: the guide to cosmetics safety"),
        ("key", "pcare:fda_cosmetics_safety", "Cosmetics safety (FDA)"),
        ("manuals", "personal_care_appliances", "Hair dryer, clipper and other appliance makers' manuals"),
        ("link", "Licensed occupations by state (CareerOneStop, US Department of Labor)",
         "https://www.careeronestop.org/Toolkit/Training/find-licenses.aspx",
         "each state licenses these trades; the site refuses programs, so open it in a browser")]),
    ("Care work, cleaning and services", "Nursing assistants, home care, custodians and other service workers.", [
        ("key", "trade:osha_nursing_home_ergonomics", "Lifting and moving residents safely (OSHA)"),
        ("key", "trade:osha_3148_workplace_violence_health_care", "Preventing workplace violence in care work (OSHA)"),
        ("key", "trade:niosh_trade_chemicals", "Cleaning chemicals (NIOSH)"),
        ("key", "trade:osha_4395_workplace_mental_health", "Workplace mental health (OSHA)"),
        ("key", "trade:osha_4396_salud_mental_lugar_de_trabajo", "Salud mental en el trabajo (OSHA, en español)")]),
    ("Mining, longshoring and hazardous waste", "Miners, dock workers and cleanup crews.", [
        ("key", "trade:msha_ot_56_parts_46_48_reference", "Mine training rules: Parts 46 and 48 (MSHA)"),
        ("key", "trade:msha_ig_37_part_46_instructors_guide", "Part 46 instructor's guide with lesson plans (MSHA)"),
        ("key", "trade:osha_2232_longshoring", "Longshoring industry (OSHA)"),
        ("key", "trade:osha_3114_hazwoper", "Hazardous waste operations and emergency response (OSHA)"),
        ("key", "trade:osha_hazardous_waste_site_manual_1985", "Hazardous waste site guidance manual (1985)")]),
    ("Openly licensed trade textbooks", "Open textbooks for trades courses (BCcampus, the Open Textbook Library) are "
     "built with the whole open catalogues.", [
        ("word", "cat:otl", "The Open Textbook Library's openly licensed books, trades among them (request word)"),
        ("link", "BCcampus open textbooks for the trades", "https://open.bccampus.ca/browse-our-collection/",
         "opentextbc.ca asks AI programs not to read it (ai-train=no); open it in a browser"),
        ("link", "Open Textbook Library", "https://open.umn.edu/opentextbooks/",
         "the catalogue; its books are built from the open catalogue snapshot")]),
]

INDEX = X.index_maker("trade", GROUP, "Trades and workplace safety: a guide to the library", "Trades and workplace "
                      "safety", "A guide to the trades in the library: for each trade (carpentry, electrical, "
                      "plumbing, HVAC, welding, masonry, roofing, auto and diesel, heavy equipment, landscaping and "
                      "farm work, culinary, cosmetology and care work), the books to read by key, the OSHA standards, "
                      "the safety guides, the manual collections, picture packs and links.", SECTIONS)

MAKERS = {"index": INDEX}
MAKERS.update({name: cfr_maker(spec) for name, spec in CFR_BOOKS.items()})
MAKERS.update({name: shelf_maker(name, shelf) for name, shelf in SHELVES.items()})

# Which theme each maker belongs to (the PDFs and guides take theirs from their list).
MAKER_THEMES = {
    "trade-construction": ["cfr_29_1926_construction", "niosh_construction_toolbox_talks",
                           "niosh_construction_hazards"],
    "trade-industry": ["cfr_29_1910_general_industry", "cfr_29_1910_subpart_z", "niosh_heat_stress", "niosh_hearing",
                       "niosh_respirators", "niosh_trade_chemicals", "niosh_drivers_vehicles"],
    "trade-farm": ["cfr_29_1928_agriculture", "niosh_farm_safety"],
    "trade-apprentice": ["index", "niosh_young_workers"],
    "trade-texts": [],
}
THEMES = {"trade-construction": CONSTRUCTION, "trade-industry": INDUSTRY, "trade-farm": FARM,
          "trade-apprentice": APPRENTICE, "trade-texts": TEXT_GUIDES + TEXTS}
PDFS = CONSTRUCTION + INDUSTRY + FARM + APPRENTICE + TEXTS
GUIDES = TEXT_GUIDES


def theme_keys(word):
    """The keys of one theme (its request word): its makers first, then its PDFs and guides."""
    return [f"trade:{n}" for n in MAKER_THEMES[word]] + [f"trade:{e['name']}" for e in THEMES[word]]


WORDS = {word: (lambda word=word: theme_keys(word)) for word in THEMES}
WORDS["trades"] = lambda: list(dict.fromkeys(k for word in THEMES for k in theme_keys(word)))

COLLECTION = K.Collection("trade", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "trades_osha": "OSHA booklets: works of the US Department of Labor (17 U.S.C. 105), read from the Defense "
                   "Technical Information Center's copies on the Internet Archive (DTIC_ADA400xxx, each checked to "
                   "have a text layer, 2026-11-23) and from the Internet Archive item 2025-removed-osha (OSHA's "
                   "publications taken off osha.gov in early 2025, saved by a private uploader; OSHA's own works); "
                   "osha.gov answered this machine \"403\" (2026-11-23); archive.org's robots.txt allows the files.",
    "trades_cfr": "29 CFR parts 1910, 1926 and 1928: the Code of Federal Regulations, a US government work, read from "
                  "govinfo.gov's annual editions (govinfo's policy page, quoting 17 U.S.C. 105, checked at every "
                  "build; the right volume is checked by its first section).",
    "trades_niosh": "NIOSH publications: CDC works, read from www.cdc.gov/niosh at every build under CDC's terms "
                    "(www.cdc.gov/other/agencymaterials.html: \"Most of the information on the CDC and ATSDR "
                    "websites is not subject to copyright, is in the public domain\", checked at every build); "
                    "www.cdc.gov's robots.txt allows the pages and PDFs; no AI rules (checked 2026-11-23).",
    "trades_msha_doe_usfs": "MSHA (msha.gov) and Department of Energy (energy.gov) publications and the Forest "
                            "Service's 1978 Chain Saw Training Guide (the National Agricultural Library's scan on "
                            "the Internet Archive): works of the US government (17 U.S.C. 105); the sites' "
                            "robots.txt allow the files; no AI rules (checked 2026-11-23).",
    "trades_bls": "The Occupational Outlook Handbook, 2012-13 edition (BLS Bulletin 2800): a US government work, read "
                  "from Claitor's Publishing Division's reprint on the Internet Archive (bls.gov refuses programs); "
                  "Claitor's copyright page claims only \"format and where modified by Claitor's\" and says the "
                  "Department of Labor's text is not copyrighted, so the text is made into the toolkit's own pages.",
    "trades_old_books": "Old trade books: Internet Archive items whose record shows a date before 1931 (checked at "
                        "every build, so a later reprint is refused): public domain in the US; archive.org's "
                        "robots.txt allows the files (checked 2026-11-23).",
    "trades_wikibooks": "Wikibooks' Welding: CC BY-SA 4.0 (share-alike, kept as its own book; the licence line on "
                        "Wikibooks:Copyrights is checked at every build).",
    "trades_index": "The index (trade:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("OSHA's web pages, eTools, QuickCards, fact sheets and current booklets (osha.gov), with the Spanish editions",
     "Public domain, but www.osha.gov answered this build machine \"403\" (2026-11-23, robots.txt included); the "
     "older booklets are built from DTIC's copies, and the publications OSHA removed in 2025 from the Internet "
     "Archive's copy. Link-only for the current editions. Index: https://www.osha.gov/publications"),
    ("OSHA Outreach Training Program (10-hour and 30-hour courses) student materials", "OSHA publishes no student "
     "book for these courses: the course is taught by authorised trainers with their own materials, and the cards "
     "come from the trainer. Link-only. Index: https://www.osha.gov/training/outreach"),
    ("Susan Harwood Training Grant materials", "Made by the grantees and published on osha.gov, which refuses "
     "programs; each grantee's licence would have to be checked one by one on a page that cannot be read here "
     "(2026-11-23). Link-only. Index: https://www.osha.gov/harwoodgrants/grantmaterials"),
    ("OSHA booklets on DTIC whose copies are scans without words: Lead in Construction (OSHA 3142, DTIC_ADA400365) "
     "and Ergonomics Program Management Guidelines for Meatpacking Plants (OSHA 3123, DTIC_ADA400145)", "Their "
     "Internet Archive copies have no text layer (checked 2026-11-23), so they cannot be read aloud. Index: "
     "https://archive.org/details/DTIC_ADA400365"),
    ("Other OSHA booklets on DTIC (bloodborne pathogens, needlesticks, video display terminals, process safety, MDA, "
     "cadmium, automated external defibrillators, voluntary protection programs)", "Health-care, chemical-plant or "
     "administrative subjects outside the trades, or a few pages only; not built. Index: "
     "https://archive.org/search?query=DTIC_ADA400"),
    ("NIOSH publications in Spanish and other languages", "NIOSH's numbered pages link few translations; the Spanish "
     "respiratory protection toolbox talk (trade:niosh_2022_102_proteccion_respiratoria_es) is built; no other "
     "Spanish copy of the trade guides was found (checked 2026-11-23). Index: https://www.cdc.gov/niosh/"
     "publications/numbered/index.html"),
    ("Apprenticeship.gov occupation guides, work process schedules and national guideline standards", "The "
     "occupation pages are a JavaScript application whose search needs keys embedded in the page (a private "
     "service, and robots.txt forbids /search/); the site's pages for apprentices are already built "
     "(edu:apprenticeship_gov). Link-only. Index: https://www.apprenticeship.gov/apprenticeship-occupations"),
    ("Job Corps trade curricula (Training Achievement Records)", "Not published openly by Job Corps (checked "
     "2026-11-23); Job Corps' own pages are built (edu:job_corps). Index: https://www.jobcorps.gov/explore"),
    ("Occupational Outlook Handbook, current edition (bls.gov)", "Public domain, but www.bls.gov refuses programs "
     "(403, 2026-11-23); the 2012-13 edition is built from its reprint, and O*NET (mw:onet_occupations) is current. "
     "Link-only. Index: https://www.bls.gov/ooh/"),
    ("BCcampus trades open textbooks (opentextbc.ca)", "CC BY, but opentextbc.ca's robots.txt says ai-train=no and "
     "shuts out AI companies' readers, so it is never read; the BCcampus Kolibri channel and the Open Textbook "
     "Library catalogue (cat:otl) are built with the open catalogues. Index: "
     "https://open.bccampus.ca/browse-our-collection/"),
    ("Washington State SBCTC open trades courses (openspace.sbctc.edu)", "The site could not be reached from this "
     "build machine (connection refused, 2026-11-23). Index: https://www.sbctc.edu/colleges-staff/programs-services/"
     "open-education/"),
    ("DOE Fundamentals Handbooks (electrical science, mechanical science, thermodynamics, instrumentation)", "No "
     "longer on energy.gov's list of current standards and no Internet Archive copy was found (2026-11-23). "
     "Index: https://www.energy.gov/ehss/technical-standards-current"),
    ("Forest Service and BLM chain saw courses newer than 1978", "fs.usda.gov's training pages answer programs "
     "\"403\"; the BLM's Chainsaw Maintenance note (1969) is two pages only. Index: "
     "https://archive.org/details/chainsawmaintena10bure"),
    ("Modern trade textbooks (Audel, ATP, Goodheart-Willcox, NCCER, Delmar)", "Copyright of their publishers; "
     "link-only. Index: https://openlibrary.org/search?q=subject%3Abuilding+trades"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
