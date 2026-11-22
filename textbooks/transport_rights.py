"""Transport rights and accessible transport for the reference library (the owner's request of 2026-11-22). Keys:
transport (every book), travel:<name>.

What this module builds, in plain words, each IN FULL, from the US Access Board (a federal agency; its guides say
"This guide is in the public domain, and users are free to distribute and share its content"):
  - the Guide to the ADA Accessibility Standards: every chapter (using the standards, new construction and
    alterations, floor surfaces, protruding objects and operable parts, accessible routes, doors, ramps,
    elevators, means of egress, parking and passenger loading zones, stairways, toilet and bathing rooms,
    signs (raised characters and braille), and recreation facilities);
  - the ADA Accessibility Guidelines for Transportation Vehicles (buses, vans, rail cars, over-the-road buses,
    trams), every subpart, with the advisory guidance and the guides to the update for buses and vans;
  - the Public Right-of-Way Accessibility Guidelines (PROWAG: sidewalks, crossings, accessible pedestrian signals,
    detectable warnings, transit stops), every page.

The Air Carrier Access Act rule itself (14 CFR part 382) is already in the library (law:cfr_14_382_air_travel_
disability). The Department of Transportation's aviation consumer guides (including "passengers with
disabilities"), the Federal Transit Administration's ADA guidance and TSA Cares answer programs "403" or "Access
Denied": link-only in NOT_INCLUDED.

Licence: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build). access-board.gov's robots.txt allows the pages; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/transport_rights.py travel:access_board_ada_guide --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "disability"
AB = "https://www.access-board.gov"
AB_NOTICE = ("A work of the US Access Board (public domain: \"users are free to distribute and share its content\"). "
             "The guides explain the standards; the enforceable rules are the Department of Justice's and the "
             "Department of Transportation's regulations.")
PUBLISHER = "US Access Board"

GUIDES = [
    K.guide(GROUP, "access_board_ada_guide", "Guide to the ADA Accessibility Standards (US Access Board)",
            "Accessible buildings and sites (ADA standards)", PUBLISHER, f"{AB}/ada/guides/",
            r"^https://www\.access-board\.gov/ada/guides/[a-z0-9-]+/?$",
            "The Access Board's whole guide to the 2010 ADA Standards, chapter by chapter: using the standards, new "
            "construction and alterations, floor and ground surfaces, clear floor space, operable parts and "
            "protruding objects, accessible routes, entrances and doors, ramps and curb ramps, elevators and lifts, "
            "means of egress, parking, passenger loading zones and stairways, toilet and bathing rooms, signs "
            "(tactile characters and braille), the International Symbol of Accessibility, and recreation facilities "
            "(play areas, pools, sports, boating, fishing, golf and amusement rides).", AB_NOTICE,
            units=[(r"chapter-1-", "Chapter 1: Using the ADA Standards"),
                   (r"chapter-2-", "Chapter 2: Application and scoping"),
                   (r"chapter-3-", "Chapter 3: Building blocks"), (r"chapter-4-", "Chapter 4: Accessible routes"),
                   (r"chapter-5-", "Chapter 5: General site and building elements"),
                   (r"chapter-6-", "Chapter 6: Plumbing elements and facilities"),
                   (r"chapter-7-", "Chapter 7: Communication elements"),
                   (r"chapter-10-", "Chapter 10: Recreation facilities"), (r".", "About the guide")], limit=80),
    K.guide(GROUP, "access_board_vehicles", "ADA Accessibility Guidelines for Transportation Vehicles (US Access Board)",
            "Accessible transport vehicles", PUBLISHER, f"{AB}/ada/vehicles/",
            r"^https://www\.access-board\.gov/ada/vehicles/([a-z0-9-]+/)*$",
            "The Access Board's guidelines for accessible buses, vans, rail cars (rapid, light, commuter and "
            "intercity rail), over-the-road buses, automated guideway systems, trams and other vehicles: every "
            "subpart, the appendix of advisory guidance, and the guides to the updated guidelines for buses and "
            "vans (lifts and ramps, securement, signs and stop announcements, public information systems).",
            AB_NOTICE, depth=2, follow=r"^https://www\.access-board\.gov/ada/vehicles/(guides|update)/?$", limit=60),
    K.guide(GROUP, "access_board_prowag", "Accessibility Guidelines for Pedestrian Facilities in the Public "
            "Right-of-Way (PROWAG, US Access Board)", "Accessible sidewalks, crossings and signals", PUBLISHER,
            f"{AB}/prowag/", r"^https://www\.access-board\.gov/prowag/([a-z0-9-]+(\.html|/))*$",
            "The Access Board's guidelines for sidewalks, street crossings and transit stops: pedestrian access "
            "routes, curb ramps and blended transitions, detectable warning surfaces, accessible pedestrian signals "
            "(audible and vibrotactile walk indications for blind pedestrians), roundabouts and channelized turn "
            "lanes, transit stops and on-street parking, with the preamble, the planning guide for alterations and "
            "the accessible sidewalks video series' text.", AB_NOTICE, depth=2,
            follow=r"^https://www\.access-board\.gov/prowag/[a-z0-9-]+/$", limit=60),
]

COLLECTION = K.Collection("travel", GROUP, guides=GUIDES,
                          words={"transport": lambda: [f"travel:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "access_board": "access-board.gov guides: \"This guide is in the public domain, and users are free to distribute "
                    "and share its content\"; works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
                    "policies page at every build). robots.txt: \"User-Agent: *\" with system folders disallowed; no "
                    "AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("DOT Aviation Consumer Protection guides, including \"Passengers with Disabilities\" and the Air Carrier Access "
     "Act fact sheets", "Public domain, but www.transportation.gov answers programs \"403 Forbidden\" (robots.txt "
     "included, checked 2026-11-22). The rule itself, 14 CFR part 382, is in the library "
     "(law:cfr_14_382_air_travel_disability). Link-only. Index: https://www.transportation.gov/airconsumer/"
     "passengers-disabilities"),
    ("Federal Transit Administration ADA guidance (Circular 4710.1)", "www.transit.dot.gov answers programs \"403 "
     "Forbidden\" (checked 2026-11-22). Link-only. Index: https://www.transit.dot.gov/regulations-and-guidance/"
     "civil-rights-ada/americans-disabilities-act"),
    ("TSA Cares and TSA's disabilities and medical conditions pages", "www.tsa.gov answered \"Access Denied\" "
     "(checked 2026-11-22). Link-only. Index: https://www.tsa.gov/travel/tsa-cares"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
