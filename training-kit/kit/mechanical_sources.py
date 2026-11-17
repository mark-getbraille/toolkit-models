"""Mechanical and automotive picture collections for the Picture Model Training Kit (car, motorcycle, bicycle and
small-engine parts, machine, plumbing and heating parts, dashboards and warning lights, car body parts and damage,
factory parts inspection) that cannot be ready-made packs because of their licence: share-alike, non-commercial, or
research use (pictures gathered from the web, or no terms stated). The open ones (Commons CC0, public domain and
CC BY car, cycle and machine parts, engine bays and dashboards, the ISO 7000 symbols, the Toyota Corolla engine bay,
three tyre-condition collections, spark-plug condition and a planetary gearbox) are packs in
packs/mechanical_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it (or, where that cannot be read by a program, the copy
named), only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with them
                   is CC BY-SA.
  "noncommercial"  CC BY-NC-SA and other non-commercial terms: personal use only (--personal-noncommercial).
  "research"       pictures gathered from the web, or no terms for the pictures: personal use only
                   (--personal-research with --accept-research-terms).

Answers are fixed sentences from each source's own labels (a Commons category's name, a symbol file's own
description, a dataset's class, box or folder names), never written by an AI model. Positions are said only from a
dataset's own boxes or outlines, as places in the picture (left, right, top, bottom, centre); "front left door" and
the like are the dataset's own names for the car's parts. The standard meanings of the main dashboard warning lights
are those vehicle handbooks give; no repair instructions are given.

The collections (MECHANICAL_SOURCES):
  share-alike
    commons_mechanical_sa     Wikimedia Commons categories of car, motorcycle, bicycle, small-engine, machine,
                              plumbing and heating parts, engine bays and dashboards (the same categories as the open
                              packs): files under CC BY-SA or GFDL, with the category's question and the file's own
                              caption. "What part is this?" -> "This is a brake caliper."
    dashboard_symbols_sa      Commons' dashboard warning and indicator symbols (Category:Dashboard SVG icons, about 380
                              drawings, and Dashboard icons and Warning lights) under CC BY-SA, each with the meaning
                              its file's description gives ("Indication symbol for high (main) beam.") and the standard
                              advice for the main warning lights. Drawn black on white.
  noncommercial
    autovi                    AutoVI, the Automotive Visual Inspection Dataset (Renault Group and the Université de
                              technologie de Compiègne, Zenodo 10459003, CC BY-NC-SA 4.0): photos from Renault's car
                              production lines of engine wiring, pipe clips and staples, fuel-tank and underbody screws
                              and underbody pipes, good or with a fault (missing, unclipped, not fastened, something in
                              the way). "Is anything wrong with this part?" Photos with an operator in them are left
                              out.
  research
    dashboard_warning_icons   Car Dashboard Warning Icons (a Roboflow Universe set by "elmello", marked CC BY 4.0;
                              copy HANTIFARAH/car-dashboard-warning-icons on Hugging Face): 5,306 pictures of
                              dashboards with 16 kinds of warning light boxed (ABS, check engine, overheating, low oil,
                              low fuel, low tyre pressure, airbag, seat belt, battery charging ...). Many file names
                              are Shutterstock stock numbers, so the pictures were gathered from the web: personal use
                              only. "What does this dashboard warning light mean?"
    car_parts_damage          Car Parts and Car Damages (Humans in the Loop and Beetroot Academy, 2023; annotations
                              CC0; copy DrBimmer/car-parts-and-damage-dataset on Hugging Face, marked MIT): 998 car
                              photos with 21 body parts outlined (doors, bumpers, wheels, lights, bonnet, boot,
                              mirrors ...) and 814 with damage outlined (dent, scratch, crack, broken or missing part,
                              paint chip, corrosion). Who took the photos is not stated. "Which parts of the car can
                              you see, and where?" / "What damage can you see on this car?"
    car_parts_dsmlr           Car Parts Segmentation (DSMLR, github.com/dsmlr/Car-Parts-Segmentation): 500 photos of
                              saloons, pick-ups and SUVs with 18 parts outlined; no licence is stated.
    car_damage_views          Car Front and Rear Damage Detection (DrBimmer on Hugging Face, marked MIT; where the
                              photos came from is not stated): cars from the front or back, undamaged, crushed or with
                              broken parts. "Is this car damaged?"
    mechanical_parts_2022     Mechanical Parts Dataset 2022 (Mübarek Mazhar Çakır, Zenodo 7504801, marked CC BY 4.0;
                              its description says the 2,250 pictures were downloaded "from various internet
                              platforms"): bearings, bolts, gears and nuts, boxed. "What mechanical parts are in this
                              picture?" -> "Three bolts and two nuts." A RAR archive, opened with the tar program built
                              into Windows 10 and 11.

Needing sign-up (cannot be downloaded automatically; MECHANICAL_SIGN_UP has the links), and looked at and not
included (MECHANICAL_NOT_INCLUDED, with the reason of each).

MECHANICAL_PICTURE_MAKING_OK holds the collections of parts and symbols without people: dashboard_symbols_sa,
dashboard_warning_icons, mechanical_parts_2022 and autovi (whose operator photos are left out). Not the Commons entry
(its workshop photos show people) nor the car photos (people may stand near the cars).

    python kit/mechanical_sources.py autovi --cap 8     (a quick check; prints a few rows)
"""

import collections
import io
import json
import os
import random
import re
import time

import sources
from big_sources import even_pick
from extra_sources import (COMMONS_SA, commons_get, commons_members, commons_session, commons_text, research, save,
                           say)
from home_sources import commons_sa_items
from more_sources import download_to, fetch_shared
from personal_sources import remote_zip, zip_members
from sources import Source, clean

ALT_TEXT = sources.ALT_TEXT
PART_Q = "What part is this?"
THING_Q = "What is this?"
WARNING_Q = "What does this dashboard warning light mean?"
SYMBOL_Q = "What does this symbol mean?"


def spot(cx, cy):
    """Where a point (fractions of the picture's width and height) is, in plain words: "at the top left of the
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


def capital(text):
    """The text with its first letter in capitals."""
    return text[:1].upper() + text[1:]


def hf_tree(repo, folder="", revision="main"):
    """The file paths under a folder of a Hugging Face dataset repository (its tree listing, page by page)."""
    import requests
    s, paths = requests.Session(), []
    s.headers["User-Agent"] = sources.USER_AGENT
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


def safe_name(path):
    """A path as a plain file name without its extension."""
    return re.sub(r"[^\w-]+", "_", path.rsplit(".", 1)[0]).strip("_")


# The standard meanings of the main dashboard warning lights, found by the words of a symbol's description (the same
# table as packs/mechanical_packs.py). Checked in this order.
WARNING_LIGHTS = [
    (r"oil pressure|pression d'huile|low engine oil", "This is the oil pressure warning light: stop the engine as "
                                                      "soon as it is safe and check the oil."),
    (r"coolant temperature|température d'eau|overheat", "This is the engine temperature warning light: the engine "
     "is too hot; stop as soon as it is safe and let it cool."),
    (r"battery charg|charging (condition|system)|charge batterie",
     "This is the battery (charging) warning light: the battery is not being charged; have it checked soon."),
    (r"anti-?lock|\babs\b", "This is the ABS warning light: the anti-lock brakes have a fault; the normal brakes "
                            "still work, but have it checked."),
    (r"brake (failure|system)|défaillance des freins|braking system", "This is the brake warning light: the brake "
     "fluid may be low or the brakes have a fault; have them checked before driving on."),
    (r"parking brake|handbrake|frein de parking", "This is the parking brake light: the parking brake (handbrake) "
                                                  "is on."),
    (r"engine malfunction|check engine|malfunction indicator|dépollution", "This is the check-engine light: the "
     "engine's control system has found a fault; have it checked soon."),
    (r"tyre pressure|tire pressure", "This is the tyre pressure warning light: a tyre's pressure is low; check the "
                                     "tyres."),
    (r"air ?bag|\bsrs\b", "This is the airbag warning light: the airbag system has a fault; have it checked."),
    (r"seat ?belt", "This is the seat-belt reminder: a seat belt is not fastened."),
    (r"fuel level|low fuel|niveau mini de carburant|fuel reserve", "This is the low fuel warning light: the tank is "
                                                                   "nearly empty."),
    (r"glow plug|pre-?heat|préchauffage", "This is the diesel glow-plug light: wait for it to go out before "
                                          "starting the engine."),
]


def warning_advice(words):
    """The standard warning-light sentence for words that match WARNING_LIGHTS, or ""."""
    if re.search(r"\btrailer\b", words, re.I):        # a trailer's own light: its description says it
        return ""
    for pattern, sentence in WARNING_LIGHTS:
        if re.search(pattern, words, re.I):
            return sentence
    return ""


# ----------------------------------------------------------------- share-alike: Commons parts

def specs(question, names, deeper=()):
    """[(category, question, answer, deeper)] for commons_sa_items, from {category: what it is}."""
    return [(c, question, f"This is {name}.", c in deeper) for c, name in names.items()]


# The categories of packs/mechanical_packs.py's Commons packs, with the plain name of each.
MECH_PARTS = {
    "Spark plugs": "a spark plug", "Glow plugs": "a glow plug", "Ignition coils": "an ignition coil",
    "Ignition distributor parts": "a part of an ignition distributor", "Pistons": "a piston",
    "Connecting rods": "a connecting rod", "Crankshafts": "a crankshaft", "Camshafts": "a camshaft",
    "Cylinder heads": "a cylinder head", "Timing belts": "a timing belt", "Flywheels": "a flywheel",
    "Oil dipsticks": "an engine oil dipstick", "Oil pan": "an engine oil pan (sump)",
    "Oil filters": "an oil filter", "Air filters": "an air filter", "Carburetors": "a carburettor",
    "Fuel injectors": "a fuel injector", "Fuel pumps (engine)": "a fuel pump", "Turbochargers": "a turbocharger",
    "Intake manifolds": "an intake manifold", "Exhaust manifolds": "an exhaust manifold",
    "Catalytic converters": "a catalytic converter", "Exhaust silencers": "an exhaust silencer (muffler)",
    "Exhaust systems": "a vehicle's exhaust", "Lambda sensors": "a lambda (oxygen) sensor",
    "Radiators (engine cooling)": "an engine radiator", "Radiator caps": "a radiator cap",
    "Automobile thermostats": "an engine thermostat", "Automobile batteries": "a car battery",
    "Alternators": "an alternator", "Electric starter motors": "a starter motor", "Automobile fuses": "car fuses",
    "Jumper cables (vehicle jump start)": "a set of jump leads", "Automobile clutches": "a car clutch",
    "Clutches": "a clutch", "Automobile transmissions": "a car gearbox (transmission)",
    "Automatic transmissions": "an automatic gearbox", "Torque converters": "a torque converter",
    "Differentials": "a differential", "Driveshafts": "a drive shaft",
    "Constant-velocity joints": "a constant-velocity (CV) joint", "Universal joints": "a universal joint",
    "Brake disks": "a brake disc", "Disk brakes": "a disc brake", "Brake calipers": "a brake caliper",
    "Drum brakes": "a drum brake", "Brake shoes": "brake shoes", "Brake master cylinders": "a brake master cylinder",
    "Shock absorbers": "a shock absorber", "Leaf springs": "a leaf spring", "Wheel hubs": "a wheel hub",
    "Automobile wheels": "a car wheel", "Tires": "a tyre", "Automobile tire treads": "the tread of a car tyre",
    "Flat tires": "a flat tyre", "Hubcaps": "a hubcap", "Lug nuts": "wheel nuts (lug nuts)",
    "Tyre pressure gauges": "a tyre pressure gauge", "Automobile headlamps": "a car headlamp",
    "Bicycle derailleur gears": "a bicycle derailleur", "Bicycle chains": "a bicycle chain",
    "Bicycle cassettes": "a bicycle cassette", "Bicycle cranksets": "a bicycle crankset",
    "Bicycle brakes": "a bicycle brake", "Bicycle rim brakes": "a bicycle rim brake", "Bicycle hubs": "a bicycle hub",
    "Bicycle pedals": "a bicycle pedal", "Bicycle saddles": "a bicycle saddle", "Bicycle spokes": "bicycle spokes",
    "Bicycle tires": "a bicycle tyre", "Bicycle wheel inner tubes": "a bicycle inner tube",
    "Presta valves": "a Presta valve", "Schrader valves": "a Schrader valve", "Bicycle forks": "a bicycle fork",
    "Bicycle frames": "a bicycle frame", "Bottom brackets": "a bicycle bottom bracket",
    "Motorcycle engines": "a motorcycle engine", "Motorcycle exhausts": "a motorcycle exhaust",
    "Motorcycle brakes": "a motorcycle brake", "Motorcycle wheels": "a motorcycle wheel",
    "Motorcycle chains": "a motorcycle chain", "Small engines": "a small engine",
    "Parts of lawn mowers": "a part of a lawn mower", "Chainsaw parts": "a chainsaw part",
    "Engine-generators": "a generator", "Outboard motors": "an outboard motor", "Ball bearings": "a ball bearing",
    "Roller bearings": "a roller bearing", "Gears": "a gear (toothed wheel)", "Bevel gears": "bevel gears",
    "Worm gears": "a worm gear", "Chain drive sprockets": "a sprocket", "Roller chains": "a roller chain",
    "Pulleys": "a pulley", "Belt drives": "a belt drive", "Springs (mechanical)": "a spring",
    "Valves": "a valve", "Ball valves": "a ball valve", "Gate valves": "a gate valve",
    "Butterfly valves": "a butterfly valve", "Check valves": "a check valve (non-return valve)",
    "Relief valves": "a pressure relief valve", "Solenoid valves": "a solenoid valve",
    "Thermostatic radiator valves": "a thermostatic radiator valve", "Pumps": "a pump",
    "Centrifugal pumps": "a centrifugal pump", "Piston pumps": "a piston pump", "Hand pumps": "a hand pump",
    "Gear pumps": "a gear pump", "Air compressors": "an air compressor", "Hydraulic cylinders": "a hydraulic cylinder",
    "Electric motors": "an electric motor", "Stepper motors": "a stepper motor", "Rivets": "rivets",
    "Wing nuts": "a wing nut", "Lock washers": "lock washers", "Cotter pins": "a split pin (cotter pin)",
    "Circlips": "a circlip", "Hose clamps": "a hose clip (hose clamp)", "O-rings": "O-rings", "Gaskets": "a gasket",
    "Fittings": "a pipe fitting", "Elbow pipe fittings": "an elbow pipe fitting", "Flanges": "a pipe flange",
    "Siphons": "a sink trap (siphon)", "Water meters": "a water meter", "Pressure gauges": "a pressure gauge",
}
MECH_THINGS = {
    "Automobile engines": "a car engine", "Automobiles with open hoods": "a car with its bonnet (hood) open, showing "
                                                                         "the engine bay",
    "Automobile dashboards": "a car's dashboard", "Speedometers": "a speedometer",
    "Tachometers": "a rev counter (tachometer)", "Fuel gauges": "a fuel gauge", "Odometers": "an odometer",
    "Motorcycle dashboards": "a motorcycle's instrument panel", "Water heating devices": "a water heater",
    "Air conditioners": "an air conditioner", "Heat pumps": "a heat pump",
    "Split type air conditioners - condenser": "the outdoor unit of a split air conditioner",
    "Sheet metal radiators": "a heating radiator", "Cooling towers": "a cooling tower",
    "Automobile repair shops": "a car repair workshop (garage)",
    "Motorcycle repair shops": "a motorcycle repair workshop",
}
MECH_DEEPER = {"Spark plugs", "Tires", "Automobile wheels", "Automobile headlamps", "Bicycle brakes", "Bicycle tires",
               "Motorcycle engines", "Small engines", "Ball bearings", "Gate valves", "Automobile engines",
               "Automobiles with open hoods", "Automobile dashboards", "Water heating devices"}
MECH_SA = specs(PART_Q, MECH_PARTS, MECH_DEEPER) + specs(THING_Q, MECH_THINGS, MECH_DEEPER)


def prepare_commons_mechanical_sa(source, data_dir, work, cap):
    """Wikimedia Commons mechanical categories, files under CC BY-SA or GFDL (home_sources.commons_sa_items: the
    categories share the cap; rows whose words name a child are marked "child")."""
    items = commons_sa_items(MECH_SA, cap, source.test, "mech-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: dashboard symbols

DASHBOARD_SYMBOL_CATEGORIES = ("Dashboard SVG icons", "Dashboard icons", "Warning lights")
SOFTWARE_ICON = re.compile(r"\b(paomedia|web fundamentals|material design|icon set)\b", re.I)


def symbol_entries(s, titles):
    """[(title, picture address, credit, description)] for files under CC BY-SA or GFDL, drawings (SVG) and photos,
    50 files a request (drawings as Commons' 320-pixel PNG of them)."""
    out = []
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 320,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription",
                               "iiextmetadatalanguage": "en"})
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            if not COMMONS_SA.match(licence) or re.search(r"\bN[CD]\b", licence.upper()) \
                    or info.get("mime") not in ("image/svg+xml", "image/png", "image/jpeg") \
                    or not info.get("thumburl"):
                continue
            artist = clean(re.sub(r"<[^>]+>", " ", (meta.get("Artist") or {}).get("value") or "")) or "unknown"
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            text = commons_text("", (meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}", text,
                        info.get("mime")))
        time.sleep(1)
    return out


def on_white(data, side=320):
    """A drawing's PNG (often see-through) as a JPEG with the drawing in the middle of a white square."""
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    img.thumbnail((side - 24, side - 24))
    out = Image.new("RGB", (side, side), "white")
    out.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    buffer = io.BytesIO()
    out.save(buffer, "JPEG", quality=92)
    return buffer.getvalue()


def prepare_dashboard_symbols_sa(source, data_dir, work, cap):
    """Commons dashboard symbols under CC BY-SA: each with the meaning its own description gives ("What does this
    symbol mean?") and, for the main warning lights, the standard advice ("What does this dashboard warning light
    mean?"). Software icons and files with no description are left out."""
    s = commons_session()
    titles = []
    for category in DASHBOARD_SYMBOL_CATEGORIES:
        titles += commons_members(s, category, "file")
    titles = list(dict.fromkeys(titles))
    random.Random(17).shuffle(titles)
    folder = os.path.join(data_dir, source.key)
    rows = []
    for title, url, credit, text, mime in symbol_entries(s, titles):
        if len({r["picture"] for r in rows}) >= cap + source.test:
            break
        if not text or SOFTWARE_ICON.search(f"{title} {text}"):
            continue
        try:
            r = s.get(url, timeout=60)
            data = on_white(r.content) if mime == "image/svg+xml" else r.content
        except Exception:  # noqa: BLE001 - a drawing that cannot be read is left out
            continue
        path = save(safe_name("dash-sa-" + title.split(":", 1)[-1]), data, folder)
        if not path:
            continue
        rows.append({"picture": path, "question": SYMBOL_Q if mime == "image/svg+xml" else ALT_TEXT, "answer": text,
                     "split": "", "credit": credit})
        advice = warning_advice(f"{title} {text}")
        if advice:
            rows.append({"picture": path, "question": WARNING_Q, "answer": advice, "split": "", "credit": credit})
        time.sleep(0.3)
    say(f"  Commons dashboard symbols: {len({r['picture'] for r in rows})} files")
    return rows


# ----------------------------------------------------------------- noncommercial: AutoVI (Renault)

AUTOVI = "https://zenodo.org/records/10459003/files/{}.zip?download=1"
AUTOVI_PARTS = {"engine_wiring": "the engine wiring", "pipe_clip": "the pipe clip", "pipe_staple": "the pipe staple",
                "tank_screw": "the fuel tank screw", "underbody_pipes": "the underbody pipes",
                "underbody_screw": "the underbody screw"}
# What each fault folder means ({part} is the part's name); "operator" (a worker in the picture) is left out.
AUTOVI_FAULTS = {"good": "No: {part} looks as it should.", "missing": "Yes: {part} is missing.",
                 "unclipped": "Yes: {part} is not clipped shut.", "fastening": "Yes: {part} is not fastened properly.",
                 "obstruction": "Yes: something is in the way.", "blue_hoop": "Yes: a blue hoop has been left there.",
                 "cardboard": "Yes: a piece of cardboard has been left there.",
                 "multiple": "Yes: there is more than one fault."}
AUTOVI_Q = "Is anything wrong with this part of the car?"
AUTOVI_CREDIT = ("AutoVI, the Automotive Visual Inspection Dataset (Philippe Carvalho, Meriem Lafou, Alexandre Durupt, "
                 "Antoine Leblanc and Yves Grandvalet; Renault Group and Université de technologie de Compiègne), "
                 "Zenodo 10459003, CC BY-NC-SA 4.0, https://autovi.utc.fr")


def prepare_autovi(source, data_dir, work, cap):
    """AutoVI's six parts, good and faulty, an even share of each part and fault, read out of each part's zip (100 MB
    to 1.3 GB) by HTTP ranges."""
    per_part = -(-(cap + source.test) // len(AUTOVI_PARTS))
    rows = []
    for key, part in AUTOVI_PARTS.items():
        url = AUTOVI.format(key)
        names = [n for n in remote_zip(url).namelist() if n.endswith(".png") and "/ground_truth/" not in n]
        groups = collections.defaultdict(list)
        for name in names:
            bits = name.split("/")
            if len(bits) == 4 and bits[2] in AUTOVI_FAULTS:
                groups[bits[2]].append(name)
        chosen = []
        for name in even_pick(groups, per_part, 23):
            fault = name.split("/")[2]
            chosen.append((name, {"question": AUTOVI_Q, "answer": AUTOVI_FAULTS[fault].format(part=part),
                                  "split": ""}))
            chosen.append((name, {"question": THING_Q, "answer": f"This is {part} of a car on a Renault production "
                                                                  "line.", "split": ""}))
        rows += zip_members(source, data_dir, work, lambda url=url: remote_zip(url), chosen, workers=3)
        say(f"  AutoVI {key}: {len(chosen) // 2} photos")
    return rows


# ----------------------------------------------------------------- research: dashboard warning icons

DASH_REPO = "HANTIFARAH/car-dashboard-warning-icons"
DASH_CLASSES = ["Anti_Lock_Braking_System", "Auto_Shift_Lock", "Braking_System_Issue", "Charging_System_Issue",
                "Check_Engine", "Engine_Overheating_Warning", "Fog_Lamp_Indicator", "Lane_Departure",
                "Low_Engine_Oil", "Low_Fuel", "Low_Tire_Pressure", "Master_warning_light", "SRS_Airbag", "Seat_Belt",
                "Traction_Control", "Washer_Fluid"]
DASH_NAMES = {"Anti_Lock_Braking_System": "the ABS light", "Auto_Shift_Lock": "the shift-lock light",
              "Braking_System_Issue": "the brake warning light", "Charging_System_Issue": "the battery charging light",
              "Check_Engine": "the check-engine light", "Engine_Overheating_Warning": "the engine temperature light",
              "Fog_Lamp_Indicator": "the fog light indicator", "Lane_Departure": "the lane departure light",
              "Low_Engine_Oil": "the low oil light", "Low_Fuel": "the low fuel light",
              "Low_Tire_Pressure": "the tyre pressure light", "Master_warning_light": "the master warning light",
              "SRS_Airbag": "the airbag light", "Seat_Belt": "the seat-belt reminder",
              "Traction_Control": "the traction control light", "Washer_Fluid": "the washer fluid light"}
DASH_MEANINGS = {
    "Anti_Lock_Braking_System": warning_advice("abs"), "Braking_System_Issue": warning_advice("braking system"),
    "Charging_System_Issue": warning_advice("charging system"), "Check_Engine": warning_advice("check engine"),
    "Engine_Overheating_Warning": warning_advice("overheat"), "Low_Fuel": warning_advice("low fuel"),
    "Low_Tire_Pressure": warning_advice("tyre pressure"), "SRS_Airbag": warning_advice("airbag"),
    "Seat_Belt": warning_advice("seat belt"),
    "Low_Engine_Oil": "This is the low engine oil warning light: stop the engine as soon as it is safe and check the "
                      "oil.",
    "Auto_Shift_Lock": "This is the shift-lock light: the gear lever stays locked until the brake pedal is pressed.",
    "Fog_Lamp_Indicator": "This is the fog light indicator: the fog lights are on.",
    "Lane_Departure": "This is the lane departure light, for the system that warns when the car drifts out of its "
                      "lane.",
    "Master_warning_light": "This is the master warning light: read the message on the dashboard display, and have "
                            "the car checked.",
    "Traction_Control": "This is the traction control light: it flashes while the system stops the wheels spinning; "
                        "if it stays on, the system is off or has a fault.",
    "Washer_Fluid": "This is the washer fluid light: the windscreen washer fluid is low.",
}
DASH_CREDIT = ("Car Dashboard Warning Icons (Roboflow Universe, elmello/car_dashboard_warning_icons-ywqdx, marked "
               "CC BY 4.0; copy https://huggingface.co/datasets/HANTIFARAH/car-dashboard-warning-icons); pictures "
               "gathered from the web")


def prepare_dashboard_warning_icons(source, data_dir, work, cap):
    """Dashboard pictures with their boxed warning lights (YOLO labels): one light -> its meaning; several -> which
    lights are on and where. An even share for each kind of light (by the first light of each picture)."""
    import requests
    paths = hf_tree(DASH_REPO)
    labels = {p.rsplit("/", 1)[-1].rsplit(".", 1)[0]: p for p in paths if "/labels/" in p and p.endswith(".txt")}
    images = {p.rsplit("/", 1)[-1].rsplit(".", 1)[0]: p for p in paths if "/images/" in p
              and p.lower().endswith((".jpg", ".jpeg", ".png"))}
    stems = sorted(set(labels) & set(images))
    random.Random(29).shuffle(stems)
    s = requests.Session()
    s.headers["User-Agent"] = sources.USER_AGENT
    groups, boxes = collections.defaultdict(list), {}
    want = cap + source.test
    for stem in stems[:want * 3]:
        try:
            text = s.get(hf_url(DASH_REPO, labels[stem]), timeout=60).text
        except Exception:  # noqa: BLE001 - a label file that cannot be read is left out
            continue
        found = []
        for line in text.splitlines():
            bits = line.split()
            if len(bits) >= 5 and bits[0].isdigit() and int(bits[0]) < len(DASH_CLASSES):
                found.append((DASH_CLASSES[int(bits[0])], float(bits[1]), float(bits[2])))
        if found:
            boxes[stem] = found
            groups[found[0][0]].append(stem)
    items = []
    for stem in even_pick(groups, want, 31):
        found = boxes[stem]
        kinds = list(dict.fromkeys(k for k, _, _ in found))
        name = safe_name("dash-" + stem)[:90] + ".jpg"
        url = hf_url(DASH_REPO, images[stem])
        if len(kinds) == 1:
            items.append((name, url, {"question": WARNING_Q, "answer": DASH_MEANINGS[kinds[0]], "split": ""}))
        said = [f"{DASH_NAMES[k]} {spot(x, y)}" for k, x, y in found[:6]]
        items.append((name, url, {"question": "Which warning lights are on in this picture, and where?",
                                  "answer": capital("; ".join(said)) + ".", "split": ""}))
    say(f"  Dashboard warning icons: {len({i[0] for i in items})} pictures of {len(groups)} kinds of light")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- research: car parts and damages (Humans in the Loop)

HITL_REPO = "DrBimmer/car-parts-and-damage-dataset"
HITL_CREDIT = ("Car Parts and Car Damages (Humans in the Loop, segmented by trainees of Beetroot Academy, 2023; "
               "annotations CC0, https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/); "
               "copy https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset; who took the photos is "
               "not stated")
HITL_DAMAGE = {"Dent": "a dent", "Cracked": "a crack", "Scratch": "a scratch", "Flaking": "flaking paint",
               "Broken part": "a broken part", "Paint chip": "a paint chip", "Missing part": "a missing part",
               "Corrosion": "rust (corrosion)"}


def part_words(label):
    """A dataset's part label in plain words: "Front-bumper" -> "front bumper", "back_left_door" -> "back left
    door", "License-plate" -> "number plate"."""
    words = label.replace("-", " ").replace("_", " ").lower().strip()
    return {"license plate": "number plate", "hood": "bonnet (hood)", "trunk": "boot (trunk)",
            "windshield": "windscreen", "back windshield": "rear windscreen", "front glass": "windscreen",
            "back glass": "rear windscreen", "tailgate": "tailgate"}.get(words, words)


def outline_spot(points, width, height):
    """Where an outline's centre is in the picture, and its area (for ordering)."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    cx, cy = (min(xs) + max(xs)) / 2 / width, (min(ys) + max(ys)) / 2 / height
    return spot(cx, cy), (max(xs) - min(xs)) * (max(ys) - min(ys))


def listed_places(found, most=6):
    """ "The front bumper at the bottom left of the picture; the bonnet (hood) in the centre ..." from [(name, place,
    area)]: the largest first, each name once."""
    said, seen = [], set()
    for name, place, _ in sorted(found, key=lambda f: -f[2]):
        if name not in seen:
            seen.add(name)
            said.append(f"{name} {place}")
        if len(said) >= most:
            break
    return capital("; ".join(said)) + "."


def prepare_car_parts_damage(source, data_dir, work, cap):
    """Humans in the Loop's car photos: each picture's outlined parts ("Which parts of the car can you see, and
    where?") or damage ("What damage can you see on this car, and where?"), half and half. The copy's two folders
    hold the other's pictures, so each folder's kind is read from its meta.json class list."""
    import concurrent.futures
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = sources.USER_AGENT
    paths = hf_tree(HITL_REPO)
    want = cap + source.test
    items = []
    for folder in sorted({p.split("/")[0] for p in paths if p.endswith("meta.json")}):
        meta = s.get(hf_url(HITL_REPO, f"{folder}/meta.json"), timeout=60).json()
        damage = any(c["title"] in HITL_DAMAGE for c in meta.get("classes", []))
        anns = [p for p in paths if p.startswith(folder + "/") and "/ann/" in p and p.endswith(".json")]
        random.Random(folder).shuffle(anns)

        def one(ann, damage=damage):
            """One picture's (name, address, row), or None."""
            try:
                data = s.get(hf_url(HITL_REPO, ann), timeout=60).json()
            except Exception:  # noqa: BLE001 - an annotation that cannot be read is left out
                return None
            size = data.get("size") or {}
            width, height = size.get("width"), size.get("height")
            found = []
            for obj in data.get("objects", []):
                points = (obj.get("points") or {}).get("exterior") or []
                title = obj.get("classTitle", "")
                if not points or not width or not height:
                    continue
                place, area = outline_spot(points, width, height)
                if damage and title in HITL_DAMAGE:
                    found.append((HITL_DAMAGE[title], place, area))
                elif not damage:
                    found.append(("the " + part_words(title), place, area))
            if not found:
                return None
            image = ann.replace("/ann/", "/img/")[:-len(".json")]
            question = "What damage can you see on this car, and where?" if damage else \
                "Which parts of the car can you see, and where?"
            return (safe_name("hitl-" + image.rsplit("/", 1)[-1]) + ".jpg", hf_url(HITL_REPO, image),
                    {"question": question, "answer": listed_places(found), "split": ""})

        with concurrent.futures.ThreadPoolExecutor(6) as pool:
            got = [x for x in pool.map(one, anns[:int(want / 2 * 1.2) + 2]) if x]
        items += got[:-(-want // 2)]
        say(f"  Car {'damages' if damage else 'parts'}: {len(got)} pictures")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- research: DSMLR car parts segmentation

DSMLR = "https://raw.githubusercontent.com/dsmlr/Car-Parts-Segmentation/master/"
DSMLR_CREDIT = ("Car Parts Segmentation (DSMLR, Data Science and Machine Learning Research), "
                "https://github.com/dsmlr/Car-Parts-Segmentation; no licence stated")


def prepare_car_parts_dsmlr(source, data_dir, work, cap):
    """DSMLR's 500 car photos with their outlined parts (COCO annotations): "Which parts of the car can you see, and
    where?" The parts' left and right are the car's own, as the dataset names them."""
    import requests
    items = []
    for split in ("trainingset", "testset"):
        coco = requests.get(DSMLR + f"{split}/annotations.json", timeout=120,
                            headers={"User-Agent": sources.USER_AGENT}).json()
        names = {c["id"]: c["name"] for c in coco["categories"]}
        found = collections.defaultdict(list)
        for a in coco["annotations"]:
            name = names.get(a["category_id"], "_background_")
            if name.startswith("_") or not a.get("bbox"):
                continue
            x, y, w, h = a["bbox"]
            found[a["image_id"]].append((name, x + w / 2, y + h / 2, w * h))
        for image in coco["images"]:
            parts = found.get(image["id"])
            if not parts:
                continue
            listed = [(("the car's " if re.search(r"left|right", n) else "the ") + part_words(n),
                       spot(cx / image["width"], cy / image["height"]), area) for n, cx, cy, area in parts]
            items.append((safe_name(f"dsmlr-{split}-{image['file_name']}") + ".jpg",
                          DSMLR + f"{split}/JPEGImages/{image['file_name']}",
                          {"question": "Which parts of the car can you see, and where?",
                           "answer": listed_places(listed), "split": ""}))
    random.Random(37).shuffle(items)
    return fetch_shared(items[:cap + source.test], os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- research: car damage, front and rear views

DAMAGE_VIEWS_REPO = "DrBimmer/comprehensive-car-damage"
DAMAGE_VIEWS = {"F_Normal": "No: the front of this car is not damaged.",
                "F_Crushed": "Yes: the front of this car is crushed.",
                "F_Breakage": "Yes: the front of this car has broken parts.",
                "R_Normal": "No: the back of this car is not damaged.",
                "R_Crushed": "Yes: the back of this car is crushed.",
                "R_Breakage": "Yes: the back of this car has broken parts."}
DAMAGE_VIEWS_CREDIT = ("Car Front and Rear Damage Detection (DrBimmer on Hugging Face, marked MIT; where the photos "
                       "came from is not stated), https://huggingface.co/datasets/DrBimmer/comprehensive-car-damage")


def prepare_car_damage_views(source, data_dir, work, cap):
    """Cars from the front or back, undamaged, crushed or with broken parts (the dataset's folders), an even share
    of each: "Is this car damaged?" """
    groups = collections.defaultdict(list)
    for path in hf_tree(DAMAGE_VIEWS_REPO):
        folder = path.split("/")[0]
        if folder in DAMAGE_VIEWS and path.lower().endswith((".jpg", ".jpeg", ".png")):
            groups[folder].append(path)
    items = [(safe_name("damage-" + path) + ".jpg", hf_url(DAMAGE_VIEWS_REPO, path),
              {"question": "Is this car damaged?", "answer": DAMAGE_VIEWS[path.split("/")[0]], "split": ""})
             for path in even_pick(groups, cap + source.test, 43)]
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=6)


# ----------------------------------------------------------------- research: Mechanical Parts Dataset 2022

MECH_PARTS_RAR = "https://zenodo.org/records/7504801/files/Mechanical%20Parts%20Dataset.rar?download=1"
MECH_PARTS_CREDIT = ("Mechanical Parts Dataset 2022 (Mübarek Mazhar Çakır), Zenodo 7504801, marked CC BY 4.0, "
                     "https://doi.org/10.5281/zenodo.7504801; pictures downloaded from internet platforms")
MECH_PARTS_NAMES = {"bearing": ("bearing", "bearings"), "bolt": ("bolt", "bolts"), "gear": ("gear", "gears"),
                    "nut": ("nut", "nuts")}
NUMBER_WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def counted_parts(counts):
    """ "Three bolts and two nuts." from {"bolt": 3, "nut": 2} (more than ten: "many")."""
    said = []
    for kind, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        one, many = MECH_PARTS_NAMES[kind]
        count = NUMBER_WORDS[n] if n < len(NUMBER_WORDS) else "many"
        said.append(f"{count} {one if n == 1 else many}")
    text = said[0] if len(said) == 1 else ", ".join(said[:-1]) + " and " + said[-1]
    return capital(text) + "."


def prepare_mechanical_parts_2022(source, data_dir, work, cap):
    """The Mechanical Parts Dataset's pictures with their boxed bearings, bolts, gears and nuts (YOLO labels; the
    class names from its YAML file): "What mechanical parts are in this picture?" An even share by the most common
    part in each picture."""
    archive = download_to(work, MECH_PARTS_RAR, "mechanical_parts_2022.rar")
    folder = os.path.join(work, "mechanical_parts_2022")
    if not os.path.isdir(folder):
        sources.unpack(archive, folder)
    names = []
    for base, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith((".yaml", ".yml")):
                with open(os.path.join(base, f), encoding="utf-8", errors="replace") as y:
                    m = re.search(r"names\s*:\s*\[([^\]]*)\]", y.read())
                if m:
                    names = [n.strip(" '\"").lower() for n in m.group(1).split(",")]
    if not names:
        names = ["bearing", "bolt", "gear", "nut"]
    groups, answers, originals = collections.defaultdict(list), {}, set()
    for picture in sources.pictures_in(folder):
        label = re.sub(r"[/\\]images([/\\])", r"\1labels\1", picture).rsplit(".", 1)[0] + ".txt"
        original = re.split(r"_(jpe?g|png)\.rf\.", os.path.basename(picture), flags=re.I)[0].lower()
        if not os.path.exists(label) or original in originals:      # Roboflow's copies share the original's name
            continue
        originals.add(original)
        counts = collections.Counter()
        with open(label, encoding="utf-8", errors="replace") as f:
            for line in f:
                bits = line.split()
                if bits and bits[0].isdigit() and int(bits[0]) < len(names) and names[int(bits[0])] in \
                        MECH_PARTS_NAMES:
                    counts[names[int(bits[0])]] += 1
        if counts:
            answers[picture] = counted_parts(counts)
            groups[counts.most_common(1)[0][0]].append(picture)
    out = []
    target = os.path.join(data_dir, source.key)
    for picture in even_pick(groups, cap + source.test, 47):
        with open(picture, "rb") as f:
            path = save(safe_name("mechparts-" + os.path.relpath(picture, folder)), f.read(), target)
        if path:
            out.append({"picture": path, "question": "What mechanical parts are in this picture?",
                        "answer": answers[picture], "split": ""})
    say(f"  Mechanical Parts 2022: {len(out)} pictures")
    return out


# ----------------------------------------------------------------- the table

MECHANICAL_SOURCES = [
    # ---- share-alike
    Source("commons_mechanical_sa", "Wikimedia Commons: car, motorcycle, bicycle, machine, plumbing and heating "
                                    "parts, engine bays and dashboards, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 3000, 30, prepare_commons_mechanical_sa, "about 300 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("dashboard_symbols_sa", "Wikimedia Commons: dashboard warning and indicator symbols with their meanings "
                                   "(share-alike)",
           "Each file CC BY-SA (its Commons page)",
           "Wikimedia Commons authors, CC BY-SA, each credited in its row (Category:Dashboard SVG icons and others), "
           "https://commons.wikimedia.org", "share-alike", 450, 10, prepare_dashboard_symbols_sa,
           "about 10 MB", terms="https://creativecommons.org/licenses/by-sa/3.0/",
           terms_summary="CC BY-SA: use with credit, and anything made from it keeps the same licence."),
    # ---- non-commercial
    Source("autovi", "AutoVI: car parts on Renault's production lines, good or faulty (personal use)",
           "CC BY-NC-SA 4.0 (Zenodo 10459003, license.txt)", AUTOVI_CREDIT, "noncommercial", 1500, 20,
           prepare_autovi, "about 300 MB, read out of six zips of 0.1 to 1.3 GB",
           terms="https://zenodo.org/records/10459003",
           terms_summary="CC BY-NC-SA 4.0: use with credit, not for commercial purposes, and anything made from it "
                         "shared under the same terms."),
    # ---- research
    Source("dashboard_warning_icons", "Car dashboard warning lights: what each light means (personal use)",
           "Marked CC BY 4.0 by its Roboflow uploader; the pictures were gathered from the web (stock photo file "
           "names), so their own rights are unclear", DASH_CREDIT, "research", 2000, 20,
           prepare_dashboard_warning_icons, "about 150 MB",
           terms="https://universe.roboflow.com/elmello/car_dashboard_warning_icons-ywqdx",
           terms_summary=research("Its uploader marked it CC BY 4.0, but many pictures carry stock-photo file names "
                                  "(Shutterstock), so the rights in the pictures are not the uploader's to give.")),
    Source("car_parts_damage", "Car Parts and Car Damages: car body parts and damage, and where they are (personal "
                               "use)",
           "Annotations CC0 (Humans in the Loop); who took the photos is not stated", HITL_CREDIT, "research", 1500,
           20, prepare_car_parts_damage, "about 500 MB",
           terms="https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/",
           terms_summary=research("The annotations are CC0, but the photos' source and licence are not stated.")),
    Source("car_parts_dsmlr", "Car Parts Segmentation: which parts of a car are where (personal use)",
           "No licence stated (github.com/dsmlr/Car-Parts-Segmentation)", DSMLR_CREDIT, "research", 500, 10,
           prepare_car_parts_dsmlr, "about 150 MB", terms="https://github.com/dsmlr/Car-Parts-Segmentation",
           terms_summary=research("No licence is stated for the photos or the annotations.")),
    Source("car_damage_views", "Car front and rear damage: is this car damaged? (personal use)",
           "Marked MIT by its uploader; where the photos came from is not stated", DAMAGE_VIEWS_CREDIT, "research",
           1200, 20, prepare_car_damage_views, "about 200 MB",
           terms="https://huggingface.co/datasets/DrBimmer/comprehensive-car-damage",
           terms_summary=research("Marked MIT, but the photos' source is not stated, so the rights in them are "
                                  "unclear.")),
    Source("mechanical_parts_2022", "Mechanical Parts Dataset: bearings, bolts, gears and nuts, counted (personal "
                                    "use)",
           "Marked CC BY 4.0 (Zenodo 7504801); its pictures were downloaded from internet platforms",
           MECH_PARTS_CREDIT, "research", 1500, 20, prepare_mechanical_parts_2022, "93 MB (a RAR archive)",
           terms="https://zenodo.org/records/7504801",
           terms_summary=research("Marked CC BY 4.0, but its own description says the pictures were downloaded from "
                                  "various internet platforms, so the rights in them are not the maker's to give.")),
]

# The collections a picture-making model may learn from: parts and symbols without people.
MECHANICAL_PICTURE_MAKING_OK = {"dashboard_symbols_sa", "dashboard_warning_icons", "mechanical_parts_2022", "autovi"}

MECHANICAL_SIGN_UP = {
    "Roboflow Universe car, engine-bay, dashboard and tyre sets":
        "https://universe.roboflow.com : a free Roboflow account and API key. Engine-bay part detection (search "
        "'engine bay', 'under hood'), car dashboard icons (for example joe-ehtxb/car-dashboard-icons-kai and "
        "space-kreca/car-dashboard-icons-2, both marked CC BY 4.0), tyre tread (mark-aft7n/tire-tread, about 5,300 "
        "pictures, CC BY 4.0) and car parts (car-parts-0s8x5/car-parts-ocfeo, CC BY 4.0). Check where each set's "
        "pictures came from; many are gathered from the web.",
    "Kaggle car-part and mechanical-part sets":
        "https://www.kaggle.com : a Kaggle account. '50 Types of Car Parts' (gpiosenka: 224-pixel web pictures of "
        "50 parts), 'Mechanical parts' (bolts, nuts, washers, locating pins), tyre-quality and car-damage sets. "
        "Check each set's licence and where its pictures came from (most are gathered from the web: research).",
    "CarDD, Car Damage Detection (USTC PIC Lab; research only)":
        "https://cardd-ustc.github.io : fill in the licence form and email it to the PIC Lab; 4,000 photos with "
        "dents, scratches, cracks, broken glass, flat tyres and broken lamps outlined. Non-commercial research only; "
        "no redistribution.",
    "BogieSeg, railway bogie parts and wheel defects (CC BY 4.0)":
        "https://zenodo.org/records/18831526 : the files are restricted on Zenodo (request access). 391 photos taken "
        "at Kotri Railway Junction, Pakistan, with axle boxes, springs, nuts, screws, rods and wheels outlined.",
    "MVTec Screws and MVTec AD (CC BY-NC-SA 4.0)":
        "https://www.mvtec.com/company/research/datasets : a download form. Screws and nuts (also listed in "
        "extra_sources.py), and metal nuts, screws, transistors and cables with defects.",
}

MECHANICAL_NOT_INCLUDED = {
    "Mechanical Components Benchmark (MCB; repository MIT)":
        "computer models (CAD), not photos, collected from TraceParts, 3D Warehouse and GrabCAD under those sites' "
        "own terms; making pictures from them would need a 3D renderer, which the kit does not include.",
    "Fusion 360 Gallery Dataset (Autodesk; non-commercial research licence)":
        "computer models (CAD) of designed parts, not photos, and no names saying what each part is.",
    "HARTU Automotive Dataset (Tekniker, Zenodo 18341239, CC BY 4.0)":
        "computer-made renders of car parts from CAD models whose parts are named only 'part1' and 'part2'.",
    "Open Mechanical 3D Models Dataset (Zenodo 24167336, CC BY 4.0)": "student CAD models and line drawings, not "
                                                                       "photos.",
    "Bearing and gearbox vibration sets (CWRU, Paderborn, XJTU-SY, Forgis/Mechanical-Components ...)":
        "sensor recordings (vibration and sound), not pictures.",
    "NMiriams Good_Tires and Defective_Tires (Hugging Face, CC BY 4.0)":
        "copies of the Velammal tyre photos, which the open tyre_condition pack takes from Mendeley Data itself.",
    "Car Parts Dataset (Zenodo 4656021 and 4656022)": "tables of car-part data, not pictures.",
    "US Army technical manuals (public domain)":
        "PDF manuals of line drawings with no list of pictures a program can read; US government photos of "
        "mechanics and vehicles reach the open Commons packs through Wikimedia Commons.",
    "Stanford Cars and CompCars": "car models, not parts; they are in culture_sources.py.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one mechanical collection.")
    parser.add_argument("key", choices=[s.key for s in MECHANICAL_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in MECHANICAL_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="mechanical-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
