"""Sports, musical instruments, places of worship, landmarks, vehicles, toys and games for the Picture Model Training
Kit: the collections whose licence keeps them out of the open packs (share-alike, non-commercial, research-only or no
terms written at all), and the open ones too big or too odd for a ready-made pack. The open ones are ready-made packs:
packs/culture_packs.py (Open Images, Wikidata with Commons pictures under CC0, public domain or CC BY, the Met's
instruments, Google Landmarks v2 free images, playing cards, chess pieces and positions, DeepScores sheet music).
The owner's rule: every collection found goes in under its licence group; none is dropped only for its licence.

Nothing here is in a ready-made pack or re-shared by the kit's makers. Each collection is downloaded by the kit on the
user's own computer, straight from its makers (or the copy named below), only when the user ticks the matching
choice. Groups (Source.group, as in sources.py and extra_sources.py):
  "permissive"     open, but downloaded by the kit itself (too big, or made only of computer drawings).
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with
                   them is CC BY-SA.
  "noncommercial"  CC BY-NC-SA: personal use only (--personal-noncommercial).
  "research"       research-only terms, or no terms stated at all: personal use only (--personal-research with
                   --accept-research-terms).

The collections (CULTURE_SOURCES):
  permissive
    lego_parts            LegoBricks (pvrancx on Hugging Face, Apache-2.0): computer-drawn pictures (LDraw) of the
                          1,000 most common LEGO parts, each named from Rebrickable's parts list ("This is a LEGO
                          piece: Brick 2 x 4, part 3001.").
  share-alike
    commons_culture_sa    Wikimedia Commons files under CC BY-SA or GFDL (most Wiki Loves Monuments photos are CC BY-SA
                          and come in through these categories) of places of worship of every faith, World Heritage
                          Sites, musical instruments, sports and car models found through Wikidata (CC0 facts: the
                          name, kind, faith, place and country, maker, country of origin), and of festivals, religious
                          objects, taxis and toys from the categories the open packs use.
    gldv2_sa              Google Landmarks Dataset v2 (labels CC BY 4.0): the clean training images whose Commons
                          licence is CC BY-SA or GFDL (the CC0, public domain and CC BY ones are the open
                          gldv2_landmarks pack).
  noncommercial
    mimo_instruments      MIMO, Musical Instrument Museums Online, through Europeana: about 63,000 instruments in
                          European museums, every record CC BY-NC-SA 4.0; the instrument's English name from MIMO's own
                          keyword list and the museum.
    chessred              ChessReD, the Chess Recognition Dataset (Masouris and van Gemert, TU Delft, CC BY-NC-SA 4.0):
                          smartphone photos of real games, every piece's square labelled (the 2,078 photos of ChessReD2K
                          read out of its 4.7 GB zip without downloading it whole).
  research (research terms, or none stated)
    sports100             100 Sports Image Classification (Kaggle; the HES-XPLAIN copy on Hugging Face, marked CC0, but
                          its pictures were collected from the web): "What sport is this?"
    stanford_cars         Stanford Cars (Krause et al., 2013; the tanganke copy on Hugging Face, clean train and test
                          files only): 196 car models by make, model, body style and year; its terms allow
                          non-commercial research only and its pictures come from the web.
    turkish_instruments   instrument-images (YakupAkdin on Hugging Face, no licence stated): photos of ten instruments
                          played in Turkey (bağlama, kanun, kemençe, oud, yaylı tambur, violin, guitar ...).

Every picture of a place gets "Where was this photo taken?" when the record gives the place; rows whose words name a
child are marked "child": True. Answers are fixed sentences from each source's own labels and records; nothing is
written by an AI model (collections whose descriptions were written by one are in CULTURE_NOT_INCLUDED).

Needing sign-up or a purchase (cannot be downloaded automatically): CULTURE_SIGN_UP has the links.
Looked at and not included, with the reason: CULTURE_NOT_INCLUDED.

    python kit/culture_sources.py turkish_instruments --data <empty folder> --cap 8     (a quick check)
"""

import csv
import gzip
import hashlib
import io
import json
import os
import random
import re
import time
import urllib.parse

import sources
from big_sources import even_pick
from extra_sources import NO_TERMS, commons_file_name, commons_get, commons_sa_entries, commons_session
from more_sources import fetch_shared, sentence
from personal_sources import CHILD_WORDS, a_or_an, listed, remote_zip
from sources import NARRATE, USER_AGENT, Source, clean, fetch_pictures

ASK_WHERE = "Where was this photo taken?"
ASK_INSTRUMENT = "What instrument is this?"
ASK_SPORT = "What sport is this?"
WDQS = "https://query.wikidata.org/sparql"


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def hf_url(repo, path):
    """The download address of one file of a Hugging Face dataset."""
    return f"https://huggingface.co/datasets/{repo}/resolve/main/" + urllib.parse.quote(path)


def hf_files(repo):
    """The file names of a Hugging Face dataset repository."""
    from huggingface_hub import HfApi
    return HfApi().list_repo_files(repo, repo_type="dataset")


def research(summary):
    """A research collection's terms in one line, ending with the kit's personal-use note."""
    return summary.rstrip(".") + ". Personal, non-commercial use only."


def is_child(*texts):
    """True when any of texts names a child."""
    return any(CHILD_WORDS.search(t or "") for t in texts)


# ----------------------------------------------------------------- permissive: LEGO parts

LEGO_REPO = "pvrancx/legobricks"
REBRICKABLE_PARTS = "https://cdn.rebrickable.com/media/downloads/parts.csv.gz"


def lego_names():
    """{part number: part name} from Rebrickable's parts list (about 1 MB)."""
    import requests
    data = requests.get(REBRICKABLE_PARTS, timeout=120, headers={"User-Agent": USER_AGENT}).content
    out = {}
    for row in csv.DictReader(io.StringIO(gzip.decompress(data).decode("utf-8", "replace"))):
        out[row.get("part_num", "")] = clean(row.get("name"))
    return out


def prepare_lego_parts(source, data_dir, work, cap):
    """LegoBricks: row groups of a few of its 51 parquet files (read from Hugging Face piece by piece, never whole),
    each picture saved with its part's name: "What LEGO piece is this?" """
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem
    fs, rng = HfFileSystem(), random.Random(601)
    names = lego_names()
    paths = sorted(p for p in hf_files(LEGO_REPO) if p.endswith(".parquet"))
    rng.shuffle(paths)
    folder, rows, want = os.path.join(data_dir, source.key), [], cap + source.test
    os.makedirs(folder, exist_ok=True)
    for path in paths:
        if len(rows) >= want:
            break
        f = pq.ParquetFile(fs.open(f"datasets/{LEGO_REPO}/{path}"))
        labels = f.schema_arrow.field("label").metadata or {}
        class_names = json.loads((f.metadata.metadata or {}).get(b"huggingface", b"{}")).get("info", {}).get(
            "features", {}).get("label", {}).get("names", []) if not labels else []
        group = rng.randrange(f.metadata.num_row_groups)
        table = f.read_row_group(group).to_pylist()
        rng.shuffle(table)
        for i, record in enumerate(table[:max(1, want // max(1, len(paths) // 4))]):
            label = record.get("label")
            part = class_names[label] if isinstance(label, int) and label < len(class_names) else str(label)
            name = names.get(part, "")
            if not name:
                continue
            row_id = f"lego-{part}-{group}-{i}"
            picture = sources.save_picture(row_id, (record.get("image") or {}).get("bytes") or b"", folder)
            if picture:
                rows.append({"question": "What LEGO piece is this?", "answer": f"This is a LEGO piece: {name} "
                             f"(part {part}).", "split": "", "picture": picture,
                             "credit": "LegoBricks (pvrancx), Apache-2.0, https://huggingface.co/datasets/pvrancx/"
                                       "legobricks ; part names from Rebrickable's parts list, "
                                       "https://rebrickable.com/downloads/"})
    say(f"  {len(rows)} LEGO part pictures.")
    return rows[:want]


# ----------------------------------------------------------------- share-alike: Wikimedia Commons through Wikidata

def sparql(query, tries=4):
    """The result rows of a Wikidata query ([{name: value}], entity addresses shortened), tried again when busy."""
    import requests
    for attempt in range(tries):
        try:
            r = requests.get(WDQS, params={"query": query, "format": "json"}, timeout=180,
                             headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"})
            if r.status_code == 200:
                return [{k: v["value"].replace("http://www.wikidata.org/entity/", "") for k, v in b.items()}
                        for b in r.json()["results"]["bindings"]]
        except Exception:  # noqa: BLE001 - tried again
            pass
        time.sleep(15 * (attempt + 1))
    say("  Wikidata did not answer one query; it is left out.")
    return []


def subjects(rows):
    """Query rows grouped by ?item: [{"label", <name>: [values]}], items without an English label left out."""
    out = {}
    for b in rows:
        label = clean(b.get("itemLabel"))
        if not b.get("item") or not label or re.fullmatch(r"Q\d+", label):
            continue
        d = out.setdefault(b["item"], {"label": label})
        for k, value in b.items():
            if k not in ("item", "itemLabel") and value and not re.fullmatch(r"Q\d+", value):
                d.setdefault(k, [])
                if value not in d[k]:
                    d[k].append(value)
    return list(out.values())


def first(d, key):
    """The first value of a subject's field, or ""."""
    return (d.get(key) or [""])[0]


def wd_place(d):
    """ "Amritsar, India" from a subject's located-in and country labels (administrative areas left out), or ""."""
    country = first(d, "countryLabel")
    if not country or len(d.get("countryLabel") or []) > 1:
        return ""
    country = {"People's Republic of China": "China", "United States of America": "USA",
               "United Kingdom": "UK"}.get(country, country)
    town = first(d, "placeLabel")
    if re.search(r"\b(district|municipality|prefecture|county|province|region|governorate|oblast|commune|"
                 r"department|borough|parish)$", town, re.I) or town.lower() == country.lower():
        town = ""
    return f"{town}, {country}" if town else country


def named(label):
    """A place's name after "This is": "the Eiffel Tower", "the Temple of Heaven", "Harmandir Sahib"."""
    if label.lower().startswith("the ") or "'s " in label or label[:1].islower():
        return label
    if re.search(r"\b(of|de la|del)\b|(Tower|Bridge|Palace|Gate|Wall|Monument|Memorial|Museum|Building|Mosque|"
                 r"Temple|Stadium|Lighthouse|Statue|Shrine|Pagoda|Stupa|Synagogue|Fort|Fortress)$", label):
        return "the " + label
    return label


def faith_words(faith):
    """ "the Catholic Church", "Sikhism"."""
    return ("the " + faith) if re.search(r"\b(Church|Communion|Bahá'í Faith)\b", faith) and \
        not faith.lower().startswith("the ") else faith


SA_WORSHIP = [("Q16970", "church", "Christianity", 8), ("Q2977", "cathedral", "Christianity", 2),
              ("Q32815", "mosque", "Islam", 1), ("Q34627", "synagogue", "Judaism", 1),
              ("Q842402", "Hindu temple", "Hinduism", 1), ("Q5393308", "Buddhist temple", "Buddhism", 1),
              ("Q337986", "gurdwara", "Sikhism", 1), ("Q845945", "Shinto shrine", "Shinto", 1),
              ("Q2613100", "Jain temple", "Jainism", 1), ("Q1151612", "Taoist temple", "Taoism", 1),
              ("Q1568313", "Bahá'í House of Worship", "the Bahá'í Faith", 1)]
SA_PLACE_QUERY = """SELECT ?item ?itemLabel ?image ?cat ?religionLabel ?countryLabel ?placeLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT ?item ?sl WHERE { %s ?item wdt:P18 ?i ; wikibase:sitelinks ?sl . FILTER(?sl >= %d) }
    ORDER BY DESC(?sl) LIMIT %d }
  ?item wdt:P18 ?image . OPTIONAL { ?item wdt:P373 ?cat } OPTIONAL { ?item wdt:P140 ?religion }
  OPTIONAL { ?item wdt:P17 ?country } OPTIONAL { ?item wdt:P131 ?place }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
SA_THING_QUERY = """SELECT ?item ?itemLabel ?cat ?parentLabel ?originLabel ?makerLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT ?item ?sl WHERE { %s ?item wdt:P373 ?c ; wikibase:sitelinks ?sl . FILTER(?sl >= %d) }
    ORDER BY DESC(?sl) LIMIT %d }
  ?item wdt:P373 ?cat . OPTIONAL { ?item wdt:P279 ?parent } OPTIONAL { ?item wdt:P495 ?origin }
  OPTIONAL { ?item wdt:P176 ?maker }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
GENERIC = {"musical instrument", "artificial object", "sport", "type of sport", "car", "automobile", "vehicle",
           "motor car", "object", "class"}
# Commons categories the open packs also use (festivals, objects, vehicles, toys), with their fixed sentences.
SA_CATEGORIES = {
    "Dipavali": ("What festival or religious occasion does this picture show?", "It shows Diwali (Deepavali), the "
                 "festival of lights of Hindus, Jains and Sikhs."),
    "Holi": ("What festival or religious occasion does this picture show?", "It shows Holi, the Hindu spring "
             "festival of colours."),
    "Eid al-Fitr": ("What festival or religious occasion does this picture show?", "It shows Eid al-Fitr, the "
                    "Muslim festival at the end of Ramadan."),
    "Hanukkah": ("What festival or religious occasion does this picture show?", "It shows Hanukkah, the Jewish "
                 "festival of lights."),
    "Vesak": ("What festival or religious occasion does this picture show?", "It shows Vesak, the Buddhist festival "
              "of the Buddha's birth, enlightenment and death."),
    "Nativity scenes": ("What festival or religious occasion does this picture show?", "It shows a nativity scene, "
                        "the birth of Jesus, set up by Christians at Christmas."),
    "Rosaries": ("What religious object is this?", "This is a rosary, Catholic prayer beads."),
    "Prayer rugs": ("What religious object is this?", "This is a prayer rug, used by Muslims for prayer."),
    "Torii": ("What is this?", "This is a torii, the gateway of a Shinto shrine."),
    "Iconostases": ("What is this?", "This is an iconostasis, the wall of icons in an Eastern Orthodox church."),
    "Jeepneys": ("What vehicle is this?", "This is a jeepney, a shared minibus of the Philippines."),
    "Cycle rickshaws": ("What vehicle is this?", "This is a cycle rickshaw, a pedal-powered taxi."),
    "Tuk-tuks in Thailand": ("What vehicle is this?", "This is a tuk-tuk, a three-wheeled taxi in Thailand."),
    "Dice": ("What toy is this?", "These are dice."), "Chess sets": ("What game is this?", "This is a chess set."),
    "Scoreboards": ("What is this?", "This is a scoreboard."),
}


def culture_sa_subjects():
    """The subjects of commons_culture_sa: (kind of subject, subject) for places of worship, World Heritage Sites,
    instruments, sports, car models and the SA_CATEGORIES, taken in turn."""
    groups = []
    for qid, kind, faith, articles in SA_WORSHIP:
        found = subjects(sparql(SA_PLACE_QUERY % (f"?item wdt:P31 wd:{qid} .", articles, 120)))
        groups.append([("worship", dict(d, kind=kind, faith=faith)) for d in found])
    groups.append([("landmark", d) for d in subjects(sparql(SA_PLACE_QUERY % ("?item wdt:P1435 wd:Q9259 .", 5,
                                                                                 600)))])
    groups.append([("instrument", d) for d in subjects(sparql(SA_THING_QUERY % ("?item wdt:P279+ wd:Q34379 .", 5,
                                                                                   600)))])
    groups.append([("sport", d) for d in subjects(sparql(SA_THING_QUERY % ("?item wdt:P31 wd:Q31629 .", 5, 400)))])
    groups.append([("car", d) for d in subjects(sparql(SA_THING_QUERY % ("?item wdt:P31 wd:Q3231690 .", 10, 600)))])
    groups.append([("category", {"label": c, "cat": [c], "ask": q, "say": a}) for c, (q, a) in
                   SA_CATEGORIES.items()] * 3)
    queues = []
    for i, g in enumerate(groups):
        g = list(g)
        random.Random(611 + i).shuffle(g)
        queues.append(g)
    out = []
    while any(queues):
        for q in queues:
            if q:
                out.append(q.pop())
    return out


# Captions written by a template, not by the photographer (Wiki Loves Monuments and heritage uploads).
BOILERPLATE = re.compile(r"identified by the ID|^this is a photo of (a|an) (monument|cultural heritage|listed|"
                         r"historic|protected|natural heritage)", re.I)


def culture_sa_rows(kind, d, title, text):
    """The rows of one share-alike picture from its subject's Wikidata facts (or its category's fixed sentence)."""
    def kind_of():
        """The subject's most useful "subclass of" label, or ""."""
        kinds = [k for k in d.get("parentLabel") or [] if k.lower() not in GENERIC and not re.match(r"^\d", k)]
        return sorted(kinds, key=len)[0] if kinds else ""

    def origin():
        """ " from Japan", or ""."""
        origins = d.get("originLabel") or []
        return f" from {sources.place_words(origins[0])}" if len(origins) == 1 else ""
    rows, place = [], ""
    if kind in ("worship", "landmark"):
        place = wd_place(d)
        name = named(d["label"])
        if kind == "worship":
            faiths = sorted(d.get("religionLabel") or [], key=len, reverse=True)
            faith = faiths[0] if faiths else d["faith"]
            answer = f"This is {name}, {a_or_an(d['kind'])} {d['kind']}" + (f" in {place}" if place else "") + \
                (f", a place of worship of {faith_words(faith)}" if faith else "") + "."
            rows.append({"question": "What place of worship is this, and of which faith?", "answer": answer})
        else:
            rows.append({"question": "What landmark is this?",
                         "answer": f"This is {name}" + (f" in {place}" if place else "") + "."})
        if place:
            rows.append({"question": ASK_WHERE, "answer": f"It was taken at {name} in {sources.place_words(place)}."})
    elif kind == "instrument":
        k = kind_of()
        rows.append({"question": ASK_INSTRUMENT, "answer": sentence(
            f"this is {a_or_an(d['label'])} {d['label']}" + (f", {a_or_an(k)} {k}" if k else "") + origin())})
    elif kind == "sport":
        rows.append({"question": ASK_SPORT, "answer": sentence(f"this is {d['label']}" + origin())})
    elif kind == "car":
        makers = d.get("makerLabel") or []
        k = kind_of() or "car"
        rows.append({"question": "What car is this?", "answer": sentence(
            f"this is {a_or_an(d['label'])} {d['label']}, {a_or_an(k)} {k}"
            + (f" made by {makers[0]}" if len(makers) == 1 else "") + origin())})
    else:
        rows.append({"question": d["ask"], "answer": d["say"]})
    if text and not BOILERPLATE.search(text):
        rows.append({"question": NARRATE, "answer": text})
    extra = sources.place_fields({"place": place}) if place else {}
    return [dict(r, **extra) for r in rows]


def prepare_commons_culture_sa(source, data_dir, work, cap, per_subject=3):
    """Wikimedia Commons files under CC BY-SA or GFDL (never NC or ND) of the subjects of culture_sa_subjects: each
    subject's Wikidata picture and a random pick from its Commons category, 50 files a request, at most per_subject
    pictures a subject."""
    s, rng = commons_session(), random.Random(612)
    want = int((cap + source.test) * 1.15)
    items, pictures, queue = [], set(), []

    def flush():
        """Check the queued files' licences; the share-alike ones become rows."""
        got = {t: (url, credit, text) for t, url, credit, text in commons_sa_entries(s, [t for t, _, _ in queue])}
        counts = {}
        for title, kind, d in queue:
            if title not in got or title in pictures or counts.get(d["label"], 0) >= per_subject:
                continue
            url, credit, text = got[title]
            pictures.add(title)
            counts[d["label"]] = counts.get(d["label"], 0) + 1
            child = is_child(title, text)
            for row in culture_sa_rows(kind, d, title, text):
                items.append((commons_file_name("culsa", title), url,
                              dict(row, split="", credit=credit, **({"child": True} if child else {}))))
        queue.clear()

    for kind, d in culture_sa_subjects():
        if len(pictures) >= want:
            break
        titles = []
        if first(d, "image"):
            titles.append("File:" + urllib.parse.unquote(first(d, "image").rsplit("/", 1)[-1]))
        for category in d.get("cat") or []:
            data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                                   "cmtype": "file", "cmlimit": 100})
            found = [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])
                     if not re.search(r"\.(svg|gif|tiff?|pdf|djvu)$|\b(map|logo|drawing|diagram|plan)\b",
                                      m["title"], re.I)]
            rng.shuffle(found)
            titles += found[:per_subject * 3]
        queue += [(t, kind, d) for t in dict.fromkeys(titles) if t not in pictures]
        if len(queue) >= 45:
            flush()
    if queue:
        flush()
    say(f"  Fetching {len(pictures)} Commons pictures of culture subjects (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- share-alike: Google Landmarks v2

GLD = "https://s3.amazonaws.com/google-landmark/metadata/"
GLD_SA = re.compile(r"\b(BY[ -]SA|GFDL|share ?alike)", re.I)


def gld_lines(url):
    """The lines of a large CSV file of Google Landmarks v2, read as it downloads, split at newline bytes only
    (requests' iter_lines also splits at Unicode line separators, which some Commons titles contain)."""
    import requests
    with requests.get(url, stream=True, timeout=600, headers={"User-Agent": USER_AGENT}) as r:
        r.raise_for_status()
        rest = b""
        for chunk in r.iter_content(1 << 20):
            rest += chunk
            *done, rest = rest.split(b"\n")
            for line in done:
                yield line.decode("utf-8", "replace").rstrip("\r")
        if rest:
            yield rest.decode("utf-8", "replace")


def prepare_gldv2_sa(source, data_dir, work, cap, per_landmark=2):
    """Google Landmarks v2: the clean training images (train_clean.csv) whose Commons licence is CC BY-SA or GFDL
    (never NC or ND), read from train.csv and train_attribution.csv line by line (the same order) until enough are
    found, at most per_landmark a landmark; the landmark's name from its Commons category."""
    rng = random.Random(613)
    clean_ids = {}
    for row in csv.reader(gld_lines(GLD + "train_clean.csv")):
        if len(row) == 2 and row[0].isdigit():
            for image_id in row[1].split():
                clean_ids[image_id] = row[0]
    names = {}
    for row in csv.reader(gld_lines(GLD + "train_label_to_category.csv")):
        if len(row) == 2 and row[0].isdigit():
            names[row[0]] = clean(urllib.parse.unquote(row[1].rsplit("Category:", 1)[-1]).replace("_", " "))
    want, items, per = int((cap + source.test) * 1.15), [], {}
    for a, b in zip(csv.reader(gld_lines(GLD + "train.csv")), csv.reader(gld_lines(GLD + "train_attribution.csv"))):
        if len(a) != 3 or len(b) != 5 or a[0] != b[0] or a[0] not in clean_ids:
            continue
        landmark, licence = clean_ids[a[0]], re.sub(r"\(https?://[^)]*\)", "", b[3]).strip()
        name = names.get(landmark, "")
        if not name or not GLD_SA.search(licence) or re.search(r"\bN[CD]\b|non-?commercial", licence, re.I) \
                or per.get(landmark, 0) >= per_landmark or rng.random() < 0.5:
            continue
        per[landmark] = per.get(landmark, 0) + 1
        file_name = urllib.parse.unquote(a[1].rsplit("/", 1)[-1])
        answer = f"This is {named(name)}."
        items.append((f"gldsa-{a[0]}.jpg", "https://commons.wikimedia.org/wiki/Special:FilePath/"
                      + urllib.parse.quote(file_name) + "?width=1280",
                      {"question": "What landmark or place is this?", "answer": answer, "split": "",
                       "credit": f"{clean(b[4])} by {clean(b[2]) or 'unknown'}, {licence}, "
                                 f"{b[1].replace('http://', 'https://')}; Google Landmarks Dataset v2, labels CC BY 4.0",
                       **({"child": True} if is_child(name, b[4]) else {})}))
        if len(items) >= want:
            break
    say(f"  Fetching {len(items)} Google Landmarks v2 images (share-alike).")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=3, pause=0.3)


# ----------------------------------------------------------------- noncommercial: MIMO through Europeana

EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
MIMO = "MIMO - Musical Instrument Museums Online"


def europeana_key():
    """The Europeana API key: EUROPEANA_KEY, or Europeana's public demonstration key."""
    return os.environ.get("EUROPEANA_KEY") or "api2demo"


def mimo_name(item):
    """The instrument's English name from MIMO's keyword (the record's English concept labels, "Musical instrument"
    left out), or ""."""
    labels = (item.get("edmConceptPrefLabelLangAware") or {}).get("en") or []
    names = [clean(x) for x in labels if clean(x) and clean(x).lower() not in ("musical instrument",
                                                                                 "musical instruments")]
    return names[0] if names else ""


def prepare_mimo_instruments(source, data_dir, work, cap):
    """MIMO through Europeana (every record CC BY-NC-SA 4.0): records page by page with Europeana's cursor, those
    with an English instrument name and a picture, at most a few of each name; Europeana's 400-pixel copy of each
    picture (the museums' own servers often refuse programs)."""
    import requests
    want = int((cap + source.test) * 1.15)
    params = [("wskey", europeana_key()), ("query", "*"), ("qf", f'PROVIDER:"{MIMO}"'), ("qf", "TYPE:IMAGE"),
              ("media", "true"), ("rows", "100"), ("profile", "rich")]
    cursor, items, per_name = "*", [], {}
    while cursor and len(items) < want:
        time.sleep(0.5)
        try:
            data = requests.get(EUROPEANA, params=params + [("cursor", cursor)], timeout=120,
                                headers={"User-Agent": USER_AGENT}).json()
        except Exception:  # noqa: BLE001 - the rest is left out
            break
        for item in data.get("items") or []:
            if len(items) // 2 >= want:
                break
            name, rights = mimo_name(item), " ".join(item.get("rights") or [])
            shown = (item.get("edmIsShownBy") or [""])[0]
            if not name or "by-nc-sa" not in rights or not shown.startswith("http") or per_name.get(name, 0) >= 6:
                continue
            per_name[name] = per_name.get(name, 0) + 1
            museum = clean((item.get("dataProvider") or [""])[0])
            title = clean((item.get("title") or [""])[0])
            lower = name[0].lower() + name[1:] if not name[:2].isupper() else name
            plural = re.search(r"[^su]s$", lower.split(" (")[0])          # "cymbals", "castanets", "bagpipes"
            answer = f"These are {lower}." if plural else f"This is {a_or_an(lower)} {lower}."
            its, it_is = ("Their", "They are") if plural else ("Its", "It is")
            more = answer + (f" {its} name in the museum's record: {title}." if title and title.lower() != lower.lower()
                             else "") + (f" {it_is} in the collection of the {museum}." if museum else "")
            page = item.get("guid") or f"https://www.europeana.eu/item{item.get('id', '')}"
            credit = f"{title or name}, {museum}, CC BY-NC-SA 4.0, MIMO via Europeana: {page.split('?')[0]}"
            picture = "https://api.europeana.eu/thumbnail/v3/400/" + hashlib.md5(shown.encode("utf-8")).hexdigest()
            file_name = "mimo-" + re.sub(r"[^\w-]+", "_", item.get("id", str(len(items))))[-80:] + ".jpg"
            items.append((file_name, picture, {"question": ASK_INSTRUMENT, "answer": answer, "split": "",
                                               "credit": credit}))
            items.append((file_name, picture, {"question": "Tell me about this museum object.", "answer": more,
                                               "split": "", "credit": credit}))
        cursor = data.get("nextCursor") if data.get("items") else None
    say(f"  Fetching {len(items) // 2} MIMO instrument pictures (non-commercial).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- noncommercial: ChessReD

CHESSRED = "https://data.4tu.nl/file/99b5c721-280b-450b-b058-b2900b69a90f/"
CHESSRED_NOTES = CHESSRED + "3cae6364-daca-4967-b426-1e4b68cdb64c"         # annotations.json, 22 MB
CHESSRED_2K = CHESSRED + "410e41c7-dde5-413f-8722-3e112363a1a2"            # chessred2k.zip, 4.7 GB
PIECES = ("king", "queen", "rook", "bishop", "knight", "pawn")


def position_words(squares):
    """ "White: king on g1, rooks on a1 and f1 ... Black: ..." from {colour: {piece: [squares]}}."""
    parts = []
    for colour in ("white", "black"):
        said = []
        for piece in PIECES:
            where = sorted(squares.get(colour, {}).get(piece, []))
            if where:
                said.append(f"{piece} on {where[0]}" if len(where) == 1 else f"{piece}s on {listed(where)}")
        if said:
            parts.append(f"{colour.capitalize()}: {', '.join(said)}.")
    return " ".join(parts)


def prepare_chessred(source, data_dir, work, cap):
    """ChessReD2K: the annotations (every piece's square on every photo) and the photos of the ChessReD2K split,
    read out of the 4.7 GB zip piece by piece; the position said square by square."""
    import requests
    notes = requests.get(CHESSRED_NOTES, timeout=600, headers={"User-Agent": USER_AGENT}).json()
    names = {c["id"]: c["name"] for c in notes["categories"]}
    wanted = set()
    for split in notes["splits"].get("chessred2k", {}).values():
        wanted |= set(split.get("image_ids") or [])
    squares = {}
    for p in notes["annotations"]["pieces"]:
        name = names.get(p["category_id"], "empty")
        if p["image_id"] in wanted and "-" in name and p.get("chessboard_position"):
            colour, piece = name.split("-", 1)
            squares.setdefault(p["image_id"], {}).setdefault(colour, {}).setdefault(piece, []).append(
                p["chessboard_position"])
    by_file = {im["file_name"]: im["id"] for im in notes["images"] if im["id"] in squares}
    archive = remote_zip(CHESSRED_2K)
    members = [m for m in archive.namelist() if m.rsplit("/", 1)[-1] in by_file]
    random.Random(614).shuffle(members)
    folder, rows = os.path.join(data_dir, source.key), []
    os.makedirs(folder, exist_ok=True)
    for member in members[:cap + source.test]:
        image_id = by_file[member.rsplit("/", 1)[-1]]
        answer = position_words(squares[image_id])
        picture = sources.save_picture(f"chessred-{image_id}", archive.read(member), folder)
        if picture and answer:
            rows.append({"question": "What is the position on this chessboard?", "answer": answer, "split": "",
                         "picture": picture,
                         "credit": "Chess Recognition Dataset (ChessReD), Athanasios Masouris and Jan van Gemert, "
                                   "TU Delft, 2023, CC BY-NC-SA 4.0, https://doi.org/10.4121/99b5c721-280b-450b-b058-"
                                   "b2900b69a90f"})
    say(f"  {len(rows)} ChessReD photos.")
    return rows


# ----------------------------------------------------------------- research: 100 sports

SPORTS_REPO = "HES-XPLAIN/SportsImageClassification"
# The dataset's folder names with their spelling mended.
SPORT_FIX = {"ampute football": "amputee football", "barell racing": "barrel racing", "canoe slamon": "canoe slalom",
             "figure skating men": "men's figure skating", "figure skating women": "women's figure skating",
             "figure skating pairs": "pairs figure skating", "nascar racing": "NASCAR racing",
             "formula 1 racing": "Formula One racing", "nhra drag racing": "NHRA drag racing",
             "ultimate": "ultimate frisbee", "sumo wrestling": "sumo wrestling", "pole climbing": "pole climbing",
             "wheelchair basketball": "wheelchair basketball", "wheelchair racing": "wheelchair racing"}


def prepare_sports100(source, data_dir, work, cap):
    """100 Sports Image Classification: its zip (read piece by piece), the pictures spread evenly over the 100
    sports: "What sport is this?" """
    from personal_sources import zip_members
    archive = remote_zip(hf_url(SPORTS_REPO, "SportsImageClassification.zip"))
    groups = {}
    for name in archive.namelist():
        parts = name.split("/")
        if len(parts) >= 3 and parts[-3].lower() in ("train", "valid", "test") and \
                name.lower().endswith((".jpg", ".jpeg", ".png")):
            groups.setdefault(parts[-2].lower(), []).append(name)
    chosen = []
    for name in even_pick(groups, cap + source.test, 615):
        sport = name.split("/")[-2].lower()
        sport = SPORT_FIX.get(sport, sport)
        chosen.append((name, {"question": ASK_SPORT, "answer": sentence(f"this is {sport}"), "split": "",
                              "credit": "100 Sports Image Classification (Kaggle; HES-XPLAIN copy), "
                                        "https://huggingface.co/datasets/HES-XPLAIN/SportsImageClassification"}))
    say(f"  Reading {len(chosen)} sports pictures of {len(groups)} sports.")
    return zip_members(source, data_dir, work, lambda: archive, chosen)


# ----------------------------------------------------------------- research: Stanford Cars

CARS_REPO = "tanganke/stanford_cars"
BODY_STYLES = ("Sedan", "Coupe", "Convertible", "Hatchback", "Wagon", "SUV", "Minivan", "Van", "Cab", "Crew Cab",
               "Extended Cab", "Regular Cab", "Club Cab", "Quad Cab", "SuperCab", "Type-S", "Type R", "Hybrid")


def car_answer(label):
    """ "This is an Audi R8 Coupe, a 2012 model." from a Stanford Cars class ("Audi R8 Coupe 2012")."""
    m = re.match(r"^(.*?)\s+((?:19|20)\d\d)$", label.strip())
    if not m:
        return sentence(f"this is {a_or_an(label)} {label}")
    return f"This is {a_or_an(m.group(1))} {m.group(1)}, a {m.group(2)} model."


def prepare_stanford_cars(source, data_dir, work, cap):
    """Stanford Cars: the clean train and test parquet files only (the copy also holds altered versions with noise
    and blur, which are left out), read row group by row group, spread over the 196 models."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem
    fs, rng = HfFileSystem(), random.Random(616)
    paths = [p for p in hf_files(CARS_REPO) if re.match(r"data/(train|test)-\d+-of-\d+\.parquet$", p)]
    folder, rows, want = os.path.join(data_dir, source.key), [], cap + source.test
    os.makedirs(folder, exist_ok=True)
    per_model = {}
    for path in sorted(paths):
        f = pq.ParquetFile(fs.open(f"datasets/{CARS_REPO}/{path}"))
        features = json.loads((f.metadata.metadata or {}).get(b"huggingface", b"{}")).get("info", {}).get(
            "features", {})
        class_names = (features.get("label") or {}).get("names") or []
        groups = list(range(f.metadata.num_row_groups))
        rng.shuffle(groups)
        for g in groups:
            if len(rows) >= want:
                break
            for i, record in enumerate(f.read_row_group(g).to_pylist()):
                label = record.get("label")
                if not isinstance(label, int) or label >= len(class_names) or \
                        per_model.get(label, 0) >= max(2, want // 150):
                    continue
                picture = sources.save_picture(f"cars-{path.split('/')[-1].split('.')[0]}-{g}-{i}",
                                               (record.get("image") or {}).get("bytes") or b"", folder)
                if picture:
                    per_model[label] = per_model.get(label, 0) + 1
                    rows.append({"question": "What car is this?", "answer": car_answer(class_names[label]),
                                 "split": "", "picture": picture,
                                 "credit": "Stanford Cars (Jonathan Krause, Michael Stark, Jia Deng and Li Fei-Fei, "
                                           "2013), tanganke copy, https://huggingface.co/datasets/tanganke/"
                                           "stanford_cars"})
                if len(rows) >= want:
                    break
    say(f"  {len(rows)} Stanford Cars pictures of {len(per_model)} models.")
    return rows


# ----------------------------------------------------------------- research: Turkish instruments

INSTRUMENTS_REPO = "YakupAkdin/instrument-images"
TURKISH_INSTRUMENTS = {"arp": "a harp", "baglama": "a bağlama (saz)", "elektroGitar": "an electric guitar",
                       "gitar": "a guitar", "kanun": "a kanun (qanun)", "keman": "a violin", "kemence": "a kemençe",
                       "mandolin": "a mandolin", "ud": "an oud", "yayliTambur": "a yaylı tambur"}


def prepare_turkish_instruments(source, data_dir, work, cap):
    """instrument-images: the ten instrument folders, spread evenly: "What instrument is this?" """
    groups = {}
    for path in hf_files(INSTRUMENTS_REPO):
        folder = path.split("/")[0]
        if folder in TURKISH_INSTRUMENTS and path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            groups.setdefault(folder, []).append(path)
    items = []
    for path in even_pick(groups, cap + source.test, 617):
        folder = path.split("/")[0]
        items.append((re.sub(r"[^\w.-]", "_", path).rsplit(".", 1)[0][-90:] + ".jpg", hf_url(INSTRUMENTS_REPO, path),
                      {"question": ASK_INSTRUMENT, "answer": f"This is {TURKISH_INSTRUMENTS[folder]}.", "split": "",
                       "credit": "instrument-images (YakupAkdin), "
                                 "https://huggingface.co/datasets/YakupAkdin/instrument-images"}))
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- needing sign-up, and not included

CULTURE_SIGN_UP = {
    "CompCars (Comprehensive Cars, CUHK; research only)":
        "http://mmlab.ie.cuhk.edu.hk/datasets/comp_cars/ : sign the agreement and e-mail it to the authors; the "
        "download password comes back by e-mail. 1,716 car models with make, model and year, web and surveillance "
        "photos.",
    "Kaggle sets: Cards Image Dataset (53 playing cards), Chess Positions (rendered boards with FEN), Musical "
    "Instruments image sets, Indian temples and architectural-style sets":
        "https://www.kaggle.com : a free Kaggle account is needed to download; check each set's licence page and "
        "where its pictures come from (most are collected from the web, so research use only).",
    "Roboflow Universe sets (playing cards, dice, chess pieces, LEGO, vehicles)":
        "https://universe.roboflow.com : a free Roboflow account and API key are needed; each set shows its own "
        "licence (the chess pieces set used in the open chess_pieces pack is the Roboflow 100 copy on Hugging Face).",
    "Europeana with your own key":
        "https://pro.europeana.eu/page/get-api : a free key; set EUROPEANA_KEY so mimo_instruments does not use the "
        "public demonstration key.",
    "Smithsonian Open Access API (National Museum of American History musical instruments)":
        "https://api.data.gov/signup/ : a free api.data.gov key for api.si.edu (the open smithsonian pack already "
        "reads the museums' open-access files without a key).",
    "European Churches & Temples Dataset (Kos1976 on Hugging Face)":
        "https://huggingface.co/datasets/Kos1976/1-temples-47-commercial : a sample of a commercial stock collection "
        "under its seller's own licence; buy a licence before use.",
}

CULTURE_NOT_INCLUDED = {
    "OpenBrush Religious Art (jaddai on Hugging Face, CC0)": "its descriptions were written by an AI model "
                                                             "(Qwen3-VL); the paintings themselves are museum "
                                                             "pictures the kit already gets from the museums.",
    "mosques-images (abdurrahman22224 on Hugging Face)": "its 113 descriptions were written by an AI captioning model "
                                                         "(they contain its typical mistake \"arafed\"), and no "
                                                         "licence or source of the photos is stated.",
    "AIDOVECL vehicles (amir-kazemi on Hugging Face, CC BY 4.0)": "its pictures were made partly by an AI picture "
                                                                  "generator (vehicles outpainted into new scenes).",
    "Olympic Vision 100 Sports (hoangbang on Hugging Face)": "the same pictures as 100 Sports (sports100), with its "
                                                             "test answers hidden.",
    "Chessboard digital images with FEN (MohammedHemed on Hugging Face, CC BY 4.0)": "flat computer-drawn boards "
                                                                                    "from python-chess; the open "
                                                                                    "chess_positions pack teaches the "
                                                                                    "same reading on realistic "
                                                                                    "renders, and chessred on photos.",
    "Playing cards (JackFurby on Hugging Face, MIT)": "machine-made card pictures (cut-out cards randomly turned and "
                                                      "scaled); the open playing_cards pack has real photos.",
    "Muse OMR Benchmark (musegroup on Hugging Face, CC0)": "PDF pages and MuseScore files; turning them into answers "
                                                           "needs a music-notation reader the kit does not have.",
    "MUSCIMA++ (CC BY-NC-SA 4.0)": "the copy reachable here (e7mac on Hugging Face) holds only the symbol labels; its "
                                   "handwritten pages, CVC-MUSCIMA, are a separate download from the Computer Vision "
                                   "Center (Barcelona) that was not reached from this machine. A non-commercial entry "
                                   "can be added once the pages can be fetched.",
    "MIMO's own website (mimo-international.com)": "did not answer from this machine; its records are used through "
                                                   "Europeana (mimo_instruments).",
    "Stanford Cars' original site": "gone (the Stanford page now says the data is no longer hosted); the tanganke "
                                    "copy is used (stanford_cars).",
    "Hugging Face sports-classification copies (vumin001, vieanh, nihaludeen, chrishocb)": "no source or licence "
                                                                                          "stated; most look like "
                                                                                          "copies of the same 100 "
                                                                                          "Sports set.",
    "LSUN church_outdoor (and its Hugging Face copies)": "only the word \"church\" for each picture, and its photos "
                                                         "were collected from the web without terms.",
    "Civil aircraft": "already in the open service_packs commons_airplanes and the kit's fgvc_aircraft.",
    "Paralympic wheelchair sports, goalball, blind football": "already in disability_packs (commons_disability, "
                                                              "open_images_disability).",
}


# ----------------------------------------------------------------- the table

def nc_terms():
    """The terms line of a CC BY-NC-SA collection."""
    return "CC BY-NC-SA 4.0: you may use and share it, with credit, for non-commercial purposes only, and share " \
           "anything made from it under the same licence. Personal, non-commercial use only."


CULTURE_SOURCES = [
    # ---- permissive
    Source("lego_parts", "LegoBricks: computer-drawn pictures of LEGO parts, named",
           "Apache-2.0 (huggingface.co/datasets/pvrancx/legobricks); part names from Rebrickable's free parts list",
           "LegoBricks (pvrancx), Apache-2.0, https://huggingface.co/datasets/pvrancx/legobricks ; part names from "
           "Rebrickable, https://rebrickable.com/downloads/", "permissive", 1500, 15, prepare_lego_parts,
           "about 600 MB read from parquet files"),
    # ---- share-alike
    Source("commons_culture_sa", "Wikimedia Commons: places of worship, landmarks, instruments, sports, cars, "
                                 "festivals and toys, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0; facts from Wikidata, CC0",
           "Wikimedia Commons authors (including Wiki Loves Monuments entrants), CC BY-SA or GFDL, each credited in "
           "its row, https://commons.wikimedia.org ; facts from Wikidata, CC0", "share-alike", 3000, 20,
           prepare_commons_culture_sa, "about 1 GB of pictures"),
    Source("gldv2_sa", "Google Landmarks Dataset v2: landmark photos under CC BY-SA or GFDL (share-alike)",
           "Labels CC BY 4.0 (github.com/cvdfoundation/google-landmark); each image CC BY-SA or GFDL (its Commons "
           "page)",
           "Google Landmarks Dataset v2 (Tobias Weyand, Andre Araujo, Bingyi Cao and Jack Sim, CVPR 2020), "
           "https://github.com/cvdfoundation/google-landmark ; images by Wikimedia Commons authors, each credited",
           "share-alike", 3000, 20, prepare_gldv2_sa, "up to 1.5 GB of lists read as they download, and the photos"),
    # ---- noncommercial
    Source("mimo_instruments", "MIMO: musical instruments in European museums (non-commercial)",
           "CC BY-NC-SA 4.0 (each record's rights statement on Europeana)",
           "MIMO - Musical Instrument Museums Online, through Europeana, https://www.europeana.eu ; each museum "
           "credited in its row", "noncommercial", 3000, 20, prepare_mimo_instruments, "about 150 MB",
           terms="https://creativecommons.org/licenses/by-nc-sa/4.0/", terms_summary=nc_terms()),
    Source("chessred", "ChessReD: photos of real chess games with every piece's square (non-commercial)",
           "CC BY-NC-SA 4.0 (data.4tu.nl, doi 10.4121/99b5c721-280b-450b-b058-b2900b69a90f)",
           "Chess Recognition Dataset (ChessReD), Athanasios Masouris and Jan van Gemert, TU Delft, 2023, "
           "https://doi.org/10.4121/99b5c721-280b-450b-b058-b2900b69a90f", "noncommercial", 2000, 20,
           prepare_chessred, "22 MB of labels and about 2 GB of photos read out of a 4.7 GB zip",
           terms="https://creativecommons.org/licenses/by-nc-sa/4.0/", terms_summary=nc_terms()),
    # ---- research
    Source("sports100", "100 Sports Image Classification: which sport (personal use)",
           "Marked CC0 on Hugging Face and Kaggle, but the pictures were collected from the web",
           "100 Sports Image Classification (Kaggle), HES-XPLAIN copy, "
           "https://huggingface.co/datasets/HES-XPLAIN/SportsImageClassification", "research", 3000, 20,
           prepare_sports100, "about 200 MB read out of a zip",
           terms="https://huggingface.co/datasets/HES-XPLAIN/SportsImageClassification",
           terms_summary=research("Marked CC0, but its pictures were gathered from websites whose owners did not "
                                  "license them")),
    Source("stanford_cars", "Stanford Cars: 196 car models by make, model and year (personal use)",
           "Stanford Cars terms: non-commercial research purposes only; pictures from the web",
           "Stanford Cars (Jonathan Krause, Michael Stark, Jia Deng and Li Fei-Fei, '3D Object Representations for "
           "Fine-Grained Categorization', 3dRR 2013), copy at https://huggingface.co/datasets/tanganke/stanford_cars",
           "research", 3000, 20, prepare_stanford_cars, "about 1 GB read from parquet files",
           terms="https://huggingface.co/datasets/tanganke/stanford_cars",
           terms_summary=research("The Stanford Cars dataset may be used for non-commercial research purposes only; "
                                  "its pictures belong to the websites they came from")),
    Source("turkish_instruments", "Instruments played in Turkey: bağlama, kanun, kemençe, oud and others "
                                  "(personal use)",
           "No licence stated (huggingface.co/datasets/YakupAkdin/instrument-images)",
           "instrument-images (YakupAkdin), https://huggingface.co/datasets/YakupAkdin/instrument-images", "research",
           989, 15, prepare_turkish_instruments, "about 100 MB",
           terms="https://huggingface.co/datasets/YakupAkdin/instrument-images", terms_summary=NO_TERMS),
]

# The collections a picture-making model may learn from: objects, buildings and vehicles without people (the LEGO
# parts, chess photos, MIMO museum instruments, Stanford Cars and the Turkish instrument photos; not the Commons and
# landmark collections, whose photos often show people and children, nor the sports pictures).
CULTURE_PICTURE_MAKING_OK = {"lego_parts", "chessred", "mimo_instruments", "stanford_cars", "turkish_instruments"}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one culture collection.")
    parser.add_argument("key", choices=[s.key for s in CULTURE_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in CULTURE_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="culture-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
