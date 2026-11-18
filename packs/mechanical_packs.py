"""Pack builders for mechanical and automotive parts: car, motorcycle, bicycle and small-engine parts, machine parts
(bearings, gears, belts, pulleys, valves, pumps, motors, fasteners), plumbing and heating parts, engine bays,
dashboards and their warning symbols, and the condition of tyres and spark plugs. Used by build_packs.py in the same
way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a
row is {"question", "answer", "credit"}, plus "place" where the source states one (the country at a Commons photo's
camera coordinates, or the town a dataset's makers name), "child": true where the words of a picture name a child,
and "facts" where the source gives more than the part's name (the Commons category a file sits in, which often
names the maker; the vehicle a part belongs to; how far a tyre had been driven; a symbol's ISO number), kept for
later uses. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Every answer is a fixed sentence written here from the source's own labels: a Commons category's name, a folder or
class name the dataset's makers gave, the meaning written in a symbol file's own description, or a note a Commons
user drew on a photo. Nothing is written by an AI model. Plain identification comes first ("This is a ball
bearing."); a short purpose line is added from the fixed table below where the part is a common one, and the
standard meaning of the main dashboard warning lights (oil pressure, engine temperature, battery charging, brakes,
ABS, check-engine, tyre pressure, airbag, seat belt, low fuel, glow plugs) is added to those symbols. No repair
instructions are given.

Positions are only stated where the source marks them: Commons image notes (boxes a Commons user drew on a photo
and named) and a dataset's own boxes. They are said as places in the picture (left, right, top, bottom, centre),
never as the left or right of the car, which a photo cannot tell.

The packs (all open: CC0, public domain, CC BY, Apache-2.0 or BSD, checked at the source in November 2026):
  commons_car_parts       Wikimedia Commons categories of car and lorry parts: spark plugs, batteries, dipsticks,
                          air and oil filters, radiators, alternators, starter motors, brake discs, pads, calipers,
                          drums and shoes, shock absorbers and springs, timing and V-belts, pistons, connecting rods,
                          crankshafts, camshafts, cylinder heads, engines, carburettors, fuel injectors and pumps,
                          turbochargers, manifolds, catalytic converters, silencers, ignition coils, glow plugs,
                          clutches, gearboxes, differentials, drive shafts and joints, wheels, tyres and treads, flat
                          tyres, hubcaps, wheel nuts, headlamps, fuses, radiator caps, oil and antifreeze cans, jump
                          leads, flywheels, and car repair workshops. "What part is this?" -> "This is a spark plug:
                          it makes the spark that lights the fuel in a petrol engine's cylinder."
  commons_cycle_parts     Commons: bicycle parts (derailleurs, chains, cassettes, cranksets, brakes, hubs, pedals,
                          saddles, spokes, tyres, inner tubes, Presta, Schrader and Dunlop valves, forks, frames),
                          motorcycle parts (engines, exhausts, brakes, wheels, tyres, chains, dashboards) and small
                          engines (lawn mower and chainsaw parts, strimmers, leaf blowers, generators, outboard
                          motors, pull-cord starters), and bicycle and motorcycle repair.
  commons_machine_parts   Commons: bearings, gears, sprockets, chains, pulleys, belt drives, couplings, springs,
                          flywheels, valves of every common kind, pumps, compressors, hydraulic cylinders, electric,
                          stepper and servo motors, rivets, wing and acorn nuts, lock washers, threaded rods, split
                          pins, circlips, hose clips, O-rings and gaskets (the screws, nuts, bolts and washers are in
                          home_packs commons_tools), pipe fittings, flanges, sink traps, water meters, pressure
                          gauges, water heaters, air conditioners, heat pumps, heating radiators and their valves,
                          and cooling towers.
  commons_engine_bays     Commons photos of engine bays (files whose title names an engine bay, engine compartment or
                          the space under the bonnet), car and motorcycle dashboards, speedometers, rev counters, fuel
                          gauges and odometers. Where a Commons user drew named boxes on the photo (image notes), the
                          parts are said with their place in the picture: "Where is the battery in this engine bay?"
                          -> "The 12-volt battery is at the bottom right of the picture." Few photos have such
                          notes (six engine photos in November 2026, the best a 2023 Subaru Outback with twelve
                          parts named).
  iso_machine_symbols     Commons' ISO 7000 symbol files ("Graphical symbols for use on equipment", 2,260 files, CC0
                          or public domain as simple shapes) with the title and use written in each file's own
                          description, and the free files of Commons' dashboard-icon and warning-light categories.
                          "What does this symbol mean?" -> "It is the symbol for 'Engine oil pressure' (ISO 7000
                          number 0248). ..." with the standard warning-light advice for the main tell-tales.
  corolla_engine_bay      ARabeitak Car Parts (Judy Wagdy, Laila Hany, Rana Raafat and Steven Albert, 2023;
                          stevenalbert10/Toyota-Corolla-Car-Parts on Hugging Face, Apache-2.0): 1,452 phone photos of
                          the engine bay of a 2015 Toyota Corolla, each in the folder of the part it shows (air
                          filter, battery, coolant reservoir, engine, engine cover, reservoir cap, windscreen washer
                          fluid). "What part is this?" -> "This is the battery." (no boxes, so no positions).
  tyre_condition          Three tyre collections from India on Mendeley Data, all CC BY 4.0: "Digital images of
                          defective and good condition tyres" (Velammal Engineering College, 1,856 phone photos,
                          bn7ch8tvyp), "TyreNet" (Presidency University, 1,698 photos from car and bike service
                          stations and tyre showrooms, 32b5vfj6tc; a RAR archive opened with bsdtar or 7-Zip) and the
                          "Annotated Tyre Image Dataset for Machine Learning-Based Life Prediction" (Meerut Institute
                          of Engineering and Technology, 620 photos taken at service stations in Meerut, each filed
                          under the distance the tyre had been driven, dfzbm2ktss). "Is this tyre in good condition?"
                          -> "No: this tyre was marked as defective." / "How far has this tyre been driven?"
  spark_plug_condition    Spark Plug Condition Classification (eoinedge on Hugging Face, BSD-3-Clause; made for an
                          Edge Impulse demonstration): 697 photos of spark plugs, normal, carbon-fouled, oil-fouled or
                          mechanically damaged. "What condition is this spark plug in?"
  planetary_gearbox       Planetary Gear Dataset (Gaurang Sharma and Roel Pieters, Tampere University, Zenodo 8223473,
                          CC BY 4.0): the 150 real photos (not the computer-made variations) of a small planetary
                          gearbox being put together, with its parts boxed: planet gears, sun gear, housing, top,
                          stepper motor and driver. "What parts are in this picture, and where?"

Share-alike, non-commercial and research collections on the same subjects (Commons BY-SA files and the BY-SA
dashboard symbols, the Roboflow dashboard warning icons, the Humans in the Loop car parts and damages, DSMLR car part
segmentation, the Mechanical Parts Dataset 2022, Renault's AutoVI), the sign-up collections and the ones looked at
and left out are in training-kit/kit/mechanical_sources.py.

    python packs/mechanical_packs.py commons_car_parts --limit 8      (prints a few rows: a quick check)
"""

import collections
import io
import json
import math
import os
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, considered, ALT_TEXT
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from build_packs import needs_description  # pictures set aside for a description (see build_packs)
from food_packs import with_twins, count_pictures, commons_get, commons_members, commons_description, credit_licence
from home_packs import commons_fetch, file_name, symbol_picture, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count
from places import where, country_at

PART_Q = "What part is this?"
THING_Q = "What is this?"
PLACE_Q = "What kind of place is this?"
DOING_Q = "What is happening in this picture?"


# ----------------------------------------------------------------- shared: positions in a picture

def spot(cx, cy):
    """Where a point (as fractions of the picture's width and height) is, in plain words: "at the top left of the
    picture", "on the right of the picture", "in the centre of the picture"."""
    across = "left" if cx < 1 / 3 else "right" if cx > 2 / 3 else ""
    down = "top" if cy < 1 / 3 else "bottom" if cy > 2 / 3 else ""
    if not across and not down:
        return "in the centre of the picture"
    if not down:
        return f"on the {across} of the picture"
    if not across:
        return f"at the {down} of the picture"
    return f"at the {down} {across} of the picture"


def the_name(label):
    """A part's label as said in a sentence with "the": "Battery" -> "the battery", "ABS unit" -> "the ABS unit",
    "The oil filler cap" -> "the oil filler cap"."""
    label = re.sub(r"^(the|a|an)\s+", "", clean(label).rstrip(".:;,"), flags=re.I)
    if len(label) > 1 and not label[:2].isupper():
        label = label[0].lower() + label[1:]
    return "the " + label


def safe_name(path):
    """A file path as a plain file name without its extension ("Air Filter/2022 1.jpg" -> "Air_Filter_2022_1")."""
    return re.sub(r"[^\w-]+", "_", path.rsplit(".", 1)[0]).strip("_")


def capital(text):
    """The text with its first letter in capitals."""
    return text[:1].upper() + text[1:]


# ----------------------------------------------------------------- shared: Wikimedia Commons

# Free licences only (never BY-SA, NC or ND: those are the kit's commons_mechanical_sa).
MECH_FREE = re.compile(r"^(cc0|public domain|pd|cc by \d|cc-by-\d|cc by-\d|mit|expat|apache|copyrighted free use)",
                       re.I)
# File and subcategory names that are not photos of the thing: drawings, art, adverts, toys and models, patents.
NOT_A_PHOTO = re.compile(r"\b(drawings?|illustrations?|paintings?|logos?|icons?|emoji|cartoons?|clip ?art|diagrams?|"
                         r"schemas?|schematics?|in art|in heraldry|coats? of arms|stamps?|maps?|advertis\w*|videos?|"
                         r"audio|animations?|animated|patents?|toys?|scale models?|lego|miniatures?|plans?|"
                         r"blueprints?|charts?|graphs?|posters?|brochures?|manuals?|\.(svg|gif|webm|ogg|ogv|pdf|"
                         r"tiff?|djvu|stl))\b", re.I)
# Subcategories that are about something else than the thing: firms, places, people and events.
NOT_THE_THING = re.compile(r"\b(compan(y|ies)|manufacturers?|factor(y|ies)|plants? in|museums?|people|persons|"
                           r"inventors?|history|exhibitions?|shows?|events?|races?|racing|stores?|shops?|"
                           r"buildings?|streets?|stations?|by country|by year|by decade|by city|in \w+ \d{4}|"
                           r"sculptures?|monuments?|statues?|memorials?)\b", re.I)
# Descriptions that are only a camera's or an archive's record, a link, or the photographer's own story ("We
# started the jeep's engine ..."), not words about the picture.
JUST_A_RECORD = re.compile(r"original digital file|descriptive metadata|date picture taken|collectie\s*/\s*archief|"
                           r"bestanddeelnr|\bexif\b|camera (make|model)|^(img|dsc|p)\d|https?://|www\.|"
                           r"link below|\b(we|our|my|me)\b|\bI\b", re.I)
# Words the child check would take for a child ("infantry", "infantryman"), taken out before it looks.
NOT_A_CHILD = re.compile(r"\binfantr\w*", re.I)
IN_A_PLACE = re.compile(r"\bin (the )?[A-Z]\w+( \w+)?$")      # "... in Germany", "... in the United States"
PLACES = {}            # {file title: the country at its camera coordinates}


def mech_entries(s, titles, drawings=False):
    """[(title, picture address, credit, caption or description)] for Commons files whose licence is CC0, public
    domain, CC BY, MIT or Apache, 50 files a request (pictures 1,280 pixels wide, a width Wikimedia keeps ready);
    JPEG and PNG photos, and SVG drawings too when drawings is True (Commons sends a PNG of them). Every file left out
    is noted with its reason (considered()). Where a file's page gives the camera's coordinates, the country is kept
    in PLACES."""
    kinds = ("image/jpeg", "image/png") + (("image/svg+xml",) if drawings else ())
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 600 if drawings else 1280,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|GPSLatitude|"
                                                      "GPSLongitude",
                               "iiextmetadatalanguage": "en"})
        pages = [p for p in ((data.get("query") or {}).get("pages") or {}).values() if p.get("pageid")]
        captions = {}
        if pages:
            entities = commons_get(s, {"action": "wbgetentities", "ids": "|".join(f"M{p['pageid']}" for p in pages),
                                       "props": "labels", "languages": "en"}).get("entities", {})
            captions = {k: ((v.get("labels") or {}).get("en") or {}).get("value", "") for k, v in entities.items()}
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            upper = licence.upper()
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            if not MECH_FREE.match(licence) or re.search(r"\b(SA|NC|ND)\b|-SA|-NC|-ND", upper):
                considered(p["title"], page, f"its licence ({licence or 'none given'}) is not CC0, public domain, "
                                             "CC BY, MIT or Apache (BY-SA files are in the kit's share-alike entry)")
                continue
            if info.get("mime") not in kinds or not info.get("thumburl"):
                considered(p["title"], page, f"not a photo this pack takes ({info.get('mime') or 'no picture'})")
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            text = commons_description(captions.get(f"M{p['pageid']}"),
                                       (meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}", text,
                        clean((meta.get("ImageDescription") or {}).get("value"))))
            if meta.get("GPSLatitude") and meta.get("GPSLongitude"):
                PLACES[p["title"]] = country_at(clean(meta["GPSLatitude"].get("value")),
                                                clean(meta["GPSLongitude"].get("value")))
        time.sleep(1)
    return out


def category_files(s, category, deeper, most_subcategories=25):
    """{file title: the subcategory it came from ("" for the category itself)} for a Commons category and, when
    deeper, its first most_subcategories subcategories (not those about firms, places, people or art). Drawings,
    adverts, toys and models are left out by their names. A category that does not exist gives none."""
    found = {t: "" for t in commons_members(s, category, "file") if not NOT_A_PHOTO.search(t)}
    if deeper:
        subs = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
        subs = [c for c in subs if not NOT_A_PHOTO.search(c) and not NOT_THE_THING.search(c)
                and not IN_A_PLACE.search(c)]
        for sub in subs[:most_subcategories]:
            for t in commons_members(s, sub, "file"):
                if not NOT_A_PHOTO.search(t):
                    found.setdefault(t, sub)
    return found


def answer_for(name, purpose=None):
    """ "This is a spark plug: it makes the spark ..." (or "This is a spark plug." when there is no purpose line);
    "These are brake shoes ..." for a plural name ("brake shoes", "wheel nuts (lug nuts)")."""
    plural = not re.match(r"(a|an|the)\b", name) and re.search(r"s\b", name.split(" (")[0])
    start = "These are" if plural else "This is"
    return f"{start} {name}: {purpose}" if purpose else f"{start} {name}."


# Words that show a description is in English, and words that show it is in another language.
ENGLISH_WORDS = re.compile(r"\b(the|of|with|and|is|are|on|this|from|for|at|by)\b", re.I)
OTHER_WORDS = re.compile(r"\b(der|die|das|und|mit|ein|eine|le|la|les|des|du|et|est|avec|het|een|van|en|el|los|"
                         r"con|del|il|di|che|och|på|og|af|na|ze|się|une|aus|den)\b", re.I)


def in_english(text):
    """Whether a description reads as English: Latin letters only, and more English than other common words."""
    if not text or re.search(r"[^\x00-\u024f\u2010-\u2027\u00b0]", text):
        return False
    return len(ENGLISH_WORDS.findall(text)) > len(OTHER_WORDS.findall(text))


def build_commons_parts(specs, limit, prefix):
    """A Commons pack from specs: [(category, deeper, question, name, purpose)] (purpose may be None; the name is
    said after "This is": "a spark plug", "brake pads"). The categories take turns, in a fixed shuffled order, so
    each gets an even share. Each picture gets the category's question and answer and, when it has a real,
    respectful caption or description, "Write a short description ..." with it. "facts" keeps the subcategory a file
    came from (which often names the maker or the vehicle: "Bosch spark plugs") and the file's own title."""
    s, items, seen = session(), [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    want = int(limit * 1.15) + 2
    queues = [[spec, None] for spec in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            (category, deeper, question, name, purpose), files = q
            if files is None:
                found = category_files(s, category, deeper)
                files = [(t, sub) for t, sub in found.items() if t not in seen]
                pass_random(category).shuffle(files)
                say(f"Commons {category}: {len(files)} files")
            batch, q[1] = files[:share * 2], files[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            subs = dict(batch)
            got = 0
            for title, url, credit, text, _ in mech_entries(s, [t for t, _ in batch]):
                if got >= share or title in seen:
                    continue
                words = NOT_A_CHILD.sub(" ", f"{title} {text}")
                text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
                if NUDE.search(words):
                    considered(title, url, "its words are about nudity")
                    continue
                seen.add(title)
                place = where(PLACES.get(title, ""))
                facts = {"commons_category": subs.get(title) or category,
                         "commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0]}
                rows = [mark_child({"question": question, "answer": answer_for(name, purpose), "credit": credit,
                                    "facts": facts, **place}, words)]
                if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
                    rows.append(mark_child({"question": ALT_TEXT, "answer": text, "credit": credit, **place}, words))
                items.append((file_name(prefix, title), url, rows))
                got += 1
            if not q[1]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    return with_twins(commons_fetch(items[:want])[:limit])


# ----------------------------------------------------------------- commons_car_parts

def part(category, name, purpose=None, deeper=False, question=PART_Q):
    """One category spec for build_commons_parts."""
    return (category, deeper, question, name, purpose)


COMMONS_CAR_PARTS = [
    # engine and ignition
    part("Spark plugs", "a spark plug", "it makes the spark that lights the fuel in a petrol engine's cylinder.",
         True),
    part("Glow plugs", "a glow plug", "it heats a diesel engine's cylinder to help the engine start when cold."),
    part("Ignition coils", "an ignition coil", "it makes the high voltage for the spark plugs."),
    part("Ignition distributor parts", "a part of an ignition distributor",
         "the distributor sends the spark to each spark plug in turn."),
    part("Automobile engines", "a car engine", deeper=True, question=THING_Q),
    part("Vintage car engines", "an old car engine", question=THING_Q),
    part("Pistons", "a piston", "it moves up and down in the cylinder, pushed by the burning fuel.", True),
    part("Connecting rods", "a connecting rod", "it links a piston to the crankshaft."),
    part("Crankshafts", "a crankshaft", "it turns the up-and-down movement of the pistons into turning.", True),
    part("Camshafts", "a camshaft", "its lobes open and close the engine's valves.", True),
    part("Cylinder heads", "a cylinder head", "it closes the top of the engine's cylinders and holds the valves.",
         True),
    part("Timing belts", "a timing belt", "it keeps the engine's camshaft turning in step with the crankshaft."),
    part("Flywheels", "a flywheel", "a heavy wheel that keeps an engine turning smoothly."),
    part("Dual-mass flywheel", "a dual-mass flywheel", "a flywheel in two parts with springs between them, which "
                                                       "smooths the engine's pulses before the gearbox."),
    part("Oil dipsticks", "an engine oil dipstick", "it is pulled out to check the level of the engine oil."),
    part("Oil pan", "an engine oil pan (sump)", "it holds the engine oil under the engine."),
    part("Oil filters", "an oil filter", "it cleans dirt out of the engine oil.", True),
    part("Air filters", "an air filter", "it catches dust in the air going into an engine or an air system.", True),
    # fuel, air and exhaust
    part("Carburetors", "a carburettor", "it mixes air and petrol for the engine, on older cars, motorcycles and "
                                         "small engines.", True),
    part("Fuel injectors", "a fuel injector", "it sprays fuel into the engine.", True),
    part("Fuel pumps (engine)", "a fuel pump", "it pumps fuel from the tank to the engine."),
    part("Turbochargers", "a turbocharger", "driven by the exhaust gas, it blows extra air into the engine for more "
                                            "power.", True),
    part("Intake manifolds", "an intake manifold", "it carries air to the engine's cylinders."),
    part("Exhaust manifolds", "an exhaust manifold", "it collects the exhaust gas from the engine's cylinders."),
    part("Catalytic converters", "a catalytic converter", "it cleans harmful gases out of the exhaust."),
    part("Exhaust silencers", "an exhaust silencer (muffler)", "it makes the engine quieter."),
    part("Exhaust systems", "a vehicle's exhaust", "the pipes that carry the engine's exhaust gas away.", True),
    part("Lambda sensors", "a lambda (oxygen) sensor", "it measures the oxygen in the exhaust so the engine can "
                                                       "get its fuel mixture right."),
    # cooling and electrics
    part("Radiators (engine cooling)", "an engine radiator", "it cools the liquid that carries heat away from the "
                                                             "engine.", True),
    part("Radiator caps", "a radiator cap", "it closes the cooling system's filler; it must not be opened while the "
                                            "engine is hot."),
    part("Automobile thermostats", "an engine thermostat", "it opens when the coolant is hot, to keep the engine at "
                                                           "the right temperature."),
    part("Automobile batteries", "a car battery", "it powers the starter motor and the car's electrics.", True),
    part("Alternators", "an alternator", "driven by the engine, it makes electricity and charges the battery.", True),
    part("Electric starter motors", "a starter motor", "it turns the engine over to start it."),
    part("Engine starters", "an engine starter", "it turns the engine over to start it."),
    part("Automobile fuses", "car fuses", "a fuse protects a circuit; it burns through if too much current flows."),
    part("Jumper cables (vehicle jump start)", "a set of jump leads (jumper cables)",
         "they connect a flat battery to a good one to start a car."),
    # drive
    part("Automobile clutches", "a car clutch", "it connects and disconnects the engine and the gearbox."),
    part("Clutches", "a clutch", "it connects and disconnects an engine and what it drives.", True),
    part("Automobile transmissions", "a car gearbox (transmission)", deeper=True),
    part("Automatic transmissions", "an automatic gearbox (transmission)", deeper=True),
    part("Automotive manual transmissions", "a manual gearbox (transmission)"),
    part("Torque converters", "a torque converter", "a fluid coupling between the engine and an automatic gearbox."),
    part("Differentials", "a differential", "it lets the wheels on each side turn at different speeds round "
                                            "corners.", True),
    part("Driveshafts", "a drive shaft", "it carries the turning from the gearbox to the wheels."),
    part("Constant-velocity joints", "a constant-velocity (CV) joint",
         "it lets a drive shaft bend while it turns, so the front wheels can steer and be driven."),
    part("Universal joints", "a universal joint", "it joins two shafts at an angle so they can turn together."),
    # brakes, suspension and wheels
    part("Brake disks", "a brake disc", "it turns with the wheel; the brake pads squeeze it to slow the vehicle.",
         True),
    part("Disk brakes", "a disc brake", "pads squeeze a disc that turns with the wheel, to slow it.", True),
    part("Brake calipers", "a brake caliper", "it squeezes the brake pads against the brake disc."),
    part("Drum brakes", "a drum brake", "brake shoes press outwards inside a drum that turns with the wheel.", True),
    part("Brake shoes", "brake shoes", "they press against the inside of a brake drum to slow the wheel."),
    part("Brake master cylinders", "a brake master cylinder",
         "it turns the push on the brake pedal into fluid pressure for the brakes."),
    part("Shock absorbers", "a shock absorber", "it damps the bouncing of a vehicle's springs.", True),
    part("Leaf springs", "a leaf spring", "a stack of curved steel strips used as a spring, often on lorries and "
                                          "older cars.", True),
    part("Wheel hubs", "a wheel hub", "the centre part that a wheel is bolted to.", True),
    part("Automobile wheels", "a car wheel", deeper=True),
    part("Tires", "a tyre", deeper=True),
    part("Automobile tire treads", "the tread of a car tyre", "the grooved part that grips the road."),
    part("Flat tires", "a flat tyre", "the tyre has lost its air."),
    part("Hubcaps", "a hubcap", "a cover over the centre of a wheel.", True),
    part("Lug nuts", "wheel nuts (lug nuts)", "they hold a wheel on its hub."),
    part("Central lug nuts", "a centre-lock wheel nut", "one large nut that holds the wheel on, on some sports and "
                                                       "racing cars."),
    part("Wheel locks", "a locking wheel nut", "a wheel nut that needs a special key, so the wheel cannot be "
                                               "stolen."),
    part("Tyre pressure gauges", "a tyre pressure gauge", "it measures the air pressure in a tyre."),
    part("Tire changers", "a tyre-changing machine", "a workshop machine that takes a tyre off its wheel and puts it "
                                                    "back.", question=THING_Q),
    part("Tire repair", "a tyre being repaired", question=DOING_Q, deeper=True),
    part("Brake fluid", "brake fluid", "the liquid that carries the push of the brake pedal to the brakes.",
         question=THING_Q),
    part("Automobile headlamps", "a car headlamp", deeper=True),
    # supplies, tools and workshops
    part("Motor oil cans", "a can of engine oil", question=THING_Q),
    part("Antifreeze", "antifreeze (engine coolant)", "it is mixed with water in the cooling system so it does not "
                                                     "freeze; it is poisonous.", question=THING_Q),
    part("Grease guns", "a grease gun", "a hand pump that pushes grease into a machine's grease points.",
         question=THING_Q),
    part("Oil filter wrenches", "an oil filter wrench", "a tool for turning an oil filter.", question=THING_Q),
    part("Automobile repair shops", "a car repair workshop (garage)", question=PLACE_Q),
]


def build_commons_car_parts(limit):
    """The Commons car parts pack."""
    return build_commons_parts(COMMONS_CAR_PARTS, limit, "carpart")


# ----------------------------------------------------------------- commons_cycle_parts

COMMONS_CYCLE_PARTS = [
    # bicycles
    part("Bicycle derailleur gears", "a bicycle derailleur", "it moves the chain from one sprocket to another to "
                                                             "change gear.", True),
    part("Bicycle front derailleurs", "a bicycle front derailleur", "it moves the chain between the front "
                                                                    "chainrings."),
    part("Bicycle rear derailleur pulley wheels", "the small pulley wheels of a bicycle's rear derailleur"),
    part("Bicycle chains", "a bicycle chain", "it carries the pedalling to the back wheel.", True),
    part("Bicycle cassettes", "a bicycle cassette", "the cluster of sprockets on the back wheel, for the gears."),
    part("Bicycle cranksets", "a bicycle crankset", "the pedal arms with the front chainrings.", True),
    part("Bicycle chainrings", "a bicycle chainring", "the toothed ring at the front that the chain runs on."),
    part("Bicycle brakes", "a bicycle brake", deeper=True),
    part("Bicycle rim brakes", "a bicycle rim brake", "its pads squeeze the rim of the wheel.", True),
    part("Bicycle brake pads", "bicycle brake pads"),
    part("Bicycle coaster brakes", "a bicycle coaster brake", "a brake in the back hub, worked by pedalling "
                                                              "backwards."),
    part("Bicycle roller brakes", "a bicycle roller brake", "a brake inside the wheel hub."),
    part("Bicycle hubs", "a bicycle hub", "the centre of the wheel, which turns on bearings.", True),
    part("Bicycle freewheels", "a bicycle freewheel", "it lets the back wheel turn while the pedals stay still."),
    part("Bicycle pedals", "a bicycle pedal", deeper=True),
    part("Bicycle saddles", "a bicycle saddle", deeper=True),
    part("Bicycle spokes", "bicycle spokes", "the thin wires that join the hub to the rim."),
    part("Bicycle tires", "a bicycle tyre", deeper=True),
    part("Bicycle wheel inner tubes", "a bicycle inner tube", "the rubber tube inside the tyre that holds the air."),
    part("Presta valves", "a Presta valve", "a thin bicycle tyre valve with a small locking nut at its tip."),
    part("Schrader valves", "a Schrader valve", "the same kind of tyre valve as on cars."),
    part("Dunlop valves", "a Dunlop (Woods) valve", "a bicycle tyre valve used in much of Europe and Asia."),
    part("Bicycle headsets", "a bicycle headset", "the bearings that let the front fork and handlebars turn."),
    part("Bicycle forks", "a bicycle fork", "it holds the front wheel."),
    part("Bicycle suspension forks", "a bicycle suspension fork", "a front fork with springs, for rough ground."),
    part("Bicycle frames", "a bicycle frame", deeper=True),
    part("Bicycle stems", "a bicycle stem", "it joins the handlebars to the fork."),
    part("Bottom brackets", "a bicycle bottom bracket", "the bearing that the pedal cranks turn on."),
    part("Bicycle bells", "a bicycle bell"),
    part("Bicycle lights", "a bicycle light"),
    part("Bicycle parts", "a bicycle part"),
    part("Bicycle repair", "a bicycle being repaired", question=DOING_Q),
    part("Bicycle repair stands", "a bicycle repair stand", "it holds a bicycle off the ground while it is worked "
                                                            "on.", question=THING_Q),
    # motorcycles
    part("Motorcycle engines", "a motorcycle engine", deeper=True, question=THING_Q),
    part("Motorcycle exhausts", "a motorcycle exhaust", deeper=True),
    part("Expansion chamber", "an expansion chamber", "the bulging exhaust pipe of a two-stroke engine."),
    part("Motorcycle brakes", "a motorcycle brake"),
    part("Motorcycle disk brakes", "a motorcycle disc brake"),
    part("Motorcycle drum brakes", "a motorcycle drum brake"),
    part("Motorcycle wheels", "a motorcycle wheel", deeper=True),
    part("Motorcycle tires", "a motorcycle tyre"),
    part("Motorcycle chains", "a motorcycle chain", "it carries the drive to the back wheel."),
    part("Motorcycle final drives", "a motorcycle's final drive", "the chain, belt or shaft that drives the back "
                                                                  "wheel.", True),
    part("Motorcycle dashboards", "a motorcycle's instrument panel", question=THING_Q),
    part("Motorcycle fuel gauges", "a motorcycle fuel gauge", "it shows how much fuel is in the tank."),
    part("Motorcycle parts", "a motorcycle part"),
    part("Motorcycle repair shops", "a motorcycle repair workshop", question=PLACE_Q, deeper=True),
    part("Motorcycle repairs", "a motorcycle being repaired", question=DOING_Q),
    # small engines
    part("Small engines", "a small engine", "the kind of petrol engine used in lawn mowers, generators and garden "
                                            "machines.", True, THING_Q),
    part("Parts of lawn mowers", "a part of a lawn mower"),
    part("Chainsaw parts", "a chainsaw part"),
    part("String trimmers", "a string trimmer (strimmer)", "it cuts grass with a fast-spinning nylon line.",
         question=THING_Q),
    part("Brushcutters", "a brushcutter", "it cuts thick grass and brush with a spinning blade.", question=THING_Q),
    part("Leaf blowers", "a leaf blower", question=THING_Q),
    part("Engine-generators", "a generator", "an engine that drives an electricity generator.", True, THING_Q),
    part("Diesel generators", "a diesel generator", question=THING_Q),
    part("Portable electrical generators", "a portable generator", question=THING_Q),
    part("Outboard motors", "an outboard motor", "an engine with a propeller that clamps onto the back of a boat.",
         True, THING_Q),
    part("Recoil start", "a pull-cord (recoil) starter", "pulling the cord turns the engine over to start it."),
    part("Stationary engines", "a stationary engine", "an engine that stays in one place and drives a pump, "
                                                      "generator or machine.", question=THING_Q),
]


def build_commons_cycle_parts(limit):
    """The Commons bicycle, motorcycle and small-engine parts pack."""
    return build_commons_parts(COMMONS_CYCLE_PARTS, limit, "cyclepart")


# ----------------------------------------------------------------- commons_machine_parts

COMMONS_MACHINE_PARTS = [
    # bearings
    part("Ball bearings", "a ball bearing", "it lets a shaft turn smoothly, on a ring of steel balls.", True),
    part("Roller bearings", "a roller bearing", "it lets a shaft turn smoothly, on steel rollers.", True),
    part("Needle roller bearings", "a needle roller bearing", "a bearing with long, thin rollers."),
    part("Spherical bearings", "a spherical bearing", "a ball-and-socket bearing that lets a joint swivel."),
    part("Pillow blocks", "a pillow block bearing", "a bearing in a housing that bolts to a surface."),
    part("Bearings", "a bearing", "it lets a shaft turn smoothly."),
    # gears and drives
    part("Gears", "a gear (toothed wheel)", "gears pass turning from one shaft to another."),
    part("Spur gears", "a spur gear", "a gear with straight teeth."),
    part("Bevel gears", "bevel gears", "cone-shaped gears that turn the drive through an angle.", True),
    part("Worm gears", "a worm gear", "a screw that turns a toothed wheel, for a big reduction in speed.", True),
    part("Herringbone gears", "a herringbone gear", "a gear with V-shaped teeth."),
    part("Chain drive sprockets", "a sprocket", "a toothed wheel that a chain runs on."),
    part("Roller chains", "a roller chain", "a chain that runs on sprockets to pass on turning.", True),
    part("Drive chains", "a drive chain"),
    part("Pulleys", "a pulley", "a wheel for a rope or belt to run on."),
    part("Belt drives", "a belt drive", "a belt running on pulleys passes turning from one shaft to another."),
    part("V belt drives", "a V-belt drive", "a belt with a V-shaped edge running on grooved pulleys."),
    part("Beam couplings", "a beam coupling", "a flexible coupling that joins two shafts."),
    part("Jaw couplings", "a jaw coupling", "a coupling that joins two shafts with interlocking jaws."),
    part("Oldham couplings", "an Oldham coupling", "a coupling that joins two shafts that are slightly out of line."),
    part("Giubo", "a flexible rubber coupling (giubo)", "it joins a drive shaft to the gearbox or axle."),
    part("Springs (mechanical)", "a spring", deeper=True),
    part("Coil springs", "a coil spring", deeper=True),
    # valves
    part("Valves", "a valve", "it opens, closes or controls a flow of liquid or gas."),
    part("Ball valves", "a ball valve", "a quarter-turn valve: a ball with a hole through it turns to open or "
                                        "close it."),
    part("Gate valves", "a gate valve", "a wheel lowers a gate across the pipe to shut it.", True),
    part("Butterfly valves", "a butterfly valve", "a disc turns in the pipe to open or close it."),
    part("Globe valves", "a globe valve", "a valve for controlling the flow, with a rounded body."),
    part("Check valves", "a check valve (non-return valve)", "it lets the flow go one way only.", True),
    part("Relief valves", "a pressure relief valve", "it opens by itself to let out pressure that is too high."),
    part("Steam boiler safety valves", "a boiler safety valve", "it opens by itself if the pressure gets too high."),
    part("Solenoid valves", "a solenoid valve", "an electrically worked valve."),
    part("Expansion valves", "an expansion valve", "it lets the refrigerant expand and cool, in a fridge, air "
                                                   "conditioner or heat pump."),
    part("Thermostatic radiator valves", "a thermostatic radiator valve", "it controls the heat of a radiator by "
                                                                          "the room temperature."),
    # pumps, compressors, hydraulics and motors
    part("Pumps", "a pump", "it moves a liquid or gas."),
    part("Centrifugal pumps", "a centrifugal pump", "a spinning impeller moves the liquid.", True),
    part("Piston pumps", "a piston pump", "a piston moving in a cylinder moves the liquid.", True),
    part("Hand pumps", "a hand pump", "a pump worked by hand, often for water from a well.", True),
    part("Gear pumps", "a gear pump", "two gears turning together move the liquid, often oil."),
    part("Air compressors", "an air compressor", "it squeezes air into a tank to power air tools and blow up tyres.",
         question=THING_Q),
    part("Scroll compressors", "a scroll compressor", "used in air conditioners and heat pumps."),
    part("Hydraulic cylinders", "a hydraulic cylinder", "oil pressure pushes a rod out of it with great force."),
    part("Electric motors", "an electric motor"),
    part("Stepper motors", "a stepper motor", "an electric motor that turns in small exact steps."),
    part("Servomotors", "a servo motor", "a motor whose position is controlled exactly."),
    # fasteners and seals (the screws, nuts, bolts and washers are in home_packs commons_tools)
    part("Rivets", "rivets", "metal pins that join plates for good.", True),
    part("Blind rivets", "blind (pop) rivets", "rivets that are set from one side with a rivet gun."),
    part("Wing nuts", "a wing nut", "a nut with two wings, turned by hand."),
    part("Acorn nuts", "an acorn (cap) nut", "a nut with a rounded top that covers the end of the bolt."),
    part("Lock washers", "lock washers", "washers that stop a nut working loose.", True),
    part("Threaded rods", "a threaded rod", "a rod threaded all along, for nuts."),
    part("Cotter pins", "a split pin (cotter pin)", "a bent pin that stops a nut or pin working loose.", True),
    part("Circlips", "a circlip", "a springy ring that clips into a groove to hold a part on a shaft.", True),
    part("Hose clamps", "a hose clip (hose clamp)", "it tightens a hose onto a pipe."),
    part("O-rings", "O-rings", "rubber rings that seal a joint."),
    part("Gaskets", "a gasket", "a flat seal between two parts.", True),
    # plumbing
    part("Elbow pipe fittings", "an elbow pipe fitting", "it joins two pipes at an angle."),
    part("Tee fittings", "a tee pipe fitting", "it joins three pipes in a T."),
    part("Butt welding fittings", "a butt-welding pipe fitting"),
    part("Flanges", "a pipe flange", "a flat rim bolted to another to join pipes."),
    part("Siphons", "a sink trap (siphon)", "the bend under a sink that holds water to keep drain smells out."),
    part("Water meters", "a water meter", "it measures how much water is used.", True),
    part("Pressure gauges", "a pressure gauge", "it shows the pressure of a gas or liquid.", True),
    part("Water heating devices", "a water heater", deeper=True, question=THING_Q),
    part("Tankless water heaters", "a tankless water heater", "it heats water only as it flows.", True, THING_Q),
    # heating, ventilation and air conditioning
    part("Air conditioners", "an air conditioner", question=THING_Q),
    part("Split type air conditioners - condenser", "the outdoor unit of a split air conditioner",
         "it gives off the heat taken from the room.", question=THING_Q),
    part("Split type air conditioners - evaporators", "the indoor unit of a split air conditioner",
         "it blows cooled air into the room.", question=THING_Q),
    part("Air source heat pumps", "an air source heat pump", "it takes heat from the outside air to heat a "
                                                            "building.", question=THING_Q),
    part("Heat pumps", "a heat pump", "it moves heat into or out of a building.", True, THING_Q),
    part("Sheet metal radiators", "a heating radiator", "hot water from the boiler flows through it to heat the "
                                                        "room.", question=THING_Q),
    part("Finned tube radiators", "a finned-tube radiator", "a heating pipe with metal fins.", question=THING_Q),
    part("Cooling towers", "a cooling tower", "it cools water from a power station or factory in the air.",
         question=THING_Q),
]


def build_commons_machine_parts(limit):
    """The Commons machine, plumbing and heating parts pack."""
    return build_commons_parts(COMMONS_MACHINE_PARTS, limit, "machinepart")


# ----------------------------------------------------------------- commons_engine_bays

ENGINE_BAY_Q = "What is this?"
ENGINE_BAY = ("This is a vehicle's engine bay: the space that holds the engine, usually under the bonnet (hood).")
# Title searches for engine bays (Commons has no category for them), and words that show another kind of engine room.
ENGINE_BAY_SEARCHES = ('intitle:"engine bay"', 'intitle:"engine compartment"', 'intitle:"under bonnet"',
                       'intitle:"under-bonnet"', 'intitle:"underhood"', 'intitle:"under the hood"',
                       )
NOT_A_ROAD_VEHICLE = re.compile(r"\b(ship|uss|hms|ns|navy|naval|aircraft|airplane|aeroplane|helicopter|jet|"
                                r"starfighter|hornet|boat|submarine|locomotive|reactor|tank|train|railcar|f-\d+)\b",
                                re.I)
# Engine-bay photos with image notes (Commons' search takes one phrase at a time here: it has no brackets).
NOTED_BAYS = tuple(f'hastemplate:ImageNote "{phrase}"' for phrase in ("engine bay", "engine compartment",
                                                                      "under the hood", "under-bonnet", "underhood",
                                                                      "under bonnet"))
# A noted photo is kept only when its title says it shows an engine or what is under the bonnet.
SHOWS_AN_ENGINE = re.compile(r"\b(engine|bonnet|hood|underhood|motor)\b|engine[ -]?bay|under-bonnet", re.I)
NOT_A_CAR_ENGINE = re.compile(r"engine house|\bmines?\b|castle|cruiser|vessel|drawing", re.I)
DASHBOARDS = [
    part("Automobiles with open hoods", "a car with its bonnet (hood) open, showing the engine bay", deeper=True,
         question=THING_Q),
    part("Automobile dashboards", "a car's dashboard", "the panel in front of the driver, with the instruments.",
         True, THING_Q),
    part("Automobile gauges", "a gauge from a car's dashboard", question=THING_Q),
    part("Speedometers", "a speedometer", "it shows how fast the vehicle is going.", True, THING_Q),
    part("Tachometers", "a rev counter (tachometer)", "it shows how fast the engine is turning.", True, THING_Q),
    part("Fuel gauges", "a fuel gauge", "it shows how much fuel is in the tank.", True, THING_Q),
    part("Automobile fuel gauges", "a car's fuel gauge", "it shows how much fuel is in the tank.",
         question=THING_Q),
    part("Odometers", "an odometer", "it shows how far the vehicle has gone in all.", True, THING_Q),
]


def search_files(s, query, most=2000):
    """The titles of Commons files a search finds (CirrusSearch), at most most."""
    titles, offset = [], 0
    while offset < most:
        data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srsearch": query,
                               "srlimit": 500, "sroffset": offset})
        hits = (data.get("query") or {}).get("search", [])
        titles += [h["title"] for h in hits]
        if "continue" not in data or not hits:
            break
        offset = data["continue"].get("sroffset", offset + 500)
        time.sleep(1)
    return titles


NOTE = re.compile(r"\{\{\s*ImageNote\s*\|([^{}]*)\}\}(.*?)\{\{\s*ImageNoteEnd[^{}]*\}\}", re.S | re.I)


def note_text(raw):
    """A note's words without wiki markup: [[a|b]] -> b, {{...}} and HTML left out."""
    raw = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", raw)
    raw = re.sub(r"\[https?://\S+\s*([^\]]*)\]", r"\1", raw)
    raw = re.sub(r"\{\{[^{}]*\}\}", " ", raw)
    return clean(raw).strip(" .;:")


def image_notes(s, title):
    """[(label, where in the picture)] from the image notes on a Commons file's page: each note's box (x, y, w, h on
    a picture dimx by dimy) and its words. Notes of more than eight words are descriptions, not labels, and are
    left out."""
    data = commons_get(s, {"action": "query", "titles": title, "prop": "revisions", "rvprop": "content",
                           "rvslots": "main"})
    page = next(iter(((data.get("query") or {}).get("pages") or {}).values()), {})
    text = (((page.get("revisions") or [{}])[0].get("slots") or {}).get("main") or {}).get("*", "")
    out = []
    for params, words in NOTE.findall(text):
        values = dict(re.findall(r"(\w+)\s*=\s*([\d.]+)", params))
        label = note_text(words)
        try:
            x, y, w, h = (float(values[k]) for k in ("x", "y", "w", "h"))
            dimx, dimy = float(values["dimx"]), float(values["dimy"])
        except (KeyError, ValueError):
            continue
        if not label or len(label.split()) > 8 or dimx <= 0 or dimy <= 0:
            continue
        out.append((label, spot((x + w / 2) / dimx, (y + h / 2) / dimy)))
    return out


def noted_rows(notes, credit, place):
    """The rows for a photo's image notes: all of them in one answer, and one "Where is ...?" per note."""
    said = [f"{the_name(label)} is {where_in}" for label, where_in in notes]
    rows = [{"question": "What parts are labelled in this picture, and where are they?",
             "answer": capital("; ".join(said)) + ".", "credit": credit, **place}]
    for (label, where_in), sentence in zip(notes, said):
        rows.append({"question": f"Where is {the_name(label)} in this picture?", "answer": capital(sentence) + ".",
                     "credit": credit, **place})
    return rows


def build_commons_engine_bays(limit):
    """Engine bays (found by their file titles, as Commons has no category for them), with their image notes where a
    Commons user named parts on the photo, and dashboards and their gauges (build_commons_parts). About two thirds
    of the limit are engine bays."""
    s = session()
    bays = int(limit * 0.65) + 1
    noted = []
    for query in NOTED_BAYS:
        noted += [t for t in search_files(s, query, 200) if SHOWS_AN_ENGINE.search(t) and t not in noted
                  and not NOT_A_ROAD_VEHICLE.search(t) and not NOT_A_CAR_ENGINE.search(t)]
    titles = list(noted)
    for query in ENGINE_BAY_SEARCHES:
        titles += search_files(s, query)
    titles = [t for t in dict.fromkeys(titles) if not NOT_A_PHOTO.search(t) and not NOT_A_ROAD_VEHICLE.search(t)]
    rest = [t for t in titles if t not in set(noted)]
    pass_random(51).shuffle(rest)
    titles = [t for t in titles if t in set(noted)] + rest
    say(f"Commons engine bays: {len(titles)} files ({len(noted)} with image notes)")
    items = []
    for title, url, credit, text, _ in mech_entries(s, titles[:int(bays * 1.3) + 10]):
        if len(items) >= bays * 1.15:
            break
        words = NOT_A_CHILD.sub(" ", f"{title} {text}")
        text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
        place = where(PLACES.get(title, ""))
        facts = {"commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0]}
        rows = [mark_child({"question": ENGINE_BAY_Q, "answer": ENGINE_BAY, "credit": credit, "facts": facts,
                            **place}, words)]
        if title in noted:
            notes = image_notes(s, title)
            rows += [mark_child(r, words) for r in noted_rows(notes, credit, place)] if notes else []
            time.sleep(1)
        if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
            rows.append(mark_child({"question": ALT_TEXT, "answer": text, "credit": credit, **place}, words))
        items.append((file_name("enginebay", title), url, rows))
    out = with_twins(commons_fetch(items)[:bays])
    out += build_commons_parts(DASHBOARDS, max(1, limit - count_pictures(out)), "dashboard")
    return out


# ----------------------------------------------------------------- iso_machine_symbols

SYMBOL_Q = "What does this symbol mean?"
WARNING_Q = "What does this dashboard warning light mean?"
# The standard meanings of the main dashboard warning lights (tell-tales), as vehicle makers' handbooks give them,
# found by the words of the symbol's title or description. Checked in this order.
WARNING_LIGHTS = [
    (r"oil pressure|pression d'huile", "This is the oil pressure warning light: stop the engine as soon as it is "
                                       "safe and check the oil."),
    (r"(engine )?coolant temperature|température d'eau|engine overheat",
     "This is the engine temperature warning light: the engine is too hot; stop as soon as it is safe and let it "
     "cool."),
    (r"battery charg|charging (condition|system)|charge batterie",
     "This is the battery (charging) warning light: the battery is not being charged; have it checked soon."),
    (r"anti-?lock|\babs\b", "This is the ABS warning light: the anti-lock brakes have a fault; the normal brakes "
                            "still work, but have it checked."),
    (r"brake (failure|system)|défaillance des freins|braking system",
     "This is the brake warning light: the brake fluid may be low or the brakes have a fault; have them checked "
     "before driving on."),
    (r"parking brake|handbrake|frein de parking", "This is the parking brake light: the parking brake (handbrake) "
                                                  "is on."),
    (r"engine malfunction|check engine|malfunction indicator|dépollution", "This is the check-engine light: the "
     "engine's control system has found a fault; have it checked soon."),
    (r"tyre pressure|tire pressure", "This is the tyre pressure warning light: a tyre's pressure is low; check the "
                                     "tyres."),
    (r"air ?bag", "This is the airbag warning light: the airbag system has a fault; have it checked."),
    (r"seat ?belt", "This is the seat-belt reminder: a seat belt is not fastened."),
    (r"fuel level|low fuel|niveau mini de carburant|fuel reserve", "This is the low fuel warning light: the tank is "
                                                                   "nearly empty."),
    (r"glow plug|pre-?heat|préchauffage", "This is the diesel glow-plug light: wait for it to go out before "
                                          "starting the engine."),
]
# The ways the ISO 7000 files' descriptions are written on Commons: "... Title/Meaning: X Function/description:
# Y", "ISO 7000 - Ref-No 0001 X; Y" and "Symbol 0016 from ISO 7000 - X To indicate Y".
ISO_WORDINGS = (re.compile(r"Title/Meaning:\s*(?P<name>.+?)\s*(?:Function/description:\s*(?P<use>.+))?$", re.S),
                re.compile(r"^ISO 7000 - Ref-No \S+\s+(?P<name>.+?);\s*(?P<use>To\b.+)$", re.S),
                re.compile(r"^ISO 7000 - Ref-No \S+\s+(?P<name>[^;]+);\s*(?P<use>.+)$", re.S),
                re.compile(r"from ISO 7000 - (?P<name>.+?)\s+(?P<use>To (?:indicate|identify|show|mark)\b.+)$", re.S))
ISO_NUMBER = re.compile(r"ISO 7000 - (?:Ref-No )?(\d{4}[A-Z]?)")


def iso_meaning(title, description):
    """(ISO 7000 number, the symbol's title, its use) from a file's name and description, or None.
    "Symbol 0011 from ISO 7000 - Title/Meaning: Electric motor, general Function/description: To indicate an
    electric motor." -> ("0011", "Electric motor, general", "To indicate an electric motor.")."""
    number = ISO_NUMBER.search(title)
    text = clean(re.sub(r"<br\s*/?>|</?p>", " ", description or ""))
    m = next((m for m in (w.search(text) for w in ISO_WORDINGS) if m), None)
    if not number or not m:
        return None
    name = clean(m.group("name")).strip(" ;.")
    if ";" in name:                       # "Engaging; mechanical activation" -> "Engaging (mechanical activation)"
        first, _, others = name.partition(";")
        name = f"{first.strip()} ({others.strip()})"
    use = clean(m.group("use") or "")
    if not name or len(name.split()) > 15:
        return None
    use = use.split(" Note")[0].strip()
    if use and not use.endswith("."):
        use += "."
    return number.group(1), name, capital(use) if use else ""


def warning_advice(words):
    """The standard warning-light sentence for a symbol whose words match WARNING_LIGHTS, or ""."""
    if re.search(r"\btrailer\b", words, re.I):        # a trailer's own light: its description says it
        return ""
    for pattern, sentence in WARNING_LIGHTS:
        if re.search(pattern, words, re.I):
            return sentence
    return ""


def symbol_entry(s, url):
    """A symbol drawing (Commons' PNG of it) as a black-on-white JPEG, or None."""
    got = commons_fetch([("symbol", url, None)], workers=1, raw=True)
    if not got:
        return None
    try:
        picture = symbol_picture(got[0][1], side=320)
    except Exception:  # noqa: BLE001 - a drawing that cannot be read is left out
        return None
    out = io.BytesIO()
    picture.save(out, "JPEG", quality=92)
    return out.getvalue()


def build_iso_machine_symbols(limit):
    """ISO 7000 symbols (each with the title and use from its file's description, which repeats the standard) and the
    free files of the dashboard-icon and warning-light categories (photos and drawings, with their own
    descriptions). Symbols whose words name a main warning light get "What does this dashboard warning light
    mean?" with its standard meaning too."""
    s, out = session(), []
    titles = [t for t in commons_members(s, "ISO 7000 symbols", "file") if t.lower().endswith((".svg", ".png"))]
    pass_random(70).shuffle(titles)
    say(f"ISO 7000: {len(titles)} symbol files")
    for title, url, credit, _, description in mech_entries(s, titles[:int(limit * 1.2) + 20], drawings=True):
        if count_pictures(out) >= limit * 0.85:
            break
        meaning = iso_meaning(title, description)
        if not meaning:
            considered(title, url, "its description does not give the symbol's title")
            if not NUDE.search(f"{title} {description}"):
                drawing = symbol_entry(s, url)          # made black on white, as the pack's symbols are
                if drawing:
                    needs_description(file_name("iso7000", title), url, credit, credit_licence(credit),
                                      text=clean(description)[:400], title=title, data=drawing,
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      reason="its description does not give the symbol's title and use",
                                      extra={"iso_7000": (ISO_NUMBER.search(title) or [None, ""])[1],
                                             "kind": "ISO 7000 symbol drawing"})
            continue
        number, name, use = meaning
        picture = symbol_entry(s, url)
        if not picture:
            considered(title, url, "the drawing could not be read")
            continue
        facts = {"iso_7000": number, "symbol_title": name}
        rows = [{"question": SYMBOL_Q, "answer": f"It is the symbol for \"{name}\" (ISO 7000 number {number})."
                 + (f" {use}" if use else ""), "credit": credit, "facts": facts}]
        advice = warning_advice(name)
        if advice:
            rows.append({"question": WARNING_Q, "answer": advice, "credit": credit, "facts": facts})
        out += with_twins([(file_name("iso7000", title), picture, rows)])
        time.sleep(0.3)
    # The free files of the dashboard-icon and warning-light categories (most are BY-SA: the kit's entry).
    dash = []
    for category in ("Dashboard icons", "Dashboard SVG icons", "Warning lights"):
        dash += commons_members(s, category, "file")
    for title, url, credit, text, description in mech_entries(s, list(dict.fromkeys(dash)), drawings=True):
        words = f"{title} {description}"
        if re.search(r"\b(paomedia|web fundamentals|icon set|material design)\b", words, re.I):
            considered(title, url, "a software icon")
            continue
        if not in_english(text):
            considered(title, url, "no English description of what it means")
            if not NUDE.search(words):              # a dashboard light or icon without an English description
                drawing = symbol_entry(s, url) if title.lower().endswith(".svg") else None
                needs_description(file_name("dashicon", title), url, credit, credit_licence(credit),
                                  text=clean(description)[:400], title=title, data=drawing,
                                  page_url=credit.rsplit(", ", 1)[-1],
                                  reason="no English description of what it means",
                                  extra={"kind": "dashboard icon or warning light"})
            continue
        picture = symbol_entry(s, url) if title.lower().endswith(".svg") else None
        rows = [{"question": ALT_TEXT, "answer": text, "credit": credit}]
        advice = warning_advice(words)
        if advice:
            rows.insert(0, {"question": WARNING_Q, "answer": advice, "credit": credit})
        if picture:
            out += with_twins([(file_name("dashicon", title), picture, rows)])
        else:
            out += with_twins(commons_fetch([(file_name("dashicon", title), url, rows)]))
    return trim(out, limit)


def trim(entries, limit):
    """The first limit pictures of entries, with their twin rows."""
    pictures = [e for e in entries if e[1] is not None][:limit]
    keep = {e[0] for e in pictures}
    return pictures + [e for e in entries if e[1] is None and e[2]["file"].split("/", 1)[-1] in keep]


# ----------------------------------------------------------------- Hugging Face helpers

def hf_files(repo, folder, revision="main"):
    """The file paths under a folder of a Hugging Face dataset repository (its tree listing, page by page)."""
    s, paths = session(), []
    url = f"https://huggingface.co/api/datasets/{repo}/tree/{revision}/{folder}?recursive=true"
    while url:
        r = s.get(url, timeout=120)
        r.raise_for_status()
        paths += [x["path"] for x in r.json() if x.get("type") == "file"]
        url = r.links.get("next", {}).get("url")
    return paths


def hf_url(repo, path, revision="main"):
    """The download address of one file of a Hugging Face dataset."""
    from urllib.parse import quote
    return f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{quote(path)}"


def even_share(groups, limit, seed):
    """An even share of each group's items (lists), taking from the larger groups when a small one runs out."""
    rng, picked = pass_random(seed), []
    pools = {k: rng.sample(v, len(v)) for k, v in groups.items()}
    while len(picked) < limit and any(pools.values()):
        for k in sorted(pools):
            if pools[k] and len(picked) < limit:
                picked.append(pools[k].pop())
    return picked


# ----------------------------------------------------------------- corolla_engine_bay

COROLLA = "stevenalbert10/Toyota-Corolla-Car-Parts"
COROLLA_PARTS = {"Air Filter": "the air filter box", "Battery": "the battery",
                 "Coolant Reservoir": "the coolant reservoir (the engine coolant's expansion tank)",
                 "New Coolant Reservoir": "the coolant reservoir (the engine coolant's expansion tank)",
                 "Engine": "the engine", "Engine Cover": "the engine cover",
                 "Reservoir Cap": "the cap of the coolant reservoir",
                 "Windshield Fluid": "the windscreen washer fluid tank"}
COROLLA_PURPOSE = {"Air Filter": "it holds the filter that cleans the air going into the engine.",
                   "Battery": "it powers the starter motor and the car's electrics.",
                   "Coolant Reservoir": "it shows the coolant level; it must not be opened while the engine is hot.",
                   "New Coolant Reservoir": "it shows the coolant level; it must not be opened while the engine is "
                                            "hot.",
                   "Reservoir Cap": "it must not be opened while the engine is hot.",
                   "Windshield Fluid": "it holds the water and screen wash for the windscreen washers."}
COROLLA_CREDIT = ("ARabeitak Car Parts Object Detection Dataset (Judy Wagdy, Laila Hany, Rana Raafat and Steven "
                  "Albert, 2023), Apache-2.0, https://huggingface.co/datasets/stevenalbert10/Toyota-Corolla-Car-Parts")


def build_corolla_engine_bay(limit):
    """Photos of a 2015 Toyota Corolla's engine bay, each in the folder of the part it shows; an even share of each
    part. "What part is this?" -> "This is the battery, in the engine bay of a Toyota Corolla: it powers ..." """
    groups = collections.defaultdict(list)
    for path in hf_files(COROLLA, ""):
        folder = path.split("/")[0]
        if folder in COROLLA_PARTS and path.lower().endswith((".jpg", ".jpeg", ".png")):
            groups[folder].append(path)
    items = []
    for path in even_share(groups, int(limit * 1.05) + 2, 81):
        folder = path.split("/")[0]
        name, purpose = COROLLA_PARTS[folder], COROLLA_PURPOSE.get(folder)
        answer = f"This is {name}, in the engine bay of a Toyota Corolla" + (f": {purpose}" if purpose else ".")
        items.append((f"corolla-{safe_name(path)}.jpg", hf_url(COROLLA, path),
                      [{"question": PART_Q, "answer": answer, "credit": COROLLA_CREDIT,
                        "facts": {"vehicle": "Toyota Corolla, 2015 model", "part_folder": folder}},
                       {"question": "Is this under the bonnet of a car?", "answer": "Yes: this is the engine bay of "
                        "a car (a 2015 Toyota Corolla).", "credit": COROLLA_CREDIT}]))
    return with_twins(fetch_all(items, workers=6)[:limit])


# ----------------------------------------------------------------- tyre_condition

TYRE_Q = "Is this tyre in good condition?"
TYRE_GOOD = "Yes: this tyre was marked as being in good condition."
TYRE_BAD = "No: this tyre was marked as defective (damaged or worn); have it checked."
TYRE_DISTANCE_Q = "How far has this tyre been driven?"
VELAMMAL = "bn7ch8tvyp"
TYRENET = "32b5vfj6tc"
MEERUT = "dfzbm2ktss"
VELAMMAL_CREDIT = ("Digital images of defective and good condition tyres (Pathmanaban P, Abishek C, Kousik Muthayala "
                   "Sai, Karthick S and Aakash S, Velammal Engineering College, 2023), Mendeley Data, "
                   "doi:10.17632/bn7ch8tvyp.1, CC BY 4.0")
TYRENET_CREDIT = ("TyreNet: A High-quality Annotated Dataset for Tyre Defect Classification (Vamsi Sravanth "
                  "Mahendrada and Murali Parameswaran, Presidency University, 2024), Mendeley Data, "
                  "doi:10.17632/32b5vfj6tc.1, CC BY 4.0")
MEERUT_CREDIT = ("Annotated Tyre Image Dataset for Machine Learning-Based Life Prediction (Vishal Jain, Vaishnavi "
                 "Chaudhary, Aryan Panwar, Raziya Khan and Mohini Singh, Meerut Institute of Engineering and "
                 "Technology, 2025), Mendeley Data, doi:10.17632/dfzbm2ktss.2, CC BY 4.0")


def mendeley_files(dataset, version):
    """The files of a Mendeley Data dataset's latest version: [(file name, download address, size)]. version is the
    version this pack was made for (the record asked for with ?version= lists no files, so the latest is read; a
    newer version is said in the log)."""
    data = session().get(f"https://data.mendeley.com/public-api/datasets/{dataset}", timeout=120).json()
    if str(data.get("version")) != str(version):
        say(f"  Mendeley {dataset}: version {data.get('version')} (this pack was made for version {version})")
    return [(f["filename"], f["content_details"]["download_url"], f.get("size", 0)) for f in data.get("files", [])]


def km_words(km):
    """ "about 4,250 km (2,640 miles)" """
    return f"about {km:,} km ({round(km * 0.621371 / 10) * 10:,} miles)"


def tyrenet_photos(want):
    """[(file name, JPEG, good or not)] from TyreNet's 1.9 GB RAR archive, opened with bsdtar or 7-Zip (Python cannot
    read RAR itself); [] when neither is installed or the archive cannot be read. Its folders name the class
    ("defective" or "good"); an even share of each."""
    import shutil
    import subprocess
    import tempfile
    files = [f for f in mendeley_files(TYRENET, 1) if f[0].lower().endswith(".rar")]
    tool = shutil.which("bsdtar") or shutil.which("7z")
    if not files or not tool:
        say("  TyreNet: no RAR file listed, or neither bsdtar nor 7z is installed; left out")
        return []
    with tempfile.TemporaryDirectory() as folder:
        archive = os.path.join(folder, "tyrenet.rar")
        with session().get(files[0][1], timeout=3600, stream=True) as r:
            r.raise_for_status()
            with open(archive, "wb") as f:
                for chunk in r.iter_content(1 << 22):
                    f.write(chunk)
        command = [tool, "-xf", archive, "-C", folder] if "bsdtar" in tool else [tool, "x", "-y", f"-o{folder}",
                                                                                   archive]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except Exception as e:  # noqa: BLE001 - the archive could not be read: left out
            say(f"  TyreNet could not be unpacked ({str(e)[:100]}); left out")
            return []
        os.remove(archive)
        groups = collections.defaultdict(list)
        for root, _, names in os.walk(folder):
            kind = "good" if re.search(r"\bgood\b", root, re.I) else "defective" if re.search(r"defect", root, re.I) \
                else ""
            for name in names:
                if kind and name.lower().endswith((".jpg", ".jpeg", ".png")):
                    groups[kind].append(os.path.join(root, name))
        out = []
        for path in even_share(groups, want, 93):
            with open(path, "rb") as f:
                picture = smaller(f.read())
            good = bool(re.search(r"\bgood\b", os.path.relpath(os.path.dirname(path), folder), re.I))
            if picture:
                out.append((safe_name(os.path.relpath(path, folder))[-80:], picture, good))
            else:
                considered(os.path.basename(path), files[0][1], "the picture could not be read")
        return out


def build_tyre_condition(limit):
    """Tyres marked good or defective (Velammal, TyreNet) and tyres filed under the distance they had been driven
    (Meerut): an even share of the three where each has enough."""
    from everyday_packs import RemoteZip
    third = max(1, limit // 3)
    out = []
    # Meerut: one zip, a folder per distance ("4250 Km"), read by HTTP ranges.
    zipped = mendeley_files(MEERUT, 2)
    if zipped:
        z = RemoteZip(zipped[0][1])
        items = []
        for name, offset, size, method in z.entries():
            m = re.search(r"/(\d+)\s*km/[^/]+\.(jpe?g|png)$", name, re.I)
            if m:
                items.append((name, (offset, size, method), int(m.group(1))))
        pass_random(91).shuffle(items)
        from everyday_packs import fetch_from_zip
        wanted = []
        for name, where_in, km in items[:third]:
            facts = {"distance_km": km}
            wanted.append((f"tyre-meerut-{safe_name(name)[-60:]}.jpg", where_in,
                           [{"question": TYRE_DISTANCE_Q, "answer": f"This tyre had been driven {km_words(km)} when "
                             "it was photographed.", "credit": MEERUT_CREDIT, "facts": facts,
                             **where("Meerut, India")},
                            {"question": THING_Q, "answer": "This is a vehicle tyre.", "credit": MEERUT_CREDIT,
                             **where("Meerut, India")}]))
        out += with_twins(fetch_from_zip(z, wanted, workers=4))
    # TyreNet: good or defective, from its RAR archive.
    for name, picture, good in tyrenet_photos(third):
        out += with_twins([(f"tyre-tyrenet-{name}.jpg", picture,
                            [{"question": TYRE_Q, "answer": TYRE_GOOD if good else TYRE_BAD, "credit": TYRENET_CREDIT,
                              "facts": {"label": "good" if good else "defective"}}])])
    # Velammal: good or defective, one file each; fills the rest of the limit.
    groups = collections.defaultdict(list)
    for name, url, _ in mendeley_files(VELAMMAL, 1):
        kind = name.split(" ")[0].lower()
        if kind in ("good", "defective") and name.lower().endswith((".jpg", ".jpeg", ".png")):
            groups[kind].append((name, url))
    rest = max(0, limit - count_pictures(out))
    items = [(f"tyre-velammal-{safe_name(name)}.jpg", url,
              [{"question": TYRE_Q, "answer": TYRE_GOOD if name.lower().startswith("good") else TYRE_BAD,
                "credit": VELAMMAL_CREDIT, "facts": {"label": name.split(" ")[0].lower()}}])
             for name, url in even_share(groups, rest, 92)]
    out += with_twins(fetch_all(items, workers=6))
    pass_random(94).shuffle(out)
    return trim(out, limit)


# ----------------------------------------------------------------- spark_plug_condition

SPARK = "eoinedge/spark-plug-classification"
SPARK_Q = "What condition is this spark plug in?"
SPARK_ANSWERS = {"normal": "It looks normal: clean, with no fouling or damage.",
                 "carbon_fouled": "It is carbon-fouled: covered in dry black soot.",
                 "oil_fouled": "It is oil-fouled: covered in wet, oily deposits.",
                 "mechanical_damage": "It is mechanically damaged."}
SPARK_CREDIT = ("Spark Plug Condition Classification (eoinedge, made for an Edge Impulse demonstration), "
                "BSD-3-Clause, https://huggingface.co/datasets/eoinedge/spark-plug-classification")


def build_spark_plug_condition(limit):
    """Spark plugs in four conditions (the dataset's folders), an even share of each."""
    groups = collections.defaultdict(list)
    for path in hf_files(SPARK, "data"):
        kind = path.split("/")[-2]
        if kind in SPARK_ANSWERS and path.lower().endswith((".jpg", ".jpeg", ".png")):
            groups[kind].append(path)
    items = []
    for path in even_share(groups, int(limit * 1.05) + 2, 61):
        kind = path.split("/")[-2]
        items.append((f"sparkplug-{kind}-{safe_name(path.rsplit('/', 1)[-1])}.jpg",
                      hf_url(SPARK, path),
                      [{"question": SPARK_Q, "answer": SPARK_ANSWERS[kind], "credit": SPARK_CREDIT,
                        "facts": {"label": kind}},
                       {"question": PART_Q, "answer": answer_for("a spark plug", COMMONS_CAR_PARTS[0][4]),
                        "credit": SPARK_CREDIT}]))
    return with_twins(fetch_all(items, workers=6)[:limit])


# ----------------------------------------------------------------- planetary_gearbox

PLANETARY_ZIP = "https://zenodo.org/records/8223473/files/PlanetaryGearDataset.zip?download=1"
PLANETARY_NAMES = {"Planetary_Gear": ("planet gear", "planet gears"), "Sun_Gear": ("sun gear", "sun gears"),
                   "Housing": ("gearbox housing", "gearbox housings"), "Top": ("gearbox top cover", "top covers"),
                   "Stepper_motor": ("stepper motor", "stepper motors"),
                   "Driver": ("motor driver board", "motor driver boards")}
PLANETARY_CREDIT = ("Planetary Gear Dataset (Gaurang Sharma and Roel Pieters, Tampere University, 2023), Zenodo "
                    "8223473, CC BY 4.0, https://doi.org/10.5281/zenodo.8223473")
NUMBER_WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def places_words(places):
    """Several places in one phrase: ["at the top left of the picture", "in the centre of the picture"] -> "at the
    top left and in the centre of the picture"; more than three -> "in several places in the picture"."""
    if len(places) == 1:
        return places[0]
    if len(places) > 3:
        return "in several places in the picture"
    short = [p.replace(" of the picture", "") for p in places]
    return ", ".join(short[:-1]) + " and " + short[-1] + " of the picture"


def build_planetary_gearbox(limit):
    """The real photos of the Planetary Gear Dataset with their boxed parts: "What parts are in this picture, and
    where?" -> "One sun gear, in the centre of the picture; three planet gears ..." (places from the boxes'
    centres), and "What is this?" -> a planetary gearbox."""
    from everyday_packs import RemoteZip, fetch_from_zip
    z = RemoteZip(PLANETARY_ZIP)
    entries = {name: (offset, size, method) for name, offset, size, method in z.entries()}
    coco = json.loads(z.read(*entries["PlanetaryGearDataset/Dataset/COCO/CocoJSON/CocoJSON.json"]))
    names = {c["id"]: c["name"] for c in coco["categories"]}
    boxes = collections.defaultdict(list)
    for a in coco["annotations"]:
        boxes[a["image_id"]].append((names.get(a["category_id"]), a["bbox"]))
    items = []
    for image in coco["images"]:
        path = "PlanetaryGearDataset/Dataset/COCO/Images/" + image["file_name"]
        if path not in entries or not boxes[image["id"]]:
            continue
        kinds = collections.defaultdict(list)
        for kind, (x, y, w, h) in boxes[image["id"]]:
            if kind in PLANETARY_NAMES:
                kinds[kind].append(spot((x + w / 2) / image["width"], (y + h / 2) / image["height"]))
        said = []
        for kind in ("Housing", "Top", "Sun_Gear", "Planetary_Gear", "Stepper_motor", "Driver"):
            if kind in kinds:
                n, (one, many) = len(kinds[kind]), PLANETARY_NAMES[kind]
                places = list(dict.fromkeys(kinds[kind]))
                count = NUMBER_WORDS[n] if n < len(NUMBER_WORDS) else str(n)
                said.append(f"{count} {one if n == 1 else many}, " + places_words(places))
        if not said:
            continue
        items.append((f"planetary-{image['file_name'].rsplit('.', 1)[0]}.jpg", entries[path],
                      [{"question": "What parts are in this picture, and where?",
                        "answer": capital("; ".join(said)) + ".", "credit": PLANETARY_CREDIT},
                       {"question": THING_Q, "answer": "These are parts of a small planetary gearbox, in which planet "
                        "gears turn around a central sun gear.", "credit": PLANETARY_CREDIT}]))
    pass_random(41).shuffle(items)
    return with_twins(fetch_from_zip(z, items[:limit], workers=4))


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what} categories: captions CC0; pictures CC0, public domain, CC BY, MIT or "
                  "Apache, each with its author and file page below. https://commons.wikimedia.org")
MECHANICAL_PACKS = {
    "commons_car_parts": (build_commons_car_parts, COMMONS_CREDIT.format(what="car and lorry part")),
    "commons_cycle_parts": (build_commons_cycle_parts, COMMONS_CREDIT.format(what="bicycle, motorcycle and "
                                                                                  "small-engine part")),
    "commons_machine_parts": (build_commons_machine_parts, COMMONS_CREDIT.format(what="machine, plumbing and "
                                                                                      "heating part")),
    "commons_engine_bays": (build_commons_engine_bays,
                            "Wikimedia Commons engine-bay photos (found by their file titles) and dashboard and "
                            "gauge categories: captions CC0; pictures CC0, public domain, CC BY, MIT or Apache, each "
                            "with its author and file page below; part places from the image notes Commons users "
                            "drew on the photos. https://commons.wikimedia.org"),
    "iso_machine_symbols": (build_iso_machine_symbols,
                            "Wikimedia Commons: the ISO 7000 symbol files (Category:ISO 7000 symbols; CC0, or public "
                            "domain as simple shapes) with the title and use given in each file's description, and "
                            "the free files of Category:Dashboard icons, Dashboard SVG icons and Warning lights, each "
                            "with its author and file page below. Drawings set black on white. Warning-light meanings "
                            "are the standard ones vehicle handbooks give."),
    "corolla_engine_bay": (build_corolla_engine_bay, COROLLA_CREDIT + ". Changes: photos made smaller."),
    "tyre_condition": (build_tyre_condition, "; ".join((VELAMMAL_CREDIT, TYRENET_CREDIT, MEERUT_CREDIT))
                       + ". Changes: photos made smaller; answers from each collection's folders."),
    "spark_plug_condition": (build_spark_plug_condition, SPARK_CREDIT + ". Changes: answers from its folders."),
    "planetary_gearbox": (build_planetary_gearbox, PLANETARY_CREDIT + ". Changes: photos made smaller; answers from "
                                                                      "its boxes."),
}

# How many pictures a full build takes from each (about what each offers after the checks, kept so that every pack
# finishes well within about four hours on GitHub's machines; Commons answers about one picture a second).
MECHANICAL_LIMITS = {
    "commons_car_parts": 3500,       # 74 categories (with subcategories where marked), about 47 photos each
    "commons_cycle_parts": 2500,     # 60 categories
    "commons_machine_parts": 3500,   # 73 categories
    "commons_engine_bays": 1500,     # 464 engine-bay files by title (6 with notes), 8 dashboard and gauge categories
    "iso_machine_symbols": 2300,     # the 2,260 ISO 7000 files and the few free dashboard icons
    "corolla_engine_bay": 1452,      # all of them (about 3 MB each)
    "tyre_condition": 4100,          # 620 Meerut, up to 1,698 TyreNet (1.9 GB RAR), 1,856 Velammal (2.9 GB)
    "spark_plug_condition": 697,     # all of them
    "planetary_gearbox": 150,        # all the real photos
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one mechanical pack builder.")
    parser.add_argument("key", choices=sorted(MECHANICAL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = MECHANICAL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"places: " + ", ".join(f"{p} {n}" for p, n in places.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
