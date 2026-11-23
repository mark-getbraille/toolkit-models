"""HOMESTEAD AND SELF-RELIANCE SKILLS for the Picture Model Training Kit (the owner's request of 2026-11-23), the picture
side of the reference books under the request word homestead-fill. This file lists:
  - the ready-made packs built in packs/homestead_fill_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_forge_traps_tanning, commons_homestead_stores and commons_stars_navigation;
  - the sources looked at for these subjects and left out, with the reason (HOMESTEAD_FILL_NOT_INCLUDED).

As in outdoor_cooking_sources.py, nothing here is re-shared by the kit's makers: each pack is downloaded by the kit on
the user's own computer from the kit's own release, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026 (Commons files CC0, public domain or CC BY only).

Answers say only what the Commons category's name says, and every answer ends with the note of its skill (forge,
horses, trap laws, tanning chemicals, meat temperatures, sharp blades, water, treated seed, fishing rules, the Sun
and old charts). The notes are the same words as the packs' (packs/test_homestead_fill.py checks). No picture of an
animal being killed or caught: the trap category is read only for historic traps in museums.

Picture-making (HOMESTEAD_FILL_PICTURE_MAKING_OK): the forge and trap tools and the star charts and instruments
(things); the stores pack is left out of picture-making because its sausage making and basketry pictures show people
at work. Topics: forge, traps, tanning and stores in "home" (homestead gear) and "crafts" (forge and basketry); the
stars and navigation instruments in "documents" (star charts are maps).

    python -c "import sources, homestead_fill_sources"      (from the kit folder: checks the file loads)
"""

from sources import Source, prepare_pack

# The safety notes, word for word as in packs/homestead_fill_packs.py.
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

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"

HOMESTEAD_FILL_SOURCES = [
    Source("commons_forge_traps_tanning", "Forge, traps and tanning: blacksmith's tools, hardies, swage blocks, "
                                          "horseshoes and farriery, historic traps in museums, fish and lobster "
                                          "traps, tanneries, with forge, trap law and tanning notes (Wikimedia "
                                          "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 700, 10, prepare_pack, "about 160 MB"),
    Source("commons_homestead_stores", "Homestead stores: seed libraries and the Svalbard seed vault, baskets and "
                                       "basketry, fishing and cast nets, sausage making, cleavers and "
                                       "butcher knives, water purification, with their safety notes (Wikimedia "
                                       "Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 900, 10, prepare_pack, "about 200 MB"),
    Source("commons_stars_navigation", "Stars and celestial navigation: constellations, star charts, celestial "
                                       "globes, sextants, octants and marine chronometers, with the Sun and old "
                                       "chart notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 700, 10, prepare_pack, "about 160 MB"),
]

# The collections a picture-making model may learn from: the tools and the star charts and instruments (things);
# never the stores pack, whose sausage making and basketry pictures show people at work.
HOMESTEAD_FILL_PICTURE_MAKING_OK = {"commons_forge_traps_tanning", "commons_stars_navigation"}

HOMESTEAD_FILL_NOT_INCLUDED = {
    "Commons categories already used by other packs": "Anvils, Forges and Meat grinders (hardware_packs), "
        "Blacksmithing (making_packs), Bellows (heating_packs), Mousetraps (chemical_packs), Leather "
        "(textile_crafts_packs), Seed packets (garden_packs), Seed drills (land_industry_packs), Ropewalks and "
        "Ropemaking (knots_outdoor_packs), Smokehouses (outdoor_cooking_packs) and Planispheres (science_packs): not asked "
        "twice.",
    "Commons categories that do not exist under the names tried (November 2026)": "Blacksmith tools, Blacksmith "
        "tongs, Farrier tools, Steel traps, Deadfalls, Hide scrapers, Tanning tools, Leather tanning, Seed saving, "
        "Seed banks, Seed storage, Net making, Rope makers, Star atlases, Octant (instrument), Nautical almanacs, "
        "Ceramic water filters, Biosand filters, Solar water disinfection, Beef cuts, Pork cuts, Sausage stuffers "
        "and Butchers' tools; Basket weaving, Rope making, Celestial charts and Star maps exist but hold no files.",
    "Commons Animals in leghold traps, Bear traps, Mole traps and Meat processing": "they show animals caught, killed "
        "or butchered, which the owner's rule leaves out; only historic traps in museums are used.",
    "Commons Fur traders": "mostly portraits of people in the fur trade, not the skills; left out.",
    "Open Images labels": "no Open Images pack was made for these skills: its Anvil and Forge labels are already "
        "asked by making_packs, and the Commons categories above name the things more exactly.",
    "USDA FSIS, NGA and state wildlife agency photo galleries": "fsis.usda.gov refuses programs (403); msi.nga.mil "
        "did not answer (503, 2026-11-23); state agencies' photos are under each state's own terms.",
}
