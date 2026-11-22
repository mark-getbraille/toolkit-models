"""The collection "Small boats: boats, sailboats, trailers and marine engines (manuals)" (category key small_boats): the
owner's request of 2026-11-22 for a small boats collection. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (sailboats and dinghies,
            pontoon, bass and jon boats, rowboats, boat trailers and winches, inboard and sterndrive engines, bilge
            pumps, boat lifts and anchor windlasses). Outboard motors and personal watercraft are already searched by
            powersports, marine electronics by marine_electronics, and kayaks, canoes, paddle boards, inflatable
            boats and life jackets by outdoors, so those words are not repeated here;
  makers    the boat builders, sailboat builders, marine engine makers, trailer makers and the epoxy makers whose
            boat repair manuals boaters use: LINK-ONLY by the owner's rule, for the person (or the personal
            assistant) to open in a browser or fetch with Program Downloader; nothing is read from their sites;
  guidance  the guides the reference library builds in full (textbooks/small_boats.py and outdoors.py: the Navigation
            Rules, the Coast Guard's boating guide and boat crew handbooks, the boating regulations) and the
            copyright course books (Chapman, US Sailing, America's Boating Club) as links.

The safety notice is said first (NOTICE): life jacket, weather, float plan, cold water, never boating under the
influence, carbon monoxide from engines, fuel and ventilation, and epoxy and solvent safety.
"""

NOTICE = ("Read the safety section first. Wear a life jacket that fits, and make sure everyone aboard has one. Check "
          "the weather before you go, and file a float plan with someone ashore. Cold water kills: dress for the "
          "water, not the air. Never boat under the influence of alcohol or drugs. Engines make carbon monoxide: "
          "keep away from exhausts and keep a carbon monoxide alarm in any cabin; run the blower and sniff for fuel "
          "before starting an inboard engine. Epoxy, resins and solvents need ventilation, gloves, eye protection "
          "and a respirator: follow the safety data sheet. In an emergency call 911 or the Coast Guard on VHF "
          "channel 16.")

IA_WORDS = ["sailboat", "sail boat", "sailing dinghy", "dinghy", "pontoon boat", "bass boat", "jon boat", "rowboat",
            "boat trailer", "trailer winch", "inboard engine", "sterndrive", "stern drive", "mercruiser",
            "bilge pump", "boat lift", "anchor windlass", "boat owner's manual", "boat owners manual"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its page "
        "is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="small_boats", prefix="sb", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="boston-whaler", maker="Boston Whaler", type="boat owner's manual",
         library="https://www.bostonwhaler.com/", site="bostonwhaler.com"),
    dict(key="sea-ray", maker="Sea Ray", type="boat owner's manual", library="https://www.searay.com/",
         site="searay.com"),
    dict(key="bayliner", maker="Bayliner", type="boat owner's manual", library="https://www.bayliner.com/",
         site="bayliner.com"),
    dict(key="grady-white", maker="Grady-White", type="boat owner's manual", library="https://www.gradywhite.com/",
         site="gradywhite.com"),
    dict(key="tracker-boats", maker="Tracker Boats (White River Marine Group)", type="bass, jon and fishing boat "
         "owner's manual", library="https://www.trackerboats.com/", site="trackerboats.com"),
    dict(key="bennington", maker="Bennington", type="pontoon boat owner's manual",
         library="https://www.benningtonmarine.com/", site="benningtonmarine.com"),
    dict(key="catalina-yachts", maker="Catalina Yachts", type="sailboat owner's manual",
         library="https://www.catalinayachts.com/", site="catalinayachts.com"),
    dict(key="laserperformance", maker="LaserPerformance", type="sailing dinghy rigging guide",
         library="https://www.laserperformance.com/", site="laserperformance.com"),
    dict(key="mercury-marine", maker="Mercury Marine (Mercury and MerCruiser)", type="outboard, sterndrive and "
         "inboard engine owner's manual", library="https://www.mercurymarine.com/", site="mercurymarine.com"),
    dict(key="yamaha-outboards", maker="Yamaha Outboards", type="outboard motor owner's manual",
         library="https://www.yamahaoutboards.com/", site="yamahaoutboards.com"),
    dict(key="honda-marine", maker="Honda Marine", type="outboard motor owner's manual",
         library="https://marine.honda.com/", site="marine.honda.com"),
    dict(key="suzuki-marine", maker="Suzuki Marine", type="outboard motor owner's manual",
         library="https://www.suzukimarine.com/", site="suzukimarine.com"),
    dict(key="tohatsu", maker="Tohatsu", type="outboard motor owner's manual", library="https://www.tohatsu.com/",
         site="tohatsu.com"),
    dict(key="volvo-penta", maker="Volvo Penta", type="inboard and sterndrive engine operator's manual",
         library="https://www.volvopenta.com/", site="volvopenta.com"),
    dict(key="ez-loader", maker="EZ Loader", type="boat trailer owner's manual", library="https://www.ezloader.com/",
         site="ezloader.com"),
    dict(key="load-rite", maker="Load Rite Trailers", type="boat trailer owner's manual",
         library="https://www.loadrite.com/", site="loadrite.com"),
    dict(key="west-system", maker="West System (Gougeon Brothers)", type="epoxy boat repair and building manual",
         library="https://www.westsystem.com/", site="westsystem.com"),
]]

GUIDANCE = [
    dict(title="Amalgamated International and US Inland Navigation Rules (NOAA; built in full in the reference "
               "library: boat:noaa_navigation_rules)",
         url="https://nauticalcharts.noaa.gov/publications/coast-pilot/index.html", by="NOAA's Office of Coast Survey"),
    dict(title="A Boater's Guide to the Federal Requirements for Recreational Boats (US Coast Guard; built in full: "
               "outdoors:uscg_boaters_guide_federal_requirements)",
         url="https://uscgboating.org/recreational-boaters/", by="the US Coast Guard"),
    dict(title="Equipment and building standards for recreational boats (33 CFR 175 and 183, 46 CFR 25; built in "
               "full: boat:cfr_recreational_boat_rules)", url="https://www.ecfr.gov/current/title-33/chapter-I/"
                                                              "subchapter-S", by="the Office of the Federal Register"),
    dict(title="Small boats: a guide to the library (books, manuals and pictures; boat:index)",
         url="https://github.com/mark-getbraille/toolkit-models", by="the toolkit"),
    dict(title="Chapman Piloting and Seamanship (copyright; open it in a browser)",
         url="https://www.chapmanpiloting.com/", by="Hearst"),
    dict(title="Boating courses: America's Boating Club, US Sailing and the BoatUS Foundation (copyright; open them "
               "in a browser)", url="https://americasboatingclub.org/", by="America's Boating Club"),
]

CATEGORY = dict(
    name="Small boats: boats, sailboats, trailers and marine engines (manuals)",
    description="Sailboats and dinghies, pontoon, bass and jon boats, rowboats, boat trailers and winches, inboard "
                "and sterndrive engines, bilge pumps, boat lifts and windlasses: the Internet Archive's manuals, the "
                "boat, engine, trailer and epoxy makers' manual pages (links) and the US government's boating rules "
                "and guides. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
