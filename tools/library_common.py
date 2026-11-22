"""Shared helpers of the three library tools: the master guide book (textbooks/library_guide.py), the size plan
(tools/size_plan.py) and the build health check (tools/health_check.py).

In plain words, this file knows how to:
  - read a web address politely (one request at a time per site, a short pause, a plain User-Agent naming this
    repository, nothing personal sent). For GitHub's API only, the token GitHub Actions gives a workflow
    (GITHUB_TOKEN, or GH_TOKEN) is sent when there is one; without it the public API is used unauthenticated. No
    other secret is ever read;
  - read GitHub releases (every page of releases and of their files) and the catalogues the builds publish
    (packs.json, textbooks.json, manuals.json);
  - read the latest GitHub Actions runs of a workflow and the state of each job (still building, failed,
    succeeded), with the build key taken from the job's name ("build / build (loc_world)" -> "loc_world");
  - write sizes in words ("1.2 GB", decimal units like the ones printed on a drive's box);
  - tell the "stem" of a published file name (its name without a date or a part number), so the newest version of
    each file can be told from older kept versions;
  - put a licence into one of the four classes the guide uses: open, share-alike, personal use, link-only;
  - classify a failure reason in plain words (too many requests 429, refused 403, robots.txt, not found, ...).

Nothing here changes anything anywhere: it only reads.
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

OWNER = "mark-getbraille"
REPO = f"{OWNER}/toolkit-models"
API = "https://api.github.com"
DOWNLOAD = "https://github.com/{repo}/releases/download/{tag}/{name}"
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"
USER_AGENT = "toolkit-models-library-tools/1 (https://github.com/mark-getbraille/toolkit-models)"
PAUSE = 0.5                 # seconds between two requests to the same site
_last = {}                  # {host: time of the last request}


# ====================================================================== reading the web

def token():
    """The token of the GitHub Actions run (GITHUB_TOKEN or GH_TOKEN), or "" when there is none. It is only ever sent
    to api.github.com."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def http_get(url, binary=False, tries=3, timeout=120):
    """The body of url (text, or bytes with binary=True). Raises urllib.error.HTTPError for an answer like 404, after
    trying a busy server (429, 5xx) a few times with a growing pause."""
    host = urllib.parse.urlsplit(url).hostname or ""
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if host == "api.github.com":
        headers["Accept"] = "application/vnd.github+json"
        if token():
            headers["Authorization"] = f"Bearer {token()}"
    for attempt in range(tries):
        wait = PAUSE - (time.monotonic() - _last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt + 1 < tries:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt + 1 < tries:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        finally:
            _last[host] = time.monotonic()
    raise OSError(f"no answer from {url}")


def get_json(url):
    """The JSON answer of url, or None when the address answers "not found" (404) or cannot be read."""
    try:
        return json.loads(http_get(url))
    except (urllib.error.URLError, OSError, ValueError):
        return None


# ====================================================================== GitHub releases and catalogues

def release_file_json(tag, name, repo=REPO):
    """A JSON file published in a release (packs.json in "training-data"), or None when it is not there."""
    return get_json(DOWNLOAD.format(repo=repo, tag=tag, name=name))


def catalogues(repo=REPO):
    """{"packs": packs.json, "textbooks": textbooks.json, "manuals": manuals.json} of the latest releases (None for
    one that is not published or cannot be read)."""
    return {"packs": release_file_json("training-data", "packs.json", repo),
            "textbooks": release_file_json("textbooks", "textbooks.json", repo),
            "manuals": release_file_json("manuals", "manuals.json", repo)}


def list_releases(repo):
    """Every release of a repository (every page), each with ALL its files: GitHub lists only some of a release's
    files with the release, so a release with many files is read again file page by file page. [] when the
    repository cannot be read (a private one without a token)."""
    out = []
    for page in range(1, 50):
        batch = get_json(f"{API}/repos/{repo}/releases?per_page=100&page={page}")
        if not batch:
            break
        out += batch
        if len(batch) < 100:
            break
    for release in out:
        if len(release.get("assets") or []) >= 100:
            files = []
            for page in range(1, 100):
                batch = get_json(f"{API}/repos/{repo}/releases/{release['id']}/assets?per_page=100&page={page}")
                if not batch:
                    break
                files += batch
                if len(batch) < 100:
                    break
            release["assets"] = files or release["assets"]
    return out


DATA_WORDS = ("training-data", "engine-models", "place-packs", "models", "textbooks", "manuals",
              "needs-description", "libretexts", "personal", "publications", "courses", "medicines", "packs")
DATA_EXTENSIONS = (".osmpack", ".zim", ".safetensors", ".onnx", ".gguf", ".pt", ".pth", ".ckpt", ".parquet",
                   ".json.gz")


def is_data_release(release):
    """True when a release holds data (what Program Downloader's "Back up all data" copies to the Data packs folder):
    its tag or name has one of DATA_WORDS, or all its files are data files, or its files are zips with a JSON list
    beside them (the same rule as Program Downloader's releases.is_data_release, in short)."""
    words = f"{release.get('tag_name', '')} {release.get('name') or ''}".lower()
    if any(w in words for w in DATA_WORDS):
        return True
    names = [a["name"].lower() for a in release.get("assets") or []]
    if names and all(n.endswith(DATA_EXTENSIONS) or n.endswith((".sha256", ".txt", ".md")) for n in names):
        return any(n.endswith(DATA_EXTENSIONS) for n in names)
    return bool(names) and any(n.endswith(".zip") for n in names) and any(n.endswith(".json") for n in names)


def workflow_jobs(workflow, max_runs=20, repo=REPO):
    """{build key: {"state", "when", "run", "id", "workflow"}} from the latest runs of a workflow file ("packs.yml"):
    each key's newest job that was not cancelled or skipped. state: "building" (running), "queued" (waiting for a
    machine), "failed" or "succeeded". A job named "build / build (loc_world)" or "build (pub:voa:2026)" gives the
    key in its last brackets; a job building several keys at once ("a+b") gives each. None when the runs cannot be
    read. Runs that were cancelled whole still count for their finished jobs."""
    runs = get_json(f"{API}/repos/{repo}/actions/workflows/{workflow}/runs?per_page={max_runs}")
    if runs is None:
        return None
    jobs = []
    for run in runs.get("workflow_runs", []):
        for page in range(1, 6):
            batch = (get_json(f"{API}/repos/{repo}/actions/runs/{run['id']}/jobs?per_page=100&page={page}")
                     or {}).get("jobs", [])
            for j in batch:
                j["_run"] = run["id"]
            jobs += batch
            if len(batch) < 100:
                break
    return job_states(jobs, workflow)


def job_key(name):
    """The build keys of a job's name: the text in its last brackets, split at "+" ("build (a+b)" -> ["a", "b"]),
    without a top-up "+" or a needs-only "?" at the end ("build (loc_fsa+)" -> ["loc_fsa"]); [] for a job that
    builds nothing (plan, merge)."""
    m = re.search(r"\(([^()]+)\)\s*$", name or "")
    if not m:
        return []
    return [k.strip().rstrip("?") for k in m.group(1).split("+") if k.strip().rstrip("?")]


def job_states(jobs, workflow=""):
    """{key: state} of GitHub job records (see workflow_jobs), the newest job of each key first."""
    state = {}
    for job in sorted(jobs, key=lambda j: j.get("started_at") or j.get("created_at") or "", reverse=True):
        if job.get("conclusion") in ("cancelled", "skipped"):
            continue
        for key in job_key(job.get("name", "")):
            if key in state:
                continue
            when = (job.get("completed_at") or job.get("started_at") or job.get("created_at") or "")[:16]
            if job.get("status") != "completed":
                s = "building" if job.get("status") == "in_progress" else "queued"
            else:
                s = "succeeded" if job.get("conclusion") == "success" else "failed"
            state[key] = {"state": s, "when": when.replace("T", " "), "id": job.get("id"),
                          "run": job.get("_run"), "workflow": workflow}
    return state


def job_log(job_id, repo=REPO):
    """The text of one job's log ("" when it cannot be read: logs need the workflow's token)."""
    try:
        return http_get(f"{API}/repos/{repo}/actions/jobs/{job_id}/logs")
    except (urllib.error.URLError, OSError):
        return ""


# ====================================================================== sizes and file names

def size_words(n):
    """A size in words with decimal units, like a drive's box: 950 -> "950 bytes", 1_200_000 -> "1.2 MB",
    3_400_000_000_000 -> "3.4 TB". None or a negative number -> "size not known"."""
    if n is None or n < 0:
        return "size not known"
    if n < 1000:
        return f"{int(n)} bytes"
    for unit in ("KB", "MB", "GB", "TB", "PB"):
        n /= 1000.0
        if n < 1000 or unit == "PB":
            return f"{n:.1f} {unit}" if n < 100 else f"{n:,.0f} {unit}"
    return f"{n:.1f} PB"


UNITS = {"": 1, "B": 1, "K": 10 ** 3, "KB": 10 ** 3, "M": 10 ** 6, "MB": 10 ** 6, "G": 10 ** 9, "GB": 10 ** 9,
         "T": 10 ** 12, "TB": 10 ** 12}


def parse_size(text):
    """Bytes of a size written in words or as a directory listing shows it: "1.7 GB", "115G", "340 GB",
    "12,345" -> int; None when there is no size. (A listing's "115G" is counted as 115 billion bytes, close enough
    for a plan.)"""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(KB|MB|GB|TB|K|M|G|T|B)?\b", text or "", re.I)
    if not m:
        return None
    return int(float(m.group(1).replace(",", "")) * UNITS[(m.group(2) or "").upper()])


# A kept version's date or pass in a published file name: "name.2026-11-19.zim" (the textbooks' and manuals' kept
# versions), "name (2026-11-19).zip" (Program Downloader's dated copies), "pack.pass2.zip", "needs-pack.v3.zip". A
# month written "name_2026-11.zim" is NOT a version: the news and VOA books are one file per month, each its own piece.
DATE_PARTS = [r"\.\d{4}-\d{2}-\d{2}(?=\.)", r" \(\d{4}-\d{2}-\d{2}\)", r"\.pass\d+", r"\.v\d+(?=\.)"]


def file_stem(name):
    """The name of a published file without its kept-version date, pass or version number and without a part number,
    so the versions of one file share a stem: "nasa_news.2026-11-19.zim" and "nasa_news.2026-11-22.zim" ->
    "nasa_news.zim"; "loc_fsa.pass2.zip.003" -> "loc_fsa.zip"; "voa_1978-04.zim" stays itself (a month's piece)."""
    stem = re.sub(r"\.\d{3}$", "", name)
    for pattern in DATE_PARTS:
        stem = re.sub(pattern, "", stem)
    return stem


def tag_stem(tag):
    """A release tag without a date at its end, so dated releases of one series are counted together:
    "packs-detail-20261112" and "packs-detail-20261122" -> "packs-detail"."""
    return re.sub(r"[-_.](?:\d{8}|\d{4}-\d{2}-\d{2})$", "", tag)


def version_of(name):
    """The date or pass written in a file name, for ordering versions ("2026-11-19", "pass2"); "" when none."""
    m = re.search(r"\d{4}-\d{2}(?:-\d{2})?|\d{8}", name)
    p = re.search(r"\.pass(\d+)", name)
    return (m.group(0).replace("-", "") if m else "") + (f"p{int(p.group(1)):03d}" if p else "")


def newest_only(files):
    """The files of the newest version of each stem. files: [{"name", "size", "release"?, "updated_at"?}]: the
    version is the date or pass in the name, then the release it is in (a later dated release of a series wins), then
    the upload time. A file split into parts keeps all its parts (they share their name, version and release)."""
    best = {}
    for f in files:
        part_of = re.sub(r"\.\d{3}$", "", f["name"])
        ident = (part_of, f.get("release", ""))
        order = (version_of(part_of), f.get("release", ""), f.get("updated_at") or "")
        stem = file_stem(f["name"])
        if stem not in best or order > best[stem][0]:
            best[stem] = (order, ident)
    keep = {v[1] for v in best.values()}
    return [f for f in files if (re.sub(r"\.\d{3}$", "", f["name"]), f.get("release", "")) in keep]


# ====================================================================== licence classes

OPEN, SHARE_ALIKE, PERSONAL, LINK_ONLY = "open", "share-alike", "personal use", "link-only"
CLASS_WORDS = {
    OPEN: "open: may be used and shared by anyone, with credit",
    SHARE_ALIKE: "share-alike: may be shared, but what is made from it keeps the same licence",
    PERSONAL: "personal use: for the owner's own computer only, never shared or sold",
    LINK_ONLY: "link-only: not copied by the builds; the owner opens or fetches it himself (Program Downloader)",
}


def licence_class(kind="", personal=False, link_only=False):
    """One of open, share-alike, personal use, link-only for a licence kind as the catalogues and code write it:
    "open", "no-changes", "permissive", "CC0", "public domain" -> open; "share-alike", "CC BY-SA" -> share-alike;
    "non-commercial", "research", "personal use only" -> personal use; "link-only", "copyright" or unknown ->
    link-only. personal=True or link_only=True wins."""
    if link_only:
        return LINK_ONLY
    if personal:
        return PERSONAL
    k = (kind or "").lower()
    if not k:
        return LINK_ONLY
    if "non-commercial" in k or "noncommercial" in k or "research" in k or "personal" in k or "-nc" in k:
        return PERSONAL
    if "share-alike" in k or "-sa" in k or "sharing" in k:
        return SHARE_ALIKE
    if k.startswith("link") or "copyright" in k:
        return LINK_ONLY
    if any(w in k for w in ("open", "no-changes", "permissive", "cc0", "public domain", "cc by", "pd", "ogl",
                            "apache", "mit")):
        return OPEN
    return LINK_ONLY


# ====================================================================== failure causes

CAUSES = [
    ("too many requests (429): the site asked the build to slow down", r"\b429\b|too many requests|rate.?limit"),
    ("a program part was missing on the build machine (a fix in the workflow)",
     r"ModuleNotFoundError|No module named|command not found"),
    ("refused by the site (403)", r"\b403\b|forbidden|refuses automated|bot check|just a moment"),
    ("robots.txt or an AI-reader block says no", r"robots\.txt|ai-train|ai companies"),
    ("not found (404) or moved", r"\b404\b|not found|\b410\b"),
    ("licence does not allow it", r"licen[cs]e|no derivatives|not repackaged|copyright"),
    ("the site did not answer in time", r"timed? ?out|timeout|did not answer|connection (reset|refused)|\b50[234]\b"),
    ("the build ran out of time or was stopped", r"time limit|exceeded the maximum execution|cancel|was stopped"),
    ("the build machine ran out of disk space", r"no space left"),
    ("no pages or pictures could be read", r"no pages|nothing (was )?(found|built|read)|empty|no pictures"),
    ("it could not be read (PDF or page problem)", r"could not be read|could not be built|pdf"),
]
OTHER_CAUSE = "another error (see the run's log)"


def cause_of(text):
    """The plain-words cause of a failure or left-out reason (CAUSES), or OTHER_CAUSE."""
    for words, pattern in CAUSES:
        if re.search(pattern, text or "", re.I):
            return words
    return OTHER_CAUSE


def failure_line(log):
    """The last thing a failed build printed before GitHub's first "##[error]" line, without its time stamp ("" when
    the log has no error line: then the job's own last lines are only GitHub's clean-up)."""
    lines = (log or "").splitlines()
    end = next((i for i, line in enumerate(lines) if "##[error]" in line), None)
    if end is None:
        return ""
    for line in reversed(lines[:end]):
        text = re.sub(r"^\S+Z ", "", line).strip()
        if text and not text.startswith("##["):
            return text[:300]
    return ""


ERROR_LINE = re.compile(r"error|fail|refus|exception|traceback|\b4\d\d\b|\b5\d\d\b|kill|cancel|time limit|"
                        r"no space", re.I)


def log_cause(log):
    """The cause of a failed job from its log: the first CAUSES pattern found in the error lines (lines that say
    error, failed, refused, an HTTP code ...) of its last 300 lines, so a 429 or 403 said earlier in the build is found
    even when the last line is a general error; OTHER_CAUSE when none matches."""
    tail = "\n".join(line for line in (log or "").splitlines()[-300:] if ERROR_LINE.search(line))
    for words, pattern in CAUSES:
        if re.search(pattern, tail, re.I):
            return words
    return OTHER_CAUSE


# ====================================================================== the Writing Kit's sources (writing-kit branch)

WRITING_REF = "writing-kit"                 # the branch the Writing Kit lives on
WRITING_DIR = "writing-kit/kit"
WRITING_CLASSES = {"OPEN": "open", "SHARE_ALIKE": "share-alike", "PERSONAL": "personal use only"}
SIZE_IN_TEXT = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?(KB|MB|GB|TB)\b")


def writing_kit_texts(repo=REPO, ref=WRITING_REF):
    """{file name: text} of the Writing Kit's source lists on its branch: writing_sources.py, styles.py and every
    sources_*.py, read from raw.githubusercontent.com (the file list from GitHub's contents API). {} when the branch
    cannot be read. The files are only READ as text and parsed (parse_writing_sources): never run."""
    listing = get_json(f"{API}/repos/{repo}/contents/{WRITING_DIR}?ref={ref}") or []
    names = [f["name"] for f in listing if isinstance(f, dict) and
             (f.get("name") in ("writing_sources.py", "styles.py") or
              re.fullmatch(r"sources_\w+\.py", f.get("name", "")))]
    if not names:
        names = ["writing_sources.py", "styles.py"]
    out = {}
    for name in names:
        try:
            out[name] = http_get(RAW.format(repo=repo, ref=ref, path=f"{WRITING_DIR}/{name}"))
        except (urllib.error.URLError, OSError):
            continue
    return out


def parse_writing_sources(texts):
    """[{"key", "name", "class", "style", "size", "size_bytes", "notes"}] of every Source(...) written in the Writing
    Kit's files (texts: {file name: text}), read with Python's own parser without running anything. Names used for
    values (a licence written once at the top of a file, the classes OPEN, SHARE_ALIKE, PERSONAL) are looked up in
    the same file. The style is the source's own "style", else styles.py's BY_SOURCE; the size is its own "size" or
    the first size its notes state ("1.7 GB"), else ""."""
    import ast
    styles = {}
    if "styles.py" in texts:
        try:
            for node in ast.walk(ast.parse(texts["styles.py"])):
                if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BY_SOURCE" for t in node.targets):
                    styles = ast.literal_eval(node.value)
        except (SyntaxError, ValueError):
            styles = {}
    found = []
    for fname, text in texts.items():
        if fname == "styles.py":
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        consts = dict(WRITING_CLASSES)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets[0].elts if isinstance(node.targets[0], ast.Tuple) else node.targets
                values = node.value.elts if isinstance(node.value, ast.Tuple) else [node.value]
                for t, v in zip(targets, values):
                    if isinstance(t, ast.Name) and isinstance(v, ast.Constant) and isinstance(v.value, str):
                        consts.setdefault(t.id, v.value)

        def value(v):
            """The text of a keyword's value ("" when it is not a plain text or a known name)."""
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                return v.value
            if isinstance(v, ast.Name):
                return consts.get(v.id, "")
            if isinstance(v, ast.BinOp):
                return value(v.left) + value(v.right)
            return ""

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and (getattr(node.func, "id", "") == "Source" or
                                               getattr(node.func, "attr", "") == "Source"):
                kw = {k.arg: value(k.value) for k in node.keywords if k.arg}
                if not kw.get("key"):
                    continue
                size = kw.get("size") or ""
                if not size:
                    m = SIZE_IN_TEXT.search(f"{kw.get('name', '')} {kw.get('notes', '')}")
                    size = f"{m.group(1)} {m.group(2)}" if m else ""
                found.append({"key": kw["key"], "name": kw.get("name", kw["key"]),
                              "class": kw.get("licence_class", ""), "style": kw.get("style") or
                              styles.get(kw["key"], ""), "size": size, "size_bytes": parse_size(size) if size else None,
                              "notes": " ".join(kw.get("notes", "").split())[:400], "file": fname})
    seen, out = set(), []
    for s in found:
        if s["key"] not in seen:
            seen.add(s["key"])
            out.append(s)
    return out


def write_text(path, lines):
    """Write lines (a list of strings) as a UTF-8 text file with Windows line ends, so Notepad shows it well."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")


def write_json(path, data):
    """Write data as a JSON file (UTF-8, indented)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
