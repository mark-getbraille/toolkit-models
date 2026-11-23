"""Homestead and self-reliance skills that the library was thin on, in the group "Reference, homesteading" (the
owner's request of 2026-11-23: fill the thin homestead and self-reliance areas). Keys: homestead-fill (every book),
hfill:<name>; one request word per area: seed-saving, butchering, trapping-tanning, blacksmithing, star-navigation,
water-purification and fibre-crafts. A sibling of homestead.py (homestead:), in the same group.

What this module builds, in plain words, each IN FULL:
  - hfill:index, a guide to these skills in the library (the toolkit's own facts and links, CC0): for each area the
    books here, the books already elsewhere in the library (by key, never copied twice: the USDA Farmers' Bulletins
    on slaughtering, curing, home tanning and saving seed, the 1961 Yearbook "Seeds", Bowditch, the CDC and EPA water
    pages and others), the picture packs, and the sources that are links only, with the reason;
  - seed saving: Brill's Farm-Gardening and Seed-Growing (1884), Johnson's The Seed Grower (1906) and the US Forest
    Service's Woody Plant Seed Manual (Agriculture Handbook 727, 2008, a US government work);
  - butchering and meat: Fulton's Home Pork Making (1900) and Rivers's The Hotel Butcher, Garde Manger and Carver
    (1916), and the USDA Agricultural Marketing Service's Institutional Meat Purchase Specifications (the IMPS: the
    numbered cuts of beef, lamb, pork and goat, cured pork and sausage), read from ams.usda.gov;
  - trapping and hide tanning (old books, for history and skills, with the trap law note): Harding's Deadfalls and
    Snares (1907), Steel Traps (1907) and Fur Buyers' Guide (1915), Kreps's Science of Trapping (1909), Farnham's Home
    Manufacture of Furs and Skins (1916), Gibson's Camp Life in the Woods and the Tricks of Trapping (1881) and Watt's
    Leather Manufacture (1906);
  - blacksmithing and the farm forge: Drew's Farm Blacksmithing (1910), Holmström's Modern Blacksmithing (1904),
    Richardson's Practical Blacksmithing (four volumes, 1889), Friese's Farm Blacksmithing (1921), Bacon's
    Forge-Practice and Heat Treatment of Steel (1919), Googerty's Practical Forging and Art Smithing (1915), Ilgen's
    Forge Work (1912) and Lungwitz's Complete Guide to Blacksmithing, Horseshoeing (1902);
  - stars and celestial navigation: the Air Force and Navy's Air Navigation (AFM 51-40, 1973) and the Army Air
    Corps' Air Navigation (TM 1-205, 1940), judged by the release rule for military publications (military_release.py);
    Muir's Navigation and Nautical Astronomy (US Naval Institute, 1911), Lecky's Wrinkles in Practical Navigation
    (1918), Dixie's Air Navigation for Flight Officers (1917); and old star books: Milham's How to Identify the Stars
    (1919), Burritt's Geography of the Heavens (1860), Serviss's Astronomy with the Naked Eye (1908), Norton's Star
    Atlas (1910), Gall's Easy Guide to the Constellations (1910), Olcott's Star Lore of All Ages (1911), Collins's
    Book of Stars (1920) and the Bartons' Guide to the Constellations (1928);
  - water purification: Sanitary Control and Surveillance of Field Water Supplies (TB MED 577 / NAVMED P-5010-10,
    2010) and the Army's Field Water Supply (TM 5-700, 1961), judged by the release rule;
  - fishing gear, nets, cordage from fibre and baskets: White's How to Make Baskets (1901), James's Practical Basket
    Making (1914), Hasluck's Basket Work of All Kinds (1914), Mason's Aboriginal American Basketry (1904), Dodge's
    Useful Fiber Plants of the World (USDA, 1897), Keene's Fishing Tackle (1886), Taylor's Preservation of Fish Nets
    (Bureau of Fisheries, 1921) and Wielder's Fishing Tackle (1922).
  Old books are public domain in the US as published before 1931 (the builder checks each Internet Archive item's
  year at every build); each description says what is out of date. Every book carries the safety note of its area
  (MEAT_SAFETY, TRAP_SAFETY, FORGE_SAFETY, NAV_SAFETY, WATER_SAFETY, FIBRE_SAFETY, SEED_SAFETY).

Already in the library and linked from the index, not repeated: the USDA Farmers' Bulletins by decade
(pub:usda_farmers_bulletins), Secrets of Meat Curing (cook:), smoking and preserving (preserve:, outcook:), game and fish
food safety (gamefish:), the 1961 Yearbook "Seeds" and 1955 "Water" (olife:), Bowditch (1914), the Admiralty and Navy
navigation manuals, the old star books of oldbooks_life.py and NASA's Skywatching pages (science:), the CDC, EPA and
Ready.gov water pages (outcook:), wells (homestead:), Field Hygiene and Sanitation (FM 21-10), the survival manuals,
the knot and rope books (knot:, kmil:) and Butterick's Tatting and Netting (craft:).

Not built (NOT_INCLUDED, link-only for Program Downloader or a browser): Extension guides (copyright), USDA FSIS and CDC
pages (they refuse programs), the National Center for Home Food Preservation (copyright), state trapper education
manuals (each state's copyright), the NGA's Bowditch and sight reduction tables (the site did not answer), the
Nautical and Air Almanacs (joint US and UK Crown works, sold), and others listed below. Psychological first aid and
remote medicine are left to the remote medicine collection; Army meat-cutting and cook manuals to the service skills
collection.

Run from the repository's folder:
  python3 textbooks/homestead_fill.py hfill:index --out build/textbooks
  python3 textbooks/homestead_fill.py --list homestead-fill
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import homestead as H  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = H.GROUP                        # "homestead": the same group as homestead.py
GROUPS = dict(H.GROUPS)                # {"homestead": "Reference, homesteading"}

# ====================================================================== the safety notes, one per area

SEED_SAFETY = ("Seed safety: never eat or feed animals seed that has been treated (it is often dyed pink, blue or "
               "green and coated with a fungicide or insecticide); keep it away from children. Old books name seed "
               "treatments, such as mercury compounds, that are now banned. Selling or swapping seed may fall under "
               "state seed laws, and some varieties are protected by plant patents or plant variety protection.")
MEAT_SAFETY = ("Meat safety (USDA): keep meat at 40 F (4 C) or colder and chill a carcass quickly; cook to a safe "
               "minimum internal temperature checked with a food thermometer: whole cuts of beef, pork, lamb and veal "
               "145 F (63 C) with a 3-minute rest, ground meat and sausage 160 F (71 C), poultry 165 F (74 C). Cure "
               "only with a tested recipe and the exact amount of curing salt it names; cold smoking and drying do "
               "not cook meat. Do not eat an animal that looked sick. Meat you sell must be slaughtered and processed "
               "under USDA or state inspection. Knives, saws and grinders cut: keep blades sharp, cut away from your "
               "body and wear a cut-resistant glove. Old books name preservatives (such as borax, formaldehyde and "
               "large amounts of saltpetre) that are now banned or known to be harmful: never use them.")
TRAP_SAFETY = ("Trapping law: trapping is regulated in every US state and Canadian province: you need a licence, "
               "and often a trapper education course; seasons, legal traps, sizes, checking times and protected "
               "species differ from place to place, and many traps in old books (deadfalls, many snares, large "
               "jawed traps) are now illegal in many places. Check your state or provincial wildlife agency's rules "
               "before you set any trap, follow the Best Management Practices for humane trapping, and keep traps "
               "away from pets and people. Wear gloves when handling animals and hides (tularemia, rabies and other "
               "diseases). Old tanning methods use arsenic, strong acids, lye and other poisons: wear gloves and eye "
               "protection, work outdoors or with good air, and never pour them down a drain or a septic system.")
FORGE_SAFETY = ("Forge safety: hot metal looks the same as cold, so treat all metal at the forge or anvil as hot; "
                "wear safety glasses, leather apron and boots, natural-fibre clothes and hearing protection, and "
                "keep a bucket of water and a fire extinguisher close. Work with good air: coal, coke and gas forges "
                "give off smoke and carbon monoxide. Never heat galvanised (zinc-coated) or plated metal: its fumes "
                "cause metal fume fever. Horseshoeing is skilled work: a horse can kick; learn from a trained "
                "farrier.")
NAV_SAFETY = ("Navigation safety: not for navigation by itself. Use current charts, a current Nautical or Air "
              "Almanac (an old almanac's figures are wrong for today) and an independent backup such as GPS. Never "
              "look at the Sun through a sextant, telescope or binoculars without the proper Sun shades or a solar "
              "filter: it can blind you instantly.")
WATER_SAFETY = ("Water safety (CDC): if you are not sure water is safe, bring it to a rolling boil for 1 minute (3 "
                "minutes above 6,500 feet), or disinfect it with chlorine or iodine as the product's own directions "
                "say; let cloudy water settle and filter it first. Boiling and chlorine do not remove chemicals, "
                "fuel or salt, and a filter removes viruses only if its maker says it does. Test well water every "
                "year. Military field methods are written for trained crews with their own test kits.")
FIBRE_SAFETY = ("Safety: knives, hooks and splitting tools cut, so cut away from your body. Fishing with nets, traps "
                "and lines is regulated: check your state's fishing licence and gear rules before you use a net or "
                "trap. Know a plant before you gather or handle it: some cause rashes or are poisonous, and many "
                "places need permission to collect plants.")

OLD_NOTE = ("Published in {year}: an old book, kept for its methods and history; its prices, laws, materials and "
            "safety advice are those of its day.")
OLD_MEAT = ("Published in {year}: an old book. Its slaughtering, curing and keeping methods are those of its day; "
            "some of its preservatives, temperatures and storage times are now known to be unsafe: follow current "
            "USDA advice and tested recipes.")
OLD_TRAP = ("Published in {year}: an old book, kept for history and skills. Many of its traps, baits, seasons and "
            "methods are now illegal or regulated, and some of its tanning chemicals (arsenic and strong acids "
            "among them) are poisonous; its views of wildlife are those of its day.")
OLD_FORGE = ("Published in {year}: an old book. Its forging methods still apply, but its safety advice is that of "
             "its day: use today's eye, ear, burn and fume protection.")
OLD_SKY = ("Published in {year}: an old book. The constellations and bright stars are the same, but star positions "
           "shift slowly over the years, and its planet positions, dates and some names are out of date.")
OLD_NAV = ("Published in {year}: an old book, kept for its explanations of navigation and nautical astronomy; its "
           "tables, almanac figures and instruments are out of date: never navigate by them.")
NATIVE_NOTE = (" It was written by white American scholars and collectors of its time: some of its words and views "
               "of Native American peoples are outdated and offensive, and it is not an account any Native nation "
               "gave of itself. Many Native basketry traditions are living arts; learn about them from the nations' "
               "own sources.")

# The first words of every military notice; the builder puts the truthful release line in front of it.
MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "military crews: its rules and equipment are military ones and may be old. ")


def _old(name, title, subject, publisher, archive, year, description, note, safety, country="United States"):
    """One old public-domain book of the Internet Archive (old_ia_books.old_book) with its area's safety note."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, notice=safety,
                    country=country)


def _gov(name, title, subject, publisher, archive, published, description, safety, work):
    """One US government publication read from its Internet Archive copy (public domain, 17 U.S.C. 105)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description, notice=f"{work} (public domain), read from the Internet Archive's copy. "
                                                    f"{safety}")


def _mil(name, title, subject, publisher, archive, published, description, safety, work):
    """One US military publication of the Internet Archive, judged at every build by the release rule
    (military=True: the builder reads its front pages and writes the truthful release line)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, version=f"{published} edition (Internet Archive item {archive})",
                    description=description, notice=MIL_NOTICE + safety, military=True, work=work)


# ====================================================================== seed saving

SEED_PDFS = [
    _old("brill_farm_gardening_seed_growing_1884", "Farm-Gardening and Seed-Growing (Francis Brill, 1884 edition)",
         "Seed saving and seed growing", "Francis Brill (Orange Judd Company)", "farmgardeningsee02bril", 1884,
         "A Long Island market gardener and seed grower's book: growing vegetables for market, and then growing "
         "their seed: choosing and keeping the best plants for seed, keeping varieties pure, harvesting, cleaning, "
         "drying and storing seed, crop by crop (cabbage, cauliflower, beets, carrots, onions, cucumbers, melons, "
         "squash, tomatoes, peppers and more).", OLD_NOTE, SEED_SAFETY),
    _old("johnson_seed_grower_1906", "The Seed Grower (Charles Johnson, 1906)", "Seed saving and seed growing",
         "Charles Johnson (Marietta, Pennsylvania)", "seedgrowerpracti00johnrich", 1906,
         "A practical treatise on growing vegetable and flower seeds and bulbs: selecting seed plants, keeping "
         "strains true, harvesting, threshing, cleaning and curing seed, testing it, and the seed of each vegetable "
         "and flower in turn.", OLD_NOTE, SEED_SAFETY),
    _gov("usfs_woody_plant_seed_manual_2008", "The Woody Plant Seed Manual (US Forest Service, Agriculture Handbook "
         "727, 2008)", "Tree and shrub seed", "US Department of Agriculture, Forest Service",
         "TheWoodyPlantSeedManual", "2008",
         "The Forest Service's manual of tree and shrub seed: seed biology, genetic improvement, collecting, "
         "cleaning, drying, storing and testing seed, dormancy and pre-treatment, nursery practice and direct "
         "seeding, then a chapter for each of more than 230 genera of trees and shrubs (flowering and fruiting "
         "dates, seed collection, extraction and storage, germination and nursery practice). Its official PDF's "
         "site shuts out programs in its robots.txt, so the Internet Archive's copy of the same handbook is read.",
         SEED_SAFETY, "A work of the US Department of Agriculture, Forest Service"),
]

# ====================================================================== butchering and meat

AMS = "https://www.ams.usda.gov"
IMPS_PAGE = f"{AMS}/grades-standards/imps"


def _imps(name, number, what, file_name, description):
    """One Institutional Meat Purchase Specification of the USDA AMS, read from its own PDF on ams.usda.gov."""
    return K.us_pdf(GROUP, name=name, title=f"Institutional Meat Purchase Specifications: {number} {what} (USDA "
                    "AMS)", subject="Meat cuts", publisher="US Department of Agriculture, Agricultural Marketing "
                    "Service", pdf=f"{AMS}/sites/default/files/media/{file_name}", page=IMPS_PAGE,
                    version="the PDF on ams.usda.gov's IMPS page at the time of the build",
                    description=description + " The IMPS are the numbered specifications that schools, government "
                    "agencies, restaurants and other large buyers use to order meat; each cut has its number, name "
                    "and how it is cut and trimmed (its photographs are described only by their captions).",
                    notice="A work of the US Department of Agriculture's Agricultural Marketing Service (public "
                           "domain). " + MEAT_SAFETY)


MEAT_PDFS = [
    _old("fulton_home_pork_making_1900", "Home Pork Making (A. W. Fulton, 1900)", "Home slaughtering and curing",
         "A. W. Fulton (Orange Judd Company)", "homeporkmakingco00fultrich", 1900,
         "A complete guide for the farm and the home to hog slaughtering, scalding, cutting up, curing, smoking, "
         "lard rendering, sausage making and preserving pork products, with plans of smokehouses.", OLD_MEAT,
         MEAT_SAFETY),
    _old("rivers_hotel_butcher_1916", "The Hotel Butcher, Garde Manger and Carver (Frank Rivers, 1916)",
         "Meat cutting", "Frank Rivers (The Hotel Monthly Press, Chicago)", "hotelbutchergard00rive", 1916,
         "A kitchen butcher's handbook of its day: cutting beef, veal, lamb, mutton and pork into the cuts kitchens "
         "used, poultry and game, fish, the cold kitchen (garde manger), and carving at the table.", OLD_MEAT,
         MEAT_SAFETY),
    _imps("ams_imps_100_fresh_beef", "Series 100", "Fresh Beef", "IMPS_100_Fresh_Beef%5B1%5D.pdf",
          "The numbered cuts of fresh beef, from carcasses and sides to primals (the round, loin, rib and chuck), "
          "sub-primals, steaks and roasts, and ground beef."),
    _imps("ams_imps_200_fresh_lamb_mutton", "Series 200", "Fresh Lamb and Mutton",
          "IMPS_200_Fresh_Lamb_and_Mutton%5B1%5D.pdf",
          "The numbered cuts of fresh lamb and mutton: carcasses, legs, loins, racks and shoulders, chops and "
          "ground lamb."),
    _imps("ams_imps_400_fresh_pork", "Series 400", "Fresh Pork", "IMPS_400_Fresh_Pork%5B1%5D.pdf",
          "The numbered cuts of fresh pork: carcasses, hams (legs), loins, bellies, shoulders (the Boston butt and "
          "picnic), spareribs, chops and ground pork."),
    _imps("ams_imps_11_fresh_goat", "Series 11", "Fresh Goat", "GoatIMPS%5B1%5D.pdf",
          "The numbered cuts of fresh goat: carcasses, legs, loins, racks, shoulders and cubed and ground goat."),
    _imps("ams_imps_500_cured_smoked_pork", "Series 500", "Cured, Cured and Smoked, and Fully Cooked Pork Products",
          "LSimps500.pdf",
          "The specifications for cured, cured and smoked, and fully cooked pork products: hams, bacon, smoked "
          "shoulders and other cured pork."),
    _imps("ams_imps_800_sausage", "Series 800", "Sausage Products", "LSimps800.pdf",
          "The specifications for sausage products: fresh, smoked, cooked and dry sausages, frankfurters and "
          "luncheon meats."),
]

# ====================================================================== trapping and hide tanning

TRAP_PDFS = [
    _old("harding_deadfalls_snares_1907", "Deadfalls and Snares (A. R. Harding, 1907)", "Trapping (history)",
         "A. R. Harding (A. R. Harding Publishing Company, Columbus, Ohio)", "deadfallssnaresb00harduoft", 1907,
         "A trappers' book of home-made traps of its day: deadfalls, snares and other traps made in the woods, how "
         "they were built and set, and the animals trapped for fur.", OLD_TRAP, TRAP_SAFETY),
    _old("harding_steel_traps_1907", "Steel Traps (A. R. Harding, 1907)", "Trapping (history)",
         "A. R. Harding (A. R. Harding Publishing Company, Columbus, Ohio)", "steeltrapsdescri00hardrich", 1907,
         "The steel traps of its day, maker by maker and size by size, how trappers set them for each fur animal, "
         "and chapters on the care of pelts.", OLD_TRAP, TRAP_SAFETY),
    _old("kreps_science_of_trapping_1909", "Science of Trapping (Elmer H. Kreps, 1909)", "Trapping (history)",
         "Elmer H. Kreps (A. R. Harding Publishing Company, Columbus, Ohio)", "scienceoftrappin00kreprich", 1909,
         "The fur-bearing animals of North America, their nature, habits and range, the trapping methods of its "
         "day for each, and skinning, stretching and caring for pelts.", OLD_TRAP, TRAP_SAFETY),
    _old("harding_fur_buyers_guide_1915", "Fur Buyers' Guide (A. R. Harding, 1915)", "Furs and pelts (history)",
         "A. R. Harding (A. R. Harding Publishing Company, Columbus, Ohio)", "furbuyersguideco00hard", 1915,
         "Buying, handling and grading raw furs: sizes, colours and quality of each kind of fur, how pelts were "
         "stretched, dried and graded, and the fur trade of its day.", OLD_TRAP, TRAP_SAFETY),
    _old("farnham_home_manufacture_furs_skins_1916", "Home Manufacture of Furs and Skins (Albert B. Farnham, 1916)",
         "Hide and fur tanning", "Albert B. Farnham (A. R. Harding Publishing Company, Columbus, Ohio)",
         "homemanufactureo00farniala", 1916,
         "How to tan, dress, colour and make up furs and skins at home: skinning and preparing hides, tanning "
         "furs, tanning leather and buckskin, dyeing, and making robes, rugs, caps and mittens.", OLD_TRAP,
         TRAP_SAFETY),
    _old("gibson_camp_life_tricks_of_trapping_1881", "Camp Life in the Woods and the Tricks of Trapping and Trap "
         "Making (W. Hamilton Gibson, 1881)", "Trapping and camp life (history)",
         "W. Hamilton Gibson (Harper and Brothers)", "camplifeinwoodst00gibsrich", 1881,
         "A naturalist-artist's book of camp life and the traps of his day: camp shelters, cooking and comforts, "
         "and how box traps, coops, snares, deadfalls and steel traps were made and set, with recipes for curing "
         "skins.", OLD_TRAP, TRAP_SAFETY),
    _old("watt_leather_manufacture_1906", "Leather Manufacture (Alexander Watt, 1906)", "Tanning leather",
         "Alexander Watt (Crosby Lockwood, London; Van Nostrand, New York)", "leathermanufactu00wattrich", 1906,
         "A practical handbook of tanning, currying and chrome leather dressing as tanneries did it: preparing "
         "hides and skins, bark and other vegetable tannages, chrome and alum tawing, currying, dyeing and "
         "finishing leather.", OLD_TRAP, TRAP_SAFETY, country="United Kingdom"),
]

# ====================================================================== blacksmithing and the farm forge


def _richardson(volume, archive, what):
    """One of the four volumes of Richardson's Practical Blacksmithing (1889), the Getty Research Institute's copies."""
    return _old(f"richardson_practical_blacksmithing_v{volume}_1889", f"Practical Blacksmithing, volume {volume} (M. "
                f"T. Richardson, ed., 1889)", "Blacksmithing", "M. T. Richardson, ed. (New York)", archive, 1889,
                "The four-volume collection of articles by working blacksmiths from the magazine The Blacksmith and "
                f"Wheelwright. Volume {volume}: {what}", OLD_FORGE, FORGE_SAFETY)


FORGE_PDFS = [
    _old("drew_farm_blacksmithing_1910", "Farm Blacksmithing (James M. Drew, 1910)", "Farm forge work",
         "James M. Drew (Webb Publishing Company, St. Paul)", "cu31924003588450", 1910,
         "A small textbook of the farm forge from the University of Minnesota's School of Agriculture: the forge, "
         "fire and tools, drawing out, upsetting, bending, punching and welding, making hooks, rings and links, "
         "and tempering simple tools.", OLD_FORGE, FORGE_SAFETY),
    _old("holmstrom_modern_blacksmithing_1904", "Modern Blacksmithing, Rational Horse Shoeing and Wagon Making (J. G. "
         "Holmström, 1904)", "Blacksmithing and horseshoeing", "J. G. Holmström (Frederick J. Drake, Chicago)",
         "modernblacksmith00holm", 1904,
         "A blacksmith's handbook with rules, tables and recipes: forging, welding, tempering steel, making "
         "tools, shoeing horses (rational horseshoeing), and wagon work.", OLD_FORGE, FORGE_SAFETY),
    _richardson(1, "gri_33125007986850", "the forge and shop, fires and fuel, tools and how to make and use them."),
    _richardson(2, "gri_33125007986793", "more tools and their making, and forging and shop practice."),
    _richardson(3, "gri_33125007987031", "welding, tempering and hardening steel, and many jobs at the forge."),
    _richardson(4, "gri_33125007986975", "further shop practice, tools and forging methods."),
    _old("friese_farm_blacksmithing_1921", "Farm Blacksmithing (John F. Friese, 1921)", "Farm forge work",
         "John F. Friese (The Manual Arts Press, Peoria)", "farmblacksmithin00frierich", 1921,
         "A textbook and problem book for agricultural schools: the forge and its tools, the fire, drawing, "
         "bending, upsetting, welding, punching and riveting, hardening and tempering, and farm repair jobs, set "
         "out as graded exercises.", OLD_FORGE, FORGE_SAFETY),
    _old("bacon_forge_practice_heat_treatment_1919", "Forge-Practice and Heat Treatment of Steel (John Lord Bacon, "
         "1919)", "Forging and heat treatment", "John Lord Bacon (John Wiley and Sons)", "forgepracticehea00bacorich",
         1919,
         "A shop textbook of forging and the heat treatment of steel: forge fires, tools, drawing, upsetting, "
         "bending and welding, tool-smithing, hardening, tempering and annealing, steel and its making, and "
         "furnaces and pyrometers.", OLD_FORGE, FORGE_SAFETY),
    _old("googerty_practical_forging_art_smithing_1915", "Practical Forging and Art Smithing (Thomas F. Googerty, "
         "1915)", "Forging and decorative ironwork", "Thomas F. Googerty (The Bruce Publishing Company)",
         "cu31924003588534", 1915,
         "A school course in forging and ornamental ironwork: the forge and tools, scrolls and twists, welding, "
         "tool-making and tempering, and making brackets, hinges, grilles and lamps.", OLD_FORGE, FORGE_SAFETY),
    _old("ilgen_forge_work_1912", "Forge Work (William L. Ilgen, 1912)", "Forging", "William L. Ilgen (American Book "
         "Company)", "forgework00ilgerich", 1912,
         "A school textbook of forge work: the forge, fuel and fire, tools, drawing, bending, upsetting, welding, "
         "making chain and hooks, tool steel, hardening and tempering, and steam-hammer work.", OLD_FORGE,
         FORGE_SAFETY),
    _old("lungwitz_complete_guide_blacksmithing_horseshoeing_1902", "The Complete Guide to Blacksmithing, Horseshoeing "
         "(Anton Lungwitz and Charles F. Adams, 1902)", "Blacksmithing and horseshoeing",
         "Anton Lungwitz and Charles F. Adams (M. A. Donohue, Chicago)", "completeguidetob00lung", 1902,
         "A guide to blacksmithing and shoeing horses: the horse's foot and how it works, examining a horse for "
         "shoeing, preparing the hoof, making and fitting shoes, shoeing faulty and diseased feet, and the "
         "smith's forge work.",
         OLD_FORGE + " Its treatments of hoof diseases are out of date: ask a veterinarian and a trained farrier.",
         FORGE_SAFETY),
]

# ====================================================================== stars and celestial navigation

NAV_PDFS = [
    _mil("usaf_afm_51_40_air_navigation_1973", "Air Navigation (AFM 51-40 / NAVAIR 00-80V-49, US Air Force and Navy, "
         "1973)", "Air and celestial navigation", "Departments of the Air Force and the Navy", "ERIC_ED082051", "1973",
         "The Air Force and Navy flying training manual of air navigation (read from ERIC's copy): the earth, maps "
         "and charts, dead reckoning, the compass, radio and radar aids, and celestial navigation: the celestial "
         "sphere, time, the almanac, the sextant, sight reduction, star identification, precomputation and "
         "celestial fixes, with polar and grid navigation.", NAV_SAFETY, "a work of the US Air Force and Navy"),
    _mil("army_tm_1_205_air_navigation_1940", "Air Navigation (TM 1-205, Army Air Corps, 1940)",
         "Air and celestial navigation", "War Department (US Army Air Corps)", "TM1-205", "1940",
         "The Army Air Corps' technical manual of air navigation before the Second World War: maps and charts, "
         "instruments, dead reckoning, radio navigation and celestial navigation (the stars, the sextant and the "
         "methods of finding a position from them). A historical manual.", NAV_SAFETY, "a work of the US Army"),
    _old("muir_navigation_nautical_astronomy_1911", "A Treatise on Navigation and Nautical Astronomy (W. C. P. Muir, "
         "1911)", "Navigation and nautical astronomy", "W. C. P. Muir (The United States Naval Institute)",
         "treatnavinautica00muirrich", 1911,
         "The US Naval Academy's textbook of navigation and nautical astronomy: the earth and charts, dead "
         "reckoning, the compass and its deviations, the celestial sphere, time, the sextant, finding latitude and "
         "longitude by the Sun, Moon and stars, and the Sumner line of position.", OLD_NAV, NAV_SAFETY),
    _old("lecky_wrinkles_practical_navigation_1918", "Wrinkles in Practical Navigation (S. T. S. Lecky, 1918 "
         "edition)", "Navigation and nautical astronomy", "S. T. S. Lecky, revised by William Allingham (George "
         "Philip and Son, London)", "wrinklesinpracti00leckrich", 1918,
         "A sea captain's famous book of practical hints for navigators: charts, the compass, sounding, the "
         "sextant and its errors, chronometers, finding a position by the stars, the Sun and the Moon, and the "
         "rule of the road of its day.", OLD_NAV, NAV_SAFETY, country="United Kingdom"),
    _old("dixie_air_navigation_flight_officers_1917", "Air Navigation for Flight Officers (A. E. Dixie, 1917)",
         "Air and celestial navigation", "A. E. Dixie (Gieves Publishing Company, Portsmouth; J. Hogg, London)",
         "airnavigationfor00dixirich", 1917,
         "A First World War handbook of air navigation for flying officers: maps and the compass, wind and drift, "
         "and finding a position by the Sun and stars from the air.", OLD_NAV, NAV_SAFETY,
         country="United Kingdom"),
    _old("milham_how_to_identify_stars_1919", "How to Identify the Stars (Willis I. Milham, 1919)", "Stargazing",
         "Willis I. Milham (The Macmillan Company)", "howtoidentifythe033088mbp", 1919,
         "A short guide to finding the constellations and bright stars with the naked eye, season by season, "
         "starting from the Big Dipper and the Pole Star.", OLD_SKY, NAV_SAFETY),
    _old("burritt_geography_of_heavens_1860", "The Geography of the Heavens and Class-Book of Astronomy (Elijah H. "
         "Burritt, 1860 edition)", "Stargazing and the constellations",
         "Elijah H. Burritt, revised by Hiram Mattison (Mason Brothers, New York)", "geographyofheav00burr", 1860,
         "A classic school book of the constellations, month by month, with the stories of their names, and a "
         "short astronomy of the Sun, Moon and planets (its celestial atlas was a separate volume).", OLD_SKY,
         NAV_SAFETY),
    _old("serviss_astronomy_naked_eye_1908", "Astronomy with the Naked Eye (Garrett P. Serviss, 1908)",
         "Stargazing and the constellations", "Garrett P. Serviss (Harper and Brothers)",
         "astronomywithnak00serviala", 1908,
         "A new geography of the heavens: the constellations season by season, with their bright stars, legends "
         "and how to find them without a telescope, and the planets and the Milky Way.", OLD_SKY, NAV_SAFETY),
    _old("norton_star_atlas_1910", "A Star Atlas and Telescopic Handbook (Arthur P. Norton, 1910)",
         "Star charts", "Arthur P. Norton (Gall and Inglis, London and Edinburgh)", "cu31924012306068", 1910,
         "The first edition of Norton's famous star atlas (epoch 1920): its handbook text on the celestial sphere, "
         "star positions, magnitudes and observing, and lists of objects for small telescopes. Its star maps are "
         "pictures, described only by their titles.", OLD_SKY, NAV_SAFETY, country="United Kingdom"),
    _old("gall_easy_guide_constellations_1910", "An Easy Guide to the Constellations (James Gall, 1910 printing)",
         "Stargazing and the constellations", "James Gall (G. P. Putnam's Sons, New York and London)",
         "easyguidetoconst00gallrich", 1910,
         "A small guide to learning the constellations by finding them from the stars you already know, with a "
         "miniature atlas of the stars described by its captions.", OLD_SKY, NAV_SAFETY),
    _old("olcott_star_lore_1911", "Star Lore of All Ages (William Tyler Olcott, 1911)", "The constellations and their "
         "stories", "William Tyler Olcott (G. P. Putnam's Sons)", "starloreofallage00olco", 1911,
         "The myths, legends and facts of the constellations of the northern sky, constellation by constellation, "
         "from many peoples and ages.", OLD_SKY, NAV_SAFETY),
    _old("collins_book_of_stars_1920", "The Book of Stars (A. Frederick Collins, 1920)", "Stargazing",
         "A. Frederick Collins (D. Appleton and Company)", "bookofstarsbeing00colluoft", 1920,
         "A simple explanation of the stars for young people: finding the constellations, the Pole Star and "
         "directions, telling time by the stars, and how the stars are used.", OLD_SKY, NAV_SAFETY),
    _old("barton_guide_constellations_1928", "A Guide to the Constellations (Samuel G. Barton and William H. Barton, "
         "1928)", "Stargazing and the constellations", "Samuel G. Barton and William H. Barton (McGraw-Hill)",
         "guidetotheconste032859mbp", 1928,
         "A guide to the constellations for beginners, with seasonal charts described by their captions, the "
         "bright stars, and lists of double stars, clusters and nebulae for small telescopes.", OLD_SKY,
         NAV_SAFETY),
]

# ====================================================================== water purification

WATER_PDFS = [
    _mil("tb_med_577_field_water_supplies_2010", "Sanitary Control and Surveillance of Field Water Supplies (TB MED "
         "577 / NAVMED P-5010-10 / AFMAN 48-138_IP, 2010)", "Field water treatment",
         "Departments of the Army, Navy and Air Force", "NAVMEDP501010SANITARYCONTROLANDSURVEILLANCEOFFIELDWATERSUPPLIES2010",
         "2010",
         "The armed forces' manual for keeping field drinking water safe (read from the Navy Bureau of Medicine "
         "and Surgery history office's copy): health risks in water, choosing a source, treatment (settling, "
         "filtration, reverse osmosis, chlorination and other disinfection), individual and small-unit water "
         "treatment, storing and carrying water, testing, and water in ice and bottled water.", WATER_SAFETY,
         "a work of the US Army, Navy and Air Force"),
    _mil("army_tm_5_700_field_water_supply_1961", "Field Water Supply (TM 5-700, US Army, 1961)",
         "Field water supply and treatment", "Headquarters, Department of the Army", "fieldwatersupply00unitrich",
         "1961",
         "The Army's 1961 technical manual of field water supply: finding water (surface water, wells and "
         "springs), testing it, treating it (settling, filtering and chlorinating), the water purification "
         "equipment of its day, and storing and distributing water. A historical manual: its equipment is long "
         "gone, but its methods are explained clearly.", WATER_SAFETY, "a work of the US Army"),
]

# ====================================================================== fishing gear, nets, cordage and baskets

FIBRE_PDFS = [
    _old("white_how_to_make_baskets_1901", "How to Make Baskets (Mary White, 1901)", "Basket weaving",
         "Mary White (Doubleday, Page)", "howtomakebaskets00whitrich", 1901,
         "A beginner's book of basket weaving in reed, raffia and rush: materials, the stitches and weaves, and "
         "baskets to make, from simple mats and trays to lidded and handled baskets.", OLD_NOTE, FIBRE_SAFETY),
    _old("james_practical_basket_making_1914", "Practical Basket Making (George Wharton James, 1914)",
         "Basket weaving", "George Wharton James (Pasadena, California)", "practicalbasketm00jameiala", 1914,
         "A manual of basket making in reed and raffia: materials and tools, the weaves, coiled and woven baskets, "
         "and finishing borders and handles.",
         OLD_NOTE + " Its remarks on Native American basket makers are those of a white writer of its day.",
         FIBRE_SAFETY),
    _old("hasluck_basket_work_1914", "Basket Work of All Kinds (Paul N. Hasluck, ed., 1914 printing)",
         "Basket weaving", "Paul N. Hasluck (David McKay, Philadelphia)", "basketworkofallk00hasliala", 1914,
         "A craftsman's handbook of willow and cane basket work: tools and materials, preparing osiers, the "
         "weaves, round and oval baskets, square work, hampers and chairs.", OLD_NOTE, FIBRE_SAFETY),
    _old("mason_aboriginal_american_basketry_1904", "Aboriginal American Basketry (Otis Tufton Mason, Smithsonian "
         "Institution, 1904)", "Basketry (history)", "Otis Tufton Mason (US National Museum, Smithsonian "
         "Institution)", "aboriginalameric00maso", 1904,
         "The Smithsonian curator's study of Native American basketry: materials, the ways baskets are woven, "
         "twined and coiled, their forms, uses and ornament, region by region. A US government publication as "
         "well as a book published before 1931.", OLD_NOTE + NATIVE_NOTE, FIBRE_SAFETY),
    _gov("usda_useful_fiber_plants_1897", "A Descriptive Catalogue of Useful Fiber Plants of the World (Charles "
         "Richards Dodge, USDA, 1897)", "Cordage and fibre plants", "US Department of Agriculture, Office of Fiber "
         "Investigations", "descriptivecatal09dodg", "1897",
         "The USDA's catalogue of the world's fibre plants (Fiber Investigations Report No. 9): each plant's fibre "
         "and how it is got out and used for cordage, twine, nets, matting, baskets, brushes and cloth. Published "
         "in 1897: its trade figures are long out of date.", FIBRE_SAFETY,
         "A work of the US Department of Agriculture"),
    _old("keene_fishing_tackle_1886", "Fishing Tackle, Its Materials and Manufacture (John Harrington Keene, 1886)",
         "Making fishing tackle", "John Harrington Keene (Ward, Lock, London and New York)", "cu31924003236308",
         1886,
         "A practical guide to making every kind of fishing tackle of its day: rods, reels, lines, hooks, flies, "
         "floats and nets.", OLD_NOTE, FIBRE_SAFETY, country="United Kingdom"),
    _gov("taylor_preservation_fish_nets_1921", "Preservation of Fish Nets (Harden F. Taylor, US Bureau of Fisheries, "
         "1921)", "Fishing nets", "US Bureau of Fisheries", "preservationoffi00tayl", "1921",
         "The Bureau of Fisheries' study of why fishing nets rot and how to make them last: tanning, tarring, "
         "drying and other treatments of cotton and linen nets and lines. Published in 1921: today's nets are "
         "mostly synthetic, and some of its preservatives (such as copper and coal-tar treatments) are now "
         "regulated.", FIBRE_SAFETY, "A work of the US Bureau of Fisheries"),
    _old("wielder_fishing_tackle_1922", "Fishing Tackle: Modern Improvements in Angling Gear (\"Wielder\", 1922)",
         "Making fishing tackle", "\"Wielder\" (The Bazaar, Exchange and Mart, London)", "fishingtacklemod00wielrich",
         1922,
         "Improvements in angling gear of its day with instructions for making tackle at home: rods, reels, "
         "lines, casts, hooks and accessories.", OLD_NOTE, FIBRE_SAFETY, country="United Kingdom"),
]

PDFS = SEED_PDFS + MEAT_PDFS + TRAP_PDFS + FORGE_PDFS + NAV_PDFS + WATER_PDFS + FIBRE_PDFS

# ====================================================================== the index

FSIS = "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation"
SECTIONS = [
    ("Seed saving", "Growing, saving, cleaning and storing seed. " + SEED_SAFETY, [
        ("key", "hfill:brill_farm_gardening_seed_growing_1884", "Farm-Gardening and Seed-Growing (Brill, 1884)"),
        ("key", "hfill:johnson_seed_grower_1906", "The Seed Grower (Johnson, 1906)"),
        ("key", "hfill:usfs_woody_plant_seed_manual_2008", "The Woody Plant Seed Manual (Forest Service, 2008)"),
        ("key", "olife:usda_yearbook_1961_seeds", "Seeds: the Yearbook of Agriculture 1961 (USDA)"),
        ("word", "pub:usda_farmers_bulletins:1910s", "USDA Farmers' Bulletin 884, Saving Vegetable Seeds for the Home "
                                                     "and Market Garden (1917; its 1922 revision is in the 1920s book)"),
        ("word", "gardening", "The gardening books (request word)"),
        ("pack", "commons_homestead_stores", "Seed libraries and the Svalbard Global Seed Vault, for the picture "
                                             "describer"),
        ("link", "Seed Savers Exchange: learn to save seeds", "https://seedsavers.org/learn",
         "copyright of Seed Savers Exchange; open it in a browser"),
        ("link", "Organic Seed Alliance", "https://seedalliance.org/", "its guides are under its own terms; "
                                                                       "open it in a browser"),
        ("link", "USDA Germplasm Resources Information Network (GRIN)", "https://www.ars-grin.gov/",
         "a database of the national seed collections, used online")]),
    ("Butchering, cutting, curing and sausage", "Home slaughter, cutting, curing, smoking and sausage. " + MEAT_SAFETY, [
        ("key", "hfill:fulton_home_pork_making_1900", "Home Pork Making (Fulton, 1900)"),
        ("key", "hfill:rivers_hotel_butcher_1916", "The Hotel Butcher, Garde Manger and Carver (Rivers, 1916)"),
        ("key", "hfill:ams_imps_100_fresh_beef", "The numbered cuts of beef (USDA IMPS 100)"),
        ("key", "hfill:ams_imps_200_fresh_lamb_mutton", "The numbered cuts of lamb and mutton (USDA IMPS 200)"),
        ("key", "hfill:ams_imps_400_fresh_pork", "The numbered cuts of pork (USDA IMPS 400)"),
        ("key", "hfill:ams_imps_11_fresh_goat", "The numbered cuts of goat (USDA IMPS 11)"),
        ("key", "hfill:ams_imps_500_cured_smoked_pork", "Cured and smoked pork products (USDA IMPS 500)"),
        ("key", "hfill:ams_imps_800_sausage", "Sausage products (USDA IMPS 800)"),
        ("word", "cook:old_secrets_of_meat_curing_1922", "Secrets of Meat Curing and Sausage Making (1922)"),
        ("word", "cook:old_practical_small_smokehouse_for_fish_1918", "A small smokehouse for fish (1918)"),
        ("word", "pub:usda_farmers_bulletins:1900s", "USDA Farmers' Bulletin 183, Meat on the Farm: Butchering, "
                                                     "Curing and Keeping (1903, revised 1906)"),
        ("word", "pub:usda_farmers_bulletins:1910s", "USDA Farmers' Bulletin 913, Killing Hogs and Curing Pork "
                                                     "(1917)"),
        ("word", "pub:usda_farmers_bulletins:1920s", "USDA Farmers' Bulletins 1186, Pork on the Farm, and 1415, Beef "
                                                     "on the Farm: Slaughtering, Cutting, Curing (1920s)"),
        ("word", "pub:usda_farmers_bulletins:1960s", "USDA Farmers' Bulletins: Slaughtering, Cutting, and Processing "
                                                     "Beef (and Pork) on the Farm (1960s)"),
        ("word", "pub:usda_farmers_bulletins:1970s", "USDA Farmers' Bulletins: Beef, Lamb and Pork Slaughtering, "
                                                     "Cutting, Preserving, and Cooking on the Farm (1977, 1978)"),
        ("word", "game-fish", "Game and fish food safety and chronic wasting disease (request word)"),
        ("word", "preserving", "Home food preserving, smoking and curing as history (request word)"),
        ("pack", "commons_homestead_stores", "Sausage making, cleavers and butcher knives, for the picture describer"),
        ("link", "USDA FSIS: smoking meat, jerky, ham, bacon and sausage food safety", f"{FSIS}/meat",
         "public domain, but fsis.usda.gov refuses programs; open it in a browser"),
        ("link", "National Center for Home Food Preservation: curing and smoking", "https://nchfp.uga.edu/how/cure-smoke",
         "copyright of the University of Georgia; open it in a browser"),
        ("link", "Penn State Extension: animals and livestock (meat processing guides)",
         "https://extension.psu.edu/animals-and-livestock", "copyright of Penn State; open it in a browser")]),
    ("Trapping, furs and hide tanning", "Old trapping and tanning books, kept for history and skills. " + TRAP_SAFETY, [
        ("key", "hfill:harding_deadfalls_snares_1907", "Deadfalls and Snares (Harding, 1907)"),
        ("key", "hfill:harding_steel_traps_1907", "Steel Traps (Harding, 1907)"),
        ("key", "hfill:kreps_science_of_trapping_1909", "Science of Trapping (Kreps, 1909)"),
        ("key", "hfill:harding_fur_buyers_guide_1915", "Fur Buyers' Guide (Harding, 1915)"),
        ("key", "hfill:gibson_camp_life_tricks_of_trapping_1881", "Camp Life in the Woods and the Tricks of Trapping "
                                                                  "(Gibson, 1881)"),
        ("key", "hfill:farnham_home_manufacture_furs_skins_1916", "Home Manufacture of Furs and Skins (Farnham, "
                                                                  "1916)"),
        ("key", "hfill:watt_leather_manufacture_1906", "Leather Manufacture (Watt, 1906)"),
        ("word", "pub:usda_farmers_bulletins:1920s", "USDA Farmers' Bulletins 1055, Country Hides and Skins, and "
                                                     "1334, Home Tanning of Leather and Small Fur Skins (1920s)"),
        ("word", "pub:usda_farmers_bulletins:1950s", "Home Tanning of Leather and Small Fur Skins (USDA, 1954 "
                                                     "revision)"),
        ("pack", "commons_forge_traps_tanning", "Historic traps in museums, fish traps, lobster traps and tanneries, "
                                                "for the picture describer"),
        ("link", "Association of Fish and Wildlife Agencies (trapping Best Management Practices and the state "
                 "agencies)", "https://www.fishwildlife.org/", "its own copyright; open it in a browser"),
        ("link", "Your state's trapper education course and trapping rules", "https://www.fws.gov/",
         "each state wildlife agency's own pages and copyright; the US Fish and Wildlife Service links them")]),
    ("Blacksmithing and the farm forge", "Forging, tool-making, heat treatment and horseshoeing. " + FORGE_SAFETY, [
        ("key", "hfill:drew_farm_blacksmithing_1910", "Farm Blacksmithing (Drew, 1910)"),
        ("key", "hfill:friese_farm_blacksmithing_1921", "Farm Blacksmithing (Friese, 1921)"),
        ("key", "hfill:holmstrom_modern_blacksmithing_1904", "Modern Blacksmithing (Holmström, 1904)"),
        ("key", "hfill:richardson_practical_blacksmithing_v1_1889", "Practical Blacksmithing, volume 1 (1889)"),
        ("key", "hfill:richardson_practical_blacksmithing_v2_1889", "Practical Blacksmithing, volume 2 (1889)"),
        ("key", "hfill:richardson_practical_blacksmithing_v3_1889", "Practical Blacksmithing, volume 3 (1889)"),
        ("key", "hfill:richardson_practical_blacksmithing_v4_1889", "Practical Blacksmithing, volume 4 (1889)"),
        ("key", "hfill:bacon_forge_practice_heat_treatment_1919", "Forge-Practice and Heat Treatment of Steel (Bacon, "
                                                                  "1919)"),
        ("key", "hfill:ilgen_forge_work_1912", "Forge Work (Ilgen, 1912)"),
        ("key", "hfill:googerty_practical_forging_art_smithing_1915", "Practical Forging and Art Smithing (Googerty, "
                                                                      "1915)"),
        ("key", "hfill:lungwitz_complete_guide_blacksmithing_horseshoeing_1902", "The Complete Guide to "
                                                                                 "Blacksmithing, Horseshoeing (1902)"),
        ("word", "making", "Home manufacturing and making: casting, machining and metalwork (request word)"),
        ("pack", "commons_forge_traps_tanning", "Blacksmith's tools, hardies, swage blocks, horseshoes and farriery, "
                                                "for the picture describer"),
        ("link", "Artist-Blacksmith's Association of North America", "https://abana.org/",
         "classes and local groups; its own copyright")]),
    ("Stars, star charts and celestial navigation", "Finding your way by the stars and the Sun. " + NAV_SAFETY, [
        ("key", "hfill:usaf_afm_51_40_air_navigation_1973", "Air Navigation (AFM 51-40, 1973), with celestial "
                                                            "navigation"),
        ("key", "hfill:army_tm_1_205_air_navigation_1940", "Air Navigation (TM 1-205, 1940)"),
        ("key", "hfill:muir_navigation_nautical_astronomy_1911", "Navigation and Nautical Astronomy (Muir, 1911)"),
        ("key", "hfill:lecky_wrinkles_practical_navigation_1918", "Wrinkles in Practical Navigation (Lecky, 1918)"),
        ("key", "hfill:dixie_air_navigation_flight_officers_1917", "Air Navigation for Flight Officers (Dixie, 1917)"),
        ("key", "pdf:bowditch_american_practical_navigator_1914", "The American Practical Navigator (Bowditch, 1914)"),
        ("key", "kmil:admiralty_manual_of_navigation_1973_v2", "Admiralty Manual of Navigation, volume II: nautical "
                                                               "astronomy (1973)"),
        ("key", "pdf:navy_quartermaster_1_c", "Quartermaster 1 and C (US Navy, 1991): celestial navigation"),
        ("key", "hfill:milham_how_to_identify_stars_1919", "How to Identify the Stars (Milham, 1919)"),
        ("key", "hfill:serviss_astronomy_naked_eye_1908", "Astronomy with the Naked Eye (Serviss, 1908)"),
        ("key", "hfill:burritt_geography_of_heavens_1860", "The Geography of the Heavens (Burritt, 1860)"),
        ("key", "hfill:gall_easy_guide_constellations_1910", "An Easy Guide to the Constellations (Gall, 1910)"),
        ("key", "hfill:barton_guide_constellations_1928", "A Guide to the Constellations (Barton, 1928)"),
        ("key", "hfill:collins_book_of_stars_1920", "The Book of Stars (Collins, 1920)"),
        ("key", "hfill:olcott_star_lore_1911", "Star Lore of All Ages (Olcott, 1911)"),
        ("key", "hfill:norton_star_atlas_1910", "A Star Atlas and Telescopic Handbook (Norton, 1910)"),
        ("key", "olife:olcott_field_book_of_stars_1907", "A Field Book of the Stars (Olcott, 1907)"),
        ("key", "olife:serviss_astronomy_opera_glass_1890", "Astronomy with an Opera-Glass (Serviss, 1890)"),
        ("key", "science:nasa_skywatching", "Skywatching: the night sky month by month (NASA)"),
        ("pack", "commons_stars_navigation", "Constellations, star charts, celestial globes, sextants, octants and "
                                             "marine chronometers, for the picture describer"),
        ("link", "NGA: The American Practical Navigator (Bowditch, Pub. 9) and the sight reduction tables (Pub. 229 "
                 "and Pub. 249)", "https://msi.nga.mil/Publications/APN", "public domain, but msi.nga.mil did not "
                                                                         "answer (\"503\", 2026-11-23); fetch "
                                                                         "them with Program Downloader"),
        ("link", "US Naval Observatory: celestial navigation data", "https://aa.usno.navy.mil/",
         "computed online; the printed Nautical and Air Almanacs are sold"),
        ("link", "NASA Night Sky Network (star charts and activities)", "https://nightsky.jpl.nasa.gov/",
         "run by NASA's Jet Propulsion Laboratory and the Astronomical Society of the Pacific under their own "
         "terms; open it in a browser")]),
    ("Water purification", "Making water safe: boiling, disinfecting, filtering and storing it. " + WATER_SAFETY, [
        ("key", "hfill:tb_med_577_field_water_supplies_2010", "Sanitary Control and Surveillance of Field Water "
                                                              "Supplies (TB MED 577, 2010)"),
        ("key", "hfill:army_tm_5_700_field_water_supply_1961", "Field Water Supply (TM 5-700, 1961)"),
        ("key", "outcook:cdc_emergency_water", "CDC: making water safe in an emergency, boiling and disinfecting"),
        ("key", "outcook:epa_emergency_water", "EPA: emergency disinfection of drinking water (personal use)"),
        ("key", "outcook:ready_food_water_power", "Ready.gov: storing water"),
        ("key", "homestead:epa_private_wells_septic", "EPA: private wells and septic systems"),
        ("key", "pdf:army_fm_21_10_field_hygiene_2000", "Field Hygiene and Sanitation (FM 21-10, 2000): water"),
        ("key", "olife:usda_yearbook_1955_water", "Water: the Yearbook of Agriculture 1955 (USDA)"),
        ("word", "bushcraft", "Bushcraft books, with finding water in the wild (request word)"),
        ("pack", "commons_homestead_stores", "Water purification, for the picture describer"),
        ("link", "CAWST: household water treatment", "https://www.cawst.org/",
         "its own terms (non-commercial); open it in a browser"),
        ("link", "SODIS: solar water disinfection", "https://www.sodis.ch/", "copyright of Eawag; open it in a browser"),
        ("link", "WHO: water, sanitation and health", "https://www.who.int/teams/environment-climate-change-and-"
                                                      "health/water-sanitation-and-health",
         "WHO's licence (CC BY-NC-SA) is non-commercial; open it in a browser")]),
    ("Fishing gear, nets, cordage and baskets", "Making and caring for tackle and nets, fibre and cordage, and "
                                                "baskets for storage. " + FIBRE_SAFETY, [
        ("key", "hfill:keene_fishing_tackle_1886", "Fishing Tackle, Its Materials and Manufacture (Keene, 1886)"),
        ("key", "hfill:wielder_fishing_tackle_1922", "Fishing Tackle (Wielder, 1922)"),
        ("key", "hfill:taylor_preservation_fish_nets_1921", "Preservation of Fish Nets (Bureau of Fisheries, 1921)"),
        ("key", "hfill:usda_useful_fiber_plants_1897", "Useful Fiber Plants of the World (USDA, 1897): cordage fibres"),
        ("key", "hfill:white_how_to_make_baskets_1901", "How to Make Baskets (White, 1901)"),
        ("key", "hfill:james_practical_basket_making_1914", "Practical Basket Making (James, 1914)"),
        ("key", "hfill:hasluck_basket_work_1914", "Basket Work of All Kinds (Hasluck, 1914)"),
        ("key", "hfill:mason_aboriginal_american_basketry_1904", "Aboriginal American Basketry (Mason, 1904)"),
        ("key", "craft:butterick_tatting_netting_1895", "Tatting and Netting (Butterick, 1895)"),
        ("key", "knot:index", "Knots and outdoor skills: the guide to knots, rope and cordage"),
        ("word", "knots-military", "Military and Coast Guard rope and knot manuals (request word)"),
        ("pack", "commons_homestead_stores", "Fishing nets, cast nets, ropemaking, baskets and basketry, for the "
                                             "picture describer"),
        ("pack", "commons_fishing_tackle", "Fishing tackle, for the picture describer")]),
]
INDEX = X.index_maker("hfill", GROUP, "Homestead skills: a guide to the library", "Homestead and self-reliance "
                      "skills", "A guide to seven homestead and self-reliance skills in the library: seed saving, "
                      "butchering and curing, trapping and hide tanning, blacksmithing, stars and celestial "
                      "navigation, water purification, and fishing gear, nets, cordage and baskets.", SECTIONS)
MAKERS = {"index": INDEX}


def _keys(pdfs):
    """The keys of a list of entries."""
    return [f"hfill:{p['name']}" for p in pdfs]


AREAS = {"seed-saving": SEED_PDFS, "butchering": MEAT_PDFS, "trapping-tanning": TRAP_PDFS,
         "blacksmithing": FORGE_PDFS, "star-navigation": NAV_PDFS, "water-purification": WATER_PDFS,
         "fibre-crafts": FIBRE_PDFS}
WORDS = {"homestead-fill": lambda: ["hfill:index"] + _keys(PDFS)}
WORDS.update({word: (lambda pdfs=pdfs: ["hfill:index"] + _keys(pdfs)) for word, pdfs in AREAS.items()})
COLLECTION = K.Collection("hfill", GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "hfill_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so a "
                       "later reprint is refused); archive.org's robots.txt allows the files; no AI rules (checked "
                       "2026-11-23). The British books (Watt, Lecky, Dixie, Norton, Keene, Wielder) are public domain "
                       "in the US as published before 1931.",
    "hfill_us_gov": "Works of the US government (17 U.S.C. 105, the licence line read on govinfo.gov's policies page at "
                    "every build): the Forest Service's Woody Plant Seed Manual (the Internet Archive's copy, as "
                    "research.fs.usda.gov's robots.txt disallows all programs), the USDA's fibre plant catalogue and "
                    "the Bureau of Fisheries' net study (Internet Archive copies), and the USDA AMS Institutional Meat "
                    "Purchase Specifications read from www.ams.usda.gov (its robots.txt allows /sites/default/files; "
                    "no AI rules, checked 2026-11-23).",
    "hfill_military": "AFM 51-40 (ERIC's copy), TM 1-205, TB MED 577 / NAVMED P-5010-10 and TM 5-700: works of the US "
                      "armed forces read from the Internet Archive and judged at every build by the release rule "
                      "(military_release.py): the builder reads the front pages and says truthfully what they print "
                      "about distribution; a restricted marking is never republished.",
    "hfill_index": "The index (hfill:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Extension guides on seed saving, home slaughter, meat cutting, curing, sausage, trapping and water treatment "
     "(Penn State, Minnesota, Utah State, Oregon State and others)", "Each university's copyright or a "
     "non-commercial licence; none was confirmed open one by one. Link-only for the owner to fetch with Program "
     "Downloader. Index: https://www.extension.org/ and https://extension.psu.edu/animals-and-livestock"),
    ("USDA FSIS pages on smoking meat, jerky, ham, bacon, sausage and safe temperatures", "Public domain, but "
     "www.fsis.usda.gov answered this build machine \"403\" again, robots.txt included (2026-11-23). Link-only. "
     "Index: https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/meat"),
    ("National Center for Home Food Preservation: curing and smoking meat", "Copyright of the University of Georgia. "
     "Link-only. Index: https://nchfp.uga.edu/how/cure-smoke"),
    ("USDA Farmers' Bulletins on slaughtering, curing, home tanning, hides and saving seed (Bulletins 183, 884, 913, "
     "1055, 1186, 1334, 1415 and the 1959 to 1983 slaughtering bulletins)", "Already in the library by decade "
     "(pub:usda_farmers_bulletins) and named in hfill:index; not built again. Index: "
     "https://archive.org/details/usda-farmersbulletin"),
    ("Seeds: the Yearbook of Agriculture 1961 (the Internet Archive's lending copy seedsyearbookofa0000usda)",
     "Already in the library from another copy (olife:usda_yearbook_1961_seeds); the lending copy cannot be "
     "downloaded. Index: https://archive.org/details/seedsyearbookofa0000usda"),
    ("The Woody-Plant Seed Manual of 1948 (USDA Miscellaneous Publication 654)", "Replaced by the 2008 manual built "
     "here (hfill:usfs_woody_plant_seed_manual_2008). Index: https://archive.org/details/woodyplantseedma654unit"),
    ("State trapper education manuals and the Association of Fish and Wildlife Agencies' trapping Best Management "
     "Practices", "Each state's and the association's own copyright (state works vary; none was confirmed open). "
     "Link-only from hfill:index. Index: https://www.fishwildlife.org/"),
    ("Harding's Mink Trapping, Fox Trapping, Wolf and Coyote Trapping and Fur Farming, and Woodcock's Fifty Years a "
     "Hunter and Trapper", "Public domain (before 1931) but they repeat the trapping methods of the three Harding "
     "and Kreps books built here, and trapping one kind of animal is a narrow, regulated use. Index: "
     "https://archive.org/search?query=creator%3Aharding+trapping"),
    ("Taxidermy books (Hornaday, Davie, Reed, Browne)", "Out of scope for homestead skills (mounting animals for "
     "display); their old preservatives include arsenic. Index: https://archive.org/search?query=taxidermy"),
    ("The American Practical Navigator (Bowditch, NGA Pub. 9) and the sight reduction tables Pub. 229 and Pub. 249",
     "Public domain (NGA), but msi.nga.mil answered \"503\" for every page and file (2026-11-23); the Internet "
     "Archive copies of the modern editions found were a Google scan without a usable date (americanpractic00offigoog). "
     "The 1914 Bowditch is in the library (pdf:bowditch_american_practical_navigator_1914). Link-only. Index: "
     "https://msi.nga.mil/Publications/APN"),
    ("The Nautical Almanac and the Air Almanac", "Produced jointly by the US Naval Observatory and HM Nautical Almanac "
     "Office (UK Crown copyright in part) and sold each year; an old almanac is useless for navigation. Link-only. "
     "Index: https://aa.usno.navy.mil/"),
    ("Water Supply and Water Purification (TM 5-295, 1942)", "Replaced by TM 5-700 (1961) and TB MED 577 (2010), "
     "both built here. Index: https://archive.org/details/TM5-295"),
    ("CAWST household water treatment guides, Eawag's SODIS manual and WHO's household water treatment documents",
     "Non-commercial licences or their makers' copyright. Link-only from hfill:index. Index: https://www.cawst.org/ "
     "and https://www.sodis.ch/"),
    ("Army meat cutting, cook and subsistence manuals (TM 10-series) and Navy metalworking rate manuals", "Left to "
     "the service skills and Navy rates collections being built at the same time, so the same manual is not built "
     "twice. Index: https://archive.org/search?query=TM+10-405"),
    ("Psychological first aid and remote medicine", "Covered by the remote medicine collection; not repeated here. "
     "Index: https://www.ptsd.va.gov/professional/treat/type/psych_firstaid_manual.asp"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
