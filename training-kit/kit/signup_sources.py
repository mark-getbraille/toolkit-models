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
        "product numbers or shelf boxes only, no names or descriptions to learn from (as personal_sources.REJECTED).",
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
        "download form", "A", "personal use allowed; the owner fills the form; a local-file entry can follow."),
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
