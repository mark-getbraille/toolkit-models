"""Pack builders for facial expressions, gestures and body language, used by build_packs.py in the same way as its own
PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}. A picture that has more than one question comes once with its JPEG and then again as
(None, None, row) rows whose "file" names the same picture (food_packs.with_twins), so the zip holds each picture only
once. The limit counts pictures (for vqa_expressions, which holds no pictures, it counts rows).

Why: a blind person often wants to know how the people in a photo look: smiling, crying, waving, hugging, arms
crossed. The answers here first say what can be SEEN (the mouth, the eyes, the eyebrows, the hands, the posture, how
people hold each other) and only then give a careful reading ("they look happy", "they seem worried"), never a
certainty about what someone feels. Every answer is written from the collection's own labels or captions by the
plain templates below; no answer is written by an AI model.

Rows whose picture probably shows a child carry "child": true (the picture-making trainer leaves those out; the
describer learns from every row): a verified Open Images label Child, Boy, Girl, Baby, Toddler and the like, or a
caption, description, category, question or COCO caption that mentions a child (CHILD below).

The packs (EXPRESSION_PACKS):
  oi_expressions      Google Open Images V7: labels people checked by hand (Confidence 1 = seen, 0 = checked and not
                      there) for expressions (Smile, Laugh, Crying, Frown, Yawn, Wink ...), gestures (Waving, V sign,
                      Clap, Salute ...), people together (Hug, Handshake, High five ...) and postures (Sitting,
                      Standing, Dance ...). Labels CC BY 4.0; each photo's own licence is checked (CC BY 2.0) and its
                      photographer credited. Validation and test sets first, then, for a full build, the training set
                      (2.7 GB of labels and 2.7 GB of photo list, read as they download, never stored).
  commons_expressions Wikimedia Commons categories of expressions, gestures, people together and body language
                      (People smiling, Crying, Frowning, Yawning people, Hugging, Handshakes, Hand waving, Thumbs up,
                      People pointing, Shrugging, Facepalms, Crossed arms, Signing ...): pictures CC0, public domain or
                      CC BY (author credited; never BY-SA, NC or ND). The category's question and, where the file has a
                      real English caption or description, "Write a short description ...". Sexual, nude and kissing
                      material, sign alphabets, animals, icons and Nazi or Roman salutes are left out.
  bice_gestures       BiCE-HG (University of Sheffield, CC BY 4.0): 23 adult volunteers, who gave written informed
                      consent, filmed their own hand gestures with a head-mounted camera (thumbs-up, OK sign, V sign,
                      pointing, wave, fist, open palm, pinch, framing). Its one representative still per recording, only
                      the gestures a still picture can show. "What gesture is this hand making?"
  vqa_expressions     Questions people asked about COCO photos that concern expressions, feelings and gestures ("Is the
                      man smiling?", "How does the woman feel?"): VQA v2 val2014 (CC BY 4.0, the answer at least three of
                      ten people gave) and Visual Dialog 1.0 train (CC BY 4.0). Only photos whose own licence is CC BY
                      2.0 or no known copyright (build_packs.COCO_FREE); rows only, the kit fetches the photos from COCO.
                      Answers about feelings are turned into careful readings ("Yes, the man looks happy.").

Sources looked at and left out are listed in REJECTED (with the reason), for the report and the next person.

    python packs/expression_packs.py oi_expressions --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import random
import re
import sys
import zipfile

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, fetch_all, say, ALT_TEXT, COCO_FREE
from food_packs import (sentence, listed, with_twins, count_pictures, oi_lines, oi_licence_name,  # noqa: F401
                        commons_get, commons_members, commons_entries, OI_CLASSES, OI_LABELS, OI_IMAGES,
                        OI_PICTURE)
from everyday_packs import RemoteZip, fetch_from_zip

FACE_Q = "What is this person's facial expression?"
OI_FACE_Q = "What is the expression on this person's face?"
OI_FACES_Q = "What expressions can you see on the faces in this picture?"
GESTURE_Q = "What gesture is the person making?"
TOGETHER_Q = "What are the people in this picture doing with each other?"
BODY_Q = "Describe the body language in this picture."
DOING_Q = "What is this person doing?"


# ----------------------------------------------------------------- children (the "child" field)

# Words that mean or may mean a child, in English and in the languages Commons captions and descriptions most often
# use. Wide on purpose: a row that mentions any of them is marked, even when the word is used about an adult.
CHILD = re.compile(
    r"\b(child\w*|kids?|kiddo\w*|boys?|girls?|bab(y|ies)|infan\w*|toddler\w*|newborn\w*|teen\w*|youngster\w*|"
    r"juvenile\w*|adolescen\w*|minors?|sons?|daughters?|pupils?|schoolchild\w*|schoolboys?|schoolgirls?|"
    r"schoolkids?|preschool\w*|kindergarten\w*|nursery|students? of (a |the )?(primary|elementary)|"
    r"enfants?|fill(e|es|ette|ettes)|gar[cç]ons?|b[ée]b[ée]s?|ni[nñ][oa]s?|chic[oa]s?|beb[eê]s?|crian[cç]as?|"
    r"menin[oa]s?|bambin[oi]|bambin[ae]|ragazz[oaie]|kind|kinder|kindje\w*|m[aä]dchen|jungen?|jongens?|meisjes?|"
    r"dzieci|dziecko|дет\w*|ребён\w*|мальчик\w*|девочк\w*)\b|子供|子ども|こども|児童|少年|少女|儿童|孩子|男孩|女孩",
    re.I)
# Open Images labels that show a child (checked against the class list when the builder runs).
OI_CHILD = ("Child", "Boy", "Girl", "Baby", "Toddler", "Infant", "Kid", "Teenager", "Schoolchild", "Newborn")


def mark_child(row, *texts):
    """The row with "child": True when any of texts mentions a child (else the row unchanged)."""
    if any(CHILD.search(t or "") for t in texts):
        return dict(row, child=True)
    return row


def child_count(entries):
    """How many rows of a pack are marked "child"."""
    return sum(1 for _, _, row in entries if row.get("child"))


# ----------------------------------------------------------------- Open Images V7

OI = "https://storage.googleapis.com/openimages/"
OI_TRAIN_LABELS = OI + "v7/oidv7-train-annotations-human-imagelabels.csv"             # 2.7 GB, sorted by picture
OI_TRAIN_IMAGES = OI + "v6/oidv6-train-images-with-labels-with-rotation.csv"          # 2.7 GB, not sorted
OI_CREDIT = "Photo by {author}{page}, {licence}; labels from Open Images V7 (Google), CC BY 4.0"

# Face labels: (what can be seen, a careful reading or None, +1 / -1 / 0 for a pleasant / unpleasant / neutral look).
# "Thumb" is not used: the label is the body part (photos of hands), not a thumbs-up.
OI_FACE_SEEN = {
    "Laugh": ("laughing, with the mouth open", "they seem to be enjoying themselves", 1),
    "Smile": ("smiling, the corners of the mouth turned up", "they look happy", 1),
    "Crying": ("crying", "they seem upset", -1),
    "Tears": ("with tears on the face", None, 0),
    "Frown": ("frowning, with the eyebrows drawn together", "they may be unhappy or concentrating", -1),
    "Yawn": ("yawning, the mouth stretched wide open", "they seem tired", 0),
    "Wink": ("winking, with one eye closed", "it looks playful", 1),
    "Smirk": ("smirking, with a lopsided half-smile", "they look amused", 1),
    "Shout": ("shouting, with the mouth wide open", None, 0),
    "Tongue": ("showing the tongue", None, 0),
}
# Labels that are only a reading of the face (people judged how the person looks), with the careful words used.
OI_FACE_READ = {
    "Fearful": ("they look frightened", -1), "Angry": ("they look angry", -1), "Sad": ("they look sad", -1),
    "Pain": ("they seem to be in pain", -1), "Worried": ("they look worried", -1),
    "Anxious": ("they look anxious", -1), "Bored": ("they look bored", -1),
    "Surprised": ("they look surprised", 0), "Thinking": ("they seem to be deep in thought", 0),
    "Happy": ("they look happy", 1), "Fun": ("they seem to be having fun", 1), "Calm": ("they look calm", 0),
}
# Gestures: the whole answer, and the short words used in "Describe the body language ...".
OI_GESTURES = {
    "Waving": ("The person is waving, with a hand raised.", "waving"),
    "V sign": ("The person is making a V sign (a peace sign), with two fingers raised in a V.", "making a V sign"),
    "Salute": ("The person is saluting, with a hand raised to the forehead.", "saluting"),
    "Clap": ("The person is clapping their hands.", "clapping"),
    "Applause": ("People are clapping their hands (applauding).", "clapping"),
    "Shrug": ("The person is shrugging, with the shoulders raised.", "shrugging"),
    "Bowing": ("The person is bowing, bending forward from the waist.", "bowing"),
    "Sign language": ("The person is signing in sign language, using the hands.", "signing"),
    "Fist": ("The person is making a fist.", "making a fist"),
    "Selfie": ("The person is holding up a phone or camera to take a selfie.", "taking a selfie"),
    "Cheering": ("The person is cheering.", "cheering"),
}
# People together: the answer, and the short words.
OI_TOGETHER = {
    "Hug": ("They are hugging, with their arms around each other.", "hugging"),
    "Handshake": ("Two people are shaking hands.", "shaking hands"),
    "High five": ("They are giving each other a high five, their raised hands meeting.", "giving a high five"),
    "Cheek kissing": ("One person is kissing another on the cheek.", "kissing someone on the cheek"),
    "Tickling": ("One person is tickling another.", "tickling someone"),
    "Argument": ("They seem to be arguing.", "arguing"),
    "Conversation": ("They are talking with each other.", "talking"),
}
# Postures (one is used: on a photo of several people two postures may belong to different people).
OI_POSTURES = {"Kneeling": "kneeling", "Squat": "squatting", "Sitting": "sitting", "Standing": "standing",
               "Running": "running", "Jumping": "jumping", "Dance": "dancing", "Walking": "walking",
               "Sleep": "sleeping", "Nap": "sleeping", "Yoga": "doing yoga", "Stretching": "stretching"}
# Short words for the face in "Describe the body language ...".
OI_FACE_SHORT = {"Laugh": "laughing", "Smile": "smiling", "Crying": "crying", "Frown": "frowning", "Yawn": "yawning",
                 "Wink": "winking", "Smirk": "smirking", "Shout": "shouting"}
# "Is anyone in this picture ...?": the label and the word.
OI_ASK_ANYONE = {"Smile": "smiling", "Laugh": "laughing", "Crying": "crying", "Waving": "waving", "Hug": "hugging",
                 "Dance": "dancing", "Yawn": "yawning", "Handshake": "shaking hands", "Sitting": "sitting down"}
OI_PEOPLE = {"Person", "Man", "Woman", "Girl", "Boy", "Child", "Baby", "Toddler", "Human face", "People"}
OI_GROUP = {"People", "Crowd", "Team", "Family", "Audience", "Friendship"}
# Pictures that are not photos of real people: a face label there may be on a drawing, a statue or a doll.
OI_NOT_REAL = {"Cartoon", "Illustration", "Drawing", "Animation", "Painting", "Sculpture", "Statue", "Doll", "Toy",
               "Mask", "Art", "Fictional character", "Mannequin", "Comics", "Clip art"}
OI_WANTED = set(OI_FACE_SEEN) | set(OI_FACE_READ) | set(OI_GESTURES) | set(OI_TOGETHER) | set(OI_POSTURES)
# The labels that make a picture worth taking (a posture alone, or "Fun" or "Calm" alone, is not enough).
OI_STRONG = set(OI_FACE_SEEN) | (set(OI_FACE_READ) - {"Fun", "Calm"}) | set(OI_GESTURES) | set(OI_TOGETHER)


def oi_face(present, group):
    """(answer, reading) for the face labels, or ("", "") when there are none. Readings that disagree (one pleasant,
    one unpleasant) are both left out: only what can be seen is said."""
    seen = [n for n in OI_FACE_SEEN if n in present]
    if "Laugh" in seen and "Smile" in seen:
        seen.remove("Smile")                                     # laughing says it
    if "Crying" in seen and "Tears" in seen:
        seen.remove("Tears")
        words = ["crying, with tears on the face"] + [OI_FACE_SEEN[n][0] for n in seen if n != "Crying"]
    else:
        words = [OI_FACE_SEEN[n][0] for n in seen]
    readings = [(OI_FACE_READ[n][0], OI_FACE_READ[n][1]) for n in OI_FACE_READ if n in present]
    readings += [(OI_FACE_SEEN[n][1], OI_FACE_SEEN[n][2]) for n in seen if OI_FACE_SEEN[n][1]]
    moods = {m for _, m in readings}
    reading = readings[0][0] if readings and not (1 in moods and -1 in moods) else ""
    subject = "Someone in this picture" if group else "The person"
    if words:
        return f"{subject} is {listed(words)}" + (f"; {reading}." if reading else "."), reading
    if reading:
        who = "someone in this picture" if group else "the person"
        return sentence(reading.replace("they ", f"{who} ", 1).replace(f"{who} look ", f"{who} looks ")
                        .replace(f"{who} seem ", f"{who} seems ")), reading
    return "", ""


def oi_expression_rows(labels, rng):
    """The rows for one picture from its {label: 1 (seen) or 0 (checked and not there)}: [] when it is not a photo of
    a real person with an expression, gesture or people-together label."""
    present = {n for n, c in labels.items() if c == 1}
    absent = {n for n, c in labels.items() if c == 0}
    if not (present & OI_PEOPLE) or present & OI_NOT_REAL or not (present & OI_STRONG):
        return []
    group = bool(present & OI_GROUP)
    rows = []
    face, reading = oi_face(present, group)
    if face:
        rows.append({"question": OI_FACES_Q if group else OI_FACE_Q, "answer": face})
    gestures = [n for n in OI_GESTURES if n in present]
    if gestures:
        answer = OI_GESTURES[gestures[0]][0]
        rows.append({"question": GESTURE_Q, "answer": answer.replace("The person", "Someone", 1) if group else answer})
    together = [n for n in OI_TOGETHER if n in present]
    if together:
        answer = OI_TOGETHER[together[0]][0]
        if "Smile" in present or "Laugh" in present:
            answer = answer[:-1] + ", and smiling."
        rows.append({"question": TOGETHER_Q, "answer": answer})
    # Is anyone ... ? One yes (smiling first) and one no, from labels people checked.
    yes = [n for n in OI_ASK_ANYONE if n in present]
    if "Laugh" in present and "Smile" not in present:
        present_smile = True                                     # someone laughing is smiling too
        yes = ["Smile"] + yes
    else:
        present_smile = "Smile" in present
    if yes:
        word = OI_ASK_ANYONE[yes[0]]
        rows.append({"question": f"Is anyone in this picture {word}?", "answer": f"Yes, someone is {word}."})
    no = sorted(n for n in absent if n in OI_ASK_ANYONE and n not in present
                and not (n == "Smile" and present_smile) and not (n == "Laugh" and "Smile" in present))
    if "Smile" in no and rng.random() < 0.6:
        no = ["Smile"]
    if no:
        word = OI_ASK_ANYONE[rng.choice(no)]
        rows.append({"question": f"Is anyone in this picture {word}?",
                     "answer": f"No, I can't see anyone {word} in this picture."})
    # Body language: a posture and an expression, gesture or people-together label.
    postures = [n for n in OI_POSTURES if n in present]
    actions = [OI_GESTURES[n][1] for n in gestures[:1]] + [OI_TOGETHER[n][1] for n in together[:1]]
    actions += [OI_FACE_SHORT[n] for n in OI_FACE_SHORT if n in present][:1]
    if "Laugh" in present and "smiling" in actions:
        actions.remove("smiling")
    if postures and actions:
        subject = "Someone in this picture is" if group else "The person is"
        text = f"{subject} {listed([OI_POSTURES[postures[0]]] + actions)}."
        if reading:
            text += " " + sentence(reading)
        rows.append({"question": BODY_Q, "answer": text})
    return rows


def oi_read_labels(s, url, names, keep, max_bytes=None):
    """Read a human-verified labels file as it downloads into keep: {picture: {label: 1, 0 or None (people
    disagreed)}}, only for the labels in names ({MID: label}) and only pictures with at least one wanted label seen.
    The file is sorted by picture, so one picture's labels are gathered and then kept or dropped. max_bytes stops early
    (for a quick test)."""
    current, labels, read = None, {}, 0

    def flush():
        """Keep the picture just read when it has a wanted label seen."""
        if current and any(c == 1 and n in OI_WANTED for n, c in labels.items()):
            merged = keep.setdefault(current, {})
            for n, c in labels.items():
                merged[n] = c if merged.get(n, c) == c else None

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


def oi_read_photos(s, url, wanted, photos, max_bytes=None):
    """Add to photos {picture: (subset, licence, author, page)} the pictures in wanted whose own licence is free and
    that need no turning, from a photo list read as it downloads."""
    read = 0
    with s.get(url, timeout=600, stream=True) as r:
        r.raise_for_status()
        lines = r.iter_lines(decode_unicode=True)
        header = next(csv.reader([next(lines)]))
        for line in lines:
            read += len(line) + 1
            if max_bytes and read > max_bytes:
                break
            if line[:16] not in wanted:
                continue
            row = dict(zip(header, next(csv.reader([line]))))
            licence = oi_licence_name(row.get("License") or "")
            if licence and (row.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[row["ImageID"]] = (row["Subset"], licence, clean(row.get("Author")) or "an unnamed photographer",
                                          row.get("OriginalLandingURL") or "")
    return photos


def oi_items(labels, photos, rng, counts):
    """[(name, address, rows)] for the pictures with rows; counts gathers {label: [seen, not there]}, for the log."""
    items = []
    for image_id in sorted(labels):
        if image_id not in photos:
            continue
        picture = labels[image_id]
        rows = oi_expression_rows(picture, rng)
        if not rows:
            continue
        for n, c in picture.items():
            if c in (0, 1):
                counts.setdefault(n, [0, 0])[1 - c] += 1
        subset, licence, author, page = photos[image_id]
        credit = OI_CREDIT.format(author=author, page=f" ({page})" if page else "", licence=licence)
        child = any(picture.get(n) == 1 for n in OI_CHILD)
        rows = [dict(r, credit=credit, **({"child": True} if child else {})) for r in rows]
        rarest = min((n for n, c in picture.items() if c == 1 and n in OI_STRONG), key=lambda n: counts[n][0])
        items.append((f"oi-expr-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id), rows, rarest))
    return items


def spread(items, rng):
    """Items in turns over their main label (round robin), so rare expressions get in before Smile fills the pack."""
    groups = {}
    for item in items:
        groups.setdefault(item[3], []).append(item[:3])
    for g in groups.values():
        rng.shuffle(g)
    out = []
    while any(groups.values()):
        for key in sorted(groups):
            if groups[key]:
                out.append(groups[key].pop())
    return out


def build_oi_expressions(limit, train=None, train_bytes=None):
    """The Open Images expressions pack's pictures. Reads the labels people checked on the validation and test sets
    (about 120 MB, read as they download); when they give fewer pictures than limit (a full build), also the training
    set (train=True forces it, False never; train_bytes reads only the first bytes of each training file, for a
    test). Keeps photos of real people whose own licence is free and that need no turning, spreads them over the
    labels and fetches them."""
    s, rng = session(), random.Random(61)
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = OI_WANTED | OI_PEOPLE | OI_GROUP | OI_NOT_REAL | set(OI_CHILD)
    names = {mids[n]: n for n in wanted if n in mids}
    say(f"Open Images: {len(names)} of {len(wanted)} labels found in the class list "
        f"(missing: {', '.join(sorted(n for n in wanted if n not in mids)) or 'none'})")
    labels = {}
    for url in OI_LABELS:
        oi_read_labels(s, url, names, labels)
    photos = {}
    for url in OI_IMAGES:
        oi_read_photos(s, url, set(labels), photos)
    counts = {}
    items = oi_items(labels, photos, rng, counts)
    say(f"Open Images validation and test: {len(items)} usable photos")
    if train or (train is None and len(items) < limit * 1.1):
        more = {}
        oi_read_labels(s, OI_TRAIN_LABELS, names, more, train_bytes)
        say(f"Open Images training set: {len(more)} pictures with a wanted label seen")
        train_photos = oi_read_photos(s, OI_TRAIN_IMAGES, set(more), {}, train_bytes)
        items += oi_items(more, train_photos, rng, counts)
        say(f"Open Images with the training set: {len(items)} usable photos")
    for n in sorted(counts):
        if n in OI_WANTED or n in OI_CHILD:
            say(f"  {n}: seen on {counts[n][0]}, checked and not there on {counts[n][1]} usable photos")
    chosen = spread(items, rng)[:int(limit * 1.1) + 2]
    return with_twins(fetch_all(chosen, workers=8)[:limit])



# ----------------------------------------------------------------- Wikimedia Commons

# Each category with its question and answer (None: only the caption is used, for broad categories). The categories
# are named one by one (no automatic subcategories): Commons subcategories of gestures and body language include
# erotic and profane gestures, kissing, nude people, sign alphabets and Nazi salutes, which are not wanted here.
COMMONS_EXPRESSIONS = {
    "People smiling": (FACE_Q, "The person is smiling."),
    "Smiling": (FACE_Q, "The person is smiling."),
    "People laughing": (FACE_Q, "The person is laughing."),
    "Laughing": (FACE_Q, "The person is laughing."),
    "People crying": (FACE_Q, "The person is crying."),
    "Crying": (FACE_Q, "The person is crying."),
    "Tears of joy": (FACE_Q, "The person has tears in their eyes; they seem to be crying with joy."),
    "Frowning": (FACE_Q, "The person is frowning, with the eyebrows drawn together."),
    "Surprise": (FACE_Q, "The person looks surprised."),
    "Shocked": (FACE_Q, "The person looks shocked."),
    "Yawning people": (FACE_Q, "The person is yawning."),
    "Anger": (FACE_Q, "The person looks angry."),
    "Disgust": (FACE_Q, "The person looks disgusted."),
    "Shouting": (FACE_Q, "The person is shouting."),
    "Screaming": (FACE_Q, "The person is screaming, with the mouth wide open."),
    "Smirking": (FACE_Q, "The person is smirking, with a lopsided half-smile."),
    "Rolling eyes": (FACE_Q, "The person is rolling their eyes."),
    "Wide open eyes": (FACE_Q, "The person's eyes are wide open."),
    "Closed eyes": (FACE_Q, "The person's eyes are closed."),
    "Sticking out the tongue": (FACE_Q, "The person is sticking out their tongue."),
    "Facial expressions": (None, None),
    "Thumbs up": (GESTURE_Q, "The person is giving a thumbs-up."),
    "People with thumbs up": (GESTURE_Q, "The person is giving a thumbs-up."),
    "Hands with thumb up": (GESTURE_Q, "The hand is giving a thumbs-up."),
    "Both thumbs up": (GESTURE_Q, "The person is giving two thumbs up, one with each hand."),
    "V-sign": (GESTURE_Q, "The person is making a V sign (a peace sign), with two fingers raised in a V."),
    "OK gesture": (GESTURE_Q, "The person is making the OK sign: the thumb and index finger touch in a circle."),
    "Hand waving": (GESTURE_Q, "The person is waving."),
    "Female people waving hands": (GESTURE_Q, "The woman is waving."),
    "Male people waving hands": (GESTURE_Q, "The man is waving."),
    "Both hands waving": (GESTURE_Q, "The person is waving with both hands."),
    "Goodbye waves": (GESTURE_Q, "The person is waving goodbye."),
    "Children waving hands": (GESTURE_Q, "The child is waving."),
    "People pointing": (GESTURE_Q, "The person is pointing."),
    "Pointing towards viewer": (GESTURE_Q, "The person is pointing straight at the viewer."),
    "Pointing up": (GESTURE_Q, "The person is pointing upwards."),
    "Pointing down": (GESTURE_Q, "The person is pointing downwards."),
    "Shrugging": (GESTURE_Q, "The person is shrugging."),
    "Facepalms": (GESTURE_Q, "The person is doing a facepalm, with a hand over the face."),
    "Clapping": (GESTURE_Q, "The person is clapping."),
    "People clapping": (GESTURE_Q, "The person is clapping."),
    "People saluting": (GESTURE_Q, "The person is saluting."),
    "Scratching head": (GESTURE_Q, "The person is scratching their head."),
    "Bicep flexing": (GESTURE_Q, "The person is flexing their arm muscles."),
    "Raised fists": (GESTURE_Q, "The person is raising a fist."),
    "Gestures": (None, None),
    "Hugging": (TOGETHER_Q, "They are hugging."),
    "People hugging": (TOGETHER_Q, "They are hugging."),
    "Group hugging": (TOGETHER_Q, "A group of people are hugging."),
    "Handshakes": (TOGETHER_Q, "Two people are shaking hands."),
    "People shaking hands": (TOGETHER_Q, "Two people are shaking hands."),
    "Close-up photographs of handshakes": (TOGETHER_Q, "Two people are shaking hands; only their hands are shown."),
    "High fives": (TOGETHER_Q, "They are giving each other a high five."),
    "Fist bumps": (TOGETHER_Q, "They are bumping fists."),
    "Elbow bumps": (TOGETHER_Q, "They are bumping elbows, a greeting used instead of a handshake."),
    "Holding hands": (TOGETHER_Q, "They are holding hands."),
    "Arm around shoulder": (TOGETHER_Q, "One person has an arm around another's shoulders."),
    "Crossed arms": (BODY_Q, "The person has their arms crossed (folded across the chest)."),
    "Men with crossed arms": (BODY_Q, "The man has his arms crossed (folded across the chest)."),
    "Women with crossed arms": (BODY_Q, "The woman has her arms crossed (folded across the chest)."),
    "People standing with crossed arms": (BODY_Q, "The person is standing with their arms crossed."),
    "Sitting with arms folded across chest": (BODY_Q, "The person is sitting with their arms folded across the "
                                                      "chest."),
    "Hands on hips": (BODY_Q, "The person is standing with their hands on their hips."),
    "Victory pose": (BODY_Q, "The person is standing in a victory pose, with their arms raised."),
    "Body language": (None, None),
    "Body language in humans": (None, None),
    "Signing": (DOING_Q, "The person is using sign language."),
    "Sign language interpreters": (DOING_Q, "The person is a sign language interpreter, signing."),
    "Tactile signing": (DOING_Q, "Two people are using tactile sign language, communicating by touch with their "
                                 "hands."),
}
# Left out: sexual or nude material, kissing, and anything a caption says is so.
COMMONS_SEXUAL = re.compile(r"\b(nud\w*|naked|nudity|sex\w*|erot\w*|porn\w*|lingerie|topless|bottomless|underwear|"
                            r"bikini\w*|strip\w*|fetish\w*|bdsm|bondage|nsfw|breasts?|genital\w*|kiss\w*|sensual\w*|"
                            r"seduct\w*|playboy|pin-?ups?|orgasm\w*|lewd|obscen\w*|middle finger)\b", re.I)
# Not a person's expression or gesture: drawings of signs, icons, animals, sign alphabets, Nazi and Roman salutes.
COMMONS_NOT_PEOPLE = re.compile(r"\b(icons?|emoji\w*|emoticons?|smilies|smiley|logos?|symbols?|clip ?art|stickers?|"
                                r"diagrams?|charts?|maps?|alphabets?|fingerspell\w*|handshapes?|letters? [a-z]\b|"
                                r"signwriting|dogs?|cats?|monkeys?|apes?|chimpanzees?|gorillas?|horses?|animals?|"
                                r"birds?|bears?|macaques?|baboons?|nazi\w*|hitler|sieg|fascis\w*|roman salute|"
                                r"mascots?|cartoons?|comics?|ai-generated|stamps?)\b", re.I)


def commons_safe(*texts):
    """True when none of texts suggests sexual material or something that is not a person's expression."""
    joined = " ".join(t or "" for t in texts)
    return not COMMONS_SEXUAL.search(joined) and not COMMONS_NOT_PEOPLE.search(joined)


def build_commons_expressions(limit):
    """The Commons expressions pack's pictures: for each category in COMMONS_EXPRESSIONS, its free pictures (CC0,
    public domain or CC BY), each with the category's question and, when the file has a real English caption or
    description, "Write a short description ...". The categories share the limit. Commons often answers this machine
    with 429 (slow down): food_packs.commons_get waits as asked and tries again."""
    s, items, seen = session(), [], set()
    per_category = max(6, limit * 2 // len(COMMONS_EXPRESSIONS))
    for category, (question, answer) in COMMONS_EXPRESSIONS.items():
        try:
            titles = [t for t in commons_members(s, category, "file") if t not in seen]
        except RuntimeError as e:                                # Commons kept refusing: the next category
            say(f"Commons {category}: left out ({e})")
            continue
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_entries(s, [t for t in titles if commons_safe(t)][:per_category * 3]):
            if title in seen or not commons_safe(title, text):
                continue
            seen.add(title)
            rows = []
            if question:
                rows.append({"question": question, "answer": answer, "credit": credit})
            if text:
                rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
            if not rows:
                continue
            rows = [mark_child(r, title, text, category) for r in rows]
            name = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
            items.append((f"commons-expr-{name}.jpg", url, rows))
            found += 1
            if found >= per_category:
                break
        say(f"Commons {category}: {found} free pictures ({len(titles)} files)")
    random.Random(62).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- BiCE-HG (University of Sheffield)

BICE_ARTICLE = "https://api.figshare.com/v2/articles/32374137"
BICE_CREDIT = ("BiCE-HG (Awfa Dakheel and Charith Abhayaratne, The University of Sheffield, 2026), CC BY 4.0, "
               "https://doi.org/10.15131/shef.data.32374137.v2")
# The gestures a still picture can show, with the answer (what the hand looks like). Swipes, circles, zooms, wrist
# turns and air taps are movements: a single frame of them does not show the gesture, so they are left out.
BICE_GESTURES = {
    "thumbs_up": "A thumbs-up: the hand is closed with the thumb pointing up.",
    "ok_sign": "The OK sign: the thumb and index finger touch to make a circle, and the other fingers are raised.",
    "v_sign": "A V sign (a peace sign): the index and middle fingers are raised and spread in a V.",
    "open_palm": "An open hand, held up with the fingers spread.",
    "fist_front": "A closed fist.",
    "fist_back": "A closed fist.",
    "point": "Pointing: the index finger is stretched out and the other fingers are curled.",
    "wave": "A wave: the open hand is raised, as if waving hello.",
    "pinch": "A pinch: the thumb and index finger are pressed together.",
    "hand_frame_left_up": "A framing gesture: both hands make the corners of a rectangle, like a picture frame.",
    "hand_frame_right_up": "A framing gesture: both hands make the corners of a rectangle, like a picture frame.",
}
BICE_ASK = "What gesture is this hand making?"


def build_bice_gestures(limit):
    """The BiCE-HG pack's pictures: the dataset's one representative still per recording ("static_frames") of the
    gestures in BICE_GESTURES, read from its 20 GB zip on figshare by range requests (the zip is never downloaded
    whole). The licence is checked first."""
    s = session()
    article = s.get(BICE_ARTICLE, timeout=60).json()
    licence = (article.get("license") or {}).get("name", "")
    if licence != "CC BY 4.0":
        raise SystemExit(f"BiCE-HG: licence is now {licence!r}, not CC BY 4.0; check it before building.")
    url = next(f["download_url"] for f in article["files"] if f["name"].lower().endswith(".zip"))
    zipped, items = RemoteZip(url), []
    for name, offset, csize, method in zipped.entries():
        m = re.search(r"/(\d+)/(full|low)_lighting/(sitting|standing|walking)/static_frames/(\w+?)_static\.jpg$", name)
        if not m or m.group(4) not in BICE_GESTURES:
            continue
        person, light, scene, gesture = m.groups()
        answer = BICE_GESTURES[gesture] + " The picture is taken from the person's own point of view" + \
            (", in dim light." if light == "low" else ".")
        items.append((f"bice-{person}-{light}-{scene}-{gesture}.jpg", (offset, csize, method),
                      {"question": BICE_ASK, "answer": answer, "credit": BICE_CREDIT}))
    say(f"BiCE-HG: {len(items)} stills of {len(BICE_GESTURES)} gestures")
    random.Random(63).shuffle(items)
    return fetch_from_zip(zipped, items[:int(limit * 1.02) + 2])[:limit]


# ----------------------------------------------------------------- VQA v2 and Visual Dialog on COCO photos

VQA_URL = "https://s3.amazonaws.com/cvmlp/vqa/mscoco/vqa/"
VISDIAL = ("jxu124/visdial", "data/train-00000-of-00001-0b41821101e89ea5.parquet")
VQA_CREDIT = "VQAv2 (Goyal et al., 2017), CC BY 4.0; photo from COCO, {licence}"
VISDIAL_CREDIT = "Visual Dialog 1.0 (Das et al., 2017), CC BY 4.0; photo from COCO, {licence}"
COCO_LICENCE_NAMES = {4: "CC BY 2.0", 7: "no known copyright restrictions"}
# Questions about expressions, feelings, gestures and people together.
ABOUT_EXPRESSION = re.compile(
    r"\b(smil\w*|grin\w*|laugh\w*|cry\w*|tears?|frown\w*|yawn\w*|wink\w*|happy|happily|sad|unhappy|angry|mad|upset|"
    r"scared|afraid|frightened|surprised|shocked|excited|bored|tired|sleepy|worried|nervous|calm|relaxed|annoyed|"
    r"confused|serious|content|pleased|joyful|cheerful|emotions?|mood|feel|feels|feeling|facial expression|"
    r"expression|enjoying (him|her|them)sel\w+|having fun|wav(e|es|ing)|thumbs? up|peace sign|hug\w*|"
    r"shak\w* hands|handshake|pointing|clapp\w*|shrug\w*|salut\w*|pos(e|es|ing) for|scream\w*|yell\w*|shout\w*|"
    r"arms crossed|crossed arms|folded arms)\b", re.I)
# A question must be about people (not an animal, a bed that "feels soft" or the weather).
ABOUT_PEOPLE = re.compile(r"\b(man|men|woman|women|person|people|persons|boy|boys|girl|girls|child|children|kid|kids|"
                          r"baby|babies|lady|ladies|guy|guys|gentleman|player|players|he|she|they|anyone|anybody|"
                          r"someone|somebody|everyone|everybody|couple|bride|groom|skier|surfer|skateboarder|chef|"
                          r"cook|batter|catcher|pitcher|rider|biker|crowd|family|friends?|teens?|teenagers?|toddler|"
                          r"his|her|their)\b", re.I)
ABOUT_ANIMAL = re.compile(r"\b(dog|dogs|cat|cats|horse|horses|cow|cows|sheep|bear|bears|giraffe|giraffes|elephant|"
                          r"elephants|zebra|zebras|bird|birds|animal|animals|puppy|kitten|teddy|doll|statue|"
                          r"mannequin|toy)\b", re.I)
FEELINGS = {"happy", "sad", "unhappy", "angry", "mad", "upset", "scared", "afraid", "frightened", "surprised",
            "shocked", "excited", "bored", "tired", "sleepy", "worried", "nervous", "calm", "relaxed", "annoyed",
            "confused", "serious", "content", "pleased", "joyful", "cheerful", "amused", "focused", "concentrating",
            "determined", "proud", "embarrassed", "sick", "cold", "hot", "busy", "comfortable", "uncomfortable",
            "playful", "silly", "lonely", "peaceful", "friendly", "curious", "interested", "thoughtful", "excitement"}
FEELING_NOUNS = {"happiness": "happy", "joy": "joyful", "sadness": "sad", "anger": "angry", "fear": "frightened",
                 "surprise": "surprised", "boredom": "bored", "excitement": "excited", "contentment": "content",
                 "concentration": "focused", "confusion": "confused", "calmness": "calm", "pride": "proud"}
ACTIONS = ("smiling", "laughing", "crying", "frowning", "waving", "hugging", "yawning", "grinning", "pointing",
           "clapping", "posing", "shouting", "screaming", "winking", "saluting", "shrugging", "cheering")
# Words between the subject and the feeling ("Does the man look happy?").
LINKS = {"look", "looks", "looking", "seem", "seems", "appear", "appears", "feel", "feels", "feeling", "being"}
HOW_FEEL = re.compile(r"^how (?:does|do|is|are) (.+?) (?:feel|feeling|look|looking)\?$|"
                      r"^what (?:is|are) (.+?)(?:'s|s'| his| her| their) (?:mood|emotion|facial expression|"
                      r"expression)\?$|^what (?:mood|emotion) (?:is|are|does|do) (.+?) (?:in|showing|show|have|"
                      r"feel|feeling|displaying|express\w*)\?$", re.I)
PLURAL = re.compile(r"(?i)\b(people|men|women|children|kids|they|them|players|boys|girls|both|ladies|guys|"
                    r"persons|couple|everyone)\b")


def as_question(text):
    """A question with a capital letter and a question mark ("is the man smiling" -> "Is the man smiling?")."""
    text = clean(text).rstrip(" ?.")
    return text[:1].upper() + text[1:] + "?" if text else ""


def subject_text(subject):
    """The subject of a question as it starts an answer sentence ("the man" stays; "anyone" -> "someone")."""
    low = subject.lower()
    return {"anyone": "someone", "anybody": "someone", "you": "I"}.get(low, subject)


def careful_answer(question, answer):
    """The answer people gave, as a careful sentence: yes or no to a feeling becomes "Yes, the man looks happy."; a
    feeling chosen ("Is she happy or sad?" "happy") or named ("How does the woman feel?") becomes "The woman looks
    happy."; yes or no to a visible action becomes "Yes, the man is smiling." Anything else is the answer as a
    sentence."""
    words = question.rstrip(" ?").split()
    low = answer.lower().rstrip(".")
    adj = FEELING_NOUNS.get(low, low)
    verb = words[0].lower() if words else ""
    at = next((i for i, w in enumerate(words[1:], 1) if w.lower() in FEELINGS or w.lower() in ACTIONS), None)
    if verb in ("is", "are", "does", "do") and at and at > 1:
        subject = words[1:at]
        while subject and subject[-1].lower() in LINKS:
            subject.pop()
        if subject and len(subject) <= 6:
            who = subject_text(" ".join(subject))
            plural = verb in ("are", "do") or bool(PLURAL.search(who))
            word, rest = words[at].lower(), " ".join(words[at + 1:])
            rest = f" {rest}" if rest else ""
            either = re.search(r"(?i)\bor\b", question)
            if low in ("yes", "no") and not either:
                if word in FEELINGS:
                    look = "look" if plural else "looks"
                    if low == "yes":
                        return f"Yes, {who} {look} {word}{rest}."
                    if who == "someone":
                        return f"No, no one looks {word}{rest}."
                    return f"No, {who} {'do' if plural else 'does'}n't look {word}{rest}."
                if verb in ("is", "are"):
                    be = "are" if plural else "is"
                    if low == "yes":
                        return f"Yes, {who} {be} {word}{rest}."
                    if who == "someone":
                        return f"No, no one is {word}{rest}."
                    return f"No, {who} {be}n't {word}{rest}."
            if either and adj in FEELINGS:
                return sentence(f"{who} {'look' if plural else 'looks'} {adj}")
            if either and adj in ACTIONS:
                return sentence(f"{who} {'are' if plural else 'is'} {adj}")
    m = HOW_FEEL.match(question.rstrip())
    if m and 1 <= len(low.split()) <= 2:
        who = subject_text(next(g for g in m.groups() if g))
        plural = verb in ("are", "do") or bool(PLURAL.search(who))
        if adj in ACTIONS:
            return sentence(f"{who} {'are' if plural else 'is'} {adj}")
        if adj in FEELINGS:
            return sentence(f"{who} {'look' if plural else 'looks'} {adj}")
    return sentence(answer)


def agreed(answers, at_least=3):
    """The answer at least at_least of the people gave (VQA counts an answer right when three gave it), or ""."""
    counts = {}
    for a in answers or []:
        a = clean(a).lower()
        if a:
            counts[a] = counts.get(a, 0) + 1
    if not counts:
        return ""
    best = max(counts, key=counts.get)
    return best if counts[best] >= at_least and best not in ("unanswerable", "unsuitable") else ""


def coco_photos():
    """{COCO image id: (photo address, licence name, all five captions joined)} for photos under CC BY 2.0 or no known
    copyright (the phiyodr copy of COCO 2017 on Hugging Face, 30 MB, which gives each photo's licence and captions)."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download
    free = {}
    for name in HfApi().list_repo_files("phiyodr/coco2017", repo_type="dataset"):
        if name.endswith(".parquet"):
            table = pq.read_table(hf_hub_download("phiyodr/coco2017", name, repo_type="dataset"),
                                  columns=["license", "image_id", "coco_url", "captions"]).to_pylist()
            free.update({r["image_id"]: (r["coco_url"], COCO_LICENCE_NAMES[r["license"]], " ".join(r["captions"] or []))
                         for r in table if r["license"] in COCO_FREE})
    return free


def expression_question(question):
    """True for a question about a person's expression, feeling or gesture (not about an animal)."""
    return bool(ABOUT_EXPRESSION.search(question) and ABOUT_PEOPLE.search(question)
                and not ABOUT_ANIMAL.search(question))


ONE_PERSON = re.compile(r"\b(a|an|one) (man|woman|person|boy|girl|lady|guy|child|kid|baby|player|skier|surfer|"
                        r"skateboarder|tennis player|chef|bride|groom)\b", re.I)
SEVERAL = re.compile(r"\b(men|women|people|boys|girls|children|kids|players|two|three|four|group|couple|family|"
                     r"crowd|and a)\b", re.I)


def build_vqa_expressions(limit, most_each=3):
    """The VQA expressions pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]. VQA v2
    val2014 questions about expressions with an answer at least three of ten people gave, and Visual Dialog train
    questions about expressions (only "he", "she" or "they" questions where the dialogue's caption names one person,
    so the question is clear alone); at most most_each rows a photo."""
    s, free = session(), coco_photos()
    say(f"COCO: {len(free)} photos under CC BY 2.0 or no known copyright")
    per_photo = {}

    def add(image_id, question, answer, credit):
        """Keep one row for a photo."""
        url, licence, captions = free[image_id]
        row = {"url": url, "question": question, "answer": answer, "credit": credit.format(licence=licence)}
        per_photo.setdefault(image_id, []).append(mark_child(row, question, answer, captions))

    found = {"VQA v2": 0, "Visual Dialog": 0}
    with zipfile.ZipFile(io.BytesIO(s.get(VQA_URL + "v2_Questions_Val_mscoco.zip", timeout=300).content)) as z:
        questions = {q["question_id"]: q for q in json.load(z.open(z.namelist()[0]))["questions"]
                     if q["image_id"] in free and expression_question(q["question"])}
    with zipfile.ZipFile(io.BytesIO(s.get(VQA_URL + "v2_Annotations_Val_mscoco.zip", timeout=300).content)) as z:
        for a in json.load(z.open(z.namelist()[0]))["annotations"]:
            q = questions.get(a["question_id"])
            answer = agreed([x["answer"] for x in a["answers"]]) if q else ""
            if answer:
                question = as_question(q["question"])
                add(q["image_id"], question, careful_answer(question, answer), VQA_CREDIT)
                found["VQA v2"] += 1
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    table = pq.read_table(hf_hub_download(VISDIAL[0], VISDIAL[1], repo_type="dataset"),
                          columns=["caption", "dialog", "global_image_id"]).to_pylist()
    for r in table:
        image_id = int(str(r["global_image_id"]).rsplit(".", 1)[-1])
        if image_id not in free:
            continue
        caption = clean(r.get("caption"))
        one = bool(ONE_PERSON.search(caption)) and not SEVERAL.search(caption)
        for question, answer in r.get("dialog") or []:
            question, answer = clean(question), clean(answer)
            if len(question.split()) < 3 or not answer or not expression_question(question):
                continue
            if re.search(r"(?i)\b(he|she|him|her|his|they|them|their|it)\b", question) and not one:
                continue                                         # whom "he" means is not clear alone
            if re.fullmatch(r"(?i)(can'?t|cannot) (tell|see)( that)?|not sure|unsure|i don'?t know|"
                            r"(i )?(can'?t|cannot) tell.*", answer):
                continue
            question = as_question(question)
            add(image_id, question, careful_answer(question, answer), VISDIAL_CREDIT)
            found["Visual Dialog"] += 1
    say(f"Expression questions: {found['VQA v2']} from VQA v2 val, {found['Visual Dialog']} from Visual Dialog, on "
        f"{len(per_photo)} photos")
    photos = sorted(per_photo)
    rng = random.Random(64)
    rng.shuffle(photos)
    rows = []
    for photo in photos:
        mine = per_photo[photo][:]
        rng.shuffle(mine)
        rows += mine[:most_each]
        if len(rows) >= limit:
            break
    return [(None, None, r) for r in rows[:limit]]


# ----------------------------------------------------------------- sources looked at and left out

# Every one of these fails the licence rules (CC0, public domain, CC BY, ODC-By, CDLA-Permissive, MIT, Apache or
# BSD only). "Free download" says whether it can be fetched without signing up or asking (for a personal-use option).
REJECTED = {
    "FER2013": "Kaggle competition set (research use; faces found by Google image search, owners never asked). Kaggle "
               "account needed; copies on Hugging Face (e.g. Jeneral/fer-2013 'Apache-2.0') are re-uploads under a "
               "licence the makers never gave.",
    "AffectNet": "research only, non-commercial; request form and agreement needed.",
    "RAF-DB": "research only, non-commercial; request by e-mail with an agreement.",
    "ExpW (Expression in-the-Wild)": "research only (faces from web search); free download from the authors' Google "
                                     "Drive, no sign-up.",
    "EMOTIC": "research only, non-commercial; request form. EMOTIF (Zenodo 24064844, 'CC BY 4.0') is cut from "
              "EMOTIC's pictures, so the same terms apply.",
    "BoLD (Body Language Dataset)": "research only, non-commercial (clips of films); request form and agreement.",
    "KDEF (Karolinska)": "non-commercial research only; free download from kdef.se after accepting the terms on the "
                         "page (no account).",
    "CK+ (Extended Cohn-Kanade)": "non-commercial research only; request with a signed agreement. Zenodo copies "
                                  "(19683234, 18983820) are re-uploads under a licence the makers never gave.",
    "Jester (20BN / Qualcomm)": "licensed for non-commercial academic use only; Qualcomm account needed.",
    "HaGRID and HaGRIDv2": "CC BY-SA 4.0 (share-alike); free download from GitHub links, no sign-up.",
    "JAFFE": "non-commercial research only, no redistribution; Zenodo 14974867 asks for a request.",
    "RAVDESS": "CC BY-NC-SA 4.0; free download from Zenodo 1188976, no sign-up.",
    "NVGesture, EgoGesture, IPN Hand": "NVGesture CC BY-NC-SA; EgoGesture by request; IPN Hand research terms.",
    "WLASL, MS-ASL, How2Sign": "research terms or CC BY-NC (videos taken from the web); How2Sign free download.",
    "IFEED (Zenodo 7971730)": "'CC BY 4.0', but the pictures are frames of the TV series Friends (owned by Warner "
                              "Bros.), so the uploaders cannot give that licence.",
    "Navarasa dance expressions (Zenodo 12094235)": "CC BY 4.0, but frames taken from performance videos of about 30 "
                                                    "dancers with no word of their consent or of who filmed them; "
                                                    "many crops under 100 pixels.",
    "Hand Gestures Dataset, ASL Hello/Bye/... (figshare 24449197)": "CC BY 4.0, but every picture has a hand skeleton "
                                                                    "drawn over it by tracking software (the "
                                                                    "describer would learn to describe the overlay).",
    "VIRI and NVIE (figshare 28236605)": "re-uploads of sign-up research sets under 'CC BY 4.0'.",
    "Hugging Face gesture and expression uploads (Teen-Different/Facial-Expression, LibreYOLO/hand-gestures-jps7z, "
    "and others)": "MIT or CC BY labels on re-uploads whose pictures come from FER2013, Roboflow Universe or web "
                   "searches with no stated source: the licence cannot be traced to the people photographed.",
    "Open Images 'Thumb' label": "not a thumbs-up: it marks the body part (photos of hands); not used.",
    "Open Images 'Kiss', 'Romance', 'Love' labels": "left out on purpose (the answers stay non-sexual).",
}


# ----------------------------------------------------------------- the packs

EXPRESSION_PACKS = {
    "oi_expressions": (build_oi_expressions, "Open Images V7 (Google): image-level labels verified by people, CC BY "
                                             "4.0, https://storage.googleapis.com/openimages/web/index.html. Each "
                                             "photo is CC BY 2.0 (checked photo by photo), credited below with its "
                                             "photographer and Flickr page. Answers written from the labels by fixed "
                                             "templates."),
    "commons_expressions": (build_commons_expressions, "Wikimedia Commons expression, gesture and body-language "
                                                       "categories: captions CC0; pictures CC0, public domain or CC "
                                                       "BY, each with its author and file page below. "
                                                       "https://commons.wikimedia.org"),
    "bice_gestures": (build_bice_gestures, "BiCE-HG: A bi-conditional egocentric hand gesture dataset under controlled "
                                           "environmental conditions (Awfa Dakheel and Charith Abhayaratne, The "
                                           "University of Sheffield, 2026), CC BY 4.0, "
                                           "https://doi.org/10.15131/shef.data.32374137.v2. All participants gave "
                                           "written informed consent (ethics approval 067003). Stills resized."),
    "vqa_expressions": (build_vqa_expressions, "Questions about expressions and feelings from VQAv2 (Goyal et al., "
                                               "2017), CC BY 4.0, https://visualqa.org, and Visual Dialog 1.0 (Das et "
                                               "al., 2017), CC BY 4.0, https://visualdialog.org. Photos are not in "
                                               "this pack: the kit fetches them from https://cocodataset.org (only "
                                               "photos under CC BY 2.0 or no known copyright)."),
}

# How many pictures a full build takes from each collection (vqa_expressions: rows). About what each offers after the
# licence checks; see the module docstring.
EXPRESSION_LIMITS = {
    "oi_expressions": 12000,          # about 1,500 usable in validation and test, many thousands more in training
    "commons_expressions": 1500,      # 70 categories, at most about 40 free pictures each
    "bice_gestures": 1350,            # the stills of the 11 still gestures (of 2,482 stills)
    "vqa_expressions": 6000,          # expression questions on free COCO photos, at most 3 a photo
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one expression pack builder.")
    parser.add_argument("key", choices=sorted(EXPRESSION_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = EXPRESSION_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
