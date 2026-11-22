"""BLIND AND LOW-VISION LIVING for the Picture Model Training Kit (the owner's request of 2026-11-22, a section of
its own with the topic add-on "vision"). This file lists:
  - the ready-made packs built in packs/vision_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_braille_writing, commons_tactile_access, commons_mobility_deafblind,
    nmah_vision_objects and aph_museum_objects;
  - the share-alike Commons files of the same braille writer, braille and tactile categories (group "share-alike":
    only with the share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (VISION_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by
the kit on the user's own computer, straight from where its makers publish it (the packs from the kit's own release),
only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a museum record's own words); every
braille writer answer ends with the care note (BRAILLER_NOTE, the same words as packs/vision_packs.py:
packs/test_vision.py checks).

Picture-making (VISION_PICTURE_MAKING_OK): only the braille writers, braille charts and tactile things, which show
no people (commons_braille_writing, nmah_vision_objects and the share-alike entry); sources.py puts the other keys
in NOT_FOR_PICTURE_MAKING (orientation and mobility, guiding and deafblind photos show people, and the tactile
collection holds parks, museums and libraries with visitors).

The topic add-on "vision" (topics.py) gathers these with the packs other files already had: white canes, guide dogs,
braille and screen readers (commons_disability), tactile paving (tapad_tactile_paving), braille signs
(commons_access_features), braille embossers and talking clocks (commons_assistive_devices), magnifiers and eye care
things (commons_eye_care), crossings and accessible pedestrian signals (commons_crosswalks_signals), indoor
wayfinding and tactile maps (commons_indoor_wayfinding), money by touch (commons_money_sides), and the braille page
photos (angelina_braille, dsbi_braille, personal use).

    python -c "import sources, vision_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# The care note, word for word as in packs/vision_packs.py.
BRAILLER_NOTE = ("Care: follow the maker's care guide, keep it covered and free of dust, and use braille paper; if "
                 "a key sticks or the paper will not feed, do not force it: ask the maker or a braille writer repair "
                 "service.")

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
NMAH_OPEN = "CC0 (Smithsonian Open Access), each record credited in CREDITS.txt"
NMAH_CREDIT = "National Museum of American History, Smithsonian Institution, https://www.si.edu/openaccess"
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def item(category, words, notes="", deeper=False):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the notes."""
    return (category, "What is this?", f"This is {words}." + (f" {notes}" if notes else ""), deeper)


# The braille writer, braille and tactile categories of packs/vision_packs.py whose files show things, not people
# (the same answers as the packs).
VISION_SA = [
    item("Perkins braille typewriters", "a Perkins braille writer (a Perkins Brailler), a machine for typing braille "
                                        "on paper", BRAILLER_NOTE),
    item("Picht braille typewriters", "a Picht braille writer, a machine for typing braille on paper", BRAILLER_NOTE),
    item("Blista braille typewriter", "a Blista braille writer, a machine for typing braille on paper", BRAILLER_NOTE),
    item("Braille manual embossers", "a manual braille embosser, a hand-worked machine that presses braille dots "
                                     "into paper or metal", BRAILLER_NOTE),
    item("Braille alphabet charts", "a braille alphabet chart, showing the letters as braille cells"),
    item("Braille numbers", "braille numbers", deeper=True),
    item("Braille musical notation", "braille music notation, the braille code for writing music"),
    item("Moon alphabet", "Moon type (the Moon alphabet), a raised alphabet of simple shapes for blind readers",
         deeper=True),
    item("New York Point", "New York Point, a raised-dot writing system for blind readers used in the United States "
                           "before braille replaced it"),
    item("Tactile graphics", "a tactile graphic: a raised picture, diagram or map to read by touch"),
    item("Tactile picture books", "a tactile picture book, with raised pictures to feel, often with braille"),
    item("Optacon", "an Optacon, a reading device that turned printed letters into a pattern of vibrating pins felt "
                    "with a fingertip"),
    item("Eye charts", "an eye chart, for testing how well someone sees"),
]


def prepare_vision_commons_sa(source, data_dir, work, cap):
    """Commons braille writer, braille, tactile and eye chart categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(VISION_SA, cap, source.test, "vision-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

VISION_SOURCES = [
    Source("commons_braille_writing", "Braille writers (Perkins and other makers) with their care note, braille "
                                      "charts, numbers and music, tactile watches, DAISY, and the Moon, New York "
                                      "Point and night-writing systems (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 5, prepare_pack, "about 90 MB"),
    Source("commons_tactile_access", "Tactile graphics, models, plaques and picture books, crossing relief symbols, "
                                     "step markings, large print, reading machines, eye charts, and parks, museums "
                                     "and libraries for blind people (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 8, prepare_pack, "about 130 MB"),
    Source("commons_mobility_deafblind", "Orientation and mobility training, sighted guiding, mobility canes, guide "
                                         "horses, awareness events, deafblind people and the Lorm alphabet "
                                         "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 150, 3, prepare_pack, "about 35 MB"),
    Source("nmah_vision_objects", "Braille writers, slates, styluses, talking book machines, reading machines and "
                                  "other things made for blind people (Smithsonian NMAH, ready-made pack)",
           NMAH_OPEN, NMAH_CREDIT, "permissive", 120, 3, prepare_pack, "about 30 MB"),
    Source("aph_museum_objects", "The APH Museum's own items marked public domain: braille writers, the Moon writer, "
                                 "talking book things, a CCTV and tactile games, with the museum's own words "
                                 "(Internet Archive, ready-made pack)",
           "Public Domain Mark 1.0, put by the Museum of the American Printing House for the Blind on its own items "
           "(checked item by item)", "Museum of the American Printing House for the Blind, "
           "https://archive.org/details/aphmigel", "permissive", 80, 3, prepare_pack, "about 20 MB"),
    Source("vision_commons_sa", "Wikimedia Commons: braille writers, braille charts and music, Moon type, New York "
                                "Point, tactile graphics and picture books, the Optacon and eye charts, files under "
                                "CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 300, 5, prepare_vision_commons_sa, "about 70 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: things only (braille writers, braille, tactile writing and
# museum objects); never the mobility and deafblind photos or the tactile places, which show people.
VISION_PICTURE_MAKING_OK = {"commons_braille_writing", "nmah_vision_objects", "vision_commons_sa"}

# The collections the topic add-on "vision" gathers from other files (topics.py names them; the self-test checks
# that each is a collection of the kit).
VISION_TOPIC_KEYS_ELSEWHERE = ("commons_disability", "tapad_tactile_paving", "commons_access_features",
                               "commons_assistive_devices", "commons_eye_care", "commons_crosswalks_signals",
                               "commons_indoor_wayfinding", "commons_money_sides", "commons_disability_sa",
                               "angelina_braille", "dsbi_braille")

VISION_NOT_INCLUDED = {
    "Commons categories already used by other packs": "White canes, Guide dogs, Braille texts, Braille publications, "
        "Braille by country, Refreshable Braille displays, Braille writing instruments (with Braille typewriters' "
        "own files), Braille keyboards, People reading Braille, Tactile paving, Screen readers and Screen magnifiers "
        "(disability_packs), Braille signage and lift buttons (home_safety_packs), Braille embossers and printers, "
        "Talking clocks, Monoculars and Optophone (electronics_packs), Magnifying glasses, Loupes and Snellen charts "
        "(home_health_packs), Audible traffic signals (street_scene_packs), Tactile maps (indoor_packs): not asked "
        "twice.",
    "Commons categories that do not exist under the names tried (November 2026)": "Slates and styluses, Braille "
        "slates, Hall Braille Writer, Lavender braille typewriters, Guide dog harnesses, Seeing Eye, Guide Dogs for "
        "the Blind, Orientation and mobility, Accessible pedestrian signals, Braille labels, Braille on packaging, "
        "Braille on medicine packaging, Braille on banknotes, Braille playing cards, Large print books, Low vision "
        "aids, Talking books and Touch tours; Tactile models exists but holds no files.",
    "Schools for the blind and Louis Braille on Commons": "Mostly buildings, portraits, statues and pupils by name "
        "(28 and 9 subcategories); not a subject of things to recognise, so left out.",
    "APH Museum items not by APH": "The collection on the Internet Archive (aphmigel, 11,493 items) also marks other "
        "people's work with the Public Domain Mark (AFB slides, Helen Keller's and John Macy's writings, letters, "
        "scrapbooks) and leaves most items unmarked; only the museum's own marked items are used "
        "(aph_museum_objects, and the book vision:aph_museum_articles).",
    "Perkins School for the Blind archives and the Perkins Brailler maintenance guides": "perkins.org refuses "
        "programs (403, checked 2026-11-22) and its archive photos' licences were not stated; the Perkins Brailler "
        "maintenance guide on the Internet Archive carries no licence (Perkins' copyright). Link-only in the "
        "manual collection vision_devices.",
    "HathiTrust": "catalog.hathitrust.org and www.hathitrust.org answer programs with a challenge page (Cloudflare), "
                  "so nothing is read; link-only.",
    "Open Images": "no label for white canes, guide dogs, braille or braille writers (disability_packs' search of the "
                   "class list).",
    "Be My Eyes, Seeing AI, Aira and other describer apps' pictures": "the companies' copyright; never used.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the blind and low-vision living share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in VISION_SOURCES if s.key == "vision_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="vision-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
