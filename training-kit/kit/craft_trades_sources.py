"""The CRAFT TRADES for the Picture Model Training Kit (the owner's request of 2026-11-23: beekeeping, glass blowing,
leather working, and clothing making and repair). This file lists:
  - the ready-made pack built in packs/craft_trades_packs.py (group "permissive"; the kit downloads it with
    prepare_pack): commons_craft_trades, the beekeeping equipment, glassblowing tools and furnaces, saddlery and leather
    carving, and tailors, hatters and milliners that no other collection pictures;
  - what was looked at and left out, with the reason (CRAFT_TRADES_NOT_INCLUDED);
  - which topic add-on holds it (CRAFT_TRADES_TOPICS): "crafts" (Arts and crafts).

The rest of these trades is already pictured: beehives, smokers, hive tools, extractors and beekeeping suits in the
homestead collections (homestead_sources.py), glassblowing, lampworking and stained glass in crafts_sources.py, and
leatherwork, shoemaking, cobblers, tailoring and sewing in home_crafts_sources.py.

Nothing here is re-shared by the kit's makers: the pack is downloaded by the kit on the user's own computer, only
when the user ticks its choice. Answers say only what the Commons category says, with one line on what the tool or
trade is and the safety note of its trade (the same words as the pack). Its pictures show working people (tailors,
hatters, saddlers, beekeepers), so it is not used for picture-making (CRAFT_TRADES_PICTURE_MAKING_OK is empty and
sources.py puts the key in NOT_FOR_PICTURE_MAKING).

    python -c "import sources, craft_trades_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

# The safety notes of the pack's answers (packs/craft_trades_packs.py says the same words).
BEE_NOTE = ("Bees sting: wear a veil and gloves and work calmly; anyone who has had a severe reaction to a sting "
            "should not work bees, and trouble breathing or swelling of the face or throat after a sting needs 911 "
            "at once. A lit smoker can start a grass fire: put it out in a closed metal can.")
GLASS_NOTE = ("Hot glass looks exactly like cold glass and burns badly: wear eye protection made for glass work, keep "
              "good ventilation, and let pieces cool where nobody will touch them.")
LEATHER_NOTE = ("Leather knives, awls and punches are very sharp: cut away from your body on a cutting mat; use dyes, "
                "cements and solvents with fresh air, away from flames.")

CRAFT_TRADES_SOURCES = [
    Source("commons_craft_trades", "Craft trades: beekeeping equipment (queen excluders, honey supers, hive frames, "
                                   "nucleus hives, pollen traps, uncapping tools), glassblowing pipes, glory holes, "
                                   "glass furnaces and lehrs, saddlers and saddle making, leather carving and swivel "
                                   "knives, tailors, hatters, milliners and hat blocks (Wikimedia Commons, "
                                   "ready-made pack)", COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10,
           prepare_pack, "about 220 MB"),
]
CRAFT_TRADES_PACK_KEYS = ("commons_craft_trades",)
# The kit topic that holds the pack (topics.py lists it; packs/test_craft_trades.py checks they match).
CRAFT_TRADES_TOPICS = {"crafts": CRAFT_TRADES_PACK_KEYS}
# People at work are in many of its pictures: not for picture-making.
CRAFT_TRADES_PICTURE_MAKING_OK = set()

CRAFT_TRADES_NOT_INCLUDED = {
    "Commons categories already in other packs": "Beehives, top-bar hives, bee smokers, hive tools, honey "
        "extractors and beekeeping suits (homestead), glassblowing, glassblowers and lampworking (crafts), "
        "leatherwork, shoemaking, cobblers, tailoring and dress forms (textile crafts): never asked twice.",
    "Commons Beekeeping equipment, Hatmaking, Millinery and Saddlery as whole categories": "Beekeeping equipment "
        "holds the homestead pack's own categories, so only its other parts are taken one by one; Hatmaking, "
        "Millinery and Saddlery have no category page on Commons (checked 2026-11-23).",
    "Sleeve boards, Scientific glassblowing and Skeps on Commons": "one or two files or none (counted 2026-11-23); "
        "too few for a useful share.",
    "Share-alike Commons files of these trades": "not built in this first version; the textile, crafts and "
        "homestead share-alike collections already hold leatherwork, glassblowing and beekeeping files.",
    "Beekeeping suppliers' and leather and glass makers' product photos": "their makers' copyright; not used.",
}
