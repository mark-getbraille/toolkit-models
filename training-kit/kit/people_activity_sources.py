"""People in daily activities, for the Picture Model Training Kit: the collections about what people are doing
(eating, washing dishes, riding a bicycle, carrying water, selling in the street, praying) that cannot be open
ready-made packs because of their licence: share-alike, non-commercial, or research use (pictures gathered from the
web, or no terms stated). The open ones (V-COCO and Visual Genome on CC BY COCO photos, Open Images activity labels,
Commons CC0, public domain and CC BY daily-life categories, and the Dollar Street daily routines) are packs in
packs/people_activity_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. The two
COCO entries are ready-made packs of text and web addresses only (V-COCO and Visual Genome rows, built like the open
packs on GitHub's machines); their photos are fetched from COCO by the kit, and are used only with the choice their
own licence allows. Every licence was checked at its source in November 2026.

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with them
                   is CC BY-SA.
  "noncommercial"  CC BY-NC (and BY-NC-SA, BY-NC-ND, BY-ND) and other non-commercial terms: personal use only
                   (--personal-noncommercial).
  "research"       pictures gathered from the web, or no terms for the pictures: personal use only
                   (--personal-research with --accept-research-terms).

Answers are fixed sentences from each source's own labels (a Commons category's name, a dataset's action class and
the box of the person doing it, the verb and the nouns people chose for each role of a situation), never written by
an AI model. Nobody is named. Positions are said only from a dataset's own boxes, as places in the picture.

Safety (packs/SOURCE-RULES.md): no sexual content; verbs, classes and files about bathing, swimming, undressing,
kissing, fighting, arrests, violence or medical care are left out; children only in everyday clothed scenes, and every
row whose words name a child is marked "child". No collection here is used for picture-making
(PEOPLE_ACTIVITY_PICTURE_MAKING_OK is empty): they are all about people.

The collections (PEOPLE_ACTIVITY_SOURCES):
  share-alike
    commons_daily_life_sa  Wikimedia Commons categories of people doing everyday things and at work (the same
                           categories as the open commons_daily_life pack, and its "Street vendors in" countries with
                           the country as the place): files under CC BY-SA or GFDL, with the category's question and
                           the file's own caption. "What is the person doing?" -> "They are drinking tea."
    coco_actions_sa        V-COCO and Visual Genome rows on COCO photos under CC BY-SA 2.0 (ready-made pack of rows;
                           the photos are fetched from COCO). "What is the person doing?" -> "The person is reading a
                           book."
  noncommercial
    coco_actions_nc        The same rows on COCO photos under CC BY-NC, BY-NC-SA, BY-NC-ND or BY-ND 2.0 (about three
                           quarters of COCO; 16,000 rows).
  research
    stanford40_actions     Stanford 40 Actions (Yao, Jiang, Khosla, Lin, Guibas and Fei-Fei, Stanford, 2011): 9,532
                           web photos of people doing 40 actions (brushing teeth, cleaning the floor, cooking, cutting
                           vegetables, washing dishes, fixing a bike, gardening, phoning, reading, pushing a cart,
                           walking a dog, writing on a board ...), with the box of the person doing it. No licence is
                           stated; the photos were gathered from Google, Bing and Flickr. "What is the person doing?"
                           -> "The person on the left of the picture is washing dishes."
    swig_situations        SWiG, Situations With Groundings (Pratt, Yatskar, Weihs, Farhadi and Kembhavi, Allen
                           Institute for AI, 2020; built on imSitu, Yatskar, Zettlemoyer and Farhadi, 2016): 126,000
                           web photos, each of one of 504 verbs with the noun people chose for each role (who, what,
                           with what, where): "What is happening in this picture?" -> "A woman is kneading dough in a
                           kitchen." Only verbs done by people, and not the left-out ones above. Its 13.6 GB zip is
                           read piece by piece; only the chosen photos are fetched.
    har_actions            Human Action Recognition (HAR) Dataset (DPhi data sprint 76, copy Bingsu/
                           Human_Action_Recognition on Hugging Face, marked ODbL): 12,600 web photos of 15 activities
                           (calling, clapping, cycling, dancing, drinking, eating, hugging, laughing, listening to
                           music, running, sitting, sleeping, texting, using a laptop; fighting is left out). "What is
                           the person doing?" -> "They are texting on a phone."

Needing sign-up or a download by hand (PEOPLE_ACTIVITY_SIGN_UP has the links), and looked at and not included
(PEOPLE_ACTIVITY_NOT_INCLUDED, with the reason of each).

    python kit/people_activity_sources.py stanford40_actions --cap 8     (a quick check; prints a few rows)
"""

import json
import os
import random
import re

import sources
from extra_sources import research, say
from home_sources import commons_sa_items
from more_sources import fetch_shared
from personal_sources import remote_zip, zip_members
from sources import Source, clean, hf_parquet_files, hf_parquet_rows

DOING_Q = "What is the person doing?"
PEOPLE_Q = "What are the people doing?"
HAPPENING_Q = "What is happening in this picture?"
# Words that name a child: such a row gets "child": true (never used to make pictures).
CHILD = re.compile(r"\b(child\w*|kids?|boys?|girls?|bab(y|ies)|toddlers?|infants?|newborns?|teen\w*|youngsters?|"
                   r"schoolchild\w*|schoolboys?|schoolgirls?|pupils?|sons?|daughters?|juveniles?|minors?)\b", re.I)


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


def a_or_an(phrase):
    """ "a" or "an" before a phrase, by its first letter."""
    return "an" if phrase[:1].lower() in "aeiou" else "a"


def marked(row, *texts):
    """The row with "child": True when any of texts names a child."""
    return dict(row, child=True) if any(CHILD.search(t or "") for t in texts) else row


# ----------------------------------------------------------------- share-alike: Commons daily life

# (category, question, answer, look in subcategories too): the same categories as packs/people_activity_packs.py
# COMMONS_DAILY_LIFE (bathing, swimming and beach categories are not used there either).
COMMONS_DAILY_SA = [
    ("People eating", DOING_Q, "They are eating.", True), ("People drinking", DOING_Q, "They are drinking.", True),
    ("People drinking tea", DOING_Q, "They are drinking tea.", False),
    ("People drinking coffee", DOING_Q, "They are drinking coffee.", False),
    ("Sleeping people", DOING_Q, "They are sleeping.", True), ("People resting", DOING_Q, "They are resting.", False),
    ("People reading", DOING_Q, "They are reading.", True), ("People writing", DOING_Q, "They are writing.", True),
    ("People cleaning", DOING_Q, "They are cleaning.", True),
    ("Laundry", HAPPENING_Q, "They are doing the laundry (washing or drying clothes).", False),
    ("Sewing", HAPPENING_Q, "Someone is sewing.", False), ("Knitting", HAPPENING_Q, "Someone is knitting.", False),
    ("Hand weaving", HAPPENING_Q, "Someone is weaving by hand.", True),
    ("Spinning (textiles)", HAPPENING_Q, "Someone is spinning thread or yarn.", False),
    ("Pounding grain", DOING_Q, "They are pounding grain.", True),
    ("Hand washing", HAPPENING_Q, "Someone is washing their hands.", False),
    ("Shaving", HAPPENING_Q, "Someone is shaving.", False),
    ("Watching television", DOING_Q, "They are watching television.", True),
    ("People taking selfies", DOING_Q, "They are taking a selfie (a photo of themselves) with a phone.", True),
    ("People in conversation", PEOPLE_Q, "They are talking with each other.", False),
    ("People sitting on benches", DOING_Q, "They are sitting on a bench.", True),
    ("People waiting", DOING_Q, "They are waiting.", True),
    ("Queues", PEOPLE_Q, "People are standing in a queue (a line), waiting their turn.", False),
    ("Shopping", HAPPENING_Q, "Someone is shopping.", False), ("People shopping", DOING_Q, "They are shopping.", True),
    ("People on trains", DOING_Q, "They are travelling on a train.", False),
    ("Commuters", DOING_Q, "They are on their way to or from work.", True),
    ("Dog walking", HAPPENING_Q, "Someone is walking a dog.", True), ("Jogging", DOING_Q, "They are jogging.", True),
    ("People cycling", DOING_Q, "They are riding bicycles.", True),
    ("Driving", HAPPENING_Q, "Someone is driving.", False),
    ("Water carriers", DOING_Q, "They are carrying water.", True),
    ("People at wells", DOING_Q, "They are at a well, getting water.", True),
    ("Milking", HAPPENING_Q, "Someone is milking an animal.", False),
    ("People feeding animals", DOING_Q, "They are feeding animals.", True),
    ("People fishing", DOING_Q, "They are fishing.", True),
    ("Picnics", HAPPENING_Q, "People are having a picnic.", False),
    ("People playing chess", DOING_Q, "They are playing chess.", False),
    ("People playing board games", DOING_Q, "They are playing a board game.", False),
    ("People singing", DOING_Q, "They are singing.", True), ("People praying", DOING_Q, "They are praying.", True),
    ("People voting", DOING_Q, "They are voting.", True),
    ("People exercising", DOING_Q, "They are exercising.", True),
    ("Street vendors", DOING_Q, "They are selling things in the street.", False),
    ("Market vendors", DOING_Q, "They are selling things at a market.", True),
    ("Shoeshiners", DOING_Q, "They are shining shoes.", True),
    ("Porters", DOING_Q, "They are carrying loads as a porter.", False),
    ("Barbers at work", HAPPENING_Q, "A barber is cutting someone's hair.", False),
    ("Hairdressers at work", HAPPENING_Q, "A hairdresser is doing someone's hair.", False),
    ("Shoemakers at work", DOING_Q, "They are making or mending shoes.", False),
    ("Cashiers", DOING_Q, "They are working at a till (a checkout).", True),
    ("Waiters", DOING_Q, "They are waiting at tables, serving food or drink.", True),
    ("Farmers at work", DOING_Q, "They are working on a farm.", False),
    ("Agricultural workers", DOING_Q, "They are working on a farm.", True),
    ("Postal workers", DOING_Q, "They are delivering or sorting post.", True),
    ("Waste collectors", DOING_Q, "They are collecting rubbish.", True),
    ("Taxi drivers", DOING_Q, "They are driving a taxi.", False),
    ("Bus drivers", DOING_Q, "They are driving a bus.", False),
    ("Office workers", DOING_Q, "They are working in an office.", True),
    ("Teaching", HAPPENING_Q, "Someone is teaching.", False),
]
# The "Street vendors in" countries of the open pack (each checked to have at least 15 files): the country is the
# place.
STREET_VENDOR_COUNTRIES = [
    "Bangladesh", "Benin", "Bolivia", "Brazil", "Burkina Faso", "Cambodia", "Cameroon", "China", "Colombia", "Egypt",
    "Ethiopia", "Ghana", "Guatemala", "India", "Indonesia", "Iran", "Japan", "Kenya", "Madagascar", "Mali", "Mexico",
    "Morocco", "Mozambique", "Myanmar", "Nepal", "Nigeria", "Pakistan", "Peru", "Russia", "Burundi", "Cuba",
    "Ecuador", "France", "Germany", "Italy", "Ivory Coast", "Namibia", "Poland", "South Africa", "South Korea",
    "Spain", "Taiwan", "Tanzania", "Thailand", "Togo", "Turkey", "Uganda", "Ukraine", "Vietnam", "Zimbabwe",
    "the United States",
]
DAILY_NOT = re.compile(r"\b(nud\w*|naked|bath(e|es|ing)|swim\w*|bikini\w*|shower\w*|beach\w*|corpses?|dead|wounded|"
                       r"injured|blood\w*|executions?)\b", re.I)


def prepare_commons_daily_life_sa(source, data_dir, work, cap):
    """Wikimedia Commons daily-life categories, files under CC BY-SA or GFDL (home_sources.commons_sa_items: the
    categories share the cap; rows whose words name a child are marked "child"); the "Street vendors in" countries
    take a fifth of the cap, each row with its country as the place. Files whose words name nudity, bathing or a
    graphic scene are left out."""
    items = commons_sa_items(COMMONS_DAILY_SA, int(cap * 0.8), int(source.test * 0.8), "daily-sa")
    for country in STREET_VENDOR_COUNTRIES:
        spec = [(f"Street vendors in {country}", DOING_Q, "They are selling things in the street.", False)]
        got = commons_sa_items(spec, max(3, cap // 5 // len(STREET_VENDOR_COUNTRIES)), 0, "daily-sa")
        items += [(name, url, dict(row, place=country.removeprefix("the ").replace("United States", "USA")))
                  for name, url, row in got]
    items = [i for i in items if not DAILY_NOT.search(f"{i[0]} {i[2]['answer']}")]
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- research: Stanford 40 Actions

STANFORD40 = "https://vision.stanford.edu/Datasets/"
STANFORD40_PHOTOS = STANFORD40 + "Stanford40_JPEGImages.zip"          # 305 MB, read piece by piece
STANFORD40_BOXES = STANFORD40 + "Stanford40_XMLAnnotations.zip"       # the person's box, one per photo
STANFORD40_CREDIT = ("Stanford 40 Actions (Bangpeng Yao, Xiaoye Jiang, Aditya Khosla, Andy Lai Lin, Leonidas Guibas "
                     "and Li Fei-Fei, ICCV 2011), https://vision.stanford.edu/Datasets/40actions.html; photos gathered "
                     "from Google, Bing and Flickr, no licence stated")
# Each action with what the person is doing ("shooting an arrow" is left out: archery is in the sport packs).
STANFORD40_ACTIONS = {
    "applauding": "clapping", "blowing_bubbles": "blowing bubbles", "brushing_teeth": "brushing their teeth",
    "cleaning_the_floor": "cleaning the floor", "climbing": "climbing", "cooking": "cooking",
    "cutting_trees": "cutting down a tree", "cutting_vegetables": "cutting vegetables", "drinking": "drinking",
    "feeding_a_horse": "feeding a horse", "fishing": "fishing", "fixing_a_bike": "fixing a bicycle",
    "fixing_a_car": "fixing a car", "gardening": "gardening", "holding_an_umbrella": "holding an umbrella",
    "jumping": "jumping", "looking_through_a_microscope": "looking through a microscope",
    "looking_through_a_telescope": "looking through a telescope", "playing_guitar": "playing the guitar",
    "playing_violin": "playing the violin", "pouring_liquid": "pouring a drink", "pushing_a_cart": "pushing a cart",
    "reading": "reading", "phoning": "talking on the phone", "riding_a_bike": "riding a bicycle",
    "riding_a_horse": "riding a horse", "rowing_a_boat": "rowing a boat", "running": "running",
    "smoking": "smoking", "taking_photos": "taking a photo", "texting_message": "texting on a phone",
    "throwing_frisby": "throwing a frisbee", "using_a_computer": "using a computer",
    "walking_the_dog": "walking a dog", "washing_dishes": "washing dishes", "watching_TV": "watching television",
    "waving_hands": "waving", "writing_on_a_board": "writing on a board", "writing_on_a_book": "writing in a book",
}


def stanford40_box(xml):
    """(the person's box centre as fractions of the photo (x, y), the share of the photo the box covers) from one
    Stanford 40 annotation file, or None."""
    def number(tag):
        """The number in the first <tag> of the file."""
        found = re.search(rf"<{tag}>\s*([\d.]+)\s*</{tag}>", xml)
        return float(found.group(1)) if found else None
    x1, x2, y1, y2 = number("xmin"), number("xmax"), number("ymin"), number("ymax")
    width, height = number("width"), number("height")
    if None in (x1, x2, y1, y2) or not width or not height:
        return None
    return ((x1 + x2) / 2 / width, (y1 + y2) / 2 / height), (x2 - x1) * (y2 - y1) / (width * height)


def prepare_stanford40_actions(source, data_dir, work, cap):
    """Stanford 40 Actions (research: web photos, no licence stated): the actions take turns, so each gets an even
    share; each photo's answer says what the person is doing, and where they are in the picture when their box
    covers less than half of it. Both zips are read piece by piece (only the chosen photos are fetched)."""
    boxes = remote_zip(STANFORD40_BOXES)
    names = [n for n in boxes.namelist() if n.endswith(".xml")]
    by_action = {}
    for n in names:
        action = re.sub(r"_\d+\.xml$", "", os.path.basename(n))
        if action in STANFORD40_ACTIONS:
            by_action.setdefault(action, []).append(n)
    want = cap + source.test
    per_action = max(1, -(-want // len(by_action)))
    chosen = []
    for action in sorted(by_action):
        files = sorted(by_action[action])
        random.Random(f"s40-{action}").shuffle(files)
        for n in files[:per_action]:
            got = stanford40_box(boxes.read(n).decode("utf-8", "replace"))
            what = STANFORD40_ACTIONS[action]
            if got and got[1] < 0.5:
                answer = f"The person {spot(*got[0])} is {what}."
            else:
                answer = f"The person is {what}."
            photo = "JPEGImages/" + os.path.basename(n)[:-4] + ".jpg"
            chosen.append((photo, {"question": DOING_Q, "answer": answer, "split": "", "credit": STANFORD40_CREDIT}))
    say(f"  Fetching {len(chosen)} Stanford 40 photos ({len(by_action)} actions).")
    return zip_members(source, data_dir, work, lambda: remote_zip(STANFORD40_PHOTOS), chosen)


# ----------------------------------------------------------------- research: SWiG (imSitu)

SWIG_JSONS = "https://raw.githubusercontent.com/allenai/swig/master/SWiG_jsons/"
SWIG_PHOTOS = "https://swig-data-weights.s3.us-east-2.amazonaws.com/images_512.zip"      # 13.6 GB, read by ranges
SWIG_CREDIT = ("SWiG, Situations With Groundings (Sarah Pratt, Mark Yatskar, Luca Weihs, Ali Farhadi and Aniruddha "
               "Kembhavi, Allen Institute for AI, ECCV 2020), https://github.com/allenai/swig, built on imSitu (Mark "
               "Yatskar, Luke Zettlemoyer and Ali Farhadi, CVPR 2016); photos gathered from the web, no licence stated")
# Verbs left out: violence, arrests, intimacy, bathing and swimming, bodily functions, medical care, and things that
# are not people's daily activities (weather, plants, animals' own actions).
SWIG_LEFT_OUT = {
    "apprehending", "arresting", "attacking", "biting", "brawling", "burning", "burying", "butting", "caressing",
    "colliding", "confronting", "crashing", "detaining", "disciplining", "dissecting", "drooling", "exterminating",
    "frisking", "handcuffing", "hunting", "injecting", "interrogating", "kissing", "nuzzling", "peeing", "pooing",
    "punching", "ramming", "restraining", "shooting", "slapping", "snuggling", "spanking", "spearing", "striking",
    "stripping", "subduing", "urinating", "whipping", "bathing", "immersing", "soaking", "lathering", "waxing",
    "moisturizing", "massaging", "decomposing", "rotting", "ailing", "recuperating", "rehabilitating", "bandaging",
    "sucking", "licking", "swimming", "diving", "wading", "drenching", "wetting", "splashing", "submerging",
    "dousing", "flexing", "perspiring", "tickling", "spitting", "vomiting", "erupting", "raining", "snowing",
    "storming", "blossoming", "sprouting", "wilting", "branching", "cresting", "flaming", "glowing", "leaking",
    "overflowing", "bubbling", "dripping", "clawing", "pawing", "pouncing", "prowling", "gnawing", "grazing",
    "slithering", "swarming", "stampeding", "wagging", "flapping", "soaring", "swooping", "hatching", "stinging",
    "chasing", "tackling", "tattooing", "shearing", "camouflaging", "spying", "betting", "gambling", "begging",
    "misbehaving", "bothering", "nagging", "scolding", "glaring", "grieving", "mourning", "crying", "weeping",
    "sneezing", "coughing", "yawning", "drowning", "falling", "tripping", "stumbling", "slipping", "skidding",
    "plummeting", "destroying", "smashing", "breaking", "crushing", "ejecting", "inserting", "plunging", "gasping",
    "baptizing",
}
# A noun is a person when its name is one of these words, or its definition starts like a person's ("a person
# who ...", "someone who ...", "an adult ..."); only verbs done by a person are used.
SWIG_PERSON_NAMES = re.compile(r"^(person|people|man|woman|men|women|child|children|boy|girl|kid|baby|adult|"
                               r"lady|gentleman|worker|player|student|teacher|farmer|fisherman|chef|cook|doctor|nurse|"
                               r"soldier|police\w*|firefighter|fireman|athlete|surfer|skier|rider|driver|cyclist|"
                               r"customer|vendor|seller|mother|father|parent|family|crowd|team|couple|female child|"
                               r"male child|female|male|individual|human)$", re.I)
SWIG_PERSON_DEF = re.compile(r"^(a |an |the )?(person|someone|somebody|human being|adult|man\b|woman|child|boy|"
                             r"girl|young person|people|one who|a group of people|worker)", re.I)
# WordNet names said otherwise ("homo" is WordNet's first name for a human being).
SWIG_NAMES = {"homo": "person", "human being": "person", "female child": "girl", "male child": "boy",
              "sodium carbonate": "soda", "people": "people"}
# Places too vague to say, and things said without "a".
SWIG_VAGUE = {"outdoors", "outside", "inside", "indoors", "outdoor", "indoor", "the outdoors"}
SWIG_UNCOUNTED = {"water", "soil", "land", "food", "makeup", "make-up", "coffee", "tea", "weight", "paper", "grass",
                  "snow", "sand", "rice", "dough", "milk", "wine", "beer", "juice", "money", "hair", "ice", "mud",
                  "dirt", "fabric", "cloth", "wood", "meat", "bread", "soup", "salad", "flour", "sugar", "salt", "oil",
                  "paint", "glue", "wool", "fish", "laundry", "clothing", "clothes", "furniture", "music", "fruit",
                  "pasta", "cereal", "air", "fire", "smoke", "luggage", "garbage", "trash", "rubbish", "lumber"}


def swig_noun(nouns, code):
    """The first name of a noun ("dough"), or "" for an empty role or a place too vague to say ("outdoors")."""
    if not code:
        return ""
    entry = nouns.get(code) or {}
    name = re.sub(r"\s*\([^)]*\)", "", clean((entry.get("gloss") or [""])[0])).strip()
    name = SWIG_NAMES.get(name.lower(), name)
    return "" if name.lower() in SWIG_VAGUE else name


def swig_is_person(entry):
    """Whether a SWiG noun is a person (by its names, or how its definition starts)."""
    return any(SWIG_PERSON_NAMES.match(clean(g)) for g in entry.get("gloss") or []) or \
        bool(SWIG_PERSON_DEF.match(clean(entry.get("def"))))


ING_DOUBLED = {w + "s": w + w[-1] + "ing" for w in ("cut", "put", "sit", "hit", "get", "run", "swim", "dig", "set",
                                                    "shut", "rub", "grab", "drag", "pat", "chop", "drop", "flip",
                                                    "dip", "stir", "tap", "wrap", "trap", "plan", "hug", "slip",
                                                    "beg", "jog", "mop", "nap", "pin", "plug", "scrub", "shop",
                                                    "skip", "snap", "spin", "strip", "tip", "trim", "whip")}
ING_DOUBLED.update({"lies": "lying", "ties": "tying", "dies": "dying"})


def ing(word):
    """The -ing form of a verb in the simple present ("extracts" -> "extracting", "makes" -> "making", "uses" ->
    "using"); rough, for the few imSitu sentences whose verb is not the situation's own."""
    word = word.lower()
    if word.endswith("ed") and len(word) >= 4:         # a sentence in the past ("used") -> "use"
        word = word[:-1] + "s"
    if word in ING_DOUBLED:
        return ING_DOUBLED[word]
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "ying"
    stem = word[:-2] if re.search(r"(s|x|z|ch|sh)es$", word) else re.sub(r"s$", "", word)
    if stem.endswith("e") and not stem.endswith(("ee", "ye", "oe")):
        stem = stem[:-1]
    return stem + "ing"


def swig_sentence(abstract, roles, nouns):
    """The verb's sentence with the roles filled in ("the AGENT kneads an ITEM at a PLACE." -> "A woman is kneading
    dough in a kitchen."), dropping each empty role with the little words before it; "" when the agent is empty or
    not a person."""
    text = abstract
    for role, code in roles.items():
        name = swig_noun(nouns, code)
        tag = role.upper()
        if not name:
            text = re.sub(rf"\s*(\b(in|at|on|from|to|with|into|onto|for|of|by|through|over|under|using|toward|"
                          rf"towards|across|along|around|off|near|inside|about|against|behind|up|down)\b\s+)?"
                          rf"(\b(a|an|the|some)\b\s+)?\b{tag}\b", "", text)
            continue
        article = "" if name.lower() in SWIG_UNCOUNTED else a_or_an(name) + " "
        text = re.sub(rf"\b(a|an)\s+{tag}\b", f"{article}{name}", text)
        text = re.sub(rf"\b{tag}\b", name, text)
    if re.search(r"[A-Z]{2,}", text):              # a role left that could not be filled
        return ""
    text = " ".join(text.split()).strip()
    text = re.sub(r"^(a|an|the) (people|crowd|team|family|group of people) is\b", lambda m: f"the {m.group(2)} are",
                  text, flags=re.I)
    return text[:1].upper() + text[1:] if text else ""


def swig_answer(item, verbs, nouns):
    """(answer, words) for one SWiG photo: its verb's sentence filled with the noun most of the three people chose
    for each role (the first person's where they all differ), or None when the agent is not a person."""
    verb = verbs.get(item.get("verb"))
    frames = item.get("frames") or []
    if not verb or not frames:
        return None
    roles = {}
    for role in frames[0]:
        votes = [f.get(role, "") for f in frames]
        roles[role] = max(votes, key=lambda v: (votes.count(v), v == votes[0]))
    agent = roles.get("agent") or roles.get("agents") or ""
    if not agent or not swig_is_person(nouns.get(agent) or {}):
        return None
    abstract = re.sub(r"\s*\([^)]*\)", "", clean(verb.get("abstract", ""))).replace("his/her", "their")
    if abstract.startswith("AGENT"):
        abstract = "the " + abstract
    # Most imSitu sentences are in the simple present ("the AGENT kneads ..."); said in the -ing form for "what is
    # happening": the situation's own verb when the sentence uses it ("kneads" -> "is kneading"), else the
    # sentence's verb turned ("extracts" -> "is extracting").
    found = re.match(r"^(the|an?|it)\s+(AGENTS?)\s+(\w+)", abstract)
    if not found:
        return None
    if found.group(3) not in ("is", "are"):
        word = found.group(3)
        doing = item["verb"] if word[:3].lower() == item["verb"][:3].lower() else ing(word)
        abstract = f"the {found.group(2)} is {doing}" + abstract[found.end():]
    sentence = swig_sentence(abstract, roles, nouns)
    if not sentence:
        return None
    return sentence.rstrip(".") + ".", " ".join(swig_noun(nouns, c) for c in roles.values())


def prepare_swig_situations(source, data_dir, work, cap):
    """SWiG (research: web photos): reads the three JSON files and the noun and verb list (about 66 MB from GitHub),
    takes the verbs in turn so that each gets an even share, writes "What is happening in this picture?" with the
    filled-in sentence, and fetches only the chosen photos out of the 13.6 GB zip by HTTP ranges."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = sources.USER_AGENT
    space = s.get(SWIG_JSONS + "imsitu_space.json", timeout=300).json()
    verbs = {k: v for k, v in space["verbs"].items() if k not in SWIG_LEFT_OUT}
    nouns = space["nouns"]
    by_verb = {}
    for part in ("train.json", "dev.json", "test.json"):
        for name, item in s.get(SWIG_JSONS + part, timeout=600).json().items():
            if item.get("verb") in verbs:
                by_verb.setdefault(item["verb"], []).append((name, item))
    want = cap + source.test
    per_verb = max(1, -(-want // max(1, len(by_verb))))
    chosen = []
    for verb in sorted(by_verb):
        photos = sorted(by_verb[verb], key=lambda x: x[0])
        random.Random(f"swig-{verb}").shuffle(photos)
        got = 0
        for name, item in photos:
            if got >= per_verb:
                break
            answer = swig_answer(item, verbs, nouns)
            if not answer:
                continue
            row = marked({"question": HAPPENING_Q, "answer": answer[0], "split": "", "credit": SWIG_CREDIT},
                         answer[1])
            chosen.append(("images_512/" + name, row))
            got += 1
    random.Random("swig").shuffle(chosen)
    chosen = chosen[:want]
    say(f"  Fetching {len(chosen)} SWiG photos ({len(by_verb)} verbs done by people).")
    return zip_members(source, data_dir, work, lambda: remote_zip(SWIG_PHOTOS), chosen)


# ----------------------------------------------------------------- research: Human Action Recognition (HAR)

HAR_REPO = "Bingsu/Human_Action_Recognition"
HAR_CREDIT = ("Human Action Recognition (HAR) Dataset, DPhi data sprint 76 (https://dphi.tech/challenges/"
              "data-sprint-76-human-activity-recognition/233/data), via Kaggle and huggingface.co/datasets/"
              "Bingsu/Human_Action_Recognition (marked ODbL); photos gathered from the web")
# The classes in their number order (the dataset card's label mapping), with the answer; fighting is left out.
HAR_CLASSES = ["calling", "clapping", "cycling", "dancing", "drinking", "eating", "fighting", "hugging", "laughing",
               "listening_to_music", "running", "sitting", "sleeping", "texting", "using_laptop"]
HAR_ANSWERS = {"calling": "They are talking on the phone.", "clapping": "They are clapping.",
               "cycling": "They are riding a bicycle.", "dancing": "They are dancing.",
               "drinking": "They are drinking.", "eating": "They are eating.", "hugging": "They are hugging.",
               "laughing": "They are laughing.", "listening_to_music": "They are listening to music.",
               "running": "They are running.", "sitting": "They are sitting.", "sleeping": "They are sleeping.",
               "texting": "They are texting on a phone.", "using_laptop": "They are using a laptop."}


def prepare_har_actions(source, data_dir, work, cap):
    """HAR (research: web photos, marked ODbL by its uploader): the training file's labelled photos (the test file's
    are all labelled 0, so it is not used), the classes taking turns; photos saved from the parquet file itself."""
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    by_class = {}
    for name in hf_parquet_files(HAR_REPO, r"train"):
        for index, r in enumerate(hf_parquet_rows(HAR_REPO, name, ["image", "labels"])):
            number = r.get("labels")
            label = HAR_CLASSES[number] if isinstance(number, int) and 0 <= number < len(HAR_CLASSES) else ""
            if label in HAR_ANSWERS and (r.get("image") or {}).get("bytes"):
                by_class.setdefault(label, []).append((f"har-{label}-{index}", r["image"]["bytes"]))
    want = cap + source.test
    per_class = max(1, -(-want // max(1, len(by_class))))
    rows = []
    for label in sorted(by_class):
        photos = by_class[label]
        random.Random(f"har-{label}").shuffle(photos)
        for name, data in photos[:per_class]:
            path = sources.save_picture(name, data, folder)
            if path:
                rows.append({"picture": path, "question": DOING_Q, "answer": HAR_ANSWERS[label], "split": "",
                             "credit": HAR_CREDIT})
    say(f"  {len(rows)} HAR photos from {len(by_class)} activities.")
    return rows


# ----------------------------------------------------------------- the collections

PEOPLE_ACTIVITY_SOURCES = [
    # ---- share-alike
    Source("commons_daily_life_sa", "Wikimedia Commons: people eating, reading, praying, shopping, washing, selling "
                                    "and at work, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 3000, 30, prepare_commons_daily_life_sa, "about 300 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("coco_actions_sa", "What are the people doing? V-COCO and Visual Genome on COCO photos under CC BY-SA "
                              "(share-alike, ready-made pack; photos fetched from COCO)",
           "Rows: V-COCO MIT, Visual Genome CC BY 4.0, COCO boxes CC BY 4.0; photos CC BY-SA 2.0 (cocodataset.org)",
           "V-COCO (Gupta and Malik, 2015), MIT, https://github.com/s-gupta/v-coco; Visual Genome (Krishna et al., "
           "2017), CC BY 4.0, https://visualgenome.org; photos from COCO (cocodataset.org), CC BY-SA 2.0",
           "share-alike", 2000, 20, sources.prepare_pack, "about 300 MB (photos fetched from COCO)",
           terms="https://creativecommons.org/licenses/by-sa/2.0/",
           terms_summary="CC BY-SA 2.0 photos: use with credit, and anything made from them keeps the same licence."),
    # ---- non-commercial
    Source("coco_actions_nc", "What are the people doing? V-COCO and Visual Genome on COCO's non-commercial photos "
                              "(personal use, ready-made pack; photos fetched from COCO)",
           "Rows: V-COCO MIT, Visual Genome CC BY 4.0, COCO boxes CC BY 4.0; photos CC BY-NC, BY-NC-SA, BY-NC-ND or "
           "BY-ND 2.0 (cocodataset.org)",
           "V-COCO (Gupta and Malik, 2015), MIT, https://github.com/s-gupta/v-coco; Visual Genome (Krishna et al., "
           "2017), CC BY 4.0, https://visualgenome.org; photos from COCO (cocodataset.org), each photo's licence in "
           "its row", "noncommercial", 6000, 30, sources.prepare_pack, "about 1 GB (photos fetched from COCO)",
           terms="https://creativecommons.org/licenses/by-nc/2.0/",
           terms_summary="The photos are CC BY-NC (some BY-NC-SA, BY-NC-ND or BY-ND): use with credit, not for "
                         "commercial purposes."),
    # ---- research
    Source("stanford40_actions", "Stanford 40 Actions: people brushing teeth, cooking, washing dishes, phoning, "
                                 "reading and 35 more actions (personal use)",
           "No licence stated (vision.stanford.edu/Datasets/40actions.html); photos gathered from Google, Bing and "
           "Flickr", STANFORD40_CREDIT, "research", 3000, 40, prepare_stanford40_actions,
           "about 120 MB of the 305 MB zip, read piece by piece",
           terms="https://vision.stanford.edu/Datasets/40actions.html",
           terms_summary=research("No licence is stated; the photos were gathered from Google, Bing and Flickr, so "
                                  "their own rights are unclear.")),
    Source("swig_situations", "SWiG (imSitu): who is doing what, with what and where, in 500 everyday situations "
                              "(personal use)",
           "Repository MIT (github.com/allenai/swig); no licence stated for the photos, which were gathered from the "
           "web", SWIG_CREDIT, "research", 6000, 60, prepare_swig_situations,
           "about 66 MB of labels and 300 MB of the 13.6 GB photo zip, read piece by piece",
           terms="https://github.com/allenai/swig",
           terms_summary=research("The labels' repository is MIT, but the photos were gathered from the web (image "
                                  "search) and no licence is stated for them.")),
    Source("har_actions", "Human Action Recognition: people calling, texting, eating, drinking, sleeping, cycling "
                          "and using a laptop (personal use)",
           "Marked ODbL by its uploader (huggingface.co/datasets/Bingsu/Human_Action_Recognition); photos gathered "
           "from the web", HAR_CREDIT, "research", 2000, 30, prepare_har_actions, "about 330 MB",
           terms="https://huggingface.co/datasets/Bingsu/Human_Action_Recognition",
           terms_summary=research("Marked ODbL (share-alike for databases) by its uploader, but the photos were "
                                  "gathered from the web, so the rights in them are not the uploader's to give.")),
]

# The collections a picture-making model may learn from: none (they are all about people).
PEOPLE_ACTIVITY_PICTURE_MAKING_OK = set()

PEOPLE_ACTIVITY_SIGN_UP = {
    "HICO-DET, Humans Interacting with Common Objects (Chao et al., University of Michigan; research)":
        "https://websites.umich.edu/~ywchao/hico/ : the 47,776 photos with 600 kinds of person-object interaction "
        "(riding, feeding, washing, repairing, cutting ...) are a 7.5 GB archive on Google Drive, which a program "
        "cannot fetch without a Google sign-in; the photos come from Flickr with no licence given, so research use "
        "only. Put the photos and their questions in the own-pictures folder.",
    "MPII Human Pose activities (Max Planck Institute for Informatics; non-commercial research)":
        "https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/software-and-datasets/"
        "mpii-human-pose-dataset/download : 25,000 YouTube frames, each named with one of 410 everyday activities "
        "(home activities, occupations, transport, self care ...). Annotations under the Simplified BSD licence, "
        "but 'commercial use is not allowed' because the makers do not own the images. The 12.9 GB tar.gz must be "
        "downloaded whole and the activity names are in a MATLAB file; it can be prepared by hand for the "
        "own-pictures folder.",
    "Ego4D and EgoObjects (Meta AI; signed licence)":
        "https://ego4d-data.org : daily life filmed from people's own heads in 74 places in 9 countries; needs a "
        "signed licence agreement and the AWS command line (also listed in things_sources.py).",
    "Kaggle activity sets":
        "https://www.kaggle.com : a Kaggle account. 'Human Action Recognition (HAR) Dataset' (the original of "
        "har_actions), 'Yoga poses', 'Daily activities' and similar sets; most gather their photos from the web, so "
        "research use only.",
    "Roboflow Universe activity sets":
        "https://universe.roboflow.com : a free account and API key. People-activity detection sets (phone use, "
        "eating, smoking, falling); check where each set's pictures came from.",
}

PEOPLE_ACTIVITY_NOT_INCLUDED = {
    "imsitu.org": "the imSitu website's domain now belongs to an unrelated betting site; imSitu's photos and labels "
                  "are taken from the SWiG copy (swig_situations), which the Allen Institute keeps.",
    "Visual Genome's other (non-COCO) photos":
        "Visual Genome records no licence for them; its relationship file needs about 4 GB of memory to read, too "
        "much for many home computers. Its people-written questions on these photos are already in vg_photos "
        "(extra_sources.py); the COCO ones are in vg_people_actions, coco_actions_nc and coco_actions_sa.",
    "Kinetics-700, AVA, Moments in Time, HAA500, ActivityNet":
        "videos on YouTube and from films that their makers do not own and do not share; many are gone. The kit's "
        "video collections already cover filmed daily life (Charades, EPIC-KITCHENS in things_sources.py).",
    "PASCAL VOC 2012 action images":
        "about 4,600 Flickr photos of 10 actions (jumping, phoning, playing an instrument, reading, riding a bike or "
        "horse, running, taking a photo, using a computer, walking), all in Stanford 40 Actions and V-COCO already, "
        "inside a 2 GB archive.",
    "People Playing Musical Instruments (PPMI)": "people with 12 instruments; musical instruments are in "
                                                  "culture_packs.py and Stanford 40 has playing guitar and violin.",
    "Open Images relationships (people holding, riding, playing ...)": "already the open open_images_in_use pack "
                                                                       "(things_packs.py).",
    "Open Images postures and expressions (sitting, walking, dancing, sleeping, talking)": "already the open "
                                                                                           "oi_expressions pack.",
    "Dollar Street homes and things": "already the open dollar_street pack (world_life_packs.py); its daily-routine "
                                      "topics are the open dollar_street_routines pack here. Most routine topics are "
                                      "videos, which are left out.",
    "Library of Congress FSA/OWI and US National Archives daily-life photos": "already the open loc_fsa, nara and "
                                                                              "related packs.",
    "Unsplash Lite": "already unsplash_lite (documentary_sources.py), photographers' own descriptions.",
    "Charades and EPIC-KITCHENS": "already in things_sources.py.",
    "Localized Narratives, Flickr30k Entities, COCO captions": "already in more_sources.py and extra_sources.py "
                                                               "(people's descriptions of everyday photos).",
    "PISC, People in Social Context (Li et al., 2017; Zenodo 1059155, marked CC BY 4.0)":
        "its labels are social relationships between pairs of people (friends, family, couple, professional) and "
        "people's occupations, which are guesses about who people are rather than what they are doing (this kit "
        "never guesses identity); its 22,670 photos come from COCO, Visual Genome and the web under their own "
        "licences, in a 3.7 GB archive that must be read whole.",
    "Stanford 40 'shooting an arrow'": "archery is a sport, in the sport collections.",
    "HAR 'fighting'": "violence between people is not a daily activity here.",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one people-activity collection.")
    parser.add_argument("key", choices=[s.key for s in PEOPLE_ACTIVITY_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PEOPLE_ACTIVITY_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="people-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
