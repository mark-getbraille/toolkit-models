"""Pack builders for GENERAL museum collections (any subject: landscapes, cityscapes, still lifes, everyday objects,
furniture, tools, clothing and textiles, ceramics, architecture, maps, scientific and natural-history pictures,
documentary and street photography), used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)].

Why: the owner widened the scope (November 2026): the describer should learn from any open work with a good
description, spread across departments and periods, not only nudes. The Met's other open collections were read only
for their highlights (the kit's "met" collection) and musical instruments (met_instruments); this pack reads the
rest, department by department.

The pack (MUSEUM_GENERAL_PACKS):
  met_collection  The Metropolitan Museum of Art: public-domain objects (isPublicDomain) of every department, the
                  same number from each (MET_DEPARTMENTS), "Tell me about this museum object." answered from the
                  record (title, kind, maker, date, material, culture) and its subject tags. Not here, so no picture is
                  in two packs: the Met's highlights (the kit's "met"), musical instruments (met_instruments), works
                  tagged or worded as nudes or erotica (art_nudes, museum_art_nudes, erotic_art,
                  nude_photo_studies: met_excluded). A record with no subject tags says only what it is called, not
                  what it shows: it is set aside for a description (build_packs.needs_description), not put in the
                  pack. The content rules of the open packs apply (archive_packs.not_shown: nothing sexual, no
                  torture or execution, no dead or injured child; graphic pictures marked; child rows marked).

Licence: CC0 (Met Open Access), each object's own isPublicDomain checked.

    python packs/museum_general_packs.py met_collection --limit 8      (prints a few rows: a quick check)
"""

import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, needs_description, pass_random
from body_packs import lead, made_in, NUDITY_WORDS, MINOR
from places import place_from_text, place_name
from service_packs import safety

MET = "https://collectionapi.metmuseum.org/public/collection/"
MUSEUM_QUESTION = "Tell me about this museum object."
# Every department but Musical Instruments (18: met_instruments) and The Libraries (16: books and papers).
MET_DEPARTMENTS = {1: "American Decorative Arts", 3: "Ancient West Asian Art", 4: "Arms and Armor",
                   5: "Arts of Africa, Oceania, and the Americas", 6: "Asian Art", 7: "The Cloisters",
                   8: "The Costume Institute", 9: "Drawings and Prints", 10: "Egyptian Art", 11: "European Paintings",
                   12: "European Sculpture and Decorative Arts", 13: "Greek and Roman Art", 14: "Islamic Art",
                   15: "The Robert Lehman Collection", 17: "Medieval Art", 19: "Photographs", 21: "Modern Art"}
# Subject tags that say nothing about what a picture shows.
EMPTY_TAGS = re.compile(r"^(men|women|man|woman|portraits?|abstraction|figures?|decorative arts)$", re.I)
# Nudes and erotica belong to the nude and erotic packs (their words, as adult_art_packs reads them).
NOT_HERE = re.compile(r"\b(nude\w*|naked|nudity|erotic\w*|shunga|sex\w*|lovers|odalisque|bathers?|courtesans?)\b",
                      re.I)


def get_json(s, url, params=None):
    """A JSON answer, tried again on a passing error; None when it cannot be had."""
    for attempt in range(3):
        try:
            r = s.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (403, 404):
                return None
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(2 * (attempt + 1))
    return None


def met_department_ids(s, department, most):
    """Object ids (with images) of one Met department, up to most (the v1.1 search, paged)."""
    ids, offset = [], 0
    while len(ids) < most:
        page = get_json(s, MET + "v1.1/search", params={"q": "*", "departmentId": department, "hasImages": "true",
                                                        "limit": 100, "offset": offset}) or {}
        found = page.get("objectIDs") or []
        ids += found
        offset += len(found)
        if not found or offset >= (page.get("total") or 0):
            break
        time.sleep(0.2)
    return ids[:most]


def met_excluded(o):
    """Why a Met object is not for met_collection ("" when it is): a highlight, a musical instrument, a nude or
    erotica (their own packs), not public domain or no picture."""
    tags = " ".join(t.get("term", "") for t in (o.get("tags") or []))
    words = f"{o.get('title')} {o.get('objectName')} {tags}"
    if not o.get("isPublicDomain") or not (o.get("primaryImage") or o.get("primaryImageSmall")):
        return "not public domain, or no picture"
    if o.get("isHighlight"):
        return "a highlight (the kit's met collection)"
    if o.get("department") == "Musical Instruments":
        return "a musical instrument (met_instruments)"
    if NOT_HERE.search(words) or NUDITY_WORDS.search(words) or "Nudes" in tags:
        return "a nude or erotica (the nude and erotic packs)"
    return ""


def met_rows(o):
    """(rows, described) of one Met object: "Tell me about this museum object." from the record and its subject
    tags; described is False when the record has no subject tags (it then only names the object)."""
    title = clean(o.get("title"))
    artist = clean(o.get("artistDisplayName"))
    answer = lead(title, o.get("objectName"), artist, o.get("objectDate"), o.get("medium"))
    culture = clean(o.get("culture") or o.get("period") or o.get("dynasty"))
    if culture and culture.lower() not in answer.lower():
        answer += f" It is {culture}."
    tags = [t.get("term", "") for t in (o.get("tags") or []) if t.get("term") and not EMPTY_TAGS.match(t["term"])]
    if tags:
        answer += " The museum lists these subjects: " + ", ".join(t.lower() for t in tags[:8]) + "."
    credit = f"The Metropolitan Museum of Art, public domain (CC0): {title}" + (f", {artist}" if artist else "") + \
        f", {o.get('objectURL', '')}"
    rows = [{"question": MUSEUM_QUESTION, "answer": answer, "credit": credit}]
    if o.get("geographyType") in ("", "Made in", "From"):
        rows = made_in(rows, place_from_text(place_name(o.get("city"), o.get("country"))))
    return rows, bool(tags)


def met_collection_items(want, s=None):
    """(name, picture address, rows) for met_collection: the same number from each department."""
    s = s or session()
    rng = pass_random(7311)
    per = max(2, want // len(MET_DEPARTMENTS) + 1)
    items = []
    for department, name in MET_DEPARTMENTS.items():
        ids = met_department_ids(s, department, 4000)
        rng.shuffle(ids)
        found = 0
        for oid in ids[:per * 4]:
            if found >= per or build_packs.listing_out_of_time():
                break
            time.sleep(0.1)
            o = get_json(s, f"{MET}v1/objects/{oid}") or {}
            if met_excluded(o):
                continue
            rows, described = met_rows(o)
            keep, marks = safety([r["answer"] for r in rows])
            if not keep:
                continue
            if MINOR.search(" ".join(r["answer"] for r in rows)):
                marks["child"] = True             # the wide young-person words (putti, Madonna and Child ...)
            rows = [dict(r, **marks) for r in rows]
            picture = o.get("primaryImage") or o.get("primaryImageSmall")
            file = f"met-{oid}.jpg"
            if not described:
                needs_description(file, picture, rows[0]["credit"], "CC0", "open", text=rows[0]["answer"],
                                  title=clean(o.get("title")), reason="its record has no subject tags: it names the "
                                  "object but does not say what it shows", page_url=o.get("objectURL", ""),
                                  extra={"department": name, **marks})
                continue
            items.append((file, picture, rows))
            found += 1
        say(f"  Met {name}: {found} usable")
    return items


def build_met_collection(limit):
    """The met_collection pack (see the module docstring)."""
    from archive_packs import finish_marked
    return finish_marked("met_collection", met_collection_items(int(limit * 1.2) + 2), limit, workers=4, pause=0.2)


MUSEUM_GENERAL_PACKS = {
    "met_collection": (build_met_collection,
                       "The Metropolitan Museum of Art, Open Access (CC0, https://www.metmuseum.org/about-the-met/"
                       "policies-and-documents/open-access): public-domain objects of every department, each credited "
                       "below; the museum's highlights, musical instruments, nudes and erotica are in other packs."),
}
MUSEUM_GENERAL_LIMITS = {
    "met_collection": 6000,        # 17 departments, the same number from each (of about 490,000 open objects)
}


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a general museum pack builder.")
    parser.add_argument("key", choices=sorted(MUSEUM_GENERAL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = MUSEUM_GENERAL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:300])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
