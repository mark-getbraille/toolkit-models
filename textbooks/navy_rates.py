"""US Navy rate training manuals (the "NRTC" and "TRAMAN" handbooks of each enlisted rating, NAVEDTRA and the older
NAVPERS and NAVTRA numbers), for the reference library, in their own group "Reference, Navy rate training manuals"
(the owner's request of 2026-11-23: every Navy rating's handbook, so the library teaches practical trade skills).
Keys: rate:<name>; rate:index is the guide. Request words: navy-rates (every book) and one word per trade group
(navy-rates-deck, navy-rates-engineering, navy-rates-seabees, navy-rates-medical, navy-rates-supply,
navy-rates-aviation, navy-rates-electronics, navy-rates-general and navy-rates-ordnance), each with the index.

What this module builds, in plain words:
  - rate:index, a guide to every Navy rating: what each one does in plain words, the books here for it, and the
    Navy books already elsewhere in the library (the NEETS electronics modules, Basic Machines, Hospital Corpsman,
    Culinary Specialist, Builder, Construction Mechanic, the Seabee Combat Handbook, Basic Military Requirements,
    Machinery Repairman, the photography courses and the others), linked by their own keys, never built twice;
  - the rate training manuals themselves (TRADES below: deck and seamanship, engineering, Seabees, medical and
    dental, supply, administration, food and media, aviation, electronics and data processing, general skills
    courses, and ordnance as history), each read WHOLE from its Internet Archive copy: the ERIC collection's copies
    (the US Department of Education's ERIC kept hundreds of Navy manuals of the 1960s to 1980s), DTIC's copies, the
    Internet Archive's NAVPERS collection of 1940s to 1970s training courses, the National Library of Medicine's and
    the Navy Bureau of Medicine and Surgery history office's scans, and the Digital Library of India and Million Book
    Project scans of 1980s and 1990s editions. Every copy was checked on 2026-11-23: a downloadable PDF with a text
    layer (not a lending-library scan), its year known, and not used by any other module.

The release rule for US military publications (military_release.py) judges every book at every build: the builder
reads its front pages and says truthfully in the notice whether Distribution Statement A is printed (most manuals
of the 1950s to 1980s print no statement: they come in as works of the US Navy published openly by the Internet
Archive). A restricted marking (the 1974 Electronics Installation and Maintenance Book on radar prints "For Official
Use Only") is never built: the builder puts it in left_out, personal use, for the owner to fetch himself. Each entry
has distribution_a, so the builder cuts every part whose title names explosives, demolition, mines, grenades, booby
traps, improvised explosives or sabotage (build_textbooks.NOT_FIELD_SAFE); everything else is kept whole, gunnery and
small arms as history. The ordnance books (Gunner's Mate) lose their chapter "Explosives and Pyrotechnics" this way.

Every notice names the Navy, the manual's number, its edition year, that it is a work of the US government (public
domain under 17 U.S.C. 105) and where the copy comes from, and carries the trade's safety note (electricity, rigging,
machinery, chemicals and fuels, aviation, food, and for the medical books "follow current medical guidance").

Not built (NOT_INCLUDED, with the reason and an address): lending-library scans (Seaman 1981, Quartermaster and
Signalman of the 1950s, Storekeeper 1951 and others), manualzilla copies (a manual-copying site), the Data Systems
Technician copies (CONFIDENTIAL printed in their front pages), the Mineman and Torpedoman's Mate copies, and the
ratings for which no open copy was found (Operations Specialist, Personnelman, Disbursing Clerk, Information Systems
Technician, Hull Maintenance Technician of the 14000 series and others); the Navy's own course site refuses programs.

Run from the repository's folder:
  python3 textbooks/navy_rates.py rate:navy_damage_controlman_3_2_1986 --out build/textbooks --limit 3
  python3 textbooks/navy_rates.py --list navy-rates-seabees
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker

GROUP = "navyrates"
GROUPS = {GROUP: "Reference, Navy rate training manuals"}
WORD = "navy-rates"

# The trade groups, in the order of the index: (id, title, plain words for the index, request word).
TRADES = [
    ("deck", "Deck, seamanship, navigation and security",
     "Sailors who handle the ship, steer and navigate it, signal other ships, fight fires and floods, and keep order "
     "on board: Boatswain's Mate, Quartermaster, Signalman, Damage Controlman, Master-at-Arms and Legalman."),
    ("engineering", "Engineering: engines, electricity and repair",
     "The engine-room and repair ratings: steam turbines, boilers, diesels and gas turbines, ship's electricity and "
     "interior communications, machine shops, optical, instrument and pattern shops."),
    ("seabees", "Seabees: construction",
     "The Navy's construction ratings (the Seabees): carpentry and concrete, steel and welding, plumbing and "
     "heating, electrical work, heavy equipment, surveying and drafting, and vehicle repair."),
    ("medical", "Medical and dental",
     "Hospital corpsmen and dental technicians, and the first aid course every sailor takes."),
    ("supply", "Supply, administration, food and media",
     "Cooking and running a galley, laundry, barbering and the ship's stores, storekeeping, office work, the post "
     "office, journalism, printing and illustration."),
    ("aviation", "Aviation",
     "The ratings that keep naval aircraft flying: engines, airframes and hydraulics, aircraft electricity, "
     "parachutes and survival gear, flight-deck handling and aircraft fuel, ground support equipment, weather "
     "forecasting and air traffic control."),
    ("electronics", "Electronics, communications and data processing",
     "Electronics technicians, radiomen, fire controlmen, sonar and data processing: radio, radar, navigation "
     "systems, computers and how to troubleshoot them."),
    ("general", "General skills courses",
     "The basic courses every rating used: tools and their uses, basic machines, blueprint reading, mathematics, "
     "electricity, electronics, hydraulics and leadership."),
    ("ordnance", "Ordnance, as history",
     "Gunner's Mate: guns, missile launchers, small arms and their maintenance, as history. Their chapters on "
     "explosives are left out by the library's rule."),
]
TRADE_IDS = [t[0] for t in TRADES]
TRADE_WORDS = {t[0]: f"{WORD}-{t[0]}" for t in TRADES}

# ====================================================================== notices and safety notes

# The first words of every notice; the builder puts the truthful release line in front of it (what the front pages
# print about distribution, and whose work it is: build_textbooks.military_notice).
NOTICE_START = ("The release line before this says what its own front pages print about distribution. A US Navy rate "
                "training manual, read whole as the Navy printed it: its equipment, rules and procedures are the "
                "Navy's of its year and may be out of date. Parts about explosives, demolition, mines, grenades and "
                "booby traps are left out. ")
SCAN_NOTE = "The machine-read text of this scan has some mistakes, and its drawings are described only by captions."

SAFETY = {
    "electric": ("Safety: electricity kills. Switch off and lock out the supply and prove it dead with a tester "
                 "before touching a circuit; capacitors and old equipment can hold a charge; follow the National "
                 "Electrical Code and local rules, and leave mains wiring to a licensed electrician where the law "
                 "says so."),
    "rigging": ("Safety: never stand under a load or in the bight of a line; inspect line, wire rope and fittings "
                "before use and never load them beyond their safe working load; wear a life jacket on deck near the "
                "water."),
    "machinery": ("Safety: lock out machinery before working on it; wear eye and hearing protection; keep guards in "
                  "place and loose clothing, hair and jewellery away from moving parts; steam, hot surfaces and "
                  "pressurised lines burn and cut."),
    "chemical": ("Safety: fuels, solvents, paints, welding fumes and refrigerants are dangerous: work with good "
                 "ventilation, wear gloves and eye protection, read each product's safety data sheet, and keep fire "
                 "away; in a poisoning call Poison Control at 1-800-222-1222, or 911."),
    "welding": ("Safety: welding and cutting need a proper helmet and filter lens, gloves, fire-resistant clothing, "
                "ventilation and a fire watch; never weld on a container that held fuel; compressed gas cylinders "
                "must be secured upright."),
    "fire": ("Safety: firefighting and damage control take training and the right equipment; at home, get out, stay "
             "out and call 911; never use water on a grease or electrical fire."),
    "aviation": ("Safety: aircraft maintenance is licensed work: in the US, follow FAA rules and the aircraft maker's "
                 "current manuals; propellers, rotors, jet intakes and exhausts kill; never work on an aircraft "
                 "without the right training and sign-off."),
    "medical": ("Medicine changes: these manuals are out of date (drugs, doses and treatments have changed). Follow "
                "current medical guidance and your own doctor; in an emergency call 911 (or 112). Read them as "
                "history and for the general ideas only, never for doses or diagnosis."),
    "food": ("Food safety: follow today's FDA Food Code and local health rules: keep cold food at 40 F (4 C) or "
             "below, cook to safe temperatures, cool leftovers quickly, and wash hands; old recipes and storage "
             "times may not meet current rules."),
    "radio": ("Safety: radio transmitters and radar can burn with radio-frequency energy: never stand in front of an "
              "operating antenna; transmitting needs the right licence (in the US, from the FCC)."),
    "ordnance": ("Weapons and ammunition: kept as history only. Never try to make, take apart or repair ammunition, "
                 "explosives or fuzes; old ordnance found anywhere can still explode: leave it alone and call 911."),
    "general": ("Safety: wear eye protection with tools, keep tools sharp and in good repair, and follow the maker's "
                "instructions for any power tool."),
}

# Where a copy comes from, by the start of its Internet Archive item name (the notice says it).
COPY_SOURCES = [
    ("ERIC_", "the Internet Archive's copy of ERIC document {doc} (from the US Department of Education's ERIC "
              "collection; Internet Archive item {item})"),
    ("micro_IA", "the Internet Archive's scan of the ERIC or Government Printing Office microfiche (item {item})"),
    ("DTIC_", "the Internet Archive's copy of Defense Technical Information Center (DTIC) document {doc} (Internet Archive item {item})"),
    ("dli.", "the Internet Archive's copy of the Digital Library of India scan (item {item})"),
]


def copy_source(archive, via=""):
    """The words for where a copy comes from (the notice says it): via when given, else by the item's name."""
    if via:
        return f"{via} (Internet Archive item {archive})"
    for start, words in COPY_SOURCES:
        if archive.startswith(start):
            return words.format(doc=archive.split("_", 1)[-1], item=archive)
    if archive.endswith("mbp"):
        return f"the Internet Archive's Million Book Project scan (item {archive})"
    return f"the Internet Archive (item {archive})"


BOOKS = []          # (trade, entry), in the order of the index


def rate(trade, name, title, archive, year, number, subject, description, safety, via="", scan=True, **more):
    """One rate training manual of the Internet Archive as a PDF entry, read whole: distribution_a makes the builder
    judge its front pages by the release rule and cut only the parts about explosives (NOT_FIELD_SAFE). number: the
    manual's own number ("NAVEDTRA 10572"); via: where the copy comes from, when the item's name does not say it."""
    notes = " ".join(SAFETY[s] for s in ((safety,) if isinstance(safety, str) else safety))
    facts = (f"US Navy, {number}, {year} edition: a work of the US government, public domain (17 U.S.C. 105). "
             f"Copy: {copy_source(archive, via)}. ")
    entry = K.us_pdf(GROUP, name=name, title=title, subject=subject,
                     publisher=more.pop("publisher", "US Navy (Naval Education and Training Command and the "
                                                     "Bureau of Naval Personnel before it)"),
                     archive=archive, published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                     description=description + (" " + SCAN_NOTE if scan else ""),
                     notice=NOTICE_START + facts + notes, distribution_a=True, work="a work of the US Navy",
                     number=number, **more)
    BOOKS.append((trade, entry))
    return entry


ERIC = "the Internet Archive's copy of ERIC document"
NAVPERS_COLL = "the Internet Archive's NAVPERS collection of Navy training courses"
NLM = "the National Library of Medicine's scan on the Internet Archive"
BUMED = "the Internet Archive collection of the Navy Bureau of Medicine and Surgery's history office"
UPLOAD = "a person's upload of the Navy's own PDF to the Internet Archive"

# ====================================================================== deck, seamanship, navigation and security

rate("deck", "navy_quartermaster_3_2_1976", "Quartermaster 3 & 2 (US Navy, NAVEDTRA 10149-F, 1976)", "ERIC_ED132263",
     1976, "NAVEDTRA 10149-F", "Navigation and ship's bridge duties",
     "The Navy's course for quartermasters, the ratings who steer and navigate: quartermaster watches, honors and "
     "ceremonies, magnetic compass and gyrocompass, aids to navigation, rules of the road, charts and publications, "
     "time and timepieces, dead reckoning and piloting, electronic and celestial navigation, tides and currents, "
     "weather, the maneuvering board and communications.", "rigging")
rate("deck", "navy_quartermaster_1_c_1972", "Quartermaster 1 & C (US Navy, NAVTRA 10151-D, 1972)", "ERIC_ED088693",
     1972, "NAVTRA 10151-D", "Navigation and ship's bridge duties",
     "The senior quartermaster's course of 1972 (the 1991 edition is pdf:navy_quartermaster_1_c): compasses and "
     "their errors and adjustment, piloting, dead reckoning, celestial and electronic navigation, the navigator's and "
     "officer of the deck's assistant, ship handling, rules of the road, navigation publications and records.",
     "rigging")
rate("deck", "navy_signalman_1_c_1974", "Signalman 1 & C (US Navy, 1974)", "ERIC_ED106512", 1974,
     "NAVEDTRA rate training manual (Signalman 1 & C, revised 1974)", "Visual signalling",
     "The senior signalman's course: advancement, administrative and training duties, naval communications, convoy "
     "communications, security, equipage and material management, assisting the officer of the deck, piloting and "
     "electronic navigation, special signals, the operations and communications department and assisting the signal "
     "officer.", "rigging")
rate("deck", "navy_signalman_1_c_1984", "Signalman 1 & C (US Navy, NAVEDTRA 10136-D, 1984)", "dli.ernet.163162", 1984,
     "NAVEDTRA 10136-D", "Visual signalling",
     "The 1984 edition: administration, training, ship's organization, naval and convoy communications, equipage and "
     "material management, piloting and assisting the officer of the deck, special signals and assisting the signal "
     "officer.", "rigging")
rate("deck", "navy_damage_controlman_3_2_1986", "Damage Controlman 3 & 2 (US Navy, NAVEDTRA 10572, 1986)",
     "micro_IA41152823_0976", 1986, "NAVEDTRA 10572", "Damage control and shipboard firefighting",
     "The damage controlman's course: the rating, damage control organization and information, ship compartmentation "
     "and watertight integrity, fundamentals of firefighting, firefighting equipment and systems, emergency repairs, "
     "radiological effects and countermeasures, and biological and chemical agents. Prints Distribution Statement "
     "A.", ("fire", "chemical"), via="the Internet Archive's scan of the Government Printing Office microfiche")
rate("deck", "navy_master_at_arms_1974", "Master-at-Arms (US Navy rate training manual, 1974)", "ERIC_ED109440", 1974,
     "NAVEDTRA rate training manual (Master-at-Arms)", "Shipboard security and law enforcement",
     "The course for the Navy's police rating, then new: career development, legal procedures, small arms, patrols "
     "and traffic control, investigations, prisoner restraint and searches, physical security, civil disturbances "
     "and natural disasters, places of confinement, administration and first aid.", "general")
rate("deck", "navy_legalman_2_1_c_1975", "Legalman 2, 1 & C (US Navy, NAVEDTRA 10455, 1975)", "micro_IA41153134_0766",
     1975, "NAVEDTRA 10455", "Military law office work",
     "The Navy legalman's course: office procedures and security, the law library, legal reporting, constitutional "
     "considerations, nonjudicial punishment, pretrial, trial and posttrial procedures, administrative discharges, "
     "fact-finding bodies, claims and legal assistance, with sample records of trial and a glossary of military law. "
     "Military law has changed since; it is not legal advice.", "general")

# ====================================================================== engineering

rate("engineering", "navy_machinists_mate_3_2_1972", "Machinist's Mate 3 & 2 (US Navy, NAVTRA 10524-D, 1972)",
     "MachinistsMate3and210524D", 1972, "NAVTRA 10524-D", "Shipboard steam machinery",
     "The engine-room course of 1972: general engineering safety, steam turbines, reduction gears, pumps, piping, "
     "valves, gaskets and packing, heat exchangers and air ejectors, lubrication, engine-room operating procedures, "
     "refrigeration and air conditioning, distilling plants, compressed air plants, other auxiliary equipment, "
     "engineering casualty control, and lathes.", "machinery", via=NAVPERS_COLL)
rate("engineering", "navy_machinists_mate_1_c_1974", "Machinist's Mate 1 & C (US Navy, NAVEDTRA 10525-D, 1974)",
     "ERIC_ED106658", 1974, "NAVEDTRA 10525-D", "Shipboard steam machinery",
     "The senior machinist's mate's course: turbines, reduction gears, steam-driven generators, heat exchangers and "
     "air ejectors, pumps, piping and valves, distilling plants, refrigeration and air conditioning, auxiliary "
     "equipment, supervision and training, propulsion plant efficiency, casualty control, inspections and trials, "
     "ship repair, and records.", "machinery")
rate("engineering", "navy_machinists_mate_3_1958", "Machinist's Mate 3 (US Navy, NAVPERS 10522, 1958)",
     "MachinistsMate310522", 1958, "NAVPERS 10522", "Shipboard steam machinery",
     "The 1958 course: engineering piping systems, main and auxiliary turbines, reduction gears, bearings, shafting "
     "and propellers, lubrication, condensers, pumps, valves and packing, distilling plants, refrigeration, air "
     "compressors, steering engines and deck machinery, industrial gases, and watches and casualty control.",
     "machinery", via=NAVPERS_COLL)
rate("engineering", "navy_machinists_mate_2_1958", "Machinist's Mate 2 (US Navy, NAVPERS 10523, 1958)",
     "MachinistsMate210523", 1958, "NAVPERS 10523", "Shipboard steam machinery",
     "The 1958 course for the second class machinist's mate: the duties of the rate and the main and auxiliary "
     "machinery of the engine room.", "machinery", via=NAVPERS_COLL)
rate("engineering", "navy_machinists_mate_1_c_1955", "Machinist's Mate 1 & C (US Navy, NAVPERS 10525, 1955)",
     "MachinistsMate1andC105251955", 1955, "NAVPERS 10525", "Shipboard steam machinery",
     "The 1955 senior course: leadership, propulsion turbines, reduction gears, condensers, turbogenerators, pumps, "
     "plant operation, casualty and damage control, distilling plants, refrigeration and air conditioning, piping "
     "repair, lathe work, auxiliary equipment, Navy repair procedures, materials, records and inspections.",
     "machinery", via=NAVPERS_COLL)
rate("engineering", "navy_engineman_3_1957", "Engineman 3 (US Navy, NAVPERS 10539, 1957)", "Engineman310539", 1957,
     "NAVPERS 10539", "Diesel and gasoline engines",
     "The 1957 course for enginemen, who run and repair the internal-combustion engines of ships and boats: the "
     "rating and the engines and auxiliary equipment in their care. (Engineman 3 & 2 of 1979 is "
     "pdf:navy_engineman_3_2_1979.)", ("machinery", "chemical"), via=NAVPERS_COLL)
rate("engineering", "navy_engineman_2_1957", "Engineman 2 (US Navy, NAVPERS 10540, 1957)", "Engineman210540", 1957,
     "NAVPERS 10540", "Diesel and gasoline engines",
     "The 1957 course for the second class engineman: the duties of the rate and the operation, maintenance and "
     "repair of diesel and gasoline engines and their systems.", ("machinery", "chemical"), via=NAVPERS_COLL)
rate("engineering", "navy_fundamentals_of_diesel_engines_1945", "Fundamentals of Diesel Engines (US Navy, NAVPERS "
     "16178, 1945)", "NAVPERS16178", 1945, "NAVPERS 16178", "Diesel engines",
     "The Navy's 1945 textbook of diesel engines: basic principles, petroleum products and diesel fuel, engine "
     "construction, the four-stroke and two-stroke cycles, scavenging, fuel injection, governors, starting, "
     "lubrication and cooling, with problems and questions.", ("machinery", "chemical"),
     via="a person's upload of the Navy's own book to the Internet Archive")
rate("engineering", "navy_electricians_mate_3_2_1974", "Electrician's Mate 3 & 2 (US Navy rate training manual, 1974)",
     "ERIC_ED110703", 1974, "NAVEDTRA rate training manual (Electrician's Mate 3 & 2)", "Ship's electrical systems",
     "The 1974 course (the 1981 edition is pdf:navy_electricians_mate_3_2_1981): safety precautions, test equipment, "
     "electrical installations, AC and DC power distribution, motor controllers, motors and generators, shipboard "
     "lighting, degaussing, electrical propulsion, basic electronic components and logic, electrical auxiliaries and "
     "sound motion picture systems.", "electric")
rate("engineering", "navy_electricians_mate_1_c_1976", "Electrician's Mate 1 & C (US Navy rate training manual, 1976)",
     "ERIC_ED132256", 1976, "NAVEDTRA rate training manual (Electrician's Mate 1 & C)", "Ship's electrical systems",
     "The senior electrician's course: career program, safety, voltage and frequency regulation, transistorized "
     "control devices, automatic degaussing, gyrocompasses, no-break power supplies, electrohydraulic speed "
     "governors, engineering casualty control, maintenance administration and visual landing aids.", "electric")
rate("engineering", "navy_electricians_mate_3_2_1959", "Electrician's Mate 3 & 2 (US Navy, NAVPERS 10546, 1959)",
     "ElectriciansMate3and210546", 1959, "NAVPERS 10546", "Ship's electrical systems",
     "The 1959 course: organization, electrical cable and accessories, electric lighting, searchlights, maintenance "
     "of motors and generators, and the ship's other electrical equipment.", "electric", via=NAVPERS_COLL)
rate("engineering", "navy_electricians_mate_1_c_1965", "Electrician's Mate 1 & C (US Navy, NAVPERS 10547-A, 1965)",
     "ElectriciansMate1andC10547A", 1965, "NAVPERS 10547-A", "Ship's electrical systems",
     "The 1965 senior course: DC and AC windings (rewinding motors and generators), voltage and frequency "
     "regulation, automatic degaussing, engineering casualty control, maintenance and repair, inspections and trials "
     "and safety precautions.", "electric", via=NAVPERS_COLL)
rate("engineering", "navy_electricians_mate_3_1950", "Electrician's Mate 3 (US Navy, NAVPERS 10548, 1950)",
     "ElectriciansMate310548", 1950, "NAVPERS 10548", "Electricity and ship's electrical systems",
     "The 1950 course, a good plain introduction to electricity: currents and circuits and Ohm's law, magnetism and "
     "induction, AC and DC generators and motors and their care, controllers, cables, batteries, electrical systems "
     "in small craft, searchlights, blueprint reading and safety precautions.", "electric", via=NAVPERS_COLL)
rate("engineering", "navy_electricians_mate_2c_1947", "Electrician's Mate 2c (US Navy, 1947)", "ElectriciansMate2C1947",
     1947, "NAVPERS training course (Electrician's Mate 2c)", "Electricity and ship's electrical systems",
     "The 1947 course: a quick review, Kirchhoff's laws, measuring instruments, armature winding and commutation, DC "
     "generators and motors and their starters, contactors, overload protection and circuit breakers, alternating "
     "current, reactance, impedance and power, alternators in parallel, transformers, AC motors and controllers.",
     "electric", via=NAVPERS_COLL)
rate("engineering", "navy_ic_electrician_3_2_1973", "IC Electrician 3 & 2 (US Navy rate training manual, 1973)",
     "ERIC_ED106514", 1973, "NAVEDTRA rate training manual (IC Electrician 3 & 2)", "Interior communications",
     "The course for interior communications electricians: safety, switches, protective devices and cables, power "
     "distribution, test equipment, sound-powered telephones, alarm and warning systems, announcing and intercom "
     "systems, dial telephones, sound recording, gyrocompasses, ship's control order and indicating systems, "
     "metering, plotting systems, maintenance and regulated power supplies.", "electric")
rate("engineering", "navy_ic_electrician_1_c_1958", "IC Electrician 1 & Chief (US Navy, NAVPERS 10557, 1958)",
     "ICElectrician1andChief10557", 1958, "NAVPERS 10557", "Interior communications",
     "The 1958 senior course: organization and administration, gas-filled electron tubes, basic mechanisms (gears, "
     "differentials, servomotors, cams), ship's metering and indicating systems (revolution, wind, salinity, "
     "underwater log), magnetic amplifiers and their uses, and gyrocompass equipment.", "electric",
     via="a person's upload of the Navy's own book to the Internet Archive")
rate("engineering", "navy_boilerman_3_2_1955", "Boilerman 3 & 2 (US Navy, NAVPERS 10535-C, 1955)",
     "Boilerman3and210535C", 1955, "NAVPERS 10535-C", "Steam boilers",
     "The fireroom course: boilers and boiler fittings, control instruments, auxiliary turbines, pumps, forced draft "
     "blowers, boiler water treatment, feed water and fuel oil systems, fireroom operations and casualty control, "
     "boiler maintenance, valves and piping, and the oil and water king.", ("machinery", "chemical"),
     via=NAVPERS_COLL)
rate("engineering", "navy_boilerman_1_c_1956", "Boilerman 1 & C (US Navy, NAVPERS 10536-B, 1956)",
     "Boilerman1andC10536B", 1956, "NAVPERS 10536-B", "Steam boilers",
     "The senior fireroom course: pumps and blowers, auxiliary turbines, fuel oil equipment, boiler fittings, water "
     "treatment, boiler operation and efficiency, retubing, refractories, cleaning, Navy repair procedures, the oil "
     "king, automatic combustion control, propulsion turbines, casualty control, records and inspections.",
     ("machinery", "chemical"), via=NAVPERS_COLL)
rate("engineering", "navy_boilermaker_1_c_1969", "Boilermaker 1 & C (US Navy, NAVPERS 10537-B, 1969)",
     "Boilermaker1andC10537B", 1969, "NAVPERS 10537-B", "Boiler repair and welding",
     "The boilermaker's course: maintenance management, boiler refractories, metals and alloys, boiler tube work, "
     "heat exchangers, an introduction to welding, metal arc and oxyacetylene welding, welded joint design, testing "
     "welds, cutting, fireroom maintenance, boiler fittings, tests and inspections, water treatment and automatic "
     "boiler controls.", ("machinery", "welding"), via=NAVPERS_COLL)
rate("engineering", "navy_gas_turbine_electrical_3_2_1988", "Gas Turbine System Technician (Electrical) 3 & 2 (US "
     "Navy, NAVEDTRA 10550, 1988)", "dli.ernet.163071", 1988, "NAVEDTRA 10550", "Marine gas turbines",
     "The course for the electrical gas turbine technician: tools and test equipment, indicating instruments, "
     "fundamentals of gas turbine engines, the LM2500 gas turbine and its operation, the Allison 501-K17, the "
     "engineering control consoles of the Spruance and Oliver Hazard Perry classes, uninterruptible power supplies, "
     "and motors, generators and switchboards. Prints Distribution Statement A.", ("electric", "machinery"))
rate("engineering", "navy_machinery_repairman_3_2_1981", "Machinery Repairman 3 & 2 (US Navy, NAVEDTRA 10530-E, 1981)",
     "ERIC_ED203130", 1981, "NAVEDTRA 10530-E", "Machine shop work",
     "The machinist's course (the 1993 Machinery Repairman is make:navy_machinery_repairman_1993): toolrooms and "
     "tools, layout and benchwork, metals and plastics, power saws and drills, grinding tools, engine and turret "
     "lathes, milling machines, shapers, planers and engravers, precision grinding, metal buildup and the repair "
     "department, with tables and gearing formulas.", "machinery")
rate("engineering", "navy_machinery_repairman_3_2_1990", "Machinery Repairman 3 & 2 (US Navy, NAVEDTRA 12204, 1990)",
     "machineryrepairm003995mbp", 1990, "NAVEDTRA 12204", "Machine shop work",
     "The 1990 edition of the machinist's course, with the same chapters as 1981 brought up to date: toolrooms, "
     "layout, metals, saws and drills, grinding, lathes, milling, shapers and planers, precision grinding, metal "
     "buildup and repair work. Prints Distribution Statement A.", "machinery")
rate("engineering", "navy_opticalman_3_2_1970", "Opticalman 3 & 2 (US Navy, NAVPERS 10205-A, 1970)", "ERIC_ED070575",
     1970, "NAVPERS 10205-A", "Optical instrument repair",
     "The optical shop course of 1970: light, mirrors, prisms, lenses and optical systems, mechanical design, "
     "maintenance and repair of spyglasses, telescopes, compasses, azimuth circles, sextants, stadimeters, "
     "alidades, binoculars, periscopes and night vision sights, and the lathes and other machines of the shop. "
     "(Opticalman 3 & 2 of 1989 is pdf:navy_opticalman_3_2.)", "machinery")
rate("engineering", "navy_opticalman_3_2_1979", "Opticalman 3 & 2 (US Navy rate training manual, 1979)",
     "ERIC_ED185315", 1979, "NAVEDTRA rate training manual (Opticalman 3 & 2)", "Optical instrument repair",
     "The 1979 edition: advancement, the nature of light, mirrors and prisms, lenses, basic optical systems, design "
     "and construction, maintenance procedures, machine tool operations, optical and navigation equipment, night "
     "vision sights and gunsights, and submarine periscopes.", "machinery")
rate("engineering", "navy_opticalman_1_c_1972", "Opticalman 1 & C (US Navy, NAVTRA 10206-A, 1972)", "ERIC_ED087618",
     1972, "NAVTRA 10206-A", "Optical instrument repair",
     "The senior optical shop course: administration and supervision, the nature of light, optical alignment "
     "instruments, night vision sights, synchros and servos, tilting-prism gunsight telescopes, rangefinders and "
     "submarine periscopes, with step-by-step overhaul procedures.", "machinery")
rate("engineering", "navy_opticalman_1_c_1985", "Opticalman 1 & C (US Navy, NAVEDTRA 10206-B, 1985)",
     "micro_IA41152806_0225", 1985, "NAVEDTRA 10206-B", "Optical instrument repair",
     "The 1985 edition of the senior optical shop course, with its occupational standards.", "machinery",
     via="the Internet Archive's scan of the Government Printing Office microfiche")
rate("engineering", "navy_instrumentman_3_2_1961", "Instrumentman 3 & 2 (US Navy, NAVPERS 10193-A, 1961)",
     "Instrumentman3and210193A", 1961, "NAVPERS 10193-A", "Watch, clock, typewriter and gauge repair",
     "The instrument repair course: timekeepers old and new, watch repair tools, cleaning and oiling watches, "
     "finding faults, making and fitting watch parts, adjusting the escapement, typewriter repair (Underwood, "
     "Remington, Royal, L. C. Smith), pressure and vacuum gauges, thermometers and pyrometers.", "machinery",
     via="a person's upload of the Navy's own book to the Internet Archive")
rate("engineering", "navy_instrumentman_1_c_1973", "Instrumentman 1 & C (US Navy, NAVTRA 10194-C, 1973)",
     "ERIC_ED082050", 1973, "NAVTRA 10194-C", "Watch, clock, office machine and gauge repair",
     "The senior instrument repair course: the repair and calibration shops, safety, watch and clock repair and "
     "adjustment, electric typewriters, calculators and other office machines, manufacturing and administration.",
     "machinery")
rate("engineering", "navy_patternmaker_3_2_1973", "Patternmaker 3 & 2 (US Navy, NAVTRA 10578-C, 1973)", "ERIC_ED098380",
     1973, "NAVTRA 10578-C", "Pattern making and foundry woodwork",
     "The pattern shop course: patternmaking and founding, hand tools, portable power tools, woodworking machines, "
     "materials, construction techniques, shop mathematics, blueprints and layouts, cores and core boxes, parted, "
     "cylindrical, flanged, segmental and staved patterns and patterns for composite castings.",
     ("machinery", "general"))
rate("engineering", "navy_fluid_power_1970", "Fluid Power (US Navy, NAVPERS 16193-B, 1970)", "ERIC_ED070578", 1970,
     "NAVPERS 16193-B", "Hydraulics and pneumatics",
     "The Navy's basic course in hydraulics and pneumatics: physical principles, fluids and contamination control, "
     "lines, connectors and seals, reservoirs, filters, accumulators, pumps and compressors, flow and pressure "
     "measurement and control, valves, actuating cylinders, fluid motors, and complete systems.", "machinery")
rate("engineering", "navy_engineering_administration_1969", "Engineering Administration (US Navy, NAVPERS 10858-D, "
     "1969)", "ERIC_ED070573", 1969, "NAVPERS 10858-D", "Running an engineering department",
     "For engineering officers: shipboard organization and watches, directives and ship's bills, damage control, "
     "training, maintenance, records and reports, supply, readiness, fuel stowage, and shipwork during overhauls.",
     "machinery")

# ====================================================================== Seabees

rate("seabees", "navy_builder_3_2_1954", "Builder 3 & 2 (US Navy, NAVPERS 10648-C, 1954)", "Builder3and210648C", 1954,
     "NAVPERS 10648-C", "Carpentry, concrete and painting",
     "The Seabee builder's course of 1954 (the 1981 edition is build:navy_builder_3_2_1981): lumber, surface "
     "preparation and painting, woodworking tools and hardware, power tools, blueprints and the steel square, "
     "foundations and forms, concrete, scaffolding, woodworking, framing, prefabricated, field and waterfront "
     "structures, and rigging.", ("general", "rigging", "chemical"), via=NAVPERS_COLL)
rate("seabees", "navy_builder_1_c_1969", "Builder 1 & C (US Navy, NAVPERS 10649-E, 1969)", "Builder1andC10649E", 1969,
     "NAVPERS 10649-E", "Construction supervision",
     "The senior builder's course: planning and estimating, scheduling, exterior and interior finish, concrete, "
     "logging and sawmill operations, heavy construction, foremanship, construction and maintenance inspection, "
     "and the company chief.", ("general", "machinery"), via=NAVPERS_COLL)
rate("seabees", "navy_builder_1_c_1973", "Builder 1 & C (US Navy, NAVTRA 10649, revised 1973)", "ERIC_ED102360", 1973,
     "NAVTRA 10649 (revised 1973)", "Construction supervision",
     "The 1973 senior builder's course: supervision, planning, estimating and scheduling, concrete and masonry, "
     "plastering, wall tile and acoustical ceilings, light frame and heavy construction, and construction and "
     "maintenance inspection.", "general")
rate("seabees", "navy_steelworker_vol1_1996", "Steelworker, Volume 1 (US Navy, NAVEDTRA 14250, 1996)", "steelworker1",
     1996, "NAVEDTRA 14250", "Welding and metalwork",
     "The Seabee steelworker's course, volume 1: properties and uses of metals, basic heat treatment, welding, gas "
     "cutting and gas welding, soldering, brazing, braze welding and wearfacing, shielded metal-arc welding and gas "
     "shielded-arc welding. Prints Distribution Statement A.", ("welding", "chemical"), via=UPLOAD, scan=False)
rate("seabees", "navy_steelworker_vol2_1996", "Steelworker, Volume 2 (US Navy, NAVEDTRA 14251, 1996)", "steelworker2",
     1996, "NAVEDTRA 14251", "Steel erection, rigging and sheet metal",
     "Volume 2: technical administration, sheet metal and fibreglass duct, structural steel and pipe, fibre line, "
     "wire rope and rigging, reinforcing steel, pre-engineered buildings, towers, storage tanks and pontoons, and "
     "steelworker tools, with hand signals and tables. Prints Distribution Statement A.", ("rigging", "welding"),
     via=UPLOAD, scan=False)
rate("seabees", "navy_steelworker_1_c_1981", "Steelworker 1 & C (US Navy, NAVEDTRA 10654-E, 1981)", "ERIC_ED211839",
     1981, "NAVEDTRA 10654-E", "Steel construction supervision",
     "The senior steelworker's course: administration, supervision, shop and construction site organization, "
     "construction inspection, and the planning of steel erection, welding and rigging work.", ("rigging", "welding"))
rate("seabees", "navy_steelworker_1_c_1954", "Steelworker 1 & C (US Navy, NAVPERS 10564-A, 1954)",
     "Steelworker1andC10564A", 1954, "NAVPERS 10564-A", "Rigging, steel and welding",
     "The 1954 senior course: rigging heavy equipment, building with wood, steel and steel fabrication, welding "
     "techniques and troubleshooting, supervision and teaching, with wire rope specifications.",
     ("rigging", "welding"), via=NAVPERS_COLL)
rate("seabees", "navy_utilitiesman_3_1990", "Utilitiesman 3 (US Navy, NAVEDTRA 12532, 1990)", "micro_IA41152645_0332",
     1990, "NAVEDTRA 12532", "Plumbing, heating and water supply",
     "The Seabee utilitiesman's course: plans and specifications, rough-in plumbing, plumbing and its repair, prime "
     "movers, pumps and air compressors, field water treatment, advanced base field support facilities, boilers, "
     "hot-water and warm-air heating, refrigeration and air conditioning. Prints Distribution Statement A. (The "
     "1973 Utilitiesman 3 & 2 is pdf:navy_utilitiesman_3_2_1973.)", ("machinery", "chemical"),
     via="the Internet Archive's scan of the Government Printing Office microfiche")
rate("seabees", "navy_utilities_man_3_2_1957", "Utilities Man 3 & 2 (US Navy, NAVPERS 10656-C, 1957)",
     "UtilitiesMan3and210656C", 1957, "NAVPERS 10656-C", "Plumbing, water and sewage",
     "The 1957 course: the utilities man and Seabee history, plumbing and plumbing repairs, sewage disposal at "
     "advanced bases, water supply and treatment, and the utilities of a construction battalion.",
     ("machinery", "chemical"), via=NAVPERS_COLL)
rate("seabees", "navy_utilities_man_1_c_1959", "Utilities Man 1 & C (US Navy, NAVPERS 10657-B, 1959)",
     "UtilitiesMan1andC10657B", 1959, "NAVPERS 10657-B", "Boilers, refrigeration and galley equipment",
     "The 1959 senior course: new duties, boilers and boiler controls, pumps, refrigeration, air conditioning, "
     "installing and servicing galley equipment, and the basic combat organization of a battalion.",
     ("machinery", "chemical"), via=NAVPERS_COLL)
rate("seabees", "navy_equipment_operator_3_2_1973", "Equipment Operator 3 & 2 (US Navy, NAVTRA 10640-G, 1973)",
     "micro_IA41152912_0572", 1973, "NAVTRA 10640-G", "Heavy equipment operation",
     "The heavy equipment course of 1973 (the 1994 Equipment Operator, Basic is pdf:navy_equipment_operator_basic): "
     "engines, fuels and lubricants, pollution control, vehicles, materials-handling equipment, earthmoving "
     "equipment and earthwork, power cranes and their attachments, and ditchers.", ("machinery", "rigging"))
rate("seabees", "navy_equipment_operator_1_c_1979", "Equipment Operator 1 & C (US Navy, NAVEDTRA 10641-G, 1979)",
     "micro_IA41153333_0132", 1979, "NAVEDTRA 10641-G", "Heavy equipment and earthwork supervision",
     "The senior equipment operator's course: administration, supervision, advanced base planning and embarkation, "
     "construction, earthmoving, roadbuilding, quarrying and well drilling, and running equipment pools. Any part on "
     "quarry blasting is left out by the library's rule.", ("machinery", "rigging"))
rate("seabees", "navy_construction_electrician_basic_1998", "Construction Electrician Basic (US Navy, NAVEDTRA 14026, "
     "1998)", "constelect1", 1998, "NAVEDTRA 14026", "Construction electrical work",
     "The Seabee electrician's basic course: construction support, drawings and specifications, power generation "
     "and distribution, interior wiring, communications and lighting, appliances, test equipment, motors and "
     "generators, with formulas and hand signals. Prints Distribution Statement A.", "electric", via=UPLOAD,
     scan=False)
rate("seabees", "navy_construction_electricians_mate_3_2_1951", "Construction Electrician's Mate 3 & 2 (US Navy, "
     "NAVPERS 10636-A, 1951)", "ConstructionElectricianMate3and210636A", 1951, "NAVPERS 10636-A",
     "Power lines, wiring and telephones",
     "The 1951 course: conductors, batteries, DC machines, AC generators and motors, advanced base generating "
     "stations, distributing power, power-line construction and stringing, interior wiring, telephone lines and "
     "installing telephones, and finding grounds, shorts and open circuits.", "electric", via=NAVPERS_COLL)
rate("seabees", "navy_construction_electrician_3_2_1960", "Construction Electrician 3 & 2 (US Navy, NAVPERS 10636-C, "
     "1960)", "ConstructionElectrician3and210636C", 1960, "NAVPERS 10636-C", "Construction electrical work",
     "The 1960 course in the basic knowledge and skills of the construction electrician (the 1976 edition is "
     "pdf:navy_construction_electrician_3_2_1976).", "electric", via=NAVPERS_COLL)
rate("seabees", "navy_construction_electricians_mate_1_c_1955", "Construction Electrician's Mate 1 & C (US Navy, "
     "NAVPERS 10637-A, 1955)", "ConstructionElectriciansMate1andC10637A", 1955, "NAVPERS 10637-A",
     "Power stations, transformers and cable splicing",
     "The 1955 senior course: administrative duties, electrical drawings, electrical repairs, installing "
     "communications equipment, telephone cable splicing, transformer installation and repair, portable and central "
     "power plants, and lead-sheathed power cable.", "electric", via=NAVPERS_COLL)
rate("seabees", "navy_construction_electrician_1_c_1966", "Construction Electrician 1 & C (US Navy, NAVPERS 10637-C, "
     "1966)", "ConstructionElectrician1andC10637C", 1966, "NAVPERS 10637-C", "Construction electrical supervision",
     "The 1966 senior course: defensive tactics, electrical sketching and planning, protective devices and "
     "controllers, testing equipment, power generators and distribution, communication, cold weather operations, "
     "training, foremanship, maintenance and NBC defence equipment.", "electric", via=NAVPERS_COLL)
rate("seabees", "navy_engineering_aid_3_2_vol1_1980", "Engineering Aid 3 & 2, Volume 1 (US Navy, NAVEDTRA 10634-C, "
     "1980)", "ERIC_ED249090", 1980, "NAVEDTRA 10634-C", "Drafting and engineering mathematics",
     "The Seabee engineering aid's course, volume 1: the rating, administration and safety, mathematics and units, "
     "drafting equipment, basic drafting techniques, lettering, geometric construction, projections and sketching.",
     "general")
rate("seabees", "navy_engineering_aid_3_2_vol2_1982", "Engineering Aid 3 & 2, Volume 2 (US Navy, NAVEDTRA 10628, "
     "1982)", "ERIC_ED249091", 1982, "NAVEDTRA 10628", "Construction materials and plans",
     "Volume 2: wood and light frame structures, heavy construction, concrete and masonry materials, mechanical and "
     "electrical materials, road and airfield construction, construction drawings, mechanical and electrical plans, "
     "and specifications.", "general")
rate("seabees", "navy_engineering_aid_1_c_1974", "Engineering Aid 1 & C (US Navy, NAVEDTRA 10635, 1974)",
     "ERIC_ED105121", 1974, "NAVEDTRA 10635", "Surveying and engineering",
     "The senior engineering aid's course: Seabee administration and safety, geodesy and field astronomy, "
     "triangulation, level and traverse computations, construction and land surveys, topographic surveys, "
     "horizontal and vertical curves, surveying instrument care, drafting, planning and estimating, and materials "
     "testing.", "general")
rate("seabees", "navy_construction_mechanic_1_c_1975", "Construction Mechanic 1 & C (US Navy, NAVEDTRA 10645-E, 1975)",
     "ERIC_ED114657", 1975, "NAVEDTRA 10645-E", "Vehicle and heavy equipment repair",
     "The senior construction mechanic's course (Construction Mechanic 3 & 2 of 1978 is "
     "gpo:navy_construction_mechanic_3_2_1978): supervising public works transportation and battalion shops, "
     "engine overhaul, automotive electrical systems, diesel fuel systems, vehicle safety inspections and power "
     "trains.", ("machinery", "chemical"))
rate("seabees", "navy_construction_mechanic_1_c_1982", "Construction Mechanic 1 & C (US Navy, NAVEDTRA 10645-F, 1982)",
     "ERIC_ED219598", 1982, "NAVEDTRA 10645-F", "Vehicle and heavy equipment repair",
     "The 1982 edition: administration, supervision, public works and battalion shops, engine overhaul, automatic "
     "transmissions, electrical and fuel systems and power trains of automotive, materials-handling and construction "
     "equipment.", ("machinery", "chemical"))
rate("seabees", "navy_constructionman_1953", "Constructionman (US Navy, NAVPERS 10630-A, 1953)",
     "Constructionman10630A", 1953, "NAVPERS 10630-A", "Seabee basics",
     "The 1953 course for the new Seabee: surveying for construction, earth moving and transport, the mechanic's "
     "work, constructing with wood and steel, AC and DC power in construction, fresh water and field sanitation, "
     "and choosing a rating.", ("general", "machinery"), via=NAVPERS_COLL)
rate("seabees", "navy_seabee_combat_handbook_1989", "Seabee Combat Handbook (US Navy, NAVEDTRA 10479-C3, 1989)",
     "DTIC_ADA218589", 1989, "NAVEDTRA 10479-C3", "Seabee field skills",
     "The 1989 edition, before the two-volume handbook of 1993 and 1996 (milw:navy_seabee_combat_handbook_v1_1993): "
     "Seabee history, clothing and equipment, leadership and fitness, the service rifle and pistol, support weapons, "
     "communications, shelters and entanglements, protective measures, formations, patrols, troop movement, defence, "
     "land navigation, evasion and survival, the rules of war, first aid and CBR defence. Its chapter 7 (hand "
     "grenades, land mines and booby traps) is left out. Prints Distribution Statement A.", ("ordnance", "medical"),
     keep_parts=r"^(?!.*\b(explosives?|demolitions?|land\s*mines?|booby|grenades?)\b)")

# ====================================================================== medical and dental

rate("medical", "navy_standard_first_aid_1991", "Standard First Aid Training Course (US Navy, NAVEDTRA 12081, 1991)",
     "navaleducationandtrainingprogrammanagementsupportactivity_standardfirstaidtrainingcourse_1991", 1991,
     "NAVEDTRA 12081", "First aid",
     "The Navy's first aid course for every sailor: basic life support, bleeding, shock, wounds, injuries to bones, "
     "joints and muscles, heat and cold, CBR casualties, poisons, common medical emergencies, rescue and "
     "transportation, and health. Prints Distribution Statement A.", "medical", via=UPLOAD)
rate("medical", "navy_standard_first_aid_1978", "Standard First Aid Training Course (US Navy, NAVEDTRA 10081-C, 1978)",
     "ERIC_ED200434", 1978, "NAVEDTRA 10081-C", "First aid",
     "The 1978 edition for nonmedical sailors: basic life support, bleeding, shock, wounds, injuries, drug abuse, "
     "poisoning, common medical emergencies, NBC casualties and rescue and transport.", "medical")
rate("medical", "navy_hospital_corpsman_3_2_1981", "Hospital Corpsman 3 & 2 (US Navy, NAVEDTRA 10669-B, 1981)",
     "DTIC_ADA191851", 1981, "NAVEDTRA 10669-B", "Medicine and patient care",
     "The corpsman's course (the 2000 course is pdf:navy_hospital_corpsman): the hospital corpsman, anatomy and "
     "physiology, first aid and emergency procedures, patient care, the clinical laboratory, pharmacology and "
     "toxicology, pharmacy, health records and physical examinations, administration, preventive medicine and CBR "
     "warfare.", "medical")
rate("medical", "navy_hospital_corpsman_1_c_1981", "Hospital Corpsman 1 & C (US Navy, NAVEDTRA 10670-B, 1981)",
     "ERIC_ED206910", 1981, "NAVEDTRA 10670-B", "Independent duty medicine",
     "The senior corpsman's course, built around independent duty: sick call, history taking, examination, diagnosis "
     "and treatment, emergency dental care, health inspections, elementary laboratory work, environmental and "
     "preventive medicine, and medical administration.", "medical")
rate("medical", "navy_hospital_corpsman_1_1955", "Hospital Corpsman 1 (US Navy, NAVPERS 10667, 1955)",
     "HospitalCorpsman1", 1955, "NAVPERS 10667", "Medicine and patient care",
     "The 1955 course for the first class corpsman, in nine chapters with tests, drawn from the Handbook of the "
     "Hospital Corps, the Manual of Naval Hygiene and Sanitation and the Navy's medical and supply manuals.",
     "medical", via="a person's upload of the Navy's own book to the Internet Archive")
rate("medical", "navy_handbook_hospital_corps_1959", "Handbook of the Hospital Corps, United States Navy (8th edition, "
     "1959)", "HandbookOfTheHospitalCorps1959", 1959, "Handbook of the Hospital Corps, 8th edition",
     "Nursing and medicine", "The corpsman's handbook of 1959: nursing and nursing procedures (patient care, vital "
     "signs, giving medicines, oxygen and fluids, heat and cold, procedures), and the corpsman's other duties.",
     "medical", via=BUMED)
rate("medical", "navy_handbook_hospital_corps_1949", "Handbook of the Hospital Corps, United States Navy (1949)",
     "14410660R.nlm.nih.gov", 1949, "Handbook of the Hospital Corps (1949 edition)", "First aid and medicine",
     "The corpsman's handbook of 1949: first aid and minor surgery, bleeding, wounds and transport of the injured, "
     "nursing, and the corpsman's other duties of its day.", "medical", via=NLM)
rate("medical", "navy_hospital_corps_handbook_1923", "Hospital Corps Handbook, United States Navy (1923)",
     "14410630R.nlm.nih.gov", 1923, "Hospital Corps Handbook (1923 edition)", "Medicine, as history",
     "The corpsman's handbook of 1923, history only: the corps' history, anatomy and physiology, first aid and "
     "minor surgery, bandaging and dental first aid, nursing, the operating room, anaesthesia, physiotherapy, foods, "
     "preventive medicine and sanitation, chemistry, pharmacy, materia medica, toxicology, bacteriology and blood "
     "work, and duty independent of medical officers. Public domain also as published before 1931.", "medical",
     via=NLM)
rate("medical", "navy_dental_assistant_advanced_1989", "Dental Assistant, Advanced (US Navy, NAVEDTRA 10678-A, 1989)",
     "DTIC_ADA218590", 1989, "NAVEDTRA 10678-A", "Dental assisting",
     "The course for senior dental technicians: the rating, the Navy medical department, legal aspects of patient "
     "care, operative and preventive dentistry, oral surgery, endodontics and periodontics, prosthodontics, "
     "extraoral radiography, training, dental administration and reports, records, supply, property and financial "
     "management. Prints Distribution Statement A.", "medical")
rate("medical", "navy_casualty_care_dental_personnel_1965", "Casualty Care Training Manual for Dental Personnel (US "
     "Navy, NAVMED P-5073, 1965)", "CasualtyCareTrainingManualForDentalPersonnel1965", 1965, "NAVMED P-5073",
     "Emergency care", "Lesson plans that taught Navy dental officers and technicians to help in mass casualties: "
     "battle dressing stations, the airway, bleeding, shock, resuscitation, wounds, dressings and splints, chest, "
     "abdominal, head and neck wounds, fractures, burns, fluids, medicines and radiation, biological and chemical "
     "injuries.", "medical", via=BUMED)

# ====================================================================== supply, administration, food and media

rate("supply", "navy_mess_management_specialist_3_2_1976", "Mess Management Specialist 3 & 2 (US Navy, NAVEDTRA 10267, "
     "1976)", "micro_IA41153047_0474", 1976, "NAVEDTRA 10267", "Cooking and galley management",
     "The Navy cook's course: running dining facilities and living quarters, estimating food, stowing perishable "
     "and semiperishable food, checking quality, menus, planning, preparing and serving meals, and keeping "
     "galleys and storerooms clean and sanitary. (Culinary Specialist of 2010 is pdf:navy_culinary_specialist.)",
     "food")
rate("supply", "navy_mess_management_specialist_1_c_1987", "Mess Management Specialist 1 & C (US Navy, NAVEDTRA "
     "10268-A, 1987)", "messmanagementsp015033mbp", 1987, "NAVEDTRA 10268-A", "Food service management",
     "The senior cook's course: supply organization, administration, the Navy ration system, buying, handling and "
     "storing food, financial reports, nutrition and menu planning, managing quarters and special feeding "
     "operations. Prints Distribution Statement A.", "food")
rate("supply", "navy_commissaryman_1_c_1973", "Commissaryman 1 & C (US Navy, NAVTRA 10280-F, 1973)",
     "micro_IA41152922_0726", 1973, "NAVTRA 10280-F", "Food service management",
     "The senior commissaryman's course (the rating before Mess Management Specialist): advancement, food service "
     "administration, supply, records and supervision.", "food")
rate("supply", "navy_ship_servicemens_handbook_1971", "Ship's Serviceman's Handbook (US Navy, NAVPERS 10292-A, 1971)",
     "ERIC_ED082009", 1971, "NAVPERS 10292-A", "Laundry, tailoring and barbering",
     "The handbook of the ship's service trades: administration of ship's service activities, then the laundryman, "
     "the tailor and the barber, each with equipment, processes, procedures and routine maintenance.",
     ("chemical", "general"))
rate("supply", "navy_ships_serviceman_3_2_1970", "Ship's Serviceman 3 & 2 (US Navy, NAVPERS 10286-F, 1970)",
     "micro_IA41153047_0461", 1970, "NAVPERS 10286-F", "Ship's stores and services",
     "The ship's serviceman's course: the supply department, administration, funds, procurement, inventory and "
     "stock control, receipt and storage, resale activities (the ship's store) and service activities (barber, "
     "cobbler, tailor and laundry).", "general")
rate("supply", "navy_ships_serviceman_laundry_handbook_1976", "Ship's Serviceman Laundry Handbook (US Navy, NAVEDTRA "
     "10293, 1976)", "micro_IA41153035_0590", 1976, "NAVEDTRA 10293", "Laundry and dry cleaning",
     "The ship's laundry course: running ship's service activities (equipment maintenance, supervision, buying "
     "supplies), then eleven chapters on the work of the laundry.", ("chemical", "machinery"))
rate("supply", "navy_ships_serviceman_3_1990", "Ship's Serviceman 3 (US Navy, NAVEDTRA 10176, 1990)",
     "shipsserviceman3004172mbp", 1990, "NAVEDTRA 10176", "Ship's stores, barbering and laundry",
     "The 1990 course: organization and security, running the sales outlets, stowage, barbershop service, the "
     "ship's laundry and dry cleaning. Prints Distribution Statement A.", ("chemical", "general"))
rate("supply", "navy_storekeeper_1_c_1974", "Storekeeper 1 & C (US Navy, NAVEDTRA 10270, 1974)", "ERIC_ED106511", 1974,
     "NAVEDTRA 10270", "Supply and storekeeping",
     "The senior storekeeper's course: administration, the Navy supply system, inventory management, procurement, "
     "receipts and expenditures, shipping, afloat funding and accounting, reports, stowage afloat and ashore and "
     "automated supply procedures.", "general")
rate("supply", "navy_yeoman_1_c_1973", "Yeoman 1 & C (US Navy, NAVTRA 10241-F, 1973)", "micro_IA41155155_0495", 1973,
     "NAVTRA 10241-F", "Office administration",
     "The senior yeoman's (office clerk's) course: the captain's office, drafting correspondence, ship's "
     "organization, officer separations, courts-martial, fact-finding bodies and casualty reporting, and security, "
     "with a grammar review.", "general")
rate("supply", "navy_postal_clerk_3_2_1973", "Postal Clerk 3 & 2 (US Navy, NAVEDTRA 10215, 1973)", "ERIC_ED101123",
     1973, "NAVEDTRA 10215 (Postal Clerk)", "Post office work",
     "The Navy postal clerk's course: the Navy postal service and post office, accepting domestic mail, "
     "classification and rates, registered and other special mail, stamps, money orders, international mail, "
     "outgoing and incoming mail, directory service, claims, audits and records.", "general")
rate("supply", "navy_journalist_3_2_1973", "Journalist 3 & 2 (US Navy rate training manual, 1973)", "ERIC_ED101124",
     1973, "NAVTRA rate training manual (Journalist 3 & 2)", "Journalism and public affairs",
     "The Navy journalist's course: Navy public affairs, news gathering, basic newswriting, features, speech, sports "
     "and other stories, magazine writing, copy editing, libel, privacy and copyright, newspapers and wire services, "
     "photography and photojournalism, publications, headlines, layout and broadcasting.", "general")
rate("supply", "navy_journalist_1_c_1978", "Journalist 1 & C (US Navy rate training manual, 1978)", "ERIC_ED158280",
     1978, "NAVEDTRA rate training manual (Journalist 1 & C)", "Public affairs management",
     "The senior journalist's course: public affairs policy, office management, community relations and special "
     "events, oral and visual communication, public affairs in adverse news, the combined information bureau, the "
     "complex news story, scientific writing, the picture story and newsfilm, and radio and television station "
     "management.", "general")
rate("supply", "navy_illustrator_draftsman_1_c_1973", "Illustrator Draftsman 1 & C (US Navy rate training manual, "
     "1973)", "ERIC_ED097460", 1973, "NAVTRA rate training manual (Illustrator Draftsman 1 & C)",
     "Illustration and graphic design",
     "The senior illustrator's course: administration, cartooning, screen process printing, colour, visual "
     "presentations, and typography and layout, with a glossary.", ("chemical", "general"))
rate("supply", "navy_draftsman_2_1956", "Draftsman 2 (US Navy, NAVPERS 10473, 1956)", "Draftsman210473", 1956,
     "NAVPERS 10473", "Technical drawing",
     "The 1956 draftsman's course: instruments, pictorial drawings, mathematics, machine parts, development of "
     "surfaces, heating and ventilation, aeronautical, electrical and structural drawings, surveying and plotting, "
     "lettering, maps and charts, lithographic drafting, and layout and illustration.", "general", via=NAVPERS_COLL)
rate("supply", "navy_draftsman_1_c_1958", "Draftsman 1 & C (US Navy, NAVPERS 10475, 1958)", "Draftsman1andC10475", 1958,
     "NAVPERS 10475", "Technical drawing",
     "The 1958 senior draftsman's course: administration, auxiliary views and perspective, mechanics, statics and "
     "strength of materials, machine and mechanical drafting and the draftsman's other work.", "general",
     via=NAVPERS_COLL)
rate("supply", "navy_lithographer_3_2_1975", "Lithographer 3 & 2 (US Navy rate training manual, 1975)",
     "ERIC_ED110635", 1975, "NAVEDTRA rate training manual (Lithographer 3 & 2)", "Offset printing",
     "The Navy printer's course: job planning, cold type composition, artwork, photographic equipment and materials, "
     "line and halftone negatives, stripping, platemaking, offset presses and duplicators, paper and ink, bindery "
     "equipment and letterpress.", "chemical")

# ====================================================================== aviation

rate("aviation", "navy_aviation_machinists_mate_1_c_1984", "Aviation Machinist's Mate 1 & C (US Navy, NAVEDTRA "
     "10324-A, 1984)", "DTIC_ADA460140", 1984, "NAVEDTRA 10324-A", "Aircraft engines",
     "The senior aircraft engine mechanic's course: fuel system maintenance, power plant troubleshooting and repair, "
     "propeller maintenance and jet engine testing and operation. Prints Distribution Statement A.", "aviation")
rate("aviation", "navy_aviation_machinists_mate_r_1_c_1974", "Aviation Machinist's Mate R 1 & C (US Navy, NAVEDTRA "
     "10344, 1974)", "ERIC_ED106513", 1974, "NAVEDTRA 10344", "Piston aircraft engines",
     "For the reciprocating-engine mechanic: aviation supply, work centre supervision, reciprocating engine systems "
     "and troubleshooting, engine analyzers, engine removal and installation, fuel systems, propellers and "
     "helicopter maintenance.", "aviation")
rate("aviation", "navy_aviation_machinists_mate_j_1_c_1972", "Aviation Machinist's Mate J 1 & C (US Navy, NAVTRA "
     "10343-C, 1972)", "micro_IA41153047_0454", 1972, "NAVTRA 10343-C", "Jet engines",
     "For the jet engine mechanic: aviation supply, work centre supervision, the Jetcal analyzer, fuel system "
     "maintenance, turbojet troubleshooting, removal and installation.", "aviation")
rate("aviation", "navy_aviation_machinists_mate_phase_1_1978", "Aviation Machinist's Mate, Phase I (US Navy course "
     "adapted for vocational education, 1978)", "ERIC_ED223899", 1978,
     "Military Curriculum Materials 2-5 (Navy Aviation Machinist's Mate course)", "Aircraft engines",
     "The first phase of the Navy's aviation machinist's school, in the Military Curriculum Materials series: "
     "teacher and student materials on aerodynamics, hand tools, electricity, mathematics and physics, and aircraft "
     "maintenance.", "aviation")
rate("aviation", "navy_aviation_machinists_mate_phase_2_1978", "Aviation Machinist's Mate, Phase II (US Navy course "
     "adapted for vocational education, 1978)", "ERIC_ED223900", 1978,
     "Military Curriculum Materials 2-6 (Navy Aviation Machinist's Mate course)", "Aircraft engines",
     "The second phase, fixed-wing aircraft: maintaining aircraft engines, inspections, field testing and adjusting "
     "components, and replacing compressor and turbine blades and combustion liners.", "aviation")
rate("aviation", "navy_aviation_structural_mechanic_s_3_2_1974", "Aviation Structural Mechanic S 3 & 2 (US Navy, "
     "NAVTRA 10308-C, 1974)", "ERIC_ED090391", 1974, "NAVTRA 10308-C", "Airframes and sheet metal",
     "For the structures mechanic: aeronautic publications, aircraft materials, airframe construction, sheet-metal "
     "machines, tools and procedures, aircraft hardware, damage repair, airframe maintenance, wheels and tyres, and "
     "tubing.", ("aviation", "chemical"))
rate("aviation", "navy_aviation_structural_mechanic_e_3_2_1972", "Aviation Structural Mechanic E 3 & 2 (US Navy, "
     "NAVTRA 10309-C, 1972)", "ERIC_ED132363", 1972, "NAVTRA 10309-C", "Aircraft safety and survival systems",
     "For the safety equipment mechanic: aeronautic publications, hand tools, tubing and hose, corrosion control and "
     "the ejection seats, canopies, oxygen, air-conditioning and pressurization systems of naval aircraft.",
     ("aviation", "chemical"))
rate("aviation", "navy_aviation_structural_mechanic_s_1_c_1975", "Aviation Structural Mechanic S 1 & C (US Navy, "
     "NAVEDTRA 10311-C, 1975, reprinted 1984)", "micro_IA41152638_0125", 1975, "NAVEDTRA 10311-C", "Airframe repair",
     "The senior structures course: airframe repair, alignment and maintenance, heat treatment and testing of "
     "metals, nondestructive inspection, and oxyacetylene welding, brazing and soldering.", ("aviation", "welding"),
     via="the Internet Archive's scan of the Government Printing Office microfiche")
rate("aviation", "navy_aviation_structural_mechanic_e_1_c_1985", "Aviation Structural Mechanic E 1 & C (US Navy, "
     "NAVEDTRA 10312-D, 1985)", "micro_IA41152823_0975", 1985, "NAVEDTRA 10312-D", "Ejection seats and egress systems",
     "The senior safety equipment course: emergency egress and canopy systems, the Martin-Baker ejection seat, "
     "oxygen and air-conditioning and pressurization systems.", "aviation",
     via="the Internet Archive's scan of the Government Printing Office microfiche")
rate("aviation", "navy_aviation_structural_mechanic_h_1_c_1976", "Aviation Structural Mechanic H 1 & C (US Navy, "
     "NAVEDTRA 10313-C, 1976)", "micro_IA41153035_0584", 1976, "NAVEDTRA 10313-C", "Aircraft hydraulics",
     "The senior course for aviation structural mechanics in hydraulics (AMH): aircraft hydraulic systems and the "
     "duties of the rate.", ("aviation", "machinery"))
rate("aviation", "navy_aviation_structural_mechanic_first_class_1981", "Aviation Structural Mechanic, First Class (US "
     "Navy course adapted for vocational education, 1981)", "ERIC_ED226193", 1981,
     "Military Curriculum Materials 2-12 (Navy Aviation Structural Mechanic course)", "Aircraft sheet metal repair",
     "Three self-paced pamphlets: aircraft maintenance management, records and reports; sheet metal layout and "
     "forming with simple shop mathematics; and aircraft damage repair.", "aviation")
rate("aviation", "navy_aviation_structural_mechanic_second_class_1981", "Aviation Structural Mechanic, Second Class "
     "(US Navy course adapted for vocational education, 1981)", "ERIC_ED226194", 1981,
     "Military Curriculum Materials 2-13 (Navy Aviation Structural Mechanic course)", "Aircraft structural repair",
     "Five self-paced pamphlets: safety in aircraft ground handling and maintenance, aircraft hardware (bolts, "
     "rivets and fasteners) and the structural maintenance and repair of aircraft.", "aviation")
rate("aviation", "navy_aviation_structural_mechanic_handbook_1953", "Aviation Structural Mechanic Handbook (US Navy, "
     "NAVPERS 10328, 1953)", "AviationStructuralMechanicHandbook10328", 1953, "NAVPERS 10328",
     "Aircraft metalwork and repair",
     "The 1953 handbook: hand tools and bench equipment, machines and power tools, sheet metal, aircraft metals, heat "
     "treatment, finishing and corrosion prevention, fasteners, structural repair and inspection, nonmetallic "
     "materials, welding, aircraft hydraulics and publications.", ("aviation", "welding"), via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_structural_maintenance_1951", "Aircraft Structural Maintenance (US Navy, NAVPERS "
     "10329, 1951)", "AircraftStructuralMaintenance10329", 1951, "NAVPERS 10329", "Aircraft metalwork and repair",
     "Structural elements and stresses, metal properties, blueprint reading and layout, fabrication, rivets and "
     "riveting, fasteners, structural repair, tubing, rubber equipment, transparent plastics and fabric covering.",
     "aviation", via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_metal_work_1945", "Aircraft Metal Work (US Navy, 1945)", "AircraftMetalWork1945", 1945,
     "NAVPERS training course (Aircraft Metal Work)", "Aircraft sheet metal",
     "Metal processes, forming aluminium, riveting, fasteners, structural repairs, tanks, tubing and plastics.",
     "aviation", via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_welding_1953", "Aircraft Welding (US Navy, NAVPERS 10322-A, 1953)",
     "AircraftWelding10322A", 1953, "NAVPERS 10322-A", "Welding",
     "Oxyacetylene and electric arc welding: equipment, fundamental techniques, ferrous and nonferrous metals, "
     "aircraft tubing, cutting, brazing and soldering, arc welding processes, inert-gas and atomic hydrogen "
     "welding, with a glossary.", ("welding", "aviation"), via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_engines_1951", "Aircraft Engines (US Navy, NAVPERS 10334-A, 1951)",
     "AircraftEngines10334A", 1951, "NAVPERS 10334-A", "Aircraft engines",
     "Power, engine parts, ignition, accessories, lubrication and cooling, the Pratt & Whitney and Wright radial "
     "engines of the day, and the first turbojet and turboprop engines (J33, J34, J42, T40).", "aviation",
     via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_fuel_systems_1954", "Aircraft Fuel Systems (US Navy, NAVPERS 10335-A, 1954)",
     "AircraftFuelSystems10335A", 1954, "NAVPERS 10335-A", "Aircraft fuel systems and carburettors",
     "Kinds of fuel systems, tanks and tubing, accessories, fuel pumps, carburetion, float-type and injection "
     "carburettors and their testing, induction systems and turbojet fuel systems.", ("aviation", "chemical"),
     via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_hydraulics_1951", "Aircraft Hydraulics (US Navy, NAVPERS 10332-A, 1951)",
     "AircraftHydraulics10332A", 1951, "NAVPERS 10332-A", "Aircraft hydraulics",
     "Hydraulic principles, fluid, seals and tubing, reservoirs and filters, pumps, pressure regulators, valves, "
     "actuating cylinders, accumulators, shock struts, brakes, shimmy dampers, complete systems and their "
     "inspection.", "aviation", via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_instruments_1954", "Aircraft Instruments (US Navy, NAVPERS 10333-A, 1954)",
     "AircraftInstruments10333A", 1954, "NAVPERS 10333-A", "Aircraft instruments",
     "Pressure and remote-reading instruments, gauges, air pressure instruments, thermometers, tachometers, fuel "
     "gauges and flowmeters, compasses, gyroscopes, automatic pilots, navigation instruments, testing and "
     "maintenance.", "aviation", via=NAVPERS_COLL)
rate("aviation", "navy_aircraft_propellers_1945", "Aircraft Propellers (US Navy, 1945)", "AircraftPropellers1945", 1945,
     "NAVPERS training course (Aircraft Propellers)", "Propellers",
     "Propeller principles, the two-position controllable-pitch, constant-speed, Hydromatic and electric propellers, "
     "and troubleshooting.", "aviation", via=NAVPERS_COLL)
rate("aviation", "navy_aviation_electricians_mate_3_2_1981", "Aviation Electrician's Mate 3 & 2 (US Navy, NAVEDTRA "
     "10348-E, 1981)", "ERIC_ED211684", 1981, "NAVEDTRA 10348-E", "Aircraft electrical systems",
     "Navy publications and supply, elementary physics, electrical maintenance and troubleshooting, aircraft power "
     "systems, electrical systems, instruments, and compass and inertial navigation systems.",
     ("aviation", "electric"))
rate("aviation", "navy_aviation_electricians_mate_1_c_1976", "Aviation Electrician's Mate 1 & C (US Navy rate training "
     "manual, 1976)", "ERIC_ED132272", 1976, "NAVEDTRA rate training manual (Aviation Electrician's Mate 1 & C)",
     "Aircraft electrical systems", "The senior aviation electrician's course, a ten-chapter text based on the AE1 "
     "and AEC standards: supervision and the electrical, instrument and navigation systems of naval aircraft.",
     ("aviation", "electric"))
rate("aviation", "navy_aviation_electronics_technician_3_2_1973", "Aviation Electronics Technician 3 & 2 (US Navy rate "
     "training manual, 1973)", "ERIC_ED099480", 1973, "NAVTRA rate training manual (Aviation Electronics Technician "
     "3 & 2)", "Avionics", "Publications, drawings and schematics, elementary physics, special tools, avionics "
     "support equipment and maintenance, airborne computers, power and cooling, airborne communications, navigation "
     "and radar, electronic countermeasures and security.", ("aviation", "radio"))
rate("aviation", "navy_aviation_electronics_technician_3_2_1956", "Aviation Electronics Technician 3 & 2 (US Navy, "
     "NAVPERS 10317, 1956)", "AvaiationElectronicsTechnician3and210317", 1956, "NAVPERS 10317", "Avionics",
     "The 1956 course: aircraft electric power, airborne radar and loran, test equipment, maintenance and "
     "publications, the AN/APS-33 radar, communication and navigation equipment and the radar equipment of its day.",
     ("aviation", "radio"), via=NAVPERS_COLL)
rate("aviation", "navy_aviation_boatswains_mate_h_1_c_1975", "Aviation Boatswain's Mate H 1 & C (US Navy, NAVEDTRA "
     "10303-C, 1975)", "ERIC_ED114655", 1975, "NAVEDTRA 10303-C", "Flight deck aircraft handling",
     "For the flight-deck aircraft handler: handling equipment, aircraft handling, crashes, firefighting and crew "
     "rescue, shore-based arresting gear and the other duties of the rate.", ("aviation", "fire"))
rate("aviation", "navy_aviation_boatswains_mate_e_1_c_1974", "Aviation Boatswain's Mate E 1 & C (US Navy, NAVEDTRA "
     "10305-C, 1974)", "ERIC_ED109344", 1974, "NAVEDTRA 10305-C", "Catapults and arresting gear",
     "For the launch and recovery equipment rating: leading petty officers, shop supervision and administration, "
     "steam catapults, catapult deck gear and accessories, arresting gear and visual landing aids.",
     ("aviation", "machinery"))
rate("aviation", "navy_aviation_boatswains_mate_f_3_2_1975", "Aviation Boatswain's Mate F 3 & 2 (US Navy, NAVEDTRA "
     "10301-D, 1975)", "micro_IA41153051_0163", 1975, "NAVEDTRA 10301-D", "Aviation fuel systems",
     "For the aviation fuels rating: operating, maintaining and repairing the aviation fuel and lubricating oil "
     "systems of carriers and other ships with aircraft, with a section on the metric system.",
     ("aviation", "chemical", "fire"))
rate("aviation", "navy_aviation_boatswains_mate_f_1_c_1975", "Aviation Boatswain's Mate F 1 & C (US Navy, NAVEDTRA "
     "10304-C, 1975)", "ERIC_ED110830", 1975, "NAVEDTRA 10304-C", "Aviation fuel systems",
     "The senior fuels course: the aviation fuels division afloat, JP-5 systems and their operation, gasoline "
     "systems, aviation lube oil, fuels ashore, quality assurance and surveillance, maintenance and repair and "
     "administration.", ("aviation", "chemical", "fire"))
rate("aviation", "navy_aerographers_mate_3_2_1976", "Aerographer's Mate 3 & 2 (US Navy, NAVEDTRA 10363, 1976)",
     "ERIC_ED132310", 1976, "NAVEDTRA 10363", "Weather observing",
     "The Navy weather observer's course: pressure, wind equipment, temperature, humidity and precipitation, clouds "
     "and visibility, radar and satellite equipment, and the observer's other duties, in seventeen chapters.",
     "general")
rate("aviation", "navy_aerographers_mate_1_c_1974", "Aerographer's Mate 1 & C (US Navy, NAVEDTRA 10362-B, 1974)",
     "ERIC_ED105253", 1974, "NAVEDTRA 10362-B", "Weather forecasting",
     "The senior weather course: atmospheric physics and world climatology, air masses, circulation and fronts, "
     "forecasting upper-air and surface systems, clouds, precipitation, temperature, storms, icing and fog, tropical "
     "weather, weather briefing and flight forecasting.", "general")
rate("aviation", "navy_aerographers_mate_2_vol1_1988", "Aerographer's Mate Second Class, Volume 1 (US Navy, NAVEDTRA "
     "10370, 1988)", "dli.ernet.171107", 1988, "NAVEDTRA 10370", "Meteorology",
     "Fundamentals of meteorology (measurement, the earth and sun, pressure, temperature, moisture), atmospheric "
     "physics, general, secondary and tertiary circulation, air masses and fronts. Prints Distribution Statement A.",
     "general")
rate("aviation", "navy_aerographers_mate_2_vol2_1990", "Aerographer's Mate Second Class, Volume 2 (US Navy, NAVEDTRA "
     "10371, 1990)", "dli.ernet.171106", 1990, "NAVEDTRA 10371", "Oceanography and weather products",
     "Oceanography (the sea surface, the ocean body and floor), sound in seawater, satellite pictures of the ocean, "
     "and Navy and National Weather Service meteorological and oceanographic products and their use. Prints "
     "Distribution Statement A.", "general")
rate("aviation", "navy_aircrew_survival_equipmentman_3_2_1973", "Aircrew Survival Equipmentman 3 & 2 (US Navy, NAVTRA "
     "10358-E, 1973)", "ERIC_ED101081", 1973, "NAVTRA 10358-E", "Parachutes and survival equipment",
     "The parachute rigger's course: parachute inspection and familiarization, the work centre, packing and "
     "rigging, the parachute assemblies of the day, automatic actuators, maintenance and repair, sewing machines, "
     "fasteners, helmets and oxygen masks, protective equipment and life rafts.", "aviation")
rate("aviation", "navy_aircrew_survival_equipmentman_1_c_1971", "Aircrew Survival Equipmentman 1 & C (US Navy, NAVPERS "
     "10360-D, 1971)", "ERIC_ED082012", 1971, "NAVPERS 10360-D", "Parachutes and survival equipment",
     "The senior course: blueprints and patterns, work centre supervision, parachutes and anti-g suits, oxygen masks, "
     "pressure suits, oxygen regulators and test stands, liquid oxygen converters, survival and search and rescue "
     "equipment and sewing machine repair.", "aviation")
rate("aviation", "navy_aircrew_survival_equipmentman_3_2_vol1_1982", "Aircrew Survival Equipmentman 3 & 2, Volume 1 "
     "(US Navy, NAVEDTRA 10328-1, 1982)", "aircrewsurvivele014458mbp", 1982, "NAVEDTRA 10328-1",
     "Survival equipment and sewing",
     "History of parachutes, the rating, sewing machines, fabrication, flight clothing, anti-g and anti-exposure "
     "garments, torso harnesses, helmets and oxygen masks, survival items, survival radios and beacons, helicopter "
     "rescue devices and carbon dioxide. Prints Distribution Statement A.", "aviation")
rate("aviation", "navy_aircrew_survival_equipmentman_3_2_vol2_1983", "Aircrew Survival Equipmentman 3 & 2, Volume 2 "
     "(US Navy, NAVEDTRA 10329, 1983)", "aircrewsurvivele014459mbp", 1983, "NAVEDTRA 10329",
     "Parachutes, life rafts and oxygen",
     "Administration, parachute familiarization and inspections, automatic opening devices, the NB-8, NES-12 and "
     "NES-14A parachutes, inflatable survival equipment, life preservers, oxygen components, regulators and liquid "
     "oxygen converters, and the rigid seat survival kit.", "aviation")
rate("aviation", "navy_aviation_support_equipment_vol1_1981", "Aviation Support Equipment Technician, Volume 1, Basics "
     "(US Navy, NAVEDTRA 10325, 1981)", "ERIC_ED210557", 1981, "NAVEDTRA 10325", "Aircraft ground support equipment",
     "The basic volume for the ground support equipment ratings (ASE and ASM), who maintain the equipment that "
     "serves aircraft on the ground.", ("aviation", "machinery"))
rate("aviation", "navy_aviation_support_equipment_e_3_2_1974", "Aviation Support Equipment Technician E 3 & 2 (US "
     "Navy, NAVEDTRA 10314-B, 1974)", "ERIC_ED109303", 1974, "NAVEDTRA 10314-B", "Ground support equipment, electrical",
     "For the electrical support equipment technician: maintenance forms and records, publications, elementary "
     "physics, and the electrical systems and equipment of aircraft ground support gear.", ("aviation", "electric"))
rate("aviation", "navy_aviation_support_equipment_m_3_2_1976", "Aviation Support Equipment Technician M 3 & 2 (US "
     "Navy, NAVEDTRA 10315, 1976)", "ERIC_ED132243", 1976, "NAVEDTRA 10315", "Ground support equipment, mechanical",
     "Tools and lifting devices, support equipment, physics, publications, reciprocating gasoline and diesel "
     "engines, chassis systems, power trains, hardware, fuels, lubricants and hydraulics.", ("aviation", "machinery"))
rate("aviation", "navy_air_controlman_3_2_1975", "Air Controlman 3 & 2 (US Navy, NAVEDTRA 10367, 1975)",
     "ERIC_ED115776", 1975, "NAVEDTRA 10367", "Air traffic control",
     "The Navy air traffic controller's course: the rating and its qualifications, military aircraft designations "
     "and characteristics, the Federal air regulations, and air traffic control in thirteen technical chapters.",
     "aviation")
rate("aviation", "navy_air_controlman_1_c_1974", "Air Controlman 1 & C (US Navy, NAVEDTRA 10368, 1974)",
     "ERIC_ED105281", 1974, "NAVEDTRA 10368", "Air traffic control",
     "The senior course: flight planning, facility operation, terminal instrument procedures, air traffic control, "
     "emergency procedures, carrier air traffic control and administration.", "aviation")
rate("aviation", "navy_tradevman_1_c_1977", "Tradevman 1 & C (US Navy, NAVEDTRA 10378-D, 1977)",
     "micro_IA41153505_0601", 1977, "NAVEDTRA 10378-D", "Training devices and audio-visual equipment",
     "For the rating that kept the Navy's training devices and audio-visual aids working: installing, repairing and "
     "maintaining simulators, training devices and their equipment.", ("electric", "general"))

# ====================================================================== electronics, communications and data processing

ET_SERIES = ("one of the nine volumes of the Electronics Technician training series (1993 to 1997), which replaced "
             "Electronics Technician 3 & 2")
for _n, (_vol, _title, _num, _year, _what) in enumerate([
        (1, "Safety", "NAVEDTRA 12411-A", 1997, "naval safety, hazardous materials and electronics safety"),
        (2, "Administration", "NAVEDTRA 12412", 1993, "general and technical administration and logistics"),
        (3, "Communications Systems", "NAVEDTRA 14088", 1997, "communications fundamentals, equipment "
         "configurations, satellite communications, Link-11 and Link-4A, data communications and local-area networks"),
        (4, "Radar Systems", "NAVEDTRA 14089", 1993, "basic radar systems, equipment configurations, interfacing "
         "and safety"),
        (5, "Navigation Systems", "NAVEDTRA 14090", 1994, "surface navigation systems and tactical air navigation"),
        (6, "Digital Data Systems", "NAVEDTRA 14091", 1997, "computers, their hardware, controls, processors, "
         "memories, input and output, magnetic tape and disk, CD-ROM, printers and data conversion"),
        (7, "Antennas and Wave Propagation", "NAVEDTRA 14092", 1995, "wave propagation, antennas, transmission lines "
         "and waveguides"),
        (8, "Support Systems", "NAVEDTRA 14093", 1996, "liquid cooling, dry air, AC power distribution, ship's input "
         "systems and information transfer systems")], 1):
    rate("electronics", f"navy_electronics_technician_vol{_vol}_{_year}", f"Electronics Technician, Volume {_vol}: "
         f"{_title} (US Navy, {_num}, {_year})", f"et{_vol}_20200208", _year, _num, "Electronics",
         f"Volume {_vol}, {ET_SERIES}: {_what}. Prints Distribution Statement A.",
         ("electric", "radio"), via=UPLOAD, scan=False)
rate("electronics", "navy_electronics_technician_3_1957", "Electronics Technician 3 (US Navy, NAVPERS 10188-B)",
     "DTIC_ADA279042", 1957, "NAVPERS 10188-B", "Electronics",
     "The electronics technician's course: advancement, safety precautions, nomenclature, publications and records, "
     "electronic installations, test equipment, switchboards, operating adjustments of transmitters, receivers, "
     "teletype and facsimile, and the radar and other equipment of its day. DTIC's record dates it 1957 (another "
     "copy of the same scan is dated 1963).", ("electric", "radio"))
rate("electronics", "navy_electronics_technician_2_vol1_1953", "Electronics Technician 2, Volume 1 (US Navy, NAVPERS "
     "10190-A, 1953)", "ElectronicsTechnician2v110190A", 1953, "NAVPERS 10190-A", "Electronics",
     "The 1953 course: responsibilities, shipboard organization, parts and funds, records and publications, and test "
     "equipment for measurement and analysis (multimeters, vacuum-tube voltmeters, tube testers, oscilloscopes, "
     "signal generators and frequency measurement).", ("electric", "radio"), via=NAVPERS_COLL)
rate("electronics", "navy_communications_technician_m_3_2_1965", "Communications Technician M 3 & 2 (US Navy, NAVPERS "
     "10232-A, 1965)", "CommunicationsTechnicianM3and210232A", 1965, "NAVPERS 10232-A", "Electronics maintenance",
     "The maintenance branch of the communications technician rating: electronics safety, designations and "
     "administration, hand tools in electronics, transistor circuits, subminiature repair, installation and "
     "maintenance, test equipment, switching and synchros, radio wave propagation, antennas and transmission lines "
     "and transmitter adjustments.", ("electric", "radio"), via=NAVPERS_COLL)
rate("electronics", "navy_radioman_3_2_1978", "Radioman 3 & 2 (US Navy, NAVEDTRA 10228-G, 1978)", "ERIC_ED160861", 1978,
     "NAVEDTRA 10228-G", "Radio communications",
     "The radioman's course, seventeen chapters: the first on the rating, advancement and preparing for Navy "
     "examinations, the other sixteen on the technical requirements of the rating (naval radio communications).",
     "radio")
rate("electronics", "navy_fire_controlman_2_1985", "Fire Controlman Second Class (US Navy, NAVEDTRA 10277, 1985)",
     "micro_IA41152806_0224", 1985, "NAVEDTRA 10277", "Servomechanisms and computers",
     "The fire controlman's course (the rating that maintains the ship's weapon-direction electronics): "
     "servomechanisms, analog computing elements and digital computers, with the occupational standards.",
     ("electric", "radio"), via="the Internet Archive's scan of the Government Printing Office microfiche")
rate("electronics", "navy_introduction_to_sonar_1976", "Introduction to Sonar (US Navy, revised 1976)",
     "ERIC_ED129585", 1976, "NAVEDTRA rate training manual (Introduction to Sonar)", "Sonar",
     "The sonar technician's course: obtaining and interpreting underwater data, operating and maintaining sonar "
     "equipment, and interpreting target and oceanographic data.", "electric")
rate("electronics", "navy_data_processing_technician_3_2_1973", "Data Processing Technician 3 & 2 (US Navy, revised "
     "1973)", "ERIC_ED096543", 1973, "NAVTRA rate training manual (Data Processing Technician 3 & 2)",
     "Data processing", "The data processing course (the forerunner of today's Information Systems Technician): "
     "the enlisted rating structure and advancement, then twelve chapters on automatic data processing, card "
     "punches and the other equipment the rating operated for the Navy's accounting and statistics.", "general")
rate("electronics", "navy_data_processing_technician_1_c_1981", "Data Processing Technician 1 & C (US Navy, NAVEDTRA "
     "10265-D, 1981)", "ERIC_ED212293", 1981, "NAVEDTRA 10265-D", "Data processing management",
     "The senior data processing course: the management and operational skills of a computer installation.",
     "general")
rate("electronics", "navy_eimb_communications_1962", "Electronics Installation and Maintenance Book: Communications "
     "(US Navy, NAVSHIPS 900,000.1, 1962)", "NAVSHIPS_900.000.1", 1962, "NAVSHIPS 900,000.1",
     "Radio equipment service notes", "The Navy's handbook of service notes on the radio receivers and transmitters of "
     "its day (AN/SRR, AN/FRR, AN/SRT, AN/URT and other sets): installation, adjustment and repair hints.", "radio",
     via=UPLOAD)
rate("electronics", "navy_eimb_electronic_circuits_1968", "Electronics Installation and Maintenance Book: Electronic "
     "Circuits (US Navy, NAVSHIPS 0967-000-0120, with change 1)", "navships-0967-000-0120-electronics-installation-"
     "and-maintenance-book-1968", 1968, "NAVSHIPS 0967-000-0120", "Electronic circuits",
     "The Navy's handbook of electronic circuits: power supplies (rectifiers, silicon-controlled rectifiers, "
     "vibrators), voltage regulators and the other circuits of its equipment, how they work and how to service them.",
     ("electric", "radio"), via=UPLOAD)
rate("electronics", "navy_eimb_radar_1974", "Electronics Installation and Maintenance Book: Radar (US Navy, NAVSHIPS "
     "0967-000-0020, 1974)", "NAVSHIPS_0967-000-0020_1974", 1974, "NAVSHIPS 0967-000-0020", "Radar",
     "The radar volume: general radar principles, circuit applications and service notes. Its front pages print "
     "\"For Official Use Only\", so the builder never makes it into a book: it goes to the catalogue's left_out as "
     "personal use, for the owner to fetch himself.", "radio", via=UPLOAD)
for _vol, _title, _year in [("1a", "Basic Electricity, Direct Current", 1965),
                            ("1b", "Basic Electricity, Alternating Current", 1965),
                            ("2", "Power Supplies and Amplifiers", 1965),
                            ("3", "Transmitter Circuit Applications", 1965),
                            ("4", "Receiver Circuit Applications", 1965),
                            ("5", "Oscilloscope Circuit Applications", 1965),
                            ("6", "Microwave Circuit Applications", 1965),
                            ("7", "Electromagnetic Circuits and Devices", 1965),
                            ("8", "Tables and Master Index", 1965)]:
    rate("electronics", f"navy_fundamentals_of_electronics_vol{_vol}_{_year}", f"Fundamentals of Electronics, Volume "
         f"{_vol}: {_title} (US Navy, NAVPERS 93400A-{_vol}, {_year})", f"FundamentalsOfElectronics93400A{_vol}",
         _year, f"NAVPERS 93400A-{_vol}", "Electronics",
         f"Volume {_vol} of the Navy's nine-volume textbook Fundamentals of Electronics: {_title.lower()}.",
         ("electric", "radio"), via=NAVPERS_COLL)
for _vol, _what in [("1", "the six-step logical troubleshooting procedure, from recognising symptoms to finding the "
                          "faulty part"),
                    ("2", "an automated (programmed) textbook of troubleshooting projects using the six steps"),
                    ("3", "the practice equipment's manual: a training oscilloscope, its controls and theory of "
                          "operation")]:
    rate("electronics", f"navy_troubleshooting_electronic_equipment_vol{_vol}_1965", f"Troubleshooting Electronic "
         f"Equipment, Volume {_vol} (US Navy, NAVPERS 93083A-{_vol}, 1965)",
         f"TroubleshootingElectronicEquipmentV{_vol}93083A{_vol}", 1965, f"NAVPERS 93083A-{_vol}",
         "Electronics troubleshooting", f"Volume {_vol}: {_what}.", "electric", via=NAVPERS_COLL)

# ====================================================================== general skills courses

rate("general", "navy_tools_and_their_uses_1971", "Tools and Their Uses (US Navy rate training manual, 1971)",
     "ERIC_ED132362", 1971, "NAVPERS rate training manual (Tools and Their Uses)", "Hand and power tools",
     "The Navy's basic tool course: identifying hand and power tools and fasteners by their right names, what each "
     "is for, how to use and care for them safely, measuring tools and safety.", "general")
rate("general", "navy_use_of_tools_1952", "Use of Tools (US Navy, NAVPERS 10623-A, 1952)", "UseOfTools10623A", 1952,
     "NAVPERS 10623-A", "Hand tools",
     "General-purpose tools, wrenches, metal-cutting tools, drilling, threads and thread cutting, metal fasteners, "
     "pipe and tubing tools, soldering and welding, woodworking with hand tools and measuring tools.", "general",
     via=NAVPERS_COLL)
rate("general", "navy_hand_tools_1944", "Hand Tools (US Navy training course, 1944)", "HandTools1944", 1944,
     "Navy training course (Hand Tools, 1944, second printing)", "Hand tools",
     "The Second World War course: general purpose tools, cutting and shaping tools, soldering, drilling and "
     "reaming, thread cutting, tubing tools, measuring tools and abrasives.", "general", via=NAVPERS_COLL)
rate("general", "navy_basic_machines_1965", "Basic Machines (US Navy training course, 1965)", "ERIC_ED173578", 1965,
     "Navy training course (Basic Machines, 1965)", "Mechanics",
     "The lever, block and tackle, wheel and axle, inclined plane, screw and gears, work and power, force and "
     "pressure, hydrostatic and hydraulic machines and complex machines. (The 1994 edition is "
     "pdf:navy_basic_machines.)", "general")
rate("general", "navy_basic_machines_1946", "Basic Machines (US Navy, NAVPERS 10624, 1946)", "BasicMachines10624", 1946,
     "NAVPERS 10624", "Mechanics",
     "The 1946 edition: levers, block and tackle, wheel and axle, inclined plane, screw, gears, work, power, force "
     "and pressure, hydrostatic and hydraulic machines and complex machines.", "general", via=NAVPERS_COLL)
rate("general", "navy_blueprint_reading_and_sketching_1956", "Blueprint Reading and Sketching (US Navy, NAVPERS "
     "10077-A, 1956)", "BlueprintReadingandSketching10077A", 1956, "NAVPERS 10077-A", "Reading technical drawings",
     "The 1956 edition of the basic course (the later NAVEDTRA 14040 is build:navy_blueprint_reading): the uses and "
     "kinds of blueprints, their language of lines, views and dimensions, and freehand sketching.", "general",
     via=NAVPERS_COLL)
rate("general", "navy_blueprint_reading_1957", "Blueprint Reading (US Navy, 1957)", "BlueprintReading1957", 1957,
     "NAVPERS training course (Blueprint Reading)", "Reading technical drawings and layout",
     "Making and handling blueprints, views, lines and sections, dimensions, title blocks and bills of material, "
     "layout tools and geometry, laying out, bend allowance, templates and developments.", "general",
     via=NAVPERS_COLL)
rate("general", "navy_use_of_blueprints_1944", "Use of Blueprints (US Navy, NAVPERS 10621, 1944)", "NAVPERS10621", 1944,
     "NAVPERS 10621", "Reading technical drawings",
     "The Second World War course: background, views, lines and sections, the working drawing, layout tools, "
     "developments, electrical blueprints and reading diagrams.", "general",
     via="a person's upload of the Navy's own book to the Internet Archive")
rate("general", "navy_mathematics_vol1_1966", "Mathematics, Volume 1 (US Navy, NAVPERS 10069-C, 1966)", "ERIC_ED064144",
     1966, "NAVPERS 10069-C", "Mathematics",
     "Basic mathematics: number systems, signed numbers, fractions, decimals and percentages, algebra (exponents, "
     "polynomials, linear equations), logarithms, the slide rule and the start of geometry and trigonometry.",
     "general")
rate("general", "navy_mathematics_vol2_1968", "Mathematics, Volume 2 (US Navy, NAVPERS 10071-B, 1968)", "ERIC_ED064145",
     1968, "NAVPERS 10071-B", "Mathematics",
     "College-level mathematics: logarithms and trigonometry, vectors and static equilibrium, coordinate geometry "
     "and conic sections, tangents and slopes, limits, differentiation and integration.", "general")
rate("general", "navy_mathematics_vol3_1969", "Mathematics, Volume 3 (US Navy, NAVPERS 10073-A, 1969)", "ERIC_ED064146",
     1969, "NAVPERS 10073-A", "Mathematics",
     "Mathematics for computers: sequences, induction and the binomial theorem, statistics, number systems other "
     "than decimal, sets and Venn diagrams and Boolean algebra.", "general")
rate("general", "navy_mathematics_vol2a_1989", "Mathematics, Volume 2-A (US Navy, NAVEDTRA 10062, 1989)",
     "mathematicsvolum004011mbp", 1989, "NAVEDTRA 10062", "Trigonometry",
     "Logarithms and computing with them, trigonometric measurement and analysis, oblique triangles, identities and "
     "equations, and vectors and forces. Prints Distribution Statement A.", "general")
rate("general", "navy_mathematics_basic_math_and_algebra_1985", "Mathematics, Basic Math and Algebra (US Navy, "
     "NAVEDTRA 14139, 1985 printing)", "US_Navy_Training_Course_-_Mathematics_Basic_Math_and_Algebra",
     1985, "NAVEDTRA 14139",
     "Arithmetic and algebra",
     "Number systems and sets, positive integers, signed numbers, fractions, decimals, percentage and measurement, "
     "exponents and radicals, logarithms, algebra, factoring, linear equations, ratio and proportion, and more. "
     "Prints Distribution Statement A.", "general", via=UPLOAD)
rate("general", "navy_mathematics_trigonometry_1989", "Mathematics, Trigonometry (US Navy, NAVEDTRA 14140, 1989)",
     "US_Navy_Training_Course_-_Mathematics_Trigonometry", 1989, "NAVEDTRA 14140", "Trigonometry",
     "Logarithms, trigonometric measurement and analysis, oblique triangles, identities and equations, vectors and "
     "forces. Prints Distribution Statement A.", "general", via=UPLOAD)
rate("general", "navy_mathematics_precalculus_probability_1988", "Mathematics, Pre-calculus and Introduction to "
     "Probability (US Navy, NAVEDTRA 14141, 1988)",
     "US_Navy_Training_Course_-_Pre-calculus_and_Introduction_to_Probability", 1988, "NAVEDTRA 14141",
     "Calculus and probability",
     "Straight lines, conic sections, tangents and slopes, limits and derivatives, integration, combinations, "
     "permutations and probability. Prints Distribution Statement A.", "general", via=UPLOAD)
rate("general", "navy_mathematics_statistics_number_systems_boolean_1986", "Mathematics, Introduction to Statistics, "
     "Number Systems and Boolean Algebra (US Navy, NAVEDTRA 14142, 1986)",
     "US_Navy_Training_Course_-_Introduction_to_Statistics_Number_Systems_and_Boolean_", 1986, "NAVEDTRA 14142",
     "Statistics and Boolean algebra",
     "Sequences and series, induction and the binomial theorem, descriptive statistics and inference, number "
     "systems, sets, Boolean algebra and its simplification, matrices and determinants. Prints Distribution "
     "Statement A.", "general", via=UPLOAD)
rate("general", "navy_advanced_mathematics_electronics_technicians_1951", "Advanced Mathematics for Electronics "
     "Technicians (US Navy, NAVPERS 10094, 1951)", "AdvancedMathematicsForElectronicsTechnicians10094", 1951,
     "NAVPERS 10094", "Mathematics",
     "Angles and direction, lines and angles, constructions, scale drawing, graphs, practical geometry formulas, the "
     "Pythagorean theorem, trigonometry, vectors, and an introduction to calculus.", "general", via=NAVPERS_COLL)
rate("general", "navy_basic_electricity_1945", "Basic Electricity (US Navy, NAVPERS 10622, 1945)",
     "BasicElectricity10622", 1945, "NAVPERS 10622", "Electricity",
     "The 1945 course: matter, static electricity, current, the circuit, EMF, Ohm's law, power, series and parallel "
     "circuits, magnetism, electromagnetism and the rest of basic electricity.", "electric", via=NAVPERS_COLL)
rate("general", "navy_electricity_1950", "Electricity (US Navy, NAVPERS 10622-A, 1950)", "Electricity10622A", 1950,
     "NAVPERS 10622-A", "Electricity",
     "The 1950 revision: matter, static electricity, current, circuits, EMF, Ohm's law, power, series and parallel "
     "circuits, magnetism, electromagnetism, induction and onward.", "electric", via=NAVPERS_COLL)
rate("general", "navy_basic_electricity_1956", "Basic Electricity (US Navy, NAVPERS 10086, 1956)",
     "BasicElectricity10086", 1956, "NAVPERS 10086", "Electricity",
     "The 1956 course: fundamental concepts, batteries, the simple circuit and Ohm's law, power and energy, DC "
     "series and parallel circuits, and onward.",
     "electric", via=NAVPERS_COLL)
rate("general", "navy_basic_electronics_1962", "Basic Electronics (US Navy, NAVPERS 10087-A, 1962)",
     "BasicElectronics10087A", 1962, "NAVPERS 10087-A", "Electronics",
     "Electron tubes, transistors, power supplies, tuned circuits, amplifiers, oscillators, transistor circuits, "
     "modulation and demodulation, transmitters, transmission lines and antennas, and onward.", ("electric", "radio"),
     via=NAVPERS_COLL)
rate("general", "navy_basic_hydraulics_1952", "Basic Hydraulics (US Navy, NAVPERS 16193, 1952)", "BasicHydraulics16193",
     1952, "NAVPERS 16193", "Hydraulics",
     "The development of hydraulics, properties of liquids, pressure and force, jacks and brakes, liquid flow, water "
     "hammer and the elements of working hydraulic systems. (Its later edition, Fluid Power, is "
     "rate:navy_fluid_power_1970.)", "machinery", via=NAVPERS_COLL)
rate("general", "navy_human_behavior_and_leadership_1977", "Human Behavior and Leadership (US Navy, NAVEDTRA 10058-B, "
     "1977)", "micro_IA41155120_0208", 1977, "NAVEDTRA 10058-B", "Leadership",
     "For petty officers: leadership techniques and styles, stress and conflict, interpersonal communication, "
     "human behaviour and motivation, and the basics of teaching and learning.", "general")

# ====================================================================== ordnance, as history

ORDNANCE_NOTE = (" Kept as history, read whole but for its chapter on explosives and pyrotechnics, which the "
                 "library's rule leaves out.")
rate("ordnance", "navy_gunners_mate_3_2_1996", "Gunner's Mate 3 & 2 (US Navy, NAVEDTRA 14109, 1996)",
     "GunnersMate32NAVEDTRA14109", 1996, "NAVEDTRA 14109", "Naval guns and launchers, as history",
     "The gunner's mate's course: ammunition, magazines and missile handling, small arms, basic mechanisms, "
     "electrical and electronic circuit analysis, gun mounts, guided missile launching systems, missile aerodynamics, "
     "target detection and weapon control. Prints Distribution Statement A." + ORDNANCE_NOTE, "ordnance",
     via=UPLOAD, scan=False)
rate("ordnance", "navy_gunners_mate_1_c_1996", "Gunner's Mate 1 & C (US Navy, NAVEDTRA 14110, 1996)",
     "GunnersMate1CNAVEDTRA14110", 1996, "NAVEDTRA 14110", "Naval guns and launchers, as history",
     "The senior gunner's mate's course, on the same subjects for supervisors. Prints Distribution Statement A."
     + ORDNANCE_NOTE, "ordnance", via=UPLOAD, scan=False)
rate("ordnance", "navy_gunners_mate_g_3_2_1974", "Gunner's Mate G 3 & 2 (US Navy, NAVEDTRA 10185-B, 1974)",
     "ERIC_ED109343", 1974, "NAVEDTRA 10185-B", "Naval guns, as history",
     "The guns branch of the rating: ammunition and magazines, small arms and machine guns, gun mounts and their "
     "maintenance." + ORDNANCE_NOTE, "ordnance")
rate("ordnance", "navy_gunners_mate_m_1_c_1973", "Gunner's Mate M 1 & C (US Navy, NAVTRA 10200-B, 1973)",
     "ERIC_ED083389", 1973, "NAVTRA 10200-B", "Guided missile launchers, as history",
     "The missile branch of the rating: missile launching systems, loading and unloading, electricity and "
     "electronics, hydraulics and pneumatics of the launchers, their maintenance and overhaul." + ORDNANCE_NOTE,
     "ordnance")

PDFS = [entry for _trade, entry in BOOKS]
TRADE_OF = {entry["name"]: trade for trade, entry in BOOKS}

# ====================================================================== the index

# Navy books elsewhere in the library, by trade: (key, what it holds). Linked from the index, never built again.
ELSEWHERE = {
    "deck": [("pdf:navy_quartermaster_1_c", "Quartermaster 1 & C (NAVEDTRA 12122, 1991)"),
             ("kmil:navy_boatswains_mate_2c_1944", "Boatswain's Mate 2c (1944)"),
             ("milw:navy_basic_military_requirements_1992", "Basic Military Requirements (NAVEDTRA 12043, 1992), "
                                                            "the course every sailor takes"),
             ("pdf:navy_military_requirements_po3", "Military Requirements for Petty Officer Third Class (1991)"),
             ("kmil:bluejackets_manual_1927", "The Bluejackets' Manual (1927)"),
             ("pdf:navy_fireman_1976", "Fireman (1976): the engineering basics of the fireman rate")],
    "engineering": [("pdf:navy_engineman_3_2_1979", "Engineman 3 & 2 (1979)"),
                    ("pdf:navy_electricians_mate_3_2_1981", "Electrician's Mate 3 & 2 (1981)"),
                    ("make:navy_machinery_repairman_1993", "Machinery Repairman (1993)"),
                    ("pdf:navy_opticalman_3_2", "Opticalman 3 & 2 (NAVEDTRA 10215, 1989)"),
                    ("pdf:navy_fireman_1976", "Fireman (1976)")],
    "seabees": [("build:navy_builder_3_2_1981", "Builder 3 & 2 (1981)"),
                ("pdf:navy_construction_electrician_3_2_1976", "Construction Electrician 3 & 2 (1976)"),
                ("pdf:navy_utilitiesman_3_2_1973", "Utilitiesman 3 & 2 (1973)"),
                ("pdf:navy_equipment_operator_basic", "Equipment Operator, Basic (NAVEDTRA 14081, 1994)"),
                ("pdf:navy_construction_mechanic_advanced", "Construction Mechanic, Advanced (NAVEDTRA 14050, 1992)"),
                ("gpo:navy_construction_mechanic_3_2_1978", "Construction Mechanic 3 & 2 (1978)"),
                ("milw:navy_seabee_combat_handbook_v1_1993", "Seabee Combat Handbook, Volume 1 (1993)"),
                ("milw:navy_seabee_combat_handbook_v2_1996", "Seabee Combat Handbook, Volume 2 (1996)")],
    "medical": [("pdf:navy_hospital_corpsman", "Hospital Corpsman (NAVEDTRA 14295, 2000)")],
    "supply": [("pdf:navy_culinary_specialist", "Culinary Specialist (NAVEDTRA 15008, 2010)"),
               ("photo:navy_navedtra_14209_photography_basic", "Photography (Basic), NAVEDTRA 14209 (1993)"),
               ("photo:navy_navedtra_14208_photography_advanced", "Photography (Advanced), NAVEDTRA 14208 (1995)"),
               ("photo:navy_photographers_mate_1_c_1974", "Photographer's Mate 1 & C (1974)")],
    "electronics": [("pdf:navy_neets_module_01", "NEETS Module 1: matter, energy and direct current"),
                    ("pdf:navy_neets_module_10", "NEETS Module 10: wave propagation, transmission lines and antennas"),
                    ("elec:navy_neets_module_17", "NEETS Module 17: radio-frequency communications"),
                    ("elec:navy_neets_module_18", "NEETS Module 18: radar principles"),
                    ("pdf:navy_neets_module_19", "NEETS Module 19: the technician's handbook"),
                    ("pdf:navy_neets_module_22", "NEETS Module 22: digital computers")],
    "general": [("pdf:navy_basic_machines", "Basic Machines (NAVEDTRA 14037, 1994)"),
                ("build:navy_blueprint_reading", "Blueprint Reading and Sketching (NAVEDTRA 14040)"),
                ("pdf:navy_ac_and_transformers", "Introduction to Alternating Current and Transformers (1998)")],
}

# The ratings with no open copy found, by trade: (rating, what it does, why there is no book here).
NOT_FOUND = {
    "deck": [("Boatswain's Mate (NAVEDTRA 14343) and Seaman (NAVEDTRA 14067)", "deck seamanship, line handling, "
              "anchoring, small boats and painting", "only lending-library scans or no text layer were found"),
             ("Operations Specialist", "radar plotting, the combat information center and air control",
              "no open copy of its course was found")],
    "engineering": [("Hull Maintenance Technician and the 1990s Gas Turbine (Mechanical) courses", "welding, "
                     "plumbing, sheet metal and gas turbine mechanics on board", "no open copy was found")],
    "supply": [("Personnelman and Disbursing Clerk", "personnel records and pay", "no open copy was found")],
    "aviation": [("Parachute Rigger (the new name of Aircrew Survival Equipmentman) of the 2000s", "parachutes and "
                  "survival gear", "only the older Aircrew Survival Equipmentman courses here were found")],
    "electronics": [("Information Systems Technician (the 2000s training series)", "computer networks and radio "
                     "communications", "only manualzilla copies were found (a manual-copying site, not used)")],
    "ordnance": [("Torpedoman's Mate, Mineman, Explosive Ordnance Disposal and Aviation Ordnanceman",
                  "torpedoes, mines, "
                  "bomb disposal and aircraft weapons", "mostly explosives and mines (left out by the library's "
                  "rule), and the copies found were mixed uploads or admin-only volumes")],
}


def _sections():
    """The index's parts: an introduction, then one part per trade (its books, the Navy books elsewhere, and the
    ratings with no open copy) and a last part on the request words."""
    parts = [("How to use this guide", "Each Navy rating (an enlisted job) had a rate training manual: the textbook "
              "a sailor studied to advance, from third class (3) and second class (2) up to first class and chief "
              "(1 & C). These books teach practical trades: cooking, carpentry, welding, plumbing, electricity, "
              "engines, first aid, weather, printing and more. They are old: their rules, equipment and medicine "
              "are those of their year. Ask for a whole trade with its request word (each trade below names its "
              "own), or every book with the word navy-rates.", [
                  ("word", WORD, "every Navy rate training manual here, with this guide"),
                  ("link", "Navy enlisted ratings today (Navy COOL, Credentialing Opportunities On-Line)",
                   "https://www.cool.osd.mil/usn/", "a Department of Defense site that describes each rating today; "
                                                    "open it in a browser")])]
    for trade, title, words in TRADES:
        entries = [("word", TRADE_WORDS[trade], f"every book of this trade ({title.lower()})")]
        entries += [("key", f"rate:{e['name']}", e["title"]) for t, e in BOOKS if t == trade]
        entries += [("key", key, f"{what} (elsewhere in the library)") for key, what in ELSEWHERE.get(trade, [])]
        entries += [("link", f"{rating}: no book here", "https://archive.org/search?query=" +
                     rating.split(" (")[0].split(",")[0].replace(" ", "+").replace("'", "%27"),
                     f"{what}; {why}") for rating, what, why in NOT_FOUND.get(trade, [])]
        parts.append((title, words, entries))
    return parts


SECTIONS = _sections()
INDEX = X.index_maker("rate", GROUP, "Navy rate training manuals: a guide", "Navy ratings and their trades",
                      "A guide to the US Navy's rate training manuals in the library, by trade: what each rating does "
                      "in plain words, its books here, the Navy books elsewhere in the library, and the ratings for "
                      "which no open copy was found.", SECTIONS)
MAKERS = {"index": INDEX}


def _keys(trade=None):
    """The keys of one trade (or of every trade), the index first."""
    return ["rate:index"] + [f"rate:{e['name']}" for t, e in BOOKS if trade in (None, t)]


WORDS = {WORD: lambda: _keys()}
WORDS.update({TRADE_WORDS[t]: (lambda t=t: _keys(t)) for t in TRADE_IDS})
COLLECTION = K.Collection("rate", GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "navy_rates": "Navy rate training manuals (rate:): works of the US Navy (17 U.S.C. 105), read from the Internet "
                  "Archive (its ERIC, DTIC, NAVPERS, National Library of Medicine, Navy medicine history office, "
                  "Digital Library of India and Million Book Project copies and people's uploads of the Navy's own "
                  "PDFs); each judged at every build by the release rule for military publications "
                  "(military_release.py: Distribution Statement A printed on the 1980s and 1990s editions, no "
                  "statement on most older ones; the 1974 radar EIMB prints FOR OFFICIAL USE ONLY and is personal use "
                  "only), its explosives parts cut (NOT_FIELD_SAFE); archive.org's robots.txt allows the files; no "
                  "AI rules (checked 2026-11-23).",
    "navy_rates_index": "The index (rate:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("US Navy Seaman (1981), Quartermaster 3 & 2 (1951), Signalman 3 & 2 (1956), Storekeeper 3 & 2 (1951, 1968), "
     "Illustrator Draftsman 3 & 2 (1972), Lithographer 1 & C (1970), Machinist's Mate 3 & 2 (1985 printing), "
     "Aviation Fire Control Technician 1 & C (1973), Aviation Structural Mechanic 3 & 2 (1956), Electronics "
     "Technician 3 (1952), Radioman 3 & 2 (1950) and Tools and Their Uses (1973)", "Lending-library scans on the "
     "Internet Archive (access restricted): they cannot be downloaded (checked 2026-11-23). Index: "
     "https://archive.org/details/seaman00nava"),
    ("Navy training courses copied from manualzilla (Air Traffic Controller NAVEDTRA 14342, Engineering Aid 2, Mess "
     "Management NAVEDTRA 14164, Aerographer's Mate module 3, Information Systems Technician and Radioman training "
     "series, Interior Communications Electrician volume 2, Storekeeper 3 & 2, Fire Controlman)", "Copies taken from "
     "a manual-copying site (manualzilla), which the owner's rules do not use, even where the work itself is the "
     "Navy's. Index: https://archive.org/search?query=manualzilla+navedtra"),
    ("Data Systems Technician 3 & 2 (NAVEDTRA 10201, 1982 and 1985)", "Their front pages print CONFIDENTIAL (the "
     "classification of the equipment they describe) with no declassification shown, so the release rule leaves "
     "them out (checked 2026-11-23). Index: https://archive.org/details/datasystemstechn00nava"),
    ("Mineman 1 & C (NAVEDTRA 12432, 1990) and Torpedoman's Mate 3 & 2 (NAVPERS 10155, 1955)", "Mineman is about "
     "mine warfare (left out by the explosives rule); its remaining chapters (organization, supply, administration) "
     "are not worth a book. The Torpedoman's Mate item mixes 21 PDFs of torpedo histories and tube manuals, so the "
     "builder could not choose the training course from it. Index: https://archive.org/details/mineman1c021445mbp"),
    ("Handbook of the Hospital Corps, United States Navy (1939)", "The 1923, 1949 and 1959 editions are built; the "
     "1939 copies are a 382 MB scan (too big for the builder's memory) and lending-library or Wellcome print-disabled "
     "copies. Index: https://archive.org/details/HandbookOfTheHospitalCorpsUSN1939"),
    ("Electronics Installation and Maintenance Book: Electronic Circuits (NAVSHIPS 0967-000-0120, 1967 and 1972 "
     "copies)", "The same book as the 1968 copy built here (rate:navy_eimb_electronic_circuits_1968); the 1972 copy "
     "also prints \"For Official Use Only\". Index: https://archive.org/details/NAVSHIPS_0967-000-0120"),
    ("Ship's Serviceman 2 (1990), Constructionman (NAVPERS 10630-E, 1971), Engineering Aid 3 & 2 Volume 1 (NAVPERS "
     "10634-C, the Internet Archive's NAVPERS copy), Electronics Technician 3 (NAVPERS 10188-B, the uploaded copy), "
     "Quartermaster 1 & C (1969), Opticalman 1 & C (1966), Ocean Systems Technician 3 & 2 and Hospital Corpsman 3 & "
     "2 (1981, the microfiche copy)", "Ship's Serviceman 2 is a scan without a text layer; the 1971 Constructionman "
     "item's text could not be read (the archive answered with an error); Ocean Systems Technician is a 70-page "
     "fragment; the others are second copies or earlier printings of books built here. Index: "
     "https://archive.org/details/shipsserviceman2023171mbp"),
    ("Navy eLearning and the Naval Education and Training Command's course pages (netc.navy.mil)", "The Navy's own "
     "course site needs a login, and netc.navy.mil refuses programs (403, checked 2026-11-23); the courses are read "
     "from the Internet Archive's copies instead. Index: https://www.netc.navy.mil/"),
    ("Navy rating manuals on manual and PDF sites (navybmr.com, PDF Drive, Scribd and others)", "Not used, by the "
     "owner's rule: manual-copying sites, sites behind logins or CAPTCHAs. The Navy's own works on the Internet "
     "Archive are used instead. Index: https://archive.org/search?query=NAVEDTRA"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
