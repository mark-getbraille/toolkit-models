"""Build the manual and instruction collections of the Digital Accessibility Toolkit, one category at a time
(manuals/categories.py), and write each as a small gzipped JSON index with its manifest. The workflow
.github/workflows/manuals.yml runs this on GitHub and publishes the files in the release "manuals"; the toolkit's
Packages window (category Manual collections) downloads them.

    python manuals/build_manuals.py frozen_meals --out build/manuals --limit 300
    python manuals/build_manuals.py all --out build/manuals --limit 5        (a quick local check)

What is published, and what is not (the owner's copyright rule; this repository is public):
  - facts and links: brand, model, product name, barcodes, FCC IDs, the official addresses of manuals and their
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
  The Picture Describers website (describe.getbraille.com)   its export of volunteer-checked instructions, read with
      the API key in the repository secret DESCRIBE_SITE_KEY ("Authorization: Bearer", never in this repository; a
      key that may fetch, 2,000 uses a day), paged with next_since; skipped without it.
  Not used: ManualsLib and other manual-copying sites (their terms forbid automated use); the FCC's equipment pages
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
        "api.fda.gov": 0.5, "describe.getbraille.com": 1.0, "data.energystar.gov": 1.0}
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

def ia_search(fetch, words, collections=("manuals", "computermanuals"), limit=200):
    """Items of the manual collections whose title has the words (each word in quotes)."""
    title = " AND ".join('"' + w.replace('"', "") + '"' for w in words.split())
    where = " OR ".join(f"collection:{c}" for c in collections)
    items, page = [], 1
    while len(items) < limit and page <= IA_PAGES and not listing_out_of_time():
        url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(
            [("q", f"mediatype:texts AND ({where}) AND title:({title})")] +
            [("fl[]", f) for f in ("identifier", "title", "item_size", "collection", "rights", "licenseurl")] +
            [("rows", IA_ROWS), ("page", page), ("output", "json")])
        docs = ((fetch.json(url).get("response") or {}).get("docs") or [])
        items += docs
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


def ia_files(fetch, identifier):
    """(pdf name, size, text name) of an item."""
    meta = fetch.json(f"https://archive.org/metadata/{urllib.parse.quote(identifier)}")
    pdfs, text = [], ""
    for f in meta.get("files") or []:
        name = str(f.get("name") or "")
        if name.lower().endswith(".pdf"):
            pdfs.append((0 if f.get("source") == "original" else 1, name, int(f.get("size") or 0)))
        elif name.endswith("_djvu.txt"):
            text = name
    pdfs.sort()
    return (pdfs[0][1], pdfs[0][2], text) if pdfs else ("", 0, text)


def ia_entry(doc):
    """The index entry of an item (its manual's address is filled in later by ia_fill)."""
    ident, title = str(doc.get("identifier")), str(doc.get("title") or "")
    if isinstance(doc.get("title"), list):
        title = str(doc["title"][0])
    name = clean_title(title)
    brand = ia_brand(doc, title)
    page = f"https://archive.org/details/{urllib.parse.quote(ident)}"
    return {"id": f"ia-{ident}", "brand": brand, "model": model_of(title), "name": name, "barcodes": [],
            "fcc_ids": [], "source": "Internet Archive",
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
    """The entries of the category key: items whose kind's label has one of its words (and is not software)."""
    cat = C.CATEGORIES[key]
    words = [w.lower() for w in (cat.get("ia") or []) + C.WIKIDATA_WORDS.get(key, [])]
    by_item = {}
    for r in rows:
        kind = r.get("kindLabel", "").lower()
        if not kind or BAD_KINDS.search(kind) or not any(re.search(r"\b" + re.escape(w) + r"s?\b", kind)
                                                         for w in words):
            continue
        qid = r["item"].rsplit("/", 1)[-1]
        e = by_item.setdefault(qid, {"id": f"wd-{qid}", "name": r.get("itemLabel", ""),
                                     "brand": r.get("brandLabel") or r.get("makerLabel") or "",
                                     "model": model_of(r.get("itemLabel", "")), "category": kind, "barcodes": [],
                                     "fcc_ids": [], "manuals": [], "source": "Wikidata (CC0)",
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
    """Devices of the FDA's identifier database (GUDID, through openFDA) whose GMDN term has the words."""
    out, skip = [], 0
    while len(out) < limit and not listing_out_of_time():
        url = "https://api.fda.gov/device/udi.json?" + urllib.parse.urlencode(
            {"search": f"gmdn_terms.name:{term}", "limit": 100, "skip": skip})
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
                        "fcc_ids": [], "manuals": [], "source": "FDA device identifiers (openFDA; public domain)"})
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
                    "fcc_ids": [], "manuals": [], "source": "ENERGY STAR certified products (US EPA)"})
    return out


def attach_manuals(entries, manual_entries):
    """Give device records (openFDA) the manuals of Internet Archive items of the same brand and model."""
    by_model = {}
    for m in manual_entries:
        if m.get("model"):
            by_model.setdefault(re.sub(r"[^a-z0-9]", "", m["model"].lower()), []).append(m)
    for e in entries:
        key = re.sub(r"[^a-z0-9]", "", str(e.get("model") or "").lower())
        for m in by_model.get(key, []) if len(key) >= 3 else []:
            if not e.get("brand") or e["brand"].lower()[:4] in (m.get("brand") or "").lower() + m["name"].lower():
                e["manuals"] += [x for x in m["manuals"] if x not in e["manuals"]]


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
    filled = ia_fill(fetch, manual_entries)
    if manual_entries:
        say(f"{key}: the files of {filled} Internet Archive manuals found")
    entries += manual_entries
    return write(key, entries, out_dir, notes, fetch.requests if fetch else 0)


def write(key, entries, out_dir, notes=(), requests_made=0):
    """Write manuals-<key>.json.gz and manifest-<key>.json; return the manifest."""
    cat = C.CATEGORIES[key]
    built = time.strftime("%Y-%m-%d")
    index = {"key": key, "name": cat["name"], "description": cat["description"], "kind": cat["kind"],
             "licence": cat["licence"], "built": built,
             "credit": "Open Food Facts, Open Beauty Facts and Open Products Facts contributors; the Internet "
                       "Archive; Wikidata; Wikimedia Commons authors; the US FDA; Picture Describers volunteers",
             "copyright": "Facts and links only: the manuals belong to their makers and are not published here.",
             "notes": list(notes)[:50], "entries": entries}
    raw = gzip.compress(json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0)
    os.makedirs(out_dir, exist_ok=True)
    name = f"manuals-{key}.json.gz"
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
                "built": built, "requests": requests_made, "files": [name]}
    with open(os.path.join(out_dir, f"manifest-{key}.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)
    say(json.dumps({k: v for k, v in manifest.items() if k != "description"}))
    return manifest


def main(argv=None):
    """Build the categories named (or all)."""
    parser = argparse.ArgumentParser(description="Build the toolkit's manual and instruction collections.")
    parser.add_argument("keys", help="category keys separated by commas, or all")
    parser.add_argument("--out", default="build/manuals")
    parser.add_argument("--cache", default="build/manuals-cache")
    parser.add_argument("--limit", type=int, default=300, help="products to look at per category, about")
    args = parser.parse_args(argv)
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
