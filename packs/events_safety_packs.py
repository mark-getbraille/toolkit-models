"""Pack builders for two kinds of picture: HISTORICAL EVENTS (noted by place and time) and SAFETY TRAINING (safety
signs, safety equipment, hazards and safety posters from around the world). They are used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus, where they apply:
  "place"     where the event happened or the photo was taken (places.py; "place_kind": "depicted" for an event
              place taken from Wikidata, since a painting of a battle shows that place too);
  "child"     True when the caption names a child (expression_packs.CHILD), so picture-making leaves it out;
  "content"   "graphic" when the picture's words name the dead, wounds or casualties (archive_packs.GRIM). Such
              pictures are kept and described plainly, by the owner's rule. Still left out whatever the record says
              (archive_packs.not_shown): anything sexual, sexual violence, torture or execution scenes (and their
              propaganda), and pictures naming both a child and death or injury.
A picture with more than one question comes once with its JPEG and then as (None, None, row) rows pointing at the
same picture (food_packs.with_twins). The limit counts pictures. Nothing is written by an AI model: every answer is
built from the source's own records (captions, Wikidata statements, catalogue fields, dataset labels).

The questions:
  "What event does this picture show?"  "This shows the Apollo 11 Moon landing, in the Sea of Tranquillity, on 20
                                         July 1969." (only from records: Wikidata or the catalogue's own words)
  "Describe this picture."               the caption the source wrote
  "Where and when was this?"             "This was in Washington, D.C., USA, on 4 March 1913."
  "What does this sign mean?"            "This is the ISO 7010 sign W012: warning, electricity."
  "What is this?"                        safety equipment ("It shows a fire extinguisher.")
  "Is there a hazard here?"              "Yes: there is fire and smoke." / "No: I can see no fire or smoke."
  "What does this poster say?"           a safety poster's own words (Library of Congress WPA posters)
Nothing here gives instructions for weapons or for harming anyone; hazard answers only say what is there.

HISTORICAL EVENTS (the whole world and all eras: protests and marches, coronations, inaugurations, royal weddings and
state funerals, elections and referendums, Olympic Games and other sporting events, disasters, the Moon landings
and other spaceflights, festivals, world's fairs, revolutions, battles and wars):
  commons_events     Wikimedia Commons pictures of events found through Wikidata (CC0): event items of about 40
                     kinds (EVENT_CLASSES) with a date (P585 point in time, or P580 start and P582 end), and their
                     location (P276), country (P17) and the larger event they were part of (P361). For each event,
                     the Commons files whose structured data "depicts" (P180) the event and the files of the event's
                     Commons category (P373). Only files whose own licence is CC0, public domain or CC BY (never
                     BY-SA, NC or ND), author credited. Massacres, genocides and murders are not taken as events.
  loc_events         Library of Congress news photographs, "no known restrictions on publication": the George Grantham
                     Bain Collection (New York news agency, about 1900-1920s) and Harris & Ewing (Washington, D.C.,
                     1905-1945), found with event words (parades, suffrage marches, inaugurations, funerals, fires,
                     floods, strikes, Olympic Games ...). The kind of event comes from the record's own title and
                     subject headings ("Parades & processions" -> "a parade"); the place and date from the record.
                     (documentary_packs.py has other LoC collections: Highsmith, FSA/OWI, Photochrom, Matson.)
  nara_events        US National Archives catalogue (catalog.archives.gov): photographs found with event words,
                     "Unrestricted" for use (US government work, public domain), with the record's date and caption.
                     The three series in archive_packs.py's nara pack (DOCUMERICA, the War Relocation Authority,
                     Ansel Adams) are left out here.
  europeana_events   Europeana: English-language records of prints, drawings and photographs of events, whose own
                     rights statement is CC0, the Public Domain Mark or CC BY. Europeana's date is the date the
                     picture was made (an engraving of a funeral in 1603 may be from 1791), so these rows say what
                     event is shown and when the picture was made, not when the event happened.

SAFETY TRAINING:
  safety_signs       Wikimedia Commons drawings (SVG files rendered to PNG by Commons, flattened onto white): the ISO
                     7010 safety signs (CC0 or public domain, their meaning from the file's own caption: "This is
                     the ISO 7010 sign W012: warning, electricity."), the nine GHS hazard pictograms (public
                     domain), and road and traffic signs of many countries (the "Diagrams of <kind> road signs of
                     <country>" categories; files CC0, public domain or CC BY, meaning from the English caption).
  commons_safety_photos
                     Wikimedia Commons photos of safety equipment (fire extinguishers, defibrillators (AEDs) and
                     their signs, first-aid kits, safety showers and eyewash stations, emergency exit signs, fire
                     alarm call points, smoke and carbon monoxide alarms, fire blankets, hose reels, lifebuoys) and
                     of hazards at home and in the street (fire, smoke, wildfires, broken glass, open manholes, wet
                     floor signs, spills, potholes, icy and flooded roads, fallen power lines and trees, sinkholes,
                     construction sites). Files CC0, public domain or CC BY. The answer comes from the category the
                     photo is filed in; the file's English caption is a second row.
  safety_training    Government safety posters and workplace safety photographs in the public domain: Library of
                     Congress posters (the WPA posters of 1936-1943 and others, "no known restrictions"), Commons
                     safety posters and photos of the US Occupational Safety and Health Administration (OSHA, US
                     government work), and CDC Public Health Image Library photographs of protective equipment
                     (NIOSH and CDC, public domain; each item's own rights field is checked).
  dfire_cameras      D-Fire (Gaia, solutions on demand, Brazil; de Venâncio, Lisboa and Barbosa, 2022): frames from the
                     makers' own wildfire-watch cameras (file names "AoF..."), released under CC0 1.0, with the
                     hand-drawn fire and smoke boxes: "Is there a hazard here?". D-Fire's web pictures and third-
                     party pictures are not in this pack (their origin is not the makers' own; they are a research
                     kit entry, training-kit/kit/events_safety_sources.py "dfire_web"). Read from the copy at
                     huggingface.co/datasets/badsaarow/d-fire (the makers' OneDrive link cannot be read by a program).

Where the other finds went (training-kit/kit/events_safety_sources.py): Commons event and safety pictures under
CC BY-SA (share-alike); the PPE photo collections with research or unclear terms (Hard Hat Workers, the Safety
Helmet Wearing Dataset, CHV) and D-Fire's web pictures (research). Needing sign-up: SH17 (Kaggle, CC BY-NC-SA 4.0),
the FIRE dataset (Kaggle), Pictor-PPE (a Google Drive folder with no licence) and Roboflow Universe sets.

Looked at and not used here (checked at the source in November 2026), with the reason:
  Health and Safety Executive (UK)   Its text is under the Open Government Licence, but its photographs are
                                     licensed separately for a fee and its images and logos are excluded from the
                                     OGL (hse.gov.uk/help/copyright.htm; solutions.hse.gov.uk Crown copyright).
  OSHA and NIOSH websites            Public domain, but they have no picture list a program can read; OSHA's own
                                     photos are reached through Commons and NIOSH's through CDC PHIL (above).
  Wikimedia Commons Query Service    Would find "depicts" statements directly, but needs a Wikimedia login; the
                                     Commons search ("haswbstatement:P180=...") is used instead.
  NARA catalogue API v2              Needs a key; the catalogue's own public search (used above) does not.

    python packs/events_safety_packs.py commons_events --limit 8      (prints a few rows: a quick check)
"""

import io
import json
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, first_sentences, LONG_SIDE, COMMONS_FREE
from food_packs import commons_get, commons_members, commons_description, with_twins, count_pictures, sentence
from documentary_packs import tidy, usable, get_json, loc_picture, loc_free, loc_place, place_words, LOC
from archive_packs import (GRIM, not_shown, graphic_rows, sentence_case, lc_place, US_STATES, NARA, NARA_SEARCH,
                           nara_picture)
from expression_packs import CHILD
from world_packs import capped_words
from places import where, country_named, place_name, place_from_text

ASK_EVENT = "What event does this picture show?"
ASK_DESCRIBE = "Describe this picture."
ASK_WHERE_WHEN = "Where and when was this?"
ASK_MADE = "When was this picture made?"
ASK_SIGN = "What does this sign mean?"
ASK_ROAD_KIND = "What kind of road sign is this?"
ASK_WHAT = "What is this?"
ASK_HAZARD = "Is there a hazard here?"
ASK_POSTER = "What does this poster say?"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")


# ----------------------------------------------------------------- shared helpers

def safe_name(text, most=80):
    """A file name part made of letters, digits, dots and dashes."""
    return re.sub(r"[^\w.-]+", "_", str(text))[:most].strip("_") or "x"


def the(name):
    """An event's name as it is said after "This shows": "the" before names like "Battle of Hastings", "2012 Summer
    Olympics" or "March on Washington"; none before "Apollo 11" or "Hurricane Katrina"."""
    name = name.strip()
    if name.lower().startswith("the "):
        return "the " + name[4:]
    if re.search(r"\b(Front|War|Wars|Revolution|Games|Olympics|Campaign|Offensive|Crisis|Movement|Uprising|"
                 r"Parade|March|Festival|Carnival|Fair|Rally|Strike|Riot|Coronation|Funeral|Wedding|Earthquake|"
                 r"Expedition|Programme|Program|Rebellion|Blitz|Exposition|Exhibition|Conference|Congress)$", name):
        return "the " + name
    if re.match(r"^\d", name) or re.match(r"^[A-Z][\w'’-]*( [A-Z][\w'’-]*)? (of|on|to|at|for|in|against|between) ",
                                         name):
        return "the " + name
    return name


def marked(rows, *texts):
    """Rows marked "child" when the caption names a child and "content": "graphic" when any of texts (caption,
    file title, categories) names the dead, wounds or casualties; [] when not_shown refuses the picture."""
    joined = " ".join(t for t in texts if t)
    if not_shown(joined):
        return []
    if any(CHILD.search(r.get("answer", "")) for r in rows):
        rows = [dict(r, child=True) for r in rows]
    if GRIM.search(joined):
        rows = [dict(r, content="graphic") for r in rows]
    return graphic_rows(rows)


def finish(key, items, limit, workers=3, pause=0.3, flatten=False):
    """Shuffle (file name, address, rows) items, download the pictures (flattened onto white for drawings with
    transparent parts) and return the pack entries, at most limit pictures; says how many came and how many are
    marked child or graphic."""
    random.Random(len(key) * 7919).shuffle(items)
    fetched = fetch_pictures(items[:int(limit * 1.2) + 2], workers=workers, pause=pause, flatten=flatten)[:limit]
    say(f"{key}: {len(fetched)} pictures, {sum(1 for _, _, r in fetched if r[0].get('child'))} marked child, "
        f"{sum(1 for _, _, r in fetched if r[0].get('content') == 'graphic')} marked graphic")
    return with_twins(fetched)


def flat_jpeg(data):
    """JPEG bytes of a picture at most LONG_SIDE pixels on the long side, with any transparent parts made white (a
    sign drawn as an SVG and rendered by Commons as a PNG has a transparent background, which would turn black); None
    when it cannot be read or is tiny."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:  # noqa: BLE001 - left out
        return None
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        white = Image.new("RGBA", img.size, (255, 255, 255, 255))
        white.alpha_composite(img)
        img = white
    img = img.convert("RGB")
    if min(img.size) < 64:
        return None
    img.thumbnail((LONG_SIDE, LONG_SIDE))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=92)
    return out.getvalue()


def fetch_pictures(items, workers=3, pause=0.3, flatten=False):
    """Download pictures: items are (name, address, rows); returns [(name, JPEG bytes, rows)] for those that came.
    Waits and tries again when the server asks to slow down (429 or 503)."""
    import concurrent.futures
    from build_packs import smaller
    s = session()

    def one(item):
        """One picture, or None."""
        name, url, rows = item
        if pause:
            time.sleep(pause)
        for attempt in range(4):
            try:
                r = s.get(url, timeout=90)
                if r.status_code == 200:
                    data = flat_jpeg(r.content) if flatten else smaller(r.content)
                    return (name, data, rows) if data else None
                if r.status_code in (429, 503):
                    after = r.headers.get("Retry-After", "")
                    wait = min(int(after) if after.isdigit() else 10 * (attempt + 1), 120)
                    say(f"  The picture server asked to slow down: waiting {wait} seconds")
                    time.sleep(wait)
                    continue
                if r.status_code in (403, 404, 410):
                    return None
            except Exception:  # noqa: BLE001 - tried again, then left out
                time.sleep(3)
        return None

    out, done = [], 0
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        for result in pool.map(one, items):
            done += 1
            if result:
                out.append(result)
            if done % 500 == 0:
                say(f"  {done} of {len(items)} pictures fetched ({len(out)} usable)")
    return out


# ----------------------------------------------------------------- dates in words

def day_words(year, month=0, day=0):
    """A date without "in" or "on": "20 July 1969", "July 1969" or "1969"."""
    if month and day:
        return f"{day} {MONTHS[month - 1]} {year}"
    if month:
        return f"{MONTHS[month - 1]} {year}"
    return str(year)


def time_parts(value, precision):
    """(year, month, day) from a Wikidata time ("1969-07-20T00:00:00Z") and its precision (11 day, 10 month, 9
    year, 8 decade, 7 century); month and day are 0 when not known. None for dates before the year 1 (BC dates are
    left out rather than risk a wrong year). Before 1583 only the year is kept (Julian and Gregorian days differ)."""
    m = re.match(r"^\+?(-?)(\d{1,4})-(\d\d)-(\d\d)", str(value or ""))
    if not m or m.group(1) == "-":
        return None
    year, month, day = int(m.group(2)), int(m.group(3)), int(m.group(4))
    if year < 1:
        return None
    precision = int(precision or 9)
    if precision < 9:
        return (year, 0, 0, precision)
    if year < 1583 or precision == 9:
        return (year, 0, 0, 9)
    if precision == 10:
        return (year, month, 0, 10)
    return (year, month, day, 11)


def when_words(point=None, start=None, end=None):
    """When an event happened, in words: "on 20 July 1969", "in July 1969", "in 1969", "in the 1960s", "in the 15th
    century", "from 28 July 1914 to 11 November 1918", "from 3 to 5 May 1912". point, start and end are time_parts
    results (or None). "" when nothing is known."""
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
    if start and end and end[:3] != start[:3] and end[3] >= 9 and start[3] >= 9:
        (y1, m1, d1, _), (y2, m2, d2, _) = start, end
        if y1 == y2 and m1 and m2 and m1 == m2 and d1 and d2:
            return f"from {d1} to {d2} {MONTHS[m1 - 1]} {y1}"
        if y1 == y2 and m1 and m2:
            return f"from {day_words(y1, m1, d1).rsplit(' ', 1)[0]} to {day_words(y2, m2, d2)}"
        return f"from {day_words(y1, m1, d1)} to {day_words(y2, m2, d2)}"
    if start:
        return single(start)
    return ""


LOC_MONTHS = {m[:3].lower(): i + 1 for i, m in enumerate(MONTHS)}
LOC_MONTHS["sept"] = 9


def catalogue_when(text, fallback_year=""):
    """A catalogue date in words: "1918 Oct. 12" -> "on 12 October 1918", "[1918]" or "1914." -> "in 1918",
    "[192-]" -> "in the 1920s", "[between 1910 and 1915]" -> "between 1910 and 1915", "ca. 1915" -> "in about
    1915"; fallback_year ("1918-01-01") when the text gives none; "" when nothing is known."""
    text = clean(text).strip(" []")
    m = re.search(r"between (\d{4}) and (\d{4})", text)
    if m:
        return f"between {m.group(1)} and {m.group(2)}"
    m = re.search(r"\b(1[5-9]\d|20[0-2])-(?!\d)", text)
    if m:
        return f"in the {m.group(1)}0s"
    about = "about " if re.search(r"\b(ca\.|circa\b|approximately\b)", text, re.I) else ""
    m = re.search(r"\b(1[5-9]\d\d|20[0-2]\d)\b(?:\s+([A-Z][a-z]{2,4})\.?(?:\s+(\d{1,2})\b)?)?", text)
    if m:
        year = int(m.group(1))
        month = LOC_MONTHS.get((m.group(2) or "").lower()[:4]) or LOC_MONTHS.get((m.group(2) or "").lower()[:3]) or 0
        day = int(m.group(3)) if month and m.group(3) and 1 <= int(m.group(3)) <= 31 else 0
        return ("on " if day and not about else "in ") + about + day_words(year, month, day)
    m = re.match(r"^(\d{4})", str(fallback_year or ""))
    return f"in {m.group(1)}" if m else ""


def where_when_answer(place, when):
    """The answer to "Where and when was this?" ("This was in Paris, France, on 14 July 1919."), or "" when neither
    is known."""
    if place and when:
        return f"This was in {place_words(place)}, {when}."
    if place:
        return f"This was in {place_words(place)}; the record gives no date."
    if when:
        return f"This was {when}; the record does not say where."
    return ""


def event_answer(event, place, when, part=""):
    """The answer to "What event does this picture show?": "This shows <event>, in <place>, <when>." and, when the
    event was part of a larger one, "It was part of <that>."."""
    answer = f"This shows {event}" + (f", in {place_words(place)}" if place else "") + (f", {when}" if when else "")
    answer = answer + "."
    if part and part.lower() not in event.lower():
        answer += f" It was part of {the(part)}."
    return answer[0].upper() + answer[1:]


# ----------------------------------------------------------------- Wikimedia Commons file details

COMMONS_OPEN = "open"


def licence_open(licence):
    """True for a Commons licence the open packs may take: CC0, public domain or CC BY (never SA, NC or ND)."""
    return bool(COMMONS_FREE.match(licence)) and not re.search(r"\b(SA|NC|ND)\b", licence.upper().replace("-", " "))


def commons_files(s, titles, mimes=("image/jpeg", "image/png", "image/tiff"), width=LONG_SIDE, ok=licence_open):
    """[{title, url, credit, caption, categories, licence, pageid}] for files whose licence passes ok, 50 files a
    request. SVG drawings (mime "image/svg+xml") come as the PNG that Commons renders at width pixels. caption is
    the file's English caption (CC0) or else the start of its English description."""
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo|categories",
                               "cllimit": "max", "clshow": "!hidden", "iiprop": "url|extmetadata|mime",
                               "iiurlwidth": width, "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription",
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
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            if not ok(licence) or info.get("mime") not in mimes or not info.get("thumburl"):
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            artist = artist if len(artist) <= 80 else artist[:77].rsplit(" ", 1)[0] + "..."
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            caption = captions.get(f"M{p['pageid']}", "")
            description = clean((meta.get("ImageDescription") or {}).get("value"))
            out.append({"title": p["title"], "url": info["thumburl"], "licence": licence, "pageid": p["pageid"],
                        "credit": f"{p['title']} by {artist}, {licence}, {page}", "caption": clean(caption),
                        "description": description, "text": commons_description(caption, description),
                        "categories": [c["title"].split(":", 1)[-1] for c in p.get("categories") or []]})
        time.sleep(1)
    return out


def commons_depicting(s, qid, most=20):
    """The titles of Commons files whose structured data "depicts" (P180) the Wikidata item qid (Commons search)."""
    data = commons_get(s, {"action": "query", "list": "search", "srsearch": f"haswbstatement:P180={qid}",
                           "srnamespace": 6, "srlimit": most})
    return [h["title"] for h in (data.get("query") or {}).get("search") or []]


def category_files(s, category, most=200):
    """Up to most file titles of a Commons category (its first page of members only: no long listings)."""
    data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                           "cmtype": "file", "cmlimit": min(500, most)})
    return [m["title"] for m in (data.get("query") or {}).get("categorymembers") or []][:most]


# ----------------------------------------------------------------- historical events: Wikidata and Commons

# Wikidata classes of events (P31) and a short name for the log. Massacres, genocides and murders are left out on
# purpose (their pictures focus on the dead); battles and wars are kept, their graphic pictures marked.
EVENT_CLASSES = {
    "Q273120": "protest", "Q175331": "demonstration", "Q657449": "parade", "Q1413045": "military parade",
    "Q51404": "pride parade", "Q898830": "procession", "Q124757": "riot", "Q49776": "strike",
    "Q209715": "coronation", "Q1417098": "inauguration", "Q63442071": "royal wedding", "Q1052001": "state funeral",
    "Q201676": "funeral", "Q2324916": "state visit", "Q2627975": "ceremony",
    "Q40231": "election", "Q858439": "presidential election", "Q43109": "referendum",
    "Q135976384": "Summer Olympic Games", "Q16510064": "sporting event",
    "Q7944": "earthquake", "Q8068": "flood", "Q168983": "conflagration", "Q7692360": "volcanic eruption",
    "Q8092": "tropical cyclone", "Q3839081": "disaster", "Q8065": "natural disaster", "Q744913": "aviation accident",
    "Q1078765": "railway accident", "Q852190": "shipwreck", "Q179057": "explosion",
    "Q752783": "human spaceflight",
    "Q132241": "festival", "Q868557": "music festival", "Q172754": "world's fair", "Q1644573": "pilgrimage",
    "Q10931": "revolution", "Q45382": "coup", "Q178561": "battle", "Q188055": "siege", "Q198": "war",
}
# Event kinds never taken, even when an item is also an instance of a class above.
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


def sparql(s, query, tries=4):
    """The bindings of a Wikidata Query Service answer (CC0 data), trying again politely when it is busy; []."""
    for attempt in range(tries):
        try:
            r = s.get(WIKIDATA_SPARQL, params={"query": query, "format": "json"}, timeout=120)
            if r.status_code == 200:
                return r.json()["results"]["bindings"]
            after = r.headers.get("Retry-After", "")
            time.sleep(min(int(after) if after.isdigit() else 10 * (attempt + 1), 120))
        except Exception:  # noqa: BLE001 - a busy service or a timeout: wait and try again
            time.sleep(10 * (attempt + 1))
    return []


def label(binding, name):
    """An English label from a SPARQL row, or "" when Wikidata has none (the label service then gives the Q-id)."""
    text = clean((binding.get(name) or {}).get("value"))
    return "" if re.match(r"^Q\d+$", text) else text


def wikidata_events(s, qclass, most):
    """[{qid, name, category, when, place, part}] for event items of one class with a date and a Commons category,
    one entry an item (the first value of each statement)."""
    events = {}
    for b in sparql(s, EVENT_QUERY % (qclass, most * 4)):
        qid = b["e"]["value"].rsplit("/", 1)[-1]
        if qid in events:
            continue
        name = label(b, "eLabel")
        if not name or EVENT_NEVER.search(name):
            continue
        point = time_parts((b.get("t") or {}).get("value"), (b.get("tp") or {}).get("value"))
        launch = time_parts((b.get("l") or {}).get("value"), (b.get("lp") or {}).get("value"))     # P619
        start = time_parts((b.get("s") or {}).get("value"), (b.get("sp") or {}).get("value"))
        end = time_parts((b.get("f") or {}).get("value"), (b.get("fp") or {}).get("value"))
        when = when_words(point, start, end) or ("launched " + when_words(launch) if launch else "")
        country_label = label(b, "countryLabel")
        country = country_named(country_label) or country_label
        location = label(b, "locLabel")
        place = place_name(location, country) if location and country_named(location) != country else country
        events[qid] = {"qid": qid, "name": name, "category": clean(b["cat"]["value"]), "when": when,
                       "place": place, "part": label(b, "partLabel")}
    return list(events.values())


def event_name(name):
    """An event's Wikidata name without a year or place added after a comma ("Gay Easter Parade, New Orleans, 2017"
    -> "Gay Easter Parade") and whether something was cut (then the answer does not repeat it)."""
    short = re.sub(r"(,\s*[^,]+)*,\s*(1[0-9]|20)\d\d$", "", name).strip()
    return (short, True) if short and short != name else (name, False)


def year_clash(event, f):
    """True when the file's title names a year (1800-2029) that is not the event's year or period, a sign that the
    file is filed under the wrong year's event."""
    years = {int(y) for y in re.findall(r"\b(1[89]\d\d|20[0-2]\d)\b", f["title"])}
    known = [int(y) for y in re.findall(r"\b(\d{4})\b", event["when"])]
    if not years or not known:
        return False
    return not any(min(known) <= y <= max(known) for y in years)


def event_rows(event, f):
    """The rows of one Commons file showing an event: what event (from Wikidata), where and when, and the file's own
    caption when it is a description of 6 words or more; [] when the file is refused (not_shown) or its title names
    another year than the event's."""
    if year_clash(event, f):
        return []
    credit = f"{f['credit']}; event facts from Wikidata ({event['qid']}, CC0)"
    place_fields = where(event["place"], "depicted")
    caption = tidy(capped_words(f["text"], 70)) if f["text"] else ""
    rows = [{"question": ASK_DESCRIBE, "answer": caption, "credit": credit, **place_fields}] if usable(caption) else []
    name, cut = event_name(event["name"])
    rows.append({"question": ASK_EVENT, "answer": event_answer(the(name), event["place"] if not cut or event["place"]
                                                               not in event["name"] else "", event["when"],
                                                               event["part"]), "credit": credit, **place_fields})
    where_when = where_when_answer(event["place"], event["when"])
    if where_when:
        rows.append({"question": ASK_WHERE_WHEN, "answer": where_when, "credit": credit, **place_fields})
    return marked(rows, caption, f["title"], " ".join(f["categories"]))


def event_items(s, ok=licence_open, limit=100, per_event=3, prefix="event", seed=503):
    """[(file name, picture address, rows)] for Commons files showing Wikidata events: the classes taken in turn (in
    a shuffled order), a few files from each event (its "depicts" files first, then its category's files)."""
    rng = random.Random(seed)
    queues = []
    for qclass, kind in EVENT_CLASSES.items():
        events = wikidata_events(s, qclass, max(20, limit // len(EVENT_CLASSES) * 2))
        rng.shuffle(events)
        queues.append((kind, events))
        say(f"  Wikidata: {len(events)} {kind} events with a date and a Commons category")
        time.sleep(1)
    items, seen = [], set()
    want = int(limit * 1.3) + 4
    while len(items) < want and any(q[1] for q in queues):
        for kind, events in queues:
            if not events or len(items) >= want:
                continue
            event = events.pop()
            titles = commons_depicting(s, event["qid"]) + category_files(s, event["category"], 60)
            titles = [t for t in dict.fromkeys(titles) if t not in seen]
            rng.shuffle(titles)
            got = 0
            for f in commons_files(s, titles[:per_event * 4], ok=ok):
                if got >= per_event:
                    break
                rows = event_rows(event, f)
                if rows:
                    seen.add(f["title"])
                    items.append((f"{prefix}-{f['pageid']}.jpg", f["url"], rows))
                    got += 1
    say(f"  Commons: {len(items)} event pictures from {len(seen)} files")
    return items


def build_commons_events(limit):
    """The Commons events pack (see the module docstring)."""
    return finish("commons_events", event_items(session(), limit=limit), limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- historical events: Library of Congress

LOC_EVENT_SETS = [("collections/bain/", "George Grantham Bain Collection"),
                  ("collections/harris-ewing/", "Harris & Ewing Collection")]
LOC_EVENT_TERMS = ("parade", "suffrage", "inauguration", "funeral", "coronation", "celebration", "ceremony",
                   "demonstration", "strike", "fire", "flood", "earthquake", "Olympic", "convention", "election",
                   "procession", "wedding", "memorial", "launching", "dedication", "rally", "march", "carnival",
                   "armistice", "disaster", "wreck")
# The kind of event from the record's own words (title, subjects, summary): (pattern, the words used).
EVENT_KINDS = [
    (r"\bsuffrag", "a women's suffrage event"), (r"\binaugura", "an inauguration"),
    (r"\bcoronation", "a coronation"), (r"\bfuneral", "a funeral"), (r"\bwedding", "a wedding"),
    (r"\bolympi", "the Olympic Games"), (r"\bmay day", "a May Day parade"), (r"\bparades?\b|\bprocession",
                                                                             "a parade"),
    (r"\bdemonstration|\bprotest", "a demonstration"), (r"\bmarch(es|ers|ing)?\b(?! \d)", "a march"),
    (r"\brall(y|ies)\b", "a rally"), (r"\bstrik(e|es|ers)\b", "a strike"), (r"\briot", "a riot"),
    (r"\bconvention\b", "a political convention"), (r"\belection", "an election"),
    (r"\berupt", "a volcanic eruption"), (r"\bearthquake", "an earthquake"), (r"\bflood", "a flood"),
    (r"\b(fire|fires|blaze)\b", "a fire"),
    (r"\bexplosion", "an explosion"), (r"\b(wreck|shipwreck|disaster)", "a disaster"),
    (r"\barmistice", "the Armistice celebrations"), (r"\blaunch(ing)?\b", "a ship launching"),
    (r"\bdedicat", "a dedication ceremony"), (r"\bmemorial (day|service)", "a memorial ceremony"),
    (r"\bcarnival|\bmardi gras", "a carnival"), (r"\bcelebrat", "a celebration"), (r"\bceremon", "a ceremony"),
]
LOC_TITLE_HEAD = re.compile(r"^[A-Z][\w &,'-]*?\s*-{1,2}\s*\d{4}\.?\s*[-.,:]?\s*")      # "Parades--1918. "


# Words that show a record is about something else than an event shown (records about an election, a page of a
# book about a carnival, a military operation's code name): no event row then.
EVENT_NOT = re.compile(r"\b(records?|documents?|exhibits?|exhibition of|posters?|maps?|page \d+|scan \d+|songs?|opera|"
                       r"book|reminiscences|astronomy|apocalyp\w*|allegor\w*|operation [A-Z]{3,}|hearings?|"
                       r"conference|discuss\w*|meeting about)\b")


def event_kind(*texts):
    """The kind of event a record's own words name ("a parade", "an inauguration"), or "" (also when the words show
    the record is about something else, EVENT_NOT)."""
    joined = " ".join(t for t in texts if t)
    if EVENT_NOT.search(joined) or re.search(r"\b(records?|documents?|posters?|book|page)\b", joined, re.I):
        return ""
    for pattern, words in EVENT_KINDS:
        if re.search(pattern, joined, re.I):
            return words
    return ""


def tidy_place(place):
    """A Library of Congress place in everyday words: "Washington (D.C.), District of Columbia, USA" ->
    "Washington, D.C., USA"."""
    place = re.sub(r"(Washington(?: \(D\.C\.\))?, )?District of Columbia|Washington \(D\.C\.\)", "Washington, D.C.",
                   place)
    parts = [p.strip() for p in re.sub(r"Washington, D\.C\.", "Washington|D.C.", place).split(",")]
    return ", ".join(dict.fromkeys(p for p in parts if p)).replace("Washington|D.C.", "Washington, D.C.")


def loc_event_place(record):
    """documentary_packs.loc_place, or else a US place heading the Bain records use ("New York (State)--New York"
    -> "New York, New York, USA"); ""."""
    place = loc_place(record)
    if place:
        return tidy_place(place)
    item = record.get("item") or {}
    heading = clean(((item.get("place") or [{}])[0] or {}).get("title"))
    parts = [re.sub(r"\s*\((state|D\.C\.)\)", "", p).strip(" .") for p in heading.split("--") if p.strip()]
    if parts and parts[0] in US_STATES:
        return place_name(*list(reversed(parts[1:]))[:1], parts[0], "USA")
    return lc_place(parts[0]) if parts else ""


def loc_event_record(record, name):
    """(file name, picture address, rows) for one Library of Congress event photo, or None."""
    item = record.get("item") or {}
    title = clean(record.get("title"))
    picture = loc_picture(record)
    if not loc_free(record) or not picture or not title:
        return None
    place = loc_event_place(record)
    words = sentence_case(LOC_TITLE_HEAD.sub("", title), place.split(", "))
    summary = clean(item.get("summary"))
    summary = re.sub(r"\s*\(Source:[^)]*\)", "", summary)
    text = words if not summary or summary.lower() in words.lower() else f"{words.rstrip('.')}. {summary}"
    answer = tidy(capped_words(text, 70))
    subjects = " ".join(clean(x) for x in (item.get("subjects") or []))
    kind = event_kind(re.split(r"(?<=[a-z]{2})\.\s", LOC_TITLE_HEAD.sub("", title))[0], subjects)
    when = catalogue_when(item.get("date") or item.get("created_published"), record.get("date"))
    if not kind and not usable(answer):
        return None
    link = re.sub(r"^(https?:)?//", "https://", item.get("link") or record.get("id") or "")
    credit = f"{title[:150]}, {name}, Library of Congress, Prints and Photographs Division, no known restrictions " \
             f"on publication, {link}"
    rows = []
    if usable(answer):
        rows.append({"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **where(place)})
    if kind:
        rows.append({"question": ASK_EVENT, "answer": event_answer(kind, place, when), "credit": credit,
                     **where(place)})
    where_when = where_when_answer(place, when)
    if where_when:
        rows.append({"question": ASK_WHERE_WHEN, "answer": where_when, "credit": credit, **where(place)})
    rows = marked(rows, answer, title, subjects)
    control = re.sub(r"\W", "", str(item.get("control_number") or record.get("id") or title))[-40:]
    return (f"loc-event-{control}.jpg", picture, rows) if rows else None


def build_loc_events(limit):
    """The Library of Congress events pack: each event word searched in each collection (a random result page or
    two), a few records from each page, each caption once."""
    s, rng, items, answers = session(), random.Random(509), [], set()
    searches = [(path, name, term) for path, name in LOC_EVENT_SETS for term in LOC_EVENT_TERMS]
    rng.shuffle(searches)
    per_search = max(2, int(limit * 1.3) // len(searches) + 1)
    for path, name, term in searches:
        time.sleep(2)                     # the Library asks programs to keep to about one request a second
        first = get_json(s, LOC + path, {"fo": "json", "c": 100, "q": term, "at": "pagination"}, pause=15) or {}
        pages = max(1, min(20, int(((first.get("pagination") or {}).get("total")) or 1)))
        data = get_json(s, LOC + path, {"fo": "json", "c": 100, "q": term, "sp": rng.randint(1, pages),
                                        "at": "results"}, pause=15) or {}
        taken = 0
        results = data.get("results") or []
        rng.shuffle(results)
        for record in results:
            item = loc_event_record(record, name)
            if not item or taken >= per_search or item[2][0]["answer"] in answers:
                continue
            answers.add(item[2][0]["answer"])
            items.append(item)
            taken += 1
        if len(items) >= limit * 1.3:
            break
    say(f"  Library of Congress: {len(items)} event photos")
    return finish("loc_events", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- historical events: US National Archives

NARA_EVENT_TERMS = ("parade", "inauguration", "ceremony", "demonstration", "protest", "march", "funeral",
                    "celebration", "flood", "hurricane", "earthquake", "fire", "Olympic", "coronation", "election",
                    "rally", "state visit", "launch", "moon landing", "dedication", "liberation", "surrender",
                    "independence")
NARA_NOT_HERE = {"542493", "536000", "519830"}       # the series in archive_packs.py's nara pack
NARA_PHOTOS = "Photographs and other Graphic Materials"


def nara_event_when(record):
    """The record's production date in words ("on 20 January 1945"), or ""."""
    for d in record.get("productionDates") or []:
        if d.get("year"):
            month = int(d.get("month") or 0)
            day = int(d.get("day") or 0) if month else 0
            return ("on " if day else "in ") + day_words(int(d["year"]), month, day)
    return ""


def nara_event_record(record):
    """(file name, picture address, rows) for one NARA event photo, or None."""
    ancestors = {str(a.get("naId")) for a in record.get("ancestors") or []}
    if (record.get("useRestriction") or {}).get("status") != "Unrestricted" or ancestors & NARA_NOT_HERE:
        return None
    picture = nara_picture(record)
    if not picture:
        return None
    title = clean(record.get("title"))
    note = re.sub(r"^\s*Original caption:\s*", "", clean(record.get("scopeAndContentNote")), flags=re.I)
    places = [clean(x.get("heading")) for x in record.get("subjects") or []
              if x.get("authorityType") == "geographicPlaceName"]
    place = next((p for p in map(lc_place, places) if p), "")
    text = note if len(note.split()) > len(title.split()) else title
    answer = tidy(capped_words(sentence_case(text, places), 80))
    kind = event_kind(re.split(r"(?<=[a-z]{2})\.\s", title)[0])
    when = nara_event_when(record)
    if not kind:
        return None
    credit = f"{title[:150]}, U.S. National Archives and Records Administration, public domain (US government " \
             f"work), {NARA}id/{record.get('naId')}"
    rows = []
    if usable(answer):
        rows.append({"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **where(place)})
    rows.append({"question": ASK_EVENT, "answer": event_answer(kind, place, when), "credit": credit, **where(place)})
    where_when = where_when_answer(place, when)
    if where_when:
        rows.append({"question": ASK_WHERE_WHEN, "answer": where_when, "credit": credit, **where(place)})
    rows = marked(rows, answer, title)
    return (f"nara-event-{record.get('naId')}.jpg", picture, rows) if rows else None


def build_nara_events(limit):
    """The NARA events pack: each event word searched among online photographs (a random result page of the first
    50), a few records from each page, each caption once. (The search answers with an error page for some page
    sizes, so 100 records a page are asked for, as archive_packs.py does.)"""
    s, rng, items, answers = session(), random.Random(521), [], set()
    terms = list(NARA_EVENT_TERMS)
    rng.shuffle(terms)
    per_term = max(2, int(limit * 1.3) // len(terms) + 1)
    for term in terms:
        time.sleep(2)
        params = {"q": term, "typeOfMaterials": NARA_PHOTOS, "availableOnline": "true", "limit": 100}
        first = get_json(s, NARA_SEARCH, dict(params, page=1), pause=10) or {}
        total = ((((first.get("body") or {}).get("hits") or {}).get("total")) or {}).get("value") or 0
        page = rng.randint(1, max(1, min(50, total // 100)))
        data = first if page == 1 else get_json(s, NARA_SEARCH, dict(params, page=page), pause=10) or {}
        hits = (((data.get("body") or {}).get("hits") or {}).get("hits")) or []
        rng.shuffle(hits)
        taken = 0
        for hit in hits:
            item = nara_event_record((hit.get("_source") or {}).get("record") or {})
            if not item or taken >= per_term or item[2][0]["answer"] in answers:
                continue
            answers.add(item[2][0]["answer"])
            items.append(item)
            taken += 1
        if len(items) >= limit * 1.3:
            break
    say(f"  NARA: {len(items)} event photos")
    return finish("nara_events", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- historical events: Europeana

EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EUROPEANA_KEY = "api2demo"         # Europeana's public test key; a full build may set EUROPEANA_KEY to its own
EUROPEANA_FREE = re.compile(r"creativecommons\.org/(publicdomain/(zero|mark)/|licenses/by/\d)", re.I)
EUROPEANA_TERMS = ("coronation", "parade", "procession", "funeral", "demonstration", "protest", "festival",
                   "carnival", "celebration", "ceremony", "inauguration", "election", "Olympic Games", "fire",
                   "flood", "earthquake", "battle", "siege", "revolution", "royal wedding", "exhibition opening",
                   "strike", "riot", "eruption", "shipwreck")
# Not an event: plant varieties ("Rosa 'Coronation Street'"), scientific names, sheet music and book pages.
EUROPEANA_NOT_EVENT = re.compile(r"'[^']+'|“[^”]+”|\b[A-Z][a-z]+ [a-z]+ L\.|\b(sheet music|score|specimen|herbarium|"
                                 r"book ?plate|title page|frontispiece)\b", re.I)


def europeana_items(limit):
    """[(file name, picture address, rows)] from Europeana: English records whose title names an event and whose own
    rights statement is CC0, the Public Domain Mark or CC BY (never BY-SA, NC or ND)."""
    import os
    from medical_packs import tidy_record_text
    s, rng, items, seen = session(), random.Random(523), [], set()
    key = os.environ.get("EUROPEANA_KEY", EUROPEANA_KEY)
    terms = list(EUROPEANA_TERMS)
    rng.shuffle(terms)
    per_term = max(2, int(limit * 1.3) // len(terms) + 1)
    for term in terms:
        data = get_json(s, EUROPEANA, {"wskey": key, "query": f"title:({term})", "qf": ["TYPE:IMAGE", "LANGUAGE:en"],
                                       "reusability": "open", "rows": 100, "profile": "rich",
                                       "start": rng.choice((1, 1, 101, 201))}) or {}
        taken = 0
        for record in data.get("items") or []:
            rights = " ".join(record.get("rights") or [])
            picture = (record.get("edmIsShownBy") or [""])[0]
            title = clean((record.get("title") or [""])[0])
            if record.get("id") in seen or not EUROPEANA_FREE.search(rights) or re.search(r"by-(sa|nc|nd)", rights) \
                    or (record.get("language") or []) != ["en"] or not picture or EUROPEANA_NOT_EVENT.search(title) \
                    or taken >= per_term:
                continue
            kind = event_kind(title)
            description = (record.get("dcDescription") or [""])[0]
            description = re.split(r"This image (has been taken from|is from a selection)", description)[0]
            description = tidy_record_text(first_sentences(description, 50))
            text = title if not description or description.lower() in title.lower() else \
                f"{title.rstrip('.')}. {description}"
            answer = tidy(capped_words(text, 70))
            if not kind or not usable(answer):
                continue
            seen.add(record["id"])
            taken += 1
            provider = clean((record.get("dataProvider") or ["Europeana"])[0])
            credit = f"{provider} via Europeana, \"{title[:150]}\", {rights}, https://www.europeana.eu/item{record['id']}"
            labels = record.get("edmPlaceLabelLangAware") or {}
            place = next((p for p in map(place_from_text, (labels.get("en") or [])) if p), "")
            rows = [{"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **where(place, "depicted")},
                    {"question": ASK_EVENT, "answer": f"It shows {kind}" +
                     (f", in {place_words(place)}" if place else "") + ".", "credit": credit,
                     **where(place, "depicted")}]
            year = next((y for y in record.get("year") or [] if re.match(r"^\d{4}$", str(y))), "")
            if year:
                rows.append({"question": ASK_MADE, "answer": f"The record dates the picture to {year}.",
                             "credit": credit})
            rows = marked(rows, answer, title)
            if rows:
                items.append((f"europeana-{safe_name(record['id'])}.jpg", picture, rows))
        time.sleep(0.5)
    say(f"  Europeana: {len(items)} event pictures")
    return items


def build_europeana_events(limit):
    """The Europeana events pack (see the module docstring)."""
    return finish("europeana_events", europeana_items(limit), limit, workers=4, pause=0.2)


# ----------------------------------------------------------------- safety signs

ISO_CATEGORY = "ISO 7010 safety signs (vector drawings)"
ISO_KINDS = {"E": "safe condition", "F": "fire equipment", "M": "mandatory action", "P": "prohibition",
             "W": "warning"}
ISO_CODE = re.compile(r"\bISO[ _]7010[ _]([EFMPW])(\d{3})\b", re.I)
# The nine official GHS pictograms: the Commons file name part, the code and what it warns of.
GHS = {"explos": ("GHS01", "explosive"), "flamme": ("GHS02", "flammable"), "rondflam": ("GHS03", "oxidising"),
       "bottle": ("GHS04", "gas under pressure"), "acid": ("GHS05", "corrosive"),
       "skull": ("GHS06", "acute toxicity: toxic or deadly"), "exclam": ("GHS07", "harmful or irritant"),
       "silhouette": ("GHS08", "serious health hazard"), "pollu": ("GHS09", "hazardous to the environment")}
GHS_CATEGORY = "GHS pictograms (Vector drawings)"
# Road sign kinds: the Commons category word and how a row says it.
ROAD_KINDS = {"warning": "a warning road sign", "prohibitory": "a prohibitory road sign (it forbids something)",
              "mandatory": "a mandatory road sign (it says what you must do)",
              "priority": "a priority road sign (it says who goes first)",
              "information": "an information road sign", "speed limit": "a speed limit road sign"}
ROAD_STRIP = re.compile(r"\b(road|traffic|street|highway|warning|regulatory|prohibitory|prohibition|mandatory|"
                        r"priority|information|informative|danger|caution)\s+signs?\b|\bsigns?\b|\bSVG\b|"
                        r"\bdiagram\b|\bfig\.?|\b[A-Z]{1,3}[- ]?\d+(\.\d+)*[a-z]?\b|\b\d+-\d+[a-z]?\b|"
                        r"\b\d{3,}[a-z]?\b(?!\s*(km|mph|t\b|m\b))|\bno\.\s*", re.I)
# A road sign meaning must use at least one of these English words (captions in other languages are left out).
ROAD_ENGLISH = re.compile(r"\b(no|not|end|entry|parking|stop|give|way|yield|speed|limit|turn|left|right|ahead|only|"
                          r"road|roads|crossing|pedestrians?|children|school|bicycles?|cycl\w*|lane|lanes|priority|"
                          r"overtaking|vehicles?|lorr(y|ies)|trucks?|goods|keep|roundabout|slippery|bend|bends|curve|"
                          r"junction|works|animals?|deer|cattle|falling|rocks|traffic|lights|signals?|tunnel|bridge|"
                          r"narrows|hill|steep|descent|ascent|danger\w*|minimum|maximum|height|width|weight|length|"
                          r"horn|u-turn|straight|motorway|expressway|bus|tram|railway|level|wind|two-way|one-way|"
                          r"dead|hospital|airport|horses?|riders?|uneven|bumps?|ice|snow|fog|queues?|motorcycles?|"
                          r"cars?|tractors?|camels?|kangaroos?|ducks?|frogs?|low|flying|aircraft|ford|quay|river|bank|"
                          r"gravel|loose|chippings|merging|ends|zone|toll|customs|police|direction|detour|closed|"
                          r"prohibited|compulsory|must|permitted|allowed|waiting|loading|uturn|reverse|crossroads|"
                          r"intersection|cats?|dogs?|jumping|crossing|pass|side|centre|center)\b",
                          re.I)


def iso_meaning(f, code):
    """The meaning of an ISO 7010 sign from its file: the words after the code in its title, caption or
    description ("ISO 7010 W012 Warning; Electricity" -> "electricity"), without the kind word; ""."""
    for text in (f["title"].split(":", 1)[-1].rsplit(".", 1)[0], f["caption"], f["description"]):
        m = re.search(re.escape(code) + r"[\s;:,–-]*(.+)$", text or "", re.I)
        if not m:
            continue
        words = m.group(1).split(";")
        words = [w.strip(" .–-") for w in words if w.strip(" .–-")]
        words = [w for w in words if w.lower() not in ("warning", "prohibition", "mandatory", "safe condition",
                                                       "fire equipment", "new", "general warning sign")
                 and not w.lower().startswith("to ")]
        meaning = clean(words[0]) if words else ""
        if meaning and not re.search(r"similar to|recommendation|arrow|\+", meaning, re.I) \
                and len(meaning.split()) <= 12:
            return meaning[0].lower() + meaning[1:] if not meaning[:2].isupper() else meaning
    return ""


def iso_purpose(f):
    """The "To indicate the location of a lifeboat" part of an ISO 7010 file's description, as a sentence ("It
    indicates the location of a lifeboat."); ""."""
    m = re.search(r";\s*To (\w+)\b([^;.]*)", f["description"] or "")
    if not m:
        return ""
    verb = m.group(1).lower()
    verb = verb + ("es" if verb.endswith(("sh", "ch", "s", "x")) else "s")
    return sentence(f"It {verb}{m.group(2)}")


def iso_items(s):
    """[(file name, address, rows)] for the ISO 7010 signs whose file names a code and a meaning."""
    items, codes = [], set()
    for f in commons_files(s, commons_members(s, ISO_CATEGORY, "file"), mimes=("image/svg+xml", "image/png"),
                           width=800):
        m = ISO_CODE.search(f["title"])
        if not m:
            continue
        code = m.group(1).upper() + m.group(2)
        meaning = iso_meaning(f, code)
        if not meaning or code in codes:
            continue
        codes.add(code)
        answer = f"This is the ISO 7010 sign {code}: {ISO_KINDS[code[0]]}, {meaning}."
        purpose = iso_purpose(f)
        rows = [{"question": ASK_SIGN, "answer": f"{answer} {purpose}".strip(), "credit": f["credit"]}]
        items.append((f"iso7010-{code}.jpg", f["url"], rows))
    say(f"  ISO 7010: {len(items)} signs with a code and a meaning")
    return items


def ghs_items(s):
    """[(file name, address, rows)] for the nine GHS hazard pictograms."""
    items = []
    for f in commons_files(s, commons_members(s, GHS_CATEGORY, "file"), mimes=("image/svg+xml",), width=800):
        m = re.match(r"^File:GHS-pictogram-([a-z]+)\.svg$", f["title"])
        if not m or m.group(1) not in GHS:
            continue
        code, meaning = GHS[m.group(1)]
        answer = f"This is the GHS hazard pictogram {code}: {meaning}. GHS pictograms are used on chemical labels."
        items.append((f"ghs-{code}.jpg", f["url"], [{"question": ASK_SIGN, "answer": answer, "credit": f["credit"]}]))
    say(f"  GHS: {len(items)} pictograms")
    return items


def road_meaning(text, country):
    """A road sign's meaning from its English caption, without the country, the words "road sign" and sign codes
    ("Japan road sign 201-A (crossroads)" -> "crossroads"); "" when nothing plain is left."""
    text = clean(text).strip(" .")
    m = re.search(r"\(([A-Za-z][^()]{2,60})\)$", text)
    if m and not re.search(r"\d{3}|\bsign\b", m.group(1), re.I):
        text = m.group(1)
    for name in {country, country.replace("USA", "United States"), country.replace("UK", "United Kingdom")}:
        text = re.sub(rf"\b(in|of|from|for)\s+(the\s+)?{re.escape(name)}\b|\b{re.escape(name)}\b", " ", text,
                      flags=re.I)
    text = ROAD_STRIP.sub(" ", text)
    text = re.sub(r"\s*[-–:;,]+\s*$|^\s*[-–:;,]+\s*", "", " ".join(text.split())).strip(" .:-–")
    words = text.split()
    if not 1 <= len(words) <= 8 or not re.match(r"^[A-Za-z0-9][A-Za-z0-9 ,'()/.-]*$", text) \
            or not ROAD_ENGLISH.search(text) \
            or re.search(r"\b(of|in|for|and|the|a)$", text, re.I) or len(text) < 3:
        return ""
    return " ".join(w if w.isupper() and len(w) > 1 else w.lower() for w in text.split())


def road_items(s, want, rng):
    """[(file name, address, rows)] for road sign drawings of many countries: for each kind, the "Diagrams of <kind>
    road signs of <country>" categories, the countries taken in turn, a few signs from each."""
    queues = []
    for kind, words in ROAD_KINDS.items():
        for sub in commons_members(s, f"Diagrams of {kind} road signs by country", "subcat"):
            m = re.match(rf"^Category:Diagrams of {kind} road signs of (?:the )?(.+)$", sub)
            country = country_named(m.group(1)) if m else ""
            if country:
                queues.append((sub.split(":", 1)[1], words, country))
    rng.shuffle(queues)
    say(f"  Road signs: {len(queues)} country categories")
    items, per = [], max(2, want // max(1, len(queues)) + 1)
    for visited, (category, words, country) in enumerate(queues[:want * 3 + 10]):
        if len(items) >= want:
            break
        if visited and visited % 25 == 0:
            say(f"  Road signs: {visited} categories read, {len(items)} signs")
        titles = category_files(s, category, 120)
        if len(titles) < per * 2:          # many countries file their signs one level down, by type
            subs = commons_members(s, category, "subcat")
            rng.shuffle(subs)
            for sub in subs[:2]:
                titles += category_files(s, sub.split(":", 1)[1], 120)
        rng.shuffle(titles)
        got = 0
        for f in commons_files(s, titles[:per * 4], mimes=("image/svg+xml", "image/png"), width=800):
            if got >= per:
                break
            meaning = road_meaning(f["caption"] or f["description"], country)
            if meaning:
                rows = [{"question": ASK_SIGN, "answer": f"It is {words} used in {place_words(country)}: {meaning}.",
                         "credit": f["credit"], "place": country}]
            else:
                rows = [{"question": ASK_ROAD_KIND, "answer": f"It is {words} used in {place_words(country)}.",
                         "credit": f["credit"], "place": country}]
            items.append((f"road-{f['pageid']}.jpg", f["url"], rows))
            got += 1
    return items


def build_safety_signs(limit):
    """The safety signs pack: every ISO 7010 sign with a meaning and the nine GHS pictograms (a few hundred in all),
    then road signs of many countries to fill the limit."""
    s, rng = session(), random.Random(541)
    items = iso_items(s) + ghs_items(s)
    rng.shuffle(items)
    items = items[:max(limit // 2, limit - limit // 2)] if len(items) > limit // 2 else items
    items += road_items(s, int((limit - len(items)) * 1.2) + 2, rng)
    return finish("safety_signs", items, limit, workers=2, pause=0.5, flatten=True)


# ----------------------------------------------------------------- safety equipment and hazards (Commons photos)

# Commons category: (question, answer, words a file must have to count, how deep into subcategories).
SAFETY_PHOTOS = {
    "Fire extinguishers": (ASK_WHAT, "It shows a fire extinguisher.", None, 1),
    "Automated external defibrillators": (ASK_WHAT, "It shows an automated external defibrillator (AED), a device "
                                                    "used to restart the heart in a cardiac arrest.", None, 1),
    "AED signs": (ASK_SIGN, "It is a sign showing where an automated external defibrillator (AED) is.", None, 1),
    "Defibrillator signs": (ASK_SIGN, "It is a sign showing where a defibrillator (AED) is.", None, 0),
    "First aid kits": (ASK_WHAT, "It shows a first aid kit.", None, 1),
    "Safety showers": (ASK_WHAT, "It shows an emergency safety shower, used to wash chemicals off the body; many "
                                 "have an eyewash station.", None, 1),
    "Emergency exit signs": (ASK_SIGN, "It is an emergency exit sign: it shows the way out.", None, 1),
    "Exit signs": (ASK_SIGN, "It is an exit sign: it shows the way out.", None, 0),
    "Manual call points": (ASK_WHAT, "It shows a fire alarm call point: pressing it sounds the fire alarm.", None, 0),
    "Fire alarms": (ASK_WHAT, "It shows part of a fire alarm system.", None, 0),
    "Smoke detectors": (ASK_WHAT, "It shows a smoke alarm (smoke detector).", None, 0),
    "Carbon monoxide detectors": (ASK_WHAT, "It shows a carbon monoxide alarm.", None, 0),
    "Fire blankets": (ASK_WHAT, "It shows a fire blanket.", None, 0),
    "Fire hose reels": (ASK_WHAT, "It shows a fire hose reel.", None, 0),
    "Fire extinguisher signs": (ASK_SIGN, "It is a sign showing where a fire extinguisher is.", None, 0),
    "Lifebuoys": (ASK_WHAT, "It shows a lifebuoy, a ring to throw to someone in the water.", None, 1),
    "Fire hydrants": (ASK_WHAT, "It shows a fire hydrant.", None, 0),
    "Wet floor signs": (ASK_HAZARD, "Yes: a sign warns that the floor is wet and may be slippery.", None, 1),
    "Broken glass": (ASK_HAZARD, "Yes: there is broken glass, which can cut.", None, 1),
    "Manholes": (ASK_HAZARD, "Yes: there is an open manhole, a hole someone could fall into.", r"\bopen(ed)?\b", 1),
    "Construction sites": (ASK_HAZARD, "Yes: this is a construction site, with hazards such as machines, holes and "
                                       "falling objects.", None, 0),
    "Smoke": (ASK_HAZARD, "Yes: there is smoke, which may come from a fire.", r"\b(fire|burning|smoke from)\b", 0),
    "Building fires": (ASK_HAZARD, "Yes: a building is on fire.", None, 1),
    "Burning buildings": (ASK_HAZARD, "Yes: a building is on fire.", None, 1),
    "House fires": (ASK_HAZARD, "Yes: a house is on fire.", None, 0),
    "Wildfires": (ASK_HAZARD, "Yes: there is a wildfire, a fire burning through open land.", None, 1),
    "Oil spills": (ASK_HAZARD, "Yes: oil has been spilled.", None, 0),
    "Flooded roads": (ASK_HAZARD, "Yes: the road is flooded; the water may be deeper or faster than it looks.",
                      None, 1),
    "Icy roads": (ASK_HAZARD, "Yes: the road is icy and slippery.", None, 1),
    "Potholes": (ASK_HAZARD, "Yes: there is a pothole in the road.", None, 1),
    "Downed power lines": (ASK_HAZARD, "Yes: power lines have fallen down; they may still carry electricity.",
                           r"\b(power|electric\w*) ?lines?\b|\bwires?\b", 0),
    "Fallen trees": (ASK_HAZARD, "Yes: a tree has fallen.", None, 0),
    "Sinkholes": (ASK_HAZARD, "Yes: there is a sinkhole, where the ground has fallen in.", None, 0),
    "Traffic cones": (ASK_WHAT, "It shows traffic cones, which mark a hazard or roadworks.", None, 0),
}
# Subcategories that are not photos of the thing (art, drawings, diagrams, logos, people's portraits ...).
NOT_A_PHOTO_CAT = re.compile(r"\b(art|drawings?|diagrams?|illustrations?|icons?|logos?|maps?|videos?|in fiction|"
                             r"paintings?|stamps?|toys?|models?|sculptures?|SVG|charts?|animations?)\b", re.I)


def safety_items(s, want, rng, ok=licence_open):
    """[(file id, address, rows)] from SAFETY_PHOTOS: each category (and, where asked, a few of its
    subcategories) taken in turn, a few files at a time whose licence passes ok; the category's answer and the
    file's English caption as a second row."""
    def titles_of(category, depth):
        """The file titles of a category and, with depth, of up to six of its subcategories (read when first
        needed, so a small build reads only a few categories)."""
        titles = category_files(s, category, 300)
        if depth:
            subs = [c for c in commons_members(s, category, "subcat") if not NOT_A_PHOTO_CAT.search(c)]
            rng.shuffle(subs)
            for sub in subs[:6]:
                titles += category_files(s, sub.split(":", 1)[1], 100)
        titles = [t for t in dict.fromkeys(titles) if not NOT_A_PHOTO_CAT.search(t)]
        rng.shuffle(titles)
        return titles

    queues = [(category, question, answer, needs, [None], depth)
              for category, (question, answer, needs, depth) in SAFETY_PHOTOS.items()]
    rng.shuffle(queues)
    items, seen = [], set()
    per_round = 4
    while len(items) < want and any(q[4] for q in queues):
        for category, question, answer, needs, titles, depth in queues:
            if not titles or len(items) >= want:
                continue
            if titles == [None]:
                titles[:] = titles_of(category, depth)
            batch, titles[:] = titles[:per_round * 3], titles[per_round * 3:]
            got = 0
            for f in commons_files(s, [t for t in batch if t not in seen], ok=ok):
                words = f"{f['title']} {f['caption']} {f['description']}"
                if got >= per_round or (needs and not re.search(needs, words, re.I)):
                    continue
                seen.add(f["title"])
                rows = [{"question": question, "answer": answer, "credit": f["credit"]}]
                caption = tidy(capped_words(f["text"], 60)) if f["text"] else ""
                if usable(caption):
                    rows.append({"question": ASK_DESCRIBE, "answer": caption, "credit": f["credit"]})
                rows = marked(rows, caption, f["title"], " ".join(f["categories"]))
                if rows:
                    items.append((f"{f['pageid']}", f["url"], rows))
                    got += 1
    return items


def build_commons_safety_photos(limit):
    """The Commons safety equipment and hazards pack (see the module docstring)."""
    s, rng = session(), random.Random(547)
    items = [(f"safety-{n}.jpg", u, r) for n, u, r in safety_items(s, int(limit * 1.2) + 2, rng)]
    return finish("commons_safety_photos", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- safety posters and workplace safety

LOC_POSTER_SEARCHES = [("collections/works-progress-administration-posters/", {"q": "safety"}, True,
                        "Work Projects Administration Poster Collection"),
                       ("collections/works-progress-administration-posters/", {"q": "fire prevention"}, True,
                        "Work Projects Administration Poster Collection"),
                       ("collections/works-progress-administration-posters/", {"q": "accident"}, True,
                        "Work Projects Administration Poster Collection"),
                       ("photos/", {"q": "safety poster", "fa": "online-format:image"}, False,
                        "Prints and Photographs Division"),
                       ("photos/", {"q": "fire prevention poster", "fa": "online-format:image"}, False,
                        "Prints and Photographs Division"),
                       ("photos/", {"q": "accident prevention poster", "fa": "online-format:image"}, False,
                        "Prints and Photographs Division")]
POSTER_NOT_SAFETY = re.compile(r"\b(war bonds?|enlist|recruit\w*|propaganda|election|theatre|theater|concert|"
                               r"exhibition|circus|travel|tourism|film|movie)\b", re.I)
COMMONS_SAFETY_TRAINING = ("Safety posters", "Occupational Safety and Health Administration",
                           "Personal protective equipment", "High-visibility clothing", "Working at height")
# A Commons caption must name safety equipment or a hazard, and not be about a meeting or a signing.
TRAINING_NOT = re.compile(r"\b(meeting|signing|alliance|conference|stakeholder|ceremony|award\w*|speaks?|speech|"
                          r"secretary|exhibition|press|roundtable|announces?|visit\w*)\b", re.I)
PHIL_SAFETY_TERMS = ("personal protective equipment", "hard hat", "hearing protection", "face shield", "goggles",
                     "respirator", "NIOSH", "protective clothing", "coal miner", "occupational safety")
PHIL_SAFETY_WORDS = re.compile(r"\b(protective|PPE|hard hat|helmet|respirator|goggles|face shield|gloves|gown|"
                               r"hearing|earplugs?|ear muffs?|safety|hazard\w*|occupational|NIOSH|worker\w*|miners?)\b",
                               re.I)
PHIL_NOT_SAFETY = re.compile(r"\b(patient|lesion|rash|wound|micrograph|microscop\w*|specimen|culture|portrait|"
                             r"pipet\w*|microbiologist|laborator\w*|biological safety cabinet|wastewater|vials?|"
                             r"samples?|aliquots?|"
                             r"EIS Officer|graphic|infographic|illustration|poster)\b", re.I)


def loc_poster_items(s, want, rng):
    """[(file name, address, rows)] for Library of Congress safety posters with no known restrictions: the
    Library's description and, for the WPA posters (whose title is the poster's own words), what it says."""
    items, seen = [], set()
    for path, extra, says, name in LOC_POSTER_SEARCHES:
        time.sleep(2)
        data = get_json(s, LOC + path, {"fo": "json", "c": 100, "at": "results", **extra}, pause=15) or {}
        results = data.get("results") or []
        rng.shuffle(results)
        for record in results[:max(4, want // len(LOC_POSTER_SEARCHES) + 2)]:
            item = record.get("item") or {}
            title = clean(record.get("title")).strip(" /")
            summary = clean(item.get("summary"))
            picture = loc_picture(record)
            if not loc_free(record) or not picture or title in seen or POSTER_NOT_SAFETY.search(f"{title} {summary}"):
                continue
            seen.add(title)
            link = re.sub(r"^(https?:)?//", "https://", item.get("link") or record.get("id") or "")
            credit = f"{title[:150]}, {name}, Library of Congress, no known restrictions on publication, {link}"
            rows = []
            if usable(tidy(summary)):
                rows.append({"question": ASK_DESCRIBE, "answer": tidy(summary), "credit": credit})
            if says and 2 <= len(title.split()) <= 25:
                rows.append({"question": ASK_POSTER, "answer": f"It says: \"{title.rstrip('.')}\".", "credit": credit})
            rows = marked(rows, summary, title) if rows else []
            if rows:
                control = re.sub(r"\W", "", str(item.get("control_number") or record.get("id")))[-40:]
                items.append((f"loc-poster-{control}.jpg", picture, rows))
    say(f"  Library of Congress: {len(items)} safety posters")
    return items


def commons_training_items(s, want, rng):
    """[(file name, address, rows)] for Commons safety posters and workplace safety photos (OSHA's are US
    government work) with an English caption, CC0, public domain or CC BY."""
    titles = []
    for category in COMMONS_SAFETY_TRAINING:
        titles += category_files(s, category, 300)
    titles = [t for t in dict.fromkeys(titles) if not NOT_A_PHOTO_CAT.search(t)]
    rng.shuffle(titles)
    items = []
    for start in range(0, min(len(titles), want * 4), 50):
        for f in commons_files(s, titles[start:start + 50]):
            caption = tidy(capped_words(f["text"], 70)) if f["text"] else ""
            if not usable(caption) or not PHIL_SAFETY_WORDS.search(caption) or TRAINING_NOT.search(caption):
                continue
            rows = marked([{"question": ASK_DESCRIBE, "answer": caption, "credit": f["credit"]}], caption,
                          f["title"], " ".join(f["categories"]))
            if rows:
                items.append((f"training-{f['pageid']}.jpg", f["url"], rows))
        if len(items) >= want:
            break
    say(f"  Commons: {len(items)} safety posters and workplace photos")
    return items


def phil_items(s, want, rng):
    """[(file name, address, rows)] for CDC PHIL photographs of protective equipment and workplace safety, each
    item's own rights field checked (public domain only); the caption's first sentences."""
    from medical_packs import phil_search, phil_record, PHIL_CREDIT
    ids = []
    for term in PHIL_SAFETY_TERMS:
        ids += phil_search(s, term, most=max(30, want))
    ids = list(dict.fromkeys(ids))
    rng.shuffle(ids)
    items = []
    for pid in ids[:want * 3]:
        r = phil_record(s, pid)
        if not r or not r["public"] or not r["picture"]:
            continue
        caption = re.sub(r"^(Captured|Created|Taken) in \d{4},?\s*", "", r["caption"])
        caption = re.sub(r"^this (historic(al)? )?(photograph|image) (shows|depicts)\s+", "This photograph shows ",
                         caption, flags=re.I)
        answer = tidy(first_sentences(caption, 60))
        if not usable(answer) or not PHIL_SAFETY_WORDS.search(answer) or PHIL_NOT_SAFETY.search(answer):
            continue
        who = r["photographer"] or r["provider"] or "CDC"
        credit = f"{PHIL_CREDIT}, ID {pid}, {who}" + (f", {r['year']}" if r["year"] else "")
        rows = marked([{"question": ASK_DESCRIBE, "answer": answer, "credit": credit}], answer)
        if rows:
            picture = r["picture"] if r["picture"].startswith("http") else "https://phil.cdc.gov" + r["picture"]
            items.append((f"phil-{pid}.jpg", picture, rows))
        if len(items) >= want:
            break
        time.sleep(0.3)
    say(f"  CDC PHIL: {len(items)} workplace safety photographs")
    return items


def build_safety_training(limit):
    """The safety training pack: Library of Congress posters, Commons posters and workplace photos, and CDC PHIL
    protective-equipment photos, about a third each (one source down does not stop the others)."""
    s, rng, items = session(), random.Random(557), []
    third = int(limit * 0.45) + 2
    for part in (loc_poster_items, commons_training_items, phil_items):
        try:
            items += part(s, third, rng)
        except Exception as e:  # noqa: BLE001 - the other sources still count
            say(f"  {part.__name__} failed: {str(e)[:120]}")
    return finish("safety_training", items, limit, workers=3, pause=0.4)


# ----------------------------------------------------------------- D-Fire: the makers' own camera frames

DFIRE_REPO = "https://huggingface.co/datasets/badsaarow/d-fire/resolve/main/data/"
DFIRE_SHARDS = ["train-00000-of-00009.parquet", "train-00001-of-00009.parquet", "train-00002-of-00009.parquet",
                "train-00003-of-00009.parquet", "test-00000-of-00003.parquet"]
DFIRE_CLASSES = {0: "smoke", 1: "fire"}
DFIRE_CREDIT = ("D-Fire: an image dataset for fire and smoke detection (Gaia, solutions on demand; de Venâncio, Lisboa "
                "and Barbosa, Neural Computing and Applications, 2022), CC0 1.0, https://github.com/gaiasd/DFireDataset"
                "; a frame from the makers' own surveillance cameras (Apaga o Fogo)")


def dfire_answer(label):
    """The answer to "Is there a hazard here?" from a frame's YOLO boxes (class 0 smoke, class 1 fire)."""
    kinds = {DFIRE_CLASSES.get(int(line.split()[0])) for line in (label or "").splitlines() if line.split()}
    if "fire" in kinds and "smoke" in kinds:
        return "Yes: there is fire and smoke."
    if "fire" in kinds:
        return "Yes: there is fire."
    if "smoke" in kinds:
        return "Yes: there is smoke, which may come from a fire."
    return "No: I can see no fire or smoke."


def build_dfire_cameras(limit):
    """The D-Fire camera pack: frames whose file name starts "AoF" (the makers' own cameras), read row group by row
    group from the parquet copy, balanced between fire, smoke and no fire (about a third each)."""
    import pyarrow.parquet as pq
    from world_life_packs import RemoteFile
    rng = random.Random(563)
    quota = {k: limit // 3 + 1 for k in ("fire", "smoke", "none")}
    out = []
    for shard in DFIRE_SHARDS:
        if sum(quota.values()) <= 0 or len(out) >= limit:
            break
        try:
            pf = pq.ParquetFile(io.BufferedReader(RemoteFile(DFIRE_REPO + shard), 1 << 22))
        except Exception as e:  # noqa: BLE001 - the next shard
            say(f"  D-Fire {shard}: {str(e)[:100]}")
            continue
        groups = list(range(pf.num_row_groups))
        rng.shuffle(groups)
        for g in groups:
            names = pf.read_row_group(g, columns=["filename", "label"]).to_pylist()
            wanted = []
            for i, r in enumerate(names):
                answer = dfire_answer(r["label"])
                kind = "none" if answer.startswith("No") else \
                    "fire" if answer.startswith("Yes: there is fire") else "smoke"
                if str(r["filename"]).startswith("AoF") and quota[kind] > 0:
                    wanted.append((i, r["filename"], answer, kind))
            rng.shuffle(wanted)
            picked = []
            for w in wanted:
                if quota[w[3]] > 0:
                    quota[w[3]] -= 1
                    picked.append(w)
            if not picked:
                continue
            images = pf.read_row_group(g, columns=["image"]).column("image").to_pylist()
            from build_packs import smaller
            for i, filename, answer, _ in picked:
                data = smaller((images[i] or {}).get("bytes") or b"")
                if data:
                    out.append((f"dfire-{safe_name(filename)}", data,
                                {"question": ASK_HAZARD, "answer": answer, "credit": f"{DFIRE_CREDIT}, {filename}"}))
            if sum(quota.values()) <= 0 or len(out) >= limit:
                break
    say(f"dfire_cameras: {len(out)} frames")
    return out[:limit]


# ----------------------------------------------------------------- the packs

EVENTS_SAFETY_PACKS = {
    "commons_events": (build_commons_events, "Wikimedia Commons pictures of historical events, found through "
                                             "Wikidata (https://www.wikidata.org, data CC0): the event's name, date, "
                                             "place and the larger event it was part of. Each picture is CC0, public "
                                             "domain or CC BY, credited below with its author and file page "
                                             "(https://commons.wikimedia.org); captions CC0."),
    "loc_events": (build_loc_events, "Library of Congress, Prints and Photographs Division: George Grantham Bain "
                                     "Collection (https://www.loc.gov/collections/bain/) and Harris & Ewing "
                                     "Collection (https://www.loc.gov/collections/harris-ewing/), 'No known "
                                     "restrictions on publication'. Titles, dates and places from the Library's "
                                     "records. https://www.loc.gov/legal/"),
    "nara_events": (build_nara_events, "U.S. National Archives and Records Administration, National Archives "
                                       "Catalog (https://catalog.archives.gov): photographs marked 'Unrestricted', "
                                       "US government work in the public domain. Captions and dates from the "
                                       "Archives' records."),
    "europeana_events": (build_europeana_events, "Europeana (https://www.europeana.eu): pictures whose own rights "
                                                 "statement is CC0, the Public Domain Mark or CC BY, each credited "
                                                 "below with its museum or library and Europeana record."),
    "safety_signs": (build_safety_signs, "Wikimedia Commons drawings of ISO 7010 safety signs, GHS hazard "
                                         "pictograms and national road signs, each CC0, public domain or CC BY "
                                         "(credited below), rendered from SVG to PNG by Commons and placed on white. "
                                         "Sign meanings from the files' own captions; GHS pictogram names from the "
                                         "UN Globally Harmonized System."),
    "commons_safety_photos": (build_commons_safety_photos, "Wikimedia Commons photos of safety equipment and "
                                                           "hazards, each CC0, public domain or CC BY, credited "
                                                           "below with its author and file page. "
                                                           "https://commons.wikimedia.org"),
    "safety_training": (build_safety_training, "Safety posters and workplace safety photographs in the public "
                                               "domain: Library of Congress (WPA Poster Collection and Prints and "
                                               "Photographs, 'No known restrictions on publication'), Wikimedia "
                                               "Commons (CC0, public domain or CC BY, including US OSHA photos) and "
                                               "the CDC Public Health Image Library (https://phil.cdc.gov, public "
                                               "domain items only). Each credited below."),
    "dfire_cameras": (build_dfire_cameras, "D-Fire (Gaia, solutions on demand; Pedro Vinícius Almeida Borges de "
                                           "Venâncio, Adriano Chaves Lisboa and Adriano Vilela Barbosa, 2022), "
                                           "https://github.com/gaiasd/DFireDataset : 'made available to the public "
                                           "domain under the Creative Commons Zero v1.0 Universal license'. Only "
                                           "frames from the makers' own surveillance cameras (AoF). Read from the "
                                           "copy at https://huggingface.co/datasets/badsaarow/d-fire ."),
}

# How many pictures a full build takes from each collection.
EVENTS_SAFETY_LIMITS = {
    "commons_events": 6000,           # about 40 kinds of event, thousands of dated events, at most 3 pictures each
    "loc_events": 3000,               # 26 event words in two collections (Bain about 40,000, Harris & Ewing 40,000)
    "nara_events": 2500,              # 23 event words among about 1 million online photographs
    "europeana_events": 1500,         # English, open records whose title names an event (a few thousand)
    "safety_signs": 2500,             # about 300 ISO 7010 signs, the 9 GHS pictograms, road signs of ~130 countries
    "commons_safety_photos": 4000,    # 35 categories, about 6,000 files before the licence check
    "safety_training": 1200,          # about 600 LoC posters, Commons posters and OSHA photos, PHIL photos
    "dfire_cameras": 4000,            # of about 9,800 camera frames in the copy (fire, smoke and none, a third each)
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one events or safety pack builder.")
    parser.add_argument("key", choices=sorted(EVENTS_SAFETY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = EVENTS_SAFETY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child, "
        f"{sum(1 for _, _, r in entries if r.get('content') == 'graphic')} rows marked graphic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
