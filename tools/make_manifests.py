"""Make two manifests (lists) of the Picture Model Training Kit's picture collections, as Excel workbooks and as CSV
files, for reading in Excel or Notepad with a screen reader.

MANIFEST 1, "Sources": one row per organisation or collection found while making the kit. It gathers:
  - the ready-made packs (packs/*.py: every *_PACKS table, its CREDITS header, its builder's description and its
    limit), built on GitHub and published in this repository's release "training-data";
  - the collections the kit downloads itself on the trainer's computer (training-kit/kit/sources.py SOURCES);
  - the review collections (REVIEW_SOURCES, ADULT_REVIEW_SOURCES, VINTAGE_REVIEW_SOURCES) and the permission collections
    (PERMISSION_SOURCES);
  - everything left out, with the reason the code gives (every *_NOT_INCLUDED, REJECTED, *_SIGN_UP,
    CONTRACT_CANDIDATES and NEEDS_LICENCE_CHECK table);
  - what the release says about each built pack (its manifest-<key>.json: rows, pictures, size and date) and what
    the latest runs of the packs workflow say (failed, or still building);
  - the permission letters written (the letters folder's "INDEX - who to write to.txt": the letter's file name and
    who to send it to).
  Sheets: README, Summary (counts by category and status, pictures published), All sources, and one sheet for each
  place a collection is used (ready-made packs, kit downloads, review, permission, not included).

MANIFEST 2, "Pictures": one row per picture in the published packs. Each pack's list of rows (rows.jsonl) is read
  straight out of its zip on GitHub, without downloading the whole zip: only the zip's table of contents and that
  one file are fetched (HTTP range requests). Packs cut into parts (pack.zip.001, .002 ...) are read as one file.
  Packs built after November 2026 also hold considered-<key>.jsonl (every candidate the builder saw, and why it was
  dropped); those rows are added as "used: no" with their reason.

Run it with a Python that has requests and openpyxl (and the packs' own needs: pillow, pyarrow, huggingface_hub):

    python tools/make_manifests.py --out ~/Manifests --letters "~/Permission-Letters-All/INDEX - who to write to.txt"

It also zips the output folder (--zip, default: the output folder's name with .zip, next to it). The release and the
workflow runs are read with the GitHub command-line tool "gh" when it works, otherwise with plain web requests.
Nothing is changed anywhere: it only reads.
"""

import argparse
import concurrent.futures
import csv
import glob
import importlib
import io
import json
import os
import re
import subprocess
import sys
import time
import zipfile

REPO = "mark-getbraille/toolkit-models"
RELEASE = "training-data"
DOWNLOAD = f"https://github.com/{REPO}/releases/download/{RELEASE}/"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                               # the repository
PACKS_DIR = os.path.join(ROOT, "packs")
KIT_DIR = os.path.join(ROOT, "training-kit", "kit")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "packs.yml")
TOO_MANY_PICTURE_ROWS = 1_000_000                          # above this, the Pictures manifest is split by topic group
EXCEL_CELL_MOST = 32000                                    # Excel holds at most 32,767 characters in a cell


def say(text):
    """Print a line at once (progress for the person running this)."""
    print(text, flush=True)


# ----------------------------------------------------------------- reading the kit's own code

def load_code():
    """Import the packs and the kit's collection lists, in the order that keeps their imports working: the kit's
    sources.py first (it imports its other *_sources.py files itself), then the review and permission files, then
    packs/build_packs.py (it imports every *_packs.py file). Returns (sources module, build_packs module)."""
    for folder in (PACKS_DIR, KIT_DIR):
        if folder not in sys.path:
            sys.path.insert(0, folder)
    sources = importlib.import_module("sources")
    for name in ("review_sources", "adult_review_sources", "vintage_review_sources", "permission_sources"):
        importlib.import_module(name)
    build_packs = importlib.import_module("build_packs")
    # Any other *_sources.py or *_packs.py file (for example one being written and not yet wired in): imported too.
    for folder, ending in ((KIT_DIR, "_sources.py"), (PACKS_DIR, "_packs.py")):
        for path in sorted(glob.glob(os.path.join(folder, "*" + ending))):
            name = os.path.basename(path)[:-3]
            if name not in sys.modules:
                try:
                    importlib.import_module(name)
                except Exception as e:  # noqa: BLE001 - a file that cannot be loaded is reported, not fatal
                    say(f"  (Could not read {name}.py: {e})")
    return sources, build_packs


def defined_here(module, name):
    """True when the module itself defines the table called name (not one it imported from another file)."""
    try:
        with open(module.__file__, encoding="utf-8") as f:
            return re.search(rf"^{name}\b\s*[:=]", f.read(), re.M) is not None
    except (OSError, TypeError):
        return False


def tables(pattern):
    """[(module name, table name, table)] of every loaded kit or packs module's own table whose name matches."""
    found = []
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None) or ""
        if not path or os.path.dirname(os.path.abspath(path)) not in (PACKS_DIR, KIT_DIR):
            continue
        for name, value in vars(module).items():
            if re.fullmatch(pattern, name) and defined_here(module, name):
                found.append((module.__name__, name, value))
    return sorted(found, key=lambda t: (t[0], t[1]))


# Topic groups: the file a collection is in says what it is about. Files that mix subjects (the first packs, the
# general kit lists) are sorted by words in the collection's key and name (TOPIC_WORDS), or else "General".
TOPIC_BY_MODULE = {
    "pill_packs": "Medicines",
    "food_packs": "Food", "big_sources": "Food",
    "everyday_packs": "Household objects and animals",
    "text_packs": "Reading text, documents and charts",
    "world_life_packs": "Getting around and homes",
    "body_packs": "Human body (art and anatomy)",
    "medical_packs": "Medical",
    "review_sources": "Medical (intimate, review only)",
    "adult_review_sources": "Adult content (review only)",
    "vintage_review_sources": "Vintage non-sexual nudes (review only)",
    "expression_packs": "Faces, expressions and gestures",
    "world_packs": "World collections", "world_more_packs": "World collections",
    "world_portal_packs": "World collections",
    "documentary_packs": "Documentary photos", "documentary_sources": "Documentary photos",
    "disability_packs": "Disability and assistive technology", "disability_sources": "Disability and assistive technology",
    "graphic_packs": "Graphic scenes (war, disasters, injuries)", "graphic_sources": "Graphic scenes (war, disasters, injuries)",
    "archive_packs": "Archives, museums and news", "archive_sources": "Archives, museums and news",
    "service_packs": "Military and uniformed services", "service_sources": "Military and uniformed services",
    "bodily_packs": "Bodily fluids and waste", "bodily_sources": "Bodily fluids and waste",
    "culture_packs": "Sport, music, religion, landmarks, vehicles, games",
    "culture_sources": "Sport, music, religion, landmarks, vehicles, games",
    "land_industry_packs": "Farming, environment and industry", "land_industry_sources": "Farming, environment and industry",
    "home_packs": "Home life", "home_sources": "Home life",
    "events_safety_packs": "Events, history and safety", "events_safety_sources": "Events, history and safety",
    "safety_rites_packs": "Ordnance, firearms and family rites", "safety_rites_sources": "Ordnance, firearms and family rites",
    "things_packs": "Technology, tools and materials", "things_sources": "Technology, tools and materials",
}
TOPIC_WORDS = [
    ("Medicines", r"\bpills?\b|medicine|medication|\bdrugs?\b|blister|pharma"),
    ("Food", r"food|fruit|\bfish|\bmeat|beef|\beggs?\b|grocer|recipe|vegetable|produce|nutrition|\bdish|cook|chicken"),
    ("Medical", r"skin|x-?ray|medical|clinical|derm|patholog|endoscop|radiolog|lesion|disease|health|case.report|"
                r"ultrasound|anatomy|surgery|wound|vulva|breast|genital|kvasir|cancer"),
    ("Faces, expressions and gestures", r"\bfaces?\b|expression|emotion|gesture|celeb"),
    ("Reading text, documents and charts", r"\btext|ocr\b|document|receipt|chart|handwrit|\bletters?\b|\bbooks?\b|"
                                           r"\bpages?\b|\bsigns?\b|screen|textcaps|textvqa|infograph|\bmaps?\b"),
    ("Disability and assistive technology", r"blind|braille|wheelchair|disab|vizwiz|cane"),
    ("Getting around and homes", r"street|sidewalk|pavement|crossing|navigation|walkway|\broads?\b|traffic"),
    ("Household objects and animals", r"animal|\bbirds?\b|insect|plant|species|flower|\bdogs?\b|\bcats?\b|wildlife|"
                                      r"\btrees?\b|inaturalist|camera.trap|household|object"),
    ("Archives, museums and news", r"museum|\bart\b|painting|gallery|archive|smithsonian|rijks|europeana|tepapa"),
    ("Sport, music, religion, landmarks, vehicles, games", r"\bcars?\b|vehicle|aircraft|sport|music|instrument|"
                                                           r"landmark|chess|\btoys?\b|lego"),
    ("Farming, environment and industry", r"farm|crop|\bweeds?\b|agricult|satellite|aerial|cloud|weather"),
]


def topic_of(module, text=""):
    """The topic group of a collection: from the file it is in, or from words in its key and name."""
    if module in TOPIC_BY_MODULE:
        return TOPIC_BY_MODULE[module]
    for topic, words in TOPIC_WORDS:
        if re.search(words, text, re.I):
            return topic
    return "General pictures and descriptions"


URL = re.compile(r"https?://[^\s,;)\]>\"']+")


def first_url(*texts):
    """The first web address in the texts ("" when none), without a full stop at its end."""
    for text in texts:
        m = URL.search(str(text or ""))
        if m:
            return m.group(0).rstrip(".")
    return ""


def organisation_from(credit, name=""):
    """Who made a collection, from its credit line: the words after "by" in its first part ("DOCCI by Google" gives
    Google), or else its first part ("Smithsonian Institution Open Access, CC0" gives Smithsonian Institution Open
    Access). Only a reading aid: the full credit is in the licence column's source."""
    text = str(credit or name or "")
    depth, cut = 0, len(text)
    for i, ch in enumerate(text):                          # the first comma, full stop or semicolon outside brackets
        depth += ch in "(["
        depth -= ch in ")]"
        if depth <= 0 and (ch in ",;" or (ch == "." and text[i + 1:i + 2] == " ")):
            cut = i
            break
    first = text[:cut].strip()
    m = re.search(r"\bby (.+)$", first)
    if m and len(m.group(1)) < 80 and not re.match(r"(\d|CC|the kit)", m.group(1)):
        return m.group(1).strip()
    return first[:150]


def doc_line(function):
    """The first sentence of a function's description (its docstring), on one line."""
    text = " ".join((getattr(function, "__doc__", None) or "").split())
    return re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0] if text else ""


CATEGORY_OF_GROUP = {"permissive": "open", "open": "open", "share-alike": "share-alike",
                     "noncommercial": "non-commercial", "non-commercial": "non-commercial",
                     "research": "research or no terms"}
UNREACHABLE = re.compile(r"\b(403|404|refused|did not answer|does not answer|timed? ?out|cloudflare|certificate|"
                         r"no longer|not reachable|could not be reached|offline|server errors?|dead|down\b|"
                         r"leads back|unavailable|blocked)", re.I)


def limits_from_workflow():
    """({pack key: its build limit}, [the pack keys the workflow knows]) from .github/workflows/packs.yml."""
    try:
        with open(WORKFLOW, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return {}, []
    limits = {k: int(n) for k, n in re.findall(r"^\s+(\w+)\) limit=(\d+) ;;", text, re.M)}
    known_block = re.search(r"known = \[(.*?)\]", text, re.S)
    known = re.findall(r'"(\w+)"', known_block.group(1)) if known_block else []
    return limits, known


# ----------------------------------------------------------------- reading GitHub (the release and the workflow)

def gh_json(path):
    """GitHub's REST API answer for path (for example "repos/<owner>/<repo>/releases/tags/<tag>"): through the gh
    tool when it works here, otherwise a plain request (public data needs no sign-in). None when neither works."""
    try:
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=120)
        if out.returncode == 0:
            return json.loads(out.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    try:
        import requests
        r = requests.get("https://api.github.com/" + path, timeout=60,
                         headers={"Accept": "application/vnd.github+json"})
        if r.status_code == 200:
            return r.json()
    except Exception:  # noqa: BLE001 - no answer: the caller says what is missing
        pass
    return None


def gh_text(path):
    """GitHub's REST API answer for path as text (a job's log), or "" when it cannot be read."""
    try:
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=180)
        return out.stdout if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def release_assets():
    """{asset name: {"size", "updated", "url"}} of the release's files, page by page (100 a page)."""
    release = gh_json(f"repos/{REPO}/releases/tags/{RELEASE}")
    if not release:
        return {}
    assets = {}
    for page in range(1, 20):
        batch = gh_json(f"repos/{REPO}/releases/{release['id']}/assets?per_page=100&page={page}") or []
        for a in batch:
            assets[a["name"]] = {"size": a["size"], "updated": a["updated_at"], "url": a["browser_download_url"]}
        if len(batch) < 100:
            break
    return assets


def pack_manifests(assets, s):
    """{pack key: its manifest (rows, pictures, size, sha256, files) with "built" (the date it was published)}: the
    manifest-<key>.json files of the release, or packs.json when the release's file list cannot be read."""
    out = {}
    names = [n for n in assets if n.startswith("manifest-") and n.endswith(".json")]
    if names:
        def one(name):
            """One manifest, with its date."""
            for _ in range(3):
                try:
                    data = s.get(DOWNLOAD + name, timeout=60).json()
                    data["built"] = assets[name]["updated"][:10]
                    return data
                except Exception:  # noqa: BLE001 - tried again
                    time.sleep(3)
            return None
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            for data in pool.map(one, names):
                if data:
                    out[data["key"]] = data
    else:
        try:
            out = s.get(DOWNLOAD + "packs.json", timeout=60).json()
        except Exception:  # noqa: BLE001 - nothing published can be read
            out = {}
    return out


def workflow_state(max_runs=15):
    """{pack key: {"state": "failed" | "building" | "succeeded", "when", "why"}} from the latest runs of the packs
    workflow: each pack's newest job that was not cancelled. For a failed job, "why" is the last line its log printed
    before the error (when the log can be read)."""
    runs = gh_json(f"repos/{REPO}/actions/workflows/packs.yml/runs?per_page={max_runs}")
    if not runs:
        return None
    jobs = []
    for run in runs.get("workflow_runs", []):
        for page in (1, 2, 3):
            batch = (gh_json(f"repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100&page={page}&filter=all")
                     or {}).get("jobs", [])
            jobs += batch
            if len(batch) < 100:
                break
    state = {}
    for job in sorted(jobs, key=lambda j: j.get("started_at") or j.get("created_at") or "", reverse=True):
        m = re.fullmatch(r"build \((\w+)\)", job.get("name", ""))
        if not m or m.group(1) in state or job.get("conclusion") in ("cancelled", "skipped"):
            continue
        when = (job.get("completed_at") or job.get("started_at") or job.get("created_at") or "")[:10]
        if job.get("status") != "completed":
            state[m.group(1)] = {"state": "building" if job.get("status") == "in_progress" else "queued",
                                 "when": when, "why": "", "id": job["id"]}
        else:
            state[m.group(1)] = {"state": "succeeded" if job.get("conclusion") == "success" else "failed",
                                 "when": when, "why": "", "id": job["id"]}
    for key, info in state.items():
        if info["state"] == "failed":
            info["why"] = failure_line(gh_text(f"repos/{REPO}/actions/jobs/{info['id']}/logs"))
    return state


def failure_line(log):
    """The last thing a failed build printed before GitHub's "##[error]" line, without the time stamp."""
    lines = log.splitlines()
    end = next((i for i, line in enumerate(lines) if "##[error]" in line), len(lines))
    for line in reversed(lines[:end]):
        text = re.sub(r"^\S+Z ", "", line).strip()
        if text and not text.startswith("##["):
            return text[:300]
    return ""


# ----------------------------------------------------------------- the permission letters

def read_letters(path):
    """[{"number", "organisation", "file", "contact", "asking", "reply_key"}] from the letters folder's index."""
    try:
        with open(os.path.expanduser(path), encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except OSError:
        say(f"  (The letters index {path} could not be read: letters are left out.)")
        return []
    letters, current, field = [], None, None
    for line in lines:
        m = re.match(r"^(\d+\.\d+) (.+)$", line)
        if m:
            current = {"number": m.group(1), "organisation": m.group(2).strip(), "file": "", "contact": "",
                       "asking": "", "reply_key": ""}
            letters.append(current)
            field = None
            continue
        if current is None:
            continue
        m = re.match(r"^   ([A-Za-z ]+): (.*)$", line)
        if m:
            field = {"File": "file", "Contact": "contact", "Asking for": "asking"}.get(m.group(1))
            if field:
                current[field] = m.group(2).strip()
            if m.group(1) == "Reply goes":
                k = re.search(r"Permissions\\(\w+)", m.group(2))
                current["reply_key"] = k.group(1) if k else ""
            continue
        if line.startswith("      ") and field:                # a field carried on to the next line
            current[field] += " " + line.strip()
            continue
        if not line.strip() or line.startswith("="):
            current, field = (None, None) if line.startswith("=") else (current, None)
    return letters


GENERIC = set("""the a an of and or for in on at to by with from de du la le des der die und van von
national museum museums library libraries dataset datasets data images image photos photo photographs pictures
picture collection collections university institute society foundation project open research center centre
archive archives digital public gallery service services department agency trust group inc llc ltd co
council new world international organisation organization official office online network media""".split())


def words(text):
    """The distinctive words of a name (lower case, without common words such as "museum" or "dataset")."""
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower().replace("'s", "")) if len(w) > 2 and
            w not in GENERIC}


def match_letters(rows, letters):
    """Fill each row's "letter written" and "contact" from the letter that fits it: the letter whose reply goes to
    the row's key, or else the letter whose organisation's distinctive words best match the row's organisation and
    name (at least two thirds of the letter's words; a letter whose name has only one distinctive word needs it to
    be at least four letters long). Among equal matches, the rows whose own words the letter covers best win, so
    "British Museum" fits the British Museum's row, not the Yale Center for British Art's. A row can have several
    letters. Returns the letters that fit no row."""
    unused = []
    for letter in letters:
        best, best_score = [], (0.0, 0.0)
        if letter["reply_key"]:
            best = [r for r in rows if r["key"] == letter["reply_key"]]
            best_score = (1.0, 1.0) if best else best_score
        if not best:
            want = words(letter["organisation"])
            if not want or (len(want) == 1 and len(next(iter(want))) < 4):
                unused.append(letter)
                continue
            for r in rows:
                have = words(" ".join((r["organisation"], r["collection name"], r["key"].replace("_", " "))))
                common = want & have
                score = (len(common) / len(want), len(common) / len(have) if have else 0.0)
                if score > best_score:
                    best, best_score = [r], score
                elif common and score == best_score:
                    best.append(r)
        if best and best_score[0] >= 0.66 and len(best) <= 6:
            for r in best:
                note = f"yes: {letter['file']} (letter {letter['number']})"
                r["letter written"] = f"{r['letter written']}; {note}" if r["letter written"] else note
                # The letter's contact, unless the row already names the same address (from the code).
                address = (re.findall(r"[\w.+-]+@[\w.-]+|[\w-]+(?:\.[\w-]+)+/[^\s,;)]*", letter["contact"]) or
                           [letter["contact"]])[0]
                if address not in r["contact"]:
                    r["contact"] = f"{r['contact']}; {letter['contact']}" if r["contact"] else letter["contact"]
        else:
            unused.append(letter)
    return unused


# ----------------------------------------------------------------- MANIFEST 1: sources

SOURCE_COLUMNS = [
    ("key", 24), ("collection name", 50), ("organisation", 36), ("topic group", 30), ("where it's used", 22),
    ("category", 20), ("licence", 50), ("licence or terms link", 45), ("content tags", 16),
    ("used for picture-making", 12), ("pictures published", 12), ("rows published", 12), ("pack size in MB", 12),
    ("pack built date", 14), ("limit or cap", 12), ("status", 22), ("reason", 70), ("letter written", 45),
    ("contact", 45), ("description from the code", 70), ("found in", 32),
]


def blank_row(**fields):
    """A Sources row with every column present."""
    row = {name: "" for name, _ in SOURCE_COLUMNS}
    row.update(fields)
    return row


def picture_making(sources, s):
    """ "yes" when a picture-making model may learn from this collection (train_pictures.chosen_sources' rule: not
    in NOT_FOR_PICTURE_MAKING, not intimate, sexual or graphic, and a personal-use one only when its key is in
    PERSONAL_PICTURE_MAKING_OK), otherwise "no"."""
    never = set(getattr(sources, "NOT_FOR_PICTURE_MAKING", ()))
    making_ok = set(getattr(sources, "PERSONAL_PICTURE_MAKING_OK", ()) or ())
    banned = set(getattr(sources, "PICTURE_MAKING_NEVER", ("intimate", "sexual", "graphic")))
    ok = s.key not in never and getattr(s, "content", "") not in banned and \
        (getattr(s, "group", "") not in ("noncommercial", "research") or s.key in making_ok)
    return "yes" if ok else "no"


def source_rows(sources, build_packs, manifests, runs, pack_stats):
    """Every Sources row (see the module docstring), before the letters are matched."""
    rows = []
    packs = dict(build_packs.PACKS)
    wired = set(packs)
    # Packs written but not yet wired into build_packs.py: their own *_PACKS tables.
    pack_module = {}                                        # {pack key: the packs file whose table lists it}
    for module, name, table in tables(r"[A-Z_]*_PACKS"):
        if isinstance(table, dict):
            for key, value in table.items():
                if isinstance(value, tuple):
                    pack_module.setdefault(key, module)
                    packs.setdefault(key, value)
    limits = {}
    for _module, _name, table in tables(r"[A-Z_]*_LIMITS"):
        if isinstance(table, dict):
            limits.update(table)
    workflow_limits, workflow_known = limits_from_workflow()
    limits.update(workflow_limits)
    by_key = {s.key: s for s in sources.SOURCES}
    # Kit collections written but not yet wired into sources.py: their own *_SOURCES lists.
    unwired_kit = {}
    for module, name, table in tables(r"[A-Z_]*_SOURCES"):
        if isinstance(table, list):
            for s in table:
                if hasattr(s, "key") and hasattr(s, "group") and s.key not in by_key:
                    by_key[s.key] = s
                    unwired_kit[s.key] = module
    needs_check = {s.key for _m, _n, t in tables(r"[A-Z_]*NEEDS_LICENCE_CHECK") for s in t if hasattr(s, "key")}

    for key, (builder, credits) in packs.items():
        s = by_key.get(key)
        module = pack_module.get(key) or builder.__module__
        if module == "__main__":
            module = "build_packs"
        topic = topic_of(module, f"{key} {getattr(s, 'name', '')}")
        manifest = manifests.get(key)
        run = (runs or {}).get(key)
        reason = ""
        if manifest:
            status = "built"
            if run and run["state"] == "failed" and run["when"] >= manifest.get("built", ""):
                reason = f"A later rebuild on {run['when']} failed ({run['why']}); the published pack is the earlier one."
            elif run and run["state"] in ("building", "queued"):
                reason = "Being rebuilt now (a packs workflow run is in progress)."
        elif run and run["state"] == "failed":
            status, reason = "failed", f"The build on {run['when']} failed: {run['why'] or 'see the workflow log'}"
        else:
            status = "not built yet"
            if key not in wired:
                reason = f"Written in packs/{module}.py but not yet wired into build_packs.py."
            elif workflow_known and key not in workflow_known:
                reason = "Not yet in the packs workflow's list of packs."
            elif run and run["state"] == "building":
                reason = f"Building now (a packs workflow run started {run['when']} is in progress)."
            elif run and run["state"] == "queued":
                reason = "Waiting to be built: queued in a packs workflow run that is in progress."
            elif runs is None:
                reason = "The workflow runs could not be read here."
        stats = pack_stats.get(key, {})
        tags = sorted({getattr(s, "content", "")} | set(stats.get("tags", ())) - {""})
        rows.append(blank_row(**{
            "key": key, "collection name": getattr(s, "name", "") or doc_line(builder),
            "organisation": organisation_from(credits), "topic group": topic, "where it's used": "ready-made pack",
            "category": CATEGORY_OF_GROUP.get(getattr(s, "group", "permissive"), "open"),
            "licence": getattr(s, "licence", "") or credits, "licence or terms link":
                getattr(s, "terms", "") or first_url(credits, getattr(s, "licence", "")),
            "content tags": ", ".join(tags), "used for picture-making": picture_making(sources, s) if s else "no",
            "pictures published": manifest["pictures"] if manifest else "",
            "rows published": manifest["rows"] if manifest else "",
            "pack size in MB": round(manifest["size"] / 1e6, 1) if manifest else "",
            "pack built date": manifest.get("built", "") if manifest else "", "limit or cap": limits.get(key, ""),
            "status": status, "reason": reason, "description from the code": doc_line(builder),
            "found in": f"packs/{module}.py ({credits[:60]}...)" if len(credits) > 60 else f"packs/{module}.py"}))

    for key, s in by_key.items():
        if key in packs:
            continue
        module = unwired_kit.get(key) or s.prepare.__module__
        where, status, reason = "kit download", "kit download", ""
        if key in needs_check:
            where, status = "not included", "rejected"
            reason = "Ready, but not trained on: its makers have not written down a licence for its words yet."
        elif key in unwired_kit:
            reason = f"Written in training-kit/kit/{module}.py but not yet wired into sources.py."
        rows.append(blank_row(**{
            "key": key, "collection name": s.name, "organisation": organisation_from(s.credit, s.name),
            "topic group": topic_of(module, f"{key} {s.name}"), "where it's used": where,
            "category": "not included" if key in needs_check else CATEGORY_OF_GROUP.get(s.group, s.group),
            "licence": s.licence, "licence or terms link": getattr(s, "terms", "") or first_url(s.licence, s.credit),
            "content tags": s.content, "used for picture-making": "no" if key in needs_check else
            picture_making(sources, s), "limit or cap": s.cap, "status": status, "reason": reason,
            "description from the code": getattr(s, "terms_summary", "") or "",
            "found in": f"training-kit/kit/{module}.py"}))
    for key in sorted(needs_check - set(by_key)):
        s = next(s for _m, _n, t in tables(r"[A-Z_]*NEEDS_LICENCE_CHECK") for s in t if getattr(s, "key", "") == key)
        rows.append(blank_row(**{
            "key": key, "collection name": s.name, "organisation": organisation_from(s.credit, s.name),
            "topic group": topic_of(s.prepare.__module__, f"{key} {s.name}"), "where it's used": "not included",
            "category": "not included", "licence": s.licence, "licence or terms link": first_url(s.licence, s.credit),
            "used for picture-making": "no", "limit or cap": s.cap, "status": "rejected",
            "reason": "Ready, but not trained on: its makers have not written down a licence for its words yet.",
            "found in": f"training-kit/kit/{s.prepare.__module__}.py (NEEDS_LICENCE_CHECK)"}))

    # Review collections (a person checks every picture before it is used) and permission collections.
    for module, name, table in tables(r"(ADULT_|VINTAGE_)?REVIEW_SOURCES|PERMISSION_SOURCES"):
        permission = name == "PERMISSION_SOURCES"
        for d in table:
            rows.append(blank_row(**{
                "key": d["key"], "collection name": d.get("name", ""),
                "organisation": d.get("organisation") or organisation_from(d.get("credit", ""), d.get("name", "")),
                "topic group": topic_of(module if not permission else "",
                                        f"{d['key']} {d.get('name', '')} {d.get('content', '')}"),
                "where it's used": "permission collection" if permission else "review collection",
                "category": "permission" if permission else CATEGORY_OF_GROUP.get(d.get("category", ""), d.get("category", "")),
                "licence": d.get("licence", ""), "licence or terms link": d.get("terms", "") or first_url(d.get("licence")),
                "content tags": d.get("content", ""), "used for picture-making": "no", "limit or cap": d.get("cap", ""),
                "status": "waiting for permission" if permission else "review",
                "_letter": f"yes: {d['letter']} (named in the code)" if d.get("letter") else "",
                "contact": d.get("contact", ""), "description from the code": d.get("terms_summary", ""),
                "found in": f"training-kit/kit/{module}.py ({name})"}))

    # Left out: not included, rejected, sign-up needed, contract candidates.
    for module, name, table in tables(r"[A-Z_]*NOT_INCLUDED|[A-Z_]*REJECTED|[A-Z_]*SIGN_UP"):
        folder = "packs" if module.endswith("_packs") else "training-kit/kit"
        sign_up = name.endswith("SIGN_UP")
        for collection, why in (table.items() if isinstance(table, dict) else ((t, "") for t in table)):
            why = " ".join(str(why).split())
            if sign_up:
                category, status, where = "sign-up needed", "sign-up needed", "not included"
            else:
                category, where = "not included", "not included"
                status = "could not reach (blocked or dead)" if UNREACHABLE.search(why) else "rejected"
            rows.append(blank_row(**{
                "collection name": collection, "organisation": organisation_from(collection),
                "topic group": topic_of(module if module not in ("extra_sources", "personal_sources") else "",
                                        collection + " " + why),
                "where it's used": where, "category": category, "licence or terms link": first_url(why, collection),
                "used for picture-making": "no", "status": status, "reason": why,
                "found in": f"{folder}/{module}.py ({name})"}))
    for module, name, table in tables(r"[A-Z_]*CONTRACT_CANDIDATES"):
        for collection in table:
            rows.append(blank_row(**{
                "collection name": collection, "organisation": collection,
                "topic group": topic_of(module, collection), "where it's used": "not included",
                "category": "permission", "used for picture-making": "no", "status": "waiting for permission",
                "reason": "A contract candidate: its pictures could only be used under a contract or with permission.",
                "found in": f"training-kit/kit/{module}.py ({name})"}))
    return rows


def letter_rows(letters):
    """Rows for letters that fit no collection in the code: organisations written to that the kit does not list
    yet."""
    rows = []
    for letter in letters:
        rows.append(blank_row(**{
            "collection name": letter["asking"] or letter["organisation"], "organisation": letter["organisation"],
            "topic group": topic_of("", letter["organisation"] + " " + letter["asking"]),
            "where it's used": "not included", "category": "permission", "used for picture-making": "no",
            "status": "waiting for permission",
            "reason": "A permission letter was written; the collection is not in the kit's code yet.",
            "letter written": f"yes: {letter['file']} (letter {letter['number']})", "contact": letter["contact"],
            "found in": "the letters index only"}))
    return rows


# ----------------------------------------------------------------- reading a pack zip on the web, piece by piece

class RemoteParts(io.RawIOBase):
    """One or more files on the web (a zip, or its numbered parts) read as one file, in pieces (HTTP Range
    requests), so zipfile can take one file out of a published pack without downloading all of it. GitHub's
    download addresses redirect to signed addresses that expire, so a fresh one is asked for when reading fails."""

    def __init__(self, urls, s):
        """Opens each part and asks for its size."""
        super().__init__()
        self.s, self.urls, self.pos = s, list(urls), 0
        self.signed, self.sizes = [], []
        for url in self.urls:
            signed, size = self.resolve(url)
            self.signed.append(signed)
            self.sizes.append(size)
        self.starts = [sum(self.sizes[:i]) for i in range(len(self.sizes))]
        self.size = sum(self.sizes)

    def resolve(self, url):
        """(the signed address after the redirect, the file's size)."""
        r = self.s.get(url, headers={"Range": "bytes=0-0"}, timeout=120, stream=True)
        r.raise_for_status()
        size = int(r.headers["Content-Range"].rsplit("/", 1)[1])
        signed = r.url
        r.close()
        return signed, size

    def readable(self):
        """It can be read."""
        return True

    def seekable(self):
        """It can be read from any place."""
        return True

    def tell(self):
        """The current place."""
        return self.pos

    def seek(self, offset, whence=0):
        """Move to a place (as for a normal file)."""
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def readinto(self, buffer):
        """Read the next bytes into buffer, from the part they are in (never across two parts in one request)."""
        n = min(len(buffer), self.size - self.pos)
        if n <= 0:
            return 0
        part = max(i for i, start in enumerate(self.starts) if start <= self.pos)
        inside = self.pos - self.starts[part]
        n = min(n, self.sizes[part] - inside)
        for attempt in range(6):
            try:
                r = self.s.get(self.signed[part], timeout=120,
                               headers={"Range": f"bytes={inside}-{inside + n - 1}"})
                if r.status_code == 206 and len(r.content) == n:
                    buffer[:n] = r.content
                    self.pos += n
                    return n
            except Exception:  # noqa: BLE001 - a fresh address and another try
                pass
            time.sleep(2 * (attempt + 1))
            try:
                self.signed[part] = self.resolve(self.urls[part])[0]
            except Exception:  # noqa: BLE001 - tried again on the next round
                pass
        raise OSError(f"could not read {self.urls[part]} at {inside}")


def read_pack_rows(key, manifest, cache, s):
    """(rows, considered rows, problem) of a published pack: its rows.jsonl (and considered-<key>.jsonl when the
    pack has one), from the cache folder when read before, otherwise read out of the zip on the web."""
    tag = (manifest.get("sha256") or "")[:12]
    rows_path = os.path.join(cache, f"rows-{key}-{tag}.jsonl")
    considered_path = os.path.join(cache, f"considered-{key}-{tag}.jsonl")
    if not os.path.exists(rows_path):
        try:
            remote = RemoteParts([DOWNLOAD + f for f in manifest["files"]], s)
            with zipfile.ZipFile(io.BufferedReader(remote, 1 << 18)) as z:
                names = set(z.namelist())
                member = "rows.jsonl" if "rows.jsonl" in names else next(
                    (n for n in names if n.endswith(".jsonl") and not n.startswith("considered-")), None)
                if not member:
                    return [], [], "no rows file in the zip"
                data = z.read(member)
                considered = z.read(f"considered-{key}.jsonl") if f"considered-{key}.jsonl" in names else b""
        except Exception as e:  # noqa: BLE001 - reported in the manifest's README
            return [], [], f"not read: {str(e).splitlines()[0][:150]}"
        with open(considered_path + ".part", "wb") as f:
            f.write(considered)
        os.replace(considered_path + ".part", considered_path)
        with open(rows_path + ".part", "wb") as f:
            f.write(data)
        os.replace(rows_path + ".part", rows_path)

    def load(path):
        """The JSON lines of a file ([] when there is none)."""
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    return load(rows_path), load(considered_path), ""


# ----------------------------------------------------------------- MANIFEST 2: pictures

PICTURE_COLUMNS = [
    ("pack key", 22), ("topic group", 26), ("picture file name in the pack", 40), ("source URL", 50),
    ("question", 40), ("answer (the description)", 90), ("credit and author", 60), ("licence", 26), ("place", 26),
    ("content tags", 14), ("child mark", 10), ("translated", 10), ("used", 8), ("why", 50),
]
LICENCE_WORDS = re.compile(
    r"\b(CC0(?: 1\.0)?|CC[ -]BY(?:[ -](?:NC-SA|NC-ND|SA|NC|ND))?(?:[ -]\d\.\d)?|Public Domain Mark|public domain|"
    r"no known copyright(?: restrictions)?|Apache[- ]2\.0|MIT licen[cs]e|ODbL|CDLA[- ]\w+[- ]\d\.\d)", re.I)


def licences_in(text):
    """The licences a credit line names, in order, without repeats ("" when it names none)."""
    found = []
    for m in LICENCE_WORDS.finditer(str(text or "")):
        name = m.group(1)
        if name.lower() not in (f.lower() for f in found):
            found.append(name)
    return "; ".join(found)


def tags_of(row):
    """A row's content tags ("graphic", "medical" ...), as a set."""
    tags = set(row.get("contents") or []) if isinstance(row.get("contents"), list) else set()
    if row.get("content"):
        tags.add(str(row["content"]).lower())
    return tags - {""}


def picture_row(key, topic, pack_licence, category, row):
    """One Pictures row for a pack row."""
    credit = str(row.get("credit") or "")
    licence = licences_in(credit) or pack_licence
    tags = tags_of(row)
    why = f"{category} licence ({licence[:60]}); passed the builder's filters"
    if row.get("translated"):
        why += "; machine translation that passed the translation check"
    if tags:
        why += f"; tagged {', '.join(sorted(tags))}: used only when that content is chosen"
    place = str(row.get("place") or "")
    if place and row.get("place_kind"):
        place += f" ({row['place_kind']})"
    return [key, topic, row.get("file") or "", row.get("url") or first_url(credit), row.get("question") or "",
            row.get("answer") or "", credit, licence, place, ", ".join(sorted(tags)),
            "yes" if row.get("child") else "", "yes" if row.get("translated") else "", "yes", why]


def considered_row(key, topic, record):
    """One Pictures row for a candidate from a pack's considered-<key>.jsonl (newer builds only)."""
    used = record.get("used")
    return [key, topic, record.get("file") or record.get("name") or "", record.get("url") or "", "", "", "", "", "",
            "", "", "", "yes" if used else "no", record.get("reason") or ("in the pack" if used else "")]


ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def cell(value):
    """A value Excel can hold: control characters removed, at most EXCEL_CELL_MOST characters."""
    if isinstance(value, str):
        value = ILLEGAL.sub(" ", value)
        if len(value) > EXCEL_CELL_MOST:
            value = value[:EXCEL_CELL_MOST] + " [cut: too long for one Excel cell]"
    return value


def new_sheet(book, title, columns, write_only=False):
    """A worksheet with a bold header row, frozen below it, and the column widths given."""
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter
    from openpyxl.cell import WriteOnlyCell
    ws = book.create_sheet(title=sheet_title(title))
    for i, (_name, width) in enumerate(columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.freeze_panes = "A2"
    if write_only:
        header = []
        for name, _ in columns:
            c = WriteOnlyCell(ws, value=name)
            c.font = Font(bold=True)
            header.append(c)
        ws.append(header)
    else:
        ws.append([name for name, _ in columns])
        for c in ws[1]:
            c.font = Font(bold=True)
    return ws


def sheet_title(title):
    """A sheet name Excel accepts: at most 31 characters, without the characters it forbids."""
    return re.sub(r"[\[\]:*?/\\]", "-", title)[:31]


def text_sheet(book, title, lines, write_only=False):
    """A sheet of plain text, one line a row (the README sheets)."""
    ws = book.create_sheet(title=title)
    ws.column_dimensions["A"].width = 120
    for line in lines:
        ws.append([cell(line)])
    return ws


def write_csv(path, columns, rows):
    """A CSV file in UTF-8 with a byte-order mark, so Excel opens it with the right characters."""
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        out = csv.writer(f)
        out.writerow([name for name, _ in columns])
        for row in rows:
            out.writerow(row)


# ----------------------------------------------------------------- README texts

def sources_readme(problems, runs_read):
    """The README sheet of the Sources manifest."""
    return [
        "SOURCES MANIFEST: one row per organisation or collection found while making the Picture Model Training Kit.",
        f"Made {time.strftime('%d %B %Y')} by tools/make_manifests.py in the toolkit-models repository.",
        "",
        "Sheets: Summary (counts by category and status, and the pictures published); All sources; then one sheet for "
        "each place a collection is used: ready-made packs, kit downloads, review collections, permission collections "
        "and not included.",
        "",
        "Where it's used:",
        "  ready-made pack: built on GitHub and published in the release 'training-data'; the kit downloads the pack.",
        "  kit download: the kit downloads the collection itself on your computer when you choose it.",
        "  review collection: fetched on your computer; you check every picture before it is used.",
        "  permission collection: used only after its owner gives permission (the letters).",
        "  not included: left out (the reason column says why), or needs a sign-up, or waits for permission.",
        "",
        "Category: open, share-alike, non-commercial, research or no terms, permission, sign-up needed, not included.",
        "Status: built, failed, not built yet (packs); kit download; review; waiting for permission; rejected; "
        "sign-up needed; could not reach (blocked or dead).",
        "The organisation column is read from each collection's credit line, so it is a reading aid, not an official "
        "name. The topic group comes from the code file the collection is in (or words in its name).",
        "Letters: matched to collections by the 'Reply goes' line or by the organisation's name; letters that fit no "
        "collection in the code have their own rows (found in: the letters index only).",
        "Workflow runs: " + ("read (failed and still-building packs are marked)." if runs_read else
                             "could not be read here, so packs without a published manifest are marked not built yet."),
        "",
    ] + (["What could not be read:"] + ["  " + p for p in problems] if problems else [])


PICTURES_README = """PICTURES MANIFEST: one row per picture in the published ready-made packs of the Picture Model Training Kit.
Made {date} by tools/make_manifests.py in the toolkit-models repository.

Each pack's list of rows (rows.jsonl) was read straight out of its zip in the GitHub release "training-data". There is
one row per row of the pack: a picture with two questions has two rows. Rows with a source URL and no file name are
pictures the kit fetches itself (the COCO photos): the pack holds only their address.

Licence: the licence the picture's credit line names, or else the pack's licence. Why: why the picture is used.
Content tags (graphic, medical ...): those rows are used only when that content choice is ticked. Child mark: the
picture shows a child (never used for picture-making). Translated: an English machine translation of a caption.

Pictures that were NOT used: the pack builders up to now did not keep a list of the pictures they looked at and
dropped (for a licence that does not allow sharing, a missing caption, a picture that could not be downloaded, or the
pack's limit). So there are "used: no" rows only where a pack recorded them. From now on, each pack built on GitHub
also holds considered-<key>.jsonl: every candidate the shared checks saw (the Commons and COCO licence checks, the Open
Images licence check of the food and household-object packs, and every picture download), with the reason when it was
dropped. When those packs are rebuilt, running tools/make_manifests.py again adds them here.

The kit's own downloads (kit downloads, review collections and permission collections) are downloaded and prepared
on your computer, so there is no list of their pictures here. The kit keeps a record of each picture it prepares in
the picture library's data folder: data/<key>-<size>.jsonl (for example data/docci-normal.jsonl), one line per
picture, on your computer.
"""


# ----------------------------------------------------------------- the main steps

def main(argv=None):
    """Make both manifests (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=os.path.expanduser("~/Manifests"), help="the folder to write them in")
    parser.add_argument("--letters", default=os.path.expanduser(
        "~/Permission-Letters-All/INDEX - who to write to.txt"), help="the permission letters' index")
    parser.add_argument("--cache", default="", help="a folder to keep the packs' rows in between runs")
    parser.add_argument("--zip", default="", help="the zip of the output folder (default: next to it)")
    parser.add_argument("--no-pictures", action="store_true", help="make only the Sources manifest")
    args = parser.parse_args(argv)
    import requests
    from openpyxl import Workbook

    out = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(out, exist_ok=True)
    cache = os.path.abspath(os.path.expanduser(args.cache or os.path.join(out, ".rows-cache")))
    os.makedirs(cache, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = "PictureModelTrainingKit-manifests/1"
    problems = []

    say("Reading the kit's code ...")
    sources, build_packs = load_code()
    say("Reading the release 'training-data' ...")
    assets = release_assets()
    if not assets:
        problems.append("The release's file list could not be read; packs.json was used instead (no build dates).")
    manifests = pack_manifests(assets, s)
    say(f"  {len(manifests)} published packs")
    say("Reading the latest runs of the packs workflow ...")
    runs = workflow_state()
    if runs is None:
        problems.append("The packs workflow runs could not be read: packs without a published manifest are marked "
                        "'not built yet'.")

    # The packs' rows: read once (into the cache), used for the pack statistics and for the Pictures manifest.
    pack_rows_problem, pack_stats = {}, {}
    if not args.no_pictures:
        say("Reading each published pack's rows from its zip (only the zip's table of contents and rows.jsonl) ...")

        def one(key):
            """One pack's rows (counted only; the rows themselves are read again from the cache when written)."""
            rows, considered, problem = read_pack_rows(key, manifests[key], cache, s)
            tags = set()
            for r in rows:
                tags |= tags_of(r)
            return key, len(rows), len(considered), tags, problem
        with concurrent.futures.ThreadPoolExecutor(6) as pool:
            for key, n, n_considered, tags, problem in pool.map(one, sorted(manifests)):
                pack_stats[key] = {"rows": n, "considered": n_considered, "tags": tags}
                if problem:
                    pack_rows_problem[key] = problem
                    problems.append(f"Pack {key}: rows {problem}.")
                say(f"  {key}: {n} rows" + (f", {n_considered} considered" if n_considered else "") +
                    (f" ({problem})" if problem else ""))

    say("Making the Sources manifest ...")
    rows = source_rows(sources, build_packs, manifests, runs, pack_stats)
    letters = read_letters(args.letters)
    unused = match_letters(rows, letters)
    rows += letter_rows(unused)
    for r in rows:
        if not r["letter written"]:
            r["letter written"] = r.get("_letter") or "no"   # the code's own letter name when the index has none
    say(f"  {len(rows)} rows; {len(letters)} letters, {len(letters) - len(unused)} matched to collections in the code")
    names = [n for n, _ in SOURCE_COLUMNS]
    book = Workbook()
    book.remove(book.active)
    text_sheet(book, "README", sources_readme(problems, runs is not None))
    summary = summary_lines(rows)
    ws = new_sheet(book, "Summary", [("what", 50), ("count", 14), ("", 14)])
    for line in summary[1:]:                               # (its first line is the header, written already)
        ws.append(line)
    sections = [("All sources", None), ("Ready-made packs", "ready-made pack"), ("Kit downloads", "kit download"),
                ("Review collections", "review collection"), ("Permission collections", "permission collection"),
                ("Not included", "not included")]
    for title, where in sections:
        ws = new_sheet(book, title, SOURCE_COLUMNS)
        for r in rows:
            if where is None or r["where it's used"] == where:
                ws.append([cell(r[n]) for n in names])
        ws.auto_filter.ref = ws.dimensions
    book.save(os.path.join(out, "Sources.xlsx"))
    write_csv(os.path.join(out, "Sources.csv"), SOURCE_COLUMNS, ([r[n] for n in names] for r in rows))
    write_csv(os.path.join(out, "Sources-Summary.csv"), [("what", 0), ("count", 0), ("", 0)], summary[1:])
    say(f"  {os.path.join(out, 'Sources.xlsx')}, Sources.csv, Sources-Summary.csv")

    picture_count = 0
    if not args.no_pictures:
        picture_count = write_pictures(out, cache, rows, manifests, pack_rows_problem, sources, s)

    with open(os.path.join(out, "README.txt"), "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(readme_text(rows, picture_count, problems, args.no_pictures))
    zip_path = os.path.abspath(os.path.expanduser(args.zip or out.rstrip(os.sep) + ".zip"))
    with zipfile.ZipFile(zip_path + ".part", "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        for name in sorted(os.listdir(out)):
            path = os.path.join(out, name)
            if os.path.isfile(path):
                z.write(path, os.path.join(os.path.basename(out.rstrip(os.sep)), name))
    os.replace(zip_path + ".part", zip_path)
    say(f"Zipped to {zip_path}")
    return 0


def summary_lines(rows):
    """The Summary sheet's rows: counts by category, by status, by where used, and the published totals."""
    def counts(column):
        """[(value, number of rows)] of a column, most first."""
        found = {}
        for r in rows:
            found[r[column]] = found.get(r[column], 0) + 1
        return sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))
    lines = [["what", "count", ""]]
    lines.append(["All rows (organisations and collections)", len(rows), ""])
    for column in ("category", "status", "where it's used", "topic group"):
        lines.append(["", "", ""])
        lines.append([f"By {column}:", "", ""])
        lines += [[f"  {value or '(none)'}", n, ""] for value, n in counts(column)]
    packs = [r for r in rows if r["where it's used"] == "ready-made pack" and r["status"] == "built"]
    lines.append(["", "", ""])
    lines.append(["Published packs", len(packs), ""])
    lines.append(["Pictures published (in the packs)", sum(int(r["pictures published"] or 0) for r in packs), ""])
    lines.append(["Rows published (in the packs)", sum(int(r["rows published"] or 0) for r in packs), ""])
    lines.append(["Size of the published packs in MB", round(sum(float(r["pack size in MB"] or 0) for r in packs), 1), ""])
    lines.append(["Letters written (rows marked yes)", sum(1 for r in rows if r["letter written"].startswith("yes")), ""])
    return lines


def write_pictures(out, cache, rows, manifests, problems, sources, s):
    """Write Pictures.xlsx (a README sheet, then one sheet per topic group) and Pictures.csv, or, above
    TOO_MANY_PICTURE_ROWS rows, one pair of files per topic group. Returns the number of picture rows written."""
    from openpyxl import Workbook
    say("Making the Pictures manifest ...")
    by_key = {r["key"]: r for r in rows if r["where it's used"] == "ready-made pack"}
    order = sorted((k for k in manifests if k in by_key and k not in problems),
                   key=lambda k: (by_key[k]["topic group"], k))
    total = sum(manifests[k]["rows"] for k in order)
    split = total > TOO_MANY_PICTURE_ROWS
    groups = []
    for k in order:
        if not groups or groups[-1][0] != by_key[k]["topic group"]:
            groups.append((by_key[k]["topic group"], []))
        groups[-1][1].append(k)
    readme = PICTURES_README.format(date=time.strftime("%d %B %Y")).splitlines()
    if problems:
        readme += ["", "Packs whose rows could not be read:"] + [f"  {k}: {p}" for k, p in sorted(problems.items())]
    files = [("Pictures", groups)] if not split else [(f"Pictures - {g}", [(g, keys)]) for g, keys in groups]
    written = 0
    for base, file_groups in files:
        base = re.sub(r"[^\w ,()-]", "-", base)
        book = Workbook(write_only=True)
        text_sheet(book, "README", readme)
        with open(os.path.join(out, base + ".csv"), "w", encoding="utf-8-sig", newline="") as f:
            out_csv = csv.writer(f)
            out_csv.writerow([n for n, _ in PICTURE_COLUMNS])
            for group, keys in file_groups:
                ws = new_sheet(book, group, PICTURE_COLUMNS, write_only=True)
                for key in keys:
                    pack_rows, considered, _ = read_pack_rows(key, manifests[key], cache, s)
                    info = by_key[key]
                    for r in pack_rows:
                        line = picture_row(key, group, info["licence"], info["category"], r)
                        ws.append([cell(v) for v in line])
                        out_csv.writerow(line)
                        written += 1
                    for record in considered:
                        if record.get("used"):
                            continue                       # already a row above (from rows.jsonl)
                        line = considered_row(key, group, record)
                        ws.append([cell(v) for v in line])
                        out_csv.writerow(line)
                        written += 1
                say(f"  {group}: {len(keys)} packs")
        book.save(os.path.join(out, base + ".xlsx"))
        say(f"  {os.path.join(out, base + '.xlsx')} and .csv")
    say(f"  {written} picture rows")
    return written


def readme_text(rows, picture_count, problems, no_pictures):
    """README.txt for the output folder (plain text for Notepad)."""
    built = [r for r in rows if r["where it's used"] == "ready-made pack" and r["status"] == "built"]
    lines = [
        "MANIFESTS OF THE PICTURE MODEL TRAINING KIT",
        f"Made {time.strftime('%d %B %Y')} by tools/make_manifests.py (toolkit-models repository).",
        "",
        "Files in this folder:",
        "  Sources.xlsx and Sources.csv: one row per organisation or collection found (" + str(len(rows)) + " rows).",
        "    Sources.xlsx has a README sheet, a Summary sheet, an All sources sheet and one sheet for each place a",
        "    collection is used. Sources-Summary.csv is the Summary sheet as a CSV file.",
    ]
    if not no_pictures:
        lines += [
            f"  Pictures.xlsx and Pictures.csv: one row per picture in the {len(built)} published packs "
            f"({picture_count} rows).",
            "    Pictures.xlsx has a README sheet, then one sheet per topic group. (Above about 1 million rows the",
            "    manifest is split into one pair of files per topic group, named 'Pictures - <topic group>'.)",
        ]
    lines += [
        "  README.txt: this file.",
        "",
        "The CSV files are UTF-8 with a byte-order mark, so Excel opens them with the right characters. In each",
        "workbook the first row holds the column names and stays in place when you move down (frozen).",
        "",
        "PICTURES THAT WERE NOT USED",
        "The pack builders up to now did not keep a list of the pictures they looked at and dropped (for a licence",
        "that does not allow sharing, a missing caption, a picture that could not be downloaded, or the pack's",
        "limit). So the Pictures manifest has 'used: no' rows only where a pack recorded them. From now on each pack",
        "built on GitHub also holds considered-<key>.jsonl, a list of every candidate the shared checks saw and the",
        "reason when one was dropped; run the script again after the packs are rebuilt to add those rows.",
        "",
        "THE KIT'S OWN DOWNLOADS",
        "The kit downloads, review collections and permission collections are downloaded and prepared on your",
        "computer, so there is no list of their pictures here. The kit keeps a record of each picture it prepares in",
        "the picture library's data folder: data/<key>-<size>.jsonl (for example data/docci-normal.jsonl), one line",
        "per picture, on your computer.",
    ]
    if problems:
        lines += ["", "WHAT COULD NOT BE READ"] + ["  " + p for p in problems]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
