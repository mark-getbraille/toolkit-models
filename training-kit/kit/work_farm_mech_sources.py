"""WORKPLACES, FARMS and BUILDING MECHANICAL SYSTEMS (mostly the United States and Canada) for the Picture Model
Training Kit: the collections that cannot be ready-made packs because of their licence, and the ones that need a
sign-up or were looked at and left out. The open ones (Commons workplace, farm and building mechanical categories,
and the USDA NRCS photos) are packs in packs/work_farm_mech_packs.py.

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link and the exact terms line are in each entry).

Groups (Source.group, as in sources.py):
  "share-alike"  CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with them
                 is CC BY-SA.

Answers are fixed sentences from each source's own words (a Commons category's name, the file's own caption), never
written by an AI model.

Safety (packs/SOURCE-RULES.md): no sexual content (files whose words name nudity or underwear are left out); files
whose words name a child, an injury, a death or an accident are left out (farm and factory photos of children can
show child labour or danger). In the farm and building-mechanical entry, files whose words name a person are left
out too, so it shows machines and buildings and may be used for picture-making; the workplace entry keeps workers
and is for describing only.

The collections (WORK_FARM_MECH_SOURCES):
  share-alike
    work_commons_sa       Wikimedia Commons files under CC BY-SA or GFDL of the categories of the open
                          work_commons_workplaces pack (factories, warehouses, pallets, pallet jacks, conveyors,
                          forklifts, machine shops, car repair shops, cranes, lifts, hard hats, respirators, welders).
    farm_mech_commons_sa  The same for the categories of the open farm_commons_equipment and mech_commons_building
                          packs (tractors, combines, balers, silos, grain elevators, barns, milking parlours; furnaces,
                          boilers, condensers, ducts, well pumps, septic tanks, electrical panels, meters, propane
                          tanks, chimneys, radiators). Captions CC0.

Needing sign-up (WORK_FARM_MECH_SIGN_UP has the links and the free key or secret each needs) and looked at but not
included (WORK_FARM_MECH_NOT_INCLUDED, with the reason and the terms line of each).

WORK_FARM_MECH_PICTURE_MAKING_OK: farm_mech_commons_sa (no people by their words). Not work_commons_sa (workers).

    python -c "import sources, work_farm_mech_sources"      (from the kit folder: checks the file loads)
"""

import os
import re

from extra_sources import say
from home_sources import commons_sa_items
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS
from sources import Source

WHAT_Q = "What is this?"
MACHINE_Q = "What kind of machine is this?"
PLACE_Q = "What kind of place is this?"
DOING_Q = "What is happening here?"

# As in packs/work_farm_mech_packs.py: files left out by their words.
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|bathing suits?|underwear|lingerie|nude|naked|topless|sexy|sexual\w*|"
                       r"erotic\w*)\b", re.I)
HARM = re.compile(r"\b(injur\w*|wounded|casualt\w*|dead|deaths?|died|killed|bod(y|ies)|blood\w*|corpses?|victims?|"
                  r"fatal\w*|accidents?|crash\w*|collapsed?|explosions?|exploded|wreck\w*|rollover|overturned)\b",
                  re.I)
NOT_MODERN = re.compile(r"\b(18\d\d|19[0-8]\d)s?\b|\b(19)?[2-8]0s\b|\b(museum|antique|vintage|historic(al)?|"
                        r"restored|replica|circa|c\. ?19|NARA|Library of Congress|Brady|Hine|Farm Security "
                        r"Administration|Civil War|Negro\w*)\b", re.I)
PERSON = re.compile(r"\b(man|men|woman|women|person|people|persons|boy|boys|girl|girls|users?|worker\w*|operator\w*|"
                    r"farmers?|selfie|portraits?|wearing|holding|he|she|his|her|him|they are|family|families|crowd\w*|"
                    r"dr|mr|mrs|ms)\b", re.I)

# (category, question, answer, also its subcategories): the categories of packs/work_farm_mech_packs.py.
WORK_SA = [
    ("Factories in the United States", PLACE_Q, "This is a factory in the USA.", True),
    ("Factories in Canada", PLACE_Q, "This is a factory in Canada.", True),
    ("Warehouses in the United States", PLACE_Q, "This is a warehouse in the USA.", True),
    ("Warehouses in Canada", PLACE_Q, "This is a warehouse in Canada.", True),
    ("Machine shops", PLACE_Q, "This is a machine shop, where metal parts are made on machine tools.", True),
    ("Automobile repair shops in the United States", PLACE_Q, "This is a car repair shop (garage) in the USA.", True),
    ("Tire shops", PLACE_Q, "This is a tire shop.", False),
    ("Forklifts in the United States", MACHINE_Q, "This is a forklift.", True),
    ("Pallet jacks", WHAT_Q, "This is a pallet jack (pallet truck).", True),
    ("Pallets", WHAT_Q, "These are pallets.", True),
    ("Pallet racking", WHAT_Q, "This is pallet racking: tall steel shelving for pallets.", False),
    ("Conveyor belts", MACHINE_Q, "This is a conveyor belt.", True),
    ("Roller conveyors", MACHINE_Q, "This is a roller conveyor.", False),
    ("Hand trucks", WHAT_Q, "This is a hand truck (dolly).", True),
    ("Overhead cranes", MACHINE_Q, "This is an overhead crane (bridge crane).", True),
    ("Scissor lifts", MACHINE_Q, "This is a scissor lift.", True),
    ("Skid-steer loaders", MACHINE_Q, "This is a skid-steer loader.", True),
    ("Milling machines", MACHINE_Q, "This is a milling machine.", True),
    ("Drill presses", MACHINE_Q, "This is a drill press.", True),
    ("Welders", DOING_Q, "Someone is welding.", True),
    ("Hard hats", WHAT_Q, "This is a hard hat (safety helmet).", True),
    ("Respirators", WHAT_Q, "This is a respirator mask.", True),
]
FARM_MECH_SA = [
    ("Tractors in the United States by state", MACHINE_Q, "This is a tractor.", True),
    ("Tractors in Canada", MACHINE_Q, "This is a tractor.", True),
    ("Combine harvesters in the United States", MACHINE_Q, "This is a combine harvester.", False),
    ("Round balers", MACHINE_Q, "This is a round baler.", True),
    ("Square balers", MACHINE_Q, "This is a square baler.", True),
    ("Field sprayers", MACHINE_Q, "This is a field sprayer.", True),
    ("Cultivators", MACHINE_Q, "This is a cultivator.", True),
    ("Manure spreaders", MACHINE_Q, "This is a manure spreader.", True),
    ("Hay rakes", MACHINE_Q, "This is a hay rake.", True),
    ("Grain dryers", WHAT_Q, "This is a grain dryer.", True),
    ("Silos in the United States", WHAT_Q, "This is a farm silo.", True),
    ("Silos in Canada", WHAT_Q, "This is a farm silo.", True),
    ("Grain elevators in Saskatchewan", WHAT_Q, "This is a prairie grain elevator in Saskatchewan, Canada.", True),
    ("Grain elevators in Alberta", WHAT_Q, "This is a prairie grain elevator in Alberta, Canada.", True),
    ("Barns in Ontario", PLACE_Q, "This is a barn in Ontario, Canada.", True),
    ("Barns in Quebec", PLACE_Q, "This is a barn in Quebec, Canada.", True),
    ("Barns in the United States by state", PLACE_Q, "This is a barn.", True),
    ("Milking parlours", PLACE_Q, "This is a milking parlor, where cows are milked by machine.", True),
    ("Dairy farms in Wisconsin", PLACE_Q, "This is a dairy farm in Wisconsin, USA.", True),
    ("Center pivot irrigation in the United States", WHAT_Q, "This is center-pivot irrigation.", True),
    ("Greenhouses in the United States", PLACE_Q, "This is a greenhouse in the USA.", True),
    ("Gas furnaces", WHAT_Q, "This is a gas furnace.", True),
    ("Heating boilers", WHAT_Q, "This is a heating boiler.", True),
    ("Air conditioners in the United States", WHAT_Q, "This is an air conditioner in the USA.", True),
    ("Air handling units", WHAT_Q, "This is an air handler (air handling unit).", False),
    ("Ductwork", WHAT_Q, "This is ductwork: metal ducts that carry heated or cooled air.", True),
    ("Exhaust fans", WHAT_Q, "This is an exhaust fan.", True),
    ("Well pumps", WHAT_Q, "This is a well pump.", True),
    ("Water softeners", WHAT_Q, "This is a water softener.", False),
    ("Septic tanks", WHAT_Q, "This is a septic tank.", False),
    ("Distribution boards", WHAT_Q, "This is an electrical panel (breaker box).", True),
    ("Fuse boxes", WHAT_Q, "This is a fuse box.", True),
    ("Smart meters", WHAT_Q, "This is a smart electricity meter.", True),
    ("Gas meters", WHAT_Q, "This is a gas meter.", True),
    ("Liquefied petroleum gas tanks", WHAT_Q, "This is a propane (LPG) tank.", True),
    ("Chimneys in the United States", WHAT_Q, "This is a chimney.", True),
    ("Cast iron radiators", WHAT_Q, "This is a cast-iron heating radiator.", False),
    ("Wood-burning stoves", WHAT_Q, "This is a wood-burning stove.", True),
    ("Boiler rooms", PLACE_Q, "This is a boiler room.", True),
]


def sa_items(specs, cap, test, prefix, people_ok):
    """home_sources.commons_sa_items (files under CC BY-SA or GFDL, the categories sharing the cap, children left
    out), without the files whose words name nudity, an injury or accident, an old or museum machine, or (unless
    people_ok) a person: every row of such a file goes."""
    items = commons_sa_items(specs, cap, test, prefix, adults_only=True)
    bad = set()
    for name, _, row in items:
        words = f"{name} {row['answer']}"
        if NOT_SHOWN.search(words) or HARM.search(words) or NOT_MODERN.search(words) or CHILD_WORDS.search(words) \
                or (not people_ok and PERSON.search(words)):
            bad.add(name)
    if bad:
        say(f"  {len(bad)} files left out by their words")
    return [i for i in items if i[0] not in bad]


def prepare_work_commons_sa(source, data_dir, work, cap):
    """Commons workplace categories, files under CC BY-SA or GFDL (workers kept: describing only)."""
    items = sa_items(WORK_SA, cap, source.test, "work-sa", people_ok=True)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_farm_mech_commons_sa(source, data_dir, work, cap):
    """Commons farm and building mechanical categories, files under CC BY-SA or GFDL, files naming a person left
    out."""
    items = sa_items(FARM_MECH_SA, cap, source.test, "farm-mech-sa", people_ok=False)
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
WORK_FARM_MECH_SOURCES = [
    Source("work_commons_sa", "Wikimedia Commons: US and Canadian workplaces, warehouses, forklifts, pallet jacks, "
                              "conveyors, machine shops and safety equipment, files under CC BY-SA or GFDL "
                              "(share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1200, 20, prepare_work_commons_sa, "about 200 MB of pictures", terms=SA_TERMS,
           terms_summary=SA_SUMMARY),
    Source("farm_mech_commons_sa", "Wikimedia Commons: tractors, combines, silos, barns and milking parlours, and "
                                   "furnaces, boilers, ducts, well pumps, electrical panels and propane tanks, files "
                                   "under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2000, 20, prepare_farm_mech_commons_sa, "about 300 MB of pictures", terms=SA_TERMS,
           terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: farm machines and building equipment (no people by their
# words). Not the workplace entry (workers at work).
WORK_FARM_MECH_PICTURE_MAKING_OK = {"farm_mech_commons_sa"}

WORK_FARM_MECH_SIGN_UP = {
    "Flickr API: USDA, NRCS state offices, DOE, EPA, OSHA and DOL photostreams":
        "https://www.flickr.com/services/apps/create/ : a free API key (it would come from a GitHub secret such as "
        "FLICKR_API_KEY), but Flickr's API terms (https://www.flickr.com/services/api/tos/) say you shall not "
        "'Cache or store any Flickr user photos other than for reasonable periods in order to provide the service "
        "you are providing to Flickr users', which a training pack does. No Flickr builder was made; the NRCS and "
        "USDA photos come from their Commons copies (farm_usda_nrcs, commons_us_agencies).",
    "NREL Image Gallery (US Department of Energy; heat pumps, building energy, farms with solar)":
        "https://images.nrel.gov : 'Downloading or copying any gallery content counts as accepting' the Image "
        "Gallery User Agreement (https://www.nrel.gov/news/image-gallery-user-agreement), which the operator 'can "
        "change ... without notice'; credit 'Photo by <name>, NREL <number>'. Neither nrel.gov nor images.nrel.gov "
        "could be reached from the machine these entries were made on, so the agreement's limits on use were not "
        "read. Read it, and if it allows training and keeping copies, add a pack.",
    "Kaggle and Roboflow sets (forklift, PPE, tractor, HVAC-unit detection)":
        "https://www.kaggle.com and https://universe.roboflow.com : an account; check each set's licence and where "
        "its photos came from (many are scraped from the web).",
}

WORK_FARM_MECH_NOT_INCLUDED = {
    "Ingenium (Canada Science and Technology Museum, Canada Agriculture and Food Museum) collection portal":
        "its robots.txt (https://collection.ingeniumcanada.org/robots.txt) says 'Content-Signal: search=yes,"
        "ai-train=no,use=reference', an express reservation of the right to train AI; its images are each CC0 or "
        "CC BY-NC-ND ('Images marked CC BY-NC-ND may not be used for commercial purposes without Ingenium's express "
        "written permission'). The older open data set (Open Government Licence - Canada, open.canada.ca 'Artifact "
        "Collection - CSTMC', source.techno-science.ca) did not answer (503). Ask Ingenium for permission; most of "
        "its farm machines are historic anyway.",
    "OSHA and NIOSH": "no photo gallery of their own; the Department of Labor says 'Some content - including both "
                      "images and text - may be the copyrighted property of others' "
                      "(https://www.dol.gov/general/aboutdol/copyright). Their Commons categories are already used "
                      "by events_safety_packs (safety_training, commons_safety_photos).",
    "Agriculture and Agri-Food Canada, Natural Resources Canada (Commons categories)":
        "only a few dozen files, mostly logos, buildings and officials; not enough for a pack. "
        "agriculture.canada.ca has no open photo library (its pages are under the Government of Canada's terms, "
        "'Crown copyright', reproduction 'for non-commercial purposes' unless stated otherwise).",
    "Library and Archives Canada": "almost all historic (before 1990); this collection is about today's equipment.",
    "The Henry Ford (Benson Ford Research Center)": "www.henryford.org did not answer from this machine; its "
                                                    "pictures are for personal and educational use with its "
                                                    "permission, and its farm and factory objects are historic.",
    "Museums Victoria (Australia)": "refused this machine (403), as before (device_sources.py); and not North "
                                    "American.",
    "ENERGY STAR and Energy.gov": "product and programme data, few photos of their own; the photos on energy.gov are "
                                  "mostly credited to others (stock) and not marked as government work.",
    "Smithsonian NMAH agriculture and industry objects": "CC0, but historic objects (plows, early tractors, mill "
                                                         "machines); this collection is about today's equipment "
                                                         "(device_packs.nmah_devices already reads NMAH).",
    "Commons categories already used by other packs":
        "Tractors, Combine harvesters, Balers, Seed drills, Greenhouses, Center pivot irrigation, Grain silos, "
        "Grain elevators, Milking machines, Cattle feedlots, Factories, Warehouses, Forklifts, Welding, Workshops, "
        "Lathes (land_industry_packs); Water heating devices, Tankless water heaters, Air conditioners, Heat pumps, "
        "Air source heat pumps, Split type air conditioners, Sheet metal and finned-tube radiators, Automobile "
        "repair shops (mechanical_packs); Engine-generators, Humidifiers, Dehumidifiers (device_packs); "
        "Thermostats (home_packs, us_modern_packs); Personal protective equipment, High-visibility clothing "
        "(events_safety_packs). Not repeated.",
    "Commons categories for range hoods, attic and whole-house fans, HRV/ERV, pressure tanks, standby generators, "
    "heating-oil tanks, propane tanks by that name, weatherheads, drain fields, furnaces in general, mini-splits, "
    "grain bins, planters, livestock trailers, loading docks, safety glasses, hearing protection":
        "Commons has no such categories, an empty redirect, or one with a single file (looked up in November 2026); "
        "the nearest ones are used (Gas furnaces, Exhaust fans, Expansion tanks, Liquefied petroleum gas tanks, Oil "
        "tanks, Service drops, Septic systems, Grain storage, Field sprayers). Seed drills (planters) are already "
        "in commons_land_industry.",
}
