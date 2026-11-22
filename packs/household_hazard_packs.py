"""Pack builders for COMMON HOUSEHOLD HAZARDS: frayed and damaged cords, overloaded sockets and power strips,
exposed wiring, mould, water leaks and stains, damaged or removed smoke alarms, expired or discharged fire
extinguishers, blocked exits, tripping hazards and space heaters too close to things. Used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)],
where a row is {"question", "answer", "credit"}, plus "child": true where the words of a picture name a child. A
picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file"
names the same picture (food_packs.with_twins). The limit counts pictures.

Why: a blind person cannot see the frayed cord behind the sofa, the stain spreading on the ceiling, the smoke alarm
hanging off the wall or the heater pushed against the curtain.

ANSWERS SAY ONLY WHAT THE RECORD STATES. A hazard is named only when the file's own title or description says it in so
many words (HAZARD_RULES: "frayed cord", "overloaded power strip", "blocked fire exit", "trip hazard", "space heater
... too close to the curtains", "leaking pipe", "extinguisher ... expired", "gauge in the red" ...), with a short
safety note from public guidance (US Fire Administration, CPSC, NFPA, EPA). Nothing is guessed from the picture, and a
file whose words name two different hazards gets each of them.

The packs (all open, checked at the source in November 2026):
  commons_household_hazards      Wikimedia Commons files found with Commons search (HAZARD_SEARCHES, files only), among
                                 them the US Consumer Product Safety Commission's and NIST's own photos copied to
                                 Commons (public domain as US government works; each file's licence checked on its
                                 own page: CC0, public domain or CC BY, never BY-SA, NC or ND). Files in a category
                                 another pack already reads for the same subject (home_safety_packs,
                                 events_safety_packs, home_packs) are left out. "Is there a hazard here?" -> "Yes: the
                                 photo's own words (its title or description) say ..." and the note; "Write a
                                 short description ..." from the file's own words.
  open_images_household_hazards  Google Open Images V7: photos where people checked by hand whether a leak, a
                                 space heater or heater, a fire sprinkler or a fire alarm system is there (labels CC BY
                                 4.0; each photo's own licence checked, photographer named), with the note.

Not repeated (other packs ask the same of the same photos): mould on walls, water damage, smoke and CO alarms,
extinguishers and their gauges with a stated state (home_safety_packs commons_home_safety), wet floor signs, broken
glass, open manholes, smoke, building fires and fire equipment (events_safety_packs commons_safety_photos), pests and
damp (home_packs commons_pests), extension cords as things (hardware_packs), space heaters as devices (device_packs),
Open Images extension cords and power strips (home_packs open_images_home). CPSC's own recall photos (the recalling
firms' pictures) and its Flickr stream are not used (packaged_goods_sources.py, Flickr's API terms).

Safety (packs/SOURCE-RULES.md): no sexual content; no injuries, deaths or victims (HARM): a fire test in a NIST
laboratory may be shown, a burned home with its victims never. Rows whose words name a child are marked "child".
People are in many of these photos: both packs are for describing only, never for picture-making.

    python packs/household_hazard_packs.py commons_household_hazards --limit 8      (a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random, ALT_TEXT
from gaps_oi_packs import group, build_oi_gap, QUICK

HAZARD_Q = "Is there a hazard here?"

CORD_NOTE = ("Unplug it and replace the cord or the appliance; tape does not make a damaged cord safe, and cords "
             "should never run under rugs or be pinched by furniture.")
OVERLOAD_NOTE = ("Plug big appliances (heaters, kettles, microwaves) straight into a wall socket, never chain power "
                 "strips or extension leads together, and do not fill every outlet of a strip with high-power things.")
WIRING_NOTE = "Do not touch it. Keep people away and call a qualified electrician."
MOULD_NOTE = ("Fix the leak or damp that feeds it. Small patches can be cleaned with soap and water while wearing "
              "gloves and a mask; larger areas need a professional (EPA advice: more than about 10 square feet).")
LEAK_NOTE = ("Turn off the water at the shut-off valve if you can, keep electrical things away from the water, and "
             "call a plumber; a spreading stain on a ceiling can mean water is collecting above it.")
SMOKE_ALARM_NOTE = ("A smoke alarm that is damaged, hanging loose, painted over or missing its battery will not warn "
                    "you of a fire: replace it (and every alarm after 10 years) and test alarms monthly.")
EXTINGUISHER_NOTE = ("An extinguisher whose gauge needle is out of the green, or that is past its service date or "
                     "has been used, may not work: have it recharged or replaced.")
EXIT_NOTE = "Exits and the path to them must be kept clear at all times, so everyone can get out quickly in a fire."
TRIP_NOTE = ("Clear the walkway or tape the edge down; falls are a leading cause of injury at home, and clutter on "
             "stairs is the most dangerous.")
HEATER_NOTE = ("Keep space heaters at least 3 feet (1 metre) from anything that can burn, such as curtains, bedding "
               "and furniture, plug them straight into a wall socket, and switch them off when you leave the room.")

# (pattern in the file's own words, what the answer says the record states, the note).
HAZARD_RULES = [
    (r"\b(frayed|damaged|worn|cracked|split|exposed|melted|burnt|burned)\s+(power |electric(al)? |extension |"
     r"appliance |lamp )?(cords?|cables?|leads?|flex)\b", "a damaged or frayed electrical cord", CORD_NOTE),
    (r"\boverload(ed|ing)?\s+(power |electrical |wall )?(sockets?|outlets?|power strips?|power boards?|"
     r"extension (leads?|cords?)|plugs?|adapters?|circuits?)\b|\b(daisy[- ]chain(ed|ing)?|octopus (wiring|plug|"
     r"connection))\b|\btoo many plugs\b", "an overloaded socket, power strip or extension lead", OVERLOAD_NOTE),
    (r"\b(exposed|bare|live|dangling|loose)\s+(electrical |electric )?(wir(es|ing)|conductors?)\b|"
     r"\b(dangerous|unsafe|faulty|illegal)\s+(electrical )?(wiring|installation)\b", "exposed or unsafe wiring",
     WIRING_NOTE),
    (r"\b(black|toxic) mou?ld\b|\bmou?ld (growth|growing|spots?|patches)\b|\bgrowing mou?ld\b|\bmildew\b|"
     r"\bmou?ldy (walls?|ceilings?|bathroom|windows?|room)\b|\bmou?ld (on|in|covering|spreading)\b.{0,30}\b(walls?|"
     r"ceilings?|bathroom|windows?|corners?|room|house|home)\b|\b(walls?|ceilings?)\b.{0,20}\b(covered (in|with)|"
     r"with) mou?ld\b", "mould on a wall, ceiling or window", MOULD_NOTE),
    (r"\b(leak(ing|y|s|ed)?|dripping)\s+(water |sink |toilet |radiator |roof |ceiling )?(pipes?|taps?|faucets?|"
     r"roofs?|ceilings?|valves?|water heaters?|boilers?)\b|\bwater (leaks?|stains?)\b|\b(ceiling|roof) leaks?\b",
     "a water leak or water stain", LEAK_NOTE),
    (r"\bsmoke (alarms?|detectors?)\b.{0,50}\b(damaged|broken|cracked|hanging|dangling|missing|removed|"
     r"disconnected|without (a |its )?batter(y|ies)|battery (removed|missing)|painted over|covered)\b|"
     r"\b(damaged|broken|disabled|disconnected|removed)\s+smoke (alarms?|detectors?)\b",
     "a damaged, disconnected or removed smoke alarm", SMOKE_ALARM_NOTE),
    (r"\b(fire )?extinguishers?\b.{0,60}\b(expired|out of date|discharged|empty|used|needle in the red|gauge "
     r"(in|on) the red|needs? recharg\w*|overdue)\b|\b(expired|discharged|empty|used)\s+(fire )?extinguishers?\b",
     "a fire extinguisher that is expired, used or not charged", EXTINGUISHER_NOTE),
    (r"\b(blocked|obstructed|locked|chained|cluttered|barricaded)\s+(fire |emergency )?(exits?|escape routes?|"
     r"exit doors?|fire doors?)\b|\b(fire |emergency )?exits?\b.{0,20}\b(blocked|obstructed)\b",
     "a blocked exit", EXIT_NOTE),
    (r"\btrip(ping)? hazards?\b|\b(loose|torn|curled|rucked) (rugs?|carpets?|mats?)\b|\bclutter(ed)? stairs?\b|"
     r"\bcables? across the floor\b", "a tripping hazard", TRIP_NOTE),
    (r"\b(space |portable |electric |fan |oil-filled |kerosene )?heaters?\b.{0,60}\b(too close|near(by)? "
     r"(the )?(curtains?|drapes?|bed|sofa|couch|furniture|paper|clothes)|next to (the )?(curtains?|drapes?|bed|"
     r"sofa|couch|furniture|clothes)|fire hazard|clearance|combustibles?)\b",
     "a space heater too close to things that can burn", HEATER_NOTE),
]
HAZARD_RULES = [(re.compile(p, re.I), what, note) for p, what, note in HAZARD_RULES]
# Words that place a photo in a home or another building people live and work in: a leak, mould or trip hazard counts
# only with one of them (a leaking pipe in a street, a field or a ship's drill is not a household hazard).
HOME = re.compile(r"\b(homes?|house|houses|kitchens?|bathrooms?|bedrooms?|living rooms?|basements?|cellars?|attics?|"
                  r"garages?|apartments?|flats?|ceilings?|walls?|floors?|sinks?|toilets?|showers?|rooms?|hallways?|"
                  r"stairs|staircases?|offices?|indoors?|inside|carpets?|rugs?)\b", re.I)
HOME_ONLY = {"mould on a wall, ceiling or window", "a water leak or water stain", "a tripping hazard"}
# Words that show a photo is not about a home: ships and drills, streets, fields, vehicles, factories.
NOT_HOUSEHOLD = re.compile(r"\b(ships?|navy|naval|sailors?|uss|damage control|drills?|exercises?|streets?|roads?|"
                           r"highways?|orchards?|fields?|farms?|military|soldiers?|aircraft|vehicles?|cars?|trucks?|"
                           r"factory|factories|refinery|pipelines?|mines?|oil|gas well)\b", re.I)
# Words that leave a file out: injuries, deaths and victims (a burned-out home is not shown here), and nudity.
HARM = re.compile(r"\b(dead|deaths?|died|killed|kills|fatal\w*|victims?|injur\w*|burns? (patients?|victims?)|"
                  r"bodies|corpses?|electrocut\w*|nude|naked)\b", re.I)
# Commons search queries (files only).
HAZARD_SEARCHES = (
    "frayed cord", "frayed cable", "damaged power cord", "overloaded outlet", "overloaded socket",
    "overloaded power strip", "daisy chained power strips", "octopus wiring", "exposed wiring", "dangerous wiring",
    "mold wall", "mould wall", "mold ceiling", "ceiling leak", "water stain ceiling", "leaking pipe",
    "smoke detector removed", "damaged smoke detector", "smoke alarm battery", "expired fire extinguisher",
    "discharged fire extinguisher", "blocked fire exit", "blocked emergency exit", "trip hazard", "tripping hazard",
    "space heater curtains", "space heater fire hazard", "CPSC space heater", "NIST fire test space heater",
    "CPSC extension cord",
)


def hazards_said(text):
    """[(what, note)] for every hazard the file's own words state (HAZARD_RULES), in the rules' order; none when the
    words are about ships, streets, fields, vehicles or factories (NOT_HOUSEHOLD), and a leak, mould or trip hazard
    only when the words also place it in a home or building (HOME)."""
    text = text or ""
    if NOT_HOUSEHOLD.search(text):
        return []
    return [(what, note) for pattern, what, note in HAZARD_RULES
            if pattern.search(text) and (what not in HOME_ONLY or HOME.search(text))]


def hazard_rows(title, text, credit):
    """The rows for one file, or [] when its words state no hazard or name harm."""
    name = re.sub(r"^File:|\.(jpe?g|png|tiff?)$", "", title, flags=re.I).replace("_", " ")
    words = f"{name}. {text or ''}"
    if HARM.search(words):
        return []
    found = hazards_said(words)
    if not found:
        return []
    said = " and ".join(w for w, _ in found)
    notes = " ".join(dict.fromkeys(n for _, n in found))
    rows = [{"question": HAZARD_Q, "credit": credit,
             "answer": f"Yes: the photo's own words (its title or description) say it shows {said}. {notes}"}]
    if text:
        rows.append({"question": ALT_TEXT, "answer": text, "credit": credit})
    return rows


def other_pack_categories():
    """The Commons category names other packs read for the same subjects (quoted names in their source files)."""
    import os
    names = set()
    here = os.path.dirname(os.path.abspath(__file__))
    for module in ("home_safety_packs.py", "events_safety_packs.py", "home_packs.py", "hardware_packs.py",
                   "device_packs.py"):
        with open(os.path.join(here, module), encoding="utf-8") as f:
            names |= set(re.findall(r'"([A-Z][^"\n]{2,80})"', f.read()))
    return names


def build_commons_household_hazards(limit):
    """The commons_household_hazards pack (see the module docstring)."""
    from food_packs import commons_get, with_twins
    from home_packs import commons_fetch, file_name, home_entries, NUDE
    from expression_packs import mark_child
    from medication_label_packs import file_categories
    s, rng = session(), pass_random(9306)
    searches = list(HAZARD_SEARCHES)
    rng.shuffle(searches)
    titles = []
    for query in searches:
        data = commons_get(s, {"action": "query", "list": "search", "srnamespace": 6, "srlimit": 100,
                               "srsearch": f"{query} filetype:bitmap"})
        titles += [r["title"] for r in (data.get("query") or {}).get("search") or [] if r["title"] not in titles]
    say(f"Commons household hazards: {len(titles)} files found by search")
    taken = other_pack_categories()
    cats = file_categories(s, titles)
    titles = [t for t in titles if not cats.get(t, set()) & taken]
    items = []
    for title, url, credit, text in home_entries(s, titles):
        if NUDE.search(f"{title} {text}"):
            continue
        rows = [mark_child(r, f"{title} {text}") for r in hazard_rows(title, text, credit)]
        if rows:
            items.append((file_name("hazard", title), url, rows))
        if len(items) >= int(limit * 1.15) + 2:
            break
    say(f"Commons household hazards: {len(items)} files whose own words state a hazard")
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- Open Images

HAZARD_OI = [
    group("Is there a leak here?", {"Leak": "a leak"}, LEAK_NOTE),
    group("Is there a heater here?", {"Space heater": "a space heater", "Heater": "a heater"}, HEATER_NOTE),
    group("What fire safety equipment is here?", {"Fire sprinkler": "a fire sprinkler",
                                                  "Fire sprinkler system": "a fire sprinkler system",
                                                  "Fire alarm system": "a fire alarm"}),
]


def build_open_images_household_hazards(limit):
    """open_images_household_hazards (see the module docstring)."""
    return build_oi_gap("open_images_household_hazards", HAZARD_OI, limit, 9307)


# ----------------------------------------------------------------- the packs

HAZARD_PACKS = {
    "commons_household_hazards": (build_commons_household_hazards,
                                  "Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain "
                                  "(including US Consumer Product Safety Commission and NIST photos, US government "
                                  "works) or CC BY, credited below, whose own words state a household hazard; "
                                  "captions CC0."),
    "open_images_household_hazards": (build_open_images_household_hazards,
                                      "Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html"
                                      "): labels CC BY 4.0; each photo under its own licence (CC BY, CC0 or the "
                                      "Public Domain Mark, checked photo by photo), photographer credited below."),
}
HAZARD_LIMITS = {
    "commons_household_hazards": 200,       # 30 searches; few files state a household hazard in so many words
    "open_images_household_hazards": 1500,  # 6 labels
}
HAZARD_COMMONS_KEYS = ("commons_household_hazards",)


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a household hazard pack builder.")
    parser.add_argument("key", choices=sorted(HAZARD_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = HAZARD_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
