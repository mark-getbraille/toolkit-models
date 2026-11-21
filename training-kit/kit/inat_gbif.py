"""iNaturalist research-grade observations for the kit's own downloads (the share-alike and non-commercial
iNaturalist entries of us_sources.py, canada_sources.py and bodily_sources.py), read the way the ready-made packs
read them (packs/na_animal_packs.py, "iNaturalist through GBIF").

Why: iNaturalist's website says "ai-train=no" and the robots.txt of its API turns every program away. So the kit
never reads www.inaturalist.org or api.inaturalist.org. Instead:
  - the records come from GBIF's occurrence API (api.gbif.org, which its robots.txt allows): the dataset
    "iNaturalist Research-grade Observations", which iNaturalist itself publishes to GBIF;
  - the photos come from the iNaturalist Open Dataset on Amazon's open-data programme
    (inaturalist-open-data.s3.amazonaws.com), which iNaturalist publishes for reuse under each photo's own licence.
A photo kept only on iNaturalist's own website (static.inaturalist.org) is never used. Each photo's OWN licence is
checked (an observation can be CC BY while its photo is CC BY-NC). training-kit/tests/test_no_inaturalist_site.py
checks that no kit file fetches iNaturalist's website or API.

Only research-grade observations are on GBIF (iNaturalist's casual ones, most pets' among them, are not).
"""

import collections
import random
import re
import time
import unicodedata
from urllib.parse import urlsplit

from sources import USER_AGENT, clean

GBIF = "https://api.gbif.org/v1/"
INAT_DATASET = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"   # GBIF's key of "iNaturalist Research-grade Observations"
OPEN_DATA_HOST = "inaturalist-open-data.s3.amazonaws.com"
PHOTO = re.compile(r"/photos/(\d+)/[a-z]+\.(\w+)$")
# iNaturalist's "iconic" groups as GBIF Backbone keys: GBIF has no class for reptiles or ray-finned fish, so their
# orders are listed (lizards and snakes, turtles, crocodiles; sharks and rays and the main bony-fish orders).
GROUP_KEYS = {"Plantae": (6,), "Fungi": (5,), "Insecta": (216,), "Aves": (212,), "Mammalia": (359,),
              "Reptilia": (11592253, 11418114, 11493978), "Amphibia": (131,), "Arachnida": (367,),
              "Mollusca": (52,),
              "Actinopterygii": (121, 587, 1313, 1153, 708, 772, 588, 549, 590, 773, 495, 538, 548)}
# A photo's licence address on GBIF -> iNaturalist's short code ("cc-by-sa") and its words ("CC BY-SA").
LICENCE = re.compile(r"creativecommons\.org/(?:licenses/([a-z-]+)|publicdomain/(zero|mark))/", re.I)
WORDS = {"cc0": "CC0", "pdm": "Public Domain Mark", "cc-by": "CC BY", "cc-by-sa": "CC BY-SA", "cc-by-nd": "CC BY-ND",
         "cc-by-nc": "CC BY-NC", "cc-by-nc-sa": "CC BY-NC-SA", "cc-by-nc-nd": "CC BY-NC-ND"}
EVIDENCE = re.compile(r'"?evidenceOfPresence"?\s*:\s*(\[[^\]]*\]|"[^"]*")', re.I)


def on_inaturalist_site(url):
    """True when an address is on iNaturalist's own website (inaturalist.org or any part of it): never fetched."""
    host = (urlsplit(url or "").hostname or "").lower()
    return host == "inaturalist.org" or host.endswith(".inaturalist.org")


def open_data_photo(url):
    """The iNaturalist Open Dataset address of a photo's "large" copy (1,024 pixels), from the address GBIF lists,
    or "" for any other address."""
    parts = urlsplit(url or "")
    m = PHOTO.search(parts.path)
    if (parts.hostname or "").lower() != OPEN_DATA_HOST or not m:
        return ""
    return f"https://{OPEN_DATA_HOST}/photos/{m.group(1)}/large.{m.group(2)}"


def licence_code(url):
    """iNaturalist's short code of a Creative Commons licence address ("cc-by-nc"), "cc0", "pdm", or ""."""
    m = LICENCE.search(url or "")
    if not m:
        return ""
    if m.group(2):
        return "cc0" if m.group(2).lower() == "zero" else "pdm"
    return "cc-" + m.group(1).lower()


def photo(record, licences):
    """(GBIF media entry, licence code, Open Dataset address) of a record's first photo in the iNaturalist Open
    Dataset whose own licence is one of licences (codes such as "cc-by-sa"), or (None, "", "")."""
    for m in record.get("media") or []:
        code, url = licence_code(m.get("license")), open_data_photo(m.get("identifier"))
        if m.get("type") == "StillImage" and code in licences and url:
            return m, code, url
    return None, "", ""


def photo_id(url):
    """iNaturalist's number of a photo, from its Open Dataset address."""
    m = PHOTO.search(urlsplit(url or "").path)
    return m.group(1) if m else ""


def gbif_json(path, params):
    """One GBIF API answer (JSON), tried again after a pause; {} when it does not come."""
    import requests
    for attempt in range(3):
        try:
            r = requests.get(GBIF + path, params=params, timeout=120, headers={"User-Agent": USER_AGENT})
            if r.status_code == 200 and isinstance(r.json(), dict):
                return r.json()
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(5 * (attempt + 1))
    return {}


def search(params, offset=0, limit=300):
    """One page of iNaturalist research-grade records with a photo on GBIF matching params."""
    offset = max(0, min(offset, 100000 - limit))
    return gbif_json("occurrence/search", {"datasetKey": INAT_DATASET, "mediaType": "StillImage",
                                           "occurrenceStatus": "PRESENT", "offset": offset, "limit": limit,
                                           **params}).get("results") or []


def folded(text):
    """Text without accents, in lower case ("Québec" -> "quebec"), to compare names."""
    return "".join(c for c in unicodedata.normalize("NFD", text or "") if unicodedata.category(c) != "Mn").lower()


def regions(country, names):
    """{name: GBIF stateProvince} for the states or provinces named, as iNaturalist's records on GBIF write them
    ("Quebec" -> "Québec"), from GBIF's counts of records by state or province (compared without accents)."""
    data = gbif_json("occurrence/search", {"datasetKey": INAT_DATASET, "country": country, "limit": 0,
                                           "facet": "stateProvince", "stateProvince.facetLimit": 200})
    written = [c["name"] for c in ((data.get("facets") or [{}])[0].get("counts") or [])]
    out = {}
    for name in names:
        match = next((w for w in written if folded(w) == folded(name)), None)
        if match:
            out[name] = match
    return out


def taxon(name):
    """GBIF search parameters for the records of a scientific name, or None when GBIF does not know it: its GBIF
    key, or, when GBIF counts the name as a synonym of a wider species ("Canis familiaris" under "Canis lupus", which
    takes in wolves), the name as iNaturalist wrote it, falling back to the accepted name only when no record is
    written that way."""
    m = gbif_json("species/match", {"name": name, "strict": "true"})
    if m.get("matchType") not in ("EXACT", "VARIANT") or not m.get("usageKey"):
        return None
    if m.get("status") == "SYNONYM" and m.get("acceptedUsageKey"):
        if search({"verbatimScientificName": name}, 0, 1):
            return {"verbatimScientificName": name}
        return {"taxonKey": m["acceptedUsageKey"]}
    return {"taxonKey": m["usageKey"]}


def latin(record):
    """The species a record is identified as, or "" when it is named only above species."""
    if record.get("taxonRank") not in ("SPECIES", "SUBSPECIES", "VARIETY", "FORM"):
        return ""
    return clean(record.get("species"))


def english_name(record, cache):
    """The English name of a record's species from GBIF's checklists, as packs/na_animal_packs.english_name chooses
    it: the name most checklists mark preferred, else the one ITIS gives, else the commonest (cached; "" when there
    is none)."""
    key = record.get("speciesKey")
    if not key:
        return ""
    if key not in cache:
        results = gbif_json(f"species/{key}/vernacularNames", {"limit": 300}).get("results") or []
        eng = [r for r in results if r.get("language") == "eng" and clean(r.get("vernacularName"))]

        def commonest(pool):
            """The name most entries of pool give (ignoring case and hyphens), as first written; "" for none."""
            counts = collections.Counter(clean(r["vernacularName"]).lower().replace("-", " ") for r in pool)
            if not counts:
                return ""
            top = counts.most_common(1)[0][0]
            return next(clean(r["vernacularName"]) for r in pool
                        if clean(r["vernacularName"]).lower().replace("-", " ") == top)
        pick = commonest([r for r in eng if r.get("preferred")]) or next(
            (clean(r["vernacularName"]) for r in eng if "Integrated Taxonomic Information System" in
             (r.get("source") or "")), "") or commonest(eng)
        cache[key] = "" if len(pick) > 60 else pick
    return cache[key]


def evidence(record):
    """The set of what iNaturalist's "Evidence of presence" annotation says a record shows ({"scat"} ...)."""
    m = EVIDENCE.search(str(record.get("dynamicProperties") or ""))
    return {w.strip().lower() for w in re.findall(r'"([^"]+)"', m.group(1))} if m else set()


def credit(record, media, code):
    """ "Photo by someone on iNaturalist, CC BY-NC, https://www.inaturalist.org/observations/5 (via GBIF,
    https://www.gbif.org/occurrence/11)" (the observation's address is only written, never fetched)."""
    who = clean(media.get("creator") or media.get("rightsHolder") or record.get("recordedBy"))
    who = who if re.search(r"[A-Za-z0-9]", who) else "an iNaturalist user"
    link = clean(record.get("references") or record.get("occurrenceID"))
    gbif = f"https://www.gbif.org/occurrence/{record.get('key')}"
    return f"Photo by {who} on iNaturalist, {WORDS.get(code, code.upper())}, " \
           f"{link if link.startswith('http') else gbif} (via GBIF, {gbif})"


def a_or_an(word):
    """ "a" or "an" before a word."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def region_items(country, found, groups, licences, want, prefix, place_of):
    """Kit items [(file name, photo address, row)] of iNaturalist records in each state or province (found: {name:
    GBIF stateProvince}) and group of living things (groups: [(iconic group, question)]) whose photo's own licence is
    one of licences: the pairs take turns, one page of 300 records at a random place among each pair's first 3,000
    (photos under the rarer licences are few on each page). Each photo gives the species row and "Where was this photo
    taken?" (place_of(name), "Ontario, Canada")."""
    rng = random.Random(prefix)
    pairs = [(name, g, q) for name in found for g, q in groups]
    rng.shuffle(pairs)
    per = max(2, -(-want // max(1, len(pairs))))
    items, seen, names = [], set(), {}
    for name, group, question in pairs:
        if len(items) >= want * 2:
            break
        params = {"country": country, "stateProvince": found[name], "taxonKey": list(GROUP_KEYS[group])}
        results = search(params, rng.randrange(0, 10) * 300) or search(params)
        got = 0
        for record in results:
            media, code, url = photo(record, licences)
            species = latin(record)
            if got >= per or not media or not species or record.get("key") in seen:
                continue
            seen.add(record["key"])
            common = english_name(record, names)
            answer = f"This is {a_or_an(common)} {common} ({species})." if common else f"This is {species}."
            line, place = credit(record, media, code), place_of(name)
            file_name = f"{prefix}-{photo_id(url)}.jpg"
            items.append((file_name, url, {"question": question, "answer": answer, "split": "", "credit": line,
                                           "place": place}))
            items.append((file_name, url, {"question": "Where was this photo taken?", "split": "", "credit": line,
                                           "answer": f"It was taken in {place}.", "place": place}))
            got += 1
        time.sleep(0.3)                           # GBIF asks clients to pace their requests
    return items


def scat_records(found, licences, want, rng, pages=10):
    """[(record, media, licence code, photo address)] of iNaturalist records of a taxon (found: search parameters
    from taxon()) whose "Evidence of presence" annotation says scat and whose first usable photo's own licence is one
    of licences, up to want."""
    out, seen = [], set()
    for page in range(pages):
        results = search(dict(found, q="scat"), page * 300)
        for record in results:
            media, code, url = photo(record, licences)
            if media and "scat" in evidence(record) and record.get("key") not in seen:
                seen.add(record["key"])
                out.append((record, media, code, url))
        if len(out) >= want or len(results) < 300:
            break
        time.sleep(0.3)                           # GBIF asks clients to pace their requests
    rng.shuffle(out)
    return out[:want]
