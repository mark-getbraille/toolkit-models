"""EMERGENCY PREPAREDNESS AND DISASTERS for the Picture Model Training Kit (the owner's request of 2026-11-22: help him
and others prepare for and get through emergencies). This file lists:
  - the ready-made packs built in packs/preparedness_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_emergency_kits_power, commons_warnings_shelters, commons_emergency_signs_maps,
    commons_disaster_types and open_images_disasters;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (PREPAREDNESS_NOT_INCLUDED).

As in home_crafts_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit
on the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only
when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say; the safety notes (generators outdoors and 20 feet away, carbon
monoxide, turn around, don't drown, downed power lines, potassium iodide only when officials say, follow your local
officials' instructions) are the same words as packs/preparedness_packs.py.

Picture-making (PREPAREDNESS_PICTURE_MAKING_OK): only the signs and maps and the kit items (things, drawings and maps,
no people) may be used; sources.py puts every other key in NOT_FOR_PICTURE_MAKING (disasters, damage, evacuations
and responders are never for making pictures).

    python -c "import sources, preparedness_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"

# The same words as packs/preparedness_packs.py (the self-test checks they match).
SAFETY_NOTE = ("Safety: follow your local officials' instructions, and evacuate when they tell you to. Use generators, "
               "grills and other fuel-burning devices only outdoors, at least 20 feet from windows, doors and vents; "
               "have a working carbon monoxide alarm, and if it sounds or anyone feels dizzy or sick, get out to fresh "
               "air and call 911. Never walk or drive through floodwater: turn around, don't drown. Stay far away "
               "from downed power lines and report them. In danger, call 911.")
GENERATOR_NOTE = ("Generator safety: run a generator only outdoors, at least 20 feet from the home with its exhaust "
                  "pointed away from windows, doors and vents, never in a home, garage, basement, shed or porch: its "
                  "carbon monoxide can kill in minutes. Have a carbon monoxide alarm, and if it sounds or anyone feels "
                  "dizzy or sick, get out to fresh air and call 911. Never plug a generator into a wall socket "
                  "(back-feeding can kill utility workers and neighbours): use heavy-duty outdoor cords, or a transfer "
                  "switch put in by a licensed electrician. Let it cool before refuelling, and store fuel in approved "
                  "containers away from the home.")
KIT_NOTE = ("Ready.gov's kit advice: water (a gallon per person per day for several days), food, a flashlight, a "
            "battery or hand-crank radio, batteries, a first aid kit, medicines and medical supplies, a whistle, "
            "copies of important papers, chargers and cash, checked twice a year.")
SHELTER_NOTE = ("When a warning is issued, go to the shelter, safe room or lowest, innermost room straight away, and "
                "stay until officials say it is safe. Follow your local officials' instructions, and evacuate when "
                "they tell you to.")


def thing(category, words, note="", deeper=False, question="What is this?"):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the note."""
    return (category, question, f"This is {words}." + (f" {note}" if note else ""), deeper)


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

# Categories of packs/preparedness_packs.py that need no word filter beyond leaving out harm (things, shelters and
# signs; the disaster and response categories are left out of the share-alike entry, which has no word filter).
PREPAREDNESS_SA = [
    thing("Bug-out bags", "a go-bag (a bug-out bag): a ready-packed bag of emergency supplies to grab when you must "
                          "leave quickly", KIT_NOTE),
    thing("Multi-tools", "a multi-tool: pliers, knife blades, screwdrivers and other tools folded into one", KIT_NOTE),
    thing("Mobile engine-generators", "a portable or mobile generator: an engine that makes electricity",
          GENERATOR_NOTE, deeper=True),
    thing("Uninterruptible power supply", "an uninterruptible power supply (a UPS): a battery that keeps a computer "
                                          "or medical device running for a short time when the power goes out"),
    thing("Tornado shelters", "a tornado shelter", SHELTER_NOTE, deeper=True),
    thing("Storm cellars", "a storm cellar: an underground shelter from tornadoes", SHELTER_NOTE),
    thing("Tsunami signs", "a tsunami sign: it marks a tsunami hazard zone or the way to high ground", "", True,
          "What does this sign mean?"),
]


def prepare_preparedness_commons_sa(source, data_dir, work, cap):
    """Commons go-bag, multi-tool, generator, UPS, tornado shelter, storm cellar and tsunami sign
    categories, files under CC BY-SA or GFDL (files naming a child left out)."""
    items = commons_sa_items(PREPAREDNESS_SA, cap, source.test, "prep-sa", adults_only=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

PREPAREDNESS_SOURCES = [
    Source("commons_emergency_kits_power", "Emergency kits and backup power: go-bags, survival equipment, whistles, N95 respirators, potassium iodide, dry bags, tarps, "
                                           "fuel containers, generators and UPS units, with the safety notes "
                                           "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 230 MB"),
    Source("commons_warnings_shelters", "Warnings and shelters: outdoor warning sirens, alert and tsunami warning "
                                        "systems, tornado shelters, storm cellars and safe rooms, emergency operations "
                                        "centres, CERT, FEMA trailers, evacuations, shutters, floodgates, levees and "
                                        "FEMA's mitigation, response and recovery photos (Wikimedia Commons, "
                                        "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 2500, 25, prepare_pack, "about 560 MB"),
    Source("commons_emergency_signs_maps", "Emergency signs and warning maps: tsunami and hurricane evacuation signs, "
                                           "emergency signs, National Weather Service watch and warning maps, "
                                           "tornado warning areas, Storm Prediction Center products and wind chill "
                                           "charts (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 5, prepare_pack, "about 90 MB"),
    Source("commons_disaster_types", "Disasters by type: volcanic eruptions, lava and ash, tsunamis, typhoons, "
                                     "drought, ice storms, hail, heat waves, wildfire smoke, dust storms, wind and "
                                     "lightning damage, avalanches, mudflows and flash floods, with safety notes; "
                                     "no injured or dead people (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 340 MB"),
    Source("open_images_disasters", "Floods, hurricanes, tornadoes, storms, wildfires, earthquakes, tsunamis, "
                                    "blizzards, volcanoes, gas masks and generators, with the safety notes (Open "
                                    "Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 800, 10, prepare_pack, "about 160 MB"),
    Source("preparedness_commons_sa", "Wikimedia Commons: go-bags, multi-tools, generators, UPS units, "
                                      "tornado shelters, storm cellars and tsunami signs, with the safety notes, files "
                                      "under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 5, prepare_preparedness_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: kit items, signs and maps (things and drawings, no people);
# never the disasters, damage, evacuations or responders, nor Open Images (people).
PREPAREDNESS_PICTURE_MAKING_OK = {"commons_emergency_signs_maps"}

# The kit topics each collection belongs to (topics.py lists them; the self-test checks they match): everything in
# "home" (preparing a household), the disasters and weather also in "nature", the signs and maps in "documents".
PREPAREDNESS_TOPICS = {
    "home": ("commons_emergency_kits_power", "commons_warnings_shelters", "commons_emergency_signs_maps",
             "commons_disaster_types", "open_images_disasters", "preparedness_commons_sa"),
    "nature": ("commons_disaster_types", "open_images_disasters"),
    "documents": ("commons_emergency_signs_maps",),
}

PREPAREDNESS_NOT_INCLUDED = {
    "FEMA Media Library, NOAA Photo Library, USGS and NWS photo pages":
        "public domain, but their own photo sites refused this machine (403) or offer no listing a program can read "
        "(2026-11-22); FEMA's photos on Commons are read by category here (mitigation, response, recovery, Disaster "
        "Recovery Centers, tsunami, typhoon, drought) and by commons_disasters (the hazard categories).",
    "Commons categories that do not exist under the names tried (November 2026)":
        "Emergency kits, Survival kits, Go bags, Emergency supplies, Emergency blankets, N95 respirators, Potassium "
        "iodide tablets, Transfer switches, Standby generators, Generator interlock kits, Gasoline cans, Tornado "
        "sirens, Civil defense sirens, Outdoor warning sirens, Storm shelters, Evacuation centers, Red Cross shelters, "
        "Disaster Recovery Centers (FEMA's own category is used), Hurricane and storm shutters (Shutters with storm "
        "words is used), Flood barriers, Flood walls, Elevated houses (Stilt houses is used), Defensible space, Power "
        "outages, Wildfire smoke (Haze with smoke words is used), Storm surge, Extreme cold, Cooling and warming "
        "centers, Emergency food and Water storage tanks.",
    "Commons categories already asked by another pack":
        "the earthquake, flood, tornado, landslide and fire damage categories and FEMA's hazard categories "
        "(commons_disasters); Downed power lines, Flooded roads, Smoke, Sandbags, Evacuation route signs, Emergency "
        "exit signs, Assembly point signs, Fallout shelter signs, Air raid sirens (commons_safety); First aid kits, "
        "Fire extinguishers, Wildfires, Sinkholes (commons_safety_photos); Lightning, Hail, Blizzards (sky_weather); "
        "Drought, Plywood, Diesel generators, Engine-generators, Jerrycans, Respirators, Dust masks, Surgical masks, "
        "Portable power stations, Solar chargers, Carbon monoxide detectors: not repeated.",
    "Emergency cooking, water and food storage, first aid, heating and lighting":
        "other helpers' collections (outdoor cooking and food storage; life skills first aid; home crafts heating and "
        "lighting): Canned water, Water purification tablets and Emergency rations are left to them.",
    "Pictures of injured or dead people":
        "never included (the owner's rule for this collection): every category leaves out files whose words speak of "
        "the dead, bodies, casualties, the injured or blood; the graphic disaster scenes are commons_disasters' own, "
        "marked graphic.",
}
