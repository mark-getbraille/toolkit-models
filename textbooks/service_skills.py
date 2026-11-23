"""Job-skill training manuals of the US Army, Marine Corps, Air Force and Coast Guard, for the reference library, in
their own group "Reference, job skills (US military training manuals)" (the owner's request of 23 November 2026:
military trade handbooks to fill in practical skills). Keys: skill:<name>, skill:index (a guide to every trade).
Request words: service-skills (every book and the index) and one word per trade (TRADES below: service-skills-food,
service-skills-medical and the rest), each at most 256 books.

What this module builds, in plain words, each book read WHOLE from its Internet Archive copy and judged at every
build by the release rule for US military publications (military_release.py: the builder reads the front pages and
says truthfully in the notice whether Distribution Statement A is printed; a restricted marking is never
republished). Only parts about explosives, demolition, mines, grenades, booby traps, improvised explosives and
sabotage are cut (build_textbooks.NOT_FIELD_SAFE, applied because every entry has distribution_a):
  - Army Correspondence Course Program (ACCP) subcourses: the Army's public-domain self-study booklets, each a
    lesson course with exercises and answers, from the Medical Department Center and School (MD), the Ordnance
    (OD), Engineer (EN), Quartermaster (QM), Signal (SS), missile and munitions electronics (MM), Transportation
    (TR), aviation (AL, AV) and finance (FI) schools, and two interschool (IS) first-aid courses;
  - Army soldier's manuals, technical manuals, field manuals, training circulars and technical bulletins on common
    trade skills (the cook's soldier's manuals, the Armed Forces Recipe Service, baking, fabric repair, plumbing,
    well drilling, electrical facilities, heating, water supply, food sanitation, preventive medicine, surveying,
    fire fighting, diving, airframe maintenance);
  - Marine Corps Institute (MCI) correspondence courses (food service, mechanics, refrigeration, plumbing,
    electricity, antennas, warehousing, supply and personal finance), from the copies the Marine Corps Institute
    gave to ERIC, the US Department of Education's library, which publishes them openly;
  - Air Force and Coast Guard courses where a government library publishes them openly: the Air Force's Fire
    Protection Specialist career development course (CDC 57150) and the Coast Guard's boating safety course, from
    the Military Curriculum Materials that ERIC publishes, and the Coast Guard's Helicopter Rescue Swimmer Manual.
  Each book carries its trade's safety note (TRADES): electricity, fuel and chemicals, workshops, food safety, and
  for the medical courses "follow current medical guidance".

Years: every book's year is the one printed on its own front pages ("Washington, DC, 30 September 1991", "REVIEWED:
1988", "EDITION DATE: October 1991"). The Medical Department's subcourses and some others print none, so their year is
the year their PDF file was made, as the PDF's own information says (checked 2026-11-23 for each one); a copy remade
in a word processor in recent years, which shows no year of its own, is left out. The ERIC copies carry the year of
their ERIC record, and the few manuals whose front pages show no date carry the year of their Internet Archive
record.
Each notice says which.

Already in the library and linked from the index rather than repeated: the field manuals (fieldmanuals: first aid,
map reading, field sanitation, rigging, survival), the Army carpentry and masonry manuals (build:), the Army
mechanic, driver, motorcycle and CDL manuals (gpo:), the radio and electronics manuals (radio:, elec:), the machine
tool manuals (make:), the generator manuals (power:), the boat manuals (boat:, kmil:), the whole military manuals
(milw:), the Army cook and recipe book of the 1940s (cookbooks) and the Army photography manuals (photo:). The US Navy
rating manuals (NAVEDTRA rate training manuals) are a separate collection. NOT_INCLUDED says what was left out and
why.

Run from the repository's folder:
  python3 textbooks/service_skills.py skill:accp_md0531_taking_vital_signs --out build/textbooks --limit 3
  python3 textbooks/service_skills.py --list service-skills-medical
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402 - the index maker
import refs_kit as K  # noqa: E402

PREFIX = "skill"
GROUP = "skills"
GROUPS = {GROUP: "Reference, job skills (US military training manuals)"}
DECISION = "23 November 2026"

# The first words of every notice; the builder puts the truthful release line in front of them (what the copy's
# front pages print about distribution, and whose work it is: build_textbooks.military_notice).
NOTICE = ("The release line before this says what its own front pages print about distribution. A US military "
          "training manual, read whole: its procedures, equipment and rules are military ones of its day and may be "
          "out of date. Parts about explosives, demolition, mines, grenades, booby traps and sabotage are left out. ")

# ---------------------------------------------------------------------- the trades and their safety notes
MEDICAL_SAFETY = ("Medical safety: medicine has changed since these were written (drug names and doses, CPR, wound "
                  "and burn care, infection control): follow current medical guidance from your doctor, pharmacist, "
                  "nurse or a current first-aid course, and call 911 (or 112) in an emergency. They are training "
                  "texts for supervised military students, not a licence to treat anyone.")
FOOD_SAFETY = ("Food safety: cook, cool and hold food at the temperatures today's FDA Food Code and USDA advice give "
               "(foodsafety.gov), wash hands and surfaces, and mind allergens; field-kitchen recipes feed 100 people "
               "and must be scaled down with care.")
VET_SAFETY = ("Food inspection and animal care: today's rules are the USDA's (FSIS) and the FDA's, and these "
              "booklets are military ones of their day; for an animal's health, ask a veterinarian. " + FOOD_SAFETY)
MECH_SAFETY = ("Workshop safety: wear eye and hearing protection, never work under a vehicle held only by a jack, "
               "disconnect the battery before electrical work, let engines and exhausts cool, weld and cut only with "
               "a proper helmet, gloves and ventilation and away from anything that burns, and follow the maker's "
               "manual for your own vehicle, engine or machine.")
BUILD_SAFETY = ("Electrical, plumbing and building safety: turn the power off at the breaker and test before touching "
                "wires, follow your local building, electrical and plumbing codes and permits (the National "
                "Electrical Code has changed since these were written), use fall protection on roofs and ladders, "
                "mind trenches that can cave in, and have a licensed electrician, plumber or gas fitter do or check "
                "the work where the law requires it. Have well or treated water tested before drinking it; "
                "refrigerants must be handled by a certified technician (EPA section 608).")
QM_SAFETY = ("Fuel, chemical and rigging safety: fuel burns and its vapours explode, so keep sparks and flames away, "
             "ground and bond containers and read each product's safety data sheet; only trained, certified riggers "
             "pack parachutes (in the US, FAA rules), and slung loads are lifted only by trained crews.")
COMMS_SAFETY = ("Electrical safety: radio transmitters, power supplies and old valve (tube) sets hold voltages that "
                "can kill even when unplugged; keep antennas and masts well clear of power lines; transmitting needs "
                "a licence (FCC rules in the US).")
ADMIN_SAFETY = ("The supply, pay and money rules here are military ones of their day; for your own money and taxes, "
                "use current IRS and CFPB guidance.")
MAPS_SAFETY = ("Outdoors, carry a current map and compass, tell someone your route, and learn navigation with someone "
               "experienced; GPS and old maps can be wrong.")
TRANSPORT_SAFETY = ("Railway and boat safety: stay off railway tracks and property unless trained and authorised; "
                    "wear a life jacket on the water.")
AVIATION_SAFETY = ("Aviation safety: in the US, aircraft maintenance needs an FAA certificate and follows the FAA's "
                   "current rules and the aircraft maker's manuals; weather codes, charts and procedures change; "
                   "for outdoor emergencies call 911 (or 112) when you can.")
RESCUE_SAFETY = ("Rescue safety: call 911 (or 112) first; never enter a burning building, smoke, deep or moving water "
                 "or a confined space to rescue someone without training, equipment and a team; diving needs "
                 "certified training.")

# Trade: (request word, title in plain words, safety note, what the trade covers in plain words)
TRADES = {
    "food": ("service-skills-food", "Food service and baking", FOOD_SAFETY,
             "Cooking for many people, baking bread and pastry, field kitchens, recipes, and keeping food safe."),
    "vet": ("service-skills-veterinary", "Veterinary food inspection", VET_SAFETY,
            "The Army veterinary service's food inspection courses: meat, poultry, fish, eggs, dairy, fruit and "
            "vegetables, preserving, storage and spoilage."),
    "medical": ("service-skills-medical", "Medical care: combat medic, nursing, pharmacy, laboratory, dental and "
                "preventive medicine", MEDICAL_SAFETY,
                "The Army Medical Department's courses: anatomy, medical words, vital signs, CPR, wounds, fractures, "
                "injections and drips, the body's systems, nursing care, the operating room, pharmacy, the "
                "laboratory, the dental clinic, and preventive medicine (diseases, insects and rodents, pesticides, "
                "industrial hygiene)."),
    "mech": ("service-skills-mechanics", "Mechanics, machining and welding", MECH_SAFETY,
             "Wheeled vehicles (engines, electrics, fuel, clutches and transmissions, axles, steering, brakes), "
             "diesel engines and generators, shop safety and measuring, the lathe, the milling machine and band saw, "
             "welding, body repair and blacksmithing."),
    "build": ("service-skills-construction", "Construction and utilities: carpentry, masonry, plumbing, electrical, "
              "heating and cooling, wells and water", BUILD_SAFETY,
              "Carpentry, frames and print reading, masonry and concrete, painting, plumbing and sewers, electrical "
              "wiring and grounding, heating, refrigeration and air conditioning, logging and sawmills, well "
              "drilling, and water supply and treatment."),
    "qm": ("service-skills-quartermaster", "Quartermaster: fabric repair, laundry and shower, parachutes, slings and "
           "petroleum", QM_SAFETY,
           "Repairing tents and canvas, field laundries and showers, sewing machine care, parachuting and slung "
           "loads, and handling fuel at supply points and in tank trucks."),
    "comms": ("service-skills-communications", "Communications and electronics", COMMS_SAFETY,
              "Basic electricity and electronics, solid-state devices, radio transmitters and receivers, "
              "antennas and wave propagation, testing wire lines, cable construction, and setting poles."),
    "admin": ("service-skills-admin", "Administration, supply and everyday math", ADMIN_SAFETY,
              "Basic math (arithmetic, decimals, area and volume, ratios), statistics, unit supply, warehousing and "
              "personal finance."),
    "maps": ("service-skills-maps", "Surveying and map making", MAPS_SAFETY,
             "Surveying and topographic surveys, and map making (cartography); map reading and land navigation are "
             "in the field manuals (FM 3-25.26), linked below."),
    "transport": ("service-skills-transport", "Transportation: railways and watercraft", TRANSPORT_SAFETY,
                  "Rail yards and dispatching, locomotives and rolling stock, track maintenance, loading rail cars, "
                  "and watercraft safety."),
    "aviation": ("service-skills-aviation", "Aviation maintenance, weather and aviation medicine", AVIATION_SAFETY,
                 "Hydraulics, aerodynamics, airframe repair and maintenance, gas turbine engines, aviation weather "
                 "and its report codes, and aviation medicine."),
    "rescue": ("service-skills-rescue", "Fire fighting, rescue, diving and boating safety", RESCUE_SAFETY,
               "Fire fighting and fire protection, rescue swimmers, engineer diving, and boating safety."),
}
ALL_WORD = "service-skills"

# The services' publishers, as each copy names them.
ARMY = "Department of the Army"
ACCP = "Department of the Army, Army Correspondence Course Program"
AMEDD = "US Army Medical Department Center and School (Academy of Health Sciences), Fort Sam Houston"
MCI = "Marine Corps Institute, Washington, DC (US Marine Corps)"
WORKS = {"army": "a work of the US Army", "usmc": "a work of the US Marine Corps", "usaf": "a work of the US Air Force",
         "uscg": "a work of the US Coast Guard", "joint": "a work of the US armed forces"}
SERVICES = {"army": "US Army", "usmc": "US Marine Corps", "usaf": "US Air Force", "uscg": "US Coast Guard",
            "joint": "US Army, Navy, Air Force and Marine Corps"}
VIA = {"ia": "the Internet Archive", "eric": "the Internet Archive's copy of ERIC, the US Department of Education's "
       "library, which publishes it openly (eric.ed.gov)"}
YEAR_BASIS = {"printed": "the date printed on its own front pages",
              "pdf": "the year its PDF was made, as the PDF's own information says; it prints no date of its own",
              "record": "the year its library record gives",
              "eric": "the year of its ERIC record"}
# More notice words, by short name: the Military Curriculum Materials of the 1970s, military courses that a project
# of the US Office of Education chose for civilian vocational schools, which ERIC publishes.
MORE = {"MCM": ("Selected and reproduced in the Military Curriculum Materials series by the National Center for "
                "Research in Vocational Education (Ohio State University) for the US Office of Education; its cover "
                "note says that materials specific to the military were deleted and that copyrighted materials were "
                "either omitted or used with approval.")}


def entry(trade, name, service, pubno, title, publisher, archive, year, basis, description, via="ia", more=""):
    """One manual of the Internet Archive as a PDF entry: read whole, judged by the release rule (distribution_a,
    so only parts about explosives are cut), with a notice that names the service, the publication number, the
    edition year and its basis, the copyright basis (a US government work, public domain) and where the copy was
    read, then the trade's safety note."""
    safety = TRADES[trade][2]
    more = MORE.get(more, more)
    publisher = {"ARMY": ARMY, "ACCP": ACCP, "AMEDD": AMEDD, "MCI": MCI}.get(publisher, publisher)
    notice = (f"{NOTICE}{SERVICES[service]}, {pubno} ({year}: {YEAR_BASIS[basis]}). {WORKS[service][0].upper()}"
              f"{WORKS[service][1:]} (17 U.S.C. 105): public domain in the US. Read from {VIA[via]} (item "
              f"{archive}). {more + ' ' if more else ''}{safety}")
    return K.us_pdf(GROUP, name=name, title=title, subject=TRADES[trade][1], publisher=publisher, archive=archive,
                    published=str(year), version=f"{pubno}, {year} (Internet Archive item {archive})",
                    description=description, notice=notice, distribution_a=True, work=WORKS[service], trade=trade,
                    service=service)


# ====================================================================== the books, by trade
# (trade, name, service, publication number, title, publisher, Internet Archive item, year, year basis,
#  description in plain words from the copy's own scope or catalogue words, via, more notice words)
ROWS = [
    # ---------------------------------------------------------------- food service and baking
    ("food", "army_stp_10_92g1_food_service_specialist_sl1_2003", "army", "STP 10-92G1-SM-TG",
     "Soldier's Manual and Trainer's Guide: Food Service Specialist, MOS 92G, Skill Level 1 (STP 10-92G1-SM-TG, "
     "2003)",
     ARMY, "stp-10-92-g-1-cook-sl-1-2003", 2003, "printed",
     "The Army cook's soldier's manual and trainer's guide for skill level 1 (MOS 92G), read whole: the tasks a "
     "cook must do and how each is trained and checked.", "ia"),
    ("food", "army_stp_10_92g25_food_service_specialist_sl2_5_2004", "army", "STP 10-92G25-SM-TG",
     "Soldier's Manual and Trainer's Guide: Food Service Specialist, MOS 92G, Skill Levels 2 to 5 (STP "
     "10-92G25-SM-TG, 2004)",
     ARMY, "stp-10-92-g-25-cook-sl-2-5-2004", 2004, "printed",
     "The Army cook's soldier's manual and trainer's guide for skill levels 2 to 5 (MOS 92G), read whole: the tasks "
     "of cooks and food service sergeants and how each is trained and checked. Its parts: Trainer's guide; "
     "MOS/Skill Level Tasks; Duty position tasks.", "ia"),
    ("food", "army_tm_10_412_armed_forces_recipe_service_2003", "joint",
     "TM 10-412 (NAVSUP P-421, AFMAN 34-406, MCO 10110.42)",
     "Armed Forces Recipe Service (TM 10-412, 2003)",
     "Departments of the Army, the Navy and the Air Force (Joint Culinary Center of Excellence)",
     "tm-10-412-armed-forces-recipe-service-2003", 2003, "printed",
     "The armed forces' recipe file, the 2003 edition (the newest of the TM 10-412 recipes, which go back to the "
     "Army Recipes of 1946 in the cookbooks), read whole: its guidelines and its recipe cards, each for 100 "
     "portions.", "ia"),
    ("food", "army_tm_10_410_the_army_baker_1941", "army", "TM 10-410",
     "The Army Baker (TM 10-410, 1941)",
     "War Department", "tm-10-410-army-baker-1941", 1941, "record",
     "The Army's 1941 manual for bakers, read whole. An old edition, kept because it teaches baking bread in field "
     "ovens, which later manuals dropped.", "ia"),
    ("food", "army_tm_10_411_pastry_baking_1966", "army", "TM 10-411",
     "Pastry Baking (TM 10-411, 1966)",
     ARMY, "tm-10-411-pastry-baking-1966", 1966, "printed",
     "The Army's 1966 manual of pastry baking, read whole. Its parts: Operations; Sanitation and safety; "
     "Ingredients; Cakes; Cookies; Quick breads; Rolls; Danish pastry; Table of equivalent weights and measures of "
     "specific foods.", "ia"),
    ("food", "army_tm_10_406_cooking_dehydrated_foods_1943", "army", "TM 10-406",
     "Cooking Dehydrated Foods (TM 10-406, 1943)",
     "War Department", "tm-10-406-cooking-dehydrated-foods-1943", 1943, "printed",
     "The Army's Second World War manual of cooking dehydrated foods, read whole; the only manual here on cooking "
     "dried foods. Its parts: Reconstitution of dehydrated foods; Eggs and meat dishes; Table of weights and "
     "measures.", "ia"),
    ("food", "army_tb_med_530_food_sanitation_2002", "joint", "TB MED 530 (NAVMED P-5010-1, AFMAN 48-147_IP)",
     "Occupational and Environmental Health: Food Sanitation (TB MED 530, 2002)",
     "Departments of the Army, the Navy and the Air Force", "ost-military-medical-tbmed530", 2002, "printed",
     "The armed forces' food sanitation bulletin (their food code), read whole. Its parts: Management and "
     "personnel; Food; Equipment and utensils; Sanitary facilities and controls; Mobile food establishments; "
     "Temporary food service establishment; Field food service; Vending machine operations; Poisonous or toxic "
     "materials; Administrative procedures; Model risk assessment plan for scheduling; Hazard analysis critical "
     "control point.", "ia"),
    ("food", "usmc_mci_food_service_fundamentals_1982", "usmc",
     "Marine Corps Institute course (ERIC document ED258039)",
     "Food Service Fundamentals (Marine Corps Institute, 1982)",
     MCI, "ERIC_ED258039", 1982, "eric",
     "The Marine Corps Institute's correspondence course on food service fundamentals, read whole, with its review "
     "exercises.", "eric"),
    ("food", "usmc_mci_pastry_baking_1984", "usmc", "Marine Corps Institute course (ERIC document ED258040)",
     "Pastry Baking (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258040", 1984, "eric",
     "The Marine Corps Institute's correspondence course on pastry baking, read whole, with its review "
     "exercises.", "eric"),
    ("food", "usmc_mci_meats_and_meat_cookery_1984", "usmc", "Marine Corps Institute course (ERIC document ED258041)",
     "Meats and Meat Cookery (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258041", 1984, "eric",
     "The Marine Corps Institute's correspondence course on meats and meat cookery, read whole, with its review "
     "exercises.", "eric"),
    ("food", "usmc_mci_vegetables_soups_sauces_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED258042)",
     "Vegetables, Soups, Sauces, Gravies and Beverages (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258042", 1984, "eric",
     "The Marine Corps Institute's correspondence course on vegetables, soups, sauces, gravies and beverages, read "
     "whole, with its review exercises.", "eric"),
    ("food", "usmc_mci_salads_sandwiches_desserts_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED258043)",
     "Salads, Sandwiches and Desserts (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258043", 1984, "eric",
     "The Marine Corps Institute's correspondence course on salads, sandwiches and desserts, read whole, with its "
     "review exercises.", "eric"),
    ("food", "accp_qm0333_basic_food_preparation", "army",
     "Army Correspondence Course Program subcourse QM0333, edition 8",
     "Basic Food Preparation (Army subcourse QM0333, edition 8, 2004)",
     ACCP, "qm-0333-basic-food-preparation-edition-8", 2004, "pdf",
     "The Army's self-study subcourse QM0333 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Control of quality in basic food preparation; the preparation of various food items with methods of "
     "controlling the quality and guidelines for judging the quality of the finished products; identification of "
     "foods that can be served as leftovers; and suggestions for serving leftovers as palatable food "
     "items.", "ia"),
    ("food", "accp_qm0454_food_preparation_i", "army",
     "Army Correspondence Course Program subcourse QM0454, edition 0",
     "Food Preparation 1 (Army subcourse QM0454, edition 0, 2004)",
     ACCP, "qm-0454-food-preparation-i-edition-0", 2004, "pdf",
     "The Army's self-study subcourse QM0454 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Common working procedures; important terms; utilization of recipes; preparation of beverages, "
     "breakfast foods, meat, poultry, seafood, paste products, and dessert and other pastry.", "ia"),
    ("food", "accp_md0181_food_service_sanitation_and_inspections_i", "army",
     "Army Correspondence Course Program subcourse MD0181, edition 100",
     "Food Service Sanitation and Inspections 1 (Army subcourse MD0181, edition 100, 2001)",
     AMEDD, "md-0181-food-service-sanitation-and-inspections-i-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0181 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Microorganisms causing foodborne disease, environmental conditions ideal for their growth, and "
     "common foodborne diseases. Discussion of the factors causing foodborne disease outbreaks in the field and in "
     "garrison and related sanitary measures to prevent foodborne disease.", "ia"),
    ("food", "accp_md0182_food_service_sanitation_and_inspections_ii", "army",
     "Army Correspondence Course Program subcourse MD0182, edition 100",
     "Food Service Sanitation and Inspections 2 (Army subcourse MD0182, edition 100, 2001)",
     AMEDD, "md-0182-food-service-sanitation-and-inspections-ii-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0182 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Areas of a food service facility examined during an inspection and the major items to inspect in "
     "each area.", "ia"),
    # ---------------------------------------------------------------- veterinary food inspection
    ("vet", "accp_md0694_basic_food_inspection_procedures", "army",
     "Army Correspondence Course Program subcourse MD0694, edition 200",
     "Basic Food Inspection Procedures (Army subcourse MD0694, edition 200, 2004)",
     AMEDD, "md-0694-basic-food-inspection-procedures-edition-200", 2004, "pdf",
     "The Army's self-study subcourse MD0694 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Basic food inspection procedures, including categories and classes of food inspection; stamping "
     "procedures; warehouse procedures; measurement of product temperature; inspection of conveyances; determining "
     "age of product; collecting, preparing, and shipping samples for laboratory testing.", "ia"),
    ("vet", "accp_md0703_preservation_of_foods", "army",
     "Army Correspondence Course Program subcourse MD0703, edition 100",
     "Preservation of Foods (Army subcourse MD0703, edition 100, 2004)",
     AMEDD, "md-0703-preservation-of-foods-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0703 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to food microbiology, including agents causing food spoilage, morphology and "
     "physiology of microorganisms, microbial growth, microbiology of various food products, food preservation, "
     "including principles and methods of food preservation.", "ia"),
    ("vet", "accp_md0710_red_meats", "army", "Army Correspondence Course Program subcourse MD0710, edition 200",
     "Red Meats (Army subcourse MD0710, edition 200, 2005)",
     AMEDD, "md-0710-red-meats-edition-200", 2005, "pdf",
     "The Army's self-study subcourse MD0710 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and nomenclature of the bovine animal, destination and surveillance inspection of "
     "carcass beef, wholesale market cuts of beef, market ready beef, ground beef, diced beef, beef roasts and "
     "steaks, beef livers, wholesale market cuts of lamb and pork, cured and smoked meats, and corned "
     "beef.", "ia"),
    ("vet", "accp_md0711_waterfoods", "army", "Army Correspondence Course Program subcourse MD0711, edition 100",
     "Waterfoods (Army subcourse MD0711, edition 100, 2001)",
     AMEDD, "md-0711-waterfoods-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0711 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to waterfoods to include basic anatomy, composition and classification of fish and "
     "shellfish; their preparation, preservation, and signs of deterioration; destination, (classes 4 and 8) and "
     "surveillance inspection procedures for waterfoods.", "ia"),
    ("vet", "accp_md0712_poultry_i", "army", "Army Correspondence Course Program subcourse MD0712, edition 100",
     "Poultry 1 (Army subcourse MD0712, edition 100, 2004)",
     AMEDD, "md-0712-poultry-i-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0712 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to poultry (chicken); requirements for class, style, and type; quality standards "
     "for chicken; destination (class 4 and class 8) and surveillance inspection procedures for poultry "
     "(chicken).", "ia"),
    ("vet", "accp_md0713_shell_eggs", "army", "Army Correspondence Course Program subcourse MD0713, edition 100",
     "Shell Eggs (Army subcourse MD0713, edition 100, 2005)",
     AMEDD, "md-0713-shell-eggs-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0713 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Physical structures and formation of an egg; preparation of egg inspection area and equipment; "
     "destination inspection (class 4 and 8) procedures; classifying/grading shell eggs and reporting destination "
     "inspection results; surveillance inspection procedures.", "ia"),
    ("vet", "accp_md0714_fresh_fruits_vegetables", "army",
     "Army Correspondence Course Program subcourse MD0714, edition 100",
     "Fresh Fruits Vegetables (Army subcourse MD0714, edition 100, 2005)",
     AMEDD, "md-0714-fresh-fruits-vegetables-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0714 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to fresh fruits and vegetables, to include: plant physiology and metabolic "
     "procurement methods; destination inspection, (classes 4 and 8) procedures; surveillance inspection "
     "procedures. Not available for individual subcourse enrollment.", "ia"),
    ("vet", "accp_md0715_dairy", "army", "Army Correspondence Course Program subcourse MD0715, edition 100",
     "Dairy (Army subcourse MD0715, edition 100, 2001)",
     AMEDD, "md-0715-dairy-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0715 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Nutritional value of dairy products; types of dairy products; handling, processing, and testing "
     "procedures for dairy products; classifying/grading dairy products for destination inspection; surveillance "
     "inspection procedures for dairy products.", "ia"),
    ("vet", "accp_md0717_storage_and_sanitation", "army",
     "Army Correspondence Course Program subcourse MD0717, edition 100",
     "Storage and Sanitation (Army subcourse MD0717, edition 100, 2005)",
     AMEDD, "md-0717-storage-and-sanitation-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0717 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Food storage and sanitation issues relevant to a food inspector, to include: types and purpose "
     "of sanitary inspections; terminology; sanitation requirements in a food establishment; inspections of "
     "commissaries and troop issue subsistence activities; food storage requirements; insect and rodent control and "
     "fumigation of subsistence.", "ia"),
    ("vet", "accp_md0723_food_deterioration", "army",
     "Army Correspondence Course Program subcourse MD0723, edition 100",
     "Food Deterioration (Army subcourse MD0723, edition 100, 2006)",
     AMEDD, "md-0723-food-deterioration-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0723 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to food deterioration, including basic terminology, causes of food deterioration, "
     "and various deterioration conditions and their characteristics. Deterioration in meat/meat products, "
     "waterfoods, dairy products, shell eggs, fresh fruits and vegetables, and semiperishable subsistence "
     "items.", "ia"),
    ("vet", "accp_md0718_operational_rations_i", "army",
     "Army Correspondence Course Program subcourse MD0718, edition 100",
     "Operational Rations 1 (Army subcourse MD0718, edition 100, 2005)",
     AMEDD, "md-0718-operational-rations-i-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0718 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Modern operational requirements demand state-of-the-art combat rations to provide the "
     "nutritional needs of the war fighter in extremely intense and highly mobile combat situations and other "
     "contingency operations. Defense Supply Center Philadelphia (DSCP) procures hundreds of millions of dollars "
     "worth of operational rations each year for the Armed Forces. As a veterinary food inspection specialist, it "
     "is very important to have a working knowledge of operational rations. You must understand the terminology. In "
     "order to protect the health of the troops as well as the financial interests of the g.", "ia"),
    ("vet", "accp_md0708_food_containers", "army", "Army Correspondence Course Program subcourse MD0708, edition 100",
     "Food Containers (Army subcourse MD0708, edition 100, 2001)",
     AMEDD, "md-0708-food-containers-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0708 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Types of food containers; the can manufacturing process; common defects of cans and other food "
     "containers.", "ia"),
    # ---------------------------------------------------------------- medical
    ("medical", "accp_md0006_basic_human_anatomy", "army",
     "Army Correspondence Course Program subcourse MD0006, edition 100",
     "Basic Human Anatomy (Army subcourse MD0006, edition 100, 2001)",
     AMEDD, "md-0006-basic-human-anatomy-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0006 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to basic human anatomy. Tissues of the body. Structures and structural "
     "relationships within the following human systems: integumentary and fascial, skeletal, muscular, digestive, "
     "respiratory, urogenital, cardiovascular, lymphatic, endocrine, and nervous systems.", "ia"),
    ("medical", "accp_md0007_basic_human_physiology", "army",
     "Army Correspondence Course Program subcourse MD0007, edition 100",
     "Basic Human Physiology (Army subcourse MD0007, edition 100, 2001)",
     AMEDD, "md-0007-basic-human-physiology-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0007 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to basic human physiology. Physiology of cells and miscellaneous tissues. Envelopes "
     "of the body. Physiology of the following human systems: skeletal, muscular, digestive, respiratory, urinary, "
     "reproductive, cardiovascular, endocrine, and nervous systems. The special senses. Elementary human "
     "genetics.", "ia"),
    ("medical", "accp_md0008_introduction_to_military_preventive_medicine", "army",
     "Army Correspondence Course Program subcourse MD0008, edition 100",
     "Introduction to Military Preventive Medicine (Army subcourse MD0008, edition 100, 2005)",
     AMEDD, "md-0008-introduction-to-military-preventive-medicine-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0008 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Disease problems of military units and preventive medicine resources in field operations and "
     "fixed installations; medical aspects of water supply and principles of water purification; waste disposal "
     "procedures for military units; field water purification and waste disposal procedures; and improvised field "
     "sanitary devices.", "ia"),
    ("medical", "accp_md0010_basic_medical_terminology", "army",
     "Army Correspondence Course Program subcourse MD0010, edition 100",
     "Basic Medical Terminology (Army subcourse MD0010, edition 100, 2001)",
     AMEDD, "md-0010-basic-medical-terminology-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0010 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. A study of basic medical terms. A programmed text defining the most common stems, prefixes, and "
     "suffixes used to build a medical vocabulary.", "ia"),
    ("medical", "accp_md0001_evacuation_in_the_field", "army",
     "Army Correspondence Course Program subcourse MD0001, edition 200",
     "Evacuation in the Field (Army subcourse MD0001, edition 200, 2005)",
     AMEDD, "md-0001-evacuation-in-the-field-edition-200", 2005, "pdf",
     "The Army's self-study subcourse MD0001 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. One-man and two-man manual carries, transporting patients on litters, improvising litters, "
     "loading patients into field ambulances and converted military vehicles, loading patients into air ambulances, "
     "and requesting aeromedical evacuation.", "ia"),
    ("medical", "accp_md0531_taking_vital_signs", "army",
     "Army Correspondence Course Program subcourse MD0531, edition 200",
     "Taking Vital Signs (Army subcourse MD0531, edition 200, 2005)",
     AMEDD, "md-0531-taking-vital-signs-edition-200", 2005, "pdf",
     "The Army's self-study subcourse MD0531 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Procedures for taking and recording a patient’s temperature, pulse, respiration, and blood "
     "pressure.", "ia"),
    ("medical", "accp_md0532_cardiopulmonary_resuscitation", "army",
     "Army Correspondence Course Program subcourse MD0532, edition 200",
     "Cardiopulmonary Resuscitation (Army subcourse MD0532, edition 200, 2006)",
     AMEDD, "md-0532-cardiopulmonary-resuscitation-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0532 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Performing rescue breathing and cardiopulmonary resuscitation (CPR) on adults, children, and "
     "infants. Removing upper airway obstructions in adults, children, and infants.", "ia"),
    ("medical", "accp_md0533_treating_fractures_in_the_field", "army",
     "Army Correspondence Course Program subcourse MD0533, edition 200",
     "Treating Fractures in the Field (Army subcourse MD0533, edition 200, 2006)",
     AMEDD, "md-0533-treating-fractures-in-the-field-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0533 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Applying splints to the upper and lower extremities. Applying traction splints. Immobilizing a "
     "casualty with a suspected spinal fracture.", "ia"),
    ("medical", "accp_md0535_communicable_diseases_and_field_sanitation", "army",
     "Army Correspondence Course Program subcourse MD0535, edition 100",
     "Communicable Diseases and Field Sanitation (Army subcourse MD0535, edition 100, 2004)",
     AMEDD, "md-0535-communicable-diseases-and-field-sanitation-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0535 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Types of communicable diseases and methods of transmission. Preventive measures including field "
     "water treatment, food storage and preparation, disposal of human and liquid wastes, disposal of garbage and "
     "rubbish, and control of arthropods and rodents.", "ia"),
    ("medical", "accp_md0540_sterile_procedures", "army",
     "Army Correspondence Course Program subcourse MD0540, edition 100",
     "Sterile Procedures (Army subcourse MD0540, edition 100, 2003)",
     AMEDD, "md-0540-sterile-procedures-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0540 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Medical and surgical asepsis; sterile technique; changing sterile dressings; irrigating a wound; "
     "obtaining a wound culture; and isolation procedures.", "ia"),
    ("medical", "accp_md0542_management_of_patients_with_respiratory_dysfunct", "army",
     "Army Correspondence Course Program subcourse MD0542, edition 200",
     "Management of Patients with Respiratory Dysfunction (Army subcourse MD0542, edition 200, 2006)",
     AMEDD, "md-0542-management-of-patients-with-respiratory-dysfunction-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0542 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Use of oral pharyngeal airways (J–tube) and bag-valve-mask (BVM) devices; oral and nasotracheal "
     "suctioning; preparing an oxygen cylinder for use; and administering oxygen using nasal prongs and "
     "face mask.", "ia"),
    ("medical", "accp_md0547_eye_ear_and_nose_injuries", "army",
     "Army Correspondence Course Program subcourse MD0547, edition 100",
     "Eye, Ear, and Nose Injuries (Army subcourse MD0547, edition 100, 2004)",
     AMEDD, "md-0547-eye-ear-and-nose-injuries-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0547 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Treatment of eye, ear, and nose injuries. Includes irrigating an eye, removing foreign objects "
     "in the eye, treating burns, applying ointment, irrigating an ear, and treating nosebleed.", "ia"),
    ("medical", "accp_md0548_environmental_injuries", "army",
     "Army Correspondence Course Program subcourse MD0548, edition 200",
     "Environmental Injuries (Army subcourse MD0548, edition 200, 2006)",
     AMEDD, "md-0548-environmental-injuries-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0548 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Treatment of heat injuries, cold injuries, snakebites, insect bites and stings, and plant "
     "contact dermatitis.", "ia"),
    ("medical", "accp_md0549_psychosocial_issues", "army",
     "Army Correspondence Course Program subcourse MD0549, edition 200",
     "Psychosocial Issues (Army subcourse MD0549, edition 200, 2006)",
     AMEDD, "md-0549-psychosocial-issues-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0549 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Substance abuse, providing initial care for a casualty suffering from combat stress reaction, "
     "applying restraining devices, referring for treatment a potentially suicidal patient, managing behavioral "
     "emergencies, identifying the physical and emotional characteristics associated with death and dying, and "
     "providing postmortem care.", "ia"),
    ("medical", "accp_md0552_administer_intramuscular_subcutaneous_and_intrad", "army",
     "Army Correspondence Course Program subcourse MD0552, edition 100",
     "Administer Intramuscular, Subcutaneous, and Intradermal Injections (Army subcourse MD0552, edition 100, "
     "2004)",
     AMEDD, "md-0552-administer-intramuscular-subcutaneous-and-intradermal-injections-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0552 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Administering the three types of injections and immunizations.", "ia"),
    ("medical", "accp_md0553_intravenous_infusions_and_related_tasks", "army",
     "Army Correspondence Course Program subcourse MD0553, edition 200",
     "Intravenous Infusions and Related Tasks (Army subcourse MD0553, edition 200, 2006)",
     AMEDD, "md-0553-intravenous-infusions-and-related-tasks-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0553 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Initiating intravenous infusions and managing patients with IVs. Obtaining blood specimens and "
     "managing patients with anaphylactic shock.", "ia"),
    ("medical", "accp_md0554_tactical_combat_casualty_care_and_wound_treatmen", "army",
     "Army Correspondence Course Program subcourse MD0554, edition 200",
     "Tactical Combat Casualty Care and Wound Treatment (Army subcourse MD0554, edition 200, 2006)",
     AMEDD, "md-0554-tactical-combat-casualty-care-and-wound-treatment-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0554 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Controlling bleeding using field dressings, pressure dressings, pressure points, and "
     "tourniquets. Treating head, chest, and abdominal injuries. Treating burns, hypovolemic shock, and soft tissue "
     "injuries. Applying bandages.", "ia"),
    ("medical", "accp_md0556_basic_patient_care_procedures", "army",
     "Army Correspondence Course Program subcourse MD0556, edition 100",
     "Basic Patient Care Procedures (Army subcourse MD0556, edition 100, 2005)",
     AMEDD, "md-0556-basic-patient-care-procedures-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0556 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Making a patient’s bed; bathing a patient; moving and positioning a patient; and performing "
     "routine patient hygiene.", "ia"),
    ("medical", "accp_md0564_blood_electrolytes_and_intravenous_infusions", "army",
     "Army Correspondence Course Program subcourse MD0564, edition 200",
     "Blood, Electrolytes, and Intravenous Infusions (Army subcourse MD0564, edition 200, 2007)",
     AMEDD, "md-0564-blood-electrolytes-and-intravenous-infusions-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0564 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Blood factors and their function during trauma; blood types/groups and their bearing on "
     "transfusions. Kinds of body fluids; normal and abnormal body fluid conditions; functions of electrolytes in "
     "homeostasis. Kinds of fluids suitable for intravenous infusion and their uses; special requirements for "
     "transfusions; infusion procedures and equipment; uses of the venous cutdown procedure.", "ia"),
    ("medical", "accp_md0568_respiratory_diseases_and_disorders", "army",
     "Army Correspondence Course Program subcourse MD0568, edition 200",
     "Respiratory Diseases and Disorders (Army subcourse MD0568, edition 200, 2007)",
     AMEDD, "md-0568-respiratory-diseases-and-disorders-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0568 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Describes the anatomy and physiology of the respiratory system; physical assessment of the "
     "respiratory system; infectious respiratory diseases; chronic obstructive pulmonary diseases; respiratory "
     "disorders; and tuberculosis.", "ia"),
    ("medical", "accp_md0569_chest_and_airway_problems", "army",
     "Army Correspondence Course Program subcourse MD0569, edition 200",
     "Chest and Airway Problems (Army subcourse MD0569, edition 200, 2007)",
     AMEDD, "md-0569-chest-and-airway-problems-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0569 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Chest trauma, airway management with an esophageal obturator airway and with an endotracheal "
     "tube. Procedures necessary to perform a cricothyrotomy.", "ia"),
    ("medical", "accp_md0571_cardiac_impairment", "army",
     "Army Correspondence Course Program subcourse MD0571, edition 100",
     "Cardiac Impairment (Army subcourse MD0571, edition 100, 2005)",
     AMEDD, "md-0571-cardiac-impairment-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0571 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Explains basic cardiac life support; dysrhythmia recognition and treatment; and "
     "cardiac arrest.", "ia"),
    ("medical", "accp_md0572_the_central_nervous_system", "army",
     "Army Correspondence Course Program subcourse MD0572, edition 100",
     "The Central Nervous System (Army subcourse MD0572, edition 100, 2006)",
     AMEDD, "md-0572-the-central-nervous-system-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0572 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology of the central nervous system. Physical assessment of the central nervous "
     "system; central nervous system diseases and disorders; seizures; and central nervous system trauma.", "ia"),
    ("medical", "accp_md0574_surgical_methods", "army",
     "Army Correspondence Course Program subcourse MD0574, edition 200",
     "Surgical Methods (Army subcourse MD0574, edition 200, 2007)",
     AMEDD, "md-0574-surgical-methods-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0574 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Describes minor surgical procedures; wound closure and sutures; and emergency surgical "
     "procedures.", "ia"),
    ("medical", "accp_md0575_integumentary_system", "army",
     "Army Correspondence Course Program subcourse MD0575, edition 100",
     "Integumentary System (Army subcourse MD0575, edition 100, 2005)",
     AMEDD, "md-0575-integumentary-system-edition-100", 2005, "pdf",
     "The Army's self-study subcourse MD0575 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology of the integumentary system; physical assessment of the integumentary "
     "system; primary and secondary skin lesions; common skin diseases; and dermatological drugs.", "ia"),
    ("medical", "accp_md0576_wound_care", "army", "Army Correspondence Course Program subcourse MD0576, edition 200",
     "Wound Care (Army subcourse MD0576, edition 200, 2007)",
     AMEDD, "md-0576-wound-care-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0576 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Wound healing and wound care; contaminated burns; and burns.", "ia"),
    ("medical", "accp_md0577_the_musculoskeletal_system", "army",
     "Army Correspondence Course Program subcourse MD0577, edition 100",
     "The Musculoskeletal System (Army subcourse MD0577, edition 100, 2003)",
     AMEDD, "md-0577-the-musculoskeletal-system-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0577 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Diseases and disorders of the musculoskeletal system. Diseases and disorders of the "
     "feet.", "ia"),
    ("medical", "accp_md0581_the_gastrointestinal_system", "army",
     "Army Correspondence Course Program subcourse MD0581, edition 100",
     "The Gastrointestinal System (Army subcourse MD0581, edition 100, 2006)",
     AMEDD, "md-0581-the-gastrointestinal-system-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0581 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology of the digestive system; physical assessment of the digestive system; "
     "diseases and disorders of the gastrointestinal system. Types of abdominal trauma. Performing nasogastric "
     "intubation. Ingested poisons and hepatitis.", "ia"),
    ("medical", "accp_md0582_the_sensory_system", "army",
     "Army Correspondence Course Program subcourse MD0582, edition 100",
     "The Sensory System (Army subcourse MD0582, edition 100, 2006)",
     AMEDD, "md-0582-the-sensory-system-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0582 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology of the sensory system; physical assessment of the sensory system; EENT "
     "diseases and disorders; and HEENT trauma.", "ia"),
    ("medical", "accp_md0583_the_endocrine_system", "army",
     "Army Correspondence Course Program subcourse MD0583, edition 100",
     "The Endocrine System (Army subcourse MD0583, edition 100, 2006)",
     AMEDD, "md-0583-the-endocrine-system-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0583 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology of the endocrine system; diseases and disorders of the endocrine system; "
     "and describes the disease diabetes mellitus.", "ia"),
    ("medical", "accp_md0584_obstetrics_and_pediatrics", "army",
     "Army Correspondence Course Program subcourse MD0584, edition 200",
     "Obstetrics and Pediatrics (Army subcourse MD0584, edition 200, 2007)",
     AMEDD, "md-0584-obstetrics-and-pediatrics-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0584 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Describes normal emergency childbirth; abnormal childbirth; and how to recognize signs of child "
     "abuse.", "ia"),
    ("medical", "accp_md0586_mental_health", "army",
     "Army Correspondence Course Program subcourse MD0586, edition 100",
     "Mental Health (Army subcourse MD0586, edition 100, 2006)",
     AMEDD, "md-0586-mental-health-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0586 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Discusses normal/abnormal behavior; burnout, depression, and suicide; hostility and violent "
     "behavior; substance abuse; combat stress reactions; death and dying; and sexual assault.", "ia"),
    ("medical", "accp_md0588_environmental_diseases_and_injuries_i", "army",
     "Army Correspondence Course Program subcourse MD0588, edition 200",
     "Environmental Diseases and Injuries 1 (Army subcourse MD0588, edition 200, 2007)",
     AMEDD, "md-0588-environmental-diseases-and-injuries-i-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0588 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Overview of harmful snake bites and insect stings, harmless snakes and insects, anaphylactic "
     "shock, diagnosis and treatment of hepatitis.", "ia"),
    ("medical", "accp_md0501_dental_anatomy_and_physiology", "army",
     "Army Correspondence Course Program subcourse MD0501, edition 200",
     "Dental Anatomy and Physiology (Army subcourse MD0501, edition 200, 2006)",
     AMEDD, "md-0501-dental-anatomy-and-physiology-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0501 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Human anatomy in general; oral anatomy to include teeth, mandible, maxilla, muscles, glands, and "
     "joints; anatomy of permanent maxillary and mandibular teeth.", "ia"),
    ("medical", "accp_md0502_dental_materials", "army",
     "Army Correspondence Course Program subcourse MD0502, edition 200",
     "Dental Materials (Army subcourse MD0502, edition 200, 2006)",
     AMEDD, "md-0502-dental-materials-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0502 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Composition, properties, and characteristics of dental materials; and principles of manipulation "
     "of these materials.", "ia"),
    ("medical", "accp_md0503_dental_instrument_setups", "army",
     "Army Correspondence Course Program subcourse MD0503, edition 200",
     "Dental Instrument Setups (Army subcourse MD0503, edition 200, 2006)",
     AMEDD, "md-0503-dental-instrument-setups-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0503 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Recognition, care, use and setup of instruments for basic examination, anesthesia, restoration, "
     "surgery, periodontics, endodontics, and prosthodontics.", "ia"),
    ("medical", "accp_md0509_infection_control_and_drugs_in_the_dental_clinic", "army",
     "Army Correspondence Course Program subcourse MD0509, edition 200",
     "Infection Control and Drugs in the Dental Clinic (Army subcourse MD0509, edition 200, 2006)",
     AMEDD, "md-0509-infection-control-and-drugs-in-the-dental-clinic-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0509 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Procedures for protection against infection; sterilization, disinfection, and storage; drugs "
     "commonly used in dentistry.", "ia"),
    ("medical", "accp_md0510_general_duties_of_the_dental_specialist", "army",
     "Army Correspondence Course Program subcourse MD0510, edition 200",
     "General Duties of the Dental Specialist (Army subcourse MD0510, edition 200, 2006)",
     AMEDD, "md-0510-general-duties-of-the-dental-specialist-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0510 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Attributes of a good dental specialist; clinical routine, administrative functions, and supply "
     "procedures; team approach to four- handed dentistry.", "ia"),
    ("medical", "accp_md0511_oral_and_maxillofacial_pathology", "army",
     "Army Correspondence Course Program subcourse MD0511, edition 200",
     "Oral and Maxillofacial Pathology (Army subcourse MD0511, edition 200, 2006)",
     AMEDD, "md-0511-oral-and-maxillofacial-pathology-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0511 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Diseases of hard and soft tissues of the mouth and teeth.", "ia"),
    ("medical", "accp_md0512_dental_radiography", "army",
     "Army Correspondence Course Program subcourse MD0512, edition 200",
     "Dental Radiography (Army subcourse MD0512, edition 200, 2006)",
     AMEDD, "md-0512-dental-radiography-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0512 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Principles of dental radiography; hazards and safety precautions; production of dental "
     "radiographs; anatomical landmarks; radiographic exposure techniques.", "ia"),
    ("medical", "accp_md0513_preventive_dentistry", "army",
     "Army Correspondence Course Program subcourse MD0513, edition 200",
     "Preventive Dentistry (Army subcourse MD0513, edition 200, 2006)",
     AMEDD, "md-0513-preventive-dentistry-edition-200", 2006, "pdf",
     "The Army's self-study subcourse MD0513 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Fundamental concepts of the Preventive Dentistry Program and the clinical and home-care "
     "procedures used in administering the Program. Technical nomenclature used in the oral examination, "
     "prophylaxis, fluoridation, and education of the dental patient.", "ia"),
    ("medical", "accp_md0801_prescription_interpretation", "army",
     "Army Correspondence Course Program subcourse MD0801, edition 200",
     "Prescription Interpretation (Army subcourse MD0801, edition 200, 2007)",
     AMEDD, "md-0801-prescription-interpretation-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0801 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Terms, abbreviations, and symbols commonly seen on prescriptions brought to the pharmacy. "
     "Authorized prescription forms are presented and the component parts of each are discussed. The emphasis of "
     "the subcourse is on the actual interpretation of prepared prescription forms.", "ia"),
    ("medical", "accp_md0802_pharmaceutical_calculations", "army",
     "Army Correspondence Course Program subcourse MD0802, edition 100",
     "Pharmaceutical Calculations (Army subcourse MD0802, edition 100, 2001)",
     AMEDD, "md-0802-pharmaceutical-calculations-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0802 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Types of calculations most often performed in the pharmacy. Review of basic mathematics, ratio "
     "and proportion principles, the metric system, percentage preparations, reduction and enlargement of formulas, "
     "and dosage calculations are only a few examples of topics addressed in the subcourse. The student is required "
     "to become actively involved in the learning process by solving realistic problems involving pharmaceutical "
     "preparations.", "ia"),
    ("medical", "accp_md0803_general_chemistry", "army",
     "Army Correspondence Course Program subcourse MD0803, edition 100",
     "General Chemistry (Army subcourse MD0803, edition 100, 2003)",
     AMEDD, "md-0803-general-chemistry-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0803 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Basic concepts related to inorganic and organic chemistry. It provides the learner with these "
     "concepts in order that the understanding of certain topics (e. g., drug therapy) in the medical field can be "
     "enhanced. Chemical nomenclature, chemical reactions, acids, bases, and salts are only a few examples of "
     "material discussed in the subcourse.", "ia"),
    ("medical", "accp_md0804_therapeutics_i", "army",
     "Army Correspondence Course Program subcourse MD0804, edition 200",
     "Therapeutics I (Army subcourse MD0804, edition 200, 2007)",
     AMEDD, "md-0804-therapeutics-i-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0804 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. First in a series of five subcourses that deal with pharmacology. Include concepts of anatomy "
     "and physiology which lead to a more in-depth understanding of the pharmacological concepts discussed. "
     "Emphasis is placed upon current drug therapy (indications, uses, side effects, and contraindications of "
     "medications). Professional references in pharmacy; anatomy, physiology, and pathology principles important to "
     "pharmacology; the central nervous system; local anesthetic agents and central nervous system "
     "stimulants.", "ia"),
    ("medical", "accp_md0805_therapeutics_ii", "army",
     "Army Correspondence Course Program subcourse MD0805, edition 200",
     "Therapeutics 2 (Army subcourse MD0805, edition 200, 2007)",
     AMEDD, "md-0805-therapeutics-ii-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0805 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Pharmacology related to the human nervous and muscular systems. Review of the principles of "
     "anatomy and physiology related to the nervous and muscular systems. Skeletal muscle relaxants; analgesics, "
     "anti-inflammatory agents, and anti-gout agents; adrenergic agents; adrenergic blocking agents; cholinergic "
     "agents; and cholinergic blocking agents.", "ia"),
    ("medical", "accp_md0806_therapeutics_iii", "army",
     "Army Correspondence Course Program subcourse MD0806, edition 200",
     "Therapeutics 3 (Army subcourse MD0806, edition 200, 2007)",
     AMEDD, "md-0806-therapeutics-iii-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0806 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Pharmacology related to the human circulatory, respiratory, and urinary systems. The anatomy and "
     "physiology of these systems is discussed in relation to pharmacology. Respiratory drugs, cardiac drugs, "
     "vasodilator agents, anti-hypertensive agents, and diuretic and antidiuretic agents.", "ia"),
    ("medical", "accp_md0807_pharmacology_iv", "army",
     "Army Correspondence Course Program subcourse MD0807, edition 100",
     "Pharmacology 4 (Army subcourse MD0807, edition 100, 2006)",
     AMEDD, "md-0807-pharmacology-iv-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0807 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Pharmacology related to the digestive and endocrine systems of the body. The anatomy and "
     "physiology of these systems is discussed in relation to pharmacology. Antacid and digestant agents; emetic, "
     "antiemetic, and antidiarrheal agents; cathartic agents; thyroid, antithyroid, and parathyroid agents; and "
     "reproductive hormones and oral contraceptives.", "ia"),
    ("medical", "accp_md0808_pharmacology_v", "army",
     "Army Correspondence Course Program subcourse MD0808, edition 100",
     "Pharmacology 5 (Army subcourse MD0808, edition 100, 2006)",
     AMEDD, "md-0808-pharmacology-v-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0808 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Agents used to treat various medical conditions. Categories include: an introduction to "
     "microbiology; intestinal parasites and antiparasitic agents; antibiotics and sulfonamides; antifungals, "
     "antihistamines, and antimalarial agents; biologicals; and vitamins and minerals.", "ia"),
    ("medical", "accp_md0809_intorduction_to_compounding", "army",
     "Army Correspondence Course Program subcourse MD0809, edition 200",
     "Intorduction to Compounding (Army subcourse MD0809, edition 200, 2007)",
     AMEDD, "md-0809-intorduction-to-compounding-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0809 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. This subcourse discusses the principles involved in compounding individual prescriptions and in "
     "manufacturing bulk quantities of pharmaceutical preparations. Classes of preparations (e. g., elixirs) are "
     "discussed with emphasis on their preparation and uses in the pharmacy.", "ia"),
    ("medical", "accp_md0811_inpatient_dispensing", "army",
     "Army Correspondence Course Program subcourse MD0811, edition 100",
     "Inpatient Dispensing (Army subcourse MD0811, edition 100, 2006)",
     AMEDD, "md-0811-inpatient-dispensing-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0811 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Dispensing of medications using the ward issue and unit dose systems; advantages and "
     "disadvantages of each; usage of forms (including the patient medication profile); packaging, labeling, and "
     "delivery. Preparation of sterile products, including usage and maintenance of the laminar airflow hood, the "
     "sterile product order form, production techniques, and work counts.", "ia"),
    ("medical", "accp_md0837_laboratory_mathematics", "army",
     "Army Correspondence Course Program subcourse MD0837, edition 200",
     "Laboratory Mathematics (Army subcourse MD0837, edition 200, 2007)",
     AMEDD, "md-0837-laboratory-mathematics-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0837 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. General mathematics review (real numbers, equality, significant figures, rounding, scientific "
     "notation, logarithms); solution mathematics; molar solutions; equivalent solutions; conversion of "
     "concentration units; dilutions; titration; concentrated acids and bases; pH and buffers.", "ia"),
    ("medical", "accp_md0841_parasitology_i", "army",
     "Army Correspondence Course Program subcourse MD0841, edition 200",
     "Parasitology 1 (Army subcourse MD0841, edition 200, 2007)",
     AMEDD, "md-0841-parasitology-i-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0841 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to Parasitology. First of two subcourses dealing with parasitology for laboratory "
     "specialists. Overview of parasitology procedures for collecting, preserving and processing clinical "
     "specimens, and microscopy.", "ia"),
    ("medical", "accp_md0845_immunohematology_and_blood_banking_i", "army",
     "Army Correspondence Course Program subcourse MD0845, edition 100",
     "Immunohematology and Blood Banking 1 (Army subcourse MD0845, edition 100, 2006)",
     AMEDD, "md-0845-immunohematology-and-blood-banking-i-edition-100", 2006, "pdf",
     "The Army's self-study subcourse MD0845 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Collection, processing, storage, and shipment of human blood; blood banks; transfusions; "
     "immunogenics (genetic determination of blood group antigens and their ramifications).", "ia"),
    ("medical", "accp_md0852_urinalysis", "army", "Army Correspondence Course Program subcourse MD0852, edition 200",
     "Urinalysis (Army subcourse MD0852, edition 200, 2005)",
     AMEDD, "md-0852-urinalysis-edition-200", 2005, "pdf",
     "The Army's self-study subcourse MD0852 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Laboratory methods commonly used in the collection and preservation of urine and in the "
     "detection of normal and abnormal constituents of urine. Photomicrographs and line-drawings illustrate the "
     "normal and abnormal sediments commonly seen in the microscopic examination of patient urine samples.", "ia"),
    ("medical", "accp_md0853_hematology_i", "army",
     "Army Correspondence Course Program subcourse MD0853, edition 200",
     "Hematology 1 (Army subcourse MD0853, edition 200, 2007)",
     AMEDD, "md-0853-hematology-i-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0853 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Laboratory studies which concern the composition of blood and the formation, maturation, and "
     "function of blood cells. Morphology, cell counts, and methods commonly used in hematology are also "
     "discussed.", "ia"),
    ("medical", "accp_md0856_bacteriology", "army",
     "Army Correspondence Course Program subcourse MD0856, edition 200",
     "Bacteriology (Army subcourse MD0856, edition 200, 2007)",
     AMEDD, "md-0856-bacteriology-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0856 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Principles, methods, and procedures used in cultivating, isolating, and identifying bacteria of "
     "clinical importance.", "ia"),
    ("medical", "accp_md0857_hematology_ii", "army",
     "Army Correspondence Course Program subcourse MD0857, edition 200",
     "Hematology 2 (Army subcourse MD0857, edition 200, 2007)",
     AMEDD, "md-0857-hematology-ii-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0857 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Laboratory procedures including differential leukocyte counts, blood coagulation studies, and "
     "equipment automation procedures.", "ia"),
    ("medical", "accp_md0861_clinical_chemistry_i", "army",
     "Army Correspondence Course Program subcourse MD0861, edition 200",
     "Clinical Chemistry 1 (Army subcourse MD0861, edition 200, 2007)",
     AMEDD, "md-0861-clinical-chemistry-i-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0861 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. First in a series of five subcourses dealing with the modern practice of clinical chemistry. "
     "Introduction to laboratory safety, the measurement of weights and volumes, laboratory chemicals, laboratory "
     "mathematics, the collection and handling of specimens, quality control, and organic chemistry.", "ia"),
    ("medical", "accp_md0863_clinical_chemistry_ii", "army",
     "Army Correspondence Course Program subcourse MD0863, edition 200",
     "Clinical Chemistry 2 (Army subcourse MD0863, edition 200, 2007)",
     AMEDD, "md-0863-clinical-chemistry-ii-edition-200", 2007, "pdf",
     "The Army's self-study subcourse MD0863 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Carbohydrates, lipids, and proteins and their importance in medicine. Specific procedures and "
     "techniques for the determination of these substances.", "ia"),
    ("medical", "accp_md0151_principles_of_epidemiology_and_microbiology", "army",
     "Army Correspondence Course Program subcourse MD0151, edition 100",
     "Principles of Epidemiology and Microbiology (Army subcourse MD0151, edition 100, 2003)",
     AMEDD, "md-0151-principles-of-epidemiology-and-microbiology-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0151 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to disease transmission; basic terminology and principles of epidemiology; "
     "fundamentals of microbiology; structure of the cell; morphology and physiology of bacteria, viruses, "
     "rickettsiae, fungi, protozoa, and helminths; practical application of microbiology in environmental "
     "health.", "ia"),
    ("medical", "accp_md0152_diseases_of_military_importance", "army",
     "Army Correspondence Course Program subcourse MD0152, edition 100",
     "Diseases of Military Importance (Army subcourse MD0152, edition 100, 2001)",
     AMEDD, "md-0152-diseases-of-military-importance-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0152 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Epidemiology, prevention, and control of selected diseases of military importance; prevention of "
     "injuries due to environmental extremes; the Army immunization program.", "ia"),
    ("medical", "accp_md0162_solid_waste_disposal", "army",
     "Army Correspondence Course Program subcourse MD0162, edition 100",
     "Solid Waste Disposal (Army subcourse MD0162, edition 100, 2001)",
     AMEDD, "md-0162-solid-waste-disposal-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0162 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Responsibilities for and public health significance of solid waste disposal at military "
     "installations; types of solid wastes generated at large and small installations and methods of collection and "
     "disposal; solid wastes generated in the field and methods and devices for their disposal; role of the "
     "preventive medicine specialist in solid waste disposal.", "ia"),
    ("medical", "accp_md0164_environmental_health_inspections_and_surveys_i", "army",
     "Army Correspondence Course Program subcourse MD0164, edition 100",
     "Environmental Health Inspections and Surveys 1 (Army subcourse MD0164, edition 100, 2001)",
     AMEDD, "md-0164-environmental-health-inspections-and-surveys-i-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0164 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Introduction to environmental health inspections; inspection procedures and public health "
     "aspects of troop housing, mobile home parks, and barber and beauty shops.", "ia"),
    ("medical", "accp_md0165_occupational_health_and_industrial_hygiene", "army",
     "Army Correspondence Course Program subcourse MD0165, edition 100",
     "Occupational Health and Industrial Hygiene (Army subcourse MD0165, edition 100, 2002)",
     AMEDD, "md-0165-occupational-health-and-industrial-hygiene-edition-100", 2002, "pdf",
     "The Army's self-study subcourse MD0165 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. An introduction to the science and art of preserving health through the recognition, evaluation, "
     "and control of environmental causes and sources of occupational health hazards in the workplace, to include "
     "occupational diseases and hazards, criteria, industrial hygiene principles, sampling, personal protective "
     "equipment and engineering control methods.", "ia"),
    ("medical", "accp_md0166_environmental_health_inspections_and_surveys_ii", "army",
     "Army Correspondence Course Program subcourse MD0166, edition 100",
     "Environmental Health Inspections and Surveys 2 (Army subcourse MD0166, edition 100, 2002)",
     AMEDD, "md-0166-environmental-health-inspections-and-surveys-ii-edition-100", 2002, "pdf",
     "The Army's self-study subcourse MD0166 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Environmental health inspections procedures and the public health aspects of swimming pools, "
     "child care centers, ice houses, and various public use facilities.", "ia"),
    ("medical", "accp_md0170_arthropod_identification_and_surveys", "army",
     "Army Correspondence Course Program subcourse MD0170, edition 100",
     "Arthropod Identification and Surveys (Army subcourse MD0170, edition 100, 2003)",
     AMEDD, "md-0170-arthropod-identification-and-surveys-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0170 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Biology and life cycles of medically important arthropods; types and methodology of arthropod "
     "surveys; collection, mounting, and identification of arthropods to evaluate actual or potential military "
     "importance of suspected infestations; field identification and sorting of medically important arthropods; "
     "preservation, mounting, and shipping technique; mosquito larval taxonomy and malaria survey "
     "technique.", "ia"),
    ("medical", "accp_md0171_arthropod_control", "army",
     "Army Correspondence Course Program subcourse MD0171, edition 100",
     "Arthropod Control (Army subcourse MD0171, edition 100, 2001)",
     AMEDD, "md-0171-arthropod-control-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0171 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Control procedures for the major group of medically important arthropods with emphasis on the "
     "preventive environmental means available for specific groups. In-depth discussion of manual and power pest "
     "control equipment, its nomenclature, uses, operation, and maintenance.", "ia"),
    ("medical", "accp_md0172_rodent_biology_survey_and_control", "army",
     "Army Correspondence Course Program subcourse MD0172, edition 100",
     "Rodent Biology, Survey, and Control (Army subcourse MD0172, edition 100, 2003)",
     AMEDD, "md-0172-rodent-biology-survey-and-control-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0172 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Biology and life history of principal domestic rodents; military medical and economic "
     "importance; identification and survey techniques; sanitary, environmental, physical, and chemical control "
     "measures.", "ia"),
    ("medical", "accp_md0173_pesticides_in_the_military", "army",
     "Army Correspondence Course Program subcourse MD0173, edition 100",
     "Pesticides in the Military (Army subcourse MD0173, edition 100, 2001)",
     AMEDD, "md-0173-pesticides-in-the-military-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0173 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Classification of pesticides and their physiological effects on pests and man; pesticide "
     "formulations, mixing, and dilution calculations; proper methods of storage, handling, and disposal of "
     "pesticides; toxicity and first aid; impact of pesticides on the environment.", "ia"),
    ("medical", "accp_md0904_pharmacology_math_for_the_practical_nurse", "army",
     "Army Correspondence Course Program subcourse MD0904, edition 100",
     "Pharmacology Math for the Practical Nurse (Army subcourse MD0904, edition 100, 2004)",
     AMEDD, "md-0904-pharmacology-math-for-the-practical-nurse-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0904 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Basic math skills (addition, subtraction, multiplication, division, fractions, decimals, "
     "percentages, and ratio and proportion); systems of measurement; computing medication dosages; computing "
     "intravenous infusion rates; and basic dose calculations.", "ia"),
    ("medical", "accp_md0905_nursing_fundamentals_i", "army",
     "Army Correspondence Course Program subcourse MD0905, edition 100",
     "Nursing Fundamentals 1 (Army subcourse MD0905, edition 100, 2002)",
     AMEDD, "md-0905-nursing-fundamentals-i-edition-100", 2002, "pdf",
     "The Army's self-study subcourse MD0905 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Patient relations including basic human needs, communication skills, stress and hospitalization, "
     "and transcultural factors influencing nursing care; the adult patient care unit; advanced principles of "
     "patient hygiene; body mechanics; positioning and ambulating the adult patient; and medical "
     "isolation.", "ia"),
    ("medical", "accp_md0906_nursing_fundamentals_ii", "army",
     "Army Correspondence Course Program subcourse MD0906, edition 100",
     "Nursing Fundamentals 2 (Army subcourse MD0906, edition 100, 2004)",
     AMEDD, "md-0906-nursing-fundamentals-ii-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0906 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Assisting with the physical examination, specimen collection, catheterization of the male and "
     "female patient, vital signs, diet therapy, physical assessment, role of the practical nurse, and "
     "perioperative care.", "ia"),
    ("medical", "accp_md0910_introduction_to_practical_nursing", "army",
     "Army Correspondence Course Program subcourse MD0910, edition 200",
     "Introduction to Practical Nursing (Army subcourse MD0910, edition 200, 2002)",
     AMEDD, "md-0910-introduction-to-practical-nursing-edition-200", 2002, "pdf",
     "The Army's self-study subcourse MD0910 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Discussion of the role of the 91WM6 practical nurse within the AMD0D. Descriptions of the "
     "practical nurse resident course and preparatory correspondence course. Duties and responsibilities of the "
     "practical nurse in the areas of soldiering, leadership, management, and clinical practice.", "ia"),
    ("medical", "accp_md0913_drug_dosage_and_therapy", "army",
     "Army Correspondence Course Program subcourse MD0913, edition 100",
     "Drug Dosage and Therapy (Army subcourse MD0913, edition 100, 2002)",
     AMEDD, "md-0913-drug-dosage-and-therapy-edition-100", 2002, "pdf",
     "The Army's self-study subcourse MD0913 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Interpreting medical orders. The metric and apothecary systems. Dose calculations Introduction "
     "to basic pharmacology. Antiseptics and disinfectants, respiratory drugs, central nervous system drugs, "
     "autonomic and cardiovascular drugs, and drugs used to prevent and/or treat infections.", "ia"),
    ("medical", "accp_md0915_nursing_care_of_the_surgical_patient", "army",
     "Army Correspondence Course Program subcourse MD0915, edition 100",
     "Nursing Care of the Surgical Patient (Army subcourse MD0915, edition 100, 2001)",
     AMEDD, "md-0915-nursing-care-of-the-surgical-patient-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0915 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Preoperative, operating room, recovery room, and postoperative care of the surgical "
     "patient.", "ia"),
    ("medical", "accp_md0916_nursing_care_related_to_the_musculoskeletal_syst", "army",
     "Army Correspondence Course Program subcourse MD0916, edition 100",
     "Nursing Care Related to the Musculoskeletal System (Army subcourse MD0916, edition 100, 2003)",
     AMEDD, "md-0916-nursing-care-related-to-the-musculoskeletal-system-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0916 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Patient assessment techniques, special orthopedic equipment, mobilization aids, care of patients "
     "with casts and traction, care of patients with contusions, sprains, strains, dislocations, fractures, and "
     "amputation.", "ia"),
    ("medical", "accp_md0917_nursing_care_related_to_the_cardiovascular_and_r", "army",
     "Army Correspondence Course Program subcourse MD0917, edition 100",
     "Nursing Care Related to the Cardiovascular and Respiratory Systems (Army subcourse MD0917, edition 100, "
     "2002)",
     AMEDD, "md-0917-nursing-care-related-to-the-cardiovascular-and-respiratory-systems-edition-100", 2002, "pdf",
     "The Army's self-study subcourse MD0917 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology, diagnostic procedures, physical examination, C–V disorders, sudden "
     "cardiac death, nursing management of respiratory disorders, and pulmonary drainage.", "ia"),
    ("medical", "accp_md0918_nursing_care_related_to_the_gastrointestinal_and", "army",
     "Army Correspondence Course Program subcourse MD0918, edition 100",
     "Nursing Care Related to the Gastrointestinal and Urinary Systems (Army subcourse MD0918, edition 100, 2003)",
     AMEDD, "md-0918-nursing-care-related-to-the-gastrointestinal-and-urinary-systems-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0918 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Anatomy and physiology, patient assessment techniques, diagnostic procedures, gastrointestinal "
     "intubation, gavage, lavage, gastrostomy, ileostomy, colostomy, gastrointestinal disorders, diabetes, urinary "
     "catheterization and drainage, urinary tract infections, disorders of the urinary system, renal "
     "failure.", "ia"),
    ("medical", "accp_md0919_nursing_care_related_to_the_sensory_and_neurolog", "army",
     "Army Correspondence Course Program subcourse MD0919, edition 100",
     "Nursing Care Related to the Sensory and Neurological Systems (Army subcourse MD0919, edition 100, 2004)",
     AMEDD, "md-0919-nursing-care-related-to-the-sensory-and-neurological-systems-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0919 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Patient assessment techniques, disorders of the eye and ear, treatment for the eye and ear, care "
     "of the unconscious patient, infectious and degenerative disorders of one nervous system, head and spine "
     "injuries, and disorders of the brain and cranial nerves.", "ia"),
    ("medical", "accp_md0921_obstetric_newborn_care_i", "army",
     "Army Correspondence Course Program subcourse MD0921, edition 200",
     "Obstetric & Newborn Care 1 (Army subcourse MD0921, edition 200, 2003)",
     AMEDD, "md-0921-obstetric-newborn-care-i-edition-200", 2003, "pdf",
     "The Army's self-study subcourse MD0921 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Reproductive anatomy and physiology, embryology and fetal development, diagnosis of pregnancy, "
     "psychologic needs during pregnancy, physiologic changes during pregnancy, prenatal care during pregnancy, "
     "personal hygiene and care during pregnancy, minor discomforts of pregnancy, patient education during "
     "pregnancy, and fetal positions.", "ia"),
    ("medical", "accp_md0922_obstetric_newborn_care_ii", "army",
     "Army Correspondence Course Program subcourse MD0922, edition 100",
     "Obstetric & Newborn Care 2 (Army subcourse MD0922, edition 100, 2004)",
     AMEDD, "md-0922-obstetric-newborn-care-ii-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0922 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Stages of labor and nursing care, precipitate and emergency delivery, management of obstetric "
     "discomfort during labor, special situations in labor and delivery, changes of the postpartal patient, "
     "psychological needs of the postpartal patient, complications of postpartum, characteristics of the typical "
     "newborn infant, care of the normal newborn following delivery, newborn nutrition, the premature infant, and "
     "the sick neonate.", "ia"),
    ("medical", "accp_md0923_introduction_to_operating_room", "army",
     "Army Correspondence Course Program subcourse MD0923, edition 100",
     "Introduction to Operating Room (Army subcourse MD0923, edition 100, 2004)",
     AMEDD, "md-0923-introduction-to-operating-room-edition-100", 2004, "pdf",
     "The Army's self-study subcourse MD0923 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Layout of surgical suite; operating room (OR) team, schedule, ethics and relationships, legal "
     "factors, bereavement. OR furniture and equipment; housekeeping; surgical nomenclature; OR policies; "
     "hazards.", "ia"),
    ("medical", "accp_md0933_scrub_gown_and_glove_procedures", "army",
     "Army Correspondence Course Program subcourse MD0933, edition 100",
     "Scrub, Gown, and Glove Procedures (Army subcourse MD0933, edition 100, 2001)",
     AMEDD, "md-0933-scrub-gown-and-glove-procedures-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0933 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Principles, procedures, and techniques for scrubbing and donning sterile gown and "
     "gloves.", "ia"),
    ("medical", "accp_md0935_routine_procedures_for_an_operation", "army",
     "Army Correspondence Course Program subcourse MD0935, edition 100",
     "Routine Procedures for an Operation (Army subcourse MD0935, edition 100, 2001)",
     AMEDD, "md-0935-routine-procedures-for-an-operation-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0935 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Procedures for the scrub and the circulator before, during, and after an operation. Procedure "
     "for cleanup following a case.", "ia"),
    ("medical", "army_is0871_combat_lifesaver_course_2012", "army", "Interschool subcourse IS0871, edition C",
     "Combat Lifesaver Course: Student Self-Study (Army subcourse IS0871, edition C, 2012)",
     "US Army Medical Department Center and School",
     "combat-lifesaver-course-student-self-study-is-0871-edition-c", 2012, "record",
     "The Army's combat lifesaver course for soldiers who are not medics, the student's self-study book, "
     "read whole.", "ia"),
    ("medical", "army_is0877_self_aid_buddy_aid_2005", "army", "Interschool subcourse IS0877, edition A",
     "Self Aid, Buddy Aid (Army subcourse IS0877, edition A, 2005)",
     ARMY, "is-0877-self-aid-buddy-aid-edition-a", 2005, "pdf",
     "The Army's self-aid and buddy-aid subcourse: first aid a soldier gives himself or a comrade, read "
     "whole.", "ia"),
    ("medical", "army_fm_4_02_17_preventive_medicine_services_2000", "army", "FM 4-02.17",
     "Preventive Medicine Services (FM 4-02.17, 2000)",
     ARMY, "fm-4-02.17-preventative-medicine-services-2000", 2000, "printed",
     "The Army's field manual of preventive medicine services, read whole. Its parts: Medical threat; Role of the "
     "soldier and unit leader; Preventive medicine staff; Preventive medicine detachments and activities; "
     "Preventive medicine detachment mobilization; Preventive medicine services in stability; Preventive medicine "
     "reports; Medical surveillance; Planning/preparations for preventive; Army force xxi preventive medicine "
     "support; Conduct aerial spray operations; Conduct an entomological survey; Preventive medicine site survey "
     "checklist; Training procedures guide; Strategic deployability data for the medical.", "ia"),
    ("medical", "army_tb_med_508_cold_weather_injuries_2005", "army", "TB MED 508",
     "Prevention and Management of Cold-Weather Injuries (TB MED 508, 2005)",
     ARMY, "ost-military-medical-tbmed508", 2005, "printed",
     "The Army's bulletin on preventing and managing cold-weather injuries, read whole. Its parts: Physiologic "
     "responses and adaptations to cold; Cold stress management; Cold weather deployment tips; Risk management "
     "steps for preventing cold casualties; Extended cold weather clothing system.", "ia"),
    # ---------------------------------------------------------------- mechanics
    ("mech", "accp_od1001_wheeled_vehicle_engines", "army", "Army Correspondence Course Program subcourse OD1001",
     "Wheeled Vehicle Engines (Army subcourse OD1001, 2004)",
     ACCP, "od-1001-wheeled-vehicle-engines", 2004, "pdf",
     "The Army's self-study subcourse OD1001 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The fundamentals of spark ignition and compression ignition engines; inspecting, testing, and "
     "troubleshooting procedures for engines; principles of engine lubrication and crankcase ventilation systems; "
     "and the principles of engine liquid cooling systems.", "ia"),
    ("mech", "accp_od1002_wheeled_vehicle_electrical_systems_part_i", "army",
     "Army Correspondence Course Program subcourse OD1002",
     "Wheeled Vehicle Electrical Systems Part 1 (Army subcourse OD1002, 2004)",
     ACCP, "od-1002-wheeled-vehicle-electrical-systems-part-i", 2004, "pdf",
     "The Army's self-study subcourse OD1002 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The fundamentals of automotive electrical systems to include circuits, batteries; and the "
     "fundamentals and use of electrical test equipment.", "ia"),
    ("mech", "accp_od1003_wheeled_vehicle_electrical_systems_part_ii", "army",
     "Army Correspondence Course Program subcourse OD1003",
     "Wheeled Vehicle Electrical Systems Part 2 (Army subcourse OD1003, 2004)",
     ACCP, "od-1003-wheeled-vehicle-electrical-systems-part-ii", 2004, "pdf",
     "The Army's self-study subcourse OD1003 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The principles of AC and DC generators and regulators; the application of the fundamentals of "
     "electricity to starting system components and to the components of wheeled vehicle battery ignition systems; "
     "and the principles of vehicle electrical accessory systems.", "ia"),
    ("mech", "accp_od1004_wheeled_vehicle_fuel_and_exhaust_system", "army",
     "Army Correspondence Course Program subcourse OD1004, edition 6",
     "Wheeled Vehicle Fuel and Exhaust System (Army subcourse OD1004, edition 6, 2004)",
     ACCP, "od-1004-wheeled-vehicle-fuel-and-exhaust-system-edition-6", 2004, "pdf",
     "The Army's self-study subcourse OD1004 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The fundamentals of gasoline engine fuel systems, compression ignition engine fuel systems, and "
     "engine exhaust systems.", "ia"),
    ("mech", "accp_od1005_introduction_to_wheeled_vehicle_clutches_transmi", "army",
     "Army Correspondence Course Program subcourse OD1005",
     "Introduction to Wheeled Vehicle Clutches, Transmission, and Transfers (Army subcourse OD1005, 2004)",
     ACCP, "od-1005-introduction-to-wheeled-vehicle-clutches-transmission-and-transfers", 2004, "pdf",
     "The Army's self-study subcourse OD1005 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The fundamentals of gears and gear trains, friction type clutches, manual transmissions, and power "
     "take-offs, automatic transmissions, and transfer cases.", "ia"),
    ("mech", "accp_od1006_wheeled_vehicle_drive_lines_axles_and_suspension", "army",
     "Army Correspondence Course Program subcourse OD1006, edition 6",
     "Wheeled Vehicle Drive Lines, Axles, and Suspension Systems (Army subcourse OD1006, edition 6, 2004)",
     ACCP, "od-1006-wheeled-vehicle-drive-lines-axles-and-suspension-systems-edition-6", 2004, "pdf",
     "The Army's self-study subcourse OD1006 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The construction, operation, and maintenance of propeller shafts and universal joints; the "
     "construction, operation, lubrication, and maintenance of axle assemblies; types and principles of axle "
     "shafts; principles of bevel gear differentials; and the construction, operation, and maintenance of springs, "
     "shock absorbers, frames, bogie suspension systems, tires, and wheels.", "ia"),
    ("mech", "accp_od1007_wheeled_vehicle_steering_systems", "army",
     "Army Correspondence Course Program subcourse OD1007, edition A",
     "Wheeled Vehicle Steering Systems (Army subcourse OD1007, edition A, 2004)",
     ACCP, "od-1007-wheeled-vehicle-steering-systems-edition-a", 2004, "pdf",
     "The Army's self-study subcourse OD1007 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The construction, operation, and inspection of mechanical steering linkages and the principles of "
     "steering geometry; and the principles, operation, construction, and inspection of power steering "
     "systems.", "ia"),
    ("mech", "accp_od1008_wheeled_vehicle_braking_systems", "army",
     "Army Correspondence Course Program subcourse OD1008",
     "Wheeled Vehicle Braking Systems (Army subcourse OD1008, 2004)",
     ACCP, "od-1008-wheeled-vehicle-braking-systems", 2004, "pdf",
     "The Army's self-study subcourse OD1008 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The principles of automotive brake systems and the construction and operation of mechanical and "
     "hydraulic brake systems; the principles, construction, and operation of air-hydraulic brake systems and "
     "straight air brake systems.", "ia"),
    ("mech", "accp_od1401_precision_measuring_instruments", "army",
     "Army Correspondence Course Program subcourse OD1401, edition 9",
     "Precision Measuring Instruments (Army subcourse OD1401, edition 9, 2006)",
     ACCP, "od-1401-precision-measuring-instruments-edition-9", 2006, "pdf",
     "The Army's self-study subcourse OD1401 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The proper care, storage, and handling of the vernier caliper, the outside micrometer, and the depth "
     "micrometer; and interpreting readings on and taking measurements with these instruments.", "ia"),
    ("mech", "accp_od1402_basic_oscilloscope", "army",
     "Army Correspondence Course Program subcourse OD1402, edition 9",
     "Basic Oscilloscope (Army subcourse OD1402, edition 9, 2004)",
     ACCP, "od-1402-basic-oscilloscope-edition-9", 2004, "pdf",
     "The Army's self-study subcourse OD1402 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The controls, indicators, and the initial set-up procedures, and the proper procedures for measuring "
     "voltage amplitude and frequency using the screen grids of the AN/USM–281C oscilloscope.", "ia"),
    ("mech", "accp_od1619_principles_of_internal_combustion_engines", "army",
     "Army Correspondence Course Program subcourse OD1619, edition 8",
     "Principles of Internal Combustion Engines (Army subcourse OD1619, edition 8, 2004)",
     ACCP, "od-1619-principles-of-internal-combustion-engines-editon-8", 2004, "pdf",
     "The Army's self-study subcourse OD1619 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The principles, components, and operation of gasoline and diesel engines, turbochargers and intake, "
     "exhaust, lubrication, and cooling systems.", "ia"),
    ("mech", "accp_od1620_principles_of_gasoline_and_diesel_fuel_systems", "army",
     "Army Correspondence Course Program subcourse OD1620, edition 7",
     "Principles of Gasoline and Diesel Fuel Systems (Army subcourse OD1620, edition 7, 2004)",
     ACCP, "od-1620-principles-of-gasoline-and-diesel-fuel-systems-edition-7", 2004, "pdf",
     "The Army's self-study subcourse OD1620 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. Function and construction of gasoline and diesel fuel systems.", "ia"),
    ("mech", "accp_od1640_machine_shop_calculation", "army",
     "Army Correspondence Course Program subcourse OD1640, edition 7",
     "Machine Shop Calculation (Army subcourse OD1640, edition 7, 2004)",
     ACCP, "od-1640-machine-shop-calculation-edition-7", 2004, "pdf",
     "The Army's self-study subcourse OD1640 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. Procedures for solving problems involving addition, subtraction, multiplication and division of "
     "fractions and decimals, and conversion of fractions to decimals and decimals to fractions; conversion of "
     "linear measurements from the English to the metric system and vice-versa; and for solving problems using "
     "ratio, proportion, and trigonometry.", "ia"),
    ("mech", "accp_od1641_principles_of_drafting_and_shop_drawings", "army",
     "Army Correspondence Course Program subcourse OD1641, edition 8",
     "Principles of Drafting and Shop Drawings (Army subcourse OD1641, edition 8, 2004)",
     ACCP, "od-1641-principles-of-drafting-and-shop-drawings-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1641 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The principles and fundamentals of drafting and shop drawing to include: orthographic projection, "
     "geometric construction, types of pictorial drawing, dimensioning, and sketching.", "ia"),
    ("mech", "accp_od1642_precision_measuring_and_gaging", "army",
     "Army Correspondence Course Program subcourse OD1642, edition 8",
     "Precision Measuring and Gaging (Army subcourse OD1642, edition 8, 2004)",
     ACCP, "od-1642-precision-measuring-and-gaging-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1642 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The types of fits, tolerances, and allowances; and the proper use and care of precision measuring "
     "tools used in the machinist trade.", "ia"),
    ("mech", "accp_od1643_metal_properties_characteristics_uses_and_codes", "army",
     "Army Correspondence Course Program subcourse OD1643, edition 7",
     "Metal Properties, Characteristics, Uses, and Codes (Army subcourse OD1643, edition 7, 2004)",
     ACCP, "od-1643-metal-properties-characteristics-uses-and-codes-edition-7", 2004, "pdf",
     "The Army's self-study subcourse OD1643 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The physical and mechanical properties and categories of various metals, procedures for using "
     "hardness testers, chemical analysis, bench grinders, simple shop tests, the numerical index system, and color "
     "codes for identifying various metals.", "ia"),
    ("mech", "accp_od1644_milling_machine_operations", "army",
     "Army Correspondence Course Program subcourse OD1644, edition 8",
     "Milling Machine Operations (Army subcourse OD1644, edition 8, 2005)",
     ACCP, "od-1644-milling-machine-operations-edition-8", 2005, "pdf",
     "The Army's self-study subcourse OD1644 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The setup, operation, and adjustments of the milling machine; and the types, nomenclature, and use "
     "of milling cutters.", "ia"),
    ("mech", "accp_od1645_lathe_operations", "army", "Army Correspondence Course Program subcourse OD1645, edition 8",
     "Lathe Operations (Army subcourse OD1645, edition 8, 2004)",
     ACCP, "od-1645-lathe-operations-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1645 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The use of the lathe to include safety; the use, repair, and adjustment of lathe attachments; and "
     "various thread forms, use, calculations, and machining techniques.", "ia"),
    ("mech", "accp_od1646_bandsaw_operations", "army",
     "Army Correspondence Course Program subcourse OD1646, edition 8",
     "Bandsaw Operations (Army subcourse OD1646, edition 8, 2004)",
     ACCP, "od-1646-bandsaw-operations-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1646 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The use of the band saw, to include a functional description of the band saw machine and the methods "
     "used to correctly operate this machine; the procedures used to maintain the band saw machine; and the methods "
     "used to troubleshoot band saw malfunctions.", "ia"),
    ("mech", "accp_od1650_welding_theory", "army", "Army Correspondence Course Program subcourse OD1650, edition 8",
     "Welding Theory (Army subcourse OD1650, edition 8, 2004)",
     ACCP, "od-1650-welding-theory-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1650 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The interpretation and use of welding symbols on shop drawings.", "ia"),
    ("mech", "accp_od1651_welding_operations_i", "army",
     "Army Correspondence Course Program subcourse OD1651, edition 8",
     "Welding Operations, Part 1 (Army subcourse OD1651, edition 8, 2004)",
     ACCP, "od-1651-welding-operations-i-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1651 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. The methods for classifying electrodes by type and intended uses; automotive welding processes, "
     "materials, and identification processes; the types and techniques of joint design; the theory, principles, "
     "and procedures of welding armor plate; the methods of destructive and nondestructive testing of welds; and "
     "troubleshooting procedures.", "ia"),
    ("mech", "accp_od1653_metal_body_repair", "army",
     "Army Correspondence Course Program subcourse OD1653, edition 7",
     "Metal Body Repair (Army subcourse OD1653, edition 7, 2004)",
     ACCP, "od-1653-metal-body-repair-edition-7", 2004, "pdf",
     "The Army's self-study subcourse OD1653 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. Various operations required to repair damaged vehicles and specific operations required to repair "
     "glass, radiators, and fuel tanks.", "ia"),
    ("mech", "accp_od1654_welding_operations_ii", "army",
     "Army Correspondence Course Program subcourse OD1654, edition 8",
     "Welding Operations, Part 2 (Army subcourse OD1654, edition 8, 2004)",
     ACCP, "od-1654-welding-operations-ii-edition-8", 2004, "pdf",
     "The Army's self-study subcourse OD1654 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. Inert gas and gas metal-arc welding principles, operations, equipment, nomenclature, and safety "
     "precautions; and procedures for troubleshooting welding equipment and determining methods of repair.", "ia"),
    ("mech", "accp_od0010_electrical_system_component_repair", "army",
     "Army Correspondence Course Program subcourse OD0010, edition 5",
     "Electrical System Component Repair (Army subcourse OD0010, edition 5, 1988)",
     ACCP, "od-0010-electrical-system-component-repair-edition-5", 1988, "printed",
     "The Army's self-study subcourse OD0010 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. Procedures for testing, overhauling, and adjusting AC and DC charging system components, starter "
     "motors, and personnel heaters; and the use and care of electrical system component test equipment.", "ia"),
    ("mech", "accp_en5260_construction_equipment_repairer_hydraulic_system", "army",
     "Army Correspondence Course Program subcourse EN5260, edition B",
     "Construction Equipment Repairer (Hydraulic Systems) (Army subcourse EN5260, edition B, 1999)",
     ACCP, "en-5260-construction-equipment-repairer-hydraulic-systems-edition-b", 1999, "printed",
     "The Army's self-study subcourse EN5260 (Engineer school), read whole, with its lessons, exercises and "
     "answers. How to adjust and repair hydraulic pumps and valves used on construction equipment. Information on "
     "positive displacement hydraulic pumps and the procedures required to disassemble, repair, and reassemble "
     "them. Also, construction, operation, and repair of hydraulic control valves.", "ia"),
    ("mech", "usmc_mci_automotive_cooling_lubricating_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED258047)",
     "Automotive Cooling and Lubricating Systems (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258047", 1984, "eric",
     "The Marine Corps Institute's correspondence course on vehicle cooling and lubricating systems, read whole, "
     "with its review exercises.", "eric"),
    ("mech", "usmc_mci_heavy_vehicle_preventive_maintenance_1983", "usmc",
     "Marine Corps Institute course (ERIC document ED258050)",
     "Preventive Maintenance and Operating Techniques for Heavy Vehicles (Marine Corps Institute, 1983)",
     MCI, "ERIC_ED258050", 1983, "eric",
     "The Marine Corps Institute's correspondence course on preventive maintenance and driving techniques for heavy "
     "vehicles, read whole, with its review exercises.", "eric"),
    ("mech", "usmc_mci_automotive_fuel_exhaust_1985", "usmc",
     "Marine Corps Institute course (ERIC document ED275868)",
     "Automotive Fuel and Exhaust Systems (Marine Corps Institute, 1985)",
     MCI, "ERIC_ED275868", 1985, "eric",
     "The Marine Corps Institute's correspondence course on automotive fuel and exhaust systems, read whole, with "
     "its review exercises.", "eric"),
    ("mech", "usmc_mci_diesel_generator_sets_1984", "usmc", "Marine Corps Institute course (ERIC document ED259127)",
     "Installation, Operation, and Operator's Maintenance of Diesel-Engine-Driven Generator Sets (Marine Corps "
     "Institute, 1984)",
     MCI, "ERIC_ED259127", 1984, "eric",
     "The Marine Corps Institute's correspondence course on installing, running and looking after diesel generator "
     "sets, read whole, with its review exercises.", "eric"),
    ("mech", "usmc_mci_fundamentals_of_diesel_engines_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED259132)",
     "Fundamentals of Diesel Engines (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED259132", 1984, "eric",
     "The Marine Corps Institute's correspondence course on the fundamentals of diesel engines, read whole, with "
     "its review exercises.", "eric"),
    ("mech", "usmc_mci_metal_working_and_welding_1983", "usmc",
     "Marine Corps Institute course (ERIC document ED259131)",
     "Metal Working and Welding Operations (Marine Corps Institute, 1983)",
     MCI, "ERIC_ED259131", 1983, "eric",
     "The Marine Corps Institute's correspondence course on metal working and welding, read whole, with its review "
     "exercises.", "eric"),
    ("mech", "usmc_mci_basic_shop_fundamentals_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED275867)",
     "Basic Shop Fundamentals for the Mechanic (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED275867", 1984, "eric",
     "The Marine Corps Institute's correspondence course of basic shop skills for mechanics, read whole, with its "
     "review exercises.", "eric"),
    ("mech", "army_tm_10_440_blacksmith_and_welder_1941", "army", "TM 10-440",
     "The Blacksmith and the Welder (TM 10-440, 1941)",
     "War Department", "tm-10-440-the-blacksmith-and-the-welder-1941", 1941, "record",
     "The Army's 1941 manual for blacksmiths and welders, read whole. An old edition, kept because later manuals "
     "dropped forge work.", "ia"),
    # ---------------------------------------------------------------- construction and utilities
    ("build", "accp_en5155_carpentry_i", "army", "Army Correspondence Course Program subcourse EN5155, edition A",
     "Carpentry 1 (Army subcourse EN5155, edition A, 1995)",
     ACCP, "en-5155-carpentry-i-edition-a", 1995, "printed",
     "The Army's self-study subcourse EN5155 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions on reading construction prints, identifying drawing legends and symbols, preparing a "
     "materials takeoff list, and maintaining tools and equipment.", "ia"),
    ("build", "accp_en5156_carpentry_ii", "army", "Army Correspondence Course Program subcourse EN5156, edition B",
     "Carpentry 2 (Army subcourse EN5156, edition B, 1995)",
     ACCP, "en-5156-carpentry-ii-edition-b", 1995, "printed",
     "The Army's self-study subcourse EN5156 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions on floor planning, subflooring and wall sheathing, doors and windows, roof covering "
     "materials and accessories, finished floors, and stairway construction.", "ia"),
    ("build", "accp_en0053_carpentry_iii", "army", "Army Correspondence Course Program subcourse EN0053, edition 7",
     "Carpentry 3 (Army subcourse EN0053, edition 7, 2004)",
     ACCP, "en-0053-carpentry-iii-edition-7", 2004, "pdf",
     "The Army's self-study subcourse EN0053 (Engineer school), read whole, with its lessons, exercises and "
     "answers. This subcourse, 533, concludes the instruction on carpentry. It discusses the requirements for "
     "competent cabinet work, explaining the kinds and selections of woods, the classification and uses of "
     "woodworking joints, and the standards for their employment. The selection of materials for constructing "
     "wooden articles, the assembling of parts into units, and the steps taken in a final inspection of completed "
     "work are presented in sequence.", "ia"),
    ("build", "accp_en0069_frame_structures", "army",
     "Army Correspondence Course Program subcourse EN0069, edition A",
     "Frame Structures (Army subcourse EN0069, edition A, 2004)",
     ACCP, "en-0069-frame-structures-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN0069 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Nomenclature of frame building members; construction print reading; layout of structures; "
     "characteristics of wood; materials and labor estimating; methods of in-place and precut construction; use of "
     "standard plans under Army Facilities Systems for theater of operations construction.", "ia"),
    ("build", "accp_en5157_masonry", "army", "Army Correspondence Course Program subcourse EN5157, edition A",
     "Masonry (Army subcourse EN5157, edition A, 1996)",
     ACCP, "en-5157-masonry-edition-a", 1996, "printed",
     "The Army's self-study subcourse EN5157 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions on selecting mortar materials and mixing mortar, constructing a concrete block wall and "
     "constructing a brick wall.", "ia"),
    ("build", "accp_en5466_concrete_engineering", "army",
     "Army Correspondence Course Program subcourse EN5466, edition A",
     "Concrete Engineering (Army subcourse EN5466, edition A, 1992)",
     ACCP, "en-5466-concrete-engineering-edition-a", 1992, "printed",
     "The Army's self-study subcourse EN5466 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Characteristics and properties of the components of concrete; ways to design concrete mixes; "
     "determining quantities of concrete needed for specific construction projects; form-work design; mixing, "
     "placing, and curing of concrete; and physical plants used in the production of concrete.", "ia"),
    ("build", "accp_en0562_painting_i", "army", "Army Correspondence Course Program subcourse EN0562, edition A",
     "Painting 1 (Army subcourse EN0562, edition A, 1998)",
     ACCP, "en-0562-painting-i-edition-a", 1998, "printed",
     "The Army's self-study subcourse EN0562 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Selection and mixing of paints, operation and maintenance of paint equipment, proper storage of "
     "paint supplies, identification of metals and detection and prevention of corrosion, safety.", "ia"),
    ("build", "accp_en5110_prepare_a_plumbing_takeoff_list_plumbing_i", "army",
     "Army Correspondence Course Program subcourse EN5110, edition A",
     "Prepare a Plumbing Takeoff List (Plumbing 1) (Army subcourse EN5110, edition A, 2004)",
     ACCP, "en-5110-prepare-a-plumbing-takeoff-list-plumbing-i-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN5110 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions for preparing a plumbing takeoff list, extracting information from a construction "
     "drawing legend, identifying plumbing symbols, and listing plumbing materials.", "ia"),
    ("build", "accp_en5111_water_supply_plumbing_ii", "army",
     "Army Correspondence Course Program subcourse EN5111, edition A",
     "Water Supply (Plumbing 2) (Army subcourse EN5111, edition A, 2004)",
     ACCP, "en-5111-water-supply-plumbing-ii-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN5111 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions for installing plumbing water supply pipe systems to include tubing, pipes, and "
     "fixtures; welding and soldering; and testing system for leaks.", "ia"),
    ("build", "accp_en5112_waste_systems_plumbing_iii", "army",
     "Army Correspondence Course Program subcourse EN5112, edition A",
     "Waste Systems (Plumbing 3) (Army subcourse EN5112, edition A, 2004)",
     ACCP, "en-5112-waste-systems-plumbing-iii-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN5112 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions for preparing, connecting, and installing pipes in a waste system. Information on waste "
     "system materials and rough-in procedures.", "ia"),
    ("build", "accp_en5113_plumbing_fixtures_plumbing_iv", "army",
     "Army Correspondence Course Program subcourse EN5113, edition 5",
     "Plumbing Fixtures (Plumbing 4) (Army subcourse EN5113, edition 5, 2004)",
     ACCP, "en-5113-plumbing-fixtures-plumbing-iv-edition-5", 2004, "pdf",
     "The Army's self-study subcourse EN5113 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Description of the procedures and equipment used to install lavatories and sinks; water closets with "
     "tanks; and urinals including tests for mechanical operations and leaks.", "ia"),
    ("build", "accp_en5114_repair_valves_and_fixture_control_devices_plumbi", "army",
     "Army Correspondence Course Program subcourse EN5114, edition A",
     "Repair Valves and Fixture Control Devices (Plumbing 5) (Army subcourse EN5114, edition A, 2004)",
     ACCP, "en-5114-repair-valves-and-fixture-control-devices-plumbing-v-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN5114 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions on the identification and repair of valves and on the repair of fixture control devices "
     "including disassembly and troubleshooting procedures.", "ia"),
    ("build", "accp_en5115_clear_waste_system_stoppages_plumbing_vi", "army",
     "Army Correspondence Course Program subcourse EN5115, edition A",
     "Clear Waste System Stoppages (Plumbing 6) (Army subcourse EN5115, edition A, 2004)",
     ACCP, "en-5115-clear-waste-system-stoppages-plumbing-vi-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN5115 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions on clearing stoppage in plumbing fixtures and waste drain lines, and identifying and "
     "using different plumbing tools.", "ia"),
    ("build", "accp_en5144_install_system_equipment_and_component_grounds", "army",
     "Army Correspondence Course Program subcourse EN5144, edition B",
     "Install System, Equipment and Component Grounds (Army subcourse EN5144, edition B, 1999)",
     ACCP, "en-5144-install-system-equipment-and-component-grounds-edition-b", 1999, "printed",
     "The Army's self-study subcourse EN5144 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Principles of installing systems, equipment and component grounds including grounding electrodes and "
     "circuit grounds.", "ia"),
    ("build", "accp_en0389_utilities_ii", "army", "Army Correspondence Course Program subcourse EN0389, edition 9",
     "Utilities 2 (Army subcourse EN0389, edition 9, 2004)",
     ACCP, "en-0389-utilities-ii-edition-9", 2004, "pdf",
     "The Army's self-study subcourse EN0389 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Design principles, construction, operation and maintenance of utilities systems for large, "
     "semipermanent installations in the theater of operations, including electrical power and distribution "
     "systems, water distribution systems, sewage collection and disposal systems.", "ia"),
    ("build", "accp_en5151_design_forms_for_a_concrete_wall", "army",
     "Army Correspondence Course Program subcourse EN5151, edition B",
     "Design Forms for a Concrete Wall (Army subcourse EN5151, edition B, 2006)",
     ACCP, "en-5151-design-forms-for-a-concrete-wall-edition-b", 2006, "printed",
     "The Army's self-study subcourse EN5151 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Selecting proper material and determining the amount of material needed and the time required to "
     "design forms for concrete walls.", "ia"),
    ("build", "accp_od1747_refrigeration_and_air_conditioning_i", "army",
     "Army Correspondence Course Program subcourse OD1747, edition A",
     "Refrigeration and Air Conditioning 1 (Army subcourse OD1747, edition A, 2004)",
     ACCP, "od-1747-refrigeration-and-air-conditioning-i-edition-a", 2004, "pdf",
     "The Army's self-study subcourse OD1747 (Ordnance school), read whole, with its lessons, exercises and "
     "answers. Fundamentals of electricity, motors, circuit protectors, troubleshooting, and safety; maintenance of "
     "the gasoline engine; physics of refrigeration; explanation of the characteristics of refrigerants.", "ia"),
    ("build", "accp_md0160_military_water_supply", "army",
     "Army Correspondence Course Program subcourse MD0160, edition 100",
     "Military Water Supply (Army subcourse MD0160, edition 100, 2003)",
     AMEDD, "md-0160-military-water-supply-edition-100", 2003, "pdf",
     "The Army's self-study subcourse MD0160 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Responsibilities for military water supply; sources, characteristics, and quality standards for "
     "drinking water; chemical and bacteriological tests on water; principles and methods of water treatment and "
     "distribution, to include field water purification; protection of water supply sources and systems.", "ia"),
    ("build", "accp_md0161_wastewater_treatment", "army",
     "Army Correspondence Course Program subcourse MD0161, edition 100",
     "Wastewater Treatment (Army subcourse MD0161, edition 100, 2001)",
     AMEDD, "md-0161-wastewater-treatment-edition-100", 2001, "pdf",
     "The Army's self-study subcourse MD0161 (Medical Department school), read whole, with its lessons, exercises "
     "and answers. Fundamentals for the treatment and disposal of wastewater. Applications for both military "
     "installations and field facilities, including construction and operations.", "ia"),
    ("build", "army_fm_3_34_471_plumbing_pipe_fitting_sewerage_2001", "army", "FM 3-34.471",
     "Plumbing, Pipe Fitting, and Sewerage (FM 3-34.471, 2001)",
     ARMY, "FM_3_34_471_P_2001", 2001, "printed",
     "The Army's plumbing manual (it took over from FM 5-420 of 1993), read whole. Its parts: Plumbing systems; "
     "Heating systems; Basic Plumbing Repairs and Maintenance; Plumbing fixtures; Water heaters; Pipes and "
     "Fittings; Valves and Faucets; Stacks and Branches; Traps and Vents; Steam, Gas, and Air Piping; Centrifugal "
     "pumps; Insulation; Construction Plans and Drawings; Pipe sizes for water distribution system design; "
     "Distribution systems design procedures.", "ia"),
    ("build", "army_fm_5_484_well_drilling_operations_1994", "joint", "FM 5-484 (NAVFAC P-1065, AFMAN 32-1072)",
     "Multiservice Procedures for Well-Drilling Operations (FM 5-484, 1994)",
     "Departments of the Army, the Navy and the Air Force", "FM_5_484_M_P_W_D_O_1994", 1994, "record",
     "The armed forces' manual of well drilling, read whole. Its parts: Basics; Well drilling; Special "
     "considerations; Water detection response team; Navy well drilling; Air force well drilling; Electrical "
     "logging system; Bit maintenance.", "ia"),
    ("build", "army_fm_5_488_logging_and_sawmill_operations_1993", "army", "FM 5-488",
     "Logging and Sawmill Operations (FM 5-488, 1993)",
     ARMY, "fm-5-488-logging-and-sawmill-operations-1993", 1993, "printed",
     "The Army's manual of logging and sawmill operations, read whole.", "ia"),
    ("build", "army_tm_5_683_electrical_interior_facilities_1995", "joint",
     "TM 5-683 (NAVFAC MO-116, AFJMAN 32-1083)",
     "Facilities Engineering: Electrical Interior Facilities (TM 5-683, 1995)",
     "Departments of the Army, the Navy and the Air Force", "ost-military-engineering-tm5_683", 1995, "printed",
     "The armed forces' manual for maintaining the electrical systems inside buildings, read whole. Its parts: "
     "Transformers; Electric motors; Motor controls; Power cables; Electronic equipment; Grounding; Illumination; "
     "Back-up, security, and protection systems; Hazardous substances; Electrical safety; Test equipment; Test "
     "methods; Maintenance schedules.", "ia"),
    ("build", "army_tm_5_682_electrical_facilities_safety_1999", "army", "TM 5-682",
     "Facilities Engineering: Electrical Facilities Safety (TM 5-682, 1999)",
     ARMY, "ost-military-engineering-tm5_682", 1999, "printed",
     "The Army's manual of electrical safety for facilities workers, read whole. Its parts: Apparel, tools, and "
     "material handling; Overhead lines and associated electrical components; Underground cables, structures, and "
     "associated electrical; Low-voltage systems; Sample safety examination.", "ia"),
    ("build", "army_tm_5_685_auxiliary_generators_1996", "army", "TM 5-685 (NAVFAC MO-912)",
     "Operation, Maintenance and Repair of Auxiliary Generators (TM 5-685, 1996)",
     ARMY, "ost-military-engineering-tm5_685", 1996, "printed",
     "The Army and Navy manual for running, maintaining and repairing standby (auxiliary) generators, read whole. "
     "Its parts: Emergency power systems; Prime movers; Switchgear; Operating procedures; Routine maintenance; Fuel "
     "and fuel storage; Lubricating oil; Cooling systems and coolants; Safety; Records.", "ia"),
    ("build", "army_tm_5_642_small_heating_systems_1990", "army", "TM 5-642",
     "Operation and Maintenance of Small Heating Systems (TM 5-642, 1990)",
     ARMY, "ost-military-engineering-tm5_642", 1990, "printed",
     "The Army's manual for running and maintaining small heating systems, read whole. Its parts: Fuels; Fuel "
     "burning equipment; Steam heating systems; Hot water heating systems; Warm air systems; Related publications; "
     "Troubleshooting underfeed stokers; Troubleshooting steam pressure pumping systems.", "ia"),
    ("build", "army_tm_5_617_maintenance_repair_of_roofs_1974", "army", "TM 5-617",
     "Facilities Engineering: Maintenance and Repair of Roofs (TM 5-617, 1974)",
     ARMY, "ost-military-engineering-tm5_617", 1974, "printed",
     "The Army's manual for maintaining and repairing roofs, read whole. Its parts: General discussion; Causes of "
     "roof failures; Built-up roofing; Asphalt-shingle roofing; Asphalt roll roofing; Asbestos-cement roofing; "
     "Slate roofing; Tile roofing; Wood-shingle roofing; Metal roofing; Flashings and appurtenances; Special "
     "roofings; Safety; Department of defense instructions; Technical manuals; Material specifications and "
     "standards; Industry publications; Guide specifications for military construction; Sample historical record "
     "formats and inspection formats.", "ia"),
    ("build", "army_fm_10_52_1_water_supply_point_1991", "army", "FM 10-52-1",
     "Water Supply Point Equipment and Operations (FM 10-52-1, 1991)",
     ARMY, "ost-military-doctrine-fm10_52_1", 1991, "record",
     "The Army's manual of water supply point equipment and operations, read whole. Its parts: Water treatment; "
     "Water reconnaissance; Water source and water point development; Purification operations; Storage operations; "
     "Distribution operations; Threat and nbc operations; Extreme environment operations; Formulas for water supply "
     "problems; Chlorine dosage; Purification equipment characteristics; Storage equipment characteristics; "
     "Distribution equipment characteristics.", "ia"),
    ("build", "army_tb_med_577_field_water_supplies_2010", "joint", "TB MED 577 (NAVMED P-5010-10, AFMAN 48-138_IP)",
     "Sanitary Control and Surveillance of Field Water Supplies (TB MED 577, 2010)",
     "Departments of the Army, the Navy and the Air Force", "ost-military-medical-tbmed577", 2010, "printed",
     "The armed forces' bulletin on keeping field water supplies safe, read whole.", "ia"),
    ("build", "usmc_mci_air_conditioning_mechanic_1982", "usmc",
     "Marine Corps Institute course (ERIC document ED259126)",
     "Air-Conditioning Mechanic (Marine Corps Institute, 1982)",
     MCI, "ERIC_ED259126", 1982, "eric",
     "The Marine Corps Institute's correspondence course for air-conditioning mechanics, read whole, with its "
     "review exercises.", "eric"),
    ("build", "usmc_mci_fundamentals_of_refrigeration_1986", "usmc",
     "Marine Corps Institute course (ERIC document ED275865)",
     "Fundamentals of Refrigeration (Marine Corps Institute, 1986)",
     MCI, "ERIC_ED275865", 1986, "eric",
     "The Marine Corps Institute's correspondence course on the fundamentals of refrigeration, read whole, with its "
     "review exercises.", "eric"),
    ("build", "usmc_mci_refrigeration_servicing_1985", "usmc",
     "Marine Corps Institute course (ERIC document ED275866)",
     "Refrigeration Servicing (Marine Corps Institute, 1985)",
     MCI, "ERIC_ED275866", 1985, "eric",
     "The Marine Corps Institute's correspondence course on servicing refrigeration equipment, read whole, with its "
     "review exercises.", "eric"),
    ("build", "usmc_mci_plumbing_and_sewage_disposal_1986", "usmc",
     "Marine Corps Institute course (ERIC document ED275862)",
     "Plumbing and Sewage Disposal (Marine Corps Institute, 1986)",
     MCI, "ERIC_ED275862", 1986, "eric",
     "The Marine Corps Institute's correspondence course on plumbing and sewage disposal, read whole, with its "
     "review exercises.", "eric"),
    ("build", "usmc_mci_marine_electrician_fundamentals_1986", "usmc",
     "Marine Corps Institute course (ERIC document ED275863)",
     "Marine Electrician: Fundamentals (Marine Corps Institute, 1986)",
     MCI, "ERIC_ED275863", 1986, "eric",
     "The Marine Corps Institute's correspondence course of electrical fundamentals for Marine Corps electricians, "
     "read whole, with its review exercises.", "eric"),
    # ---------------------------------------------------------------- quartermaster
    ("qm", "army_fm_10_16_general_fabric_repair_2000", "army", "FM 10-16",
     "General Fabric Repair (FM 10-16, 2000)",
     ARMY, "fm-10-16-general-fabric-repair-2000", 2000, "printed",
     "The Army's manual of general fabric repair (tents, canvas and other textiles), read whole. Its parts: "
     "Inspecting and marking clothing and textile items; Hand sewing on clothing and textiles; Machine sewing on "
     "clothing and textiles; Repairing clothing and textile items; Inspecting and marking canvas and webbing; Using "
     "the tentage repair kit; Hand sewing on canvas and webbing; Machine sewing on canvas and webbing; Sewing "
     "repairs to canvas; Repairing with cement and sealer; Repairing lines; Replacing hardware; Repairing webbing; "
     "Re-treating tents and tarpaulins.", "ia"),
    ("qm", "army_fm_42_414_field_service_company_1998", "army", "FM 42-414",
     "Tactics, Techniques and Procedures for Quartermaster Field Service Company, Direct Support (FM 42-414, "
     "1998)",
     ARMY, "FM_42_414_T_T_P_Q_F_S_C_D_S_1998", 1998, "printed",
     "The Army's manual for quartermaster field service companies, which run field showers, laundries and clothing "
     "repair, read whole. Its parts: Alignment of quartermaster field service support; Suggested sop format; "
     "Fratricide prevention; Mission-kill operational data; Unit public affairs; Laundry washing formulas; Dry "
     "weights of standard clothing items; Clothing resizing.", "ia"),
    ("qm", "usmc_mci_bulk_fuel_man_1984", "usmc", "Marine Corps Institute course (ERIC document ED259133)",
     "Bulk Fuel Man (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED259133", 1984, "eric",
     "The Marine Corps Institute's correspondence course for bulk fuel handlers, read whole, with its review "
     "exercises.", "eric"),
    ("qm", "army_fm_3_21_220_static_line_parachuting_2003", "joint",
     "FM 3-21.220 (MCWP 3-15.7, AFMAN 11-420, NAVSEA SS400-AF-MMO-010)",
     "Static Line Parachuting Techniques and Training (FM 3-21.220, 2003)",
     "Departments of the Army, the Navy and the Air Force", "ost-military-doctrine-fm3_21x220", 2003, "printed",
     "The armed forces' manual of static line parachuting techniques and training, read whole. Its parts: Airborne "
     "training; Personal equipment; Five points of performance; Training apparatuses; Jump command sequence and "
     "jumper actions; Jumpmaster duties at the unit area; Jumpmaster and safety duties; Jumpmaster and safety "
     "duties in flight; Departure airfield control officer; Individual combat equipment jump loads; Arctic rigging; "
     "A-series containers; Aircraft and jump altitudes; High-performance transport aircraft; Rotary-wing aircraft; "
     "Other service aircraft; Nonstandard aircraft; Procedures on the drop zone; Drop zone computations and "
     "formulas; Establishment and operation of a drop zone; Malfunctions reporting and duties; Adverse weather "
     "aerial delivery system; Deliberate water drop zone operations; Exit procedures.", "ia"),
    ("qm", "army_fm_4_20_197_sling_load_single_point_2009", "joint",
     "FM 4-20.197 (MCRP 4-11.3E, NTTP 3-04.11, AFMAN 11-223)",
     "Multiservice Helicopter Sling Load: Single-Point Load Rigging Procedures (2009)",
     "Departments of the Army, the Navy and the Air Force", "ost-military-doctrine-fm4_20x198", 2009, "printed",
     "The armed forces' manual of rigging loads to hang under a helicopter from one hook, read whole. Its parts: "
     "Fundamental Principles of Sling Load; Certified Single-Point Rigging Procedures for Wheeled Vehicles; "
     "Certified Single-Point Rigging Procedures for Trailers; Certified Single-Point Rigging Procedures for "
     "Trailers With Mounted Generators; Certified Single-Point Rigging Procedures for Truck and Towed Combinations; "
     "Certified Single-Point Rigging Procedures for Howitzers and Weapons Systems; Certified Single-Point Rigging "
     "Procedures for Guided Missile Systems; Certified Single-Point Rigging Procedures for Engineer Equipment; "
     "Certified Single-Point Rigging Procedures for Liquid Containers; Certified Single-Point Rigging Procedures "
     "for Shelters; Certified Single-Point Rigging Procedures for Containers; Certified Single-Point Rigging "
     "Procedures for Radar and Satellite Equipment; Certified Single-Point Rigging Procedures for Generator Sets; "
     "Certified Single-Point Rigging Procedures for Miscellaneous Equipment; Suitable Single-Point Rigging "
     "Procedures for Wheeled Vehicles; Suitable Single-Point Rigging Procedures for Trailers; Suitable Single-Point "
     "Rigging Procedures for Engineer Equipment; Suitable Single-Point Rigging Procedures for Liquid Containers; "
     "Suitable Single-Point Rigging Procedures for Shelters; Suitable Single-Point Rigging Procedures for "
     "Containers; Suitable Single-Point Rigging Procedures for Radar Equipment; Suitable Single-Point Rigging "
     "Procedures for Generator Sets; Suitable Single-Point Rigging Procedures for Miscellaneous Equipment; National "
     "Stock Numbers for Slings, Nets, and Spare Parts.", "ia"),
    ("qm", "army_fm_10_67_1_petroleum_operations_1998", "army", "FM 10-67-1",
     "Concepts and Equipment of Petroleum Operations (FM 10-67-1, 1998)",
     ARMY, "ost-military-doctrine-fm10_67_1", 1998, "printed",
     "The Army's manual of the concepts and equipment of petroleum (fuel) operations, read whole. Its parts: Tank "
     "strapping; Fundamentals of pipeline hydraulics; Pmcs checklists; Water detection (aqua-glo) test; Procedures "
     "for testing resistance to ground; Filter membrane color ratings; Standard petroleum containers; Volume "
     "conversion; Checklist for delivery and unloading; Petroleum Product and Crude Oil Factors; Flow conversion "
     "chart; Material safety data sheets; Force provider; Authorization page.", "ia"),
    ("qm", "usaf_fabrication_and_parachute_specialist_1978", "usaf",
     "Military Curriculum Materials 18-2 (an Air Force course) (ERIC document ED183836)",
     "Fabrication and Parachute Specialist (Air Force course, Military Curriculum Materials 18-2, 1978)",
     "Department of the Air Force (Air Training Command); selected by the National Center for Research in "
     "Vocational Education",
     "ERIC_ED183836", 1978, "eric",
     "The Air Force's course for fabrication and parachute specialists, read whole. The machine-read text of this "
     "microfiche scan has many mistakes.", "eric", "MCM"),
    ("qm", "usaf_sewing_machine_maintenance_1978", "usaf",
     "Military Curriculum Materials 18-3 (a military course) (ERIC document ED183837)",
     "Sewing Machine Maintenance (Military Curriculum Materials 18-3, 1978)",
     "US armed forces; selected by the National Center for Research in Vocational Education",
     "ERIC_ED183837", 1978, "eric",
     "A military course on sewing machine maintenance, read whole. The machine-read text of this microfiche scan "
     "has many mistakes.", "eric", "MCM"),
    ("qm", "accp_qm3503_direct_fuel_system_supply_point_operations", "army",
     "Army Correspondence Course Program subcourse QM3503, edition A",
     "Direct Fuel System Supply Point Operations (Army subcourse QM3503, edition A, 1993)",
     ACCP, "qm-3503-direct-fuel-system-supply-point-operations-edition-a", 1993, "printed",
     "The Army's self-study subcourse QM3503 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Identify the components of a fuel system supply point (FSSP); perform and supervise preventive "
     "maintenance checks and services on the components of an FSSP; direct site preparation, layout, and assembly "
     "of an FSSP; and perform emergency repair of collapsible storage tanks.", "ia"),
    ("qm", "accp_qm5094_direct_tank_vehicles", "army",
     "Army Correspondence Course Program subcourse QM5094, edition A",
     "Direct Tank Vehicles (Army subcourse QM5094, edition A, 1999)",
     ACCP, "qm-5094-direct-tank-vehicles-edition-a", 1999, "printed",
     "The Army's self-study subcourse QM5094 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. The soldier will learn to supervise the loading and unloading of tank vehicles, gaging of tank "
     "vehicles, PMCS verify appropriate entries on DA Form 2404 and DA Form 5988-E (ULLS) and correction of "
     "deficiencies, operation of tank units and vehicles, observe fire and safety precautions, and identify "
     "environmental considerations.", "ia"),
    ("qm", "accp_qm5200_petroleum_operations_and_applications", "army",
     "Army Correspondence Course Program subcourse QM5200, edition A",
     "Petroleum Operations and Applications (Army subcourse QM5200, edition A, 1999)",
     ACCP, "qm-5200-petroleum-operations-and-applications-edition-a", 1999, "printed",
     "The Army's self-study subcourse QM5200 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Discusses and provides the knowledge of joint petroleum and the peculiarities of petroleum products. "
     "It discusses what the required knowledge is for the proper procedures for storing petroleum products using "
     "meters, verifying meters and calculating meter correction factors. It also discusses the waterfront terminal "
     "and its required equipment and facilities, its responsibilities and capabilities as well as how to properly "
     "report the proper issuing and receiving of products under the defense automated management system "
     "(DFAMS).", "ia"),
    # ---------------------------------------------------------------- communications and electronics
    ("comms", "accp_mm0308_introduction_to_electricity", "army",
     "Army Correspondence Course Program subcourse MM0308, edition 9",
     "Introduction to Electricity (Army subcourse MM0308, edition 9, 1988)",
     ACCP, "mm-0308-introduction-to-electricity-edition-9", 1988, "printed",
     "The Army's self-study subcourse MM0308 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Electron theory; current flow and magnetic fields; Ohm’s Law; electrical "
     "power; magnetism; generation of AC power, effects of resistance, capacitors and inductance on AC power, "
     "impedance, characteristics of tuned circuits and resonance. CMF 35, 918.", "ia"),
    ("comms", "accp_mm0703_basic_electricity", "army", "Army Correspondence Course Program subcourse MM0703",
     "Basic Electricity, Part 1 (Army subcourse MM0703, 2002)",
     ACCP, "mm-0703-basic-electricity", 2002, "pdf",
     "The Army's self-study subcourse MM0703 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Describes the principles of electron flow, static electricity, conductors, "
     "and insulators and discusses basic electrical concepts and principles of magnetism; explains what an electric "
     "circuit is, defines the standard electrical units of measure and explains how to use Ohm’s and Kirchoff’s "
     "laws; explains characteristics of direct and alternating currents; the generation at a sine wave of voltage "
     "or current; vector representation of a sine wave; and peak, average, and effective values of alternating "
     "current; explains what capacitance and inductance are and describes resistive and capacitive cir.", "ia"),
    ("comms", "accp_mm0704_basic_electricity_ii", "army",
     "Army Correspondence Course Program subcourse MM0704, edition 7",
     "Basic Electricity Part 2 (Army subcourse MM0704, edition 7, 2008)",
     ACCP, "mm-0704-basic-electricity-ii-edition-7", 2008, "pdf",
     "The Army's self-study subcourse MM0704 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Mathematics required to understand the basic operating principles of guided "
     "missiles in general, and electronic and radar circuits in particular; electron theory direct and alternating "
     "current laws and circuitry, theory and use of inductors and capacitors. CMF 35, 918.", "ia"),
    ("comms", "accp_mm0705_electronics_1", "army", "Army Correspondence Course Program subcourse MM0705",
     "Electronics 1 (Army subcourse MM0705, 1988)",
     ACCP, "mm-0705-electronics-1", 1988, "printed",
     "The Army's self-study subcourse MM0705 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Principles, functions, and use of electron emission, diode tubes, rectifiers, "
     "power supplies, voltage regulators, amplifiers, oscillators, and cathode ray tubes. Also deals with the "
     "principles of amplitude modulation and the superheterodyne received. (.", "ia"),
    ("comms", "accp_mm0321_am_radio_transmitters", "army",
     "Army Correspondence Course Program subcourse MM0321, edition 9",
     "AM Radio Transmitters (Army subcourse MM0321, edition 9, 2009)",
     ACCP, "mm-0321-am-radio-transmitters-edition-9", 2009, "pdf",
     "The Army's self-study subcourse MM0321 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Radio communications systems; frequencies used; components of radio systems; "
     "block diagrams of simple and multiple transmitters; radio frequency amplifiers; keying methods; analysis of "
     "AM transmitters; interstage coupling, analysis of block and schematic diagrams of radio transmitters; "
     "transmitter troubleshooting. CMF 35.", "ia"),
    ("comms", "accp_mm0322_am_radio_receivers", "army",
     "Army Correspondence Course Program subcourse MM0322, edition 9",
     "AM Radio Receivers (Army subcourse MM0322, edition 9, 2009)",
     ACCP, "mm-0322-am-radio-receivers-edition-9", 2009, "pdf",
     "The Army's self-study subcourse MM0322 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Fundamentals of amplitude-modulated radio receivers including: reception of "
     "radio waves; block diagrams of radio receivers; selectivity and sensitivity of radio frequency and IF "
     "amplifiers; frequency conversion by heterodyning; automatic volume control; detection of modulated and "
     "unmodulated waves; circuit analysis of AM superheterodyne receivers; comparison of electron tube and "
     "transistor circuitry; tuning indicators; continuous wave detection; troubleshooting AM receivers. "
     "CMF 35.", "ia"),
    ("comms", "accp_mm0323_fm_radio_transmitters", "army",
     "Army Correspondence Course Program subcourse MM0323, edition 6",
     "FM Radio Transmitters (Army subcourse MM0323, edition 6, 1971)",
     ACCP, "mm-0323-fm-radio-transmitters-edition-6", 1971, "printed",
     "The Army's self-study subcourse MM0323 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Principles of frequency modulation; methods of producing frequency "
     "modulation; basic FM transmitter circuits to include reactance-tube modulators; phase modulators, frequency "
     "multipliers and automatic frequency control circuits. CMF 35, 918.", "ia"),
    ("comms", "accp_mm0324_fm_radio_receivers", "army",
     "Army Correspondence Course Program subcourse MM0324, edition 6",
     "FM Radio Receivers (Army subcourse MM0324, edition 6, 1971)",
     ACCP, "mm-0324-fm-radio-receivers-edition-6", 1971, "printed",
     "The Army's self-study subcourse MM0324 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Basic FM receiver circuits including wideband amplifiers, limiters, "
     "discriminators and ratio detector circuits; familiarization with typical FM equipment in military use. CMF "
     "35, 918.", "ia"),
    ("comms", "accp_mm0750_high_frequency_fixed_station_radio_systems", "army",
     "Army Correspondence Course Program subcourse MM0750, edition 0",
     "High Frequency Fixed Station Radio Systems (Army subcourse MM0750, edition 0, 2007)",
     ACCP, "mm-0750-high-frequency-fixed-station-radio-systems-edition-0", 2007, "pdf",
     "The Army's self-study subcourse MM0750 (missile and munitions electronics school), read whole, with its "
     "lessons, exercises and answers. Introduction to high frequency long distance radio communications including "
     "types of signal used, significance of circuit quality, configurations of equipment for transmitting and "
     "receiving antenna characteristics, frequency planning and types of mobile communications terminals.", "ia"),
    ("comms", "accp_ss0130_principles_of_radio_wave_propagation", "army",
     "Army Correspondence Course Program subcourse SS0130, edition B",
     "Principles of Radio Wave Propagation (Army subcourse SS0130, edition B, 2005)",
     ACCP, "ss-0130-principles-of-radio-wave-propagation-edition-b", 2005, "printed",
     "The Army's self-study subcourse SS0130 (Signal school), read whole, with its lessons, exercises and answers. "
     "Fundamentals of radio wave propagation, modulation, propagation characteristics through different media, "
     "ground wave propagation and the terrestrial influences that affect communications, sky wave propagation and "
     "the effects of atmospheric conditions on radio communication.", "ia"),
    ("comms", "accp_ss0131_antenna_theory", "army", "Army Correspondence Course Program subcourse SS0131, edition A",
     "Antenna Theory (Army subcourse SS0131, edition A, 2005)",
     ACCP, "ss-0131-antenna-theory-edition-a", 2005, "printed",
     "The Army's self-study subcourse SS0131 (Signal school), read whole, with its lessons, exercises and answers. "
     "Theory of antennas to include the principles of antenna radiation, characteristics and capabilities of the "
     "various types of tactical combat net radio, high frequency, ultra high frequency, very high frequency "
     "antennas, formulas used in antenna design, and fabricating field expedient antennas using various repair "
     "techniques.", "ia"),
    ("comms", "accp_ss0437_testing_wire_lines_and_locating_faults", "army",
     "Army Correspondence Course Program subcourse SS0437, edition 7",
     "Testing Wire Lines and Locating Faults (Army subcourse SS0437, edition 7, 2011)",
     ACCP, "ss-0437-testing-wire-lines-and-locating-faults-edition-7", 2011, "pdf",
     "The Army's self-study subcourse SS0437 (Signal school), read whole, with its lessons, exercises and answers. "
     "How to perform tasks related to troubleshooting field wire WD–1()/TT. Also provides procedures and methods of "
     "testing wire lines and locating faults. You must have access to this equipment to complete this "
     "subcourse.", "ia"),
    ("comms", "accp_ss0439_set_poles_install_anchors_and_guys", "army",
     "Army Correspondence Course Program subcourse SS0439, edition A",
     "Set Poles, Install Anchors and Guys (Army subcourse SS0439, edition A, 1994)",
     ACCP, "ss-0439-set-poles-install-anchors-and-guys-edition-a", 1994, "printed",
     "The Army's self-study subcourse SS0439 (Signal school), read whole, with its lessons, exercises and answers. "
     "Information on setting poles, pole inspection, and installing anchors and guys.", "ia"),
    ("comms", "accp_ss0444_cable_construction", "army",
     "Army Correspondence Course Program subcourse SS0444, edition A",
     "Cable Construction (Army subcourse SS0444, edition A, 1994)",
     ACCP, "ss-0444-cable-construction-edition-a", 1994, "printed",
     "The Army's self-study subcourse SS0444 (Signal school), read whole, with its lessons, exercises and answers. "
     "Construction practices generally followed by wire systems installer personnel. This training is for those in "
     "a signal unit supporting another unit; a signal battalion with a division that is equipped with mobile "
     "subscriber equipment; or a signal unit supporting echelons above corps.", "ia"),
    ("comms", "usmc_mci_antenna_construction_propagation_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED258035)",
     "Antenna Construction and Propagation of Radio Waves (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258035", 1984, "eric",
     "The Marine Corps Institute's correspondence course on building antennas and how radio waves travel, read "
     "whole, with its review exercises.", "eric"),
    ("comms", "usmc_mci_solid_state_devices_1986", "usmc", "Marine Corps Institute course (ERIC document ED275864)",
     "Solid-State Devices (Marine Corps Institute, 1986)",
     MCI, "ERIC_ED275864", 1986, "eric",
     "The Marine Corps Institute's correspondence course on solid-state devices (diodes, transistors and the like), "
     "read whole, with its review exercises.", "eric"),
    # ---------------------------------------------------------------- administration and supply
    ("admin", "accp_qm3519_unit_and_organizational_supply", "army",
     "Army Correspondence Course Program subcourse QM3519, edition A",
     "Unit and Organizational Supply (Army subcourse QM3519, edition A, 1993)",
     ACCP, "qm-3519-unit-and-organizational-supply-edition-a", 1993, "printed",
     "The Army's self-study subcourse QM3519 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Implement the command supply discipline program: ensure that property authorization documents and "
     "supply records are maintained error free and that supplies are on hand or on request; conduct an inventory of "
     "property; and conduct a report of survey.", "ia"),
    ("admin", "accp_qm0113_basic_mathematics_i_addition_subtraction_multipl", "army",
     "Army Correspondence Course Program subcourse QM0113, edition A",
     "Basic Mathematics 1 (Addition, Subtraction, Multiplication, and Division) (Army subcourse QM0113, edition A, "
     "2004)",
     ACCP, "qm-0113-basic-mathematics-i-addition-subtraction-multiplication-and-division-edition-a", 2004, "pdf",
     "The Army's self-study subcourse QM0113 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Basic principles of simple addition, subtraction, multiplication, and division of whole numbers; "
     "problem solving; short division; multiplication tables; addition and subtraction of fractions and mixed "
     "numbers.", "ia"),
    ("admin", "accp_qm0114_basic_mathematics_ii_decimal_fractions", "army",
     "Army Correspondence Course Program subcourse QM0114, edition 4",
     "Basic Mathematics 2 (Decimal Fractions) (Army subcourse QM0114, edition 4, 2004)",
     ACCP, "qm-0114-basic-mathematics-ii-decimal-fractions-edition-4", 2004, "pdf",
     "The Army's self-study subcourse QM0114 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Basic principles of addition, subtraction, multiplication, and division of numbers containing up to "
     "four decimal places; conversion of percent to decimal fractions and decimal fractions to percents.", "ia"),
    ("admin", "accp_qm0115_basic_mathematics_iii_area_and_volume", "army",
     "Army Correspondence Course Program subcourse QM0115, edition A",
     "Basic Mathematics 3 (Area and Volume) (Army subcourse QM0115, edition A, 2004)",
     ACCP, "qm-0115-basic-mathematics-iii-area-and-volume-edition-a", 2004, "pdf",
     "The Army's self-study subcourse QM0115 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Basic principles and formulas used in solving problems in area and volume which are of primary "
     "interest to supply and service personnel.", "ia"),
    ("admin", "accp_qm0116_basic_mathematics_iv_ratio_and_proportion", "army",
     "Army Correspondence Course Program subcourse QM0116, edition 4",
     "Basic Mathematics 4 (Ratio and Proportion) (Army subcourse QM0116, edition 4, 1988)",
     ACCP, "qm-0116-basic-mathematics-iv-ratio-and-proportion-edition-4", 1988, "printed",
     "The Army's self-study subcourse QM0116 (Quartermaster school), read whole, with its lessons, exercises and "
     "answers. Basic concepts of ratio and proportion to include the definition of terms; methods of applying the "
     "rules and problem solving.", "ia"),
    ("admin", "accp_fi0921_basic_statistics", "army",
     "Army Correspondence Course Program subcourse FI0921, edition B",
     "Basic Statistics (Army subcourse FI0921, edition B, 1991)",
     ACCP, "fi-0921-basic-statistics-edition-b", 1991, "printed",
     "The Army's self-study subcourse FI0921 (finance school), read whole, with its lessons, exercises and answers. "
     "Covers percentages, index numbers, measures of central tendency and of dispersion, and the properties of the "
     "normal curve.", "ia"),
    ("admin", "usmc_mci_basic_warehousing_1984", "usmc", "Marine Corps Institute course (ERIC document ED258036)",
     "Basic Warehousing (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258036", 1984, "eric",
     "The Marine Corps Institute's correspondence course on basic warehousing, read whole, with its review "
     "exercises.", "eric"),
    ("admin", "usmc_mci_warehousing_operations_1984", "usmc",
     "Marine Corps Institute course (ERIC document ED258037)",
     "Warehousing Operations (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258037", 1984, "eric",
     "The Marine Corps Institute's correspondence course on warehousing operations, read whole, with its review "
     "exercises.", "eric"),
    ("admin", "usmc_mci_supply_management_1984", "usmc", "Marine Corps Institute course (ERIC document ED258038)",
     "Supply Management (Marine Corps Institute, 1984)",
     MCI, "ERIC_ED258038", 1984, "eric",
     "The Marine Corps Institute's correspondence course on supply management, read whole, with its review "
     "exercises.", "eric"),
    ("admin", "usmc_mci_personal_finance_1985", "usmc", "Marine Corps Institute course (ERIC document ED258044)",
     "Personal Finance (Marine Corps Institute, 1985)",
     MCI, "ERIC_ED258044", 1985, "eric",
     "The Marine Corps Institute's correspondence course on personal finance, read whole, with its review "
     "exercises; its prices, interest rates and rules are those of its day.", "eric"),
    ("admin", "army_fm_10_27_4_organizational_supply_2000", "army", "FM 10-27-4",
     "Organizational Supply and Services for Unit Leaders (FM 10-27-4, 2000)",
     ARMY, "ost-military-doctrine-fm10_27_4", 2000, "printed",
     "The Army's manual of organizational supply and services for unit leaders, read whole. Its parts: Supply "
     "procedures; Methods of Supply; Water and Field Services; Supply in Tactical Operations; Property "
     "Accountability at Unit Level.", "ia"),
    # ---------------------------------------------------------------- maps and surveying
    ("maps", "army_fm_3_34_331_topographic_surveying_2001", "army", "FM 3-34.331",
     "Topographic Surveying (FM 3-34.331, 2001)",
     ARMY, "ost-military-doctrine-fm3_34x331", 2001, "printed",
     "The Army's manual of topographic surveying, read whole. Its parts: Missions, Operations, and Duties; Project "
     "planning; Survey recon; Datums, Grids, and Coordinate References; Conventional survey-data collection; "
     "Traverse; Differential leveling; Navstar gps; Artillery surveys; Airfield-Obstruction and NAVAID Surveys; "
     "Reports, Briefings, and Operation Orders; Mensural conversion charts; Control-survey standards; Basic survey "
     "computations; Survey forms.", "ia"),
    ("maps", "accp_en0591_surveying_i", "army", "Army Correspondence Course Program subcourse EN0591, edition C",
     "Surveying 1 (Army subcourse EN0591, edition C, 1997)",
     ACCP, "en-0591-surveying-i-edition-c", 1997, "printed",
     "The Army's self-study subcourse EN0591 (Engineer school), read whole, with its lessons, exercises and "
     "answers. General survey principles; mathematics including geometry, trigonometry, and logarithms; care, use, "
     "and operation of the common surveying instruments and equipment; and general field work procedures.", "ia"),
    ("maps", "accp_en0593_surveying_iii_topographic_and_geodetic_surveys", "army",
     "Army Correspondence Course Program subcourse EN0593, edition A",
     "Surveying 3 (Topographic and Geodetic Surveys) (Army subcourse EN0593, edition A, 2001)",
     ACCP, "en-0593-surveying-iii-topographic-and-geodetic-surveys-edition-a", 2001, "printed",
     "The Army's self-study subcourse EN0593 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Precise topographic surveying based upon geodetic survey methods including astronomic observations "
     "and electronic measuring systems.", "ia"),
    ("maps", "accp_en5301_cartography_i_map_mathematics", "army",
     "Army Correspondence Course Program subcourse EN5301, edition 2",
     "Cartography 1 Map Mathematics (Army subcourse EN5301, edition 2, 2004)",
     ACCP, "en-5301-cartography-i-map-mathematics-edition-2", 2004, "pdf",
     "The Army's self-study subcourse EN5301 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Basic skill (or refresher) in map mathematics including basic algebra, decimals and the metric "
     "system; engineer metric and inbar scales in cartography.", "ia"),
    ("maps", "accp_en5302_cartography_ii_grid_construction_plotting_and_pr", "army",
     "Army Correspondence Course Program subcourse EN5302, edition 6",
     "Cartography 2 Grid Construction, Plotting and Projection Graticules (Army subcourse EN5302, edition 6, "
     "2004)",
     ACCP, "en-5302-cartography-ii-grid-construction-plotting-and-projection-graticules-edition-6", 2004, "pdf",
     "The Army's self-study subcourse EN5302 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instruction and hands-on training in preparing a map base to include universal transverse mercator "
     "grid construction, transverse mercator projection plotting, and plotting geodetic controls.", "ia"),
    ("maps", "accp_en5303_cartography_iii", "army", "Army Correspondence Course Program subcourse EN5303, edition 2",
     "Cartography 3 Aerial Photography (Army subcourse EN5303, edition 2, 2004)",
     ACCP, "en-5303-cartography-iii-edition-2", 2004, "pdf",
     "The Army's self-study subcourse EN5303 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions for identifying aerial photographic imagery using a pocket stereoscope; preparing an "
     "aerial photographic line index; and establishing supplementary control.", "ia"),
    ("maps", "accp_en5309_cartography_ix_map_overlays", "army",
     "Army Correspondence Course Program subcourse EN5309, edition A",
     "Cartography 9 Map Overlays (Army subcourse EN5309, edition A, 2004)",
     ACCP, "en-5309-cartography-ix-map-overlays-edition-a", 2004, "pdf",
     "The Army's self-study subcourse EN5309 (Engineer school), read whole, with its lessons, exercises and "
     "answers. Instructions on preparing map overlays. Discusses techniques, materials, equipment, and uses of map "
     "overlays.", "ia"),
    # ---------------------------------------------------------------- transportation
    ("transport", "accp_tr0636_rail_operations_yard", "army",
     "Army Correspondence Course Program subcourse TR0636, edition 7",
     "Rail Operations, Yard (Army subcourse TR0636, edition 7, 2004)",
     ACCP, "tr-0636-rail-operations-yard-edition-7", 2004, "pdf",
     "The Army's self-study subcourse TR0636 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Mission, functions, and characteristics of rail yards and terminals; switching, classification, and "
     "building up of through and local trains; operating personnel and their duties; safe operating "
     "practices.", "ia"),
    ("transport", "accp_tr0638_rail_operations_dispatching", "army",
     "Army Correspondence Course Program subcourse TR0638",
     "Rail Operations, Dispatching (Army subcourse TR0638, 2004)",
     ACCP, "tr-0638-rail-operations-dispatching", 2004, "pdf",
     "The Army's self-study subcourse TR0638 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Train dispatching principles, including methods of dispatch on single, double, and multiple lines; "
     "dispatching personnel, documentation, records, and communications; right and superiority of trains; forms of "
     "train orders and their interpretation.", "ia"),
    ("transport", "accp_tr0655_railway_rolling_stock", "army",
     "Army Correspondence Course Program subcourse TR0655, edition 4",
     "Railway Rolling Stock (Army subcourse TR0655, edition 4, 2004)",
     ACCP, "tr-0655-railway-rolling-stock-edition-4", 2004, "pdf",
     "The Army's self-study subcourse TR0655 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Railway cars; their types, wheels, axles, trucks, underframes, draft gear, couplers, airbrakes, "
     "handbrakes, and safety appliances.", "ia"),
    ("transport", "accp_tr0656_diesel_electric_locomotives", "army",
     "Army Correspondence Course Program subcourse TR0656, edition 4",
     "Diesel-Electric Locomotives (Army subcourse TR0656, edition 4, 2004)",
     ACCP, "tr-0656-diesel-electric-locomotives-edition-4", 2004, "pdf",
     "The Army's self-study subcourse TR0656 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Mechanical and electrical construction; maintenance and repair of engine, mechanical parts, and "
     "electrical system.", "ia"),
    ("transport", "accp_tr0670_railway_track_maintenance_i", "army",
     "Army Correspondence Course Program subcourse TR0670, edition 8",
     "Railway Track Maintenance 1 (Army subcourse TR0670, edition 8, 2004)",
     ACCP, "tr-0670-railway-track-maintenance-i-edition-8", 2004, "pdf",
     "The Army's self-study subcourse TR0670 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Fundamentals of railway engineering, roadbed, and drainage; the elements of track and fastenings; "
     "ties and tie treatment and rail joints; problems associated with construction and maintenance.", "ia"),
    ("transport", "accp_tr0671_railway_track_maintenance_ii", "army",
     "Army Correspondence Course Program subcourse TR0671, edition 1",
     "Railway Track Maintenance 2 (Army subcourse TR0671, edition 1, 2004)",
     ACCP, "tr-0671-railway-track-maintenance-ii-edition-1", 2004, "pdf",
     "The Army's self-study subcourse TR0671 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Track rehabilitation; use of special tools and equipment; types of switches; crossovers; diverging "
     "track maintenance and installations; types and characteristics of curves; methods of maintaining by "
     "stringlining; highway grade crossings, guard rails, and seasonal maintenance; problems of ice and snow; "
     "large-scale destruction and rehabilitation of rail plants in theaters; maintenance-of-way programming and "
     "management.", "ia"),
    ("transport", "accp_tr0690_loading_blocking_and_bracing_on_rail_cars", "army",
     "Army Correspondence Course Program subcourse TR0690, edition 3",
     "Loading, Blocking, and Bracing on Rail Cars (Army subcourse TR0690, edition 3, 2004)",
     ACCP, "tr-0690-loading-blocking-and-bracing-on-rail-cars-edition-3", 2004, "pdf",
     "The Army's self-study subcourse TR0690 (Transportation school), read whole, with its lessons, exercises and "
     "answers. Principles of loading, blocking, and bracing; pertinent rules, regulations, and publications; "
     "material requirements for blocking and bracing equipment on flatcars.", "ia"),
    ("transport", "army_fm_4_01_502_army_watercraft_safety_2008", "army", "FM 4-01.502",
     "Army Watercraft Safety (FM 4-01.502, 2008)",
     ARMY, "ost-military-doctrine-fm4_01x502", 2008, "printed",
     "The Army's watercraft safety manual (it took over from FM 55-502 of 1996, which is in the boat books), read "
     "whole.", "ia"),
    # ---------------------------------------------------------------- aviation
    ("aviation", "accp_al0907_basic_hydraulics_and_its_plumbing", "army",
     "Army Correspondence Course Program subcourse AL0907, edition A",
     "Basic Hydraulics and Hydraulic Plumbing (Army subcourse AL0907, edition A, 1994)",
     ACCP, "al-0907-basic-hydraulics-and-its-plumbing-edition-a", 1994, "printed",
     "The Army's self-study subcourse AL0907 (aviation logistics school), read whole, with its lessons, exercises "
     "and answers. Instruction on the science of hydraulics; explanation of hydraulic principles; study of the "
     "fluids used in aircraft hydraulic systems.", "ia"),
    ("aviation", "accp_al0926_basic_hydraulic_systems_and_components", "army",
     "Army Correspondence Course Program subcourse AL0926, edition A",
     "Basic Hydraulic Systems and Components (Army subcourse AL0926, edition A, 1994)",
     ACCP, "al-0926-basic-hydraulic-systems-and-components-edition-a", 1994, "printed",
     "The Army's self-study subcourse AL0926 (aviation logistics school), read whole, with its lessons, exercises "
     "and answers. Instruction on the concept and operation of the basic components of the hydraulic system. "
     "Explains flow control, actuating and discharge devices, and pressure-limiting, controlling, and sensing "
     "devices.", "ia"),
    ("aviation", "accp_al0966_basic_aerodynamics", "army",
     "Army Correspondence Course Program subcourse AL0966, edition B",
     "Basic Aerodynamics (Army subcourse AL0966, edition B, 1994)",
     ACCP, "al-0966-basic-aerodynamics-edition-b", 1994, "printed",
     "The Army's self-study subcourse AL0966 (aviation logistics school), read whole, with its lessons, exercises "
     "and answers. How and why an aircraft flies and what effect the atmosphere and flight controls have "
     "on flight.", "ia"),
    ("aviation", "accp_al0992_basic_airframe_repair", "army",
     "Army Correspondence Course Program subcourse AL0992, edition A",
     "Basic Airframe Repair (Army subcourse AL0992, edition A, 1994)",
     ACCP, "al-0992-basic-airframe-repair-edition-a", 1994, "printed",
     "The Army's self-study subcourse AL0992 (aviation logistics school), read whole, with its lessons, exercises "
     "and answers. Provides a general familiarization of the airframe of today’s aircraft and repair "
     "procedures.", "ia"),
    ("aviation", "accp_al0993_gas_turbine_engines", "army",
     "Army Correspondence Course Program subcourse AL0993, edition 5",
     "Army Aircraft Gas Turbine Engines (Army subcourse AL0993, edition 5, 2004)",
     ACCP, "al-0993-gas-turbine-engines-edition-5", 2004, "pdf",
     "The Army's self-study subcourse AL0993 (aviation logistics school), read whole, with its lessons, exercises "
     "and answers. Theory and principles of gas turbine engines; major sections of gas turbine engines; fuel and "
     "oil systems; testing procedures, inspection, maintenance, and storage of aircraft gas turbine engines; and "
     "T53, T55, Solar T62, T63, T74, and T700 engines.", "ia"),
    ("aviation", "accp_av0593_aviation_medicine", "army",
     "Army Correspondence Course Program subcourse AV0593, edition 6",
     "Aviation Medicine (Army subcourse AV0593, edition 6, 2004)",
     ACCP, "av-0593-aviation-medicine-edition-6", 2004, "pdf",
     "The Army's self-study subcourse AV0593 (aviation school), read whole, with its lessons, exercises and "
     "answers. Requirements and capabilities of the aviation medicine program, capabilities and limitations of "
     "night vision, perceptual limitations, and spatial disorientation in relation to aviation unit "
     "safety training.", "ia"),
    ("aviation", "accp_av0603_airways_code_aviation_weather_report_and_meteoro", "army",
     "Army Correspondence Course Program subcourse AV0603",
     "Airways Code Aviation Weather Report and Meteorological Terminal Aviation Report (METAR) Code (Army subcourse "
     "AV0603, 1993)",
     ACCP, "av-0603-airways-code-aviation-weather-report-and-meteorological-terminal-aviatio", 1993, "printed",
     "The Army's self-study subcourse AV0603 (aviation school), read whole, with its lessons, exercises and "
     "answers. Identification of types of aviation weather teletype sequence reports and how to decode all "
     "information in each type of report.", "ia"),
    ("aviation", "army_fm_1_563_airframe_maintenance_1991", "army", "FM 1-563",
     "Fundamentals and Procedures of Airframe Maintenance (FM 1-563, 1991)",
     ARMY, "ost-military-doctrine-fm1_563", 1991, "printed",
     "The Army's manual of the fundamentals and procedures of airframe maintenance, read whole. Its parts: Aircraft "
     "fasteners; Basic aircraft information; Aircraft structural metals; Sheet metal tools and shop equipment; "
     "Engineering drawing and blueprint reading; Forming; Rivets, special-purpose fasteners, and resistance "
     "welding; Aircraft plastics; Rebalancing movable surfaces.", "ia"),
    ("aviation", "army_fm_1_230_meteorology_for_army_aviators_1982", "army", "FM 1-230",
     "Meteorology for Army Aviators (FM 1-230, 1982)",
     ARMY, "ost-military-doctrine-fm1_230", 1982, "printed",
     "The Army's weather manual for aviators, read whole. Its parts: The atmosphere; Temperature; Moisture; "
     "Atmospheric; Atmospheric circulation; Stability and instability; Clouds; Air masses; Frontal weather; "
     "Turbulence; Thunderstorms; Icing; Polar and subpolar weather; Tropical weather; Preflight planning; In-flight "
     "planning; Teletype information.", "ia"),
    # ---------------------------------------------------------------- fire, rescue and diving
    ("rescue", "army_fm_5_415_fire_fighting_operations_1999", "army", "FM 5-415",
     "Fire-Fighting Operations (FM 5-415, 1999)",
     ARMY, "fm-5-415-fire-fighting-operations-1999", 1999, "record",
     "The Army's manual of fire-fighting operations, read whole. Its parts: Fire-fighting basics; Organization, "
     "Responsibilities, and Equipment; Command and Control; Wartime operations; Fire-prevention operations; "
     "Water-tanker resupply operations; Aircraft crash/rescue fire-fighting operations; Structural fire-fighting "
     "operations; Miscellaneous facility-based fire-fighting operations; HAZMAT Incidents and Fire Procedures; "
     "Aircraft prefire plans; Ammunition identification chart.", "ia"),
    ("rescue", "usaf_cdc_57150_fire_protection_specialist_1979", "usaf",
     "Career Development Course CDC 57150 (Military Curriculum Materials 17-12) (ERIC document ED195778)",
     "Fire Protection Specialist (Air Force Career Development Course 57150, 1979)",
     "Air Force School of Applied Aerospace Sciences, Chanute Air Force Base; selected by the National Center for "
     "Research in Vocational Education",
     "ERIC_ED195778", 1979, "eric",
     "The Air Force's career development course for fire protection specialists (five volumes: general subjects for "
     "fire protection, fire engineering and investigation, first aid and rescue, fire protection vehicles, and "
     "structural firefighting, as its ERIC record lists them), read whole, with review exercises. The machine-read "
     "text of this microfiche scan has many mistakes.", "eric", "MCM"),
    ("rescue", "uscg_helicopter_rescue_swimmer_manual_2018", "uscg", "COMDTINST M3710.4 series",
     "Helicopter Rescue Swimmer Manual (US Coast Guard, 2018)",
     "US Coast Guard", "helicopter-rescue-swimmer-manual-us-coast-guard", 2018, "printed",
     "The Coast Guard's manual for its helicopter rescue swimmers, read whole. Its parts: Policies and "
     "requirements; Helicopter rescue swimmer training requirements; Procedures.", "ia"),
    ("rescue", "uscg_boating_safety_course_1981", "uscg",
     "Military Curriculum Materials 15-6 (a Coast Guard course) (ERIC document ED232029)",
     "Boating Safety (Coast Guard course, Military Curriculum Materials 15-6, 1981)",
     "US Coast Guard; selected by the National Center for Research in Vocational Education",
     "ERIC_ED232029", 1981, "eric",
     "The Coast Guard's boating safety course, read whole. The machine-read text of this microfiche scan has many "
     "mistakes.", "eric", "MCM"),
    ("rescue", "army_fm_3_34_280_engineer_diving_operations_2004", "army", "FM 3-34.280",
     "Engineer Diving Operations (FM 3-34.280, 2004)",
     ARMY, "ost-military-doctrine-fm3_34x280", 2004, "printed",
     "The Army's manual of engineer diving operations, read whole; any part about underwater demolition or "
     "explosives is left out. Its parts: Engineer diving missions; Engineer diving organizations; Employment of "
     "Engineer Divers; Considerations.", "ia"),
]

PDFS = [entry(*row) for row in ROWS]


def trade_keys(trade):
    """The keys of one trade's books, in the order of ROWS."""
    return [f"{PREFIX}:{p['name']}" for p in PDFS if p["trade"] == trade]


# ====================================================================== the index
# Per trade: the request word of its books, the books already in the library on the same trade (by key or by their
# request word), and links for what is left out.
RELATED = {
    "food": [("word", "cookbooks", "The cookbooks, with the Army's Army Recipes (TM 10-412, 1946) and The Army Cook "
                                   "(TM 10-405, 1942)"),
             ("key", "pdf:army_fm_10_23_field_feeding_1996", "Army Field Feeding and Class I Operations (FM 10-23)"),
             ("key", "pdf:navy_culinary_specialist", "The Navy's Culinary Specialist course (NAVEDTRA 15008)"),
             ("word", "outdoor-cooking", "Emergency, camp and outdoor cooking"),
             ("word", "preserving", "Home food preserving")],
    "vet": [("word", "pet-care", "Pet care"), ("word", "homestead", "Homesteading and small livestock")],
    "medical": [("key", "pdf:army_fm_4_25_11_first_aid", "First Aid (FM 4-25.11)"),
                ("key", "pdf:army_fm_21_11_first_aid_1989", "First Aid for Soldiers (FM 21-11, 1989)"),
                ("key", "pdf:navy_hospital_corpsman", "The Navy's Hospital Corpsman course (NAVEDTRA 14295)"),
                ("key", "firstaid:army_st_31_91b_special_forces_medical", "Special Forces Medical Handbook "
                                                                         "(ST 31-91B)"),
                ("key", "pdf:army_tc_4_02_3_field_hygiene_2015", "Field Hygiene and Sanitation (TC 4-02.3, 2015)"),
                ("key", "pdf:army_fm_4_25_12_field_sanitation", "Unit Field Sanitation Team (FM 4-25.12)"),
                ("key", "boat:uscg_bch_first_aid", "The Coast Guard's Boat Crew Handbook: First Aid"),
                ("word", "first-aid", "Emergency and wilderness first aid"),
                ("word", "wilderness-first-aid", "Wilderness first aid and backcountry safety"),
                ("word", "dental-care", "Dental care"), ("word", "home-health", "Home health and caregiving")],
    "mech": [("key", "gpo:army_tm_9_8000_1985", "Principles of Automotive Vehicles (TM 9-8000, 1985)"),
             ("key", "gpo:army_tm_9_6140_200_14_batteries_1998", "Lead-acid storage batteries (TM 9-6140-200-14)"),
             ("key", "gpo:army_tm_9_1870_1_tires_1955", "Care and Maintenance of Pneumatic Tires (TM 9-1870-1)"),
             ("key", "pdf:navy_construction_mechanic_advanced", "The Navy's Construction Mechanic, Advanced"),
             ("key", "pdf:navy_equipment_operator_basic", "The Navy's Equipment Operator, Basic"),
             ("key", "make:army_tc_9_524_machine_tools", "Fundamentals of Machine Tools (TC 9-524)"),
             ("key", "make:army_tm_10_445_machinist_1941", "The Machinist (TM 10-445, 1941)"),
             ("key", "build:army_tm_9_243_hand_tools", "Use and Care of Hand Tools and Measuring Tools (TM 9-243)"),
             ("key", "pdf:navy_basic_machines", "Basic Machines (NAVEDTRA 14037)"),
             ("key", "power:army_tm_9_6115_641_10_mep802a", "The 5 kW tactical quiet generator (TM 9-6115-641-10)")],
    "build": [("key", "build:army_fm_5_426_carpentry", "Carpentry (FM 5-426, 1995)"),
              ("key", "build:army_fm_5_428_concrete_masonry", "Concrete and Masonry (FM 5-428, 1998)"),
              ("key", "build:navy_builder_3_2_1981", "The Navy's Builder 3 & 2 (1981)"),
              ("key", "build:navy_blueprint_reading", "Blueprint Reading and Sketching (NAVEDTRA 14040)"),
              ("key", "power:army_fm_5_424_electrical_systems_1997", "Theater of Operations Electrical Systems "
                                                                     "(FM 5-424)"),
              ("key", "pdf:army_fm_5_125_rigging", "Rigging Techniques (FM 5-125)"),
              ("word", "building", "Light construction books"), ("word", "backup-power", "Backup power")],
    "qm": [("key", "kmil:army_fm_25_7_pack_transportation_1944", "Pack Transportation (FM 25-7, 1944)"),
           ("key", "pdf:army_fm_5_125_rigging", "Rigging Techniques (FM 5-125)"),
           ("word", "knots-military", "The military and Coast Guard knot, rope and pack manuals")],
    "comms": [("key", "radio:army_fm_24_19_radio_operators_handbook", "Radio Operator's Handbook (FM 24-19)"),
              ("key", "radio:army_tm_11_666_antennas_propagation", "Antennas and Radio Propagation (TM 11-666)"),
              ("key", "radio:usmc_mcrp_3_40_3c_antenna_handbook", "The Marine Corps antenna handbook (MCRP 3-40.3C)"),
              ("key", "pdf:navy_ac_and_transformers", "Introduction to Alternating Current and Transformers "
                                                      "(NEETS)"),
              ("word", "radio", "Radio rules, question pools and radio manuals"),
              ("word", "electronics", "Electronics repair books, with the Navy's NEETS modules")],
    "admin": [("word", "money-work", "Money and work: IRS, CFPB and Labor Department guides")],
    "maps": [("key", "pdf:army_fm_3_25_26_map_reading", "Map Reading and Land Navigation (FM 3-25.26, 2001)")],
    "transport": [("key", "drive:army_tc_21_305_20", "Manual for the Wheeled Vehicle Operator (TC 21-305-20)"),
                  ("key", "gpo:army_tc_21_305_100_cdl_1996", "The Military Commercial Driver's License Manual"),
                  ("key", "boat:army_fm_55_501_marine_crewman_1999", "Marine Crewman's Handbook (FM 55-501)"),
                  ("word", "small-boats", "Small boats: rules, Coast Guard and Army boat manuals"),
                  ("word", "driving", "Driving and road rules")],
    "aviation": [("key", "milw:usaf_afh_10_644_sere_2017", "The Air Force's survival textbook (AFH 10-644)")],
    "rescue": [("key", "boat:uscg_bch_rescue_survival", "The Coast Guard's Boat Crew Handbook: Rescue and Survival"),
               ("key", "kmil:uscg_bch_seamanship_fundamentals", "The Coast Guard's Boat Crew Handbook: Seamanship"),
               ("word", "military-whole", "Whole military manuals: survival, Seabee and Navy basics")],
}


def sections():
    """The index's parts: one per trade (its request word, its books by key, the related books), then the other
    services' notes."""
    out = []
    for trade, (word, title, _safety, covers) in TRADES.items():
        items = [("word", word, f"Every book of this trade (request word {word})")]
        items += [("key", f"{PREFIX}:{p['name']}", p["title"]) for p in PDFS if p["trade"] == trade]
        items += RELATED.get(trade, [])
        out.append((title, covers, items))
    out.append(("Left out, and where to find it", "Courses that are restricted or not openly published: open them "
                "in a browser, or fetch them for your own use with Program Downloader.",
                [("link", name, url, why) for name, url, why in LINKS]))
    return out


# Sources the owner can open himself (link-only): restricted or not openly published, or not readable by the builder.
LINKS = [
    ("Air Force e-Publishing (career development courses and handbooks)", "https://www.e-publishing.af.mil/",
     "the Air Force's own library; most career development courses are restricted to Air Force members, and the "
     "site refuses automated readers"),
    ("Army Publishing Directorate", "https://armypubs.army.mil/",
     "the Army's own library of current manuals; its robots.txt shuts out automated readers"),
    ("Coast Guard Directives (manuals such as the Boat Crew Seamanship Manual)",
     "https://www.dcms.uscg.mil/directives/",
     "the Coast Guard's own library; it refuses automated readers"),
    ("Marine Corps Institute and MarineNet", "https://www.marines.mil/",
     "today's Marine Corps distance courses are on MarineNet, which needs a Marine Corps login"),
]

SECTIONS = sections()
INDEX = X.index_maker(PREFIX, GROUP, "Job skills from US military training manuals: a guide to the library",
                      "Job skills (US military training manuals)",
                      "A guide to the job-skill training manuals of the US Army, Marine Corps, Air Force and Coast "
                      "Guard in the library, one part per trade, with the related books already in the library and "
                      "links for what is left out.", SECTIONS)
MAKERS = {"index": INDEX}

WORDS = {ALL_WORD: lambda: [f"{PREFIX}:index"] + [f"{PREFIX}:{p['name']}" for p in PDFS]}
for _trade, (_word, *_rest) in TRADES.items():
    WORDS[_word] = (lambda t: lambda: trade_keys(t))(_trade)
COLLECTION = K.Collection(PREFIX, GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "service_skills": "Internet Archive copies of US Army, Marine Corps, Air Force and Coast Guard training manuals "
                      "(Army Correspondence Course Program subcourses, soldier's, technical and field manuals, "
                      "training circulars and technical bulletins): works of the US government (17 U.S.C. 105), each "
                      "judged at every build by the release rule for military publications (military_release.py); "
                      "every copy was opened on 2026-11-23: a text layer on its pages, a year printed on its front "
                      "pages (or, for the Medical Department's subcourses, which print none, the year in the PDF's "
                      "own information), and no restricted or classified marking on its front pages. archive.org's "
                      "robots.txt allows the files and has no AI rules (checked 2026-11-23).",
    "service_skills_eric": "ERIC copies on the Internet Archive (collection ericarchive, a mirror of eric.ed.gov, the "
                           "US Department of Education's library, which publishes them openly): the Marine Corps "
                           "Institute's correspondence courses (works of the US Marine Corps) and four Military "
                           "Curriculum Materials courses of the Air Force and Coast Guard (works of the US government; "
                           "the National Center for Research in Vocational Education's cover note says copyrighted "
                           "materials were omitted or used with approval, and each notice says so); checked "
                           "2026-11-23.",
    "service_skills_index": "The index (skill:index) is the toolkit's own facts and links, CC0.",
}

ACCP_SEARCH = "https://archive.org/search?query=subject%3Aaccp"
NOT_INCLUDED = [
    ("Army Correspondence Course Program subcourses on explosives, mines, ammunition, weapons and tactics (EN5501 "
     "and EN5503 Land Mine Warfare, the MM ammunition subcourses, CM3209 Flame Field Expedients, EN5463 and EN5464 "
     "Quarry Operations, the OD machine-gun maintenance subcourses, and the IN infantry, IT intelligence, MP military "
     "police and AD air defence subcourses)", "Explosives, mines, blasting and incendiaries are never built "
     "(build_textbooks.NOT_FIELD_SAFE), and a subcourse that is wholly about them has nothing left; the weapons, "
     "tactics, intelligence and police subcourses are not job skills for this collection. Index: " + ACCP_SEARCH),
    ("Older editions of the Medical Department's subcourses (edition 100 where an edition 200 exists) and of other "
     "subcourses", "The newest edition on the Internet Archive is built; an older one only when it covers a skill the "
     "newer one dropped. Index: " + ACCP_SEARCH),
    ("Army subcourses kept out to stay within 256 books: the radiology (MD0950 to MD0959), medical equipment repair "
     "(MD0353 to MD0373), blood donor, quality assurance and ethics subcourses, the special surgical procedures, the "
     "television, video and photography subcourses (SS0507 to SS0607), the radar, test equipment and telephone "
     "switching subcourses, the paving, quarry, soils and geology subcourses, and the rail planning subcourses",
     "Each request word holds at most 256 books, so the most practical trades were chosen; these are on the Internet "
     "Archive for the owner to fetch himself (the photography subcourses beside the photography books, photo:). "
     "Index: " + ACCP_SEARCH),
    ("Air Force career development courses (CDCs) and most Air Force handbooks", "Most CDCs are restricted to Air "
     "Force members, and the Air Force's own library (e-Publishing) refuses automated readers (403, checked "
     "2026-11-23); the only openly published CDC found, Fire Protection Specialist (CDC 57150, 1979, from ERIC), is "
     "built. Link-only. Index: https://www.e-publishing.af.mil/"),
    ("Current Army manuals from the Army Publishing Directorate (armypubs.army.mil)", "Its robots.txt shuts out every "
     "automated reader (\"Disallow: /\", checked 2026-11-23), so only Internet Archive copies are read; the current "
     "editions are link-only for the owner. Index: https://armypubs.army.mil/"),
    ("Coast Guard rating performance qualification guides, the Boat Crew Seamanship Manual and the Coast Guard "
     "Auxiliary's training manuals", "The Coast Guard's sites refuse automated readers, and no openly published copy "
     "with a text layer was found on the Internet Archive (searched 2026-11-23); the Auxiliary's course books are its "
     "own and sold. The Boat Crew Handbooks are in the boat books (kmil:, boat:). Index: "
     "https://www.dcms.uscg.mil/directives/"),
    ("Parachute Rigger rate training manuals (US Navy, 1951 and 1957) and the Parachute Rigger Handbook", "They are "
     "several PDFs in one Internet Archive item, and the builder reads one PDF per item; the Navy's rate training "
     "manuals are a separate collection. Index: https://archive.org/details/parachute-rigging-technical-manuals"),
    ("Military Curriculum Materials (ERIC) other than the four built", "About 200 courses of the 1970s from all the "
     "services, scanned from microfiche (the machine-read text has many mistakes), whose cover note says some "
     "copyrighted materials were used with approval; four that fill Air Force and Coast Guard gaps are built. "
     "Index: https://archive.org/search?query=%22Military+Curriculum+Materials%22+collection%3Aericarchive"),
    ("Marine Corps distance courses today (MarineNet)", "They need a Marine Corps login; the Marine Corps "
     "Institute's 1980s courses that ERIC publishes are built. Index: https://www.marines.mil/"),
    ("Older Army trade manuals the newer ones replaced: FM 5-420 Plumbing and Pipefitting (1993), TM 5-297 Well "
     "Drilling (1943) and FM 5-166 Well Drilling Operations (1975), FM 10-43M Fabric Repair Specialist (1978 to "
     "1981), FM 10-94B Food Service Specialist (1977 to 1981), TM 10-350 and TM 10-352 laundry manuals (1940 to "
     "1943), TM 9-237 Welding Theory (1967)", "FM 3-34.471 (2001), FM 5-484 (1994), FM 10-16 (2000), the cook's "
     "soldier's manuals (2003 and 2004), FM 42-414 (1998) and the welding subcourses are built instead. Index: "
     "https://archive.org/search?query=%22FM+5-420%22"),
    ("Army engineering design manuals (TM 5-8xx: water supply, wastewater, roads and foundations design)", "Design "
     "criteria for engineers rather than trade skills; kept out to stay within 256 books. Index: "
     "https://archive.org/details/ost-military-engineering-tm5_813_3"),
    ("Map Reading and Land Navigation (TC 3-25.26, 2013)", "Its front pages print \"Distribution authorized to U.S. "
     "government agencies and their contractors only\", and no government site publishes it openly: personal use "
     "only, never built, for the owner to fetch himself with Program Downloader; FM 3-25.26 (2001) is in the field "
     "manuals (pdf:army_fm_3_25_26_map_reading). Index: "
     "https://archive.org/details/map-reading-and-land-navigation-tc-3-25-26"),
    ("FM 5-34 Engineer Field Data (1999 printing with change 3)", "Its front pages print a restricted marking "
     "(personal use only), and it is mostly combat engineering. Index: "
     "https://archive.org/details/fm-5-34-engineer-field-data-w-change-3-1999"),
    ("Army subcourses whose copies cannot be read aloud or dated: OD0611 Principles of Automotive Electricity, OD1403 "
     "Shop Safety, EN0113 Construction Print Reading and TR0635 Military Train Operation (most pages are pictures "
     "without words); QM0471 Preparation and Serving of Special Food Items, EN5262 Construction Equipment Steering "
     "Systems, AV0900 Locate Coordinates on Aeronautical Charts, MM0311 Electron Tubes, MM0320 Communications "
     "Fundamentals, MM0706 Electronics 2, SS0330 Telephone and Telegraph Transmission and MM0701 Transistors and "
     "Semiconductors (no date printed, and their PDFs were remade recently, so the edition's year is not known)",
     "Left out until a copy with a text layer and a known year is found (checked 2026-11-23); the subcourses beside "
     "them cover the same trades. Index: " + ACCP_SEARCH),
    ("Aviation Survival, parts I to IV (Army subcourses AV0661 to AV0664)", "Two parts print no date and two copies "
     "were made by a shop (its address printed in the PDF); survival is in the library already (milw:, fieldmanuals). "
     "Index: " + ACCP_SEARCH),
    ("U.S. Air Force Survival Handbook (2008)", "A commercial publisher's edition, on the Internet Archive only as a "
     "lending-library scan; the Air Force's own survival textbook (AFH 10-644) is built whole in milw:. Index: "
     "https://archive.org/details/usairforcesurviv0000unit"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
