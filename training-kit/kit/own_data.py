"""Your own pictures: turn a folder of pictures with their descriptions into training rows, for personal use.

The person training picks a folder (train.py --own FOLDER, or "Your own pictures folder" in the program). Every
picture in it and in its sub-folders is found, and its description is taken from one of these layouts, which are
recognised by themselves (several can be mixed in one folder):

  a) a text file of the same name beside the picture: photo.jpg with photo.txt (photo.caption is read too). This is
     also how picture-making trainers expect their pictures, so one folder serves both kinds of training.
  b) a table named captions.csv or metadata.csv, with a column for the file (file, file_name, filename, image,
     image_file or path) and one for the description (description, text, caption or answer), and optionally a
     "question" column. File names are read from the table's own folder.
  c) a .jsonl file (one entry per line), each {"image" or "file_name" or "file": ..., "question": ... (optional),
     "answer" or "text" or "caption" or "description": ...}. One picture may have several lines (several questions).
  d) folders named after what they show: Pictures\\Apples\\1.jpg is learned as "What is this?", "These are apples."
     A folder is read this way only when none of its pictures has a description of its own, and never the chosen
     folder itself (its name says nothing about the pictures).

A folder made by the program's "Describe pictures" window (a describing workspace, kit\\describe_package.py) is
layout a) with a work file, describing.json, that gives each picture a status: only pictures marked "described" or
"checked" there are used; the others (not described yet, skipped, or needing another look) are left out and said.

REVIEW COLLECTIONS (review_sources.py, adult_review_sources.py): a workspace whose describing.json says
"review_only": true holds pictures that a trusted sighted adult must screen first. From such a workspace (and from
any folder inside it) ONLY pictures marked "checked" are used; "described" is not enough, and a picture the work file
does not list is never used. A description that is empty or still says "<description needed>" is refused, in any
folder. Those pictures are counted in the summary as "waiting for review".
Content: a review workspace's describing.json gives the whole collection a content tag ("content": "medical",
"intimate", "sexual" or "graphic": war, disasters, injuries and death), and a picture's own entry may give it one
too ("content": "intimate", as Fitzpatrick17k's genital-site pictures have). A picture is used only when EVERY tag it has (its own and its collection's) is among
the contents the caller allows (check_folder's contents=: the training's content choices, see
sources.allowed_contents); otherwise it is left out and said. The same applies to a tagged picture in any workspace.
Terms: a review collection's describing.json may say "review_category": "noncommercial" or "research"; such a
collection is used only when the caller allows that category (categories=: the personal-use boxes).
Picture-making training calls check_folder with review=False: then every picture in a review workspace is left out.
Rows from a review workspace have "source": "review" (not "own"), "review" (the collection's key or name),
"review_category" and "contents" (the tags it needed).
A picture whose workspace entry says "child": "yes" (pictures that needed a description, needs_workspace.py) gives
rows marked "child": True, so a picture-making training leaves it out like the packs' pictures of children.
Its other versions of a description (photo.other-Anna.txt) are never read as descriptions (only photo.txt and
photo.caption are), and a question written in the window is used instead of the usual one.

Files that are never read as descriptions: question.txt (see below), stills-for-describers.jsonl (video_frames.py's
list of stills for the describers' website), and the extra text files beside pictures: photo.draft.txt (a draft
that a person must check), photo.narration.txt (what was said near a still) and photo.other-Anna.txt (another
person's version). Only photo.txt and photo.caption describe photo.jpg.

A question.txt in a folder gives, in its first line, the question for every picture described by a text file of the
same name (layout a) in that folder and in its sub-folders, unless a sub-folder has a question.txt of its own (for
example "What is this?" for stills from your own narrated videos). A question set in the "Describe pictures" window
for one picture comes before it.

Where in the world the pictures are from (optional): a place.txt in a folder gives, in its first line, the place of
every picture in that folder and its sub-folders (unless a sub-folder has its own), for example "Accra, Ghana" or
"Kyoto, Japan": a short place name, most specific first, ending with the country. A table may have a "place" column
and a .jsonl entry a "place" key instead (and "place_kind": "origin" for an object made there). Rows then carry
"place", which teaches the model what places look like: the describer learns to say which country a photo might be
from, and a picture-making add-on learns "a kitchen in Ghana". Only give a place you know.

Otherwise a description without a question of its own is asked "Describe this picture in detail." when it has 45 words or
more, otherwise "Describe this picture." (the toolkit's own questions, as in sources.py).

Pictures may be jpg, jpeg, png, webp, bmp, gif or tif. About 1 in 20 pictures (at least 1, at most 50) is kept back
as a test picture, the same ones every time, so the model can be compared before and after training.

Main part: check_folder(folder, copies=None, report=None, contents=(), review=True, categories=OPEN_CATEGORIES) ->
(rows, problems, summary). Without copies it only checks (the
program's "Check my pictures" button), and each row's "picture" is the original file. With copies (a folder), a
smaller training copy of each picture is made there with sources.smaller, and "picture" is that copy.

Rows are in the kit's row format (as sources.prepare_source writes them): "picture", "question", "answer", "split"
("test" or ""), "source" ("own"), plus "original" (the picture in the person's folder), "file" (its place inside the
folder), "layout" (which layout described it) and "credit".

Only the Python standard library is needed to check a folder (Pillow is used when it is there, to open each
picture); sources.py is loaded only when copies are made.
"""

import csv
import hashlib
import json
import os
import re

SOURCE_KEY = "own"
CREDIT = "Your own pictures (for personal use only)"
PICTURE_ENDINGS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff")
TEXT_ENDINGS = (".txt", ".caption")
TABLE_NAMES = ("captions.csv", "metadata.csv")
FILE_COLUMNS = ("file", "file_name", "filename", "image", "image_file", "path")
TEXT_COLUMNS = ("description", "text", "caption", "answer")
JSON_FILE_KEYS = ("image", "file_name", "file", "filename")
JSON_TEXT_KEYS = ("answer", "text", "caption", "description")

# The toolkit's own questions (the same words as sources.DETAILED and sources.NARRATE).
DETAILED = "Describe this picture in detail."
NARRATE = "Describe this picture."
FOLDER_QUESTION = "What is this?"
DETAILED_WORDS = 45
SMALLEST = 64                  # pixels: a smaller picture is left out (as sources.smaller does)
SHOW = 10                      # how many file names a problem lists at most
TEST_SHARE, TEST_MOST = 20, 50  # about 1 picture in 20 is kept back for the test, at most 50
QUESTION_FILE = "question.txt"  # a folder's question for its layout a) pictures
PLACE_FILE = "place.txt"        # a folder's place (where in the world its pictures are from)
PLACE_KINDS = ("photo", "origin", "depicted")
IGNORED_LISTS = ("stills-for-describers.jsonl",)            # lists that are not descriptions
NOT_DESCRIPTIONS = (".draft.txt", ".narration.txt")         # text files beside pictures that are not descriptions
OTHER_VERSION = re.compile(r"\.other(-[^\\/]*)?\.txt$", re.IGNORECASE)  # photo.other-Anna.txt
WORK_FILE = "describing.json"   # a describing workspace's work file (describe_package.py)
READY = ("described", "checked")  # the statuses in it that are used for training
REVIEW_READY = ("checked",)       # in a review-only workspace, only this status is used
NEEDED = "<description needed>"   # a draft that still says this is not a description yet
REVIEW_SOURCE = "review"          # the "source" of rows from a review workspace
# The review categories used without a personal-use choice ("" is a review workspace that names none).
OPEN_CATEGORIES = ("", "open", "share-alike")

LAYOUT_NAMES = {"text file": "with a text file of the same name",
                "table": "listed in a captions.csv or metadata.csv table",
                "jsonl": "listed in a .jsonl file",
                "folder": "named by the folder they are in"}


# ----------------------------------------------------------------- small helpers

def clean(text):
    """A text with its spaces tidied; "" for nothing."""
    return " ".join(str(text or "").split())


def same_path(path):
    """A path in one form for comparing (full, and in the same letter case on Windows)."""
    return os.path.normcase(os.path.abspath(path))


def question_for(answer):
    """The question for a description that has none: the detailed one for long descriptions."""
    return DETAILED if len(answer.split()) >= DETAILED_WORDS else NARRATE


def folder_answer(name):
    """The answer for a picture in a folder named after what it shows: "Apples" -> "These are apples.";
    "Red bus" -> "This is: Red bus." (a leading number and underscores are left out: "01_apples" -> "apples")."""
    text = clean(re.sub(r"[_]+", " ", name))
    text = clean(re.sub(r"^\d+[\s.\-)]+", "", text)) or text
    words = text.split()
    lower = text.lower()
    if len(words) == 1 and lower.endswith("s") and not lower.endswith(("ss", "us", "is")):
        return f"These are {lower}."
    return f"This is: {text}" + ("" if text.endswith((".", "!", "?")) else ".")


def listed(items, what):
    """A plain sentence part listing up to SHOW items: "a.jpg, b.jpg and 3 more"."""
    shown = list(items[:SHOW])
    rest = len(items) - len(shown)
    return ", ".join(shown) + (f" and {rest} more" if rest else "") + (f" {what}" if what else "")


def plural(count, one, many=None):
    """ "1 picture", "3 pictures"."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


MAGIC = (b"\xff\xd8\xff", b"\x89PNG", b"GIF8", b"BM", b"II*\x00", b"MM\x00*")


def picture_size(path):
    """(width, height) of a picture, or None when it cannot be read. Uses Pillow when it is installed; without it,
    only the start of the file is checked (then the size is not known and (SMALLEST, SMALLEST) is given)."""
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if Image is not None:
        try:
            with Image.open(path) as picture:
                picture.load()
                return picture.size
        except Exception:  # noqa: BLE001 - a damaged picture or not a picture
            return None
    try:
        with open(path, "rb") as f:
            start = f.read(12)
    except OSError:
        return None
    if start.startswith(MAGIC) or (start[:4] == b"RIFF" and start[8:12] == b"WEBP"):
        return (SMALLEST, SMALLEST)
    return None


def test_order(row_file):
    """A fixed order for picking test pictures (the same pictures every time, without a random number generator)."""
    return hashlib.sha1(row_file.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------- reading the descriptions

def read_text(path):
    """The text of a description file (UTF-8, with or without a byte order mark; odd characters replaced)."""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return clean(f.read())


def column(names, wanted):
    """The first column in names (as written in the table) whose lower-case name is one of wanted, or None."""
    lower = {clean(n).lower(): n for n in names if n}
    return next((lower[w] for w in wanted if w in lower), None)


def read_table(path, found, problems, places=None):
    """Read a captions.csv or metadata.csv into found {picture path: [(question, answer, layout, where)]}; the
    problems go into problems (a dict of lists, see check_folder); places (when given) gets {picture path: (place,
    place kind)} from the optional "place" and "place_kind" columns."""
    base = os.path.dirname(path)
    name = os.path.basename(path)
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        file_col = column(reader.fieldnames or [], FILE_COLUMNS)
        text_col = column(reader.fieldnames or [], TEXT_COLUMNS)
        question_col = column(reader.fieldnames or [], ("question",))
        place_col = column(reader.fieldnames or [], ("place",))
        kind_col = column(reader.fieldnames or [], ("place_kind",))
        if not file_col or not text_col:
            problems["tables"].append(f"{name} has no column named " + ("file" if not file_col else "description") +
                                      " (the first line must name the columns, for example: file,description)")
            return
        for number, entry in enumerate(reader, 2):
            add_entry(base, name, number, entry.get(file_col), entry.get(question_col) if question_col else "",
                      entry.get(text_col), "table", found, problems)
            if place_col and places is not None:
                add_place(base, entry.get(file_col), entry.get(place_col),
                          entry.get(kind_col) if kind_col else "", places)


def read_jsonl(path, found, problems, places=None):
    """Read a .jsonl file into found and places (see read_table)."""
    base = os.path.dirname(path)
    name = os.path.basename(path)
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for number, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                entry = None
            if not isinstance(entry, dict):
                problems["lines"].append(f"line {number} of {name}")
                continue
            picture = next((entry[k] for k in JSON_FILE_KEYS if entry.get(k)), "")
            text = next((entry[k] for k in JSON_TEXT_KEYS if entry.get(k)), "")
            add_entry(base, name, number, picture, entry.get("question"), text, "jsonl", found, problems)
            if places is not None:
                add_place(base, picture, entry.get("place"), entry.get("place_kind"), places)


def add_place(base, picture, place, kind, places):
    """Note the place of a picture named in a table or .jsonl file (nothing when either is empty)."""
    place, picture = clean(place if isinstance(place, str) else "").strip(" ,."), clean(picture)
    if place and picture:
        kind = clean(kind if isinstance(kind, str) else "").lower()
        path = same_path(os.path.join(base, picture.replace("\\", os.sep).replace("/", os.sep)))
        places[path] = (place, kind if kind in PLACE_KINDS else "photo")


def add_entry(base, name, number, picture, question, text, layout, found, problems):
    """One line of a table or .jsonl file: its picture (read from the file's own folder) and description."""
    picture = clean(picture)
    where = f"line {number} of {name}"
    if not picture:
        problems["lines"].append(where + " (no picture named)")
        return
    path = same_path(os.path.join(base, picture.replace("\\", os.sep).replace("/", os.sep)))
    if not os.path.isfile(path):
        problems["missing"].append(f"{picture} ({where})")
        return
    answer = clean(text)
    if not answer:
        problems["empty"].append(where)
        found.setdefault(path, [])                 # the picture had a description, even an empty one
        return
    question = clean(question if isinstance(question, str) else "") or question_for(answer)
    found.setdefault(path, []).append((question, answer, layout, where))


# ----------------------------------------------------------------- the folder

def walk(folder):
    """(pictures, tables, jsonl files) under folder; hidden folders (a name starting with ".") and __MACOSX are
    skipped. Pictures are in a fixed order."""
    pictures, tables, lists = [], [], []
    for base, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__MACOSX")
        for name in sorted(files):
            lower = name.lower()
            path = os.path.join(base, name)
            if lower.endswith(PICTURE_ENDINGS) and not name.startswith("."):
                pictures.append(path)
            elif lower in TABLE_NAMES:
                tables.append(path)
            elif lower.endswith(".jsonl") and lower not in IGNORED_LISTS:
                lists.append(path)
    return pictures, tables, lists


def workspace_info(folder, cache):
    """What a describing workspace's work file in folder says, as a dict: "pictures" {picture file name in lower
    case: (status, question, content tag, True when its entry marks a child)}, "review" (True when "review_only" is true), "content" (the collection's
    content tag, "" for none), "category" (its review_category) and "name" (its review_source key, or its name).
    A folder that is not a workspace, or whose work file cannot be read, gives empty values. cache keeps each
    folder's answer."""
    if folder not in cache:
        info = {"pictures": {}, "review": False, "content": "", "category": "", "name": "", "workspace": False}
        try:
            with open(os.path.join(folder, WORK_FILE), encoding="utf-8") as f:
                data = json.load(f)
            info["workspace"] = True
            info["review"] = data.get("review_only") is True or str(data.get("review_only")).lower() == "true"
            info["content"] = clean(data.get("content", "")).lower()
            info["category"] = clean(data.get("review_category", "")).lower()
            info["name"] = clean(data.get("review_source", "")) or clean(data.get("name", "")) or \
                os.path.basename(folder)
            for name, entry in data.get("pictures", {}).items():
                if isinstance(entry, dict):
                    info["pictures"][name.lower()] = (str(entry.get("status", "new")),
                                                      clean(entry.get("question", "")),
                                                      clean(entry.get("content", "")).lower(),
                                                      str(entry.get("child", "")).lower() in ("yes", "true"))
        except (OSError, ValueError, AttributeError):
            pass
        cache[folder] = info
    return cache[folder]


def workspace_status(folder, cache):
    """{picture file name in lower case: (status, question)} from a describing workspace's work file in folder
    ({} when the folder is not a workspace or its work file cannot be read); cache keeps each folder's answer."""
    return {name: found[:2] for name, found in workspace_info(folder, cache)["pictures"].items()}


def review_home(folder, cache, infos):
    """The review-only workspace folder that folder is (or is inside), or None. Every folder above is looked at,
    so pictures in a sub-folder of a review collection (which its work file does not list) are never used as
    ordinary pictures. cache keeps each folder's answer; infos is workspace_info's cache."""
    key = same_path(folder)
    if key not in cache:
        parent = os.path.dirname(key)
        if workspace_info(folder, infos)["review"]:
            cache[key] = folder
        else:
            cache[key] = review_home(parent, cache, infos) if parent != key else None
    return cache[key]


def needed_contents(picture_tag, collection_tag):
    """The content tags a picture needs: its own and its collection's (without "")."""
    return sorted({t for t in (picture_tag, collection_tag) if t})


def not_a_description(path):
    """True for a text file that is never a picture's description: question.txt, and photo.draft.txt,
    photo.narration.txt and photo.other-Anna.txt (even beside a picture named photo.draft.jpg)."""
    name = os.path.basename(path).lower()
    return name in (QUESTION_FILE, PLACE_FILE) or name.endswith(NOT_DESCRIPTIONS) or bool(OTHER_VERSION.search(name))


def sidecar(picture):
    """The text file of the same name as picture (photo.txt or photo.caption, any letter case), or None."""
    stem = os.path.splitext(picture)[0]
    for ending in TEXT_ENDINGS:
        for candidate in (stem + ending, stem + ending.upper()):
            if os.path.isfile(candidate) and not not_a_description(candidate):
                return candidate
    return None


def folder_question(base, top, cache, file_name=QUESTION_FILE):
    """The question from the nearest question.txt in base or a folder above it, up to top (the chosen folder);
    "" when there is none. cache keeps each folder's answer. file_name: another such file (place.txt, with its own
    cache)."""
    key = same_path(base)
    if key not in cache:
        path = os.path.join(base, file_name)
        question = ""
        if os.path.isfile(path):
            with open(path, encoding="utf-8-sig", errors="replace") as f:
                question = clean(next((line for line in f if line.strip()), ""))
        if not question and key != same_path(top) and os.path.dirname(key) != key:
            question = folder_question(os.path.dirname(base), top, cache, file_name)
        cache[key] = question
    return cache[key]


def make_copy(original, target):
    """Make the training copy of original at target with sources.smaller (no large library copy: the person keeps
    the originals); True when it worked."""
    import sources
    if os.path.exists(target):
        return True
    with open(original, "rb") as f:
        data = f.read()
    keep = sources.ARCHIVE_DIR
    sources.ARCHIVE_DIR = None                    # the picture library keeps no copy of a person's own pictures
    try:
        return sources.smaller(data, target)
    finally:
        sources.ARCHIVE_DIR = keep


def check_folder(folder, copies=None, report=None, contents=(), review=True, categories=OPEN_CATEGORIES):
    """Read the pictures and descriptions in folder (see the module docstring) and return (rows, problems, summary):
    rows ready for training, problems as plain sentences, and a summary in plain words (with the problems). Nothing
    is trained. copies: a folder for the smaller training copies (None: only check). report(text): says progress
    for big folders (every 500 pictures). contents: the content tags allowed ("medical", "intimate", "sexual" ...;
    none by default, so a tagged picture is left out unless the caller allows its tags). review: False leaves out
    every picture of a review-only workspace (picture-making). categories: the review categories allowed (the
    personal-use choices add "noncommercial" and "research")."""
    problems = {"tables": [], "lines": [], "missing": [], "empty": [], "undescribed": [], "unreadable": [],
                "small": [], "not ready": [], "waiting": [], "content": {}, "terms": {}, "review off": []}
    contents, categories = set(contents or ()), set(categories or ())
    folder = os.path.abspath(folder or "")
    if not folder or not os.path.isdir(folder):
        text = f"The folder {folder} was not found. Choose the folder that holds your pictures."
        return [], [text], text
    pictures, tables, lists = walk(folder)
    if not pictures:
        text = (f"No pictures were found in {folder} or its sub-folders. Pictures must be jpg, jpeg, png, webp, bmp, "
                "gif or tif files.")
        return [], [text], text

    # Descriptions from tables and .jsonl files (layouts b and c) come first; then text files of the same name (a).
    found, places, folder_places = {}, {}, {}
    for path in tables:
        read_table(path, found, problems, places)
    for path in lists:
        read_jsonl(path, found, problems, places)
    described, waiting, has_text, workspaces, questions = {}, [], set(), {}, {}
    children = set()                             # pictures whose workspace entry marks a child
    homes, tags = {}, {}                         # review workspace of each folder; each picture's review details
    for picture in pictures:
        key = same_path(picture)
        base = os.path.dirname(picture)
        relative = os.path.relpath(picture, folder)
        info = workspace_info(base, workspaces)
        status = info["pictures"].get(os.path.basename(picture).lower())
        if status and status[3]:
            children.add(picture)
        home = review_home(base, homes, workspaces)
        if home is not None:                      # a review collection's picture: the strict rules
            has_text.add(os.path.dirname(key))
            home_info = workspace_info(home, workspaces)
            if not review:
                problems["review off"].append(relative)
                continue
            if home_info["category"] not in categories:
                problems["terms"].setdefault((home_info["name"], home_info["category"]), []).append(relative)
                continue
            if not status or same_path(home) != same_path(base) or status[0] not in REVIEW_READY:
                problems["waiting"].append(relative)
                continue
            tags[picture] = (home_info["name"], home_info["category"],
                             needed_contents(status[2], home_info["content"]))
        elif status and status[0] not in READY:   # a describing workspace's picture that is not ready
            problems["not ready"].append(relative)
            has_text.add(os.path.dirname(key))
            continue
        need = tags[picture][2] if picture in tags else needed_contents(status[2] if status else "",
                                                                         info["content"])
        left = [t for t in need if t not in contents]
        if left:                                  # a content tag the training's choices do not allow
            problems["content"].setdefault(", ".join(left), []).append(relative)
            has_text.add(os.path.dirname(key))
            continue
        if need and picture not in tags:
            tags[picture] = ("", "", need)
        reviewed = picture in tags and bool(tags[picture][0])
        if key in found and not reviewed:          # a review picture is only ever described by its own .txt
            entries = [e for e in found[key] if NEEDED not in e[1].lower()]
            if len(entries) < len(found[key]) and not entries:
                problems["waiting"].append(relative)
            else:
                described[picture] = entries
            has_text.add(os.path.dirname(key))
            continue
        text_file = sidecar(picture)
        if text_file:
            has_text.add(os.path.dirname(key))
            answer = read_text(text_file)
            if answer and NEEDED in answer.lower():
                problems["waiting"].append(relative)        # a draft still waiting for its description
            elif answer:
                asked = (status[1] if status and status[1] and status[1] != NARRATE else
                         folder_question(os.path.dirname(picture), folder, questions) or question_for(answer))
                described[picture] = [(asked, answer, "text file", os.path.relpath(text_file, folder))]
            elif reviewed:
                problems["waiting"].append(relative)        # a checked review picture with an empty description
            else:
                problems["empty"].append(os.path.relpath(text_file, folder))
            continue
        if reviewed:
            problems["waiting"].append(relative)            # a review picture with no description at all
            continue
        waiting.append(picture)

    # Folder names (layout d): only in a sub-folder where no picture has a description of its own.
    named_folders = set()
    for picture in waiting:
        base = os.path.dirname(picture)
        if same_path(base) != same_path(folder) and same_path(base) not in has_text:
            described[picture] = [(FOLDER_QUESTION, folder_answer(os.path.basename(base)), "folder",
                                   os.path.relpath(base, folder))]
            named_folders.add(os.path.basename(base))
        else:
            problems["undescribed"].append(os.path.relpath(picture, folder))

    # Each described picture is opened (and, with copies, made smaller) to be sure it can be used.
    rows, used = [], 0
    if copies:
        os.makedirs(copies, exist_ok=True)
    for number, picture in enumerate(sorted(described), 1):
        if not described[picture]:
            continue                               # only empty descriptions (said as a problem already)
        relative = os.path.relpath(picture, folder)
        size = picture_size(picture)
        if size is None:
            problems["unreadable"].append(relative)
            continue
        if min(size) < SMALLEST:
            problems["small"].append(relative)
            continue
        path = picture
        if copies:
            path = os.path.join(copies, re.sub(r"[^\w.-]", "_", relative)[-150:])
            path = os.path.splitext(path)[0] + ".jpg"
            try:
                if not make_copy(picture, path):
                    problems["unreadable"].append(relative)
                    continue
            except OSError:
                problems["unreadable"].append(relative)
                continue
        used += 1
        place, kind = places.get(same_path(picture)) or (
            folder_question(os.path.dirname(picture), folder, folder_places, PLACE_FILE).strip(" ,."), "photo")
        where = ({"place": place} if kind == "photo" else {"place": place, "place_kind": kind}) if place else {}
        review_name, review_category, need = tags.get(picture, ("", "", []))
        extra = {"contents": need} if need else {}
        if picture in children:
            extra["child"] = True
        if review_name:                           # a checked picture of a review collection
            extra.update(review=review_name, review_category=review_category)
        for question, answer, layout in dict.fromkeys(entry[:3] for entry in described[picture]):
            rows.append({"picture": path, "question": question, "answer": answer, "split": "",
                         "source": REVIEW_SOURCE if review_name else SOURCE_KEY, "original": picture,
                         "file": relative.replace(os.sep, "/"), "layout": layout, "credit": CREDIT, **where,
                         **extra})
        if report and number % 500 == 0:
            report(f"    {number} of {len(described)} of your pictures checked")

    # The test pictures: about 1 in 20 (by picture, so a picture is never both learned and tested).
    files = sorted({r["file"] for r in rows}, key=test_order)
    want = 0 if len(files) < 2 else min(TEST_MOST, max(1, round(len(files) / TEST_SHARE)))
    test_files = set(files[:want])
    for row in rows:
        if row["file"] in test_files:
            row["split"] = "test"

    sentences = problem_sentences(problems)
    summary = make_summary(folder, len(pictures), used, rows, test_files, named_folders, sentences,
                           len(problems["waiting"]))
    return rows, sentences, summary


def problem_sentences(problems):
    """The problems as plain sentences, each listing up to SHOW files."""
    out = []
    p = problems
    if p["undescribed"]:
        out.append(f"{plural(len(p['undescribed']), 'picture has', 'pictures have')} no description (no text file of "
                   "the same name, and not listed in a captions.csv, metadata.csv or .jsonl file), so "
                   f"{'it is' if len(p['undescribed']) == 1 else 'they are'} left out: "
                   + listed(p["undescribed"], "") + ".")
    if p["empty"]:
        out.append(f"{plural(len(p['empty']), 'description is', 'descriptions are')} empty, so "
                   f"{'its picture is' if len(p['empty']) == 1 else 'their pictures are'} left out: "
                   + listed(p["empty"], "") + ".")
    if p["not ready"]:
        out.append(f"{plural(len(p['not ready']), 'picture')} in a describing workspace "
                   f"{'is' if len(p['not ready']) == 1 else 'are'} not described or checked yet (or skipped, or "
                   "needing another look), so left out: " + listed(p["not ready"], "") + ".")
    if p["waiting"]:
        out.append(f"{plural(len(p['waiting']), 'picture is', 'pictures are')} waiting for review (in a review "
                   "collection only pictures marked checked are used, and a description that is empty or still says "
                   f"{NEEDED} is never used), so left out: " + listed(p["waiting"], "") + ".")
    if p["review off"]:
        out.append(f"{plural(len(p['review off']), 'picture is', 'pictures are')} in a review collection, which is "
                   "never used for this kind of training, so left out: " + listed(p["review off"], "") + ".")
    for tags, files in sorted(p["content"].items()):
        out.append(f"{plural(len(files), 'picture is', 'pictures are')} marked {tags} content, which the content "
                   "choices of this training do not include (intimate needs both art with nudity and medical "
                   "pictures; sexual needs art with nudity and adult sexual content; graphic needs graphic scenes, "
                   "and a picture-making model never uses it), so left out: "
                   + listed(files, "") + ".")
    for (name, category), files in sorted(p["terms"].items()):
        box = "research-only" if category == "research" else "non-commercial"
        out.append(f"The review collection {name} is {box if category in ('research', 'noncommercial') else category}"
                   f" ({plural(len(files), 'picture')}): it is left out because Include {box} collections is not "
                   "ticked" + (" (and its terms agreed)" if category == "research" else "") + ".")
    if p["unreadable"]:
        out.append(f"{plural(len(p['unreadable']), 'picture')} could not be read (damaged, or not really a picture): "
                   + listed(p["unreadable"], "") + ".")
    if p["small"]:
        out.append(f"{plural(len(p['small']), 'picture is', 'pictures are')} too small (under {SMALLEST} pixels) and "
                   "left out: " + listed(p["small"], "") + ".")
    if p["missing"]:
        out.append(f"{plural(len(p['missing']), 'line names', 'lines name')} a picture that is not in the folder: "
                   + listed(p["missing"], "") + ".")
    if p["lines"]:
        out.append(f"{plural(len(p['lines']), 'line')} could not be read: " + listed(p["lines"], "") + ".")
    out += [f"The table {t}." for t in p["tables"]]
    return out


def make_summary(folder, found, used, rows, test_files, named_folders, sentences, waiting=0):
    """The summary in plain words: how many pictures, how they are described, how many wait for review, the test
    pictures and the problems."""
    lines = [f"Your own pictures in {folder}: {plural(found, 'picture')} found, {used} can be used for training"
             + (f", {waiting} waiting for review." if waiting else ".")]
    reviewed = len({r["file"] for r in rows if r.get("review")})
    if reviewed:
        lines.append(f"{plural(reviewed, 'picture comes', 'pictures come')} from review collections (checked by a "
                     "trusted sighted adult): the training is then for personal use only.")
    if rows:
        counts = {}
        for layout in [r["layout"] for r in {r["file"]: r for r in rows}.values()]:
            counts[layout] = counts.get(layout, 0) + 1
        parts = [f"{n} {LAYOUT_NAMES[k]}" for k, n in counts.items()]
        if named_folders:
            lines.append("How they are described: " + "; ".join(parts) + ". The folders used as names: "
                         + listed(sorted(named_folders), "") + ".")
        else:
            lines.append("How they are described: " + "; ".join(parts) + ".")
        if len(rows) != used:
            lines.append(f"Together they give {len(rows)} questions and answers to learn from.")
        kept = "1 picture is kept back as a test picture" if len(test_files) == 1 else \
            f"{len(test_files)} pictures are kept back as test pictures"
        lines.append(f"{kept}, to compare the model before and after training; the other {used - len(test_files)} "
                     f"{'is' if used - len(test_files) == 1 else 'are'} for training.")
    if sentences:
        lines.append(f"Problems ({len(sentences)}):")
        lines += [f"- {s}" for s in sentences]
    else:
        lines.append("No problems were found.")
    return "\n".join(lines)


def folder_tag(folder, rows):
    """A short code for a folder's pictures and descriptions (8 letters and digits), so a training on changed
    pictures is a new training and not mistaken for an earlier one."""
    digest = hashlib.sha1(same_path(folder).encode())
    for row in sorted(rows, key=lambda r: (r["file"], r["question"])):
        digest.update(f"\n{row['file']}\t{row['question']}\t{row['answer']}".encode())
    return digest.hexdigest()[:8]


if __name__ == "__main__":
    import sys
    _rows, _problems, _summary = check_folder(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(_summary)
