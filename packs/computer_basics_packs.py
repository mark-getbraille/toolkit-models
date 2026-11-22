"""Picture packs for COMPUTER AND PHONE BASICS FOR BEGINNERS (the owner's request of 2026-11-22). Used by
build_packs.py in the same way as its own PACKS (build_<key>(limit) returns [(file name, JPEG bytes or None, row)]).

Why: a blind beginner, or a blind person helping a sighted beginner, often needs to know which part of a computer or
phone a photo shows: the power button, the touchpad, the arrow and function keys, a memory card or SIM card and its
tray, an ink or toner cartridge, the cables and plugs at the back of a router. The answers name the part and what it
is for, in plain words.

Answers say only what the source says (a Commons category's name, an Open Images label people confirmed); no brand
or model is named unless the category names it. Answers about storage and connections end with TECH_NOTE (restart
first, keep the system updated, back up, download only from the maker's own store or site), the same words as the
kit's practical_sources.py.

The packs (COMPUTER_BASICS_PACKS):
  commons_computer_basics  Wikimedia Commons (CC0, public domain or CC BY files only): power buttons, touchpads,
                           arrow keys, function keys, laptop keyboards, numeric keypads, keyboard shortcuts,
                           docking stations, video calls, computer cases, memory cards (SD and microSD), SIM
                           cards, ink and toner cartridges.
  open_images_computer_basics  Open Images V7 (labels CC BY 4.0; photos CC BY, CC0 or the Public Domain Mark):
                           old storage (floppy disk and drive), an Ethernet hub, and desk and tablet things
                           (mousepad, graphics tablet, tablet charger and stand, printer consumables). No
                           label is asked twice (packs/test_practical.py checks).

Not repeated here: things_packs (USB flash drives, laptops, desktop computers, tablets, webcams, modems as Commons
categories), the electronics packs (cables and connectors, electronic parts and repair), device_packs and the
Open Images keyboards, mice, laptops, phones, hard disks, USB drives and cables, routers and
modems that other packs ask, and commons_screens (phone screens). Screenshots of
programs are left out (the programs' makers own them).

    python packs/computer_basics_packs.py commons_computer_basics --limit 8
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap
from outdoor_cooking_packs import thing, with_yes_notes

TECH_NOTE = ("Computer help: when something stops working, restart it first; keep the system and apps updated; back "
             "up your files; and download programs and apps only from the maker's own site or the official app "
             "store.")

COMPUTER_BASICS = [
    thing("Power buttons", "a power button, usually marked with a circle broken by a short line at the top; press "
                           "it to turn the device on, and on most computers hold it for several seconds only to force "
                           "it off when it stops responding", TECH_NOTE),
    thing("Touchpads", "a touchpad, which moves the pointer on a laptop; tap or press it to click"),
    thing("Arrow keys", "the arrow keys, which move the cursor or the focus up, down, left and right"),
    thing("Function keys", "the function keys (F1 to F12) along the top of a keyboard; F1 often opens help"),
    thing("Laptop keyboards", "a laptop keyboard"),
    thing("Numeric keypads", "a numeric keypad, the number keys laid out like a calculator", "", True),
    thing("Keyboard shortcuts", "a keyboard shortcut (keys pressed together to give a command, such as Control and C "
                                "to copy)"),
    thing("Docking stations", "a docking station, which connects a laptop to a screen, keyboard, network and power "
                              "with one plug", "", True),
    thing("Videoconferencing", "a video call or video conference, people talking to each other over cameras and "
                               "screens", "", True),
    thing("Computer cases", "a computer case (the tower or box that holds a desktop computer's parts)"),
    thing("Memory cards", "a memory card (such as an SD or microSD card) that stores photos and files", TECH_NOTE,
          True),
    thing("SIM cards", "a SIM card, the small chip card that connects a phone to its mobile network; it sits in a "
                       "tray opened with a small pin"),
    thing("Ink cartridges", "a printer ink cartridge", "", True),
    thing("Toner cartridges", "a laser printer toner cartridge"),
]


def build_commons_computer_basics(limit):
    """The commons_computer_basics pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(COMPUTER_BASICS, limit, "pcbasics")


COMPUTER_OI = [
    group("What computer storage is in this picture?",
          {"Floppy disk": "a floppy disk", "Floppy drive": "a floppy drive"}, TECH_NOTE),
    group("What cables or network things are in this picture?",
          {"Ethernet hub": "an Ethernet hub"}, TECH_NOTE),
    group("What computer or phone accessories are in this picture?",
          {"Mousepad": "a mousepad", "Graphics tablet": "a graphics tablet", "Tablet computer charger": "a tablet "
           "charger", "Tablet computer stand": "a tablet stand",
           "Printer consumable": "printer supplies"}),
]


def build_open_images_computer_basics(limit):
    """open_images_computer_basics (see the module docstring)."""
    return with_yes_notes(build_oi_gap("open_images_computer_basics", COMPUTER_OI, limit, 9402), COMPUTER_OI)


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
COMPUTER_BASICS_PACKS = {
    "commons_computer_basics": (build_commons_computer_basics, COMMONS_LICENCE.format(
        what="power button, touchpad, keyboard key, computer case, memory card, SIM card and printer cartridge")),
    "open_images_computer_basics": (build_open_images_computer_basics, OI_LICENCE),
}
COMPUTER_BASICS_LIMITS = {
    "commons_computer_basics": 900,       # 16 categories
    "open_images_computer_basics": 500,   # 7 labels
}
COMPUTER_BASICS_COMMONS_KEYS = ("commons_computer_basics",)
COMPUTER_BASICS_SPECS = COMPUTER_BASICS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    from practical_packs import try_pack
    return try_pack(COMPUTER_BASICS_PACKS, "Try a computer basics pack builder.", argv)


if __name__ == "__main__":
    sys.exit(main())
