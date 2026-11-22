"""Picture packs for BLIND AND LOW-VISION LIVING (the owner's request of 2026-11-22, a section of its own). Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row)
rows naming the same picture. The limit counts pictures.

Why: the owner is blind (a braille transcriber who uses JAWS and NVDA). He wants the picture describer to know the
things of blind and low-vision life by name: braille writers (Perkins Braillers and the others) and their care,
slates, braille charts and braille in daily life, tactile graphics, tactile models and maps, large print, talking
and reading machines, eye charts, canes, sighted guiding and orientation and mobility training, and the writing
systems and hand alphabets of blind and deafblind people.

Much was already in other packs and is NOT repeated here (each Commons category is asked by one pack only;
packs/test_vision.py checks): white canes, guide dogs, braille texts and publications, braille by country,
refreshable braille displays, braille writing instruments and keyboards, people reading braille, tactile paving,
screen readers and magnifiers, goalball and blind football (disability_packs: commons_disability), braille signs and
lift buttons with braille (home_safety_packs: commons_access_features), braille embossers and printers, talking
clocks, monoculars and the optophone (electronics_packs: commons_assistive_devices), magnifying glasses, loupes and
Snellen charts (home_health_packs: commons_eye_care), audible traffic signals and pedestrian push buttons
(street_scene_packs), tactile maps (indoor_packs) and the touch features of US and Canadian money
(everyday_extras_packs: commons_money_sides). The kit's topic "vision" gathers those packs with these.

Answers say only what the source says: a Commons category's own name (a Perkins braille typewriter category is
answered "a Perkins braille writer"), or a museum record's own object name, maker, date, place and materials. No
part of a machine is named unless the source names it. Every braille writer answer ends with the care note
(BRAILLER_NOTE), the same words as the kit's vision_sources.py.

The packs (VISION_PACKS):
  commons_braille_writing  Wikimedia Commons (CC0, public domain or CC BY files only): braille writers by maker
                           (Perkins, Blista, Picht, Mountbatten, Tatrapoint, Stainsby, Light, Writer, Mignon, Herde &
                           Wendt), manual braille embossers and the Moon writer, braille alphabet charts, braille
                           numbers and icons, braille music, braille measuring tools, World Braille Day, watches for
                           blind people, DAISY, and the other tactile writing systems (Moon, New York Point, night
                           writing).
  commons_tactile_access   Commons: tactile graphics, tactile picture books, tactile plaques and signs, scale models
                           for blind people, relief symbols at crossings, high-contrast step markings, ColorADD colour
                           symbols, games for blind people, large print, reading machines (Kurzweil, Optacon, the
                           Library of Congress cassette player, Tellatouch, Elektroftalm), telephones for blind
                           people, eye charts, near vision charts and optotypes, and parks, sensory gardens, museums
                           and libraries for blind people.
  commons_mobility_deafblind  Commons: orientation and mobility training, sighted guides, people with mobility
                           canes, guide horses, simulated visual impairment (training with blindfolds or simulation
                           glasses), visual impairment awareness events, deafblind people and the Lorm hand alphabet.
                           People are in these photos: describing only, never picture-making.
  nmah_vision_objects      The Smithsonian's National Museum of American History (open-access records, CC0): braille
                           writers, slates and styluses, talking book machines, reading machines, canes and other
                           things made for blind people, named from each record's own words (a fair share for each
                           kind of object).

    python packs/vision_packs.py commons_braille_writing --limit 8      (prints a few rows: a quick check)
"""

import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, pass_random, listing_out_of_time, fetch_all, SI_BUCKET, si_keys

ASK_WHAT = "What is this?"
ASK_DOING = "What is happening here?"

# The care note every braille writer answer ends with (the kit's vision_sources.py says the same words).
BRAILLER_NOTE = ("Care: follow the maker's care guide, keep it covered and free of dust, and use braille paper; if "
                 "a key sticks or the paper will not feed, do not force it: ask the maker or a braille writer repair "
                 "service.")
# The note for answers about orientation and mobility (canes, guiding) and about crossing streets.
MOBILITY_NOTE = ("Orientation and mobility skills are taught by a certified orientation and mobility (O&M) "
                 "specialist; in the US, state services for the blind and the VA arrange training.")


def thing(category, words, note="", deeper=False, question=ASK_WHAT):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, "This is <words>." and the
    note)])."""
    return (category, deeper, [(question, f"This is {words}." + (f" {note}" if note else ""))])


def writer(category, words, deeper=False):
    """A braille writer's Commons spec: "This is <words>." and the care note."""
    return thing(category, words, BRAILLER_NOTE, deeper)


# ----------------------------------------------------------------- Commons: braille and writing

BRAILLE_WRITING = [
    writer("Perkins braille typewriters", "a Perkins braille writer (a Perkins Brailler), a machine for typing "
                                          "braille on paper"),
    writer("Blista braille typewriter", "a Blista braille writer, a machine for typing braille on paper"),
    writer("Picht braille typewriters", "a Picht braille writer, a machine for typing braille on paper"),
    writer("Mountbatten braille typewriters", "a Mountbatten braille writer, an electric machine for typing braille"),
    writer("Tatrapoint braille typewriters", "a Tatrapoint braille writer, a machine for typing braille on paper"),
    writer("Henry Stainsby braille typewriters", "a Stainsby braille writer (Henry Stainsby's design), a machine "
                                                 "for writing braille"),
    writer("Light braille typewriters", "a Light braille writer, a machine for typing braille on paper"),
    writer("Writer braille typewriters", "a braille writer of the make named Writer, a machine for typing braille"),
    writer("Mignon braille typewriters", "a Mignon braille writer, a machine for typing braille"),
    writer("Herde & Wendt Braille typewriters", "a Herde & Wendt braille writer, a machine for typing braille"),
    writer("Braille manual embossers", "a manual braille embosser, a hand-worked machine that presses braille dots "
                                       "into paper or metal"),
    writer("Moon writer", "a Moon writer, a frame for writing Moon type, a raised-line alphabet for blind readers"),
    thing("Braille alphabet charts", "a braille alphabet chart, showing the letters as braille cells"),
    thing("Braille numbers", "braille numbers", deeper=True),
    thing("Braille icons", "a braille icon or symbol"),
    thing("Braille musical notation", "braille music notation, the braille code for writing music"),
    thing("Braille measurement", "a measuring tool marked in braille"),
    thing("World Braille Day", "something marking World Braille Day (4 January, Louis Braille's birthday)"),
    thing("Watches for people with visual impairment", "a watch made for blind or low-vision people: a tactile "
                                                       "watch to read by touch, or a talking watch"),
    thing("Digital Accessible Information System (DAISY)", "something about DAISY, the format of digital talking "
                                                           "books that can be navigated by chapter and page"),
    thing("Moon alphabet", "Moon type (the Moon alphabet), a raised alphabet of simple shapes for blind readers",
          deeper=True),
    thing("New York Point", "New York Point, a raised-dot writing system for blind readers used in the United "
                            "States before braille replaced it"),
    thing("Night Writing", "night writing, the raised-dot code of Charles Barbier from which Louis Braille made "
                           "braille"),
]

# ----------------------------------------------------------------- Commons: tactile things, reading machines, low vision

TACTILE_ACCESS = [
    thing("Tactile graphics", "a tactile graphic: a raised picture, diagram or map to read by touch"),
    thing("Tactile picture books", "a tactile picture book, with raised pictures to feel, often with braille"),
    thing("Tactile plaques and signs", "a tactile plaque or sign, with raised letters, pictures or braille to read "
                                       "by touch", deeper=True),
    thing("Scale models for people with visual impairment", "a scale model to explore by touch, made for blind and "
                                                            "low-vision visitors", deeper=True),
    thing("Pedestrian crossing relief symbols", "a relief symbol at a pedestrian crossing: a raised plan of the "
                                                "crossing to feel with the fingers", MOBILITY_NOTE),
    thing("High-contrast step markings", "high-contrast step markings: bright strips on the edges of steps so "
                                         "people with low vision can see them", deeper=True),
    thing("ColorADD", "ColorADD, a code of simple symbols that name colours, for colour-blind people"),
    thing("Games for people with visual impairment", "a game made for blind or low-vision players", deeper=True),
    thing("Large print", "large print: text printed big for people with low vision"),
    thing("Kurzweil reader", "a Kurzweil reading machine, which scans printed pages and reads them aloud"),
    thing("Optacon", "an Optacon, a reading device that turned printed letters into a pattern of vibrating pins "
                     "felt with a fingertip"),
    thing("Reading Machine", "a reading machine for blind people", deeper=True),
    thing("Library Of Congress C1 cassette player", "a Library of Congress C1 cassette player, a talking-book "
                                                    "cassette player lent to blind readers by the National Library "
                                                    "Service"),
    thing("Tellatouch", "a Tellatouch, a typewriter-like machine that shows each typed letter in braille under a "
                        "deafblind person's fingertip"),
    thing("Elektroftalm", "an Elektroftalm, an early electronic device that turned light into touch or sound for "
                          "blind people"),
    thing("Telephones for people with visual impairment", "a telephone made for blind or low-vision people",
          deeper=True),
    thing("Eye charts", "an eye chart, for testing how well someone sees"),
    thing("Near vision charts", "a near vision chart, for testing reading vision close up"),
    thing("Optotypes", "optotypes, the letters or symbols on an eye chart", deeper=True),
    thing("Sloan letters", "Sloan letters, the letters used on modern eye charts"),
    thing("Parks for people with visual impairment", "a park or garden made for blind and low-vision visitors, "
                                                     "with things to touch, smell and hear", deeper=True),
    thing("Sensory gardens", "a sensory garden, planted for touch, smell and sound", deeper=True),
    thing("Museums for people with visual impairment", "a museum, or a part of one, made for blind and low-vision "
                                                       "visitors", deeper=True),
    thing("Libraries for people with visual impairment", "a library for blind and low-vision readers (braille, "
                                                         "talking books and large print)", deeper=True),
]

# ----------------------------------------------------------------- Commons: mobility, guiding and deafblind life

MOBILITY_DEAFBLIND = [
    thing("Orientation and mobility training", "orientation and mobility training: learning to travel safely "
                                               "without sight, for example with a long cane", MOBILITY_NOTE,
          question=ASK_DOING),
    thing("Sighted guides", "sighted guiding: the blind person holds the guide's arm just above the elbow and "
                            "walks half a step behind", deeper=True, question=ASK_DOING),
    thing("People with mobility canes", "a person travelling with a mobility cane (a long white cane)",
          MOBILITY_NOTE, question=ASK_DOING),
    thing("Guide horses", "a guide horse, a miniature horse trained to guide a blind person"),
    thing("Simulated visual impairment", "simulated visual impairment: someone sighted wearing a blindfold or "
                                         "simulation glasses, to learn what low vision or blindness is like",
          question=ASK_DOING),
    thing("Visual impairment awareness", "a visual impairment awareness event (such as White Cane Day)",
          deeper=True, question=ASK_DOING),
    thing("Deafblind people", "a deafblind person or people (people who have both hearing and sight loss)",
          deeper=True, question=ASK_DOING),
    thing("Lorm alphabet", "the Lorm alphabet, a hand-touch alphabet: letters are spelled by touching and stroking "
                           "places on the deafblind person's palm"),
]


def build_commons_braille_writing(limit):
    """The commons_braille_writing pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(BRAILLE_WRITING, limit, "visbraille")


def build_commons_tactile_access(limit):
    """The commons_tactile_access pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(TACTILE_ACCESS, limit, "vistactile")


def build_commons_mobility_deafblind(limit):
    """The commons_mobility_deafblind pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MOBILITY_DEAFBLIND, limit, "vismobility")


# ----------------------------------------------------------------- Smithsonian NMAH: things made for blind people (CC0)

# Object names (the record's "Object Name" or title) with the plain name the answer gives; the first that matches.
NMAH_VISION_NAMES = [(re.compile(p, re.I), n, care) for p, n, care in [
    (r"\bbraille ?writers?\b|\bbraillewriters?\b|\bbraillers?\b|\bbraille typewriters?\b|\bwriters?,? braille\b",
     "a braille writer (a machine for typing braille)", True),
    (r"\bslates?\b", "a braille slate (a frame for writing braille by hand with a stylus)", False),
    (r"\bstyl(us|i|uses)\b", "a braille stylus (a pointed tool for punching braille dots by hand)", False),
    (r"\btalking[- ]book\b|\btalking[- ]book (machine|player|phonograph)s?\b", "a talking book machine or record",
     False),
    (r"\boptacon\b", "an Optacon (a reading device that turned print into a pattern of vibrating pins)", False),
    (r"\bkurzweil\b|\breading machines?\b", "a reading machine for blind people", False),
    (r"\bcanes?\b", "a cane", False),
    (r"\bwatch(es)?\b|\bclocks?\b", "a watch or clock made for blind people", False),
    (r"\bmaps?\b|\bglobes?\b", "a tactile (raised) map or globe", False),
    (r"\btypewriters?\b", "a typewriter made for blind people", False),
    (r"\bbooks?\b|\bprimers?\b|\breaders?\b", "a book in braille or raised type", False),
]]
# Only records whose own words say they are for blind people.
NMAH_VISION_WORDS = re.compile(r"braille|\bblind\b|visually impaired|visual impairment|talking book|optacon|kurzweil|"
                               r"moon type|new york point|raised (type|print|letters?)", re.I)
NMAH_VISION_NOT = re.compile(r"\b(photograph|print|poster|lithograph|negative|postcard|stamp|coin|medal|button|pin|"
                             r"advertis\w*|trade card|catalog(ue)?|sheet music|label|flag|banner|blinds?\b.*window|"
                             r"venetian|window blinds?)\b", re.I)


def nmah_vision_row(record):
    """(picture address, rows) for an NMAH record of a thing made for blind people with a CC0 picture, or None. The
    answer gives the object's own name, maker, date and place as catalogued (textile_crafts_packs.nmah_textile_row
    does the same for sewing things)."""
    content = record.get("content") or {}
    title = clean(record.get("title") or "")
    free = content.get("freetext") or {}
    names = [clean(o.get("content")) for o in free.get("objectType") or [] if o.get("label") == "Object Name"]
    object_name = names[0] if names else title
    notes = " ".join(clean(n.get("content")) for n in free.get("notes") or [])
    words = f"{object_name} {title} {notes}"
    if not NMAH_VISION_WORDS.search(words) or NMAH_VISION_NOT.search(f"{object_name} {title}"):
        return None
    found = next(((n, care) for p, n, care in NMAH_VISION_NAMES if p.search(object_name)), None) or \
        next(((n, care) for p, n, care in NMAH_VISION_NAMES if p.search(title)), None)
    if not found:
        return None
    plain, care = found
    media = ((content.get("descriptiveNonRepeating") or {}).get("online_media") or {}).get("media") or []
    picture = next((m for m in media if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"
                    and m.get("content")), None)
    if not picture:
        return None
    makers = [clean(n.get("content")) for n in free.get("name") or [] if "maker" in (n.get("label") or "").lower()
              or "manufacturer" in (n.get("label") or "").lower()]
    makers = [m for m in makers if not re.match(r"^(unknown|unidentified|anonymous)\b", m, re.I)]
    dates = [clean(d.get("content")) for d in free.get("date") or [] if "made" in (d.get("label") or "").lower()]
    places = [clean(p.get("content")) for p in free.get("place") or [] if "made" in (p.get("label") or "").lower()]
    answer = f"This is {plain}"
    if title and title.lower() not in plain.lower():
        answer += f" (its record calls it \"{title}\")"
    if makers:
        answer += f", made by {makers[0]}"
    if places:
        answer += (" in " if makers else ", made in ") + places[0].replace("United States: ", "")
    if dates:
        answer += f", {dates[0]}"
    answer += "."
    if care:
        answer += f" {BRAILLER_NOTE}"
    nr = content.get("descriptiveNonRepeating") or {}
    credit = (f"National Museum of American History, Smithsonian Institution, CC0: {title} "
              f"({nr.get('record_ID', '')}), {nr.get('guid', '')}")
    return picture["content"] + "&max=2048", [{"question": ASK_WHAT, "answer": answer, "credit": credit}]


def build_nmah_vision_objects(limit, most_files=None):
    """The NMAH records of things made for blind people with a CC0 picture, read from the Smithsonian open-access
    bucket (the museum's metadata files in a fixed shuffled order, a quick word check before each record is read),
    until enough are found or half the time limit is spent; each kind of object gets a fair share. most_files: read
    at most so many metadata files (a quick live check)."""
    s, by_kind = session(), {}
    keys = si_keys("nmah")
    pass_random("nmah-vision").shuffle(keys)
    found = 0
    for key in keys[:most_files] if most_files else keys:
        if listing_out_of_time() or found >= limit * 2:
            break
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=300).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            if '"CC0"' not in line or not NMAH_VISION_WORDS.search(line):
                continue
            try:
                got = nmah_vision_row(json.loads(line))
            except ValueError:
                continue
            if got:
                url, rows = got
                kind = rows[0]["answer"].split(" (", 1)[0].split(",", 1)[0].split(".", 1)[0]
                by_kind.setdefault(kind, []).append((url, rows))
                found += 1
        say(f"  NMAH {key.rsplit('/', 1)[-1]}: {found} records so far")
    items, share = [], max(10, int(limit * 1.2) // max(1, len(by_kind)))
    for kind in sorted(by_kind):
        items += by_kind[kind][:share]
    pass_random("nmah-vision-order").shuffle(items)
    from food_packs import with_twins
    named = [(f"nmah-vis-{i:05d}.jpg", url, rows) for i, (url, rows) in enumerate(items[:int(limit * 1.1) + 2])]
    return with_twins(fetch_all(named, workers=6, pause=0.1)[:limit])


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
NMAH_LICENCE = ("Smithsonian National Museum of American History, Smithsonian Open Access, CC0 "
                "(https://www.si.edu/openaccess): records and pictures of things made for blind people, each record "
                "credited below. Changes: pictures made smaller; answers written from each record's own words.")
VISION_PACKS = {
    "commons_braille_writing": (build_commons_braille_writing, COMMONS_LICENCE.format(
        what="braille writer, braille chart, braille music, tactile watch, DAISY and tactile writing system")),
    "commons_tactile_access": (build_commons_tactile_access, COMMONS_LICENCE.format(
        what="tactile graphic, tactile model, large print, reading machine, eye chart and accessible place")),
    "commons_mobility_deafblind": (build_commons_mobility_deafblind, COMMONS_LICENCE.format(
        what="orientation and mobility, sighted guide, cane, guide horse, awareness and deafblind")),
    "nmah_vision_objects": (build_nmah_vision_objects, NMAH_LICENCE),
}
VISION_LIMITS = {
    "commons_braille_writing": 400,       # 23 small categories (Perkins 17 files, the charts and New York Point most)
    "commons_tactile_access": 600,        # 24 categories; the scale models and eye charts have most files
    "commons_mobility_deafblind": 150,    # 8 small categories
    "nmah_vision_objects": 120,           # few NMAH records are CC0 and made for blind people
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
VISION_COMMONS_KEYS = ("commons_braille_writing", "commons_tactile_access", "commons_mobility_deafblind")
# The Commons category specs of the packs (for the self-test).
VISION_SPECS = BRAILLE_WRITING + TACTILE_ACCESS + MOBILITY_DEAFBLIND


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try a blind and low-vision living pack builder.")
    parser.add_argument("key", choices=sorted(VISION_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--files", type=int, default=None, help="NMAH: read at most so many metadata files")
    args = parser.parse_args(argv)
    if args.key == "nmah_vision_objects":
        entries = build_nmah_vision_objects(args.limit, args.files)
    else:
        entries = VISION_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
