"""Download and build the whole American Stories newspaper corpus (historical US newspapers, 1770 to 1964) for the
Writing Kit. The source itself, its licence and its rules are in sources_newspapers.py; this is the command that
runs it, because the corpus is too big for the ordinary build (340 GB to download, a few hundred million articles).

What it does, step by step:
  1. reads the list of year files from Hugging Face (their sizes and checksums) and says how many years were chosen,
     how big they are and how long the download takes;
  2. downloads the chosen year files into the newspapers folder, one after another, saying each file's size and the
     running total. It is resumable: stop it whenever you like (close the window) and run it again to carry on
     where it stopped; finished files are checked against their checksums and never downloaded twice;
  3. builds the training examples year by year, several years at once (--workers), into
       out/newspapers/<decade>/<year>/<style>-train.jsonl.gz and <style>-validation.jsonl.gz
     (gzip-compressed JSON lines: one example per line, the same fields as the kit's train.jsonl plus the
     newspaper's details; most training programs read .jsonl.gz directly, and 7-Zip opens them). A finished year has
     a file DONE.txt and is skipped next time (--rebuild builds it again), so the build can be stopped and resumed too;
  4. writes out/newspapers/README.txt, NEWSPAPERS-REPORT.txt (how many examples per decade and style) and
     ATTRIBUTION.txt (the credit, licence and citation).

Every article with any text is kept exactly as printed: nothing is scrubbed, nothing is left out for OCR quality and
repeats (articles reprinted by many papers) are kept (the owner's decision of 22 November 2026).

Usage (from the writing-kit folder):
  python kit/build_newspapers.py                          (every year: download, then build)
  python kit/build_newspapers.py --list                   (each year's size, and what is downloaded already)
  python kit/build_newspapers.py --years 1850-1869,1900s --max-gb 60
  python kit/build_newspapers.py --download-only          (download now, build later)
  python kit/build_newspapers.py --build-only             (build from the files already downloaded; no network)
  python kit/build_newspapers.py --styles newspaper_editorial_historical,newspaper_letter_historical
"""

import argparse
import gzip
import json
import os
import shutil
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_dataset  # noqa: E402
import fetch  # noqa: E402
import sources_newspapers as sn  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402


def year_folder(out, year):
    """out/newspapers/<decade>/<year>."""
    return os.path.join(out, "newspapers", f"{int(year) // 10 * 10}s", str(year))


def build_year(year, path, out, wanted_styles=(), rebuild=False, say=print, report_every=200_000):
    """Build one year file into its own folder (see the module notes). Returns the year's counts (a dict), read back
    from DONE.txt when the year was finished before."""
    folder = year_folder(out, year)
    done = os.path.join(folder, "DONE.txt")
    if os.path.exists(done) and not rebuild:
        with open(done, encoding="utf-8") as f:
            return json.load(f)
    work = folder + ".part"
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    source = writing_sources.by_key()[sn.SOURCE_KEY]
    files, counts = {}, Counter()
    try:
        with open(path, "rb") as stream:
            for record in sn.records_from_stream(stream):
                counts["articles"] += 1
                # privacy is irrelevant here: the records are "unchanged", so build_dataset never scrubs them
                for row, _ in build_dataset.examples_from_record(record, source):
                    row["style"], row["register"] = styles.label(row, source.key, record)
                    if wanted_styles and row["style"] not in wanted_styles:
                        counts["not one of the chosen styles"] += 1
                        continue
                    part = "validation" if build_dataset.is_validation(row) else "train"
                    name = f"{row['style']}-{part}.jsonl.gz"
                    if name not in files:
                        files[name] = gzip.open(os.path.join(work, name), "wt", encoding="utf-8")
                    files[name].write(json.dumps(row, ensure_ascii=False) + "\n")
                    counts[f"{row['style']} {part}"] += 1
                    counts["examples"] += 1
                if counts["articles"] % report_every == 0:
                    say(f"  {year}: {counts['articles']} articles so far")
    finally:
        for f in files.values():
            f.close()
    result = {"year": int(year), "file": os.path.basename(path), **counts}
    with open(os.path.join(work, "DONE.txt"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    shutil.rmtree(folder, ignore_errors=True)
    os.replace(work, folder)
    say(f"  {year}: finished, {counts['examples']} examples from {counts['articles']} articles.")
    return result


def _build_year_job(job):
    """build_year for a worker process (one tuple in, the counts out; lines printed with the year in front)."""
    year, path, out, wanted, rebuild = job
    return build_year(year, path, out, wanted, rebuild, say=lambda text: print(text, flush=True))


README = """Historical US newspapers (American Stories), built by the Writing Kit.

One folder per decade, and in it one folder per year. In each year folder, every style has two files:
  <style>-train.jsonl.gz        the training examples, one per line (gzip-compressed JSON lines)
  <style>-validation.jsonl.gz   about one example in twenty, kept back to check the training
and DONE.txt gives the year's counts. To train on an era, use the decade folders you want; to train on a style,
use the files of that style. Most training programs read .jsonl.gz directly; 7-Zip opens them.

Each example has the kit's usual fields (instruction, response, messages, style, register, source, licence, credit)
and also: year, decade, date, newspaper, newspaper_title, state, lccn, page, edition, article_id, headline, byline,
ocr_quality (0 to 1: the share of ordinary English words), legibility (0 to 1, or empty in the earliest years: how
much of the article American Stories' own classifier found legible) and style_rule (the rule that chose the style).

The text is kept exactly as printed and read by OCR, with its mistakes: nothing was scrubbed, corrected or left out.

The styles:
"""


def write_summary(out, results, say=print):
    """README.txt, NEWSPAPERS-REPORT.txt and ATTRIBUTION.txt in out/newspapers."""
    base = os.path.join(out, "newspapers")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "README.txt"), "w", encoding="utf-8") as f:
        f.write(README + "".join(f"  {k}: {v}.\n" for k, v in sn.STYLES.items()))
    by_decade, total = {}, Counter()
    for r in results:
        decade = f"{r['year'] // 10 * 10}s"
        by_decade.setdefault(decade, Counter()).update({k: v for k, v in r.items() if isinstance(v, int)
                                                        and k != "year"})
        total.update({k: v for k, v in r.items() if isinstance(v, int) and k != "year"})
    with open(os.path.join(base, "NEWSPAPERS-REPORT.txt"), "w", encoding="utf-8") as f:
        f.write(f"American Stories newspaper build, {time.strftime('%Y-%m-%d %H:%M')}.\n\n")
        f.write(f"Years built: {len(results)}. Articles read: {total['articles']}. Examples: {total['examples']}.\n\n")
        for decade in sorted(by_decade):
            c = by_decade[decade]
            f.write(f"{decade}: {c['articles']} articles, {c['examples']} examples.\n")
            for style in sn.STYLES:
                n = c[f"{style} train"] + c[f"{style} validation"]
                if n:
                    f.write(f"  {style}: {n}\n")
            if c["not one of the chosen styles"]:
                f.write(f"  not one of the chosen styles: {c['not one of the chosen styles']}\n")
    with open(os.path.join(base, "ATTRIBUTION.txt"), "w", encoding="utf-8") as f:
        f.write(f"Credit: {sn.CREDIT}.\nLicence: {sn.LICENCE} ({sn.CC_BY}).\nWhere: {sn.HF_HOME}\n"
                "Changes: the article texts are unchanged (the narrow columns' line breaks joined into paragraphs, "
                "except in poems); instructions written by rules; styles chosen by rules.\n\n"
                f"Please cite the paper, as the dataset asks:\n{sn.CITATION}\n")
    say(f"Summary written in {base}.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download and build the American Stories newspaper corpus.")
    parser.add_argument("--years", default="", help="years, ranges and decades separated by commas, for example "
                                                    "1850-1869,1900,1920s (default: every year, 1770 to 1964)")
    parser.add_argument("--max-gb", type=float, default=0, help="download at most this many gigabytes in all, "
                                                                "oldest years first (default: no limit)")
    parser.add_argument("--folder", default="newspapers", help="where the year files are kept (made if missing)")
    parser.add_argument("--out", default="out", help="the output folder (the examples go into out/newspapers)")
    parser.add_argument("--list", action="store_true", help="only list the years, their sizes and what is "
                                                            "downloaded already")
    parser.add_argument("--download-only", action="store_true", help="download, do not build")
    parser.add_argument("--build-only", action="store_true", help="build from the files already downloaded")
    parser.add_argument("--rebuild", action="store_true", help="build again the years that were finished before")
    parser.add_argument("--styles", default="", help="build only these styles, separated by commas")
    parser.add_argument("--workers", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)),
                        help="how many years to build at the same time (default: up to 4)")
    args = parser.parse_args(argv)
    say = lambda text: print(text, flush=True)
    wanted = {x.strip() for x in args.styles.split(",") if x.strip()}
    if wanted - set(sn.STYLES):
        parser.error("unknown style: " + ", ".join(sorted(wanted - set(sn.STYLES))) + ". Known: "
                     + ", ".join(sn.STYLES))
    try:
        sn.parse_years(args.years)
    except ValueError as err:
        parser.error(str(err))

    if not args.build_only:
        fetcher = fetch.Fetcher(say)
        say("Reading the list of year files from Hugging Face.")
        files = sn.year_files(fetcher.get(sn.HF_TREE))
        chosen, left_out = sn.choose(files, args.years, args.max_gb)
        total = sum(f["size"] for f in chosen)
        have = sum(f["size"] for f in chosen if os.path.exists(os.path.join(args.folder, f["name"]))
                   and os.path.getsize(os.path.join(args.folder, f["name"])) == f["size"])
        if args.list:
            for f in files:
                path = os.path.join(args.folder, f["name"])
                state = "downloaded" if os.path.exists(path) and os.path.getsize(path) == f["size"] else \
                    ("partly downloaded" if os.path.exists(path + ".part") else "not downloaded")
                say(f"{f['year']}: {sn.gb(f['size'])}, {state}.")
            say(f"All {len(files)} years: {sn.gb(sum(f['size'] for f in files))}.")
            return 0
        say(f"Chosen: {len(chosen)} years, {sn.gb(total)} ({sn.gb(have)} of it downloaded already).")
        if left_out:
            say(f"Left out by the {args.max_gb:g} GB limit: {len(left_out)} years "
                f"({left_out[0]['year']} onwards among those chosen), {sn.gb(sum(f['size'] for f in left_out))}.")
        rest = total - have
        if rest:
            say(f"Still to download: {sn.gb(rest)}. That takes {sn.hours_text(rest, 100)} at 100 megabits a second, "
                f"or {sn.hours_text(rest, 25)} at 25 megabits a second. Close the window to stop; run again to resume.")
        sn.download_years(fetcher, args.folder, chosen, say)
        if args.download_only:
            say("Done downloading.")
            return 0
        local = [(f["year"], os.path.join(args.folder, f["name"])) for f in chosen
                 if os.path.exists(os.path.join(args.folder, f["name"]))]
    else:
        local = sn.local_year_files(args.folder, args.years)
    if not local:
        say(f"No year files to build in {os.path.abspath(args.folder)}.")
        return 1
    say(f"Building {len(local)} years, {args.workers} at a time, into {os.path.abspath(args.out)}"
        f"{os.sep}newspapers. A big year takes about an hour.")
    jobs = [(year, path, args.out, wanted, args.rebuild) for year, path in local]
    if args.workers > 1 and len(jobs) > 1:
        import multiprocessing
        with multiprocessing.Pool(args.workers) as pool:
            results = list(pool.imap_unordered(_build_year_job, jobs))
    else:
        results = [build_year(*job, say=say) for job in jobs]
    write_summary(args.out, sorted(results, key=lambda r: r["year"]), say)
    say(f"Done: {sum(r.get('examples', 0) for r in results)} examples from {len(results)} years. Read "
        "NEWSPAPERS-REPORT.txt in out\\newspapers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
