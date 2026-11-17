"""Pack builders for practical home life: things a blind person often needs a sighted helper for at home. Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" where the source gives one (the
country at a Commons photo's camera coordinates) and "child": true where the picture may show a child (the
picture-making trainer leaves those rows out). A picture with more than one question comes once with its JPEG and
then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins), so the zip holds each
picture only once. The limit counts pictures.

Every answer is a fixed sentence written here from the source's own labels: a category's name, a label people checked
by hand, a time people read off a clock, the number a display was made to show (nothing is written by an AI model).
Where a Commons file also has a real caption or description, it is used as it is for "Write a short description of
this picture for someone who cannot see it." Descriptions with sexual or pitying words are left out.

The packs (all open: CC0, public domain, CC BY, MIT or Apache, checked at the source):
  clock_times          "It's About Time: Analog Clock Reading in the Wild" (Charig Yang, Weidi Xie and Andrew
                       Zisserman, CVPR 2022; github.com/charigyang/itsabouttime, MIT licence): the hour and minute that
                       people read by hand off the analogue clock in 1,317 Open Images photos and 1,911 COCO photos.
                       Photos with more than one clock are left out (the label is for one of them). Open Images photos
                       are checked to be CC BY 2.0 one by one (photographer named); COCO photos are kept only when
                       COCO lists them as CC BY 2.0 or "no known copyright restrictions". "What time does this clock
                       show?" -> "It shows 6:09, nine minutes past six." (an analogue clock cannot say morning or
                       evening, and the answer does not guess).
  seven_segment        7SEG_OCR (MiXaiLL76 on Hugging Face, MIT licence): 3,333 computer-made pictures of seven-segment
                       LED and LCD displays (the digits drawn onto photos of real display boards), each with the number
                       it shows. "What number does this display show?" A first step to reading oven, microwave, scale,
                       thermometer and meter displays.
  open_images_home     Google Open Images V7 (validation and test sets): labels people checked by hand for household
                       pests (bed bugs, cockroaches, termites, mosquitoes, ticks, ants, wasps, hornets, mice, rats,
                       flies, spiders, mould), tools and hardware (drills, saws, tape measures, nails, screws, bolts,
                       pliers, chisels, plungers, taps, garden tools, padlocks), devices with a display or plug
                       (bathroom and kitchen scales, blood-glucose meters, blood-pressure monitors, digital clocks,
                       timers, cash machines, plugs, USB and aerial cables, power strips, extension leads, irons),
                       personal care and accessories (rings, jewellery, nail polish, mascara, toothpaste, deodorant,
                       soap, wigs, hats), hairstyles of adults (braids, dreadlocks, Afro, ponytail, long hair, beards,
                       moustaches) and the kitchen (saucepans, stock pots, graters, peelers, rolling pins, colanders,
                       and whether a gas burner is lit or a pot is boiling). Only labels that open_images_objects does
                       not already ask about. Labels CC BY 4.0; each photo CC BY 2.0 (checked photo by photo),
                       photographer named. "Is there a bed bug in this picture?" (no only where people checked and
                       rejected it), "What tools are in this picture?", "Is the burner on?" ...
  commons_pests        Wikimedia Commons species and damage categories: bed bugs, German, American and Oriental
                       cockroaches, termites and the wood they damaged, ants that come indoors (Pharaoh, Argentine,
                       carpenter, fire ants), wasp and hornet nests, ticks (deer, castor bean, American dog, lone star),
                       house mosquitoes and the tiger and yellow-fever mosquitoes, clothes moths, carpet beetles, cat
                       fleas, silverfish, head lice, rodent damage, wood rot, water damage and black mould. Many are
                       US government photos (CDC, USDA, EPA: public domain). "Is there a bed bug in this picture?"
                       and "What pest is this?", and a careful "no" for look-alikes ("No: this is a carpet beetle,
                       not a bed bug.").
  commons_appliances   Commons: thermostats, control knobs, microwave ovens, washing machines, kitchen and bathroom
                       scales, thermometers, blood-glucose meters, blood-pressure monitors, seven-segment displays,
                       lift (elevator) buttons, cash machines, ticket machines and self-service check-in machines.
                       "What is this?" and the file's own description (which often gives the reading). Commons has
                       no category for cooker knobs, oven or washing-machine control panels, or indicator lights
                       (searched in November 2026); Open Images and seven_segment cover some of that.
  commons_connectors   Commons: mains plugs and sockets by standard (Types A to O, with where each is used), USB
                       (all kinds), USB-C, micro-USB, Lightning, HDMI and audio jacks, battery sizes (AA, AAA, C, D,
                       9-volt, button cells) and chargers. Commons has no usable category for the Type C Europlug or
                       the Danish Type K, so those two are missing. "What kind of plug is this, and where is it used?"
  laundry_symbols      Commons' laundry-symbol files (Category:Laundry symbols and its Tabler icons, CC0, public domain,
                       CC BY or MIT, checked file by file): each symbol with its meaning, taken from the file's own
                       name ("Waschen 30s.svg" -> "Machine wash at 30 °C, gentle cycle."), and computer-made care
                       labels of four or five of them in a row with every meaning in order ("What do these washing
                       symbols mean?" -> "Machine wash at 30 °C. Do not bleach. Do not tumble dry. Iron on low ...").
                       Photos of real care labels (Category:Laundry tags) come with their own descriptions. The symbols
                       are a GINETEX trademark (a trademark, not a copyright: describing them is not limited by it).
  commons_tools        Commons: hand tools, power tools, screws, nails, bolts, nuts and washers, wall plugs, plumbing
                       parts and garden tools. "What tool is in this picture?"
  commons_personal     Commons: toiletries and cosmetics (shampoo, conditioner, toothpaste, deodorant, shower gel, soap,
                       lipstick, mascara, nail polish), jewellery, wristwatches, glasses, hats and bags. "What is
                       this?" and, for shampoo and conditioner, "Is this shampoo or conditioner?"
  commons_hairstyles   Commons hairstyle categories (braids, cornrows, dreadlocks, ponytails, crew cuts, shaved heads,
                       bald men, grey and long hair). Adults only: a file whose title or
                       words name a child is left out. Described plainly: "What hairstyle does this person have?" ->
                       "Their hair is in braids."
  commons_kitchen      Commons: gas flames on a cooker (only files whose words name a stove, burner, hob or pan: "Is the
                       burner on?" -> "Yes: there is a flame ..."), gas and induction cookers, boiling water, table
                       settings, kitchen utensils and cookware. "What is this?"

Share-alike, non-commercial and research collections on the same subjects (Open Beauty Facts, Open Products Facts,
Open Pet Food Facts, Commons BY-SA files, DTD patterns ...) are kit download entries in
training-kit/kit/home_sources.py, with the sign-up and left-out collections listed there.

    python packs/home_packs.py clock_times --limit 8      (prints a few rows: a quick check)
"""

import csv
import io
import json
import math
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, ALT_TEXT
from food_packs import (listed, with_twins, count_pictures, oi_lines, oi_licence_name, commons_get, commons_members,
                        OI_LABELS, OI_CLASSES, OI_IMAGES, OI_PICTURE)
from everyday_packs import OI_HOME
from expression_packs import mark_child, child_count, CHILD, OI_CHILD
from places import where, country_at

NUDE = re.compile(r"\b(nude|naked|nudity|topless|undress\w*|erotic|sex\w*|porn\w*|lingerie|underwear)\b", re.I)
# A photographer's own story ("Okay so here is my big rant ..."), not a description of the picture.
FIRST_PERSON = re.compile(r"(^\s*(okay|ok|so|well)\b)|\b(I|I'm|I've|my|me|we|our)\b")
NOT_RESPECTFUL = re.compile(r"\b(ugly|weird|freak\w*|bad hair|messy|unkempt|ghetto|nappy|savage|exotic)\b", re.I)


# ----------------------------------------------------------------- clock_times (It's About Time, MIT)

CLOCK_DATA = "https://raw.githubusercontent.com/charigyang/itsabouttime/main/data/"
CLOCK_FILES = {"openimages": CLOCK_DATA + "openimg_final.csv", "coco": CLOCK_DATA + "coco_final.csv"}
# The Open Images photos with clocks are in its training set; its list (with each photo's licence) is 638 MB and
# sorted by picture, so it is read only until every wanted photo is found.
OI_TRAIN_BOXABLE = "https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv"
CLOCK_ASK = "What time does this clock show?"
CLOCK_CREDIT = ("Time read by hand in 'It's About Time: Analog Clock Reading in the Wild' (Yang, Xie and Zisserman, "
                "CVPR 2022), MIT licence, https://github.com/charigyang/itsabouttime; ")
HOURS = ["twelve", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
MINUTE_WORDS = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                "thirteen", "fourteen", "quarter", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
                "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six",
                "twenty-seven", "twenty-eight", "twenty-nine", "half"]


def clock_words(hour, minute):
    """ "6:09, nine minutes past six", "quarter to seven" ...: the time a clock shows, said both ways."""
    hour = hour % 12 or 12
    digits = f"{hour}:{minute:02d}"
    if minute == 0:
        said = f"{HOURS[hour]} o'clock"
    elif minute <= 30:
        words = MINUTE_WORDS[minute]
        said = f"{words}{'' if words in ('quarter', 'half') else (' minute' if minute == 1 else ' minutes')} " \
               f"past {HOURS[hour]}"
    else:
        left = 60 - minute
        words = MINUTE_WORDS[left]
        said = f"{words}{'' if words == 'quarter' else (' minute' if left == 1 else ' minutes')} " \
               f"to {HOURS[hour % 12 + 1]}"
    return f"It shows {digits}, {said}."


def utf8(text):
    """Text from Open Images' lists read as Latin-1 by mistake ("MusÃ©e") put right ("Musée"); other text unchanged."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def clock_rows(s, url):
    """The clock list's rows with exactly one clock: [(picture file name or id, hour, minute)]."""
    out = []
    for r in csv.DictReader(io.StringIO(s.get(url, timeout=120).text)):
        boxes = json.loads(r.get("bbox_gt") or "[]")
        if len(boxes) == 1:
            out.append((r["file_name"], r["img_id"], int(r["hour"]), int(r["minute"])))
    return out


def build_clock_times(limit):
    """The clock pack: Open Images and COCO photos with one analogue clock and the time people read off it, half and
    half; only photos whose own licence is free."""
    s, items = session(), []
    want = int(limit * 1.2) + 2
    oi_rows = clock_rows(s, CLOCK_FILES["openimages"])
    coco_rows = clock_rows(s, CLOCK_FILES["coco"])
    say(f"Clocks: {len(oi_rows)} Open Images and {len(coco_rows)} COCO photos with one clock")
    # Open Images: each photo's licence and photographer from the training list (read until all are found).
    wanted = {img_id: (hour, minute) for _, img_id, hour, minute in oi_rows}
    enough = len(wanted) if limit >= 200 else want // 2 + 2       # a quick check stops after a few
    found = 0
    for r in csv.DictReader(oi_lines(s, OI_TRAIN_BOXABLE)):
        if r["ImageID"] not in wanted:
            continue
        found += 1
        licence = oi_licence_name(r.get("License") or "")
        if licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
            hour, minute = wanted[r["ImageID"]]
            author = utf8(clean(r.get("Author"))) or "an unnamed photographer"
            page = r.get("OriginalLandingURL") or ""
            credit = CLOCK_CREDIT + f"photo by {author}{f' ({page})' if page else ''}, {licence}, from Open Images V7"
            items.append((f"clock-oi-{r['ImageID']}.jpg", OI_PICTURE.format(subset="train", image_id=r["ImageID"]),
                          {"question": CLOCK_ASK, "answer": clock_words(hour, minute), "credit": credit}))
        if found >= enough:
            break
    say(f"Clocks: {len(items)} free Open Images photos ({found} of {len(wanted)} found in the training list)")
    # COCO: only photos COCO lists as CC BY 2.0 or no known copyright (build_packs.coco_licences).
    free = build_packs.coco_licences()
    coco = []
    for file_name, img_id, hour, minute in coco_rows:
        url = free.get(int(img_id))
        if url:
            coco.append((f"clock-coco-{img_id}.jpg", url,
                         {"question": CLOCK_ASK, "answer": clock_words(hour, minute),
                          "credit": CLOCK_CREDIT + "photo from COCO (cocodataset.org), CC BY 2.0 or no known "
                                                   f"copyright restrictions, {url}"}))
    say(f"Clocks: {len(coco)} free COCO photos")
    random.Random(62).shuffle(coco)
    items = items[:want // 2] + coco[:want - min(len(items), want // 2)]
    random.Random(63).shuffle(items)
    return fetch_all(items, workers=8)[:limit]


# ----------------------------------------------------------------- seven_segment (7SEG_OCR, MIT)

SEVEN_SEG_REPO = "MiXaiLL76/7SEG_OCR"
SEVEN_SEG_FILE = "data/train-00000-of-00001.parquet"
SEVEN_SEG_REVISION = "59873e636d5bd8bd850b3ba5788ee761cef5e895"
SEVEN_SEG_CREDIT = ("7SEG_OCR, synthetic seven-segment display pictures, by MiXaiLL76, MIT licence, "
                    "https://huggingface.co/datasets/MiXaiLL76/7SEG_OCR")


def display_words(text):
    """ "The display shows 6.691." (a minus sign said as "minus")."""
    text = text.strip()
    shown = ("minus " + text[1:]) if text.startswith("-") else text
    return f"The display shows {shown}."


def build_seven_segment(limit):
    """The seven-segment pack: pictures and the number each shows, from the one 202 MB Parquet file."""
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    path = hf_hub_download(SEVEN_SEG_REPO, SEVEN_SEG_FILE, repo_type="dataset", revision=SEVEN_SEG_REVISION)
    table = pq.ParquetFile(path)
    out, rng = [], random.Random(71)
    for batch in table.iter_batches(batch_size=200, columns=["image", "text"]):
        for r in batch.to_pylist():
            text = clean(r.get("text"))
            if not re.fullmatch(r"-?[\d.]+", text or ""):
                continue
            data = smaller((r.get("image") or {}).get("bytes") or b"")
            if data:
                out.append((f"sevenseg-{len(out):05d}.jpg", data,
                            {"question": rng.choice(("What number does this display show?",
                                                     "What does the display say?", "Read the display.")),
                             "answer": display_words(text), "credit": SEVEN_SEG_CREDIT}))
        if len(out) >= limit * 3 and limit < 1000:
            break
    rng.shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- open_images_home (Open Images V7)

OI_PESTS = {"Bed bug": "a bed bug", "Cockroach": "a cockroach", "Termite": "a termite", "Mosquito": "a mosquito",
            "Tick": "a tick", "Ant": "an ant", "Wasp": "a wasp", "Hornet": "a hornet", "Mouse": "a mouse",
            "Rat": "a rat", "Fly": "a fly", "Spider": "a spider", "Mold": "mould"}
OI_TOOLS = {"Drill (Tool)": "a drill", "Chainsaw": "a chainsaw", "Hand saw": "a hand saw", "Saw": "a saw",
            "Ruler": "a ruler", "Tape measure": "a tape measure", "Nail (Construction)": "nails", "Screw": "screws",
            "Bolt": "bolts", "Lawn mower": "a lawn mower", "Shovel": "a shovel", "Rake": "a rake", "Axe": "an axe",
            "Pliers": "pliers", "Chisel": "a chisel", "Plunger": "a plunger", "Tap": "a tap",
            "Garden hose": "a garden hose", "Watering can": "a watering can", "Wheelbarrow": "a wheelbarrow",
            "Padlock": "a padlock"}
OI_DEVICES = {"Bathroom scale": "bathroom scales", "Kitchen scale": "kitchen scales",
              "Glucose meter": "a blood-glucose meter", "Blood pressure monitor": "a blood-pressure monitor",
              "Digital clock": "a digital clock", "Timer": "a timer", "Stopwatch": "a stopwatch",
              "Automated teller machine": "a cash machine (ATM)", "Plug": "a plug",
              "Electrical connector": "an electrical connector", "Usb cable": "a USB cable",
              "Coaxial cable": "a coaxial (aerial) cable", "Power strip": "a power strip",
              "Extension cord": "an extension lead", "Clothes iron": "an iron"}
OI_PERSONAL = {"Ring": "a ring", "Jewellery": "jewellery", "Nail polish": "nail polish", "Mascara": "mascara",
               "Toothpaste": "toothpaste", "Deodorant": "deodorant", "Soap": "soap", "Wig": "a wig",
               "Fedora": "a fedora hat", "Sun hat": "a sun hat", "Cowboy hat": "a cowboy hat",
               "Beanie": "a beanie hat", "Cap": "a cap"}
OI_HAIR = {"Braid": "braids", "Dreadlocks": "dreadlocks", "Afro": "an Afro", "Ponytail": "a ponytail",
           "Long hair": "long hair", "Beard": "a beard", "Moustache": "a moustache"}
OI_KITCHEN = {"Saucepan": "a saucepan", "Stock pot": "a stock pot", "Grater": "a grater", "Peeler": "a peeler",
              "Rolling pin": "a rolling pin", "Colander": "a colander"}
OI_GROUP_QUESTIONS = ((OI_TOOLS, "What tools or hardware are in this picture?"),
                      (OI_DEVICES, "What devices are in this picture?"),
                      (OI_PERSONAL, "What personal items are in this picture?"),
                      (OI_KITCHEN, "What kitchen things are in this picture?"))
OI_HELPERS = ("Flame", "Boiling", "Gas stove", "Stove", "Man", "Woman") + OI_CHILD
OI_POTS = ("Saucepan", "Stock pot", "Cookware and bakeware")


def oi_home_rows(labels, rng):
    """Rows for one picture from its {label: 1 (confirmed) or 0 (rejected)}; [] when it has nothing for this pack."""
    yes = {n for n, c in labels.items() if c == 1}
    no = {n for n, c in labels.items() if c == 0}
    child = bool(yes & set(OI_CHILD))
    rows = []
    pests_yes = [n for n in OI_PESTS if n in yes]
    pests_no = [n for n in OI_PESTS if n in no]
    if pests_yes:
        n = rng.choice(pests_yes)
        thing = OI_PESTS[n]
        rows.append({"question": f"Is there {thing} in this picture?",
                     "answer": f"Yes, there is {thing} in this picture." if n != "Mold" else
                               "Yes, there is mould in this picture."})
    if pests_no and (pests_yes or rng.random() < 0.5):
        thing = OI_PESTS[rng.choice(pests_no)]
        rows.append({"question": f"Is there {thing} in this picture?",
                     "answer": f"No, I can't see {thing} in this picture."})
    for group, question in OI_GROUP_QUESTIONS:
        things = [group[n] for n in group if n in yes]
        if things:
            rows.append({"question": question, "answer": f"I can see {listed(things[:6])}."})
    hair = [OI_HAIR[n] for n in OI_HAIR if n in yes]
    if hair and not child and yes & {"Man", "Woman"}:
        rows.append({"question": "What hairstyles can you see in this picture?",
                     "answer": f"I can see {listed(hair)}."})
    stove = yes & {"Gas stove", "Stove"}
    if stove and "Flame" in yes:
        rows.append({"question": "Is the burner on?", "answer": "Yes: there is a flame, so the burner is lit."})
    elif "Gas stove" in yes and "Flame" in no:
        rows.append({"question": "Is the burner on?", "answer": "I can't see a flame, so the gas burner looks off."})
    if yes & set(OI_POTS) and "Boiling" in yes:
        rows.append({"question": "Is it boiling?", "answer": "Yes, it is boiling."})
    elif yes & set(OI_POTS) and "Boiling" in no:
        rows.append({"question": "Is it boiling?", "answer": "No, it doesn't look as if it is boiling."})
    return [dict(r, child=True) if child else r for r in rows]


def build_open_images_home(limit):
    """The Open Images home pack: reads the labels people checked on the validation and test sets, keeps photos with
    a pest, tool, device, personal, hairstyle or kitchen label (those open_images_objects does not ask about) whose
    own licence is free and that need no turning, and fetches them; the rarest kinds first, so bed bugs and
    glucose meters are not crowded out by hats."""
    s, rng = session(), random.Random(81)
    wanted = set(OI_PESTS) | set(OI_HAIR) | set(OI_HELPERS) | set(OI_POTS)
    for group, _ in OI_GROUP_QUESTIONS:
        wanted |= set(group)
    wanted -= set(OI_HOME) - set(OI_HELPERS)              # asked already by open_images_objects
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2 and line[1] in wanted:
            mids.setdefault(line[0], line[1])
    say(f"Open Images: {len(mids)} of {len(wanted)} home labels found in the class list")
    labels = {}
    for url in OI_LABELS:
        for cells in csv.reader(oi_lines(s, url)):
            if len(cells) == 4 and cells[2] in mids:
                try:
                    confidence = round(float(cells[3]))
                except ValueError:
                    continue
                labels.setdefault(cells[0], {})[mids[cells[2]]] = confidence
    labels = {k: v for k, v in labels.items() if any(n not in OI_HELPERS for n, c in v.items() if c == 1)
              or ("Gas stove" in v and "Flame" in v)}
    say(f"Open Images: {len(labels)} pictures with a home label checked")
    photos = {}
    for url in OI_IMAGES:
        for r in csv.DictReader(oi_lines(s, url)):
            licence = oi_licence_name(r.get("License") or "")
            if r["ImageID"] in labels and licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[r["ImageID"]] = (r["Subset"], licence, utf8(clean(r.get("Author"))) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
    counts = {}
    for v in labels.values():
        for n, c in v.items():
            if c == 1:
                counts[n] = counts.get(n, 0) + 1
    items = []
    for image_id in sorted(labels):
        if image_id not in photos:
            continue
        rows = oi_home_rows(labels[image_id], rng)
        if not rows:
            continue
        subset, licence, author, page = photos[image_id]
        credit = f"Photo by {author}{f' ({page})' if page else ''}, {licence}; labels from Open Images V7 (Google), " \
                 "CC BY 4.0"
        rarest = min((counts.get(n, 10 ** 6) for n, c in labels[image_id].items() if c == 1), default=10 ** 6)
        items.append((rarest + rng.random(), f"oi-home-{image_id}.jpg",
                      OI_PICTURE.format(subset=subset, image_id=image_id), [dict(r, credit=credit) for r in rows]))
    say(f"Open Images: {len(items)} free home photos")
    items.sort(key=lambda x: x[0])
    chosen = [x[1:] for x in items[:int(limit * 1.1) + 2]]
    random.Random(82).shuffle(chosen)
    return with_twins(fetch_all(chosen, workers=8)[:limit])


# ----------------------------------------------------------------- Wikimedia Commons: shared engine

# Free licences only (never BY-SA, NC or ND: those are the kit's commons_home_sa).
HOME_FREE = re.compile(r"^(cc0|public domain|pd|cc by \d|cc-by-\d|cc by-\d|mit|expat|apache)", re.I)
NOT_A_PHOTO = re.compile(r"\b(drawings?|illustrations?|paintings?|logos?|icons?|emoji|cartoons?|clip ?art|diagrams?|"
                         r"in art|in heraldry|coats? of arms|stamps?|maps?|advertis\w*|videos?|audio|microscop\w*|"
                         r"SEM|micrographs?|slides?|specimens? in alcohol|museum specimens?|casent\d+)\b", re.I)
COMMONS_PLACES = {}        # {file title: the country at its camera coordinates}
# An insect's or plant's life stage, which the child check must not take for a child.
LIFE_STAGE = re.compile(r"\b(juvenile\w*|nymph\w*|larva\w*|instars?|young (ticks?|insects?|roaches|cockroaches|"
                        r"bugs?|ants?|wasps?|plants?|shoots?))\b", re.I)


def home_entries(s, titles, drawings=False):
    """[(title, picture address, credit, caption or description)] for Commons files whose licence is CC0, public
    domain, CC BY, MIT or Apache, 50 files a request (pictures at 1,280 pixels, a width Wikimedia keeps ready, so
    fetching them is not refused); JPEG and PNG photos, and SVG drawings too when drawings is
    True (Commons sends a PNG of them). Where a file's page gives the camera's coordinates, the country is kept in
    COMMONS_PLACES."""
    from food_packs import commons_description
    kinds = ("image/jpeg", "image/png") + (("image/svg+xml", "image/gif") if drawings else ())
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 960 if drawings else 1280,
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
            if not HOME_FREE.match(licence) or re.search(r"\b(SA|NC|ND)\b|-SA|-NC|-ND", upper) \
                    or info.get("mime") not in kinds or not info.get("thumburl"):
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            text = commons_description(captions.get(f"M{p['pageid']}"),
                                       (meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}", text))
            if meta.get("GPSLatitude") and meta.get("GPSLongitude"):
                COMMONS_PLACES[p["title"]] = country_at(clean(meta["GPSLatitude"].get("value")),
                                                        clean(meta["GPSLongitude"].get("value")))
        time.sleep(1)
    return out


def commons_fetch(items, workers=2, raw=False):
    """Download Commons pictures (items are (name, address, row)) as fetch_all does, but patiently: when Wikimedia's
    picture server says "too many requests" (429) it waits as long as asked (or 10, 20, 40 ... seconds, at most a
    minute) and tries again, up to five times, instead of leaving the picture out. raw: the bytes as sent (a
    drawing's see-through PNG), not made into a JPEG."""
    import concurrent.futures
    s = session()

    def one(item):
        """One picture as (name, JPEG, row), or None."""
        name, url, row = item
        wait = 10
        for _ in range(5):
            time.sleep(0.5)
            try:
                r = s.get(url, timeout=60)
            except Exception:  # noqa: BLE001 - network trouble: wait and try again
                time.sleep(wait)
                continue
            if r.status_code == 200:
                data = r.content if raw else smaller(r.content)
                return (name, data, row) if data else None
            if r.status_code not in (429, 500, 502, 503, 504):
                return None
            after = r.headers.get("Retry-After", "")
            time.sleep(min(int(after) if after.isdigit() else wait, 60))
            wait = min(wait * 2, 60)
        return None

    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        return [x for x in pool.map(one, items) if x]


def file_name(prefix, title):
    """A pack picture's file name for a Commons file."""
    return f"{prefix}-" + re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80] + ".jpg"


def category_files(s, category, deeper):
    """The files of a Commons category (and of its subcategories when deeper), leaving out drawings, art and
    microscope pictures by their names. A category that does not exist gives none."""
    titles = commons_members(s, category, "file")
    if deeper:
        for sub in commons_members(s, category, "subcat"):
            if not NOT_A_PHOTO.search(sub):
                titles += commons_members(s, sub.split(":", 1)[-1], "file")
    return [t for t in dict.fromkeys(titles) if not NOT_A_PHOTO.search(t)]


def build_commons_topic(specs, limit, prefix, adults_only=False):
    """A Commons pack from specs: [(category, deeper, rows)] or [(category, deeper, rows, pattern)], rows being
    [(question, answer)] for every picture of the category (and, with a pattern, only pictures whose title or words
    match it). The categories take turns (in a fixed shuffled order) until the limit is reached, so each gets an
    even share; each picture also gets "Write a short description ..." from its own caption or description when it
    is a real, respectful one. adults_only: files whose title or words name a child are left out (else such rows are
    marked "child")."""
    s, items, seen = session(), [], set()
    order = list(specs)
    random.Random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    queues = []
    for spec in order:
        queues.append([spec[0], spec[1], spec[2], None, spec[3] if len(spec) > 3 else None])
    want = int(limit * 1.15) + 2
    rounds = 0
    while len(items) < want and queues and rounds < 50:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            category, deeper, rows, titles, must = q
            if titles is None:
                titles = [t for t in category_files(s, category, deeper) if t not in seen]
                random.Random(category).shuffle(titles)
                say(f"Commons {category}: {len(titles)} files")
            batch, q[3] = titles[:max(3, share) * 2], titles[max(3, share) * 2:]
            if not batch:
                queues.remove(q)
                continue
            got = 0
            for title, url, credit, text in home_entries(s, batch):
                if got >= share or title in seen:
                    continue
                words = f"{title} {text}"
                if NUDE.search(words) or (must and not must.search(words)):
                    continue
                if adults_only and CHILD.search(words):
                    continue
                seen.add(title)
                place = where(COMMONS_PLACES.get(title, ""))
                words = LIFE_STAGE.sub(" ", words)          # "juvenile" tick or "young" nymph: not a child
                out = [mark_child({"question": qn, "answer": an, "credit": credit, **place}, words)
                       for qn, an in rows]
                if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
                    out.append(mark_child({"question": ALT_TEXT, "answer": text, "credit": credit, **place}, words))
                items.append((file_name(prefix, title), url, out))
                got += 1
            if not q[3]:
                queues.remove(q)
    random.Random(prefix + "-order").shuffle(items)
    return with_twins(commons_fetch(items[:want])[:limit])


def ask_what(thing, extra=""):
    """[("What is this?", "This is a thermostat.")] plus a second, more specific question when extra is given."""
    rows = [("What is this?", f"This is {thing}.")]
    if extra:
        rows.append(extra)
    return rows


# ----------------------------------------------------------------- commons_pests

BED_BUG_Q = "Is there a bed bug in this picture?"
PEST_Q = "What pest is this?"


def pest(name, about, bed_bug_lookalike=False):
    """Rows for a pest category: what it is, and "Is there a bed bug ...?" (yes for bed bugs; a careful no for
    look-alikes)."""
    rows = [(PEST_Q, f"This looks like {name}. {about}")]
    if bed_bug_lookalike:
        rows.append((BED_BUG_Q, f"No: this looks like {name}, not a bed bug."))
    return rows


COMMONS_PESTS = [
    ("Cimex lectularius", True, [(BED_BUG_Q, "Yes: this looks like a bed bug (Cimex lectularius)."),
                                 (PEST_Q, "This looks like a bed bug: a small, flat, reddish-brown insect that "
                                          "hides in mattresses and bites at night.")]),
    ("Bedbug bites", False, [("What could have caused these marks?",
                              "These are bed bug bites: small, itchy red bumps, often in a line or a cluster.")]),
    ("Blattella germanica", True, pest("a German cockroach", "It is a small, light-brown cockroach with two dark "
                                       "stripes behind its head, common in kitchens.", True)),
    ("Periplaneta americana", True, pest("an American cockroach", "It is a large, reddish-brown cockroach.", True)),
    ("Blatta orientalis", True, pest("an Oriental cockroach", "It is a dark, shiny cockroach that likes damp "
                                     "places.", True)),
    ("Reticulitermes flavipes", True, pest("a termite (eastern subterranean termite)", "Termites eat wood from the "
                                           "inside.")),
    ("Wood damaged by termites", True, [("What has damaged this wood?", "Termites have damaged this wood.")]),
    ("Monomorium pharaonis", True, pest("a Pharaoh ant", "It is a tiny, yellowish ant that often comes indoors.")),
    ("Linepithema humile", True, pest("an Argentine ant", "It is a small brown ant that forms long trails "
                                      "indoors.")),
    ("Camponotus pennsylvanicus", True, pest("a carpenter ant", "It is a large black ant that nests in damp "
                                             "wood.")),
    ("Solenopsis invicta", True, pest("a red imported fire ant", "Its sting burns; keep away from its mounds.")),
    ("Vespula nests", True, [("What is this?", "This is a wasp nest. Keep away from it: wasps sting to defend it.")]),
    ("Vespa velutina nests", False, [("What is this?", "This is an Asian hornet nest. Keep away from it and report "
                                                       "it: the hornets sting to defend it.")]),
    ("Ixodes scapularis", True, pest("a deer tick (black-legged tick)", "It can carry Lyme disease; remove it "
                                     "with fine tweezers, close to the skin.", True)),
    ("Ixodes ricinus", True, pest("a castor bean tick (sheep tick)", "It can carry Lyme disease; remove it with "
                                  "fine tweezers, close to the skin.", True)),
    ("Dermacentor variabilis", True, pest("an American dog tick", "It is a brown tick with pale markings.", True)),
    ("Amblyomma americanum", True, pest("a lone star tick", "The female has a white spot on her back.", True)),
    ("Ixodes sucking blood", False, [("What is on the skin?", "A tick is attached to the skin, feeding on blood.")]),
    ("Aedes aegypti", True, pest("a yellow fever mosquito (Aedes aegypti)", "It is a small black mosquito with "
                                 "white markings on its legs.")),
    ("Aedes albopictus", True, pest("an Asian tiger mosquito", "It is a black mosquito with white stripes.")),
    ("Culex pipiens", True, pest("a common house mosquito (Culex pipiens)", "It is a plain brown mosquito.")),
    ("Tineola bisselliella", True, pest("a common clothes moth", "Its larvae eat wool and other natural fibres.")),
    ("Dermestidae", False, pest("a carpet beetle (or a related skin beetle)", "Its larvae eat wool, fur and "
                                "stored food.", True)),
    ("Ctenocephalides felis", True, pest("a cat flea", "It also bites dogs and people.", True)),
    ("Lepisma saccharinum", True, pest("a silverfish", "It is harmless but eats paper and starch.")),
    ("Cimex hemipterus", True, [(BED_BUG_Q, "Yes: this looks like a tropical bed bug (Cimex hemipterus)."),
                                (PEST_Q, "This looks like a tropical bed bug.")]),
    ("Rodent damage", True, [("What caused this damage?", "Rodents (mice or rats) have gnawed this.")]),
    ("Stachybotrys chartarum", False, [("What is this?", "This is black mould (Stachybotrys chartarum), which "
                                                         "grows on damp walls, paper and wood.")]),
    ("Water damage", True, [("What is wrong here?", "This shows water damage: stains, peeling or rot from a leak "
                                                    "or damp.")]),
    ("Wood decay", False, [("What is wrong with this wood?", "The wood is rotting (decayed by fungus).")]),
    ("Serpula lacrymans", True, [("What is this?", "This is dry rot (Serpula lacrymans), a fungus that destroys "
                                                   "timber in damp buildings.")]),
]


def build_commons_pests(limit):
    """The Commons household pests and damp pack."""
    return build_commons_topic(COMMONS_PESTS, limit, "pest")


# ----------------------------------------------------------------- commons_appliances

COMMONS_APPLIANCES = [
    ("Thermostats", True, ask_what("a thermostat")),
    ("Control knobs", False, ask_what("a control knob")),
    ("Microwave ovens", True, ask_what("a microwave oven")),
    ("Washing machines", False, ask_what("a washing machine")),
    ("Kitchen scales", True, ask_what("a kitchen scale")),
    ("Bathroom scales", True, ask_what("a set of bathroom scales")),
    ("Digital thermometers", True, ask_what("a digital thermometer")),
    ("Medical thermometers", True, ask_what("a medical thermometer")),
    ("Meat thermometers", True, ask_what("a meat thermometer")),
    ("Glucose meters", True, ask_what("a blood-glucose meter")),
    ("Electronic arm blood pressure monitor", False, ask_what("a blood-pressure monitor")),
    ("Sphygmomanometers", False, ask_what("a blood-pressure monitor")),
    ("Seven segment displays", False, ask_what("a seven-segment display")),
    ("Elevator buttons", True, [("What is this?", "These are the buttons of a lift (elevator buttons).")]),
    ("Automatic teller machines", False, ask_what("a cash machine (ATM)")),
    ("Ticket machines", False, ask_what("a ticket machine")),
    ("Check-in terminals", True, ask_what("a self-service check-in machine")),
]


def build_commons_appliances(limit):
    """The Commons appliance displays and controls pack."""
    return build_commons_topic(COMMONS_APPLIANCES, limit, "appliance")


# ----------------------------------------------------------------- commons_connectors

PLUG_Q = "What kind of plug is this, and where is it used?"


def plug(kind, pins, where_used):
    """Rows for a plug standard's category."""
    return [(PLUG_Q, f"This is {kind}, with {pins}. It is used in {where_used}.")]


COMMONS_CONNECTORS = [
    ("NEMA 1–15", True, plug("a Type A plug or socket (NEMA 1-15)", "two flat parallel pins",
                             "the USA, Canada, Mexico, Japan and much of Central America")),
    ("NEMA 5–15", True, plug("a Type B plug or socket (NEMA 5-15)", "two flat parallel pins and a round earth pin",
                             "the USA, Canada, Mexico and much of Central America")),
    ("BS 546", True, plug("a Type D plug or socket (BS 546)", "three large round pins in a triangle",
                          "India, Nepal, Sri Lanka and parts of Africa")),
    ("CEE 7/5", True, plug("a Type E plug or socket (CEE 7/5)", "two round pins and a hole for the socket's earth pin",
                           "France, Belgium, Poland, Czechia and Slovakia")),
    ("Schuko connectors", True, plug("a Type F plug or socket (Schuko, CEE 7/4)", "two round pins and earth clips "
                                     "at the sides", "Germany, Austria, the Netherlands, Sweden, Spain, Russia, "
                                     "South Korea and most of continental Europe")),
    ("BS 1363", True, plug("a Type G plug or socket (BS 1363)", "three rectangular pins",
                           "the UK, Ireland, Malta, Cyprus, Malaysia, Singapore, Hong Kong and the Gulf states")),
    ("SI 32", True, plug("a Type H plug or socket (SI 32)", "three pins in a V shape", "Israel")),
    ("AS/NZS 3112", True, plug("a Type I plug or socket (AS/NZS 3112)", "two flat pins in a V shape, often with an "
                               "earth pin", "Australia, New Zealand, China, Argentina and Pacific islands")),
    ("SN 441011", True, plug("a Type J plug or socket (SEV 1011)", "three round pins", "Switzerland and "
                             "Liechtenstein")),
    ("CEI 23-50", True, plug("a Type L plug or socket (CEI 23-50)", "three round pins in a row", "Italy and Chile")),
    ("IEC 60906-1", True, plug("a Type N plug or socket (IEC 60906-1)", "three round pins", "Brazil and South Africa")),
    ("TIS 166-2549 plugs", True, plug("a Type O plug (TIS 166-2549)", "three round pins", "Thailand")),
    ("Mains adaptors", True, [("What is this?", "This is a mains plug adaptor, for using a plug from one country "
                                                "in another country's socket.")]),
    ("USB connectors", True, [("What kind of connector is this?", "This is a USB connector.")]),
    ("USB-C", True, [("What kind of connector is this?", "This is a USB-C connector: small and oval, it goes in "
                                                         "either way up.")]),
    ("Micro-USB", True, [("What kind of connector is this?", "This is a micro-USB connector: small, with sloping "
                                                             "sides, it only goes in one way up.")]),
    ("Lightning (connector)", True, [("What kind of connector is this?", "This is an Apple Lightning connector.")]),
    ("HDMI connectors", True, [("What kind of connector is this?", "This is an HDMI connector, for video and "
                                                                   "sound to a television or screen.")]),
    ("Phone connectors (audio)", True, [("What kind of connector is this?", "This is an audio jack (a phone "
                                                                            "connector), for headphones or "
                                                                            "speakers.")]),
    ("AA batteries", True, [("What size of battery is this?", "This is an AA battery.")]),
    ("AAA batteries", True, [("What size of battery is this?", "This is an AAA battery.")]),
    ("C batteries", True, [("What size of battery is this?", "This is a C battery.")]),
    ("D batteries", True, [("What size of battery is this?", "This is a D battery.")]),
    ("PP3 batteries", True, [("What size of battery is this?", "This is a 9-volt (PP3) battery.")]),
    ("Button cells", True, [("What size of battery is this?", "This is a button cell (a coin battery).")]),
    ("Mobile phone chargers", True, ask_what("a mobile phone charger")),
    ("Battery chargers", True, ask_what("a battery charger")),
]


def build_commons_connectors(limit):
    """The Commons plugs, connectors and batteries pack."""
    return build_commons_topic(COMMONS_CONNECTORS, limit, "connector")


# ----------------------------------------------------------------- laundry_symbols

LAUNDRY_Q = "What does this laundry symbol mean?"
LAUNDRY_LABEL_Q = "What do these washing symbols mean?"
# Each symbol file (its Commons title) with its kind and meaning, from the file's own name. Files whose name does not
# say plainly what they mean (ISO 7000 and IEC 60417 numbers, "kilo" variants) are not used.
WASH, BLEACH, TUMBLE, IRON, CLEAN, DRY = "wash", "bleach", "tumble", "iron", "clean", "dry"
LAUNDRY_SYMBOLS = {
    "Waschen.svg": (WASH, "Machine washable."), "Tabler-icons wash.svg": (WASH, "Machine washable."),
    "Waschen nein.svg": (WASH, "Do not wash."), "Nicht waschen.svg": (WASH, "Do not wash."),
    "Laundry symbol do not wash.svg": (WASH, "Do not wash."), "Tabler-icons wash-off.svg": (WASH, "Do not wash."),
    "Handwäsche.svg": (WASH, "Hand wash only."), "Laundry symbol hand wash.svg": (WASH, "Hand wash only."),
    "Washsym handwash.png": (WASH, "Hand wash only."),
    "Waschen bei 60C.svg": (WASH, "Machine wash at 60 °C."),
    "Laundry symbol wash 30 delicate.svg": (WASH, "Machine wash at 30 °C, gentle cycle."),
    "Laundry symbol wash 95.svg": (WASH, "Machine wash at 95 °C."),
    "Laundry-symbol-wash-95.svg": (WASH, "Machine wash at 95 °C."),
    "Laundry symbol wash delicate.svg": (WASH, "Wash on a gentle cycle."),
    "Laundry symbol wash very delicate.svg": (WASH, "Wash on a very gentle cycle."),
    "Tabler-icons wash-gentle.svg": (WASH, "Wash on a gentle cycle."),
    "Bleichen.svg": (BLEACH, "Any bleach may be used."), "Tabler-icons bleach.svg": (BLEACH, "Any bleach may be used."),
    "Chloren ja.svg": (BLEACH, "Chlorine bleach may be used."),
    "Bleichen mit chlor.svg": (BLEACH, "Chlorine bleach may be used."),
    "Tabler-icons bleach-chlorine.svg": (BLEACH, "Chlorine bleach may be used."),
    "Sauerstoffbleichen.svg": (BLEACH, "Only non-chlorine (oxygen) bleach may be used."),
    "Tabler-icons bleach-no-chlorine.svg": (BLEACH, "Only non-chlorine (oxygen) bleach may be used."),
    "Nicht bleichen.svg": (BLEACH, "Do not bleach."), "Nicht bleichen v2.svg": (BLEACH, "Do not bleach."),
    "Tabler-icons bleach-off.svg": (BLEACH, "Do not bleach."),
    "Chloren nein.svg": (BLEACH, "Do not use chlorine bleach."),
    "Trommeltrocknen.svg": (TUMBLE, "Tumble drying is allowed."),
    "Tabler-icons wash-tumble-dry.svg": (TUMBLE, "Tumble drying is allowed."),
    "Trommeltrocknen 1.svg": (TUMBLE, "Tumble dry on low heat."),
    "Trockner wenig Temperatur.svg": (TUMBLE, "Tumble dry on low heat."),
    "Trommeltrocknen 2.svg": (TUMBLE, "Tumble dry on normal heat."),
    "Trockner hohe Temperatur.svg": (TUMBLE, "Tumble dry on normal heat."),
    "Nicht trommeltrocknen.svg": (TUMBLE, "Do not tumble dry."), "Trockner nein.svg": (TUMBLE, "Do not tumble dry."),
    "Tabler-icons wash-tumble-off.svg": (TUMBLE, "Do not tumble dry."),
    "Bügeln.svg": (IRON, "Ironing is allowed."),
    "Bügeln 1.svg": (IRON, "Iron on low (up to 110 °C)."), "Buegeln 1.svg": (IRON, "Iron on low (up to 110 °C)."),
    "Tabler-icons ironing-1.svg": (IRON, "Iron on low (up to 110 °C)."),
    "Bügeln 2.svg": (IRON, "Iron on medium (up to 150 °C)."), "Buegeln 2.svg": (IRON, "Iron on medium (up to 150 °C)."),
    "Tabler-icons ironing-2.svg": (IRON, "Iron on medium (up to 150 °C)."),
    "Laundry symbol iron warm.svg": (IRON, "Iron on medium (up to 150 °C)."),
    "Bügeln 3.svg": (IRON, "Iron on high (up to 200 °C)."), "Buegeln 3.svg": (IRON, "Iron on high (up to 200 °C)."),
    "Tabler-icons ironing-3.svg": (IRON, "Iron on high (up to 200 °C)."),
    "Nicht bügeln.svg": (IRON, "Do not iron."), "Buegeln nein.svg": (IRON, "Do not iron."),
    "Tabler-icons ironing-off.svg": (IRON, "Do not iron."),
    "Ironing without steam (ISO 7000).svg": (IRON, "Iron without steam."),
    "Tabler-icons ironing-steam-off.svg": (IRON, "Iron without steam."),
    "Tabler-icons ironing-steam.svg": (IRON, "Steam ironing is allowed."),
    "Chem A.svg": (CLEAN, "Professional dry cleaning with any solvent."),
    "Professionelle reinigung (A).svg": (CLEAN, "Professional dry cleaning with any solvent."),
    "Laundry symbol dry clean any solvent.svg": (CLEAN, "Professional dry cleaning with any solvent."),
    "Chem P.svg": (CLEAN, "Professional dry cleaning with tetrachloroethene (P)."),
    "Professionelle reinigung (P).svg": (CLEAN, "Professional dry cleaning with tetrachloroethene (P)."),
    "Tabler-icons wash-dry-p.svg": (CLEAN, "Professional dry cleaning with tetrachloroethene (P)."),
    "Professionelle reinigung (P)s.svg": (CLEAN, "Professional dry cleaning with tetrachloroethene (P), gentle "
                                                 "process."),
    "Professionelle reinigung (P)ss.svg": (CLEAN, "Professional dry cleaning with tetrachloroethene (P), very "
                                                  "gentle process."),
    "Professionelle reinigung (F).svg": (CLEAN, "Professional dry cleaning with hydrocarbon solvents (F)."),
    "Tabler-icons wash-dry-f.svg": (CLEAN, "Professional dry cleaning with hydrocarbon solvents (F)."),
    "Professionelle reinigung (F)s.svg": (CLEAN, "Professional dry cleaning with hydrocarbon solvents (F), gentle "
                                                 "process."),
    "Professionelle reinigung (F)ss.svg": (CLEAN, "Professional dry cleaning with hydrocarbon solvents (F), very "
                                                  "gentle process."),
    "Professionelle reinigung (W).svg": (CLEAN, "Professional wet cleaning."),
    "Tabler-icons wash-dry-w.svg": (CLEAN, "Professional wet cleaning."),
    "Professionelle reinigung (W)s.svg": (CLEAN, "Professional wet cleaning, gentle process."),
    "Professionelle reinigung (W)ss.svg": (CLEAN, "Professional wet cleaning, very gentle process."),
    "Professionelle reinigung.svg": (CLEAN, "Professional dry cleaning is allowed."),
    "Tabler-icons wash-dryclean.svg": (CLEAN, "Professional dry cleaning is allowed."),
    "Chem nein.svg": (CLEAN, "Do not dry clean."), "Nicht chemisch reinigen.svg": (CLEAN, "Do not dry clean."),
    "Tabler-icons wash-dryclean-off.svg": (CLEAN, "Do not dry clean."),
    "Nicht nassreinigen.svg": (CLEAN, "Do not wet clean."), "Мокрая чистка запрещена.svg": (CLEAN, "Do not wet clean."),
    "Trocknen (leine).svg": (DRY, "Hang to dry."), "Trocknen (hang).svg": (DRY, "Hang to dry."),
    "Tabler-icons wash-dry-hang.svg": (DRY, "Hang to dry."),
    "Сушка в вертикальном положении.svg": (DRY, "Hang to dry."),
    "Trocknen (leine im schatten).svg": (DRY, "Hang to dry in the shade."),
    "Trocknen (hang in shade).svg": (DRY, "Hang to dry in the shade."),
    "Сушка в вертикальном положении в тени.svg": (DRY, "Hang to dry in the shade."),
    "Trocknen (liegend).svg": (DRY, "Dry flat."), "Сушка в горизонтальном положении.svg": (DRY, "Dry flat."),
    "Trocknen (liegend im schatten).svg": (DRY, "Dry flat in the shade."),
    "Сушка в горизонтальном положении в тени.svg": (DRY, "Dry flat in the shade."),
    "Trocknen (tropfnass).svg": (DRY, "Drip dry: hang up wet, without wringing."),
    "Tabler-icons wash-dry-dip.svg": (DRY, "Drip dry: hang up wet, without wringing."),
    "Сушка без отжима в вертикальном положении.svg": (DRY, "Drip dry: hang up wet, without wringing."),
    "Trocknen (tropfnass im schatten).svg": (DRY, "Drip dry in the shade."),
    "Сушка без отжима в вертикальном положении в тени.svg": (DRY, "Drip dry in the shade."),
    "Сушка без отжима в горизонтальном положении.svg": (DRY, "Dry flat, without wringing."),
    "Сушка без отжима в горизонтальном положении в тени.svg": (DRY, "Dry flat in the shade, without wringing."),
    "Trocknen (schatten).svg": (DRY, "Dry in the shade."),
    "Tabler-icons wash-dry-shade.svg": (DRY, "Dry in the shade."),
}
for _t in (30, 40, 50, 60, 70, 95):
    LAUNDRY_SYMBOLS[f"Waschen {_t}.svg"] = (WASH, f"Machine wash at {_t} °C.")
    LAUNDRY_SYMBOLS[f"Waschen {_t}s.svg"] = (WASH, f"Machine wash at {_t} °C, gentle cycle.")
    LAUNDRY_SYMBOLS[f"Waschen {_t}ss.svg"] = (WASH, f"Machine wash at {_t} °C, very gentle cycle.")
for _n, _t in enumerate((30, 40, 50, 60, 70, 95), 1):          # Tabler's dots: one dot 30 °C ... six dots 95 °C
    LAUNDRY_SYMBOLS[f"Tabler-icons wash-temperature-{_n}.svg"] = (WASH, f"Machine wash at {_t} °C.")
LABEL_ORDER = (WASH, BLEACH, TUMBLE, DRY, IRON, CLEAN)


def symbol_picture(data, side=256):
    """A symbol drawing (PNG, often see-through) as a black-on-white square picture, side pixels wide."""
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("RGBA")
    img.thumbnail((side - 24, side - 24))
    out = Image.new("RGB", (side, side), "white")
    out.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    return out


def care_label(pictures):
    """A computer-made care label: the symbol pictures in a row on a pale label, as JPEG bytes."""
    from PIL import Image
    side, gap = 200, 24
    label = Image.new("RGB", (len(pictures) * (side + gap) + gap, side + 2 * gap), (250, 248, 240))
    for i, picture in enumerate(pictures):
        label.paste(picture.resize((side, side)), (gap + i * (side + gap), gap))
    out = io.BytesIO()
    label.save(out, "JPEG", quality=92)
    return out.getvalue()


def build_laundry_symbols(limit):
    """The laundry symbols pack: each free symbol file with its meaning, computer-made care labels of four or five of
    them (one of each kind, in the usual order: washing, bleaching, tumble drying, natural drying, ironing,
    professional cleaning), and Commons photos of real care labels with their own descriptions."""
    s = session()
    titles = []
    for category in ("Laundry symbols", "Tabler laundry icons", "Dutch laundry symbols", "Japanese laundry symbols"):
        titles += commons_members(s, category, "file")
    titles = [t for t in dict.fromkeys(titles) if t.split(":", 1)[-1] in LAUNDRY_SYMBOLS]
    entries = home_entries(s, titles, drawings=True)
    say(f"Laundry symbols: {len(entries)} free symbol files with a known meaning (of {len(titles)})")
    symbols = []                        # (kind, meaning, credit, picture)
    for title, url, credit, _ in entries:
        got = commons_fetch([("symbol", url, None)], workers=1, raw=True)
        if not got:
            continue
        try:
            picture = symbol_picture(got[0][1])
        except Exception:  # noqa: BLE001 - a drawing that cannot be read is left out
            continue
        kind, meaning = LAUNDRY_SYMBOLS[title.split(":", 1)[-1]]
        symbols.append((kind, meaning, credit, picture, title))
        time.sleep(0.3)
    out, rng = [], random.Random(91)
    for kind, meaning, credit, picture, title in symbols:
        buffer = io.BytesIO()
        picture.save(buffer, "JPEG", quality=92)
        out.append((file_name("laundry", title), buffer.getvalue(),
                    {"question": LAUNDRY_Q, "answer": meaning, "credit": credit}))
    singles = len(out)
    by_kind = {k: [x for x in symbols if x[0] == k and not x[1].startswith(("Machine washable", "Ironing is",
                                                                            "Tumble drying is", "Professional dry "
                                                                            "cleaning is"))]
               for k in LABEL_ORDER}
    labels_wanted = max(0, limit - singles) if limit > singles else max(1, limit // 3)
    for n in range(labels_wanted):
        kinds = [k for k in LABEL_ORDER if by_kind[k]]
        if len(kinds) < 4:
            break
        chosen = [k for k in kinds if k not in (DRY,) or rng.random() < 0.4]
        chosen = chosen[:5] if len(chosen) >= 4 else kinds[:4]
        picks = [rng.choice(by_kind[k]) for k in chosen]
        if picks[0][1] == "Do not wash.":
            picks = [p for p in picks if p[0] not in (BLEACH, TUMBLE)] or picks
        answer = " ".join(p[1] for p in picks)
        credit = "A care label made from these symbol files: " + "; ".join(dict.fromkeys(p[2] for p in picks))
        out.append((f"laundry-label-{n:05d}.jpg", care_label([p[3] for p in picks]),
                    {"question": LAUNDRY_LABEL_Q, "answer": answer, "credit": credit}))
    # Photos of real care labels, with their own descriptions.
    photos = []
    for title, url, credit, text in home_entries(s, [t for t in commons_members(s, "Laundry tags", "file")]):
        rows = [{"question": "What is this?", "answer": "This is a clothing care label.", "credit": credit,
                 **where(COMMONS_PLACES.get(title, ""))}]
        if text:
            rows.append({"question": ALT_TEXT, "answer": text, "credit": credit,
                         **where(COMMONS_PLACES.get(title, ""))})
        photos.append((file_name("laundry-tag", title), url, rows))
    out += with_twins(commons_fetch(photos))
    rng.shuffle(out)
    pictures = [e for e in out if e[1] is not None][:limit]
    keep = {e[0] for e in pictures}
    return pictures + [e for e in out if e[1] is None and e[2]["file"].split("/", 1)[-1] in keep]


# ----------------------------------------------------------------- commons_tools

TOOL_Q = "What tool is in this picture?"


def tool(name, extra=None):
    """Rows for a tool category (said so that it fits a close-up of the tool and a photo of someone using it)."""
    rows = [(TOOL_Q, f"I can see {name}.")]
    if extra:
        rows.append(extra)
    return rows


COMMONS_TOOLS = [
    ("Claw hammers", True, tool("a claw hammer")), ("Sledgehammers", False, tool("a sledgehammer")),
    ("Screwdrivers", True, tool("a screwdriver")), ("Pliers", True, tool("a pair of pliers")),
    ("Needle-nose pliers", True, tool("a pair of needle-nose pliers")),
    ("Adjustable wrenches", True, tool("an adjustable spanner (wrench)")),
    ("Combination wrenches", True, tool("a combination spanner (wrench)")),
    ("Pipe wrenches", True, tool("a pipe wrench")), ("Hex keys", True, tool("a hex key (Allen key)")),
    ("Hand saws", True, tool("a hand saw")), ("Hacksaws", True, tool("a hacksaw")),
    ("Cordless drills", True, tool("a cordless drill")),
    ("Angle grinders", True, tool("an angle grinder")), ("Circular saws", True, tool("a circular saw")),
    ("Tape measures", True, tool("a tape measure")),
    ("Spirit levels", True, tool("a spirit level")), ("Utility knives", True, tool("a utility knife")),
    ("Chisels", True, tool("a chisel")), ("Soldering irons", True, tool("a soldering iron")),
    ("Wood screws", True, [("What is this?", "These are wood screws.")]),
    ("Machine screws", True, [("What is this?", "These are machine screws.")]),
    ("Nails (fasteners)", True, [("What is this?", "These are nails.")]),
    ("Bolts", True, [("What is this?", "These are bolts.")]),
    ("Screws", True, [("What is this?", "These are screws.")]),
    ("Nuts (hardware)", True, [("What is this?", "These are nuts (for bolts).")]),
    ("Washers (hardware)", True, [("What is this?", "These are washers.")]),
    ("Wall plugs", True, [("What is this?", "These are wall plugs (anchors), for screws in walls.")]),
    ("Plungers", True, tool("a plunger, for clearing a blocked sink or toilet")),
    ("Water taps", True, [("What is this?", "This is a tap (faucet).")]),
    ("Spades", True, tool("a garden spade")), ("Shovels", True, tool("a shovel")),
    ("Garden forks", True, tool("a garden fork")), ("Rakes", True, tool("a rake")), ("Hoes", True, tool("a hoe")),
    ("Secateurs", True, tool("a pair of secateurs (pruning shears)")),
    ("Garden trowels", True, tool("a garden trowel")), ("Wheelbarrows", True, tool("a wheelbarrow")),
    ("Watering cans", True, tool("a watering can")), ("Garden hoses", True, tool("a garden hose")),
    ("Lawn mowers", True, tool("a lawn mower")),
]


def build_commons_tools(limit):
    """The Commons tools and hardware pack."""
    return build_commons_topic(COMMONS_TOOLS, limit, "tool")


# ----------------------------------------------------------------- commons_personal

COMMONS_PERSONAL = [
    ("Shampoo", True, ask_what("shampoo", ("Is this shampoo or conditioner?", "It is shampoo."))),
    ("Hair conditioners", True, ask_what("hair conditioner", ("Is this shampoo or conditioner?",
                                                              "It is conditioner."))),
    ("Toothpaste", True, ask_what("toothpaste")), ("Deodorants", True, ask_what("deodorant")),
    ("Shower gels", True, ask_what("shower gel")), ("Soap bars", False, ask_what("a bar of soap")),
    ("Liquid soap", True, ask_what("liquid soap")), ("Sunscreen", True, ask_what("sunscreen")),
    ("Lipsticks", True, ask_what("a lipstick")), ("Mascara", True, ask_what("mascara")),
    ("Nail polish", True, ask_what("nail polish")), ("Face powder", True, ask_what("face powder")),
    ("Hairbrushes", True, ask_what("a hairbrush")), ("Razors", True, ask_what("a razor")),
    ("Rings (jewellery)", True, ask_what("a ring")), ("Earrings", True, ask_what("a pair of earrings")),
    ("Necklaces", True, ask_what("a necklace")), ("Bracelets", True, ask_what("a bracelet")),
    ("Brooches", True, ask_what("a brooch")),
    ("Wristwatches", False, ask_what("a wristwatch")), ("Digital watches", True, ask_what("a digital watch")),
    ("Spectacles", False, ask_what("a pair of glasses")), ("Sunglasses", True, ask_what("a pair of sunglasses")),
    ("Baseball caps", True, ask_what("a baseball cap")), ("Knit caps", True, ask_what("a knitted hat (beanie)")),
    ("Handbags", True, ask_what("a handbag")),
    ("Backpacks", True, ask_what("a backpack")), ("Wallets", True, ask_what("a wallet")),
]


def build_commons_personal(limit):
    """The Commons personal care and accessories pack."""
    return build_commons_topic(COMMONS_PERSONAL, limit, "personal")


# ----------------------------------------------------------------- commons_hairstyles

HAIR_Q = "What hairstyle does this person have?"


def hair(answer):
    """Rows for a hairstyle category."""
    return [(HAIR_Q, answer)]


COMMONS_HAIRSTYLES = [
    ("Braids", False, hair("Their hair is in braids.")),
    ("Cornrows", True, hair("Their hair is in cornrows (braids close to the scalp).")),
    ("Dreadlocks", True, hair("Their hair is in dreadlocks (locs).")),
    ("Ponytails", True, hair("Their hair is tied back in a ponytail.")),
    ("Crew cuts", True, hair("They have a crew cut: hair cut very short.")),
    ("Shaved heads", True, hair("Their head is shaved.")),
    ("Bald men", False, hair("He is bald.")),
    ("Gray hair", True, hair("They have grey hair.")),
    ("Long hair", False, hair("They have long hair.")),
]


def build_commons_hairstyles(limit):
    """The Commons hairstyles pack (adults only)."""
    return build_commons_topic(COMMONS_HAIRSTYLES, limit, "hair", adults_only=True)


# ----------------------------------------------------------------- commons_kitchen

BURNER_Q = "Is the burner on?"
BURNER_WORDS = re.compile(r"\b(stoves?|burners?|hobs?|cookers?|cooktops?|kitchens?|cooking|pans?|pots?)\b", re.I)
COMMONS_KITCHEN = [
    ("Gas flames", False, [(BURNER_Q, "Yes: there is a flame, so the burner is lit.")], BURNER_WORDS),
    ("Gas burners", False, [("What is this?", "This is a gas burner on a cooker.")]),
    ("Gas stoves", True, ask_what("a gas cooker")), ("Cookers", False, ask_what("a cooker")),
    ("Induction cookers", True, ask_what("an induction hob")),
    ("Boiling water", True, [("Is it boiling?", "Yes, the water is boiling.")]),
    ("Table settings", True, [("What is on the table?", "The table is set for a meal, with plates, cutlery and "
                                                        "glasses.")]),
    ("Kitchenware", False, ask_what("kitchenware")),
    ("Whisks", True, ask_what("a whisk")), ("Ladles", True, ask_what("a ladle")),
    ("Spatulas", True, ask_what("a spatula")), ("Graters", True, ask_what("a grater")),
    ("Peelers", True, ask_what("a vegetable peeler")), ("Colanders", True, ask_what("a colander")),
    ("Can openers", True, ask_what("a tin opener")), ("Garlic presses", True, ask_what("a garlic press")),
    ("Rolling pins", True, ask_what("a rolling pin")), ("Saucepans", True, ask_what("a saucepan")),
    ("Frying pans", True, ask_what("a frying pan")), ("Pressure cookers", True, ask_what("a pressure cooker")),
    ("Electric kettles", True, ask_what("an electric kettle")), ("Toasters", True, ask_what("a toaster")),
    ("Rice cookers", True, ask_what("a rice cooker")),
]


def build_commons_kitchen(limit):
    """The Commons kitchen pack."""
    return build_commons_topic(COMMONS_KITCHEN, limit, "kitchen")


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what} categories: captions CC0; pictures CC0, public domain (including US "
                  "government photos from the CDC, USDA and EPA) or CC BY, each with its author and file page below. "
                  "https://commons.wikimedia.org")
HOME_PACKS = {
    "clock_times": (build_clock_times,
                    "Times read by hand in 'It's About Time: Analog Clock Reading in the Wild' (Charig Yang, Weidi "
                    "Xie and Andrew Zisserman, CVPR 2022), MIT licence, Copyright (c) 2024 Charig Yang, "
                    "https://github.com/charigyang/itsabouttime. Photos from Open Images V7 (CC BY 2.0, checked "
                    "photo by photo, photographer named) and COCO (CC BY 2.0 or no known copyright restrictions)."),
    "seven_segment": (build_seven_segment,
                      "7SEG_OCR by MiXaiLL76, MIT licence, https://huggingface.co/datasets/MiXaiLL76/7SEG_OCR "
                      "(computer-made pictures of seven-segment displays, with the number each shows)."),
    "open_images_home": (build_open_images_home,
                         "Open Images V7 (Google): image-level labels verified by people, CC BY 4.0, "
                         "https://storage.googleapis.com/openimages/web/index.html. Each photo is CC BY 2.0 (checked "
                         "photo by photo), credited below with its photographer and Flickr page."),
    "commons_pests": (build_commons_pests, COMMONS_CREDIT.format(what="household pest, mould and damp")),
    "commons_appliances": (build_commons_appliances, COMMONS_CREDIT.format(what="appliance display and control")),
    "commons_connectors": (build_commons_connectors, COMMONS_CREDIT.format(what="plug, connector and battery")),
    "laundry_symbols": (build_laundry_symbols,
                        "Wikimedia Commons laundry symbol files (Category:Laundry symbols, its Tabler icons by "
                        "Paweł Kuna under the MIT licence, and Category:Laundry tags): CC0, public domain, CC BY or "
                        "MIT, each credited below; the care labels are made here from those files. The symbols are "
                        "a GINETEX trademark. https://commons.wikimedia.org/wiki/Category:Laundry_symbols"),
    "commons_tools": (build_commons_tools, COMMONS_CREDIT.format(what="tool, hardware and garden tool")),
    "commons_personal": (build_commons_personal, COMMONS_CREDIT.format(what="toiletry, cosmetic and accessory")),
    "commons_hairstyles": (build_commons_hairstyles, COMMONS_CREDIT.format(what="hairstyle")),
    "commons_kitchen": (build_commons_kitchen, COMMONS_CREDIT.format(what="kitchen")),
}

# How many pictures a full build takes from each collection (about what each offers after the licence and label
# checks; the Commons ones are estimates from the categories' sizes, the free share being about half).
HOME_LIMITS = {
    "clock_times": 1300,          # one-clock photos: at most 1,127 Open Images (those in its boxable training list)
                                  # and the 254 of 1,378 COCO ones that are CC BY 2.0 or no known copyright
    "seven_segment": 3333,        # all of them
    "open_images_home": 3900,     # 3,949 free photos with a home label checked by hand (validation and test sets)
    "commons_pests": 900,
    "commons_appliances": 700,
    "commons_connectors": 900,
    "laundry_symbols": 600,       # about 120 symbols with a known meaning, made into care labels, and the tag photos
    "commons_tools": 1200,
    "commons_personal": 1000,
    "commons_hairstyles": 600,
    "commons_kitchen": 900,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one home pack builder.")
    parser.add_argument("key", choices=sorted(HOME_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = HOME_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
