"""Picture packs for RADIO COMMUNICATIONS: ham and other two-way radio, antennas and station gear, and off-grid mesh
and data radio (the owner's request of 2026-11-22: radio communications as its own section, separate from
preparedness). Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as
(None, None, row) rows naming the same picture. The limit counts pictures.

Already in other packs, and so NOT repeated (packs/test_radio.py checks that no Commons category here is named by
another pack file and no Open Images label is asked twice): coaxial cables and coaxial connectors in general,
vacuum tube radios and radio repair, power cables and test equipment (electronics_packs, hardware_packs); radios,
transistor radios and satellite dishes as household things (things_packs, and Open Images' Radio, Radio receiver,
Antenna and Satellite dish); microphones and loudspeakers (everyday_packs); megaphones (gaps_oi_packs); weather maps
(weather_map_packs); NOAA Weather Radio's warnings and the preparedness pictures (preparedness_packs.py).

Answers say only what the source says: a Commons category's name, with one short line written here on what that kind
of radio, antenna or part is, or an Open Images label people confirmed; no frequency, power, call sign, model or
reading is ever made up (each photo's own caption or description is its second row). Every answer about a radio,
antenna, tower or station ends with RADIO_SAFETY (power lines, towers, lightning and grounding, RF exposure, transmit
only where licensed or the service allows, no encryption on amateur frequencies; the same words as
textbooks/radio_books.py), and the licence-free and licensed services say which they are (LICENCE_FREE, HAM_ONLY).

The packs (all open: CC0, public domain or CC BY, checked file by file; Open Images labels CC BY 4.0):
  commons_radios               Wikimedia Commons: amateur radio transceivers, receivers and transmitters, handheld
                               transceivers (the Baofeng UV-5R among them), Yaesu, Motorola and Uniden radios, CB
                               radios, marine radios, radio scanners, satellite phones, shortwave listening, NOAA
                               Weather Radio receivers, software-defined radio and portable amateur radio.
  commons_antennas_station     Commons: amateur radio antennas, Yagi-Uda, dipole, J-pole, loop, discone and
                               log-periodic antennas, antenna and lattice towers, baluns, UHF (PL-259 and SO-239),
                               BNC, SMA and N connectors, SWR meters and antenna analysers, telegraph and straight keys,
                               hand microphones, amateur repeaters, ham shacks and operators, hamfests, amateur radio
                               direction finding and amateur satellites (with the radio on the International Space
                               Station).
  commons_radio_cards_charts   Commons: QSL cards (with each card's call sign only where the file's own words give
                               it), Morse code charts, amateur radio frequency allocation charts and amateur radio maps.
  commons_mesh_data_radio      Commons: Meshtastic, LoRa and LoRaWAN devices, Heltec boards, APRS, packet radio,
                               digital amateur radio and slow-scan television.
  open_images_radio            Open Images V7: two-way radios, CB radios, antenna rotators and masts.

The share-alike Commons files and what was left out are in training-kit/kit/radio_sources.py.

    python packs/radio_packs.py commons_radios --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from gaps_oi_packs import group, build_oi_gap, QUICK

# ----------------------------------------------------------------- the safety notes (fixed sentences)

# The same words as textbooks/radio_books.py RADIO_SAFETY (the self-test checks).
RADIO_SAFETY = ("Radio safety: keep every antenna, mast and feed line far from power lines, more than the length of "
                "the antenna and mast from the nearest line (contact can kill). Never climb a tower without training "
                "and fall protection. Ground your station, and disconnect antennas when lightning is near. Follow the "
                "FCC's RF exposure limits and keep transmitting antennas away from people. Transmit only where you "
                "are licensed or the service allows it; encryption is not allowed on amateur frequencies; in an "
                "emergency, call 911 first.")
HAM_ONLY = "Transmitting on amateur (ham) frequencies needs an amateur radio licence; listening needs none."
LICENCE_FREE = ("In the US, FRS, MURS and CB radios need no licence; GMRS needs an FCC licence (one covers a family); "
                "amateur frequencies need an amateur licence.")
MESH_NOTE = ("Meshtastic and most LoRa mesh devices use licence-free bands (902 to 928 MHz in the US) at low power "
             "with encryption allowed; run on amateur frequencies or power under a ham licence, encryption is not "
             "allowed.")
LISTEN_NOTE = "Listening is legal almost everywhere in the US, but some states limit scanners in cars."
WEATHER_RADIO_NOTE = ("NOAA Weather Radio broadcasts warnings around the clock; program your county's SAME code (in "
                      "the reference library) so it alarms only for your area.")

ASK_RADIO = "What kind of radio is this?"
ASK_WHAT = "What is this?"
ASK_ANTENNA = "What kind of antenna is this?"
ASK_SEE = "What does this picture show?"


def radio(category, words, note="", question=ASK_RADIO, deeper=False, must=None):
    """A Commons spec for home_packs.build_commons_topic: "<question>" -> "This is <words>." then the note and
    RADIO_SAFETY; must: only files whose title or words match this pattern."""
    answer = f"This is {words}." + (f" {note}" if note else "") + f" {RADIO_SAFETY}"
    spec = (category, deeper, [(question, answer)])
    return spec + (must,) if must is not None else spec


def card(category, words, deeper=False, must=None):
    """A spec for a card, chart or map: "What is this?" -> "This is <words>." (no safety note: nothing to transmit)."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}.")])
    return spec + (must,) if must is not None else spec


# Brand categories also hold other products (Motorola's phones, Uniden's cordless phones, Yaesu's company photos):
# only files whose own words make them radios.
RADIO_WORDS = re.compile(r"\b(radios?|transceivers?|walkie|talkie|handhelds?|HT|scanners?|receivers?|VHF|UHF|ham|"
                         r"amateur|two-way|2-way|GMRS|FRS|CB|repeaters?|FT-\d+\w*|VX-\d+\w*|UV-\d+\w*)\b", re.I | re.S)

# ----------------------------------------------------------------- Commons: radios

RADIOS = [
    radio("Amateur radio transceivers", "an amateur (ham) radio transceiver: it both transmits and receives",
          HAM_ONLY, deeper=True),
    radio("Amateur radio receivers", "an amateur radio receiver", HAM_ONLY, deeper=True),
    radio("Amateur radio transmitters", "an amateur radio transmitter", HAM_ONLY, deeper=True),
    radio("Handheld transceivers", "a handheld transceiver (a walkie-talkie)", LICENCE_FREE, deeper=True),
    radio("Baofeng UV-5R", "a Baofeng UV-5R, a small, cheap dual-band (VHF and UHF) handheld radio",
          "It can transmit on amateur and other frequencies; transmit only on those you are licensed for (the FCC "
          "has acted against such radios used on GMRS and FRS channels). " + HAM_ONLY),
    radio("Yaesu", "a Yaesu radio", HAM_ONLY, must=RADIO_WORDS),
    radio("Motorola radios", "a Motorola two-way radio", LICENCE_FREE, deeper=True, must=RADIO_WORDS),
    radio("Uniden", "a Uniden radio or scanner", LISTEN_NOTE, deeper=True, must=RADIO_WORDS),
    radio("CB radios", "a CB (Citizens Band) radio: 40 channels near 27 MHz, no licence needed in the US",
          LICENCE_FREE, deeper=True),
    radio("Marine radios", "a marine radio", "Channel 16 is the marine distress and calling channel; a marine VHF "
                                             "radio with DSC can send a distress alert with your position.",
          deeper=True),
    radio("Radio scanners", "a radio scanner: a receiver that searches many channels (police, fire, weather, "
                            "aircraft)", LISTEN_NOTE, deeper=True),
    radio("Satellite phones", "a satellite phone, which works where there is no mobile signal", "Satellite phones "
                                                                                               "need a clear view of "
                                                                                               "the sky.",
          deeper=True),
    radio("Shortwave listening", "shortwave listening: receiving long-distance broadcasts and radio traffic",
          LISTEN_NOTE, question=ASK_SEE),
    radio("NOAA Weather Radio", "a NOAA Weather Radio receiver or transmitter", WEATHER_RADIO_NOTE, deeper=True),
    radio("Software-defined radio", "a software-defined radio: a radio whose tuning and decoding are done by a "
                                    "computer", LISTEN_NOTE),
    radio("Portable amateur radio", "portable amateur radio: a ham station carried into the field", HAM_ONLY,
          question=ASK_SEE, deeper=True),
]

# ----------------------------------------------------------------- Commons: antennas, towers and station gear

ANTENNAS_STATION = [
    radio("Amateur radio antennas", "an amateur radio antenna", HAM_ONLY, ASK_ANTENNA, deeper=True),
    radio("Yagi-Uda antennas", "a Yagi-Uda antenna (a Yagi): a beam antenna with several rod elements that sends and "
                               "receives mostly in one direction", question=ASK_ANTENNA),
    radio("Dipole antennas", "a dipole antenna: two equal wires or rods fed in the middle", question=ASK_ANTENNA,
          deeper=True),
    radio("J-pole antennas", "a J-pole antenna: a vertical antenna shaped like the letter J, often for the 2-metre "
                             "band", question=ASK_ANTENNA),
    radio("Loop antennas", "a loop antenna", question=ASK_ANTENNA, deeper=True),
    radio("Discone antennas", "a discone antenna: a disc above a cone, which receives a very wide range of "
                              "frequencies", question=ASK_ANTENNA),
    radio("Log-periodic antennas", "a log-periodic antenna: a beam antenna whose elements grow longer along the boom, "
                                   "working over a wide band", question=ASK_ANTENNA, deeper=True),
    radio("Antenna towers", "an antenna tower", question=ASK_WHAT, deeper=True),
    radio("Lattice towers", "a lattice tower: an open steel framework tower", question=ASK_WHAT),
    radio("Baluns", "a balun: it joins a balanced antenna to an unbalanced coaxial feed line", deeper=True),
    radio("UHF connectors", "a UHF connector: the PL-259 plug and SO-239 socket used on most HF and many VHF radios "
                            "and antennas"),
    radio("BNC connectors", "a BNC connector: a bayonet coaxial connector that locks with a quarter turn",
          deeper=True),
    radio("SMA connectors", "an SMA connector: a small threaded coaxial connector, used on many handheld radios and "
                            "small antennas", deeper=True),
    radio("N connectors", "an N connector: a threaded, weatherproof coaxial connector for higher frequencies"),
    radio("SWR meters", "an SWR meter: it shows how well the antenna is matched to the radio", deeper=True),
    radio("Antenna analyzers", "an antenna analyser: it measures an antenna's SWR and impedance across frequencies"),
    radio("Telegraph keys", "a telegraph key, for sending Morse code", HAM_ONLY, ASK_WHAT, deeper=True),
    radio("Straight keys", "a straight key: a Morse key pressed up and down", HAM_ONLY, ASK_WHAT, deeper=True),
    radio("Hand microphones", "a hand microphone of a radio, with a push-to-talk button", question=ASK_WHAT,
          deeper=True),
    radio("Amateur radio repeaters", "an amateur radio repeater: it receives on one frequency and retransmits on "
                                     "another from a high place, so handheld radios reach much farther",
          "Repeaters need the right offset and access tone (CTCSS or DCS) set in the radio. " + HAM_ONLY, ASK_WHAT,
          deeper=True),
    radio("Ham shacks or operators", "an amateur radio station (a ham shack) or its operator", HAM_ONLY, ASK_SEE,
          deeper=True),
    radio("Hamfests", "a hamfest: an amateur radio fair and flea market", question=ASK_SEE, deeper=True),
    radio("Amateur radio direction finding", "amateur radio direction finding (a fox hunt): finding a hidden "
                                             "transmitter with a receiver and a directional antenna", HAM_ONLY,
          ASK_SEE, deeper=True),
    radio("Amateur radio satellites", "an amateur radio satellite, or a station working one", HAM_ONLY, ASK_SEE),
    radio("Amateur Radio on the International Space Station", "amateur radio on the International Space Station "
                                                              "(ARISS), through which astronauts talk with hams and "
                                                              "school groups", HAM_ONLY, ASK_SEE, deeper=True),
]

# ----------------------------------------------------------------- Commons: cards, charts and maps

CARDS_CHARTS = [
    card("QSL cards (amateur radio)", "a QSL card: a card amateur radio operators send each other to confirm a "
                                      "contact, printed with the station's call sign", deeper=True),
    card("Morse code", "about Morse code: letters and numbers sent as short and long signals (dits and dahs)",
         must=re.compile(r"\b(chart|table|alphabet|code|key|signal|letters?)\b", re.I)),
    card("Amateur radio frequency allocations", "an amateur radio frequency allocation chart: which bands hams may use "
                                                "and for what"),
    card("Amateur radio maps", "an amateur radio map (call sign areas, grid squares or zones)"),
]

# ----------------------------------------------------------------- Commons: mesh and data radio

MESH_DATA = [
    radio("Meshtastic", "a Meshtastic device: a small LoRa radio that passes text messages along a mesh of nodes, "
                        "without any phone network", MESH_NOTE, ASK_WHAT),
    radio("LoRa", "a LoRa radio or module: a long-range, low-power radio for small amounts of data", MESH_NOTE,
          ASK_WHAT, deeper=True),
    radio("LoRaWAN", "LoRaWAN equipment: a LoRa network for sensors, with gateways", MESH_NOTE, ASK_WHAT, deeper=True),
    radio("Heltec", "a Heltec board: a small development board with a LoRa radio, Wi-Fi, Bluetooth and often a little "
                    "screen, used for Meshtastic nodes", MESH_NOTE, ASK_WHAT, deeper=True),
    radio("Automatic Packet Reporting System", "APRS (the Automatic Packet Reporting System): position, weather and "
                                               "short messages sent by amateur radio", HAM_ONLY, ASK_SEE),
    radio("Packet radio", "packet radio: computers exchanging data over amateur radio", HAM_ONLY, ASK_SEE,
          deeper=True),
    radio("Digital amateur radio", "digital amateur radio (modes such as FT8, DMR, D-STAR, System Fusion and "
                                   "Winlink)", HAM_ONLY, ASK_SEE, deeper=True),
    radio("Slow scan television", "slow-scan television (SSTV): still pictures sent by amateur radio", HAM_ONLY,
          ASK_SEE),
]


def build_commons_radios(limit):
    """The commons_radios pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(RADIOS, limit, "radio")


def build_commons_antennas_station(limit):
    """The commons_antennas_station pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(ANTENNAS_STATION, limit, "antenna")


def build_commons_radio_cards_charts(limit):
    """The commons_radio_cards_charts pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CARDS_CHARTS, limit, "qsl")


def build_commons_mesh_data_radio(limit):
    """The commons_mesh_data_radio pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MESH_DATA, limit, "mesh")


# ----------------------------------------------------------------- Open Images

RADIO_OI = [
    group("What radio equipment is in this picture?",
          {"Two-way radio": "a two-way radio", "Citizens band radio": "a CB radio",
           "Antenna rotator": "an antenna rotator", "Mast": "a mast"}, RADIO_SAFETY),
]


def build_open_images_radio(limit):
    """open_images_radio (see the module docstring)."""
    return build_oi_gap("open_images_radio", RADIO_OI, limit, 9319)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
RADIO_PACKS = {
    "commons_radios": (build_commons_radios, COMMONS_LICENCE.format(
        what="amateur, handheld, CB, marine, scanner, satellite phone, weather radio and software-defined radio")),
    "commons_antennas_station": (build_commons_antennas_station, COMMONS_LICENCE.format(
        what="antenna, tower, balun, coaxial connector, meter, Morse key, microphone, repeater and ham station")),
    "commons_radio_cards_charts": (build_commons_radio_cards_charts, COMMONS_LICENCE.format(
        what="QSL card, Morse code, frequency allocation and amateur radio map")),
    "commons_mesh_data_radio": (build_commons_mesh_data_radio, COMMONS_LICENCE.format(
        what="Meshtastic, LoRa, Heltec, APRS, packet radio and digital amateur radio")),
    "open_images_radio": (build_open_images_radio, OI_LICENCE),
}
RADIO_LIMITS = {
    "commons_radios": 1000,              # 16 categories
    "commons_antennas_station": 1500,    # 25 categories
    "commons_radio_cards_charts": 300,   # 4 categories
    "commons_mesh_data_radio": 250,      # 8 small categories
    "open_images_radio": 400,            # 4 labels
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
RADIO_COMMONS_KEYS = ("commons_radios", "commons_antennas_station", "commons_radio_cards_charts",
                      "commons_mesh_data_radio")
# Every Commons spec of these packs (for the self-test).
RADIO_SPECS = RADIOS + ANTENNAS_STATION + CARDS_CHARTS + MESH_DATA


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a radio pack builder.")
    parser.add_argument("key", choices=sorted(RADIO_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = RADIO_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
