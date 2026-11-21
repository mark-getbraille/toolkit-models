"""SIGN-UP collections for the Picture Model Training Kit: collections that need the owner's own free account, key or
request form, downloaded only on the owner's own computer, for his personal use. Nothing here is ever in a ready-made
pack, re-shared, published or put in a product.

Where the keys come from (never from this repository, never written to a log):
  1. Windows user environment variables (Start, type "environment variables", "Edit environment variables for your
     account", New): KAGGLE_USERNAME and KAGGLE_KEY, DVIDS_API_KEY, and the keys other kit files already read
     (EUROPEANA_KEY, DPLA_API_KEY, SI_API_KEY);
  2. or the key file the wizard keeps in the user's own settings folder (KEY_FILE:
     %APPDATA%\\Picture Model Training\\signup-keys.json), filled in its "Sign-up keys" window;
  3. Kaggle only: also the kaggle.json file Kaggle gives (%USERPROFILE%\\.kaggle\\kaggle.json).
use_key_file() copies the key file's keys into this program's own environment (never over a variable already set), so
the existing Europeana, DPLA and Smithsonian entries in other kit files use the owner's own keys too. It runs when this
file is loaded.

Every entry, the first time it runs on a computer, says in plain words where to get its key, the line of the terms the
owner agrees to (quoted, with the address) and what the collection adds (SIGNUP_INFO; explain_once). Without its key
or file it says so in one line and adds nothing (the training carries on).

The collections (SIGNUP_SOURCES), each checked at its source in November 2026:
  research
    dvids_us        DVIDS (Defense Visual Information Distribution Service) photos of the US forces at work: disaster
                    relief, training, ships, aircraft, field hospitals, engineers, with the photographers' own
                    captions (DVIDS_API_KEY). API terms: "All media assets and information accessible via the DVIDS
                    API is free for commercial use", but the cache must follow removals, so it is kept personal.
    kaggle_chess    Kaggle "Chess Positions" (koryakinp, CC0): 100,000 drawn chess boards; the answer lists every
                    piece and its square, read from the file name (KAGGLE_USERNAME and KAGGLE_KEY). The boards and
                    pieces are Chess.com's drawings, so it is research use only and never for picture-making.
    flickr30k       Flickr30k (University of Illinois): 31,783 everyday photos with five descriptions each written by
                    people; a request form, then the owner puts the downloaded files in the sign-up folder
                    (signup_folder("flickr30k")). "non-commercial research and/or educational purposes".
  noncommercial
    dvids_caf       Canadian Armed Forces photos on DVIDS (Crown copyright, personal or public non-commercial use).
    museums_victoria  Museums Victoria Collections (Melbourne): household appliances, radios, televisions, telephones,
                    tools and toys with the museum's own descriptions; only pictures marked public domain or CC BY,
                    BY-SA, BY-NC or BY-NC-SA (no NoDerivatives). No key is needed, but its site refused the machine
                    these entries were made on (403), so it runs only on the owner's computer, slowly (one request
                    every three seconds), and says so clearly if it refuses him too.

  local files (the owner downloads by hand and puts the files in Documents\\Picture Model Training sign-up files\\
  <key>, as zips or unpacked; the kit reads the makers' own labels: LocalFiles, LOCAL_LABEL_FILES, local_ready)
    lisa_traffic_lights  LISA Traffic Light (Kaggle, CC BY-NC-SA 4.0, noncommercial): each light's colour.
    lisa_traffic_signs   LISA Traffic Sign (UC San Diego, academic licence, research): the US sign types marked.
    bdd100k         BDD100K (Berkeley, educational and research use, research): weather, time of day, road users,
                    traffic light colours.
    mapillary_signs Mapillary Traffic Sign Dataset (CC BY-NC-SA 4.0, noncommercial): every sign named.
    mapillary_vistas  Mapillary Vistas (CC BY-NC-SA 4.0, noncommercial): what is in a street scene.
    deepfashion     DeepFashion Category and Attribute Prediction (research agreement): the kind of clothing.
    fastener_sets   Kaggle "The Fasteners" (CC0) and "SortScrews" (Apache 2.0), or a Roboflow set exported by
                    folder: bolts, screws, nuts and washers named by their folder.
    mvtec_d2s       MVTec D2S (CC BY-NC-SA 4.0, noncommercial): supermarket products named.

People: DVIDS and Flickr30k photos show people, and none of these collections is used for picture-making
(SIGNUP_PICTURE_MAKING_OK is empty). Children: a row whose words name a child is marked "child": true (picture-making
leaves it out, and it never is a picture-making collection anyway). Nothing sexual, no crime, prisoners, detainees,
executions or torture (archive_sources.make_rows and LEFT_OUT); war injuries and the dead are marked "content":
"graphic" and used only with the graphic-scenes choice.

Not built, each with its reason, and the review of every not-included list in the kit for personal use
(PERSONAL_REVIEW, with A: worth adding for personal use, B: not useful, C: not allowed even for personal use):
SIGNUP_NOT_INCLUDED and PERSONAL_REVIEW below.

Main parts: SIGNUP_SOURCES, SIGNUP_PICTURE_MAKING_OK, SIGNUP_INFO, SIGNUP_KEYS, KEY_FILE, load_key_file,
save_key_file, get_key, missing_keys, use_key_file, explain_once, signup_folder, one prepare_<key> function per
collection, chess_answer, dvids_answer, victoria_item.

    python -c "import sources, signup_sources"      (from the kit folder: checks the file loads)
"""

import json
import os
import random
import re
import tarfile
import time
import zipfile

import sources
from sources import Source, clean

APP_FOLDER = "Picture Model Training"
DOCUMENTS_FOLDER = "Picture Model Training sign-up files"


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


# ----------------------------------------------------------------- the owner's keys

def key_file():
    """Where the wizard keeps the sign-up keys: the user's own settings folder (%APPDATA%\\Picture Model Training\\
    signup-keys.json), never the kit folder or this repository."""
    return os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_FOLDER, "signup-keys.json")


KEY_FILE = key_file()

# The keys a sign-up collection can use: name -> (what it is, where to get it, in plain words).
SIGNUP_KEYS = {
    "KAGGLE_USERNAME": ("Kaggle user name",
                        "Make a free account at https://www.kaggle.com , then open Settings, API, Create New Token: "
                        "the kaggle.json file it gives has your user name and key."),
    "KAGGLE_KEY": ("Kaggle key",
                   "The key from the same kaggle.json file (Kaggle, Settings, API, Create New Token)."),
    "DVIDS_API_KEY": ("DVIDS API key",
                      "Sign up at https://api.dvidshub.net (Sign up, then create an API application); the key "
                      "starts with key-."),
    "EUROPEANA_KEY": ("Europeana API key",
                      "Ask for a free key at https://pro.europeana.eu/page/get-api ; the kit's Europeana collections "
                      "then use your own key instead of the shared demonstration key."),
    "DPLA_API_KEY": ("DPLA API key",
                     "Ask for a free key at https://pro.dp.la/developers/api-basics ; DPLA e-mails a 32-character "
                     "key. The college and university entries (university_sources.py) use it."),
    "SI_API_KEY": ("Smithsonian (api.data.gov) key",
                   "Ask for a free key at https://api.data.gov/signup/ ; the Smithsonian entries use it."),
}


def load_key_file(path=None):
    """The keys saved in the key file ({} when there is none or it cannot be read). Only names in SIGNUP_KEYS."""
    try:
        with open(path or key_file(), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return {k: str(v).strip() for k, v in (data or {}).items() if k in SIGNUP_KEYS and str(v or "").strip()}


def save_key_file(keys, path=None):
    """Save the keys (empty ones are left out) in the key file, in the user's own settings folder. Never says or logs
    a value. True when saved."""
    path = path or key_file()
    keep = {k: str(v).strip() for k, v in keys.items() if k in SIGNUP_KEYS and str(v or "").strip()}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + ".part", "w", encoding="utf-8") as f:
            json.dump(keep, f, indent=1)
        os.replace(path + ".part", path)
        return True
    except OSError:
        return False


def kaggle_json():
    """{"KAGGLE_USERNAME": ..., "KAGGLE_KEY": ...} from Kaggle's own kaggle.json (in .kaggle in the user's folder),
    or {}."""
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    try:
        with open(os.path.join(home, ".kaggle", "kaggle.json"), encoding="utf-8") as f:
            data = json.load(f)
        return {"KAGGLE_USERNAME": str(data.get("username") or "").strip(),
                "KAGGLE_KEY": str(data.get("key") or "").strip()}
    except (OSError, ValueError, AttributeError):
        return {}


def get_key(name):
    """A key's value: the environment variable, else the key file, else (Kaggle) kaggle.json; "" when none."""
    value = os.environ.get(name, "").strip()
    if not value:
        value = load_key_file().get(name, "")
    if not value and name.startswith("KAGGLE_"):
        value = kaggle_json().get(name, "")
    return value


def missing_keys(names):
    """The names among names that have no value (get_key)."""
    return [n for n in names if not get_key(n)]


def use_key_file():
    """Copy the key file's keys into this program's environment, never over a variable already set, so the kit's
    other entries that read EUROPEANA_KEY, DPLA_API_KEY or SI_API_KEY use the owner's own keys. The names copied."""
    copied = []
    for name, value in load_key_file().items():
        if not os.environ.get(name, "").strip():
            os.environ[name] = value
            copied.append(name)
    return copied


use_key_file()


def signup_folder(key):
    """The folder where the owner puts the files of a request-form collection: Documents\\Picture Model Training
    sign-up files\\<key> (made when missing)."""
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    folder = os.path.join(home, "Documents", DOCUMENTS_FOLDER, key)
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        pass
    return folder


# ----------------------------------------------------------------- what each entry says the first time

# key -> {"keys": names it needs, "where": where to get them, "terms": the terms line quoted, "terms_url",
#         "adds": what the collection adds}
SIGNUP_INFO = {
    "dvids_us": {
        "keys": ["DVIDS_API_KEY"],
        "where": "Sign up at https://api.dvidshub.net (Sign up at the top right), create an API application, and "
                 "set DVIDS_API_KEY to its key (it starts with key-).",
        "terms": "'All media assets and information accessible via the DVIDS API is free for commercial use.' and "
                 "'You must use commercially reasonable efforts to cause Your API Client to update cached results "
                 "upon any changes in asset metadata. For example, if a video is removed from the DVIDS service, "
                 "cached results and assets shall be removed from Your cache.'",
        "terms_url": "https://api.dvidshub.net/docs/tos",
        "adds": "Photos of US forces at work with the photographers' own captions: disaster relief, rescues, field "
                "hospitals, ships, aircraft, engineers, training in snow and desert.",
    },
    "dvids_caf": {
        "keys": ["DVIDS_API_KEY"],
        "where": "The same DVIDS_API_KEY as dvids_us (https://api.dvidshub.net).",
        "terms": "Canadian Armed Forces imagery is Crown copyright, which allows 'personal or public "
                 "non-commercial use'.",
        "terms_url": "https://www.canada.ca/en/department-national-defence/corporate/terms-conditions.html",
        "adds": "Canadian Armed Forces photos on DVIDS: exercises, rescues, ships and aircraft, with captions.",
    },
    "kaggle_chess": {
        "keys": ["KAGGLE_USERNAME", "KAGGLE_KEY"],
        "where": "Make a free account at https://www.kaggle.com , open Settings, API, Create New Token, and either "
                 "keep the kaggle.json it gives in the .kaggle folder of your user folder or set KAGGLE_USERNAME and "
                 "KAGGLE_KEY to the two values in it.",
        "terms": "The dataset's page gives its licence as 'CC0: Public Domain', and its maker writes 'Chess.com for "
                 "providing images of pieces and boards.' Your Kaggle account also comes with Kaggle's own terms "
                 "(https://www.kaggle.com/terms), which you accept when you sign up.",
        "terms_url": "https://www.kaggle.com/datasets/koryakinp/chess-positions",
        "adds": "Drawn chess boards: the answer names every piece and its square, so the describer can read a chess "
                "diagram out.",
    },
    "flickr30k": {
        "keys": [],
        "where": "Fill in the request form at https://forms.illinois.edu/sec/229675 (from "
                 "https://shannon.cs.illinois.edu/DenotationGraph/ ). Put the files it gives you "
                 "(flickr30k-images.tar.gz and flickr30k.tar.gz, or the unpacked flickr30k-images folder and "
                 "results_20130124.token) in Documents\\Picture Model Training sign-up files\\flickr30k.",
        "terms": "'Use of the images must abide by the Flickr Terms of Use. We do not own the copyright of the "
                 "images. They are solely provided at the link below for researchers and educators who wish to use "
                 "the dataset for non-commercial research and/or educational purposes.'",
        "terms_url": "https://shannon.cs.illinois.edu/DenotationGraph/",
        "adds": "Everyday photos of people doing things, each described in a sentence by people.",
    },
    "museums_victoria": {
        "keys": [],
        "where": "No key: it downloads from https://collections.museumsvictoria.com.au/api on your computer, one "
                 "request every three seconds (its robots.txt allows the API).",
        "terms": "Each picture has its own licence on its record; only those marked Public Domain or CC BY, BY-SA, "
                 "BY-NC or BY-NC-SA are taken (never 'All Rights Reserved' or NoDerivatives).",
        "terms_url": "https://collections.museumsvictoria.com.au/about",
        "adds": "Household appliances, radios, televisions, telephones, cameras, tools and toys with the museum's "
                "own descriptions.",
    },
    # The local-file entries: the owner downloads by hand and puts the files in the entry's sign-up folder.
    "lisa_traffic_lights": {
        "keys": [],
        "where": "Sign in to Kaggle (a free account) and press Download on "
                 "https://www.kaggle.com/datasets/mbornoe/lisa-traffic-light-dataset (archive.zip, about 5.2 GB). Put "
                 "the zip, or what it unpacks to, in Documents\\Picture Model Training sign-up files\\"
                 "lisa_traffic_lights.",
        "terms": "The dataset's Kaggle page gives its licence as 'CC BY-NC-SA 4.0' (non-commercial, with credit, "
                 "anything made from it under the same terms). Kaggle's own terms (https://www.kaggle.com/terms) "
                 "come with your account.",
        "terms_url": "https://www.kaggle.com/datasets/mbornoe/lisa-traffic-light-dataset",
        "adds": "Street photos from San Diego, day and night, with every traffic light's colour (red, yellow, green, "
                "left-turn arrows) as its makers marked it.",
    },
    "lisa_traffic_signs": {
        "keys": [],
        "where": "Open https://cvrr.ucsd.edu/lisa-traffic-signs-dataset , accept its academic licence agreement and "
                 "download the dataset (signDatabasePublicFramesOnly.zip). Put the zip, or what it unpacks to, in "
                 "Documents\\Picture Model Training sign-up files\\lisa_traffic_signs.",
        "terms": "The page says the dataset is 'released under academic license agreement': research and personal "
                 "use only.",
        "terms_url": "https://cvrr.ucsd.edu/lisa-traffic-signs-dataset",
        "adds": "US road signs in street photos (stop, yield, speed limits, pedestrian crossings, school zones and "
                "about 40 more kinds), named as its makers marked them.",
    },
    "bdd100k": {
        "keys": [],
        "where": "Make a free account at https://bdd-data.berkeley.edu , accept its licence, and download '100K "
                 "Images' (bdd100k_images_100k.zip) and the detection labels (bdd100k_labels_images_trainval.zip "
                 "or bdd100k_det_20_labels_trainval.zip). Put the zips, or what they unpack to, in "
                 "Documents\\Picture Model Training sign-up files\\bdd100k.",
        "terms": "In short: BDD100K may be used for educational, research and not-for-profit purposes; commercial "
                 "use is reserved for Berkeley DeepDrive's members. Read the licence on the download page before "
                 "you accept it.",
        "terms_url": "https://bdd-data.berkeley.edu",
        "adds": "Driving photos from New York and the San Francisco Bay Area with the weather, the time of day, the "
                "kind of road, the cars, people and bicycles marked, and the colour of each traffic light.",
    },
    "mapillary_signs": {
        "keys": [],
        "where": "Make a free Mapillary account, open https://www.mapillary.com/dataset/trafficsign , accept the "
                 "terms and download the fully annotated set (the annotations zip and the images zips). Put the "
                 "zips, or what they unpack to, in Documents\\Picture Model Training sign-up files\\"
                 "mapillary_signs.",
        "terms": "Released under CC BY-NC-SA 4.0 for research: non-commercial, with credit, anything made from it "
                 "under the same terms.",
        "terms_url": "https://www.mapillary.com/dataset/trafficsign",
        "adds": "Street photos from around the world with every traffic sign named (stop, no entry, speed limits, "
                "warnings and information signs).",
    },
    "mapillary_vistas": {
        "keys": [],
        "where": "Make a free Mapillary account, open https://www.mapillary.com/dataset/vistas , accept the terms "
                 "and download the dataset (version 2.0). Put the zip, or what it unpacks to (with config_v2.0.json "
                 "and the training and validation folders), in Documents\\Picture Model Training sign-up files\\"
                 "mapillary_vistas.",
        "terms": "Released under CC BY-NC-SA 4.0 for research: non-commercial, with credit, anything made from it "
                 "under the same terms.",
        "terms_url": "https://www.mapillary.com/dataset/vistas",
        "adds": "Street scenes from around the world with what is in them as its makers outlined it: road, "
                "sidewalk, crosswalk, curb, cars, poles, traffic lights and signs, people.",
    },
    "deepfashion": {
        "keys": [],
        "where": "Read https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html , follow its link to the Category and "
                 "Attribute Prediction Benchmark and download, from its Google Drive folder, img.zip (Img) and the "
                 "Anno_coarse folder (list_category_cloth.txt and list_category_img.txt). Put them in "
                 "Documents\\Picture Model Training sign-up files\\deepfashion.",
        "terms": "DeepFashion is for non-commercial research only, under its makers' agreement (on its page).",
        "terms_url": "https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html",
        "adds": "Clothing photos (shop and street) with each garment's kind: blouse, T-shirt, jeans, dress, "
                "jacket and about 45 more.",
    },
    "fastener_sets": {
        "keys": [],
        "where": "Download fastener sets sorted into one folder per kind, and put each set in a folder of its own "
                 "(named after the set) in Documents\\Picture Model Training sign-up files\\fastener_sets. Checked "
                 "in November 2026: Kaggle 'The Fasteners' (https://www.kaggle.com/datasets/alexandrparkhomenko/"
                 "the-fasteners, marked CC0) and 'SortScrews' (https://www.kaggle.com/datasets/terryfuatatc/"
                 "sortscrews, Apache 2.0, 'We collected 560 images of 6 types of screws'), with a free Kaggle "
                 "account. A Roboflow Universe set works too when exported in 'Folder Structure' format, but take "
                 "only a set whose page says the photos are its makers' own and gives an open licence.",
        "terms": "Each set's own licence on its page (CC0 and Apache 2.0 for the two Kaggle sets named); Kaggle's "
                 "and Roboflow's own terms come with your account.",
        "terms_url": "https://www.kaggle.com/datasets/terryfuatatc/sortscrews",
        "adds": "Close photos of single bolts, screws, nuts and washers, each named by the folder its makers "
                "sorted it into.",
    },
    "mvtec_d2s": {
        "keys": [],
        "where": "Open https://www.mvtec.com/company/research/datasets/mvtec-d2s , fill in the download form and "
                 "download the images and the annotations. Unpack them (7-Zip opens .tar.xz files) into "
                 "Documents\\Picture Model Training sign-up files\\mvtec_d2s, so that the D2S_*.json "
                 "annotation files and the images folder are there.",
        "terms": "'The data is released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 "
                 "International License' (CC BY-NC-SA 4.0).",
        "terms_url": "https://www.mvtec.com/company/research/datasets/mvtec-d2s",
        "adds": "Supermarket products photographed on a tray, each one named: fruit and vegetables, bottles, cans, "
                "boxes and bags of 60 kinds.",
    },
}


def explained_file(data_dir):
    """The file that remembers which entries have explained themselves on this computer."""
    return os.path.join(data_dir, "signup-explained.json")


def explain_once(source, data_dir):
    """The first time an entry runs on this computer, say where to get its key, the terms line it agrees to (quoted,
    with the address) and what it adds; later, nothing. True when it was said now."""
    info = SIGNUP_INFO.get(source.key)
    if not info:
        return False
    path = explained_file(data_dir)
    try:
        with open(path, encoding="utf-8") as f:
            done = set(json.load(f))
    except (OSError, ValueError, TypeError):
        done = set()
    if source.key in done:
        return False
    say(f"  {source.name}: a sign-up collection, for your personal use only. Where to get it: {info['where']} "
        f"The terms you agree to ({info['terms_url']}): {info['terms']} What it adds: {info['adds']}")
    done.add(source.key)
    try:
        os.makedirs(data_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sorted(done), f)
    except OSError:
        pass
    return True


def keys_or_skip(source, data_dir):
    """Explain the entry the first time; then {name: value} of its keys, or None (said in one line) when one is
    missing, so the entry adds nothing and the training carries on."""
    explain_once(source, data_dir)
    info = SIGNUP_INFO[source.key]
    missing = missing_keys(info["keys"])
    if missing:
        say(f"  {source.key}: no {' or '.join(missing)} on this computer, so it is left out. {info['where']}")
        return None
    return {n: get_key(n) for n in info["keys"]}


# ----------------------------------------------------------------- DVIDS (US and Canadian forces)

DVIDS = "https://api.dvidshub.net/"
DVIDS_TOPICS = ["disaster relief", "humanitarian assistance", "search and rescue", "field hospital", "flood",
                "wildfire", "hurricane", "aircraft carrier", "helicopter", "cargo aircraft", "parachute", "convoy",
                "engineers construction", "bridge", "military working dog", "dining facility", "cooking",
                "physical training", "snow training", "desert training", "jungle training", "boat", "submarine",
                "ship at sea", "flight deck", "maintenance", "medical training", "dental", "band", "firefighting",
                "vehicle", "radar", "satellite communications", "weather", "range", "obstacle course"]
CAF = re.compile(r"\b(canadian armed forces|canadian army|royal canadian (navy|air force)|canadian forces|"
                 r"combat camera|forces arm[ée]es canadiennes)\b", re.I)
# Records left out: ceremonies and portraits of named people, prisoners and detainees, the dead's remains.
DVIDS_LEFT_OUT = re.compile(r"\b(portraits?|head ?shots?|official photo|awards?|promot\w+|change of command|"
                            r"assumption of command|retirement|re-?enlist\w*|oath|ceremon\w+|funerals?|remains|"
                            r"dignified transfer|detainees?|prisoners?|inmates?|captives?|interrogat\w*|"
                            r"arrest\w*|suspects?|autops\w+|nud\w+|naked|sex\w*)\b", re.I)
# The credit sentence DVIDS captions end with: "(U.S. Army photo by Sgt. ...)".
DVIDS_CREDIT = re.compile(r"\((?:U\.S\.|US|Canadian|DND|Photo)[^()]{0,160}\)\s*$|\s*Photo (?:by|courtesy)[^.]*\.?\s*$",
                          re.I)


def dvids_answer(record):
    """The caption of a DVIDS image record (its description, else its title) without the photo credit, at most about
    80 words; "" when under six words."""
    text = clean(record.get("description") or record.get("short_description") or record.get("title"))
    text = DVIDS_CREDIT.sub("", text).strip()
    text = re.sub(r"https?://\S+", "", text)
    words = text.split()
    if len(words) < 6:
        return ""
    text = " ".join(words[:80])
    return text if text.endswith((".", "!", "?")) else text + "."


def dvids_place(record):
    """'City, State, Country' of a DVIDS record (search or asset form), or ""."""
    loc = record.get("location") if isinstance(record.get("location"), dict) else record
    parts = [clean(loc.get(k)) for k in ("city", "state", "country")]
    return ", ".join(dict.fromkeys(p for p in parts if p))


def dvids_is_caf(record):
    """True when a DVIDS record is Canadian Armed Forces material (its unit, credit or caption says so)."""
    credit = record.get("credit")
    if isinstance(credit, list):
        credit = " ".join(str(c.get("name") or "") if isinstance(c, dict) else str(c) for c in credit)
    words = " ".join(str(x or "") for x in (record.get("unit_name"), record.get("branch"), credit,
                                             record.get("description"), record.get("title")))
    return bool(CAF.search(words))


def dvids_items(key, canadian, want, seed, get=None, pause=1.0):
    """[(file name, picture address, row)] of DVIDS image records: Canadian Armed Forces ones when canadian, the
    others when not; found by DVIDS_TOPICS, each record read in full with the asset API. get(url, params) gives the
    JSON (archive_sources.get_json by default)."""
    import archive_sources
    if get is None:
        s = archive_sources.session()

        def get(url, params):
            """DVIDS JSON through the shared session."""
            return archive_sources.get_json(s, url, params)
    rng = random.Random(seed)
    topics = list(DVIDS_TOPICS)
    rng.shuffle(topics)
    items, seen = [], set()
    for topic in topics:
        if len(items) >= want:
            break
        query = f"Canadian Armed Forces {topic}" if canadian else topic
        page = rng.randint(1, 3)
        found = get(DVIDS + "search", {"api_key": key, "q": query, "type[]": "image", "max_results": 50,
                                       "page": page}) or {}
        got = 0
        for hit in found.get("results") or []:
            if len(items) >= want:
                break
            asset = str(hit.get("id") or "")
            if not asset.startswith("image:") or asset in seen:
                continue
            seen.add(asset)
            if pause:
                time.sleep(pause)
            record = (get(DVIDS + "asset", {"api_key": key, "id": asset}) or {}).get("results") or {}
            if not record or dvids_is_caf(record) != canadian:
                continue
            words = f"{record.get('title') or ''} {record.get('description') or ''} {record.get('keywords') or ''}"
            answer, url = dvids_answer(record), str(record.get("image") or "")
            if DVIDS_LEFT_OUT.search(words) or not answer or not url.startswith("http"):
                continue
            credit = record.get("credit")
            who = ", ".join(" ".join(x for x in (c.get("rank"), c.get("name")) if x) for c in credit
                            if isinstance(c, dict)) if isinstance(credit, list) else clean(credit)
            line = (f"{clean(record.get('title'))[:120]}, {who or 'DVIDS'}, {record.get('unit_name') or ''}, via DVIDS, "
                    f"{record.get('url') or ''}")
            name = f"dvids-{asset.split(':')[1]}.jpg"
            rows = archive_sources.make_rows(name, url, answer, line, dvids_place(record))
            items += rows
            got += 1 if rows else 0
        say(f"  DVIDS '{query}': {got} photos")
    return items


def prepare_dvids(source, data_dir, canadian, seed):
    """One DVIDS entry: explained the first time; the key; the records (dvids_items); the pictures fetched gently."""
    keys = keys_or_skip(source, data_dir)
    if keys is None:
        return []
    from more_sources import fetch_shared
    want = int((source.cap + source.test) * 1.2) + 2
    items = dvids_items(keys["DVIDS_API_KEY"], canadian, want, seed)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_dvids_us(source, data_dir, work, cap):
    """DVIDS photos of the US forces (not Canadian ones)."""
    return prepare_dvids(source, data_dir, False, 731)


def prepare_dvids_caf(source, data_dir, work, cap):
    """DVIDS photos of the Canadian Armed Forces."""
    return prepare_dvids(source, data_dir, True, 732)


# ----------------------------------------------------------------- Kaggle: Chess Positions

KAGGLE_DOWNLOAD = "https://www.kaggle.com/api/v1/datasets/download/"
CHESS_DATASET = "koryakinp/chess-positions"
CHESS_QUESTION = "Describe this chess position."
PIECES = {"k": ("king", "kings"), "q": ("queen", "queens"), "r": ("rook", "rooks"), "b": ("bishop", "bishops"),
          "n": ("knight", "knights"), "p": ("pawn", "pawns")}


def listed(words):
    """'a', 'a and b', 'a, b and c'."""
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


def chess_answer(name):
    """The answer for one Chess Positions picture, read from its file name (the board in Forsyth-Edwards notation with
    dashes for slashes, from the 8th rank down: "1b1B1b2-2pK2q1-..."); "" when the name is not a board."""
    board = os.path.splitext(os.path.basename(name))[0]
    ranks = board.split("-")
    if len(ranks) != 8:
        return ""
    found = {"white": {}, "black": {}}
    for i, rank in enumerate(ranks):
        file = 0
        for ch in rank:
            if ch.isdigit():
                file += int(ch)
                continue
            if ch.lower() not in PIECES or file > 7:
                return ""
            colour = "white" if ch.isupper() else "black"
            found[colour].setdefault(ch.lower(), []).append(f"{'abcdefgh'[file]}{8 - i}")
            file += 1
        if file != 8:
            return ""
    total = sum(len(v) for side in found.values() for v in side.values())
    parts = []
    for colour in ("white", "black"):
        said = []
        for piece in "kqrbnp":
            squares = sorted(found[colour].get(piece, []))
            if squares:
                one, many = PIECES[piece]
                said.append(f"{one if len(squares) == 1 else many} on {listed(squares)}")
        parts.append(f"{colour.capitalize()}: {'; '.join(said) if said else 'no pieces'}.")
    return f"A diagram of a chess board with {total} pieces. " + " ".join(parts)


def kaggle_download(dataset, path, keys, get=None):
    """Download a whole Kaggle dataset (its zip) to path with the owner's Kaggle user name and key, carrying on from
    a part already there; True when it is there. get(url, auth=, headers=, stream=, timeout=) is requests.get by
    default. Never says the key."""
    if os.path.exists(path):
        return True
    if get is None:
        import requests
        get = requests.get
    part = path + ".part"
    done = os.path.getsize(part) if os.path.exists(part) else 0
    headers = {"User-Agent": sources.USER_AGENT, **({"Range": f"bytes={done}-"} if done else {})}
    with get(KAGGLE_DOWNLOAD + dataset, auth=(keys["KAGGLE_USERNAME"], keys["KAGGLE_KEY"]), headers=headers,
             stream=True, timeout=120) as r:
        if r.status_code in (401, 403):
            say(f"  Kaggle refused the download of {dataset} ({r.status_code}): check KAGGLE_USERNAME and KAGGLE_KEY, "
                "and open the dataset's page once while signed in.")
            return False
        r.raise_for_status()
        if done and r.status_code != 206:
            done = 0
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(part, "ab" if done else "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    os.replace(part, path)
    return True


def chess_rows(zip_path, folder, want, seed):
    """Rows of up to want pictures from the Chess Positions zip at zip_path, made smaller into folder; the pictures
    of its "test" folder are marked "test"."""
    rows = []
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith((".jpeg", ".jpg", ".png")) and chess_answer(n)]
        rng = random.Random(seed)
        rng.shuffle(names)
        os.makedirs(folder, exist_ok=True)
        for n in names[:want]:
            target = os.path.join(folder, os.path.splitext(os.path.basename(n))[0][:100] + ".jpg")
            if not sources.have(target) and not sources.smaller(z.read(n), target):
                continue
            split = "test" if "/test/" in f"/{n.lower()}" else ""
            rows.append({"question": CHESS_QUESTION, "answer": chess_answer(n), "split": split, "picture": target,
                         "credit": f"Chess Positions by Pavel Koryakin (Kaggle {CHESS_DATASET}, CC0), boards and "
                                   "pieces drawn by Chess.com"})
    return rows


def prepare_kaggle_chess(source, data_dir, work, cap):
    """Kaggle Chess Positions: the zip (about 4.3 GB, kept in the downloads folder) with the owner's Kaggle key, then
    the boards with their pieces read from the file names."""
    keys = keys_or_skip(source, data_dir)
    if keys is None:
        return []
    zip_path = os.path.join(work, source.key, "chess-positions.zip")
    if not kaggle_download(CHESS_DATASET, zip_path, keys):
        return []
    return chess_rows(zip_path, os.path.join(data_dir, source.key), cap + source.test, 741)


# ----------------------------------------------------------------- Flickr30k (request form, local files)

def flickr30k_captions(folder):
    """{picture file name: [descriptions]} from the files in folder (and below): results_20130124.token
    ("1000092795.jpg#0<TAB>Two young guys ..."), inside flickr30k.tar.gz too, or a results.csv
    ("image_name| comment_number| comment")."""
    captions = {}

    def take(lines):
        """Read caption lines in either layout."""
        for line in lines:
            line = line.strip()
            if "\t" in line and "#" in line.split("\t")[0]:
                name, text = line.split("\t", 1)
                captions.setdefault(name.split("#")[0].strip(), []).append(clean(text))
            elif line.count("|") >= 2 and not line.lower().startswith("image_name"):
                name, _number, text = line.split("|", 2)
                captions.setdefault(name.strip(), []).append(clean(text))

    for root, _dirs, files in os.walk(folder):
        for f in files:
            path = os.path.join(root, f)
            low = f.lower()
            if low.endswith(".token") or low == "results.csv":
                with open(path, encoding="utf-8", errors="replace") as fh:
                    take(fh)
            elif low == "flickr30k.tar.gz":
                try:
                    with tarfile.open(path) as t:
                        for m in t.getmembers():
                            if m.name.lower().endswith(".token"):
                                take(t.extractfile(m).read().decode("utf-8", "replace").splitlines())
                except (OSError, tarfile.TarError):
                    say(f"  flickr30k: {f} could not be read.")
    return captions


def flickr30k_answer(texts):
    """The longest of a photo's descriptions as a sentence (people's own words), or ""."""
    texts = [t for t in texts if len(t.split()) >= 5]
    if not texts:
        return ""
    text = max(texts, key=len).strip()
    text = text[0].upper() + text[1:]
    return text if text.endswith((".", "!", "?")) else text + "."


def flickr30k_pictures(folder, wanted, keep):
    """{file name: picture bytes path} for the wanted file names: loose pictures anywhere under folder, else read out
    of an image archive there (flickr30k-images.tar.gz, .tgz or .zip) into keep (the originals, kept unchanged)."""
    found = {}
    for root, _dirs, files in os.walk(folder):
        for f in files:
            if f in wanted and f not in found:
                found[f] = os.path.join(root, f)
    left = set(wanted) - set(found)
    if not left:
        return found
    os.makedirs(keep, exist_ok=True)
    for f in list(left):
        if os.path.exists(os.path.join(keep, f)):
            found[f] = os.path.join(keep, f)
            left.discard(f)
    for root, _dirs, files in os.walk(folder):
        for f in files:
            if not left:
                return found
            path, low = os.path.join(root, f), f.lower()
            try:
                if low.endswith((".tar.gz", ".tgz", ".tar")) and low != "flickr30k.tar.gz":
                    with tarfile.open(path) as t:
                        for m in t:
                            base = os.path.basename(m.name)
                            if m.isfile() and base in left:
                                with open(os.path.join(keep, base), "wb") as out:
                                    out.write(t.extractfile(m).read())
                                found[base] = os.path.join(keep, base)
                                left.discard(base)
                elif low.endswith(".zip"):
                    with zipfile.ZipFile(path) as z:
                        for n in z.namelist():
                            base = os.path.basename(n)
                            if base in left:
                                with open(os.path.join(keep, base), "wb") as out:
                                    out.write(z.read(n))
                                found[base] = os.path.join(keep, base)
                                left.discard(base)
            except (OSError, tarfile.TarError, zipfile.BadZipFile):
                say(f"  flickr30k: {f} could not be read.")
    return found


def flickr30k_rows(folder, data_dir, work, want, seed):
    """Rows of up to want Flickr30k photos from the owner's files in folder (see flickr30k_captions and
    flickr30k_pictures); [] (said) when the files are not there."""
    import archive_sources
    captions = flickr30k_captions(folder)
    if not captions:
        say(f"  flickr30k: no description file (results_20130124.token or flickr30k.tar.gz) in {folder}, so it is "
            f"left out. {SIGNUP_INFO['flickr30k']['where']}")
        return []
    names = sorted(captions)
    random.Random(seed).shuffle(names)
    chosen = names[:int(want * 1.1) + 2]
    pictures = flickr30k_pictures(folder, set(chosen), os.path.join(work, "flickr30k"))
    if not pictures:
        say(f"  flickr30k: the descriptions are there but no photos (flickr30k-images.tar.gz or the "
            f"flickr30k-images folder) in {folder}, so it is left out.")
        return []
    out_folder = os.path.join(data_dir, "flickr30k")
    os.makedirs(out_folder, exist_ok=True)
    rows = []
    for name in chosen:
        if name not in pictures or len(rows) >= want:
            continue
        answer = flickr30k_answer(captions[name])
        made = archive_sources.make_rows(name, "", answer, "Flickr30k (Young, Lai, Hodosh and Hockenmaier, "
                                         "University of Illinois), a photo from Flickr; descriptions by people",
                                         "") if answer else []
        if not made:
            continue
        target = os.path.join(out_folder, os.path.splitext(name)[0] + ".jpg")
        if not sources.have(target):
            with open(pictures[name], "rb") as f:
                if not sources.smaller(f.read(), target):
                    continue
        rows.append(dict(made[0][2], picture=target))
    return rows


def prepare_flickr30k(source, data_dir, work, cap):
    """Flickr30k from the files the owner received through the request form."""
    explain_once(source, data_dir)
    return flickr30k_rows(signup_folder("flickr30k"), data_dir, work, cap + source.test, 751)


# ----------------------------------------------------------------- Museums Victoria (refused the build machine)

VICTORIA = "https://collections.museumsvictoria.com.au/api/search"
VICTORIA_TOPICS = ["toaster", "electric kettle", "radio", "television", "telephone", "mobile phone", "camera",
                   "sewing machine", "vacuum cleaner", "electric iron", "refrigerator", "washing machine", "mixer",
                   "typewriter", "computer", "calculator", "clock", "lamp", "heater", "fan", "hair dryer",
                   "record player", "cassette", "game", "toy", "kitchen utensil", "saucepan", "tool", "drill",
                   "wheelchair", "hearing aid", "spectacles"]
VICTORIA_OK = re.compile(r"public domain|\bcc ?by\b(?![- ]?(nc[- ]?)?nd)|attribution(?!.*no ?deriv)", re.I)
VICTORIA_LEFT_OUT = re.compile(r"\b(nud\w*|naked|sex\w*|erotic\w*|weapons?|guns?|rifles?|ammunition|crime|"
                               r"prisons?|police|aboriginal|torres strait|human remains|skulls?|portraits?)\b", re.I)


class Refused(Exception):
    """The museum's server refused this computer (said once, then the entry stops)."""


def victoria_item(record):
    """(file name, picture address, answer, credit) of one Museums Victoria record with a picture under an allowed
    licence and the museum's own description of six words or more, or None."""
    if str(record.get("recordType") or "item") != "item":
        return None
    text = clean(record.get("physicalDescription") or record.get("objectSummary") or record.get("summary"))
    text = re.sub(r"<[^>]+>", "", text)
    title = clean(record.get("displayTitle") or record.get("objectName"))
    if VICTORIA_LEFT_OUT.search(f"{title} {text} {record.get('category') or ''}"):
        return None
    for media in record.get("media") or []:
        if not isinstance(media, dict) or media.get("type") != "image":
            continue
        licence = media.get("licence") or {}
        name = clean(licence.get("name") or licence.get("shortName")) if isinstance(licence, dict) else clean(licence)
        if not VICTORIA_OK.search(name) or re.search(r"all rights reserved", name, re.I):
            continue
        url = ((media.get("large") or {}).get("uri") or (media.get("medium") or {}).get("uri") or "")
        if not url.startswith("http"):
            continue
        answer = f"{title}. {text}" if title and title.lower()[:30] not in text.lower() else text
        words = answer.split()
        if len(words) < 6:
            return None
        answer = " ".join(words[:90])
        answer = answer if answer.endswith((".", "!", "?")) else answer + "."
        rid = re.sub(r"\W+", "-", str(record.get("id") or title))[:60]
        credit = (f"{title[:120]}, Museums Victoria, {name}, "
                  f"https://collections.museumsvictoria.com.au/{record.get('id') or ''}")
        return f"mv-{rid}.jpg", url, answer, credit
    return None


def victoria_items(want, seed, get=None, pause=3.0):
    """[(file name, picture address, row)] from the Museums Victoria API, one request every pause seconds; raises
    Refused when the museum refuses this computer. get(url, params) gives (status, JSON)."""
    import archive_sources
    if get is None:
        import requests
        s = requests.Session()
        s.headers["User-Agent"] = sources.USER_AGENT

        def get(url, params):
            """(status, JSON or None) of one API request."""
            try:
                r = s.get(url, params=params, timeout=90)
                return r.status_code, (r.json() if r.status_code == 200 else None)
            except Exception:  # noqa: BLE001 - counted as no answer
                return 0, None
    rng = random.Random(seed)
    topics = list(VICTORIA_TOPICS)
    rng.shuffle(topics)
    items, seen = [], set()
    for topic in topics:
        if len(items) >= want:
            break
        if pause:
            time.sleep(pause)
        status, data = get(VICTORIA, {"query": topic, "hasimages": "yes", "recordtype": "item", "perpage": 100})
        if status in (401, 403, 429):
            raise Refused(f"Museums Victoria answered {status}")
        got = 0
        for record in data or []:
            found = victoria_item(record) if isinstance(record, dict) else None
            if not found or found[0] in seen:
                continue
            seen.add(found[0])
            rows = archive_sources.make_rows(found[0], found[1], found[2], found[3])
            items += rows
            got += 1 if rows else 0
        say(f"  Museums Victoria '{topic}': {got} objects")
    return items


def prepare_museums_victoria(source, data_dir, work, cap):
    """Museums Victoria objects, politely; a clear message when the museum refuses this computer."""
    explain_once(source, data_dir)
    try:
        items = victoria_items(cap + source.test + 10, 761)
    except Refused as e:
        say(f"  museums_victoria: {e}: the museum's server refused this computer, as it refused the machine these "
            "entries were made on. It is left out; nothing else is affected. It can be tried again another day.")
        return []
    return sources.fetch_pictures(items, os.path.join(data_dir, source.key), workers=1, pause=3.0)


# ----------------------------------------------------------------- local-file entries (the owner downloads by hand)

# Each of these collections is behind an account, a licence the owner accepts himself, or a download form, so the
# kit never downloads it. The owner downloads the files by hand (SIGNUP_INFO[key]["where"] says from where and
# which files) and puts them, as they came (zip files) or unpacked, in Documents\Picture Model Training sign-up
# files\<key>. The kit then reads the labels the makers wrote and turns them into answers; nothing is guessed from a
# picture. A .tar, .tar.gz or .tar.xz archive must be unpacked first (7-Zip does it), because a tar cannot be read
# piece by piece.

class LocalFiles:
    """The files in a sign-up folder: loose files anywhere under it, and the files inside every .zip there, each by
    its path inside (with "/" between folders). read(name) gives a file's bytes. Zip files are read piece by piece,
    so a large one is never unpacked."""

    def __init__(self, folder):
        """Index every file under folder (zip files are opened, not unpacked)."""
        self.where, self.zips = {}, []
        for root, _dirs, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                rel = os.path.relpath(path, folder).replace(os.sep, "/")
                if f.lower().endswith(".zip"):
                    try:
                        z = zipfile.ZipFile(path)
                    except (OSError, zipfile.BadZipFile):
                        say(f"  {f} could not be read (is it a whole download?).")
                        continue
                    self.zips.append(z)
                    for n in z.namelist():
                        if not n.endswith("/"):
                            self.where.setdefault(n, (z, n))
                else:
                    self.where.setdefault(rel, (None, path))
        self.by_base = {}
        for name in self.where:
            self.by_base.setdefault(name.rsplit("/", 1)[-1], name)

    def names(self):
        """Every file's path, sorted."""
        return sorted(self.where)

    def find(self, pattern):
        """The paths whose last part matches the regular expression pattern (case ignored), sorted."""
        rx = re.compile(pattern, re.I)
        return [n for n in self.names() if rx.search(n.rsplit("/", 1)[-1])]

    def named(self, base):
        """The path of a file by its last part ("frame_00001.jpg"), or None."""
        return self.by_base.get(base)

    def read(self, name):
        """The bytes of a file by its path."""
        z, inner = self.where[name]
        if z is not None:
            return z.read(inner)
        with open(inner, "rb") as f:
            return f.read()

    def text(self, name):
        """A text file's text (UTF-8, with any byte-order mark dropped)."""
        return self.read(name).decode("utf-8-sig", "replace")


def local_ready(key):
    """True when the sign-up folder of a local-file entry holds the file its makers' labels come in
    (LOCAL_LABEL_FILES), loose or inside a zip whose name says so, or any zip at all (its inside is read later)."""
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    folder = os.path.join(home, "Documents", DOCUMENTS_FOLDER, key)
    rx = re.compile(LOCAL_LABEL_FILES[key], re.I)
    return os.path.isdir(folder) and any(rx.search(f) or f.lower().endswith(".zip")
                                         for _r, _d, files in os.walk(folder) for f in files)


def local_files_or_skip(source, data_dir):
    """Explain the entry the first time; then its LocalFiles, or None (said in one line) when its folder is empty."""
    explain_once(source, data_dir)
    folder = signup_folder(source.key)
    files = LocalFiles(folder)
    if not files.where:
        say(f"  {source.key}: no files in {folder}, so it is left out. {SIGNUP_INFO[source.key]['where']}")
        return None
    return files


def local_rows(source, data_dir, files, items, cap, seed):
    """Kit rows from [(file path in files, [(question, answer)], credit)]: up to cap pictures, shuffled the same way
    each time, each picture made smaller into the data folder once, a row marked "child" when its answer names a
    child. Items whose picture is missing or unreadable are passed over."""
    import archive_sources
    items = list(items)
    random.Random(seed).shuffle(items)
    out_folder = os.path.join(data_dir, source.key)
    os.makedirs(out_folder, exist_ok=True)
    rows, used = [], 0
    for name, qas, credit in items:
        if used >= cap:
            break
        if name not in files.where or not qas:
            continue
        stem = re.sub(r"[^\w.-]+", "_", os.path.splitext(name)[0])[-120:]
        target = os.path.join(out_folder, stem + ".jpg")
        if not sources.have(target):
            try:
                if not sources.smaller(files.read(name), target):
                    continue
            except (OSError, zipfile.BadZipFile, KeyError):
                continue
        used += 1
        for question, answer in qas:
            child = bool(archive_sources.CHILD_WORDS.search(answer))
            rows.append({"picture": target, "question": question, "answer": answer, "split": "", "credit": credit,
                         "child": child})
    if not rows:
        say(f"  {source.key}: the files are there but no labelled pictures were found in them, so it is left out. "
            f"{SIGNUP_INFO[source.key]['where']}")
    return rows


def counted(counts, order):
    """ "2 red (stop) and 1 green (go)" from {label: count} in the given order of (label, words)."""
    parts = [f"{counts[label]} {words}" for label, words in order if counts.get(label)]
    if not parts:
        return ""
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def a_sign(words):
    """ "a stop sign", "an end of school zone sign" """
    return ("an " if words[:1].lower() in "aeiou" else "a ") + words + " sign"


def listed_with_and(parts):
    """ "a, b and c" """
    parts = list(parts)
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def camel_words(tag):
    """A LISA sign tag in words: "speedLimit35" -> "speed limit 35", "pedestrianCrossing" -> "pedestrian crossing"."""
    text = re.sub(r"(?<=[a-z])(?=[A-Z0-9])|(?<=[0-9])(?=[A-Za-z])", " ", tag)
    return text.lower().strip()


# LISA Traffic Light: the light states its makers marked, with what they mean.
LIGHT_Q = "What colour are the traffic lights?"
LIGHT_STATES = [("stop", "red (stop)"), ("stopLeft", "red left-turn arrow"), ("warning", "yellow (about to turn red)"),
                ("warningLeft", "yellow left-turn arrow"), ("go", "green (go)"), ("goLeft", "green left-turn arrow"),
                ("goForward", "green straight-ahead arrow")]
LISA_LIGHTS_CREDIT = ("LISA Traffic Light Dataset (Jensen, Philipsen, Møgelmose, Moeslund and Trivedi), "
                      "CC BY-NC-SA 4.0, https://www.kaggle.com/datasets/mbornoe/lisa-traffic-light-dataset")


def lisa_csv(text):
    """{picture file's last part: [annotation tag]} from a LISA annotation file ("Filename;Annotation tag;...")."""
    out = {}
    lines = text.splitlines()
    if not lines or "annotation tag" not in lines[0].lower():
        return out
    for line in lines[1:]:
        parts = line.split(";")
        if len(parts) > 1 and parts[0].strip():
            out.setdefault(parts[0].strip().rsplit("/", 1)[-1], []).append(parts[1].strip())
    return out


def light_answer(tags, night=False):
    """ "The traffic lights marked in this photo: 1 red (stop) and 2 green (go)." (and " It is night." for a night
    clip), or "" when no tag is a light state."""
    from collections import Counter
    text = counted(Counter(tags), LIGHT_STATES)
    return f"The traffic lights marked in this photo: {text}." + (" It is night." if night else "") if text else ""


def prepare_lisa_traffic_lights(source, data_dir, work, cap):
    """LISA Traffic Light from the owner's Kaggle download: each frame with the light states its makers marked
    (frameAnnotationsBOX.csv files)."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    items = []
    for ann in files.find(r"^frameAnnotationsBOX\.csv$"):
        night = "night" in ann.lower()
        for base, tags in lisa_csv(files.text(ann)).items():
            name = files.named(base)
            answer = light_answer(tags, night)
            if name and answer:
                items.append((name, [(LIGHT_Q, answer)], LISA_LIGHTS_CREDIT))
    return local_rows(source, data_dir, files, items, cap + source.test, 771)


# LISA Traffic Sign: the US sign types its makers marked.
SIGNS_Q = "What road signs are in this photo?"
LISA_SIGNS_CREDIT = ("LISA Traffic Sign Dataset (Møgelmose, Trivedi and Moeslund, UC San Diego), academic licence, "
                     "https://cvrr.ucsd.edu/lisa-traffic-signs-dataset")


def sign_answer(tags):
    """ "The road signs marked in this photo: a stop sign and a speed limit 35 sign." (each kind once, in the order
    first marked), or ""."""
    kinds = list(dict.fromkeys(camel_words(t) for t in tags if t))
    return f"The road signs marked in this photo: {listed_with_and(a_sign(k) for k in kinds)}." if kinds else ""


def prepare_lisa_traffic_signs(source, data_dir, work, cap):
    """LISA Traffic Sign from the owner's download: each frame with the sign types its makers marked
    (allAnnotations.csv, or the frameAnnotations.csv files)."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    tags = {}
    for ann in files.find(r"^allAnnotations\.csv$") or files.find(r"^frameAnnotations\.csv$"):
        for base, found in lisa_csv(files.text(ann)).items():
            tags.setdefault(base, []).extend(found)
    items = [(files.named(base), [(SIGNS_Q, sign_answer(found))], LISA_SIGNS_CREDIT)
             for base, found in tags.items() if files.named(base) and sign_answer(found)]
    return local_rows(source, data_dir, files, items, cap + source.test, 773)


# BDD100K: the weather, scene and time of day its makers gave each frame, and the things they marked.
BDD_SCENE_Q = "What is the weather and time of day, and where is this?"
BDD_THINGS_Q = "What is on the road?"
BDD_CREDIT = ("BDD100K (Yu et al., Berkeley DeepDrive), for educational, research and not-for-profit use, "
              "https://bdd-data.berkeley.edu")
BDD_TIMES = {"daytime": "Daytime", "night": "Night", "dawn/dusk": "Dawn or dusk"}
BDD_PLACES = {"city street": "on a city street", "highway": "on a highway", "residential": "in a residential street",
              "parking lot": "in a car park", "gas stations": "at a petrol (gas) station", "tunnel": "in a tunnel"}
# (label, one, more than one): both label sets (the 2018 labels and det_20) say the same things.
BDD_THINGS = [("car", "car", "cars"), ("bus", "bus", "buses"), ("truck", "lorry (truck)", "lorries (trucks)"),
              ("person", "person on foot", "people on foot"), ("pedestrian", "person on foot", "people on foot"),
              ("rider", "rider", "riders"), ("bike", "bicycle", "bicycles"), ("bicycle", "bicycle", "bicycles"),
              ("motor", "motorbike", "motorbikes"), ("motorcycle", "motorbike", "motorbikes"),
              ("train", "train", "trains"), ("traffic sign", "traffic sign", "traffic signs"),
              ("traffic light", "traffic light", "traffic lights")]
BDD_LIGHTS = [("red", "red"), ("yellow", "yellow"), ("green", "green")]


def bdd_answers(frame):
    """[(question, answer)] of one BDD100K frame record: its weather, scene and time of day (when given), the things
    marked in it with their counts, and the colours of the traffic lights marked."""
    from collections import Counter
    out = []
    a = frame.get("attributes") or {}
    time_of_day = BDD_TIMES.get(str(a.get("timeofday") or ""))
    weather = str(a.get("weather") or "")
    place = BDD_PLACES.get(str(a.get("scene") or ""))
    if time_of_day and weather and weather != "undefined":
        out.append((BDD_SCENE_Q, f"{time_of_day}, {weather} weather" + (f", {place}" if place else "") + "."))
    labels = [x for x in frame.get("labels") or [] if isinstance(x, dict)]
    counts = Counter(x.get("category") for x in labels)
    merged, one = Counter(), {}
    for label, single, words in BDD_THINGS:
        merged[words] += counts.get(label, 0)
        one[words] = single
    order = list(dict.fromkeys(words for _, _, words in BDD_THINGS))
    things = [f"{merged[w]} {w if merged[w] > 1 else one[w]}" for w in order if merged[w]]
    if things:
        out.append((BDD_THINGS_Q, f"Marked in this photo: {listed_with_and(things)}."))
    colours = Counter(str((x.get("attributes") or {}).get("trafficLightColor") or (x.get("attributes") or {}).get(
        "trafficLightColour") or "") for x in labels if x.get("category") == "traffic light")
    text = counted(colours, BDD_LIGHTS)
    if text:
        out.append((LIGHT_Q, f"The traffic lights marked in this photo: {text}."))
    return out


def prepare_bdd100k(source, data_dir, work, cap):
    """BDD100K from the owner's download: the label file (bdd100k_labels_images_val.json or det_val.json; the
    smallest one there is read, as it covers enough frames) and the 100K images zip."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    label_files = files.find(r"^(bdd100k_labels_images|det)_(val|train)\.json$")
    if not label_files:
        say(f"  bdd100k: no label file (bdd100k_labels_images_val.json or det_val.json) there, so it is left out. "
            f"{SIGNUP_INFO['bdd100k']['where']}")
        return []
    label_files.sort(key=lambda n: (0 if "val" in n else 1, n))
    try:
        frames = json.loads(files.text(label_files[0]))
    except ValueError:
        say(f"  bdd100k: {label_files[0]} could not be read, so it is left out.")
        return []
    items = []
    for frame in frames if isinstance(frames, list) else []:
        name = files.named(str(frame.get("name") or ""))
        answers = bdd_answers(frame)
        if name and answers:
            items.append((name, answers, BDD_CREDIT))
    return local_rows(source, data_dir, files, items, cap + source.test, 777)


# Mapillary: sign labels ("regulatory--stop--g1") and Vistas' readable label names.
MAPILLARY_SIGNS_CREDIT = ("Mapillary Traffic Sign Dataset (Ertler et al., Mapillary), CC BY-NC-SA 4.0, "
                          "https://www.mapillary.com/dataset/trafficsign")
MAPILLARY_KINDS = {"regulatory": "a rule", "warning": "a warning", "information": "information",
                   "complementary": "an extra plate under another sign"}


def mapillary_sign(label):
    """ "regulatory--maximum-speed-limit-50--g1" -> "maximum speed limit 50 sign (a rule)"; "" for "other-sign" or
    a label not in that form."""
    parts = label.split("--")
    if len(parts) < 2 or parts[0] not in MAPILLARY_KINDS:
        return ""
    return f"{parts[1].replace('-', ' ')} sign ({MAPILLARY_KINDS[parts[0]]})"


def prepare_mapillary_signs(source, data_dir, work, cap):
    """Mapillary Traffic Sign Dataset from the owner's download: each photo with the signs its makers named
    (annotations/<key>.json; the photos in the images zips)."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    items = []
    for ann in files.find(r"\.json$"):
        if "/annotations/" not in "/" + ann:
            continue
        try:
            data = json.loads(files.text(ann))
        except ValueError:
            continue
        signs = list(dict.fromkeys(filter(None, (mapillary_sign(str(o.get("label") or ""))
                                                 for o in data.get("objects") or [] if isinstance(o, dict)))))
        name = files.named(ann.rsplit("/", 1)[-1][:-5] + ".jpg")
        if name and signs:
            answer = f"The traffic signs marked in this photo: {listed_with_and(signs)}."
            items.append((name, [(SIGNS_Q, answer)], MAPILLARY_SIGNS_CREDIT))
    return local_rows(source, data_dir, files, items, cap + source.test, 779)


VISTAS_Q = "What is in this street scene?"
VISTAS_CREDIT = ("Mapillary Vistas Dataset (Neuhold et al., Mapillary), CC BY-NC-SA 4.0, "
                 "https://www.mapillary.com/dataset/vistas")
VISTAS_LEFT_OUT = re.compile(r"\b(unlabeled|ego vehicle|car mount|void)\b", re.I)


def vistas_readable(config_text):
    """{label name: its readable name} from Vistas' config file ("construction--flat--sidewalk" -> "Sidewalk")."""
    try:
        labels = json.loads(config_text).get("labels") or []
    except (ValueError, AttributeError):
        return {}
    return {str(x.get("name")): str(x.get("readable") or "") for x in labels if isinstance(x, dict) and x.get("name")}


def vistas_answer(labels, readable, most=12):
    """ "Marked in this street photo: road, sidewalk, crosswalk, car and traffic light." The kinds marked most
    often first (at most most of them), each once, in their readable names (the last part of the label when the
    config has none), leaving out "unlabeled", the camera's own car and its mount."""
    from collections import Counter
    words = []
    for label in labels:
        word = readable.get(label) or label.split("--")[-1].replace("-", " ")
        if word and not VISTAS_LEFT_OUT.search(word):
            words.append(word.lower())
    kinds = [w for w, _ in Counter(words).most_common(most)]
    return f"Marked in this street photo: {listed_with_and(kinds)}." if kinds else ""


def prepare_mapillary_vistas(source, data_dir, work, cap):
    """Mapillary Vistas from the owner's download: each photo with the kinds of things its makers outlined
    (v2.0 polygons, or v1.2 instance files are not read), in the config file's readable names."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    configs = files.find(r"^config_v2\.0\.json$") or files.find(r"^config.*\.json$")
    readable = vistas_readable(files.text(configs[0])) if configs else {}
    items = []
    for ann in files.find(r"\.json$"):
        if "/polygons/" not in "/" + ann:
            continue
        try:
            data = json.loads(files.text(ann))
        except ValueError:
            continue
        labels = [str(o.get("label") or "") for o in data.get("objects") or [] if isinstance(o, dict)]
        name = files.named(ann.rsplit("/", 1)[-1][:-5] + ".jpg")
        answer = vistas_answer(labels, readable)
        if name and answer:
            items.append((name, [(VISTAS_Q, answer)], VISTAS_CREDIT))
    return local_rows(source, data_dir, files, items, cap + source.test, 781)


# DeepFashion (Category and Attribute Prediction Benchmark): the clothing category its makers gave each photo.
CLOTHES_Q = "What kind of clothing is this?"
DEEPFASHION_CREDIT = ("DeepFashion (Liu, Luo, Qiu, Wang and Tang, CUHK), non-commercial research use, "
                      "https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html")
CLOTHES_WORDS = {"tee": "T-shirt", "tank": "tank top", "henley": "Henley shirt", "jeggings": "jeggings",
                 "joggers": "joggers", "romper": "romper (playsuit)", "kaftan": "kaftan", "coverup": "cover-up",
                 "onesie": "onesie", "caftan": "kaftan", "chinos": "chinos", "culottes": "culottes"}
PLURAL_CLOTHES = re.compile(r"(jeans|shorts|leggings|jeggings|joggers|sweatpants|chinos|culottes|trunks|jodhpurs|"
                            r"capris|gauchos|sweatshorts)$", re.I)


def clothing_answer(category):
    """ "This is a blouse." / "These are jeans." from a DeepFashion category name ("Tee" -> "a T-shirt")."""
    word = CLOTHES_WORDS.get(category.lower(), category.lower())
    if PLURAL_CLOTHES.search(word):
        return f"These are {word}."
    return f"This is {'an' if word[:1] in 'aeiou' else 'a'} {word}."


def deepfashion_categories(cloth_text, img_text):
    """{image path ("img/Sheer_Blouse/img_00000001.jpg"): category name} from list_category_cloth.txt (a count,
    a header, then "Anorak 1" lines, numbered from 1) and list_category_img.txt (a count, a header, then "<image>
    <number>" lines)."""
    names = [line.rsplit(None, 1)[0].strip() for line in cloth_text.splitlines()[2:] if line.strip()]
    out = {}
    for line in img_text.splitlines()[2:]:
        parts = line.split()
        if len(parts) == 2 and parts[1].isdigit() and 1 <= int(parts[1]) <= len(names):
            out[parts[0]] = names[int(parts[1]) - 1]
    return out


def prepare_deepfashion(source, data_dir, work, cap):
    """DeepFashion Category and Attribute Prediction from the owner's download: each photo with its clothing
    category (Anno_coarse/list_category_cloth.txt and list_category_img.txt; the photos in img.zip)."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    cloth, img = files.find(r"^list_category_cloth\.txt$"), files.find(r"^list_category_img\.txt$")
    if not cloth or not img:
        say(f"  deepfashion: list_category_cloth.txt or list_category_img.txt is missing, so it is left out. "
            f"{SIGNUP_INFO['deepfashion']['where']}")
        return []
    paths = set(files.where)
    items = []
    for path, category in deepfashion_categories(files.text(cloth[0]), files.text(img[0])).items():
        name = path if path in paths else next((p for p in (f"img/{path}", path.split("/", 1)[-1]) if p in paths),
                                               None)
        if name:
            items.append((name, [(CLOTHES_Q, clothing_answer(category))], DEEPFASHION_CREDIT))
    return local_rows(source, data_dir, files, items, cap + source.test, 783)


# Fastener sets sorted into one folder per kind (Kaggle "The Fasteners" and "SortScrews", or a Roboflow Universe set
# exported in "Folder Structure"): the folder names the kind.
FASTENER_Q = "What kind of fastener is this?"
SPLIT_FOLDERS = re.compile(r"^(train|training|valid|validation|val|test|testing|images|data|dataset)$", re.I)
PHOTO_FILE = re.compile(r"\.(jpe?g|png|bmp|webp)$", re.I)


def folder_kind(path):
    """The kind a picture's folder names ("The Fasteners/bolt/IMG_1.jpg" -> "bolt", "SortScrews/train/hex_nut/x.jpg"
    -> "hex nut"): the nearest folder that is not a split folder ("train", "valid") nor the set's own top folder;
    "" when there is none or it is only a number."""
    parts = path.split("/")
    for folder in reversed(parts[1:-1]):
        if SPLIT_FOLDERS.match(folder):
            continue
        word = re.sub(r"[_-]+", " ", folder).strip()
        return "" if not word or re.fullmatch(r"[\d\s]+", word) else word.lower()
    return ""


def prepare_fastener_sets(source, data_dir, work, cap):
    """Fastener photos sorted by kind, one folder per kind, from the sets the owner downloaded into this entry's
    folder (each set in a folder of its own, named after it, for the credit)."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    items = []
    for name in files.names():
        kind = folder_kind(name) if PHOTO_FILE.search(name) else ""
        if kind and len(name.split("/")) >= 3:
            set_name = name.split("/", 1)[0]
            answer = f"This is {'an' if kind[:1] in 'aeiou' else 'a'} {kind}, as the set's makers sorted it."
            items.append((name, [(FASTENER_Q, answer)], f"{set_name} (downloaded by you; its own licence)"))
    return local_rows(source, data_dir, files, items, cap + source.test, 787)


# MVTec D2S: supermarket products its makers outlined, in COCO files (D2S_training.json and the like).
PRODUCTS_Q = "What products are in this photo?"
D2S_CREDIT = ("MVTec D2S, Densely Segmented Supermarket Dataset (Follmann et al., MVTec Software), CC BY-NC-SA 4.0, "
              "https://www.mvtec.com/company/research/datasets/mvtec-d2s")


def coco_products(coco):
    """{image file name: "The products marked in this photo: avocado (2) and coca cola bottle (1)."} from a COCO
    annotation file's dict (its categories, images and annotations)."""
    from collections import Counter
    cats = {c.get("id"): str(c.get("name") or "").replace("_", " ") for c in coco.get("categories") or []}
    files = {i.get("id"): str(i.get("file_name") or "") for i in coco.get("images") or []}
    found = {}
    for a in coco.get("annotations") or []:
        if a.get("image_id") in files and cats.get(a.get("category_id")):
            found.setdefault(files[a["image_id"]], Counter())[cats[a["category_id"]]] += 1
    return {f: "The products marked in this photo: " + listed_with_and(f"{n} ({c})" for n, c in sorted(
        counts.items(), key=lambda x: (-x[1], x[0]))) + "." for f, counts in found.items() if f}


def prepare_mvtec_d2s(source, data_dir, work, cap):
    """MVTec D2S from the owner's download (unpacked: the images folder and the annotations folder with its
    D2S_*.json files): each photo with the products its makers outlined."""
    files = local_files_or_skip(source, data_dir)
    if files is None:
        return []
    answers = {}
    for ann in files.find(r"^D2S_.*\.json$"):
        try:
            answers.update(coco_products(json.loads(files.text(ann))))
        except (ValueError, AttributeError):
            continue
    items = [(files.named(f.rsplit("/", 1)[-1]), [(PRODUCTS_Q, a)], D2S_CREDIT) for f, a in answers.items()
             if files.named(f.rsplit("/", 1)[-1])]
    return local_rows(source, data_dir, files, items, cap + source.test, 789)


# The file in each local-file entry's folder whose presence means the owner has put the download there
# (local_ready; any zip counts too, as its inside is only read when the training runs).
LOCAL_LABEL_FILES = {
    "lisa_traffic_lights": r"^frameAnnotationsBOX\.csv$",
    "lisa_traffic_signs": r"^(allAnnotations|frameAnnotations)\.csv$",
    "bdd100k": r"^(bdd100k_labels_images|det)_(val|train)\.json$",
    "mapillary_signs": r"\.json$",
    "mapillary_vistas": r"\.json$",
    "deepfashion": r"^list_category_img\.txt$",
    "fastener_sets": r"\.(jpe?g|png)$",
    "mvtec_d2s": r"^D2S_.*\.json$",
}


# ----------------------------------------------------------------- the collections

SIGNUP_SOURCES = [
    Source("dvids_us", "US forces at work: disaster relief, rescues, ships, aircraft and training, with the "
                       "photographers' captions (DVIDS; your own free DVIDS key; personal use)",
           "DVIDS API: 'All media assets and information accessible via the DVIDS API is free for commercial use' "
           "(https://api.dvidshub.net/docs/tos); cached copies must follow removals, so personal use only",
           "Defense Visual Information Distribution Service (DVIDS), US Department of Defense photographers, each "
           "credited in its row, https://www.dvidshub.net", "research", 1500, 20, prepare_dvids_us,
           "up to about 600 MB of pictures", terms="https://api.dvidshub.net/docs/tos",
           terms_summary="Free to use, but the copies must be kept up to date with DVIDS, so the result is for your "
                         "personal use only. Needs your own DVIDS_API_KEY."),
    Source("kaggle_chess", "Chess diagrams with every piece named (Kaggle Chess Positions; your own free Kaggle "
                           "key; personal use)",
           "CC0 as marked on Kaggle (https://www.kaggle.com/datasets/koryakinp/chess-positions); boards and pieces "
           "drawn by Chess.com, so research use only",
           "Chess Positions by Pavel Koryakin (Kaggle koryakinp/chess-positions), boards and pieces by Chess.com",
           "research", 1500, 20, prepare_kaggle_chess, "4.3 GB (the whole zip, kept in the downloads folder)",
           terms="https://www.kaggle.com/datasets/koryakinp/chess-positions",
           terms_summary="Marked CC0, but the pieces and boards are Chess.com's drawings: research and personal use "
                         "only. Needs your own Kaggle key."),
    Source("flickr30k", "Everyday photos of people, described by people (Flickr30k; request form; personal use)",
           "Flickr30k: 'for researchers and educators who wish to use the dataset for non-commercial research "
           "and/or educational purposes' (https://shannon.cs.illinois.edu/DenotationGraph/)",
           "Flickr30k (Young, Lai, Hodosh and Hockenmaier, University of Illinois), photos from Flickr",
           "research", 3000, 30, prepare_flickr30k, "4.4 GB (downloaded by you after the request form)",
           terms="https://shannon.cs.illinois.edu/DenotationGraph/",
           terms_summary="Non-commercial research and educational use only; the photos stay their Flickr owners'. "
                         "You fill in the request form and put the files in the sign-up folder."),
    Source("dvids_caf", "Canadian Armed Forces at work (DVIDS; your own free DVIDS key; personal use)",
           "Crown copyright of National Defence: 'personal or public non-commercial use' "
           "(https://www.canada.ca/en/department-national-defence/corporate/terms-conditions.html)",
           "Canadian Armed Forces imagery via DVIDS, each credited in its row, https://www.dvidshub.net",
           "noncommercial", 600, 10, prepare_dvids_caf, "up to about 250 MB of pictures",
           terms="https://www.canada.ca/en/department-national-defence/corporate/terms-conditions.html",
           terms_summary="Non-commercial use only. Needs your own DVIDS_API_KEY."),
    Source("museums_victoria", "Household appliances, radios, telephones, tools and toys from Museums Victoria "
                               "(downloaded slowly on your computer; personal use)",
           "Each picture's own licence on Museums Victoria Collections: public domain or CC BY, BY-SA, BY-NC or "
           "BY-NC-SA only (https://collections.museumsvictoria.com.au/about)",
           "Museums Victoria Collections, each object credited in its row, https://collections.museumsvictoria.com.au",
           "noncommercial", 1500, 20, prepare_museums_victoria, "up to about 500 MB of pictures",
           terms="https://collections.museumsvictoria.com.au/about",
           terms_summary="Each picture's own licence (public domain or Creative Commons without NoDerivatives); its "
                         "site refused the machine these entries were made on, so it may refuse yours too."),
    # The local-file entries (downloaded by you, put in the sign-up folder; LOCAL_LABEL_FILES, local_ready).
    Source("lisa_traffic_lights", "Traffic light colours in San Diego street photos (LISA Traffic Light; your own "
                                  "Kaggle download; personal use)",
           "CC BY-NC-SA 4.0 as its Kaggle page states (https://www.kaggle.com/datasets/mbornoe/"
           "lisa-traffic-light-dataset)", LISA_LIGHTS_CREDIT, "noncommercial", 2000, 20,
           prepare_lisa_traffic_lights, "5.2 GB (downloaded by you from Kaggle)",
           terms="https://www.kaggle.com/datasets/mbornoe/lisa-traffic-light-dataset",
           terms_summary="Non-commercial use with credit; anything made from it keeps the same terms. You download "
                         "it and put it in the sign-up folder."),
    Source("lisa_traffic_signs", "US road signs in street photos (LISA Traffic Sign; academic licence; personal use)",
           "'released under academic license agreement' (https://cvrr.ucsd.edu/lisa-traffic-signs-dataset)",
           LISA_SIGNS_CREDIT, "research", 2000, 20, prepare_lisa_traffic_signs,
           "several GB (downloaded by you after accepting the agreement)",
           terms="https://cvrr.ucsd.edu/lisa-traffic-signs-dataset",
           terms_summary="Academic (research) use only. You accept the agreement, download it and put it in the "
                         "sign-up folder."),
    Source("bdd100k", "Driving photos with weather, time of day, road users and traffic light colours (BDD100K; "
                      "your own free account; personal use)",
           "BDD100K licence: educational, research and not-for-profit use (https://bdd-data.berkeley.edu)",
           BDD_CREDIT, "research", 3000, 30, prepare_bdd100k, "about 5.5 GB (downloaded by you after signing up)",
           terms="https://bdd-data.berkeley.edu",
           terms_summary="Educational, research and not-for-profit use only. You sign up, download it and put it "
                         "in the sign-up folder."),
    Source("mapillary_signs", "Traffic signs named in street photos from around the world (Mapillary Traffic Sign "
                              "Dataset; your own free account; personal use)",
           "CC BY-NC-SA 4.0 for research (https://www.mapillary.com/dataset/trafficsign)",
           MAPILLARY_SIGNS_CREDIT, "noncommercial", 3000, 30, prepare_mapillary_signs,
           "tens of GB (downloaded by you after signing up)", terms="https://www.mapillary.com/dataset/trafficsign",
           terms_summary="Non-commercial use with credit; anything made from it keeps the same terms. You sign up, "
                         "download it and put it in the sign-up folder."),
    Source("mapillary_vistas", "What is in a street scene: road, sidewalk, crosswalk, cars, poles and signs "
                               "(Mapillary Vistas; your own free account; personal use)",
           "CC BY-NC-SA 4.0 for research (https://www.mapillary.com/dataset/vistas)",
           VISTAS_CREDIT, "noncommercial", 3000, 30, prepare_mapillary_vistas,
           "tens of GB (downloaded by you after signing up)", terms="https://www.mapillary.com/dataset/vistas",
           terms_summary="Non-commercial use with credit; anything made from it keeps the same terms. You sign up, "
                         "download it and put it in the sign-up folder."),
    Source("deepfashion", "Kinds of clothing: blouses, T-shirts, jeans, dresses and more (DeepFashion; research "
                          "agreement; personal use)",
           "non-commercial research only (https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html)",
           DEEPFASHION_CREDIT, "research", 3000, 30, prepare_deepfashion,
           "about 2 GB (downloaded by you from its Google Drive folder)",
           terms="https://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html",
           terms_summary="Non-commercial research use only. You download it and put it in the sign-up folder."),
    Source("fastener_sets", "Bolts, screws, nuts and washers sorted by kind (Kaggle or Roboflow sets you download; "
                            "personal use)",
           "each set's own licence on its page (Kaggle 'The Fasteners': CC0; 'SortScrews': Apache 2.0)",
           "Fastener sets downloaded by you from Kaggle or Roboflow Universe, each credited by its folder name",
           "research", 1500, 15, prepare_fastener_sets, "under 1 GB (downloaded by you)",
           terms="https://www.kaggle.com/datasets/terryfuatatc/sortscrews",
           terms_summary="Each set's own licence; the Kaggle and Roboflow terms of your account. You download the "
                         "sets and put each in its own folder in the sign-up folder."),
    Source("mvtec_d2s", "Supermarket products named on a tray (MVTec D2S; download form; personal use)",
           "'released under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License' "
           "(https://www.mvtec.com/company/research/datasets/mvtec-d2s)",
           D2S_CREDIT, "noncommercial", 2000, 20, prepare_mvtec_d2s, "several GB (downloaded by you after the form)",
           terms="https://www.mvtec.com/company/research/datasets/mvtec-d2s",
           terms_summary="Non-commercial use with credit; anything made from it keeps the same terms. You fill in "
                         "the form, download and unpack it into the sign-up folder."),
]

# People are in DVIDS and Flickr30k; the chess drawings are Chess.com's; Museums Victoria was never checked from here:
# none is used for picture-making.
SIGNUP_PICTURE_MAKING_OK = set()


def needs_keys(source):
    """The key names a sign-up collection needs ([] for others and for those needing none)."""
    return list((SIGNUP_INFO.get(getattr(source, "key", "")) or {}).get("keys") or [])


def ready(source):
    """True when a sign-up collection has what it needs on this computer (its keys; Flickr30k: its description
    file in the sign-up folder). Other collections: True."""
    key = getattr(source, "key", "")
    if key not in SIGNUP_INFO:
        return True
    if key in LOCAL_LABEL_FILES:
        return local_ready(key)
    if key == "flickr30k":
        home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        folder = os.path.join(home, "Documents", DOCUMENTS_FOLDER, "flickr30k")
        return os.path.isdir(folder) and any(f.lower().endswith((".token", ".tar.gz", ".csv"))
                                             for _r, _d, files in os.walk(folder) for f in files)
    return not missing_keys(needs_keys(source))


def keys_text():
    """Every sign-up collection and key in plain words, for the wizard's Sign-up keys window: where to get each key,
    the terms line agreed to and what it adds, and the warning never to paste a key into a chat or an e-mail."""
    parts = ["Your keys stay on this computer, in your own settings folder (or in your Windows environment "
             "variables). Never paste a key into a chat, an e-mail or a forum: anyone with it can use your account."]
    for s in SIGNUP_SOURCES:
        info = SIGNUP_INFO[s.key]
        need = " and ".join(info["keys"]) if info["keys"] else "no key"
        parts.append(f"{s.name}. Needs: {need}. Where to get it: {info['where']} The terms you agree to "
                     f"({info['terms_url']}): {info['terms']} What it adds: {info['adds']}")
    for name in ("EUROPEANA_KEY", "DPLA_API_KEY", "SI_API_KEY"):
        label, where = SIGNUP_KEYS[name]
        parts.append(f"{label} ({name}), used by collections already in the kit: {where}")
    return "\n\n".join(parts)


# ----------------------------------------------------------------- not built, and the personal-use review

SIGNUP_NOT_INCLUDED = {
    "Kaggle web-picture sets (Cards, Car Parts, Musical Instruments by gpiosenka; FIRE by phylake1337)":
        "marked CC0 or Apache 2.0 on Kaggle, but the pictures were gathered from web searches (unknown provenance): "
        "left out by the owner's rule on scraped sets.",
    "Kaggle SH17 PPE (mugheesahmad/sh17-dataset-for-ppe-detection, CC BY-NC-SA 4.0, Pexels photos)":
        "allowed for personal use, but 14 GB and its label layout could not be read without an account; can be "
        "added once its files are seen.",
    "Kaggle RPC, Retail Product Checkout (diyer22, CC BY-NC-SA 4.0)":
        "allowed for personal use, but 27 GB and its file layout on Kaggle could not be read without an account; "
        "can be added once its files are seen.",
    "Roboflow Universe sets (surgical tools, dashboard icons, electronic components, PPE, landmines)":
        "universe.roboflow.com refused this machine (403), so no set's licence or picture source could be read; most "
        "Roboflow sets hold photos gathered from the web (unknown provenance): left out by the owner's rule.",
    "Digital Public Library of America (DPLA_API_KEY)":
        "already built in university_sources.py (dpla_campus_sa, dpla_campus_nc) and the open dpla_campus pack; not "
        "repeated. The wizard's key file gives those entries the owner's DPLA_API_KEY.",
    "Europeana with the owner's own key (EUROPEANA_KEY)":
        "no new entry: culture_sources, service_sources and adult_review_sources already read EUROPEANA_KEY (falling "
        "back to the demonstration key); the wizard's key file now supplies it.",
    "Powerhouse Collection API (POWERHOUSE_API_KEY)":
        "api.maas.museum did not answer this machine, so its answers and picture licences could not be read; the "
        "website's robots.txt says 'User-agent: * Disallow: /'. Can be added once the API answers.",
    "YFCC100M (Yahoo Webscope)":
        "the media are on AWS (multimedia-commons), but the metadata is 'subject to the relevant Webscope License "
        "Agreement', and 'Webscope is not currently offering access to the YFCC100M' "
        "(https://multimediacommons.wordpress.com/yfcc100m-core-dataset/): it cannot be obtained legitimately now.",
    "Flickr8k":
        "its request form is gone (the page at https://hockenmaier.cs.illinois.edu/8k-pictures.html points to a page "
        "with no form); Kaggle copies are re-uploads the makers never licensed.",
    "Products-10K, SKU-110K":
        "product numbers or shelf boxes only, no names or descriptions to learn from (as personal_sources.REJECTED). "
        "Checked again in November 2026: Products-10K's labels are still product and group numbers, so a local-file "
        "entry would have nothing to say.",
    "Retail-786k (Lamm and Keuper; Zenodo 7970567, CC BY-NC-ND 4.0)":
        "an open download, not a sign-up, but its 786,000 cut-out leaflet pictures are labelled only by product "
        "number (no names), so it has nothing to teach a describer (packaged_goods_sources.py says the same).",
    "Stanford Dogs":
        "already a personal-use kit entry (personal_sources.stanford_dogs, downloaded by the kit itself): not "
        "repeated here.",
    "Unitail, Locount, RP2K":
        "request forms or e-mail to the authors; Unitail's and Locount's labels are boxes, counts or text fragments, "
        "RP2K states no licence. Can be added once the owner receives the files and their layout is seen.",
}

# The review of every not-included, sign-up and permission list in the kit for PERSONAL use on the owner's computer:
# (list, source) -> (why it was skipped, "A"/"B"/"C", action). A: OK for personal use and worth adding; B: not useful
# even if allowed; C: not allowed even for personal use (permission letters are being drafted for the C ones worth
# asking).
PERSONAL_REVIEW = {
    ("canada", "Library and Archives Canada"): (
        "refused this machine (403)", "C",
        "its robots.txt says 'Content-Signal: search=yes,ai-train=no,use=reference', an express reservation against "
        "AI training: stays out; permission letter (CANADA_PERMISSION_CANDIDATES)."),
    ("canada", "City of Vancouver Archives"): (
        "refused this machine (403)", "A", "not built: its pages and robots.txt also refused this machine, so its "
        "terms and layout could not be read; check them from the owner's computer first."),
    ("canada", "Ingenium (CC BY-NC-ND)"): (
        "NoDerivatives", "C", "robots.txt 'ai-train=no': stays out."),
    ("canada", "ISED Radio Equipment List"): ("robots Disallow: /", "C", "stays out."),
    ("canada", "Loblaw, Sobeys, Metro, Walmart.ca, Canadian Tire, Amazon.ca; Realtor.ca, Centris"): (
        "terms forbid scraping", "C", "stays out; permission letters."),
    ("canada", "NRC Archives Photographs"): (
        "non-commercial reproduction only", "A", "personal use allowed; not built this pass (no picture listing a "
        "program can read was found); permission letter already listed."),
    ("device", "Museums Victoria"): ("refused this machine (403)", "A",
                                    "built: museums_victoria (robots.txt allows /api; polite, one request every 3 s)."),
    ("device/archive", "Science Museum Group (CC BY-NC-SA)"): (
        "refused this machine (403)", "C", "its robots.txt disallows /api/, /iiif/ and every address with '?', so "
        "automated searching and picture downloads are not allowed; ask the museum."),
    ("device", "Powerhouse (Sydney)"): ("API did not answer", "A", "not built: the API could not be read (see "
                                       "SIGNUP_NOT_INCLUDED); the website's robots.txt disallows all robots."),
    ("device", "MyFixit and iFixit"): ("robots 'ai-train=no'", "C", "stays out."),
    ("work_farm_mech", "The Henry Ford"): ("did not answer; permission needed; historic", "B",
                                          "historic objects; its terms ask for permission: not added."),
    ("work_farm_mech/land", "NREL image gallery"): (
        "did not answer", "A", "not built: 'Downloading or copying any gallery content counts as accepting' a user "
        "agreement that 'can change without notice'; the site did not answer, so its robots.txt and layout are "
        "unknown. Check from the owner's computer."),
    ("us_modern/archive/graphic", "FEMA, USDA, SSA, USCIS, DOL, State Department sites"): (
        "refused this machine (403)", "A", "public domain, but robots.txt and page layout could not be read from "
        "here (403); FEMA and USDA photos already come from their Commons copies, the forms are B (forms seen "
        "elsewhere). Not built."),
    ("documentary/graphic/us", "NOAA Photo Library"): (
        "refused this machine (403)", "A", "robots.txt (www.noaa.gov) disallows only /search/ and admin paths; not "
        "built: the digital-library pages could not be read to write a reader. Its Commons copies are used."),
    ("archive", "British Museum, Yale Center for British Art, Belvedere"): (
        "Cloudflare or 403", "A", "not built: no API and the pages refused this machine; the art reaches the kit "
        "through other museums."),
    ("archive", "State Library Victoria, Danish Royal Library, Nationalmuseum Sweden, Finnish National Gallery"): (
        "refused or broken API", "B", "historic art and photos already reached through Europeana and K-samsök."),
    ("graphic", "President of Ukraine (CC BY 4.0)"): ("403", "B", "its Commons copies are in the open commons_war pack."),
    ("review", "NCI Visuals Online"): ("did not answer", "B", "public domain; some are on Commons already."),
    ("service", "af.mil, navy.mil, uscg.mil"): ("403", "B", "their photos are on Commons and DVIDS (dvids_us)."),
    ("med_vet", "SURGICAL TOOLS (Mendeley cyghvmjrt3, CC BY-ND 4.0)"): (
        "NoDerivatives", "C", "about 1,000 of its 6,000 photos were 'sourced from various online platforms', and the "
        "files (all renamed by Roboflow) cannot tell them apart from the makers' own: stays out; permission letter."),
    ("safety_rites", "OSCE demining photos (CC BY-ND 4.0)"): (
        "NoDerivatives", "A", "ND allows private training of unchanged originals, but no listing a program can read "
        "was found; not built. Permission letter listed."),
    ("review", "DermNet (CC BY-NC-ND, watermarked)"): (
        "NoDerivatives", "C", "site terms: 'must not remove the watermark'; clean pictures are paid: stays out."),
    ("review", "Film 'Three Cadets' (CC BY-NC-ND)"): ("NoDerivatives", "B", "a single old film; not worth it."),
    ("expression/personal", "FER2013, ExpW, AffectNet, RAF-DB, CK+, EMOTIC, BoLD, KDEF, JAFFE site, Jester"): (
        "research, sign-up or scraped faces", "C", "faces taken from web searches or by request with agreements per "
        "person: scraped sets stay out; the agreement ones need the owner to sign each himself."),
    ("expression", "RAVDESS (CC BY-NC-SA)"): ("non-commercial", "A", "personal use allowed; video of actors: not "
                                             "built this pass (frames would need video_frames)."),
    ("expression/personal", "HaGRID, Oxford-IIIT Pet (CC BY-SA)"): (
        "share-alike", "A", "already a share-alike kit choice where built; the 'everything' switch ticks share-alike."),
    ("personal/med", "HAM10000, ISIC BY-NC, SCIN, Fitzpatrick17k, DermNet"): (
        "non-commercial", "A", "HAM10000, ISIC BY-NC and SCIN are already personal kit entries; Fitzpatrick17k is C "
        "(pictures owned by the atlases; children)."),
    ("medical", "WHO pictures (CC BY-NC-SA)"): ("non-commercial", "A", "not built: no bulk listing found."),
    ("medical/extra/personal", "Kvasir v2, datasets.simula.no"): ("bad certificate", "B",
                                                                  "HyperKvasir (open) already covers it."),
    ("people_activity", "Kinetics, AVA, Moments in Time, HAA500, ActivityNet"): (
        "YouTube films", "C", "videos the makers do not own: stays out."),
    ("people_activity", "HICO-DET, MPII Human Pose"): (
        "Google Drive, research", "A", "personal research use allowed; not built (Google Drive download needs a "
        "sign-in; MPII frames are YouTube stills: C)."),
    ("things", "Ego4D, EgoObjects, Something-Something, Assembly101, MINC full"): (
        "signed licence agreements", "A", "the owner signs each agreement himself; then a local-file entry like "
        "flickr30k can be added. Not built this pass."),
    ("adult_review", "porn sites, NSFW scrapes, LSPD, NPDI, anonymous vintage erotica"): (
        "no consent or age records", "C", "stays out."),
    ("adult_review", "Kinsey Institute, AMAZE, Scarleteen, OMGYes and similar"): (
        "copyright, no licence", "C", "contract or permission candidates."),
    ("us/canada", "Walmart, Target, Kroger, Costco, Amazon, Zillow, Redfin and other shops and listing sites"): (
        "terms forbid scraping", "C", "stays out; permission letters."),
    ("med_vet", "NPR, PBS, GBH, CBC/Radio-Canada, TVO"): ("terms forbid copying and AI training", "C",
                                                       "stays out; permission letters."),
    ("us_modern/state/med_vet", "Flickr API streams"): (
        "Flickr API terms forbid storing photos", "C", "stays out; Commons copies are used."),
    ("adult_review", "Google Patents, USPTO bulk search"): ("terms forbid scraping/bulk", "C", "stays out."),
    ("university", "Canadiana"): ("terms forbid robots", "C", "stays out."),
    ("university", "UBC Archives, Portal to Texas History, University of Alberta, Yale Library"): (
        "research and reference use only, permission", "C", "permission needed for copies: letters."),
    ("university", "UMedia, Michigan, Illinois, Utah, Harvard, McGill, UNC"): (
        "refused this machine", "B", "their open items reach the kit through DPLA (dpla_campus, needs DPLA_API_KEY)."),
    ("culture", "CompCars, MUSCIMA++ handwritten pages"): (
        "research agreement by e-mail; site not reached", "A", "the owner can sign CompCars' agreement himself; "
        "local-file entries can follow."),
    ("culture/extra", "Hugging Face sets with AI-written descriptions or AI-made pictures"): (
        "AI-written or AI-made", "B", "the kit learns only from people's own words and real pictures."),
    ("land", "Agriculture-Vision"): ("terms forbid training beyond a 2020 challenge", "C", "stays out."),
    ("land", "MVTec AD, LOCO, D2S, Screws (CC BY-NC-SA)"): (
        "download form", "A", "personal use allowed; the owner fills the form. D2S is built as the local-file entry "
        "mvtec_d2s; AD, LOCO and Screws can follow the same way."),
    ("mechanical", "CarDD (research, licence form)"): ("form", "A", "the owner sends the form himself; then a local "
                                                       "file entry can follow."),
    ("canada", "Bank of Canada bank-note gallery"): ("non-commercial, 'without alterations'", "B",
                                                    "Commons bank-note files are already used."),
    ("various", "CAD models, vibration recordings, tables, hyperspectral data, microscope pictures"): (
        "not photos", "B", "nothing to learn for a picture describer."),
    ("various", "Commons categories already used, duplicates and re-uploads"): (
        "duplicates or re-uploads with false licences", "B/C", "duplicates not repeated; re-uploads stay out."),
    ("various", "children's classrooms, school cafeterias, circumcision, mugshots, police photos, colonial and "
                "asylum photographs"): ("child-safety, crime and consent rules", "C", "stays out."),
}
