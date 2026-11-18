"""Build a Review Pack: get the pictures that need a description ready for the people who will describe them.

The training packs' builders set aside every picture that passed all of a pack's rules but had no good description
(packs/build_packs.py needs_description); they are published per collection as needs-<key>.vN.zip in this
repository's release "needs-description", listed in needs-manifest.json. A REVIEW PACK is a folder on this computer
(and a zip of it) that holds, for the chosen collections:
  - the pictures, in a "Describe pictures" workspace (describing.json): every picture "new", a review collection, so
    nothing is ever trained on until a person writes its description and marks it checked;
  - two independent DRAFT descriptions per picture, written by two picture models from the PICTURE ALONE (Qwen3-VL 8B
    and InternVL 3.5 8B by default; Florence-2 large or your own trained describer can be chosen instead), so the
    drafts say only what can be seen (kit\\prepare_data.py write_drafts);
  - kept apart and clearly labelled, what is known about the picture: the collection's hints (its title, the poor
    description, tags, place) and the TEXT GATHERED FROM THE PICTURE'S WEB PAGE ("page_text"): the picture's alt
    text, its title attribute, its caption (figcaption), the nearest heading, the paragraphs around or about it,
    the page's own summary, and the structured record where the site has an open interface (Wikimedia Commons:
    the file's description, caption and categories from its API, not from the web page). Each field keeps where it
    came from ("page_text_sources"). This text may be under copyright: it is kept ON THIS COMPUTER ONLY, in the
    review pack, and is never uploaded or published (the pack's READ ME says so);
  - optionally (off unless asked for), a "suggested combined description": the first model writes one description
    with the page text and hints as context, marked as needing a person's check ("draft_suggested");
  - review-pack.jsonl: every picture as one line with the same fields, for the reviewers' own database, whose job is
    to merge the alt text, the AI drafts and the page text into one good description for training.

Being polite to other people's websites: every request names this program (USER_AGENT, never the person); robots.txt
is read for each site and obeyed (a page or picture it forbids is not fetched, and the reason is noted); at most one
request every PER_SITE_SECONDS seconds per site; a busy answer (429, 5xx) is waited out and tried again a few times;
pages are kept in a cache (.page-cache) so a page is never fetched twice. The Wikimedia Commons API is used for
Commons files (Commons asks programs to use its API rather than its web pages; its robots.txt is for crawlers of
the web pages), with the same pace and name.

Stopping and carrying on: every step remembers what is done (.review-pack.json, the downloads' partial files, the
workspace's entries), so running it again carries on where it stopped. A picture that fails is noted in
review-pack-problems.txt and the work goes on.

Command line (kit\\run_prepare.cmd runs it through prepare_data.py: prepare_data.py PACK review-pack ...):
    python review_pack.py PACK_FOLDER --keys loc_fsa,commons_valued [--zips FOLDER] [--engines qwen,internvl]
        [--no-page-text] [--suggest] [--no-drafts] [--library FOLDER]
    python review_pack.py --list                       (the collections in needs-manifest.json, with their sizes)
Lines "N of M" move the program's progress bar; lines starting "Finished" or "STOPPED" end the work.
"""

import argparse
import datetime
import hashlib
import html
import html.parser
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import describe_package as package  # noqa: E402
import needs_workspace  # noqa: E402

NEEDS_URL = "https://github.com/mark-getbraille/toolkit-models/releases/download/needs-description/"
USER_AGENT = "PictureModelTrainingKit-ReviewPack/1 (+https://github.com/mark-getbraille/toolkit-models)"
PER_SITE_SECONDS = 3.0           # at most one request every this many seconds to one website
TRIES = 4
STATE_FILE = ".review-pack.json"
DOWNLOADS = ".downloads"         # needs zips being downloaded (and kept, so a stopped download carries on)
PAGE_CACHE = ".page-cache"       # the web pages read, so none is fetched twice (kept on this computer only)
EXPORT_FILE = "review-pack.jsonl"
PROBLEMS_FILE = "review-pack-problems.txt"
README_FILE = "READ ME - REVIEW PACK.txt"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
DEFAULT_ENGINES = ("qwen", "internvl")   # two independent drafts by default
PAGE_FIELDS = ("alt", "title", "caption", "heading", "nearby", "summary", "api", "categories")
MOST_TEXT = 1200                 # characters kept of each gathered field
SUGGEST_GUIDE = ("Below is what the picture's collection and its web page say about it. It may be wrong, about "
                 "another picture on the same page, or incomplete. Look at the picture and write ONE accurate "
                 "description for someone who cannot see it: say what can be seen; use names, places and dates from "
                 "the text only where the picture agrees with them; do not copy the text's wording; do not mention "
                 "the text.")

README = """READ ME: this review pack

This folder is a review pack made by Build a Review Pack (Dataset Preparation) on {date}, from these collections of
pictures that need a description: {keys}.

What is in it
- The pictures, with describing.json: open this folder in Describe pictures (Workspace folder) to describe them.
  Every picture starts as "new". Nothing here is ever used for training until a person writes the description and
  marks it checked.
- For each picture, two draft descriptions written by two picture models from the picture alone ({engines}). They
  are drafts: they can be wrong. Check every word against the picture.
- Kept apart, what is known about the picture: the collection's hints and the text gathered from its web page (alt
  text, caption, heading, nearby paragraphs, the record from the site's open interface). This text helps with names,
  places and dates, but it may describe another picture or be wrong, and it may be under copyright.
- review-pack.jsonl: the same, one line per picture, for the reviewers' database (the fields are explained in
  "HOW TO DESCRIBE PICTURES THAT NEED A DESCRIPTION.txt" in the training kit).
- review-pack-problems.txt: pictures or pages that could not be fetched, and why.

PLEASE NOTE: the text gathered from web pages is for reviewing on your own computers only. Do not upload, publish
or share it beyond your reviewers. The pictures' credits and licences are in each picture's entry and in the JSONL
file; keep them with the pictures.
"""


def say(text=""):
    """Write one line at once (Dataset Preparation reads the lines as they come)."""
    print(text, flush=True)


def now():
    """The time now in UTC, as text."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean(text):
    """Text with its spaces tidied."""
    return " ".join(html.unescape(str(text or "")).split())


def cut(text, most=MOST_TEXT):
    """Text cut to at most most characters, at a word."""
    text = clean(text)
    return text if len(text) <= most else text[:most].rsplit(" ", 1)[0] + " ..."


# ----------------------------------------------------------------- polite downloads

class Refused(Exception):
    """A website's robots.txt does not allow this program to fetch the address."""


def plain_open(url, headers=None, timeout=60):
    """Fetch url with this program's name: (status, body bytes, headers dict). An HTTP error gives its status."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as r:  # noqa: S310 - http(s) addresses only
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read() if hasattr(e, "read") else b"", dict(e.headers or {})


class Polite:
    """Downloads that keep to each website's robots.txt and pace (see the module docstring).

    opener(url, headers) -> (status, bytes, headers) does the fetching (plain_open; the tests give a made-up one);
    clock and sleep tell and pass the time (the tests give made-up ones)."""

    def __init__(self, opener=None, clock=time.monotonic, sleep=time.sleep, per_site=PER_SITE_SECONDS):
        """Start with no site visited yet."""
        self.opener = opener or (lambda url, headers=None: plain_open(url, headers))
        self.clock, self.sleep, self.per_site = clock, sleep, per_site
        self.last, self.robots = {}, {}

    def wait_for(self, host):
        """Wait until this site may be asked again (one request every per_site seconds)."""
        if host in self.last:
            left = self.last[host] + self.per_site - self.clock()
            if left > 0:
                self.sleep(left)
        self.last[host] = self.clock()

    def allowed(self, url):
        """True when the site's robots.txt lets this program fetch url (read once per site). A robots.txt that
        cannot be read because the site refuses (401, 403) or does not answer counts as "no"; one that is simply
        missing (404 and the like) as "yes", as robots.txt asks."""
        parts = urllib.parse.urlsplit(url)
        site = f"{parts.scheme}://{parts.netloc}"
        if site not in self.robots:
            rules = urllib.robotparser.RobotFileParser()
            try:
                self.wait_for(parts.netloc)
                status, body, _ = self.opener(site + "/robots.txt", None)
            except Exception:  # noqa: BLE001 - no answer: do not fetch from this site
                status, body = 0, b""
            if status == 200:
                rules.parse(body.decode("utf-8", "replace").splitlines())
            elif status in (401, 403) or status == 0 or status >= 500:
                rules.disallow_all = True
            else:
                rules.allow_all = True
            self.robots[site] = rules
        return self.robots[site].can_fetch(USER_AGENT, url)

    def get(self, url, api=False):
        """The body of url (bytes), waiting for the site's pace and trying again when it is busy. Raises Refused when
        robots.txt forbids it (api=True: an open interface meant for programs, see the module docstring), and
        RuntimeError when it never came."""
        if not api and not self.allowed(url):
            raise Refused(f"robots.txt of {urllib.parse.urlsplit(url).netloc} does not allow it")
        host = urllib.parse.urlsplit(url).netloc
        answer = "no answer"
        for attempt in range(TRIES):
            self.wait_for(host)
            try:
                status, body, headers = self.opener(url, None)
            except Exception as e:  # noqa: BLE001 - tried again
                answer = type(e).__name__
                self.sleep((5, 15, 30, 0)[attempt])
                continue
            if status == 200:
                return body
            answer = f"the site answered {status}"
            if status not in (429, 500, 502, 503, 504):
                break
            after = str((headers or {}).get("Retry-After", ""))
            self.sleep(min(int(after), 120) if after.isdigit() else (10, 30, 60, 0)[attempt])
        raise RuntimeError(answer)


# ----------------------------------------------------------------- the needs zips

def read_manifest(fetch=None):
    """The published needs-manifest.json ({key: {"file", "count", "size", "category", ...}}); while it is being
    replaced, needs-manifest.next.json. fetch(url) -> bytes (plain_open by default)."""
    def fetch_plain(url):
        """The body of url, or b"" when the answer is not 200."""
        status, body, _headers = plain_open(url)
        return body if status == 200 else b""
    fetch = fetch or fetch_plain
    for name in ("needs-manifest.json", "needs-manifest.next.json"):
        try:
            body = fetch(NEEDS_URL + name)
        except Exception:  # noqa: BLE001 - try the other name
            body = b""
        if body:
            return json.loads(body.decode("utf-8"))
    return {}


def size_words(size):
    """A size in plain words: "12 MB", "1.3 GB"."""
    size = int(size or 0)
    return f"{size / 1e9:.1f} GB" if size >= 1e9 else f"{max(1, round(size / 1e6))} MB"


def list_lines(manifest):
    """One plain line per collection of the manifest: "loc_fsa: 1,200 pictures, 380 MB, open, 2026-11-18"."""
    return [f"{key}: {entry.get('count', 0):,} pictures, {size_words(entry.get('size'))}, "
            f"{entry.get('category', 'open')}, {entry.get('date', '')}" for key, entry in sorted(manifest.items())]


def download_resumable(url, path, size=0, sha256="", opener=None):
    """Download url to path, carrying on from a partial path + ".part" (a Range request), and check its SHA-256.
    Returns path. A file that does not match is removed (so the next run starts it again) and RuntimeError says so."""
    if os.path.exists(path) and (not sha256 or file_sha256(path) == sha256):
        return path
    part = path + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if size and have >= size:
        have = 0
        os.remove(part)
    opener = opener or (lambda u, headers=None: plain_open(u, headers, timeout=600))
    status, body, _ = opener(url, {"Range": f"bytes={have}-"} if have else None)
    if status not in (200, 206):
        raise RuntimeError(f"the download of {os.path.basename(path)} was refused ({status})")
    with open(part, "ab" if status == 206 else "wb") as f:
        f.write(body)
    if sha256 and file_sha256(part) != sha256:
        os.remove(part)
        raise RuntimeError(f"{os.path.basename(path)} did not download whole; start again to fetch it afresh")
    os.replace(part, path)
    return path


def file_sha256(path):
    """The SHA-256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def zips_in(folder):
    """{key: path} of the needs zips in a folder (needs-<key>.vN.zip; the newest version of each)."""
    found = {}
    for name in sorted(os.listdir(folder)):
        m = re.match(r"^needs-(.+?)(?:\.v(\d+))?\.zip$", name)
        if m:
            version = int(m.group(2) or 0)
            if m.group(1) not in found or version >= found[m.group(1)][0]:
                found[m.group(1)] = (version, os.path.join(folder, name))
    return {k: p for k, (_v, p) in found.items()}


# ----------------------------------------------------------------- reading a web page

class PageParser(html.parser.HTMLParser):
    """Reads a web page into a flat list of blocks, in page order: headings, paragraphs, pictures (with their
    attributes and the figure they are in), figure captions and table captions; plus the page's own summary (meta
    description) and its structured data (JSON-LD). Scripts, styles and navigation are skipped."""

    TEXT_TAGS = {"p": "p", "li": "p", "dd": "p", "blockquote": "p", "figcaption": "caption", "caption": "caption",
                 "h1": "heading", "h2": "heading", "h3": "heading", "h4": "heading", "h5": "heading", "h6": "heading"}
    SKIP_TAGS = {"script", "style", "nav", "header", "footer", "noscript", "svg", "form", "button"}

    def __init__(self):
        """An empty page."""
        super().__init__(convert_charrefs=True)
        self.blocks, self.meta, self.json_ld = [], {}, []
        self.open_text, self.skip, self.figures, self.in_json = None, 0, [], False

    def handle_starttag(self, tag, attrs):
        """A tag opens: start a block, note a picture, or start skipping."""
        attrs = {k.lower(): v or "" for k, v in attrs}
        if tag in self.SKIP_TAGS:
            if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
                self.in_json, self.json_text = True, []
            else:
                self.skip += 1
            return
        if tag == "figure":
            self.figures.append(len(self.blocks))
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key in ("description", "og:description", "twitter:description", "og:title"):
                self.meta.setdefault(key, clean(attrs.get("content")))
        elif tag == "img" and not self.skip:
            self.blocks.append({"kind": "img", "attrs": attrs, "figure": self.figures[-1] if self.figures else None})
        elif tag in self.TEXT_TAGS and not self.skip and self.open_text is None:
            self.open_text = {"kind": self.TEXT_TAGS[tag], "tag": tag, "text": [],
                              "figure": self.figures[-1] if self.figures else None}

    def handle_endtag(self, tag):
        """A tag closes: finish its block, or stop skipping."""
        if tag == "script" and self.in_json:
            self.in_json = False
            try:
                self.json_ld.append(json.loads("".join(self.json_text)))
            except ValueError:
                pass
            return
        if tag in self.SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if tag == "figure" and self.figures:
            self.figures.pop()
        if self.open_text is not None and tag == self.open_text["tag"]:
            text = clean(" ".join(self.open_text["text"]))
            if text:
                self.blocks.append({"kind": self.open_text["kind"], "text": text, "figure": self.open_text["figure"]})
            self.open_text = None

    def handle_data(self, data):
        """Text: into the open block (or the JSON-LD being read)."""
        if self.in_json:
            self.json_text.append(data)
        elif self.open_text is not None and not self.skip:
            self.open_text["text"].append(data)


def picture_tokens(*addresses):
    """The distinctive parts of picture addresses and names, for finding the picture on its page: the file name
    without size marks ("1280px-", "_large") and its long letter-and-number runs."""
    tokens = set()
    for address in addresses:
        base = urllib.parse.unquote(urllib.parse.urlsplit(address or "").path.rsplit("/", 1)[-1]).lower()
        base = re.sub(r"^\d+px-", "", base)
        stem = re.sub(r"\.(jpe?g|png|gif|webp|tiff?)$", "", base)
        stem = re.sub(r"[_-](large|medium|small|thumb\w*|full|preview|\d+x\d+)$", "", stem)
        if len(stem) >= 4 and stem not in ("default", "image", "picture", "full", "thumbnail", "proxyhires"):
            tokens.add(stem)
        tokens.update(t for t in re.findall(r"[a-z0-9]{6,}", urllib.parse.unquote(address or "").lower())
                      if re.search(r"\d", t))
    return tokens


def find_picture(blocks, tokens):
    """The index of the picture block that matches tokens (its src, srcset, data-src or alt names one), or None."""
    best, best_score = None, 0
    for i, block in enumerate(blocks):
        if block["kind"] != "img":
            continue
        where = urllib.parse.unquote(" ".join(block["attrs"].get(k, "") for k in ("src", "srcset", "data-src",
                                                                                 "data-original"))).lower()
        score = sum(len(t) for t in tokens if t in where)
        if score > best_score:
            best, best_score = i, score
    return best


def extract_page_text(page, picture_addresses=(), page_url=""):
    """What a web page says about one picture: {field: text} for "alt" (the picture's alt text), "title" (its title
    attribute), "caption" (its figcaption, or a caption right beside it), "heading" (the nearest heading above it),
    "nearby" (the paragraphs right around it, and any that refer to it by its figure number or caption), "summary"
    (the page's own description) and "api" (structured data the page gives, JSON-LD). picture_addresses: the
    picture's web address and file name, to find it on the page; when it is not found, only "summary" and the page's
    first heading are given. Empty fields are left out."""
    parser = PageParser()
    try:
        parser.feed(page if isinstance(page, str) else page.decode("utf-8", "replace"))
        parser.close()
    except Exception:  # noqa: BLE001 - a broken page gives what was read so far
        pass
    blocks, out = parser.blocks, {}
    summary = parser.meta.get("description") or parser.meta.get("og:description") or ""
    if summary:
        out["summary"] = cut(summary, 600)
    structured = structured_text(parser.json_ld)
    if structured:
        out["api"] = structured
    at = find_picture(blocks, picture_tokens(*picture_addresses))
    if at is None:
        heading = next((b["text"] for b in blocks if b["kind"] == "heading"), "")
        if heading:
            out["heading"] = cut(heading, 300)
        return out
    attrs = blocks[at]["attrs"]
    if clean(attrs.get("alt")):
        out["alt"] = cut(attrs["alt"], 600)
    if clean(attrs.get("title")):
        out["title"] = cut(attrs["title"], 300)
    figure = blocks[at]["figure"]
    caption = next((b["text"] for b in blocks if b["kind"] == "caption" and figure is not None
                    and b["figure"] == figure), "")
    if not caption:                         # a caption block right after (or before) the picture
        for j in (at + 1, at - 1):
            if 0 <= j < len(blocks) and blocks[j]["kind"] == "caption":
                caption = blocks[j]["text"]
                break
    if caption:
        out["caption"] = cut(caption, 600)
    heading = next((blocks[j]["text"] for j in range(at, -1, -1) if blocks[j]["kind"] == "heading"), "")
    if heading:
        out["heading"] = cut(heading, 300)
    nearby = []
    for j in list(range(at + 1, min(len(blocks), at + 4))) + list(range(at - 1, max(-1, at - 4), -1)):
        if blocks[j]["kind"] == "heading" or blocks[j]["kind"] == "img":
            continue
        if blocks[j]["kind"] == "p" and blocks[j]["text"] not in nearby and len(nearby) < 2:
            nearby.append(blocks[j]["text"])
    figure_number = re.match(r"^\s*((fig(ure)?|plate|abb(ildung)?)\.?\s*\d+[a-z]?)", caption, re.I)
    if figure_number:                       # paragraphs elsewhere that refer to "Figure 3"
        mark = re.escape(figure_number.group(1).lower())
        nearby += [b["text"] for b in blocks if b["kind"] == "p" and re.search(mark, b["text"].lower())
                   and b["text"] not in nearby][:2]
    if nearby:
        out["nearby"] = cut(" ".join(nearby))
    return out


def structured_text(records):
    """The descriptive words of a page's JSON-LD records (name, description, caption, abstract), as one text."""
    found = []

    def walk(node):
        """Collect the descriptive fields of every record inside node."""
        if isinstance(node, dict):
            for key in ("name", "headline", "description", "caption", "abstract"):
                value = node.get(key)
                if isinstance(value, str) and clean(value) and clean(value) not in found:
                    found.append(clean(value))
            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
    walk(records)
    return cut(" ".join(found)) if found else ""


def commons_title(page_url):
    """The "File:..." title of a Wikimedia Commons file page address, or ""."""
    parts = urllib.parse.urlsplit(page_url or "")
    if parts.netloc.endswith("commons.wikimedia.org") and parts.path.startswith("/wiki/File:"):
        return urllib.parse.unquote(parts.path[len("/wiki/"):]).replace("_", " ")
    return ""


def commons_text(polite, title):
    """What Commons' API says about a file: {"api": its description, "caption": its structured caption,
    "categories": its categories}, with where each came from."""
    query = urllib.parse.urlencode({"action": "query", "format": "json", "titles": title, "prop": "imageinfo",
                                    "iiprop": "extmetadata", "iiextmetadatalanguage": "en", "maxlag": 5,
                                    "iiextmetadatafilter": "ImageDescription|ObjectName|Categories|DateTimeOriginal"})
    data = json.loads(polite.get(f"{COMMONS_API}?{query}", api=True).decode("utf-8"))
    pages = list(((data.get("query") or {}).get("pages") or {}).values())
    if not pages:
        return {}, {}
    page = pages[0]
    meta = ((page.get("imageinfo") or [{}])[0].get("extmetadata")) or {}
    value = lambda k: clean(re.sub(r"<[^>]+>", " ", str((meta.get(k) or {}).get("value") or "")))   # noqa: E731
    out, sources = {}, {}
    described = " ".join(t for t in (value("ObjectName"), value("ImageDescription")) if t)
    if described:
        out["api"], sources["api"] = cut(described), "Wikimedia Commons API (file description)"
    if value("Categories"):
        out["categories"], sources["categories"] = cut(value("Categories").replace("|", "; "), 600), \
            "Wikimedia Commons API (categories)"
    if page.get("pageid"):
        ids = urllib.parse.urlencode({"action": "wbgetentities", "format": "json", "ids": f"M{page['pageid']}",
                                      "props": "labels", "languages": "en"})
        entities = json.loads(polite.get(f"{COMMONS_API}?{ids}", api=True).decode("utf-8")).get("entities", {})
        label = (((entities.get(f"M{page['pageid']}") or {}).get("labels") or {}).get("en") or {}).get("value", "")
        if clean(label):
            out["caption"], sources["caption"] = cut(label, 600), "Wikimedia Commons API (structured caption)"
    return out, sources


def gather_page_text(polite, entry, cache_folder):
    """({field: text}, {field: where it came from}, outcome) for one picture's entry (its page_url and source_url).
    outcome is "yes", or why nothing was gathered ("refused by robots.txt ...", "no web page", "failed: ...")."""
    page_url = entry.get("page_url", "")
    if not page_url.startswith(("http://", "https://")):
        return {}, {}, "no web page"
    title = commons_title(page_url)
    try:
        if title:
            fields, sources = commons_text(polite, title)
            return fields, sources, "yes"
        os.makedirs(cache_folder, exist_ok=True)
        cached = os.path.join(cache_folder, hashlib.sha1(page_url.encode("utf-8")).hexdigest() + ".html")
        if os.path.exists(cached):
            with open(cached, "rb") as f:
                body = f.read()
        else:
            body = polite.get(page_url)
            with open(cached + ".new", "wb") as f:
                f.write(body)
            os.replace(cached + ".new", cached)
        fields = extract_page_text(body, (entry.get("source_url", ""), entry.get("needs_name", "")), page_url)
        return fields, {k: page_url for k in fields}, "yes"
    except Refused as e:
        return {}, {}, f"refused by {e}"
    except Exception as e:  # noqa: BLE001 - noted; the other pictures go on
        return {}, {}, f"failed: {str(e)[:150] or type(e).__name__}"


# ----------------------------------------------------------------- building the pack

class State:
    """What is done already (.review-pack.json in the pack folder), saved after each change."""

    def __init__(self, folder):
        """Read the state of the pack in folder (empty when new)."""
        self.path = os.path.join(folder, STATE_FILE)
        try:
            with open(self.path, encoding="utf-8") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            self.data = {}
        self.data.setdefault("zips", {})

    def save(self):
        """Write the state safely (a new file first)."""
        with open(self.path + ".new", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1)
        os.replace(self.path + ".new", self.path)


def note_problem(folder, text):
    """Add a line to review-pack-problems.txt (a picture or page that failed, and why)."""
    with open(os.path.join(folder, PROBLEMS_FILE), "a", encoding="utf-8") as f:
        f.write(f"{now()}  {text}\n")


def get_zips(folder, keys, zips_folder=None, manifest=None, opener=None, report=say):
    """{key: path of its needs zip}: from zips_folder when given (zips already downloaded), else downloaded from
    the release (resumable, checked by SHA-256) into the pack's .downloads folder."""
    found = {}
    if zips_folder:
        found = zips_in(zips_folder)
        if keys != ["all"]:
            found = {k: p for k, p in found.items() if k in keys}
        return found
    manifest = read_manifest() if manifest is None else manifest
    wanted = sorted(manifest) if keys == ["all"] else [k for k in keys if k in manifest]
    for missing in [k for k in keys if k != "all" and k not in manifest]:
        report(f"{missing}: no pictures that need a description are published for this collection.")
    os.makedirs(os.path.join(folder, DOWNLOADS), exist_ok=True)
    for number, key in enumerate(wanted, 1):
        entry = manifest[key]
        report(f"Downloading collection {number} of {len(wanted)}: {key} ({size_words(entry.get('size'))})")
        path = os.path.join(folder, DOWNLOADS, entry["file"])
        try:
            found[key] = download_resumable(NEEDS_URL + entry["file"], path, entry.get("size", 0),
                                            entry.get("sha256", ""), opener)
        except Exception as e:  # noqa: BLE001 - this collection waits; the others go on
            report(f"  {key} could not be downloaded: {e}")
            note_problem(folder, f"{key}: the needs zip could not be downloaded: {e}")
    return found


def add_collections(folder, zips, polite, state, library=None, report=say):
    """Import each needs zip into the pack's workspace once (pictures already there are not added twice) and
    download the pictures that came with only an address (politely)."""
    for number, (key, path) in enumerate(sorted(zips.items()), 1):
        digest = file_sha256(path)
        if state.data["zips"].get(key) == digest:
            continue
        report(f"Adding collection {number} of {len(zips)}: {key}")

        def fetch(url):
            """One picture with only an address, fetched politely (robots.txt kept)."""
            return polite.get(url)
        report("  " + needs_workspace.open_needs_zip(path, folder, fetch=fetch, say=report, library=library))
        for row in needs_workspace.pending(folder):
            note_problem(folder, f"{row.get('url')}: still waiting ({row.get('failed', 'not fetched yet')})")
        state.data["zips"][key] = digest
        state.save()


def add_page_text(folder, polite, report=say):
    """Gather the web-page text of every picture that has a page and none yet (see gather_page_text)."""
    workspace = package.open_workspace(folder)
    names = [n for n in sorted(workspace.pictures, key=str.lower)
             if workspace.entry(n).get("page_url") and not workspace.entry(n).get("page_text_done")]
    if not names:
        report("Every picture's web page has been read before (or there are none).")
        return
    report(f"Reading the web pages of {package.plural(len(names), 'picture')} (one request every "
           f"{PER_SITE_SECONDS:g} seconds per website, robots.txt kept).")
    gathered = 0
    for number, name in enumerate(names, 1):
        entry = workspace.entry(name)
        entry.setdefault("needs_name", name)
        fields, sources, outcome = gather_page_text(polite, entry, os.path.join(folder, PAGE_CACHE))
        if fields:
            entry["page_text"], entry["page_text_sources"] = fields, sources
            gathered += 1
        entry["page_text_done"] = outcome
        if outcome != "yes":
            note_problem(folder, f"{name}: page text not gathered ({outcome}): {entry.get('page_url')}")
        if number % 10 == 0 or number == len(names):
            workspace.save()
            report(f"  {number} of {len(names)} web pages read")
    workspace.save()
    report(f"Page text gathered for {package.plural(gathered, 'picture')}.")


def context_of(entry):
    """The collection's hints and the gathered page text of a picture, as labelled lines (for the suggestion)."""
    lines = [f"Collection's notes: {entry['hint']}"] if entry.get("hint") else []
    names = {"alt": "Alt text", "title": "Picture title", "caption": "Caption", "heading": "Heading above it",
             "nearby": "Text near it", "summary": "Page summary", "api": "Record", "categories": "Categories"}
    lines += [f"{names[k]}: {v}" for k, v in (entry.get("page_text") or {}).items() if k in names and v]
    return "\n".join(lines)


def suggest(folder, report=say):
    """The optional "suggested combined description": Qwen3-VL 8B looks at each picture with its hints and page text
    and writes one description, kept as "draft_suggested" (never the starting description, never trained on)."""
    import prepare_data
    import train
    workspace = package.open_workspace(folder)
    names = [n for n in prepare_data.new_pictures(workspace)
             if not workspace.entry(n).get("draft_suggested") and context_of(workspace.entry(n))]
    if not names:
        report("No picture needs a suggested description.")
        return
    report(f"Writing suggested descriptions from the page text for {package.plural(len(names), 'picture')}.")
    engine = prepare_data.Engine("qwen")
    try:
        for number, name in enumerate(names, 1):
            entry = workspace.entry(name)
            try:
                img = prepare_data.open_upright(workspace.path(name))
                img.thumbnail((1536, 1536))
                text = engine.ask(img, f"{package.question_of(workspace, name)} {SUGGEST_GUIDE}\n\n{context_of(entry)}",
                                  train.SYSTEM)
                entry["draft_suggested"] = prepare_data.tidy(text)
            except Exception as e:  # noqa: BLE001 - noted; the others go on
                note_problem(folder, f"{name}: no suggested description ({str(e)[:150]})")
            if number % 10 == 0 or number == len(names):
                workspace.save()
                report(f"  {number} of {len(names)} suggested descriptions")
    finally:
        engine.close()
    workspace.save()


def write_drafts(folder, engines, report=say):
    """Two (or more) independent drafts per picture from the picture alone (prepare_data.write_drafts, without
    combining them, so each model's own words stay apart). Without the graphics card it says so and goes on."""
    import prepare_data
    text = prepare_data.write_drafts(folder, engines, combine=False)
    report(text)
    return not text.startswith("STOPPED")


def finish_pack(folder, keys, engines, report=say):
    """Write the pack's READ ME, review-pack.jsonl and the zip of the pack (beside the folder; the downloads and the
    page cache are left out of the zip)."""
    with open(os.path.join(folder, README_FILE), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(README.format(date=now()[:10], keys=", ".join(keys), engines=" and ".join(engines) or "none"))
    report(needs_workspace.export_jsonl(folder, os.path.join(folder, EXPORT_FILE)))
    target = os.path.abspath(folder).rstrip("\\/") + ".zip"
    with zipfile.ZipFile(target + ".new", "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in (DOWNLOADS, PAGE_CACHE, needs_workspace.STAGING)]
            for name in files:
                if name.endswith((".new", ".part")) or name == STATE_FILE:
                    continue
                path = os.path.join(base, name)
                z.write(path, os.path.relpath(path, folder))
    os.replace(target + ".new", target)
    report(f"The review pack is in {folder} and zipped as {target}. Its page text is for your own computers only.")
    return target


def build(folder, keys, zips_folder=None, engines=("qwen", "internvl"), page_text=True, drafts=True,
          suggest_too=False, library=None, polite=None, manifest=None, opener=None, report=say):
    """Build (or carry on building) the review pack in folder; returns a plain summary (see the module docstring)."""
    os.makedirs(folder, exist_ok=True)
    workspace = package.make_workspace(folder, "Review pack")
    workspace.data.update(review_only=True, never_for_picture_making=True, review_source="review-pack")
    workspace.save()
    state = State(folder)
    polite = polite or Polite()
    zips = get_zips(folder, list(keys), zips_folder, manifest, opener, report)
    if not zips:
        return "STOPPED: no needs zip was found for the chosen collections."
    add_collections(folder, zips, polite, state, library, report)
    if page_text:
        add_page_text(folder, polite, report)
    if drafts and engines:
        if write_drafts(folder, list(engines), report) and suggest_too:
            suggest(folder, report)
    finish_pack(folder, sorted(zips), list(engines) if drafts else [], report)
    counts = package.counts(package.open_workspace(folder))
    return (f"Finished: the review pack has {package.plural(counts['all'], 'picture')}, {counts['new']} waiting for "
            "a description. Nothing is trained on until a person describes each picture and marks it checked.")


def main(argv=None):
    """The command line (see the module docstring)."""
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--list"]:
        for line in list_lines(read_manifest()) or ["No collections are published yet."]:
            say(line)
        return 0
    parser = argparse.ArgumentParser(description="Build a review pack of pictures that need a description.")
    parser.add_argument("folder")
    parser.add_argument("--keys", default="all", help="collection keys, separated by commas, or all")
    parser.add_argument("--zips", default="", help="a folder of needs zips already downloaded")
    parser.add_argument("--engines", default="qwen,internvl")
    parser.add_argument("--no-page-text", action="store_true")
    parser.add_argument("--no-drafts", action="store_true")
    parser.add_argument("--suggest", action="store_true")
    parser.add_argument("--library", default="")
    args = parser.parse_args(argv)
    keys = [k.strip() for k in args.keys.split(",") if k.strip()] or ["all"]
    try:
        text = build(args.folder, keys, args.zips or None, [e for e in args.engines.split(",") if e.strip()],
                     not args.no_page_text, not args.no_drafts, args.suggest, args.library or None)
    except Exception as e:  # noqa: BLE001 - said in plain words
        text = f"STOPPED: {str(e).splitlines()[0][:300] if str(e) else type(e).__name__}"
    say(text)
    return 1 if text.startswith("STOPPED") else 0


if __name__ == "__main__":
    sys.exit(main())
