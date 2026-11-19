"""Pack builders for UNITED STATES pictures: American houses outside and inside, rooms, streets and what people on
them wear, cars, wild plants and animals by state, US money, US road signs, and packaged products and the shops that
sell them. Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" ("Natchez,
Louisiana, USA"; "place_kind" when the place is not where the photo was taken), "child": true where the words of a
picture name a child, and "facts" where the source gives more than the answer says. A picture with more than one
question comes once with its JPEG and then again as (None, None, row) rows whose "file" names the same picture
(food_packs.with_twins). The limit counts pictures.

Every answer is a fixed sentence written here from the source's own records: a Library of Congress survey caption
and its subject headings, a Commons category's name (the categories a file sits in say which car model it is, or
that a man in it wears a hat), a road-sign file's own description, an iNaturalist community identification. Nothing
is written by an AI model, nobody is named, and nothing is guessed about who a person is: what people wear is said
only where a Commons category says it ("Men wearing baseball caps"), and as "a man", "a woman" or "people" only as
that category says. Places come from the records only (the survey's place heading, the state or city a category
names, an iNaturalist observation's state, or a Commons photo's camera coordinates).

Safety (packs/SOURCE-RULES.md): no sexual content (files whose words name nudity, underwear or swimwear are left out,
and so are clothing categories of those kinds); children only in everyday clothed scenes, and every row whose words
name a child is marked "child". The street and people pack and the car pack (people stand near the cars) are never
used for picture-making (the kit's NOT_FOR_PICTURE_MAKING and PEOPLE_AND_BODILY_PACK_KEYS).

The packs (all open: public domain, CC0 or CC BY; checked at the source in November 2026):
  loc_habs_houses       Library of Congress, Historic American Buildings Survey (HABS, 1933 onwards, US National Park
                        Service; https://www.loc.gov/collections/historic-american-buildings-landscapes-and-engineering-
                        records/, rights: "No known restrictions on images made by the U.S. Government",
                        https://www.loc.gov/rr/print/res/114_habs.html): photographs of American houses, outside and
                        inside (farmhouses, log houses, mansions, row houses, cottages, adobe and shotgun houses;
                        kitchens, parlors, dining rooms, bedrooms, stair halls), with the survey's own caption, the
                        record's place and building date. "What room is this?" -> "This is the kitchen of the
                        Badin-Roque House." / "What kind of house is this?" -> "It is a wooden house with clapboard
                        siding, built about 1919." (from the record's subject headings). The engineering side of the
                        same collection (dams, bridges, mills) is land_industry_packs.loc_haer; this pack asks only
                        for houses and rooms, and leaves out photos loc_haer's search words would find first.
  commons_us_homes      Wikimedia Commons: "Houses in <state>" for all 50 states and the District of Columbia, house
                        styles of the United States (Victorian, Colonial Revival, Greek Revival, Tudor Revival,
                        Italianate, Federal, log cabins, mobile homes, row houses and townhouses, sod, dogtrot,
                        shotgun, adobe and split-level houses) and US rooms (home kitchens, living rooms, bedrooms,
                        bathrooms, dining rooms). Pictures CC0, public domain or CC BY (never BY-SA: the kit's
                        commons_us_sa).
  commons_us_streets    Commons: "Streets in <city>" for 40 US cities (the city as the place), pedestrians and street
                        photography in the United States and street fashion, with "What is the person wearing?"
                        from the clothing categories a photo sits in ("A man in this picture is wearing a baseball
                        cap.") and the file's own caption.
  commons_us_cars       Commons: "Automobiles in <state>" for all 50 states and their city subcategories; each photo's
                        model from the model category it sits in ("It is a 1966 Ford Mustang.") and its colour from
                        its colour category. Only photos whose categories name a model are used.
  inaturalist_us        iNaturalist research-grade observations in each US state (photos CC0 or CC BY, each
                        photographer credited; https://www.inaturalist.org/pages/terms): plants, fungi, insects,
                        birds, mammals, reptiles, amphibians, spiders, molluscs and fish, the states taking turns, the
                        state as the place. The global inaturalist pack takes the most-voted observations worldwide;
                        this one takes ordinary observations state by state.
  commons_us_money      Commons: US banknotes by denomination ($1 to $100, and the older large notes) and US coins by
                        name (cents, nickels, dimes, quarters, half dollars, dollar coins). US currency designs are US
                        government work; each photo's own licence is checked (CC0, PD or CC BY).
  us_road_signs         Commons: the drawings of US road signs (Category:Diagrams of road signs of the United States,
                        mostly MUTCD signs, public domain as US government work or simple shapes), each with its MUTCD
                        number from its file name and its meaning from its own description, set black on white; and
                        photos of US stop, yield, speed-limit and pedestrian-crossing signs. (events_safety_packs
                        safety_signs takes a few road signs of each of many countries; this pack is the US set.)
  commons_packaging     Commons: packaged goods and their packaging (packaged food, drink cans, plastic and glass
                        bottles, egg cartons, milk containers, cardboard food boxes, sweet wrappers, blister packs,
                        cartons, carrier bags, supermarket shelves) and US supermarkets and grocery stores ("What
                        kind of place is this?").

Share-alike, non-commercial and research collections on the same subjects (Commons BY-SA files of these categories,
Open Food/Beauty/Products Facts products sold in the USA, iNaturalist CC BY-NC photos in the USA, CPSC recall
photos), the sign-up collections, the ones looked at and left out (with Walmart, Target and Zillow: their terms
forbid copying) and the owners to ask for permission are in training-kit/kit/us_sources.py.

    python packs/us_packs.py loc_habs_houses --limit 8      (prints a few rows: a quick check)
"""

import collections
import io
import json
import math
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, fetch_all, article, needs_description
from build_packs import INAT_GROUPS
from food_packs import with_twins, count_pictures, commons_get, commons_members
from home_packs import commons_fetch, file_name, symbol_picture, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count
from mechanical_packs import mech_entries, in_english, PLACES, JUST_A_RECORD, NOT_A_CHILD, NOT_A_PHOTO
from documentary_packs import tidy, usable, get_json, LOC, loc_free
from land_industry_packs import US_STATE_CODES, haer_case
from places import where, place_name

DESCRIBE_Q = "Describe this picture."
WHAT_Q = "What is this?"
HOUSE_Q = "What kind of house is this?"
ROOM_Q = "What room is this?"
PLACE_Q = "What kind of place is this?"
WEAR_Q = "What is the person wearing?"
CAR_Q = "What car is this?"
COLOUR_Q = "What colour is the car?"
MONEY_Q = "What money is this?"
SIGN_Q = "What does this road sign mean?"
PRODUCT_Q = "What product is this?"
WHERE_Q = "Where was this photo taken?"

STATES = [s for c, s in US_STATE_CODES.items() if c not in ("PR", "GU", "VI", "DC")]
# Words that make a picture unusable here: nudity, underwear and swimwear (the safety rules).
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|bathing suits?|underwear|lingerie|bra|bras|briefs|nude|naked|topless|"
                       r"shirtless|bare-chested|sexy|sexual\w*|erotic\w*)\b"
                       # criminal-investigation evidence photos (Commons files many FBI photos of the Epstein
                       # properties under "Home kitchens in the United States" and other room categories)
                       r"|epstein|\bEFTA\d+|crime scenes?|evidence photo\w*|mug ?shots?|\bautops\w*", re.I)


def capital(text):
    """The text with its first letter in capitals."""
    return text[:1].upper() + text[1:]


def listed(parts):
    """ "a, b and c" from a list of words."""
    parts = list(parts)
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


# ----------------------------------------------------------------- Library of Congress: HABS houses

HABS = "collections/historic-american-buildings-landscapes-and-engineering-records/"
HABS_CREDIT = ("Historic American Buildings Survey, Library of Congress, Prints and Photographs Division, no known "
               "restrictions on images made by the U.S. Government (https://www.loc.gov/rr/print/res/114_habs.html)")
# Search words: kinds of house, and rooms (each search is limited to records with pictures).
HABS_TERMS = ("house", "dwelling", "farmhouse", "mansion", "cottage", "log house", "log cabin", "row house",
              "townhouse", "plantation house", "bungalow", "adobe house", "shotgun house", "parsonage",
              "boarding house", "double house", "tenant house", "kitchen", "parlor", "dining room", "bedroom",
              "stair hall", "living room", "sitting room", "library room", "front porch", "fireplace")
# Captions that are copies of older pictures or drawings, not the survey's own photographs ("elevation" and
# "section" are kept: on a HABS photo, "NORTH ELEVATION" means the north side of the house).
HABS_NOT_OWN = re.compile(r"\b(photocopy|photocopied|copy of|reproduction|drawing|drawn|floor plan|site plan|plans?\b|"
                          r"sketch|map|postcard|lithograph|engraving|rendering|blueprint|diagram|courtesy|"
                          r"original in|source:|data pages?|chamber of commerce|collection of|lent by)\b", re.I)
# The rooms a caption can name, as said in the answer.
ROOMS = [(r"\bsummer kitchen\b", "summer kitchen"), (r"\bkitchen\b", "kitchen"),
         (r"\b(front |back |rear )?parlou?rs?\b", "parlor (sitting room)"), (r"\bdining room\b", "dining room"),
         (r"\bliving room\b", "living room"), (r"\bsitting room\b", "sitting room"),
         (r"\bdrawing room\b", "drawing room"), (r"\b(master )?bed ?rooms?\b|\bbedchamber\b", "bedroom"),
(r"\bstair ?hall\b|\bstaircase\b|\bstairway\b", "stair hall"),
         (r"\bcentral hall\b|\bentrance hall\b|\bfront hall\b|\bhallway\b", "hall"),
         (r"\blibrary\b", "library"), (r"\bstudy\b", "study"), (r"\bbath ?rooms?\b", "bathroom"),
         (r"\bpantry\b", "pantry"), (r"\battic\b", "attic"), (r"\bcellar\b|\bbasement\b", "cellar (basement)"),
         (r"\bball ?room\b", "ballroom"), (r"\boffice\b", "office"), (r"\bnursery\b", "nursery"),
         (r"\bsun ?(room|porch)\b", "sunroom"), (r"\bsleeping porch\b", "sleeping porch")]
INTERIOR = re.compile(r"\b(interior|room|parlou?r|kitchen|hall|stair|chamber|fireplace|mantel|attic|cellar|"
                      r"basement|pantry|library|bath)\b", re.I)
EXTERIOR = re.compile(r"\b(exterior|elevation|fa[cç]ade|front|rear|side|view (from|of|looking)|general view|"
                      r"perspective|oblique|context|streetscape)\b", re.I)
# The record's subject headings as kinds of house (the first that matches) and as the material or a feature.
HOUSE_KINDS = [("log houses", "log house"), ("log cabins", "log cabin"), ("farmhouses", "farmhouse"),
               ("mansions", "mansion"), ("row houses", "row house"), ("townhouses", "townhouse"),
               ("plantation houses", "plantation house"), ("bungalows", "bungalow"), ("cottages", "cottage"),
               ("shotgun houses", "shotgun house"), ("double houses", "double house"),
               ("tenant houses", "tenant house"), ("boardinghouses", "boarding house"),
               ("rectories", "rectory"), ("parsonages", "parsonage"), ("apartment houses", "apartment building"),
               ("dwellings", "house"), ("houses", "house")]
HOUSE_MATERIALS = [("brick buildings", "brick"), ("stone buildings", "stone"), ("wooden buildings", "wooden"),
                   ("log buildings", "log"), ("adobe buildings", "adobe"), ("frame buildings", "timber-framed"),
                   ("concrete buildings", "concrete"), ("stucco", "stucco")]
HOUSE_FEATURES = [("clapboard siding", "clapboard siding"), ("shingle siding", "shingle siding"),
                  ("board & batten siding", "board-and-batten siding"), ("gable roofs", "a gable roof"),
                  ("hipped roofs", "a hipped roof"), ("gambrel roofs", "a gambrel roof"),
                  ("mansard roofs", "a mansard roof"), ("porches", "a porch"), ("verandas", "a veranda"),
                  ("chimneys", "a chimney"), ("dormers", "dormer windows"), ("cupolas", "a cupola")]


def habs_caption(text, title):
    """A HABS photo caption as (what the photo shows, the site's name): "13. Interior view of east room of house
    view from the north - George Riley Willis House & Kitchen, Portsmouth, Carteret County, NC" -> ("Interior view
    of east room of house view from the north", "George Riley Willis House & Kitchen"); ("", "") when the photo is a
    copy of an older picture or a drawing."""
    text = re.sub(r"^\s*\d+[A-Z]?\.\s*", "", clean(text))
    if HABS_NOT_OWN.search(text):
        return "", ""
    what, _, site = text.partition(" - ")
    what = what.strip(" .")
    capitals = re.search(r"\b[A-Z]{2,}[A-Z0-9 ,.;:'()&/\-]{8,}$", what)    # a photographer's note in front
    if capitals and capitals.start() > 0:
        what = capitals.group(0)
    if sum(c.isupper() for c in what) > sum(c.islower() for c in what):
        what = haer_case(what)
    site = (site or clean(title)).split(",")[0].strip(" .")
    return what, site


def habs_place(record, item):
    """Where a HABS item is: "Natchez, Louisiana, USA" from its place heading or the state code ending its title;
    ""."""
    for rec in (item, record):
        for p in (rec.get("place") or []):
            parts = [x.strip(" .") for x in clean((p or {}).get("title")).split("--") if x.strip(" .")]
            if parts and parts[0] in US_STATE_CODES.values():
                town = [x for x in parts[1:] if not re.search(r"\b(county|parish|borough)$", x, re.I)]
                return place_name(*(town[-1:] + [parts[0], "USA"]))
    parts = [x.strip(" .") for x in clean(record.get("title")).split(",")]
    if len(parts) >= 3 and parts[-1] in US_STATE_CODES:
        town = parts[-3] if re.search(r"\b(county|parish|borough)$", parts[-2], re.I) else parts[-2]
        return place_name(town, US_STATE_CODES[parts[-1]], "USA")
    return ""


def habs_built(item):
    """When the house was built, from the record's note "Building/structure dates: ca. 1919 Initial Construction"
    -> "about 1919"; "" when the record does not say."""
    for note in item.get("notes") or []:
        m = re.search(r"Building/structure dates:\s*(ca\.\s*)?(\d{4})(\s*-\s*\d{4})?\s+Initial Construction",
                      str(note), re.I)
        if m:
            return ("about " if m.group(1) else "in ") + m.group(2) + (m.group(3) or "").replace(" ", "")
    return ""


def habs_kind(subjects, built):
    """ "It is a brick farmhouse with a gable roof and a porch, built about 1850." from the record's subject
    headings (only the kinds, materials and features in the tables above); "" when no kind of house is listed."""
    subjects = {clean(s).lower() for s in subjects}
    kind = next((name for tag, name in HOUSE_KINDS if tag in subjects), "")
    if not kind:
        return ""
    material = next((name for tag, name in HOUSE_MATERIALS if tag in subjects), "")
    if material == "log" and kind.startswith("log"):
        material = ""
    features = [name for tag, name in HOUSE_FEATURES if tag in subjects][:3]
    if kind == "house" and not material and not features and not built:
        return ""                                        # "It is a house." says nothing the question does not
    words = f"{material} {kind}".strip()
    text = f"It is {article(words)} {words}"
    if features:
        text += " with " + listed(features)
    if built:
        text += f", built {built}"
    return text + "."


def habs_room(what):
    """The room a caption names ("kitchen", "parlor (sitting room)"), when it is an inside view; ""."""
    if not INTERIOR.search(what) or re.search(r"\bexterior\b", what, re.I):
        return ""
    return next((name for pattern, name in ROOMS if re.search(pattern, what, re.I)), "")


def habs_items(s, term, want, rng, seen):
    """[(name, picture address, rows)] for HABS items found by a search word: up to three photos from each item,
    each with its caption ("Describe this picture."), the room or the kind of house, and the place."""
    data = get_json(s, LOC + HABS, {"fo": "json", "c": 100, "q": term, "sp": rng.randint(1, 8),
                                    "fa": "online-format:image", "at": "results"}, pause=15)
    results = (data or {}).get("results") or []
    rng.shuffle(results)
    items = []
    for record in results:
        if len(items) >= want or listing_out_of_time():
            break
        url = re.sub(r"^(https?:)?//", "https://", record.get("url") or record.get("id") or "")
        subjects = record.get("subject") or []
        if url in seen or not loc_free(record) or "/item/" not in url:
            continue
        if not {"houses", "dwellings", "domestic life", "kitchens"} & {clean(x).lower() for x in subjects}:
            continue                                     # a mill, a church or a bridge: not a home
        seen.add(url)
        time.sleep(1.5)                                  # the Library asks for about one request a second
        full = get_json(s, url, {"fo": "json"}, pause=15) or {}
        item = full.get("item") or {}
        place = habs_place(record, item)
        built = habs_built(item)
        kind = habs_kind(item.get("subject_headings") or subjects, built)
        photos = []
        for resource in full.get("resources") or []:
            for files in resource.get("files") or []:
                pics = [f for f in files if f.get("mimetype") in ("image/jpeg", "image/jpg") and f.get("width")]
                cap = next((f.get("title") for f in files if f.get("use") == "caption"), "")
                best = max((f for f in pics if f["width"] <= 2100), key=lambda f: f["width"], default=None)
                if best and cap:
                    photos.append((best["url"], cap))
        rng.shuffle(photos)
        taken = 0
        for picture, cap in photos:
            what, site = habs_caption(cap, record.get("title"))
            answer = tidy(f"{what}. {site}") if what else ""
            if taken >= 3 or NOT_SHOWN.search(f"{answer} {cap}"):
                continue
            if not usable(answer, 4):          # free HABS photo, caption too short: set aside for a description
                stem = re.sub(r"\W", "", picture.rsplit("/", 1)[-1].rsplit(".", 1)[0])
                needs_description(f"habs-{stem}.jpg", picture, f"{clean(cap)[:150]}, {HABS_CREDIT}, {url}",
                                  "no known restrictions (U.S. Government work)", text=answer, title=clean(cap),
                                  page_url=url, place=place, reason="its caption is under four words",
                                  extra={"subjects": [clean(x) for x in subjects][:12], "kind": kind})
                continue
            taken += 1
            credit = f"{clean(cap)[:150]}, {HABS_CREDIT}, {url}"
            rows = [{"question": DESCRIBE_Q, "answer": answer, "credit": credit, **where(place)}]
            room = habs_room(what)
            if room:
                rows.append({"question": ROOM_Q, "answer": f"This is the {room} of {site}." if site else
                             f"This is the {room}.", "credit": credit, **where(place)})
            elif kind and EXTERIOR.search(what) and not re.search(r"\bdetail\b", what, re.I):
                rows.append({"question": HOUSE_Q, "answer": kind, "credit": credit, **where(place),
                             "facts": {"subjects": sorted(clean(x) for x in subjects)[:20]}})
            if place:
                rows.append({"question": WHERE_Q, "answer": f"It was taken in {place}.", "credit": credit,
                             **where(place)})
            rows = [mark_child(r, cap) for r in rows]
            stem = re.sub(r"\W", "", picture.rsplit("/", 1)[-1].rsplit(".", 1)[0])
            items.append((f"habs-{stem}.jpg", picture, rows))
    return items


def build_loc_habs_houses(limit):
    """The HABS houses pack: for each search word, items of the HABS/HAER/HALS collection that are homes (their
    subject headings say houses, dwellings or domestic life), up to three photos each."""
    s, rng, items, seen = session(), random.Random(1933), [], set()
    terms = list(HABS_TERMS)
    rng.shuffle(terms)
    per_term = limit // len(terms) + 2
    rounds = 0
    while len(items) < limit * 1.25 and rounds < 3:
        rounds += 1
        for term in terms:
            if listing_out_of_time():          # leave the rest of the time for fetching what was found
                say("  HABS: stopped looking at half the time limit")
                break
            found = habs_items(s, term, int(per_term * 1.3), rng, seen)
            items += found
            say(f"  HABS '{term}': {len(found)} photos ({len(items)} in all)")
            if len(items) >= limit * 1.25:
                break
        if listing_out_of_time():
            break
    rng.shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.2) + 2], workers=3, pause=0.5)[:limit]
    say(f"loc_habs_houses: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- shared: Wikimedia Commons, US categories

# Subcategories that are about something else than the thing: firms, events, art, maps, museums of other things.
US_NOT_THE_THING = re.compile(r"\b(by (color|colour|year|decade|century|architect|style|type|artist|museum|"
                              r"collection|name|county|city|state)|drawings?|maps?|plans?|paintings?|in art|"
                              r"postcards?|advertis\w*|logos?|events?|exhibitions?|comic-con|views from|"
                              r"dealerships?|parts|repair|interiors? of (the )?\w+ museum|people depicted|"
                              r"signatures|imitations?|fantasy|errors?|gallery pages|quality images)\b", re.I)


def us_spec(category, question, answer, place="", depth=0, kind=None):
    """One Commons category for us_commons: its question and fixed answer (None: the rows come from the file's own
    categories or caption), the place it names and how deep to look (0: the category itself; 1: and its
    subcategories)."""
    return {"category": category, "question": question, "answer": answer, "place": place, "depth": depth,
            "kind": kind}


def spec_files(s, spec, most_subcategories=40):
    """[(file title, the subcategory it came from)] for a spec: the category's files and, at depth 1, its
    subcategories' (not those about something else), drawings and art left out by their names."""
    category = spec["category"]
    found = {t: category for t in commons_members(s, category, "file") if not NOT_A_PHOTO.search(t)}
    if spec["depth"]:
        subs = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
        subs = [c for c in subs if not NOT_A_PHOTO.search(c) and not US_NOT_THE_THING.search(c)]
        random.Random(category).shuffle(subs)
        for sub in subs[:most_subcategories]:
            if listing_out_of_time():
                break
            for t in commons_members(s, sub, "file"):
                if not NOT_A_PHOTO.search(t):
                    found.setdefault(t, sub)
    return list(found.items())


def file_categories(s, titles):
    """{file title: [its visible Commons categories, without "Category:"]} for up to 50 files at a time."""
    out = {}
    for start in range(0, len(titles), 50):
        params = {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "categories",
                  "clshow": "!hidden", "cllimit": "max"}
        while True:
            data = commons_get(s, params)
            for p in ((data.get("query") or {}).get("pages") or {}).values():
                out.setdefault(p.get("title"), []).extend(c["title"].split(":", 1)[-1]
                                                          for c in p.get("categories") or [])
            if "continue" not in data:
                break
            params.update(data["continue"])
        time.sleep(1)
    return out


def us_commons(specs, limit, prefix, extra=None, drawings=False):
    """A Commons pack from US category specs: the categories take turns, in a fixed shuffled order, so each gets an
    even share. Each picture gets its spec's question and answer (where the spec has one), the rows extra(title,
    categories, spec, place) gives from the file's own categories (where extra is given), and, when it has a real,
    respectful English caption or description, "Describe this picture." with it. The place is the spec's, else the
    country at the photo's camera coordinates. A file with no row is left out."""
    s, items, seen = session(), [], set()
    order = list(specs)
    random.Random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    want = int(limit * 1.15) + 2
    queues = [[spec, None] for spec in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            if listing_out_of_time():          # leave the rest of the time for fetching what was found
                say(f"  {prefix}: stopped looking at half the time limit")
                queues = []
                break
            spec, files = q
            if files is None:
                try:
                    files = [(t, sub) for t, sub in spec_files(s, spec) if t not in seen]
                except RuntimeError as e:      # Commons kept refusing: keep what was found and stop asking
                    say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                    queues = []
                    break
                random.Random(spec["category"]).shuffle(files)
                say(f"Commons {spec['category']}: {len(files)} files")
            batch, q[1] = files[:share * 2], files[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            subs = dict(batch)
            try:
                entries = mech_entries(s, [t for t, _ in batch], drawings=drawings)
                cats = file_categories(s, [e[0] for e in entries]) if extra else {}
            except RuntimeError as e:          # Commons kept refusing: keep what was found and stop asking
                say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                queues = []
                break
            got = 0
            for title, url, credit, text, _ in entries:
                if got >= share or title in seen:
                    continue
                words = NOT_A_CHILD.sub(" ", f"{title} {text} {' '.join(cats.get(title, []))}")
                text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
                if NUDE.search(words) or NOT_SHOWN.search(words):
                    considered(title, url, "its words are about nudity, underwear or swimwear")
                    continue
                place = where(spec["place"], spec.get("kind")) if spec["place"] else where(PLACES.get(title, ""))
                facts = {"commons_category": subs.get(title) or spec["category"],
                         "commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0]}
                rows = []
                if spec["answer"]:
                    rows.append({"question": spec["question"], "answer": spec["answer"], "credit": credit,
                                 "facts": facts, **place})
                if extra:
                    rows += [dict(r, credit=credit, **place) for r in extra(title, cats.get(title, []), spec, place)]
                if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text) and (rows or extra):
                    rows.append({"question": DESCRIBE_Q, "answer": text, "credit": credit, **place})
                if not rows:
                    considered(title, url, "no answer: its categories name nothing this pack asks about, and it has "
                                           "no English caption")
                    continue
                seen.add(title)
                items.append((file_name(prefix, title), url, [mark_child(r, words) for r in rows]))
                got += 1
            if not q[1]:
                queues.remove(q)
    random.Random(prefix + "-order").shuffle(items)
    return items[:want]


def commons_pack(specs, limit, prefix, extra=None):
    """us_commons, then the pictures downloaded (patiently), as pack entries."""
    return with_twins(commons_fetch(us_commons(specs, limit, prefix, extra))[:limit])


# ----------------------------------------------------------------- commons_us_homes

HOUSE_STYLES = [
    ("Victorian houses in the United States", "It is a Victorian house, a style of the later 1800s, often with "
                                              "decorated woodwork, bay windows and steep roofs."),
    ("Colonial Revival houses in the United States", "It is a Colonial Revival house, built in the style of early "
                                                     "American colonial houses."),
    ("Greek Revival houses in the United States", "It is a Greek Revival house, usually with columns and a "
                                                  "triangular gable like an ancient Greek temple."),
    ("Tudor Revival houses in the United States", "It is a Tudor Revival house, with steep gables and often "
                                                  "half-timbering (dark wooden beams on light walls)."),
    ("Italianate houses in the United States", "It is an Italianate house, with a low roof, wide eaves held up by "
                                               "brackets and tall windows."),
    ("Federal style houses in the United States", "It is a Federal-style house, a plain, balanced style of about "
                                                  "1780 to 1830."),
    ("Log cabins in the United States", "It is a log cabin."),
    ("Mobile homes in the United States", "It is a mobile home (a manufactured home)."),
    ("Townhouses in the United States", "It is a townhouse (a row house), joined to the houses on each side."),
    ("Row houses in the United States", "It is a row house, joined to the houses on each side."),
    ("Sod houses", "It is a sod house, built of blocks of turf, as settlers built them on the prairies."),
    ("Dogtrot houses", "It is a dogtrot house: two rooms under one roof with an open breezeway between them."),
    ("Shotgun houses", "It is a shotgun house: a narrow house one room wide, its rooms one behind another."),
    ("Adobe houses in the United States", "It is an adobe house, built of sun-dried mud bricks."),
    ("Split-level houses", "It is a split-level house, its floors at staggered heights."),
    ("Farmhouses in the United States", "It is a farmhouse."),
    ("Bungalows in the United States", "It is a bungalow, a small, low house of one storey or one and a half."),
    ("Prairie School houses", "It is a Prairie School house, low and long with wide overhanging eaves."),
]
ROOM_CATEGORIES = [("Home kitchens in the United States", "This is a kitchen."),
                   ("Kitchens in the United States", "This is a kitchen."),
                   ("Living rooms in the United States", "This is a living room."),
                   ("Bedrooms in the United States", "This is a bedroom."),
                   ("Bathrooms in the United States", "This is a bathroom."),
                   ("Dining rooms in the United States", "This is a dining room."),
                   ("Interiors of houses in the United States", None)]


def home_specs():
    """The commons_us_homes categories: houses in each state, house styles and rooms."""
    specs = [us_spec(f"Houses in {state}", WHAT_Q, f"This is a house in {state}.", f"{state}, USA", 1)
             for state in STATES + ["Washington, D.C."]]
    specs += [us_spec(c, HOUSE_Q, a, "USA", 1) for c, a in HOUSE_STYLES]
    specs += [us_spec(c, ROOM_Q, a, "USA", 1) for c, a in ROOM_CATEGORIES]
    return specs


def build_commons_us_homes(limit):
    """The Commons US houses and rooms pack."""
    return commons_pack(home_specs(), limit, "ushome")


# ----------------------------------------------------------------- commons_us_streets

US_CITIES = [("New York City", "New York"), ("Los Angeles", "California"), ("Chicago", "Illinois"),
             ("Houston", "Texas"), ("Phoenix, Arizona", "Arizona"), ("Philadelphia", "Pennsylvania"),
             ("San Antonio", "Texas"), ("San Diego", "California"), ("Dallas", "Texas"),
             ("San Francisco", "California"), ("Seattle", "Washington"), ("Boston", "Massachusetts"),
             ("Denver", "Colorado"), ("Washington, D.C.", ""), ("Atlanta", "Georgia"), ("Miami", "Florida"),
             ("New Orleans", "Louisiana"), ("Nashville, Tennessee", "Tennessee"), ("Portland, Oregon", "Oregon"),
             ("Las Vegas", "Nevada"), ("Detroit", "Michigan"), ("Minneapolis", "Minnesota"),
             ("Austin, Texas", "Texas"), ("Baltimore", "Maryland"), ("Pittsburgh", "Pennsylvania"),
             ("St. Louis", "Missouri"), ("Kansas City, Missouri", "Missouri"), ("Salt Lake City", "Utah"),
             ("Honolulu", "Hawaii"), ("Anchorage, Alaska", "Alaska"), ("Cleveland", "Ohio"), ("Cincinnati", "Ohio"),
             ("Milwaukee", "Wisconsin"), ("Albuquerque, New Mexico", "New Mexico"), ("Charleston, South Carolina",
                                                                                    "South Carolina"),
             ("Savannah, Georgia", "Georgia"), ("Memphis, Tennessee", "Tennessee"), ("Louisville, Kentucky",
                                                                                    "Kentucky"),
             ("Richmond, Virginia", "Virginia"), ("Providence, Rhode Island", "Rhode Island")]
PEOPLE_CATEGORIES = ["Pedestrians in the United States", "Pedestrians in New York City",
                     "Street photography in the United States", "Street Style (fashion)", "Streetwear"]
# Clothing categories: "Men wearing baseball caps", "Women in jeans in New York City", "People with umbrellas".
WEARING = re.compile(r"^(?P<who>men|women|people|persons|girls|boys|teenagers|young men|young women|elderly men|"
                     r"elderly women|old men|old women) (?:wearing|in) (?P<what>.+?)"
                     r"(?: (?:in|at|of|on|from|by|during) .+)?$", re.I)
WHO = {"men": ("A man", False), "women": ("A woman", False), "people": ("People", True), "persons": ("People", True),
       "girls": ("A girl", False), "boys": ("A boy", False), "teenagers": ("A teenager", False),
       "young men": ("A young man", False), "young women": ("A young woman", False),
       "elderly men": ("An older man", False), "old men": ("An older man", False),
       "elderly women": ("An older woman", False), "old women": ("An older woman", False)}
# Clothes said in the plural even for one person, and words that are not clothes ("Men in suits" is; "Men in
# cars" is not).
PAIRS = re.compile(r"(jeans|trousers|pants|shorts|glasses|sunglasses|spectacles|leggings|tights|overalls|"
                   r"dungarees|boots|shoes|sneakers|sandals|gloves|mittens|clothes|clothing|earrings|"
                   r"headphones|earmuffs|suspenders|braces|sweatpants)$", re.I)
CLOTHES = re.compile(r"\b(hats?|caps?|beanies?|hoods?|hoodies?|jackets?|coats?|suits?|ties?|bow ties?|shirts?|"
                     r"t-shirts?|blouses?|sweaters?|jumpers?|cardigans?|vests?|waistcoats?|dress(es)?|skirts?|"
                     r"kilts?|jeans|trousers|pants|shorts|leggings|uniforms?|scarf|scarves|shawls?|headscarf|"
                     r"headscarves|hijabs?|turbans?|kippot|kippah|yarmulkes?|veils?|glasses|sunglasses|"
                     r"spectacles|masks?|face masks?|boots|shoes|sneakers|sandals|gloves|mittens|backpacks?|"
                     r"bags?|handbags?|umbrellas?|headphones|earmuffs|helmets?|aprons?|overalls|costumes?|"
                     r"raincoats?|ponchos?|tracksuits?|sweatshirts?|flannel|plaid|denim|leather|fur|cowboy|"
                     r"stetsons?|fedoras?|berets?|bandanas?|jerseys?|saris?|kimonos?|robes?|tank tops?|"
                     r"polo shirts?|sportswear|streetwear|black|white|red|blue|green|yellow|pink|purple|brown|"
                     r"grey|gray|orange)\b", re.I)


def singular(what):
    """A clothing category's words for one person: "baseball caps" -> "a baseball cap", "jeans" -> "jeans",
    "black dresses" -> "a black dress"."""
    what = what.strip().lower()
    if PAIRS.search(what) or re.search(r"(clothing|wear|denim|leather|fur|plaid|flannel|uniforms)$", what):
        return what
    if re.search(r"(ses|xes|ches|shes)$", what):
        what = what[:-2]
    elif re.search(r"ves$", what) and what.endswith(("scarves", "headscarves")):
        what = what[:-3] + "f"
    elif what.endswith("s") and not what.endswith("ss"):
        what = what[:-1]
    return f"{article(what)} {what}"


def wearing_rows(title, categories, spec, place):
    """ "What is the person wearing?" from the clothing categories a file sits in: "A man in this picture is wearing
    a baseball cap and jeans." (several kinds of person: one sentence each)."""
    said = collections.OrderedDict()
    for c in categories:
        m = WEARING.match(c)
        if not m or not CLOTHES.search(m.group("what")) or NOT_SHOWN.search(c):
            continue
        who = m.group("who").lower()
        said.setdefault(who, [])
        what = m.group("what").lower() if WHO[who][1] else singular(m.group("what"))
        if what not in said[who]:
            said[who].append(what)
    sentences = []
    for who, things in said.items():
        name, many = WHO[who]
        sentences.append(f"{name} in this picture {'are' if many else 'is'} wearing {listed(things[:4])}.")
    rows = []
    if sentences:
        rows.append({"question": WEAR_Q, "answer": " ".join(sentences[:3]), "facts": {"commons_categories": [
            c for c in categories if WEARING.match(c)]}})
    return rows


def street_specs():
    """The commons_us_streets categories: the streets of US cities (the city as the place) and people on US streets
    (no fixed answer: their clothing categories and captions give the rows)."""
    specs = []
    for city, state in US_CITIES:
        place = place_name(city.split(",")[0], state, "USA") if state else "Washington, D.C., USA"
        specs.append(us_spec(f"Streets in {city}", PLACE_Q, f"This is a street in {place}.", place, 1))
    for c in PEOPLE_CATEGORIES:
        place = "New York City, New York, USA" if "New York" in c else "USA" if "United States" in c else ""
        specs.append(us_spec(c, WEAR_Q, None, place, 1))
    return specs


def build_commons_us_streets(limit):
    """The Commons US streets and street fashion pack."""
    return commons_pack(street_specs(), limit, "usstreet", extra=wearing_rows)


# ----------------------------------------------------------------- commons_us_cars

CAR_MAKES = ("Acura|Alfa Romeo|AMC|American Motors|Aston Martin|Audi|Austin|Bentley|BMW|Buick|Cadillac|Checker|"
             "Chevrolet|Chrysler|Citroën|DeSoto|Dodge|Edsel|Ferrari|Fiat|Ford|Genesis|GMC|Honda|Hudson|Hummer|"
             "Hyundai|Infiniti|International Harvester|Jaguar|Jeep|Kaiser|Kia|Lamborghini|Land Rover|Lexus|"
             "Lincoln|Lucid|Maserati|Mazda|Mercedes-Benz|Mercury|Mini|Mitsubishi|Nash|Nissan|Oldsmobile|Packard|"
             "Plymouth|Polestar|Pontiac|Porsche|Ram|Rambler|Rivian|Rolls-Royce|Saab|Saturn|Scion|Studebaker|"
             "Subaru|Suzuki|Tesla|Toyota|Tucker|Volkswagen|Volvo|Willys")
MODEL = re.compile(rf"^(?:(?P<year>(?:19|20)\d\d) )?(?P<make>{CAR_MAKES})\b(?P<rest>.*)$")
NOT_A_MODEL = re.compile(r"\b(in|at|of|by|on|from|automobiles|vehicles|museum|logos?|emblems?|badges?|dealers?|"
                         r"dealerships?|license|licence|plates?|interiors?|dashboards?|engines?|wheels?|"
                         r"advertisements?|photographs?|taken with|seats?|steering|street|avenue|road|boulevard|"
                         r"drive|highway|county|city|park|station|building|center|centre)\b", re.I)
COLOURS = re.compile(r"^(?P<colour>black|white|silver|grey|gray|red|blue|green|yellow|orange|brown|beige|gold|"
                     r"purple|pink|maroon|turquoise|tan) (automobiles|cars|pickup trucks|SUVs)\b", re.I)
CAR_PLURALS = re.compile(r"\b(convertibles|sedans|coupes|wagons|station wagons|pickups|pickup trucks|hatchbacks|"
                         r"roadsters|limousines|vans|hardtops)\b", re.I)


def car_model(categories):
    """The model category a car photo sits in, as said in a sentence ("1966 Ford Mustang convertible", "Ford
    Mustang (first generation)"), preferring one with a year; ""."""
    found = []
    for c in categories:
        m = MODEL.match(c)
        if not m or NOT_A_MODEL.search(m.group("rest")) or len(c.split()) > 8 or not m.group("rest").strip():
            continue
        name = CAR_PLURALS.sub(lambda x: x.group(0)[:-1], c)       # "Ford Mustang convertibles" -> "convertible"
        name = re.sub(r"(?<= [a-z]{3})([a-z]*[^s])s$", r"\1", name)   # "Jeep ambulances" -> "Jeep ambulance"
        found.append((0 if m.group("year") else 1, len(name), name))
    return min(found)[2] if found else ""


def car_rows(title, categories, spec, place):
    """ "What car is this?" from the model category and "What colour is the car?" from the colour category a file
    sits in; none when no model category is there."""
    model = car_model(categories)
    if not model:
        return []
    rows = [{"question": CAR_Q, "answer": f"It is {article(model)} {model}.",
             "facts": {"commons_categories": [c for c in categories if MODEL.match(c) or COLOURS.match(c)]}}]
    colours = {m.group("colour").lower().replace("gray", "grey") for m in map(COLOURS.match, categories) if m}
    if len(colours) == 1:
        rows.append({"question": COLOUR_Q, "answer": f"The car is {colours.pop()}."})
    return rows


def car_specs():
    """The commons_us_cars categories: automobiles in each state, with their city and kind subcategories."""
    return [us_spec(f"Automobiles in {state}", CAR_Q, None, f"{state}, USA", 1) for state in STATES] + \
        [us_spec("Automobiles in New York City", CAR_Q, None, "New York City, New York, USA", 1),
         us_spec("Pickup trucks in the United States", CAR_Q, None, "USA", 1),
         us_spec("Police automobiles in the United States", CAR_Q, None, "USA", 1)]


def build_commons_us_cars(limit):
    """The Commons US cars pack: only photos whose categories name a model."""
    items = us_commons(car_specs(), int(limit * 1.3) + 4, "uscar", extra=car_rows)
    items = [(n, u, rows) for n, u, rows in items if any(r["question"] == CAR_Q for r in rows)]
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- inaturalist_us

INAT = "https://api.inaturalist.org/v1/"


def inat_states(s):
    """{state name: iNaturalist place id} for the 50 states (each looked up by name, one request a second)."""
    out = {}
    for state in STATES:
        if listing_out_of_time():
            break
        try:
            data = s.get(INAT + "places/autocomplete", params={"q": state, "per_page": 20}, timeout=60).json()
        except Exception:  # noqa: BLE001 - that state is left out
            continue
        for p in data.get("results") or []:
            if p.get("admin_level") == 10 and 1 in (p.get("ancestor_place_ids") or []) \
                    and clean(p.get("name")).lower() == state.lower():
                out[state] = p["id"]
                break
        time.sleep(1.1)
    return out


def build_inaturalist_us(limit):
    """iNaturalist research-grade observations in each US state whose photo is CC0 or CC BY (credit kept): the
    states and the groups of living things take turns, one page of observations each."""
    s, items, seen = session(), [], set()
    states = inat_states(s)
    say(f"iNaturalist: {len(states)} states found")
    rng = random.Random(1776)
    pairs = [(state, group, question) for state in states for group, question in INAT_GROUPS]
    rng.shuffle(pairs)
    per_pair = max(2, math.ceil(limit * 1.15 / max(1, len(pairs))))
    for state, group, question in pairs:
        if len(items) >= limit * 1.15:
            break
        if listing_out_of_time():
            say("  iNaturalist: stopped looking at half the time limit")
            break
        try:
            data = s.get(INAT + "observations", timeout=60, params={
                "quality_grade": "research", "photo_license": "cc0,cc-by", "iconic_taxa": group,
                "place_id": states[state], "per_page": 50, "page": rng.randint(1, 10), "order_by": "id"}).json()
        except Exception:  # noqa: BLE001 - next pair
            continue
        got = 0
        for o in data.get("results") or []:
            taxon, photos = o.get("taxon") or {}, o.get("photos") or []
            photo = next((ph for ph in photos if (ph.get("license_code") or "") in ("cc0", "cc-by")), None)
            if got >= per_pair or not photo or not taxon.get("name") or o["id"] in seen:
                continue
            seen.add(o["id"])
            latin, common = taxon["name"], clean(taxon.get("preferred_common_name"))
            answer = f"This is {article(common)} {common} ({latin})." if common else f"This is {latin}."
            login = (o.get("user") or {}).get("login", "an iNaturalist user")
            place = f"{state}, USA"
            credit = (f"Photo by {login} on iNaturalist, {photo['license_code'].upper()}, "
                      f"https://www.inaturalist.org/observations/{o['id']}")
            facts = {"taxon_id": taxon.get("id"), "rank": taxon.get("rank"), "observed_on": o.get("observed_on")}
            rows = [{"question": question, "answer": answer, "credit": credit, "facts": facts, **where(place)},
                    {"question": "Where was this photo taken?", "answer": f"It was taken in {place}.",
                     "credit": credit, **where(place)}]
            items.append((f"inatus-{photo['id']}.jpg", photo["url"].replace("/square.", "/large."), rows))
            got += 1
        time.sleep(1.1)                    # iNaturalist asks for at most about one request a second
    rng.shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.3)[:limit]
    say(f"inaturalist_us: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- commons_us_money

DOLLAR_WORDS = {"1": "one-dollar", "2": "two-dollar", "5": "five-dollar", "10": "ten-dollar", "20": "twenty-dollar",
                "50": "fifty-dollar", "100": "hundred-dollar", "500": "five-hundred-dollar",
                "1000": "thousand-dollar"}
COINS = [("United States cents", "a US one-cent coin (a penny)"), ("United States nickels", "a US five-cent coin "
                                                                                           "(a nickel)"),
         ("United States dimes", "a US ten-cent coin (a dime)"), ("United States quarters", "a US 25-cent coin "
                                                                                           "(a quarter)"),
         ("Half dollar (United States)", "a US half-dollar coin (50 cents)"),
         ("Dollar coins of the United States", "a US one-dollar coin")]


def money_specs():
    """The commons_us_money categories: banknotes by denomination and coins by name."""
    specs = [us_spec(f"{n} United States dollar banknotes", MONEY_Q,
                     f"This is a US {word} bill (a {n}-dollar banknote).", "USA", 1, "origin")
             for n, word in DOLLAR_WORDS.items()]
    specs += [us_spec(c, MONEY_Q, f"This is {name}.", "USA", 1, "origin") for c, name in COINS]
    return specs


def build_commons_us_money(limit):
    """The Commons US banknotes and coins pack."""
    return commons_pack(money_specs(), limit, "usmoney")


# ----------------------------------------------------------------- us_road_signs

MUTCD = re.compile(r"\b([A-Z]{1,2}\d{1,2}-\d{1,2}[A-Z]{0,2}(?:\([A-Z0-9]{1,3}\))?)(?=[\s_.)(-]|$)")
QUOTED = re.compile(r"[\"“”']([^\"“”']{2,60})[\"“”']")
SIGN_NOISE = re.compile(r"\b(custom|hand-coded|from the manual of uniform traffic control devices|in the united states|"
                        r"of the united states|united states|u\.s\.|svg|png|drawn|made|version|file)\b", re.I)
SIGN_PHOTOS = [("Stop signs in the United States", "It is a stop sign: stop completely, then go on when it is "
                                                   "safe."),
               ("Yield signs in the United States", "It is a yield sign: give way to traffic on the road you are "
                                                    "joining."),
               ("Speed limit signs in the United States", "It is a speed limit sign: the highest speed allowed, in "
                                                          "miles per hour."),
               ("Pedestrian crossing signs in the United States", "It is a pedestrian crossing sign: people may be "
                                                                  "crossing the road here.")]


def sign_meaning(title, text):
    """(MUTCD number, what the sign says) of a US sign drawing, from its file name and its own description:
    "MUTCD R3-32P.svg", "Plaque R3-32P 'No Cash' from the Manual ..." -> ("R3-32P", 'it reads "No Cash"');
    "FHWA bicycle lane sign.png", "Bicycle lane sign: diamond symbol with text ..." -> ("", "Bicycle lane sign").
    The words are "" when the description gives neither a quoted wording nor a short English name."""
    name = title.split(":", 1)[-1].rsplit(".", 1)[0]
    m = MUTCD.search(name) or MUTCD.search(text or "")
    number = m.group(1) if m else ""
    text = clean(text or "")
    quoted = QUOTED.search(text)
    if quoted and in_english(quoted.group(1) + " of the"):
        return number, f'it reads "{quoted.group(1).strip()}"'
    first = re.split(r"[:.;(]|, (?:a|an|the|which|located)\b", text)[0]
    first = clean(SIGN_NOISE.sub(" ", first)).strip(" ,-")
    if not first or len(first.split()) > 10 or not in_english(first + " of the") or not re.search(r"[a-z]", first):
        return number, ""
    return number, first[:1].upper() + first[1:]


def build_us_road_signs(limit):
    """US road sign drawings (about two thirds: each with its MUTCD number and its description, set black on white)
    and photos of the most common US signs."""
    s = session()
    drawings = int(limit * 0.65) + 1
    titles = []
    for sub in [""] + [c.split(":", 1)[-1] for c in commons_members(s, "Diagrams of road signs of the United States",
                                                                   "subcat")]:
        if listing_out_of_time():
            break
        if sub and re.search(r"proposed|unofficial|non-compliant|historic|by (state|city|year)", sub, re.I):
            continue
        titles += commons_members(s, sub or "Diagrams of road signs of the United States", "file")
    titles = [t for t in dict.fromkeys(titles) if t.lower().endswith((".svg", ".png"))]
    random.Random(1935).shuffle(titles)
    say(f"US road sign drawings: {len(titles)} files")
    items = []
    for title, url, credit, text, _ in mech_entries(s, titles[:int(drawings * 1.6) + 10], drawings=True):
        if len(items) >= drawings * 1.1 or listing_out_of_time():
            break
        number, meaning = sign_meaning(title, text)
        if not meaning:
            continue
        answer = (f"It is a US road sign; {meaning}." if meaning.startswith("it reads") else
                  f"It is a US road sign: {meaning}.") + (f" (MUTCD sign {number}.)" if number else "")
        items.append((file_name("ussign", title), url,
                      [{"question": SIGN_Q, "answer": answer, "credit": credit, "place": "USA",
                        "facts": {"mutcd": number} if number else {}}]))
    out = []
    for name, data, rows in commons_fetch(items, raw=True):
        try:
            picture = symbol_picture(data, side=320)
        except Exception:  # noqa: BLE001 - a drawing that cannot be read is left out
            continue
        jpeg = io.BytesIO()
        picture.save(jpeg, "JPEG", quality=92)
        out.append((name, jpeg.getvalue(), rows))
    out = with_twins(out[:drawings])
    photos = [us_spec(c, SIGN_Q, a, "USA", 1) for c, a in SIGN_PHOTOS]
    out += commons_pack(photos, max(1, limit - count_pictures(out)), "ussignphoto")
    return out


# ----------------------------------------------------------------- commons_packaging

PACKAGING = [("Packaged food", "This is packaged food.", 1), ("Beverage cans", "This is a drink can.", 1),
             ("Plastic bottles", "This is a plastic bottle.", 1), ("Glass bottles", "This is a glass bottle.", 0),
             ("Egg cartons", "This is an egg carton.", 1), ("Milk retail containers", "This is a milk container.", 1),
             ("Cardboard food boxes", "This is a cardboard food box.", 1),
             ("Candy packaging", "This is sweets (candy) packaging.", 1),
             ("Blister packs", "This is a blister pack: items sealed in clear plastic bubbles on a card.", 1),
             ("Tetra Pak", "This is a drinks carton (Tetra Pak).", 1),
             ("Plastic bags", "This is a plastic bag.", 0), ("Shopping bags", "This is a shopping bag.", 1),
             ("Supermarket shelves", "This is a supermarket shelf, stocked with products.", 1),
             ("Products in supermarkets", "These are products on sale in a supermarket.", 1)]
SHOPS = [("Supermarkets in the United States", "This is a supermarket in the USA."),
         ("Grocery stores in the United States", "This is a grocery store in the USA.")]


def packaging_specs():
    """The commons_packaging categories."""
    specs = [us_spec(c, WHAT_Q, a, "", d) for c, a, d in PACKAGING]
    specs += [us_spec(c, PLACE_Q, a, "USA", 1) for c, a in SHOPS]
    return specs


def build_commons_packaging(limit):
    """The Commons packaging, packaged goods and US shops pack."""
    return commons_pack(packaging_specs(), limit, "pack")


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
US_PACKS = {
    "loc_habs_houses": (build_loc_habs_houses,
                        "Historic American Buildings Survey (HABS), Library of Congress, Prints and Photographs "
                        "Division, https://www.loc.gov/collections/historic-american-buildings-landscapes-and-"
                        "engineering-records/ : no known restrictions on images made by the U.S. Government "
                        "(https://www.loc.gov/rr/print/res/114_habs.html). Answers from each photo's survey caption "
                        "and the record's subject headings, place and building dates."),
    "commons_us_homes": (build_commons_us_homes, COMMONS_CREDIT.format(what="categories of US houses, house styles "
                                                                            "and rooms")),
    "commons_us_streets": (build_commons_us_streets, COMMONS_CREDIT.format(
        what="categories of streets in US cities, pedestrians and street fashion (what people wear from the "
             "clothing categories each photo sits in)")),
    "commons_us_cars": (build_commons_us_cars, COMMONS_CREDIT.format(
        what="categories of automobiles in each US state (the model and colour from the categories each photo "
             "sits in)")),
    "inaturalist_us": (build_inaturalist_us,
                       "iNaturalist (https://www.inaturalist.org) research-grade observations in each US state: "
                       "photos CC0 or CC BY, each photographer credited below; names by the iNaturalist community."),
    "commons_us_money": (build_commons_us_money, COMMONS_CREDIT.format(
        what="categories of US banknotes by denomination and US coins (the designs are US government work)")),
    "us_road_signs": (build_us_road_signs,
                      "Wikimedia Commons: Category:Diagrams of road signs of the United States (MUTCD signs, public "
                      "domain as US government work or simple shapes; drawings set black on white) and photo "
                      "categories of US road signs (CC0, public domain or CC BY), each with its author and file "
                      "page below. Meanings from each drawing's own description. https://commons.wikimedia.org"),
    "commons_packaging": (build_commons_packaging, COMMONS_CREDIT.format(
        what="categories of packaged goods, packaging, supermarket shelves and US supermarkets and grocery stores")),
}

# How many pictures a full build takes from each (kept so every pack finishes well within about four hours on
# GitHub's machines: Commons answers about one picture a second, the Library of Congress one item in two seconds).
US_LIMITS = {
    "loc_habs_houses": 3000,      # 27 search words, up to three photos from each of about 1,000 homes
    "commons_us_homes": 4000,     # 51 state categories, 18 house styles, 7 room categories
    "commons_us_streets": 3000,   # 40 cities' street categories and 5 people categories
    "commons_us_cars": 2500,      # 50 states; only photos whose categories name a model
    "inaturalist_us": 5000,       # 50 states x 10 groups
    "commons_us_money": 1200,     # 9 banknote denominations and 6 coins
    "us_road_signs": 2000,        # about 1,300 drawings with a description, and four photo categories
    "commons_packaging": 2500,    # 14 packaging categories and 2 shop categories
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one US pack builder.")
    parser.add_argument("key", choices=sorted(US_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = US_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"places: " + ", ".join(f"{p} {n}" for p, n in places.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
