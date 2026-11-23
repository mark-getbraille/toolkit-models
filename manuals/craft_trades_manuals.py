"""The craft trades' equipment in the manual library (the owner's request of 2026-11-23: beekeeping, glass blowing,
leather working, and clothing making and repair). categories.py adds the one collection and puts it under the heading
"Arts and crafts" (crafts_manuals.HEADING); build_manuals.py builds it. An INDEX of facts and links only: each manual
belongs to its maker.

  craft_trades_tools  leather working and glass working equipment and the hatter's steamer: leather sewing machines
                      (Tippmann Boss, Cobra), leather splitters, clicker presses and leather tools (Tandy Leather;
                      Weaver Leather is already a maker of pet_livestock_supplies), lampworking and glass-blowing
                      torches (Bethlehem Burners, Nortel), bead and glass annealers (Arrow Springs), and hat and
                      garment steamers (Jiffy Steamer).

Already elsewhere and not repeated: beekeeping equipment (homestead, with Mann Lake, Dadant and Betterbee), sewing
machines and sergers (sewing_textile), knitting machines, looms and old sewing machines (textile_craft_tools), glass
and pottery kilns (pottery_kilns) and jewellers' torches (jewellery_tools).

Every maker is LINK ONLY (their terms were not checked one by one, so nothing is read from their sites; each library
is listed for the person to open in a browser). The Internet Archive's manuals are searched with CRAFT_TRADES_WORDS,
none of them a word another collection searches. The safety notice is written into the index, for the toolkit to say
first.
"""

RULE = ("listed for the person to open in a browser; nothing is read from its site in this first version (its terms "
        "were not checked one by one)")
INDEX_LICENCE = "CC0 (facts and links); each manual belongs to its maker"

NOTICE = ("Read the safety section first. Leather knives, splitters, clicker presses and sewing machines can cut or "
          "crush fingers: keep hands clear of blades, dies and needles and unplug machines before adjusting them. "
          "Lampworking torches burn propane or natural gas with oxygen: leak-test fittings with soapy water, use "
          "flashback arrestors as the maker says, work with ventilation and wear eye protection made for glass work. "
          "Steamers and annealers are hot enough to burn at a touch.")

CRAFT_TRADES_WORDS = ["leather sewing machine", "harness sewing machine", "shoe repair machine", "shoe finisher",
                      "skiving machine", "leather splitter", "clicker press", "lampworking", "glass lathe",
                      "bead annealer", "hat steamer", "hat block"]


def _maker(key, maker, type_, library):
    """One maker of the collection, link only, with the shared fields."""
    return dict(prefix="ct", key=key, maker=maker, type=type_, library=library, types=[], documents="manuals",
                category="craft_trades_tools", access="link", reason=RULE)


MAKERS = [
    _maker("tippmann-boss", "Tippmann Industrial (Boss)", "leather sewing machine", "https://tippmannindustrial.com/"),
    _maker("leather-machine-cobra", "Leather Machine Co. (Cobra)", "leather sewing machine",
           "https://leathermachineco.com/"),
    _maker("tandy-leather", "Tandy Leather", "leather tools", "https://tandyleather.com/"),
    _maker("bethlehem-burners", "Bethlehem Burners", "lampworking and glass-blowing torch",
           "https://www.bethlehemburners.com/"),
    _maker("nortel-glass", "Nortel Manufacturing", "lampworking torch", "https://www.nortelglass.com/"),
    _maker("arrow-springs", "Arrow Springs", "bead and glass annealer", "https://arrowsprings.com/"),
    _maker("jiffy-steamer", "Jiffy Steamer", "hat and garment steamer", "https://jiffysteamer.com/"),
]

CATEGORY = dict(
    name="Craft trades: leather working, glass working and hat making equipment (manuals)",
    description="Leather sewing machines, splitters, clicker presses and leather tools, lampworking and glass-blowing "
                "torches, glass annealers and hat steamers: Tippmann Boss, Cobra, Tandy, Bethlehem, Nortel, Arrow "
                "Springs and Jiffy (links), with the Internet Archive's manuals.",
    kind="manuals", licence=INDEX_LICENCE, makers=MAKERS, ia=CRAFT_TRADES_WORDS, notice=NOTICE)
CATEGORIES = {"craft_trades_tools": CATEGORY}
