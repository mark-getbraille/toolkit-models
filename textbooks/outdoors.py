"""Outdoor recreation for the reference library, in the group "Reference, outdoor recreation" (the owner's request of
2026-11-22). Keys: outdoors (every book), outdoors:<name>.

What this module builds, in plain words, each IN FULL:
  - the US Coast Guard's "A Boater's Guide to the Federal Requirements for Recreational Boats" (the boating
    handbook: life jackets, fire extinguishers, lights, sound signals, navigation rules, registration, reporting
    accidents), a US government work, and the Coast Guard Boating Safety pages for recreational boaters (wearing a
    life jacket, engine cut-off switches, carbon monoxide, boating under the influence, float plans, courses);
  - the US Forest Service's "Know before you go" safety pages not already built by outdoor_cooking.py: hiking, if you
    get lost, hypothermia, heat and sun, lightning, avalanches, ticks, snakes, mountain lions, hazard trees, floods,
    caves, mountain biking, off-highway vehicles, hunting and target shooting safety, places to fish and wildlife
    photography;
  - the National Park Service's hiking safety, trails, birding and accessibility pages (the NPS accessibility
    programme: what parks offer visitors with disabilities and how to ask);
  - the US Fish and Wildlife Service's hunting and fishing pages (hunting and fishing on national wildlife refuges and
    hatchery lands, licences and where to go);
  - NOAA Fisheries' species directory, species by species (what each fish, shellfish or marine mammal looks like,
    where it lives, its status, and fishing rules in federal waters), for identifying what you catch;
  - Horace Kephart's Camping and Woodcraft (1921), an old public-domain classic of camp skills (with what is out of
    date said in its description).
  Every book carries the outdoor safety note (SAFETY): wear a life jacket, cold water, ice, lightning, telling someone
  your plan, and for hunting the firearm line used everywhere in the toolkit ("Treat every gun as loaded, and keep
  your fingers away from the trigger.") with blaze orange and hunter education.

Already in the library and not repeated: the camping, food, bear and water safety pages of the Forest Service and the
Park Service's camp cooking pages (outdoor_cooking.py), the NWS weather safety pages (prep:), the old seamanship books
(thin:boating), the Access Board's recreation facility guides (travel:), the marine electronics, outboard motor and
camping gear manuals (manual collections), and the firearms collections (their safety rules are kept here).

Not built (NOT_INCLUDED, link-only): the hunter education course (IHEA-USA and Kalkomey: copyright), state wildlife
agency regulations and guides (each state's own; rules change every season: link-only by state), Red Cross swimming
and water safety (copyright), CDC drowning pages and NHTSA bicycle safety (refuse programs), NWS JetStream and the
Coast Guard's navigation centre (refuse programs), Leave No Trace (copyright).

Run from the repository's folder:
  python3 textbooks/outdoors.py outdoors:uscg_boating_safety --out build/textbooks --limit 3
  python3 textbooks/outdoors.py --list outdoors
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "outdoors"
GROUPS = {GROUP: "Reference, outdoor recreation"}

# The firearm line used everywhere in the toolkit (packs/safety_rites_packs.py GUN_LINE).
GUN_LINE = "Treat every gun as loaded, and keep your fingers away from the trigger."
SAFETY = ("Safety: wear a life jacket on and near the water, and make sure everyone has one that fits; cold water "
          "can stop you swimming within minutes. Never walk on ice unless it is known to be thick enough, and never "
          "alone. Tell someone where you are going and when you will be back; carry water, a light and a phone or "
          "whistle. When thunder roars, go indoors. Hunters: take a hunter education course, wear blaze orange, "
          "identify your target and what is beyond it, and follow your state's rules. " + GUN_LINE +
          " In an emergency call 911 (on the water, VHF channel 16).")

# ====================================================================== US Coast Guard boating safety

USCG = "https://uscgboating.org/recreational-boaters/"
PDFS = [
    K.us_pdf(GROUP, name="uscg_boaters_guide_federal_requirements", title="A Boater's Guide to the Federal "
             "Requirements for Recreational Boats and Safety Tips (US Coast Guard)",
             subject="Boating safety", publisher="US Coast Guard, Office of Auxiliary and Boating Safety",
             pdf="https://www.uscgboating.org/assets/1/AssetManager/Boaters-Guide-to-Federal-Requirements-for-"
                 "Receational-Boats-20231108.pdf", page=USCG,
             version="the November 2023 printing (its file name's date)", published="2023-11",
             description="The Coast Guard's boating handbook: registration and documentation, the equipment the law "
                         "requires (life jackets, fire extinguishers, visual distress signals, sound devices, "
                         "navigation lights, ventilation, backfire flame arrestors), the navigation rules and aids to "
                         "navigation (buoys and markers), boating under the influence, carbon monoxide, reporting "
                         "accidents, and safety tips.",
             notice="A work of the US Coast Guard (public domain). " + SAFETY),
]
GUIDES = [
    K.guide(GROUP, "uscg_boating_safety", "Recreational boating safety (US Coast Guard Boating Safety)",
            "Boating safety", "US Coast Guard, Office of Auxiliary and Boating Safety", USCG + "index.php",
            r"^https://(www\.)?uscgboating\.org/recreational-boaters/[a-z0-9-]+\.php$",
            "The Coast Guard Boating Safety pages for recreational boaters: wearing your life jacket and choosing one, "
            "engine cut-off devices, carbon monoxide on boats, boating under the influence, float plans, fire "
            "extinguishers, boating safety courses, shallow-water boat performance and accident reporting.",
            "A work of the US Coast Guard (public domain). " + SAFETY, depth=1, limit=40,
            content=(r'<div class="body-container"[^>]*>', r'<div class="footer-container'),
            urls=[USCG + "life-jacket-wear-wearing-your-life-jacket.php"]),
]

# ====================================================================== US Forest Service: know before you go

FS = "https://www.fs.usda.gov/visit/know-before-you-go/"
FS_PAGES = [FS + p for p in (
    "safety", "hiking", "if-you-get-lost", "hypothermia", "heat", "sun-safety", "lightning", "avalanches", "ticks",
    "snakes", "mountain-lions", "bats", "hazard-trees", "floods", "cave-safety", "mines", "mountain-biking",
    "off-highway-vehicle-touring", "hunting", "shooting", "great-places-to-fish-with-us", "wildlife-photography")]
GUIDES.append(K.us_web(
    GROUP, name="usfs_know_before_you_go", title="Outdoor safety on the national forests: hiking, getting lost, "
    "weather, wildlife, hunting and fishing (US Forest Service)", subject="Hiking and outdoor safety",
    publisher="US Forest Service (US Department of Agriculture)", source=FS_PAGES[0], crawl=[(FS_PAGES[0], 0)],
    urls=list(FS_PAGES), pages=r"^https://www\.fs\.usda\.gov/visit/know-before-you-go/[a-z0-9-]+$",
    unit_rules=[(r"/(hunting|shooting|great-places-to-fish|wildlife-photography)$", "Hunting, shooting and fishing"),
                (r"/(hypothermia|heat|sun-safety|lightning|avalanches|floods)$", "Weather, cold and heat"),
                (r"/(ticks|snakes|mountain-lions|bats|hazard-trees|cave-safety|mines)$", "Wildlife and hazards"),
                (r".", "Hiking and getting lost")], limit=len(FS_PAGES) + 5,
    description="The Forest Service's visitor safety pages: general safety, hiking, what to do if you get lost, "
                "hypothermia, heat and sun, lightning, avalanches, ticks, snakes, mountain lions, bats, hazard trees, "
                "floods, caves and old mines, mountain biking, off-highway vehicles, hunting and target shooting on "
                "the national forests, great places to fish, and wildlife photography.",
    notice="From the US Forest Service: a US government work (public domain). Check the local forest's rules and "
           "conditions before you go. " + SAFETY))

# ====================================================================== National Park Service

NPS = "https://www.nps.gov"
NPS_TERMS = NPS + "/aboutus/disclaimer.htm"
NPS_TEXT = r"material created by the National Park Service and presented on this website, unless otherwise " \
           r"indicated, is generally considered in the public domain"
NPS_PAGES = [NPS + p for p in ("/subjects/trails/hiking-safety.htm", "/articles/hiking-safety.htm",
                               "/subjects/birds/birding.htm", "/subjects/accessibility/index.htm",
                               "/subjects/accessibility/about.htm", "/subjects/accessibility/what-we-do.htm",
                               "/subjects/accessibility/what-you-can-do.htm")]
GUIDES.append(dict(K.us_web(
    GROUP, name="nps_hiking_birding_accessibility", title="Hiking safety, birding and accessibility in the national "
    "parks (National Park Service)", subject="National parks: hiking, birding and accessibility",
    publisher="National Park Service (US Department of the Interior)", source=NPS_PAGES[0], crawl=[(NPS_PAGES[0], 0)],
    urls=list(NPS_PAGES), pages=r"^https://www\.nps\.gov/(subjects/(trails|birds|accessibility)|articles)/"
                                r"[a-z0-9-]+\.htm$",
    content=(r'<div id="main" role="main" class="MainContent">', r'<div id="related_content_position">|<footer\b'),
    unit_rules=[(r"accessibility", "Accessibility in the parks"), (r"birds", "Birding"), (r".", "Hiking safety")],
    limit=len(NPS_PAGES) + 5,
    description="The National Park Service's pages on hiking safely (the ten essentials, water, weather, pacing, "
                "staying on the trail), birding in the parks, and accessibility: what the parks do for visitors with "
                "disabilities, the Access Pass, and how to ask a park about accessible trails, tours and programmes.",
    notice="From the National Park Service: \"material created by the National Park Service ... is generally "
           "considered in the public domain\"; source: National Park Service (nps.gov). Each park has its own rules: "
           "check them before you go. " + SAFETY),
    licence_page=NPS_TERMS, licence_text=NPS_TEXT))

# ====================================================================== US Fish and Wildlife Service

FWS_PAGES = ["https://www.fws.gov/hunting", "https://www.fws.gov/fishing",
             "https://www.fws.gov/initiative/hunting/hunting-us-fish-and-wildlife-service-lands-and-waters"]
GUIDES.append(K.us_web(
    GROUP, name="fws_hunting_fishing", title="Hunting and fishing on national wildlife refuges (US Fish and Wildlife "
    "Service)", subject="Hunting and fishing", publisher="US Fish and Wildlife Service (US Department of the "
    "Interior)", source=FWS_PAGES[0], crawl=[(FWS_PAGES[0], 0)], urls=list(FWS_PAGES),
    pages=r"^https://www\.fws\.gov/(hunting|fishing|initiative/hunting/[a-z0-9-]+)$",
    unit_rules=[(r"fishing", "Fishing"), (r".", "Hunting")], limit=10,
    description="The Fish and Wildlife Service's pages on hunting and fishing: where you may hunt and fish on "
                "national wildlife refuges and hatchery lands, licences and stamps (each state's licence and the "
                "federal duck stamp), and the rules that apply on the refuges.",
    notice="From the US Fish and Wildlife Service: a US government work (public domain). Hunting and fishing rules are "
           "set by each state and refuge and change every season: check the current regulations. " + SAFETY))

# ====================================================================== NOAA Fisheries species directory

NOAA_DIR = "https://www.fisheries.noaa.gov/species-directory?page="
GUIDES.append(K.us_web(
    GROUP, name="noaa_fisheries_species", title="Fish and marine species directory (NOAA Fisheries)",
    subject="Fish identification", publisher="NOAA Fisheries (National Marine Fisheries Service)",
    source="https://www.fisheries.noaa.gov/species-directory", crawl=[(f"{NOAA_DIR}{n}", 1) for n in range(13)],
    pages=r"^https://www\.fisheries\.noaa\.gov/species/[a-z0-9-]+$", limit=340,
    description="NOAA Fisheries' species directory, species by species: fish, shellfish, sea turtles and marine "
                "mammals of US waters, each with what it looks like, where it lives, its life and diet, its "
                "population status, and fishing rules in federal waters (\"Fishing and Seafood\").",
    notice="From NOAA Fisheries: a US government work (public domain). Fishing rules in state waters are each state's: "
           "check them before you fish. " + SAFETY))

# ====================================================================== old public-domain book

PDFS.append(old_book(
    GROUP, "kephart_camping_woodcraft_1921", "Camping and Woodcraft (Horace Kephart, 1921)", "Camping and woodcraft",
    "Horace Kephart (Macmillan)", "campingwoodcraft00kephrich", 1921,
    "The classic American handbook of camp skills: outfits, tents and bedding, camp cookery, finding the way, "
    "woodcraft, axemanship, shelters and first aid in the woods.",
    note="Published in {year}: an old book. Cutting live trees, building bough beds and big fires, and many of its "
         "foods, remedies and first aid methods are out of date or not allowed today: follow current Forest Service "
         "and Park Service rules and Leave No Trace.", notice=SAFETY))

COLLECTION = K.Collection("outdoors", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"outdoors": lambda: [f"outdoors:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "outdoors_uscg": "uscgboating.org: works of the US Coast Guard (17 U.S.C. 105, checked on govinfo.gov's policies "
                     "page at every build); the site has no robots.txt rules (404), no AI rules (checked 2026-11-22).",
    "outdoors_usfs_fws_noaa": "www.fs.usda.gov, www.fws.gov and www.fisheries.noaa.gov: works of the US government "
                              "(17 U.S.C. 105); robots.txt allows the pages, no AI rules (checked 2026-11-22).",
    "outdoors_nps": "www.nps.gov/aboutus/disclaimer.htm (checked at every build): NPS material \"is generally "
                    "considered in the public domain\", credited in the notice; NPS asks 5 seconds between pages, "
                    "which the builder keeps.",
    "outdoors_old_book": "Internet Archive item campingwoodcraft00kephrich: its metadata \"date\" (1921) is checked at "
                         "every build.",
}
NOT_INCLUDED = [
    ("Hunter education course and handbook (IHEA-USA, Kalkomey's hunter-ed.com and the state courses)", "Copyright "
     "of IHEA-USA and Kalkomey; link-only. Every state requires its own course for new hunters. Index: "
     "https://www.ihea-usa.org/ and https://www.hunter-ed.com/"),
    ("State wildlife agency hunting and fishing regulations and guides (all 50 states)", "Each state's own work "
     "(many state works are copyright) and they change every season; link-only, by state. Index: "
     "https://www.fws.gov/hunting (links to each state agency)"),
    ("American Red Cross swimming and water safety", "\"(c) American Red Cross\": copyright; link-only. Index: "
     "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/water-safety.html"),
    ("CDC drowning prevention pages", "Public domain under CDC's terms, but www.cdc.gov answered this build machine "
     "\"403\" (2026-11-22). Link-only. Index: https://www.cdc.gov/drowning/"),
    ("NHTSA bicycle safety (bike touring and riding on roads)", "Public domain, but www.nhtsa.gov refuses programs "
     "(\"403\", robots.txt included, 2026-11-22). Link-only. Index: https://www.nhtsa.gov/road-safety/bicycle-safety"),
    ("NWS JetStream and NWS winter and water safety", "JetStream refuses programs (\"403\"); the NWS safety pages are "
     "already built (prep:). Index: https://www.weather.gov/safety/"),
    ("US Coast Guard Navigation Center: the US Aids to Navigation System brochure (buoys and markers)", "Public "
     "domain, but www.navcen.uscg.gov refuses programs (\"403\", robots.txt included, 2026-11-22); the Boater's "
     "Guide (built) explains the buoys and markers. Link-only. Index: https://www.navcen.uscg.gov/"),
    ("Leave No Trace Seven Principles", "Copyright of the Leave No Trace Center for Outdoor Ethics; link-only (as in "
     "outdoor_cooking.py). Index: https://lnt.org/why/7-principles/"),
    ("Adaptive outdoor recreation programmes (Disabled Sports USA / Move United, NSCD, Adaptive Adventures, the Access "
     "Board's outdoor guide)", "The programmes' pages are each organisation's copyright; the Access Board's guides "
     "are already in the library (travel:). Link-only. Index: https://moveunitedsport.org/ and "
     "https://www.access-board.gov/ada/guides/"),
    ("Paddling, winter sports and bike touring guides (American Canoe Association, National Ski Areas Association, "
     "Adventure Cycling Association)", "Copyright of each organisation; link-only. The Coast Guard's life jacket "
     "pages and the Forest Service's avalanche and hypothermia pages are built. Index: "
     "https://americancanoe.org/ and https://www.adventurecycling.org/"),
    ("Fishing reel, boat, kayak and outboard motor makers' manuals", "The makers' copyright; links in the manual "
     "collection outdoors (outboards and marine electronics are already in their own collections). Index: "
     "https://www.pure-fishing.com/ and https://www.mercurymarine.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
