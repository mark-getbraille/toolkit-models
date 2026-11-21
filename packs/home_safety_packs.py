"""Pack builders for HOME SAFETY AND CONTROLS, FOOD STATE and PUBLIC ACCESSIBILITY FEATURES, used by build_packs.py in
the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus "place" where something says where the photo was taken, "child":
true where the words of a picture name a child, and "facts" (the Commons category it came from). A picture with more
than one question comes once with its JPEG and then again as (None, None, row) rows whose "file" names the same picture
(food_packs.with_twins). The limit counts pictures.

Why: a blind person at home needs to know what the box on the wall is (a breaker panel, a gas meter, a smoke alarm),
what an appliance's display says, whether the bread has gone mouldy or the bananas are ripe, and, out of the house,
where the braille on a sign or a lift is, what a bus stop sign or a ticket machine is, and how to reach a platform.
Answers are fixed sentences written here from each source's own labels (a Commons category's name, the file's own
title and description, an agency's own caption), never by an AI model, with a short safety note where it matters.

NEVER GUESS A READING OR A LIGHT STATE. A meter's reading, a thermostat's or oven's setting, a smoke alarm's light,
a breaker's position, an extinguisher's gauge or a meat thermometer's temperature is given only where the file's own
title or description says it in so many words, with its unit ("the meter reads 04512 kWh", "LED blinking red",
"gauge in the green", "thermometer reads 165 F"), and never when the words give two different states (the readers
below: alarm_light, meter_reading, display_reading, breaker_state, gauge_state, food_temperature). Ripeness, mould and
doneness come only from a category that says them ("Unripe tomatoes", "Mouldy bread"-like categories, "Rare steak").

The packs (all open: CC0, public domain or CC BY, checked file by file at the source, November 2026):
  commons_home_safety      Wikimedia Commons: breaker panels (distribution boards), fuse boxes and circuit breakers,
                           gas meters, smart meters, stopcocks (shut-off valves), sump pumps, gas furnaces; and, ONLY
                           where this pack adds a question no other pack asks (a reading, a light, a gauge, a kind),
                           the categories other packs already show: smoke and carbon monoxide alarms (events_safety
                           commons_safety, us_modern commons_us_controls), thermostats, microwave ovens and washing
                           machines (home_packs commons_appliances), dishwashers, dryers and ovens
                           (commons_us_controls), water meters (mechanical_packs), fire extinguishers
                           (commons_safety) and water damage (commons_pests).
  commons_food_state       Commons: unripe and green bananas and tomatoes, mould on food, rotting fruit, meat
                           doneness; and meat thermometers only where the file states the temperature. Mould answers
                           carry the USDA's advice (MOULD_NOTE); a cheese made with mould (blue cheese, Brie) is never
                           called spoiled.
  usda_food_safety_photos  US Department of Agriculture photos on Commons (public domain, works of the US government):
                           its Flickr stream's photos whose own caption is about food safety (thermometers, safe
                           temperatures, leftovers, thawing, washing hands, mould), found with Commons search; the
                           agency's caption is the answer, and the temperature only where the caption states it.
  commons_access_features  Commons: braille signage, bus stop signs (US and elsewhere), US ticket machines; and lift
                           (elevator) buttons only where the file's record says they have braille.

Not repeated (other packs ask the same of the same photos): crosswalks, pedestrian signals, push buttons, audible
signals, curb cuts and tactile paving (street_scene_packs, ptl_crossings, commons_disability), wheelchair ramps, lifts,
disabled parking, accessibility signs, kneeling buses and tactile paving in stations (commons_disability), elevator
buttons and ticket machines as things (commons_appliances), seven-segment displays (seven_segment), laundry symbols,
clock times, Open Images home and food labels (open_images_home, open_images_food: Open Images has no label for
smoke alarms, meters, breaker panels, ripeness or doneness), commons_food's spoiled food, eggs and steaks, and
Mendeley food-freshness sets (fish_eyes, the kit's beef, fish and chicken freshness entries). Share-alike and
non-commercial collections on the same subjects are entries or notes in training-kit/kit/home_safety_sources.py.

Safety (packs/SOURCE-RULES.md): no sexual content (NUDE, us_packs.NOT_SHOWN); no fire, injury or death photos (HARM:
these are everyday packs); every row whose words name a child is marked "child". The home and food packs show things
and may be used for picture-making unless a file's words name a person; commons_access_features shows public places
with people in them and is never used for picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS). A free photo dropped
only because it has no answer is set aside for a description (build_packs.needs_description).

    python packs/home_safety_packs.py commons_home_safety --limit 8      (prints a few rows: a quick check)
"""

import collections
import json
import math
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from food_packs import with_twins, count_pictures, commons_members, commons_get, sentence
from home_packs import commons_fetch, file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import mech_entries, in_english, PLACES, JUST_A_RECORD, NOT_A_CHILD, NOT_A_PHOTO
from us_packs import NOT_SHOWN, file_categories
from us_modern_packs import agency_entries, agency_caption, only_the_name, OFFICIAL
from places import where

WHAT_Q = "What is this?"
KIND_Q = "What kind is this?"
DESCRIBE_Q = "Describe this picture."
LIGHT_Q = "What does the alarm's light show?"
READING_Q = "What does the meter read?"
DISPLAY_Q = "What does the display or dial show?"
BREAKER_Q = "Is a breaker tripped or switched off?"
GAUGE_Q = "What does the extinguisher's pressure gauge show?"
RIPE_Q = "Is this ripe?"
SAFE_Q = "Is this food safe to eat?"
DONE_Q = "How well cooked is this meat?"
TEMP_Q = "What temperature does the thermometer show?"
BRAILLE_Q = "Is there braille here?"
SIGN_Q = "What does this sign tell me?"
USA, CANADA = "USA", "Canada"

# Questions whose answer is one state: when a photo's categories or words give two different answers, none is used.
ONE_STATE = {LIGHT_Q, READING_Q, DISPLAY_Q, BREAKER_Q, GAUGE_Q, RIPE_Q, DONE_Q, TEMP_Q, KIND_Q}
# The questions that count as new for a category another pack already shows (state_only topics).
NEW_QUESTIONS = {LIGHT_Q, READING_Q, DISPLAY_Q, BREAKER_Q, GAUGE_Q, TEMP_Q, KIND_Q, BRAILLE_Q, DONE_Q}

# ----------------------------------------------------------------- safety notes (short, from public guidance)

SMOKE_NOTE = ("Test it once a month with its test button and replace the whole alarm every 10 years. A short chirp "
              "every minute or so usually means its battery is low.")
CO_NOTE = ("Carbon monoxide has no smell. If the alarm sounds, get everyone out into fresh air at once and call "
           "911 (or your emergency number) from outside.")
PANEL_NOTE = ("A tripped breaker sits in the middle or off position: push it fully off, then on. A breaker that trips "
              "again and again, a warm or buzzing panel, or a burning smell needs an electrician. Never take the "
              "panel's inner cover off.")
FUSE_NOTE = ("A blown fuse must be replaced with one of the same rating, with the power off; never with wire, foil "
             "or a bigger fuse.")
GAS_NOTE = ("If you smell gas (like rotten eggs), leave at once and call the gas company or 911 from outside; do "
            "not switch lights or appliances on or off, and do not use a phone inside.")
WATER_SHUTOFF_NOTE = ("Know where your main water shut-off is before a leak: turning the handle clockwise (or a "
                      "lever across the pipe) closes it.")
SUMP_NOTE = "Test it before the rainy season by pouring a bucket of water into the pit: the pump should start."
FURNACE_NOTE = ("Change or clean its air filter every one to three months. A carbon monoxide alarm should be on every "
                "floor of a home with a gas furnace.")
EXTINGUISHER_NOTE = ("To use one: Pull the pin, Aim at the base of the fire, Squeeze the handle, Sweep side to side "
                     "(PASS). Get out and call 911 if the fire is spreading.")
LEAK_NOTE = ("Turn off the water at the shut-off valve, and keep electrical things away from the water. Damp left for "
             "a day or two can grow mould.")
MOULD_NOTE = ("Do not smell it (spores can harm your lungs) and throw it away: on bread, soft fruit and soft cheese "
              "the mould's roots spread further than you can see. Only hard cheese and firm vegetables may be saved "
              "by cutting away at least 1 inch (2.5 cm) around the spot (USDA advice).")
CHEESE_MOULD_NOTE = ("Some cheeses, such as blue cheese and Brie, are made with safe moulds. Unexpected mould on soft "
                     "cheese means throw it away; on hard cheese cut at least 1 inch (2.5 cm) around it (USDA "
                     "advice).")
TEMP_NOTE = ("USDA safe minimum inside temperatures: chicken and other poultry 165 F (74 C); ground meat 160 F (71 C); "
             "beef, pork and lamb steaks, chops and roasts 145 F (63 C) with a 3-minute rest; fish 145 F (63 C).")
RARE_NOTE = ("The USDA advises cooking beef steaks to at least 145 F (63 C) inside; rarer meat carries more risk, "
             "especially for children, pregnant people and older people. Ground beef should never be eaten rare.")


def answer(text, note=""):
    """An answer with its safety note after it."""
    return f"{text} {note}".strip()


# ----------------------------------------------------------------- category rules

# One rule per kind of thing: (pattern on a category name, question, answer). A file gets the rows of every rule
# that the category it was found in or any of its other categories matches.
RULES = [
    # commons_home_safety
    (r"\bsmoke detectors?\b|\bsmoke alarms?\b", WHAT_Q, answer("This is a smoke alarm (smoke detector).", SMOKE_NOTE)),
    (r"\bcarbon monoxide (detectors?|alarms?)\b", WHAT_Q, answer("This is a carbon monoxide (CO) alarm.", CO_NOTE)),
    (r"\bdistribution boards?\b|\bbreaker (panels?|boxes)\b|\bload centers?\b",
     WHAT_Q, answer("This is an electrical panel (a breaker box or distribution board): each of the building's "
                    "circuits has its own breaker or fuse here, and there is usually a main switch.", PANEL_NOTE)),
    (r"\bfuse boxes\b", WHAT_Q, answer("This is a fuse box: each circuit has a fuse that burns through (blows) if too "
                                      "much current flows.", FUSE_NOTE)),
    (r"\bcircuit breakers\b", WHAT_Q, answer("This is a circuit breaker: a switch that turns itself off (trips) when "
                                            "too much current flows, to stop wires overheating.", PANEL_NOTE)),
    (r"\bgas meters?\b", WHAT_Q, answer("This is a gas meter: it measures how much gas the building uses.", GAS_NOTE)),
    (r"\bsmart meters?\b", WHAT_Q, "This is a smart meter: a meter that measures the electricity (or gas) used and "
                                   "sends its readings to the supplier."),
    (r"\belectricity meters?\b|\belectric meters?\b|\bwatt-hour meters?\b",
     WHAT_Q, "This is an electricity meter: it measures how much electricity the building uses, in kilowatt-hours "
             "(kWh)."),
    (r"\bwater meters?\b", WHAT_Q, "This is a water meter: it measures how much water the building uses."),
    (r"\bstopcocks?\b|\bshut-?off valves?\b", WHAT_Q,
     answer("This is a stopcock (a shut-off valve) on a water pipe: it turns the water off.", WATER_SHUTOFF_NOTE)),
    (r"\bsump pumps?\b", WHAT_Q, answer("This is a sump pump: it pumps water out of a pit in the basement floor so the "
                                       "basement does not flood.", SUMP_NOTE)),
    (r"\bgas furnaces?\b", WHAT_Q, answer("This is a gas furnace: it burns gas to heat air that fans blow through the "
                                         "home's ducts.", FURNACE_NOTE)),
    (r"\bwater heaters?\b|\bboilers \(water heating\)\b", WHAT_Q,
     answer("This is a water heater: a tank or unit that heats the home's water.",
            "Setting it to about 120 F (49 C) prevents scalds. The pipe from the valve on its side is the pressure "
            "relief outlet: water coming out of it, or a leaking tank, needs a plumber.")),
    (r"\bthermostats?\b", WHAT_Q, "This is a thermostat: it switches the heating or cooling on and off to keep the room "
                                  "at the temperature it is set to."),
    (r"\bfire extinguishers?\b(?! signs?)", WHAT_Q, answer("This is a fire extinguisher.", EXTINGUISHER_NOTE)),
    (r"\bcarbon dioxide fire extinguishers\b|\bCO2 fire extinguishers\b", KIND_Q,
     "It is a carbon dioxide (CO2) extinguisher, for electrical fires and burning liquids. Its horn gets very cold: "
     "hold it by the handle, and never point it at a person."),
    (r"\bwater fire extinguishers\b", KIND_Q, "It is a water extinguisher, for paper, wood and cloth only: never use "
                                              "it on an electrical, oil or fat fire."),
    (r"\b(powder|dry chemical|ABC) fire extinguishers\b", KIND_Q,
     "It is a dry powder (dry chemical) extinguisher, for most kinds of fire; the powder makes a thick cloud."),
    (r"\bfoam fire extinguishers\b", KIND_Q, "It is a foam extinguisher, for paper, wood and burning liquids; not "
                                             "for electrical or cooking-fat fires."),
    (r"\bmou?ld on (buildings?|walls?|ceilings?)\b", WHAT_Q,
     answer("This shows mould growing on a wall or building: a sign of damp or a leak.", "Do not scrub or sniff it "
            "dry; find and fix the damp first. A patch bigger than about 10 square feet (1 square metre) needs a "
            "professional (US EPA advice).")),
    (r"\bwater damage\b|\bwater leaks?\b|\bwater stains?\b|\bleaking (pipes?|roofs?)\b|\bdamp(ness)?\b(?! proof)",
     WHAT_Q, answer("This shows water damage: a leak or damp has stained, swollen or rotted the surface.", LEAK_NOTE)),
    # commons_food_state
    (r"\b(green|unripe) bananas\b", RIPE_Q, "No: these bananas are green (unripe). Bananas ripen at room temperature "
                                            "in a few days, turning yellow, then getting brown spots as they get "
                                            "sweeter and softer. Green cooking bananas and plantains are often cooked while "
                                            "still green."),
    (r"\bunripe tomatoes\b", RIPE_Q, "No: this tomato is not ripe yet. It ripens on the counter, out of the fridge, "
                                     "turning red (or its ripe colour) and a little soft."),
    (r"\bunripe (fruits?|avocados?|mangoes|peaches|strawberries)\b", RIPE_Q,
     "No: this fruit is not ripe yet. It ripens at room temperature; a ripe one gives a little when pressed gently."),
    (r"\bovert?ripe bananas\b|\bbrown bananas\b", RIPE_Q,
     "These bananas are overripe: brown and soft. They are still safe to eat if there is no mould and no sour smell, "
     "and are good for baking."),
    (r"\bmou?ldy? (bread|food|fruits?|vegetables?)\b|\bmou?ld on (bread|food|fruits?|vegetables?)\b|"
     r"\brhizopus stolonifer\b|\bpenicillium on food\b", SAFE_Q, answer("No: there is mould on it.", MOULD_NOTE)),
    (r"\b(rotten|rotting|decaying|decomposing) (fruits?|apples?|bananas?|tomatoes|vegetables?|food|oranges?|"
     r"pears?|potatoes?|peaches?|strawberr(y|ies)|lemons?|onions?)\b", SAFE_Q,
     answer("No: it is rotten.", "Throw it away; rot spreads to the fruit or vegetables touching it.")),
    (r"\bmou?ldy? cheese\b|\bmould on cheese\b", SAFE_Q, answer("There is mould on this cheese.", CHEESE_MOULD_NOTE)),
    (r"\brare (steaks?|beef|meat)\b|\bblue steaks?\b", DONE_Q, answer("It is rare: red and cool in the middle.",
                                                                     RARE_NOTE)),
    (r"\bmedium[- ]rare (steaks?|beef|meat)\b", DONE_Q, answer("It is medium rare: warm and red to pink in the middle.",
                                                              RARE_NOTE)),
    (r"\bmedium (steaks?|beef)\b", DONE_Q, "It is cooked medium: pink in the middle."),
    (r"\bwell[- ]done (steaks?|beef|meat)\b", DONE_Q, "It is well done: brown all the way through, with no pink."),
    (r"\braw (meat|beef|chicken|pork|poultry|steaks?|minced meat|ground beef)\b", DONE_Q,
     answer("It is raw: not cooked at all.", "Keep raw meat away from ready-to-eat food, and wash your hands and "
                                            "anything it touched.")),
    (r"\bmeat thermometers?\b", WHAT_Q, answer("This is a meat thermometer, pushed into the thickest part of the meat "
                                              "to check it is cooked.", TEMP_NOTE)),
    # commons_access_features
    (r"\bbraille signage\b|\bbraille signs?\b|\bsigns? with braille\b|\btactile signs?\b", BRAILLE_Q,
     "Yes: this sign has braille, raised dots usually placed under raised print letters, so it can be read by "
     "touch. In the US, room signs with braille are on the wall beside the door, on the latch side, about 4 to 5 "
     "feet (1.2 to 1.5 m) from the floor."),
    (r"\bbraille in elevators\b|\belevator buttons with braille\b", BRAILLE_Q,
     "Yes: the lift buttons have braille beside them, and usually raised numbers and symbols."),
    (r"\belevator buttons\b|\blift buttons\b", WHAT_Q, "These are the buttons of a lift (elevator). In the US the "
                                                       "main entrance floor is often marked with a raised star."),
    (r"\bbus stop signs?\b|\bbus stop flags?\b", SIGN_Q,
     "It is a bus stop sign: it marks where the bus stops. Many list the route numbers, and some give a stop number "
     "for phoning or texting for the next bus."),
    (r"\bticket machines\b|\bfare (machines|vending machines)\b|\bticket vending machines\b", WHAT_Q,
     "This is a ticket machine (fare machine): choose a ticket on its screen or buttons and pay. Many US transit "
     "machines have an audio jack, braille and a tactile keypad; ask staff or the transit agency where they are."),
]
RULES = [(re.compile(p, re.I), q, a) for p, q, a in RULES]

# Subcategories that are not photos of the thing: drawings, art, history, museums, logos, industry, ships, cars.
SKIP = re.compile(r"\b(diagrams?|drawings?|art|artistic|historic|history|videos?|maps?|logos?|museums?|by year|"
                  r"quality images|industrial|blast|smelting|glass|metallurg\w*|ships?|locomotives?|automobiles?|"
                  r"cars?|aircraft|patents?|advertis\w*|people|persons|in literature|icons?|emoji|cooking|recipes|"
                  r"dishes|cuisine|fried|varieties|cultivars?|plants?|trees|flowers|military|nuclear|"
                  r"substations?|power stations?|high voltage)\b", re.I)
# Words that leave a file out: fires, injuries and death (everyday packs), sex.
HARM = re.compile(r"\b(fires? damage|burn(ed|t) (out|down)|house fires?|killed|dead|deaths?|died|fatal\w*|injur\w*|"
                  r"wounded|blood\w*|bod(y|ies)|corpses?|explosions?|exploded|electrocut\w*|arson)\b", re.I)


# ----------------------------------------------------------------- readers: only what the words say

def _one(found):
    """The one value found, or "" when none or two different ones (never a guess between them)."""
    found = list(dict.fromkeys(found))
    return found[0] if len(found) == 1 else ""


LIGHT = re.compile(r"\b(?:LED|light|lamp|indicator)s?\s+(?:is\s+|was\s+)?(?:(blinking|flashing|steady|solid|"
                   r"glowing|lit|on)\s+)?(?:in\s+)?(red|green|amber|yellow|blue|white|orange)\b|"
                   r"\b(blinking|flashing|steady|solid|glowing|lit)\s+(red|green|amber|yellow|blue|white|orange)\s+"
                   r"(?:LED|light|lamp|indicator)\b|\b(red|green|amber|yellow|blue|white|orange)\s+(?:LED|light|"
                   r"lamp|indicator)\s+(?:is\s+|was\s+)?(blinking|flashing|steady|solid|glowing|lit|on)\b", re.I)


def alarm_light(text):
    """The answer to "What does the alarm's light show?" when a file's own words name a light's colour and, where
    given, whether it blinks ("the LED is blinking red", "steady green light", "green light is on"); "" otherwise,
    and "" when two colours are named. The meaning of a colour differs by model, so the answer says to check."""
    seen = []
    for m in LIGHT.finditer(clean(text or "")):
        g = [x for x in m.groups() if x]
        colour = next((x.lower() for x in g if x.lower() in ("red", "green", "amber", "yellow", "blue", "white",
                                                            "orange")), "")
        how = next((x.lower() for x in g if x.lower() not in (colour,)), "")
        how = {"flashing": "blinking", "solid": "steady", "glowing": "lit", "on": "lit"}.get(how, how)
        seen.append((colour, how))
    colours = {c for c, _ in seen}
    if len(colours) != 1:
        return ""
    colour = colours.pop()
    hows = {h for _, h in seen if h} - {"lit"}
    how = hows.pop() if len(hows) == 1 else ""
    shown = f"a {how} {colour} light" if how else f"a {colour} light"
    return (f"The photo's own description says the alarm shows {shown}. What each light means differs from model to "
            f"model, so check the label on the back of the alarm or its manual.")


UNITS = {"kwh": "kWh", "kw h": "kWh", "kilowatt hours": "kWh", "kilowatt-hours": "kWh", "m3": "cubic metres",
         "m³": "cubic metres", "cubic metres": "cubic metres", "cubic meters": "cubic metres",
         "cubic feet": "cubic feet", "cu ft": "cubic feet", "ccf": "CCF (hundreds of cubic feet)",
         "gallons": "gallons", "litres": "litres", "liters": "litres"}
METER = re.compile(r"\b(?:reads|reading(?: of| is| was)?|shows|showing|displays|displaying|at)\s*:?\s+"
                   r"(\d[\d,. ]{0,12}\d|\d)\s*(kwh|kw h|kilowatt[- ]hours|m3|m³|cubic met(?:er|re)s|cubic feet|cu ft|"
                   r"ccf|gallons|lit(?:er|re)s)\b", re.I)


def meter_reading(text):
    """The answer to "What does the meter read?" when a file's own words give a reading with its unit ("the meter
    reads 04512 kWh", "reading of 1234.5 m3"); "" otherwise, or when two different readings are given."""
    found = [(m.group(1).strip(" ,."), UNITS[re.sub(r"\s+", " ", m.group(2).lower()).replace("meter", "metre")
                                             if m.group(2).lower() not in UNITS else m.group(2).lower()])
             for m in METER.finditer(clean(text or ""))]
    got = _one(found)
    return f"The photo's own description gives the reading as {got[0]} {got[1]}." if got else ""


SET = re.compile(r"\b(?:set (?:to|at)|reads|reading|shows|showing|displays|displaying|turned to|dial (?:is )?"
                 r"(?:on|at))\s+(?:a |an |the )?(-?\d{1,3}(?:\.\d)?\s*(?:°\s*[FC]?|degrees(?: [FC]| fahrenheit| "
                 r"celsius)?|F\b|C\b)|\d{1,2}:\d\d(?:\s*[ap]\.?m\.?)?|\d{1,3}\s*(?:minutes?|mins?|seconds?|"
                 r"hours?)|\"[^\"]{1,30}\"|'[^']{1,30}')", re.I)


def display_reading(text):
    """The answer to "What does the display or dial show?" when a file's own words give a setting or a reading with
    its unit ("set to 72 degrees", "shows 12:45", "dial is on 'Normal'"); "" otherwise, or when two are given."""
    got = _one(clean(m.group(1)).strip("\"'") for m in SET.finditer(clean(text or "")))
    return f"The photo's own description says it shows {got}." if got else ""


BREAKER_OFF = re.compile(r"\b(?:breakers?|switch)\s+(?:is |are |was |has been )?(tripped|switched off|turned off|in "
                         r"the off position|off)\b|\btripped (?:circuit )?breakers?\b", re.I)
BREAKER_ON = re.compile(r"\b(?:all )?(?:breakers?|switch(?:es)?)\s+(?:is |are |was )?(?:switched on|turned on|in the "
                        r"on position|on)\b", re.I)


def breaker_state(text):
    """The answer to "Is a breaker tripped or switched off?" only when a file's own words say a breaker is tripped or
    off ("tripped breaker", "the breaker is switched off"), or that all are on; "" otherwise, or when both."""
    text = clean(text or "")
    off, on = BREAKER_OFF.search(text), BREAKER_ON.search(text)
    if off and on:
        return ""
    if off:
        tripped = "trip" in off.group(0).lower()
        return ("The photo's own description says a breaker is " + ("tripped (it switched itself off)." if tripped
                                                                   else "switched off.") + " " + PANEL_NOTE)
    if on and re.search(r"\ball\b", on.group(0), re.I):
        return "The photo's own description says all the breakers are on."
    return ""


GAUGE = re.compile(r"\b(?:gauge|needle|pointer|indicator)\s+(?:needle\s+)?(?:is\s+|was\s+|points?\s+|pointing\s+)?"
                   r"(?:in|on|at|to|into)\s+(?:the\s+)?(green|red|recharge|overcharged?|empty|full)\b", re.I)


def gauge_state(text):
    """The answer to "What does the extinguisher's pressure gauge show?" only when a file's own words say where the
    needle is ("gauge in the green", "needle in the red"); "" otherwise, or when two places are named."""
    got = _one(m.group(1).lower() for m in GAUGE.finditer(clean(text or "")))
    if got in ("green", "full"):
        return "The photo's own description says the gauge needle is in the green: the extinguisher is charged."
    if got in ("red", "recharge", "empty", "overcharge", "overcharged"):
        return ("The photo's own description says the gauge needle is out of the green (in the red): the extinguisher "
                "may not work. Have it recharged or replaced.")
    return ""


TEMP = re.compile(r"(?<![\d.])(\d{2,3})\s*(?:°\s*|degrees\s*|deg\.?\s*)(F|C|fahrenheit|celsius)\b", re.I)
THERMOMETER = re.compile(r"\b(thermometers?|internal temperature|safe (minimum )?temperature|cooked to|reads|"
                         r"reaches|reached)\b", re.I)


def food_temperature(text):
    """The answer to "What temperature does the thermometer show?" when a file's own words name a thermometer (or an
    inside temperature) and one temperature with its unit ("the thermometer reads 165 °F"); "" otherwise, or when
    two different temperatures are named (a caption listing the safe temperatures is not a reading)."""
    text = clean(text or "")
    if not THERMOMETER.search(text):
        return ""
    got = _one((m.group(1), m.group(2)[0].upper()) for m in TEMP.finditer(text))
    if not got:
        return ""
    return f"The photo's own description gives the temperature as {got[0]} {got[1]}. {TEMP_NOTE}"


BRAILLE_WORD = re.compile(r"\bbraille\b", re.I)
NO_BRAILLE = re.compile(r"\b(no|without|lacks?|missing)\s+(\w+\s+)?braille\b", re.I)


def braille_said(text):
    """The answer to "Is there braille here?" for lift buttons when a file's own words or categories say braille
    (and do not say there is none); ""."""
    text = clean(text or "")
    if BRAILLE_WORD.search(text) and not NO_BRAILLE.search(text):
        return "Yes: the photo's own record says there is braille here, beside or on the buttons."
    return ""


# ----------------------------------------------------------------- the rows of one file

def topic(root, depth=1, prefer=WHAT_Q, state_only=False, readers=()):
    """One Commons topic: its root category, how many levels of subcategories to walk, the question asked first, and
    state_only=True for a category another pack already shows (a file is kept only when this pack adds a NEW
    question for it: a reading, a light, a gauge, a kind, braille). readers: the reader names to run on the file's
    own words ("light", "meter", "display", "breaker", "gauge", "temperature", "braille")."""
    return {"root": root, "depth": depth, "prefer": prefer, "state_only": state_only, "readers": tuple(readers)}


READERS = {"light": (LIGHT_Q, alarm_light), "meter": (READING_Q, meter_reading),
           "display": (DISPLAY_Q, display_reading), "breaker": (BREAKER_Q, breaker_state),
           "gauge": (GAUGE_Q, gauge_state), "temperature": (TEMP_Q, food_temperature),
           "braille": (BRAILLE_Q, braille_said)}


def rule_rows(categories, prefer=None):
    """The rows the RULES give for a file from its categories (the one it was found in first): one per question, the
    first match winning, except that a ONE_STATE question with two different answers gives nothing."""
    answers = collections.OrderedDict()
    for c in categories:
        for pattern, question, said in RULES:
            if pattern.search(c):
                answers.setdefault(question, [])
                if said not in answers[question]:
                    answers[question].append(said)
    rows = [{"question": q, "answer": said[0]} for q, said in answers.items()
            if not (q in ONE_STATE and len(said) > 1)]
    rows.sort(key=lambda r: r["question"] != prefer)
    return rows


def file_place(title, cats):
    """Where a photo was taken: the USA or Canada when one of its categories says "in the United States" or "in
    Canada" (or a US state), else the country at the camera's coordinates; "" when nothing says."""
    for c in cats:
        if re.search(r"\bin (the )?(United States|USA|U\.S\.)\b|\((U\.S\. )?state\)", c):
            return USA
        if re.search(r"\bin Canada\b", c):
            return CANADA
    return PLACES.get(title, "")


def file_rows(title, credit, text, raw, found_in, cats, t):
    """The rows of one Commons file: the RULES rows from its categories, the readers' rows from its own title and
    description, and its English caption ("Describe this picture."); [] for a state_only topic's file that gets no
    new question."""
    all_cats = [found_in] + [c for c in cats if c != found_in]
    rows = rule_rows(all_cats, prefer=t["prefer"])
    words = f"{title.split(':', 1)[-1].rsplit('.', 1)[0].replace('_', ' ')}. {raw}"
    have = {r["question"] for r in rows}
    for name in t["readers"]:
        question, read = READERS[name]
        said = read(words if name != "braille" else f"{words} {' '.join(all_cats)}")
        if said and question not in have:
            rows.insert(1, {"question": question, "answer": said})
            have.add(question)
    if t["state_only"] and not have & NEW_QUESTIONS:
        return []
    text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
    if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
        rows.append({"question": DESCRIBE_Q, "answer": text})
    place = file_place(title, all_cats)
    facts = {"commons_category": found_in, "commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0]}
    return [dict(r, credit=credit, facts=facts, **where(place)) for r in rows]


# ----------------------------------------------------------------- the Commons builder

def walk(s, root, depth):
    """The root category and its subcategories down to depth levels, leaving out those SKIP names, each once."""
    found, level = [root], [root]
    for _ in range(depth):
        nxt = []
        for c in level:
            if listing_out_of_time():
                return found
            for sub in commons_members(s, c, "subcat"):
                name = sub.split(":", 1)[-1]
                if name not in found and not SKIP.search(name):
                    found.append(name)
                    nxt.append(name)
        level = nxt
    return found


def topic_files(s, t, seen):
    """[(file title, the category it was found in)] for a topic, shuffled the same way each time (a different way on
    a top-up pass), drawings and art left out by their names."""
    found = {}
    for category in walk(s, t["root"], t["depth"]):
        if listing_out_of_time():
            break
        for title in commons_members(s, category, "file"):
            if title not in seen and not NOT_A_PHOTO.search(title):
                found.setdefault(title, category)
    files = list(found.items())
    pass_random(len(t["root"]) * 7919 + sum(map(ord, t["root"]))).shuffle(files)
    return files


def safety_commons(topics, limit, prefix, key, people=False):
    """A Commons pack from topics: the topics take turns, in a fixed shuffled order, so each gets an even share. Each
    file's licence is checked (mechanical_packs.mech_entries: CC0, public domain or CC BY), files whose words name
    nudity or harm are left out, a state_only topic's file is kept only with a new question, and a free file of a
    new topic with no answer is set aside for a description. people: the pack shows people (public places)."""
    s, items, seen = session(), [], set()
    order = list(topics)
    random.Random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    want = int(limit * 1.15) + 2
    queues = [[t, None] for t in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            if listing_out_of_time():
                say(f"  {prefix}: stopped looking at half the time limit")
                queues = []
                break
            t, files = q
            try:
                if files is None:
                    files = topic_files(s, t, seen)
                    say(f"Commons {t['root']}: {len(files)} files")
                batch, q[1] = files[:share * 2], files[share * 2:]
                if not batch:
                    queues.remove(q)
                    continue
                found_in = dict(batch)
                entries = mech_entries(s, [title for title, _ in batch])
                cats = file_categories(s, [e[0] for e in entries])
            except RuntimeError as e:          # Commons kept refusing: keep what was found and stop asking
                say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                queues = []
                break
            got = 0
            for title, url, credit, text, raw in entries:
                if got >= share or title in seen:
                    continue
                words = NOT_A_CHILD.sub(" ", f"{title} {text} {' '.join(cats.get(title, []))}")
                if NUDE.search(words) or NOT_SHOWN.search(words):
                    considered(title, url, "its words are about nudity, underwear or swimwear")
                    continue
                if HARM.search(words):
                    considered(title, url, "its words name a fire, an injury or a death (an everyday pack)")
                    continue
                seen.add(title)
                rows = file_rows(title, credit, text, raw, found_in.get(title, t["root"]), cats.get(title, []), t)
                if not rows:
                    if t["state_only"]:
                        considered(title, url, "another pack already shows this category, and its words give no "
                                               "reading, light, gauge or kind")
                        continue
                    needs_description(file_name(prefix, title), url, credit, credit.rsplit(", ", 2)[-2],
                                      text=text, title=title, reason="no label this pack can read and no English "
                                                                     "caption",
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"commons_category": found_in.get(title, t["root"]),
                                             "child": bool(CHILD.search(words)), "not_for_picture_making": people})
                    considered(title, url, "no answer: set aside for a description")
                    continue
                items.append((file_name(prefix, title), url, [mark_child(r, words) for r in rows]))
                got += 1
            if not q[1]:
                queues.remove(q)
    random.Random(prefix + "-order").shuffle(items)
    fetched = commons_fetch(items[:want])[:limit]
    say(f"{key}: {len(fetched)} pictures")
    return with_twins(fetched)


HOME_TOPICS = [
    topic("Distribution boards", 1, WHAT_Q, readers=("breaker",)),
    topic("Fuse boxes", 1, WHAT_Q, readers=("breaker",)),
    topic("Circuit breakers", 1, WHAT_Q, readers=("breaker",)),
    topic("Gas meters", 1, WHAT_Q, readers=("meter",)),
    topic("Smart meters", 1, WHAT_Q, readers=("meter",)),
    topic("Stopcocks", 1, WHAT_Q),
    topic("Sump pumps", 0, WHAT_Q),
    topic("Gas furnaces", 1, WHAT_Q),
    topic("Electronic electricity meters", 1, WHAT_Q, readers=("meter",)),
    topic("Mold on buildings", 1, WHAT_Q),
    # already shown by other packs: kept only with a new question
    topic("Smoke detectors", 2, LIGHT_Q, True, ("light",)),
    topic("Carbon monoxide detectors", 0, LIGHT_Q, True, ("light", "display")),
    topic("Water meters", 1, READING_Q, True, ("meter",)),
    topic("Thermostats", 1, DISPLAY_Q, True, ("display",)),
    topic("Microwave ovens", 1, DISPLAY_Q, True, ("display",)),
    topic("Washing machines", 1, DISPLAY_Q, True, ("display",)),
    topic("Dishwashers", 1, DISPLAY_Q, True, ("display",)),
    topic("Clothes dryers", 1, DISPLAY_Q, True, ("display",)),
    topic("Electric ovens", 1, DISPLAY_Q, True, ("display",)),
    topic("Fire extinguishers", 1, KIND_Q, True, ("gauge",)),
    topic("Fire extinguishers in the United States", 0, GAUGE_Q, True, ("gauge",)),
    topic("Water damage", 1, WHAT_Q, True),
    topic("Tankless water heaters controllers", 1, DISPLAY_Q, True, ("display",)),
]
FOOD_TOPICS = [
    topic("Green bananas", 1, RIPE_Q),
    topic("Unripe tomatoes", 0, RIPE_Q),
    topic("Meat thermometers", 0, TEMP_Q, True, ("temperature",)),
]
ACCESS_TOPICS = [
    topic("Braille signage", 1, BRAILLE_Q),
    topic("Bus stop signs", 1, SIGN_Q),
    topic("Bus stop signs in the United States", 1, SIGN_Q),
    topic("Ticket machines in the United States", 1, WHAT_Q),
    topic("Elevator buttons", 1, BRAILLE_Q, True, ("braille",)),
]


def build_commons_home_safety(limit):
    """Breaker panels, fuse boxes, meters, stopcocks, sump pumps, furnaces; alarms, displays and gauges with a
    stated state."""
    return safety_commons(HOME_TOPICS, limit, "homesafe", "commons_home_safety")


def build_commons_food_state(limit):
    """Ripeness, mould, rot and doneness from Commons categories; thermometer readings from the file's words."""
    return safety_commons(FOOD_TOPICS, limit, "foodstate", "commons_food_state")


def build_commons_access_features(limit):
    """Braille signage, bus stop signs, US ticket machines, and lift buttons with braille."""
    return safety_commons(ACCESS_TOPICS, limit, "access", "commons_access_features", people=True)


# ----------------------------------------------------------------- usda_food_safety_photos

USDA_STREAM = "Files from U.S. Department of Agriculture Flickr stream"
# Commons searches (CirrusSearch, files in the USDA stream) whose words are about food safety at home.
USDA_SEARCHES = ["food thermometer", "meat thermometer", "food safety", "internal temperature", "leftovers",
                 "thawing", "refrigerator temperature", "wash hands food", "cutting board raw", "mold food",
                 "cooked to", "food safe"]
FOOD_SAFETY_WORDS = re.compile(r"\b(food safety|foodsafety|thermometers?|internal temperature|safe (minimum )?"
                               r"temperatures?|leftovers?|thaw\w*|refrigerat\w*|fridge|freezer|cross[- ]contaminat\w*|"
                               r"cutting boards?|wash(ing)? (your )?hands|raw (meat|poultry|chicken|eggs?)|mou?ld\w*|"
                               r"spoil\w*|food ?borne|cooked to|undercooked)\b", re.I)


def usda_rows(caption, credit):
    """The rows of one USDA photo: its caption as the description, and the temperature where the caption names a
    thermometer and one temperature; [] when the caption is not about food safety, is too short, or is about an
    official event."""
    if not caption or len(caption.split()) < 6 or not in_english(caption):
        return []
    if OFFICIAL.search(caption) or HARM.search(caption) or NUDE.search(caption) or not FOOD_SAFETY_WORDS.search(caption):
        return []
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit}]
    temp = food_temperature(caption)
    if temp:
        rows.insert(0, {"question": TEMP_Q, "answer": temp, "credit": credit})
    return rows


def usda_search(s, words, most=200):
    """File titles in the USDA Flickr stream whose page matches words (Commons search, 50 a request)."""
    titles, offset = [], 0
    while offset < most and not listing_out_of_time():
        data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": 50,
                               "sroffset": offset, "srprop": "",
                               "srsearch": f'incategory:"{USDA_STREAM}" {words}'})
        found = [m["title"] for m in (data.get("query") or {}).get("search", [])]
        titles += found
        if len(found) < 50 or "continue" not in data:
            break
        offset += 50
        time.sleep(1)
    return titles


def build_usda_food_safety_photos(limit):
    """USDA's own food safety photos (their Commons copies), the agency's captions as answers."""
    s, rng, items, seen = session(), pass_random(1862), [], set()
    titles = []
    for words in USDA_SEARCHES:
        if listing_out_of_time():
            break
        got = [t for t in usda_search(s, words) if t not in titles and not NOT_A_PHOTO.search(t)]
        say(f"Commons search {words!r} in the USDA stream: {len(got)} files")
        titles += got
    rng.shuffle(titles)
    for start in range(0, len(titles), 50):
        if listing_out_of_time() or len(items) >= limit * 1.15:
            break
        for title, url, credit, raw, year in agency_entries(s, titles[start:start + 50]):
            if title in seen:
                continue
            seen.add(title)
            rows = usda_rows(agency_caption(raw), credit)
            if not rows:
                considered(title, url, "its caption is not about food safety, is too short, or is about an event")
                continue
            items.append((file_name("usdafs", title), url, [mark_child(r, f"{title} {raw}") for r in rows]))
    rng.shuffle(items)
    fetched = commons_fetch(items[:int(limit * 1.1) + 2])[:limit]
    say(f"usda_food_safety_photos: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
HOME_SAFETY_PACKS = {
    "commons_home_safety": (build_commons_home_safety, COMMONS_CREDIT.format(
        what="categories of breaker panels, fuse boxes, circuit breakers, gas and smart meters, stopcocks, sump pumps "
             "and gas furnaces, and of smoke and CO alarms, thermostats, appliance panels, water meters, fire "
             "extinguishers and water damage where the file's own words give a reading, light, gauge or kind; "
             "safety notes from public guidance")),
    "commons_food_state": (build_commons_food_state, COMMONS_CREDIT.format(
        what="categories of unripe fruit, mould and rot on food, meat doneness and meat thermometers (a temperature "
             "only where the file states it); food safety notes from USDA guidance")),
    "usda_food_safety_photos": (build_usda_food_safety_photos,
                                "US Department of Agriculture photos (public domain, works of the US government, "
                                "17 U.S.C. 105), from their Wikimedia Commons copies in Category:Files from U.S. "
                                "Department of Agriculture Flickr stream, found by Commons search; each file's "
                                "licence checked there. Answers from the agency's own captions."),
    "commons_access_features": (build_commons_access_features, COMMONS_CREDIT.format(
        what="categories of braille signage, bus stop signs, US ticket machines, and lift buttons whose record says "
             "they have braille")),
}

# How many pictures a full build takes from each (Commons answers about one picture a second).
HOME_SAFETY_LIMITS = {
    "commons_home_safety": 1200,       # about 600 files in the new topics, plus the stated states of the others
    "commons_food_state": 400,         # bananas 176, tomatoes 80, and the food categories found
    "usda_food_safety_photos": 400,    # the stream's food safety photos
    "commons_access_features": 500,    # braille signage 146, bus stop signs about 250, US ticket machines about 200
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one home safety, food state or accessibility pack builder.")
    parser.add_argument("key", choices=sorted(HOME_SAFETY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = HOME_SAFETY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
