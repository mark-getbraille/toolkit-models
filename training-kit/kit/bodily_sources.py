"""Picture collections of bodily fluids and waste for the Picture Model Training Kit that cannot be ready-made packs:
share-alike, non-commercial, or research-only (or with rights that are not clear). The open ones (ScatSpotter dog
poop, iNaturalist droppings, Open Images blood and injury labels, Wikimedia Commons CC0/PD/CC BY files, PubMed Central
case-report photos and urine samples) are packs in packs/bodily_packs.py.

Why: a blind parent asks "my child was sick: what does this look like? is there blood in it?", and a blind dog owner
photographs the yard and asks "has my dog pooped here?". The describer should say plainly what is visible and when to
get help.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py): "share-alike" (only with the share-alike choice), "noncommercial" (personal
use only), "research" (rights not clear: personal use only, after agreeing to the terms).

Safety and content:
  - Human material (stool, vomit, urine, blood) is content "medical": only with the medical box. Pet and yard material
    (droppings) has no content mark.
  - Commons pictures that may show a person's body are kept only when the file's own words say the person is an adult
    and name no child; nothing intimate, nude or sexual. Stool, vomit and urine themselves may come from a child (they
    do not show the child); rows whose words name a child are marked "child".
  - Answers are fixed sentences from each source's own labels, file names and captions (nothing is written by an AI
    model); human medical answers end with a fixed line saying when to see a doctor.
  - BODILY_PICTURE_MAKING_OK is empty: no collection here is used for picture-making. (The owner may later add the
    dog-poop-on-grass collections, which show no people, if he wants a picture-making model to learn them.)

The collections (BODILY_SOURCES):
  share-alike
    commons_bodily_sa      Wikimedia Commons: human stool, the Bristol stool chart, vomit, discoloured and bloody urine,
                           urine bags, blood stains and nosebleeds, files under CC BY-SA or GFDL (content "medical").
    commons_droppings_sa   Wikimedia Commons: dog, cat, horse and bird droppings and litter boxes, files under CC BY-SA
                           or GFDL.
    inat_droppings_sa      iNaturalist "Evidence of presence: Scat" observations of pets, farm animals, birds and yard
                           animals whose photo is CC BY-SA (research-grade only, through GBIF and the iNaturalist
                           Open Dataset, inat_gbif.py; such photos are few).
  noncommercial
    inat_droppings_nc      The same, photos under CC BY-NC, CC BY-NC-SA or CC BY-NC-ND (most of iNaturalist's
                           research-grade droppings photos, through GBIF and the iNaturalist Open Dataset).
  research (rights not clear)
    bloodstain_patterns    Blood Stain Pattern Data Set (BSPDS; Mendeley Data 234yvmkcys): 24 high-speed laboratory
                           videos of blood dripping, swiped, wiped and transferred onto clear plastic, cardboard and
                           cloth; two stills from each (the middle and the end), with what the video's own name says.
                           "CC BY 4.0" is stated by the uploaders, but the frames credit the Midwest Forensics Resource
                           Center film by T. L. Laber, B. P. Epstein and M. C. Taylor (2007), whose own terms are not
                           given. Needs the video extras (requirements-video.txt).

Needing sign-up (cannot be downloaded automatically; get them yourself, then put the pictures in the own-pictures folder
with your own descriptions, as the user guide says). Each is listed with what its page says about its licence:
  Roboflow Universe dog-poop sets           https://universe.roboflow.com (a free account and API key are needed to
                                            download; each set shows its own licence, many CC BY 4.0): Poop Finder
                                            (universe.roboflow.com/lex-cmebl/poop-finder, about 700 photos, CC BY 4.0),
                                            dogpoop (universe.roboflow.com/kjw-ipsh9/dogpoop-ehbe6, about 2,000, CC BY
                                            4.0), Yolo-person-dog-poop (universe.roboflow.com/umai-tower/
                                            yolo-person-dog-poop-rznwm, about 1,200, CC BY 4.0), pooping-dog-detection
                                            (universe.roboflow.com/caquetaproject/pooping-dog-detection, CC BY 4.0;
                                            dogs in the act), and the sets ScatSpotter's author recommends:
                                            han-bjamu/poppopo, pazini/dog-poop-detection-uip1h, new-workspace-j42am/
                                            softpoop and new-workspace-j42am/dp-4iarz. Roboflow counts include
                                            augmented copies, and ScatSpotter's author says one set copies his photos
                                            under a wrong licence: check where each set's photos came from.
  Roboflow Universe stool, vomit and        universe.roboflow.com/project-ap1yb/bristol-stool-slqqx (Bristol stool
  diarrhoea sets                            classes, CC BY 4.0 stated), universe.roboflow.com/newdrowningdata
                                            ("childVomiting", about 1,100 photos; licence not shown without an account),
                                            universe.roboflow.com/hannah-k-y-chu-gmail-com/diarrhea and
                                            universe.roboflow.com/mariem-wqdga/project_sign (a "vomissement" class,
                                            public domain stated). Check that the photos were the makers' own.
  Kaggle Dog Poop Dataset                   https://www.kaggle.com/datasets/wengjiyao/dog-poop-dataset : about 4,900
                                            photos in "poop" and "notpoop" folders; a Kaggle account is needed; its
                                            page names the World Bank dataset terms (check them there).
  AnimalClue feces_yolo (ICCV 2025)         https://huggingface.co/datasets/risashinoda/feces_yolo : animal droppings
                                            from iNaturalist with boxes; access must be requested on Hugging Face, and
                                            each photo keeps its own iNaturalist licence. The inat_droppings pack and
                                            the two entries above read the same kind of iNaturalist photos through
                                            GBIF and the iNaturalist Open Dataset (inat_gbif.py).
  Human stool photo collections             No open set exists (checked November 2026 on Zenodo, Mendeley Data,
  (Bristol scale)                           figshare, Kaggle, GitHub and Hugging Face). The research sets are held by
                                            their authors: Hachuel et al., "Augmenting Gastrointestinal Health: A Deep
                                            Learning Approach to Human Stool Recognition" (arXiv 1903.10578, about 900
                                            to 50,000 photos rated on the Bristol scale, "for academic use": write to
                                            the authors), Zhou et al., "Stool Image Analysis for Precision Health
                                            Monitoring by Smart Toilets" (MLHC 2021, 3,275 photos), and Zhang et al.,
                                            "Human Stools Classification ..." (CVPR Workshops 2022). The POOING project
                                            (github.com/forreal03/pooing) plans a made-up (synthetic) set under CC BY
                                            4.0, not yet released.
  Infant stool colour cards                 Taiwan's card (Health Promotion Administration and Prof. Mei-Hwei Chang;
                                            nine numbered stool photos in the Children's Health Handbook): other
                                            countries use it with the Administration's permission; ask
                                            https://www.hpa.gov.tw . Japan's 便色カード in the Mother and Child Health
                                            Handbook: the ministry's site terms allow reuse with credit, but the card
                                            itself may belong to its makers; ask the Ministry of Health, Labour and
                                            Welfare (https://www.mhlw.go.jp). Newborn Screening Ontario's card
                                            (https://www.newbornscreening.on.ca) is copyrighted and asks to be asked.
                                            The Geneva University Hospitals card (https://www.hug.ch) states no terms.
                                            Photos of a baby's pale (acholic) stool from CC BY case reports are in the
                                            case_report_bodily pack.
  Smartphone urine colour photos            Chew et al. (PLOS Neglected Tropical Diseases 2020, dengue patients) and
                                            Bustam et al. (Digital Health 2023, 1,400 photos): the articles are open,
                                            the photo sets are not published; write to the authors.
  BloodNet bloodstain-age photos            Duke University (figshare; see scholars.duke.edu/publication/1668166):
                                            check the figshare record's licence.

The owner's describers website and his own-pictures folder can fill the gaps listed in BODILY_GAPS.

Looked at and not included (the reason of each is in BODILY_NOT_INCLUDED).

    python -c "import sources, bodily_sources"      (from the kit folder: checks the file loads)
"""

import os
import random
import re

import sources
from extra_sources import (NUDE, commons_file_name, commons_members, commons_sa_entries, commons_session,
                           is_adult_text, video_still)
from personal_sources import CHILD_WORDS, INTIMATE_SITE
from sources import USER_AGENT, Source, clean, download_file, fetch_pictures

# The fixed sentences said after a human medical answer (as packs/bodily_packs.py).
STOOL_ADVICE = "Only a doctor can diagnose this; if a child has blood in their stool, a black stool, or seems " \
               "unwell, contact a doctor."
VOMIT_ADVICE = "If vomit contains blood or looks like coffee grounds, get medical help."
URINE_ADVICE = "Only a doctor can diagnose this; if urine looks red, brown or cola-coloured, or stays very dark, " \
               "contact a doctor."
BLOOD_ADVICE = "If bleeding is heavy or does not stop, get medical help."
ALT_TEXT = "Write a short description of this picture for someone who cannot see it."


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


# ----------------------------------------------------------------- research: Blood Stain Pattern Data Set (videos)

BSPDS_API = "https://data.mendeley.com/public-api/datasets/234yvmkcys"
BSPDS_CREDIT = "Blood Stain Pattern Data Set (BSPDS; Sedik, Albeedan, Kolivand and Abd El-Latif), Mendeley Data " \
               "234yvmkcys, https://data.mendeley.com/datasets/234yvmkcys; videos by T. L. Laber, B. P. Epstein and " \
               "M. C. Taylor, Midwest Forensics Resource Center, 2007"
BLOOD_Q = "What does this picture show?"


# What each video shows, in plain words, from its own file name (keyed by the code at the start of the name).
BSPDS_SHOWS = {
    "10Aa3": "a swipe of blood on a clear plastic sheet, made with a bloodied finger",
    "10Aa5": "a swipe of blood on a clear plastic sheet, made with bloodied fingers",
    "10Ab1": "a swipe of blood on a clear plastic sheet, made with a bloodied piece of cotton sweatshirt",
    "10Ba2": "blood on a clear plastic sheet, wiped with a finger after 30 seconds",
    "10Ba6": "blood on a clear plastic sheet, wiped with a finger after 4 minutes",
    "10Bb1": "blood on a clear plastic sheet, wiped with a paper towel after 90 seconds",
    "10Bb3": "blood on a clear plastic sheet, wiped and swiped with a paper towel",
    "10Ca1": "a blood-stained cotton sweatshirt pressed against a clean sweatshirt",
    "10Ca2": "a blood-stained cotton sweatshirt drawn over another sweatshirt",
    "10Cd1": "bloodied toothbrush bristles touched to a sweatshirt",
    "10Cd2": "bloodied toothbrush bristles touched to a sweatshirt",
    "15Aa2": "coughed-up blood",
    "1Aa2": "blood dripping from a wrench handle",
    "1Ab1": "blood dripping from a wrench handle already wet with blood",
    "1Ab2": "blood dripping from a wrench handle already wet with blood",
    "1Ba2": "blood dripping from the tip of a tyre iron",
    "1Bb1": "blood dripping from a tyre iron already wet with blood",
    "1Ca1": "blood dripping from the tip of a pipette held upright",
    "1Cb1": "blood dripping from the tip of a pipette held at an angle",
    "1Da1": "blood dripping through cotton denim cloth",
    "1Ea1": "blood dripping from the tip of a bleeding finger",
    "3Aa1a": "a drop of blood that fell 10 centimetres onto cardboard",
    "3Ab1b": "a drop of blood that fell 1 metre onto cardboard",
}


def bspds_answer(file_name):
    """The answer for one video ("1Aa2 Blood dripping from a wrench handle.avi" -> "... It shows blood dripping from
    a wrench handle."), or "" for a video not in BSPDS_SHOWS."""
    shows = BSPDS_SHOWS.get(file_name.split(" ", 1)[0])
    return f"This is a still from a laboratory video of blood stains. It shows {shows}." if shows else ""


def prepare_bloodstain_patterns(source, data_dir, work, cap):
    """BSPDS (Mendeley Data 234yvmkcys; "CC BY 4.0" stated by its uploaders): 24 videos (about 600 MB, kept in the
    downloads folder), two stills from each (the middle and the end, when the stain has formed), read with PyAV
    (requirements-video.txt). The answer comes from the video's own name. Content "medical" (human blood). Each
    still carries the film's own caption panel (its makers' names and the frame rate) on the left."""
    import requests
    record = requests.get(BSPDS_API, timeout=120, headers={"User-Agent": USER_AGENT}).json()
    licence = (record.get("data_licence") or {}).get("short_name", "")
    if licence and licence != "CC BY 4.0":
        say(f"  BSPDS: the stated licence is now {licence!r}; check it on the dataset's page")
    folder, rows = os.path.join(data_dir, source.key), []
    files = [f for f in record.get("files") or [] if f.get("filename", "").lower().endswith(".avi")]
    seen = set()
    for f in files:
        name = f["filename"]
        if not bspds_answer(name):
            continue
        if re.sub(r"\s*\(\d+\)", "", name) in seen:                        # a second copy of the same video
            continue
        seen.add(re.sub(r"\s*\(\d+\)", "", name))
        path = os.path.join(work, "bspds", re.sub(r"[^\w.-]", "_", name))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        download_file(f["content_details"]["download_url"], path)
        with open(path, "rb") as fh:
            data = fh.read()
        for at, part in ((0.5, "middle"), (0.97, "end")):
            picture = sources.save_picture(f"bspds-{os.path.splitext(name)[0]}-{part}", video_still(data, at), folder)
            if picture:
                rows.append({"question": BLOOD_Q, "answer": bspds_answer(name), "split": "", "picture": picture,
                             "credit": BSPDS_CREDIT})
        if len(rows) >= cap + source.test:
            break
    return rows


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

# Each category: (question, answer, whether a picture may show a person's body, so needs the file's words to say the
# person is an adult). As packs/bodily_packs.COMMONS_BODILY.
COMMONS_HUMAN = {
    "Human feces": ("What is this?", "This is human poop (stool). " + STOOL_ADVICE, False),
    "Bristol Stool Chart": ("What does this chart show?",
                            "This is the Bristol Stool Form Scale: a chart of seven types of stool, from type 1 "
                            "(separate hard lumps, like nuts) to type 7 (entirely liquid, no solid pieces). Types 3 "
                            "and 4 are the usual, healthy kinds.", False),
    "Vomits": ("What is this?", "This is vomit. " + VOMIT_ADVICE, False),
    "Humans vomiting": ("What is happening here?", "Someone is being sick (vomiting). " + VOMIT_ADVICE, True),
    "Urine discoloration": ("What does this urine look like?",
                            "This urine is not its usual pale-yellow colour. " + URINE_ADVICE, False),
    "Hematuria": ("What does this urine look like?", "It is red or pink: it may have blood in it (haematuria). " +
                  URINE_ADVICE, False),
    "Urine bags": ("What is this?", "This is a urine bag: a bag that collects urine through a tube (a catheter). " +
                   URINE_ADVICE, False),
    "Bloodstains": ("What is this stain?", "It looks like a blood stain.", False),
    "Bloodstains on asphalt": ("What is this stain?", "It looks like a blood stain on the road.", False),
    "Bloodstains on snow": ("What is this stain?", "It looks like blood on the snow.", False),
    "Nosebleeds": ("What is happening here?", "This is a nosebleed: blood is coming from the nose. " + BLOOD_ADVICE,
                   True),
}
URINE_CHART = ("What does this chart show?",
               "This is a urine colour chart: it shows shades from pale yellow (drinking enough) to dark yellow or "
               "amber (drink more water). " + URINE_ADVICE)
# Single Commons files under CC BY-SA with their question and answer: urine colour (hydration) charts.
COMMONS_SA_FILES = {"File:Urine Hydration chart.jpg": URINE_CHART}
COMMONS_ANIMAL = {
    "Dog feces": ("What is this?", "This is dog poop.", False),
    "Dog feces on the streets of the cities": ("What is this on the ground?", "This is dog poop on the street.",
                                               False),
    "Dog fouling": ("What is this on the ground?", "This is dog poop that has been left on the ground.", False),
    "Cat feces": ("What is this?", "This is cat poop.", False),
    "Horse feces": ("What is this?", "This is horse manure (horse droppings).", False),
    "Bird feces": ("What is this?", "These are bird droppings.", False),
    "Litter boxes": ("What is this?", "This is a cat litter box (litter tray).", False),
}
# Words a file's title, caption or description must have for its category (Commons categories hold other things too:
# a street, a sewer, toilet limescale), by category; a category not listed needs none.
COMMONS_NEEDS = {
    "Human feces": r"fa?eces|fa?ecal|stools?|poo+p?s?|excrement|shit|turds?|defecat\w*",
    "Vomits": r"vomit\w*|puke\w*|sick",
    "Humans vomiting": r"vomit\w*|puke\w*|being sick|throw\w* up",
    "Urine discoloration": r"urine",
    "Hematuria": r"urine|hae?maturia",
    "Urine bags": r"urine|catheter|bag",
    "Bloodstains": r"blood\w*",
    "Bloodstains on asphalt": r"blood\w*",
    "Bloodstains on snow": r"blood\w*",
    "Nosebleeds": r"nose|epistaxis",
    "Dog feces": r"dog|canine|fa?eces|poo+p?s?|excrement|dropping\w*|shit|fouling|turds?",
    "Dog feces on the streets of the cities": r"dog|fa?eces|poo+p?s?|excrement|dropping\w*|shit|fouling",
    "Dog fouling": r"dog|fa?eces|poo+p?s?|excrement|dropping\w*|fouling",
    "Cat feces": r"cat|fa?eces|poo+p?s?|excrement|dropping\w*|scat",
    "Horse feces": r"horse|manure|dung|fa?eces|poo+p?s?|dropping\w*|apples",
    "Bird feces": r"bird|guano|dropping\w*|fa?eces|poo+p?s?|excrement|pigeon|gull|goose|geese",
    "Litter boxes": r"litter\w*|tray",
}
# Animal words: a file in a human category (vomit) that names an animal is about an animal and is left out.
ANIMAL_WORDS = re.compile(r"\b(birds?|cats?|dogs?|animals?|owls?|pellets?|horses?|cows?|fox(es)?)\b", re.I)
COMMONS_NEEDS = {k: re.compile(rf"\b({v})\b", re.I) for k, v in COMMONS_NEEDS.items()}
# Files that are not a photograph of the thing (art, signs, bins), or not wanted.
COMMONS_NOT_THIS = re.compile(r"\b(art|drawings?|paintings?|logos?|icons?|emoji|sculptures?|toys?|models?|"
                              r"in literature|videos?|audio|microscop\w*|micrograph\w*|beetles?|insects?|fossil\w*|"
                              r"coprolites?|fuel|briquett\w*|museum|caricatur\w*|cartoons?|signs?|containers?|"
                              r"bins?|dispensers?|stations?|coproph\w*|Santorum|statues?|fountains?|interdi\w*|"
                              r"prohibit\w*|forbidden|verboten|vietato|prohibido|notice)\b", re.I)
ENGLISH = re.compile(r"\b(the|a|an|of|in|on|with|and|is|are|from|after|showing|shows)\b", re.I)


def commons_bodily_rows(source, data_dir, categories, prefix, medical):
    """Rows from Commons categories, files under CC BY-SA or GFDL (extra_sources.commons_sa_entries): the category's
    question and answer, and the file's English caption or description as "Write a short description ..."."""
    s, items = commons_session(), []
    per_category = max(5, int((source.cap + source.test) * 1.2) // len(categories))
    for category, (question, answer, body) in categories.items():
        try:
            titles = [t for t in commons_members(s, category, "file") if not COMMONS_NOT_THIS.search(t)]
        except RuntimeError:
            continue
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 3]):
            words = f"{title} {text}"
            if category in COMMONS_NEEDS and not COMMONS_NEEDS[category].search(words.replace("_", " ")):
                continue
            if found >= per_category or COMMONS_NOT_THIS.search(words) or INTIMATE_SITE.search(words) \
                    or NUDE.search(words) or (body and (not is_adult_text(words) or CHILD_WORDS.search(words))):
                continue
            extra = {"split": "", "credit": credit, **({"content": "medical"} if medical else {}),
                     **({"child": True} if CHILD_WORDS.search(words) else {})}
            name = commons_file_name(prefix, title)
            items.append((name, url, dict({"question": question, "answer": answer}, **extra)))
            if medical and ANIMAL_WORDS.search(words):
                continue
            named = category not in COMMONS_NEEDS or COMMONS_NEEDS[category].search(text)
            if text and ENGLISH.search(text) and named:
                items.append((name, url, dict({"question": ALT_TEXT, "answer": text}, **extra)))
            found += 1
        say(f"  Commons {category}: {found} files under CC BY-SA or GFDL")
    if medical:
        for title, url, credit, text in commons_sa_entries(s, list(COMMONS_SA_FILES)):
            question, answer = COMMONS_SA_FILES[title]
            items.append((commons_file_name(prefix, title), url, {"question": question, "answer": answer, "split": "",
                                                                  "credit": credit, "content": "medical"}))
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=2, pause=0.5)


def prepare_commons_bodily_sa(source, data_dir, work, cap):
    """Wikimedia Commons: human stool, the Bristol stool chart, vomit, discoloured and bloody urine, urine bags, blood
    stains and nosebleeds, under CC BY-SA or GFDL. Pictures that may show a person's body only when the file's words
    say the person is an adult."""
    return commons_bodily_rows(source, data_dir, COMMONS_HUMAN, "bodily-sa", True)


def prepare_commons_droppings_sa(source, data_dir, work, cap):
    """Wikimedia Commons: dog, cat, horse and bird droppings and litter boxes, under CC BY-SA or GFDL."""
    return commons_bodily_rows(source, data_dir, COMMONS_ANIMAL, "droppings-sa", False)


# ----------------------------------------------------------------- iNaturalist droppings under other licences

# As packs/bodily_packs.INAT_ANIMALS: (scientific name, the droppings in plain words, the animal, whether it lives
# with people). Only research-grade observations are on GBIF.
INAT_ANIMALS = [
    ("Canis familiaris", "dog poop", "a domestic dog", True),
    ("Felis catus", "cat poop", "a domestic cat", True),
    ("Equus caballus", "horse manure (horse droppings)", "a horse", True),
    ("Equus asinus", "donkey droppings", "a donkey", True),
    ("Bos taurus", "a cow pat (cow dung)", "a cow", True),
    ("Ovis aries", "sheep droppings", "a sheep", True),
    ("Capra hircus", "goat droppings", "a goat", True),
    ("Branta canadensis", "goose droppings", "a Canada goose", False),
    ("Columba livia", "pigeon droppings", "a pigeon", False),
    ("Vulpes vulpes", "fox droppings (fox scat)", "a red fox", False),
    ("Procyon lotor", "raccoon droppings", "a raccoon", False),
    ("Odocoileus virginianus", "deer droppings", "a white-tailed deer", False),
    ("Capreolus capreolus", "deer droppings", "a roe deer", False),
    ("Oryctolagus cuniculus", "rabbit droppings", "a rabbit", False),
    ("Sylvilagus floridanus", "rabbit droppings", "an eastern cottontail rabbit", False),
    ("Erinaceus europaeus", "hedgehog droppings", "a hedgehog", False),
    ("Aves", "bird droppings", "a bird", False),
]
INAT_SINGULAR = {"dog poop", "cat poop", "horse manure (horse droppings)", "a cow pat (cow dung)"}
INAT_LICENCES = {"cc-by-sa": "CC BY-SA", "cc-by-nc": "CC BY-NC", "cc-by-nc-sa": "CC BY-NC-SA",
                 "cc-by-nc-nd": "CC BY-NC-ND"}


def inat_droppings_rows(source, data_dir, licences, prefix):
    """Rows for iNaturalist "Evidence of presence: Scat" observations whose first usable photo's own licence is one
    of licences, shared evenly over the animals: "What is this?" and "What animal left these droppings?". The
    records come from GBIF and the photos from the iNaturalist Open Dataset (inat_gbif.py); iNaturalist's website
    and API are never read."""
    import inat_gbif
    want = int((source.cap + source.test) * 1.1)
    per_animal = max(5, want // len(INAT_ANIMALS) * 2)
    rng, items, names = random.Random(prefix), [], {}
    for latin, words, animal, domestic in INAT_ANIMALS:
        taxon = inat_gbif.taxon(latin)
        if not taxon:
            continue
        found = 0
        for record, media, code, url in inat_gbif.scat_records(taxon, licences, per_animal, rng):
            words_of = " ".join(clean(record.get(k)) for k in ("occurrenceRemarks", "identificationRemarks"))
            if re.search(r"\bdingo", words_of, re.I):
                continue                          # dingoes are filed under Canis familiaris; they are wild
            species = inat_gbif.latin(record)
            who = animal
            common = inat_gbif.english_name(record, names) if words == "bird droppings" and species else ""
            if words == "bird droppings" and common:
                who = f"{sources_article(common)} {common} ({species})"
            elif " " in latin and words != "bird droppings":
                who = f"{animal} ({latin})"
            credit = inat_gbif.credit(record, media, code)
            lead = "This is" if words in INAT_SINGULAR else "These are"
            name = f"{prefix}-{inat_gbif.photo_id(url)}.jpg"
            items.append((name, url, {"question": "What is this?", "answer": f"{lead} {words}, left by {who}.",
                                      "split": "", "credit": credit}))
            items.append((name, url, {"question": "What animal left these droppings?", "split": "",
                                      "answer": f"They look like droppings left by {who}.", "credit": credit}))
            found += 1
        say(f"  iNaturalist (on GBIF) droppings of {latin}: {found}")
    rng.shuffle(items)
    return fetch_pictures(items[:want * 2], os.path.join(data_dir, source.key), workers=4, pause=0.3)


def sources_article(word):
    """ "a" or "an" before a word."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def prepare_inat_droppings_sa(source, data_dir, work, cap):
    """iNaturalist droppings whose photo is CC BY-SA."""
    return inat_droppings_rows(source, data_dir, ("cc-by-sa",), "inatscat-sa")


def prepare_inat_droppings_nc(source, data_dir, work, cap):
    """iNaturalist droppings whose photo is CC BY-NC, CC BY-NC-SA or CC BY-NC-ND."""
    return inat_droppings_rows(source, data_dir, ("cc-by-nc", "cc-by-nc-sa", "cc-by-nc-nd"), "inatscat-nc")


# ----------------------------------------------------------------- what could not be included, and the gaps

BODILY_NOT_INCLUDED = {
    "Korosensei001/fake-feces (Hugging Face)": "pictures made by a computer (\"Synthetic Images\"), not photos.",
    "MSHIT (Kaggle mikian/dog-poop)": "plastic fake dog poop photographed in a studio, not real poop.",
    "Open Images 'Diaper' label": "the photos are mostly babies wearing nappies (a child's body), not nappy contents.",
    "Open Images 'Urine' label": "no photo in the validation, test or train lists has it confirmed.",
    "zhoumiaosen/seeed_poopascoopa_v2 and ishandotsh/poopascoopa_v1 (Hugging Face, Apache-2.0)": "camera frames of "
        "a robot arm picking things up in a lab, with no labels saying what is in each frame.",
    "dikaizm/urine-particle-image-dataset (MIT)": "microscope pictures of urine sediment, not what a person sees.",
    "Bloodstain measurement sets on Mendeley Data (kbb89k5gyg, wvwh3rfdmp and others)": "tables and documents of "
                                                                                       "measurements, not pictures.",
    "Hyperspectral blood-detection sets (TU Dresden; arXiv 2008.10254)": "hyperspectral camera data, not ordinary "
                                                                         "photos.",
    "Veterinary articles in PubMed Central (pet vomit and diarrhoea)": "tried: of about 870 CC BY or CC0 articles "
        "about dogs, cats, rabbits and horses whose figure captions name stool, vomit or urine, only 1 in 200 had a "
        "usable photograph (most are charts); the vet_case_figures pack already holds veterinary case-report "
        "photos.",
    "NIDDK Bristol stool images": "CC BY-NC (seen reused in articles); not found as a downloadable collection.",
    "Wikimedia Commons 'Meconium' and 'Diarrhea' categories": "their photos often show a baby's or a patient's body "
                                                              "with no words saying it is an adult; left out.",
}

# What no open collection covers (November 2026); the owner's describers website and his own-pictures folder can fill
# these.
BODILY_GAPS = [
    "Human stool photos labelled with a Bristol type (1 to 7): no open or downloadable research set; the Commons "
    "chart and the case-report photos (black, bloody, pale stool) are all there is.",
    "Vomit photos: only about a dozen open Commons files and a few case-report photos (coffee-ground or bloody "
    "vomit); no picture set.",
    "Baby stool colours and nappy contents: no open stool-colour card; a few case-report photos of pale stool.",
    "Small cuts, blood on skin, bandages and clothing, and nosebleeds of adults: the Open Images blood, injury and "
    "bandage labels and a few Commons files; no first-aid picture set with an open licence was found.",
    "Pet vomit and diarrhoea: no open set; very few usable veterinary photos.",
]


# ----------------------------------------------------------------- the table

def research(summary):
    """A terms summary that also says it is for personal, non-commercial use (as extra_sources.research)."""
    return summary + " Personal, non-commercial use only."


BODILY_SOURCES = [
    # ---- share-alike
    Source("commons_bodily_sa", "Wikimedia Commons: stool, vomit, urine and blood stains, files under CC BY-SA or "
                                "GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page)",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 300, 10, prepare_commons_bodily_sa, "about 40 MB", content="medical"),
    Source("commons_droppings_sa", "Wikimedia Commons: dog, cat, horse and bird droppings, files under CC BY-SA or "
                                   "GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page)",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 200, 10, prepare_commons_droppings_sa, "about 30 MB"),
    Source("inat_droppings_sa", "iNaturalist: droppings of pets, farm animals, birds and yard animals, photos under "
                                "CC BY-SA (share-alike)",
           "Each photo CC BY-SA (its iNaturalist page)",
           "iNaturalist observers, CC BY-SA, each credited in its row, https://www.inaturalist.org", "share-alike",
           150, 10, prepare_inat_droppings_sa, "about 20 MB"),
    # ---- noncommercial
    Source("inat_droppings_nc", "iNaturalist: droppings of pets, farm animals, birds and yard animals (personal use)",
           "Each photo CC BY-NC, CC BY-NC-SA or CC BY-NC-ND (its iNaturalist page)",
           "iNaturalist observers, CC BY-NC, BY-NC-SA or BY-NC-ND, each credited in its row, "
           "https://www.inaturalist.org", "noncommercial", 2500, 20, prepare_inat_droppings_nc, "about 300 MB",
           terms="https://www.inaturalist.org/pages/terms",
           terms_summary="Each photo's own licence, here CC BY-NC, CC BY-NC-SA or CC BY-NC-ND: use with credit, not "
                         "for commercial purposes."),
    # ---- research (rights not clear)
    Source("bloodstain_patterns", "Blood stain patterns: stills of laboratory videos of blood dripping and swiped "
                                  "onto plastic, card and cloth (personal use)",
           "\"CC BY 4.0\" stated by the uploaders (Mendeley Data 234yvmkcys); the videos are the Midwest Forensics "
           "Resource Center's (Laber, Epstein and Taylor, 2007), whose own terms are not given",
           BSPDS_CREDIT, "research", 44, 4, prepare_bloodstain_patterns,
           "about 600 MB of videos (kept), needs the video extras", content="medical",
           terms="https://data.mendeley.com/datasets/234yvmkcys",
           terms_summary=research("CC BY 4.0 is stated by the people who uploaded the videos, but the videos were "
                                  "made by the Midwest Forensics Resource Center, whose own terms are not given.")),
]

# The collections a picture-making model may learn from: none (the owner may add dog poop on grass if he wants it).
BODILY_PICTURE_MAKING_OK = set()
