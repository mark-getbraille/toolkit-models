"""The collection "Driver, CDL and motorcycle handbooks (links)" (category key driving_handbooks): the owner's request
of 2026-11-22 for driving and road rules. practical_manuals.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (driver handbooks, driver's
            manuals, CDL manuals, motorcycle operator manuals, rules of the road);
  makers    every US state's and DC's driver licensing agency, and every Canadian province's and territory's: the
            agency's page where its driver handbook, commercial driver (CDL) manual and motorcycle manual are
            published. LINK-ONLY: US state works are not covered by the federal public-domain rule (17 U.S.C. 105),
            each state and province sets its own terms, and most handbooks print a copyright notice or no licence, so
            nothing is read from their sites; the person (or the personal assistant) opens the page or fetches the
            handbook with Program Downloader. The same agencies are listed in the reference library's index books
            drive:index_us and drive:index_canada (manuals/test_practical_manuals.py checks the two lists agree);
  guidance  the US government guides the reference library builds in full (the MUTCD, CDC's road safety pages, the
            Army's driver manual) and the federal pages that refuse programs (NHTSA, FMCSA), as links.

The safety notice is said first (NOTICE).
"""

NOTICE = ("Each state's or province's own handbook is the law where you live. Everyone buckles up; never drive after "
          "drinking or using drugs, or when drowsy; put the phone away; stop for school buses with red lights "
          "flashing; and yield to pedestrians, stopping for anyone with a white cane or a guide dog.")

IA_WORDS = ["driver handbook", "driver's handbook", "drivers handbook", "driver manual", "driver's manual",
            "drivers manual", "cdl manual", "commercial driver", "motorcycle operator manual", "rules of the road"]

RULE = ("state and provincial works are not covered by the federal public-domain rule and each government sets its "
        "own terms, so the handbooks are link-only: nothing is read from the agency's site; its page is listed for "
        "the person to open or fetch with Program Downloader")

# (state, the agency that licenses drivers, its address): the same list as textbooks/driving.py US_AGENCIES.
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
# The provinces and territories: the same list as textbooks/driving.py CA_AGENCIES.
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


def _slug(name):
    """"New Hampshire" -> "new-hampshire"."""
    return "-".join(name.lower().replace("'", "").split())


def _site(url):
    """The host of an address without its "www." ("https://www.in.gov/bmv/" -> "in.gov")."""
    host = url.split("/")[2]
    return host[4:] if host.startswith("www.") else host


_COMMON = dict(category="driving_handbooks", prefix="dh", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, key=f"us-{_slug(state)}", maker=f"{who} ({state})",
               type="driver handbook, CDL manual and motorcycle manual", library=url, site=_site(url))
          for state, who, url in US_AGENCIES] + \
         [dict(_COMMON, key=f"ca-{_slug(prov)}", maker=f"{who} ({prov})", type="driver's handbook", library=url,
               site=_site(url))
          for prov, who, url in CA_AGENCIES]

GUIDANCE = [
    dict(title="Manual on Uniform Traffic Control Devices, 11th edition (FHWA; built in full in the reference library: "
               "drive:mutcd_11th)", url="https://mutcd.fhwa.dot.gov/", by="the Federal Highway Administration"),
    dict(title="Road safety: impaired and distracted driving, teen and older drivers, child passengers, pedestrians "
               "(CDC; in the reference library: drive:cdc_road_safety)",
         url="https://www.cdc.gov/transportation-safety/", by="the US Centers for Disease Control and Prevention"),
    dict(title="Manual for the Wheeled Vehicle Operator (Army TC 21-305-20; in the reference library: "
               "drive:army_tc_21_305_20)",
         url="https://archive.org/details/tc-21-305-20-manual-for-the-wheeled-vehicle-operator-2016",
         by="the US Army"),
    dict(title="NHTSA road safety (open it in a browser: it refuses programs)", url="https://www.nhtsa.gov/road-safety",
         by="the National Highway Traffic Safety Administration"),
    dict(title="Commercial driver's license (FMCSA; open it in a browser: it refuses programs)",
         url="https://www.fmcsa.dot.gov/registration/commercial-drivers-license",
         by="the Federal Motor Carrier Safety Administration"),
    dict(title="State motor vehicle services (USA.gov)", url="https://www.usa.gov/state-motor-vehicle-services",
         by="USA.gov"),
]

CATEGORY = dict(
    name="Driver, CDL and motorcycle handbooks (links)",
    description="Every US state's and Canadian province's driver handbook, commercial driver (CDL) manual and "
                "motorcycle operator manual, as links to the licensing agency's own page, the Internet Archive's "
                "driver manuals, and the federal road sign manual and road safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each handbook belongs to its state or province",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
