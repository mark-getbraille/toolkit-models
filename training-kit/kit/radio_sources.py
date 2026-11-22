"""RADIO COMMUNICATIONS for the Picture Model Training Kit (the owner's request of 2026-11-22: ham and other two-way
radio, and off-grid mesh and data radio, as their own section). This file lists:
  - the ready-made packs built in packs/radio_packs.py (group "permissive"; the kit downloads them with prepare_pack):
    commons_radios, commons_antennas_station, commons_radio_cards_charts, commons_mesh_data_radio and
    open_images_radio;
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (RADIO_NOT_INCLUDED).

As in home_crafts_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit
on the user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.
Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say; the radio safety note (power lines, towers, lightning and
grounding, RF exposure, transmit only where licensed or the service allows, no encryption on amateur frequencies) is
the same words as packs/radio_packs.py.

Picture-making (RADIO_PICTURE_MAKING_OK): the antennas, connectors and station gear, the cards and charts, and the
mesh devices (things and drawings) may be used; the radios pack (people hold handhelds in many photos) and Open Images
(people) may not.

    python -c "import sources, radio_sources"      (from the kit folder: checks the file loads)
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

# The same words as packs/radio_packs.py (the self-test checks they match).
RADIO_SAFETY = ("Radio safety: keep every antenna, mast and feed line far from power lines, more than the length of "
                "the antenna and mast from the nearest line (contact can kill). Never climb a tower without training "
                "and fall protection. Ground your station, and disconnect antennas when lightning is near. Follow the "
                "FCC's RF exposure limits and keep transmitting antennas away from people. Transmit only where you "
                "are licensed or the service allows it; encryption is not allowed on amateur frequencies; in an "
                "emergency, call 911 first.")
HAM_ONLY = "Transmitting on amateur (ham) frequencies needs an amateur radio licence; listening needs none."
MESH_NOTE = ("Meshtastic and most LoRa mesh devices use licence-free bands (902 to 928 MHz in the US) at low power "
             "with encryption allowed; run on amateur frequencies or power under a ham licence, encryption is not "
             "allowed.")


def thing(category, words, note="", deeper=False, question="What is this?"):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." then the note and
    the radio safety note."""
    return (category, question, f"This is {words}." + (f" {note}" if note else "") + f" {RADIO_SAFETY}", deeper)


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

# Categories of packs/radio_packs.py that need no word filter (the brand categories are left out).
RADIO_SA = [
    thing("Amateur radio transceivers", "an amateur (ham) radio transceiver: it both transmits and receives",
          HAM_ONLY, True, "What kind of radio is this?"),
    thing("Handheld transceivers", "a handheld transceiver (a walkie-talkie)", deeper=True,
          question="What kind of radio is this?"),
    thing("CB radios", "a CB (Citizens Band) radio: 40 channels near 27 MHz, no licence needed in the US", deeper=True,
          question="What kind of radio is this?"),
    thing("Yagi-Uda antennas", "a Yagi-Uda antenna (a Yagi): a beam antenna with several rod elements that sends and "
                               "receives mostly in one direction", question="What kind of antenna is this?"),
    thing("Dipole antennas", "a dipole antenna: two equal wires or rods fed in the middle", deeper=True,
          question="What kind of antenna is this?"),
    thing("Telegraph keys", "a telegraph key, for sending Morse code", HAM_ONLY, True),
    thing("SWR meters", "an SWR meter: it shows how well the antenna is matched to the radio", deeper=True),
    thing("Meshtastic", "a Meshtastic device: a small LoRa radio that passes text messages along a mesh of nodes, "
                        "without any phone network", MESH_NOTE),
]


def prepare_radio_commons_sa(source, data_dir, work, cap):
    """Commons transceiver, handheld, CB radio, Yagi and dipole antenna, telegraph key, SWR meter and Meshtastic
    categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(RADIO_SA, cap, source.test, "radio-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

RADIO_SOURCES = [
    Source("commons_radios", "Radios: amateur transceivers, receivers and transmitters, handhelds (the Baofeng UV-5R "
                             "among them), Yaesu, Motorola and Uniden radios, CB and marine radios, scanners, "
                             "satellite phones, NOAA weather radios and software-defined radio, with the radio safety "
                             "and licence notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 230 MB"),
    Source("commons_antennas_station", "Antennas and station gear: Yagi, dipole, J-pole, loop, discone and "
                                       "log-periodic antennas, towers, baluns, UHF, BNC, SMA and N connectors, SWR "
                                       "meters and analysers, Morse keys, microphones, repeaters, ham shacks, "
                                       "hamfests, fox hunts and amateur satellites (Wikimedia Commons, ready-made "
                                       "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 340 MB"),
    Source("commons_radio_cards_charts", "QSL cards, Morse code charts, amateur frequency allocation charts and amateur "
                                         "radio maps (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    Source("commons_mesh_data_radio", "Off-grid mesh and data radio: Meshtastic and LoRa devices, Heltec boards, APRS, "
                                      "packet radio, digital amateur radio and slow-scan television (Wikimedia "
                                      "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 250, 5, prepare_pack, "about 60 MB"),
    Source("open_images_radio", "Two-way radios, CB radios, antenna rotators and masts, with the radio safety note "
                                "(Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 400, 5, prepare_pack, "about 80 MB"),
    Source("radio_commons_sa", "Wikimedia Commons: amateur transceivers, handhelds, CB radios, Yagi and dipole "
                               "antennas, telegraph keys, SWR meters and Meshtastic devices, with the radio safety "
                               "note, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 5, prepare_radio_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: antennas, connectors and station gear, cards and charts, mesh
# devices (things and drawings); never the radios pack (hands and people) or Open Images (people).
RADIO_PICTURE_MAKING_OK = {"commons_radio_cards_charts", "commons_mesh_data_radio"}

# The kit topics each collection belongs to (topics.py lists them; the self-test checks they match): every collection in
# the radio communications topic (the owner's decision of 22 November 2026), the radios, antennas and mesh devices
# also with the devices in "machines", the cards and charts also in "documents".
RADIO_TOPICS = {
    "radio": ("commons_radios", "commons_antennas_station", "commons_radio_cards_charts", "commons_mesh_data_radio",
              "open_images_radio", "radio_commons_sa"),
    "machines": ("commons_radios", "commons_antennas_station", "commons_mesh_data_radio", "open_images_radio",
                 "radio_commons_sa"),
    "documents": ("commons_radio_cards_charts",),
}

RADIO_NOT_INCLUDED = {
    "Smithsonian NMAH and other museum radios (CC0)":
        "the museum collections are already read whole by met_collection, aic_collection, cleveland_collection and "
        "smithsonian; their old radios and telegraph keys reach the kit that way. Not repeated.",
    "Makers' product photos (Baofeng, Yaesu, Icom, Kenwood, Midland, Cobra, Garmin, goTenna, LILYGO, RAK)":
        "copyright of each maker; not used. Their manuals are links in the manual collections.",
    "Meshtastic project photos":
        "the documentation site's pictures are under the site's GPL-3.0 with the text, but many are makers' product "
        "renders; the Commons Meshtastic category (open files) is used instead.",
    "Commons categories that do not exist under the names tried (November 2026)":
        "Scanners (radio), Police scanners, Marine VHF radios, VHF radios, Shortwave radios, Crank radios, Emergency "
        "radios, LilyGO, RAK Wireless, APRS (the long name is used), Winlink, AREDN, Vertical antennas, Whip and "
        "rubber ducky antennas, Ground plane antennas, Antenna rotators, Antenna tuners, PL-259 connectors (UHF "
        "connectors is used), Morse keys and Paddle keys (Straight keys and Telegraph keys are used), Lightning "
        "arresters, Ground rods, Icom, Midland, Cobra Electronics, Garmin inReach, goTenna, RTL-SDR, Fox hunting and "
        "ARRL Field Day.",
    "Commons categories already asked by another pack":
        "Coaxial cables and Coaxial connectors (electronics_packs, hardware_packs; the connector kinds UHF, BNC, SMA "
        "and N are asked here, as that pack does not walk its subcategories), Transistor radios and Radios "
        "(things_packs), Microphones (Hand microphones is asked here), Vacuum tube radios and Radio repair "
        "(electronics_packs): not repeated.",
    "Open Images labels left out":
        "Radio, Radio receiver, Antenna and Satellite dish (things_packs), Microphone and Loudspeaker (everyday_packs), "
        "Megaphone (gaps_oi_packs): asked by other packs; Scanner (also a document scanner) and Ham (the food): "
        "other meanings.",
}
