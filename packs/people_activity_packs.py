"""Pack builders for PEOPLE IN DAILY ACTIVITIES: what a person in a photo is doing (eating, reading, washing dishes,
riding a bicycle, carrying water, selling vegetables, praying, waiting for a bus), so a blind person hears it plainly:
"The person is riding a horse.", "Someone is washing clothes.", "The man on the left of the picture is holding an
umbrella." Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"} with "file" (a picture in the
pack) or "url" (a COCO photo the kit fetches itself, as coco_questions does), plus "place" where the source states one
and "child": true where the words of a picture (its labels, its captions, a Commons file's title or description) name
a child. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins). The limit counts pictures (rows for the rows-only packs).

Every answer is a fixed sentence written here from the source's own labels: the verb and the objects people marked
on a COCO photo (V-COCO), the relationships people drew between boxes (Visual Genome), the labels people checked on
an Open Images photo, a Commons category's name, or a Dollar Street topic. Nothing is written by an AI model, nobody
is named, and nothing is guessed about who a person is: "man", "woman", "boy" and "girl" are said only where the
source's own label says so; otherwise "the person", "someone" or "people". Positions are said only from a source's
own boxes, as places in the picture (left, right, top, bottom, centre).

Safety (packs/SOURCE-RULES.md): no sexual content (files whose words name nudity are left out; Open Images bathing,
kissing and swimwear labels and the Commons bathing categories are not used); children only in everyday clothed
scenes, and every row whose words name a child is marked "child". None of these packs is used for picture-making
(they are in the kit's NOT_FOR_PICTURE_MAKING and PEOPLE_AND_BODILY_PACK_KEYS).

The packs (licences checked at the source in November 2026):
  vcoco_actions          V-COCO, Verbs in COCO (Saurabh Gupta and Jitendra Malik, UC Berkeley, 2015; github.com/
                         s-gupta/v-coco, MIT licence): 26 actions people marked on every person in 10,346 COCO photos,
                         with the object of each action (holding a kite, riding a horse, eating a sandwich with a fork,
                         talking on the phone, reading a book, cutting a cake, working on a laptop, skiing ...). The
                         person and object boxes are COCO's (CC BY 4.0). Rows only: the kit fetches each photo from
                         COCO, and only photos whose own COCO licence is CC BY 2.0 or "no known copyright" are used.
                         "What is the person doing?" -> "The person is riding a horse." / "What are the people doing?"
                         -> "The person on the left of the picture is holding a tennis racket. ..."
  vg_people_actions      Visual Genome 1.2 relationships (Krishna et al., 2017; visualgenome.org, CC BY 4.0) on its
                         51,000 COCO photos, again only those whose COCO licence is CC BY 2.0 or no known copyright,
                         and not the photos vcoco_actions already has: what a man, woman, boy, girl, player, skier or
                         person is doing to or with something (holding, riding, carrying, eating, reading, pushing,
                         feeding, throwing, flying a kite, crossing the street, waiting for a bus ...). Rows only.
                         "What is the person doing?" -> "The woman is holding an umbrella."
  open_images_activities Open Images V7 (Google; labels CC BY 4.0, each photo CC BY 2.0, checked photo by photo, its
                         photographer credited): everyday activities and work that people checked by hand on a photo
                         (cooking, eating, reading, writing, shopping, gardening, laundry, sewing, knitting, fishing,
                         harvest, herding, weaving, pottery, praying, queueing, a market, a street vendor, a barber, a
                         cashier ...); the postures, expressions and sports that oi_expressions and
                         open_images_culture already ask about are not repeated. "What is happening in this picture?"
                         -> "Someone is knitting." / "People in this picture are shopping at a market."
  commons_daily_life     Wikimedia Commons categories of people doing everyday things (eating, drinking tea or coffee,
                         reading, writing, sleeping, praying, waiting, queueing, shopping, cleaning, laundry, sewing,
                         knitting, spinning, pounding grain, carrying water, milking, feeding animals, fishing,
                         walking a dog, playing chess, singing, talking, voting, taking a selfie ...) and at work
                         (street and market vendors, shoe-shiners, porters, barbers, hairdressers, cashiers, waiters,
                         farm workers, postal workers, refuse collectors, taxi and bus drivers); for regional
                         diversity, the "People at work in", "Women at work in" and "Street vendors in" categories of
                         about 70 countries (that country as the place; the work categories only with a file's own
                         real English caption or description: "Describe this picture."). Pictures CC0, public domain
                         or CC BY (author credited; never BY-SA, NC or ND: those are the kit's share-alike entry).
  dollar_street_routines Dollar Street (Gapminder, CC BY 4.0, photographers credited): how families in about 60
                         countries do their daily routines, photographed in their own homes: washing hands, washing
                         and drying clothes, cleaning floors, shaving, getting and drinking water, and guests at
                         dinner. Most of these photos show the things and the place used, not a person, so the answer
                         says what routine the photo is about: "It shows how this family washes their hands."
                         (the family's country as the place; income is never put in an answer).
  coco_actions_nc        The same V-COCO and Visual Genome rows on the COCO photos whose own licence is non-commercial
                         (CC BY-NC, BY-NC-SA, BY-NC-ND) or no-derivatives (CC BY-ND): rows only, so no such photo is
                         copied; the kit fetches the photos from COCO only with the personal-use (non-commercial)
                         choice. Not an open pack: the kit lists it in its non-commercial group.
  coco_actions_sa        The same rows on COCO photos under CC BY-SA 2.0: rows only, for the kit's share-alike choice.

Non-open collections on the same subject (Commons BY-SA files, Stanford 40 Actions, SWiG/imSitu, the HAR 15
actions set) are kit download entries in training-kit/kit/people_activity_sources.py, with the sign-up and
left-out collections listed there.

    python packs/people_activity_packs.py vcoco_actions --limit 8      (prints a few rows: a quick check)
"""

import collections
import csv
import json
import math
import os
import re
import sys
import tempfile
import time
import zipfile

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, fetch_all, say, considered, listing_out_of_time, ALT_TEXT, NARRATE, COCO_LICENCES
from build_packs import pass_random  # shuffles differently on a top-up pass (see build_packs)
from food_packs import listed, with_twins, count_pictures, oi_lines, OI_CLASSES, OI_LABELS, OI_IMAGES, OI_PICTURE
from expression_packs import mark_child, child_count, OI_CHILD
from home_packs import commons_fetch, file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from mechanical_packs import spot, mech_entries, category_files, in_english, PLACES, JUST_A_RECORD, NOT_A_CHILD
from things_packs import with_article
from places import where, country_named

DOING_Q = "What is the person doing?"
PEOPLE_Q = "What are the people doing?"
HAPPENING_Q = "What is happening in this picture?"
ROUTINE_Q = "What daily routine does this picture show?"

# Where a builder may keep a large download while it reads it (a fresh temporary folder unless PEOPLE_PACK_WORK
# names one: a quick local check can then reuse what it fetched before).
WORK = os.environ.get("PEOPLE_PACK_WORK") or ""


def work_file(url, name=None):
    """Download url once into the work folder (PEOPLE_PACK_WORK, or a temporary folder) and give its path; a file
    already there is used as it is."""
    global WORK
    if not WORK:
        WORK = tempfile.mkdtemp(prefix="people-pack-")
    path = os.path.join(WORK, name or url.rsplit("/", 1)[-1].split("?")[0])
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    s = session()
    for attempt in range(3):
        try:
            with s.get(url, timeout=600, stream=True) as r:
                r.raise_for_status()
                with open(path + ".part", "wb") as f:
                    for block in r.iter_content(1 << 20):
                        f.write(block)
            os.replace(path + ".part", path)
            return path
        except Exception as e:  # noqa: BLE001 - tried again, then given up
            say(f"  Download of {url} failed ({e}); trying again")
            time.sleep(20 * (attempt + 1))
    raise RuntimeError(f"could not download {url}")


def capital(text):
    """The text with its first letter in capitals."""
    return text[:1].upper() + text[1:]


def where_in_picture(x, y, w, h, width, height):
    """Where a box (left, top, width, height in pixels) is in a picture of width x height, in plain words ("on the
    left of the picture"), from the box's centre."""
    if not width or not height:
        return ""
    return spot(min(max((x + w / 2) / width, 0), 1), min(max((y + h / 2) / height, 0), 1))


def overlap(a, b):
    """How much two boxes (x, y, w, h) overlap: the shared area over the area of both together (0 to 1)."""
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    shared = max(0, x2 - x1) * max(0, y2 - y1)
    whole = a[2] * a[3] + b[2] * b[3] - shared
    return shared / whole if whole > 0 else 0


def people_sentences(people):
    """The answer for one picture from [(who, box area, position, [phrases])], the largest people first: one person
    -> ("What is the person doing?", "The man is riding a horse."); a group word ("people") -> ("What are the people
    doing?", "The people are ..."); several -> ("What are the people doing?", "The man on the left of the picture is
    ... The woman on the right of the picture is ..."). Two people with the same word in the same place are said
    once, and when everyone said is doing the same, it is said once ("The people are standing on the beach."; not
    counted, as the same person is sometimes drawn twice). None when nothing is left."""
    people = [p for p in people if p[3]]
    if not people:
        return None
    people.sort(key=lambda p: -p[1])
    if len(people) == 1:
        who, _, _, phrases = people[0]
        plural = who in PLURAL_PEOPLE
        verb = "are" if plural else "is"
        return (PEOPLE_Q if plural else DOING_Q), f"The {who} {verb} {listed(phrases)}."
    shown = people[:4]
    if len({p[0] for p in shown}) == 1 and len({tuple(p[3]) for p in shown}) == 1 and shown[0][0] not in PLURAL_PEOPLE:
        many = MANY.get(shown[0][0], shown[0][0] + "s")
        return PEOPLE_Q, f"The {many} are {listed(shown[0][3])}."
    said, seen = [], set()
    for who, _, position, phrases in shown:
        if (who, position) in seen:
            continue
        seen.add((who, position))
        verb = "are" if who in PLURAL_PEOPLE else "is"
        said.append(f"The {who} {position} {verb} {listed(phrases)}." if position else
                    f"The {who} {verb} {listed(phrases)}.")
    if len(said) == 1:
        said = [said[0]]
    return PEOPLE_Q, " ".join(said)


PLURAL_PEOPLE = {"people", "men", "women", "children", "kids", "players", "boys", "girls"}
MANY = {"man": "men", "woman": "women", "person": "people", "child": "children"}


# ----------------------------------------------------------------- COCO photos and their own licences

COCO_FREE = (4, 7)                      # CC BY 2.0, no known copyright restrictions: the open packs
COCO_NONCOMMERCIAL = (1, 2, 3, 6)       # BY-NC-SA, BY-NC, BY-NC-ND, BY-ND: the kit's non-commercial group
COCO_SHARE_ALIKE = (5,)                 # BY-SA: the kit's share-alike group


def coco_photos(licences, note=True):
    """{COCO image id: (photo address, licence name, captions)} for the COCO 2017 photos whose own licence is one of
    licences (COCO's numbers), from the phiyodr/coco2017 copy on Hugging Face, which lists each photo's licence and
    its five captions (the captions are read only to see whether they name a child). With note, the other photos
    are noted as considered and dropped for their licence."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download
    out = {}
    for name in HfApi().list_repo_files("phiyodr/coco2017", repo_type="dataset"):
        if not name.endswith(".parquet"):
            continue
        table = pq.read_table(hf_hub_download("phiyodr/coco2017", name, repo_type="dataset"),
                              columns=["license", "image_id", "coco_url", "captions"]).to_pylist()
        for r in table:
            if r["license"] in licences:
                out[r["image_id"]] = (r["coco_url"], COCO_LICENCES.get(r["license"], str(r["license"])),
                                      " ".join(r.get("captions") or []))
            elif note:
                considered(f"coco-{r['image_id']}", r["coco_url"],
                           f"its COCO licence is {COCO_LICENCES.get(r['license'], r['license'])}, not one this pack "
                           "takes")
    return out


COCO_2014_ANNOTATIONS = "http://images.cocodataset.org/annotations/annotations_trainval2014.zip"     # 253 MB


def coco_boxes(wanted_ids):
    """COCO 2014's object boxes (CC BY 4.0) for the wanted annotation ids: ({annotation id: (image id, category
    name, (x, y, w, h))}, {image id: (width, height)}), read from COCO's annotation zip (train and val 2014)."""
    path = work_file(COCO_2014_ANNOTATIONS)
    boxes, sizes = {}, {}
    with zipfile.ZipFile(path) as z:
        for member in ("annotations/instances_train2014.json", "annotations/instances_val2014.json"):
            with z.open(member) as f:
                data = json.load(f)
            names = {c["id"]: c["name"] for c in data["categories"]}
            images = {i["id"]: (i["width"], i["height"]) for i in data["images"]}
            for a in data["annotations"]:
                if a["id"] in wanted_ids:
                    boxes[a["id"]] = (a["image_id"], names.get(a["category_id"], ""), tuple(a["bbox"]))
                    sizes[a["image_id"]] = images.get(a["image_id"], (0, 0))
            del data
    return boxes, sizes


# ----------------------------------------------------------------- vcoco_actions (V-COCO)

VCOCO = "https://raw.githubusercontent.com/s-gupta/v-coco/master/data/vcoco/vcoco_{}.json"
VCOCO_PARTS = ("trainval", "test")
VCOCO_CREDIT = ("V-COCO, Verbs in COCO (Saurabh Gupta and Jitendra Malik, UC Berkeley, 2015), MIT licence, "
                "https://github.com/s-gupta/v-coco; boxes from COCO (Lin et al., 2014), CC BY 4.0; photo from COCO "
                "(cocodataset.org), {licence}")
# COCO's object names as said in an answer.
COCO_NAMES = {"sports ball": "ball", "dining table": "table", "cell phone": "mobile phone", "tv": "television",
              "couch": "sofa", "potted plant": "pot plant", "hair drier": "hair dryer", "person": "another person",
              "scissors": "a pair of scissors", "skis": "skis", "laptop": "laptop computer", "remote":
              "remote control", "mouse": "computer mouse", "keyboard": "keyboard", "motorcycle": "motorbike",
              "baseball glove": "baseball glove", "wine glass": "wine glass"}
COCO_UNCOUNTED = {"pizza", "cake", "broccoli", "skis", "another person", "a pair of scissors"}
# The order in which a person's actions are said (most telling first); the last ones are said only when little else
# is known about the person.
VCOCO_ORDER = ["talk_on_phone", "read", "eat", "drink", "cut", "work_on_computer", "ride", "ski", "surf",
               "skateboard", "snowboard", "hit", "kick", "throw", "catch", "carry", "hold", "jump", "lay", "point",
               "sit", "run", "walk", "look", "stand", "smile"]
VCOCO_WEAK = {"look", "stand", "smile", "walk", "sit"}


def coco_thing(category):
    """A COCO object as said after a verb: "a horse", "an umbrella", "skis", "pizza", "another person"."""
    name = COCO_NAMES.get(category, category)
    if name in COCO_UNCOUNTED:
        return name
    return with_article(name)


def vcoco_phrase(action, roles):
    """The words for one action of a person, from its roles ({"obj": category, "instr": category}, either may be
    missing): "riding a horse", "eating a sandwich with a fork", "talking on the phone"; "" when the action needs an
    object that was not marked."""
    obj, instr = roles.get("obj"), roles.get("instr")
    o, i = (coco_thing(obj) if obj else ""), (coco_thing(instr) if instr else "")
    simple = {"run": "running", "walk": "walking", "stand": "standing", "smile": "smiling", "ski": "skiing",
              "surf": "surfing", "skateboard": "skateboarding", "snowboard": "snowboarding",
              "talk_on_phone": "talking on the phone"}
    if action in simple:
        return simple[action]
    if action == "hold":
        return f"holding {o}" if o else ""
    if action == "sit":
        return f"sitting on {i}" if i else "sitting"
    if action == "ride":
        return f"riding {i}" if i else ""
    if action == "look":
        return f"looking at {o}" if o else ""
    if action == "hit":
        return f"hitting {o} with {i}" if o and i else f"hitting {o}" if o else f"swinging {i}" if i else ""
    if action == "eat":
        return f"eating {o} with {i}" if o and i else f"eating {o}" if o else "eating"
    if action == "jump":
        return f"jumping on {i}" if i else "jumping"
    if action == "lay":
        return f"lying on {i}" if i else "lying down"
    if action in ("carry", "throw", "catch", "kick", "read"):
        verb = {"carry": "carrying", "throw": "throwing", "catch": "catching", "kick": "kicking", "read": "reading"}
        return f"{verb[action]} {o}" if o else ("reading" if action == "read" else "")
    if action == "cut":
        return f"cutting {o} with {i}" if o and i else f"cutting {o}" if o else f"cutting something with {i}" \
            if i else ""
    if action == "work_on_computer":
        return f"working on {i}" if i else "working on a computer"
    if action == "drink":
        return f"drinking from {i}" if i else "drinking"
    if action == "point":
        return f"pointing at {i}" if i else "pointing"
    return ""


def vcoco_person_phrases(actions):
    """A person's phrases from {action: roles}: the most telling actions first, at most three; "walking", "sitting"
    and "smiling" only when fewer than two others are known, "standing" and "looking at" only when nothing more
    telling is; "sitting on" left out when the person rides something, and "holding" left out when the held thing is
    the tool of another action."""
    names = sorted(actions, key=VCOCO_ORDER.index)
    tools = {r.get("instr") for a, r in actions.items() if a != "hold"} | \
            {r.get("obj") for a, r in actions.items() if a not in ("hold", "look")}
    strong = [a for a in names if a not in VCOCO_WEAK]
    out = []
    for a in names:
        if a in VCOCO_WEAK and len(strong) >= 2 and a != "smile":
            continue
        if a in ("look", "stand") and strong:          # said only when nothing more telling is known
            continue
        if a == "sit" and "ride" in actions:
            continue
        if a == "hold" and actions[a].get("obj") in tools:
            continue
        roles = actions[a]
        if a == "jump" and {"skateboard", "ski", "snowboard", "surf"} & set(actions):
            roles = {}                                  # "skateboarding and jumping", not "... jumping on a skateboard"
        phrase = vcoco_phrase(a, roles)
        if phrase and phrase not in out:
            out.append(phrase)
    return out[:3]


def vcoco_people():
    """Every person V-COCO marked doing something: {image id: {person annotation id: {action: {role: annotation
    id}}}}, from the trainval and test files (MIT)."""
    s = session()
    people = {}
    for part in VCOCO_PARTS:
        for entry in s.get(VCOCO.format(part), timeout=300).json():
            action, roles = entry["action_name"], entry["role_name"]
            n = len(entry["image_id"])
            for k in range(n):
                if not entry["label"][k]:
                    continue
                marked = {}
                for r, role in enumerate(roles[1:], 1):
                    object_id = entry["role_object_id"][r * n + k]
                    if object_id:
                        marked[role] = int(object_id)
                image, person = int(entry["image_id"][k]), int(entry["ann_id"][k])
                people.setdefault(image, {}).setdefault(person, {})[action] = marked
    return people


def vcoco_items(photos, credit_format=VCOCO_CREDIT):
    """[(image id, row)] for the V-COCO photos among photos ({image id: (address, licence, captions)}): one row per
    photo saying what its people are doing, with their place in the picture when there are several."""
    people = {i: p for i, p in vcoco_people().items() if i in photos}
    say(f"V-COCO: {len(people)} photos with a person doing something, under the licences wanted")
    wanted = {a for persons in people.values() for person, acts in persons.items()
              for a in [person] + [x for roles in acts.values() for x in roles.values()]}
    boxes, sizes = coco_boxes(wanted)
    out = []
    for image_id, persons in people.items():
        width, height = sizes.get(image_id, (0, 0))
        said = []
        for person, acts in persons.items():
            if person not in boxes:
                continue
            named = {a: {role: boxes[x][1] for role, x in roles.items() if x in boxes} for a, roles in acts.items()}
            phrases = vcoco_person_phrases(named)
            box = boxes[person][2]
            said.append(("person", box[2] * box[3], where_in_picture(*box, width, height), phrases))
        if len([p for p in said if p[3]]) > 1:
            said = [("person", area, pos, ph) for _, area, pos, ph in said]
        answer = people_sentences(said)
        if not answer:
            continue
        url, licence, captions = photos[image_id]
        row = mark_child({"url": url, "question": answer[0], "answer": answer[1],
                          "credit": credit_format.format(licence=licence)}, captions)
        out.append((image_id, row))
    return out


def build_vcoco_actions(limit):
    """The vcoco_actions pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]."""
    items = vcoco_items(coco_photos(COCO_FREE))
    pass_random(141).shuffle(items)
    say(f"V-COCO: {len(items)} rows")
    return [(None, None, row) for _, row in items[:limit]]


# ----------------------------------------------------------------- vg_people_actions (Visual Genome)

VG = "https://homes.cs.washington.edu/~ranjay/visualgenome/data/dataset/"
VG_CREDIT = ("Visual Genome 1.2 relationships (Krishna et al., 2017), CC BY 4.0, https://visualgenome.org; photo "
             "from COCO (cocodataset.org), {licence}")
VCOCO_IDS = "https://raw.githubusercontent.com/s-gupta/v-coco/master/data/splits/vcoco_all.ids"
# Visual Genome's names for people, as said in an answer (a name not here is not a person).
VG_PEOPLE = {"man": "man", "woman": "woman", "person": "person", "boy": "boy", "girl": "girl", "lady": "woman",
             "guy": "man", "child": "child", "kid": "child", "player": "player", "skier": "skier", "surfer": "surfer",
             "skateboarder": "skateboarder", "snowboarder": "snowboarder", "tennis player": "tennis player",
             "baseball player": "baseball player", "batter": "batter", "catcher": "catcher", "pitcher": "pitcher",
             "biker": "cyclist", "cyclist": "cyclist", "rider": "rider", "chef": "cook", "cook": "cook",
             "worker": "worker", "vendor": "vendor", "people": "people", "men": "men", "women": "women",
             "children": "children", "kids": "children", "players": "players", "boys": "boys", "girls": "girls"}
# Visual Genome's predicates that say what someone is doing, as said in an answer (first form of each kept).
VG_VERBS = {
    "holding": "holding", "holds": "holding", "hold": "holding", "holding up": "holding up",
    "holding onto": "holding onto", "riding": "riding", "rides": "riding", "riding on": "riding",
    "carrying": "carrying", "carries": "carrying", "carry": "carrying", "playing": "playing",
    "plays": "playing", "playing with": "playing with", "watching": "watching", "watches": "watching",
    "watch": "watching", "looking at": "looking at", "looks at": "looking at", "using": "using", "uses": "using",
    "eating": "eating", "eats": "eating", "drinking": "drinking", "flying": "flying", "crossing": "crossing",
    "swinging": "swinging", "talking on": "talking on", "throwing": "throwing", "hitting": "hitting",
    "hits": "hitting", "catching": "catching", "kicking": "kicking", "cutting": "cutting", "pushing": "pushing",
    "pulling": "pulling", "driving": "driving", "reading": "reading", "feeding": "feeding", "petting": "stroking",
    "brushing": "brushing", "casting": "casting", "serving": "serving", "selling": "selling", "fixing": "fixing",
    "helping": "helping", "hugging": "hugging", "leading": "leading", "washing": "washing", "cooking": "cooking",
    "cleaning": "cleaning", "typing on": "typing on", "painting": "painting", "writing on": "writing on",
    "writing": "writing", "making": "making", "preparing": "preparing", "sweeping": "sweeping",
    "skiing on": "skiing on", "skiing down": "skiing down", "skiing in": "skiing in",
    "surfing in": "surfing in", "surfing on": "surfing on", "surfing": "surfing on",
    "skateboarding on": "skateboarding on", "swimming in": "swimming in", "walking on": "walking on",
    "walking in": "walking in", "walking down": "walking down", "walking across": "walking across",
    "walking along": "walking along", "walking with": "walking with", "walking": "walking",
    "sitting on": "sitting on", "sits on": "sitting on", "seated on": "sitting on", "sitting in": "sitting in",
    "sitting at": "sitting at", "sitting on top of": "sitting on", "standing on": "standing on",
    "standing in": "standing in", "standing at": "standing at", "laying on": "lying on", "lying on": "lying on",
    "laying in": "lying in", "kneeling on": "kneeling on", "leaning on": "leaning on",
    "waiting for": "waiting for", "waiting on": "waiting for", "working on": "working on",
    "talking to": "talking to", "reaching for": "reaching for", "grabbing": "grabbing", "boarding": "getting on",
    "getting on": "getting on", "jumping on": "jumping on", "doing trick on": "doing a trick on",
    "balancing on": "balancing on", "taking": "taking", "shopping": "shopping",
}
# Verbs said only when little else is known about the person.
VG_WEAK = {"sitting on", "sitting in", "sitting at", "standing on", "standing in", "standing at", "walking on",
           "walking in", "walking down", "walking across", "walking along", "walking", "looking at", "watching",
           "holding", "leaning on", "kneeling on", "lying in", "lying on"}
# Things said with "the" (places and the like), and things said without "a" (food and other masses).
VG_THE = {"street", "road", "sidewalk", "beach", "grass", "field", "snow", "water", "ocean", "sea", "court", "slope",
          "hill", "sand", "track", "platform", "floor", "ground", "lake", "river", "waves", "wave", "sky", "sun",
          "shore", "park", "crosswalk", "dirt", "mountain", "ramp", "phone", "camera", "tennis court", "pavement",
          "kitchen", "room", "train", "bus", "plane"}
VG_BARE = {"pizza", "food", "cake", "ice cream", "wine", "beer", "coffee", "tea", "water", "soup", "rice", "meat",
           "bread", "salad", "frisbee", "tennis", "baseball", "soccer", "football", "golf", "video game", "wii",
           "game", "games", "cards", "chess", "music", "guitar", "piano", "drums", "milk", "juice", "lunch",
           "dinner", "breakfast", "cereal", "pasta", "spaghetti", "dough", "paper", "hay", "grass", "skis"}
VG_PLAY_THE = {"guitar", "piano", "drums", "violin", "flute", "trumpet", "saxophone", "drum"}


def vg_thing(verb, name):
    """A Visual Genome object as said after its verb: "a horse", "the street", "pizza", "frisbee" (after playing),
    "the guitar" (after playing an instrument), "bananas" (a plural); "" when it cannot be said."""
    name = " ".join(name.lower().split())
    if not name or not re.match(r"^[a-z][a-z' -]*$", name):
        return ""
    if verb == "playing" and name in VG_PLAY_THE:
        return f"the {name}"
    if verb in ("playing", "eating", "drinking") and name in VG_BARE:
        return name
    if name in VG_THE:
        return f"the {name}"
    if name in VG_BARE:
        return name
    if name.endswith("s") and not name.endswith(("ss", "us", "is")):
        return name
    return with_article(name)


def vg_name(thing):
    """The first name of a Visual Genome box ("man"), in lower case."""
    return " ".join(str(thing.get("name") or (thing.get("names") or [""])[0]).lower().split())


def vg_rows_for(relationships, width, height):
    """(question, answer, words) for one Visual Genome photo from its relationships: the people (boxes named man,
    woman, person ... at least 1 % of the photo) with the things they are doing, the same person drawn twice taken
    as one; or None. words: every name used, to see whether the photo shows a child."""
    people = []          # [[who, box, {phrase}]]
    words = []
    for r in relationships:
        who = VG_PEOPLE.get(vg_name(r.get("subject") or {}))
        verb = VG_VERBS.get(" ".join(str(r.get("predicate") or "").lower().split()).removesuffix(" a")
                            .removesuffix(" an").removesuffix(" the"))
        if not who or not verb:
            continue
        subject, obj = r["subject"], r.get("object") or {}
        box = (subject.get("x", 0), subject.get("y", 0), subject.get("w", 0), subject.get("h", 0))
        if width and height and box[2] * box[3] < 0.01 * width * height:
            continue
        thing_name = vg_name(obj)
        if VG_PEOPLE.get(thing_name):
            thing = VG_PEOPLE[thing_name]
            thing = thing if thing in PLURAL_PEOPLE else with_article(thing)
        else:
            thing = vg_thing(verb, thing_name)
        if verb == "talking on" and "phone" in thing_name:
            phrase = "talking on the phone"
        elif verb == "flying" and "kite" in thing_name:
            phrase = "flying a kite"
        elif verb == "walking" or not thing:
            if verb not in ("walking", "shopping", "cooking", "writing", "reading", "eating", "drinking"):
                continue
            phrase = verb
        else:
            if verb == "playing" and not thing.startswith("the ") and thing_name not in VG_BARE:
                verb = "playing with"
            phrase = f"{verb} {thing}"
        words += [vg_name(subject), thing_name]
        for p in people:
            if p[0] == who and overlap(p[1], box) > 0.5:
                p[2].append(phrase)
                break
        else:
            people.append([who, box, [phrase]])
    said = []
    for who, box, phrases in people:
        phrases = list(dict.fromkeys(phrases))
        strong = [p for p in phrases if p.split(" ")[0] not in {w.split(" ")[0] for w in VG_WEAK}
                  or p.startswith(("holding up", "holding onto"))]
        weak = [p for p in phrases if p not in strong]
        chosen = (strong[:2] + weak[:1]) if len(strong) < 2 else strong[:3]
        # one phrase per verb and per thing (people draw "holding a racket" and "holding a tennis racket" on the
        # same hand, and "holding up a kite" and "carrying a kite" on the same kite)
        kept, verbs, things = [], set(), set()
        for p in chosen:
            verb_word, thing_words = p.split(" ")[0], " ".join(p.split(" ")[-1:])
            if verb_word in verbs or thing_words in things:
                continue
            verbs.add(verb_word)
            things.add(thing_words)
            kept.append(p)
        said.append((who, box[2] * box[3], where_in_picture(*box, width, height), kept))
    answer = people_sentences(said)
    return (answer[0], answer[1], " ".join(words)) if answer else None


def vg_items(photos, credit_format=VG_CREDIT):
    """[(image id, row)] for the Visual Genome photos that are COCO photos among photos ({COCO id: (address,
    licence, captions)}), leaving out the photos V-COCO has."""
    s = session()
    vcoco_ids = {int(x) for x in s.get(VCOCO_IDS, timeout=120).text.split() if x.strip().isdigit()}
    with zipfile.ZipFile(work_file(VG + "image_data.json.zip")) as z:
        images = {i["image_id"]: i for i in json.load(z.open(z.namelist()[0]))
                  if i.get("coco_id") in photos and i["coco_id"] not in vcoco_ids}
    say(f"Visual Genome: {len(images)} of its COCO photos under the licences wanted (V-COCO's left out)")
    out = []
    with zipfile.ZipFile(work_file(VG + "relationships.json.zip")) as z:
        data = json.load(z.open(z.namelist()[0]))           # 744 MB of JSON: about 4 GB of memory while read
    for entry in data:
        image = images.get(entry.get("image_id"))
        if not image:
            continue
        got = vg_rows_for(entry.get("relationships") or [], image.get("width"), image.get("height"))
        if not got:
            continue
        url, licence, captions = photos[image["coco_id"]]
        row = mark_child({"url": url, "question": got[0], "answer": got[1],
                          "credit": credit_format.format(licence=licence)}, got[2], captions)
        out.append((image["coco_id"], row))
    del data
    return out


def build_vg_people_actions(limit):
    """The vg_people_actions pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]."""
    items = vg_items(coco_photos(COCO_FREE))
    pass_random(142).shuffle(items)
    say(f"Visual Genome: {len(items)} rows")
    return [(None, None, row) for _, row in items[:limit]]


def build_coco_actions(limit, licences):
    """The V-COCO and Visual Genome rows on COCO photos under other licences (rows only, so no photo is copied): half
    from each source where both have enough."""
    photos = coco_photos(licences, note=False)
    first, second = vcoco_items(photos), vg_items(photos)
    pass_random(143).shuffle(first)
    pass_random(144).shuffle(second)
    take = max(limit // 2, limit - len(second))
    rows = [r for _, r in first[:take]] + [r for _, r in second[:limit - min(take, len(first))]]
    pass_random(145).shuffle(rows)
    say(f"COCO rows under {', '.join(COCO_LICENCES[n] for n in licences)}: {len(first)} V-COCO, {len(second)} Visual "
        f"Genome; {len(rows)} kept")
    return [(None, None, r) for r in rows[:limit]]


def build_coco_actions_nc(limit):
    """The non-commercial (and no-derivatives) COCO photos' rows: for the kit's personal-use choice only."""
    return build_coco_actions(limit, COCO_NONCOMMERCIAL)


def build_coco_actions_sa(limit):
    """The share-alike COCO photos' rows: for the kit's share-alike choice only."""
    return build_coco_actions(limit, COCO_SHARE_ALIKE)


# ----------------------------------------------------------------- open_images_activities (Open Images V7)

# Each label people checked, with the words after "Someone is" / "People in this picture are". The postures,
# expressions and gestures (oi_expressions), sports and music (open_images_culture), cooking tools and using things
# (open_images_in_use) are left to those packs. Bathing, kissing, swimming, bodybuilding, weight training and
# massage (often bare skin) are not used.
OI_ACTIVITIES = {
    # at home
    "Cooking": "cooking", "Baking": "baking", "Eating": "eating", "Drinking": "drinking", "Breakfast":
    "having breakfast", "Lunch": "having lunch", "Dinner": "having dinner", "Picnic": "having a picnic",
    "Barbecue": "having a barbecue", "Laundry": "doing the laundry", "Washing": "washing something",
    "Housekeeping": "doing housework", "Sewing": "sewing", "Knitting": "knitting", "Reading": "reading",
    "Writing": "writing", "Typing": "typing", "Homework": "doing homework", "Drawing": "drawing",
    "Shaving": "shaving", "Smoking": "smoking", "Gardening": "gardening", "Nap": None, "Selfie": None,
    # out and about
    "Shopping": "shopping", "Queue": "queueing", "Driving": "driving", "Hiking": "hiking", "Camping": "camping",
    "Backpacking": "backpacking", "Jogging": "jogging", "Fishing": "fishing", "Angling": "fishing with a rod",
    "Recreational fishing": "fishing", "Photography": "taking photographs", "Worship": "worshipping",
    "Meditation": "meditating", "Exercise": "exercising", "Physical fitness": "exercising",
    "Singing": "singing", "Meeting": "in a meeting",
    "Lecture": "at a lecture", "Classroom": "in a classroom", "Learning": "learning", "Party": "at a party",
    "Wedding": "at a wedding", "Funeral": "at a funeral", "Parade": "in a parade", "Protest": "protesting",
    "Demonstration": "at a demonstration", "Manicure": "having a manicure",
    # work
    "Harvest": "harvesting a crop", "Herding": "herding animals", "Farmworker": "working on a farm",
    "Weaving": "weaving", "Pottery": "making pottery", "Construction worker": "working on a building site",
    "Tradesman": "doing a trade", "Blue-collar worker": "doing manual work", "White-collar worker":
    "doing office work", "Street food": "selling or buying street food", "Vendor": "selling things",
    "Hawker": "selling things in the street", "Peddler": "selling things in the street",
    "Marketplace": "at a market", "Bazaar": "at a bazaar (market)", "Cashier": "working at a till",
    "Chef": "cooking as a chef", "Baker": "baking bread as a baker", "Butcher": "cutting meat as a butcher",
    "Barber": "cutting hair as a barber", "Hairdresser": "doing someone's hair", "Tailor": "working as a tailor",
    "Fisherman": "fishing for a living", "Shepherd": "looking after sheep", "Porter": "carrying loads as a porter",
    "Nurse": "nursing (caring for someone)",
}
OI_ACTIVITIES = {k: v for k, v in OI_ACTIVITIES.items() if v}
# A label left out when a more specific one says it ("cooking as a chef", not "cooking and cooking as a chef").
OI_ACT_COVERED = {"Cooking": {"Chef", "Baking"}, "Fishing": {"Angling", "Recreational fishing", "Fisherman"},
                  "Angling": {"Recreational fishing"}, "Eating": {"Breakfast", "Lunch", "Dinner", "Picnic"},
                  "Exercise": {"Physical fitness", "Weight training", "Jogging"}, "Physical fitness":
                  {"Weight training"}, "Vendor": {"Hawker", "Peddler", "Street food"}, "Hawker": {"Peddler"},
                  "Marketplace": {"Bazaar"}, "Washing": {"Laundry"}, "Shopping": {"Marketplace", "Bazaar"},
                  "Learning": {"Classroom", "Lecture", "Homework"}, "Baking": {"Baker"},
                  "Hairdresser": {"Barber"}, "Herding": {"Shepherd"}, "Farmworker": {"Harvest", "Herding", "Shepherd"},
                  "Blue-collar worker": {"Construction worker", "Tradesman", "Farmworker", "Butcher", "Porter"},
                  "Tradesman": {"Construction worker"}, "Protest": {"Demonstration"}}
# Labels too common to choose a picture by on their own.
OI_ACT_COMMON = {"Eating", "Drinking", "Learning", "Exercise", "Washing"}
OI_ACT_PEOPLE = {"Person", "Man", "Woman", "Girl", "Boy", "Child", "Human face", "People", "Crowd", "Team",
                 "Family", "Audience"}
OI_ACT_GROUP = {"People", "Crowd", "Team", "Family", "Audience"}
# Not a photo of real people doing it, or something these packs must not show.
OI_ACT_NOT = {"Cartoon", "Illustration", "Drawing", "Animation", "Painting", "Sculpture", "Statue", "Doll", "Toy",
              "Art", "Fictional character", "Mannequin", "Comics", "Clip art", "Bathing", "Kiss", "Swimwear",
              "Bikini", "Underpants", "Undergarment", "Brassiere", "Lingerie", "Swimming", "Bodybuilding",
              "Nudity", "Barechested", "Massage", "Weight training", "Sunbathing"}
OI_ACT_WANTED = set(OI_ACTIVITIES) | OI_ACT_PEOPLE | OI_ACT_NOT | set(OI_CHILD)
OI_ACT_CREDIT = "Photo by {author}{page}, {licence}; labels from Open Images V7 (Google), CC BY 4.0"


def oi_activity_rows(present):
    """The row of one photo from its labels seen ({label}): "Someone is knitting." or "People in this picture are
    shopping and eating."; [] when it shows no activity of this pack, no person, or something left out."""
    if present & OI_ACT_NOT or not present & OI_ACT_PEOPLE:
        return []
    names = [n for n in OI_ACTIVITIES if n in present and not (OI_ACT_COVERED.get(n, set()) & present)]
    if not names or all(n in OI_ACT_COMMON for n in names):
        return []
    words = list(dict.fromkeys(OI_ACTIVITIES[n] for n in names))[:3]
    group = bool(present & OI_ACT_GROUP)
    answer = f"People in this picture are {listed(words)}." if group else f"Someone is {listed(words)}."
    if "Drawing" in names and "Drawing" in present & OI_ACT_NOT:
        return []
    return [{"question": HAPPENING_Q, "answer": answer}]


def oi_read_wanted(s, url, names, keep, max_bytes=None):
    """Read a human-verified labels file as it downloads into keep: {picture: {label: 1, 0 or None (people
    disagreed)}}, only for the labels in names ({MID: label}), and only pictures with an activity label seen. The
    file is sorted by picture, so one picture's labels are gathered and then kept or dropped. max_bytes stops early
    (for a quick test)."""
    current, labels, read = None, {}, 0

    def flush():
        """Keep the picture just read when it has an activity label seen."""
        if current and any(c == 1 and n in OI_ACTIVITIES for n, c in labels.items()):
            keep[current] = labels

    with s.get(url, timeout=600, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            read += len(line) + 1
            if max_bytes and read > max_bytes:
                break
            cells = line.split(",")
            if len(cells) != 4 or cells[2] not in names:
                continue
            if cells[0] != current:
                flush()
                current, labels = cells[0], {}
            try:
                confidence = round(float(cells[3]))
            except ValueError:
                continue
            name = names[cells[2]]
            labels[name] = confidence if labels.get(name, confidence) == confidence else None
    flush()
    return keep


def oi_activity_items(labels, photos, counts):
    """[(name, address, rows, main label)] for the photos with a row; counts gathers {label: photos}."""
    items = []
    for image_id in sorted(labels):
        if image_id not in photos:
            continue
        present = {n for n, c in labels[image_id].items() if c == 1}
        rows = oi_activity_rows(present)
        if not rows:
            continue
        subset, licence, author, page = photos[image_id]
        credit = OI_ACT_CREDIT.format(author=author, page=f" ({page})" if page else "", licence=licence)
        child = bool(present & set(OI_CHILD))
        rows = [dict(r, credit=credit, **({"child": True} if child else {})) for r in rows]
        mains = [n for n in OI_ACTIVITIES if n in present and n not in OI_ACT_COMMON] or \
                [n for n in OI_ACTIVITIES if n in present]
        for n in mains:
            counts[n] = counts.get(n, 0) + 1
        items.append((f"oi-act-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id), rows, mains))
    return items


def build_open_images_activities(limit, train=None, train_bytes=None):
    """The Open Images activities pack's pictures. Reads the labels people checked on the validation and test sets
    (read as they download); when they give fewer pictures than limit, also the training set (train=True forces it,
    False never; train_bytes reads only the first bytes of each training file, for a test). Keeps photos of real
    people whose own licence is free and that need no turning, takes the activities in turn (rarest first, so every
    activity gets in) and fetches the photos."""
    from expression_packs import oi_read_photos, OI_TRAIN_LABELS, OI_TRAIN_IMAGES
    s, rng = session(), pass_random(146)
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    names = {mids[n]: n for n in OI_ACT_WANTED if n in mids}
    say(f"Open Images: {len(names)} of {len(OI_ACT_WANTED)} labels found in the class list (missing: "
        f"{', '.join(sorted(n for n in OI_ACT_WANTED if n not in mids)) or 'none'})")
    labels = {}
    for url in OI_LABELS:
        oi_read_wanted(s, url, names, labels)
    photos = {}
    for url in OI_IMAGES:
        oi_read_photos(s, url, set(labels), photos)
    counts = {}
    items = oi_activity_items(labels, photos, counts)
    say(f"Open Images validation and test: {len(items)} usable photos")
    if (train or (train is None and len(items) < limit * 1.1)) and not listing_out_of_time():
        more = {}
        oi_read_wanted(s, OI_TRAIN_LABELS, names, more, train_bytes)
        say(f"Open Images training set: {len(more)} pictures with an activity label seen")
        if not listing_out_of_time():
            items += oi_activity_items(more, oi_read_photos(s, OI_TRAIN_IMAGES, set(more), {}, train_bytes), counts)
        say(f"Open Images with the training set: {len(items)} usable photos")
    say("Open Images activities: " + ", ".join(f"{n} {c}" for n, c in sorted(counts.items(), key=lambda x: x[1])))
    by_label = {}
    for name, url, rows, mains in items:
        by_label.setdefault(min(mains, key=lambda n: counts.get(n, 0)), []).append((name, url, rows))
    for group in by_label.values():
        rng.shuffle(group)
    order = sorted(by_label, key=lambda n: len(by_label[n]))
    chosen, want = [], int(limit * 1.1) + 2
    while len(chosen) < want and any(by_label.values()):
        for n in order:
            if by_label[n] and len(chosen) < want:
                chosen.append(by_label[n].pop())
    fetched = fetch_all(chosen, workers=8)
    rng.shuffle(fetched)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- commons_daily_life (Wikimedia Commons)

def doing(answer, question=DOING_Q):
    """The rows of a category of people doing one thing: [(question, answer)]."""
    return [(question, answer)]


# (category, look in its subcategories too, rows, country or ""). Categories already in commons_in_use (laptops,
# computers, typing, cooking, kitchens, ironing, sweeping, gardeners), commons_expressions (hugging, handshakes,
# waving) and commons_religious_life are not repeated. Bathing, swimming and beach categories are not used.
COMMONS_DAILY_LIFE = [
    # at home and everyday life
    ("People eating", True, doing("They are eating.")),
    ("People drinking", True, doing("They are drinking.")),
    ("People drinking tea", False, doing("They are drinking tea.")),
    ("People drinking coffee", False, doing("They are drinking coffee.")),
    ("Sleeping people", True, doing("They are sleeping.")),
    ("People resting", False, doing("They are resting.")),
    ("People reading", True, doing("They are reading.")),
    ("People writing", True, doing("They are writing.")),
    ("People cleaning", True, doing("They are cleaning.")),
    ("Laundry", False, doing("They are doing the laundry (washing or drying clothes).", HAPPENING_Q)),
    ("Sewing", False, doing("Someone is sewing.", HAPPENING_Q)),
    ("Knitting", False, doing("Someone is knitting.", HAPPENING_Q)),
    ("Hand weaving", True, doing("Someone is weaving by hand.", HAPPENING_Q)),
    ("Spinning (textiles)", False, doing("Someone is spinning thread or yarn.", HAPPENING_Q)),
    ("Pounding grain", True, doing("They are pounding grain.")),
    ("Hand washing", False, doing("Someone is washing their hands.", HAPPENING_Q)),
    ("Hair washing", False, doing("Someone's hair is being washed.", HAPPENING_Q)),
    ("Shaving", False, doing("Someone is shaving.", HAPPENING_Q)),
    ("Parenting", False, doing("A parent is looking after a child.", HAPPENING_Q)),
    ("Babysitting", True, doing("Someone is looking after a child.", HAPPENING_Q)),
    ("Caregivers", True, doing("Someone is caring for another person.", HAPPENING_Q)),
    ("Watching television", True, doing("They are watching television.")),
    ("People taking selfies", True, doing("They are taking a selfie (a photo of themselves) with a phone.")),
    ("People in conversation", False, doing("They are talking with each other.", PEOPLE_Q)),
    ("People sitting on benches", True, doing("They are sitting on a bench.")),
    ("People waiting", True, doing("They are waiting.")),
    ("Queues", False, doing("People are standing in a queue (a line), waiting their turn.", PEOPLE_Q)),
    ("Shopping", False, doing("Someone is shopping.", HAPPENING_Q)),
    ("People shopping", True, doing("They are shopping.")),
    ("People on trains", False, doing("They are travelling on a train.")),
    ("Commuters", True, doing("They are on their way to or from work.")),
    ("Dog walking", True, doing("Someone is walking a dog.", HAPPENING_Q)),
    ("Jogging", True, doing("They are jogging.")),
    ("People cycling", True, doing("They are riding bicycles.")),
    ("Driving", False, doing("Someone is driving.", HAPPENING_Q)),
    ("Water carriers", True, doing("They are carrying water.")),
    ("People at wells", True, doing("They are at a well, getting water.")),
    ("Milking", False, doing("Someone is milking an animal.", HAPPENING_Q)),
    ("People feeding animals", True, doing("They are feeding animals.")),
    ("People fishing", True, doing("They are fishing.")),
    ("Picnics", False, doing("People are having a picnic.", HAPPENING_Q)),
    ("People playing chess", False, doing("They are playing chess.")),
    ("People playing board games", False, doing("They are playing a board game.")),
    ("People singing", True, doing("They are singing.")),
    ("People praying", True, doing("They are praying.")),
    ("People voting", True, doing("They are voting.")),
    ("People donating blood", False, doing("They are giving blood.")),
    ("People exercising", True, doing("They are exercising.")),
    # at work
    ("Street vendors", False, doing("They are selling things in the street.")),
    ("Market vendors", True, doing("They are selling things at a market.")),
    ("Shoeshiners", True, doing("They are shining shoes.")),
    ("Porters", False, doing("They are carrying loads as a porter.")),
    ("Barbers at work", False, doing("A barber is cutting someone's hair.", HAPPENING_Q)),
    ("Hairdressers at work", False, doing("A hairdresser is doing someone's hair.", HAPPENING_Q)),
    ("Shoemakers at work", False, doing("They are making or mending shoes.")),
    ("Weavers at work", True, doing("They are weaving.")),
    ("Cashiers", True, doing("They are working at a till (a checkout).")),
    ("Waiters", True, doing("They are waiting at tables, serving food or drink.")),
    ("Chefs at work", False, doing("They are cooking in a professional kitchen.")),
    ("Bakers at work", True, doing("They are baking.")),
    ("Farmers at work", False, doing("They are working on a farm.")),
    ("Agricultural workers", True, doing("They are working on a farm.")),
    ("Postal workers", True, doing("They are delivering or sorting post.")),
    ("Waste collectors", True, doing("They are collecting rubbish.")),
    ("Taxi drivers", False, doing("They are driving a taxi.")),
    ("Bus drivers", False, doing("They are driving a bus.")),
    ("Office workers", True, doing("They are working in an office.")),
    ("Teaching", False, doing("Someone is teaching.", HAPPENING_Q)),
]
# Country categories, for regional diversity (Commons has no "Daily life in <country>" categories; these were
# checked in November 2026, each with at least 15 files): "People at work in", "Women at work in" and "Street vendors
# in" a country. The country is the place. The work categories say nothing about the work itself, so only their files
# with a real English caption or description are used ("Describe this picture."); street vendors are also asked
# "What is the person doing?".
PEOPLE_AT_WORK_IN = [
    "Bangladesh", "Brazil", "Cameroon", "China", "Egypt", "Ethiopia", "Ghana", "India", "Indonesia", "Japan",
    "Kenya", "Laos", "Madagascar", "Mexico", "Morocco", "Mozambique", "Niger", "Nigeria", "Peru", "Russia", "Rwanda",
    "Senegal", "South Africa", "Sudan", "Tanzania", "Thailand", "Uganda", "Angola", "Botswana", "Ecuador", "France",
    "Germany", "Italy", "Namibia", "South Sudan", "Spain", "Taiwan", "Ukraine", "Vietnam", "Zimbabwe",
    "the United Kingdom", "the United States",
]
WOMEN_AT_WORK_IN = [
    "Afghanistan", "Bangladesh", "Benin", "Bolivia", "Brazil", "Burkina Faso", "Cambodia", "Cameroon", "China",
    "Egypt", "Ethiopia", "Ghana", "Guatemala", "India", "Indonesia", "Iran", "Japan", "Burundi", "Ecuador", "Guinea",
    "Ivory Coast", "Kenya", "Laos", "Madagascar", "Mali", "Mexico", "Morocco", "Mozambique", "Myanmar", "Nepal",
    "Nigeria", "Peru", "Russia", "Rwanda", "Senegal", "South Africa", "Sri Lanka", "Taiwan", "Tajikistan",
    "Tanzania", "Thailand", "Togo", "Turkey", "Uganda", "Ukraine", "Uzbekistan", "Vietnam", "Zambia", "Botswana",
    "France", "Germany", "Italy", "Namibia", "Poland", "Spain", "the United Kingdom", "the United States",
]
STREET_VENDORS_IN = [
    "Bangladesh", "Benin", "Bolivia", "Brazil", "Burkina Faso", "Cambodia", "Cameroon", "China", "Colombia", "Egypt",
    "Ethiopia", "Ghana", "Guatemala", "India", "Indonesia", "Iran", "Japan", "Kenya", "Madagascar", "Mali", "Mexico",
    "Morocco", "Mozambique", "Myanmar", "Nepal", "Nigeria", "Pakistan", "Peru", "Russia", "Burundi", "Cuba",
    "Ecuador", "France", "Germany", "Italy", "Ivory Coast", "Namibia", "Poland", "South Africa", "South Korea",
    "Spain", "Taiwan", "Tanzania", "Thailand", "Togo", "Turkey", "Uganda", "Ukraine", "Vietnam", "Zimbabwe",
    "the United States",
]
# Words in a file's title or description that leave it out: nudity and bathing, and graphic scenes.
DAILY_NOT = re.compile(r"\b(bath(e|es|ing)|swim\w*|bikini\w*|shower\w*|beach\w*|corpses?|dead|wounded|injured|"
                       r"blood\w*|executions?|war|refugees? camp)\b", re.I)
# Descriptions that say nothing about the picture (a photo contest's stock line: "This is an image with the theme
# "Rites and Rituals" from:.").
NOT_A_DESCRIPTION = re.compile(r"^this is an? (image|photo|picture)\b.*\btheme\b|\bfrom:\s*\.?$|^(image|photo) "
                               r"(of|from) (wiki loves|the contest)", re.I)
DAILY_NOT_A_PHOTO = re.compile(r"\b(drawings?|illustrations?|paintings?|engravings?|prints?|posters?|"
                               r"lithographs?|maps?|logos?|icons?|cartoons?|caricatures?|stamps?|sculptures?|"
                               r"statues?|figurines?|postcards?|videos?|audio)\b", re.I)


def commons_daily_specs():
    """Every Commons category of this pack as (category, deeper, rows, country): the activity categories, and the
    country categories (the work ones with no rows of their own: only the file's own description is used)."""
    specs = [(c, d, r, "") for c, d, r in COMMONS_DAILY_LIFE]
    specs += [(f"People at work in {c}", False, [], c.removeprefix("the ")) for c in PEOPLE_AT_WORK_IN]
    specs += [(f"Women at work in {c}", False, [], c.removeprefix("the ")) for c in WOMEN_AT_WORK_IN]
    specs += [(f"Street vendors in {c}", False, doing("They are selling things in the street."),
               c.removeprefix("the ")) for c in STREET_VENDORS_IN]
    return specs


def build_commons_daily_life(limit):
    """The Commons daily-life pack: the categories take turns, in a fixed shuffled order, so each gets an even share
    (the activity categories about two thirds of the pack, the countries the rest). Files must be CC0, public domain
    or CC BY (mechanical_packs.mech_entries notes every other file with its reason). Each picture gets its
    category's question and, when it has a real, respectful English caption or description, "Describe this
    picture." too; the place is the category's country, else the country at the file's camera coordinates. Files
    whose words name a child are marked "child"; nudity, bathing and graphic words leave a file out. Stops looking
    at half the time limit (listing_out_of_time) and fetches what it found."""
    s, items, seen = session(), [], set()
    specs = commons_daily_specs()
    pass_random("daily").shuffle(specs)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(specs))))
    want = int(limit * 1.15) + 2
    queues = [[spec, None] for spec in specs]
    rounds = 0
    while len(items) < want and queues and rounds < 40 and not listing_out_of_time():
        rounds += 1
        for q in list(queues):
            if len(items) >= want or listing_out_of_time():
                break
            (category, deeper, rows, country), files = q
            if files is None:
                found = category_files(s, category, deeper)
                files = [t for t in found if t not in seen and not DAILY_NOT_A_PHOTO.search(t)]
                pass_random(category).shuffle(files)
                say(f"Commons {category}: {len(files)} files")
            batch, q[1] = files[:share * 2], files[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            got = 0
            for title, url, credit, text, _ in mech_entries(s, batch):
                if got >= share or title in seen:
                    continue
                words = NOT_A_CHILD.sub(" ", f"{category} {title} {text}")
                text = "" if JUST_A_RECORD.search(text or "") or NOT_A_DESCRIPTION.search(text or "") \
                    or not in_english(text) else text
                if NUDE.search(words) or DAILY_NOT.search(words) or DAILY_NOT_A_PHOTO.search(text or ""):
                    considered(title, url, "its words are about nudity, bathing or a graphic scene, or it is not a "
                                           "photo")
                    continue
                described = text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text)
                if not rows and not described:
                    considered(title, url, "a work category's file without a real English description")
                    continue
                seen.add(title)
                place = where(country_named(country) or country if country else PLACES.get(title, ""))
                out = [mark_child({"question": qn, "answer": an, "credit": credit, **place}, words) for qn, an in rows]
                if described:
                    out.append(mark_child({"question": NARRATE if not rows else ALT_TEXT, "answer": text,
                                           "credit": credit, **place}, words))
                items.append((file_name("daily", title), url, out))
                got += 1
            if not q[1]:
                queues.remove(q)
    pass_random("daily-order").shuffle(items)
    return with_twins(commons_fetch(items[:want])[:limit])


# ----------------------------------------------------------------- dollar_street_routines (Gapminder)

# Dollar Street's daily-routine topics (the ones with photos; most of its routine topics are videos), with what the
# photo is about. Topics about the toilet, showers, menstruation and bathing are not used.
DS_ROUTINES = {
    "hand-washing": "how this family washes their hands",
    "washing-hands": "how this family washes their hands",
    "washing-clothes": "how this family washes their clothes",
    "drying-clothes": "how this family dries their clothes",
    "cleaning-floors": "how this family cleans the floor",
    "shaving": "what this family uses for shaving",
    "get-water": "where this family gets their water",
    "drinking-water": "the water this family drinks, and what they keep it in",
    "dinner-guests": "a family with guests at dinner",
    "walking-to-get-water": "someone walking to get water",
    "chopping-food": "someone chopping food",
    "starting-stoves": "how this family lights their stove",
    "answering-phones": "someone answering a phone",
    "sleeping": "where and how someone in this family sleeps",
    "socializing": "this family spending time with others",
}


def build_dollar_street_routines(limit):
    """The Dollar Street routines pack's pictures: about the same number of photos from each routine topic, each with
    the family's country (Gapminder's own record) and photographers; "What daily routine does this picture show?"
    -> "It shows how this family washes their hands." Photos of the same family in two topics are taken once."""
    from world_life_packs import ds_hits, ds_photographers, DS_PAGE
    s, items, photographers, seen = session(), [], {}, set()
    topics = sorted(DS_ROUTINES)
    pass_random(147).shuffle(topics)
    per_topic = max(1, math.ceil(limit * 1.15 / len(topics)))
    for topic in topics:
        if len(items) >= limit * 1.15 or listing_out_of_time():
            break
        hits = [h for h in ds_hits(s, topic) if (h.get("images") or {}).get("full1024") and h["id"] not in seen]
        pass_random(topic).shuffle(hits)
        for h in hits[:per_topic]:
            seen.add(h["id"])
            place = h.get("place") or {}
            country = (h.get("country") or place.get("country") or {}).get("name", "")
            who = photographers.get(place.get("id"))
            if who is None:
                time.sleep(0.3)
                who = ds_photographers(s, h["id"], photographers)
            credit = (f"Photo: {who or 'Gapminder'}, Dollar Street (Gapminder, www.gapminder.org/dollar-street), "
                      f"CC BY 4.0: {DS_PAGE}{place.get('slug', '')}")
            row = {"question": ROUTINE_Q, "answer": f"It shows {DS_ROUTINES[topic]}.", "credit": credit}
            if topic in ("dinner-guests", "socializing", "sleeping"):
                row = mark_child(row, " ".join(t.get("name", "") for t in h.get("topics") or []))
            if country:
                row.update(where(country_named(country) or country))
            items.append((f"ds-routine-{h['id']}.jpg", h["images"]["full1024"], [row]))
        say(f"Dollar Street {topic}: {len(hits)} photos")
    pass_random(148).shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.15) + 2], workers=4, pause=0.2)[:limit])


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons daily-life categories: captions CC0; pictures CC0, public domain or CC BY, each "
                  "with its author and file page below. https://commons.wikimedia.org")
COCO_ROWS_NOTE = (" Rows only: the pictures are COCO's photos, which this pack does not copy; the kit fetches each "
                  "one from cocodataset.org. COCO does not name its photographers; each photo's licence is in its row.")
PEOPLE_ACTIVITY_PACKS = {
    "vcoco_actions": (build_vcoco_actions,
                      "V-COCO, Verbs in COCO (Saurabh Gupta and Jitendra Malik, 2015), MIT licence, "
                      "https://github.com/s-gupta/v-coco (Copyright (c) 2016 The Regents of the University of "
                      "California); person and object boxes from COCO (Lin et al., 2014), CC BY 4.0, "
                      "https://cocodataset.org. Only photos whose own COCO licence is CC BY 2.0 or no known "
                      "copyright. Changes: the marked actions and objects turned into plain sentences." +
                      COCO_ROWS_NOTE),
    "vg_people_actions": (build_vg_people_actions,
                          "Visual Genome 1.2 (Ranjay Krishna et al., 2017), CC BY 4.0, https://visualgenome.org; "
                          "only its COCO photos whose own COCO licence is CC BY 2.0 or no known copyright. Changes: "
                          "the relationships people drew between boxes turned into plain sentences." +
                          COCO_ROWS_NOTE),
    "open_images_activities": (build_open_images_activities,
                               "Open Images V7 (Google): image-level labels verified by people, CC BY 4.0, "
                               "https://storage.googleapis.com/openimages/web/index.html. Each photo is CC BY 2.0 "
                               "(checked photo by photo), credited below with its photographer and Flickr page. "
                               "Changes: photos made smaller; the labels turned into plain sentences."),
    "commons_daily_life": (build_commons_daily_life, COMMONS_CREDIT),
    "dollar_street_routines": (build_dollar_street_routines,
                               "Dollar Street by Gapminder (www.gapminder.org/dollar-street), CC BY 4.0; each "
                               "photographer credited below. Changes: photos made smaller; the topic turned into a "
                               "plain sentence."),
    "coco_actions_nc": (build_coco_actions_nc,
                        "V-COCO (MIT, https://github.com/s-gupta/v-coco) and Visual Genome 1.2 (CC BY 4.0, "
                        "https://visualgenome.org) rows on COCO photos whose own licence is CC BY-NC, BY-NC-SA, "
                        "BY-NC-ND or BY-ND 2.0: for personal, non-commercial use only. Boxes from COCO, CC BY 4.0." +
                        COCO_ROWS_NOTE),
    "coco_actions_sa": (build_coco_actions_sa,
                        "V-COCO (MIT, https://github.com/s-gupta/v-coco) and Visual Genome 1.2 (CC BY 4.0, "
                        "https://visualgenome.org) rows on COCO photos under CC BY-SA 2.0: anything made from them "
                        "keeps the same licence. Boxes from COCO, CC BY 4.0." + COCO_ROWS_NOTE),
}

# How many pictures (rows, for the rows-only packs) a full build takes from each.
PEOPLE_ACTIVITY_LIMITS = {
    "vcoco_actions": 1800,            # 1,727 V-COCO photos are CC BY 2.0 or no known copyright (rows)
    "vg_people_actions": 1800,        # 1,762 of the 7,772 free Visual Genome COCO photos say what someone is doing
    "open_images_activities": 6000,   # validation and test first, then the training set
    "commons_daily_life": 3500,
    "dollar_street_routines": 1250,   # about 1,250 photos in the routine topics (most routines are videos)
    "coco_actions_nc": 16200,         # 7,621 V-COCO and 8,520 Visual Genome rows (November 2026)
    "coco_actions_sa": 2400,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one people-activity pack builder.")
    parser.add_argument("key", choices=sorted(PEOPLE_ACTIVITY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = PEOPLE_ACTIVITY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"places: " + ", ".join(f"{p} {n}" for p, n in places.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
