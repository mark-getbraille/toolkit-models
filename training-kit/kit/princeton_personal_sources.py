"""PERSONAL-USE collection: the Princeton University Art Museum's nudes, figure studies and erotic art, downloaded by
the kit on the owner's own computer only (never in a ready-made pack, a release or CI).

Why personal use: the museum's data API (data.artmuseum.princeton.edu) and its IIIF manifests give NO rights
statement on the record ("restrictions: None" is not public domain or CC0), so its pictures cannot go into the open
packs. The owner chose (November 2026) to use them for personal use only: group "research" (records with no stated
terms, SOURCE-RULES.md), so the kit uses them only with the personal-use research choice (--personal-research and
--accept-research-terms; the program's personal-use switch), and an add-on trained with them is personal use only.
Every row and every credit says "personal use only: no rights statement".

Only the museum's data API and its image server are read (its website is behind a Cloudflare challenge and is
never touched; neither host has a robots.txt that forbids this), with a pause between requests (PAUSE).

The SAME RULES as the open packs, by the packs' own code (packs/adult_art_packs.py, found beside the kit in a copy of
the repository, or in the folder named by PICTURE_KIT_PACKS, as uxo_personal_sources.figure_tools does; without it
this collection is left out with a plain message):
  - non-sexual nudes and academic studies: museum_art_nudes's rules (adult_art_packs.nude_candidate: no photograph,
    nothing sexual, no sexual violence, no death or torture, the child rules; rows "content" none beyond the
    collection's "nudity");
  - sexual works: erotic_art's rules (erotic_left_out: sexual first, the young-person screen, incest, harm, animals,
    no photographs; girl or boy alone goes to the review route and only the allow-list lets it in); rows "content":
    "sexual" (used only with the adult-sexual-content choice) and their "theme";
  - photographs: nude_photo_studies's rules (nude_photo_left_out: a record that describes an adult, nothing sexual,
    no young person, group or family).
Never used for picture-making (sources.NOT_FOR_PICTURE_MAKING).

    python princeton_personal_sources.py <folder> [cap]      (a quick test: prints the rows, downloads nothing)
"""

import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from sources import Source, fetch_pictures, say, USER_AGENT  # noqa: E402

KEY = "princeton_art_personal"
API = "https://data.artmuseum.princeton.edu/search"
PAUSE = 0.5
LABEL = "personal use only: no rights statement"
TERMS = "https://artmuseum.princeton.edu/about/open-access"
QUERIES = ("nude", "naked", "academy figure", "académie", "life study", "figure study", "écorché", "bather",
           "erotic", "shunga", "lovers", "odalisque", "torso", "Venus")
SIDE = 1200                        # pixels asked of the IIIF server (the kit makes its own smaller copy)


def pack_tools():
    """packs/adult_art_packs.py, imported, or None when it is not on this computer (see the module docstring)."""
    import importlib
    for folder in ("", os.environ.get("PICTURE_KIT_PACKS", ""), os.path.join(HERE, "..", "..", "packs")):
        if folder:
            if not os.path.isfile(os.path.join(folder, "adult_art_packs.py")):
                continue
            folder = os.path.abspath(folder)
            if folder not in sys.path:
                sys.path.append(folder)                 # appended, so it never hides the kit's own modules
        try:
            importlib.import_module("build_packs")      # loaded first, as the pack modules expect
            return importlib.import_module("adult_art_packs")
        except ImportError:
            continue
        except Exception:  # noqa: BLE001 - there, but not usable here
            return None
    return None


def search(s, query, most=500, pause=PAUSE):
    """The search hits (their _source) of the museum's data API for one query."""
    time.sleep(pause)
    try:
        r = s.get(API, params={"q": query, "type": "artobjects", "size": most}, timeout=60)
        hits = (r.json().get("hits") or {}).get("hits") or [] if r.status_code == 200 else []
    except Exception:  # noqa: BLE001 - the next query
        hits = []
    return [h.get("_source") or {} for h in hits]


def first(value):
    """The first item of a list (or the value), as text."""
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value or "").strip()


OBJECT = "https://data.artmuseum.princeton.edu/objects/"


def full_record(s, r, pause=PAUSE):
    """The search hit with its object's own record merged in (the search gives no classification, so a photograph
    could not be told from a drawing without it); the hit alone when the record cannot be read."""
    if r.get("classification") or not s:
        return r
    time.sleep(pause)
    try:
        got = s.get(OBJECT + str(r.get("objectid")), timeout=60)
        extra = got.json() if got.status_code == 200 else {}
    except Exception:  # noqa: BLE001 - the hit alone
        extra = {}
    return {**r, **{k: v for k, v in extra.items() if v not in (None, "", [])}} if isinstance(extra, dict) else r


def record_rows(a, r, s=None, pause=PAUSE):
    """(file name, picture address, rows) of one Princeton search hit by the open packs' rules (a: the pack tools;
    s: a session to read the object's own record), or None. Rows carry the licence label; sexual works "content":
    "sexual". A work whose kind is still not known is left out (it could be a photograph)."""
    title = a.clean(r.get("displaytitle"))
    oid = str(r.get("objectid") or "")
    picture = first(r.get("primaryimage"))
    if not title or not oid or not picture.startswith("https://media.artmuseum.princeton.edu/iiif/"):
        return None
    r = full_record(s, r, pause)
    if not a.clean(r.get("classification") or r.get("type")):
        return None
    if str(r.get("nowebuse")).lower() == "true":
        return None                                       # the museum asks that it not be shown on the web
    kind = a.clean(r.get("classification") or r.get("type"))
    medium = a.clean(r.get("medium"))
    medium = "" if medium.lower() in ("unknown", "none") else medium
    maker = a.clean(r.get("displaymaker"))
    maker = "" if maker in ("None", "none") else maker
    when = a.clean(r.get("displaydate"))
    text = a.clean(r.get("caption") or r.get("description") or "")
    credit = f"Princeton University Art Museum, {LABEL}: {title}" + (f", {maker}" if maker else "") + \
        f", https://artmuseum.princeton.edu/art/collection/object/{oid}"
    name = f"princeton-{re.sub(r'[^\w-]', '_', oid)}.jpg"
    url = f"{picture}/full/!{SIDE},{SIDE}/0/default.jpg"
    kind_text = f"{kind} {medium}"
    if a.PHOTO_WORDS.search(kind_text):
        if a.nude_photo_left_out(title, text, kind=kind_text):
            return None
        rows = a.nude_photo_rows(title, credit)
    else:
        why = a.erotic_left_out(text, medium, kind=kind_text, title=title)
        if a.reviewed(why, "Princeton University Art Museum", oid, title,
                      f"https://artmuseum.princeton.edu/art/collection/object/{oid}"):
            why = ""
        if not why:
            rows = a.erotic_rows(credit, title, kind, maker, when, medium, text, (), "museum")
        elif why == a.NOT_SEXUAL:
            item = a.nude_candidate("Princeton", name, url, title, credit, kind, maker, when, medium, text)
            if not item:
                return None
            rows = item[2]
        else:
            return None
    return name, url, [dict(row, licence=LABEL) for row in rows]


def princeton_items(cap, s=None, a=None, pause=PAUSE):
    """(file name, picture address, row) for up to cap Princeton works by the open packs' rules."""
    import requests
    a = a or pack_tools()
    if a is None:
        raise RuntimeError("this collection needs the packs folder of the toolkit-models repository beside the kit "
                           "(or its folder in PICTURE_KIT_PACKS), for the same rules as the open packs")
    if s is None:
        s = requests.Session()
        s.headers["User-Agent"] = USER_AGENT
    items, seen = [], set()
    for q in QUERIES:
        for r in search(s, q, pause=pause):
            oid = str(r.get("objectid") or "")
            if not oid or oid in seen:
                continue
            seen.add(oid)
            got = record_rows(a, r, s, pause)
            if got:
                name, url, rows = got
                items += [(name, url, row) for row in rows]
        if len({n for n, _, _ in items}) >= cap:
            break
    names = list(dict.fromkeys(n for n, _, _ in items))[:cap]
    return [i for i in items if i[0] in set(names)]


def prepare_princeton(source, data_dir, work, cap):
    """The kit's prepare function: Princeton works by the open packs' rules, their pictures fetched (paced) and made
    smaller into data_dir/<key>. Twin rows of one picture share its file."""
    items = princeton_items(cap)
    say(f"    Princeton University Art Museum: {len({n for n, _, _ in items})} works by the open packs' rules.")
    folder = os.path.join(data_dir, source.key)
    first_rows = {}
    for name, url, row in items:
        first_rows.setdefault(name, (name, url, dict(row, split="")))
    fetched = {r["picture"]: r for r in fetch_pictures(list(first_rows.values()), folder, workers=2, pause=PAUSE)}
    out = []
    for name, url, row in items:
        path = os.path.join(folder, name)
        if path in fetched:
            out.append(dict(row, picture=path, split=""))
    return out


PRINCETON_SOURCES = [
    Source(KEY, "Princeton University Art Museum: nudes, figure studies and erotic art (personal use: no rights "
                "statement)",
           "No rights statement on the museum's records: personal use only (the kit's research group)",
           f"Princeton University Art Museum, {LABEL}; each work credited in ATTRIBUTION.txt",
           "research", 600, 10, prepare_princeton, "about 150 MB", content="nudity", terms=TERMS,
           terms_summary="Personal use only: the museum's records give no rights statement for their pictures."),
]
# Never used for picture-making.
PRINCETON_PICTURE_MAKING_OK = set()


def main(argv=None):
    """Quick test: the rows of a few works (no pictures downloaded)."""
    import json
    argv = list(sys.argv[1:] if argv is None else argv)
    cap = int(argv[1]) if len(argv) > 1 else 8
    for name, url, row in princeton_items(cap):
        print(name, json.dumps(row, ensure_ascii=False)[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
