"""More picture collections for the Picture Model Training Kit: the ones earlier checks left out because of their
licence (share-alike, non-commercial, research-only, or no terms written at all). The owner's rule is that every
picture collection found goes into the kit under the right group, instead of being dropped for its licence.

Nothing here is in a ready-made pack or re-shared by the kit's makers. Each collection is downloaded by the kit on the
user's own computer, straight from where its makers (or, where the makers' own copy is gone, the copy named below)
publish it, into the downloads folder (the picture library's "downloads" folder when there is one), only when the
user ticks the matching choice.

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA, GPL-style copyleft and ODbL collections. Only with the share-alike choice
                   (--with-wikipedia); an add-on trained with them is CC BY-SA.
  "noncommercial"  CC BY-NC, BY-NC-SA or BY-NC-ND. Personal use only (--personal-noncommercial).
  "research"       research, academic or educational use only, or NO STATED TERMS AT ALL (said so in terms_summary:
                   "no licence or terms are stated; personal, non-commercial use only"). Personal use only
                   (--personal-research with --accept-research-terms).

Safety, as in personal_sources.py and the packs:
  - Nothing sexual. Medical pictures of the genitals, groin, buttocks or breasts are left out (INTIMATE_SITE).
  - Medical collections (content "medical") use adults only: an age of 18 or more where the data gives ages
    (PAPILA), or, where it gives none (Wikimedia Commons), only files whose own words say the person is an adult and
    never name a child. Every medical answer ends with DOCTOR.
  - Facial expressions and gestures: the visible signs first, then a careful reading, and "posed" when it was.
  - Everyday photos may show children; rows whose people's own words name a child are marked "child": true, so
    picture-making leaves them out. Indoor scenes of changing rooms and swimming pools are left out.
  - EXTRA_PICTURE_MAKING_OK holds only collections whose answers describe non-people objects or scenes (products,
    plants, pets, birds, food); never people, children or medical.

The collections (EXTRA_SOURCES):
  share-alike
    oxford_pets           Oxford-IIIT Pet: 37 cat and dog breeds (CC BY-SA 4.0).
    hagrid                HaGRIDv2: hand gestures made by adults (a variant of CC BY-SA 4.0).
    plantvillage          PlantVillage: leaves of 14 crops, healthy or with a named disease (CC BY-SA 3.0).
    plantnet_sa           Pl@ntNet-300K v2: 1,000 plant species, the photos under CC BY-SA.
    hiertext              HierText: the text in everyday photos, read out (CC BY-SA 4.0; Open Images photos).
    mapqa                 MapQA: questions about real US choropleth maps (CC BY-SA 4.0).
    hypersim              Hypersim: computer-made pictures of rooms, with the kind of room (CC BY-SA 3.0).
    openfoodfacts         Open Food Facts: product front photos with the name, brand and size (photos CC BY-SA
                          3.0, data ODbL).
    openfoodfacts_labels  Open Food Facts: ingredient-list and nutrition-table photos, read out.
    commons_breeds_sa     Wikimedia Commons: animal breed photos under CC BY-SA or GFDL.
    commons_food_sa       Wikimedia Commons: food photos under CC BY-SA or GFDL.
    commons_medical_sa    Wikimedia Commons: medical photos of adults under CC BY-SA or GFDL (content "medical").
    papila                PAPILA: eye-fundus photos of adults, healthy, glaucoma or suspect (GPL-3.0+; medical).
  noncommercial
    plantnet_nc           Pl@ntNet-300K v2: the photos under CC BY-NC or CC BY-NC-SA.
    ravdess               RAVDESS: stills of 24 adult actors posing eight expressions (CC BY-NC-SA 4.0 videos).
    how2sign              How2Sign: stills of adults signing American Sign Language (CC BY-NC 4.0 videos).
  research (research or educational terms, or none stated)
    cub200                CUB-200-2011: 200 bird species (non-commercial research and education).
    plantdoc              PlantDoc: crop leaves found on the web, healthy or diseased (no rights to the pictures).
    nocaps                nocaps: one-sentence descriptions of Open Images photos (no licence stated for the words).
    vizwiz_quality        VizWiz: what is wrong with a blind person's photo (blur, dark, framing; no terms stated).
    rico_screens          Screen2Words on Rico: phone app screens summed up in a sentence (screens: no terms).
    rico_widgets          Widget Captioning on Rico: what a button on a phone screen does.
    sroie                 SROIE receipts: shop name, date, address and total (no licence stated).
    wildreceipt           WildReceipt: receipts, their shop, date, items and total (no licence stated).
    dvqa                  DVQA: questions about bar charts (no licence stated).
    gothenburg_price_tags Swedish shelf price tags with the product and price (licence of the photos unclear).
    streetsignset         Street Sign Set: European road signs (some photos from street-mapping services).
    ifeed                 IFEED: expressions on faces from a TV series (frames of a TV show: research only).
    navarasa              Navarasa: the nine expressions of Indian classical dance (frames from performances).
    objects365            Objects365: the objects in everyday photos, counted (research).
    vg_photos             Visual Genome questions on its own photos (not COCO's; Flickr photos, no terms).
    uecfoodpix            UEC FoodPix Complete: Japanese meals, the dishes on the tray (research only).
    indoor_scenes         MIT Indoor 67: kinds of indoor places (research only).
    stanford_products     Stanford Online Products: everyday things from online shop listings (no terms stated).

Needing sign-up (cannot be downloaded automatically; get them yourself, then put the pictures in the own-pictures
folder with your own descriptions, as the user guide says):
  PadChest chest X-rays (CC BY-SA 4.0)   https://bimcv.cipf.es/bimcv-projects/padchest/ : fill in the Google form on
                                         the page; the download links come by e-mail.
  KDEF and AKDEF faces                   https://www.kdef.se/download-2/register : register (name, e-mail and
                                         institution) and accept the terms; research use only.
  CK+ (Extended Cohn-Kanade)             https://www.jeffcohn.net/Resources/ : send the signed agreement.
  DCI (Densely Captioned Images)         https://ai.meta.com/datasets/segment-anything-downloads/ : accept Meta's SA-1B
                                         licence to get the pictures; DCI's captions are on GitHub
                                         (facebookresearch/DCI).
  Total-Text                             https://github.com/cs-chan/Total-Text-Dataset : its 2026 terms ask research by
                                         or for a company to get written confirmation first: e-mail the authors.
  Roboflow Universe sets (dog breeds,    https://universe.roboflow.com : a free Roboflow account and API key are needed
  price tags and others)                 to download; each set shows its own licence.
  EMOTIC, BoLD, RAF-DB, AffectNet,       request forms or agreements (see personal_sources.py).
  Jester, EgoGesture

Looked at and not included (the reason of each is in NOT_INCLUDED).

Main parts: EXTRA_SOURCES, EXTRA_PICTURE_MAKING_OK, NOT_INCLUDED, one prepare_<key>(source, data_dir, work, cap)
function per collection, and helpers: stream_tar (a tar archive read straight from the web, stopping as soon as
enough pictures are taken), video_still (one picture out of a short video, with PyAV), gdrive (a Google Drive
file's download address) and the Wikimedia Commons helpers.
"""

import collections
import csv
import gzip
import io
import json
import math
import os
import random
import re
import time
import urllib.parse
import zipfile

import sources
from sources import BRIEF, Source, USER_AGENT, clean, download_file, fetch_pictures
from big_sources import even_pick
from more_sources import as_question, download_to, fetch_shared, json_in_zip, sentence
from personal_sources import (CHILD_WORDS, DOCTOR, INTIMATE_SITE, a_or_an, listed, looks_like,
                              remote_zip, zip_members)

NO_TERMS = "No licence or terms are stated; personal, non-commercial use only."
READ_TEXT_ALL = "Read out all the text in this picture."
EXPRESSION_QUESTION = "What expression is on this person's face?"


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


# ----------------------------------------------------------------- shared helpers

def gdrive(file_id):
    """The direct download address of a public Google Drive file (it answers range requests, so a big zip there can
    be read piece by piece)."""
    return f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"


def zenodo(record, name):
    """The download address of one file of a Zenodo record."""
    return f"https://zenodo.org/records/{record}/files/{urllib.parse.quote(name)}?download=1"


def zenodo_sizes(record):
    """{file name: size in bytes} of a Zenodo record."""
    import requests
    data = requests.get(f"https://zenodo.org/api/records/{record}", timeout=60,
                        headers={"User-Agent": USER_AGENT}).json()
    return {f["key"]: f["size"] for f in data["files"]}


def get_json(url, params=None, tries=4):
    """The JSON at url, tried again a few times (waiting longer each time) when the server is busy."""
    import requests
    for attempt in range(tries):
        try:
            r = requests.get(url, params=params, timeout=120, headers={"User-Agent": USER_AGENT})
            if r.status_code == 200:
                return r.json()
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{url} did not answer; it is tried again the next time")


def get_bytes(url):
    """The bytes at url (raises when it cannot be fetched)."""
    import requests
    r = requests.get(url, timeout=120, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    return r.content


def stream_tar(url, take, what):
    """Read a tar archive (plain or gzip) straight from the web, member by member, without saving the archive:
    take(member, tar) handles each member and returns True when enough has been taken, which stops the download
    there. Used for big archives whose pictures come in no particular order, so the first ones are as good a pick as
    any. If the connection breaks, what was taken so far is kept (and the pictures already made are not fetched
    again the next time)."""
    import requests
    import tarfile
    say(f"  Reading {what} straight from the web (it stops as soon as enough pictures are taken).")
    with requests.get(url, stream=True, timeout=120, headers={"User-Agent": USER_AGENT}) as r:
        r.raise_for_status()
        try:
            with tarfile.open(fileobj=r.raw, mode="r|*") as tar:
                for member in tar:
                    if take(member, tar):
                        return
        except Exception as e:  # noqa: BLE001 - keep what was taken
            say(f"  The download of {what} stopped early ({str(e).splitlines()[0][:120]}); what was read is used.")


def video_still(data, at=0.5):
    """One picture (JPEG bytes) from a short video, at the given share of its length (0.5: the middle), read with
    PyAV (installed with requirements-video.txt). None when the video cannot be read."""
    try:
        import av
    except ImportError as e:
        raise RuntimeError("this collection is made of videos: install the video extras first "
                           "(kit\\requirements-video.txt, which has PyAV)") from e
    try:
        with av.open(io.BytesIO(data)) as box:
            stream = box.streams.video[0]
            length = float(stream.duration * stream.time_base) if stream.duration else \
                (box.duration / 1_000_000 if box.duration else 0)
            want, last = length * at, None
            for frame in box.decode(stream):
                last = frame
                if frame.time is not None and frame.time >= want:
                    break
            if last is None:
                return None
            out = io.BytesIO()
            last.to_image().convert("RGB").save(out, "JPEG", quality=95)
            return out.getvalue()
    except Exception:  # noqa: BLE001 - a video that cannot be read is left out
        return None


def save(name, data, folder):
    """Save picture bytes as a training copy named name in folder; the path, or None."""
    return sources.save_picture(name, data, folder)


def per_label(want, labels):
    """How many pictures each label should give so that want pictures come out (rounded up)."""
    return max(1, math.ceil(want / max(1, labels)))


def plural(word):
    """A rough English plural ("box" -> "boxes", "berry" -> "berries", "person" -> "people")."""
    special = {"person": "people", "man": "men", "woman": "women", "child": "children", "mouse": "mice",
               "knife": "knives", "shelf": "shelves", "glasses": "glasses", "sheep": "sheep", "fish": "fish"}
    last = word.split()[-1]
    if last.lower() in special:
        return word[:-len(last)] + special[last.lower()]
    if re.search(r"(s|x|z|ch|sh)$", word):
        return word + "es"
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    return word + "s"


def counted(counts, most=8):
    """Objects and how many: {"chair": 2, "cup": 1} -> "2 chairs and a cup" (the most common first)."""
    parts = []
    for name, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:most]:
        parts.append(f"{a_or_an(name)} {name}" if n == 1 else f"{n} {plural(name)}")
    return listed(parts) if parts else ""


# ----------------------------------------------------------------- share-alike: Oxford-IIIT Pet

PETS_URL = "https://thor.robots.ox.ac.uk/datasets/pets/images.tar.gz"
# The dog breeds' names as people write them (the file names are lower case).
PET_DOGS = {"american_bulldog": "American Bulldog", "american_pit_bull_terrier": "American Pit Bull Terrier",
            "basset_hound": "Basset Hound", "beagle": "Beagle", "boxer": "Boxer", "chihuahua": "Chihuahua",
            "english_cocker_spaniel": "English Cocker Spaniel", "english_setter": "English Setter",
            "german_shorthaired": "German Shorthaired Pointer", "great_pyrenees": "Great Pyrenees",
            "havanese": "Havanese", "japanese_chin": "Japanese Chin", "keeshond": "Keeshond",
            "leonberger": "Leonberger", "miniature_pinscher": "Miniature Pinscher", "newfoundland": "Newfoundland",
            "pomeranian": "Pomeranian", "pug": "Pug", "saint_bernard": "Saint Bernard", "samoyed": "Samoyed",
            "scottish_terrier": "Scottish Terrier", "shiba_inu": "Shiba Inu",
            "staffordshire_bull_terrier": "Staffordshire Bull Terrier", "wheaten_terrier": "Soft-coated Wheaten Terrier",
            "yorkshire_terrier": "Yorkshire Terrier"}


def pet_breed(stem):
    """(breed, "cat" or "dog") from an Oxford-IIIT Pet file name ("Bengal_12" -> ("Bengal", "cat")); cat names
    start with a capital letter, dog names do not."""
    name = re.sub(r"_\d+$", "", stem)
    if name[:1].isupper():
        return name.replace("_", " "), "cat"
    return PET_DOGS.get(name, name.replace("_", " ").title()), "dog"


def prepare_oxford_pets(source, data_dir, work, cap):
    """Oxford-IIIT Pet (Parkhi, Vedaldi, Zisserman and Jawahar, 2012; CC BY-SA 4.0): about 7,400 photos of 12 cat and
    25 dog breeds. Its 790 MB archive holds the photos in no particular order, so it is read from the web only until
    every breed has its share. "What breed of cat is this?" """
    quota, counts, rows = per_label(cap + source.test, 37), collections.Counter(), []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep the photo when its breed still needs one; True when every breed is full."""
        name = os.path.basename(member.name)
        if member.isfile() and name.endswith(".jpg"):
            breed, kind = pet_breed(name[:-4])
            if counts[breed] < quota:
                path = save(f"pet-{name[:-4]}", tar.extractfile(member).read(), folder)
                if path:
                    counts[breed] += 1
                    rows.append({"picture": path, "question": f"What breed of {kind} is this?",
                                 "answer": f"This looks like {a_or_an(breed)} {breed} {kind}.", "split": ""})
        return len(counts) >= 37 and min(counts.values()) >= quota

    stream_tar(PETS_URL, take, "the Oxford-IIIT Pet photos (790 MB at most)")
    say(f"  {len(rows)} pet photos of {len(counts)} breeds.")
    return rows


# ----------------------------------------------------------------- share-alike: HaGRIDv2 hand gestures

HAGRID = "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
HAGRID_V1 = HAGRID + "hagrid/hagrid_dataset_new_554800/hagrid_dataset/"
HAGRID_V2 = HAGRID + "hagrid_v2/hagrid_v2_zip/"
HAGRID_NOTES = HAGRID + "hagrid_v2/annotations_with_landmarks/annotations.zip"
GESTURE_QUESTION = "What gesture is this person making with their hand?"
# Each gesture, where its zip is (HaGRID's first release or v2), and what the hand does. Left out: middle_finger
# (rude), and grip, three3, three_gun, thumb_index and thumb_index2, whose exact hand shapes the labels do not say
# plainly enough to describe without guessing.
HAGRID_GESTURES = {
    "call": (HAGRID_V1, "The person is making a \"call me\" sign: the thumb and little finger are stretched out and "
                        "the other fingers folded, like a telephone."),
    "dislike": (HAGRID_V1, "The person is giving a thumbs-down: a fist with the thumb pointing down."),
    "fist": (HAGRID_V1, "The person is making a fist: all the fingers are curled into the palm."),
    "four": (HAGRID_V1, "The person is holding up four fingers, with the thumb folded in."),
    "like": (HAGRID_V1, "The person is giving a thumbs-up: a fist with the thumb pointing up."),
    "mute": (HAGRID_V1, "The person is holding a finger to the lips, the sign for \"be quiet\"."),
    "ok": (HAGRID_V1, "The person is making the OK sign: the thumb and index finger touch in a circle and the other "
                      "fingers are raised."),
    "one": (HAGRID_V2, "The person is holding up one finger, the index finger."),
    "palm": (HAGRID_V1, "The person is holding up an open hand with the palm facing forward and the fingers spread."),
    "peace": (HAGRID_V1, "The person is making a V sign (a peace sign): the index and middle fingers are raised in a "
                         "V, palm facing forward."),
    "peace_inverted": (HAGRID_V1, "The person is making a V sign with the back of the hand facing forward: the index "
                                  "and middle fingers are raised in a V."),
    "rock": (HAGRID_V2, "The person is making the \"rock on\" sign: the index and little fingers are raised and the "
                        "middle fingers folded."),
    "stop": (HAGRID_V1, "The person is holding up a flat hand, palm forward and fingers together, as if saying "
                        "\"stop\"."),
    "stop_inverted": (HAGRID_V1, "The person is holding up a flat hand with the back of the hand facing forward and "
                                 "the fingers together."),
    "three": (HAGRID_V1, "The person is holding up three fingers: the thumb, index and middle fingers."),
    "three2": (HAGRID_V1, "The person is holding up three fingers: the index, middle and ring fingers."),
    "two_up": (HAGRID_V1, "The person is holding up two fingers together, the index and middle fingers."),
    "two_up_inverted": (HAGRID_V1, "The person is holding up two fingers together, the index and middle fingers, with "
                                   "the back of the hand facing forward."),
    "grabbing": (HAGRID_V2, "The person's hand is curled with the fingers bent, as if about to grab something."),
    "hand_heart": (HAGRID_V2, "The person is making a heart shape with both hands."),
    "hand_heart2": (HAGRID_V2, "The person is making a small heart shape with the fingers."),
    "holy": (HAGRID_V2, "The person is holding both palms pressed together in front of the chest, as in prayer or a "
                        "thank-you."),
    "little_finger": (HAGRID_V2, "The person is holding up the little finger, with the other fingers folded."),
    "point": (HAGRID_V2, "The person is pointing with the index finger."),
    "take_picture": (HAGRID_V2, "The person is making a frame with the fingers of both hands, as if taking a "
                                "picture."),
    "timeout": (HAGRID_V2, "The person is making a T shape with both hands, the sign for \"time out\"."),
    "xsign": (HAGRID_V2, "The person is crossing the arms or hands in an X, a sign for \"no\" or \"stop\"."),
    "no_gesture": (HAGRID_V2, "The person's hands are relaxed: no particular hand gesture."),
}


def prepare_hagrid(source, data_dir, work, cap):
    """HaGRIDv2 (Kapitanov, Kvanchiani, Nagaev et al., 2024; a variant of CC BY-SA 4.0): photos people took of
    themselves making hand gestures, each labelled. The labels and the estimated ages come from the test part of the
    annotations (a 720 MB zip, of which only the needed files are read); the photos are read one by one out of each
    gesture's zip (40 GB each) by HTTP ranges. Only photos where every person's estimated age is 18 or more."""
    notes = remote_zip(HAGRID_NOTES)
    quota = per_label(cap + source.test, len(HAGRID_GESTURES))
    rows = []
    for gesture, (base, answer) in HAGRID_GESTURES.items():
        try:
            data = json.loads(notes.read(f"annotations/test/{gesture}.json"))
        except KeyError:
            continue
        ids = sorted(i for i, a in data.items()
                     if set(a.get("labels") or []) <= {gesture, "no_gesture"} and gesture in (a.get("labels") or [])
                     and (a.get("meta") or {}).get("age") and min(a["meta"]["age"]) >= 18)
        random.Random(f"181-{gesture}").shuffle(ids)
        ids = set(ids[:quota * 2])
        url = f"{base}{gesture}.zip"
        try:
            z = remote_zip(url)
        except Exception as e:  # noqa: BLE001 - one gesture that cannot be reached is left out
            say(f"  HaGRID {gesture}: left out ({e})")
            continue
        chosen = [(n, {"question": GESTURE_QUESTION, "answer": answer, "split": ""}) for n in z.namelist()
                  if os.path.splitext(os.path.basename(n))[0] in ids][:quota]
        z.close()
        say(f"  HaGRID {gesture}: reading {len(chosen)} photos.")
        rows += zip_members(source, data_dir, work, lambda u=url: remote_zip(u), chosen, workers=4)
    return rows


# ----------------------------------------------------------------- share-alike: PlantVillage

PLANTVILLAGE_URL = "https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/data.zip"
LEAF_QUESTION = "What is wrong with this plant leaf?"


def plantvillage_answer(folder):
    """The answer for a PlantVillage class folder ("Tomato___Early_blight", "Pepper,_bell___healthy")."""
    plant, disease = folder.split("___", 1)
    plant = re.sub(r"_?\(.*?\)", "", plant).replace("_", " ").strip(" ,").lower()
    plant = {"pepper, bell": "bell pepper"}.get(plant, plant)
    disease = disease.replace("_", " ").strip().replace("Haunglongbing", "Huanglongbing")
    if disease.lower() == "healthy":
        return f"This is {a_or_an(plant)} {plant} leaf. It looks healthy."
    disease = re.sub(r"\s+", " ", disease)
    disease = disease[0].lower() + disease[1:] if not disease.split()[0].isupper() else disease
    return f"This is {a_or_an(plant)} {plant} leaf. It looks like it has {disease}."


def prepare_plantvillage(source, data_dir, work, cap):
    """PlantVillage (Hughes and Salathe, 2015; CC BY-SA 3.0; the makers' copy on Hugging Face, mohanty/PlantVillage):
    54,000 photos of single leaves of 14 crops on a plain background, healthy or with one of 26 diseases. Only the
    colour photos used are read out of the 2.2 GB zip by HTTP ranges, an equal share for each class."""
    z = remote_zip(PLANTVILLAGE_URL)
    groups = {}
    for n in z.namelist():
        parts = n.split("/")
        if len(parts) == 4 and parts[1] == "color" and parts[3].lower().endswith((".jpg", ".jpeg", ".png")):
            groups.setdefault(parts[2], []).append(n)
    z.close()
    picked = even_pick(groups, cap + source.test, 191)
    chosen = [(n, {"question": LEAF_QUESTION, "answer": plantvillage_answer(n.split("/")[2]), "split": ""})
              for n in picked]
    say(f"  PlantVillage: reading {len(chosen)} leaf photos from {len(groups)} classes.")
    return zip_members(source, data_dir, work, lambda: remote_zip(PLANTVILLAGE_URL), chosen)


# ----------------------------------------------------------------- Pl@ntNet-300K (share-alike and non-commercial parts)

PLANTNET_RECORD = "10419064"
ORGANS = {"leaf": "its leaves", "flower": "its flowers", "fruit": "its fruit", "bark": "its bark",
          "habit": "the whole plant"}
LICENCE_NAMES = {"cc-by-sa": "CC BY-SA", "cc-by-nc": "CC BY-NC", "cc-by-nc-sa": "CC BY-NC-SA"}


def plantnet_rows(source, data_dir, work, cap, licences, seed):
    """Pl@ntNet-300K v2 rows for the photos whose own licence is in licences: an equal share for each species, read
    out of the 42 GB images zip by HTTP ranges. "What plant is this?" The test part gives the test pictures."""
    import requests
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    sizes = zenodo_sizes(PLANTNET_RECORD)
    species = {r["species_id"]: r for r in csv.DictReader(io.StringIO(
        session.get(zenodo(PLANTNET_RECORD, "species_metadata.csv"), timeout=120).content.decode("utf-8-sig")))}
    meta = os.path.join(work, "plantnet300K_v2_metadata.csv")
    download_file(zenodo(PLANTNET_RECORD, "plantnet300K_metadata.csv"), meta)
    groups = {}
    with open(meta, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["license"] in licences and r["species_id"] in species:
                groups.setdefault(r["species_id"], []).append(
                    (r["split"], r["species_id"], r["PN_hash"], r["organ"], r["author"], r["license"]))
    picked = even_pick(groups, cap + source.test, seed)
    chosen = []
    for split, sid, hash_, organ, author, licence in picked:
        sp = species[sid]
        answer = f"This looks like {sp['species']}, of the {sp['family']} family."
        if organ in ORGANS:
            answer += f" The photo shows {ORGANS[organ]}."
        chosen.append((f"images/{split}/{int(sid):04d}/{hash_}.jpg",
                       {"question": "What plant is this?", "answer": answer, "split": "test" if split == "test" else "",
                        "credit": f"Photo by {clean(author) or 'a Pl@ntNet user'}, {LICENCE_NAMES[licence]}, "
                                  "Pl@ntNet-300K"}))
    url, size = zenodo(PLANTNET_RECORD, "images.zip"), sizes["images.zip"]
    say(f"  Pl@ntNet-300K: reading {len(chosen)} photos of {len(groups)} species.")
    return zip_members(source, data_dir, work, lambda: remote_zip(url, size), chosen, workers=4)


def prepare_plantnet_sa(source, data_dir, work, cap):
    """Pl@ntNet-300K v2 (Garcin et al., 2021; Zenodo 10419064), the photos under CC BY-SA (305,614 of 306,087)."""
    return plantnet_rows(source, data_dir, work, cap, {"cc-by-sa"}, 193)


def prepare_plantnet_nc(source, data_dir, work, cap):
    """Pl@ntNet-300K v2, the 473 photos under CC BY-NC or CC BY-NC-SA."""
    return plantnet_rows(source, data_dir, work, cap, {"cc-by-nc", "cc-by-nc-sa"}, 197)


# ----------------------------------------------------------------- share-alike: HierText

HIERTEXT_GT = "https://raw.githubusercontent.com/google-research-datasets/hiertext/main/gt/validation.jsonl.gz"
HIERTEXT_IMAGES = "https://open-images-dataset.s3.amazonaws.com/ocr/validation.tgz"


def hiertext_answer(entry, most_words=120):
    """The legible text of one HierText photo, a paragraph a line, as "The text reads: ..."; "" when it has none or
    too much (more than most_words words)."""
    paragraphs = []
    for p in entry.get("paragraphs") or []:
        lines = [clean(l.get("text")) for l in p.get("lines") or [] if l.get("legible") and clean(l.get("text"))]
        if lines:
            paragraphs.append(" ".join(lines))
    words = sum(len(p.split()) for p in paragraphs)
    if not paragraphs or words > most_words:
        return ""
    return "The text reads:\n" + "\n".join(paragraphs)


def prepare_hiertext(source, data_dir, work, cap):
    """HierText (Long et al., 2022, Google; CC BY-SA 4.0): Open Images photos (CC BY 2.0) full of text (signs,
    packets, posters, notices), every word, line and paragraph written out by people. Its validation part (1,724
    photos; 12 MB of text and a 577 MB photo archive, read from the web until enough are taken) is used. Photos with
    no legible text or more than 120 words are left out. "Read out all the text in this picture." """
    answers = {}
    data = json.loads(gzip.decompress(get_bytes(HIERTEXT_GT)))
    for entry in data["annotations"]:
        answer = hiertext_answer(entry)
        if answer:
            answers[entry["image_id"]] = answer
    want, rows = cap + source.test, []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep a photo whose text is known; True when there are enough."""
        stem = os.path.splitext(os.path.basename(member.name))[0]
        if member.isfile() and stem in answers:
            path = save(f"hiertext-{stem}", tar.extractfile(member).read(), folder)
            if path:
                rows.append({"picture": path, "question": READ_TEXT_ALL, "answer": answers[stem], "split": ""})
        return len(rows) >= want

    stream_tar(HIERTEXT_IMAGES, take, "the HierText photos (577 MB at most)")
    return rows


# ----------------------------------------------------------------- share-alike: MapQA

MAPQA_U = gdrive("1ul_FcgoHbcm5txmYEr9IQtkN6e8sRZJy")


def mapqa_answer(answer):
    """A MapQA answer in words (a list of states becomes "Alaska, Hawaii and Idaho.")."""
    if isinstance(answer, list):
        items = [clean(a) for a in answer if clean(a)]
        return sentence(listed(items)) if items else ""
    return sentence(str(answer))


def prepare_mapqa(source, data_dir, work, cap):
    """MapQA (Chang, Palzer, Li, Fosler-Lussier and Xiao, 2022; CC BY-SA 4.0; the makers' Google Drive): MapQA-U, real
    choropleth maps of the United States (states shaded by a value, with a legend), with questions about them
    ("Which states have the lowest value in the West?"). The question files (80 MB) and the chosen maps are read out
    of the 2 GB zip by HTTP ranges; its dev part gives the test pictures. At most 3 questions per map."""
    z = remote_zip(MAPQA_U)
    rows = []
    for part, split, want in (("dev", "test", source.test * 3), ("test", "", cap)):
        per_map = {}
        for q in json.loads(z.read(f"MapQA_U/questions/{part}-QA.json")):
            answer = mapqa_answer(q.get("answer"))
            question = as_question(q.get("question", "").replace(" ?", "?"))
            if answer and question and len(answer.split()) <= 60:
                per_map.setdefault(q["map_id"], []).append((question, answer))
        maps = sorted(per_map)
        random.Random(f"199-{part}").shuffle(maps)
        chosen, count = [], 0
        for m in maps:
            if count >= want:
                break
            for question, answer in per_map[m][:3]:
                chosen.append((f"MapQA_U/images/{m}", {"question": question, "answer": answer, "split": split}))
                count += 1
        say(f"  MapQA: {len(chosen)} questions from its {part} part.")
        rows += zip_members(source, data_dir, work, lambda: remote_zip(MAPQA_U), chosen, workers=2)
    z.close()
    return rows


# ----------------------------------------------------------------- share-alike: Hypersim

HYPERSIM_META = "https://raw.githubusercontent.com/apple/ml-hypersim/main/evermotion_dataset/analysis/"
HYPERSIM_SCENES = "https://docs-assets.developer.apple.com/ml-research/datasets/hypersim/v1/scenes/"
ROOMS = {"Living room": "a living room", "Kitchen": "a kitchen", "Restaurant": "a restaurant", "Bedroom": "a bedroom",
         "Bathroom": "a bathroom", "Hall": "a hall", "Office": "an office", "Hotel lobby": "a hotel lobby",
         "Retail space": "a shop", "Dining room": "a dining room", "Office (home)": "a home office",
         "Transit station": "a station", "Lecture theater": "a lecture theatre", "Staircase": "a staircase",
         "Library": "a library", "Hallway": "a hallway", "Office (conference room)": "a meeting room",
         "Office (building foyer)": "the entrance hall of an office building",
         "Office (waiting area)": "a waiting area", "Courtyard": "a courtyard", "Art gallery": "an art gallery"}


def prepare_hypersim(source, data_dir, work, cap):
    """Hypersim (Roberts et al., 2021, Apple; CC BY-SA 3.0): photo-like computer-made pictures of 461 indoor scenes
    (people and logos were removed by its makers), each camera path labelled with the kind of room. One picture per
    camera path, an equal share for each kind of room; each picture is read out of its scene's zip (1 to 20 GB) by
    HTTP ranges. "What kind of room or place is this?" """
    paths = {}
    for r in csv.DictReader(io.StringIO(get_bytes(HYPERSIM_META + "metadata_camera_trajectories.csv").decode())):
        if r["Scene type"] in ROOMS:
            scene, cam = r["Animation"].rsplit("_cam_", 1)
            paths[(scene, "cam_" + cam)] = r["Scene type"]
    frames, splits = {}, {}
    for r in csv.DictReader(io.StringIO(get_bytes(HYPERSIM_META + "metadata_images_split_scene_v1.csv").decode())):
        key = (r["scene_name"], r["camera_name"])
        if key in paths and r["included_in_public_release"] == "True":
            frames.setdefault(key, []).append(int(r["frame_id"]))
            splits[r["scene_name"]] = r["split_partition_name"]
    groups = {}
    for key, room in paths.items():
        if frames.get(key):
            groups.setdefault(room, []).append(key)
    picked = even_pick(groups, cap + source.test, 211)
    by_scene = {}
    for scene, cam in picked:
        frame = random.Random(f"{scene}-{cam}").choice(frames[(scene, cam)])
        by_scene.setdefault(scene, []).append(
            (f"{scene}/images/scene_{cam}_final_preview/frame.{frame:04d}.tonemap.jpg",
             {"question": "What kind of room or place is this?",
              "answer": f"This is a computer-made picture (a 3D rendering) of {ROOMS[paths[(scene, cam)]]}.",
              "split": "test" if splits.get(scene) == "test" else ""}))
    say(f"  Hypersim: {len(picked)} pictures from {len(by_scene)} scenes.")
    rows = []
    for scene, chosen in sorted(by_scene.items()):
        url = f"{HYPERSIM_SCENES}{scene}.zip"
        try:
            rows += zip_members(source, data_dir, work, lambda u=url: remote_zip(u), chosen, workers=2)
        except Exception as e:  # noqa: BLE001 - one scene that cannot be read is left out
            say(f"  Hypersim {scene}: left out ({e})")
    return rows


# ----------------------------------------------------------------- share-alike: Open Food Facts

OFF_SEARCH = "https://search.openfoodfacts.org/search"
OFF_PRODUCT = "https://world.openfoodfacts.org/api/v2/product/"
OFF_IMAGES = "https://images.openfoodfacts.org/images/products/"
# Food categories (Open Food Facts tags), so the products are spread over the whole shop.
OFF_CATEGORIES = ("breakfast-cereals", "biscuits", "chocolates", "crisps", "yogurts", "cheeses", "breads",
                  "pastas", "rices", "canned-vegetables", "soups", "sauces", "jams", "fruit-juices", "sodas", "teas",
                  "coffees", "frozen-foods", "meals", "candies", "plant-based-milks", "milks", "spreads",
                  "condiments", "nuts", "canned-fishes", "sausages", "ice-creams", "cakes", "baby-foods")
OFF_CREDIT = "Open Food Facts contributors, product {code}: photos CC BY-SA 3.0, data ODbL, " \
             "https://world.openfoodfacts.org/product/{code}"


def off_image(code, images, kind):
    """The full-size address of a product's chosen English photo of a kind ("front", "ingredients" or "nutrition"),
    or "" when there is none."""
    chosen = images.get(f"{kind}_en") or {}
    if not chosen.get("rev"):
        return ""
    path = "/".join([code[:3], code[3:6], code[6:9], code[9:]]) if len(code) > 8 else code
    return f"{OFF_IMAGES}{path}/{kind}_en.{chosen['rev']}.full.jpg"


def off_products(per_category):
    """Open Food Facts products in English, the most scanned first, up to per_category from each category:
    [(category, hit)], each hit with its code, names, brands, quantity, nutriments and chosen photos."""
    found = []
    for category in OFF_CATEGORIES:
        hits, page = [], 1
        while len(hits) < per_category and page <= 10:
            data = get_json(OFF_SEARCH, {"q": f'categories_tags:"en:{category}" AND lang:en', "page_size": 100,
                                         "page": page, "sort_by": "-unique_scans_n",
                                         "fields": "code,product_name,product_name_en,brands,quantity,lang,"
                                                   "nutriments,images"})
            batch = data.get("hits") or []
            hits += [h for h in batch if (h.get("images") or {}).get("front_en")]
            if len(batch) < 100:
                break
            page += 1
            time.sleep(1)
        found += [(category, h) for h in hits[:per_category]]
        say(f"  Open Food Facts {category}: {min(len(hits), per_category)} products")
    return found


def off_name(hit):
    """ "Weetabix by Weetabix, 430 g" -> a plain sentence naming the product, or ""."""
    name = clean(hit.get("product_name_en") or hit.get("product_name"))
    if not name:
        return ""
    brands = hit.get("brands") or []
    brand = clean(brands[0] if isinstance(brands, list) and brands else brands if isinstance(brands, str) else "")
    text = f"This is {name}"
    if brand and brand.lower() not in name.lower():
        text += f" by {brand}"
    if clean(hit.get("quantity")):
        text += f", {clean(hit['quantity'])}"
    return text + "."


def prepare_openfoodfacts(source, data_dir, work, cap):
    """Open Food Facts (photos CC BY-SA 3.0, database ODbL 1.0): the English front photo of food products, with the
    name, brand and size people typed in. The most scanned products of 30 food categories, an equal share of each.
    "What product is this?" """
    items = []
    for category, hit in off_products(per_label(int((cap + source.test) * 1.2), len(OFF_CATEGORIES))):
        answer, url = off_name(hit), off_image(hit["code"], hit["images"], "front")
        if answer and url:
            items.append((f"off-front-{hit['code']}.jpg", url,
                          {"question": "What product is this?", "answer": answer, "split": "",
                           "credit": OFF_CREDIT.format(code=hit["code"])}))
    say(f"  Fetching {len(items)} Open Food Facts product photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4, pause=0.2)


NUTRIENTS = (("energy-kcal_100g", "energy {} kcal"), ("fat_100g", "fat {} g"),
             ("saturated-fat_100g", "of which saturates {} g"), ("carbohydrates_100g", "carbohydrate {} g"),
             ("sugars_100g", "of which sugars {} g"), ("fiber_100g", "fibre {} g"), ("proteins_100g", "protein {} g"),
             ("salt_100g", "salt {} g"))


def nutrition_answer(nutriments):
    """The nutrition values per 100 g in one sentence, or "" when the main ones are missing."""
    if not all(isinstance(nutriments.get(k), (int, float)) for k in ("energy-kcal_100g", "fat_100g",
                                                                     "carbohydrates_100g", "proteins_100g")):
        return ""
    parts = []
    for key, words in NUTRIENTS:
        value = nutriments.get(key)
        if isinstance(value, (int, float)):
            parts.append(words.format(f"{value:.2f}".rstrip("0").rstrip(".")))
    return "Per 100 g: " + "; ".join(parts) + "."


def prepare_openfoodfacts_labels(source, data_dir, work, cap):
    """Open Food Facts (photos CC BY-SA 3.0, database ODbL 1.0): the English ingredient-list and nutrition-table
    photos of food products, with what people typed from them: "Read the ingredients on this label." and "What does
    the nutrition label say per 100 grams?" The ingredient text is fetched product by product, gently (one a
    second). Ingredient lists over 120 words are left out."""
    items = []
    for category, hit in off_products(per_label(int((cap + source.test) * 0.7), len(OFF_CATEGORIES))):
        code, credit = hit["code"], OFF_CREDIT.format(code=hit["code"])
        url = off_image(code, hit["images"], "nutrition")
        answer = nutrition_answer(hit.get("nutriments") or {})
        if url and answer:
            items.append((f"off-nutrition-{code}.jpg", url,
                          {"question": "What does the nutrition label say per 100 grams?", "answer": answer,
                           "split": "", "credit": credit}))
        url = off_image(code, hit["images"], "ingredients")
        if url:
            try:
                product = get_json(OFF_PRODUCT + code + ".json", {"fields": "ingredients_text_en"}).get("product")
            except RuntimeError:
                product = None
            text = clean(re.sub(r"_", "", (product or {}).get("ingredients_text_en") or ""))
            if text and len(text.split()) <= 120:
                items.append((f"off-ingredients-{code}.jpg", url,
                              {"question": "Read the ingredients on this label.",
                               "answer": f"The ingredients are: {text.rstrip('.')}.", "split": "", "credit": credit}))
            time.sleep(1)
    say(f"  Fetching {len(items)} Open Food Facts label photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4, pause=0.2)


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
# Copyleft licences only (the open packs already take CC0, public domain and CC BY): CC BY-SA, GFDL, Free Art.
COMMONS_SA = re.compile(r"^(CC[ -]BY[ -]SA|GFDL|FAL|Free Art|Art Libre)", re.I)
COMMONS_NOT_PHOTO = re.compile(r"\b(art|drawings?|illustrations?|paintings?|logos?|icons?|emoji|sculptures?|signs?|"
                               r"advertis\w*|toys?|models?|in literature|videos?|audio|microscop\w*|diagrams?|"
                               r"stamps?|coats? of arms|maps?|statues?)\b", re.I)
NUDE = re.compile(r"\b(nude|naked|nudity|topless|undress\w*|erotic|sex\w*|porn\w*|lingerie|underwear)\b", re.I)


def commons_session():
    """A requests session for the Commons API, with the kit's plain name."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def commons_get(s, params, tries=8):
    """A Commons API answer (JSON), waiting politely when the server asks to slow down."""
    params = dict(params, format="json", maxlag=5)
    wait = 5
    for _ in range(tries):
        try:
            r = s.get(COMMONS_API, params=params, timeout=60)
            if r.status_code == 200:
                data = r.json()
                if (data.get("error") or {}).get("code") != "maxlag":
                    return data
            after = r.headers.get("Retry-After", "")
            pause = int(after) if after.isdigit() else wait
        except Exception:  # noqa: BLE001 - network trouble: wait and try again
            pause = wait
        time.sleep(min(pause, 120))
        wait = min(wait * 2, 120)
    raise RuntimeError("Wikimedia Commons kept refusing requests; try again later.")


def commons_members(s, category, kind):
    """The titles of a Commons category's members of one kind ("file" or "subcat")."""
    titles, params = [], {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                          "cmtype": kind, "cmlimit": 500}
    while True:
        data = commons_get(s, params)
        titles += [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])]
        if "continue" not in data:
            return titles
        params.update(data["continue"])
        time.sleep(1)


def commons_text(caption, description):
    """A file's English caption, or else the start of its description, as a sentence of 5 words or more; or ""."""
    from personal_sources import first_sentences
    for text in (clean(caption), first_sentences(re.sub(r"<[^>]+>", " ", clean(description)), 60)):
        text = re.sub(r"^\s*English\s*:\s*", "", clean(text))
        if len(text.split()) >= 5 and not re.match(r"^[\d\W]", text) and not text.lower().startswith("file:"):
            return sentence(text)
    return ""


def commons_sa_entries(s, titles):
    """[(title, picture address, credit, caption or description)] for files whose licence is copyleft (CC BY-SA,
    GFDL, Free Art; never NC or ND), 50 files a request."""
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": sources.LONG_SIDE,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription",
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
            if not COMMONS_SA.match(licence) or re.search(r"\bN[CD]\b", licence.upper()) \
                    or info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                continue
            artist = clean(re.sub(r"<[^>]+>", " ", (meta.get("Artist") or {}).get("value") or "")) or "unknown"
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            text = commons_text(captions.get(f"M{p['pageid']}"), (meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}", text))
        time.sleep(1)
    return out


def commons_file_name(prefix, title):
    """A training copy's file name for a Commons file."""
    return f"{prefix}-" + re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80] + ".jpg"


COMMONS_BREEDS = [("dog", "Dog breeds by name", "What breed of dog is this?"),
                  ("cat", "Cat breeds", "What breed of cat is this?"),
                  ("horse", "Horse breeds by name", "What breed of horse is this?"),
                  ("cattle", "Cattle breeds by name", "What breed of cattle is this?"),
                  ("sheep", "Sheep breeds by name", "What breed of sheep is this?"),
                  ("goat", "Goat breeds by name", "What breed of goat is this?"),
                  ("pig", "Pig breeds", "What breed of pig is this?"),
                  ("chicken", "Chicken breeds", "What breed of chicken is this?"),
                  ("rabbit", "Rabbit breeds", "What breed of rabbit is this?")]
BREED_NOT_ONE = re.compile(r"\b(by|breeds|groups?|unidentified|mixed|crossbreeds?|history|extinct|landrace|types?|"
                           r"illustrations?|in art|heads?|portraits?|coat|colou?rs?|female|male|puppies|kittens|"
                           r"foals|lambs|kids|chicks|associations?|riding|wool|mini)\b", re.I)
PEOPLE_WORDS = re.compile(r"\b(person|people|man|men|woman|women|girl|boy|child\w*|kids?|owner|rider|farmer|"
                          r"handler|judge|breeder|family|bab(y|ies))\b", re.I)


def breed_name(category, animal):
    """The breed's name from its Commons category ("Category:Harlequin rabbits" -> "Harlequin rabbit")."""
    name = re.sub(r"\s*\([^)]*\)$", "", category.split(":", 1)[-1]).strip()
    words = name.split()
    if len(words) > 1 and words[-1].lower() in (animal + "s", plural(animal)):
        words[-1] = animal
    return " ".join(words)


def prepare_commons_breeds_sa(source, data_dir, work, cap, per_breed=4):
    """Wikimedia Commons breed categories (dogs, cats, horses, cattle, sheep, goats, pigs, chickens, rabbits): a few
    photos under CC BY-SA or GFDL from each breed, the animals taken in turn. Files whose words mention people are
    left out. "What breed of dog is this?" """
    s, rng = commons_session(), random.Random(223)
    queues = []
    for animal, parent, question in COMMONS_BREEDS:
        breeds = [c for c in commons_members(s, parent, "subcat") if not BREED_NOT_ONE.search(c.split(":", 1)[-1])]
        rng.shuffle(breeds)
        queues.append((animal, question, breeds))
        say(f"  Commons: {len(breeds)} {animal} breeds")
    want, items = int((cap + source.test) * 1.1), []
    while len(items) < want and any(q[2] for q in queues):
        for animal, question, breeds in queues:
            if not breeds or len(items) >= want:
                continue
            category = breeds.pop()
            breed = breed_name(category, animal)
            titles = [t for t in commons_members(s, category.split(":", 1)[-1], "file")
                      if not COMMONS_NOT_PHOTO.search(t) and not PEOPLE_WORDS.search(t)]
            rng.shuffle(titles)
            got = 0
            for title, url, credit, text in commons_sa_entries(s, titles[:per_breed * 3]):
                if PEOPLE_WORDS.search(text) or NUDE.search(text) or got >= per_breed:
                    continue
                items.append((commons_file_name("breed-sa", title), url,
                              {"question": question, "split": "", "credit": credit,
                               "answer": f"It looks like {a_or_an(breed)} {breed}, a breed of {animal}."}))
                got += 1
    say(f"  Fetching {len(items)} Commons breed photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=2, pause=0.5)


COMMONS_FOOD = {
    "Fried eggs": ("How is this egg cooked?", "It is fried.", True),
    "Boiled eggs": ("How is this egg cooked?", "It is boiled.", False),
    "Scrambled eggs": ("How is this egg cooked?", "It is scrambled.", True),
    "Poached eggs": ("How is this egg cooked?", "It is poached.", True),
    "Cooked rice": ("Is this rice cooked?", "Yes, it is cooked.", False),
    "Toast": ("Is this bread toasted?", "Yes, it is toasted.", False),
    "Frozen food": ("Is this food frozen?", "Yes, it is frozen.", True),
    "Steaks": ("What food is this?", "This is a steak.", False),
    "Spoiled food": ("Is this food safe to eat?", "No: it is spoiled (mouldy).", True),
    "Soups": ("What food is this?", "This is a soup.", False),
    "Salads": ("What food is this?", "This is a salad.", False),
    "Sandwiches": ("What food is this?", "This is a sandwich.", False),
    "Pizza": ("What food is this?", "This is a pizza.", False),
    "Cakes": ("What food is this?", "This is a cake.", False),
    "Pasta dishes": ("What food is this?", "This is a pasta dish.", False),
    "Curries": ("What food is this?", "This is a curry.", False),
    "Breads": ("What food is this?", "This is bread.", False),
    "Fruit": ("What food is this?", "This is fruit.", False),
    "Vegetables": ("What food is this?", "These are vegetables.", False),
}


def prepare_commons_food_sa(source, data_dir, work, cap):
    """Wikimedia Commons food categories: photos under CC BY-SA or GFDL, with the category's question and, when the
    file has a real caption or description (and it names no people), "Write a short description ..." too."""
    s, items = commons_session(), []
    per_category = per_label(int((cap + source.test) * 0.8), len(COMMONS_FOOD))
    for category, (question, answer, deeper) in COMMONS_FOOD.items():
        titles = commons_members(s, category, "file")
        if deeper:
            for sub in commons_members(s, category, "subcat"):
                if not COMMONS_NOT_PHOTO.search(sub):
                    titles += commons_members(s, sub.split(":", 1)[-1], "file")
        titles = [t for t in dict.fromkeys(titles) if not COMMONS_NOT_PHOTO.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 4]):
            if found >= per_category or NUDE.search(f"{title} {text}"):
                continue
            name = commons_file_name("food-sa", title)
            items.append((name, url, {"question": question, "answer": answer, "split": "", "credit": credit}))
            if text and not PEOPLE_WORDS.search(text):
                items.append((name, url, {"question": sources.ALT_TEXT, "answer": text, "split": "",
                                          "credit": credit}))
            found += 1
        say(f"  Commons {category}: {found} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# Medical categories: (Commons category, the name for "This looks like ...", a plain explanation).
COMMONS_MEDICAL = [
    ("Bruises", "a bruise", "bleeding under the skin after a knock"),
    ("Burns (injury)", "a burn", "skin damaged by heat, chemicals or electricity"),
    ("Sunburn", "sunburn", "red, sore skin from too much sun"),
    ("Psoriasis", "psoriasis", "thick, red, scaly patches that come and go"),
    ("Eczema", "eczema", "dry, itchy, inflamed skin"),
    ("Acne vulgaris", "acne", "spots, blackheads and pimples"),
    ("Herpes labialis", "a cold sore", "small painful blisters on the lip caused by a virus"),
    ("Herpes zoster", "shingles (herpes zoster)", "a painful, blistering rash on one side of the body"),
    ("Urticaria", "hives (urticaria)", "raised, itchy welts that come and go"),
    ("Insect bites and stings", "an insect bite or sting", ""),
    ("Varicose veins", "varicose veins", "swollen, twisted veins, usually in the legs"),
    ("Cellulitis", "cellulitis", "a skin infection that makes the skin red, hot and swollen"),
    ("Warts", "a wart", "a harmless growth caused by a virus"),
    ("Vitiligo", "vitiligo", "patches of skin that have lost their colour"),
    ("Rosacea", "rosacea", "redness and small bumps on the face"),
    ("Gout", "gout", "a painful, swollen joint caused by uric acid crystals"),
    ("Onychomycosis", "a fungal nail infection", "thick, discoloured nails"),
    ("Conjunctivitis", "conjunctivitis (pink eye)", "a red, irritated eye"),
    ("Hordeolum", "a stye", "a painful red lump on the edge of the eyelid"),
    ("Ingrown nails", "an ingrown nail", "a nail growing into the skin beside it"),
    ("Blisters", "a blister", "a bubble of fluid under the skin"),
    ("Scars", "a scar", "skin that has healed after an injury"),
    ("Wounds", "a wound", ""),
    ("Edema", "swelling (oedema)", "fluid building up under the skin"),
    ("Jaundice", "jaundice", "yellowing of the skin or the whites of the eyes"),
]
# An adult in a file's own words: a man or woman, an adult, or an age of 18 or more.
ADULT = re.compile(r"\b(man|woman|men|women|adult|gentleman|lady|elderly|old man|old woman|(\d{2,3})[- ]year[- ]old|"
                   r"aged (\d{2,3})|age (\d{2,3}))\b", re.I)


def is_adult_text(text):
    """True when a file's words say the person is an adult and never name a child (an age, when given, 18 or more)."""
    if CHILD_WORDS.search(text) or re.search(r"\b(infant|newborn|neonat\w*|paediatric|pediatric)\b", text, re.I):
        return False
    found = ADULT.search(text)
    if not found:
        return False
    age = next((g for g in found.groups()[1:] if g), None)
    return age is None or int(age) >= 18


def prepare_commons_medical_sa(source, data_dir, work, cap):
    """Wikimedia Commons medical categories (bruises, burns, rashes, eye and nail problems ...): photos under CC BY-SA
    or GFDL whose own words say the person is an adult (a man, a woman, an adult, or an age of 18 or more) and never
    name a child; nothing intimate, nude or sexual. Commons gives no ages of its own, so a file without such words is
    left out. "What could this be?" with the condition, its plain explanation and DOCTOR."""
    s, items = commons_session(), []
    per_category = per_label(int((cap + source.test) * 1.1), len(COMMONS_MEDICAL))
    for category, name, explanation in COMMONS_MEDICAL:
        try:
            titles = commons_members(s, category, "file")
        except RuntimeError:
            continue
        titles = [t for t in titles if not COMMONS_NOT_PHOTO.search(t) and not INTIMATE_SITE.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 8]):
            words = f"{title} {text}"
            if found >= per_category or not is_adult_text(words) or INTIMATE_SITE.search(words) or NUDE.search(words):
                continue
            answer = f"A photo of an adult. {looks_like(name, explanation)} {DOCTOR}"
            items.append((commons_file_name("medical-sa", title), url,
                          {"question": "What could this be?", "answer": answer, "split": "", "credit": credit}))
            found += 1
        say(f"  Commons {category}: {found} photos of adults")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=2, pause=0.5)


# ----------------------------------------------------------------- share-alike (GPL): PAPILA

PAPILA_URL = "https://ndownloader.figshare.com/files/35013982"
PAPILA_SIZE = 590857635


def xlsx_rows(data):
    """The cells of the first sheet of an .xlsx file as {row number: {column letters: text}} (a tiny reader, so the
    kit needs no spreadsheet package)."""
    x = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in x.namelist():
        for si in re.findall(r"<si>(.*?)</si>", x.read("xl/sharedStrings.xml").decode("utf-8"), re.S):
            shared.append("".join(re.findall(r"<t[^>]*>([^<]*)</t>", si)))
    rows = {}
    for ref, attrs, value in re.findall(r'<c r="([A-Z]+\d+)"([^>]*)>(?:<f>[^<]*</f>)?<v>([^<]*)</v>',
                                        x.read("xl/worksheets/sheet1.xml").decode("utf-8")):
        col, row = re.match(r"([A-Z]+)(\d+)", ref).groups()
        rows.setdefault(int(row), {})[col] = shared[int(value)] if 't="s"' in attrs else value
    return rows


def papila_answer(eye, sex, age, diagnosis):
    """The answer for one PAPILA fundus photo."""
    side = {"OD": "right", "OS": "left"}[eye]
    who = {"0": "man", "1": "woman"}.get(sex, "person")
    text = (f"A photo of the back of the {side} eye (a fundus photo), showing the optic nerve head and the blood "
            f"vessels of the retina, of a {who} aged {age}. ")
    if diagnosis == "0":
        text += "Eye doctors judged this eye healthy, with no sign of glaucoma."
    elif diagnosis == "1":
        text += looks_like("glaucoma", "damage to the optic nerve that slowly narrows the field of vision")
    else:
        text += "Eye doctors marked this eye as a glaucoma suspect: some signs that need to be watched."
    return f"{text} {DOCTOR}"


def prepare_papila(source, data_dir, work, cap):
    """PAPILA (Kovalyk et al., 2022; figshare 14798004, GPL-3.0 or later, a copyleft licence): 488 fundus photos of
    both eyes of 244 patients in Spain, with age, sex and the eye doctors' diagnosis (healthy, glaucoma or glaucoma
    suspect). Adults only (18 or more). The tables and the photos are read out of the 590 MB zip by HTTP ranges."""
    z = remote_zip(PAPILA_URL, PAPILA_SIZE)
    base = next(n for n in z.namelist() if n.endswith("/ClinicalData/"))[:-len("ClinicalData/")]
    chosen = []
    for eye in ("OD", "OS"):
        table = xlsx_rows(z.read(f"{base}ClinicalData/patient_data_{eye.lower()}.xlsx"))
        header_row = next(r for r, cells in sorted(table.items()) if "Age" in cells.values())
        columns = {v: c for c, v in table[header_row].items()}
        for r, cells in sorted(table.items()):
            ident = next((v for v in cells.values() if re.fullmatch(r"#\d+", v)), "")
            try:
                age = int(float(cells.get(columns["Age"], "")))
            except ValueError:
                continue
            diagnosis = cells.get(columns["Diagnosis"], "").split(".")[0]
            if not ident or age < 18 or diagnosis not in ("0", "1", "2"):
                continue
            sex = cells.get(columns["Gender"], "").split(".")[0]
            chosen.append((f"{base}FundusImages/RET{ident[1:]}{eye}.jpg",
                           {"question": "What does this eye picture show?",
                            "answer": papila_answer(eye, sex, age, diagnosis), "split": ""}))
    z.close()
    say(f"  PAPILA: {len(chosen)} fundus photos of adults.")
    return zip_members(source, data_dir, work, lambda: remote_zip(PAPILA_URL, PAPILA_SIZE),
                       chosen[:cap + source.test], workers=2)


# ----------------------------------------------------------------- non-commercial: RAVDESS stills

RAVDESS_RECORD = "1188976"
# RAVDESS emotion codes: the visible signs first, then a careful reading ({} is "He" or "She", [] "his" or "her").
RAVDESS_EXPRESSIONS = {
    "01": "The face is at rest: the mouth relaxed and the eyebrows level. {} looks neutral, showing no particular "
          "expression.",
    "02": "The face is relaxed and soft, the eyes calm and the brow smooth. {} looks calm.",
    "03": "The corners of the mouth are drawn up and the cheeks raised. {} seems to be happy.",
    "04": "The corners of the mouth turn down and the inner eyebrows are drawn up. {} looks sad.",
    "05": "The eyebrows are drawn down and together, the eyes narrowed and the lips pressed or tense. {} looks angry.",
    "06": "The eyebrows are raised and drawn together, the eyes wide and the mouth stretched. {} looks afraid.",
    "07": "The nose is wrinkled and the upper lip raised. {} looks disgusted.",
    "08": "The eyebrows are raised high and the eyes wide open. {} looks surprised.",
}


def ravdess_answer(name):
    """The answer for one RAVDESS video ("02-01-06-01-02-01-12.mp4": video only, speech, fearful, normal, ..., actor
    12; odd actors are men, even actors women)."""
    parts = os.path.basename(name)[:-4].split("-")
    channel, emotion, strength, actor = parts[1], parts[2], parts[3], int(parts[6])
    who, he = ("man", "He") if actor % 2 else ("woman", "She")
    text = (f"A photo of a young {who}'s face and shoulders against a plain white background, looking at the camera"
            f"{', in the middle of speaking' if channel == '01' else ', singing'}. ")
    text += RAVDESS_EXPRESSIONS[emotion].format(he)
    if strength == "02" and emotion != "01":
        text += " The expression is strong."
    return text + " This expression was posed by an actor for a recording."


def prepare_ravdess(source, data_dir, work, cap):
    """RAVDESS (Livingstone and Russo, 2018; Zenodo 1188976, CC BY-NC-SA 4.0): videos of 24 professional actors (12
    men, 12 women, all adults) speaking and singing with eight posed expressions at two strengths. One still from the
    middle of each chosen video (PyAV; install requirements-video.txt), an equal share for each expression; only the
    chosen videos (about 4 MB each) are read out of the 48 actor zips by HTTP ranges and kept in the downloads
    folder."""
    sizes = {k: v for k, v in zenodo_sizes(RAVDESS_RECORD).items() if k.startswith("Video_")}
    groups = {}
    for name in sorted(sizes):
        z = remote_zip(zenodo(RAVDESS_RECORD, name), sizes[name])
        for member in z.namelist():
            base = os.path.basename(member)
            if re.fullmatch(r"0[12]-0[12]-0[1-8]-0[12]-0[12]-0[12]-\d\d\.mp4", base):
                groups.setdefault(base.split("-")[2], []).append((name, member))
        z.close()
    picked = even_pick(groups, cap + source.test, 227)
    rows = []
    for name in sorted({p[0] for p in picked}):
        chosen = [(member, {"question": EXPRESSION_QUESTION, "answer": ravdess_answer(member), "split": ""})
                  for zip_name, member in picked if zip_name == name]
        say(f"  RAVDESS {name}: {len(chosen)} stills.")
        url, size = zenodo(RAVDESS_RECORD, name), sizes[name]
        rows += zip_members(source, data_dir, work, lambda u=url, s=size: remote_zip(u, s), chosen, workers=3,
                            prepare_picture=video_still)
    return rows


# ----------------------------------------------------------------- non-commercial: How2Sign stills

HOW2SIGN_CLIPS = gdrive("1VX7n0jjW0pW3GEdgOks3z8nqE6iI6EnW")         # train_rgb_front_clips.zip, 31 GB


def prepare_how2sign(source, data_dir, work, cap):
    """How2Sign (Duarte et al., 2021; CC BY-NC 4.0; the makers' Google Drive): sentence clips of adult signers
    signing American Sign Language in front of a green screen, front view. One still from the middle of each chosen
    clip (PyAV; install requirements-video.txt), one clip per instructional video first so every signer and topic
    is spread; only the chosen clips are read out of the 31 GB zip by HTTP ranges. A still cannot show what is being
    said, so the answer says what can be seen."""
    z = remote_zip(HOW2SIGN_CLIPS)
    groups = {}
    for member in z.namelist():
        if member.endswith(".mp4"):
            groups.setdefault(os.path.basename(member).split("_")[0][:11], []).append(member)
    z.close()
    picked = even_pick(groups, cap + source.test, 229)
    answer = ("A person in front of a plain green background is signing in American Sign Language, using their "
              "hands, face and body. From a single picture the meaning cannot be read.")
    chosen = [(m, {"question": "What is this person doing?", "answer": answer, "split": ""}) for m in picked]
    say(f"  How2Sign: {len(chosen)} stills from {len(groups)} videos.")
    return zip_members(source, data_dir, work, lambda: remote_zip(HOW2SIGN_CLIPS), chosen, workers=3,
                       prepare_picture=video_still)


# ----------------------------------------------------------------- research: birds, plant diseases, captions

CUB_URL = "https://data.caltech.edu/records/65de6-vp158/files/CUB_200_2011.tgz?download=1"
COMPOUND = re.compile(r"\b(\w+) (footed|throated|winged|bellied|crowned|headed|billed|tailed|breasted|eyed|backed|"
                      r"sided|capped|naped|rumped|cheeked|necked|legged|chinned|faced|fronted|shouldered|crested|"
                      r"collared|bellied|banded|spotted|striped)\b", re.I)


def bird_name(folder):
    """A CUB species in words ("001.Black_footed_Albatross" -> "Black-footed Albatross")."""
    name = folder.split(".", 1)[-1].replace("_", " ")
    return COMPOUND.sub(lambda m: f"{m.group(1)}-{m.group(2).lower()}", name)


def prepare_cub200(source, data_dir, work, cap):
    """CUB-200-2011 (Wah, Branson, Welinder, Perona and Belongie, 2011; Caltech): 11,788 Flickr photos of 200 North
    American bird species. The 1.1 GB archive is downloaded once (kept, and it resumes), then read once, taking an
    equal share of each species. "What bird is this?" """
    import tarfile
    archive = os.path.join(work, "CUB_200_2011.tgz")
    say("  Downloading CUB-200-2011 (1.1 GB, kept in the downloads folder; it resumes if stopped).")
    download_file(CUB_URL, archive)
    quota, counts, rows = per_label(cap + source.test, 200), collections.Counter(), []
    folder = os.path.join(data_dir, source.key)
    with tarfile.open(archive, "r|gz") as tar:
        for m in tar:
            parts = m.name.split("/")
            if m.isfile() and len(parts) == 4 and parts[1] == "images" and parts[3].endswith(".jpg") \
                    and counts[parts[2]] < quota:
                path = save(f"cub-{parts[3][:-4]}", tar.extractfile(m).read(), folder)
                if path:
                    counts[parts[2]] += 1
                    bird = bird_name(parts[2])
                    rows.append({"picture": path, "question": "What bird is this?",
                                 "answer": f"This looks like {a_or_an(bird)} {bird}.", "split": ""})
    say(f"  {len(rows)} bird photos of {len(counts)} species.")
    return rows


PLANTDOC_REPO = "pratikkayal/PlantDoc-Dataset"
PLANTDOC_ANSWERS = {
    "Apple Scab Leaf": "an apple leaf with apple scab", "Apple leaf": "a healthy apple leaf",
    "Apple rust leaf": "an apple leaf with rust", "Bell_pepper leaf": "a healthy bell pepper leaf",
    "Bell_pepper leaf spot": "a bell pepper leaf with leaf spot", "Blueberry leaf": "a healthy blueberry leaf",
    "Cherry leaf": "a healthy cherry leaf", "Corn Gray leaf spot": "a corn (maize) leaf with grey leaf spot",
    "Corn leaf blight": "a corn (maize) leaf with leaf blight", "Corn rust leaf": "a corn (maize) leaf with rust",
    "Peach leaf": "a healthy peach leaf", "Potato leaf early blight": "a potato leaf with early blight",
    "Potato leaf late blight": "a potato leaf with late blight", "Raspberry leaf": "a healthy raspberry leaf",
    "Soyabean leaf": "a healthy soybean leaf", "Squash Powdery mildew leaf": "a squash leaf with powdery mildew",
    "Strawberry leaf": "a healthy strawberry leaf", "Tomato Early blight leaf": "a tomato leaf with early blight",
    "Tomato Septoria leaf spot": "a tomato leaf with Septoria leaf spot", "Tomato leaf": "a healthy tomato leaf",
    "Tomato leaf bacterial spot": "a tomato leaf with bacterial spot",
    "Tomato leaf late blight": "a tomato leaf with late blight",
    "Tomato leaf mosaic virus": "a tomato leaf with mosaic virus",
    "Tomato leaf yellow virus": "a tomato leaf with yellow leaf curl virus", "Tomato mold leaf": "a tomato leaf with leaf mould",
    "grape leaf": "a healthy grape leaf", "grape leaf black rot": "a grape leaf with black rot",
}


def github_files(repo, branch="master"):
    """Every file path in a GitHub repository (one request to GitHub's tree API)."""
    data = get_json(f"https://api.github.com/repos/{repo}/git/trees/{branch}", {"recursive": "1"})
    return [t["path"] for t in data.get("tree", []) if t.get("type") == "blob"]


def prepare_plantdoc(source, data_dir, work, cap):
    """PlantDoc (Singh et al., 2020): 2,598 photos of crop leaves found on Google Images and Ecosia, healthy or with
    one of 17 diseases, labelled by the authors (the pictures' own owners are unknown). Fetched file by file from the
    makers' GitHub repository; its test folder gives the test pictures. "What is wrong with this plant leaf?" """
    groups = {}
    for path in github_files(PLANTDOC_REPO):
        parts = path.split("/")
        if len(parts) == 3 and parts[1] in PLANTDOC_ANSWERS and parts[2].lower().endswith((".jpg", ".jpeg", ".png")):
            groups.setdefault(parts[1], []).append(path)
    items = []
    for path in even_pick(groups, int((cap + source.test) * 1.1), 233):
        split, label, name = path.split("/")
        items.append((re.sub(r"[^\w.-]", "_", f"{split}-{label}-{name}")[-120:].rsplit(".", 1)[0] + ".jpg",
                      f"https://raw.githubusercontent.com/{PLANTDOC_REPO}/master/{urllib.parse.quote(path)}",
                      {"question": LEAF_QUESTION, "split": "test" if split == "test" else "",
                       "answer": f"This looks like {PLANTDOC_ANSWERS[label]}."}))
    say(f"  Fetching {len(items)} PlantDoc photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


NOCAPS_VAL = gdrive("1zrsLhT94nazJ5h-LleHsU4AojHBqpcA0")


def prepare_nocaps(source, data_dir, work, cap):
    """nocaps (Agrawal et al., 2019): 4,500 Open Images photos (CC BY 2.0) with ten one-sentence descriptions each,
    written by people (no licence is stated for the descriptions). The first good description of each photo.
    "child" marks photos whose descriptions name a child."""
    data = json.loads(get_bytes(NOCAPS_VAL))
    captions = {}
    for a in data["annotations"]:
        captions.setdefault(a["image_id"], []).append(clean(a["caption"]))
    items = []
    for image in data["images"]:
        texts = captions.get(image["id"]) or []
        first = next((t for t in texts if len(t.split()) >= 5), "")
        if first:
            items.append((image["file_name"], f"https://s3.amazonaws.com/nocaps/val/{image['file_name']}",
                          {"question": BRIEF, "answer": sentence(first), "split": "",
                           "child": any(CHILD_WORDS.search(t) for t in texts)}))
    random.Random(239).shuffle(items)
    items = items[:int((cap + source.test) * 1.05)]
    say(f"  Fetching {len(items)} nocaps photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=6)


def prepare_vizwiz_quality(source, data_dir, work, cap):
    """VizWiz Image Quality Issues (Chiu et al., 2020): photos blind people took, with what at least three of five
    people said is wrong with each (blurry, too dark, cut off ...). The labels have no licence or terms written
    (the photos are CC BY 4.0). The work is done by more_sources.prepare_vizwiz_quality."""
    from more_sources import prepare_vizwiz_quality as prepare
    return prepare(source, data_dir, work, cap)


# ----------------------------------------------------------------- research: Rico phone screens

RICO_URL = "https://storage.googleapis.com/crowdstf-rico-uiuc-4540/rico_dataset_v0.1/unique_uis.tar.gz"
SCREEN2WORDS = "https://raw.githubusercontent.com/google-research-datasets/screen2words/main/"
WIDGETS = "https://raw.githubusercontent.com/google-research-datasets/widget-caption/main/widget_captions.csv"


def prepare_rico_screens(source, data_dir, work, cap):
    """Screen2Words (Wang et al., 2021, Google; summaries CC BY 4.0) on Rico (Deka et al., 2017; the screenshots have
    no licence or terms written): Android app screens, each summed up in a sentence by five people; the first good
    one is used. Rico's 6.4 GB archive holds the screens in no particular order, so it is read from the web only until
    enough are taken. "What is on this phone screen?" """
    summaries = {}
    for r in csv.DictReader(io.StringIO(get_bytes(SCREEN2WORDS + "screen_summaries.csv").decode("utf-8"))):
        if r["screenId"] not in summaries and len(clean(r["summary"]).split()) >= 4:
            summaries[r["screenId"]] = sentence(r["summary"])
    tests = set(get_bytes(SCREEN2WORDS + "split/test_screens.txt").decode().split())
    want, rows = cap + source.test, []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep a screen that has a summary; True when there are enough."""
        stem, ext = os.path.splitext(os.path.basename(member.name))
        if ext == ".jpg" and stem in summaries:
            path = save(f"rico-{stem}", tar.extractfile(member).read(), folder)
            if path:
                rows.append({"picture": path, "question": "What is on this phone screen?",
                             "answer": f"This app screen shows {summaries[stem][0].lower()}{summaries[stem][1:]}",
                             "split": "test" if stem in tests else ""})
        return len(rows) >= want

    stream_tar(RICO_URL, take, "the Rico phone screens (6.4 GB at most)")
    return rows


def widget_node(view, node_id):
    """The view-hierarchy node a Widget Captioning nodeId points to ("0.0.1.2"), or None."""
    node = (view.get("activity") or {}).get("root")
    try:
        for index in node_id.split(".")[1:]:
            node = node["children"][int(index)]
    except (KeyError, IndexError, TypeError, ValueError):
        return None
    return node


def widget_picture(jpg, view, node_id):
    """The screenshot with a thick red box drawn round the widget, as JPEG bytes; None when the widget's place is
    not known or is too small or too big."""
    from PIL import Image, ImageDraw
    node = widget_node(view, node_id)
    bounds = (node or {}).get("bounds")
    if not bounds or len(bounds) != 4:
        return None
    img = Image.open(io.BytesIO(jpg)).convert("RGB")
    scale = img.width / 1440                                       # Rico's hierarchies are in 1440 x 2560 pixels
    x0, y0, x1, y1 = (v * scale for v in bounds)
    if x1 - x0 < 8 or y1 - y0 < 8 or (x1 - x0) * (y1 - y0) > 0.5 * img.width * img.height:
        return None
    ImageDraw.Draw(img).rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), outline=(255, 0, 0), width=5)
    out = io.BytesIO()
    img.save(out, "JPEG", quality=92)
    return out.getvalue()


def prepare_rico_widgets(source, data_dir, work, cap):
    """Widget Captioning (Li et al., 2020, Google; captions CC BY 4.0) on Rico screens (no licence or terms written):
    what a button or other control on an Android screen does, in people's words. The control is outlined in red on
    the screenshot (its place comes from the screen's view hierarchy in the same archive), one control per screen.
    Rico's archive is read from the web only until enough are taken. "What does the control outlined in red do?" """
    wanted = {}
    for r in csv.DictReader(io.StringIO(get_bytes(WIDGETS).decode("utf-8"))):
        if r["datasetId"] == "rc" and r["screenId"] not in wanted:
            words = collections.Counter(clean(c).lower() for c in r["captions"].split("|") if clean(c))
            if words:
                wanted[r["screenId"]] = (r["nodeId"], words.most_common(1)[0][0])
    want, rows, pending = cap + source.test, [], {}
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep the picture and view of a wanted screen until both are there; True when there are enough."""
        stem, ext = os.path.splitext(os.path.basename(member.name))
        if stem in wanted and ext in (".jpg", ".json"):
            pending.setdefault(stem, {})[ext] = tar.extractfile(member).read()
            if len(pending[stem]) == 2:
                parts = pending.pop(stem)
                node_id, caption = wanted[stem]
                try:
                    data = widget_picture(parts[".jpg"], json.loads(parts[".json"]), node_id)
                except Exception:  # noqa: BLE001 - a screen that cannot be read is left out
                    data = None
                path = data and save(f"widget-{stem}", data, folder)
                if path:
                    rows.append({"picture": path, "question": "What does the control outlined in red do?",
                                 "answer": f"It is for: {caption}.", "split": ""})
        return len(rows) >= want

    stream_tar(RICO_URL, take, "the Rico phone screens (6.4 GB at most)")
    return rows


# ----------------------------------------------------------------- research: receipts, charts, price tags, signs

SROIE_RAW = "https://raw.githubusercontent.com/zzzDavid/ICDAR-2019-SROIE/master/data/"
RECEIPT_QUESTION = "Read the shop's name, the date, the address and the total from this receipt."


def prepare_sroie(source, data_dir, work, cap):
    """SROIE (ICDAR 2019 competition on scanned receipts; the 626 training receipts with their key fields, from the
    zzzDavid/ICDAR-2019-SROIE copy on GitHub, as the competition's own site needs an account; no licence stated):
    Malaysian shop receipts with the shop's name, date, address and total. The last 26 are the test pictures."""
    items = []
    for n in range(626):
        try:
            key = json.loads(get_bytes(f"{SROIE_RAW}key/{n:03d}.json"))
        except Exception:  # noqa: BLE001 - a receipt without its fields is left out
            continue
        if not all(clean(key.get(k)) for k in ("company", "date", "total")):
            continue
        answer = f"This receipt is from {clean(key['company'])}, dated {clean(key['date'])}."
        if clean(key.get("address")):
            answer += f" The address is {clean(key['address']).rstrip('.')}."
        answer += f" The total is {clean(key['total'])}."
        items.append((f"sroie-{n:03d}.jpg", f"{SROIE_RAW}img/{n:03d}.jpg",
                      {"question": RECEIPT_QUESTION, "answer": answer, "split": "test" if n >= 600 else ""}))
        if len(items) >= cap + source.test:
            break
    say(f"  Fetching {len(items)} SROIE receipts.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


WILDRECEIPT_URL = "https://download.openmmlab.com/mmocr/data/wildreceipt.tar"
# WildReceipt's label numbers for the values it marks.
WILD_FIELDS = {1: "store", 3: "address", 7: "date", 9: "time", 11: "item", 13: "quantity", 15: "price", 23: "total"}


def wildreceipt_answer(entry):
    """The answer for one WildReceipt receipt (its marked values in reading order), or ""."""
    found = {}
    for a in sorted(entry.get("annotations") or [], key=lambda a: (a["box"][1], a["box"][0])):
        field = WILD_FIELDS.get(a.get("label"))
        if field and clean(a.get("text")):
            found.setdefault(field, []).append(clean(a["text"]))
    if not found.get("store") or not found.get("total"):
        return ""
    text = f"This receipt is from {' '.join(found['store'])}."
    when = " ".join(found.get("date", [])[:1] + found.get("time", [])[:1])
    if when:
        text += f" It is dated {when}."
    items = found.get("item", [])
    if items:
        text += f" It lists {listed(items[:8])}" + (" and more" if len(items) > 8 else "") + "."
    return text + f" The total is {found['total'][-1]}."


def prepare_wildreceipt(source, data_dir, work, cap):
    """WildReceipt (Sun et al., 2021, OpenMMLab; no licence stated): 1,768 photos of receipts from many shops, with
    the store, date, time, items, prices and total marked. The 185 MB archive is downloaded once (kept; it resumes).
    "Read the shop's name, the date, the items and the total from this receipt." """
    import tarfile
    archive = download_to(work, WILDRECEIPT_URL)
    rows = []
    folder = os.path.join(data_dir, source.key)
    with tarfile.open(archive) as tar:
        answers = {}
        for part, split in (("wildreceipt/train.txt", ""), ("wildreceipt/test.txt", "test")):
            for line in tar.extractfile(part).read().decode("utf-8").splitlines():
                if line.strip():
                    entry = json.loads(line)
                    answer = wildreceipt_answer(entry)
                    if answer:
                        answers["wildreceipt/" + entry["file_name"]] = (answer, split)
        names = sorted(answers)
        random.Random(241).shuffle(names)
        for name in names[:cap + source.test * 2]:
            answer, split = answers[name]
            path = save("wildreceipt-" + re.sub(r"\W", "_", name)[-80:], tar.extractfile(name).read(), folder)
            if path:
                rows.append({"picture": path, "answer": answer, "split": split,
                             "question": "Read the shop's name, the date, the items and the total from this receipt."})
    return rows


DVQA_QA = gdrive("1VKYd3kaiCFziSsSv4SgQJ2T5m7jxuh5u")
DVQA_IMAGES = gdrive("1iKH2lTi1-QxtNUVRxTUWFvUvRHq6HAsZ")


def json_array_items(f, block=1 << 20):
    """The items of a big JSON list read from a file one by one, without loading the whole file."""
    decoder, buffer, started = json.JSONDecoder(), "", False
    while True:
        chunk = f.read(block)
        buffer += chunk.decode("utf-8", "ignore") if chunk else ""
        while True:
            buffer = buffer.lstrip(" \r\n\t,")
            if not started:
                if not buffer.startswith("["):
                    break
                buffer, started = buffer[1:], True
                continue
            if buffer.startswith("]"):
                return
            try:
                item, end = decoder.raw_decode(buffer)
            except ValueError:
                break
            yield item
            buffer = buffer[end:]
        if not chunk:
            return


def prepare_dvqa(source, data_dir, work, cap):
    """DVQA (Kafle, Price, Cohen and Kanan, 2018; no licence stated; the makers' Google Drive): bar charts drawn by a
    program, with questions about them ("What is the value of the largest bar?"). Questions are read from the 500 MB
    train file in the 73 MB question archive, keeping those about one chart in six (at most 2 each); then the 5.6 GB
    picture archive is read from the web only until enough of those charts are taken."""
    import requests
    import tarfile
    questions = {}
    with requests.get(DVQA_QA, stream=True, timeout=120, headers={"User-Agent": USER_AGENT}) as r:
        r.raise_for_status()
        with tarfile.open(fileobj=r.raw, mode="r|gz") as tar:
            for member in tar:
                if member.name.endswith("train_qa.json"):
                    for q in json_array_items(tar.extractfile(member)):
                        number = int(re.sub(r"\D", "", q["image"]) or 0)
                        if number % 6 == 0 and len(questions.get(q["image"], [])) < 2 \
                                and q.get("question_type") in ("data", "reasoning"):
                            questions.setdefault(q["image"], []).append(
                                (as_question(q["question"]), sentence(str(q["answer"]))))
                    break
    say(f"  DVQA: questions kept for {len(questions)} charts.")
    want, rows = cap + source.test, []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep a chart that has questions; True when there are enough rows."""
        name = os.path.basename(member.name)
        if name in questions:
            path = save(f"dvqa-{name[:-4]}", tar.extractfile(member).read(), folder)
            for question, answer in questions[name] if path else []:
                rows.append({"picture": path, "question": question, "answer": answer, "split": ""})
        return len(rows) >= want

    stream_tar(DVQA_IMAGES, take, "the DVQA charts (5.6 GB at most)")
    return rows


PRICE_TAGS = "https://huggingface.co/datasets/fangsonglong/gothenburg-price-tag/resolve/main/"
PRICE_UNITS = {"kg": "per kilo", "st": "each", "l": "per litre", "lit": "per litre", "liter": "per litre",
               "förp": "per pack", "frp": "per pack", "m": "per metre", "tv": "per wash", "dos": "per dose"}


def prepare_gothenburg_price_tags(source, data_dir, work, cap):
    """Gothenburg price tags (fangsonglong/gothenburg-price-tag on Hugging Face; "Unlicense" stated by the uploader,
    who does not say who took the photos or where): about 300 photos of Swedish supermarket shelf labels, with the
    product name and its comparison price. "What does this price tag say?" """
    items = []
    for split in ("train", "validation", "test"):
        try:
            text = get_bytes(f"{PRICE_TAGS}{split}/metadata.csv").decode("utf-8-sig")
        except Exception:  # noqa: BLE001 - a part without a list is left out
            continue
        for r in csv.DictReader(io.StringIO(text)):
            name, price, unit = clean(r.get("name")), clean(r.get("avg_price")), clean(r.get("unit")).lower()
            if not name or not re.fullmatch(r"\d+(\.\d+)?", price):
                continue
            per = PRICE_UNITS.get(unit, f"per {unit}" if unit else "")
            answer = f"The price tag is for {name}. The comparison price is {price.replace('.', ',')} kronor {per}."
            items.append((f"{split}-{r['file_name'].rsplit('.', 1)[0]}.jpg", f"{PRICE_TAGS}{split}/{r['file_name']}",
                          {"question": "What does this price tag say?", "answer": answer.replace(" .", "."),
                           "split": "test" if split == "test" else ""}))
    say(f"  Fetching {len(items)} price tag photos.")
    return fetch_pictures(items[:cap + source.test * 3], os.path.join(data_dir, source.key), workers=4)


STREET_SIGNS = "AlessandroFerrante/StreetSignSet"
SIGNS = {
    "prio_give_way": "a give-way (yield) sign", "prio_stop": "a stop sign", "prio_priority_road": "a priority road sign",
    "forb_no_entry": "a no-entry sign", "forb_no_parking": "a no-parking sign", "forb_no_stopping": "a no-stopping sign",
    "forb_overtake_car": "a no-overtaking sign", "forb_overtake_trucks": "a no-overtaking-for-lorries sign",
    "forb_trucks": "a no-lorries sign", "forb_turn_left": "a no-left-turn sign", "forb_turn_right": "a no-right-turn sign",
    "forb_weight_over_3.5t": "a sign banning vehicles over 3.5 tonnes",
    "forb_weight_over_7.5t": "a sign banning vehicles over 7.5 tonnes", "forb_u_turn": "a no-U-turn sign",
    "info_bus_station": "a bus stop sign", "info_crosswalk": "a pedestrian crossing sign",
    "info_highway": "a motorway sign", "info_one_way": "a one-way street sign", "info_parking": "a parking sign",
    "info_taxi_parking": "a taxi rank sign", "warn_children": "a warning sign for children",
    "warn_construction": "a roadworks warning sign", "warn_crosswalk": "a warning sign for a pedestrian crossing",
    "warn_cyclists": "a warning sign for cyclists", "warn_left_curve": "a warning sign for a bend to the left",
    "warn_right_curve": "a warning sign for a bend to the right",
    "warn_domestic_animals": "a warning sign for farm animals", "warn_other_dangers": "a general danger warning sign",
    "warn_poor_road_surface": "a warning sign for an uneven road", "warn_roundabout": "a warning sign for a roundabout",
    "warn_sharp_left_curve": "a warning sign for a sharp bend to the left",
    "warn_sharp_right_curve": "a warning sign for a sharp bend to the right",
    "warn_slippery_road": "a slippery road warning sign", "warn_hump": "a warning sign for a speed bump",
    "warn_traffic_light": "a warning sign for traffic lights", "warn_tram": "a warning sign for trams",
    "warn_two_way_traffic": "a warning sign for two-way traffic", "warn_wild_animals": "a warning sign for wild animals",
    "mand_bike_lane": "a cycle lane sign", "mand_go_left": "a sign saying turn left",
    "mand_go_left_right": "a sign saying turn left or right", "mand_go_right": "a sign saying turn right",
    "mand_go_straight": "a sign saying go straight ahead", "mand_go_straight_left": "a sign saying go straight or left",
    "mand_go_straight_right": "a sign saying go straight or right", "mand_pass_left": "a sign saying keep left",
    "mand_pass_left_right": "a sign saying pass on either side", "mand_pass_right": "a sign saying keep right",
    "mand_roundabout": "a roundabout sign",
}


def sign_words(label):
    """A Street Sign Set label in words ("forb_speed_over_50" -> "a 50 km/h speed limit sign"), or ""."""
    speed = re.fullmatch(r"forb_speed_over_(\d+)", label)
    return f"a {speed.group(1)} km/h speed limit sign" if speed else SIGNS.get(label, "")


def prepare_streetsignset(source, data_dir, work, cap):
    """Street Sign Set (Ferrante, 2025; "CC BY 4.0" stated, but some photos come from other Kaggle sets and from
    street-mapping services whose own terms do not allow that, so it is kept for personal use): road signs of Italy
    and Europe, the signs in each photo named in its file name. "What road signs can you see?" """
    groups = {}
    for split in ("train", "valid", "test"):
        files = get_json(f"https://huggingface.co/api/datasets/{STREET_SIGNS}/tree/main/{split}/images",
                         {"recursive": "1"})
        for f in files:
            name = os.path.basename(f["path"])
            if not name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            labels = [re.sub(r"-[\d-]+$", "", part) for part in os.path.splitext(name)[0].split("~")]
            words = [sign_words(label) for label in labels]
            if all(words):
                groups.setdefault(labels[0], []).append((f["path"], tuple(dict.fromkeys(words)), split))
    items = []
    for path, words, split in even_pick(groups, int((cap + source.test) * 1.05), 251):
        answer = f"I can see {listed(list(words))}."
        items.append((re.sub(r"[^\w.-]", "_", path)[-110:].rsplit(".", 1)[0] + ".jpg",
                      f"https://huggingface.co/datasets/{STREET_SIGNS}/resolve/main/{urllib.parse.quote(path)}",
                      {"question": "What road signs can you see?", "answer": answer,
                       "split": "test" if split == "test" else ""}))
    say(f"  Fetching {len(items)} road sign photos from {len(groups)} kinds.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- research: expressions from a TV series and dance

IFEED_URL, IFEED_SIZE = zenodo("7971730", "IFEED_Base.zip"), 166651224
IFEED_SIGNS = {
    "happy": "The corners of the mouth are drawn up and the cheeks raised. The person seems to be happy.",
    "sad": "The corners of the mouth turn down and the inner eyebrows are drawn up. The person looks sad.",
    "angry": "The eyebrows are drawn down and together and the mouth is tense. The person looks angry.",
    "neutral": "The face is at rest. The person looks neutral, showing no particular expression.",
    "fear": "The eyebrows are raised and drawn together and the eyes are wide. The person looks afraid.",
    "disgust": "The nose is wrinkled and the upper lip raised. The person looks disgusted.",
    "surprise": "The eyebrows are raised high and the eyes and mouth are wide open. The person looks surprised.",
}


def prepare_ifeed(source, data_dir, work, cap):
    """IFEED (Zenodo 7971730, base set; "CC BY 4.0" stated, but its pictures are frames of the TV series Friends,
    which belongs to Warner Bros., so research or personal use only): small face crops (112 pixels) of the series'
    actors, labelled with seven expressions. One frame per spoken line, an equal share for each expression; its
    Testing folder gives the test pictures."""
    z = remote_zip(IFEED_URL, IFEED_SIZE)
    groups, seen = {}, set()
    for n in z.namelist():
        m = re.search(r"/(Training|Testing|Crossing)/(dia\d+_utt\d+)/frame\d+_[^_/]+_(\w+)\.jpg$", n)
        if m and m.group(3) in IFEED_SIGNS and (m.group(1), m.group(2)) not in seen:
            seen.add((m.group(1), m.group(2)))
            groups.setdefault(m.group(3), []).append((n, m.group(1)))
    z.close()
    chosen = [(n, {"question": EXPRESSION_QUESTION, "split": "test" if part == "Testing" else "",
                   "answer": f"A small close-up of a face from a TV show. {IFEED_SIGNS[n.rsplit('_', 1)[1][:-4]]}"})
              for n, part in even_pick(groups, cap + source.test, 257)]
    say(f"  IFEED: reading {len(chosen)} faces.")
    return zip_members(source, data_dir, work, lambda: remote_zip(IFEED_URL, IFEED_SIZE), chosen)


NAVARASA_URL, NAVARASA_SIZE = zenodo("12094235", "NAVARASA.zip"), 169985458
RASAS = {"Shringaara": "shringara, love and devotion", "Hasya": "hasya, joy and laughter",
         "Karuna": "karuna, sorrow and compassion", "Roudra": "raudra, anger", "Veera": "veera, courage and pride",
         "Bhayaanaka": "bhayanaka, fear", "Bheebhatsya": "bibhatsa, disgust", "Adbhutha": "adbhuta, wonder",
         "Shaanta": "shanta, peace and calm"}


def prepare_navarasa(source, data_dir, work, cap):
    """Navarasa (Zenodo 12094235; "CC BY 4.0" stated, but the frames come from performance videos of about 30 dancers
    with no word of their consent or of who filmed them, so research or personal use only): faces of Indian classical
    dancers showing the nine rasas (expressions). Only its original frames, not its augmented copies; an equal share
    for each rasa. "Which of the nine dance expressions (navarasas) is this?" """
    z = remote_zip(NAVARASA_URL, NAVARASA_SIZE)
    groups = {}
    for n in z.namelist():
        parts = n.split("/")
        if len(parts) == 4 and parts[1] == "DATASET_NAVARASA" and parts[2] in RASAS and n.endswith(".jpg"):
            groups.setdefault(parts[2], []).append(n)
    z.close()
    chosen = [(n, {"question": "Which of the nine dance expressions (navarasas) is this dancer showing?",
                   "answer": f"A dancer's face showing {RASAS[n.split('/')[2]]}, one of the nine expressions of "
                             "Indian classical dance. The expression is performed for the dance.", "split": ""})
              for n in even_pick(groups, cap + source.test, 263)]
    say(f"  Navarasa: reading {len(chosen)} dancers' faces.")
    return zip_members(source, data_dir, work, lambda: remote_zip(NAVARASA_URL, NAVARASA_SIZE), chosen)


# ----------------------------------------------------------------- research: everyday photos

OBJECTS365 = "https://dorc.ks3-cn-beijing.ksyun.com/data-set/2020Objects365%E6%95%B0%E6%8D%AE%E9%9B%86/val/"


def object_name(name):
    """An Objects365 category in plain words ("Cabinet/shelf" -> "cabinet", "Street Lights" -> "street light")."""
    name = name.split("/")[0].strip().lower()
    if name in ("glasses", "sneakers", "other shoes", "slippers", "high heels", "boots", "gloves", "scissors",
                "pliers", "tongs", "chopsticks", "shorts", "jeans", "trousers", "pants"):
        return name.replace("other ", "")
    return re.sub(r"(?<!s)s$", "", name) if not name.endswith(("ss", "us", "is")) else name


def prepare_objects365(source, data_dir, work, cap):
    """Objects365 (Shao et al., 2019, Megvii; research use; photos from Flickr and Places365, whose owners keep their
    rights): everyday photos with every object boxed and named (365 kinds). Its validation list (270 MB) and its
    first picture archive (133 MB, about 1,700 photos) are downloaded once and kept. "What objects can you see in this
    picture?" with the objects counted (people included, so "child" cannot be marked; never used for
    picture-making)."""
    import tarfile
    notes = download_to(work, OBJECTS365 + "zhiyuan_objv2_val.json", "objects365_val.json")
    archive = download_to(work, OBJECTS365 + "images/v1/patch0.tar.gz", "objects365_val_patch0.tar.gz")
    with open(notes, encoding="utf-8") as f:
        data = json.load(f)
    names = {c["id"]: object_name(c["name"]) for c in data["categories"]}
    wanted = {i["id"]: os.path.basename(i["file_name"]) for i in data["images"] if "/v1/patch0/" in i["file_name"]}
    counts = {}
    for a in data["annotations"]:
        if a["image_id"] in wanted and not a.get("iscrowd"):
            counts.setdefault(wanted[a["image_id"]], collections.Counter())[names[a["category_id"]]] += 1
    del data
    rows = []
    folder = os.path.join(data_dir, source.key)
    with tarfile.open(archive) as tar:
        for m in tar:
            name = os.path.basename(m.name)
            if name in counts and len(rows) < cap + source.test:
                path = save(f"o365-{name[:-4]}", tar.extractfile(m).read(), folder)
                if path:
                    rows.append({"picture": path, "question": "What objects can you see in this picture?",
                                 "answer": f"I can see {counted(counts[name])}.", "split": ""})
    return rows


VG_URL = "https://homes.cs.washington.edu/~ranjay/visualgenome/data/dataset/"


def prepare_vg_photos(source, data_dir, work, cap):
    """Visual Genome (Krishna et al., 2017): questions and answers people wrote (CC BY 4.0) about its own photos that
    are NOT in COCO (the open kit uses the COCO ones). These photos come from Flickr and YFCC with no licence or terms
    of their own written down, so they are for personal use. Fetched one by one from Visual Genome's server; at most
    3 questions per photo. "child" marks rows whose words name a child."""
    from more_sources import pick_by_photo
    say("  Downloading Visual Genome's list of photos and its questions (27 MB; shared with visual_genome_qa).")
    photos = {}
    for image in json_in_zip(download_to(work, VG_URL + "image_data.json.zip", "vg_image_data.json.zip")):
        if not image.get("coco_id") and image.get("url"):
            photos[image["image_id"]] = image["url"].replace("http://", "https://")
    per_photo = {}
    for entry in json_in_zip(download_to(work, VG_URL + "question_answers.json.zip", "vg_question_answers.json.zip")):
        url = photos.get(entry.get("id"))
        if not url:
            continue
        for qa in entry.get("qas") or []:
            question, answer = as_question(qa.get("question")), sentence(qa.get("answer"))
            if question and answer:
                per_photo.setdefault(entry["id"], []).append(
                    (f"vg-{entry['id']}.jpg", url, {"question": question, "answer": answer, "split": "",
                                                     "child": bool(CHILD_WORDS.search(question + " " + answer))}))
    items = pick_by_photo(per_photo, int((cap + source.test) * 1.05), 269, 3)
    say(f"  Fetching the Visual Genome photos for {len(items)} questions.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=6)


UECFOODPIX_URL = "https://mm.cs.uec.ac.jp/uecfoodpix/UECFOODPIXCOMPLETE.tar"


def mask_dishes(png, names):
    """The dishes a UEC FoodPix mask marks (its red channel holds each pixel's dish number), the biggest first, each
    covering at least 2 percent of the picture."""
    from PIL import Image
    img = Image.open(io.BytesIO(png)).convert("RGB")
    counts = collections.Counter(img.getchannel("R").getdata())
    total = img.width * img.height
    return [names[v] for v, n in counts.most_common() if v in names and n >= 0.02 * total]


def prepare_uecfoodpix(source, data_dir, work, cap):
    """UEC FoodPix Complete (Okamoto and Yanai, 2021, University of Electro-Communications, Tokyo; non-commercial
    research only), from the UEC Food-100 photos (the UEC Food-256 download is gone): 10,000 photos of Japanese and
    other meals, every dish outlined by hand and named (102 dishes). Its 795 MB archive is read from the web until
    enough are taken. "What food is this?" """
    names, pending, rows = {}, {}, []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Read the dish names, then pair each photo with its mask; True when there are enough."""
        if member.name.endswith("category.txt"):
            for line in tar.extractfile(member).read().decode("utf-8").splitlines()[1:]:
                number, _, name = line.strip().partition("\t") if "\t" in line else line.strip().partition(" ")
                if number.isdigit() and name.strip() and name.strip() != "other":
                    names[int(number)] = name.strip().replace("hambarg", "hamburger").replace("omelete", "omelette")
            return False
        m = re.search(r"/(train|test)/(img|mask)/(\d+)\.(jpg|png)$", member.name)
        if not m:
            return False
        key = (m.group(1), m.group(3))
        pending.setdefault(key, {})[m.group(2)] = tar.extractfile(member).read()
        if len(pending[key]) == 2 and names:
            parts = pending.pop(key)
            dishes = mask_dishes(parts["mask"], names)
            if dishes:
                path = save(f"uecfoodpix-{key[0]}-{key[1]}", parts["img"], folder)
                if path:
                    text = f"This looks like {dishes[0]}." if len(dishes) == 1 else \
                        f"This looks like a meal of {listed(dishes[:6])}."
                    rows.append({"picture": path, "question": "What food is this?", "answer": text,
                                 "split": "test" if key[0] == "test" else ""})
        return len([r for r in rows if not r["split"]]) >= cap and len(rows) >= cap + source.test

    stream_tar(UECFOODPIX_URL, take, "UEC FoodPix Complete (795 MB at most)")
    return rows


INDOOR = "https://huggingface.co/datasets/Voxel51/IndoorSceneRecognition/resolve/main/"
INDOOR_LEFT_OUT = {"locker_room", "poolinside"}           # changing rooms and swimming pools: people undressed
INDOOR_WORDS = {"airport_inside": "the inside of an airport", "inside_bus": "the inside of a bus",
                "inside_subway": "the inside of an underground train", "kindergarden": "a nursery school classroom",
                "children_room": "a child's bedroom", "artstudio": "an art studio", "computerroom": "a computer room",
                "livingroom": "a living room", "dentaloffice": "a dentist's surgery", "prisoncell": "a prison cell",
                "gameroom": "a games room", "winecellar": "a wine cellar", "videostore": "a video shop",
                "tv_studio": "a television studio", "toystore": "a toy shop", "trainstation": "a railway station",
                "waitingroom": "a waiting room", "bookstore": "a bookshop", "clothingstore": "a clothes shop",
                "shoeshop": "a shoe shop", "jewelleryshop": "a jewellery shop", "fastfood_restaurant":
                "a fast-food restaurant", "hairsalon": "a hairdresser's", "mall": "a shopping centre",
                "elevator": "a lift", "grocerystore": "a grocery shop", "restaurant_kitchen": "a restaurant kitchen",
                "studiomusic": "a music studio", "concert_hall": "a concert hall", "movietheater": "a cinema",
                "operating_room": "an operating theatre", "hospitalroom": "a hospital room",
                "classroom": "a classroom", "laboratorywet": "a laboratory", "greenhouse": "a greenhouse",
                "cloister": "a cloister", "church_inside": "the inside of a church"}


def indoor_words(label):
    """An MIT Indoor 67 label in words ("bakery" -> "a bakery", "inside_bus" -> "the inside of a bus")."""
    if label in INDOOR_WORDS:
        return INDOOR_WORDS[label]
    words = label.replace("_", " ")
    return f"{a_or_an(words)} {words}"


def prepare_indoor_scenes(source, data_dir, work, cap):
    """MIT Indoor 67 (Quattoni and Torralba, 2009; "for research purposes only"): 15,620 photos of 67 kinds of indoor
    places. Its own download (groups.csail.mit.edu) is gone, so the photos are fetched one by one from the Voxel51
    copy on Hugging Face, which keeps the original labels and train/test lists. Changing rooms and indoor swimming
    pools are left out. "What kind of place is this?" """
    data = json.loads(get_bytes(INDOOR + "samples.json"))
    groups = {}
    for s in data["samples"]:
        label = ((s.get("ground_truth") or {}).get("label") or "").strip()
        if label and label not in INDOOR_LEFT_OUT:
            groups.setdefault(label, []).append((s["filepath"], "test" if "test" in (s.get("tags") or []) else ""))
    items = []
    for path, split in even_pick(groups, int((cap + source.test) * 1.05), 271):
        label = next(k for k, v in groups.items() if (path, split) in v)
        items.append((re.sub(r"[^\w.-]", "_", path)[-110:].rsplit(".", 1)[0] + ".jpg",
                      INDOOR + urllib.parse.quote(path),
                      {"question": "What kind of place is this?", "answer": f"This looks like {indoor_words(label)}.",
                       "split": split}))
    say(f"  Fetching {len(items)} indoor photos of {len(groups)} kinds.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


SOP_URL, SOP_SIZE = "http://ftp.cs.stanford.edu/cs/cvgl/Stanford_Online_Products.zip", 3083860082
SOP_THINGS = {"bicycle": "a bicycle", "cabinet": "a cabinet", "chair": "a chair", "coffee_maker": "a coffee maker",
              "fan": "an electric fan", "kettle": "a kettle", "lamp": "a lamp", "mug": "a mug", "sofa": "a sofa",
              "stapler": "a stapler", "table": "a table", "toaster": "a toaster"}


def prepare_stanford_products(source, data_dir, work, cap):
    """Stanford Online Products (Song, Xiang, Jegelka and Savarese, 2016; no licence or terms stated; photos from
    eBay listings): 120,000 photos of 22,600 things for sale in 12 kinds (bicycles, kettles, lamps, staplers ...).
    One photo per thing, an equal share for each kind, read out of the 3 GB zip by HTTP ranges. "What is this?" """
    z = remote_zip(SOP_URL, SOP_SIZE)
    groups, seen = {}, set()
    for line in z.read("Stanford_Online_Products/Ebay_info.txt").decode().splitlines()[1:]:
        parts = line.split()
        if len(parts) == 4 and parts[1] not in seen:
            seen.add(parts[1])
            kind = parts[3].split("/")[0].replace("_final", "")
            if kind in SOP_THINGS:
                groups.setdefault(kind, []).append(parts[3])
    z.close()
    chosen = [(f"Stanford_Online_Products/{p}", {"question": "What is this?", "split": "",
                                                 "answer": f"This is {SOP_THINGS[p.split('/')[0][:-6]]}, "
                                                           "photographed for an online shop listing."})
              for p in even_pick(groups, cap + source.test, 277)]
    say(f"  Stanford Online Products: reading {len(chosen)} photos.")
    return zip_members(source, data_dir, work, lambda: remote_zip(SOP_URL, SOP_SIZE), chosen, workers=4)


# ----------------------------------------------------------------- what could not be included

NOT_INCLUDED = {
    "Kvasir v2 (datasets.simula.no)": "tried again in November 2026: the server still sends an incomplete certificate "
                                      "chain, so a secure download fails, and plain HTTP redirects to the same secure "
                                      "address. The open gi_endoscopy pack (HyperKvasir, CC BY 4.0) covers the same "
                                      "kind of pictures.",
    "ExpW (Expression in-the-Wild)": "downloadable from the authors' Google Drive, but only as a split 7-Zip archive "
                                     "(origin.7z.001 ...), which the kit cannot read without an extra 7-Zip program.",
    "UEC Food-256": "its download (foodcam.mobi) is gone; UEC FoodPix Complete from the same lab is used instead "
                    "(uecfoodpix).",
    "Stanford Cars": "its download server (ai.stanford.edu) answers 503; there is no official copy.",
    "SVHN house numbers": "the full-size photos' labels are MATLAB 7.3 (HDF5) files that need h5py, which the kit does "
                          "not install; the ready-cut digits are only 32 pixels.",
    "Oxford 102 Flowers": "its label file gives numbers, not flower names, and its makers publish no list of names.",
    "Hand Gestures Dataset (figshare 24449197)": "a hand skeleton drawn by tracking software is over every picture.",
    "Re-uploads of other sets (CK+48, VIRI, NVIE, FER2013 copies, EMOTIF)": "copies whose licence the original makers "
                                                                           "never gave; the originals are on the "
                                                                           "sign-up list.",
    "WLASL, MS-ASL": "only lists of YouTube links; the videos must be scraped from YouTube.",
    "SemArt, WikiArt": "SemArt's terms cannot be checked; WikiArt has no official download and most of its works are "
                       "in copyright.",
}


# ----------------------------------------------------------------- the table

def research(summary):
    """A research-terms summary that also says it is for personal, non-commercial use."""
    return summary + " Personal, non-commercial use only."


EXTRA_SOURCES = [
    # ---- share-alike
    Source("oxford_pets", "Oxford-IIIT Pet: 37 cat and dog breeds (share-alike)",
           "CC BY-SA 4.0 (robots.ox.ac.uk/~vgg/data/pets)",
           "Oxford-IIIT Pet Dataset (Parkhi, Vedaldi, Zisserman and Jawahar, 2012), CC BY-SA 4.0, "
           "https://www.robots.ox.ac.uk/~vgg/data/pets/", "share-alike", 2000, 20, prepare_oxford_pets,
           "up to 790 MB, read once"),
    Source("hagrid", "HaGRIDv2: hand gestures made by adults (share-alike)",
           "A variant of CC BY-SA 4.0 (github.com/hukenovs/hagrid, license/en_us.pdf)",
           "HaGRIDv2 (Kapitanov, Kvanchiani, Nagaev, Kraynov, Makhliarchuk and Nuzhdin, 2024), CC BY-SA 4.0 variant, "
           "https://github.com/hukenovs/hagrid", "share-alike", 1500, 20, prepare_hagrid, "about 2.5 GB of photos"),
    Source("plantvillage", "PlantVillage: crop leaves, healthy or with a named disease (share-alike)",
           "CC BY-SA 3.0 (huggingface.co/datasets/mohanty/PlantVillage)",
           "PlantVillage (Hughes and Salathe, 2015), CC BY-SA 3.0, https://github.com/spMohanty/PlantVillage-Dataset",
           "share-alike", 2000, 20, prepare_plantvillage, "about 300 MB of photos"),
    Source("plantnet_sa", "Pl@ntNet-300K: 1,000 plant species, photos under CC BY-SA (share-alike)",
           "Each photo CC BY-SA (plantnet300K_metadata.csv, Zenodo 10419064)",
           "Pl@ntNet-300K v2 (Garcin et al., 2021), photos by Pl@ntNet users under CC BY-SA, "
           "https://zenodo.org/records/10419064", "share-alike", 3000, 20, prepare_plantnet_sa,
           "about 600 MB of photos"),
    Source("hiertext", "HierText: the text in everyday photos, read out (share-alike)",
           "CC BY-SA 4.0 (github.com/google-research-datasets/hiertext); Open Images photos, CC BY 2.0",
           "HierText (Long et al., 2022, Google), CC BY-SA 4.0; photos from Open Images, CC BY 2.0", "share-alike",
           1500, 20, prepare_hiertext, "up to 577 MB, read once"),
    Source("mapqa", "MapQA: questions about real US maps (share-alike)",
           "CC BY-SA 4.0 (github.com/OSU-slatelab/MapQA)",
           "MapQA (Chang, Palzer, Li, Fosler-Lussier and Xiao, 2022), CC BY-SA 4.0, "
           "https://github.com/OSU-slatelab/MapQA", "share-alike", 2000, 20, prepare_mapqa, "about 300 MB"),
    Source("hypersim", "Hypersim: computer-made pictures of rooms, with the kind of room (share-alike)",
           "CC BY-SA 3.0 (github.com/apple/ml-hypersim)",
           "Hypersim (Roberts et al., 2021, Apple), CC BY-SA 3.0, https://github.com/apple/ml-hypersim",
           "share-alike", 800, 20, prepare_hypersim, "about 100 MB of pictures"),
    Source("openfoodfacts", "Open Food Facts: food products, their name, brand and size (share-alike)",
           "Photos CC BY-SA 3.0, database ODbL 1.0 (world.openfoodfacts.org/terms-of-use)",
           "Open Food Facts contributors, photos CC BY-SA 3.0, data ODbL 1.0, https://world.openfoodfacts.org",
           "share-alike", 1500, 20, prepare_openfoodfacts, "about 600 MB of photos"),
    Source("openfoodfacts_labels", "Open Food Facts: ingredient lists and nutrition tables, read out (share-alike)",
           "Photos CC BY-SA 3.0, database ODbL 1.0 (world.openfoodfacts.org/terms-of-use)",
           "Open Food Facts contributors, photos CC BY-SA 3.0, data ODbL 1.0, https://world.openfoodfacts.org",
           "share-alike", 2000, 20, prepare_openfoodfacts_labels, "about 800 MB of photos"),
    Source("commons_breeds_sa", "Wikimedia Commons: animal breeds, photos under CC BY-SA or GFDL (share-alike)",
           "Each photo CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 20, prepare_commons_breeds_sa, "about 150 MB"),
    Source("commons_food_sa", "Wikimedia Commons: food photos under CC BY-SA or GFDL (share-alike)",
           "Each photo CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 20, prepare_commons_food_sa, "about 150 MB"),
    Source("commons_medical_sa", "Wikimedia Commons: medical photos of adults under CC BY-SA or GFDL (share-alike)",
           "Each photo CC BY-SA or GFDL (its Commons page)",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 600, 10, prepare_commons_medical_sa, "about 60 MB", content="medical"),
    Source("papila", "PAPILA: eye-fundus photos of adults, healthy or with glaucoma (copyleft)",
           "GPL-3.0 or later (figshare 14798004)",
           "PAPILA (Kovalyk, Morales-Sanchez, Verdu-Monedero et al., 2022), GPL-3.0+, "
           "https://doi.org/10.6084/m9.figshare.14798004", "share-alike", 488, 10, prepare_papila,
           "about 600 MB, read in pieces", content="medical"),
    # ---- noncommercial
    Source("plantnet_nc", "Pl@ntNet-300K: plant photos under CC BY-NC (personal use)",
           "Each photo CC BY-NC or CC BY-NC-SA (plantnet300K_metadata.csv, Zenodo 10419064)",
           "Pl@ntNet-300K v2 (Garcin et al., 2021), photos by Pl@ntNet users under CC BY-NC or BY-NC-SA, "
           "https://zenodo.org/records/10419064", "noncommercial", 473, 10, prepare_plantnet_nc, "about 100 MB",
           terms="https://zenodo.org/records/10419064",
           terms_summary="Each photo's own licence, here CC BY-NC or CC BY-NC-SA: use with credit, not for commercial "
                         "purposes."),
    Source("ravdess", "RAVDESS: posed facial expressions of adult actors, stills (personal use)",
           "CC BY-NC-SA 4.0 (Zenodo 1188976)",
           "RAVDESS (Livingstone and Russo, 2018), CC BY-NC-SA 4.0, https://doi.org/10.5281/zenodo.1188976",
           "noncommercial", 1000, 20, prepare_ravdess, "about 4 GB of videos (kept), needs the video extras",
           terms="https://zenodo.org/records/1188976",
           terms_summary="CC BY-NC-SA 4.0: use with credit, not for commercial purposes, and anything made from it "
                         "keeps the same licence."),
    Source("how2sign", "How2Sign: stills of adults signing American Sign Language (personal use)",
           "CC BY-NC 4.0 (how2sign.github.io)",
           "How2Sign (Duarte et al., 2021), CC BY-NC 4.0, https://how2sign.github.io", "noncommercial", 800, 20,
           prepare_how2sign, "about 2 GB of clips (kept), needs the video extras",
           terms="https://how2sign.github.io",
           terms_summary="CC BY-NC 4.0: use with credit, not for commercial purposes; the page also says research "
                         "purposes."),
    # ---- research or no stated terms
    Source("cub200", "CUB-200-2011: 200 bird species (research terms; personal use)",
           "Non-commercial research and educational use only (vision.caltech.edu/datasets/cub_200_2011)",
           "Caltech-UCSD Birds-200-2011 (Wah, Branson, Welinder, Perona and Belongie, 2011), "
           "https://www.vision.caltech.edu/datasets/cub_200_2011/", "research", 2400, 20, prepare_cub200,
           "1.1 GB, once", terms="https://www.vision.caltech.edu/datasets/cub_200_2011/",
           terms_summary=research("The makers do not own the photos; their use is restricted to non-commercial "
                                  "research and educational purposes.")),
    Source("plantdoc", "PlantDoc: crop leaves from the web, healthy or diseased (personal use)",
           "CC BY 4.0 stated for the labels, but the pictures were taken from web searches and their owners are "
           "unknown (arXiv 1911.10317)",
           "PlantDoc (Singh et al., 2020), https://github.com/pratikkayal/PlantDoc-Dataset", "research", 2400, 20,
           prepare_plantdoc, "about 400 MB", terms="https://github.com/pratikkayal/PlantDoc-Dataset",
           terms_summary=research("The labels are CC BY 4.0, but nobody has given rights to the pictures, which "
                                  "were found with web searches.")),
    Source("nocaps", "nocaps: Open Images photos described in one sentence (personal use)",
           "No licence stated for the descriptions (nocaps.org); photos CC BY 2.0 (Open Images)",
           "nocaps (Agrawal et al., 2019), https://nocaps.org; photos from Open Images, CC BY 2.0", "research", 4000,
           20, prepare_nocaps, "about 600 MB", terms="https://nocaps.org/download",
           terms_summary="No licence or terms are stated for the descriptions; personal, non-commercial use only "
                         "(the photos are CC BY 2.0)."),
    Source("vizwiz_quality", "VizWiz photo quality: is a blind person's photo clear, and if not, what is wrong "
                             "(personal use)",
           "No licence or terms stated for the labels (vizwiz.org/tasks-and-datasets/image-quality-issues); photos "
           "CC BY 4.0", "VizWiz Image Quality Issues (Chiu et al., 2020), https://vizwiz.org", "research", 6000, 20,
           prepare_vizwiz_quality, "up to 10 GB of photos",
           terms="https://vizwiz.org/tasks-and-datasets/image-quality-issues/",
           terms_summary="No licence or terms are stated for the labels; personal, non-commercial use only (the "
                         "photos are CC BY 4.0)."),
    Source("rico_screens", "Screen2Words on Rico: phone app screens summed up (personal use)",
           "Summaries CC BY 4.0 (github.com/google-research-datasets/screen2words); Rico screenshots: no licence or "
           "terms stated (interactionmining.org/rico)",
           "Screen2Words (Wang et al., 2021, Google), CC BY 4.0; Rico (Deka et al., 2017), http://interactionmining.org",
           "research", 1500, 20, prepare_rico_screens, "up to 6.4 GB, read once", terms="http://interactionmining.org/rico",
           terms_summary=NO_TERMS),
    Source("rico_widgets", "Widget Captioning on Rico: what a button on a phone screen does (personal use)",
           "Captions CC BY 4.0 (github.com/google-research-datasets/widget-caption); Rico screenshots: no licence or "
           "terms stated", "Widget Captioning (Li et al., 2020, Google), CC BY 4.0; Rico (Deka et al., 2017)",
           "research", 1500, 20, prepare_rico_widgets, "up to 6.4 GB, read once",
           terms="http://interactionmining.org/rico", terms_summary=NO_TERMS),
    Source("sroie", "SROIE: shop receipts, their name, date, address and total (personal use)",
           "No licence stated (rrc.cvc.uab.es/?ch=13; copy at github.com/zzzDavid/ICDAR-2019-SROIE)",
           "SROIE, ICDAR 2019 Robust Reading Challenge on Scanned Receipts (Huang et al., 2019)", "research", 626, 20,
           prepare_sroie, "about 60 MB", terms="https://rrc.cvc.uab.es/?ch=13", terms_summary=NO_TERMS),
    Source("wildreceipt", "WildReceipt: photographed receipts, their shop, items and total (personal use)",
           "No licence stated (OpenMMLab, download.openmmlab.com)",
           "WildReceipt (Sun et al., 2021, OpenMMLab)", "research", 1700, 20, prepare_wildreceipt, "185 MB, once",
           terms="https://mmocr.readthedocs.io/en/dev-1.x/user_guides/data_prepare/datasetzoo.html",
           terms_summary=NO_TERMS),
    Source("dvqa", "DVQA: questions about bar charts (personal use)",
           "No licence stated (github.com/kushalkafle/DVQA_dataset)",
           "DVQA (Kafle, Price, Cohen and Kanan, 2018), https://github.com/kushalkafle/DVQA_dataset", "research", 3000,
           20, prepare_dvqa, "up to 1 GB, read once", terms="https://github.com/kushalkafle/DVQA_dataset",
           terms_summary=NO_TERMS),
    Source("gothenburg_price_tags", "Swedish supermarket price tags, the product and price (personal use)",
           "\"Unlicense\" stated by the uploader; who took the photos is not said "
           "(huggingface.co/datasets/fangsonglong/gothenburg-price-tag)",
           "Gothenburg price tags, https://huggingface.co/datasets/fangsonglong/gothenburg-price-tag", "research", 300,
           15, prepare_gothenburg_price_tags, "about 300 MB",
           terms="https://huggingface.co/datasets/fangsonglong/gothenburg-price-tag",
           terms_summary=research("The uploader states the Unlicense but does not say who took the photos or where, "
                                  "so the rights in them are unclear.")),
    Source("streetsignset", "Street Sign Set: European road signs (personal use)",
           "\"CC BY 4.0\" stated; some photos come from other Kaggle sets and street-mapping services "
           "(huggingface.co/datasets/AlessandroFerrante/StreetSignSet)",
           "Street Sign Set (Ferrante, 2025), https://doi.org/10.34740/KAGGLE/DS/8410752", "research", 2000, 20,
           prepare_streetsignset, "about 300 MB", terms="https://huggingface.co/datasets/AlessandroFerrante/StreetSignSet",
           terms_summary=research("CC BY 4.0 is stated, but some photos come from street-mapping services whose own "
                                  "terms do not allow re-licensing.")),
    Source("ifeed", "IFEED: facial expressions in frames of a TV series (research only; personal use)",
           "\"CC BY 4.0\" stated, but the frames belong to the TV series Friends (Warner Bros.) (Zenodo 7971730)",
           "IFEED: Interactive Facial Expression and Emotion Detection Dataset, https://zenodo.org/records/7971730",
           "research", 1500, 20, prepare_ifeed, "167 MB, read in pieces", terms="https://zenodo.org/records/7971730",
           terms_summary=research("The pictures are frames of a TV show owned by its studio, so only research or "
                                  "personal use can be justified.")),
    Source("navarasa", "Navarasa: the nine expressions of Indian classical dance (personal use)",
           "\"CC BY 4.0\" stated; frames from performance videos with no word of the dancers' consent (Zenodo "
           "12094235)", "Navarasa facial emotions in Indian classical dance, https://zenodo.org/records/12094235",
           "research", 900, 18, prepare_navarasa, "170 MB, read in pieces", terms="https://zenodo.org/records/12094235",
           terms_summary=research("Frames of dancers' performances; the dancers' consent and the filmers' rights "
                                  "are not stated.")),
    Source("objects365", "Objects365: the objects in everyday photos, counted (research; personal use)",
           "Research use; photos from Flickr and Places365 keep their owners' rights (objects365.org)",
           "Objects365 (Shao et al., 2019), https://www.objects365.org", "research", 1500, 20, prepare_objects365,
           "400 MB, once", terms="https://www.objects365.org/overview.html",
           terms_summary=research("For research; the photos belong to their owners on Flickr and Places365.")),
    Source("vg_photos", "Visual Genome: questions about its own (non-COCO) photos (personal use)",
           "Questions CC BY 4.0 (visualgenome.org); photos from Flickr and YFCC with no licence stated",
           "Visual Genome (Krishna et al., 2017), CC BY 4.0, https://visualgenome.org", "research", 6000, 20,
           prepare_vg_photos, "up to 1.5 GB of photos", terms="https://visualgenome.org/about",
           terms_summary="The questions are CC BY 4.0; no licence or terms are stated for the photos; personal, "
                         "non-commercial use only."),
    Source("uecfoodpix", "UEC FoodPix Complete: meals, the dishes on the tray (research only; personal use)",
           "Non-commercial research only (mm.cs.uec.ac.jp/uecfoodpix)",
           "UEC FoodPix Complete (Okamoto and Yanai, 2021), University of Electro-Communications, "
           "https://mm.cs.uec.ac.jp/uecfoodpix/", "research", 2000, 20, prepare_uecfoodpix, "up to 795 MB, read once",
           terms="https://mm.cs.uec.ac.jp/uecfoodpix/#agreement",
           terms_summary=research("UECFoodPix Complete can be used only for non-commercial research.")),
    Source("indoor_scenes", "MIT Indoor 67: kinds of indoor places (research only; personal use)",
           "For research purposes only (web.mit.edu/torralba/www/indoor.html); copy at "
           "huggingface.co/datasets/Voxel51/IndoorSceneRecognition",
           "MIT Indoor 67 (Quattoni and Torralba, 2009), https://web.mit.edu/torralba/www/indoor.html", "research",
           2000, 20, prepare_indoor_scenes, "about 300 MB", terms="https://web.mit.edu/torralba/www/indoor.html",
           terms_summary=research("The images are provided for research purposes only.")),
    Source("stanford_products", "Stanford Online Products: everyday things from shop listings (personal use)",
           "No licence or terms stated (cvgl.stanford.edu/projects/lifted_struct); photos from eBay listings",
           "Stanford Online Products (Song, Xiang, Jegelka and Savarese, 2016)", "research", 1500, 20,
           prepare_stanford_products, "about 60 MB, read in pieces",
           terms="https://cvgl.stanford.edu/projects/lifted_struct/",
           terms_summary="No licence or terms are stated; personal, non-commercial use only (the photos come from "
                         "eBay listings)."),
]

# The collections a picture-making model may learn from: whole-picture answers about non-people things (products,
# plants, pets, birds, food). Never people, children or medical.
EXTRA_PICTURE_MAKING_OK = {"oxford_pets", "plantvillage", "plantnet_sa", "plantnet_nc", "openfoodfacts",
                           "commons_breeds_sa", "commons_food_sa", "cub200", "plantdoc", "uecfoodpix"}
