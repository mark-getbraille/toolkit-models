"""Motorcycles, RVs and trailers for the reference library, in the group "Reference, motorcycles, RVs and trailers"
(the owner's request of 2026-11-22). Keys: motorcycles-rvs (every book), rvs:<name>.

What this module builds, in plain words:
  - rvs:index, a guide to the library on motorcycles, RVs and trailers (the toolkit's own facts and links, CC0):
    motorcycle safety and maintenance, RV systems (12-volt and 30/50-amp electrical, fresh water, propane, black and
    grey tanks), RV maintenance and winterising, towing (hitch types and classes, weight distribution, sway control,
    trailer brakes, tongue weight, safety chains), trailer maintenance (bearings, tyres, lights), campgrounds and
    accessibility, and towing laws, with the books by key, the picture packs, the manual collections and the links;
  - IN FULL: the US Army's operator and maintenance manual for the M1101 and M1102 cargo trailers (TM 9-2330-392-13&P,
    2012: coupling, safety chains, lights and the electrical connector, brakes, tyres, wheel bearings, lubrication
    and checks before every trip), read from the Internet Archive under the release rule for military publications;
    and the National Park Service's camping, campground and accessibility pages (a US government work, "generally
    considered in the public domain");
  - one old public-domain book (published before 1931; the builder checks the item's year at every build): J. C.
    Long and John D. Long's Motor Camping (1923), on camping with a car and trailer.
  Every book carries ROAD_SAFETY in its notice (motorcycle helmets and gear, towing ratings, tongue weight, safety
  chains, lights and breakaway checks, RV propane and carbon monoxide).

Already in the library and not repeated: every state's driver, CDL and motorcycle handbook as links
(drive:index_us), the Army's Manual for the Wheeled Vehicle Operator (drive:army_tc_21_305_20: coupling and towing
trailers), the motorcycle, ATV and snowmobile owner's manuals (the manual collection powersports), the old car care
books (car-care), NHTSA vehicle recalls (rcl:), and boats on trailers (the leisure collections).

Not built (NOT_INCLUDED, link-only): NHTSA's towing and motorcycle safety pages (refuse programs; no Internet Archive
copy found), FMCSA (refuses programs), the Motorcycle Safety Foundation's handbooks (copyright), and the makers'
manuals (Harley-Davidson, Honda, Airstream, Winnebago, Dometic and others: links in the manual collection
motorcycles_rvs).

Run from the repository's folder:
  python3 textbooks/motorcycles_rvs.py rvs:army_tm_m1101_trailer --out build/textbooks --limit 3
  python3 textbooks/motorcycles_rvs.py --list motorcycles-rvs
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "rvs"
GROUPS = {GROUP: "Reference, motorcycles, RVs and trailers"}

# The same safety words as packs/motorcycles_rvs_packs.py TOW_NOTE, RV_NOTE and MOTO_NOTE, written for a book.
ROAD_SAFETY = ("Safety: on a motorcycle, wear a DOT-approved helmet (it meets the US standard FMVSS 218), eye "
               "protection and protective clothing, and hold the licence or endorsement your state requires. When "
               "towing, match the hitch, ball and coupler ratings to the loaded trailer's weight, keep the tongue "
               "weight at about 10 to 15 percent of the trailer's weight, cross the safety chains under the tongue, "
               "and check the lights and breakaway brake before every trip. In an RV, keep working smoke, carbon "
               "monoxide and propane alarms, turn the propane off while driving and refuelling, and never run a "
               "generator where its exhaust can drift inside.")

# ====================================================================== the Army trailer manual and the old book

PDFS = [
    K.us_pdf(GROUP, name="army_tm_m1101_trailer", title="Operator's and Maintenance Manual: Trailer, Cargo, High "
             "Mobility, M1101 and M1102 (TM 9-2330-392-13&P, 2012)", subject="Trailers: coupling, brakes, lights "
             "and maintenance", publisher="Headquarters, Department of the Army",
             archive="trl-m-1101-m-1102-tm-9-2330-392-13-p-ltt", military=True, published="2012-12",
             version="TM 9-2330-392-13&P, 2012 (Internet Archive item trl-m-1101-m-1102-tm-9-2330-392-13-p-ltt)",
             description="The Army's operator and maintenance manual for its small cargo trailers: coupling and "
                         "uncoupling, safety chains, the electrical connector and lights, the parking and surge "
                         "brakes, tyres and wheels, wheel bearings and lubrication, the checks to make before, during "
                         "and after every trip, and troubleshooting. Military trailers differ from civilian ones in "
                         "their hitch (a pintle) and connector, but the checks are the same kind.",
             notice=f"A work of the US Army (public domain); the builder says what its own front pages print about "
                    f"distribution. Written for military trailers; civilian towing law is the state's handbook. "
                    f"{ROAD_SAFETY}"),
    X.old_book(GROUP, "long_motor_camping_1923", "Motor Camping (J. C. Long and John D. Long, 1923)",
               "Camping with a car and trailer", "J. C. Long and John D. Long (Dodd, Mead and Company)",
               "motorcamping00longrich", 1923,
               "Camping with a car in the 1920s: planning a trip, tents and camp trailers, beds, stoves and cooking "
               "outfits, packing the car, choosing a campsite and auto camps.",
               "Published in 1923: an old book whose cars, trailers, stoves and fuels are long out of date (never use "
               "a fuel stove or heater inside a tent, car or trailer: carbon monoxide); kept for the history of motor "
               "camping and its planning advice. The machine-read text has the scanner's mistakes."),
]
# The old books carry the safety notice too (after the scan notice).
for _p in PDFS:
    if _p.get("old_public_domain"):
        _p["notice"] = f"{_p['notice']} {ROAD_SAFETY}"

# ====================================================================== National Park Service

NPS = "https://www.nps.gov"
NPS_TERMS = NPS + "/aboutus/disclaimer.htm"
NPS_TEXT = r"material created by the National Park Service and presented on this website, unless otherwise " \
           r"indicated, is generally considered in the public domain"
NPS_PAGES = [NPS + p for p in ("/subjects/camping/index.htm", "/subjects/camping/campground.htm",
                               "/subjects/camping/camping-with-kids.htm", "/subjects/accessibility/index.htm",
                               "/subjects/accessibility/what-we-do.htm")]
GUIDES = [dict(X.page_list_book(
    GROUP, "nps_campgrounds_accessibility", "Campgrounds and accessibility in the national parks (National Park "
    "Service)", "Campgrounds and accessibility", "National Park Service (US Department of the Interior)", NPS_PAGES,
    r"^https://www\.nps\.gov/subjects/(camping|accessibility)/[a-z0-9-]+\.htm$",
    "The National Park Service's pages on camping: the kinds of camping in the parks, campgrounds (reserving a site, "
    "RV and tent sites, hookups and dump stations where the park has them, campground rules), camping with children, "
    "and accessibility in the parks (what the Park Service does for visitors with disabilities and how to find each "
    "park's accessible campsites and trails).",
    f"From the National Park Service: \"material created by the National Park Service ... is generally considered in "
    f"the public domain\"; source: National Park Service (nps.gov). Each park has its own campground rules, vehicle "
    f"length limits and generator hours: check them before you go. {ROAD_SAFETY}",
    content=(r'<div id="main" role="main" class="MainContent">', r'<div id="related_content_position">|<footer\b'),
    units=[(r"accessibility", "Accessibility"), (r".", "Camping and campgrounds")]),
    licence_page=NPS_TERMS, licence_text=NPS_TEXT)]

# ====================================================================== the index

SECTIONS = [
    ("Motorcycles: safety and maintenance", "Helmets and gear, licences and rider training, and looking after a "
                                            "motorcycle.", [
        ("key", "drive:index_us", "Every state's motorcycle operator manual, as links"),
        ("pack", "commons_motorcycle_gear", "Motorcycle handlebars, mirrors, lights, helmets and protective gear"),
        ("pack", "open_images_motorcycles_rvs", "Motorcycle kinds and gear"),
        ("manuals", "powersports", "Motorcycle, scooter, ATV and snowmobile owner's manuals, as links"),
        ("manuals", "motorcycles_rvs", "Motorcycle, RV and trailer makers' manuals and safety guidance, as links"),
        ("link", "NHTSA motorcycle safety", "https://www.nhtsa.gov/road-safety/motorcycle-safety",
         "public domain, but nhtsa.gov refuses programs; open it in a browser"),
        ("link", "Motorcycle Safety Foundation (rider courses and handbooks)", "https://www.msf-usa.org/",
         "the MSF's copyright; open it in a browser")]),
    ("RV systems, maintenance and winterising", "12-volt and 30/50-amp power, fresh water, propane, black and grey "
                                                "tanks, and getting ready for winter.", [
        ("pack", "commons_trailers_rvs", "Travel trailers, truck campers, campervans, RVs, RV parks and dump stations"),
        ("manuals", "motorcycles_rvs", "RV, appliance (Dometic, Norcold, Suburban, Atwood) and generator manuals, as "
                                       "links")]),
    ("Towing and trailers", "Hitch types and classes, weight distribution, sway control, trailer brakes, tongue "
                            "weight, safety chains, bearings, tyres and lights.", [
        ("key", "rvs:army_tm_m1101_trailer", "The Army's trailer manual: coupling, chains, lights, brakes, bearings "
                                             "and checks"),
        ("key", "drive:army_tc_21_305_20", "The Army's driver manual: coupling and towing trailers"),
        ("pack", "commons_trailers_rvs", "Trailer couplings and tow bars"),
        ("link", "NHTSA: Towing a Trailer, Being Equipped for Safety", "https://www.nhtsa.gov/",
         "public domain, but nhtsa.gov refuses programs and no Internet Archive copy was found")]),
    ("Campgrounds and accessibility", "Finding campgrounds, hookups and accessible sites.", [
        ("key", "rvs:nps_campgrounds_accessibility", "Campgrounds and accessibility (National Park Service)"),
        ("key", "rvs:long_motor_camping_1923", "Motor Camping (1923): the history of camping by car"),
        ("link", "Recreation.gov (reserving federal campgrounds)", "https://www.recreation.gov/",
         "a booking site; open it in a browser")]),
    ("Towing laws", "Trailer brakes, lights, mirrors and speed limits differ by state.", [
        ("key", "drive:index_us", "Every state's driver handbook, as links (towing rules are in each)")]),
]
INDEX = X.index_maker("rvs", GROUP, "Motorcycles, RVs and trailers: a guide to the library",
                      "Motorcycles, RVs and trailers",
                      "A guide to the library on motorcycles, RVs and trailers: motorcycle safety and maintenance, RV "
                      "systems and winterising, towing and trailers, campgrounds and accessibility, and towing laws.",
                      SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("rvs", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"motorcycles-rvs": lambda: ["rvs:index"] + [f"rvs:{g['name']}"
                                                                             for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "rvs_army": "TM 9-2330-392-13&P (2012): a work of the US Army, read from the Internet Archive because "
                "armypubs.army.mil shuts out automated readers; the builder reads its front pages and follows the "
                "shared release rule (military_release.py).",
    "rvs_nps": "www.nps.gov/aboutus/disclaimer.htm (checked at every build): NPS material \"is generally considered in "
               "the public domain\", credited in the notice; NPS's robots.txt asks 5 seconds between pages, which the "
               "builder keeps (checked 2026-11-22).",
    "rvs_old_book": "Motor Camping (1923): Internet Archive item motorcamping00longrich, its metadata \"date\" before "
                    "1931 (checked at every build).",
    "rvs_index": "The index (rvs:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("NHTSA's \"Towing a Trailer: Being Equipped for Safety\" and its motorcycle safety pages", "Public domain, but "
     "www.nhtsa.gov refuses programs (\"403\", robots.txt included, 2026-11-22), and no Internet Archive copy was "
     "found (searched 2026-11-22: towing a trailer, DOT HS towing, NHTSA motorcycle). The Army's driver and trailer "
     "manuals cover coupling, chains, lights and checks. Index: https://www.nhtsa.gov/road-safety/motorcycle-safety"),
    ("FMCSA towing and cargo securement rules", "Public domain, but www.fmcsa.dot.gov refuses programs (\"403\"); the "
     "federal rules themselves are in the library's US Code and CFR books. Index: https://www.fmcsa.dot.gov/"),
    ("Motorcycle Safety Foundation handbooks and the Basic RiderCourse", "Copyright of the MSF; link-only. Every "
     "state's "
     "motorcycle operator manual is listed in drive:index_us. Index: https://www.msf-usa.org/"),
    ("Makers' manuals (Harley-Davidson, Honda, Yamaha, Airstream, Winnebago, Thor, Forest River, Dometic, Norcold, "
     "Suburban, Atwood, Curt, B&W, Equal-i-zer and others)", "The makers' copyright; links in the manual collection "
     "motorcycles_rvs. Index: https://www.airstream.com/owners/"),
    ("Older US Army trailer manuals (M101, M103, M105, M116)", "On the Internet Archive too, but they repeat the same "
     "checks for older trailers; the newest (M1101, 2012) is built. Index: https://archive.org/details/"
     "trl-1-ton-m-116-tm-9-2330-202-14-p-m-116-14-p"),
    ("Old motorcycle books (before 1931)", "None with a text layer was found on the Internet Archive except magazines "
     "and catalogues (searched 2026-11-22); motorcycles of that age share little with today's. Index: "
     "https://archive.org/search?query=motorcycle+1915"),
    ("Boats on trailers, launching and boating safety", "The leisure collections cover boating; not repeated. Index: "
     "https://www.uscgboating.org/"),
    ("NEMA TT-30 and 14-50 RV plugs and their wiring", "The power collections cover plug types; not repeated. Index: "
     "https://www.nema.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
