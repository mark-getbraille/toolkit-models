"""Open Food Facts, read only through the routes it publishes for bulk reuse (never its websites).

Why: the Open Food Facts family of websites (world.openfoodfacts.org and its country sites, static and
images.openfoodfacts.org, Open Beauty Facts, Open Products Facts and Open Pet Food Facts, all on the same software and
robots.txt) shut out AI crawlers by name ("User-agent: GPTBot / anthropic-ai / ClaudeBot / Claude-Web: Disallow: /",
checked 2026-11-21), disallow /api and /cgi to every robot, and search.openfoodfacts.org disallows every robot. The
owner's rule is that such blocks are obeyed, so none of those hosts is read (tests/test_no_off_sites.py checks it).

Open Food Facts publishes two routes for reuse in bulk that are not blocked, and the kit reads only these:

  the product database   the Hugging Face dataset openfoodfacts/product-database (huggingface.co; robots.txt
                         "User-agent: * / Allow: /"; ODbL 1.0, its contents DbCL 1.0), the daily JSONL export of Open
                         Food Facts turned into Parquet by Open Food Facts itself. Its food.parquet is about 7.7 GB,
                         but only a few columns are read, piece by piece (row group by row group), never the whole
                         file: about 450 MB, read once and kept in the work folder (CACHE), shared by every Open Food
                         Facts entry of the kit.
  the product photos     the Open Food Facts Images dataset on the Registry of Open Data on AWS
                         (registry.opendata.aws/openfoodfacts-images; the bucket openfoodfacts-images in eu-west-3,
                         no robots.txt; "licenced under the Creative Commons Attribution ShareAlike licence"): every
                         photo people uploaded, synchronised monthly, as the photo was sent ("raw"), by barcode and
                         photo number (PHOTOS).

The product database names, for each product, which uploaded photo is its chosen front, ingredients and nutrition
photo in each language ("front_en" -> photo 3); the kit takes that photo from the AWS bucket. The website's cropped and
turned copy is not on AWS, so the picture is the photo as the shopper took it (the kit makes it smaller anyway).

Open Beauty Facts, Open Products Facts and Open Pet Food Facts have no photo route that is not blocked (the AWS
bucket holds Open Food Facts photos only; their photos are only on their own blocked image servers), so the kit's
entries for them are not built (NOT_BUILT; home_sources.py keeps their code).

Licences (unchanged): the photos are CC BY-SA 3.0, so these entries stay share-alike; the data is ODbL 1.0, so each
row's credit names Open Food Facts and the product's page (an address shown to people, never fetched).

Main parts: CACHE and build_cache (the slim local copy), products (every kept product, one by one), top_by_label (the
most scanned products of each label), details (ingredients and nutrition of chosen products), photo_url and
front_photo (a photo's address on AWS), refuse (stops code that would read a blocked site).
"""

import collections
import concurrent.futures
import glob
import gzip
import heapq
import json
import os
import re

HF_REPO = "openfoodfacts/product-database"
HF_FILE = "food.parquet"
PHOTOS = "https://openfoodfacts-images.s3.eu-west-3.amazonaws.com/data/"
# Shown to people in credits and terms (never fetched).
PRODUCT_PAGE = "https://world.openfoodfacts.org/product/{code}"
TERMS = "https://world.openfoodfacts.org/terms-of-use"
ROUTE = ("read from the Open Food Facts product database on Hugging Face (openfoodfacts/product-database) and the "
         "Open Food Facts Images dataset on AWS Open Data, never from its websites")

# Said for the entries that cannot be built (Open Beauty, Products and Pet Food Facts).
NOT_BUILT = ("not built: the source blocks AI crawlers (its robots.txt shuts out GPTBot, anthropic-ai and ClaudeBot "
             "on every host, its own photo server included, and no open bulk route holds its photos)")

# The folder in the work folder that keeps the slim copy of the database.
CACHE = "openfoodfacts-db"
# The columns read for every product (the light ones); DETAIL_COLUMNS only for chosen products.
COLUMNS = ["code", "product_name", "brands", "quantity", "lang", "countries_tags", "categories_tags",
           "unique_scans_n", "images"]
DETAIL_COLUMNS = ["code", "ingredients_text", "nutriments"]
# Row groups per part file of the slim copy (a broken download goes on from the last part made).
PART = 100
PHOTO_KIND = re.compile(r"^(front|ingredients|nutrition)_[a-z]{2}$")
TAG = re.compile(r"<[^>]+>")


def say(text):
    """Print a progress line at once (the kit's console)."""
    print(text, flush=True)


def refuse(what):
    """Stop code that would read one of the blocked Open ... Facts websites: raises RuntimeError with NOT_BUILT."""
    raise RuntimeError(f"{what}: {NOT_BUILT}")


# ----------------------------------------------------------------- the photos (AWS Open Data)

def photo_folder(code):
    """The bucket folder of a barcode: "4012359114303" -> "401/235/911/4303" (13 digits are split 3/3/3/4); shorter
    codes (EAN-8 and the like) are one folder."""
    code = str(code or "")
    if len(code) == 13 and code.isdigit():
        return "/".join([code[:3], code[3:6], code[6:9], code[9:]])
    return code


def photo_url(code, images, kind, lang="en"):
    """The AWS address of a product's chosen photo of a kind ("front", "ingredients", "nutrition") in a language,
    as uploaded ("raw"), or "" when the product has none. images: {"front_en": {"imgid": 3, ...}, ...}."""
    chosen = (images or {}).get(f"{kind}_{lang}") or {}
    imgid = chosen.get("imgid")
    if not code or not str(imgid or "").isdigit():
        return ""
    return f"{PHOTOS}{photo_folder(code)}/{int(imgid)}.jpg"


def front_photo(hit, langs=("en",)):
    """A product's front photo on AWS: the first of langs that has one ("" when none)."""
    for lang in langs:
        url = photo_url(hit.get("code"), hit.get("images"), "front", lang) if lang else ""
        if url:
            return url
    return ""


# ----------------------------------------------------------------- the product database (Hugging Face)

def texts(entries):
    """{language: text} of a database field kept per language ([{"lang": "main", "text": ...}, ...]); the first
    text of each language, without HTML marks."""
    out = {}
    for e in entries or []:
        lang, text = (e or {}).get("lang") or "", TAG.sub("", (e or {}).get("text") or "").strip()
        if lang and text and lang not in out:
            out[lang] = text
    return out


def slim(row, group):
    """One database row as the kit keeps it (the shape the older website answers had): code, names, brands,
    quantity, language, countries, English category tags, scans, the chosen photos and the row group; None for a
    product with no name, no category or no chosen photo."""
    names = texts(row.get("product_name"))
    images = {}
    for i in row.get("images") or []:
        key = (i or {}).get("key") or ""
        if PHOTO_KIND.match(key) and i.get("imgid") is not None:
            images[key] = {"imgid": int(i["imgid"]), "rev": i.get("rev")}
    categories = [t for t in row.get("categories_tags") or [] if t.startswith("en:") and t != "en:null"]
    name = names.get("main") or next(iter(names.values()), "")
    if not row.get("code") or not name or not categories or not images:
        return None
    return {"code": row["code"], "product_name": name, "product_name_en": names.get("en", ""),
            "brands": row.get("brands") or "", "quantity": row.get("quantity") or "", "lang": row.get("lang") or "",
            "countries_tags": list(row.get("countries_tags") or []), "categories_tags": categories,
            "unique_scans_n": int(row.get("unique_scans_n") or 0), "images": images, "group": group}


def revision():
    """The commit of the Hugging Face dataset now (so every part of the slim copy, and the details read later, come
    from the same file)."""
    from huggingface_hub import HfApi
    return HfApi().dataset_info(HF_REPO).sha


def open_file(rev):
    """(file system, path) of the database's food file at a revision."""
    from huggingface_hub import HfFileSystem
    return HfFileSystem(), f"datasets/{HF_REPO}@{rev}/{HF_FILE}"


def cache_folder(work):
    """The folder of a finished slim copy in the work folder (the newest), or "" when there is none."""
    done = sorted(glob.glob(os.path.join(work, CACHE, "*", "complete")), key=os.path.getmtime)
    return os.path.dirname(done[-1]) if done else ""


def build_cache(work, workers=6):
    """Make the slim copy of the database in the work folder, once: the light columns of every row group, read piece
    by piece from Hugging Face, the kept products written as gzip JSON lines, PART row groups to a file. Parts
    already made are not read again. The folder, named after the dataset's revision."""
    folder = cache_folder(work)
    if folder:
        return folder
    import pyarrow.parquet as pq
    rev = revision()
    folder = os.path.join(work, CACHE, rev[:12])
    os.makedirs(folder, exist_ok=True)
    fs, path = open_file(rev)
    with fs.open(path, block_size=1 << 20) as f:
        meta = pq.ParquetFile(f).metadata
    groups = meta.num_row_groups
    parts = [range(start, min(start + PART, groups)) for start in range(0, groups, PART)]
    say(f"  Reading the Open Food Facts product database from Hugging Face ({HF_REPO}, {groups} pieces; about "
        f"450 MB, once).")

    def one(part):
        """Write one part file (its row groups' kept products); the number of products kept."""
        out = os.path.join(folder, f"part-{part.start // PART:04d}.jsonl.gz")
        if os.path.exists(out):
            return -1
        kept = []
        with fs.open(path, block_size=1 << 20) as handle:
            reader = pq.ParquetFile(handle, metadata=meta)
            for g in part:
                for row in reader.read_row_group(g, columns=COLUMNS).to_pylist():
                    item = slim(row, g)
                    if item:
                        kept.append(item)
        with gzip.open(out + ".tmp", "wt", encoding="utf-8") as fh:
            for item in kept:
                fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        os.replace(out + ".tmp", out)
        return len(kept)

    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for done, _ in enumerate(pool.map(one, parts), 1):
            if done % 5 == 0 or done == len(parts):
                say(f"    {done} of {len(parts)} parts of the database read")
    with open(os.path.join(folder, "revision.txt"), "w", encoding="utf-8") as fh:
        fh.write(rev + "\n")
    with open(os.path.join(folder, "complete"), "w", encoding="utf-8") as fh:
        fh.write("ok\n")
    return folder


def products(work):
    """Every product of the slim copy (made first when needed), one by one, as dicts (see slim)."""
    folder = build_cache(work)
    for part in sorted(glob.glob(os.path.join(folder, "part-*.jsonl.gz"))):
        with gzip.open(part, "rt", encoding="utf-8") as fh:
            for line in fh:
                yield json.loads(line)


def top_by_label(work, labels_of, per):
    """The most scanned products of each label: labels_of(product) gives the labels a product counts for (none to
    leave it out); {label: [product, ...]}, at most per each, the most scanned first (ties: by barcode)."""
    heaps = collections.defaultdict(list)
    for hit in products(work):
        for label in labels_of(hit) or ():
            entry = (hit["unique_scans_n"], hit["code"], hit)
            if len(heaps[label]) < per:
                heapq.heappush(heaps[label], entry)
            elif entry[:2] > heaps[label][0][:2]:
                heapq.heapreplace(heaps[label], entry)
    return {label: [h for _, _, h in sorted(heap, key=lambda e: (-e[0], e[1]))] for label, heap in heaps.items()}


def nutriments(entries):
    """{"fat_100g": 3.5, ...} of the database's nutriment list (only the values per 100 g)."""
    out = {}
    for e in entries or []:
        if (e or {}).get("name") and isinstance(e.get("100g"), (int, float)):
            out[f"{e['name']}_100g"] = float(e["100g"])
    return out


def details(work, hits):
    """{code: {"ingredients_text_en", "ingredients_text", "nutriments"}} for chosen products: only their row groups
    are read again (the ingredient and nutrition columns, from the same revision as the slim copy)."""
    import pyarrow.parquet as pq
    folder = build_cache(work)
    with open(os.path.join(folder, "revision.txt"), encoding="utf-8") as fh:
        rev = fh.read().strip()
    wanted = collections.defaultdict(set)
    for hit in hits:
        wanted[hit["group"]].add(hit["code"])
    fs, path = open_file(rev)
    out = {}
    with fs.open(path, block_size=1 << 20) as handle:
        reader = pq.ParquetFile(handle)
        for n, (group, codes) in enumerate(sorted(wanted.items()), 1):
            for row in reader.read_row_group(group, columns=DETAIL_COLUMNS).to_pylist():
                if row["code"] in codes:
                    ingredients = texts(row.get("ingredients_text"))
                    out[row["code"]] = {"ingredients_text_en": ingredients.get("en", ""),
                                        "ingredients_text": ingredients.get("main", ""),
                                        "nutriments": nutriments(row.get("nutriments"))}
            if n % 200 == 0:
                say(f"    ingredients and nutrition: {n} of {len(wanted)} pieces read")
    return out

