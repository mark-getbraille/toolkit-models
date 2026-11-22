"""Gardening and lawn care for the reference library, in the group "Reference, gardening and lawn care" (the owner's
request of 2026-11-22). Keys: gardening (every book), garden:<name>.

What this module builds, in plain words:
  - the USDA Plant Hardiness Zone Map's own pages (Agricultural Research Service): what the zones mean, how to use
    the maps, how the map was made, and the downloads, every page;
  - NRCS soil health pages (Natural Resources Conservation Service): the principles of soil health, cover crops,
    soil testing and soil health on cropland, pasture, range and forest land, every page;
  - "Lawn Weed Control with Herbicides" (USDA Home and Garden Bulletin No. 123, 1971), a US government work, whole
    from the Internet Archive's copy (ERIC), with today's note that the products named may no longer be sold;
  - old public-domain gardening books (published before 1931, checked on the Internet Archive's record at every
    build), each whole and marked out of date: The Vegetable Garden (Vilmorin-Andrieux, English edition of 1920),
    Garden Guide: the Amateur Gardener's Handbook (1917), Dwarf
    Fruit Trees (Waugh, 1906) and Lawns and Gardens (Jønns, 1897).
  (The USDA Farmers' Bulletins are pub:usda_farmers_bulletins, and the Internet Archive's gardening books by topic
  are open catalogue keys: not repeated. APHIS's pages are in pets_home.py.)

Every book starts with the safety note: read and follow every garden chemical's label, keep children and pets away
until it is safe, and wear gloves; local cooperative extension offices answer questions about your own garden.

Not built (NOT_INCLUDED): university cooperative extension guides ("All rights reserved", or AI readers shut out),
the RHS and the Old Farmer's Almanac (copyright), Pinterest, YouTube and forums.

Run from the repository's folder:
  python3 textbooks/gardening.py garden:usda_hardiness_zones --out build/textbooks
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import car_care as C  # noqa: E402 - old_book, the old public-domain book entry

GROUP = "garden"
GROUPS = {GROUP: "Reference, gardening and lawn care"}
SAFETY = ("Garden safety: read and follow every garden chemical's label, keep children and pets away until it is "
          "safe, and wear gloves. Your local cooperative extension office answers questions about your own garden.")

GUIDES = [
    K.guide(GROUP, "usda_hardiness_zones", "USDA Plant Hardiness Zone Map: what the zones mean (USDA ARS)",
            "Gardening zones", "Agricultural Research Service, US Department of Agriculture",
            "https://planthardiness.ars.usda.gov/",
            r"^https://planthardiness\.ars\.usda\.gov/(pages/[a-z0-9-]+|home)?$",
            "The USDA Plant Hardiness Zone Map's own pages, every page: what a hardiness zone is (the average "
            "coldest winter temperature, in 10-degree zones and 5-degree half zones), how to find your zone and use "
            "the maps, how the 2023 map was made, and the map downloads.",
            SAFETY + " A work of the US Department of Agriculture (public domain).", depth=1, limit=20),
    K.guide(GROUP, "nrcs_soil_health", "Soil health (USDA NRCS)", "Soil and compost",
            "Natural Resources Conservation Service, US Department of Agriculture",
            "https://www.nrcs.usda.gov/conservation-basics/soil/soil-health",
            r"^https://www\.nrcs\.usda\.gov/conservation-basics/soil/soil-health(/[a-z0-9-]+)?$",
            "NRCS's soil health pages, every page: the principles of soil health (keep the soil covered, disturb it "
            "less, keep living roots, more kinds of plants), cover crops, soil testing, soil carbon, soil health "
            "for water, and soil health on cropland, pasture, range and forest land.",
            SAFETY + " A work of the US Department of Agriculture (public domain).", depth=1, limit=40),
]
PDFS = [
    K.us_pdf(GROUP, name="usda_lawn_weed_control_1971", title="Lawn Weed Control with Herbicides (USDA Home and "
             "Garden Bulletin No. 123, 1971)", subject="Lawn weeds", publisher="US Department of Agriculture",
             archive="ERIC_ED159069", published="1971", version="Home and Garden Bulletin No. 123 (1971)",
             description="The USDA's bulletin on lawn weeds: identifying the common ones (crabgrass, dandelion, "
                         "plantain, chickweed, clover and others), mowing, watering and feeding a lawn so weeds "
                         "cannot take hold, and when weed killers are used.",
             notice=SAFETY + " A US government work of 1971: many of the weed killers it names are no longer "
                             "sold or allowed; follow today's product labels."),
    C.old_book(GROUP, "vilmorin_vegetable_garden_1920", "The Vegetable Garden (Vilmorin-Andrieux, 1920)",
               "Vegetable gardening (old book)", "vegetablegardeni00vilmrich", 1920,
               "The classic description of every garden vegetable of its time: each one's varieties, how it is "
               "sown, grown and harvested.", SAFETY),
    C.old_book(GROUP, "garden_guide_1917", "Garden Guide: the Amateur Gardener's Handbook (1917)",
               "Home gardening (old book)", "gardenguideamate00dickrich", 1917,
               "How to plan, plant and keep a home garden: soil, seeds, vegetables, flowers, lawns, fruit, pests "
               "and tools.", SAFETY),
    C.old_book(GROUP, "waugh_dwarf_fruit_trees_1906", "Dwarf Fruit Trees (Waugh, 1906)", "Fruit trees (old book)",
               "dwarffruittreest00waugrich", 1906,
               "Growing dwarf fruit trees in a garden: propagation, planting, pruning and general management.",
               SAFETY),
    C.old_book(GROUP, "lawns_and_gardens_1897", "Lawns and Gardens: How to Plant and Beautify the Home Lot (1897)",
               "Lawns (old book)", "lawnsgardenshowt00jn", 1897,
               "Making and keeping a lawn and planting a home garden, as it was done in the 1890s.", SAFETY),
]

COLLECTION = K.Collection("garden", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"gardening": lambda: [f"garden:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "garden_usda": "planthardiness.ars.usda.gov and www.nrcs.usda.gov: works of the US government (17 U.S.C. 105, "
                   "checked on govinfo.gov's policies page at every build); robots.txt allows the pages; no AI rules "
                   "(checked 2026-11-22). The old books and the 1971 bulletin: the Internet Archive's copies (its "
                   "robots.txt allows the files), the old ones checked to be published before 1931 at every build.",
}
NOT_INCLUDED = [
    ("University cooperative extension gardening guides (for example Minnesota, Penn State, Illinois, Cornell)",
     "Each university's copyright (\"All rights reserved\"), or their sites shut out AI readers (checked "
     "2026-11-22); a few are CC BY-NC-SA but in no form a program may collect. Link-only: find your state's office "
     "at the index. Index: https://www.nifa.usda.gov/about-nifa/how-we-work/extension/cooperative-extension-system"),
    ("Royal Horticultural Society and the Old Farmer's Almanac planting calendars", "Copyright (checked 2026-11-22). "
     "Link-only. Index: https://www.rhs.org.uk/advice and https://www.almanac.com/gardening/planting-calendar"),
    ("USDA PLANTS Database (plants.usda.gov)", "A JavaScript application; its plant profiles are reached through its "
     "data downloads, not pages (link-only). Index: https://plants.usda.gov/"),
    ("The Principles and Practice of Pruning (Kains, 1917)", "The Internet Archive's record of its scan "
     "(principlespracti00kainrich) gives no publication year, so the builder cannot confirm it is from before 1931 "
     "(checked 2026-11-22). Index: https://archive.org/details/principlespracti00kainrich"),
    ("Pinterest, YouTube gardening videos, Instructables, Reddit and garden forums", "Not read (the owner's rule: their terms forbid scraping, or the "
     "pictures and text are their users' own). Index: https://www.youtube.com/results?search_query=gardening"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
