"""US court opinions for the Writing Kit (added on 22 November 2026 at the owner's request): the whole opinions
corpus of CourtListener (Free Law Project), kept in this one file so it is easy to merge with other work on the kit.
writing_sources.py adds SOURCES and NOT_USED from here, styles.py adds the style labels, build_dataset.py reads a
small sample with read_court_opinions, and build_court_opinions.py downloads and builds the whole corpus.

The source, key courtlistener_opinions
  CourtListener's bulk data: every table of its database as a CSV file compressed with bzip2, made again every
  quarter (the last day of March, June, September and December) and kept in a public Amazon S3 bucket
  (com-courtlistener-storage, folder bulk-data/), listed at
  https://com-courtlistener-storage.s3-us-west-2.amazonaws.com/list.html?prefix=bulk-data/ . Its help page
  (wiki.free.law, "Bulk Legal Data", read 22 November 2026) says: "Our bulk data files are free of known copyright
  restrictions" with the Creative Commons Public Domain Mark; US court opinions are public records. The bucket has no
  robots.txt (no rules); courtlistener.com's own robots.txt shuts programs out of the website and points them to the
  bulk data and the API instead, so the kit never reads the website. No key is needed for the bulk files.
  The old per-court and per-year files were removed by Free Law Project in 2023 (GitHub issue 285); now the opinions
  are ONE file. On 2026-09-30 the files the kit needs were:
      courts            0.001 GB   the courts (name, kind of court)
      citations         0.13 GB    the reporter citations of each case ("347 U.S. 483")
      opinion-clusters  2.47 GB    each case (its name, date, judges and status), grouping its opinions
      dockets           5.14 GB    each case's docket (its court and docket number)
      opinions          55.25 GB   every opinion's text, with its type (majority, concurrence, dissent ...)
  63 GB in all. The opinions do not name their court or date: the kit joins them to the clusters, dockets and courts
  through a small database it makes on the owner's computer (an SQLite file, index.sqlite), then reads the opinions
  file once, from start to end, and writes each opinion under its court and year.

What the kit makes of each opinion
  One training example: the instruction asks for that kind of opinion, for that court, case, citation and date (and
  the judge who wrote it, when the data says); the answer is the opinion's whole text. The text is the plain text
  when there is one, otherwise the opinion's HTML or XML with its tags taken out. Privacy: court opinions are public
  records, but modern ones can quote Social Security, card, bank and account numbers or passwords, so they go
  through the kit's usual scrub (build_dataset.protect: under the owner's rule only those numbers and passwords are
  masked; nothing else is changed). Each example also carries: court, court_name, court_type, year, decade,
  date_filed, case_name, docket_number, citation, opinion_type, author, per_curiam, precedential_status, word_count,
  cluster_id and opinion_id.

The styles (from the opinion's "type" field, set by CourtListener; nothing is guessed):
  court_opinion_majority      "020lead" (the lead or majority opinion), "015unamimous" (spelled so in the data),
                              "025plurality", and per curiam opinions
  court_opinion_concurrence   "030concurrence" and "035concurrenceinpart" (concurring in part and dissenting in part)
  court_opinion_dissent       "040dissent"
  court_opinion_combined      "010combined": the court's opinions printed together as one text (most older cases
                              and most state cases), so a majority with any concurrences and dissents in one answer
  court_opinion_other         "050addendum", "060remittitur", "070rehearing", "080onthemerits",
                              "090onmotiontostrike", "100trialcourt" and anything else
"""

import bz2
import csv
import datetime
import html
import io
import re
import sys
import urllib.parse

import sources_more

SOURCE_KEY = "courtlistener_opinions"
BUCKET = "https://com-courtlistener-storage.s3-us-west-2.amazonaws.com"
LIST_PAGE = f"{BUCKET}/list.html?prefix=bulk-data/"
HELP_PAGE = "https://wiki.free.law/c/courtlistener/help/api/bulk-data/bulk-legal-data"
LICENCE = "Public domain (CourtListener bulk data: \"free of known copyright restrictions\", Public Domain Mark)"
LICENCE_URL = "https://creativecommons.org/publicdomain/mark/1.0/"
CREDIT = ("CourtListener bulk data, Free Law Project (free.law); court opinions are public records of US federal and "
          "state courts")
# The tables the kit needs, in the order they are downloaded (smallest first, the opinions last).
TABLES = ("courts", "citations", "opinion-clusters", "dockets", "opinions")
FULL_SIZE_GB = 63.0                     # the five files of 2026-09-30
FILE_NAME = re.compile(r"^bulk-data/(?P<table>[a-z-]+)-(?P<date>\d{4}-\d{2}-\d{2})\.csv\.bz2$")

# Off in the ordinary build unless named in --sources (the corpus is 63 GB: build_court_opinions.py builds it).
OPT_IN = {SOURCE_KEY}

STYLES = {
    "court_opinion_majority": "court opinion (majority, lead, unanimous, plurality or per curiam)",
    "court_opinion_concurrence": "court opinion (concurrence)",
    "court_opinion_dissent": "court opinion (dissent)",
    "court_opinion_combined": "court opinions printed together as one text (majority with any concurrences and "
                              "dissents)",
    "court_opinion_other": "court opinion (addendum, remittitur, rehearing, trial court and other)",
}
FORMAL = set(STYLES)
CASUAL = set()

TYPE_STYLE = {"015unamimous": "court_opinion_majority", "020lead": "court_opinion_majority",
              "025plurality": "court_opinion_majority", "030concurrence": "court_opinion_concurrence",
              "035concurrenceinpart": "court_opinion_concurrence", "040dissent": "court_opinion_dissent",
              "010combined": "court_opinion_combined"}
TYPE_WORDS = {"010combined": "the opinion", "015unamimous": "the unanimous opinion", "020lead": "the majority opinion",
              "025plurality": "the plurality opinion", "030concurrence": "a concurring opinion",
              "035concurrenceinpart": "an opinion concurring in part and dissenting in part",
              "040dissent": "a dissenting opinion", "050addendum": "an addendum", "060remittitur": "a remittitur",
              "070rehearing": "the opinion on rehearing", "080onthemerits": "the opinion on the merits",
              "090onmotiontostrike": "the opinion on a motion to strike", "100trialcourt": "the trial court's opinion"}
COURT_TYPES = {"F": "federal court of appeals", "FD": "federal district court", "FB": "federal bankruptcy court",
               "FBP": "federal bankruptcy appellate panel", "FS": "federal special court", "S": "state supreme court",
               "SA": "state appellate court", "ST": "state trial court", "SS": "state special court",
               "SAG": "state attorney general", "TRS": "tribal supreme court", "TRA": "tribal appellate court",
               "TRT": "tribal trial court", "TRX": "tribal special court", "TS": "territorial supreme court",
               "TA": "territorial appellate court", "TT": "territorial trial court", "TSP": "territorial special court",
               "MA": "military appeals court", "MT": "military trial court", "C": "committee", "I": "international",
               "T": "testing"}


def style_for(opinion_type, per_curiam=False):
    """(style, rule) of one opinion from CourtListener's own type field (see the module notes)."""
    t = str(opinion_type or "").strip()
    if per_curiam and t in ("", "010combined", "020lead"):
        return "court_opinion_majority", f"type {t or 'not given'}, per curiam"
    return TYPE_STYLE.get(t, "court_opinion_other"), f"type {t or 'not given'}"


# ====================================================================== the bulk files and choosing what to download

def bucket_files(listing_pages):
    """{date: {table: {"name", "size", "url"}}} from the S3 bucket's XML listings (one or more pages of text)."""
    out = {}
    for page in listing_pages:
        for key, size in re.findall(r"<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>", page, re.S):
            m = FILE_NAME.match(key)
            if m and m.group("table") in TABLES:
                out.setdefault(m.group("date"), {})[m.group("table")] = {
                    "name": key.rsplit("/", 1)[1], "size": int(size), "url": f"{BUCKET}/{urllib.parse.quote(key)}"}
    return out


def latest_complete(files):
    """(date, [file dicts in TABLES order]) of the newest export that has all five tables (a quarter's files appear
    over several hours; a half-finished one is skipped)."""
    for date in sorted(files, reverse=True):
        if all(t in files[date] and files[date][t]["size"] > 100 for t in TABLES):
            return date, [dict(files[date][t], table=t) for t in TABLES]
    return "", []


def list_bucket(fetcher):
    """The pages of the bucket's listing of bulk-data/ (the S3 interface, 1,000 names a page)."""
    pages, marker = [], ""
    while True:
        url = f"{BUCKET}/?prefix=bulk-data/" + (f"&marker={urllib.parse.quote(marker)}" if marker else "")
        page = fetcher.get(url).decode("utf-8", "replace")
        pages.append(page)
        if "<IsTruncated>true</IsTruncated>" not in page:
            return pages
        found = re.findall(r"<Key>([^<]+)</Key>", page)
        marker = (re.search(r"<NextMarker>([^<]+)</NextMarker>", page) or [None, found[-1] if found else ""])[1]
        if not marker:
            return pages


def parse_filter(text):
    """A set of lowercase court ids from what the owner types ("scotus, ca9, cal"); empty means every court."""
    return {c.strip().lower() for c in str(text or "").split(",") if c.strip()}


# ====================================================================== reading the CSV files

def csv_rows(stream):
    """Dicts for the rows of one bulk CSV (an open binary stream of the .csv.bz2 file, read as it arrives).
    CourtListener writes them with PostgreSQL's COPY: every value in double quotes, a backslash before a quote or
    backslash inside a value, and NULL as nothing at all."""
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    text = io.TextIOWrapper(bz2.BZ2File(stream) if not isinstance(stream, bz2.BZ2File) else stream,
                            encoding="utf-8", errors="replace", newline="")
    reader = csv.reader(text, escapechar="\\", doublequote=False)
    head = next(reader, None)
    if not head:
        return
    for row in reader:
        if len(row) == len(head):
            yield dict(zip(head, row))


TEXT_FIELDS = ("plain_text", "html_with_citations", "html", "html_lawbox", "html_columbia", "html_anon_2020",
               "xml_harvard")


def html_to_text(markup):
    """Plain text from an opinion's HTML or XML: block tags become paragraph breaks, other tags are taken out, and
    entities are read. No word is changed."""
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", markup or "")
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</?(p|div|blockquote|h[1-6]|li|tr|section|opinion|parties|docketnumber|court|decisiondate|"
                  r"attorneys|author|headnotes|summary|syllabus|footnote|center|pre)\b[^>]*>", "\n\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    lines = [" ".join(line.split()) for line in text.replace("\r", "").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def opinion_text(row):
    """(text, which field) of one opinion row: the plain text when there is one, else the first HTML or XML version
    with its tags taken out; ("", "") when it has no text."""
    for name in TEXT_FIELDS:
        value = row.get(name) or ""
        if value.strip():
            text = value.strip() if name == "plain_text" else html_to_text(value)
            if text.split():
                return text, name
    return "", ""


# ====================================================================== making the examples

def date_words(iso):
    """"1954-05-17" -> "17 May 1954" (the text as given when it is not a date)."""
    try:
        d = datetime.date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso or "")
    return f"{d.day} {d.strftime('%B')} {d.year}"


def instruction_for(info, opinion_type, author="", per_curiam=False):
    """The instruction for one opinion: what kind, for which court, case, citation and date, and by whom."""
    what = TYPE_WORDS.get(opinion_type, "an opinion")
    court = info.get("court_name") or "an American court"
    case = info.get("case_name") or "a case"
    cite = f" ({info['citation']})" if info.get("citation") else ""
    when = f", decided {date_words(info['date_filed'])}" if info.get("date_filed") else ""
    text = f"Write {what} of the {court} in {case}{cite}{when}" if info.get("court_name") else \
        f"Write {what} of {court} in {case}{cite}{when}"
    if per_curiam:
        text += ", issued per curiam (by the court as a whole)"
    elif author:
        text += f", written by {author}"
    if info.get("docket_number"):
        text += f" (docket number {info['docket_number']})"
    return text + ". Write it in the formal style of an American judicial opinion."


def opinion_record(row, info):
    """The training record (a "text" record build_dataset.py understands) for one opinion row and its case's
    details (info: court, court_name, court_type, case_name, date_filed, docket_number, citation,
    precedential_status), or None when the opinion has no text."""
    text, field = opinion_text(row)
    if not text:
        return None
    per_curiam = str(row.get("per_curiam") or "").lower() in ("t", "true", "1")
    opinion_type = str(row.get("type") or "").strip()
    style, rule = style_for(opinion_type, per_curiam)
    author = " ".join(str(row.get("author_str") or "").split())
    year = int(info["date_filed"][:4]) if str(info.get("date_filed", ""))[:4].isdigit() else 0
    extra = {"court": info.get("court", ""), "court_name": info.get("court_name", ""),
             "court_type": COURT_TYPES.get(info.get("court_type", ""), info.get("court_type", "")),
             "year": year, "decade": f"{year // 10 * 10}s" if year else "", "date_filed": info.get("date_filed", ""),
             "case_name": info.get("case_name", ""), "docket_number": info.get("docket_number", ""),
             "citation": info.get("citation", ""), "opinion_type": opinion_type, "author": author,
             "per_curiam": per_curiam, "precedential_status": info.get("precedential_status", ""),
             "word_count": len(text.split()), "text_from": field, "style_rule": rule,
             "cluster_id": row.get("cluster_id", ""), "opinion_id": row.get("id", "")}
    return sources_more.text_record(
        info.get("court", "") or "court", style, TYPE_WORDS.get(opinion_type, "an opinion"), "court opinion",
        "formal judicial style", "the parties, lawyers and the public",
        instruction_for(info, opinion_type, author, per_curiam), text, extra=extra)


# ====================================================================== the sample read by the ordinary build

def read_court_opinions(fetcher, say=print, court_folder="court_opinions", per_source=300, sample_rows=60, **_):
    """Records for a SAMPLE build (build_dataset.py --sources courtlistener_opinions): when build_court_opinions.py
    has made its database, the first opinions of the downloaded opinions file with their courts and cases;
    otherwise the start of the newest opinions file read straight from the bucket (only its first part is
    downloaded, nothing is saved), without court or case details. The whole corpus is built by
    build_court_opinions.py instead."""
    import build_court_opinions as bco
    local = bco.local_export(court_folder)
    if local:
        index = bco.Index(local["index"])
        got = 0
        with open(local["opinions"], "rb") as f:
            for row in csv_rows(f):
                record = opinion_record(row, index.case(row.get("cluster_id")))
                if record:
                    got += 1
                    yield record
                    if got >= min(per_source, sample_rows):
                        break
        say(f"  court opinions: {got} read from {local['opinions']}.")
        return
    date, files = latest_complete(bucket_files(list_bucket(fetcher)))
    if not files:
        say("  court opinions: no complete bulk export found in the bucket.")
        return
    opinions = files[-1]
    resp = fetcher.open_stream(opinions["url"])
    got = 0
    try:
        for row in csv_rows(resp):
            record = opinion_record(row, {})
            if record:
                got += 1
                yield record
                if got >= min(per_source, sample_rows):
                    break
    finally:
        resp.close()
    say(f"  court opinions: {got} from the start of {opinions['url']} (export of {date}; courts and cases are named "
        "only after build_court_opinions.py has downloaded the files).")


# ====================================================================== the Source entry and the sources not used

def sources(Source, OPEN, SHARE_ALIKE, PERSONAL):
    """The Source entry for writing_sources.SOURCES (it passes its own Source class and licence classes in)."""
    return [
        Source(key=SOURCE_KEY, name="CourtListener court opinions: US federal and state courts (Free Law Project bulk "
               "data)", licence=LICENCE, licence_class=OPEN, licence_url=LICENCE_URL, credit=CREDIT, home=HELP_PAGE,
               reader="read_court_opinions",
               notes="Five bulk files, 63 GB in all (2026-09-30 export), downloaded by build_court_opinions.py "
                     "(resumable); the opinions are joined to their courts and cases in a local database and written "
                     "by court and year. Styles from CourtListener's own opinion type (majority, concurrence, "
                     "dissent, combined, other). Scrubbed by the owner's rule (only Social Security, card, bank and "
                     "account numbers and passwords masked). Off in the ordinary build unless named in --sources, "
                     "which reads a small sample."),
    ]


NOT_USED = [
    ("CourtListener's website and REST API (courtlistener.com)",
     "Its robots.txt disallows every program except search engines and shuts out AI companies' crawlers, and its "
     "API needs a token and is meant for lookups, not the whole corpus; the robots.txt itself points programs to the "
     "bulk data, which the kit uses (courtlistener_opinions)."),
    ("Caselaw Access Project (Harvard Law School Library) downloads (static.case.law)",
     "Public domain case law by reporter and volume, but static.case.law's robots.txt disallows every program. Its "
     "cases are also in CourtListener's data."),
    ("COLD Cases (Harvard Library Innovation Lab, Hugging Face harvard-lil/cold-cases)",
     "CC0, CourtListener's opinions regrouped one decision a record (32 GB of Parquet files, 2024 snapshot), but "
     "reading Parquet needs the pyarrow library, which the kit does not install; CourtListener's own CSV files are "
     "newer and need nothing extra."),
]
