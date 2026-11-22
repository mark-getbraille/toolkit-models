"""The collection "Garden and lawn care (guides and manuals)" (category key garden_care), the owner's life-skills
request of 2026-11-22. categories.py adds it to CATEGORIES. Mowers, trimmers, blowers and other powered equipment are
the category lawn_garden (their repair belongs to the home repair collections); garden chemicals' labels are the
chemical categories.

What it lists, in plain words (an INDEX of facts and links only):
  ia             the Internet Archive's manual collections, searched by IA_WORDS (irrigation and sprinkler timers,
                 hose timers, soil testers and pH meters, seed starting kits, grow lights, indoor gardens, composters,
                 rain barrels, garden planters);
  public_guides  USDA Home and Garden Bulletins, each the Internet Archive's copy (US government works), kept only
                 when the item has a PDF: Lawn Weed Control with Herbicides (No. 123, 1971);
  makers         irrigation, soil-testing and indoor garden makers: link-only by the owner's rule (nothing is read);
  guidance       the USDA Plant Hardiness Zone Map and NRCS's soil health pages (in the reference library too), and
                 the Cooperative Extension directory.
"""

GARDEN_SAFETY = ("Read and follow every garden chemical's label; keep children and pets away until it is safe; wear "
                 "gloves. Unplug pumps, grow lights and timers before cleaning them, and keep outdoor electrics dry.")

IA_WORDS = ["sprinkler timer", "irrigation controller", "irrigation timer", "hose timer", "water timer",
            "drip irrigation", "soil tester", "soil test kit", "ph meter", "moisture meter", "seed starting",
            "grow light", "indoor garden", "aerogarden", "composter", "compost tumbler", "rain barrel",
            "greenhouse kit", "raised garden bed"]

RULE = ("by the owner's rule the maker's own guides and manuals are link-only: nothing is read from its site; its "
        "page is listed for the person to open")
_COMMON = dict(category="garden_care", prefix="gc", documents="guides and manuals", access="link", reason=RULE,
               types=[])
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="rain-bird", maker="Rain Bird", type="irrigation controllers and sprinklers",
         library="https://www.rainbird.com/homeowners/support", site="rainbird.com"),
    dict(key="orbit", maker="Orbit (B-hyve)", type="hose timers and irrigation controllers",
         library="https://www.orbitonline.com/pages/support", site="orbitonline.com"),
    dict(key="hunter", maker="Hunter Industries", type="irrigation controllers",
         library="https://www.hunterirrigation.com/support", site="hunterirrigation.com"),
    dict(key="melnor", maker="Melnor", type="hose timers and sprinklers", library="https://www.melnor.com/",
         site="melnor.com"),
    dict(key="luster-leaf", maker="Luster Leaf (Rapitest)", type="soil test kits and meters",
         library="https://www.lusterleaf.com/", site="lusterleaf.com"),
    dict(key="aerogarden", maker="AeroGarden", type="indoor gardens", library="https://aerogarden.com/support",
         site="aerogarden.com"),
    dict(key="gardeners-supply", maker="Gardener's Supply Company", type="planters, composters and seed starting",
         library="https://www.gardeners.com/how-to", site="gardeners.com"),
]]

GUIDANCE = [
    dict(title="USDA Plant Hardiness Zone Map (find your zone; in the reference library: garden:usda_hardiness_zones)",
         url="https://planthardiness.ars.usda.gov/", by="the US Department of Agriculture"),
    dict(title="Soil health (USDA NRCS; in the reference library: garden:nrcs_soil_health)",
         url="https://www.nrcs.usda.gov/conservation-basics/soil/soil-health", by="the US Department of Agriculture"),
    dict(title="Find your local Cooperative Extension office (USDA NIFA)",
         url="https://www.nifa.usda.gov/about-nifa/how-we-work/extension/cooperative-extension-system",
         by="the US Department of Agriculture"),
]

PUBLIC_GUIDES = [
    dict(ia="ERIC_ED159069", title="Lawn Weed Control with Herbicides (USDA Home and Garden Bulletin No. 123, 1971)",
         by="the US Department of Agriculture", year=1971, military=False),
]

CATEGORY = dict(
    name="Garden and lawn care (guides and manuals)",
    description="Garden and lawn care equipment that is not powered machinery: irrigation and sprinkler timers, hose "
                "timers, soil testers and pH meters, seed starting kits, grow lights and indoor gardens, composters, "
                "rain barrels, greenhouse kits and raised beds: the Internet Archive's manuals, a USDA bulletin, the "
                "makers' guides (links), and the USDA's zone map, soil health pages and extension directory.",
    kind="manuals", licence="CC0 (facts and links); the USDA bulletin is public domain; each other document belongs "
                            "to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, public_guides=PUBLIC_GUIDES, notice=GARDEN_SAFETY)
