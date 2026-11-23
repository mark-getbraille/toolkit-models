"""Picture packs for the thin HOMESTEAD AND SELF-RELIANCE SKILLS (the owner's request of 2026-11-23), the picture side
of textbooks/homestead_fill.py (hfill:). Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes once
with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

Why: the owner is blind and wants the picture describer (and his offline assistant) to recognise the tools and things
of these skills, blacksmith's tools and horseshoes, historic traps in museums, tanneries, seed libraries, baskets,
fishing nets, sausage making, constellations and star charts, sextants and chronometers, and to say
the safety rule that goes with each.

Answers say only what the source says (a Commons category's name), never a guess. No picture of an animal being
killed or caught: the leghold trap category is read only for files whose own words name a museum, a collection or an
old date, and never for files whose words name a dead, caught or bleeding animal (MUSEUM_TRAP_WORDS); the butchery
categories are tools and sausage making only. Every answer ends with the note of its skill (the same words in the
kit's homestead_fill_sources.py):
  FORGE_NOTE   hot metal, eye and ear protection, fumes, never heating galvanised metal.
  HORSE_NOTE   a horse can kick; shoeing is work for a trained farrier.
  TRAP_NOTE    traps are regulated: licence, seasons and legal traps from the state wildlife agency.
  TANNING_NOTE tanning chemicals are poisonous: gloves, eye protection, good air.
  MEAT_NOTE    USDA safe temperatures and keeping meat cold.
  KNIFE_NOTE   sharp blades: cut away from your body.
  WATER_NOTE   boil water 1 minute (3 above 6,500 feet) when unsure (CDC).
  SEED_NOTE    never eat treated seed.
  NET_NOTE     fishing nets and traps are regulated by state fishing rules.
  SUN_NOTE     never look at the Sun through a sextant or telescope without proper shades or a solar filter.
  NAV_NOTE     an old chart or instrument is not for navigation by itself.

The packs (HOMESTEAD_FILL_PACKS), all Wikimedia Commons (CC0, public domain or CC BY files only):
  commons_forge_traps_tanning  blacksmith's tools, hardies, swage blocks, horseshoes and farriery; historic leghold
                               traps in museums, fish traps and lobster traps; tanneries and leather tanning.
  commons_homestead_stores     seed libraries and the Svalbard Global Seed Vault; baskets and basketry; fishing nets
                               and cast nets; sausage making, cleavers and butcher knives; water purification.
  commons_stars_navigation     constellations, star charts, celestial globes, celestial navigation, sextants, octants
                               and marine chronometers.

Not repeated here (other packs ask them): Anvils and Forges (hardware_packs), Blacksmithing and the Open Images labels
Anvil and Forge (making_packs), Bellows (heating_packs), Mousetraps (chemical_packs), Leather (textile_crafts_packs),
Seed packets (garden_packs), Seed drills (land_industry_packs), Ropewalks and Ropemaking (knots_outdoor_packs), Meat
grinders (hardware_packs), Smokehouses (outdoor_cooking_packs), Planispheres and telescopes (science_packs) and the
fishing tackle of outdoors_packs. What was looked at and left out is in the kit's homestead_fill_sources.py
(HOMESTEAD_FILL_NOT_INCLUDED).

    python packs/homestead_fill_packs.py commons_stars_navigation --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

FORGE_NOTE = ("Forge safety: hot metal looks the same as cold, so treat all metal at the forge or anvil as hot; wear "
              "safety glasses and hearing protection, work with good air, and never heat galvanised (zinc-coated) "
              "metal, whose fumes cause metal fume fever.")
HORSE_NOTE = "Horses: a horse can kick; shoeing is skilled work for a trained farrier."
TRAP_NOTE = ("Trapping law: traps are regulated everywhere: check your state or provincial wildlife agency's rules on "
             "licences, trapper education, seasons and legal traps before setting any trap.")
TANNING_NOTE = ("Tanning: many tanning chemicals (old ones include arsenic and strong acids) are poisonous: wear gloves "
                "and eye protection and work with good air.")
MEAT_NOTE = ("Meat safety (USDA): keep meat at 40 F (4 C) or colder and cook it to a safe internal temperature checked "
             "with a food thermometer: whole cuts 145 F (63 C) with a 3-minute rest, ground meat and sausage 160 F "
             "(71 C), poultry 165 F (74 C).")
KNIFE_NOTE = "Sharp blades: keep them sharp and cut away from your body."
WATER_NOTE = ("Water safety (CDC): if you are not sure water is safe, bring it to a rolling boil for 1 minute (3 "
              "minutes above 6,500 feet), or treat it as the product's own directions say.")
SEED_NOTE = ("Seed: never eat or feed animals seed that has been treated (it is often dyed a bright colour and "
             "coated with a pesticide).")
NET_NOTE = "Fishing rules: nets and fish traps are regulated: check your state's fishing licence and gear rules."
SUN_NOTE = ("Never look at the Sun through a sextant, telescope or binoculars without the proper Sun shades or a solar "
            "filter: it can blind you instantly.")
NAV_NOTE = "An old chart, almanac or instrument is not for navigation by itself: use current charts and a backup."
ASK_WHAT = "What is this?"

# Only historic traps in museums or collections, never a trapped, dead or bleeding animal (the file's own words).
MUSEUM_TRAP_WORDS = re.compile(r"^(?!.*\b(dead|killed|caught|trapped|bleeding|blood|carcass|corpse|injured|in a "
                               r"trap|animals? in|cartoon|merrie|melodies|lobby card)\b).*\b(museums?|museo|museet|"
                               r"muzeum|folkemuseum|collectie|collezione|collection|wellcome|antique|historic\w*|"
                               r"1[5-8]\d\d|19[0-2]\d|1[5-9]th|jh\.?)\b", re.I | re.S)
# Commons "Tanning" may hold sun tanning: only files whose own words name leather, hides, skins or tanneries.
LEATHER_WORDS = re.compile(r"\b(leather|hides?|skins?|tanner(y|ies|s)?|tannin|tan ?yard|gerberei|tannerie|curtid\w*|"
                           r"conceria|looierij)\b", re.I)


def thing(category, words, notes="", deeper=False, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the notes)]), with a pattern when only files whose own words match may be taken."""
    spec = (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {notes}" if notes else ""))])
    return spec + (pattern,) if pattern else spec


# ----------------------------------------------------------------- Commons: forge, traps and tanning

FORGE_TRAPS_TANNING = [
    thing("Blacksmith's tools", "a blacksmith's tool, such as tongs, hammers, punches or fullers used at the forge",
          FORGE_NOTE),
    thing("Hardy tools", "a hardy tool, a cutting or shaping tool that fits the square hole of an anvil", FORGE_NOTE),
    thing("Swage blocks", "a swage block, a heavy iron block with holes and grooves for shaping hot metal",
          FORGE_NOTE),
    thing("Horseshoes", "a horseshoe, a shaped metal shoe nailed to a horse's hoof", HORSE_NOTE),
    thing("Farriery", "farriery, the trimming and shoeing of horses' hooves", f"{HORSE_NOTE} {FORGE_NOTE}"),
    thing("Leghold traps", "a leghold (foothold) trap, shown as a historic object", TRAP_NOTE,
          pattern=MUSEUM_TRAP_WORDS),
    thing("Fish traps", "a fish trap, a basket, pot or fence that fish swim into and cannot leave", NET_NOTE),
    thing("Lobster traps", "a lobster trap (lobster pot), a cage that lobsters enter for bait", NET_NOTE),
    thing("Tanneries", "a tannery, where hides and skins are made into leather", TANNING_NOTE),
    thing("Tanning", "leather tanning, turning hides and skins into leather", TANNING_NOTE, pattern=LEATHER_WORDS),
]

# ----------------------------------------------------------------- Commons: seeds, baskets, nets, meat and water

HOMESTEAD_STORES = [
    thing("Seed libraries", "a seed library, where gardeners borrow seed and return seed they have saved", SEED_NOTE),
    thing("Svalbard Global Seed Vault", "the Svalbard Global Seed Vault in Norway, which stores back-up copies of "
                                        "seed from the world's seed banks", SEED_NOTE),
    thing("Baskets", "a basket, a container woven from plant fibres, cane, willow or similar materials"),
    thing("Basketry", "basketry, the craft of weaving baskets", KNIFE_NOTE),
    thing("Fishing nets", "a fishing net", NET_NOTE),
    thing("Cast nets", "a cast net, a round weighted net thrown by hand over fish", NET_NOTE),
    thing("Sausage making", "sausage making: ground meat and seasoning stuffed into casings", MEAT_NOTE),
    thing("Cleavers", "a cleaver, a heavy broad knife for chopping meat and bone", KNIFE_NOTE),
    thing("Butcher knives", "a butcher knife, a large knife for cutting meat", KNIFE_NOTE),
    thing("Water purification", "water purification: making water safe to drink", WATER_NOTE),
]

# ----------------------------------------------------------------- Commons: stars and celestial navigation

STARS_NAVIGATION = [
    thing("Constellations", "a constellation, a named pattern of stars in the night sky, or a chart of one"),
    thing("Star charts", "a star chart, a map of the stars in the night sky"),
    thing("Celestial globes", "a celestial globe, a globe showing the stars and constellations on a sphere"),
    thing("Celestial navigation", "celestial navigation, finding a position from the Sun, Moon, planets and stars",
          f"{NAV_NOTE} {SUN_NOTE}"),
    thing("Sextants", "a sextant, an instrument for measuring the angle between a star, the Sun or the Moon and the "
                      "horizon", f"{SUN_NOTE} {NAV_NOTE}"),
    thing("Octants", "an octant, an older navigation instrument for measuring the height of the Sun or a star above "
                     "the horizon", f"{SUN_NOTE} {NAV_NOTE}"),
    thing("Marine chronometers", "a marine chronometer, a very accurate clock carried at sea for finding longitude",
          NAV_NOTE),
]


def build_commons_forge_traps_tanning(limit):
    """The commons_forge_traps_tanning pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(FORGE_TRAPS_TANNING, limit, "forgetrap")


def build_commons_homestead_stores(limit):
    """The commons_homestead_stores pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(HOMESTEAD_STORES, limit, "hstores")


def build_commons_stars_navigation(limit):
    """The commons_stars_navigation pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(STARS_NAVIGATION, limit, "starnav")


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
HOMESTEAD_FILL_PACKS = {
    "commons_forge_traps_tanning": (build_commons_forge_traps_tanning, COMMONS_LICENCE.format(
        what="blacksmith's tool, hardy, swage block, horseshoe, farriery, historic trap, fish trap, lobster trap and "
             "tannery")),
    "commons_homestead_stores": (build_commons_homestead_stores, COMMONS_LICENCE.format(
        what="seed library, seed vault, basket, fishing net, sausage making, cleaver, butcher knife and "
             "water purification")),
    "commons_stars_navigation": (build_commons_stars_navigation, COMMONS_LICENCE.format(
        what="constellation, star chart, celestial globe, celestial navigation, sextant, octant and chronometer")),
}
HOMESTEAD_FILL_LIMITS = {
    "commons_forge_traps_tanning": 700,    # 10 categories, few files in some (Swage blocks, Leghold traps)
    "commons_homestead_stores": 900,       # 10 categories
    "commons_stars_navigation": 700,       # 7 categories
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS): all three.
HOMESTEAD_FILL_COMMONS_KEYS = tuple(HOMESTEAD_FILL_PACKS)
# The Commons category specs of the packs (for the self-test).
HOMESTEAD_FILL_SPECS = FORGE_TRAPS_TANNING + HOMESTEAD_STORES + STARS_NAVIGATION


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a homestead skills pack builder.")
    parser.add_argument("key", choices=sorted(HOMESTEAD_FILL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = HOMESTEAD_FILL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
