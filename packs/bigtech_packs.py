"""Pack builders for the picture collections that big technology companies publish OPENLY (Google, IBM): used by
build_packs.py in the same way as its own PACKS. Each builder is build_<key>(limit) and returns [(file name, JPEG bytes
or None, row)], where a row is {"question", "answer", "credit"}. A picture with more than one question comes once
with its JPEG and then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins).
The limit counts pictures.

Most big-company picture sets are NOT open even when their words are: their pictures were taken from the web (LAION,
Conceptual Captions, PixMo, MetaCLIP, DataComp ...), or need a signed agreement (SA-1B, Ego4D, Aria), or are for
research only. Those are in training-kit/kit/bigtech_sources.py (research entries, sign-up notes and the reasons
others are left out). Only sets whose PICTURES are themselves openly licensed become packs here.

Every answer is a fixed sentence written here from the source's own records: the product name Google gave its 3D
scan, the labels people checked on a photo, the words printed in a table. Nothing is written by an AI model.

The packs (all open; checked at the source in November 2026):
  gso_objects       Google Scanned Objects (Downs et al., Google Research, 2022): 3D scans of about 1,000 real
                    household products, toys, shoes and kitchen things, published on Gazebo Fuel, each model marked
                    "Creative Commons Attribution 4.0 International" (the Fuel API's license_name for every model;
                    https://app.gazebosim.org/GoogleResearch/fuel/models). The pictures are Fuel's own rendered views
                    of each scan (640 x 460), so every answer starts "This is a computer-made picture of a 3D scan
                    of a real product, not a photo." and then names the product as Google named it. No people.
  oi_crowdsourced   Open Images Extended, Crowdsourced (Google, 2018-2019): photos that people around the world,
                    most of them in India, gave through the Google Crowdsource app, of household objects, plants,
                    animals and food. Each photo's own licence is in the image list (every one read so far is
                    https://creativecommons.org/licenses/by/4.0/, with the giver's name) and each is checked; the
                    labels were checked by people at Google (labels CC BY 4.0, like Open Images).
                    "What is in this picture?" from the giver's own tag that people confirmed, and "Is there ... in
                    this picture?" answered yes and no from labels people confirmed or rejected. Photos with any
                    label of a person, a face or a body part are left out (the givers' photos of people at work have
                    blurred faces), so the pack shows things only. The photos come in ten 6.5 GB archives; each pass
                    reads one archive from the start until it has enough (a top-up pass reads the next archive).
  pubtabnet_tables  Tables from scientific articles, read out: PubTabNet (Zhong, ShafieiBavani and Jimeno Yepes, IBM
                    Research, 2020; annotations CDLA-Permissive-1.0), from IBM's own copy on Hugging Face
                    (ds4sd/PubTabNet_OTSL). Its table pictures are cut from articles of the PubMed Central Open
                    Access Subset, whose articles keep their own licences ("IBM does not own the copyright of the
                    images", the PubLayNet README), so each article's licence is checked with Europe PMC and only
                    tables from articles under CC BY or CC0 are used, each credited to its article. "Read this table
                    to me." with the table's words row by row, and "How many rows and columns does this table
                    have?". Tables over 15 rows, 6 columns or about 220 words, or mostly blank, are left out.

Nothing is set aside for a description (build_packs.needs_description): every answer comes from the source's own
records, so no picture is dropped for a missing description.

    python packs/bigtech_packs.py gso_objects --limit 4      (prints a few rows: a quick check)
"""

import collections
import csv
import html
import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import (session, clean, say, considered, listing_out_of_time, out_of_time, fetch_all, pass_random,
                         smaller, note_source, already_in_pack, article)
from food_packs import with_twins, count_pictures, oi_lines, oi_licence_name, OI_CLASSES, OI

WHAT_Q = "What is this?"
IN_Q = "What is in this picture?"
READ_Q = "Read this table to me."
SIZE_Q = "How many rows and columns does this table have?"


# ----------------------------------------------------------------- gso_objects (Google Scanned Objects)

GSO_LIST = "https://fuel.gazebosim.org/1.0/GoogleResearch/models"
GSO_THUMB = "https://fuel.gazebosim.org/1.0/GoogleResearch/models/{name}/tip/files/thumbnails/{view}.jpg"
GSO_PAGE = "https://app.gazebosim.org/GoogleResearch/fuel/models/{name}"
GSO_CREDIT = ("Google Scanned Objects (Laura Downs, Anthony Francis, Nate Koenig and others, Google Research, 2022), "
              "CC BY 4.0, {page}")
GSO_FREE = re.compile(r"Attribution 4\.0", re.I)
GSO_VIEWS = 5                       # Fuel keeps five rendered views of each scan (thumbnails/0.jpg ... 4.jpg)
# Fuel's categories, as a few words the answer can use ("" says nothing more).
GSO_KINDS = {"toys": "a toy", "stuffed toys": "a soft toy", "shoe": "a shoe", "action figures": "a toy figure",
             "board games": "a board game", "bottles and cans and cups": "a container: a bottle, can, jar or cup",
             "hat": "a hat",
             "headphones": "headphones", "keyboard": "a computer keyboard", "mouse": "a computer mouse",
             "camera": "a camera", "bag": "a bag", "car seat": "a car seat", "legos": "a LEGO set",
             "media cases": "a case for a disc or game", "consumer goods": ""}
GSO_NOT_A_NAME = re.compile(r"^(test|todo|none|n/?a)\.?$", re.I)


def gso_name(model):
    """The product's name as Google gave it: the first line of the model's description ("Vtech Roll & Learn Turtle"),
    or its Fuel name with spaces ("Vtech_Roll_Learn_Turtle" -> "Vtech Roll Learn Turtle") when the description is
    empty or only a placeholder."""
    for line in str(model.get("description") or "").splitlines():
        line = clean(line)
        if line and not GSO_NOT_A_NAME.match(line):
            return line
    return clean(str(model.get("name") or "").replace("_", " "))


def gso_rows(model):
    """The row for one scanned model, or None when its licence is not CC BY 4.0 or it has no name."""
    name = str(model.get("name") or "")
    if not name or not GSO_FREE.search(str(model.get("license_name") or "")):
        return None
    product = gso_name(model)
    if not product:
        return None
    kinds = [GSO_KINDS.get(str(c).strip().lower(), "") for c in (model.get("categories") or [])]
    kind = next((k for k in kinds if k), "")
    answer = ("This is a computer-made picture of a 3D scan of a real product, not a photo. The product is: "
              f"{product.rstrip('.')}." + (f" It is {kind}." if kind else ""))
    return {"question": WHAT_Q, "answer": answer, "credit": GSO_CREDIT.format(page=GSO_PAGE.format(name=name))}


def gso_models(s):
    """Every model of the GoogleResearch owner on Gazebo Fuel (about 1,030), page by page."""
    out, page = [], 1
    while not listing_out_of_time():
        r = s.get(GSO_LIST, params={"per_page": 100, "page": page}, timeout=120)
        if r.status_code != 200:
            break
        batch = r.json() or []
        if not batch:
            break
        out += batch
        page += 1
        time.sleep(0.5)
    return out


def build_gso_objects(limit):
    """The Google Scanned Objects pack: for each model one rendered view (the first, then a second view of each
    model while the limit allows), "What is this?" with the product's name."""
    s, rng = session(), pass_random("gso_objects")
    models = gso_models(s)
    say(f"Google Scanned Objects: {len(models)} models listed")
    firsts, seconds = [], []
    for model in models:
        row = gso_rows(model)
        if row is None:
            considered(str(model.get("name") or ""), "", "its licence is not CC BY 4.0, or it has no name")
            continue
        name = model["name"]
        views = list(range(GSO_VIEWS))
        rng.shuffle(views)
        for i, view in enumerate(views[:2]):
            item = (f"gso-{name}-{view}.jpg", GSO_THUMB.format(name=name, view=view), row)
            (firsts if i == 0 else seconds).append(item)
    rng.shuffle(firsts)
    rng.shuffle(seconds)
    items = (firsts + seconds)[:int(limit * 1.05) + 2]
    fetched = fetch_all(items, workers=4, pause=0.2)[:limit]
    say(f"Google Scanned Objects: {len(fetched)} pictures")
    return fetched


# ----------------------------------------------------------------- oi_crowdsourced (Open Images Extended)

OIE = "https://storage.googleapis.com/open-images-extended/"
OIE_IDS = OIE + "extended-crowdsourced-image-ids.csv"            # 126 MB: licence, giver's name, rotation
OIE_LABELS = OIE + "extended-crowdsourced-image-labels.csv"      # 48 MB: ImageID, Source, LabelName, Confidence
OIE_SET = OIE + "extended-crowdsourced-images-{n}.tar.gz"        # ten archives of about 6.5 GB
OIE_SETS = 10
OIE_CLASSES_OLD = OI + "2018_04/class-descriptions.csv"          # labels the V7 class list may lack
OIE_CREDIT = ("Photo by {author}, {licence}, Google Crowdsource (Open Images Extended, Crowdsourced; Google, labels "
              "CC BY 4.0), https://storage.googleapis.com/openimages/web/extended.html#crowdsourced")
# Labels that show a person, a face or a body part: such photos are left out (the pack shows things only).
OIE_PEOPLE = re.compile(r"\b(person|people|man|men|woman|women|boy|girl|child\w*|kid|bab(y|ies)|toddler|infant|"
                        r"human|face|facial|smile|selfie|portrait|head|hair\w*|beard|moustache|mustache|eye\w*|nose|"
                        r"mouth|lip|ear|tooth|teeth|hand|finger|nail|arm|leg|foot|feet|knee|skin|tattoo|"
                        r"skull|chin|cheek|forehead|neck|shoulder|thigh|toe|"
                        r"player|worker|officer|police\w*|soldier|chef|cook|doctor|nurse|teacher|student|farmer|"
                        r"vendor|dancer|musician|singer|bride|groom|crowd|team|family|tradesman|"
                        r"construction worker|businessperson|gentleman|lady|male|female|fashion|model|"
                        r"sitting|standing|walking|gesture|fun|event|party|wedding|ceremony|festival)\b", re.I)
# Labels that say nothing about what is in the picture (colours, shapes, kinds of photo, design words).
OIE_VAGUE = re.compile(r"^(product|font|material property|rectangle|circle|triangle|square|pattern|line|symmetry|"
                       r"photography|close-up|macro photography|still life( photography)?|snapshot|darkness|light|"
                       r"tints and shades|colorfulness|electric blue|magenta|black|white|red|blue|green|yellow|purple|"
                       r"pink|brown|orange|grey|gray|beige|peach|violet|aqua|turquoise|teal|azure|maroon|gold|silver|"
                       r"art|visual arts|design|graphic design|logo|brand|text|label|number|graphics|illustration|"
                       r"organism|adaptation|space|technology|metal|plastic|wood|glass|paper|transparent material|"
                       r"composite material|monochrome( photography)?|black-and-white|style|sky|water|liquid|fluid|"
                       r"recreation|leisure|world|automotive design|interior design|room|still life|"
                       r"landscape|natural environment|natural landscape|plant|terrestrial plant|flowering plant|"
                       r"food|ingredient|cuisine|dish|recipe|produce|natural foods|tableware|serveware)$", re.I)


# Labels that name a stuff, not one thing ("glitter", "lighting", "rice"): no "a" before them, and no "Is there ...?"
# question about them (the label list has no grammar, so these are guessed from their endings and a short list).
OIE_MASS = re.compile(r"(ing|ware|wear|ery|ry|ice|ics|ism|ness|ment|ure|age)$|^(.* )?(glitter|tape|rice|bread|meat|"
                      r"sugar|salt|flour|butter|cheese|chocolate|candy|ice cream|yogurt|honey|milk|juice|tea|coffee|"
                      r"oil|water|soil|sand|grass|foliage|vegetation|smoke|fire|fog|snow|ice|money|cash|mail|"
                      r"luggage|furniture|equipment|machinery|hardware|software|jewellery|jewelry|makeup|paint|"
                      r"soap|shampoo|toothpaste|medicine|seafood|poultry|pasta|cereal|wool|cotton|silk|leather|"
                      r"denim|lace|rope|wire|cable|thread|yarn|fabric|textile|cloth|laundry|garbage|waste|litter|"
                      r"air force|army|navy|traffic|weather|art|music|text|writing|graffiti)$", re.I)


def oie_said(name):
    """How an answer names a label: lower case unless every word starts with a capital (a name such as "Taj
    Mahal"), or the second letter is a capital too ("TV stand", "LED lamp")."""
    name = re.sub(r"\s*\([^)]*\)", "", name).strip() or name          # "Pastel (Art)" -> "Pastel"
    words = name.split()
    proper = len(words) > 1 and all(w[:1].isupper() for w in words)
    return name if proper or name[1:2].isupper() else name[:1].lower() + name[1:]


def oie_countable(name):
    """True when a label names one thing that "a" or "an" can go before (not a stuff, not plural, not a name)."""
    said = oie_said(name)
    return said[:1].islower() and not said.endswith("s") and not OIE_MASS.search(said)


def oie_listed(things):
    """ "cup", "cup and spoon", "cup, spoon and plate"."""
    return things[0] if len(things) == 1 else ", ".join(things[:-1]) + " and " + things[-1]


def oie_rows(labels, names, rng):
    """Rows for one photo from its labels {mid: (source, confidence)} (source "tag-verification": the giver's own tag,
    checked by people; "verification": a label people checked), or [] when the photo is left out: a label of a
    person or body part people confirmed, or no confirmed label that says what is in it. The labels are said as a
    list, as the open_images_objects pack does ("In this photo: pressure cooker and spoon."); "Is there ...?" is
    asked only about labels that name one countable thing."""
    present, tagged, absent = [], [], []
    for mid, (source, confidence) in labels.items():
        name = names.get(mid)
        if not name:
            continue
        if confidence == 1:
            if OIE_PEOPLE.search(name):
                return []
            if not OIE_VAGUE.match(name):
                (tagged if source == "tag-verification" else present).append(name)
        elif confidence == 0 and not OIE_VAGUE.match(name) and not OIE_PEOPLE.search(name):
            absent.append(name)
    shown = sorted(set(tagged)) + sorted(set(present) - set(tagged))
    if not shown:
        return []
    rows = [{"question": IN_Q, "answer": f"In this photo: {oie_listed([oie_said(n) for n in shown[:4]])}."}]
    countable = [n for n in shown[:4] if oie_countable(n)]
    if countable:
        yes = oie_said(rng.choice(countable))
        rows.append({"question": f"Is there {article(yes)} {yes} in this picture?",
                     "answer": f"Yes, there is {article(yes)} {yes} in this picture."})
    absent = [n for n in sorted(set(absent) - set(shown)) if oie_countable(n)]
    if absent:
        no = oie_said(rng.choice(absent))
        rows.append({"question": f"Is there {article(no)} {no} in this picture?",
                     "answer": f"No, I can't see {article(no)} {no} in this picture."})
    return rows


def oie_names(s):
    """{mid: label name} from the Open Images class lists (V7 first, then the 2018 list for older labels)."""
    names = {}
    for url in (OI_CLASSES, OIE_CLASSES_OLD):
        try:
            for line in csv.reader(oi_lines(s, url)):
                if len(line) == 2:
                    names.setdefault(line[0], line[1])
        except Exception as e:  # noqa: BLE001 - the other list is enough
            say(f"  Open Images class list {url} could not be read ({e})")
    return names


def oie_candidates(s, rng):
    """{image id: (file name, rows with credit)}: photos whose own licence is free, that need no turning, and whose
    labels give rows (oie_rows)."""
    names = oie_names(s)
    labels = collections.defaultdict(dict)
    for cells in csv.reader(oi_lines(s, OIE_LABELS)):
        if len(cells) == 4 and cells[0] != "ImageID":
            try:
                confidence = round(float(cells[3]))
            except ValueError:
                continue
            old = labels[cells[0]].get(cells[2])
            if old is None or cells[1] == "tag-verification":
                labels[cells[0]][cells[2]] = (cells[1], confidence)
    say(f"Open Images Extended: {len(labels)} crowdsourced photos with checked labels")
    out = {}
    for r in csv.DictReader(oi_lines(s, OIE_IDS)):
        image_id = r.get("ImageID") or ""
        if image_id not in labels:
            continue
        name = f"oie-{image_id}.jpg"
        licence = oi_licence_name(r.get("License") or "", image_id)
        if not licence:
            continue
        if (r.get("Rotation") or "0") not in ("0", "0.0", "", "nan"):
            considered(name, "", "the photo needs turning")
            continue
        rows = oie_rows(labels[image_id], names, rng)
        if not rows:
            considered(name, "", "it shows a person or a body part, or no label says what is in it")
            continue
        author = clean(r.get("Author")) or "an unnamed giver"
        credit = OIE_CREDIT.format(author=author, licence=licence)
        out[image_id] = (name, [dict(row, credit=credit) for row in rows])
    say(f"Open Images Extended: {len(out)} free photos of things")
    return out


def oie_archive_pictures(url, wanted, limit):
    """Read one crowdsourced archive from the web, member by member, keeping the wanted photos ({image id: (file
    name, rows)}) until limit; [(file name, JPEG bytes, rows)]. Stops at the build's time limit."""
    import tarfile
    out, s = [], session()
    with s.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        try:
            with tarfile.open(fileobj=r.raw, mode="r|gz") as tar:
                for member in tar:
                    if len(out) >= limit or out_of_time():
                        break
                    image_id = member.name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                    if image_id not in wanted or not member.isfile():
                        continue
                    name, rows = wanted[image_id]
                    source = f"{url}#{image_id}"
                    if already_in_pack(name, source):
                        continue
                    data = smaller(tar.extractfile(member).read())
                    considered(name, source, "" if data else "the picture could not be read, or is tiny")
                    if data:
                        note_source(name, source)
                        out.append((name, data, rows))
        except Exception as e:  # noqa: BLE001 - keep what was read
            say(f"  The archive stopped early ({str(e).splitlines()[0][:120]}); what was read is used.")
    return out


def build_oi_crowdsourced(limit):
    """The Open Images Extended crowdsourced pack: the checked labels and the image list are read, then one archive
    (the pass's own: pass 1 reads archive 0, a top-up pass the next) is read until the limit."""
    if build_packs.NEEDS_ONLY:
        return []
    s, rng = session(), pass_random("oi_crowdsourced")
    wanted = oie_candidates(s, rng)
    number = (build_packs.PASS - 1) % OIE_SETS
    fetched = oie_archive_pictures(OIE_SET.format(n=number), wanted, limit)
    say(f"Open Images Extended: {len(fetched)} photos from archive {number}")
    return with_twins(fetched)


# ----------------------------------------------------------------- pubtabnet_tables (IBM PubTabNet)

PTN_REPO = "ds4sd/PubTabNet_OTSL"
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PTN_FREE = {"cc by": "CC BY", "cc0": "CC0"}       # Europe PMC licence values used (never -NC, -SA or -ND)
PTN_CREDIT = ("Table from \"{title}\" by {authors}, {journal} ({year}), {licence}, "
              "https://europepmc.org/article/PMC/{pmcid}; table text and structure from PubTabNet (Xu Zhong, Elaheh "
              "ShafieiBavani and Antonio Jimeno Yepes, IBM Research, 2020), CDLA-Permissive-1.0, "
              "https://huggingface.co/datasets/ds4sd/PubTabNet_OTSL")
PTN_MOST_ROWS, PTN_MOST_COLUMNS, PTN_MOST_WORDS = 15, 6, 220
PTN_PER_GROUP = 120                 # at most this many tables from one row group, so many articles are used
PTN_FORMAT = re.compile(r"</?(b|i|u|em|strong|sup|sub|underline|strike|overline|span|br)\s*/?>", re.I)


def ptn_cell_text(cell):
    """The words of one table cell: its characters joined, bold, italic and other marks taken out, spaces tidied."""
    text = "".join(str(t) for t in ((cell or {}).get("tokens") or []))
    text = " ".join(html.unescape(PTN_FORMAT.sub(" ", text)).split())
    return re.sub(r"\s*•\s*", ", ", text).strip(", ")         # bullet lists inside a cell, said as a list


def ptn_grid(html_tokens, cells):
    """The table as [(is a heading row, [cell words])] from PubTabNet's structure tokens ("<thead>", "<tr>", "<td>"
    or "<td" with colspan / rowspan, "</tr>" ...) and its cells (one per "<td", in order); [] when the two do not
    match. The OTSL copy nests the cells in one more list, which is undone."""
    if cells and isinstance(cells[0], list):
        cells = cells[0]
    rows, current, heading, used = [], None, False, 0
    for token in html_tokens or []:
        if token == "<thead>":
            heading = True
        elif token == "</thead>":
            heading = False
        elif token == "<tr>":
            current = []
        elif token == "</tr>":
            if current is not None:
                rows.append((heading, current))
            current = None
        elif token in ("<td>", "<td"):
            text = ptn_cell_text(cells[used]) if used < len(cells or []) else None
            used += 1
            if current is not None:
                current.append(text or "")
    if used != len(cells or []) or not rows:
        return []
    return rows


def ptn_rows(grid, columns):
    """The two rows for one table ("Read this table to me." and its size), or [] when the table is too big, too
    wordy or mostly blank."""
    if not grid or len(grid) > PTN_MOST_ROWS or columns > PTN_MOST_COLUMNS or columns < 2:
        return []
    filled = sum(1 for _, cells in grid for c in cells if c)
    total = sum(len(cells) for _, cells in grid)
    if not total or filled * 2 < total:
        return []
    lines = []
    for number, (heading, cells) in enumerate(grid, 1):
        said = "; ".join(c if c else "blank" for c in cells)
        lines.append(f"Row {number}{' (headings)' if heading else ''}: {said.rstrip('.')}.")
    size = f"This table has {len(grid)} rows and {columns} columns."
    answer = size + " " + " ".join(lines)
    if len(answer.split()) > PTN_MOST_WORDS:
        return []
    headings = sum(1 for heading, _ in grid if heading)
    told = f"It has {len(grid)} rows and {columns} columns" + (
        "; the first row holds the headings." if headings == 1 else
        f"; the first {headings} rows hold the headings." if headings > 1 else ".")
    return [{"question": READ_Q, "answer": answer}, {"question": SIZE_Q, "answer": told}]


def ptn_authors(text):
    """At most three authors from Europe PMC's author string, then "and others"."""
    names = [n.strip() for n in str(text or "").rstrip(".").split(",") if n.strip()]
    return ", ".join(names[:3]) + (" and others" if len(names) > 3 else "") if names else "its authors"


def ptn_free_articles(s, pmcids):
    """{pmcid: credit facts} of the articles under CC BY or CC0 among pmcids, asked of Europe PMC 100 at a time
    (an article whose licence Europe PMC does not give is left out)."""
    out, pmcids = {}, sorted(set(pmcids))
    for start in range(0, len(pmcids), 100):
        chunk = pmcids[start:start + 100]
        query = "(" + " OR ".join(f"PMCID:{p}" for p in chunk) + ') AND (LICENSE:"cc by" OR LICENSE:"cc0")'
        for attempt in range(3):
            try:
                data = s.get(EUROPE_PMC, timeout=180, params={"query": query, "format": "json",
                                                               "resultType": "core", "pageSize": 100}).json()
                break
            except Exception:  # noqa: BLE001 - tried again
                time.sleep(10 * (attempt + 1))
        else:
            continue
        for r in (data.get("resultList") or {}).get("result") or []:
            licence = PTN_FREE.get(str(r.get("license") or "").strip().lower())
            if licence and r.get("pmcid") in chunk:
                journal = ((r.get("journalInfo") or {}).get("journal") or {}).get("title") or r.get("journalTitle")
                out[r["pmcid"]] = {"licence": licence, "title": clean(r.get("title")).rstrip("."),
                                   "authors": ptn_authors(r.get("authorString")), "journal": clean(journal) or
                                   "PubMed Central", "year": r.get("pubYear") or "no year given"}
        time.sleep(0.4)
    return out


def ptn_pmcid(filename):
    """The PubMed Central id in a PubTabNet file name ("PMC5755158_010_01.png" -> "PMC5755158"), or ""."""
    m = re.match(r"^(PMC\d+)_", str(filename or ""))
    return m.group(1) if m else ""


def build_pubtabnet_tables(limit):
    """The PubTabNet tables pack: row groups of IBM's parquet copy are read in a shuffled order (first without the
    pictures, to choose tables, then the chosen tables' pictures), each article's licence is checked with Europe
    PMC, and the tables of CC BY and CC0 articles are read out."""
    if build_packs.NEEDS_ONLY:
        return []
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    fs, rng, s = HfFileSystem(), pass_random("pubtabnet_tables"), session()
    paths = sorted(p for p in HfApi().list_repo_files(PTN_REPO, repo_type="dataset") if p.endswith(".parquet"))
    groups = []
    for path in paths:
        f = pq.ParquetFile(fs.open(f"datasets/{PTN_REPO}/{path}"))
        groups += [(path, g) for g in range(f.metadata.num_row_groups)]
    rng.shuffle(groups)
    out, seen_articles = [], collections.Counter()
    for path, group in groups:
        if len(out) >= limit or listing_out_of_time():
            break
        f = pq.ParquetFile(fs.open(f"datasets/{PTN_REPO}/{path}"))
        table = f.read_row_group(group, columns=["filename", "html", "cells", "cols"]).to_pylist()
        chosen = {}
        for index, record in enumerate(table):
            name = f"ptn-{str(record.get('filename') or '').rsplit('.', 1)[0]}.jpg"
            pmcid = ptn_pmcid(record.get("filename"))
            if not pmcid or already_in_pack(name):
                continue
            rows = ptn_rows(ptn_grid(record.get("html"), record.get("cells")), int(record.get("cols") or 0))
            if not rows:
                considered(name, "", "the table is too big, too wordy, mostly blank, or could not be read")
                continue
            chosen[index] = (name, pmcid, rows)
        free = ptn_free_articles(s, [pmcid for _, pmcid, _ in chosen.values()])
        keep = [i for i, (name, pmcid, _) in chosen.items() if pmcid in free]
        for i, (name, pmcid, _) in chosen.items():
            if pmcid not in free:
                considered(name, "", "its article is not under CC BY or CC0 (Europe PMC)")
        rng.shuffle(keep)
        keep = [i for i in keep if seen_articles[chosen[i][1]] < 3][:PTN_PER_GROUP]
        if not keep:
            continue
        pictures = f.read_row_group(group, columns=["image"]).column("image").to_pylist()
        for i in keep:
            name, pmcid, rows = chosen[i]
            data = smaller(((pictures[i] or {}).get("bytes")) or b"")
            if not data or seen_articles[pmcid] >= 3:
                continue
            credit = PTN_CREDIT.format(pmcid=pmcid, **free[pmcid])
            source = f"https://huggingface.co/datasets/{PTN_REPO}#{name}"
            considered(name, source, "")
            note_source(name, source)
            out.append((name, data, [dict(r, credit=credit) for r in rows]))
            seen_articles[pmcid] += 1
            if len(out) >= limit:
                break
        say(f"  PubTabNet: {len(out)} tables so far ({path}, row group {group})")
    say(f"PubTabNet: {len(out)} tables from {len(seen_articles)} articles")
    return with_twins(out[:limit])


# ----------------------------------------------------------------- the packs

BIGTECH_PACKS = {
    "gso_objects": (build_gso_objects,
                    "Google Scanned Objects (Laura Downs, Anthony Francis, Nate Koenig, Brandon Kinman, Ryan Hickman, "
                    "Krista Reymann, Thomas B. McHugh and Vincent Vanhoucke, Google Research, 2022), each model CC BY "
                    "4.0, https://app.gazebosim.org/GoogleResearch/fuel/models; the pictures are Gazebo Fuel's "
                    "rendered views of the scans."),
    "oi_crowdsourced": (build_oi_crowdsourced,
                        "Open Images Extended, Crowdsourced (Google): photos given through the Google Crowdsource app, "
                        "each under its own licence (CC BY 4.0) with the giver's name below; labels checked by people "
                        "at Google, CC BY 4.0. https://storage.googleapis.com/openimages/web/extended.html"),
    "pubtabnet_tables": (build_pubtabnet_tables,
                         "PubTabNet (Xu Zhong, Elaheh ShafieiBavani and Antonio Jimeno Yepes, IBM Research, 2020), "
                         "annotations CDLA-Permissive-1.0, from IBM's copy https://huggingface.co/datasets/ds4sd/"
                         "PubTabNet_OTSL; each table is from a PubMed Central Open Access article under CC BY or CC0 "
                         "(checked with Europe PMC), credited below."),
}

# How many pictures a full build takes from each (each finishes well within the time limit on GitHub's machines).
BIGTECH_LIMITS = {
    "gso_objects": 2000,        # about 1,030 models, two views of each
    "oi_crowdsourced": 4000,    # one 6.5 GB archive holds about 38,000 photos; about 1.5 GB of large JPEGs
    "pubtabnet_tables": 3000,   # about 570,000 tables; at most three per article
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one big-company open pack builder.")
    parser.add_argument("key", choices=sorted(BIGTECH_PACKS))
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args(argv)
    entries = BIGTECH_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
