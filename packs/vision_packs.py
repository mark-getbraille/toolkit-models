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
  aph_museum_objects       The Museum of the American Printing House for the Blind's own items on the Internet
                           Archive that APH marked with the Public Domain Mark (braille writers such as a Russian
                           braillewriter and the Possum Moon writer, talking book phonograph needles, a CCTV, braille
                           duplicators and tactile games): each item's picture with the item's own title (said as its title), and
                           what the museum says about it in its video's subtitles. Museum staff appear in some
                           pictures: describing only.

    python packs/vision_packs.py commons_braille_writing --limit 8      (prints a few rows: a quick check)
"""

import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, clean, listing_out_of_time, fetch_all

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


# ----------------------------------------------------------------- APH Museum (Internet Archive, Public Domain Mark)

IA_SEARCH = "https://archive.org/advancedsearch.php"
APH_QUERY = ('collection:aphmigel AND licenseurl:("https://creativecommons.org/publicdomain/mark/1.0/" OR '
             '"http://creativecommons.org/publicdomain/mark/1.0/")')
# Only APH's own work: the museum's items ("museum-...") whose creator is APH or its museum director (the same rule
# as textbooks/vision_living.py); APH's mark on other people's work is not the author's own.
APH_AUTHORS = re.compile(r"^(American Printing House for the Blind|M[Ii]ke Hudson|Mic(ha|he)al Hudson)$")
APH_DATE = re.compile(r"^(museum\s+)?\d{4}[ -]\d{2}[ -]\d{1,2}\s+(\d{4}-\d{2}-\d{2}\s+)?", re.I)
APH_GREETING = re.compile(r"^.*?(Director|Curator) of the Museum (of|at) the American Printing House for the "
                          r"Blind[^.]*\.\s*", re.I | re.S)
APH_MUSEUM = "Museum of the American Printing House for the Blind (APH)"


def aph_title(title):
    """An APH museum item's title without its leading date ("Museum 2022 02 21 Russian Braillewriter" -> "Russian
    Braillewriter")."""
    return APH_DATE.sub("", clean(title)).strip(" -") or clean(title)


def aph_words(srt):
    """The first words the museum says about the object in its video (the subtitles without numbers, times and
    the greeting), at most about 60 words ending at a full stop, or ""."""
    cues = [" ".join(ln.strip() for ln in block.splitlines() if ln.strip() and not ln.strip().isdigit() and
                     "-->" not in ln) for block in re.split(r"\n\s*\n", (srt or "").replace("\r", ""))]
    text = APH_GREETING.sub("", " ".join(c for c in cues if c)).strip()
    words = text.split()
    if len(words) < 12:
        return ""
    cut = " ".join(words[:60])
    return cut[:cut.rfind(".") + 1] if "." in cut[40:] else ""


def aph_row(ident, title, files, srt=""):
    """(picture address, rows) of one APH museum item: its own JPEG (not a thumbnail), "What is this?" answered with
    the item's own title (said as the item's title: the picture may be a still of a video about it), and what the museum says about it in its video's subtitles; or None without a JPEG."""
    jpeg = next((f for f in files if f.lower().endswith((".jpg", ".jpeg")) and "thumb" not in f.lower()
                 and "/" not in f), None)
    if not jpeg:
        return None
    name = aph_title(title)
    credit = f"{APH_MUSEUM}, Public Domain Mark 1.0: \"{clean(title)}\", https://archive.org/details/{ident}"
    rows = [{"question": ASK_WHAT, "answer": f"It is a picture from the {APH_MUSEUM}'s item \"{name}\" (its own "
                                             f"title for it).", "credit": credit}]
    said = aph_words(srt)
    if said:
        rows.append({"question": "What does the museum say about this?", "answer": said, "credit": credit})
    from urllib.parse import quote
    return f"https://archive.org/download/{ident}/{quote(jpeg)}", rows


def build_aph_museum_objects(limit):
    """The aph_museum_objects pack: the APH Museum's own Internet Archive items marked with the Public Domain Mark,
    each item's picture with its title and the first words of its video's subtitles."""
    import urllib.parse
    s = session()
    q = urllib.parse.urlencode([("q", APH_QUERY), ("fl[]", "identifier"), ("fl[]", "title"), ("fl[]", "creator"),
                                ("rows", "1000"), ("output", "json")])
    docs = s.get(f"{IA_SEARCH}?{q}", timeout=120).json()["response"]["docs"]
    items = []
    for d in sorted(docs, key=lambda x: x["identifier"]):
        creators = d.get("creator") if isinstance(d.get("creator"), list) else [d.get("creator") or ""]
        if not d["identifier"].startswith("museum-") or not all(APH_AUTHORS.match(str(c).strip()) for c in creators):
            continue
        if len(items) >= limit * 1.2 or listing_out_of_time():
            break
        try:
            meta = s.get(f"https://archive.org/metadata/{d['identifier']}", timeout=120).json()
        except Exception:  # noqa: BLE001 - next item
            continue
        if "publicdomain/mark" not in str((meta.get("metadata") or {}).get("licenseurl", "")):
            continue
        files = [f.get("name", "") for f in meta.get("files") or []]
        srt_file = next((f for f in files if f.endswith(".srt")), "")
        srt = ""
        if srt_file:
            try:
                srt = s.get(f"https://archive.org/download/{d['identifier']}/{urllib.parse.quote(srt_file)}",
                            timeout=120).text
            except Exception:  # noqa: BLE001 - the picture without the museum's words
                srt = ""
        got = aph_row(d["identifier"], str(d.get("title") or d["identifier"]), files, srt)
        if got:
            items.append((f"aph-{len(items):04d}.jpg", got[0], got[1]))
    say(f"APH Museum: {len(items)} items with a picture")
    from food_packs import with_twins
    return with_twins(fetch_all(items, workers=2, pause=1.0)[:limit])


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
VISION_PACKS = {
    "commons_braille_writing": (build_commons_braille_writing, COMMONS_LICENCE.format(
        what="braille writer, braille chart, braille music, tactile watch, DAISY and tactile writing system")),
    "commons_tactile_access": (build_commons_tactile_access, COMMONS_LICENCE.format(
        what="tactile graphic, tactile model, large print, reading machine, eye chart and accessible place")),
    "commons_mobility_deafblind": (build_commons_mobility_deafblind, COMMONS_LICENCE.format(
        what="orientation and mobility, sighted guide, cane, guide horse, awareness and deafblind")),
    "aph_museum_objects": (build_aph_museum_objects, f"{APH_MUSEUM}, its own items on the Internet Archive marked "
                                                     "with the Public Domain Mark 1.0 by APH "
                                                     "(https://archive.org/details/aphmigel; checked item by item), "
                                                     "each credited below. Changes: pictures made smaller; answers "
                                                     "from each item's title and its video's subtitles."),
}
VISION_LIMITS = {
    "commons_braille_writing": 400,       # 23 small categories (Perkins 17 files, the charts and New York Point most)
    "commons_tactile_access": 600,        # 24 categories; the scale models and eye charts have most files
    "commons_mobility_deafblind": 150,    # 8 small categories
    "aph_museum_objects": 80,             # about 80 of the museum's own items carry the Public Domain Mark
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
    args = parser.parse_args(argv)
    entries = VISION_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
