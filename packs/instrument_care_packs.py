"""Picture packs for MUSICAL INSTRUMENT CARE AND REPAIR: the parts of instruments by name (strings, frets and
fingerboards, tuning pegs and machine heads, bridges, nuts, pickups, bows and rosin, chinrests, f-holes, sound posts
and scrolls; reeds, mouthpieces, ligatures, valves and mutes; drumheads, drum keys, drumsticks and cymbals; piano
actions, hammers, strings and soundboards), the tools and accessories of care (tuners, tuning forks, metronomes, capos,
picks, cases), and luthiers' and piano technicians' work. Used by build_packs.py in the same way as its own PACKS:
each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]. The limit counts pictures.

The owner's request of 2026-11-22 ("life skills"). Instruments as whole museum objects are already in the kit (the
Met's CC0 instruments, met_instruments; Wikidata's instruments of the world, wikidata_instruments; MIMO, the V&A and
the Turkish instruments, personal use) and instruments people play in everyday photos are in everyday_extras_packs'
commons_toys_sports_music and the culture packs; nothing of theirs is asked again (packs/test_instrument_care.py
checks every Commons category and Open Images label). Electronic instruments, amplifiers and effects pedals belong
to the electronics helper (repair) and the manuals library (musical_instruments).

Answers say only what the source says: a Commons category's name with a fixed line written here about what the part
does, or an Open Images label people confirmed. Notes:
  ELECTRIC_NOTE  after answers about pickups and electric instruments: unplug from the amplifier and the wall before
                 working on them; amplifiers hold dangerous voltages inside even when unplugged.
  CARE_NOTE      after answers about wooden instruments' parts that crack or warp with dry air or heat (bodies,
                 soundboards, fingerboards): keep them away from heaters and sunny windows, at a steady humidity.

The packs (all open: CC0, public domain or CC BY files; Open Images labels CC BY 4.0):
  commons_string_instrument_parts  Commons: guitar strings, frets and fingerboards, machine heads and tuning pegs,
                                   guitar bridges, nuts, pickups, truss rods, headstocks, bows and rosin, chinrests,
                                   shoulder rests, violin bridges, f-holes, sound posts, scrolls, pegboxes and
                                   tailpieces, capos and picks.
  commons_wind_percussion_parts    Commons: reeds (clarinet, saxophone, oboe and bassoon reeds), mouthpieces,
                                   ligatures, piston and rotary valves, mutes, woodwind keys and pads, drumheads,
                                   drum keys, drumsticks, hi-hats and cymbals.
  commons_piano_parts              Commons: piano actions, hammers, keys, strings, pedals and soundboards, upright
                                   pianos, piano tuning and piano tuners.
  commons_instrument_care          Commons: luthiers and their workshops, violin making, instrument repair, piano
                                   restoration, tuners and tuning forks, metronomes, instrument cases and music
                                   stands.
  open_images_instrument_care      Open Images V7: acoustic, electric and bass guitars, ukuleles, mandolins, double
                                   basses, bassoons, recorders, euphoniums, sousaphones, cornets and flugelhorns,
                                   marimbas, vibraphones and glockenspiels, drumheads, hi-hats, bass and tom-tom drums,
                                   capos, music stands, pipe organs and synthesizers.

What was looked at and left out (YouTube, makers' care guides, forums and others) is in the kit's
instrument_care_sources.py.

    python packs/instrument_care_packs.py commons_piano_parts --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

ASK_PART = "What instrument part is this?"
ASK_WHAT = "What is this?"
ASK_DOING = "What is happening in this picture?"

ELECTRIC_NOTE = ("Safety: unplug an electric instrument from the amplifier and the wall before working on it; "
                 "amplifiers hold dangerous voltages inside even when unplugged, so leave their repair to a "
                 "technician.")
CARE_NOTE = ("Wooden instruments crack and warp with dry air and heat: keep them away from heaters and sunny windows, "
             "at a steady humidity.")


def part(category, words, note="", deeper=True, question=ASK_PART, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, "This is <words>." and the
    note)]) and an optional pattern of words a file's title or description must have."""
    spec = (category, deeper, [(question, f"This is {words}." + (f" {note}" if note else ""))])
    return spec + ((pattern,) if pattern is not None else ())


# Broad categories (bridges, nuts, keys, valves, pads, mutes) hold other things too: only files whose own words name
# an instrument.
MUSIC_WORDS = re.compile(r"\b(guitars?|violins?|violas?|cellos?|basses|bass|ukuleles?|banjos?|mandolins?|lutes?|"
                         r"harps?|pianos?|clarinets?|saxophones?|oboes?|bassoons?|flutes?|trumpets?|trombones?|horns?|"
                         r"tubas?|cornets?|drums?|instruments?|musical|music)\b", re.I)

STRING_PARTS = [
    part("Guitar strings", "a set of guitar strings; strings are changed one at a time so the neck keeps its tension"),
    part("Frets", "the frets: thin metal bars across a fingerboard that mark the notes", pattern=MUSIC_WORDS),
    part("Fingerboards", "a fingerboard, the strip on the neck where the strings are pressed", CARE_NOTE,
         pattern=MUSIC_WORDS),
    part("Machine heads", "machine heads (tuning machines), the geared tuners that tighten or loosen the strings"),
    part("Tuning pegs", "tuning pegs, turned to tune the strings", pattern=MUSIC_WORDS),
    part("Guitar bridges", "a guitar bridge, which holds the strings on the body and passes their vibration to it"),
    part("Guitar pickups", "a guitar pickup, which turns the strings' vibration into an electrical signal",
         ELECTRIC_NOTE),
    part("Guitar necks", "a guitar neck; the truss rod inside it keeps it straight, and is turned only a little at a "
                         "time"),
    part("Guitar headstocks", "a guitar headstock, the end of the neck that holds the tuners"),
    part("Violin bows", "a violin bow; loosen the hair after playing and never touch the hair with your fingers"),
    part("Bows (music)", "a bow for a violin-family instrument, strung with horsehair; loosen the hair after playing"),
    part("Rosin", "rosin, rubbed on bow hair so it grips the strings"),
    part("Chinrests", "a chinrest, which a violinist rests the jaw on"),
    part("Violin bridges", "a violin bridge, the thin wooden piece that holds the strings up; it should stand "
                           "straight, at a right angle to the top"),
    part("F-holes", "the f-holes, the f-shaped sound holes in the top of a violin-family instrument", CARE_NOTE),
    part("Sound posts", "a sound post, the small wooden dowel standing inside a violin under the bridge; only a "
                        "luthier should reset it"),
    part("Scrolls (music)", "the scroll, the carved curl at the top of a violin-family instrument's neck"),
    part("Pegboxes", "a pegbox, where the tuning pegs of a violin-family instrument sit"),
    part("Tailpieces", "a tailpiece, which anchors the strings at the bottom of the instrument", pattern=MUSIC_WORDS),
    part("Capos", "a capo, clamped across the strings to raise their pitch", question=ASK_WHAT),
    part("Guitar picks", "a guitar pick (plectrum)", question=ASK_WHAT),
]

WIND_PERCUSSION_PARTS = [
    part("Reeds (music)", "a reed, the thin cane strip that vibrates to make the sound of a clarinet, saxophone or "
                          "similar instrument; store reeds flat in a reed case"),
    part("Double reeds", "a double reed of an oboe or bassoon: two blades of cane tied together"),
    part("Saxophone mouthpieces", "a saxophone mouthpiece, which the reed is fastened to with a ligature"),
    part("Trumpet mouthpieces", "a trumpet mouthpiece; wash it often with warm water and a mouthpiece brush"),
    part("Brass instrument valves", "a brass instrument's valve"),
    part("Piston valves", "a piston valve of a brass instrument; it needs valve oil to move freely",
         pattern=MUSIC_WORDS),
    part("Rotary valves", "a rotary valve of a brass instrument such as a French horn", pattern=MUSIC_WORDS),
    part("Trumpet mutes", "a trumpet mute, put in the bell to soften or change the sound"),
    part("Drum heads", "a drumhead, the skin stretched over a drum; it is tuned by tightening the tension rods evenly, "
                      "a little at a time in a star pattern"),
    part("Drumsticks", "a pair of drumsticks", question=ASK_WHAT),
    part("Cymbals", "a cymbal; clean it only with a cleaner made for cymbals"),
    part("Hi-hats", "a hi-hat: two cymbals on a stand, played with a foot pedal and sticks"),
]

PIANO_PARTS = [
    part("Piano strings", "piano strings, stretched over the iron frame"),
    part("Piano pedals", "piano pedals: the right one (sustain) lets notes ring on"),
    part("Piano tuning", "a piano being tuned: a technician turns the tuning pins with a tuning lever",
         question=ASK_DOING),
    part("Piano tuners", "a piano tuner (piano technician) at work", question=ASK_DOING),
]

CARE = [
    part("Luthiers", "a luthier, a maker and repairer of stringed instruments, at work", deeper=False,
         question=ASK_DOING),
    part("Electronic tuners", "an electronic tuner, which shows whether a note is sharp, flat or in tune; many speak "
                              "or show the note's name", question=ASK_WHAT),
    part("Tuning forks", "a tuning fork, which rings at one exact pitch, often A at 440 Hz", question=ASK_WHAT),
    part("Metronomes", "a metronome, which ticks a steady beat at a chosen speed", question=ASK_WHAT),
    part("Musical instrument cases", "a musical instrument case", question=ASK_WHAT),
    part("Guitar cases", "a guitar case; a hard case protects best, and a humidifier pack can go inside in dry "
                         "weather", question=ASK_WHAT),
    part("Violin cases", "a violin case; loosen the bow before putting it in", question=ASK_WHAT),
    part("Music stands", "a music stand", question=ASK_WHAT),
]


def build_commons_string_instrument_parts(limit):
    """The commons_string_instrument_parts pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(STRING_PARTS, limit, "stringparts")


def build_commons_wind_percussion_parts(limit):
    """The commons_wind_percussion_parts pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(WIND_PERCUSSION_PARTS, limit, "windparts")


def build_commons_piano_parts(limit):
    """The commons_piano_parts pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PIANO_PARTS, limit, "pianoparts")


def build_commons_instrument_care(limit):
    """The commons_instrument_care pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CARE, limit, "instrcare")


INSTRUMENT_OI = [
    group("What musical instruments are in this picture?",
          {"Acoustic guitar": "an acoustic guitar", "Electric guitar": "an electric guitar",
           "Bass guitar": "a bass guitar", "Ukulele": "a ukulele", "Mandolin": "a mandolin",
           "Double bass": "a double bass", "Bassoon": "a bassoon", "Recorder": "a recorder",
           "Euphonium": "a euphonium", "Sousaphone": "a sousaphone", "Cornet": "a cornet",
           "Flugelhorn": "a flugelhorn", "Marimba": "a marimba", "Vibraphone": "a vibraphone",
           "Glockenspiel": "a glockenspiel", "Pipe organ": "a pipe organ", "Synthesizer": "a synthesizer"}),
    group("What drum parts are in this picture?",
          {"Drumhead": "a drumhead", "Hi-hat": "a hi-hat", "Bass drum": "a bass drum", "Tom-tom drum": "a tom-tom"}),
    group("What music accessories are in this picture?", {"Capo": "a capo", "Music stand": "a music stand"}),
]


def build_open_images_instrument_care(limit):
    """The open_images_instrument_care pack (see the module docstring)."""
    return build_oi_gap("open_images_instrument_care", INSTRUMENT_OI, limit, 9331)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
INSTRUMENT_CARE_PACKS = {
    "commons_string_instrument_parts": (build_commons_string_instrument_parts, COMMONS_LICENCE.format(
        what="stringed instrument part and accessory")),
    "commons_wind_percussion_parts": (build_commons_wind_percussion_parts, COMMONS_LICENCE.format(
        what="wind and percussion instrument part")),
    "commons_piano_parts": (build_commons_piano_parts, COMMONS_LICENCE.format(what="piano part and piano tuning")),
    "commons_instrument_care": (build_commons_instrument_care, COMMONS_LICENCE.format(
        what="luthier, instrument repair, tuner, metronome and case")),
    "open_images_instrument_care": (build_open_images_instrument_care, OI_LICENCE),
}
INSTRUMENT_CARE_LIMITS = {
    "commons_string_instrument_parts": 1600,   # 22 categories
    "commons_wind_percussion_parts": 1100,     # 15 categories
    "commons_piano_parts": 700,                # 9 categories
    "commons_instrument_care": 800,            # 10 categories
    "open_images_instrument_care": 2500,       # 23 labels
}
INSTRUMENT_CARE_COMMONS_KEYS = ("commons_string_instrument_parts", "commons_wind_percussion_parts",
                                "commons_piano_parts", "commons_instrument_care")


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an instrument care pack builder.")
    parser.add_argument("key", choices=sorted(INSTRUMENT_CARE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = INSTRUMENT_CARE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
