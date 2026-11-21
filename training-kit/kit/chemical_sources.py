"""HOUSEHOLD AND GARAGE PRODUCTS AND CHEMICALS for the Picture Model Training Kit: the collection that cannot be a
ready-made pack because of its licence, and the ones that were looked at and left out. The open ones (Commons
products in their containers with safety notes, finishes and corrosion as they look applied or in use, and WHMIS,
DOT and NFPA hazard symbols) are packs in packs/chemical_packs.py; Amazon's catalogue photos of cleaners, laundry
detergent and motor oil are in abo_packaged_goods (packs/packaged_goods_packs.py), now with safety notes.

As in street_scene_sources.py, nothing here is re-shared by the kit's makers: the collection is downloaded by the kit
on the user's own computer, straight from Wikimedia Commons, only when the user ticks the share-alike choice. Every
licence was checked at its source in November 2026.

The collection (CHEMICAL_SOURCES):
  share-alike
    chemical_commons_sa   Wikimedia Commons files under CC BY-SA or GFDL of the open packs' main categories:
                          cleaners and detergents, fertilisers and weed killers, paint and spray cans, motor oil and
                          lubricants, antifreeze, glues and sealants, solvents, mousetraps and bait stations,
                          batteries, propane cylinders and fuel cans, and rust, corrosion, galvanised and
                          powder-coated metal and wood finishes. Captions CC0. Hazardous products' answers end with
                          the same safety notes as the open pack.

Looked at and not included (CHEMICAL_NOT_INCLUDED, with the reason).

    python -c "import sources, chemical_sources"      (from the kit folder: checks the file loads)
"""

import os
import re

from home_sources import commons_sa_items
from more_sources import fetch_shared
from extra_sources import say
from sources import Source

# Words that leave a share-alike file out: poisonings, injuries, deaths, drug labs, explosives and weapons.
HARM = re.compile(r"\b(poison(ed|ing)s?|overdoses?|suicides?|killed|dead|deaths?|died|fatal\w*|injur\w*|wounded|"
                  r"blood\w*|meth labs?|drug labs?|explosives?|bombs?|napalm|chemical weapons?|weapons?|arson|"
                  r"molotov)\b", re.I)

WHAT_Q = "What is this?"
FINISH_Q = "What finish is on this?"
SURFACE_Q = "What does this surface look like?"
KEEP_AWAY = "Keep it away from children and pets"


def spec(category, question, answer, deeper=True):
    """(category, question, answer, also one level of its subcategories) for home_sources.commons_sa_items."""
    return (category, question, answer, deeper)


CHEMICAL_SA = [
    spec("Bleach bottles", WHAT_Q, "This is a bottle of bleach. Keep it away from children and pets. Never mix bleach "
                                   "with ammonia, vinegar, acids or other cleaners: together they give off toxic "
                                   "gas.", False),
    spec("Toilet cleaners", WHAT_Q, "This is a toilet cleaner. It is corrosive: it can burn skin and eyes. Wear "
                                    "gloves, keep it away from children, and never mix it with other cleaners."),
    spec("Detergents", WHAT_Q, f"This is a picture of a detergent (a soap-like cleaner). {KEEP_AWAY}, and do not "
                               "mix it with other cleaners."),
    spec("Cleaning products", WHAT_Q, f"This is a picture of household cleaning products. {KEEP_AWAY}, use them "
                                      "with fresh air, and do not mix them with other cleaners."),
    spec("Fertilizers", WHAT_Q, f"This is a picture of fertiliser: plant food spread on soil or lawns. {KEEP_AWAY}, "
                                "and wash your hands after using it."),
    spec("Herbicides", WHAT_Q, "This is a picture of a weed killer (herbicide): the product, its container or its "
                               "use. Read and follow its label, and keep children and pets away until it has "
                               "dried."),
    spec("Paint cans", WHAT_Q, "This is a can of paint. Use it with fresh air, and keep it away from children.",
         False),
    spec("Spray cans", WHAT_Q, "This is a spray can (an aerosol can), such as spray paint. It is under pressure and "
                               "often flammable: keep it away from heat and flames, and never puncture or burn it."),
    spec("Motor oil", WHAT_Q, "This is motor oil (engine oil). Keep it away from children, wipe up spills, and take "
                              "used oil to a recycling point."),
    spec("Antifreeze", WHAT_Q, "This is antifreeze (engine coolant). It is poisonous and tastes sweet: keep it away "
                               "from children and pets, and wipe up every spill."),
    spec("Adhesives", WHAT_Q, "This is a picture of glue or another adhesive. Some glues bond skin in seconds: keep "
                              "them away from eyes and children."),
    spec("Turpentine", WHAT_Q, "This is turpentine, a solvent for thinning oil paint and cleaning brushes. It is "
                               "flammable: use it with fresh air, far from flames."),
    spec("Mousetraps", WHAT_Q, "This is a mousetrap."),
    spec("Rodent bait stations", WHAT_Q, "This is a rodent bait station. It holds poison: keep it away from "
                                         "children and pets.", False),
    spec("AA batteries", WHAT_Q, "These are household batteries. Do not throw batteries in the household bin: take "
                                 "them to a battery recycling point."),
    spec("Propane cylinders", WHAT_Q, "This is a propane cylinder (a propane tank). It is flammable gas under "
                                      "pressure: keep it upright, outdoors and away from heat."),
    spec("Jerrycans", WHAT_Q, "This is a jerrycan, a sturdy can for fuel or water."),
    spec("Rust", SURFACE_Q, "This shows rust: rough, flaky, orange-brown iron oxide that forms on iron and steel left "
                            "wet. It eats the metal away."),
    spec("Corrosion", SURFACE_Q, "This shows corroded metal: its surface is eaten away, pitted, crusted or "
                                 "discoloured."),
    spec("Hot-dip galvanizing", FINISH_Q, "This is galvanised steel: coated with zinc, a dull grey or silvery "
                                          "finish, often with a crystal pattern, that protects the steel from rust."),
    spec("Powder coating", FINISH_Q, "This metal is powder-coated: a tough, even, baked-on plastic paint, usually "
                                     "smooth and slightly glossy."),
    spec("Varnish", FINISH_Q, "This shows varnish: a clear, hard protective coat, usually glossy, over wood (in its "
                              "tin, or applied)."),
    spec("Shellac", FINISH_Q, "This shows shellac, a traditional wood finish that dries to a warm, amber, glossy "
                              "coat."),
]


def sa_items(specs, cap, test, prefix):
    """home_sources.commons_sa_items (files under CC BY-SA or GFDL, the categories sharing the cap, children left
    out), without the files whose words name a poisoning, an injury, a death, a drug lab, explosives or weapons."""
    items = commons_sa_items(specs, cap, test, prefix, adults_only=True)
    bad = {name for name, _, row in items if HARM.search(f"{name.replace('_', ' ')} {row['answer']}")}
    if bad:
        say(f"  {len(bad)} files left out by their words")
    return [i for i in items if i[0] not in bad]


def prepare_chemical_commons_sa(source, data_dir, work, cap):
    """Commons household chemical and finish categories, files under CC BY-SA or GFDL."""
    items = sa_items(CHEMICAL_SA, cap, source.test, "chem-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
CHEMICAL_SOURCES = [
    Source("chemical_commons_sa", "Wikimedia Commons: household and garage products (cleaners, fertilisers, weed "
                                  "killers, paint and spray cans, motor oil, antifreeze, glues, solvents, traps, "
                                  "batteries, propane) and finishes (rust, corrosion, galvanised and powder-coated "
                                  "metal, varnish, shellac), files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 1500, 15, prepare_chemical_commons_sa, "about 300 MB of pictures", terms=SA_TERMS,
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
]

# The collections a picture-making model may learn from: none (people appear in some of these photos).
CHEMICAL_PICTURE_MAKING_OK = set()

CHEMICAL_NOT_INCLUDED = {
    "Open Products Facts household chemicals (paints, glues, lubricants, pesticides, fertilisers)":
        "Its category counts in November 2026 were tiny (paints 3, adhesives 7, lubricants 8, fertilizers 5, "
        "insecticides 2, motor oils, antifreeze, varnishes and wood stains 0). Its cleaners and detergents were "
        "the share-alike openproductsfacts entry (home_sources.py), now not built: the source blocks AI crawlers "
        "(its robots.txt shuts out GPTBot, anthropic-ai and ClaudeBot).",
    "Open Images V7 classes for household chemicals":
        "Open Images has no class for a paint can, a chemical bottle, a spray can or a fuel can that people checked "
        "by hand (its packaging classes are open_images_packaged_goods'); nothing to add.",
    "Amazon Berkeley Objects garage and garden product types":
        "ABO holds Amazon's own brands only: no paints, pesticides, fertilisers, glues or automotive fluids beyond "
        "motor oil and a few glue sticks; its cleaners and motor oil are already in abo_packaged_goods, whose "
        "answers now carry safety notes. JANITORIAL_SUPPLY listings are abo_products' (things_packs.ABO_GENERAL), "
        "so they are not taken twice.",
    "Smithsonian Open Access (CC0) older household products":
        "Its API needs an api.data.gov key, which this build has not got; museum_general_packs and the kit's "
        "smithsonian entry already take its CC0 pictures.",
    "CPSC and Health Canada recall photos of chemical products":
        "The recalling firms' own photos, not public domain (see packaged_goods_sources.py).",
    "Water test strip colour charts (pool and aquarium)":
        "No open collection was found that records the reading of each strip in its own words; a strip's colour is "
        "never guessed, so none is described.",
}
