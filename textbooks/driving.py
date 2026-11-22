"""Driving and road rules for the reference library, in the group "Reference, driving and road rules" (the owner's
request of 2026-11-22). Keys: driving (every book), driving-us and driving-canada (one country's books), drive:<name>.

What this module builds, in plain words:
  - drive:index_us, a guide to the library for US drivers, passengers and pedestrians (the toolkit's own facts and
    links, CC0): every state's and DC's driver licensing agency, where its driver handbook, commercial driver (CDL)
    manual and motorcycle manual are published, and the books, manual collections and picture packs on driving;
  - drive:index_canada, the same for the provinces and territories;
  - IN FULL: the Federal Highway Administration's Manual on Uniform Traffic Control Devices (MUTCD, 11th edition, the
    national standard for every sign, signal and road marking; a US government work); CDC's road safety pages (drunk
    and drugged driving, distracted driving, teen and older drivers, child passenger safety, pedestrian safety) kept
    whole under CDC's terms; and the US Army's Manual for the Wheeled Vehicle Operator (TC 21-305-20, 2016: driving
    defensively, at night and in bad weather, backing, towing trailers and what to do after an accident), read from
    the Internet Archive under the release rule for military publications.
  Every book carries DRIVE_SAFETY in its notice (seat belts; never drive impaired or distracted; school buses;
  pedestrians and white canes; what to do after a crash; the state's own handbook is the law).

Already in the library and not repeated: Alberta's Driver's Guide (pdf:alberta_drivers_guide, under the Open
Government Licence - Alberta), the US Access Board's and FTA's transport and paratransit guides (transport), car care
books (car-care), NHTSA vehicle recalls (rcl:), the field manuals (fieldmanuals) and the blind and low-vision books on
orientation, mobility, transit and paratransit (the vision helper's collection, request word vision-living).

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): the states' and provinces' own handbooks (US
state works are not covered by the federal public-domain rule, 17 U.S.C. 105, and each state and province sets its
own terms; most print a copyright notice or no licence), the AAMVA model CDL manual, NHTSA's and FMCSA's pages (both
refuse programs, and no Internet Archive copy was found), defensive driving courses, and rideshare companies' help.

Licences: the MUTCD and the Army manual are works of the US government (17 U.S.C. 105, checked on govinfo.gov's
policies page at every build); CDC's statement is checked at every build and its conditions met in the notice.

Run from the repository's folder:
  python3 textbooks/driving.py drive:mutcd_11th --out build/textbooks --limit 5
  python3 textbooks/driving.py --list driving
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "driving"
GROUPS = {GROUP: "Reference, driving and road rules"}

# The safety notice every book carries (the picture packs say the same things in packs/driving_packs.py).
DRIVE_SAFETY = ("Safety: everyone buckles up on every trip; never drive after drinking or using drugs, or when "
                "drowsy, and put the phone away. Stop for a school bus with red lights flashing and its stop arm out. "
                "Yield to pedestrians, and stop for anyone with a white cane or a guide dog. After a crash: stop, "
                "check for injuries, call 911, move to a safe place if you can, and exchange information. Your state's "
                "or province's own driver handbook has the law where you live.")

# ====================================================================== the indexes of state and provincial handbooks

# (state, the agency that licenses drivers, its address): checked to answer on 2026-11-22 (some answer programs
# "403" but open in a browser). Each agency publishes its driver handbook, CDL manual and motorcycle manual there.
US_AGENCIES = [
    ("Alabama", "Alabama Law Enforcement Agency, Driver License Division", "https://www.alea.gov/dps/driver-license"),
    ("Alaska", "Alaska Division of Motor Vehicles", "https://dmv.alaska.gov/"),
    ("Arizona", "Arizona Department of Transportation, Motor Vehicle Division", "https://azdot.gov/mvd"),
    ("Arkansas", "Arkansas Department of Public Safety (State Police driver testing)", "https://dps.arkansas.gov/"),
    ("California", "California Department of Motor Vehicles", "https://www.dmv.ca.gov/portal/driver-handbooks/"),
    ("Colorado", "Colorado Division of Motor Vehicles", "https://dmv.colorado.gov/"),
    ("Connecticut", "Connecticut Department of Motor Vehicles", "https://portal.ct.gov/dmv"),
    ("Delaware", "Delaware Division of Motor Vehicles", "https://dmv.de.gov/"),
    ("District of Columbia", "DC Department of Motor Vehicles", "https://dmv.dc.gov/"),
    ("Florida", "Florida Department of Highway Safety and Motor Vehicles",
     "https://www.flhsmv.gov/driver-licenses-id-cards/"),
    ("Georgia", "Georgia Department of Driver Services", "https://dds.georgia.gov/"),
    ("Hawaii", "Hawaii Department of Transportation, Highways (driver licensing)",
     "https://hidot.hawaii.gov/highways/"),
    ("Idaho", "Idaho Transportation Department, Division of Motor Vehicles", "https://itd.idaho.gov/dmv/"),
    ("Illinois", "Illinois Secretary of State, Driver Services", "https://www.ilsos.gov/departments/drivers/home.html"),
    ("Indiana", "Indiana Bureau of Motor Vehicles", "https://www.in.gov/bmv/"),
    ("Iowa", "Iowa Department of Transportation, Motor Vehicle Division", "https://iowadot.gov/dmv-services"),
    ("Kansas", "Kansas Department of Revenue, Division of Vehicles", "https://www.ksrevenue.gov/dovindex.html"),
    ("Kentucky", "Kentucky Transportation Cabinet, Driver Licensing", "https://drive.ky.gov/Pages/index.aspx"),
    ("Louisiana", "Louisiana Office of Motor Vehicles", "https://expresslane.la.gov/"),
    ("Maine", "Maine Bureau of Motor Vehicles", "https://www.maine.gov/sos/bmv/"),
    ("Maryland", "Maryland Motor Vehicle Administration", "https://mva.maryland.gov/"),
    ("Massachusetts", "Massachusetts Registry of Motor Vehicles",
     "https://www.mass.gov/orgs/massachusetts-registry-of-motor-vehicles"),
    ("Michigan", "Michigan Secretary of State", "https://www.michigan.gov/sos"),
    ("Minnesota", "Minnesota Driver and Vehicle Services", "https://dps.mn.gov/divisions/dvs"),
    ("Mississippi", "Mississippi Department of Public Safety, Driver Service Bureau",
     "https://www.driverservicebureau.dps.ms.gov/"),
    ("Missouri", "Missouri Department of Revenue, Driver License Bureau", "https://dor.mo.gov/driver-license/"),
    ("Montana", "Montana Motor Vehicle Division", "https://mvdmt.gov/"),
    ("Nebraska", "Nebraska Department of Motor Vehicles", "https://dmv.nebraska.gov/"),
    ("Nevada", "Nevada Department of Motor Vehicles", "https://dmv.nv.gov/"),
    ("New Hampshire", "New Hampshire Division of Motor Vehicles", "https://www.dmv.nh.gov/"),
    ("New Jersey", "New Jersey Motor Vehicle Commission", "https://www.nj.gov/mvc/"),
    ("New Mexico", "New Mexico Motor Vehicle Division", "https://www.mvd.newmexico.gov/"),
    ("New York", "New York State Department of Motor Vehicles", "https://dmv.ny.gov/"),
    ("North Carolina", "North Carolina Division of Motor Vehicles", "https://www.ncdot.gov/dmv/Pages/default.aspx"),
    ("North Dakota", "North Dakota Department of Transportation, Driver License", "https://www.dot.nd.gov/"),
    ("Ohio", "Ohio Bureau of Motor Vehicles", "https://www.bmv.ohio.gov/"),
    ("Oklahoma", "Service Oklahoma", "https://oklahoma.gov/service.html"),
    ("Oregon", "Oregon Driver and Motor Vehicle Services", "https://www.oregon.gov/odot/dmv/Pages/index.aspx"),
    ("Pennsylvania", "PennDOT Driver and Vehicle Services", "https://www.pa.gov/agencies/dmv"),
    ("Rhode Island", "Rhode Island Division of Motor Vehicles", "https://dmv.ri.gov/"),
    ("South Carolina", "South Carolina Department of Motor Vehicles", "https://dmv.sc.gov/"),
    ("South Dakota", "South Dakota Department of Public Safety, Driver Licensing",
     "https://dps.sd.gov/driver-licensing"),
    ("Tennessee", "Tennessee Department of Safety and Homeland Security, Driver Services",
     "https://www.tn.gov/safety/driver-services.html"),
    ("Texas", "Texas Department of Public Safety, Driver License Division",
     "https://www.dps.texas.gov/section/driver-license"),
    ("Utah", "Utah Driver License Division", "https://dld.utah.gov/"),
    ("Vermont", "Vermont Department of Motor Vehicles", "https://dmv.vermont.gov/"),
    ("Virginia", "Virginia Department of Motor Vehicles", "https://www.dmv.virginia.gov/"),
    ("Washington", "Washington State Department of Licensing", "https://dol.wa.gov/"),
    ("West Virginia", "West Virginia Division of Motor Vehicles", "https://dmv.wv.gov/"),
    ("Wisconsin", "Wisconsin Department of Transportation, Division of Motor Vehicles",
     "https://wisconsindot.gov/Pages/home.aspx"),
    ("Wyoming", "Wyoming Department of Transportation, Driver Services", "https://www.dot.state.wy.us/"),
]
# The provinces and territories (Alberta's guide is built: pdf:alberta_drivers_guide).
CA_AGENCIES = [
    ("Alberta", "Government of Alberta (Alberta Transportation and Economic Corridors)",
     "https://open.alberta.ca/publications/drivers-guide"),
    ("British Columbia", "ICBC (Insurance Corporation of British Columbia)", "https://www.icbc.com/driver-licensing"),
    ("Manitoba", "Manitoba Public Insurance", "https://www.mpi.mb.ca/"),
    ("New Brunswick", "Service New Brunswick and the Department of Public Safety",
     "https://www.gnb.ca/en/org/justice-public-safety.html"),
    ("Newfoundland and Labrador", "Motor Registration Division, Digital Government and Service NL",
     "https://www.gov.nl.ca/gs/"),
    ("Northwest Territories", "Department of Infrastructure, Driver and Vehicle Licensing",
     "https://www.inf.gov.nt.ca/en/services/driver-and-vehicle-licensing"),
    ("Nova Scotia", "Nova Scotia Registry of Motor Vehicles", "https://novascotia.ca/driving-and-road-safety/"),
    ("Nunavut", "Department of Economic Development and Transportation, Motor Vehicles",
     "https://www.gov.nu.ca/en/driving-and-vehicles"),
    ("Ontario", "Ontario Ministry of Transportation", "https://www.ontario.ca/document/official-mto-drivers-handbook"),
    ("Prince Edward Island", "PEI Highway Safety", "https://www.princeedwardisland.ca/en/topic/highway-safety"),
    ("Quebec", "Société de l'assurance automobile du Québec (SAAQ)", "https://saaq.gouv.qc.ca/en/"),
    ("Saskatchewan", "SGI (Saskatchewan Government Insurance)", "https://sgi.sk.ca/"),
    ("Yukon", "Government of Yukon, Driver and Vehicle Services", "https://yukon.ca/en/driving-and-transportation"),
]

US_HANDBOOK_WHY = "its driver handbook, CDL manual and motorcycle manual (the state's own terms; link only)"
US_INTRO = ("Every state's driver handbook is the official guide to its traffic laws, road signs, licences and the "
            "knowledge test; each state also publishes a commercial driver's licence (CDL) manual, based on the "
            "AAMVA model manual, and a motorcycle operator manual. They are links only: US state works are not "
            "covered by the federal public-domain rule (17 U.S.C. 105), each state sets its own terms, and most "
            "handbooks print a copyright notice or no licence. Open the agency's page in a browser or fetch the "
            "handbook with Program Downloader; every handbook is also offered in large print or audio by many "
            "states (ask the agency).")
CA_INTRO = ("Each province and territory publishes its own driver's handbook (in Quebec, the SAAQ's guides, mostly "
            "in French). They are Crown copyright with each government's own terms, so they are links only, except "
            "Alberta's Driver's Guide, which Alberta publishes under the Open Government Licence - Alberta and the "
            "library builds in full. Canadian rules differ from US rules: speeds are in kilometres per hour, and "
            "licences, signs and some right-of-way rules are different.")

US_SECTIONS = [
    ("State driver handbooks, Alabama to Missouri", US_INTRO,
     [("link", f"{s}: {who}", url, US_HANDBOOK_WHY) for s, who, url in US_AGENCIES[:26]]),
    ("State driver handbooks, Montana to Wyoming", US_INTRO,
     [("link", f"{s}: {who}", url, US_HANDBOOK_WHY) for s, who, url in US_AGENCIES[26:]]),
    ("Road signs, signals and markings", "What every sign, signal and marking means, nationwide.", [
        ("key", "drive:mutcd_11th", "The MUTCD, 11th edition: every traffic sign, signal and pavement marking, in "
                                    "full (Federal Highway Administration)"),
        ("pack", "us_road_signs", "US road signs, for the picture describer"),
        ("pack", "ca_road_signs", "Canadian road signs"),
        ("pack", "commons_driving", "Car controls, learner signs, road markings, roundabouts, school buses, "
                                    "crossing guards and paratransit"),
        ("pack", "open_images_driving", "Car controls, lanes, road shoulders, traffic circles and parking")]),
    ("Safe driving", "Seat belts, impaired and distracted driving, teens and older drivers, children in cars, and "
                     "defensive driving.", [
        ("key", "drive:cdc_road_safety", "CDC's road safety pages, kept whole"),
        ("key", "drive:army_tc_21_305_20", "The Army's Manual for the Wheeled Vehicle Operator: defensive driving, "
                                           "night and bad weather, backing, towing, after an accident"),
        ("key", "pdf:alberta_drivers_guide", "Alberta's Driver's Guide (a good plain-language guide to the rules of "
                                             "the road; Canadian)"),
        ("manuals", "driving_handbooks", "Driver, CDL and motorcycle handbooks and the safety guidance, as links"),
        ("link", "NHTSA road safety (drunk, drugged, distracted and drowsy driving, seat belts, child seats, "
                 "pedestrians, older drivers)", "https://www.nhtsa.gov/road-safety",
         "public domain, but nhtsa.gov refuses programs; open it in a browser")]),
    ("Blind and low-vision pedestrians and passengers", "Crossing streets safely, riding as a passenger, rideshare "
                                                        "and paratransit.", [
        ("key", "travel:access_board_prowag", "The Access Board's rules for accessible sidewalks, crossings and "
                                              "accessible pedestrian signals"),
        ("key", "travel:access_board_vehicles", "The Access Board's guide to accessible buses, vans and paratransit "
                                                "vehicles"),
        ("pack", "commons_driving", "Paratransit vans and wheelchair-accessible taxis"),
        ("link", "FTA: ADA paratransit (who qualifies and how to apply)",
         "https://www.transit.dot.gov/regulations-and-guidance/civil-rights-ada/ada-paratransit",
         "a US government page; open it in a browser (transportation.gov refuses programs)"),
        ("word", "vision-living", "The vision collection's books on orientation and mobility, transit and "
                                  "paratransit")]),
    ("Commercial vehicles and motorcycles", "CDL and motorcycle licences; towing.", [
        ("link", "FMCSA: commercial driver's license", "https://www.fmcsa.dot.gov/registration/commercial-drivers-"
                                                       "license", "public domain, but fmcsa.dot.gov refuses programs"),
        ("link", "AAMVA model CDL manual", "https://www.aamva.org/", "AAMVA's copyright: each state publishes its "
                                                                     "own version (see the state pages)"),
        ("key", "rvs:index", "Motorcycles, RVs and trailers: the library's guide")]),
]
CA_SECTIONS = [
    ("Provincial and territorial driver handbooks", CA_INTRO,
     [("link", f"{s}: {who}", url, "its driver's handbook (link only)") for s, who, url in CA_AGENCIES] +
     [("key", "pdf:alberta_drivers_guide", "Alberta's Driver's Guide, in full (Open Government Licence - Alberta)"),
      ("pack", "ca_road_signs", "Canadian road signs")]),
]

US_INDEX = X.index_maker("drive_us", GROUP, "Driving and road rules in the US: a guide to the library",
                         "Driving and road rules (US)",
                         "A guide to the library for US drivers, passengers and pedestrians: every state's driver "
                         "licensing agency and where its driver handbook, CDL manual and motorcycle manual are "
                         "published, the national sign manual, safe driving, blind and low-vision pedestrians and "
                         "passengers, and commercial vehicles and motorcycles.", US_SECTIONS)
CA_INDEX = X.index_maker("drive_canada", GROUP, "Driving in Canada: a guide to the library",
                         "Driving and road rules (Canada)",
                         "A guide to the library for drivers in Canada: every province's and territory's driver "
                         "licensing agency and where its driver's handbook is published, and Alberta's guide in full.",
                         CA_SECTIONS, country="Canada")
MAKERS = {"index_us": US_INDEX, "index_canada": CA_INDEX}

# ====================================================================== the books built in full

PDFS = [
    K.us_pdf(GROUP, name="mutcd_11th", title="Manual on Uniform Traffic Control Devices (MUTCD), 11th Edition (FHWA)",
             subject="Road signs, signals and markings", publisher="Federal Highway Administration (US Department of "
             "Transportation)", pdf="https://mutcd.fhwa.dot.gov/pdfs/11th_Edition/mutcd11thedition.pdf",
             page="https://mutcd.fhwa.dot.gov/", published="2023-12", version="11th Edition, December 2023",
             description="The national standard for every traffic control device on US roads: the meaning, shape, "
                         "colour and placement of every regulatory, warning and guide sign, traffic signals and "
                         "pedestrian signals (accessible pedestrian signals and their push buttons among them), "
                         "pavement markings, school zones, work zones, railway crossings and bicycle facilities.",
             notice=f"From the Federal Highway Administration: a US government work (public domain). States adopt the "
                    f"MUTCD with their own supplements; the state's own law decides. {DRIVE_SAFETY}"),
    K.us_pdf(GROUP, name="army_tc_21_305_20", title="Manual for the Wheeled Vehicle Operator (TC 21-305-20, 2016)",
             subject="Driving (defensive driving and towing)", publisher="Headquarters, Department of the Army",
             archive="tc-21-305-20-manual-for-the-wheeled-vehicle-operator-2016", distribution_a=True,
             published="2016", version="TC 21-305-20, 2016 (Internet Archive item tc-21-305-20-manual-for-the-"
                                       "wheeled-vehicle-operator-2016)",
             description="The US Army's driver training manual: the driver's duties, vehicle checks before, during "
                         "and after driving, defensive driving, driving at night and in rain, snow, ice and fog, "
                         "backing and parking, coupling and towing trailers, and what to do after an accident.",
             notice=f"A work of the US Army (public domain); the builder says what its own front pages print about "
                    f"distribution. Written for military vehicles; civilian traffic law is the state's handbook. "
                    f"{DRIVE_SAFETY}"),
]

GUIDES = [
    X.cdc_site_book(GROUP, "cdc_road_safety", "Road safety: impaired and distracted driving, teen and older drivers, "
                    "child passengers and pedestrians (CDC)", "Road safety",
                    ["impaired-driving", "distracted-driving", "teen-drivers", "older-adult-drivers",
                     "child-passenger-safety", "pedestrian-safety", "transportation-safety"],
                    "CDC's road safety pages, every page: alcohol- and drug-impaired driving, distracted driving "
                    "(phones and texting), teen drivers and graduated licensing, older adult drivers, child passenger "
                    "safety (car seats, booster seats and seat belts by age), pedestrian safety, and CDC's "
                    "transportation safety overview.", DRIVE_SAFETY,
                    units=[(r"/impaired", "Impaired driving"), (r"/distracted", "Distracted driving"),
                           (r"/teen", "Teen drivers"), (r"/older", "Older drivers"), (r"/child-passenger",
                                                                                     "Child passengers"),
                           (r"/pedestrian", "Pedestrians"), (r".", "Transportation safety")]),
]

US_KEYS = ["drive:index_us"] + [f"drive:{p['name']}" for p in PDFS] + [f"drive:{g['name']}" for g in GUIDES]
CA_KEYS = ["drive:index_canada"]
COLLECTION = K.Collection("drive", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"driving": lambda: US_KEYS + CA_KEYS, "driving-us": lambda: list(US_KEYS),
                                 "driving-canada": lambda: list(CA_KEYS)})

# Where a Canadian book's practice differs (sources.PRACTICE_SUBJECTS; first match wins).
PRACTICE_SUBJECTS = [
    (r"driving and road rules \(canada\)", "traffic laws, road signs, licence classes and speeds in kilometres per "
                                           "hour, which apply only there"),
]
LICENCE_LINES = {
    "driving_mutcd": "mutcd.fhwa.dot.gov: a work of the Federal Highway Administration (17 U.S.C. 105, checked on "
                     "govinfo.gov's policies page at every build); robots.txt allows the PDF and asks 1 second "
                     "between requests; no AI rules (checked 2026-11-22).",
    "driving_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are public domain "
                   "on four conditions (credit, no endorsement, no change, free on CDC's site), met in the notice; "
                   "the pages are kept whole. www.cdc.gov answered this build machine \"403\" on 2026-11-22; the "
                   "builder asks robots.txt at every build and leaves the book out while CDC refuses.",
    "driving_army": "TC 21-305-20 (2016): a work of the US Army, read from the Internet Archive (its item is marked "
                    "with the Public Domain Mark) because armypubs.army.mil shuts out automated readers; the builder "
                    "reads its front pages and follows the shared release rule (military_release.py).",
    "driving_index": "The indexes (drive:index_us, drive:index_canada) are the toolkit's own facts and links, CC0. "
                     "Every agency address was checked to answer on 2026-11-22 (some answer programs \"403\" and open "
                     "in a browser).",
}
NOT_INCLUDED = [
    ("The states' driver handbooks, CDL manuals and motorcycle manuals (all 50 states and DC)", "US state works are "
     "not covered by 17 U.S.C. 105, and each state sets its own terms; the handbooks checked print a copyright notice "
     "or no licence, so none is copied. Every agency is listed with its address in drive:index_us for the owner to "
     "open or fetch with Program Downloader. Index: https://www.usa.gov/state-motor-vehicle-services"),
    ("The provinces' and territories' driver's handbooks (Ontario's Official MTO Driver's Handbook, ICBC's Learn to "
     "Drive Smart, SGI, MPI, the SAAQ guides and the others)", "Crown copyright of each province or its insurer, with "
     "their own terms (ICBC's and SGI's handbooks are their copyright; the SAAQ's guides are sold); link-only in "
     "drive:index_canada. Alberta's guide is built (pdf:alberta_drivers_guide). Index: "
     "https://www.ontario.ca/document/official-mto-drivers-handbook"),
    ("AAMVA model Commercial Driver's License Manual", "Copyright of the American Association of Motor Vehicle "
     "Administrators; the states publish their own versions (links in drive:index_us). Index: https://www.aamva.org/"),
    ("NHTSA's road safety pages and brochures (drunk, drugged, drowsy and distracted driving, seat belts, child "
     "seats, older drivers, pedestrians, motorcycle safety, towing a trailer)", "Public domain, but www.nhtsa.gov "
     "refuses programs (\"403\", robots.txt included, 2026-11-22), and no Internet Archive copy was found (searched "
     "2026-11-22: towing a trailer, driving safely while aging, adapting motor vehicles, DOT HS). CDC's road safety "
     "pages say the same and are built (drive:cdc_road_safety). Index: https://www.nhtsa.gov/road-safety"),
    ("FMCSA's commercial driver's licence pages and the CDL program", "Public domain, but www.fmcsa.dot.gov refuses "
     "programs (\"403\", 2026-11-22). Link-only. Index: https://www.fmcsa.dot.gov/registration/commercial-drivers-"
     "license"),
    ("Defensive driving courses (National Safety Council, AAA, state-approved online courses)", "Copyright of each "
     "organisation (and most are paid courses). The Army's TC 21-305-20 teaches defensive driving and is built. Index: "
     "https://www.nsc.org/safety-training/defensive-driving"),
    ("Rideshare and taxi apps' help for blind riders (Uber, Lyft) and guide dog rules", "The companies' copyright; "
     "link-only. The ADA's service animal rules for rides are in the library's transport books. Index: "
     "https://help.uber.com/ and https://help.lyft.com/"),
    ("The vision helper's books on orientation and mobility, paratransit and being a safe pedestrian", "Built by the "
     "vision collection (request word vision-living), not repeated here. Index: https://www.access-board.gov/prowag/"),
    ("Older road sign and driving manuals (MUTCD 2009 edition, pre-1931 motoring books)", "The current MUTCD (11th "
     "edition) replaces the 2009 edition; old motoring books are out of date for today's laws (the old car care books "
     "are in car-care). Index: https://mutcd.fhwa.dot.gov/kno_2009r1r2.htm"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
