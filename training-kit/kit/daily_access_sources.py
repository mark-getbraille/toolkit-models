"""EVERYDAY ACCESS for the Picture Model Training Kit: finding your way inside public buildings, and the other
everyday-access packs made with it (see DAILY_ACCESS_SOURCES). This file lists:
  - the ready-made packs built in packs/ (group "permissive"; the kit downloads them with prepare_pack):
      indoor_packs.py              commons_indoor_wayfinding, open_images_indoor
      appliance_controls_packs.py  commons_appliance_controls, open_images_appliance_controls
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sign-up, permission and not-included collections looked at for these subjects, with the reason
    (DAILY_ACCESS_SIGN_UP, DAILY_ACCESS_NOT_INCLUDED).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked); sign text is
read only where a category names it (a room number, a men's, women's or all-gender toilet).

Picture-making (DAILY_ACCESS_PICTURE_MAKING_OK): the indoor collections show public places with people in them and are
for describing only, as are the Open Images appliance photos; the Commons appliance controls (things) may be used.
sources.py puts every key not in DAILY_ACCESS_PICTURE_MAKING_OK in NOT_FOR_PICTURE_MAKING.

    python -c "import sources, daily_access_sources"      (from the kit folder: checks the file loads)
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


# ----------------------------------------------------------------- share-alike: Commons BY-SA files

# The main categories of packs/indoor_packs.py (category, question, answer, also its subcategories).
INDOOR_SA = [
    ("Corridors", "What kind of place is this?", "This is a corridor (hallway) inside a building.", False),
    ("Hotel lobbies", "What kind of place is this?", "This is a hotel lobby.", False),
    ("Entrance halls", "What kind of place is this?", "This is the entrance hall (lobby) of a building.", False),
    ("Stairwells", "What kind of place is this?", "This is a stairwell: the stairs inside a building.", True),
    ("Interiors of elevators", "What kind of place is this?", "This is the inside of a lift (elevator).", False),
    ("Escalators", "What is this?", "This is an escalator: moving stairs.", False),
    ("Men's toilet signs", "What does this sign tell me?", "It is a men's toilet sign.", True),
    ("Women's toilet signs", "What does this sign tell me?", "It is a women's toilet sign.", True),
    ("Unisex toilet signs", "What does this sign tell me?", "It is an all-gender (unisex) toilet sign.", True),
    ("Public toilets", "What kind of place is this?", "This is a public toilet (restroom).", False),
    ("Emergency exits", "What is this?", "This is an emergency exit.", False),
    ("Door signs", "What does this sign tell me?", "It is a sign on a door.", True),
    ("Wayfinding signs", "What does this sign tell me?", "It is a wayfinding sign: it shows the way.", True),
    ("Reception desks", "What is this?", "This is a reception desk.", False),
    ("Information desks", "What is this?", "This is an information desk.", False),
    ("Waiting rooms", "What kind of place is this?", "This is a waiting room.", False),
    ("Ticket offices", "What kind of place is this?", "This is a ticket office.", True),
    ("Airport gates", "What kind of place is this?", "This is an airport gate.", True),
    ("Departure boards", "What is this?", "This is a departure board.", True),
    ("Ticket barriers", "What is this?", "This is a ticket barrier (fare gate).", True),
]


# The main categories of packs/appliance_controls_packs.py (the broad ones are left out: the share-alike entry has no
# appliance-word filter).
APPLIANCE_SA = [
    ("Rotary switches", "What is this?", "This is a rotary switch: a knob that clicks round to choose a setting.",
     True),
    ("Air conditioner remote controls", "What is this?", "This is an air-conditioner remote control.", True),
    ("Nest Learning Thermostat", "What is this?", "This is a Nest smart thermostat.", False),
    ("Cooktops", "What is this?", "This is a cooktop (hob), with knobs or touch controls.", True),
]


def prepare_appliance_commons_sa(source, data_dir, work, cap):
    """Commons appliance control categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(APPLIANCE_SA, cap, source.test, "applctl-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_indoor_commons_sa(source, data_dir, work, cap):
    """Commons indoor wayfinding categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(INDOOR_SA, cap, source.test, "indoor-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- the table

DAILY_ACCESS_SOURCES = [
    # ---- ready-made packs (packs/indoor_packs.py)
    Source("commons_indoor_wayfinding", "Inside public buildings: lobbies, corridors, stairwells, lifts, escalators, "
                                        "toilet signs, room numbers, door and wayfinding signs, desks, waiting rooms, "
                                        "ticket offices, gates and ticket barriers (Wikimedia Commons, ready-made "
                                        "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 2500, 25, prepare_pack, "about 550 MB"),
    Source("open_images_indoor", "Lobbies, halls, waiting rooms, restrooms, airport terminals, signs, maps, revolving "
                                 "and sliding doors (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2500, 25, prepare_pack, "about 500 MB"),
    # ---- ready-made packs (packs/appliance_controls_packs.py)
    Source("commons_appliance_controls", "Appliance controls close up: rotary switches, control panels, push buttons, "
                                         "touch screens, timers, air-conditioner remotes, smart thermostats and "
                                         "cooktops, a setting only where the file says it (Wikimedia Commons, "
                                         "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 600, 10, prepare_pack, "about 130 MB"),
    Source("open_images_appliance_controls", "Control knobs, control panels, push buttons, LED displays, doorbells, "
                                             "coffee makers, air conditioners, dryers, stoves and convection ovens "
                                             "(Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 2000, 20, prepare_pack, "about 400 MB"),
    # ---- share-alike
    Source("appliance_commons_sa", "Wikimedia Commons: rotary switches, air-conditioner remotes, smart thermostats and "
                                   "cooktops, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 300, 5, prepare_appliance_commons_sa, "about 60 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
    Source("indoor_commons_sa", "Wikimedia Commons: corridors, lobbies, stairwells, lifts, escalators, toilet signs, "
                                "door and wayfinding signs, desks, waiting rooms and gates, files under CC BY-SA or "
                                "GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 1500, 15, prepare_indoor_commons_sa, "about 300 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: the Commons appliance controls (things); not the indoor
# collections or the Open Images photos (people).
DAILY_ACCESS_PICTURE_MAKING_OK = {"commons_appliance_controls", "appliance_commons_sa"}

DAILY_ACCESS_SIGN_UP = {
    "Places365 (MIT CSAIL)":
        "365 kinds of scenes, among them lobby, corridor, elevator, escalator, waiting room, ticket booth and airport "
        "terminal; 'for non-commercial research and educational purposes' and the download is now behind a request "
        "form (http://places2.csail.mit.edu). Research use only: the owner can ask and use the own-pictures folder.",
    "ADE20K (MIT CSAIL)":
        "scene parsing with indoor rooms and halls labelled object by object; download needs an account and "
        "agreeing to its terms (https://groups.csail.mit.edu/vision/datasets/ADE20K/), photos from other datasets "
        "keep their owners' rights. Research use only.",
    "Matterport3D and InteriorNet":
        "3D scans and computer-made views of homes and buildings; both need a signed licence or terms of use "
        "(https://niessner.github.io/Matterport/, https://interiornet.org). Recorded only.",
    "Indoor Sign Dataset, ISD (Almeida et al., VISAPP 2019)":
        "1,200 photos of accessibility, emergency exit, men's and women's toilet, wifi and no-smoking signs, made for "
        "wearable aids for blind people; no licence stated (the page asks only for a citation) and the files are in a "
        "Google Drive folder (https://sites.google.com/view/indoorsigndatasetisd). Ask the authors for an open "
        "licence before use.",
    "Roboflow Universe washing-machine panel sets (some CC BY 4.0, with buttons, display and selector marked)":
        "https://universe.roboflow.com : a free Roboflow account and API key to export; check each set's licence and "
        "where its photos came from.",
    "A Dataset ... to Classify and Augment Interface Elements of Household Appliances (Zenodo 7586107)":
        "photos of appliance control panels with every control labelled, made to help people with visual "
        "impairment; the record states no licence and its files are restricted (log in and ask for access). Ask the "
        "authors.",
}

DAILY_ACCESS_NOT_INCLUDED = {
    "Appliance Knobs (Codatta / Humanbased-AI on Hugging Face)":
        "408 front and side photo pairs of appliance knobs, but under the OpenRAIL licence (use restrictions, not an "
        "open data licence), with no setting or angle labels and no statement of where the photos come from.",
    "Water-Heater Control Panel Detection Dataset (Mobiusi on Hugging Face)":
        "CC BY-NC-SA 4.0 and gated (an account is needed); a non-commercial share-alike entry could be added once its "
        "photos' origin is known.",
    "Amazon Berkeley Objects appliance listings":
        "already things_packs.abo_products (microwaves, coffee makers, air conditioners, washer-dryers ...): catalogue "
        "photos with no control or setting labels, so not repeated.",
    "Commons categories for appliance control panels (November 2026)":
        "none exists for stove knobs, oven controls, microwave, washing-machine or dishwasher control panels, dimmer "
        "switches or LCD displays; Control panels, Push buttons, Touchscreens and Timers are used for their appliance "
        "files only.",
    "MIT Indoor67 (Quattoni and Torralba, 2009)":
        "67 indoor scene kinds (corridor, lobby, waiting room, elevator, stairscase, airport inside ...); 'The images "
        "provided here are for research purposes only' (https://web.mit.edu/torralba/www/indoor.html) and the "
        "download (groups.csail.mit.edu/vision/LabelMe/NewImages/indoorCVPR_09.tar) answered 404 in November 2026.",
    "SUN397":
        "research use; its download page is gone (see personal_sources.py).",
    "MCIndoor20000 (Marshfield Clinic)":
        "20,000 photos of doors, stairs and hospital signs, 'for any academic, educational, and research purposes', "
        "but the images 'will no longer be hosted' (removed on 9 November 2020; github.com/bircatmcri/MCIndoor20000).",
    "Commons categories with no files (November 2026)":
        "Lobbies, Elevator lobbies, Hallways, Moving walkways, Gender-neutral toilet signs, Information signs, "
        "Lifts (the spellings Corridors, Entrance halls, Foyers, Interiors of elevators, Moving ramps and Unisex "
        "toilet signs do have files and are used); no category exists for building directories, indoor 'you are here' maps, "
        "boarding gates, security checkpoints or fare gates (Wayfinding signs, Tactile maps, Airport gates and "
        "Ticket barriers are the nearest and are used).",
}
