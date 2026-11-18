"""Pictures that need a description: open a needs zip as a "Describe pictures" workspace, and export a workspace's
pictures as one plain JSONL file for the reviewers' own database.

The training packs' builders (packs/build_packs.py, in the repository) set aside every picture that passed all of a
pack's rules but had no good description, and publish them per pack as needs-<key>.vN.zip in the release
"needs-description". Such a zip is already a describing package (describe_package.py): Describe pictures can import
it straight away (Import a package, Alt+I). Inside it:
  needs.jsonl      one line per picture: "file" (pictures/<name>) or only "url" (a source whose terms do not allow
                   copying its pictures: the picture is downloaded here, see open_needs_zip), "url", "page_url",
                   "credit", "licence", "category", "source" (the pack), "hints" (what the collection said: title,
                   the poor description, tags, place ...), "reason", "place", "place_kind", "content", "child",
                   "not_for_picture_making", "added"
  describing.json  the same pictures, every one "new", as a REVIEW collection: only pictures a person marks checked
                   are ever trained on, and never for picture-making (own_data.py)
  README.txt, CREDITS.txt

Main parts:
  open_needs_zip(zip_path, folder, fetch=None, say=None) -> summary   import the zip into the workspace in folder
                   (made when new); pictures with only an address are downloaded with fetch(url) -> bytes (the
                   polite downloader of review_pack.py; without one they are listed as waiting)
  entry_fields(row) -> {...}        a needs row as the fields of its picture's entry in describing.json
  export_jsonl(folder, out_path) -> summary    every picture of a workspace as one JSON line (see EXPORT_FIELDS)

Command line (in the kit's Python):
    python needs_workspace.py open needs-loc_fsa.v1.zip "D:\\Review\\loc_fsa"
    python needs_workspace.py export "D:\\Review\\loc_fsa" "D:\\Review\\loc_fsa.jsonl"

Only the Python standard library is needed (Pillow, when there, makes big pictures smaller).
"""

import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import describe_package as package  # noqa: E402

NEEDS_ROWS = "needs.jsonl"
PENDING_FILE = ".needs-waiting.jsonl"      # pictures with only an address that are not downloaded yet
STAGING = ".incoming"                       # a hidden folder for downloads in progress (never read for training)

# The fields of each line of export_jsonl, in this order (described in plain words in "HOW TO DESCRIBE PICTURES
# THAT NEED A DESCRIPTION.txt").
EXPORT_FIELDS = ("file", "workspace", "source", "status", "description", "question", "described_by", "described_at",
                 "checked_by", "checked_at", "url", "page_url", "credit", "licence", "category", "reason", "hints",
                 "page_text", "page_text_sources", "drafts", "draft", "draft_suggested", "draft_agreement", "content",
                 "child", "not_for_picture_making", "place", "place_kind", "notes")


def say_nothing(_text):
    """The default for say: print nothing."""


def hint_text(hints):
    """A needs row's hints as one plain line ("title: ...; text: ...")."""
    parts = []
    for key, value in (hints or {}).items():
        shown = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        if shown:
            parts.append(f"{key}: {shown}")
    return "; ".join(parts)


def entry_fields(row):
    """The fields of a picture's describing.json entry for a needs row (as packs/build_packs.needs_entry writes
    them): the hints in "hint" and in the notes, where the picture comes from, its credit, licence and marks."""
    hint = hint_text(row.get("hints"))
    fields = {"hint": hint, "needs_source": row.get("source", ""), "needs_reason": row.get("reason", ""),
              "page_url": row.get("page_url", ""), "source_url": row.get("url", ""), "credit": row.get("credit", ""),
              "licence": row.get("licence", ""), "category": row.get("category", ""),
              "notes": ("What the collection said (may be wrong or incomplete): " + hint) if hint else
              "The collection gave no description."}
    if row.get("content"):
        fields["content"] = row["content"]
    for flag in ("child", "not_for_picture_making"):
        if row.get(flag):
            fields[flag] = "yes"
    for key in ("place", "place_kind"):
        if row.get(key):
            fields[key] = row[key]
    return {k: v for k, v in fields.items() if v}


def read_rows(zip_path):
    """The rows of a needs zip's needs.jsonl ([] when it has none)."""
    with zipfile.ZipFile(zip_path) as z:
        if NEEDS_ROWS not in z.namelist():
            return []
        return [json.loads(line) for line in z.read(NEEDS_ROWS).decode("utf-8").splitlines() if line.strip()]


def pending(folder):
    """The rows of pictures with only an address that are still waiting to be downloaded into the workspace."""
    path = os.path.join(folder, PENDING_FILE)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_pending(folder, rows):
    """Save the rows still waiting (the file is removed when none is left)."""
    path = os.path.join(folder, PENDING_FILE)
    if not rows:
        if os.path.exists(path):
            os.remove(path)
        return
    with open(path + ".new", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    os.replace(path + ".new", path)


def open_needs_zip(zip_path, folder, fetch=None, say=None, library=None):
    """Import a needs zip into the workspace in folder (made when new; a review collection, every picture "new"),
    then download the pictures that came with only an address (fetch(url) -> bytes, or None when it failed;
    without fetch they wait in .needs-waiting.jsonl). library: the Picture Library folder, where a copy of each
    downloaded picture is kept (as the packs' pictures are). Returns a plain summary. Safe to run again: pictures
    already in the workspace are not added twice."""
    say = say or say_nothing
    summary = package.import_package(folder, zip_path, say)
    rows = read_rows(zip_path)
    waiting = pending(folder)
    known = {r.get("url") for r in waiting}
    waiting += [r for r in rows if not r.get("file") and r.get("url") and r["url"] not in known]
    write_pending(folder, waiting)
    if waiting and fetch:
        got, left = fetch_waiting(folder, fetch, say, library)
        summary += (f" {package.plural(got, 'picture')} downloaded from their sources"
                    + (f", {left} still waiting." if left else "."))
    elif waiting:
        summary += (f" {package.plural(len(waiting), 'picture comes', 'pictures come')} with only an address and "
                    "waits to be downloaded." if len(waiting) == 1 else
                    f" {len(waiting)} pictures come with only their address and wait to be downloaded.")
    return summary


def fetch_waiting(folder, fetch, say=None, library=None):
    """Download the waiting pictures into the workspace (each with its entry fields). Returns (downloaded, still
    waiting). A picture that cannot be fetched (refused by robots.txt, gone, not a picture) keeps waiting with the
    reason in its row, so a later run tries again only when asked."""
    say = say or say_nothing
    workspace = package.open_workspace(folder)
    staging = os.path.join(workspace.folder, STAGING)
    os.makedirs(staging, exist_ok=True)
    left, got = [], 0
    rows = pending(workspace.folder)
    for number, row in enumerate(rows, 1):
        try:
            data = fetch(row["url"])
        except Exception as e:  # noqa: BLE001 - this picture waits; the others go on
            data, row["failed"] = None, str(e)[:200] or type(e).__name__
        if not data:
            row.setdefault("failed", "it could not be downloaded")
            left.append(row)
            continue
        name = package.safe_name(os.path.basename(row.get("name") or row["url"].split("?")[0])) or f"picture-{number}"
        if not package.is_picture(name):
            name += ".jpg"
        path = os.path.join(staging, name)
        with open(path, "wb") as f:
            f.write(data)
        before = set(workspace.pictures)
        package.add_pictures(workspace, [path])
        workspace = package.open_workspace(workspace.folder)
        for added in set(workspace.pictures) - before:
            workspace.entry(added).update(entry_fields(row))
            if library:
                keep = os.path.join(library, "needs-description", row.get("source") or "other")
                os.makedirs(keep, exist_ok=True)
                shutil.copyfile(workspace.path(added), os.path.join(keep, added))
        workspace.save()
        os.remove(path)
        got += 1
        if number % 20 == 0 or number == len(rows):
            say(f"  {number} of {len(rows)} pictures with only an address looked at")
    write_pending(workspace.folder, left)
    return got, len(left)


def export_row(workspace, name):
    """One picture of a workspace as a plain dict for the reviewers' database (see EXPORT_FIELDS)."""
    entry = workspace.entry(name)
    drafts = {k[len("draft_"):]: v for k, v in entry.items()
              if k.startswith("draft_") and k not in ("draft_agreement", "draft_engines", "draft_suggested") and v}
    hints = {}
    for part in (entry.get("hint") or "").split("; "):
        key, colon, value = part.partition(": ")
        if colon:
            hints[key] = value
    row = {"file": name, "workspace": workspace.name, "source": entry.get("needs_source", ""),
           "status": entry["status"], "description": package.description(workspace, name),
           "question": package.question_of(workspace, name), "described_by": entry["described_by"],
           "described_at": entry["described_at"], "checked_by": entry["checked_by"],
           "checked_at": entry["checked_at"], "url": entry.get("source_url", ""), "page_url": entry.get("page_url", ""),
           "credit": entry.get("credit", ""), "licence": entry.get("licence", ""),
           "category": entry.get("category", ""), "reason": entry.get("needs_reason", ""), "hints": hints,
           "page_text": entry.get("page_text") or {}, "page_text_sources": entry.get("page_text_sources") or {},
           "drafts": drafts, "draft": entry.get("draft", ""), "draft_suggested": entry.get("draft_suggested", ""),
           "draft_agreement": entry.get("draft_agreement", ""), "content": entry.get("content", ""),
           "child": entry.get("child") == "yes", "not_for_picture_making": entry.get("not_for_picture_making") == "yes",
           "place": entry.get("place", ""), "place_kind": entry.get("place_kind", ""), "notes": entry["notes"]}
    return {k: row[k] for k in EXPORT_FIELDS}


def export_jsonl(folder, out_path):
    """Write every picture of the workspace in folder as one JSON line (EXPORT_FIELDS) to out_path (written to a
    new file first, then put in place). Returns a plain summary."""
    workspace = package.open_workspace(folder)
    names = sorted(workspace.pictures, key=str.lower)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path + ".new", "w", encoding="utf-8") as f:
        for name in names:
            f.write(json.dumps(export_row(workspace, name), ensure_ascii=False) + "\n")
    os.replace(out_path + ".new", out_path)
    return f"{package.plural(len(names), 'picture')} written to {out_path}."


def main(argv=None):
    """The command line (see the module docstring)."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 3 and argv[0] == "open":
        print(open_needs_zip(argv[1], argv[2], say=print))
        return 0
    if len(argv) == 3 and argv[0] == "export":
        print(export_jsonl(argv[1], argv[2]))
        return 0
    print(__doc__.split("Command line")[1].split("Only the")[0].strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
