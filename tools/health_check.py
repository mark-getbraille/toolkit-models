"""The build health check: which picture packs, books and manual collections failed, are missing, or came out nearly
empty, and why when the builds record a reason.

It reads (public sources only: GitHub's API unauthenticated, or with the GitHub Actions run's own GITHUB_TOKEN):
  - the latest catalogues: packs.json (release "training-data"), textbooks.json (release "textbooks") and
    manuals.json (release "manuals");
  - what the code says should be there (tools/library_inventory.py: every pack key, every book key the reference
    library's code lists, every manual category);
  - the latest runs of the build workflows (packs.yml, textbooks.yml and its hourly backfill, manuals.yml): each
    key's newest job that was not cancelled, so a missing item is told apart as STILL BUILDING (running or waiting
    for a machine), FAILED (its last job failed) or NOT BUILT YET (no recent job: not asked for yet, or asked for
    long ago);
  - for failed jobs, their logs (only with the workflow's token; up to --logs of them), to find the cause: too many
    requests (429), refused (403), robots.txt, not found, out of time and so on (library_common.CAUSES).
Nearly empty means: a picture pack with fewer than 10 pictures (rows), a book of fewer than 3 pages, a manual
collection with fewer than 10 entries. The books the textbook builds left out are grouped by the cause their
catalogue records ("left_out" reasons).

It writes health-check.txt (plain text for Notepad and a screen reader) and health-check.json (for the master guide's
page), and prints the summary:
    python3 tools/health_check.py --out build/library-reports
    python3 tools/health_check.py --out build/library-reports --logs 0          (do not read any logs)
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library_common as C  # noqa: E402

WORKFLOWS = {"packs": ["packs.yml"], "textbooks": ["textbooks.yml", "textbooks-backfill.yml"],
             "manuals": ["manuals.yml"]}
FEW_PICTURES = 10           # a pack with fewer pictures (rows) is nearly empty
FEW_PAGES = 3               # a book with fewer pages is nearly empty
FEW_ENTRIES = 10            # a manual collection with fewer entries is nearly empty
FAILED, BUILDING, NOT_YET, NEARLY_EMPTY, OK = "failed", "still building", "not built yet", "nearly empty", "ok"
STATUS_ORDER = [FAILED, BUILDING, NEARLY_EMPTY, NOT_YET]


def missing_status(job):
    """(status, detail) of an item that is not published, from its newest job (None: no recent job)."""
    if not job:
        return NOT_YET, "no recent build job (not asked for yet, or asked for long ago)"
    if job["state"] in ("building", "queued"):
        return BUILDING, ("building now" if job["state"] == "building" else "waiting for a build machine") + \
            f" (since {job['when']})"
    if job["state"] == "failed":
        return FAILED, f"its last build failed ({job['when']})"
    return NOT_YET, f"its last build finished ({job['when']}) but the catalogue does not list it yet"


def item(key, title, status, detail, job=None, cause=""):
    """One line of the check."""
    return {"key": key, "title": title or key, "status": status, "detail": detail, "cause": cause,
            "job": (job or {}).get("id"), "job_state": (job or {}).get("state", ""),
            "workflow": (job or {}).get("workflow", "")}


def check_packs(packs_json, pack_keys, names, jobs):
    """Items for the picture packs: missing (failed, still building, not built yet) and nearly empty ones, and a
    published pack whose latest build failed (the older pack stays published)."""
    packs_json, jobs, out = packs_json or {}, jobs or {}, []
    for key in pack_keys:
        pub, job = packs_json.get(key), jobs.get(key)
        title = names.get(key, key)
        if pub is None:
            status, detail = missing_status(job)
            out.append(item(key, title, status, detail, job))
            continue
        rows = pub.get("rows", pub.get("pictures", 0)) or 0
        if rows < FEW_PICTURES:
            out.append(item(key, title, NEARLY_EMPTY, f"only {rows} pictures", job))
        elif job and job["state"] == "failed":
            out.append(item(key, title, FAILED, f"its last build failed ({job['when']}); the older pack with "
                            f"{rows} pictures stays published", job))
        elif job and job["state"] in ("building", "queued"):
            out.append(item(key, title, BUILDING, f"being built again (the published pack has {rows} pictures)",
                            job))
    return out


def check_books(textbooks_json, book_keys, titles, groups, jobs):
    """Items for the reference library: keys the code lists that are not built (failed, still building, not built
    yet), keys the catalogue records as failed, and nearly empty books. Also returns the left-out books grouped by
    cause ({cause: [(title, reason)]})."""
    t, jobs, out = textbooks_json or {}, jobs or {}, []
    books = t.get("books", [])
    built = {b.get("key") for b in books if b.get("key")} | set(t.get("pieces_done", []))
    failed = t.get("pieces_failed", {}) or {}
    for key in book_keys:
        if key in built:
            continue
        job = jobs.get(key)
        if key in failed and not (job and job["state"] in ("building", "queued")):
            status, detail = FAILED, f"failed {failed[key]} time(s) (catalogue)"
        else:
            status, detail = missing_status(job)
        out.append(dict(item(key, titles.get(key, key), status, detail, job), group=groups.get(key, "")))
    for key, n in failed.items():
        if key not in book_keys and key not in built:
            out.append(item(key, key, FAILED, f"failed {n} time(s) (catalogue)", jobs.get(key)))
    for b in books:
        pages = b.get("article_count")
        if pages is not None and pages < FEW_PAGES:
            out.append(dict(item(b.get("key") or b.get("name", ""), b.get("title", ""), NEARLY_EMPTY,
                                 f"only {pages} page(s) ({b.get('file', '')})"), group=b.get("group", "")))
    left = {}
    for x in t.get("left_out", []):
        left.setdefault(C.cause_of(x.get("reason", "")), []).append((x.get("title", ""), x.get("reason", "")))
    return out, left


def check_manuals(manuals_json, categories, jobs):
    """Items for the manual collections: missing categories (failed, still building, not built yet) and nearly empty
    ones."""
    cols = (manuals_json or {}).get("collections", {}) or {}
    if isinstance(cols, list):
        cols = {c.get("key"): c for c in cols}
    jobs, out = jobs or {}, []
    for c in categories:
        key, job = c["key"], jobs.get(c["key"])
        pub = cols.get(key)
        if pub is None:
            status, detail = missing_status(job)
            out.append(item(key, c.get("name", key), status, detail, job))
            continue
        entries = pub.get("entries", 0) or 0
        if entries < FEW_ENTRIES:
            out.append(item(key, c.get("name", key), NEARLY_EMPTY, f"only {entries} entries", job))
        elif job and job["state"] == "failed":
            out.append(item(key, c.get("name", key), FAILED, f"its last build failed ({job['when']}); the older "
                            f"collection with {entries} entries stays published", job))
    return out


def add_causes(items, read_log, most=30):
    """Fill in "cause" (and the last line the build printed) for failed items with a job, reading at most `most` logs
    (read_log(job id) -> text, "" when it cannot be read)."""
    done = 0
    cache = {}
    for it in items:
        if it["status"] != FAILED or not it.get("job") or it["cause"] or it.get("job_state") != "failed":
            continue
        if it["job"] not in cache:
            if done >= most:
                break
            cache[it["job"]] = read_log(it["job"]) or ""
            done += 1
        log = cache[it["job"]]
        if log:
            it["cause"] = C.log_cause(log)
            line = C.failure_line(log)
            if line:
                it["detail"] += f"; last line: {line}"
    return items


def run_check(cats=None, inv=None, jobs=None, read_log=None, logs=30):
    """The whole check as a dict. cats: the catalogues (library_common.catalogues); inv: {"books", "packs", "kit",
    "manuals"} of tools/library_inventory.py; jobs: {"packs"|"textbooks"|"manuals": {key: job} or None}; read_log:
    a job's log text. Each one left out is read here."""
    import library_inventory as L
    cats = cats if cats is not None else C.catalogues()
    if inv is None:
        inv = {}
        for part in ("books", "packs", "kit", "manuals"):
            try:
                inv[part] = L.inventory(part)
            except Exception as e:  # noqa: BLE001 - said in the report
                inv[part] = {"error": str(e)}
    if jobs is None:
        jobs = {}
        for area, files in WORKFLOWS.items():
            merged, readable = {}, False
            for wf in files:
                got = C.workflow_jobs(wf)
                if got is not None:
                    readable = True
                    for k, v in got.items():
                        if k not in merged or v["when"] > merged[k]["when"]:
                            merged[k] = v
            jobs[area] = merged if readable else None
    names = {k: v.get("name", k) for k, v in (inv.get("kit", {}).get("collections") or {}).items()}
    pack_keys = [p["key"] for p in inv.get("packs", {}).get("packs", [])]
    book_list = inv.get("books", {}).get("books", [])
    titles = {b["key"]: b["title"] for b in book_list}
    group_names = inv.get("books", {}).get("groups", {})
    groups = {b["key"]: group_names.get(b["group"], b["group"]) for b in book_list}
    book_keys = inv.get("books", {}).get("keys", [])
    packs = check_packs(cats.get("packs"), pack_keys, names, jobs.get("packs"))
    books, left = check_books(cats.get("textbooks"), book_keys, titles, groups, jobs.get("textbooks"))
    manuals = check_manuals(cats.get("manuals"), inv.get("manuals", {}).get("categories", []), jobs.get("manuals"))
    if logs:
        add_causes(packs + books + manuals, read_log or C.job_log, logs)
    notes = []
    for part in ("books", "packs", "kit", "manuals"):
        if inv.get(part, {}).get("error"):
            notes.append(f"The {part} code could not be read: {inv[part]['error']}")
    for area in ("packs", "textbooks", "manuals"):
        if cats.get(area) is None:
            notes.append(f"The {area} catalogue is not published or could not be read.")
        if jobs.get(area) is None:
            notes.append(f"The {area} build runs could not be read, so missing items cannot be told apart as still "
                         f"building or failed.")
    published = {"packs": len(cats.get("packs") or {}), "books": len((cats.get("textbooks") or {}).get("books", [])),
                 "manuals": len(((cats.get("manuals") or {}).get("collections")) or {})}
    expected = {"packs": len(pack_keys), "books": len(book_keys),
                "manuals": len(inv.get("manuals", {}).get("categories", []))}
    return {"packs": packs, "books": books, "manuals": manuals, "left_out": left, "notes": notes,
            "published": published, "expected": expected}


def counts(items):
    """{status: how many} of a list of items."""
    out = {}
    for it in items:
        out[it["status"]] = out.get(it["status"], 0) + 1
    return out


def summary_lines(result):
    """The short summary: per area, how many are published, failed, still building, nearly empty, not built yet."""
    out = []
    for area, label, unit in (("packs", "Picture packs", "packs"), ("books", "Reference books", "book keys"),
                              ("manuals", "Manual collections", "categories")):
        c = counts(result[area])
        pub = result["published"].get(area, 0)
        exp = result["expected"].get(area, 0)
        out.append(f"{label}: {pub} published; the code lists {exp} {unit}. Failed {c.get(FAILED, 0)}, still "
                   f"building {c.get(BUILDING, 0)}, nearly empty {c.get(NEARLY_EMPTY, 0)}, not built yet "
                   f"{c.get(NOT_YET, 0)}.")
    left = result.get("left_out", {})
    if left:
        out.append("Books left out by the textbook builds, by cause: " +
                   "; ".join(f"{cause}: {len(v)}" for cause, v in sorted(left.items(), key=lambda x: -len(x[1])))
                   + ".")
    return out


def report_lines(result, date=""):
    """The whole report as plain text lines: the summary, then each area by status, failed ones grouped by cause, the
    books not built yet grouped by their library group, and the left-out books by cause."""
    out = ["BUILD HEALTH CHECK" + (f" ({date})" if date else ""), "", "SUMMARY"] + \
        [f"  {x}" for x in summary_lines(result)] + [""]
    for area, label in (("packs", "PICTURE PACKS"), ("books", "REFERENCE BOOKS"), ("manuals", "MANUAL COLLECTIONS")):
        items = result[area]
        out.append(label)
        if not items:
            out += ["  Everything the code lists is published and none is nearly empty.", ""]
            continue
        for status in STATUS_ORDER:
            these = [it for it in items if it["status"] == status]
            if not these:
                continue
            out.append(f"  {status.upper()} ({len(these)})")
            if status == FAILED:
                by_cause = {}
                for it in these:
                    by_cause.setdefault(it["cause"] or "cause not recorded (no log read)", []).append(it)
                for cause, its in sorted(by_cause.items(), key=lambda x: -len(x[1])):
                    out.append(f"    Cause: {cause} ({len(its)})")
                    out += [f"      {it['title']} ({it['key']}): {it['detail']}." for it in its]
            elif status == NOT_YET and area == "books":
                by_group = {}
                for it in these:
                    by_group.setdefault(it.get("group") or "other", []).append(it["key"])
                for group, keys in sorted(by_group.items()):
                    out.append(f"    {group} ({len(keys)}): {', '.join(keys)}.")
            else:
                out += [f"    {it['title']} ({it['key']}): {it['detail']}." for it in these]
        out.append("")
    left = result.get("left_out", {})
    if left:
        out.append("BOOKS LEFT OUT BY THE TEXTBOOK BUILDS (as the catalogue records them), BY CAUSE")
        for cause, rows in sorted(left.items(), key=lambda x: -len(x[1])):
            out.append(f"  {cause} ({len(rows)})")
            out += [f"    {title}: {reason}" for title, reason in rows]
        out.append("")
    if result.get("notes"):
        out += ["NOTES"] + [f"  {n}" for n in result["notes"]]
    return out


def main(argv=None):
    """Run the check, write health-check.txt and health-check.json into --out, and print the summary."""
    import datetime
    p = argparse.ArgumentParser(description="List the packs, books and manual collections that failed, are missing "
                                            "or came out nearly empty.")
    p.add_argument("--out", default="build/library-reports")
    p.add_argument("--logs", type=int, default=30, help="read at most this many failed jobs' logs for their cause")
    a = p.parse_args(argv)
    result = run_check(logs=a.logs)
    result["date"] = datetime.date.today().isoformat()
    lines = report_lines(result, result["date"])
    C.write_text(os.path.join(a.out, "health-check.txt"), lines)
    C.write_json(os.path.join(a.out, "health-check.json"), result)
    print("\n".join(["BUILD HEALTH CHECK " + result["date"]] + summary_lines(result)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
