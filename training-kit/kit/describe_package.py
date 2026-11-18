"""Describing pictures with friends, offline: the data side of the program's "Describe pictures" window.

A WORKSPACE is an ordinary folder of pictures, each with its description in a text file of the same name
(photo.jpg with photo.txt: layout a) of own_data.py), so the folder can be chosen as "Your own pictures folder" for
training straight away. Beside the pictures is one work file, describing.json, which remembers for each picture:
  - its status: "new" (no description yet), "described", "checked" (a second person confirmed the description),
    "needs another look" or "skip" (left out);
  - who described it and when, who checked it and when, the question asked, notes, and the picture's fingerprint
    (a SHA-256 checksum, so the same picture is recognised under another name and never added twice);
  - "seen": short fingerprints of the earlier texts this description replaced, so an older copy of a description
    that comes back in a package is recognised as older and does not count as a difference.
The work file also holds the workspace's name and the names of the people who worked on it.

Only "described" and "checked" pictures are used for training: own_data.py reads describing.json and leaves the
others out. Another version of a description (when two people wrote different ones) is kept beside the picture as
photo.other-Anna.txt, which own_data.py never reads as a description (it only reads photo.txt and photo.caption).
When someone chooses between two versions, the versions not chosen are moved into the hidden sub-folder
".resolved versions" (own_data.py skips folders whose name starts with "."), so nothing is ever lost.

REVIEW COLLECTIONS (review_sources.py, adult_review_sources.py): a workspace whose describing.json says
"review_only": true holds pictures that a trusted sighted adult must screen first. own_data.py trains ONLY its
"checked" pictures. A package can never approve a picture on someone's behalf: importing into a review workspace
turns a package's "checked" into "described" (the person importing marks it checked themselves, after looking), and
a package made from a review workspace carries its review marks (REVIEW_KEYS, and each picture's "content" tag), so
importing it makes the receiving workspace a review workspace too. A description that still says
"<description needed>" cannot be marked checked.

People pass their work to each other as PACKAGES: zip files made by export_package and read by import_package,
carried by USB stick, email or a shared drive. Nothing is sent anywhere by this module.

Main parts:
  make_workspace(folder, name) -> Workspace         a new workspace (or the one already there)
  open_workspace(folder) -> Workspace               an existing workspace
  add_pictures(workspace, files_or_folders) -> text  copy pictures in (at most 2,048 pixels; duplicates skipped)
  register_new(workspace) -> text                    record pictures put into the folder by other means (videos)
  export_package(workspace, out_zip, which, person) -> text
  import_package(workspace, zip_path) -> text        merge a package in (see import_package for the rules)
and, for the window: describe, set_status, mark_checked, other_versions, resolve, picture_names, counts,
place_of and set_place (the workspace's optional place.txt: where in the world its pictures are from, such as
"Accra, Ghana"; it travels in packages too).

Only the Python standard library is needed; Pillow is used when it is there, to make big pictures smaller and to
turn photos the right way up.
"""

import datetime
import hashlib
import json
import os
import re
import shutil
import zipfile

WORK_FILE = "describing.json"
PERSONAL_FILE = "PERSONAL-USE.txt"
QUESTION_FILE = "question.txt"           # a folder's question for all its pictures (own_data.py reads it too)
PLACE_FILE = "place.txt"                 # where in the world the pictures are from (own_data.py reads it too)
RESOLVED_FOLDER = ".resolved versions"
PACKAGE_README = "README.txt"
PACKAGE_PICTURES = "pictures/"           # the pictures and descriptions are in this folder inside a package
# The computer's drafts of a picture (kit\prepare_data.py), kept in its entry as text and carried in packages;
# never used for training (own_data.py reads only descriptions people saved).
DRAFT_KEYS = ("draft", "draft_agreement", "draft_engines", "draft_qwen", "draft_internvl", "draft_florence",
              "draft_yours", "started_from_draft", "draft_suggested")
# What a picture's collection said about it, for pictures that came without a good description (the "needs
# description" zips of the training packs, kit\needs_workspace.py, and review packs, kit\review_pack.py): hints, its
# web page and the text gathered from it ("page_text": {"alt": ..., "caption": ...}, kept on this computer only), its
# credit, licence and marks. Kept in the entry and carried in packages; NEVER used for training (only a description a
# person saves is). "child" and "not_for_picture_making" are "yes" when set.
NEEDS_KEYS = ("hint", "needs_source", "needs_reason", "page_url", "source_url", "credit", "licence", "category",
              "child", "not_for_picture_making", "place", "place_kind", "page_text", "page_text_sources")
FORMAT = 1                               # the version of describing.json's layout

NEW, DESCRIBED, CHECKED, LOOK, SKIP = "new", "described", "checked", "needs another look", "skip"
STATUSES = (NEW, DESCRIBED, CHECKED, LOOK, SKIP)
TRAINED = (DESCRIBED, CHECKED)           # the statuses own_data.py uses for training (only CHECKED in a review one)
NEEDED = "<description needed>"          # a draft that still needs its description (never checked or trained)
# The review marks of a review collection's describing.json, carried in packages (never removed by an import).
REVIEW_KEYS = ("review_only", "content", "review_source", "review_category", "needs_explicit_choice",
               "never_for_picture_making", "never_publish")
REVIEW_NOTE = "This is a review collection: only pictures you mark checked are used."
DEFAULT_QUESTION = "Describe this picture."
PICTURE_ENDINGS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff")
LONG_SIDE = 2048                         # pixels: bigger pictures are made smaller when added
JPEG_QUALITY = 92
SEEN_MOST = 50                           # how many earlier versions' fingerprints are remembered per picture

# What export_package can put in a package.
WHICH = {"all": "all pictures",
         "not described": "the pictures that have no description yet",
         "described": "the described and checked pictures",
         "to check": "the pictures waiting to be checked (described, or needing another look)"}

PERSONAL_USE = (
    "Personal use only\n\n"
    "These pictures and descriptions are for training your own and your friends' models only. Don't publish the "
    "pictures, the descriptions or a model trained on them unless everyone involved agrees and owns the rights "
    "(to the pictures, and to anything or anyone shown in them).\n")

README = """What this zip is

This is a describing package from the Picture Model Training program: pictures and their descriptions, passed
between friends who describe pictures together. It was made by {person} on {date}, from the workspace "{name}".
It holds {what}: {count}.

How to open it
1. Start Picture Model Training (Picture-Model-Training.exe).
2. Press Describe pictures (Alt+J).
3. In Workspace folder, choose your own describing folder with Browse (Alt+B), or an empty folder for a new one.
4. Press Import a package (Alt+I) and choose this zip. Do not unpack it first.
The program adds the new pictures and descriptions to your workspace. Nothing you already wrote is lost: when two
people wrote different descriptions of the same picture, both are kept, and the picture is marked "needs another
look" so you can choose one.

What is inside
- the "pictures" folder: each picture, with its description in a text file of the same name (photo.jpg and
  photo.txt), and sometimes another person's version (photo.other-Anna.txt);
- describing.json: who described and checked each picture, and when (the program reads it);
- PERSONAL-USE.txt: these pictures are for personal use only. Please read it.

The full instructions are in "HOW TO DESCRIBE PICTURES WITH FRIENDS.txt" in the training kit's folder.
"""


class PackageProblem(Exception):
    """Something the person must put right (said in plain words)."""


# ----------------------------------------------------------------- small helpers

def now():
    """The time now, in UTC, as text that sorts by time ("2026-11-16T12:30:00Z"), the same on every computer."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def plural(count, one, many=None):
    """ "1 picture", "3 pictures"."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


def clean(text):
    """A description with its spaces tidied (line breaks kept as single spaces); "" for nothing."""
    return " ".join(str(text or "").split())


def fingerprint(text):
    """A short fingerprint of a description's words (the same for the same words, whatever the spacing)."""
    return hashlib.sha1(clean(text).encode("utf-8")).hexdigest()[:12]


def file_hash(path):
    """The SHA-256 checksum of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def bytes_hash(data):
    """The SHA-256 checksum of some bytes."""
    return hashlib.sha256(data).hexdigest()


def is_picture(name):
    """True for a picture's file name (by its ending; hidden files starting with "." are not counted)."""
    base = os.path.basename(name)
    return base.lower().endswith(PICTURE_ENDINGS) and not base.startswith(".")


def safe_person(person):
    """A person's name made safe for a file name ("Anna Smith" -> "Anna-Smith"; "someone" when empty)."""
    text = re.sub(r"[^\w-]+", "-", clean(person), flags=re.UNICODE).strip("-")
    return text[:40] or "someone"


def safe_name(name):
    """A file name made safe: only the name (no folders), without characters Windows does not allow."""
    base = os.path.basename(str(name).replace("\\", "/"))
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", base).strip(" .")
    return base[:150]


def description_path(folder, name):
    """The description file of a picture: photo.jpg -> photo.txt in the same folder."""
    return os.path.join(folder, os.path.splitext(name)[0] + ".txt")


def other_prefix(name):
    """The start of the file names of a picture's other versions: photo.jpg -> "photo.other-"."""
    return os.path.splitext(name)[0] + ".other-"


def read_file_text(path):
    """A text file's text (UTF-8, with or without a byte order mark), tidied; "" when it is missing."""
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            return clean(f.read())
    except OSError:
        return ""


def write_file_text(path, text):
    """Write a description file in UTF-8 (Notepad's usual choice), ending with a line break."""
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(clean(text) + "\n")


def free_name(folder, name, taken=()):
    """name, or name-2, name-3 ... when a file of that name (or its description) is already in folder or taken."""
    stem, ending = os.path.splitext(name)
    candidate, number = name, 1
    lower_taken = {t.lower() for t in taken}
    while (os.path.exists(os.path.join(folder, candidate)) or candidate.lower() in lower_taken
           or os.path.exists(description_path(folder, candidate))):
        number += 1
        candidate = f"{stem}-{number}{ending}"
    return candidate


def tiny_png():
    """A small grey PNG picture (80 by 80 pixels) made without Pillow, for the program's self-test."""
    import struct
    import zlib

    def chunk(kind, data):
        """One PNG chunk: length, kind, data and checksum."""
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + bytes([128, 128, 128]) * 80 for _ in range(80))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 80, 80, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


# ----------------------------------------------------------------- the workspace

class Workspace:
    """A describing workspace: its folder and the contents of its describing.json (see the module docstring)."""

    def __init__(self, folder, data):
        """Use the workspace in folder with the work file's data (made by make_workspace or open_workspace)."""
        self.folder = os.path.abspath(folder)
        self.data = data

    @property
    def name(self):
        """The workspace's name."""
        return self.data.get("name") or os.path.basename(self.folder)

    @property
    def pictures(self):
        """{file name: entry} of every picture in the workspace."""
        return self.data.setdefault("pictures", {})

    def path(self, name):
        """The full path of a file in the workspace."""
        return os.path.join(self.folder, name)

    def entry(self, name):
        """A picture's entry, with every field there (missing ones filled in)."""
        entry = self.pictures.setdefault(name, {})
        for key, value in (("status", NEW), ("described_by", ""), ("described_at", ""), ("checked_by", ""),
                           ("checked_at", ""), ("notes", ""), ("question", DEFAULT_QUESTION), ("hash", ""),
                           ("source_hash", ""), ("added_at", ""), ("changed_at", ""), ("seen", [])):
            entry.setdefault(key, value)
        return entry

    def add_person(self, person):
        """Remember a person's name in the workspace's people (once)."""
        person = clean(person)
        if person and person not in self.data.setdefault("people", []):
            self.data["people"].append(person)

    def save(self):
        """Write describing.json safely (to a new file first, then put in place, so a power cut cannot spoil it)."""
        self.data["format"] = FORMAT
        target = self.path(WORK_FILE)
        temporary = target + ".new"
        with open(temporary, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1, ensure_ascii=False, sort_keys=True)
        os.replace(temporary, target)


def is_review(workspace):
    """True when the workspace is a review collection ("review_only": true in describing.json): only its checked
    pictures are trained on."""
    return workspace.data.get("review_only") is True


def is_workspace(folder):
    """True when folder holds a describing.json."""
    return bool(folder) and os.path.isfile(os.path.join(folder, WORK_FILE))


def open_workspace(folder):
    """The workspace in folder (a Workspace is given back as it is). Raises PackageProblem when there is none."""
    if isinstance(folder, Workspace):
        return folder
    path = os.path.join(folder or "", WORK_FILE)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise PackageProblem(f"{folder} is not a describing workspace yet (it has no {WORK_FILE}).") from None
    except (OSError, ValueError) as e:
        raise PackageProblem(f"The work file {path} could not be read ({e}).") from None
    if not isinstance(data, dict):
        raise PackageProblem(f"The work file {path} is not a describing work file.")
    data.setdefault("pictures", {})
    data.setdefault("people", [])
    return Workspace(folder, data)


def write_personal_use(folder):
    """Put PERSONAL-USE.txt in folder (when it is not there)."""
    path = os.path.join(folder, PERSONAL_FILE)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8", newline="\r\n") as f:
            f.write(PERSONAL_USE)


def make_workspace(folder, name=""):
    """Make a describing workspace in folder (made when missing) called name, and give it back. A folder that is
    a workspace already is opened as it is (its name is kept). Pictures already in the folder are recorded, with
    their descriptions when they have a .txt of the same name."""
    os.makedirs(folder, exist_ok=True)
    if is_workspace(folder):
        return open_workspace(folder)
    workspace = Workspace(folder, {"format": FORMAT, "name": clean(name) or os.path.basename(os.path.abspath(folder)),
                                   "people": [], "pictures": {}, "made_at": now()})
    write_personal_use(folder)
    register_new(workspace, save=False)
    workspace.save()
    return workspace


def register_new(workspace, say=None, save=True):
    """Record the pictures in the workspace folder that describing.json does not list yet (for example the stills
    "Take stills from videos" put there): "described" when a .txt of the same name is there, otherwise "new".
    A picture that is the same as one already listed is left as it is but not recorded twice. Returns a plain
    summary."""
    workspace = open_workspace(workspace)
    known = known_hashes(workspace)
    added = described = same = 0
    for name in sorted(os.listdir(workspace.folder)):
        if not is_picture(name) or name in workspace.pictures or not os.path.isfile(workspace.path(name)):
            continue
        digest = file_hash(workspace.path(name))
        if digest in known:
            same += 1
            continue
        known[digest] = name
        entry = workspace.entry(name)
        entry.update(hash=digest, source_hash=digest, added_at=now(), changed_at=now())
        text = read_file_text(description_path(workspace.folder, name))
        if text:
            entry.update(status=DESCRIBED, described_at=now(), notes="The description came with the picture.")
            described += 1
        added += 1
    if save:
        workspace.save()
    text = (f"{plural(added, 'new picture')} recorded in the workspace, {described} of them with a description."
            + (f" {plural(same, 'picture was', 'pictures were')} the same as one already there, so "
               f"{'it was' if same == 1 else 'they were'} not recorded twice." if same else ""))
    if say:
        say(text)
    return text


def known_hashes(workspace):
    """{checksum: picture name} of every picture in the workspace (both the stored file's and its original's)."""
    known = {}
    for name in list(workspace.pictures):
        entry = workspace.entry(name)
        if not entry["hash"] and os.path.isfile(workspace.path(name)):
            entry["hash"] = file_hash(workspace.path(name))
        for key in ("hash", "source_hash"):
            if entry[key]:
                known.setdefault(entry[key], name)
    return known


# ----------------------------------------------------------------- adding pictures

def picture_files(files_or_folders):
    """Every picture in the files and folders given (folders with their sub-folders; hidden folders skipped)."""
    found = []
    for item in files_or_folders:
        if os.path.isdir(item):
            for base, dirs, files in os.walk(item):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                found += [os.path.join(base, n) for n in sorted(files) if is_picture(n)]
        elif is_picture(item) and os.path.isfile(item):
            found.append(item)
    return found


def store_picture(source, target):
    """Copy the picture source to target, at most LONG_SIDE pixels on its longest side and the right way up
    (Pillow); without Pillow, or when the picture needs nothing, it is copied as it is."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        shutil.copyfile(source, target)
        return
    try:
        with Image.open(source) as picture:
            turned = picture.getexif().get(0x0112, 1) not in (0, 1)        # the photo's "turn me" mark
            if max(picture.size) <= LONG_SIDE and not turned:
                shutil.copyfile(source, target)
                return
            picture = ImageOps.exif_transpose(picture)
            picture.thumbnail((LONG_SIDE, LONG_SIDE), Image.LANCZOS)
            ending = os.path.splitext(target)[1].lower()
            if ending in (".jpg", ".jpeg"):
                picture.convert("RGB").save(target, quality=JPEG_QUALITY)
            else:
                picture.save(target)
    except Exception:  # noqa: BLE001 - a picture Pillow cannot open is copied as it is (own_data says if it is bad)
        shutil.copyfile(source, target)


def add_pictures(workspace, files_or_folders, person="", say=None):
    """Copy pictures (files, or folders of pictures) into the workspace, each at most 2,048 pixels; exact
    duplicates (the same file, by checksum) are skipped. A picture with a .txt of the same name brings its
    description along ("described"). say(text) is told the progress every 50 pictures. Returns a plain summary."""
    workspace = open_workspace(workspace)
    if isinstance(files_or_folders, str):
        files_or_folders = [files_or_folders]
    sources = picture_files(files_or_folders)
    if not sources:
        return "No pictures were found there. Pictures must be jpg, jpeg, png, webp, bmp, gif or tif files."
    known = known_hashes(workspace)
    added = described = duplicates = renamed = 0
    for number, source in enumerate(sources, 1):
        digest = file_hash(source)
        if digest in known:
            duplicates += 1
            continue
        wanted = safe_name(os.path.basename(source)) or f"picture-{number}.jpg"
        name = free_name(workspace.folder, wanted, workspace.pictures)
        renamed += name != wanted
        store_picture(source, workspace.path(name))
        stored = file_hash(workspace.path(name))
        if stored in known:                       # the same as a picture there once made smaller
            os.remove(workspace.path(name))
            duplicates += 1
            continue
        known[digest] = known[stored] = name
        entry = workspace.entry(name)
        entry.update(hash=stored, source_hash=digest, added_at=now(), changed_at=now())
        text = read_file_text(os.path.splitext(source)[0] + ".txt")
        if text:
            write_file_text(description_path(workspace.folder, name), text)
            entry.update(status=DESCRIBED, described_at=now(), notes="The description came with the picture.")
            described += 1
        added += 1
        if say and number % 50 == 0:
            say(f"{number} of {len(sources)} pictures looked at.")
    workspace.add_person(person)
    workspace.save()
    parts = [f"{plural(added, 'picture')} added"]
    if described:
        parts.append(f"{described} with a description that came with {'it' if described == 1 else 'them'}")
    if duplicates:
        parts.append(f"{plural(duplicates, 'picture was', 'pictures were')} already there and skipped")
    if renamed:
        parts.append(f"{plural(renamed, 'picture was', 'pictures were')} given a new name because the name was taken")
    return ", ".join(parts) + "."


# ----------------------------------------------------------------- describing, checking, the status

def description(workspace, name):
    """A picture's description ("" when it has none)."""
    workspace = open_workspace(workspace)
    return read_file_text(description_path(workspace.folder, name))


def other_versions(workspace, name):
    """A picture's other versions: [(file path, person, text)] from its .other-<person>.txt files."""
    workspace = open_workspace(workspace)
    prefix = other_prefix(name).lower()
    found = []
    for file in sorted(os.listdir(workspace.folder)):
        if file.lower().startswith(prefix) and file.lower().endswith(".txt"):
            person = file[len(prefix):-4]
            found.append((workspace.path(file), re.sub(r"-\d+$", "", person).replace("-", " "),
                          read_file_text(workspace.path(file))))
    return found


def remember_replaced(entry, old_text, new_text):
    """Remember the fingerprint of a description that is being replaced by another (see "seen")."""
    if old_text and clean(old_text) != clean(new_text):
        seen = [f for f in entry["seen"] if f != fingerprint(old_text)]
        entry["seen"] = (seen + [fingerprint(old_text)])[-SEEN_MOST:]


def describe(workspace, name, text, person, question=DEFAULT_QUESTION):
    """Save a picture's description written by person (status "described"; it stays "needs another look" while
    other versions are waiting). An empty text removes the description (status "new"). Returns the status."""
    workspace = open_workspace(workspace)
    entry = workspace.entry(name)
    old = description(workspace, name)
    path = description_path(workspace.folder, name)
    entry["question"] = clean(question) or DEFAULT_QUESTION
    if not clean(text):
        if os.path.exists(path):
            os.remove(path)
        remember_replaced(entry, old, "")
        entry.update(status=NEW, described_by="", described_at="", checked_by="", checked_at="", changed_at=now())
    elif clean(text) != old:
        write_file_text(path, text)
        remember_replaced(entry, old, text)
        entry.update(status=LOOK if other_versions(workspace, name) else DESCRIBED, described_by=clean(person),
                     described_at=now(), checked_by="", checked_at="", changed_at=now())
    elif entry["status"] in (NEW, SKIP, LOOK):    # the same words, now found right: described again
        entry.update(status=LOOK if other_versions(workspace, name) else DESCRIBED,
                     described_by=entry["described_by"] or clean(person), described_at=entry["described_at"] or now(),
                     changed_at=now())
    workspace.add_person(person)
    workspace.save()
    return entry["status"]


def set_status(workspace, name, status, person="", note=""):
    """Set a picture's status ("needs another look" or "skip", or back to "new" or "described"); a note is added to
    its notes with the person's name."""
    workspace = open_workspace(workspace)
    if status not in STATUSES:
        raise PackageProblem(f"Unknown status: {status}")
    entry = workspace.entry(name)
    entry.update(status=status, changed_at=now())
    if status != CHECKED:
        entry.update(checked_by="", checked_at="")
    if clean(note):
        entry["notes"] = clean(f"{entry['notes']} {clean(person) or 'Someone'}: {clean(note)}")
    workspace.add_person(person)
    workspace.save()
    return status


def set_notes(workspace, name, notes):
    """Replace a picture's notes (what the people describing it tell each other)."""
    workspace = open_workspace(workspace)
    entry = workspace.entry(name)
    entry.update(notes=clean(notes), changed_at=now())
    workspace.save()


def question_of(workspace, name):
    """The question shown for a picture: its own when one was written, otherwise the first line of the workspace's
    question.txt (made by the video tool, for example "What is this?"), otherwise DEFAULT_QUESTION. own_data.py
    asks the same question when training."""
    workspace = open_workspace(workspace)
    own = clean(workspace.entry(name)["question"])
    if own and own != DEFAULT_QUESTION:
        return own
    first = next((line for line in read_lines(workspace.path(QUESTION_FILE)) if line.strip()), "")
    return clean(first) or DEFAULT_QUESTION


def place_of(workspace):
    """The workspace's place: the first line of its place.txt ("" when there is none)."""
    workspace = open_workspace(workspace)
    return clean(next((line for line in read_lines(workspace.path(PLACE_FILE)) if line.strip()), ""))


def set_place(workspace, place):
    """Write the workspace's place into place.txt (a short place name ending with the country, such as "Kyoto,
    Japan"); an empty place removes the file. own_data.py gives every picture in the folder this place."""
    workspace = open_workspace(workspace)
    place = clean(place).strip(" ,.")
    path = workspace.path(PLACE_FILE)
    if place:
        write_file_text(path, place)
    elif os.path.exists(path):
        os.remove(path)


def read_lines(path):
    """The lines of a text file ([] when it is missing)."""
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            return f.read().splitlines()
    except OSError:
        return []


def mark_checked(workspace, name, person):
    """A second person confirms the description is right (status "checked"). Raises PackageProblem when the picture
    has no description, or other versions are still waiting."""
    workspace = open_workspace(workspace)
    if not description(workspace, name):
        raise PackageProblem("This picture has no description yet, so it cannot be checked.")
    if NEEDED in description(workspace, name).lower():
        raise PackageProblem(f"The description still says {NEEDED}. Write what the picture shows in its place "
                             "first, then mark it as checked.")
    if other_versions(workspace, name):
        raise PackageProblem("This picture has another version of its description. Choose one first (Show the "
                             "other version).")
    entry = workspace.entry(name)
    entry.update(status=CHECKED, checked_by=clean(person), checked_at=now(), changed_at=now())
    workspace.add_person(person)
    workspace.save()
    return entry


def resolve(workspace, name, text, person):
    """Settle a picture with other versions: text becomes its description (written by person), and every version
    not kept is moved into the hidden ".resolved versions" folder, so nothing is lost. Status "described"."""
    workspace = open_workspace(workspace)
    entry = workspace.entry(name)
    old = description(workspace, name)
    for path, _person, other in other_versions(workspace, name):
        remember_replaced(entry, other, text)
        retire_other(workspace, path)
    remember_replaced(entry, old, text)
    write_file_text(description_path(workspace.folder, name), text)
    entry.update(status=DESCRIBED, described_by=clean(person) if clean(text) != old else entry["described_by"],
                 described_at=now() if clean(text) != old else entry["described_at"], checked_by="", checked_at="",
                 changed_at=now())
    workspace.add_person(person)
    workspace.save()
    return entry


def picture_names(workspace, show="all"):
    """The workspace's pictures in name order, for the window's list; show: "all", "not described",
    "needs another look", "described" (described and checked), "checked", "skipped" (set aside or skipped), or
    "drafts disagree" (not described, the pictures whose drafts agree least first)."""
    workspace = open_workspace(workspace)
    wanted = {"all": STATUSES, "not described": (NEW,), "needs another look": (LOOK,), "described": TRAINED,
              "checked": (CHECKED,), "skipped": (SKIP,), "drafts disagree": (NEW,)}.get(show, STATUSES)
    names = [n for n in sorted(workspace.pictures, key=str.lower)
             if workspace.entry(n)["status"] in wanted and os.path.isfile(workspace.path(n))]
    if show == "drafts disagree":            # the drafts that agree least first; pictures without drafts last
        names.sort(key=lambda n: agreement_of(workspace.entry(n)))
    return names


def agreement_of(entry):
    """How much a picture's drafts agree (Dataset Preparation's draft_agreement, 0 to 1); 2 when it has none."""
    try:
        return float(entry.get("draft_agreement", ""))
    except ValueError:
        return 2.0


def counts(workspace):
    """{status: how many pictures} and "all"."""
    workspace = open_workspace(workspace)
    found = {s: 0 for s in STATUSES}
    for name in workspace.pictures:
        status = workspace.entry(name)["status"]
        found[status if status in found else NEW] += 1
    found["all"] = len(workspace.pictures)
    return found


# ----------------------------------------------------------------- packages

def chosen_for(workspace, which):
    """The pictures export_package puts in a package (see WHICH)."""
    statuses = {"all": STATUSES, "not described": (NEW,), "described": TRAINED, "to check": (DESCRIBED, LOOK)}
    if which not in statuses:
        raise PackageProblem(f"Unknown choice of pictures: {which}. Choose one of: {', '.join(WHICH)}.")
    return [n for n in sorted(workspace.pictures, key=str.lower)
            if workspace.entry(n)["status"] in statuses[which] and os.path.isfile(workspace.path(n))]


def export_package(workspace, out_zip, which="all", person="", say=None):
    """Make a package (a zip) of the workspace's chosen pictures (which: see WHICH) with their descriptions, other
    versions and describing.json entries, a README.txt saying what it is and how to open it, and PERSONAL-USE.txt.
    person: who is making it. Returns a plain summary."""
    workspace = open_workspace(workspace)
    names = chosen_for(workspace, which)
    if not names:
        raise PackageProblem(f"There are no pictures to export: the workspace has none of {WHICH[which]}.")
    workspace.add_person(person)
    # Each entry carries the question asked (also one from the workspace's question.txt, which is not packed).
    entries = {n: dict(workspace.entry(n), question=question_of(workspace, n)) for n in names}
    meta = {"format": FORMAT, "name": workspace.name, "people": workspace.data.get("people", []),
            "pictures": entries, "package": {"made_by": clean(person), "made_at": now(), "which": which}}
    if place_of(workspace):
        meta["place"] = place_of(workspace)            # where the pictures are from (place.txt is not packed)
    if is_review(workspace):                           # the review marks travel with the pictures
        meta.update({k: workspace.data[k] for k in REVIEW_KEYS if k in workspace.data})
    folder = os.path.dirname(os.path.abspath(out_zip))
    os.makedirs(folder, exist_ok=True)
    temporary = out_zip + ".new"
    described = 0
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(PACKAGE_README, README.format(
            person=clean(person) or "someone", date=now()[:10], name=workspace.name, what=WHICH[which],
            count=f"{plural(len(names), 'picture')}").replace("\n", "\r\n"))
        z.writestr(PERSONAL_FILE, PERSONAL_USE.replace("\n", "\r\n"))
        z.writestr(WORK_FILE, json.dumps(meta, indent=1, ensure_ascii=False, sort_keys=True))
        for number, name in enumerate(names, 1):
            z.write(workspace.path(name), PACKAGE_PICTURES + name, compress_type=zipfile.ZIP_STORED)
            text_path = description_path(workspace.folder, name)
            if os.path.exists(text_path):
                z.write(text_path, PACKAGE_PICTURES + os.path.basename(text_path))
                described += 1
            for path, _person, _text in other_versions(workspace, name):
                z.write(path, PACKAGE_PICTURES + os.path.basename(path))
            if say and number % 50 == 0:
                say(f"{number} of {len(names)} pictures put in the package.")
    os.replace(temporary, out_zip)
    workspace.save()
    return (f"The package {os.path.basename(out_zip)} was made with {plural(len(names), 'picture')} "
            f"({described} with a description). Pass it on by USB stick, email or a shared drive.")


def read_package(zip_path):
    """(meta, {file name inside the pictures folder: zip member name}) of a package. Raises PackageProblem when it
    is not a describing package."""
    try:
        z = zipfile.ZipFile(zip_path)
    except (OSError, zipfile.BadZipFile) as e:
        raise PackageProblem(f"{os.path.basename(zip_path)} could not be opened as a zip file ({e}).") from None
    with z:
        try:
            meta = json.loads(z.read(WORK_FILE).decode("utf-8-sig"))
        except KeyError:
            raise PackageProblem(f"{os.path.basename(zip_path)} is not a describing package (it has no "
                                 f"{WORK_FILE}).") from None
        except ValueError as e:
            raise PackageProblem(f"The package's {WORK_FILE} could not be read ({e}).") from None
        members = {}
        for info in z.infolist():
            if info.filename.startswith(PACKAGE_PICTURES) and not info.is_dir():
                inner = info.filename[len(PACKAGE_PICTURES):]
                if "/" not in inner and safe_name(inner) == inner:      # nothing outside the folder, no odd names
                    members[inner] = info.filename
    if not isinstance(meta, dict) or not isinstance(meta.get("pictures"), dict):
        raise PackageProblem("The package's work file is not a describing work file.")
    return meta, members


def import_package(workspace, zip_path, say=None):
    """Merge a package into the workspace (made from the package's name when the folder is not a workspace yet).

    New pictures are added (a different picture with a name already used gets a new name). For a picture both
    sides have (recognised by its checksum, whatever its name):
      - when only one side has a description, it is kept;
      - when both have the same text, it is kept (the newer status is taken, for example "checked");
      - when one text is an earlier version of the other (the newer one remembers replacing it), the newer is kept;
      - when they really differ, the newer one becomes the .txt and the other is saved beside it as
        <name>.other-<person>.txt, and the picture is marked "needs another look", so nothing is ever lost.
    In a review workspace (or with a package made from one, which makes this workspace a review one too), a
    package's "checked" becomes "described": only the person importing can mark it checked, after looking at it.
    A picture checked here stays checked when the package brings the same description.
    Returns a plain summary, such as "12 new pictures, 30 descriptions added, 2 differences to look at."."""
    if not isinstance(workspace, Workspace) and not is_workspace(workspace):
        meta, _members = read_package(zip_path)
        workspace = make_workspace(workspace, meta.get("name", ""))
    workspace = open_workspace(workspace)
    meta, members = read_package(zip_path)
    their_entries = meta["pictures"]
    if isinstance(meta.get("place"), str) and meta["place"].strip() and not place_of(workspace):
        set_place(workspace, meta["place"])            # the sender's place, when this workspace has none yet
    sender = clean((meta.get("package") or {}).get("made_by", ""))
    became_review = False
    if meta.get("review_only") is True:                # a package from a review collection keeps its marks
        became_review = not is_review(workspace)
        for key in REVIEW_KEYS:
            if key in meta and not workspace.data.get(key):
                workspace.data[key] = meta[key]
        workspace.data["review_only"] = True
    review = is_review(workspace)
    known = known_hashes(workspace)
    tally = {"new": 0, "added": 0, "updated": 0, "differences": 0, "checks": 0, "renamed": 0, "missing": 0,
             "unchecked": 0, "review": review, "became review": became_review}
    with zipfile.ZipFile(zip_path) as z:
        for number, (their_name, theirs) in enumerate(sorted(their_entries.items()), 1):
            if not isinstance(theirs, dict) or not is_picture(their_name) or their_name not in members:
                tally["missing"] += 1
                continue
            data = z.read(members[their_name])
            digest = bytes_hash(data)
            theirs = dict(checked_entry(theirs), hash=digest)
            if meta.get("review_only") is True and not theirs.get("content") and meta.get("content"):
                theirs["content"] = meta["content"]    # each picture keeps its collection's content tag
            if review and theirs.get("status") == CHECKED:
                # A package cannot approve a picture of a review collection on someone's behalf.
                theirs.update(status=DESCRIBED, checked_by="", checked_at="")
                tally["unchecked"] += 1
            their_text_name = os.path.splitext(their_name)[0] + ".txt"
            their_text = clean(z.read(members[their_text_name]).decode("utf-8-sig", "replace")) \
                if their_text_name in members else ""
            their_others = [(m, clean(z.read(members[m]).decode("utf-8-sig", "replace"))) for m in sorted(members)
                            if m.lower().startswith(other_prefix(their_name).lower()) and m.lower().endswith(".txt")]
            ours_name = known.get(digest) or known.get(theirs.get("source_hash") or "-")
            if ours_name is None:
                name = free_name(workspace.folder, safe_name(their_name), workspace.pictures)
                tally["renamed"] += name != their_name
                add_from_package(workspace, name, data, theirs, their_text, their_others, tally)
                known[digest] = name
            else:
                before = dict(workspace.entry(ours_name)), description(workspace, ours_name)
                merge_picture(workspace, ours_name, theirs, their_text, their_others, sender, tally)
                entry = workspace.entry(ours_name)
                if review and before[0]["status"] == CHECKED and entry["status"] == DESCRIBED and \
                        description(workspace, ours_name) == before[1]:
                    # Checked here, and the package brought the same words: the check made here stays.
                    entry.update({k: before[0][k] for k in ("status", "checked_by", "checked_at")})
            if say and number % 50 == 0:
                say(f"{number} of {len(their_entries)} pictures of the package looked at.")
    for person in meta.get("people", []) + [sender]:
        workspace.add_person(person)
    write_personal_use(workspace.folder)
    workspace.save()
    return import_summary(tally, sender)


def other_person(member):
    """The person in an other version's file name: "photo.other-Anna-Smith-2.txt" -> "Anna-Smith"."""
    person = member.split(".other-", 1)[-1][:-4]
    return re.sub(r"-\d+$", "", person) or "someone"


def retire_other(workspace, path):
    """Move an other version that is settled into the hidden ".resolved versions" folder (nothing is deleted)."""
    keep = os.path.join(workspace.folder, RESOLVED_FOLDER)
    os.makedirs(keep, exist_ok=True)
    shutil.move(path, os.path.join(keep, f"{now().replace(':', '-')} {os.path.basename(path)}"))


def checked_entry(theirs):
    """A package's entry for a picture with only sensible values (an odd or damaged entry cannot spoil the
    workspace): known statuses, text fields as text, "seen" as a list of fingerprints."""
    entry = {}
    for key, value in theirs.items():
        if key == "seen":
            entry[key] = [f for f in value if isinstance(f, str)][-SEEN_MOST:] if isinstance(value, list) else []
        elif key in ("page_text", "page_text_sources") and isinstance(value, dict):
            entry[key] = {str(k): v for k, v in value.items() if isinstance(v, str)}   # text fields only
        elif isinstance(value, str):
            entry[key] = value
    if entry.get("status") not in STATUSES:
        entry["status"] = NEW
    return entry


def add_from_package(workspace, name, data, theirs, text, others, tally):
    """Add a picture that is new to the workspace, with its description, other versions and entry."""
    with open(workspace.path(name), "wb") as f:
        f.write(data)
    entry = workspace.entry(name)
    entry.update({k: v for k, v in theirs.items() if k in entry})
    if theirs.get("content"):
        entry["content"] = theirs["content"]      # a review picture's content tag ("intimate" ...) comes along
    for key in DRAFT_KEYS + NEEDS_KEYS:            # the computer's drafts and the collection's hints come along
        if theirs.get(key):
            entry[key] = theirs[key]
    entry["added_at"] = entry["added_at"] or now()
    if text:
        write_file_text(description_path(workspace.folder, name), text)
        tally["added"] += 1
    elif entry["status"] in (DESCRIBED, CHECKED, LOOK):
        entry["status"] = NEW                     # a status that says "described" needs a description
    for member, other_text in others:
        save_other(workspace, name, other_text, other_person(member))
    if others:
        entry["status"] = LOOK
    tally["new"] += 1


def save_other(workspace, name, text, person):
    """Save another version of a picture's description as <name>.other-<person>.txt (a new number when that file
    is there already), unless the same text is already the description or another version. True when saved."""
    text = clean(text)
    if not text or text == description(workspace, name) or any(text == t for _p, _person, t in
                                                                other_versions(workspace, name)):
        return False
    stem = other_prefix(name) + safe_person(person)
    path, number = workspace.path(stem + ".txt"), 1
    while os.path.exists(path):
        number += 1
        path = workspace.path(f"{stem}-{number}.txt")
    write_file_text(path, text)
    return True


def merge_picture(workspace, name, theirs, their_text, their_others, sender, tally):
    """Merge the package's version of a picture the workspace already has (the rules are in import_package)."""
    entry = workspace.entry(name)
    our_text = description(workspace, name)
    seen = list(dict.fromkeys(entry["seen"] + [f for f in theirs.get("seen", []) if isinstance(f, str)]))
    their_newer = (theirs.get("changed_at") or "") > (entry["changed_at"] or "")
    fields = ("status", "described_by", "described_at", "checked_by", "checked_at", "question", "changed_at")
    counted = False
    for key in DRAFT_KEYS + NEEDS_KEYS:            # drafts and hints we do not have yet come along (ours kept)
        if theirs.get(key) and not entry.get(key):
            entry[key] = theirs[key]
    if their_text and not our_text:                                   # only theirs: take it
        write_file_text(description_path(workspace.folder, name), their_text)
        entry.update({k: theirs.get(k, entry[k]) for k in fields})
        tally["added"] += 1
    elif their_text and their_text != our_text:
        our_print, their_print = fingerprint(our_text), fingerprint(their_text)
        if their_print in entry["seen"] or any(their_text == t for _p, _w, t in other_versions(workspace, name)):
            pass                                                      # an older version we already had: keep ours
        elif our_print in theirs.get("seen", []):                     # ours is the older one: take theirs
            write_file_text(description_path(workspace.folder, name), their_text)
            entry.update({k: theirs.get(k, entry[k]) for k in fields})
            tally["updated"] += 1
        else:                                                         # a real difference: keep both
            theirs_newer = (theirs.get("described_at") or "") > (entry["described_at"] or "")
            if theirs_newer:
                write_file_text(description_path(workspace.folder, name), their_text)
                save_other(workspace, name, our_text, entry["described_by"] or "earlier")
                entry.update({k: theirs.get(k, entry[k]) for k in ("described_by", "described_at", "question")})
            else:
                save_other(workspace, name, their_text, theirs.get("described_by") or sender)
            entry.update(status=LOOK, checked_by="", checked_at="", changed_at=now())
            entry["notes"] = clean(f"{entry['notes']} Two different descriptions came together on {now()[:10]}: "
                                   "choose one with Show the other version.")
            tally["differences"] += 1
            counted = True
    elif their_text and their_newer:                                  # the same text: the newer status counts
        if theirs.get("status") == CHECKED and entry["status"] != CHECKED:
            tally["checks"] += 1
        entry.update({k: theirs.get(k, entry[k]) for k in fields})
    elif not their_text and not our_text and their_newer and theirs.get("status") in (NEW, SKIP, LOOK):
        entry.update(status=theirs["status"], changed_at=theirs.get("changed_at", now()))
    # Our other versions that they have settled (they remember replacing them), or that are now the description,
    # are moved to ".resolved versions"; their other versions that we do not have yet come along.
    current = description(workspace, name)
    for path, _person, other_text in other_versions(workspace, name):
        if fingerprint(other_text) in theirs.get("seen", []) or other_text == current:
            retire_other(workspace, path)
    brought = False
    for member, other_text in their_others:
        if fingerprint(other_text) not in entry["seen"] and save_other(workspace, name, other_text,
                                                                         other_person(member)):
            entry.update(status=LOOK, checked_by="", checked_at="")
            brought = True
    if brought and not counted:
        tally["differences"] += 1                                     # a difference found on their side
    if theirs.get("content") and not entry.get("content"):
        entry["content"] = theirs["content"]      # a content tag is never lost (only ever added)
    their_notes = clean(theirs.get("notes", ""))
    if their_notes and their_notes not in entry["notes"]:
        entry["notes"] = clean(f"{entry['notes']} {their_notes}")
    entry["seen"] = seen[-SEEN_MOST:]
    if other_versions(workspace, name):
        entry["status"] = LOOK                                        # waiting versions always need a look


def import_summary(tally, sender):
    """The plain summary of import_package."""
    parts = [plural(tally["new"], "new picture"), f"{plural(tally['added'], 'description')} added"]
    if tally["updated"]:
        parts.append(f"{plural(tally['updated'], 'description')} updated to a newer version")
    if tally["checks"]:
        parts.append(f"{plural(tally['checks'], 'check')} added")
    parts.append(f"{plural(tally['differences'], 'difference')} to look at")
    text = ", ".join(parts) + "."
    if sender:
        text = f"From {sender}: " + text
    if tally["renamed"]:
        text += (f" {plural(tally['renamed'], 'picture had', 'pictures had')} the same name as a different picture "
                 "of yours, so it was given a new name.")
    if tally["missing"]:
        text += (f" {plural(tally['missing'], 'entry in the package has', 'entries in the package have')} no picture, "
                 "so it was left out." if tally["missing"] == 1 else " so they were left out.")
    if tally.get("became review"):
        text += (" The package comes from a review collection, so this workspace is now a review collection too: "
                 "only pictures you mark checked are used for training.")
    if tally.get("unchecked"):
        text += (f" {plural(tally['unchecked'], 'picture was', 'pictures were')} marked checked in the package; in a "
                 "review collection only a check made here counts, so "
                 f"{'it is' if tally['unchecked'] == 1 else 'they are'} described here. Look at "
                 f"{'it' if tally['unchecked'] == 1 else 'each one'} and mark it checked yourself (Alt+C).")
    if tally["differences"]:
        text += (" Choose Needs another look in Filter to find the differences, and use Show the other version on "
                 "each.")
    return text


def self_test(folder):
    """Make a tiny workspace in folder, describe a picture, export it and import it into a second workspace; raises
    AssertionError when something is wrong (for the program's --self-test)."""
    source = os.path.join(folder, "source")
    os.makedirs(source)
    with open(os.path.join(source, "grey.png"), "wb") as f:
        f.write(tiny_png())
    first = make_workspace(os.path.join(folder, "first"), "Self-test")
    assert "1 picture added" in add_pictures(first, [source], "Tester")
    describe(first, "grey.png", "A plain grey square.", "Tester")
    package = os.path.join(folder, "package.zip")
    export_package(first, package, "all", "Tester")
    summary = import_package(os.path.join(folder, "second"), package)
    assert "1 new picture, 1 description added, 0 differences" in summary, summary
    assert description(os.path.join(folder, "second"), "grey.png") == "A plain grey square."
    return summary
