"""Picture packs for EMERGENCY PREPAREDNESS AND DISASTERS (the owner's request of 2026-11-22: help him and others
prepare for and get through emergencies). Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes
once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

Already in other packs, and so NOT repeated (packs/test_preparedness.py checks that no Commons category here is named
by another pack file and no Open Images label is asked twice): FEMA's disaster categories (hurricanes, floods,
tornadoes, debris, earthquakes, landslides, wildfires, fires, winter storms, levee breaks, aerial views) and the
earthquake, flood, tornado, landslide and fire damage categories (graphic_packs commons_disasters); downed power
lines, flooded roads, smoke, collapsed buildings, sandbags, evacuation route, emergency exit and assembly point
signs, fallout shelter signs and air-raid sirens (graphic_packs commons_safety); fire extinguishers, first aid kits,
smoke and carbon monoxide alarms, wildfires, sinkholes, icy and flooded roads (events_safety_packs); clouds,
tornadoes, lightning, hail and blizzards in the sky (everyday_extras_packs commons_sky_weather); weather maps and
hurricane forecast cones (weather_map_packs); civil defence booklets and films (civil_defense_packs); diesel
generators and engine-generators, jerrycans, respirators and dust masks, portable power stations and solar chargers
(the device, hardware, chemical and lighting packs); emergency heating and lighting (heating_packs, lighting_packs);
two-way and ham radios, antennas and weather radios (radio_packs.py, its own collection).

Answers say only what the source says: a Commons category's name, with one short line written here on what that kind
of thing is, or an Open Images label people confirmed; nothing about a particular photo is made up (each photo's own
caption or description is its second row, as home_packs.build_commons_topic does). Every answer ends with the
safety note of its subject (the same words as textbooks/disaster_ready.py and the kit): GENERATOR_NOTE (outdoors
only, 20 feet from windows and doors, carbon monoxide alarm, get out and call 911, never back-feed: a transfer switch
by a licensed electrician), FLOOD_NOTE (turn around, don't drown), POWER_LINE_NOTE, KI_NOTE (potassium iodide only
when officials say), SMOKE_NOTE, SHELTER_NOTE, and OFFICIALS_NOTE (follow your local officials' instructions).

No picture of injured or dead people: every category here leaves out files whose own words speak of the dead,
bodies, casualties, the injured or blood (NO_HARM), and the disaster and shelter packs leave out files whose words
name a child (home_packs.build_commons_topic adults_only); the kit packs mark such rows "child".

The packs (all open: CC0, public domain or CC BY, checked file by file; Open Images labels CC BY 4.0):
  commons_emergency_kits_power  Wikimedia Commons: bug-out bags, everyday carry, survival equipment, whistles,
                                particulate (N95) respirators, potassium iodide, multi-tools, ferrocerium fire
                                starters, dry bags, tarpaulins, sleeping bags, fuel containers; mobile
                                engine-generators, emergency power systems and uninterruptible power supplies.
  commons_warnings_shelters     Commons: warning sirens (Whelen, Thunderbolt), mobile public warning systems, tsunami
                                warning systems, emergency telephones, tornado shelters, storm cellars and safe rooms,
                                emergency operations centres, Community Emergency Response Teams, FEMA trailers,
                                evacuations, hurricane preparations, shutters, floodgates, levees, houses on stilts,
                                firebreaks, and FEMA's mitigation, response, recovery and Disaster Recovery Center
                                photographs.
  commons_emergency_signs_maps  Commons: tsunami signs, hurricane evacuation route signs, "in case of emergency" and
                                emergency access signs, the National Weather Service's watch and warning maps,
                                tornado warning zones, Storm Prediction Center products and wind chill charts.
  commons_disaster_types        Commons: the disasters commons_disasters does not have: volcanic eruptions, lava flows
                                and volcanic ash, tsunamis and tsunami damage, typhoons, drought and cracked earth,
                                ice storms and freezing rain, hail damage and hailstones, heat waves, wildfire smoke
                                haze, dust storms and haboobs, wind and derecho damage, lightning damage, avalanches,
                                mudflows and lahars, flash floods and snowdrifts.
  open_images_disasters         Open Images V7: floods, hurricanes, tornadoes, storms, wildfires, earthquakes,
                                tsunamis, blizzards, volcanoes and lava, gas masks and electric generators.

The share-alike Commons files and what was left out are in training-kit/kit/preparedness_sources.py.

    python packs/preparedness_packs.py commons_emergency_kits_power --limit 8      (prints a few rows)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

# ----------------------------------------------------------------- the safety notes (fixed sentences)

# The same words as textbooks/disaster_ready.py SAFETY_NOTE (the self-test checks).
SAFETY_NOTE = ("Safety: follow your local officials' instructions, and evacuate when they tell you to. Use generators, "
               "grills and other fuel-burning devices only outdoors, at least 20 feet from windows, doors and vents; "
               "have a working carbon monoxide alarm, and if it sounds or anyone feels dizzy or sick, get out to fresh "
               "air and call 911. Never walk or drive through floodwater: turn around, don't drown. Stay far away "
               "from downed power lines and report them. In danger, call 911.")
OFFICIALS_NOTE = "Follow your local officials' instructions, and evacuate when they tell you to."
GENERATOR_NOTE = ("Generator safety: run a generator only outdoors, at least 20 feet from the home with its exhaust "
                  "pointed away from windows, doors and vents, never in a home, garage, basement, shed or porch: its "
                  "carbon monoxide can kill in minutes. Have a carbon monoxide alarm, and if it sounds or anyone feels "
                  "dizzy or sick, get out to fresh air and call 911. Never plug a generator into a wall socket "
                  "(back-feeding can kill utility workers and neighbours): use heavy-duty outdoor cords, or a transfer "
                  "switch put in by a licensed electrician. Let it cool before refuelling, and store fuel in approved "
                  "containers away from the home.")
FLOOD_NOTE = ("Never walk, swim or drive through floodwater: turn around, don't drown. Moving water only ankle to knee "
              "deep can knock a person down or float a car, and floodwater hides holes and carries sewage and "
              "chemicals. " + OFFICIALS_NOTE)
POWER_LINE_NOTE = ("Stay far away from downed power lines and anything touching them, treat every line as live, and "
                   "call 911 and the power company.")
KI_NOTE = ("Take potassium iodide (KI) only when public health or emergency officials tell you to: it protects only "
           "the thyroid, and only from radioactive iodine.")
SMOKE_NOTE = ("Wildfire smoke: check the air quality (AirNow.gov), stay inside with windows and doors closed, use an "
              "air cleaner in one clean room, and outdoors a well-fitting N95 or better respirator helps; people "
              "with heart or lung disease, older adults and children are most at risk. " + OFFICIALS_NOTE)
SHELTER_NOTE = ("When a warning is issued, go to the shelter, safe room or lowest, innermost room straight away, and "
                "stay until officials say it is safe. " + OFFICIALS_NOTE)
HEAT_NOTE = ("Extreme heat: drink water, stay in air conditioning or a cooling centre, never leave anyone or a pet in "
             "a parked car, and call 911 for confusion, fainting or a very high body temperature.")
COLD_NOTE = ("Ice and extreme cold: stay off icy roads, keep warm and dry, and never use a generator, grill or "
             "outdoor heater indoors (carbon monoxide). " + OFFICIALS_NOTE)
VOLCANO_NOTE = ("Volcanic ash is sharp, glass-like rock: stay inside, protect your lungs (an N95 respirator) and eyes, "
                "and keep ash out of cars and machines. " + OFFICIALS_NOTE)
TSUNAMI_NOTE = ("A strong earthquake near the coast or the sea suddenly pulling back is a natural tsunami warning: go to "
                "high ground or far inland at once, on foot if you can, and stay there until officials say it is "
                "safe.")
LIGHTNING_NOTE = "When thunder roars, go indoors: there is no safe place outside in a thunderstorm."
MASK_NOTE = ("An N95 respirator filters smoke and dust particles only when it fits well (no gaps, no beard under the "
             "seal); it does not protect against gases such as carbon monoxide.")
KIT_NOTE = ("Ready.gov's kit advice: water (a gallon per person per day for several days), food, a flashlight, a "
            "battery or hand-crank radio, batteries, a first aid kit, medicines and medical supplies, a whistle, "
            "copies of important papers, chargers and cash, checked twice a year.")

ASK_WHAT = "What is this?"
ASK_KIND = "What kind of emergency equipment is this?"
ASK_SEE = "What does this picture show?"
ASK_SIGN = "What does this sign mean?"
ASK_MAP = "What kind of map is this?"
ASK_DISASTER = "What kind of disaster or hazard does this picture show?"
ASK_ABOUT = "What is this photo about?"

# No injured or dead people: files whose own words speak of them are left out of every category (a negative look-ahead
# over the title and description).
_HARM = (r"dead|death|deaths|died|bod(?:y|ies)|corpses?|cadavers?|killed|kill|injur\w*|wounded|casualt\w*|blood\w*|"
         r"victims?|morgue|funeral|fatalit\w*|remains|missing persons?")
NO_HARM = re.compile(rf"^(?!.*\b({_HARM})\b)", re.I | re.S)


def only(words):
    """A pattern that keeps a file only when its own words match words (a regular expression), and never when they
    speak of injured or dead people."""
    return re.compile(rf"^(?!.*\b({_HARM})\b)(?=.*\b({words})\b)", re.I | re.S)


def spec(category, words, note, question=ASK_WHAT, deeper=False, must=None):
    """A Commons spec for home_packs.build_commons_topic: "<question>" -> "This is <words>." then the note; every
    file must pass NO_HARM (or must, which includes it)."""
    return (category, deeper, [(question, f"This is {words}. {note}".strip())], must or NO_HARM)


def shows(category, words, note, question=ASK_SEE, deeper=False, must=None):
    """A spec whose answer is "It shows <words>." (scenes and damage rather than one thing)."""
    return (category, deeper, [(question, f"It shows {words}. {note}".strip())], must or NO_HARM)


# ----------------------------------------------------------------- Commons: kits, supplies and backup power

EMERGENCY_KITS_POWER = [
    spec("Bug-out bags", "a go-bag (a bug-out bag): a ready-packed bag of emergency supplies to grab when you must "
                         "leave quickly", KIT_NOTE, ASK_KIND),
    spec("Everyday carry", "an everyday-carry kit: the small tools and supplies a person carries every day",
         KIT_NOTE, ASK_KIND),
    spec("Survival equipment", "survival equipment", KIT_NOTE, ASK_KIND, deeper=True),
    spec("Whistles", "a whistle: in an emergency kit, a whistle lets you signal for help (three blasts) without "
                     "shouting", KIT_NOTE),
    spec("Particulate respirators", "a particulate respirator, such as an N95 mask", MASK_NOTE + " " + SMOKE_NOTE,
         deeper=True),
    spec("Potassium iodide", "potassium iodide (KI)", KI_NOTE, deeper=True),
    spec("Multi-tools", "a multi-tool: pliers, knife blades, screwdrivers and other tools folded into one",
         KIT_NOTE),
    spec("Ferrocerium", "a ferrocerium rod (a fire starter), which throws hot sparks when scraped",
         "Use it only outdoors, away from dry grass and fuel."),
    spec("Dry bags", "a dry bag: a waterproof bag that keeps papers, phones and clothes dry",
         "Keep copies of important documents (identity papers, insurance, medical lists) in a waterproof bag in "
         "your go-bag. " + KIT_NOTE, deeper=True),
    spec("Tarpaulins", "a tarpaulin (a tarp): a strong waterproof sheet, used to cover a damaged roof or make a "
                       "shelter", "Leave roof work to professionals or trained volunteers: falls kill. " +
         OFFICIALS_NOTE),
    spec("Sleeping bags", "a sleeping bag", KIT_NOTE),
    spec("Fuel containers", "a fuel container", "Store fuel only in approved containers, outdoors or in a detached "
                                                "shed, away from the home and from anything that can spark. " +
         GENERATOR_NOTE, must=only(r"cans?|containers?|canisters?|jerr\w*|jugs?|tanks?")),
    spec("Mobile engine-generators", "a portable or mobile generator: an engine that makes electricity",
         GENERATOR_NOTE, ASK_KIND, deeper=True),
    spec("Emergency power system", "an emergency power system: backup power for when the mains fail",
         GENERATOR_NOTE, ASK_KIND, deeper=True),
    spec("Uninterruptible power supply", "an uninterruptible power supply (a UPS): a battery that keeps a computer or "
                                         "medical device running for a short time when the power goes out",
         "If you rely on power-dependent medical equipment, tell your power company and local emergency managers, "
         "and plan for longer backup power.", ASK_KIND),
]

# ----------------------------------------------------------------- Commons: warnings, shelters, response and protection

WARNINGS_SHELTERS = [
    spec("Warning sirens", "an outdoor warning siren, which sounds when a tornado, tsunami or other danger is coming",
         "A siren means go inside and get information now (radio, TV, phone alerts); it is not an all-clear. " +
         SHELTER_NOTE, deeper=True),
    spec("Whelen sirens", "a Whelen outdoor warning siren", SHELTER_NOTE, deeper=True),
    spec("Thunderbolt sirens", "a Thunderbolt outdoor warning siren", SHELTER_NOTE, deeper=True),
    spec("Mobile public warning systems", "a public warning system: a way officials send alerts to people's phones "
                                          "or screens", "Turn on emergency alerts on your phone. " + OFFICIALS_NOTE,
         deeper=True),
    spec("Tsunami warning systems", "part of a tsunami warning system", TSUNAMI_NOTE, deeper=True),
    spec("Emergency telephones", "an emergency telephone", "In an emergency, call 911.", deeper=True),
    spec("Tornado shelters", "a tornado shelter", SHELTER_NOTE, deeper=True),
    spec("Storm cellars", "a storm cellar: an underground shelter from tornadoes", SHELTER_NOTE),
    spec("Safe rooms", "a safe room: a room built to protect people from tornadoes and hurricanes", SHELTER_NOTE,
         deeper=True),
    spec("Emergency operations centers", "an emergency operations centre, where officials coordinate the response to "
                                         "a disaster", OFFICIALS_NOTE, deeper=True),
    shows("Community Emergency Response Team", "a Community Emergency Response Team (CERT): trained volunteers who "
                                               "help their neighbours in a disaster",
          "CERT training is free from many local emergency management offices.", deeper=True),
    spec("FEMA trailers", "a FEMA trailer: temporary housing for people whose homes were destroyed in a disaster",
         "After a declared disaster, apply for help at DisasterAssistance.gov or 1-800-621-3362."),
    shows("Evacuations", "an evacuation: people leaving an area because of danger", OFFICIALS_NOTE, deeper=True),
    shows("Hurricane preparations", "preparations for a hurricane", FLOOD_NOTE),
    spec("Shutters", "a set of window shutters; storm shutters protect windows from wind and flying debris",
         OFFICIALS_NOTE, must=only(r"storms?|hurricanes?|typhoons?|cyclones?|roller|rolling|metal|steel|aluminium|"
                                   r"aluminum|protect\w*|security")),
    spec("Floodgates", "a floodgate, which is closed to keep flood water out", FLOOD_NOTE, deeper=True),
    spec("Levees", "a levee: a bank built along a river to hold back flood water", FLOOD_NOTE),
    spec("Stilt houses", "a house raised on stilts, which keeps it above flood water", FLOOD_NOTE),
    spec("Firebreaks", "a firebreak: a strip cleared of plants to slow a wildfire", SMOKE_NOTE),
    shows("Images from FEMA, category Mitigation", "FEMA's work to lower the damage the next disaster can do (FEMA "
                                                   "files this photo under mitigation: raising houses, safe rooms, "
                                                   "shutters, buyouts and stronger building)", OFFICIALS_NOTE,
          ASK_ABOUT),
    shows("Images from FEMA, category Disaster Recovery Center", "a FEMA Disaster Recovery Center, where people get "
                                                                  "help in person after a disaster (FEMA files this "
                                                                  "photo there)",
          "Apply for help at DisasterAssistance.gov or 1-800-621-3362; FEMA never charges for help.", ASK_ABOUT),
    shows("Images from FEMA, category Response", "the response to a disaster (FEMA files this photo under response)",
          SAFETY_NOTE, ASK_ABOUT),
    shows("Images from FEMA, category Recovery", "recovery after a disaster (FEMA files this photo under recovery)",
          "After a disaster, help is there: the Disaster Distress Helpline, call or text 1-800-985-5990. Beware of "
          "scams: FEMA never charges for help.", ASK_ABOUT),
]

# ----------------------------------------------------------------- Commons: signs and warning maps

SIGNS_MAPS = [
    spec("Tsunami signs", "a tsunami sign: it marks a tsunami hazard zone or the way to high ground", TSUNAMI_NOTE,
         ASK_SIGN, deeper=True),
    spec("Hurricane evacuation route signs", "a hurricane evacuation route sign: it shows the road to take when "
                                             "officials order an evacuation", OFFICIALS_NOTE, ASK_SIGN, deeper=True),
    spec("In case of emergency signs", "an \"in case of emergency\" sign, telling people what to do in an emergency",
         "In an emergency, call 911.", ASK_SIGN, deeper=True),
    spec("Emergency access signs", "an emergency access sign: it keeps a way clear for emergency vehicles",
         "Never block emergency access.", ASK_SIGN, deeper=True),
    spec("National Weather Service WWA maps", "a National Weather Service watches, warnings and advisories map: the "
                                              "coloured areas are where a watch, warning or advisory is in effect",
         "A watch means be prepared; a warning means take action now. " + OFFICIALS_NOTE, ASK_MAP),
    spec("Tornado warning zones", "a map of tornado warning areas", SHELTER_NOTE, ASK_MAP, deeper=True),
    spec("Storm Prediction Center products", "a Storm Prediction Center forecast product (severe thunderstorm and "
                                             "tornado outlooks and watches)", SHELTER_NOTE, ASK_MAP, deeper=True),
    spec("Wind chill", "a wind chill chart or reading: how cold it feels on bare skin when wind and cold combine",
         COLD_NOTE),
]

# ----------------------------------------------------------------- Commons: disasters by type (not in commons_disasters)

DISASTER_TYPES = [
    shows("Volcanic eruptions", "a volcanic eruption", VOLCANO_NOTE, ASK_DISASTER),
    shows("Lava flows", "a lava flow: molten rock moving over the ground", VOLCANO_NOTE, ASK_DISASTER),
    shows("Volcanic ash", "volcanic ash", VOLCANO_NOTE, ASK_DISASTER),
    shows("Ashfall", "ashfall: volcanic ash fallen over the land", VOLCANO_NOTE, ASK_DISASTER),
    shows("Tsunamis", "a tsunami", TSUNAMI_NOTE, ASK_DISASTER),
    shows("Tsunami damage", "damage from a tsunami", TSUNAMI_NOTE, ASK_DISASTER, deeper=True),
    shows("Images from FEMA, category Tsunami", "a tsunami's effects (FEMA files this photo under tsunami)",
          TSUNAMI_NOTE, ASK_DISASTER, deeper=True),
    shows("Images from FEMA, category Typhoon", "a typhoon's damage (FEMA files this photo under typhoon)", FLOOD_NOTE,
          ASK_DISASTER, deeper=True),
    shows("Images from FEMA, category Drought", "drought (FEMA files this photo under drought)",
          "In a drought, follow local water restrictions.", ASK_DISASTER, deeper=True),
    shows("Cracked earth", "cracked, dried-out earth, as in a drought", "In a drought, follow local water "
                                                                        "restrictions.", ASK_DISASTER),
    shows("Ice storms", "an ice storm: freezing rain coating everything in ice", COLD_NOTE + " " + POWER_LINE_NOTE,
          ASK_DISASTER, deeper=True),
    shows("Freezing rain", "freezing rain and the ice it leaves", COLD_NOTE, ASK_DISASTER, deeper=True),
    shows("Hail damage", "hail damage", "When hail or a severe thunderstorm comes, go indoors and away from windows. "
                                        + LIGHTNING_NOTE, ASK_DISASTER, deeper=True),
    spec("Hailstones", "hailstones: lumps of ice that fall in severe thunderstorms", LIGHTNING_NOTE),
    shows("Heat waves", "a heat wave", HEAT_NOTE, ASK_DISASTER, deeper=True),
    shows("Haze", "haze", SMOKE_NOTE, ASK_DISASTER,
          must=only(r"smoke|smoky|wildfires?|bushfires?|forest fires?|fires?|burning")),
    shows("Dust storms", "a dust storm", "In a dust storm, stay inside; if driving, pull aside, stay buckled, turn "
                                         "off your lights and wait.", ASK_DISASTER, deeper=True),
    shows("Haboobs", "a haboob: a wall of dust pushed ahead of a thunderstorm", "In a dust storm, stay inside; if "
                                                                               "driving, pull aside and wait.",
          ASK_DISASTER),
    shows("Wind damage", "wind damage", POWER_LINE_NOTE, ASK_DISASTER, deeper=True),
    shows("Derechos", "a derecho: a long line of storms with damaging straight-line winds", POWER_LINE_NOTE,
          ASK_DISASTER, deeper=True),
    shows("Lightning damage", "lightning damage", LIGHTNING_NOTE, ASK_DISASTER, deeper=True),
    shows("Avalanches", "an avalanche", "In avalanche country, check the avalanche forecast and carry a beacon, probe "
                                        "and shovel.", ASK_DISASTER),
    shows("Mudflows", "a mudflow", "Mudflows and debris flows move fast after heavy rain or on burned slopes: move "
                                   "away from their path. " + OFFICIALS_NOTE, ASK_DISASTER, deeper=True),
    shows("Lahars", "a lahar: a volcanic mudflow", VOLCANO_NOTE, ASK_DISASTER, deeper=True),
    shows("Flash floods", "a flash flood", FLOOD_NOTE, ASK_DISASTER, deeper=True),
    shows("Snowdrifts", "snowdrifts: snow piled up by the wind", COLD_NOTE, ASK_DISASTER),
]


def build_commons_emergency_kits_power(limit):
    """The commons_emergency_kits_power pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(EMERGENCY_KITS_POWER, limit, "prepkit")


def build_commons_warnings_shelters(limit):
    """The commons_warnings_shelters pack (see the module docstring); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(WARNINGS_SHELTERS, limit, "prepwarn", adults_only=True)


def build_commons_emergency_signs_maps(limit):
    """The commons_emergency_signs_maps pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(SIGNS_MAPS, limit, "prepsign")


def build_commons_disaster_types(limit):
    """The commons_disaster_types pack (see the module docstring); files naming a child are left out."""
    from home_packs import build_commons_topic
    return build_commons_topic(DISASTER_TYPES, limit, "prepdis", adults_only=True)


# ----------------------------------------------------------------- Open Images

DISASTERS_OI = [
    group("What kind of disaster or severe weather is in this picture?",
          {"Flood": "a flood", "Hurricane": "a hurricane", "Tornado": "a tornado", "Storm": "a storm",
           "Wildfire": "a wildfire", "Earthquake": "earthquake damage", "Tsunami": "a tsunami",
           "Blizzard": "a blizzard", "Volcano": "a volcano", "Lava": "lava", "Disaster": "a disaster"},
          SAFETY_NOTE),
    group("Is there a gas mask in this picture?", {"Gas mask": "a gas mask"}, MASK_NOTE),
    group("Is there a generator in this picture?", {"Electric generator": "an electric generator"}, GENERATOR_NOTE),
]


def build_open_images_disasters(limit):
    """open_images_disasters (see the module docstring)."""
    return build_oi_gap("open_images_disasters", DISASTERS_OI, limit, 9311)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
PREPAREDNESS_PACKS = {
    "commons_emergency_kits_power": (build_commons_emergency_kits_power, COMMONS_LICENCE.format(
        what="emergency kit, supply, respirator, potassium iodide, generator and backup power")),
    "commons_warnings_shelters": (build_commons_warnings_shelters, COMMONS_LICENCE.format(
        what="warning siren, alert system, shelter, safe room, emergency response, evacuation, storm and flood "
             "protection and FEMA mitigation, response and recovery")),
    "commons_emergency_signs_maps": (build_commons_emergency_signs_maps, COMMONS_LICENCE.format(
        what="tsunami, evacuation and emergency sign and weather warning map")),
    "commons_disaster_types": (build_commons_disaster_types, COMMONS_LICENCE.format(
        what="volcano, tsunami, typhoon, drought, ice storm, hail, heat wave, smoke, dust storm, wind, lightning, "
             "avalanche, mudflow and flash flood")),
    "open_images_disasters": (build_open_images_disasters, OI_LICENCE),
}
PREPAREDNESS_LIMITS = {
    "commons_emergency_kits_power": 1000,     # 16 categories, few files in some
    "commons_warnings_shelters": 2500,        # 23 categories; FEMA's response and recovery have thousands
    "commons_emergency_signs_maps": 400,      # 8 categories
    "commons_disaster_types": 1500,           # 26 categories
    "open_images_disasters": 800,             # 14 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
PREPAREDNESS_COMMONS_KEYS = ("commons_emergency_kits_power", "commons_warnings_shelters", "commons_emergency_signs_maps",
                             "commons_disaster_types")
# Every Commons spec of these packs (for the self-test).
PREPAREDNESS_SPECS = EMERGENCY_KITS_POWER + WARNINGS_SHELTERS + SIGNS_MAPS + DISASTER_TYPES


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a preparedness pack builder.")
    parser.add_argument("key", choices=sorted(PREPAREDNESS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = PREPAREDNESS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
