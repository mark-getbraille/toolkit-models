"""Build the manual and instruction collections of the Digital Accessibility Toolkit, one category at a time
(manuals/categories.py), and write each as a small gzipped JSON index with its manifest. The workflow
.github/workflows/manuals.yml runs this on GitHub and publishes the files in the release "manuals"; the toolkit's
Packages window (category Manual collections) downloads them.

    python manuals/build_manuals.py frozen_meals --out build/manuals --limit 300
    python manuals/build_manuals.py all --out build/manuals --limit 5        (a quick local check)

What is published, and what is not (the owner's copyright rule; this repository is public):
  - facts and links: brand, model, product name, barcodes, FCC IDs, Canadian certification numbers ("ic_ids", from
    Internet Archive items whose title or description prints "IC: 4492A-XYZ123"; empty for every other source,
    EnerGuide included, which prints none), the official addresses of manuals and their
    rights, and small thumbnails only when their licence allows passing them on (Open Food Facts photos, CC BY-SA;
    Wikimedia Commons files under CC0, public domain, CC BY or CC BY-SA);
  - the full text of openly licensed instructions (Open Food Facts' and its sister databases' photos and fields,
    CC BY-SA; the Picture Describers volunteers' instructions, as licensed in their export), each with its credit;
  - NEVER the manuals themselves: the toolkit fetches each from its official address for the owner's own use.

Sources, and why each may be used by a program:
  Open Food Facts, Open Beauty Facts, Open Products Facts   documented APIs for programs (search.openfoodfacts.org,
      /api/v2/product, /api/v2/search), the OCR text they publish for every photo (images.*.org/.../<n>.json) and
      the photos; data ODbL, photos CC BY-SA 3.0; they ask for a User-Agent naming the program, at most 100 product
      reads and 10 searches a minute.
  The Internet Archive   advancedsearch.php and metadata/ are its documented interfaces; robots.txt allows them;
      its terms: scholarship and research, not infringing copyright. Only the items' facts and addresses are kept.
  Wikidata (query.wikidata.org) and Wikimedia Commons (its API)   CC0 data; Commons files keep their own licence,
      checked for each thumbnail; Wikimedia's policy asks for a User-Agent with contact.
  openFDA (api.fda.gov)   the FDA's device identifiers (GUDID): public domain US government data.
  ENERGY STAR (data.energystar.gov)   the EPA's certified-product lists (brand, model, some UPC barcodes), read with
      its documented Socrata interface; a US government work; robots.txt asks for a crawl delay of 1 second.
  EnerGuide (Natural Resources Canada)   the Canadian lists of home appliances sold in Canada (brand and model),
      the open.canada.ca dataset "Energy consumption of home appliances - EnerGuide label"
      (fbfdf946-8dd1-4830-a5c9-f8a72d8fabda), read through open.canada.ca's documented CKAN interface
      (package_show) and the ZIP files it lists; under the Open Government Licence - Canada 2.0, which allows any
      use with the attribution "Contains information licensed under the Open Government Licence - Canada"
      (https://open.canada.ca/en/open-government-licence-canada). No barcodes; its files were last changed in 2017.
  The Picture Describers website (describe.getbraille.com)   its export of volunteer-checked instructions, read with
      the API key in the repository secret DESCRIBE_SITE_KEY ("Authorization: Bearer", never in this repository; a
      key that may fetch, 2,000 uses a day), paged with next_since; skipped without it.
  Makers' own manual libraries (category firearms, categories.MAKERS)   each maker's robots.txt and terms were read
      on 2026-11-19: a library is READ only where robots.txt allows this builder (checked again at every build) and
      the terms do not forbid programs (GLOCK, Henry, Remington, Browning, Winchester, Weatherby, Bergara; the optics
      makers Burris and EOTECH; the suppressor makers Dead Air and HUXWRX): only the pages listed, only links to
      the maker's own files, a HEAD request for each PDF's size, never the manual itself. Makers whose terms forbid
      robots, scraping or indexing, or whose sites refuse programs, are only LINKED (the library's address,
      entered by hand, for the person to open): among them every cleaning-chemical maker checked (Hoppe's and
      M-Pro 7, Break-Free, Ballistol, Otis, Real Avid, Lucas, Birchwood Casey, Rem Oil), whose safety data sheets
      the person opens from the link; Smith & Wesson, whose terms forbid links without permission, is only NAMED.
      A document whose title or file name says "SDS" or "safety data sheet" is marked document "safety data sheet".
      A manual file that the maker's robots.txt disallows is left out. Legal but regulated items (the owner's
      policy of November 2026) are kept, the toolkit saying a legal note with each: the instructions of
      unfinished frames and receivers, their jigs and kits (80% Arms, 5D Tactical, Juggernaut Tactical read;
      Modulus Arms, Lone Wolf linked), binary and forced-reset triggers (Franklin Armory, Fostech read; Rare Breed
      linked), bump stocks (Slide Fire linked), magazine extensions (Pearce Grip, Shield Arms linked), solvent traps,
      NFA and automatic firearms. Never anything for making a suppressor (suppressor and baffle kits, drilled cups,
      filter adapters), automatic-fire conversion parts (auto sears, lightning links, "switches", conversion
      kits), reloading equipment or armorer's manuals (categories.FIREARMS_EXCLUDE).
  US military manuals of automatic firearms (category firearms, categories.PUBLIC_MANUALS)   the Internet Archive's
      copies of Army training circulars, each put in the index only when the front of its own text says "Approved
      for public release; distribution is unlimited" (Distribution Statement A) and shows no restricted marking
      (public_manual_entries, checked at every build).
  Not used: ManualsLib and other manual-copying sites (their terms forbid automated use), nor the Internet Archive's
      copies of them (items such as manualsbase-id-2170, manualsonline-id-..., manualzilla-id-..., manualsplus_...:
      COPY_SITE_ITEMS, or an item whose metadata names one of NEVER_SITES): never put into any index (the owner's
      decision); other Archive items (scans people uploaded, makers' manuals) stay, each with its rights. The FCC's
      equipment pages
      (its Akamai protection refuses programs from cloud machines; the toolkit reads them on the owner's computer).

Politeness: one request at a time, a pause for each site (GAPS), the builder's User-Agent, answers kept in a cache
folder (the workflow keeps it between runs), up to four tries when a server is busy (429, 5xx). Time: the workflow
sets MANUALS_TIME_LIMIT_MINUTES; listing products stops at half of it (LISTING_SHARE: "stop looking at half the
time"), and after the limit every request fails at once, so the index is still written with what was found.
"""

import argparse
import base64
import gzip
import hashlib
import html
import html.parser
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import categories as C  # noqa: E402
import instructions as I  # noqa: E402

USER_AGENT = ("DigitalAccessibilityToolkit-ManualsBuilder/1.0 (github.com/mark-getbraille/toolkit-models; "
              "one request at a time)")
GAPS = {"search.openfoodfacts.org": 6.5, "world.openfoodfacts.org": 0.7, "world.openbeautyfacts.org": 6.5,
        "world.openproductsfacts.org": 6.5, "images.openfoodfacts.org": 0.2, "images.openbeautyfacts.org": 0.2,
        "images.openproductsfacts.org": 0.2, "static.openfoodfacts.org": 0.2, "archive.org": 1.0,
        "query.wikidata.org": 2.0, "commons.wikimedia.org": 0.5, "upload.wikimedia.org": 0.2,
        "api.fda.gov": 0.5, "describe.getbraille.com": 1.0, "data.energystar.gov": 1.0,
        "open.canada.ca": 1.0, "natural-resources.canada.ca": 1.0, "www.nrcan.gc.ca": 1.0,
        "www.henryusa.com": 10.0}           # Henry's robots.txt asks for a crawl delay of 10 seconds
DEFAULT_GAP = 1.0
TIMEOUT = 40
STARTED = time.time()
TIME_LIMIT = float(os.environ.get("MANUALS_TIME_LIMIT_MINUTES", "0") or 0) * 60
LISTING_SHARE = 0.5
OFF_SITES = {"food": "openfoodfacts", "beauty": "openbeautyfacts", "products": "openproductsfacts"}
OFF_NAMES = {"food": "Open Food Facts", "beauty": "Open Beauty Facts", "products": "Open Products Facts"}
OFF_IMAGE_LICENCE = "CC BY-SA 3.0"
MAX_RAW_IMAGES = 12          # photos of one product whose OCR text is read (the newest first)
MAX_TESSERACT = 2            # photos of one product read with tesseract when the site has no OCR text
THUMB_SIDE = 128
OPEN_THUMB_LICENCES = re.compile(r"^(cc0|public domain|pd|cc[ -]by(?:-sa)?(?:[ -][\d.]+)?)", re.I)
DESCRIBE_EXPORT = "https://describe.getbraille.com/export/instructions.json"
DESCRIBE_EXPORT_FALLBACK = "https://describe.getbraille.com/instructions_json.php"
VOLUNTEER_PAGE = 1000
IA_ROWS = 100
IA_PAGES = 5                 # pages of one IA search at most
# The manual-copying sites, never used, and the start of the identifiers of the Internet Archive's copies of them
# (followed by "-" or "_"), never put into an index. They MUST match NEVER_SITES of app/toolkit/manuals/websearch.py
# and COPY_SITE_ITEMS of app/toolkit/manuals/archive.py in the toolkit (mark-getbraille/video-transcriber): this
# builder cannot import the toolkit, so the lists are copied here; change them together.
NEVER_SITES = ("manualslib.com", "manualzz.com", "manualsonline.com", "manua.ls", "manualowl.com", "safemanuals.com",
               "all-guidesbox.com", "manualsdir.com", "manualsbase.com", "manualzilla.com", "usermanual.wiki",
               "manualsplus.com", "manuals.plus", "device.report", "fccid.io", "manualsbrain.com", "manualmachine.com",
               "manualsfile.com", "libble.eu", "manualzz.net", "manuallib.com")
COPY_SITE_ITEMS = ("manualslib", "manualzz", "manualsonline", "manua-ls", "manuals-ls", "manualowl", "safemanuals",
                   "manualsbase", "manualzilla", "manualsdir", "usermanual-wiki", "usermanualwiki", "manualsplus",
                   "manuals-plus", "device-report", "devicereport", "fccid-io", "fccidio", "fccid", "all-guidesbox",
                   "allguidesbox", "manualsbrain", "manualmachine", "manualsfile", "libble", "manuallib")
_COPY_ID = re.compile(r"^(?:" + "|".join(re.escape(p) for p in COPY_SITE_ITEMS) + r")[-_]", re.I)
SOURCE_FIELDS = ("source", "originalurl", "original_url", "originalUrl", "url", "external-identifier")
BAD_KINDS = re.compile(r"software|program|library|application|website|programming|package|game|framework|"
                       r"operating system|distribution|utility|service|database|web|protocol|format|font", re.I)


class OutOfTime(Exception):
    """The build's time is up: no more requests."""


def out_of_time():
    """True once the build's time limit (if any) has passed."""
    return bool(TIME_LIMIT) and time.time() - STARTED > TIME_LIMIT


def listing_out_of_time():
    """True once half the time limit was spent: stop looking for more products and finish those found."""
    return bool(TIME_LIMIT) and time.time() - STARTED > TIME_LIMIT * LISTING_SHARE


def say(text):
    """A progress line for the workflow's log."""
    print(text, flush=True)


class Fetcher:
    """Polite requests: one at a time, GAPS seconds apart for each site, the builder's User-Agent, JSON and text
    answers kept in cache_dir, retries when a server is busy, nothing after the time limit."""

    def __init__(self, cache_dir):
        import requests
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.cache_dir = cache_dir
        self.last = {}
        self.requests = 0
        os.makedirs(cache_dir, exist_ok=True)

    def _path(self, url):
        return os.path.join(self.cache_dir, hashlib.sha256(url.encode("utf-8")).hexdigest()[:40])

    def _wait(self, host):
        wait = self.last.get(host, -1e9) + GAPS.get(host, DEFAULT_GAP) - time.monotonic()
        if wait > 0:
            time.sleep(wait)

    def raw(self, url, headers=None, cache=True, max_bytes=20_000_000):
        """The bytes of url (kept in the cache when cache). Raises OutOfTime, or RuntimeError with the reason."""
        path = self._path(url)
        if cache and os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        error, status = None, 0
        for attempt in range(4):
            if out_of_time():
                raise OutOfTime()
            self._wait(host)
            try:
                r = self.session.get(url, headers=headers or {}, timeout=TIMEOUT, stream=True)
                data = r.raw.read(max_bytes + 1, decode_content=True)
                status = r.status_code
            except Exception as e:  # noqa: BLE001 - tried again
                status, data = 0, b""
                error = e
            finally:
                self.last[host] = time.monotonic()
                self.requests += 1
            if status == 200:
                if len(data) > max_bytes:
                    raise RuntimeError(f"{url}: too large")
                if cache:
                    with open(path + ".tmp", "wb") as f:
                        f.write(data)
                    os.replace(path + ".tmp", path)
                return data
            if status in (429, 500, 502, 503, 504, 0):
                time.sleep(min(60, 5 * (attempt + 1) ** 2))
                continue
            raise RuntimeError(f"{url}: HTTP {status}")
        raise RuntimeError(f"{url}: the server stayed busy" + (f" ({error})" if error is not None else ""))

    def size(self, url):
        """The size in bytes a server gives for url (a HEAD request: nothing is downloaded), or 0 when unknown."""
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        if out_of_time():
            return 0
        self._wait(host)
        try:
            r = self.session.head(url, timeout=TIMEOUT, allow_redirects=True)
            return int(r.headers.get("Content-Length") or 0) if r.status_code == 200 else 0
        except Exception:  # noqa: BLE001 - the size is only a help
            return 0
        finally:
            self.last[host] = time.monotonic()
            self.requests += 1

    def json(self, url, headers=None, cache=True):
        """The JSON of url."""
        return json.loads(self.raw(url, dict({"Accept": "application/json"}, **(headers or {})), cache)
                          .decode("utf-8", "replace"))

    def text(self, url, headers=None, cache=True):
        """The text of url."""
        return self.raw(url, headers, cache).decode("utf-8", "replace")


# ------------------------------------------------------------------------------------------------- helpers

def thumbnail(data, side=THUMB_SIDE):
    """A small JPEG (base64) of a picture's bytes, at most side pixels; "" when it cannot be read."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img.thumbnail((side, side))
        out = io.BytesIO()
        img.save(out, "JPEG", quality=80)
        return base64.b64encode(out.getvalue()).decode("ascii")
    except Exception:  # noqa: BLE001
        return ""


def model_of(title):
    """The model number in a title ("Cuisinart CPT-180 toaster" -> "CPT-180"): a word with letters and digits, or
    digits with a hyphen; "" when none."""
    for word in re.findall(r"[A-Za-z0-9][A-Za-z0-9./+-]*[A-Za-z0-9]", str(title or "")):
        if re.search(r"\d", word) and (re.search(r"[A-Za-z]", word) or "-" in word) and \
                not re.fullmatch(r"(19|20)\d\d", word) and len(word) <= 24 and \
                not re.fullmatch(r"[\d.,]+\s*(l|ml|oz|qt|w|kw|v|cups?|in|cm|mm|ft|lbs?|kg|g|pcs?|pack)", word, re.I):
            return word
    return ""


def clean_title(title):
    """A product name from a manual's title, without "user manual", "user guide" and the like."""
    t = re.sub(r"\b(user'?s?|owner'?s?|operating|operation|instruction|instructions|service|quick start|quick|"
               r"setup|installation|use and care|use & care)\b\s*(manual|guide|instructions|book)?\b", " ",
               str(title or ""), flags=re.I)
    t = re.sub(r"\b(manual|guide|pdf|download)\b", " ", t, flags=re.I)
    return " ".join(t.split()).strip(" -:,")


# --------------------------------------------------------------------------------- Open Food Facts and family

def off_image_base(code, site):
    """The folder of a product's photos on the database's image server."""
    code = re.sub(r"\D", "", str(code))
    if len(code) > 8:
        code = code.zfill(13)
        folder = f"{code[:3]}/{code[3:6]}/{code[6:9]}/{code[9:]}"
    else:
        folder = code
    return f"https://images.{site}.org/images/products/{folder}"


def off_products(fetch, db, query, limit):
    """Product codes of one search (search.openfoodfacts.org for food; the database's v2 search for the others),
    at most limit."""
    codes, page = [], 1
    while len(codes) < limit and not listing_out_of_time():
        if db == "food":
            url = "https://search.openfoodfacts.org/search?" + urllib.parse.urlencode(
                {"q": query, "page_size": 100, "page": page, "fields": "code"})
            answer = fetch.json(url)
            hits = answer.get("hits") or []
            pages = int(answer.get("page_count") or 1)
        else:
            url = f"https://world.{OFF_SITES[db]}.org/api/v2/search?{query}&" + urllib.parse.urlencode(
                {"fields": "code", "page_size": 100, "page": page})
            answer = fetch.json(url)
            hits = answer.get("products") or []
            pages = int((answer.get("count") or 0) // 100 + 1)
        codes += [str(h.get("code")) for h in hits if h.get("code")]
        if page >= pages or not hits:
            break
        page += 1
    return codes[:limit]


def ocr_blocks(answer):
    """The text of each block of an OCR answer (Google Cloud Vision's fullTextAnnotation: pages, blocks,
    paragraphs, words, symbols), one paragraph a line. A block is one region of the package (a column, a panel),
    so instructions are not mixed with the nutrition table beside them, as the answer's whole text is."""
    blocks = []
    for r in (answer or {}).get("responses") or []:
        for page in (r.get("fullTextAnnotation") or {}).get("pages") or []:
            for block in page.get("blocks") or []:
                lines = []
                for para in block.get("paragraphs") or []:
                    words = ["".join(s.get("text", "") for s in w.get("symbols") or []) for w in para.get("words") or []]
                    line = " ".join(w for w in words if w)
                    line = re.sub(r"\s+([.,:;!?%)])", r"\1", line)
                    line = re.sub(r"([(])\s+", r"\1", line)
                    if line:
                        lines.append(line)
                if lines:
                    blocks.append("\n".join(lines))
    return blocks


def instruction_text(blocks):
    """The blocks that hold instructions, in order: each block that reads like instructions (instructions.looks_like)
    and the blocks right after it that do too or that start a method (Microwave, Conventional oven ...)."""
    keep = []
    for i, b in enumerate(blocks):
        if I.looks_like(b) or I.START.search(b[:60]) and i + 1 < len(blocks) and I.looks_like(blocks[i + 1]):
            if not I.NOISE.search(b[:40]):
                keep.append(b)
    return "\n".join(keep)


def ocr_text_of(fetch, base, key):
    """The instruction blocks of the OCR text the database published for one photo (<base>/<key>.json, Google
    Cloud Vision's answer), or ""."""
    try:
        answer = fetch.json(f"{base}/{key}.json")
    except (RuntimeError, ValueError):
        return ""
    return instruction_text(ocr_blocks(answer))


def tesseract_text(fetch, url):
    """The text of a photo read with tesseract on this machine ("" when tesseract is not installed)."""
    if not shutil.which("tesseract"):
        return ""
    try:
        data = fetch.raw(url, cache=False, max_bytes=8_000_000)
    except (RuntimeError, OutOfTime):
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "photo.jpg")
        with open(path, "wb") as f:
            f.write(data)
        try:
            done = subprocess.run(["tesseract", path, "stdout", "-l", "eng", "--psm", "3"], capture_output=True,
                                  text=True, timeout=120)
            return done.stdout
        except (OSError, subprocess.SubprocessError):
            return ""


def score(ins):
    """How complete extracted instructions are: their steps, more for a temperature or a time in them."""
    steps = [st for m in ins.methods for st in m.steps]
    return len(steps) + sum(2 for m in ins.methods if m.temperature or m.time) + len(ins.safety) * 0.5


def off_entry(fetch, db, code):
    """The index entry of one product (with its instructions when its texts have any), or None."""
    site = OFF_SITES[db]
    fields = "code,product_name,product_name_en,brands,quantity,categories_tags,preparation,preparation_en,images," \
             "image_front_thumb_url,image_front_small_url,lang"
    answer = fetch.json(f"https://world.{site}.org/api/v2/product/{code}?fields={fields}")
    p = answer.get("product") if isinstance(answer, dict) else None
    if not isinstance(p, dict):
        return None
    name = str(p.get("product_name_en") or p.get("product_name") or "").strip()
    brand = str(p.get("brands") or "").split(",")[0].strip()
    if not name and not brand:
        return None
    source = OFF_NAMES[db]
    page = f"https://world.{site}.org/product/{code}"
    common = dict(barcode=code, product=name, brand=brand, source=source, source_url=page,
                  licence="CC BY-SA 4.0" if db == "food" else "CC BY-SA 4.0",
                  credit=f"{source} contributors")
    records = []
    prep = p.get("preparation_en") or p.get("preparation")
    if prep:
        found = I.extract(prep, name, brand, code, source, common["licence"], common["credit"], page)
        if found is not None:
            rec = I.to_record(found)
            rec["from"] = "preparation"
            records.append(rec)
    if not records:
        base = off_image_base(code, site)
        raw = sorted((k for k in (p.get("images") or {}) if str(k).isdigit()), key=int, reverse=True)
        tried_tesseract, best = 0, None
        for key in raw[:MAX_RAW_IMAGES]:
            text = ocr_text_of(fetch, base, key)
            if not text and tried_tesseract < MAX_TESSERACT:
                tried_tesseract += 1
                text = tesseract_text(fetch, f"{base}/{key}.jpg")
            found = I.extract(text, name, brand, code, source, common["licence"], common["credit"],
                              f"{base}/{key}.jpg") if text else None
            if found is not None and (best is None or score(found) > score(best[0])):
                best = (found, key)       # several photos may show the instructions: the most complete wins
        if best is not None:
            rec = I.to_record(best[0])
            rec.update({"from": "photo", "image_url": f"{base}/{best[1]}.jpg", "image_licence": OFF_IMAGE_LICENCE})
            records.append(rec)
    entry = {"id": f"{db}-{code}", "brand": brand, "name": name, "quantity": str(p.get("quantity") or ""),
             "category": ", ".join(t.split(":", 1)[-1].replace("-", " ") for t in (p.get("categories_tags") or [])[-3:]),
             "barcodes": [code], "instructions": records, "page": page,
             "source": source, "licence": "ODbL (facts); CC BY-SA (texts and photos)"}
    thumb_url = p.get("image_front_thumb_url") or p.get("image_front_small_url")
    if thumb_url:
        try:
            data = thumbnail(fetch.raw(thumb_url))
            if data:
                entry["thumb"] = {"data": data, "licence": OFF_IMAGE_LICENCE, "credit": f"{source} contributors",
                                  "source": thumb_url}
        except (RuntimeError, OutOfTime):
            pass
    return entry


# ------------------------------------------------------------------------------- the Picture Describers export

def volunteer_records(fetch, kinds, key=None):
    """The volunteers' accepted records of these kinds from the Picture Describers export ([] without the key).
    The export answers {"format": 1, "count", "next_since", "items": [...]}, oldest acceptance first, at most
    VOLUNTEER_PAGE a time: the next page is asked with since = next_since until a page is empty. The short address
    (export/instructions.json) is tried first, then instructions_json.php (servers without its rewrite rule)."""
    key = key if key is not None else os.environ.get("DESCRIBE_SITE_KEY", "")
    if not key:
        say("The Picture Describers export is skipped: the secret DESCRIBE_SITE_KEY is not set.")
        return []
    headers = {"Authorization": f"Bearer {key}"}
    records, since, address = [], "", None
    for _ in range(200):                     # at most 200 pages (200,000 records)
        answer = None
        for url in ([address] if address else [DESCRIBE_EXPORT, DESCRIBE_EXPORT_FALLBACK]):
            try:
                text = fetch.text(url + "?" + urllib.parse.urlencode({"since": since, "limit": VOLUNTEER_PAGE}),
                                  headers=headers, cache=False)
                answer, address = text, url
                break
            except (RuntimeError, OutOfTime) as e:
                say(f"The Picture Describers export at {url} could not be read: {e}")
        if answer is None:
            break
        page = parse_volunteer_export(answer, kinds, every_kind=True)
        records += [r for r in page if r.get("kind", "cooking") in kinds]
        try:
            following = json.loads(answer).get("next_since", "") if answer.lstrip().startswith("{") else ""
        except ValueError:
            following = ""
        if not page or not following or following == since:
            break
        since = following
    say(f"Picture Describers volunteers: {len(records)} accepted instructions of the kinds {', '.join(kinds)}")
    return records


def parse_volunteer_export(text, kinds, every_kind=False):
    """The records of an export (the site's JSON answer {"items": [...]}, JSON lines, or one JSON array) of the
    given kinds (every_kind: all of them), format 1 only."""
    text = text.strip()
    rows = []
    if text.startswith("{") and '"items"' in text[:4000]:
        try:
            rows = json.loads(text).get("items") or []
        except ValueError:
            rows = []
    elif text.startswith("["):
        try:
            rows = json.loads(text)
        except ValueError:
            rows = []
    else:
        for line in text.splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    out = []
    for r in rows:
        if isinstance(r, dict) and r.get("format", 1) == 1 and r.get("barcode") and \
                (every_kind or r.get("kind", "cooking") in kinds):
            out.append(r)
    return out


def add_volunteers(entries, records, fetch=None):
    """Put the volunteers' records into the entries by barcode (a product not there yet gets its own entry, with
    the volunteer photo as its thumbnail when its licence allows)."""
    by_code = {}
    for e in entries:
        for b in e.get("barcodes") or []:
            by_code[re.sub(r"\D", "", b).zfill(14)] = e
    for r in records:
        code = re.sub(r"\D", "", str(r["barcode"]))
        e = by_code.get(code.zfill(14))
        rec = dict(r)
        rec.setdefault("source", "volunteer photo")
        if e is None:
            e = {"id": f"vol-{code}", "brand": r.get("brand", ""), "name": r.get("product_name", ""),
                 "quantity": r.get("quantity", ""), "barcodes": [code], "instructions": [],
                 "source": "Picture Describers volunteers", "licence": r.get("licence", "")}
            if fetch is not None and r.get("image_url") and OPEN_THUMB_LICENCES.match(str(r.get("image_licence"))):
                try:
                    data = thumbnail(fetch.raw(r["image_url"]))
                    if data:
                        e["thumb"] = {"data": data, "licence": r.get("image_licence"), "credit": r.get("credit", ""),
                                      "source": r["image_url"]}
                except (RuntimeError, OutOfTime):
                    pass
            entries.append(e)
            by_code[code.zfill(14)] = e
        # Volunteer-checked text replaces OCR text of the same kind.
        e["instructions"] = [x for x in e.get("instructions") or [] if x.get("kind", "cooking") != rec.get("kind")
                             or x.get("reviews")] + [rec]
    return entries


# ----------------------------------------------------------------------------------------- Internet Archive

def _ia_text(value):
    """A metadata field that may be a list, as text."""
    if isinstance(value, list):
        return "; ".join(str(v) for v in value if v)
    return str(value or "").strip()


def copy_site_item(identifier, doc=None):
    """True when an Internet Archive item is a copy of a manual-copying site (never put into an index): its
    identifier starts with one of COPY_SITE_ITEMS, or its fields (doc: a search answer's doc or an item's
    metadata) name one of NEVER_SITES as where it came from ("source", "originalurl" ...) or in its "subject"
    words ("manualsbase; manuals;"). The same test as archive.copy_site_item in the toolkit."""
    if _COPY_ID.match(str(identifier or "").strip()):
        return True
    doc = doc if isinstance(doc, dict) else {}
    if not doc:
        return False
    if _COPY_ID.match(_ia_text(doc.get("identifier"))):
        return True
    for name in SOURCE_FIELDS:
        value = _ia_text(doc.get(name)).lower()
        if value and any(re.search(r"(?<![a-z0-9-])" + re.escape(s) + r"(?![a-z0-9-])", value) for s in NEVER_SITES):
            return True
    words = {w.strip().lower() for w in re.split(r"[;,]", _ia_text(doc.get("subject")))}
    return bool(words & ((set(COPY_SITE_ITEMS) | set(NEVER_SITES)) - {"fccid"}))


def copy_site_manual(manual):
    """True when a manual record names a copy of a manual-copying site: its "ia" item, or the archive.org item of
    its "url", "page" or "text_url"."""
    if manual.get("ia") and copy_site_item(manual["ia"]):
        return True
    for key in ("url", "page", "text_url"):
        m = re.match(r"https?://(?:www\.)?archive\.org/(?:download|details|metadata)/([^/?#]+)",
                     str(manual.get(key) or ""), re.I)
        if m and copy_site_item(urllib.parse.unquote(m.group(1))):
            return True
    return False


def without_copy_sites(entries):
    """The entries with every manual that is a copy of a manual-copying site taken out (also those ia_fill found
    out by their metadata, marked "copy_site"); an entry left with no manual and no instructions is dropped."""
    out = []
    for e in entries:
        manuals = e.get("manuals") or []
        kept = [m for m in manuals if not m.get("copy_site") and not copy_site_manual(m)]
        if manuals and not kept and not e.get("instructions"):
            continue
        if len(kept) != len(manuals):
            e = dict(e, manuals=kept)
        out.append(e)
    return out


OLDEST_YEAR = 1990          # manuals of products from about 1990 to today (an item with no known year is kept)


def before_1990(doc):
    """True when an Internet Archive item's own year (or date), or a year in its title, is before OLDEST_YEAR. Items
    with no year at all are kept: most manuals' records give none."""
    years = []
    for field in ("year", "date"):
        value = doc.get(field)
        for v in (value if isinstance(value, list) else [value]):
            m = re.match(r"\s*(\d{4})", str(v or ""))
            if m:
                years.append(int(m.group(1)))
    title = doc.get("title")
    title = " ".join(title) if isinstance(title, list) else str(title or "")
    years += [int(y) for y in re.findall(r"\b(19[0-8]\d)\b", title)]
    return bool(years) and max(years) < OLDEST_YEAR


def ia_search(fetch, words, collections=("manuals", "computermanuals"), limit=200):
    """Items of the manual collections whose title has the words (each word in quotes), without the copies of
    manual-copying sites (left out by the search itself, and again by copy_site_item)."""
    title = " AND ".join('"' + w.replace('"', "") + '"' for w in words.split())
    where = " OR ".join(f"collection:{c}" for c in collections)
    not_copies = " OR ".join(f"identifier:{p}-* OR identifier:{p}_*" for p in COPY_SITE_ITEMS)
    items, page = [], 1
    while len(items) < limit and page <= IA_PAGES and not listing_out_of_time():
        url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(
            [("q", f"mediatype:texts AND ({where}) AND title:({title}) AND NOT ({not_copies})")] +
            [("fl[]", f) for f in ("identifier", "title", "description", "item_size", "collection", "rights",
                                   "licenseurl", "subject", "source", "originalurl", "year", "date")] +
            [("rows", IA_ROWS), ("page", page), ("output", "json")])
        docs = ((fetch.json(url).get("response") or {}).get("docs") or [])
        items += [d for d in docs if not copy_site_item(d.get("identifier"), d) and not before_1990(d)]
        if len(docs) < IA_ROWS:
            break
        page += 1
    return items[:limit]


def ia_brand(doc, title):
    """The brand of an item: from its collection "manuals_<brand>", else the title's first word."""
    for c in doc.get("collection") or []:
        m = re.fullmatch(r"manuals_([a-z0-9]+)", str(c), re.I)
        if m:
            hit = re.search(r"\b" + re.escape(m.group(1)) + r"\b", title, re.I)
            if hit:                     # only a maker's collection named in the title ("manuals_contributions" is not)
                return hit.group(0)
    first = str(title or "").split(" ")[0]
    return first if first[:1].isupper() else ""


def ia_rights(doc):
    """An item's rights in words."""
    rights = doc.get("rights")
    if isinstance(rights, list):
        rights = "; ".join(rights)
    return str(rights or doc.get("licenseurl") or "not stated (the manual belongs to its maker)")


class CopySite(ValueError):
    """An item whose metadata shows it is a copy of a manual-copying site."""


def ia_files(fetch, identifier):
    """(pdf name, size, text name) of an item. Raises CopySite when its metadata names a manual-copying site."""
    meta = fetch.json(f"https://archive.org/metadata/{urllib.parse.quote(identifier)}")
    if copy_site_item(identifier, meta.get("metadata")):
        raise CopySite(identifier)
    pdfs, text = [], ""
    for f in meta.get("files") or []:
        name = str(f.get("name") or "")
        if name.lower().endswith(".pdf"):
            pdfs.append((0 if f.get("source") == "original" else 1, name, int(f.get("size") or 0)))
        elif name.endswith("_djvu.txt"):
            text = name
    pdfs.sort()
    return (pdfs[0][1], pdfs[0][2], text) if pdfs else ("", 0, text)


# Canadian certification numbers (ISED, formerly Industry Canada): "IC: 4492A-XYZ123", "IC 4492A-XYZ123",
# "ISED: 4492A-XYZ123": a company number of up to 5 digits with an optional letter, a hyphen, a product number of up
# to 11 letters and digits. The SAME rule as app/toolkit/manuals/ised.py in the toolkit (mark-getbraille/
# video-transcriber), which reads the "ic_ids" written here: after "IC" the number counts only with ":" (or "#",
# "."), "ID", or the company number's letter, so "IC 555-TIMER" (a chip) and "CAN ICES-3(B)" are not numbers.
IC_NUMBER = re.compile(r"\b(?P<word>IC|ISEDC?)(?P<id>\s*ID)?\s*(?P<sep>[:#.])?\s*(?P<digits>\d{1,5})(?P<letter>[A-Z]?)"
                       r"\s*-\s*(?P<product>[A-Z0-9]{1,11})(?![A-Z0-9]|-[A-Z0-9])", re.I)


def ic_numbers(text):
    """The Canadian certification numbers printed in text, as "4492A-XYZ123" (without "IC:"), each once, in order."""
    out = []
    for m in IC_NUMBER.finditer(str(text or "")):
        if not (m.group("word").upper().startswith("ISED") or m.group("sep") or m.group("id") or m.group("letter")):
            continue
        number = f"{m.group('digits')}{m.group('letter')}-{m.group('product')}".upper()
        if number not in out:
            out.append(number)
    return out


def ia_entry(doc):
    """The index entry of an item (its manual's address is filled in later by ia_fill). Its "ic_ids" are the
    Canadian certification numbers its title or description prints ("IC: 4492A-XYZ123")."""
    ident, title = str(doc.get("identifier")), str(doc.get("title") or "")
    if isinstance(doc.get("title"), list):
        title = str(doc["title"][0])
    name = clean_title(title)
    brand = ia_brand(doc, title)
    page = f"https://archive.org/details/{urllib.parse.quote(ident)}"
    description = re.sub(r"<[^>]+>", " ", html.unescape(_ia_text(doc.get("description"))))
    return {"id": f"ia-{ident}", "brand": brand, "model": model_of(title), "name": name, "barcodes": [],
            "fcc_ids": [], "ic_ids": ic_numbers(title + "\n" + description), "source": "Internet Archive",
            "manuals": [{"title": title, "url": "", "page": page, "kind": "page", "ia": ident,
                         "size": int(doc.get("item_size") or 0), "rights": ia_rights(doc),
                         "source": "Internet Archive"}]}


def ia_fill(fetch, entries):
    """The PDF (and OCR text) address of each Internet Archive manual, while time allows (one request each)."""
    done = 0
    for e in entries:
        for m in e.get("manuals") or []:
            if not m.get("ia") or m.get("url"):
                continue
            try:
                pdf, size, text = ia_files(fetch, m["ia"])
            except OutOfTime:
                return done
            except CopySite:
                m["copy_site"] = True       # taken out by without_copy_sites
                continue
            except (RuntimeError, ValueError):
                continue
            base = f"https://archive.org/download/{urllib.parse.quote(m['ia'])}/"
            if pdf:
                m.update(url=base + urllib.parse.quote(pdf), kind="pdf", size=size)
            if text:
                m["text_url"] = base + urllib.parse.quote(text)
            done += 1
    return done


# ------------------------------------------------------------------------------------- Wikidata and Commons

WIKIDATA_QUERY = """SELECT ?item ?itemLabel ?url ?kindLabel ?brandLabel ?makerLabel ?image ?gtin WHERE {
  ?item wdt:P2078 ?url ; wdt:P31 ?kind .
  OPTIONAL { ?item wdt:P1716 ?brand . }
  OPTIONAL { ?item wdt:P176 ?maker . }
  OPTIONAL { ?item wdt:P18 ?image . }
  OPTIONAL { ?item wdt:P3962 ?gtin . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""


def wikidata_rows(fetch):
    """Every Wikidata item with a user manual URL (one query, kept in the cache)."""
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": WIKIDATA_QUERY,
                                                                          "format": "json"})
    answer = fetch.json(url, headers={"Accept": "application/sparql-results+json"})
    rows = []
    for b in (answer.get("results") or {}).get("bindings") or []:
        rows.append({k: v.get("value", "") for k, v in b.items()})
    return rows


def wikidata_entries(rows, key):
    """The entries of the category key: items whose kind's label has one of its words (and is not software), and
    neither whose kind nor name matches the category's "exclude" rule (firearms: no machine guns, solvent traps ...)."""
    cat = C.CATEGORIES[key]
    words = [w.lower() for w in (cat.get("ia") or []) + C.WIKIDATA_WORDS.get(key, [])]
    exclude = re.compile(cat["exclude"], re.I) if cat.get("exclude") else None
    by_item = {}
    for r in rows:
        kind = r.get("kindLabel", "").lower()
        if not kind or BAD_KINDS.search(kind) or not any(re.search(r"\b" + re.escape(w) + r"s?\b", kind)
                                                         for w in words):
            continue
        if exclude is not None and (exclude.search(kind) or exclude.search(r.get("itemLabel", ""))):
            continue
        qid = r["item"].rsplit("/", 1)[-1]
        e = by_item.setdefault(qid, {"id": f"wd-{qid}", "name": r.get("itemLabel", ""),
                                     "brand": r.get("brandLabel") or r.get("makerLabel") or "",
                                     "model": model_of(r.get("itemLabel", "")), "category": kind, "barcodes": [],
                                     "fcc_ids": [], "ic_ids": [], "manuals": [], "source": "Wikidata (CC0)",
                                     "page": r["item"], "image": r.get("image", "")})
        if r.get("gtin") and r["gtin"] not in e["barcodes"]:
            e["barcodes"].append(r["gtin"])
        url = r.get("url", "")
        if url.startswith("http") and url not in [m["url"] for m in e["manuals"]]:
            pdf = urllib.parse.urlsplit(url).path.lower().endswith(".pdf")
            e["manuals"].append({"title": f"{e['name']} manual (the maker's site)", "url": url if pdf else "",
                                 "page": url, "kind": "pdf" if pdf else "page",
                                 "rights": "belongs to its maker", "source": "Wikidata (user manual URL)"})
    return list(by_item.values())


def commons_thumb(fetch, image_url):
    """(base64 JPEG, licence, credit) of a Commons file when its licence allows passing it on, else None."""
    name = urllib.parse.unquote(image_url.rsplit("/", 1)[-1])
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "titles": f"File:{name}", "prop": "imageinfo", "iiprop": "url|extmetadata",
         "iiurlwidth": THUMB_SIDE, "format": "json"})
    pages = ((fetch.json(url).get("query") or {}).get("pages") or {})
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        licence = (meta.get("LicenseShortName") or {}).get("value", "")
        if not OPEN_THUMB_LICENCES.match(licence.strip()):
            return None
        artist = re.sub(r"<[^>]+>", "", html.unescape((meta.get("Artist") or {}).get("value", ""))).strip()
        data = thumbnail(fetch.raw(info.get("thumburl") or info.get("url")))
        if data:
            return data, licence, f"{artist or 'Unknown author'}, Wikimedia Commons"
    return None


# --------------------------------------------------------------------------------------------- openFDA UDI

def udi_entries(fetch, term, limit):
    """Devices of the FDA's identifier database (GUDID, through openFDA) whose GMDN term has the words, only those
    sold over the counter (is_otc: the ones a person has at home, not hospital kits)."""
    out, skip = [], 0
    while len(out) < limit and not listing_out_of_time():
        url = "https://api.fda.gov/device/udi.json?" + urllib.parse.urlencode(
            {"search": f"gmdn_terms.name:{term} AND is_otc:true", "limit": 100, "skip": skip})
        try:
            results = fetch.json(url).get("results") or []
        except RuntimeError:
            break
        for r in results:
            gtins = [i["id"] for i in r.get("identifiers") or [] if i.get("issuing_agency") == "GS1" and i.get("id")]
            brand = str(r.get("brand_name") or "").strip()
            model = str(r.get("version_or_model_number") or "").strip()
            if not gtins or not (brand or model):
                continue
            gmdn = "; ".join(g.get("name", "") for g in r.get("gmdn_terms") or [])
            out.append({"id": f"udi-{gtins[0]}", "brand": brand, "model": model,
                        "name": str(r.get("device_description") or gmdn)[:160],
                        "maker": str(r.get("company_name") or ""), "category": gmdn, "barcodes": gtins,
                        "fcc_ids": [], "ic_ids": [], "manuals": [],
                        "source": "FDA device identifiers (openFDA; public domain)"})
        if len(results) < 100:
            break
        skip += 100
    return out[:limit]


# ------------------------------------------------------------------------------------------------ ENERGY STAR

def energystar_entries(fetch, dataset, limit):
    """Certified models of one ENERGY STAR dataset (data.energystar.gov): brand, model, kind and the UPC barcode
    when the dataset has it."""
    url = f"https://data.energystar.gov/resource/{dataset}.json?" + urllib.parse.urlencode({"$limit": limit})
    out = []
    for r in fetch.json(url) or []:
        brand, model = str(r.get("brand_name") or "").strip(), str(r.get("model_number") or "").strip()
        if not brand or not model:
            continue
        upcs = [u for u in re.split(r"[,;\s]+", str(r.get("upc") or "")) if re.fullmatch(r"\d{8,14}", u)]
        kind = str(r.get("type") or r.get("product_type") or "").strip()
        out.append({"id": f"es-{dataset}-{r.get('pd_id') or model}", "brand": brand, "model": model,
                    "name": " ".join(w for w in (brand, model, kind) if w), "category": kind, "barcodes": upcs,
                    "fcc_ids": [], "ic_ids": [], "manuals": [],
                    "source": "ENERGY STAR certified products (US EPA)"})
    return out


# ------------------------------------------------------------------------------------------------ EnerGuide (Canada)

ENERGUIDE_DATASET = ("https://open.canada.ca/data/api/3/action/package_show?id="
                     "fbfdf946-8dd1-4830-a5c9-f8a72d8fabda")
ENERGUIDE_SOURCE = ("EnerGuide (Natural Resources Canada). Contains information licensed under the Open Government "
                    "Licence - Canada")


def energuide_files(package):
    """[(the file's English name in lower case, its address)] of the ZIP files an open.canada.ca package_show answer
    lists ("clothes dryers", ".../001_clothes-dryers_secheuses.zip")."""
    out = []
    for r in (package.get("result") or {}).get("resources") or []:
        names = r.get("name_translated") if isinstance(r.get("name_translated"), dict) else {}
        name = str(names.get("en") or r.get("name") or "").strip().lower()
        if str(r.get("format") or "").upper() == "ZIP" and r.get("url"):
            out.append((name, r["url"]))
    return out


def energuide_models(data, kind, limit):
    """Entries for the models of one EnerGuide ZIP (its "*Data*.csv": BRAND_NAME, MODEL_NUM_1 and, for some kinds,
    TYPE_LABEL_EN), each brand and model once, at most limit. kind: the file's English name ("dishwashers")."""
    import csv
    import zipfile
    out, seen = [], set()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv") and "data" in n.lower()]
        if not names:
            return out
        text = z.read(names[0]).decode("cp1252", "replace")
    for r in csv.DictReader(io.StringIO(text)):
        brand, model = str(r.get("BRAND_NAME") or "").strip(), str(r.get("MODEL_NUM_1") or "").strip()
        if not brand or not model or (brand.lower(), model.lower()) in seen:
            continue
        seen.add((brand.lower(), model.lower()))
        what = " ".join(w for w in (str(r.get("TYPE_LABEL_EN") or "").strip(), kind) if w)
        out.append({"id": f"eg-{r.get('REC_REF_KEY') or model}", "brand": brand, "model": model,
                    "name": f"{brand} {model} ({what})", "category": kind, "barcodes": [], "fcc_ids": [],
                    "ic_ids": [], "manuals": [], "source": ENERGUIDE_SOURCE, "market": "Canada"})
        if len(out) >= limit:
            break
    return out


def energuide_entries(fetch, kinds, limit):
    """The EnerGuide models of the kinds named (words of the files' English names: "dishwashers", "ranges"), an
    even share of limit for each file."""
    files = [(n, u) for n, u in energuide_files(fetch.json(ENERGUIDE_DATASET)) if any(k in n for k in kinds)]
    out = []
    for name, url in files:
        if listing_out_of_time():
            break
        out += energuide_models(fetch.raw(url), name, max(1, limit // max(1, len(files))))
    return out


# --------------------------------------------------------------------------- makers' own manual libraries (firearms)
#
# categories.MAKERS lists each maker and what may be done with its site (access "read", "link" or "mention", with
# the reason, from its robots.txt and terms). Only "read" makers are fetched, only the pages listed for them, and only
# when robots.txt allows this builder; the manual links kept are those that point to the maker's own files (its
# "hosts"). The manuals are never downloaded: their address (and the size the server gives, by a HEAD request) is all.

class _LinkParser(html.parser.HTMLParser):
    """Collects (address, link text, the heading above it) of every link of a page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.heading = [], ""
        self._href, self._text, self._label = None, [], ""
        self._in_heading, self._heading_text = False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4", "h5"):
            self._in_heading, self._heading_text = True, []
        elif tag == "a" and a.get("href"):
            self._href, self._text, self._label = a["href"], [], a.get("title") or ""

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5") and self._in_heading:
            self._in_heading = False
            self.heading = " ".join("".join(self._heading_text).split())
        elif tag == "a" and self._href is not None:
            text = " ".join("".join(self._text).split()) or self._label
            self.links.append((self._href, text, self.heading))
            self._href = None

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)
        if self._in_heading:
            self._heading_text.append(data)


GENERIC_LIBRARY = re.compile(r"^(?:(?:firearms?|guns?|manuals?|all|products?)\b\s*)*$", re.I)   # a list page
# A heading that is not a manual's title (an age question, a cookie notice): the file name is used instead.
NOT_A_TITLE = re.compile(r"\?\s*$|years old|cookies?|newsletter|subscribe|sign up|log ?in", re.I)
# A link whose words say nothing of the manual ("Click here", "go here", or the bare address written out).
# A heading that only names the page ("Instructions", "Manuals"): the file name is used instead.
GENERIC_HEADING = re.compile(r"^(?:instructions?|manuals?|downloads?|owner'?s manuals?|resources?|support)$", re.I)
GENERIC_LINK = re.compile(r"^(click here.*|download.*|(?:go |see )?here|pdf|view.*|open.*|read more|manual|"
                          r"https?://\S+|\s*)$", re.I)
PDF_IN_TEXT = re.compile(r"https?://[^\s\"'<>\\]+?\.pdf(?:\?[^\s\"'<>\\]*)?", re.I)
TITLE_BEFORE = re.compile(r"""(?<![a-z])["']?title["']?\s*:\s*(?:"([^"]{2,120})"|'([^']{2,120})')""", re.I)
SUBTITLE_BEFORE = re.compile(r"""(?<![a-z])["']?subtitle["']?\s*:\s*(?:"([^"]{2,160})"|'([^']{2,160})')""", re.I)
# The kind of product a document is about, from the words of its title (the accessories first, so that "Pistol
# Magazine Loader" or "Rifle Scope" is not taken for the firearm itself; product_type looks for the firearm words
# first for a firearm maker).
TYPES = [("solvent trap", "solvent trap"), ("jig", "frame"), ("80 lower", "frame"), ("80 frame", "frame"),
         ("unfinished", "frame"), ("receiver blank", "frame"), ("parts kit", "frame"), ("build kit", "frame"),
         ("binary", "trigger"), ("bfsiii", "trigger"), ("forced reset", "trigger"), ("forced-reset", "trigger"),
         ("frt", "trigger"), ("bump stock", "stock"), ("bump fire", "stock"), ("magazine extension", "magazine"),
         ("machine gun", "automatic"), ("submachine gun", "automatic"), ("safety data sheet", "chemical"),
         ("sds", "chemical"), ("msds", "chemical"), ("solvent", "chemical"),
         ("bore cleaner", "chemical"), ("lubricant", "chemical"), ("gun oil", "chemical"), ("clp", "chemical"),
         ("grease", "chemical"), ("cleaning kit", "cleaning"), ("cleaning rod", "cleaning"),
         ("bore brush", "cleaning"), ("bore snake", "cleaning"), ("boresnake", "cleaning"), ("jag", "cleaning"),
         ("suppressor", "suppressor"), ("silencer", "suppressor"), ("moderator", "suppressor"),
         ("magazine loader", "loader"), ("speed loader", "loader"), ("speedloader", "loader"),
         ("moon clip", "loader"), ("stripper clip", "loader"), ("uplula", "loader"), ("magazine", "magazine"),
         ("holster", "holster"), ("laser", "laser"), ("weapon light", "light"), ("weaponlight", "light"),
         ("flashlight", "light"), ("riflescope", "optic"), ("scope", "optic"), ("red dot", "optic"),
         ("reflex sight", "optic"), ("holographic", "optic"), ("magnifier", "optic"), ("sight", "optic"),
         ("optic", "optic"), ("bipod", "mount"), ("sling", "mount"), ("scope mount", "mount"), ("rings", "mount"),
         ("air rifle", "airgun"), ("air pistol", "airgun"), ("airgun", "airgun"), ("air gun", "airgun"),
         ("bb gun", "airgun"), ("pellet", "airgun"), ("revolver", "revolver"), ("pistol", "pistol"),
         ("handgun", "pistol"), ("shotgun", "shotgun"), ("over under", "shotgun"), ("over-under", "shotgun"),
         ("over/under", "shotgun"), ("o/u", "shotgun"), ("side by side", "shotgun"), ("side-by-side", "shotgun"),
         ("carbine", "rifle"), ("rifle", "rifle"), ("cable lock", "lock"), ("trigger lock", "lock"), ("gun lock", "lock"), ("lock box", "safe"),
         ("lockbox", "safe"), ("safe", "safe"), ("vault", "safe"), ("cabinet", "safe")]
FIREARM_TYPES = {"pistol", "revolver", "rifle", "shotgun", "firearm", "airgun"}
# What a maker's documents are called, by its type: a chemical's document is its safety data sheet; a firearm's,
# its owner's manual.
DOCUMENT_WORDS = {"chemical": "safety data sheets", "cleaning": "instructions and safety data sheets",
                  "holster": "instructions", "magazine": "instructions", "loader": "instructions",
                  "lock": "instructions", "mount": "instructions", "frame": "instructions",
                  "trigger": "instructions", "stock": "instructions", "solvent trap": "instructions"}
SDS_WORDS = re.compile(r"\bm?sds\b|safety[- ]data[- ]sheet", re.I)


def title_from_file(url):
    """A readable title from a PDF's file name ("51959_Instructions-for-use_Gen6_14102025-EN-low.pdf" ->
    "Instructions for use Gen6"): no numbers of 5 or more digits, no "EN", "low", "web", "final", "rev"."""
    name = urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1])
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("name")
    if q:
        name = q[0]
    name = re.sub(r"\.pdf$", "", name, flags=re.I)
    words = [w for w in re.split(r"[\s_\-+()]+", name) if w and not re.fullmatch(
        r"\d{5,}|en|low|lr|web|file|final|rev\w*|v\d+|\d+|digital", w, re.I)]
    return " ".join(words)


def product_type(text, default):
    """The kind of product a document is about, from its words ("pistol", "rifle", "airgun", "safe", "optic",
    "suppressor", "chemical" ...), else default. For a firearm maker the firearm words are looked for first."""
    t = str(text or "").lower()
    order = TYPES
    if default in FIREARM_TYPES:          # a gun maker's "Tube Magazine Rifle" is a rifle: the firearm words first
        order = [w for w in TYPES if w[1] in FIREARM_TYPES] + [w for w in TYPES if w[1] not in FIREARM_TYPES]
    for word, kind in order:
        if re.search(r"\b" + re.escape(word) + r"s?\b", t):
            return kind
    return default


def library_links(text, base):
    """[(address, title)] of the links of a manual library page: its <a> links (a link that only says "Click here
    to download" takes the heading above it) and the PDF addresses written in its scripts (a "title:" and
    "subtitle:" just before one name it; else its file name). Pages sent as escaped HTML (an XML answer holding
    "&lt;a href=...") are read too. Each address once, in order."""
    if "&lt;a " in text:
        text = html.unescape(text)
    parser = _LinkParser()
    try:
        parser.feed(text)
    except Exception:  # noqa: BLE001 - a broken page gives the links read so far
        pass
    out, seen = [], set()
    for href, label, heading in parser.links:
        url = urllib.parse.urljoin(base, html.unescape(href.strip()))
        if not url.startswith("http") or url in seen:
            continue
        title = heading if GENERIC_LINK.match(label or "") else label
        if title and (NOT_A_TITLE.search(title) or GENERIC_HEADING.match(title)):
            title = title_from_file(url) if url.lower().split("?")[0].endswith(".pdf") else ""
        seen.add(url)
        out.append((url, title or ""))
    for m in PDF_IN_TEXT.finditer(text):
        url = m.group(0).replace("\\u0026", "&")
        if url in seen:
            continue
        seen.add(url)
        before = text[max(0, m.start() - 400):m.start()]
        titles = ["".join(t) for t in TITLE_BEFORE.findall(before)]
        subtitles = ["".join(t) for t in SUBTITLE_BEFORE.findall(before)]
        title = titles[-1] if titles else title_from_file(url)
        if titles and subtitles:
            title += " " + subtitles[-1]
        out.append((url, html.unescape(title)))
    return out


_ROBOTS = {}


def robots_allows(fetch, url):
    """True when the robots.txt of url's site allows this builder to read url. No robots.txt (HTTP 404) allows
    everything; a robots.txt that cannot be read allows nothing."""
    import urllib.robotparser
    parts = urllib.parse.urlsplit(url)
    site = f"{parts.scheme}://{parts.netloc}"
    if site not in _ROBOTS:
        parser = urllib.robotparser.RobotFileParser()
        try:
            parser.parse(fetch.text(site + "/robots.txt").splitlines())
        except RuntimeError as e:
            if "HTTP 404" in str(e) or "HTTP 410" in str(e):
                parser.parse([])
            else:
                parser = None
        except OutOfTime:
            return False
        _ROBOTS[site] = parser
    parser = _ROBOTS[site]
    return parser is not None and parser.can_fetch(USER_AGENT, url)


def firearm_model(name, maker):
    """The model in a manual's title, without the maker's name and the words about the document ("GLOCK Owner's
    Manual Models G17 - G48" -> "Models G17 - G48"; "Model 870 Pump-Action Shotgun — Owner's Manual" -> "Model 870
    Pump-Action Shotgun")."""
    text = re.split(r"\s+[—–]\s+", str(name or ""))[0]
    for word in maker.replace("(", " ").replace(")", " ").split():
        text = re.sub(r"\b" + re.escape(word) + r"\b", " ", text, flags=re.I)
    text = re.sub(r"\b(owner'?s?|owner’s|user|instruction|operator'?s?)\b|\b(manual|instructions?|supplement(al)?|"
                  r"addendum|sheet|for|series)\b", " ", text, flags=re.I)
    return " ".join(text.split()).strip(" -:,&")


def maker_entry(maker, title, url, kind, size=0):
    """One index entry: a maker's manual (kind "pdf", or "page" for a manual published as a web page)."""
    name = re.sub(r"\s*[®™©]", "", " ".join(str(title or "").replace("’", "'").split()))
    name = re.sub(r"[\s→»›>]+$", "", name) or title_from_file(url)          # "FLOW →": no arrow
    words = name if maker["maker"].split()[0].lower() in name.lower() else f"{maker['maker']} {name}"
    return {"id": f"fa-{maker['key']}-{hashlib.sha256(url.encode('utf-8')).hexdigest()[:10]}",
            "brand": maker["maker"], "model": firearm_model(name, maker["maker"]), "name": words,
            "type": product_type(name + " " + re.sub(r"[-_/.]+", " ", urllib.parse.urlsplit(url).path), maker["type"]),
            "category": "firearms", "barcodes": [], "fcc_ids": [],
            "ic_ids": [], "source": f"{maker['maker']}'s own manual library", "page": maker.get("library", ""),
            "manuals": [{"title": words, "url": url, "page": maker.get("library", "") if kind == "pdf" else url,
                         "kind": kind, "size": int(size or 0), "document": document_of(words, url),
                         "rights": f"belongs to its maker ({maker['maker']}); fetched from the maker for the "
                                   "owner's own use", "source": "the maker"}]}


def document_of(title, url=""):
    """"safety data sheet" for a chemical's SDS (its title or file name says so), else "manual"."""
    return "safety data sheet" if SDS_WORDS.search(f"{title} {title_from_file(url) if url else ''}") else "manual"


def documents_word(maker):
    """What the maker's documents are called: "owner's manuals", "safety data sheets", "instructions" ..."""
    return DOCUMENT_WORDS.get(maker.get("type", ""), "owner's manuals")


def library_entry(maker):
    """The entry of a maker's whole library: its address (for "read" and "link" makers; for "mention", its site in
    words only), for the person to open when no manual of their model is listed."""
    library = maker.get("library", "") if maker["access"] in ("read", "link") else ""
    return {"id": f"fa-{maker['key']}-library", "brand": maker["maker"], "model": "",
            "name": f"{maker['maker']} {documents_word(maker)} (the maker's own library)", "type": maker["type"],
            "category": "firearms", "barcodes": [], "fcc_ids": [], "ic_ids": [], "source": "the maker's site",
            "page": library, "site": maker.get("site", ""), "access": maker["access"], "access_reason": maker["reason"],
            "manuals": [{"title": f"{maker['maker']} {documents_word(maker)}", "url": "", "page": library,
                         "kind": "library", "document": "library",
                         "size": 0, "rights": f"belongs to its maker ({maker['maker']})", "source": "the maker"}]
            if library else []}


def wanted_document(title, url, exclude):
    """True when a document of a maker's library is a manual the index may hold: not a sales paper (NOT_A_MANUAL)
    and nothing the category excludes (solvent traps, automatic weapons, conversion parts, reloading ...)."""
    words = f"{title} {title_from_file(url)}"
    return not re.search(C.NOT_A_MANUAL, words, re.I) and not (exclude and re.search(exclude, words, re.I))


def maker_documents(fetch, maker, exclude, sizes=True):
    """The manual entries of one "read" maker: the links of its listed pages that point to its own files (a PDF on
    one of its hosts) or, with page_links, to its manuals published as web pages. Returns (entries, notes)."""
    entries, notes, seen = [], [], set()
    page_rule = re.compile(maker["page_links"]) if maker.get("page_links") else None
    for page in maker.get("pages") or []:
        if not robots_allows(fetch, page):
            notes.append(f"{maker['maker']}: robots.txt does not allow {page}; skipped")
            continue
        try:
            text = fetch.text(page)
        except (RuntimeError, OutOfTime) as e:
            notes.append(f"{maker['maker']}: {e}")
            continue
        for url, title in library_links(text, page):
            host = (urllib.parse.urlsplit(url).hostname or "").lower()
            is_pdf = urllib.parse.urlsplit(url).path.lower().endswith(".pdf") or ".pdf" in url.lower()
            if url in seen or host not in maker.get("hosts", []):
                continue
            if is_pdf:
                kind = "pdf"
            elif page_rule is not None and page_rule.match(url.split("#")[0]) and url.split("#")[0] != page:
                kind = "page"
            else:
                continue
            if not wanted_document(title, url, exclude) or GENERIC_LIBRARY.match(firearm_model(title, maker["maker"])):
                continue
            seen.add(url)
            if not robots_allows(fetch, url):
                notes.append(f"{maker['maker']}: robots.txt does not allow {url}; left out")
                continue
            size = fetch.size(url) if sizes and kind == "pdf" else 0
            entries.append(maker_entry(maker, title, url, kind, size))
    return entries, notes


def maker_entries(fetch, makers, exclude=None, sizes=True):
    """The entries of every maker: the manuals of "read" makers, and one library entry for each maker (so the
    toolkit can always offer the maker's own page, or name its site). Returns (entries, notes)."""
    entries, notes = [], []
    for maker in makers:
        if maker["access"] == "read" and not listing_out_of_time():
            got, why = maker_documents(fetch, maker, exclude, sizes)
            entries += got
            notes += why
            say(f"{maker['maker']}: {len(got)} manuals")
        entries.append(library_entry(maker))
    return entries, notes


# Distribution Statement A, and the markings that refuse a document even when it is also printed (the same rule as
# training-kit/kit/uxo_personal_sources.py).
DISTRIBUTION_A = re.compile(r"approved\s+for\s+public\s+release\s*[;,.:]?\s*distribution\s+is\s+unlimited", re.I)
RESTRICTED = re.compile(r"distribution\s*(?:statement\s*)?[B-F]\s*[:.\-–—]|distribution\s+statement\s+[B-F]\b|"
                        r"distribution\s+authori[sz]ed\s+to|for\s+official\s+use\s+only|\bFOUO\b|\bCUI\b|"
                        r"controlled\s+unclassified|\bNOFORN\b|export[- ]controlled|warning:?\s+this\s+document\s+"
                        r"contains\s+technical\s+data\s+whose\s+export", re.I)
FRONT_CHARS = 12000


def public_release(front_text):
    """(True, "") when the front of a document's text says Distribution Statement A and shows no restricted
    marking; else (False, why)."""
    text = " ".join(str(front_text or "").split())
    bad = RESTRICTED.search(text)
    if bad:
        return False, f"a restricted marking ({bad.group(0)})"
    if not DISTRIBUTION_A.search(text):
        return False, "no Distribution Statement A on its front pages"
    return True, ""


def public_manual_entries(fetch, docs):
    """The index entries of publicly released military manuals (categories.PUBLIC_MANUALS): each Internet Archive
    item's PDF, kept only when the front of its own text passes public_release. Returns (entries, notes)."""
    entries, notes = [], []
    for doc in docs:
        if listing_out_of_time():
            break
        try:
            pdf, size, text = ia_files(fetch, doc["ia"])
            base = f"https://archive.org/download/{urllib.parse.quote(doc['ia'])}/"
            front = fetch.text(base + urllib.parse.quote(text))[:FRONT_CHARS] if text else ""
        except (RuntimeError, OutOfTime, ValueError, CopySite) as e:
            notes.append(f"{doc['name']}: {e}")
            continue
        ok, why = public_release(front)
        if not ok or not pdf:
            notes.append(f"{doc['name']}: left out ({why or 'no PDF'})")
            continue
        entries.append({"id": f"fa-public-{doc['ia']}", "brand": doc["brand"], "model": doc["model"],
                        "name": doc["name"], "type": "automatic", "category": "firearms", "barcodes": [],
                        "fcc_ids": [], "ic_ids": [], "source": "Internet Archive",
                        "page": f"https://archive.org/details/{urllib.parse.quote(doc['ia'])}",
                        "manuals": [{"title": doc["name"], "url": base + urllib.parse.quote(pdf),
                                     "page": f"https://archive.org/details/{urllib.parse.quote(doc['ia'])}",
                                     "kind": "pdf", "ia": doc["ia"], "size": size, "document": "manual",
                                     "text_url": base + urllib.parse.quote(text) if text else "",
                                     "release": "Distribution Statement A: approved for public release; "
                                                "distribution is unlimited",
                                     "rights": "a US government work (public domain)",
                                     "source": "Internet Archive"}]})
    return entries, notes


def attach_manuals(entries, manual_entries):
    """Give device records (openFDA, ENERGY STAR, EnerGuide) the manuals of Internet Archive items of the same brand
    and model, and the Canadian certification numbers those items print."""
    by_model = {}
    for m in manual_entries:
        if m.get("model"):
            by_model.setdefault(re.sub(r"[^a-z0-9]", "", m["model"].lower()), []).append(m)
    for e in entries:
        key = re.sub(r"[^a-z0-9]", "", str(e.get("model") or "").lower())
        for m in by_model.get(key, []) if len(key) >= 3 else []:
            if not e.get("brand") or e["brand"].lower()[:4] in (m.get("brand") or "").lower() + m["name"].lower():
                e["manuals"] += [x for x in m["manuals"] if x not in e["manuals"]]
                e["ic_ids"] = list(e.get("ic_ids") or []) + [i for i in m.get("ic_ids") or []
                                                             if i not in (e.get("ic_ids") or [])]


# ------------------------------------------------------------------------------------------------ building

def build(key, out_dir, limit, fetch):
    """Build the category key: its entries, then its index file and manifest. Returns the manifest."""
    cat = C.CATEGORIES[key]
    entries, notes = [], []
    if cat.get("off"):
        per_query = max(1, limit // len(cat["off"]))
        seen = set()
        for db, query in cat["off"]:
            if listing_out_of_time():
                notes.append("Listing stopped at half the time limit.")
                break
            try:
                codes = off_products(fetch, db, query, per_query)
            except (RuntimeError, OutOfTime, ValueError) as e:
                notes.append(f"{OFF_NAMES[db]} search {query!r} failed: {e}")
                continue
            for code in codes:
                if code in seen:
                    continue
                seen.add(code)
                try:
                    e = off_entry(fetch, db, code)
                except OutOfTime:
                    break
                except (RuntimeError, ValueError) as err:
                    notes.append(f"{code}: {err}")
                    continue
                if e is not None and (e.get("instructions") or e.get("thumb")):
                    entries.append(e)
            say(f"{key}: {len(entries)} products after {query}")
        if cat.get("volunteers"):
            add_volunteers(entries, volunteer_records(fetch, cat["volunteers"]), fetch)
        entries = [e for e in entries if e.get("instructions")]
    manual_entries = []
    if cat.get("ia"):
        per_word = max(1, limit // len(cat["ia"]))
        seen = set()
        for words in cat["ia"]:
            if listing_out_of_time():
                notes.append("Listing stopped at half the time limit.")
                break
            try:
                docs = ia_search(fetch, words, ("manuals", "computermanuals") + tuple(cat.get("ia_collections", ())),
                                 per_word)
            except (RuntimeError, OutOfTime, ValueError) as e:
                notes.append(f"Internet Archive search {words!r} failed: {e}")
                continue
            for d in docs:
                if d.get("identifier") not in seen:
                    seen.add(d.get("identifier"))
                    manual_entries.append(ia_entry(d))
            say(f"{key}: {len(manual_entries)} Internet Archive items after {words!r}")
    if cat.get("wikidata"):
        try:
            wd = wikidata_entries(wikidata_rows(fetch), key)
            for e in wd:
                if e.get("image") and not listing_out_of_time():
                    try:
                        got = commons_thumb(fetch, e["image"])
                    except (RuntimeError, OutOfTime, ValueError):
                        got = None
                    if got:
                        e["thumb"] = {"data": got[0], "licence": got[1], "credit": got[2], "source": e["image"]}
                e.pop("image", None)
            manual_entries += wd
            say(f"{key}: {len(wd)} Wikidata products with a manual address")
        except (RuntimeError, OutOfTime, ValueError) as e:
            notes.append(f"Wikidata failed: {e}")
    if cat.get("makers"):
        got, why = maker_entries(fetch, cat["makers"], cat.get("exclude"))
        manual_entries += got
        notes += why
    if cat.get("public_manuals"):
        got, why = public_manual_entries(fetch, cat["public_manuals"])
        manual_entries += got
        notes += why
        say(f"{key}: {len(got)} publicly released military manuals")
    if cat.get("udi"):
        devices = []
        for term in cat["udi"]:
            try:
                devices += udi_entries(fetch, term, max(1, limit // len(cat["udi"])))
            except (OutOfTime, ValueError):
                break
        attach_manuals(devices, manual_entries)
        manual_entries += devices
        say(f"{key}: {len(devices)} FDA device records")
    if cat.get("energystar"):
        models = []
        for dataset in cat["energystar"]:
            if listing_out_of_time():
                break
            try:
                models += energystar_entries(fetch, dataset, max(1, limit // len(cat["energystar"])))
            except (RuntimeError, OutOfTime, ValueError) as e:
                notes.append(f"ENERGY STAR {dataset} failed: {e}")
        attach_manuals(models, manual_entries)
        manual_entries += models
        say(f"{key}: {len(models)} ENERGY STAR certified models")
    if cat.get("energuide"):
        try:
            models = energuide_entries(fetch, cat["energuide"], limit)
        except (RuntimeError, OutOfTime, ValueError) as e:
            notes.append(f"EnerGuide failed: {e}")
            models = []
        attach_manuals(models, manual_entries)
        manual_entries += models
        say(f"{key}: {len(models)} EnerGuide models sold in Canada")
    filled = ia_fill(fetch, manual_entries)
    if manual_entries:
        say(f"{key}: the files of {filled} Internet Archive manuals found")
    entries += manual_entries
    return write(key, entries, out_dir, notes, fetch.requests if fetch else 0)


def write(key, entries, out_dir, notes=(), requests_made=0):
    """Write manuals-<key>.json.gz and manifest-<key>.json; return the manifest."""
    cat = C.CATEGORIES[key]
    built = time.strftime("%Y-%m-%d")
    entries = without_copy_sites(entries)      # never an Internet Archive copy of a manual-copying site
    index = {"key": key, "name": cat["name"], "description": cat["description"], "kind": cat["kind"],
             "licence": cat["licence"], "built": built,
             "credit": "Open Food Facts, Open Beauty Facts and Open Products Facts contributors; the Internet "
                       "Archive; Wikidata; Wikimedia Commons authors; the US FDA; Picture Describers volunteers"
                       + ("; Natural Resources Canada (EnerGuide): contains information licensed under the Open "
                          "Government Licence - Canada" if cat.get("energuide") else ""),
             "copyright": "Facts and links only: the manuals belong to their makers and are not published here.",
             "notes": list(notes)[:50], "entries": entries}
    if cat.get("guidance"):
        index["guidance"] = cat["guidance"]
    if cat.get("makers"):
        index["makers"] = [{k: m.get(k, "") for k in ("key", "maker", "type", "access", "library", "site", "reason")}
                           for m in cat["makers"]]
        index["copyright"] += (" Makers' sites are read only where their robots.txt and terms allow programs; the "
                               "others are linked (or named) for the person to open.")
    raw = gzip.compress(json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0)
    os.makedirs(out_dir, exist_ok=True)
    # The same entries give the same checksum whatever day they were built (merge_catalogue keeps a new version only
    # when this changed); each build is a new file, so every version stays in the release.
    content = hashlib.sha256(json.dumps({k: v for k, v in index.items() if k != "built"}, ensure_ascii=False,
                                        sort_keys=True).encode("utf-8")).hexdigest()
    name = f"manuals-{key}.{built}.json.gz"
    with open(os.path.join(out_dir, name), "wb") as f:
        f.write(raw)
    # The manuals the toolkit fetches: those with a PDF address, and the Internet Archive items whose file it finds
    # itself (their whole item size is the estimate).
    manuals = [m for e in entries for m in e.get("manuals") or [] if (m.get("kind") == "pdf" and m.get("url"))
               or m.get("ia")]
    manifest = {"key": key, "name": cat["name"], "description": cat["description"], "kind": cat["kind"],
                "licence": cat["licence"], "entries": len(entries),
                "instructions": sum(1 for e in entries if e.get("instructions")),
                "thumbnails": sum(1 for e in entries if e.get("thumb")),
                "file": name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                "manual_count": len(manuals), "manuals_size": sum(int(m.get("size") or 0) for m in manuals),
                "built": built, "requests": requests_made, "files": [name], "content_sha256": content}
    with open(os.path.join(out_dir, f"manifest-{key}.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    say(json.dumps({k: v for k, v in manifest.items() if k != "description"}))
    return manifest


RELEASE = "https://github.com/mark-getbraille/toolkit-models/releases/download/manuals"


def merge_catalogue(manifests, previous=None, today=None):
    """manuals.json from the newest manifests (one per category) and the manuals.json published before: every
    collection's newest version in its own fields (as before, so the toolkit's present code keeps working) and
    "versions" ([{file, url, size, sha256, published, built, change_note}], newest first) with every version kept. A
    rebuild with the same entries as the newest version (content_sha256) adds no version."""
    collections = dict((previous or {}).get("collections", {}))
    for m in manifests:
        old = collections.get(m["key"])
        version = {"file": m["file"], "url": f"{RELEASE}/{m['file']}", "size": m["size"], "sha256": m["sha256"],
                   "published": m["built"], "built": m["built"], "change_note": ""}
        if old is None:
            collections[m["key"]] = dict(m, versions=[dict(version, change_note="First version")])
            continue
        versions = list(old.get("versions") or [{"file": old["file"], "url": f"{RELEASE}/{old['file']}",
                                                 "size": old.get("size", 0), "sha256": old.get("sha256", ""),
                                                 "published": old.get("built", ""), "built": old.get("built", ""),
                                                 "change_note": ""}])
        if m.get("content_sha256") and m.get("content_sha256") == old.get("content_sha256"):
            continue                                        # the same entries: the newest version stays
        versions = [v for v in versions if v["file"] != m["file"]]
        versions.insert(0, dict(version, change_note=f"Rebuilt: {m.get('entries', 0)} entries"))
        versions.sort(key=lambda v: (v.get("built", ""), v["file"]), reverse=True)
        main = m if versions[0]["file"] == m["file"] else old
        collections[m["key"]] = dict(main, versions=versions)
    return {"built": today or time.strftime("%Y-%m-%d"), "collections": collections}


def main(argv=None):
    """Build the categories named (or all), or merge manifests into manuals.json (--merge)."""
    parser = argparse.ArgumentParser(description="Build the toolkit's manual and instruction collections.")
    parser.add_argument("keys", nargs="?", default="all", help="category keys separated by commas, or all")
    parser.add_argument("--out", default="build/manuals")
    parser.add_argument("--cache", default="build/manuals-cache")
    parser.add_argument("--limit", type=int, default=300, help="products to look at per category, about")
    parser.add_argument("--merge", nargs="*", default=None, help="merge these manifests into manuals.json")
    parser.add_argument("--existing", default=None, help="the manuals.json published before (with --merge)")
    args = parser.parse_args(argv)
    if args.merge is not None:
        previous = json.load(open(args.existing)) if args.existing and os.path.exists(args.existing) else None
        manifests = [json.load(open(p)) for p in sorted(args.merge) if os.path.exists(p)]
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "manuals.json"), "w", encoding="utf-8") as f:
            json.dump(merge_catalogue(manifests, previous), f, indent=1)
        return 0
    keys = list(C.CATEGORIES) if args.keys == "all" else [k for k in args.keys.split(",") if k]
    unknown = [k for k in keys if k not in C.CATEGORIES]
    if unknown:
        parser.error(f"unknown categories: {', '.join(unknown)}")
    fetch = Fetcher(args.cache)
    for key in keys:
        build(key, args.out, args.limit, fetch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
