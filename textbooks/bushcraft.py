"""Bushcraft and woodcraft for the reference library, in the group "Reference, knots and outdoor skills" (the owner's
request of 2026-11-22: deepen the knots, lashings and bushcraft holdings). Keys: bushcraft (every book), bush:<name>.
A sibling of knots_outdoor.py (knot:) and knots_military.py (kmil:), in the same group.

What this module builds, in plain words:
  - bush:index, a guide to bushcraft in the library (the toolkit's own facts and links, CC0): the woodcraft classics,
    fire, shelter, water, finding your way, tools and knots, and the modern bushcraft books as links only (they are
    in copyright). It points to the survival manuals' fire, shelter, water and navigation chapters by key instead of
    copying them;
  - IN FULL, the New Zealand Department of Conservation's outdoor safety pages ("Know before you go": being prepared,
    the Land Safety Code, river crossing, fires, weather, avalanches, distress beacons, gear lists, human waste,
    litter, river safety and maps): New Zealand Crown copyright, reused under CC BY 4.0 as DOC's copyright page says
    (checked at every build), with credit to DOC;
  - old public-domain books (published before 1931; the builder checks each item's year on the Internet Archive at
    every build): Nessmuk's Woodcraft (George W. Sears, 1884; the 1900 printing), Ernest Thompson Seton's The Book of
    Woodcraft and Indian Lore (1912), Daniel Carter Beard's Shelters, Shacks and Shanties (1914), The Field and Forest
    Handy Book (1906) and The Outdoor Handy Book (1900), Robert Baden-Powell's Scouting for Boys (7th edition, 1915),
    the Girl Scouts' How Girls Can Help Their Country (1913), Frank A. Bates's Camping and Camp Cooking (1909), Stewart
    Edward White's Camp and Trail (1907) and Elon Jessup's Snow and Ice Sports (1923). Each description says what is
    out of date; Seton's and Baden-Powell's say plainly that their portrayals of Native American and other peoples
    are outdated and offensive.
  Every book carries knots_outdoor.OUTDOOR_SAFETY (rope loads, climbing training, sharp tools, fire safety and local
  rules on fires and cutting).

Already in the library and not repeated (linked from the index): Kephart's Camping and Woodcraft (outdoors:), Camp
Craft and the 1914 Boy Scout handbook (knot:), the survival and cold-weather manuals (pdf:), map reading (pdf:), the
Forest Service's and Park Service's camping and campfire pages (outcook:) and wilderness first aid (wild:).

Not built (NOT_INCLUDED, link-only): the modern bushcraft books of Mors Kochanski, Dave Canterbury and Ray Mears
(copyright), Leave No Trace (copyright), Baden-Powell's Pig-Sticking (hunting of that kind is out of scope) and the
1908 first edition of Scouting for Boys (lending-library scans only).

Run from the repository's folder:
  python3 textbooks/bushcraft.py bush:nessmuk_woodcraft_1900 --out build/textbooks --limit 3
  python3 textbooks/bushcraft.py --list bushcraft
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knots_outdoor as KO  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = KO.GROUP                       # "knots": the same group as knots_outdoor.py
GROUPS = dict(KO.GROUPS)               # {"knots": "Reference, knots and outdoor skills"}

# What is out of date in every old camping book (said in each description; "{year}" is filled in).
OLD_CAMP_NOTE = ("Published in {year}: an old book. Its camping ways are those of its day: cutting live trees and "
                 "boughs for beds and shelters, big open fires anywhere, digging trenches round tents, hunting and "
                 "trapping for food, and old remedies and first aid are out of date or not allowed today. Follow "
                 "Leave No Trace, local fire and land rules and current first aid instead.")

# ====================================================================== New Zealand Department of Conservation

DOC = "https://www.doc.govt.nz/parks-and-recreation/know-before-you-go/"
DOC_PAGES = [DOC] + [DOC + p + "/" for p in (
    "be-prepared", "land-safety-code", "river-crossing-safety", "fires", "weather", "be-avalanche-alert",
    "distress-beacon", "walking-and-tramping-gear-lists", "walking-and-tramping-gear-lists/day-hikes-gear-list",
    "walking-and-tramping-gear-lists/multi-day-tramp-gear-list", "walking-and-tramping-gear-lists/camping-gear-list",
    "walking-and-tramping-gear-lists/alpine-snow-gear-list", "disposing-of-human-waste", "take-your-litter-with-you",
    "rafting-and-kayaking-river-safety", "maps")]
DOC_LICENCE_PAGE = "https://www.doc.govt.nz/copyright/"
DOC_LICENCE_TEXT = (r"Crown Copyright and can be reused under the terms of the Creative Commons Attribution 4\.0 "
                    r"International Licence")

GUIDES = [X.page_list_book(
    GROUP, "nz_doc_outdoor_safety", "Know before you go: outdoor safety in New Zealand (Department of Conservation)",
    "Outdoor safety and backcountry skills", "Department of Conservation | Te Papa Atawhai (New Zealand)", DOC_PAGES,
    r"^https://www\.doc\.govt\.nz/parks-and-recreation/know-before-you-go/([a-z0-9-]+/){0,2}$",
    "New Zealand's Department of Conservation on getting ready for the outdoors: being prepared, the Land Safety Code, "
    "crossing rivers safely (when not to cross, and how to cross alone or as a group), fires (fire bans, safe "
    "fires and putting them out), weather, avalanches, distress beacons, gear lists for day walks, multi-day tramps, "
    "camping and alpine snow, disposing of human waste and taking your litter home, rafting and kayaking river "
    "safety, and maps.",
    "From the Department of Conservation | Te Papa Atawhai (New Zealand): Crown copyright, reused under the Creative "
    "Commons Attribution 4.0 International Licence (CC BY 4.0), credited to the Department of Conservation, as its "
    "copyright page allows; reproduced accurately, not in a misleading context. New Zealand rules and phone numbers "
    "(111 for emergencies there): check your own country's. If you are not sure a river is safe, do not cross. "
    + KO.OUTDOOR_SAFETY,
    units=[(r"gear-list", "Gear lists"), (r"river|rafting", "Rivers"), (r".", "Know before you go")],
    country="New Zealand", licence="CC BY 4.0", licence_url="https://creativecommons.org/licenses/by/4.0/",
    licence_page=DOC_LICENCE_PAGE, licence_text=DOC_LICENCE_TEXT, version="www.doc.govt.nz Know before you go",
    title_from=r"<title>\s*([^<:|]+?)\s*(?::|\||</title>)")]       # "River crossing safety: Know before you go"

# ====================================================================== old public-domain books


def _old(name, title, subject, publisher, archive, year, description, note=OLD_CAMP_NOTE, country="United States"):
    """One old public-domain bushcraft book (old_ia_books.old_book) with the safety notice."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=KO.OUTDOOR_SAFETY, country=country)


SETON_NOTE = (OLD_CAMP_NOTE + " Its \"Indian lore\" is written from the romantic and stereotyped view of white "
              "Americans in 1912: its portrayals of Native American peoples, the invented \"Indian\" names, "
              "ceremonies and costumes, and some of its words are outdated and offensive, and they are not an "
              "accurate account of any Native nation's culture. Learn about Native nations from their own sources.")
BP_NOTE = (OLD_CAMP_NOTE + " Written by a British Army general for boys of the British Empire in its day: it has "
           "military and imperial views, and some of its stories and words about African, Indian and other peoples "
           "are outdated and offensive. Its tracking, stalking and pioneering skills are what it is kept for.")

PDFS = [
    _old("nessmuk_woodcraft_1900", "Woodcraft (\"Nessmuk\", George W. Sears, 1884; the 1900 printing)",
         "Woodcraft and going light", "George W. Sears (\"Nessmuk\") (Forest and Stream Publishing)",
         "woodcraft00searuoft", 1900,
         "The classic of going light in the woods, by the writer who canoed the Adirondacks in a very light canoe: "
         "the knapsack, hatchet, knives and tinware, getting lost, camping out, insects, camps and how to make them, "
         "camp-fires and the right way to make them, fishing, camp cooking with simple recipes, a ten days' trip "
         "alone, the light canoe and double-bladed paddle, and odds and ends."),
    _old("seton_book_of_woodcraft_1912", "The Book of Woodcraft and Indian Lore (Ernest Thompson Seton, 1912)",
         "Woodcraft and nature lore", "Ernest Thompson Seton (Doubleday, Page)", "bookofwoodcrafti00seto", 1912,
         "Seton's handbook of his Woodcraft movement, gathered from twenty-five years of camp talks: camping and "
         "camp-fires, the activities, customs, laws and games of his camps, signs and signals, tracking, the stars, "
         "nature study (trees, birds and animals) and the woodcraft honours.", note=SETON_NOTE),
    _old("beard_shelters_shacks_shanties_1914", "Shelters, Shacks and Shanties (Daniel Carter Beard, 1914)",
         "Shelters and camp building", "Daniel Carter Beard (Charles Scribner's Sons)", "sheltersshackssh01bear",
         1914,
         "How to build camps and shelters, in two parts: \"tomahawk camps\" that need no tool but a hatchet (the "
         "simplest lean-tos, bough, bark and thatched shelters) and \"axe camps\" (shacks, shanties and log houses, "
         "notching logs, roofs and fireplaces), with Beard's own drawings described by their captions.",
         note=OLD_CAMP_NOTE + " Some of its names and words reflect the prejudices of its time."),
    _old("beard_field_forest_handy_book_1906", "The Field and Forest Handy Book: New Ideas for Out of Doors (Daniel "
         "Carter Beard, 1906)", "Outdoor crafts", "Daniel Carter Beard (Charles Scribner's Sons)",
         "bub_gb_TgA2AAAAMAAJ", 1906,
         "Things to make and do out of doors through the seasons, by a founder of the Boy Scouts of America: kites "
         "and broom-straw flying machines, a herbarium of pressed plants, quail and houses for useful birds, and "
         "many more outdoor projects.",
         note=OLD_CAMP_NOTE + " Some of its names and words (its first kite's name among them) reflect the "
                              "prejudices of its time."),
    _old("beard_outdoor_handy_book_1900", "The Outdoor Handy Book: For Playground, Field and Forest (Daniel Carter "
         "Beard, 1900)", "Outdoor crafts", "Daniel Carter Beard (Charles Scribner's Sons)", "forplaygroundfie00bear",
         1900,
         "Beard's book of outdoor play and craft through the seasons: marbles, tops, kites of many kinds, hoops, "
         "stilts and many more games and things to make.",
         note=OLD_CAMP_NOTE + " Some of its names and words (kite names among them) reflect the prejudices of its "
                              "time."),
    _old("baden_powell_scouting_for_boys_1915", "Scouting for Boys (Robert Baden-Powell, 7th edition, 1915)",
         "Scouting: woodcraft and pioneering", "Robert Baden-Powell (C. Arthur Pearson, London)",
         "in.ernet.dli.2015.97178", 1915,
         "The founding handbook of Scouting: scoutcraft, campaigning and camp life, tracking and observation, "
         "woodcraft and nature, knots and pioneering, endurance and health, chivalry and first aid. (The author "
         "died in 1941; the book is public domain in the US as published before 1931.)", note=BP_NOTE,
         country="United Kingdom"),
    _old("girl_scouts_how_girls_can_help_1913", "How Girls Can Help Their Country (Girl Scouts handbook, 1913)",
         "Scouting: camping and nature", "W. J. Hoxie, adapted for Juliette Gordon Low's Girl Scouts (Knickerbocker "
         "Press)", "howgirlscanhelpt00hoxi", 1913,
         "The first handbook of the Girl Scouts in the United States, adapted from Agnes and Robert Baden-Powell's "
         "handbook: starting a patrol and the Girl Scout law, camping (open-air pursuits, woodcraft, botany, the "
         "stars, gardening), home life, tending the injured and preparing for accidents, and the tests for badges.",
         note=OLD_CAMP_NOTE + " Its ideas of what girls should learn are those of 1913."),
    _old("bates_camping_camp_cooking_1909", "Camping and Camp Cooking (Frank A. Bates, 1909)",
         "Camping and camp cooking", "Frank A. Bates (The Ball Publishing Company)", "campingcampcooki00bate", 1909,
         "A small handbook for campers who want rest and three square meals without a guide: camp outfits, making "
         "camp, camp cooking with simple recipes, and cleaning fish. (Today's camp and emergency cooking books are "
         "under the request word outdoor-cooking.)"),
    _old("white_camp_and_trail_1907", "Camp and Trail (Stewart Edward White, 1907)", "Camping and trail travel",
         "Stewart Edward White (The Outing Publishing Company)", "camptrail00whitrich", 1907,
         "Travelling and camping in the wilderness: the wilderness traveller and common sense, personal equipment, "
         "the camp outfit and cook outfit, grub and camp cookery, horse outfits and horse packs, horses, mules and "
         "burros, and canoes."),
    _old("jessup_snow_ice_sports_1923", "Snow and Ice Sports (Elon Jessup, 1923)", "Winter outdoors",
         "Elon Jessup (E. P. Dutton and Company)", "snowicesports0000elon", 1923,
         "A winter outdoors book: dressing for the cold, skis and ski jumping, snowshoes, toboggans, winter "
         "mountaineering, ice creepers, camping in the snow, snow photography, ice fishing, ice boating, skating, "
         "ice hockey and curling.",
         note=OLD_CAMP_NOTE + " Its ski and skate gear is that of 1923; check ice thickness with local advice, and "
                              "never go on ice alone."),
]

# ====================================================================== the index

SECTIONS = [
    ("Woodcraft classics", "The old books of camping and woodcraft, each with a note on what is out of date.", [
        ("key", "bush:nessmuk_woodcraft_1900", "Woodcraft (Nessmuk, 1884): going light"),
        ("key", "outdoors:kephart_camping_woodcraft_1921", "Camping and Woodcraft (Kephart, 1921)"),
        ("key", "bush:seton_book_of_woodcraft_1912", "The Book of Woodcraft (Seton, 1912), with a note on its "
                                                     "outdated portrayals"),
        ("key", "bush:white_camp_and_trail_1907", "Camp and Trail (White, 1907)"),
        ("key", "knot:miller_camp_craft_1915", "Camp Craft (Miller, 1915)"),
        ("key", "knot:boy_scouts_handbook_1914", "The Boy Scouts' Official Handbook for Boys (1914)"),
        ("key", "bush:baden_powell_scouting_for_boys_1915", "Scouting for Boys (Baden-Powell, 1915)"),
        ("key", "bush:girl_scouts_how_girls_can_help_1913", "How Girls Can Help Their Country (Girl Scouts, 1913)"),
        ("key", "bush:beard_field_forest_handy_book_1906", "The Field and Forest Handy Book (Beard, 1906)"),
        ("key", "bush:beard_outdoor_handy_book_1900", "The Outdoor Handy Book (Beard, 1900)")]),
    ("Fire", "Lighting a fire safely, keeping it small and putting it out cold. Check fire bans first.", [
        ("key", "bush:nz_doc_outdoor_safety", "Fires, fire bans and putting a fire out (New Zealand DOC)"),
        ("key", "outcook:usfs_camping_food_bears", "Campfires (US Forest Service)"),
        ("key", "pdf:army_atp_3_50_21_survival", "The Army's survival manual: firecraft (ATP 3-50.21)"),
        ("key", "pdf:army_fm_21_76_survival_1992", "Survival (FM 21-76, 1992): firecraft"),
        ("key", "pdf:usaf_afr_64_4_survival_1985", "The Air Force's survival textbook: fire (AFR 64-4)"),
        ("link", "Smokey Bear: campfire safety", "https://smokeybear.com/",
         "the US Forest Service and the Ad Council's campaign site; open it in a browser")]),
    ("Shelter", "Tents, tarps, lean-tos, snow shelters and staying warm.", [
        ("key", "bush:beard_shelters_shacks_shanties_1914", "Shelters, Shacks and Shanties (Beard, 1914)"),
        ("key", "kmil:usmc_mcrp_12_10a2_winter_operations", "Snow shelters (Marine Corps winter guide)"),
        ("key", "pdf:army_tc_21_3_cold_weather", "The Army's cold-weather handbook: shelters (TC 21-3)"),
        ("key", "pdf:army_fm_31_70_cold_weather_1968", "Basic Cold Weather Manual (FM 31-70)"),
        ("key", "pdf:army_atp_3_50_21_survival", "The Army's survival manual: shelters (ATP 3-50.21)")]),
    ("Water", "Finding water and making it safe to drink.", [
        ("key", "pdf:army_atp_3_50_21_survival", "The Army's survival manual: water procurement (ATP 3-50.21)"),
        ("key", "pdf:army_fm_21_76_survival_1992", "Survival (FM 21-76, 1992): water"),
        ("word", "wilderness-first-aid", "Wilderness first aid and backcountry safety, with water treatment"),
        ("word", "preparedness", "Emergency preparedness books: storing and treating water")]),
    ("Finding your way, weather and rivers", "Maps and compass, weather, and crossing rivers safely.", [
        ("key", "pdf:army_fm_3_25_26_map_reading", "Map Reading and Land Navigation (FM 3-25.26)"),
        ("key", "bush:nz_doc_outdoor_safety", "River crossing, weather, maps and distress beacons (New Zealand DOC)"),
        ("key", "pdf:army_fm_21_76_survival_1992", "Survival (FM 21-76, 1992): direction finding"),
        ("pack", "commons_outdoor_skills", "Compasses, for the picture describer")]),
    ("Tools, knots and lashings", "Axe, saw and knife work, knots and lashings.", [
        ("key", "knot:index", "Knots and outdoor skills: the guide to knots, lashings, axes and saws"),
        ("key", "knot:usfs_ax_manual", "An Ax to Grind: the Forest Service's axe manual"),
        ("word", "knots-outdoor", "The knot and outdoor skills books (request word)"),
        ("word", "knots-military", "The military and Coast Guard knot, rope and pack manuals (request word)"),
        ("manuals", "outdoor_tools", "Axe, saw, knife, sharpener, compass and rope makers' manuals, as links")]),
    ("Modern bushcraft books (links only)", "These are in copyright: borrow them from a library or buy them.", [
        ("link", "Mors Kochanski, Bushcraft: Outdoor Skills and Wilderness Survival",
         "https://openlibrary.org/search?q=mors+kochanski+bushcraft", "copyright; Open Library's catalogue entry"),
        ("link", "Dave Canterbury, Bushcraft 101", "https://openlibrary.org/search?q=dave+canterbury+bushcraft",
         "copyright; Open Library's catalogue entry"),
        ("link", "Ray Mears, Essential Bushcraft and Outdoor Survival", "https://openlibrary.org/search?q=ray+mears",
         "copyright; Open Library's catalogue entry"),
        ("link", "Leave No Trace Seven Principles", "https://lnt.org/why/7-principles/",
         "copyright of the Leave No Trace Center; open it in a browser")]),
]
INDEX = X.index_maker("bush", GROUP, "Bushcraft and woodcraft: a guide to the library", "Bushcraft and woodcraft",
                      "A guide to bushcraft in the library: the woodcraft classics, fire, shelter, water, finding "
                      "your way, tools, knots and lashings, and the modern bushcraft books as links.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("bush", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"bushcraft": lambda: ["bush:index"] + [f"bush:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "bush_nz_doc": "www.doc.govt.nz/copyright/ (checked at every build): \"Unless identified as having third party "
                   "copyright or other licence, the material on this website is Crown Copyright and can be reused "
                   "under the terms of the Creative Commons Attribution 4.0 International Licence (CC BY 4.0)\"; "
                   "robots.txt allows /parks-and-recreation/; no AI rules (checked 2026-11-22).",
    "bush_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so a "
                      "later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                      "2026-11-22). Scouting for Boys is a British book: public domain in the US as published before "
                      "1931 (and in the UK, its author having died in 1941).",
    "bush_index": "The index (bush:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Modern bushcraft books: Mors Kochanski, Dave Canterbury, Ray Mears, Cody Lundin and others", "Copyright of their "
     "authors and publishers; link-only from the index (bush:index). Index: "
     "https://openlibrary.org/search?q=bushcraft"),
    ("Scouting for Boys, 1908 first edition", "The Internet Archive's 1908 copies are lending-library scans that "
     "cannot be downloaded; the 7th edition (1915) is built. Index: "
     "https://archive.org/details/scoutingforboys0000lord_t5a2"),
    ("Baden-Powell, Pig-Sticking or Hoghunting (1889)", "Hunting with spears from horseback: out of scope for this "
     "collection. Index: https://archive.org/search?query=pig-sticking+baden-powell"),
    ("Elon Jessup, The Motor Camping Book and Roughing It Smoothly", "Not found as downloadable copies on the Internet "
     "Archive (searched 2026-11-22); motor camping is in the RV collection (rvs:). Index: "
     "https://archive.org/search?query=creator%3Ajessup+camping"),
    ("US Forest Service and National Park Service Leave No Trace and campcraft pages", "Leave No Trace's own "
     "principles are copyright of the Leave No Trace Center; the Forest Service's and Park Service's camping and "
     "campfire pages are already built (outcook:usfs_camping_food_bears and the outdoors collection). Index: "
     "https://www.fs.usda.gov/visit/know-before-you-go"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
