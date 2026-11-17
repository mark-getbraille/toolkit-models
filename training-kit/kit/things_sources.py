"""Technology, tools, kitchen gadgets, hardware and building supplies, and people using them, for the Picture Model
Training Kit: the collections that cannot be ready-made packs because of their licence (non-commercial, or research
use only, or no terms stated). The open ones (Amazon Berkeley Objects products, Open Images people-using-things and
technology labels, Commons electronics, tools, building supplies, kitchen gadgets and people at work, brick grades,
building waste and building surfaces) are in packs/things_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py):
  "noncommercial"  CC BY-NC or other non-commercial terms. Personal use only (--personal-noncommercial).
  "research"       research use only, or no licence stated for the labels. Personal use only (--personal-research
                   with --accept-research-terms).

Answers are fixed sentences from each source's own labels (an action's verb and object, a class of action, an object's
colour and material that people marked, a material class), never written by an AI model.

Where in the world: none of these collections states a country for each picture, so no "place" is given. EPIC-KITCHENS
was filmed in 45 kitchens in 4 cities in Europe and North America (its pages do not say which kitchen is where);
Charades was filmed in people's own homes through Amazon Mechanical Turk; PACO's photos are COCO's (Flickr); MINC's are
from OpenSurfaces (Flickr) and Houzz.

The collections (THINGS_SOURCES):
  noncommercial
    epic_kitchens        EPIC-KITCHENS-55 (University of Bristol and others, CC BY-NC 4.0): frames filmed from the
                         cook's head in home kitchens, each in the middle of an action people named ("open fridge",
                         "cut onion"): "What is the person doing?" -> "They are cutting the onion." Only the start of
                         each person's shortest video (10 minutes at most) is used, so every kitchen is in it; its
                         frame tar (up to about 600 MB) is read straight from the web and only the chosen frames are
                         kept.
    charades             Charades (Allen Institute for AI, 2016; non-commercial licence): videos people filmed of
                         themselves at home doing everyday things with household objects; one still from the middle of
                         a named action: "What is the person doing?" -> "They are holding a laptop." Only the chosen
                         videos are read out of the 16 GB zip by HTTP ranges. Needs the video extras (PyAV).
  research
    paco_attributes      PACO, Parts and Attributes of Common Objects (Meta AI, 2023): the colour, material and
                         pattern people marked on 75 kinds of everyday objects (mugs, kettles, laptops, drills, hammers,
                         pliers, wrenches, blenders, phones ...) in COCO photos: "What is the mug made of?" -> "The mug
                         is made of ceramic." Only photos with one object of that kind. The annotations have no licence
                         of their own (the repository's MIT licence names its source code), so personal use only.
    minc_materials       MINC-2500, Materials in Context (Bell, Upchurch, Snavely and Bala, Cornell, CVPR 2015): close
                         patches of brick, carpet, ceramic, fabric, glass, leather, metal, mirror, painted surfaces,
                         paper, plastic, polished stone, stone, tile, wallpaper and wood: "What material is this?" The
                         labels are CC BY 4.0 but the photos keep their own licences, which the patches do not give.

Needing sign-up (cannot be downloaded automatically; THINGS_SIGN_UP has the links): Ego4D, EgoObjects, PACO's Ego4D
frames, Something-Something v2, Assembly101, the MINC full-resolution photos, Roboflow Universe and IEEE DataPort
electronic-component sets, and Kaggle sets.

Looked at and not included (THINGS_NOT_INCLUDED has the reasons): HOI4D, 100 Days of Hands.

THINGS_PICTURE_MAKING_OK: only minc_materials (close patches of materials, no people). PACO's photos often show
people, and the rest are about people.

    python -c "import sources, things_sources"      (from the kit folder: checks the file loads)
"""

import csv
import io
import json
import os
import random
import re
import zipfile

import sources
from big_sources import even_pick
from extra_sources import save, say, stream_tar, video_still
from more_sources import download_to, fetch_shared
from personal_sources import remote_zip, zip_members
from sources import Source, clean

DOING_Q = "What is the person doing?"


def gerund(verb):
    """The -ing form of a plain English verb ("cut" -> "cutting", "take" -> "taking", "turn-on" -> "turning on")."""
    first, _, rest = verb.replace("-", " ").partition(" ")
    special = {"put": "putting", "cut": "cutting", "get": "getting", "set": "setting", "let": "letting",
               "stab": "stabbing", "rip": "ripping", "pat": "patting", "scrub": "scrubbing", "flip": "flipping",
               "drop": "dropping", "grab": "grabbing", "stir": "stirring", "chop": "chopping", "wrap": "wrapping",
               "unwrap": "unwrapping", "plug": "plugging", "unplug": "unplugging", "dip": "dipping",
               "rub": "rubbing", "tap": "tapping", "hug": "hugging", "sit": "sitting", "run": "running",
               "lie": "lying", "die": "dying", "see": "seeing", "be": "being", "unfreeze": "unfreezing"}
    if first in special:
        word = special[first]
    elif first.endswith("ie"):
        word = first[:-2] + "ying"
    elif first.endswith("e") and not first.endswith(("ee", "ye", "oe")):
        word = first[:-1] + "ing"
    else:
        word = first + "ing"
    return f"{word} {rest}".strip()


# ----------------------------------------------------------------- noncommercial: EPIC-KITCHENS-55

EPIC_ANNOTATIONS = "https://raw.githubusercontent.com/epic-kitchens/epic-kitchens-100-annotations/master/"
EPIC_FRAMES = ("https://data.bris.ac.uk/datasets/3h91syskeag572hl6tvuovwv4d/frames_rgb_flow/rgb/{split}/"
               "{participant}/{video}.tar")
EPIC_SPLITS = ("https://raw.githubusercontent.com/epic-kitchens/epic-kitchens-download-scripts/master/data/"
               "epic_55_splits.csv")            # which EPIC-KITCHENS-55 videos are in its "train" or "test" folder
EPIC_MOST_SECONDS = 600            # only videos of at most 10 minutes (their frame tar is about 600 MB at most)
EPIC_FRAME_BYTES = 17_000           # about how big one frame is, for the download estimate
# The verbs used (clear, visible actions), and how a sentence says the object after them.
EPIC_VERBS = {"take": "", "put": "down", "wash": "", "open": "", "close": "", "insert": "", "turn-on": "",
              "cut": "", "turn-off": "", "pour": "", "mix": "", "move": "", "remove": "", "throw": "away",
              "dry": "", "shake": "", "scoop": "", "squeeze": "", "peel": "", "empty": "", "press": "", "flip": "",
              "fill": "", "scrape": "", "apply": "", "fold": "", "scrub": "", "break": "", "pull": "", "lift": "",
              "hold": "", "eat": "", "wrap": "", "filter": "", "unroll": "", "hang": "up", "sprinkle": "",
              "rip": "", "spray": "", "cook": "", "add": "", "roll": "", "crush": "", "stretch": "", "knead": "",
              "divide": "", "rub": "", "soak": "", "brush": "", "sharpen": "", "drink": "", "slide": "",
              "water": "", "attach": "", "coat": "", "wear": "", "measure": "", "unscrew": "", "grate": "",
              "screw": "", "stab": "", "serve": "", "uncover": "", "unwrap": "", "lock": "", "flatten": "",
              "carry": "", "season": "", "unlock": "", "bake": "", "bend": "", "unfreeze": ""}
EPIC_CREDIT = ("EPIC-KITCHENS-55 (Dima Damen, Hazel Doughty, Giovanni Maria Farinella and others, University of "
               "Bristol, University of Catania and University of Toronto), CC BY-NC 4.0, "
               "https://epic-kitchens.github.io")


def epic_noun(key):
    """A noun class key in plain words ("pan:frying" -> "frying pan", "onion:spring" -> "spring onion")."""
    parts = key.replace("_", " ").split(":")
    return " ".join(reversed(parts))


def epic_answer(verb, noun):
    """ "They are cutting the onion." / "They are putting the plate down." """
    after = EPIC_VERBS[verb]
    return f"They are {gerund(verb)} the {noun}" + (f" {after}" if after else "") + "."


def epic_csv(name):
    """One of EPIC-KITCHENS' annotation files (from its GitHub), as a list of dict rows."""
    import requests
    r = requests.get(EPIC_ANNOTATIONS + name, timeout=120, headers={"User-Agent": sources.USER_AGENT})
    r.raise_for_status()
    return list(csv.DictReader(io.StringIO(r.content.decode("utf-8"))))


def prepare_epic_kitchens(source, data_dir, work, cap):
    """EPIC-KITCHENS-55 frames with their action: for each person, their shortest video (of at most
    EPIC_MOST_SECONDS) with enough named actions, and frames from the middle of an even share of its actions. A
    video's frames are stored in its tar in no order, so the whole tar is read from the web (it stops once every
    wanted frame is found); only the chosen frames are kept."""
    import requests
    nouns = {r["id"]: epic_noun(r["key"]) for r in epic_csv("EPIC_100_noun_classes.csv")}
    seconds = {r["video_id"]: float(r["duration"]) for r in epic_csv("EPIC_100_video_info.csv")}
    r = requests.get(EPIC_SPLITS, timeout=120, headers={"User-Agent": sources.USER_AGENT})
    r.raise_for_status()
    split_of = {row["video_id"]: row["split"] for row in csv.DictReader(io.StringIO(r.text))}
    actions = {}
    for row in epic_csv("EPIC_100_train.csv"):
        video = row["video_id"]
        if video not in split_of or seconds.get(video, 1e9) > EPIC_MOST_SECONDS or row["verb"] not in EPIC_VERBS \
                or row["noun_class"] not in nouns:
            continue
        middle = (int(row["start_frame"]) + int(row["stop_frame"])) // 2
        actions.setdefault(row["participant_id"], {}).setdefault(video, []).append(
            (middle, epic_answer(row["verb"], nouns[row["noun_class"]])))
    want = cap + source.test
    per_person = max(4, -(-want // max(1, len(actions))))
    folder = os.path.join(data_dir, source.key)
    rows = []
    for participant in sorted(actions):
        if len(rows) >= want:
            break
        videos = actions[participant]
        usable = [v for v in videos if len(videos[v]) >= per_person] or list(videos)
        video = min(usable, key=lambda v: seconds[v])
        chosen = sorted(videos[video])
        random.Random(video).shuffle(chosen)
        frames = {}
        for middle, answer in chosen:
            frames.setdefault(f"frame_{middle:010d}.jpg", answer)
            if len(frames) >= per_person:
                break
        done = {}

        def take(member, tar, frames=frames, done=done, video=video):
            """Keep a wanted frame; stop once all are kept."""
            base = os.path.basename(member.name)
            if base in frames and base not in done:
                path = save(f"{video}-{base[:-4]}", tar.extractfile(member).read(), folder)
                done[base] = path
            return len(done) >= len(frames)

        size = seconds[video] * 60 * EPIC_FRAME_BYTES / 1e6
        url = EPIC_FRAMES.format(split=split_of[video], participant=participant, video=video)
        try:
            stream_tar(url, take, f"EPIC-KITCHENS {video} (about {size:,.0f} MB)")
        except Exception as e:  # noqa: BLE001 - a video that cannot be read is left out
            say(f"  EPIC-KITCHENS {video} could not be read ({str(e)[:100]}); left out.")
        for base, path in done.items():
            if path:
                rows.append({"picture": path, "question": DOING_Q, "answer": frames[base], "split": ""})
        say(f"  EPIC-KITCHENS {participant}: {sum(1 for p in done.values() if p)} frames from {video}.")
    return rows


# ----------------------------------------------------------------- noncommercial: Charades

CHARADES = "https://ai2-public-datasets.s3-us-west-2.amazonaws.com/charades/"
CHARADES_VIDEOS = CHARADES + "Charades_v1_480.zip"        # 16 GB: read by HTTP ranges
CHARADES_LABELS = CHARADES + "Charades.zip"               # 3.5 MB
CHARADES_CREDIT = ("Charades (Gunnar A. Sigurdsson, Gul Varol, Xiaolong Wang, Ali Farhadi, Ivan Laptev and Abhinav "
                   "Gupta, ECCV 2016), Allen Institute for AI, licence for non-commercial use, "
                   "https://prior.allenai.org/projects/charades")
# Classes that are about the person, not a thing, or that a still cannot show, are left out.
CHARADES_NOT_SEEN = re.compile(r"\b(sneezing|laughing|smiling|awakening|someone is|watching|standing up|sitting "
                               r"down|walking|running|undressing|dressing)\b", re.I)


def charades_answer(name):
    """ "Holding a laptop" -> "They are holding a laptop." """
    name = clean(name)
    return f"They are {name[0].lower()}{name[1:]}." if name else ""


def prepare_charades(source, data_dir, work, cap):
    """Charades stills: for each chosen video, one action (the longest of those a still can show) and a still from
    its middle (PyAV; install requirements-video.txt); an even share for each action class. Only the chosen videos
    (about 3 MB each) are read out of the 16 GB zip, and kept in the downloads folder."""
    labels = download_to(work, CHARADES_LABELS)
    with zipfile.ZipFile(labels) as z:
        classes = {}
        for line in z.read("Charades/Charades_v1_classes.txt").decode("utf-8").splitlines():
            code, _, name = line.partition(" ")
            if code and name and not CHARADES_NOT_SEEN.search(name):
                classes[code] = name
        videos = list(csv.DictReader(io.StringIO(z.read("Charades/Charades_v1_train.csv").decode("utf-8"))))
    groups = {}
    for v in videos:
        try:
            length = float(v["length"])
        except (KeyError, ValueError):
            continue
        best = None
        for part in (v.get("actions") or "").split(";"):
            bits = part.split()
            if len(bits) == 3 and bits[0] in classes:
                start, end = float(bits[1]), float(bits[2])
                if 0 <= start < end <= length and (best is None or end - start > best[2] - best[1]):
                    best = (bits[0], start, end)
        if best:
            groups.setdefault(best[0], []).append((v["id"], (best[1] + best[2]) / 2 / length))
    picked = even_pick(groups, cap + source.test, 331)
    code_of = {vid: code for code, items in groups.items() for vid, _ in items}
    chosen = [(f"Charades_v1_480/{vid}.mp4", {"question": DOING_Q, "answer": charades_answer(classes[code_of[vid]]),
                                              "split": "", "_at": at}) for vid, at in picked]
    say(f"  Charades: {len(chosen)} videos chosen from {len(groups)} actions.")
    rows = []
    for at in sorted({round(row["_at"], 1) for _, row in chosen}):
        group = [(name, {k: v for k, v in row.items() if k != "_at"}) for name, row in chosen
                 if round(row["_at"], 1) == at]
        rows += zip_members(source, data_dir, work, lambda: remote_zip(CHARADES_VIDEOS), group, workers=3,
                            prepare_picture=lambda data, at=at: video_still(data, at=min(0.95, max(0.05, at))))
    return rows


# ----------------------------------------------------------------- research: PACO

PACO_ZIP = "https://dl.fbaipublicfiles.com/paco/annotations/paco_lvis_v1.zip"      # 134 MB
PACO_CREDIT = ("PACO: Parts and Attributes of Common Objects (Vignesh Ramanathan, Anmol Kalia and others, Meta AI, "
               "CVPR 2023), https://github.com/facebookresearch/paco; photos from COCO (cocodataset.org, Flickr)")
PACO_MATERIALS = {"stone", "wood", "rattan", "fabric", "crochet", "wool", "leather", "velvet", "metal", "paper",
                  "plastic", "glass", "ceramic"}
PACO_PATTERNS = {"striped", "dotted", "checkered", "woven", "studded", "perforated", "floral"}
PACO_NAMES = {"car_(automobile)": "car", "drum_(musical_instrument)": "drum", "glass_(drink_container)": "glass",
              "laptop_computer": "laptop", "mouse_(computer_equipment)": "computer mouse", "pan_(for_cooking)": "pan",
              "slipper_(footwear)": "slipper", "tape_(sticky_cloth_or_paper)": "roll of tape",
              "cellular_telephone": "mobile phone", "television_set": "television", "trash_can": "bin",
              "remote_control": "remote control", "plastic_bag": "plastic bag", "tissue_paper": "tissue paper"}


def paco_colour(name):
    """A PACO colour in plain words ("light_blue" -> "light blue", "grey" stays)."""
    return name.replace("_", " ")


def prepare_paco_attributes(source, data_dir, work, cap):
    """PACO-LVIS (validation and test annotations): for photos with exactly one object of a kind whose material,
    colour or pattern people marked, "What is the X made of?", "What colour is the X?" and "What pattern does the X
    have?"; an even share for each kind of object; the photos are fetched from COCO."""
    path = download_to(work, PACO_ZIP)
    per_photo, groups = {}, {}
    with zipfile.ZipFile(path) as z:
        for member in ("paco_lvis_v1_val.json", "paco_lvis_v1_test.json"):
            with z.open(member) as f:
                data = json.load(f)
            attributes = {a["id"]: a["name"] for a in data["attributes"]}
            kinds = {c["id"]: c["name"] for c in data["categories"] if ":" not in c["name"]}
            images = {i["id"]: i for i in data["images"]}
            count = {}
            for a in data["annotations"]:
                if a["category_id"] in kinds:
                    count[(a["image_id"], a["category_id"])] = count.get((a["image_id"], a["category_id"]), 0) + 1
            for a in data["annotations"]:
                kind = kinds.get(a["category_id"])
                if not kind or count[(a["image_id"], a["category_id"])] != 1 or a["image_id"] not in images:
                    continue
                names = [attributes[i] for i in a.get("attribute_ids") or [] if i in attributes]
                thing = PACO_NAMES.get(kind, kind.replace("_", " "))
                rows = []
                materials = [n for n in names if n in PACO_MATERIALS]
                if len(materials) == 1:
                    rows.append((f"What is the {thing} made of?", f"The {thing} is made of {materials[0]}."))
                colours = [paco_colour(attributes[i]) for i in a.get("dom_color_ids") or [] if i in attributes]
                colours = [c for c in colours if not c.startswith("other")]
                if 1 <= len(colours) <= 2:
                    rows.append((f"What colour is the {thing}?", f"The {thing} is {' and '.join(colours)}."))
                patterns = [n for n in names if n in PACO_PATTERNS]
                if len(patterns) == 1:
                    rows.append((f"What pattern does the {thing} have?", f"The {thing} is {patterns[0]}."))
                elif "plain" in names and not patterns:
                    rows.append((f"What pattern does the {thing} have?", f"The {thing} is plain, with no pattern."))
                if not rows:
                    continue
                image = images[a["image_id"]]
                key = f"paco-{image['id']}"
                per_photo.setdefault(key, (image.get("coco_url") or "", []))[1].extend(rows)
                groups.setdefault(kind, []).append(key)
    picked = even_pick({k: sorted(set(v)) for k, v in groups.items()}, cap + source.test, 401)
    items = []
    for key in dict.fromkeys(picked):
        url, rows = per_photo[key]
        if not url:
            continue
        for question, answer in rows[:3]:
            items.append((f"{key}.jpg", url, {"question": question, "answer": answer, "split": ""}))
    say(f"  PACO: {len(set(picked))} photos of {len(groups)} kinds of object.")
    return fetch_shared(items, os.path.join(data_dir, source.key))


# ----------------------------------------------------------------- research: MINC-2500

MINC_URL = "http://opensurfaces.cs.cornell.edu/static/minc/minc-2500.tar.gz"         # 2.1 GB
MINC_CREDIT = ("MINC-2500, Materials in Context Database (Sean Bell, Paul Upchurch, Noah Snavely and Kavita Bala, "
               "Cornell University, CVPR 2015), labels CC BY 4.0, "
               "http://opensurfaces.cs.cornell.edu/publications/minc/; "
               "photos from OpenSurfaces (Flickr) and Houzz, under their own licences")
MINC_ANSWERS = {"brick": "It is brick.", "carpet": "It is carpet.", "ceramic": "It is ceramic.",
                "fabric": "It is fabric (cloth).", "glass": "It is glass.", "leather": "It is leather.",
                "metal": "It is metal.", "mirror": "It is a mirror.", "painted": "It is a painted surface.",
                "paper": "It is paper.", "plastic": "It is plastic.", "polishedstone": "It is polished stone.",
                "stone": "It is stone.", "tile": "These are tiles.", "wallpaper": "It is wallpaper.",
                "wood": "It is wood."}
MINC_Q = "What material is this?"


def prepare_minc_materials(source, data_dir, work, cap):
    """MINC-2500 patches (362 x 362 pixels) of the materials above (not skin, hair, food, plants, sky or water), an
    even share of each, read straight from the 2.1 GB archive and stopped once every material has its share."""
    want = cap + source.test
    quota = -(-want // len(MINC_ANSWERS))
    folder = os.path.join(data_dir, source.key)
    counts, rows = {}, []

    def take(member, tar):
        """Keep a patch of a wanted material until its share is full."""
        parts = member.name.split("/")
        if len(parts) < 3 or parts[-3] != "images" or not member.name.endswith(".jpg"):
            return False
        kind = parts[-2]
        if kind in MINC_ANSWERS and counts.get(kind, 0) < quota:
            path = save(f"minc-{os.path.basename(member.name)[:-4]}", tar.extractfile(member).read(), folder)
            if path:
                counts[kind] = counts.get(kind, 0) + 1
                rows.append({"picture": path, "question": MINC_Q, "answer": MINC_ANSWERS[kind], "split": ""})
        return len(counts) == len(MINC_ANSWERS) and min(counts.values()) >= quota

    stream_tar(MINC_URL, take, "MINC-2500 (2.1 GB at most)")
    say(f"  MINC: {len(rows)} patches of {len(counts)} materials.")
    return rows


# ----------------------------------------------------------------- the collections

THINGS_SOURCES = [
    # ---- non-commercial
    Source("epic_kitchens", "EPIC-KITCHENS: what a cook's hands are doing in a home kitchen (personal use)",
           "CC BY-NC 4.0 (epic-kitchens.github.io)", EPIC_CREDIT, "noncommercial", 1000, 20,
           prepare_epic_kitchens, "about 4 to 8 GB, read straight from the web (only the pictures are kept)",
           terms="https://creativecommons.org/licenses/by-nc/4.0/",
           terms_summary="CC BY-NC 4.0: use with credit, not for commercial purposes (EPIC-KITCHENS sells commercial "
                         "licences separately)."),
    Source("charades", "Charades: people at home doing everyday things with household objects, stills (personal "
                       "use)",
           "Licence for non-commercial use (Allen Institute for AI; in Charades.zip, license.txt)", CHARADES_CREDIT,
           "noncommercial", 1000, 20, prepare_charades,
           "about 3 GB of videos (kept), needs the video extras",
           terms="https://prior.allenai.org/projects/charades",
           terms_summary="For academic, non-profit or government research and evaluation; not for a for-profit "
                         "enterprise; the data may not be passed on or published, except short stills in an "
                         "academic paper; treat the people in it with respect and dignity."),
    # ---- research
    Source("paco_attributes", "PACO: the colour, material and pattern of everyday objects (personal use)",
           "No licence stated for the annotations (the repository's MIT licence names its source code); photos "
           "from COCO, each under its Flickr licence", PACO_CREDIT, "research", 1500, 20,
           prepare_paco_attributes, "134 MB of labels and about 250 MB of photos",
           terms="https://github.com/facebookresearch/paco",
           terms_summary="No licence is stated for the annotations; personal, non-commercial use only. The photos "
                         "are COCO's, each under its own Flickr licence."),
    Source("minc_materials", "MINC-2500: close-ups of materials (brick, wood, metal, tile ...) (personal use)",
           "Labels CC BY 4.0; photos under their own licences, not given for the patches "
           "(opensurfaces.cs.cornell.edu/publications/minc)", MINC_CREDIT, "research", 1600, 32,
           prepare_minc_materials, "up to 2.1 GB, read once",
           terms="http://opensurfaces.cs.cornell.edu/publications/minc/",
           terms_summary="The labels are CC BY 4.0, but the photos keep their own licences (Flickr and Houzz), "
                         "which the patches do not name; personal, non-commercial use only."),
]

# The collections a picture-making model may learn from: materials without people.
THINGS_PICTURE_MAKING_OK = {"minc_materials"}

THINGS_SIGN_UP = {
    "Ego4D (Meta and partners; licence agreement)":
        "https://ego4ddataset.com : sign the Ego4D licence agreement; credentials come in about 48 hours. 3,670 "
        "hours of first-person video from 74 places in 9 countries (scenarios such as cooking, carpentry, "
        "bike repair, building work, knitting), with narrations.",
    "PACO-Ego4D frames": "https://github.com/facebookresearch/paco : the frames come through the Ego4D agreement "
                         "(above). The PACO-LVIS part (COCO photos) is the paco_attributes entry.",
    "EgoObjects (Meta AI; repository MIT)":
        "https://ai.meta.com/datasets/egoobjects-downloads : the 40 GB of images are given only after accepting "
        "Meta's terms on that page. 114,000 frames of 368 kinds of indoor objects filmed by 250 people worldwide.",
    "Something-Something v2 (Qualcomm; research licence)":
        "https://www.qualcomm.com/developer/software/something-something-v-2-dataset : a Qualcomm account and "
        "acceptance of its licence. 220,000 short videos of hands doing things with objects ('putting something "
        "into something').",
    "Assembly101 (NUS and Meta; CC BY-NC 4.0)":
        "https://huggingface.co/datasets/cvml-nus/assembly101 : a gated Hugging Face dataset (log in and accept), "
        "or a 14-day Google Drive access request. People taking apart and putting together toy vehicles with "
        "screwdrivers, filmed in Singapore.",
    "MINC full-resolution photos (non-commercial research)":
        "http://opensurfaces.cs.cornell.edu/publications/minc/ : a form that makes a terms document. The patches "
        "(MINC-2500) are the minc_materials entry.",
    "Roboflow Universe electronic-component sets (resistors, capacitors, LEDs, chips, Arduino boards)":
        "https://universe.roboflow.com : a free Roboflow account and API key. Several are marked CC BY 4.0 (for "
        "example school-p0xt8/electric-components-kkgsp); check each set's licence and where its photos came from.",
    "IEEE DataPort BEPD (balanced electronic package dataset)":
        "https://ieee-dataport.org/documents/balanced-electronic-package-dataset-bepd-6-capacitors-dip-8-dip-16-"
        "7-segment-resistors : an IEEE account; 540 photos of capacitors, chips, displays and resistors.",
    "Kaggle tool, electronics and e-waste sets": "https://www.kaggle.com : a Kaggle account; check each set's licence "
                                                 "and where its pictures came from.",
}

THINGS_NOT_INCLUDED = {
    "HOI4D (CC BY-NC 4.0)": "the files are only in OneDrive and Baidu share folders (Baidu needs a password), with "
                            "no direct addresses the kit can download from, and the RGB videos are hundreds of "
                            "gigabytes. It can be added if its makers publish direct links.",
    "100 Days of Hands (100DOH)": "its project page (fouheylab.eecs.umich.edu) did not answer (503) in November "
                                  "2026; its frames are stills of YouTube videos with no licence stated.",
    "EPIC-KITCHENS-100 extension videos": "only the EPIC-KITCHENS-55 videos are used: the extension's frames are "
                                          "in a different store, and the 55 part already gives every kitchen.",
    "Open Images visual relationships, Amazon Berkeley Objects": "open (CC BY 4.0): ready-made packs "
                                                                 "open_images_in_use and abo_products.",
}
