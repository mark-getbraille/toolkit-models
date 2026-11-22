"""More reference books for the textbooks builder, from the reference inventory's top 50 (2026-11-21): FAA aviation
handbooks, more US Navy rate training manuals and non-weapon Army field manuals, NIST weights-and-measures
handbooks, more CFR parts (FTC consumer rules, drug labelling, Medicare, truck drivers), and the UK National
Archives' teaching resources. sources.py imports this module and adds its lists to PDF_DOCS, LAWS, LAWS_MORE,
GOV_GUIDES, NOT_INCLUDED, LICENCE_LINES and PRACTICE_SUBJECTS, so the builder needs no change (keys pdf:<name>,
law:<name>, guide:<name>, and the group keys such as fieldmanuals, courses, government, laws, laws-more).

The periodical-style sources of the same inventory (GAO reports, the United States Government Manual, ERIC full
texts, Canadian Open Government Licence publications, GOV.UK guides and UK safety alerts, USDA Farmers' Bulletins)
are in publications_more.py.

Every source was checked by hand on 2026-11-21; the builder checks the licence again at every build (the licence
page's line; for military manuals, the release rule of military_release.py on the PDF's front matter) and obeys
each site's robots.txt.
"""

# These names are the same as in sources.py (this module is imported at its end, so it cannot import them).
US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"
GOVINFO_POLICY = "https://www.govinfo.gov/about/policies"
GOVINFO_TEXT = r"Copyright protection under this title is not available for any work of the United States Government"
OGL_UK_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

US_PDF = dict(country="United States", licence=US_GOV, licence_url=US_GOV_URL, licence_page=GOVINFO_POLICY,
              licence_text=GOVINFO_TEXT)

# ---------------------------------------------------------------------- FAA aviation handbooks (item 6)
# faa.gov/regulations_policies/handbooks_manuals/aviation (robots.txt allows; read 2026-11-21). The FAA publishes no
# copyright page of its own: like the IRS and Medicare books, the licence line checked is govinfo's quotation of 17
# U.S.C. 105 (works of the US government are not under copyright). Each PDF has a text layer.
FAA = "https://www.faa.gov"
FAA_FILES = FAA + "/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation"
FAA_PAGE = FAA + "/regulations_policies/handbooks_manuals/aviation"
AVIATION = dict(US_PDF, group="government", publisher="Federal Aviation Administration (FAA), US Department of "
                "Transportation", page=FAA_PAGE)


def _faa(name, title, pdf, subject, description, published=""):
    """One FAA handbook as a PDF_DOCS entry."""
    entry = dict(AVIATION, name=name, title=title, pdf=pdf, subject=subject, description=description)
    if published:
        entry["published"] = published
    return entry


FAA_HANDBOOKS = [
    _faa("faa_pilots_handbook_aeronautical_knowledge", "Pilot's Handbook of Aeronautical Knowledge (FAA-H-8083-25C)",
         FAA_PAGE + "/faa-h-8083-25c.pdf", "Aviation",
         "The FAA's basic book for pilots: aircraft structure, principles of flight, flight controls, systems, "
         "instruments, weight and balance, performance, weather, airport operations, airspace, navigation and "
         "aeromedical factors."),
    _faa("faa_airplane_flying_handbook", "Airplane Flying Handbook (FAA-H-8083-3C)",
         FAA_FILES + "/airplane_handbook/00_afh_full.pdf", "Aviation",
         "How to fly an airplane: ground operations, basic flight maneuvers, takeoffs and landings, performance "
         "maneuvers, night operations, transition to other airplanes, and emergencies."),
    _faa("faa_instrument_flying_handbook", "Instrument Flying Handbook (FAA-H-8083-15B)",
         FAA_FILES + "/FAA-H-8083-15B.pdf", "Aviation",
         "Flying by instruments: human factors, aerodynamics, flight instruments, attitude instrument flying, "
         "navigation systems, the air traffic control system and IFR emergencies."),
    _faa("faa_instrument_procedures_handbook", "Instrument Procedures Handbook (FAA-H-8083-16B)",
         FAA_FILES + "/instrument_procedures_handbook/FAA-H-8083-16B.pdf", "Aviation",
         "Instrument procedures in the National Airspace System: departures, en route, arrivals and approaches."),
    _faa("faa_aviation_weather_handbook", "Aviation Weather Handbook (FAA-H-8083-28B)", FAA + "/sites/faa.gov/files/"
         "FAA-H-8083-28B.pdf", "Weather",
         "The FAA's book of weather for pilots and everyone curious about it: the atmosphere, wind, clouds, "
         "thunderstorms, icing, turbulence, fog, and how weather observations and forecasts are made and read."),
    _faa("faa_risk_management_handbook", "Risk Management Handbook (FAA-H-8083-2A)", FAA + "/sites/faa.gov/files/"
         "2022-06/risk_management_handbook_2A.pdf", "Aviation safety",
         "How pilots identify hazards, assess risk and make decisions: checklists, single-pilot resource "
         "management, automation and situational awareness."),
    _faa("faa_weight_and_balance_handbook", "Aircraft Weight and Balance Handbook (FAA-H-8083-1)",
         FAA_FILES + "/FAA-H-8083-1.pdf", "Aviation",
         "Weighing aircraft and working out their center of gravity, for airplanes and helicopters."),
    _faa("faa_aviation_instructors_handbook", "Aviation Instructor's Handbook (FAA-H-8083-9)",
         FAA_FILES + "/aviation_instructors_handbook/aviation_instructors_handbook.pdf", "Teaching and learning",
         "How people learn and how to teach them: the learning process, communication, assessment, planning "
         "lessons and flight instruction."),
    _faa("faa_helicopter_flying_handbook", "Helicopter Flying Handbook (FAA-H-8083-21)",
         FAA_FILES + "/helicopter_flying_handbook/helicopter_flying_handbook.pdf", "Aviation",
         "How helicopters fly and how to fly them: aerodynamics, flight controls, systems, maneuvers and "
         "emergencies."),
    _faa("faa_glider_flying_handbook", "Glider Flying Handbook (FAA-H-8083-13)", FAA + "/sites/faa.gov/files/"
         "Glider-Flying-Handbook.pdf", "Aviation", "Gliders and soaring: components, aerodynamics, instruments, "
         "launch and recovery, soaring weather and techniques, and cross-country soaring."),
    _faa("faa_weight_shift_control_handbook", "Weight-Shift Control Aircraft Flying Handbook (FAA-H-8083-5)",
         FAA_FILES + "/FAA-H-8083-5.pdf", "Aviation", "Trikes (weight-shift control light-sport aircraft): how "
         "they fly, preflight, takeoffs, landings and emergencies."),
    _faa("faa_powered_parachute_handbook", "Powered Parachute Flying Handbook (FAA-H-8083-29)",
         FAA_FILES + "/powered_parachute_handbook.pdf", "Aviation", "Powered parachutes: the wing, the cart, "
         "preflight, flight and emergency procedures."),
    _faa("faa_plane_sense", "Plane Sense: General Aviation Information (FAA-H-8083-19A)",
         FAA_FILES + "/faa-h-8083-19A.pdf", "Aviation", "A plain introduction for aircraft owners: buying, "
         "registering, maintaining and operating a general aviation aircraft."),
    _faa("faa_amt_general_handbook", "Aviation Maintenance Technician Handbook: General (FAA-H-8083-30)",
         FAA_PAGE + "/amtg_handbook.pdf", "Aircraft maintenance",
         "The general book for aircraft mechanics: mathematics, physics, electricity, materials, hardware, "
         "inspection, ground handling, regulations and human factors."),
    _faa("faa_amt_airframe_handbook", "Aviation Maintenance Technician Handbook: Airframe (FAA-H-8083-31B)",
         FAA_PAGE + "/FAA-H-8083-31B_Aviation_Maintenance_Technician_Handbook.pdf", "Aircraft maintenance",
         "Aircraft structures, assembly and rigging, sheet metal, composites, welding, fabric, painting, "
         "hydraulics, landing gear, fuel, electrical, instrument and cabin systems."),
    _faa("faa_amt_powerplant_handbook", "Aviation Maintenance Technician Handbook: Powerplant (FAA-H-8083-32)",
         FAA_PAGE + "/amt_powerplant_handbook.pdf", "Aircraft maintenance",
         "Aircraft engines: reciprocating and turbine engines, fuel, induction, ignition, starting, lubrication, "
         "cooling and propellers."),
]

# ---------------------------------------------------------------------- US Navy rate training manuals (item 10)
# Internet Archive copies with a text layer (the ERIC and Digital Library of India scans have their OCR words).
# Like the Navy courses already built, each is judged at every build by the release rule for military publications
# (distribution_a; military_release.py, the owner's decision of 22 November 2026): built with or without
# Distribution Statement A, its notice saying truthfully which; a restricted marking only when the government
# publishes that copy itself. US government works (17 U.S.C. 105). Checked on 2026-11-21: the six below print the
# statement; the 1970s ERIC copies (Builder, Construction Electrician, Utilitiesman, Engineman, Electrician's Mate,
# Fireman) do not, and come in under the new rule (NAVY_RATE_MANUALS_NO_STATEMENT below). Seaman, Damage
# Controlman and Basic Military Requirements were not found on the Internet Archive with a text layer.
COURSE = dict(group="course", country="United States", licence=US_GOV, licence_url=US_GOV_URL, distribution_a=True,
              publisher="Naval Education and Training Command (US Navy)")


def _navy(name, title, archive, subject, description, published):
    """One Navy rate training manual as a PDF_DOCS entry."""
    return dict(COURSE, name=name, title=title, archive=archive, subject=subject, description=description,
                published=published)


NAVY_RATE_MANUALS = [
    _navy("navy_military_requirements_po3", "Military Requirements for Petty Officer Third Class (NAVEDTRA 12044, "
          "1991)", "militaryrequirem015037mbp", "Leadership and Navy life",
          "Leadership, supervision and training, Navy programmes, security, safety and the duties of a petty "
          "officer.", "1991"),
    _navy("navy_quartermaster_1_c", "Quartermaster 1 and C (NAVEDTRA 12122, 1991)", "quatermaster1and015200mbp",
          "Navigation", "Navigation and seamanship for quartermasters: charts and publications, piloting, "
          "celestial and electronic navigation, tides and currents, and weather.", "1991"),
    _navy("navy_construction_mechanic_advanced", "Construction Mechanic, Advanced (NAVEDTRA 14050, 1992)",
          "navedtra-14050-construction-mechanic-advanced-1992", "Automotive and heavy equipment repair",
          "Engines, fuel and electrical systems, power trains, brakes, hydraulics and shop management for "
          "construction mechanics.", "1992"),
    _navy("navy_equipment_operator_basic", "Equipment Operator, Basic (NAVEDTRA 14081, 1994)",
          "navedtra-14081-equipment-operator-basic-1994", "Heavy equipment",
          "Operating trucks, tractors, loaders, graders, cranes and forklifts safely; their maintenance; and "
          "earthwork.", "1994"),
    _navy("navy_ac_and_transformers", "Introduction to Alternating Current and Transformers (NAVEDTRA 14174, 1998)",
          "navedtra-14174-introduction-to-alternating-current-and-transformers-1998", "Electricity",
          "Alternating current, inductance, capacitance, impedance, power and transformers.", "1998"),
    _navy("navy_opticalman_3_2", "Opticalman 3 & 2 (NAVEDTRA 10215, 1989)", "opticalman32nave015103mbp",
          "Optics and instrument repair", "Light and optics, optical instruments (binoculars, telescopes, "
          "periscopes), and their repair and maintenance.", "1989"),
]

# ---------------------------------------------------------------------- Army field manuals, non-weapon (item 11)
# The Kiwix catalogue already offers the whole Army Publishing Directorate (armypubs_en_all). These are Internet
# Archive copies (Distribution Statement A in their front matter, checked 2026-11-21; judged again at every build by
# the release rule, military_release.py) of field hygiene manuals not already built; weapons and tactics parts are
# left out by the builder (NOT_FIELD_SAFE).
FIELD = dict(group="fieldmanual", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
             distribution_a=True, publisher="Headquarters, Department of the Army")
ARMY_MANUALS = [
    dict(FIELD, name="army_fm_21_10_field_hygiene_2000", title="Field Hygiene and Sanitation (FM 21-10, 2000)",
         subject="Field hygiene and sanitation", archive="FM21-10_2000", published="2000",
         description="Every soldier's field hygiene manual: personal hygiene and physical fitness, water, food, "
                     "waste disposal, insects, rodents and other pests, and heat, cold and noise injuries."),
    dict(FIELD, name="army_tc_4_02_3_field_hygiene_2015", title="Field Hygiene and Sanitation (TC 4-02.3, 2015)",
         subject="Field hygiene and sanitation", archive="tc-4-02.3-field-hygiene-and-sanitation-may-2015",
         published="2015-05", description="The 2015 Army field hygiene manual: preventing disease and injury in "
         "the field, safe water and food, waste, pests, and heat and cold injuries."),
]

# ---------------------------------------------------------------------- NIST weights-and-measures handbooks (33)
# nvlpubs.nist.gov (no robots.txt rules); NIST works are US government works. The 2025 editions (a new one comes
# out each year; change the year here when it does).
NIST = dict(US_PDF, group="government", publisher="National Institute of Standards and Technology (NIST), Office "
            "of Weights and Measures", page="https://www.nist.gov/pml/owm/publications")
NIST_HANDBOOKS = [
    dict(NIST, name="nist_handbook_44_2025", title="NIST Handbook 44: Specifications, Tolerances, and Other Technical "
         "Requirements for Weighing and Measuring Devices (2025)", subject="Weights and measures", published="2025",
         pdf="https://nvlpubs.nist.gov/nistpubs/hb/2025/NIST.HB.44-2025.pdf",
         description="The US rules for scales, gas pumps, meters and other commercial weighing and measuring "
                     "devices, as adopted by the states."),
    dict(NIST, name="nist_handbook_130_2025", title="NIST Handbook 130: Uniform Laws and Regulations in the Areas of "
         "Legal Metrology and Fuel Quality (2025)", subject="Weights and measures; packaging and labelling",
         published="2025", pdf="https://nvlpubs.nist.gov/nistpubs/hb/2025/NIST.HB.130-2025.pdf",
         description="The model laws and regulations on packaging and labelling, method of sale, unit pricing, "
                     "fuel quality and weights-and-measures enforcement."),
    dict(NIST, name="nist_handbook_133_2025", title="NIST Handbook 133: Checking the Net Contents of Packaged Goods "
         "(2025)", subject="Weights and measures; packaging and labelling", published="2025",
         pdf="https://nvlpubs.nist.gov/nistpubs/hb/2025/NIST.HB.133-2025.pdf",
         description="How inspectors check that packages hold the amount their labels say."),
]

# ---------------------------------------------------------------------- statute compilations (item 24)
# govinfo.gov's COMPS collection: the Social Security Act as amended, title by title, with its OWN section numbers
# (people cite "section 1614", which the US Code renumbers as 42 U.S.C. 1382c). Package ids read from govinfo's
# MODS records on 2026-11-21. The compilations are kept current by the House Office of the Legislative Counsel.
COMPS = dict(US_PDF, group="law", publisher="Office of the Legislative Counsel, US House of Representatives (statute "
             "compilations, from govinfo.gov)", subject="Social Security")


def _comps(number, name, title, description):
    """One statute compilation (a govinfo COMPS package) as a PDF_DOCS entry."""
    return dict(COMPS, name=name, title=title, description=description,
                pdf=f"https://www.govinfo.gov/content/pkg/COMPS-{number}/pdf/COMPS-{number}.pdf",
                page=f"https://www.govinfo.gov/app/details/COMPS-{number}")


STATUTE_COMPILATIONS = [
    _comps(8755, "comps_social_security_act_title_2", "Social Security Act, Title II: Old-Age, Survivors, and "
           "Disability Insurance Benefits (as amended)", "The Social Security Act's retirement, survivors and "
           "disability insurance title, as amended, with the Act's own section numbers (sections 201 to 234)."),
    _comps(8766, "comps_social_security_act_title_16", "Social Security Act, Title XVI: Supplemental Security Income "
           "for the Aged, Blind, and Disabled (as amended)", "The SSI title of the Social Security Act, as amended, "
           "with the Act's own section numbers (sections 1601 to 1637)."),
    _comps(8768, "comps_social_security_act_title_18", "Social Security Act, Title XVIII: Health Insurance for the "
           "Aged and Disabled (Medicare, as amended)", "Medicare's law: Parts A, B, C and D of the Social Security "
           "Act as amended, with the Act's own section numbers (sections 1801 to 1899)."),
    _comps(8765, "comps_social_security_act_title_19", "Social Security Act, Title XIX: Grants to States for Medical "
           "Assistance Programs (Medicaid, as amended)", "Medicaid's law: the Social Security Act's Title XIX as "
           "amended, with the Act's own section numbers (sections 1900 to 1946)."),
]

PDF_DOCS = FAA_HANDBOOKS + NAVY_RATE_MANUALS + ARMY_MANUALS + NIST_HANDBOOKS + STATUTE_COMPILATIONS

# ---------------------------------------------------------------------- more CFR parts (item 16)
# govinfo.gov annual editions (checked 2026-11-21: every part below is in the 2025 edition at these volumes).
# Fields as sources._cfr; the entries are made by sources.py with its own _cfr (see the end of sources.py).
# (name, title, subject, title number, volume, part, description[, more parts]) ; "more": [(title, volume, part)].
CFR_LAWS = [
    ("cfr_16_453_funeral_rule", "The Funeral Rule (16 CFR part 453)", "Consumer rights", 16, 1, 453,
     "The Federal Trade Commission's Funeral Industry Practices rule: price lists, embalming, caskets and what "
     "funeral providers must tell you."),
    ("cfr_16_700_warranties", "Consumer product warranties (16 CFR parts 700 to 703, Magnuson-Moss)",
     "Consumer rights", 16, 1, 700, "The Federal Trade Commission's rules on written warranties: what they must "
     "say, making them available before you buy, and informal dispute settlement.", [(16, 1, 701), (16, 1, 702),
                                                                                      (16, 1, 703)]),
    ("cfr_16_423_care_labeling", "Care labeling of textile wearing apparel (16 CFR part 423)", "Consumer rights", 16,
     1, 423, "The Federal Trade Commission's Care Labeling Rule: the washing, drying, ironing and dry-cleaning "
             "instructions sewn into clothes, and the care symbols."),
    ("cfr_16_429_cooling_off", "The Cooling-Off Rule for door-to-door sales (16 CFR part 429)", "Consumer rights", 16,
     1, 429, "The Federal Trade Commission's rule giving three days to cancel sales made at your home and other "
             "places away from the seller's store."),
    ("cfr_16_310_telemarketing", "The Telemarketing Sales Rule (16 CFR part 310)", "Consumer rights", 16, 1, 310,
     "The Federal Trade Commission's Telemarketing Sales Rule, including the National Do Not Call Registry and "
     "rules against abusive and deceptive calls."),
]
CFR_LAWS_MORE = [
    ("cfr_21_201_drug_labeling", "Drug labeling (21 CFR part 201)", "Medicines", 21, 4, 201,
     "The Food and Drug Administration's labeling rules for prescription and over-the-counter medicines: the "
     "Drug Facts label, warnings, directions and the prescribing information."),
    ("cfr_42_410_medicare_part_b", "Medicare Part B benefits (42 CFR part 410)", "Health insurance", 42, 2, 410,
     "Medicare's Supplementary Medical Insurance benefits: what Part B covers, conditions and limits, including "
     "preventive services and durable medical equipment."),
    ("cfr_42_423_medicare_part_d", "Medicare Part D prescription drug benefit (42 CFR part 423)", "Health insurance",
     42, 3, 423, "Medicare's voluntary prescription drug benefit: eligibility and enrolment, plan rules, formularies, "
                 "low-income subsidy, grievances and appeals."),
    ("cfr_49_390_fmcsa_drivers", "Federal Motor Carrier Safety Regulations for drivers (49 CFR parts 390, 391, 392, "
     "395 and 396)", "Trucking and commercial driving", 49, 5, 390,
     "The FMCSA's rules for commercial truck and bus drivers: general rules, driver qualifications and medical "
     "standards, driving rules, hours of service, and inspection and maintenance.",
     [(49, 5, 391), (49, 5, 392), (49, 5, 395), (49, 5, 396)]),
]

# ---------------------------------------------------------------------- UK National Archives teaching resources (19)
# Re-checked on 2026-11-21. www.nationalarchives.gov.uk/robots.txt now says "Content-Signal: ai-train=no,
# search=yes, ai-input=yes" and "Crawl-delay: 10 seconds". Reasoning (written down for the owner): the
# Content-Signal names three uses. "ai-train" is training or fine-tuning a model's weights; "ai-input" is putting
# content into a model to answer a question (retrieval, grounding). This book is read offline by the person and
# searched by the toolkit's Assistant to answer that person's questions, which is ai-input (allowed); it is never
# used to train or fine-tune a model (the toolkit's models are fixed downloads, and nothing is sent anywhere), so
# ai-train=no is obeyed. The pages are under the Open Government Licence v3.0 (every page's footer). The old
# education pages (/education/resources/...) are gone (410, or moved), so only the current teaching resources
# (/education/teaching-resources/) are read, at most one page every 10 seconds (build_textbooks.allowed_by_robots
# reads "Crawl-delay: 10 seconds" since 2026-11-21; Python's own parser took only a bare number).
TNA = "https://www.nationalarchives.gov.uk"
GOV_GUIDES = [
    dict(name="uk_national_archives_teaching_resources", title="The National Archives (UK): teaching resources",
         subject="History", group="history", publisher="The National Archives (UK)", country="United Kingdom",
         licence="OGL-UK-3.0", licence_url=OGL_UK_URL, source=TNA + "/education/teaching-resources/",
         description="The UK National Archives' history lessons built on original documents, for ages 5 to 18: "
                     "each resource's background, tasks and the transcripts and descriptions of its sources, from "
                     "the Middle Ages to the 20th century (pictures of the documents are left out; their "
                     "descriptions and transcripts kept).",
         licence_page=TNA + "/education/teaching-resources/", licence_text=r"Open Government Licence",
         page_mark=r"Open Government Licence", sitemap="", unit_rules=[], units="",
         start=[TNA + "/education/teaching-resources/"] +
               [f"{TNA}/education/teaching-resources/?page={n}" for n in range(2, 7)],
         pages=r"^https://www\.nationalarchives\.gov\.uk/education/teaching-resources/[a-z0-9-]+/$",
         content=(r"<main\b[^>]*>", r"</main>"),
         drop=[r"<nav\b.*?</nav>", r'<div class="tna-(?:cookie|notification|phase)[^"]*".*?</div>'], limit=300),
]

# ---------------------------------------------------------------------- licence lines checked by hand
LICENCE_LINES = {
    "faa_handbooks": "faa.gov/regulations_policies/handbooks_manuals/aviation (robots.txt allows the handbooks): FAA "
                     "handbooks are works of the US government (17 U.S.C. 105); faa.gov states no copyright policy "
                     "of its own, so govinfo.gov's quotation of 17 U.S.C. 105 is the line checked, as for the IRS "
                     "and Medicare books.",
    "navy_rate_manuals": "Internet Archive copies (ERIC and Digital Library of India scans with OCR text) of Navy rate "
                         "training manuals; US government works; each judged by the builder with the release rule "
                         "for military publications (military_release.py): built with or without Distribution "
                         "Statement A, the notice saying truthfully which.",
    "nist_handbooks": "nvlpubs.nist.gov: NIST Handbooks 44, 130 and 133 (2025 editions), works of the US government "
                      "(17 U.S.C. 105).",
    "tna_teaching_resources": "www.nationalarchives.gov.uk footer: \"All content is available under the Open "
                              "Government Licence v3.0, except where otherwise stated\"; robots.txt: "
                              "\"Content-Signal: ai-train=no, search=yes, ai-input=yes\", \"Crawl-delay: 10 seconds\".",
}

# ---------------------------------------------------------------------- where a non-US book's practice differs
# More specific notices for the new non-US books (Canada's publications, GOV.UK's guides, the UK safety alerts);
# sources.py puts them before its own subjects (the first match wins).
PRACTICE_SUBJECTS = [
    (r"pension|benefit|carer|caring|social security|welfare|veteran", "benefits and pensions, who qualifies, the "
     "ages and amounts, and the agencies, forms and phone numbers to use"),
    (r"housing|tenan|landlord|renting|council tax", "tenancy and housing law, deposits, evictions, local taxes and "
     "council services"),
    (r"debt|bankrupt|insolven|court claim", "tax and debt rules, bankruptcy and insolvency, and court procedures"),
    (r"recall|product safety", "which products are sold there, the recall and reporting systems, and the agencies "
     "to contact"),
    (r"transport|boating|aviation|aircraft|marine", "transport rules and licences, the side of the road, boating "
     "and aviation rules, emergency numbers and metric units"),
]

# ---------------------------------------------------------------------- looked at and not built (2026-11-21)
NOT_INCLUDED = [
    ("FAA Seaplane, Skiplane, and Float/Ski Equipped Helicopter Operations Handbook and the Balloon Flying Handbook",
     "Published only as separate chapter files on faa.gov (no single PDF); not built yet."),
    ("FAA Aeronautical Information Manual (AIM)", "Changed twice a year under a dated file name; not built yet (the "
     "14 CFR rules it explains are on govinfo.gov)."),
    ("Navy rate training manuals for Seaman, Damage Controlman and Basic Military Requirements",
     "No Internet Archive copy with a text layer was found (netc.navy.mil refuses programs)."),
    ("Navy Gunner's Mate and Seabee Combat Handbook copies on the Internet Archive", "Weapons and combat: never "
     "chosen."),
    ("Navy rate training manuals of the 1970s on the Internet Archive (ERIC copies): Builder 3 & 2, Construction "
     "Electrician 3 & 2, Utilitiesman 3 and 2, Engineman 3 & 2, Electrician's Mate 3 & 2, Fireman", "Their front "
     "matter does not print Distribution Statement A (checked 2026-11-21), which the owner's rule requires for "
     "military manuals."),
    ("Army FM 3-05.70 Survival (2002) and FM 21-11 First Aid for Soldiers (1989) copies", "Their front matter says "
     "\"Distribution authorized to ...\" (restricted); FM 4-25.10 (2004) prints no distribution statement. Not "
     "built."),
    ("Old UK National Archives education pages (/education/resources/...)", "Gone from the site (410, or moved to "
     "the new teaching resources, which are built); the UK Government Web Archive keeps them, and its own terms were "
     "not checked."),
]
