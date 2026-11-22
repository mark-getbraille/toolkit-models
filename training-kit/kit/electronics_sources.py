"""ELECTRONICS REPAIR AND ASSISTIVE TECHNOLOGY for the Picture Model Training Kit (the owner's request of 2026-11-22).
This file lists:
  - the ready-made packs built in packs/electronics_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): electronic parts, cables and connectors, soldering and repair, assistive and low-vision devices,
    circuit diagrams, and Open Images electronics;
  - the share-alike Commons files of the main categories (group "share-alike": only with the share-alike choice,
    --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sign-up and not-included sources looked at, with the reason (ELECTRONICS_SIGN_UP, ELECTRONICS_NOT_INCLUDED).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, only when the user ticks the matching choice. Every licence was checked at its source in
November 2026. Answers say only what the Commons category, the file's own words or the Open Images labels say; a
part's value or a battery's size only where the file's own words state exactly one. Safety notes (mains, lithium,
soldering, the care of assistive devices) are the same words as the packs'.

Picture-making (ELECTRONICS_PICTURE_MAKING_OK): only the parts, cables and diagrams (things, no people) may be used;
sources.py puts every other key in NOT_FOR_PICTURE_MAKING.

    python -c "import sources, electronics_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

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

MAINS_NOTE = ("Safety first: mains electricity can kill. Unplug a device before opening it; televisions, picture "
              "tubes, valve equipment, microwave ovens and power supplies can hold a dangerous charge for a long "
              "time after unplugging, so their insides are work for a trained technician.")
LITHIUM_NOTE = ("Lithium batteries can catch fire or explode if they are damaged, punctured, swollen, overheated or "
                "short-circuited: never charge or use a swollen or damaged one, and take old ones to a battery "
                "recycling drop-off, never the household bin.")
SOLDER_NOTE = ("A soldering iron's tip is hot enough to burn at a touch: keep it in its stand, work with fresh air or "
               "a fume extractor (flux smoke irritates the lungs), wear eye protection, and wash your hands after "
               "handling solder, which may contain lead.")


def thing(category, words, note="", deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "It shows <words>." and the note."""
    return (category, "What is this?", f"It shows {words}." + (f" {note}" if note else ""), deeper)


# The main categories of packs/electronics_packs.py, files under CC BY-SA or GFDL.
ELECTRONICS_SA = [
    thing("Potentiometers", "a potentiometer, a variable resistor turned by a knob or slider"),
    thing("Film capacitors", "a film capacitor"),
    thing("Diodes", "a diode, a part that lets current flow one way only", deeper=False),
    thing("Bipolar junction transistors", "a bipolar junction transistor"),
    thing("Voltage regulators", "a voltage regulator"),
    thing("Close-ups of integrated circuits", "an integrated circuit (a chip), seen close up", deeper=False),
    thing("Relays", "a relay, a switch worked by an electromagnet", deeper=False),
    thing("Lithium-ion batteries", "a lithium-ion battery", LITHIUM_NOTE),
    thing("Vacuum tubes", "a vacuum tube (a valve)", MAINS_NOTE),
    thing("Soldering joints", "soldered joints", SOLDER_NOTE),
    thing("Digital multimeters", "a digital multimeter, which measures voltage, current and resistance"),
    thing("Disassembled smartphones", "a smartphone taken apart", LITHIUM_NOTE),
    thing("DVI connectors", "a DVI connector, a wide video plug for computer screens"),
    thing("XLR connectors", "an XLR connector, a round plug with three pins used for microphones"),
]


def prepare_electronics_commons_sa(source, data_dir, work, cap):
    """Commons electronic parts, soldering, test equipment and connector categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(ELECTRONICS_SA, cap, source.test, "electronics-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


ELECTRONICS_SOURCES = [
    Source("commons_electronic_parts", "Electronic parts by name: resistors and the colour code, capacitors, diodes, "
                                       "transistors, chips, relays, fuses, lithium batteries, switches and valves, a "
                                       "value only where the file states it, with safety notes (Wikimedia Commons, "
                                       "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 2500, 25, prepare_pack, "about 450 MB"),
    Source("commons_cables_connectors", "Cables and connectors by name: HDMI cables, DisplayPort, VGA, DVI, audio, "
                                        "XLR, RCA, coaxial and network plugs, power adapters (Wikimedia Commons, "
                                        "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 110 MB"),
    Source("commons_electronics_repair", "Soldering and desoldering, multimeters, oscilloscopes and test equipment, "
                                         "workbenches, phones and laptops opened up, radio repair, with safety notes "
                                         "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("commons_assistive_devices", "Assistive and low-vision devices: braille embossers and printers, talking "
                                        "clocks, monoculars, the optophone reading machine, phone covers and screen "
                                        "protectors, with care and repair notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 250, 5, prepare_pack, "about 50 MB"),
    Source("commons_circuit_diagrams", "Circuit diagrams (schematics), chip pinouts and electronic symbols, said only "
                                       "as what kind of drawing it is and its own description (Wikimedia Commons, "
                                       "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 90 MB"),
    Source("open_images_electronics", "Electronics, computers, televisions, chips, diodes and LEDs, fuses, solder, "
                                      "wiring and network cables (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("electronics_commons_sa", "Wikimedia Commons: electronic parts, lithium batteries, valves, soldering, "
                                     "multimeters, phones taken apart and connectors, files under CC BY-SA or GFDL "
                                     "(share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_electronics_commons_sa, "about 160 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]
# The ready-made packs of this file (the self-test compares them with packs/electronics_packs.py).
ELECTRONICS_PACK_KEYS = ("commons_electronic_parts", "commons_cables_connectors", "commons_electronics_repair",
                         "commons_assistive_devices", "commons_circuit_diagrams", "open_images_electronics")
# Things only, no people: the parts, cables and diagrams may be used for picture-making.
ELECTRONICS_PICTURE_MAKING_OK = {"commons_electronic_parts", "commons_cables_connectors", "commons_circuit_diagrams"}

ELECTRONICS_SIGN_UP = {
    "Roboflow Universe electronic component and PCB sets (several CC BY 4.0)":
        "https://universe.roboflow.com : a free account and API key are needed to export, and Roboflow's robots.txt "
        "disallows the dataset download pages (see gaps_sources.py); check each set's licence and where its photos "
        "came from.",
    "Kaggle electronic component, resistor and PCB defect sets":
        "https://www.kaggle.com : a free account and API token are needed; most sets give no licence or say "
        "research use only. The owner can use the own-pictures folder.",
    "FICS-PCB (University of Florida) and PCB-DSLR":
        "printed circuit board photo sets for research (request forms and research-only terms); recorded only.",
}

ELECTRONICS_NOT_INCLUDED = {
    "iFixit guides and their photos (CC BY-NC-SA)":
        "iFixit's robots.txt says \"Content-Signal: search=yes, ai-input=yes, ai-train=no\" and its Terms of Use keep "
        "API answers 24 hours and out of datasets (read 2026-11-21); MyFixit's step photos are iFixit's. Not even a "
        "personal-use entry; the manual library links iFixit's pages for the owner to open.",
    "Instructables, Hackaday, YouTube and Pinterest":
        "their terms do not allow programs to copy their pictures (scraping is forbidden); not read.",
    "Makers' product photos (HumanWare, Vispero, Optelec, Eschenbach, Zeiss, Enhanced Vision, Orbit Research, APH)":
        "the makers' copyright, with no open licence; the commons_assistive_devices pack has the Commons photos.",
    "NASA, NIST and DOE electronics photos":
        "public domain, but the agencies' galleries have no listing by electronic part; those copied to Commons are "
        "in the Commons categories the packs read, each file's licence checked.",
    "Open Images electronics labels already asked elsewhere (Printed circuit board, Resistor, Capacitor, Transistor, "
    "Motherboard, Laptop, Mobile phone, Cable, Television, Hard disk drive, Usb flash drive, Battery)":
        "asked by things_packs, home_packs and everyday_packs; never asked twice. Labels with no checked photos "
        "(Soldering iron, Cable tester, Sound card, HDMI and others) are left out.",
    "Commons categories that do not exist under the names tried (November 2026)":
        "Resistor color code, Through-hole and SMD resistors, Rectifier diodes, Glass and cartridge fuses, "
        "Swollen batteries, Dual in-line packages, Thermal paste, Desoldering pumps and braid, Bench power "
        "supplies, Mobile phone repair, Television repair, Battery fires; the packs use the categories that exist "
        "(Electronic color code, Insert fuses, Desoldering, Defective electronic components ...).",
    "Commons pictures of video magnifiers, electronic magnifiers, braille notetakers, DAISY and talking-book players, "
    "talking watches and calculators, reading machines and electronic travel aids":
        "no Commons category exists for any of them (checked 2026-11-22), and Commons search is not used for them in "
        "this first version; the makers' product photos are their copyright. Braille embossers, talking clocks, "
        "monoculars and the optophone are in commons_assistive_devices; refreshable braille displays in "
        "disability_packs. The owner's own photos can be added with the own-pictures folder.",
}
