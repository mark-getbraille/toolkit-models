"""Power and electrical for the reference library, in the top-level group "Reference, power and electrical" (the
owner's request of 2026-11-22: backup generators, solar and battery power, small wind and water power, do-it-yourself
power projects and home electrical safety). Keys: backup-power (generators, wind, water, do-it-yourself and electrical
books), solar (solar, batteries and the tax credit), power:<name>.

What this module builds, in plain words, each IN FULL:
  backup-power
  - the US Department of Energy's wind pages (how wind turbines work, distributed and small wind, the questions and
    answers on small wind systems) and WINDExchange (the Small Wind Guidebook, siting, installation, safety, maps and
    data, permitting and zoning, money, small community wind), and its hydropower pages (how hydropower works, the
    kinds of plants and turbines, the glossary); US government works on energy.gov;
  - the US Army's field manual on electrical systems (FM 5-424, 1997: generators, power distribution, wiring and
    grounding) and the operator's manuals of three military generator sets (TM 9-6115-641-10, the 5 kW MEP-802A;
    TM 9-6115-749-10, the 5 kW AMMPS MEP-1030; TM 9-6115-643-10, the 15 kW MEP-804A: setting up, grounding, starting,
    loads, checks and troubleshooting), read from the Internet Archive and judged at every build by the release rule
    for military publications (military_release.py; their front pages print Distribution Statement A);
  - OSHA's Controlling Electrical Hazards (OSHA 3075, 1997, from DTIC's public copy on the Internet Archive);
  - Wikibooks' Electric Motors and Generators (CC BY-SA 4.0, share-alike);
  - old public-domain books (published before 1931; the builder checks each Internet Archive item's year) on making
    and using small power plants: Anderson's Electricity for the Farm (1915: water wheels and small dynamos),
    Koester's Electricity for the Farm and Home (1913), Hasluck's Dynamos and Electric Motors: how to make and run
    them (1903), Crofts' How to Make a Dynamo (1890), Case's Theory of Direct Current Dynamos and Motors (1921),
    Powell's Windmills and Wind Motors: how to build and run them (1910), Murphy's The Windmill (USGS, 1901),
    Daugherty's Hydraulic Turbines (1913), Mead's Water Power Engineering (1915) and Potter's Farm Motors (1917).
  solar
  - the Department of Energy's Homeowner's Guide to Solar and its consumer articles (a step-by-step guide to going
    solar, choosing an installer, leases, loans and power purchase agreements, solar co-ops, community solar, will I
    save money, adding solar when replacing a roof);
  - the US Treasury's consumer guides: Before You Buy Solar Panels, Before You Sign a Solar Lease, Before You Sign a
    Power Purchase Agreement, Before You Sign a Community Solar Subscription;
  - the IRS instructions for Form 5695 (Residential Energy Credits), with a note that the rules change: the IRS page
    says which years and expenses qualify;
  - Wikibooks' Battery Power (CC BY-SA 4.0);
  - old public-domain battery books: Marshall's Small Accumulators: how made and used (1899) and Morse's Storage
    Batteries (1912).

Every book's notice carries SAFETY: carbon monoxide (generators outdoors only, at least 20 feet from the house; get
out and call 911 if a CO alarm sounds), never back-feed (a transfer switch or interlock installed by a licensed
electrician), electric shock and DC arcs, battery fires, rotating parts and fuel, and roof falls. The old books' notices
also say that their safety advice is out of date.

Moved into this group (MOVED_TO_POWER: the owner's decision of 2026-11-22; their keys stay the same, only the group
label changes): Lessons in Electric Circuits (elec:kuphaldt_liec_*), the NEETS electricity modules 1 to 5 and the Navy
manuals Introduction to Alternating Current and Transformers, Construction Electrician 3 & 2 and Electrician's Mate
3 & 2 (sources.py and reference_more.py; sources.py applies the move at its end).

Not built (NOT_INCLUDED, link-only for the owner's personal assistant, each with its index address): NREL (now the
National Laboratory of the Rockies) and Sandia handbooks (contractor copyright, "may be subject to copyright"), the
NEC (NFPA's copyright), OSHA's, CPSC's, FEMA's and Ready.gov's generator and solar pages (they refuse programs),
Open Source Ecology (ai-train=no), Hugh Piggott's books, Practical Action's technical briefs, the Florida Solar Energy
Center, the makers' manuals and vehicle power guides (the manual collections link them), a restricted Army generator
manual (personal use), and Instructables and YouTube.

Licences: energy.gov, irs.gov, home.treasury.gov, OSHA and the Army: works of the US government (17 U.S.C. 105, the
line checked on govinfo.gov's policies page at every build); Wikibooks: CC BY-SA 4.0 (its copyright page checked at
every build); the old books: US public domain (published before 1931). robots.txt of every site allows the pages;
none has AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/power_books.py power:doe_small_wind --out build/textbooks --limit 5
  python3 textbooks/power_books.py --list backup-power solar
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from electronics_books import wikibook  # noqa: E402

GROUP = "power"
GROUPS = {GROUP: "Reference, power and electrical"}

# The safety notice every book carries (the picture packs say the same things in packs/power_packs.py).
SAFETY = ("Safety: run a generator only outdoors, at least 20 feet from the house with its exhaust away from windows "
          "and doors: its carbon monoxide can kill. Have a carbon monoxide alarm; if it sounds or anyone feels dizzy "
          "or sick, get out to fresh air and call 911. Never back-feed: never plug a generator into a wall or dryer "
          "outlet, which can kill utility line workers; connect to house wiring only through a transfer switch or "
          "interlock installed by a licensed electrician. Electricity can kill: turn the power off and test it before "
          "touching wiring; solar panels and batteries stay live and DC can arc. Large batteries can burn (lithium "
          "thermal runaway, hydrogen from lead-acid). Guard belts, blades and other rotating parts, let engines cool "
          "before refuelling, and use fall protection on roofs and towers. Electrical codes (the National Electrical "
          "Code) and permits apply: when in doubt, hire a licensed electrician.")

E = "https://www.energy.gov"
DOE = "US Department of Energy"
DOE_NOTICE = f"From the US Department of Energy (energy.gov): a US government work (public domain). {SAFETY}"


def page_list_book(name, title, subject, publisher, urls, pages, description, notice, units=()):
    """A web guide of a fixed list of pages (no crawl beyond them): the first address is its source."""
    return K.us_web(GROUP, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=notice, crawl=[(urls[0], 0)], urls=list(urls), pages=pages,
                    unit_rules=list(units), limit=len(urls) + 5)


# ====================================================================== energy.gov: wind, WINDExchange, hydropower

WIND_PAGES = [f"{E}/cmei/systems/{p}" for p in (
    "how-do-wind-turbines-work", "explore-wind-turbine-text-version", "wind-energy-basics", "distributed-wind",
    "how-distributed-wind-works", "how-do-distributed-wind-energy-systems-work-text-version",
    "frequently-asked-questions-small-distributed-wind-systems", "frequently-asked-questions-about-wind-energy",
    "advantages-and-challenges-wind-energy")]
WINDEXCHANGE_PAGES = [f"{E}/cmei/systems/windexchange/{p}" for p in (
    "small-wind-guidebook", "what-wind-energy", "site-selection", "maps-and-data", "installation", "safety",
    "permitting-and-zoning", "ordinances", "financial-considerations", "sound", "small-community-wind-handbook")]
HYDRO_PAGES = [f"{E}/cmei/water/{p}" for p in (
    "hydropower-basics", "how-hydropower-works", "types-hydropower-plants", "types-hydropower-turbines",
    "benefits-hydropower", "history-hydropower", "glossary-hydropower-terms")]

GUIDES = [
    page_list_book("doe_wind_basics", "How wind turbines and small wind systems work (US Department of Energy)",
                   "Wind power", DOE, WIND_PAGES,
                   r"^https://www\.energy\.gov/cmei/systems/[a-z0-9-]+$",
                   "The Department of Energy's wind pages for homeowners and farmers: how a wind turbine works and "
                   "its parts (the text version of the turbine explorer), wind energy basics, distributed wind (small "
                   "turbines on homes, farms and businesses) and how it works, the questions and answers about small "
                   "and distributed wind systems (sizing, cost, towers, connecting to the grid or batteries), and the "
                   "advantages and challenges of wind energy.", DOE_NOTICE,
                   units=[(r"distributed|small", "Small and distributed wind"), (r".", "How wind turbines work")]),
    page_list_book("doe_small_wind", "Small wind: the Small Wind Guidebook, siting, installation and safety "
                   "(WINDExchange, US Department of Energy)", "Small wind turbines", f"{DOE}, WINDExchange",
                   WINDEXCHANGE_PAGES, r"^https://www\.energy\.gov/cmei/systems/windexchange/[a-z0-9-]+$",
                   "WINDExchange's pages for people thinking of a small wind turbine: the Small Wind Guidebook (is "
                   "wind right for you, how much energy a turbine will make, choosing and siting a turbine and its "
                   "tower height), what wind energy is, site selection, wind maps and data, installation, safety, "
                   "permitting and zoning, local ordinances, money matters, turbine sound, and the small community "
                   "wind handbook.", DOE_NOTICE,
                   units=[(r"guidebook|what-wind", "The Small Wind Guidebook"),
                          (r"site|maps", "Siting and wind maps"), (r"installation|safety|sound", "Installing safely"),
                          (r".", "Permits, money and community wind")]),
    page_list_book("doe_hydropower_basics", "How hydropower works: plants, turbines and terms (US Department of "
                   "Energy)", "Water power", DOE, HYDRO_PAGES, r"^https://www\.energy\.gov/cmei/water/[a-z0-9-]+$",
                   "The Department of Energy's hydropower pages: hydropower basics, how hydropower works (head and "
                   "flow), the kinds of hydropower plants (run-of-river, storage and pumped storage), the kinds of "
                   "water turbines (Pelton, Turgo, cross-flow, Francis, propeller and Kaplan), the benefits and "
                   "history of hydropower, and a glossary of hydropower terms. Water rights and permits are set by "
                   "each state: ask the state's water agency before building a micro-hydro system.", DOE_NOTICE,
                   units=[(r"turbines|plants", "Plants and turbines"), (r".", "Hydropower basics")]),
]

# ====================================================================== energy.gov: the homeowner's guide to solar

SOLAR_PAGES = [f"{E}/cmei/systems/homeowners-guide-solar",
               f"{E}/cmei/systems/articles/walk-me-through-it-step-step-guide-consumers-going-solar",
               f"{E}/cmei/systems/articles/decisions-decisions-choosing-solar-installer",
               f"{E}/cmei/systems/articles/homeowners-guide-solar-financing-leases-loans-and-ppas",
               f"{E}/cmei/systems/articles/purchasing-power-going-solar-through-cooperatives",
               f"{E}/cmei/systems/community-solar",
               f"{E}/articles/will-i-save-money-solar-energy",
               f"{E}/articles/replacing-your-roof-its-great-time-add-solar"]
GUIDES.append(page_list_book(
    "doe_homeowners_guide_solar", "Homeowner's Guide to Solar: going solar step by step (US Department of Energy)",
    "Home solar power", DOE, SOLAR_PAGES,
    r"^https://www\.energy\.gov/(cmei/systems/(articles/)?[a-z0-9-]+|articles/[a-z0-9-]+)$",
    "The Department of Energy's Homeowner's Guide to Solar and its consumer articles: is solar right for my home "
    "(roof, shade and orientation), how much power can I make (NREL's PVWatts calculator), a step-by-step guide to "
    "going solar, choosing a solar installer, buying with cash or a loan, leases and power purchase agreements, solar "
    "co-ops, community solar for renters and shaded homes, whether solar will save money, and adding solar when the "
    "roof is replaced.", DOE_NOTICE,
    units=[(r"homeowners-guide-solar$", "The homeowner's guide"), (r"community", "Community solar"),
           (r".", "Going solar")]))

# ====================================================================== Treasury and IRS

TREASURY = "https://home.treasury.gov/system/files/136/"
TREASURY_PAGE = "https://www.energy.gov/cmei/systems/homeowners-guide-solar"
TREASURY_NOTICE = f"A work of the US Department of the Treasury (public domain). {SAFETY}"
PDFS = [
    K.us_pdf(GROUP, name=f"treasury_{name}", title=f"{title} (US Department of the Treasury)",
             subject="Home solar power (consumer guide)", publisher="US Department of the Treasury",
             pdf=TREASURY + pdf, page=TREASURY_PAGE, version=f"the PDF {pdf}",
             description=f"The Treasury's plain-language consumer guide {title}: {words}", notice=TREASURY_NOTICE)
    for name, pdf, title, words in [
        ("before_you_buy_solar", "Guide-Before-You-Buy-Solar-Panels-eng.pdf", "Before You Buy Solar Panels",
         "the questions to ask before buying, getting several quotes, what a contract should say, warranties, "
         "tax credits and incentives, and how to avoid scams."),
        ("before_you_sign_solar_lease", "Guide-Before-You-Sign-a-Solar-Lease-eng.pdf", "Before You Sign a Solar "
         "Lease", "how a solar lease works, payments and escalators, who owns and maintains the panels, selling the "
         "house, and the questions to ask."),
        ("before_you_sign_ppa", "Guide-Before-You-Sign-a-Power-Purchase-Agreement-eng.pdf", "Before You Sign a "
         "Power Purchase Agreement", "how a solar power purchase agreement works, the price per kilowatt-hour and "
         "its increases, the length of the contract, and the questions to ask."),
        ("before_you_sign_community_solar", "Guide-Before-You-Sign-a-Community-Solar-Subscription-eng.pdf",
         "Before You Sign a Community Solar Subscription", "how community solar subscriptions and bill credits "
         "work, contract terms, cancelling, and the questions to ask."),
    ]
]
PDFS.append(K.us_pdf(
    GROUP, name="irs_form_5695_instructions", title="Instructions for Form 5695, Residential Energy Credits (IRS)",
    subject="Solar and energy tax credits", publisher="Internal Revenue Service (US Department of the Treasury)",
    pdf="https://www.irs.gov/pub/irs-pdf/i5695.pdf", page="https://www.irs.gov/forms-pubs/about-form-5695",
    version="the current i5695.pdf on irs.gov at the time of the build",
    description="The IRS's instructions for Form 5695: who can claim the residential energy credits, which costs "
                "count (solar electric and solar water heating, small wind, geothermal heat pumps, battery storage, "
                "and home energy improvements), how to work out the credit, and carrying unused credit forward. Tax "
                "credits change with the law (Congress changed these credits in 2025): the IRS page about Form 5695 "
                "says which tax years and expenses qualify; ask a tax professional about your own return.",
    notice=f"A work of the Internal Revenue Service (public domain). This is the IRS's own text, not tax advice. "
           f"{SAFETY}"))

# ====================================================================== military and OSHA manuals

ARMY = "Headquarters, Department of the Army"
PDFS += [
    K.us_pdf(GROUP, name="army_fm_5_424_electrical_systems_1997", title="Theater of Operations Electrical Systems "
             "(FM 5-424, 1997)", subject="Generators, power distribution and wiring", publisher=ARMY,
             archive="fm-5-424-theater-of-operations-electrical-systems-1997", distribution_a=True,
             work="a work of the US Army", published="1997-06",
             version="FM 5-424, June 1997 (Internet Archive item fm-5-424-theater-of-operations-electrical-"
                     "systems-1997)",
             description="The US Army's field manual for electricians: electrical theory, safety, generators and "
                         "power plants, power distribution lines, interior wiring of buildings, grounding, "
                         "transformers, motors, lighting, and estimating loads. 1997 edition: follow current "
                         "electrical codes for any work on a home.",
             notice=f"A work of the US Army (public domain); the builder says what its own front pages print about "
                    f"distribution. {SAFETY}"),
    K.us_pdf(GROUP, name="army_tm_9_6115_641_10_mep802a", title="Operator's Manual for the 5 kW Tactical Quiet "
             "Generator Set MEP-802A (TM 9-6115-641-10, 2009)", subject="Generator sets", publisher=ARMY,
             archive="5kw-mep-802-tqg-9-6115-641-10-oct-09-pin-071025", military=True, work="a work of the US Army",
             published="2009-10-15", version="TM 9-6115-641-10, 15 October 2009 (Internet Archive item 5kw-mep-802-"
                                             "tqg-9-6115-641-10-oct-09-pin-071025)",
             description="The operator's manual of the Army's 5 kilowatt diesel generator set: its controls and "
                         "indicators, siting and grounding it, starting, running and stopping, connecting loads, "
                         "the checks before, during and after running (PMCS), troubleshooting, and operating in "
                         "unusual conditions. It shows how a modern generator is set up and cared for; household "
                         "generators follow their own makers' manuals.",
             notice=f"A work of the US Army (public domain); the builder says what its own front pages print about "
                    f"distribution. {SAFETY}"),
    K.us_pdf(GROUP, name="army_tm_9_6115_749_10_mep1030", title="Operator's Manual for the 5 kW Advanced Medium "
             "Mobile Power Source MEP-1030 (TM 9-6115-749-10, 2011)", subject="Generator sets", publisher=ARMY,
             archive="5-kw-mep-1030-ammps-tm-9-6115-749-10-pin-086624-1-feb-11", military=True,
             work="a work of the US Army", published="2011-02-01",
             version="TM 9-6115-749-10, 1 February 2011 (Internet Archive item 5-kw-mep-1030-ammps-tm-9-6115-749-10-"
                     "pin-086624-1-feb-11)",
             description="The operator's manual of the Army's newer 5 kilowatt generator set (AMMPS): its digital "
                         "control panel, setting up and grounding, starting and stopping, paralleling, loads, "
                         "routine checks and troubleshooting.",
             notice=f"A work of the US Army (public domain); the builder says what its own front pages print about "
                    f"distribution. {SAFETY}"),
    K.us_pdf(GROUP, name="army_tm_9_6115_643_10_mep804a", title="Operator's Manual for the 15 kW Tactical Quiet "
             "Generator Sets MEP-804A and MEP-814A (TM 9-6115-643-10, 2010)", subject="Generator sets",
             publisher=ARMY, archive="mep804amep814atechnicalmanualoperatorsmanualtm9611564310", military=True,
             work="a work of the US Army", published="2010-02-15",
             version="TM 9-6115-643-10, 2010 (Internet Archive item mep804amep814atechnicalmanualoperatorsmanual"
                     "tm9611564310)",
             description="The operator's manual of the Army's 15 kilowatt generator sets: controls, siting and "
                         "grounding, voltage and frequency changeover, starting and stopping, loads, checks and "
                         "troubleshooting.",
             notice=f"A work of the US Army (public domain); the builder says what its own front pages print about "
                    f"distribution. {SAFETY}"),
    K.us_pdf(GROUP, name="osha_controlling_electrical_hazards_1997", title="Controlling Electrical Hazards (OSHA "
             "3075, 1997)", subject="Electrical safety", publisher="Occupational Safety and Health Administration "
             "(US Department of Labor)", archive="DTIC_ADA400134", published="1997",
             version="OSHA 3075, 1997 revision (DTIC's copy, Internet Archive item DTIC_ADA400134)",
             description="OSHA's booklet on basic electrical safety for people with little electrical training: how "
                         "electricity hurts people (shock, burns, falls), insulation, guarding, grounding, circuit "
                         "protection (fuses, breakers and ground-fault circuit interrupters), safe work practices "
                         "and lockout, and what to do for someone who has had a shock (do not touch them until the "
                         "power is off; call 911).",
             notice=f"A work of the US Department of Labor (public domain), read from DTIC's public copy on the "
                    f"Internet Archive. {SAFETY}"),
]

# ====================================================================== Wikibooks (CC BY-SA 4.0)

GUIDES += [
    wikibook(GROUP, "wikibooks_electric_motors_generators", "Electric_Motors_And_Generators", "Electric Motors "
             "and Generators (Wikibooks)", "Generators and motors", "Wikibooks' book on electric machines: magnetic "
             "fields, vectors and fields, AC motors and generators, single-phase and three-phase machines.", SAFETY),
    wikibook(GROUP, "wikibooks_battery_power", "Battery_Power", "Battery Power (Wikibooks)", "Batteries",
             "Wikibooks' book on batteries: the types of batteries, alkaline, lead-acid and lithium-ion batteries, "
             "how they work, charge and wear out.", SAFETY),
]

# ====================================================================== old public-domain books (before 1931)

OLD = dict(group=GROUP, country="United States", licence="Public domain (published before 1931)",
           licence_url="https://www.copyright.gov/help/faq/faq-duration.html", old_public_domain=True,
           level="reference", changes="its scanned pages' machine-read text (with the scanner's mistakes) made into "
                                      "web pages, one per chapter")
OLD_NOTE = ("Published in {year}: an old book, kept for its plain explanations of how {what} work and are built; "
            "its wiring practice, materials and safety advice are out of date (follow today's electrical code and "
            "the makers' instructions), and the machine-read text has the scanner's mistakes. ")


def old_book(name, title, subject, publisher, archive, year, description, what, country="United States"):
    """An old public-domain book from the Internet Archive as a PDF entry."""
    return dict(OLD, name=name, title=title, subject=subject, publisher=publisher, archive=archive, country=country,
                published=str(year), version=f"{year} edition", description=description,
                notice=OLD_NOTE.format(year=year, what=what) + SAFETY)


OLD_BACKUP = [
    old_book("anderson_electricity_for_the_farm_1915", "Electricity for the Farm: light, heat and power by "
             "inexpensive methods from the water wheel or farm engine (Frederick Irving Anderson, 1915)",
             "Small water and engine power plants", "Frederick Irving Anderson (Macmillan)",
             "electricityforfa00anderich", 1915,
             "A practical book for farmers making their own electricity: measuring a stream's head and flow, water "
             "wheels and small turbines, dams and flumes, choosing and driving a dynamo, the switchboard, wiring the "
             "house and barn, storage batteries, and engine-driven plants.", "small power plants"),
    old_book("koester_electricity_farm_home_1913", "Electricity for the Farm and Home (Frank Koester, 1913)",
             "Small power plants", "Frank Koester (Sturgis and Walton)", "electricityforfa00koesrich", 1913,
             "How farms and country homes can make and use electricity: water power, wind power and engine plants, "
             "generators, batteries, wiring, lighting, and electric motors on the farm.", "small power plants"),
    old_book("hasluck_dynamos_electric_motors_1903", "Dynamos and Electric Motors: how to make and run them (Paul "
             "N. Hasluck, 1903)", "Building dynamos", "Paul N. Hasluck (Cassell and Company)",
             "dynamoselectricm00hasliala", 1903,
             "A workshop handbook for building small dynamos and motors: field magnets, armatures and their winding, "
             "commutators and brushes, and running and testing the machines.", "dynamos and motors",
             country="United Kingdom"),
    old_book("crofts_how_to_make_a_dynamo_1890", "How to Make a Dynamo: a practical treatise for amateurs (Alfred "
             "Crofts, 1890)", "Building dynamos", "Alfred Crofts", "howtomakedynamop00crofrich", 1890,
             "An amateur's guide to building a small dynamo step by step: the magnets, armature, commutator, brushes "
             "and winding, with the reasons for each part.", "dynamos", country="United Kingdom"),
    old_book("case_direct_current_dynamos_motors_1921", "The Theory of Direct Current Dynamos and Motors (John Case, "
             "1921)", "Generator principles", "John Case", "TheTheoryOfDirectCurrentDynamosAndMotors", 1921,
             "A textbook of how direct-current dynamos and motors work: magnetic circuits, armature reaction, "
             "commutation, voltage regulation, efficiency and testing.", "dynamos and motors",
             country="United Kingdom"),
    old_book("powell_windmills_wind_motors_1910", "Windmills and Wind Motors: how to build and run them (F. E. "
             "Powell, 1910)", "Building windmills", "F. E. Powell", "windmillsandwin00powegoog", 1910,
             "A do-it-yourself book on building small windmills and wind motors: sails and wheels, towers, "
             "governing in high winds, and using them to pump water and drive dynamos.", "windmills"),
    old_book("murphy_the_windmill_1901", "The Windmill: its efficiency and economic use (Edward Charles Murphy, US "
             "Geological Survey, 1901)", "Windmills", "US Geological Survey (Water-Supply and Irrigation Papers)",
             "windmillitseffic00murprich", 1901,
             "The US Geological Survey's study of farm windmills: kinds of mills, their power and efficiency in "
             "different winds, pumping and irrigation, and their cost.", "windmills"),
    old_book("daugherty_hydraulic_turbines_1913", "Hydraulic Turbines (R. L. Daugherty, 1913)", "Water turbines",
             "R. L. Daugherty (McGraw-Hill)", "HydraulicTurbines", 1913,
             "A textbook of water turbines: impulse wheels (Pelton) and reaction turbines, head, flow and speed, "
             "governing, draft tubes, testing and choosing a turbine for a site.", "water turbines"),
    old_book("mead_water_power_engineering_1915", "Water Power Engineering (Daniel W. Mead, 1915)", "Water power",
             "Daniel W. Mead (McGraw-Hill)", "enginewaterpower00meadrich", 1915,
             "A large reference on developing water power: measuring stream flow and head, dams, intakes, racks and "
             "penstocks, water wheels and turbines, governors, and planning a plant.", "water power plants"),
    old_book("potter_farm_motors_1917", "Farm Motors: steam and gas engines, hydraulic and electric motors, traction "
             "engines, automobiles, animal motors, windmills (Andrey A. Potter, 1917)", "Farm power",
             "Andrey A. Potter (McGraw-Hill)", "farmmotorssteamg00pottrich", 1917,
             "A college textbook of the power sources of the farm: windmills, water wheels and hydraulic motors, "
             "gas and oil engines, electric motors and their care.", "farm engines, windmills and water motors"),
]
OLD_SOLAR = [
    old_book("marshall_small_accumulators_1899", "Small Accumulators: how made and used (Percival Marshall, 1899)",
             "Storage batteries", "Percival Marshall (Dawbarn and Ward)", "smallaccumulato00unkngoog", 1899,
             "An amateur's handbook of small lead-acid storage batteries: how they work, how to make plates and "
             "cells, charging, and caring for them.", "storage batteries", country="United Kingdom"),
    old_book("morse_storage_batteries_1912", "Storage Batteries: the chemistry and physics of the lead accumulator "
             "(Harry W. Morse, 1912)", "Storage batteries", "Harry W. Morse (Macmillan)", "storagebatteries00morsrich",
             1912, "How lead-acid storage batteries work: the chemistry of charging and discharging, capacity, "
                   "efficiency, sulphation and the care of batteries.", "lead-acid batteries"),
]
PDFS += OLD_BACKUP + OLD_SOLAR

# The books of each request word.
SOLAR_NAMES = ["doe_homeowners_guide_solar"] + [p["name"] for p in PDFS if p["name"].startswith("treasury_")] + \
    ["irs_form_5695_instructions", "wikibooks_battery_power"] + [b["name"] for b in OLD_SOLAR]
BACKUP_NAMES = [g["name"] for g in GUIDES + PDFS if g["name"] not in SOLAR_NAMES]
COLLECTION = K.Collection("power", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"backup-power": lambda: [f"power:{n}" for n in BACKUP_NAMES],
                                 "solar": lambda: [f"power:{n}" for n in SOLAR_NAMES]})

# Books of other modules that move into this group (only the group label changes; their keys stay the same).
# Lessons in Electric Circuits is moved in electronics_books.py itself; these are moved by sources.py at its end.
MOVED_TO_POWER = ("navy_neets_module_01", "navy_neets_module_02", "navy_neets_module_03", "navy_neets_module_04",
                  "navy_neets_module_05", "navy_ac_and_transformers", "navy_construction_electrician_3_2_1976",
                  "navy_electricians_mate_3_2_1981")

LICENCE_LINES = {
    "power_doe": "www.energy.gov: works of the US Department of Energy (17 U.S.C. 105, checked on govinfo.gov's "
                 "policies page at every build); robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "power_treasury_irs": "home.treasury.gov and www.irs.gov: works of the US Department of the Treasury and the IRS "
                          "(17 U.S.C. 105); robots.txt allows the files; no AI rules (checked 2026-11-22).",
    "power_army_osha": "FM 5-424 (1997), TM 9-6115-641-10 (2009), TM 9-6115-749-10 (2011) and TM 9-6115-643-10 "
                       "(2010): works of the US Army, read from the Internet Archive and judged at every build by the "
                       "shared release rule (all four printed Distribution Statement A when checked on 2026-11-22); "
                       "OSHA 3075 (1997): a work of the US Department of Labor, DTIC's public copy (\"Approved for "
                       "public release, distribution unlimited\").",
    "power_wikibooks": "en.wikibooks.org/wiki/Wikibooks:Copyrights (checked at every build): CC BY-SA 4.0, "
                       "share-alike.",
    "power_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                       "a later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                       "2026-11-22).",
}
NOT_INCLUDED = [
    ("NREL (now the National Laboratory of the Rockies) publications: Small Wind Electric Systems consumer guides, PV "
     "and battery best-practice handbooks, the PVWatts calculator", "The laboratory is run for DOE by a contractor; "
     "its disclaimer says its documents \"may be subject to U.S. and foreign Copyright Laws\" (www.nlr.gov/disclaimer, "
     "read 2026-11-22), so they are not public domain; www.nrel.gov did not answer this machine. Link-only for "
     "Program Downloader; PVWatts is a web calculator to open in a browser. Index: https://docs.nlr.gov/ and "
     "https://pvwatts.nrel.gov/"),
    ("Sandia National Laboratories PV handbooks (Stand-Alone Photovoltaic Systems: A Handbook of Recommended Design "
     "Practices; Photovoltaic Power Systems and the National Electrical Code: Suggested Practices)", "Written by a "
     "DOE contractor (Sandia) and its subcontractors, not federal employees, so not automatically public domain; no "
     "open licence was found. Link-only. Index: https://www.sandia.gov/ and https://www.osti.gov/"),
    ("National Electrical Code (NFPA 70) and NFPA 70E", "Copyright of the National Fire Protection Association; "
     "NFPA lets people read it free online after signing in, not copy it. Link-only. Index: "
     "https://www.nfpa.org/codes-and-standards/nfpa-70-standard-development/70"),
    ("OSHA portable generator, solar and fall protection pages; CPSC portable generator and carbon monoxide pages; "
     "FEMA and Ready.gov power outage pages; USDA Rural Development energy programs", "Public domain, but "
     "www.osha.gov, www.cpsc.gov, www.fema.gov, www.ready.gov and www.rd.usda.gov answered this machine \"403 "
     "Forbidden\" (robots.txt included, 2026-11-22). OSHA's Controlling Electrical Hazards is built from DTIC's copy "
     "and CDC's generator page is in outcook:cdc_food_power_outage. Link-only. Index: "
     "https://www.osha.gov/green-jobs/solar and https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/"
     "Portable-Generators"),
    ("DOE Energy Saver: planning a microhydropower system, small wind and off-grid systems, home energy audits and "
     "saving electricity", "The microhydropower, small wind and off-grid pages answer \"404\" (removed in "
     "energy.gov's redesign, 2026-11-22); the Energy Saver articles still on energy.gov are already built "
     "(dir:energy_saver_articles: standby power, appliances, lighting, solar at home). Index: "
     "https://www.energy.gov/energysaver/"),
    ("Open Source Ecology (Power Cube, solar and wind designs)", "CC BY-SA, but wiki.opensourceecology.org's "
     "robots.txt says ai-train=no and shuts out AI companies' crawlers (checked 2026-11-22); not read. Link-only. "
     "Index: https://wiki.opensourceecology.org/wiki/Power_Cube"),
    ("Hugh Piggott's wind turbine books and plans (A Wind Turbine Recipe Book, Windpower Workshop)", "Copyright of "
     "the author; not openly licensed. Link-only for the owner to buy or fetch. Index: https://www.scoraigwind.co.uk/"),
    ("Practical Action technical briefs (micro-hydro, small wind, solar, pedal power)", "Many are CC BY-NC-SA "
     "(non-commercial) and others the charity's copyright; the licence was not confirmed brief by brief, so they "
     "are link-only, for personal use. Index: https://practicalaction.org/knowledge-centre/"),
    ("Florida Solar Energy Center (University of Central Florida) consumer guides", "Copyright of the university; "
     "not openly licensed. Link-only. Index: https://energyresearch.ucf.edu/"),
    ("TM 9-6115-639-13&P, the 3 kW Tactical Quiet Generator MEP-831A (2017)", "Its front pages print Distribution "
     "Statement C and an export-control warning, and only the Internet Archive has it: by the release rule it is "
     "never put in a public collection; personal use only, for the owner to fetch himself. Index: "
     "https://archive.org/details/3-kw-mep-831-tqg-tm-9-6115-639-13-p-31-aug-2017-pin-082629"),
    ("Generator, solar, battery and vehicle power makers' manuals (Generac, Honda, Champion, Westinghouse, Kohler, "
     "Briggs and Stratton, Renogy, Victron, EcoFlow, Jackery, Goal Zero, Enphase, SolarEdge, Tesla Powerwall, Battle "
     "Born, Ford Pro Power Onboard, F-150 Lightning Intelligent Backup Power, GM Energy V2H)", "The makers' copyright; "
     "listed as links in the manual collections of the Power and electrical heading for the owner to fetch with "
     "Program Downloader. Index: https://www.generac.com/support/ and https://www.victronenergy.com/support-and-"
     "downloads/manuals"),
    ("Instructables, YouTube and other do-it-yourself generator and solar videos and pages", "Their terms do not "
     "allow programs to copy their content (the owner's rule for this collection); not read. Index: "
     "https://www.instructables.com/"),
    ("Wikibooks: Energy Efficiency Reference and Electricity and Magnetism", "Already whole in the Kiwix library's "
     "Wikibooks (CC BY-SA); the two short books on generators and batteries are built here. Index: "
     "https://en.wikibooks.org/wiki/Energy_Efficiency_Reference"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
