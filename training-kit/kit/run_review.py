"""Download review collections into review workspaces (started by kit\\run_review.cmd, which the program's "Review
collections" window runs in the kit's own Python).

    python run_review.py --library "D:\\Picture Library" cdc_phil_intimate fitzpatrick17k ...

    python run_review.py --library "D:\\Picture Library" --source "D:\\Their pictures.zip" some_permission_key

Each collection named (a key of review_sources.REVIEW_SOURCES, adult_review_sources.ADULT_REVIEW_SOURCES or
permission_sources.PERMISSION_SOURCES) is
downloaded into <library>\\Review\\<key>, a "Describe pictures" workspace whose describing.json says
"review_only": true, by the collection's own fetch function (which skips pictures it has already tried, so a
stopped run carries on). Nothing there is trained on until a trusted sighted adult has marked a picture "checked"
(own_data.py). One collection failing never stops the others.
A permission collection (category "permission": an organisation must agree first) is downloaded only when
permission_sources.permission_on_file(library, key) says their permission is on file (their reply in
<library>\\Permissions\\<key>). With --source (a folder or zip the organisation sent), its fetch function adds
those pictures instead (fetch(folder, cap, say, source=path)); only one collection may be named then.

Every line it prints is plain English for the screen reader: "Collection 1 of 3: ...", each collection's summary,
and "Finished: ..." at the end (or "STOPPED: ..." when nothing could be done).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REVIEW_FOLDER = "Review"        # the review workspaces' folder inside the picture library


def say(text=""):
    """Print one line at once (the program reads the lines as they come)."""
    print(text, flush=True)


def all_sources():
    """({key: collection dict} of every review collection the kit has, [plain notes about lists that could not be
    loaded]). The adult list may be missing or unfinished: then only the other list is offered."""
    found, notes = {}, []
    for module_name, list_name in (("review_sources", "REVIEW_SOURCES"),
                                   ("adult_review_sources", "ADULT_REVIEW_SOURCES"),
                                   ("permission_sources", "PERMISSION_SOURCES")):
        try:
            module = __import__(module_name)
            for item in getattr(module, list_name, []) or []:
                if isinstance(item, dict) and item.get("key") and callable(item.get("fetch")):
                    found[item["key"]] = dict(item, _permission=getattr(module, "permission_on_file", None))
        except ModuleNotFoundError as e:
            if not (e.name == module_name == "permission_sources"):      # that list may simply not be there yet
                notes.append(f"The list {module_name}.py could not be loaded ({e}); its collections are left out.")
        except Exception as e:  # noqa: BLE001 - said in plain words; the other list still works
            notes.append(f"The list {module_name}.py could not be loaded ({str(e).splitlines()[0][:150]}); its "
                         "collections are left out.")
    return found, notes


def permission_on_file(item, library):
    """True for a collection that needs no permission, or whose permission is on file; False otherwise (also when
    the check cannot be made)."""
    if item.get("category") != "permission":
        return True
    try:
        return bool(item.get("_permission") and item["_permission"](library, item["key"]))
    except Exception:  # noqa: BLE001 - not on file then
        return False


def mark_review(folder, item):
    """Make sure the workspace in folder is marked review-only with the collection's content and category (the
    fetch functions do this themselves; this is a second safety)."""
    import describe_package as dp
    if not dp.is_workspace(folder):
        return
    workspace = dp.open_workspace(folder)
    data = workspace.data
    data["review_only"] = True
    data.setdefault("content", item.get("content", ""))
    data.setdefault("review_source", item["key"])
    data.setdefault("review_category", item.get("category", ""))
    workspace.save()


def main(argv=None):
    """Download each named collection into its review workspace (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--library", required=True, help="the picture library folder")
    parser.add_argument("--source", default="", help="a folder or zip an organisation sent (one permission "
                        "collection)")
    parser.add_argument("keys", nargs="+", help="the review collections to download")
    args = parser.parse_args(argv)
    if args.source and len(args.keys) != 1:
        say("STOPPED: what an organisation sent can be imported into one collection at a time.")
        return 1
    sources, notes = all_sources()
    for note in notes:
        say(note)
    for key in [k for k in args.keys if k in sources and not permission_on_file(sources[k], args.library)]:
        say(f"The review collection {key} is waiting for permission: put their reply in "
            f"{os.path.join(args.library, 'Permissions', key)} first. It is left out.")
    wanted = [k for k in args.keys if k in sources and permission_on_file(sources[k], args.library)]
    for key in args.keys:
        if key not in sources:
            say(f"The review collection {key} is not in this kit; it is left out.")
    if not wanted:
        say("STOPPED: none of the chosen review collections can be downloaded with this kit.")
        return 1
    done = 0
    for number, key in enumerate(wanted, 1):
        item = sources[key]
        folder = os.path.join(args.library, REVIEW_FOLDER, key)
        name = item.get("name") or item.get("organisation") or key
        say(f"Collection {number} of {len(wanted)}: {name} (downloads {item.get('download', 'some')}), "
            f"into {folder}.")
        try:
            os.makedirs(folder, exist_ok=True)
            if args.source:
                summary = item["fetch"](folder, item.get("cap") or 0, say, source=args.source)
            else:
                summary = item["fetch"](folder, item.get("cap") or 0, say)
            mark_review(folder, item)
            say(f"Done: {summary}")
            done += 1
        except Exception as e:  # noqa: BLE001 - one collection failing never stops the others
            say(f"  This collection could not be downloaded now ({str(e).splitlines()[0][:200] if str(e) else e!r});"
                " it is left out. Try again later: it carries on where it stopped.")
            try:
                mark_review(folder, item)
            except Exception:  # noqa: BLE001 - nothing more to do
                pass
    say(f"Finished: {done} of {len(wanted)} review collection{'s' if len(wanted) != 1 else ''} downloaded. Nothing is "
        "trained on until a trusted sighted adult has looked at each picture and marked it checked.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say("STOPPED by you. Start it again to carry on where it stopped.")
        sys.exit(1)
