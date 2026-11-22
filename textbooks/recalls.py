"""Vehicle and product recalls for the reference library, in the group "recalls" ("Reference, vehicle and product
recalls"), the owner's request of 2026-11-22. Keys: recalls (every book here), rcl:nhtsa (all the vehicle books),
rcl:nhtsa:<letters> (the vehicle makes starting with those letters, such as rcl:nhtsa:c), rcl:nhtsa:equipment (tires,
child seats and equipment), rcl:cpsc (consumer products).

What this module builds, in plain words, all of it works of the US government and so in the public domain:

  NHTSA vehicle recalls and technical service bulletins. The National Highway Traffic Safety Administration
    publishes every safety recall since 1967 and every manufacturer communication it has received since 1995
    (technical service bulletins, service campaigns, warranty extensions, over-the-air updates) as "flat files", tab-
    separated text in zip files on static.nhtsa.gov (its own bulk data; no robots.txt there, so nothing is refused).
    One book per vehicle make (a make with at least MIN_CAMPAIGNS recall campaigns or MIN_BULLETINS bulletins; the
    smaller makes share an "other makes" book for their letters), with one part per model and, for each model, an
    index of its model years and one page per model year holding that year's recalls IN FULL (defect, consequence,
    remedy, notes, dates, units, the "do not drive" and "park outside" warnings) and its service bulletins IN FULL
    (NHTSA's summary of each). Tires, child seats and equipment recalls get three books of their own, by brand.
  CPSC consumer product recalls. The Consumer Product Safety Commission's Recalls API (www.saferproducts.gov
    RestWebServices, its official data service for programs) gives every recall it has published: one book per
    product category (children's products and toys, furniture, kitchen and household, electrical and appliances,
    outdoor and sports, vehicles and riding toys, clothing and jewelry, tools and home improvement, and other), one
    page per recall with its products, hazard, remedy, injuries, sellers, units and the consumer contact, grouped by
    year.

Each build job downloads the files once (about 100 MB of zip files from NHTSA, or one request per year from CPSC, a
pause between requests). The vehicle makes are split by letter so that each job ends well within four hours.

Every book has its licence and notice, "published" (the newest report date in it), "version" (the files' dates),
the key and fingerprint for the weekly update check (sign(): the files' ETags, or the newest CPSC recall), and
"originals" (every file read, with its size and SHA-256 where it was downloaded whole).

refs_common.REGISTRY sends the rcl: keys here. Run from the repository's folder:
  python3 textbooks/recalls.py rcl:nhtsa:u-z --out build/textbooks --limit 3      (a small test: three makes)
  python3 textbooks/recalls.py rcl:cpsc --out build/textbooks --limit 40           (a small test: 40 recalls)
  python3 textbooks/recalls.py --list recalls
"""

import argparse
import collections
import datetime
import hashlib
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_common as R  # noqa: E402

US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"

GROUP = "recalls"
GROUPS = {GROUP: "Reference, vehicle and product recalls"}
WORDS = ("recalls", f"group:{GROUP}", "rcl:nhtsa")


def esc(text):
    """Text made safe for HTML."""
    return html.escape(text or "", quote=True)


def iso(yyyymmdd):
    """"20190306" -> "2019-03-06" ("" when it is not such a date)."""
    s = (yyyymmdd or "").strip()
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}" if re.fullmatch(r"(19|20)\d{6}", s) else ""


# ====================================================================== NHTSA

NHTSA_FILES = "https://static.nhtsa.gov/odi/ffdd"
RECALL_FILES = [f"{NHTSA_FILES}/rcl/FLAT_RCL_PRE_2010.zip", f"{NHTSA_FILES}/rcl/FLAT_RCL_POST_2010.zip"]
RECALL_README = f"{NHTSA_FILES}/rcl/RCL.txt"
# The manufacturer-communication files, five years each; the next one is tried too and used once NHTSA publishes it.
BULLETIN_FILES = [f"{NHTSA_FILES}/tsbs/TSBS_RECEIVED_{y}-{y + 4}.zip" for y in range(1995, 2030, 5)]
BULLETIN_README = f"{NHTSA_FILES}/tsbs/TSBS.txt"
NHTSA = "National Highway Traffic Safety Administration (NHTSA), US Department of Transportation"
NHTSA_SOURCE = "https://www.nhtsa.gov/nhtsa-datasets-and-apis"
NHTSA_NOTICE = ("Data of the National Highway Traffic Safety Administration (a US government work, not under "
                "copyright in the United States). NHTSA's summaries of manufacturer communications are not the "
                "bulletins themselves, which belong to the manufacturers: ask a dealer or the manufacturer for the "
                "full bulletin. To see whether a particular vehicle still needs a recall repair, enter its VIN at "
                "nhtsa.gov/recalls or call the Vehicle Safety Hotline, 1-888-327-4236.")

# The vehicle books' letters (each key one build job). Makes starting with a digit go with "a-b".
LETTER_GROUPS = ["a-b", "c", "d-f", "g-j", "k-m", "n-r", "s-t", "u-z"]
MIN_CAMPAIGNS = 20                # a make with fewer recall campaigns and fewer than MIN_BULLETINS bulletins goes into
MIN_BULLETINS = 200               # its letters' "other makes" book
EQUIPMENT_TYPES = [("T", "tires", "Tire recalls"), ("C", "child_seats", "Child seat (child restraint) recalls"),
                   ("E", "equipment", "Vehicle equipment recalls (lights, mirrors, wheelchair lifts, trailer parts, "
                                      "aftermarket parts and other equipment)")]
YES = ("Y", "YES", "1", "TRUE")


def norm_make(make):
    """A make as one key ("Mercedes-Benz" and "MERCEDES BENZ" -> "MERCEDES BENZ")."""
    return re.sub(r"[^A-Z0-9]+", " ", (make or "").upper()).strip()


def in_letters(make, letters):
    """True when the make (norm_make) belongs to the letter group "c" or "d-f" (a digit belongs to "a-b")."""
    first = make[:1]
    if not first:
        return False
    if first.isdigit():
        first = "A"
    lo, _, hi = letters.partition("-")
    return lo.upper() <= first <= (hi or lo).upper()


def zip_lines(data):
    """The lines of the text files in a zip file's bytes (Windows-1252 text, as NHTSA writes it)."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if not name.lower().endswith((".txt", ".tsv")):
                continue
            with z.open(name) as f:
                for raw in f:
                    yield raw.decode("cp1252", "replace").rstrip("\r\n")


class NhtsaData:
    """The recalls and bulletins of some makes, read from NHTSA's flat files: by (make, model, year) the recall
    campaigns and bulletin ids, with each campaign's and bulletin's text once."""

    def __init__(self):
        """Empty."""
        self.recalls = {}                                  # (campaign, recall type) -> fields
        self.recall_products = collections.defaultdict(lambda: collections.defaultdict(set))  # type -> (mk,md,yr) -> {campaign}
        self.components = collections.defaultdict(set)     # (campaign, make, model, year) -> {component}
        self.bulletins = {}                                 # NHTSA id -> fields
        self.bulletin_products = collections.defaultdict(set)   # (make, model, year) -> {NHTSA id}
        self.bulletin_components = collections.defaultdict(set)  # NHTSA id -> {component}
        self.make_names = {}                               # norm_make -> the spelling first seen
        self.dates = []

    def add_recall_line(self, line, keep):
        """One line of a recall file; keep(make, recall type) says whether its make is wanted."""
        f = line.split("\t")
        if len(f) < 23:
            return
        f += [""] * (29 - len(f))
        kind = f[10].strip().upper() or "V"
        make = norm_make(f[2])
        if not keep(make, kind):
            return
        self.make_names.setdefault(make, " ".join(f[2].split()))
        campaign = f[1].strip()
        model, year = " ".join(f[3].split()) or "(model not given)", f[4].strip() or "9999"
        if (campaign, kind) not in self.recalls:
            self.recalls[(campaign, kind)] = {
                "campaign": campaign, "manufacturer": f[7].strip() or f[14].strip(), "begin": iso(f[8]),
                "end": iso(f[9]), "units": f[11].strip(), "owners_notified": iso(f[12]), "by": f[13].strip(),
                "received": iso(f[15]), "fmvss": f[18].strip(), "defect": f[19].strip(), "consequence": f[20].strip(),
                "remedy": f[21].strip(), "notes": f[22].strip(), "mfr_campaign": f[5].strip(),
                "do_not_drive": f[27].strip().upper() in YES, "park_outside": f[28].strip().upper() in YES}
            self.dates.append(iso(f[15]))
        r = self.recalls[(campaign, kind)]
        r["do_not_drive"] = r["do_not_drive"] or f[27].strip().upper() in YES    # a warning on any row counts
        r["park_outside"] = r["park_outside"] or f[28].strip().upper() in YES
        self.recall_products[kind][(make, model, year)].add(campaign)
        self.components[(campaign, make, model, year)].add(" ".join(f[6].split()))
        part = " ".join(x for x in (f[24].strip(), f[25].strip(), f"part {f[26].strip()}" if f[26].strip() else "")
                        if x)
        if part:
            self.components[(campaign, make, model, year)].add(f"manufacturer's part: {part}")

    def add_bulletin_line(self, line, keep):
        """One line of a manufacturer-communication file; keep(make, "B") says whether its make is wanted."""
        f = line.split("\t")
        if len(f) < 14:
            return
        make = norm_make(f[7])
        if not keep(make, "B"):
            return
        self.make_names.setdefault(make, " ".join(f[7].split()))
        nid = f[0].strip()
        if nid not in self.bulletins:
            self.bulletins[nid] = {"id": nid, "document": f[3].strip(), "date": iso(f[4]) or iso(f[2]),
                                   "campaign": f[5].strip(), "type": f[6].strip() or "Communication",
                                   "summary": " ".join(f[13].split())}
            self.dates.append(iso(f[4]) or iso(f[2]))
        model, year = " ".join(f[8].split()) or "(model not given)", f[9].strip() or "9999"
        self.bulletin_products[(make, model, year)].add(nid)
        for c in f[10].split(","):
            if c.strip():
                self.bulletin_components[nid].add(" ".join(c.split()))


def year_words(year):
    """"2019" or "year not given" (9999)."""
    return "year not given" if year in ("9999", "", "0000") else year


def recall_html(r, components):
    """The full text of one recall campaign for one vehicle (or product), as HTML."""
    warn = []
    if r["do_not_drive"]:
        warn.append("<p><strong>Do not drive this vehicle</strong> until it has been repaired (NHTSA's consumer "
                    "advisory).</p>")
    if r["park_outside"]:
        warn.append("<p><strong>Park outside</strong> and away from buildings until it has been repaired (risk of "
                    "fire; NHTSA's consumer advisory).</p>")
    facts = [("Components", "; ".join(sorted(c for c in components if c))), ("Manufacturer", r["manufacturer"]),
             ("Report received by NHTSA", r["received"]), ("Owners notified", r["owners_notified"]),
             ("Units potentially affected", r["units"]), ("Recall initiated by", r["by"]),
             ("Manufactured from", r["begin"]), ("Manufactured to", r["end"]),
             ("Manufacturer's campaign number", r["mfr_campaign"]),
             ("Federal Motor Vehicle Safety Standard", r["fmvss"])]
    parts = [f"<h3>Recall {esc(r['campaign'])}</h3>"] + warn
    parts.append("<ul>" + "".join(f"<li>{esc(k)}: {esc(v)}</li>" for k, v in facts if v) + "</ul>")
    for label, key in (("Defect", "defect"), ("Consequence", "consequence"), ("Remedy", "remedy"),
                       ("Notes", "notes")):
        if r[key]:
            parts.append(f"<p>{label}: {esc(r[key])}</p>")
    return "\n".join(parts)


def bulletin_html(b, components):
    """The full NHTSA summary of one manufacturer communication, as HTML."""
    head = f"{b['type']} {b['document'] or b['id']}"
    facts = [("NHTSA ID", b["id"]), ("Date", b["date"]), ("Components", "; ".join(sorted(components))),
             ("Manufacturer's campaign or software version", b["campaign"])]
    return (f"<h3>{esc(head)}</h3><ul>" + "".join(f"<li>{esc(k)}: {esc(v)}</li>" for k, v in facts if v) +
            f"</ul><p>{esc(b['summary'])}</p>")


def year_page_html(data, make_label, make, model, year, kind="V"):
    """The page of one model year: its recalls, newest first, then its bulletins, newest first."""
    key = (make, model, year)
    campaigns = sorted(data.recall_products[kind].get(key, ()), key=lambda c: data.recalls[(c, kind)]["received"],
                       reverse=True)
    bulletins = sorted(data.bulletin_products.get(key, ()) if kind == "V" else (),
                       key=lambda i: data.bulletins[i]["date"], reverse=True)
    what = "recall" if len(campaigns) == 1 else "recalls"
    parts = [f"<p>{esc(make_label)} {esc(model)}, model {esc(year_words(year))}: {len(campaigns)} safety {what}"
             + (f" and {len(bulletins)} service bulletins and other manufacturer communications" if kind == "V" else "")
             + ".</p>"]
    if campaigns:
        parts.append("<h2>Safety recalls</h2>")
        parts += [recall_html(data.recalls[(c, kind)], data.components[(c, make, model, year)]) for c in campaigns]
    if bulletins:
        parts.append("<h2>Service bulletins and manufacturer communications</h2>")
        parts += [bulletin_html(data.bulletins[i], data.bulletin_components.get(i, set())) for i in bulletins]
    return "\n".join(parts)


def models_of(data, makes, kind="V"):
    """{(make, model): [years, newest first]} of some makes, from their recalls (of kind) and, for vehicles, their
    bulletins."""
    out = collections.defaultdict(set)
    keys = list(data.recall_products[kind]) + (list(data.bulletin_products) if kind == "V" else [])
    for make, model, year in keys:
        if make in makes:
            out[(make, model)].add(year)
    return {k: sorted(v, key=lambda y: ("0" if y == "9999" else y), reverse=True) for k, v in out.items()}


def make_book(data, name, title, makes, description, kind="V", by_make=False):
    """One Book: a part per model ("MAKE MODEL" when the book holds several makes, by_make), the model's index of
    years first, then a page per year."""
    import build_textbooks as B
    book = B.Book(name=name, title=title, subject="Vehicle safety recalls and service bulletins" if kind == "V" else
                  "Vehicle equipment, tire and child seat recalls", level="reference", group=GROUP, publisher=NHTSA,
                  country="United States", licence=US_GOV, licence_url=US_GOV_URL, source=NHTSA_SOURCE,
                  description=description, notice=NHTSA_NOTICE)
    book.changes = "NHTSA's tab-separated flat files arranged by make, model and model year"
    dates = []
    models = models_of(data, set(makes), kind)
    for n, (make, model) in enumerate(sorted(models, key=lambda m: (m[0], m[1])), 1):
        label = data.make_names.get(make, make)
        unit = f"{label} {model}" if by_make else model
        years = models[(make, model)]
        base = B.slug(f"{make}-{model}" if by_make else model, 60) or f"model-{n}"
        rows = []
        for y in years:
            key = (make, model, y)
            nr = len(data.recall_products[kind].get(key, ()))
            nb = len(data.bulletin_products.get(key, ())) if kind == "V" else 0
            counts = f"{nr} recalls" + (f", {nb} bulletins" if kind == "V" else "")
            rows.append(f'<li><a href="{base}-{y}">{esc(year_words(y))}</a>: {counts}</li>')
        book.pages.append(B.Page(base, f"{label} {model}: model years",
                                 f"<p>The model years of the {esc(label)} {esc(model)} with recalls"
                                 f"{' or bulletins' if kind == 'V' else ''}:</p><ul>{''.join(rows)}</ul>", n, unit))
        for y in years:
            book.pages.append(B.Page(f"{base}-{y}", f"{label} {model} {year_words(y)}",
                                     year_page_html(data, label, make, model, y, kind), n, unit))
            for c in data.recall_products[kind].get((make, model, y), ()):
                dates.append(data.recalls[(c, kind)]["received"])
            for i in (data.bulletin_products.get((make, model, y), ()) if kind == "V" else ()):
                dates.append(data.bulletins[i]["date"])
    book.published = B.newest_date([d for d in dates if d and d <= datetime.date.today().isoformat()])
    return book


def nhtsa_download(urls, cache, left_out, optional=False):
    """[(address, bytes)] of NHTSA's files (a missing optional file is skipped quietly)."""
    import build_textbooks as B
    out = []
    for url in urls:
        if not R.readable(url, cache):
            left_out.append({"title": url, "reason": "Not allowed by robots.txt."})
            continue
        try:
            out.append((url, B.fetch(url, cache, binary=True)))
        except urllib.error.HTTPError as e:
            if not (optional and e.code in (403, 404)):
                left_out.append({"title": url, "reason": f"It could not be read ({e.code})."})
        except (urllib.error.URLError, OSError):
            left_out.append({"title": url, "reason": "It could not be read."})
    return out


def nhtsa_books(piece, cache=None, left_out=None, limit=None):
    """The Books of one NHTSA key piece: "c" (the vehicle makes of those letters: a book each for the bigger makes,
    one "other makes" book) or "equipment" (tires, child seats, equipment). limit: only so many makes (a test)."""
    left_out = left_out if left_out is not None else []
    equipment = piece == "equipment"
    if equipment:
        def keep(make, kind):
            return kind in ("T", "C", "E")
    else:
        def keep(make, kind):
            return kind in ("V", "B") and in_letters(make, piece)
    recall_files = nhtsa_download(RECALL_FILES, cache, left_out)
    bulletin_files = [] if equipment else nhtsa_download(BULLETIN_FILES, cache, left_out, optional=True)
    if not recall_files:
        return []
    data = NhtsaData()
    for _url, blob in recall_files:
        for line in zip_lines(blob):
            data.add_recall_line(line, keep)
    for _url, blob in bulletin_files:
        for line in zip_lines(blob):
            data.add_bulletin_line(line, keep)
    originals = [{"url": u, "kind": "zip", "size": len(b), "sha256": hashlib.sha256(b).hexdigest()}
                 for u, b in recall_files + bulletin_files] + [{"url": RECALL_README, "kind": "txt"}] + \
        ([] if equipment else [{"url": BULLETIN_README, "kind": "txt"}])
    stamp = datetime.date.today().isoformat()
    version = f"NHTSA flat files read {stamp} ({len(recall_files)} recall files" + \
        ("" if equipment else f", {len(bulletin_files)} bulletin files") + ")"
    books = []
    if equipment:
        for kind, name, title in EQUIPMENT_TYPES:
            makes = sorted({m for m, _md, _y in data.recall_products[kind]})
            if limit:
                makes = makes[:limit]
            book = make_book(data, f"nhtsa_{name}_recalls", f"NHTSA {title}", makes,
                             f"Every NHTSA {title.lower()[:1] + title[1:]} since 1967, by brand and product, each "
                             "recall in full (defect, consequence, remedy, notes, dates and units).", kind, True)
            books.append(book)
    else:
        per_make = collections.defaultdict(set)
        for (make, _md, _y), cs in data.recall_products["V"].items():
            per_make[make] |= cs
        bull = collections.defaultdict(set)
        for (make, _md, _y), ids in data.bulletin_products.items():
            bull[make] |= ids
        makes = sorted(set(per_make) | set(bull))
        big = [m for m in makes if len(per_make.get(m, ())) >= MIN_CAMPAIGNS or len(bull.get(m, ())) >= MIN_BULLETINS]
        small = [m for m in makes if m not in big]
        if limit:
            big, small = big[:limit], small[:limit]
        for make in big:
            label = data.make_names.get(make, make)
            books.append(make_book(data, f"nhtsa_{B_slug(make)}", f"{label}: vehicle recalls and service bulletins "
                                   "(NHTSA)", [make],
                                   f"Every NHTSA safety recall (since 1967) and every service bulletin and other "
                                   f"manufacturer communication NHTSA has received (since 1995) for {label} "
                                   "vehicles, by model; each model has an index of its model years and a page per "
                                   "year with the recalls and bulletins in full."))
        if small:
            books.append(make_book(data, f"nhtsa_other_makes_{piece.replace('-', '_')}",
                                   f"Other vehicle makes {piece.upper()}: recalls and service bulletins (NHTSA)",
                                   small, f"The NHTSA recalls and bulletins of the smaller vehicle makes (motorhomes, "
                                   f"trailers, buses, motorcycles and others) starting with {piece.upper()}, by make "
                                   "and model, with a page per model year.", "V", True))
    for book in books:
        book.version = version
        book.originals = list(originals)
    return books


def B_slug(text):
    """A book-name piece of a make ("MERCEDES BENZ" -> "mercedes_benz")."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40] or "make"


def nhtsa_sign(piece):
    """The weekly check's sign of an NHTSA key: the ETag, date and size of each file it reads."""
    import build_textbooks as B
    import updates
    signs = []
    for url in RECALL_FILES + ([] if piece == "equipment" else BULLETIN_FILES):
        time.sleep(B.PAUSE)
        signs.append(f"{url}|{updates.head_signs(url)}")
    return hashlib.sha256("\n".join(signs).encode()).hexdigest()[:24]


# ====================================================================== CPSC

CPSC_API = "https://www.saferproducts.gov/RestWebServices/Recall"
CPSC_SOURCE = "https://www.cpsc.gov/Recalls"
CPSC_DOCS = "https://www.cpsc.gov/Recalls/CPSC-Recalls-Application-Program-Interface-API-Information"
CPSC = "US Consumer Product Safety Commission (CPSC)"
CPSC_NOTICE = ("Recall notices of the US Consumer Product Safety Commission (a US government work, not under "
               "copyright in the United States), read from CPSC's Recalls API. Company names and trademarks belong "
               "to their owners. The pictures of the recalled products are not included; their captions are. To "
               "report an unsafe product: saferproducts.gov, or CPSC's hotline 1-800-638-2772.")
FIRST_YEAR = 1973                  # the CPSC was created in 1973

# The books, in order, with the words of a product's "Type" (CPSC's product type) that put a recall in them; the first
# that matches wins; "other" takes the rest.
CPSC_CATEGORIES = [
    ("children", "Children's products, toys and nursery items",
     r"child|kid|toy|baby|infant|crib|bassinet|stroller|nursery|play ?yard|high ?chair|pacifier|teeth|rattle|doll|"
     r"game|puzzle|youth|juvenile|bath seat|carrier|sling|walker|bouncer|swing|rocker|bib|school|art supplies"),
    ("vehicles", "Bicycles, e-bikes, scooters, ATVs and riding products",
     r"bicycl|bike|scooter|hoverboard|skateboard|atv|all.terrain|off.road|go.kart|minibike|moped|golf cart|"
     r"utility vehicle|snowmobile|helmet|riding"),
    ("electrical", "Electrical products, electronics, batteries, heating and lighting",
     r"electric|electronic|battery|batteries|charger|power ?(?:bank|strip|supply|adapter|cord)|extension cord|"
     r"outlet|light|lamp|bulb|heater|heating|fan\b|fans\b|air condition|dehumidif|humidif|computer|phone|tablet|"
     r"laptop|audio|speaker|headphone|television|smoke alarm|carbon monoxide|detector|generator|cord"),
    ("furniture", "Furniture, beds, mattresses and window coverings",
     r"furniture|dresser|chest|table|chair|sofa|couch|bed\b|beds\b|bunk|mattress|cabinet|shel|desk|wardrobe|"
     r"window (?:blind|cover|shade)|blind|shade|curtain|futon|ottoman|stool|bench|nightstand|headboard|carpet|rug|"
     r"pillow"),
    ("kitchen", "Kitchen, cooking and household products",
     r"kitchen|cook|pot\b|pan\b|kettle|blender|mixer|food processor|coffee|toaster|microwave|oven|range|stove|"
     r"grill|fryer|knife|knives|utensil|cup|mug|glass|bottle|dish|container|household|cleaning|vacuum|candle|"
     r"decor|houseware|appliance|refrigerat|freezer|washing machine|dishwasher|espresso|dehydrator|sewing"),
    ("outdoor", "Outdoor, garden, sports and recreation products",
     r"outdoor|garden|lawn|mower|trimmer|chain ?saw|leaf blower|pool|spa|hot tub|camp|tent|sport|exercise|fitness|"
     r"treadmill|ball|fishing|hunting|boat|kayak|trampoline|playground|swing set|patio|fire ?pit|firework|"
     r"recreation|golf|ski|snow|scuba|diving|climbing|archery|hammock|air rifle|bb gun|tractor|log split"),
    ("clothing", "Clothing, footwear, jewelry and personal care",
     r"cloth|apparel|garment|shirt|pant|dress|jacket|coat|sweat|pajama|sleepwear|robe|hood|drawstring|shoe|"
     r"boot|sandal|footwear|jewel|necklace|bracelet|earring|cosmetic|personal care|hair|dryer|razor|watch|bag|"
     r"backpack|purse"),
    ("tools", "Tools, hardware and home improvement",
     r"tool|drill|saw\b|saws\b|ladder|hardware|paint|lumber|build|construction|plumbing|water heater|furnace|"
     r"boiler|gas|valve|door|window|gate|garage|lock|fastener|welding|compressor|pressure washer|home improvement"),
    ("other", "Other consumer products", r"."),
]


def category_of(recall):
    """The CPSC book (CPSC_CATEGORIES name) of one recall, from its products' types, names and its title."""
    words = " ".join([p.get("Type") or "" for p in recall.get("Products") or []] +
                     [p.get("Name") or "" for p in recall.get("Products") or []] + [recall.get("Title") or ""]).lower()
    for name, _title, pattern in CPSC_CATEGORIES:
        if re.search(pattern, words):
            return name
    return "other"


def cpsc_recall_html(r):
    """The full text of one CPSC recall, as HTML."""
    def names(field, key="Name"):
        return [" ".join(str(x.get(key) or "").split()) for x in r.get(field) or [] if (x.get(key) or "").strip()]
    parts = []
    date = (r.get("RecallDate") or "")[:10]
    parts.append(f"<p>Recall number {esc(str(r.get('RecallNumber') or ''))}, {esc(date)}.</p>")
    if r.get("Description"):
        parts.append(f"<p>{esc(r['Description'])}</p>")
    products = []
    for p in r.get("Products") or []:
        bits = [x for x in (p.get("Name"), p.get("Model") and f"model {p['Model']}", p.get("Type") and
                            f"type: {p['Type']}", p.get("NumberOfUnits") and f"units: {p['NumberOfUnits']}") if x]
        if bits:
            products.append(", ".join(" ".join(str(b).split()) for b in bits))
    for heading, items in (("Products", products), ("Hazard", names("Hazards")), ("Remedy", names("Remedies")),
                           ("Remedy options", names("RemedyOptions", "Option")), ("Injuries", names("Injuries")),
                           ("Manufacturers", names("Manufacturers")), ("Importers", names("Importers")),
                           ("Distributors", names("Distributors")), ("Sold at", names("Retailers")),
                           ("Made in", names("ManufacturerCountries", "Country")),
                           ("UPC codes", names("ProductUPCs", "UPC")),
                           ("Recalled together with", names("Inconjunctions", "URL")),
                           ("Pictures (captions only)", names("Images", "Caption"))):
        if items:
            parts.append(f"<h2>{esc(heading)}</h2>" + ("<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"
                                                      if len(items) > 1 else f"<p>{esc(items[0])}</p>"))
    if r.get("ConsumerContact"):
        parts.append(f"<h2>Consumer contact</h2><p>{esc(' '.join(r['ConsumerContact'].split()))}</p>")
    if r.get("URL"):
        parts.append(f"<p>CPSC's recall page: <a href=\"{esc(r['URL'])}\">{esc(r['URL'])}</a></p>")
    return "\n".join(parts)


def cpsc_recalls(cache=None, left_out=None, years=None):
    """Every CPSC recall (the API asked one year at a time, a pause between), oldest first."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    out, seen = [], set()
    for year in years or range(FIRST_YEAR, datetime.date.today().year + 1):
        url = f"{CPSC_API}?format=json&RecallDateStart={year}-01-01&RecallDateEnd={year}-12-31"
        try:
            rows = json.loads(B.fetch(url, cache if year < datetime.date.today().year else None))
        except (urllib.error.URLError, OSError, ValueError):
            left_out.append({"title": f"CPSC recalls of {year}", "reason": "The Recalls API could not be read."})
            continue
        for r in rows if isinstance(rows, list) else []:
            if r.get("RecallID") not in seen:
                seen.add(r.get("RecallID"))
                out.append(r)
    return sorted(out, key=lambda r: (r.get("RecallDate") or "", str(r.get("RecallNumber") or "")))


def cpsc_books(cache=None, left_out=None, limit=None):
    """The CPSC Books: one per category, one page per recall (newest year first), grouped by year."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    if not R.api_readable(CPSC_API, cache):
        left_out.append({"title": "CPSC recalls", "reason": "The Recalls API's site refuses programs in robots.txt or "
                         "shuts out AI readers."})
        return []
    recalls = cpsc_recalls(cache, left_out)
    if limit:
        recalls = recalls[-limit:]
    by_cat = collections.defaultdict(list)
    for r in recalls:
        by_cat[category_of(r)].append(r)
    books = []
    stamp = datetime.date.today().isoformat()
    for name, title, _pattern in CPSC_CATEGORIES:
        rows = by_cat.get(name) or []
        if not rows:
            continue
        book = B.Book(name=f"cpsc_recalls_{name}", title=f"CPSC recalls: {title}", subject="Consumer product "
                      "recalls", level="reference", group=GROUP, publisher=CPSC, country="United States",
                      licence=US_GOV, licence_url=US_GOV_URL, source=CPSC_SOURCE,
                      description=f"Every recall of {title.lower()} the US Consumer Product Safety Commission has "
                                  "published (from 1973), one page each with the products, the hazard, the remedy, "
                                  "injuries, where they were sold and how to contact the company; newest first, "
                                  "grouped by year.", notice=CPSC_NOTICE)
        book.changes = "CPSC's Recalls API records written out as pages (pictures left out, their captions kept)"
        years = sorted({(r.get("RecallDate") or "0000")[:4] for r in rows}, reverse=True)
        number = {y: i for i, y in enumerate(years, 1)}
        for r in sorted(rows, key=lambda r: r.get("RecallDate") or "", reverse=True):
            year = (r.get("RecallDate") or "0000")[:4]
            title_r = " ".join((r.get("Title") or f"Recall {r.get('RecallNumber')}").split())
            book.pages.append(B.Page(f"recall-{r.get('RecallID')}", title_r, cpsc_recall_html(r), number[year],
                                     f"Recalls of {year}"))
        book.published = max((r.get("RecallDate") or "")[:10] for r in rows)
        book.version = f"CPSC Recalls API read {stamp} ({len(rows)} recalls; the newest published " \
                       f"{max((r.get('LastPublishDate') or '')[:10] for r in rows)})"
        book.originals = [{"url": CPSC_API + "?format=json", "kind": "json"}, {"url": CPSC_DOCS, "kind": "html"}]
        books.append(book)
    return books


def cpsc_sign():
    """The weekly check's sign of the CPSC books: the recalls published or changed in the last 120 days (id and
    last publish date)."""
    import build_textbooks as B
    since = (datetime.date.today() - datetime.timedelta(days=120)).isoformat()
    rows = json.loads(B.fetch(f"{CPSC_API}?format=json&LastPublishDateStart={since}", None))
    marks = sorted(f"{r.get('RecallID')}|{r.get('LastPublishDate')}" for r in rows if isinstance(r, dict))
    return hashlib.sha256("\n".join(marks).encode()).hexdigest()[:24]


# ====================================================================== keys, signs, the build

def all_keys():
    """Every build key of this module."""
    return [f"rcl:nhtsa:{g}" for g in LETTER_GROUPS] + ["rcl:nhtsa:equipment", "rcl:cpsc"]


def knows(word):
    """True when word is one of this module's request words or keys."""
    return word in WORDS or word.startswith("rcl:")


def expand_keys(words):
    """The keys the words stand for: "recalls" or "group:recalls" (every book), "rcl:nhtsa" (the vehicle and
    equipment books), or one key (kept as it is)."""
    keys = []
    for w in words:
        if w in ("recalls", f"group:{GROUP}"):
            keys += all_keys()
        elif w == "rcl:nhtsa":
            keys += [k for k in all_keys() if k.startswith("rcl:nhtsa:")]
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change of one key ("" when it cannot be asked: then nothing is rebuilt)."""
    parts = key.split(":")
    try:
        if parts[1] == "nhtsa" and (parts[2] in LETTER_GROUPS or parts[2] == "equipment"):
            return nhtsa_sign(parts[2])
        if parts[1] == "cpsc":
            return cpsc_sign()
    except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError):
        return ""
    return ""


def books_for(key, work, cache=None, left_out=None, limit=None):
    """The Books of one key, or [] (the reason in left_out)."""
    left_out = left_out if left_out is not None else []
    parts = key.split(":")
    if len(parts) == 3 and parts[1] == "nhtsa" and (parts[2] in LETTER_GROUPS or parts[2] == "equipment"):
        return nhtsa_books(parts[2], cache, left_out, limit)
    if key == "rcl:cpsc":
        return cpsc_books(cache, left_out, limit)
    left_out.append({"title": key, "reason": "Unknown key."})
    return []


def build(keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys into out_dir with one manifest per key (refs_common.build_keys)."""
    return R.build_keys(R._module("recalls"), keys, out_dir, cache, date, limit)  # (also when run as a script)


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "nhtsa_flat_files": "static.nhtsa.gov/odi/ffdd/ (NHTSA's recall and manufacturer-communication flat files): works "
                        "of the US government (17 U.S.C. 105). static.nhtsa.gov has no robots.txt (404, checked "
                        "2026-11-22), so nothing is refused; www.nhtsa.gov answers programs with \"Access Denied\" "
                        "and is not read (only named as the data's home page). The file layouts are in RCL.txt and "
                        "TSBS.txt next to the files.",
    "cpsc_recalls_api": "www.saferproducts.gov/RestWebServices/Recall (CPSC's Recalls API, its official data service "
                        "for programs, no key needed): works of the US government (17 U.S.C. 105). The site answers "
                        "the address of its robots.txt with a firewall's \"Access Denied\" (no robots rules); the "
                        "robots.txt standard (RFC 9309) treats that as no rules, and the API itself answers programs "
                        "(checked 2026-11-22). One request per year of recalls, with a pause.",
}

NOT_INCLUDED = [
    ("NHTSA recalls API (api.nhtsa.gov) and nhtsa.gov recall pages", "Not needed: the same recalls and bulletins are "
     "in NHTSA's flat files, which are read whole instead (one download per build, kinder to NHTSA's servers than "
     "one request per make, model and year). www.nhtsa.gov refuses programs. To look up one vehicle by VIN: "
     "https://www.nhtsa.gov/recalls"),
    ("The manufacturers' full technical service bulletins", "Copyrighted by each manufacturer (NHTSA publishes only "
     "its summary of each, which is in the books). The full bulletins are sold through the manufacturers' service "
     "sites; NHTSA's own copies (static.nhtsa.gov/odi/tsbs/) are documents the manufacturers sent, not US "
     "government works, so they are not copied. Index for the Program Downloader: https://www.nhtsa.gov/recalls"),
    ("NHTSA complaints and investigations files (FLAT_CMPL, investigations)", "Left out: they are owners' complaints "
     "and defect investigations, not recalls or bulletins (the request). Index: "
     "https://www.nhtsa.gov/nhtsa-datasets-and-apis"),
    ("CPSC recall pictures", "Left out: the books are text for screen readers (each picture's caption is kept), and "
     "some pictures are the companies' own photographs."),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["recalls"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many makes or recalls")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
