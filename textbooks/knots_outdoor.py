"""Knots, rope and practical outdoor skills for the reference library, in the group "Reference, knots and outdoor
skills" (the owner's request of 2026-11-22). Keys: knots-outdoor (every book), knot:<name>.

What this module builds, in plain words:
  - knot:index, a guide to the library on knots and outdoor skills (the toolkit's own facts and links, CC0): knots by
    name and use, splicing and lashings, rope types and care, map and compass, fire building and safety, shelter,
    water, tool sharpening and axe and saw use, with the books by key, the picture packs and the links;
  - IN FULL, from the US Forest Service (US government works): An Ax to Grind: A Practical Ax Manual (1999, the
    Forest Service's axe manual, every page of its web edition), the Crosscut Saw Manual (Warren Miller, 1977, revised
    2003) and Saws That Sing: A Guide to Using Crosscut Saws (2004);
  - old public-domain books (published before 1931; the builder checks each item's year on the Internet Archive at
    every build): A. Hyatt Verrill's Knots, Splices and Rope Work (1912), Clifford Aldridge's Knots: a study of
    marlinespike seamanship (1918), Paul Hasluck's Knotting and Splicing Ropes and Cordage (1907), the Boy Scouts of
    America's Official Handbook for Boys (1914 printing: knots, camping, first aid, woodcraft and signalling) and
    Warren Miller's Camp Craft (1915). Each old book's description says what is out of date in it.
  Every book carries OUTDOOR_SAFETY in its notice (sharp tools, rope that holds people and its working load, fire and
  local rules on fires and cutting, and telling someone where you are going).
  Two more old knot books were added with the sibling modules (2026-11-22): J. Tom Burgess's Knots, Ties and Splices
  (1884) and George Russell Shaw's Knots, Useful and Ornamental (1924).

Sibling modules in the same group (each with its own request word): knots_military.py (kmil:, knots-military: the
Coast Guard, Navy, Army and Marine Corps knot, rope, pack and mountain manuals) and bushcraft.py (bush:, bushcraft:
the old woodcraft classics, New Zealand's Department of Conservation outdoor safety pages and the bushcraft index).
The index here (knot:index) links their books by key.

Already in the library and not repeated: the Army's rigging manual (FM 5-125: knots, hitches, splices, lashings and
lifting), map reading and land navigation (FM 3-25.26), the survival manuals (ATP 3-50.21, FM 21-76 and others) and
mountaineering (TC 3-97.61) (fieldmanuals), the USGS topographic map symbols (thin), the Forest Service's and Park
Service's camping, campfire and bear pages (outdoor-cooking), and water, shelter and preparedness (preparedness and
disasters).

Not built (NOT_INCLUDED, link-only): The Ashley Book of Knots (copyright), Animated Knots (copyright), the current
Boy Scout and Girl Scout handbooks (copyright), Leave No Trace (copyright) and the Forest Service's other saw and
chainsaw guides that answer programs "403".

Run from the repository's folder:
  python3 textbooks/knots_outdoor.py knot:usfs_ax_manual --out build/textbooks --limit 3
  python3 textbooks/knots_outdoor.py --list knots-outdoor
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "knots"
GROUPS = {GROUP: "Reference, knots and outdoor skills"}

# The same safety words as packs/knots_outdoor_packs.py ROPE_NOTE and TOOL_NOTE, written for a book.
OUTDOOR_SAFETY = ("Safety: a knot weakens a rope and some knots slip or jam, so never load a rope beyond its working "
                  "load limit, and for climbing, lifting or rescue use rated gear and learn from a qualified "
                  "instructor (climbing needs proper training). With axes, saws and knives, cut away from your "
                  "body, keep people at least two tool lengths away, wear eye protection and sturdy boots, and keep "
                  "blades covered. Check fire restrictions before lighting any fire and put it out cold; know and "
                  "follow local rules on fires and cutting. Tell someone where you are going and when you will be "
                  "back.")
OLD_OUTDOOR_NOTE = ("Published in {year}: an old book. Its knots and rope work are still tied the same way, but "
                    "natural-fibre ropes have given way to nylon and polyester (which need different knots for "
                    "slippery line), and its camping advice is out of date (cutting live trees for beds and shelters, "
                    "open fires anywhere, old first aid): follow Leave No Trace, local fire rules and current first "
                    "aid "
                    "instead. The machine-read text has the scanner's mistakes.")

FS_TD = "https://www.fs.usda.gov/t-d/pubs/"

# ====================================================================== US Forest Service (public domain)

AX = FS_TD + "htmlpubs/htm99232823/"
GUIDES = [K.guide(GROUP, "usfs_ax_manual", "An Ax to Grind: A Practical Ax Manual (US Forest Service, 1999)",
                  "Axe use and care", "US Forest Service, Missoula Technology and Development Center (Bernie "
                  "Weisgerber and Brian Vachowski)", AX + "toc.htm", rf"^{AX}(toc|page\d\d)\.htm$",
                  "The Forest Service's axe manual, every page: the history of the axe, axe patterns and handles, "
                  "choosing an axe, hanging (fitting) a handle, sharpening by file and stone, safe use (clearing the "
                  "swing, stance, felling, limbing and bucking, splitting), carrying and storing an axe, and the "
                  "related tools (hatchets, double-bit axes, the Pulaski).",
                  f"From the US Forest Service: a US government work (public domain). {OUTDOOR_SAFETY}", depth=1,
                  units=[(r"toc", "Contents"), (r".", "The ax manual")], limit=40,
                  version="9923-2823-MTDC (1999), web edition")]

PDFS = [
    K.us_pdf(GROUP, name="usfs_crosscut_saw_manual", title="Crosscut Saw Manual (US Forest Service, 1977, revised "
             "2003)", subject="Crosscut saws", publisher="US Forest Service, Missoula Technology and Development "
             "Center (Warren Miller)", pdf=FS_TD + "pdfpubs/pdf77712508/pdf77712508dpi300.pdf",
             page=FS_TD + "pdfpubs/pdf77712508/pdf77712508dpi300.pdf", published="2003",
             version="7771-2508-MTDC, revised 2003",
             description="The Forest Service's classic guide to the crosscut saw: the kinds of saws and teeth, how a "
                         "saw cuts, filing and setting the teeth, the tools and a filing vise, and keeping a saw "
                         "sharp and true.",
             notice=f"From the US Forest Service: a US government work (public domain). {OUTDOOR_SAFETY}"),
    K.us_pdf(GROUP, name="usfs_saws_that_sing", title="Saws That Sing: A Guide to Using Crosscut Saws (US Forest "
             "Service, 2004)", subject="Crosscut saws", publisher="US Forest Service, Missoula Technology and "
             "Development Center", pdf=FS_TD + "pdfpubs/pdf04232822/pdf04232822dpi300.pdf",
             page=FS_TD + "pdfpubs/pdf04232822/pdf04232822dpi300.pdf", published="2004",
             version="0423-2822-MTDC, 2004",
             description="Using a crosscut saw safely: sizing up a cut, binds and how the log will move, felling, "
                         "bucking and limbing, single and two-person sawing, wedges and axes, and caring for the saw "
                         "in the field.",
             notice=f"From the US Forest Service: a US government work (public domain). {OUTDOOR_SAFETY}"),
    X.old_book(GROUP, "verrill_knots_splices_1912", "Knots, Splices and Rope Work (A. Hyatt Verrill, 1912)",
               "Knots and splices", "A. Hyatt Verrill (Norman W. Henley Publishing)", "knotssplicesrope00verr", 1912,
               "A practical treatise on tying every useful knot: the parts of a rope, simple knots and hitches, "
               "bends, loops, splices (eye, short and long), whippings and seizings, fancy knots and rope work, and "
               "knots for fishing and boating, with the figures described by their captions.",
               OLD_OUTDOOR_NOTE.format(year=1912)),
    X.old_book(GROUP, "aldridge_knots_marlinespike_1918", "Knots: a study of marlinespike seamanship (Clifford "
               "Aldridge, 1918)", "Knots and marlinespike seamanship", "Clifford Aldridge", "knotsstudyofmarl00aldr",
               1918, "Knots, bends, hitches, ties, fastenings and splices as sailors use them, and how each is used "
                     "on board.", OLD_OUTDOOR_NOTE.format(year=1918)),
    X.old_book(GROUP, "hasluck_knotting_splicing_1907", "Knotting and Splicing Ropes and Cordage (Paul N. Hasluck, "
               "1907)", "Knots and splices", "Paul N. Hasluck (Cassell and Company)", "gri_33125000664421", 1907,
               "Knots, hitches, bends, splices and lashings for ropes and cords, with slings, nets and fancy rope "
               "work.", OLD_OUTDOOR_NOTE.format(year=1907), country="United Kingdom"),
    X.old_book(GROUP, "boy_scouts_handbook_1914", "The Official Handbook for Boys (Boy Scouts of America, 1914 "
               "printing)", "Scouting: knots, camping and woodcraft", "Boy Scouts of America", "officialhandbook00newy",
               1914, "The early Boy Scout handbook: scoutcraft, woodcraft and campcraft (knots, camping, cooking, "
                     "fire building), tracking, nature study, first aid and life saving, signalling, and health.",
               OLD_OUTDOOR_NOTE.format(year=1914)),
    X.old_book(GROUP, "miller_camp_craft_1915", "Camp Craft: Modern Practice and Equipment (Warren H. Miller, 1915)",
               "Camping and woodcraft", "Warren H. Miller (Charles Scribner's Sons)", "campcraftmodernp00millrich",
               1915, "Camping as practised in 1915: tents and shelters, bedding, packs, camp cooking and fires, axes "
                     "and knives, canoe and pack trips.", OLD_OUTDOOR_NOTE.format(year=1915)),
    # Added with the military and bushcraft books (knots_military.py, bushcraft.py), 2026-11-22.
    X.old_book(GROUP, "burgess_knots_ties_splices_1884", "Knots, Ties and Splices (J. Tom Burgess, 1884)",
               "Knots and splices", "J. Tom Burgess (George Routledge and Sons, London)", "cu31924014519940", 1884,
               "A handbook for seafarers, travellers and all who use cordage: the simple knots, bends and hitches, "
               "loops and nooses for work, splices and seizings, knots for fishing lines, and the history and "
               "heraldry of knots.", OLD_OUTDOOR_NOTE.format(year=1884), country="United Kingdom"),
    X.old_book(GROUP, "shaw_knots_useful_ornamental_1924", "Knots, Useful and Ornamental (George Russell Shaw, "
               "1924)", "Knots and splices", "George Russell Shaw (Houghton Mifflin Company)",
               "bwb_S0-ACD-595", 1924,
               "An architect's carefully drawn book of knots: the elements of a knot, knots and hitches for every "
               "use, bends, loops, splices, sennits (braided cords), and ornamental knots and mats, each drawing "
               "described by its caption.", OLD_OUTDOOR_NOTE.format(year=1924)),
]
# The old books carry the safety notice too (after the scan notice).
for _p in PDFS:
    if _p.get("old_public_domain"):
        _p["notice"] = f"{_p['notice']} {OUTDOOR_SAFETY}"

# ====================================================================== the index

SECTIONS = [
    ("Knots by name and use", "Loops, hitches, bends, stoppers and binding knots: which knot for which job.", [
        ("key", "knot:verrill_knots_splices_1912", "Knots, Splices and Rope Work (Verrill, 1912)"),
        ("key", "knot:aldridge_knots_marlinespike_1918", "Knots: marlinespike seamanship (Aldridge, 1918)"),
        ("key", "knot:burgess_knots_ties_splices_1884", "Knots, Ties and Splices (Burgess, 1884)"),
        ("key", "knot:shaw_knots_useful_ornamental_1924", "Knots, Useful and Ornamental (Shaw, 1924)"),
        ("key", "pdf:army_fm_5_125_rigging", "The Army's rigging manual: knots, hitches, splices and lashings "
                                             "(FM 5-125)"),
        ("key", "kmil:uscg_bch_seamanship_fundamentals", "The Coast Guard's Boat Crew Handbook: marlinspike "
                                                         "seamanship, line handling and splices"),
        ("key", "pdf:knight_modern_seamanship_1921", "Modern Seamanship (Knight, 1921): rope and knots on ships"),
        ("word", "knots-military", "Every military and Coast Guard knot, rope and pack manual (request word)"),
        ("pack", "commons_knots", "Knots by name, for the picture describer"),
        ("link", "The Ashley Book of Knots", "https://archive.org/details/ashleybookofknot00ashl",
         "Clifford Ashley's 1944 book is still in copyright; borrow it from a library"),
        ("link", "Animated Knots", "https://www.animatedknots.com/", "copyright; open it in a browser")]),
    ("Splicing, lashings, rope types and care", "Joining and finishing rope, lashing poles, and looking after rope.", [
        ("key", "knot:hasluck_knotting_splicing_1907", "Knotting and Splicing (Hasluck, 1907)"),
        ("key", "pdf:army_fm_5_125_rigging", "Fibre and wire rope, their care and inspection (FM 5-125)"),
        ("key", "kmil:army_manual_pack_transportation_1917", "Lash ropes, slings and the diamond hitch: the "
                                                             "Army's Manual of Pack Transportation (1917)"),
        ("key", "kmil:army_fm_25_7_pack_transportation_1944", "Lashed loads and pack hitches (FM 25-7, 1944)"),
        ("key", "bush:beard_shelters_shacks_shanties_1914", "Lashed shelters and camp building (Beard, 1914)"),
        ("pack", "commons_knots", "Lashings, seizings, splices, rope making and marlinespikes, for the picture "
                                  "describer"),
        ("pack", "open_images_knots_outdoor", "Wire rope, carabiners and tarps")]),
    ("Climbing, mountain and snow rope work", "Rope management, anchors, rappelling, rescue systems, avalanches "
     "and snow shelters. Learn these from a qualified instructor before you rely on them.", [
        ("key", "pdf:army_tc_3_97_61_mountaineering", "Military Mountaineering (TC 3-97.61)"),
        ("key", "kmil:usmc_mcrp_12_10a3_mountain_rope_work", "The Marine Corps mountain leader's rope, climbing, "
                                                             "rescue and survival chapters"),
        ("key", "kmil:usmc_mcrp_12_10a2_winter_operations", "The Marine Corps mountain leader's avalanche, ice, "
                                                            "skiing and snow shelter chapters"),
        ("word", "wilderness-first-aid", "Wilderness first aid and backcountry safety (request word)")]),
    ("Map and compass", "Reading a map, taking a bearing and finding your way.", [
        ("key", "pdf:army_fm_3_25_26_map_reading", "Map Reading and Land Navigation (FM 3-25.26)"),
        ("key", "pdf:usgs_topographic_map_symbols", "Topographic Map Symbols (USGS)"),
        ("pack", "commons_outdoor_skills", "Baseplate, lensatic and magnetic compasses")]),
    ("Fire, shelter and water", "Building a fire safely, simple shelters, and finding and treating water.", [
        ("key", "outcook:usfs_camping_food_bears", "Camping, campfires and bears (US Forest Service)"),
        ("key", "pdf:army_atp_3_50_21_survival", "The Army's survival manual: fire, shelter and water (ATP 3-50.21)"),
        ("key", "knot:boy_scouts_handbook_1914", "The Official Handbook for Boys (1914): campcraft"),
        ("key", "knot:miller_camp_craft_1915", "Camp Craft (1915)"),
        ("key", "bush:index", "Bushcraft and woodcraft: a guide to the old woodcraft classics and the survival "
                              "manuals' fire, shelter, water and navigation chapters"),
        ("word", "bushcraft", "The bushcraft and woodcraft books (request word)"),
        ("word", "preparedness", "Emergency preparedness books: water, shelter and kits"),
        ("link", "Leave No Trace Seven Principles", "https://lnt.org/why/7-principles/",
         "copyright of the Leave No Trace Center; open it in a browser")]),
    ("Axes, saws and sharpening", "Choosing, sharpening and using axes and saws safely.", [
        ("key", "knot:usfs_ax_manual", "An Ax to Grind: the Forest Service's axe manual"),
        ("key", "knot:usfs_crosscut_saw_manual", "Crosscut Saw Manual (Forest Service)"),
        ("key", "knot:usfs_saws_that_sing", "Saws That Sing: using crosscut saws (Forest Service)"),
        ("pack", "commons_outdoor_skills", "Axes, hatchets, saws, whetstones and knife sharpeners"),
        ("manuals", "outdoor_tools", "Axe, saw, knife, sharpener, compass and rope makers' manuals, as links")]),
]
INDEX = X.index_maker("knot", GROUP, "Knots and outdoor skills: a guide to the library", "Knots and outdoor skills",
                      "A guide to the library on knots and outdoor skills: knots by name and use, splicing, lashings "
                      "and rope care, map and compass, fire, shelter and water, and axes, saws and sharpening.",
                      SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("knot", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"knots-outdoor": lambda: ["knot:index"] + [f"knot:{g['name']}"
                                                                           for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "knots_usfs": "www.fs.usda.gov/t-d: works of the US Forest Service (17 U.S.C. 105, checked on govinfo.gov's "
                  "policies page at every build); robots.txt allows the pages and PDFs; no AI rules (checked "
                  "2026-11-22).",
    "knots_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                       "a later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                       "2026-11-22).",
    "knots_index": "The index (knot:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("The Ashley Book of Knots (Clifford W. Ashley, 1944)", "Still in copyright (renewed); link-only. The library has "
     "the public-domain knot books (Verrill, Aldridge, Hasluck) and the Army's FM 5-125. Index: "
     "https://archive.org/details/ashleybookofknot00ashl"),
    ("Animated Knots, NetKnots and other knot websites", "Copyright of their makers; link-only. Index: "
     "https://www.animatedknots.com/"),
    ("Current Boy Scout (Scouts BSA) and Girl Scout handbooks and merit badge pamphlets", "Copyright of the "
     "organisations; only the handbook printed before 1931 is built. Index: https://www.scouting.org/"),
    ("Boy Scouts of America, Official Handbook for Boys, 1911 first edition", "The Internet Archive's 1911 copy is a "
     "lending-library scan that cannot be downloaded; the 1914 printing is built. Index: "
     "https://archive.org/details/boyscoutsofameri0000vari_u4q6"),
    ("Leave No Trace Seven Principles", "\"(c) 1999 by the Leave No Trace Center for Outdoor Ethics\"; link-only. "
     "Index: https://lnt.org/why/7-principles/"),
    ("US Forest Service chainsaw, rigging and trail construction guides", "Chainsaws are power tools (the hardware "
     "and power tool collections); the Forest Service's Trail Construction and Maintenance Notebook and other T&D "
     "pages answered this build machine \"403\" (2026-11-22). Index: https://www.fs.usda.gov/t-d/"),
    ("Army TC 3-25.26 (2013) Map Reading and Land Navigation", "No Internet Archive copy was found (searched "
     "2026-11-22); FM 3-25.26 (2001), which it replaced, is in the library. Index: https://archive.org/search?query="
     "TC+3-25.26"),
    ("Navy Boatswain's Mate and Seaman rate training manuals after 1944 (marlinspike seamanship)", "The Internet "
     "Archive's Seaman (1981) and Boatswain's Mate 3 & 2 (1959) are lending-library scans that cannot be downloaded "
     "(searched 2026-11-22); the 1944 Boatswain's Mate 2c is built whole, gunnery chapter included as history, and so "
     "is the Coast Guard's Boat Crew Handbook (both kmil:). Index: https://archive.org/search?query=boatswain%27s+mate"),
    ("Finding and treating water, shelters and survival kits", "The preparedness and disaster collections and the "
     "field manuals cover them; not repeated. Index: https://www.ready.gov/water"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
