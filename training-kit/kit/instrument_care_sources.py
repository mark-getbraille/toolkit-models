"""MUSICAL INSTRUMENT CARE AND REPAIR for the Picture Model Training Kit (the owner's request of 2026-11-22). This
file lists:
  - the ready-made packs built in packs/instrument_care_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_string_instrument_parts, commons_wind_percussion_parts, commons_piano_parts,
    commons_instrument_care, open_images_instrument_care;
  - the share-alike Commons files of the main categories (instrument_care_commons_sa: only with the share-alike
    choice);
  - the sources looked at and left out, with the reason (INSTRUMENT_CARE_NOT_INCLUDED).

Already in the kit and not repeated: the Met's CC0 instruments (met_instruments), Wikidata's instruments of the world
(wikidata_instruments), MIMO, the V&A and the Turkish instruments (personal use), instruments in everyday photos
(commons_toys_sports_music, the culture packs), and the electronic instruments' manuals (manual library).

Answers say only what the source says; pickups end with ELECTRIC_NOTE and wooden parts that crack with dry air with
CARE_NOTE (the packs' words). Every licence was checked at its source in November 2026.

Picture-making (INSTRUMENT_CARE_PICTURE_MAKING_OK): none (people play, tune and repair the instruments in many of
these photos).

    python -c "import sources, instrument_care_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

ELECTRIC_NOTE = ("Safety: unplug an electric instrument from the amplifier and the wall before working on it; "
                 "amplifiers hold dangerous voltages inside even when unplugged, so leave their repair to a "
                 "technician.")
CARE_NOTE = ("Wooden instruments crack and warp with dry air and heat: keep them away from heaters and sunny windows, "
             "at a steady humidity.")
COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"


def part(category, words, note="", deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items."""
    return (category, "What instrument part is this?", f"This is {words}." + (f" {note}" if note else ""), deeper)


INSTRUMENT_SA = [
    part("Guitar strings", "a set of guitar strings; strings are changed one at a time so the neck keeps its tension"),
    part("Guitar bridges", "a guitar bridge, which holds the strings on the body and passes their vibration to it"),
    part("Guitar pickups", "a guitar pickup, which turns the strings' vibration into an electrical signal",
         ELECTRIC_NOTE),
    part("Capos", "a capo, clamped across the strings to raise their pitch"),
    part("F-holes", "the f-holes, the f-shaped sound holes in the top of a violin-family instrument", CARE_NOTE),
    part("Rosin", "rosin, rubbed on bow hair so it grips the strings"),
    part("Reeds (music)", "a reed, the thin cane strip that vibrates to make the sound of a clarinet, saxophone or "
                          "similar instrument; store reeds flat in a reed case"),
    part("Drumsticks", "a pair of drumsticks"),
    part("Cymbals", "a cymbal; clean it only with a cleaner made for cymbals"),
    part("Piano tuning", "a piano being tuned: a technician turns the tuning pins with a tuning lever"),
    part("Metronomes", "a metronome, which ticks a steady beat at a chosen speed"),
]


def prepare_instrument_care_commons_sa(source, data_dir, work, cap):
    """Commons instrument part and care categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(INSTRUMENT_SA, cap, source.test, "instrument-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


INSTRUMENT_CARE_SOURCES = [
    Source("commons_string_instrument_parts", "Stringed instrument parts: strings, frets, fingerboards, machine heads "
                                              "and pegs, bridges, pickups, necks, bows and rosin, chinrests, "
                                              "f-holes, sound posts, scrolls, pegboxes, tailpieces, capos and picks "
                                              "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 20, prepare_pack, "about 330 MB"),
    Source("commons_wind_percussion_parts", "Wind and percussion parts: reeds and double reeds, mouthpieces, valves, "
                                            "trumpet mutes, drum heads, drumsticks, cymbals and hi-hats (Wikimedia "
                                            "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_piano_parts", "Piano strings and pedals, piano tuning and piano tuners (Wikimedia "
                                  "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    Source("commons_instrument_care", "Luthiers at work, electronic tuners, tuning forks, metronomes, instrument, "
                                      "guitar and violin cases and music stands (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 700, 10, prepare_pack, "about 150 MB"),
    Source("open_images_instrument_care", "Guitars, ukuleles, mandolins, double basses, bassoons, recorders, brass "
                                          "and mallet instruments, drum heads and drums, capos, music stands, pipe "
                                          "organs and synthesizers (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2500, 25, prepare_pack, "about 500 MB"),
    Source("instrument_care_commons_sa", "Wikimedia Commons: guitar strings, bridges and pickups, capos, f-holes, "
                                         "rosin, reeds, drumsticks, cymbals, piano tuning and metronomes, files under "
                                         "CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_instrument_care_commons_sa,
           "about 170 MB of pictures", terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

INSTRUMENT_CARE_PICTURE_MAKING_OK = set()

INSTRUMENT_CARE_NOT_INCLUDED = {
    "Museum instrument collections (the Met, MIMO, the V&A, Smithsonian)":
        "already in the kit (met_instruments, wikidata_instruments, mimo_instruments, vam, smithsonian); the "
        "Smithsonian's open instruments are reached by the smithsonian entry. Not repeated.",
    "Makers' care guides and pictures (Yamaha, Steinway, Fender, Martin, Taylor, D'Addario, Conn-Selmer, Remo)":
        "copyright of the makers; their care pages are LINKED by the manual library's instrument_care category.",
    "Commons categories that do not exist or hold no files under the names tried (November 2026)":
        "Fretboards, Tuning machines, Nuts (string instruments), Plectrums, Guitar tuners, Shoulder rests, Luthier "
        "workshops, Musical instrument repair, Truss rods, Violin making, Piano making, Piano restoration, Flute and "
        "Saxophone keys, Upright pianos (another pack's), Clarinet, Saxophone, Oboe and Bassoon reeds (Reeds (music) and Double reeds are used), "
        "Mouthpieces (music), Mutes (music), Ligatures (music), Drumheads (Drum heads is used), Drum keys, Piano "
        "actions, Piano hammers, Piano interiors, Piano soundboards; Lutherie, Violin makers, Drum kits and Piano "
        "keys are empty.",
    "Open Images instrument labels already asked elsewhere":
        "Guitar, Violin, Cello, Piano, Musical keyboard, Drum, Snare drum, Cymbal, Trumpet, Trombone, French horn, "
        "Tuba, Saxophone, Clarinet, Flute, Oboe, Harmonica, Accordion, Banjo, Harp, Xylophone and Bagpipes are "
        "other packs'; Bow, Reed and Valve are left out (they name other things too), and the musician labels "
        "(Pianist, Guitarist, Drummer) judge people by role.",
    "YouTube lessons and repair videos, Instructables, Reddit and instrument forums":
        "not read (the owner's rule).",
}
