"""Small boats for the reference library, in the group "Reference, small boats" (the owner's request of 2026-11-22:
a small boats collection of books, manuals and pictures). Keys: small-boats (every book), boat:<name>.

What this module builds, in plain words:
  - boat:index, a guide to everything in the library on small boats (the toolkit's own facts and links, CC0): boat
    handling under oars, paddle, motor and sail; the navigation rules, buoyage and charts; tides, currents and
    weather; safety, life jackets, float plans and cold water (with the wilderness first aid books); building and
    repairing boats; maintenance (trailers, outboard and small engines, winterising); knots and rigging; and boat
    types by name. It lists the books by key, the manual collections, the picture packs and the link-only sources;
  - IN FULL, works of the US government:
      the amalgamated International and US Inland Navigation Rules as NOAA's Office of Coast Survey publishes them
      (the 72 COLREGS and 33 CFR 83 side by side); the US regulations on the inland rules (33 CFR
      parts 83 to 88) and on recreational boats (33 CFR 175, equipment such as life jackets; 33 CFR 183, boat
      building standards: capacity, flotation, ventilation, fuel and electrical systems; 46 CFR 25, fire
      extinguishers, ventilation and backfire flame arrestors), from govinfo's newest annual edition;
      three more volumes of the Coast Guard's Boat Crew Handbook series (Navigation and Piloting, Rescue and Survival
      Procedures, First Aid; Seamanship Fundamentals is already kmil:uscg_bch_seamanship_fundamentals);
      four Army watercraft manuals: FM 55-501 Marine Crewman's Handbook (1999), FM 55-130 Small Boats and Harbor
      Craft (1944), FM 55-502 Army Watercraft Safety (1996) and FM 55-509-1 Introduction to Marine Electricity
      (1994), each judged by the release rule for military publications (military_release.py) and read whole, only
      parts about explosives or demolition left out (build_textbooks.NOT_FIELD_SAFE);
      NOAA's tides and currents tutorials (the National Ocean Service's education pages) and the National Weather
      Service's marine weather pages (marine forecasts explained, the coastal warning flags, marine publications);
  - old public-domain books (published before 1931; the builder checks each item's year on the Internet Archive at
    every build): W. P. Stephens's Canoe and Boat Building (1889 edition), Douglas Frazar's Practical Boat-Sailing
    (1879), A. J. Kenealy's Boat Sailing in Fair Weather and Foul (1895), E. F. Knight's Small-Boat Sailing (1902),
    Charles F. Chapman's Practical Motor Boat Handling, Seamanship and Piloting (1917), H. W. Slauson's The Motor
    Boat, its Selection, Care and Use (1911), Warren Miller's The Boys' Book of Canoeing and Sailing (1917), Harper's
    Boating Book for Boys (1912), Stevens and Darling's Practical Rowing with Scull and Sweep (1906) and the
    Admiralty Manual of Navigation (1914). Each old book's description says what is out of date in it.
  Every book carries BOAT_SAFETY in its notice (life jacket, weather, float plan, cold water, never boating under
  the influence, carbon monoxide from engines, 911 and VHF channel 16); the building, repair and engine books also
  carry WORKSHOP_SAFETY (epoxy, resins, solvents, old lead paint, sanding dust, tools).

Already in the library and not repeated (linked from the index): the Coast Guard's Boater's Guide to the Federal
Requirements and its boating safety pages (outdoors:), the Coast Guard Boat Crew Handbook Seamanship Fundamentals,
the Bluejacket's Manual (1917), Boatswain's Mate 2c (1944) and the Admiralty Manuals of Seamanship 1915 to 1972
(kmil:), the knot books (knot:), U.S. Chart No. 1 (pdf:noaa_us_chart_no_1), Knight's Modern Seamanship and Bowditch
(1914) (pdf:), the Navy's Quartermaster rate manual (pdf:navy_quartermaster_1_c), NOAA's Ocean Facts
(science:noaa_ocean_facts), the NWS weather safety pages (prep:nws_safety), the cold-weather and backcountry safety
books (wild:), the Army trailer manual and the RV and trailer index (rvs:), the Forest Products Laboratory's Wood
Handbook (build:fpl_wood_handbook), and the manual collections for outboard motors (powersports), marine electronics,
small engines, kayaks, canoes and life jackets (outdoors).

Not built (NOT_INCLUDED, with the reason and an address): Chapman Piloting and the other modern boating books
(copyright), the US Coast Pilot (changes every week and NOAA warns about incomplete copies), the RNLI, US Sailing,
ASA, ACA, America's Boating Club, WoodenBoat and the boat and engine makers' manuals (copyright: link-only), Transport
Canada's Safe Boating Guide, Maritime New Zealand and the Australian state handbooks, the Admiralty navigation
manuals of 1938 to 1973, and the old books whose scans have no text layer or whose records show a later printing.

Run from the repository's folder:
  python3 textbooks/small_boats.py boat:noaa_navigation_rules --out build/textbooks --limit 3
  python3 textbooks/small_boats.py --list small-boats
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "boats"
GROUPS = {GROUP: "Reference, small boats"}

# The safety notes (the same words as packs/small_boats_packs.py BOAT_NOTE and WORKSHOP_NOTE, written for a book).
BOAT_SAFETY = ("Safety on the water: wear a life jacket that fits, and make sure everyone aboard has one. Check the "
               "weather and water before you go and keep watching it. File a float plan: tell someone ashore where "
               "you are going and when you will be back. Cold water kills: cold shock and hypothermia can stop you "
               "swimming within minutes, so dress for the water, not the air. Never boat under the influence of "
               "alcohol or drugs. Engines make carbon monoxide: keep away from exhausts and the swim platform while "
               "an engine runs, and keep a carbon monoxide alarm in any cabin. Take a boating safety course. In an "
               "emergency call 911 or the Coast Guard on VHF channel 16.")
WORKSHOP_SAFETY = ("Workshop safety: epoxy, polyester resin, solvents, paint strippers and old paints (many old "
                   "paints contain lead) are hazardous. Work with good ventilation, wear gloves, eye protection and a "
                   "respirator for organic vapours (and a dust mask for sanding), keep sparks and flames away from "
                   "solvents and fuel, and follow each product's safety data sheet. Use guards, eye and hearing "
                   "protection with power tools.")
OLD_BOAT_NOTE = ("Published in {year}: an old book. Its boats, engines, materials and rules of the road are those of "
                 "its day: life jackets were rarely worn, the navigation rules have changed, its paints and "
                 "preservatives (lead, arsenic, creosote) are no longer safe to use, and its engines are long "
                 "obsolete. Use it for how boats are built, rigged and handled, and follow today's rules and "
                 "safety advice. The machine-read text has the scanner's mistakes.")
NAV_NOTE = "Not for navigation by itself: always use current official charts and the current rules."

# ====================================================================== US government works

NOAA_RULES_PAGE = "https://nauticalcharts.noaa.gov/publications/coast-pilot/index.html"
PDFS = [
    K.us_pdf(GROUP, name="noaa_navigation_rules", title="Amalgamated International and US Inland Navigation Rules "
             "(NOAA Office of Coast Survey)", subject="Navigation Rules (the rules of the road)",
             publisher="NOAA Office of Coast Survey (US Department of Commerce)",
             pdf="https://nauticalcharts.noaa.gov/publications/coast-pilot/docs/NavigationRulesStandardSize.pdf",
             page=NOAA_RULES_PAGE, version="the edition on NOAA's Coast Pilot page when it was read",
             description="The rules of the road for every boat: the International Regulations for Preventing "
                         "Collisions at Sea (72 COLREGS) and the US Inland Navigation Rules (33 CFR 83) side by side, "
                         "with their record of changes: steering and sailing rules (lookout, safe speed, risk of "
                         "collision, narrow channels, crossing, overtaking and head-on situations, sailing vessels, "
                         "restricted visibility), lights and shapes, sound and light signals, and the verification of "
                         "compliance.",
             notice="A work of the US government (NOAA), public domain. NOAA says an up-to-date printed or "
                    "downloaded copy of its amalgamation may meet the requirement to carry the rules; this "
                    "converted copy is for reading and study, not that official copy. " + NAV_NOTE + " " +
                    BOAT_SAFETY),
]


def _mil(name, title, subject, publisher, archive, published, description, notice="", **more):
    """One military manual of the Internet Archive as a PDF entry, judged by the release rule (military=True, or
    distribution_a=True for a field manual, whose parts about explosives or demolition the builder leaves out)."""
    fields = dict(military=True)
    fields.update(more)
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description,
                    notice=("The release line before this says what its own front pages print about distribution. "
                            "Written for military crews: its rules and equipment are military ones and may be old. "
                            + (notice + " " if notice else "") + BOAT_SAFETY), **fields)


USCG_BOAT_FORCES = "US Coast Guard, Office of Boat Forces"
PDFS += [
    _mil("uscg_bch_navigation_piloting", "Boat Crew Handbook: Navigation and Piloting (US Coast Guard, 2021)",
         "Navigation and piloting for small boats", USCG_BOAT_FORCES, "boat-crew-handbook-navigation-and-piloting",
         "2021", "The Coast Guard's handbook for boat crews on finding the way: the aids to navigation (the US "
                 "system of buoys, beacons, lights and markers and its regional variations) and navigation "
                 "(nautical charts, integrated electronic navigation systems, finding the boat's position and "
                 "voyage planning), with a glossary and acronyms.",
         "Recreational boaters follow the Coast Guard's boating rules (outdoors:uscg_boating_safety).",
         work="a work of the US Coast Guard"),
    _mil("uscg_bch_rescue_survival", "Boat Crew Handbook: Rescue and Survival Procedures (US Coast Guard, 2021)",
         "Rescue and survival on the water", USCG_BOAT_FORCES, "boat-crew-handbook-rescue-and-survival-procedures",
         "2021", "The Coast Guard's handbook for boat crews on surviving in the water: survivability factors (what "
                 "keeps a person alive in the water, cold water included), survival equipment and pyrotechnics "
                 "(life jackets, survival suits and distress signals), and getting out of a capsized boat and into "
                 "a life raft, with a glossary.",
         work="a work of the US Coast Guard"),
    _mil("uscg_bch_first_aid", "Boat Crew Handbook: First Aid (US Coast Guard, 2017)", "First aid on boats",
         USCG_BOAT_FORCES, "boat-crew-handbook-first-aid", "2017",
         "The Coast Guard's first aid handbook for boat crews: responsibilities and handling and moving the "
         "injured, motion sickness, shock, resuscitation (artificial respiration and CPR) and the other "
         "emergencies its first aid chapter covers, with a glossary.",
         "General information, not medical advice: take a first aid and CPR course.",
         work="a work of the US Coast Guard"),
    _mil("army_fm_55_501_marine_crewman_1999", "Marine Crewman's Handbook (FM 55-501, 1999)", "Small boat seamanship",
         "Department of the Army (US Army)", "FM_55_501_M_C_H_1999", "1999",
         "The Army's handbook for the crews of its boats and landing craft, read whole: Army watercraft and "
         "shipboard life, vessel terms, small boat handling, charts and publications, dead reckoning and "
         "piloting, tides and currents, weather, communications, marine emergencies, fire fighting, marlinespike "
         "seamanship, deck maintenance, beaching and landing craft operations, safety, search and rescue, towing, "
         "rigging, ground tackle and damage control, with chart symbols and a glossary. Any part about explosives "
         "or demolition is left out.", distribution_a=True, military=False,
         work="a work of the US Army"),
    _mil("army_fm_55_130_small_boats_1944", "Small Boats and Harbor Craft (FM 55-130, 1944)", "Small boat handling",
         "War Department (US Army Transportation Corps)", "FM_55_130_S_B_H_C_1944", "1944",
         "The Army Transportation Corps' 1944 field manual for the crews of its small boats and harbour craft, "
         "read whole: the sea and the boatman, how harbour craft companies are organised, operating a boat, and "
         "keeping it shipshape, as they were done then. The machine-read text of this scan has some mistakes. "
         "Any part about explosives or demolition is left out.", distribution_a=True, military=False, work="a work of the US Army"),
    _mil("army_fm_55_502_watercraft_safety_1996", "Army Watercraft Safety (FM 55-502, 1996)", "Boating safety",
         "Department of the Army (US Army)", "FM_55_502_A_W_S_1996", "1996",
         "The Army's safety manual for its watercraft, read whole: accident reporting, risk management, the "
         "sailing order, lockout and tagout, confined spaces and hot work, distress signals and emergency "
         "beacons (EPIRBs), hypothermia protective clothing, personal flotation devices, ring buoys, life rafts "
         "and their release devices, safety harnesses, stretchers, first aid kits, fire fighting and its "
         "equipment, and dewatering pumps.", distribution_a=True, military=False,
         work="a work of the US Army"),
    _mil("army_fm_55_509_1_marine_electricity_1994", "Introduction to Marine Electricity (FM 55-509-1, 1994)",
         "Boat electrical systems", "Department of the Army (US Army)", "FM_55_509_1_I_M_E_1994", "1994",
         "The Army's textbook of electricity on boats, read whole: electrical safety, the fundamentals of "
         "electricity, direct and alternating current, batteries, circuit measurement, circuit protection and "
         "control, conductors and wiring, alternators, generators and motors, and electrical symbols.",
         "Electricity and batteries on boats can shock, burn and start fires: disconnect power before work.",
         distribution_a=True, military=False, work="a work of the US Army"),
]
# The engine, electrical and safety manuals carry the workshop note too.
for _p in PDFS:
    if _p["name"] in ("army_fm_55_509_1_marine_electricity_1994", "army_fm_55_502_watercraft_safety_1996"):
        _p["notice"] = f"{_p['notice']} {WORKSHOP_SAFETY}"

# ---------------------------------------------------------------------- web guides: tides, currents and weather

NOS = "https://oceanservice.noaa.gov/education/"
TIDE_PAGES = [NOS + "tutorial_tides/" + p for p in (
    "tides01_intro.html", "tides02_cause.html", "tides03_gravity.html", "tides04_angle.html",
    "tides05_lunarday.html", "tides06_variations.html", "tides07_cycles.html", "tides08_othereffects.html",
    "tides09_monitor.html", "tides10_oldmeasure.html", "tides11_newmeasure.html")]
CURRENT_PAGES = [NOS + "tutorial_currents/" + p for p in (
    "04currents1.html", "04currents2.html", "04currents3.html", "04currents4.html")]
GUIDES = [
    X.page_list_book(GROUP, "noaa_tides_currents", "Tides and water levels, and ocean currents (NOAA National Ocean "
                     "Service tutorials)", "Tides and currents", "NOAA National Ocean Service",
                     TIDE_PAGES + CURRENT_PAGES,
                     r"^https://oceanservice\.noaa\.gov/education/tutorial_(tides|currents)/[a-z0-9_]+\.html$",
                     "NOAA's two tutorials for understanding the water a boat moves on: what causes tides (the Moon's "
                     "and Sun's gravity, the lunar day, spring and neap tides, daily patterns and local effects) and "
                     "how they are measured, and ocean currents (the Coriolis effect, surface currents, boundary "
                     "currents and the Ekman spiral).",
                     "From NOAA's National Ocean Service: a US government work (public domain). For tide and "
                     "current predictions where you boat, use NOAA's current tables (tidesandcurrents.noaa.gov). " +
                     BOAT_SAFETY,
                     units=[(r"tutorial_tides", "Tides and water levels"), (r".", "Currents")],
                     content=(r'<div class="inner_content">', r'<div id="footer-top">')),
]
# The National Weather Service's marine pages (the same licence check as emergency_prep.py's weather books).
NWS = "https://www.weather.gov"
NWS_LICENCE = f"{NWS}/disclaimer"
NWS_TEXT = r"National Weather Service \(NWS\) Web pages are in the public domain"
NWS_MARINE = [f"{NWS}/marine/faq", f"{NWS}/marine/cwd", f"{NWS}/marine/pub"]
GUIDES.append(X.page_list_book(
    GROUP, "nws_marine_weather", "Marine weather for boaters: forecasts explained, warning flags and publications "
    "(National Weather Service)", "Marine weather", "National Weather Service (NOAA)", NWS_MARINE,
    r"^https://www\.weather\.gov/marine/(faq|cwd|pub)$",
    "The National Weather Service's marine pages: questions and answers about marine forecasts, warnings and "
    "advisories (small craft advisories, gale and storm warnings, how forecast zones and wave heights are given and "
    "where to hear them, NOAA Weather Radio included), the coastal warning display flags and lights, and the "
    "marine weather publications.",
    "From the National Weather Service (NOAA), whose web pages are in the public domain. Check the marine forecast "
    "before you go and listen to NOAA Weather Radio or VHF weather channels while you are out. " + BOAT_SAFETY,
    units=[(r"/cwd$", "Coastal warning flags"), (r"/pub$", "Publications"), (r".", "Marine forecasts explained")],
    content=(r'<div class="cms-content">', r'<div class="footer">'), licence_page=NWS_LICENCE,
    licence_text=NWS_TEXT))

# ---------------------------------------------------------------------- the federal boating regulations (33 CFR, 46 CFR)

CFR_FIELDS = dict(group=GROUP, country="United States", licence=K.US_GOV, licence_url=K.US_GOV_URL,
                  licence_page=K.GOVINFO_POLICY, licence_text=K.GOVINFO_TEXT,
                  publisher="Office of the Federal Register (Code of Federal Regulations, annual edition from "
                            "govinfo.gov)", split=r'<h3 class="cfr-section"', unit=r'<h2 class="cfr-subpart"')
LAWS = {
    "cfr_inland_navigation_rules": dict(
        CFR_FIELDS, name="boat_cfr_inland_navigation_rules", title="Inland Navigation Rules and their annexes (33 CFR "
        "parts 83 to 88)", subject="Navigation Rules (inland waters)",
        cfr=[dict(title=33, volume=1, part=p) for p in (83, 84, 85, 86, 87, 88)],
        source="https://www.ecfr.gov/current/title-33/chapter-I/subchapter-E",
        description="The US Inland Navigation Rules as law: the rules of the road on US inland waters (part 83), "
                    "and their annexes: positioning and technical details of lights and shapes (84), additional "
                    "signals for fishing vessels (85), technical details of sound signals (86), distress signals "
                    "(87) and pilot rules (88).",
        notice="A US government work (public domain), from govinfo.gov's annual edition of the Code of Federal "
               "Regulations; not an official version. " + NAV_NOTE + " " + BOAT_SAFETY),
    "cfr_recreational_boat_rules": dict(
        CFR_FIELDS, name="boat_cfr_recreational_boat_rules", title="Equipment and building standards for "
        "recreational boats (33 CFR parts 175 and 183, 46 CFR part 25)", subject="Boating law and required equipment",
        cfr=[dict(title=33, volume=2, part=175), dict(title=33, volume=2, part=183), dict(title=46, volume=1,
                                                                                         part=25)],
        source="https://www.ecfr.gov/current/title-33/chapter-I/subchapter-S",
        description="The federal rules on what a recreational boat must carry and how it must be built: life "
                    "jackets (personal flotation devices) and visual distress signals (33 CFR 175); the safety "
                    "standards for boat builders, such as capacity labels, flotation, ventilation, fuel and "
                    "electrical systems and start-in-gear protection (33 CFR 183); and fire extinguishers, "
                    "ventilation and backfire flame arrestors for uninspected vessels (46 CFR 25). States add their "
                    "own rules.",
        notice="A US government work (public domain), from govinfo.gov's annual edition of the Code of Federal "
               "Regulations; not an official version, and your state's boating laws apply too. " + BOAT_SAFETY),
}


def law_maker(entry):
    """(make, sign) of one set of federal regulations read whole from govinfo's newest annual edition
    (build_textbooks.lawdoc_book; the weekly sign is updates.law_sign: the address of the newest edition)."""

    def make(name, work, cache=None, left_out=None, limit=None):
        """The book of the regulations (None when govinfo's licence line or text cannot be read; said in
        left_out)."""
        import build_textbooks as B
        book = B.lawdoc_book(entry, cache, left_out)
        if book is not None and limit:
            book.pages = book.pages[:limit]
        return book

    def sign(name):
        """The weekly sign of change: govinfo's newest edition of each part."""
        import updates
        return updates.law_sign(entry)

    return make, sign


# ====================================================================== old public-domain books

def _old(name, title, subject, publisher, archive, year, description, workshop=False, country="United States"):
    """One old public-domain book (published before 1931) with the old-boat note, and the boating (and, for the
    building and engine books, the workshop) safety notes after the scan notice."""
    entry = X.old_book(GROUP, name, title, subject, publisher, archive, year, description,
                       OLD_BOAT_NOTE.format(year=year), country=country)
    entry["notice"] = f"{entry['notice']} {BOAT_SAFETY}" + (f" {WORKSHOP_SAFETY}" if workshop else "")
    return entry


PDFS += [
    _old("stephens_canoe_boat_building_1889", "Canoe and Boat Building: a complete manual for amateurs (W. P. "
         "Stephens, 1889 edition)", "Building canoes and small boats", "William Picard Stephens (Forest and Stream "
         "Publishing)", "canoeboatbuildin00stepiala", 1889,
         "The classic American manual for amateurs building canoes, rowing and sailing boats and hunting craft "
         "(the fourth edition, revised): plain directions for their construction, with fifty plates of working "
         "drawings described by their captions.", workshop=True),
    _old("frazar_practical_boat_sailing_1879", "Practical Boat-Sailing (Douglas Frazar, 1879)", "Sailing small boats",
         "Douglas Frazar (Lee and Shepard)", "practicalboatsai00fraziala", 1879,
         "A concise treatise on managing small boats and yachts under sail in all conditions: sails, helm and "
         "anchor, useful knots, anchoring in a gale, grounding and floating off, the helm and rudder, springing a "
         "leak, running free and what to do in other emergencies, with a short vocabulary of nautical terms."),
    _old("kenealy_boat_sailing_fair_foul_1895", "Boat Sailing in Fair Weather and Foul (A. J. Kenealy, 1895)",
         "Sailing small boats", "Ahmed John Kenealy (Outing Publishing)", "boatsailinginfai00kene", 1895,
         "A practical handbook of sailing small boats: rigs and sails, handling a boat in light and heavy weather, "
         "reefing, capsizes, anchoring, and the care of boat and gear."),
    _old("knight_small_boat_sailing_1902", "Small-Boat Sailing (E. F. Knight, 1902)", "Sailing small boats",
         "Edward Frederick Knight (E. P. Dutton)", "smallboatsailing01knig", 1902,
         "An explanation of the management of small yachts, half-decked and open sailing boats: their rigs and "
         "sails, sailing on and off the wind, reefing, heavy weather, anchoring and mooring, and cruising and "
         "navigating in small craft.", country="United Kingdom"),
    _old("chapman_practical_motor_boat_handling_1917", "Practical Motor Boat Handling, Seamanship and Piloting "
         "(Charles F. Chapman, 1917)", "Motorboat handling and piloting", "Charles Frederic Chapman (Motor Boating)",
         "practicalmotorbo00chap", 1917,
         "The first edition of the handbook that became Chapman Piloting: the navigation laws and the "
         "International and Inland Rules of its day, buoys, government navigation lights, nautical instruments "
         "and publications, flags and colours, boat equipment, signalling and etiquette, with boat handling, "
         "seamanship and piloting. (The modern editions are copyright: link-only.)"),
    _old("slauson_motor_boat_1911", "The Motor Boat: its Selection, Care and Use (H. W. Slauson, 1911)",
         "Motorboat care", "Harold Whiting Slauson (Outing Publishing)", "motorboatitssele00slau", 1911,
         "A small handbook of choosing, running and looking after a motor boat: the kinds and uses of motor "
         "boats, marine power and what to do when the motor balks, speeding up a boat, accessories, covers, "
         "canopies and tops, camping and cruising, and the boathouse.", workshop=True),
    _old("miller_boys_book_canoeing_sailing_1917", "The Boys' Book of Canoeing and Sailing (Warren H. Miller, 1917)",
         "Canoeing and small boat sailing", "Warren Hastings Miller (George H. Doran)", "boysbookofcanoei00mill",
         1917, "Building and rigging sailing canoes and small sailboats, canoe handling and paddling, sailing, and "
               "motor boat management, for young boaters.", workshop=True),
    _old("davis_harpers_boating_book_1912", "Harper's Boating Book for Boys (Charles G. Davis, 1912)",
         "Motor boating, sailing, canoeing and rowing", "Charles Gerard Davis, editor (Harper and Brothers)",
         "harpersboatingbo01davi", 1912,
         "A guide to motor boating, sailing, canoeing and rowing: choosing and building small boats, rigging, "
         "handling under oars, paddle, sail and power, and simple seamanship.", workshop=True),
    _old("stevens_practical_rowing_1906", "Practical Rowing with Scull and Sweep (Arthur W. Stevens and Edward "
         "Darling, 1906)", "Rowing", "Arthur Wesselhoeft Stevens and Edward Darling (Little, Brown)",
         "practicalrowingw00stev", 1906,
         "How to row well: the stroke with sculls (two oars) and with a sweep (one oar), boats and oars, rigging a "
         "boat, coaching and training."),
    _old("admiralty_manual_of_navigation_1914", "Admiralty Manual of Navigation, 1914 (UK)", "Navigation",
         "Admiralty (Great Britain), His Majesty's Stationery Office", "admiraltymanualo00grea", 1915,
         "The Royal Navy's manual of navigation of 1914 (printed 1915), written for junior officers: charts and "
         "chart work, the compass, pilotage, tides, and finding the ship's position at sea. Also public domain in "
         "the UK (Crown copyright ended 50 years after publication).", country="United Kingdom"),
]

# ====================================================================== the index

SECTIONS = [
    ("Boat handling", "Rowing, paddling, motorboats, sailing dinghies and small keelboats: getting under way, "
     "docking, anchoring, towing, capsize recovery, heavy weather and man overboard.", [
        ("key", "boat:chapman_practical_motor_boat_handling_1917", "Motor boat handling, docking and anchoring "
                                                                   "(Chapman, 1917)"),
        ("key", "boat:army_fm_55_130_small_boats_1944", "Small boats and harbour craft (FM 55-130, 1944)"),
        ("key", "boat:army_fm_55_501_marine_crewman_1999", "Deck seamanship, anchoring, mooring and towing (FM "
                                                            "55-501)"),
        ("key", "kmil:uscg_bch_seamanship_fundamentals", "Boat handling: to and from a dock, alongside, in heavy "
                                                          "weather (Coast Guard)"),
        ("key", "boat:frazar_practical_boat_sailing_1879", "Sailing small boats (Frazar, 1879)"),
        ("key", "boat:kenealy_boat_sailing_fair_foul_1895", "Sailing in fair weather and foul, reefing and capsizes "
                                                             "(Kenealy, 1895)"),
        ("key", "boat:knight_small_boat_sailing_1902", "Small-boat sailing (Knight, 1902)"),
        ("key", "boat:miller_boys_book_canoeing_sailing_1917", "Canoe handling and small boat sailing (Miller, 1917)"),
        ("key", "boat:davis_harpers_boating_book_1912", "Motor boating, sailing, canoeing and rowing (1912)"),
        ("key", "boat:stevens_practical_rowing_1906", "Rowing with sculls and sweeps (1906)"),
        ("key", "boat:uscg_bch_rescue_survival", "Man overboard, person in the water and towing (Coast Guard)"),
        ("word", "knots-military", "The Admiralty Manuals of Seamanship (boats under oars, sail and power) and the "
                                   "Navy and Coast Guard seamanship manuals (request word)"),
        ("link", "Chapman Piloting and Seamanship", "https://www.chapmanpiloting.com/",
         "copyright (Hearst); borrow it from a library or buy it"),
        ("link", "US Sailing, American Sailing Association and American Canoe Association courses",
         "https://www.ussailing.org/", "copyright course books; their courses teach hands-on skills")]),
    ("Navigation rules, buoyage and charts", "The rules of the road, lights and sound signals, buoys and markers, "
     "and reading a nautical chart.", [
        ("key", "boat:noaa_navigation_rules", "The International and Inland Navigation Rules side by side (NOAA)"),
        ("key", "boat:cfr_inland_navigation_rules", "The Inland Navigation Rules and annexes as law (33 CFR 83 to "
                                                    "88)"),
        ("key", "outdoors:uscg_boaters_guide_federal_requirements", "Buoys, markers and the navigation rules in "
                                                                    "brief (Coast Guard Boater's Guide)"),
        ("key", "pdf:noaa_us_chart_no_1", "U.S. Chart No. 1: every chart symbol and abbreviation"),
        ("key", "boat:uscg_bch_navigation_piloting", "Charts, compass, dead reckoning, piloting and GPS (Coast "
                                                     "Guard)"),
        ("key", "boat:admiralty_manual_of_navigation_1914", "Chart work, pilotage and the compass (Admiralty, 1914)"),
        ("key", "pdf:bowditch_american_practical_navigator_1914", "The American Practical Navigator (Bowditch, 1914)"),
        ("key", "pdf:navy_quartermaster_1_c", "Charts, piloting, tides and weather (Navy Quartermaster)"),
        ("pack", "commons_water_trail_markers", "Buoys, lateral and cardinal marks, daymarks and leading lights"),
        ("manuals", "marine_electronics", "Chartplotters, GPS, depth sounders and marine radios (manuals)"),
        ("link", "US Coast Pilot (NOAA)", "https://nauticalcharts.noaa.gov/publications/coast-pilot/index.html",
         "free from NOAA, updated every week: download the current volume yourself"),
        ("link", "US Aids to Navigation System (Coast Guard Navigation Center)", "https://www.navcen.uscg.gov/",
         "public domain, but the site refuses programs")]),
    ("Tides, currents and weather", "Why the water rises and falls, how currents run, and marine forecasts and "
     "warnings.", [
        ("key", "boat:noaa_tides_currents", "Tides and currents explained (NOAA tutorials)"),
        ("key", "boat:nws_marine_weather", "Marine forecasts, small craft advisories and warning flags (NWS)"),
        ("key", "science:noaa_ocean_facts", "Ocean facts: waves, rip currents and tides (NOAA)"),
        ("key", "prep:nws_safety", "Weather safety: thunderstorms, lightning, fog, rip currents (NWS)"),
        ("link", "NOAA tide and current predictions", "https://tidesandcurrents.noaa.gov/",
         "live predictions: look them up for your waters before you go")]),
    ("Safety, life jackets, float plans and cold water", "Life jackets and required equipment, float plans, "
     "boating under the influence, carbon monoxide, and cold-water immersion and hypothermia.", [
        ("key", "outdoors:uscg_boating_safety", "Life jackets, engine cut-off switches, carbon monoxide, boating "
                                                 "under the influence and float plans (Coast Guard)"),
        ("key", "outdoors:uscg_boaters_guide_federal_requirements", "Required equipment: life jackets, fire "
                                                                    "extinguishers, signals and lights"),
        ("key", "boat:cfr_recreational_boat_rules", "The federal equipment and building rules (33 CFR 175 and 183, "
                                                    "46 CFR 25)"),
        ("key", "boat:army_fm_55_502_watercraft_safety_1996", "Watercraft safety (FM 55-502)"),
        ("key", "boat:uscg_bch_rescue_survival", "Survival equipment and cold-water survival (Coast Guard)"),
        ("key", "boat:uscg_bch_first_aid", "First aid on boats, hypothermia and near drowning (Coast Guard)"),
        ("key", "wild:army_tb_med_508_cold", "Cold injuries and hypothermia (Army TB MED 508)"),
        ("key", "wild:usfs_backcountry_safety", "Hypothermia and backcountry safety (Forest Service)"),
        ("word", "wilderness-first-aid", "Wilderness first aid and backcountry safety (request word)"),
        ("pack", "commons_boating_paddling", "Life jackets, throw bags and distress signals"),
        ("manuals", "outdoors", "Life jacket, kayak and canoe makers' manuals, as links"),
        ("link", "National Center for Cold Water Safety", "https://www.coldwatersafety.org/",
         "copyright; open it in a browser"),
        ("link", "RNLI water safety", "https://rnli.org/safety", "copyright of the RNLI (a charity); link-only")]),
    ("Building and repairing boats", "Wooden boats (plank-on-frame, lapstrake, plywood), canoes and kayaks, "
     "fibreglass and epoxy, caulking, painting and varnishing.", [
        ("key", "boat:stephens_canoe_boat_building_1889", "Canoe and Boat Building (Stephens): lapstrake and carvel "
                                                           "planking, framing and fittings"),
        ("key", "boat:miller_boys_book_canoeing_sailing_1917", "Building and rigging sailing canoes (Miller, 1917)"),
        ("key", "build:fpl_wood_handbook", "Wood as a material: species, moisture, glues and finishes (Forest "
                                           "Products Laboratory)"),
        ("key", "boat:cfr_recreational_boat_rules", "Building standards for boats sold in the US (33 CFR 183)"),
        ("pack", "commons_small_boats", "Boat types, parts and fittings, and wooden boats being built"),
        ("link", "WoodenBoat magazine and books", "https://www.woodenboat.com/", "copyright; link-only"),
        ("link", "Howard Chapelle's boatbuilding books", "https://archive.org/search?query=chapelle+boatbuilding",
         "still in copyright unless proven not renewed; borrow them from a library"),
        ("link", "Epoxy makers' boat repair manuals (West System, System Three, MAS)",
         "https://www.westsystem.com/", "the makers' copyright; read their safety data sheets")]),
    ("Maintenance: trailers, engines and winterising", "Boat trailers, outboard and small engines, electrical "
     "systems, and laying up for winter.", [
        ("key", "boat:slauson_motor_boat_1911", "Running and looking after a motor boat (1911)"),
        ("key", "boat:army_fm_55_509_1_marine_electricity_1994", "Batteries, wiring and electricity on boats (FM "
                                                                  "55-509-1)"),
        ("key", "rvs:army_tm_m1101_trailer", "Trailer maintenance: bearings, brakes, lights and tyres (Army trailer "
                                             "manual)"),
        ("key", "rvs:index", "RVs, trailers and towing: a guide to the library"),
        ("manuals", "powersports", "Outboard motor and personal watercraft owner's manuals"),
        ("manuals", "small_engines", "Small engine owner's and repair manuals"),
        ("manuals", "motorcycles_rvs", "Trailer hitch, brake controller and trailer makers' manuals, as links"),
        ("manuals", "small_boats", "Boat, sailboat, trailer and marine engine makers' manuals, as links"),
        ("pack", "commons_boating_paddling", "Boat trailers and boat ramps"),
        ("link", "Outboard makers' owner's manuals (Mercury, Yamaha, Honda, Suzuki, Tohatsu)",
         "https://www.mercurymarine.com/", "the makers' copyright; link-only")]),
    ("Knots and rigging for small boats", "The knots, splices and line handling a boater uses, and blocks, tackles "
     "and rigging.", [
        ("key", "knot:index", "Knots and outdoor skills: a guide to the library"),
        ("key", "kmil:uscg_bch_seamanship_fundamentals", "Line, knots, splices and deck fittings (Coast Guard)"),
        ("key", "knot:verrill_knots_splices_1912", "Knots, splices and rope work, knots for boating (Verrill)"),
        ("key", "knot:aldridge_knots_marlinespike_1918", "Marlinespike seamanship (Aldridge, 1918)"),
        ("key", "pdf:knight_modern_seamanship_1921", "Modern Seamanship (Knight, 1921): rope, blocks and rigging"),
        ("word", "knots-outdoor", "The knot and rope books (request word)"),
        ("pack", "commons_knots", "Knots by name, for the picture describer")]),
    ("Boat types by name", "Rowboats, dinghies, dories, skiffs, punts, canoes and kayaks, sailing dinghies and "
     "keelboats, catamarans, motorboats, pontoon and jon boats, and inflatable boats.", [
        ("key", "boat:davis_harpers_boating_book_1912", "Choosing a small boat (1912)"),
        ("key", "boat:army_fm_55_130_small_boats_1944", "Types of small boats (FM 55-130)"),
        ("pack", "commons_small_boats", "Boat types by name, and their parts and fittings (cleats, rowlocks, "
                                        "fairleads, blocks, keels, daggerboards)"),
        ("pack", "commons_boating_paddling", "Kayaks, canoes, stand-up paddleboards and paddles")]),
]
INDEX = X.index_maker("boat", GROUP, "Small boats: a guide to the library", "Small boats",
                      "A guide to the library on small boats: handling, the navigation rules and charts, tides and "
                      "weather, safety and cold water, building and repair, maintenance, knots and rigging, and boat "
                      "types.", SECTIONS)
MAKERS = {"index": INDEX}
MAKERS.update({name: law_maker(entry) for name, entry in LAWS.items()})

COLLECTION = K.Collection("boat", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"small-boats": lambda: ["boat:index"] + [f"boat:{n}" for n in LAWS] +
                                 [f"boat:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "boats_us_government": "nauticalcharts.noaa.gov, oceanservice.noaa.gov and govinfo.gov: works of the US government "
                           "(17 U.S.C. 105, checked on govinfo.gov's policies page at every build); robots.txt allows "
                           "the pages (nauticalcharts.noaa.gov has none: 404), no AI rules (checked 2026-11-22).",
    "boats_nws": "www.weather.gov/disclaimer (checked at every build): \"National Weather Service (NWS) Web pages are "
                 "in the public domain\"; www.weather.gov has no robots.txt (no rules), checked 2026-11-22.",
    "boats_military": "Internet Archive copies of US Coast Guard and Army manuals: works of the US government (17 "
                      "U.S.C. 105), judged at every build by the release rule for military publications "
                      "(military_release.py); archive.org's robots.txt allows the files; no AI rules (checked "
                      "2026-11-22).",
    "boats_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so a "
                       "later reprint is refused).",
    "boats_index": "The index (boat:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Chapman Piloting and Seamanship (1922 and later editions) and other modern boating books (Royce, Annapolis Book "
     "of Seamanship, Time-Life Library of Boating)", "Copyright (Chapman's editions are renewed and still sold by "
     "Hearst); the Internet Archive's copies are lending-library scans. The 1917 first edition is built "
     "(boat:chapman_practical_motor_boat_handling_1917). Link-only. Index: https://www.chapmanpiloting.com/"),
    ("US Coast Pilot (NOAA, volumes 1 to 10)", "A US government work, but it is updated every week, each volume is "
     "hundreds of pages, it is downloaded through an interactive map, and NOAA warns that incomplete or reworked "
     "copies may not meet the Coast Guard's carriage rules: link-only, for the owner to download the current volume "
     "from NOAA himself. Index: https://nauticalcharts.noaa.gov/publications/coast-pilot/index.html"),
    ("US Coast Guard Navigation Rules and Regulations Handbook (navcen.uscg.gov)", "navcen.uscg.gov refuses programs "
     "(403); NOAA's amalgamated International and Inland Rules (boat:noaa_navigation_rules) and 33 CFR 83 to 88 "
     "(boat:cfr_inland_navigation_rules) are built instead. The Internet Archive's 1982 microfiche copy "
     "(micro_IA41152601_0103) is out of date. Index: https://www.navcen.uscg.gov/navigation-rules-amalgamated"),
    ("US Coast Guard Boat Crew Handbook: Boat Operations and the other volumes of BCH 16114", "No downloadable copy "
     "of the boat operations volume was found on the Internet Archive (searched 2026-11-22), and uscg.mil refuses "
     "programs (403). Seamanship Fundamentals (kmil:), Navigation and Piloting, Rescue and Survival Procedures and "
     "First Aid are built. Index: https://archive.org/search?query=%22boat+crew+handbook%22"),
    ("US Navy boat handling and Boatswain's Mate rate manuals after 1944; Navy \"Small Boats\" NAVPERS manuals", "No "
     "downloadable copy with a text layer was found on the Internet Archive (searched 2026-11-22); the Army's "
     "watercraft manuals are built instead. Index: https://archive.org/search?query=navy+boat+handling"),
    ("RNLI, US Sailing, American Sailing Association, American Canoe Association, America's Boating Club (US Power "
     "Squadrons), BoatUS Foundation, the National Center for Cold Water Safety and WoodenBoat", "Copyright of each "
     "organisation; link-only (listed in boat:index). Index: https://rnli.org/safety"),
    ("Outboard, inboard and boat makers' manuals (Mercury, Yamaha, Honda, Suzuki, Tohatsu, Evinrude, Volvo Penta; "
     "Boston Whaler, Bayliner, Sea Ray, Grady-White, Hobie, Laser)", "The makers' copyright; links in the manual "
     "collection small_boats (and the outboard owner's manuals on the Internet Archive in powersports). Index: "
     "https://www.mercurymarine.com/"),
    ("Howard I. Chapelle's Boatbuilding (1941) and American Small Sailing Craft (1951)", "Their copyright renewals "
     "were not checked as absent (the Stanford Copyright Renewal Database and the Online Books Page were not "
     "searched for them in this build), so they are treated as copyright: link-only. Index: "
     "https://onlinebooks.library.upenn.edu/webbin/book/search?author=chapelle"),
    ("Transport Canada's Safe Boating Guide (TP 511)", "Crown copyright under the terms of the canada.ca web pages "
     "(non-commercial reproduction only: personal use at most; open.canada.ca, where some Transport Canada "
     "publications are under the Open Government Licence - Canada, was not searched for it in this build), and its pages answered \"404\" at two addresses "
     "(2026-11-22). Link-only. Index: https://tc.canada.ca/en/marine-transportation"),
    ("Maritime New Zealand boating guides; Australian state boating handbooks (NSW, Queensland, Victoria, Western "
     "Australia)", "maritimenz.govt.nz refuses programs (403) so its CC BY statement could not be checked; the "
     "Australian state handbooks were not checked for CC BY licences in this build. Link-only. Index: "
     "https://www.maritimenz.govt.nz/recreational/"),
    ("UK Maritime and Coastguard Agency and Canal and River Trust boating guides (e.g. The Boater's Handbook, "
     "British Waterways, 2006)", "The Boater's Handbook on the Internet Archive (the-boaters-handbook-basic-boat-"
     "handling-and-safety-2006) is a British Waterways (now Canal and River Trust) publication with no open licence "
     "stated; MCA guidance on gov.uk is under the Open Government Licence and could be added. Link-only. Index: "
     "https://canalrivertrust.org.uk/"),
    ("Admiralty Navigation Manual (1938, reprinted 1943) and Admiralty Manual of Navigation (1955 to 1973)", "The 1938 "
     "volumes (Indian Digital Library scans and admiraltynavigationmanualvol1) are public domain in the UK and, as "
     "their Crown copyright ended before 1996, in the US; not added yet (poor scans). The 1970 and 1973 volumes "
     "(admiralty-manual-navigation-v-1, admiralty-manual-of-navigation-volume-2) are downloadable but, like the "
     "Admiralty seamanship manuals, their US copyright may have been restored (URAA, 1996); the owner's decision of "
     "22 November 2026 named seamanship, boat and rigging manuals, so they are link-only until he decides. The 1914 "
     "manual is built. Index: https://archive.org/details/admiralty-publications"),
    ("Old boat books whose copies cannot be used", "Daniel Beard's Boat-Building and Boating (1911): the Internet "
     "Archive's copy is a 1931 printing, so the builder's year check refuses it; T. H. Russell's Motor Boats: "
     "Construction and Operation (1910) and Linton Hope's Small Yacht Construction and Rigging (1903): scans without "
     "a text layer, and so are the Internet Archive's copies of Edson Schock's How to Build a Rowboat (1904) and "
     "Charles Mower's How to Build a Motor Launch (The Rudder, 1901), checked by a trial build on 2026-11-22; Frank "
     "Sterling's Small Boat Navigation (1917): its record shows a 1944 printing. Index: "
     "https://archive.org/details/boatbuildingboat00bear"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
