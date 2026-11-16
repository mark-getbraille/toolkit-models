"""Big food collections that the kit downloads itself, straight into the picture library's downloads folder, and
keeps there for good (each is a few gigabytes, too big for the GitHub packs).

All seven are CC BY 4.0 (checked through each archive's own API: Mendeley Data, figshare and Zenodo):
  locbeef           LOCBEEF beef, fresh or rotten (Mendeley Data nhs6mjg6yy, two zips, 5.5 GB)
  fish_freshness    pangas, rui and tilapia from markets: fresh, medium or spoiled (figshare 33087308, 11.7 GB)
  horse_mackerel    horse mackerel on ice, days 0, 3 and 6 (Zenodo 23729265, 3.2 GB)
  fish_eyes_stages  fish eyes at three stages of freshness (Mendeley Data 67nmx3mhwh version 2, 3.7 GB)
  chicken_breast    chicken breast, good or bad (Mendeley Data myp3sd2zkh: 1,000 single photos, only those used
                    are downloaded)
  food_packaging    food packs with their text written out (Mendeley Data 3cpx2fmn3r version 2, 2.6 GB)
  packeat           fruit and vegetables in shops, by variety, with count and weight (Zenodo 16901178: a zip split
                    into 16 parts plus a test zip, 20.4 GB)

How these differ from sources.archive_collection: every archive here is a zip, so its pictures are read straight
out of the zip (no unpacked copy is needed, which saves as much disk space again as the download), and an archive
split into parts (Packeat's train.zip.001 to .016, a plain byte-for-byte split of one zip) is read as one file
through PartsReader, without joining the parts on disk. Pictures are picked evenly from every label, as in
archive_collection, and a label with too few pictures leaves its share to the others.

Main parts: BIG_SOURCES (Source entries for the table in sources.py), and one prepare_<key>(source, data_dir, work,
cap) function per collection.
"""

import csv
import io
import json
import os
import random
import re
import zipfile

import sources
from sources import Source, clean, have, meat_label, smaller, USER_AGENT

MENDELEY = "https://data.mendeley.com/public-api/datasets/"
ZENODO = "https://zenodo.org/api/records/"
FIGSHARE = "https://api.figshare.com/v2/articles/"
FISH_QUESTION = "How fresh is this fish?"


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


# ----------------------------------------------------------------- shared helpers

def api_json(url):
    """The JSON an archive's public API gives for url."""
    import requests
    r = requests.get(url, timeout=60, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    return r.json()


def fetch(url, path, size):
    """Download url to path once, carrying on from a part already there, when its size is known from the archive's
    API (figshare's storage refuses the size question sources.download_file asks first). Says the progress every 5
    percent of a big file; raises RuntimeError when the file does not come out at the expected size."""
    import requests
    os.makedirs(os.path.dirname(path), exist_ok=True)
    done = os.path.getsize(path) if os.path.exists(path) else 0
    if done == size:
        return
    if done > size:                                    # a different file was there: start again
        os.remove(path)
        done = 0
    headers = {"User-Agent": USER_AGENT, **({"Range": f"bytes={done}-"} if done else {})}
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        if done and r.status_code != 206:
            done = 0                                   # the server started again from the beginning
        next_say = (done * 100 // size // 5 + 1) * 5
        with open(path, "ab" if done else "wb") as f:
            for block in r.iter_content(1 << 20):
                f.write(block)
                done += len(block)
                if size > 300_000_000 and done * 100 // size >= next_say:
                    say(f"    {done * 100 // size} percent of {size / 1024 ** 3:.1f} GB")
                    next_say = done * 100 // size + 5
    if os.path.getsize(path) != size:
        raise RuntimeError(f"{os.path.basename(path)} did not download completely; it carries on the next time")


def fetch_all(files, folder):
    """Download every (url, name, size) of files into folder (kept for good in the picture library); the paths."""
    paths = []
    for number, (url, name, size) in enumerate(files, 1):
        path = os.path.join(folder, name)
        if not (os.path.exists(path) and os.path.getsize(path) == size):
            say(f"  Downloading {name}, {size / 1024 ** 3:.1f} GB (file {number} of {len(files)}; kept in the picture "
                "library, and it resumes if stopped).")
        fetch(url, path, size)
        paths.append(path)
    return paths


class PartsReader(io.RawIOBase):
    """Several files read as one, end to end: a zip split byte for byte into parts (train.zip.001, .002 ...) can then
    be opened by Python's zipfile without joining the parts into one more big file on disk."""

    def __init__(self, paths):
        """Open every part; paths in their order."""
        super().__init__()
        self.files = [open(p, "rb") for p in paths]
        self.sizes = [os.path.getsize(p) for p in paths]
        self.size, self.pos = sum(self.sizes), 0

    def readable(self):
        """It can be read."""
        return True

    def seekable(self):
        """It can be moved about in."""
        return True

    def seek(self, offset, whence=0):
        """Move to offset (from the start, the current place or the end, as for any file)."""
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def tell(self):
        """The current place."""
        return self.pos

    def readinto(self, buffer):
        """Read into buffer from the part that holds the current place (at most to that part's end)."""
        start = 0
        for f, size in zip(self.files, self.sizes):
            if self.pos < start + size:
                f.seek(self.pos - start)
                got = f.readinto(memoryview(buffer)[:min(len(buffer), start + size - self.pos)])
                self.pos += got
                return got
            start += size
        return 0

    def close(self):
        """Close every part."""
        for f in self.files:
            f.close()
        super().close()


def open_zip(paths):
    """A zipfile.ZipFile for one zip (a path) or for a zip split into parts (a list of paths, in order)."""
    if isinstance(paths, str):
        return zipfile.ZipFile(paths)
    return zipfile.ZipFile(io.BufferedReader(PartsReader(paths), 1 << 20))


def is_picture(name):
    """True for a picture file in a zip (not a folder, nor a Jupyter or macOS leftover)."""
    lower = name.lower()
    return (lower.endswith((".jpg", ".jpeg", ".png", ".bmp")) and "/." not in "/" + lower
            and "__macosx" not in lower)


def even_pick(groups, want, seed):
    """Pick want items evenly from groups ({label: [items]}): each list shuffled, then one from every label in turn,
    so a label with too few leaves its share to the others. The picks, in a fixed order."""
    lists = []
    for label in sorted(groups):
        items = sorted(groups[label])
        random.Random(f"{seed}-{label}").shuffle(items)
        lists.append(items)
    picked, index = [], 0
    while len(picked) < want and any(index < len(items) for items in lists):
        for items in lists:
            if index < len(items) and len(picked) < want:
                picked.append(items[index])
        index += 1
    return picked


def zip_collection(source, data_dir, zips, label_of, cap, seed):
    """Make training rows from pictures inside downloaded zips (see the module docstring). zips: open ZipFiles;
    label_of(name) gives (label, question, answer) for a picture's name inside its zip, or None to leave it out.
    The label is what the pictures are picked evenly by (at most cap + the source's test count of them)."""
    groups, labels = {}, {}
    for number, z in enumerate(zips):
        for name in z.namelist():
            got = is_picture(name) and label_of(name)
            if got:
                groups.setdefault(got[0], []).append((number, name))
                labels[(number, name)] = got
    if not groups:
        raise RuntimeError("no labelled pictures were found in the download")
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    picked = even_pick(groups, cap + source.test, seed)
    say(f"  Making training copies of {len(picked)} pictures from {len(groups)} kinds.")
    rows = []
    for count, (number, name) in enumerate(picked, 1):
        target = os.path.join(folder, re.sub(r"[^\w.-]", "_", name)[-120:])
        target = os.path.splitext(target)[0] + ".jpg"
        _label, question, answer = labels[(number, name)]
        if have(target) or smaller(zips[number].read(name), target):
            rows.append({"picture": target, "question": question, "answer": answer, "split": ""})
        if count % 500 == 0:
            say(f"    {count} of {len(picked)} pictures done")
    say(f"  {len(rows)} pictures from {len(groups)} kinds.")
    return rows


def mendeley_files(dataset, version, folder_id="root"):
    """The (download address, file name, size) of every file in a folder of a Mendeley Data dataset version."""
    found = api_json(f"{MENDELEY}{dataset}/files?folder_id={folder_id}&version={version}")
    return [(f["content_details"]["download_url"], f["filename"], f["content_details"]["size"]) for f in found]


def zenodo_files(record):
    """{file name: (download address, file name, size)} for a Zenodo record."""
    found = api_json(f"{ZENODO}{record}")["files"]
    return {f["key"]: (f["links"]["self"], f["key"], f["size"]) for f in found}


# ----------------------------------------------------------------- LOCBEEF

def locbeef_label(name):
    """Fresh or rotten beef, from LOCBEEF's folders ("train/fresh/Fresh (1).jpg", "test/rotten/Rotten (9).jpg"),
    with the same answers as MeatScan (sources.meat_label)."""
    got = meat_label(name)
    return got and (got[1], got[0], got[1])


def prepare_locbeef(source, data_dir, work, cap):
    """LOCBEEF (Mendeley Data nhs6mjg6yy, CC BY 4.0): 3,268 photos of local Aceh beef, fresh or rotten, in train.zip
    and test.zip (train/fresh, train/rotten, test/fresh, test/rotten): "Is this meat still safe to cook?"."""
    files = [f for f in mendeley_files("nhs6mjg6yy", 1) if f[1].lower().endswith(".zip")]
    paths = fetch_all(sorted(files, key=lambda f: f[1]), os.path.join(work, source.key))
    zips = [open_zip(p) for p in paths]
    try:
        return zip_collection(source, data_dir, zips, locbeef_label, cap, 41)
    finally:
        for z in zips:
            z.close()


# ----------------------------------------------------------------- fish freshness (figshare)

FISH_KINDS = {"pangash": "pangas catfish", "rui": "rui (rohu) fish", "telapia": "tilapia"}
FISH_VIEWS = {"fullbody": "This is a whole {fish}.", "eye": "This is a close-up of the eye of a {fish}.",
              "grill": "This is a close-up of the gills of a {fish}."}
FISH_STATES = {"fresh": "It looks fresh.",
               "medium": "It looks only moderately fresh: not spoiled, but no longer at its best.",
               "spoiled": "It looks spoiled. Do not eat it."}


def fish_freshness_label(name):
    """Species, freshness and view from the figshare fish folders, e.g. "Rui/Rui spoiled/Rui_spiled_Grill/..." or
    "Telapia/Telapia_Medium/Telapia_Medium_Fullbody/...": species from the first folder, freshness from the second
    (whose spelling is steadier than the third's), and whole fish, eye or gills ("Grill") from the third."""
    parts = name.lower().split("/")
    if len(parts) < 4 or parts[0] not in FISH_KINDS:
        return None
    state = ("spoiled" if "spoil" in parts[1] else "medium" if "medium" in parts[1]
             else "fresh" if "fresh" in parts[1] else None)
    view = next((v for v in FISH_VIEWS if v in parts[2].replace(" ", "")), None)
    if not state or not view:
        return None
    answer = FISH_VIEWS[view].format(fish=FISH_KINDS[parts[0]]) + " " + FISH_STATES[state]
    return (answer, FISH_QUESTION, answer)


def prepare_fish_freshness(source, data_dir, work, cap):
    """Fish Freshness Detection (figshare 33087308, CC BY 4.0): 6,848 market photos of pangas, rui and tilapia, each
    as a whole fish, its eye or its gills, labelled Fresh, Medium (Fresh) or Spoiled: "How fresh is this fish?"."""
    article = api_json(f"{FIGSHARE}33087308")
    files = [(f["download_url"], "DatasetOfFishFreshness.zip", f["size"]) for f in article["files"]
             if f["name"].lower().endswith(".zip")]
    path, = fetch_all(files[:1], os.path.join(work, source.key))
    with open_zip(path) as z:
        return zip_collection(source, data_dir, [z], fish_freshness_label, cap, 42)


# ----------------------------------------------------------------- horse mackerel (Zenodo)

# The article's three storage stages (README.md; the original folders were taze, orta and bayat: fresh, medium
# and stale).
MACKEREL_DAYS = {
    "day0": "This horse mackerel is fresh: it was photographed on its first day on ice.",
    "day3": "This horse mackerel is no longer fully fresh: it has been on ice for three days.",
    "day6": "This horse mackerel is not fresh: it has been on ice for six days. Do not eat it.",
}


def horse_mackerel_label(name):
    """The storage day of a whole-fish photo ("data/raw_images/Day3/IMG_6600.JPG"); the eye and skin crops
    (data/roi_eye, data/roi_skin) are left out."""
    parts = name.lower().split("/")
    if len(parts) < 3 or parts[-3] != "raw_images" or parts[-2] not in MACKEREL_DAYS:
        return None
    return (parts[-2], FISH_QUESTION, MACKEREL_DAYS[parts[-2]])


def prepare_horse_mackerel(source, data_dir, work, cap):
    """Horse Mackerel Freshness (Zenodo 23729265, data CC BY 4.0): 720 photos of single Mediterranean horse mackerel
    on a white board, from fish stored on ice for 0, 3 or 6 days: "How fresh is this fish?"."""
    path, = fetch_all([zenodo_files(23729265)["data.zip"]], os.path.join(work, source.key))
    with open_zip(path) as z:
        return zip_collection(source, data_dir, [z], horse_mackerel_label, cap, 43)


# ----------------------------------------------------------------- fish eyes (Mendeley)

FISH_EYE_STAGES = {
    "highly fresh": "This is a close-up of a fish's eye. The eye is clear and the pupil sharp: this fish is very "
                    "fresh.",
    "fresh": "This is a close-up of a fish's eye. The eye is slightly cloudy and the edge of the pupil is blurred: "
             "this fish is still fresh, but no longer at its best.",
    "not fresh": "This is a close-up of a fish's eye. The eye is very cloudy and the pupil misshapen: this fish is "
                 "not fresh. Do not eat it.",
}


def fish_eyes_label(name):
    """The stage from the folder ("Multistage Fish Eye Dataset/Highly Fresh/12.png"): highly fresh (stored up to 2
    days at 4 degrees), fresh (3 to 4 days) or not fresh (more than 4 days), as the dataset's description defines
    them."""
    parts = name.split("/")
    stage = parts[-2].strip().lower() if len(parts) >= 2 else ""
    return stage in FISH_EYE_STAGES and (stage, FISH_QUESTION, FISH_EYE_STAGES[stage])


def prepare_fish_eyes_stages(source, data_dir, work, cap):
    """Multistage Fish Eyes (Mendeley Data 67nmx3mhwh version 2, CC BY 4.0): 4,800 close-ups of the eyes of rice
    flower carp and crucian carp, 1,600 at each of three stages of freshness: "How fresh is this fish?"."""
    files = [f for f in mendeley_files("67nmx3mhwh", 2) if f[1].lower().endswith(".zip")]
    path, = fetch_all([(files[0][0], "Multistage_Fish_Eyes_Dataset.zip", files[0][2])], os.path.join(work, source.key))
    with open_zip(path) as z:
        return zip_collection(source, data_dir, [z], fish_eyes_label, cap, 44)


# ----------------------------------------------------------------- chicken breast (Mendeley, single files)

CHICKEN_QUESTION = "Is this chicken still safe to cook?"
CHICKEN_ANSWERS = {"good": "Yes: this chicken breast looks fresh.",
                   "bad": "No: this chicken breast looks spoiled. Do not eat it."}


def prepare_chicken_breast(source, data_dir, work, cap):
    """Chicken breast, good or bad (Mendeley Data myp3sd2zkh, CC BY 4.0): 1,000 single photos (about 2.3 MB each) in
    the folders Good and Bad, not in a zip, so only the photos used are downloaded (kept in the picture library):
    "Is this chicken still safe to cook?"."""
    groups = {}
    for folder in api_json(f"{MENDELEY}myp3sd2zkh/folders/1"):
        label = folder["name"].strip().lower()
        if label in CHICKEN_ANSWERS:
            for item in mendeley_files("myp3sd2zkh", 1, folder["id"]):
                if is_picture(item[1]):
                    groups.setdefault(label, []).append(item)
    if not groups:
        raise RuntimeError("no labelled pictures were found")
    picked = even_pick(groups, cap + source.test, 45)
    keep = os.path.join(work, source.key)
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    label_of = {item: label for label, items in groups.items() for item in items}
    say(f"  Downloading {len(picked)} chicken photos (kept in the picture library).")
    rows = []
    for count, item in enumerate(picked, 1):
        url, name, size = item
        label = label_of[item]
        safe = label + "_" + re.sub(r"[^\w.-]", "_", name)
        target = os.path.join(folder, os.path.splitext(safe)[0] + ".jpg")
        if not have(target):
            original = os.path.join(keep, safe)
            try:
                fetch(url, original, size)
            except Exception as e:  # noqa: BLE001 - a photo that cannot be fetched is left out
                say(f"    {name} could not be downloaded ({str(e)[:100]}); left out.")
                continue
            with open(original, "rb") as f:
                if not smaller(f.read(), target):
                    continue
        rows.append({"picture": target, "question": CHICKEN_QUESTION, "answer": CHICKEN_ANSWERS[label], "split": ""})
        if count % 100 == 0:
            say(f"    {count} of {len(picked)} photos done")
    say(f"  {len(rows)} pictures from {len(groups)} kinds.")
    return rows


# ----------------------------------------------------------------- food packaging (Mendeley)

PACK_READ = "Read the text on this package."
PACK_DATE = "What is the use-by date on this package?"
# Words that introduce a date on a pack, longest first (the transcriptions are single words). "Display until" is
# the shop's date, not the eater's, so it is not used.
DATE_WORDS = [("use", "or", "freeze", "by"), ("best", "if", "used", "by"), ("best", "before", "end"),
              ("use", "by"), ("best", "before"), ("best", "by"), ("expiry", "date"),
              ("expiry",), ("exp",), ("bbe",)]
MONTH = (r"(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?"
         r"|dec(ember)?)")
NUMERIC_DATE = re.compile(r"^\d{1,2}[./-]\d{1,2}[./-](\d{2}|\d{4})$")
MONTH_WORD = re.compile(f"^{MONTH}$", re.I)
DAY_MONTH = re.compile(rf"^(\d{{1,2}})({MONTH})$", re.I)
DAY = re.compile(r"^\d{1,2}$")
YEAR = re.compile(r"^(19|20)\d{2}$|^\d{2}$")


def pack_date(words):
    """The use-by or best-before date as printed, from a pack's words in reading order: "Use by 24/06/2021",
    "Best before 02 FEB", "Use by 25 SEP", "Best before end March 2016"; None unless a date follows the words that
    introduce it at once (up to two stray single letters or a colon may come between)."""
    low = [w.lower().strip(":.") for w in words]
    for i in range(len(words)):
        for phrase in DATE_WORDS:
            if tuple(low[i:i + len(phrase)]) != phrase:
                continue
            j = i + len(phrase)
            skipped = 0
            while j < len(words) and skipped < 2 and (len(words[j]) == 1 and not words[j].isdigit() or
                                                       words[j] == ":"):
                j, skipped = j + 1, skipped + 1
            date = date_at(words, j)
            if date:
                said = " ".join(words[i:i + len(phrase)]).lower().strip(":")
                return said[0].upper() + said[1:] + " " + date
            break
    return None


def date_at(words, j):
    """The date that starts at words[j] ("24/06/2021", "27 JAN", "25SEP", "MAY 02 22", "March 2016"), or None."""
    w = words[j] if j < len(words) else ""
    after = words[j + 1] if j + 1 < len(words) else ""
    third = words[j + 2] if j + 2 < len(words) else ""
    if NUMERIC_DATE.match(w):
        return w
    m = DAY_MONTH.match(w)
    if m:
        return m.group(1) + " " + w[len(m.group(1)):]
    if DAY.match(w) and MONTH_WORD.match(after):
        return w + " " + after
    if MONTH_WORD.match(w) and re.match(r"^(19|20)\d{2}$", after):
        return w + " " + after
    if MONTH_WORD.match(w) and DAY.match(after):
        return w + " " + after + (" " + third if YEAR.match(third) else "")
    return None


def pack_text(words):
    """A pack's words joined as they would be read: no space before , . : ; % ) ! ? and none after ( ."""
    text = ""
    for w in words:
        if text and not (w[0] in ",.:;%)!?" or text.endswith("(")):
            text += " "
        text += w
    return text


def pack_rows(z, base):
    """{picture name in the zip: (label, question, answer)} for the whole-pack photos of the detection part
    (det/train, det/valid, det/test; the rec part holds single-word crops and is left out). Its labels.txt lines are
    "0001.jpg<tab>[{"transcription": "MILK", "points": [...]}, ...]", one per word, in reading order. A pack with a
    use-by or best-before date found by pack_date asks for that; another with 3 to 40 words is read out; packs with
    more words, or with words marked unreadable ("###"), are left out."""
    found = {}
    for subset in ("train", "valid", "test"):
        try:
            lines = z.read(f"{base}det/{subset}/labels.txt").decode("utf-8-sig").splitlines()
        except KeyError:
            continue
        for line in lines:
            if "\t" not in line:
                continue
            picture, notes = line.split("\t", 1)
            try:
                words = [clean(n["transcription"]) for n in json.loads(notes)]
            except (ValueError, KeyError, TypeError):
                continue
            words = [w for w in words if w]
            name = f"{base}det/{subset}/images/{picture.strip()}"
            if not words or any("#" in w and set(w) == {"#"} for w in words):
                continue
            date = pack_date(words)
            if date:
                found[name] = ("date", PACK_DATE, f"It says: {date}.")
            elif 3 <= len(words) <= 40:
                found[name] = ("read", PACK_READ, "The main text on this package reads: " + pack_text(words))
    return found


def prepare_food_packaging(source, data_dir, work, cap):
    """Food Packaging OCR (Mendeley Data 3cpx2fmn3r version 2, CC BY 4.0): 10,920 photos of food packs, each word
    on them written out by people (no field names: brand, product and date are not marked). Used: "What is the
    use-by date on this package?" where a date follows "use by", "best before" and the like (about 350 packs, all
    used), and "Read the text on this package." for the others."""
    files = [f for f in mendeley_files("3cpx2fmn3r", 2) if f[1].lower().endswith(".zip")]
    path, = fetch_all([(files[0][0], "Food_Packaging_OCR_Dataset.zip", files[0][2])], os.path.join(work, source.key))
    with open_zip(path) as z:
        top = sorted({n.split("/")[0] for n in z.namelist() if n.endswith("/det/train/labels.txt")})
        base = (top[0] + "/") if top else ""
        found = pack_rows(z, base)
        return zip_collection(source, data_dir, [z], found.get, cap, 46)


# ----------------------------------------------------------------- Packeat (Zenodo, a zip split into parts)

# Each variety's name for one and for several, by the dataset's (species, variety) columns. None for one: not
# counted, because the counts do not fit (grapes: four "bunches" weighing 350 g; broccoli: one "head" of 12 g).
PRODUCE = {
    ("apple", "fuji"): ("Fuji apple", "Fuji apples"),
    ("apple", "golden"): ("Golden Delicious apple", "Golden Delicious apples"),
    ("apple", "granny"): ("Granny Smith apple", "Granny Smith apples"),
    ("apple", "ligol"): ("Ligol apple", "Ligol apples"),
    ("apple", "red_delicious"): ("Red Delicious apple", "Red Delicious apples"),
    ("apple", "spartan"): ("Spartan apple", "Spartan apples"),
    ("apricot", "armenian"): ("Armenian apricot", "Armenian apricots"),
    ("apricot", "jerdel"): ("Jerdel apricot", "Jerdel apricots"),
    ("avocado", "hass"): ("Hass avocado", "Hass avocados"),
    ("avocado", "zutano"): ("Zutano avocado", "Zutano avocados"),
    ("banana", "mini"): ("mini banana", "mini bananas"),
    ("banana", "yellow"): ("banana", "bananas"),
    ("beet", "round"): ("beetroot", "beetroots"),
    ("cabbage", "broccoli"): (None, "broccoli"),
    ("cabbage", "cauliflower"): ("cauliflower", "cauliflowers"),
    ("cabbage", "peking"): ("Chinese cabbage", "Chinese cabbages"),
    ("cabbage", "white"): ("white cabbage", "white cabbages"),
    ("carrot", "carrot"): ("carrot", "carrots"),
    ("corn", "corn"): ("corn cob", "corn cobs"),
    ("cucumber", "long"): ("long cucumber", "long cucumbers"),
    ("cucumber", "medium"): ("short cucumber", "short cucumbers"),
    ("daikon", "daikon"): ("daikon radish", "daikon radishes"),
    ("garlic", "garlic"): ("garlic bulb", "garlic bulbs"),
    ("grape", "black"): (None, "black grapes"),
    ("grape", "green"): (None, "green grapes"),
    ("grape", "pink"): (None, "pink grapes"),
    ("grapefruit", "grapefruit"): ("grapefruit", "grapefruits"),
    ("kiwi", "kiwi"): ("kiwi fruit", "kiwi fruits"),
    ("lemon", "orange"): ("orange-skinned lemon", "orange-skinned lemons"),
    ("lemon", "yellow"): ("lemon", "lemons"),
    ("lime", "lime"): ("lime", "limes"),
    ("mango", "mango"): ("mango", "mangoes"),
    ("melon", "torpeda"): ("Torpeda melon", "Torpeda melons"),
    ("nectarine", "flat"): ("flat nectarine", "flat nectarines"),
    ("nectarine", "round"): ("nectarine", "nectarines"),
    ("onion", "purple"): ("red onion", "red onions"),
    ("onion", "white"): ("white onion", "white onions"),
    ("orange", "orange"): ("orange", "oranges"),
    ("pear", "conference"): ("Conference pear", "Conference pears"),
    ("pear", "williams_rouge"): ("Red Williams pear", "Red Williams pears"),
    ("pepper", "chili"): ("chilli pepper", "chilli peppers"),
    ("pepper", "sweet_elonged"): ("long sweet pepper", "long sweet peppers"),
    ("pepper", "sweet_green"): ("green sweet pepper", "green sweet peppers"),
    ("pepper", "sweet_red"): ("red sweet pepper", "red sweet peppers"),
    ("pepper", "sweet_yellow"): ("yellow sweet pepper", "yellow sweet peppers"),
    ("plum", "pink"): ("pink plum", "pink plums"),
    ("plum", "purple"): ("purple plum", "purple plums"),
    ("pomegranate", "pomegranate"): ("pomegranate", "pomegranates"),
    ("pomelo", "pomelo"): ("pomelo", "pomelos"),
    ("potato", "pink"): ("pink potato", "pink potatoes"),
    ("potato", "yellow"): ("yellow potato", "yellow potatoes"),
    ("pumpkin", "elonged"): ("long pumpkin", "long pumpkins"),
    ("raddish", "elonged"): ("long radish", "long radishes"),
    ("raddish", "round"): ("round radish", "round radishes"),
    ("salad", "green"): ("head of green lettuce", "heads of green lettuce"),
    ("tangerine", "tangerine"): ("tangerine", "tangerines"),
    ("tomato", "bull_heart"): ("oxheart tomato", "oxheart tomatoes"),
    ("tomato", "cherry_red"): ("red cherry tomato", "red cherry tomatoes"),
    ("tomato", "cherry_yellow"): ("yellow cherry tomato", "yellow cherry tomatoes"),
    ("tomato", "pink"): ("pink tomato", "pink tomatoes"),
    ("tomato", "slivka"): ("plum tomato", "plum tomatoes"),
    ("tomato", "yellow"): ("yellow tomato", "yellow tomatoes"),
    ("watermelon", "elonged"): ("long watermelon", "long watermelons"),
    ("zucchini", "green"): ("green courgette (zucchini)", "green courgettes (zucchini)"),
    ("zucchini", "white"): ("white courgette (zucchini)", "white courgettes (zucchini)"),
}
NUMBERS = ["no", "one", "two", "three", "four", "five", "six"]


def produce_weight(text):
    """A weight in grams from the dataset's weight column as words ("about 780 g", "about 1.4 kg"); "" when it is
    missing, zero or not a number."""
    try:
        grams = float(str(text).strip())
    except ValueError:
        return ""
    if not grams > 0:
        return ""
    if grams < 1000:
        return f"about {max(10, round(grams, -1)):.0f} g"
    return f"about {grams / 1000:.1f} kg".replace(".0 kg", " kg")


def produce_answer(row):
    """What Packeat's labels say about one photo, e.g. "These are four Granny Smith apples in a plastic bag, about
    780 g." Counts of 1 to 6 are given as they are; 7 and more as "seven or more" (the dataset's own grouping, and
    7 is far more common than 6 or 8, so it often means "many"); 0 (not counted) and weights that are missing or
    zero are left out. "Some look spoiled" when the photo is marked spoiled."""
    one, many = PRODUCE[(row["species"], row["variety"])]
    try:
        count = int(row.get("amount") or 0) if one else 0
    except ValueError:
        count = 0
    if not one:
        text = f"This is {many}" if many == "broccoli" else f"These are {many}"
    elif count == 1:
        text = f"This is one {one}"
    elif 2 <= count <= 6:
        text = f"These are {NUMBERS[count]} {many}"
    elif count >= 7:
        text = f"These are seven or more {many}"
    else:
        text = f"These are {many}"
    if str(row.get("packed")) == "1":
        text += " in a plastic bag"
    weight = produce_weight(row.get("weight"))
    if weight:
        text += ", " + weight
    text += "."
    if str(row.get("spoiled")) == "1":
        text += " It looks partly spoiled." if count == 1 or many == "broccoli" else " Some of them look spoiled."
    return text


def prepare_packeat(source, data_dir, work, cap):
    """Packeat (Zenodo 16901178, CC BY 4.0): 103,412 shop photos of fruit and vegetables, 65 varieties of 34 species,
    some in plastic bags, each with its count and weight in variety_classification.csv. train.zip is split byte for
    byte into train.zip.001 to .016 (1 GB each; joined end to end they are one zip64 file) and test.zip is whole;
    both are kept, and read without joining or unpacking. The segmentation zips (masks) are not downloaded.
    "What is this?", answered with the variety, the count and the weight."""
    files = zenodo_files(16901178)
    parts = sorted((name for name in files if re.fullmatch(r"train\.zip\.\d{3}", name)), key=lambda n: int(n[-3:]))
    keep = os.path.join(work, source.key)
    table, = fetch_all([files["variety_classification.csv"]], keep)
    paths = fetch_all([files[name] for name in parts] + [files["test.zip"]], keep)
    by_name = {}
    with open(table, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            # "varieties_classification_dataset/train/apple_fuji/007576.jpg" is "train/train/apple_fuji/007576.jpg"
            # in the zip: the last three parts match.
            if (row.get("species"), row.get("variety")) in PRODUCE:
                by_name["/".join(row["variety_image_path"].split("/")[-3:])] = row

    def label_of(name):
        """The variety (picked evenly by) and the answer for a photo in the zips."""
        row = by_name.get("/".join(name.split("/")[-3:]))
        return row and (row["species"] + " " + row["variety"], "What is this?", produce_answer(row))

    zips = [open_zip(paths[:-1]), open_zip(paths[-1])]
    try:
        return zip_collection(source, data_dir, zips, label_of, cap, 47)
    finally:
        for z in zips:
            z.close()


# ----------------------------------------------------------------- the table

BIG_SOURCES = [
    Source("locbeef", "LOCBEEF: fresh or rotten beef (a 5.5 GB download, kept in the picture library)",
           "CC BY 4.0 (data.mendeley.com/datasets/nhs6mjg6yy)",
           "LOCBEEF beef quality image dataset (Mendeley Data nhs6mjg6yy), CC BY 4.0, "
           "https://data.mendeley.com/datasets/nhs6mjg6yy", "permissive", 2000, 20, prepare_locbeef, "5.5 GB, once"),
    Source("fish_freshness", "Fish freshness: pangas, rui and tilapia, fresh, medium or spoiled (an 11.7 GB download)",
           "CC BY 4.0 (figshare.com, article 33087308)",
           "Fish Freshness Detection Dataset (figshare 33087308), CC BY 4.0, "
           "https://doi.org/10.6084/m9.figshare.33087308.v1", "permissive", 3000, 15, prepare_fish_freshness,
           "11.7 GB, once"),
    Source("horse_mackerel", "Horse mackerel on ice: days 0, 3 and 6 (a 3.2 GB download)",
           "CC BY 4.0 for the images (zenodo.org/records/23729265, README.md)",
           "Horse Mackerel Freshness: Multi-Region Image Dataset (Ünal, Altan and Koç, Zenodo 23729265), CC BY 4.0, "
           "https://doi.org/10.5281/zenodo.23729265", "permissive", 600, 15, prepare_horse_mackerel, "3.2 GB, once"),
    Source("fish_eyes_stages", "Fish eyes: three stages of freshness (a 3.7 GB download)",
           "CC BY 4.0 (data.mendeley.com/datasets/67nmx3mhwh, version 2)",
           "Multistage Fish Eyes Dataset (Mendeley Data 67nmx3mhwh, version 2), CC BY 4.0, "
           "https://data.mendeley.com/datasets/67nmx3mhwh/2", "permissive", 1200, 15, prepare_fish_eyes_stages,
           "3.7 GB, once"),
    Source("chicken_breast", "Chicken breast: good or spoiled (up to 2.4 GB of single photos)",
           "CC BY 4.0 (data.mendeley.com/datasets/myp3sd2zkh)",
           "Good and bad classification of chicken breast (Islam and Sarkar, Mendeley Data myp3sd2zkh), CC BY 4.0, "
           "https://data.mendeley.com/datasets/myp3sd2zkh", "permissive", 800, 10, prepare_chicken_breast,
           "about 2 GB, once"),
    Source("food_packaging", "Food packs: their text read out, and use-by dates (a 2.6 GB download)",
           "CC BY 4.0 (data.mendeley.com/datasets/3cpx2fmn3r, version 2)",
           "Food Packaging OCR Dataset (Mendeley Data 3cpx2fmn3r, version 2), CC BY 4.0, "
           "https://data.mendeley.com/datasets/3cpx2fmn3r/2", "permissive", 3000, 15, prepare_food_packaging,
           "2.6 GB, once"),
    Source("packeat", "Packeat: fruit and vegetables in shops, by variety, count and weight (a 20 GB download)",
           "CC BY 4.0 (zenodo.org/records/16901178)",
           "Packeat: Packed Fruits and Vegetables Visual Classification Benchmark (Zenodo 16901178), CC BY 4.0, "
           "https://doi.org/10.5281/zenodo.16901178", "permissive", 4000, 20, prepare_packeat, "20.4 GB, once"),
]
