"""Disability and assistive-technology picture collections for the Picture Model Training Kit that cannot be
ready-made packs because of their licence (share-alike, research-only, or no terms written at all). The open ones
(Open Images devices and disability sports, Wikimedia Commons CC0/PD/CC BY files including Disabled And Here and the
Warrior Games, and TaPaD tactile paving) are packs in packs/disability_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py): "share-alike" (only with the share-alike choice), "research" (research or
educational terms, or no terms stated at all: personal use only, after agreeing to the terms).

Respect and safety:
  - Answers are fixed sentences from each dataset's own labels, about what people use and do ("a person using a
    walking frame"), never pitying. Commons descriptions with pitying or outdated words (NOT_RESPECTFUL) or any word
    of nudity are not learnt from.
  - Rows whose words name a child, and Commons files from a subcategory about children, carry "child": true.
  - DISABILITY_PICTURE_MAKING_OK holds only collections of pictures without people: braille pages and aerial photos
    of car parks. Never people or children.

The collections (DISABILITY_SOURCES):
  share-alike
    commons_disability_sa   Wikimedia Commons disability and accessibility categories: files under CC BY-SA or GFDL.
  research (research terms, or none stated)
    mobility_aids           Freiburg Mobility Aids dataset (Vasquez, Kollmitz, Eitel and Burgard, 2017): hospital
                            and university photos of people using wheelchairs, crutches and walking frames, or pushing
                            a wheelchair ("for research purposes only; any commercial use is prohibited").
    angelina_braille        Angelina Braille Images Dataset (Ovodov, 2021): phone photos of braille book pages and
                            handwritten braille, every cell labelled, plus printed documents with no braille (no
                            licence stated). "Is there braille in this picture?" and the first line, cell by cell.
    dsbi_braille            DSBI, Double-Sided Braille Image dataset (Li, Liu, Wan and Qiang, 2018): scanned pages of
                            Chinese braille books, every cell labelled (no licence stated).
    visible_disability      "visible-disability" on Hugging Face (zzh-2002): photos with wheelchairs, walking sticks
                            and walking frames boxed (no licence or source of the photos stated).
    wheelchair_types        "various_wheelchairs" on Hugging Face (samitesla): product photos of ten kinds of
                            wheelchairs and mobility scooters (no licence stated; shop photos).
    wheelchair_detection    "wheel-chair-images-annotation4object-detec" on Hugging Face (Falah): photos with
                            wheelchairs boxed ("Apache-2.0" stated, but who took the photos is not said).
    rotterdam_accessibility Mobility and Accessibility in Rotterdam (Martin, Vos, Piepaliute and Holef, Erasmus
                            University, 2025): street photos judged accessible or not for wheelchairs, walkers and
                            prams ("Apache-2.0" stated, but most photos are from Google Street View, Google Images
                            and Bing, whose terms do not allow re-licensing).
    accessparkcv            AccessParkCV (Hwang, Li, Kang, Hosseini and Froehlich, University of Washington, ASSETS
                            2025): aerial photos of car parks in Seattle, Washington DC and Spring Hill with the
                            disability parking spaces and access aisles outlined ("MIT" and "CC BY 4.0" stated, but
                            the aerial photos come from city imagery whose own terms are not given).

Already in the kit, so not repeated here: ORBIT (blind people's own photos of white canes, guide-dog harnesses and
braille devices; the orbit pack), VizWiz (blind people's photos; vizwiz_quality and the VizWiz questions), How2Sign
(American Sign Language; extra_sources.py), the Open Images and Commons sign-language and tactile-signing rows
(packs/expression_packs.py), the Open Images wheelchair, walking frame, crutch and walking-stick labels as household
objects (open_images_objects) and in the street (open_images_street), and the Seoul pavements (seoul_sidewalks).

Needing sign-up (cannot be downloaded automatically; get them yourself, then put the pictures in the own-pictures
folder with your own descriptions, as the user guide says):
  DVIDS (US Defense Visual Information         https://www.dvidshub.net : photos of adaptive sports and the Warrior
  Distribution Service)                        Games are public domain, but its API needs a free key
                                               (https://api.dvidshub.net). Many of the same photos are on Commons and
                                               are already in the commons_disability pack.
  Roboflow Universe tactile paving, braille    https://universe.roboflow.com (for example
  and wheelchair sets                          universe.roboflow.com/project-bflsl/braille_block_intrusion_seg, CC BY
                                               4.0, and the braille sets codefair/braille-fzvs1 and
                                               prasarnmit-demonstration-school/braille-xpelz): a free Roboflow account
                                               and API key are needed; each set shows its own licence, and many hold
                                               photos copied from the web.
  Kaggle braille sets (for example             https://www.kaggle.com/datasets/shanks0465/braille-character-dataset :
  the Braille Character Dataset)               a Kaggle account is needed; check each set's licence and where its
                                               pictures came from.
  GuideTWSI (tactile walking surface           https://arxiv.org/abs/2603.07060 : released on its project website;
  indicators)                                  check its licence there.
  Crowd4Access footpath photos (Dublin City    https://doras.dcu.ie/26261 : ask the authors; no download or licence
  University)                                  is published.
  US VA, NIH and CDC photo libraries           https://www.va.gov , https://www.nih.gov , https://phil.cdc.gov : public
                                               domain, but searched by hand through their web pages (no bulk download
                                               of disability photos); the Commons categories already carry many.

Looked at and not included (the reason of each is in DISABILITY_NOT_INCLUDED).

    python -c "import sources, disability_sources"      (from the kit folder: checks the file loads)
"""

import ast
import hashlib
import json
import os
import random
import re
import urllib.parse
import zipfile

import sources
from big_sources import even_pick
from extra_sources import (NO_TERMS, NUDE, commons_file_name, commons_members, commons_sa_entries,
                           commons_session, parquet_picture_rows, per_label, research)
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS, listed, remote_zip, zip_members
from sources import ALT_TEXT, USER_AGENT, Source, download_file, fetch_pictures

DEVICE_Q = "What assistive device is in this picture?"
SPORT_Q = "What sport is this?"
AIDS_Q = "What mobility aids can you see in this picture?"
BRAILLE_Q = "Is there braille in this picture?"
FIRST_LINE_Q = "Write out the first line of braille in this picture, cell by cell, in Unicode braille."

# Words that pity disabled people or are outdated or offensive (as packs/disability_packs.py).
NOT_RESPECTFUL = re.compile(r"\b(suffer\w*|afflict\w*|victims?|wheelchair[- ]bound|confined to|cripple\w*|crippled|"
                            r"handicapped|invalids?|retard\w*|deaf[- ]and[- ]dumb|deaf[- ]mutes?|dumb|lame|"
                            r"spastics?|mongol\w*|midgets?|defective|abnormal|poor (man|woman|boy|girl)|"
                            r"brave(ly)?|inspir\w*|despite (his|her|their) disabilit\w*|beggars?)\b", re.I)

# A description that is really a place name with language links ("zh:屯門 Tuen Mun ...") or in another script.
NOT_A_DESCRIPTION = re.compile(r"\b[a-z]{2}:\S|[^\x00-\u024f\u2010-\u2027]")
# Words that mean a child's device or a child, beyond personal_sources.CHILD_WORDS.
YOUNG = re.compile(r"\b(p(a)?ediatric\w*|children's)\b", re.I)


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def side(middle):
    """ "on the left", "in the middle" or "on the right" for a centre given as a share of the picture's width."""
    return "on the left" if middle < 0.36 else "on the right" if middle > 0.64 else "in the middle"


def place_list(things):
    """ "On the left, a person using a wheelchair; in the middle, ..." from [(centre share, words)], left to right,
    with things on the same side joined."""
    by_side = {}
    for middle, words in sorted(things):
        by_side.setdefault(side(middle), []).append(words)
    parts = [f"{where}, {listed(items)}" for where, items in by_side.items()]
    text = "; ".join(parts) + "."
    return text[0].upper() + text[1:]


def braille_cells(bits):
    """A Unicode braille character from dots as bits (dot 1 the lowest bit ... dot 6 the highest)."""
    return chr(0x2800 + (bits & 0x3F))


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

BRAILLE = ("This is braille: writing made of raised dots, in cells of up to six dots, that blind people read with "
           "their fingertips.")
TACTILE = ("Yes: there is tactile paving, ground with raised bumps that blind and partially sighted people can feel "
           "with their feet or a cane.")
ACCESSIBLE_TOILET = ("It is an accessible toilet, made for wheelchair users and other disabled people, with room to "
                     "move and support rails.")
# Each category: (question, answer, whether one level of its subcategories is used too); the same table as the open
# commons_disability pack, which takes the CC0, public-domain and CC BY files of the same categories.
COMMONS_DISABILITY = {
    "White canes": (DEVICE_Q, "A white cane: a long white cane that blind and partially sighted people sweep or tap "
                              "ahead of them to find obstacles, steps and kerbs.", True),
    "People with white canes": (DEVICE_Q, "A white cane: a long white cane that blind and partially sighted people "
                                          "use to find their way.", False),
    "Guide dogs": ("What kind of dog is this?", "It is a guide dog: a dog trained to lead a blind or partially "
                                                "sighted person safely around obstacles.", True),
    "Assistance dogs": ("What kind of dog is this?", "It is an assistance dog: a dog trained to help a disabled "
                                                     "person.", False),
    "Braille texts": ("What is this?", BRAILLE, False),
    "Braille publications": ("What is this?", BRAILLE, False),
    "Braille by country": ("What is this?", BRAILLE, True),
    "Refreshable Braille displays": (DEVICE_Q, "A refreshable braille display: a flat device with rows of small "
                                               "pins that rise and fall to show braille from a computer or phone, "
                                               "read with the fingertips.", False),
    "Braille writing instruments": (DEVICE_Q, "A braille writing tool, such as a braille writer (a Perkins brailler) "
                                              "or a slate and stylus.", True),
    "Braille keyboards": (DEVICE_Q, "A braille keyboard, with keys for the six braille dots.", False),
    "People reading Braille": ("What is this person doing?", "Reading braille: feeling the raised dots with their "
                                                             "fingertips.", False),
    "Wheelchairs": (DEVICE_Q, "A wheelchair.", False),
    "People in wheelchairs": (DEVICE_Q, "A wheelchair.", True),
    "Electric wheelchairs": (DEVICE_Q, "A powered (electric) wheelchair, driven with a small joystick.", False),
    "Mobility scooters": (DEVICE_Q, "A mobility scooter: a small electric scooter with a seat, for people who "
                                    "find walking far difficult.", True),
    "Rollators": (DEVICE_Q, "A rollator: a walking frame with wheels, handles with brakes, and often a seat.", False),
    "Crutches": (DEVICE_Q, "Crutches.", False),
    "Forearm crutches": (DEVICE_Q, "Forearm crutches (elbow crutches), with a cuff round the forearm.", False),
    "People with crutches": (DEVICE_Q, "Crutches.", False),
    "Walking sticks": (DEVICE_Q, "A walking stick.", False),
    "Limb prostheses": (DEVICE_Q, "A prosthesis: an artificial leg or arm.", True),
    "Hand prostheses": (DEVICE_Q, "A prosthetic hand: an artificial hand.", False),
    "People with limb prostheses": (DEVICE_Q, "A prosthesis: an artificial limb.", True),
    "People with bionic prostheses": (DEVICE_Q, "A bionic prosthesis: a powered artificial limb.", False),
    "Hearing aids": (DEVICE_Q, "A hearing aid: a small device worn in or behind the ear that makes sounds louder.",
                     False),
    "Hearing aids in use": (DEVICE_Q, "A hearing aid, worn behind or in the ear.", False),
    "Hearing aid types": (DEVICE_Q, "A hearing aid.", True),
    "Cochlear implants": (DEVICE_Q, "A cochlear implant: a hearing device with a sound processor worn behind the "
                                    "ear and a round coil held on the side of the head by a magnet.", False),
    "Tactile paving": ("Is there tactile paving here?", TACTILE, False),
    "Directional tactile paving": ("Is there tactile paving here?", "Yes: there is guiding tactile paving, raised "
                                                                    "lines that show which way to walk.", False),
    "Tactile studs": ("Is there tactile paving here?", "Yes: there are tactile warning studs, raised dots that warn "
                                                       "of a hazard ahead, such as a crossing, steps or a platform "
                                                       "edge.", False),
    "Tactile paving on curb cuts": ("Is there tactile paving here?", TACTILE + " Here it marks a dropped kerb, where "
                                    "the pavement meets the road.", False),
    "Tactile paving in train stations": ("Is there tactile paving here?", TACTILE + " Here it is in a station, "
                                         "leading along the platform or warning of its edge.", False),
    "Accessible toilets": ("What kind of toilet is this?", ACCESSIBLE_TOILET, False),
    "Accessible public toilets": ("What kind of toilet is this?", ACCESSIBLE_TOILET, False),
    "Disability handrails": (DEVICE_Q, "Grab rails: support rails that help a disabled person stand, sit or move "
                                       "across, for example by a toilet.", False),
    "Accessible bathrooms": ("What kind of room is this?", "An accessible bathroom, made for wheelchair users and "
                                                           "other disabled people.", False),
    "Wheelchair ramps": ("Is there a ramp here?", "Yes: there is a wheelchair ramp, a gentle slope in place of steps.",
                         True),
    "Wheelchair lifts": (DEVICE_Q, "A wheelchair lift: a platform that raises a wheelchair user up steps or into a "
                                   "vehicle.", False),
    "Stair lifts": (DEVICE_Q, "A stair lift: a seat that runs along a rail up the stairs.", False),
    "Kneeling buses": ("What is this?", "A kneeling bus: it lowers its floor at the stop, so getting on is easier "
                                        "with a wheelchair, a pram or a walking aid.", False),
    "Vehicles with wheelchair ramps": ("What is this?", "A vehicle with a wheelchair ramp, so a wheelchair user can "
                                                        "get on board.", False),
    "Disabled parking": ("What does this show?", "Accessible parking: parking spaces kept for disabled people, "
                                                 "usually marked with the wheelchair symbol.", True),
    "Accessibility signs": ("What does this sign show?", "It is an accessibility sign, showing a facility or route "
                                                         "for disabled people.", True),
    "Priority seats": ("What are these seats?", "Priority seats: seats kept for disabled, older or pregnant "
                                                "passengers, or anyone who needs to sit.", False),
    "Wheelchair spaces": ("What is this space for?", "It is a wheelchair space, kept for a wheelchair user, for "
                                                     "example on a bus or train or in a theatre.", False),
    "Screen readers": ("What is shown here?", "Screen-reader software, which reads out what is on a computer or "
                                              "phone screen for blind people.", True),
    "Screen magnifiers": ("What is shown here?", "Screen-magnifier software, which enlarges part of the screen for "
                                                 "people with low vision.", False),
    "Augmentative and alternative communication": (DEVICE_Q, "An AAC (augmentative and alternative communication) "
                                                             "aid, which helps someone who does not speak, or speaks "
                                                             "little, to communicate.", True),
    "Wheelchair basketball": (SPORT_Q, "This is wheelchair basketball: basketball played by athletes in sports "
                                       "wheelchairs.", False),
    "Wheelchair rugby": (SPORT_Q, "This is wheelchair rugby: a full-contact team sport played in strong sports "
                                  "wheelchairs.", False),
    "Wheelchair racing": (SPORT_Q, "This is wheelchair racing: athletes race in light three-wheeled racing "
                                   "wheelchairs, pushing the wheels with their hands.", False),
    "Wheelchair tennis": (SPORT_Q, "This is wheelchair tennis: tennis played from sports wheelchairs; the ball may "
                                   "bounce twice.", False),
    "Goalball": (SPORT_Q, "This is goalball: a team sport for blind and partially sighted athletes, who wear "
                          "blacked-out eyeshades and roll a ball with bells inside towards the other team's goal.",
                 False),
    "Blind football": (SPORT_Q, "This is blind football: five-a-side football for blind and partially sighted "
                                "players, with a ball that rattles.", False),
    "Paralympic sports": (SPORT_Q, "This is a Paralympic sport, played by disabled athletes.", True),
    "Warrior Games": ("What event is this?", "This is the Warrior Games, adaptive sports for wounded, "
                                                           "ill and injured service members and veterans.", True),
    "Images from Disabled and Here": (None, None, False),     # (all CC BY 4.0: in the open pack, none here)
}
COMMONS_NOT_IT = re.compile(r"\b(art|drawings?|illustrations?|paintings?|logos?|icons?|emoji|U\+[0-9A-F]+|svg|"
                            r"sculptures?|statues?|videos?|audio|recordings?|maps?|diagrams?|stamps?|coins?|"
                            r"advertis\w*|posters?|cartoons?|comics?|in literature|organi[sz]ations?|"
                            r"associated|manufacturers?|companies|shops?|museums?|collections?|x-rays?|radiograph\w*|"
                            r"scans?|surgery|operations?|veterinary|dogs? wheelchairs|nude|naked|logo|"
                            r"history|historical|charts?|penile|breasts?|heart|valves?|spine|dental|dentures?|"
                            r"prosthodontics|epithes\w*|voice|nose|ocular|eyes?|implants?|licen[cs]e plates?|parent|"
                            r"watches|cosplay\w*|SVG|ramps? signs)\b", re.I)


def prepare_commons_disability_sa(source, data_dir, work, cap):
    """Wikimedia Commons disability and accessibility categories (the table above): files under CC BY-SA or GFDL,
    each with the category's question and, where it has a real and respectful description, "Write a short
    description ..." too. The categories share the cap; files from a subcategory about children, or whose words name
    a child, are marked "child"."""
    s, items, seen = commons_session(), [], set()
    per_category = per_label(int((cap + source.test) * 0.9), len(COMMONS_DISABILITY))
    for category, (question, answer, deeper) in COMMONS_DISABILITY.items():
        if question is None:
            continue
        titles, young = commons_members(s, category, "file"), set()
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                sub = sub.split(":", 1)[-1]
                if not COMMONS_NOT_IT.search(sub):
                    files = commons_members(s, sub, "file")
                    titles += files
                    if CHILD_WORDS.search(sub):
                        young.update(files)
        titles = [t for t in dict.fromkeys(titles) if t not in seen and not COMMONS_NOT_IT.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 4]):
            if found >= per_category or NUDE.search(f"{title} {text}"):
                continue
            seen.add(title)
            child = {"child": True} if title in young or CHILD_WORDS.search(f"{title} {text}") \
                or YOUNG.search(f"{title} {text}") else {}
            name = commons_file_name("dis-sa", title)
            url = re.sub(r"/\d+px-([^/]+)$", r"/960px-\1", url)      # a width Wikimedia keeps ready
            items.append((name, url, {"question": question, "answer": answer, "split": "", "credit": credit,
                                      **child}))
            if text and not NOT_RESPECTFUL.search(text) and not NOT_A_DESCRIPTION.search(text):
                items.append((name, url, {"question": ALT_TEXT, "answer": text, "split": "", "credit": credit,
                                          **child}))
            found += 1
        say(f"  Commons {category}: {found} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- research: Freiburg Mobility Aids

MOBILITY = "http://mobility-aids.informatik.uni-freiburg.de/dataset/"
MOBILITY_WORDS = {
    "wheelchair": "a person using a wheelchair",
    "push_wheelchair": "a person pushing someone in a wheelchair",
    "crutches": "a person using crutches",
    "walking_frame": "a person using a walking frame",
    "person": "a person walking without a mobility aid",
}
BOX = re.compile(r"bndbox:\s*\{([^}]*)\}\s*name:\s*(\w+)")


def mobility_boxes(text):
    """[(class, x centre as a share of the width)] from one annotation file (YAML, read with a regular
    expression so no YAML library is needed)."""
    width = re.search(r"width:\s*'?(\d+)", text)
    width = int(width.group(1)) if width else 960
    out = []
    for inside, name in BOX.findall(text):
        xs = dict((k, float(v)) for k, v in re.findall(r"(xmin|xmax):\s*'?([\d.]+)'?", inside))
        if name in MOBILITY_WORDS and len(xs) == 2:
            out.append((name, (xs["xmin"] + xs["xmax"]) / 2 / width))
    return out


def prepare_mobility_aids(source, data_dir, work, cap):
    """The Freiburg Mobility Aids dataset: RGB photos taken by a robot's camera in a hospital in Frankfurt and the
    university's buildings, with every person boxed by the aid they use. The annotations (7.6 MB) are downloaded
    once; the chosen photos are read one by one out of the 12.4 GB zip by HTTP ranges, spread evenly over the
    aids. "What mobility aids can you see in this picture?" with where each person is."""
    keep = os.path.join(work, source.key)
    os.makedirs(keep, exist_ok=True)
    notes = os.path.join(keep, "Annotations_RGB.zip")
    download_file(MOBILITY + "Annotations_RGB.zip", notes)
    groups = {}
    with zipfile.ZipFile(notes) as z:
        for member in z.namelist():
            if not member.endswith(".yml"):
                continue
            text = z.read(member).decode("utf-8", "replace")
            boxes = mobility_boxes(text)
            aids = [b for b in boxes if b[0] != "person"]
            if not aids:
                continue
            picture = re.search(r"filename:\s*(\S+)", text)
            stem = picture.group(1) if picture else os.path.basename(member).replace(".yml", ".png")
            groups.setdefault(aids[0][0], []).append((f"Images_RGB/{stem}", boxes))
    picked = even_pick({k: [json.dumps(v) for v in items] for k, items in groups.items()}, cap + source.test, 241)
    chosen = []
    for item in picked:
        member, boxes = json.loads(item)
        answer = place_list([(middle, MOBILITY_WORDS[name]) for name, middle in boxes])
        chosen.append((member, {"question": AIDS_Q, "answer": answer, "split": "",
                                "credit": "Mobility Aids Dataset (Vasquez, Kollmitz, Eitel and Burgard, University "
                                          "of Freiburg, 2017), http://mobility-aids.informatik.uni-freiburg.de"}))
    say(f"  Mobility Aids: {len(chosen)} photos ({', '.join(f'{k} {len(v)}' for k, v in sorted(groups.items()))}).")
    return zip_members(source, data_dir, work, lambda: remote_zip(MOBILITY + "Images_RGB.zip"), chosen, workers=3)


# ----------------------------------------------------------------- research: braille pages (Angelina, DSBI)

ANGELINA = "https://raw.githubusercontent.com/IlyaOvodov/AngelinaDataset/master/"
ANGELINA_LISTS = {
    "books": ("books/train.txt", "books/val.txt"),
    "handwritten": ("handwritten/train.txt", "handwritten/val.txt"),
    "not_braille": ("not_braille/train.txt",),
    "uploaded": ("uploaded/test.txt",),
}
ANGELINA_KINDS = {
    "books": "Yes: this is a photo of a page of a braille book in Russian braille, embossed on both sides of the "
             "paper.",
    "handwritten": "Yes: this is a photo of a page of braille written by hand by a student, in Russian braille.",
    "uploaded": "Yes: this is a photo of a page of braille.",
    "not_braille": "No: this is a printed document with ink print, and there is no braille on it.",
}


def braille_lines(cells):
    """Lines of Unicode braille from cells [(left, top, right, bottom, bits)] (boxes as shares of the picture): the
    cells are grouped into lines by their height on the page, put in order left to right, with a space where the gap
    is wider than about one cell. Empty when there are no cells."""
    if not cells:
        return []
    heights = sorted(b - t for _, t, _, b, _ in cells)
    widths = sorted(right - left for left, _, right, _, _ in cells)
    h, w = heights[len(heights) // 2], widths[len(widths) // 2]
    lines = []
    for cell in sorted(cells, key=lambda c: (c[1] + c[3]) / 2):
        middle = (cell[1] + cell[3]) / 2
        if lines and abs(middle - lines[-1][0]) < h * 0.6:
            lines[-1][1].append(cell)
        else:
            lines.append([middle, [cell]])
    out = []
    for _, line in lines:
        line.sort(key=lambda c: c[0])
        text, last = "", None
        for left, _, right, _, bits in line:
            if last is not None and left - last > w * 0.9:
                text += " " * max(1, round((left - last) / (w * 1.6)))
            text += braille_cells(bits)
            last = right
        out.append(text)
    return out


def prepare_angelina_braille(source, data_dir, work, cap):
    """The Angelina Braille Images Dataset: phone photos of braille book pages, handwritten braille and printed
    documents without braille, from its GitHub repository (about 60 MB). Each braille photo's CSV gives every cell's
    box and dots, so the first line of braille can be written out cell by cell in Unicode braille (the page's own
    signs, whatever its language). "Is there braille in this picture?" for every photo."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    groups = {}
    for kind, lists in ANGELINA_LISTS.items():
        for name in lists:
            folder = name.rsplit("/", 1)[0]
            for line in s.get(ANGELINA + name, timeout=60).text.splitlines():
                path = line.strip().replace("\\", "/")
                if path.lower().endswith(".jpg"):
                    groups.setdefault(kind, []).append(f"{folder}/{path}")
    picked = even_pick(groups, cap + source.test, 251)
    kind_of = {p: k for k, items in groups.items() for p in items}
    credit = "Angelina Braille Images Dataset (Ilya G. Ovodov, 2021), https://github.com/IlyaOvodov/AngelinaDataset"
    items = []
    for path in picked:
        kind = kind_of[path]
        name = "angelina-" + re.sub(r"[^\w.-]", "_", path)[-100:]
        url = ANGELINA + "/".join(requests.utils.quote(p) for p in path.split("/"))
        items.append((name, url, {"question": BRAILLE_Q, "answer": ANGELINA_KINDS[kind], "split": "",
                                  "credit": credit}))
        if kind == "not_braille":
            continue
        cells = []
        r = s.get(url[:-4] + ".csv", timeout=60)
        for row in r.text.splitlines() if r.status_code == 200 else []:
            parts = row.split(";")
            try:
                left, top, right, bottom, bits = (float(parts[0]), float(parts[1]), float(parts[2]),
                                                  float(parts[3]), int(parts[4]))
            except (IndexError, ValueError):
                continue
            if 1 <= bits <= 63:
                cells.append((left, top, right, bottom, bits))
        lines = braille_lines(cells)
        if lines and lines[0].strip():
            items.append((name, url, {"question": FIRST_LINE_Q, "split": "", "credit": credit,
                                      "answer": f"{lines[0].strip()} (the page has about {len(lines)} lines of "
                                                f"braille)."}))
    say(f"  Angelina: {len(picked)} photos ({', '.join(f'{k} {len(v)}' for k, v in sorted(groups.items()))}).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


DSBI = "https://raw.githubusercontent.com/yeluo1994/DSBI/master/"
DSBI_BOOKS = {"Massage": "a book about massage", "Fundamentals of Massage": "a book called Fundamentals of Massage",
              "The Second Volume of Ninth Grade Chinese Book 1": "a ninth-grade Chinese language textbook",
              "The Second Volume of Ninth Grade Chinese Book 2": "a ninth-grade Chinese language textbook",
              "Math": "a mathematics book", "Shaver Yang Fengting": "the novel Shaver Yang Fengting",
              "Ordinary printed document": "an ordinary braille document"}


def dsbi_cells(text):
    """{line: {column: bits}} from a DSBI annotation (after the angle and the two grid lines, one cell a line:
    row, column and its six dots 1 to 6 as 0 or 1)."""
    cells = {}
    for line in text.splitlines()[3:]:
        parts = line.split()
        if len(parts) == 8 and all(p.isdigit() for p in parts):
            row, col, dots = int(parts[0]), int(parts[1]), [int(p) for p in parts[2:]]
            bits = sum(1 << i for i, d in enumerate(dots) if d)
            if bits:
                cells.setdefault(row, {})[col] = bits
    return cells


def prepare_dsbi_braille(source, data_dir, work, cap):
    """DSBI: 114 colour scans (200 dpi) of pages of six Chinese braille books and a braille document, embossed on
    both sides, with every cell of the front side marked on a grid. "Is there braille in this picture?" and the
    first line of the front side, cell by cell in Unicode braille (empty cells as spaces)."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    paths = []
    for name in ("train.txt", "test.txt"):
        paths += [p.strip().replace("\\", "/") for p in s.get(DSBI + name, timeout=60).text.splitlines()
                  if p.strip().lower().endswith(".jpg")]
    random.Random(252).shuffle(paths)
    credit = ("DSBI: Double-Sided Braille Image dataset (Renqiang Li, Hong Liu, Xiangdong Wan and Yueliang Qiang, "
              "Institute of Computing Technology, Chinese Academy of Sciences, 2018), "
              "https://github.com/yeluo1994/DSBI")
    items = []
    for path in paths[:cap + source.test]:
        book = path.split("/")[0]
        url = DSBI + "data/" + requests.utils.quote(path)
        name = "dsbi-" + re.sub(r"[^\w.-]", "_", path)
        recto = s.get(url[:-4] + "%2Brecto.txt", timeout=60)
        verso = s.get(url[:-4] + "%2Bverso.txt", timeout=60)
        cells = dsbi_cells(recto.text) if recto.status_code == 200 else {}
        two_sided = verso.status_code == 200 and dsbi_cells(verso.text)
        answer = (f"Yes: this is a scanned page of braille from {DSBI_BOOKS.get(book, 'a braille book')}, in Chinese "
                  "braille." + (" It is embossed on both sides: the dots of this side stand up, and the dots "
                                "pressed from the other side show as dents between them." if two_sided else ""))
        items.append((name, url, {"question": BRAILLE_Q, "answer": answer, "split": "", "credit": credit}))
        if cells:
            first = cells[min(cells)]
            line = "".join(braille_cells(first[c]) if c in first else " " for c in range(1, max(first) + 1))
            if line.strip():
                items.append((name, url, {"question": FIRST_LINE_Q, "split": "", "credit": credit,
                                          "answer": f"{line.strip()} (the page has {len(cells)} lines of braille)."}))
    say(f"  DSBI: {len(paths[:cap + source.test])} scans.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=3)


# ----------------------------------------------------------------- research: mobility aids on Hugging Face

VISIBLE_WORDS = {"wheelchair": "a wheelchair", "stick": "a walking stick or cane", "walking_frame": "a walking frame"}


def prepare_visible_disability(source, data_dir, work, cap):
    """"visible-disability" (zzh-2002 on Hugging Face, one 180 MB parquet file): photos with wheelchairs, walking
    sticks and walking frames boxed. "What assistive device is in this picture?" from the box labels (photos with
    only people boxed are left out)."""
    def text_of(record):
        """(picture id, row) for one parquet row, or None."""
        try:
            names = ast.literal_eval(record.get("objects_categories") or "[]")
        except (ValueError, SyntaxError):
            return None
        aids = list(dict.fromkeys(VISIBLE_WORDS[n] for n in names if n in VISIBLE_WORDS))
        data = (record.get("image") or {}).get("bytes") or b""
        if not aids or not data:
            return None
        return hashlib.sha1(data).hexdigest()[:16], {
            "question": DEVICE_Q, "answer": f"There is {listed(aids)}.", "split": "",
            "credit": "visible-disability, https://huggingface.co/datasets/zzh-2002/visible-disability"}
    return parquet_picture_rows(source, data_dir, "zzh-2002/visible-disability", r"^data/", "image", text_of, cap,
                                253)


WHEELCHAIR_TYPES = {
    "manual_wheelchair": "a manual wheelchair, pushed by the user's own hands on the wheel rims",
    "power_wheelchair": "a powered (electric) wheelchair, driven with a joystick",
    "transport_wheelchair": "a transport wheelchair, with small wheels, pushed by a helper",
    "ultralight_wheelchair": "an ultralight wheelchair, a light rigid chair for active everyday use",
    "sports_wheelchair": "a sports wheelchair, with wheels angled outwards for quick turns",
    "racing_wheelchair": "a racing wheelchair, long and low with three wheels",
    "all_terrain_wheelchair": "an all-terrain wheelchair, with wide tyres for rough ground",
    "bariatric_wheelchair": "a bariatric wheelchair, extra wide and strong",
    "pediatric_wheelchair": "a children's wheelchair",
    "mobility_scooter": "a mobility scooter, an electric scooter with a seat and handlebars",
}


def prepare_wheelchair_types(source, data_dir, work, cap):
    """"various_wheelchairs" (samitesla on Hugging Face): about 245 product photos sorted into ten kinds of
    wheelchairs and mobility scooters. "What kind of wheelchair is this?" The children's wheelchair photos are
    marked "child" (a child may be sitting in them)."""
    from huggingface_hub import HfApi
    repo = "samitesla/various_wheelchairs"
    groups = {}
    for f in HfApi().list_repo_files(repo, repo_type="dataset"):
        kind = f.split("/")[0]
        if kind in WHEELCHAIR_TYPES and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            groups.setdefault(kind, []).append(f)
    items = []
    for f in even_pick(groups, cap + source.test, 254):
        kind = f.split("/")[0]
        items.append((re.sub(r"[^\w.-]", "_", f)[-100:].rsplit(".", 1)[0] + ".jpg",
                      f"https://huggingface.co/datasets/{repo}/resolve/main/" + urllib.parse.quote(f),
                      {"question": "What kind of wheelchair is this?", "split": "",
                       "answer": f"It is {WHEELCHAIR_TYPES[kind]}.",
                       "credit": "various_wheelchairs, https://huggingface.co/datasets/samitesla/various_wheelchairs",
                       **({"child": True} if kind == "pediatric_wheelchair" else {})}))
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


def prepare_wheelchair_detection(source, data_dir, work, cap):
    """"wheel-chair-images-annotation4object-detec" (Falah on Hugging Face, one 25 MB parquet file): 416-pixel
    photos with people and wheelchairs boxed (boxes are centre and size as shares of the picture). "Is there a
    wheelchair in this picture?" with where it is, for photos with a wheelchair box."""
    def text_of(record):
        """(picture id, row) for one parquet row, or None."""
        boxes = [i for i in record.get("instances") or [] if i.get("label") == 1 and len(i.get("box") or []) == 4]
        data = (record.get("image") or {}).get("bytes") or b""
        if not boxes or not data:
            return None
        sides = sorted({side(b["box"][0]) for b in boxes}, key=["on the left", "in the middle", "on the right"].index)
        what = "a wheelchair" if len(boxes) == 1 else f"{len(boxes)} wheelchairs"
        return hashlib.sha1(data).hexdigest()[:16], {
            "question": "Is there a wheelchair in this picture?", "split": "",
            "answer": f"Yes, there is {what}, {listed(sides)}.",
            "credit": "Wheelchair dataset for object detection (Falah), "
                      "https://huggingface.co/datasets/Falah/wheel-chair-images-annotation4object-detec"}
    return parquet_picture_rows(source, data_dir, "Falah/wheel-chair-images-annotation4object-detec", r"^data/",
                                "image", text_of, cap, 255)


ROTTERDAM = ("https://huggingface.co/datasets/comarti15/accessibility-rotterdam-the-netherlands/resolve/main/"
             "Data%20Challenge.zip")
ROTTERDAM_ANSWERS = {
    "Accessible": "Yes, it looks accessible: the way looks clear and even enough for a wheelchair, a walker or a pram.",
    "Inaccessible": "No, it looks hard to get through: the people who labelled it saw a barrier for wheelchairs, "
                    "walkers or prams here, such as a blocked or missing pavement, no ramp or dropped kerb, or bikes "
                    "or scooters in the way.",
}


def prepare_rotterdam_accessibility(source, data_dir, work, cap):
    """Mobility and Accessibility in Rotterdam (Erasmus University students, 2025): 1,883 street photos sorted into
    Accessible and Inaccessible folders, read one by one out of the 371 MB zip by HTTP ranges, the two kinds evenly.
    "Can a wheelchair user get along here?" """
    z = remote_zip(ROTTERDAM)
    groups = {}
    for member in z.namelist():
        parts = member.split("/")
        if len(parts) >= 4 and parts[-2] in ROTTERDAM_ANSWERS and member.lower().endswith((".jpg", ".jpeg", ".png")):
            groups.setdefault(parts[-2], []).append(member)
    z.close()
    chosen = [(m, {"question": "Can a wheelchair user get along here?", "split": "",
                   "answer": ROTTERDAM_ANSWERS[m.split("/")[-2]], "place": "Rotterdam, Netherlands",
                   "credit": "Mobility and Accessibility in Rotterdam (Cora Martin, Yu Vos, Agne Piepaliute and Lucas "
                             "Holef, Erasmus University Rotterdam, 2025), https://huggingface.co/datasets/comarti15/"
                             "accessibility-rotterdam-the-netherlands"})
              for m in even_pick(groups, cap + source.test, 256)]
    return zip_members(source, data_dir, work, lambda: remote_zip(ROTTERDAM), chosen, workers=3)


ACCESSPARK = "https://huggingface.co/datasets/makeabilitylab/AccessParkCV_coco/resolve/main/disabilityparking_dataset/"


def accesspark_answer(names):
    """The answer for one aerial photo from its outlined things' class names; "" when it shows no disability
    parking space."""
    spaces = {"dp_no_aisle": 0, "dp_one_aisle": 0, "dp_two_aisle": 0}
    for n in names:
        if n in spaces:
            spaces[n] += 1
    total = sum(spaces.values())
    if not total:
        return ""
    aisle = spaces["dp_one_aisle"] + spaces["dp_two_aisle"]
    beside = "a striped access aisle beside {} for getting a wheelchair in and out"
    if total == 1:
        how = f"with {beside.format('it')}" if aisle else "with no access aisle beside it"
        return f"This is an aerial photo of a car park, seen from straight above. It shows one disability parking " \
               f"space, {how}."
    if aisle == total:
        how = f"all with {beside.format('them')}"
    elif not aisle:
        how = "none with an access aisle beside it"
    else:
        how = f"{aisle} with {beside.format('them' if aisle > 1 else 'it')} and {total - aisle} without"
    return f"This is an aerial photo of a car park, seen from straight above. It shows {total} disability parking " \
           f"spaces, {how}."


def prepare_accessparkcv(source, data_dir, work, cap):
    """AccessParkCV (University of Washington Makeability Lab, 2025): 512-pixel aerial photos of car parks with
    disability parking spaces and access aisles outlined (COCO files of the train, valid and test parts, 4 MB).
    "Is there disability parking here?" with how many spaces and whether they have an access aisle."""
    import requests
    groups = {}
    for part in ("train", "valid", "test"):
        data = requests.get(ACCESSPARK + f"{part}/_annotations.coco.json", timeout=120,
                            headers={"User-Agent": USER_AGENT}).json()
        names = {c["id"]: c["name"] for c in data["categories"]}
        found = {}
        for a in data["annotations"]:
            found.setdefault(a["image_id"], []).append(names.get(a["category_id"], ""))
        for image in data["images"]:
            answer = accesspark_answer(found.get(image["id"], []))
            if answer:
                kind = "several" if answer.count("disability parking spaces") else "one"
                groups.setdefault(kind, []).append(json.dumps([part, image["file_name"], answer]))
    items = []
    for item in even_pick(groups, cap + source.test, 257):
        part, file_name, answer = json.loads(item)
        items.append((f"accesspark-{file_name}", ACCESSPARK + f"{part}/{file_name}",
                      {"question": "Is there disability parking here?", "answer": "Yes. " + answer, "split": "",
                       "credit": "AccessParkCV (Jared Hwang, Chu Li, Hanbyul Kang, Maryam Hosseini and Jon E. "
                                 "Froehlich, ASSETS 2025), https://huggingface.co/datasets/makeabilitylab/"
                                 "AccessParkCV_coco"}))
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- what could not be included

DISABILITY_NOT_INCLUDED = {
    "Project Sidewalk (University of Washington)": "its crowd labels of kerb ramps, missing ramps, obstacles and "
                                                   "surface problems are CC0, but they are marked on Google Street "
                                                   "View imagery, which may not be downloaded or re-used.",
    "Dataset Multi Braille Characters (Mendeley Data s4pmywvwbc, CC BY 4.0)": "its single braille cells are cut-out "
                                                                              "scans of 42 by 24 pixels (too small to "
                                                                              "learn from) and many are machine-made "
                                                                              "copies; its multi-cell pictures carry "
                                                                              "no labels.",
    "Tactile Braille Letters datasets (Zenodo 7050094 and 13841759)": "recordings from a robot's touch sensor, not "
                                                                      "pictures.",
    "Formella Braille (Zenodo 10381638)": "a 3D model of one braille panel, not photos.",
    "Synthetic disability picture sets (electricsheepafrica on Hugging Face)": "made by an AI picture generator; the "
                                                                                "kit only learns from real pictures "
                                                                                "and people's own words.",
    "Getty Images Disability Collection, Microsoft inclusive images": "stock photos sold under licence, not open and "
                                                                     "not downloadable for training.",
    "The Gender Spectrum Collection (Vice)": "not about disability, and its photos are for editorial use under its own "
                                             "terms (no derivatives), not for training.",
    "Freiburg Mobility Aids depth images": "only the colour photos are used (mobility_aids); the depth pictures show "
                                           "no more for a describer.",
}


# ----------------------------------------------------------------- the table

DISABILITY_SOURCES = [
    # ---- share-alike
    Source("commons_disability_sa", "Wikimedia Commons: disability and assistive technology, files under CC BY-SA or "
                                    "GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 20, prepare_commons_disability_sa, "about 150 MB"),
    # ---- research or no stated terms
    Source("mobility_aids", "Freiburg Mobility Aids: people using wheelchairs, crutches and walking frames in a "
                            "hospital (research only; personal use)",
           "For research purposes only; commercial use prohibited (mobility-aids.informatik.uni-freiburg.de)",
           "Mobility Aids Dataset (Andres Vasquez, Marina Kollmitz, Andreas Eitel and Wolfram Burgard, University of "
           "Freiburg, 2017), http://mobility-aids.informatik.uni-freiburg.de", "research", 1500, 20,
           prepare_mobility_aids, "about 1.1 GB of photos, read out of a 12.4 GB zip",
           terms="http://mobility-aids.informatik.uni-freiburg.de/",
           terms_summary=research("This dataset is provided for research purposes only. Any commercial use is "
                                  "prohibited. Cite the authors' paper.")),
    Source("angelina_braille", "Angelina: photos of braille book pages and handwritten braille (personal use)",
           "No licence stated (github.com/IlyaOvodov/AngelinaDataset)",
           "Angelina Braille Images Dataset (Ilya G. Ovodov, 'Optical Braille Recognition Using Object Detection "
           "Neural Network', ICCV Workshops 2021), https://github.com/IlyaOvodov/AngelinaDataset", "research", 334,
           15, prepare_angelina_braille, "about 30 MB", terms="https://github.com/IlyaOvodov/AngelinaDataset",
           terms_summary="No licence or terms are stated (the author asks that his paper be cited); personal, "
                         "non-commercial use only."),
    Source("dsbi_braille", "DSBI: scanned pages of Chinese braille books (personal use)",
           "No licence stated (github.com/yeluo1994/DSBI)",
           "DSBI: Double-Sided Braille Image Dataset (Renqiang Li, Hong Liu, Xiangdong Wan and Yueliang Qiang, 2018, "
           "arXiv 1811.10893), https://github.com/yeluo1994/DSBI", "research", 114, 10, prepare_dsbi_braille,
           "about 140 MB", terms="https://github.com/yeluo1994/DSBI",
           terms_summary="No licence or terms are stated (the authors ask that their paper be cited); personal, "
                         "non-commercial use only."),
    Source("visible_disability", "Visible disability: photos with wheelchairs, walking sticks and walking frames "
                                 "(personal use)",
           "No licence or source of the photos stated (huggingface.co/datasets/zzh-2002/visible-disability)",
           "visible-disability (zzh-2002), https://huggingface.co/datasets/zzh-2002/visible-disability", "research",
           2000, 20, prepare_visible_disability, "up to 180 MB, read in parts",
           terms="https://huggingface.co/datasets/zzh-2002/visible-disability", terms_summary=NO_TERMS),
    Source("wheelchair_types", "Kinds of wheelchairs and mobility scooters: product photos (personal use)",
           "No licence stated (huggingface.co/datasets/samitesla/various_wheelchairs); the photos look like shop "
           "pictures", "various_wheelchairs (samitesla), https://huggingface.co/datasets/samitesla/various_wheelchairs",
           "research", 245, 10, prepare_wheelchair_types, "about 60 MB",
           terms="https://huggingface.co/datasets/samitesla/various_wheelchairs",
           terms_summary="No licence or terms are stated, and the photos look like manufacturers' and shops' "
                         "pictures; personal, non-commercial use only."),
    Source("wheelchair_detection", "Wheelchair detection photos (personal use)",
           "\"Apache-2.0\" stated by the uploader; who took the photos is not said "
           "(huggingface.co/datasets/Falah/wheel-chair-images-annotation4object-detec)",
           "Wheelchair dataset for object detection (Falah), "
           "https://huggingface.co/datasets/Falah/wheel-chair-images-annotation4object-detec", "research", 600, 15,
           prepare_wheelchair_detection, "25 MB, once",
           terms="https://huggingface.co/datasets/Falah/wheel-chair-images-annotation4object-detec",
           terms_summary=research("The uploader states Apache-2.0 but does not say who took the photos or where "
                                  "they came from, so the rights in them are unclear.")),
    Source("rotterdam_accessibility", "Rotterdam streets: accessible or not for wheelchairs, walkers and prams "
                                      "(personal use)",
           "\"Apache-2.0\" stated; most photos are from Google Street View, Google Images and Bing "
           "(huggingface.co/datasets/comarti15/accessibility-rotterdam-the-netherlands)",
           "Mobility and Accessibility in Rotterdam (Cora Martin, Yu Vos, Agne Piepaliute and Lucas Holef, Erasmus "
           "University Rotterdam, 2025), https://huggingface.co/datasets/comarti15/"
           "accessibility-rotterdam-the-netherlands", "research", 1500, 20, prepare_rotterdam_accessibility,
           "about 300 MB, read out of a 371 MB zip",
           terms="https://huggingface.co/datasets/comarti15/accessibility-rotterdam-the-netherlands",
           terms_summary=research("Apache-2.0 is stated, but most photos come from Google Street View, Google Images "
                                  "and Bing, whose own terms do not allow re-licensing.")),
    Source("accessparkcv", "AccessParkCV: disability parking spaces in aerial photos of car parks (personal use)",
           "\"MIT\" and \"CC BY 4.0\" stated (huggingface.co/datasets/makeabilitylab/disabilityparking and "
           "AccessParkCV_coco); the aerial photos come from city imagery whose own terms are not given",
           "AccessParkCV (Jared Hwang, Chu Li, Hanbyul Kang, Maryam Hosseini and Jon E. Froehlich, 'Where Can I "
           "Park?', ASSETS 2025), https://huggingface.co/datasets/makeabilitylab/AccessParkCV_coco", "research", 1500,
           20, prepare_accessparkcv, "about 90 MB",
           terms="https://huggingface.co/datasets/makeabilitylab/disabilityparking",
           terms_summary=research("The labels are MIT or CC BY 4.0, but the aerial photos of Seattle, Washington DC "
                                  "and Spring Hill come from city imagery whose own terms are not stated.")),
]

# The collections a picture-making model may learn from: pictures with no people (braille pages, car parks seen from
# above). Never people, children or medical.
DISABILITY_PICTURE_MAKING_OK = {"angelina_braille", "dsbi_braille", "accessparkcv"}
