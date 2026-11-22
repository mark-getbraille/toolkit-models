"""The collection "Fishing, paddling, hiking and outdoor recreation gear (manuals)" (category key outdoors): the
owner's request of 2026-11-22 for outdoor recreation. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (fishing reels and rods,
            kayaks, canoes, paddle boards, inflatable boats, life jackets, trail cameras, handheld GPS receivers,
            binoculars, spotting scopes, rangefinders, tree stands and hunting blinds,
            snowshoes, ski bindings and cycling computers). Outboard motors, marine electronics and camping gear are
            already searched by powersports, marine_electronics and camping_outdoor; firearms and bows are not listed
            here (the firearms collection keeps its own rules);
  makers    the fishing, paddling, boating and outdoor gear makers: LINK-ONLY by the owner's rule;
  guidance  the US government pages the reference library builds in full (textbooks/outdoors.py: the Coast Guard's
            boating handbook and safety pages, the Forest Service's and Park Service's safety pages).

The safety notice is said first (NOTICE): life jackets, cold water, ice, telling someone your plan, and the firearm
line used everywhere in the toolkit for tree stands and blinds.
"""

NOTICE = 'Read the safety section first. Wear a life jacket on the water and make sure it fits; cold water is dangerous even for strong swimmers. Never go on ice unless it is known to be thick enough. Tell someone where you are going. In a tree stand always wear a full-body safety harness attached to the tree. Treat every gun as loaded, and keep your fingers away from the trigger.'

IA_WORDS = ["fishing reel", "spinning reel", "baitcasting reel", "fly reel", "fishing rod", "kayak", "canoe", "paddle board", "inflatable boat", "life jacket", "personal flotation", "trail camera", "game camera", "handheld gps", "gps receiver", "binoculars", "spotting scope", "rangefinder", "tree stand", "hunting blind", "snowshoe", "ski binding", "cycling computer", "bike computer"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="outdoors", prefix="od", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="penn", maker="PENN Fishing (Pure Fishing)", type="fishing reels", library="https://www.pennfishing.com/", site="pennfishing.com"),
    dict(key="shimano-fishing", maker="Shimano Fishing", type="fishing reels and rods", library="https://fish.shimano.com/", site="fish.shimano.com"),
    dict(key="abu-garcia", maker="Abu Garcia (Pure Fishing)", type="baitcasting and spinning reels", library="https://www.abugarcia.com/", site="abugarcia.com"),
    dict(key="daiwa", maker="Daiwa", type="fishing reels and rods", library="https://daiwa.us/", site="daiwa.us"),
    dict(key="old-town", maker="Old Town Canoe and Kayak", type="canoes and kayaks", library="https://www.oldtowncanoe.com/", site="oldtowncanoe.com"),
    dict(key="pelican", maker="Pelican Sport", type="kayaks and paddle boards", library="https://www.pelicansport.com/", site="pelicansport.com"),
    dict(key="hobie", maker="Hobie", type="pedal kayaks", library="https://www.hobie.com/", site="hobie.com"),
    dict(key="stearns", maker="Stearns", type="life jackets", library="https://www.stearnsflotation.com/", site="stearnsflotation.com"),
    dict(key="garmin-outdoor", maker="Garmin (outdoor and fitness)", type="handheld GPS and cycling computers", library="https://support.garmin.com/", site="garmin.com"),
    dict(key="bushnell", maker="Bushnell", type="binoculars, rangefinders and trail cameras", library="https://www.bushnell.com/", site="bushnell.com"),
    dict(key="vortex", maker="Vortex Optics", type="binoculars and spotting scopes", library="https://vortexoptics.com/", site="vortexoptics.com"),
    dict(key="msr-snowshoes", maker="MSR (snowshoes)", type="snowshoes", library="https://www.msrgear.com/snowshoes", site="msrgear.com"),
    dict(key="summit-stands", maker="Summit Treestands", type="tree stands", library="https://www.summitstands.com/", site="summitstands.com"),
]]

GUIDANCE = [
    dict(title="A Boater's Guide to the Federal Requirements for Recreational Boats (US Coast Guard; built in full: outdoors:uscg_boaters_guide_federal_requirements)",
         url="https://uscgboating.org/recreational-boaters/", by="the US Coast Guard"),
    dict(title="Outdoor safety on the national forests (US Forest Service; in the reference library: outdoors:usfs_know_before_you_go)",
         url="https://www.fs.usda.gov/visit/know-before-you-go", by="the US Forest Service"),
    dict(title="Hiking safety and accessibility (National Park Service; in the reference library: outdoors:nps_hiking_birding_accessibility)",
         url="https://www.nps.gov/subjects/trails/hiking-safety.htm", by="the National Park Service"),
    dict(title="Treestand safety (Treestand Manufacturers Association; copyright, open it in a browser)",
         url="https://www.tmastands.com/", by="the Treestand Manufacturers Association"),
]

CATEGORY = dict(
    name='Fishing, paddling, hiking and outdoor recreation gear (manuals)',
    description="Fishing reels and rods, kayaks, canoes, paddle boards, inflatable boats, life jackets, trail cameras, handheld GPS receivers, binoculars, spotting scopes and rangefinders, tree stands and blinds, snowshoes, ski bindings and cycling computers: the Internet Archive's manuals, the makers' manual pages (links) and the US government's boating and outdoor safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
