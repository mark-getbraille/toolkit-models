"""The size plan: how much drive space the owner's whole library needs, and what drives to buy.

It adds up, from public sources only (no secrets; GitHub's API unauthenticated, or with the GITHUB_TOKEN of the
GitHub Actions run):
  1. Every DATA release of the owner's public repositories (REPOS: toolkit-models with its training data, needs-
     description, textbooks and the other book releases, manuals, the personal-use releases and the converted AI
     models of engine-models; and place-packs), each file as GitHub lists it. Program Downloader's "Back up all
     data" copies exactly these into B:\\Data packs. Private repositories cannot be read without the owner's own
     login, so they are not counted (the report says so).
  2. The Kiwix libraries, from the directory listing of ftp.fau.de/kiwix/zim/, an official Kiwix mirror whose
     robots.txt allows programs. (download.kiwix.org and the Kiwix online catalogue both say "Disallow: /" in their
     robots.txt, so they are not read.) English only by default (one file per book: its biggest flavour, which holds
     the others' content), with every language and every flavour said beside it.
  3. The original AI models on Hugging Face that plan.json converts (each base model at its pinned commit), from
     Hugging Face's public API (the size of every file of the repository at that commit).
  4. The Writing Kit's big corpora: the American Stories newspapers (the Hugging Face dataset's size, about 340 GB to
     download, and about 190 GB of built output, the coordinator's estimate of 22 November 2026), the court opinions
     (the newest opinions file of CourtListener's public bulk-data bucket), and the patents (the kit has not built
     them yet; its notes give no total, so they are listed without a size). The kit's other sources are small; the
     sizes their notes state are added.
Each GitHub release is counted twice: with every version kept (every file GitHub has, as Program Downloader's backup
keeps them) and newest only (the newest version of each file). The report then recommends drive sizes, with room to
grow, in plain words.

Run it from the repository's folder (it writes size-plan.txt and size-plan.json):
    python3 tools/size_plan.py --out build/library-reports
    python3 tools/size_plan.py --out build/library-reports --all-languages     (Kiwix in every language)
"""

import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import library_common as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPOS = [f"{C.OWNER}/toolkit-models", f"{C.OWNER}/place-packs"]
SKIP_TAGS = ("library-reports",)            # this tool's own reports
KIWIX_MIRROR = "https://ftp.fau.de/kiwix/zim/"
HF_API = "https://huggingface.co/api"
NEWSPAPERS_DATASET = "dell-research-harvard/AmericanStories"
NEWSPAPERS_GB = 340.4                       # writing-kit/kit/sources_newspapers.py FULL_SIZE_GB (22 November 2026)
NEWSPAPERS_OUTPUT_GB = 190                  # the built newspaper data: the coordinator's estimate (22 November 2026)
COURTLISTENER_BUCKET = "https://com-courtlistener-storage.s3-us-west-2.amazonaws.com/?list-type=2&prefix=bulk-data/"
DRIVE_TB = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]     # common hard drive sizes on sale
GROWTH = 1.5                                # room to grow: half as much again for the coming year's new versions
TB = 10 ** 12


# ====================================================================== 1. GitHub releases

def area_of(repo, tag):
    """The plain-words area of a release, for the report and the guide."""
    t = tag.lower()
    if repo.endswith("/place-packs"):
        return "Place packs (maps)"
    if t in ("training-data", "needs-description"):
        return "Picture packs (training data)"
    if t.startswith("personal"):
        return "Personal-use book releases"
    if t.startswith("manuals"):
        return "Manual collections"
    if t == "engine-models" or "models" in t:
        return "Converted AI models (engine-models)"
    if t.startswith(("textbooks", "libretexts", "courses", "publications", "medicines")):
        return "Reference books"
    return "Other data releases"


def github_rows(repos=None, releases_of=None):
    """[{"area", "item", "files", "all", "newest"}] of every data release of the repositories (sizes in bytes).
    releases_of(repo) gives a repository's releases (library_common.list_releases; tests give made-up ones)."""
    releases_of = releases_of or C.list_releases
    rows, unread = [], []
    for repo in repos or REPOS:
        releases = releases_of(repo)
        if not releases:
            unread.append(repo)
            continue
        series = {}                       # dated releases of one series ("packs-detail-2026...") counted together
        for r in releases:
            tag = r.get("tag_name", "")
            if r.get("draft") or tag in SKIP_TAGS or not C.is_data_release(r):
                continue
            s = series.setdefault(C.tag_stem(tag), {"tags": [], "files": []})
            s["tags"].append(tag)
            s["files"] += [{"name": a["name"], "size": a.get("size") or 0, "release": tag,
                            "updated_at": a.get("updated_at", "")} for a in r.get("assets") or []]
        for stem, s in series.items():
            if not s["files"]:
                continue
            tags = sorted(s["tags"])
            rows.append({"area": area_of(repo, tags[-1]), "item": f"{repo.split('/')[1]}: {', '.join(tags)}",
                         "files": len(s["files"]), "all": sum(f["size"] for f in s["files"]),
                         "newest": sum(f["size"] for f in C.newest_only(s["files"]))})
    return rows, unread


# ====================================================================== 2. Kiwix (an official mirror's listing)

LISTING_ROW = re.compile(r'href="([^"?/][^"]*?\.zim)".*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+([\d.]+[KMGT]?)(?=\s|$)')
LISTING_DIR = re.compile(r'href="([a-z0-9_-]+/)"')


def kiwix_files(get=None, mirror=KIWIX_MIRROR):
    """[{"folder", "name", "book", "date", "size"}] of every .zim file in the mirror's folders. book is the file
    name without its date ("wikipedia_en_all_maxi"). get(url) -> the listing's HTML (library_common.http_get)."""
    get = get or C.http_get
    top = get(mirror)
    out = []
    for folder in dict.fromkeys(LISTING_DIR.findall(top)):
        page = get(mirror + folder)
        for line in page.splitlines():
            m = LISTING_ROW.search(line)
            if m:
                name = m.group(1)
                out.append({"folder": folder.strip("/"), "name": name,
                            "book": re.sub(r"_\d{4}-\d{2}\.zim$", "", name), "date": m.group(2)[:10],
                            "size": C.parse_size(m.group(3)) or 0})
    return out


FLAVOURS = ("_maxi", "_nopic", "_mini")


def kiwix_rows(files, all_languages=False):
    """Rows for the Kiwix files: the newest file of each book (newest), every dated file the mirror keeps (all), in
    English only (a name with "_en_" or ending "_en"), or every language. One file per book: of a book's flavours
    (maxi, nopic, mini) only the biggest is counted (it holds what the others hold). Also returns the totals of the
    other choices for the report's notes."""
    def english(name):
        """True for an English library."""
        return "_en_" in name + "_" or name.endswith("_en")

    def plan(choose):
        """(newest bytes, all bytes, number of books) for the books choose(book) keeps."""
        newest = {}
        for f in files:
            if choose(f["book"]) and (f["book"] not in newest or f["date"] > newest[f["book"]]["date"]):
                newest[f["book"]] = f
        per_book = {}
        for book, f in newest.items():
            base = book
            for fl in FLAVOURS:
                base = base.replace(fl, "")
            if base not in per_book or f["size"] > per_book[base]["size"]:
                per_book[base] = f
        keep = {f["book"] for f in per_book.values()}
        all_bytes = sum(f["size"] for f in files if f["book"] in keep)
        return sum(f["size"] for f in per_book.values()), all_bytes, len(per_book)

    en = plan(english)
    every = plan(lambda b: True)
    every_flavour = sum(f["size"] for f in files if english(f["book"]))
    chosen = every if all_languages else en
    label = "every language" if all_languages else "English"
    rows = [{"area": "Kiwix libraries", "item": f"Kiwix, {label}: {chosen[2]} libraries, one file each",
             "files": chosen[2], "all": chosen[1], "newest": chosen[0]}]
    notes = {"english_newest": en[0], "english_all": en[1], "english_books": en[2],
             "every_language_newest": every[0], "every_language_all": every[1], "every_language_books": every[2],
             "english_every_flavour_all_dates": every_flavour, "all_languages": all_languages}
    return rows, notes


# ====================================================================== 3. AI models on Hugging Face

def plan_models(path=None):
    """[(repository, commit)] of the base models plan.json converts (each once)."""
    with open(path or os.path.join(ROOT, "plan.json"), encoding="utf-8") as f:
        plan = json.load(f)
    return list(dict.fromkeys((m["base_model"], m.get("base_revision") or "main") for m in plan
                              if m.get("base_model")))


def hf_size(repo, revision="main", kind="models", get_json=None):
    """The total size in bytes of every file of a Hugging Face repository at a commit (None when it cannot be read).
    kind: "models" or "datasets"."""
    get_json = get_json or C.get_json
    data = get_json(f"{HF_API}/{kind}/{repo}/revision/{revision}?blobs=true")
    if not data or "siblings" not in data:
        return None
    return sum((s.get("size") or 0) for s in data["siblings"])


def hf_rows(models, get_json=None):
    """One row for the original AI models (all of them together) and the list of models that could not be read."""
    total, unread = 0, []
    for repo, rev in models:
        size = hf_size(repo, rev, get_json=get_json)
        if size is None:
            unread.append(repo)
        else:
            total += size
    rows = [{"area": "AI models (originals on Hugging Face)",
             "item": f"{len(models) - len(unread)} original models that plan.json converts", "files": len(models),
             "all": total, "newest": total}]
    return rows, unread


# ====================================================================== 4. the Writing Kit's corpora

def courtlistener_opinions(get=None):
    """(file name, bytes) of the newest opinions file in CourtListener's public bulk-data bucket, or (None, None)."""
    get = get or C.http_get
    try:
        text = get(COURTLISTENER_BUCKET + "opinions")
    except Exception:  # noqa: BLE001 - not readable: listed without a size
        return None, None
    found = re.findall(r"<Key>(bulk-data/opinions-(\d{4}-\d{2}-\d{2})\.csv\.bz2)</Key>.*?<Size>(\d+)</Size>", text)
    if not found:
        return None, None
    name, _date, size = max(found, key=lambda x: x[1])
    return name.split("/")[-1], int(size)


def writing_rows(get=None, get_json=None, writing=None):
    """Rows for the Writing Kit: the newspapers (download and built output), the court opinions, the patents (no size
    stated yet) and the kit's other sources whose notes state a size. writing: the parsed sources
    (library_common.parse_writing_sources), or None to read the writing-kit branch."""
    news = hf_size(NEWSPAPERS_DATASET, kind="datasets", get_json=get_json) or int(NEWSPAPERS_GB * 1e9)
    rows = [
        {"area": "Writing Kit corpora", "item": "Historical newspapers (American Stories), download",
         "files": 180, "all": news, "newest": news},
        {"area": "Writing Kit corpora", "item": "Historical newspapers, the built writing data (estimate)",
         "files": 0, "all": int(NEWSPAPERS_OUTPUT_GB * 1e9), "newest": int(NEWSPAPERS_OUTPUT_GB * 1e9)}]
    name, size = courtlistener_opinions(get)
    rows.append({"area": "Writing Kit corpora", "item": f"Court opinions (CourtListener bulk file {name})" if name
                 else "Court opinions (CourtListener bulk file: size could not be read)",
                 "files": 1 if name else 0, "all": size or 0, "newest": size or 0})
    notes = ["Patents (USPTO full texts): not counted. The Writing Kit has not built them yet, and its notes say only "
             "that the USPTO's weekly full-text files are a gigabyte or more each."]
    if writing is None:
        try:
            writing = C.parse_writing_sources(C.writing_kit_texts())
        except Exception:  # noqa: BLE001 - the branch could not be read
            writing = []
    small = [s for s in writing if s.get("size_bytes") and s["key"] != "american_stories_newspapers"]
    if small:
        total = sum(s["size_bytes"] for s in small)
        rows.append({"area": "Writing Kit corpora", "item": f"Other Writing Kit sources whose notes state a size "
                     f"({', '.join(s['key'] for s in small)})", "files": len(small), "all": total, "newest": total})
    return rows, notes


# ====================================================================== the plan and the recommendation

def recommend(total_bytes, growth=GROWTH):
    """(drive size in TB, how many drives for one copy, words) for a library of total_bytes: the smallest common drive
    that holds it with room to grow (growth), or several of the biggest common size when none does. Always two sets:
    one for the B: drive and one as the second copy."""
    need = total_bytes * growth
    for tb in DRIVE_TB:
        if tb * TB >= need:
            return tb, 1, (f"Buy two {tb} TB drives: one as your B: drive and one as a second copy (a backup), kept "
                           f"apart from the first.")
    tb = DRIVE_TB[-1]
    n = math.ceil(need / (tb * TB))
    return tb, n, (f"No single drive is big enough. Buy {2 * n} drives of {tb} TB: {n} for the library and {n} for "
                   f"the second copy. (Program Downloader puts the Data packs, Original sources, Kiwix and AI models "
                   f"folders where you choose, so they can be spread over the {n} drives.)")


def make_plan(rows, notes, kiwix_notes=None, unread=None):
    """The whole plan as a dict: rows, totals (every version kept, newest only), the recommendation, notes."""
    total_all = sum(r["all"] for r in rows)
    total_new = sum(r["newest"] for r in rows)
    areas = {}
    for r in rows:
        a = areas.setdefault(r["area"], {"area": r["area"], "all": 0, "newest": 0, "items": 0})
        a["all"] += r["all"]
        a["newest"] += r["newest"]
        a["items"] += 1
    tb, n, words = recommend(total_all)
    k = kiwix_notes or {}
    other = ""
    if k and not k.get("all_languages") and k.get("every_language_all"):
        alt = total_all - k.get("english_all", 0) + k["every_language_all"]
        other = (f"If you also want the Kiwix libraries in every language (not only English), the library needs about "
                 f"{C.size_words(alt)}: " + recommend(alt)[2])
    return {"rows": rows, "areas": list(areas.values()), "total_all": total_all, "total_newest": total_new,
            "drive_tb": tb, "drives_per_copy": n, "recommendation": words, "other_choice": other, "growth": GROWTH,
            "notes": list(notes), "kiwix": kiwix_notes or {}, "unread": list(unread or [])}


def gather(all_languages=False, releases_of=None, get=None, get_json=None, models=None, writing=None):
    """Read every source and return the plan (make_plan). Each source that cannot be read is said in the notes."""
    rows, notes, unread = [], [], []
    gh, gh_unread = github_rows(REPOS, releases_of)
    rows += gh
    if gh_unread:
        notes.append("Could not read the releases of: " + ", ".join(gh_unread) + ".")
    notes.append("Private repositories (the toolkit's program releases and others) are not counted: they cannot be "
                 "read without your own GitHub login. Program Downloader's backup reads them with your login.")
    kiwix_notes = {}
    try:
        k, kiwix_notes = kiwix_rows(kiwix_files(get), all_languages)
        rows += k
    except Exception as e:  # noqa: BLE001 - said in the report
        notes.append(f"The Kiwix mirror could not be read ({e}); Kiwix is not counted.")
    try:
        h, h_unread = hf_rows(models if models is not None else plan_models(), get_json)
        rows += h
        unread += h_unread
        if h_unread:
            notes.append(f"{len(h_unread)} AI models on Hugging Face could not be read: {', '.join(h_unread)}.")
    except Exception as e:  # noqa: BLE001 - said in the report
        notes.append(f"The AI models could not be read ({e}).")
    w, w_notes = writing_rows(get, get_json, writing)
    rows += w
    notes += w_notes
    return make_plan(rows, notes, kiwix_notes, unread)


def report_lines(plan, date=""):
    """The plan as plain text lines for Notepad and a screen reader."""
    s = C.size_words
    out = ["SIZE PLAN FOR THE WHOLE LIBRARY" + (f" ({date})" if date else ""), "",
           f"You need about {s(plan['total_all'])} with every version kept, or {s(plan['total_newest'])} if you keep "
           f"only the newest version of each file.",
           f"With room to grow (half as much again for the coming year), plan for about "
           f"{s(plan['total_all'] * plan['growth'])}.", "",
           "WHAT TO BUY", plan["recommendation"]] + ([plan["other_choice"]] if plan.get("other_choice") else []) + [
           "",
           "Sizes are in decimal units, as printed on a drive's box (1 TB is 1,000 GB). Windows shows a little less "
           "(it counts 1 TB as 1,024 GB), so a 20 TB drive shows as about 18.2 TB.", "",
           "BY AREA (every version kept; newest only)"]
    for a in sorted(plan["areas"], key=lambda a: -a["all"]):
        out.append(f"  {a['area']}: {s(a['all'])}; newest only {s(a['newest'])}.")
    out += ["", "EVERY ITEM (every version kept; newest only)"]
    for r in sorted(plan["rows"], key=lambda r: (r["area"], -r["all"])):
        files = f", {r['files']} files" if r.get("files") else ""
        out.append(f"  {r['area']}, {r['item']}{files}: {s(r['all'])}; newest only {s(r['newest'])}.")
    k = plan.get("kiwix") or {}
    if k:
        out += ["", "KIWIX CHOICES",
                f"  English, one file per library: {k.get('english_books', 0)} libraries, "
                f"{s(k.get('english_newest'))}.",
                f"  Every language, one file per library: {k.get('every_language_books', 0)} libraries, "
                f"{s(k.get('every_language_newest'))}.",
                f"  English, every flavour and every dated copy the mirror keeps: "
                f"{s(k.get('english_every_flavour_all_dates'))}."]
    if plan.get("notes"):
        out += ["", "NOTES"] + [f"  {n}" for n in plan["notes"]]
    return out


def main(argv=None):
    """Read everything, write size-plan.txt and size-plan.json into --out, and print the report."""
    import datetime
    p = argparse.ArgumentParser(description="Add up the size of the whole library and recommend drive sizes.")
    p.add_argument("--out", default="build/library-reports")
    p.add_argument("--all-languages", action="store_true", help="count Kiwix in every language, not only English")
    a = p.parse_args(argv)
    plan = gather(all_languages=a.all_languages)
    plan["date"] = datetime.date.today().isoformat()
    lines = report_lines(plan, plan["date"])
    C.write_text(os.path.join(a.out, "size-plan.txt"), lines)
    C.write_json(os.path.join(a.out, "size-plan.json"), plan)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
