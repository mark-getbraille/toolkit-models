"""Picture packs for ELECTRONICS REPAIR: electronic parts by name (resistors and the colour code, capacitors, diodes,
transistors, chips, relays, fuses, batteries, switches, valves), the cables and connectors the home packs do not ask
about (HDMI cables, DisplayPort, VGA, DVI, audio and network plugs, power adapters), soldering and desoldering, test
equipment (multimeters, oscilloscopes, signal generators), phones, laptops and radios opened up for repair, circuit
diagrams and their symbols, and Open Images photos of electronics no other pack asks about. Used by build_packs.py in
the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)];
a picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same
picture (food_packs.with_twins). The limit counts pictures.

The owner's request of 2026-11-22 (electronics repair, light construction around the home, and arts and crafts other
than textiles; the other two are packs/building_packs.py and packs/crafts_packs.py, which use build_commons_facts
from this file).

WHAT THE ANSWERS SAY. Every answer is a fixed sentence written here from the Commons category a file sits in (a file
in "Zener diodes" is a Zener diode), with one short plain line on what the part is for; nothing is written by an AI
model and nothing is guessed from the picture. A VALUE (a resistor's ohms, a capacitor's farads, a fuse's amps) or a
battery SIZE is said only where the file's own title or description states exactly one ("The file's own words give
its value: 4.7 kilohms."), never read from colour bands or markings in the picture (stated_value). Safety notes,
in the style of the drinks distilling warning:
  MAINS_NOTE     after answers about things that run on mains power or hold high voltage inside (televisions and
                 their picture tubes, valve radios and amplifiers, power supplies, capacitors that store charge);
  LITHIUM_NOTE   after answers about lithium batteries (fire if damaged, swollen, punctured or short-circuited;
                 recycling, never the bin);
  SOLDER_NOTE    after answers about soldering and desoldering (burns, flux fumes, lead);
  FUSE_NOTE      after a blown fuse (find the cause; replace only with the same rating);
  EWASTE_NOTE    after old or broken electronics (take them to an e-waste drop-off);
  DEVICE_NOTE    after assistive devices (the maker's battery and charger, cleaning, the warranty, loan agreement or
                 repair programme before opening one).

The packs (ELECTRONICS_PACKS; all open: Commons files CC0, public domain or CC BY, checked file by file; Open Images
labels CC BY 4.0 and photos CC BY, CC0 or the Public Domain Mark):
  commons_electronic_parts      resistors (power, variable, light- and heat-sensitive, the colour code chart),
                                capacitors (film, tantalum, supercapacitors, variable), diodes, Zener diodes, bridge
                                rectifiers, transistors, voltage regulators, opto-isolators, chips close up and their
                                packages and sockets, surface-mount parts, inductors, transformers, relays, crystals,
                                fuses (blade, cartridge, thermal, holders, blown ones), lithium-ion and laptop
                                batteries and battery packs, switches, pin headers, heat sinks, buzzers, valves and
                                picture tubes, damaged parts. "What is this?" -> "This is a Zener diode, a diode made
                                to hold a steady voltage." and, where the file states one, "What value does it have?"
  commons_cables_connectors     cables and connectors home_packs commons_connectors does not ask about: HDMI cables,
                                DisplayPort, VGA, DVI, TRS, XLR, RCA, coaxial and F connectors, Ethernet cables and
                                RJ45 plugs, Molex and DC power connectors, power adapters. "What kind of connector is
                                this?"
  commons_electronics_repair    soldering tools and stations, soldering joints, solder wire, desoldering, third
                                hands, wave soldering; digital and analogue multimeters, logic analysers, function and
                                signal generators, spectrum analysers, LCR meters, test equipment; electronics
                                workbenches, antistatic bags, spudgers; phones, smartphones and laptops opened up;
                                radio repair, valve radios, audio amplifiers; assistive technology devices.
  commons_assistive_devices     assistive and low-vision devices (the owner's request of 2026-11-22): braille
                                embossers and printers, talking clocks, monoculars, the optophone (an early reading
                                machine), phone covers and screen protectors, computer speakers, with DEVICE_NOTE
                                (battery, cleaning, warranty and the repair programmes). Commons has no category for
                                video magnifiers, notetakers, DAISY players or travel aids (checked 2026-11-22: the
                                kit's electronics_sources.py lists them); refreshable braille displays, hearing aids,
                                white canes and binoculars are disability_packs' and other packs' (not repeated).
  commons_circuit_diagrams      circuit diagrams (schematics), amplifier circuits, resistor and fuse diagrams, chip
                                pinout diagrams and electronic symbols (drawings, which Commons sends as pictures):
                                "What is this?" -> "This is a circuit diagram (a schematic): ..." Only what kind of
                                drawing it is, and the file's own description; never a reading of the circuit.
  open_images_electronics       Open Images labels no other pack asks about: electronics, computers, television sets,
                                electric motors, memory cards, power adapters, chips and semiconductors, diodes and
                                LEDs, fuses, solder, electrical wiring and network cables.

Not repeated here: things_packs commons_things (printed circuit boards, integrated circuits, electrolytic and ceramic
capacitors, resistors, transistors, LEDs, breadboards, radios, multimeters, people soldering), home_packs
commons_connectors (USB, USB-C, micro-USB, Lightning, HDMI connectors, audio jacks, AA to D, 9-volt and button cell
batteries, chargers), home_packs commons_tools (soldering irons), hardware_packs (clamp meters, electrical boxes,
wire and cable), mechanical/device packs (computer repair, electronic waste, Raspberry Pi), and the Open Images labels
those packs ask (Printed circuit board, Resistor, Capacitor, Transistor, Motherboard, Laptop, Mobile phone, Cable ...).
What was looked at and left out (iFixit, Hugging Face and Kaggle component sets, Roboflow) is in the kit's
electronics_sources.py.

    python packs/electronics_packs.py commons_electronic_parts --limit 8      (prints a few rows: a quick check)
"""

import math
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, ALT_TEXT, pass_random
from gaps_oi_packs import group, build_oi_gap, QUICK

WHAT_Q = "What is this?"
CONNECTOR_Q = "What kind of connector is this?"
VALUE_Q = "What value does it have?"
BATTERY_Q = "What size of battery is this?"
DRAWING_Q = "What kind of drawing is this?"

MAINS_NOTE = ("Safety first: mains electricity can kill. Unplug a device before opening it; televisions, picture "
              "tubes, valve equipment, microwave ovens and power supplies can hold a dangerous charge for a long "
              "time after unplugging, so their insides are work for a trained technician.")
LITHIUM_NOTE = ("Lithium batteries can catch fire or explode if they are damaged, punctured, swollen, overheated or "
                "short-circuited: never charge or use a swollen or damaged one, and take old ones to a battery "
                "recycling drop-off, never the household bin.")
SOLDER_NOTE = ("A soldering iron's tip is hot enough to burn at a touch: keep it in its stand, work with fresh air or "
               "a fume extractor (flux smoke irritates the lungs), wear eye protection, and wash your hands after "
               "handling solder, which may contain lead.")
FUSE_NOTE = ("A blown fuse means too much current flowed: find out why before replacing it, and use only a fuse of "
             "the same type and rating.")
EWASTE_NOTE = "Old or broken electronics belong at an e-waste recycling drop-off, not in the household bin."


def part(category, words, note="", deeper=True):
    """A Commons spec for a part or thing: "What is this?" -> "This is <words>." and the note after."""
    return (category, deeper, [(WHAT_Q, f"This is {words}." + (f" {note}" if note else ""))])


def connector(category, words, deeper=True):
    """A Commons spec for a connector or cable: "What kind of connector is this?" -> "This is <words>."."""
    return (category, deeper, [(CONNECTOR_Q, f"This is {words}.")])


def drawing(category, words, deeper=True):
    """A Commons spec for a drawing: "What kind of drawing is this?" -> "This is <words>."."""
    return (category, deeper, [(DRAWING_Q, f"This is {words}.")])


# ----------------------------------------------------------------- values and sizes the file's own words state

# A value with its unit, as written in a title or description: "220 ohm", "4.7kΩ", "10 µF", "100nF", "5A fuse".
_NUMBER = r"(\d+(?:[.,]\d+)?)"
VALUE_PATTERNS = [
    (re.compile(_NUMBER + r"\s?(k|K|M)?\s?(?:Ω|ohms?\b|Ohms?\b)"), "resistance"),
    (re.compile(r"\b(\d+)(k|K|M|R)(\d+)\b"), "resistance code"),          # 4k7 = 4.7 kilohms, 2R2 = 2.2 ohms
    (re.compile(_NUMBER + r"\s?(µ|μ|u|n|p)F\b"), "capacitance"),
    (re.compile(_NUMBER + r"\s?(m)?A\b"), "fuse rating"),            # only in words that name a fuse
]
UNIT_WORDS = {"": "ohms", "k": "kilohms", "K": "kilohms", "M": "megohms", "R": "ohms",
              "µ": "microfarads", "μ": "microfarads", "u": "microfarads", "n": "nanofarads", "p": "picofarads"}
# Battery sizes a title can name without doubt (not "C" or "D", which are ordinary letters).
BATTERY_SIZES = re.compile(r"\b(AAA|AA|9V|PP3|CR\d{4}|LR\d{2}|SR\d{2,3}|18650|21700|14500|26650)\b")


def stated_value(text):
    """The one value the words state, in plain words ("4.7 kilohms", "100 nanofarads", "5 amps"), or "" when they
    state none or more than one (two different values: neither is said)."""
    found = set()
    for pattern, kind in VALUE_PATTERNS:
        if kind == "fuse rating" and not re.search(r"\bfuses?\b", text or "", re.I):
            continue
        for m in pattern.finditer(text or ""):
            if kind == "resistance":
                number, unit = m.group(1).replace(",", "."), m.group(2) or ""
                found.add(f"{number} {UNIT_WORDS[unit]}")
            elif kind == "resistance code":
                number = f"{m.group(1)}.{m.group(3)}"
                found.add(f"{number} {UNIT_WORDS[m.group(2)]}")
            elif kind == "capacitance":
                found.add(f"{m.group(1).replace(',', '.')} {UNIT_WORDS[m.group(2)]}")
            else:
                found.add(f"{m.group(1).replace(',', '.')} {'milliamps' if m.group(2) else 'amps'}")
    return found.pop() if len(found) == 1 else ""


def stated_battery(text):
    """The one battery size the words name ("AA", "CR2032", "18650"), or "" (none, or two different ones)."""
    sizes = {m.group(1).upper() for m in BATTERY_SIZES.finditer(text or "")}
    sizes = {"9V" if s == "PP3" else s for s in sizes}
    return sizes.pop() if len(sizes) == 1 else ""


def part_facts(title, text):
    """Extra rows for a part from its file's own words: its value or battery size, when exactly one is stated."""
    words = f"{title.split(':', 1)[-1].rsplit('.', 1)[0]} {text or ''}"
    rows = []
    value = stated_value(words)
    if value:
        rows.append((VALUE_Q, f"The file's own words give its value: {value}."))
    size = stated_battery(words)
    if size:
        rows.append((BATTERY_Q, f"The file's own words give its size: {size}." + (
            f" {LITHIUM_NOTE}" if re.match(r"CR|18650|21700|14500|26650", size) else "")))
    return rows


# ----------------------------------------------------------------- the shared Commons builder

def build_commons_facts(specs, limit, prefix, facts=None, adults_only=False, drawings=False):
    """home_packs.build_commons_topic with two additions used by the electronics, building and crafts packs: facts
    (a function (title, text) -> [(question, answer)] for extra rows from a file's own words, such as a stated value)
    and drawings (SVG drawings too, which Commons sends as pictures). specs: [(category, deeper, rows)] or [(category,
    deeper, rows, pattern)]; the categories take turns in a fixed shuffled order so each gets an even share; a file
    whose words name a nude is left out, and with adults_only one whose words name a child."""
    from food_packs import with_twins
    from home_packs import (category_files, home_entries, commons_fetch, file_name, NUDE, FIRST_PERSON,
                            NOT_RESPECTFUL, COMMONS_PLACES, LIFE_STAGE)
    from expression_packs import mark_child, CHILD
    from places import where
    s, items, seen = session(), [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    queues = [[spec[0], spec[1], spec[2], None, spec[3] if len(spec) > 3 else None] for spec in order]
    want = int(limit * 1.15) + 2
    rounds = 0
    while len(items) < want and queues and rounds < 50:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            category, deeper, rows, titles, must = q
            if titles is None:
                titles = [t for t in category_files(s, category, deeper) if t not in seen]
                pass_random(category).shuffle(titles)
                build_packs.say(f"Commons {category}: {len(titles)} files")
            batch, q[3] = titles[:max(3, share) * 2], titles[max(3, share) * 2:]
            if not batch:
                queues.remove(q)
                continue
            got = 0
            for title, url, credit, text in home_entries(s, batch, drawings=drawings):
                if got >= share or title in seen:
                    continue
                words = f"{title} {text}"
                if NUDE.search(words) or (must and not must.search(words)):
                    continue
                if adults_only and CHILD.search(words):
                    continue
                seen.add(title)
                place = where(COMMONS_PLACES.get(title, ""))
                words = LIFE_STAGE.sub(" ", words)
                pairs = list(rows) + (facts(title, text) if facts else [])
                out = [mark_child({"question": qn, "answer": an, "credit": credit, **place}, words)
                       for qn, an in pairs]
                if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
                    out.append(mark_child({"question": ALT_TEXT, "answer": text, "credit": credit, **place}, words))
                items.append((file_name(prefix, title), url, out))
                got += 1
            if not q[3]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    return with_twins(commons_fetch(items[:want])[:limit])


# ----------------------------------------------------------------- Commons: electronic parts

COLOUR_CODE = ("the electronic colour code, the coloured bands that give a resistor's value: black 0, brown 1, red 2, "
               "orange 3, yellow 4, green 5, blue 6, violet 7, grey 8, white 9; the first bands are digits, the next "
               "says how many zeros follow, and a gold or silver band gives the tolerance")
PARTS = [
    part("Electronic color code", COLOUR_CODE, deeper=False),
    part("Power resistors", "a power resistor, a large resistor made to get rid of heat"),
    part("Potentiometers", "a potentiometer, a variable resistor turned by a knob or slider (volume controls are "
                           "often potentiometers)"),
    part("Photoresistors", "a photoresistor (light-dependent resistor), whose resistance falls in light"),
    part("Thermistors", "a thermistor, a resistor whose resistance changes with temperature, used to sense heat"),
    part("Varistors", "a varistor, a part that protects a circuit from voltage spikes"),
    part("Film capacitors", "a film capacitor"),
    part("Tantalum capacitors", "a tantalum capacitor, a small capacitor that must be fitted the right way round"),
    part("Supercapacitors", "a supercapacitor, which stores far more charge than an ordinary capacitor",
         MAINS_NOTE.split(": ", 1)[0] + ": a charged capacitor can give a shock or spark; discharge it before "
         "handling."),
    part("Variable capacitors", "a variable capacitor, turned to tune a circuit (old radios tune with one)"),
    part("Diodes", "a diode, a part that lets current flow one way only (a band marks its cathode end)", deeper=False),
    part("Zener diodes", "a Zener diode, a diode made to hold a steady voltage"),
    part("Bridge rectifiers", "a bridge rectifier, four diodes in one part that turn alternating current into direct "
                              "current"),
    part("Bipolar junction transistors", "a bipolar junction transistor, a part that switches or amplifies current"),
    part("Power transistors", "a power transistor, a transistor made to handle large currents, usually on a heat "
                              "sink"),
    part("Voltage regulators", "a voltage regulator, a part that keeps a supply voltage steady"),
    part("Opto-isolators", "an opto-isolator (optocoupler), which passes a signal by light between two circuits that "
                           "are not connected"),
    part("Close-ups of integrated circuits", "an integrated circuit (a chip), seen close up", deeper=False),
    part("Integrated circuits (SMD)", "a surface-mount integrated circuit, a chip soldered flat onto a board"),
    part("Integrated circuit sockets", "an integrated circuit socket, which holds a chip so it can be removed"),
    part("Surface-mounted devices", "surface-mount parts (SMD), tiny parts soldered flat onto a circuit board",
         deeper=False),
    part("Electronic component packages", "an electronic component package, the case a part comes in"),
    part("Inductors", "an inductor (a coil), which stores energy in a magnetic field"),
    part("Toroidal transformers", "a toroidal transformer, a ring-shaped transformer", MAINS_NOTE),
    part("Relays", "a relay, a switch worked by an electromagnet", deeper=False),
    part("Crystal oscillators", "a crystal oscillator, which keeps time for a circuit"),
    part("Blade type fuses", "a blade fuse, the plug-in fuse used in cars"),
    part("Insert fuses", "a cartridge fuse"),
    part("Thermal fuses", "a thermal fuse, which cuts the power for good when a device overheats"),
    part("Fuse holders", "a fuse holder"),
    part("Burnt fuses", "a blown fuse", FUSE_NOTE),
    part("Lithium-ion batteries", "a lithium-ion battery", LITHIUM_NOTE),
    part("18650 batteries", "an 18650 cell, a cylindrical lithium-ion battery", LITHIUM_NOTE),
    part("Battery packs", "a battery pack, several cells joined in one case", LITHIUM_NOTE),
    part("Laptop batteries", "a laptop battery", LITHIUM_NOTE),
    part("Mobile phone batteries", "a mobile phone battery", LITHIUM_NOTE),
    part("Toggle switches", "a toggle switch, flipped up and down by a lever"),
    part("DIP switches", "a DIP switch, a row of tiny switches on a circuit board for settings"),
    part("Slide switches", "a slide switch"),
    part("Rotary encoders", "a rotary encoder, a knob that turns without end and tells a device how far it turned"),
    part("Pin headers", "pin headers, rows of metal pins for plugging in wires or boards"),
    part("Heat sinks", "a heat sink, finned metal that carries heat away from a chip or transistor"),
    part("Buzzers", "a buzzer, a small part that beeps"),
    part("Vacuum tubes", "a vacuum tube (a valve), used in old radios and televisions and in guitar amplifiers",
         MAINS_NOTE),
    part("Cathode ray tubes", "a cathode ray tube, the picture tube of an old television or monitor", MAINS_NOTE),
    part("Defective electronic components", "a damaged or failed electronic part", EWASTE_NOTE),
]

# ----------------------------------------------------------------- Commons: cables and connectors

CABLES = [
    connector("HDMI cables", "an HDMI cable, for video and sound to a television or screen"),
    connector("DisplayPort", "a DisplayPort connector, for video to a computer screen (one corner is cut off)"),
    connector("VGA connectors", "a VGA connector, an older video plug with fifteen pins in three rows, usually blue"),
    connector("DVI connectors", "a DVI connector, a wide video plug for computer screens"),
    connector("TRS connectors", "a TRS jack plug (tip, ring and sleeve), an audio plug such as a headphone plug"),
    connector("XLR connectors", "an XLR connector, a round plug with three pins used for microphones"),
    connector("RCA connectors", "an RCA (phono) connector, a round plug for audio and video, often red, white and "
                                "yellow"),
    connector("Coaxial connectors", "a coaxial connector, for aerial, cable TV and radio cables", deeper=False),
    connector("F connectors", "an F connector, the screw-on plug for cable TV, satellite and aerial cables"),
    connector("Ethernet cables", "an Ethernet cable, for a wired network or internet connection"),
    connector("RJ45", "an RJ45 plug, the network plug on an Ethernet cable (it clicks in with a small latch)"),
    connector("Molex connectors", "a Molex connector, a power plug inside a computer"),
    connector("DC connectors", "a DC power connector, the small round plug of a power adapter"),
    connector("Power adapters", "a power adapter (a power brick), which turns mains power into low-voltage power for "
                                "a device"),
]

# ----------------------------------------------------------------- Commons: soldering, test equipment, repair

REPAIR = [
    part("Soldering tools", "a soldering tool", SOLDER_NOTE),
    part("Soldering stations", "a soldering station: a soldering iron with a stand and a temperature control",
         SOLDER_NOTE),
    part("Soldering joints", "soldered joints", SOLDER_NOTE),
    part("Solder wires", "solder wire, the metal melted to join parts", SOLDER_NOTE),
    part("Soft-soldering", "soft soldering", SOLDER_NOTE),
    part("Desoldering", "desoldering: removing solder to take a part off a board (with a solder sucker, desoldering "
                        "braid or hot air)", SOLDER_NOTE),
    part("Third hands", "a 'third hand' (helping hands), clips on arms that hold work for soldering"),
    part("Wave soldering", "wave soldering, the factory machine that solders whole circuit boards at once"),
    part("Digital multimeters", "a digital multimeter, which measures voltage, current and resistance"),
    part("Analog multimeters", "an analogue multimeter, which shows voltage, current and resistance with a needle"),
    part("Logic analyzers", "a logic analyser, which records many digital signals at once"),
    part("Function generators", "a function generator, which makes test signals"),
    part("Signal generators", "a signal generator, which makes test signals", deeper=False),
    part("Spectrum analyzers", "a spectrum analyser, which shows the frequencies in a signal", deeper=False),
    part("LCR meters", "an LCR meter, which measures inductance, capacitance and resistance"),
    part("Electronic test equipment", "electronic test equipment", deeper=False),
    part("Electronics workbenches", "an electronics workbench"),
    part("Antistatic bags", "an antistatic bag, which protects circuit boards and parts from static electricity"),
    part("Spudgers", "a spudger, a plastic prying tool for opening phones and laptops without scratching them"),
    part("Disassembled mobile phones", "a mobile phone taken apart", LITHIUM_NOTE),
    part("Disassembled smartphones", "a smartphone taken apart", LITHIUM_NOTE),
    part("Disassembled laptops", "a laptop taken apart", LITHIUM_NOTE),
    part("Radio repair", "radio repair", MAINS_NOTE),
    part("Vacuum tube radios", "a valve (vacuum tube) radio", MAINS_NOTE, deeper=False),
    part("Audio amplifiers", "an audio amplifier", deeper=False),
    part("Assistive technology", "assistive technology: equipment that helps disabled people do things", deeper=False),
]

# ----------------------------------------------------------------- Commons: assistive and low-vision devices

DEVICE_NOTE = ("Care: use only the maker's battery and charger, keep it dry, clean screens and lenses with a soft "
               "lens cloth, and check the warranty, loan agreement or repair programme (an NLS player is repaired "
               "free through your library; a state Assistive Technology programme or VA VIST coordinator can help) "
               "before opening it.")
ASSISTIVE = [
    part("Braille embossers", "a braille embosser: a printer that punches braille dots into paper", DEVICE_NOTE),
    part("Braille printers", "a braille printer (embosser)", DEVICE_NOTE),
    part("Talking clocks", "a talking clock, which speaks the time at the press of a button", DEVICE_NOTE),
    part("Monoculars", "a monocular: a small one-eyed telescope, used by some low-vision people to see signs and "
                       "faces at a distance", "Care: clean the lenses only with a lens brush and lens cloth; turn "
                       "the focus ring gently."),
    part("Computer speakers", "computer speakers"),
    part("Optophone", "an optophone, an early reading machine that turned printed letters into sounds for blind "
                      "readers", deeper=False),
    part("Mobile phone covers", "a mobile phone case (cover)"),
    part("Smartphone screen protectors", "a screen protector, a thin film or glass sheet that protects a phone "
                                         "screen"),
]

# ----------------------------------------------------------------- Commons: circuit diagrams and symbols

DIAGRAMS = [
    drawing("Electronic circuit diagrams", "a circuit diagram (a schematic), which shows how electronic parts are "
                                           "connected, each part drawn as its symbol", deeper=False),
    drawing("Amplifier circuits", "a circuit diagram of an amplifier"),
    drawing("Resistor diagrams", "a diagram of resistors in a circuit"),
    drawing("Fuse symbols", "the symbol of a fuse, as drawn in circuit diagrams"),
    drawing("Fuse diagrams", "a diagram of fuses in a circuit"),
    drawing("IC pinout diagrams", "a pinout diagram of a chip, which says what each pin of an integrated circuit is "
                                  "for"),
    drawing("Electronic symbols", "an electronic symbol, as drawn in circuit diagrams"),
]


def build_commons_electronic_parts(limit):
    """The commons_electronic_parts pack (see the module docstring)."""
    return build_commons_facts(PARTS, limit, "elecpart", facts=part_facts)


def build_commons_cables_connectors(limit):
    """The commons_cables_connectors pack (see the module docstring)."""
    return build_commons_facts(CABLES, limit, "eleccable")


def build_commons_electronics_repair(limit):
    """The commons_electronics_repair pack (see the module docstring)."""
    return build_commons_facts(REPAIR, limit, "elecrepair", facts=part_facts)


def build_commons_assistive_devices(limit):
    """The commons_assistive_devices pack (see the module docstring)."""
    return build_commons_facts(ASSISTIVE, limit, "elecassist", facts=part_facts)


def build_commons_circuit_diagrams(limit):
    """The commons_circuit_diagrams pack (see the module docstring): drawings too."""
    return build_commons_facts(DIAGRAMS, limit, "elecdiagram", drawings=True)


# ----------------------------------------------------------------- Open Images

ELECTRONICS_OI = [
    group("What electronics are in this picture?",
          {"Electronics": "electronics", "Computer": "a computer", "Television set": "a television set",
           "Electric motor": "an electric motor", "Memory card": "a memory card",
           "Adapter (Electrical)": "an electrical adapter",            "Personal computer hardware": "computer parts",                       "Analog television": "an old analogue television",
                      "Audio power amplifier": "a power amplifier"}),
    group("What electronic parts are in this picture?",
          {"Electronic component": "electronic components", "Passive circuit component": "electronic components",
           "Semiconductor": "a semiconductor chip", "Chipset": "a chip", "Diode": "a diode",
           "Light-emitting diode": "a light-emitting diode (LED)", "Fuse": "a fuse",
                      "Operational amplifier": "an operational amplifier chip"}),
    group("What soldering or test things are in this picture?",
          {"Solder": "solder",                       "Circuit prototyping": "a circuit being built on a board"}, SOLDER_NOTE),
    group("What wiring or cables are in this picture?",
          {"Electrical wiring": "electrical wiring", "Networking cables": "network cables",
           "Ethernet cable": "an Ethernet cable", "Data transfer cable": "a data cable",                       "Optical fiber cable": "a fibre-optic cable",            "Cable management": "tidied cables"}),
]


def build_open_images_electronics(limit):
    """open_images_electronics (see the module docstring)."""
    return build_oi_gap("open_images_electronics", ELECTRONICS_OI, limit, 9301)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
ELECTRONICS_PACKS = {
    "commons_electronic_parts": (build_commons_electronic_parts, COMMONS_LICENCE.format(
        what="resistor, capacitor, diode, transistor, chip, fuse, battery, switch and valve")),
    "commons_cables_connectors": (build_commons_cables_connectors, COMMONS_LICENCE.format(
        what="cable and connector")),
    "commons_electronics_repair": (build_commons_electronics_repair, COMMONS_LICENCE.format(
        what="soldering, test equipment and electronics repair")),
    "commons_assistive_devices": (build_commons_assistive_devices, COMMONS_LICENCE.format(
        what="braille embosser, talking clock, monocular, reading machine, phone cover and screen protector")),
    "commons_circuit_diagrams": (build_commons_circuit_diagrams, COMMONS_LICENCE.format(
        what="circuit diagram and electronic symbol")),
    "open_images_electronics": (build_open_images_electronics, OI_LICENCE),
}
ELECTRONICS_LIMITS = {
    "commons_electronic_parts": 2500,      # 46 categories, an even share each
    "commons_cables_connectors": 600,      # 14 categories
    "commons_electronics_repair": 1500,    # 26 categories
    "commons_assistive_devices": 250,      # 8 categories, few open files each
    "commons_circuit_diagrams": 800,       # 7 categories of drawings
    "open_images_electronics": 1500,       # 25 labels, few photos for most
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
ELECTRONICS_COMMONS_KEYS = ("commons_electronic_parts", "commons_cables_connectors", "commons_electronics_repair",
                            "commons_assistive_devices", "commons_circuit_diagrams")
# Every Commons spec of this file, for the self-test.
ELECTRONICS_SPECS = PARTS + CABLES + REPAIR + ASSISTIVE + DIAGRAMS


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an electronics pack builder.")
    parser.add_argument("key", choices=sorted(ELECTRONICS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = ELECTRONICS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
