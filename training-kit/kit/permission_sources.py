"""PERMISSION-GATED picture collections: pictures whose owners forbid copying unless they give permission.

Why: these organisations publish some of the best pictures there are of healthy adult bodies, normal variation,
skin conditions on every skin tone and the warning signs of breast cancer, but every one of them keeps its rights
("all rights reserved", a no-derivatives licence, a research agreement, or terms that ask to be asked first). The
owner of the kit (blind, running GetBraille.com) is writing to each one. Nothing here downloads anything until that
organisation's reply is on file.

THE PERMISSION GATE
  Each collection has a folder <library>\\Permissions\\<key>\\ (for example C:\\Pictures\\Permissions\\dermnet\\).
  permission_on_file(library, key) is True only when that folder holds a permission record: any .eml, .msg, .pdf,
  .txt or .docx file (an email saved as a file, a letter, or a plain note of a phone call). Without one, every fetch
  refuses with a plain message (NoPermission) that says where to put the reply. A README in the Permissions folder
  explains this in plain words for screen-reader users (write_permissions_readme).
  The kit does not read the wording of the permission: the person who files it must keep to its conditions (credit
  wording, no sharing, a time limit). The conditions can be written in the note.

WHAT A FETCH DOES (fetch_<key>(folder, cap, say, source=None, library=None))
  - source is a folder or a zip file the organisation sent (or, for DDI and Geograph, the download address they
    gave): the pictures are imported from it, with their captions from the files that came with them (photo.txt or
    photo.caption beside photo.jpg, a CSV or TSV table naming the files, an Instagram data download's JSON, or the
    file and folder names when there is nothing else).
  - source is None: the pictures are downloaded politely from the public site (at most one request every
    2 seconds per site, or the site's own Crawl-delay when longer; a User-Agent naming the kit; robots.txt
    honoured for every address, pictures included), skipping pictures already there or already tried, so a stopped
    run carries on where it stopped. Collections that are not on a website the kit may read (Brown Skin Matters,
    DDI) need a source; the fetch says so plainly.
  - Every picture arrives in a "Describe pictures" review workspace (describe_package.py, through
    review_sources.ReviewWorkspace) with a DRAFT description made from the source's own caption, title or topic
    (clinical and plain; medical ones end "Only a doctor can diagnose this."), the credit "Used with permission of
    <organisation>", and the status "needs another look". The review instructions of review_sources.py
    (REVIEW-INSTRUCTIONS.txt) apply, with a paragraph about the permission added. Only pictures a sighted, trusted
    adult marks "checked" are ever trained on (own_data.py's rule for review workspaces).
  - ADULTS ONLY and NO SEXUAL CONTENT, as in review_sources.py: a record whose text mentions or suggests a child, or
    gives an age under 18, is left out (DermNet's paediatric, infant, neonatal and congenital topics among them),
    and so is a record naming sexual activity.
  - SKIN TONE is recorded only when the source states it (a Fitzpatrick type, DDI's skin-tone column, the skin tone
    a caption or file name gives, such as the Labia Library's "medium-dark skin tone" or the Skin of Color Society
    file names' "light", "medium" or "dark"), never guessed.

How to use (for the kit's own code):
  PERMISSION_SOURCES   a list of plain dicts: key, organisation, contact, letter (the owner's letter file), category
                       ("permission"), content ("intimate", "medical" or ""), credit, cap, fetch, plus name, licence,
                       terms, terms_summary, how (how it fetches, in plain words), needs_source (True when there is
                       no website route), review_only (True) and permission_folder ("Permissions\\<key>").
  permission_on_file(library, key), permission_status(library), write_permissions_readme(library),
  library_of(folder)   (the library a review workspace belongs to: <library>\\Review\\<key> gives <library>).
  NoPermission         the exception a fetch raises when no permission is on file (str(e) is the plain message).

    python permission_sources.py --list <key> [how many]   (reads only the public listing pages and prints what it
                                                            parsed; never fetches a picture, needs no permission)
    python permission_sources.py <key> <folder> [cap] [source] [library]   (a real run: needs the permission)

Only requests and Pillow are needed (as for the rest of the kit). Nothing is sent anywhere except the requests for
the listings and pictures themselves.
"""

import csv
import hashlib
import html
import json
import os
import re
import shutil
import time
import urllib.parse
import zipfile

import describe_package as dp
import review_sources as rs

USER_AGENT = ("PictureModelTrainingKit/2 (permission-based review download; "
              "https://github.com/mark-getbraille/toolkit-models)")
ROBOTS_NAME = "PictureModelTrainingKit"  # the name robots.txt rules are matched against
GAP = 2.0                                # seconds between two requests to the same site (at least)
PERMISSIONS = "Permissions"              # <library>\Permissions\<key>\ holds each organisation's reply
README_NAME = "README - PERMISSIONS.txt"
RECORD_ENDINGS = (".eml", ".msg", ".pdf", ".txt", ".docx")
KEY_FILE = "api-key.txt"                 # Geograph's API key, kept beside its permission (not a permission itself)
LISTING_CACHE = ".permission-listing.json"   # a hidden copy of a big listing (DermNet), reused for a week
IMPORT_FOLDER = ".permission-import"     # a hidden folder for unpacking a zip that was sent (removed afterwards)
DOWNLOAD_FOLDER = ".permission-download"  # a hidden folder for a zip downloaded from a given address (resumable)
WEEK = 7 * 24 * 3600


class NoPermission(RuntimeError):
    """Raised by a fetch when no permission record is on file (or the collection needs a source that was not
    given). str(error) is a plain message for the person."""


# ----------------------------------------------------------------- the permission gate

def library_of(folder, library=None):
    """The picture library a review workspace belongs to: library when given, else the KIT_LIBRARY environment
    variable, else the folder above "Review" (<library>\\Review\\<key>), else the folder above the workspace."""
    if library:
        return os.path.abspath(library)
    if os.environ.get("KIT_LIBRARY"):
        return os.path.abspath(os.environ["KIT_LIBRARY"])
    parent = os.path.dirname(os.path.abspath(folder))
    if os.path.basename(parent).lower() == "review":
        return os.path.dirname(parent)
    return parent


def permission_folder(library, key):
    """<library>\\Permissions\\<key>: where the organisation's reply is kept."""
    return os.path.join(library, PERMISSIONS, key)


def permission_records(library, key):
    """The permission records in <library>\\Permissions\\<key>: files ending .eml, .msg, .pdf, .txt or .docx that are
    not empty, not hidden, not a Word lock file (~$...), not the README and not Geograph's api-key.txt."""
    folder = permission_folder(library, key)
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return []
    found = []
    for name in names:
        path = os.path.join(folder, name)
        low = name.lower()
        if not low.endswith(RECORD_ENDINGS) or low.startswith((".", "~$")) or low == KEY_FILE \
                or low.startswith("readme"):
            continue
        try:
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                found.append(name)
        except OSError:
            continue
    return found


def permission_on_file(library, key):
    """True only when <library>\\Permissions\\<key>\\ holds a permission record (see permission_records)."""
    return bool(permission_records(library, key))


PERMISSIONS_README = """PERMISSIONS FOLDER (Picture Model Training Kit)

What this folder is for
Some picture collections belong to organisations that do not allow copying unless they give permission. The kit
downloads one of these collections ONLY when the organisation's reply is kept here, in the folder with that
collection's short name. Without a reply, the kit refuses and tells you which folder to use.

How to add a permission
1. Open the folder with the collection's short name (the list is below). If it is not there, make a new folder with
   exactly that name.
2. Save the organisation's reply into it. Any of these counts:
   - the email itself, saved as a file (in Outlook: File, Save As; it ends .msg or .eml);
   - a letter or form they sent (.pdf or .docx);
   - a plain text note (.txt) that you write yourself, for example after a phone call: who agreed, on what date,
     and exactly what they allowed.
3. Run the collection again in the kit.

Good to know
- The kit only checks that a reply is here. It does not read the wording, so please keep to any conditions
  yourself (for example the credit wording, "for your own use only", "do not share the model", or a time limit).
  Writing the conditions in a note in the same folder helps you and anyone who helps you.
- Removing the reply stops future downloads. Pictures already downloaded stay in their review workspace until you
  delete them.
- Every downloaded picture still needs a check by a sighted, trusted adult before it is ever used for training.
- Geograph only: if they give you an API key, put it alone in a file called api-key.txt in the geograph folder.
  That file is not a permission by itself.

The collections, their folder names, and your letters
{table}
"""


def write_permissions_readme(library):
    """Write (or refresh) the plain-language README in <library>\\Permissions and make each collection's folder, so a
    screen-reader user can find the right place for each reply. Returns the README's path."""
    folder = os.path.join(library, PERMISSIONS)
    os.makedirs(folder, exist_ok=True)
    rows = []
    for entry in PERMISSION_SOURCES:
        os.makedirs(os.path.join(folder, entry["key"]), exist_ok=True)
        state = "reply on file" if permission_on_file(library, entry["key"]) else "no reply yet"
        rows.append(f"- {entry['key']}: {entry['organisation']} ({state}). Your letter: {entry['letter']}. "
                    f"Contact: {entry['contact']}")
    path = os.path.join(folder, README_NAME)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(PERMISSIONS_README.format(table="\n".join(rows)))
    return path


def permission_status(library):
    """[(key, organisation, True when a reply is on file, the folder)] for every collection (for the wizard)."""
    return [(e["key"], e["organisation"], permission_on_file(library, e["key"]),
             permission_folder(library, e["key"])) for e in PERMISSION_SOURCES]


def refusal(entry, library):
    """The plain refusal message for entry (and the folder made ready, with the README)."""
    folder = permission_folder(library, entry["key"])
    try:
        write_permissions_readme(library)
    except OSError:
        pass
    return (f"No permission is on file for {entry['organisation']}. Put their reply (an email saved as a file, or a "
            f"note of it) in {folder}, then try again.")


def check_permission(entry, folder, library, say):
    """The library, when a permission record for entry is on file; otherwise say the refusal and raise
    NoPermission."""
    library = library_of(folder, library)
    if not permission_on_file(library, entry["key"]):
        message = refusal(entry, library)
        say(message)
        raise NoPermission(message)
    return library


# ----------------------------------------------------------------- polite downloading

class Robots:
    """The rules of one robots.txt for the kit, read the way the robots.txt standard (RFC 9309) says: the group
    whose User-agent names the kit (else the "*" group); the LONGEST matching Allow or Disallow rule wins, Allow
    winning a tie; "*" and "$" work as wildcards. (Python's own robotparser takes the first rule that matches,
    which reads Breastcancer.org's "Allow: /" before its Disallow lines as allowing everything.) A Crawl-delay
    written before any User-agent line (as on the Labia Library) is taken as meant for everyone."""

    def __init__(self, text="", allow_all=False, disallow_all=False):
        """Rules from the text of a robots.txt (or allow or forbid everything)."""
        self.allow_all, self.disallow_all = allow_all, disallow_all
        self.rules, self.delay = [], None
        groups, current, loose_delay, in_agents = [], None, None, False
        for line in (text or "").splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            field, value = (part.strip() for part in line.split(":", 1))
            field = field.lower()
            if field == "user-agent":
                if not in_agents:
                    current = {"agents": [], "rules": [], "delay": None}
                    groups.append(current)
                current["agents"].append(value.lower())
                in_agents = True
                continue
            in_agents = False
            if field == "crawl-delay":
                try:
                    number = float(value)
                except ValueError:
                    continue
                if current is None:
                    loose_delay = number
                else:
                    current["delay"] = number
            elif field in ("allow", "disallow") and current is not None:
                current["rules"].append((field == "allow", value))
        name = ROBOTS_NAME.lower()
        mine = [g for g in groups if any(a != "*" and a in name for a in g["agents"])] \
            or [g for g in groups if "*" in g["agents"]]
        for group in mine:
            self.rules += [(allow, path) for allow, path in group["rules"] if path or not allow]
            self.delay = group["delay"] if group["delay"] is not None else self.delay
        if self.delay is None:
            self.delay = loose_delay

    @staticmethod
    def matches(path, rule):
        """True when the address path (with its query) matches a robots.txt rule (with * and $)."""
        pattern = re.escape(rule).replace(r"\*", ".*")
        if pattern.endswith(r"\$"):
            pattern = pattern[:-2] + "$"
        return re.match(pattern, path) is not None

    def can_fetch(self, url):
        """True when the kit may fetch url."""
        if self.allow_all:
            return True
        if self.disallow_all:
            return False
        parts = urllib.parse.urlsplit(url)
        path = urllib.parse.unquote(parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        best = None                                   # (length, allow)
        for allow, rule in self.rules:
            if not rule:                              # "Disallow:" with nothing: allows everything
                continue
            if self.matches(path, urllib.parse.unquote(rule)):
                candidate = (len(rule), allow)
                if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and allow):
                    best = candidate
        return True if best is None else best[1]


class Polite:
    """A careful downloader: one requests session with the kit's User-Agent, robots.txt read and honoured per
    site (pictures included), and at least GAP seconds (or the site's Crawl-delay) between two requests to the
    same site."""

    def __init__(self, say=None, gap=GAP):
        """A downloader that tells say(text) about addresses robots.txt forbids."""
        self.session = rs.session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.say = say or (lambda text: None)
        self.gap = gap
        self.last = {}                   # {site: time of its last request}
        self.robots = {}                 # {site: RobotFileParser}
        self.refused = 0

    @staticmethod
    def site(url):
        """scheme://host of url."""
        parts = urllib.parse.urlsplit(url)
        return f"{parts.scheme}://{parts.netloc}"

    def wait(self, site):
        """Sleep until this site may be asked again."""
        delay = self.gap
        robot = self.robots.get(site)
        if robot is not None and robot.delay:
            delay = max(delay, min(robot.delay, 60.0))
        passed = time.time() - self.last.get(site, 0)
        if passed < delay:
            time.sleep(delay - passed)
        self.last[site] = time.time()

    def robot(self, site):
        """The site's robots.txt rules (read once). A missing robots.txt (4xx) allows everything; a site that
        cannot be reached or answers with an error (5xx) is treated as forbidding everything, to be safe."""
        if site not in self.robots:
            self.wait(site)
            try:
                r = self.session.get(site + "/robots.txt", timeout=60)
                if r.status_code >= 500:
                    parser = Robots(disallow_all=True)
                elif r.status_code >= 400:
                    parser = Robots(allow_all=True)
                else:
                    parser = Robots(r.text)
            except Exception:  # noqa: BLE001 - unreachable: nothing is fetched from it
                parser = Robots(disallow_all=True)
            self.robots[site] = parser
        return self.robots[site]

    def allowed(self, url):
        """True when robots.txt allows the kit to fetch url."""
        return self.robot(self.site(url)).can_fetch(url)

    def get(self, url, **kwargs):
        """GET url politely (None when robots.txt forbids it or it fails)."""
        if not self.allowed(url):
            self.refused += 1
            self.say(f"  robots.txt does not allow {url}; skipped.")
            return None
        self.wait(self.site(url))
        return rs.get(self.session, url, tries=3, **kwargs)

    def text(self, url):
        """The text of a page, or "" when it cannot be read."""
        r = self.get(url)
        return r.text if r is not None and r.status_code == 200 else ""

    def json(self, url):
        """A JSON answer, or None."""
        r = self.get(url, timeout=180)
        if r is None or r.status_code != 200:
            return None
        try:
            return r.json()
        except ValueError:
            return None

    def picture(self, url):
        """The JPEG bytes of the picture at url (made smaller, the right way up, review_sources.jpeg), or None."""
        r = self.get(url, timeout=120)
        if r is None or r.status_code != 200 or not r.content:
            return None
        if "html" in (r.headers.get("content-type") or "").lower():
            return None
        return rs.jpeg(r.content)

    def download_file(self, url, path):
        """Download url to path, carrying on from a partial copy (path + ".part") when the server allows it.
        Returns path, or raises OSError with a plain message."""
        if os.path.isfile(path):
            return path
        if not self.allowed(url):
            raise OSError(f"robots.txt of {self.site(url)} does not allow downloading {url}.")
        part = path + ".part"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        for _attempt in range(6):
            have = os.path.getsize(part) if os.path.isfile(part) else 0
            headers = {"Range": f"bytes={have}-"} if have else {}
            self.wait(self.site(url))
            try:
                with self.session.get(url, headers=headers, stream=True, timeout=120) as r:
                    if r.status_code == 416:                      # already complete
                        break
                    if r.status_code not in (200, 206):
                        raise OSError(f"the address answered {r.status_code}")
                    mode = "ab" if r.status_code == 206 and have else "wb"
                    with open(part, mode) as f:
                        for chunk in r.iter_content(1 << 20):
                            f.write(chunk)
                break
            except Exception as e:  # noqa: BLE001 - tried again from where it stopped
                last = e
                time.sleep(10)
        else:
            raise OSError(f"The download from {url} did not finish ({last}). Run it again to carry on.")
        os.replace(part, path)
        return path


# ----------------------------------------------------------------- small helpers

def stable_name(key, ident):
    """A file name that stays the same for the same picture on every run (so a stopped run can carry on)."""
    slug = re.sub(r"[^a-z0-9]+", "-", rs.clean(ident).lower()).strip("-")[:40]
    digest = hashlib.sha1(f"{key}:{ident}".encode("utf-8")).hexdigest()[:10]
    return f"{key}-{slug + '-' if slug else ''}{digest}.jpg"


TONE_GROUP = {"very light": "I-II", "very fair": "I-II", "fair": "I-II", "light": "I-II", "pale": "I-II",
              "light-medium": "III-IV", "medium-light": "III-IV", "light brown": "III-IV", "olive": "III-IV",
              "medium": "III-IV", "moderate brown": "III-IV", "medium-dark": "III-IV",
              "dark": "V-VI", "dark brown": "V-VI", "very dark": "V-VI", "black": "V-VI"}
TONE_WORDS = re.compile(r"\b(very light|very fair|light-medium|medium-light|medium-dark|light brown|moderate brown|"
                        r"dark brown|very dark|fair|light|pale|olive|medium|dark|black)(?:[- ]skin(?:ned)?)?"
                        r"(?: tone| colou?r)?\b", re.I)


def skin_from_value(value):
    """(group, words) from a skin-tone value a source gives in a table, caption or file name: a Fitzpatrick number
    (1 to 6, or DDI's 12, 34, 56), a Roman numeral, or a tone word (light, medium, dark ...); ("not stated", "")
    when there is none."""
    value = rs.clean(value)
    if not value:
        return rs.GROUPS[3], ""
    pairs = {"12": (0, "very fair to fair skin (Fitzpatrick type I or II)"),
             "34": (1, "light brown to moderate brown skin (Fitzpatrick type III or IV)"),
             "56": (2, "dark brown to black skin (Fitzpatrick type V or VI)")}
    if value in pairs:
        group, words = pairs[value]
        return rs.GROUPS[group], "on " + words
    roman = {v: k for k, v in rs.ROMAN.items()}
    number = rs.fitz_type(value) or roman.get(value.upper())
    if number:
        return rs.GROUPS[(number - 1) // 2], f"on {rs.SKIN_WORDS[number]} skin (Fitzpatrick type {rs.ROMAN[number]})"
    group, words = rs.skin_from_text(value)
    if words:
        return group, words
    m = TONE_WORDS.search(value)
    if m:
        tone = m.group(1).lower()
        return TONE_GROUP.get(tone, rs.GROUPS[3]), f"the source describes the skin tone as {tone}"
    return rs.GROUPS[3], ""


def plain_caption(text, words=70):
    """A caption tidied for a draft: no tags, at most about words words."""
    return rs.first_sentences(rs.no_tags(text), words, 4)


YOUNG = re.compile(r"\b(?:when (?:I|we) (?:was|were)|(?:I|we) (?:was|were)|at(?: the age of)?|aged?) "
                   r"(?:only |just )?([1-9]|1[0-7])\b(?! ?(?:%|percent|cm|kg|weeks? pregnant))", re.I)


def adults_and_clinical(*texts):
    """(True, "") when the texts suggest no child (review_sources.child_free, plus "I was 15" and the like) and
    name nothing sexual; otherwise (False, why)."""
    text = " ".join(rs.clean(t) for t in texts if t)
    if not rs.child_free(text) or YOUNG.search(text):
        return False, "mentions or suggests a child or an age under 18"
    if not rs.not_sexual(text):
        return False, "names something sexual"
    return True, ""


def intimate_text(*texts):
    """True when the texts name the genitals or breasts."""
    text = " ".join(rs.clean(t) for t in texts if t)
    return bool(rs.GENITAL.search(text) or rs.BREAST.search(text))


def read_cache(ws, max_age=WEEK):
    """The listing kept in the workspace by an earlier run (when younger than max_age seconds), or None."""
    path = os.path.join(ws.folder, LISTING_CACHE)
    try:
        if time.time() - os.path.getmtime(path) < max_age:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    return None


def write_cache(ws, data):
    """Keep a listing in the workspace (a hidden file), so a run that carries on does not read it again."""
    try:
        with open(os.path.join(ws.folder, LISTING_CACHE), "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        pass


# ----------------------------------------------------------------- the review workspace

PERMISSION_EXTRA = """
PERMISSION: these pictures are used with permission of {organisation}. Their reply is kept in {folder}
({records}). The pictures are NOT free to share: keep them, and anything made from them, to what that permission
allows. Each picture's credit says "Used with permission of {organisation}".
"""

GENERAL_REVIEW = """REVIEW-ONLY COLLECTION: {name}

These pictures were collected with the permission of their owners. NONE of them is used for training until a person
has checked it.

For every picture:
1. DELETE the picture (do not just skip it) when it shows, or may show, a child or a young person under 18 as its
   main subject.
2. DELETE any picture that is sexual, violent or private in any way.
3. Read the draft description. It was made from the source's own title and caption and may be wrong or incomplete.
   Correct it so that it says plainly what is visible.
4. Mark the picture "checked" ONLY when you are sure it is suitable and correctly described.

Only checked pictures are ever trained on.

Where each picture comes from, and its licence, is in CREDITS.txt and in each picture's notes.
Source: {credit}
Licence or terms: {licence}
"""


class PermissionWorkspace(rs.ReviewWorkspace):
    """A review workspace (review_sources.ReviewWorkspace) for a permission-gated collection: it also records the
    permission in describing.json and in REVIEW-INSTRUCTIONS.txt."""

    def __init__(self, folder, entry, library, say=None):
        """Open (or make) the workspace in folder for entry (one of PERMISSION_SOURCES)."""
        records = permission_records(library, entry["key"])
        perm_folder = permission_folder(library, entry["key"])
        source = dict(entry, instructions_extra=PERMISSION_EXTRA.format(
            organisation=entry["organisation"], folder=perm_folder, records=", ".join(records) or "none")
            + entry.get("instructions_extra", ""))
        super().__init__(folder, source, say)
        if not entry["content"]:                          # not medical: the general instructions
            with open(os.path.join(self.folder, rs.REVIEW_FILE), "w", encoding="utf-8", newline="\r\n") as f:
                f.write(GENERAL_REVIEW.format(name=entry["name"], credit=entry["credit"],
                                              licence=f"{entry['licence']} ({entry['terms_summary']})")
                        + source["instructions_extra"])
        self.workspace.data.update(permission={"organisation": entry["organisation"], "folder": perm_folder,
                                               "records": records, "checked_at": dp.now()},
                                   never_publish=True)
        self.workspace.save()
        self.entry = entry

    def put(self, item, data):
        """Add one picture (JPEG bytes) for item (a dict made by a listing or by the local import)."""
        org = self.entry["organisation"]
        credit = f"Used with permission of {org}" + (f"; {item['credit_extra']}" if item.get("credit_extra") else "")
        licence = f"used with permission of {org} (see {self.entry['permission_folder']})"
        self.add(item["name"], data, item_text(self.entry, item), credit, licence, item.get("page", ""),
                 item.get("content") or self.entry["content"] or "", item.get("note", ""),
                 item.get("skin", rs.GROUPS[3]))


def item_text(entry, item):
    """The draft description of one picture: from its own caption, title or topic; clinical and plain, with
    "Only a doctor can diagnose this." for medical and intimate collections."""
    caption = item.get("caption") or ""
    if not entry["content"]:                              # Geograph: a plain photo caption, no medical sentence
        lead = rs.clean(item.get("lead", ""))
        parts = [f"{lead} {rs.sentence(caption)}"] if lead.endswith(":") else [rs.sentence(lead), rs.sentence(caption)]
        if item.get("extra"):
            parts.append(rs.sentence(item["extra"]))
        return " ".join(p for p in parts if p) or "A photograph."
    text = rs.draft(item.get("lead", ""), caption, [item.get("title", ""), caption] + item.get("texts", []),
                    extra=item.get("extra", ""), skin_words=item.get("skin_words", ""))
    return re.sub(r"([.!?] )([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)   # "inner lips" at a start


def fill_web(ws, items, cap, polite):
    """Download items into ws one at a time (politely) until it holds cap pictures; returns how many could not be
    downloaded. Pictures already there or tried before are skipped."""
    failed = 0
    for item in items:
        if ws.full(cap):
            break
        if ws.done(item["name"]):
            continue
        data = polite.picture(item["url"])
        if data is None:
            ws.mark_tried(item["name"])
            failed += 1
            continue
        ws.put(item, data)
    return failed


# ----------------------------------------------------------------- importing what an organisation sent

CAPTION_COLUMNS = ("caption", "alt", "alt_text", "alt text", "description", "comment", "title", "label", "disease",
                   "diagnosis", "condition", "topic", "subject", "imageclass", "tags", "name")
CREDIT_COLUMNS = ("credit", "photographer", "realname", "author", "contributor", "copyright", "artist")
SKIN_COLUMNS = ("skin_tone", "skin tone", "skintone", "fitzpatrick", "fitzpatrick_scale", "fitzpatrick type",
                "skin_type", "skin type", "phototype")
AGE_COLUMNS = ("age", "patient_age", "age_years", "age (years)")
TITLE_COLUMNS = ("title", "label", "disease", "condition", "diagnosis", "topic", "subject")


def fix_mojibake(text):
    """Instagram's data download writes UTF-8 text as if it were Latin-1; this puts it right (or leaves it)."""
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def read_table(path):
    """The rows of a CSV or TSV file as dicts with lower-case column names ([] when it cannot be read)."""
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;") if sample else csv.excel
            return [{rs.clean(k).lower(): rs.clean(v) for k, v in row.items() if k} for row in
                    csv.DictReader(f, dialect=dialect)]
    except (OSError, csv.Error, UnicodeDecodeError):
        return []


def first_of(row, columns):
    """The first non-empty value of row among columns ("" when none)."""
    for column in columns:
        if row.get(column):
            return row[column]
    return ""


def json_pictures(path):
    """{file path relative to the JSON's folder tree: caption} from a JSON file such as Instagram's data download
    (posts_1.json: media with "uri" and "title")."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    found = {}

    def walk(node, caption=""):
        """Look for {"uri": picture, "title": caption} anywhere in the data."""
        if isinstance(node, dict):
            caption = node.get("title") if isinstance(node.get("title"), str) and node.get("title") else caption
            uri = node.get("uri")
            if isinstance(uri, str) and dp.is_picture(uri):
                found[uri.replace("\\", "/")] = fix_mojibake(caption or "")
            for value in node.values():
                walk(value, caption)
        elif isinstance(node, list):
            for value in node:
                walk(value, caption)
    walk(data)
    return found


def collect_local(top):
    """Every picture under the folder top, as dicts: path, rel (path inside top), caption, title, credit, skin
    (the raw value), age, folder (the folder names above it). Captions come from photo.txt or photo.caption beside
    photo.jpg, from any CSV/TSV table naming the files, or from an Instagram-style JSON file; titles fall back on
    the folder and file names."""
    pictures, tables, jsons = [], [], []
    for here, folders, files in os.walk(top):
        folders[:] = sorted(f for f in folders if not f.startswith((".", "__MACOSX")))
        for name in sorted(files):
            path = os.path.join(here, name)
            low = name.lower()
            if dp.is_picture(name) and not name.startswith("."):
                pictures.append(path)
            elif low.endswith((".csv", ".tsv")):
                tables.append(path)
            elif low.endswith(".json"):
                jsons.append(path)
    by_stem, by_name = {}, {}
    for path in pictures:
        by_name.setdefault(os.path.basename(path).lower(), path)
        by_stem.setdefault(os.path.splitext(os.path.basename(path))[0].lower(), path)
    rows = {}                                  # {picture path: table row}
    for table in tables:
        for row in read_table(table):
            for value in row.values():
                base = os.path.basename(value.replace("\\", "/")).lower()
                match = by_name.get(base) or by_stem.get(base) or by_stem.get(os.path.splitext(base)[0])
                if match and match not in rows:
                    rows[match] = row
                    break
    captions = {}                              # {picture path: caption from JSON}
    for path in jsons:
        for uri, caption in json_pictures(path).items():
            base = os.path.basename(uri).lower()
            match = by_name.get(base)
            if match:
                captions.setdefault(match, caption)
    records = []
    for path in pictures:
        stem = os.path.splitext(path)[0]
        side = dp.read_file_text(stem + ".txt") or dp.read_file_text(stem + ".caption")
        row = rows.get(path, {})
        rel = os.path.relpath(path, top).replace("\\", "/")
        folder_names = [p for p in rel.split("/")[:-1] if p]
        file_words = re.sub(r"[_+]+", " ", os.path.splitext(os.path.basename(path))[0])
        records.append(dict(
            path=path, rel=rel, folder=" / ".join(folder_names),
            caption=rs.clean(side or first_of(row, CAPTION_COLUMNS) or captions.get(path, "")),
            title=rs.clean(first_of(row, TITLE_COLUMNS) or (folder_names[-1] if folder_names else "")
                           or (file_words if not re.fullmatch(r"[\d\s_-]*|img\s?\d+|dsc\w*|p\d+", file_words, re.I)
                               else "")),
            credit=first_of(row, CREDIT_COLUMNS), skin=first_of(row, SKIN_COLUMNS), age=first_of(row, AGE_COLUMNS),
            row=row, file_words=file_words, stem=os.path.splitext(os.path.basename(path))[0]))
    return records


SOCS_FILE = re.compile(r"^SOCS_(?P<who>[^_]+)_(?P<condition>.+)_(?P<tone>light|medium|dark)$", re.I)


def local_items(entry, records, say):
    """Turn imported records into items for the workspace (left-out records are counted). Returns
    (items, left out, {reason: count})."""
    items, why_left = [], {}
    for record in records:
        title, caption = record["title"], record["caption"]
        tone_value = record["skin"]
        socs = SOCS_FILE.match(record["stem"].strip())
        if socs:                                    # the Skin of Color Society's own file-name format
            if not first_of(record["row"], TITLE_COLUMNS):
                title = socs.group("condition")
            tone_value = tone_value or socs.group("tone")
        texts = [caption, title, record["folder"], record["file_words"]]
        ok, why = adults_and_clinical(*texts)
        try:
            age = int(float(record["age"])) if record["age"] else None
        except ValueError:
            age = None
        if ok and age is not None and age < 18:
            ok, why = False, "gives an age under 18"
        if ok and entry.get("local_filter"):
            ok, why = entry["local_filter"](record)
        if not ok:
            why_left[why] = why_left.get(why, 0) + 1
            continue
        skin, skin_words = skin_from_value(tone_value)
        if not skin_words:
            skin, skin_words = rs.skin_from_text(caption, title)
        if not skin_words and entry.get("skin_words"):
            skin_words = entry["skin_words"]
        extra = []
        if record["row"].get("malignant") or record["row"].get("malignancy(malig=1)"):
            value = (record["row"].get("malignant") or record["row"].get("malignancy(malig=1)")).lower()
            extra.append("The source's records say this was " + ("malignant (a cancer)" if value in ("true", "1")
                                                                   else "benign (not a cancer)") +
                         ", confirmed by a biopsy")
        if age is not None:
            extra.append(f"The source gives the person's age as {age}")
        shown = caption or title or record["file_words"]
        if re.fullmatch(r"[\w'()]+(?:-[\w'()]+)+", shown):      # a label like "melanoma-acral-lentiginous"
            shown = shown.replace("-", " ")
        items.append(dict(
            name=stable_name(entry["key"], record["rel"]), path=record["path"], caption=plain_caption(shown),
            title=title, texts=[record["folder"]], lead=entry["local_lead"], skin=skin, skin_words=skin_words,
            extra=". ".join(extra),
            content=("intimate" if entry["content"] != "" and intimate_text(*texts) else entry["content"]),
            credit_extra=record["credit"], page=f"sent by {entry['organisation']}: {record['rel']}",
            note=("No age given: confirm the person is an adult. " if age is None and entry["content"] else "")
            + (f"Skin tone: {skin_words}." if skin_words else "Skin tone: not stated by the source.")))
    if why_left:
        say(f"{entry['organisation']}: left out of what was sent: "
            + ", ".join(f"{n} ({w})" for w, n in why_left.items()))
    return items, sum(why_left.values()), why_left


def open_source(entry, source, ws, polite, say):
    """The folder to import from: source itself (a folder), a zip unpacked into a hidden folder, or a zip
    downloaded first from an address (resumable). Returns (folder, folder to remove afterwards or None)."""
    source = str(source).strip().strip('"')
    if re.match(r"^https?://", source, re.I):
        name = os.path.basename(urllib.parse.urlsplit(source).path) or f"{entry['key']}.zip"
        if not name.lower().endswith(".zip"):
            name += ".zip"
        say(f"{entry['organisation']}: downloading {name} from the address they gave (it carries on if stopped).")
        source = polite.download_file(source, os.path.join(ws.folder, DOWNLOAD_FOLDER, name))
    if os.path.isdir(source):
        return source, None
    if os.path.isfile(source) and zipfile.is_zipfile(source):
        target = os.path.join(ws.folder, IMPORT_FOLDER, os.path.splitext(os.path.basename(source))[0])
        shutil.rmtree(target, ignore_errors=True)
        os.makedirs(target, exist_ok=True)
        root = os.path.realpath(target)
        with zipfile.ZipFile(source) as z:
            for member in z.infolist():
                if member.is_dir():
                    continue
                out = os.path.realpath(os.path.join(target, member.filename))
                if not out.startswith(root + os.sep):            # a name that tries to leave the folder
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with z.open(member) as src, open(out, "wb") as dst:
                    shutil.copyfileobj(src, dst)
        return target, os.path.join(ws.folder, IMPORT_FOLDER)
    raise NoPermission(f"{source} is not a folder, a zip file or a web address the kit can read. Choose the folder "
                       f"or zip file that {entry['organisation']} sent.")


def import_local(entry, ws, source, cap, polite, say):
    """Import the pictures an organisation sent (a folder, a zip, or a zip's download address) into ws."""
    top, remove = open_source(entry, source, ws, polite, say)
    try:
        records = collect_local(top)
        say(f"{entry['organisation']}: {len(records)} pictures found in what was sent.")
        items, left, _why = local_items(entry, records, say)
        failed = 0
        for item in items:
            if ws.full(cap):
                break
            if ws.done(item["name"]):
                continue
            try:
                with open(item["path"], "rb") as f:
                    data = rs.jpeg(f.read())
            except OSError:
                data = None
            if data is None:
                ws.mark_tried(item["name"])
                failed += 1
                continue
            ws.put(item, data)
        ws.flush()
        return len(records), left + failed
    finally:
        if remove:
            shutil.rmtree(remove, ignore_errors=True)


# ----------------------------------------------------------------- 1. Labia Library (Women's Health Victoria)

LL_GALLERY = "https://www.labialibrary.org.au/labia_gallery/"
LL_IMG = re.compile(r'<img src="(https://www\.labialibrary\.org\.au/wp-content/uploads/[^"]*?Person-(\d+)-labia-'
                    r'(front|below)\.(?:jpe?g|png|webp))" alt="([^"]*)"', re.I)
LL_CREDIT = re.compile(r"Photographs (\d+)\s*(?:–|-|&#8211;)\s*(\d+)(.*?)</p>", re.S)
LL_TONE = re.compile(r"\b(light-medium|medium-light|medium-dark|light|medium|dark) skin tone\b", re.I)


def listing_labia_library(polite, say, ws=None):
    """The Labia Library gallery (one page, 52 people, each seen from the front and from below): each photo's own
    description (its alt text, written by Women's Health Victoria) is the caption; the skin tone it states is
    recorded; the photographer's credit for that person's number is read from the page."""
    page = polite.text(LL_GALLERY)
    credits = []
    for m in LL_CREDIT.finditer(page):
        words = rs.no_tags(m.group(3))
        owner = re.search(r"Photographs (©\s*\d{4}\s*[^.]+)", words)
        who = re.search(r"Photographer:\s*([^.]+)", words)
        credits.append((int(m.group(1)), int(m.group(2)),
                        "; ".join(x for x in ((owner.group(1) if owner else words),
                                              (f"photographer {who.group(1)}" if who else "")) if x)))
    items, seen = [], set()
    for m in LL_IMG.finditer(page):
        url, number, view, alt = m.group(1), int(m.group(2)), m.group(3).lower(), rs.clean(m.group(4))
        if url in seen:
            continue
        seen.add(url)
        view_words = "from the front, standing" if view == "front" else "from below"
        caption = alt or f"Vulva viewed {view_words}"
        tone = LL_TONE.search(alt)
        skin, skin_words = (TONE_GROUP.get(tone.group(1).lower(), rs.GROUPS[3]),
                            f"the source describes the skin tone as {tone.group(1).lower()}") if tone \
            else (rs.GROUPS[3], "")
        who = next((c for a, b, c in credits if a <= number <= b), "")
        items.append(dict(
            name=stable_name("labia_library", f"person-{number:02d}-{view}"), url=url, page=LL_GALLERY,
            caption=caption, title=f"Person {number}, viewed {view_words}",
            lead="A photograph from the Labia Library (Women's Health Victoria), an educational gallery showing the "
                 "natural variety of adult vulvas. Its description says:",
            skin=skin, skin_words=skin_words, content="intimate",
            credit_extra=f"Labia Library gallery, person {number} ({view}); {who}".strip("; "),
            note=f"Labia Library person {number}, view {view}. Photographer credit: {who or 'see the gallery page'}. "
                 "Check that the permission covers this photographer's pictures too (the page credits two "
                 "photographers). No age given: confirm the person is an adult."))
    return [i for i in items if adults_and_clinical(i["caption"])[0]]


# ----------------------------------------------------------------- 2. The Vulva Gallery (Hilde / Sam Hil Atalanta)

VG = "https://www.thevulvagallery.com"
VG_ARTICLE = re.compile(r'(?s)<article class="hentry[^"]*blog-item">(.*?)</article>')
VG_ATTRIBUTION = re.compile(r"[–—-]\s*([^–—<>\n]{1,40}?,\s*\d{1,3} years? old[^()<>\n]{0,60}(?:\([^)]{0,20}\))?)")


def vg_story(polite, url):
    """(story text, attribution such as "K, 25 years old, Switzerland (she/her)") of one personal story page."""
    page = polite.text(url)
    start = page.find('class="blog-item-content')
    body = page[start:page.find("</article>", start)] if start >= 0 else ""
    text = rs.no_tags(re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", body))
    m = VG_ATTRIBUTION.search(text)
    return text, (rs.clean(m.group(1)) if m else "")


def listing_vulva_gallery(polite, say, ws=None, most=None):
    """The Vulva Gallery's website: the "Personal stories" blog (watercolour vulva portraits, each with the story
    the person shared). Pages are followed through their "?offset=" links; each story page gives the story and
    the person's own short description ("K, 25 years old, Switzerland"), which must give an age of 18 or more
    (the adults-only and no-sexual checks read the title and that description). Most of the gallery is on Instagram
    only, so the rest comes from what the artist sends (source=folder or zip)."""
    url, seen_pages, posts = f"{VG}/stories", set(), []
    while url and url not in seen_pages and (most is None or len(posts) < most):
        seen_pages.add(url)
        page = polite.text(url)
        for body in VG_ARTICLE.findall(page):
            href = re.search(r'href="(/stories/\d{4}/[^"]+)"', body)
            image = re.search(r'data-image="([^"]+)"', body) or re.search(r'data-src="([^"]+)"', body)
            title = re.search(r'class="blog-title"[^>]*>\s*(?:<a[^>]*>)?(.*?)</', body, re.S)
            if href and image:
                posts.append((VG + href.group(1), image.group(1), rs.no_tags(title.group(1)) if title else ""))
        nxt = re.search(r'href="(/stories\?offset=\d+)"', page)
        url = VG + nxt.group(1) if nxt else None
    items, left = [], 0
    for page_url, image, title in posts[:most] if most else posts:
        story, who = vg_story(polite, page_url)
        portrait = re.search(r"Portrait\+?(?:%20| )?(?:%23|#)(\d+)", image)
        # The portrait shows the person as they are now, and they give their own age. The story often looks back
        # on childhood or criticises porn, which says nothing about the picture, so the checks read the title and
        # the person's own description; the stated age must be 18 or more (no age: left out).
        ok, why = adults_and_clinical(title, who)
        adult, age = rs.adult_shown(who)
        if not ok or not adult or (age is not None and age < 18):
            left += 1
            continue
        skin, skin_words = rs.skin_from_text(story)
        items.append(dict(
            name=stable_name("vulva_gallery", page_url.rsplit("/", 1)[-1]),
            url=image.split("?")[0] + "?format=1500w", page=page_url,
            caption="A watercolour portrait of an adult's vulva, painted from a photo shared with consent"
                    + (f" (The Vulva Gallery portrait number {portrait.group(1)})" if portrait else "")
                    + f". It goes with the personal story titled {title.strip(chr(34) + '“” ')}",
            title=title, texts=[story], extra=f"The person describes themself as: {who}",
            lead="An illustration from The Vulva Gallery, an educational gallery of vulva portraits by the artist Sam "
                 "Hil Atalanta (formerly Hilde Atalanta):",
            skin=skin, skin_words=skin_words, content="intimate", credit_extra="illustration by Sam Hil Atalanta",
            note="An illustration, not a photograph. The person's age is in their own words in the story."))
    if left:
        say(f"The Vulva Gallery: {left} stories left out by the adults-only and no-sexual-content rules.")
    return items


def vg_filter(record):
    """Pictures the artist sent: kept unless the caption is missing a vulva portrait's usual words (a shop or
    announcement post); review checks the rest."""
    text = " ".join([record["caption"], record["title"], record["file_words"]]).lower()
    if re.search(r"\b(sale|discount|shop|giveaway|webshop|pre-?order|newsletter|book launch)\b", text):
        return False, "a shop or announcement post"
    return True, ""


# ----------------------------------------------------------------- 3. Know Your Lemons Foundation

KYL = "https://www.knowyourlemons.org"
KYL_PAGES = ("/symptoms-of-breast-cancer", "/symptoms-hard-lump", "/symptoms-dimple", "/how-to-self-exam")
KYL_SKIP = re.compile(r"logo|badge|abcglobal|bbb|candid|uicc|UNDG|shopitems|banner|tedx|headshot|couch|sofa|"
                      r"our_app|app[-_]|linkedin|award|DetectionPath", re.I)
KYL_SIGN = re.compile(r"lump|dimple|crust|nipple|fluid|sore|bump|vein|shape|peel|rash|thick|signs|self ?exam|"
                      r"anatomy|lumptypes|look and feel|breast", re.I)


def listing_know_your_lemons(polite, say, ws=None):
    """Know Your Lemons' sign pictures (lemon illustrations of the 12 signs of breast cancer, self-exam and anatomy
    pictures) from its symptom and self-exam pages (and any other /symptoms-... page they link to). The caption is
    the nearest heading and paragraph above the picture on the page, and the file name."""
    pages, done, items, seen = list(KYL_PAGES), set(), [], set()
    while pages:
        path = pages.pop(0)
        if path in done:
            continue
        done.add(path)
        page = polite.text(KYL + path)
        for link in re.findall(r'href="(/symptoms-[a-z0-9-]+)"', page):
            if link not in done:
                pages.append(link)
        for m in re.finditer(r"<img\b[^>]*>", page):
            tag = m.group(0)
            src = re.search(r'data-src="([^"]+)"', tag) or re.search(r'\bsrc="([^"]+)"', tag)
            if not src or "squarespace-cdn" not in src.group(1):
                continue
            url = src.group(1).split("?")[0]
            file_words = urllib.parse.unquote_plus(url.rstrip("/").rsplit("/", 1)[-1]).rsplit(".", 1)[0]
            if url in seen or KYL_SKIP.search(url):
                continue
            before = page[max(0, m.start() - 6000):m.start()]
            heads = re.findall(r"(?s)<h[1-4][^>]*>(.*?)</h[1-4]>", before)
            heading = rs.no_tags(heads[-1]) if heads else ""
            paras = re.findall(r"(?s)<p[^>]*>(.*?)</p>", page[m.end():m.end() + 4000])
            words = " ".join(rs.no_tags(p) for p in paras[:2])
            if not KYL_SIGN.search(file_words + " " + heading):
                continue
            seen.add(url)
            alt = re.search(r'alt="([^"]*)"', tag)
            caption = rs.clean(alt.group(1)) if alt and alt.group(1) else ""
            topic = rs.clean(re.sub(r"(?i)know your lemons|copyrighted|generic|\d{3,4}x\d{3,4}|website|\(\d+\)", " ",
                                    re.sub(r"[_+-]+", " ", file_words)))
            items.append(dict(
                name=stable_name("know_your_lemons", "/".join(url.rstrip("/").split("/")[-2:])),
                url=url + "?format=1500w", page=KYL + path,
                caption=caption or f"Know Your Lemons picture: {topic}" + (f". Page heading: {heading}" if heading
                                                                             else ""),
                title=heading or topic, texts=[words],
                extra=rs.first_sentences(words, 40, 2) if words else "",
                lead="An illustration from Know Your Lemons, a breast-health charity that shows the signs of breast "
                     "cancer as lemons:",
                content="intimate", note="An illustration (Know Your Lemons draws the signs as lemons)."))
    return items


# ----------------------------------------------------------------- 4. DermNet (dermnetnz.org)

DERMNET = "https://dermnetnz.org"
DERMNET_LISTING = DERMNET + "/assets/___cache/images.json"
DERMNET_META_TAGS = {"histopathology-image", "histopathology slide", "non-clinical-image", "possible-duplicate",
                     "duplicate", "immunohistochemistry stain", "sensitive-image", "sensitive image"}
DERMNET_NOT_CLINICAL = re.compile(r"\b(histopatholog\w*|histolog\w*|patholog\w*|micrograph\w*|microscop\w*|"
                                  r"stain\w*|diagram\w*|illustration\w*|virus|bacteria|culture)\b", re.I)
DERMNET_SKIP_TAGS = re.compile(r"^(dermnet_|location_|key:|histopatholog|histolog|male\.|female\.)", re.I)
ETHNICITY_TAG = re.compile(r"^([A-Za-z /-]+?) (?:ethnicity|skin)$", re.I)


def dermnet_age(meta):
    """The patient's age from DermNet's camera notes ("patient_age=60"), or None."""
    m = re.search(r"patient_age=(\d{1,3})", meta or "")
    return int(m.group(1)) if m else None


def dermnet_tags(record):
    """DermNet's own tags for a picture (its "c" field), without the housekeeping ones."""
    return [t.strip() for t in (record.get("c") or "").split(",") if t.strip()]


def dermnet_keep(record):
    """(True, "") when a DermNet listing record may be used; otherwise (False, why)."""
    title, caption, tags = rs.clean(record.get("a")), rs.clean(record.get("b")), dermnet_tags(record)
    low_tags = {t.lower() for t in tags}
    if not record.get("q", True) or not record.get("l"):
        return False, "not shown on the site"
    if low_tags & (DERMNET_META_TAGS - {"sensitive-image", "sensitive image"}) or DERMNET_NOT_CLINICAL.search(title):
        return False, "not a clinical photograph (slide, diagram, duplicate)"
    age = dermnet_age(record.get("d"))
    if age is not None and age < 18:
        return False, "a child (age under 18)"
    ok, why = adults_and_clinical(title, caption, ", ".join(tags), record.get("l"), record.get("m"))
    return ok, why


def dermnet_skin(tags):
    """(group, words, ordering group) from DermNet's tags: a stated Fitzpatrick or skin type, an ethnicity tag, or
    "Skin of colour" (recorded as words, group "not stated", but ordered early so skin of colour is not crowded
    out)."""
    text = ", ".join(tags)
    group, words = rs.skin_from_text(text)
    if words and group != rs.GROUPS[3]:
        return group, words, group
    for tag in tags:
        m = ETHNICITY_TAG.match(tag)
        if m and m.group(1).lower() not in ("skin of", "dark", "fair", "normal"):
            return rs.GROUPS[3], f"the source tags the person's ethnicity as {m.group(1)}", "skin of colour"
    if any(t.lower() == "skin of colour" for t in tags):
        return rs.GROUPS[3], "the source tags this picture 'skin of colour'", "skin of colour"
    return rs.GROUPS[3], "", rs.GROUPS[3]


def listing_dermnet(polite, say, ws=None):
    """DermNet's whole image library from its own listing file (one request: /assets/___cache/images.json, which
    the site's image search uses): title (the topic), caption or body site, tags, copyright holder and the
    watermarked picture's address. Paediatric, infant, neonatal, congenital and adolescent topics are left out;
    histology slides, diagrams and duplicates too. Genital and breast pictures (DermNet's own "sensitive" mark, or
    genital or breast words) are tagged "intimate" one by one. Ordered in turns across skin-type groups (skin of
    colour early) and topics."""
    data = read_cache(ws) if ws else None
    if data is None:
        data = polite.json(DERMNET_LISTING) or []
        if ws and data:
            write_cache(ws, data)
    say(f"DermNet: {len(data)} pictures in its listing.")
    kept, why_left = [], {}
    for record in data:
        ok, why = dermnet_keep(record)
        if not ok:
            why_left[why] = why_left.get(why, 0) + 1
            continue
        kept.append(record)
    say("DermNet left out before download: " + ", ".join(f"{n} ({w})" for w, n in why_left.items()))
    order = rs.balanced(kept, lambda r: dermnet_skin(dermnet_tags(r))[2], lambda r: rs.clean(r.get("a")).lower())
    items = []
    for record in order:
        title, caption, tags = rs.clean(record.get("a")), rs.clean(record.get("b")), dermnet_tags(record)
        skin, skin_words, _order = dermnet_skin(tags)
        shown_tags = [t for t in tags if t.lower() not in DERMNET_META_TAGS and not DERMNET_SKIP_TAGS.search(t)
                      and t.lower() != title.lower()][:8]
        intimate = bool(record.get("e")) or any(t.lower().startswith("sensitive") for t in tags) \
            or intimate_text(title, caption, ", ".join(tags))
        dermoscopy = bool(re.search(r"dermoscop|dermatoscop", f"{title} {', '.join(tags)}", re.I))
        if caption and caption.lower() != title.lower() and not re.fullmatch(r"figure \d+\w?", caption, re.I):
            text = f"{title}. {caption}"
        else:
            text = title
        age = dermnet_age(record.get("d"))
        holder = rs.clean(record.get("f")) or "© DermNet"
        items.append(dict(
            name=stable_name("dermnet", str(record.get("o"))), url=DERMNET + record["l"],
            page=DERMNET + (record.get("m") or ""), caption=text, title=title, texts=[", ".join(tags)],
            lead=("A dermoscopy picture (a magnified close-up taken through a skin lens) from DermNet, titled:"
                  if dermoscopy else "A clinical photograph from DermNet, titled:"),
            extra=("DermNet's tags: " + ", ".join(shown_tags)) if shown_tags else "",
            skin=skin, skin_words=skin_words, content="intimate" if intimate else "medical",
            credit_extra=f"{holder}, DermNet image {record.get('o')}",
            note=(f"Age given by the source: {age}. " if age else "No age given: confirm the person is an adult. ")
            + ("INTIMATE: a genital or breast picture. " if intimate else "")
            + f"Skin tone: {skin_words or 'not stated by the source'}."))
    return items


# ----------------------------------------------------------------- 5. Mind the Gap / Black & Brown Skin

BBS = "https://www.blackandbrownskin.co.uk"
BBS_PAGES = ("/headandneck", "/chest", "/abdomen", "/upper-limb", "/lower-limb", "/mindthegap")
BBS_SKIN = "the source (Black & Brown Skin) shows conditions on Black and brown skin"


def listing_mind_the_gap(polite, say, ws=None):
    """Black & Brown Skin (Malone Mukwende's Mind the Gap project): its condition pages by body region are
    Squarespace product lists whose data (title, description, tags and picture addresses) is in the page itself;
    every picture of every condition is taken. Conditions of babies (neonatal rash, witch's milk) are left out by
    the adults-only rule. The Mind the Gap handbook's own pictures come from what the authors send (source)."""
    items, left = [], 0
    for path in BBS_PAGES:
        page = polite.text(BBS + path)
        m = re.search(r'data-controller="ProductList"\s+data-context="([^"]*)"', page)
        if not m:
            continue
        try:
            data = json.loads(html.unescape(m.group(1)))
        except ValueError:
            continue
        region = data.get("collectionTitle") or path.strip("/")
        for product in data.get("items", []):
            title = rs.clean(product.get("title"))
            words = rs.no_tags(product.get("description"))
            tags = ", ".join(product.get("tags") or [])
            ok, _why = adults_and_clinical(title, words, tags, product.get("fullUrl"))
            if not ok:
                left += 1
                continue
            for number, image in enumerate(product.get("images") or [], 1):
                url = image.get("assetUrl")
                if not url:
                    continue
                file_words = urllib.parse.unquote_plus(url.rsplit("/", 1)[-1]).rsplit(".", 1)[0]
                skin, skin_words = rs.skin_from_text(words)
                if skin == rs.GROUPS[3]:                  # general text about the condition, not this person
                    skin_words = ""
                items.append(dict(
                    name=stable_name("mind_the_gap", f"{product.get('id')}-{number}"),
                    url=url + "?format=1500w", page=BBS + (product.get("fullUrl") or path), caption=title,
                    title=title, texts=[words, tags],
                    extra=(f"Body region on the site: {region}. " + rs.first_sentences(words, 45, 2)).strip(),
                    lead="A clinical photograph from Black & Brown Skin (Mind the Gap), which shows how conditions "
                         "look on Black and brown skin. Its title says:",
                    skin=skin, skin_words=skin_words or BBS_SKIN,
                    content="intimate" if intimate_text(title, words, tags) else "medical",
                    note=f"Region: {region}. Picture file '{file_words}'. No age given: confirm the person is an "
                         "adult."))
    if left:
        say(f"Black & Brown Skin: {left} conditions left out by the adults-only rule (babies and children).")
    return items


# ----------------------------------------------------------------- 6. Skin of Color Society

SOCS = "https://skinofcolorsociety.org"
SOCS_EDUCATION = SOCS + "/discover-patients-public/public-education"
SOCS_ADDON = re.compile(r'(?s)<div class="sppb-addon-title">([^<]+)</div>.*?<a href="([^"]+)"[^>]*>\s*'
                        r'<img[^>]*src="([^"]+)"')


def listing_skin_of_color_society(polite, say, ws=None):
    """The Skin of Color Society's public-education page: a few condition pictures, each linked to its topic page
    (whose first sentences are the caption). SOCS has no public picture atlas (its clinical image collection is
    the American Academy of Dermatology's, for members), so the main route is what SOCS sends (source), whose
    file names follow SOCS's own format "SOCS_Name_Condition_SkinTone" (light, medium or dark)."""
    page = polite.text(SOCS_EDUCATION)
    items = []
    for title, link, src in SOCS_ADDON.findall(page):
        title = rs.clean(title)
        topic_url = urllib.parse.urljoin(SOCS, link)
        ok, _why = adults_and_clinical(title, link, src)
        if not ok:
            continue
        topic = polite.text(topic_url)
        start = topic.find("<main")
        words = rs.first_sentences(rs.no_tags(re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ",
                                                     topic[start:] if start >= 0 else "")), 60, 3)
        words = re.sub(r"^.{0,120}?\b(?:MD|DO|PhD|FAAD)\b,?\s+", "", words, count=1)   # title and author first
        ok, _why = adults_and_clinical(words)
        if not ok:
            continue
        skin, skin_words = rs.GROUPS[3], ""               # the topic text is general, not about this person
        items.append(dict(
            name=stable_name("skin_of_color_society", src), url=urllib.parse.urljoin(SOCS, src), page=topic_url,
            caption=title, title=title, texts=[words], extra=rs.first_sentences(words, 40, 2),
            lead="A picture from the Skin of Color Society's public education page, showing:",
            skin=skin, skin_words=skin_words, content="medical",
            note="No age given: confirm the person is an adult."))
    return items


# ----------------------------------------------------------------- 7. Brown Skin Matters

def listing_brown_skin_matters(polite, say, ws=None):
    """Brown Skin Matters is published on Instagram (@brownskinmatters). Its old website address
    (brownskinmatters.com) was found in November 2026 to belong to someone else (a gambling site re-showing old
    copies), so nothing is read from it: the pictures must come from what Brown Skin Matters sends (source)."""
    raise NoPermission("Brown Skin Matters publishes its pictures on Instagram, and its old website address now "
                       "belongs to someone else, so the kit does not download from it. When they send you their "
                       "pictures (a folder, a zip, or their Instagram data download), choose that folder or zip "
                       "as the source and try again.")


# ----------------------------------------------------------------- 8. Breastcancer.org

BCO = "https://www.breastcancer.org"
BCO_PAGES = ("/surgical-images", "/types/inflammatory", "/types/paget-disease", "/signs-symptoms",
             "/signs-symptoms/inverted-nipples", "/screening-testing/breast-self-exam-bse/breast-lumps",
             "/treatment/surgery/going-flat-no-reconstruction/aesthetic-flat-closure",
             "/treatment/surgery/breast-reconstruction/types/nipple-tattoos",
             "/treatment/surgery/breast-reconstruction/women-of-color")
BCO_SKIP_KEYS = {"signUpBanner", "editorData", "sponsors", "author", "authors", "reviewers", "seo",
                 "fullWidthFeaturedImage", "featuredImage", "relatedContent", "community", "headerImage"}
BCO_SKIP_WORDS = re.compile(r"headshot|logo|banner|homepage|icon|portrait|avatar|sponsor|donat|webinar|podcast|"
                            r"BCSignsandSymptoms|_\d{3,4}x\d{3,4}", re.I)


def rich_text(node):
    """The plain text of a Contentful rich-text document (the "value" of its text nodes)."""
    out = []

    def walk(n):
        """Collect text values."""
        if isinstance(n, dict):
            if n.get("nodeType") == "text" and isinstance(n.get("value"), str):
                out.append(n["value"])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(node)
    return rs.clean(" ".join(out))


def bco_pictures(data):
    """[(picture address, title, caption, source, extra)] from a Breastcancer.org page's __NEXT_DATA__: gallery
    images ({"image": {"src", "alt"}, "title", "caption", "source"}) and pictures placed in articles (Contentful
    assets with "url", "title", "description"), leaving out banners, headshots, logos and featured stock pictures."""
    found = []

    def walk(node, context=None):
        """Look for pictures, remembering the nearest carousel's surgery types."""
        if isinstance(node, dict):
            if node.get("surgeryTypes"):
                context = ", ".join(node["surgeryTypes"])
            image = node.get("image")
            if isinstance(image, dict) and isinstance(image.get("src"), str) and "ctfassets" in image["src"]:
                found.append((image["src"], rs.clean(node.get("title") or image.get("alt")),
                              rich_text(node.get("caption")), rs.clean(node.get("source")), context or ""))
            elif node.get("__typename") == "Asset" and isinstance(node.get("url"), str) \
                    and re.search(r"\.(jpe?g|png|webp)$", node["url"], re.I):
                found.append((node["url"], rs.clean(node.get("title")), rs.clean(node.get("description")), "", ""))
            for key, value in node.items():
                if key not in BCO_SKIP_KEYS and key != "image":
                    walk(value, context)
        elif isinstance(node, list):
            for value in node:
                walk(value, context)
    walk(data)
    out, seen = [], set()
    for url, title, caption, source, extra in found:
        if url in seen or BCO_SKIP_WORDS.search(url + " " + title):
            continue
        seen.add(url)
        out.append((url, title, caption, source, extra))
    return out


def listing_breastcancer_org(polite, say, ws=None):
    """Breastcancer.org: its surgical image gallery (reconstruction, implants, flat closure, corrective surgery,
    with each picture's history and before-and-after caption) and the pictures in its articles about breast
    changes. Every page's data is in its own __NEXT_DATA__ block."""
    items = []
    for path in BCO_PAGES:
        page = polite.text(BCO + path)
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
        if not m:
            continue
        try:
            data = json.loads(m.group(1)).get("props", {}).get("pageProps", {})
        except ValueError:
            continue
        for url, title, caption, source, extra in bco_pictures(data):
            ok, _why = adults_and_clinical(title, caption, url)
            if not ok:
                continue
            title = re.sub(r"\s*(CRBS)?\s*watermark$", "", title, flags=re.I)
            skin, skin_words = rs.skin_from_text(caption, title)
            items.append(dict(
                name=stable_name("breastcancer_org", url.split("/")[-3] if url.count("/") > 4 else url),
                url=url, page=BCO + path, caption=caption or title, title=title,
                lead=f"A photograph from Breastcancer.org titled {title.rstrip('.')}. Its caption says:"
                if caption else "A picture from Breastcancer.org, titled:",
                extra=(f"Surgery types: {extra}" if extra else ""), skin=skin, skin_words=skin_words,
                content="intimate", credit_extra=(f"photograph: {source}" if source else ""),
                note=("Before-and-after pictures may show two views side by side. " if "before" in caption.lower()
                      else "") + (f"The photograph belongs to {source}: check the permission covers it. "
                                  if source else "") + "No age given: confirm the person is an adult."))
    return items


# ----------------------------------------------------------------- 9. Geograph Britain and Ireland

GEOGRAPH_API = "https://api.geograph.org.uk/syndicator.php"
GEOGRAPH_TOPICS = ("church", "bridge", "farm", "beach", "harbour", "railway station", "canal", "castle",
                   "woodland", "village", "high street", "market", "lighthouse", "waterfall", "moorland", "lake",
                   "river", "cottage", "pub", "factory", "bus station", "cathedral", "garden", "park", "cliff",
                   "motorway", "footpath", "allotment", "windmill", "ruin")


def geograph_key(library):
    """Geograph's API key: the GEOGRAPH_API_KEY environment variable, or Permissions\\geograph\\api-key.txt."""
    if os.environ.get("GEOGRAPH_API_KEY"):
        return os.environ["GEOGRAPH_API_KEY"].strip()
    return (dp.read_file_text(os.path.join(permission_folder(library, "geograph"), KEY_FILE)) or "").strip()


def geograph_full_size(thumb):
    """The 640-pixel picture address from a Geograph thumbnail address (..._120x120.jpg gives ....jpg)."""
    return re.sub(r"_\d+x\d+(\.jpe?g)$", r"\1", thumb or "", flags=re.I)


def geograph_items(answer, topic):
    """Items from one syndicator.php JSON answer ({"items": [{"title", "description", "author", "link" or "guid",
    "thumb", "licence", ...}]}); records naming a child or anything sexual are left out."""
    items = []
    for record in (answer or {}).get("items", []) or []:
        title = rs.clean(record.get("title"))
        words = rs.no_tags(record.get("description"))
        link = record.get("link") or record.get("guid") or ""
        photo = re.search(r"/photo/(\d+)", link)
        url = geograph_full_size(record.get("thumb") or record.get("thumbnail") or "")
        if not photo or not url:
            continue
        ok, _why = adults_and_clinical(title, words)
        if not ok:
            continue
        author = rs.clean(record.get("author") or record.get("realname") or record.get("dc:creator"))
        taken = rs.clean(record.get("imageTaken") or record.get("taken"))
        items.append(dict(
            name=stable_name("geograph", photo.group(1)), url=url, page=f"https://www.geograph.org.uk/photo/"
                                                                         f"{photo.group(1)}",
            caption=f"{title}. {rs.first_sentences(words, 50, 3)}" if words else title, title=title,
            lead="A photograph from Geograph Britain and Ireland, titled:",
            extra=(f"Taken {taken}" if taken else ""), content="",
            credit_extra=f"© {author or 'the photographer'}, CC BY-SA 2.0, Geograph photo {photo.group(1)}",
            note=f"Found by the topic '{topic}'. Licence CC BY-SA 2.0: credit the photographer; anything shared "
                 f"that is made from it must be CC BY-SA too."))
    return items


def listing_geograph(polite, say, ws=None, library=None, most=None):
    """Geograph through its official API (syndicator.php, JSON, 100 per page, at most 1,000 per search, one
    request every 2 seconds) with the key Geograph gave (geograph_key). Geograph asks that bulk and training use
    comes from its datasets instead, so the better route is the dataset it sends (source: a folder, a zip or the
    download address, with its metadata.csv)."""
    key = geograph_key(library) if library else os.environ.get("GEOGRAPH_API_KEY", "")
    if not key:
        raise NoPermission("Geograph needs an API key for its API, or the dataset they send you. Put the key alone in "
                           f"a file called {KEY_FILE} in the geograph permissions folder, or choose the folder or "
                           "zip of their dataset as the source, and try again.")
    items = []
    for topic in GEOGRAPH_TOPICS:
        for page in range(1, 11):
            url = (f"{GEOGRAPH_API}?key={urllib.parse.quote(key)}&format=JSON&perpage=100&page={page}"
                   f"&text={urllib.parse.quote(topic)}")
            found = geograph_items(polite.json(url), topic)
            items += found
            if len(found) < 50 or (most and len(items) >= most):
                break
        if most and len(items) >= most:
            break
    return items


# ----------------------------------------------------------------- 10. Stanford Diverse Dermatology Images

def listing_ddi(polite, say, ws=None):
    """DDI is not on a public page: after Stanford approves the research agreement, the owner gets a download
    link (the Stanford AIMI portal). The fetch takes that zip (a file) or its address as the source."""
    raise NoPermission("The Stanford Diverse Dermatology Images come as a download after Stanford approves your "
                       "research agreement. Choose the zip file they let you download (or paste its download "
                       "address) as the source, and try again.")


# ----------------------------------------------------------------- the collections

def make_fetch(key):
    """A fetch function fetch(folder, cap, say=print, source=None, library=None) for the collection key."""

    def fetch(folder, cap, say=print, source=None, library=None):
        """Download (or import) this permission-gated collection into the review workspace in folder; refuses
        (NoPermission) when no permission is on file. Returns a plain summary."""
        entry = source_by_key(key)
        library = check_permission(entry, folder, library, say)
        if not source and entry["needs_source"]:
            entry["listing"](None, say)                   # raises NoPermission with the plain reason
        if not source and key == "geograph" and not geograph_key(library):
            listing_geograph(None, say, library=library)  # raises NoPermission: no key
        ws = PermissionWorkspace(folder, entry, library, say)
        polite = Polite(say)
        if source:
            found, left = import_local(entry, ws, source, cap, polite, say)
            return ws.finish(found, left)
        if key == "geograph":
            items = listing_geograph(polite, say, ws, library=library, most=cap * 2 if cap else None)
        else:
            items = entry["listing"](polite, say, ws)
        say(f"{entry['organisation']}: {len(items)} pictures found on the site.")
        left = fill_web(ws, items, cap, polite)
        if polite.refused:
            say(f"{entry['organisation']}: {polite.refused} addresses skipped because robots.txt does not allow "
                f"them.")
        return ws.finish(len(items), left)
    fetch.__name__ = f"fetch_{key}"
    return fetch


PERMISSION = "used with permission (all rights reserved by the owner)"
PERMISSION_SOURCES = [
    dict(key="labia_library", organisation="Women's Health Victoria (Labia Library)",
         name="Labia Library photographs of adult vulvas (permission, review only)",
         contact="labialibrary@whv.org.au (phone +61 3 9664 9300; https://www.labialibrary.org.au/contact-us/)",
         letter="01 Labia Library - Women's Health Victoria.docx",
         terms="https://www.labialibrary.org.au/labia_gallery/",
         licence="All rights reserved: photographs 1 to 28 (c) 2024 Breeana Dunbar; 29 to 52 (c) 2011 Show Off Books "
                 "('I'll Show You Mine', photographer Katie Huisman), reproduced on the site with permission",
         terms_summary=PERMISSION + "; the permission must cover both photographers' pictures",
         credit="Labia Library, Women's Health Victoria (labialibrary.org.au), used with permission",
         content="intimate", cap=104, download="about 15 MB (104 photographs)",
         how="Website: the gallery page (one page, 52 people seen from the front and from below), each photo's own "
             "description as the caption and its stated skin tone; or a folder or zip they send.",
         listing=listing_labia_library, needs_source=False,
         local_lead="A photograph from the Labia Library (Women's Health Victoria), sent with permission. Its "
                    "caption says:"),
    dict(key="vulva_gallery", organisation="The Vulva Gallery (Sam Hil Atalanta, formerly Hilde Atalanta)",
         name="The Vulva Gallery illustrations (permission, review only)",
         contact="hello@thevulvagallery.com (https://www.thevulvagallery.com/contact; Instagram @the.vulva.gallery)",
         letter="02 The Vulva Gallery - Hilde Atalanta.docx", terms="https://www.thevulvagallery.com/stories",
         licence="All rights reserved by the artist (illustrations sold as prints and in a book)",
         terms_summary=PERMISSION, credit="The Vulva Gallery, illustrations by Sam Hil Atalanta, used with permission",
         content="intimate", cap=600, download="about 20 MB from the website; more from what the artist sends",
         how="Website: the 'Personal stories' blog (about 30 portraits, each with its story) read page by page; "
             "the main gallery is on Instagram only, so the rest is imported from the folder, zip or Instagram "
             "data download the artist sends.",
         listing=listing_vulva_gallery, needs_source=False, local_filter=vg_filter,
         local_lead="An illustration from The Vulva Gallery by Sam Hil Atalanta, sent with permission. Its caption "
                    "says:"),
    dict(key="know_your_lemons", organisation="Know Your Lemons Foundation",
         name="Know Your Lemons breast-cancer sign pictures (permission, review only)",
         contact="hello@knowyourlemons.org (https://www.knowyourlemons.org/contact; image-use policy at "
                 "https://www.knowyourlemons.org/image-use)",
         letter="03 Know Your Lemons Foundation.docx", terms="https://www.knowyourlemons.org/image-use",
         licence="All rights reserved, with its own Image Use Policy (no changes, no commercial use without a "
                 "partnership)", terms_summary=PERMISSION,
         credit="Know Your Lemons Foundation (knowyourlemons.org), used with permission", content="intimate", cap=60,
         download="about 10 MB",
         how="Website: the symptom and self-exam pages (a dozen or so illustrations; captions from the heading and "
             "paragraph next to each picture); the full sign set (the app's and the press kit's pictures) from what "
             "the charity sends.",
         listing=listing_know_your_lemons, needs_source=False,
         local_lead="An illustration from Know Your Lemons, sent with permission. Its caption says:"),
    dict(key="dermnet", organisation="DermNet (DermNet New Zealand Trust)",
         name="DermNet clinical skin pictures, all topics (permission, review only)",
         contact="the image application form, https://dermnetnz.org/image-application-form (licence terms "
                 "https://dermnetnz.org/image-licence; general contact form https://dermnetnz.org/contact-us)",
         letter="04 DermNet - image licence.docx", terms="https://dermnetnz.org/image-licence",
         licence="Watermarked images CC BY-NC-ND 4.0 (no derivatives: training copies are derivatives); clean "
                 "images by paid licence", terms_summary=PERMISSION + "; keep the watermark unless DermNet agrees "
                                                                      "otherwise",
         credit="DermNet (dermnetnz.org), used with permission", content="medical", cap=6000,
         download="about 1 GB for 21,000 pictures (about 50 KB each)",
         how="Website: DermNet's own listing file of its whole image library (one request), then each watermarked "
             "picture; titles, captions and tags give the draft; genital and breast pictures tagged intimate; "
             "paediatric topics left out. Or the clean pictures DermNet sends.",
         listing=listing_dermnet, needs_source=False,
         local_lead="A clinical photograph from DermNet, sent with permission. Its caption says:"),
    dict(key="mind_the_gap", organisation="Black & Brown Skin / Mind the Gap (Malone Mukwende)",
         name="Black & Brown Skin and Mind the Gap pictures (permission, review only)",
         contact="info@blackandbrownskin.co.uk (https://www.blackandbrownskin.co.uk/contact)",
         letter="05 Mind the Gap - Malone Mukwende.docx", terms="https://www.blackandbrownskin.co.uk/",
         licence="All rights reserved (the website's pictures, many contributed; the Mind the Gap handbook is a "
                 "copyrighted book)", terms_summary=PERMISSION,
         credit="Black & Brown Skin (blackandbrownskin.co.uk) and Mind the Gap (Mukwende, Tamony and Turner), used "
                "with permission", content="medical", cap=1000, download="about 50 MB",
         how="Website: the condition pages by body region (Head and Neck, Chest, Abdomen, Upper and Lower Limb), "
             "whose data is in each page; the Mind the Gap handbook's pictures from what the authors send.",
         listing=listing_mind_the_gap, needs_source=False, skin_words=BBS_SKIN,
         local_lead="A clinical photograph from Mind the Gap (Black & Brown Skin), sent with permission. Its caption "
                    "says:"),
    dict(key="skin_of_color_society", organisation="Skin of Color Society",
         name="Skin of Color Society pictures (permission, review only)",
         contact="info@skinofcolorsociety.org (https://skinofcolorsociety.org/contact)",
         letter="06 Skin of Color Society.docx", terms="https://skinofcolorsociety.org/who-is-socs/copyright-policy",
         licence="(c) Skin of Color Society, all rights reserved; members' pictures stay the members' copyright",
         terms_summary=PERMISSION, credit="Skin of Color Society (skinofcolorsociety.org), used with permission",
         content="medical", cap=1000, download="small from the website; more from what SOCS sends",
         how="Website: only the few pictures on its public-education page (no public atlas exists); the main route "
             "is a folder or zip SOCS sends, whose file names 'SOCS_Name_Condition_SkinTone' give the condition and "
             "the stated skin tone.",
         listing=listing_skin_of_color_society, needs_source=False,
         local_lead="A clinical photograph from the Skin of Color Society, sent with permission, showing:"),
    dict(key="brown_skin_matters", organisation="Brown Skin Matters",
         name="Brown Skin Matters pictures (permission, review only)",
         contact="Instagram @brownskinmatters (https://www.instagram.com/brownskinmatters/); the email on its old "
                 "site was brownskinmatters@gmail.com (confirm it on Instagram first: the old website address now "
                 "belongs to someone else)",
         letter="07 Brown Skin Matters.docx", terms="https://www.instagram.com/brownskinmatters/",
         licence="All rights reserved; pictures contributed by the public", terms_summary=PERMISSION,
         credit="Brown Skin Matters (@brownskinmatters), used with permission", content="medical", cap=1000,
         download="what they send",
         how="Folder import only: the pictures they send (a folder, a zip or an Instagram data download with "
             "captions). The old website is not read (it was taken over by a gambling site).",
         listing=listing_brown_skin_matters, needs_source=True,
         local_lead="A photograph from Brown Skin Matters, which shows skin conditions on brown skin, sent with "
                    "permission. Its caption says:",
         skin_words="the source (Brown Skin Matters) shows conditions on brown skin"),
    dict(key="breastcancer_org", organisation="Breastcancer.org",
         name="Breastcancer.org breast-change and after-surgery pictures (permission, review only)",
         contact="https://www.breastcancer.org/contact (contact form)", letter="08 Breastcancer.org.docx",
         terms="https://www.breastcancer.org/terms-of-use",
         licence="(c) Breastcancer.org, all rights reserved; surgical photographs belong to the surgeons who gave "
                 "them (for example the Center for Restorative Breast Surgery)", terms_summary=PERMISSION,
         credit="Breastcancer.org, used with permission", content="intimate", cap=200, download="about 20 MB",
         how="Website: the surgical image gallery (reconstruction, implants, flat closure, corrective surgery, each "
             "with its history and before-and-after caption) and pictures in its articles about breast changes, "
             "read from each page's own data block.",
         listing=listing_breastcancer_org, needs_source=False,
         local_lead="A photograph from Breastcancer.org, sent with permission. Its caption says:"),
    dict(key="geograph", organisation="Geograph Britain and Ireland (Geograph Project)",
         name="Geograph photographs of Britain and Ireland (permission for bulk use, review only)",
         contact="https://www.geograph.org.uk/contact.php (API keys: https://www.geograph.org.uk/get-api-key.php; "
                 "datasets: https://data.geograph.org.uk/datasets.html)",
         letter="09 Geograph Project - bulk images.docx", terms="https://www.geograph.org.uk/help/api",
         licence="CC BY-SA 2.0 (each photographer credited); Geograph's terms ask that bulk and training use comes "
                 "from its datasets, with its agreement",
         terms_summary="share-alike: credit each photographer; anything shared that is made from them must be CC BY-SA",
         credit="Geograph Britain and Ireland photographers, CC BY-SA 2.0, used with the Geograph Project's agreement",
         content="", group="share-alike", cap=5000, download="about 1 GB per 10,000 pictures (640 pixels)",
         how="The dataset Geograph sends (a folder, zip or download address, with metadata.csv for titles and "
             "photographers), or its official API (syndicator.php, JSON) with the key Geograph gives (in "
             "Permissions\\geograph\\api-key.txt). The website itself is never scraped (Geograph forbids it).",
         listing=None, needs_source=False,
         local_lead="A photograph from Geograph Britain and Ireland, titled:"),
    dict(key="ddi", organisation="Stanford Diverse Dermatology Images (Stanford University School of Medicine)",
         name="Stanford Diverse Dermatology Images (research agreement, review only)",
         contact="roxanad@stanford.edu (Dr Roxana Daneshjou; the agreement and download are on the Stanford AIMI "
                 "portal, https://stanfordaimi.azurewebsites.net/datasets/35866158-8196-48d8-87bf-50dca81df965)",
         letter="10 Stanford Diverse Dermatology Images.docx", terms="https://ddi-dataset.github.io/#access",
         licence="Stanford Research Use Agreement: personal, non-commercial research only; no sharing or "
                 "reproducing; no derivative works without written permission",
         terms_summary="personal research use only, never shared (and a written permission for training copies)",
         credit="Diverse Dermatology Images (Daneshjou et al., Science Advances 2022), Stanford University School of "
                "Medicine, used with permission", content="medical", cap=656,
         download="about 1 GB (656 biopsy-proven pictures)",
         how="Folder import only: the zip downloaded from Stanford after approval (or its download address, "
             "resumable); ddi_metadata.csv gives the disease, benign or malignant, and the skin tone (Fitzpatrick "
             "I-II, III-IV or V-VI) for each picture.",
         listing=listing_ddi, needs_source=True,
         local_lead="A clinical photograph from the Stanford Diverse Dermatology Images (a biopsy-proven skin "
                    "condition). The source's label says:"),
]
for _entry in PERMISSION_SOURCES:
    _entry.update(category="permission", review_only=True, fetch=make_fetch(_entry["key"]),
                  permission_folder=os.path.join(PERMISSIONS, _entry["key"]))


def source_by_key(key):
    """The PERMISSION_SOURCES entry with this key."""
    return next(s for s in PERMISSION_SOURCES if s["key"] == key)


def list_only(key, most=8):
    """Read only the public listing pages of a collection and print what was parsed (title, picture address,
    caption, skin tone, content): never fetches a picture, so it needs no permission."""
    entry = source_by_key(key)
    polite = Polite(print)
    if key == "vulva_gallery":
        items = listing_vulva_gallery(polite, print, most=most)
    elif key == "geograph":
        items = listing_geograph(polite, print, most=most)
    else:
        items = entry["listing"](polite, print)
    print(f"{entry['organisation']}: {len(items)} pictures parsed from the listing. The first {min(most, len(items))}:")
    for item in items[:most]:
        print(json.dumps({k: item.get(k) for k in ("name", "url", "page", "title", "caption", "skin", "skin_words",
                                                   "content", "credit_extra")}, ensure_ascii=False))
        print("  draft:", item_text(entry, item))
    if polite.refused:
        print(f"{polite.refused} addresses were not read because robots.txt does not allow them.")
    return items


def main(argv):
    """python permission_sources.py --list <key> [how many]  |  <key> <folder> [cap] [source] [library]"""
    if len(argv) >= 3 and argv[1] == "--list":
        list_only(argv[2], int(argv[3]) if len(argv) > 3 else 8)
        return 0
    if len(argv) < 3:
        print(main.__doc__ + "\nkeys: " + ", ".join(s["key"] for s in PERMISSION_SOURCES))
        return 1
    entry = source_by_key(argv[1])
    try:
        print(entry["fetch"](argv[2], int(argv[3]) if len(argv) > 3 else 5, print,
                             argv[4] if len(argv) > 4 else None, argv[5] if len(argv) > 5 else None))
    except NoPermission as e:
        print(e)
        return 2
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
