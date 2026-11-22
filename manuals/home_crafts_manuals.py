"""Three manual collections for home upkeep and the textile crafts (the owner's request of 2026-11-22: home repair,
upkeep and handcrafts). categories.py adds them to CATEGORIES:
  bicycles             bicycle owner's, service and repair manuals: the Internet Archive's manuals searched with
                       BIKE_WORDS, the makers' and Park Tool's pages as links, and the US government's bicycle safety
                       pages as guidance;
  small_engines        small engine owner's and repair manuals (lawn mower, snow blower, generator and garden machine
                       engines): the Internet Archive's manuals searched with ENGINE_WORDS, the engine makers' pages as
                       links, and the carbon monoxide and generator safety pages;
  textile_craft_tools  knitting machines, spinning wheels, looms, longarm quilting machines and old sewing machines'
                       instruction books: the Internet Archive's manuals searched with CRAFT_WORDS and the makers'
                       pages as links. (Modern sewing machines, sergers and embroidery machines are already the
                       category sewing_textile, with SINGER, Brother, Janome, JUKI, BERNINA, Baby Lock and PFAFF.)

What each lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker, as in every
manual collection): by the owner's rule for these collections the makers' own manual libraries are LINK-ONLY, as in
home_health_tests.py: nothing is read from their sites, their pages are listed for the person (or the personal
assistant) to open. Already elsewhere and not repeated: lawn mowers, snow blowers, generators and chainsaws as
machines (lawn_garden, with Honda Power Equipment and the other outdoor makers), motorcycles and Briggs & Stratton's
Internet Archive collection (powersports), door locks (door_hardware_locks), faucets and toilet parts
(plumbing_fittings), furnaces and water heaters (home_appliances) and pesticide labels (pest_control,
pesticide_labels).

  home_heating         stoves, fireplaces and space heaters for emergency and secondary heat (the coordinator's
                       addition of 2026-11-22), with the carbon monoxide, 3-feet and gas-professional notice;
  emergency_lighting   flashlights, lanterns, lamps, glow sticks and power banks (added the same day), with the fuel
                       lamp notice.

The safety notice of each category is written into its index, for the toolkit to say first.
"""

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is listed "
        "for the person to open")

BIKE_NOTICE = ("Check the brakes and that the wheels are tight before every ride, and wear a helmet. Have brakes, "
               "suspension and electric-bike batteries serviced by a bicycle shop if you are not sure.")
ENGINE_NOTICE = ("Read the safety section first. Run engines only outdoors, far from windows and doors (exhaust carbon "
                 "monoxide can kill); let the engine cool before refuelling; disconnect the spark plug before working "
                 "on a blade.")
CRAFT_NOTICE = ("Unplug machines before threading, oiling or changing needles; keep fingers clear of moving needles, "
                "hooks and carriages.")

BIKE_WORDS = ["bicycle", "bicycle repair", "bicycle maintenance", "bike manual", "derailleur", "shimano", "sram",
              "campagnolo", "electric bicycle", "e-bike", "tricycle", "tandem bicycle", "bicycle owner's manual"]
ENGINE_WORDS = ["small engine", "small engines", "briggs & stratton", "briggs and stratton", "tecumseh",
                "kohler engine",
                "honda engine", "kawasaki engine", "two-cycle engine", "four-cycle engine", "lawn mower engine",
                "engine repair manual"]
CRAFT_WORDS = ["knitting machine", "spinning wheel", "loom", "weaving loom", "quilting frame", "longarm",
               "sewing machine instructions", "treadle sewing machine", "singer instructions", "knitting",
               "crochet"]


def _makers(category, prefix, documents, makers):
    """The makers of one category (all link-only), with the shared fields."""
    return [dict(category=category, prefix=prefix, types=[], documents=documents, access="link", reason=RULE, **m)
            for m in makers]


BIKE_MAKERS = _makers("bicycles", "bk", "owner's and service manuals", [
    dict(key="park-tool", maker="Park Tool (repair help)", type="bicycle repair guide",
         library="https://www.parktool.com/en-us/blog/repair-help", site="parktool.com"),
    dict(key="shimano", maker="Shimano", type="bicycle components",
         library="https://si.shimano.com/", site="si.shimano.com"),
    dict(key="sram", maker="SRAM", type="bicycle components", library="https://www.sram.com/en/service",
         site="sram.com"),
    dict(key="trek", maker="Trek", type="bicycle", library="https://www.trekbikes.com/us/en_US/manuals/",
         site="trekbikes.com"),
    dict(key="specialized", maker="Specialized", type="bicycle", library="https://www.specialized.com/us/en",
         site="specialized.com"),
    dict(key="giant", maker="Giant", type="bicycle", library="https://www.giant-bicycles.com/us/manuals",
         site="giant-bicycles.com"),
    dict(key="schwinn", maker="Schwinn", type="bicycle", library="https://www.schwinnbikes.com/",
         site="schwinnbikes.com"),
    dict(key="bosch-ebike", maker="Bosch eBike Systems", type="electric bicycle drive",
         library="https://www.bosch-ebike.com/us", site="bosch-ebike.com"),
])
ENGINE_MAKERS = _makers("small_engines", "se", "owner's and repair manuals", [
    dict(key="briggs-stratton", maker="Briggs & Stratton", type="small engine",
         library="https://www.briggsandstratton.com/na/en_us/support/manuals.html", site="briggsandstratton.com"),
    dict(key="kohler-engines", maker="Kohler Engines", type="small engine",
         library="https://www.kohlerengines.com/en/resources/manuals", site="kohlerengines.com"),
    dict(key="honda-engines", maker="Honda Engines", type="small engine",
         library="https://engines.honda.com/", site="engines.honda.com"),
    dict(key="kawasaki-engines", maker="Kawasaki Engines", type="small engine",
         library="https://www.kawasakienginesusa.com/", site="kawasakienginesusa.com"),
    dict(key="generac", maker="Generac", type="generator and engine", library="https://www.generac.com/support/",
         site="generac.com"),
])
CRAFT_MAKERS = _makers("textile_craft_tools", "tc", "manuals and assembly instructions", [
    dict(key="ashford", maker="Ashford", type="spinning wheel and loom",
         library="https://www.ashford.co.nz/", site="ashford.co.nz"),
    dict(key="schacht", maker="Schacht Spindle Company", type="spinning wheel and loom",
         library="https://schachtspindle.com/", site="schachtspindle.com"),
    dict(key="louet", maker="Louët", type="spinning wheel and loom", library="https://www.louet.com/",
         site="louet.com"),
    dict(key="kromski", maker="Kromski", type="spinning wheel and loom", library="https://www.kromski.com/",
         site="kromski.com"),
    dict(key="silver-reed", maker="Silver Reed (knitting machines)", type="knitting machine",
         library="https://www.silver-reed.com/", site="silver-reed.com"),
    dict(key="addi", maker="addi (knitting machines)", type="knitting machine",
         library="https://www.addinadeln.de/", site="addinadeln.de"),
    dict(key="handi-quilter", maker="Handi Quilter", type="longarm quilting machine",
         library="https://handiquilter.com/", site="handiquilter.com"),
    dict(key="gammill", maker="Gammill", type="longarm quilting machine", library="https://www.gammill.com/",
         site="gammill.com"),
])

# Emergency and secondary heating, and emergency and backup lighting (the coordinator's additions of 2026-11-22).
HEAT_NOTICE = ("Heating safety: keep anything that can burn at least 3 feet (1 metre) away. Stoves, fireplaces and "
               "fuel-burning heaters make carbon monoxide, which can kill: have a working carbon monoxide alarm, "
               "never use outdoor heaters, grills or generators indoors, and if the alarm sounds or anyone feels ill "
               "(headache, dizziness, nausea), get everyone out and call 911. Gas lines, gas appliances and stove "
               "installation are work for a qualified professional. Kerosene heaters: clear 1-K kerosene only, never "
               "gasoline; refuel outdoors when cool.")
LIGHT_NOTICE = ("Fuel lamp safety: fuel lanterns and lamps can start fires and make carbon monoxide, which can kill. "
                "Use them outdoors or with good ventilation, as the maker says; never refuel one that is hot or lit; "
                "use only the fuel the lamp is made for; keep it away from children, pets and curtains. Battery lights "
                "are safer indoors during a power cut; never leave a candle burning unattended.")
HEAT_WORDS = ["wood stove", "woodstove", "pellet stove", "kerosene heater", "fireplace insert", "gas fireplace",
              "fireplace", "coal stove", "masonry heater", "outdoor wood furnace", "wood furnace", "wood boiler",
              "vent-free heater", "propane heater", "diesel heater", "oil-filled heater", "multi-fuel stove"]
LIGHT_WORDS = ["flashlight", "headlamp", "kerosene lamp", "kerosene lantern", "pressure lantern", "dual fuel lantern",
               "propane lantern", "petromax", "tilley lamp", "dietz", "lamplight", "mantle lamp", "aladdin lamp",
               "hurricane lamp", "hurricane lantern", "oil lamp", "emergency light", "glow stick", "power bank",
               "portable power station", "solar generator", "solar lantern", "crank flashlight", "candle"]
HEAT_MAKERS = _makers("home_heating", "hh", "owner's and installation manuals", [
    dict(key="harman", maker="Harman (Hearth & Home Technologies)", type="pellet and wood stove",
         library="https://www.harmanstoves.com/", site="harmanstoves.com"),
    dict(key="quadra-fire", maker="Quadra-Fire (Hearth & Home Technologies)", type="wood and pellet stove",
         library="https://www.quadrafire.com/", site="quadrafire.com"),
    dict(key="jotul", maker="Jøtul", type="wood and gas stove", library="https://jotul.com/", site="jotul.com"),
    dict(key="vermont-castings", maker="Vermont Castings", type="wood and gas stove",
         library="https://www.vermontcastings.com/", site="vermontcastings.com"),
    dict(key="lopi", maker="Lopi (Travis Industries)", type="wood, pellet and gas stove",
         library="https://www.lopistoves.com/", site="lopistoves.com"),
    dict(key="pacific-energy", maker="Pacific Energy", type="wood stove", library="https://www.pacificenergy.net/",
         site="pacificenergy.net"),
    dict(key="napoleon", maker="Napoleon", type="fireplace and stove", library="https://www.napoleon.com/",
         site="napoleon.com"),
    dict(key="central-boiler", maker="Central Boiler", type="outdoor wood furnace",
         library="https://centralboiler.com/", site="centralboiler.com"),
    dict(key="mr-heater", maker="Mr. Heater (Enerco)", type="propane heater", library="https://www.mrheater.com/",
         site="mrheater.com"),
    dict(key="dyna-glo", maker="Dyna-Glo (GHP Group)", type="kerosene and propane heater",
         library="https://www.dynaglo.com/", site="dynaglo.com"),
    dict(key="toyotomi", maker="Toyotomi", type="kerosene heater", library="https://www.toyotomiusa.com/",
         site="toyotomiusa.com"),
])
LIGHT_MAKERS = _makers("emergency_lighting", "el", "manuals and instructions", [
    dict(key="coleman", maker="Coleman (its Internet Archive manuals are in Camping and outdoor gear)",
         type="lantern", library="https://www.coleman.com/", site="coleman.com"),
    dict(key="aladdin", maker="Aladdin Mantle Lamp Company", type="mantle lamp",
         library="https://www.aladdinlamps.com/", site="aladdinlamps.com"),
    dict(key="dietz", maker="W.T. Kirkman (Dietz lanterns)", type="hurricane lantern",
         library="https://www.lanternnet.com/", site="lanternnet.com"),
    dict(key="maglite", maker="Maglite", type="flashlight", library="https://maglite.com/", site="maglite.com"),
    dict(key="goal-zero", maker="Goal Zero", type="power station and lantern", library="https://www.goalzero.com/",
         site="goalzero.com"),
    dict(key="eton", maker="Eton (hand-crank radios and lights)", type="hand-crank light",
         library="https://etoncorp.com/", site="etoncorp.com"),
])

LICENCE = "CC0 (facts and links); each manual belongs to its maker; the guidance pages are US government works"
CATEGORIES = {
    "bicycles": dict(
        name="Bicycles (owner's, service and repair manuals)",
        description="Bicycles, electric bicycles, tricycles and tandems and their parts (gears and derailleurs, "
                    "brakes, hubs, suspension): the Internet Archive's owner's and service manuals, and the makers' "
                    "and Park Tool's pages as links.",
        kind="manuals", licence=LICENCE, any_year=True, ia=BIKE_WORDS, makers=BIKE_MAKERS, notice=BIKE_NOTICE,
        ia_exclude=r"\b(fitness|exercise|recumbent bike|stationary|spin bike|elliptical|treadmill|sega|ic|\d+k)\b",
        guidance=[dict(title="Bicycle safety (NHTSA)", url="https://www.nhtsa.gov/road-safety/bicycle-safety",
                       by="the US National Highway Traffic Safety Administration")]),
    "small_engines": dict(
        name="Small engines (owner's and repair manuals)",
        description="The engines of lawn mowers, snow blowers, tillers, pressure washers and generators: Briggs & "
                    "Stratton, Tecumseh, Kohler, Honda and Kawasaki owner's and repair manuals from the Internet "
                    "Archive, and the engine makers' pages as links (the machines themselves are in Lawn, garden "
                    "and outdoor equipment).",
        kind="manuals", licence=LICENCE, any_year=True, ia=ENGINE_WORDS, makers=ENGINE_MAKERS, notice=ENGINE_NOTICE,
        guidance=[dict(title="Carbon monoxide poisoning: prevention (CDC)",
                       url="https://www.cdc.gov/carbon-monoxide/prevention/index.html",
                       by="the US Centers for Disease Control and Prevention"),
                  dict(title="Portable generator safety (CPSC)",
                       url="https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Portable-Generators",
                       by="the US Consumer Product Safety Commission")]),
    "textile_craft_tools": dict(
        name="Knitting machines, spinning wheels, looms and old sewing machines (manuals)",
        description="Knitting machines, spinning wheels, floor and table looms, longarm quilting machines, and the "
                    "instruction books of old and treadle sewing machines: the Internet Archive's manuals, and the "
                    "makers' pages as links (Ashford, Schacht, Louët, Kromski, Silver Reed, addi, Handi "
                    "Quilter, Gammill).",
        kind="manuals", licence=LICENCE, any_year=True, ia=CRAFT_WORDS, makers=CRAFT_MAKERS, notice=CRAFT_NOTICE,
        ia_exclude=r"\b(lucas ?arts|adventure|video game|game manual|handbuch)\b"),
    "home_heating": dict(
        name="Stoves, fireplaces and space heaters for emergency and secondary heat (manuals)",
        description="Wood, pellet, coal and multi-fuel stoves, fireplace inserts and gas fireplaces, masonry heaters, "
                    "outdoor wood furnaces, and propane, kerosene, diesel and oil-filled heaters: the Internet "
                    "Archive's owner's and installation manuals, and the makers' pages as links, with the US Fire "
                    "Administration's and the EPA's guidance.",
        kind="manuals", licence=LICENCE, any_year=True, ia=HEAT_WORDS, makers=HEAT_MAKERS, notice=HEAT_NOTICE,
        ia_exclude=r"\b(gas range|kitchen range|cookstove|cook stove|grill)\b",
        guidance=[dict(title="Heating fire safety (US Fire Administration; in the reference library: "
                             "craft:usfa_home_heating_fire_safety)",
                       url="https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/heating/",
                       by="the US Fire Administration (FEMA)"),
                  dict(title="Burn Wise (EPA; in the reference library: craft:epa_burn_wise)",
                       url="https://www.epa.gov/burnwise", by="the US Environmental Protection Agency"),
                  dict(title="Carbon monoxide (CPSC; open it in a browser)",
                       url="https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-"
                           "Information-Center", by="the US Consumer Product Safety Commission")]),
    "emergency_lighting": dict(
        name="Flashlights, lanterns, lamps and backup power for lights (manuals)",
        description="Flashlights and headlamps, pressure and mantle lanterns, kerosene, hurricane and oil lamps, "
                    "emergency lights, glow sticks, power banks and portable power stations: the Internet Archive's "
                    "manuals, and the makers' pages as links (Coleman's own Internet Archive collection is in Camping "
                    "and outdoor gear).",
        kind="manuals", licence=LICENCE, any_year=True, ia=LIGHT_WORDS, makers=LIGHT_MAKERS, notice=LIGHT_NOTICE,
        ia_exclude=r"\b(lucas ?arts|video game|game manual|candle ?light dinner|magic candle|extras|sega)\b",
        guidance=[dict(title="Candle fire safety (US Fire Administration; in the reference library)",
                       url="https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/candle/",
                       by="the US Fire Administration (FEMA)"),
                  dict(title="Power outages (Ready.gov; open it in a browser)",
                       url="https://www.ready.gov/power-outages", by="the US Federal Emergency Management Agency")]),
}
