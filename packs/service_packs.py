"""Pack builders for military equipment and the uniformed services, past and present, used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus "place" when the record says where the photo was taken (or,
for museum objects, where the object was made: place_kind "origin"; see places.py), "child": True when the picture's
words name a child, and "content": "graphic" for war pictures whose record shows the dead, wounds, injuries or
destruction with casualties (the kit uses those rows only when the person training chooses graphic content). A
picture with more than one question comes once with its JPEG and then as (None, None, row) twins pointing at it
(food_packs.with_twins). The limit counts pictures.

Why: a describer for blind people should be able to say "This is an M4 Sherman, a US medium tank of the Second World
War" or "Police uniform of the UK, photographed in 2014, with a high-visibility jacket and a custodian helmet". Every
fact in an answer comes from the source's own record or from Wikidata (CC0), never guessed and never written by an
AI model:
  - the model, its kind, the country it comes from (Wikidata P495 country of origin, or P17 country for a single
    ship or aircraft), the service that operated it (P137, named only when there is one), the years in service
    (P729 service entry, P730 service retirement; P571 inception for decorations) and the conflicts it served in
    (P607, in date order);
  - the place a photo was taken (the camera's coordinates, turned into a country offline by places.py, or the
    archive's place headings) and its date (the file's or record's own date);
  - the caption, tidied, as "Describe this picture." (6 words or more).
Questions: "What is this?", "What uniform is this person wearing?", "What service is this?", "Describe this
picture.", "Where and when was this photo taken?" (with the conflict when the record names one) and, for museum
objects, "Tell me about this museum object.".

Safety: weapons are named and described as objects, never how to use them (captions that read like instructions
are not learnt from). War pictures of the dead, wounds or injuries are kept, described plainly from the record and
marked "content": "graphic" (GRAPHIC). Left out altogether: anything naming sexual violence, pictures whose words put
a dead or injured child at their centre, and executions or torture (NOT_SHOWN_WAR). Captions with old slurs are not
repeated. People are described with the archive's own words; rows naming a child are marked "child".

The packs (all open: public domain, CC0 or CC BY, checked at the source in November 2026):
  commons_military    Wikimedia Commons categories of military models and named ships, found through Wikidata:
                      tanks and armoured vehicles, jeeps, artillery, military aircraft and helicopters, warships,
                      submarines and boats, small arms, swords and armour, and military decorations. Files CC0, public
                      domain (most US forces photos) or CC BY, each credited; captions CC0. Wikidata gives each model's
                      facts (WD_KINDS). "What is this?", the caption, and "Where and when ...".
  commons_airplanes   The same for airliners, business jets, light aircraft, cargo planes, flying boats, airships and
                      civil helicopters (models that are not military kinds), said as airplanes ("a passenger
                      airplane").
  commons_uniformed   Wikimedia Commons categories of people in uniform by country: police officers, firefighters,
                      paramedics, military police, park rangers, nurses, postal workers, border guards and military
                      uniforms ("Police officers of the United Kingdom" ...), ceremonial guards (the King's Guard, the
                      Pontifical Swiss Guard, the Evzones), prison guards, customs officers and mail carriers, and police
                      cars, fire engines, ambulances and coast guards by country. "What uniform is this person
                      wearing?" ("Police uniform of the UK, photographed in 2014, with a high-visibility jacket"),
                      details only from the file's caption, title and categories (UNIFORM_DETAILS).
  loc_service         Library of Congress, Prints and Photographs: the Civil War glass negatives (about 8,700), the
                      Bain news photos of soldiers and the First World War (about 3,000), and searches by subject
                      (tanks, warships, military uniforms, police, fire fighters, fire engines, nurses, postal workers).
                      "No known restrictions on publication" only (the Library's Second World War and Korean War
                      subject headings lead mostly to Veterans History Project photos, which are restricted). The
                      Library's titles; the place and date from the record; the conflict from the collection or the
                      record's subject headings and title.
  nara_military       US National Archives catalogue: General Photographic Files of the Department of the Navy
                      (80-G), the Marine Corps (127), the Coast Guard (26-G) and the Army Signal Corps (111-SC), each
                      with its caption and production date. US government work, public domain; only records marked
                      "Unrestricted".
  army_mil            U.S. Army photos from www.army.mil/photos (about 250 of the latest, renewed by the Army), each
                      with its full caption and photographer. US government work, public domain.
  nasm_aircraft       Smithsonian National Air and Space Museum, open access (CC0): aircraft with their full records
                      (maker, date, country, the museum's use flags such as "Fighters" and "World War I"), and flight
                      uniforms, helmets, insignia and medals. "What is this?" for aircraft, the museum's physical
                      description as "Describe this picture." and its summary as "Tell me about this museum object.".
  nmah_service        Smithsonian National Museum of American History, open access (CC0 pictures only): uniforms,
                      insignia, medals, arms and armour, police and fire objects (topics "Armed Forces History",
                      "Firefighting", "Law Enforcement" ...), the museum's description and where and when each was
                      made.

Share-alike, non-commercial and research collections on the same subjects are kit entries in
training-kit/kit/service_sources.py (Commons BY-SA and GFDL files of the same categories, Bundesarchiv photos on
Commons, Europeana 1914-1918), with the collections needing sign-up and those that could not be used.

Needing sign-up (get them yourself, then put them in the own-pictures folder):
  DVIDS (Defense Visual Information Distribution Service, https://www.dvidshub.net): US forces photos, public
      domain, but its API needs a free key (https://api.dvidshub.net). Many of its photos are already on Commons
      and reach commons_military and commons_uniformed.
  NARA catalogue API v2 (https://catalog.archives.gov/api/v2): needs a key; the catalogue's public search, used
      above, does not, but it can only walk series whose number is known.
  Flickr collections of the US Air Force, US Navy, US Coast Guard, US Army, NASA Armstrong, the UK Ministry of
      Defence and many police and fire services: a free Flickr API key (https://www.flickr.com/services/api/).
  Imperial War Museums (https://www.iwm.org.uk/collections): IWM Non-Commercial Licence; its site refused this
      machine (Cloudflare check) and has no open API. Download by hand under its licence if wanted.
  National Army Museum, RAF Museum, Royal Museums Greenwich, Canadian War Museum: online collections without a bulk
      download or an open licence; ask the museum (most images are for non-commercial use with permission).

Looked at and not used here (November 2026), with the reason:
  af.mil, uscg.mil and navy.mil photo pages, FEMA's media library, americanhistory.si.edu and api.si.edu: refused
      this machine (403). Their Commons copies are in the Commons packs; the Smithsonian's own bulk files are used
      (nasm_aircraft, nmah_service).
  Naval History and Heritage Command (www.history.navy.mil): public domain, but no secure connection could be made
      (an incomplete certificate chain); its photos are widely on Commons (NH series), so they reach commons_military.
  US Army Center of Military History: its art and photos are on Commons and DVIDS; no listing service of its own.
  NASA aircraft photos: already in the kit (training-kit/kit/sources.py "nasa").
  Australian War Memorial and Nationaal Archief: already open packs (archive_packs.py "awm" and "anefo").
  Europeana with an open-licence filter: almost no English descriptions of military or police photos came back
      (mostly Wellcome prints and find records); Europeana 1914-1918 is CC BY-SA and is a share-alike kit entry.

    python packs/service_packs.py commons_military --limit 8      (prints a few rows: a quick check of one builder)
"""

import json
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, fetch_all, say, COMMONS_FREE, MUSEUM, SI_BUCKET, si_keys, \
    first_sentences
from food_packs import with_twins, count_pictures, commons_get, commons_members
from expression_packs import CHILD
from everyday_packs import a_or_an as plain_a_or_an
from world_packs import capped_words, full_stop
from places import country_at, country_named, place_from_text, where
from documentary_packs import tidy, usable, get_json, loc_picture, loc_place, loc_free, place_words, LOC
from archive_packs import SLURS, sentence_case, lc_place, nara_picture, NARA_SEARCH, NARA, NARA_NOTES, WRA_FULL

ASK_WHAT = "What is this?"
ASK_UNIFORM = "What uniform is this person wearing?"
ASK_SERVICE = "What service is this?"
ASK_DESCRIBE = "Describe this picture."
ASK_WHERE_WHEN = "Where and when was this photo taken?"
WDQS = "https://query.wikidata.org/sparql"

# War pictures of the dead, wounds and injuries: kept, marked "content": "graphic".
GRAPHIC = re.compile(r"\b(dead|corpses?|bod(y|ies) of|killed|wounded|wounds?|casualt\w*|injur\w*|bloody|blood|"
                     r"massacre\w*|atrocit\w*|skeletons?|remains of (the )?(dead|soldiers?|victims?)|slain|"
                     r"mortally|amputat\w*|burned bodies|charred|mass graves?|dying|fallen soldiers?)\b", re.I)
# Never kept: sexual violence, executions and torture (and propaganda made of them).
NOT_SHOWN_WAR = re.compile(r"\b(rap(e|ed|es|ing)|sexual(ly)? (assault|violence|abuse)\w*|molest\w*|execut(ion|ions|ed|"
                           r"ing)|firing squad|beheading|beheaded|hang(ed|ing) of|being hanged|lynch\w*|tortur\w*|"
                           r"nud\w*|naked|topless|porn\w*|erotic\w*)\b", re.I)
# Captions that read like instructions for a weapon: the picture keeps its other rows, the caption is not learnt.
HOW_TO = re.compile(r"\b(how to|step[- ]by[- ]step|instructions?|disassembl\w*|field[- ]strip\w*|reassembl\w*|"
                    r"load(ing)? (the|a) (magazine|weapon|rifle|pistol)|manual of arms)\b", re.I)
# The conflicts a caption or subject heading may name, with how an answer says them.
CONFLICTS = [(re.compile(r"world war,? 1914-1918|world war i\b|first world war|great war|wwi\b", re.I),
              "the First World War"),
             (re.compile(r"world war,? 1939-1945|world war ii\b|second world war|ww2|wwii", re.I),
              "the Second World War"),
             (re.compile(r"korean war", re.I), "the Korean War"),
             (re.compile(r"vietnam war", re.I), "the Vietnam War"),
             (re.compile(r"spanish-american war", re.I), "the Spanish-American War"),
             (re.compile(r"(american |u\.s\. )?civil war,? 1861-1865|american civil war", re.I),
              "the American Civil War"),
             (re.compile(r"gulf war|operation desert (storm|shield)", re.I), "the Gulf War"),
             (re.compile(r"falklands war", re.I), "the Falklands War"),
             (re.compile(r"\bcold war\b", re.I), "the Cold War")]


# Military words that the child pattern would mistake for a child ("infantry", "Sons of Liberty", "Pvt. Son").
NOT_A_CHILD = re.compile(r"\b(infantr\w*|infante\w*|sons of [A-Z]\w+|minor (repairs?|damage|injur\w*)|"
                         r"boys? (scouts?|brigade)|ship'?s boys?|powder monkeys?)\b", re.I)


def safety(texts):
    """(keep, extra row fields) for a picture from its words: keep is False when they name sexual violence, an
    execution or torture, or a dead or injured child, or hold an old slur; the extra fields mark "content": "graphic"
    (the dead, wounds, injuries) and "child"."""
    text = " ".join(t for t in texts if t)
    if NOT_SHOWN_WAR.search(text) or SLURS.search(text):
        return False, {}
    graphic, child = bool(GRAPHIC.search(text)), bool(CHILD.search(NOT_A_CHILD.sub(" ", text)))
    if graphic and child:
        return False, {}
    extra = {}
    if graphic:
        extra["content"] = "graphic"
    if child:
        extra["child"] = True
    return True, extra


def conflict_in(*texts):
    """The first conflict a caption or subject heading names ("the Second World War"), or ""."""
    text = " ".join(t for t in texts if t)
    return next((said for pattern, said in CONFLICTS if pattern.search(text)), "")


def when_words(text):
    """How a record's date is said after "taken": "in 1941", "between 1861 and 1865", "around 1918", or ""."""
    text = clean(text)
    if not text or re.search(r"no date|undated|unknown", text, re.I):
        return ""
    years = re.findall(r"\b(1[6-9]\d\d|20\d\d)\b", text)
    if not years:
        return ""
    if len(set(years)) >= 2 and re.search(r"between|-|–|to", text):
        return f"between {min(years)} and {max(years)}"
    if re.search(r"\b(ca\.?|circa|about|approximately|\?)", text, re.I):
        return f"around {years[0]}"
    return f"in {years[0]}"


def where_when_row(place, when, conflict, credit, extra):
    """The "Where and when was this photo taken?" row from what the record says, or None when it says neither
    place nor date: "It was taken in France in 1918, during the First World War."."""
    if not place and not when:
        return None
    answer = "It was taken" + (f" in {place_words(place)}" if place else "") + (f" {when}" if when else "")
    if conflict:
        answer += f", during {conflict}"
    return {"question": ASK_WHERE_WHEN, "answer": answer + ".", "credit": credit, **where(place), **extra}


def file_name(prefix, text):
    """A picture's file name in the zip: prefix and a tidy short form of text."""
    return f"{prefix}-" + re.sub(r"[^\w.-]+", "_", text)[:80].strip("_") + ".jpg"


def finish(key, items, limit, workers=3, pause=0.3):
    """Shuffle (name, address, rows) items, download the pictures and return the pack entries (at most limit
    pictures), saying how many came and how many rows are graphic or marked child."""
    random.Random(len(key) * 7907).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.2) + 2], workers=workers, pause=pause)[:limit]
    entries = with_twins(fetched)
    say(f"{key}: {len(fetched)} pictures, {len(entries)} rows, "
        f"{sum(1 for _, _, r in entries if r.get('content') == 'graphic')} graphic rows, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return entries


def a_or_an(phrase):
    """ "a" or "an" before a phrase, knowing that "US", "Ukrainian" and "European" start with a "you" sound ("a US
    medium tank")."""
    if re.match(r"^(U\.?S\.?\b|Ukrain|Ugand|Urugu|Uzbek|Europe|Unite|Univers|Union|Utility|Unif)", phrase):
        return "a"
    return plain_a_or_an(phrase)


# ----------------------------------------------------------------- Wikidata: model facts

# The kinds of thing, most specific first: (Wikidata class, how an answer says it, group). An item takes the first
# kind whose class tree (the class and its subclasses) holds one of the item's classes: its "subclass of" for a
# model ("M4 Sherman" is a subclass of "medium tank"), its "instance of" for a single ship or aircraft ("USS Missouri"
# is an instance of "Iowa-class battleship", a subclass of "battleship").
WD_KINDS = [
    ("Q920182", "main battle tank", "vehicle"), ("Q1069116", "medium tank", "vehicle"),
    ("Q771712", "heavy tank", "vehicle"), ("Q875583", "light tank", "vehicle"), ("Q161161", "tank destroyer", "vehicle"),
    ("Q12876", "tank", "vehicle"), ("Q202825", "infantry fighting vehicle", "vehicle"),
    ("Q4407246", "armoured personnel carrier", "vehicle"), ("Q649062", "armoured car", "vehicle"),
    ("Q2000908", "self-propelled gun", "vehicle"), ("Q506219", "multiple rocket launcher", "vehicle"),
    ("Q180126", "howitzer", "vehicle"), ("Q1330892", "field gun", "vehicle"), ("Q7325635", "anti-aircraft gun", "vehicle"),
    ("Q81103", "cannon", "vehicle"), ("Q6546105", "military light utility vehicle (a jeep)", "vehicle"),
    ("Q753058", "attack helicopter", "aircraft"), ("Q2735392", "utility helicopter", "aircraft"),
    ("Q1543102", "military helicopter", "aircraft"), ("Q385642", "fighter-bomber", "aircraft"),
    ("Q127771", "fighter aircraft", "aircraft"), ("Q170877", "bomber", "aircraft"),
    ("Q3041792", "reconnaissance aircraft", "aircraft"),
    ("Q17205", "aircraft carrier", "ship"), ("Q182531", "battleship", "ship"), ("Q104843", "cruiser", "ship"),
    ("Q174736", "destroyer", "ship"), ("Q161705", "frigate", "ship"), ("Q170013", "corvette", "ship"),
    ("Q2811", "submarine", "ship"), ("Q207452", "ship of the line", "ship"), ("Q324233", "torpedo boat", "ship"),
    ("Q214196", "gunboat", "ship"), ("Q202527", "minesweeper", "ship"), ("Q11479410", "patrol boat", "ship"),
    ("Q474748", "amphibious assault ship", "ship"),
    ("Q177456", "assault rifle", "weapon"), ("Q1194268", "battle rifle", "weapon"),
    ("Q190570", "sniper rifle", "weapon"), ("Q183302", "carbine", "weapon"), ("Q178550", "submachine gun", "weapon"),
    ("Q720711", "light machine gun", "weapon"), ("Q12800", "machine gun", "weapon"),
    ("Q3389302", "semi-automatic pistol", "weapon"), ("Q170382", "revolver", "weapon"), ("Q1907525", "pistol", "weapon"),
    ("Q486396", "shotgun", "weapon"), ("Q178243", "musket", "weapon"), ("Q124072", "rifle", "weapon"),
    ("Q12791", "sword", "weapon"), ("Q182780", "dagger", "weapon"), ("Q173366", "bayonet", "weapon"),
    ("Q3579211", "combat helmet", "weapon"), ("Q3391846", "suit of plate armour", "weapon"),
    ("Q1788716", "military decoration", "decoration"),
    # The general kinds last, so a ship or an aircraft is never called just a military vehicle.
    ("Q2031121", "warship", "ship"), ("Q216916", "military aircraft", "aircraft"),
    ("Q130368", "armoured fighting vehicle", "vehicle"), ("Q1184840", "military vehicle", "vehicle"),
]

# Civil aircraft, said as airplanes; an item that is also a military kind is left out of this pack.
WD_CIVIL_KINDS = [
    ("Q210932", "airliner (a passenger airplane)", "civil"), ("Q1062135", "business jet (a small passenger airplane)",
                                                              "civil"),
    ("Q19799", "cargo airplane", "civil"), ("Q1153376", "flying boat (an airplane that lands on water)", "civil"),
    ("Q1372231", "light aircraft (a small airplane)", "civil"), ("Q133585", "airship", "civil"),
    ("Q34486", "helicopter", "civil"),
]
# How a pack shares its pictures between the groups.
GROUP_SHARE = {"vehicle": 0.3, "aircraft": 0.22, "ship": 0.22, "weapon": 0.18, "decoration": 0.08, "civil": 1.0}
# Short adjectives for countries of origin (Wikidata QIDs); others use Wikidata's English demonym, or no adjective.
ADJECTIVES = {"Q30": "US", "Q145": "British", "Q174193": "British", "Q161885": "British", "Q15180": "Soviet",
              "Q7318": "German", "Q183": "German", "Q43287": "German", "Q41304": "German", "Q713750": "West German",
              "Q16957": "East German", "Q142": "French", "Q70972": "French", "Q71084": "French", "Q17": "Japanese",
              "Q188712": "Japanese", "Q159": "Russian", "Q34266": "Russian", "Q38": "Italian", "Q172579": "Italian",
              "Q148": "Chinese", "Q13426199": "Chinese", "Q16": "Canadian", "Q408": "Australian", "Q34": "Swedish",
              "Q39": "Swiss", "Q36": "Polish", "Q55": "Dutch", "Q29": "Spanish", "Q43": "Turkish", "Q12560": "Ottoman",
              "Q801": "Israeli", "Q668": "Indian", "Q155": "Brazilian", "Q884": "South Korean", "Q423": "North Korean",
              "Q33": "Finnish", "Q213": "Czech", "Q33946": "Czechoslovak", "Q28513": "Austro-Hungarian",
              "Q40": "Austrian", "Q31": "Belgian", "Q35": "Danish", "Q20": "Norwegian", "Q41": "Greek",
              "Q45": "Portuguese", "Q794": "Iranian", "Q212": "Ukrainian", "Q865": "Taiwanese", "Q414": "Argentine",
              "Q96": "Mexican", "Q664": "New Zealand", "Q258": "South African", "Q36704": "Yugoslav",
              "Q218": "Romanian", "Q28": "Hungarian", "Q219": "Bulgarian", "Q252": "Indonesian", "Q843": "Pakistani",
              "Q79": "Egyptian", "Q851": "Saudi", "Q881": "Vietnamese", "Q869": "Thai", "Q928": "Filipino",
              "Q241": "Cuban", "Q298": "Chilean", "Q739": "Colombian", "Q736": "Ecuadorian", "Q419": "Peruvian",
              "Q717": "Venezuelan", "Q37": "Lithuanian", "Q211": "Latvian", "Q191": "Estonian", "Q184": "Belarusian",
              "Q224": "Croatian", "Q403": "Serbian", "Q215": "Slovenian", "Q214": "Slovak", "Q27": "Irish",
              "Q1033": "Nigerian", "Q115": "Ethiopian", "Q114": "Kenyan", "Q1028": "Moroccan", "Q262": "Algerian",
              "Q796": "Iraqi", "Q858": "Syrian", "Q889": "Afghan", "Q902": "Bangladeshi", "Q334": "Singaporean",
              "Q833": "Malaysian", "Q232": "Kazakh"}
# Not a country of origin a sentence can use (a company or a region given by mistake).
NOT_COUNTRY = re.compile(r"\b(company|corporation|inc\.?|ltd|gmbh|works|factory)\b", re.I)


def sparql(s, query, tries=5):
    """The rows of a Wikidata SPARQL query ([{name: value}]), waiting and trying again when the service is busy;
    [] when it never answered."""
    for attempt in range(tries):
        try:
            r = s.get(WDQS, params={"query": query, "format": "json"}, timeout=120)
            if r.status_code == 200:
                return [{k: v["value"].rsplit("/entity/", 1)[-1] for k, v in b.items()}
                        for b in r.json()["results"]["bindings"]]
            after = r.headers.get("Retry-After", "")
            time.sleep(int(after) if after.isdigit() else 10 * (attempt + 1))
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(10 * (attempt + 1))
    say("  Wikidata did not answer a query")
    return []


def kind_items(s, qid):
    """{item: (Commons category, "model" or "one")} of the items of one kind that have a Commons category: models
    (subclasses of the kind's class tree) and single ships, aircraft or decorations (instances of it)."""
    rows = sparql(s, f"""SELECT DISTINCT ?item ?cat ?how WHERE {{ ?c wdt:P279* wd:{qid} .
        {{ ?item wdt:P279 ?c . BIND("model" AS ?how) }} UNION {{ ?item wdt:P31 ?c . BIND("one" AS ?how) }}
        ?item wdt:P373 ?cat . }}""")
    out = {}
    for r in rows:
        if r["item"].startswith("Q") and r["item"] != qid:
            out.setdefault(r["item"], (r["cat"], r["how"]))
    return out


def wd_facts(s, items):
    """{item: facts} for Wikidata items, 150 a query: label, origins (P495), countries (P17), operators (P137),
    service entry and retirement years (P729, P730), inception (P571), conflicts (P607) and makers (P176)."""
    out = {}
    items = list(items)
    for start in range(0, len(items), 150):
        values = " ".join(f"wd:{q}" for q in items[start:start + 150])
        rows = sparql(s, f"""SELECT ?item ?label (GROUP_CONCAT(DISTINCT ?o; separator="|") AS ?origins)
            (GROUP_CONCAT(DISTINCT ?c; separator="|") AS ?countries) (GROUP_CONCAT(DISTINCT ?op; separator="|") AS ?ops)
            (MIN(?from) AS ?start) (MAX(?to) AS ?end) (MIN(?made) AS ?inception)
            (GROUP_CONCAT(DISTINCT ?war; separator="|") AS ?wars) WHERE {{ VALUES ?item {{ {values} }}
            ?item rdfs:label ?label . FILTER(LANG(?label) = "en")
            OPTIONAL {{ ?item wdt:P495 ?o }} OPTIONAL {{ ?item wdt:P17 ?c }} OPTIONAL {{ ?item wdt:P137 ?op }}
            OPTIONAL {{ ?item wdt:P729 ?from }} OPTIONAL {{ ?item wdt:P730 ?to }} OPTIONAL {{ ?item wdt:P571 ?made }}
            OPTIONAL {{ ?item wdt:P607 ?war }} }} GROUP BY ?item ?label""")
        for r in rows:
            out[r["item"]] = {"label": r.get("label", ""), "start": r.get("start", "")[:4],
                              "end": r.get("end", "")[:4], "inception": r.get("inception", "")[:4],
                              **{k: [v for v in (r.get(k) or "").split("|") if v.startswith("Q")]
                                 for k in ("origins", "countries", "ops", "wars")}}
        time.sleep(1)
    return out


def wd_labels(s, ids):
    """{id: (English label, English demonym, start date)} for countries, operators and conflicts."""
    out = {}
    ids = list(ids)
    for start in range(0, len(ids), 200):
        values = " ".join(f"wd:{q}" for q in ids[start:start + 200])
        for r in sparql(s, f"""SELECT ?x ?label (SAMPLE(?d) AS ?dem) (MIN(?t) AS ?start) WHERE {{ VALUES ?x {{ {values} }}
                ?x rdfs:label ?label . FILTER(LANG(?label) = "en")
                OPTIONAL {{ ?x wdt:P1549 ?d . FILTER(LANG(?d) = "en") }} OPTIONAL {{ ?x wdt:P580 ?t }} }}
                GROUP BY ?x ?label"""):
            out[r["x"]] = (r.get("label", ""), r.get("dem", ""), r.get("start", ""))
        time.sleep(1)
    return out


def conflict_name(label):
    """A conflict's label as it follows "of": "World War II" -> "the Second World War", "Korean War" -> "the Korean
    War", "Operation Desert Storm" -> "Operation Desert Storm"."""
    label = {"World War II": "Second World War", "World War I": "First World War"}.get(label, label)
    if re.match(r"^(Operation|Battle of|Siege of)\b", label) or re.match(r"^the\b", label, re.I):
        return label
    return "the " + label


def service_name(label):
    """An operator's label after "operated by": "the Royal Air Force", "the United States Navy", "British Airways"."""
    if re.search(r"\b(Navy|Army|Air Force|Corps|Marines?|Guard|Forces?|Service|Police|Administration|Ministry)\b",
                 label) and not label.lower().startswith("the "):
        return "the " + label
    return label


def model_answer(item, facts, how, kind, labels):
    """"This is an M4 Sherman, a US medium tank of the Second World War and the Korean War, in service from 1942 to
    1957." from Wikidata facts; "" when Wikidata gives no country, period or conflict (nothing worth saying)."""
    name = clean(facts.get("label"))
    if not name or re.match(r"^Q\d+$", name):
        return ""
    countries = facts["origins"] or (facts["countries"] if how == "one" or kind == "military decoration" else [])
    adjective = ""
    if len(countries) == 1:
        label, demonym, _ = labels.get(countries[0], ("", "", ""))
        adjective = ADJECTIVES.get(countries[0]) or (demonym if demonym and not NOT_COUNTRY.search(label) else "")
    wars = sorted((labels[w][2] or "9999", conflict_name(labels[w][0])) for w in facts["wars"]
                  if w in labels and labels[w][0])
    wars = list(dict.fromkeys(w for _, w in wars))
    if kind == "military decoration":
        period = f", established in {facts['inception']}" if facts["inception"] else ""
    elif facts["start"] and facts["end"] and facts["end"] >= facts["start"]:
        period = f", in service from {facts['start']} to {facts['end']}"
    elif facts["start"]:
        period = f", which entered service in {facts['start']}"
    else:
        period = ""
    if not adjective and not wars and not period:
        return ""
    if how == "model":
        subject = f"{a_or_an(name)} {name}"
    elif kind == "military decoration" and not name.lower().startswith("the "):
        subject = f"the {name}"
    else:
        subject = name
    described = f"{adjective} {kind}".strip()
    answer = f"This is {subject}, {a_or_an(described)} {described}"
    if wars:
        shown = wars[:2]
        answer += " of " + (" and ".join(shown) if len(wars) <= 2 else ", ".join(shown) + " and other conflicts")
    answer += period
    if len(facts["ops"]) == 1 and facts["ops"][0] in labels and labels[facts["ops"][0]][0]:
        answer += f", operated by {service_name(labels[facts['ops'][0]][0])}"
    return full_stop(answer)


WD_CACHE = {}           # {qid: kind_items(...)}: the military kinds are read once when both Commons packs are built


def wd_models(s, kinds, avoid=()):
    """[(item, Commons category, how, kind phrase, group, answer)] for every kind in kinds (an item counted under
    its first kind), leaving out items of the kinds in avoid."""
    taken, chosen = set(), []
    for qid, _, _ in avoid:
        if qid not in WD_CACHE:
            WD_CACHE[qid] = kind_items(s, qid)
        taken.update(WD_CACHE[qid])
    for qid, phrase, group in kinds:
        if qid not in WD_CACHE:
            WD_CACHE[qid] = kind_items(s, qid)
        for item, (cat, how) in WD_CACHE[qid].items():
            if item not in taken:
                taken.add(item)
                chosen.append([item, cat, how, phrase, group])
        time.sleep(1)
    say(f"  Wikidata: {len(chosen)} items with a Commons category")
    facts = wd_facts(s, [c[0] for c in chosen])
    ids = {q for f in facts.values() for k in ("origins", "countries", "ops", "wars") for q in f[k]}
    labels = wd_labels(s, ids)
    out = []
    for item, cat, how, phrase, group in chosen:
        if item in facts:
            answer = model_answer(item, facts[item], how, phrase, labels)
            if answer:
                out.append((item, cat, how, phrase, group, answer))
    say(f"  Wikidata: {len(out)} items with facts to say")
    return out


# ----------------------------------------------------------------- Wikimedia Commons files

# Subcategories and files that are not photos of the thing itself: drawings, models, toys, parts, insides, logos.
NOT_THE_THING = re.compile(r"\b(drawings?|diagrams?|schem\w*|blueprints?|plans?|illustrations?|paintings?|art|"
                           r"models?|scale|toys?|miniatures?|lego|kits?|dioramas?|cosplay\w*|logos?|icons?|svg|"
                           r"insignia|emblems?|patch(es)?|stamps?|coins?|posters?|maps?|charts?|interiors?|cockpits?|"
                           r"engines?|instrument\w*|details?|wheels?|tracks?|turrets?|parts?|components?|video\w*|"
                           r"audio|nose art|manuals?|documents?|cartoons?|animations?|renders?|renderings?|cgi|"
                           r"3d|computer[- ]generated|games?|video game|screenshots?|ammunition|cartridges?|"
                           r"people associated|personnel|crews?|commanders?)\b", re.I)
# File categories and words about people (the share-alike entry for picture-making leaves those out).
UNIFORM_DETAILS = [
    (r"high[- ]?vis\w*|hi[- ]?vis|reflective (vest|jacket)|safety vests?|fluorescent (vest|jacket)",
     "a high-visibility jacket"),
    (r"custodian helmets?", "a custodian helmet"), (r"bearskins?", "a bearskin cap"),
    (r"peaked caps?|visor caps?", "a peaked cap"), (r"\bberets?\b", "a beret"), (r"\bk[eé]pis?\b", "a kepi"),
    (r"\bshakos?\b", "a shako"), (r"pith helmets?|sun helmets?", "a pith helmet"),
    (r"fire(fighter|man)'?s? helmets?|fire helmets?", "a firefighter's helmet"),
    (r"turnout (gear|coats?)|bunker gear", "turnout gear"), (r"breathing apparatus|scba", "breathing apparatus"),
    (r"body armou?r|bullet[- ]?proof vests?|stab vests?|ballistic vests?", "body armour"),
    (r"camouflage|camo\b", "camouflage"), (r"dress uniforms?|full dress|parade uniforms?", "a dress uniform"),
    (r"\btunics?\b", "a tunic"), (r"\bsash(es)?\b", "a sash"), (r"white gloves", "white gloves"),
    (r"\bmedals?\b|decorations", "medals"), (r"epaulet\w*", "epaulettes"), (r"aiguillettes?", "an aiguillette"),
    (r"greatcoats?", "a greatcoat"), (r"\bplumes?\b|feathered", "a plume"), (r"halberds?", "a halberd"),
    (r"\bkilts?\b", "a kilt"), (r"\bturbans?\b", "a turban"), (r"nurse'?s? caps?", "a nurse's cap"),
    (r"\baprons?\b", "an apron"), (r"\bscrubs\b", "scrubs"), (r"white coats?|lab coats?", "a white coat"),
    (r"\bfustanellas?\b", "a fustanella (a pleated kilt)"), (r"\btsarouchia\b", "tsarouchia (pompom shoes)"),
    (r"stetsons?|campaign hats?|ranger hats?", "a campaign hat"), (r"helmets?", "a helmet"),
]
UNIFORM_DETAILS = [(re.compile(r"\b(" + p + r")\b", re.I), said) for p, said in UNIFORM_DETAILS]


def details_in(*texts):
    """The uniform details a file's words name ("a high-visibility jacket and a custodian helmet"), at most three,
    a general "a helmet" only when no particular helmet is named; or ""."""
    text = " ".join(t for t in texts if t)
    found = []
    for pattern, said in UNIFORM_DETAILS:
        if pattern.search(text) and said not in found:
            if said == "a helmet" and any("helmet" in f for f in found):
                continue
            found.append(said)
    found = found[:3]
    return " and ".join(found) if len(found) <= 2 else f"{found[0]}, {found[1]} and {found[2]}"


def commons_year(value):
    """The year a Commons file's photo was taken, from its DateTimeOriginal ("2014-05-03 12:00:00", "1944",
    "circa 1917"), or ""."""
    years = [y for y in re.findall(r"\b(1[89]\d\d|20[0-2]\d)\b", clean(value)) if int(y) <= 2026]
    return years[0] if years else ""


# Catalogue lines that are not captions ("Catalog #: 01_00086067, Title: ..."), and captions that say the picture is
# a model or a toy, not the thing itself.
NOT_A_CAPTION = re.compile(r"catalog(ue)? ?#|\btitle:|\btitre\s*:|\bformat\s*:|r[ée]f[ée]rence|corporation name|"
                           r"official nickname|\b(scale )?(models?|miniatures?|toys?|replicas?) of\b|\bscale model|"
                           r"\bdiorama", re.I)
# Files that are paintings, drawings or prints (by their name or categories), not photos.
PAINTED = re.compile(r"\b(paintings?|painted by|oil on|watercolou?rs?|drawings?|lithograph\w*|engravings?|etchings?|"
                     r"woodcuts?|prints? (of|by)|illustrations?|retrato|gem[äa]lde|peinture|tableau|portrait "
                     r"paintings|caricatures?|cartoons?|posters?)\b", re.I)


def trusted_year(year, caption, title, latitude):
    """The file's year when it can be trusted as the year the photo was taken: when the caption or file name says
    the same year, or when the camera recorded its coordinates (a camera's own date). An old photo scanned or
    uploaded later often carries the scan date, so otherwise no year is given."""
    if year and (year in f"{caption} {title}" or latitude):
        return year
    return ""


def era_words(year):
    """A photo's era after "photographed": "in 2014", "in the 1940s" (before 1980), or ""."""
    if not year:
        return ""
    return f"in the {year[:3]}0s" if int(year) < 1980 else f"in {year}"


def commons_files(s, titles, free=True):
    """[{title, url, credit, caption, year, place, cats}] for files whose licence is CC0, public domain or CC BY
    (never SA, NC or ND), JPEG or PNG, 50 files a request: the English caption (or the start of the English
    description), the photo's year, the country at the camera's coordinates and the file's categories."""
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 1280,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|GPSLatitude|"
                                                      "GPSLongitude|DateTimeOriginal|Categories",
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
            upper = licence.upper()
            if free and (not COMMONS_FREE.match(licence) or re.search(r"\b(SA|NC|ND)\b", upper)):
                continue
            if info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                continue
            value = lambda k: clean((meta.get(k) or {}).get("value"))          # noqa: E731
            if PAINTED.search(f"{p['title']} {value('Categories')}"):
                continue                               # a painting, drawing or print: not a photo of the thing
            artist = value("Artist")[:100] or "unknown"
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            caption = tidy(captions.get(f"M{p['pageid']}"))
            if NOT_A_CAPTION.search(caption):
                caption = ""
            if not usable(caption):
                description = re.sub(r"^\s*English\s*:\s*", "", value("ImageDescription"))
                caption = tidy(capped_words(description, 60))
                if not usable(caption) or re.match(r"^[\d\W]", caption) or re.search(r"\b[a-z]{2}:\S", caption) \
                        or NOT_A_CAPTION.search(caption):
                    caption = ""
            out.append({"title": p["title"], "url": re.sub(r"/\d+px-([^/]+)$", r"/1280px-\1", info["thumburl"]),
                        "credit": f"{p['title']} by {artist}, {licence}, {page}", "caption": caption,
                        "year": trusted_year(commons_year(value("DateTimeOriginal")), caption, p["title"],
                                             value("GPSLatitude")),
                        "place": country_at(value("GPSLatitude"), value("GPSLongitude"))
                        if value("GPSLatitude") and value("GPSLongitude") else "",
                        "cats": value("Categories").replace("|", "; ")})
        time.sleep(1)
    return out


def category_titles(s, category, most_subcats=6):
    """The file titles of a Commons category and of up to most_subcats of its subcategories that are photos of the
    thing (NOT_THE_THING left out); [] when the category cannot be read."""
    try:
        titles = commons_members(s, category, "file")
        subcats = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
    except RuntimeError:
        return []
    for sub in [c for c in subcats if not NOT_THE_THING.search(c)][:most_subcats]:
        try:
            titles += commons_members(s, sub, "file")
        except RuntimeError:
            break
    return [t for t in dict.fromkeys(titles) if not NOT_THE_THING.search(t.rsplit(".", 1)[0])]


def model_rows(f, answer, kind, group):
    """The rows of one Commons file of a model: "What is this?", its caption (not for a caption that reads like
    weapon instructions) and "Where and when ..."; [] when its words must be left out."""
    keep, extra = safety([f["caption"], f["title"], f["cats"]])
    if not keep:
        return []
    rows = [{"question": ASK_WHAT, "answer": answer, "credit": f["credit"], **where(f["place"]), **extra}]
    if f["caption"] and not (group == "weapon" and HOW_TO.search(f["caption"])):
        rows.append({"question": ASK_DESCRIBE, "answer": f["caption"], "credit": f["credit"], **where(f["place"]),
                     **extra})
    row = where_when_row(f["place"], f"in {f['year']}" if f["year"] else "", conflict_in(f["caption"]),
                         f["credit"], extra)
    if row:
        rows.append(row)
    return rows


def build_commons_models(key, kinds, avoid, limit):
    """A Commons pack of models: Wikidata's items of the kinds (WD_KINDS or WD_CIVIL_KINDS) with a Commons category
    and facts to say, a few free files of each (the groups share the pack by GROUP_SHARE, and no item gives more
    than per_item pictures)."""
    s = session()
    models = wd_models(s, kinds, avoid)
    rng = random.Random(sum(map(ord, key)))
    rng.shuffle(models)
    items = []
    for group in dict.fromkeys(g for _, _, g in kinds):
        want = int(limit * GROUP_SHARE[group] * 1.25) + 2
        group_models = [m for m in models if m[4] == group]
        per_item = max(2, min(6, want // max(1, len(group_models)) + 1))
        found = 0
        for item, cat, how, phrase, _, answer in group_models:
            if found >= want:
                break
            titles = category_titles(s, cat)
            rng.shuffle(titles)
            taken = 0
            for f in commons_files(s, titles[:per_item * 3]):
                rows = model_rows(f, answer, phrase, group)
                if not rows or taken >= per_item:
                    continue
                items.append((file_name(f"{key}-{item}", f["title"].split(":", 1)[-1].rsplit(".", 1)[0]),
                              f["url"], rows))
                taken += 1
            found += taken
        say(f"  Commons {group}: {found} free pictures")
    return finish(key, items, limit, workers=2, pause=0.5)


def build_commons_military(limit):
    """The commons_military pack (see the module docstring)."""
    return build_commons_models("commons_military", WD_KINDS, (), limit)


def build_commons_airplanes(limit):
    """The commons_airplanes pack (see the module docstring): civil aircraft kinds, leaving out military ones."""
    return build_commons_models("commons_airplanes", WD_CIVIL_KINDS, WD_KINDS, limit)


# ----------------------------------------------------------------- Wikimedia Commons: uniformed services

# By-country categories: (the parent category, the pattern of its subcategories with the country, the question, how
# the answer starts). "{country}" is filled with the country as said in a sentence ("the UK").
SERVICE_BY_COUNTRY = [
    ("Police officers by country", r"^Police officers (?:of|in|from) (.+)$", ASK_UNIFORM, "Police uniform of {country}"),
    ("Firefighters by country", r"^Firefighters (?:of|in|from) (.+)$", ASK_UNIFORM,
     "Firefighter's uniform of {country}"),
    ("Paramedics by country", r"^Paramedics (?:of|in|from) (.+)$", ASK_UNIFORM, "Paramedic's uniform of {country}"),
    ("Military police by country", r"^Military police (?:of|in) (.+)$", ASK_UNIFORM,
     "Military police uniform of {country}"),
    ("Park rangers by country", r"^Park rangers (?:of|in|from) (.+)$", ASK_UNIFORM, "Park ranger's uniform of {country}"),
    ("Nurses by country", r"^Nurses (?:of|in|from) (.+)$", ASK_UNIFORM, "Nurse's uniform of {country}"),
    ("Postal workers by country", r"^Postal workers (?:of|in|from) (.+)$", ASK_UNIFORM,
     "Postal worker's uniform of {country}"),
    ("Border guards by country", r"^Border guards (?:of|in|from) (.+)$", ASK_UNIFORM,
     "Border guard's uniform of {country}"),
    ("Military uniforms by country", r"^Military uniforms (?:of|in) (.+)$", ASK_UNIFORM, "Military uniform of {country}"),
    ("Police vehicles by country", r"^Police vehicles (?:of|in) (.+)$", ASK_WHAT, "This is a police vehicle in {country}"),
    ("Fire engines by country", r"^Fire engines (?:of|in) (.+)$", ASK_WHAT, "This is a fire engine in {country}"),
    ("Ambulances by country", r"^Ambulances (?:of|in) (.+)$", ASK_WHAT, "This is an ambulance in {country}"),
    ("Coast guards by country", r"^(?:Coast guard|Coastguard)s? (?:of|in) (.+)$", ASK_SERVICE,
     "The coast guard of {country}"),
]
# Single categories: (category, question, answer start).
SERVICE_FIXED = [
    ("King's Guard", ASK_UNIFORM, "The uniform of the King's Guard of the UK, the British Army's guard at the royal "
                                  "palaces in London"),
    ("Pontifical Swiss Guard", ASK_UNIFORM, "The uniform of the Pontifical Swiss Guard, the Pope's guard in the "
                                            "Vatican"),
    ("Evzones", ASK_UNIFORM, "The uniform of the Evzones, the Presidential Guard of Greece"),
    ("Prison guards", ASK_UNIFORM, "A prison officer's uniform"),
    ("Customs officers", ASK_UNIFORM, "A customs officer's uniform"),
    ("Mail carriers", ASK_UNIFORM, "A mail carrier's uniform"),
    ("Traffic police", ASK_UNIFORM, "A traffic police officer's uniform"),
    ("Paramedics", ASK_UNIFORM, "A paramedic's uniform"),
]
# Subcategories that are not people in that service's uniform at work (fiction, statues, memorials, the dead).
NOT_IN_SERVICE = re.compile(r"\b(fictional|cosplay\w*|statues?|sculptures?|monuments?|memorials?|graves?|funerals?|"
                            r"killed|in art|paintings?|drawings?|toys?|models?|logos?|insignia|badges?|stamps?|"
                            r"female|male|by name|people associated|in the line of duty)\b", re.I)


def country_words(name):
    """A category's country as said in a sentence ("the United Kingdom" -> "the UK", "Georgia (country)" ->
    "Georgia", "the Soviet Union" -> "the Soviet Union"); "" when it is not a country or former state."""
    name = re.sub(r"\s*\((country|state)\)$", "", clean(name)).strip()
    bare = re.sub(r"^the\s+", "", name, flags=re.I)
    known = country_named(bare)
    if known:
        return place_words(known)
    if re.match(r"^(Soviet Union|Confederate States|German Empire|Russian Empire|Ottoman Empire|Austria-Hungary|"
                r"Czechoslovakia|Yugoslavia|East Germany|West Germany|Empire of Japan|Kingdom of \w+)$", bare):
        return ("the " if name.lower().startswith("the ") or bare.startswith(("Soviet", "Confederate", "German E",
                                                                              "Russian E", "Ottoman", "Empire",
                                                                              "Kingdom")) else "") + bare
    return ""


def service_categories(s):
    """[(category, question, answer start)] of the by-country subcategories (SERVICE_BY_COUNTRY) and the single
    categories (SERVICE_FIXED)."""
    out = []
    for parent, pattern, question, start in SERVICE_BY_COUNTRY:
        try:
            subcats = [c.split(":", 1)[-1] for c in commons_members(s, parent, "subcat")]
        except RuntimeError:
            continue
        for sub in subcats:
            m = re.match(pattern, sub)
            country = country_words(m.group(1)) if m else ""
            if country:
                out.append((sub, question, start.format(country=country)))
    return out + list(SERVICE_FIXED)


def uniform_rows(f, question, start):
    """The rows of one Commons file of a uniformed service: the category's question (a uniform answer with the
    photo's era and the details its words name), its caption, and "Where and when ..."; [] when its words must be
    left out."""
    keep, extra = safety([f["caption"], f["title"], f["cats"]])
    if not keep:
        return []
    answer = start
    if question == ASK_UNIFORM:
        era = era_words(f["year"])
        details = details_in(f["caption"], f["title"].split(":", 1)[-1], f["cats"])
        answer += (f", photographed {era}" if era else "") + (f", with {details}" if details else "")
    rows = [{"question": question, "answer": full_stop(answer), "credit": f["credit"], **where(f["place"]), **extra}]
    if f["caption"]:
        rows.append({"question": ASK_DESCRIBE, "answer": f["caption"], "credit": f["credit"], **where(f["place"]),
                     **extra})
    row = where_when_row(f["place"], f"in {f['year']}" if f["year"] else "", conflict_in(f["caption"]),
                         f["credit"], extra)
    if row:
        rows.append(row)
    return rows


def build_commons_uniformed(limit):
    """The commons_uniformed pack (see the module docstring): free files of each service category and of up to
    four of its subcategories (by region or city), the categories sharing the pack."""
    s = session()
    categories = service_categories(s)
    say(f"  Commons uniformed services: {len(categories)} categories")
    rng = random.Random(83)
    rng.shuffle(categories)
    per_category = max(3, int(limit * 1.3 / max(1, len(categories))) + 1)
    items, seen = [], set()
    for category, question, start in categories:
        try:
            titles = commons_members(s, category, "file")
            subs = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
            for sub in [c for c in subs if not NOT_IN_SERVICE.search(c)][:4]:
                titles += commons_members(s, sub, "file")
        except RuntimeError:
            continue
        titles = [t for t in dict.fromkeys(titles) if t not in seen and not NOT_IN_SERVICE.search(t)]
        rng.shuffle(titles)
        found = 0
        for f in commons_files(s, titles[:per_category * 3]):
            rows = uniform_rows(f, question, start)
            if not rows or found >= per_category:
                continue
            seen.add(f["title"])
            items.append((file_name("commons-uniformed", f["title"].split(":", 1)[-1].rsplit(".", 1)[0]), f["url"],
                          rows))
            found += 1
        if len(items) >= limit * 1.3:
            break
    say(f"  Commons uniformed services: {len(items)} free pictures")
    return finish("commons_uniformed", items, limit, workers=2, pause=0.5)


# ----------------------------------------------------------------- Library of Congress

# (search address, extra parameters, number of records, name in the credit, conflict, uniform answer start or None)
LOC_SERVICE_SETS = [
    ("collections/civil-war-glass-negatives/", {}, 8700, "Civil War Glass Negatives and Related Prints",
     "the American Civil War", "Military uniform of {country}"),
    ("photos/", {"q": "world war", "fa": "partof:bain collection"}, 2232, "George Grantham Bain Collection", "",
     None),
    ("photos/", {"q": "soldiers", "fa": "partof:bain collection"}, 735, "George Grantham Bain Collection", "", None),
    ("photos/", {"fa": "subject:tanks (military science)|online-format:image"}, 231, "", "", None),
    ("photos/", {"fa": "subject:warships|online-format:image"}, 290, "", "", None),
    ("photos/", {"fa": "subject:military uniforms|online-format:image"}, 7345, "", "",
     "Military uniform of {country}"),
    ("photos/", {"fa": "subject:police|online-format:image"}, 842, "", "", "Police uniform of {country}"),
    ("photos/", {"fa": "subject:fire fighters|online-format:image"}, 282, "", "", "Firefighter's uniform of {country}"),
    ("photos/", {"fa": "subject:fire engines|online-format:image"}, 70, "", "", None),
    ("photos/", {"fa": "subject:nurses|online-format:image"}, 622, "", "", "Nurse's uniform of {country}"),
    ("photos/", {"fa": "subject:postal service employees|online-format:image"}, 43, "", "",
     "Postal worker's uniform of {country}"),
]
LOC_NOT_A_PHOTO = re.compile(r"\b(map|maps|plan|plans|drawing|diagram|title card|caption card|untitled|poster|"
                             r"cartoon|sheet music|letter|envelope|broadside|certificate|membership|advertisement|"
                             r"print|lithograph|engraving|illustration)\b", re.I)


def loc_service_items(s, path, extra, total, name, conflict, uniform, want, rng):
    """[(name, picture address, rows)] from random result pages of one Library of Congress set, a few from each
    page and each title once: the title as "Describe this picture.", "Where and when ..." from the record, and,
    for sets of people in uniform, the uniform with the country and date of the record. The Library asks programs
    to keep to about one search page a second."""
    pages = list(range(1, max(2, total // 100 + 1) + 1))
    rng.shuffle(pages)
    items, answers = [], set()
    per_page = max(3, want // 15)
    for page in pages[:40]:
        time.sleep(2)
        data = get_json(s, LOC + path, {"fo": "json", "c": 100, "sp": page, "at": "results", **extra}, pause=15)
        taken = 0
        for record in (data or {}).get("results") or []:
            title = clean(record.get("title"))
            answer = tidy(title)
            picture = loc_picture(record)
            item = record.get("item") or {}
            summary = clean(item.get("summary"))
            subjects = " ".join(record.get("subject") or [])
            keep, safe = safety([title, summary])
            if not keep or not loc_free(record) or not picture or not usable(answer) or LOC_NOT_A_PHOTO.search(title) \
                    or answer in answers or taken >= per_page:
                continue
            answers.add(answer)
            taken += 1
            link = re.sub(r"^(https?:)?//", "https://", item.get("link") or record.get("id") or "")
            collection = name or next((clean(p) for p in record.get("partof") or [] if "collection" in str(p).lower()),
                                      "Prints and Photographs Division")
            credit = (f"{title[:150]}, {collection}, Library of Congress, no known restrictions on publication, "
                      f"{link}")
            place = loc_place(record)
            when = when_words(item.get("date") or item.get("created_published_date") or "")
            said_conflict = conflict or conflict_in(subjects, title)
            rows = [{"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **where(place), **safe}]
            row = where_when_row(place, when, said_conflict, credit, safe)
            if row:
                rows.append(row)
            country = place.split(",")[-1].strip() if place else ""
            if uniform and country:
                details = details_in(title, summary)
                said = uniform.format(country=place_words(country)) + (f", photographed {when}" if when else "") \
                    + (f", with {details}" if details else "")
                rows.insert(0, {"question": ASK_UNIFORM, "answer": full_stop(said), "credit": credit, **where(place),
                                **safe})
            control = re.sub(r"\W", "", str(item.get("control_number") or item.get("id") or len(items)))
            items.append((f"loc-service-{control}.jpg", picture, rows))
        if len(items) >= want:
            break
    say(f"  {name or extra.get('fa', path)}: {len(items)} usable records")
    return items


def build_loc_service(limit):
    """The loc_service pack (see the module docstring): each set in proportion to its size, at least a twentieth
    of the pack each (or all of a smaller set)."""
    s, rng, items = session(), random.Random(81), []
    total = sum(n for _, _, n, _, _, _ in LOC_SERVICE_SETS)
    for path, extra, n, name, conflict, uniform in LOC_SERVICE_SETS:
        share = max(0.05, n / total)
        items += loc_service_items(s, path, extra, n, name, conflict, uniform, int(limit * share * 1.3) + 3, rng)
    return finish("loc_service", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- US National Archives

# (series catalogue id, online items, name in the credit, largest picture in bytes)
NARA_MILITARY_SERIES = [
    (520587, 1700, "General Photographic Files, General Records of the Department of the Navy (80-G)", 8_000_000),
    (532396, 700, "General Photograph File of the U.S. Marine Corps, Records of the U.S. Marine Corps (127)",
     8_000_000),
    (513164, 6700, "Photographs of Activities, Facilities, and Personalities, Records of the U.S. Coast Guard (26-G)",
     8_000_000),
    (530707, 100000, "Photographs of American Military Activities, Records of the Office of the Chief Signal Officer "
                     "(111-SC)", 25_000_000),
]


def nara_small_picture(record, most):
    """The address of a record's JPEG or GIF of at most most bytes, or ""."""
    best, best_size = "", most + 1
    for obj in record.get("digitalObjects") or []:
        kind, url, size = obj.get("objectType") or "", obj.get("objectUrl") or "", int(obj.get("objectFileSize") or 0)
        if url and 0 < size < best_size and ("JPG" in kind or "JPEG" in kind or "GIF" in kind):
            best, best_size = url, size
    return best or (nara_picture(record) if most <= 4_000_000 else "")


def nara_text(record):
    """(caption, place words) of a NARA record: the full caption in its scope note when it has one, otherwise the
    title, without file notes, in sentence case when typed in capitals."""
    title, note = clean(record.get("title")), clean(record.get("scopeAndContentNote"))
    text = WRA_FULL.sub("", note) if len(note.split()) > len(title.split()) and len(note.split()) < 120 else title
    text = re.sub(r"\s*--\s*", ", ", NARA_NOTES.sub("", text)).strip(" .")
    text = re.sub(r"^\s*(original caption|caption|photograph of)\s*:?\s*", "", text, flags=re.I)
    text = re.sub(r"\b(Taken by|Alt\.|F\. ?L\.)\s*:?[^.]*\.\s*", "", text)          # camera notes of aerial photos
    places = [clean(x.get("heading")) for x in record.get("subjects") or []
              if x.get("authorityType") == "geographicPlaceName"]
    return sentence_case(text, places), places


def nara_military_items(s, naid, total, name, most, want, rng):
    """[(name, picture address, rows)] from random result pages of one NARA series (the search reaches its first
    10,000 records): the caption, and "Where and when ..." from the record's place headings, production date and
    the conflict the caption names."""
    pages = list(range(1, max(2, min(total, 10000) // 100) + 1))
    rng.shuffle(pages)
    items, answers = [], set()
    per_page = max(3, want // 15)
    for page in pages[:40]:
        time.sleep(1)
        data = get_json(s, NARA_SEARCH, {"ancestorNaId": naid, "availableOnline": "true", "limit": 100,
                                         "page": page}, pause=10)
        hits = (((data or {}).get("body") or {}).get("hits") or {}).get("hits") or []
        taken = 0
        for hit in hits:
            record = (hit.get("_source") or {}).get("record") or {}
            if (record.get("useRestriction") or {}).get("status") != "Unrestricted" or taken >= per_page:
                continue
            caption, places = nara_text(record)
            answer = tidy(capped_words(caption, 80))
            picture = nara_small_picture(record, most)
            keep, safe = safety([caption])
            if not keep or not picture or not usable(answer) or answer in answers:
                continue
            answers.add(answer)
            taken += 1
            place = next((p for p in map(lc_place, places) if p), "")
            years = [str(d.get("year")) for d in record.get("productionDates") or [] if d.get("year")]
            when = f"in {years[0]}" if years else ""
            credit = (f"{clean(record.get('title'))[:150]}, {name}, U.S. National Archives and Records "
                      f"Administration, public domain (US government work), {NARA}id/{record.get('naId')}")
            rows = [{"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **where(place), **safe}]
            row = where_when_row(place, when, conflict_in(caption), credit, safe)
            if row:
                rows.append(row)
            items.append((f"nara-mil-{record.get('naId')}.jpg", picture, rows))
        if len(items) >= want:
            break
    say(f"  NARA {name.rsplit('(', 1)[-1].rstrip(')')}: {len(items)} usable records")
    return items


def build_nara_military(limit):
    """The nara_military pack (see the module docstring): a quarter of the pack from each series (or all of a
    smaller one)."""
    s, rng, items = session(), random.Random(82), []
    for naid, n, name, most in NARA_MILITARY_SERIES:
        items += nara_military_items(s, naid, n, name, most, int(limit * 0.25 * 1.3) + 3, rng)
    return finish("nara_military", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- U.S. Army photos (army.mil)

ARMY = "https://www.army.mil/photos"
MONTHS = r"(Jan|Feb|March|April|May|June|July|Aug|Sept?|Oct|Nov|Dec)\w*\.?"


def build_army_mil(limit):
    """The army_mil pack: the photos on www.army.mil/photos (the Army's latest, about 250), each with its full
    caption as "Describe this picture." and the date its caption gives as "Where and when ..." (the place is in the
    caption itself, not in a field, so it is not repeated)."""
    import html as html_lib
    s = session()
    try:
        page = s.get(ARMY, timeout=60).text
    except Exception:  # noqa: BLE001 - nothing to read
        return []
    items, seen = [], set()
    for tag in re.findall(r"<img [^>]*data-full-desc=[^>]*>", page):
        attrs = {k: html_lib.unescape(html_lib.unescape(v)) for k, v in re.findall(r'([\w-]+)="([^"]*)"', tag)}
        url = attrs.get("src", "")
        if not url.startswith("https://api.army.mil/") or url in seen:
            continue
        seen.add(url)
        answer = tidy(capped_words(attrs.get("data-full-desc", ""), 90))
        keep, safe = safety([answer])
        if not keep or not usable(answer):
            continue
        who = clean(attrs.get("data-author")) or "U.S. Army"
        credit = (f"{clean(attrs.get('data-title'))}, {who}, U.S. Army, public domain (US government work), "
                  f"{ARMY}")
        rows = [{"question": ASK_DESCRIBE, "answer": answer, "credit": credit, **safe}]
        m = re.search(MONTHS + r"\s+\d{1,2},\s+(\d{4})", answer)
        if m:
            rows.append({"question": ASK_WHERE_WHEN, "answer": f"It was taken on {m.group(0)}.", "credit": credit,
                         **safe})
        items.append((f"army-mil-{url.split('/images/', 1)[-1].rsplit('/', 1)[0].replace('/', '-')}.jpg",
                      url.rsplit("/", 1)[0] + "/original.jpg", rows))
    say(f"army.mil: {len(items)} photos")
    return finish("army_mil", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- Smithsonian (NASM and NMAH)

NASM_AIRCRAFT = {"Aircraft", "Rotorcraft", "Jet aircraft", "Baloons (aircraft)", "Gliders"}
NASM_UNIFORMS = {"Clothing", "Protective wear", "Helmets", "Headgear", "Insignias", "Medals", "Awards", "Handwear",
                 "Costume accessories", "Uniforms"}
NASM_KINDS = [("Fighters", "fighter aircraft"), ("Bombers", "bomber"), ("Commercial", "airliner (a passenger airplane)"),
              ("Vertical Flight", "helicopter"), ("Gliders", "glider"), ("Homebuilt", "home-built airplane"),
              ("Private", "private airplane"), ("Military", "military aircraft")]
NASM_CONFLICTS = [("World War I", "the First World War"), ("World War II", "the Second World War"),
                  ("Korean War", "the Korean War"), ("Vietnam War", "the Vietnam War"), ("Cold War", "the Cold War")]
NASM_NOT_WHOLE = re.compile(r"^(parts?|components?|fragment|section|model|wing|fuselage|engine)\b|,\s*(parts?|"
                            r"fragment)\b", re.I)
# NMAH topics and collections about the forces and the uniformed services.
NMAH_SERVICE = re.compile(r"armed forces|military|civil war|world war|korean war|vietnam|revolution|uniforms?|"
                          r"insignia|medals?|decorations|firefight\w*|fire fighting|fire department|law enforcement|"
                          r"police|coast guard|postal|nursing|nurses|arms and armor|edged weapons|firearms", re.I)
NMAH_NOT_OBJECT = re.compile(r"patent|sheet|newspaper|clipping|manuscript|letter|book|document|lithograph|print|"
                             r"sketch|drawing|photograph|negative|card|certificate|map|sheet music|ticket|label", re.I)


def si_country_adjective(country):
    """An adjective for a Smithsonian record's country ("France" -> "French"), from the Wikidata table's common
    countries, or ""."""
    names = {"USA": "US", "UK": "British", "France": "French", "Germany": "German", "Japan": "Japanese",
             "Italy": "Italian", "Russia": "Russian", "Canada": "Canadian", "Netherlands": "Dutch",
             "Sweden": "Swedish", "Switzerland": "Swiss", "Australia": "Australian", "Spain": "Spanish",
             "Poland": "Polish", "Czechia": "Czech", "Austria": "Austrian", "Belgium": "Belgian", "China": "Chinese"}
    return names.get(country, "")


def si_media(content, most=3):
    """The addresses of up to most CC0 pictures of a Smithsonian record (at most 2,048 pixels)."""
    media = (content.get("descriptiveNonRepeating", {}).get("online_media") or {}).get("media", [])
    return [m["content"] + "&max=2048" for m in media if (m.get("usage") or {}).get("access") == "CC0"
            and m.get("type") == "Images" and m.get("content")][:most]


def si_notes(content, labels):
    """The record's notes with one of labels, joined, tidied."""
    return " ".join(clean(n.get("content")) for n in content.get("freetext", {}).get("notes") or []
                    if n.get("label") in labels)


def nasm_rows(record):
    """(picture addresses, rows) of a NASM aircraft or flight-clothing record with CC0 pictures, or None."""
    content = record.get("content", {})
    idx = content.get("indexedStructured", {})
    kinds, flags = set(idx.get("object_type") or []), idx.get("usage_flag") or []
    pictures = si_media(content)
    title = clean(record.get("title"))
    if not pictures or not title or "Models" in kinds or "Certificates" in kinds \
            or re.match(r"^(license|licence|certificate|card|letter)\b", title, re.I):
        return None
    aircraft = bool(kinds & NASM_AIRCRAFT) and not NASM_NOT_WHOLE.search(title) and "Components (objects)" not in kinds
    uniform = bool(kinds & NASM_UNIFORMS) or "Uniforms" in flags
    if not aircraft and not uniform:
        return None
    looks = tidy(first_sentences(si_notes(content, ("Physical Description",)), 70))
    summary = first_sentences(si_notes(content, ("Summary",)), 90)
    keep, safe = safety([title, looks, summary])
    if not keep:
        return None
    countries = [g["L2"]["content"] for g in idx.get("geoLocation") or [] if (g.get("L2") or {}).get("type") == "Country"]
    country = country_named(countries[0]) if countries else ""
    dates = [clean(d.get("content")) for d in content.get("freetext", {}).get("date") or []]
    makers = [clean(n.get("content")) for n in content.get("freetext", {}).get("name") or []
              if n.get("label") == "Manufacturer"]
    link = content.get("descriptiveNonRepeating", {}).get("record_link") or record.get("id", "")
    credit = f"{title}, National Air and Space Museum, Smithsonian Institution, CC0, {link}"
    rows = []
    if aircraft:
        kind = next((said for flag, said in NASM_KINDS if flag in flags), "aircraft")
        if "Rotorcraft" in kinds and kind == "aircraft":
            kind = "helicopter"
        described = f"{si_country_adjective(country)} {kind}".strip()
        wars = [said for flag, said in NASM_CONFLICTS if flag in flags]
        answer = f"This is the {title}, {a_or_an(described)} {described}" + (f" of {' and '.join(wars)}" if wars else "")
        if dates and re.search(r"\d{4}", dates[0]):
            answer += f", made {when_words(dates[0])}"
        if makers and makers[0].lower() != "unknown":
            answer += f" by {makers[0]}"
        rows.append({"question": ASK_WHAT, "answer": full_stop(answer), "credit": credit, **safe})
    if usable(looks):
        rows.append({"question": ASK_DESCRIBE, "answer": looks, "credit": credit, **safe})
    if len(summary.split()) >= 12:
        rows.append({"question": MUSEUM, "answer": full_stop(f"{title}. {summary}" if title.lower() not in
                                                             summary.lower() else summary), "credit": credit, **safe})
    if not rows:
        return None
    place = where(country, "origin")
    return pictures, [dict(r, **place) for r in rows]


def build_nasm_aircraft(limit):
    """The nasm_aircraft pack: every NASM open-access record (about 1,000 with CC0 pictures, in the Smithsonian's
    bulk files) that is a whole aircraft or flight clothing, insignia or a medal, up to three pictures each."""
    s, items = session(), []
    for key in si_keys("nasm"):
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=120).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            got = nasm_rows(record)
            if got:
                pictures, rows = got
                for n, url in enumerate(pictures):
                    items.append((file_name("nasm", f"{record.get('id', len(items))}-{n}"), url, rows))
    say(f"NASM: {len(items)} pictures of aircraft and flight clothing")
    return finish("nasm_aircraft", items, limit, workers=4, pause=0.1)


def nmah_rows(record):
    """(picture addresses, rows) of an NMAH record with CC0 pictures about the forces or the uniformed services,
    or None: "Tell me about this museum object." with its description, and "When was this made?" when it says."""
    content = record.get("content", {})
    pictures = si_media(content, 2)
    if not pictures:
        return None
    free = content.get("freetext", {})
    topics = " ".join(clean(t.get("content")) for k in ("topic", "setName") for t in free.get(k) or [])
    kind = " ".join(clean(t.get("content")) for t in free.get("objectType") or [])
    title = clean(record.get("title"))
    if not NMAH_SERVICE.search(topics) or NMAH_NOT_OBJECT.search(kind) or not title:
        return None
    text = first_sentences(si_notes(content, ("Description", "Description (Brief)", "General History")), 90)
    text = re.sub(r"\b(Physical Description|General History|Description \(Brief\)|Specifications|Markings)\b:?\s*",
                  "", text).strip()
    text = text.replace("â\x80\x99", "’").replace("â\x80\x9c", "“").replace("â\x80\x9d", "”")
    keep, safe = safety([title, text])
    if not keep or len(text.split()) < 12:
        return None
    link = content.get("descriptiveNonRepeating", {}).get("record_link") or record.get("id", "")
    credit = f"{title}, National Museum of American History, Smithsonian Institution, CC0, {link}"
    answer = full_stop(text if title.lower() in text.lower() else f"{title}. {text}")
    places = {clean(p.get("label")).lower(): p.get("content") for p in free.get("place") or []}
    place = place_from_text(places.get("place made") or places.get("place used") or "")
    rows = [{"question": MUSEUM, "answer": answer, "credit": credit, **safe}]
    made = next((clean(d.get("content")) for d in free.get("date") or [] if "made" in clean(d.get("label")).lower()),
                "")
    when = when_words(made)
    if when:
        rows.append({"question": "When was this made?", "answer": f"It was made {when}.", "credit": credit, **safe})
    kind_place = "origin" if "place made" in places else None
    return pictures, [dict(r, **where(place, kind_place)) for r in rows]


def build_nmah_service(limit):
    """The nmah_service pack: NMAH's bulk files (about 2.5 GB, read one file at a time in random order) until
    enough records about the forces and the uniformed services with CC0 pictures are found."""
    s, items = session(), []
    keys = si_keys("nmah")
    random.Random(84).shuffle(keys)
    for key in keys:
        if len(items) >= limit * 1.3:
            break
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=300).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            got = nmah_rows(record)
            if got:
                pictures, rows = got
                for n, url in enumerate(pictures):
                    items.append((file_name("nmah", f"{record.get('id', len(items))}-{n}"), url, rows))
    say(f"NMAH: {len(items)} pictures of service objects")
    return finish("nmah_service", items, limit, workers=4, pause=0.1)


# ----------------------------------------------------------------- the packs

LOC_TERMS = "https://www.loc.gov/legal/ (Prints and Photographs Division rights statements)"

SERVICE_PACKS = {
    "commons_military": (build_commons_military,
                         "Wikimedia Commons categories of military models, named ships and decorations, found through "
                         "Wikidata (facts CC0, https://www.wikidata.org/wiki/Wikidata:Licensing): captions CC0; "
                         "pictures CC0, public domain or CC BY, each with its author and file page below. "
                         "https://commons.wikimedia.org"),
    "commons_airplanes": (build_commons_airplanes,
                          "Wikimedia Commons categories of civil aircraft models, found through Wikidata (CC0): "
                          "captions CC0; pictures CC0, public domain or CC BY, each with its author below. "
                          "https://commons.wikimedia.org"),
    "commons_uniformed": (build_commons_uniformed,
                          "Wikimedia Commons categories of police, fire, ambulance, rangers, nurses, postal, border, "
                          "military and ceremonial uniforms and service vehicles by country: captions CC0; pictures "
                          "CC0, public domain or CC BY, each with its author below. https://commons.wikimedia.org"),
    "loc_service": (build_loc_service,
                    "Library of Congress, Prints and Photographs Division (Civil War glass negatives and photos by "
                    "subject), https://www.loc.gov/pictures/ : 'No known restrictions on publication'. Titles, places "
                    f"and dates from the Library's records. {LOC_TERMS}"),
    "nara_military": (build_nara_military,
                      "U.S. National Archives and Records Administration, https://catalog.archives.gov : photo series "
                      "80-G, 127, 26-G and 111-SC. US government work, public domain; only records marked "
                      "'Unrestricted'. Captions from the Archives' records."),
    "army_mil": (build_army_mil,
                 "U.S. Army, https://www.army.mil/photos : photos by U.S. Army photographers, US government work, "
                 "public domain (https://www.army.mil/privacy), each with its photographer below."),
    "nasm_aircraft": (build_nasm_aircraft,
                      "Smithsonian National Air and Space Museum, Smithsonian Open Access, CC0. "
                      "https://www.si.edu/openaccess (records and pictures)."),
    "nmah_service": (build_nmah_service,
                     "Smithsonian National Museum of American History, Smithsonian Open Access, CC0 pictures and "
                     "records only. https://www.si.edu/openaccess"),
}

# How many pictures a full build takes from each collection.
SERVICE_LIMITS = {
    "commons_military": 6000,         # a few files each of about 8,000 Wikidata items with a Commons category
    "commons_airplanes": 2500,        # civil aircraft models with a Commons category and facts
    "commons_uniformed": 4000,        # about 600 service categories by country, a few files each
    "loc_service": 4000,              # Civil War negatives (8,700), Bain (3,000) and about 9,000 photos by subject
    "nara_military": 3000,            # 80-G, 127 and 26-G (small files) and 111-SC (large files)
    "army_mil": 250,                  # all the Army's current gallery
    "nasm_aircraft": 1200,            # all usable: about 250 records, up to three pictures each
    "nmah_service": 1500,             # CC0 records about the forces and services (about 1 in 100 records is CC0)
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one service pack builder.")
    parser.add_argument("key", choices=sorted(SERVICE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--rows", type=int, default=0, help="print only this many rows (0: all)")
    args = parser.parse_args(argv)
    entries = SERVICE_PACKS[args.key][0](args.limit)
    for name, data, row in entries[:args.rows or None]:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('content') == 'graphic')} graphic rows, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
