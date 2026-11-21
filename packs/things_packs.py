"""Pack builders for technology and devices, tools, kitchen gadgets, hardware and building supplies, and for all of
these (and household things in general) IN USE: a person holding, using or operating something. Used by build_packs.py
in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None,
row)], where a row is {"question", "answer", "credit"}, plus "place" where the source states one and "child": true
where the picture may show a child (the picture-making trainer leaves those rows out). A picture with more than one
question comes once with its JPEG and then again as (None, None, row) rows whose "file" names the same picture
(food_packs.with_twins), so the zip holds each picture only once. The limit counts pictures.

Every answer is a fixed sentence written here from the source's own records: a product listing's type, brand, name,
colour and material; a label or a relationship people checked by hand; a Commons category's name; a class the
dataset's makers gave. Where a tool's use is said, it is one short generic line ("a spirit level, used to check that
something is level"). Nothing is written by an AI model.

Where in the world (the row's "place"): only where the source says so. ABO gives the Amazon shop (country) each
listing is from: rows carry it as "place" with "place_kind": "market" (the country where the product is sold, not
where the catalogue photo was taken). Commons categories named after a country ("Cooking in Uganda") give that
country, and a Commons file's own camera coordinates give theirs. CODD (Cyprus) and the NYU Abu Dhabi materials (Abu
Dhabi, United Arab Emirates) say where all their photos were taken. Open Images photos have no stated place, so none
is given. Where a source spans several countries, the builders take them in turn, so one country does not fill a pack.

The packs (all open, checked at the source):
  abo_products       Amazon Berkeley Objects (Amazon.com and UC Berkeley, CC BY 4.0): catalogue photos of products
                     sold on Amazon's shops in 19 countries (India, USA, Canada, UK, Germany, Mexico, Spain, France,
                     Italy, Japan, Australia, the Netherlands, Singapore, United Arab Emirates, Sweden, Saudi Arabia,
                     Turkey, Poland, Brazil): electronics and their accessories, tools and hardware, kitchen things,
                     furniture and home goods (not clothes, shoes, jewellery, food or medicines). "What is this?" ->
                     "This is an electric kettle by AmazonBasics. Its listing calls it ... Colour: silver. Material:
                     stainless steel." and, for tools, "What tool is this, and what is it used for?" The countries
                     take turns, and phone cases (half of ABO) are held to a small share.
  open_images_in_use Google Open Images V7 visual relationships (CC BY 4.0; each photo CC BY 2.0, checked photo by
                     photo, photographer named): what a man, woman, boy, girl or person is doing with a thing, as
                     people marked it by hand: holds, plays, uses (interacts with), talks on the phone, reads, cuts,
                     eats, drinks, hits, kicks, throws, catches, rides, wears (headphones, glasses, helmets ...).
                     "What is the person doing with the guitar?" -> "The man is playing the guitar." Animals, other
                     people and weapons are left out. Rows with a boy or girl are marked "child".
  open_images_tech   Open Images V7 labels people checked by hand for technology and electronics (smartphones,
                     desktop computers, circuit boards, microcontrollers, resistors, cameras, tripods, projectors,
                     routers, hard disks ...), building materials (bricks, concrete, lumber, plywood, tiles, pipes,
                     scaffolding), workshop tools (lathes, grinders, clamps, workbenches) and kitchen gadgets (espresso
                     machines, juicers, rice cookers, mortars and pestles): only labels that open_images_objects and
                     open_images_home do not already ask about. "What technology is in this picture?" and "Is there
                     a ... in this picture?" (no only where people checked and rejected it).
  commons_things     Wikimedia Commons: electronic parts (circuit boards, chips, capacitors, resistors, LEDs,
                     Raspberry Pi, breadboards, memory, USB sticks), devices (smartphones, feature phones, laptops,
                     keyboards, webcams, projectors, radios, solar lamps and chargers, e-waste), tools commons_tools
                     does not have (ladders, chainsaws, vices, crowbars, trowels, pickaxes, sanders, multimeters ...),
                     building supplies (bricks, concrete blocks, roof tiles, rebar, plywood, cement bags, corrugated
                     iron, copper pipes, circuit breakers) and kitchen gadgets commons_kitchen does not have (clay
                     pots, mortars and pestles, sieves, blenders, juicers, French presses, rocket, kerosene and
                     charcoal stoves, charcoal irons ...). Pictures CC0, public domain or CC BY (author credited).
  commons_in_use     Wikimedia Commons categories of people using things: laptops, computers, tablets, typewriters,
                     headphones, hammers, chainsaws, ladders, wheelbarrows, brooms, irons, soldering irons; carpenters,
                     gardeners, photographers and repairers at work; cooking (and cooking and kitchens in Uganda,
                     Nigeria, Ghana, Kenya, Tanzania, India, Pakistan, Bangladesh and Mexico, with that country as
                     the place); brick making in India and construction workers in Nigeria. "What is the person
                     doing?" Files whose words name a child are marked "child".
  brick_quality      Brick quality photos (Rahman, Iesmin, Noyon, Hasan, Rimi and Jahan, Mendeley Data n4wf5g4nrm,
                     CC BY 4.0): bricks at three brick fields and two building sites, sorted by the authors into
                     first class, second class, second class with algae, third class (under-burnt), "pricate"
                     (over-burnt, warped) and "jhama" (very over-burnt). "What grade is this brick?" The dataset does
                     not say which country, so no place is given.
  codd_materials     CODD, Construction and Demolition Waste Object Detection Dataset (Demetriou, Mavromatidis, Petrou
                     and Nicolaides, Mendeley Data wds85kt64j v3, CC BY 4.0): building waste at a recycling plant in
                     Cyprus, every piece outlined by hand as brick, concrete, tile, wood, pipe, plastic, foam
                     insulation, stone, plasterboard or general waste. "What building materials are in this picture?"
                     (The Mendeley listing gives the first 1,000 files of each folder, so about 1,500 photos.)
  nyuad_materials    Construction material conditions (Mengiste, Mannem, Prieto and Garcia de Soto, NYU Abu Dhabi,
                     Mendeley Data zv66h54b8j, CC BY 4.0): 208 photos from a building site on the NYU Abu Dhabi campus
                     of concrete-block walls, concrete, chiselled concrete, gypsum, mesh and first and second coats of
                     plaster. "What building material or surface is this?"

Non-open collections on the same subjects (EPIC-KITCHENS, Charades, PACO, MINC) are kit download entries in
training-kit/kit/things_sources.py, with the sign-up and left-out collections listed there.

    python packs/things_packs.py abo_products --limit 8      (prints a few rows: a quick check of one builder)
"""

import collections
import csv
import gzip
import io
import json
import math
import re
import sys
import time
import xml.etree.ElementTree as ElementTree
import zipfile

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, considered, ALT_TEXT
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from food_packs import (listed, with_twins, count_pictures, oi_lines, oi_licence_name, OI_LABELS, OI_CLASSES,
                        OI_IMAGES, OI_PICTURE)
from everyday_packs import OI_HOME
from expression_packs import mark_child, child_count, OI_CHILD
from home_packs import (OI_TOOLS, OI_DEVICES, OI_PERSONAL, OI_KITCHEN, NUDE, NOT_RESPECTFUL, FIRST_PERSON,
                        LIFE_STAGE, COMMONS_PLACES, home_entries, commons_fetch, file_name, category_files)
from places import where, country_named


def a_or_an(phrase):
    """ "a" or "an" before a phrase (by its first letter; "an hour" and "a university" are rare here)."""
    return "an" if phrase[:1].lower() in "aeiou" else "a"


def with_article(phrase):
    """ "a drill", "an iron"; plural or uncountable phrases ("pliers", "concrete") as they are."""
    if phrase in UNCOUNTED or phrase.endswith("s") and not phrase.endswith(("ss", "us")):
        return phrase
    return f"{a_or_an(phrase)} {phrase}"


UNCOUNTED = {"concrete", "cement", "lumber", "plywood", "wood", "tile", "wire", "scaffolding", "brickwork",
             "building insulation", "headphones", "glasses", "sunglasses", "goggles", "jeans", "trousers",
             "electronics", "beer", "wine", "juice", "milk", "coffee", "a cocktail", "food", "pasta", "cheese",
             "watermelon", "cake", "candy", "pizza", "mortar"}


# ----------------------------------------------------------------- abo_products (Amazon Berkeley Objects)

ABO = "https://amazon-berkeley-objects.s3.amazonaws.com/"
ABO_LISTINGS = ABO + "listings/metadata/listings_{}.json.gz"        # 16 files, 0-9 and a-f, about 5 MB each
ABO_IMAGES = ABO + "images/metadata/images.csv.gz"                  # image id -> path (6 MB)
ABO_PICTURE = ABO + "images/original/{}"
ABO_CREDIT = ("Amazon Berkeley Objects: data and images by Amazon.com; dataset by Matthieu Guillaumin, Thomas "
              "Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC Berkeley); "
              "CC BY 4.0, https://amazon-berkeley-objects.s3.amazonaws.com/index.html; item {item} ({domain})")
# The product types used, with the plain words an answer names them by. The listing's own name, brand, colour and
# material follow. Types that are too general to name the thing ("HOME", "KITCHEN", "TOOLS" ...) are in ABO_GENERAL:
# for them the answer names only the listing.
ABO_TYPES = {
    # technology and electronics
    "HEADPHONES": "headphones", "SPEAKERS": "a loudspeaker", "CHARGING_ADAPTER": "a charger",
    "ELECTRONIC_ADAPTER": "an electronic adapter", "BATTERY": "batteries", "KEYBOARDS": "a computer keyboard",
    "INPUT_MOUSE": "a computer mouse", "COMPUTER_INPUT_DEVICE": "a computer input device",
    "MULTIPORT_HUB": "a multi-port hub", "COMPUTER_DRIVE_OR_STORAGE": "a computer storage drive",
    "FLASH_MEMORY": "a memory card or USB stick", "COMPUTER_COMPONENT": "a computer part",
    "COMPUTER_ADD_ON": "a computer accessory", "PERSONAL_COMPUTER": "a computer", "COMPUTER": "a computer",
    "NOTEBOOK_COMPUTER": "a laptop", "PHONE": "a phone", "LANDLINE_PHONE": "a landline phone",
    "PHONE_ACCESSORY": "a phone accessory", "WIRELESS_ACCESSORY": "a wireless accessory",
    "SCREEN_PROTECTOR": "a screen protector", "PORTABLE_ELECTRONIC_DEVICE_STAND": "a stand for a phone or tablet",
    "PORTABLE_ELECTRONIC_DEVICE_MOUNT": "a mount for a phone or tablet",
    "PORTABLE_ELECTRONIC_DEVICE_COVER": "a cover for a tablet or e-reader",
    "FLAT_SCREEN_DISPLAY_MOUNT": "a wall mount for a television or monitor", "POWER_STRIP": "a power strip",
    "POWER_SUPPLIES_OR_PROTECTION": "a power supply", "ELECTRONIC_CABLE": "a cable", "ANTENNA": "an aerial",
    "SECURITY_ELECTRONICS": "a security camera or alarm", "MICROPHONE": "a microphone", "RADIO": "a radio",
    "PORTABLE_AUDIO": "a portable audio player", "SOUND_AND_RECORDING_EQUIPMENT": "sound recording equipment",
    "PORTABLE_AV_DEVICE": "a portable audio or video device", "VIDEO_PROJECTOR": "a video projector",
    "VIDEO_GAME_ACCESSORIES": "a video game accessory", "CAMERA_TRIPOD": "a camera tripod",
    "CAMERA_LENS_FILTERS": "a camera lens filter", "CAMERA_BAGS_AND_CASES": "a camera bag",
    "CAMERA_OTHER_ACCESSORIES": "a camera accessory", "OFFICE_ELECTRONICS": "an office machine",
    "INK_OR_TONER": "printer ink or toner", "INKJET_PRINTER_INK": "printer ink", "REMOTE_CONTROL": "a remote control",
    "INPUT_PEN": "a stylus pen", "MOUSE_PAD": "a mouse mat", "BLANK_MEDIA": "blank discs or media",
    "CE_ACCESSORY": "an electronics accessory", "CE_CARRYING_CASE_OR_BAG": "a case for electronics",
    "ELECTRIC_FAN": "an electric fan", "STRING_LIGHT": "string lights", "LIGHT_BULB": "a light bulb",
    "LIGHT_SOURCE": "a light", "HOME_LIGHTING_AND_LAMPS": "a lamp", "LAMP": "a lamp",
    "LIGHT_FIXTURE": "a light fitting",
    "WATCH": "a watch", "CELLULAR_PHONE_CASE": "a phone case", "THERMOPLASTIC_FILAMENT": "3D printer filament",
    "ELECTROMECHANICAL_GAUGE": "a gauge", "WEIGH_SCALE": "a weighing scale", "MICROSCOPES": "a microscope",
    # tools and hardware
    "WRENCH": "a spanner (wrench)", "SCREWDRIVER": "a screwdriver", "PLIERS": "a pair of pliers",
    "DRILL_BITS": "drill bits", "UTILITY_KNIFE": "a utility knife", "MULTITOOL": "a multi-tool",
    "LADDER": "a ladder", "SCISSORS": "a pair of scissors", "HARDWARE_HANDLE": "a door or drawer handle",
    "HARDWARE_HINGE": "a hinge", "LOCK": "a lock", "SAFE": "a safe", "DOORSTOP": "a door stop",
    "STORAGE_HOOK": "a hook", "MECHANICAL_COMPONENTS": "a mechanical part", "SEALS": "seals",
    "CARGO_STRAP": "a cargo strap", "SAFETY_GLASSES": "safety glasses", "EARMUFF": "ear defenders",
    "EARPLUG": "earplugs", "PLUMBING_FIXTURE": "a plumbing fitting", "FAUCET": "a tap (faucet)",
    "SHOWERHEAD": "a shower head", "TOILET_SEAT": "a toilet seat", "WATER_PUMP": "a water pump",
    "WATER_PURIFICATION_UNIT": "a water purifier", "BUILDING_MATERIAL": "a building material",
    "BUCKET": "a bucket", "BROOM": "a broom", "CLEANING_BRUSH": "a cleaning brush",
    "VACUUM_CLEANER": "a vacuum cleaner", "AIR_CONDITIONER": "an air conditioner", "HUMIDIFIER": "a humidifier",
    "WASHER_DRYER_COMBINATION": "a washer-dryer", "MAJOR_HOME_APPLIANCES": "a large home appliance",
    "AUTO_PART": "a car part", "AUTO_ACCESSORY": "a car accessory", "WHEEL": "a wheel",
    "FIRST_AID_KIT": "a first aid kit", "LAB_SUPPLY": "laboratory equipment", "STAPLER": "a stapler",
    "WRITING_BOARD": "a whiteboard or writing board", "WRITING_INSTRUMENT": "a pen or pencil",
    "MARKING_PEN": "a marker pen", "LABEL": "labels", "ENVELOPE": "envelopes", "FILE_FOLDER": "file folders",
    "STORAGE_BINDER": "a ring binder", "PRINT_COPY_PAPER": "printer paper", "TENT": "a tent",
    "SLEEPING_BAG": "a sleeping bag", "FREESTANDING_SHELTER": "a shelter or gazebo", "PLANTER": "a plant pot",
    "WILDLIFE_FEEDER": "a bird feeder",
    # kitchen
    "SAUTE_FRY_PAN": "a frying pan", "DUTCH_OVENS": "a casserole pot (Dutch oven)", "CASSEROLES": "a casserole dish",
    "BAKING_PAN": "a baking tin", "SHEET_PAN": "a baking tray", "PRESSURE_COOKER": "a pressure cooker",
    "RICE_COOKERS": "a rice cooker", "COFFEE_MAKER": "a coffee maker", "ELECTRIC_WATER_BOILER": "an electric kettle",
    "FOOD_BLENDER": "a blender", "TOASTER": "a toaster", "KITCHEN_KNIFE": "a kitchen knife",
    "FOOD_SLICER": "a food slicer", "CAN_OPENER": "a tin opener", "FLATWARE": "cutlery", "DRINKING_CUP": "a cup",
    "DISHWARE_PLATE": "a plate", "DISHWARE_BOWL": "a bowl", "DISHWARE_PLACE_SETTING": "a dinner set",
    "JAR": "a jar", "BOTTLE": "a bottle", "PITCHER": "a jug", "THERMOS": "a vacuum flask",
    "FOOD_STORAGE_BAG": "food storage bags", "MEAL_HOLDER": "a lunch box", "POT_HOLDER": "an oven glove",
    "PLACEMAT": "place mats", "DRYING_RACK": "a drying rack", "BOTTLE_RACK": "a bottle rack",
    "PAPER_TOWEL_HOLDER": "a kitchen roll holder", "TRASH_CAN": "a bin", "PUMP_DISPENSER": "a pump dispenser",
    "FOOD_SERVICE_SUPPLY": "catering supplies",
    # home and furniture
    "CHAIR": "a chair", "SOFA": "a sofa", "TABLE": "a table", "DESK": "a desk", "BED": "a bed",
    "BED_FRAME": "a bed frame", "HEADBOARD": "a headboard", "MATTRESS": "a mattress", "OTTOMAN": "a footstool",
    "STOOL_SEATING": "a stool", "BENCH": "a bench", "CABINET": "a cabinet", "SHELF": "a shelf",
    "DRESSER": "a chest of drawers", "STORAGE_DRAWER": "a set of storage drawers", "STORAGE_BOX": "a storage box",
    "STORAGE_RACK": "a storage rack", "STORAGE_BAG": "a storage bag", "BASKET": "a basket",
    "LAUNDRY_HAMPER": "a laundry basket", "CLOTHES_HANGER": "clothes hangers", "CLOTHES_RACK": "a clothes rail",
    "BEAN_BAG_CHAIR": "a beanbag chair", "HOME_MIRROR": "a mirror", "CLOCK": "a clock", "CURTAIN": "curtains",
    "WINDOW_SHADE": "a window blind", "RUG": "a rug", "PILLOW": "a pillow or cushion", "FLAT_SHEET": "a bed sheet",
    "TOWEL_HOLDER": "a towel rail", "TOILET_PAPER_HOLDER": "a toilet roll holder", "UMBRELLA": "an umbrella",
    "SUITCASE": "a suitcase", "LUGGAGE": "luggage", "BACKPACK": "a backpack", "CANDLE": "a candle",
    "CANDLE_HOLDER": "a candle holder", "VASE": "a vase", "FURNITURE_COVER": "a furniture cover",
    "AV_FURNITURE": "a television stand", "EXERCISE_MAT": "an exercise mat", "STATIONARY_BICYCLE": "an exercise bike",
    "AREA_DEODORIZER": "an air freshener", "JEWELRY_STORAGE": "a jewellery box", "WASTE_BAG": "bin bags",
}
ABO_GENERAL = {"HOME", "KITCHEN", "TOOLS", "HARDWARE", "OFFICE_PRODUCTS", "ABIS_HOME_IMPROVEMENT", "ABIS_KITCHEN",
               "ABIS_ELECTRONICS", "ABIS_LAWN_AND_GARDEN", "CONSUMER_ELECTRONICS", "OUTDOOR_LIVING",
               "HOME_BED_AND_BATH", "HOME_FURNITURE_AND_DECOR", "FURNITURE", "ACCESSORY_OR_PART_OR_SUPPLY",
               "JANITORIAL_SUPPLY", "SAFETY_SUPPLY", "HOME_LIGHTING_ACCESSORY", "STORAGE_HOOK"}
# A short generic use, for "What tool is this, and what is it used for?"
ABO_USES = {
    "WRENCH": "used to turn nuts and bolts", "SCREWDRIVER": "used to turn screws",
    "PLIERS": "used to grip, bend or cut wire", "DRILL_BITS": "fitted into a drill to make holes",
    "UTILITY_KNIFE": "used to cut card, carpet and other materials", "MULTITOOL": "a folding tool with several "
    "blades and tools in one", "LADDER": "used to reach high places", "SCISSORS": "used to cut paper or cloth",
    "CAN_OPENER": "used to open tins", "KITCHEN_KNIFE": "used to cut food", "FOOD_SLICER": "used to slice food",
    "CAMERA_TRIPOD": "used to hold a camera steady", "WEIGH_SCALE": "used to weigh things",
    "MICROSCOPES": "used to see very small things", "STAPLER": "used to fasten sheets of paper together",
    "BROOM": "used to sweep the floor", "VACUUM_CLEANER": "used to clean floors and carpets by suction",
    "FOOD_BLENDER": "used to blend food and drinks",
    "PRESSURE_COOKER": "used to cook food quickly under steam pressure",
    "RICE_COOKER": "used to cook rice", "RICE_COOKERS": "used to cook rice", "TOASTER": "used to toast bread",
    "ELECTRIC_WATER_BOILER": "used to boil water", "COFFEE_MAKER": "used to make coffee",
    "MARKING_PEN": "used to write or mark", "WATER_PUMP": "used to pump water",
}
# The hardware, tool, plumbing-fixture and protective-equipment types that hardware_packs abo_hardware takes, with
# answers that name finishes and sizes: abo_products leaves them out, so no listing is in both packs.
ABO_HARDWARE_TYPES = frozenset({
    "HARDWARE_HANDLE", "HARDWARE", "HARDWARE_HINGE", "LOCK", "DOORSTOP", "STORAGE_HOOK", "HARDWARE_CLAMP_VISE",
    "TOOLS", "WRENCH", "SCREWDRIVER", "PLIERS", "DRILL_BITS", "FASTENER_DRIVE_BIT", "MULTITOOL", "UTILITY_KNIFE",
    "PORTABLE_TOOL_BOX", "LADDER", "FAUCET", "SHOWERHEAD", "VALVE", "TOILET_SEAT", "TOWEL_HOLDER",
    "TOILET_PAPER_HOLDER", "CARGO_STRAP", "EARMUFF", "EARPLUG", "SAFETY_GLASSES"})
ABO_TOOL_Q = "What tool is this, and what is it used for?"
ABO_WHAT_Q = "What is this?"
ABO_PHONE_CASE_SHARE = 0.03          # phone cases are half of ABO: at most this share of the pack
ABO_NOT_A_WORD = re.compile(r"^(n/?a|none|multi(colou?r)?|other|see description|not applicable|\d+)$", re.I)


def abo_value(field, country=""):
    """The English value of a listing's language-tagged field ([{"language_tag", "value"}]), preferring the English of
    the listing's own country (en_IN for India); "" when there is none in English."""
    values = [v for v in field or [] if isinstance(v, dict) and str(v.get("language_tag", "")).startswith("en")]
    values.sort(key=lambda v: v.get("language_tag") != f"en_{country}")
    return clean(str(values[0].get("value", ""))) if values else ""


ABO_NOT_TELLING = {"a", "an", "or", "for", "of", "the", "and", "pair", "set", "part", "large", "home", "small"}


def abo_name_says(kind, name):
    """Whether the listing's name has one of the telling words of a kind ("a pair of pliers": "pliers"), singular or
    plural."""
    words = [w for w in re.findall(r"[a-z]+", re.sub(r"\(.*?\)", " ", kind.lower()) + " " +
                                   " ".join(re.findall(r"\((.*?)\)", kind.lower())))
             if w not in ABO_NOT_TELLING and len(w) > 2]
    low = name.lower()
    return any(re.search(rf"\b{re.escape(w.rstrip('s'))}(s|es)?\b", low) for w in words)


def abo_rows(listing):
    """The rows for one ABO listing, or [] when it is not one this pack uses (or has no English name)."""
    kind_code = ((listing.get("product_type") or [{}])[0] or {}).get("value", "")
    if (kind_code not in ABO_TYPES and kind_code not in ABO_GENERAL) or kind_code in ABO_HARDWARE_TYPES:
        return []
    country = listing.get("country") or ""
    name = abo_value(listing.get("item_name"), country)
    if not name or not listing.get("main_image_id"):
        return []
    brand = abo_value(listing.get("brand"), country)
    colour = abo_value(listing.get("color"), country)
    material = abo_value(listing.get("material"), country)
    # The product type is named only when the listing's own name says the same (the types are sometimes wrong: an
    # extension lead filed as a security camera), so the answer never says more than the record.
    kind = ABO_TYPES.get(kind_code, "")
    if kind and not abo_name_says(kind, name):
        kind = ""
    verb = "These are" if kind.endswith("s") and not kind.startswith(("a ", "an ")) else "This is"
    first = f"{verb} {kind}" + (f" by {brand}" if brand and brand.lower() not in name.lower() else "") + ". " \
        if kind else (f"This is a product by {brand}. " if brand and brand.lower() not in name.lower() else "")
    answer = first + f"Its listing calls it: {name.rstrip('.')}."
    if colour and not ABO_NOT_A_WORD.match(colour) and colour.lower() not in name.lower():
        answer += f" Colour: {colour.lower()}."
    if material and not ABO_NOT_A_WORD.match(material) and material.lower() not in name.lower():
        answer += f" Material: {material.lower()}."
    rows = [{"question": ABO_WHAT_Q, "answer": answer}]
    if kind_code in ABO_USES and kind:
        rows.append({"question": ABO_TOOL_Q, "answer": f"This is {kind}, {ABO_USES[kind_code]}."})
    return rows


def build_abo_products(limit):
    """The ABO pack: reads the 16 listing files (about 85 MB) and the image list (6 MB), keeps the product types above
    that have an English name and a main photo, and takes the shops' countries in turn (and, within a country, the
    product types in turn), so that India's many listings do not fill the pack; phone cases are held to a small
    share. Then fetches the catalogue photos (the originals, made smaller)."""
    s, rng = session(), pass_random(91)
    by_country = collections.defaultdict(lambda: collections.defaultdict(list))
    seen_images = set()
    for part in "0123456789abcdef":
        r = s.get(ABO_LISTINGS.format(part), timeout=600)
        r.raise_for_status()
        for line in gzip.decompress(r.content).decode("utf-8").splitlines():
            try:
                listing = json.loads(line)
            except ValueError:
                continue
            rows = abo_rows(listing)
            image = listing.get("main_image_id")
            if not rows or image in seen_images:          # the same product in several shops: once only
                continue
            seen_images.add(image)
            kind = listing["product_type"][0]["value"]
            by_country[listing.get("country") or ""][kind].append((listing, rows))
    say(f"ABO: {sum(len(v) for c in by_country.values() for v in c.values())} usable listings in "
        f"{len(by_country)} countries")
    paths = {}
    r = s.get(ABO_IMAGES, timeout=600)
    r.raise_for_status()
    for row in csv.DictReader(io.StringIO(gzip.decompress(r.content).decode("utf-8"))):
        if row["image_id"] in seen_images:
            paths[row["image_id"]] = row["path"]
    # Each country's listings, the product types in turn; then the countries in turn.
    queues = {}
    for country, kinds in by_country.items():
        lists = []
        for kind in sorted(kinds):
            items = kinds[kind]
            rng.shuffle(items)
            lists.append(items)
        rng.shuffle(lists)
        queue = []
        while any(lists):
            for items in lists:
                if items:
                    queue.append(items.pop())
        queues[country] = queue
    want, items, cases = int(limit * 1.1) + 2, [], 0
    order = sorted(queues)
    while len(items) < want and any(queues.values()):
        for country in order:
            if len(items) >= want or not queues[country]:
                continue
            listing, rows = queues[country].pop(0)
            kind = listing["product_type"][0]["value"]
            if kind == "CELLULAR_PHONE_CASE":
                if cases >= max(1, ABO_PHONE_CASE_SHARE * want):
                    continue
                cases += 1
            path = paths.get(listing["main_image_id"])
            if not path:
                continue
            credit = ABO_CREDIT.format(item=listing.get("item_id", ""), domain=listing.get("domain_name", ""))
            place = where(country_named("GB" if country == "UK" else country), "market")
            items.append((f"abo-{listing['main_image_id']}.jpg".replace("+", "_"), ABO_PICTURE.format(path),
                          [dict(r, credit=credit, **place) for r in rows]))
    counts = collections.Counter(r[2][0].get("place", "not stated") for r in items)
    say("ABO countries: " + ", ".join(f"{c} {n}" for c, n in counts.most_common()))
    fetched = fetch_all(items, workers=8)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Open Images photos and their licences

def oi_photos(s, wanted, urls=OI_IMAGES, sorted_list=False):
    """{image id: (subset, licence, author, page)} for the wanted photos whose own licence is free and that need no
    turning, read from Open Images' image lists. sorted_list: the list is sorted by image id, so reading stops once
    the last wanted id is passed (the 638 MB training list)."""
    photos, last = {}, max(wanted) if wanted else ""
    for url in urls:
        for r in csv.DictReader(oi_lines(s, url)):
            image_id = r["ImageID"]
            if image_id in wanted:
                licence = oi_licence_name(r.get("License") or "", image_id)
                if licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                    photos[image_id] = (r.get("Subset") or "train", licence,
                                        clean(r.get("Author")) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
            if sorted_list and image_id > last:
                break
    return photos


OI_ROW_CREDIT = "Photo by {author}{page}, {licence}; {what} from Open Images V7 (Google), CC BY 4.0"


def oi_credit(photo, what="labels"):
    """The credit line of an Open Images photo."""
    _, licence, author, page = photo
    return OI_ROW_CREDIT.format(author=author, page=f" ({page})" if page else "", licence=licence, what=what)


# ----------------------------------------------------------------- open_images_in_use (visual relationships)

OI_VRD = ("https://storage.googleapis.com/openimages/v6/oidv6-validation-annotations-vrd.csv",
          "https://storage.googleapis.com/openimages/v6/oidv6-test-annotations-vrd.csv")
OI_VRD_TRAIN = "https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-vrd.csv"     # 357 MB
OI_TRAIN_LIST = "https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv"
VRD_SUBJECTS = {"Man": "man", "Woman": "woman", "Boy": "boy", "Girl": "girl", "Person": "person"}
VRD_CHILD = {"Boy", "Girl"}
# The relationships used, most telling first: (the verb phrase before the object, how the object is named).
# "the": "playing the guitar"; "a": "holding a drill"; "bare": "drinking beer"; "none": the verb says it all.
VRD_VERBS = {
    "talk_on_phone": ("talking on", "the"), "plays": ("playing", "the"), "read": ("reading", "a"),
    "cut": ("cutting", "the"), "eat": ("eating", "a"), "drink": ("drinking", "bare"), "hits": ("hitting", "the"),
    "kick": ("kicking", "the"), "throw": ("throwing", "the"), "catch": ("catching", "the"),
    "skateboard": ("riding", "a"), "surf": ("surfing on", "a"), "ski": ("skiing on", "bare"),
    "snowboard": ("snowboarding on", "a"), "ride": ("riding", "a"), "interacts_with": ("using", "a"),
    "holds": ("holding", "a"), "wears": ("wearing", "a"),
}
VRD_ORDER = list(VRD_VERBS)
# "wears" is kept only for worn devices and gear (clothes are in other packs).
VRD_WORN = {"Headphones", "Sunglasses", "Glasses", "Goggles", "Helmet", "Bicycle helmet", "Football helmet",
            "Watch", "Backpack", "Roller skates", "Personal flotation device", "Earrings", "Necklace"}
VRD_NOT_THINGS = re.compile(r"^(Man|Woman|Boy|Girl|Person|Human \w+|Dog|Cat|Horse|Elephant|Monkey|Panda|Alpaca|"
                            r"Hamster|Lizard|Dolphin|Whale|Shark|Brown bear|Crab|Sea lion|Jaguar.*|Dinosaur|"
                            r"Rifle|Shotgun|Handgun|Sword|Cannon|Tank|Dagger|Bow and arrow|Weapon|Missile|Knife)$")
VRD_NAMES = {"Mobile phone": "mobile phone", "Table tennis racket": "table tennis bat",
             "Volleyball (Ball)": "volleyball", "Coffee (drink)": "coffee", "Organ (Musical Instrument)": "organ",
             "Drum": "drum", "Musical keyboard": "keyboard", "Orange (fruit)": "orange", "Ski": "skis",
             "Flying disc": "frisbee", "Football": "football", "Racket": "racket", "Wine glass": "wine glass",
             "Bicycle wheel": "bicycle wheel", "Hiking equipment": "hiking pole", "Bowling equipment": "bowling ball",
             "Stationary bicycle": "exercise bike", "Indoor rower": "rowing machine", "Horizontal bar":
             "horizontal bar"}
VRD_ASK = "What is the person doing with the {thing}?"
VRD_ASK_ALL = "What is the person doing?"


def vrd_thing(label):
    """The plain name of an object label ("Volleyball (Ball)" -> "volleyball")."""
    return VRD_NAMES.get(label) or re.sub(r"\s*\(.*\)", "", label).lower()


def vrd_phrase(relation, label):
    """ "playing the guitar", "holding a drill", "drinking beer", "talking on the phone"."""
    verb, how = VRD_VERBS[relation]
    thing = vrd_thing(label)
    if relation == "talk_on_phone":
        return "talking on the phone"
    if how == "bare" or thing in UNCOUNTED or relation == "wears" and thing.endswith("s"):
        return f"{verb} {thing}"
    if how == "the":
        return f"{verb} the {thing}"
    return f"{verb} {with_article(thing)}"


def vrd_read(s, url, keep):
    """Read one relationship list: {image id: {(object label, object box): {(subject label, relation)}}} for the
    relations kept, person subjects only."""
    names = keep["names"]
    out = keep["pictures"]
    for r in csv.DictReader(oi_lines(s, url)):
        subject, thing = names.get(r["LabelName1"], ""), names.get(r["LabelName2"], "")
        relation = r["RelationshipLabel"]
        if subject not in VRD_SUBJECTS or relation not in VRD_VERBS or not thing or VRD_NOT_THINGS.match(thing):
            continue
        if relation == "wears" and thing not in VRD_WORN:
            continue
        box = (r["XMin2"], r["XMax2"], r["YMin2"], r["YMax2"])
        out.setdefault(r["ImageID"], {}).setdefault((thing, box), set()).add((subject, relation))


def vrd_rows(objects):
    """The rows for one picture from {(object, box): {(subject, relation)}}: one "What is the person doing with the
    ...?" per kind of object (left out when people do different things with the same kind of object), and "What is
    the person doing?" when only one thing is going on. [] when nothing is clear."""
    by_thing = {}
    child = False
    for (thing, _box), pairs in objects.items():
        relation = min((rel for _, rel in pairs), key=VRD_ORDER.index)
        subjects = {sub for sub, rel in pairs if rel == relation}
        specific = sorted(subjects - {"Person"}) or ["Person"]
        child = child or bool(subjects & VRD_CHILD)
        subject = specific[0] if len(specific) == 1 else "Person"
        by_thing.setdefault(thing, set()).add((subject, relation))
    rows = []
    for thing, pairs in sorted(by_thing.items()):
        relations = {rel for _, rel in pairs}
        if len(relations) != 1:
            continue                                      # different people do different things with it
        relation = relations.pop()
        subjects = {sub for sub, _ in pairs}
        who = f"The {VRD_SUBJECTS[subjects.pop()]} is" if len(subjects) == 1 and len(pairs) == 1 else \
            "The people are" if len(pairs) > 1 else "The person is"
        phrase = vrd_phrase(relation, thing)
        rows.append({"question": VRD_ASK.format(thing=vrd_thing(thing)), "answer": f"{who} {phrase}."})
    if len(rows) == 1:
        rows.append({"question": VRD_ASK_ALL, "answer": rows[0]["answer"]})
    return [dict(r, child=True) if child else r for r in rows]


def build_open_images_in_use(limit):
    """The Open Images "in use" pack: reads the relationships people marked on the validation and test sets (12 MB),
    and, when more pictures are wanted than those give, on the training set too (357 MB, with the 638 MB training
    photo list read only as far as needed); keeps photos whose own licence is free; tools, devices and kitchen things
    first (not sports or music), then the rest."""
    s = session()
    names = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            names[line[0]] = line[1]
    keep = {"names": names, "pictures": {}}
    for url in OI_VRD:
        vrd_read(s, url, keep)
    say(f"Open Images relationships: {len(keep['pictures'])} validation and test pictures with a person using "
        f"something")
    photos = oi_photos(s, set(keep["pictures"]))
    if len(photos) < limit * 1.3:
        before = set(keep["pictures"])
        vrd_read(s, OI_VRD_TRAIN, keep)
        train = set(keep["pictures"]) - before
        say(f"Open Images relationships: {len(train)} more training pictures")
        photos.update(oi_photos(s, train, (OI_TRAIN_LIST,), sorted_list=True))
    sport = re.compile(r"\b(ball|racket|bat|board|ski|surf|guitar|violin|cello|trumpet|horn|trombone|saxophone|"
                       r"flute|drum|harp|accordion|piano|keyboard|banjo|oboe|organ|harpsichord|paddle|glove|"
                       r"bicycle|wheel|dumbbell|bar)\b", re.I)
    first, rest = [], []
    for image_id, objects in keep["pictures"].items():
        if image_id not in photos:
            continue
        rows = vrd_rows(objects)
        if not rows:
            continue
        subset = photos[image_id][0]
        credit = oi_credit(photos[image_id], "relationships")
        item = (f"oi-use-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id),
                [dict(r, credit=credit) for r in rows])
        things = " ".join(t for t, _ in objects)
        only_worn = all(rel == "wears" for pairs in objects.values() for _, rel in pairs)
        (rest if sport.search(things) or only_worn else first).append(item)
    say(f"Open Images relationships: {len(first)} pictures of tools, devices and household things in use, "
        f"{len(rest)} of sport, music or only things worn")
    pass_random(93).shuffle(first)
    pass_random(94).shuffle(rest)
    # Household things first, but never more than two thirds sport and music.
    chosen = first[:int(limit * 1.1) + 2]
    chosen += rest[:max(0, int(limit * 1.1) + 2 - len(chosen))]
    fetched = fetch_all(chosen, workers=8)
    pass_random(95).shuffle(fetched)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- open_images_tech (labels checked by hand)

OI_TECH = {
    "Smartphone": "a smartphone", "Feature phone": "a mobile phone with buttons (feature phone)",
    "Personal computer": "a personal computer", "Desktop computer": "a desktop computer",
    "Computer case": "a computer case", "Computer speaker": "computer speakers", "Hard disk drive": "a hard disk drive",
    "Usb flash drive": "a USB stick", "Router (Computing)": "a router", "Wireless router": "a wireless router",
    "Modem": "a modem", "Server": "a computer server", "Webcam": "a webcam", "Digital camera": "a digital camera",
    "Single-lens reflex camera": "an SLR camera", "Instant camera": "an instant camera",
    "Video camera": "a video camera", "Camera lens": "a camera lens", "Tripod": "a tripod", "Projector": "a projector",
    "Video projector": "a video projector", "Image scanner": "a scanner", "Fax": "a fax machine",
    "Typewriter": "a typewriter", "Joystick": "a joystick", "Handheld game console": "a handheld games console",
    "Drone": "a drone", "Robot": "a robot", "Headset": "a headset", "Electronic keyboard": "an electronic keyboard",
    "Mixing console": "a mixing desk", "Radio": "a radio", "Radio receiver": "a radio receiver",
    "Satellite dish": "a satellite dish", "Antenna": "an aerial (antenna)", "Television antenna": "a TV aerial",
    "Ipod": "an iPod", "MP3 Player": "an MP3 player", "Battery charger": "a battery charger",
    "Laptop power adapter": "a laptop charger", "Oscilloscope": "an oscilloscope",
}
OI_ELECTRONIC_PARTS = {
    "Printed circuit board": "a circuit board", "Motherboard": "a computer motherboard",
    "Microcontroller": "a microcontroller board", "Circuit component": "electronic components",
    "Resistor": "resistors", "Capacitor": "capacitors", "Transistor": "transistors", "Video card": "a graphics card",
    "Computer component": "computer parts", "Computer hardware": "computer hardware", "Wire": "wire",
}
OI_BUILDING = {
    "Brick": "bricks", "Brickwork": "brickwork", "Concrete": "concrete", "Cement": "cement",
    "Concrete masonry unit": "concrete blocks", "Concrete mixer": "a concrete mixer", "Lumber": "lumber (timber)",
    "Plywood": "plywood", "Tile": "tile", "Pipe": "a pipe", "Scaffolding": "scaffolding",
    "Wood flooring": "a wooden floor", "Building insulation": "building insulation",
}
OI_WORKSHOP = {
    "Utility knife": "a utility knife", "Grinder": "a grinder", "Lathe": "a lathe", "Welding": "welding",
    "Clamp": "a clamp", "Workbench": "a workbench", "Toolbox": "a toolbox", "Sander": "a sander",
    "Circular saw": "a circular saw", "Plane (Tool)": "a wood plane", "Nut (Fastener)": "nuts (for bolts)",
}
OI_GADGETS = {
    "Espresso machine": "an espresso machine", "Juicer": "a juicer", "Rice cooker": "a rice cooker",
    "Wooden spoon": "a wooden spoon", "Mortar and pestle": "a mortar and pestle", "Pizza cutter": "a pizza cutter",
    "Corkscrew": "a corkscrew", "Coffee grinder": "a coffee grinder", "Toaster oven": "a toaster oven",
    "Deep fryer": "a deep fryer", "Electric kettle": "an electric kettle",
}
OI_TECH_GROUPS = ((OI_TECH, "What technology is in this picture?"),
                  (OI_ELECTRONIC_PARTS, "What electronic parts are in this picture?"),
                  (OI_BUILDING, "What building materials are in this picture?"),
                  (OI_WORKSHOP, "What workshop tools are in this picture?"),
                  (OI_GADGETS, "What kitchen gadgets are in this picture?"))
OI_TECH_ALL = {k: v for group, _ in OI_TECH_GROUPS for k, v in group.items()}
# Labels the other Open Images packs already ask about are never asked here.
OI_TECH_ALL = {k: v for k, v in OI_TECH_ALL.items()
               if k not in OI_HOME and k not in OI_TOOLS and k not in OI_DEVICES and k not in OI_KITCHEN
               and k not in OI_PERSONAL}


def oi_tech_rows(labels, rng):
    """Rows for one picture from {label: 1 (confirmed) or 0 (rejected)}: what of each group is there, one "Is
    there ...?" answered yes and, where people rejected one, one answered no; [] when nothing of this pack is there."""
    yes = {n for n, c in labels.items() if c == 1}
    no = {n for n, c in labels.items() if c == 0}
    rows = []
    for group, question in OI_TECH_GROUPS:
        things = [group[n] for n in group if n in yes and n in OI_TECH_ALL]
        if things:
            rows.append({"question": question, "answer": f"I can see {listed(things[:6])}."})
    if not rows:
        return []
    present = sorted(n for n in yes if n in OI_TECH_ALL)
    thing = OI_TECH_ALL[rng.choice(present)]
    many = thing.endswith("s") and not thing.startswith(("a ", "an "))
    rows.append({"question": f"Is there {thing} in this picture?",
                 "answer": f"Yes, there {'are' if many else 'is'} {thing} in this picture."})
    rejected = sorted(n for n in no if n in OI_TECH_ALL)
    if rejected:
        thing = OI_TECH_ALL[rng.choice(rejected)]
        rows.append({"question": f"Is there {thing} in this picture?",
                     "answer": f"No, I can't see {thing} in this picture."})
    if yes & set(OI_CHILD):
        rows = [dict(r, child=True) for r in rows]
    return rows


def build_open_images_tech(limit):
    """The Open Images technology, electronics, building materials, workshop and kitchen gadget pack: reads the labels
    people checked on the validation and test sets (about 120 MB of lists, read as they download), keeps photos with
    a confirmed label of this pack whose own licence is free, rarest labels first."""
    s, rng = session(), pass_random(97)
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = set(OI_TECH_ALL) | set(OI_CHILD)
    names = {mids[n]: n for n in wanted if n in mids}
    say(f"Open Images: {len(names)} of {len(wanted)} labels found in the class list")
    labels = {}
    for url in OI_LABELS:
        for cells in csv.reader(oi_lines(s, url)):
            if len(cells) == 4 and cells[2] in names:
                try:
                    confidence = round(float(cells[3]))
                except ValueError:
                    continue
                picture = labels.setdefault(cells[0], {})
                name = names[cells[2]]
                picture[name] = confidence if picture.get(name, confidence) == confidence else None
    labels = {k: v for k, v in labels.items() if any(c == 1 and n in OI_TECH_ALL for n, c in v.items())}
    say(f"Open Images: {len(labels)} pictures with a label of this pack confirmed")
    photos = oi_photos(s, set(labels))
    counts = collections.Counter(n for v in labels.values() for n, c in v.items() if c == 1 and n in OI_TECH_ALL)
    items = []
    for image_id in sorted(labels):
        if image_id not in photos:
            continue
        rows = oi_tech_rows(labels[image_id], rng)
        if not rows:
            continue
        rarest = min(counts[n] for n, c in labels[image_id].items() if c == 1 and n in OI_TECH_ALL)
        items.append((rarest, rng.random(), (f"oi-tech-{image_id}.jpg",
                                             OI_PICTURE.format(subset=photos[image_id][0], image_id=image_id),
                                             [dict(r, credit=oi_credit(photos[image_id])) for r in rows])))
    items.sort(key=lambda x: (x[0], x[1]))
    say(f"Open Images: {len(items)} free photos for this pack")
    fetched = fetch_all([x[2] for x in items[:int(limit * 1.1) + 2]], workers=8)
    pass_random(98).shuffle(fetched)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Commons (things, and things in use)

WHAT_Q = "What is this?"
TOOL_USE_Q = "What tool is this, and what is it used for?"
DOING_Q = "What is the person doing?"


def thing(name, use=""):
    """Rows for a category of things: "What is this?" and, with a use, "What tool is this, and what is it used
    for?"."""
    rows = [(WHAT_Q, f"This is {name}." if not name.endswith("s") or name.startswith(("a ", "an ")) else
             f"These are {name}.")]
    if use:
        rows.append((TOOL_USE_Q, f"This is {name}, {use}."))
    return rows


def doing(answer):
    """Rows for a category of people using something."""
    return [(DOING_Q, answer)]


# (category, look in subcategories too, rows, country or "")
COMMONS_THINGS = [
    # electronic parts
    ("Printed circuit boards", False, thing("a printed circuit board")),
    ("Integrated circuits", False, thing("an integrated circuit (a chip)")),
    ("Electrolytic capacitors", False, thing("electrolytic capacitors")),
    ("Ceramic capacitors", False, thing("ceramic capacitors")),
    ("Resistors", True, thing("resistors")), ("Transistors", True, thing("transistors")),
    ("Light-emitting diodes", True, thing("light-emitting diodes (LEDs)")),
    ("Raspberry Pi", True, thing("a Raspberry Pi computer board")),
    ("Breadboards", False, thing("a breadboard", "used to build electronic circuits without soldering")),
    ("RAM modules", False, thing("a computer memory (RAM) module")),
    ("Solid-state drives", False, thing("a solid-state drive (SSD)")),
    ("USB flash drives", False, thing("a USB stick")),
    # devices
    ("Smartphones", False, thing("a smartphone")), ("Feature phones", True, thing("a mobile phone with buttons")),
    ("Laptops", False, thing("a laptop")), ("Desktop computers", False, thing("a desktop computer")),
    ("Computer keyboards", False, thing("a computer keyboard")), ("Computer mice", False, thing("a computer mouse")),
    ("Tablet computers", False, thing("a tablet computer")), ("Smartwatches", False, thing("a smartwatch")),
    ("Webcams", False, thing("a webcam")), ("Digital cameras", False, thing("a digital camera")),
    ("Projectors", False, thing("a projector")), ("Modems", False, thing("a modem")),
    ("Radios", False, thing("a radio")), ("Transistor radios", False, thing("a transistor radio")),
    ("Mobile phone chargers", False, thing("a mobile phone charger")),
    ("Solar panels", False, thing("a solar panel")), ("Solar lamps", False, thing("a solar lamp")),
    ("Solar chargers", False, thing("a solar charger")), ("Electronic waste", False, thing("electronic waste")),
    ("Multimeters", False, thing("a multimeter", "used to measure voltage, current and resistance")),
    ("Oscilloscopes", False, thing("an oscilloscope", "used to show electrical signals as a moving line")),
    # tools commons_tools does not have
    ("Ladders", False, thing("a ladder", "used to reach high places")),
    ("Chainsaws", False, thing("a chainsaw", "used to cut through wood and trees")),
    ("Toolboxes", False, thing("a toolbox")), ("Workbenches", False, thing("a workbench")),
    ("Vises", False, thing("a vice", "used to hold something firmly while you work on it")),
    ("Crowbars", False, thing("a crowbar", "used to lever things apart")),
    ("Trowels", False, thing("a trowel", "used to spread mortar or plaster")),
    ("Torque wrenches", False, thing("a torque wrench", "used to tighten bolts to an exact tightness")),
    ("Pickaxes", False, thing("a pickaxe", "used to break up hard ground or rock")),
    ("Paint rollers", False, thing("a paint roller", "used to paint walls")),
    ("Try squares", False, thing("a try square", "used to mark and check right angles")),
    ("Bolt cutters", False, thing("a pair of bolt cutters", "used to cut chains, bolts and padlocks")),
    ("Heat guns", False, thing("a heat gun", "used to strip paint or soften plastic with hot air")),
    ("Random orbital sanders", False, thing("a random orbital sander", "used to sand surfaces smooth")),
    ("Belt sanders", False, thing("a belt sander", "used to sand surfaces smooth")),
    ("Hammer drills", False, thing("a hammer drill", "used to drill into brick and concrete")),
    ("Socket wrenches", False, thing("a socket wrench", "used to turn nuts and bolts")),
    ("Caulking guns", False, thing("a caulking gun", "used to squeeze out sealant")),
    # building supplies
    ("Bricks", False, thing("bricks")), ("Concrete blocks", False, thing("concrete blocks")),
    ("Roof tiles", False, thing("roof tiles")), ("Rebar", False, thing("reinforcing bars (rebar)")),
    ("Plywood", False, thing("plywood")), ("Cement bags", False, thing("bags of cement")),
    ("Sandbags", False, thing("sandbags")), ("Corrugated iron", False, thing("corrugated iron sheets")),
    ("Copper pipes", False, thing("copper pipes")), ("Circuit breakers", False, thing("a circuit breaker")),
    ("Glass wool", False, thing("glass wool insulation")), ("Ceramic tiles", True, thing("ceramic tiles")),
    # kitchen gadgets commons_kitchen does not have
    ("Clay pots", False, thing("a clay pot")), ("Cooking pots", False, thing("a cooking pot")),
    ("Kitchen knives", False, thing("a kitchen knife", "used to cut food")),
    ("Espresso machines", False, thing("an espresso machine")), ("Sieves", False, thing("a sieve")),
    ("Waffle irons", False, thing("a waffle iron")),
    ("Mortars and pestles", False, thing("a mortar and pestle", "used to grind spices and seeds")),
    ("Measuring cups", False, thing("a measuring cup")), ("Blenders", False, thing("a blender")),
    ("Juicers", False, thing("a juicer")), ("Nutcrackers", False, thing("a nutcracker")),
    ("Coffee grinders", False, thing("a coffee grinder")),
    ("French presses", False, thing("a cafetiere (French press)")),
    ("Tongs", False, thing("a pair of tongs")), ("Cutting boards", False, thing("a chopping board")),
    ("Rocket stoves", False, thing("a rocket stove")), ("Kerosene stoves", False, thing("a kerosene (paraffin) stove")),
    ("Charcoal stoves", False, thing("a charcoal stove")), ("Charcoal irons", False, thing("a charcoal iron")),
    ("Food processors", False, thing("a food processor")), ("Kitchen timers", False, thing("a kitchen timer")),
    ("Measuring spoons", False, thing("measuring spoons")), ("Slow cookers", False, thing("a slow cooker")),
    ("Corkscrews", False, thing("a corkscrew")),
]
COMMONS_IN_USE = [
    ("People using laptops", True, doing("They are using a laptop.")),
    ("People using computers", False, doing("They are using a computer.")),
    ("People using tablet computers", False, doing("They are using a tablet computer.")),
    ("People typing", False, doing("They are typing.")),
    ("People using typewriters", False, doing("They are typing on a typewriter.")),
    ("People with headphones", False, doing("They are wearing headphones.")),
    ("People using hammers", False, doing("They are using a hammer.")),
    ("People using chainsaws", False, doing("They are cutting with a chainsaw.")),
    ("Carpenters at work", False, doing("They are doing carpentry (working with wood).")),
    ("Gardeners at work", False, doing("They are gardening.")),
    ("Sweeping", False, doing("They are sweeping.")),
    ("People with brooms", False, doing("They have a broom.")),
    ("Ironing", False, doing("They are ironing.")),
    ("People with wheelbarrows", False, doing("They are using a wheelbarrow.")),
    ("People on ladders", False, doing("They are up a ladder.")),
    ("People soldering", False, doing("They are soldering.")),
    ("Computer repair", False, doing("A computer is being repaired.")),
    ("Electronics repair", False, doing("Electronics are being repaired.")),
    ("Photographers at work", False, doing("They are taking photographs.")),
    ("People cooking", False, doing("They are cooking.")),
    ("Men cooking", False, doing("He is cooking.")), ("Women cooking", False, doing("She is cooking.")),
    ("People in kitchens", False, doing("They are in a kitchen.")),
    # places the other packs have few of: the category names the country
    ("Cooking in Uganda", True, doing("They are cooking."), "Uganda"),
    ("Cooking in Nigeria", True, doing("They are cooking."), "Nigeria"),
    ("Cooking in Ghana", False, doing("They are cooking."), "Ghana"),
    ("Cooking in Kenya", True, doing("They are cooking."), "Kenya"),
    ("Cooking in Tanzania", True, doing("They are cooking."), "Tanzania"),
    ("Cooking in India", True, doing("They are cooking."), "India"),
    ("Women cooking in India", False, doing("She is cooking."), "India"),
    ("Cooking in Pakistan", True, doing("They are cooking."), "Pakistan"),
    ("Cooking in Bangladesh", True, doing("They are cooking."), "Bangladesh"),
    ("Cooking in Mexico", True, doing("They are cooking."), "Mexico"),
    ("Kitchens in India", True, [(WHAT_Q, "This is a kitchen.")], "India"),
    ("Kitchens in Nigeria", True, [(WHAT_Q, "This is a kitchen.")], "Nigeria"),
    ("Kitchens in Kenya", True, [(WHAT_Q, "This is a kitchen.")], "Kenya"),
    ("Brick making in India", True, doing("They are making bricks."), "India"),
    ("Construction workers in Nigeria", True, doing("They are working on a building site."), "Nigeria"),
    ("Mobile phones in India", True, [(WHAT_Q, "This is a mobile phone.")], "India"),
]


def just_the_title(text, title):
    """Whether a file's "description" only repeats its file name ("Summer in the City 28 October005."), which says
    nothing about the picture."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    return words <= set(re.findall(r"[a-z]+", title.lower()))


def build_commons_list(specs, limit, prefix):
    """A Commons pack from specs [(category, deeper, rows[, country])], as home_packs.build_commons_topic does (the
    categories take turns, so each gets an even share; CC0, public domain and CC BY files only; a real, respectful
    caption or description also gives "Write a short description ..."), and with each row's place: the country a
    category names, else the country at the file's own camera coordinates. Files whose words name a child are
    marked "child"."""
    s, items, seen = session(), [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    queues = [[spec[0], spec[1], spec[2], None, spec[3] if len(spec) > 3 else ""] for spec in order]
    want, rounds = int(limit * 1.15) + 2, 0
    while len(items) < want and queues and rounds < 50:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            category, deeper, rows, titles, country = q
            if titles is None:
                titles = [t for t in category_files(s, category, deeper) if t not in seen]
                pass_random(category).shuffle(titles)
                say(f"Commons {category}: {len(titles)} files")
            batch, q[3] = titles[:share * 2], titles[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            got = 0
            for title, url, credit, text in home_entries(s, batch):
                if got >= share or title in seen:
                    continue
                words = f"{title} {text}"
                if NUDE.search(words):
                    continue
                seen.add(title)
                place = where(country or COMMONS_PLACES.get(title, ""))
                words = LIFE_STAGE.sub(" ", words)
                out = [mark_child({"question": qn, "answer": an, "credit": credit, **place}, words)
                       for qn, an in rows]
                if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text) \
                        and not just_the_title(text, title):
                    out.append(mark_child({"question": ALT_TEXT, "answer": text, "credit": credit, **place}, words))
                items.append((file_name(prefix, title), url, out))
                got += 1
            if not q[3]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    return with_twins(commons_fetch(items[:want])[:limit])


def build_commons_things(limit):
    """The Commons electronics, devices, tools, building supplies and kitchen gadgets pack."""
    return build_commons_list(COMMONS_THINGS, limit, "thing")


def build_commons_in_use(limit):
    """The Commons people-using-things pack."""
    return build_commons_list(COMMONS_IN_USE, limit, "use")


# ----------------------------------------------------------------- Mendeley Data collections

MENDELEY_API = "https://data.mendeley.com/public-api/datasets/{dataset}/files?folder_id={folder}&version={version}"
MENDELEY_FOLDERS = "https://data.mendeley.com/public-api/datasets/{dataset}/folders/{version}"


def mendeley_files(s, dataset, version, folder="root"):
    """The files of one folder of a Mendeley Data dataset: [(file name, download address, size)]. (The listing gives
    at most 1,000 files a folder.)"""
    files = s.get(MENDELEY_API.format(dataset=dataset, folder=folder, version=version), timeout=120).json()
    return [(f["filename"], f["content_details"]["download_url"], f.get("size", 0)) for f in files]


def mendeley_folders(s, dataset, version):
    """{folder name: folder id} of a Mendeley Data dataset."""
    return {f["name"]: f["id"] for f in s.get(MENDELEY_FOLDERS.format(dataset=dataset, version=version),
                                                   timeout=120).json()}


class RangeFile(io.RawIOBase):
    """A file on the web read piece by piece with range requests, so that zipfile can read a few pictures from a very
    large zip (the 9.5 GB brick zip) without downloading all of it."""

    def __init__(self, s, url):
        """Open url (one small request finds its size and where it really is)."""
        super().__init__()
        self.s, self.pos = s, 0
        r = s.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=120)
        r.close()
        self.url = r.url
        self.size = int((r.headers.get("Content-Range") or "/0").rsplit("/", 1)[-1])

    def seekable(self):
        """It can seek."""
        return True

    def readable(self):
        """It can be read."""
        return True

    def tell(self):
        """Where reading is."""
        return self.pos

    def seek(self, offset, whence=0):
        """Move to offset (from the start, here or the end)."""
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def readinto(self, buffer):
        """Read into buffer with one range request (tried three times)."""
        n = min(len(buffer), self.size - self.pos)
        if n <= 0:
            return 0
        for attempt in range(3):
            try:
                r = self.s.get(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + n - 1}"}, timeout=300)
                if r.status_code == 206:
                    data = r.content[:n]
                    buffer[:len(data)] = data
                    self.pos += len(data)
                    return len(data)
            except Exception:  # noqa: BLE001 - tried again
                pass
            time.sleep(5 * (attempt + 1))
        raise OSError("a piece of the file could not be downloaded")


# ---- brick_quality

BRICK_DATASET = "n4wf5g4nrm"
BRICK_FILE = "https://data.mendeley.com/public-files/datasets/n4wf5g4nrm/files/6c2141f7-aea6-475f-a6f8-a5a500207e9e/" \
             "file_downloaded"
BRICK_Q = "What grade is this brick?"
# The authors' own class descriptions, in plain words.
BRICK_CLASSES = {
    "Bricks_1st Class": "This is a first-class brick: an even, deep red or copper colour and sharp, square corners.",
    "Bricks_2nd Class": "This is a second-class brick: a standard brick with small faults in its shape, slight wear "
                        "or small chips.",
    "Bricks_2nd Class (Algae)": "This is a second-class brick with moss, algae or a green film growing on it.",
    "Bricks_3rd Class": "This is a third-class brick: under-burnt, pale pink or yellowish, with soft, crumbling "
                        "edges.",
    "Bricks_Pricate": "This is an over-burnt brick (called 'pricate'): warped, bloated or fused out of shape.",
    "Bricks_Jhama": "This is a very over-burnt brick (called 'jhama'): purplish-black, glassy and full of holes.",
}
BRICK_CREDIT = ("Brick quality grading dataset (Md Mijanur Rahman, Sumaiya Iesmin, Md Hafizur Rahman Noyon, Mehedi "
                "Hasan, Tanzila Reza Rimi and Israt Jahan), Mendeley Data n4wf5g4nrm v1, "
                "https://doi.org/10.17632/n4wf5g4nrm.1, CC BY 4.0")


def build_brick_quality(limit):
    """The brick quality pack: reads the 9.5 GB zip's list of files with range requests, then only the pictures
    taken: the classes and places (three brick fields, two building sites) in turn."""
    s = session()
    z = zipfile.ZipFile(io.BufferedReader(RangeFile(s, BRICK_FILE), 1 << 20))
    groups = collections.defaultdict(list)
    for name in z.namelist():
        if not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        parts = name.split("/")
        site = parts[0]
        kind = parts[1] if len(parts) > 2 else ""
        if kind in BRICK_CLASSES or (not kind and site.lower().startswith("constraction site")):
            groups[(site, kind)].append(name)
    say("Bricks: " + ", ".join(f"{s_}/{k or 'site'} {len(v)}" for (s_, k), v in sorted(groups.items())))
    queues = []
    for key in sorted(groups):
        names = groups[key]
        pass_random(str(key)).shuffle(names)
        queues.append((key, names))
    out = []
    while len(out) < limit and any(names for _, names in queues):
        for (site, kind), names in queues:
            if len(out) >= limit or not names:
                continue
            name = names.pop()
            try:
                data = smaller(z.read(name))
            except Exception:  # noqa: BLE001 - a broken piece is left out
                data = None
            considered(f"brick-{len(out)}.jpg", name, "" if data else "the picture could not be read")
            if not data:
                continue
            if kind:
                row = {"question": BRICK_Q, "answer": BRICK_CLASSES[kind]}
            else:
                row = {"question": WHAT_Q, "answer": "These are bricks at a building site."}
            out.append((f"brick-{len(out):05d}.jpg", data, dict(row, credit=BRICK_CREDIT)))
    return out


# ---- codd_materials

CODD_DATASET, CODD_VERSION = "wds85kt64j", 3
CODD_NAMES = {"brick": "bricks", "bricks": "bricks", "concrete": "concrete", "tile": "tiles", "tiles": "tiles",
              "wood": "wood", "pipe": "pipes", "pipes": "pipes", "plastic": "plastic", "plastics": "plastic",
              "foam": "foam insulation", "foaming insulation": "foam insulation", "insulation": "foam insulation",
              "stone": "stones", "stones": "stones", "plaster board": "plasterboard", "plasterboard": "plasterboard",
              "plaster boards": "plasterboard", "general waste": "general waste", "general_waste": "general waste"}
CODD_Q = "What building materials are in this picture?"
CODD_CREDIT = ("CODD, Construction and Demolition Waste Object Detection Dataset (Demetris Demetriou, Pavlos "
               "Mavromatidis, Michael Petrou and Demetris Nicolaides), Mendeley Data wds85kt64j v3, "
               "https://doi.org/10.17632/wds85kt64j.3, CC BY 4.0")


def codd_label(name):
    """The plain name of a CODD object label, or "" when unknown."""
    key = re.sub(r"[\s_-]+", " ", name.strip().lower())
    return CODD_NAMES.get(key) or CODD_NAMES.get(key.rstrip("s")) or ""


def build_codd_materials(limit):
    """The CODD pack: the photos and their hand-drawn labels (Pascal VOC XML) from the testing, validation and
    training folders (the listing gives 1,000 files, so about 500 photos, of each)."""
    s = session()
    folders = mendeley_folders(s, CODD_DATASET, CODD_VERSION)
    pairs = []
    for folder in ("testing", "validation", "training"):
        if folder not in folders:
            continue
        files = {name: url for name, url, _ in mendeley_files(s, CODD_DATASET, CODD_VERSION, folders[folder])}
        for name, url in files.items():
            stem = name.rsplit(".", 1)[0]
            if name.lower().endswith(".jpg") and f"{stem}.xml" in files:
                pairs.append((f"{folder}-{stem}", url, files[f"{stem}.xml"]))
    pass_random(99).shuffle(pairs)
    say(f"CODD: {len(pairs)} photos with labels listed")
    items = []
    for key, picture, labels in pairs[:int(limit * 1.1) + 2]:
        try:
            root = ElementTree.fromstring(s.get(labels, timeout=120).content)
        except Exception:  # noqa: BLE001 - a broken label file is left out
            continue
        counts = collections.Counter(codd_label(o.findtext("name") or "") for o in root.iter("object"))
        counts.pop("", None)
        if not counts:
            continue
        names = [n for n, _ in counts.most_common()]
        answer = (f"This is building waste at a recycling plant: {listed(names)}." if len(names) > 1 else
                  f"This is building waste at a recycling plant: {names[0]}.")
        items.append((f"codd-{key}.jpg", picture, {"question": CODD_Q, "answer": answer, "credit": CODD_CREDIT,
                                                    **where("Cyprus")}))
    return fetch_all(items, workers=4)[:limit]


# ---- nyuad_materials

NYUAD_DATASET = "zv66h54b8j"
NYUAD_Q = "What building material or surface is this?"
NYUAD_ANSWERS = {
    "CMU wall": "This is a wall of concrete blocks (concrete masonry units).",
    "Chiseled concrete": "This is concrete whose surface has been chiselled rough.",
    "Concrete": "This is a concrete surface.",
    "Gypsum": "This is a gypsum (plaster) surface.",
    "Mesh": "This is a wall covered with mesh.",
    "First coat plaster": "This wall has its first coat of plaster.",
    "Second coat plaster": "This wall has its second coat of plaster.",
}
NYUAD_CREDIT = ("Construction material conditions (Eyob Mengiste, Karunakar Reddy Mannem, Samuel A. Prieto and Borja "
                "Garcia de Soto, S.M.A.R.T. Construction Research Group, NYU Abu Dhabi), Mendeley Data zv66h54b8j v1, "
                "https://doi.org/10.17632/zv66h54b8j.1, CC BY 4.0")


def build_nyuad_materials(limit):
    """The NYU Abu Dhabi construction materials pack: every folder in turn (the photos are large, about 17 MB each,
    so they are fetched four at a time)."""
    s = session()
    folders = mendeley_folders(s, NYUAD_DATASET, 1)
    queues = []
    for folder, answer in NYUAD_ANSWERS.items():
        if folder in folders:
            files = [(n, u) for n, u, _ in mendeley_files(s, NYUAD_DATASET, 1, folders[folder])
                     if n.lower().endswith((".jpg", ".jpeg", ".png"))]
            pass_random(folder).shuffle(files)
            queues.append((answer, files))
    items = []
    while len(items) < limit and any(f for _, f in queues):
        for answer, files in queues:
            if files and len(items) < limit:
                name, url = files.pop()
                items.append(("nyuad-" + re.sub(r"[^\w.-]+", "_", name), url,
                              {"question": NYUAD_Q, "answer": answer, "credit": NYUAD_CREDIT,
                               **where("Abu Dhabi, United Arab Emirates")}))
    return fetch_all(items, workers=4)[:limit]


# ----------------------------------------------------------------- the packs

COMMONS_THINGS_CREDIT = ("Wikimedia Commons {what} categories: captions CC0; pictures CC0, public domain or CC BY, "
                         "each with its author and file page below. https://commons.wikimedia.org")
THINGS_PACKS = {
    "abo_products": (build_abo_products,
                     "Amazon Berkeley Objects (ABO), CC BY 4.0, https://amazon-berkeley-objects.s3.amazonaws.com/"
                     "index.html. Data and images: Amazon.com. Dataset: Matthieu Guillaumin, Thomas Dideriksen, "
                     "Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC Berkeley). "
                     "Changes: photos made smaller; answers written from the listings' type, brand, name, colour "
                     "and material."),
    "open_images_in_use": (build_open_images_in_use,
                           "Open Images V7 (Google): visual relationship annotations, CC BY 4.0, "
                           "https://storage.googleapis.com/openimages/web/index.html. Each photo is CC BY 2.0 "
                           "(checked photo by photo), credited below with its photographer and Flickr page."),
    "open_images_tech": (build_open_images_tech,
                         "Open Images V7 (Google): image-level labels verified by people, CC BY 4.0, "
                         "https://storage.googleapis.com/openimages/web/index.html. Each photo is CC BY 2.0 (checked "
                         "photo by photo), credited below with its photographer and Flickr page."),
    "commons_things": (build_commons_things,
                       COMMONS_THINGS_CREDIT.format(what="electronics, device, tool, building supply and kitchen "
                                                         "gadget")),
    "commons_in_use": (build_commons_in_use, COMMONS_THINGS_CREDIT.format(what="people using things, cooking and "
                                                                               "work")),
    "brick_quality": (build_brick_quality, BRICK_CREDIT + ". Changes: photos made smaller."),
    "codd_materials": (build_codd_materials, CODD_CREDIT + ". Recorded at a recycling plant in Cyprus. Changes: "
                                                           "photos made smaller; answers listed from the labels."),
    "nyuad_materials": (build_nyuad_materials, NYUAD_CREDIT + ". Photos from a building site on the NYU Abu Dhabi "
                                                              "campus. Changes: photos made smaller."),
}

# How many pictures a full build takes from each (about what each offers after the checks, kept so that every pack
# finishes well within the build's time on GitHub).
THINGS_LIMITS = {
    "abo_products": 6000,         # of 85,416 usable listings (21,000 not phone cases); originals about 0.5 MB
    "open_images_in_use": 4000,   # about 1,800 validation and test pictures, the rest from the training set
    "open_images_tech": 4500,     # of 5,187 free photos with a label of this pack confirmed
    "commons_things": 2500,
    "commons_in_use": 1500,
    "brick_quality": 1500,        # of 9,808 (about 1 MB each, read from the zip by range requests)
    "codd_materials": 1400,       # the about 1,500 photos the listing gives
    "nyuad_materials": 208,       # all of them (17 MB each: about 3.5 GB fetched)
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one things pack builder.")
    parser.add_argument("key", choices=sorted(THINGS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = THINGS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"places: " + ", ".join(f"{p} {n}" for p, n in places.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
