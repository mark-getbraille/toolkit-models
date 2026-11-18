"""Pack builders for WORKPLACES, FARMS and BUILDING MECHANICAL SYSTEMS, mostly in the United States and Canada:
  (A) work: modern workplaces and light industry: factories, warehouses, loading and storage (pallets, pallet jacks,
      racking, conveyors, forklifts, hand trucks), machine shops and workshops, car repair and tyre shops, overhead
      and gantry cranes, scissor and boom lifts, and safety equipment in use (hard hats, respirators, safety boots);
  (B) farm: modern farming: tractors (by state and province, and by maker), combine harvesters, balers, cultivators,
      manure spreaders, hay rakes and wagons, potato and cotton harvesters, grain bins, silos, grain dryers and
      elevators, centre-pivot irrigation, milking parlours and dairy farms, barns, feedlots, chicken coops,
      greenhouses and farm sheds;
  (C) mech: the machinery of a building: furnaces, boilers, heat pumps, air conditioner condensers, air handlers,
      ducts and vents, range hoods and exhaust fans, heat-recovery ventilators, water heaters, well pumps and pressure
      tanks, water softeners, sump pumps, septic tanks, electrical panels and meters, standby generators, propane and
      heating-oil tanks, chimneys, radiators and baseboard heaters. (Thermostats are elsewhere: home_packs and
      us_modern_packs.)

Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name,
JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" (the state or province a
Commons category names, "Iowa, USA"; else the country at the photo's camera coordinates) and "facts" (the Commons
category the picture was found in). A picture with more than one question comes once with its JPEG and then again as
(None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Every answer is a fixed sentence written here from the source's own words, never by an AI model and never guessed:
  - the name of the Wikimedia Commons category a photo sits in ("Grain dryers" -> "This is a grain dryer: a farm
    machine that dries harvested grain with heated air so it keeps in storage."), with one plain line on what the
    thing does;
  - the state or province the category names ("Tractors in Iowa" -> "Where was this photo taken?" "It was taken in
    Iowa, USA.");
  - the file's own English caption or description, as "Describe this picture.", when it is a real, respectful one.
Questions: "What is this?", "What kind of machine is this?", "What kind of place is this?", "What is happening
here?", "Where was this photo taken?" and "Describe this picture.". A part question ("What is this part of the
furnace?") is not asked: no Commons category of furnace or boiler parts was found that says which part a photo shows.

Some categories have no fixed answer (CAPTION_ONLY: "Agriculture in Iowa", "Industry in Canada" ...): their photos
are used only with their own caption; a photo there that passes every check but has no usable caption is SET ASIDE
for a description (build_packs.needs_description), not thrown away.

Modern only: files whose words give a year before 1990, a decade before the 1990s, or say "antique", "vintage",
"museum", "restored" or "historic" are left out, and so are files dated before 1990 (us_modern_packs.recent_only), so
these show today's machines and buildings (old barns and grain elevators that still stand are kept when their photo is
recent and their words do not say "historic").

Safety (packs/SOURCE-RULES.md): no sexual content (NUDE and us_packs.NOT_SHOWN words leave a file out); files whose
words name a child are LEFT OUT (farm and factory photos of children can show child labour or danger); files whose
words name an injury, a death or an accident are left out. In the farm and building-mechanical packs, files whose
words name a person are left out too (device_packs.PERSON), so those two packs show machines and buildings and may be
used for picture-making. The workplace pack keeps workers at work, so it is for describing only (the kit's
PEOPLE_AND_BODILY_PACK_KEYS), and so is the NRCS pack.

The packs (all open; every file's licence checked one by one from its own Commons page: CC0, public domain, CC BY,
or an open government licence that allows any use with credit (OGL-ON, OGL-Canada, OGL UK) or Flickr Commons' "No
known copyright restrictions" (is_free); never BY-SA, NC or ND, which are the kit's work_commons_sa and
farm_mech_commons_sa; captions are Commons structured data,
CC0: "All structured data from the file namespace is available under the Creative Commons CC0 License",
https://commons.wikimedia.org/wiki/Commons:Structured_data; checked November 2026):
  work_commons_workplaces   Commons categories of US and Canadian workplaces and of workplace machines and safety
                            equipment (WORK_SPECS).
  farm_commons_equipment    Commons categories of farm machines, farm buildings and livestock handling, US states
                            and Canadian provinces where Commons has them (FARM_SPECS).
  mech_commons_building     Commons categories of building heating, cooling, ventilation, water, drainage, power and
                            fuel equipment (MECH_SPECS).
  farm_usda_nrcs            Commons "Natural Resources Conservation Service": photos by the US Department of
                            Agriculture's NRCS (copied to Commons from its Flickr streams), US government work, public
                            domain ("works of the United States Government are in the public domain", the file's
                            {{PD-USGov-USDA-NRCS}} tag; each file's licence is checked all the same), with NRCS's own
                            caption: conservation on working farms and ranches (cover crops, no-till planting,
                            irrigation, grazing, fencing, manure storage, high tunnels). A photo whose caption is under
                            six English words is set aside for a description.

What already existed and is left alone (other packs): commons_land_industry (worldwide top-level Commons categories:
Tractors, Combine harvesters, Balers, Seed drills, Greenhouses, Center pivot irrigation, Grain silos, Grain elevators,
Milking machines, Cattle feedlots, Factories, Assembly lines, Warehouses, Forklifts, Welding, Workshops, Lathes ...);
loc_haer (historic engineering); usda_ars (ARS research photos); commons_us_agencies (a random sample of the USDA,
FEMA, HUD and Forest Service Flickr copies); commons_machine_parts (Water heating devices, Tankless water heaters,
Air conditioners, Split type air conditioners, Heat pumps, Air source heat pumps, Sheet metal and finned-tube
radiators, valves, pumps, Automobile repair shops); commons_devices (Engine-generators, Air conditioners, Dehumidifiers,
Humidifiers, Electric heaters, Lawn tractors); commons_things (Workbenches, Ladders, Toolboxes, Circuit breakers);
safety_training and commons_safety_photos (Personal protective equipment, High-visibility clothing, OSHA, NIOSH).
None of those categories is asked for again here; the US and Canadian subcategories asked for here can share some
files with a worldwide category whose subcategories commons_land_industry also reads (it reads at most 30 of them),
so a few photos may be in both packs, with different questions.

    python packs/work_farm_mech_packs.py farm_commons_equipment --limit 8     (prints a few rows: a quick check)
"""

import collections
import json
import math
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from food_packs import with_twins, count_pictures, commons_members, credit_licence, commons_get, commons_description
from home_packs import commons_fetch, file_name, NUDE, NOT_RESPECTFUL, FIRST_PERSON
from expression_packs import CHILD, child_count
from mechanical_packs import MECH_FREE, OTHER_WORDS, PLACES, JUST_A_RECORD, NOT_A_CHILD, NOT_A_PHOTO
from us_packs import NOT_SHOWN, US_NOT_THE_THING
from us_modern_packs import NOT_MODERN, recent_only, agency_caption
from land_industry_packs import US_STATE_CODES, INJURY, looks_english, ENGLISH_WORDS
from device_packs import PERSON
from places import where, country_at

WHAT_Q = "What is this?"
MACHINE_Q = "What kind of machine is this?"
PLACE_Q = "What kind of place is this?"
DOING_Q = "What is happening here?"
WHERE_Q = "Where was this photo taken?"
DESCRIBE_Q = "Describe this picture."
QUESTIONS = {"thing": WHAT_Q, "machine": MACHINE_Q, "place": PLACE_Q, "doing": DOING_Q}

US_STATES = sorted(US_STATE_CODES.values(), key=len, reverse=True)
PROVINCES = ["British Columbia", "Alberta", "Saskatchewan", "Manitoba", "Ontario", "Quebec", "New Brunswick",
             "Nova Scotia", "Prince Edward Island", "Newfoundland and Labrador", "Yukon", "Northwest Territories",
             "Nunavut"]
# Accidents and damage (with land_industry_packs.INJURY: injuries and deaths): such files are left out here.
ACCIDENT = re.compile(r"\b(accidents?|crash\w*|collapsed?|explosions?|exploded|fires? damage|burn(ed|t)[- ]out|"
                      r"wreck\w*|rollover|overturned|tipped over|derail\w*)\b", re.I)
# More words that show people at work (device_packs.PERSON has the general ones), and US military public-affairs
# photos, which nearly always show service members: left out of the packs without people.
PEOPLE_AT_WORK = re.compile(r"\b(volunteers?|technicians?|engineers?|plumbers?|electricians?|inspectors?|staff|"
                            r"employees?|crews?|soldiers?|sailors?|airm[ae]n|marines?|seabees?|specialists?|team|"
                            r"members?|students?|contractors?|installers?|homeowners?|residents?|officials?)\b|"
                            r"\bUS (Navy|Army|Air Force|Marine Corps)\b|"
                            r"\bU\.S\. (Navy|Army|Air Force|Marines?)\b", re.I)
# File names that show a document, sign or label about the thing rather than the thing itself.
NOT_THE_THING_ITSELF = re.compile(r"\b(listings?|signs?|signboards?|labels?|leaflets?|flyers?|brochures?|documents?|"
                                  r"forms?|invoices?|screenshots?|screen ?shots?|instructions?|warning stickers?)\b",
                                  re.I)
# Old archive photos filed under today's categories (the US National Archives' and Library of Congress' Civil War,
# Farm Security Administration and Lewis Hine photos, some of child labour), and words of their era: left out.
OLD_ARCHIVE = re.compile(r"\b(NARA|Library of Congress|LOC|Mathew (Benjamin )?Brady|Lewis (Wickes )?Hine|Farm Security "
                         r"Administration|FSA|Office of War Information|OWI|WPA|Works Progress Administration|Civil "
                         r"War|Negro\w*|colored)\b")
# Archive boilerplate that is not a description of the picture.
BOILERPLATE = re.compile(r"general notes|when ordering a reproduction|requesting information|no known restrictions|"
                         r"rights advisory|call number|reproduction number|digital id|courtesy of|"
                         r"use (war and conflict )?number", re.I)
# More words that show children (expression_packs.CHILD has the general ones): school classes, youth groups.
CHILD_MORE = re.compile(r"\b(elementary|grade school|schoolchildren|school ?kids|(school|elementary|grade|"
                        r"kindergarten) class(es)?|classes of (students|children)|4-H|FFA|youth|scouts?|"
                        r"campers)\b", re.I)
# The caption-only categories' captions must say something: at least six words.
CAPTION_WORDS = 6


# ----------------------------------------------------------------- places from category names

def category_place(name):
    """The place a Commons category's name ends with, as a row's place: "Tractors in Iowa" -> "Iowa, USA", "Barns in
    Ontario" -> "Ontario, Canada", "... in the United States" -> "USA", "... in Canada" -> "Canada"; "" otherwise
    (a state name inside a longer place, "Kansas City", is not taken)."""
    m = re.search(r"\bin (the )?([A-Z][\w .'()-]+?)$", name or "")
    if not m:
        return ""
    where_ = m.group(2).strip()
    if where_ in ("United States", "United States of America", "USA", "US"):
        return "USA"
    if where_ == "Canada":
        return "Canada"
    if where_ in US_STATES or where_ == "Washington (state)":
        return f"{where_.replace(' (state)', '')}, USA"
    if where_ in PROVINCES:
        return f"{where_}, Canada"
    return ""


def where_row(row, place):
    """ "Where was this photo taken?" for a place that names a state or province (not a whole country: a category
    says only that the thing is somewhere in it), or None."""
    if "," not in place:
        return None
    return {"question": WHERE_Q, "answer": f"It was taken in {place}.", "credit": row["credit"],
            "facts": row.get("facts", {}), **where(place)}


# ----------------------------------------------------------------- free Commons files

# Open government licences that allow any use with credit (packs/SOURCE-RULES.md, "open"): Ontario's and Canada's
# Open Government Licences and the UK's ("OGL-ON", "OGL-Canada-2.0", "OGL v3.0"), and the Flickr Commons "No known
# copyright restrictions" files ("No restrictions"), as well as everything mechanical_packs.MECH_FREE takes.
OPEN_GOVERNMENT = re.compile(r"^(ogl\b|ogl-|open government licen[cs]e|no restrictions)", re.I)


def is_free(licence):
    """Whether a Commons file's licence name lets it into an open pack: CC0, public domain, CC BY, MIT or Apache, or
    an open government licence; never share-alike, non-commercial or no-derivatives."""
    if re.search(r"\b(SA|NC|ND)\b|-SA|-NC|-ND|non-?commercial", licence or "", re.I):
        return False
    return bool(MECH_FREE.match(licence or "") or OPEN_GOVERNMENT.match(licence or ""))


def free_entries(s, titles):
    """[(title, picture address, credit, caption or description, the raw description)] for Commons files whose
    licence is free (is_free), 50 files a request, as mechanical_packs.mech_entries (which takes the same files but
    not the open government licences). JPEG and PNG photos only; every file left out is noted with its reason. Where
    a file's page gives the camera's coordinates, the country is kept in PLACES."""
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 1280,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|GPSLatitude|"
                                                      "GPSLongitude",
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
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            if not is_free(licence):
                considered(p["title"], page, f"its licence ({licence or 'none given'}) is not CC0, public domain, "
                                             "CC BY or an open government licence (BY-SA files are in the kit's "
                                             "share-alike entries)")
                continue
            if info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                considered(p["title"], page, f"not a photo this pack takes ({info.get('mime') or 'no picture'})")
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            raw = clean((meta.get("ImageDescription") or {}).get("value"))
            text = commons_description(captions.get(f"M{p['pageid']}"),
                                       (meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}", text, raw))
            if meta.get("GPSLatitude") and meta.get("GPSLongitude"):
                PLACES[p["title"]] = country_at(clean(meta["GPSLatitude"].get("value")),
                                                clean(meta["GPSLongitude"].get("value")))
        time.sleep(1)
    return out


# ----------------------------------------------------------------- specs and the Commons listing

def spec(category, kind, answer, depth=0, place=""):
    """One Commons category: the kind of question ("thing", "machine", "place", "doing", or "caption" for a category
    whose photos are used only with their own caption), the fixed answer (None for "caption"), how deep to look (0:
    the category's own files; 1: and its subcategories'; 2: and theirs) and the place it names (else the place is
    read from the name of the category or subcategory a file is in)."""
    return {"category": category, "kind": kind, "answer": answer, "depth": depth,
            "place": place or category_place(category)}


def spec_files(s, sp, most_subcategories=60):
    """[(file title, the category it was found in)] for a spec: the category's files and, as deep as the spec says,
    its subcategories' (not those about something else, drawings or art). The subcategories are shuffled with
    pass_random, so a top-up pass looks at others first."""
    found = {}
    level = [sp["category"]]
    for depth in range(sp["depth"] + 1):
        nxt = []
        for category in level:
            if listing_out_of_time():
                break
            try:
                for t in commons_members(s, category, "file"):
                    if not NOT_A_PHOTO.search(t):
                        found.setdefault(t, category)
                if depth < sp["depth"]:
                    subs = [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")]
                    nxt += [c for c in subs if not NOT_A_PHOTO.search(c) and not US_NOT_THE_THING.search(c)
                            and not NOT_MODERN.search(c)]
            except RuntimeError as e:                   # Commons kept refusing: keep what was found
                say(f"  Commons {category}: stopped ({e})")
                return list(found.items())
        pass_random(sp["category"] + f"/{depth}").shuffle(nxt)
        level = nxt[:most_subcategories]
    return list(found.items())


def left_out_because(title, text, people_ok):
    """Why a Commons file is left out by its words, or "": nudity or underwear, a child, an injury or accident, an
    old or museum machine or an old archive photo, a file name that says it is a document, sign or label, and
    (unless people_ok) a person or people at work."""
    words = NOT_A_CHILD.sub(" ", f"{title} {text}")
    if NUDE.search(words) or NOT_SHOWN.search(words):
        return "its words are about nudity, underwear or swimwear, or it is an evidence photo"
    if CHILD.search(words) or CHILD_MORE.search(words):
        return "its words name a child (farm and work photos of children are left out)"
    if INJURY.search(words) or ACCIDENT.search(words):
        return "its words name an injury, a death or an accident"
    if NOT_MODERN.search(words) or OLD_ARCHIVE.search(words):
        return "its words say it is older than 1990, or a museum, antique or restored machine"
    if NOT_THE_THING_ITSELF.search(title.split(":", 1)[-1]):
        return "its file name says it shows a document, sign or label, not the thing itself"
    if not people_ok and (PERSON.search(words) or PEOPLE_AT_WORK.search(words)):
        return "its words name a person (this pack shows the machines and buildings themselves)"
    return ""


def in_english(text):
    """Whether a caption reads as English: Latin letters only, at least one common English word ("a", "in", "the"
    ...), and no more words of other languages ("der", "les", "het" ...) than English ones."""
    return bool(text) and looks_english(text) and len(OTHER_WORDS.findall(text)) <= len(ENGLISH_WORDS.findall(text))


def good_caption(text, title):
    """The file's caption or description when it is a real, respectful English one that says more than the file's
    name; else ""."""
    text = clean(text)
    if not text or JUST_A_RECORD.search(text) or BOILERPLATE.search(text) or not in_english(text) or \
            NOT_RESPECTFUL.search(text) or \
            FIRST_PERSON.search(text):
        return ""
    if not set(re.findall(r"[a-z]+", text.lower())) - set(re.findall(r"[a-z]+", title.lower())):
        return ""
    return text


def file_rows(sp, found_in, title, credit, text):
    """The rows of one Commons file (see the module docstring), or [] when it has none (a caption-only category and
    no usable caption)."""
    place = sp["place"] if "," in sp["place"] else (category_place(found_in) or sp["place"])
    place = place or PLACES.get(title, "")
    facts = {"commons_category": found_in or sp["category"]}
    caption = good_caption(text, title)
    rows = []
    if sp["answer"]:
        rows.append({"question": QUESTIONS[sp["kind"]], "answer": sp["answer"], "credit": credit, "facts": facts,
                     **where(place)})
    if caption and (sp["answer"] or len(caption.split()) >= CAPTION_WORDS):
        rows.append({"question": DESCRIBE_Q, "answer": caption, "credit": credit, "facts": facts, **where(place)})
    if rows:
        extra = where_row(rows[0], place)
        if extra:
            rows.append(extra)
    return rows


def commons_items(specs, limit, prefix, people_ok):
    """[(file name, picture address, rows)] from Commons specs: the categories take turns, in an order shuffled with
    pass_random, so each gets an even share; only files under CC0, public domain, CC BY or an open government
    licence (free_entries); files left
    out by their words are noted (considered()); a file of a caption-only category with no usable caption is set
    aside for a description. people_ok: False leaves out files whose words name a person."""
    s, items, seen = session(), [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.3 / max(1, len(order))))
    want = int(limit * 1.3) + 2
    queues = [[sp, None] for sp in order]
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
            sp, files = q
            if files is None:
                files = [(t, c) for t, c in spec_files(s, sp) if t not in seen]
                pass_random(sp["category"]).shuffle(files)
                say(f"Commons {sp['category']}: {len(files)} files")
            batch, q[1] = files[:share * 2], files[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            found_in = dict(batch)
            got = 0
            try:
                entries = free_entries(s, [t for t, _ in batch])
            except RuntimeError as e:                   # Commons kept refusing: stop looking, keep what was found
                say(f"  Commons refused ({e}); {len(items)} pictures found")
                queues = []
                break
            for title, url, credit, text, raw in entries:
                if got >= share or title in seen:
                    continue
                why = left_out_because(title, f"{text} {raw}", people_ok)
                if why:
                    considered(title, url, why)
                    continue
                rows = file_rows(sp, found_in.get(title, ""), title, credit, text)
                seen.add(title)
                if not rows:
                    needs_description(file_name(prefix, title), url, credit, credit_licence(credit), text=text,
                                      title=title, reason="its caption is missing or under six English words",
                                      place=category_place(found_in.get(title, "")) or sp["place"],
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"commons_category": found_in.get(title) or sp["category"],
                                             "not_for_picture_making": people_ok})
                    continue
                items.append((file_name(prefix, title), url, rows))
                got += 1
            if not q[1]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    return items[:want]


def commons_pack(specs, limit, prefix, people_ok):
    """commons_items, then the files dated before 1990 left out, then the pictures downloaded (patiently)."""
    items = commons_items(specs, limit, prefix, people_ok)
    items = recent_only(items)
    fetched = commons_fetch(items)[:limit]
    say(f"{prefix}: {len(fetched)} pictures")
    return with_twins(fetched)


def machine(category, answer, depth=0, place=""):
    """A spec asking "What kind of machine is this?"."""
    return spec(category, "machine", answer, depth, place)


def thing(category, answer, depth=0, place=""):
    """A spec asking "What is this?"."""
    return spec(category, "thing", answer, depth, place)


def place_kind(category, answer, depth=0, place=""):
    """A spec asking "What kind of place is this?"."""
    return spec(category, "place", answer, depth, place)


def doing(category, answer, depth=0, place=""):
    """A spec asking "What is happening here?"."""
    return spec(category, "doing", answer, depth, place)


def caption_only(category, depth=1, place=""):
    """A spec whose photos are used only with their own caption (else set aside for a description)."""
    return spec(category, "caption", None, depth, place)


# ----------------------------------------------------------------- work_commons_workplaces

WORK_SPECS = [
    # places
    place_kind("Factories in the United States", "This is a factory in the USA, where goods are made.", 1),
    place_kind("Factories in Canada", "This is a factory in Canada, where goods are made.", 1),
    place_kind("Factories in Ontario", "This is a factory in Ontario, Canada.", 1),
    place_kind("Factories in Quebec", "This is a factory in Quebec, Canada.", 1),
    place_kind("Warehouses in the United States", "This is a warehouse in the USA, where goods are stored.", 1),
    place_kind("Warehouses in Canada", "This is a warehouse in Canada, where goods are stored.", 1),
    place_kind("Machine shops", "This is a machine shop: a workshop where metal parts are cut and shaped on machine "
                                "tools such as lathes, milling machines and drill presses.", 1),
    place_kind("Automobile repair shops in the United States", "This is a car repair shop (garage) in the USA, "
                                                               "where cars are serviced and repaired.", 1),
    place_kind("Automobile repair shops in Canada", "This is a car repair shop (garage) in Canada.", 1),
    place_kind("Workshops in the United States", "This is a workshop in the USA, with workbenches and tools.", 1),
    place_kind("Sawmills in the United States", "This is a sawmill in the USA, where logs are cut into lumber.", 1),
    place_kind("Sawmills in Canada", "This is a sawmill in Canada, where logs are cut into lumber.", 1),
    place_kind("Tire shops", "This is a tire shop, where tires are sold, fitted and repaired."),
    place_kind("Truck stops", "This is a truck stop: a fuel station and rest place for truck drivers on a highway."),
    place_kind("Breweries in the United States", "This is a brewery in the USA, where beer is made in big tanks.",
               1),
    place_kind("Bottling plants", "This is a bottling plant, where drinks are filled into bottles or cans on a "
                                  "production line.", 1),
    place_kind("Steel mills in the United States", "This is a steel mill in the USA.", 1),
    # moving and storing goods
    machine("Forklifts in the United States", "This is a forklift: a small truck with two forks at the front that "
                                              "lift and carry loads on pallets.", 1),
    machine("Forklifts in Canada", "This is a forklift: a small truck with two forks that lift and carry pallets."),
    thing("Pallet jacks", "This is a pallet jack (pallet truck): a hand-pulled or powered cart whose two forks slide "
                          "under a pallet and lift it just off the floor to move it.", 1),
    thing("Pallets", "These are pallets: flat wooden or plastic platforms that goods are stacked on, so a forklift "
                     "or pallet jack can lift them.", 1),
    thing("Pallet racking", "This is pallet racking: tall steel shelving in a warehouse that holds loaded pallets."),
    machine("Conveyor belts", "This is a conveyor belt: a moving belt that carries goods or material along.", 1),
    machine("Roller conveyors", "This is a roller conveyor: a line of rollers that boxes and goods move along."),
    thing("Hand trucks", "This is a hand truck (dolly): an upright two-wheeled cart for moving boxes and heavy "
                         "things.", 1),
    machine("Overhead cranes", "This is an overhead crane (bridge crane): a crane that runs on rails high across a "
                               "factory or warehouse and lifts heavy loads with a hoist.", 1),
    machine("Gantry cranes", "This is a gantry crane: a crane on legs that straddle the load, often running on "
                             "rails.", 1),
    machine("Scissor lifts", "This is a scissor lift: a work platform raised by criss-cross metal arms, so workers "
                             "can reach high places.", 1),
    machine("Aerial work platforms", "This is an aerial work platform (a lift): a machine that raises workers in a "
                                     "basket or on a platform to work up high.", 1),
    machine("Skid-steer loaders", "This is a skid-steer loader: a small, nimble loader with a bucket or forks at the "
                                  "front, steered by turning its wheels at different speeds.", 1),
    # machine tools and work
    machine("Milling machines", "This is a milling machine: a machine tool whose spinning cutter shapes metal.", 1),
    machine("Drill presses", "This is a drill press: a drill fixed on a stand, lowered by a handle to drill straight "
                             "holes.", 1),
    machine("Packaging machines", "This is a packaging machine, which wraps, fills or seals products on a "
                                  "production line.", 1),
    machine("Industrial robots in the United States", "This is an industrial robot: a machine arm that welds, "
                                                      "lifts or assembles in a factory.", 1),
    thing("Tool boards", "This is a tool board (pegboard): a wall panel where tools hang, each in its place."),
    doing("Welders", "Someone is welding: joining metal with great heat, wearing a welding helmet against the "
                     "bright light and sparks.", 1),
    doing("Machinists", "A machinist is at work, making metal parts on a machine tool.", 1),
    # safety equipment in use
    thing("Hard hats", "This is a hard hat (safety helmet), worn on building sites and in factories to protect the "
                       "head.", 1),
    thing("Respirators", "This is a respirator: a mask that filters dust, fumes or germs out of the air breathed "
                         "in.", 1),
    thing("Steel-toe boots", "These are steel-toe boots (safety boots), with a hard toe cap that protects the feet "
                             "from heavy things."),
    thing("Fire extinguishers in the United States", "This is a fire extinguisher, for putting out a small fire."),
    # captions only
    caption_only("Industry in the United States"),
    caption_only("Industry in Canada"),
    caption_only("Manufacturing in the United States"),
]


def build_work_commons_workplaces(limit):
    """The Commons workplaces and light industry pack (workers kept: for describing only)."""
    return commons_pack(WORK_SPECS, limit, "work", people_ok=True)


# ----------------------------------------------------------------- farm_commons_equipment

TRACTOR = "This is a tractor: a farm vehicle with big rear wheels that pulls and powers farm machines."

FARM_SPECS = [
    # tractors and harvest machines
    machine("Tractors in the United States by state", TRACTOR, 1),
    machine("Tractors in Canada", TRACTOR, 1),
    machine("Tractors in Ontario", TRACTOR),
    machine("Tractors in Saskatchewan", TRACTOR),
    machine("John Deere tractors", "This is a John Deere tractor (green and yellow).", 1),
    machine("Case IH tractors", "This is a Case IH tractor (red).", 1),
    machine("New Holland tractors", "This is a New Holland tractor.", 1),
    machine("Massey Ferguson tractors", "This is a Massey Ferguson tractor.", 1),
    machine("Kubota tractors", "This is a Kubota tractor.", 1),
    machine("Combine harvesters in the United States", "This is a combine harvester: a big farm machine that cuts a "
                                                       "grain crop and separates the grain from the straw as it "
                                                       "drives."),
    machine("Combine harvesters in Canada", "This is a combine harvester, which cuts and threshes grain as it "
                                            "drives."),
    machine("Round balers", "This is a round baler: a farm machine pulled by a tractor that rolls hay or straw into "
                            "big round bales.", 1),
    machine("Square balers", "This is a square baler: a farm machine pulled by a tractor that presses hay or straw "
                             "into rectangular bales.", 1),
    machine("Forage harvesters", "This is a forage harvester: a farm machine that chops a crop such as corn or grass "
                                 "into silage and blows it into a wagon.", 1),
    machine("Cotton pickers", "This is a cotton picker: a farm machine that picks cotton from the plants."),
    machine("Cotton harvesters", "This is a cotton harvester: a farm machine that harvests cotton."),
    machine("Potato harvesters", "This is a potato harvester: a farm machine that lifts potatoes out of the ground.",
            1),
    # field machines
    machine("Cultivators", "This is a cultivator: a farm implement pulled by a tractor whose tines stir the soil "
                           "and pull out weeds.", 1),
    machine("Manure spreaders", "This is a manure spreader: a farm trailer that spreads manure over a field as "
                                "fertilizer.", 1),
    machine("Fertilizer spreaders", "This is a fertilizer spreader, which throws fertilizer evenly over a field.", 1),
    machine("Hay rakes", "This is a hay rake: a farm implement that rakes cut hay into rows to dry and be baled.",
            1),
    thing("Hay wagons", "This is a hay wagon: a flat farm wagon for carrying hay bales.", 1),
    thing("Gravity wagons", "This is a gravity wagon: a farm wagon with a sloped bottom that unloads grain through "
                            "a door at the side."),
    thing("Three-point hitches", "This is a tractor's three-point hitch: three arms at the back that lift and pull "
                                 "an implement."),
    thing("Power take-offs", "This is a power take-off (PTO): a spinning shaft at the back of a tractor that drives "
                             "a machine; it can catch clothing, so stay clear of it."),
    machine("Field sprayers", "This is a field sprayer: a farm machine with long booms that sprays a crop with "
                              "fertilizer or pesticide.", 1),
    machine("Self-propelled field sprayers", "This is a self-propelled sprayer: a tall farm machine with its own "
                                             "engine and wide spray booms, for spraying crops.", 1),
    thing("Augers", "This is an auger: a long tube with a turning screw inside that moves grain up into a bin or "
                    "truck.", 1),
    # storage
    thing("Grain dryers", "This is a grain dryer: a farm machine that dries harvested grain with heated air so it "
                          "keeps in storage.", 1),
    thing("Grain storage", "This is grain storage: bins or silos where harvested grain is kept dry.", 1),
    thing("Silos in the United States", "This is a farm silo in the USA, for storing grain or silage.", 1),
    thing("Silos in Canada", "This is a farm silo in Canada, for storing grain or silage.", 1),
    thing("Tower silos", "This is a tower silo: a tall round tower beside a barn for storing silage (fermented "
                         "cattle feed).", 1),
    thing("Bunker silos", "This is a bunker silo: a long pit with concrete walls where silage is packed and covered "
                          "with plastic.", 1),
    thing("Grain elevators in the United States", "This is a grain elevator: a tall building where farmers' grain is "
                                                  "stored and loaded onto trucks or trains.", 1),
    thing("Grain elevators in Canada", "This is a grain elevator in Canada, where grain is stored and loaded onto "
                                       "trains.", 1),
    thing("Grain elevators in Saskatchewan", "This is a prairie grain elevator in Saskatchewan, Canada.", 1),
    thing("Grain elevators in Alberta", "This is a prairie grain elevator in Alberta, Canada.", 1),
    thing("Quonset huts", "This is a Quonset hut: a half-round building of corrugated steel, often used on farms as "
                          "a machine shed.", 1),
    # water
    thing("Center pivot irrigation in the United States", "This is center-pivot irrigation: a long sprinkler arm on "
                                                          "wheels that turns round a field, watering a circle.", 1),
    # buildings and livestock
    place_kind("Barns in the United States by state", "This is a barn: a farm building for animals, hay or "
                                                      "machines.", 1),
    place_kind("Barns in the United States", "This is a barn in the USA.", 0),
    place_kind("Barns in Canada", "This is a barn in Canada.", 1),
    place_kind("Barns in Ontario", "This is a barn in Ontario, Canada.", 1),
    place_kind("Barns in Quebec", "This is a barn in Quebec, Canada.", 1),
    place_kind("Bank barns", "This is a bank barn: a barn built into a slope, so wagons can drive into the upper "
                             "floor and animals are kept below.", 1),
    place_kind("Round barns", "This is a round barn.", 1),
    place_kind("Pole barns", "This is a pole barn: a simple farm building whose roof rests on poles set in the "
                             "ground."),
    place_kind("Hay barns", "This is a hay barn, where hay bales are stored out of the rain.", 1),
    place_kind("Milking parlours", "This is a milking parlor: the room on a dairy farm where cows are milked by "
                                   "machine.", 1),
    place_kind("Rotary milking parlours", "This is a rotary milking parlor: cows stand on a slowly turning "
                                          "platform while they are milked."),
    place_kind("Dairy farms in Wisconsin", "This is a dairy farm in Wisconsin, USA.", 1),
    place_kind("Feedlots in the United States", "This is a cattle feedlot in the USA: many cattle kept in pens and "
                                                "fed for beef.", 1),
    thing("Cattle chutes", "This is a cattle chute: a narrow fenced lane that holds cattle one at a time so they "
                           "can be checked or treated safely."),
    thing("Chicken coops", "This is a chicken coop: a small house where hens roost and lay eggs.", 1),
    thing("Electric fences", "This is an electric fence: thin wires carrying short electric pulses that keep "
                             "livestock in.", 1),
    place_kind("Greenhouses in the United States", "This is a greenhouse in the USA: a building of glass or clear "
                                                   "plastic where plants are grown.", 1),
    place_kind("Greenhouses in Canada", "This is a greenhouse in Canada.", 1),
    place_kind("Greenhouses in Ontario", "This is a greenhouse in Ontario, Canada.", 1),
    place_kind("Hydroponics", "This is hydroponic growing: plants grown in water with nutrients instead of soil.",
               1),
    place_kind("Vertical farming", "This is a vertical farm: crops grown indoors on stacked shelves under lights.",
               1),
    doing("Maple syrup production", "Maple syrup is being made: sap from maple trees is collected and boiled down.",
          1),
    place_kind("Farms in the United States", "This is a farm in the USA.", 1),
    place_kind("Farms in Canada", "This is a farm in Canada.", 1),
    # captions only
    caption_only("Agriculture in the United States"),
    caption_only("Agriculture in Canada"),
    caption_only("Farms in Iowa"),
]


def build_farm_commons_equipment(limit):
    """The Commons farm machines and buildings pack (files naming a person left out: may be used for
    picture-making)."""
    return commons_pack(FARM_SPECS, limit, "farm", people_ok=False)


# ----------------------------------------------------------------- mech_commons_building

MECH_SPECS = [
    # heating
    thing("Gas furnaces", "This is a gas furnace: a furnace or heater that burns natural gas or propane.", 1),
    thing("Heating boilers", "This is a heating boiler: it heats water or makes steam to heat a building.", 1),
    thing("Cast iron radiators", "This is a cast-iron radiator: hot water or steam from the boiler flows through it "
                                 "to heat the room."),
    thing("Radiators", "This is a heating radiator: hot water or steam flows through it to heat the room."),
    thing("Baseboard heaters", "This is a baseboard heater: a long, low heater along the bottom of a wall."),
    thing("Wood-burning stoves", "This is a wood stove: a metal stove that burns wood to heat a room, with a "
                                 "stovepipe to the chimney.", 1),
    thing("Pellet stoves", "This is a pellet stove: a stove that burns small wood pellets fed from a hopper."),
    thing("Chimneys in the United States", "This is a chimney: it carries smoke and fumes from a furnace, boiler, "
                                           "fireplace or stove up and out of the building.", 1),
    thing("Flues", "This is a flue: the pipe or channel that carries fumes from a furnace, boiler or stove out of "
                   "the building."),
    # cooling and air
    thing("Air conditioners in the United States", "This is an air conditioner: it cools a building by moving "
                                                   "heat from inside to outside.", 1),
    thing("Air handling units", "This is an air handler (air handling unit): a big metal cabinet with a fan that "
                                "moves heated or cooled air through the building's ducts."),
    thing("Ductwork", "This is ductwork: metal ducts that carry heated or cooled air around a building.", 1),
    thing("Vents", "This is a vent: an opening with a grille that lets air in or out.", 1),
    thing("Exhaust fans", "This is an exhaust fan: it pulls stale or damp air out of a room or building.", 1),
    thing("Bathroom exhaust fans", "This is a bathroom exhaust fan: it pulls damp air out of the bathroom.", 1),
    thing("Air filters", "This is an air filter: it catches dust from the air going through a furnace, air "
                         "conditioner or air handler.", 1),
    # water and drainage
    thing("Well pumps", "This is a well pump: it pumps water up from a well to the house.", 1),
    thing("Water wells in the United States", "This is a water well in the USA.", 1),
    thing("Expansion tanks", "This is an expansion tank: a small tank on a water heater or boiler that takes up "
                             "the water's expansion as it heats."),
    thing("Water softeners", "This is a water softener: it takes the hardness (calcium and magnesium) out of the "
                             "water, with a tank of salt beside it."),
    thing("Sump pumps", "This is a sump pump: a pump that sits in a pit (a sump) and pumps out the water that "
                        "collects there, such as groundwater under a basement floor."),
    thing("Septic tanks", "This is a septic tank: a buried tank that holds a house's waste water where there is no "
                          "sewer."),
    thing("Septic systems", "This is a septic system: a septic tank and drain field that treat a house's waste "
                            "water where there is no sewer.", 1),
    place_kind("Boiler rooms", "This is a boiler room: the room that holds a building's boilers and heating "
                               "equipment.", 1),
    place_kind("Mechanical rooms", "This is a mechanical room: the room that holds a building's heating, cooling, "
                                   "water and electrical equipment."),
    place_kind("Basements in the United States", "This is a basement in the USA, where the furnace, water heater "
                                                 "and other equipment are often kept.", 1),
    # power and fuel
    thing("Distribution boards", "This is an electrical panel (distribution board): it holds the circuit breakers "
                                 "or fuses that feed and protect electrical circuits.", 1),
    thing("Fuse boxes", "This is a fuse box: an older kind of electrical panel with fuses for each circuit.", 1),
    thing("Electricity meters in Canada", "This is an electricity meter: it measures how much electricity the "
                                          "building uses.", 1),
    thing("Smart meters", "This is a smart meter: an electricity meter with a digital display that sends its "
                          "readings to the power company.", 1),
    thing("Gas meters", "This is a gas meter: it measures how much natural gas the building uses.", 1),
    thing("Service drops", "This is a service drop: the overhead wires that bring electricity from the pole to the "
                           "building."),
    thing("Liquefied petroleum gas tanks", "This is a tank of liquefied petroleum gas (LPG, propane), a fuel "
                                           "for heating, hot water, cooking or engines.", 1),
    thing("Oil tanks", "This is an oil tank: a tank that stores fuel oil.", 1),
]


def build_mech_commons_building(limit):
    """The Commons building mechanical pack (files naming a person left out: may be used for picture-making)."""
    return commons_pack(MECH_SPECS, limit, "mech", people_ok=False)


# ----------------------------------------------------------------- farm_usda_nrcs

NRCS_CATEGORY = "Natural Resources Conservation Service"
NRCS_AGENCY = "the US Department of Agriculture (USDA)"
# Captions that are about people, not the land: officials, meetings, awards and portraits.
NRCS_NOT_FARM = re.compile(r"\b(secretary|chief|administrator|meeting|conference|award\w*|ceremony|portrait|"
                           r"headshot|speaks?|speech|signing|logo|banner|poster|booth|service cent(er|re)|"
                           r"offices?|employees?|staff|training session|workshop attendees)\b", re.I)


def nrcs_state(title):
    """The state of an NRCS Photo Gallery file from its number ("File:NRCSIA00016 - Iowa (2235)(NRCS Photo
    Gallery).jpg" -> "Iowa, USA": the gallery numbered its photos by state), or ""."""
    m = re.match(r"(?:File:)?NRCS([A-Z]{2})\d", title or "")
    state = US_STATE_CODES.get(m.group(1), "") if m else ""
    return f"{state}, USA" if state else ""


def nrcs_rows(caption, credit, place):
    """The rows of one NRCS photo: its caption, and that it is a USDA photo (the files filed under NRCS on Commons
    are by NRCS and by other USDA offices, so the department is named, not the office)."""
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit, **where(place)},
            {"question": "Who took this photo?",
             "answer": f"It is a photo by {NRCS_AGENCY}, a US government department.",
             "credit": credit}]
    extra = where_row(rows[0], place)
    return rows + ([extra] if extra else [])


def build_farm_usda_nrcs(limit):
    """The NRCS pack: the category and its subcategories, files sampled in a pass_random order, public domain or
    other free files only, with NRCS's caption; a free photo whose caption is under six English words is set aside
    for a description."""
    s, items, seen = session(), [], set()
    sp = spec(NRCS_CATEGORY, "caption", None, 1, "USA")
    files = spec_files(s, sp, most_subcategories=20)
    pass_random("nrcs").shuffle(files)
    found_in = dict(files)
    say(f"Commons {NRCS_CATEGORY}: {len(files)} files")
    titles = [t for t, _ in files]
    for start in range(0, len(titles), 100):
        if len(items) >= limit * 1.3 or listing_out_of_time():
            break
        try:
            entries = free_entries(s, titles[start:start + 100])
        except RuntimeError as e:
            say(f"  Commons refused ({e}); {len(items)} pictures found")
            break
        for title, url, credit, text, raw in entries:
            if title in seen:
                continue
            seen.add(title)
            words = f"{text} {raw}"
            why = left_out_because(title, words, people_ok=True) or \
                ("an official event or a portrait, not the land" if NRCS_NOT_FARM.search(words) else "")
            if why:
                considered(title, url, why)
                continue
            place = nrcs_state(title) or category_place(found_in.get(title, "")) or PLACES.get(title, "") or "USA"
            caption = good_caption(agency_caption(raw or text), title)
            if len(caption.split()) < CAPTION_WORDS:
                needs_description(file_name("nrcs", title), url, credit, credit_licence(credit), text=caption or text,
                                  title=title, reason="its caption is under six English words", place=place,
                                  page_url=credit.rsplit(", ", 1)[-1],
                                  extra={"agency": NRCS_AGENCY, "commons_category": found_in.get(title, ""),
                                         "not_for_picture_making": True})
                continue
            items.append((file_name("nrcs", title), url, nrcs_rows(caption, credit, place)))
    items = recent_only(items[:int(limit * 1.3) + 2])
    fetched = commons_fetch(items)[:limit]
    say(f"farm_usda_nrcs: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain, CC BY or an open government "
                  "licence (OGL-ON, OGL-Canada, OGL UK), each with its author "
                  "and file page below. https://commons.wikimedia.org. Changes: pictures made smaller; answers "
                  "written from the category names.")
WORK_FARM_MECH_PACKS = {
    "work_commons_workplaces": (build_work_commons_workplaces, COMMONS_CREDIT.format(
        what="categories of US and Canadian workplaces, workplace machines and safety equipment")),
    "farm_commons_equipment": (build_farm_commons_equipment, COMMONS_CREDIT.format(
        what="categories of farm machines, farm buildings and livestock handling in the US and Canada")),
    "mech_commons_building": (build_mech_commons_building, COMMONS_CREDIT.format(
        what="categories of building heating, cooling, ventilation, water, drainage, power and fuel equipment")),
    "farm_usda_nrcs": (build_farm_usda_nrcs,
                       "US Department of Agriculture, Natural Resources Conservation Service (NRCS) photos, via "
                       "Wikimedia Commons (Category:Natural Resources Conservation Service): US government work, "
                       "public domain; each file's licence checked on its Commons page; captions by NRCS. Changes: "
                       "pictures made smaller."),
}

# How many pictures a full build takes from each (about what each offers after the checks).
WORK_FARM_MECH_LIMITS = {
    "work_commons_workplaces": 1500,      # about 45 categories; many small, and the US and Canadian ones are thin
    "farm_commons_equipment": 2500,       # about 65 categories, tractors by state and maker the largest
    "mech_commons_building": 1200,        # about 35 categories, most of them under 200 files
    "farm_usda_nrcs": 3000,               # 12,400 files; about half have a caption of six words or more
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one workplace, farm or building mechanical pack builder.")
    parser.add_argument("key", choices=sorted(WORK_FARM_MECH_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = WORK_FARM_MECH_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    questions = collections.Counter(row["question"] for _, _, row in entries)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child, "
        f"{len(build_packs.NEEDS)} set aside for a description; questions: " +
        ", ".join(f"{q} {n}" for q, n in questions.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
