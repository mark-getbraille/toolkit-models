"""The collection "Cleaning machines and household management (manuals)" (category key household_cleaning): the owner's
request of 2026-11-22 for cleaning and household management. practical_manuals.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (vacuum cleaners, robot
            vacuums, carpet and steam cleaners, steam mops and floor scrubbers; wet and dry vacs and air purifiers
            are searched by other collections);
  makers    the vacuum and floor-care makers (Hoover, Bissell, Dyson, Shark, iRobot, Eureka, Miele, Kärcher, Oreck):
            by the owner's rule LINK-ONLY, for the person (or the personal assistant) to open in a browser or fetch
            with Program Downloader; nothing is read from their sites;
  guidance  the guides the reference library builds in full (FDA kitchen food safety, the EPA's Safer Choice, the
            CPSC's home safety checklist) and the pages that refuse programs (FMCSA's Protect Your Move, CPSC's
            safety guides), as links.

The cleaning product labels and safety data sheets are the collection household_cleaners; this one is the machines
and household management. The notice is said first (NOTICE): never mix cleaners.
"""

NOTICE = ("Never mix cleaning products: bleach mixed with ammonia, or with acids such as some toilet bowl and rust "
          "cleaners or vinegar, makes poisonous gas. Use one product at a time with fresh air and follow the label. "
          "Unplug a vacuum or cleaner before clearing a blockage or changing a brush or filter.")

IA_WORDS = ["vacuum cleaner", "upright vacuum", "canister vacuum", "stick vacuum", "robot vacuum", "roomba",
            "carpet cleaner", "carpet shampooer", "steam cleaner", "steam mop", "floor scrubber"]

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is "
        "listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="household_cleaning", prefix="hc", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="hoover", maker="Hoover", type="vacuum and carpet cleaner",
         library="https://hoover.com/", site="hoover.com"),
    dict(key="bissell", maker="Bissell", type="vacuum, carpet cleaner and steam mop",
         library="https://www.bissell.com/",
         site="bissell.com"),
    dict(key="dyson", maker="Dyson", type="vacuum and air purifier", library="https://www.dyson.com/support",
         site="dyson.com"),
    dict(key="shark", maker="Shark (SharkNinja)", type="vacuum, robot vacuum and steam mop",
         library="https://www.sharkclean.com/", site="sharkclean.com"),
    dict(key="irobot", maker="iRobot", type="Roomba robot vacuum and Braava mop",
         library="https://homesupport.irobot.com/",
         site="irobot.com"),
    dict(key="eureka", maker="Eureka", type="vacuum", library="https://www.eureka.com/", site="eureka.com"),
    dict(key="miele", maker="Miele", type="vacuum", library="https://www.mieleusa.com/", site="mieleusa.com"),
    dict(key="karcher", maker="Kärcher", type="steam cleaner, floor cleaner and wet and dry vac",
         library="https://www.kaercher.com/", site="kaercher.com"),
    dict(key="oreck", maker="Oreck", type="vacuum and air purifier",
         library="https://www.oreck.com/", site="oreck.com"),
]]

GUIDANCE = [
    dict(title="Food safety in the home kitchen (FDA; built in full in the reference library: "
               "house:fda_kitchen_food_safety)",
         url="https://www.fda.gov/food/buy-store-serve-safe-food/safe-food-handling",
         by="the US Food and Drug Administration"),
    dict(title="Safer Choice: choosing safer cleaning products (EPA; in the reference library, personal use: "
               "house:epa_safer_choice)", url="https://www.epa.gov/saferchoice", by="the US Environmental Protection "
                                                                                    "Agency"),
    dict(title="Protect Your Move: your rights when you hire movers (FMCSA; open it in a browser: it refuses programs)",
         url="https://www.fmcsa.dot.gov/protect-your-move", by="the Federal Motor Carrier Safety Administration"),
    dict(title="Home safety guides (CPSC; open them in a browser: it refuses programs)",
         url="https://www.cpsc.gov/Safety-Education/Safety-Guides", by="the US Consumer Product Safety Commission"),
    dict(title="Poison Control (1-800-222-1222 in the US)", url="https://www.poison.org/",
         by="America's Poison Centers"),
]

CATEGORY = dict(
    name="Cleaning machines and household management (manuals)",
    description="Vacuum cleaners, robot vacuums, carpet and steam cleaners, steam mops and floor scrubbers: the "
                "Internet Archive's manuals, the makers' manual pages (links), and the government's kitchen hygiene, "
                "safer cleaner, moving and home safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
