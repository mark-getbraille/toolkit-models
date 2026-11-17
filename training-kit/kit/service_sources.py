"""Military equipment and uniformed-services picture collections for the Picture Model Training Kit that cannot be
ready-made packs because of their licence (share-alike). The open ones (Wikimedia Commons CC0/PD/CC BY files of
military models, civil aircraft and uniformed services found through Wikidata, the Library of Congress, the US
National Archives, army.mil, and the Smithsonian's Air and Space and American History museums) are packs in
packs/service_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py): every collection here is "share-alike" (used only with the share-alike
choice).

What the answers say: as in packs/service_packs.py, every fact comes from the source's record or from Wikidata (CC0):
"This is an M4 Sherman, a US medium tank of the Second World War, in service from 1942 to 1957." (Wikidata: P495
country of origin, P17 country, P137 operator, P729 and P730 years in service, P571 inception, P607 conflicts),
"Police uniform of the UK, photographed in 2014, with a high-visibility jacket" (the Commons category, the file's
date and the details its words name), the caption as "Describe this picture." and "Where and when was this photo
taken?" from the record's date (the kit has no offline map of countries, so Commons camera coordinates are not
turned into a place here; the open packs do that on the building machine).

Safety:
  - Weapons are named and described as objects; captions that read like instructions are not learnt from.
  - War pictures of the dead, wounds or injuries are kept, described plainly from the record and marked
    "content": "graphic" (the kit uses those rows only when graphic content is chosen). Left out altogether:
    anything naming sexual violence, executions or torture, and pictures whose words put a dead or injured child at
    their centre. Captions with old slurs are not repeated.
  - Rows whose words name a child carry "child": true.
  - SERVICE_PICTURE_MAKING_OK holds only commons_military_sa: vehicles, aircraft and ships, with files whose words
    name people (crews, soldiers, portraits) left out. Never weapons, never people.

The collections (SERVICE_SOURCES), all share-alike:
  commons_military_sa    Wikimedia Commons files under CC BY-SA or GFDL in the categories of military vehicles,
                         artillery, aircraft, helicopters, warships and submarines that Wikidata links to models
                         (files naming people left out).
  commons_weapons_sa     The same for small arms, swords, armour and military decorations.
  commons_airplanes_sa   The same for civil aircraft (airliners, business jets, light aircraft ...), said as airplanes.
  commons_uniformed_sa   Wikimedia Commons files under CC BY-SA or GFDL of police officers, firefighters, paramedics,
                         military police, park rangers, nurses, postal workers, border guards, military uniforms,
                         ceremonial guards, police cars, fire engines, ambulances and coast guards by country.
  bundesarchiv_sa        German Federal Archives (Bundesarchiv) photos given to Wikimedia Commons under CC BY-SA 3.0
                         de: soldiers, vehicles, aircraft, ships, police and fire brigades, 1900s-1990s, with the
                         Archive's caption where it is in English.
  europeana_1914_1918    Europeana 1914-1918: about 5,000 photos and documents from family collections across Europe
                         (soldiers, uniforms, the front, everyday life in the First World War), CC BY-SA 3.0, with the
                         English descriptions.

Already in the kit or the packs, so not repeated here: Commons CC0/PD/CC BY files of the same categories, the
Library of Congress, NARA, army.mil and Smithsonian packs (packs/service_packs.py), the Australian War Memorial and
Nationaal Archief packs (packs/archive_packs.py), and NASA's pictures (sources.py "nasa").

Needing sign-up (cannot be downloaded automatically; get them yourself, then put the pictures in the own-pictures
folder with your own descriptions, as the user guide says): SERVICE_SIGN_UP.

Looked at and not included: SERVICE_NOT_INCLUDED.

    python kit/service_sources.py europeana_1914_1918 --cap 8      (a quick check into an empty folder)
"""

import os
import random
import re
import time

import sources
from extra_sources import COMMONS_SA, commons_get, commons_members, commons_session, per_label
from more_sources import fetch_shared, sentence
from personal_sources import CHILD_WORDS, first_sentences
from sources import NARRATE, Source, clean

ASK_WHAT = "What is this?"
ASK_UNIFORM = "What uniform is this person wearing?"
ASK_SERVICE = "What service is this?"
ASK_WHERE_WHEN = "Where and when was this photo taken?"
WDQS = "https://query.wikidata.org/sparql"
EUROPEANA = "https://api.europeana.eu/record/v2/search.json"
EUROPEANA_KEY = "api2demo"        # Europeana's public test key; set EUROPEANA_KEY to your own if it is refused

# The same safety words as packs/service_packs.py.
GRAPHIC = re.compile(r"\b(dead|corpses?|bod(y|ies) of|killed|wounded|wounds?|casualt\w*|injur\w*|bloody|blood|"
                     r"massacre\w*|atrocit\w*|skeletons?|remains of (the )?(dead|soldiers?|victims?)|slain|"
                     r"mortally|amputat\w*|burned bodies|charred|mass graves?|dying|fallen soldiers?|"
                     r"tote|toten|gefallene\w*|verwundete\w*|leichen?)\b", re.I)
NOT_SHOWN_WAR = re.compile(r"\b(rap(e|ed|es|ing)|sexual(ly)? (assault|violence|abuse)\w*|molest\w*|execut(ion|ions|ed|"
                           r"ing)|firing squad|beheading|beheaded|hang(ed|ing) of|being hanged|lynch\w*|tortur\w*|"
                           r"hinrichtung\w*|erschie(ss|ß)ung\w*|nud\w*|naked|topless|porn\w*|erotic\w*)\b", re.I)
SLURS = re.compile(r"\b(japs?|nips?|niggers?|negroes|coloreds?|squaws?|redskins?|krauts?|huns)\b", re.I)
HOW_TO = re.compile(r"\b(how to|step[- ]by[- ]step|instructions?|disassembl\w*|field[- ]strip\w*|reassembl\w*|"
                    r"manual of arms)\b", re.I)
NOT_A_CHILD = re.compile(r"\b(infantr\w*|infante\w*|sons of [A-Z]\w+|boys? (scouts?|brigade)|ship'?s boys?)\b", re.I)
# Words for people: files naming them are left out of commons_military_sa, so it can feed picture-making.
PEOPLE = re.compile(r"\b(people|persons?|man|men|woman|women|soldiers?|sailors?|airmen|airman|marines?|pilots?|"
                    r"crews?|crewmen|officers?|troops?|personnel|portrait\w*|visitors?|children|child|boys?|girls?|"
                    r"family|families|veterans?|general|admiral|captain|commander|president|king|queen|prince)\b",
                    re.I)
CONFLICTS = [(re.compile(r"world war,? 1914-1918|world war i\b|first world war|great war|wwi\b", re.I),
              "the First World War"),
             (re.compile(r"world war,? 1939-1945|world war ii\b|second world war|ww2|wwii", re.I),
              "the Second World War"),
             (re.compile(r"korean war", re.I), "the Korean War"), (re.compile(r"vietnam war", re.I), "the Vietnam War"),
             (re.compile(r"american civil war", re.I), "the American Civil War"),
             (re.compile(r"falklands war", re.I), "the Falklands War"), (re.compile(r"gulf war", re.I), "the Gulf War")]


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def safety(texts):
    """(keep, extra row fields) from a picture's words: keep is False for sexual violence, executions, torture,
    slurs, or a dead or injured child; extra marks "content": "graphic" and "child"."""
    text = " ".join(t for t in texts if t)
    if NOT_SHOWN_WAR.search(text) or SLURS.search(text):
        return False, {}
    graphic, child = bool(GRAPHIC.search(text)), bool(CHILD_WORDS.search(NOT_A_CHILD.sub(" ", text)))
    if graphic and child:
        return False, {}
    return True, {**({"content": "graphic"} if graphic else {}), **({"child": True} if child else {})}


def conflict_in(text):
    """The first conflict a caption names ("the Second World War"), or ""."""
    return next((said for pattern, said in CONFLICTS if pattern.search(text or "")), "")


def where_when(place, year, conflict, row):
    """The "Where and when was this photo taken?" twin of row, or None when the record gives neither."""
    if not place and not year:
        return None
    answer = "It was taken" + (f" in {sources.place_words(place)}" if place else "") + (f" in {year}" if year else "")
    answer += f", during {conflict}." if conflict else "."
    return dict(row, question=ASK_WHERE_WHEN, answer=answer, **sources.place_fields({"place": place}))


def caption_text(text, most=60):
    """A caption or description as an answer (6 words or more, first sentences, a full stop), or ""."""
    text = re.sub(r"^\s*English\s*:\s*", "", clean(text))
    text = re.sub(r"\{\{[^}]*\}\}|[\[\]]", "", text)
    text = first_sentences(text, most)
    if len(text.split()) < 6 or re.match(r"^[\d\W]", text) or re.search(r"\b[a-z]{2}:\S", text):
        return ""
    return sentence(text)


# ----------------------------------------------------------------- Wikidata (as packs/service_packs.py)

WD_KINDS = [
    ("Q920182", "main battle tank", "vehicle"), ("Q1069116", "medium tank", "vehicle"),
    ("Q771712", "heavy tank", "vehicle"), ("Q875583", "light tank", "vehicle"), ("Q161161", "tank destroyer", "vehicle"),
    ("Q12876", "tank", "vehicle"), ("Q202825", "infantry fighting vehicle", "vehicle"),
    ("Q4407246", "armoured personnel carrier", "vehicle"), ("Q649062", "armoured car", "vehicle"),
    ("Q2000908", "self-propelled gun", "vehicle"), ("Q506219", "multiple rocket launcher", "vehicle"),
    ("Q180126", "howitzer", "vehicle"), ("Q1330892", "field gun", "vehicle"), ("Q7325635", "anti-aircraft gun", "vehicle"),
    ("Q81103", "cannon", "vehicle"), ("Q6546105", "military light utility vehicle (a jeep)", "vehicle"),
    ("Q753058", "attack helicopter", "vehicle"), ("Q2735392", "utility helicopter", "vehicle"),
    ("Q1543102", "military helicopter", "vehicle"), ("Q385642", "fighter-bomber", "vehicle"),
    ("Q127771", "fighter aircraft", "vehicle"), ("Q170877", "bomber", "vehicle"),
    ("Q3041792", "reconnaissance aircraft", "vehicle"),
    ("Q17205", "aircraft carrier", "vehicle"), ("Q182531", "battleship", "vehicle"), ("Q104843", "cruiser", "vehicle"),
    ("Q174736", "destroyer", "vehicle"), ("Q161705", "frigate", "vehicle"), ("Q170013", "corvette", "vehicle"),
    ("Q2811", "submarine", "vehicle"), ("Q207452", "ship of the line", "vehicle"), ("Q324233", "torpedo boat", "vehicle"),
    ("Q214196", "gunboat", "vehicle"), ("Q202527", "minesweeper", "vehicle"), ("Q11479410", "patrol boat", "vehicle"),
    ("Q474748", "amphibious assault ship", "vehicle"),
    ("Q177456", "assault rifle", "weapon"), ("Q1194268", "battle rifle", "weapon"),
    ("Q190570", "sniper rifle", "weapon"), ("Q183302", "carbine", "weapon"), ("Q178550", "submachine gun", "weapon"),
    ("Q720711", "light machine gun", "weapon"), ("Q12800", "machine gun", "weapon"),
    ("Q3389302", "semi-automatic pistol", "weapon"), ("Q170382", "revolver", "weapon"), ("Q1907525", "pistol", "weapon"),
    ("Q486396", "shotgun", "weapon"), ("Q178243", "musket", "weapon"), ("Q124072", "rifle", "weapon"),
    ("Q12791", "sword", "weapon"), ("Q182780", "dagger", "weapon"), ("Q173366", "bayonet", "weapon"),
    ("Q3579211", "combat helmet", "weapon"), ("Q3391846", "suit of plate armour", "weapon"),
    ("Q1788716", "military decoration", "weapon"),
    # The general kinds last, so a ship or an aircraft is never called just a military vehicle.
    ("Q2031121", "warship", "vehicle"), ("Q216916", "military aircraft", "vehicle"),
    ("Q130368", "armoured fighting vehicle", "vehicle"), ("Q1184840", "military vehicle", "vehicle"),
]

WD_CIVIL_KINDS = [
    ("Q210932", "airliner (a passenger airplane)", "civil"),
    ("Q1062135", "business jet (a small passenger airplane)", "civil"), ("Q19799", "cargo airplane", "civil"),
    ("Q1153376", "flying boat (an airplane that lands on water)", "civil"),
    ("Q1372231", "light aircraft (a small airplane)", "civil"), ("Q133585", "airship", "civil"),
    ("Q34486", "helicopter", "civil"),
]
ADJECTIVES = {"Q30": "US", "Q145": "British", "Q174193": "British", "Q161885": "British", "Q15180": "Soviet",
              "Q7318": "German", "Q183": "German", "Q43287": "German", "Q41304": "German", "Q713750": "West German",
              "Q16957": "East German", "Q142": "French", "Q70972": "French", "Q71084": "French", "Q17": "Japanese",
              "Q188712": "Japanese", "Q159": "Russian", "Q34266": "Russian", "Q38": "Italian", "Q172579": "Italian",
              "Q148": "Chinese", "Q16": "Canadian", "Q408": "Australian", "Q34": "Swedish", "Q39": "Swiss",
              "Q36": "Polish", "Q55": "Dutch", "Q29": "Spanish", "Q43": "Turkish", "Q801": "Israeli", "Q668": "Indian",
              "Q155": "Brazilian", "Q884": "South Korean", "Q423": "North Korean", "Q33": "Finnish", "Q213": "Czech",
              "Q33946": "Czechoslovak", "Q28513": "Austro-Hungarian", "Q40": "Austrian", "Q31": "Belgian",
              "Q35": "Danish", "Q20": "Norwegian", "Q41": "Greek", "Q45": "Portuguese", "Q212": "Ukrainian",
              "Q36704": "Yugoslav", "Q218": "Romanian", "Q28": "Hungarian", "Q664": "New Zealand",
              "Q258": "South African", "Q96": "Mexican", "Q414": "Argentine"}


def sparql(s, query, tries=5):
    """The rows of a Wikidata SPARQL query, waiting and trying again when the service is busy; [] when it never
    answered."""
    for attempt in range(tries):
        try:
            r = s.get(WDQS, params={"query": query, "format": "json"}, timeout=120)
            if r.status_code == 200:
                return [{k: v["value"].rsplit("/entity/", 1)[-1] for k, v in b.items()}
                        for b in r.json()["results"]["bindings"]]
            time.sleep(10 * (attempt + 1))
        except Exception:  # noqa: BLE001 - tried again
            time.sleep(10 * (attempt + 1))
    return []


def wd_models(s, kinds, avoid=(), groups=None):
    """[(item, Commons category, answer, group)] for Wikidata's items of kinds with a Commons category and facts to
    say (as packs/service_packs.model_answer), leaving out items of the kinds in avoid."""
    found, taken = [], set()
    for qid, _, _ in avoid:
        taken.update(r["item"] for r in sparql(s, f"SELECT DISTINCT ?item WHERE {{ ?c wdt:P279* wd:{qid} . "
                                                  f"{{ ?item wdt:P279 ?c }} UNION {{ ?item wdt:P31 ?c }} }}"))
    for qid, phrase, group in kinds:
        if groups and group not in groups:
            continue
        for r in sparql(s, f"""SELECT DISTINCT ?item ?cat ?how WHERE {{ ?c wdt:P279* wd:{qid} .
                {{ ?item wdt:P279 ?c . BIND("model" AS ?how) }} UNION {{ ?item wdt:P31 ?c . BIND("one" AS ?how) }}
                ?item wdt:P373 ?cat . }}"""):
            if r["item"] not in taken and r["item"] != qid:
                taken.add(r["item"])
                found.append((r["item"], r["cat"], r["how"], phrase, group))
        time.sleep(1)
    facts = {}
    for start in range(0, len(found), 150):
        values = " ".join(f"wd:{f[0]}" for f in found[start:start + 150])
        for r in sparql(s, f"""SELECT ?item ?label (GROUP_CONCAT(DISTINCT ?o; separator="|") AS ?origins)
                (GROUP_CONCAT(DISTINCT ?c; separator="|") AS ?countries) (MIN(?from) AS ?start) (MAX(?to) AS ?end)
                (MIN(?made) AS ?inception) (GROUP_CONCAT(DISTINCT ?warLabel; separator="|") AS ?wars) WHERE {{
                VALUES ?item {{ {values} }} ?item rdfs:label ?label . FILTER(LANG(?label) = "en")
                OPTIONAL {{ ?item wdt:P495 ?o }} OPTIONAL {{ ?item wdt:P17 ?c }} OPTIONAL {{ ?item wdt:P729 ?from }}
                OPTIONAL {{ ?item wdt:P730 ?to }} OPTIONAL {{ ?item wdt:P571 ?made }}
                OPTIONAL {{ ?item wdt:P607 ?war . ?war rdfs:label ?warLabel . FILTER(LANG(?warLabel) = "en") }}
                }} GROUP BY ?item ?label"""):
            facts[r["item"]] = r
        time.sleep(1)
    out = []
    for item, cat, how, phrase, group in found:
        f = facts.get(item)
        if not f:
            continue
        origins = [q for q in (f.get("origins") or "").split("|") if q]
        countries = origins or ([q for q in (f.get("countries") or "").split("|") if q]
                                if how == "one" or phrase == "military decoration" else [])
        adjective = ADJECTIVES.get(countries[0], "") if len(countries) == 1 else ""
        wars = [{"World War II": "the Second World War", "World War I": "the First World War"}.get(
            w, w if re.match(r"^(Operation|Battle of|Siege of|the )", w) else "the " + w)
            for w in (f.get("wars") or "").split("|") if w][:2]
        start, end, made = (f.get("start") or "")[:4], (f.get("end") or "")[:4], (f.get("inception") or "")[:4]
        if phrase == "military decoration":
            period = f", established in {made}" if made else ""
        else:
            period = f", in service from {start} to {end}" if start and end else \
                f", which entered service in {start}" if start else ""
        name = clean(f.get("label"))
        if not name or (not adjective and not wars and not period):
            continue
        described = f"{adjective} {phrase}".strip()
        article = "a" if re.match(r"^(US|Ukrain|Ugand|Urugu|Uzbek|Europe|Unite|Utility)", described) \
            or described[0].lower() not in "aeiou" else "an"
        subject = (("an " if name[0] in "AEFHILMNORSX" else "a ") + name) if how == "model" else \
            ("the " + name if phrase == "military decoration" else name)
        answer = f"This is {subject}, {article} {described}" + (f" of {' and '.join(wars)}" if wars else "") + period
        out.append((item, cat, sentence(answer), group))
    say(f"  Wikidata: {len(out)} items with facts to say")
    return out


# ----------------------------------------------------------------- Wikimedia Commons, share-alike files

NOT_THE_THING = re.compile(r"\b(drawings?|diagrams?|schem\w*|blueprints?|plans?|illustrations?|paintings?|models?|"
                           r"scale|toys?|miniatures?|lego|kits?|dioramas?|cosplay\w*|logos?|icons?|svg|insignia|"
                           r"emblems?|patch(es)?|stamps?|coins?|posters?|maps?|interiors?|cockpits?|engines?|"
                           r"instrument\w*|details?|parts?|video\w*|manuals?|cartoons?|renders?|cgi|3d|games?|"
                           r"screenshots?|ammunition|cartridges?|fictional|statues?|sculptures?|memorials?|"
                           r"graves?|funerals?|in art)\b", re.I)
# Catalogue lines that are not captions, and captions saying the picture is a model or a toy.
NOT_A_CAPTION = re.compile(r"catalog(ue)? ?#|\btitle:|\btitre\s*:|\bformat\s*:|r[ée]f[ée]rence|corporation name|"
                           r"official nickname|\b(scale )?(models?|miniatures?|toys?|replicas?) of\b|\bscale model|"
                           r"\bdiorama", re.I)
# Files that are paintings, drawings or prints (by their name or categories), not photos.
PAINTED = re.compile(r"\b(paintings?|painted by|oil on|watercolou?rs?|drawings?|lithograph\w*|engravings?|etchings?|"
                     r"woodcuts?|prints? (of|by)|illustrations?|retrato|gem[äa]lde|peinture|tableau|portrait "
                     r"paintings|caricatures?|cartoons?|posters?)\b", re.I)
UNIFORM_DETAILS = [(re.compile(r"\b(" + p + r")\b", re.I), said) for p, said in (
    (r"high[- ]?vis\w*|hi[- ]?vis|reflective (vest|jacket)|safety vests?", "a high-visibility jacket"),
    (r"custodian helmets?", "a custodian helmet"), (r"bearskins?", "a bearskin cap"), (r"peaked caps?", "a peaked cap"),
    (r"berets?", "a beret"), (r"k[eé]pis?", "a kepi"), (r"shakos?", "a shako"), (r"pith helmets?", "a pith helmet"),
    (r"turnout gear|bunker gear", "turnout gear"), (r"body armou?r|stab vests?|bullet[- ]?proof vests?", "body armour"),
    (r"camouflage", "camouflage"), (r"dress uniforms?|full dress", "a dress uniform"), (r"medals?", "medals"),
    (r"white gloves", "white gloves"), (r"fustanellas?", "a fustanella (a pleated kilt)"), (r"halberds?", "a halberd"),
    (r"nurse'?s? caps?", "a nurse's cap"), (r"helmets?", "a helmet"))]


def details_in(text):
    """Up to two uniform details a file's words name ("a high-visibility jacket and a peaked cap"), or ""."""
    found = []
    for pattern, said in UNIFORM_DETAILS:
        if pattern.search(text or "") and said not in found and not (said == "a helmet" and any("helmet" in f
                                                                                              for f in found)):
            found.append(said)
    return " and ".join(found[:2])


def sa_files(s, titles):
    """[{title, url, credit, caption, year, place, cats}] for files whose licence is copyleft (CC BY-SA, GFDL, Free
    Art; never NC or ND), 50 a request, with the photo's year and the country at its camera's coordinates."""
    out = []
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 960,
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
            value = lambda k: clean(re.sub(r"<[^>]+>", " ", (meta.get(k) or {}).get("value") or ""))  # noqa: E731
            licence = value("LicenseShortName")
            if PAINTED.search(f"{p['title']} {value('Categories')}"):
                continue                               # a painting, drawing or print: not a photo of the thing
            if not COMMONS_SA.match(licence) or re.search(r"\bN[CD]\b", licence.upper()) \
                    or info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                continue
            years = [y for y in re.findall(r"\b(1[89]\d\d|20[0-2]\d)\b", value("DateTimeOriginal")) if int(y) <= 2026]
            place = ""                                 # (no offline map of countries in the kit)
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            caption = caption_text(captions.get(f"M{p['pageid']}")) or caption_text(value("ImageDescription"))
            if NOT_A_CAPTION.search(caption):
                caption = ""
            # The year only when the caption or file name says it, or the camera recorded its place (an old photo
            # scanned later often carries the scan date).
            year = years[0] if years and (years[0] in f"{caption} {p['title']}" or value("GPSLatitude")) else ""
            out.append({"title": p["title"], "url": re.sub(r"/\d+px-([^/]+)$", r"/960px-\1", info["thumburl"]),
                        "credit": f"{p['title']} by {value('Artist')[:100] or 'unknown'}, {licence}, {page}",
                        "caption": caption, "year": year, "place": place,
                        "cats": value("Categories").replace("|", "; ")})
        time.sleep(1)
    return out


def file_name(prefix, title):
    """A training copy's file name for a Commons file."""
    return f"{prefix}-" + re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80] + ".jpg"


def category_titles(s, category, most_subcats=6):
    """The file titles of a Commons category and of up to most_subcats of its subcategories (NOT_THE_THING left
    out); [] when the category cannot be read."""
    try:
        titles = commons_members(s, category, "file")
        subs = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
        for sub in [c for c in subs if not NOT_THE_THING.search(c)][:most_subcats]:
            titles += commons_members(s, sub, "file")
    except RuntimeError:
        return []
    return [t for t in dict.fromkeys(titles) if not NOT_THE_THING.search(t.rsplit(".", 1)[0])]


def file_rows(f, question, answer, prefix, weapon=False):
    """[(file name, address, row)] for one Commons file: the question, its caption, and "Where and when ..."."""
    keep, extra = safety([f["caption"], f["title"], f["cats"]])
    if not keep:
        return []
    name = file_name(prefix, f["title"])
    row = {"question": question, "answer": answer, "split": "", "credit": f["credit"],
           **sources.place_fields({"place": f["place"]}), **extra}
    out = [(name, f["url"], row)]
    if f["caption"] and not (weapon and HOW_TO.search(f["caption"])):
        out.append((name, f["url"], dict(row, question=NARRATE, answer=f["caption"])))
    twin = where_when(f["place"], f["year"], conflict_in(f["caption"]), row)
    if twin:
        out.append((name, f["url"], twin))
    return out


def prepare_models_sa(source, data_dir, kinds, avoid, groups, cap, prefix, no_people=False):
    """A Commons share-alike collection of models: Wikidata's items of kinds (in groups), a few BY-SA or GFDL files
    of each item's category, "What is this?" with Wikidata's facts, the caption and "Where and when ..."."""
    s = commons_session()
    models = wd_models(s, kinds, avoid, groups)
    random.Random(source.key).shuffle(models)
    want = int((cap + source.test) * 1.2)
    per_item = 3
    items, pictures = [], 0
    for item, cat, answer, group in models:
        if pictures >= want:
            break
        titles = category_titles(s, cat)
        random.Random(item).shuffle(titles)
        taken = 0
        for f in sa_files(s, titles[:per_item * 4]):
            if taken >= per_item or (no_people and PEOPLE.search(f"{f['title']} {f['caption']} {f['cats']}")):
                continue
            rows = file_rows(f, ASK_WHAT, answer, prefix, weapon=group == "weapon")
            if rows:
                items += rows
                taken += 1
        pictures += taken
    say(f"  Fetching {pictures} Commons share-alike pictures.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_commons_military_sa(source, data_dir, work, cap):
    """Vehicles, artillery, aircraft and ships under CC BY-SA or GFDL, files naming people left out."""
    return prepare_models_sa(source, data_dir, WD_KINDS, (), {"vehicle"}, cap, "milsa", no_people=True)


def prepare_commons_weapons_sa(source, data_dir, work, cap):
    """Small arms, swords, armour and decorations under CC BY-SA or GFDL."""
    return prepare_models_sa(source, data_dir, WD_KINDS, (), {"weapon"}, cap, "wpnsa")


def prepare_commons_airplanes_sa(source, data_dir, work, cap):
    """Civil aircraft under CC BY-SA or GFDL, military kinds left out."""
    return prepare_models_sa(source, data_dir, WD_CIVIL_KINDS, WD_KINDS, None, cap, "airsa")


# The uniformed services by country (as packs/service_packs.SERVICE_BY_COUNTRY) and single categories.
SERVICE_BY_COUNTRY = [
    ("Police officers by country", r"^Police officers (?:of|in|from) (.+)$", ASK_UNIFORM, "Police uniform of {c}"),
    ("Firefighters by country", r"^Firefighters (?:of|in|from) (.+)$", ASK_UNIFORM, "Firefighter's uniform of {c}"),
    ("Paramedics by country", r"^Paramedics (?:of|in|from) (.+)$", ASK_UNIFORM, "Paramedic's uniform of {c}"),
    ("Military police by country", r"^Military police (?:of|in) (.+)$", ASK_UNIFORM, "Military police uniform of {c}"),
    ("Park rangers by country", r"^Park rangers (?:of|in|from) (.+)$", ASK_UNIFORM, "Park ranger's uniform of {c}"),
    ("Nurses by country", r"^Nurses (?:of|in|from) (.+)$", ASK_UNIFORM, "Nurse's uniform of {c}"),
    ("Postal workers by country", r"^Postal workers (?:of|in|from) (.+)$", ASK_UNIFORM, "Postal worker's uniform of {c}"),
    ("Border guards by country", r"^Border guards (?:of|in|from) (.+)$", ASK_UNIFORM, "Border guard's uniform of {c}"),
    ("Military uniforms by country", r"^Military uniforms (?:of|in) (.+)$", ASK_UNIFORM, "Military uniform of {c}"),
    ("Police vehicles by country", r"^Police vehicles (?:of|in) (.+)$", ASK_WHAT, "This is a police vehicle in {c}"),
    ("Fire engines by country", r"^Fire engines (?:of|in) (.+)$", ASK_WHAT, "This is a fire engine in {c}"),
    ("Ambulances by country", r"^Ambulances (?:of|in) (.+)$", ASK_WHAT, "This is an ambulance in {c}"),
    ("Coast guards by country", r"^(?:Coast guard|Coastguard)s? (?:of|in) (.+)$", ASK_SERVICE, "The coast guard of {c}"),
]
SERVICE_FIXED = [
    ("King's Guard", ASK_UNIFORM, "The uniform of the King's Guard of the UK, the British Army's guard at the royal "
                                  "palaces in London"),
    ("Pontifical Swiss Guard", ASK_UNIFORM, "The uniform of the Pontifical Swiss Guard, the Pope's guard in the Vatican"),
    ("Evzones", ASK_UNIFORM, "The uniform of the Evzones, the Presidential Guard of Greece"),
    ("Prison guards", ASK_UNIFORM, "A prison officer's uniform"),
    ("Customs officers", ASK_UNIFORM, "A customs officer's uniform"),
    ("Mail carriers", ASK_UNIFORM, "A mail carrier's uniform"),
]
COUNTRY_SAID = {"United States": "the USA", "the United States": "the USA", "United Kingdom": "the UK",
                "the United Kingdom": "the UK", "the Netherlands": "the Netherlands", "the Philippines": "the Philippines",
                "the Czech Republic": "Czechia", "Czech Republic": "Czechia"}


def prepare_commons_uniformed_sa(source, data_dir, work, cap):
    """Uniformed services by country under CC BY-SA or GFDL: the uniform with the photo's era and the details its
    words name, its caption, and "Where and when ..."."""
    s = commons_session()
    categories = []
    for parent, pattern, question, start in SERVICE_BY_COUNTRY:
        try:
            subs = [c.split(":", 1)[-1] for c in commons_members(s, parent, "subcat")]
        except RuntimeError:
            continue
        for sub in subs:
            m = re.match(pattern, sub)
            if m:
                country = re.sub(r"\s*\((country|state)\)$", "", m.group(1))
                categories.append((sub, question, start.format(c=COUNTRY_SAID.get(country, country))))
    categories += SERVICE_FIXED
    random.Random(source.key).shuffle(categories)
    want = int((cap + source.test) * 1.2)
    per_category = max(3, per_label(want, len(categories)))
    items, pictures = [], 0
    for category, question, start in categories:
        if pictures >= want:
            break
        titles = category_titles(s, category, 4)
        random.Random(category).shuffle(titles)
        taken = 0
        for f in sa_files(s, titles[:per_category * 3]):
            if taken >= per_category:
                break
            answer = start
            if question == ASK_UNIFORM:
                era = (f"in the {f['year'][:3]}0s" if int(f["year"]) < 1980 else f"in {f['year']}") if f["year"] else ""
                details = details_in(f"{f['caption']} {f['title']} {f['cats']}")
                answer += (f", photographed {era}" if era else "") + (f", with {details}" if details else "")
            rows = file_rows(f, question, sentence(answer), "unisa")
            if rows:
                items += rows
                taken += 1
        pictures += taken
    say(f"  Fetching {pictures} Commons share-alike uniformed-service pictures.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- Bundesarchiv on Commons

BUNDESARCHIV = "Images from the German Federal Archive"
BUNDESARCHIV_WORDS = ("Soldat", "Soldaten", "Panzer", "Flugzeug", "Kriegsschiff", "U-Boot", "Uniform", "Polizei",
                      "Feuerwehr", "Volkspolizei", "Grenztruppen", "Bundeswehr", "Wehrmacht", "Marine", "Artillerie",
                      "Parade", "Wachregiment")
ENGLISH = re.compile(r"\b(the|of|and|with|in|at|on)\b")


def prepare_bundesarchiv_sa(source, data_dir, work, cap):
    """Bundesarchiv photos on Commons (CC BY-SA 3.0 de) found by German search words in the Archive's category,
    each with its English caption or English description ("Describe this picture.") and "Where and when ..."
    (the photo's year; its place when the camera's coordinates give one). Files with no English text are left out:
    the kit has no German translation model."""
    s = commons_session()
    want = int((cap + source.test) * 1.2)
    per_word = per_label(want * 3, len(BUNDESARCHIV_WORDS))
    titles = []
    for word in BUNDESARCHIV_WORDS:
        try:
            data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": min(500, per_word),
                                   "srsearch": f'incategory:"{BUNDESARCHIV}" {word}'})
        except RuntimeError:
            break
        titles += [h["title"] for h in (data.get("query") or {}).get("search", [])]
        time.sleep(1)
    titles = list(dict.fromkeys(titles))
    random.Random(405).shuffle(titles)
    items, pictures = [], 0
    for start in range(0, len(titles), 200):
        for f in sa_files(s, titles[start:start + 200]):
            if not f["caption"] or len(ENGLISH.findall(f["caption"])) < 2:
                continue
            keep, extra = safety([f["caption"], f["title"]])
            if not keep:
                continue
            name = file_name("bunda", f["title"])
            row = {"question": NARRATE, "answer": f["caption"], "split": "", "credit": f["credit"],
                   **sources.place_fields({"place": f["place"]}), **extra}
            items.append((name, f["url"], row))
            twin = where_when(f["place"], f["year"], conflict_in(f["caption"]), row)
            if twin:
                items.append((name, f["url"], twin))
            pictures += 1
        if pictures >= want:
            break
    say(f"  Fetching {pictures} Bundesarchiv pictures.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- Europeana 1914-1918

def europeana_text(item):
    """An item's English description (or its English title when that is a description), or ""."""
    for field in ("dcDescriptionLangAware", "dcTitleLangAware"):
        for text in (item.get(field) or {}).get("en") or []:
            said = caption_text(re.sub(r"^(glass plate|photograph|photo|postcard)\s*:\s*", "", text, flags=re.I), 70)
            if said:
                return said
    return ""


def europeana_picture(url):
    """A Europeana picture address at about 1,600 pixels (a IIIF address sized down, others as they are)."""
    return re.sub(r"/full/full/0/default\.jpg$", "/full/!1600,1600/0/default.jpg", url or "")


def prepare_europeana_1914_1918(source, data_dir, work, cap):
    """Europeana 1914-1918 (collection 2020601): items under CC BY-SA with an English description, the description
    as "Describe this picture." and "When was this photo taken?" from the item's year, during the First World War
    when the year is 1914-1918 (the collection's subject)."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = sources.USER_AGENT
    key = os.environ.get("EUROPEANA_KEY", EUROPEANA_KEY)
    want = int((cap + source.test) * 1.2)
    items, pictures, cursor = [], 0, "*"
    while pictures < want and cursor:
        try:
            data = s.get(EUROPEANA, timeout=60, params={"wskey": key, "query": "europeana_collectionName:2020601*",
                                                        "qf": "TYPE:IMAGE", "rows": 100, "profile": "rich",
                                                        "cursor": cursor}).json()
        except Exception:  # noqa: BLE001 - stop here
            break
        for item in data.get("items") or []:
            if pictures >= want:
                break
            rights = " ".join(item.get("rights") or [])
            picture = europeana_picture((item.get("edmIsShownBy") or [""])[0])
            answer = europeana_text(item)
            if "/by-sa/" not in rights or not picture or not answer:
                continue
            keep, extra = safety([answer])
            if not keep:
                continue
            name = "eu1418-" + re.sub(r"[^\w-]+", "_", item.get("id", str(pictures)))[-80:] + ".jpg"
            provider = ", ".join(p for p in item.get("dataProvider") or [] if p != "Europeana 1914-1918")
            credit = (f"{clean((item.get('title') or [''])[0])[:120]}, " + (f"{provider}, " if provider else "")
                      + f"Europeana 1914-1918, {rights}, {item.get('guid', '').split('?')[0]}")
            row = {"question": NARRATE, "answer": answer, "split": "", "credit": credit, **extra}
            items.append((name, picture, row))
            years = [y for y in (item.get("year") or []) if re.match(r"^(19[01]\d)$", y)]
            if years:
                during = ", during the First World War" if "1914" <= years[0] <= "1918" else ""
                items.append((name, picture, dict(row, question="When was this photo taken?",
                                                  answer=f"It was taken in {years[0]}{during}.")))
            pictures += 1
        cursor = data.get("nextCursor")
        time.sleep(1)
    say(f"  Fetching {pictures} Europeana 1914-1918 pictures.")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=4)


# ----------------------------------------------------------------- needing sign-up, and not included

SERVICE_SIGN_UP = {
    "DVIDS, the US Defense Visual Information Distribution Service (public domain US forces photos)":
        "https://www.dvidshub.net : its API needs a free key (https://api.dvidshub.net). Many of its photos are "
        "already on Commons and reach the service packs.",
    "US National Archives catalogue API v2": "https://catalog.archives.gov/api/v2 : needs a key, to search series "
                                             "beyond those in packs/service_packs.py.",
    "Flickr: US Air Force, US Navy, US Coast Guard, US Army, NASA Armstrong, UK Ministry of Defence, police and fire "
    "services": "https://www.flickr.com/services/api/misc.api_keys.html : a free Flickr API key; check each photo's "
                "licence on its page.",
    "Imperial War Museums (IWM Non-Commercial Licence)": "https://www.iwm.org.uk/collections : the site refuses "
                                                         "programs (Cloudflare check) and has no open API; download by "
                                                         "hand under its licence (personal, non-commercial use).",
    "National Army Museum, RAF Museum, Royal Museums Greenwich, Canadian War Museum": "their online collections have "
        "no bulk download or open licence; ask the museum (images are mostly for non-commercial use with "
        "permission).",
    "Australian War Memorial items still in copyright": "https://www.awm.gov.au/copyright : by request; its "
                                                        "public-domain photos are already the open awm pack.",
}

SERVICE_NOT_INCLUDED = {
    "af.mil, navy.mil and uscg.mil photo pages, FEMA's media library": "refused the machine these entries were made "
                                                                       "on (403); their photos are on Commons.",
    "Naval History and Heritage Command": "no secure connection could be made (an incomplete certificate chain); its "
                                          "NH photos are on Commons.",
    "Europeana with an open-licence filter": "almost no English descriptions of military or police photos came back.",
    "Commons files under NC or ND licences": "not allowed on Commons, so none are found.",
}


# ----------------------------------------------------------------- the table

SERVICE_SOURCES = [
    Source("commons_military_sa", "Wikimedia Commons: military vehicles, aircraft and ships, files under CC BY-SA or "
                                  "GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0; facts from Wikidata (CC0)",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org ; "
           "facts from Wikidata, CC0, https://www.wikidata.org", "share-alike", 3000, 20,
           prepare_commons_military_sa, "about 300 MB"),
    Source("commons_weapons_sa", "Wikimedia Commons: small arms, swords, armour and military decorations, files "
                                 "under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0; facts from Wikidata (CC0)",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org ; "
           "facts from Wikidata, CC0, https://www.wikidata.org", "share-alike", 1200, 15,
           prepare_commons_weapons_sa, "about 120 MB"),
    Source("commons_airplanes_sa", "Wikimedia Commons: airliners and civil aircraft, files under CC BY-SA or GFDL "
                                   "(share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0; facts from Wikidata (CC0)",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org ; "
           "facts from Wikidata, CC0, https://www.wikidata.org", "share-alike", 1500, 15,
           prepare_commons_airplanes_sa, "about 150 MB"),
    Source("commons_uniformed_sa", "Wikimedia Commons: police, fire, ambulance, rangers, nurses, military and "
                                   "ceremonial uniforms by country, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2500, 20, prepare_commons_uniformed_sa, "about 250 MB"),
    Source("bundesarchiv_sa", "German Federal Archives (Bundesarchiv) photos of soldiers, vehicles, police and fire "
                              "brigades, on Wikimedia Commons (share-alike)",
           "CC BY-SA 3.0 de (https://creativecommons.org/licenses/by-sa/3.0/de/), as given by the Bundesarchiv to "
           "Wikimedia Commons",
           "Bundesarchiv, CC BY-SA 3.0 de, each photo with its Bild number and photographer in its row, "
           "https://commons.wikimedia.org/wiki/Commons:Bundesarchiv", "share-alike", 2000, 20,
           prepare_bundesarchiv_sa, "about 200 MB"),
    Source("europeana_1914_1918", "Europeana 1914-1918: family photos and documents of the First World War "
                                  "(share-alike)",
           "CC BY-SA 3.0 (each item's rights on Europeana)",
           "Europeana 1914-1918, contributors and partner institutions, CC BY-SA 3.0, "
           "https://www.europeana.eu/en/collections/topic/83-1914-1918", "share-alike", 2500, 20,
           prepare_europeana_1914_1918, "about 500 MB"),
]

# The collections a picture-making model may learn from: vehicles, aircraft and ships without people. Never weapons,
# never people.
SERVICE_PICTURE_MAKING_OK = {"commons_military_sa"}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try one service collection.")
    parser.add_argument("key", choices=[s.key for s in SERVICE_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in SERVICE_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="service-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('content') == 'graphic')} graphic rows, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
