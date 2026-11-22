"""The collection "Car care and maintenance (guides and manuals)" (category key car_care), the owner's life-skills
request of 2026-11-22. categories.py adds it to CATEGORIES. Owner's manuals by car model stay in the category "cars".

What it lists, in plain words (an INDEX of facts and links only; each document belongs to its maker):
  ia             the Internet Archive's manual collections, searched by the words in IA_WORDS (maintenance and
                 service schedules, tyre and battery guides, jump starters, tyre inflators, EV chargers, dash cams);
  public_guides  US Army automotive manuals, each the Internet Archive's copy, kept when the item has a PDF and,
                 being military, judged by the release rule for military publications (military_release.py, the
                 owner's decision of 22 November 2026; build_manuals.public_guide_entries at every build): indexed
                 with or without Distribution Statement A, with a truthful release line; link only and personal use
                 when it prints a restricted marking: Principles of Automotive Vehicles (TM 9-2700, 1947) and the
                 Driver's Manual (TM 21-305, 1944);
  makers         tyre, battery, jump starter, charger and EV charger makers: by the owner's rule their own guides and
                 manuals are LINK-ONLY, for the person (or the personal assistant) to open; nothing is read;
  guidance       NHTSA's and the DOE's own pages (US government works, but their sites refuse programs or carry no
                 licence: linked for the person to open).

The safety notice is said first (CAR_SAFETY).
"""

CAR_SAFETY = ("Never get under a car held up only by a jack: use jack stands on firm, level ground. Let a hot engine "
              "cool before opening the radiator cap. Battery acid burns and batteries give off explosive gas: wear eye "
              "protection and follow the order of the jump leads in your car's handbook. If you break down, get off "
              "the road, turn on the hazard lights and call for help (911 in an emergency).")

IA_WORDS = ["maintenance schedule", "service schedule", "maintenance guide", "car care", "tire inflator",
            "tyre inflator", "jump starter", "jump pack", "battery charger", "battery maintainer", "trickle charger",
            "ev charger", "wallbox", "charging station", "level 2 charger", "tire pressure gauge", "obd2", "obd-ii",
            "code reader", "dash cam", "dashcam", "roadside emergency kit"]

RULE = ("by the owner's rule the maker's own guides and manuals are link-only: nothing is read from its site; its "
        "page is listed for the person to open")
_COMMON = dict(category="car_care", prefix="cc", documents="guides and manuals", access="link", reason=RULE,
               types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="michelin", maker="Michelin", type="tyres (care and safety guides)",
         library="https://www.michelinman.com/auto/tire-advice", site="michelinman.com"),
    dict(key="goodyear", maker="Goodyear", type="tyres (care and safety guides)",
         library="https://www.goodyear.com/en_US/learn", site="goodyear.com"),
    dict(key="bridgestone", maker="Bridgestone", type="tyres (care and safety guides)",
         library="https://www.bridgestonetire.com/learn/", site="bridgestonetire.com"),
    dict(key="interstate", maker="Interstate Batteries", type="car batteries",
         library="https://www.interstatebatteries.com/",
         site="interstatebatteries.com"),
    dict(key="noco", maker="NOCO", type="jump starters and battery chargers", library="https://no.co/support",
         site="no.co"),
    dict(key="schumacher", maker="Schumacher Electric", type="battery chargers and jump starters",
         library="https://www.batterychargers.com/", site="batterychargers.com"),
    dict(key="chargepoint", maker="ChargePoint", type="EV chargers", library="https://www.chargepoint.com/support",
         site="chargepoint.com"),
    dict(key="tesla-charging", maker="Tesla (Wall Connector and charging)", type="EV chargers",
         library="https://www.tesla.com/support/charging", site="tesla.com"),
    dict(key="rain-x", maker="Rain-X", type="wiper blades and washer fluid", library="https://www.rainx.com/",
         site="rainx.com"),
    dict(key="bosch-auto", maker="Bosch Automotive (wipers, bulbs)", type="wiper blades and car parts",
         library="https://www.boschautoparts.com/", site="boschautoparts.com"),
]]

GUIDANCE = [
    dict(title="Tires: tire safety, tread, pressure and the sidewall (NHTSA; open it in a browser: it refuses "
               "programs)", url="https://www.nhtsa.gov/equipment/tires",
         by="the US National Highway Traffic Safety Administration"),
    dict(title="Recalls: check a vehicle by its VIN (NHTSA; the recalls are in the reference library)",
         url="https://www.nhtsa.gov/recalls", by="the US National Highway Traffic Safety Administration"),
    dict(title="Keeping your vehicle in shape (FuelEconomy.gov, DOE and EPA)",
         url="https://www.fueleconomy.gov/feg/maintain.jsp", by="the US Department of Energy"),
    dict(title="Electric vehicle charging at home (Alternative Fuels Data Center, DOE)",
         url="https://afdc.energy.gov/fuels/electricity-charging-home", by="the US Department of Energy"),
]


def _guide(ia, title, by, year, military=False):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military manual (judged by the release rule for military publications (military_release.py, the owner's decision of 22 November 2026); build_manuals.public_guide_entries)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


PUBLIC_GUIDES = [
    _guide("TM9-2700", "Principles of Automotive Vehicles (TM 9-2700, 1947)", "the US Army", 1947, True),
    _guide("TM21-305", "Driver's Manual (TM 21-305, 1944)", "the US Army", 1944, True),
]

CATEGORY = dict(
    name="Car care and maintenance (guides and manuals)",
    description="Looking after a car: maintenance schedules, tyres (pressure, tread, the sidewall), batteries, jump "
                "starters and chargers, tyre inflators and gauges, code readers, wipers and bulbs, EV home chargers "
                "and roadside kits: the Internet Archive's manuals, the US Army's public automotive manuals, the "
                "makers' guides (links) and NHTSA's and the DOE's pages (links). Owner's manuals by car model are in "
                "the category Cars.",
    kind="manuals", licence="CC0 (facts and links); the US Army manuals are public domain; each other document "
                            "belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, public_guides=PUBLIC_GUIDES, notice=CAR_SAFETY)
