"""Manual collections for POWER AND ELECTRICAL, under their own heading (the owner's request of 2026-11-22: backup
generators, solar and battery power, small wind and water power, and home electrical things). categories.py adds them
to CATEGORIES and gives them, and the existing electrical collections named in HEADING_KEYS, the field "heading":
"Power and electrical" (build_manuals.write puts it in the index and the manifest, so the toolkit can list them
together). The other categories' keys do not change.

  backup_generators    generator sets, gensets, tri-fuel, propane and natural gas generators, RV, PTO and welder
                       generators, generator heads and vehicle power: the Internet Archive's manuals searched with
                       GENERATOR_WORDS, the makers' pages as links (including Ford's and GM's vehicle-to-home power
                       guides), the US Army generator manuals (public_guides, judged by the release rule) and the
                       government guidance;
  solar_battery_power  solar panels, charge controllers (PWM and MPPT), solar, grid-tie, off-grid and micro
                       inverters, deep-cycle and LiFePO4 batteries, battery monitors and management systems, and solar
                       kits;
  wind_hydro_power     small wind turbines and wind generators, windmills and wind pumps, micro-hydro and water
                       turbines;
  home_electrical      surge protectors, power strips, extension cords, breaker panels and electrical testers for
                       the home, with the electrical safety and shock first aid guidance.

What each lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker, as in every
manual collection): by the owner's rule the makers' own manual libraries are LINK-ONLY, as in outdoor_cooking.py:
nothing is read from their sites, their pages are listed for the person (or the personal assistant) to open or fetch
with Program Downloader. (Victron publishes its manuals freely to download, but its site's terms do not grant
re-publishing them, so it is a link like the others.) The Internet Archive words are new: no other collection searches
them (the preparedness collection emergency_power already searches "inverter generator", "standby generator",
"transfer switch", "interlock kit", "portable generator" and the UPS and home battery words, lawn_garden "generator",
emergency_lighting "portable power station" and "solar generator", electrical_devices "gfci", "outlet" and "circuit
breaker"); the self-test checks.

The safety notice of each category is written into its index, for the toolkit to say first: carbon monoxide
(generators outdoors only, 20 feet from the house; get out and call 911 if a CO alarm sounds), never back-feed (a
transfer switch or interlock installed by a licensed electrician), DC arcs, roof falls, battery fires, rotating
blades and wheels, and electric shock.
"""

HEADING = "Power and electrical"

GENERATOR_NOTICE = ("Read the safety section first. Run a generator only outdoors, at least 20 feet from the house with "
                    "its exhaust away from windows, doors and vents: its carbon monoxide can kill. Have a carbon "
                    "monoxide alarm; if it sounds or anyone feels dizzy or sick, get out to fresh air and call 911. "
                    "Never plug a generator into a wall or dryer outlet (back-feeding can kill utility line workers): "
                    "connect to house wiring only through a transfer switch or interlock kit installed by a licensed "
                    "electrician. Let the engine cool before refuelling, keep it dry, and guard belts and rotating "
                    "parts on home-made and PTO generators.")
SOLAR_NOTICE = ("Read the safety section first. Solar panels make electricity whenever light falls on them and DC "
                "wiring can arc and shock: turn off the disconnects before touching wiring, and use fall protection "
                "on roofs. Large batteries can start fires (lithium thermal runaway, hydrogen from lead-acid): fuse "
                "every circuit, ventilate, and never charge a swollen battery. Connecting to the house and the grid is "
                "work for a licensed electrician, with the permits and inspection your town requires.")
WIND_HYDRO_NOTICE = ("Read the safety section first. Turbine blades and water wheels can kill: stop and brake the "
                     "turbine before going near it. Climb or tilt a tower only with fall protection and a partner, "
                     "never in a storm (lightning). Water intakes and penstocks hold strong currents; water rights and "
                     "permits are set by each state. Connecting to the house and the grid is work for a licensed "
                     "electrician.")
HOME_ELECTRICAL_NOTICE = ("Read the safety section first. Turn the power off at the breaker and check it is off with a "
                          "tester before touching wiring; do not overload or chain power strips and extension cords. "
                          "If someone has had an electric shock, do not touch them until the power is off, then call "
                          "911. Work inside the breaker panel, and anything you are unsure of, is for a licensed "
                          "electrician.")

GENERATOR_WORDS = ["generator set", "genset", "tri fuel generator", "propane generator", "natural gas generator",
                   "rv generator", "onan", "pto generator", "welder generator", "generator head", "power take off",
                   "diesel generator", "gasoline generator"]
SOLAR_WORDS = ["solar panel", "charge controller", "mppt", "solar inverter", "grid tie inverter", "power inverter",
               "microinverter", "deep cycle battery", "lifepo4", "battery monitor", "battery management system",
               "solar kit"]
WIND_HYDRO_WORDS = ["wind turbine", "wind generator", "wind charger", "windmill", "aermotor", "micro hydro",
                    "water turbine", "pelton", "hydro generator"]
HOME_ELECTRICAL_WORDS = ["surge protector", "power strip", "extension cord", "electrical panel", "breaker panel",
                         "voltage detector", "outlet tester"]

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is listed "
        "for the person to open or fetch with Program Downloader")


def _makers(category, prefix, documents, makers):
    """The makers of one category (all link-only), with the shared fields."""
    return [dict(category=category, prefix=prefix, types=[], documents=documents, access="link", reason=RULE, **m)
            for m in makers]


# Generac, Champion, Honda, Westinghouse, Kohler, Reliance Controls, Jackery, EcoFlow, BLUETTI, Anker SOLIX, APC and
# CyberPower are linked by the preparedness collection emergency_power (under the same heading): not repeated.
GENERATOR_MAKERS = _makers("backup_generators", "bg", "owner's, installation and service manuals", [
    dict(key="briggs-stratton-power", maker="Briggs & Stratton (portable and standby generators)",
         type="generator", library="https://www.briggsandstratton.com/na/en_us/support/manuals.html",
         site="briggsandstratton.com"),
    dict(key="cummins-onan", maker="Cummins (Onan RV and home generators)", type="generator",
         library="https://www.cummins.com/generators", site="cummins.com"),
    dict(key="yamaha-generators", maker="Yamaha (inverter generators)", type="generator",
         library="https://yamahamotorsports.com/generators", site="yamahamotorsports.com"),
    dict(key="duromax", maker="DuroMax (dual-fuel generators)", type="generator", library="https://www.duromaxpower.com/",
         site="duromaxpower.com"),
    dict(key="firman", maker="Firman (portable and tri-fuel generators)", type="generator",
         library="https://firmanpowerequipment.com/", site="firmanpowerequipment.com"),
    dict(key="winco", maker="WINCO (PTO and standby generators)", type="generator", library="https://wincogen.com/",
         site="wincogen.com"),
    dict(key="miller-welders", maker="Miller Electric (engine-driven welder generators)", type="welder generator",
         library="https://www.millerwelds.com/support/manuals-and-parts", site="millerwelds.com"),
    dict(key="lincoln-electric", maker="Lincoln Electric (engine-driven welder generators)", type="welder generator",
         library="https://www.lincolnelectric.com/en/support/manuals", site="lincolnelectric.com"),
    dict(key="generlink", maker="GenerLink (meter-socket transfer switch)", type="transfer switch",
         library="https://www.generlink.com/", site="generlink.com"),
    dict(key="ford-pro-power", maker="Ford (Pro Power Onboard and F-150 Lightning Intelligent Backup Power)",
         type="vehicle power", library="https://www.ford.com/support/", site="ford.com"),
    dict(key="gm-energy", maker="GM Energy (vehicle-to-home power for GM electric vehicles)", type="vehicle power",
         library="https://www.gmenergy.gm.com/", site="gmenergy.gm.com"),
])
SOLAR_MAKERS = _makers("solar_battery_power", "sb", "manuals, installation guides and data sheets", [
    dict(key="renogy", maker="Renogy", type="solar panel, charge controller and battery",
         library="https://www.renogy.com/", site="renogy.com"),
    dict(key="victron", maker="Victron Energy", type="inverter, charge controller and battery monitor",
         library="https://www.victronenergy.com/support-and-downloads/manuals", site="victronenergy.com"),
    dict(key="enphase", maker="Enphase Energy", type="microinverter and home battery",
         library="https://enphase.com/installers/resources/documentation", site="enphase.com"),
    dict(key="solaredge", maker="SolarEdge", type="inverter and power optimiser",
         library="https://www.solaredge.com/us/support", site="solaredge.com"),
    dict(key="tesla-energy", maker="Tesla (Powerwall)", type="home battery",
         library="https://www.tesla.com/support/energy", site="tesla.com"),
    dict(key="battle-born", maker="Battle Born Batteries", type="LiFePO4 battery",
         library="https://battlebornbatteries.com/", site="battlebornbatteries.com"),
    dict(key="sma", maker="SMA Solar Technology", type="inverter", library="https://www.sma-america.com/",
         site="sma-america.com"),
    dict(key="fronius", maker="Fronius", type="inverter", library="https://www.fronius.com/en-us/usa/solar-energy",
         site="fronius.com"),
    dict(key="schneider-solar", maker="Schneider Electric (Conext solar inverters)", type="inverter",
         library="https://solar.se.com/us/en/", site="solar.se.com"),
    dict(key="outback-power", maker="OutBack Power", type="off-grid inverter and charge controller",
         library="https://www.outbackpower.com/", site="outbackpower.com"),
    dict(key="magnum-energy", maker="Magnum Energy (Sensata)", type="inverter-charger",
         library="https://www.magnum-dimensions.com/", site="magnum-dimensions.com"),
    dict(key="midnite-solar", maker="MidNite Solar", type="charge controller and combiner box",
         library="https://www.midnitesolar.com/", site="midnitesolar.com"),
    dict(key="morningstar", maker="Morningstar", type="charge controller", library="https://www.morningstarcorp.com/",
         site="morningstarcorp.com"),
    dict(key="sol-ark", maker="Sol-Ark", type="hybrid inverter", library="https://www.sol-ark.com/", site="sol-ark.com"),
    dict(key="eg4", maker="EG4 Electronics", type="hybrid inverter and battery", library="https://eg4electronics.com/",
         site="eg4electronics.com"),
    dict(key="franklinwh", maker="FranklinWH", type="home battery", library="https://www.franklinwh.com/",
         site="franklinwh.com"),
])
WIND_HYDRO_MAKERS = _makers("wind_hydro_power", "wh", "owner's and installation manuals", [
    dict(key="bergey", maker="Bergey Windpower", type="small wind turbine", library="https://www.bergey.com/",
         site="bergey.com"),
    dict(key="primus-wind", maker="Primus Wind Power (AIR wind turbines)", type="small wind turbine",
         library="https://www.primuswindpower.com/", site="primuswindpower.com"),
    dict(key="aermotor", maker="Aermotor Windmill Company", type="water-pumping windmill",
         library="https://www.aermotorwindmill.com/", site="aermotorwindmill.com"),
    dict(key="powerspout", maker="PowerSpout", type="micro-hydro turbine", library="https://www.powerspout.com/",
         site="powerspout.com"),
    dict(key="es-and-d", maker="Energy Systems & Design (Stream Engine micro-hydro)", type="micro-hydro turbine",
         library="https://www.microhydropower.com/", site="microhydropower.com"),
    dict(key="scoraig-wind", maker="Hugh Piggott (Scoraig Wind: axial-flux wind turbine books and plans, copyright)",
         type="wind turbine plans", library="https://www.scoraigwind.co.uk/", site="scoraigwind.co.uk"),
])
HOME_ELECTRICAL_MAKERS = _makers("home_electrical", "he", "instructions and data sheets", [
    dict(key="leviton", maker="Leviton", type="outlet, switch and surge protector", library="https://leviton.com/",
         site="leviton.com"),
    dict(key="eaton", maker="Eaton", type="breaker panel and surge protector", library="https://www.eaton.com/",
         site="eaton.com"),
    dict(key="square-d", maker="Square D (Schneider Electric)", type="breaker panel",
         library="https://www.se.com/us/en/", site="se.com"),
    dict(key="tripp-lite", maker="Tripp Lite (Eaton)", type="surge protector and power strip",
         library="https://tripplite.eaton.com/", site="tripplite.eaton.com"),
    dict(key="klein-tools", maker="Klein Tools", type="voltage tester and outlet tester",
         library="https://www.kleintools.com/", site="kleintools.com"),
])


def _guide(ia, title, by, year, military=False):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military manual (judged by the release rule, military_release.py; build_manuals.public_guide_entries)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


GENERATOR_GUIDES = [
    _guide("fm-5-424-theater-of-operations-electrical-systems-1997", "Theater of Operations Electrical Systems "
           "(FM 5-424, 1997)", "the US Army", 1997, True),
    _guide("5kw-mep-802-tqg-9-6115-641-10-oct-09-pin-071025", "Operator's Manual, 5 kW Tactical Quiet Generator "
           "MEP-802A (TM 9-6115-641-10, 2009)", "the US Army", 2009, True),
    _guide("5-kw-mep-1030-ammps-tm-9-6115-749-10-pin-086624-1-feb-11", "Operator's Manual, 5 kW AMMPS MEP-1030 "
           "(TM 9-6115-749-10, 2011)", "the US Army", 2011, True),
    _guide("mep804amep814atechnicalmanualoperatorsmanualtm9611564310", "Operator's Manual, 15 kW Tactical Quiet "
           "Generators MEP-804A and MEP-814A (TM 9-6115-643-10, 2010)", "the US Army", 2010, True),
]
HOME_ELECTRICAL_GUIDES = [
    _guide("DTIC_ADA400134", "Controlling Electrical Hazards (OSHA 3075, 1997)",
           "the US Occupational Safety and Health Administration", 1997),
]

LICENCE = "CC0 (facts and links); each manual belongs to its maker; the guidance pages are US government works"
CATEGORIES = {
    "backup_generators": dict(
        name="Backup generators, PTO and welder generators, and vehicle power (manuals)",
        description="Generator sets and gensets, tri-fuel, propane and natural gas generators, RV generators, PTO "
                    "(power take-off) and welder generators, generator heads for home-built sets, and vehicle "
                    "power (pickup truck onboard power and electric vehicle home backup): the Internet Archive's "
                    "manuals, the makers' pages as links, the US Army's generator manuals, and the government "
                    "guidance. Portable, inverter and home standby generators and transfer switches are in Emergency "
                    "preparedness (emergency_power), under the same heading.",
        kind="manuals", licence=LICENCE, any_year=True, ia=GENERATOR_WORDS, makers=GENERATOR_MAKERS,
        notice=GENERATOR_NOTICE, public_guides=GENERATOR_GUIDES, heading=HEADING,
        ia_exclude=r"\b(sega|video game|game manual|signal generator|function generator|lucas ?arts|van de graaff|"
                   r"steam generator)\b",
        guidance=[dict(title="Generator safety and the electrical systems manual (in the reference library: "
                             "backup-power, power:army_fm_5_424_electrical_systems_1997)",
                       url="https://archive.org/details/fm-5-424-theater-of-operations-electrical-systems-1997",
                       by="the US Army"),
                  dict(title="Portable generator safety (CPSC; open it in a browser: it refuses programs)",
                       url="https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Portable-Generators",
                       by="the US Consumer Product Safety Commission"),
                  dict(title="Use a generator safely (CDC; in the reference library: outcook:cdc_food_power_outage)",
                       url="https://www.cdc.gov/natural-disasters/psa-toolkit/use-a-generator-safely.html",
                       by="the US Centers for Disease Control and Prevention"),
                  dict(title="National Electrical Code (NFPA 70; copyright, free to read after signing in)",
                       url="https://www.nfpa.org/codes-and-standards/nfpa-70-standard-development/70",
                       by="the National Fire Protection Association")]),
    "solar_battery_power": dict(
        name="Solar panels, charge controllers, inverters and battery banks (manuals)",
        description="Solar panels, PWM and MPPT charge controllers, solar, grid-tie, off-grid and micro inverters "
                    "and optimisers, deep-cycle, AGM, gel and LiFePO4 batteries, battery monitors and management "
                    "systems, home batteries and solar kits for homes, cabins, RVs, vans and boats: the Internet "
                    "Archive's manuals, the makers' pages as links (Renogy, Victron, Enphase, SolarEdge, Tesla, "
                    "Battle Born and others), and the Department of Energy's solar guidance.",
        kind="manuals", licence=LICENCE, any_year=True, ia=SOLAR_WORDS, makers=SOLAR_MAKERS, notice=SOLAR_NOTICE,
        heading=HEADING, ia_exclude=r"\b(sega|video game|game manual|solar system|calculator)\b",
        guidance=[dict(title="Homeowner's Guide to Solar (DOE; in the reference library: "
                             "power:doe_homeowners_guide_solar)",
                       url="https://www.energy.gov/cmei/systems/homeowners-guide-solar", by="the US Department of Energy"),
                  dict(title="PVWatts calculator: how much electricity solar panels would make (NREL/NLR; a web "
                             "tool to open in a browser)", url="https://pvwatts.nrel.gov/",
                       by="the National Laboratory of the Rockies (formerly NREL)"),
                  dict(title="Before You Buy Solar Panels (US Treasury; in the reference library: "
                             "power:treasury_before_you_buy_solar)",
                       url="https://home.treasury.gov/system/files/136/Guide-Before-You-Buy-Solar-Panels-eng.pdf",
                       by="the US Department of the Treasury"),
                  dict(title="About Form 5695, Residential Energy Credits (IRS)",
                       url="https://www.irs.gov/forms-pubs/about-form-5695", by="the Internal Revenue Service"),
                  dict(title="DSIRE: state incentives, net metering and interconnection rules (NC Clean Energy "
                             "Technology Center; open it in a browser)", url="https://www.dsireusa.org/",
                       by="the NC Clean Energy Technology Center")]),
    "wind_hydro_power": dict(
        name="Small wind turbines, windmills and micro-hydro (manuals)",
        description="Small wind turbines and wind generators, wind chargers, water-pumping windmills, micro-hydro "
                    "and pico-hydro turbines (Pelton, Turgo, cross-flow) and hydro generators: the Internet "
                    "Archive's manuals, the makers' pages as links (Bergey, Primus Wind Power, Aermotor, PowerSpout, "
                    "Energy Systems & Design; Hugh Piggott's plans as a link), and the Department of Energy's small "
                    "wind and hydropower guidance.",
        kind="manuals", licence=LICENCE, any_year=True, ia=WIND_HYDRO_WORDS, makers=WIND_HYDRO_MAKERS,
        notice=WIND_HYDRO_NOTICE, heading=HEADING, ia_exclude=r"\b(sega|video game|game manual|windows|quadrille|dental|pelton & crane|lego|"
                   r"song|sheet music)\b",
        guidance=[dict(title="Small Wind Guidebook (WINDExchange, DOE; in the reference library: power:doe_small_wind)",
                       url="https://www.energy.gov/cmei/systems/windexchange/small-wind-guidebook",
                       by="the US Department of Energy"),
                  dict(title="Wind maps and data (WINDExchange, DOE)",
                       url="https://www.energy.gov/cmei/systems/windexchange/maps-and-data",
                       by="the US Department of Energy"),
                  dict(title="How hydropower works and the kinds of turbines (DOE; in the reference library: "
                             "power:doe_hydropower_basics)", url="https://www.energy.gov/cmei/water/how-hydropower-works",
                       by="the US Department of Energy"),
                  dict(title="Small and low-impact hydropower: when a federal licence is needed (FERC)",
                       url="https://www.ferc.gov/industries-data/hydropower", by="the Federal Energy Regulatory "
                                                                                 "Commission")]),
    "home_electrical": dict(
        name="Home electrical: surge protectors, power strips, extension cords, panels and testers (manuals)",
        description="Surge protectors, power strips, extension cords, breaker panels and voltage and outlet "
                    "testers: the Internet Archive's manuals, the makers' pages as links, OSHA's Controlling "
                    "Electrical Hazards, and the electrical safety and shock first aid guidance. Outlets, switches, "
                    "GFCIs and breakers are in Electrical devices (electrical_devices), under the same heading.",
        kind="manuals", licence=LICENCE, any_year=True, ia=HOME_ELECTRICAL_WORDS, makers=HOME_ELECTRICAL_MAKERS,
        notice=HOME_ELECTRICAL_NOTICE, public_guides=HOME_ELECTRICAL_GUIDES, heading=HEADING,
        guidance=[dict(title="Appliance and electrical fire safety (US Fire Administration; in the reference library: "
                             "craft:usfa_home_heating_fire_safety)",
                       url="https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/appliance-and-electrical/",
                       by="the US Fire Administration (FEMA)"),
                  dict(title="Electric shock first aid (in the reference library: the first aid books, key firstaid)",
                       url="https://medlineplus.gov/ency/article/000053.htm", by="MedlinePlus (US National Library "
                                                                                 "of Medicine)"),
                  dict(title="Energy Saver: saving electricity at home (DOE; in the reference library: "
                             "dir:energy_saver_articles)", url="https://www.energy.gov/energysaver/",
                       by="the US Department of Energy")]),
}

# The existing collections that also go under the heading (their keys and contents do not change).
HEADING_KEYS = ("electrical_devices", "batteries", "emergency_power")
