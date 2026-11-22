"""Picture packs for CAR CARE BASICS: the things a driver checks and changes (wipers, bulbs, fluids, tyres and their
markings, jacks and spare wheels, jump-starting), roadside safety (warning triangles, flares, breakdowns), electric
vehicle charging connectors, and dashboard warning lights read from a symbol file's own words. Used by build_packs.py
in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None,
row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the
same picture. The limit counts pictures.

The owner's request of 2026-11-22 ("life skills": car care, gardening, home health, instrument care). Car parts by
name, engine bays, dashboards, gauges, the ISO 7000 symbols with the main tell-tales, tyre and spark-plug condition
are already packs (mechanical_packs.py: commons_car_parts, commons_engine_bays, iso_machine_symbols, tyre_condition,
spark_plug_condition); charging STATIONS as places are us_modern_packs' and canada_packs'. Nothing of theirs is
asked again here (packs/test_car_care.py checks every Commons category and Open Images label).

Answers say only what the source says: a Commons category's name (with a fixed purpose line written here), an Open
Images label people confirmed, or, for a dashboard symbol, the meaning its own file title or description names
(DASHBOARD_LIGHTS: never guessed from the drawing). Safety notes are added where the work can hurt:
  JACK_NOTE      jacks, lug wrenches and spare wheels: never under a car held only by a jack.
  ROADSIDE_NOTE  breakdowns, roadside help and tow trucks: get off the road, hazard lights, call for help.
  CHARGING_NOTE  charging connectors: use only undamaged, certified equipment as the car's maker says.
  (HOT_NOTE and BATTERY_NOTE are the same words the kit's share-alike entry and the manual library use.)

The packs (all open: CC0, public domain or CC BY files; Open Images labels CC BY 4.0):
  commons_car_care          Commons: windshield wipers, tyre valves, snow chains, scissor jacks, wheel chocks, lug
                            wrenches and spare tyres, car washing, AdBlue (diesel exhaust fluid), broken-down
                            vehicles, roadside assistance and tow trucks.
  commons_ev_charging       Commons: the plugs and sockets of electric car charging (IEC 62196: Type 1 or J1772,
                            Type 2 and CCS; CHAdeMO; the North American Charging Standard), Tesla Superchargers and
                            home wallboxes. "What charging connector is this?"
  commons_dashboard_lights  Commons symbol files and photos found by their own titles (warning light, tell-tale,
                            ISO 2575): the meaning is said only when the file's own words name a road vehicle (or
                            the symbol standard) and one light listed in DASHBOARD_LIGHTS (about 45 lights, with
                            what the driver should do, as car handbooks
                            give it), else the file is left out. Light colours are said only where the words say
                            them (red: stop safely; amber: check soon; green or blue: a system is on).
  open_images_car_care      Open Images V7: tyres, treads, rims and alloy wheels, hubcaps, headlamps and car lights,
                            motor oil and antifreeze, gauges (speedometer, odometer, tachometer), steering wheels and
                            gear shifts, electric cars, tow trucks, car washes, traffic cones.

Commons has no category with free files for wiper blades, bulbs, washer fluid, coolant reservoirs, jump starters,
tyre sidewall markings, tread wear bars, warning triangles or car jacks (checked 2026-11-22): the kit's
car_care_sources.py lists them, and the manual library's car_care category links the makers' guides for them.
What was looked at and left out (owner's manuals' pictures, NHTSA's site, YouTube, forums and others) is in the
kit's car_care_sources.py (CAR_CARE_NOT_INCLUDED).

    python packs/car_care_packs.py commons_ev_charging --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, ALT_TEXT
from gaps_oi_packs import group, build_oi_gap, QUICK

ASK_WHAT = "What is this?"
ASK_PART = "What car part or car care item is this?"
ASK_CONNECTOR = "What charging connector is this?"
ASK_LIGHT = "What does this dashboard warning light mean?"

JACK_NOTE = ("Safety: never get under a car held up only by a jack; use jack stands on firm, level ground, set the "
             "parking brake and chock the wheels.")
HOT_NOTE = ("Safety: never open the radiator or coolant cap of a hot engine; hot coolant can spray out and scald. "
            "Let the engine cool first.")
BATTERY_NOTE = ("Safety: car batteries hold acid that burns and give off explosive gas; wear eye protection, keep "
                "flames and sparks away, and follow the car's handbook for the order of the jump leads.")
ROADSIDE_NOTE = ("Safety: if your car breaks down, get as far off the road as you can, turn on the hazard lights, "
                 "stay away from traffic and call for help (911 in an emergency).")
CHARGING_NOTE = "Use only undamaged, certified charging equipment, as the car's maker says."


def car(category, words, note="", deeper=True, question=ASK_PART, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, answer)]) and an optional
    pattern of words a file's title or description must have. The answer is "This is <words>." and the note."""
    spec = (category, deeper, [(question, f"This is {words}." + (f" {note}" if note else ""))])
    return spec + ((pattern,) if pattern is not None else ())


# Broad categories hold other things too: only files whose own words say car, vehicle, tyre or similar.
CAR_WORDS = re.compile(r"\b(cars?|automobiles?|vehicles?|auto(motive)?|tyres?|tires?|trucks?|vans?|motor)\b", re.I)

# ----------------------------------------------------------------- Commons: car care things

CAR_CARE = [
    car("Windshield wipers", "a windscreen wiper (windshield wiper), which clears rain from the glass"),
    car("Tire valves", "a tyre valve, where air is put into a tyre"),
    car("Snow chains", "snow chains, fitted over tyres for grip on snow and ice"),
    car("Scissor jacks", "a scissor jack, the small jack that comes with many cars", JACK_NOTE),
    car("Wheel chocks", "a wheel chock, a wedge put against a wheel so the car cannot roll"),
    car("Lug wrenches", "a lug wrench (wheel brace), for undoing the wheel nuts", JACK_NOTE),
    car("Spare tires", "a spare tyre", JACK_NOTE),
    car("Car washing", "a car being washed", question="What is happening in this picture?"),
    car("AdBlue", "diesel exhaust fluid (AdBlue), a liquid that some diesel vehicles need topped up in "
                                "its own tank, never in the fuel tank"),
    car("Vehicle breakdowns", "a broken-down vehicle", ROADSIDE_NOTE,
        question="What is happening in this picture?"),
    car("Roadside assistance", "roadside assistance: a breakdown service helping a driver", ROADSIDE_NOTE,
        question="What is happening in this picture?"),
    car("Tow trucks", "a tow truck (breakdown truck), which takes broken-down cars away", ROADSIDE_NOTE,
        question=ASK_WHAT),
]

# ----------------------------------------------------------------- Commons: electric vehicle charging

# The connector categories hold photos of whole cars too: only files whose own words name a plug, socket or port.
CONNECTOR_WORDS = re.compile(r"\b(connectors?|plugs?|sockets?|ports?|inlets?|couplers?|cables?|charg\w*)\b", re.I)
EV_CHARGING = [
    car("CHAdeMO", "a CHAdeMO connector, a round fast-charging plug used mostly by older Japanese electric cars",
        CHARGING_NOTE, question=ASK_CONNECTOR, pattern=CONNECTOR_WORDS),
    car("North American Charging System", "a North American Charging Standard (NACS, SAE J3400) connector, the small "
                                          "plug first used by Tesla", CHARGING_NOTE, question=ASK_CONNECTOR,
        pattern=CONNECTOR_WORDS),
    car("IEC 62196", "an IEC 62196 charging plug or socket: Type 1 (J1772), Type 2 (Mennekes) or CCS",
        CHARGING_NOTE, question=ASK_CONNECTOR, pattern=CONNECTOR_WORDS),
    car("Tesla Supercharger", "a Tesla Supercharger, a fast charging post", CHARGING_NOTE, question=ASK_WHAT),
    car("Wallboxes", "a wallbox, a home charging unit for an electric car", CHARGING_NOTE, question=ASK_WHAT),
]

# ----------------------------------------------------------------- Commons: dashboard warning lights by their own words

# The dashboard lights as car handbooks explain them, found by the words of a symbol file's own title or description.
# Checked in this order (the more particular first). The colour is not part of the meaning here: it is said only
# where the file's own words give it (light_colour).
DASHBOARD_LIGHTS = [
    (r"tyre pressure|tire pressure|\btpms\b", "the tyre pressure warning light: a tyre's pressure is low; check and "
                                             "inflate the tyres as the label in the door frame says"),
    (r"oil pressure", "the oil pressure warning light: stop the engine as soon as it is safe and check the oil"),
    (r"oil level", "the oil level warning light: the engine oil is low; check it and top it up"),
    (r"coolant level", "the coolant level warning light: the coolant is low; let the engine cool, then check it"),
    (r"coolant temperature|engine temperature|overheat", "the engine temperature warning light: the engine is too "
                                                         "hot; stop as soon as it is safe and let it cool"),
    (r"battery|charging system|alternator", "the battery (charging) warning light: the battery is not being "
                                            "charged; have it checked soon"),
    (r"anti-?lock|\babs\b", "the ABS warning light: the anti-lock brakes have a fault; the normal brakes still work, "
                            "but have it checked"),
    (r"parking brake|handbrake|hand brake", "the parking brake light: the parking brake is on, or has a fault"),
    (r"brake pad|brake wear|brake lining", "the brake pad wear light: the brake pads are worn; have them replaced"),
    (r"brake fluid|brake (failure|system|warning)", "the brake warning light: the brake fluid may be low or the "
                                                    "brakes have a fault; have them checked before driving on"),
    (r"check engine|engine malfunction|malfunction indicator|\bmil\b|engine management|service engine",
     "the check-engine light: the engine's control system has found a fault; have it checked soon (if it flashes, "
     "slow down and have it checked at once)"),
    (r"air ?bag|\bsrs\b", "the airbag warning light: the airbag system has a fault; have it checked"),
    (r"seat ?belt", "the seat-belt reminder: a seat belt is not fastened"),
    (r"low fuel|fuel level|fuel reserve", "the low fuel warning light: the tank is nearly empty"),
    (r"glow plug|pre-?heat", "the diesel glow-plug light: wait for it to go out before starting the engine"),
    (r"diesel particulate|\bdpf\b", "the diesel particulate filter light: the exhaust filter is getting full; a "
                                    "longer drive at steady speed may clear it, else have it checked"),
    (r"adblue|diesel exhaust fluid|\bdef\b", "the AdBlue (diesel exhaust fluid) light: top up the AdBlue tank soon"),
    (r"traction control|stability control|\besc\b|\besp\b|skid", "the traction or stability control light: when "
                                                                  "it flashes the system is working; if it stays on "
                                                                  "it is switched off or has a fault"),
    (r"power steering|steering (fault|warning)", "the power steering warning light: the steering may become heavy; "
                                                 "have it checked"),
    (r"transmission|gearbox", "the transmission warning light: the gearbox has a fault or is too hot; have it checked"),
    (r"washer fluid|washer", "the washer fluid light: the windscreen washer fluid is low; top it up"),
    (r"door (open|ajar)|open door", "the door-open light: a door is not fully shut"),
    (r"boot (open|lid)|trunk (open|lid)|tailgate", "the boot (trunk) open light: the boot or tailgate is not shut"),
    (r"bonnet|hood (open|ajar)", "the bonnet (hood) open light: the bonnet is not shut"),
    (r"high ?beam|main beam", "the high-beam (main beam) light: the headlights are on full beam; dip them for other "
                              "drivers"),
    (r"low ?beam|dipped beam|headlights? on", "the headlight light: the dipped headlights are on"),
    (r"rear fog", "the rear fog light indicator: the rear fog light is on"),
    (r"fog (light|lamp)", "the fog light indicator: the front fog lights are on"),
    (r"bulb (failure|out)|lamp (failure|out)|light (failure|out)", "the bulb failure light: an outside light has "
                                                                   "stopped working"),
    (r"cruise control", "the cruise control light: cruise control is on"),
    (r"lane (departure|keep)", "the lane-keeping light: the lane-keeping assistant is on, or warns that the car is "
                               "drifting out of its lane"),
    (r"turn signal|direction indicator|turn indicator|blinker",
     "the turn signal (indicator) light: the indicator is on; "
                                                           "fast blinking can mean a bulb is out"),
    (r"hazard", "the hazard warning light: all the indicators are flashing"),
    (r"key (not detected|fob)|immobili[sz]er", "the key or immobiliser light: the car does not detect the "
                                                        "key, or the anti-theft system is on"),
    (r"service (due|required|reminder)|maintenance (due|required)|spanner|wrench", "the service reminder: the car is "
                                                                                    "due for a service"),
    (r"frost|ice warning|low outside temperature|snowflake", "the frost warning light: it is cold outside and the "
                                                             "road may be icy"),
    (r"eco mode|\beco\b", "the eco mode light: the economy driving mode is on"),
    (r"\bready\b", "the READY light of an electric or hybrid car: the car is on and ready to drive, though it is "
                   "silent"),
    (r"turtle|reduced power|limited power", "the reduced power (turtle) light of an electric car: power is limited, "
                                            "often because the battery is very low or too hot; stop safely and charge "
                                            "or have it checked"),
    (r"charging (cable|plug)|plug(ged)? in", "the charging cable light: the charging cable is connected"),
    (r"hybrid system|electric (drive|system) (fault|warning)", "the hybrid or electric system warning light: stop "
                                                               "safely and have the car checked"),
    (r"water in fuel", "the water-in-fuel light of a diesel: water must be drained from the fuel filter; have it "
                       "checked"),
    (r"catalytic|exhaust (temperature|system)", "the exhaust or catalytic converter warning light: have the exhaust "
                                                "checked"),
    (r"tow mode|trailer", "the trailer or tow light: a trailer is connected, or its lights are on"),
]
LIGHT_COLOURS = re.compile(r"\b(red|amber|orange|yellow|green|blue|white)\b", re.I)
COLOUR_MEANING = {"red": "red lights mean stop safely or act at once", "amber": "amber lights mean check soon",
                  "orange": "amber lights mean check soon", "yellow": "amber lights mean check soon",
                  "green": "green lights show a system is on", "blue": "blue is the high-beam light",
                  "white": "white lights show a system is on"}
LIGHT_SEARCHES = ('intitle:"warning light"', 'intitle:"telltale"', 'intitle:"tell-tale"', 'intitle:"ISO 2575"',
                  'intitle:"dashboard symbol"', 'intitle:"dashboard icon"', 'intitle:"warning lamp"',
                  'intitle:"indicator light" car')
# Files the iso_machine_symbols pack already takes (the ISO 7000 files and these categories) are left out here.
ALREADY_IN_ISO_PACK = re.compile(r"ISO[ _]7000", re.I)
# A file must be about a road vehicle's dashboard: its words name one (or the symbol standard), and not an aircraft,
# a ship or a machine.
ROAD_VEHICLE = re.compile(r"\b(cars?|automobiles?|vehicles?|automotive|trucks?|lorr(y|ies)|vans?|motorcycles?|"
                          r"scooters?|dashboards?|instrument (cluster|panel)|tell-?tales?|ISO[ _]2575|honda|toyota|"
                          r"ford|volkswagen|vw|bmw|mercedes|nissan|hyundai|kia|tesla|renault|peugeot|fiat|skoda|"
                          r"subaru|mazda|chevrolet|opel|volvo|audi)\b", re.I)
NOT_ROAD = re.compile(r"\b(aircraft|airplanes?|aeroplanes?|aviation|cockpit|helicopters?|altimeter|navy|ships?|"
                      r"submarines?|locomotives?|trains?|tractors?|forklifts?)\b", re.I)


def light_meaning(words):
    """"the oil pressure warning light: ..." for words that name one of DASHBOARD_LIGHTS (the first that matches),
    or "". Two different lights named in the same words give "" (the file shows several: not one meaning)."""
    found = [meaning for pattern, meaning in DASHBOARD_LIGHTS if re.search(pattern, words, re.I)]
    names = {m.split(":")[0] for m in found}
    if not found or len(names) > 1 and not all(n in names for n in ("the turn signal (indicator) light",
                                                                    "the hazard warning light")):
        return ""
    return found[0]


def light_colour(words):
    """The one colour the words give the light ("red"), or "" when none or more than one is named."""
    colours = {c.lower() for c in LIGHT_COLOURS.findall(words)}
    colours = {"amber" if c in ("orange", "yellow") else c for c in colours}
    return colours.pop() if len(colours) == 1 else ""


def light_rows(title, text, credit):
    """The rows of one dashboard symbol file: its meaning (and its colour where the words give it), or [] when its
    own words name no light of DASHBOARD_LIGHTS (or several)."""
    words = f"{title.rsplit('.', 1)[0].replace('_', ' ')} {text}"
    meaning = light_meaning(words)
    if not meaning or ALREADY_IN_ISO_PACK.search(words) or not ROAD_VEHICLE.search(words) or NOT_ROAD.search(words):
        return []
    answer = f"This is {meaning}."
    colour = light_colour(words)
    if colour:
        answer += f" Its file says it is {colour}; {COLOUR_MEANING[colour]}."
    rows = [{"question": ASK_LIGHT, "answer": answer, "credit": credit}]
    if text and len(text.split()) >= 4:
        rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
    return rows


def build_commons_car_care(limit):
    """The commons_car_care pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CAR_CARE, limit, "carcare")


def build_commons_ev_charging(limit):
    """The commons_ev_charging pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(EV_CHARGING, limit, "evcharge")


def build_commons_dashboard_lights(limit):
    """Dashboard symbol files and photos found by Commons search on their titles, each kept only when its own words
    name one light of DASHBOARD_LIGHTS (drawings come as a black-on-white JPEG, as in iso_machine_symbols)."""
    from described_commons import search_titles
    from food_packs import with_twins
    from home_packs import home_entries, commons_fetch, file_name
    s = session()
    titles = []
    for query in LIGHT_SEARCHES:
        titles += search_titles(s, query, most=600)
    titles = [t for t in dict.fromkeys(titles) if not ALREADY_IN_ISO_PACK.search(t)]
    pass_random("dashlights").shuffle(titles)
    say(f"Commons dashboard lights: {len(titles)} files found by their titles")
    items = []
    for title, url, credit, text in home_entries(s, titles[:int(limit * 3) + 50], drawings=True):
        rows = light_rows(title, text, credit)
        if rows:
            items.append((file_name("dashlight", title), url, rows))
        if len(items) >= limit * 1.1 + 2:
            break
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- Open Images

CAR_OI = [
    group("What car parts or car care things are in this picture?",
          {"Tire": "a tyre", "Automotive tire": "a car tyre", "Tread": "a tyre tread", "Rim": "a wheel rim",
           "Alloy wheel": "an alloy wheel", "Hubcap": "a hubcap", "Auto part": "a car part",
           "Headlamp": "a headlamp", "Automotive lighting": "car lights", "Motor oil": "motor oil",
           "Antifreeze": "antifreeze (coolant)", "Bumper": "a bumper",
           "Vehicle registration plate": "a number plate (licence plate)"}),
    group("What car controls or gauges are in this picture?",
          {"Speedometer": "a speedometer", "Odometer": "an odometer", "Tachometer": "a rev counter (tachometer)",
           "Steering wheel": "a steering wheel", "Gear shift": "a gear lever"}),
    group("What vehicles or road things are in this picture?",
          {"Electric car": "an electric car", "Electric vehicle": "an electric vehicle", "Tow truck": "a tow truck",
           "Traffic cone": "a traffic cone"}),
    group("What kind of place is this?", {"Car wash": "a car wash"}),
]


def build_open_images_car_care(limit):
    """The open_images_car_care pack (see the module docstring)."""
    return build_oi_gap("open_images_car_care", CAR_OI, limit, 9301)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what}.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
CAR_CARE_PACKS = {
    "commons_car_care": (build_commons_car_care, COMMONS_LICENCE.format(
        what="car care categories (wipers, tyre valves, snow chains, jacks, wheel chocks and spare wheels, car "
             "washing, AdBlue, breakdowns and roadside help)")),
    "commons_ev_charging": (build_commons_ev_charging, COMMONS_LICENCE.format(
        what="electric vehicle charging connector, cable and port categories")),
    "commons_dashboard_lights": (build_commons_dashboard_lights, COMMONS_LICENCE.format(
        what="dashboard warning light files found by their own titles, each meaning taken from the file's own "
             "words")),
    "open_images_car_care": (build_open_images_car_care, OI_LICENCE),
}
CAR_CARE_LIMITS = {
    "commons_car_care": 900,           # 12 categories, an even share each
    "commons_ev_charging": 300,        # 5 categories, few free files
    "commons_dashboard_lights": 400,   # files whose own words name a light
    "open_images_car_care": 2500,      # 23 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
CAR_CARE_COMMONS_KEYS = ("commons_car_care", "commons_ev_charging", "commons_dashboard_lights")


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a car care pack builder.")
    parser.add_argument("key", choices=sorted(CAR_CARE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = CAR_CARE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
