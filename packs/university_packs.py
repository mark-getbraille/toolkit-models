"""Pack builders for COLLEGE AND UNIVERSITY photo collections of the United States and Canada: campus life (students
at work and at play, adults only by the words of each record), libraries, laboratories, classrooms, sports, campus
buildings, college towns, farms and experiment stations, and the everyday life of earlier decades that university
libraries put online with no known copyright. Used by build_packs.py in the same way as its own PACKS: each builder
is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"}, plus "place" where the record names one, "facts" (the holding library, the year, the subjects), "child":
true where the words of a picture name a child, and "content": "graphic" where they name the dead or injured. A
picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file"
names the same picture (food_packs.with_twins). The limit counts pictures.

Every answer is the institution's own words or a fixed sentence: "Describe this picture." with the record's own title
and description (catalogue fields, persistent addresses, credit lines and web addresses taken out), "Where was this
photo taken?" when the record names the place, and "Who took this photo?" for a college's own photo stream. Nothing
is written by an AI model and nothing is guessed. A picture that passes every check but whose words are too short to
describe it (under six English words, or only the file name or a number) is set aside for a description
(build_packs.needs_description), keeping its marks.

Safety and privacy (packs/SOURCE-RULES.md): no sexual content, swimwear or underwear; no crime, arrests, prisons,
evidence photos, mugshots or victims; no yearbook portraits, head shots, class or team portraits, student records,
transcripts or rosters (privacy); no summer camps, youth programmes or school pupils on campus (minors whose age the
record does not give); official events (trustees, donors, award ceremonies, ribbon cuttings, politicians) left out,
as in us_modern_packs; photos whose words name the dead or injured marked "content": "graphic" (and a dead or
injured child left out); every row whose words name a child marked "child". All three packs show people and are
never used for picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS).

The packs (all open; every licence checked at the source in November 2026):
  dpla_campus              The Digital Public Library of America (DPLA, https://dp.la): items from US college and
                           university libraries (DPLA's data provider is a university, college or institute: the
                           Portal to Texas History (UNT), Calisphere's UC campuses and USC, the Mountain West Digital
                           Library's Utah universities, Ohio, Minnesota, Wisconsin, Illinois, Indiana, Michigan,
                           Pennsylvania, North Carolina, Washington and Oregon hubs ...), image items only, found by
                           everyday words (campus, students, library, laboratory, farm, main street ...), whose
                           rights URI is open: No Copyright - United States (rightsstatements.org NoC-US), the Public
                           Domain Mark, CC0 or CC BY. The rights URI comes from DPLA's own "rights" field (each
                           item's), so items under other statements are never taken (their CC BY-SA and CC BY-NC
                           items are the kit's entries in university_sources.py). DPLA metadata is CC0 ("DPLA ...
                           dedicates all Metadata to the public domain pursuant to the CC0", dp.la/about/terms-
                           conditions). Pictures: the item's full-size file (DPLA's "mediaMaster"), its IIIF image
                           (from the item's IIIF manifest, or the CONTENTdm IIIF address made from a CONTENTdm
                           thumbnail's address); an item with only a small thumbnail is left out. Needs the free DPLA
                           API key in the environment variable DPLA_API_KEY (a GitHub secret of the same name in the
                           packs workflow); without it the builder says so and makes nothing. Items from state
                           archives and state libraries are left to state_packs.py (only college and university data
                           providers are taken here).
  commons_college_streams  Wikimedia Commons copies of colleges' own Flickr photo streams, each file's own licence
                           checked (public domain, CC0 or CC BY; never share-alike, non-commercial or no-derivatives)
                           and its author line checked to name the college: College of DuPage (Illinois, about 7,000
                           files, CC BY 2.0), Germanna Community College (Virginia, about 4,300, CC BY 2.0), Community
                           College of Vermont (about 2,700, CC BY 2.0), Texas A&M University-Commerce Marketing
                           Communications (about 1,500, CC BY 2.0), Roanoke College (Virginia, about 200, CC BY 2.0),
                           Union College (about 90, public domain mark), the University of Louisville (about 70,
                           public domain mark), the University of Michigan School for Environment and Sustainability
                           (event subcategories) and the University of the District of Columbia law school (its CC BY
                           files). Only photos of 1990 or later. Flickr itself is never used (its API terms forbid
                           storing photos). The streams of Texas Tech student housing, Texas A&M's Memorial Student
                           Center and university pictures, the Colorado School of Mines and Oregon State University
                           are in state_packs.commons_state_community and are not repeated here.
  commons_university_archives  Commons copies of university libraries' digitized photographs marked "No known
                           copyright restrictions" or public domain (Flickr Commons and the libraries' own uploads),
                           with each library's catalogue description: the University of Washington Libraries Digital
                           Collections (Seattle and Washington State, about 650), Miami University Libraries (Oxford,
                           Ohio: campus, sports, the Snyder photographs of Ohio life, about 6,800; its "Group
                           Portraits" and "Fraternities & Sororities" subcategories left out), the University of
                           Alberta Library (Peel's Prairie Provinces postcards of the Prairies, about 330) and Southern
                           Methodist University's Central University Libraries (Dallas, Texas, and stereographs of
                           everyday life, about 4,500). Earlier decades (about 1860-1960): these are the openly
                           marked everyday-life photographs of these libraries that no other pack takes (the Library
                           of Congress, the National Archives and the state archives are elsewhere).

Looked at and not made into packs here (the reasons, and the non-open entries, are in
training-kit/kit/university_sources.py: UNIVERSITY_SOURCES, UNIVERSITY_SIGN_UP, UNIVERSITY_PERMISSION and
UNIVERSITY_NOT_INCLUDED).

    python packs/university_packs.py commons_college_streams --limit 8      (prints a few rows: a quick check)
"""

import json
import math
import os
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from build_packs import first_sentences, fetch_all, new_only
from food_packs import with_twins, count_pictures, commons_get, sentence
from home_packs import commons_fetch, file_name, NUDE
from expression_packs import mark_child, CHILD
from mechanical_packs import MECH_FREE, NOT_A_PHOTO, in_english
from us_packs import NOT_SHOWN, DESCRIBE_Q
from us_modern_packs import (agency_caption, sample_members, only_the_name, photo_year, NOT_MODERN, OFFICIAL,
                             GRAPHIC)
from places import place_name, country_named, where

WHO_Q = "Who took this photo?"
WHERE_Q = "Where was this photo taken?"
WORDS = 6                       # an answer of fewer words is not a description (set aside instead)

# ----------------------------------------------------------------- the shared word checks

# Crime, prisons and victims: never taken (as state_packs.CRIME).
CRIME = re.compile(r"\b(arrest\w*|suspects?|inmates?|prisons?|prisoners?|jail\w*|penitentiar\w*|correctional|"
                   r"crimes?|criminal|homicides?|murder\w*|shootings?|gunman|victims?|mug ?shots?|evidence|"
                   r"autops\w*|overdos\w*|lynch\w*|execut\w*|electric chair|gallows|hanging)\b", re.I)
# Privacy: portraits of named students and staff, yearbooks and records are not everyday scenes.
PRIVATE = re.compile(r"\b(portraits?|head ?shots?|yearbooks?|class (photo|picture|portrait)s?|team (photo|picture|"
                     r"portrait)s?|group (photo|portrait|shot)s?|composites?|id cards?|student records?|"
                     r"transcripts?|rosters?|report cards?|grade (book|sheet)s?|enrollment records?|"
                     r"passport photos?)\b", re.I)
# Minors on campus whose age is not given: camps, youth programmes, school pupils and visits.
MINORS = re.compile(r"\b(camps?|campers?|youth|high schools?|middle schools?|elementary|grade school|junior high|"
                    r"k-12|4-h|scouts?|cub|brownies|summer program\w*|kids? (college|day|camp)|"
                    r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)[- ]grad\w*|"
                    r"\d+(st|nd|rd|th) grad\w*|preschool\w*|day ?care|child ?care|orphan\w*)\b", re.I)
# College official events (as us_modern_packs.OFFICIAL, plus the campus words): not everyday life.
CAMPUS_OFFICIAL = re.compile(r"\b(trustees?|regents?|board of (visitors|governors)|donors?|philanthropist\w*|"
                             r"foundation (honors|gala|dinner|luncheon)|gala|banquet|luncheon|fundrais\w*|"
                             r"ribbon[- ]cutting|groundbreaking|ground[- ]breaking|dedication ceremony|"
                             r"inaugurat\w*|investiture|retirement (party|reception)|reception for|honorary degree|"
                             r"president's (dinner|reception)|legislat\w*|lawmakers?|senator|congress\w*|"
                             r"governor|mayor|candidates?|campaign|debate watch|induction)\b", re.I)
# Words that a description must not have, beyond the shared ones (us_packs.NOT_SHOWN, home_packs.NUDE).
SWIMWEAR = re.compile(r"\b(bathing (suit|beaut)\w*|swimsuits?|beauty (contest|pageant|queen)s?|pageants?|"
                      r"miss [A-Z]\w+)\b", re.I)
# Old slurs in some early captions: such captions are left out rather than repeated.
SLURS = re.compile(r"\b(japs?|nips?|niggers?|negro(es)?|coloreds?|squaws?|redskins?|savages?|half-?breeds?|"
                   r"pickaninn\w*|darkies|coons?|mammy|chinks?|eskimos?)\b", re.I)


def left_out_because(words, year=0, modern=True):
    """Why a picture is left out by its words and date ("" when it may be taken): nudity, swimwear or beauty
    contests; crime, prisons or victims; a portrait or record of a person (privacy); a camp, youth programme or school
    pupils (minors whose age is not given); an official event; an old slur; and (modern) a photo older than 1990."""
    if NUDE.search(words) or NOT_SHOWN.search(words) or SWIMWEAR.search(words):
        return "its words are about nudity, swimwear, a beauty contest or evidence photos"
    if CRIME.search(words):
        return "its words are about crime, prison, an execution or a victim"
    if PRIVATE.search(words):
        return "a portrait, yearbook, team or class photo, or a record about a person (privacy)"
    if MINORS.search(words):
        return "a camp, youth programme or school pupils (minors whose age the record does not give)"
    if OFFICIAL.search(words) or CAMPUS_OFFICIAL.search(words):
        return "an official event (trustees, donors, ceremonies, politicians), not everyday life"
    if SLURS.search(words):
        return "its words hold an old slur"
    if GRAPHIC.search(words) and CHILD.search(words):
        return "its words name a dead or injured child"
    if modern and ((year and year < 1990) or NOT_MODERN.search(words)):
        return "older than 1990 (by its date or words): this pack is about 1990 onwards"
    return ""


def marked(rows, words):
    """Rows marked "child" when words name a child and "content": "graphic" when they name the dead or injured."""
    rows = [mark_child(r, words) for r in rows]
    if GRAPHIC.search(words):
        rows = [dict(r, content="graphic") for r in rows]
    return rows


def long_enough(text, title=""):
    """True when an answer is real English of at least WORDS words, says more than the file's name, and says what is
    in the picture rather than only names and dates: at least three ordinary lower-case words ("Wade Henderson and
    Stephen B. Bright." and "Community College of Vermont Commencement 2024." are not descriptions)."""
    ordinary = [w for w in re.findall(r"[A-Za-z]+", text or "") if w.islower() and len(w) > 2]
    return bool(text) and len(text.split()) >= WORDS and len(ordinary) >= 3 and in_english(text) and \
        not only_the_name(text, title)


# ----------------------------------------------------------------- DPLA (college and university data providers)

DPLA = "https://api.dp.la/v2/items"
DPLA_TERMS = "https://dp.la/about/terms-conditions"
# The rights URIs that make an item open (DPLA's "rights" field, as the item's institution gave it).
DPLA_OPEN = re.compile(r"^https?://(rightsstatements\.org/(vocab|page)/NoC-US/|creativecommons\.org/publicdomain/"
                       r"(mark|zero)/|creativecommons\.org/licenses/by/)", re.I)
DPLA_RIGHTS_NAMES = (("NoC-US", "No Copyright - United States (rightsstatements.org)"),
                     ("publicdomain/mark", "Public Domain Mark"), ("publicdomain/zero", "CC0"),
                     ("licenses/by/", "CC BY"))
# A data provider that is a college or university (state archives and libraries are left to state_packs.py).
UNIVERSITY = re.compile(r"\b(universit(y|ies|é)|college|institute of technology|polytechnic|school of mines|"
                        r"seminary)\b", re.I)
NOT_UNIVERSITY = re.compile(r"\b(state (library|archives)|public library|historical society|museum)\b", re.I)
# The everyday words DPLA is searched with (each a separate search; shuffled with pass_random).
DPLA_TOPICS = ["campus", "college students", "university students", "dormitory", "residence hall",
               "student union", "dining hall", "cafeteria", "library reading room", "library interior", "laboratory",
               "classroom", "lecture hall", "commencement", "homecoming", "football game", "basketball game",
               "baseball game", "track meet", "marching band", "college band", "rowing", "gymnasium", "stadium",
               "agricultural experiment station", "cooperative extension", "dairy barn", "farm machinery",
               "greenhouse", "orchard", "livestock judging", "home economics", "main street", "downtown",
               "street scene", "parade", "county fair", "farmers market", "railroad depot", "bus", "bridge",
               "park", "botanical garden", "forest", "lake", "river", "mountains", "snow", "flood",
               "construction", "hospital", "church", "grocery store", "kitchen", "festival", "concert"]
DPLA_PAGES = 100                     # DPLA answers at most 100 pages a search (ParamValidator.maxPage)
# A CONTENTdm thumbnail address, made into the CONTENTdm IIIF address of the full picture.
CONTENTDM_THUMB = re.compile(r"^(https?://[^/]+)/(?:digital/api/singleitem/collection/([^/]+)/id/(\d+)/thumbnail|"
                             r"utils/getthumbnail/collection/([^/]+)/id/(\d+))")


def dpla_key():
    """The DPLA API key from the environment (DPLA_API_KEY, a GitHub secret in the packs workflow); "" when none."""
    return os.environ.get("DPLA_API_KEY", "").strip()


def as_list(value):
    """A DPLA field as a list (DPLA gives one value or a list)."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def dpla_rights_name(uri):
    """A rights URI in words ("No Copyright - United States (rightsstatements.org)", "CC BY 4.0" ...)."""
    for part, name in DPLA_RIGHTS_NAMES:
        if part in uri:
            if name == "CC BY":
                version = re.search(r"/by/(\d\.\d)", uri)
                return f"CC BY {version.group(1)}" if version else name
            return name
    return uri


def dpla_provider(doc):
    """The name of an item's data provider (the holding library) and of its DPLA hub."""
    dp, hub = doc.get("dataProvider"), doc.get("provider")
    dp = (dp.get("name") if isinstance(dp, dict) else (as_list(dp) or [""])[0]) or ""
    hub = (hub.get("name") if isinstance(hub, dict) else hub) or ""
    return clean(dp), clean(hub)


def dpla_place(src):
    """The place of a DPLA item from its first spatial entry with a US state or Canadian province ("Denton, Texas,
    USA"), or ""."""
    for sp in as_list(src.get("spatial")):
        if not isinstance(sp, dict):
            continue
        country = country_named(sp.get("country") or "")
        state = clean(sp.get("state"))
        if not country and state:
            country = "USA"
        if country not in ("USA", "Canada"):
            continue
        return place_name(clean(sp.get("city")), state, country)
    return ""


def dpla_year(src):
    """The first year an item's date gives (its begin date or display date); 0 when none."""
    for d in as_list(src.get("date")):
        text = " ".join(str(d.get(k) or "") for k in ("begin", "displayDate")) if isinstance(d, dict) else str(d)
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", text)
        if m:
            return int(m.group(1))
    return 0


# Catalogue fields and notes that are not about the picture.
RECORD_NOISE = re.compile(r"(\bpersistent url\s*:\s*\S+|https?://\S+|www\.\S+|\b(call|item|negative|accession|"
                          r"image|photo) (no|number|id)\.?\s*[:#]?\s*[\w./-]+|\bphotograph(ed)? by [^.;]*[.;]?|"
                          r"\bcourtesy of [^.;]*[.;]?|\bcopyright [^.;]*[.;]?)", re.I)


def record_text(title, descriptions):
    """The answer of a library record: its title, then its first description when that says more, catalogue noise
    taken out, at most about 70 words, ending with a full stop; "" when nothing is left."""
    title = RECORD_NOISE.sub(" ", clean(title)).strip(" .,;:[]")
    title = re.sub(r"[\[\]]", "", title)
    text = title
    for d in descriptions:
        d = RECORD_NOISE.sub(" ", clean(d)).strip(" ,;:")
        if d and d.lower()[:40] not in title.lower():
            text = f"{title.rstrip('.')}. {d}" if title else d
            break
    text = first_sentences(" ".join(text.split()), 70)
    return sentence(text) if text else ""


def dpla_picture(doc):
    """The address of an item's full-size picture: its "mediaMaster", else the CONTENTdm IIIF address made from a
    CONTENTdm thumbnail ("object"), else "" (the item's IIIF manifest is read later, dpla_manifest_picture)."""
    for url in as_list(doc.get("mediaMaster")):
        if isinstance(url, str) and url.startswith("http"):
            return url
    m = CONTENTDM_THUMB.match(str(doc.get("object") or ""))
    if m:
        host, alias, pointer = m.group(1), m.group(2) or m.group(4), m.group(3) or m.group(5)
        return f"{host}/iiif/2/{alias}:{pointer}/full/!2048,2048/0/default.jpg"
    return ""


def iiif_image(manifest):
    """The address of the first picture of a IIIF manifest (Presentation 2 or 3), asked for at most 2048 pixels; ""
    when none is found."""
    sequences = manifest.get("sequences") or []
    canvases = (sequences[0].get("canvases") if sequences else None) or manifest.get("items") or []
    for canvas in canvases[:1]:
        for image in (canvas.get("images") or []):                      # Presentation 2
            service = (image.get("resource") or {}).get("service") or {}
            service = service[0] if isinstance(service, list) and service else service
            sid = service.get("@id") or service.get("id") if isinstance(service, dict) else ""
            if sid:
                return sid.rstrip("/") + "/full/!2048,2048/0/default.jpg"
            if (image.get("resource") or {}).get("@id"):
                return image["resource"]["@id"]
        for page in (canvas.get("items") or []):                        # Presentation 3
            for anno in (page.get("items") or []):
                body = anno.get("body") or {}
                service = body.get("service") or []
                service = service[0] if isinstance(service, list) and service else service
                sid = (service.get("id") or service.get("@id")) if isinstance(service, dict) else ""
                if sid:
                    return sid.rstrip("/") + "/full/!2048,2048/0/default.jpg"
                if body.get("id"):
                    return body["id"]
    return ""


def dpla_item(doc):
    """(file name, answer, credit, place, year, provider, words, rights) of one DPLA item, or (None, reason) when it
    is not taken: not an image, not a college or university data provider, not openly licensed."""
    src = doc.get("sourceResource") or {}
    rights = str(doc.get("rights") or "")
    if "image" not in [str(t).lower() for t in as_list(src.get("type"))]:
        return None, "not an image item"
    provider, hub = dpla_provider(doc)
    if not UNIVERSITY.search(provider) or NOT_UNIVERSITY.search(provider):
        return None, f"its data provider ({provider or 'none'}) is not a college or university"
    if not DPLA_OPEN.match(rights):
        return None, f"its rights ({rights or 'none given'}) are not NoC-US, the Public Domain Mark, CC0 or CC BY"
    title = " ".join(as_list(src.get("title"))[:1])
    answer = record_text(title, as_list(src.get("description")))
    subjects = [clean(s.get("name") if isinstance(s, dict) else s) for s in as_list(src.get("subject"))][:12]
    year = dpla_year(src)
    words = " ".join([title, *map(str, as_list(src.get("description"))), *subjects])
    link = doc.get("isShownAt") or f"https://dp.la/item/{doc.get('id')}"
    credit = (f"{clean(title)[:150]}, {provider}" + (f", via {hub}" if hub and hub != provider else "") +
              f" and the Digital Public Library of America, {dpla_rights_name(rights)} ({rights}), {link}")
    return {"name": f"dpla-{doc.get('id')}.jpg", "answer": answer, "credit": credit, "place": dpla_place(src),
            "year": year, "provider": provider, "words": words, "rights": rights, "title": clean(title),
            "subjects": subjects, "page": link}, ""


def dpla_rows(item):
    """The rows of one DPLA picture: its record's words, and where it was taken when the record says."""
    facts = {"holding_library": item["provider"], "year": item["year"] or None, "subjects": item["subjects"]}
    facts = {k: v for k, v in facts.items() if v}
    rows = [{"question": DESCRIBE_Q, "answer": item["answer"], "credit": item["credit"], "facts": facts,
             **where(item["place"])}]
    if item["place"]:
        place = ("the " + item["place"]) if item["place"] == "USA" else item["place"]
        rows.append({"question": WHERE_Q, "answer": f"It was taken in {place}.", "credit": item["credit"],
                     **where(item["place"])})
    return marked(rows, item["words"])


def dpla_search(s, key, topic, rights, page):
    """One page (100 items) of a DPLA search: topic words, one exact rights URI."""
    from documentary_packs import get_json
    params = {"api_key": key, "q": topic, "rights": rights, "exact_field_match": "true", "page_size": 100,
              "page": page}
    return get_json(s, DPLA, params) or {}


def dpla_open_rights(s, key, topic):
    """The open rights URIs among a topic's items, with their counts, from DPLA's facet of the "rights" field; None
    when DPLA did not answer (a wrong key is refused with 403)."""
    from documentary_packs import get_json
    data = get_json(s, DPLA, {"api_key": key, "q": topic, "facets": "rights", "facet_size": 100, "page_size": 0})
    if data is None:
        return None                       # DPLA refused (a wrong key) or did not answer
    terms = ((data.get("facets") or {}).get("rights") or {}).get("terms") or []
    return [(t["term"], int(t.get("count") or 0)) for t in terms if DPLA_OPEN.match(str(t.get("term") or ""))]


def build_dpla_campus(limit):
    """The DPLA campus pack: college and university items whose rights are open, found by everyday words."""
    key = dpla_key()
    if not key:
        say("DPLA: no API key (set DPLA_API_KEY, a GitHub secret: the key is free from "
            "https://pro.dp.la/developers/api-basics). Nothing made.")
        return []
    s, rng, items, seen, answers = session(), pass_random("dpla_campus"), [], set(), set()
    topics = list(DPLA_TOPICS)
    rng.shuffle(topics)
    share = max(4, math.ceil(limit * 1.4 / len(topics)))
    manifests = refused = 0
    for topic in topics:
        if listing_out_of_time() or len(items) >= limit * 1.4:
            break
        got = 0
        open_rights = dpla_open_rights(s, key, topic)
        if open_rights is None:
            refused += 1
            if refused >= 3 and not items:
                say("DPLA refused three searches in a row (is DPLA_API_KEY right?). Stopping.")
                break
            continue
        for rights, count in open_rights:
            pages = list(range(1, min(DPLA_PAGES, math.ceil(count / 100)) + 1))
            rng.shuffle(pages)
            for page in pages[:6]:
                if got >= share or listing_out_of_time():
                    break
                time.sleep(0.5)
                for doc in dpla_search(s, key, topic, rights, page).get("docs") or []:
                    if got >= share:
                        break
                    item, reason = dpla_item(doc)
                    if item is None or item["name"] in seen:
                        continue
                    seen.add(item["name"])
                    reason = left_out_because(item["words"], item["year"], modern=False)
                    if reason:
                        considered(item["name"], item["page"], reason)
                        continue
                    url = dpla_picture(doc)
                    if not url and doc.get("iiifManifest") and manifests < limit * 2:
                        manifests += 1
                        from documentary_packs import get_json
                        url = iiif_image(get_json(s, doc["iiifManifest"], tries=2) or {})
                    if not url:
                        considered(item["name"], item["page"], "only a small thumbnail (no full-size picture or "
                                                               "IIIF image)")
                        continue
                    if not long_enough(item["answer"], item["title"]) or item["answer"] in answers:
                        needs_description(item["name"], url, item["credit"], dpla_rights_name(item["rights"]),
                                          text=item["answer"], title=item["title"], place=item["place"],
                                          reason="its title and description are under six English words",
                                          page_url=item["page"],
                                          extra={"subjects": item["subjects"], "year": item["year"],
                                                 "holding_library": item["provider"],
                                                 "child": bool(CHILD.search(item["words"])),
                                                 "content": "graphic" if GRAPHIC.search(item["words"]) else "",
                                                 "not_for_picture_making": True})
                        continue
                    answers.add(item["answer"])
                    items.append((item["name"], url, dpla_rows(item)))
                    got += 1
        say(f"DPLA '{topic}': {got} items")
    rng.shuffle(items)
    items = new_only(items)
    fetched = fetch_all(items[:int(limit * 1.25) + 2], workers=4, pause=0.3)[:limit]
    say(f"dpla_campus: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if r[0].get('child'))} marked child")
    return with_twins(fetched)


# ----------------------------------------------------------------- Commons: the shared listing

# Flickr Commons' "no known copyright restrictions" (Commons' short licence name "No restrictions") is open, as
# archive_packs.digital_commonwealth takes it; and the public domain, CC0 and CC BY.
NO_KNOWN = re.compile(r"^no restrictions$", re.I)


def is_open(licence, no_known_ok=False):
    """Whether a Commons file's short licence name lets it into an open pack (never SA, NC or ND)."""
    if re.search(r"\b(SA|NC|ND)\b|-SA|-NC|-ND|non-?commercial", licence or "", re.I):
        return False
    return bool(MECH_FREE.match(licence or "")) or (no_known_ok and bool(NO_KNOWN.match(licence or "")))


def open_entries(s, titles, no_known_ok=False):
    """[(title, picture address, credit, raw description, year, author)] for Commons files whose own licence is open
    (is_open), JPEG or PNG photos only, 50 a request; the files left out are noted with the reason."""
    out = []
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 1600,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|DateTimeOriginal",
                               "iiextmetadatalanguage": "en"})
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            if not p.get("pageid"):
                continue
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            if not is_open(licence, no_known_ok):
                considered(p["title"], page, f"its licence ({licence or 'none given'}) is not open (public domain, "
                                             "CC0, CC BY" + (" or no known copyright restrictions" if no_known_ok
                                                             else "") + ")")
                continue
            if info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                considered(p["title"], page, f"not a photo ({info.get('mime') or 'no picture'})")
                continue
            author = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            raw = clean((meta.get("ImageDescription") or {}).get("value"))
            if licence.lower() == "no restrictions":
                licence = "No known copyright restrictions"
            out.append((p["title"], info["thumburl"], f"{p['title']} by {author}, {licence}, {page}", raw,
                        photo_year(meta), author))
        time.sleep(1)
    return out


def licence_of(credit):
    """The licence part of a credit line made by open_entries ("<title> by <author>, <licence>, <page>")."""
    parts = credit.rsplit(", ", 2)
    return parts[1] if len(parts) == 3 else ""


def stream(category, who, place, pages, author, skip=""):
    """One college photo stream or library collection on Commons: its category, the college as said in a sentence,
    the place (as a row's place, "Glen Ellyn, Illinois, USA"), how many random listing pages of 500 files to sample
    (0: a few files from each subcategory), a pattern its files' author line must match, and a pattern of
    subcategory or file names to leave out."""
    return {"category": category, "who": who, "place": place, "pages": pages, "author": re.compile(author, re.I),
            "skip": re.compile(skip, re.I) if skip else None}


def stream_rows(caption, spec, credit, words, who_row=True):
    """The rows of one Commons photo: its caption, where it was taken (when the stream is in one place), and which
    college took it (for a college's own stream)."""
    here = where(spec["place"], "origin")
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit, **here}]
    if who_row:
        rows.append({"question": WHO_Q, "answer": f"It is a photo by {spec['who']}.", "credit": credit, **here})
    if "," in spec["place"]:
        rows.append({"question": WHERE_Q, "answer": f"It was taken in {spec['place']}.", "credit": credit, **here})
    return marked(rows, words)


def commons_stream_pack(specs, limit, key, prefix, caption_of, modern, no_known_ok, who_row):
    """One pack from Commons streams: each category sampled at random places of its listing, its open-licence photos
    by that author (open_entries checks each file's licence), those that pass left_out_because, with the caption
    caption_of(raw, title) gives; a free photo whose caption is too short is set aside for a description. The
    categories share the limit."""
    s, rng, items, seen = session(), pass_random(key), [], set()
    share = math.ceil(limit * 1.3 / len(specs))
    for spec in specs:
        if listing_out_of_time():
            break
        titles = [t for t in sample_members(s, spec["category"], spec["pages"], rng)
                  if not NOT_A_PHOTO.search(t) and t not in seen and not (spec["skip"] and spec["skip"].search(t))]
        rng.shuffle(titles)
        say(f"Commons {spec['category']}: {len(titles)} files sampled")
        got = 0
        for start in range(0, len(titles), 100):
            if got >= share or listing_out_of_time():
                break
            for title, url, credit, raw, year, author in open_entries(s, titles[start:start + 100], no_known_ok):
                if got >= share:
                    break
                seen.add(title)
                if not spec["author"].search(author):
                    considered(title, url, "its author line does not name the college or library (not its own "
                                           "photo)")
                    continue
                words = f"{title} {raw}"
                reason = left_out_because(words, year, modern)
                if reason:
                    considered(title, url, reason)
                    continue
                caption = caption_of(raw, title)
                if not long_enough(caption, title):
                    needs_description(file_name(prefix, title), url, credit, licence_of(credit), text=caption,
                                      title=title, reason="its caption is under six English words or only the "
                                                          "file name", place=spec["place"], place_kind="origin",
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"college": spec["who"], "commons_category": spec["category"],
                                             "year": year, "child": bool(CHILD.search(words)),
                                             "content": "graphic" if GRAPHIC.search(words) else "",
                                             "not_for_picture_making": True})
                    continue
                items.append((file_name(prefix, title), url, stream_rows(caption, spec, credit, words, who_row)))
                got += 1
        say(f"  {got} photos from {spec['who']}")
    rng.shuffle(items)
    fetched = commons_fetch(items[:int(limit * 1.1) + 2])[:limit]
    say(f"{key}: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if r[0].get('child'))} marked child")
    return with_twins(fetched)


# ----------------------------------------------------------------- commons_college_streams

COLLEGE = "a college"
COLLEGE_STREAMS = [
    stream("Files from COD Newsroom Flickr stream", "the College of DuPage, a community college",
           "Glen Ellyn, Illinois, USA", 4, r"COD Newsroom|College of DuPage"),
    stream("Files from Germanna Community College Flickr stream", "Germanna Community College",
           "Virginia, USA", 3, r"Germanna"),
    stream("Files from Community College of Vermont Flickr stream", "the Community College of Vermont",
           "Vermont, USA", 2, r"Community College of Vermont|\bCCV\b"),
    stream("Photographs by Texas A&M University–Commerce Marketing Communications Photography",
           "Texas A&M University-Commerce", "Commerce, Texas, USA", 2, r"Texas A&M|Commerce"),
    stream("Files from the Roanoke College Flickr stream", "Roanoke College", "Salem, Virginia, USA", 1,
           r"Roanoke College"),
    stream("Files from Union College Flickr stream", "Union College", "USA", 1, r"Union College"),
    stream("Files from Uoflphoto3 Flickr stream", "the University of Louisville", "Louisville, Kentucky, USA", 1,
           r"uoflphoto|University of Louisville"),
    stream("Files from the University of Michigan School for Environment and Sustainability Flickr stream",
           "the University of Michigan School for Environment and Sustainability", "Ann Arbor, Michigan, USA", 0,
           r"University of Michigan|SEAS|SNRE"),
    stream("Files from UDC David A. Clarke School of Law Flickr stream",
           "the University of the District of Columbia David A. Clarke School of Law",
           "Washington, District of Columbia, USA", 1, r"UDC|Clarke School of Law"),
]
# College photo-file notes that are not about the picture ("13390-Rodeo Team group shot -2037.jpg", "_97A8288").
STREAM_NOISE = re.compile(r"(^|\s)[\w-]*\d{3,}[\w-]*\.(jpe?g|png)\b|^\s*_?\w*\d{4,}\w*\s*$|\(\d{8,}\)", re.I)


def college_caption(raw, title):
    """A college's own caption: the file-name notes, credit lines and web addresses taken out
    (us_modern_packs.agency_caption)."""
    text = re.sub(r"^\s*English\s*:\s*", "", clean(raw))
    text = re.sub(r"^.{0,120}?\.(jpe?g|png)\s+", "", text, flags=re.I)   # a file name the caption starts with
    text = STREAM_NOISE.sub(" ", text)
    return re.sub(r"\s+([.,;:!?])", r"\1", agency_caption(text))


def build_commons_college_streams(limit):
    """Colleges' own photo streams on Commons (1990 onwards)."""
    return commons_stream_pack(COLLEGE_STREAMS, limit, "commons_college_streams", "college", college_caption,
                               modern=True, no_known_ok=False, who_row=True)


# ----------------------------------------------------------------- commons_university_archives

# A library collection's files carry the original photographer (or "Unknown") as their author, not the library,
# so any author line is accepted: the category itself is the library's upload (Flickr Commons or its own).
ANY_AUTHOR = r"."
ARCHIVE_STREAMS = [
    stream("Photographs by University of Washington Libraries Digital Collections",
           "the University of Washington Libraries", "Washington, USA", 1,
           ANY_AUTHOR, skip=r"bathing|fashion plate"),
    stream("Files from Miami University Libraries - Digital Collections", "Miami University Libraries",
           "Oxford, Ohio, USA", 3, ANY_AUTHOR, skip=r"group portraits?|fraternit|sororit|amusement of youth"),
    stream("Images from University of Alberta Library", "the University of Alberta Library (Peel's Prairie "
           "Provinces)", "Canada", 1, ANY_AUTHOR),
    stream("Photographs by SMU Central University Libraries", "Southern Methodist University's Central University "
           "Libraries", "", 2, ANY_AUTHOR),
]
# The labels of a library record in a Commons description ("Title: ... Creator: ... Date: ... Description: ...").
RECORD_LABELS = re.compile(r"\b(Title|Alternative Title|Creator|Contributors?|Date|Place|Part Of|Photographer|"
                           r"Subjects?(?: \(\w+\))?|Digital Collection|Notes|On Back|On Front|Postmark Date|Location|"
                           r"Physical Description|Rights|Repository|Collection|Lineup|Address|Message|To|"
                           r"Description|Persistent URL|Format|Identifier|Source|Publisher)\s*:", re.I)


def record_fields(raw):
    """{label: text} of a library record written into a Commons description, and the text before the first label
    (under "")."""
    fields, parts = {}, RECORD_LABELS.split(clean(raw))
    fields[""] = parts[0].strip()
    for i in range(1, len(parts) - 1, 2):
        fields.setdefault(parts[i].lower(), parts[i + 1].strip(" ;"))
    return fields


def archive_caption(raw, title):
    """A library record's words for a picture: its title (or the text before the record's fields, or the file's
    name) and its description; dates, creators, subjects and notes taken out."""
    f = record_fields(raw)
    head = f.get("title") or f.get("") or re.sub(r"\s*\(\d{6,}\)$", "", title.split(":", 1)[-1].rsplit(".", 1)[0])
    head = re.sub(r",?\s*(n\.d\.|ca\. ?\d{4}|\d{4})\s*$", "", head.strip()).strip(" .,;")
    return record_text(head, [f.get("description", "")])


def build_commons_university_archives(limit):
    """University libraries' digitized photographs with no known copyright restrictions (earlier decades)."""
    return commons_stream_pack(ARCHIVE_STREAMS, limit, "commons_university_archives", "uarch", archive_caption,
                               modern=False, no_known_ok=True, who_row=False)


# ----------------------------------------------------------------- the packs

UNIVERSITY_PACKS = {
    "dpla_campus": (build_dpla_campus, "Digital Public Library of America (https://dp.la), items from US college "
                                       "and university libraries whose rights are No Copyright - United States, the "
                                       "Public Domain Mark, CC0 or CC BY (each item's own rights URI and holding "
                                       "library below); DPLA metadata CC0 (https://dp.la/about/terms-conditions)."),
    "commons_college_streams": (build_commons_college_streams, "Wikimedia Commons copies of US colleges' own photo "
                                                               "streams (College of DuPage, Germanna Community "
                                                               "College, Community College of Vermont, Texas A&M "
                                                               "University-Commerce, Roanoke College, Union "
                                                               "College, University of Louisville, University of "
                                                               "Michigan SEAS, UDC Law): each file's own licence "
                                                               "checked (public domain, CC0 or CC BY), credited "
                                                               "below with its author and file page; captions by "
                                                               "the colleges. https://commons.wikimedia.org"),
    "commons_university_archives": (build_commons_university_archives, "Wikimedia Commons copies of university "
                                                                       "libraries' digitized photographs (University "
                                                                       "of Washington Libraries, Miami University "
                                                                       "Libraries, University of Alberta Library, "
                                                                       "SMU Central University Libraries) marked no "
                                                                       "known copyright restrictions or public "
                                                                       "domain, each credited below; descriptions "
                                                                       "from the libraries' records."),
}

# How many pictures a full build takes from each.
UNIVERSITY_LIMITS = {
    "dpla_campus": 6000,                   # of the open college and university image items DPLA finds by topic
    "commons_college_streams": 4000,       # of about 19,000 files in nine streams; many captions are short
    "commons_university_archives": 3000,   # of about 12,000 files in four collections
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one university pack builder.")
    parser.add_argument("key", choices=sorted(UNIVERSITY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--rows", type=int, default=0, help="print only this many rows (0: all)")
    args = parser.parse_args(argv)
    entries = UNIVERSITY_PACKS[args.key][0](args.limit)
    for name, data, row in entries[:args.rows or None]:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child, "
        f"{sum(1 for _, _, r in entries if r.get('content') == 'graphic')} rows marked graphic, "
        f"{len(build_packs.NEEDS)} set aside for a description")
    return 0


if __name__ == "__main__":
    sys.exit(main())
