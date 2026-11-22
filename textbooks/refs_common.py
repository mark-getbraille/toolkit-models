"""Shared plumbing of the reference sources added on 2026-11-22 (the owner's request of that day): benefits manuals,
vehicle and product recalls, WordNet, and open computer-help documentation. Each source lives in its own module; this
module holds what they share and the ONE registry the builder, the weekly check and sources.py ask, so adding a
module needs no other change to those files.

In plain words:
  - REGISTRY says which module builds which build keys (by the word before the first ":", such as "ben" in
    "ben:poms:GN:1") and which request words stand for whole collections (such as "benefits");
  - readable() and api_readable() say whether a page or an official data service may be read (robots.txt and the
    AI-reader rules, directory_sources.ai_refused);
  - shallow_clone() makes a small copy of a public git repository (only the folders a book needs);
  - build_keys() builds the books of some keys and writes one manifest per key, as the builder does for its own
    keys: every book is a new version (versioned file name), with its key and the weekly check's fingerprint.

The builder (build_textbooks.build), the weekly check (updates.fingerprint) and sources.expand_keys call
module_for(), words() and records() here. Modules are imported only when they are needed, because they import the
builder, which imports sources, which imports this module.
"""

import importlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse

# The word before the first ":" of a build key -> the module that builds it. A module is listed here when it is added.
REGISTRY = {
    "ben": "benefits_manuals",       # SSA POMS, CMS manuals, the IRS Internal Revenue Manual
    "rcl": "recalls",                # NHTSA vehicle recalls and service bulletins, CPSC product recalls
    "dict": "wordnet_dict",          # Open English WordNet (dictionary and thesaurus)
}


def _module(name):
    """The module called name (imported the first time it is asked for)."""
    return importlib.import_module(name)


def module_for(key):
    """The module that builds key ("ben:poms:GN:1" -> benefits_manuals), or None when no module here builds it."""
    kind = key.split(":", 1)[0] if ":" in key else ""
    name = REGISTRY.get(kind)
    return _module(name) if name else None


def words(word):
    """The build keys a request word stands for when a module here knows it (its collection words, "group:<its
    group>", or one of its keys), else None."""
    for name in REGISTRY.values():
        mod = _module(name)
        keys = mod.expand_keys([word]) if mod.knows(word) else None
        if keys is not None:
            return keys
    return None


def records():
    """Every module's records for sources.py: (GROUPS, LICENCE_LINES, NOT_INCLUDED) of all of them together."""
    groups, lines, missing = {}, {}, []
    for name in REGISTRY.values():
        mod = _module(name)
        groups.update(mod.GROUPS)
        lines.update(mod.LICENCE_LINES)
        missing += list(mod.NOT_INCLUDED)
    return groups, lines, missing


# ====================================================================== reading rules

def readable(url, cache=None):
    """True when the builder may read url: robots.txt allows our reader and no AI-reader block or "ai-train=no"
    applies (directory_sources.ai_refused)."""
    import build_textbooks as B
    import directory_sources as D
    return B.allowed_by_robots(url, cache) and not D.ai_refused(url, cache)


def api_readable(url, cache=None):
    """True when the builder may call an agency's official data service at url. Its robots.txt is obeyed when the
    service has one; a service that answers "no such file" or refuses the robots.txt address itself (an API gateway
    or a firewall answering 403 for that one address) has no robots rules, and the robots.txt standard (RFC 9309,
    section 2.3.1.3) says such a site may be read. The AI-reader rules apply as everywhere."""
    import build_textbooks as B
    import directory_sources as D
    parts = urllib.parse.urlsplit(url)
    site = f"{parts.scheme}://{parts.netloc}"
    try:
        text = B.fetch(site + "/robots.txt", cache)
    except urllib.error.HTTPError as e:
        if 400 <= e.code < 500:
            return not D.ai_refused(url, cache)
        return False
    except (urllib.error.URLError, OSError):
        return False
    if re.search(r"<html\b", text[:2000], re.I):
        return not D.ai_refused(url, cache)        # a web page instead of a robots.txt: no rules
    return B.allowed_by_robots(url, cache) and not D.ai_refused(url, cache)


# ====================================================================== git repositories

def shallow_clone(repo, work, paths=None, ref=None):
    """A small copy of the public git repository repo ("https://github.com/owner/name") in work: only the newest
    commit (of ref, a tag or branch, when given), only the folders and files in paths (all when None). Returns the
    folder. GitHub allows cloning public repositories; one clone per build is all that is asked of it."""
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", repo.rstrip("/").split("/", 3)[-1]) + (f"@{ref}" if ref else "")
    dest = os.path.join(work, "git", name)
    if os.path.isdir(os.path.join(dest, ".git")):
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    cmd = ["git", "clone", "--quiet", "--depth", "1", "--filter=blob:none", "--no-checkout"]
    if ref:
        cmd += ["--branch", ref]
    subprocess.run(cmd + [repo, dest], check=True, env=env, timeout=1800)
    if paths:
        subprocess.run(["git", "-C", dest, "sparse-checkout", "set", "--no-cone"] + list(paths), check=True, env=env,
                       timeout=600)
    subprocess.run(["git", "-C", dest, "checkout", "--quiet"], check=True, env=env, timeout=3600)
    return dest


def git_facts(dest):
    """(commit, date "YYYY-MM-DD") of a clone's newest commit."""
    out = subprocess.run(["git", "-C", dest, "log", "-1", "--format=%H %cs"], capture_output=True, text=True,
                         timeout=60).stdout.split()
    return (out[0], out[1]) if len(out) == 2 else ("", "")


# ====================================================================== building

def build_keys(mod, keys, out_dir, cache=None, date=None, limit=None):
    """Build the books of keys (mod.expand_keys) with mod.books_for(key, work, cache, left_out, limit) (a list of
    Books) into out_dir, and write manifest-<key>.json for each key (as build_textbooks.build does); returns {key:
    manifest}. Every book is a new version (versioned file names, kept by updates.merge_versions). limit: a small
    test build (fewer pages; manifests named "..._sample", no fingerprint)."""
    import build_textbooks as B
    manifests = {}
    work = os.path.join(cache or out_dir, "work")
    os.makedirs(out_dir, exist_ok=True)
    for key in mod.expand_keys(keys):
        if module_for(key) is not mod:
            print(f"Not a key of {mod.__name__}: {key}; skipped.")
            continue
        left_out, entries = [], []
        fingerprint = "" if limit else mod.sign(key)
        try:
            books = mod.books_for(key, work, cache, left_out, limit) or []
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            books = []
        for book in books:
            if not book.pages:
                left_out.append({"title": book.title, "reason": "No pages could be read."})
                continue
            entry = B.write_book(book, out_dir, date, versioned=True)
            entry.update({"key": key, "fingerprint": fingerprint, "release": "textbooks"})
            print(f"{entry['file']}: {entry['article_count']} pages, {entry['size']:,} bytes, {entry['licence_text']}")
            entries.append(entry)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": "textbooks", "books": entries, "left_out": left_out,
                    "files": [e["file"] for e in entries], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if limit else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


def page_text(html_text):
    """The words of some HTML on one line (tags removed, entities read)."""
    import html
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", html_text or "")).split())
