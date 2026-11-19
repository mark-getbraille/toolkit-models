"""PERSONAL-USE collection: pictures from US state digital libraries whose records give NO rights statement, or whose
rights words allow research, teaching or private study only, downloaded by the kit on the owner's own computer
(never in a ready-made pack, a release or CI). Also the list of the collections looked at and left out.

Why personal use: the open packs (packs/state_collections_packs.py) take only items whose own rights statement is
open (No Copyright - United States, No Known Copyright, the Public Domain Mark, CC0 or CC BY) with no restricting
words. The same libraries hold many well-described pictures with no statement at all ("rights" left empty), and some
whose words say "Online access is provided for research purposes only" (the Ohio History Connection's collections on
Ohio Memory) or "made available for use in research, teaching, and private study" (East Carolina University's digital
collections). Their robots.txt files allow the libraries' APIs, and their terms do not forbid reading them, so the
owner may use them on his own computer: group "research" (records with no stated terms or research-only terms,
SOURCE-RULES.md), so the kit uses them only with the personal-use research choice, and an add-on trained with them is
personal use only. Every row and every credit says which it is ("personal use only: no rights statement" or
"personal use only: research and private study").

The readers and the SAME RULES as the open packs come from the packs' own code (packs/state_collections_packs.py, found
beside the kit in a copy of the repository, or in the folder named by PICTURE_KIT_PACKS, as
princeton_personal_sources.pack_tools does; without it this collection is left out with a plain message): the
CONTENTdm server API and OAI-PMH readers, robots.txt obeyed (AI-crawler blocks and ai-train=no refused, Crawl-Delay
kept), and the screens (no nudity, crime, portraits of named people, camps and pupils, official events, slurs,
violence and atrocity, or American Indian and Indigenous material). Never used for picture-making.

    python state_collections_personal_sources.py [cap]      (a quick test: prints the rows, downloads no pictures)
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from sources import Source, fetch_pictures, say  # noqa: E402

KEY = "state_libraries_personal"
LABELS = {"none": "personal use only: no rights statement",
          "research": "personal use only: research and private study"}
PAUSE = 1.0                  # the CONTENTdm sites' Crawl-Delay
# OAI-PMH sites read for this entry: (base address, name, file-name prefix, the sets to read ("" for all)).
OAI_SITES = [("https://digital.lib.ecu.edu/oai", "East Carolina University Digital Collections", "ecu", ("c1",))]

# Looked at and NOT used, with the reason (checked on 19 November 2026; shown in the kit's list of left-out sources).
STATE_COLLECTIONS_NOT_INCLUDED = {
    "Indianapolis Museum of Art at Newfields": "public-domain images (no further permission needed) and CC0 metadata, "
        "but no official API, IIIF listing or bulk data: only the website's own search behind its pages. Not read; "
        "usable if Newfields publishes an API or a data download.",
    "Denver Art Museum": "CC0 open-access images, but no API or data download, and its robots.txt forbids the "
        "collection search pages (/en/search/collections?...). Not read.",
    "Dallas Museum of Art": "public-domain downloads, but the collection is a JavaScript site reading the museum's own "
        "search servers (no documented API or bulk data). Not read.",
    "Saint Louis Art Museum": "public-domain downloads under its terms, but its WordPress listing gives only titles "
        "and thumbnails (no rights or descriptions), and the object pages are web pages, not an API. Not read.",
    "Hammer Museum (UCLA)": "CC0 for public-domain images, but no API, IIIF listing or bulk data was found. Not read.",
    "DigitalNC (North Carolina Digital Heritage Center)": "answers automated readers with an empty bot-challenge page "
        "(202), its OAI-PMH address too. Not read.",
    "Connecticut Digital Archive": "a Cloudflare Turnstile challenge on every address, its OAI-PMH too. Not read.",
    "FIU dPanther": "an empty bot-challenge page (202). Not read.",
    "Montana Memory Project": "answered every request, the first one too, with 429 (too many requests); its old "
        "CONTENTdm API is gone. Not read.",
    "Mountain West Digital Library": "a Primo search portal with no open API (Ex Libris keys only); its members' own "
        "sites are read where they allow it (Washington State University).",
    "UF Digital Collections": "the old SobekCM OAI-PMH address now serves the new website, and its new API could not "
        "be reached (502). Not read.",
    "Utah State University Digital Library": "moved to Preservica (libraryusu.access.preservica.com); not explored.",
    "New York Heritage, Tennessee Virtual Archive, Missouri Digital Heritage": "CONTENTdm sites hosted by OCLC "
        "(*.contentdm.oclc.org): their API answered on 19 November 2026 at first, then with a Cloudflare challenge "
        "(403 'Just a moment'). Not read; the reader stops at any site that refuses three requests in a row.",
    "Illinois Digital Archives, Kentucky Digital Library, Auburn, Alabama Archives, New Mexico": "read by the open "
        "packs, but in November 2026 almost all of their collections said In Copyright, educational use only or "
        "permission needed: few or no items qualify (the reader finds any that do).",
}


def pack_tools():
    """packs/state_collections_packs.py, imported, or None when it is not on this computer (see the docstring)."""
    import importlib
    for folder in ("", os.environ.get("PICTURE_KIT_PACKS", ""), os.path.join(HERE, "..", "..", "packs")):
        if folder:
            if not os.path.isfile(os.path.join(folder, "state_collections_packs.py")):
                continue
            folder = os.path.abspath(folder)
            if folder not in sys.path:
                sys.path.append(folder)                 # appended, so it never hides the kit's own modules
        try:
            importlib.import_module("build_packs")      # loaded first, as the pack modules expect
            return importlib.import_module("state_collections_packs")
        except ImportError:
            continue
        except Exception:  # noqa: BLE001 - there, but not usable here
            return None
    return None


def candidate_rows(p, item, kind):
    """The rows of one personal-use candidate (p: the pack tools; item: a reader's candidate dict; kind: "none" or
    "research"), or [] when its words do not describe the picture. Each row carries the licence label."""
    label = LABELS[kind]
    answer = p.record_text(item["title"], [item["description"]] if item.get("description") else [])
    if not item.get("description") or not p.long_enough(answer, item["title"], name_ok=True):
        return []
    item = dict(item, answer=answer, credit=item["credit"].replace("{licence}", label))
    return [dict(row, licence=label) for row in p.item_rows(item)]


def oai_items(p, cap, s=None):
    """(name, url, rows) of the OAI_SITES records whose rights are research-only or absent, by the open packs'
    screens."""
    import requests
    if s is None:
        s = requests.Session()
        s.headers["User-Agent"] = p.USER_AGENT
    robots, out = p.RobotsGuard(s), []
    for base, name, prefix, sets in OAI_SITES:
        for set_spec in sets or ("",):
            for rec in p.oai_records(s, base, set_spec, most=cap * 3, robots=robots):
                item, rights = p.oai_candidate(rec, name, prefix)
                kind = p.rights_of(rights)[0]
                if kind not in LABELS or not item["url"] or p.why_left_out(item["words"], item["year"]) or \
                        robots.allowed(item["url"])[0]:
                    continue
                rows = candidate_rows(p, item, kind)
                if rows:
                    out.append((item["name"], item["url"], rows))
                if len(out) >= cap:
                    return out
    return out


def cdm_items(p, cap):
    """(name, url, rows) of the CONTENTdm sites' records with no rights statement or research-only words."""
    import random
    out, answers = [], set()
    sites = p.MIDWEST_SITES + p.SOUTH_SITES + p.WEST_SITES
    robots = p.RobotsGuard()
    share = max(10, cap // len(sites))
    for host, name, prefix in sites:
        site = p.ContentDM(host, name, robots=robots, prefix=prefix, pause=PAUSE)
        for kind in LABELS:
            try:
                found = p.cdm_site_items(site, share // 2, random.Random(f"{KEY}/{host}/{kind}"), KEY, answers,
                                         mode=kind)
            except Exception as error:  # noqa: BLE001 - one site down does not stop the collection
                say(f"    {name}: left out ({type(error).__name__})")
                found = []
            for item_name, url, item in found:
                rows = candidate_rows(p, item, kind)
                if rows and rows[0]["answer"] not in answers:      # the same words twice: one picture only
                    answers.add(rows[0]["answer"])
                    out.append((item_name, url, rows))
        if len(out) >= cap:
            break
    return out[:cap]


def state_items(cap):
    """(file name, picture address, row) for up to cap pictures, every row of a picture as its own item."""
    p = pack_tools()
    if p is None:
        raise RuntimeError("this collection needs the packs folder of the toolkit-models repository beside the kit "
                           "(or its folder in PICTURE_KIT_PACKS), for the same rules as the open packs")
    found = oai_items(p, max(5, cap // 5)) + cdm_items(p, cap)
    seen, out = set(), []
    for name, url, rows in found:
        if name in seen:
            continue
        seen.add(name)
        out += [(name, url, row) for row in rows]
        if len(seen) >= cap:
            break
    return out


def prepare_state(source, data_dir, work, cap):
    """The kit's prepare function: the pictures fetched (paced, two at a time) and made smaller into
    data_dir/<key>. Twin rows of one picture share its file."""
    items = state_items(cap)
    say(f"    State digital libraries (personal use): {len({n for n, _, _ in items})} pictures by the open packs' "
        f"rules.")
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


STATE_COLLECTIONS_SOURCES = [
    Source(KEY, "Towns, farms, buildings and daily life from US state digital libraries: items with no rights "
                "statement or research-only terms (personal use)",
           "No rights statement, or research and private study only, item by item: personal use only (the kit's "
           "research group)",
           "US state digital libraries (Ohio Memory, East Carolina University and the other CONTENTdm sites read by "
           "packs/state_collections_packs.py); each item credited in ATTRIBUTION.txt",
           "research", 1500, 15, prepare_state, "about 400 MB",
           terms="https://www.ohiohistory.org/research/archives-library/rights-reproductions/",
           terms_summary="Personal use only: these items give no rights statement, or allow research and private "
                         "study only."),
]
# Never used for picture-making.
STATE_COLLECTIONS_PICTURE_MAKING_OK = set()


def main(argv=None):
    """Quick test: the rows of a few pictures (no pictures downloaded)."""
    import json
    argv = list(sys.argv[1:] if argv is None else argv)
    cap = int(argv[0]) if argv else 6
    for name, url, row in state_items(cap):
        print(name, url, json.dumps(row, ensure_ascii=False)[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
