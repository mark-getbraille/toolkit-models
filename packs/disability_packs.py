"""Pack builders for disability and assistive technology, used by build_packs.py in the same way as its own PACKS:
each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question",
"answer", "credit"}, plus "place" where the source gives one and "child": true where the picture may show a child (the
picture-making trainer leaves those rows out). A picture with more than one question comes once with its JPEG and
then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins), so the zip holds
each picture only once. The limit counts pictures.

Why: a describer for blind people should know white canes, guide dogs, braille, wheelchairs, walking aids,
prostheses, hearing aids, tactile paving, ramps, accessible toilets and the people who use them, and describe disabled
people plainly and respectfully: what they are doing and what they use, never with pity ("suffers from", "confined to
a wheelchair"). Answers here are fixed sentences written from each source's own labels and categories (nothing is
written by an AI model), and descriptions with pitying or outdated words are left out (NOT_RESPECTFUL).

The packs (all open: CC0, public domain or CC BY, checked at the source):
  open_images_disability  Google Open Images V7 (validation and test sets): photos where people checked by hand that a
                          wheelchair, powered wheelchair, mobility scooter, walking frame, crutch, walking stick or
                          wheelchair ramp is there, or a disability sport (wheelchair basketball, racing, tennis, rugby,
                          fencing, curling ...). Labels CC BY 4.0; each photo CC BY 2.0 (checked photo by photo), its
                          photographer named. "What assistive device is in this picture?", "What sport is this?" and
                          "Is there a wheelchair in this picture?" (no only where people checked and rejected it).
                          Open Images has no label for white canes, guide dogs, braille, prostheses or hearing aids
                          (the class list was searched), so those come from Commons below. Some photos may also be in
                          open_images_objects and open_images_street (asked other questions there).
  commons_disability      Wikimedia Commons categories: white canes, guide and assistance dogs, braille (texts, signs
                          by country, devices, people reading it), wheelchairs, powered wheelchairs, mobility scooters,
                          rollators, crutches, walking sticks, prostheses, hearing aids, cochlear implants, tactile
                          paving, accessible toilets and grab rails, wheelchair ramps and lifts, stair lifts, kneeling
                          buses and vehicles with ramps, disabled parking, accessibility signs and symbols, priority
                          seats and wheelchair spaces, screen readers and magnifiers, AAC, adaptive sports
                          (Paralympic sports, wheelchair basketball and rugby, goalball, blind football, the Warrior
                          Games, whose US Defense Department photos are public domain), and "Images from Disabled and
                          Here" (a disability-led stock collection, CC BY 4.0, with its own descriptions). Pictures
                          CC0, public domain or CC BY only (author credited; never BY-SA, NC or ND: those are the kit's
                          commons_disability_sa). The category's question, and the file's caption or description where
                          it is a real, respectful description.
  tapad_tactile_paving    TaPaD, Deteriorated Tactile Paving (Matsuda et al., Convivial Computing Laboratory, Okayama
                          University, Zenodo 23388177, CC BY 4.0): road-surface photos, mostly in Okayama, Japan, from a
                          bicycle camera (all 1,611 annotated) and from smartphones (the 1,200 annotated, through Repot,
                          CC BY 4.0), every tactile paving block boxed as guiding (lines) or warning (dots) with its
                          damage (cracked, dirty, faded, melting, worn out). "Is there tactile paving here?" and "What
                          condition is the tactile paving in?"

Share-alike, non-commercial and research collections on the same subject are kit download entries in
training-kit/kit/disability_sources.py (Commons BY-SA files, the Freiburg Mobility Aids hospital photos, braille page
photos and scans, and others), with the sign-up and left-out collections listed there.

    python packs/disability_packs.py tapad_tactile_paving --limit 8      (prints a few rows: a quick check)
"""

import csv
import json
import random
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, ALT_TEXT, NARRATE  # noqa: F401
from food_packs import (sentence, listed, with_twins, count_pictures, oi_lines, oi_licence_name,  # noqa: F401
                        commons_members, commons_entries, commons_place, OI_LABELS, OI_CLASSES, OI_IMAGES,
                        OI_PICTURE)
from expression_packs import mark_child, child_count, OI_CHILD, CHILD
from world_life_packs import remote_zip
from places import where, country_at

DEVICE_Q = "What assistive device is in this picture?"
SPORT_Q = "What sport is this?"

# Words that pity disabled people or are outdated or offensive; a description using them is not learnt from (the
# category's own question still is).
NOT_RESPECTFUL = re.compile(r"\b(suffer\w*|afflict\w*|victims?|wheelchair[- ]bound|confined to|cripple\w*|crippled|"
                            r"handicapped|invalids?|retard\w*|deaf[- ]and[- ]dumb|deaf[- ]mutes?|dumb|lame|"
                            r"spastics?|mongol\w*|midgets?|defective|abnormal|poor (man|woman|boy|girl)|"
                            r"brave(ly)?|inspir\w*|despite (his|her|their) disabilit\w*|beggars?)\b", re.I)
NUDE = re.compile(r"\b(nude|naked|nudity|topless|undress\w*|erotic|sex\w*|porn\w*|lingerie|underwear)\b", re.I)


# ----------------------------------------------------------------- Open Images V7 (Google)

# Assistive devices: label -> the words in the answer.
OI_AIDS = {
    "Motorized wheelchair": "a powered (electric) wheelchair", "Wheelchair": "a wheelchair",
    "Mobility scooter": "a mobility scooter", "Walker": "a walking frame (walker)", "Crutch": "a crutch",
    "Walking stick": "a walking stick", "Cane": "a walking stick (cane)", "Wheelchair ramp": "a wheelchair ramp",
}
# A general label left out when a more specific one is there.
OI_AIDS_COVERED = {"Wheelchair": {"Motorized wheelchair"}, "Cane": {"Walking stick"}}
# Disability sports, most specific first: label -> the answer to "What sport is this?".
OI_SPORTS = {
    "Wheelchair basketball": "This is wheelchair basketball: basketball played by athletes in sports wheelchairs.",
    "Wheelchair racing": "This is wheelchair racing: athletes race in light three-wheeled racing wheelchairs, "
                         "pushing the wheels with their hands.",
    "Wheelchair tennis": "This is wheelchair tennis: tennis played from sports wheelchairs; the ball may bounce "
                         "twice.",
    "Wheelchair rugby league": "This is wheelchair rugby league, played in sports wheelchairs.",
    "Wheelchair rugby": "This is wheelchair rugby: a full-contact team sport played in strong sports wheelchairs.",
    "Wheelchair fencing": "This is wheelchair fencing: the fencers' wheelchairs are fixed to the floor.",
    "Wheelchair curling": "This is wheelchair curling: curling played from wheelchairs, the stone pushed with a "
                          "long stick.",
    "Wheelchair football": "This is wheelchair football (powerchair football), played in powered wheelchairs.",
    "Wheelchair sports": "This is a wheelchair sport: athletes compete in sports wheelchairs.",
    "Disabled sports": "This is a disability sport (adaptive sport), adapted for disabled athletes.",
}
OI_ASK_WHEELCHAIR = "Is there a wheelchair in this picture?"
OI_CREDIT = "Photo by {author}{page}, {licence}; labels from Open Images V7 (Google), CC BY 4.0"


def oi_disability_rows(labels):
    """The rows for one photo from its {label: 1 (verified present), 0 (verified absent) or None}: [] when no
    assistive device or disability sport is verified present."""
    present = {n for n, c in labels.items() if c == 1}
    absent = {n for n, c in labels.items() if c == 0}
    rows = []
    aids = [OI_AIDS[n] for n in OI_AIDS if n in present and not (OI_AIDS_COVERED.get(n, set()) & present)]
    aids = list(dict.fromkeys(aids))
    if aids:
        rows.append({"question": DEVICE_Q, "answer": sentence(f"there is {listed(aids)}")})
    sport = next((n for n in OI_SPORTS if n in present), None)
    if sport:
        rows.append({"question": SPORT_Q, "answer": OI_SPORTS[sport]})
    if not rows:
        return []
    if present & {"Wheelchair", "Motorized wheelchair"} or sport and sport.startswith("Wheelchair"):
        rows.append({"question": OI_ASK_WHEELCHAIR, "answer": "Yes, there is a wheelchair."})
    elif "Wheelchair" in absent and "Motorized wheelchair" not in present:
        rows.append({"question": OI_ASK_WHEELCHAIR, "answer": "No, I can't see a wheelchair in this picture."})
    return rows


def build_open_images_disability(limit):
    """The Open Images disability pack's pictures: [(name, JPEG or None, row)]. Reads the labels people checked on
    the validation and test sets (about 120 MB of lists) and the photo lists (60 MB), keeps photos with a device or
    disability-sport label verified present whose own licence is free and that need no turning, and fetches them,
    the rarer labels first so that walking frames and scooters are not crowded out by wheelchairs."""
    s = session()
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = set(OI_AIDS) | set(OI_SPORTS) | set(OI_CHILD)
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
    keep = {k for k, v in labels.items() if any(v.get(n) == 1 for n in list(OI_AIDS) + list(OI_SPORTS))}
    say(f"Open Images: {len(keep)} pictures with an assistive device or disability sport verified")
    photos = {}
    for url in OI_IMAGES:
        for r in csv.DictReader(oi_lines(s, url)):
            licence = oi_licence_name(r.get("License") or "")
            if r["ImageID"] in keep and licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[r["ImageID"]] = (r["Subset"], licence, clean(r.get("Author")) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
    by_label = {}
    for image_id in sorted(keep & set(photos)):
        rows = oi_disability_rows(labels[image_id])
        if not rows:
            continue
        subset, licence, author, page = photos[image_id]
        credit = OI_CREDIT.format(author=author, page=f" ({page})" if page else "", licence=licence)
        child = any(labels[image_id].get(n) == 1 for n in OI_CHILD)
        rows = [dict(r, credit=credit, **({"child": True} if child else {})) for r in rows]
        main = next(n for n in list(OI_AIDS) + list(OI_SPORTS) if labels[image_id].get(n) == 1)
        by_label.setdefault(main, []).append((f"oi-dis-{image_id}.jpg", OI_PICTURE.format(subset=subset,
                                                                                          image_id=image_id), rows))
    for label, items in sorted(by_label.items(), key=lambda kv: len(kv[1])):
        say(f"  {label}: {len(items)} pictures")
    # Take the labels in turn (the rarest first), so every kind of device and sport is there.
    queues = [items for _, items in sorted(by_label.items(), key=lambda kv: len(kv[1]))]
    for i, q in enumerate(queues):
        random.Random(70 + i).shuffle(q)
    chosen, want = [], int(limit * 1.1) + 2
    while len(chosen) < want and any(queues):
        for q in queues:
            if q and len(chosen) < want:
                chosen.append(q.pop())
    fetched = fetch_all(chosen, workers=8)
    random.Random(71).shuffle(fetched)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Wikimedia Commons categories

BRAILLE = ("This is braille: writing made of raised dots, in cells of up to six dots, that blind people read with "
           "their fingertips.")
TACTILE = ("Yes: there is tactile paving, ground with raised bumps that blind and partially sighted people can feel "
           "with their feet or a cane.")
ACCESSIBLE_TOILET = ("It is an accessible toilet, made for wheelchair users and other disabled people, with room to "
                     "move and support rails.")
# Each category: (question, answer, whether one level of its subcategories is used too). The same question for a
# picture of a device alone and of a person using it, so the answer is right for both. Answers about places and
# signs say what the thing is for.
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
    "Wheelchair basketball": (SPORT_Q, OI_SPORTS["Wheelchair basketball"], False),
    "Wheelchair rugby": (SPORT_Q, OI_SPORTS["Wheelchair rugby"], False),
    "Wheelchair racing": (SPORT_Q, OI_SPORTS["Wheelchair racing"], False),
    "Wheelchair tennis": (SPORT_Q, OI_SPORTS["Wheelchair tennis"], False),
    "Goalball": (SPORT_Q, "This is goalball: a team sport for blind and partially sighted athletes, who wear "
                          "blacked-out eyeshades and roll a ball with bells inside towards the other team's goal.",
                 False),
    "Blind football": (SPORT_Q, "This is blind football: five-a-side football for blind and partially sighted "
                                "players, with a ball that rattles.", False),
    "Paralympic sports": (SPORT_Q, "This is a Paralympic sport, played by disabled athletes.", True),
    "Sports at the Warrior Games": ("What event is this?", "This is the Warrior Games, adaptive sports for wounded, "
                                                           "ill and injured service members and veterans.", True),
    "Images from Disabled and Here": (None, None, False),     # their own descriptions only (commons_rows)
}
# Subcategories (and file names) that are not photos of the thing: drawings, emoji, art, logos, videos, maps ...;
# and subcategories about people by name or organisations, where the category's answer may not fit.
COMMONS_NOT_IT = re.compile(r"\b(art|drawings?|illustrations?|paintings?|logos?|icons?|emoji|U\+[0-9A-F]+|svg|"
                            r"sculptures?|statues?|videos?|audio|recordings?|maps?|diagrams?|stamps?|coins?|"
                            r"advertis\w*|posters?|cartoons?|comics?|in literature|organi[sz]ations?|"
                            r"associated|manufacturers?|companies|shops?|museums?|collections?|x-rays?|radiograph\w*|"
                            r"scans?|surgery|operations?|veterinary|dogs? wheelchairs|nude|naked|logo|"
                            r"history|historical|charts?|penile|breasts?|heart|valves?|spine|dental|dentures?|prosthodontics|"
                            r"epithes\w*|voice|nose|ocular|eyes?|implants?|licen[cs]e plates?|parent|watches|"
                            r"cosplay\w*|SVG|ramps? signs)\b", re.I)


def commons_rows(category, question, answer, title, text, credit, child=False):
    """The rows for one Commons file: the category's question, and its caption or description when it is a real,
    respectful description that names no nudity; [] when the file's words are not suitable. The Disabled And Here
    pictures get only their own description ("Describe this picture.")."""
    if NUDE.search(f"{title} {text}"):
        return []
    rows = []
    if question:
        rows.append({"question": question, "answer": answer, "credit": credit})
    if text and not NOT_RESPECTFUL.search(text):
        rows.append({"question": NARRATE if question is None else ALT_TEXT, "answer": text, "credit": credit})
    return [dict(mark_child(r, title, text), **({"child": True} if child else {}), **commons_place(title))
            for r in rows]


def build_commons_disability(limit):
    """The Commons disability pack's pictures: [(name, JPEG or None, row)]. For each category: its files (and those
    of its subcategories where COMMONS_DISABILITY says so, leaving out drawings, emoji, art and organisations), the
    free ones (CC0, public domain, CC BY), each with the category's question and, when it has one, its description.
    The categories share the limit, so no single category fills the pack; a file is used once, under the first
    category it is met in."""
    s, items, seen = session(), [], set()
    per_category = max(6, limit // len(COMMONS_DISABILITY) * 2)
    for category, (question, answer, deeper) in COMMONS_DISABILITY.items():
        titles = commons_members(s, category, "file")
        young = set()                                 # files of a subcategory about children ("Children in ...")
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                sub = sub.split(":", 1)[-1]
                if not COMMONS_NOT_IT.search(sub):
                    files = commons_members(s, sub, "file")
                    titles += files
                    if CHILD.search(sub):
                        young.update(files)
        titles = [t for t in dict.fromkeys(titles) if t not in seen and not COMMONS_NOT_IT.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_entries(s, titles[:per_category * 3]):
            rows = commons_rows(category, question, answer, title, text, credit, child=title in young)
            if not rows:
                continue
            seen.add(title)
            name = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
            items.append((f"commons-dis-{name}.jpg", url, rows))
            found += 1
            if found >= per_category:
                break
        say(f"Commons {category}: {found} free pictures ({len(titles)} files)")
    random.Random(72).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- TaPaD: tactile paving (Okayama University)

TAPAD = "https://zenodo.org/records/23388177/files/{}?download=1"
TAPAD_PARTS = (("bicycle.zip", "bicycle"), ("smartphone.zip", "smartphone"))
TAPAD_CREDIT = ("TaPaD: Deteriorated Tactile Paving dataset (Yuto Matsuda et al., Convivial Computing Laboratory, "
                "Okayama University), Zenodo 23388177, CC BY 4.0")
TAPAD_REPOT = "; photo from Repot Archive by repot contributors, CC BY 4.0 (https://repot-archive.cocolab.jp)"
TAPAD_DAMAGE = {
    "cracked": "cracked", "dirty": "dirty", "faded": "faded (its colour is hard to see)",
    "melting": "deformed (melted out of shape)", "worn-out": "worn down (the raised parts are worn away)",
}
TAPAD_KINDS = {"guiding": "guiding blocks (raised lines that show which way to walk)",
               "warning": "warning blocks (raised dots that warn of a hazard ahead, such as a crossing or steps)"}


def tapad_side(box, width):
    """ "on the left", "in the middle" or "on the right" for a box [x, y, w, h] in a picture width pixels wide."""
    middle = (box[0] + box[2] / 2) / max(1, width)
    return "on the left" if middle < 0.36 else "on the right" if middle > 0.64 else "in the middle"


def tapad_rows(entry):
    """The questions and answers for one TaPaD picture from its JSON annotation; [] when no block is marked."""
    blocks = entry.get("annotations") or []
    width = (entry.get("image") or {}).get("width") or 1280
    if not blocks:
        return []
    kinds = {}
    for b in blocks:
        kinds.setdefault((b.get("attributes") or {}).get("block_type"), []).append(b)
    parts = []
    for kind in ("guiding", "warning"):
        if kinds.get(kind):
            sides = sorted({tapad_side(b["bbox"], width) for b in kinds[kind]},
                           key=["on the left", "in the middle", "on the right"].index)
            parts.append(f"{TAPAD_KINDS[kind]}, {listed(sides)}")
    if not parts:
        return []
    rows = [{"question": "Is there tactile paving here?",
             "answer": f"Yes: there is tactile paving here, with {' and '.join(parts)}."}]
    damage = {}
    for b in blocks:
        for d in (b.get("attributes") or {}).get("deteriorations") or []:
            if d in TAPAD_DAMAGE:
                damage[d] = damage.get(d, 0) + 1
    if not damage:
        rows.append({"question": "What condition is the tactile paving in?",
                     "answer": "It looks in good condition: no cracks, dirt, fading or wear can be seen."})
    else:
        share = sum(1 for b in blocks if (b.get("attributes") or {}).get("deteriorations"))
        some = "All the blocks" if share == len(blocks) else "Most blocks" if share * 2 > len(blocks) else \
            "Some blocks"
        words = [TAPAD_DAMAGE[d] for d in sorted(damage, key=lambda d: -damage[d])]
        hard = " Worn or damaged blocks are harder to feel with the feet or a cane." \
            if {"worn-out", "cracked", "melting"} & set(damage) else \
            " Faded or dirty blocks are harder for partially sighted people to see." if \
            {"faded", "dirty"} & set(damage) else ""
        rows.append({"question": "What condition is the tactile paving in?",
                     "answer": f"{some} are {listed(words)}.{hard}"})
    return rows


def build_tapad_tactile_paving(limit):
    """The TaPaD pack's pictures: [(name, JPEG or None, row)]. Reads the two zips piece by piece (the bicycle zip is
    59 MB; of the 3.5 GB smartphone zip only the annotated photos used are read), each annotation JSON giving the
    blocks, and the place from the photo's GPS where it has one (turned into a country offline)."""
    s, out = session(), []
    for zip_name, part in TAPAD_PARTS:
        z = remote_zip(TAPAD.format(zip_name), s)
        names = set(z.namelist())
        notes = sorted(n for n in names if n.startswith(f"{part}/annotations/") and n.endswith(".json"))
        random.Random(f"tapad-{part}").shuffle(notes)
        want = (limit + 1) // 2 if part == "bicycle" else limit - len(out)
        taken = 0
        for note in notes:
            if taken >= want:
                break
            entry = json.loads(z.read(note))
            picture = f"{part}/images/{(entry.get('image') or {}).get('filename', '')}"
            rows = tapad_rows(entry)
            if not rows or picture not in names:
                continue
            data = smaller(z.read(picture))
            if not data:
                continue
            gps = (entry.get("image") or {}).get("gps") or {}
            place = where(country_at(gps.get("lat"), gps.get("lon"))) if gps.get("lat") else {}
            credit = TAPAD_CREDIT + (TAPAD_REPOT if part == "smartphone" else "")
            stem = picture.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            out.append((f"tapad-{part}-{re.sub(r'[^\w.-]+', '_', stem)}.jpg", data,
                        [dict(r, credit=credit, **place) for r in rows]))
            taken += 1
        say(f"TaPaD {part}: {taken} pictures ({len(notes)} annotated)")
    random.Random(73).shuffle(out)
    return with_twins(out[:limit])


# ----------------------------------------------------------------- the packs

DISABILITY_PACKS = {
    "open_images_disability": (build_open_images_disability,
                               "Open Images V7 (Google): image-level labels verified by people, CC BY 4.0, "
                               "https://storage.googleapis.com/openimages/web/index.html. Each photo is CC BY 2.0 "
                               "(checked photo by photo), credited below with its photographer and Flickr page."),
    "commons_disability": (build_commons_disability,
                           "Wikimedia Commons disability and accessibility categories: captions CC0; pictures CC0, "
                           "public domain (including US Department of Defense photos of the Warrior Games) or CC BY "
                           "(including Disabled And Here, https://affecttheverb.com/disabledandhere, CC BY 4.0), each "
                           "with its author and file page below. https://commons.wikimedia.org"),
    "tapad_tactile_paving": (build_tapad_tactile_paving,
                             "TaPaD: Deteriorated Tactile Paving dataset, Copyright (C) Convivial Computing "
                             "Laboratory, Okayama University, CC BY 4.0: https://zenodo.org/records/23388177. The "
                             "smartphone photos are from Repot Archive by repot contributors, CC BY 4.0 "
                             "(https://repot-archive.cocolab.jp). Answers written from the dataset's block and damage "
                             "labels."),
}

# How many pictures a full build takes from each collection (about what each offers after the licence and label
# checks).
DISABILITY_LIMITS = {
    "open_images_disability": 2500,    # of about 2,000 to 3,000 usable photos with a device or sport label
    "commons_disability": 1500,        # the free files of about 60 small categories
    "tapad_tactile_paving": 2811,      # 1,611 bicycle and 1,200 annotated smartphone photos
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one disability pack builder.")
    parser.add_argument("key", choices=sorted(DISABILITY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = DISABILITY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
