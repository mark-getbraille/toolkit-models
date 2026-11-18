"""Picture collections published by big technology companies (Google, Meta, Microsoft, Amazon, Apple, IBM, NVIDIA,
Adobe, Salesforce, the Allen Institute for AI ...) for the Picture Model Training Kit: the ones that cannot be
ready-made packs because their PICTURES are not openly licensed, even where the company's own words about them are
(CC BY questions about phone screens whose screenshots have no licence; ODC-BY descriptions of pictures found on the
web; tables cut from companies' annual reports). The open ones (Google Scanned Objects, Open Images Extended
crowdsourced photos and IBM's PubTabNet tables from CC BY articles) are ready-made packs in packs/bigtech_packs.py;
many more big-company sets are already in the kit (see BIGTECH_ALREADY_IN_THE_KIT).

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py):
  "research"     research use, or no licence stated for the pictures: personal use only (--personal-research with
                 --accept-research-terms).

Answers are the collections' own words, written by people: a person's answer to a question about a phone screen, the
transcript of what a person said while looking at a picture, the number of things a person pointed at, the words
printed in a table. Nothing written by an AI model is used: PixMo-Cap's own captions (rewritten by a language model)
are never read, only the transcripts of what the people said.

The collections (BIGTECH_SOURCES), all "research":
  screenqa_rico       ScreenQA (Hsiao et al., Google, 2022-2024): questions people asked about Android app screens
                      and the full-sentence answers other people wrote (CC BY 4.0, github.com/google-research-datasets/
                      screen_qa), on Rico's screenshots (Deka et al., 2017; no licence or terms written for them), read
                      from Rico's archive as the rico_screens entry does. "What is the rating of 'War Robots'?" ->
                      "The rating of "War Robots" is 4.6 stars." Where most people found no answer on the screen:
                      "That is not shown on this screen." ScreenQA Short and ComplexQA are not used: their answers
                      were made by a model.
  pixmo_cap_spoken    PixMo-Cap (Deitke et al., Allen Institute for AI, 2024; ODC-BY 1.0, "intended for research and
                      educational use"): the transcripts of what people said for 60 to 90 seconds about a picture
                      (about 200 words). The pictures are web addresses the Allen Institute collected from the web
                      (Reddit, Pinterest, Flickr, shops ...), with no licence of their own, so personal use only;
                      pictures from stock-photo sites (watermarked previews) are left out. "Describe this picture in
                      detail." Rows whose words name a child are marked "child".
  pixmo_points_count  PixMo-Points (Allen Institute for AI, 2024; ODC-BY 1.0): people pointed at every one of a kind of
                      thing in a picture ("collection_method": "counting"); the number of points is the answer. "How
                      many books are there in this picture?" -> "There are 21 books." Only plain names of things (no
                      phrases such as "book on the right shelf"), at most 30 points; each picture is checked against
                      the SHA-256 PixMo gives, so a picture that changed since is left out. Web pictures, as above.
  fintabnet_tables    FinTabNet (Zheng et al., IBM Research, 2021; annotations CDLA-Permissive-1.0), from IBM's copy on
                      Hugging Face (ds4sd/FinTabNet_OTSL): tables cut from the annual reports of S&P 500 companies,
                      read out row by row as the open pubtabnet_tables pack does. The reports belong to the companies,
                      so personal use only. "Read this table to me."

Needing sign-up (BIGTECH_SIGN_UP has the links; no key or agreement is asked for here) and looked at but not included
(BIGTECH_NOT_INCLUDED has the reasons). YFCC100M (Yahoo) is handled in signup_sources.py, not here.

BIGTECH_PICTURE_MAKING_OK: fintabnet_tables only (tables, no people). ScreenQA's screens and PixMo's web pictures may
show people, so they are for describing only.

    python -c "import sources, bigtech_sources"      (from the kit folder: checks the file loads)
"""

import collections
import concurrent.futures
import hashlib
import html
import json
import os
import random
import re

import sources
from extra_sources import NUDE, RICO_URL, get_bytes, plural, save, say, stream_tar
from more_sources import sentence
from personal_sources import CHILD_WORDS
from sources import DETAILED, USER_AGENT, Source, clean

READ_Q = "Read this table to me."
SIZE_Q = "How many rows and columns does this table have?"
NOT_SHOWN = "That is not shown on this screen."


def research(summary):
    """A research-terms summary that also says it is for personal, non-commercial use."""
    return summary + " Personal, non-commercial use only."


def with_child(row, *texts):
    """The row with "child": True when any of texts names a child (picture-making then leaves it out)."""
    return dict(row, child=True) if any(CHILD_WORDS.search(t or "") for t in texts) else row


# ----------------------------------------------------------------- research: ScreenQA on Rico

SCREENQA = "https://raw.githubusercontent.com/google-research-datasets/screen_qa/main/answers_and_bboxes/"
SCREENQA_SPLITS = {"train": "", "validation": "", "test": "test"}     # ScreenQA's split -> the kit's split
SCREENQA_CREDIT = ("ScreenQA (Yu-Chung Hsiao, Fedir Zubach, Gilles Baechler and others, Google, 2024), CC BY 4.0, "
                   "https://github.com/google-research-datasets/screen_qa; screenshot from Rico (Deka et al., 2017), "
                   "http://interactionmining.org/rico")
SCREENQA_PER_SCREEN = 3


def screenqa_answer(ground_truth):
    """The answer most of the people wrote (ties: the first), as a sentence; NOT_SHOWN when most found no answer on
    the screen; "" when there is nothing usable."""
    answers = [clean(g.get("full_answer")) for g in ground_truth or [] if clean(g.get("full_answer"))]
    if not answers:
        return ""
    none = sum(1 for a in answers if a.lower() == "<no answer>")
    if none * 2 > len(answers):
        return NOT_SHOWN
    real = [a for a in answers if a.lower() != "<no answer>"]
    if not real:
        return ""
    counts = collections.Counter(real)
    best = max(real, key=lambda a: (counts[a], -real.index(a)))
    return sentence(best)


def screenqa_rows():
    """{Rico screen id: [rows]}: ScreenQA's questions and answers, at most SCREENQA_PER_SCREEN for each screen."""
    per_screen = collections.defaultdict(list)
    for split, kit_split in SCREENQA_SPLITS.items():
        for record in json.loads(get_bytes(SCREENQA + f"{split}.json").decode("utf-8")):
            question, answer = clean(record.get("question")), screenqa_answer(record.get("ground_truth"))
            screen = str(record.get("image_id") or "")
            if not screen or not question or not answer or len(per_screen[screen]) >= SCREENQA_PER_SCREEN:
                continue
            per_screen[screen].append({"question": sources.as_question(question), "answer": answer,
                                       "split": kit_split, "credit": SCREENQA_CREDIT})
    return per_screen


def prepare_screenqa_rico(source, data_dir, work, cap):
    """ScreenQA on Rico: the questions and answers are read (30 MB), then Rico's 6.4 GB archive is read from the web
    only until enough screens with questions are taken (as rico_screens does). The cap counts questions."""
    per_screen = screenqa_rows()
    say(f"  ScreenQA: questions about {len(per_screen)} screens.")
    want, rows = cap + source.test, []
    folder = os.path.join(data_dir, source.key)

    def take(member, tar):
        """Keep a screen that has questions; True when there are enough."""
        stem, ext = os.path.splitext(os.path.basename(member.name))
        if ext == ".jpg" and stem in per_screen:
            path = save(f"screenqa-{stem}", tar.extractfile(member).read(), folder)
            if path:
                rows.extend(dict(r, picture=path) for r in per_screen.pop(stem))
        return len(rows) >= want

    stream_tar(RICO_URL, take, "the Rico phone screens (6.4 GB at most)")
    return rows


# ----------------------------------------------------------------- research: PixMo (Allen Institute for AI)

PIXMO_CAP = "allenai/pixmo-cap"
PIXMO_POINTS = "allenai/pixmo-points"
PIXMO_TERMS = "https://allenai.org/responsible-use"
PIXMO_CAP_CREDIT = ("PixMo-Cap (Matt Deitke, Christopher Clark and others, Allen Institute for AI, 2024), ODC-BY 1.0, "
                    "https://huggingface.co/datasets/allenai/pixmo-cap: the transcript of a person's spoken "
                    "description; picture from {url} (its rights belong to its owner)")
PIXMO_POINTS_CREDIT = ("PixMo-Points (Allen Institute for AI, 2024), ODC-BY 1.0, https://huggingface.co/datasets/"
                       "allenai/pixmo-points: things a person pointed at, counted; picture from {url} (its rights "
                       "belong to its owner)")
# Stock-photo sites: their pictures on the web are watermarked previews sold under licence, so they are left out.
STOCK_SITES = re.compile(r"(shutterstock|dreamstime|alamy|gettyimages|istockphoto|depositphotos|123rf|stock\.adobe|"
                         r"ftcdn\.net|freepik|vectorstock|canstockphoto|bigstockphoto|pond5|agefotostock|"
                         r"stockfresh|photodune|envato|pixta)\.", re.I)
SEXUAL = re.compile(r"\b(sex\w*|porn\w*|erotic\w*|genital\w*|penis|vagina|breasts?|nipples?|bikini|lingerie|"
                    r"underwear|naked|nude|nudity|topless)\b", re.I)
FILLERS = re.compile(r"\b(um+|uh+|erm|hmm+|uh-huh)\b[,.]?\s*", re.I)
REPEATED = re.compile(r"\b(\w+(?:'\w+)?)(\s+\1\b)+", re.I)          # "There's There's" -> "There's"
SPOKEN_START = re.compile(r"^(so|okay|ok|alright|all right|well|right)[,.]?\s+", re.I)
PIXMO_MOST_WORDS = 260


def spoken_text(text):
    """A transcript tidied for an answer: "um" and "uh" taken out, a word said twice in a row said once, a leading
    "So," or "Okay," dropped, spaces tidied, at most about PIXMO_MOST_WORDS words (whole sentences), ending with a
    full stop. "" when it is shorter than 40 words or names anything sexual."""
    text = clean(text)
    if not text or SEXUAL.search(text) or NUDE.search(text):
        return ""
    text = FILLERS.sub("", text)
    text = REPEATED.sub(r"\1", text)
    text = SPOKEN_START.sub("", " ".join(text.split()))
    out = ""
    for part in re.split(r"(?<=[.!?])\s+", text):
        if out and len((out + " " + part).split()) > PIXMO_MOST_WORDS:
            break
        out = (out + " " + part).strip()
    if len(out.split()) > PIXMO_MOST_WORDS:                         # one endless sentence: cut at a comma or a word
        out = " ".join(out.split()[:PIXMO_MOST_WORDS]).rsplit(",", 1)[0]
    if len(out.split()) < 40:
        return ""
    out = out[0].upper() + out[1:]
    return out if out.endswith((".", "!", "?")) else out.rstrip(",;:") + "."


def best_transcript(transcripts):
    """The transcript to use of the one to three people's: the longest that tidies to an answer, or ""."""
    said = [spoken_text(t) for t in (transcripts or [])]
    said = [s for s in said if s]
    return max(said, key=lambda s: len(s.split())) if said else ""


def pixmo_url_ok(url):
    """True for a picture address the kit may fetch: https or http, and not a stock-photo site."""
    return bool(re.match(r"^https?://", str(url or ""))) and not STOCK_SITES.search(str(url))


def pixmo_name(prefix, url):
    """A file name for a web picture: the prefix and the first 16 letters of its address's SHA-256."""
    return f"{prefix}-{hashlib.sha256(str(url).encode('utf-8')).hexdigest()[:16]}"


def parquet_groups(repo, seed):
    """[(parquet file, row group)] of a Hugging Face dataset, shuffled with seed, and the file system to read them."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    fs = HfFileSystem()
    files = sorted(p for p in HfApi().list_repo_files(repo, repo_type="dataset") if p.endswith(".parquet"))
    groups = []
    for path in files:
        groups += [(path, g) for g in range(pq.ParquetFile(fs.open(f"datasets/{repo}/{path}")).metadata.num_row_groups)]
    random.Random(seed).shuffle(groups)
    return fs, groups


def fetch_checked(items, folder, workers=8):
    """Download web pictures: items are (file name, address, SHA-256 or "", rows); the rows whose picture came (and,
    when a SHA-256 is given, is still the same picture), with "picture" set."""
    import requests
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    os.makedirs(folder, exist_ok=True)

    def one(item):
        """One picture's rows, or []."""
        name, url, digest, rows = item
        path = os.path.join(folder, name + ".jpg")
        if not sources.have(path):
            try:
                r = session.get(url, timeout=30)
                if r.status_code != 200 or (digest and hashlib.sha256(r.content).hexdigest() != digest):
                    return []
                if not sources.smaller(r.content, path):
                    return []
            except Exception:  # noqa: BLE001 - a picture that cannot be fetched is left out
                return []
        return [dict(row, picture=path) for row in rows]

    out = []
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for done, result in enumerate(pool.map(one, items), 1):
            out += result
            if done % 500 == 0:
                say(f"    {done} of {len(items)} pictures fetched ({len(out)} rows usable)")
    return out


def prepare_pixmo_cap_spoken(source, data_dir, work, cap):
    """PixMo-Cap transcripts: row groups of the parquet files are read in a shuffled order (address and transcripts
    only), the pictures fetched from the web; about 1.3 rows are tried for each one wanted (some pictures are gone)."""
    fs, groups = parquet_groups(PIXMO_CAP, 801)
    import pyarrow.parquet as pq
    want, items, seen = int((cap + source.test) * 1.3) + 10, [], set()
    for path, group in groups:
        if len(items) >= want:
            break
        table = pq.ParquetFile(fs.open(f"datasets/{PIXMO_CAP}/{path}")).read_row_group(
            group, columns=["image_url", "transcripts"]).to_pylist()
        random.Random(f"{path}/{group}").shuffle(table)
        for record in table[:400]:
            url = record.get("image_url") or ""
            answer = best_transcript(record.get("transcripts"))
            if not answer or not pixmo_url_ok(url) or url in seen:
                continue
            seen.add(url)
            row = with_child({"question": DETAILED, "answer": answer, "split": "",
                              "credit": PIXMO_CAP_CREDIT.format(url=url)}, answer)
            items.append((pixmo_name("pixmo-cap", url), url, "", [row]))
            if len(items) >= want:
                break
    say(f"  PixMo-Cap: fetching {len(items)} pictures from the web.")
    rows = fetch_checked(items, os.path.join(data_dir, source.key))
    for row in rows[:source.test]:
        row["split"] = "test"
    return rows[:cap + source.test]


# A plain name of a thing: one to three words, letters only (no "on", "in", "with", "left", "right" ... phrases).
PLAIN_THING = re.compile(r"^[a-z][a-z'-]*( [a-z][a-z'-]*){0,2}$")
NOT_PLAIN = re.compile(r"\b(on|in|at|of|with|without|near|behind|under|over|left|right|top|bottom|front|back|middle|"
                       r"center|centre|and|or|the|a|an|that|which|who|is|are|visible|other)\b")
NUMBER_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")


def count_rows(label, count):
    """The question and answer for one counting record: "How many books are there in this picture?" -> "There are
    21 books." (one: "There is one book."; none: "There are no books in this picture."), or None when the label is
    not a plain name of a thing, names something sexual, or more than 30 were pointed at."""
    thing = " ".join(str(label or "").lower().split())
    if not PLAIN_THING.match(thing) or NOT_PLAIN.search(thing) or SEXUAL.search(thing) or not 0 <= count <= 30:
        return None
    many = thing if thing.endswith("s") and not thing.endswith("ss") else plural(thing)
    number = NUMBER_WORDS[count] if count < len(NUMBER_WORDS) else str(count)
    answer = (f"There are no {many} in this picture." if count == 0 else f"There is one {thing}." if count == 1
              else f"There are {number} {many}.")
    return {"question": f"How many {many} are there in this picture?", "answer": answer}


def prepare_pixmo_points_count(source, data_dir, work, cap):
    """PixMo-Points counting records: row groups read in a shuffled order, at most three questions for each picture,
    every picture checked against its SHA-256."""
    fs, groups = parquet_groups(PIXMO_POINTS, 802)
    import pyarrow.parquet as pq
    want, per_picture = int((cap + source.test) * 1.4) + 10, collections.OrderedDict()
    total = 0
    for path, group in groups:
        if total >= want:
            break
        table = pq.ParquetFile(fs.open(f"datasets/{PIXMO_POINTS}/{path}")).read_row_group(
            group, columns=["image_url", "image_sha256", "points", "label", "collection_method"]).to_pylist()
        random.Random(f"{path}/{group}").shuffle(table)
        for record in table:
            url = record.get("image_url") or ""
            if record.get("collection_method") != "counting" or not pixmo_url_ok(url):
                continue
            row = count_rows(record.get("label"), len(record.get("points") or []))
            key = (url, record.get("image_sha256") or "")
            if row is None or len(per_picture.get(key, [])) >= 3 or \
                    any(r["question"] == row["question"] for r in per_picture.get(key, [])):
                continue
            per_picture.setdefault(key, []).append(dict(row, split="", credit=PIXMO_POINTS_CREDIT.format(url=url)))
            total += 1
            if total >= want:
                break
    items = [(pixmo_name("pixmo-count", url), url, digest, rows) for (url, digest), rows in per_picture.items()]
    say(f"  PixMo-Points: fetching {len(items)} pictures from the web ({total} questions).")
    rows = fetch_checked(items, os.path.join(data_dir, source.key))
    for row in rows[:source.test]:
        row["split"] = "test"
    return rows[:cap + source.test]


# ----------------------------------------------------------------- research: FinTabNet tables

FINTAB_REPO = "ds4sd/FinTabNet_OTSL"
FINTAB_CREDIT = ("FinTabNet (Xinyi Zheng, Douglas Burdick, Lucian Popa, Xu Zhong and Nancy Xin Ru Wang, IBM Research, "
                 "2021), annotations CDLA-Permissive-1.0, https://huggingface.co/datasets/ds4sd/FinTabNet_OTSL; table "
                 "from the {year} annual report of the company with the stock symbol {ticker} (the report belongs to "
                 "the company)")
TABLE_MOST_ROWS, TABLE_MOST_COLUMNS, TABLE_MOST_WORDS = 15, 6, 220
TABLE_FORMAT = re.compile(r"</?(b|i|u|em|strong|sup|sub|underline|strike|overline|span|br)\s*/?>", re.I)


def table_cell_text(cell):
    """The words of one table cell (as packs/bigtech_packs.ptn_cell_text): characters joined, marks taken out."""
    text = "".join(str(t) for t in ((cell or {}).get("tokens") or []))
    text = " ".join(html.unescape(TABLE_FORMAT.sub(" ", text)).split())
    return re.sub(r"\s*•\s*", ", ", text).strip(", ")


def table_grid(html_tokens, cells):
    """[(is a heading row, [cell words])] from the structure tokens and cells (as packs/bigtech_packs.ptn_grid); []
    when they do not match."""
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
            text = table_cell_text(cells[used]) if used < len(cells or []) else ""
            used += 1
            if current is not None:
                current.append(text)
    return rows if rows and used == len(cells or []) else []


def table_rows(grid, columns):
    """"Read this table to me." and its size (as packs/bigtech_packs.ptn_rows), or [] for a table too big, too wordy
    or mostly blank."""
    if not grid or len(grid) > TABLE_MOST_ROWS or columns > TABLE_MOST_COLUMNS or columns < 2:
        return []
    total = sum(len(cells) for _, cells in grid)
    if not total or sum(1 for _, cells in grid for c in cells if c) * 2 < total:
        return []
    lines = [f"Row {n}{' (headings)' if heading else ''}: " + "; ".join(c or "blank" for c in cells).rstrip(".") + "."
             for n, (heading, cells) in enumerate(grid, 1)]
    answer = f"This table has {len(grid)} rows and {columns} columns. " + " ".join(lines)
    if len(answer.split()) > TABLE_MOST_WORDS:
        return []
    headings = sum(1 for heading, _ in grid if heading)
    told = f"It has {len(grid)} rows and {columns} columns" + (
        "; the first row holds the headings." if headings == 1 else
        f"; the first {headings} rows hold the headings." if headings > 1 else ".")
    return [{"question": READ_Q, "answer": answer}, {"question": SIZE_Q, "answer": told}]


def fintab_report(filename):
    """(stock symbol, year) from a FinTabNet file name ("DFS.2012.page_94.pdf_81952.png" -> ("DFS", "2012"))."""
    m = re.match(r"^([A-Z.]+?)\.(\d{4})\.page_", str(filename or ""))
    return (m.group(1), m.group(2)) if m else ("not given", "unknown")


def prepare_fintabnet_tables(source, data_dir, work, cap):
    """FinTabNet tables: row groups of IBM's parquet copy in a shuffled order, at most 60 tables from each, the
    pictures saved from the parquet itself. The cap counts tables."""
    import pyarrow.parquet as pq
    fs, groups = parquet_groups(FINTAB_REPO, 803)
    want, rows, tables = cap + source.test, [], 0
    folder = os.path.join(data_dir, source.key)
    for path, group in groups:
        if tables >= want:
            break
        table = pq.ParquetFile(fs.open(f"datasets/{FINTAB_REPO}/{path}")).read_row_group(
            group, columns=["filename", "html", "cells", "cols", "image"]).to_pylist()
        random.Random(f"{path}/{group}").shuffle(table)
        taken = 0
        for record in table:
            made = table_rows(table_grid(record.get("html"), record.get("cells")), int(record.get("cols") or 0))
            if not made or taken >= 60:
                continue
            stem = re.sub(r"\W", "_", str(record.get("filename") or "").rsplit(".", 1)[0])
            picture = save(f"fintab-{stem}", ((record.get("image") or {}).get("bytes")) or b"", folder)
            if not picture:
                continue
            ticker, year = fintab_report(record.get("filename"))
            split = "test" if tables < source.test else ""
            rows += [dict(r, picture=picture, split=split, credit=FINTAB_CREDIT.format(ticker=ticker, year=year))
                     for r in made]
            tables += 1
            taken += 1
            if tables >= want:
                break
    say(f"  FinTabNet: {tables} tables.")
    return rows


# ----------------------------------------------------------------- the collections

BIGTECH_SOURCES = [
    Source("screenqa_rico", "ScreenQA: questions people asked about phone app screens, answered (personal use)",
           "Questions and answers CC BY 4.0 (github.com/google-research-datasets/screen_qa); Rico screenshots: no "
           "licence or terms stated", SCREENQA_CREDIT, "research", 4000, 30, prepare_screenqa_rico,
           "up to 6.4 GB read from the web (only until enough screens are found); about 300 MB kept",
           terms="https://github.com/google-research-datasets/screen_qa",
           terms_summary=research("The questions and answers are CC BY 4.0; the Rico screenshots have no licence or "
                                  "terms written.")),
    Source("pixmo_cap_spoken", "PixMo-Cap: pictures from the web described aloud by people for a minute or more, "
                               "transcribed (personal use)",
           "ODC-BY 1.0 for the transcripts, \"intended for research and educational use\" (huggingface.co/datasets/"
           "allenai/pixmo-cap); the pictures are web addresses with no licence of their own",
           "PixMo-Cap (Deitke, Clark and others, Allen Institute for AI, 2024), ODC-BY 1.0, "
           "https://huggingface.co/datasets/allenai/pixmo-cap", "research", 4000, 30, prepare_pixmo_cap_spoken,
           "about 600 MB of pictures fetched one by one from many websites",
           terms=PIXMO_TERMS,
           terms_summary=research("ODC-BY 1.0, for research and educational use under the Allen Institute's "
                                  "Responsible Use Guidelines; the pictures belong to their owners on the web.")),
    Source("pixmo_points_count", "PixMo-Points: how many of a thing are in a picture, from people pointing at each "
                                 "one (personal use)",
           "ODC-BY 1.0 (huggingface.co/datasets/allenai/pixmo-points); the pictures are web addresses with no "
           "licence of their own",
           "PixMo-Points (Allen Institute for AI, 2024), ODC-BY 1.0, https://huggingface.co/datasets/allenai/"
           "pixmo-points", "research", 3000, 30, prepare_pixmo_points_count,
           "about 400 MB of pictures fetched one by one from many websites",
           terms=PIXMO_TERMS,
           terms_summary=research("ODC-BY 1.0, for research and educational use under the Allen Institute's "
                                  "Responsible Use Guidelines; the pictures belong to their owners on the web.")),
    Source("fintabnet_tables", "FinTabNet: tables from companies' annual reports, read out (personal use)",
           "Annotations CDLA-Permissive-1.0 (IBM); the table pictures are cut from S&P 500 companies' annual "
           "reports, which belong to the companies", FINTAB_CREDIT.format(ticker="(each row's)", year="(each row's)"),
           "research", 2000, 30, prepare_fintabnet_tables,
           "about 150 to 400 MB read from Hugging Face (whole row groups); about 60 MB kept",
           terms="https://huggingface.co/datasets/ds4sd/FinTabNet_OTSL",
           terms_summary=research("IBM's annotations are CDLA-Permissive-1.0; the reports the tables come from "
                                  "belong to the companies.")),
]

# The collections a picture-making model may learn from: tables only (no people).
BIGTECH_PICTURE_MAKING_OK = {"fintabnet_tables"}

# Big-company picture sets already in the kit, and where (so they are not added twice).
BIGTECH_ALREADY_IN_THE_KIT = {
    "Google": "Open Images V7 (open_images_* packs, oi_expressions), Crossmodal-3600 (xm3600, crossmodal), "
              "Localized Narratives (localized_narratives, ln_coco, ln_open_images_more, ln_coco_nc), DOCCI (docci), "
              "ImageInWords (imageinwords), WIT (wikipedia, share-alike), Google Landmarks v2 (gldv2_landmarks, "
              "gldv2_sa), Screen2Words and Widget Captioning on Rico (rico_screens, rico_widgets), HierText "
              "(hiertext), Nutrition5k (nutrition5k), Fashionpedia (fashionpedia), A-OKVQA answers' Open Images "
              "photos (coco_questions); Objectron in device_sources.py's not-included notes.",
    "Microsoft": "COCO (coco, coco_questions, coco_nc ...), ORBIT (orbit); VizWiz (University of Texas, with "
                 "Microsoft support: vizwiz_captions, vizwiz_vqa, vizwiz_quality), MS-ASL noted in extra_sources.py.",
    "Meta": "TextCaps, TextVQA and TextOCR (textcaps, textvqa, textocr), nocaps (nocaps), Visual Dialog (visdial, "
            "vqa_expressions), LVIS (things_sources.py, us_sources.py), PACO (paco_attributes), CO3D (co3d_devices), "
            "Charades (Allen AI with others: charades); SA-1B and DCI as a sign-up note in extra_sources.py; Ego4D, "
            "EgoObjects and Ego-Exo-style sets in signup_sources.py, things_sources.py and people_activity_sources.py.",
    "Amazon": "Amazon Berkeley Objects (abo_products).",
    "Apple": "Hypersim (hypersim, share-alike).",
    "IBM": "DocLayNet (doclaynet).",
    "Allen Institute for AI": "A-OKVQA (coco_questions), AI2D (ai2d), ScienceQA (scienceqa, UCLA with Allen AI), "
                              "Charades (charades).",
    "Yahoo": "YFCC100M: handled in signup_sources.py (another entry), not here.",
}

BIGTECH_SIGN_UP = {
    "Segment Anything SA-1B and DCI (Meta)":
        "https://ai.meta.com/datasets/segment-anything-downloads/ : accept Meta's SA-1B research licence to get the "
        "download links (already listed in extra_sources.py with DCI's human-written region descriptions).",
    "Ego-Exo4D (Meta and partners)":
        "https://ego-exo4d-data.org : sign the Ego4D/Ego-Exo4D licence agreement to get AWS keys; skilled activities "
        "(cooking, bike repair, music, health care) filmed by the wearer and from outside, with expert commentary. "
        "People in every video: describing only, never for picture-making.",
    "Project Aria datasets (Meta): Aria Everyday Activities, Aria Everyday Objects, Aria Digital Twin, HOT3D":
        "https://www.projectaria.com/datasets/ : accept the Project Aria research licence (non-commercial) on the "
        "page to get links; first-person views of homes and everyday objects, close to what a blind person's "
        "camera sees. People appear: describing only.",
    "Casual Conversations v1 and v2 (Meta)":
        "https://ai.meta.com/datasets/casual-conversations-v2-dataset/ : a signed agreement; Meta's summary: \"You "
        "can evaluate models on the provided labels. You can only train your model on certain labels\". Videos of "
        "paid adults talking to the camera: not used (see BIGTECH_NOT_INCLUDED).",
    "Waymo Open Dataset (Google)":
        "https://waymo.com/open/ : sign in and accept the non-commercial licence; street scenes from self-driving "
        "cars, labelled boxes only (no descriptions).",
    "ARMBench (Amazon), full archives":
        "https://huggingface.co/datasets/amazon/armbench-defect-image : open (CC BY 4.0), but 65 GB in one archive; "
        "warehouse photos of products in totes, with \"multi-pick\" and \"package opened or broken\" labels. Could "
        "be an open pack from its 70 MB \"tiny\" archive; not built, as a robot's view of a tote is far from what "
        "a blind person photographs.",
    "VIST, Visual Storytelling (Microsoft Research and others)":
        "https://visionandlanguage.net/VIST/ : the descriptions of single photos (\"descriptions in isolation\") are "
        "people's words, but the photos are Flickr albums with no licence stated, and the download links were not "
        "checked from this machine.",
    "Kaputt (Amazon, 2025)":
        "https://huggingface.co/datasets/amazon/kaputt : retail items with and without defects; its licence is "
        "\"other\" (a non-commercial research licence on the card): accept it on Hugging Face to download.",
}

BIGTECH_NOT_INCLUDED = {
    "Conceptual Captions CC3M and CC12M (Google), WebLI (Google, not released), RedCaps, COYO, DataComp, LAION, "
    "MetaCLIP (Meta), Apple DFN and DataComp-DR, Salesforce BLIP CapFilt, BLIP3-KALE, BLIP3-OCR and MINT-1T, "
    "OBELICS, MMC4":
        "scraped web image sets: pictures taken from the web with their alt text or machine captions, of unknown "
        "rights. The kit's rule leaves every such set out.",
    "PixMo-Docs, PixMo-CapQA, PixMo-AskModelAnything and PixMo-Cap's own captions (Allen AI)":
        "written or rewritten by AI models (Claude and others); the kit only learns people's words. PixMo-Cap's "
        "transcripts and PixMo-Points are used (pixmo_cap_spoken, pixmo_points_count).",
    "PixMo-Clocks (Allen AI)": "only the settings of virtual watch faces from facer.io: the pictures are not "
                               "published and the watch faces belong to their designers.",
    "PixMo-Count (Allen AI)": "its training counts were made by a detector (Detic); only its small checked "
                              "validation and test sets are people's, and PixMo-Points already gives people's counts.",
    "LLaVA-Instruct, ShareGPT4V, Docmatix, olmOCR-mix, CoSyn-400K, Llama-Nemotron VLM data (NVIDIA), Describe "
    "Anything (NVIDIA), PLM-Image-Auto (Meta), Pico-Banana-400K (Apple), ScreenQA Short and ComplexQA (Google)":
        "their words (or pictures) were made by AI models.",
    "FACET (Meta)": "Meta's page: \"Intended Use Cases: Research purposes only. Measure or evaluate the robustness "
                    "and algorithmic fairness of AI and machine-learning vision models\"; \"The images are licensed "
                    "from a large photo company.\" People labelled with perceived skin tone and other attributes: "
                    "an evaluation set, not descriptions. Not used.",
    "Casual Conversations v1 and v2 (Meta)": "videos of paid adults talking to the camera, made for measuring "
                                             "fairness (\"You can only train your model on certain labels\"); not "
                                             "pictures to describe. Never used.",
    "MIAP, More Inclusive Annotations for People (Google, Open Images Extended)":
        "boxes round people labelled with perceived gender and age, for fairness research; Google asks that it not "
        "be used to build gender or age classifiers, and it describes nothing.",
    "Diversity in Faces (IBM), MS-Celeb-1M (Microsoft), FFHQ (NVIDIA)":
        "face sets: withdrawn by their makers (Diversity in Faces, MS-Celeb-1M) or faces only under CC BY-NC-SA "
        "(FFHQ). Faces are not a describing task, and never for picture-making.",
    "Hateful Memes (Meta)": "made to detect hateful content; its pictures are Getty Images under a research "
                            "licence. Not something to describe.",
    "Winoground (Meta)": "pictures licensed from Getty Images for evaluation only.",
    "Objectron (Google, C-UDA 1.0)": "already noted in device_sources.py: few everyday kinds, already covered.",
    "Google Quick, Draw! (CC BY 4.0)": "50 million doodles drawn in 20 seconds: not pictures a blind person needs "
                                       "described.",
    "Open Buildings, Waymo, Google Earth Engine sets (Google)": "satellite or driving data with no descriptions.",
    "Android in the Wild and AndroidControl (Google)":
        "phone screens with the steps of tasks (\"tap the search bar\"); the steps are not descriptions, and the "
        "screenshots show third-party apps' content with no licence stated. ScreenQA is used instead.",
    "Screen Annotation (Google)": "a list of each screen element's kind and position, not people's words; the same "
                                  "Rico screens as ScreenQA.",
    "Google RefExp and Crisscrossed Captions (Google)": "phrases that pick out one region of a COCO photo, and "
                                                        "similarity scores between COCO captions: COCO is already "
                                                        "used with its own descriptions.",
    "Fashion IQ (IBM)": "relative captions (\"is darker and has longer sleeves\") on Amazon product photos taken "
                        "from Amazon's site, with no licence for the photos.",
    "PubLayNet (IBM)": "page layouts (boxes for title, text, list, table, figure): DocLayNet already gives document "
                       "pages with their kinds and titles. Its pages are PMC articles of mixed licences.",
    "PubTables-1M (Microsoft, CDLA-Permissive-2.0)": "table structure for PMC articles: the open pubtabnet_tables "
                                                     "pack already reads PMC tables, with each article's licence "
                                                     "checked.",
    "PubTabNet tables from CC BY-SA and CC BY-ND articles":
        "the PMC commercial-use collection also has CC BY-SA and CC BY-ND articles; few, and left out of the open "
        "pack. A share-alike entry could be added later.",
    "SynthTabNet (IBM)": "computer-made tables with made-up text.",
    "ARKitScenes (Apple)": "3D scans of rooms with furniture boxes only (no descriptions); its own licence is "
                           "non-commercial.",
    "MIT-Adobe FiveK (Adobe and MIT)": "photos for teaching photo retouching, with no descriptions; Adobe's licence "
                                       "for each photo is for research.",
    "Behance Artistic Media (Adobe)": "artwork collected from Behance, research licence, no descriptions.",
    "SciCap (Penn State with Adobe)": "figures from arXiv papers with their authors' captions, CC BY-NC-SA; "
                                      "scientific figures are already covered by PlotQA, ChartQA and the case-report "
                                      "figures.",
    "imSitu and Visual Commonsense Reasoning (University of Washington and Allen AI)":
        "imSitu's photos come from Google Image Search and VCR's from films: no rights to the pictures, and VCR's "
        "licence is for research and asks that frames not be redistributed.",
    "TQA, Textbook Question Answering (Allen AI)": "school-textbook diagrams (CK-12, CC BY-NC); AI2D and ScienceQA "
                                                   "already give school diagrams.",
    "Objaverse (Allen AI)": "800,000 3D models, each under its own licence (many CC BY-NC); computer-made renders, "
                            "and Google Scanned Objects already gives real products.",
    "NVIDIA synthetic sets (Physical AI, warehouse and robot scenes)": "computer-made scenes for robots, no "
                                                                      "descriptions.",
    "Amazon Reviews '23 (UCSD) and Amazon product photos beyond ABO":
        "customers' photos and product pictures taken from Amazon's site, no licence for the pictures; Amazon's own "
        "open product set (ABO) is already used.",
    "ShopBench, ShoppingReasoningBench, AmazonQAC (Amazon)": "text only, or CC BY-NC text about products with no "
                                                            "pictures of their own.",
    "ABO-Edit (Amazon)": "computer-edited versions of ABO product photos: the originals are already used.",
    "YFCC100M (Yahoo)": "handled in signup_sources.py, not here.",
}
