"""Pack builders for READING the world: text in photos, receipts, document pages, charts and handwritten letters.
Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}. A picture that has more
than one question comes once with its JPEG and then again as (None, None, row) rows whose "file" names the same
picture (as food_packs.with_twins does), so the zip holds each picture only once; the limit counts pictures. COCO
photos are never copied: those rows carry the photo's address ("url") and the kit fetches it.

Pictures keep up to 2,048 pixels on the long side (build_packs.smaller), so small print stays readable. Every answer
is a person's transcription or label (or a sentence made from them by a fixed template), never machine-written text:

  textocr       TextOCR (Singh et al., 2021, Facebook AI; annotations CC BY 4.0, textvqa.org/textocr) on Open Images
                photos whose own licence is CC BY (photographer credited): every word in the picture typed by
                people, read out line by line. "Read all the text in this picture." Only photos where every word was
                legible (TextOCR marks unreadable words with "."), with 2 to 60 words, none written sideways.
  coco_text     COCO-Text v2 (Veit et al., 2016; annotations CC BY 4.0, bgshih.github.io/cocotext) on COCO photos
                under CC BY 2.0 or no known copyright (the kit fetches them): the same question, only photos where
                every marked piece of text is legible and big enough to read.
  cord          CORD v2 (Park et al., 2019, NAVER CLOVA; CC BY 4.0, github.com/clovaai/cord): photos of 1,000
                Indonesian shop and restaurant receipts with every field labelled by people. "What is the total on
                this receipt?", "List the items and prices on this receipt." and "How much change was given?"
  doclaynet     DocLayNet v1.2 (IBM Research, 2022; CDLA-Permissive-1.0): 80,000 pages of annual reports,
                manuals, scientific articles, laws, tenders and patents, whose parts (title, headings, text,
                pictures, tables) were marked by trained people; the words come from the page's own PDF.
                "What kind of document is this page from?", "What is the title on this page?" and, for pages in
                one column, "Read this page."
  plotqa        PlotQA (Methani et al., 2020; CC BY 4.0, github.com/NiteshMethani/PlotQA): bar charts and line
                graphs drawn by code from real World Bank and other public data, with the data behind each chart.
                "What does this chart show?" and "Read the values in this chart." (template sentences).
  loc_letters   Library of Congress "By the People" (crowd.loc.gov): pages of letters, diaries, papers and books,
                mostly handwritten, typed out by volunteers (transcriptions CC0); only campaigns whose
                transcriptions are public domain and whose collection the Library says has no known copyright
                restrictions. "Read this page."

    python packs/text_packs.py cord --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import os
import random
import re
import sys
import tempfile
import time
import zipfile

from build_packs import session, clean, smaller, fetch_all, say, coco_licences  # noqa: F401

READ_ALL = "Read all the text in this picture."
READ_PAGE = "Read this page."
COCO_PHOTO = "photo from COCO (cocodataset.org), CC BY 2.0 or no known copyright restrictions"


# ----------------------------------------------------------------- shared helpers

def with_twins(fetched):
    """Fetched pictures whose row is a list of rows, as pack entries: the first row with the picture, the others as
    (None, None, row) pointing at the same picture."""
    out = []
    for name, data, rows in fetched:
        out.append((name, data, rows[0]))
        out += [(None, None, dict(r, file=f"pictures/{name}")) for r in rows[1:]]
    return out


def word_count(text):
    """How many words a text has."""
    return len(str(text).split())


def text_lines(words):
    """The words of a picture in reading order, as lines of text: words are (text, x, y, width, height) boxes. Words
    whose middles are at about the same height make a line (read left to right); a wide gap inside a line starts a
    new line (two signs side by side); lines are read from top to bottom. None when a word is written sideways
    (taller than wide), as its place in the reading order cannot be told."""
    for text, x, y, w, h in words:
        if len(text) >= 3 and h > 1.5 * w:
            return None
    lines = []                                          # each: [middle height, word height, [(x, w, text)]]
    for text, x, y, w, h in sorted(words, key=lambda b: b[2] + b[4] / 2):
        middle = y + h / 2
        for line in lines:
            if abs(line[0] - middle) <= 0.5 * min(line[1], h):
                line[2].append((x, w, text))
                break
        else:
            lines.append([middle, h, [(x, w, text)]])
    out = []
    for middle, height, parts in lines:
        parts.sort()
        current, right = [], None
        for x, w, text in parts:
            if right is not None and x - right > 3 * height:
                out.append((middle, " ".join(current)))
                current = []
            current.append(text)
            right = x + w
        out.append((middle, " ".join(current)))
    return [text for _, text in sorted(out, key=lambda m: m[0])]


def plain_number(value):
    """A number as people say it: 234280000 -> "234 million", 45.2999992 -> "45.3", 1234.5 -> "1,235"."""
    v = float(value)
    a = abs(v)
    if a >= 1e12:
        return f"{v / 1e12:,.3g} trillion" if a < 1e15 else f"{v / 1e12:,.0f} trillion"
    if a >= 1e9:
        return f"{v / 1e9:.3g} billion"
    if a >= 1e6:
        return f"{v / 1e6:.3g} million"
    if a >= 1000:
        return f"{v:,.0f}"
    if a >= 1 or a == 0:
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return f"{v:.3g}"


def listed(words):
    """Words joined in plain English: "a", "a and b", "a, b and c"."""
    words = list(words)
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]


# ----------------------------------------------------------------- TextOCR (text in Open Images photos)

TEXTOCR = "https://dl.fbaipublicfiles.com/textvqa/data/textocr/TextOCR_0.1_{}.json"     # val (40 MB), train (280 MB)
OI_ALL_IMAGES = "https://storage.googleapis.com/openimages/2018_04/image_ids_and_rotation.csv"   # 3.3 GB, any order
OI_TRAIN_PICTURE = "https://open-images-dataset.s3.amazonaws.com/train/{}.jpg"
OI_FREE = re.compile(r"creativecommons\.org/(licenses/by/(\d\.\d)/?$|publicdomain/(zero|mark)/)")


def oi_licence_name(url):
    """ "CC BY 2.0" (and so on) for a Creative Commons address, "" for any other licence."""
    m = OI_FREE.search(url or "")
    if not m:
        return ""
    if m.group(2):
        return f"CC BY {m.group(2)}"
    return "CC0" if m.group(3) == "zero" else "Public Domain Mark"


def textocr_answers(data):
    """{Open Images id: the picture's text, line by line} for the TextOCR pictures where every word was legible,
    with 2 to 60 words, none written sideways."""
    out = {}
    for image_id, ann_ids in data["imgToAnns"].items():
        words = []
        for ann_id in ann_ids:
            a = data["anns"][ann_id]
            text = clean(a.get("utf8_string"))
            if not text or text == ".":                 # "." marks a word people could not read
                words = None
                break
            x, y, w, h = a["bbox"]
            words.append((text, x, y, w, h))
        if not words or not 2 <= len(words) <= 60:
            continue
        lines = text_lines(words)
        if lines:
            out[image_id] = "\n".join(lines)
    return out


def build_textocr(limit):
    """The TextOCR pack's pictures: [(name, JPEG, row)]. Reads the validation annotations (40 MB) and, when more
    pictures are wanted, the training ones (280 MB); then reads Open Images' list of photos (3.3 GB, in no order) as
    it downloads, stopping once enough photos with a free licence that need no turning are found."""
    s = session()
    answers = {}
    for part in ("val", "train"):
        if len(answers) >= limit * 3:
            break
        data = s.get(TEXTOCR.format(part), timeout=900).json()
        found = textocr_answers(data)
        say(f"TextOCR {part}: {len(found)} of {len(data['imgs'])} pictures have all their text legible")
        answers.update(found)
        del data
    wanted, items = int(limit * 1.2) + 2, []
    with s.get(OI_ALL_IMAGES, timeout=900, stream=True) as r:
        r.raise_for_status()
        for photo in csv.DictReader(line for line in r.iter_lines(decode_unicode=True) if line):
            image_id = photo.get("ImageID")
            if image_id not in answers or (photo.get("Rotation") or "0") not in ("0", "0.0", ""):
                continue
            licence = oi_licence_name(photo.get("License"))
            if not licence:
                continue
            author = clean(photo.get("Author")) or "an unnamed photographer"
            page = photo.get("OriginalLandingURL") or ""
            credit = (f"Photo by {author}" + (f" ({page})" if page else "") + f", {licence}, from Open Images; "
                      f"text typed by people for TextOCR (Singh et al., 2021), CC BY 4.0")
            items.append((f"textocr-{image_id}.jpg", OI_TRAIN_PICTURE.format(image_id),
                          {"question": READ_ALL, "answer": answers[image_id], "credit": credit}))
            if len(items) >= wanted:
                break
    say(f"TextOCR: {len(items)} photos with a free licence chosen")
    return fetch_all(items, workers=8)[:limit]


# ----------------------------------------------------------------- COCO-Text (text in COCO photos)

COCO_TEXT = "https://github.com/bgshih/cocotext/releases/download/dl/cocotext.v2.zip"      # 12 MB


def build_coco_text(limit):
    """The COCO-Text pack's rows (no pictures: the kit fetches them from COCO): [(None, None, row)]. Only photos
    where every marked piece of text is legible, typed in, and at least 10 pixels tall (COCO's photos are 640
    pixels wide, so smaller text cannot be read), with 1 to 40 words."""
    free = coco_licences()
    say(f"COCO: {len(free)} photos under CC BY 2.0 or no known copyright")
    with zipfile.ZipFile(io.BytesIO(session().get(COCO_TEXT, timeout=300).content)) as z:
        data = json.loads(z.read("cocotext.v2.json"))
    rows = []
    for image_id, ann_ids in sorted(data["imgToAnns"].items(), key=lambda kv: int(kv[0])):
        if not ann_ids or int(image_id) not in free:
            continue
        words = []
        for ann_id in ann_ids:
            a = data["anns"][str(ann_id)]
            text = clean(a.get("utf8_string"))
            x, y, w, h = a["bbox"]
            if a.get("legibility") != "legible" or not text or min(w, h) < 10:
                words = None
                break
            words.append((text, x, y, w, h))
        if not words or len(words) > 40 or (len(words) == 1 and len(words[0][0]) < 3):
            continue
        lines = text_lines(words)
        if lines:
            rows.append({"url": free[int(image_id)], "question": READ_ALL, "answer": "\n".join(lines),
                         "credit": f"Text typed by people for COCO-Text (Veit et al., 2016), CC BY 4.0; {COCO_PHOTO}"})
    say(f"COCO-Text: {len(rows)} free photos with all their text legible")
    random.Random(61).shuffle(rows)
    return [(None, None, r) for r in rows[:limit]]


# ----------------------------------------------------------------- CORD (receipts)

CORD = "naver-clova-ix/cord-v2"


def cord_value(value):
    """A field of a CORD receipt as text (a field read twice is a list: the first is kept)."""
    if isinstance(value, list):
        value = value[0] if value else ""
    return clean(value)


def cord_items(menu):
    """The lines "2 x Ice tea: 24,000" of a receipt's items (with their extras, "with Coconut jelly: 4,000")."""
    lines = []
    for item in (menu if isinstance(menu, list) else [menu]):
        if not isinstance(item, dict):
            continue
        name, count, price = cord_value(item.get("nm")), cord_value(item.get("cnt")), cord_value(item.get("price"))
        if not name:
            continue
        count = re.sub(r"\s*[xX]$", "", count)
        line = (f"{count} x {name}" if count and count not in ("1",) else name) + (f": {price}" if price else "")
        lines.append(line)
        subs = item.get("sub") or []
        for sub in (subs if isinstance(subs, list) else [subs]):
            if isinstance(sub, dict) and cord_value(sub.get("nm")):
                sub_price = cord_value(sub.get("price"))
                lines.append(f"  with {cord_value(sub.get('nm'))}" + (f": {sub_price}" if sub_price else ""))
    return lines


def cord_rows(parse, credit):
    """The questions and answers for one CORD receipt (its people-labelled fields, gt_parse)."""
    rows = []
    total = parse.get("total") or {}
    total = total[0] if isinstance(total, list) and total else total
    total_price = cord_value(total.get("total_price")) if isinstance(total, dict) else ""
    if total_price:
        rows.append({"question": "What is the total on this receipt?", "answer": f"The total is {total_price}."})
    items = cord_items(parse.get("menu") or [])
    if items and len(items) <= 25:
        rows.append({"question": "List the items and prices on this receipt.", "answer": "\n".join(items)})
    change = cord_value(total.get("changeprice")) if isinstance(total, dict) else ""
    cash = cord_value(total.get("cashprice")) if isinstance(total, dict) else ""
    if change and cash:
        rows.append({"question": "How much change was given?",
                     "answer": f"The change was {change}, from {cash} paid in cash."})
    return [dict(r, credit=credit) for r in rows]


def build_cord(limit):
    """The CORD pack's pictures: [(name, JPEG, row)], each receipt once with its other questions pointing at it.
    Reads the dataset's parquet files (2.3 GB in all) one at a time, the test part first."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    files = sorted((f for f in HfApi().list_repo_files(CORD, repo_type="dataset") if f.endswith(".parquet")),
                   key=lambda f: (not f.startswith("data/test"), f))
    fs, fetched = HfFileSystem(), []
    for name in files:
        with fs.open(f"datasets/{CORD}/{name}", "rb", block_size=1 << 22) as f:
            table = pq.ParquetFile(f).read().to_pylist()
        for record in table:
            truth = json.loads(record["ground_truth"])
            meta = truth.get("meta") or {}
            split, number = meta.get("split", "cord"), meta.get("image_id", len(fetched))
            credit = (f"CORD v2 receipt {split} {number} (Park et al., 2019, NAVER CLOVA), CC BY 4.0, "
                      f"https://github.com/clovaai/cord")
            rows = cord_rows(truth.get("gt_parse") or {}, credit)
            data = smaller((record.get("image") or {}).get("bytes") or b"") if rows else None
            if data:
                fetched.append((f"cord-{split}-{number}.jpg", data, rows))
            if len(fetched) >= limit:
                break
        say(f"CORD {name}: {len(fetched)} receipts so far")
        if len(fetched) >= limit:
            break
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- DocLayNet (document pages)

DOCLAYNET = "docling-project/DocLayNet-v1.2"
DLN_CAPTION, DLN_FOOTNOTE, DLN_FORMULA, DLN_LIST, DLN_FOOTER, DLN_HEADER = 1, 2, 3, 4, 5, 6
DLN_PICTURE, DLN_SECTION, DLN_TABLE, DLN_TEXT, DLN_TITLE = 7, 8, 9, 10, 11
DLN_KINDS = {"financial_reports": "a company's financial report", "scientific_articles": "a scientific article",
             "laws_and_regulations": "a law or regulation", "government_tenders": "a government call for tenders",
             "manuals": "a manual", "patents": "a patent"}
DLN_ASK_KIND = "What kind of document is this page from?"
DLN_ASK_TITLE = "What is the title on this page?"


def dln_box_text(cells):
    """The words of one marked part of a page: its PDF text cells joined (a word broken by a hyphen at the end of
    a line is joined again)."""
    text = " ".join(clean(c.get("text")) for c in cells or [] if clean(c.get("text")))
    text = re.sub(r"GLYPH(<[^>]*>)?\s*", "", text).strip()          # bullets and symbols the PDF had no letter for
    return re.sub(r"(\w)- (?=[a-z])", r"\1", text)


def dln_one_column(boxes):
    """True when no two parts of the page sit side by side (so reading top to bottom is the reading order)."""
    for i, (_, a) in enumerate(boxes):
        for _, b in boxes[i + 1:]:
            ax, ay, aw, ah = a
            bx, by, bw, bh = b
            overlap = min(ay + ah, by + bh) - max(ay, by)
            if overlap > 0.3 * min(ah, bh) and (ax + aw <= bx or bx + bw <= ax):
                return False
    return True


def dln_rows(record):
    """The questions and answers for one DocLayNet page."""
    meta = record.get("metadata") or {}
    rows = []
    kind = DLN_KINDS.get(meta.get("doc_category"))
    if kind:
        rows.append({"question": DLN_ASK_KIND, "answer": f"This page is from {kind}."})
    parts = list(zip(record.get("category_id") or [], record.get("bboxes") or [], record.get("pdf_cells") or []))
    titles = [dln_box_text(c) for k, _, c in parts if k == DLN_TITLE and dln_box_text(c)]
    if titles and word_count(titles[0]) <= 25:
        rows.append({"question": DLN_ASK_TITLE, "answer": titles[0]})
    if any(k == DLN_FORMULA for k, _, _ in parts) or not parts:
        return rows
    body = [(k, box) for k, box, _ in parts if k not in (DLN_HEADER, DLN_FOOTER)]
    if not dln_one_column(body):
        return rows
    lines = []
    for k, box, cells in sorted(parts, key=lambda p: (p[1][1], p[1][0])):
        if k == DLN_PICTURE:
            lines.append("[Picture]")
        elif k == DLN_TABLE:
            lines.append("[Table]")
        else:
            text = dln_box_text(cells)
            if not text:
                return rows                              # a part whose words are not in the PDF (a scan)
            lines.append(text)
    words = word_count(" ".join(lines))
    if 15 <= words <= 250:
        rows.append({"question": READ_PAGE, "answer": "\n".join(lines)})
    return rows


def build_doclaynet(limit):
    """The DocLayNet pack's pictures: [(name, JPEG, row)], each page once with its other questions pointing at it.
    The dataset is 40 GB in 87 parquet files, so it reads chosen row groups (about 60 MB each, without the PDF
    column) from files picked at random until there are enough pages."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    files = [f for f in HfApi().list_repo_files(DOCLAYNET, repo_type="dataset") if f.endswith(".parquet")]
    random.Random(71).shuffle(files)
    fs, fetched, seen = HfFileSystem(), [], set()
    columns = ["image", "bboxes", "category_id", "pdf_cells", "metadata"]
    per_group = max(4, limit // 40)                    # pages taken from one row group, so many files are used
    for name in files:
        with fs.open(f"datasets/{DOCLAYNET}/{name}", "rb", block_size=1 << 22) as f:
            parquet = pq.ParquetFile(f)
            groups = list(range(parquet.metadata.num_row_groups))
            random.Random(name).shuffle(groups)
            for group in groups[:2]:
                taken = 0
                for record in parquet.read_row_group(group, columns=columns).to_pylist():
                    meta = record.get("metadata") or {}
                    if meta.get("page_hash") in seen:
                        continue
                    rows = dln_rows(record)
                    if len(rows) < 2:                    # only "what kind of document": too little to learn
                        continue
                    data = smaller((record.get("image") or {}).get("bytes") or b"")
                    if not data:
                        continue
                    seen.add(meta.get("page_hash"))
                    credit = (f"DocLayNet v1.2 (Pfitzmann et al., 2022, IBM Research), CDLA-Permissive-1.0: "
                              f"{meta.get('original_filename')}, page {meta.get('page_no')}")
                    fetched.append((f"doclaynet-{meta.get('page_hash', '')[:16]}.jpg", data,
                                    [dict(r, credit=credit) for r in rows]))
                    taken += 1
                    if taken >= per_group or len(fetched) >= limit:
                        break
                if len(fetched) >= limit:
                    break
        say(f"DocLayNet {name}: {len(fetched)} pages so far")
        if len(fetched) >= limit:
            break
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- PlotQA (charts of real data)

PLOTQA = "Dodon/PlotQA_dataset"             # the authors' files in one zip (6.8 GB); read in place, part by part
PLOTQA_ZIP = "PlotQA.zip"
PLOTQA_PARTS = ("validation", "test")        # 33,650 + 33,657 charts (the training part's 1.2 GB list is not read)
PLOTQA_KINDS = {"vbar_categorical": "bar chart", "hbar_categorical": "horizontal bar chart",
                "line": "line graph", "dot_line": "dot-and-line chart"}
PLOT_ASK_ABOUT = "What does this chart show?"
PLOT_ASK_VALUES = "Read the values in this chart."


def plot_rows(chart):
    """The questions and answers for one PlotQA chart, made from the data it was drawn from."""
    info = chart["general_figure_info"]
    kind = PLOTQA_KINDS.get(chart.get("type"))
    title = clean((info.get("title") or {}).get("text"))
    x_label = clean((info.get("x_axis", {}).get("label") or {}).get("text"))
    y_label = clean((info.get("y_axis", {}).get("label") or {}).get("text"))
    models = chart.get("models") or []
    if not kind or not title or not models:
        return []
    across = chart["type"] == "hbar_categorical"            # categories up the side, values along the bottom
    category_label, value_label = (y_label, x_label) if across else (x_label, y_label)
    tick_names = [clean(v) for v in info.get("x_axis", {}).get("major_labels", {}).get("values", [])]
    series = []
    for m in models:
        categories, values = (m["y"], m["x"]) if across else (m["x"], m["y"])
        names = [clean(c) if isinstance(c, str) else (tick_names[int(c)] if int(c) < len(tick_names) else "")
                 for c in categories]
        if not all(names) or len(names) != len(values):
            return []
        series.append((clean(m.get("label") or m.get("name")), list(zip(names, values))))
    first, last = series[0][1][0][0], series[0][1][-1][0]
    category_side, value_side = ("side", "bottom") if across else ("bottom", "side")
    about = (f'A {kind} titled "{title}". Along the {category_side} it shows {category_label or "categories"}, '
             f"from {first} to {last}; along the {value_side}, {value_label or 'the values'}.")
    named = [name for name, _ in series if name]
    if len(series) > 1 and named:
        about += f" It compares {listed(named)}."
    rows = [{"question": PLOT_ASK_ABOUT, "answer": about}]
    if sum(len(points) for _, points in series) <= 30:
        lines = []
        for name, points in series:
            values = ", ".join(f"{category} {plain_number(value)}" for category, value in points)
            lines.append(f"{name}: {values}." if name and len(series) > 1 else f"{values}.")
        unit = f" ({value_label})" if value_label else ""
        rows.append({"question": PLOT_ASK_VALUES, "answer": f"The values{unit} are about:\n" + "\n".join(lines)})
    return rows


def build_plotqa(limit):
    """The PlotQA pack's pictures: [(name, JPEG, row)], each chart once with its second question pointing at it.
    Reads each part's chart list (250 MB, read in place from the zip on Hugging Face), then streams the part's
    pictures (a 880 MB tar.gz, in no particular order) and keeps charts until there are enough."""
    import tarfile
    from huggingface_hub import HfFileSystem
    fs, fetched = HfFileSystem(), []
    per_part = limit // len(PLOTQA_PARTS) + 1
    with fs.open(f"datasets/{PLOTQA}/{PLOTQA_ZIP}", "rb", block_size=1 << 23) as f:
        archive = zipfile.ZipFile(f)
        for part in PLOTQA_PARTS:
            charts = {c["image_index"]: c for c in json.loads(archive.read(f"PlotQA/{part}/annotations.json"))}
            say(f"PlotQA {part}: {len(charts)} charts")
            taken = 0
            with archive.open(f"PlotQA/{part}/png.tar.gz") as member, tarfile.open(fileobj=member, mode="r|gz") as tar:
                for entry in tar:
                    match = re.search(r"(\d+)\.png$", entry.name)
                    chart = charts.get(int(match.group(1))) if match else None
                    rows = plot_rows(chart) if chart else []
                    if not rows:
                        continue
                    data = smaller(tar.extractfile(entry).read())
                    if not data:
                        continue
                    credit = (f"PlotQA (Methani et al., 2020), CC BY 4.0, https://github.com/NiteshMethani/PlotQA: "
                              f"{part} chart {match.group(1)}, drawn from public data (World Bank and others)")
                    fetched.append((f"plotqa-{part}-{match.group(1)}.jpg", data, [dict(r, credit=credit) for r in rows]))
                    taken += 1
                    if taken >= per_part or len(fetched) >= limit:
                        break
            del charts
            if len(fetched) >= limit:
                break
    random.Random(81).shuffle(fetched)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Library of Congress, By the People (letters)

BTP_ITEM = "https://www.loc.gov/item/2026395156/"          # the comprehensive transcription data package
BTP_ZIP = "https://tile.loc.gov/storage-services/master/gdc/gdcdatasets/2026395156/2026395156_parquet.zip"  # 190 MB
BTP_TEXT_FREE = re.compile(r"dataset is in the Public Domain", re.I)
# The rights statement of a collection whose pictures may be shared: the Library knows of no copyright in it.
BTP_PICTURE_FREE = re.compile(r"no known (copyright )?restrictions|not aware of any copyright|public domain|"
                              r"free to use and reuse", re.I)
BTP_NOT_FREE = re.compile(r"may be (subject to|protected by) copyright|permission|copyright (is )?(held|owned)|"
                          r"restricted|rights (are )?reserved", re.I)
# Transcriptions that do not say what is on the page.
BTP_EMPTY = re.compile(r"^\s*(nothing to transcribe|blank( page)?|\[?blank\]?|no text)\s*\.?\s*$", re.I)


def btp_pictures_free(s, resource_url, cache):
    """True when the Library of Congress says the collection of a page has no known copyright restrictions (its
    "rights" statement, read once per collection page and kept in cache)."""
    if resource_url not in cache:
        rights = ""
        for attempt in range(3):                  # the Library's server is slow and sometimes answers nothing
            try:
                item = s.get(resource_url, params={"fo": "json", "at": "item.rights"}, timeout=120).json()
                rights = clean(" ".join(item.get("item.rights") or []))
            except Exception:  # noqa: BLE001 - tried again, then unknown rights: left out
                rights = ""
            if rights:
                break
            time.sleep(5 * (attempt + 1))
        cache[resource_url] = bool(BTP_PICTURE_FREE.search(rights)) and not BTP_NOT_FREE.search(rights)
    return cache[resource_url]


def build_loc_letters(limit):
    """The By the People pack's pictures: [(name, JPEG, row)]. Downloads the Library's comprehensive data package
    (one parquet file per campaign, 190 MB), keeps the campaigns whose transcriptions are public domain and whose
    pictures the Library says are free (checked on two pages of each campaign), and takes pages with 5 to 220
    words, at most two pages of one item, spread over the campaigns."""
    import pyarrow.parquet as pq
    s = session()
    rows_by_campaign = {}
    with tempfile.TemporaryDirectory() as folder:
        archive = os.path.join(folder, "btp.zip")
        with s.get(BTP_ZIP, timeout=900, stream=True) as r, open(archive, "wb") as out:
            r.raise_for_status()
            for chunk in r.iter_content(1 << 20):
                out.write(chunk)
        with zipfile.ZipFile(archive) as z:
            names = sorted(n for n in z.namelist() if n.endswith(".parquet"))
            for name in names:
                columns = ["Campaign", "Item", "Asset", "DownloadUrl", "Transcription", "RightsAdvisory",
                           "SegmentUrl", "ResourceUrl", "AssetStatus"]
                table = pq.read_table(io.BytesIO(z.read(name)), columns=columns).to_pylist()
                if not table or not BTP_TEXT_FREE.search(table[0].get("RightsAdvisory") or ""):
                    say(f"By the People {name}: transcriptions not public domain, left out")
                    continue
                rows_by_campaign[name] = table
    cache, chosen = {}, {}
    for name, table in rows_by_campaign.items():
        samples = random.Random(name).sample(table, min(2, len(table)))
        if not all(btp_pictures_free(s, r["ResourceUrl"], cache) for r in samples):
            say(f"By the People {name}: pictures not marked free of copyright, left out")
            continue
        pages, per_item = [], {}
        for r in table:
            text = (r.get("Transcription") or "").strip()
            if r.get("AssetStatus") != "completed" or not r.get("DownloadUrl") or BTP_EMPTY.match(text):
                continue
            if not 5 <= word_count(text) <= 220:
                continue
            pages.append(r)
        random.Random(name + "pages").shuffle(pages)
        kept = []
        for r in pages:
            if per_item.get(r["Item"], 0) < 2:
                per_item[r["Item"]] = per_item.get(r["Item"], 0) + 1
                kept.append(r)
        chosen[name] = kept
        say(f"By the People {name}: {len(kept)} pages usable")
    share = max(1, int(limit * 1.2) // max(1, len(chosen)) + 1)
    items = []
    for name, pages in chosen.items():
        for r in pages[:share]:
            text = re.sub(r"[ \t]+", " ", r["Transcription"].replace("\r", "")).strip()
            text = re.sub(r"\n{3,}", "\n\n", text)
            url = re.sub(r"/full/[^/]+/", "/full/!2048,2048/", r["DownloadUrl"])
            credit = (f"Library of Congress: {clean(r['Item'])} ({r.get('SegmentUrl') or r.get('ResourceUrl')}), "
                      f"no known copyright restrictions; transcribed by volunteers of By the People "
                      f"(crowd.loc.gov), CC0")
            asset = re.sub(r"[^\w.-]+", "_", str(r["Asset"]))[:80]
            items.append((f"loc-{asset}.jpg", url,
                          {"question": READ_PAGE, "answer": text, "credit": credit}))
    random.Random(91).shuffle(items)
    say(f"By the People: {len(items)} pages chosen from {len(chosen)} campaigns")
    return fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.3)[:limit]


# ----------------------------------------------------------------- the packs

TEXT_PACKS = {
    "textocr": (build_textocr, "Text: TextOCR (Singh et al., 2021, Facebook AI Research), CC BY 4.0, "
                               "https://textvqa.org/textocr. Photos: Open Images (Google), each under the CC licence "
                               "named below with its photographer."),
    "coco_text": (build_coco_text, "Text: COCO-Text v2 (Veit et al., 2016, Cornell Tech), CC BY 4.0, "
                                   "https://bgshih.github.io/cocotext/. Photos are not in this pack: the kit fetches "
                                   "them from https://cocodataset.org (only photos under CC BY 2.0 or no known "
                                   "copyright)."),
    "cord": (build_cord, "CORD v2: Consolidated Receipt Dataset (Park et al., 2019, NAVER CLOVA), CC BY 4.0, "
                         "https://github.com/clovaai/cord (pictures and labels; copy used: "
                         "https://huggingface.co/datasets/naver-clova-ix/cord-v2)."),
    "doclaynet": (build_doclaynet, "DocLayNet v1.2 (Pfitzmann et al., 2022, IBM Research), Community Data License "
                                   "Agreement - Permissive 1.0 (https://cdla.io/permissive-1-0/), "
                                   "https://github.com/DS4SD/DocLayNet and "
                                   "https://huggingface.co/datasets/docling-project/DocLayNet-v1.2."),
    "plotqa": (build_plotqa, "PlotQA (Methani, Ganguly, Khapra and Kumar, 2020), CC BY 4.0, "
                             "https://github.com/NiteshMethani/PlotQA (copy used: "
                             "https://huggingface.co/datasets/Dodon/PlotQA_dataset). The sentences are made from "
                             "each chart's data by fixed templates."),
    "loc_letters": (build_loc_letters, "Library of Congress, By the People comprehensive transcription data package "
                                       f"({BTP_ITEM}): transcriptions by volunteers, CC0; pictures from Library of "
                                       "Congress collections with no known copyright restrictions, each page "
                                       "credited below. https://www.loc.gov/legal/"),
}

# How many pictures a full build takes from each source (about what each offers after the checks above).
TEXT_LIMITS = {
    "textocr": 12000,
    "coco_text": 6000,
    "cord": 1000,
    "doclaynet": 6000,
    "plotqa": 6000,
    "loc_letters": 8000,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one text pack builder.")
    parser.add_argument("key", choices=sorted(TEXT_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = TEXT_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
