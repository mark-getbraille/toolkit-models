"""Craft trades for the reference library (the owner's request of 23 November 2026): beekeeping, glass blowing and
glass work, leather working, and clothing making and repair. Keys: ctrade:<name>. Request words: ctrade-bees,
ctrade-glass, ctrade-leather, ctrade-clothing (one per trade) and craft-trades (all four).

Where the books go in the library:
  - the beekeeping books are in the group "Reference, homesteading" (homestead.py's group), beside Langstroth (1913)
    and Root's ABC of Bee Culture (1905), which homestead.py already builds;
  - the glass, leather and clothing books are in "Reference, arts and crafts" (crafts_books.GROUP).
  The arts and crafts guide (arts_crafts_index.py, arts:index) lists every book of this module on one page per trade,
  with the picture packs and manual collections that go with it.

What this module builds, each book IN FULL (machine-read text, one web page per chapter or ten scanned pages):
  - old public-domain books (published before 1931; the builder checks each Internet Archive item's year at every
    build and refuses a later one):
      beekeeping  Langstroth's first edition (1853), Root's ABC and XYZ of Bee Culture (1910), Phillips' Beekeeping
                  (1918 printing), Comstock's How to Keep Bees (1905), Cowan's British Bee-Keeper's Guide Book (1911),
                  Cook's Bee-Keeper's Guide (1902), Hasluck's Beehives and Bee Keepers' Appliances (1911, how to make
                  hives), Pellett's Practical Queen Rearing (1918), Miller's Thousand Answers (1917), Dadant's First
                  Lessons (1918) and Beekeeping in the South (1920);
      glass       Shenstone's Methods of Glass-Blowing (1916 printing), Frary's Laboratory Manual of Glass-Blowing
                  (1914), Bernard Bolas' Handbook of Laboratory Glass-Blowing (1921), Thomas Bolas' Glass Blowing and
                  Working (1898), Lynde's Experimental Glass Blowing for Boys (1920), Threlfall's On Laboratory Arts
                  (1898), Woollatt's Laboratory Arts (1908), Danger's Art of Glass-Blowing (1831), and the stained glass
                  books of Henry Holiday (1896) and Alfred Werck (1922);
      leather     Wilson's Leather Work (1908), Leland's Leather Work (1925 edition), Hasluck's Leather Working,
                  Harness Making and Saddlery (1904), The Harness Makers' Guide (1907), Fitz-Gerald's Harness Makers'
                  Illustrated Manual (1880), Roehl's Harness Repairing (1921), Dooley's Manual of Shoemaking (1912),
                  Leno's Art of Boot and Shoemaking (1889), Levinson's Home Book of Shoe Repairing (1916) and Rogers'
                  Practical Tanning (1922);
      clothing    Vincent's Cutter's Practical Guide (ladies' garments, 1892), Mitchell's "Standard" Work on Cutting
                  (1886) and New Standard Work on ladies' tailor-made garments (1921), the Woman's Institute's
                  Pattern Drafting (1920) and Tailored Buttonholes (1923, Mary Brooks Picken), Merwin's American
                  System of Dressmaking (1912), Wakeman's Scientific Sewing and Garment Cutting (1898), Conover's
                  Complete Course in Dressmaking (draping and pattern making; men's clothes; 1922), the Ladies' Tailor
                  Complete Instructor (1892), Hecklinger's Vest Cutting (1883), three millinery courses (1909, 1919,
                  1922) and Trilling's Girl's Problems in Home Economics (1926).
    They are OLD: methods, materials and safety advice are out of date (arsenic and lead in old dyes and pigments,
    mercury in hat felting, asbestos and mercury in old glass work, strong acids, lime and sulphides in tanning, old bee
    medicines). Each notice gives today's safety note first and says the machine-read text has the scanner's mistakes.
  - US government works (public domain, 17 U.S.C. 105), from the Internet Archive's copies of the National Agricultural
    Library's and NIST's collections: the USDA's bee bulletins (Benton's manual of 1899, Snodgrass's Anatomy of the
    Honey Bee, foulbrood, bee diseases, comb honey, wintering, equipment, pesticides, Varroa and Africanized bees, and
    Agriculture Handbook 690, Diagnosis of Honey Bee Diseases), the Bureau of Standards' papers on glasses that protect
    the eyes, on annealing glass and on making a large glass disk, and the USDA's clothing bulletins (fitting, mending,
    make-overs, coat making, work clothes, pattern alteration, hand sewing, menswear jackets, sewing machine care);
  - US Army manuals, judged by the release rule (military_release.py) on their own front matter at every build: TM
    10-430 The Saddler (1942) and TM 10-269 Repair of Canvas and Webbing (1948). FM 10-16 General Fabric Repair (2000)
    and the military sewing machine and parachute courses are service_skills.py's (skill:), listed in arts:index;
  - Wikibooks' Beekeeping and Sewing (CC BY-SA 4.0, share-alike: kept separate as every Wikibooks book is).

Not built (NOT_INCLUDED, each with its index address): university Extension beekeeping, sewing and leather guides
(each university's copyright: link-only), the Peace Corps beekeeping manuals and blacksmithing (other helpers' books,
named by their request words in arts:index), modern craft books (copyright), and the makers' own manuals (the manual
library's collections, linked from arts:index).

Run from the repository's folder:
  python3 textbooks/craft_trades.py ctrade:frary_laboratory_glass_blowing_1914 --out build/textbooks --limit 5
  python3 textbooks/craft_trades.py --list craft-trades
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crafts_books as CB  # noqa: E402
import homestead as HS  # noqa: E402
import refs_kit as K  # noqa: E402
from electronics_books import wikibook  # noqa: E402

GROUP = CB.GROUP                 # "crafts": "Reference, arts and crafts"
BEE_GROUP = HS.GROUP             # "homestead": "Reference, homesteading"
GROUPS = {}                      # both groups are named by crafts_books.py and homestead.py

# The four trades: (request word, area name).
AREAS = {"bees": "ctrade-bees", "glass": "ctrade-glass", "leather": "ctrade-leather", "clothing": "ctrade-clothing"}
ALL_WORD = "craft-trades"

# ----------------------------------------------------------------- today's safety notes (said first in each notice)

BEE_NOTE = ("Safety today: bees sting. Wear a veil and gloves, work calmly and use the smoker. Anyone who has had a "
            "severe reaction to a sting should not work bees and should keep the emergency medicine their doctor "
            "prescribed with them; call 911 at once for trouble breathing, swelling of the face or throat, or "
            "fainting after a sting. A smoker burns hot: light it on bare ground or stone, never set it down in dry "
            "grass, and put it out fully in a closed metal can. Bee diseases and mites are treated differently "
            "today: follow current product labels and your state's apiary rules (in many places American foulbrood "
            "must be reported).")
GLASS_NOTE = ("Safety today: hot glass looks exactly like cold glass and burns badly: let work cool where nobody will "
              "touch it, and keep a bucket of water and a fire extinguisher near. Wear eye protection made for glass "
              "work (didymium lenses cut the bright yellow sodium flare of soft glass; borosilicate and quartz work "
              "need darker shade lenses against infrared and ultraviolet). Work with good ventilation, keep gas "
              "cylinders upright and leak-test fittings with soapy water. Old books' asbestos, mercury and benzene "
              "are never to be used.")
STAINED_NOTE = CB.GLASS_NOTE
LEATHER_NOTE = ("Safety today: leather knives, awls and punches are very sharp: cut away from your body, on a cutting "
                "mat, and keep blades covered. Leather dyes, cements and solvents give off fumes and some catch fire: "
                "use them with fresh air, away from flames, wearing gloves. Old books' arsenic, lime, sulphides, chrome "
                "salts and strong acids for tanning are dangerous: their recipes are history, not instructions.")
CANVAS_NOTE = ("Safety today: sewing machines, knives, awls and grommet tools can injure hands: keep fingers clear of "
               "the needle and work on a cutting mat. Use waterproofing and fire-retardant compounds only with "
               "ventilation and gloves, as their labels say.")
CLOTHING_NOTE = ("Safety today: keep pins, needles and shears out of children's reach; an iron is hot enough to burn "
                 "at a touch, so unplug it when you finish and keep its cord out of the way. Old books' dyes and "
                 "finishes (arsenic greens, lead) and mercury for hat felts are poisonous and must not be used.")

OLD = dict(country="United States", licence="Public domain (published before 1931)",
           licence_url="https://www.copyright.gov/help/faq/faq-duration.html", old_public_domain=True,
           level="reference", changes="its scanned pages' machine-read text (with the scanner's mistakes) made into "
                                      "web pages, one per chapter")
ARMY = "Headquarters, Department of the Army"
WAR_DEPT = "War Department (US Army)"
USDA = "US Department of Agriculture"
NBS = "National Bureau of Standards (now NIST)"
NAL = ("A work of the US Department of Agriculture (public domain), from the National Agricultural Library's copy on "
       "the Internet Archive.")


def _safety(area):
    """Today's safety note of one trade (the glass area's stained glass books use the stained glass note instead)."""
    return {"bees": BEE_NOTE, "glass": GLASS_NOTE, "leather": LEATHER_NOTE, "clothing": CLOTHING_NOTE}[area]


def old_book(area, name, title, subject, publisher, archive, year, description, country="United States",
             safety=None):
    """An old public-domain book (published before 1931) from the Internet Archive as a PDF entry of one trade, with
    today's safety note first in its notice."""
    safety = safety or _safety(area)
    return dict(OLD, group=BEE_GROUP if area == "bees" else GROUP, area=area, name=name, title=title,
                subject=subject, publisher=publisher, archive=archive, published=str(year), version=f"{year} edition",
                country=country,
                description=description + f" Published in {year}: an old book whose methods, materials and safety "
                                          "advice are out of date, kept for its explanations and history.",
                notice=f"{safety} This is an old book (published in {year}); its machine-read text has the scanner's "
                       "mistakes.")


def gov_book(area, name, title, subject, publisher, archive, year, description, source=NAL, dated=True,
             safety=None):
    """A US government work (public domain) from the Internet Archive as a PDF entry of one trade; dated=True says in
    the description that its methods are of their time."""
    safety = safety or _safety(area)
    more = (f" Published in {year}: methods and materials of its time; check current guidance." if dated else "")
    return K.us_pdf(BEE_GROUP if area == "bees" else GROUP, area=area, name=name, title=title, subject=subject,
                    publisher=publisher, archive=archive, published=str(year), version=f"{year} edition",
                    description=description + more, notice=f"{source} {safety}")


def army(area, name, title, subject, publisher, archive, year, description, safety):
    """A US Army manual from the Internet Archive, judged by the release rule (military_release.py) on its own front
    matter at every build (distribution_a); the builder puts the truthful release line first, so the notice holds
    only the safety words."""
    return K.us_pdf(GROUP, area=area, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    distribution_a=True, published=str(year), version=f"{year} edition", description=description,
                    notice=safety)


# ====================================================================== beekeeping

BEES = [
    old_book("bees", "langstroth_hive_honey_bee_1853", "Langstroth on the Hive and the Honey-Bee: a Bee-Keeper's "
             "Manual (L. L. Langstroth, 1853)", "Beekeeping", "L. L. Langstroth (Hopkins, Bridgman and Company)",
             "langstrothonhiv00lang", 1853,
             "The first edition of the book that introduced the movable-frame hive and the bee space: the queen, "
             "workers and drones, comb building, swarming and dividing colonies, the hive and its frames, feeding, "
             "wintering, robbing, enemies of bees, and honey and wax. (homestead.py builds the Dadants' revision of "
             "1913.)"),
    old_book("bees", "root_abc_xyz_bee_culture_1910", "The ABC and XYZ of Bee Culture (A. I. and E. R. Root, 1910)",
             "Beekeeping", "A. I. Root Company", "abcxyzofbeecultu00root", 1910,
             "The enlarged encyclopedia of beekeeping, arranged A to Z: hives and frames, extracting and comb honey, "
             "smokers and veils, swarming, queen rearing, honey plants, wintering, diseases, beeswax and the bee "
             "itself. (homestead.py builds the shorter ABC of Bee Culture of 1905.)"),
    old_book("bees", "phillips_beekeeping_1918", "Beekeeping (Everett Franklin Phillips, 1918 printing)",
             "Beekeeping", "Everett Franklin Phillips (Macmillan)", "beekeepingdiscus00philrich", 1918,
             "A textbook by the man in charge of the USDA's bee work: the life of the honey bee, the colony through "
             "the year, the apiary and its equipment, managing colonies for honey, swarm control, wintering, honey "
             "plants, diseases and enemies, and marketing honey."),
    old_book("bees", "comstock_how_to_keep_bees_1905", "How to Keep Bees: a Handbook for the Use of Beginners (Anna "
             "Botsford Comstock, 1905)", "Beekeeping", "Anna Botsford Comstock (Doubleday, Page and Company)",
             "howtokeepbeeshan00comsiala", 1905,
             "A plain beginner's handbook: why keep bees, the inhabitants of the hive, choosing hives and tools, "
             "handling bees, swarming, getting honey and wax, wintering, and bee diseases and enemies."),
    old_book("bees", "cowan_british_beekeepers_guide_1911", "The British Bee-Keeper's Guide Book (T. W. Cowan, "
             "1911)", "Beekeeping", "T. W. Cowan (Madgwick, Houlston and Company)", "britishbeekeeper00cowa", 1911,
             "The standard British guide to keeping bees in movable-comb hives: the bee and the colony, hives and "
             "appliances, manipulating colonies, swarming, queens, honey, wax, and diseases.",
             country="United Kingdom"),
    old_book("bees", "cook_beekeepers_guide_1902", "The Bee-Keeper's Guide, or Manual of the Apiary (A. J. Cook, "
             "1902)", "Beekeeping", "Albert John Cook (George W. York and Company)", "beekeepersguideo00cook", 1902,
             "A college professor's manual of the apiary: the natural history and anatomy of the honey bee, then "
             "practical beekeeping: hives, extractors and other tools, handling, increase, queen rearing, comb and "
             "extracted honey, wintering, honey plants, and enemies and diseases."),
    old_book("bees", "hasluck_beehives_appliances_1911", "Beehives and Bee Keepers' Appliances (Paul N. Hasluck, 1911)",
             "Making hives and beekeeping equipment", "Paul N. Hasluck (David McKay)", "beehivesbeekeepe00haslrich",
             1911,
             "A workshop handbook for making your own beekeeping equipment: frame hives of several patterns, frames "
             "and sections, observation hives, honey extractors, wax extractors, smokers and other appliances, with "
             "the measurements and how to put them together."),
    old_book("bees", "pellett_practical_queen_rearing_1918", "Practical Queen Rearing (Frank C. Pellett, 1918)",
             "Queen rearing", "Frank C. Pellett (American Bee Journal)", "practicalqueenre00pellrich", 1918,
             "The methods beekeepers used to raise queen bees: the queen and her development, swarm cells, grafting "
             "and cell cups, cell-building colonies, mating nuclei, introducing queens, and the methods of Doolittle, "
             "Alley, Miller and others."),
    old_book("bees", "miller_thousand_answers_beekeeping_1917", "A Thousand Answers to Beekeeping Questions (C. C. "
             "Miller, 1917)", "Beekeeping questions and answers", "C. C. Miller (American Bee Journal)",
             "cu31924003235870", 1917,
             "One of the best-known beekeepers of his day answers a thousand questions sent to the American Bee "
             "Journal, arranged by subject: hives and frames, swarming, queens, feeding, wintering, comb and "
             "extracted honey, and diseases."),
    old_book("bees", "dadant_first_lessons_beekeeping_1918", "First Lessons in Beekeeping (C. P. Dadant, 1918)",
             "Beekeeping for beginners", "C. P. Dadant (American Bee Journal)", "cu31924003445354", 1918,
             "A short course for beginners: the colony and its members, hives and tools, getting started, handling "
             "bees, swarms, honey production, wintering and the common diseases."),
    old_book("bees", "hawkins_beekeeping_in_the_south_1920", "Beekeeping in the South (Kennith Hawkins, 1920)",
             "Beekeeping in the southern states", "Kennith Hawkins (American Bee Journal)", "cu31924003267311", 1920,
             "A handbook of the seasons, methods and honey plants of the fifteen southern states: the beekeeper's "
             "year in a warm climate, equipment, increase, swarm control, queen rearing and the honey flora."),
    gov_book("bees", "usda_benton_honey_bee_manual_1899", "The Honey Bee: a Manual of Instruction in Apiculture "
             "(Frank Benton, USDA, 1899)", "Beekeeping", f"Frank Benton ({USDA}, Division of Entomology)",
             "honeybeemanualof00bentrich", 1899,
             "The USDA's manual of instruction in beekeeping: the races of bees, the colony and its members, honey "
             "plants, hives and appliances, the apiary, handling bees, swarming and increase, queen rearing, comb "
             "and extracted honey, wax, wintering, and diseases and enemies."),
    gov_book("bees", "usda_snodgrass_anatomy_honey_bee_1910", "The Anatomy of the Honey Bee (R. E. Snodgrass, USDA, "
             "1910)", "Bee anatomy", f"R. E. Snodgrass ({USDA}, Bureau of Entomology)", "cu31924003168865", 1910,
             "The classic description of the honey bee's body: the head, mouthparts and antennae, the thorax, legs "
             "and wings, the sting, the wax and other glands, digestion, breathing, circulation, the nervous system "
             "and the sense organs, and the reproductive organs.", dated=False),
    gov_book("bees", "usda_phillips_bees_1911", "Bees (E. F. Phillips, USDA Farmers' Bulletin, 1911)", "Beekeeping",
             f"Everett Franklin Phillips ({USDA})", "beesusdept00phil", 1911,
             "The USDA's short guide to beekeeping for farmers: the colony, hives and equipment, starting and "
             "handling bees, swarming, comb and extracted honey, wintering and the brood diseases."),
    gov_book("bees", "usda_phillips_treatment_bee_diseases_1911", "The Treatment of Bee Diseases (E. F. Phillips, "
             "USDA Farmers' Bulletin, 1911)", "Bee diseases", f"Everett Franklin Phillips ({USDA})",
             "CUbiodiversity424212", 1911,
             "How American and European foulbrood and sacbrood were recognised and treated in 1911: the signs in the "
             "comb, the shaking treatment, requeening, and the care of hives and honey from diseased colonies."),
    gov_book("bees", "usda_american_foulbrood_1920", "American Foulbrood (G. F. White, USDA Bulletin, 1920)",
             "Bee diseases: American foulbrood", f"G. F. White ({USDA})", "americanfoulbroo809whit", 1920,
             "The USDA's study of American foulbrood: the germ that causes it, how it spreads between colonies and "
             "apiaries, how to recognise it in the brood comb, and how it was controlled."),
    gov_book("bees", "usda_european_foulbrood_1920", "European Foulbrood (G. F. White, USDA Bulletin, 1920)",
             "Bee diseases: European foulbrood", f"G. F. White ({USDA})", "europeanfoulbroo810whit", 1920,
             "The USDA's study of European foulbrood: its cause, the signs in the brood, how it spreads, and how "
             "strong colonies and requeening were used against it."),
    gov_book("bees", "usda_demuth_comb_honey_1917", "Comb Honey (George S. Demuth, USDA Farmers' Bulletin, 1917)",
             "Comb honey", f"George S. Demuth ({USDA})", "CAT10306216", 1917,
             "Producing honey in the comb: strong colonies, supers and sections, foundation, swarm control in comb "
             "honey production, removing, cleaning, grading and packing sections."),
    gov_book("bees", "usda_sechrist_transferring_bees_1918", "Transferring Bees to Modern Hives (E. L. Sechrist, USDA "
             "Farmers' Bulletin, 1918)", "Moving bees into frame hives", f"E. L. Sechrist ({USDA})", "CAT87202609",
             1918,
             "How to move a colony from a box hive, gum or tree into a modern movable-frame hive: when to do it, "
             "drumming and driving the bees, cutting and fitting the combs, and letting the bees move up."),
    gov_book("bees", "usda_phillips_wintering_bees_cellars_1918", "Wintering Bees in Cellars (E. F. Phillips, USDA "
             "Farmers' Bulletin, 1918)", "Wintering bees", f"Everett Franklin Phillips ({USDA})", "CAT87202773",
             1918,
             "How colonies were wintered in cellars in cold country: preparing the colonies, the cellar's "
             "temperature, air and quiet, carrying the bees in and out, and spring care."),
    gov_book("bees", "usda_owens_selecting_beekeeping_equipment_1977", "Selecting and Operating Beekeeping Equipment "
             "(Charles D. Owens, USDA Farmers' Bulletin, 1977)", "Beekeeping equipment",
             f"Charles D. Owens ({USDA})", "CAT31108247", 1977,
             "The parts of the modern hive (bottom board, hive bodies, supers, frames and foundation, inner and "
             "outer covers, queen excluders), the beekeeper's tools (smoker, hive tool, veil, gloves), and honey "
             "house equipment for extracting."),
    gov_book("bees", "usda_shimanuki_identification_control_bee_diseases_1983", "Identification and Control of Honey "
             "Bee Diseases (H. Shimanuki, USDA Farmers' Bulletin, 1983)", "Bee diseases",
             f"H. Shimanuki ({USDA})", "CAT31108283", 1983,
             "How to recognise and control the diseases of honey bee brood and adults: American and European "
             "foulbrood, sacbrood, chalkbrood, nosema and others, with what to look for in the comb."),
    gov_book("bees", "usda_ah690_diagnosis_honey_bee_diseases_1991", "Diagnosis of Honey Bee Diseases (USDA "
             "Agriculture Handbook 690, 1991)", "Bee diseases and parasites", USDA, "DiagnosisOfHoneyBeeDiseases",
             1991,
             "The USDA's handbook for apiary inspectors and beekeepers on recognising bee diseases and parasites in "
             "the field and sending samples to the laboratory: the brood diseases, adult bee diseases, Varroa and "
             "tracheal mites, and other pests.", source="A work of the US Department of Agriculture (public "
             "domain), from the Internet Archive's copy."),
    gov_book("bees", "aphis_varroa_mite_manual_1988", "Regulatory and Survey Manual for the Varroa Mite (USDA APHIS, "
             "1988)", "Varroa mites", f"Animal and Plant Health Inspection Service ({USDA})", "CAT88888377", 1988,
             "The manual US inspectors used when the Varroa mite arrived in the United States: what the mite is and "
             "does, how to survey colonies for it (sampling and detection methods), and the rules for moving bees."),
    gov_book("bees", "usda_shimanuki_varroa_mite_1982", "Varroa Mite (H. Shimanuki, USDA APHIS Pest Leaflet, 1982)",
             "Varroa mites", f"H. Shimanuki ({USDA})", "CAT31375506", 1982,
             "A short leaflet written just before Varroa reached the United States: what the mite looks like, its "
             "life on the brood and adult bees, the damage it does, and how it is detected."),
    gov_book("bees", "usda_pesticides_honey_bees_1985", "Pesticides and Honey Bees (W. T. Wilson and others, USDA "
             "Leaflet, 1985)", "Protecting bees from pesticides", f"W. T. Wilson and others ({USDA})",
             "pesticideshoneyb563wils", 1985,
             "How pesticides poison honey bees and how beekeepers and growers can protect colonies: the signs of "
             "poisoning, the more and less dangerous kinds of spray, timing, and moving or covering hives."),
    gov_book("bees", "usda_africanized_honey_bee_1978", "The Africanized Honey Bee (USDA Science and Education "
             "Administration, 1978)", "Africanized honey bees", USDA, "CAT31375337", 1978,
             "A short USDA paper on the Africanized honey bee as it spread north through the Americas: where it came "
             "from, how it behaves, and what it meant for beekeepers."),
]

# ====================================================================== glass blowing and glass work

GLASS = [
    old_book("glass", "shenstone_methods_glass_blowing_1916", "The Methods of Glass-Blowing and of Working Silica in "
             "the Oxy-Gas Flame (W. A. Shenstone, 1916 printing)", "Scientific glassblowing",
             "W. A. Shenstone (Longmans, Green)", "methodsofglassbl00shenuoft", 1916,
             "The classic student's guide to laboratory glassblowing: the blowpipe and table, cutting and bending "
             "tube, joining, blowing bulbs, sealing in platinum wire, making simple apparatus, and working fused "
             "silica in the oxy-gas flame.", country="United Kingdom"),
    old_book("glass", "frary_laboratory_glass_blowing_1914", "Laboratory Manual of Glass-Blowing (Francis C. Frary, "
             "1914)", "Scientific glassblowing", "Francis C. Frary (McGraw-Hill)", "laboratorymanual00frarrich", 1914,
             "A short course of exercises in laboratory glassblowing: the tools and the blast lamp, cutting, bending "
             "and drawing tube, straight and T joints, bulbs, sealing wires and ring seals, and annealing."),
    old_book("glass", "bolas_handbook_laboratory_glass_blowing_1921", "A Handbook of Laboratory Glass-Blowing "
             "(Bernard D. Bolas, 1921)", "Scientific glassblowing", "Bernard D. Bolas (George Routledge and Sons)",
             "handbookoflabora00bola", 1921,
             "A laboratory glassblower's handbook: the glass, the blowpipe and bench, the elementary operations, "
             "joints of every kind, bulbs and vessels, graduating and calibrating, and making and mending "
             "apparatus.", country="United Kingdom"),
    old_book("glass", "bolas_glass_blowing_working_1898", "Glass Blowing and Working, for Amateurs, Experimentalists "
             "and Technicians (Thomas Bolas, 1898)", "Glassblowing and lampwork", "Thomas Bolas (Dawbarn and Ward)",
             "glassblowingwork00bola", 1898,
             "Glass working at the lamp for amateurs and technicians: lamps and blowpipes, the kinds of glass, "
             "cutting, bending, drawing and blowing, making ornamental and scientific pieces, drilling, grinding and "
             "silvering glass.", country="United Kingdom"),
    old_book("glass", "lynde_experimental_glass_blowing_1920", "Experimental Glass Blowing for Boys (Carleton John "
             "Lynde, 1920)", "Glassblowing for beginners", "Carleton John Lynde (A. C. Gilbert Company)",
             "experimentalglas00lynd", 1920,
             "A beginner's glassblowing booklet that came with a home experiment set: the alcohol lamp and blowpipe, "
             "cutting, bending and drawing tube, closing ends, blowing bulbs, and simple experiments."),
    old_book("glass", "threlfall_on_laboratory_arts_1898", "On Laboratory Arts (Richard Threlfall, 1898)",
             "Laboratory glassblowing and workshop methods", "Richard Threlfall (Macmillan)",
             "onlaboratoryarts00threuoft", 1898,
             "A physicist's handbook of the workshop skills a laboratory needs, with a long part on glass blowing "
             "and glass working (the lamp, joints, bulbs, seals, grinding and drilling glass), then silvering, "
             "quartz fibres, electrical work, soldering and cements.", country="United Kingdom"),
    old_book("glass", "woollatt_laboratory_arts_1908", "Laboratory Arts: a Teacher's Handbook (George H. Woollatt, "
             "1908)", "Laboratory glass working and apparatus", "George H. Woollatt (Longmans, Green)",
             "laboratoryartste00woolrich", 1908,
             "A teacher's handbook of the materials and tools for making school laboratory apparatus: glass "
             "working (cutting, bending, blowing and joining tube), cork and rubber boring, wood and metal work, "
             "and cements.", country="United Kingdom"),
    old_book("glass", "danger_art_of_glass_blowing_1831", "The Art of Glass-Blowing, or Plain Instructions for Making "
             "Chemical and Philosophical Instruments (T.-P. Danger, 1831)", "Glassblowing (history)",
             "T.-P. Danger (Bumpus and Griffin)", "gri_33125001061320", 1831,
             "An early glassblowing manual: the lamp and bellows, the glass, and making barometers, thermometers, "
             "hydrometers, hour-glasses, funnels, siphons and toys of glass.", country="United Kingdom"),
    old_book("glass", "holiday_stained_glass_as_an_art_1896", "Stained Glass as an Art (Henry Holiday, 1896)",
             "Stained glass", "Henry Holiday (Macmillan)", "stainedglassasar00holi", 1896,
             "A stained glass designer's account of the craft: the nature of glass and colour, designing for "
             "windows, cutting, painting and firing, leading, and the history of the art.",
             country="United Kingdom", safety=STAINED_NOTE),
    old_book("glass", "werck_stained_glass_handbook_1922", "Stained Glass: a Handbook on the Art of Stained and Painted "
             "Glass (Alfred Werck, 1922)", "Stained glass", "Alfred Werck (N. L. Brown)",
             "stainedglasshand00werc", 1922,
             "A handbook on stained and painted glass, its origin and development, with the materials and methods "
             "of making a window: glass, cartoons, cutting, painting, firing and leading.", safety=STAINED_NOTE),
    gov_book("glass", "nbs_glasses_protecting_eyes_1919", "Glasses for Protecting the Eyes from Injurious Radiations "
             "(W. W. Coblentz and W. B. Emerson, Bureau of Standards Technologic Paper 93, 1919)",
             "Eye protection for glass and furnace work", f"W. W. Coblentz and W. B. Emerson ({NBS})",
             "glassesforpro1919933cobl", 1919,
             "The Bureau of Standards' measurements of which coloured glasses block the ultraviolet and infrared "
             "light of furnaces, welding and glass working, and which are best for the eyes of furnace and glass "
             "workers.", source="A work of the National Bureau of Standards (public domain), from NIST's copy on "
             "the Internet Archive."),
    gov_book("glass", "nbs_annealing_glass_1919", "Concerning the Annealing and Characteristics of Glass (A. Q. Tool "
             "and J. Valasek, Bureau of Standards, 1919)", "Annealing glass", f"A. Q. Tool and J. Valasek ({NBS})",
             "concerninganneal15537tool", 1919,
             "The Bureau of Standards' study of annealing: why glass must be cooled slowly, the strain left by fast "
             "cooling, annealing temperatures and how long to hold them.", source="A work of the National Bureau "
             "of Standards (public domain), from NIST's copy on the Internet Archive.", dated=False),
    gov_book("glass", "nbs_making_glass_disk_telescope_1929", "Making the Glass Disk for a 70-inch Telescope Reflector "
             "(A. N. Finn, Bureau of Standards, 1929)", "Glass making", f"A. N. Finn ({NBS})",
             "makingglassdiskf3231finn", 1929,
             "How the Bureau of Standards melted, poured and annealed a large glass disk for a telescope mirror: the "
             "glass, the furnace and pot, casting, and months of slow cooling.", source="A work of the National "
             "Bureau of Standards (public domain), from NIST's copy on the Internet Archive.", dated=False),
]

# ====================================================================== leather working

LEATHER = [
    old_book("leather", "wilson_leather_work_1908", "Leather Work (Winifred H. Wilson, 1908)", "Leather craft",
             "Winifred H. Wilson (M. B. Willcox)", "leatherwork00wils", 1908,
             "A short craft book of decorative leather work: tools, kinds of leather, modelling, tooling, cutting "
             "and staining, and making small articles."),
    old_book("leather", "leland_leather_work_1925", "Leather Work: a Practical Manual for Learners (Charles G. Leland, "
             "1925 edition)", "Leather craft", "Charles G. Leland (Pitman)", "b1625323", 1925,
             "A practical manual of art leather work for learners: stamped and embossed leather, cuir bouilli "
             "(moulded hard leather), carving and colouring, with designs.", country="United Kingdom"),
    old_book("leather", "hasluck_leather_working_1904", "Leather Working (Paul N. Hasluck, 1904)", "Leather working",
             "Paul N. Hasluck (David McKay)", "leatherworking00hasl", 1904,
             "A workshop handbook of leather working: tools and materials, cutting and stitching, making bags, cases "
             "and straps, embossing and colouring leather, and repairs."),
    old_book("leather", "hasluck_harness_making_1904", "Harness Making (Paul N. Hasluck, 1904)", "Harness making",
             "Paul N. Hasluck (Cassell and Company)", "harnessmaking00hasl", 1904,
             "The harness maker's trade: tools, leather and stitching, then making collars, saddles, bridles, reins, "
             "traces and the other parts of cart and carriage harness.", country="United Kingdom"),
    old_book("leather", "hasluck_saddlery_1904", "Saddlery (Paul N. Hasluck, 1904)", "Saddlery",
             "Paul N. Hasluck (David McKay)", "saddlery00hasl", 1904,
             "Making riding saddles and related gear: the saddle tree, panels and stuffing, seats and flaps, "
             "girths, stirrup leathers, bridles and repairs."),
    old_book("leather", "harness_makers_guide_1907", "The Harness Makers' Guide (Office of Saddlery and Harness, "
             "1907)", "Harness making", "Office of Saddlery and Harness (Walsall)", "harnessmakersgui00offi", 1907,
             "A trade guide giving the lengths for cutting and making harness, bridle work and straps, with notes "
             "on making each part.", country="United Kingdom"),
    old_book("leather", "fitzgerald_harness_makers_manual_1880", "The Harness Makers' Illustrated Manual (William N. "
             "Fitz-Gerald, 1880)", "Harness making", "William N. Fitz-Gerald (New York)", "cu31924000022636", 1880,
             "A practical guide for makers of harness, pads, collars and saddles: leather, tools and stitching, "
             "cutting patterns, and making every part of the harness."),
    old_book("leather", "roehl_harness_repairing_1921", "Harness Repairing (Louis M. Roehl, 1921)", "Harness repair",
             "Louis M. Roehl (Bruce Publishing Company)", "harnessrepairing00roehrich", 1921,
             "A school and farm course in repairing harness: tools, waxed thread and stitching, splicing and "
             "patching straps, buckles and rivets, and oiling and caring for harness."),
    old_book("leather", "dooley_manual_of_shoemaking_1912", "A Manual of Shoemaking and Leather and Rubber Products "
             "(William H. Dooley, 1912)", "Shoemaking", "William H. Dooley (Little, Brown and Company)",
             "manualofshoemaki00dool", 1912,
             "A textbook of the shoe trade: the foot and the last, leathers and how they are tanned, the parts of a "
             "shoe, pattern making, cutting, stitching, lasting, bottoming and finishing, and rubber footwear."),
    old_book("leather", "leno_boot_and_shoemaking_1889", "The Art of Boot and Shoemaking (John Bedford Leno, 1889)",
             "Shoemaking", "John Bedford Leno (Crosby Lockwood and Son)", "artofbootshoemak00leno", 1889,
             "A practical handbook of hand shoemaking: measuring the foot, fitting lasts, cutting out, closing the "
             "uppers, making and finishing boots and shoes, and repairing.", country="United Kingdom"),
    old_book("leather", "levinson_home_shoe_repairing_1916", "Home Book to Learn Expert Shoe Repairing (Joseph M. "
             "Levinson, 1916)", "Shoe repair", "Joseph M. Levinson (Monrovia, California)", "homebooktolearne01levin",
             1916,
             "A short home course in shoe repairing: tools, soling and heeling, sewing rips, patching and finishing."),
    old_book("leather", "rogers_practical_tanning_1922", "Practical Tanning (Allen Rogers, 1922)", "Tanning",
             "Allen Rogers (Henry Carey Baird)", "practicaltanning00roge", 1922,
             "A handbook of the tanning trade of 1922: hides and skins, soaking, liming and unhairing, vegetable and "
             "chrome tanning, currying and finishing, and the leathers made for each use, kept as history of how "
             "leather is made."),
    army("leather", "army_tm_10_430_saddler_1942", "The Saddler (TM 10-430, 1942)", "Saddlery and harness repair",
         WAR_DEPT, "TM10-430", 1942,
         "The US Army's manual for its saddlers: tools, leather and thread, hand stitching, and repairing saddles, "
         "harness, bridles and other horse equipment.", LEATHER_NOTE),
    army("leather", "army_tm_10_269_repair_canvas_webbing_1948", "Repair of Canvas and Webbing (TM 10-269, 1948)",
         "Canvas and webbing repair", ARMY, "tm-10-269-repair-of-canvas-and-webbing-1948", 1948,
         "The US Army's manual for repairing tents, tarpaulins, covers, packs and web equipment: canvas and webbing, "
         "hand and machine stitches, patches and darns, grommets, snaps and buckles, and waterproofing.",
         CANVAS_NOTE),
]

# ====================================================================== clothing making and repair

CLOTHING = [
    old_book("clothing", "vincent_cutters_practical_guide_ladies_1892", "The Cutter's Practical Guide to the Cutting "
             "of Ladies' Garments (W. D. F. Vincent, 1892)", "Tailoring and pattern cutting",
             "W. D. F. Vincent (John Williamson)", "cutterspractical00vinc", 1892,
             "A tailor's guide to drafting and cutting women's tailored garments: measuring, drafting systems, "
             "jackets, coats, bodices, skirts and riding habits, and fitting.", country="United Kingdom"),
    old_book("clothing", "mitchell_standard_work_on_cutting_1886", "The \"Standard\" Work on Cutting (Jno. J. "
             "Mitchell Company, 1886)", "Tailoring and pattern cutting", "Jno. J. Mitchell Company (New York)",
             "standardworkoncu00mitc", 1886,
             "The American tailor's treatise on drafting men's garments: measures, the proportional system, coats, "
             "vests and trousers, and alterations for figure."),
    old_book("clothing", "mitchell_ladies_tailor_made_garments_1921", "The New Standard Work on Designing and "
             "Pattern-Making of Ladies' Tailor-Made Garments (Mitchell, 1921)", "Tailoring and pattern making",
             "Mitchell Publications (New York)", "newstandardworko00mitc", 1921,
             "Drafting patterns for women's tailored coats, jackets, suits and skirts: measures, the foundation "
             "drafts, styles, grading and fitting."),
    old_book("clothing", "picken_pattern_drafting_1920", "Pattern Drafting (Woman's Institute of Domestic Arts and "
             "Sciences, 1920)", "Pattern drafting", "Woman's Institute of Domestic Arts and Sciences (Scranton)",
             "patterdraftingpicken", 1920,
             "A Woman's Institute course in drafting your own patterns: taking measures, drafting the foundation "
             "waist, sleeve and skirt, and changing them for different styles."),
    old_book("clothing", "picken_tailored_buttonholes_1923", "Tailored Buttonholes and Buttons, Seams, Plackets, "
             "Skirts and Pockets (Mary Brooks Picken, Woman's Institute, 1923)", "Tailoring",
             "Mary Brooks Picken (Woman's Institute of Domestic Arts and Sciences)", "pickentailoredbuttonholes1923",
             1923,
             "The Woman's Institute's tailoring lessons: worked and bound buttonholes, sewing on buttons, tailored "
             "seams and plackets, tailored skirts, pockets, and pressing."),
    old_book("clothing", "merwin_american_system_dressmaking_1912", "The American System of Dressmaking (Pearl Merwin, "
             "1912)", "Dressmaking", "Pearl Merwin (The American College of Dressmaking)", "americansystemof03merw",
             1912,
             "A long home-study course in dressmaking: measuring, drafting, cutting and fitting, stitches and seams, "
             "waists, skirts and dresses, finishing, and children's clothes."),
    old_book("clothing", "wakeman_scientific_sewing_1898", "Scientific Sewing and Garment Cutting (Antoinette Van "
             "Hoesen Wakeman and Louise M. Heller, 1898)", "Sewing and garment cutting",
             "Antoinette Van Hoesen Wakeman and Louise M. Heller (Silver, Burdett and Company)",
             "scientificsewing00wake", 1898,
             "A school and home course: hand stitches, seams and hems, patching and darning, then drafting and "
             "cutting simple garments by measurement."),
    old_book("clothing", "conover_draping_pattern_making_1922", "A Complete Course in Dressmaking: Draping and Pattern "
             "Making (Isabel De Nyse Conover, 1922)", "Draping and pattern making",
             "Isabel De Nyse Conover (E. J. Clode)", "completecoursein08cono", 1922,
             "Lesson eight of a twelve-part dressmaking course: draping fabric on a dress form, making and altering "
             "patterns, and fitting."),
    old_book("clothing", "conover_mens_clothes_1922", "A Complete Course in Dressmaking: Men's Clothes and Index "
             "(Isabel De Nyse Conover, 1922)", "Making men's clothes", "Isabel De Nyse Conover (E. J. Clode)",
             "completecoursein00cono", 1922,
             "The last part of a twelve-part dressmaking course: making and remodelling men's and boys' clothes at "
             "home, with the index to the whole course."),
    old_book("clothing", "hughes_ladies_tailor_instructor_1892", "The Ladies' Tailor Complete Instructor (Hughes and "
             "Storey, 1892)", "Tailoring and pattern cutting", "Hughes and Storey (St. Louis)",
             "ladiestailorcomp00hugh", 1892,
             "A short instructor in a tailor's system for cutting women's garments by measure: waists, sleeves, "
             "skirts and jackets."),
    old_book("clothing", "hecklinger_vest_cutting_1883", "Vest Cutting: a Manual for the Practical Tailor and Cutter "
             "(Charles Hecklinger, 1883)", "Tailoring: waistcoats", "Charles Hecklinger (New York)",
             "vestcuttingmanua00heck", 1883,
             "A tailor's manual for drafting and cutting vests (waistcoats) of every style, with the measures and "
             "alterations for figure."),
    old_book("clothing", "bottomley_complete_course_millinery_1919", "A Complete Course in Millinery (Julia "
             "Bottomley, 1919)", "Millinery and hat making", "Julia Bottomley (Illustrated Milliner Company)",
             "completecoursein00bott", 1919,
             "Twenty-four practical lessons in making hats: frames of wire and buckram, covering, straw braids, "
             "facings and bindings, bows, flowers and other trimmings, and renovating."),
    old_book("clothing", "aiken_millinery_1922", "Millinery (Charlotte Rankin Aiken, 1922)",
             "Millinery and hat making", "Charlotte Rankin Aiken (Ronald Press)", "millinery00aikerich", 1922,
             "A textbook of millinery: tools and materials, wire and buckram frames, covering and lining hats, "
             "straw and fabric hats, trimmings, and the hat trade."),
    old_book("clothing", "home_millinery_course_1909", "Home Millinery Course (National Millinery Company, 1909)",
             "Millinery and hat making", "National Millinery Company (Cleveland)", "homemillinerycou00nati", 1909,
             "A series of home lessons in making and trimming hats: frames, covering, bows and trimmings."),
    old_book("clothing", "trilling_girls_problems_home_economics_1926", "A Girl's Problems in Home Economics (Mabel B. "
             "Trilling and Florence Williams, 1926)", "Clothing construction", "Mabel B. Trilling and Florence "
             "Williams (J. B. Lippincott Company)", "girlsproblemsinh00trilrich", 1926,
             "A school textbook whose chapters on clothing cover healthful clothing, dress design, choosing fabrics, "
             "using patterns, and making and caring for clothes, alongside home planning."),
    gov_book("clothing", "usda_fitting_dresses_blouses_1927", "Fitting Dresses and Blouses (Maude Campbell, USDA "
             "Farmers' Bulletin, 1927)", "Fitting clothes", f"Maude Campbell ({USDA})", "CAT87209389", 1927,
             "How to fit dresses and blouses at home: where a garment should fall on the body, and how to correct "
             "common fitting problems at the shoulders, bust, waist and sleeves."),
    gov_book("clothing", "usda_fitting_dresses_1945", "Fitting Dresses (Edna Sommerfeld, USDA Farmers' Bulletin, "
             "1945)", "Fitting clothes", f"Edna E. Sommerfeld ({USDA})", "CAT87204360", 1945,
             "Fitting a dress step by step: what a good fit looks like, and how to fix wrinkles and pulls by "
             "changing seams, darts and hems."),
    gov_book("clothing", "usda_abcs_of_mending_1942", "ABC's of Mending (Clarice L. Scott, USDA Farmers' Bulletin, "
             "1942)", "Mending", f"Clarice L. Scott ({USDA})", "CAT87203517", 1942,
             "Mending clothes and household linens: darning, patching (hemmed, set-in and underlaid patches), "
             "mending tears and worn places, and mending knitted things."),
    gov_book("clothing", "usda_mending_mens_suits_1946", "Mending Men's Suits (Clarice L. Scott, USDA, 1946)",
             "Mending tailored clothes", f"Clarice L. Scott ({USDA})", "mendingmenssuits482scot_0", 1946,
             "Repairing men's suits so the repair hardly shows: reweaving and darning, patching, frayed cuffs and "
             "edges, pockets, linings and buttonholes."),
    gov_book("clothing", "usda_make_overs_coats_suits_1944", "Make-overs from Coats and Suits (Clarice L. Scott, USDA, "
             "1944)", "Remaking clothes", f"Clarice L. Scott ({USDA})", "makeoversfromcoa545scot", 1944,
             "Remaking old coats and suits into new clothes for women and children: taking garments apart, "
             "cleaning and pressing the cloth, and cutting and making the new garment."),
    gov_book("clothing", "usda_make_overs_leather_fur_felt_1946", "Make-overs from Leather, Fur and Felt (Clarice L. "
             "Scott, USDA, 1946)", "Remaking clothes: leather, fur and felt", f"Clarice L. Scott ({USDA})",
             "makeoversfromlea614scot", 1946,
             "Remaking old leather, fur and felt into jackets, vests, mittens, hats, slippers and other things: "
             "taking them apart, cutting and sewing leather and fur, and working felt."),
    gov_book("clothing", "usda_knitwear_make_overs_1945", "Knitwear Make-overs (Clarice L. Scott, USDA, 1945)",
             "Remaking knitted clothes", f"Clarice L. Scott ({USDA})", "knitwearmakeover575scot", 1945,
             "Remaking worn sweaters and other knitted clothes: cutting and sewing knitted cloth, finishing edges, "
             "and making children's clothes from adults' knitwear."),
    gov_book("clothing", "usda_coat_making_at_home_1941", "Coat Making at Home (Margaret Smith, USDA Farmers' Bulletin, "
             "1941)", "Tailoring at home", f"Margaret Smith ({USDA})", "CAT87203733", 1941,
             "Making a tailored coat at home: choosing pattern and cloth, shrinking, cutting and marking, "
             "interfacing, pressing, collars, sleeves, pockets, buttonholes and lining."),
    gov_book("clothing", "usda_work_clothes_for_women_1942", "Work Clothes for Women (Clarice L. Scott, USDA Farmers' "
             "Bulletin, 1942)", "Work clothes", f"Clarice L. Scott ({USDA})", "CAT87203592", 1942,
             "Safe and practical work clothes for women in farm and factory work: overalls, coveralls, slacks, "
             "shirts and caps, with features that keep clothing out of machinery."),
    gov_book("clothing", "usda_sewing_for_girls_club_work_1919", "Sewing for Girls' Club Work (Ola Powell, USDA "
             "Department Circular, 1919)", "Sewing lessons", f"Ola Powell ({USDA}, States Relations Service)",
             "sewingforgirlscl02powe", 1919,
             "Sewing lessons for girls' clubs: the sewing box, hand stitches and seams, patching and darning, and "
             "simple garments to make."),
    gov_book("clothing", "usda_pattern_alteration_1965", "Pattern Alteration: a Guide for Leaders in Clothing Programs "
             "(USDA Home Economics Research Report, 1965)", "Pattern alteration",
             f"Agricultural Research Service ({USDA})", "patternalteratio32unit", 1965,
             "How to change a paper pattern to fit a figure before cutting: measuring, lengthening and shortening, "
             "and altering bust, waist, hips, shoulders, back and sleeves."),
    gov_book("clothing", "usda_sewing_menswear_jackets_1977", "Sewing Menswear: Jackets (USDA Program Aid, 1977)",
             "Tailoring men's jackets", USDA, "CAIN779087760", 1977,
             "Making a man's tailored jacket: pattern and fabric, interfacing, the front and canvas, collar and "
             "lapels, pockets, sleeves, lining and pressing."),
    gov_book("clothing", "usda_sewing_by_hand_1966", "Sewing by Hand: Teaching Guide for Home Economics Program Aides "
             "(USDA Federal Extension Service, 1966)", "Hand sewing",
             f"Federal Extension Service ({USDA})", "CAT10236989", 1966,
             "A teaching guide for hand sewing: threading a needle and knotting thread, the basic stitches, sewing "
             "on buttons and snaps, hems, and simple repairs."),
    gov_book("clothing", "usda_sewing_machines_cleaning_adjusting_1943", "Sewing Machines: Cleaning and Adjusting "
             "(Helen S. Holbrook, USDA Farmers' Bulletin, 1943)", "Sewing machine care",
             f"Helen S. Holbrook ({USDA})", "CAT87204140", 1943,
             "Keeping a home sewing machine running well: cleaning and oiling, adjusting the tension, stitch length "
             "and pressure, the needle and bobbin, and fixing skipped stitches and other troubles. (The makers' own "
             "manuals are in the manual library's sewing machine collection.)"),
]

GUIDES = [
    dict(wikibook(BEE_GROUP, "wikibooks_beekeeping", "Beekeeping", "Beekeeping (Wikibooks)", "Beekeeping",
                  "Wikibooks' open book on beekeeping: getting started, the hive and its parts, the bee suit, smoker "
                  "and hive tool, the colony (queen, workers and drones), seasons, swarms, honey and wax, pests and "
                  "diseases (Varroa, foulbrood, chalkbrood and others), allergies, and a glossary.", BEE_NOTE),
         area="bees"),
    dict(wikibook(GROUP, "wikibooks_sewing", "Sewing", "Sewing (Wikibooks)", "Sewing",
                  "Wikibooks' short open book on sewing: sewing tools, fabric, hand sewing, seams and embroidery.",
                  CLOTHING_NOTE), area="clothing"),
]

PDFS = BEES + GLASS + LEATHER + CLOTHING


def area_keys(area):
    """The keys of one trade ("bees", "glass", "leather", "clothing"), in the order listed."""
    return [f"ctrade:{e['name']}" for e in GUIDES + PDFS if e["area"] == area]


def all_keys():
    """Every key of the module (the request word craft-trades)."""
    return [k for area in AREAS for k in area_keys(area)]


WORDS = {word: (lambda a=area: area_keys(a)) for area, word in AREAS.items()}
WORDS[ALL_WORD] = all_keys
COLLECTION = K.Collection("ctrade", GROUP, guides=GUIDES, pdfs=PDFS, words=WORDS)

LICENCE_LINES = {
    "ctrade_old_books": "Craft trade books on the Internet Archive published before 1931: public domain in the US "
                        "(each item's year is checked at every build, build_textbooks.archive_year, so a later "
                        "reprint is refused); books first published in the UK are kept under the same US rule and "
                        "marked with their country. archive.org's robots.txt allows the files (checked 2026-11-23).",
    "ctrade_us_gov": "USDA, APHIS and National Bureau of Standards publications: works of the US government (17 U.S.C. "
                     "105, checked on govinfo.gov's policies page at every build), read from the National "
                     "Agricultural Library's and NIST's copies on the Internet Archive.",
    "ctrade_army": "US Army manuals TM 10-430 and TM 10-269: judged at every build by the release rule "
                   "(military_release.py) on their own front matter, from the Internet Archive's copies.",
    "ctrade_wikibooks": "Wikibooks' Beekeeping and Sewing: CC BY-SA 4.0 (share-alike), the licence line checked at "
                        "every build; kept apart from the permissive books as every Wikibooks book is.",
}
NOT_INCLUDED = [
    ("University Extension beekeeping, sewing, clothing and leather guides (Penn State, Cornell, Oregon State and "
     "others)", "Each university's copyright, mostly without an open licence; link-only for the owner to open. "
     "Index: https://extension.psu.edu/animals-and-livestock/bees"),
    ("USDA ARS Bee Research Laboratory pages and the Honey Bee Health Coalition's Varroa guide", "The ARS pages are "
     "public domain but homestead.py found www.ars.usda.gov did not answer; the Coalition's guide is its own "
     "copyright. Link-only. Index: https://honeybeehealthcoalition.org/varroa/"),
    ("Peace Corps beekeeping manuals and blacksmithing books", "Built by other helpers' modules (the appropriate "
     "technology and homestead collections), not repeated here. Index: https://archive.org/search?query=peace+corps+"
     "beekeeping"),
    ("Modern beekeeping, glassblowing, leather craft, tailoring and millinery books", "In copyright (lending-only "
     "copies on the Internet Archive); only books published before 1931 and US government works are built. Index: "
     "https://archive.org/search?query=subject%3Aleatherwork"),
    ("Woman's Institute Library of Dressmaking volumes of 1923 to 1925 marked \"0000unse\" on the Internet Archive",
     "Not checked one by one (which volume and printing each is), so left out for now; the Pattern Drafting "
     "(1920) and Tailored Buttonholes (1923) volumes are built. Index: https://archive.org/search?query=woman%27s+"
     "institute+library+of+dressmaking"),
    ("Navy Parachute Rigger, Army FM 10-16 General Fabric Repair and other service fabric manuals", "Left to the navy "
     "rates and service skills collections (service_skills.py builds FM 10-16 as skill:army_fm_10_16_general_fabric_"
     "repair_2000, listed in arts:index), so that no manual is built twice. Index: https://archive.org/search?query=parachute+rigger"),
    ("Leather, glass and sewing machine makers' manuals", "Their makers' copyright; the manual library lists them "
     "(arts:index links the collections). Index: https://archive.org/details/manuals"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
