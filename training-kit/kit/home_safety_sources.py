"""HOME SAFETY AND CONTROLS, FOOD STATE and PUBLIC ACCESSIBILITY FEATURES for the Picture Model Training Kit: the
collections that cannot be ready-made packs because of their licence, and the ones looked at and left out. The open
ones (Commons breaker panels, fuse boxes, meters, stopcocks, sump pumps, furnaces, alarms and appliance displays with a
stated state, unripe fruit, mould, doneness, USDA food safety photos, braille signage, bus stop signs and ticket
machines) are packs in packs/home_safety_packs.py.

As in street_scene_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit
on the user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.
Every licence was checked at its source in November 2026.

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia).

NEVER GUESS A READING OR A LIGHT STATE: the share-alike entry asks only what a Commons category says (what the thing
is, whether fruit is unripe, whether there is mould), never a reading or a light.

The collections (HOME_SAFETY_SOURCES):
  share-alike
    home_safety_commons_sa  Wikimedia Commons files under CC BY-SA or GFDL of the open packs' new categories
                            (distribution boards, fuse boxes, circuit breakers, gas and smart meters, stopcocks, sump
                            pumps, gas furnaces, green bananas, unripe tomatoes, braille signage, bus stop signs, US
                            ticket machines). Captions CC0.

Looked at but not included (HOME_SAFETY_NOT_INCLUDED, with the reason) and open candidates for a later pack
(HOME_SAFETY_CANDIDATES).

    python kit/home_safety_sources.py home_safety_commons_sa --cap 8      (from the kit folder: a quick check)
"""

import json
import os
import re

from home_sources import commons_sa_items
from more_sources import fetch_shared
from extra_sources import say
from sources import Source

# Words that leave a share-alike file out: fires, injuries and death (these are everyday collections).
HARM = re.compile(r"\b(fires? damage|house fires?|killed|dead|deaths?|died|fatal\w*|injur\w*|wounded|blood\w*|"
                  r"explosions?|electrocut\w*)\b", re.I)

PANEL = ("This is an electrical panel (a breaker box or distribution board): each circuit has its own breaker or "
         "fuse. A breaker that trips again and again, or a warm or buzzing panel, needs an electrician.")
GAS = ("This is a gas meter. If you smell gas, leave at once and call the gas company or 911 from outside; do not "
       "switch anything on or off.")


def spec(category, question, answer, deeper=True):
    """(category, question, answer, also one level of its subcategories) for home_sources.commons_sa_items."""
    return (category, question, answer, deeper)


HOME_SAFETY_SA = [
    spec("Distribution boards", "What is this?", PANEL),
    spec("Fuse boxes", "What is this?", "This is a fuse box: each circuit has a fuse that blows if too much current "
                                        "flows. Replace a blown fuse only with one of the same rating."),
    spec("Circuit breakers", "What is this?", "This is a circuit breaker: a switch that turns itself off (trips) when "
                                              "too much current flows."),
    spec("Gas meters", "What is this?", GAS),
    spec("Smart meters", "What is this?", "This is a smart meter: it measures the electricity (or gas) used and sends "
                                          "the readings to the supplier."),
    spec("Stopcocks", "What is this?", "This is a stopcock (a shut-off valve) on a water pipe: it turns the water "
                                       "off. Know where your main one is before a leak."),
    spec("Sump pumps", "What is this?", "This is a sump pump: it pumps water out of a pit in the basement floor so the "
                                        "basement does not flood.", False),
    spec("Gas furnaces", "What is this?", "This is a gas furnace: it heats air that fans blow through the home's "
                                          "ducts. Change its filter every one to three months."),
    spec("Green bananas", "Is this ripe?", "No: these bananas are green (unripe). They ripen at room temperature in a "
                                           "few days, turning yellow."),
    spec("Unripe tomatoes", "Is this ripe?", "No: this tomato is not ripe yet. It ripens on the counter, out of the "
                                             "fridge.", False),
    spec("Braille signage", "Is there braille here?", "Yes: there is a sign with braille here, raised dots usually "
                                                      "under raised print letters, read by touch."),
    spec("Bus stop signs", "Is there a bus stop here?", "Yes: there is a bus stop sign here, marking where the bus "
                                                        "stops; many list the route numbers."),
    spec("Ticket machines in the United States", "What is this?", "This is a ticket machine (fare machine): choose a "
                                                                  "ticket on its screen or buttons and pay."),
]


def sa_items(specs, cap, test, prefix):
    """home_sources.commons_sa_items (files under CC BY-SA or GFDL, the categories sharing the cap, children left
    out), without the files whose words name a fire, injury or death."""
    items = commons_sa_items(specs, cap, test, prefix, adults_only=True)
    bad = {name for name, _, row in items if HARM.search(f"{name.replace('_', ' ')} {row['answer']}")}
    if bad:
        say(f"  {len(bad)} files left out by their words")
    return [i for i in items if i[0] not in bad]


def prepare_home_safety_commons_sa(source, data_dir, work, cap):
    """Commons home safety, food state and accessibility categories, files under CC BY-SA or GFDL."""
    items = sa_items(HOME_SAFETY_SA, cap, source.test, "homesafe-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
HOME_SAFETY_SOURCES = [
    Source("home_safety_commons_sa", "Wikimedia Commons: breaker panels, fuse boxes, gas and smart meters, shut-off "
                                     "valves, sump pumps, furnaces, unripe bananas and tomatoes, braille signs, bus "
                                     "stop signs and ticket machines, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1000, 15, prepare_home_safety_commons_sa, "about 220 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
]

# The collections a picture-making model may learn from: none (bus stops and stations show people).
HOME_SAFETY_PICTURE_MAKING_OK = set()

HOME_SAFETY_CANDIDATES = {
    "AgRobTomato Dataset: greenhouse tomatoes with different ripeness stages (Zenodo 5596799)":
        "CC BY 4.0 (its Zenodo record), 136 MB. Tomatoes on the vine boxed by ripeness stage; several tomatoes per "
        "photo, so an answer would count them by stage. Open: could be a later pack. Not built in this pass.",
    "OpenField-BD-Tomato-Maturity-Detection Dataset (Zenodo 20176021)":
        "CC BY 4.0 (its Zenodo record), 2.4 GB, open-field tomatoes by maturity. Not built in this pass (size).",
}

HOME_SAFETY_NOT_INCLUDED = {
    "Open Images V7 home and food labels":
        "already the open_images_home and open_images_food packs. Open Images has no label for smoke alarms, meters, "
        "breaker panels, ripeness or doneness, so no new Open Images pack was made.",
    "Commons categories other packs already show (smoke and CO alarms, thermostats, microwave ovens, washing "
    "machines, dishwashers, dryers, ovens, water meters, fire extinguishers, water damage, lift buttons)":
        "used in commons_home_safety and commons_access_features ONLY where the file's own words give a reading, a "
        "light, a gauge, a kind or braille, so the same photo is never asked the same question twice.",
    "Wheelchair ramps, lifts, disabled parking, accessibility signs, tactile paving, crosswalks and pedestrian "
    "signals":
        "already commons_disability and the street scene packs (commons_crosswalks_signals, ptl_crossings).",
    "Banana ripeness papers on Zenodo (11480598, 19656951)":
        "CC BY 4.0, but each record holds only the paper (a PDF), not the photos. Not usable.",
    "Commons categories with no such name (November 2026)":
        "'Smoke alarms', 'Electrical panels', 'Circuit breaker panels', 'Consumer units', 'Water heaters' (no "
        "files), 'Furnace filters', 'HVAC filters', 'Shut-off valves', 'Water leaks', 'Water stains', 'Ripe "
        "bananas', 'Overripe bananas', 'Moldy bread', 'Mouldy bread', 'Moldy cheese', 'Rotten fruit', 'Rare "
        "steaks', 'Braille signs', 'Tactile signs', 'Accessible entrances', 'Platform edges' and 'Ticket vending "
        "machines' do not exist; 'Distribution boards', 'Fuse boxes', 'Stopcocks', 'Green bananas', 'Unripe "
        "tomatoes', 'Braille signage' and 'Bus stop signs' do and are used.",
    "US agency photo sets (CPSC, NIST, FTA, Access Board, FSIS) on Commons":
        "Commons has no 'Images from the Consumer Product Safety Commission' or 'United States Access Board' "
        "category; 'Federal Transit Administration' (72 files) and 'Food Safety and Inspection Service' (91 files) "
        "are mostly logos, officials and buildings, and NIST's 1,124 files are laboratory photos. USDA's Flickr "
        "stream copy (76,000 files) is searched for food safety photos instead (usda_food_safety_photos).",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one home safety collection.")
    parser.add_argument("key", choices=[s.key for s in HOME_SAFETY_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in HOME_SAFETY_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="home-safety-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
