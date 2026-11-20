"""Pack builders for US and CANADIAN STREET SCENES as a pedestrian meets them, used by build_packs.py in the same way
as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}, plus "place" ("Ontario, Canada"), "child": true where the words of a picture name a
child, and "facts" (the Commons category it came from). A picture with more than one question comes once with its
JPEG and then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit
counts pictures.

Why: a describer for blind people should say what a pedestrian needs at a street: whether there is a crosswalk and
of what kind, a curb ramp, detectable warning strips (tactile paving), a pedestrian signal and its push button, what
colour the traffic light shows, and what the road, the signs and the neighbourhood are like. Answers are fixed
sentences written here from each source's own labels (a Commons category's name, an agency's own caption), never by
an AI model.

NEVER GUESS A SIGNAL STATE. "What colour is the traffic light showing?" is asked only where Commons files the photo
in a "Traffic lights at red (yellow, green, dark) state" category, and never when the same photo is filed under two
states. "What does the pedestrian signal show?" is asked only where the file's own title or description says it in
so many words ("showing the walking person", "countdown at 8"), and never when it names both walk and don't walk
(ped_signal_state). Every other signal photo is asked what is there ("Is there a pedestrian signal?"), not its state.

The packs (all open: CC0, public domain or CC BY, checked file by file at the source, November 2026):
  commons_crosswalks_signals  Wikimedia Commons, US and Canadian categories and their state, province and city
                        subcategories: crosswalks by style (continental, standard, ladder, zebra, raised, twin
                        parallel lines, rainbow, scrambles, unmarked), curb cuts, tactile paving in the US,
                        pedestrian signals, push buttons and audible (accessible) pedestrian signals, countdown
                        signals, HAWK beacons (pedestrian hybrid beacons), rectangular rapid flashing beacons,
                        flashing yellow arrows, and traffic lights at red, yellow, green and dark state.
  commons_streets_roads_na  Commons, US and Canada: street name signs, roundabouts, highway interchanges and their
                        ramps, freeways, school zone signs, road works (construction zones) and traffic cones, bike
                        (cycle) lanes, bus stops and shelters, sidewalks and things blocking them, and speed bumps.
                        (Stop, yield, speed-limit and pedestrian-crossing sign photos are us_road_signs' and
                        ca_road_signs'; "Streets in <city>" are commons_us_streets' and commons_ca_streets'.)
  commons_neighbourhoods_na Commons: US suburbs and residential areas, and US and Canadian driveways and porches
                        (Commons has no files in "Suburbs in Canada" or "Residential areas in Canada").
  us_dot_street_photos  US Federal Highway Administration photos on Commons (public domain, works of the US
                        government): its Interstate Photo Gallery (captioned photos of the interstates, their
                        interchanges and ramps, 1950s to 1970s) and the photos of its Flickr stream whose own caption
                        names a road, street, crossing, intersection, sidewalk, bike lane, work zone or the like; the
                        agency's caption is the answer, the state from the gallery's file name ("GA 6 I20 I75 ...").

Not repeated: ptl_crossings (pedestrian lights in Shanghai, ImVisible), open_images_street (Open Images labels for
crossings, curbs, traffic lights, stop signs and street lights: an Open Images traffic pack would ask the same
questions of the same photos), us_road_signs, ca_road_signs, safety_signs, commons_us_streets, commons_ca_streets,
commons_state_roads (state DOT photo streams), commons_disability (its "Tactile paving" categories) and loc_highsmith.
Share-alike, non-commercial and research collections on the same subject (Commons BY-SA files, LISA, Bosch, BDD100K,
Mapillary, KartaView) are entries or notes in training-kit/kit/street_scene_sources.py.

Safety (packs/SOURCE-RULES.md): no sexual content (NUDE, us_packs.NOT_SHOWN); no crash, injury or death photos
(HARM: these are everyday packs); every row whose words name a child is marked "child" (school zones often show
children). People walk through many of these photos, so all four packs are never used for picture-making (the kit's
PEOPLE_AND_BODILY_PACK_KEYS). A free photo dropped only because it has no answer (no label this pack can read and no
English caption) is set aside for a description (build_packs.needs_description).

    python packs/street_scene_packs.py commons_crosswalks_signals --limit 8      (prints a few rows: a quick check)
"""

import collections
import json
import math
import random
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from food_packs import with_twins, count_pictures, commons_members
from home_packs import commons_fetch, file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import mech_entries, in_english, PLACES, JUST_A_RECORD, NOT_A_CHILD, NOT_A_PHOTO
from land_industry_packs import US_STATE_CODES
from canada_packs import PROVINCES, TERRITORIES
from us_packs import NOT_SHOWN, file_categories
from us_modern_packs import agency_entries, agency_caption, only_the_name, sample_members, OFFICIAL
from places import where, place_name

WHAT_Q = "What is this?"
PLACE_Q = "What kind of place is this?"
DESCRIBE_Q = "Describe this picture."
CROSSWALK_Q = "Is there a crosswalk here?"
CROSSWALK_KIND_Q = "What kind of crosswalk is this?"
CURB_Q = "Is there a curb ramp here?"
TACTILE_Q = "Is there tactile paving here?"
PED_SIGNAL_Q = "Is there a pedestrian signal here?"
PED_STATE_Q = "What does the pedestrian signal show?"
BUTTON_Q = "Is there a push button for the walk signal?"
LIGHT_Q = "What colour is the traffic light showing?"
SIGNAL_KIND_Q = "What kind of traffic signal is this?"
SIGN_Q = "What does this sign tell me?"
ROAD_Q = "What kind of road is this?"
WHERE_Q = "Where was this photo taken?"
USA, CANADA = "USA", "Canada"

# Questions whose answer is a state that cannot be two things at once: when a photo's categories give two
# different answers to one of these, neither is used.
ONE_STATE = {LIGHT_Q, PED_STATE_Q}

CHECK_PED = "Check the pedestrian signal and listen for turning cars before you cross."
# ----------------------------------------------------------------- answers, from the category names

CROSSWALK_YES = "Yes, there is a crosswalk: a marked place for people to cross the street."
CROSSWALK_KINDS = [
    (r"\bcontinental crosswalks?\b", "It is a continental crosswalk: wide white bars side by side across the street, "
                                     "each bar running the same way as the traffic."),
    (r"\b(standard crosswalks?|twin parallel line crosswalks?)\b",
     "It is a crosswalk marked with two parallel white lines across the street; you cross between them."),
    (r"\bladder crosswalks?\b", "It is a ladder crosswalk: two white lines across the street with wide bars between "
                                "them, like the rungs of a ladder."),
    (r"\bzebra (crosswalks?|crossings?)\b", "It is a zebra crosswalk: white stripes across the street."),
    (r"\braised (pedestrian crossings?|crosswalks?)\b",
     "It is a raised crosswalk: the crossing is built up to the height of the sidewalk, like a wide speed hump, so "
     "cars slow down and you cross on the level."),
    (r"\b(rainbow|colou?rful) (pedestrian crossings?|crosswalks?)\b",
     "It is a painted crosswalk in bright colours (a rainbow crosswalk)."),
    (r"\bpedestrian scrambles?\b", "It is a pedestrian scramble: all the cars stop at once and people may cross every "
                                   "way, even diagonally, while the walk signal is on."),
    (r"\bunmarked pedestrian crossings?\b", "It is an unmarked crossing: there are no painted lines, so drivers may "
                                            "not expect people to cross here."),
]
LIGHT_STATES = {
    "red": "The traffic light is red: traffic facing it must stop.",
    "yellow": "The traffic light is yellow (amber): it is about to turn red, and traffic facing it should stop if it "
              "safely can.",
    "green": "The traffic light is green: traffic facing it may go. A green light for cars does not always mean it is "
             "safe to cross; " + CHECK_PED[0].lower() + CHECK_PED[1:],
    "dark": "The traffic light is dark (switched off). Drivers must treat a dark signal as an all-way stop, so take "
            "extra care: cars may not stop for you.",
}
PED_SIGNAL = ("Yes, there is a pedestrian signal: the light that shows a walking person when you may start to cross "
              "and a raised hand when you should not.")
BUTTON = ("Yes, there is a pedestrian push button. Press it to ask for the walk signal; at many crossings the walk "
          "signal does not come on unless someone presses it.")
ACCESSIBLE_BUTTON = ("Yes, this is an accessible pedestrian signal: a push button that ticks so you can find it, often "
                     "with a raised arrow that points the way to cross, and that speaks, beeps or vibrates when the "
                     "walk signal is on.")
CURB = "Yes, there is a curb ramp (a curb cut), where the sidewalk slopes down to the street."
TACTILE = ("Yes, there is tactile paving: detectable warning strips of raised bumps (truncated domes), often yellow, "
           "that you can feel with your feet or cane, warning of the edge of the street or a platform.")

# One rule per kind of thing: (pattern on a category name, question, answer). A file gets the rows of every rule
# that its own category (the one it was found in) or any of its other categories matches; ONE_STATE questions with
# two different answers are dropped.
RULES = [
    (r"\b(crosswalks?|pedestrian crossings?|zebra crossings?|pedestrian scrambles?)\b(?! signs?)", CROSSWALK_Q,
     CROSSWALK_YES),
] + [(p, CROSSWALK_KIND_Q, a) for p, a in CROSSWALK_KINDS] + [
    (r"\btraffic lights at red state\b", LIGHT_Q, LIGHT_STATES["red"]),
    (r"\btraffic lights at yellow state\b", LIGHT_Q, LIGHT_STATES["yellow"]),
    (r"\btraffic lights at green state\b", LIGHT_Q, LIGHT_STATES["green"]),
    (r"\btraffic lights at dark state\b", LIGHT_Q, LIGHT_STATES["dark"]),
    (r"\bpedestrian signals in\b", PED_SIGNAL_Q, PED_SIGNAL),
    (r"\b(pedestrian signal push buttons|R10-3\b|R10-4\b)", BUTTON_Q, BUTTON),
    (r"\baudible traffic signals\b", BUTTON_Q, ACCESSIBLE_BUTTON),
    (r"\bcountdown traffic signals\b", SIGNAL_KIND_Q,
     "It is a countdown signal: its numbers count down the seconds left to finish crossing before the signal "
     "changes. If the countdown has started and you have not, wait for the next walk signal."),
    (r"\bHAWK beacons\b", SIGNAL_KIND_Q,
     "It is a pedestrian hybrid beacon (a HAWK signal): it stays dark until someone presses the crossing button, then "
     "flashes yellow and turns solid red to stop the cars, and the walk signal comes on."),
    (r"\bRectangular Rapid Flashing Beacons\b", SIGNAL_KIND_Q,
     "These are rectangular rapid flashing beacons: yellow lights beside a crosswalk sign that flash quickly when "
     "someone presses the button, to warn drivers. They do not stop the traffic, so wait until cars have stopped."),
    (r"\bFlashing yellow arrow\b", SIGNAL_KIND_Q,
     "It is a flashing yellow arrow signal: when it flashes, drivers may turn left but must give way to oncoming "
     "traffic and to people crossing."),
    (r"\bcurb cuts\b", CURB_Q, CURB),
    (r"\btactile paving\b", TACTILE_Q, TACTILE),
    # commons_streets_roads_na
    (r"\bstreet signs\b", SIGN_Q, "It is a street name sign, showing the name of the street, usually on a pole at a "
                                  "corner."),
    (r"\broundabouts\b(?! signs?)", PLACE_Q,
     "This is a roundabout: traffic goes one way around a central island and drivers entering give way to traffic "
     "already in it. People cross the roads leading into it, away from the circle, often in two stages."),
    (r"\binterchange ramps\b", ROAD_Q, "This is a highway ramp, where traffic joins or leaves a highway at an "
                                       "interchange (an on-ramp or off-ramp)."),
    (r"\binterchanges\b", PLACE_Q, "This is a highway interchange, where ramps and bridges connect one highway to "
                                   "another."),
    (r"\bfreeways\b", ROAD_Q, "This is a freeway: a divided highway for fast traffic, entered only by ramps, with no "
                              "crossings at street level. People may not walk on it."),
    (r"\bschool zone (warning road signs|speed limit road signs|road signs)\b|\bS1-1\b", SIGN_Q,
     "It is a school zone sign: a school is near and children may be crossing, so drivers must slow down, often to a "
     "lower speed limit at set times."),
    (r"\bEnd School Zone\b|\bS5-2\b", SIGN_Q, "It is an End School Zone sign: the slower school-zone speed limit ends "
                                             "here."),
    (r"\bschool crossing signs\b", SIGN_Q, "It is a school crossing sign: children cross the road here on their way to "
                                           "school."),
    (r"\broadworks\b", PLACE_Q, "This is road work (a construction zone). Watch for cones, barriers, open trenches, "
                                "closed sidewalks and detours."),
    (r"\btraffic cones\b", WHAT_Q, "These are traffic cones, marking road work or a hazard; they are easy to walk "
                                   "into."),
    (r"\bcycle lanes\b", ROAD_Q, "This is a bike lane: a part of the street marked for bicycles. Look out for "
                                 "cyclists when you cross it, even where the cars have stopped."),
    (r"\bbus stops\b", PLACE_Q, "This is a bus stop."),
    (r"\bbus shelters\b", PLACE_Q, "This is a bus shelter at a bus stop: a small roofed place to wait for the bus."),
    (r"\bsidewalks\b", PLACE_Q, "This is a sidewalk, the path for people walking beside the street."),
    (r"\bsidewalk obstructions\b", WHAT_Q, "Something is blocking the sidewalk, in the way of people walking."),
    (r"\bspeed bumps\b|\btraffic calming\b", ROAD_Q,
     "This street has traffic calming, such as a speed bump (a raised hump across the road) to slow the cars down."),
    # commons_neighbourhoods_na
    (r"\bsuburbs\b", PLACE_Q, "This is a suburban street: a quiet residential area of houses, usually with lawns and "
                              "driveways, outside a city centre."),
    (r"\bresidential areas\b", PLACE_Q, "This is a residential neighbourhood: a street of homes."),
    (r"\bdriveways\b", WHAT_Q, "This is a driveway, where cars cross the sidewalk to reach a house or garage; listen "
                               "for cars backing out."),
    (r"\bporches\b", WHAT_Q, "This is a porch: a covered area at the entrance of a house."),
]
RULES = [(re.compile(p, re.I), q, a) for p, q, a in RULES]

# Subcategories that are not photos of the thing, or are of another place: drawings, aerial views, art, history,
# railways and stations, police, people, parking, signs about the thing (under its own category), and US insular
# areas.
SKIP = re.compile(r"\b(diagrams?|drawings?|aerial|art|artistic|historic|history|videos?|maps?|logos?|museums?|"
                  r"by year|quality images|walks of fame|moving sidewalks|sidewalk doors|sidewalk caf\w*|stations?|"
                  r"light rail|level crossings?|railways?|police|people|persons|queues|waiting|cabinets|parking|"
                  r"insular|puerto rico|guam|virgin islands|samoa|mariana|night|in winter|snow|construction of|"
                  r"advance entrance|guide signs|arrow-per-lane|walks? of|signs on university|route 66|"
                  r"bus turning places|cyclists|bicycles|accidents?|collisions?|crash\w*)\b", re.I)
# Words that leave a file out: crashes, injuries and death (everyday packs), and protests or police action.
HARM = re.compile(r"\b(crash\w*|collisions?|accidents?|wreck\w*|killed|dead|deaths?|died|fatal\w*|injur\w*|wounded|"
                  r"blood\w*|bod(y|ies)|memorial|ghost bike|shooting|riot\w*|protest\w*|arrest\w*|police "
                  r"(car|line|tape))\b", re.I)


def topic(root, depth=2, country=USA, prefer=None):
    """One Commons topic: its root category, how many levels of subcategories to walk ("by state" and "by city"
    categories need two), the country, and the rule its files are asked about first."""
    return {"root": root, "depth": depth, "country": country, "prefer": prefer}


def category_place(category, country):
    """The place a category names ("Pedestrian signals in Georgia (U.S. state)" -> "Georgia, USA", "Traffic lights at
    red state in Toronto" -> "Toronto, Canada", "... in the United States" -> "USA"); the country when it names
    none."""
    m = re.search(r"\bin (?:the )?([A-Z][^()]*?)(?: \((?:U\.S\. )?state\))?(?: by \w+.*)?$", category)
    if not m:
        return country
    name = m.group(1).strip()
    if name in ("United States", "United States of America", "USA"):
        return USA
    if name == "Canada":
        return CANADA
    if name in ("Washington, D.C.", "District of Columbia"):
        return "Washington, D.C., USA"
    if name in US_STATE_CODES.values():
        return place_name(name, USA)
    if name in PROVINCES + TERRITORIES:
        return place_name(name, CANADA)
    if name.startswith(("New York City", "NYC")):
        return "New York City, New York, USA"
    return place_name(name.split(",")[0], country)


def walk(s, root, depth):
    """[(category, its place)] for a topic: the root and its subcategories down to depth levels, leaving out those
    SKIP names, each once."""
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


def rule_rows(categories, prefer=None):
    """The rows the RULES give for a file from its categories (the one it was found in first): one per question, the
    first match winning, except that a ONE_STATE question with two different answers gives nothing. prefer: the
    question asked first (the topic's own)."""
    answers = collections.OrderedDict()
    for c in categories:
        for pattern, question, answer in RULES:
            if pattern.search(c):
                answers.setdefault(question, [])
                if answer not in answers[question]:
                    answers[question].append(answer)
    rows = []
    for question, said in answers.items():
        if question in ONE_STATE and len(said) > 1:
            continue
        if question == CROSSWALK_KIND_Q and len(said) > 1:
            continue                                   # two crosswalk styles: not sure which one shows
        rows.append({"question": question, "answer": said[0]})
    rows.sort(key=lambda r: r["question"] != prefer)
    return rows


# The words that say, in a file's own title or description, what a pedestrian signal shows. Both walk and don't walk
# named -> nothing (the text is about the signal, not its state).
SHOWING = r"(?:showing|shows|displaying|displays|lit(?: up)?|illuminated|reads|reading|with the|on)"
WALK_STATE = re.compile(rf"\b{SHOWING}\W+(?:a |an |the )?(?:white )?(?:\"?walk\"?(?: sign(?:al)?| symbol| light)?|"
                        r"walking (?:person|man|figure|pedestrian)(?: symbol| light)?)\b", re.I)
STOP_STATE = re.compile(rf"\b{SHOWING}\W+(?:a |an |the )?(?:flashing |steady |solid )?(?:orange |red |raised |upraised "
                        r")*(?:hand|\"?don'?t walk\"?|\"?do not walk\"?)\b", re.I)
COUNTDOWN = re.compile(r"\bcount(?:ing)?[- ]?down(?: timer| display| signal)?\W+(?:at|showing|shows|reading|reads|of|"
                       r"displaying|on)\W+(\d{1,2})(?:\s*(?:seconds?|secs?)\b)?(?=\s*(?:$|[.,;:)!]|remaining\b|left\b))",
                       re.I)
# The same said the other way round: "the walking person is lit", "a red hand illuminated".
WALK_AFTER = re.compile(r"\b(?:walking (?:person|man|figure|pedestrian)|\"?walk\"? (?:symbol|signal|light))\W+(?:is |was )?"
                        r"(?:lit|on|illuminated|showing|displayed)\b", re.I)
STOP_AFTER = re.compile(r"\b(?:hand|\"?don'?t walk\"?)(?: symbol| signal| light)?\W+(?:is |was )?(?:lit|on|illuminated|"
                        r"showing|displayed|flashing)\b", re.I)
BOTH_NAMED = re.compile(r"\bwalk\b.*\b(don'?t walk|do not walk|hand)\b|\b(don'?t walk|do not walk|hand)\b.*"
                        r"\bwalk(ing)?\b(?! signal)", re.I)
NOT_A_STATE = re.compile(r"\b(sign|signs|icon|symbol on|sticker|diagram|drawing|button reads)\b.*\b(walk|hand)\b|"
                         r"\b(both|either|alternat\w*|and the|or the)\b", re.I)


def ped_signal_state(text):
    """The answer to "What does the pedestrian signal show?" when a file's own words say it plainly ("Pedestrian
    signal showing the walking person", "countdown at 8"); "" otherwise. Never a guess: words naming both walk and
    don't walk, or describing a sign or symbol rather than a lit signal, give "", and so do numbers that are not
    seconds."""
    text = clean(text or "")
    if not text or not re.search(r"\b(pedestrian|walk|crossing|crosswalk|countdown|signal)\b", text, re.I):
        return ""
    count = COUNTDOWN.search(text)
    walk_on = WALK_STATE.search(text) or WALK_AFTER.search(text)
    stop_on = STOP_STATE.search(text) or STOP_AFTER.search(text)
    if NOT_A_STATE.search(text) or (walk_on and stop_on) or (walk_on and count):
        return ""
    if count and 1 <= int(count.group(1)) <= 99:
        n = int(count.group(1))
        return (f"The pedestrian countdown shows {n}: about {n} second{'s' if n != 1 else ''} "
                f"{'are' if n != 1 else 'is'} left before the signal changes to don't walk. If you have not started "
                f"to cross, wait for the next walk signal.")
    if stop_on and not walk_on:
        return "The pedestrian signal shows the raised hand (don't walk): do not start to cross."
    if walk_on and not BOTH_NAMED.search(text):
        return ("The pedestrian signal shows the walking person: the walk signal is on. Listen for turning cars before "
                "you cross.")
    return ""


# ----------------------------------------------------------------- the Commons packs

CROSSWALK_TOPICS = [
    topic("Pedestrian crossings in the United States by style", 2, USA, CROSSWALK_KIND_Q),
    topic("Crosswalks in the United States by city", 2, USA, CROSSWALK_Q),
    topic("Pedestrian crossings in the United States by state", 2, USA, CROSSWALK_Q),
    topic("Pedestrian crossings in Canada", 1, CANADA, CROSSWALK_KIND_Q),
    topic("Pedestrian crossings in Canada by province or territory", 2, CANADA, CROSSWALK_Q),
    topic("Pedestrian crossings in Canada by city", 1, CANADA, CROSSWALK_Q),
    topic("Raised pedestrian crossings", 0, "", CROSSWALK_KIND_Q),
    topic("Curb cuts in the United States", 1, USA, CURB_Q),
    topic("Tactile paving in the United States", 1, USA, TACTILE_Q),
    topic("Pedestrian signals in the United States", 1, USA, PED_SIGNAL_Q),
    topic("Pedestrian signals in Canada", 1, CANADA, PED_SIGNAL_Q),
    topic("Pedestrian signal push buttons in the United States", 1, USA, BUTTON_Q),
    topic("Pedestrian signal push buttons in Canada", 1, CANADA, BUTTON_Q),
    topic("Audible traffic signals", 1, "", BUTTON_Q),
    topic("Countdown traffic signals in the United States", 0, USA, SIGNAL_KIND_Q),
    topic("HAWK beacons", 0, USA, SIGNAL_KIND_Q),
    topic("Rectangular Rapid Flashing Beacons", 1, USA, SIGNAL_KIND_Q),
    topic("Flashing yellow arrow", 0, USA, SIGNAL_KIND_Q),
] + [topic(f"Traffic lights at {state} state in {where_}", 2, country, LIGHT_Q)
     for state in ("red", "yellow", "green", "dark") for where_, country in (("the United States", USA),
                                                                             ("Canada", CANADA))
     if not (state == "dark" and country == CANADA)]
ROAD_TOPICS = [
    topic("Street signs in the United States by state", 1, USA, SIGN_Q),
    topic("Street signs in the United States by city", 1, USA, SIGN_Q),
    topic("Street signs in Canada", 2, CANADA, SIGN_Q),
    topic("Roundabouts in the United States", 2, USA, PLACE_Q),
    topic("Roundabouts in Canada", 2, CANADA, PLACE_Q),
    topic("Interchanges in the United States by state", 1, USA, PLACE_Q),
    topic("Interchange ramps in the United States", 1, USA, ROAD_Q),
    topic("Interchanges in Canada", 2, CANADA, PLACE_Q),
    topic("Freeways in the United States", 1, USA, ROAD_Q),
    topic("Freeways in Canada", 1, CANADA, ROAD_Q),
    topic("School zone warning road signs in the United States", 1, USA, SIGN_Q),
    topic("School zone speed limit road signs", 1, "", SIGN_Q),
    topic("End School Zone road signs in the United States", 1, USA, SIGN_Q),
    topic("School zone warning road signs in Canada", 1, CANADA, SIGN_Q),
    topic("School crossing signs in the United States", 1, USA, SIGN_Q),
    topic("Roadworks in the United States", 2, USA, PLACE_Q),
    topic("Roadworks in Canada", 2, CANADA, PLACE_Q),
    topic("Traffic cones in the United States", 1, USA, WHAT_Q),
    topic("Cycle lanes in the United States", 2, USA, ROAD_Q),
    topic("Cycle lanes in Canada", 2, CANADA, ROAD_Q),
    topic("Bus stops in the United States by state", 1, USA, PLACE_Q),
    topic("Bus shelters in the United States", 1, USA, PLACE_Q),
    topic("Bus stops in Canada", 1, CANADA, PLACE_Q),
    topic("Bus shelters in Canada", 1, CANADA, PLACE_Q),
    topic("Sidewalks in the United States by location", 2, USA, PLACE_Q),
    topic("Sidewalks in Canada by province or territory", 2, CANADA, PLACE_Q),
    topic("Sidewalk obstructions", 1, "", WHAT_Q),
    topic("Speed bumps in the United States", 1, USA, ROAD_Q),
    topic("Traffic calming in the United States", 1, USA, ROAD_Q),
]
HOME_TOPICS = [
    topic("Suburbs in the United States", 2, USA, PLACE_Q),
    topic("Residential areas in the United States", 2, USA, PLACE_Q),
    topic("Driveways in the United States", 1, USA, WHAT_Q),
    topic("Driveways in Canada", 1, CANADA, WHAT_Q),
    topic("Porches in the United States", 2, USA, WHAT_Q),
    topic("Porches in Canada", 1, CANADA, WHAT_Q),
]


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
    pass_random(len(t["root"]) * 7907 + sum(map(ord, t["root"]))).shuffle(files)
    return files


def in_north_america(place):
    """True when a place is in the USA or Canada ("Ontario, Canada", "USA")."""
    return bool(re.search(r"(^|, )(USA|Canada)$", place or ""))


def file_place(title, found_in, cats, country):
    """Where a file's photo was taken: the place its own category names ("... in Ohio" -> "Ohio, USA"); where that
    is only the country (or nothing), a state or province one of its other categories names, in that country; then
    the country at the camera's coordinates; then the topic's country ("" for a worldwide category such as "Raised
    pedestrian crossings", whose files are kept only when one of these says the USA or Canada)."""
    place = category_place(found_in, country) if " in " in found_in else country
    if place in ("", USA, CANADA):
        for c in [found_in] + list(cats):
            p = category_place(c, "")
            if in_north_america(p) and p not in (USA, CANADA) and (not place or p.endswith(place)):
                return p
        for c in cats:
            p = category_place(c, "")
            if not place and p in (USA, CANADA):
                place = p
    gps = PLACES.get(title, "")
    if not place and in_north_america(gps):
        place = gps
    if place in (USA, CANADA) and gps and gps != place:
        return gps                      # the camera says another country: kept only if it is the USA or Canada
    return place


def file_rows(title, url, credit, text, raw, found_in, cats, t):
    """The rows of one Commons file: the RULES rows from the category it was found in and its other categories, the
    pedestrian signal's state where its own words say it, and its English caption ("Describe this picture."), with
    the place (file_place); None when the photo is not shown to be in the USA or Canada."""
    place = file_place(title, found_in, cats, t["country"])
    if not in_north_america(place):
        return None, place                  # not shown to be in the USA or Canada
    rows = rule_rows([found_in] + [c for c in cats if c != found_in], prefer=t["prefer"])
    state = ped_signal_state(f"{title.split(':', 1)[-1].rsplit('.', 1)[0]}. {raw}")
    if state and any(r["question"] in (PED_SIGNAL_Q, CROSSWALK_Q, BUTTON_Q, SIGNAL_KIND_Q) for r in rows):
        rows.insert(1, {"question": PED_STATE_Q, "answer": state})
    text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
    if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
        rows.append({"question": DESCRIBE_Q, "answer": text})
    facts = {"commons_category": found_in, "commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0]}
    return [dict(r, credit=credit, facts=facts, **where(place)) for r in rows], place


def street_commons(topics, limit, prefix, key):
    """A Commons pack from topics: the topics take turns, in a fixed shuffled order, so each gets an even share. Each
    file's licence is checked (mechanical_packs.mech_entries: CC0, public domain or CC BY), files whose words name
    nudity or harm are left out, and a free file with no answer is set aside for a description. Returns the pack
    entries (the pictures downloaded patiently)."""
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
                    considered(title, url, "its words name a crash, an injury, a death or a protest (an everyday pack)")
                    continue
                seen.add(title)
                rows, place = file_rows(title, url, credit, text, raw, found_in.get(title, t["root"]),
                                        cats.get(title, []), t)
                if rows is None:
                    considered(title, url, f"not shown to be in the USA or Canada ({place or 'no place'})")
                    continue
                if not rows:
                    needs_description(file_name(prefix, title), url, credit, credit.rsplit(", ", 2)[-2],
                                      text=text, title=title, place=place,
                                      reason="no label this pack can read and no English caption",
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"commons_category": found_in.get(title, t["root"]),
                                             "child": bool(CHILD.search(words)), "not_for_picture_making": True})
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


def build_commons_crosswalks_signals(limit):
    """Crosswalks, curb cuts, tactile paving, pedestrian signals and push buttons, and traffic lights by state."""
    return street_commons(CROSSWALK_TOPICS, limit, "xwalk", "commons_crosswalks_signals")


def build_commons_streets_roads_na(limit):
    """Street signs, roundabouts, interchanges, freeways, school zones, road works, bike lanes, bus stops, sidewalks."""
    return street_commons(ROAD_TOPICS, limit, "naroad", "commons_streets_roads_na")


def build_commons_neighbourhoods_na(limit):
    """Suburbs, residential areas, driveways and porches in the US and Canada."""
    return street_commons(HOME_TOPICS, limit, "nahome", "commons_neighbourhoods_na")


# ----------------------------------------------------------------- us_dot_street_photos (FHWA on Commons)

FHWA_GALLERY = "Interstate Photo Gallery of the Federal Highway Administration"
# (category, listing pages of 500 to sample: 1 reads a small category whole)
FHWA_STREAMS = [("Images from the Federal Highway Administration Flickr stream", 3),
                ("U.S. Federal Highway Administration Flickr files uploaded by OptimusPrimeBot", 1)]
FHWA_CREDIT = "the Federal Highway Administration (FHWA), US Department of Transportation"
# The words an FHWA Flickr caption must name to be a street or road scene (most of the stream is bridge parts, staff
# events and history paintings).
STREET_WORDS = re.compile(r"\b(street|streets|road|roads|roadway|highway|interstate|freeway|expressway|parkway|"
                          r"intersection|crosswalks?|crossings?|pedestrians?|sidewalks?|curb|ramps?|interchange|"
                          r"roundabout|bike lanes?|bicycle lanes?|bikeway|trail|work zone|traffic|signals?|lanes?|"
                          r"median|shoulder|rumble strips?|guardrail|signs?|bus|transit)\b", re.I)
# Captions that are bridge-building close-ups, events, people or history paintings, not a scene of the road.
NOT_A_SCENE = re.compile(r"\b(dowel|rebar|beams?|girders?|abutments?|bents?|deck reinforcement|shear key|formwork|"
                         r"grout|bearings?|pier caps?|specimens?|lab|laboratory|staff|employees?|ceremony|"
                         r"conference|meeting|award\w*|breast cancer|civil rights|awareness|portrait|painting|"
                         r"painted by|artist|steam roller|horse|stagecoach|wagon|overland)\b", re.I)
GALLERY_STATE = re.compile(r"^File:([A-Z]{2}) ")
GALLERY_FIX = {"WS": "Wisconsin"}                 # the gallery's own two-letter code for Wisconsin


def gallery_place(title):
    """The state an Interstate Photo Gallery file name starts with ("File:GA 6 I20 I75 FHWA 1966 124.jpg" ->
    "Georgia, USA"); "USA" for the general ones ("US 1 GEN ...")."""
    m = GALLERY_STATE.match(title)
    code = m.group(1) if m else ""
    state = GALLERY_FIX.get(code) or (US_STATE_CODES.get(code) if code not in ("US", "DC") else "")
    return place_name(state, USA) if state else ("Washington, D.C., USA" if code == "DC" else USA)


def fhwa_row(title, caption, credit, place, gallery):
    """The rows of one FHWA photo: its own caption as the description, with the place; [] when the caption is not a
    road scene (a Flickr photo) or too short."""
    if not caption or len(caption.split()) < 5 or only_the_name(caption, title) or not in_english(caption):
        return []
    if OFFICIAL.search(caption) or HARM.search(caption) or NUDE.search(caption):
        return []
    if not gallery and (not STREET_WORDS.search(caption) or NOT_A_SCENE.search(f"{title} {caption}")):
        return []
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit, **where(place)}]
    if place != USA:
        rows.append({"question": WHERE_Q, "answer": f"It was taken in {place}.", "credit": credit,
                     **where(place)})
    return rows


def build_us_dot_street_photos(limit):
    """FHWA's Interstate Photo Gallery and the road scenes of its Flickr stream, from their Commons copies."""
    s, rng, items, seen = session(), pass_random(1956), [], set()
    sources = [(FHWA_GALLERY, 1, True)] + [(c, pages, False) for c, pages in FHWA_STREAMS]
    for category, pages, gallery in sources:
        if listing_out_of_time() or len(items) >= limit * 1.15:
            break
        titles = [t for t in sample_members(s, category, pages, rng) if t not in seen and not NOT_A_PHOTO.search(t)]
        rng.shuffle(titles)
        say(f"Commons {category}: {len(titles)} files")
        for start in range(0, len(titles), 50):
            if listing_out_of_time() or len(items) >= limit * 1.15:
                break
            for title, url, credit, raw, year in agency_entries(s, titles[start:start + 50]):
                if title in seen:
                    continue
                seen.add(title)
                caption = agency_caption(raw)
                place = gallery_place(title) if gallery else USA
                rows = fhwa_row(title, caption, credit, place, gallery)
                if not rows:
                    if gallery and not (OFFICIAL.search(caption) or HARM.search(caption)):
                        needs_description(file_name("fhwa", title), url, credit, "public domain", text=caption,
                                          title=title, place=place, reason="its caption is under five English words",
                                          page_url=credit.rsplit(", ", 1)[-1],
                                          extra={"agency": FHWA_CREDIT, "year": year,
                                                 "not_for_picture_making": True})
                    considered(title, url, "not a road scene, or its caption is too short or about people or events")
                    continue
                words = f"{title} {caption}"
                items.append((file_name("fhwa", title), url, [mark_child(r, words) for r in rows]))
    rng.shuffle(items)
    fetched = commons_fetch(items[:int(limit * 1.1) + 2])[:limit]
    say(f"us_dot_street_photos: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
STREET_SCENE_PACKS = {
    "commons_crosswalks_signals": (build_commons_crosswalks_signals, COMMONS_CREDIT.format(
        what="categories of US and Canadian crosswalks, curb cuts, tactile paving, pedestrian signals and push "
             "buttons, and traffic lights by state (red, yellow, green, dark), with their state, province and city "
             "subcategories; a signal's state only from its category or the file's own words")),
    "commons_streets_roads_na": (build_commons_streets_roads_na, COMMONS_CREDIT.format(
        what="categories of US and Canadian street signs, roundabouts, interchanges and ramps, freeways, school zone "
             "signs, road works, bike lanes, bus stops and shelters, sidewalks and speed bumps")),
    "commons_neighbourhoods_na": (build_commons_neighbourhoods_na, COMMONS_CREDIT.format(
        what="categories of US and Canadian suburbs, residential areas, driveways and porches")),
    "us_dot_street_photos": (build_us_dot_street_photos,
                             "US Federal Highway Administration photos (public domain, works of the US government, "
                             "17 U.S.C. 105), from their Wikimedia Commons copies: Category:Interstate Photo Gallery "
                             "of the Federal Highway Administration and the FHWA Flickr stream "
                             "(https://commons.wikimedia.org/wiki/Category:Federal_Highway_Administration), each "
                             "file's licence checked there. Answers from the agency's own captions."),
}

# How many pictures a full build takes from each (Commons answers about one picture a second).
STREET_SCENE_LIMITS = {
    "commons_crosswalks_signals": 2500,  # 25 topics, a few thousand files under their state and city categories
    "commons_streets_roads_na": 3000,    # 29 topics
    "commons_neighbourhoods_na": 1500,   # 6 topics (US porches about 2,800 files, suburbs 940, driveways 730)
    "us_dot_street_photos": 500,         # the gallery's 274 captioned photos and the stream's road scenes
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one street scene pack builder.")
    parser.add_argument("key", choices=sorted(STREET_SCENE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = STREET_SCENE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"places: " + ", ".join(f"{p} {n}" for p, n in places.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
