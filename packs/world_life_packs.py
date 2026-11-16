"""Pack builders for two needs of blind people, used by build_packs.py in the same way as its own PACKS: each builder
is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"}. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (as food_packs.py does), so the zip holds each picture only once. The limit
counts pictures.

Getting around safely (streets, crossings, pavements, stairs, doors, buses, indoor places):
  ptl_crossings     Pedestrian-Traffic-Lights (PTL, Yu, Lee and Kim, 2019; MIT licence, github.com/samuelyu2002/
                    ImVisible): 5,059 photos taken at crossings in Shanghai for a blind people's app, each labelled
                    with the pedestrian light (red, green, green counting down, none) and the line of the zebra
                    crossing. "What does the pedestrian light show?" and "Which way does the zebra crossing go?"
  uroac_crossings   UrOAC, Urban Objects in Any-light Conditions (University of Alicante, Mendeley Data fcrmp92ckn,
                    CC BY 4.0; faces and number plates already masked by the authors): about 1,010 street photos in
                    daylight, dusk and night, with pedestrian crossings and red and green pedestrian lights marked.
  open_images_street Google Open Images V7 (labels CC BY 4.0; each photo CC BY 2.0 with its photographer named):
                    photos where people checked by hand whether stairs, escalators, lifts, doors, handrails, ramps,
                    pedestrian crossings, kerbs, pavements, bus stops, traffic lights, buses, benches, bollards and
                    similar things are there, and where (boxes). "Are there any stairs here?" "Yes, there are stairs
                    in the middle of the picture..."
  walkway_dhaka     Navigation Assistance for the Visually Impaired (Ashik et al., East West University, Mendeley Data
                    m68g3h7p87, CC BY 4.0): frames from videos filmed on footpaths in Dhaka, with 22 kinds of
                    obstacles and vehicles marked. "What is ahead of me on this path?"
  outdoor_navigation Outdoor Navigation Dataset (Craciunescu, Politehnica University of Bucharest, Zenodo 14043015,
                    CC BY 4.0): pedestrian-eye frames with crossings, ramps, pavements, roads and people marked.
  seoul_sidewalks   Seoul Sidewalk Accessibility Image Dataset (Zenodo 22908353, CC0): 514 pavements photographed
                    in Seoul with their width and slopes measured on site and their surface graded A to D by three
                    raters. "Is this pavement in good condition?" "How wide is it?" (most photos are HEIC: reading
                    them needs the pillow-heif package; without it only the JPEG photos are used).

The whole world's everyday life:
  dollar_street     Dollar Street (Gapminder, CC BY 4.0, photographer credited): homes and everyday things of
                    families in about 60 countries at every income, from Gapminder's own site. "What is this?" or
                    "What kind of place is this?", and for street views and house overviews "Where might this photo
                    be from?" (the country only; income is never put in an answer).
  geode             GeoDE (Ramaswamy et al., Princeton, 2023; CC BY): about 62,000 photos of 40 kinds of everyday
                    objects and places, taken for the dataset by paid workers in six regions of the world (Africa,
                    the Americas, East Asia, Europe, South-East Asia, West Asia). "What is this?"

Answers are written from each dataset's own labels with fixed sentences (nothing is written by an AI model), with
practical safety advice where it matters ("do not cross yet").

    python packs/world_life_packs.py ptl_crossings --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import math
import random
import re
import struct
import sys
import time
import zipfile
import zlib

from build_packs import session, clean, smaller, fetch_all, say, article  # noqa: F401
from food_packs import with_twins, sentence, listed, oi_lines, oi_licence_name, OI, OI_PICTURE


# ----------------------------------------------------------------- shared helpers

class RemoteFile(io.RawIOBase):
    """A file on a web server read in pieces (HTTP Range requests), so zipfile can take a few pictures out of a
    large zip without downloading all of it. got counts the bytes read."""

    def __init__(self, url, s=None):
        """Opens url and asks for its size."""
        super().__init__()
        self.url, self.s, self.pos, self.got = url, s or session(), 0, 0
        r = self.s.get(url, headers={"Range": "bytes=0-0"}, timeout=120, stream=True)
        r.raise_for_status()
        self.url = r.url                                    # after any redirect (signed addresses)
        self.size = int(r.headers["Content-Range"].rsplit("/", 1)[1])
        r.close()

    def readable(self):
        """It can be read."""
        return True

    def seekable(self):
        """It can be read from any place."""
        return True

    def tell(self):
        """The current place."""
        return self.pos

    def seek(self, offset, whence=0):
        """Move to a place (as for a normal file)."""
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def readinto(self, buffer):
        """Read the next bytes into buffer (tried three times)."""
        n = min(len(buffer), self.size - self.pos)
        if n <= 0:
            return 0
        for attempt in range(3):
            try:
                r = self.s.get(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + n - 1}"}, timeout=300)
                if r.status_code == 206:
                    break
            except Exception:  # noqa: BLE001 - tried again
                pass
            time.sleep(3 * (attempt + 1))
        else:
            raise OSError(f"cannot read {self.url}")
        data = r.content
        buffer[:len(data)] = data
        self.pos += len(data)
        self.got += len(data)
        return len(data)


def remote_zip(url, s=None):
    """A zipfile.ZipFile reading a zip on the web piece by piece."""
    return zipfile.ZipFile(io.BufferedReader(RemoteFile(url, s), 1 << 20))


class _Joined:
    """Bytes already read followed by the rest of a stream (used by zip_entries)."""

    def __init__(self, head, stream):
        """head: bytes to give first; stream: where the rest comes from."""
        self.head, self.stream = head, stream

    def read(self, n):
        """The next n bytes."""
        if self.head:
            out, self.head = self.head[:n], self.head[n:]
            return out + (self.stream.read(n - len(out)) if len(out) < n else b"")
        return self.stream.read(n)


def zip_entries(stream):
    """(name, bytes) of each file of a zip read from start to end as a stream (for a zip inside a zip, which cannot
    be read piece by piece), stopping at the zip's list of contents."""
    while True:
        head = stream.read(30)
        if len(head) < 30 or head[:4] != b"PK\x03\x04":
            return
        flag, method, size, name_length, extra_length = struct.unpack("<6xHH8xI4xHH", head)
        name = stream.read(name_length).decode("utf-8", "replace")
        stream.read(extra_length)
        if flag & 8:                       # sizes come after the data: decompress until the data ends
            if method != 8:
                return
            unzip, parts = zlib.decompressobj(-15), []
            while not unzip.eof:
                chunk = stream.read(1 << 16)
                if not chunk:
                    return
                parts.append(unzip.decompress(chunk))
            data, rest = b"".join(parts), unzip.unused_data
            if len(rest) < 16:
                rest += stream.read(16 - len(rest))
            stream = _Joined(rest[16:] if rest[:4] == b"PK\x07\x08" else rest[12:], stream)
        else:
            data = stream.read(size)
            if method == 8:
                data = zlib.decompress(data, -15)
        yield name, data


def mendeley_tree(dataset, version=1):
    """{folder path/file name: download address} of every file of a Mendeley Data dataset (its folders walked)."""
    s, api = session(), f"https://data.mendeley.com/public-api/datasets/{dataset}"
    folders = s.get(f"{api}/folders/{version}", timeout=60).json()
    by_id = {f["id"]: f for f in folders}

    def path(folder):
        """The folder's path from the dataset's root."""
        parent = by_id.get(folder.get("parent_id"))
        return (path(parent) + "/" if parent else "") + folder["name"]

    out = {}
    for folder_id, prefix in [("root", "")] + [(f["id"], path(f) + "/") for f in folders]:
        files = s.get(f"{api}/files", params={"folder_id": folder_id, "version": version}, timeout=120).json()
        for f in files:
            out[prefix + f["filename"]] = f["content_details"]["download_url"]
    return out


def side_of(x):
    """Where a point across the picture is (0 left, 1 right), as seen by someone holding the camera."""
    return "on your left" if x < 0.33 else "on your right" if x > 0.67 else "straight ahead"


def picture_part(x, y=None):
    """Where a point is in a picture (0-1 from the left and from the top), in plain words."""
    across = "left" if x < 0.33 else "right" if x > 0.67 else "middle"
    if y is None:
        return f"on the {across} of the picture" if across != "middle" else "in the middle of the picture"
    down = "top" if y < 0.33 else "bottom" if y > 0.67 else ""
    if across == "middle" and not down:
        return "in the middle of the picture"
    if across == "middle":
        return f"at the {down} of the picture"
    return f"at the {down} {across} of the picture" if down else f"on the {across} of the picture"


def distance_word(area):
    """"close to you" for an object filling much of the picture, "in the distance" for a small one, else ""."""
    return " close to you" if area > 0.15 else " in the distance" if area < 0.004 else ""


def yolo_boxes(text):
    """[(class number, x centre, y centre, width, height)] from a YOLO label file, boxes or polygons (0-1)."""
    out = []
    for line in text.splitlines():
        cells = line.split()
        if len(cells) < 5:
            continue
        number, values = int(cells[0]), [float(v) for v in cells[1:]]
        if len(values) == 4:
            x, y, w, h = values
        else:                                              # a polygon: x1 y1 x2 y2 ...
            xs, ys = values[0::2], values[1::2]
            x, y, w, h = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys)
        out.append((number, x, y, w, h))
    return out


def count_words(n, one, many):
    """ "a bus", "two buses", "5 buses"."""
    words = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
    return one if n == 1 else f"{words.get(n, n)} {many}"


def safe_name(text):
    """A file-name-safe version of a name."""
    return re.sub(r"[^\w.-]+", "_", str(text))[:80]


def capitalised(text):
    """Text starting with a capital letter."""
    return text[:1].upper() + text[1:]


# ----------------------------------------------------------------- PTL pedestrian lights (Shanghai)

PTL_ZIP = "https://drive.usercontent.google.com/download?id=117HUGczZwXFRbuBl7y4cHakH3xQV2Omo&export=download&confirm=t"
PTL_LABELS = "https://raw.githubusercontent.com/samuelyu2002/ImVisible/master/Annotations/"
PTL_FILES = ("training_file.csv", "validation_file.csv", "testing_file.csv")
PTL_SIZE = (4032, 3024)                    # the labels' coordinates are on the original photo
PTL_ASK_LIGHT = "What does the pedestrian light show?"
PTL_ASK_CROSSING = "Which way does the zebra crossing go?"
# The paper: "countdown green" and "countdown blank" are the same light, a green light whose numbers count down
# (blank between two numbers); "none" means no pedestrian light can be seen.
PTL_ANSWERS = {
    "0": "The pedestrian light shows red, the standing person: do not cross yet. Wait for the green walking person.",
    "1": "The pedestrian light is green, the walking person: you may cross, but listen for turning traffic first.",
    "2": "The pedestrian light is green, with numbers counting down: it will soon turn red. Only start to cross if "
         "you have time to reach the other side; otherwise wait for the next green light.",
    "3": "The pedestrian light is green, with a countdown timer: it will soon turn red. Only start to cross if you "
         "have time to reach the other side; otherwise wait for the next green light.",
    "4": "I can't see a pedestrian light in this picture. Find another way to know when it is safe to cross, such "
         "as listening to the traffic or asking someone.",
}
PTL_CREDIT = "Pedestrian-Traffic-Lights (PTL) dataset (Yu, Lee and Kim, 2019), MIT licence, " \
             "https://github.com/samuelyu2002/ImVisible"


def ptl_crossing_answer(x1, y1, x2, y2, blocked):
    """Where the zebra crossing starts and which way it goes, from its labelled middle line (photo pixels)."""
    (nx, ny), (fx, fy) = sorted([(x1, y1), (x2, y2)], key=lambda p: -p[1])      # the near end is lower in the photo
    angle = math.degrees(math.atan2((fx - nx) / PTL_SIZE[0] * 4, max((ny - fy) / PTL_SIZE[1] * 3, 1e-6)))
    start = nx / PTL_SIZE[0]
    begins = ("on your left" if start < 0.15 else "a little to your left" if start < 0.35 else "in front of you"
              if start <= 0.65 else "a little to your right" if start <= 0.85 else "on your right")
    if abs(angle) < 12:
        goes = "goes straight ahead"
    elif abs(angle) < 35:
        goes = "bears slightly to the " + ("right" if angle > 0 else "left")
    else:
        goes = "goes off to the " + ("right" if angle > 0 else "left")
    answer = f"The zebra crossing starts {begins} and {goes}."
    if blocked == "blocked":
        answer += " People or vehicles are on part of it."
    return answer


def build_ptl_crossings(limit):
    """The PTL pack's pictures: [(name, JPEG or None, row)]. Reads the labels (GitHub) and takes the photos one by
    one out of the 768x576 zip on Google Drive (609 MB; only the photos used are downloaded)."""
    s = session()
    labels = {}
    for name in PTL_FILES:
        for row in csv.DictReader(io.StringIO(s.get(PTL_LABELS + name, timeout=60).text.lstrip("﻿"))):
            labels[row["file"].lower()] = row
    say(f"PTL: {len(labels)} labelled photos")
    z = remote_zip(PTL_ZIP, s)
    names = {n.rsplit("/", 1)[-1].lower(): n for n in z.namelist() if n.lower().endswith((".jpg", ".jpeg"))}
    keys = sorted(k for k in labels if k in names)
    random.Random(51).shuffle(keys)
    out = []
    for key in keys:
        if len(out) >= limit:
            break
        row = labels[key]
        data = smaller(z.read(names[key]))
        if not data or row["mode"] not in PTL_ANSWERS:
            continue
        rows = [{"question": PTL_ASK_LIGHT, "answer": PTL_ANSWERS[row["mode"]], "credit": PTL_CREDIT}]
        try:
            x1, y1, x2, y2 = (float(row[k]) for k in ("x1", "y1", "x2", "y2"))
            rows.append({"question": PTL_ASK_CROSSING, "credit": PTL_CREDIT,
                         "answer": ptl_crossing_answer(x1, y1, x2, y2, row.get("block", ""))})
        except (TypeError, ValueError):
            pass
        out.append((f"ptl-{key.rsplit('.', 1)[0]}.jpg", data, rows))
    return with_twins(out)


# ----------------------------------------------------------------- UrOAC crossings in any light (Alicante)

UROAC = ("fcrmp92ckn", 2)
UROAC_CREDIT = "UrOAC: Urban Objects in Any-light Conditions (Gomez-Donoso, Moreno-Martinez and Cazorla, " \
               "University of Alicante, 2022), Mendeley Data fcrmp92ckn, CC BY 4.0 (faces and number plates masked " \
               "by the authors)"
UROAC_CROSSING, UROAC_GREEN, UROAC_RED = 0, 1, 2          # the label numbers (checked against the photos)
UROAC_ASK_LIGHT = "Can I cross? What does the pedestrian light show?"
UROAC_ASK_CROSSING = "Is there a pedestrian crossing in front of me?"


def uroac_rows(boxes):
    """The questions and answers for one UrOAC photo from its boxes."""
    rows = []
    reds = [b for b in boxes if b[0] == UROAC_RED]
    greens = [b for b in boxes if b[0] == UROAC_GREEN]
    if reds and not greens:
        rows.append({"question": UROAC_ASK_LIGHT, "answer": "Not yet: the pedestrian light shows red, the standing "
                                                            "person. Wait for the green walking person."})
    elif greens and not reds:
        rows.append({"question": UROAC_ASK_LIGHT, "answer": "The pedestrian light is green, the walking person: you "
                                                            "may cross, but listen for turning traffic first."})
    crossings = [b for b in boxes if b[0] == UROAC_CROSSING]
    if crossings:
        nearest = max(crossings, key=lambda b: b[2] + b[4] / 2)
        where = "right in front of you" if 0.33 <= nearest[1] <= 0.67 else side_of(nearest[1])
        rows.append({"question": UROAC_ASK_CROSSING, "answer": f"Yes, there is a pedestrian crossing {where}."})
    else:
        rows.append({"question": UROAC_ASK_CROSSING, "answer": "No, I can't see a pedestrian crossing here."})
    return [dict(r, credit=UROAC_CREDIT) for r in rows]


def build_uroac_crossings(limit):
    """The UrOAC pack's pictures: [(name, JPEG or None, row)]. The labels are read piece by piece from the outer zip;
    the photos are inside a second zip that can only be read from its start, so they are read in order until there
    are enough (all 3.2 GB for a full pack)."""
    tree = mendeley_tree(*UROAC)
    address = next(url for name, url in tree.items() if name.lower().endswith(".zip"))
    outer = remote_zip(address)
    labels = {n.rsplit("/", 1)[-1].rsplit(".", 1)[0]: yolo_boxes(outer.read(n).decode("utf-8", "replace"))
              for n in outer.namelist() if n.upper().startswith("LABELS/") and n.endswith(".txt")}
    say(f"UrOAC: {len(labels)} labelled photos")
    inner = next(n for n in outer.namelist() if n.lower().endswith(".zip"))
    out = []
    for name, data in zip_entries(outer.open(inner)):
        key = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if key not in labels or not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        picture = smaller(data)
        rows = uroac_rows(labels[key])
        if picture and rows:
            out.append((f"uroac-{key}.jpg", picture, rows))
        if len(out) >= limit:
            break
    random.Random(52).shuffle(out)
    return with_twins(out)


# ----------------------------------------------------------------- Open Images: streets and buildings

OI_BOXES = {"validation": OI + "v5/validation-annotations-bbox.csv", "test": OI + "v5/test-annotations-bbox.csv"}
OI_IMAGE_LABELS = {"validation": OI + "v7/oidv7-val-annotations-human-imagelabels.csv",
                   "test": OI + "v7/oidv7-test-annotations-human-imagelabels.csv"}
OI_IMAGE_LISTS = {"validation": OI + "2018_04/validation/validation-images-with-rotation.csv",
                  "test": OI + "2018_04/test/test-images-with-rotation.csv"}
OI_CLASS_LIST = OI + "v7/oidv7-class-descriptions.csv"
# Each thing: (question, the thing's words with "a" or as plural, its plural, yes-advice, no answer).
OI_THINGS = {
    "Stairs": ("Are there any stairs here?", "stairs", "flights of stairs",
               "Take care: find the handrail and check with your foot or cane whether they go up or down.",
               "No, I can't see any stairs here."),
    "Escalator": ("Is there an escalator here?", "an escalator", "escalators",
                  "Find the moving handrail first, and step on and off carefully.",
                  "No, I can't see an escalator here."),
    "Elevator": ("Is there a lift (elevator) here?", "a lift (elevator)", "lifts", "",
                 "No, I can't see a lift here."),
    "Door": ("Is there a door?", "a door", "doors", "", "No, I can't see a door here."),
    "Handrail": ("Is there a handrail I can hold?", "a handrail", "handrails", "",
                 "No, I can't see a handrail here."),
    "Ramp": ("Is there a ramp here?", "a ramp", "ramps", "", "No, I can't see a ramp here."),
    "Pedestrian crossing": ("Is there a pedestrian crossing here?", "a pedestrian crossing", "pedestrian crossings",
                            "Check the traffic or the pedestrian light before you cross.",
                            "No, I can't see a pedestrian crossing here."),
    "Curb": ("Is there a kerb (curb) here?", "a kerb (curb)", "kerbs", "Mind the step down to the road.",
             "No, I can't see a kerb here."),
    "Sidewalk": ("Is there a pavement (sidewalk) here?", "a pavement (sidewalk)", "pavements", "",
                 "No, I can't see a pavement here."),
    "Bus stop": ("Is this a bus stop?", "a bus stop", "bus stops", "", "No, I can't see a bus stop here."),
    "Traffic light": ("Is there a traffic light?", "a traffic light", "traffic lights", "",
                      "No, I can't see a traffic light here."),
    "Bus": ("Is there a bus?", "a bus", "buses", "", "No, I can't see a bus here."),
    "Train station": ("Is this a train station?", "a train station", "train stations", "",
                      "No, this does not look like a train station."),
    "Metro station": ("Is this an underground (metro) station?", "an underground (metro) station", "metro stations",
                      "Keep well back from the platform edge.", "No, this does not look like a metro station."),
    "Turnstile": ("Is there a ticket gate or turnstile here?", "a turnstile", "turnstiles", "",
                  "No, I can't see a turnstile here."),
    "Bollard": ("Are there any bollards here?", "bollards", "bollards", "Low posts like these are easy to walk into.",
                "No, I can't see any bollards here."),
    "Bench": ("Is there a bench where I can sit?", "a bench", "benches", "", "No, I can't see a bench here."),
    "Fire hydrant": ("Is there a fire hydrant on the pavement?", "a fire hydrant", "fire hydrants",
                     "It is low, so it is easy to walk into.", "No, I can't see a fire hydrant here."),
    "Street light": ("Is there a street light or lamp post?", "a street light", "street lights", "",
                     "No, I can't see a street light here."),
    "Waste container": ("Is there a rubbish bin here?", "a rubbish bin", "rubbish bins", "",
                        "No, I can't see a rubbish bin here."),
    "Stop sign": ("Is there a stop sign?", "a stop sign", "stop signs", "", "No, I can't see a stop sign here."),
    "Wheelchair": ("Is there a wheelchair here?", "a wheelchair", "wheelchairs", "",
                   "No, I can't see a wheelchair here."),
}
OI_PLURAL_WORDS = {"stairs", "bollards"}                   # answered "there are" even when one box
OI_PLACES = {"Train station", "Metro station", "Bus stop"}  # answered "this is", not "there is"
OI_STREET = {"Stairs", "Escalator", "Elevator", "Pedestrian crossing", "Curb", "Sidewalk", "Bus stop", "Traffic light",
             "Bus", "Train station", "Metro station", "Turnstile", "Bollard", "Handrail", "Ramp"}  # a photo needs one
OI_MAX_NO = 0.3                                             # at most this share of the answers are "no"


def oi_yes_answer(name, boxes):
    """ "Yes, there is a bus on the left of the picture..." from the boxes of one thing (or none)."""
    _, one, many, advice, _ = OI_THINGS[name]
    if name in OI_PLACES:
        return f"Yes, this is {one}." + (f" {advice}" if advice else "")
    boxes = [b for b in boxes if not b["depiction"]]
    plural = one in OI_PLURAL_WORDS
    if not boxes:
        where = ""
        start = f"Yes, there {'are' if plural else 'is'} {one}"
    elif len(boxes) == 1 or all(b["group"] for b in boxes[:1]):
        b = boxes[0]
        where = " " + picture_part((b["x1"] + b["x2"]) / 2, (b["y1"] + b["y2"]) / 2)
        start = f"Yes, there {'are' if plural or b['group'] else 'is'} {many if b['group'] and not plural else one}"
    else:
        sides = []
        for b in sorted(boxes, key=lambda b: -(b["x2"] - b["x1"]) * (b["y2"] - b["y1"]))[:3]:
            part = picture_part((b["x1"] + b["x2"]) / 2)
            if part not in sides:
                sides.append(part)
        where = " " + listed(sides)
        start = f"Yes, there are {count_words(len(boxes), one, many) if len(boxes) <= 6 else 'several ' + many}"
    biggest = max(((b["x2"] - b["x1"]) * (b["y2"] - b["y1"]) for b in boxes), default=0)
    close = ", close to the camera" if biggest > 0.25 else ""
    return f"{start}{where}{close}." + (f" {advice}" if advice else "")


def build_open_images_street(limit):
    """The Open Images street pack's pictures: [(name, JPEG or None, row)]. Reads the labels people checked and the
    boxes they drew on the validation set (and, for a large pack, the test set), keeps photos whose own licence is
    free, need no turning and have at least one street or building label, and asks one question per checked label
    (most "yes", some "no")."""
    s = session()
    subsets = ("validation",) if limit < 500 else ("validation", "test")
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASS_LIST)):
        if len(line) == 2 and line[1] in OI_THINGS:
            mids.setdefault(line[0], line[1])
    say(f"Open Images: {len(mids)} of {len(OI_THINGS)} street and building labels found")
    labels, boxes = {}, {}
    for subset in subsets:
        for cells in csv.reader(oi_lines(s, OI_IMAGE_LABELS[subset])):
            if len(cells) == 4 and cells[2] in mids:
                try:
                    verdict = round(float(cells[3]))
                except ValueError:
                    continue
                picture = labels.setdefault(cells[0], {})
                name = mids[cells[2]]
                picture[name] = verdict if picture.get(name, verdict) == verdict else None
        for r in csv.DictReader(oi_lines(s, OI_BOXES[subset])):
            if r["LabelName"] in mids and r["ImageID"] in labels:
                boxes.setdefault(r["ImageID"], {}).setdefault(mids[r["LabelName"]], []).append({
                    "x1": float(r["XMin"]), "x2": float(r["XMax"]), "y1": float(r["YMin"]), "y2": float(r["YMax"]),
                    "group": r["IsGroupOf"] == "1", "depiction": r["IsDepiction"] == "1"})
    say(f"Open Images: {len(labels)} photos with a street or building label checked")
    photos = {}
    for subset in subsets:
        for r in csv.DictReader(oi_lines(s, OI_IMAGE_LISTS[subset])):
            licence = oi_licence_name(r.get("License") or "")
            if r["ImageID"] in labels and licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[r["ImageID"]] = (r["Subset"], licence, clean(r.get("Author")) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
    items, yes_count, no_count = [], 0, 0
    order = sorted(photos)
    random.Random(53).shuffle(order)
    for image_id in order:
        checked = labels[image_id]
        present = {n for n, v in checked.items() if v == 1}
        if not present & OI_STREET:
            continue
        found = boxes.get(image_id, {})
        if any(b["depiction"] for n in present for b in found.get(n, [])):
            continue                                       # a picture of a picture (a poster or a toy)
        subset, licence, author, page = photos[image_id]
        credit = (f"Photo by {author}" + (f" ({page})" if page else "") + f", {licence}; labels and boxes from Open "
                  f"Images V7 (Google), CC BY 4.0")
        rows = []
        for name in sorted(present, key=lambda n: (n not in OI_STREET, n)):
            rows.append({"question": OI_THINGS[name][0], "answer": oi_yes_answer(name, found.get(name, [])),
                         "credit": credit})
        for name in sorted(n for n, v in checked.items() if v == 0):
            if no_count < OI_MAX_NO * (yes_count + len(rows)):
                rows.append({"question": OI_THINGS[name][0], "answer": OI_THINGS[name][4], "credit": credit})
                no_count += 1
        yes_count += len(present)
        items.append((f"oi-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id), rows[:4]))
        if len(items) >= limit * 1.15 + 2:
            break
    say(f"Open Images: {len(items)} photos chosen ({yes_count} 'yes' and {no_count} 'no' answers)")
    return with_twins(fetch_all(items, workers=8)[:limit])


# ----------------------------------------------------------------- footpaths in Dhaka (Bangladesh)

DHAKA = ("m68g3h7p87", 1)
DHAKA_CREDIT = "Object Detection Dataset: Navigation Assistance for the Visually Impaired People (Ashik et al., " \
               "East West University, 2025), Mendeley Data m68g3h7p87, CC BY 4.0"
DHAKA_NAMES = ["a rubbish bin", "a building pillar", "a bus", "a CNG auto-rickshaw", "a car", "a bicycle",
               "an electric pole", "a food van", "a food cart", "the footpath", "a leguna (a small passenger truck)",
               "a motorcycle", "an obstacle", "a traffic cone", "a person", "a pickup truck", "a cycle rickshaw",
               "stairs", "a tree", "a truck", "a van", "a pedal van (a cargo tricycle)"]
DHAKA_PLURALS = {"a rubbish bin": "rubbish bins", "a building pillar": "building pillars", "a bus": "buses",
                 "a CNG auto-rickshaw": "CNG auto-rickshaws", "a car": "cars", "a bicycle": "bicycles",
                 "an electric pole": "electric poles", "a food van": "food vans", "a food cart": "food carts",
                 "a leguna (a small passenger truck)": "legunas (small passenger trucks)",
                 "a motorcycle": "motorcycles", "an obstacle": "obstacles", "a traffic cone": "traffic cones",
                 "a person": "people", "a pickup truck": "pickup trucks", "a cycle rickshaw": "cycle rickshaws",
                 "stairs": "stairs", "a tree": "trees", "a truck": "trucks", "a van": "vans",
                 "a pedal van (a cargo tricycle)": "pedal vans (cargo tricycles)"}
DHAKA_FOOTPATH, DHAKA_STAIRS = 9, 17
DHAKA_ASK_AHEAD = "What is in front of me on this path?"
DHAKA_ASK_FOOTPATH = "Where is the footpath?"


def dhaka_rows(boxes):
    """The questions and answers for one footpath photo from its marked objects (YOLO boxes or outlines)."""
    rows = []
    near = [b for b in boxes if b[0] != DHAKA_FOOTPATH and b[2] + b[4] / 2 > 0.45]   # their foot in the lower half
    if near:
        groups = {}
        for b in sorted(near, key=lambda b: -(b[2] + b[4] / 2)):
            groups.setdefault((b[0], side_of(b[1])), []).append(b)
        parts = []
        for (number, side), found in list(groups.items())[:4]:
            name = DHAKA_NAMES[number]
            thing = name if len(found) == 1 else count_words(len(found), name, DHAKA_PLURALS[name])
            parts.append(f"{thing} {side}")
        answer = capitalised(listed(parts)) + "."
        if any(b[0] == DHAKA_STAIRS for b in near):
            answer += " Take care at the stairs."
        elif any(1 / 3 <= b[1] <= 2 / 3 and b[2] + b[4] / 2 > 0.7 for b in near):
            answer += " Something is close in front of you: slow down."
        rows.append({"question": DHAKA_ASK_AHEAD, "answer": answer})
    paths = [b for b in boxes if b[0] == DHAKA_FOOTPATH]
    if paths:
        widest = max(paths, key=lambda b: b[3] * b[4])
        if widest[3] > 0.5 and 0.35 <= widest[1] <= 0.65:
            answer = "You are on the footpath: it goes on ahead of you."
        else:
            answer = f"The footpath is {side_of(widest[1])}."
        rows.append({"question": DHAKA_ASK_FOOTPATH, "answer": answer})
    return [dict(r, credit=DHAKA_CREDIT) for r in rows]


def base_frame(name):
    """A Roboflow file name without its copy marks ("frame_jpg.rf.123abc.jpg" -> "frame"), so the augmented copies
    of one photo count as one."""
    return re.sub(r"_(jpg|jpeg|png)\.rf\.[0-9a-f]+\.(jpg|jpeg|png|txt)$", "", name.rsplit("/", 1)[-1], flags=re.I)


def build_walkway_dhaka(limit):
    """The Dhaka footpath pack's pictures: [(name, JPEG or None, row)]. Lists the dataset's files on Mendeley Data
    and uses the validation and test frames only: the training set holds three altered copies (turned, flipped,
    brighter) of each frame, and its frame names repeat from video to video, so its copies cannot be told apart.
    Downloads the label and the picture of each frame used."""
    tree = mendeley_tree(*DHAKA)
    pictures, labels = {}, {}
    for path, url in tree.items():
        folder, _, name = path.partition("/")
        if folder not in ("valid", "test"):
            continue
        key = folder + "-" + name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        if "/images/" in "/" + name:
            pictures[key] = url
        elif "/labels/" in "/" + name:
            labels[key] = url
    keys = sorted(k for k in pictures if k in labels)
    say(f"Dhaka footpaths: {len(keys)} frames")
    random.Random(54).shuffle(keys)
    s, items = session(), []
    for key in keys:
        if len(items) >= limit * 1.1 + 2:
            break
        try:
            rows = dhaka_rows(yolo_boxes(s.get(labels[key], timeout=60).text))
        except Exception:  # noqa: BLE001 - left out
            continue
        if rows:
            items.append((f"dhaka-{safe_name(key.replace('_jpg.rf.', '-'))}.jpg", pictures[key], rows))
    return with_twins(fetch_all(items, workers=4, pause=0.2)[:limit])


# ----------------------------------------------------------------- Outdoor Navigation Dataset (Bucharest)

ONAV_ZIP = "https://zenodo.org/records/14043015/files/outdoor_navigation_dataset.zip?download=1"
ONAV_CREDIT = "Outdoor Navigation Dataset (Mihai Craciunescu, Politehnica University of Bucharest, 2024), " \
              "Zenodo 14043015, CC BY 4.0"
ONAV_CROSSWALK, ONAV_PEDESTRIAN, ONAV_RAMP, ONAV_ROAD, ONAV_SIDEWALK = range(5)


def onav_rows(boxes):
    """The questions and answers for one frame of the Outdoor Navigation Dataset from its marked areas."""
    rows = []
    crossings = [b for b in boxes if b[0] == ONAV_CROSSWALK]
    if crossings:
        nearest = max(crossings, key=lambda b: b[2] + b[4] / 2)
        where = "right in front of you" if 0.33 <= nearest[1] <= 0.67 else side_of(nearest[1])
        rows.append({"question": "Is there a pedestrian crossing here?",
                     "answer": f"Yes, there is a pedestrian crossing {where}. Check the traffic or the pedestrian "
                               f"light before you cross."})
    else:
        rows.append({"question": "Is there a pedestrian crossing here?",
                     "answer": "No, I can't see a pedestrian crossing here."})
    ramps = [b for b in boxes if b[0] == ONAV_RAMP]
    if ramps:
        nearest = max(ramps, key=lambda b: b[2] + b[4] / 2)
        rows.append({"question": "Is there a ramp nearby?",
                     "answer": f"Yes, there is a ramp (a slope instead of a step) {side_of(nearest[1])}"
                               f"{distance_word(nearest[3] * nearest[4])}."})
    pavements = [b for b in boxes if b[0] == ONAV_SIDEWALK]
    if pavements:
        widest = max(pavements, key=lambda b: b[3] * b[4])
        if widest[3] > 0.5 and 0.35 <= widest[1] <= 0.65 and widest[2] + widest[4] / 2 > 0.85:
            answer = "You are on the pavement: it goes on ahead of you."
        else:
            answer = f"The pavement is {side_of(widest[1])}."
        rows.append({"question": "Where is the pavement (sidewalk)?", "answer": answer})
    people = [b for b in boxes if b[0] == ONAV_PEDESTRIAN and 0.25 <= b[1] <= 0.75 and b[2] + b[4] / 2 > 0.55]
    if people:
        rows.append({"question": "Is anyone in my way?",
                     "answer": f"Yes, {count_words(len(people), 'one person is', 'people are')} close ahead of you."})
    return [dict(r, credit=ONAV_CREDIT) for r in rows]


def build_outdoor_navigation(limit):
    """The Outdoor Navigation pack's pictures: [(name, JPEG or None, row)]. Downloads the 80 MB zip and keeps one
    copy of each frame (the training set holds three altered copies of each)."""
    z = zipfile.ZipFile(io.BytesIO(session().get(ONAV_ZIP, timeout=600).content))
    names = z.namelist()
    pictures, labels = {}, {}
    for name in names:
        if "/images/" in name and name.lower().endswith((".jpg", ".jpeg", ".png")):
            pictures.setdefault(base_frame(name), name)
        elif "/labels/" in name and name.endswith(".txt"):
            labels.setdefault(base_frame(name), name)
    keys = sorted(k for k in pictures if k in labels)
    say(f"Outdoor Navigation: {len(keys)} frames")
    random.Random(55).shuffle(keys)
    out = []
    for key in keys:
        rows = onav_rows(yolo_boxes(z.read(labels[key]).decode("utf-8", "replace")))
        data = smaller(z.read(pictures[key]))
        if rows and data:
            out.append((f"onav-{safe_name(key)}.jpg", data, rows))
        if len(out) >= limit:
            break
    return with_twins(out)


# ----------------------------------------------------------------- Seoul pavements

SEOUL = "https://zenodo.org/records/22908353/files/"
SEOUL_ZIPS = ("imagery_1.zip", "imagery_2.zip", "imagery_3.zip")
SEOUL_CREDIT = "Seoul Sidewalk Accessibility Image Dataset (Zenodo 22908353), CC0"
# The grades of the Korean guideline for pavements (the dataset's ground_truth_protocol.md).
SEOUL_GRADES = {
    "A": "Yes, it is in very good condition: smooth, with no cracks or bumps.",
    "B": "Yes, it is in good condition: not entirely smooth, but even overall.",
    "C": "It is in fair condition: you can walk on it, but the surface is worn, so take care.",
    "D": "No, it is in poor condition: there are hazards on much of the surface. Walk carefully or find another way.",
    "E": "No, it is in very poor condition: it is not possible to walk on it normally. Find another way.",
}


def seoul_slope(percent):
    """A slope in plain words, to follow "it is"."""
    percent = abs(percent)
    if percent < 1:
        return f"nearly level ({percent:g}%)"
    if percent <= 3:
        return f"gently sloping ({percent:g}%)"
    if percent <= 5.6:
        return f"noticeably sloping ({percent:g}%)"
    return f"steep for a pavement ({percent:g}%), so take care"


def seoul_rows(record):
    """The questions and answers for one Seoul pavement from its measured attributes."""
    rows = []
    grade = (record.get("damage") or "").strip().upper()
    if grade in SEOUL_GRADES:
        rows.append({"question": "Is this pavement in good condition?", "answer": SEOUL_GRADES[grade]})
    try:
        width = float(record["width"])
        narrow = " That is narrow: two people can hardly pass each other." if width < 1.5 else ""
        rows.append({"question": "How wide is this pavement?",
                     "answer": f"It is about {width:.1f} metres wide.{narrow}"})
        running, cross = float(record["running_slope"]), float(record["cross_slope"])
        rows.append({"question": "Does this pavement slope?",
                     "answer": f"Along the way it is {seoul_slope(running)}; from side to side it is "
                               f"{seoul_slope(cross)}."})
    except (KeyError, TypeError, ValueError):
        pass
    return [dict(r, credit=SEOUL_CREDIT) for r in rows]


def build_seoul_sidewalks(limit):
    """The Seoul pavement pack's pictures: [(name, JPEG or None, row)]. Reads the measured attributes and takes the
    photos one by one out of the three zips (4.6 GB in all; only the photos used are downloaded). Most photos are
    HEIC: read with pillow-heif when it is installed, otherwise left out."""
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        heic = True
    except ImportError:
        heic = False
        say("Seoul pavements: pillow-heif is not installed, so only the JPEG photos are used")
    s = session()
    text = s.get(SEOUL + "summary_attributes.csv?download=1", timeout=120).content.decode("utf-8-sig")
    records = {r["filename"].lower(): r for r in csv.DictReader(io.StringIO(text))}
    say(f"Seoul pavements: {len(records)} measured pavements")
    out = []
    for zip_name in SEOUL_ZIPS:
        z = remote_zip(f"{SEOUL}{zip_name}?download=1", s)
        names = [n for n in z.namelist() if n.rsplit("/", 1)[-1].lower() in records and "__MACOSX" not in n]
        names = [n for n in names if heic or not n.lower().endswith((".heic", ".heif"))]
        random.Random(56).shuffle(names)
        for name in names[:max(1, limit - len(out))]:
            record = records[name.rsplit("/", 1)[-1].lower()]
            data = smaller(z.read(name))
            rows = seoul_rows(record)
            if data and rows:
                out.append((f"seoul-{name.rsplit('/', 1)[-1].rsplit('.', 1)[0]}.jpg", data, rows))
        if len(out) >= limit:
            break
    random.Random(57).shuffle(out)
    return with_twins(out[:limit])


# ----------------------------------------------------------------- Dollar Street (Gapminder)

DS_API = "https://api.dollarstreet.org/v1"
DS_PAGE = "https://www.gapminder.org/dollar-street/families/"
# The topics used: ("thing", answer) for an object, ("place", answer) for a room or a scene. Topics about feelings,
# activities or money (dreams, most loved items, income) are left out.
DS_TOPICS = {
    "alarm-clocks": ("thing", "an alarm clock"), "arm-watches": ("thing", "a wristwatch"),
    "armchairs": ("thing", "an armchair"), "beds": ("thing", "a bed"), "bikes": ("thing", "a bicycle"),
    "books": ("thing", "books"), "bowls": ("thing", "a bowl"), "car-keys": ("thing", "car keys"),
    "cars": ("thing", "a car"), "ceilings": ("thing", "a ceiling"), "chickens": ("thing", "chickens"),
    "cleaning-equipment": ("thing", "cleaning equipment"), "computers": ("thing", "a computer"),
    "cooking-pots": ("thing", "a cooking pot"), "cooking-utensils": ("thing", "cooking utensils"),
    "cups": ("thing", "cups"), "cutlery": ("thing", "cutlery"), "diapers": ("thing", "nappies (diapers)"),
    "dish-brushes": ("thing", "a dish brush"), "dish-racks": ("thing", "a dish rack"),
    "dishwashers": ("thing", "a dishwasher"), "dish-washing-soaps": ("thing", "washing-up liquid (dish soap)"),
    "earings": ("thing", "earrings"), "everyday-shoes": ("thing", "everyday shoes"),
    "floors": ("thing", "a floor"), "freezers": ("thing", "a freezer"), "front-doors": ("thing", "a front door"),
    "frontdoor-keys": ("thing", "front-door keys"), "fruits": ("thing", "fruit"),
    "goats": ("thing", "goats"), "grains": ("thing", "grains"), "hair-brushes": ("thing", "a hairbrush"),
    "instruments": ("thing", "a musical instrument"), "jackets": ("thing", "a jacket"),
    "jewelry": ("thing", "jewellery"), "kitchen-sinks": ("thing", "a kitchen sink"),
    "light-sources": ("thing", "a light"), "lock-on-front-doors": ("thing", "the lock on a front door"),
    "make-up": ("thing", "make-up"), "meat": ("thing", "meat"), "medication": ("thing", "medicine"),
    "mosquito-protections": ("thing", "mosquito protection"), "motorcycles": ("thing", "a motorcycle"),
    "music-equipment": ("thing", "music equipment"), "necklaces": ("thing", "a necklace"),
    "ovens": ("thing", "an oven"), "papers": ("thing", "papers"), "pens": ("thing", "pens"),
    "pet-foods": ("thing", "pet food"), "pets": ("thing", "a pet"), "phones": ("thing", "a phone"),
    "plates": ("thing", "plates"), "plates-of-food": ("thing", "a plate of food"),
    "power-outlets": ("thing", "a power socket (outlet)"), "power-switches": ("thing", "a light switch"),
    "radios": ("thing", "a radio"), "refrigerators": ("thing", "a fridge"), "roofs": ("thing", "a roof"),
    "rugs": ("thing", "a rug"), "salt": ("thing", "salt"), "shampoo": ("thing", "shampoo"),
    "shoes": ("thing", "shoes"), "showers": ("thing", "a shower"), "soaps": ("thing", "soap"),
    "sofas": ("thing", "a sofa"), "sources-of-cool": ("thing", "something to keep cool, such as a fan"),
    "sources-of-heat": ("thing", "a heater"), "spices": ("thing", "spices"), "stoves": ("thing", "a stove"),
    "toilet-paper": ("thing", "toilet paper"), "toilets": ("thing", "a toilet"), "tools": ("thing", "tools"),
    "tooth-paste": ("thing", "toothpaste"), "toothbrushes": ("thing", "a toothbrush"), "toys": ("thing", "toys"),
    "trash": ("thing", "rubbish (trash)"), "tvs": ("thing", "a television"), "vegetables": ("thing", "vegetables"),
    "wall-clocks": ("thing", "a wall clock"), "wall-decorations": ("thing", "wall decorations"),
    "wardrobes": ("thing", "a wardrobe"), "washing-detergent": ("thing", "washing detergent"),
    "water-outlets": ("thing", "a water tap or outlet"), "wheel-barrows": ("thing", "a wheelbarrow"),
    "backyards": ("place", "a backyard"), "bathrooms": ("place", "a bathroom"), "bedrooms": ("place", "a bedroom"),
    "child-rooms": ("place", "a child's room"), "hallways": ("place", "a hallway"),
    "house-overviews": ("place", "the outside of a home"), "kitchens": ("place", "a kitchen"),
    "living-rooms": ("place", "a living room"), "parking-lots": ("place", "a parking area"),
    "places-for-dinner": ("place", "the place where a family eats dinner"),
    "storage-rooms": ("place", "a storage room"),
    "street-view": ("place", "a street outside a home"), "vegetable-plots": ("place", "a vegetable plot"),
    "waste-dumps": ("place", "a rubbish dump"), "work-areas": ("place", "a work area"),
    "worship-places": ("place", "a place of worship"),
}
DS_WHERE = {"street-view", "house-overviews"}              # the only topics asked "Where might this photo be from?"
DS_IGNORED = {"visit", "families", "homes"}                # topics added to many photos: not a second subject


def ds_hits(s, topic):
    """Every photo of one Dollar Street topic: the search gives at most 60 photos, so the families' income range is
    cut into slices until each slice gives all of its photos."""
    hits, slices = {}, [(0, 100000)]
    while slices:
        low, high = slices.pop()
        page = None
        for attempt in range(3):
            time.sleep(0.3 + 2 * attempt)
            try:
                page = s.get(f"{DS_API}/search/families", timeout=60, params={
                    "topic": topic, "featuredOnly": "false", "media": "image", "lng": "en", "min": low,
                    "max": high}).json()
            except Exception:  # noqa: BLE001 - tried again
                page = None
            if isinstance(page, dict):
                break
        if not isinstance(page, dict):
            say(f"  Dollar Street {topic}: incomes {low}-{high} could not be read")
            continue
        found = [h for group in (page.get("hits") or {}).values() for h in group]
        if page.get("totalHits", 0) > len(found) and high - low > 1:
            middle = (low + high) / 2 if high < 100000 else 1000
            slices += [(low, middle), (middle, high)] if middle > low else []
            continue
        for h in found:
            hits[h["id"]] = h
    return list(hits.values())


def ds_photographers(s, media_id, cache):
    """The names of the photographers of a family (from one of its photos), remembered by family."""
    try:
        media = s.get(f"{DS_API}/media/{media_id}", params={"lng": "en"}, timeout=60).json()
    except Exception:  # noqa: BLE001 - unnamed
        return ""
    place = media.get("place") or {} if isinstance(media, dict) else {}
    names = [v.get("name") for v in place.get("visitors") or []
             if "photographer" in [str(k).lower() for k in v.get("kind") or []]]
    if not names and isinstance(media, dict):
        own = media.get("photographer")
        names = [own.get("name") if isinstance(own, dict) else own] if own else []
    cache[place.get("id")] = ", ".join(str(n) for n in names if n)
    return cache[place.get("id")]


def this_is(words):
    """ "This is a bed." or "These are goats." (plural when the words end in s, not counting a note in brackets,
    and have no "a", "an" or "the")."""
    plain = re.sub(r"\s*\(.*?\)", "", words)
    plural = plain.endswith("s") and not re.match(r"(a|an|the)\s", plain)
    return f"{'These are' if plural else 'This is'} {words}."


def build_dollar_street(limit):
    """The Dollar Street pack's pictures: [(name, JPEG or None, row)]. Takes about the same number of photos from
    each topic, each with its country and photographers, and asks what the thing or the place is."""
    s, items, photographers = session(), [], {}
    topics = sorted(DS_TOPICS)
    random.Random(58).shuffle(topics)
    per_topic = max(1, round(limit * 1.15 / len(topics)) + (1 if limit < len(topics) else 0))
    for topic in topics:
        if len(items) >= limit * 1.15:
            break
        hits = [h for h in ds_hits(s, topic) if (h.get("images") or {}).get("full1024")
                and not ({t["id"] for t in h.get("topics") or []} - DS_IGNORED - {topic}) & set(DS_TOPICS)]
        random.Random(topic).shuffle(hits)
        for h in hits[:per_topic]:
            place = h.get("place") or {}
            country = (h.get("country") or place.get("country") or {}).get("name", "")
            who = photographers.get(place.get("id"))
            if who is None:
                time.sleep(0.3)
                who = ds_photographers(s, h["id"], photographers)
            credit = (f"Photo: {who or 'Gapminder'}, Dollar Street (Gapminder, www.gapminder.org/dollar-street), "
                      f"CC BY 4.0: {DS_PAGE}{place.get('slug', '')}")
            kind, words = DS_TOPICS[topic]
            if kind == "thing":
                rows = [{"question": "What is this?", "answer": this_is(words), "credit": credit}]
            else:
                rows = [{"question": "What kind of place is this?", "answer": this_is(words), "credit": credit}]
            if topic in DS_WHERE and country:
                rows.append({"question": "Where might this photo be from?",
                             "answer": f"It was taken in {country}.", "credit": credit})
            items.append((f"ds-{h['id']}.jpg", h["images"]["full1024"], rows))
        say(f"Dollar Street {topic}: {len(hits)} photos")
    random.Random(59).shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.15) + 2], workers=4, pause=0.2)[:limit])


# ----------------------------------------------------------------- GeoDE (Princeton)

GEODE = "MLap/GeoDE"                                       # a copy of the Princeton release on Hugging Face
GEODE_CREDIT = "GeoDE (Ramaswamy, Lin, Zhao, Adcock, van der Maaten, Ghadiyaram and Russakovsky, NeurIPS 2023), " \
               "CC BY, https://geodiverse-data-collection.cs.princeton.edu (via huggingface.co/datasets/MLap/GeoDE)"
GEODE_NAMES = {
    "bag": "a bag", "chair": "a chair", "dustbin": "a dustbin (rubbish bin)", "hairbrush_comb": "a hairbrush or comb",
    "hand_soap": "hand soap", "hat": "a hat", "light_fixture": "a light fitting", "light_switch": "a light switch",
    "toothbrush": "a toothbrush", "toothpaste_toothpowder": "toothpaste", "candle": "a candle",
    "cleaning_equipment": "cleaning equipment", "cooking_pot": "a cooking pot", "jug": "a jug",
    "lighter": "a lighter", "medicine": "medicine", "plate_of_food": "a plate of food", "spices": "spices",
    "stove": "a stove", "toy": "a toy", "backyard": "a backyard", "car": "a car", "fence": "a fence",
    "front_door": "a front door", "house": "a house", "road_sign": "a road sign",
    "streetlight_lantern": "a street light", "tree": "a tree", "truck": "a lorry (truck)",
    "waste_container": "a large rubbish container", "bicycle": "a bicycle", "boat": "a boat", "bus": "a bus",
    "dog": "a dog", "flag": "a flag", "monument": "a monument", "religious_building": "a religious building",
    "stall": "a market stall", "storefront": "a shop front", "wheelbarrow": "a wheelbarrow",
}


def build_geode(limit):
    """The GeoDE pack's pictures: [(name, JPEG or None, row)]. The copy's files are sorted by object, so groups of
    100 rows are read from files spread across all of them, a few pictures from each group."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    files = sorted(f for f in HfApi().list_repo_files(GEODE, repo_type="dataset") if f.endswith(".parquet"))
    fs, out = HfFileSystem(), []
    groups = max(2, math.ceil(limit / 25))                   # 25 pictures from each group of 100
    per_group = math.ceil(limit / groups)
    rng = random.Random(60)
    picks = sorted(rng.sample(range(len(files) * 10), min(groups, len(files) * 10)))
    for pick in picks:
        name = files[pick // 10]
        with fs.open(f"datasets/{GEODE}/{name}", "rb", block_size=1 << 22) as f:
            parquet = pq.ParquetFile(f)
            group = (pick % 10) % parquet.metadata.num_row_groups
            table = parquet.read_row_group(group).to_pylist()
        rng.shuffle(table)
        taken = 0
        for row in table:
            words = GEODE_NAMES.get(row.get("object") or "", (row.get("object") or "").replace("_", " "))
            data = smaller((row.get("image") or {}).get("bytes") or b"")
            if not data or not words:
                continue
            out.append((f"geode-{len(out)}.jpg", data, {"question": "What is this?",
                        "answer": this_is(words), "credit": GEODE_CREDIT}))
            taken += 1
            if taken >= per_group:
                break
        say(f"GeoDE {name} group {group}: {len(out)} pictures so far")
        if len(out) >= limit:
            break
    rng.shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- the packs

LIFE_PACKS = {
    "ptl_crossings": (build_ptl_crossings, "Pedestrian-Traffic-Lights (PTL) dataset (Samuel Yu, Heon Lee and John "
                                           "Kim, 2019), MIT licence: https://github.com/samuelyu2002/ImVisible "
                                           "(photos taken by the authors in Shanghai)."),
    "uroac_crossings": (build_uroac_crossings, "UrOAC: Urban Objects in Any-light Conditions (Francisco Gomez-Donoso, "
                                               "Marcos Moreno-Martinez and Miguel Cazorla, University of Alicante, "
                                               "2022), CC BY 4.0: https://data.mendeley.com/datasets/fcrmp92ckn/2 "
                                               "(faces and number plates masked by the authors)."),
    "open_images_street": (build_open_images_street, "Google Open Images V7: labels and boxes CC BY 4.0 "
                                                     "(https://storage.googleapis.com/openimages/web/index.html); "
                                                     "each photo CC BY 2.0, its photographer credited below."),
    "walkway_dhaka": (build_walkway_dhaka, "Object Detection Dataset: Navigation Assistance for the Visually Impaired "
                                           "People using YOLOv11 (Md Ashikur Rahoman Ashik et al., East West "
                                           "University, 2025), CC BY 4.0: https://data.mendeley.com/datasets/"
                                           "m68g3h7p87/1"),
    "outdoor_navigation": (build_outdoor_navigation, "Outdoor Navigation Dataset (Mihai Craciunescu, Politehnica "
                                                     "University of Bucharest, 2024), CC BY 4.0: "
                                                     "https://zenodo.org/records/14043015"),
    "seoul_sidewalks": (build_seoul_sidewalks, "Seoul Sidewalk Accessibility Image Dataset, CC0: "
                                               "https://zenodo.org/records/22908353"),
    "dollar_street": (build_dollar_street, "Dollar Street by Gapminder, CC BY 4.0 (Free material from "
                                           "www.gapminder.org): https://www.gapminder.org/dollar-street; each photo's "
                                           "photographer credited below."),
    "geode": (build_geode, "GeoDE: a Geographically Diverse Evaluation Dataset for Object Recognition (Vikram V. "
                           "Ramaswamy, Sing Yu Lin, Dora Zhao, Aaron B. Adcock, Laurens van der Maaten, Deepti "
                           "Ghadiyaram and Olga Russakovsky, Princeton University, NeurIPS 2023), CC BY: "
                           "https://geodiverse-data-collection.cs.princeton.edu"),
}

# How many pictures a full build takes from each collection (about what each offers after the checks).
LIFE_LIMITS = {
    "ptl_crossings": 5000,
    "uroac_crossings": 1000,
    "open_images_street": 5000,
    "walkway_dhaka": 1000,
    "outdoor_navigation": 700,
    "seoul_sidewalks": 514,
    "dollar_street": 8000,
    "geode": 6000,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one world-life pack builder.")
    parser.add_argument("key", choices=sorted(LIFE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = LIFE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {sum(1 for e in entries if e[1])} pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
