"""Pools, spas and hot tubs for the reference library, in the group "Reference, pools and spas" (the owner's request
of 2026-11-22). Keys: pools-spas (every book), pool:<name>.

What this module builds, in plain words:
  - pool:index, a guide to the library on pools, spas and hot tubs (the toolkit's own facts and links, CC0): water
    chemistry (chlorine, pH, alkalinity, cyanuric acid, shocking) and testing, equipment (pumps, filters, heaters,
    chlorinators), opening, closing and cleaning, safety (drowning prevention, drain entrapment, never mixing pool
    chemicals), hot tub care and safety, and Legionella, with the books by key, the picture pack, the manual
    collections and the links;
  - IN FULL: CDC's Healthy Swimming pages (pool and hot tub water, chlorine and pH, testing, recreational water
    illnesses), CDC's drowning prevention pages, CDC's Legionella pages (hot tubs and Legionnaires' disease) and the
    Model Aquatic Health Code pages, kept whole under CDC's terms; and two US military manuals on running pools and
    spas safely, read from the Internet Archive under the release rule for military publications: the Army's
    Swimming Pools and Bathing Facilities (TB MED 575, 1993: disinfection, pH, filtration, water testing and safety)
    and the Navy's Manual of Naval Preventive Medicine, chapter 4, Swimming Pools and Bathing Places (NAVMED P-5010-4,
    2002).
  Every book carries POOL_SAFETY in its notice (drowning prevention, drain covers, never mixing pool chemicals,
  chemical to water, hot tub temperature and Legionella).

Already in the library and not repeated: the pool and spa chemical labels and safety data sheets (the manual
collection pool_spa_chemicals), the household chemical picture packs (pool test kits, pool chemicals, algae in pools)
and the first aid and CPR books (first-aid).

Not built (NOT_INCLUDED, link-only): the CPSC's Pool Safely campaign (public domain, but poolsafely.gov and cpsc.gov
refuse programs and no Internet Archive copy was found), the Model Aquatic Health Code's PDF (CDC refuses this build
machine; its CDC pages are in pool:cdc_healthy_swimming when CDC answers), the Red Cross's water safety pages
(copyright), the Pool and Hot Tub Alliance's standards (sold) and the makers' manuals (links in the manual collection
pools_spas).

Run from the repository's folder:
  python3 textbooks/pools_spas.py pool:army_tb_med_575 --out build/textbooks --limit 3
  python3 textbooks/pools_spas.py --list pools-spas
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "pools"
GROUPS = {GROUP: "Reference, pools and spas"}

# The same safety words as packs/pools_spas_packs.py DROWNING_NOTE and POOL_CHEM_NOTE, written for a book.
POOL_SAFETY = ("Safety: never leave children alone in or near water, even for a moment; fence a pool on all four "
               "sides with a self-closing, self-latching gate; keep drain covers in place so no one is trapped by "
               "the suction; learn CPR. Keep pool chemicals dry, closed and away from children; never mix different "
               "pool chemicals, and add the chemical to water, never water to the chemical: they can catch fire or "
               "give off toxic gas. Keep a hot tub at 104 F (40 C) or below, and keep its disinfectant and pH in "
               "range to prevent Legionella.")
MILITARY_NOTICE = ("A work of the US armed forces (public domain); the builder says what its own front pages print "
                   "about distribution. Written for military pools: follow your state's and county's pool rules. ")

GUIDES = [
    X.cdc_site_book(GROUP, "cdc_healthy_swimming", "Healthy swimming: pool and hot tub water, chemicals, drowning "
                    "prevention and Legionella (CDC)", "Pool and hot tub safety",
                    ["healthy-swimming", "drowning", "legionella", "model-aquatic-health-code"],
                    "CDC's pages on pools, spas and hot tubs, every page: healthy swimming (keeping germs out of the "
                    "water, chlorine and pH, testing with test strips, pool chemical safety, hot tubs, recreational "
                    "water illnesses), drowning prevention (fences, supervision, life jackets, CPR), Legionella and "
                    "Legionnaires' disease (hot tubs and water systems), and the Model Aquatic Health Code (the "
                    "national guidance for public pools).", POOL_SAFETY,
                    units=[(r"/healthy-swimming", "Healthy swimming"), (r"/drowning", "Drowning prevention"),
                           (r"/legionella", "Legionella"), (r".", "Model Aquatic Health Code")]),
]

PDFS = [
    K.us_pdf(GROUP, name="army_tb_med_575", title="Swimming Pools and Bathing Facilities (TB MED 575, 1993)",
             subject="Pool operation and water treatment", publisher="Headquarters, Department of the Army",
             archive="DTIC_ADA355816", military=True, published="1993",
             version="TB MED 575, 1993 (Internet Archive item DTIC_ADA355816, the DTIC copy)",
             description="The Army's technical bulletin on running swimming pools and bathing places safely: "
                         "disinfection with chlorine and bromine, pH and alkalinity, filtration and recirculation, "
                         "water testing, cleaning, pool chemical storage and handling, lifeguards and safety rules, "
                         "and natural bathing places. Published in 1993: some limits and test methods have changed "
                         "(CDC's Model Aquatic Health Code is today's guidance).",
             notice=MILITARY_NOTICE + POOL_SAFETY),
    K.us_pdf(GROUP, name="navmed_p5010_4", title="Manual of Naval Preventive Medicine, Chapter 4: Swimming Pools and "
             "Bathing Places (NAVMED P-5010-4, 2002)", subject="Pool operation and water treatment",
             publisher="Department of the Navy, Bureau of Medicine and Surgery", archive="NAVMEDP50104", military=True,
             published="2002", version="NAVMED P-5010-4, June 2002 (Internet Archive item NAVMEDP50104)",
             description="The Navy's chapter on pools, spas and bathing places: design and operation, disinfection, "
                         "pH and water chemistry, filtration, water testing and records, hot tubs and spas, "
                         "chemical safety, and preventing illness and injury.",
             notice=MILITARY_NOTICE + POOL_SAFETY),
]

SECTIONS = [
    ("Water chemistry and testing", "Chlorine, pH, alkalinity, cyanuric acid, shocking and testing the water.", [
        ("key", "pool:cdc_healthy_swimming", "CDC's Healthy Swimming pages: chlorine, pH and test strips"),
        ("key", "pool:army_tb_med_575", "Swimming Pools and Bathing Facilities: disinfection, pH and testing (Army)"),
        ("key", "pool:navmed_p5010_4", "Swimming Pools and Bathing Places (Navy)"),
        ("manuals", "pool_spa_chemicals", "Pool and spa chemical labels and safety data sheets, as links"),
        ("pack", "commons_household_chemicals", "Pool chemicals and test kits, with the never-mix note")]),
    ("Equipment, opening, closing and cleaning", "Pumps, filters, heaters, chlorinators, cleaners and covers.", [
        ("pack", "commons_pool_equipment", "Pool pumps, sand filters, cleaners, covers, ladders and rescue hooks"),
        ("manuals", "pools_spas", "Pool, spa and hot tub makers' manuals and the Internet Archive's, as links")]),
    ("Safety: drowning, drains and chemicals", "Supervision, fences, drain covers, CPR and chemical safety.", [
        ("key", "pool:cdc_healthy_swimming", "CDC's drowning prevention pages"),
        ("word", "first-aid", "First aid and CPR books"),
        ("link", "Pool Safely (CPSC): drowning and drain entrapment prevention", "https://www.poolsafely.gov/",
         "public domain, but poolsafely.gov refuses programs; open it in a browser")]),
    ("Hot tubs and Legionella", "Hot tub temperature, disinfectant and Legionnaires' disease.", [
        ("key", "pool:cdc_healthy_swimming", "CDC's hot tub and Legionella pages")]),
]
INDEX = X.index_maker("pool", GROUP, "Pools, spas and hot tubs: a guide to the library", "Pools, spas and hot tubs",
                      "A guide to the library on pools, spas and hot tubs: water chemistry and testing, equipment, "
                      "opening, closing and cleaning, safety (drowning, drains and chemicals), and hot tubs and "
                      "Legionella.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("pool", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"pools-spas": lambda: ["pool:index"] + [f"pool:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "pools_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are public domain on "
                 "four conditions (credit, no endorsement, no change, free on CDC's site), met in the notice; the "
                 "pages are kept whole. www.cdc.gov answered this build machine \"403\" on 2026-11-22; the builder "
                 "asks robots.txt at every build and leaves the book out while CDC refuses.",
    "pools_military": "TB MED 575 (1993; the DTIC copy, as the other copy has no text layer) and NAVMED P-5010-4 "
                      "(2002): works of the US armed forces, read from the Internet Archive; the builder reads each one's front pages and follows the shared release rule "
                      "(military_release.py).",
    "pools_index": "The index (pool:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Pool Safely (CPSC): drowning and drain entrapment prevention, the Virginia Graeme Baker Pool and Spa Safety Act",
     "Public domain, but www.poolsafely.gov and www.cpsc.gov refuse programs (\"403\", 2026-11-22), and no Internet "
     "Archive copy was found (searched: pool safely, swimming pool safety). Link-only. Index: "
     "https://www.poolsafely.gov/"),
    ("CDC Model Aquatic Health Code (the code and its annex, PDF)", "Public domain, but www.cdc.gov refuses this build "
     "machine (\"403\", 2026-11-22) and the Internet Archive has only a web capture. Its CDC pages are in "
     "pool:cdc_healthy_swimming when CDC answers. Index: https://www.cdc.gov/model-aquatic-health-code/"),
    ("American Red Cross water safety and CPR pages", "\"(c) American Red Cross\"; link-only. Index: "
     "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/water-safety.html"),
    ("Pool and Hot Tub Alliance (PHTA) standards and the Certified Pool Operator course", "Copyright, sold. Index: "
     "https://www.phta.org/"),
    ("Makers' manuals (Pentair, Hayward, Jandy, Zodiac, Intex, Bestway, Jacuzzi, Hot Spring, Sundance and others)",
     "The makers' copyright; links in the manual collection pools_spas. Index: https://www.pentair.com/"),
    ("Extension guides on pool and hot tub care", "Copyright of each university (as for the other collections); "
     "link-only. Index: https://extension.psu.edu/"),
    ("Swimming lessons and swimwear", "Not wanted for this collection (equipment, chemistry and safety only). Index: "
     "https://www.cdc.gov/drowning/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
