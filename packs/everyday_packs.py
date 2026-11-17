"""Pack builders for household objects and animals, used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"}. A picture that has more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins), so the zip holds each picture only once. The limit counts
pictures.

Household objects:
  open_images_objects  Google Open Images V7 (validation and test sets): photos with household labels people checked by
                       hand (labels CC BY 4.0; each photo CC BY 2.0, checked photo by photo, photographer named).
                       "What objects are in this picture?" and "Is there a remote control in this picture?" (yes from
                       a label people confirmed, no from a label people checked and rejected).
  orbit                ORBIT (City, University of London and Microsoft, CC BY 4.0): videos that blind and low-vision
                       people filmed of their own things (keys, remote controls, white canes, guide-dog harnesses ...),
                       a few frames from each. Clean videos: "What is this?" and "Is this a good photo of the object?"
                       (from the dataset's hand-marked blur, framing, lighting and covering problems). Cluttered
                       videos: "Where is the ... in this picture?" (from the hand-drawn box).
  core50               CORe50 (Lomonaco and Maltoni, 2017, CC BY 4.0): 50 small objects of 10 kinds (phones, remote
                       controls, glasses, scissors, cups, cans ...) held in a hand in 11 indoor and outdoor places.
                       "What is this?"

Animals:
  lila_camera_traps    Camera-trap pictures from 21 LILA BC collections (lila.science), each checked to be under the
                       Community Data License Agreement, permissive variant (CDLA-Permissive-1.0): species named by
                       people, mapped to scientific names by LILA. Empty frames, frames with people and frames in which
                       MegaDetector finds no animal are left out. "What animal is in this picture?"
  gbif_species         GBIF (gbif.org) observations with a photo whose own licence is CC0 or CC BY (the photo's licence
                       is checked, not only the record's), from national recording schemes, museums and other
                       platforms; iNaturalist records are left out (the inaturalist pack has them). Birds, mammals,
                       reptiles, amphibians, fish, insects, spiders, molluscs, plants and fungi, at most two photos a
                       species. "What bird is this?" and so on.
  commons_breeds       Wikimedia Commons breed categories (dogs, cats, horses, cattle, sheep, goats, pigs, chickens,
                       rabbits): pictures CC0, public domain or CC BY (never BY-SA), author credited. "What breed of dog
                       is this?"

    python packs/everyday_packs.py orbit --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import random
import re
import struct
import sys
import time
import zipfile
import zlib

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import out_of_time, session, clean, smaller, fetch_all, say, article  # noqa: F401
from food_packs import (sentence, listed, with_twins, count_pictures, oi_lines, oi_licence_name,  # noqa: F401
                        commons_members, commons_entries, OI_LABELS, OI_CLASSES, OI_IMAGES, OI_PICTURE,
                        COMMONS_NOT_FOOD, commons_place)
from places import where, country_named, place_name


# ----------------------------------------------------------------- shared helpers

def a_or_an(phrase):
    """ "a" or "an" before a phrase, knowing that "USB", "UNO" and "one" start with a "you" or "won" sound."""
    word = phrase.split()[0] if phrase.split() else ""
    first = word.lower()
    if first.startswith(("usb", "uno", "one", "uni", "eu", "ewe", "ura", "ure")):
        return "a"
    if len(word) >= 2 and word.isupper() and word[0] in "AEFHILMNORSX":        # letters said one by one: "an RNIB"
        return "an"
    return article(phrase)


PLURAL_SAME = {"deer", "sheep", "moose", "bison", "fish", "elk", "eland", "springbok", "impala", "duiker", "steenbok",
               "kudu", "hartebeest", "wildebeest", "grysbok", "oribi", "klipspringer", "reedbuck", "bushbuck",
               "waterbuck", "gemsbok", "cattle", "swine", "grouse", "quail", "squid", "salmon", "trout", "aircraft"}
PLURAL_ODD = {"mouse": "mice", "goose": "geese", "wolf": "wolves", "calf": "calves", "ox": "oxen", "foot": "feet",
              "child": "children", "person": "people", "tooth": "teeth", "louse": "lice", "human": "humans"}


def plural(name):
    """The plural of an animal's English name ("red fox" -> "red foxes", "house mouse" -> "house mice")."""
    words = name.split()
    if not words:
        return name
    last = words[-1]
    low = last.lower()
    if low in PLURAL_SAME or low.endswith(("deer", "fish", "sheep")):
        new = last
    elif low in PLURAL_ODD:
        new = PLURAL_ODD[low]
    elif low.endswith(("s", "x", "z", "ch", "sh")):
        new = last + "es"
    elif low.endswith("y") and low[-2:-1] not in "aeiou":
        new = last[:-1] + "ies"
    else:
        new = last + "s"
    return " ".join(words[:-1] + [new])


NUMBERS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def number_word(n):
    """ "two" for 2, "12" for 12."""
    return NUMBERS[n] if 0 <= n < len(NUMBERS) else str(n)


def is_greyscale(jpeg):
    """True when a picture is black and white (a camera trap's infrared night picture): its colours hardly differ."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(jpeg)).convert("RGB").resize((64, 64))
    except Exception:  # noqa: BLE001 - not known: treated as colour
        return False
    raw = img.tobytes()
    diff = sum(max(raw[i:i + 3]) - min(raw[i:i + 3]) for i in range(0, len(raw), 3)) / (64 * 64)
    return diff < 4


# ----------------------------------------------------------------- reading single files from a large remote zip

class RemoteZip:
    """A zip file on a web server that allows byte ranges (figshare, a university server), read without downloading
    it: its central directory (the list of files at the end) is read as it downloads, and single files are fetched
    with range requests. Used for ORBIT (zips of 6 to 50 GB) and CORe50 (28 GB). Figshare sends the zip from a
    signed address that expires, so the address is looked up again when a request is refused."""

    def __init__(self, url):
        self.url, self.s = url, session()
        self.resolve()

    def resolve(self):
        """Follow the redirect to the real address and learn the zip's size."""
        r = self.s.get(self.url, headers={"Range": "bytes=0-0"}, timeout=120, allow_redirects=True)
        r.raise_for_status()
        self.real = r.url
        self.size = int(r.headers["Content-Range"].split("/")[1])

    def get(self, start, end, stream=False):
        """Bytes start..end (inclusive), trying again after a new address lookup or a pause."""
        for attempt in range(4):
            try:
                r = self.s.get(self.real, headers={"Range": f"bytes={start}-{end}"}, timeout=300, stream=stream)
                if r.status_code == 206:
                    return r if stream else r.content
                if r.status_code in (400, 401, 403):
                    self.resolve()
            except Exception:  # noqa: BLE001 - network trouble: wait and try again
                time.sleep(5 * (attempt + 1))
        raise RuntimeError(f"Could not read bytes {start}-{end} of {self.url}")

    def directory(self):
        """(where the central directory starts, its length, how many entries) from the zip's end records."""
        tail_start = max(0, self.size - 70000)
        tail = self.get(tail_start, self.size - 1)
        at = tail.rfind(b"PK\x06\x06")                                  # zip64 end record (zips over 4 GB)
        if at >= 0:
            count, length, start = struct.unpack("<QQQ", tail[at + 32:at + 56])
        else:
            at = tail.rfind(b"PK\x05\x06")
            count, length, start = struct.unpack("<HII", tail[at + 10:at + 20])
        return start, length, count

    def entries(self):
        """Every entry of the zip as (name, local header offset, compressed size, method), read in a stream."""
        start, length, _ = self.directory()
        r = self.get(start, start + length - 1, stream=True)
        buf = b""
        for chunk in r.iter_content(1 << 22):
            buf += chunk
            at = 0
            while len(buf) - at >= 46 and buf[at:at + 4] == b"PK\x01\x02":
                method = struct.unpack("<H", buf[at + 10:at + 12])[0]
                csize, usize = struct.unpack("<II", buf[at + 20:at + 28])
                nl, xl, cl = struct.unpack("<HHH", buf[at + 28:at + 34])
                offset = struct.unpack("<I", buf[at + 42:at + 46])[0]
                if len(buf) - at < 46 + nl + xl + cl:
                    break
                name = buf[at + 46:at + 46 + nl].decode("utf-8", "replace")
                extra = buf[at + 46 + nl:at + 46 + nl + xl]
                q = 0
                while q + 4 <= len(extra):                                # zip64 sizes and offset, where used
                    hid, hl = struct.unpack("<HH", extra[q:q + 4])
                    if hid == 1:
                        body, k = extra[q + 4:q + 4 + hl], 0
                        values = []
                        for v in (usize, csize, offset):
                            if v == 0xFFFFFFFF:
                                values.append(struct.unpack("<Q", body[k:k + 8])[0])
                                k += 8
                            else:
                                values.append(v)
                        usize, csize, offset = values
                    q += 4 + hl
                yield name, offset, csize, method
                at += 46 + nl + xl + cl
            buf = buf[at:]

    def read(self, offset, csize, method):
        """One file's bytes, from its local header offset and compressed size."""
        data = self.get(offset, offset + 30 + 1024 + csize)
        nl, xl = struct.unpack("<HH", data[26:30])
        body = data[30 + nl + xl:30 + nl + xl + csize]
        if len(body) < csize:
            body = self.get(offset + 30 + nl + xl, offset + 30 + nl + xl + csize - 1)
        return zlib.decompressobj(-15).decompress(body) if method == 8 else body


def fetch_from_zip(zipped, items, workers=6):
    """Pictures from a RemoteZip: items are (name, (offset, size, method), rows); returns [(name, JPEG, rows)]."""
    import concurrent.futures

    def one(item):
        """One picture, or None."""
        name, where, rows = item
        try:
            data = smaller(zipped.read(*where))
        except Exception:  # noqa: BLE001 - left out
            return None
        return (name, data, rows) if data else None

    out = []
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for done, result in enumerate(pool.map(one, items), 1):
            if result:
                out.append(result)
            if done % 500 == 0:
                say(f"  {done} of {len(items)} pictures read ({len(out)} usable)")
    return out


# ----------------------------------------------------------------- Open Images V7: household objects

# Household labels with the plain words used in the answer (singular: image-level labels do not say how many there
# are). Labels people confirm as missing give the "No" answers.
OI_HOME = {
    # things a blind person often looks for
    "Remote control": "remote control", "Mobile phone": "mobile phone", "Key": "key", "Glasses": "glasses",
    "Sunglasses": "sunglasses", "Wallet": "wallet", "Handbag": "handbag", "Backpack": "backpack", "Watch": "watch",
    "Headphones": "headphones", "Umbrella": "umbrella", "Cane": "walking stick", "Wheelchair": "wheelchair",
    "Walker": "walking frame", "Crutch": "crutch", "Credit card": "bank card", "Banknote": "banknote", "Coin": "coin",
    "Medicine": "medicine", "Pill": "pills", "Capsule": "capsules", "Pharmaceutical drug": "medicine",
    "Thermometer": "thermometer", "Syringe": "syringe", "Bandage": "bandage", "Band-aid": "sticking plaster",
    # kitchen
    "Microwave oven": "microwave oven", "Refrigerator": "fridge", "Oven": "oven", "Gas stove": "gas cooker",
    "Stove": "cooker", "Toaster": "toaster", "Kettle": "kettle", "Coffeemaker": "coffee maker", "Blender": "blender",
    "Food processor": "food processor", "Mixer": "food mixer", "Waffle iron": "waffle iron",
    "Pressure cooker": "pressure cooker", "Slow cooker": "slow cooker", "Dishwasher": "dishwasher",
    "Mug": "mug", "Coffee cup": "coffee cup", "Plate": "plate", "Bowl": "bowl", "Saucer": "saucer",
    "Mixing bowl": "mixing bowl", "Fork": "fork", "Spoon": "spoon", "Kitchen knife": "kitchen knife", "Knife": "knife",
    "Chopsticks": "chopsticks", "Frying pan": "frying pan", "Wok": "wok", "Cutting board": "chopping board",
    "Spatula": "spatula", "Ladle": "ladle", "Whisk": "whisk", "Measuring cup": "measuring jug",
    "Can opener": "tin opener", "Bottle opener": "bottle opener", "Bottle": "bottle", "Water bottle": "water bottle",
    "Baby bottle": "baby bottle", "Wine glass": "wine glass", "Jug": "jug", "Pitcher (Container)": "jug",
    "Teapot": "teapot", "Jar": "jar", "Tin can": "tin can", "Salt and pepper shakers": "salt and pepper shakers",
    "Spice rack": "spice rack", "Drinking straw": "drinking straw", "Napkin": "napkin", "Tablecloth": "tablecloth",
    "Paper towel": "kitchen roll", "Countertop": "worktop", "Sink": "sink",
    # furniture and the house
    "Chair": "chair", "Table": "table", "Kitchen & dining room table": "dining table", "Coffee table": "coffee table",
    "Couch": "sofa", "Bed": "bed", "Desk": "desk", "Stool": "stool", "Bench": "bench", "Shelf": "shelf",
    "Bookcase": "bookcase", "Cabinetry": "cupboard", "Chest of drawers": "chest of drawers", "Wardrobe": "wardrobe",
    "Lamp": "lamp", "Light bulb": "light bulb", "Ceiling fan": "ceiling fan", "Clock": "clock",
    "Alarm clock": "alarm clock", "Wall clock": "wall clock", "Mirror": "mirror", "Pillow": "cushion",
    "Blanket": "blanket", "Duvet": "duvet", "Bed sheet": "bed sheet", "Curtain": "curtain",
    "Window blind": "window blind", "Door": "door", "Door handle": "door handle", "Window": "window",
    "Stairs": "stairs", "Fireplace": "fireplace", "Radiator": "radiator", "Light switch": "light switch",
    "Power plugs and sockets": "plug socket", "Fire extinguisher": "fire extinguisher",
    "Smoke detector": "smoke alarm", "Thermostat": "thermostat", "Picture frame": "picture frame", "Vase": "vase",
    "Houseplant": "houseplant", "Flowerpot": "flowerpot", "Candle": "candle", "Box": "box", "Basket": "basket",
    "Laundry basket": "laundry basket", "Plastic bag": "plastic bag", "Bucket": "bucket", "Broom": "broom",
    "Mop": "mop", "Vacuum cleaner": "vacuum cleaner", "Washing machine": "washing machine",
    "Ironing board": "ironing board", "Clothes hanger": "clothes hanger", "Ladder": "ladder",
    "Waste container": "bin",
    # bathroom
    "Toilet": "toilet", "Toilet paper": "toilet paper", "Bathtub": "bath", "Shower": "shower", "Towel": "towel",
    "Toothbrush": "toothbrush", "Soap dispenser": "soap dispenser", "Hair dryer": "hair dryer", "Comb": "comb",
    "Hairbrush": "hairbrush", "Razor": "razor", "Cosmetics": "make-up", "Lipstick": "lipstick", "Perfume": "perfume",
    # electronics and the office
    "Laptop": "laptop", "Computer keyboard": "computer keyboard", "Computer mouse": "computer mouse",
    "Computer monitor": "computer screen", "Tablet computer": "tablet computer", "Television": "television",
    "Telephone": "telephone", "Corded phone": "corded telephone", "Camera": "camera", "Printer": "printer",
    "Loudspeaker": "loudspeaker", "Microphone": "microphone", "Video game console": "games console",
    "Game controller": "game controller", "Calculator": "calculator", "Battery": "battery", "Cable": "cable",
    "Flashlight": "torch", "Book": "book", "Notebook": "notebook", "Paper": "paper", "Envelope": "envelope",
    "Pen": "pen", "Pencil": "pencil", "Stapler": "stapler", "Scissors": "scissors",
    # tools
    "Hammer": "hammer", "Screwdriver": "screwdriver", "Wrench": "spanner", "Sewing machine": "sewing machine",
    # clothes and accessories
    "Shoe": "shoe", "Boot": "boot", "Sandal": "sandal", "Slipper": "slipper", "High heels": "high-heeled shoe",
    "Sock": "sock", "Hat": "hat", "Glove": "glove", "Scarf": "scarf", "Belt": "belt", "Tie": "tie",
    "Jacket": "jacket", "Coat": "coat", "Dress": "dress", "Jeans": "jeans", "Trousers": "trousers",
    "Sweater": "jumper", "Necklace": "necklace", "Bracelet": "bracelet", "Suitcase": "suitcase",
    # toys and games
    "Teddy bear": "teddy bear", "Doll": "doll", "Dice": "dice", "Board game": "board game",
    "Jigsaw puzzle": "jigsaw puzzle", "Pacifier": "dummy", "Diaper": "nappy",
}
# A label left out of the answer when a more specific one is there ("dining table", not "table and dining table").
OI_HOME_COVERED = {"Table": {"Kitchen & dining room table", "Coffee table", "Desk"},
                   "Clock": {"Alarm clock", "Wall clock"}, "Knife": {"Kitchen knife"},
                   "Telephone": {"Mobile phone", "Corded phone"}, "Bottle": {"Water bottle", "Baby bottle"},
                   "Stove": {"Gas stove"}, "Jug": {"Pitcher (Container)"}, "Bowl": {"Mixing bowl"},
                   "Shoe": {"High heels", "Boot", "Sandal", "Slipper"}, "Medicine": {"Pill", "Capsule"},
                   "Pharmaceutical drug": {"Pill", "Capsule", "Medicine"}, "Basket": {"Laundry basket"},
                   "Coat": {"Jacket"}, "Glasses": {"Sunglasses"}}
# Group labels: read so that the label lists are complete, never named (a photo needs a specific household label).
OI_GROUPS = {"Kitchen utensil": "kitchen utensil", "Kitchen appliance": "kitchen appliance", "Furniture": "furniture",
             "Clothing": "clothing", "Tool": "tool", "Toy": "toy", "Container": "container",
             "Bathroom accessory": "bathroom item", "Electronic device": "electronic device",
             "Tableware": "tableware", "Kitchenware": "kitchenware", "Home appliance": "home appliance",
             "Footwear": "footwear", "Office supplies": "office supplies", "Medical equipment": "medical equipment",
             "Hand tool": "hand tool", "Power tool": "power tool"}
# How "Is there a ... ?" names a thing (a pair of, some ...), where "a" + the word does not fit.
OI_ASK_AS = {"Glasses": "a pair of glasses", "Sunglasses": "a pair of sunglasses", "Headphones": "headphones",
             "Pill": "pills", "Capsule": "capsules", "Medicine": "medicine", "Pharmaceutical drug": "medicine",
             "Chopsticks": "chopsticks", "Salt and pepper shakers": "salt and pepper shakers",
             "Paper towel": "kitchen roll", "Stairs": "stairs", "Toilet paper": "toilet paper",
             "Cosmetics": "make-up", "Perfume": "perfume", "Paper": "paper", "Scissors": "a pair of scissors",
             "Jeans": "a pair of jeans", "Trousers": "a pair of trousers", "Dice": "dice", "Jigsaw puzzle":
             "a jigsaw puzzle"}
# Things a blind person often asks about: these are asked "Is there ... ?" first.
OI_ASK_FIRST = ("Remote control", "Mobile phone", "Key", "Glasses", "Sunglasses", "Wallet", "Handbag", "Backpack",
                "Watch", "Headphones", "Mug", "Coffee cup", "Bottle", "Kettle", "Scissors", "Book", "Laptop",
                "Medicine", "Pill", "Cane", "Door", "Chair", "Toilet", "Toothbrush", "Shoe", "Umbrella")
OI_ASK_OBJECTS = "What objects are in this picture?"
OI_CREDIT = "Photo by {author}{page}, {licence}; labels from Open Images V7 (Google), CC BY 4.0"


def oi_thing(label):
    """ "a remote control", "a pair of glasses" or "medicine": how a question names a label's thing."""
    if label in OI_ASK_AS:
        return OI_ASK_AS[label]
    word = OI_HOME[label]
    return f"{a_or_an(word)} {word}"


def oi_home_rows(labels, rng):
    """Rows for one picture from its {label: 1 (people confirmed it) or 0 (people rejected it)}: the objects named,
    one "Is there ...?" that is answered yes and one answered no. [] when no household thing is confirmed."""
    present = {n for n, c in labels.items() if c == 1}
    absent = {n for n, c in labels.items() if c == 0}
    things = [n for n in OI_HOME if n in present]
    if not things:
        return []
    words = []
    for n in things:
        if OI_HOME_COVERED.get(n, set()) & present:
            continue
        if OI_HOME[n] not in words:
            words.append(OI_HOME[n])
    rows = [{"question": OI_ASK_OBJECTS, "answer": f"Objects in this picture: {listed(words[:8])}"
                                                    f"{' and more' if len(words) > 8 else ''}."}]
    first = [n for n in OI_ASK_FIRST if n in present]
    yes = first[0] if first and rng.random() < 0.6 else rng.choice(things)
    thing = oi_thing(yes)
    rows.append({"question": f"Is there {thing} in this picture?", "answer": f"Yes, there is {thing} in this picture."
                 if not thing.endswith("s") or thing.startswith("a ") else f"Yes, there are {thing} in this picture."})
    no = [n for n in absent if n in OI_HOME and OI_HOME[n] not in words]
    if no:
        no.sort()
        thing = oi_thing(rng.choice(no))
        rows.append({"question": f"Is there {thing} in this picture?",
                     "answer": f"No, I can't see {thing} in this picture."})
    return rows


def build_open_images_objects(limit):
    """The Open Images household pack's pictures: reads the labels people checked on the validation and test sets
    (about 120 MB of lists, read as they download), keeps photos with a confirmed household label whose own licence
    is free and that need no turning, and fetches them."""
    s, rng = session(), random.Random(51)
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = set(OI_HOME) | set(OI_GROUPS)
    names = {mids[n]: n for n in wanted if n in mids}
    say(f"Open Images: {len(names)} of {len(wanted)} household labels found in the class list")
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
    say(f"Open Images: {len(labels)} pictures with a household label checked")
    photos = {}
    for url in OI_IMAGES:
        for r in csv.DictReader(oi_lines(s, url)):
            licence = oi_licence_name(r.get("License") or "", r["ImageID"] if r["ImageID"] in labels else None)
            if r["ImageID"] in labels and licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[r["ImageID"]] = (r["Subset"], licence, clean(r.get("Author")) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
    items = []
    for image_id in sorted(labels):
        if image_id not in photos:
            continue
        rows = oi_home_rows(labels[image_id], rng)
        if not rows:
            continue
        subset, licence, author, page = photos[image_id]
        credit = OI_CREDIT.format(author=author, page=f" ({page})" if page else "", licence=licence)
        items.append((f"oi-home-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id),
                      [dict(r, credit=credit) for r in rows]))
    say(f"Open Images: {len(items)} free household photos")
    random.Random(52).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=8)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- ORBIT (blind people's own videos)

ORBIT_ZIPS = {"validation": "https://ndownloader.figshare.com/files/27188237",     # 6 GB
              "test": "https://ndownloader.figshare.com/files/27346766",           # 26 GB
              "train": "https://ndownloader.figshare.com/files/27189155"}          # 50 GB
ORBIT_ANNOTATIONS = "https://raw.githubusercontent.com/microsoft/ORBIT-Dataset/master/data/orbit_extra_annotations.zip"
ORBIT_CREDIT = ("ORBIT dataset (Massiceti, Zintgraf, Bronskill, Theodorou, Harris, Cutrell, Morrison, Hofmann and "
                "Stumpf, 2021), City, University of London and Microsoft, CC BY 4.0, "
                "https://doi.org/10.25383/city.14294597")
# The collectors' own names for their things, tidied: spelling slips mended, private or unclear names left out (None).
ORBIT_FIX = {
    "white came": "white cane", "white mobility came": "white mobility cane", "p939411 white cane": "white cane",
    "apple wath": "Apple Watch", "walletv": "wallet", "remote comtrol": "remote control", "control": "remote control",
    "clickr": "remote control", "nobile phone stand": "mobile phone stand", "migenta marker": "magenta marker",
    "braille displat": "braille display", "favourite earings": "earrings", "sisters car": "car",
    "pro": "pair of AirPods Pro", "cup again": "cup", "sport bago": "sports bag", "numb bag": "bum bag",
    "tred mill": "treadmill", "tilly hat upside down": "Tilley hat", "tilly hat": "Tilley hat",
    "i phone 11 pro": "iPhone 11 Pro", "jd whisky bottle": "Jack Daniel's whisky bottle", "watering": "watering can",
    "mobility": "mobility cane", "1 cup measuring cup": "one-cup measuring cup", "12 measuring cup": "measuring cup",
    "13 measuring cup": "measuring cup", "14 measuring cup": "measuring cup", "buckleys": "bottle of Buckley's",
    "spacer": "inhaler spacer", "sennheiser pxc 350-2": "pair of Sennheiser PXC 350-2 headphones",
    "muse s headband": "Muse S headband", "t. v. remote control": "TV remote control", "i d wallet": "ID wallet",
    "blue tooth keyboard": "Bluetooth keyboard", "skip prep": None, "flee": None, "dog poo": None,
    "cannabis vape battery": None, "condom box": None, "aspirin vs tylenol": None, "make up": "make-up",
    "orbit braille reader and notetaker": "Orbit Reader braille notetaker", "dogs": "dogs",
    "front door from outside": "front door", "front door to house": "front door", "shelf unit with things":
    "shelf unit", "washing machine setting": "washing machine dial", "tumble dry setting washing machine":
    "washing machine dial", "usb": "USB stick", "mouse": "computer mouse", "remote tv": "TV remote",
    "pen friend": "PenFriend audio labeller", "dogs lead": "dog lead", "wheely bin": "wheelie bin",
    "airpod pro": "pair of AirPods Pro", "airpod pros case": "AirPods Pro case", "iphone air pods": "AirPods",
    "glasses": "pair of glasses", "eye glasses": "pair of glasses", "reading glasses": "pair of reading glasses",
    "dark glasses": "pair of dark glasses", "sunglasses": "pair of sunglasses", "scissors": "pair of scissors",
    "wraparound sunglasses": "pair of wraparound sunglasses", "headphones": "pair of headphones",
    "tweezers": "pair of tweezers", "secateurs": "pair of secateurs", "spectacles": "pair of glasses",
    "pex plumbers pliers": "pair of PEX plumber's pliers", "gloves": "pair of gloves",
    "winter gloves": "pair of winter gloves",
}
ORBIT_WORDS = {"iphone": "iPhone", "ipad": "iPad", "ipod": "iPod", "airpod": "AirPod", "airpods": "AirPods",
               "earpods": "EarPods", "apple": "Apple", "bose": "Bose", "tv": "TV", "usb": "USB", "ps4": "PS4",
               "bluetooth": "Bluetooth", "samsung": "Samsung", "amazon": "Amazon", "virgin": "Virgin", "sky": "Sky",
               "rnib": "RNIB", "nike": "Nike", "uno": "UNO", "dab": "DAB", "orbit": "Orbit", "victor": "Victor",
               "ottawa": "Ottawa", "mediterranean": "Mediterranean", "himalayan": "Himalayan",
               "phillips": "Phillips", "covid": "COVID", "pinesol": "Pine-Sol", "mountain": "Mountain",
               "dew": "Dew", "q": "Q", "smarttv": "smart TV", "fire": "Fire", "stick": "stick"}
ORBIT_UNCOUNTED = {"tea", "rice", "money", "make-up", "hand gel", "mustard", "prosecco", "valve oil", "slide grease",
                   "mediterranean sea salt", "pink himalayan salt", "fish food", "medication", "cranberry cream tea"}
ORBIT_ISSUES = {"blur_issue": "the picture is blurred", "underexposed_issue": "the picture is too dark",
                "overexposed_issue": "the picture is too bright",
                "framing_issue": "the object is partly outside the picture",
                "occlusion_issue": "something, such as a hand, covers part of the object",
                "viewpoint_issue": "the object is seen from an unusual angle"}
ORBIT_ASK_WHAT, ORBIT_ASK_GOOD = "What is this?", "Is this a good photo of the object?"


def orbit_name(raw):
    """(the thing's name, True when it is plural or uncounted) from a collector's own name ("my front door" ->
    ("front door", False)), or None for a name that is unclear or too private to use."""
    name = " ".join(raw.lower().replace("_", " ").split())
    name = re.sub(r"^(my|your|our|his|her|personal) ", "", name)
    name = ORBIT_FIX.get(name, name)
    if not name:
        return None
    if name.startswith("pair of "):
        return name, False
    words = [ORBIT_WORDS.get(w, w) for w in name.split()]
    name = " ".join(words)
    head = re.split(r" (?:with|of|for|in|on|from) ", name)[0]           # "vase with flowers": the vase counts
    last = head.split()[-1].lower()
    many = name.lower() in ORBIT_UNCOUNTED or (last.endswith("s") and not last.endswith(("ss", "us", "is")))
    return name, many


def orbit_this(name, many):
    """ "This is a front door." / "These are house keys." / "This is make-up." """
    if name.lower() in ORBIT_UNCOUNTED or name in ("money",):
        return f"This is {name}."
    if many:
        return f"These are {name}."
    return f"This is {a_or_an(name)} {name}."


def orbit_where(name, many, box, side=1080):
    """Where the thing is in a cluttered frame, from its hand-drawn box (x, y, w, h on a 1080 x 1080 frame)."""
    cx, cy = (box["x"] + box["w"] / 2) / side, (box["y"] + box["h"] / 2) / side
    across = "left" if cx < 1 / 3 else "right" if cx > 2 / 3 else ""
    down = "top" if cy < 1 / 3 else "bottom" if cy > 2 / 3 else ""
    if across and down:
        place = f"at the {down} {across}"
    elif down:
        place = f"at the {down}"
    elif across:
        place = f"on the {across}"
    else:
        place = "in the middle"
    subject = "the " + (name[len("pair of "):] if name.startswith("pair of ") else name)
    verb = "are" if many or name.startswith("pair of ") else "is"
    text = f"{subject[0].upper() + subject[1:]} {verb} {place} of the picture."
    area = box["w"] * box["h"] / side / side
    if area > 0.4:
        text += " It fills much of the picture." if verb == "is" else " They fill much of the picture."
    elif area < 0.03:
        text += " It is quite small in the picture." if verb == "is" else " They are quite small in the picture."
    return text


def orbit_quality(flags):
    """The answer to "Is this a good photo of the object?" from a clean frame's marked problems."""
    problems = [text for key, text in ORBIT_ISSUES.items() if flags.get(key)]
    if not problems:
        return "Yes: the object is in focus, well lit and fully in the picture."
    return sentence("not quite: " + listed(problems))


def orbit_pick(frames, rng):
    """For a video's {frame name: annotation}: the frames to use, as [(frame name, annotation)]. Clean videos: one
    frame without problems and one with problems where there are such (else two apart). Cluttered videos: two
    frames with the thing's box, a third and two thirds of the way through."""
    usable = sorted((k, v) for k, v in frames.items() if not v.get("object_not_present_issue"))
    if not usable:
        return []
    if "object_bounding_box" in usable[0][1]:
        boxed = [(k, v) for k, v in usable if v.get("object_bounding_box")]
        return [boxed[int(len(boxed) * f)] for f in (1 / 3, 2 / 3)] if len(boxed) >= 6 else boxed[:1]
    good = [(k, v) for k, v in usable if not any(v.get(i) for i in ORBIT_ISSUES)]
    bad = [(k, v) for k, v in usable if any(v.get(i) for i in ORBIT_ISSUES)]
    out = [rng.choice(good)] if good else []
    if bad:
        out.append(rng.choice(bad))
    while len(out) < 2 and len(usable) > len(out):
        extra = usable[int(len(usable) * (len(out) + 1) / 3)]
        if extra not in out:
            out.append(extra)
        else:
            break
    return out


def build_orbit(limit):
    """The ORBIT pack's pictures. Reads the dataset's frame annotations (a 14 MB zip from its GitHub repository), picks
    two frames of each video, finds them in the central directory of the figshare zips (validation, then test, then
    train; the zips are never downloaded whole) and reads just those frames."""
    s, rng = session(), random.Random(53)
    notes = zipfile.ZipFile(io.BytesIO(s.get(ORBIT_ANNOTATIONS, timeout=600).content))
    out = []
    for split, url in ORBIT_ZIPS.items():
        if len(out) >= limit:
            break
        members = [m for m in notes.namelist() if m.startswith(split + "/") and m.endswith(".json")]
        rng.shuffle(members)
        wanted = {}
        for m in members:
            for frame, flags in orbit_pick(json.load(notes.open(m)), rng):
                wanted[frame] = flags
            if len(wanted) >= (limit - len(out)) * 1.3:
                break
        say(f"ORBIT {split}: {len(wanted)} frames wanted from {len(members)} videos")
        zipped, found = RemoteZip(url), []
        for name, offset, csize, method in zipped.entries():
            frame = name.rsplit("/", 1)[-1]
            if frame not in wanted:
                continue
            parts = name.split("/")                    # split / collector / thing / clean|clutter / video / frame
            named = orbit_name(parts[2]) if len(parts) >= 6 else None
            if named:
                thing, many = named
                flags = wanted[frame]
                if parts[3] == "clean":
                    rows = [{"question": ORBIT_ASK_WHAT, "answer": orbit_this(thing, many)},
                            {"question": ORBIT_ASK_GOOD, "answer": orbit_quality(flags)}]
                else:
                    shown = thing[len("pair of "):] if thing.startswith("pair of ") else thing
                    rows = [{"question": f"Where is the {shown} in this picture?" if not many else
                             f"Where are the {shown} in this picture?",
                             "answer": orbit_where(thing, many, flags["object_bounding_box"])}]
                found.append((f"orbit-{frame}", (offset, csize, method),
                              [dict(r, credit=ORBIT_CREDIT) for r in rows]))
            if len(found) >= len(wanted):
                break
        say(f"ORBIT {split}: {len(found)} frames located")
        rng.shuffle(found)
        out += fetch_from_zip(zipped, found[:limit - len(out)])
    # No place: ORBIT's first phase was filmed in the UK, its second by collectors around the world (mostly the UK,
    # Canada, the USA and Australia), and a video does not say which (the ORBIT paper, appendix A.1).
    return with_twins(out[:limit])


# ----------------------------------------------------------------- CORe50

CORE50_ZIP = "http://bias.csr.unibo.it/maltoni/download/core50/core50_350x350.zip"
CORE50_KINDS = ("This is a plug adapter.", "This is a mobile phone.", "This is a pair of scissors.",
                "This is a light bulb.", "This is a drink can.", "This is a pair of glasses.", "This is a ball.",
                "This is a marker pen.", "This is a cup.", "This is a remote control.")   # objects 1-5, 6-10 ...
CORE50_CREDIT = ("CORe50 (Vincenzo Lomonaco and Davide Maltoni, 'CORe50: a New Dataset and Benchmark for Continuous "
                 "Object Recognition', CoRL 2017), CC BY 4.0, https://vlomonaco.github.io/core50/")


def build_core50(limit, every=40):
    """The CORe50 pack's pictures: every 40th frame of each object's 300-frame clip in each of the 11 sessions
    (about 4,100), read from the 28 GB zip of 350 x 350 frames by range requests."""
    zipped, items = RemoteZip(CORE50_ZIP), []
    for name, offset, csize, method in zipped.entries():
        m = re.search(r"/s(\d+)/o(\d+)/C_\d+_\d+_(\d+)\.png$", name)
        if m and int(m.group(3)) % every == 0:
            answer = CORE50_KINDS[(int(m.group(2)) - 1) // 5]
            items.append((f"core50-s{m.group(1)}-o{m.group(2)}-{m.group(3)}.jpg", (offset, csize, method),
                          {"question": "What is this?", "answer": answer, "credit": CORE50_CREDIT}))
    say(f"CORe50: {len(items)} frames chosen")
    random.Random(54).shuffle(items)
    return fetch_from_zip(zipped, items[:int(limit * 1.02) + 2])[:limit]


# ----------------------------------------------------------------- LILA BC camera traps

LILA_LIST = "https://lila.science/wp-content/uploads/2023/06/lila_camera_trap_datasets.csv"
LILA_TAXONOMY = "https://lila.science/public/lila-taxonomy-mapping_release.csv"
# The collections used, each checked on its lila.science page to be under the Community Data License Agreement,
# permissive variant (https://cdla.dev/permissive-1-0/). Left out: Idaho Camera Traps (its terms say the images "may
# not be sold"), and, for size, Snapshot Serengeti (190 MB of labels), NACTI, WCS, SWG, the NZ trail cameras and
# the Snapshot Safari 2024 expansion (all CDLA-Permissive too; add them here for a bigger pack).
LILA_SETS = ("Caltech Camera Traps", "ENA24", "Missouri Camera Traps", "Wellington Camera Traps",
             "Island Conservation Camera Traps", "Channel Islands Camera Traps", "Snapshot Karoo", "Snapshot Kgalagadi",
             "Snapshot Enonkishu", "Snapshot Camdeboo", "Snapshot Mountain Zebra", "Snapshot Kruger",
             "Orinoquia Camera Traps", "Desert Lion Conservation Camera Traps", "Ohio Small Animals",
             "Seattle(ish) Camera Traps", "UNSW Predators", "Nkhotakota Camera Traps",
             "Biome Health Project Maasai Mara 2018", "Oregon Critters", "Duck Pictures in Wetlands")
LILA_NOT_ANIMAL = re.compile(r"^(empty|blank|human|person|people|vehicle|car|motorcycle|bicycle|misfire|unknown|"
                             r"unidentif|unclassif|start|end|setup|test|fire|other|none|nothing|ignore|"
                             r"humans?$|.*\bhuman\b|.*\bvehicle\b)", re.I)
LILA_ASK = "What animal is in this picture?"


def lila_place(row):
    """The place of a LILA collection from LILA's list (its "region" and "country" columns), or "" where the list
    gives none (Missouri Camera Traps, named after its university, shows red deer and mouflon from elsewhere) or
    several countries. The list is UTF-8 that may have been read as Latin-1 ("OrinoquÃ­a"): mended first."""
    def mended(text):
        """Text read as Latin-1 turned back into its UTF-8 letters (unchanged when it was read right)."""
        try:
            return str(text or "").encode("latin-1").decode("utf-8")
        except UnicodeError:
            return str(text or "")
    country = mended(row.get("country"))
    if not country or ";" in country:
        return ""
    return place_name(mended(row.get("region")), country_named(country) or country)


def lila_json(s, url):
    """A LILA metadata file (JSON, or JSON in a zip)."""
    data = s.get(url, timeout=900).content
    if url.endswith(".zip") or data[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(data))
        name = next(n for n in z.namelist() if n.endswith(".json"))
        return json.load(z.open(name))
    return json.loads(data)


def lila_taxa(s):
    """{(collection, label in lower case): (common name, scientific name or "")} for animals."""
    out = {}
    for r in csv.DictReader(io.StringIO(s.get(LILA_TAXONOMY, timeout=120).text)):
        common, latin = clean(r.get("common_name")), clean(r.get("scientific_name"))
        if not common or not latin or latin.startswith("homo") or (r.get("kingdom") or "") != "animalia":
            continue
        level = r.get("taxonomy_level") or ""
        if level in ("species", "subspecies", "genus"):
            latin = latin[0].upper() + latin[1:]
        else:
            latin = ""
        if level not in ("species", "subspecies") and common.endswith("s") and not common.endswith("ss"):
            common = common[:-2] if re.search(r"(x|z|ch|sh|sses)$", common) else common[:-1]   # "iguanas" -> "iguana"
        out[(r["dataset_name"], r["query"].lower())] = (common, latin)
    return out


def lila_count(value):
    """A count people gave ("2"), or None when none was given (or a range such as "11-50")."""
    try:
        n = int(float(str(value)))
        return n if n > 0 else None
    except ValueError:
        return None


def lila_answer(species):
    """ "It shows two plains zebras (Equus quagga)." from [(common, latin, count or None)]."""
    parts = []
    for common, latin, count in species:
        latin_part = f" ({latin})" if latin else ""
        if count and count > 1:
            parts.append(f"{number_word(count)} {plural(common)}{latin_part}")
        else:
            parts.append(f"{a_or_an(common)} {common}{latin_part}")
    if all(c for _, _, c in species):                # every count known
        return f"It shows {listed(parts)}."
    if len(parts) == 1:
        return f"The animal in this picture is {parts[0]}."
    return f"The animals in this picture are {listed(parts)}."


def lila_collection(s, row, taxa, quota, rng):
    """[(name, address, row)] from one LILA collection: images whose labels are all mapped animals, one image of each
    sequence, checked by MegaDetector (an animal found, no person) where LILA has its results, spread over the
    species."""
    dataset = row["name"]
    meta = lila_json(s, row["metadata_url_gcp"])
    categories = {c["id"]: str(c["name"]).lower() for c in meta["categories"]}
    images = {i["id"]: i for i in meta["images"]}
    labels = {}
    for a in meta["annotations"]:
        labels.setdefault(a["image_id"], []).append(a)
    md_url = row.get("md_results_with_rde") or row.get("mdv5a_results_raw")
    seen_by_md = None
    if md_url:
        md = lila_json(s, md_url)
        seen_by_md = {}
        for im in md.get("images", []):
            dets = im.get("detections") or []
            animal = max([d["conf"] for d in dets if d.get("category") == "1"] or [0])
            person = max([d["conf"] for d in dets if d.get("category") in ("2", "3")] or [0])
            seen_by_md[im["file"].replace("\\", "/")] = animal >= 0.5 and person < 0.3
    by_species, sequences = {}, set()
    ids = sorted(labels, key=str)
    rng.shuffle(ids)
    for image_id in ids:
        image = images.get(image_id)
        if not image or image.get("corrupt"):
            continue
        species, ok = {}, True
        for a in labels[image_id]:
            label = categories.get(a.get("category_id"), "")
            if LILA_NOT_ANIMAL.match(label) or (dataset, label) not in taxa:
                ok = False
                break
            entry = species.setdefault(taxa[(dataset, label)], {"boxes": 0, "count": None})
            entry["boxes"] += 1 if a.get("bbox") else 0
            entry["count"] = entry["count"] or lila_count(a.get("count"))
        if not ok or not species:
            continue
        sequence = image.get("seq_id")
        if sequence and sequence in sequences:
            continue
        if seen_by_md is not None and not seen_by_md.get(image["file_name"], False):
            continue
        if seen_by_md is None and any(a.get("sequence_level_annotation") for a in labels[image_id]):
            continue                                   # a whole sequence's label, unchecked: the frame may be empty
        sequences.add(sequence)
        named = sorted((common, latin, e["boxes"] or e["count"]) for (common, latin), e in species.items())
        key = tuple(n[0] for n in named)
        by_species.setdefault(key, []).append((image, named))
    items, rounds = [], 0
    while len(items) < quota and any(by_species.values()) and rounds < 1000:
        rounds += 1
        for key in list(by_species):                  # round robin: rare species get in before common ones fill up
            if by_species[key] and len(items) < quota:
                image, named = by_species[key].pop()
                address = row["image_base_url_gcp"].rstrip("/") + "/" + image["file_name"]
                credit = f"{dataset} (LILA BC, lila.science), Community Data License Agreement (permissive), " \
                         f"{row['image_base_url_gcp'].rstrip('/')}/{image['file_name']}"
                items.append((f"lila-{row['short_name']}-{re.sub(r'[^A-Za-z0-9]+', '-', str(image['id']))[-60:]}.jpg",
                              address, {"question": LILA_ASK, "answer": lila_answer(named), "credit": credit,
                                        **where(lila_place(row))}))
    say(f"LILA {dataset}: {sum(len(v) for v in by_species.values()) + len(items)} usable images of "
        f"{len(by_species)} kinds, {len(items)} taken")
    return items


def build_lila_camera_traps(limit):
    """The LILA camera-trap pack's pictures: the collections share the limit; night pictures (black and white,
    taken with an infrared flash) are said to be so."""
    s, rng = session(), random.Random(55)
    rows = {r["name"]: r for r in csv.DictReader(io.StringIO(s.get(LILA_LIST, timeout=120).text))}
    taxa = lila_taxa(s)
    chosen = [rows[name] for name in LILA_SETS if name in rows]
    quota = max(1, -(-int(limit * 1.15) // len(chosen)))
    items = []
    for row in chosen:
        try:
            items += lila_collection(s, row, taxa, quota, rng)
        except Exception as e:  # noqa: BLE001 - a collection that cannot be read is left out
            say(f"LILA {row['name']}: left out ({e})")
    rng.shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=8)
    out = []
    for name, data, row in fetched[:limit]:
        night = " It is a black-and-white night picture from a camera trap." if is_greyscale(data) else \
            " It is a picture from a camera trap."
        out.append((name, data, dict(row, answer=row["answer"] + night)))
    return out


# ----------------------------------------------------------------- GBIF: species photos from many sources

GBIF = "https://api.gbif.org/v1/"
GBIF_INATURALIST = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"      # left out: the inaturalist pack has these
# A photo's own licence (not only its record's) must be one of these: CC0, the Public Domain Mark, or CC BY.
GBIF_FREE = re.compile(r"creativecommons\.org/(licenses/by/(\d\.\d)|publicdomain/(zero|mark)/\d\.\d)/?(legalcode)?"
                       r"(\.\w+)?$", re.I)
# The groups, as GBIF Backbone keys (its backbone has no class for reptiles or ray-finned fish, so their orders are
# listed: lizards and snakes, turtles, crocodiles; sharks and rays and the main bony-fish orders), with the question.
GBIF_GROUPS = [((212,), "What bird is this?"), ((359,), "What animal is this?"),
               ((11592253, 11418114, 11493978), "What animal is this?"), ((131,), "What animal is this?"),
               ((121, 587, 1313, 1153, 708, 772, 588, 549, 590, 773, 495, 538, 548), "What fish is this?"),
               ((216,), "What insect is this?"), ((367,), "What is this creature?"), ((52,), "What is this creature?"),
               ((6,), "What plant is this?"), ((5,), "What mushroom or fungus is this?")]
# English names that name a disease or damage rather than the living thing (fungi): the Latin name is used instead.
GBIF_NOT_A_NAME = re.compile(r"\b(disease|rot|blight|canker|wilt|scab|mildew|spot|gall)\b", re.I)


def gbif_licence(url):
    """ "CC BY 4.0", "CC0" or "Public Domain Mark" for a free Creative Commons address, else ""."""
    m = GBIF_FREE.search((url or "").strip())
    if not m:
        return ""
    if m.group(2):
        return f"CC BY {m.group(2)}"
    return "CC0" if m.group(3).lower() == "zero" else "Public Domain Mark"


def gbif_english(s, key, cache):
    """A species' English name from GBIF's backbone (cached), or ""."""
    if key not in cache:
        name = ""
        try:
            for v in s.get(f"{GBIF}species/{key}/vernacularNames", params={"limit": 200}, timeout=60).json().get(
                    "results", []):
                if v.get("language") == "eng" and v.get("vernacularName"):
                    name = clean(v["vernacularName"])
                    break
        except Exception:  # noqa: BLE001 - no English name
            pass
        cache[key] = name
    return cache[key]


def gbif_datasets(s, params):
    """[(dataset key, records)] of the datasets holding a group's photo records, iNaturalist left out (a facet
    query: GBIF pages deep in a big list very slowly, so the builder samples shallow pages of each dataset)."""
    data = s.get(f"{GBIF}occurrence/search", params=dict(params, limit=0, facet="datasetKey", facetLimit=60),
                 timeout=120).json()
    counts = (data.get("facets") or [{}])[0].get("counts", [])
    return [(c["name"], c["count"]) for c in counts if c["name"] != GBIF_INATURALIST]


def build_gbif_species(limit, per_species=2):
    """The GBIF pack's pictures: for each group (birds, mammals ... fungi), pages of human observations with photos
    from the group's 60 biggest datasets (not iNaturalist; datasets weighted by the square root of their size, so
    small ones count too), at random places in each dataset's first 3,000 records, keeping photos whose own licence
    is free, at most per_species photos of a species."""
    s, rng = session(), random.Random(56)
    names, titles, items = {}, {}, []
    per_group = -(-int(limit * 1.15) // len(GBIF_GROUPS))
    for taxon, question in GBIF_GROUPS:
        params = {"mediaType": "StillImage", "taxonKey": list(taxon), "basisOfRecord": "HUMAN_OBSERVATION",
                  "license": ["CC0_1_0", "CC_BY_4_0"]}
        try:
            datasets = gbif_datasets(s, params)
        except Exception as e:  # noqa: BLE001 - the group is left out
            say(f"GBIF group {taxon}: left out ({e})")
            continue
        weights = [n ** 0.5 for _, n in datasets]
        species, found, tries, empty = {}, 0, 0, set()
        while datasets and found < per_group and tries < max(10, per_group // 5):
            tries += 1
            key, count = rng.choices(datasets, weights)[0]
            if key in empty:
                continue
            offset = rng.randrange(0, max(1, min(count, 3000) - 100))
            try:
                results = s.get(f"{GBIF}occurrence/search", timeout=120,
                                params=dict(params, datasetKey=key, offset=offset, limit=100)).json().get("results", [])
            except Exception:  # noqa: BLE001 - another page
                time.sleep(5)
                continue
            usable = 0
            for o in results:
                taxon_key = o.get("speciesKey")
                if not taxon_key or species.get(taxon_key, 0) >= per_species \
                        or o.get("taxonRank") not in ("SPECIES", "SUBSPECIES", "VARIETY"):
                    continue
                media = next((m for m in o.get("media") or [] if m.get("type") == "StillImage"
                              and (m.get("identifier") or "").startswith("http") and gbif_licence(m.get("license"))
                              and "inaturalist" not in m["identifier"]), None)
                if not media:
                    continue
                usable += 1
                latin = clean(o.get("species"))
                common = gbif_english(s, taxon_key, names)
                common = "" if GBIF_NOT_A_NAME.search(common) else common
                answer = f"This is {a_or_an(common)} {common} ({latin})." if common else f"This is {latin}."
                if key not in titles:
                    titles[key] = clean(o.get("datasetName")) or clean(s.get(f"{GBIF}dataset/{key}",
                                                                             timeout=60).json().get("title"))
                who = clean(media.get("creator") or media.get("rightsHolder") or o.get("recordedBy"))
                if not re.search(r"[A-Za-z]", who):
                    who = "an unnamed photographer"
                credit = (f"Photo by {who}, {gbif_licence(media['license'])}, from {titles[key]} via GBIF, "
                          f"https://www.gbif.org/occurrence/{o['key']}")
                species[taxon_key] = species.get(taxon_key, 0) + 1
                items.append((f"gbif-{o['key']}.jpg", media["identifier"],
                              {"question": question, "answer": answer, "credit": credit,
                               **where(country_named(o.get("countryCode")))}))      # the record's country
                found += 1
                if found >= per_group:
                    break
            if not usable:
                empty.add(key)                         # no free photos there (often "all rights reserved")
            time.sleep(0.3)
        say(f"GBIF group {taxon[0]}: {found} photos of {len(species)} species from {len(datasets)} datasets")
    rng.shuffle(items)
    return fetch_all(items[:int(limit * 1.15) + 2], workers=6, pause=0.2)[:limit]


# ----------------------------------------------------------------- Wikimedia Commons: breeds

# The animal, its breed categories ("<Animal> breeds by name" where Commons has it) and the question asked.
COMMONS_BREEDS = [("dog", "Dog breeds by name", "What breed of dog is this?"),
                  ("cat", "Cat breeds", "What breed of cat is this?"),
                  ("horse", "Horse breeds by name", "What breed of horse is this?"),
                  ("cattle", "Cattle breeds by name", "What breed of cattle is this?"),
                  ("sheep", "Sheep breeds by name", "What breed of sheep is this?"),
                  ("goat", "Goat breeds by name", "What breed of goat is this?"),
                  ("pig", "Pig breeds", "What breed of pig is this?"),
                  ("chicken", "Chicken breeds", "What breed of chicken is this?"),
                  ("rabbit", "Rabbit breeds", "What breed of rabbit is this?")]
# Category names that are not one breed (lists, groups, art, heads and so on).
BREED_NOT_ONE = re.compile(r"\b(by|breeds|groups?|unidentified|mixed|crossbreeds?|history|extinct|landrace|types?|"
                           r"illustrations?|in art|heads?|portraits?|coat|colou?rs?|female|male|puppies|kittens|"
                           r"foals|lambs|kids|chicks|associations?|riding|wool|mini)\b", re.I)


def breed_name(category, animal):
    """The breed's name from its category ("Category:Alaska (rabbit)" -> "Alaska", "Category:Harlequin rabbits" ->
    "Harlequin rabbit")."""
    name = category.split(":", 1)[-1]
    name = re.sub(r"\s*\([^)]*\)$", "", name).strip()
    words = name.split()
    if len(words) > 1 and words[-1].lower() in (animal + "s", plural(animal)):
        words[-1] = animal                                      # "Chartreux cats" -> "Chartreux cat"
    return " ".join(words)


def build_commons_breeds(limit, per_breed=4):
    """The Commons breeds pack's pictures: the breeds of every animal taken in turn (in a shuffled order), a few free
    pictures from each breed's category; drawings, art and signs left out."""
    s, rng = session(), random.Random(57)
    queues = []
    for animal, parent, question in COMMONS_BREEDS:
        breeds = [c for c in commons_members(s, parent, "subcat") if not BREED_NOT_ONE.search(c.split(":", 1)[-1])]
        rng.shuffle(breeds)
        queues.append((animal, question, breeds))
        say(f"Commons breeds: {len(breeds)} {animal} breeds")
    items, seen = [], set()
    while len(items) < limit * 1.15 and any(q[2] for q in queues) and not out_of_time():
        for animal, question, breeds in queues:
            if not breeds or len(items) >= limit * 1.15:
                continue
            category = breeds.pop()
            breed = breed_name(category, animal)
            titles = [t for t in commons_members(s, category.split(":", 1)[-1], "file")
                      if t not in seen and not COMMONS_NOT_FOOD.search(t)]
            rng.shuffle(titles)
            got = 0
            for title, url, credit, _ in commons_entries(s, titles[:per_breed * 3]):
                seen.add(title)
                name = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
                kind = "cattle" if animal == "cattle" else animal
                answer = f"It looks like {a_or_an(breed)} {breed}, a breed of {kind}."
                items.append((f"breed-{name}.jpg", url, {"question": question, "answer": answer, "credit": credit,
                                                         **commons_place(title)}))
                got += 1
                if got >= per_breed:
                    break
    say(f"Commons breeds: {len(items)} free pictures")
    rng.shuffle(items)
    return fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)[:limit]


# ----------------------------------------------------------------- the packs

EVERYDAY_PACKS = {
    "open_images_objects": (build_open_images_objects, "Open Images V7 (Google): image-level labels verified by "
                                                       "people, CC BY 4.0, https://storage.googleapis.com/openimages/"
                                                       "web/index.html. Each photo is CC BY 2.0 (checked photo by "
                                                       "photo), credited below with its photographer and Flickr page."),
    "orbit": (build_orbit, "ORBIT: A Real-World Few-Shot Dataset for Teachable Object Recognition, collected from "
                           "people who are blind or low vision (Daniela Massiceti, Luisa Zintgraf, John Bronskill, "
                           "Lida Theodorou, Matthew Tobias Harris, Edward Cutrell, Cecily Morrison, Katja Hofmann and "
                           "Simone Stumpf, ICCV 2021), City, University of London, CC BY 4.0. "
                           "https://doi.org/10.25383/city.14294597 and https://github.com/microsoft/ORBIT-Dataset "
                           "(frame annotations). Frames resized; names of the collectors' things tidied."),
    "core50": (build_core50, CORE50_CREDIT + " Frames converted to JPEG."),
    "lila_camera_traps": (build_lila_camera_traps, "Camera-trap collections from LILA BC (Labeled Information "
                                                   "Library of Alexandria: Biology and Conservation), "
                                                   "https://lila.science, each "
                                                   "released under the Community Data License Agreement - Permissive "
                                                   "1.0 (https://cdla.dev/permissive-1-0/); scientific names from "
                                                   "LILA's taxonomy mapping. Collections: " + ", ".join(LILA_SETS) +
                                                   ". Each picture's collection and address below."),
    "gbif_species": (build_gbif_species, "GBIF (Global Biodiversity Information Facility), https://www.gbif.org: "
                                         "observation photos whose own licence is CC0, Public Domain Mark or CC BY, "
                                         "each with its photographer, source dataset and GBIF record below. English "
                                         "names from the GBIF Backbone Taxonomy. iNaturalist records are not "
                                         "included."),
    "commons_breeds": (build_commons_breeds, "Wikimedia Commons breed categories: pictures CC0, public domain or CC "
                                             "BY, each with its author and file page below. "
                                             "https://commons.wikimedia.org"),
}

# How many pictures a full build takes from each collection (about what each offers after the licence checks).
EVERYDAY_LIMITS = {
    "open_images_objects": 12000,     # of about 44,900 free photos with a confirmed household label
    "orbit": 7000,                    # 2 frames from each of about 3,800 videos in the benchmark zips
    "core50": 4000,                   # of about 4,100 frames taken (every 40th frame)
    "lila_camera_traps": 8000,        # of about 725,000 usable images (21 collections, about 1,000 kinds)
    "gbif_species": 6000,             # 10 groups, at most 2 photos a species (hundreds of thousands free)
    "commons_breeds": 3000,           # about 1,000 breed categories, at most 4 pictures each
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one household-object or animal pack builder.")
    parser.add_argument("key", choices=sorted(EVERYDAY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = EVERYDAY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
