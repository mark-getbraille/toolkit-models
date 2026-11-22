"""Historical US newspapers for the Writing Kit (added on 22 November 2026 at the owner's request): the American
Stories dataset, kept in this one file so it is easy to merge with other work on the kit. writing_sources.py adds
SOURCES and NOT_USED from here, styles.py adds the style labels, build_dataset.py reads a sample with
read_american_stories, and build_newspapers.py downloads and builds the whole corpus.

The source, key american_stories_newspapers
  American Stories (Melissa Dell, Jacob Carlson, Tom Bryan, Emily Silcock, Abhishek Arora, Zejiang Shen, Luca
  D'Amico-Wong, Quan Le, Pablo Querubin and Leander Heldring, 2023): the article texts found on nearly 20 million
  public-domain newspaper page scans of the Library of Congress's Chronicling America collection, 1770 to 1964,
  each scan read with the authors' own layout detection and OCR. Licence: CC BY 4.0 (the dataset card says "The
  dataset has a CC-BY 4.0 license", and the repository holds the CC BY 4.0 legal text as LICENSE). The card asks to
  cite the paper (CITATION below).
  On Hugging Face as dell-research-harvard/AmericanStories: one file per year, faro_<year>.tar.gz, 180 files, 340.4 GB
  in all (checked 22 November 2026; the largest, 1910, is 7.6 GB). The dataset is public and not gated, so no key is
  needed; huggingface.co's robots.txt allows every program, and its terms let downloaded content be used under the
  content's own licence. The kit downloads the same files the dataset's own loading script uses (the
  ".../resolve/main/faro_<year>.tar.gz" addresses) and lists them, with their sizes and checksums, through the
  Hugging Face file-list interface (api/datasets/.../tree/main).

What a year file holds
  A folder faro_<year>/ with one JSON file per page scan, named <date>_<page>_<lccn>_<reel>_<issue><edition>_<seq>.json
  (for example 1910-07-16_p7_sn92070146_00175047220_1910071601_0677.json; the page is "pna" when unknown). Each has
  "lccn" (the newspaper: title, state ...), "bboxes" (every region of the page with its class: article, headline or
  author, and from about 1800 on its "legibility": Legible, Questionable or Illegible) and "full articles" (each
  article with its headline, byline and text, and "object_ids": the regions it was made from).
  There is NO field saying what kind of article it is (news, advertisement, notice ...), so the kit decides that by
  simple rules (classify, below).

What the kit makes of each article
  One training example: the instruction asks for that kind of article for that newspaper and date, with its headline
  and byline; the answer is the article text EXACTLY as printed (OCR mistakes included; only the line breaks of the
  page's columns are joined, except in poems). Every article that has any text is kept: nothing is dropped for OCR
  quality, and nothing is scrubbed (the owner's decision of 22 November 2026, see SOURCE_UNCHANGED). Each example
  also carries: year, decade, date, newspaper, state, lccn, page, edition, article_id, headline, byline,
  ocr_quality, legibility and style_rule (which rule chose the style), so training can choose eras, styles and OCR
  quality later.

The style rules (classify), tried in this order on the headline and the start (and end) of the text:
  newspaper_notice_historical         legal and public notices: "Notice is hereby given", sheriff's and trustee's
                                      sales, summonses, court and probate notices, estates of the deceased, sealed
                                      bids and proposals, ordinances, election notices, estrays, dissolutions
  newspaper_letter_historical         letters to the editor: a headline such as "To the Editor", "Communicated",
                                      "Voice of the People", "Open Letter", or a text that opens "To the Editor",
                                      "Mr. Editor", "Messrs. Editors", "Dear Sir"
  newspaper_fiction_poetry_historical serial fiction and poems: "Chapter IV", "To be continued", "Synopsis",
                                      "Copyright, 1910, by", "a story"; or a headline with poem, verses, sonnet,
                                      ballad, hymn, ode; or (tried last, after the advertisement rule, and only with
                                      fewer than two signs of an advertisement) a text of six or more short lines
                                      that nearly all start with a capital
  newspaper_editorial_historical      editorials and opinion: a headline that starts "Editorial", "Opinion", "Comment",
                                      "Views of the Press", "What Other Editors Say", "Topics of the Day"; or two
                                      editorial phrases ("in our opinion", "it seems to us", "we believe that",
                                      "our esteemed contemporary" ...) in the first 3,000 characters, or one with
                                      "we/our/us" making at least 2 in 100 words
  newspaper_ad_historical             advertisements that were printed in article boxes: a headline such as "For
                                      Sale", "Wanted", "Lost", "To Let", "Bargains" with one sign of an
                                      advertisement, or three different signs (prices in dollars or cents, "per
                                      yard", "sold by", "call at", "apply to", "all druggists", cures, bitters and
                                      pills, "low prices", stock and goods) in the first 1,500 characters of a text under
                                      400 words
  newspaper_news_historical           everything else: news reports, local items, dispatches

ocr_quality (0 to 1): the share of the article's words that are ordinary English words in the kit's wordlists.json.
Numbers and capitalised words not in the list (names and places) are not counted either way; tokens that mix
letters with digits or symbols ("1t", "AbriI3") count as not words. legibility (0 to 1, or empty before about 1800):
the share of the article's page regions that American Stories' own classifier called Legible (Questionable counts
half). Neither is used to leave anything out.
"""

import hashlib
import json
import os
import re
import tarfile
import urllib.error

import names
import sources_more

SOURCE_KEY = "american_stories_newspapers"
HF_DATASET = "dell-research-harvard/AmericanStories"
HF_HOME = "https://huggingface.co/datasets/dell-research-harvard/AmericanStories"
HF_TREE = "https://huggingface.co/api/datasets/dell-research-harvard/AmericanStories/tree/main"
HF_FILE = "https://huggingface.co/datasets/dell-research-harvard/AmericanStories/resolve/main/{name}"
YEAR_FILE = re.compile(r"^faro_(\d{4})\.tar\.gz$")
FULL_SIZE_GB = 340.4              # all 180 year files, checked 22 November 2026
CC_BY = "https://creativecommons.org/licenses/by/4.0/"
LICENCE = "CC BY 4.0"
CREDIT = ("American Stories: A Large-Scale Structured Text Dataset of Historical U.S. Newspapers, by Melissa Dell, "
          "Jacob Carlson, Tom Bryan, Emily Silcock, Abhishek Arora, Zejiang Shen, Luca D'Amico-Wong, Quan Le, Pablo "
          "Querubin and Leander Heldring (2023, arXiv:2308.12477), made from the Library of Congress's Chronicling "
          "America newspaper scans (public domain)")
CITATION = """@misc{dell2023american,
      title={American Stories: A Large-Scale Structured Text Dataset of Historical U.S. Newspapers},
      author={Melissa Dell and Jacob Carlson and Tom Bryan and Emily Silcock and Abhishek Arora and Zejiang Shen and Luca D'Amico-Wong and Quan Le and Pablo Querubin and Leander Heldring},
      year={2023},
      eprint={2308.12477},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}"""

# The owner's decision (22 November 2026): this source is NOT scrubbed. Historical newspapers hold no Social
# Security, card or account numbers or passwords, and the text must stay exactly as printed, so the records are
# marked "unchanged" and build_dataset.py passes them through without scrub.py (under either privacy setting).
SOURCE_UNCHANGED = True

# Off in the ordinary build unless named in --sources (the whole corpus is 340 GB: build_newspapers.py builds it).
OPT_IN = {SOURCE_KEY}
# The years read for a sample build when nothing has been downloaded yet (only the start of each file is read).
SAMPLE_YEARS = ("1805", "1835", "1865", "1885", "1905", "1925", "1955")

# New style labels (styles.py adds them to its list): name -> what it is.
STYLES = {
    "newspaper_news_historical": "newspaper news report (historical, 1770 to 1964)",
    "newspaper_editorial_historical": "newspaper editorial or opinion (historical)",
    "newspaper_ad_historical": "newspaper advertisement (historical)",
    "newspaper_letter_historical": "newspaper letter to the editor (historical)",
    "newspaper_notice_historical": "newspaper notice or legal notice (historical)",
    "newspaper_fiction_poetry_historical": "newspaper serial fiction or poetry (historical)",
}
FORMAL = {"newspaper_news_historical", "newspaper_editorial_historical", "newspaper_letter_historical",
          "newspaper_notice_historical"}
CASUAL = set()

# What the instruction asks for, and the example's "kind", for each style.
ASK = {
    "newspaper_news_historical": ("news report", "Write a news report"),
    "newspaper_editorial_historical": ("editorial", "Write a newspaper editorial"),
    "newspaper_ad_historical": ("advertisement", "Write a newspaper advertisement"),
    "newspaper_letter_historical": ("letter to the editor", "Write a letter to the editor"),
    "newspaper_notice_historical": ("notice", "Write a public or legal notice"),
    "newspaper_fiction_poetry_historical": ("serial fiction or poetry", "Write a story installment or poem"),
}


# ====================================================================== the list of year files, and choosing years

def year_files(listing):
    """[{"year", "name", "size", "sha256", "url"}] in year order, from the Hugging Face file list (the JSON of
    HF_TREE, as text or already read)."""
    items = json.loads(listing) if isinstance(listing, (str, bytes)) else listing
    out = []
    for item in items:
        m = YEAR_FILE.match(str(item.get("path", "")))
        if m and item.get("type", "file") == "file":
            lfs = item.get("lfs") or {}
            out.append({"year": int(m.group(1)), "name": item["path"], "size": int(lfs.get("size") or item["size"]),
                        "sha256": lfs.get("oid", ""), "url": HF_FILE.format(name=item["path"])})
    return sorted(out, key=lambda f: f["year"])


def parse_years(text):
    """A test (year -> True or False) from what the owner types: years, ranges and decades separated by commas,
    for example "1850-1869, 1900, 1920s, 1950-". Empty means every year. Raises ValueError for anything else."""
    parts = [p.strip() for p in str(text or "").split(",") if p.strip()]
    if not parts:
        return lambda year: True
    spans = []
    for p in parts:
        m = re.fullmatch(r"(\d{4})s", p) or re.fullmatch(r"(\d{4})\s*-\s*(\d{4})?", p) or re.fullmatch(r"(\d{4})", p)
        if not m:
            raise ValueError(f"not a year, range or decade: {p!r} (examples: 1865, 1850-1869, 1920s, 1950-)")
        if p.endswith("s"):
            start = int(m.group(1)) // 10 * 10
            spans.append((start, start + 9))
        elif "-" in p:
            spans.append((int(m.group(1)), int(m.group(2)) if m.group(2) else 9999))
        else:
            spans.append((int(m.group(1)), int(m.group(1))))
    return lambda year: any(a <= int(year) <= b for a, b in spans)


def choose(files, years="", max_gb=0):
    """(chosen, left_out): the year files whose year matches years, oldest first, stopping before the total size
    would pass max_gb gigabytes (0: no cap). left_out lists the matching files that did not fit under the cap."""
    wanted = parse_years(years)
    chosen, left_out, total = [], [], 0
    for f in files:
        if not wanted(f["year"]):
            continue
        if max_gb and total + f["size"] > max_gb * 1e9:
            left_out.append(f)
            continue
        chosen.append(f)
        total += f["size"]
    return chosen, left_out


def gb(n):
    """A size in bytes as gigabytes for reading aloud ("7.62 GB")."""
    return f"{n / 1e9:.2f} GB"


def hours_text(n_bytes, megabits):
    """How long n_bytes take at a connection of megabits a second, in words."""
    hours = n_bytes * 8 / (megabits * 1e6) / 3600
    return f"about {hours:.0f} hours" if hours >= 2 else f"about {max(1, round(hours * 60))} minutes"


def download_years(fetcher, folder, chosen, say=print, free_bytes=None):
    """Download the chosen year files into folder (resumable: run again to carry on). Says each file's size, its
    place in the list and the running total. Stops before a file that would not fit in the free disk space
    (free_bytes, measured when not given). Returns [(year, "downloaded" | "already" | reason)]."""
    import shutil
    os.makedirs(folder, exist_ok=True)
    total = sum(f["size"] for f in chosen)
    done_bytes, results = 0, []
    for n, f in enumerate(chosen, 1):
        dest = os.path.join(folder, f["name"])
        have = os.path.getsize(dest) if os.path.exists(dest) else 0
        part = os.path.getsize(dest + ".part") if os.path.exists(dest + ".part") else 0
        if have != f["size"]:
            free = free_bytes if free_bytes is not None else shutil.disk_usage(folder).free
            if f["size"] - part > free:
                say(f"STOPPED before {f['year']}: it needs {gb(f['size'] - part)} and only {gb(free)} is free on "
                    "that disk. Free some space or choose fewer years, then run again.")
                results.append((f["year"], "not enough disk space"))
                break
        say(f"Year {f['year']}: {gb(f['size'])} (file {n} of {len(chosen)}; {gb(done_bytes)} of {gb(total)} done "
            "before it).")
        try:
            how = fetcher.download(f["url"], dest, size=f["size"], sha256=f["sha256"] or None, say=say)
        except (OSError, ValueError, urllib.error.URLError) as err:
            say(f"  {f['year']}: not finished ({err}). Run again later to resume.")
            results.append((f["year"], str(err)))
            continue
        if free_bytes is not None and how == "downloaded":
            free_bytes -= f["size"] - part
        done_bytes += f["size"]
        say(f"  {f['year']}: {'already downloaded' if how == 'already' else 'downloaded'}. Running total "
            f"{gb(done_bytes)} of {gb(total)}.")
        results.append((f["year"], how))
    return results


def local_year_files(folder, years=""):
    """[(year, path)] of the complete year files in folder (no ".part"), oldest first, matching years."""
    wanted = parse_years(years)
    out = []
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            m = YEAR_FILE.match(name)
            if m and wanted(int(m.group(1))):
                out.append((int(m.group(1)), os.path.join(folder, name)))
    return sorted(out)


# ====================================================================== reading the articles of a year file

SCAN_NAME = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})_(?P<page>p\w+?)_(?P<lccn>[a-z]+\d+)_(?P<reel>[^_]+)_"
                       r"(?P<issue>\d{8})(?P<edition>\d{2})_(?P<seq>\d+)")


def scan_info(member_name):
    """{date, page, lccn, reel, edition, seq} from a scan's file name ("" for parts it does not have)."""
    base = os.path.basename(member_name).rsplit(".", 1)[0]
    m = SCAN_NAME.match(base)
    if not m:
        return {"date": base[:10] if re.match(r"\d{4}-\d{2}-\d{2}", base) else "", "page": "", "lccn": "",
                "reel": "", "edition": "", "seq": "", "scan_id": base}
    page = m.group("page")[1:]
    return {"date": m.group("date"), "page": "" if page == "na" else page, "lccn": m.group("lccn"),
            "reel": m.group("reel"), "edition": m.group("edition"), "seq": m.group("seq"), "scan_id": base}


def newspaper_name(title):
    """A newspaper's title as Chronicling America gives it, tidied for an instruction:
    "The Massachusetts spy. [volume] (Boston [Mass.]) 1770-1772" -> "The Massachusetts spy (Boston [Mass.])"."""
    title = re.sub(r"\s*\[volume\]", "", str(title or ""))
    title = re.sub(r"\s+\d{4}-(\d{4}|current)?\s*\.?$", "", title.strip())
    title = re.sub(r"\.\s+\(", " (", title)
    return re.sub(r"\s+", " ", title).strip().rstrip(".")


LEGIBLE = {"legible": 1.0, "questionable": 0.5, "illegible": 0.0}


def legibility(article, regions):
    """The share of an article's page regions that American Stories called Legible (Questionable counts half), or
    None when the scan has no legibility labels (the earliest years)."""
    marks = [LEGIBLE.get(str(regions.get(i, {}).get("legibility", "")).lower()) for i in article.get("object_ids") or []]
    marks = [m for m in marks if m is not None]
    return round(sum(marks) / len(marks), 3) if marks else None


def articles_of_scan(data, member_name):
    """The articles of one scan (its JSON already read), each a dict with the newspaper, date, page, headline,
    byline, text and legibility."""
    info = scan_info(member_name)
    lccn = data.get("lccn") or {}
    regions = {b.get("id"): b for b in data.get("bboxes") or []}
    date = info["date"] or str((data.get("edition") or {}).get("date", ""))
    year = int(date[:4]) if date[:4].isdigit() else 0
    for art in data.get("full articles") or []:
        yield {"article_id": f"{art.get('full_article_id', '')}_{info['scan_id']}", "year": year,
               "decade": f"{year // 10 * 10}s" if year else "", "date": date,
               "page": info["page"] or str(data.get("page_number") or ""), "edition": info["edition"],
               "lccn": info["lccn"] or lccn.get("lccn", ""), "newspaper_title": lccn.get("title", ""),
               "newspaper": newspaper_name(lccn.get("title", "")), "state": lccn.get("state", ""),
               "headline": art.get("headline") or "", "byline": art.get("byline") or "",
               "text": art.get("article") or "", "legibility": legibility(art, regions)}


def year_articles(stream):
    """Every article in a year file (an open binary stream of the .tar.gz, read as it arrives)."""
    with tarfile.open(fileobj=stream, mode="r|gz") as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith(".json"):
                continue
            try:
                data = json.loads(tar.extractfile(member).read().decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                continue
            if isinstance(data, dict) and "full articles" in data:
                yield from articles_of_scan(data, member.name)


# ====================================================================== OCR quality (recorded, never used to drop)

KNOWN = {w.lower() for w in names.COMMON_WORDS} | {w.lower() for w in names.PUBLIC_NAMES}
PLAIN_WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
NUMBERISH = re.compile(r"[\d.,$/%:\-]+|\d+(?:st|nd|rd|th|d)")


def ocr_quality(text, known=None):
    """The share (0 to 1, three decimals) of text's words that are ordinary English words (see the module notes)."""
    known = KNOWN if known is None else known
    good = bad = 0
    for raw in str(text or "").split():
        w = raw.strip(".,;:!?\"'()[]{}*-_\u2014\u2018\u2019\u201c\u201d")
        if not w:
            continue
        low = w.lower()
        if low in known:                                   # the usual case first, for speed
            good += 1
        elif w.isalpha() and w.isascii():
            if len(w) > 1 and w[0].isupper() and w[1:].islower():
                continue                                   # a name or a place: counted neither way
            bad += 1
        elif NUMBERISH.fullmatch(w):
            continue
        elif PLAIN_WORD.fullmatch(w) and low.endswith("'s") and low[:-2] in known:
            good += 1
        else:
            bad += 1                                       # letters mixed with digits or symbols
    return round(good / (good + bad), 3) if good + bad else 0.0


# ====================================================================== the style rules (see the module notes)

NOTICE = re.compile(
    r"(?i)\b(notice is hereby given|legal notice|public notice|notice to (creditors|contractors|bidders|taxpayers|"
    r"water users|the public)|notice of (sale|election|application|dissolution|hearing)|sheriff'?s sale|trustee'?s "
    r"sale|master'?s sale|mortgage sale|foreclosure|summons|in the (circuit|district|county|probate|chancery|superior|"
    r"justice'?s) court|estate of .{0,40}deceased|administrat(or|rix)'?s? (notice|sale)|executor'?s? (notice|sale)|"
    r"guardian'?s sale|sealed (bids|proposals)|proposals (for|will be received)|notice inviting bids|an ordinance|be "
    r"it ordained|be it enacted|election notice|estray|dissolution of (co-?)?partnership)")
LETTER_HEAD = re.compile(r"(?i)\b(letter to the editor|to the editor|communicated|communication|voice of the people|"
                         r"people'?s forum|open letter|readers'? (views|forum)|from our readers)\b")
LETTER_OPEN = re.compile(r"(?i)^\W*(to the editors?\b|mr\.? editor|messrs\.? editors|editor (of )?the\b|dear sir\b|"
                         r"editor\s+\w+[,:])")
FICTION = re.compile(r"(?i)(\bchapter [ivxlc\d]+\b|\bto be continued\b|\bcontinued from (last|yesterday)|\bsynopsis\b|"
                     r"\bserial story\b|\ba (short |true )?story\b|\bcopyright,? \d{4},? by\b|\bthe story so far\b|"
                     r"\bwhat has gone before\b)")
POEM_HEAD = re.compile(r"(?i)\b(poem|poetry|verses?|sonnet|ballad|hymn|ode|lines (on|to|written))\b")
EDITORIAL_HEAD = re.compile(r"(?i)^\W*(editorials?|editor'?s (note|notes|table|drawer)|opinions?|our view|comments?|"
                            r"current comment|views of the press|press comment|what (other )?(editors|papers) say|"
                            r"topics of the (day|times)|as we see it)\b")
EDITORIAL_TEXT = re.compile(r"(?i)\b(in our (opinion|judgment|judgement)|we are of (the )?opinion|it seems to us|"
                            r"we (believe|think|submit|maintain|trust|hope|venture to say) that|we have (often|always|"
                            r"repeatedly) (said|urged|contended)|our (esteemed )?contemporary|this paper (has|is))\b")
WE_WORDS = re.compile(r"(?i)\b(we|our|us|ourselves)\b")
AD_HEAD = re.compile(r"(?i)^\W*(for sale|for rent|to let|to rent|wanted|lost|found|strayed|auction|bargains?|"
                     r"special sale|great sale|clearance|removal|new goods|just received)\b")
AD_SIGNALS = [re.compile(p) for p in (
    r"\$\s?\d", r"(?i)\b\d+\s?(cents|cts)\b",
    r"(?i)\bper (yard|pound|lb|dozen|doz|bottle|box|pair|bushel|barrel|gallon|ton|month|week)\b",
    r"(?i)\b(for sale (by|at)|sold by|sold everywhere|all druggists|call (at|on)|apply (to|at)|inquire (of|at)|"
    r"manufactured by|agents? wanted|send for|free (trial|sample|catalogue)|cash or (credit|terms))\b",
    r"(?i)\b(cures?|remedy|remedies|bitters|pills|tonic|sarsaparilla|liniment)\b",
    r"(?i)\b(bargains?|low(est)? prices?|cheap(est)?|discount|prices? (reduced|cut)|great reductions?|on sale)\b",
    r"(?i)\b(stock|goods|assortment|merchandise)\b")]


def looks_like_poem(text):
    """True for a text of at least six short lines that nearly all start with a capital letter (prose set in
    newspaper columns has short lines too, but most of them start with a small letter)."""
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if len(lines) < 6 or len(" ".join(lines).split()) > 600:
        return False
    capitals = sum(1 for ln in lines if ln[0].isupper() or (ln[0] in "\"'“" and ln[1:2].isupper()))
    hyphen_ends = sum(1 for ln in lines if ln.endswith("-"))
    return capitals / len(lines) >= 0.8 and sum(map(len, lines)) / len(lines) <= 50 and hyphen_ends <= 1


def classify(headline, text):
    """(style, rule): the style of one article and the name of the rule that chose it (see the module notes)."""
    head = " ".join(str(headline or "").split())
    body = str(text or "")
    start, end = body[:400], body[-200:]
    if NOTICE.search(head) or NOTICE.search(start):
        return "newspaper_notice_historical", "notice words"
    if LETTER_HEAD.search(head) or LETTER_OPEN.search(start[:120]):
        return "newspaper_letter_historical", "letter to the editor words"
    if FICTION.search(head) or FICTION.search(start[:300]) or re.search(r"(?i)to be continued", end):
        return "newspaper_fiction_poetry_historical", "serial story words"
    if POEM_HEAD.search(head):
        return "newspaper_fiction_poetry_historical", "poem"
    words = body.split()
    phrases = len(EDITORIAL_TEXT.findall(body[:3000]))
    if EDITORIAL_HEAD.search(head) or phrases >= 2 or \
            (phrases == 1 and len(WE_WORDS.findall(body[:3000])) / max(1, min(len(words), 500)) >= 0.02):
        return "newspaper_editorial_historical", "editorial words"
    signals = sum(1 for p in AD_SIGNALS if p.search(body[:1500]))
    if ((AD_HEAD.search(head) or AD_HEAD.search(start[:60])) and signals >= 1) or (signals >= 3 and len(words) < 400):
        return "newspaper_ad_historical", "advertisement words"
    if signals < 2 and looks_like_poem(body):
        return "newspaper_fiction_poetry_historical", "poem"
    return "newspaper_news_historical", "default (news)"


# ====================================================================== making the examples

def join_columns(text, keep_lines=False):
    """The article's text with the line breaks of the newspaper's narrow columns joined into paragraphs (a blank
    line between paragraphs); with keep_lines (poems) every line stays. No word is changed, added or removed."""
    paragraphs = re.split(r"\n\s*\n", str(text).replace("\r", ""))
    out = []
    for p in paragraphs:
        lines = [ln.strip() for ln in p.split("\n") if ln.strip()]
        if lines:
            out.append("\n".join(lines) if keep_lines else " ".join(" ".join(lines).split()))
    return "\n\n".join(out)


def date_words(date):
    """"1870-01-01" -> "1 January 1870" (the date as given when it cannot be read)."""
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(date or ""))
    if not m or not 1 <= int(m.group(2)) <= 12:
        return str(date or "")
    return f"{int(m.group(3))} {months[int(m.group(2)) - 1]} {m.group(1)}"


def instruction_for(style, art, poem=False):
    """The instruction for one article: what to write, for which newspaper and date, with its headline and byline."""
    kind, ask = ASK[style]
    if style == "newspaper_fiction_poetry_historical":
        ask = "Write a poem" if poem else "Write an installment of a serial story"
    paper = art["newspaper"] or "an American newspaper"
    where = f", {art['state']}," if art.get("state") and art["state"] not in paper else ""
    head = " / ".join(" ".join(part.split()) for part in re.split(r"\n\s*\n", art["headline"]) if part.strip())
    text = f"{ask} for {paper}{where} published on {date_words(art['date'])}"
    text += f', headed "{head}"' if head else ""
    byline = " ".join(art["byline"].split())
    text += f" (byline: {byline})" if byline else ""
    return text + f". Write it in the language and style of an American newspaper of the {art['decade']}."


def article_record(art, known=None):
    """The training record (a "text" record build_dataset.py understands) for one article, or None when the
    article has no text at all."""
    if not str(art.get("text") or "").split():
        return None
    style, rule = classify(art["headline"], art["text"])
    poem = rule == "poem"
    response = join_columns(art["text"], keep_lines=poem)
    extra = {"year": art["year"], "decade": art["decade"], "date": art["date"], "newspaper": art["newspaper"],
             "newspaper_title": art["newspaper_title"], "state": art["state"], "lccn": art["lccn"],
             "page": art["page"], "edition": art["edition"], "article_id": art["article_id"],
             "headline": art["headline"], "byline": art["byline"], "ocr_quality": ocr_quality(art["text"], known),
             "legibility": art["legibility"], "style_rule": rule}
    return sources_more.text_record(
        str(art["year"]), style, ASK[style][0], "newspaper article", "period newspaper style", "newspaper readers",
        instruction_for(style, art, poem), response, unchanged=SOURCE_UNCHANGED, extra=extra)


def records_from_stream(stream, limit=None):
    """Records for the articles of one year file (an open binary stream), up to limit records (None: all)."""
    n = 0
    for art in year_articles(stream):
        record = article_record(art)
        if record:
            yield record
            n += 1
            if limit and n >= limit:
                return


def read_american_stories(fetcher, say=print, newspaper_folder="newspapers", newspaper_years="", per_year=50,
                          sample_years=SAMPLE_YEARS, **_):
    """Records for a SAMPLE build (build_dataset.py --sources american_stories_newspapers): up to per_year articles
    from each year file already downloaded in newspaper_folder (by build_newspapers.py), or, when none is there, from
    the start of each of sample_years read straight from Hugging Face (only the first part of each file is
    downloaded, and nothing is saved). The whole corpus is built by build_newspapers.py instead."""
    local = local_year_files(newspaper_folder, newspaper_years)
    if local:
        for year, path in local:
            with open(path, "rb") as f:
                got = 0
                for record in records_from_stream(f, per_year):
                    got += 1
                    yield record
            say(f"  newspapers {year}: {got} articles read from {path}.")
        return
    wanted = parse_years(newspaper_years)
    for year in [y for y in sample_years if wanted(int(y))]:
        url = HF_FILE.format(name=f"faro_{year}.tar.gz")
        try:
            resp = fetcher.open_stream(url)
        except urllib.error.HTTPError as err:
            say(f"  newspapers {year}: not read ({err}).")
            continue
        got = 0
        try:
            for record in records_from_stream(resp, per_year):
                got += 1
                yield record
        finally:
            resp.close()
        say(f"  newspapers {year}: {got} articles from the start of {url}.")


def row_key(row):
    """A short fingerprint of an example (for reports and tests)."""
    return hashlib.sha1(row["response"].encode("utf-8")).hexdigest()[:16]


# ====================================================================== the Source entry and the sources not used

def sources(Source, OPEN, SHARE_ALIKE, PERSONAL):
    """The Source entry for writing_sources.SOURCES (it passes its own Source class and licence classes in)."""
    return [
        Source(key=SOURCE_KEY, name="American Stories: historical US newspaper articles, 1770 to 1964 (Library of "
               "Congress Chronicling America scans, from Hugging Face)", licence=LICENCE, licence_class=OPEN,
               licence_url=CC_BY, credit=CREDIT, home=HF_HOME, reader="read_american_stories",
               notes="180 year files, 340.4 GB in all, downloaded by build_newspapers.py (resumable; years and a "
                     "size cap can be chosen). Article text kept exactly as printed (OCR errors included): not "
                     "scrubbed and nothing left out for OCR quality (the owner's decision); each example records "
                     "its ocr_quality, legibility, year, decade, newspaper and style. Styles chosen by the rules in "
                     "sources_newspapers.py (the dataset has no article-type field). Off in the ordinary build "
                     "unless named in --sources, which reads a small sample. Please cite: " + CITATION.replace("\n", " ")),
    ]


NOT_USED = [
    ("Library of Congress Chronicling America bulk OCR (chroniclingamerica.loc.gov/data/ocr/), for pages American "
     "Stories missed",
     "Public domain and still downloadable (3,064 batch files, about 2.5 TB of .tar.bz2, checked 22 November 2026), "
     "but not built in this round: the site is moving into loc.gov (its robots.txt now redirects to an HTML "
     "collection page and its old ocr.json list answers 404), loc.gov asks for 5 seconds between requests (robots.txt "
     "Crawl-Delay) and blocks for an hour above its published limits (20 API requests or 150 file requests a "
     "minute), and the text is whole-page OCR with no article boundaries. An optional later step: list the batches, "
     "download only those with pages whose <lccn>/<reel>/<issue><edition>/<seq> are not among American Stories' "
     "scan names (scan_info gives the same parts), at most one request every 5 seconds."),
]
