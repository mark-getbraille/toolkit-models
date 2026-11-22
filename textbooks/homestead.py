"""Homesteading and small livestock for the reference library, in the group "Reference, homesteading" (the owner's
request of 2026-11-22). Keys: homestead (every book), homestead:<name>.

What this module builds, in plain words, each IN FULL:
  - the EPA's private well and septic system pages, every page (testing and protecting well water, what is in it,
    flooded wells; how a septic system works, caring for it, SepticSmart for homeowners), marked "personal use
    only" (the EPA's copyright statement, checked at every build, allows its documents for non-commercial, scientific
    and educational purposes);
  - the FDA's egg safety page (buying, storing, cooking and serving eggs safely), a US government work;
  - old public-domain livestock books from the Internet Archive (published before 1931; the builder checks each
    item's year at every build): Langstroth on the Hive and Honey Bee (the 1913 Dadant revision) and Root's ABC of
    Bee Culture (1905) for beekeeping; Lippincott's Poultry Production (1921) and Nourse's Turkeys, Ducks and Geese
    (1909); Holmes Pegler's Book of the Goat (1917) and Richards's Modern Milk Goats (1921); Practical Rabbit Keeping
    (1919); Dietrich's Swine (1910); Warren's Farm Management (1914) for the small-farm business. Each old book's
    description says what is out of date (medicines, breeds, methods and safety advice).
  Every book carries the animal handling and homestead safety note (SAFETY): calm handling and an escape route, hand
  washing after touching poultry (Salmonella), bee stings and allergies, testing well water every year, never
  entering a septic tank, and qualified electricians for power systems.

Already in the library and not repeated (said in each description where it matters): the USDA Farmers' Bulletins on
poultry, bees, goats, rabbits, sheep, pigs, fences and farm water (pub:usda_farmers_bulletins), the Internet Archive's
farming and livestock books by subject (the "farming" and "insects" topics of open_catalogues.py), the light
construction books for fences, sheds and shelters (build: keys, building_books.py), the animal medicine books
(the vet_medicines group, medications.py), home canning, cheese and smoking (cookbooks.py), gardening (garden:), and
the Energy Saver articles on solar and home energy (dir:energy_saver_articles) for off-grid power.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): university extension guides (copyright or
non-commercial), SARE and ATTRA books (their own terms), USDA APHIS "Defend the Flock" and the AMS egg grading manual
(addresses moved or refused), CDC's private well pages (cdc.gov refuses programs), and the makers' incubator and
equipment manuals (the manual collection homestead lists them as links).

Run from the repository's folder:
  python3 textbooks/homestead.py homestead:fda_egg_safety --out build/textbooks --limit 3
  python3 textbooks/homestead.py --list homestead
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "homestead"
GROUPS = {GROUP: "Reference, homesteading"}

# The safety note every book carries (the picture packs say the same things in packs/homestead_packs.py).
SAFETY = ("Safety: handle animals calmly and always keep an escape route; never step between a mother animal and her "
          "young, and be careful around bucks, rams, boars and roosters. Wash your hands after touching poultry, eggs "
          "or animal pens (Salmonella); keep children under 5 from handling chicks and ducklings. Anyone allergic to "
          "bee stings should keep their emergency medicine with them and not work bees alone. Test well water every "
          "year for bacteria and nitrates. Never enter a septic tank or manure pit: their gases can kill in minutes. "
          "Electrical, solar and generator wiring is work for a qualified electrician. In an emergency call 911.")
OLD_LIVESTOCK = ("Published in {year}: an old book whose medicines, feeds, breeds and methods are out of date (some "
                 "remedies it names are now known to be harmful or are banned); ask a veterinarian about animal "
                 "health and use the animal medicine books for current medicines.")
OLD_BEES = ("Published in {year}: an old book; hives, equipment and much of its advice still apply, but bee diseases, "
            "mites (Varroa came later) and their treatments have changed: follow current guidance and product "
            "labels.")
OLD_BUSINESS = ("Published in {year}: an old book; its prices, laws and figures are out of date, kept for its "
                "explanations of planning and keeping farm accounts.")

# ====================================================================== EPA (personal use) and FDA

EPA_TERMS = "EPA website copyright statement"
EPA_DISCLAIMER = "https://www.epa.gov/web-policies-and-procedures/epa-disclaimers"
EPA_TEXT = r"These documents may be freely distributed and used for non-commercial, scientific and educational purposes"
GUIDES = [
    dict(K.guide(GROUP, "epa_private_wells_septic", "Private wells and septic systems (EPA)", "Wells and septic "
                 "systems", "US Environmental Protection Agency (EPA)",
                 ["https://www.epa.gov/privatewells", "https://www.epa.gov/septic"],
                 r"^https://www\.epa\.gov/(privatewells|septic)(/(?!forms/)[a-z0-9-]+)*$",
                 "The EPA's pages for people with their own well or septic system, every page: protecting and testing "
                 "your well, potential well water contaminants and their effects, what to do after a flood, "
                 "well water and your health; how a septic system works, how to care for it (pumping, saving water, "
                 "what not to flush or pour down the drain, protecting the drain field), SepticSmart tips for "
                 "homeowners, and septic systems after a flood.",
                 "From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be "
                 "freely distributed and used for non-commercial, scientific and educational purposes\". " + SAFETY,
                 depth=1, units=[(r"/privatewells", "Private wells"), (r"/septic", "Septic systems")], limit=80),
         licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
         personal_use=True, urls=["https://www.epa.gov/privatewells/potential-well-water-contaminants-and-their-"
                                  "impacts", "https://www.epa.gov/septic/how-care-your-septic-system"]),
    K.us_web(GROUP, name="fda_egg_safety", title="Egg safety: what you need to know (FDA)", subject="Egg safety",
             publisher="US Food and Drug Administration (FDA)",
             source="https://www.fda.gov/food/buy-store-serve-safe-food/what-you-need-know-about-egg-safety",
             crawl=[("https://www.fda.gov/food/buy-store-serve-safe-food/what-you-need-know-about-egg-safety", 0)],
             urls=["https://www.fda.gov/food/buy-store-serve-safe-food/what-you-need-know-about-egg-safety"],
             pages=r"^https://www\.fda\.gov/food/buy-store-serve-safe-food/[a-z0-9-]+$", limit=5,
             description="The FDA's guide to eggs: buying them cold and clean, storing them at 40 F (4 C) or colder, "
                         "cooking eggs until the yolks and whites are firm and egg dishes to 160 F (71 C), serving "
                         "them safely, and who is most at risk from Salmonella.",
             notice="From the US Food and Drug Administration: a US government work (public domain). " + SAFETY),
]
ALLOWED = {EPA_TERMS: "non-commercial"}

# ====================================================================== old public-domain livestock books


def old(name, title, subject, publisher, archive, year, description, note=OLD_LIVESTOCK, country="United States"):
    """One old livestock book of the Internet Archive with the safety note in its notice."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, notice=SAFETY,
                    country=country)


PDFS = [
    old("langstroth_hive_honey_bee_1913", "Langstroth on the Hive and Honey Bee (revised by Dadant, 1913)",
        "Beekeeping", "C. P. Dadant (Dadant and Sons)", "cu31924003227679", 1913,
        "The classic beekeeping manual of the man who invented the movable-frame hive, as revised by the Dadants: "
        "the bees and their life, hives and frames, handling bees, swarms, queens, feeding, wintering, honey and wax.",
        note=OLD_BEES),
    old("root_abc_bee_culture_1905", "The ABC of Bee Culture (A. I. Root, 1905)", "Beekeeping",
        "A. I. Root Company", "CAT11016094", 1905,
        "An encyclopedia of beekeeping from A to Z: hives, extractors, smokers, swarming, queen rearing, honey plants, "
        "comb honey, wintering and bee diseases.", note=OLD_BEES),
    old("lippincott_poultry_production_1921", "Poultry Production (William Adams Lippincott, 1921)", "Poultry",
        "William Adams Lippincott (Lea and Febiger)", "cu31924001685431", 1921,
        "A college textbook on keeping chickens: breeds, the egg and incubation, brooding chicks, feeding, housing "
        "and coops, laying flocks, meat birds, culling, and marketing eggs and poultry."),
    old("nourse_turkeys_ducks_geese_1909", "Turkeys, Ducks and Geese (1909)", "Poultry: turkeys, ducks and geese",
        "Orange Judd Company", "turkeysducksgees00nour", 1909,
        "Raising turkeys, ducks and geese: breeds, housing, feeding, hatching and rearing the young, and marketing."),
    old("pegler_book_of_the_goat_1917", "The Book of the Goat (H. S. Holmes Pegler, 1917)", "Goats",
        "H. S. Holmes Pegler (The Bazaar, Exchange and Mart)", "cu31924003207986", 1917,
        "Keeping goats: the breeds, housing, feeding, milking, breeding, kidding and the goat's diseases.",
        country="United Kingdom"),
    old("richards_modern_milk_goats_1921", "Modern Milk Goats (Irmagarde Richards, 1921)", "Goats",
        "Irmagarde Richards (J. B. Lippincott)", "modernmilkgoatss00rich", 1921,
        "Dairy goats in America: breeds, buying a goat, housing, feeding, milking and milk, breeding and kids, and "
        "the goat as a home milk supply."),
    old("practical_rabbit_keeping_1919", "Practical Rabbit Keeping (1919)", "Rabbits", "Outing Publishing Company",
        "cu31924003171323", 1919,
        "Raising rabbits for meat and fur: breeds, hutches, feeding, breeding and litters, and common ailments."),
    old("dietrich_swine_1910", "Swine: Breeding, Feeding and Management (William Dietrich, 1910)", "Pigs",
        "William Dietrich (Sanders Publishing)", "swinebreedingfee00dietrich", 1910,
        "Raising pigs: breeds, the breeding herd, farrowing and young pigs, feeding, housing and pasture, and "
        "diseases."),
    old("warren_farm_management_1914", "Farm Management (G. F. Warren, 1914)", "Small-farm business",
        "G. F. Warren (Macmillan)", "farmmanagement00warruoft", 1914,
        "Running a farm as a business: choosing a farm and its kinds of farming, size, labour and equipment, "
        "livestock and crops in the farm plan, farm records and accounts, and renting or buying land.",
        note=OLD_BUSINESS),
]

COLLECTION = K.Collection("homestead", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"homestead": lambda: [f"homestead:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "homestead_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): \"These documents "
                     "may be freely distributed and used for non-commercial, scientific and educational purposes\": "
                     "personal use only. www.epa.gov's robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "homestead_fda": "www.fda.gov: a work of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at "
                     "every build); robots.txt allows the page (checked 2026-11-22).",
    "homestead_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, "
                           "so a later reprint is refused); archive.org's robots.txt allows the files (2026-11-22).",
}
NOT_INCLUDED = [
    ("University extension guides on chickens, egg handling, goats, sheep, rabbits, pigs and beekeeping (Penn State, "
     "Cornell, NC State, UC ANR and others)", "Each university's copyright or CC BY-NC-SA without a usable bulk route; "
     "none was confirmed open one by one. Link-only for the owner to fetch with Program Downloader. Index: "
     "https://extension.psu.edu/animals-and-livestock and https://poultry.extension.org/"),
    ("SARE books (Building Soils for Better Crops, Managing Cover Crops Profitably, the small-farm business guides) "
     "and ATTRA (NCAT) livestock guides", "Free to download, but under SARE's and NCAT's own terms, not an open "
     "licence that was found on their pages (checked 2026-11-22). Link-only. Index: https://www.sare.org/resources/ "
     "and https://attra.ncat.org/"),
    ("USDA APHIS Defend the Flock (poultry biosecurity) and the USDA AMS Egg Grading Manual", "Public domain, but the "
     "addresses answered \"404\" (moved) and APHIS refused programs earlier the same day (2026-11-22). Link-only. "
     "Index: https://www.aphis.usda.gov/ and https://www.ams.usda.gov/grades-standards/eggs"),
    ("USDA ARS Bee Research Laboratory and honey bee health pages", "Public domain, but www.ars.usda.gov did not answer "
     "the bee laboratory's pages within two minutes (2026-11-22). Link-only. Index: https://www.ars.usda.gov/"
     "northeast-area/beltsville-md-barc/beltsville-agricultural-research-center/bee-research-laboratory/"),
    ("CDC private well and drinking water pages", "Public domain under CDC's terms, but www.cdc.gov answered this build "
     "machine \"403\" (2026-11-22). The EPA's well pages are built. Link-only. Index: "
     "https://www.cdc.gov/drinking-water/about/about-private-wells.html"),
    ("DOE off-grid and stand-alone power pages", "Their old Energy Saver addresses answer \"404\" (removed); the Energy "
     "Saver articles still on energy.gov, including solar at home, are already built (dir:energy_saver_articles). "
     "Index: https://www.energy.gov/energysaver/"),
    ("USDA Farmers' Bulletins on poultry, bees, goats, rabbits, sheep, pigs, fences and farm water", "Already in the "
     "library by decade (pub:usda_farmers_bulletins). Index: https://archive.org/details/usda-farmersbulletin"),
    ("Incubator, brooder, beekeeping, fencing and solar equipment makers' manuals", "The makers' copyright; listed as "
     "links in the manual collection homestead. Index: https://www.brinsea.com/ and https://www.mannlakeltd.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
