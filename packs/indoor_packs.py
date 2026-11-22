"""Pack builders for FINDING YOUR WAY INSIDE PUBLIC BUILDINGS: lobbies, corridors, stairwells, lifts (elevators) and
escalators, toilets (restrooms) and their signs, emergency exits, door and room-number signs, wayfinding signs and
tactile maps, reception and information desks, waiting rooms and halls, ticket offices and counters, gates, departure
boards, ticket barriers, turnstiles and walk-through metal detectors. Used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}, plus "place" where the file's camera coordinates give a country and "child": true
where the words of a picture name a child. A picture with more than one question comes once with its JPEG and then
again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts
pictures.

Why: a blind person in a station, hospital, office block or airport needs to know what kind of space they are in,
whether the lift or the stairs are here, which toilet door is the men's, women's or all-gender one, what room number is
on the door, and where the desk, the gate or the ticket barrier is.

Every answer is a fixed sentence written here from the source's own labels: the name of the Commons category a photo
sits in ("Women's toilet signs" -> "It is a women's toilet sign ..."), or a label people checked by hand (Open
Images). SIGN TEXT IS READ ONLY WHERE THE SOURCE LABELS IT: the room number comes only from the Commons category that
names it ("102 (room number)" -> "Room number 102 is shown here."), the kind of toilet only from the category
that names it; nothing else on a sign is read, and nothing is written by an AI model. Each Commons file's own English
caption or description is added as "Write a short description ..." when it is a real, respectful one.

The packs (all open, checked at the source in November 2026):
  commons_indoor_wayfinding  Wikimedia Commons categories (INDOOR_SPECS) and the numbered subcategories of
                             Category:Room numbers. Files CC0, public domain or CC BY (each file's licence checked on
                             its own page; never BY-SA, NC or ND); captions CC0 (Commons structured data).
  open_images_indoor         Google Open Images V7: photos where people checked by hand whether a lobby, hall,
                             waiting room, restroom, airport terminal, conference or function hall, signs, an
                             electronic sign, a map, a revolving or sliding door is there (labels CC BY 4.0; each
                             photo's own licence checked, CC BY, CC0 or the Public Domain Mark, photographer named).
                             "What kind of place is this?" -> "I can see a waiting room."; "Is there a revolving door
                             in this picture?" (no only where people checked and found none).

Not repeated (other packs ask the same of the same photos): the US hotel lobbies, waiting rooms, hospital corridors,
lifts, escalators, airport terminals and TSA checkpoints of us_modern_packs (commons_us_public_places,
commons_us_getting_around: here only the general categories, without their subcategories), exit and emergency exit
signs (events_safety_packs commons_safety_photos), braille signs and lift buttons with braille (home_safety_packs
commons_access_features), lift buttons as things (home_packs commons_appliances), accessible toilets
(disability_packs), queues (people_activity_packs), and the Open Images stairs, escalators, lifts, doors, handrails and
turnstiles of world_life_packs.open_images_street. Indoor-scene datasets that are not open (MIT Indoor67, SUN397,
Places365, ADE20K, InteriorNet, Matterport3D, the Indoor Sign Dataset, MCIndoor20000) are listed with the reason in
training-kit/kit/daily_access_sources.py, with the share-alike Commons files of these categories.

Safety (packs/SOURCE-RULES.md): no sexual content (home_packs.NUDE); rows whose words name a child are marked "child".
Public places have people in them: both packs are for describing only, never for picture-making (the kit puts them in
NOT_FOR_PICTURE_MAKING).

    python packs/indoor_packs.py commons_indoor_wayfinding --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say
from gaps_oi_packs import group, build_oi_gap, QUICK

PLACE_Q = "What kind of place is this?"
WHAT_Q = "What is this?"
SIGN_Q = "What does this sign tell me?"
ROOM_Q = "What room number is shown here?"

STAIRS_NOTE = "Find the handrail, and check with your foot or cane whether the stairs go up or down."
ESCALATOR_NOTE = "Find the moving handrail first, and step on and off carefully."
LIFT_NOTE = "Lift buttons are usually beside the door outside, and on a panel just inside the door."


def place(category, words, note="", deeper=False):
    """A Commons spec for a kind of place: "What kind of place is this?" -> "This is <words>." and the note."""
    return (category, deeper, [(PLACE_Q, f"This is {words}." + (f" {note}" if note else ""))])


def thing(category, words, note="", deeper=False):
    """A Commons spec for a thing: "What is this?" -> "This is <words>." and the note."""
    return (category, deeper, [(WHAT_Q, f"This is {words}." + (f" {note}" if note else ""))])


def sign(category, words, deeper=False):
    """A Commons spec for a sign: "What does this sign tell me?" -> "It is <words>"."""
    return (category, deeper, [(SIGN_Q, f"It is {words}")])


# Commons categories (deeper=False where a subcategory belongs to another pack, such as "Hospital corridors" or the
# US lifts and escalators of us_modern_packs, or holds people or art).
INDOOR_SPECS = [
    place("Corridors", "a corridor (hallway) inside a building"),
    place("Corridors in office buildings", "a corridor in an office building", deeper=True),
    place("Hotel corridors", "a hotel corridor, with room doors along it", deeper=True),
    place("Apartment hallways", "a hallway in a block of flats (an apartment building)", deeper=True),
    place("Hotel lobbies", "a hotel lobby: the entrance hall, usually with the front desk"),
    place("Entrance halls", "the entrance hall (lobby) of a building"),
    place("Foyers", "a foyer: the entrance hall of a theatre, hall or other public building"),
    place("Stairwells", "a stairwell: the stairs inside a building, from floor to floor", STAIRS_NOTE, True),
    thing("Elevators", "a lift (elevator)", LIFT_NOTE),
    place("Interiors of elevators", "the inside of a lift (elevator)", LIFT_NOTE),
    thing("Escalators", "an escalator: moving stairs", ESCALATOR_NOTE),
    thing("Escalator handrails", "the moving handrail of an escalator", ESCALATOR_NOTE, True),
    sign("Hold the handrail signs", "a sign asking people to hold the handrail on the escalator.", True),
    sign("Escalator signs", "a sign at an escalator.", True),
    thing("Airport escalators", "an escalator in an airport", ESCALATOR_NOTE, True),
    thing("Rapid transit escalators", "an escalator in an underground (metro) station", ESCALATOR_NOTE, True),
    thing("Escalators in shopping malls", "an escalator in a shopping centre (mall)", ESCALATOR_NOTE, True),
    thing("Moving ramps", "a moving walkway (a moving ramp or travelator)", ESCALATOR_NOTE, True),
    sign("Toilet signs", "a toilet (restroom) sign: the toilets are here or this way."),
    sign("Men's toilet signs", "a men's toilet sign: the men's toilets (restroom) are here or this way.", True),
    sign("Women's toilet signs", "a women's toilet sign: the women's toilets (restroom) are here or this way.", True),
    sign("Unisex toilet signs", "an all-gender (unisex) toilet sign: this toilet is for anyone.", True),
    place("Public toilets", "a public toilet (restroom)"),
    thing("Emergency exits", "an emergency exit: a door or way out of the building for emergencies"),
    sign("Door signs", "a sign on a door.", True),
    sign("Wayfinding signs", "a wayfinding sign: it shows the way to places in or around the building.", True),
    thing("Tactile maps", "a tactile map: a raised map to read by touch, often with braille", deeper=True),
    thing("Reception desks", "a reception desk, where visitors check in or ask for help"),
    thing("Information desks", "an information desk, where people can ask for help or directions"),
    thing("Reference desks", "a library's reference desk, where librarians help people find things", deeper=True),
    place("Waiting rooms", "a waiting room"),
    place("Waiting areas", "a waiting area"),
    place("Departure halls", "a departure hall, where travellers check in and wait to leave", deeper=True),
    place("Arrival halls", "an arrival hall, where arriving travellers come out and are met", deeper=True),
    thing("Ticket counters", "a ticket counter, where tickets are sold", deeper=True),
    place("Ticket offices", "a ticket office, where tickets are sold", deeper=True),
    thing("Box offices", "a box office, where theatre, cinema or event tickets are sold", deeper=True),
    place("Airport gates", "an airport gate, where passengers wait and board the plane", deeper=True),
    place("Bus station gates", "a bus station gate, where passengers board the bus", deeper=True),
    thing("Departure boards", "a departure board: a screen or board listing departures, their times and platforms or "
                              "gates", deeper=True),
    thing("Walk-through metal detectors", "a walk-through metal detector at a security check"),
    thing("Ticket barriers", "a ticket barrier (fare gate): you pass a ticket or card to open it", deeper=True),
    thing("Turnstiles", "a turnstile: a gate with turning arms that lets one person through at a time", deeper=True),
    place("Interiors of airports", "the inside of an airport"),
]

ROOM_NUMBER = re.compile(r"^(?:Category:)?(\d{1,4}[A-Za-z]?) \(room number\)$")


def room_number_specs(subcategories):
    """Specs for the numbered subcategories of Category:Room numbers: "102 (room number)" -> "Room number 102 is
    shown here." (the number only from the category's name; other names are not used)."""
    specs = []
    for sub in subcategories:
        m = ROOM_NUMBER.match(sub)
        if m:
            specs.append((sub.split(":", 1)[-1], False,
                          [(ROOM_Q, f"Room number {m.group(1)} is shown here.")]))
    return specs


def build_commons_indoor_wayfinding(limit):
    """The commons_indoor_wayfinding pack (see the module docstring)."""
    from home_packs import build_commons_topic
    from food_packs import commons_members
    rooms = room_number_specs(commons_members(session(), "Room numbers", "subcat"))
    say(f"Commons Room numbers: {len(rooms)} numbered subcategories")
    return build_commons_topic(INDOOR_SPECS + rooms, limit, "indoor")


# ----------------------------------------------------------------- Open Images

INDOOR_OI = [
    group(PLACE_Q, {"Lobby": "a lobby", "Hall": "a hall", "Waiting room": "a waiting room",
                    "Restroom": "a public toilet (restroom)", "Airport terminal": "an airport terminal",
                    "Airport": "an airport", "Conference hall": "a conference hall",
                    "Function hall": "a function hall"}),
    group("What signs or maps are in this picture?",
          {"Signage": "signs", "Electronic signage": "an electronic sign (a display screen)",
           "Address sign": "an address sign", "Map": "a map"},
          "I can say that signs are there, not what they say."),
    group("What kind of door is here?", {"Revolving door": "a revolving door", "Sliding door": "a sliding door",
                                         "Sliding glass door": "a sliding glass door"}),
]


def build_open_images_indoor(limit):
    """open_images_indoor (see the module docstring)."""
    return build_oi_gap("open_images_indoor", INDOOR_OI, limit, 9301)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories; captions CC0.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
INDOOR_PACKS = {
    "commons_indoor_wayfinding": (build_commons_indoor_wayfinding, COMMONS_LICENCE.format(
        what="lobby, corridor, stairwell, lift, escalator, toilet sign, door and room-number sign, wayfinding, desk, "
             "waiting room, ticket office, gate and security")),
    "open_images_indoor": (build_open_images_indoor, OI_LICENCE),
}
INDOOR_LIMITS = {
    "commons_indoor_wayfinding": 2500,   # 45 categories and about 66 room numbers, about 5,000 files before the check
    "open_images_indoor": 2500,          # 15 labels
}
INDOOR_COMMONS_KEYS = ("commons_indoor_wayfinding",)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an indoor wayfinding pack builder.")
    parser.add_argument("key", choices=sorted(INDOOR_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = INDOOR_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
