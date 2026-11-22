"""Download and build the whole CourtListener court opinions corpus (US federal and state courts) for the Writing
Kit. The source itself, its licence and its rules are in sources_courts.py; this is the command that runs it,
because the corpus is too big for the ordinary build (63 GB to download, about ten million opinions).

What it does, step by step:
  1. reads the bucket's list of bulk files and picks the newest quarterly export that has all five files the kit
     needs (courts, citations, opinion clusters, dockets, opinions), and says how big they are and how long the
     download takes;
  2. downloads them into court_opinions/<export date>/, smallest first, saying each file's size and the running
     total. It is resumable: stop it whenever you like (close the window) and run it again to carry on where it
     stopped; finished files are checked by their size and never downloaded twice;
  3. makes a small database (index.sqlite in the same folder) that joins each case to its court, date, name,
     docket number and citation, table by table (a finished table is not made again);
  4. reads the opinions file once, from start to end, and writes each opinion into
       out/court_opinions/<court>/<decade>/<year>/<style>-train.jsonl.gz and <style>-validation.jsonl.gz
     (gzip-compressed JSON lines; most training programs read .jsonl.gz directly, and 7-Zip opens them). Every 20,000
     opinions it saves its place (PROGRESS.json), so a stopped build carries on from there: files written after the
     last saved place are cut back to it, and the opinions already done are skipped;
  5. writes out/court_opinions/README.txt, COURT-OPINIONS-REPORT.txt (how many examples per court and style) and
     ATTRIBUTION.txt.

--courts and --years choose which opinions are written (the opinions file is still read whole, because the bulk
data is one file; choosing only saves disk space and time writing).

Usage (from the writing-kit folder):
  python kit/build_court_opinions.py                         (download, make the database, build everything)
  python kit/build_court_opinions.py --list                  (the files, their sizes and what you have)
  python kit/build_court_opinions.py --courts scotus,ca9,cal --years 1950-
  python kit/build_court_opinions.py --download-only         (download now, build later)
  python kit/build_court_opinions.py --build-only            (build from the files already downloaded)
  python kit/build_court_opinions.py --styles court_opinion_dissent,court_opinion_concurrence
"""

import argparse
import collections
import gzip
import json
import os
import shutil
import sqlite3
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_dataset  # noqa: E402
import fetch  # noqa: E402
import sources_courts as sc  # noqa: E402
import sources_newspapers as sn  # noqa: E402  (parse_years, gb, hours_text: the same as for the newspapers)
import styles  # noqa: E402
import writing_sources  # noqa: E402

CHECKPOINT = 20_000                 # opinions between two saved places
OPEN_FILES = 200                    # output files kept open at once (the rest are closed and opened again)
EXAMPLES_GB = 100                   # about how big the finished examples are (written in the guide)
INDEX_GB = 10                       # about how big index.sqlite becomes


# ====================================================================== the local files

def export_folder(folder, date):
    """court_opinions/<export date>."""
    return os.path.join(folder, date)


def local_export(folder):
    """{"date", "folder", "opinions", "index"} of the newest export in folder whose files and database are finished,
    or None."""
    if not os.path.isdir(folder):
        return None
    for date in sorted(os.listdir(folder), reverse=True):
        base = os.path.join(folder, date)
        index = os.path.join(base, "index.sqlite")
        opinions = os.path.join(base, f"opinions-{date}.csv.bz2")
        if os.path.exists(opinions) and os.path.exists(index) and Index(index).finished():
            return {"date": date, "folder": base, "opinions": opinions, "index": index}
    return None


# ====================================================================== the database that joins opinions to cases

class Index:
    """index.sqlite: the courts, dockets, clusters (cases) and citations the opinions need, each table made once."""

    TABLES = {
        "courts": ("CREATE TABLE IF NOT EXISTS courts (id TEXT PRIMARY KEY, full_name TEXT, short_name TEXT, "
                   "jurisdiction TEXT)", "courts", ("id", "full_name", "short_name", "jurisdiction")),
        "dockets": ("CREATE TABLE IF NOT EXISTS dockets (id INTEGER PRIMARY KEY, court_id TEXT, docket_number TEXT, "
                    "case_name TEXT)", "dockets", ("id", "court_id", "docket_number", "case_name")),
        "clusters": ("CREATE TABLE IF NOT EXISTS clusters (id INTEGER PRIMARY KEY, docket_id INTEGER, date_filed "
                     "TEXT, case_name TEXT, precedential_status TEXT)", "opinion-clusters",
                     ("id", "docket_id", "date_filed", "case_name", "precedential_status")),
        "citations": ("CREATE TABLE IF NOT EXISTS citations (cluster_id INTEGER, cite TEXT)", "citations",
                      ("cluster_id", "volume", "reporter", "page")),
    }

    def __init__(self, path):
        self.path = path
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS done (name TEXT PRIMARY KEY)")

    def finished(self):
        """True when every table has been made."""
        done = {r[0] for r in self.db.execute("SELECT name FROM done")}
        return set(self.TABLES) <= done

    def make(self, paths, say=print, report_every=2_000_000):
        """Make each table not made yet from its bulk file (paths: {table name of the bulk data: file path})."""
        done = {r[0] for r in self.db.execute("SELECT name FROM done")}
        for name, (create, table, fields) in self.TABLES.items():
            if name in done:
                continue
            say(f"Making the {name} table from {os.path.basename(paths[table])} ...")
            self.db.execute(f"DROP TABLE IF EXISTS {name}")
            self.db.execute(create)
            n, batch = 0, []
            with open(paths[table], "rb") as f:
                for row in sc.csv_rows(f):
                    if name == "citations":
                        values = (row.get("cluster_id"), " ".join(x for x in (row.get("volume"), row.get("reporter"),
                                                                              row.get("page")) if x))
                    else:
                        values = tuple(row.get(k, "") for k in fields)
                    batch.append(values)
                    n += 1
                    if len(batch) >= 50_000:
                        self._insert(name, batch)
                        batch = []
                    if n % report_every == 0:
                        say(f"  {name}: {n:,} rows so far")
            if batch:
                self._insert(name, batch)
            if name == "citations":
                self.db.execute("CREATE INDEX IF NOT EXISTS citations_cluster ON citations (cluster_id)")
            self.db.execute("INSERT OR REPLACE INTO done VALUES (?)", (name,))
            self.db.commit()
            say(f"  {name}: {n:,} rows.")

    def _insert(self, name, batch):
        marks = ",".join("?" * len(batch[0]))
        verb = "INSERT INTO" if name == "citations" else "INSERT OR REPLACE INTO"
        self.db.executemany(f"{verb} {name} VALUES ({marks})", batch)

    def case(self, cluster_id):
        """The case details of one cluster (court, court_name, court_type, case_name, date_filed, docket_number,
        citation, precedential_status); {} when the cluster is unknown."""
        try:
            cid = int(cluster_id)
        except (TypeError, ValueError):
            return {}
        row = self.db.execute(
            "SELECT c.date_filed, c.case_name, c.precedential_status, d.court_id, d.docket_number, d.case_name, "
            "ct.full_name, ct.jurisdiction FROM clusters c LEFT JOIN dockets d ON d.id = c.docket_id "
            "LEFT JOIN courts ct ON ct.id = d.court_id WHERE c.id = ?", (cid,)).fetchone()
        if not row:
            return {}
        cites = [r[0] for r in self.db.execute("SELECT cite FROM citations WHERE cluster_id = ? LIMIT 3", (cid,))
                 if r[0]]
        return {"date_filed": row[0] or "", "case_name": row[1] or row[5] or "", "precedential_status": row[2] or "",
                "court": row[3] or "", "docket_number": row[4] or "", "court_name": row[6] or "",
                "court_type": row[7] or "", "citation": "; ".join(cites)}


# ====================================================================== writing the examples, with saved places

class Writer:
    """The output files of the build: a few hundred open at once (the oldest closed and opened again for adding),
    each a gzip file of JSON lines. A gzip file opened again for adding gets a new part, which every gzip reader
    reads as one file."""

    def __init__(self, base):
        self.base = base
        self.open = collections.OrderedDict()

    def write(self, rel, line):
        f = self.open.pop(rel, None)
        if f is None:
            path = os.path.join(self.base, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            f = gzip.open(path, "at", encoding="utf-8")
            while len(self.open) >= OPEN_FILES:
                self.open.popitem(last=False)[1].close()
        self.open[rel] = f
        f.write(line)

    def close(self):
        for f in self.open.values():
            f.close()
        self.open.clear()

    def sizes(self):
        """{relative path: size} of every output file under base (after close())."""
        out = {}
        for root, _dirs, files in os.walk(self.base):
            for name in files:
                if name.endswith(".jsonl.gz"):
                    path = os.path.join(root, name)
                    out[os.path.relpath(path, self.base)] = os.path.getsize(path)
        return out


def restore(base, sizes):
    """Cut every output file back to its size at the last saved place, and delete those made after it."""
    for root, _dirs, files in os.walk(base):
        for name in files:
            if not name.endswith(".jsonl.gz"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, base)
            if rel not in sizes:
                os.remove(path)
            elif os.path.getsize(path) != sizes[rel]:
                with open(path, "r+b") as f:
                    f.truncate(sizes[rel])


def rel_path(row):
    """The file of one example: <court>/<decade>/<year>/<style>-<train or validation>.jsonl.gz."""
    court = row.get("court") or "unknown_court"
    year = row.get("year") or 0
    part = "validation" if build_dataset.is_validation(row) else "train"
    when = os.path.join(f"{year // 10 * 10}s", str(year)) if year else os.path.join("unknown_decade", "unknown_year")
    return os.path.join(court, when, f"{row['style']}-{part}.jsonl.gz")


def build(opinions_path, index, out, courts=(), years="", wanted_styles=(), privacy=build_dataset.OWNER,
          rebuild=False, say=print, checkpoint=CHECKPOINT):
    """Build every opinion of the opinions file into out/court_opinions (see the module notes); returns the counts.
    Resumes from PROGRESS.json unless rebuild."""
    base = os.path.join(out, "court_opinions")
    done_file, progress_file = os.path.join(base, "DONE.json"), os.path.join(base, "PROGRESS.json")
    settings = {"opinions": os.path.basename(opinions_path), "courts": sorted(courts), "years": years,
                "styles": sorted(wanted_styles), "privacy": privacy}
    if os.path.exists(done_file) and not rebuild:
        with open(done_file, encoding="utf-8") as f:
            done = json.load(f)
        if done.get("settings") == settings:
            say("The court opinions were built before with these choices; add --rebuild to build them again.")
            return Counter(done["counts"])
    progress = {}
    if rebuild:
        shutil.rmtree(base, ignore_errors=True)
    elif os.path.exists(progress_file):
        with open(progress_file, encoding="utf-8") as f:
            progress = json.load(f)
        if progress.get("settings") != settings:
            say("The choices differ from the stopped build's, so it starts again from the beginning.")
            shutil.rmtree(base, ignore_errors=True)
            progress = {}
    os.makedirs(base, exist_ok=True)
    restore(base, progress.get("sizes", {}))
    skip = progress.get("rows", 0)
    counts = Counter(progress.get("counts", {}))
    if skip:
        say(f"Carrying on after {skip:,} opinions (they are read again but not written).")
    wanted_year = sn.parse_years(years)
    source = writing_sources.by_key()[sc.SOURCE_KEY]
    writer, n = Writer(base), 0
    started = time.time()

    def save_place():
        writer.close()
        with open(progress_file + ".part", "w", encoding="utf-8") as f:
            json.dump({"settings": settings, "rows": n, "counts": counts, "sizes": writer.sizes()}, f)
        os.replace(progress_file + ".part", progress_file)

    with open(opinions_path, "rb") as stream:
        for row in sc.csv_rows(stream):
            n += 1
            if n <= skip:
                continue
            info = index.case(row.get("cluster_id"))
            year = int(info["date_filed"][:4]) if str(info.get("date_filed", ""))[:4].isdigit() else 0
            if courts and info.get("court", "").lower() not in courts:
                counts["not one of the chosen courts"] += 1
            elif years and not (year and wanted_year(year)):
                counts["not one of the chosen years"] += 1
            else:
                record = sc.opinion_record(row, info)
                if record is None:
                    counts["no text"] += 1
                else:
                    counts["opinions"] += 1
                    for example, _reason in build_dataset.examples_from_record(record, source, privacy):
                        if example is None:
                            continue
                        example["style"], example["register"] = styles.label(example, source.key, record)
                        if wanted_styles and example["style"] not in wanted_styles:
                            counts["not one of the chosen styles"] += 1
                            continue
                        writer.write(rel_path(example), json.dumps(example, ensure_ascii=False) + "\n")
                        counts[f"court {example.get('court') or 'unknown_court'}"] += 1
                        counts[f"style {example['style']}"] += 1
                        counts["examples"] += 1
            if n % checkpoint == 0:
                save_place()
                rate = (n - skip) / max(1.0, time.time() - started)
                say(f"  {n:,} opinions read, {counts['examples']:,} examples written ({rate:,.0f} a second).")
    save_place()
    with open(done_file, "w", encoding="utf-8") as f:
        json.dump({"settings": settings, "counts": counts, "rows": n}, f, indent=1)
    os.remove(progress_file)
    return counts


README = """US court opinions (CourtListener, Free Law Project), built by the Writing Kit.

One folder per court (CourtListener's court ids: scotus is the Supreme Court of the United States, ca1 to ca11 and
cadc the federal courts of appeals, cal the Supreme Court of California, and so on), in it one folder per decade and
one per year. In each year folder, every style has two files:
  <style>-train.jsonl.gz        the training examples, one per line (gzip-compressed JSON lines)
  <style>-validation.jsonl.gz   about one example in twenty, kept back to check the training
Most training programs read .jsonl.gz directly; 7-Zip opens them. To train on one court, use its folder; on one
style, the files of that style.

Each example has the kit's usual fields (instruction, response, messages, style, register, source, licence, credit)
and also: court, court_name, court_type, year, decade, date_filed, case_name, docket_number, citation,
opinion_type (CourtListener's own type), author, per_curiam, precedential_status, word_count, text_from (which
version of the text was used), style_rule, cluster_id and opinion_id.

The text is the opinion's whole text. Under the owner's rule only Social Security, card, bank and account numbers
and passwords are masked; nothing else is changed. Some opinions are very long: word_count lets training choose.

The styles:
"""


def write_summary(out, counts, date, say=print):
    """README.txt, COURT-OPINIONS-REPORT.txt and ATTRIBUTION.txt in out/court_opinions."""
    base = os.path.join(out, "court_opinions")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "README.txt"), "w", encoding="utf-8") as f:
        f.write(README + "".join(f"  {k}: {v}.\n" for k, v in sc.STYLES.items()))
    with open(os.path.join(base, "COURT-OPINIONS-REPORT.txt"), "w", encoding="utf-8") as f:
        f.write(f"CourtListener court opinions build, {time.strftime('%Y-%m-%d %H:%M')}, export of {date}.\n\n")
        f.write(f"Opinions written: {counts['opinions']:,}. Examples: {counts['examples']:,}. Without text: "
                f"{counts['no text']:,}.\n")
        for reason in ("not one of the chosen courts", "not one of the chosen years", "not one of the chosen styles"):
            if counts[reason]:
                f.write(f"{reason}: {counts[reason]:,}\n")
        f.write("\nBy style:\n")
        for style in sc.STYLES:
            f.write(f"  {style}: {counts['style ' + style]:,}\n")
        f.write("\nBy court (most first):\n")
        courts = sorted(((k[6:], v) for k, v in counts.items() if k.startswith("court ")), key=lambda x: -x[1])
        for court, n in courts:
            f.write(f"  {court}: {n:,}\n")
    with open(os.path.join(base, "ATTRIBUTION.txt"), "w", encoding="utf-8") as f:
        f.write(f"Credit: {sc.CREDIT}.\nLicence: {sc.LICENCE} ({sc.LICENCE_URL}).\nWhere: {sc.HELP_PAGE}\n"
                f"Files: {sc.LIST_PAGE} (export of {date})\n"
                "Changes: HTML and XML versions made into plain text; Social Security, card, bank and account numbers "
                "and passwords masked; instructions written by rules; styles from CourtListener's opinion types.\n")
    say(f"Summary written in {base}.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download and build the CourtListener court opinions corpus.")
    parser.add_argument("--folder", default="court_opinions", help="where the bulk files and the database are kept")
    parser.add_argument("--out", default="out", help="the output folder (the examples go into out/court_opinions)")
    parser.add_argument("--courts", default="", help="only these courts, by CourtListener id, separated by commas, "
                                                     "for example scotus,ca9,cal (default: every court)")
    parser.add_argument("--years", default="", help="only these years, for example 1950-1999,2010s (default: all)")
    parser.add_argument("--styles", default="", help="build only these styles, separated by commas")
    parser.add_argument("--list", action="store_true", help="only list the files, their sizes and what you have")
    parser.add_argument("--download-only", action="store_true", help="download, do not build")
    parser.add_argument("--build-only", action="store_true", help="build from the files already downloaded")
    parser.add_argument("--rebuild", action="store_true", help="build again from the beginning")
    parser.add_argument("--privacy", choices=[build_dataset.OWNER, build_dataset.STRICT], default=build_dataset.OWNER,
                        help="owner (the default): mask only Social Security, card, bank and account numbers and "
                             "passwords; strict: also replace names and personal details")
    args = parser.parse_args(argv)
    say = lambda text: print(text, flush=True)
    wanted = {x.strip() for x in args.styles.split(",") if x.strip()}
    if wanted - set(sc.STYLES):
        parser.error("unknown style: " + ", ".join(sorted(wanted - set(sc.STYLES))) + ". Known: " + ", ".join(sc.STYLES))
    try:
        sn.parse_years(args.years)
    except ValueError as err:
        parser.error(str(err))

    if args.build_only:
        local = None
        if os.path.isdir(args.folder):
            for date in sorted(os.listdir(args.folder), reverse=True):
                base = export_folder(args.folder, date)
                names = {t: os.path.join(base, f"{t}-{date}.csv.bz2") for t in sc.TABLES}
                if all(os.path.exists(p) for p in names.values()):
                    local = (date, names)
                    break
        if not local:
            say(f"No complete set of files in {os.path.abspath(args.folder)}. Run without --build-only first.")
            return 1
        date, paths = local
    else:
        fetcher = fetch.Fetcher(say)
        say("Reading the list of bulk files from CourtListener's storage.")
        date, files = sc.latest_complete(sc.bucket_files(sc.list_bucket(fetcher)))
        if not files:
            say("No complete bulk export was found. Try again later.")
            return 1
        base = export_folder(args.folder, date)
        paths = {f["table"]: os.path.join(base, f["name"]) for f in files}
        total = sum(f["size"] for f in files)
        have = sum(f["size"] for f in files if os.path.exists(paths[f["table"]])
                   and os.path.getsize(paths[f["table"]]) == f["size"])
        if args.list:
            for f in files:
                path = paths[f["table"]]
                state = "downloaded" if os.path.exists(path) and os.path.getsize(path) == f["size"] else \
                    ("partly downloaded" if os.path.exists(path + ".part") else "not downloaded")
                say(f"{f['name']}: {sn.gb(f['size'])}, {state}.")
            say(f"All five files: {sn.gb(total)} (export of {date}).")
            return 0
        say(f"Export of {date}: five files, {sn.gb(total)} ({sn.gb(have)} of it downloaded already).")
        rest = total - have
        if rest:
            say(f"Still to download: {sn.gb(rest)}. That takes {sn.hours_text(rest, 100)} at 100 megabits a second, "
                f"or {sn.hours_text(rest, 25)} at 25 megabits a second. Close the window to stop; run again to resume.")
        os.makedirs(base, exist_ok=True)
        done_bytes = 0
        for n, f in enumerate(files, 1):
            path = paths[f["table"]]
            if not (os.path.exists(path) and os.path.getsize(path) == f["size"]):
                part = os.path.getsize(path + ".part") if os.path.exists(path + ".part") else 0
                free = shutil.disk_usage(base).free
                if f["size"] - part > free:
                    say(f"STOPPED before {f['name']}: it needs {sn.gb(f['size'] - part)} and only {sn.gb(free)} is "
                        "free on that disk. Free some space, then run again.")
                    return 1
            say(f"{f['name']}: {sn.gb(f['size'])} (file {n} of {len(files)}; {sn.gb(done_bytes)} of {sn.gb(total)} "
                "done before it).")
            try:
                how = fetcher.download(f["url"], path, size=f["size"], say=say)
            except (OSError, ValueError) as err:
                say(f"  {f['name']}: not finished ({err}). Run again later to resume.")
                return 1
            done_bytes += f["size"]
            say(f"  {'already downloaded' if how == 'already' else 'downloaded'}. Running total {sn.gb(done_bytes)} "
                f"of {sn.gb(total)}.")
        if args.download_only:
            say("Done downloading.")
            return 0
    base = export_folder(args.folder, date)
    index = Index(os.path.join(base, "index.sqlite"))
    if not index.finished():
        say(f"Making the database that joins opinions to their courts and cases (about {INDEX_GB} GB, an hour or "
            "two). It is kept, and a finished table is never made again.")
        index.make(paths, say)
    say(f"Building the examples into {os.path.abspath(args.out)}{os.sep}court_opinions. The opinions file is read "
        "once from start to end; this takes many hours (about a day for everything). Close the window to stop; run "
        "again to carry on.")
    counts = build(paths["opinions"], index, args.out, sc.parse_filter(args.courts), args.years, wanted,
                   args.privacy, args.rebuild, say)
    write_summary(args.out, counts, date, say)
    say(f"Done: {counts['examples']:,} examples from {counts['opinions']:,} opinions. Read COURT-OPINIONS-REPORT.txt "
        "in out\\court_opinions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
