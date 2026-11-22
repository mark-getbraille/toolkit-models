"""What the repository's own code says is in the library, read fresh at every run, so the guide never goes stale.

Each part is read in its OWN Python process, because the parts have files with the same names (textbooks/sources.py
and training-kit/kit/sources.py, three military_release.py files): importing them into one process would mix them up.
inventory(part) starts this file as a small program ("python tools/library_inventory.py packs"), which imports only
that part's code and prints what it found as JSON.

The parts:
  books    the reference library (textbooks/): every group (sources.GROUPS) with its name; the books the code
           lists (sources.py's PDF, web guide, non-profit, law and school-book records, and every module of
           more_refs.MODULES: its web guides, PDFs and its own makers' keys), each with its key, title, one-line
           description, group and licence class; the rows checked and not built (NOT_INCLUDED); and every key
           the code can build (for the health check).
  packs    the picture packs (packs/build_packs.py PACKS): key, licence line and its builder's first line.
  kit      the Picture Model Training Kit: the topic add-ons (training-kit/kit/topics.py TOPICS) with their
           collections, and every collection (sources.SOURCES) with its name, licence group, download size and
           whether a picture-making model may learn from it (train_pictures.chosen_sources' rule).
  manuals  the manual collections (manuals/categories.py CATEGORIES): key, name, description, kind, licence and
           the heading the toolkit lists it under.

Nothing is downloaded and nothing is changed: it only imports the code and reads its tables.
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ("books", "packs", "kit", "manuals")


def inventory(part, timeout=600):
    """The JSON of one part, read by a separate Python process (see the module docstring). Raises RuntimeError with
    the program's last words when the part cannot be read."""
    if part not in PARTS:
        raise ValueError(f"unknown part {part}")
    out = subprocess.run([sys.executable, os.path.abspath(__file__), part], capture_output=True, text=True,
                         timeout=timeout, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError(f"the {part} code could not be read: {(out.stderr or out.stdout).strip()[-500:]}")
    return json.loads(out.stdout.strip().splitlines()[-1])


def first_line(text):
    """The first sentence or line of a description or docstring, in one line (at most 300 characters)."""
    text = " ".join((text or "").split())
    return text[:300]


# ====================================================================== the parts (run inside the small program)

def books():
    """The reference library's groups, books, not-built rows and keys (see the module docstring)."""
    sys.path.insert(0, os.path.join(ROOT, "textbooks"))
    import build_textbooks as B
    import more_refs
    import sources

    def kind_of(entry):
        """The licence class of a code entry (open, share-alike, personal use, link-only)."""
        lic = entry.get("licence", "")
        kind = ""
        for whole in (False, True):
            try:
                kind = kind or B.licence_kind(lic, whole) or B.licence_kind(B.licence_short(lic), whole)
            except Exception:  # noqa: BLE001 - an odd licence line: its class is worked out below
                pass
        if entry.get("link_only"):
            return "link-only"
        if entry.get("personal_use") or kind.startswith("non-commercial"):
            return "personal use"
        if kind == "share-alike":
            return "share-alike"
        if kind in ("open", "no-changes"):
            return "open"
        return "link-only" if not lic else "open" if "public domain" in lic.lower() else "unknown"

    entries = []

    def add(key, e, group=None):
        """One book the code lists."""
        entries.append({"key": key, "name": e.get("name", ""), "title": e.get("title", "") or key,
                        "description": first_line(e.get("description", "")),
                        "group": group or e.get("group", ""), "licence": e.get("licence", ""),
                        "class": kind_of(e)})

    for prefix, table in (("pdf", sources.PDF_DOCS), ("guide", sources.GOV_GUIDES), ("nonprofit", sources.NONPROFIT),
                          ("law", list(sources.LAWS) + list(sources.LAWS_MORE)), ("k12", sources.K12_GUIDES)):
        for e in table:
            add(f"{prefix}:{e['name']}", e, e.get("group") or {"law": "law", "k12": "k12",
                                                               "nonprofit": "nonprofit"}.get(prefix, ""))
    keys = list(sources.expand_keys(["all"]))
    for m in more_refs.modules():
        c = m.COLLECTION
        for name, e in list(c.guides.items()) + list(c.pdfs.items()):
            add(f"{c.prefix}:{name}", e, e.get("group") or c.group)
        try:
            own = c.own_keys()
        except Exception:  # noqa: BLE001 - a pieced maker that needs the network: only its listed keys
            own = [f"{c.prefix}:{n}" for n in list(c.guides) + list(c.pdfs)]
        listed = {f"{c.prefix}:{n}" for n in list(c.guides) + list(c.pdfs)}
        for key in own:
            if key not in listed:
                entries.append({"key": key, "name": key.split(":", 1)[1], "title": key, "description": "",
                                "group": c.group, "licence": "", "class": ""})
        keys += own
    not_included = [{"title": str(r[0]), "reason": first_line(str(r[1]))} for r in sources.NOT_INCLUDED
                    if isinstance(r, (list, tuple)) and len(r) >= 2]
    return {"groups": dict(sources.GROUPS), "books": entries, "not_included": not_included,
            "keys": list(dict.fromkeys(keys))}


def packs():
    """The picture packs: key, licence line and the first line of its builder's description."""
    sys.path.insert(0, os.path.join(ROOT, "packs"))
    import build_packs
    out = []
    for key, value in build_packs.PACKS.items():
        builder, licence = (value[0], value[1]) if isinstance(value, (tuple, list)) else (value, "")
        doc = getattr(builder, "__doc__", "") or ""
        out.append({"key": key, "licence": first_line(licence), "about": first_line(doc.split("\n\n")[0])})
    return {"packs": out}


def kit():
    """The training kit's topic add-ons and collections (see the module docstring)."""
    sys.path.insert(0, os.path.join(ROOT, "training-kit", "kit"))
    import sources
    import topics
    never = set(getattr(sources, "NOT_FOR_PICTURE_MAKING", ()))
    making_ok = set(getattr(sources, "PERSONAL_PICTURE_MAKING_OK", ()) or ())
    banned = set(getattr(sources, "PICTURE_MAKING_NEVER", ("intimate", "sexual", "graphic")))
    collections = {}
    for s in sources.SOURCES:
        ok = s.key not in never and getattr(s, "content", "") not in banned and \
            (getattr(s, "group", "") not in ("noncommercial", "research") or s.key in making_ok)
        collections[s.key] = {"key": s.key, "name": s.name, "group": s.group, "download": s.download,
                              "content": getattr(s, "content", ""), "picture_making": ok,
                              "licence": first_line(s.licence)}
    tops = [{"id": t.id, "title": t.title, "description": first_line(t.description), "keys": list(t.keys),
             "sensitive": t.sensitive, "personal_only": t.personal_only} for t in topics.TOPICS]
    return {"topics": tops, "collections": collections}


def manuals():
    """The manual collections by category (see the module docstring)."""
    sys.path.insert(0, os.path.join(ROOT, "manuals"))
    import categories
    out = []
    for key, c in categories.CATEGORIES.items():
        out.append({"key": key, "name": c.get("name", key), "description": first_line(c.get("description", "")),
                    "kind": c.get("kind", ""), "licence": c.get("licence", ""), "heading": c.get("heading", "")})
    return {"categories": out}


def main(argv=None):
    """The small program: print one part's JSON on the last line (anything the code prints itself comes before)."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] not in PARTS:
        print(f"Usage: python tools/library_inventory.py {'|'.join(PARTS)}", file=sys.stderr)
        return 2
    data = {"books": books, "packs": packs, "kit": kit, "manuals": manuals}[argv[0]]()
    sys.stdout.flush()
    print("\n" + json.dumps(data, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
