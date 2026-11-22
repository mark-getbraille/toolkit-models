"""Download and build the US patent text corpus for the Writing Kit, year by year: abstracts, claims and descriptions
(technical writing). The sources, licences and rules are in sources_patents.py; this is the command that runs them,
because the corpus is too big for the ordinary build.

Two sources (--source):
  hupd   (the default) the Harvard USPTO Patent Dataset: patent applications filed 2004 to 2018, one file per year
         from Hugging Face, 61.76 GB in all, CC BY-SA 4.0 (share-alike). No key needed.
  uspto  the USPTO's own Patent Grant Full Text: every granted patent, 1976 to now, one file per week, public domain.
         Needs the owner's own free key in the setting USPTO_ODP_API_KEY (data.uspto.gov, "API key management");
         the key is sent only to api.uspto.gov. The sizes come from the USPTO's own list before anything is
         downloaded (--list shows them).

What it does, step by step (the same design as the newspapers):
  1. reads the list of files and says how many years were chosen, how big they are and how long the download takes;
  2. downloads the chosen years into patents/<source>/, oldest first, saying each file's size and the running
     total. Resumable: stop it whenever you like (close the window) and run it again to carry on; finished files are
     checked (by checksum or size) and never downloaded twice; it stops before a file that would not fit on the disk;
  3. builds the examples year by year, several years at once (--workers), into
       out/patents/<source>/<decade>/<year>/<style>-train.jsonl.gz and <style>-validation.jsonl.gz
     A finished year has DONE.txt and is skipped next time (--rebuild builds it again);
  4. writes out/patents/README.txt, PATENTS-REPORT.txt and ATTRIBUTION.txt.

Usage (from the writing-kit folder):
  python kit/build_patents.py                                   (HUPD, every year)
  python kit/build_patents.py --list                            (each year's size and what you have)
  python kit/build_patents.py --years 2010-2014 --max-gb 20
  python kit/build_patents.py --source uspto --years 1976-1980  (needs USPTO_ODP_API_KEY)
  python kit/build_patents.py --styles patent_claims
  python kit/build_patents.py --download-only | --build-only
"""

import argparse
import gzip
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_dataset  # noqa: E402
import fetch  # noqa: E402
import sources_newspapers as sn  # noqa: E402  (parse_years, choose, gb, hours_text, download_years)
import sources_patents as sp  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402

SOURCES = {"hupd": sp.HUPD_KEY, "uspto": sp.USPTO_KEY}
DOWNLOADED = "DOWNLOADED.json"          # in a USPTO year folder when all its weekly files are downloaded


# ====================================================================== the USPTO Open Data Portal (with the key)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuses to follow redirects, so the USPTO key is never sent on to another address."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def odp_json(key, url):
    """The JSON of one Open Data Portal address, asked with the key (sent only to api.uspto.gov)."""
    if not url.startswith(sp.ODP):
        raise ValueError(f"not an Open Data Portal address: {url}")
    time.sleep(1.0)
    req = urllib.request.Request(url, headers={"X-API-KEY": key, "Accept": "application/json",
                                               "User-Agent": fetch.USER_AGENT})
    with urllib.request.build_opener(NoRedirect).open(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve(key, url, opener=None):
    """Where a file is really downloaded from: (address, needs the key). An Open Data Portal address that sends the
    file itself needs the key; one that redirects (to the USPTO's file store) is downloaded from the new address
    WITHOUT the key."""
    if not url.startswith(sp.ODP):
        return url, False
    opener = opener or urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"X-API-KEY": key, "User-Agent": fetch.USER_AGENT})
    try:
        with opener.open(req, timeout=60):          # closed at once: only the answer's first line is wanted
            return url, True
    except urllib.error.HTTPError as err:
        if err.code in (301, 302, 303, 307, 308) and err.headers.get("Location"):
            return err.headers["Location"], False
        raise


def uspto_year_files(key, years, say=print):
    """[{"year", "files": [{"name", "size", "url"}], "size"}] of the chosen years, from the portal's product list
    (the full text of granted patents, without images)."""
    found = odp_json(key, f"{sp.ODP}datasets/products/search?q=patent%20grant%20full%20text&limit=100")
    products = sp.grant_products(found)
    if not products:
        say("The USPTO's list has no product for the full text of granted patents now; nothing to download.")
        return []
    say(f"USPTO products used: {', '.join(products)}.")
    out = []
    for year in years:
        files = []
        for product in products:
            data = odp_json(key, f"{sp.ODP}datasets/products/{product}?fromDate={year}-01-01&toDate={year}-12-31")
            files += sp.odp_files(data, year)
        if files:
            seen, unique = set(), []
            for f in files:
                if f["name"] not in seen:
                    seen.add(f["name"])
                    unique.append(f)
            out.append({"year": year, "files": unique, "size": sum(f["size"] for f in unique)})
    return out


def download_uspto(key, folder, chosen, say=print, fetcher=None, key_fetcher=None):
    """Download the weekly files of the chosen years into folder/<year>/ (resumable). Returns [(year, how)]."""
    fetcher = fetcher or fetch.Fetcher(say)
    if key_fetcher is None:
        key_fetcher = fetch.Fetcher(say, opener=urllib.request.build_opener(NoRedirect))
        key_fetcher.extra_headers = {"X-API-KEY": key}
    total = sum(y["size"] for y in chosen)
    done, results = 0, []
    for y in chosen:
        base = os.path.join(folder, str(y["year"]))
        os.makedirs(base, exist_ok=True)
        say(f"Year {y['year']}: {len(y['files'])} weekly files, {sn.gb(y['size'])} ({sn.gb(done)} of {sn.gb(total)} "
            "done before it).")
        for f in y["files"]:
            dest = os.path.join(base, f["name"])
            if os.path.exists(dest) and (not f["size"] or os.path.getsize(dest) == f["size"]):
                continue
            free = shutil.disk_usage(base).free
            if f["size"] > free:
                say(f"STOPPED before {f['name']}: it needs {sn.gb(f['size'])} and only {sn.gb(free)} is free.")
                results.append((y["year"], "not enough disk space"))
                return results
            try:
                url, with_key = resolve(key, f["url"])
                (key_fetcher if with_key else fetcher).download(url, dest, size=f["size"] or None, say=say)
            except (OSError, ValueError, urllib.error.URLError) as err:
                say(f"  {f['name']}: not finished ({err}). Run again later to resume.")
                results.append((y["year"], str(err)))
                break
        else:
            # every weekly file of the year is here: the year may be built
            with open(os.path.join(base, DOWNLOADED), "w", encoding="utf-8") as fh:
                json.dump([f["name"] for f in y["files"]], fh)
            done += y["size"]
            say(f"  {y['year']}: done. Running total {sn.gb(done)} of {sn.gb(total)}.")
            results.append((y["year"], "downloaded"))
    return results


# ====================================================================== building a year

def year_folder(out, source_key, year):
    """out/patents/<source>/<decade>/<year>."""
    return os.path.join(out, "patents", source_key, f"{int(year) // 10 * 10}s", str(year))


def year_records(source_key, path):
    """The records of one year: a HUPD year file, or a folder of USPTO weekly files."""
    if source_key == sp.HUPD_KEY:
        with open(path, "rb") as f:
            yield from sp.hupd_records(f)
    else:
        for name in sorted(os.listdir(path)):
            if name.lower().endswith(".zip"):
                with open(os.path.join(path, name), "rb") as f:
                    yield from sp.weekly_records(f)


def build_year(source_key, year, path, out, wanted_styles=(), rebuild=False, say=print, report_every=100_000):
    """Build one year into its own folder; returns its counts (read back from DONE.txt when built before)."""
    folder = year_folder(out, source_key, year)
    done = os.path.join(folder, "DONE.txt")
    if os.path.exists(done) and not rebuild:
        with open(done, encoding="utf-8") as f:
            return json.load(f)
    work = folder + ".part"
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    source = writing_sources.by_key()[source_key]
    files, counts = {}, Counter()
    try:
        for record in year_records(source_key, path):
            for row, _ in build_dataset.examples_from_record(record, source):
                if row is None:
                    continue
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
                if counts["examples"] % report_every == 0:
                    say(f"  {year}: {counts['examples']} examples so far")
    finally:
        for f in files.values():
            f.close()
    result = {"year": int(year), "source": source_key, **counts}
    with open(os.path.join(work, "DONE.txt"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    shutil.rmtree(folder, ignore_errors=True)
    os.replace(work, folder)
    say(f"  {year}: finished, {counts['examples']} examples.")
    return result


def _build_year_job(job):
    """build_year for a worker process."""
    source_key, year, path, out, wanted, rebuild = job
    return build_year(source_key, year, path, out, wanted, rebuild, say=lambda text: print(text, flush=True))


README = """US patents, built by the Writing Kit: technical writing in three styles.

One folder per source (hupd_patents: applications filed 2004 to 2018, CC BY-SA 4.0, share-alike; uspto_patent_grants:
granted patents, public domain), in it one folder per decade and one per year. In each year folder, every style has
two files: <style>-train.jsonl.gz (the training examples) and <style>-validation.jsonl.gz (about one in twenty, kept
back). Most training programs read .jsonl.gz directly; 7-Zip opens them.

Each example has the kit's usual fields and also: year, decade, application_number, patent_number, title,
filing_date, grant_date, main_cpc, decision, section and word_count. Patents with a copyright or mask-work notice
were left out. Under the owner's rule only Social Security, card, bank and account numbers and passwords are masked.

The styles:
"""


def write_summary(out, results, say=print):
    """README.txt, PATENTS-REPORT.txt and ATTRIBUTION.txt in out/patents."""
    base = os.path.join(out, "patents")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "README.txt"), "w", encoding="utf-8") as f:
        f.write(README + "".join(f"  {k}: {v}.\n" for k, v in sp.STYLES.items()))
    with open(os.path.join(base, "PATENTS-REPORT.txt"), "w", encoding="utf-8") as f:
        f.write(f"Patent build, {time.strftime('%Y-%m-%d %H:%M')}.\n\n")
        for r in sorted(results, key=lambda r: (r.get("source", ""), r["year"])):
            parts = ", ".join(f"{s}: {r.get(s + ' train', 0) + r.get(s + ' validation', 0)}" for s in sp.STYLES)
            f.write(f"{r.get('source', '')} {r['year']}: {r.get('examples', 0)} examples ({parts}).\n")
    with open(os.path.join(base, "ATTRIBUTION.txt"), "w", encoding="utf-8") as f:
        f.write(f"hupd_patents: {sp.HUPD_CREDIT}. Licence: {sp.HUPD_LICENCE} ({sp.HUPD_LICENCE_URL}), share-alike: "
                f"anything made from it that you share must keep the same licence. Where: {sp.HUPD_HOME}\n\n"
                f"uspto_patent_grants: {sp.USPTO_CREDIT}. Licence: {sp.USPTO_LICENCE} ({sp.USPTO_LICENCE_URL}). Where: "
                f"{sp.USPTO_HOME}\n\nChanges: each patent's abstract, claims and description made into examples with "
                "instructions written by rules; identity-theft numbers masked.\n")
    say(f"Summary written in {base}.")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download and build the US patent text corpus, year by year.")
    parser.add_argument("--source", choices=sorted(SOURCES), default="hupd", help="hupd (applications 2004 to 2018, "
                        "no key) or uspto (granted patents 1976 to now, needs USPTO_ODP_API_KEY)")
    parser.add_argument("--years", default="", help="years, ranges and decades separated by commas (default: all)")
    parser.add_argument("--max-gb", type=float, default=0, help="download at most this many gigabytes, oldest first")
    parser.add_argument("--folder", default="patents", help="where the downloaded files are kept")
    parser.add_argument("--out", default="out", help="the output folder (the examples go into out/patents)")
    parser.add_argument("--list", action="store_true", help="only list the years, their sizes and what you have")
    parser.add_argument("--download-only", action="store_true", help="download, do not build")
    parser.add_argument("--build-only", action="store_true", help="build from the files already downloaded")
    parser.add_argument("--rebuild", action="store_true", help="build again the years finished before")
    parser.add_argument("--styles", default="", help="build only these styles, separated by commas")
    parser.add_argument("--workers", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)),
                        help="how many years to build at the same time (default: up to 4)")
    args = parser.parse_args(argv)
    say = lambda text: print(text, flush=True)
    wanted = {x.strip() for x in args.styles.split(",") if x.strip()}
    if wanted - set(sp.STYLES):
        parser.error("unknown style: " + ", ".join(sorted(wanted - set(sp.STYLES))) + ". Known: " + ", ".join(sp.STYLES))
    try:
        wanted_year = sn.parse_years(args.years)
    except ValueError as err:
        parser.error(str(err))
    source_key = SOURCES[args.source]
    folder = os.path.join(args.folder, source_key)

    local = []
    if args.source == "hupd":
        if not args.build_only:
            fetcher = fetch.Fetcher(say)
            say("Reading the list of HUPD year files from Hugging Face.")
            files = sp.hupd_year_files(fetcher.get(sp.HUPD_TREE))
            chosen, left_out = sn.choose(files, args.years, args.max_gb)
            if args.list:
                for f in files:
                    path = os.path.join(folder, f["name"])
                    state = "downloaded" if os.path.exists(path) and os.path.getsize(path) == f["size"] else \
                        ("partly downloaded" if os.path.exists(path + ".part") else "not downloaded")
                    say(f"{f['year']}: {sn.gb(f['size'])}, {state}.")
                say(f"All {len(files)} years: {sn.gb(sum(f['size'] for f in files))}.")
                return 0
            total = sum(f["size"] for f in chosen)
            say(f"Chosen: {len(chosen)} years, {sn.gb(total)}.")
            if left_out:
                say(f"Left out by the {args.max_gb:g} GB limit: {len(left_out)} years.")
            say(f"Downloading takes {sn.hours_text(total, 100)} at 100 megabits a second, or "
                f"{sn.hours_text(total, 25)} at 25 (less for what you have already). Close the window to stop; run "
                "again to resume.")
            sn.download_years(fetcher, folder, chosen, say)
            if args.download_only:
                say("Done downloading.")
                return 0
        if os.path.isdir(folder):
            for name in sorted(os.listdir(folder)):
                m = sp.HUPD_YEAR.match(name)
                if m and wanted_year(int(m.group(1))):
                    local.append((int(m.group(1)), os.path.join(folder, name)))
    else:
        key = os.environ.get(sp.USPTO_KEY_ENV, "").strip()
        if not args.build_only:
            if not key:
                say(f"The USPTO source needs your own free key in the setting {sp.USPTO_KEY_ENV}. Make one at "
                    f"{sp.ODP_SIGNUP} (API key management), add the setting (see READ ME FIRST.txt, 'Settings'), "
                    "then run this again. Nothing was downloaded.")
                return 1
            years = [y for y in range(1976, time.localtime().tm_year + 1) if wanted_year(y)]
            listed = uspto_year_files(key, years, say)
            chosen, total = [], 0
            for y in listed:
                if args.max_gb and total + y["size"] > args.max_gb * 1e9:
                    break
                chosen.append(y)
                total += y["size"]
            if args.list:
                for y in listed:
                    say(f"{y['year']}: {len(y['files'])} weekly files, {sn.gb(y['size'])}.")
                say(f"All {len(listed)} years: {sn.gb(sum(y['size'] for y in listed))}.")
                return 0
            say(f"Chosen: {len(chosen)} years, {sn.gb(total)}. Downloading takes {sn.hours_text(total, 100)} at 100 "
                f"megabits a second, or {sn.hours_text(total, 25)} at 25.")
            download_uspto(key, folder, chosen, say)
            if args.download_only:
                say("Done downloading.")
                return 0
        if os.path.isdir(folder):
            for name in sorted(os.listdir(folder)):
                path = os.path.join(folder, name)
                if name.isdigit() and os.path.exists(os.path.join(path, DOWNLOADED)) and wanted_year(int(name)):
                    local.append((int(name), path))
    if not local:
        say(f"No year files to build in {os.path.abspath(folder)}.")
        return 1
    say(f"Building {len(local)} years, {args.workers} at a time, into {os.path.abspath(args.out)}{os.sep}patents.")
    jobs = [(source_key, year, path, args.out, wanted, args.rebuild) for year, path in local]
    if args.workers > 1 and len(jobs) > 1:
        import multiprocessing
        with multiprocessing.Pool(args.workers) as pool:
            results = list(pool.imap_unordered(_build_year_job, jobs))
    else:
        results = [build_year(*job, say=say) for job in jobs]
    write_summary(args.out, results, say)
    say(f"Done: {sum(r.get('examples', 0) for r in results)} examples from {len(results)} years. Read "
        "PATENTS-REPORT.txt in out\\patents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
