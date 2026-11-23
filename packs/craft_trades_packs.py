"""A picture pack for the CRAFT TRADES (the owner's request of 23 November 2026: beekeeping, glass blowing, leather
working, and clothing making and repair). Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; the limit counts pictures.

Why only one pack: the trades are already well pictured elsewhere (the homestead pack has beehives, top-bar hives,
bee smokers, hive tools, honey extractors and beekeeping suits; the crafts pack has glassblowing, glassblowers,
lampworking and stained glass; the textile pack has leatherwork, shoemaking, cobblers, tailoring, dress forms and
sewing patterns). This pack fills only the clear gaps, with Commons categories no other pack file names (the self-test
packs/test_craft_trades.py checks it):
  commons_craft_trades  Wikimedia Commons (files CC0, public domain or CC BY only, checked file by file):
                        beekeeping equipment beyond the hive itself (queen excluders, honey supers, hive frames,
                        entrance reducers, nucleus hives, pollen traps, uncapping tools, hive scales, bee feeding and
                        beekeepers' protective clothing); the glassblower's tools and furnaces (blowpipes, glory holes,
                        glass furnaces, glass kilns and lehrs); saddlers, saddleries and saddle making, leather carving
                        and swivel knives; tailors and tailor shops, hatters, milliners and hat blocks.

Answers say only what the Commons category names, with one short line written here on what that tool, place or trade
is, and the safety note of its trade (the same words as the kit's craft_trades_sources.py):
  BEE_NOTE      stings and allergies (911), the smoker's fire;
  GLASS_NOTE    hot glass looks cold, eye protection, ventilation;
  LEATHER_NOTE  sharp knives and awls, dye and solvent fumes.
No maker, date, size or material is said unless the category itself says it.

What was looked at and left out is in the kit's craft_trades_sources.py (CRAFT_TRADES_NOT_INCLUDED).

    python packs/craft_trades_packs.py commons_craft_trades --limit 8      (prints a few rows: a quick check)
"""

import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other

ASK_WHAT = "What is this?"
BEE_NOTE = ("Bees sting: wear a veil and gloves and work calmly; anyone who has had a severe reaction to a sting "
            "should not work bees, and trouble breathing or swelling of the face or throat after a sting needs 911 "
            "at once. A lit smoker can start a grass fire: put it out in a closed metal can.")
GLASS_NOTE = ("Hot glass looks exactly like cold glass and burns badly: wear eye protection made for glass work, keep "
              "good ventilation, and let pieces cool where nobody will touch them.")
LEATHER_NOTE = ("Leather knives, awls and punches are very sharp: cut away from your body on a cutting mat; use dyes, "
                "cements and solvents with fresh air, away from flames.")


def thing(category, words, note="", deeper=False):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [("What is this?", "This is <words>."
    and the note)])."""
    return (category, deeper, [(ASK_WHAT, f"This is {words}." + (f" {note}" if note else ""))])


BEEKEEPING = [
    thing("Queen excluders", "a queen excluder, a grid that lets worker bees through but keeps the larger queen out "
                             "of the honey boxes", BEE_NOTE),
    thing("Honey supers", "a honey super, a box put on top of a hive for the bees to store honey in", BEE_NOTE),
    thing("Hive frames", "a hive frame, the removable wooden frame that holds a sheet of comb in a hive", BEE_NOTE),
    thing("Hive entrance reducers", "a hive entrance reducer, a strip that makes the hive entrance smaller", BEE_NOTE),
    thing("Nucleus hives", "a nucleus hive (a nuc), a small hive for a small new colony", BEE_NOTE),
    thing("Pollen traps", "a pollen trap, fitted at a hive entrance to collect pollen from returning bees", BEE_NOTE),
    thing("Uncapping tools", "an uncapping tool, used to cut the wax caps off honeycomb before extracting honey"),
    thing("Beehive scales", "a beehive scale, which weighs a hive to follow the honey flow"),
    thing("Feeding bees", "bees being fed, usually with sugar syrup in a feeder", BEE_NOTE),
    thing("Personal protective equipment for beekeeping", "beekeepers' protective clothing: veils, suits and gloves",
          BEE_NOTE),
]
GLASSWORK = [
    thing("Glassblowing tools", "a glassblower's tools", GLASS_NOTE),
    thing("Pipes (glassblowing)", "a glassblowing pipe (blowpipe), the long tube used to gather and blow molten glass",
          GLASS_NOTE),
    thing("Glory holes", "a glory hole, the small furnace a glassblower reheats work in", GLASS_NOTE),
    thing("Glass furnaces", "a glass furnace, which melts the glass", GLASS_NOTE),
    thing("Glass kilns", "a glass kiln, for fusing, slumping or annealing glass", GLASS_NOTE),
    thing("Lehr (glassmaking)", "a lehr, the long oven in which glass is cooled slowly (annealed) so it does not "
                                "crack", GLASS_NOTE),
]
LEATHERWORK = [
    thing("Saddlers", "a picture of saddlers (people who make and repair saddles and harness) or their work",
          LEATHER_NOTE),
    thing("Saddleries", "a saddlery, a saddler's shop or workshop", LEATHER_NOTE),
    thing("Manufacture of saddles", "saddles being made", LEATHER_NOTE),
    thing("Leather carving", "leather carving, cutting and tooling a pattern into leather", LEATHER_NOTE),
    thing("Swivel knives", "a swivel knife, the leather carver's knife with a turning blade", LEATHER_NOTE),
]
CLOTHING_TRADES = [
    thing("Tailors", "a picture of tailors (people who make and alter clothes to measure) or their work"),
    thing("Tailor shops", "a tailor's shop"),
    thing("Hatters", "a picture of hatters (people who make or sell hats) or their shop"),
    thing("Milliners", "a picture of milliners (people who make and trim hats) or their shop"),
    thing("Hat blocks", "a hat block, a wooden form on which a hat is shaped"),
    thing("Hat block making", "hat blocks being made"),
]


def build_commons_craft_trades(limit):
    """The commons_craft_trades pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(CRAFT_TRADES_SPECS, limit, "crafttrades")


COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
CRAFT_TRADES_SPECS = BEEKEEPING + GLASSWORK + LEATHERWORK + CLOTHING_TRADES
CRAFT_TRADES_PACKS = {
    "commons_craft_trades": (build_commons_craft_trades, COMMONS_LICENCE.format(
        what="beekeeping equipment, glassblowing tool and furnace, saddlery, leather carving, tailor, hatter and "
             "milliner")),
}
CRAFT_TRADES_LIMITS = {
    "commons_craft_trades": 1000,   # 27 categories, most with a few dozen files
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
CRAFT_TRADES_COMMONS_KEYS = ("commons_craft_trades",)


def main(argv=None):
    """Build the pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try the craft trades pack builder.")
    parser.add_argument("key", choices=sorted(CRAFT_TRADES_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = CRAFT_TRADES_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
