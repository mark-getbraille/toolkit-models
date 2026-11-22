"""Two manual collections for EMERGENCY PREPAREDNESS (the owner's request of 2026-11-22). categories.py adds them to
CATEGORIES, under names that start "Emergency preparedness:" so they sit together in the manuals list:
  emergency_power             portable, inverter and home standby generators, transfer switches and interlock kits,
                              portable power stations and home batteries, UPS battery backups;
  emergency_preparedness_gear emergency and survival kits, fire escape ladders, N95 respirators, and alerting devices
                              for deaf, hard of hearing and blind people (bed shakers, strobe and talking alarms).

What each lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker, as in every
manual collection): the Internet Archive's manuals found with each category's words (IA words that the categories
beside them already use are not repeated: lawn_garden's "generator", emergency_lighting's "power bank", "portable
power station" and "solar generator", home_systems' smoke and carbon monoxide alarms, safety_ppe's "respirator");
the makers' own manual libraries, LINK-ONLY by the owner's rule (nothing is read from their sites; their pages are
listed for the person to open or fetch with Program Downloader); public-domain guides (the Internet Archive's copies
of US government works); and guidance pages, with the reference library's key where the page is already a book.

Already elsewhere and not repeated: generators as garden machines (lawn_garden), small engines (small_engines),
flashlights, lanterns, power banks and power stations for lights (emergency_lighting), smoke and carbon monoxide
alarms and sump pumps (home_systems), respirators as work equipment (safety_ppe), stoves and heaters
(home_heating); weather radios and two-way radios are the radio collections (radio_manuals.py).

Each category's notice is written into its index, for the toolkit to say first: the generator notice (outdoors only,
20 feet from windows and doors, carbon monoxide alarm, get out and call 911, never back-feed: a transfer switch put in
by a licensed electrician) and the officials notice.
"""

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is listed "
        "for the person to open or fetch with Program Downloader")
LICENCE = "CC0 (facts and links); each manual belongs to its maker; the guides are US government works"

# The same words as packs/preparedness_packs.py GENERATOR_NOTE (the self-test checks).
GENERATOR_NOTE = ("Generator safety: run a generator only outdoors, at least 20 feet from the home with its exhaust "
                  "pointed away from windows, doors and vents, never in a home, garage, basement, shed or porch: its "
                  "carbon monoxide can kill in minutes. Have a carbon monoxide alarm, and if it sounds or anyone feels "
                  "dizzy or sick, get out to fresh air and call 911. Never plug a generator into a wall socket "
                  "(back-feeding can kill utility workers and neighbours): use heavy-duty outdoor cords, or a transfer "
                  "switch put in by a licensed electrician. Let it cool before refuelling, and store fuel in approved "
                  "containers away from the home.")
OFFICIALS_NOTE = "Follow your local officials' instructions, and evacuate when they tell you to."
POWER_NOTICE = (GENERATOR_NOTE + " Power stations and home batteries: charge and keep them where the maker says, away "
                "from heat, and never use a swollen or damaged battery. " + OFFICIALS_NOTE)
GEAR_NOTICE = ("Check kits twice a year (water, food, medicines, batteries). An N95 respirator filters smoke and dust "
               "only when it fits well and does not protect against carbon monoxide. Practise with an escape ladder "
               "from a ground-floor window first. " + OFFICIALS_NOTE + " In danger, call 911.")

POWER_WORDS = ["inverter generator", "standby generator", "home standby", "transfer switch", "interlock kit",
               "generator transfer", "uninterruptible power supply", "ups battery backup", "ups battery", "home battery",
               "solar power station", "portable generator", "dual fuel generator", "generator manual"]
GEAR_WORDS = ["emergency kit", "survival kit", "fire escape ladder", "escape ladder", "n95", "bed shaker",
              "vibrating alarm", "strobe alarm", "emergency whistle", "go bag", "weather alert receiver for deaf",
              "visual alert"]


def _makers(category, prefix, documents, makers):
    """The makers of one category (all link-only), with the shared fields."""
    return [dict(category=category, prefix=prefix, types=[], documents=documents, access="link", reason=RULE, **m)
            for m in makers]


POWER_MAKERS = _makers("emergency_power", "ep", "owner's and installation manuals", [
    dict(key="generac", maker="Generac (portable and home standby generators, transfer switches, PWRcell)",
         type="generator", library="https://www.generac.com/support/product-support-lookup/", site="generac.com"),
    dict(key="champion", maker="Champion Power Equipment", type="generator",
         library="https://www.championpowerequipment.com/", site="championpowerequipment.com"),
    dict(key="honda-power", maker="Honda Power Equipment (generators)", type="generator",
         library="https://powerequipment.honda.com/support/manuals", site="powerequipment.honda.com"),
    dict(key="westinghouse-outdoor", maker="Westinghouse Outdoor Power Equipment", type="generator",
         library="https://westinghouseoutdoorpower.com/", site="westinghouseoutdoorpower.com"),
    dict(key="kohler-generators", maker="Kohler Home Generators", type="generator",
         library="https://www.kohlerenergy.com/", site="kohlerenergy.com"),
    dict(key="reliance-controls", maker="Reliance Controls (transfer switches)", type="transfer switch",
         library="https://reliancecontrols.com/", site="reliancecontrols.com"),
    dict(key="jackery", maker="Jackery", type="portable power station", library="https://www.jackery.com/",
         site="jackery.com"),
    dict(key="ecoflow", maker="EcoFlow", type="portable power station", library="https://us.ecoflow.com/",
         site="ecoflow.com"),
    dict(key="bluetti", maker="BLUETTI", type="portable power station", library="https://www.bluettipower.com/",
         site="bluettipower.com"),
    dict(key="anker-solix", maker="Anker SOLIX", type="portable power station", library="https://www.ankersolix.com/",
         site="ankersolix.com"),
    dict(key="apc", maker="APC by Schneider Electric (UPS)", type="UPS battery backup",
         library="https://www.apc.com/us/en/support/", site="apc.com"),
    dict(key="cyberpower", maker="CyberPower (UPS)", type="UPS battery backup", library="https://www.cyberpowersystems.com/",
         site="cyberpowersystems.com"),
])
GEAR_MAKERS = _makers("emergency_preparedness_gear", "eg", "instructions and manuals", [
    dict(key="3m-respirators", maker="3M (N95 respirators: fitting and user instructions)", type="respirator",
         library="https://www.3m.com/3M/en_US/respirator-selection-guide-us/", site="3m.com"),
    dict(key="first-alert-ladders", maker="First Alert (escape ladders)", type="fire escape ladder",
         library="https://www.firstalert.com/", site="firstalert.com"),
    dict(key="kidde-ladders", maker="Kidde (escape ladders)", type="fire escape ladder", library="https://www.kidde.com/",
         site="kidde.com"),
    dict(key="ready-america", maker="Ready America (emergency kits)", type="emergency kit",
         library="https://www.readyamerica.com/", site="readyamerica.com"),
    dict(key="bellman-symfon", maker="Bellman & Symfon (alerting systems for deaf and hard of hearing people)",
         type="visual and vibrating alert", library="https://www.bellman.com/", site="bellman.com"),
    dict(key="lifetone", maker="Lifetone (bed shaker smoke alarm alerts)", type="bed shaker alert",
         library="https://www.lifetonetechnology.com/", site="lifetonetechnology.com"),
    dict(key="serene-innovations", maker="Serene Innovations (amplified and visual alerts)", type="visual alert",
         library="https://sereneinnovations.com/", site="sereneinnovations.com"),
])


def _guide(ia, title, by, year, military=False):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military manual (the shared check of build_manuals.public_guide_entries reads its front text; the owner's rule of
    2026-11-22, being put into that check on another branch, keeps a manual with no distribution statement too)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


GEAR_GUIDES = [
    _guide("fm-21-76-survival-manual", "US Army Survival Manual (FM 21-76, 1992)", "the US Army", 1992, True),
    _guide("fema-hs-4-preparedness-planning-for-a-nuclear-crisis-1987", "Preparedness Planning for a Nuclear Crisis "
           "(FEMA HS-4, 1987)", "the Federal Emergency Management Agency", 1987),
]

CATEGORIES = {
    "emergency_power": dict(
        name="Emergency preparedness: generators, transfer switches, power stations and battery backups (manuals)",
        description="Backup power for outages: portable, inverter and home standby generators, transfer switches "
                    "and interlock kits, portable power stations and home batteries, and UPS battery backups for "
                    "computers and medical equipment: the Internet Archive's manuals, the makers' manual pages as "
                    "links, and the safety guidance.",
        kind="manuals", licence=LICENCE, any_year=True, ia=POWER_WORDS, makers=POWER_MAKERS, notice=POWER_NOTICE,
        ia_exclude=r"\b(sega|video game|game manual|signal generator|function generator|lucas ?arts|imac|macbook|"
                   r"iphone|ipad|laptop)\b",
        guidance=[dict(title="Power outages (Ready.gov; in the reference library: ready:ready_gov)",
                       url="https://www.ready.gov/power-outages", by="the Federal Emergency Management Agency"),
                  dict(title="Fire safety in severe weather and power outages, generators (US Fire Administration; in "
                             "the reference library: craft:usfa_home_heating_fire_safety)",
                       url="https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/severe-weather/",
                       by="the US Fire Administration (FEMA)"),
                  dict(title="Portable generator safety (CPSC; open it in a browser)",
                       url="https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Portable-Generators",
                       by="the US Consumer Product Safety Commission"),
                  dict(title="HHS emPOWER and power-dependent equipment (in the reference library: "
                             "ready:aspr_at_risk_empower)", url="https://empowerprogram.hhs.gov/",
                       by="the US Department of Health and Human Services")]),
    "emergency_preparedness_gear": dict(
        name="Emergency preparedness: kits, escape ladders, respirators and alerts for deaf and blind people (manuals)",
        description="Emergency and survival kits, fire escape ladders, N95 respirators, and alerting devices for "
                    "deaf, hard of hearing and blind people (bed shakers, strobe and vibrating alerts): the Internet "
                    "Archive's instructions, the makers' pages as links, the US Army survival manual and FEMA's "
                    "nuclear preparedness guide (public domain), and Ready.gov's guidance.",
        kind="manuals", licence=LICENCE, any_year=True, ia=GEAR_WORDS, makers=GEAR_MAKERS, notice=GEAR_NOTICE,
        public_guides=GEAR_GUIDES,
        ia_exclude=r"\b(sega|video game|game manual|lucas ?arts|zombie)\b",
        guidance=[dict(title="Build a kit (Ready.gov; in the reference library: ready:ready_gov)",
                       url="https://www.ready.gov/kit", by="the Federal Emergency Management Agency"),
                  dict(title="People with disabilities (Ready.gov; in the reference library: ready:ready_gov)",
                       url="https://www.ready.gov/people-disabilities",
                       by="the Federal Emergency Management Agency"),
                  dict(title="Where to find more: the Church's home storage guidance, USU Extension, Red Cross (in "
                             "the reference library: ready:where_to_find_more)",
                       url="https://providentliving.churchofjesuschrist.org/food-storage",
                       by="The Church of Jesus Christ of Latter-day Saints (link only: its terms forbid copying by "
                          "program)")]),
}
