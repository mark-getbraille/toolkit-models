"""PRACTICAL LIFE collections for the Picture Model Training Kit (the owner's request of 2026-11-22): driving and road
rules, computer and phone basics, cleaning and household management, knots and outdoor skills, pool equipment, and
motorcycles, RVs and trailers. This file lists:
  - the ready-made packs built in packs/driving_packs.py, computer_basics_packs.py, household_packs.py,
    knots_outdoor_packs.py, pools_spas_packs.py and motorcycles_rvs_packs.py (group "permissive"; the kit downloads
    them with prepare_pack);
  - one share-alike collection, knots_commons_sa: knot diagrams and photos of the same Commons knot categories under
    CC BY-SA or GFDL (only with the share-alike choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at for these subjects and left out, with the reason (PRACTICAL_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the
kit on the user's own computer, straight from where its makers publish it (the packs from the kit's own release),
only when the user ticks the matching choice. Every licence was checked at its source in November 2026.

Answers say only what the source's own labels say (a Commons category's name, a label people checked), and the
answers end with the safety notes that fit: seat belts and never driving impaired, school buses and pedestrians,
never mixing cleaners or pool chemicals, drowning prevention, rope and sharp tools, towing, RV propane and carbon
monoxide, and motorcycle helmets. The notes are the same words as the packs' (packs/test_practical.py checks).

Picture-making (PRACTICAL_PICTURE_MAKING_OK): only the collections of things (computer parts, cleaning tools, knots,
outdoor tools, pool equipment, trailers and RVs); sources.py puts every other key in NOT_FOR_PICTURE_MAKING (the
driving, motorcycle and Open Images collections show people, children among them).
Topics: driving, computers, motorcycles, RVs and trailers in the machines topic; cleaning, pools, knots and outdoor
tools in the home topic.

    python -c "import sources, practical_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

# ----------------------------------------------------------------- the safety notes, word for word as in the packs

DRIVE_NOTE = ("Driving safety: everyone buckles up, the phone stays put away, and never drive after drinking or "
              "using drugs or when drowsy; your state's or province's driver handbook has the rules of the road.")
SCHOOL_BUS_NOTE = ("School buses: when a school bus stops with its red lights flashing and its stop arm out, traffic "
                   "must stop and wait until the lights stop flashing; your state's driver handbook says when "
                   "traffic going the other way must stop too.")
PEDESTRIAN_NOTE = ("Pedestrians: drivers must yield to people in crosswalks; a person with a white cane or a guide "
                   "dog is blind or has low vision, and drivers must stop for them.")
PASSENGER_NOTE = ("Passengers: buckle up, and before getting in, confirm the vehicle and the driver (a rideshare app "
                  "or the dispatcher gives the driver's name and the plate number).")
TECH_NOTE = ("Computer help: when something stops working, restart it first; keep the system and apps updated; back "
             "up your files; and download programs and apps only from the maker's own site or the official app "
             "store.")
MIX_NOTE = ("Cleaning safety: never mix cleaning products; bleach mixed with ammonia, or with acids such as some "
            "toilet bowl and rust cleaners or vinegar, makes poisonous gas. Use one product at a time with fresh air, "
            "follow the label, and keep cleaners away from children. Poison Control: 1-800-222-1222 in the US.")
ROPE_NOTE = ("Rope safety: a knot weakens a rope, and some knots slip or jam; for climbing, lifting or rescue use "
             "rated gear and learn the knot from a qualified instructor, and check a rope for cuts, wear and "
             "stiffness before trusting it.")
TOOL_NOTE = ("Sharp tools: cut away from your body, keep people at least two tool lengths away, wear eye protection "
             "and sturdy boots, and keep the blade covered when it is not in use.")
DROWNING_NOTE = ("Drowning prevention: never leave children alone in or near water, even for a moment; fence a pool "
                 "on all four sides with a self-closing, self-latching gate; keep drain covers in place so no one is "
                 "trapped by the suction; and learn CPR.")
POOL_CHEM_NOTE = ("Keep pool chemicals dry, closed and away from children. Never mix different pool chemicals, and "
                  "add the chemical to water, never water to the chemical: they can catch fire or give off toxic gas.")
TOW_NOTE = ("Towing safety: match the hitch, ball and coupler ratings to the loaded trailer's weight; keep the "
            "tongue weight at about 10 to 15 percent of the trailer's weight; cross the safety chains under the "
            "tongue; connect and check the lights and the breakaway brake before every trip; and drive slower, "
            "leaving more room to stop.")
RV_NOTE = ("RV safety: keep working smoke, carbon monoxide and propane alarms; turn the propane off while driving "
           "and refuelling; and never run a generator where its exhaust can drift into a window, vent or door.")
MOTO_NOTE = ("Motorcycle safety: wear a DOT-approved helmet (it meets the US standard FMVSS 218), eye protection, "
             "and a protective jacket, gloves, trousers and boots; take a rider course and hold the motorcycle "
             "licence or endorsement your state requires.")
NOTE_NAMES = ("DRIVE_NOTE", "SCHOOL_BUS_NOTE", "PEDESTRIAN_NOTE", "PASSENGER_NOTE", "TECH_NOTE", "MIX_NOTE",
              "ROPE_NOTE", "TOOL_NOTE", "DROWNING_NOTE", "POOL_CHEM_NOTE", "TOW_NOTE", "RV_NOTE", "MOTO_NOTE")

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


def knot(category, words, notes=""):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "What knot is this?" "This is ..."."""
    return (category, "What knot is this?", f"This is {words}." + (f" {notes}" if notes else ""), False)


# The knot categories of packs/knots_outdoor_packs.py most drawn in share-alike diagrams (the same answers).
KNOTS_SA = [
    knot("Bowlines", "a bowline, a fixed loop at the end of a rope that does not slip and is easy to untie",
         ROPE_NOTE),
    knot("Clove hitches", "a clove hitch, two turns round a post or rail; quick to tie, but it can slip if the pull "
                          "changes direction"),
    knot("Square knots", "a square knot (reef knot), which ties the two ends of one cord round a bundle; it is not "
                         "safe for joining two ropes that will carry weight"),
    knot("Sheet bends", "a sheet bend, which joins two ropes, even of different thickness"),
    knot("Figure-eight knots", "a figure-eight knot, a stopper knot that keeps a rope's end from running through a "
                               "hole or pulley"),
    knot("Figure-eight loops", "a figure-eight loop (figure eight on a bight), a strong fixed loop used in climbing",
         ROPE_NOTE),
    knot("Trucker's hitches", "a trucker's hitch, which pulls a rope tight with a loop that works like a pulley, used "
                              "for tying down loads", ROPE_NOTE),
    knot("Timber hitches", "a timber hitch, for dragging or lifting a log or pole"),
    knot("Prusik knots", "a Prusik knot, a loop of cord wrapped round a rope that grips when loaded and slides when "
                         "not, used in climbing and rescue", ROPE_NOTE),
    knot("Alpine butterfly knots", "an alpine butterfly, a fixed loop in the middle of a rope that can be pulled in "
                                   "any direction", ROPE_NOTE),
    knot("Eye splices", "an eye splice, a lasting loop made by weaving a rope's strands back into itself"),
    knot("Carrick bends", "a carrick bend, which joins two heavy ropes"),
]


def prepare_knots_commons_sa(source, data_dir, work, cap):
    """Commons knot categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(KNOTS_SA, cap, source.test, "knots-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def pack(key, name, cap, test, size, licence=COMMONS_OPEN, credit=COMMONS_CREDIT):
    """A ready-made pack's Source (group "permissive", downloaded with prepare_pack)."""
    return Source(key, name, licence, credit, "permissive", cap, test, prepare_pack, size)


def oi_pack(key, name, cap, test, size):
    """A ready-made Open Images pack's Source."""
    return pack(key, name, cap, test, size, OI_OPEN, OI_CREDIT)


# ----------------------------------------------------------------- the table

PRACTICAL_SOURCES = [
    # driving and road rules
    pack("commons_driving", "Driving: steering wheels, driver's seats, ignition switches, pedals, gear sticks, cruise "
                            "control, seat belts, learner signs and driving schools, road markings, roundabouts, "
                            "rumble strips, speed bumps, ramp meters, school buses, crossing guards, paratransit and "
                            "accessible taxis, with driving safety notes (Wikimedia Commons, ready-made pack)",
         900, 10, "about 200 MB"),
    oi_pack("open_images_driving", "Driving: steering parts, car pedals, seat belts, lanes, road shoulders, dirt roads, "
                                   "traffic circles, traffic jams, parking lots and meters (Open Images, ready-made "
                                   "pack)", 1500, 15, "about 300 MB"),
    # computer and phone basics
    pack("commons_computer_basics", "Computer and phone basics: power buttons, touchpads, arrow and function keys, "
                                    "laptop keyboards, numeric keypads, keyboard shortcuts, docking stations, video "
                                    "calls, computer cases, memory cards, SIM cards, ink and toner cartridges "
                                    "(Wikimedia Commons, ready-made pack)", 900, 10, "about 200 MB"),
    oi_pack("open_images_computer_basics", "Floppy disks and drives, Ethernet hubs, mousepads, graphics tablets, "
                                           "tablet chargers and stands, printer supplies (Open Images, ready-made "
                                           "pack)", 500, 5, "about 100 MB"),
    # cleaning and household management
    pack("commons_cleaning_tools", "Cleaning and organising: brooms, dustpans, mops and buckets, sponges, dusters, "
                                   "squeegees, toilet brushes, rubber gloves, spray bottles, dish racks, laundry "
                                   "baskets, lint rollers, storage boxes, closets and pantries, with the never-mix "
                                   "cleaners note (Wikimedia Commons, ready-made pack)", 1000, 10, "about 220 MB"),
    oi_pack("open_images_cleaning", "Dustpans, dusters, squeegees, sponges, cleaning supplies and kitchen towels (Open "
                                    "Images, ready-made pack)", 800, 10, "about 160 MB"),
    # knots and outdoor skills
    pack("commons_knots", "Knots by name: bowline, clove hitch, square knot, sheet bend, figure eight, taut-line and "
                          "trucker's hitches, Prusik, splices, whippings, lashings, seizings and about thirty more, "
                          "with their uses (Wikimedia Commons, ready-made pack)", 1500, 15, "about 250 MB"),
    pack("commons_outdoor_skills", "Outdoor tools: compasses, felling axes and hatchets, crosscut and bow saws, "
                                   "whetstones, knife sharpeners, bivouac shelters, marlinespikes, fids and rope "
                                   "making, with sharp-tool notes "
                                   "(Wikimedia Commons, ready-made pack)", 700, 10, "about 150 MB"),
    oi_pack("open_images_knots_outdoor", "Wire rope, carabiners, tarps, bow and crosscut saws, hatchets and sharpening "
                                         "stones (Open Images, ready-made pack)", 800, 10, "about 160 MB"),
    # pools and spas
    pack("commons_pool_equipment", "Pool equipment: pumps, sand filters, pool cleaners and robots, covers, ladders and "
                                   "rescue hooks, with drowning-prevention and pool chemical notes; equipment only "
                                   "(Wikimedia Commons, ready-made pack)", 250, 5, "about 60 MB"),
    # motorcycles, RVs and trailers
    pack("commons_trailers_rvs", "Trailers and RVs: trailer couplings, tow bars, travel and teardrop trailers, truck "
                                 "campers, campervans, RVs, RV parks and dump stations, with towing and RV safety notes "
                                 "(Wikimedia Commons, ready-made pack)", 900, 10, "about 200 MB"),
    pack("commons_motorcycle_gear", "Motorcycle gear: handlebars, mirrors, lights, helmets, protective clothing, gloves "
                                    "and boots, rider training and sidecars, with helmet notes (Wikimedia Commons, "
                                    "ready-made pack)", 900, 10, "about 200 MB"),
    oi_pack("open_images_motorcycles_rvs", "RVs, travel trailers, caravans and trailers, cruiser and enduro "
                                           "motorcycles, mopeds and motor scooters, helmets and protective gear (Open "
                                           "Images, ready-made pack)", 1500, 15, "about 300 MB"),
    # share-alike
    Source("knots_commons_sa", "Wikimedia Commons: knot diagrams and photos (bowline, clove hitch, square knot, sheet "
                               "bend, figure eight, trucker's hitch, Prusik, splices), files under CC BY-SA or GFDL "
                               "(share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 10, prepare_knots_commons_sa, "about 60 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: things only. Never the driving, motorcycle or Open Images
# collections, which show people (children among them).
PRACTICAL_PICTURE_MAKING_OK = {"commons_computer_basics", "commons_cleaning_tools", "commons_knots",
                               "commons_outdoor_skills", "commons_pool_equipment", "commons_trailers_rvs",
                               "knots_commons_sa"}

# The topic each collection belongs to (topics.py lists the same keys; packs/test_practical.py checks).
PRACTICAL_TOPICS = {
    "machines": ("commons_driving", "open_images_driving", "commons_computer_basics", "open_images_computer_basics",
                 "commons_trailers_rvs", "commons_motorcycle_gear", "open_images_motorcycles_rvs"),
    "home": ("commons_cleaning_tools", "open_images_cleaning", "commons_knots", "commons_outdoor_skills",
             "open_images_knots_outdoor", "commons_pool_equipment", "knots_commons_sa"),
}

PRACTICAL_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Child safety seats (baby_packs), Vacuum cleaners, Robotic "
        "vacuum cleaners and Window cleaning, Motorhomes (culture_packs), Motorcycle tires, chains and dashboards "
        "(mechanical_packs), USB flash drives, Desktop computers, Tablet computers, Webcams and Modems "
        "(things_packs), Computer and Smart speakers, Splitting mauls, Wheel chocks and Horse trailers: not asked "
        "twice. The first level of Commons Knots and Ropes is the hardware pack's, so the knots are taken by name.",
    "Commons categories that do not exist under the names tried (November 2026)": "Car pedals, Turn signal levers, "
        "Handbrakes, Parking brakes, Road surface markings, School bus stop arms, L-plates, Warning triangles, Enter, "
        "Escape and Windows keys, Power symbols, USB ports, Wi-Fi routers, Tango icons, Sponges (cleaning), Steam "
        "mops, Microfiber cloths, Orienteering compasses, Ferrocerium rods, Paracord, Kernmantle ropes, Pool pumps, "
        "Pool skimmers, Pool filters, Pool fences, Pool drains, Chlorinators, Tow hitches, Tow balls, Fifth wheel "
        "couplings, Gooseneck hitches, Trailer connectors, Safety chains, Weight distribution hitches, Pop-up "
        "campers, Dump stations, RV hookups and Motorcycle controls; Taut-line hitches, Rolling hitches and Half "
        "hitches hold only a few files. The packs use the categories that hold files.",
    "Commons Hot tubs and every swimming category": "the owner's rule for the pool collection is equipment and "
        "chemistry only; hot tub photos often show people in swimwear, so the category is left out, and hot tub "
        "care and safety are in the books (pools-spas).",
    "Hangman's nooses, BDSM knots and Shibari knots on Commons": "left out of the knot pack (not wanted).",
    "Open Images labels asked elsewhere": "Steering wheel, Gear shift, Driving, Broom, Mop, Paper towel, Knot, Hard "
        "disk drive, USB flash drive, USB cable, Ethernet cable, Router, Wireless router, Modem, Smartphone and "
        "Scooter: asked by other packs, never twice. Swimming pool and Jacuzzi are the public places pack's; "
        "Compass is the outings pack's; Axe is the home pack's.",
    "Open Images swimming and pool photos": "they show swimming people; the owner's rule for pools is equipment and "
                                           "chemistry only, so no Open Images pool pack is made.",
    "NEMA TT-30, 14-50 and trailer plug and socket pictures": "the power helper's plug and socket packs cover plug "
                                                            "types; not repeated.",
    "Boat trailers and boating": "the leisure helper's collections cover boating; not repeated.",
    "Makers' product photos (Harley-Davidson, Honda, Airstream, Winnebago, Dometic, Pentair, Hayward and others)":
        "the makers' copyright; not used. Their manuals are links in the manual collections.",
    "Screenshots of programs and phone screens": "the programs' makers own them; commons_screens has the phone "
                                                "screens that are free to use.",
}


def main(argv=None):
    """Prepare the share-alike collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try the knots share-alike collection.")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in PRACTICAL_SOURCES if s.key == "knots_commons_sa")
    source.test, source.cap = 0, args.cap
    data = tempfile.mkdtemp(prefix="knots-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
