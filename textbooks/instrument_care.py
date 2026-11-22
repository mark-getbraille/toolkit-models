"""Musical instrument care and repair for the reference library, in the group "Reference, musical instrument care"
(the owner's request of 2026-11-22). Keys: instrument-care (every book), instr:<name>.

What this module builds, in plain words: the old public-domain books on tuning, making and repairing instruments,
each whole from the Internet Archive's scan with its text layer, only when the Internet Archive's record shows it was
published before 1931 (checked at every build), each marked as an old book:
  - Modern Piano Tuning and Allied Arts (William Braid White, 1917): tuning, regulating and repairing pianos;
  - Violin-Making, As It Was and Is (Edward Heron-Allen, 1885): the parts of the violin, how it is made, and its
    care (bridges, sound posts, strings and bows);
  - Georg Gemünder's Progress in Violin Making (1881).
(Wikibooks' guitar, piano and instrument books are in the toolkit's Kiwix library already, and the makers' care guides
are linked from the manual library's instrument_care category.)

Every book starts with the safety note: unplug electric instruments and amplifiers before working on them (amplifiers
hold dangerous voltages inside even when unplugged), loosen strings slowly, and wear eye protection when cutting
strings or using tools.

Run from the repository's folder:
  python3 textbooks/instrument_care.py instr:white_piano_tuning_1917 --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import car_care as C  # noqa: E402 - old_book, the old public-domain book entry

GROUP = "instruments"
GROUPS = {GROUP: "Reference, musical instrument care"}
SAFETY = ("Safety: unplug electric instruments and amplifiers before working on them (amplifiers hold dangerous "
          "voltages inside even when unplugged, so leave their repair to a technician); loosen strings slowly; "
          "wear eye protection when cutting strings or using tools.")

PDFS = [
    C.old_book(GROUP, "white_piano_tuning_1917", "Modern Piano Tuning and Allied Arts (William Braid White, 1917)",
               "Piano tuning and repair (old book)", "modernpianotunin00whit", 1917,
               "The piano tuner's handbook: how the piano works, the principles and practice of tuning (temperament, "
               "setting the bearings, unisons and octaves), regulating the action, and repairs.", SAFETY),
    C.old_book(GROUP, "heron_allen_violin_making_1885", "Violin-Making, As It Was and Is (Edward Heron-Allen, 1885)",
               "Violin making and care (old book)", "cu31924022320216", 1885,
               "The classic treatise on the violin: its history, every part named and described, how a violin is "
               "made by hand, and its care and repair (the bridge, sound post, strings and bow).", SAFETY),
    C.old_book(GROUP, "gemunder_violin_making_1881", "Georg Gemünder's Progress in Violin Making (1881)",
               "Violin making (old book)", "georggemunderspr00gemuiala", 1881,
               "A violin maker's account of the art and science of violin making, with facts about old and new "
               "instruments and their care.", SAFETY),
]

COLLECTION = K.Collection("instr", GROUP, pdfs=PDFS,
                          words={"instrument-care": lambda: [f"instr:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "instr_old_books": "archive.org (its robots.txt allows the files): books published before 1931 are in the US "
                       "public domain; the builder checks each item's year on the Internet Archive's record at every "
                       "build.",
}
NOT_INCLUDED = [
    ("Wikibooks: Guitar, Piano and other instrument books (CC BY-SA)", "Already in the toolkit's Kiwix library "
     "(Wikibooks in full), which the toolkit reads. Index: https://en.wikibooks.org/wiki/Guitar"),
    ("Makers' care and setup guides (Yamaha, Steinway, Fender, Martin, Taylor, Gibson, D'Addario, Conn-Selmer, "
     "Remo, Evans)", "Copyright of each maker. Link-only, in the manual library's instrument_care category. Index: "
     "https://usa.yamaha.com/support/ and https://www.daddario.com/"),
    ("Smithsonian and museum instrument pages", "The museums' open pictures are in the picture kit (met_instruments, "
     "smithsonian); their web pages are not openly licensed text. Index: https://www.si.edu/openaccess"),
    ("How to Repair Violins and Other Musical Instruments (Alfred F. Common, 1904)", "The Internet Archive's copy is "
     "lending-library only (checked 2026-11-22). Index: https://archive.org/details/howtorepairvioli0000alfr"),
    ("YouTube lessons and repair videos, Instructables, Reddit and instrument forums", "Not read (the owner's "
     "rule: their terms forbid scraping, or the text and pictures are their users' own). Index: "
     "https://www.youtube.com/results?search_query=instrument+repair"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
