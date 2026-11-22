"""Picture packs from the NASA Image and Video Library (https://images.nasa.gov), by theme (the owner's request of
2026-11-22 for large, well-captioned public-domain photo collections). Used by build_packs.py in the same way as its
own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"} (and "child": True when the caption mentions a child). The limit counts pictures.

The library: about 230,000 pictures (November 2026) from every NASA centre, read through its public search API
(https://images-api.nasa.gov, no key, documented at https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf). The
API gives at most 10,000 results for one search (100 pages of 100), so each pack reads random pages of many searches.

Copyright: NASA's own pictures are not under copyright in the US (US government work; NASA's media guidelines,
https://www.nasa.gov/nasa-brand-center/images-and-media/). The library also holds pictures by other people (company
photos from SpaceX or Rocket Lab, photos by European, Canadian and Japanese astronauts and agencies, university and
amateur pictures, "courtesy of" pictures, a few marked copyright), so a picture is kept only when (nasa_free):
  - its record names a NASA centre ("center": KSC, JSC, HQ, JPL ...);
  - its photographer, when one is named, is credited to NASA ("NASA/Bill Ingalls", "NASA", "NASA JSC");
  - its other credit ("secondary_creator") and any "Image credit:" line in its caption name only NASA, its centres,
    JPL-Caltech, STScI (which claims no copyright on what it makes for NASA) or the USGS (another US agency);
  - nothing in the record says copyright, (c), "courtesy", a Creative Commons licence or "all rights reserved".
NASA's logos and insignia are not a concern here (the packs teach describing, not branding), but logo, patch and
poster pictures are left out anyway because they are graphics, not photos (NOT_A_PHOTO), as are artist's concepts,
illustrations, renderings, charts, maps and diagrams.

Every picture gets "Describe this picture." with the plain description from its own record (nasa_answer): the
caption with its catalogue prefix ("S73-12345 (8 Feb. 1974) ---"), credit lines, web addresses and "for more
information" sentences taken out, whole sentences up to about 70 words. Nothing is added or guessed. A picture whose
caption is under six words (or only repeats its title) is set aside for a description (build_packs.needs_description).

The packs (NASA_LIBRARY_PACKS). Each picture belongs to one pack only: theme_of() gives each record one theme, in the
order below, and a pack keeps only the records of its own theme, so the same picture never comes in two packs.
  nasa_planets_telescopes   planets, moons, the Sun, comets, galaxies and nebulas from NASA missions and telescopes
                            (Hubble, Webb, Chandra, Spitzer), Mars rovers' views. Pictures with people go to the
                            people themes instead.
  nasa_earth_from_space     the Earth seen from the space station, the shuttle, Apollo and NASA satellites: storms,
                            coasts, cities at night, auroras. Pictures with people go to the people themes.
  nasa_aircraft             NASA research aircraft and their flights: X-planes, the ER-2, SOFIA, DC-8, F/A-18s,
                            helicopters, drones, wind-tunnel models.
  nasa_people_at_work       NASA people at work: engineers, technicians and scientists in labs, clean rooms and
                            mission control, training and testing (describing only: the answers say what the
                            caption says, names included, and never recognise a face).
  nasa_rockets_launch       rockets, launches and launch facilities: launch pads, the Vehicle Assembly Building,
                            crawler-transporters, rollouts, engine tests, the Saturn V, the shuttle stack, SLS.
  nasa_space_astronauts     astronauts and spaceflight: spacewalks, the space station inside and out, the shuttle in
                            orbit, Apollo on the Moon, Skylab, spacesuits, crews training.
Already in the kit and not repeated: the kit's small live "nasa" collection (training-kit/kit/sources.py, 800
pictures with "What does this NASA picture show?"; it reads the first pages of its searches, these packs random
pages, so they rarely meet) and NASA Earth Observatory (documentary_packs earth_observatory, its own site).

    python packs/nasa_library_packs.py nasa_aircraft --limit 8      (prints a few rows: a quick check of one builder)
"""

import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, LONG_SIDE
from build_packs import pass_random, already_in_pack, listing_out_of_time
from build_packs import needs_description
from food_packs import count_pictures
from documentary_packs import tidy, usable, picture_rows, get_json, finish, NOT_SHOWN

API = "https://images-api.nasa.gov/search"
PAGE_SIZE = 100
MOST_PAGES = 100                       # the API refuses page 101 of 100 ("Maximum number of search results")

# The centre codes NASA's library uses (with the spellings seen in its records).
NASA_CENTRES = {"ARC", "AFRC", "DFRC", "GRC", "GSFC", "HQ", "JPL", "JSC", "KSC", "LARC", "MAF", "MSFC", "SSC", "WSTF",
                "WFF", "IVV", "NSSC", "GISS", "SCEPTER"}
# The credits that are NASA's own or another public, no-copyright maker's (see the module docstring).
NASA_PARTS = re.compile(r"^(NASA|N\.A\.S\.A\.|JPL|JPL-Caltech|Caltech|STScI|USGS|U\.S\. Geological Survey|"
                        r"GSFC|Goddard( Space Flight Center)?|JSC|KSC|MSFC|ARC|AFRC|GRC|LaRC|SSC|HQ|"
                        r"(NASA )?(Johnson|Kennedy|Marshall|Glenn|Ames|Langley|Armstrong|Stennis)"
                        r"( Space| Research| Flight)?( Center)?|NASA Earth Observatory|"
                        r"Jet Propulsion Laboratory|Space Telescope Science Institute|Image Science and Analysis "
                        r"Laboratory|Earth Science and Remote Sensing Unit)$", re.I)
NOT_FREE = re.compile(r"copyright|©|\(c\)\s*\d|\bcourtesy\b|creative ?commons|\bCC[- ]BY|all rights reserved|"
                      r"used with permission|\bGetty\b|\bAP Photo\b|\bReuters\b|\bAFP\b", re.I)
CREDIT_LINE = re.compile(r"\(?\b(?:image|photo|video|picture)?\s*credits?\s*:\s*([^)\n]*)\)?", re.I)
# Graphics, not photos.
NOT_A_PHOTO = re.compile(r"\b(artist'?s? (concept|impression|rendering|illustration)|illustration|rendering|render|"
                         r"infographic|logo|insignia|emblem|patch|poster|chart|graph|diagram|map|schematic|"
                         r"animation|computer[- ]generated|computer simulation|visuali[sz]ation|graphic|drawing|cartoon|"
                         r"mosaic of (thumbnail|icon)s?|screen ?shot|title card|slide)\b", re.I)


PEOPLE = re.compile(r"\b(astronauts?|cosmonauts?|crew( members?)?|spacewalk\w*|EVA|extravehicular|engineers?|"
                    r"technicians?|scientists?|researchers?|workers?|employees?|students?|interns?|visitors?|guests?|"
                    r"teams?|officials?|administrator|director|pilots?|people|person|man|woman|men|women|children|"
                    r"kids?|speaks?|speaking|poses?|portrait|ceremony|briefing|conference|panel|audience|meets?|"
                    r"greets?|tours?|mission control|control room|firing room|Mr\.|Mrs\.|Ms\.|Dr\.)\b", re.I)


# "Photographed by the crew" names who took the picture, not who is in it.
TAKEN_BY = re.compile(r"\b(photographed|taken|captured|shot|recorded|imaged|seen|viewed)\s+by\s+(one of\s+)?(the\s+)?"
                      r"([\w-]+\s+){0,3}?(crew\s*(members?|men)?|crewmen|astronauts?|cosmonauts?)\b", re.I)


def has_people(text):
    """True when words say people are in the picture (such pictures go to the people themes, see theme_of); "taken
    by the crew" does not count."""
    return bool(PEOPLE.search(TAKEN_BY.sub("", text)))


# The themes, in the order theme_of() tries them: (pack key, words of the theme, True when people are not wanted).
THEMES = [
    ("nasa_planets_telescopes", re.compile(
        r"\b(planets?|Venus|Mars|Martian|Jupiter|Jovian|Saturn's|Saturnian|Uranus|Neptune|Pluto|Ceres|Vesta|"
        r"asteroids?|comets?|moons?|lunar surface|crater|Io|Europa|Ganymede|Callisto|Saturn's moon Titan|"
        r"Enceladus|Triton|Charon|galax(y|ies)|nebula[es]?|star cluster|supernova|black hole|quasar|exoplanet|"
        r"Milky Way|Hubble|Webb|JWST|Chandra|Spitzer|Kepler|TESS|Cassini|Juno|Voyager|New Horizons|"
        r"Galileo orbiter|Curiosity|Perseverance|Opportunity|Spirit rover|Sojourner|InSight|Ingenuity|rover|"
        r"Mars Reconnaissance|HiRISE|Lunar Reconnaissance|LRO|solar flares?|sunspots?|corona|"
        r"Solar Dynamics Observatory|SDO|SOHO|eclipse|telescopes?)\b", re.I), True),
    ("nasa_earth_from_space", re.compile(
        r"\b(Earth observations?|earth from space|view of (the )?Earth|Earth's (limb|horizon|surface|atmosphere)|"
        r"Earth limb|limb of the Earth|city lights|at night from (the )?(International Space Station|ISS|orbit)|"
        r"(seen|photographed|captured|taken|viewed|imaged) from (the )?(International Space Station|ISS|orbit|"
        r"space|the space shuttle|Apollo \d+|Gemini \d+|Skylab|STS-\d+|the [\w-]+( \d+)? spacecraft)|"
        r"(from|in) (low )?Earth orbit|hurricanes?|typhoons?|cyclones?|tropical storms?|auroras?|aurora (australis|"
        r"borealis)|Landsat|MODIS|Terra satellite|Aqua satellite|Suomi NPP|VIIRS|GOES-\d+|blue marble|"
        r"earthrise)\b", re.I), True),
    ("nasa_aircraft", re.compile(
        r"\b(aircraft|airplanes?|aeroplanes?|jets?(?! Propulsion)|X-\d+[A-Z]?|ER-2|SOFIA|DC-8|C-130|P-3|G-?III|G-?V|Gulfstream|"
        r"T-38|F-15|F-16|F-18|F/A-18|F-104|B-52|SR-71|U-2|WB-57|Global Hawk|Ikhana|helicopters?|rotorcraft|"
        r"tilt ?rotor|gliders?|drones?|unmanned aircraft|UAS|UAV|flight research|research flights?|in flight|"
        r"wind tunnel|airfoil|landing gear|runway|Super Guppy|Shuttle Carrier Aircraft|747)\b", re.I),
     False),
    ("nasa_rockets_launch", re.compile(
        r"\b(rockets?|launch(es|ed|ing)?|lifts? ?off|liftoff|launch pad|launch complex|Pad 39[AB]|Space Launch "
        r"Complex|Vehicle Assembly Building|VAB|crawler[- ]transporter|mobile launcher|rollout|rolls? out|"
        r"Saturn V|Saturn IB|Space Launch System|SLS|solid rocket boosters?|external tank|booster|Atlas|Delta II|"
        r"Delta IV|Titan [IV]+|Antares|Pegasus|Vulcan|Falcon|engine test|hot[- ]fire|test stand|RS-25|"
        r"sounding rocket|stacking|countdown)\b", re.I), False),
    ("nasa_space_astronauts", re.compile(
        r"\b(astronauts?|cosmonauts?|spacewalks?|extravehicular|EVA|International Space Station|space station|ISS|"
        r"Expedition \d+|space shuttle|orbiter|STS-\d+|Apollo|Gemini|Mercury Seven|Skylab|spacesuits?|"
        r"space suits?|crew|Soyuz|neutral buoyancy|zero[- ]g|microgravity|Canadarm|cupola|in orbit|"
        r"on orbit)\b", re.I), False),
    ("nasa_people_at_work", re.compile(
        r"\b(engineers?|technicians?|scientists?|researchers?|workers?|employees?|team members?|teams?|"
        r"flight controllers?|mission control|control room|firing room|clean ?room|laborator(y|ies)|machinist|"
        r"welders?|at work|works? on|working on)\b", re.I), False),
]
NASA_LIBRARY_KEYS = ["nasa_space_astronauts", "nasa_aircraft", "nasa_earth_from_space", "nasa_planets_telescopes",
                     "nasa_rockets_launch", "nasa_people_at_work"]

# The searches each pack reads (random pages of each); a record is kept only when theme_of() gives the pack's theme.
SEARCHES = {
    "nasa_planets_telescopes": ("Hubble", "James Webb Space Telescope", "Chandra", "Spitzer", "galaxy", "nebula",
                                "Mars rover", "Mars surface", "Jupiter", "Saturn", "moon crater", "comet",
                                "asteroid", "Solar Dynamics Observatory", "solar flare", "Pluto", "Cassini", "Juno",
                                "Voyager", "eclipse"),
    "nasa_earth_from_space": ("earth observation", "earth from space", "Earth from the International Space Station",
                              "hurricane from space", "city lights at night", "aurora from space", "Landsat",
                              "MODIS", "Earth limb", "coastline from orbit", "earthrise", "sea ice"),
    "nasa_aircraft": ("aircraft", "research aircraft", "ER-2", "SOFIA", "DC-8", "F/A-18", "X-plane", "X-59",
                      "helicopter", "unmanned aircraft", "glider", "wind tunnel", "flight research",
                      "Shuttle Carrier Aircraft", "Super Guppy", "Armstrong Flight Research Center"),
    "nasa_people_at_work": ("engineers", "technicians", "clean room", "mission control", "laboratory",
                            "scientists", "flight controllers", "inspection", "assembly", "test", "machine shop",
                            "employees"),
    "nasa_rockets_launch": ("rocket launch", "launch pad", "liftoff", "Vehicle Assembly Building",
                            "crawler-transporter", "rollout", "Saturn V", "Space Launch System", "solid rocket booster",
                            "engine test", "test stand", "sounding rocket", "Launch Complex 39", "Atlas", "Delta"),
    "nasa_space_astronauts": ("astronaut", "spacewalk", "International Space Station", "space shuttle", "Apollo",
                              "Gemini", "Skylab", "spacesuit", "Expedition crew", "neutral buoyancy laboratory",
                              "cupola", "Orion", "Moon landing", "astronaut training"),
}

# Caption pieces that are not the description: a catalogue prefix, credit lines, web addresses, "for more" sentences.
PREFIX = re.compile(r"^.{0,120}?---\s*")
NOT_DESCRIPTION = re.compile(r"https?://\S+|www\.\S+|\S+@\S+|\(?\b(?:image|photo|video|picture)?\s*credits?\s*:"
                             r"[^)\n]*\)?", re.I)
DROP_SENTENCE = re.compile(r"^(for more|to learn more|learn more|read more|more information|find out more|"
                           r"for information|follow |visit |click |see also|download |view the |watch |"
                           r"original caption|this image (was|is) (released|available)|nasa image|nasa photo|"
                           r"image number|photo number|caption:)", re.I)


def credit_parts(text):
    """The makers named in one credit ("NASA/JPL-Caltech/MSSS", "NASA, ESA and J. Smith"), each tidied."""
    parts = re.split(r"\s*(?:/|,|;|\band\b|&|\s-\s)\s*", clean(text))
    return [p.strip(" .()") for p in parts if p.strip(" .()")]


def nasa_free(info):
    """True when a library record is NASA's own picture with no third-party credit (see the module docstring)."""
    centre = clean(info.get("center")).upper()
    if centre not in NASA_CENTRES:
        return False
    photographer = clean(info.get("photographer"))
    secondary = clean(info.get("secondary_creator"))
    words = " ".join(clean(info.get(k)) for k in ("title", "description", "description_508", "photographer",
                                                   "secondary_creator"))
    if NOT_FREE.search(words) or NOT_FREE.search(" ".join(clean(k) for k in info.get("keywords") or [])):
        return False
    if photographer and not re.search(r"\bNASA\b", photographer, re.I):
        return False
    credits = [secondary] + [m.group(1) for m in CREDIT_LINE.finditer(clean(info.get("description")))]
    for credit in credits:
        if credit and not all(NASA_PARTS.match(p) for p in credit_parts(credit)):
            return False
    return True


def nasa_answer(info):
    """The plain description of a record (see the module docstring): whole sentences up to about 70 words, or ""
    when what is left is under six words or only repeats the title."""
    text = clean(info.get("description"))
    if "---" in text[:140]:
        text = PREFIX.sub("", text, count=1)
    text = NOT_DESCRIPTION.sub("", text)
    answer = ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        sentence = sentence.strip()
        if not sentence or DROP_SENTENCE.match(sentence):
            continue
        if len((answer + " " + sentence).split()) > 70:
            break
        answer = (answer + " " + sentence).strip()
    answer = tidy(answer)
    title = clean(info.get("title")).rstrip(".").lower()
    if not usable(answer) or answer.rstrip(".").lower() == title:
        return ""
    return answer


def theme_of(info):
    """The one theme (pack key) of a record, or "" when it has none or is a graphic. The themes are tried in THEMES
    order on the title alone first, then on the title, keywords and the start of the caption, so a title decides
    when it can ("STS-135 launch" is a launch even when its caption names the crew). The planets and Earth themes
    take no picture whose title or first caption sentence says people are in it."""
    title = clean(info.get("title"))
    caption = clean(info.get("description"))
    first = re.split(r"(?<=[.!?])\s+", PREFIX.sub("", caption, count=1) if "---" in caption[:140] else caption)[0]
    text = " ".join([title, " ".join(clean(k) for k in info.get("keywords") or []), " ".join(caption.split()[:50])])
    if NOT_A_PHOTO.search(title) or NOT_A_PHOTO.search(" ".join(text.split()[:40])):
        return ""
    people = has_people(f"{title} {first}")
    for words_of in (title, text):
        for key, words, no_people in THEMES:
            if words.search(words_of) and not (no_people and people):
                return key
    return ""


def picture_link(item):
    """The address of the largest ready-made copy of a library item that is at most about LONG_SIDE pixels, or ""."""
    best, best_side = "", 0
    for link in item.get("links") or []:
        side = max(int(link.get("width") or 0), int(link.get("height") or 0))
        href = link.get("href") or ""
        if link.get("render") == "image" and href.lower().endswith((".jpg", ".jpeg")) \
                and side <= LONG_SIDE * 1.1 and side > best_side:
            best, best_side = href, side
    return best


def credit_of(info):
    """A record's credit line: its title, its maker as NASA writes it, the centre and its page."""
    who = clean(info.get("photographer")) or clean(info.get("secondary_creator")) or "NASA"
    return (f"{clean(info.get('title'))[:120].rstrip('.')}, {who}, NASA {clean(info.get('center'))}, NASA Image and "
            f"Video Library, https://images.nasa.gov/details/{info.get('nasa_id')} (NASA images are not under "
            "copyright)")


def file_name(info):
    """The pack file name of a record: "nasa-" and its NASA id, made safe for a file name."""
    return "nasa-" + re.sub(r"[^\w.-]", "_", clean(info.get("nasa_id")))[:100] + ".jpg"


def library_items(key, limit, s=None):
    """[(file name, picture address, rows)] for one pack: random pages of each of its SEARCHES, keeping the free
    records of its own theme with a usable description (each caption once); records free and of the theme but with
    too short a caption are set aside for a description."""
    s, rng = s or session(), pass_random(sum(map(ord, key)) * 13)
    searches = list(SEARCHES[key])
    want = int(limit * 1.3) + 4
    per_search = want // len(searches) + 2
    items, seen, answers = [], set(), set()
    for query in searches:
        if listing_out_of_time():
            say(f"  {key}: stopped looking at half the time limit")
            break
        first = get_json(s, API, {"q": query, "media_type": "image", "page_size": PAGE_SIZE, "page": 1})
        total = int((((first or {}).get("collection") or {}).get("metadata") or {}).get("total_hits") or 0)
        pages = list(range(1, min(MOST_PAGES, (total + PAGE_SIZE - 1) // PAGE_SIZE) + 1))
        rng.shuffle(pages)
        found = 0
        for page in pages[:20]:
            time.sleep(0.5)
            data = first if page == 1 else get_json(s, API, {"q": query, "media_type": "image",
                                                             "page_size": PAGE_SIZE, "page": page})
            for item in ((data or {}).get("collection") or {}).get("items") or []:
                info = (item.get("data") or [{}])[0]
                nasa_id = clean(info.get("nasa_id"))
                picture = picture_link(item)
                if not nasa_id or nasa_id in seen or not picture or info.get("media_type") != "image":
                    continue
                seen.add(nasa_id)
                if theme_of(info) != key or not nasa_free(info) or already_in_pack(file_name(info), picture):
                    continue
                answer = nasa_answer(info)
                if not answer:
                    words = clean(info.get("description"))
                    if not NOT_SHOWN.search(words):
                        needs_description(file_name(info), picture, credit_of(info), "NASA, not under copyright",
                                          text=words[:500], title=clean(info.get("title")),
                                          page_url=f"https://images.nasa.gov/details/{nasa_id}",
                                          reason="its caption is under six words or only repeats its title",
                                          extra={"keywords": [clean(k) for k in info.get("keywords") or []][:12],
                                                 "date": clean(info.get("date_created"))[:10],
                                                 "centre": clean(info.get("center")),
                                                 "description_508": clean(info.get("description_508"))})
                    continue
                if answer in answers:
                    continue
                answers.add(answer)
                items.append((file_name(info), picture, picture_rows(answer, credit_of(info), "",
                                                                     [clean(info.get("title"))])))
                found += 1
            if found >= per_search:
                break
        if len(items) >= want:
            break
    say(f"  {key}: {len(items)} usable records")
    return items


def build_nasa(key, limit):
    """One NASA library pack (see the module docstring)."""
    return finish(key, library_items(key, limit), limit, workers=4, pause=0.2)


NASA_TERMS = ("NASA Image and Video Library, https://images.nasa.gov : NASA images are not under copyright "
              "(https://www.nasa.gov/nasa-brand-center/images-and-media/); only records crediting NASA, its centres, "
              "JPL-Caltech, STScI or the USGS, with no copyright, courtesy or licence words, are used. Captions by "
              "NASA, each picture's own; its credit and page below.")
NASA_LIBRARY_PACKS = {key: ((lambda limit, key=key: build_nasa(key, limit)), NASA_TERMS) for key in NASA_LIBRARY_KEYS}

# How many pictures a full build takes from each pack (the library has about 230,000 pictures in all).
NASA_LIBRARY_LIMITS = {
    "nasa_planets_telescopes": 3000,   # of about 40,000 planet, Sun and telescope pictures (many are graphics)
    "nasa_earth_from_space": 3000,     # of about 20,000 Earth pictures from orbit
    "nasa_aircraft": 2500,             # of about 15,000 aircraft pictures
    "nasa_people_at_work": 2500,       # of tens of thousands of pictures of NASA people at work
    "nasa_rockets_launch": 3000,       # of about 40,000 launch and launch-site pictures
    "nasa_space_astronauts": 3000,     # of about 60,000 astronaut and spaceflight pictures
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one NASA library pack builder.")
    parser.add_argument("key", choices=sorted(NASA_LIBRARY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = NASA_LIBRARY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
