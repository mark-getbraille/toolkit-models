"""Historical-event and safety-training picture collections for the Picture Model Training Kit whose licence keeps
them out of the open packs. The open ones found in the same search (Wikimedia Commons event pictures found through
Wikidata, Library of Congress and US National Archives event photos, Europeana, ISO 7010 and GHS signs, road signs,
Commons safety equipment and hazard photos, government safety posters, CDC PHIL workplace photos and D-Fire's own
camera frames) are ready-made packs: packs/events_safety_packs.py.

The owner's rule: every collection found goes in under its licence category (open -> pack; share-alike,
non-commercial or research -> an entry here; sign-up -> listed below). Nothing here is in a ready-made pack or
re-shared by the kit's makers. Each collection is downloaded by the kit on the user's own computer, straight from its
makers (or the copy named), only when the user ticks the matching choice. Groups (Source.group, as in sources.py,
extra_sources.py and packs/SOURCE-RULES.md):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with
                   them is CC BY-SA.
  "research"       research terms, no stated terms, or a stated licence that cannot cover the pictures (photos
                   gathered from the web by the dataset's makers): personal-use box (Alt+Z) after agreeing to the
                   terms; personal use only.

The collections (EVENTS_SAFETY_SOURCES):
  share-alike
    commons_events_sa   Wikimedia Commons pictures of historical events under CC BY-SA or GFDL, found as in the
                        open commons_events pack: Wikidata event items (CC0: name, date P585 or P580/P582, location
                        P276, country P17, part of P361) and the Commons files that "depict" (P180) them or are in
                        their Commons category (P373). "What event does this picture show?", "Where and when was
                        this?" and the file's caption. Graphic pictures (the dead, wounds) are kept and marked
                        "content": "graphic"; sexual violence, torture, executions and dead or injured children are
                        left out.
    commons_safety_sa   Wikimedia Commons photos of safety equipment and signs (fire extinguishers, defibrillators and
                        their signs, first-aid kits, exit signs, fire alarm call points, smoke alarms, wet floor signs,
                        lifebuoys, warning and danger signs) under CC BY-SA or GFDL. Files whose words mention people
                        are left out, so picture-making may learn from it (EVENTS_SAFETY_PICTURE_MAKING_OK).
    commons_hazards_sa  Wikimedia Commons photos of hazards at home and in the street (fire, smoke, wildfires, broken
                        glass, open manholes, spills, potholes, icy and flooded roads, fallen power lines and trees,
                        sinkholes, construction sites) under CC BY-SA or GFDL: "Is there a hazard here?".
  research
    hard_hat_workers    Hard Hat Workers (credited by its copies to Northeastern University, China; 5,000 photos of
                        workplaces with hand-drawn boxes for heads with and without hard hats). Its copies state
                        "Public Domain" or CC0 (Roboflow, Kaggle, Voxel51 on Hugging Face), but no source says who
                        took the photos (they appear to be gathered from the web), so personal use only. "Is this
                        person wearing safety equipment?" -> "Yes: a hard hat." / "No: no hard hat.", and for groups
                        "How many people are wearing hard hats?".
    shwd                Safety Helmet Wearing Dataset (SHWD, njvisionpower; 7,581 photos): the code is MIT, but its
                        hard-hat photos were "got from google or baidu" and its other heads from SCUT-HEAD (research
                        use), so personal use only. Only photos with at least one hard hat are used (the SCUT-HEAD
                        classroom photos have none).
    chv                 Color Helmet and Vest (CHV; Wang, Wu, Yang, Thirunavukarasu, Evison and Zhao, Sensors 2021;
                        1,330 photos "from the Internet and open datasets"): people, high-visibility vests and hard
                        hats in four colours. "The dataset is open for free use" with no licence, and the photos'
                        owners are not named, so personal use only. "Yes: a yellow hard hat and a high-visibility
                        vest." / "Partly: a white hard hat; no high-visibility vest."
    dfire_web           D-Fire's web pictures (file names "WEB..."): the makers release D-Fire under CC0 1.0 and call
                        its pictures public domain, but these were gathered from the web and their owners are not
                        named, so personal use only (the makers' own camera frames are the open dfire_cameras pack).
                        "Is there a hazard here?" -> "Yes: there is fire and smoke." / "No: I can see no fire or
                        smoke."

Every answer comes from the source's own records or labels; nothing is written by an AI model. Nothing here gives
instructions for weapons or for harming anyone; hazard answers only say what is there. Rows whose words name a child
carry "child": True (picture-making leaves them out).

Needing sign-up or a request (cannot be downloaded automatically; EVENTS_SAFETY_SIGN_UP has the links): SH17 (CC BY-
NC-SA 4.0; labels on Kaggle), the FIRE dataset (Kaggle), Pictor-PPE (a Google Drive folder, no licence), Roboflow
Universe PPE and fire sets (each with its own licence; a free account and API key), the Wikimedia Commons Query
Service (a Wikimedia login), the NARA catalogue API v2 (a key), and the UK Health and Safety Executive's photo
library (a paid licence).

Looked at and not included: EVENTS_SAFETY_NOT_INCLUDED.

    python kit/events_safety_sources.py chv --data <empty folder> --cap 8     (a quick check)
"""

import json
import os
import random
import re
import time
import xml.etree.ElementTree as ET

import sources
from archive_sources import GRAPHIC, NEVER
from extra_sources import COMMONS_SA, NUDE, commons_get, commons_session, gdrive, parquet_picture_rows
from more_sources import fetch_shared, sentence
from personal_sources import CHILD_WORDS, first_sentences, remote_zip, zip_members
from sources import NARRATE, Source, clean, fetch_pictures

ASK_EVENT = "What event does this picture show?"
ASK_WHERE_WHEN = "Where and when was this?"
ASK_WHAT = "What is this?"
ASK_SIGN = "What does this sign mean?"
ASK_HAZARD = "Is there a hazard here?"
ASK_PPE = "Is this person wearing safety equipment?"
ASK_HATS = "How many people are wearing hard hats?"
ASK_PPE_GROUP = "Are these people wearing safety equipment?"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
NUMBERS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")
PEOPLE_WORDS = re.compile(r"\b(person|people|man|men|woman|women|girl|boy|child\w*|kids?|workers?|firefighters?|"
                          r"staff|students?|crowd|family|volunteers?|bab(y|ies)|portrait|selfie)\b", re.I)


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def number(n):
    """ "two" for 2, "15" for 15."""
    return NUMBERS[n] if 0 <= n < len(NUMBERS) else str(n)


def marked(rows, *texts):
    """Rows marked "child" when an answer names a child and "content": "graphic" when the words (answers, file title,
    categories) name the dead or injuries; [] when they name sexual violence, torture, an execution or a dead or
    injured child, or anything sexual."""
    joined = " ".join([r["answer"] for r in rows] + [t for t in texts if t])
    child = any(CHILD_WORDS.search(r["answer"]) for r in rows)
    graphic = bool(GRAPHIC.search(joined))
    if NEVER.search(joined) or NUDE.search(joined) or (graphic and CHILD_WORDS.search(joined)):
        return []
    rows = [dict(r, child=child) for r in rows]
    return [dict(r, content="graphic") for r in rows] if graphic else rows


# ----------------------------------------------------------------- Commons files under share-alike licences

def sa_ok(licence):
    """True for a copyleft Commons licence (CC BY-SA, GFDL, Free Art; never NC or ND)."""
    return bool(COMMONS_SA.match(licence)) and not re.search(r"\bN[CD]\b", licence.upper().replace("-", " "))


def commons_files(s, titles):
    """[{title, url, credit, text, categories, pageid}] for JPEG and PNG files under a copyleft licence, 50 files a
    request; text is the English caption, or else the start of the English description."""
    from extra_sources import commons_text
    out = []
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]),
                               "prop": "imageinfo|categories", "cllimit": "max", "clshow": "!hidden",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": sources.LONG_SIDE,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription",
                               "iiextmetadatalanguage": "en"})
        pages = [p for p in ((data.get("query") or {}).get("pages") or {}).values() if p.get("pageid")]
        captions = {}
        if pages:
            entities = commons_get(s, {"action": "wbgetentities", "ids": "|".join(f"M{p['pageid']}" for p in pages),
                                       "props": "labels", "languages": "en"}).get("entities", {})
            captions = {k: ((v.get("labels") or {}).get("en") or {}).get("value", "") for k, v in entities.items()}
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean(re.sub(r"<[^>]+>", " ", (meta.get("LicenseShortName") or {}).get("value") or ""))
            if not sa_ok(licence) or info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                continue
            artist = clean(re.sub(r"<[^>]+>", " ", (meta.get("Artist") or {}).get("value") or "")) or "unknown"
            artist = artist if len(artist) <= 80 else artist[:77].rsplit(" ", 1)[0] + "..."
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            out.append({"title": p["title"], "url": info["thumburl"], "pageid": p["pageid"],
                        "credit": f"{p['title']} by {artist}, {licence}, {page}",
                        "text": commons_text(captions.get(f"M{p['pageid']}"),
                                             (meta.get("ImageDescription") or {}).get("value")),
                        "categories": [c["title"].split(":", 1)[-1] for c in p.get("categories") or []]})
        time.sleep(1)
    return out


def category_files(s, category, most=200):
    """Up to most file titles of a Commons category (its first page of members only)."""
    data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                           "cmtype": "file", "cmlimit": min(500, most)})
    return [m["title"] for m in (data.get("query") or {}).get("categorymembers") or []][:most]


def caption(text, words=6, most=70):
    """A Commons caption as an answer (its first sentences, a capital and a full stop), or "" when it is shorter
    than words words."""
    text = first_sentences(clean(text), most)
    return sentence(text) if len(text.split()) >= words else ""


# ----------------------------------------------------------------- share-alike: Commons event pictures

EVENT_CLASSES = ("Q273120", "Q175331", "Q657449", "Q1413045", "Q51404", "Q898830", "Q124757", "Q49776", "Q209715",
                 "Q1417098", "Q63442071", "Q1052001", "Q201676", "Q2324916", "Q2627975", "Q40231", "Q858439",
                 "Q43109", "Q135976384", "Q16510064", "Q7944", "Q8068", "Q168983", "Q7692360", "Q8092", "Q3839081",
                 "Q8065", "Q744913", "Q1078765", "Q852190", "Q179057", "Q752783", "Q132241", "Q868557", "Q172754",
                 "Q1644573", "Q10931", "Q45382", "Q178561", "Q188055", "Q198")
EVENT_NEVER = re.compile(r"\b(massacre|genocide|pogrom|murder|lynching|execution|shooting|beheading|rape|"
                         r"holocaust|extermination)\b", re.I)
EVENT_QUERY = """SELECT ?e ?eLabel ?cat ?t ?tp ?s ?sp ?f ?fp ?l ?lp ?locLabel ?countryLabel ?partLabel WHERE {
  ?e wdt:P31 wd:%s ; wdt:P373 ?cat .
  OPTIONAL { ?e p:P585/psv:P585 [ wikibase:timeValue ?t ; wikibase:timePrecision ?tp ] }
  OPTIONAL { ?e p:P580/psv:P580 [ wikibase:timeValue ?s ; wikibase:timePrecision ?sp ] }
  OPTIONAL { ?e p:P582/psv:P582 [ wikibase:timeValue ?f ; wikibase:timePrecision ?fp ] }
  OPTIONAL { ?e p:P619/psv:P619 [ wikibase:timeValue ?l ; wikibase:timePrecision ?lp ] }
  FILTER(BOUND(?t) || BOUND(?s) || BOUND(?l))
  OPTIONAL { ?e wdt:P276 ?loc }
  OPTIONAL { ?e wdt:P17 ?country }
  OPTIONAL { ?e wdt:P361 ?part }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} LIMIT %d"""
SHORT_COUNTRIES = {"United States": "USA", "United States of America": "USA", "United Kingdom": "UK",
                   "People's Republic of China": "China", "Russian Federation": "Russia"}


def time_parts(value, precision):
    """(year, month, day, precision) from a Wikidata time and its precision, as in packs/events_safety_packs.py:
    None before the year 1; only the year before 1583 or at year precision."""
    m = re.match(r"^\+?(-?)(\d{1,4})-(\d\d)-(\d\d)", str(value or ""))
    if not m or m.group(1) == "-" or int(m.group(2)) < 1:
        return None
    year, month, day, precision = int(m.group(2)), int(m.group(3)), int(m.group(4)), int(precision or 9)
    if precision < 9:
        return (year, 0, 0, precision)
    if year < 1583 or precision == 9:
        return (year, 0, 0, 9)
    return (year, month, 0, 10) if precision == 10 else (year, month, day, 11)


def day_words(year, month=0, day=0):
    """ "20 July 1969", "July 1969" or "1969"."""
    return f"{day} {MONTHS[month - 1]} {year}" if month and day else f"{MONTHS[month - 1]} {year}" if month else \
        str(year)


def when_words(point=None, start=None, end=None):
    """When an event happened in words ("on 20 July 1969", "from 28 July 1914 to 11 November 1918", "in the
    1960s"); ""."""
    def single(p):
        """One date with "in" or "on"."""
        year, month, day, precision = p
        if precision == 8:
            return f"in the {year // 10 * 10}s"
        if precision == 7:
            century = (year - 1) // 100 + 1
            suffix = "th" if 10 <= century % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(century % 10, "th")
            return f"in the {century}{suffix} century"
        return ("on " if day else "in ") + day_words(year, month, day)
    if point:
        return single(point)
    if start and end and end[:3] != start[:3] and min(start[3], end[3]) >= 9:
        return f"from {day_words(*start[:3])} to {day_words(*end[:3])}"
    return single(start) if start else ""


def the(name):
    """ "the" before event names like "Battle of Hastings", "2012 Summer Olympics" or "Western Front"."""
    if name.lower().startswith("the "):
        return "the " + name[4:]
    if re.match(r"^\d", name) or re.search(r"\b(Front|War|Wars|Revolution|Games|Olympics|Campaign|Offensive|Crisis|"
                                           r"Movement|Uprising|Expedition|Rebellion|Exhibition|Exposition|Parade|March|"
                                           r"Festival|Carnival|Fair|Rally|Strike|Riot|Coronation|Funeral|Wedding|"
                                           r"Earthquake)$", name) \
            or re.match(r"^[A-Z][\w'’-]*( [A-Z][\w'’-]*)? (of|on|to|at|for|in|against|between) ", name):
        return "the " + name
    return name


def place_words(place):
    """A place as it follows "in" ("the USA", "Paris, France")."""
    return sources.place_words(place)


def wikidata_events(s, qclass, most):
    """[{qid, name, category, when, place, part}] for event items of one class with a date and a Commons category."""
    import requests  # noqa: F401 - s is a requests session
    bindings = []
    for attempt in range(4):
        try:
            r = s.get(WIKIDATA_SPARQL, params={"query": EVENT_QUERY % (qclass, most * 4), "format": "json"},
                      timeout=120)
            if r.status_code == 200:
                bindings = r.json()["results"]["bindings"]
                break
        except Exception:  # noqa: BLE001 - busy: wait and try again
            pass
        time.sleep(10 * (attempt + 1))

    def label(b, name):
        """An English label, or "" (the label service gives the Q-id when there is none)."""
        text = clean((b.get(name) or {}).get("value"))
        return "" if re.match(r"^Q\d+$", text) else text

    events = {}
    for b in bindings:
        qid = b["e"]["value"].rsplit("/", 1)[-1]
        name = label(b, "eLabel")
        if qid in events or not name or EVENT_NEVER.search(name):
            continue
        launch = time_parts((b.get("l") or {}).get("value"), (b.get("lp") or {}).get("value"))     # P619
        when = when_words(time_parts((b.get("t") or {}).get("value"), (b.get("tp") or {}).get("value")),
                          time_parts((b.get("s") or {}).get("value"), (b.get("sp") or {}).get("value")),
                          time_parts((b.get("f") or {}).get("value"), (b.get("fp") or {}).get("value")))
        when = when or ("launched " + when_words(launch) if launch else "")
        country = label(b, "countryLabel")
        country = SHORT_COUNTRIES.get(country, country)
        location = label(b, "locLabel")
        place = f"{location}, {country}" if location and country and location != country else location or country
        events[qid] = {"qid": qid, "name": name, "category": clean(b["cat"]["value"]), "when": when, "place": place,
                       "part": label(b, "partLabel")}
    return list(events.values())


def event_rows(event, f):
    """The kit rows of one Commons file showing an event, or [] (also when the file's title names a year outside the
    event's dates: a file filed under the wrong year's event)."""
    years = {int(y) for y in re.findall(r"\b(1[89]\d\d|20[0-2]\d)\b", f["title"])}
    known = [int(y) for y in re.findall(r"\b(\d{4})\b", event["when"])]
    if years and known and not any(min(known) <= y <= max(known) for y in years):
        return []
    credit = f"{f['credit']}; event facts from Wikidata ({event['qid']}, CC0)"
    place = sources.place_fields({"place": event["place"], "place_kind": "depicted"}) if event["place"] else {}
    name = re.sub(r"(,\s*[^,]+)*,\s*(1[0-9]|20)\d\d$", "", event["name"]).strip() or event["name"]
    say_place = event["place"] and (name == event["name"] or event["place"] not in event["name"])
    answer = f"This shows {the(name)}" + (f", in {place_words(event['place'])}" if say_place else "") \
        + (f", {event['when']}" if event["when"] else "") + "."
    if event["part"] and event["part"].lower() not in event["name"].lower():
        answer += f" It was part of {the(event['part'])}."
    rows = []
    text = caption(f["text"])
    if text:
        rows.append({"question": NARRATE, "answer": text, "split": "", "credit": credit, **place})
    rows.append({"question": ASK_EVENT, "answer": answer[0].upper() + answer[1:], "split": "", "credit": credit,
                 **place})
    if event["place"] and event["when"]:
        rows.append({"question": ASK_WHERE_WHEN, "answer": f"This was in {place_words(event['place'])}, "
                                                           f"{event['when']}.", "split": "", "credit": credit, **place})
    return marked(rows, f["title"], " ".join(f["categories"]))


def prepare_commons_events_sa(source, data_dir, work, cap, per_event=3):
    """Commons event pictures under CC BY-SA or GFDL: the event classes taken in turn, a few files from each event
    (its "depicts" files first, then its category's files)."""
    s, rng = commons_session(), random.Random(601)
    want = int((cap + source.test) * 1.2) + 4
    queues = []
    for qclass in EVENT_CLASSES:
        events = wikidata_events(s, qclass, max(20, want // len(EVENT_CLASSES) * 2))
        rng.shuffle(events)
        queues.append(events)
        time.sleep(1)
    say(f"  Wikidata: {sum(map(len, queues))} dated events with a Commons category")
    items, pictures = [], 0
    while pictures < want and any(queues):
        for events in queues:
            if not events or pictures >= want:
                continue
            event = events.pop()
            data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": 20,
                                   "srsearch": f"haswbstatement:P180={event['qid']}"})
            titles = [h["title"] for h in (data.get("query") or {}).get("search") or []]
            titles = list(dict.fromkeys(titles + category_files(s, event["category"], 60)))
            rng.shuffle(titles)
            got = 0
            for f in commons_files(s, titles[:per_event * 4]):
                rows = event_rows(event, f) if got < per_event else []
                if rows:
                    name = f"event-sa-{f['pageid']}.jpg"
                    items += [(name, f["url"], r) for r in rows]
                    got += 1
                    pictures += 1
    say(f"  Fetching {pictures} Commons event pictures (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: Commons safety equipment, hazards

SAFETY_EQUIPMENT = {
    "Fire extinguishers": (ASK_WHAT, "It shows a fire extinguisher."),
    "Automated external defibrillators": (ASK_WHAT, "It shows an automated external defibrillator (AED), a device "
                                                    "used to restart the heart in a cardiac arrest."),
    "AED signs": (ASK_SIGN, "It is a sign showing where an automated external defibrillator (AED) is."),
    "First aid kits": (ASK_WHAT, "It shows a first aid kit."),
    "Safety showers": (ASK_WHAT, "It shows an emergency safety shower, used to wash chemicals off the body; many "
                                 "have an eyewash station."),
    "Emergency exit signs": (ASK_SIGN, "It is an emergency exit sign: it shows the way out."),
    "Exit signs": (ASK_SIGN, "It is an exit sign: it shows the way out."),
    "Manual call points": (ASK_WHAT, "It shows a fire alarm call point: pressing it sounds the fire alarm."),
    "Smoke detectors": (ASK_WHAT, "It shows a smoke alarm (smoke detector)."),
    "Carbon monoxide detectors": (ASK_WHAT, "It shows a carbon monoxide alarm."),
    "Fire blankets": (ASK_WHAT, "It shows a fire blanket."),
    "Fire hose reels": (ASK_WHAT, "It shows a fire hose reel."),
    "Fire extinguisher signs": (ASK_SIGN, "It is a sign showing where a fire extinguisher is."),
    "Lifebuoys": (ASK_WHAT, "It shows a lifebuoy, a ring to throw to someone in the water."),
    "Wet floor signs": (ASK_SIGN, "It is a wet floor warning sign: the floor may be slippery."),
    "Traffic cones": (ASK_WHAT, "It shows traffic cones, which mark a hazard or roadworks."),
    "Warning signs": (None, None), "Danger signs": (None, None), "Hazard signs": (None, None),
}
HAZARDS = {
    "Broken glass": "Yes: there is broken glass, which can cut.",
    "Manholes": "Yes: there is an open manhole, a hole someone could fall into.",
    "Construction sites": "Yes: this is a construction site, with hazards such as machines, holes and falling "
                          "objects.",
    "Building fires": "Yes: a building is on fire.", "Burning buildings": "Yes: a building is on fire.",
    "House fires": "Yes: a house is on fire.", "Wildfires": "Yes: there is a wildfire, a fire burning through open "
                                                            "land.",
    "Oil spills": "Yes: oil has been spilled.",
    "Flooded roads": "Yes: the road is flooded; the water may be deeper or faster than it looks.",
    "Icy roads": "Yes: the road is icy and slippery.", "Potholes": "Yes: there is a pothole in the road.",
    "Downed power lines": "Yes: power lines have fallen down; they may still carry electricity.",
    "Fallen trees": "Yes: a tree has fallen.", "Sinkholes": "Yes: there is a sinkhole, where the ground has fallen in.",
    "Smoke": "Yes: there is smoke, which may come from a fire.",
}
HAZARD_NEEDS = {"Manholes": r"\bopen(ed)?\b", "Smoke": r"\b(fire|burning|smoke from)\b",
                "Downed power lines": r"\b(power|electric\w*) ?lines?\b|\bwires?\b"}
NOT_A_PHOTO = re.compile(r"\b(art|drawings?|diagrams?|illustrations?|icons?|logos?|maps?|videos?|paintings?|stamps?|"
                         r"toys?|models?|sculptures?|SVG|charts?|animations?)\b", re.I)


def safety_rows(s, table, want, rng, people_ok, prefix):
    """[(file name, address, row)] from a table {category: (question, answer)} (an answer of None: the caption
    only), the categories taken in turn, a few copyleft files at a time."""
    queues = []
    for category in table:
        titles = [t for t in category_files(s, category, 300) if not NOT_A_PHOTO.search(t)]
        rng.shuffle(titles)
        queues.append((category, titles))
    items, pictures = [], 0
    while pictures < want and any(q[1] for q in queues):
        for category, titles in queues:
            if not titles or pictures >= want:
                continue
            batch, titles[:] = titles[:12], titles[12:]
            question, answer = table[category]
            for f in commons_files(s, batch):
                words = f"{f['title']} {f['text']}"
                if (not people_ok and PEOPLE_WORDS.search(words)) or \
                        (category in HAZARD_NEEDS and not re.search(HAZARD_NEEDS[category], words, re.I)):
                    continue
                rows = [{"question": question, "answer": answer, "split": "", "credit": f["credit"]}] if answer \
                    else []
                text = caption(f["text"])
                if text:
                    rows.append({"question": NARRATE, "answer": text, "split": "", "credit": f["credit"]})
                rows = marked(rows, f["title"], " ".join(f["categories"])) if rows else []
                if rows:
                    items += [(f"{prefix}-{f['pageid']}.jpg", f["url"], r) for r in rows]
                    pictures += 1
    return items, pictures


def prepare_commons_safety_sa(source, data_dir, work, cap):
    """Commons photos of safety equipment and signs under CC BY-SA or GFDL, files whose words mention people left
    out: "What is this?" or "What does this sign mean?" from the category, and the caption."""
    s, rng = commons_session(), random.Random(607)
    table = {k: v for k, v in SAFETY_EQUIPMENT.items()}
    items, pictures = safety_rows(s, table, int((cap + source.test) * 1.2) + 2, rng, False, "safety-sa")
    say(f"  Fetching {pictures} Commons safety equipment photos (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_commons_hazards_sa(source, data_dir, work, cap):
    """Commons photos of hazards under CC BY-SA or GFDL: "Is there a hazard here?" from the category, and the
    caption."""
    s, rng = commons_session(), random.Random(613)
    table = {k: (ASK_HAZARD, v) for k, v in HAZARDS.items()}
    items, pictures = safety_rows(s, table, int((cap + source.test) * 1.2) + 2, rng, True, "hazard-sa")
    say(f"  Fetching {pictures} Commons hazard photos (share-alike).")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- research: hard hats (head counts)

def hat_rows(hats, bare):
    """The answer rows for a photo with hats heads wearing a hard hat and bare heads without; [] for none or a
    crowd (more than 12)."""
    total = hats + bare
    if total == 0 or total > 12:
        return []
    if total == 1:
        return [{"question": ASK_PPE, "answer": "Yes: a hard hat." if hats else "No: no hard hat."}]
    if bare == 0:
        answer = ("Both people" if total == 2 else f"All {number(total)} people") + \
            " whose heads can be seen are wearing hard hats."
    elif hats == 0:
        answer = ("Neither of the two people" if total == 2 else f"None of the {number(total)} people") + \
            " whose heads can be seen is wearing a hard hat."
    else:
        answer = f"Of the {number(total)} people whose heads can be seen, {number(hats)} " + \
                 ("is" if hats == 1 else "are") + f" wearing a hard hat and {number(bare)} " + \
                 ("is" if bare == 1 else "are") + " not."
    return [{"question": ASK_HATS, "answer": answer}]


HARD_HAT = "https://huggingface.co/datasets/Voxel51/hard-hat-detection/resolve/main/"
HARD_HAT_CREDIT = "Hard Hat Workers dataset (credited to Northeastern University, China; copy by Voxel51 on Hugging " \
                  "Face, https://huggingface.co/datasets/Voxel51/hard-hat-detection, 'cc0-1.0' stated)"


def prepare_hard_hat_workers(source, data_dir, work, cap):
    """Hard Hat Workers (Voxel51's copy on Hugging Face): its samples.json (9 MB) gives each photo's boxes: "helmet"
    (a head with a hard hat), "head" (without) and "person". Photos with one head: "Is this person wearing safety
    equipment?"; with 2 to 12: "How many people are wearing hard hats?". Each photo is fetched from the copy."""
    samples = sources.get_json(HARD_HAT + "samples.json") if hasattr(sources, "get_json") else None
    if samples is None:
        import requests
        samples = requests.get(HARD_HAT + "samples.json", timeout=300,
                               headers={"User-Agent": sources.USER_AGENT}).json()
    groups = {"one": [], "group": []}
    for sample in samples["samples"]:
        labels = [d.get("label") for d in ((sample.get("ground_truth") or {}).get("detections") or [])]
        rows = hat_rows(labels.count("helmet"), labels.count("head"))
        if rows:
            groups["one" if rows[0]["question"] == ASK_PPE else "group"].append((sample["filepath"], rows[0]))
    rng = random.Random(617)
    for v in groups.values():
        rng.shuffle(v)
    want = cap + source.test
    chosen = groups["one"][:want // 2] + groups["group"][:want - min(len(groups["one"]), want // 2)]
    items = [(re.sub(r"\W", "_", path.rsplit("/", 1)[-1].rsplit(".", 1)[0]) + ".jpg", HARD_HAT + path,
              dict(row, split="", credit=f"{HARD_HAT_CREDIT}, {path}", child=False)) for path, row in chosen]
    say(f"  Fetching {len(items)} Hard Hat Workers photos.")
    return fetch_pictures(items, os.path.join(data_dir, source.key), workers=6)


SHWD_URL, SHWD_SIZE = gdrive("1qWm7rrwvjAWs1slymbrLaCf7Q-wnGLEX"), 1117970537
SHWD_CREDIT = "Safety Helmet Wearing Dataset (SHWD), njvisionpower, https://github.com/njvisionpower/" \
              "Safety-Helmet-Wearing-Dataset (code MIT; photos from web searches and SCUT-HEAD)"


def prepare_shwd(source, data_dir, work, cap):
    """SHWD (VOC2028.zip, 1.1 GB on Google Drive, read piece by piece): its Pascal VOC boxes "hat" (a head with a
    hard hat) and "person" (a head without). Only photos with at least one hard hat (the SCUT-HEAD classroom photos
    have none); the annotations are read in the zip's order until about three times the photos needed are found."""
    z = remote_zip(SHWD_URL, SHWD_SIZE)
    want = cap + source.test
    found = []
    for name in z.namelist():
        if not re.match(r"^VOC2028/Annotations/[^/]+\.xml$", name):
            continue
        try:
            root = ET.fromstring(z.read(name))
        except Exception:  # noqa: BLE001 - an unreadable annotation is skipped
            continue
        labels = [clean(o.findtext("name")).lower() for o in root.iter("object")]
        if "hat" not in labels:
            continue
        rows = hat_rows(labels.count("hat"), labels.count("person"))
        stem = name.rsplit("/", 1)[-1][:-4]
        if rows:
            found.append((f"VOC2028/JPEGImages/{stem}.jpg", dict(rows[0], split="", child=False,
                                                                credit=f"{SHWD_CREDIT}, {stem}.jpg")))
        if len(found) >= want * 3:
            break
    z.close()
    random.Random(619).shuffle(found)
    say(f"  SHWD: reading {min(want, len(found))} photos.")
    return zip_members(source, data_dir, work, lambda: remote_zip(SHWD_URL, SHWD_SIZE), found[:want])


CHV_URL, CHV_SIZE = gdrive("1fdGn67W0B7ShpBDbbQpUF0ScPQa4DR0a"), 439733771
# CHV's classes (checked from the pictures: the colour inside each helmet box): 0 person, 1 vest, 2-5 hard hats.
CHV_HATS = {2: "blue", 3: "red", 4: "white", 5: "yellow"}
CHV_CREDIT = "Color Helmet and Vest (CHV) dataset (Wang, Wu, Yang, Thirunavukarasu, Evison and Zhao, Sensors 21(10) " \
             "3478, 2021), https://github.com/ZijianWang-ZW/PPE_detection ('open for free use'; photos from the " \
             "Internet and open datasets)"


def chv_rows(classes):
    """The answer row for one CHV photo from its box classes, or None (no person, or a crowd of more than 12)."""
    people, vests = classes.count(0), classes.count(1)
    hats = [CHV_HATS[c] for c in classes if c in CHV_HATS]
    if people == 0 or people > 12:
        return None
    if people == 1:
        hat = f"a {hats[0]} hard hat" if len(hats) == 1 else "a hard hat" if hats else ""
        vest = "a high-visibility vest" if vests else ""
        if hat and vest:
            answer = f"Yes: {hat} and {vest}."
        elif hat or vest:
            answer = f"Partly: {hat or vest}; no {'high-visibility vest' if hat else 'hard hat'}."
        else:
            answer = "No: no hard hat and no high-visibility vest."
        return {"question": ASK_PPE, "answer": answer}
    h, v = min(len(hats), people), min(vests, people)
    colours = sorted(set(hats))
    colour_words = f" ({', '.join(colours[:-1]) + ' and ' + colours[-1] if len(colours) > 1 else colours[0]})" \
        if colours else ""

    def how_many(n, thing, things):
        """ "all three are wearing hard hats", "one is wearing a hard hat", "none is wearing a hard hat"."""
        if n == people:
            return f"{'both' if n == 2 else 'all'} are wearing {things}"
        if n == 0:
            return f"none is wearing {thing}"
        return f"{number(n)} {'is' if n == 1 else 'are'} wearing {thing if n == 1 else things}"
    answer = f"Of the {number(people)} people, {how_many(h, 'a hard hat', 'hard hats')}{colour_words if h else ''}, " \
             f"and {how_many(v, 'a high-visibility vest', 'high-visibility vests')}."
    return {"question": ASK_PPE_GROUP, "answer": answer}


def prepare_chv(source, data_dir, work, cap):
    """CHV (CHV_dataset.zip, 440 MB on Google Drive, read piece by piece): its YOLO boxes for people, vests and hard
    hats of four colours. One person: "Is this person wearing safety equipment?"; 2 to 12: "Are these people
    wearing safety equipment?" with counts. Its test list gives the test pictures."""
    z = remote_zip(CHV_URL, CHV_SIZE)
    names = set(z.namelist())
    test = set(z.read("CHV_dataset/data split/test.txt").decode().split()) \
        if "CHV_dataset/data split/test.txt" in names else set()
    groups = {"one": [], "group": []}
    for name in sorted(names):
        if not re.match(r"^CHV_dataset/annotations/[^/]+\.txt$", name):
            continue
        classes = [int(line.split()[0]) for line in z.read(name).decode(errors="replace").splitlines()
                   if line.split() and line.split()[0].isdigit()]
        row = chv_rows(classes)
        picture = name.replace("/annotations/", "/images/")[:-4] + ".jpg"
        if row and picture in names:
            row = dict(row, split="test" if picture in test else "", child=False,
                       credit=f"{CHV_CREDIT}, {picture.rsplit('/', 1)[-1]}")
            groups["one" if row["question"] == ASK_PPE else "group"].append((picture, row))
    z.close()
    from big_sources import even_pick
    chosen = even_pick({k: [(p, json.dumps(r)) for p, r in v] for k, v in groups.items()}, cap + source.test, 631)
    chosen = [(p, json.loads(r)) for p, r in chosen]
    say(f"  CHV: reading {len(chosen)} photos.")
    return zip_members(source, data_dir, work, lambda: remote_zip(CHV_URL, CHV_SIZE), chosen)


# ----------------------------------------------------------------- research: D-Fire's web pictures

DFIRE_REPO = "badsaarow/d-fire"
DFIRE_CREDIT = "D-Fire (Gaia, solutions on demand; de Venâncio, Lisboa and Barbosa, 2022), " \
               "https://github.com/gaiasd/DFireDataset ('CC0 1.0' stated; this picture was gathered from the web)"


def dfire_answer(label):
    """ "Is there a hazard here?" from a frame's YOLO boxes (class 0 smoke, class 1 fire, from the makers'
    dfire.yaml)."""
    kinds = {line.split()[0] for line in (label or "").splitlines() if line.split()}
    if "1" in kinds and "0" in kinds:
        return "Yes: there is fire and smoke."
    if "1" in kinds:
        return "Yes: there is fire."
    if "0" in kinds:
        return "Yes: there is smoke, which may come from a fire."
    return "No: I can see no fire or smoke."


def prepare_dfire_web(source, data_dir, work, cap):
    """D-Fire's web pictures (file names "WEB...") from the copy on Hugging Face (parquet files holding the pictures,
    read one part at a time): "Is there a hazard here?" from the hand-drawn fire and smoke boxes, about a third each
    with fire, with smoke only and with neither."""
    quota = {k: (cap + source.test) // 3 + 1 for k in ("fire", "smoke", "none")}

    def text_of(r):
        """(picture id, row) for a web picture whose kind still has room, or None."""
        name = str(r.get("filename") or "")
        answer = dfire_answer(r.get("label"))
        kind = "none" if answer.startswith("No") else "fire" if answer.startswith("Yes: there is fire") else "smoke"
        if not name.startswith("WEB") or quota[kind] <= 0:
            return None
        quota[kind] -= 1
        return name, {"question": ASK_HAZARD, "answer": answer, "split": "", "child": False,
                      "credit": f"{DFIRE_CREDIT}, {name}"}
    return parquet_picture_rows(source, data_dir, DFIRE_REPO, r"^data/train-0000[4-8]", "image", text_of, cap, 641)


# ----------------------------------------------------------------- needing sign-up, and not included

EVENTS_SAFETY_SIGN_UP = {
    "SH17: 8,099 Pexels photos of workers with 17 kinds of PPE boxes (helmets, vests, gloves, glasses, masks, "
    "earmuffs, shoes ...), CC BY-NC-SA 4.0":
        "https://www.kaggle.com/datasets/mugheesahmad/sh17-dataset-for-ppe-detection : a Kaggle account is needed "
        "for the labels (the photos themselves can be listed from https://github.com/ahmadmughees/SH17dataset , "
        "but not the labels). Non-commercial; the makers add 'for educational, research, and analysis purposes'.",
    "FIRE dataset (fire and non-fire photos, Kaggle phylake1337)":
        "https://www.kaggle.com/datasets/phylake1337/fire-dataset : a Kaggle account is needed; its licence is "
        "shown only on the Kaggle page after login and could not be read from here.",
    "Pictor-PPE (Pictor-v3: 774 crowd-sourced and 698 web-mined photos of construction workers, hats and vests)":
        "https://github.com/ciber-lab/pictor-ppe : the pictures are in a Google Drive folder (a folder cannot be "
        "downloaded by a program); no licence is stated, so research or personal use only.",
    "Roboflow Universe PPE and fire sets (Hard Hats, Construction Site Safety and many others)":
        "https://universe.roboflow.com : a free Roboflow account and API key; each set shows its own licence.",
    "Wikimedia Commons Query Service (finds every file that 'depicts' an event at once)":
        "https://commons-query.wikimedia.org : a Wikimedia account login is needed; the kit uses the Commons search "
        "instead.",
    "NARA catalogue API v2": "https://www.archives.gov/research/catalog/help/api : an API key; the open nara_events "
                             "pack uses the catalogue's public search instead.",
    "UK Health and Safety Executive photo library (Crown copyright)":
        "https://solutions.hse.gov.uk (Crown copyright material): HSE's photos are licensed for a fee, not under "
        "the Open Government Licence (its images and logos are excluded from the OGL).",
}

EVENTS_SAFETY_NOT_INCLUDED = {
    "Roboflow 'Hard Hats' copy (keremberke/hard-hat-detection on Hugging Face, CC BY 4.0 stated)":
        "every picture was stretched to a 640 by 640 square (distorted shapes teach a describer wrong proportions); "
        "the same kind of photos come unstretched in hard_hat_workers, and the photos' origin is not stated.",
    "IITU Safety Helmet Dataset (ersace on Hugging Face, CC BY 4.0 stated)": "access is restricted (a Hugging Face "
                                                                            "login and the owner's approval).",
    "UniDataPro and other commercial fire, smoke and PPE sets (CC BY-NC-ND samples)": "small samples of paid "
                                                                                      "datasets; the full sets are "
                                                                                      "sold.",
    "OSHA and NIOSH websites (public domain)": "no picture list a program can read; OSHA's photos reach the open "
                                              "safety_training pack through Wikimedia Commons and NIOSH's through "
                                              "CDC PHIL.",
    "D-Fire's third-party pictures (file names 'PublicDataset...': HPWREN, FESB wildfire images, FireNet)":
        "not in the Hugging Face copy, and the makers say they 'remain subject to the terms of their original "
        "providers'.",
}


# ----------------------------------------------------------------- the table

def research(summary):
    """A research-terms summary that also says it is for personal, non-commercial use."""
    return summary + " Personal, non-commercial use only."


EVENTS_SAFETY_SOURCES = [
    Source("commons_events_sa", "Wikimedia Commons pictures of historical events, with place and date (share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page); event facts from Wikidata (CC0)",
           "Wikimedia Commons contributors, each file under CC BY-SA or GFDL with its author named, "
           "https://commons.wikimedia.org ; event names, dates and places from Wikidata, https://www.wikidata.org "
           "(CC0)", "share-alike", 2500, 20, prepare_commons_events_sa, "about 1 GB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("commons_safety_sa", "Wikimedia Commons photos of safety equipment and signs (share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page)",
           "Wikimedia Commons contributors, each file under CC BY-SA or GFDL with its author named, "
           "https://commons.wikimedia.org", "share-alike", 1500, 20, prepare_commons_safety_sa,
           "about 500 MB of pictures", terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("commons_hazards_sa", "Wikimedia Commons photos of hazards at home and in the street (share-alike)",
           "Each file CC BY-SA or GFDL (its licence on its Commons page)",
           "Wikimedia Commons contributors, each file under CC BY-SA or GFDL with its author named, "
           "https://commons.wikimedia.org", "share-alike", 1500, 20, prepare_commons_hazards_sa,
           "about 500 MB of pictures", terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    Source("hard_hat_workers", "Hard Hat Workers: are the people wearing hard hats? (personal use)",
           "'Public Domain' or CC0 stated by its copies (Roboflow, Kaggle, Voxel51); who took the photos is not "
           "stated", HARD_HAT_CREDIT, "research", 2500, 20, prepare_hard_hat_workers, "about 1 GB of photos",
           terms="https://huggingface.co/datasets/Voxel51/hard-hat-detection",
           terms_summary=research("Its copies call it public domain (CC0), but no source names who took the "
                                  "photos, which appear to be gathered from the web, so the rights in them are "
                                  "unclear.")),
    Source("shwd", "Safety Helmet Wearing Dataset: hard hats on building sites (personal use)",
           "Code MIT (github.com/njvisionpower/Safety-Helmet-Wearing-Dataset); photos from Google and Baidu searches "
           "and SCUT-HEAD, with no licence for them", SHWD_CREDIT, "research", 2000, 20, prepare_shwd,
           "1.1 GB, read in pieces", terms="https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset",
           terms_summary=research("The MIT licence covers the code; the photos were taken from web searches and "
                                  "from SCUT-HEAD (research use), and nobody has given rights to them.")),
    Source("chv", "CHV: hard hats in four colours and high-visibility vests (personal use)",
           "'Open for free use', no licence (github.com/ZijianWang-ZW/PPE_detection); photos from the Internet and "
           "open datasets", CHV_CREDIT, "research", 1300, 30, prepare_chv, "440 MB, read in pieces",
           terms="https://github.com/ZijianWang-ZW/PPE_detection",
           terms_summary=research("The makers say the dataset is 'open for free use' but give no licence, and the "
                                  "photos were gathered from the Internet without naming their owners.")),
    Source("dfire_web", "D-Fire web pictures: is there fire or smoke? (personal use)",
           "CC0 1.0 stated by the makers (github.com/gaiasd/DFireDataset), who call the pictures public domain; "
           "these were gathered from the web", DFIRE_CREDIT, "research", 3000, 20, prepare_dfire_web,
           "up to 1.5 GB, read in parts", terms="https://github.com/gaiasd/DFireDataset",
           terms_summary=research("The makers release D-Fire under CC0 and say its pictures are in the public "
                                  "domain, but these pictures were gathered from the web and their owners are not "
                                  "named.")),
]

# The collections a picture-making model may learn from: signs and equipment without people only.
EVENTS_SAFETY_PICTURE_MAKING_OK = {"commons_safety_sa"}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one events or safety collection.")
    parser.add_argument("key", choices=[s.key for s in EVENTS_SAFETY_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in EVENTS_SAFETY_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="events-safety-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, "
          f"{sum(1 for r in rows if r.get('content') == 'graphic')} rows marked graphic, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
