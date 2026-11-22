"""EVERYDAY ACCESS for the Picture Model Training Kit: finding your way inside public buildings, and the other
everyday-access packs made with it (see DAILY_ACCESS_SOURCES). This file lists:
  - the ready-made packs built in packs/ (group "permissive"; the kit downloads them with prepare_pack):
      indoor_packs.py              commons_indoor_wayfinding, open_images_indoor
      appliance_controls_packs.py  commons_appliance_controls, open_images_appliance_controls
      baby_packs.py                commons_baby_products, open_images_baby_products, abo_baby_products
      household_hazard_packs.py    commons_household_hazards, open_images_household_hazards
      care_label_packs.py          laundry_care_labels (computer-made labels and Commons photos)
      health_test_packs.py         lfa_covid_tests, commons_home_health_tests
      medication_label_packs.py    commons_medication_labels
      synthetic_bills_packs.py     synthetic_bills (computer-made, made-up details)
  - the share-alike Commons files of the same Commons categories (group "share-alike": only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sign-up, permission and not-included collections looked at for these subjects, with the reason
    (DAILY_ACCESS_SIGN_UP, DAILY_ACCESS_NOT_INCLUDED).

As in drinks_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on
the user's own computer, straight from where its makers publish it (the packs from the kit's own release), only when
the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked); sign text is
read only where a category names it (a room number, a men's, women's or all-gender toilet).

Picture-making (DAILY_ACCESS_PICTURE_MAKING_OK): only the Commons appliance controls, the care labels and the
figshare test cassettes (things only) may be used; sources.py puts every other key in NOT_FOR_PICTURE_MAKING.

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
    # ---- ready-made pack (packs/synthetic_bills_packs.py)
    Source("synthetic_bills", "Bills and statements, computer-made with made-up names and amounts: utility, phone, "
                              "bank and credit-card statements, pharmacy receipts and medical bills; the amount due, "
                              "due date, account holder and how to pay (synthetic, ready-made pack)",
           "CC0 (drawn by packs/synthetic_bills_packs.py from a fixed seed; no real person's documents)",
           "Computer-made by the kit's makers (packs/synthetic_bills_packs.py)", "permissive", 4000, 40, prepare_pack,
           "about 600 MB"),
    # ---- ready-made pack (packs/medication_label_packs.py)
    Source("commons_medication_labels", "Medicine packages, bottles, inhalers, pens and eye drops whose own record "
                                        "names the medicine and its strength, with the check-with-your-pharmacist note "
                                        "(Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain, CC BY or an open government licence (credited in CREDITS.txt); captions CC0",
           COMMONS_CREDIT, "permissive", 300, 5, prepare_pack, "about 70 MB"),
    # ---- ready-made packs (packs/health_test_packs.py)
    Source("lfa_covid_tests", "COVID-19 rapid antigen test cassettes after a known amount of virus protein was added, "
                              "read from the researchers' record, with the faint-lines note (figshare, ready-made "
                              "pack)",
           "CC BY 4.0 (figshare collection 7581998, Anne M. Davis and Asahi Tomitaka, 2024)",
           "Images of COVID-19 Lateral Flow Assay Results, Anne M. Davis and Asahi Tomitaka, figshare (CC BY 4.0), "
           "https://figshare.com/collections/7581998", "permissive", 1200, 20, prepare_pack, "about 250 MB"),
    Source("commons_home_health_tests", "Home health tests: rapid antigen, pregnancy and ovulation tests and glucose "
                                        "meters, the result only where the photo's own words give it (Wikimedia "
                                        "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 10, prepare_pack, "about 90 MB"),
    # ---- ready-made pack (packs/care_label_packs.py)
    Source("laundry_care_labels", "Clothing care labels close up: computer-made labels with the care symbols read out, "
                                  "and Commons photos of real labels (synthetic and Wikimedia Commons, ready-made "
                                  "pack)",
           "Computer-made labels CC0 (packs/care_label_packs.py); Commons pictures CC0, public domain or CC BY "
           "(credited in CREDITS.txt); captions CC0", COMMONS_CREDIT + "; computer-made labels by the kit's makers",
           "permissive", 3000, 30, prepare_pack, "about 250 MB"),
    # ---- ready-made packs (packs/household_hazard_packs.py)
    Source("commons_household_hazards", "Household hazards stated by the photo's own words: frayed cords, overloaded "
                                        "sockets, exposed wiring, mould, leaks, damaged smoke alarms, spent "
                                        "extinguishers, blocked exits, trip hazards, heaters too close, with safety "
                                        "notes (Wikimedia Commons, ready-made pack)",
           "Pictures CC0, public domain (US government works, CPSC and NIST among them) or CC BY (credited in "
           "CREDITS.txt); captions CC0", COMMONS_CREDIT, "permissive", 200, 5, prepare_pack, "about 45 MB"),
    Source("open_images_household_hazards", "Leaks, space heaters and heaters, fire sprinklers and fire alarms, with "
                                            "safety notes (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    # ---- ready-made packs (packs/baby_packs.py)
    Source("commons_baby_products", "Baby and young child products: bottles, formula, baby food, car seats, cribs, "
                                    "high chairs, playpens, gates, strollers, monitors, pacifiers, oral syringes and "
                                    "more, features only from the record, with safety notes (Wikimedia Commons, "
                                    "ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 180 MB"),
    Source("open_images_baby_products", "Baby gates, bibs, baby food, infant formula, baby monitors, cradles, child "
                                        "car seats, prams, baby carriers, mobiles and rattles (Open Images, ready-made "
                                        "pack)",
           OI_OPEN, OI_CREDIT, "permissive", 1500, 15, prepare_pack, "about 300 MB"),
    Source("abo_baby_products", "Baby products in Amazon's catalogue photos: bottles and nipples, pacifiers by age "
                                "stage, bowls, sheets and sleeping bags (Amazon Berkeley Objects, ready-made pack)",
           "CC BY 4.0 (Amazon Berkeley Objects)", "Amazon Berkeley Objects (Amazon.com and UC Berkeley), CC BY 4.0, "
           "https://amazon-berkeley-objects.s3.amazonaws.com/", "permissive", 80, 5, prepare_pack, "about 20 MB"),
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

# The collections a picture-making model may learn from: the Commons appliance controls, the care labels and the
# figshare test cassettes (things only); never the indoor, medicine-label, bill, hazard, home-test or baby collections,
# nor the Open Images photos (people, children, private papers).
DAILY_ACCESS_PICTURE_MAKING_OK = {"commons_appliance_controls", "appliance_commons_sa", "laundry_care_labels",
                                  "lfa_covid_tests"}

DAILY_ACCESS_SIGN_UP = {
    "Roboflow Universe laundry-symbol and care-label sets (several CC BY 4.0 or MIT)":
        "https://universe.roboflow.com (for example 'Laundry Symbols' by laundrymanager, 'laundry_symbols' by "
        "alexander-pitkin, 'care_symbols' by decodelaundrysymbols): a free Roboflow account and API key to export; "
        "where their photos come from is not stated. The computer-made labels of laundry_care_labels cover the same "
        "symbols.",
    "Kaggle lateral flow test sets (for example the 325-photo set used in arXiv 2404.14990, said to be MIT)":
        "https://www.kaggle.com : a free Kaggle account and API token are needed to download; check each set's "
        "licence and where its photos came from.",
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
    "CPSC recall photos of baby products (saferproducts.gov Recalls API)":
        "not public domain as a whole: CPSC allows copying recall notices, but 'any other use of photographs ... may "
        "require permission from a copyright holder' (the recalling firms' own pictures). Already the personal-use "
        "entry us_sources.cpsc_recalls, which includes the baby product recalls.",
    "Commons diapers, baby baths and changing tables":
        "their photos often show an undressed baby (the owner's rule: never unclothed children outside the medical "
        "and birth collections), so they are not taken; ABO's diaper and wipe listings are abo_packaged_goods'.",
    "CPSC and NIST photo galleries (cpsc.gov, nist.gov, their Flickr streams)":
        "CPSC's recall photos are the recalling firms' own pictures (not public domain; see packaged_goods_sources.py) "
        "and the agencies' Flickr streams fall under Flickr's API terms (no storing). Their own public-domain photos "
        "that people copied to Commons are found by commons_household_hazards' searches, each file's licence checked.",
    "Commons categories for household hazards (November 2026)":
        "none exists for overloaded sockets, frayed or damaged cords, exposed wiring, blocked exits, trip hazards, "
        "expired extinguishers or damaged smoke alarms; Commons search finds the files whose own words say so. Mould, "
        "water damage, smoke alarms and extinguisher gauges are home_safety_packs' (not repeated).",
    "FDA at-home test pages and EUA instructions (fda.gov)":
        "the pictures on FDA's at-home COVID-19 test pages are the makers' packaging, shown as small thumbnails, and "
        "the EUA 'instructions for use' are the makers' own documents (as with DailyMed's labels: the makers' "
        "copyright); fda.gov asks robots to wait 30 seconds between pages. Not built; the general reading rule "
        "(control line and test line) is written into the answers of health_test_packs.py.",
    "Machine learning for determining lateral flow device results (University of Birmingham, Mendeley Data "
    "hj9hmywh9c)":
        "CC BY 4.0, but it holds two PDF documents (a validation report and a study protocol), no pictures.",
    "REACT-2 lateral flow image library (Imperial College London)":
        "about 595,000 participants' photos of home antibody tests, described in Communications Medicine (2022), "
        "but not released for download.",
    "FDA and DailyMed package and label pictures (as open packs)":
        "the package and label art is the drug makers' (NLM: content 'licensed from private individuals, companies, "
        "or organizations that may be protected'), so they stay the kit's research entries dailymed_human_labels and "
        "dailymed_vet_labels (med_vet_sources.py), which already take each label's package, carton, bottle or "
        "container picture. Not an open pack.",
    "Mobile-Captured Drug Packs (Mendeley Data bsmy5jjysy, CC BY 4.0)":
        "2,000 phone photos of 166 drug packs, but no names or strengths are given with them (the files are numbered "
        "photos only), so no answer could come from label data.",
    "Italian OTC medicines (mennox on Hugging Face, tagged Apache-2.0)":
        "718 packaging pictures with names, but the page does not say where the pictures come from (they look like "
        "shop catalogue images, whose rights the uploader may not hold). Not used.",
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
        "toilet signs do have files and are used); no category exists for building directories, indoor 'you are "
        "here' maps, "
        "boarding gates, security checkpoints or fare gates (Wayfinding signs, Tactile maps, Airport gates and "
        "Ticket barriers are the nearest and are used).",
}
