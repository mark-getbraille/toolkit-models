"""More books for nine thin life-skills sections of the reference library (the owner's request of 2026-11-22):
public-domain books published before 1931, US government works (the USDA Yearbooks of Agriculture and Home and
Garden Bulletins, Forest Service and Park Service books, NASA educator guides) and openly licensed modern guides
(the LibreOffice Impress and Draw guides, the GNOME desktop help). Keys: oldbooks-life (every book), one request
word per section (oldbooks-life-household and the others in AREAS), olife:<name>.

This module adds books to groups that other modules already own. Every book carries the group of its section, so it
is filed beside that module's books in the library (the same group label), and nothing here makes a new group:
  - Reference, cleaning and household management (household.py): housekeeping, laundry, cleaning and home economics
    books (Catharine Beecher, Christine Frederick, Ellen Richards and others), four Yearbooks of Agriculture for the
    home and five Home and Garden Bulletins. Each carries household.py's cleaning safety note (never mix bleach
    and ammonia) and says its old cleaning chemistry may be unsafe today;
  - Reference, musical instrument care (instrument_care.py): violin making, piano tuning and repair, organ building
    and tuning, band instruments, and guitar, mandolin and banjo methods;
  - Reference, gardening and lawn care (gardening.py): the themed Yearbooks of Agriculture (Grass 1948 to Gardening
    for Food and Fun 1977), Home and Garden Bulletins and old gardening, lawn and house-plant books, each saying
    that its old pest remedies are dangerous and banned;
  - Reference, outdoor recreation (outdoors.py): Forest Service and Park Service books (1916 to 1930, and the 1967
    yearbook Outdoors USA), old camping, canoeing, hiking and fishing books not already in bushcraft.py, outdoors.py,
    knots_outdoor.py or small_boats.py, and old bird books;
  - Reference, science you can use (science_use.py): old popular science (Faraday, Tyndall, Huxley, Serviss,
    Olcott, Ball, Slosson, Thomson's Outline of Science, Comstock's Handbook of Nature-Study, Yule's statistics),
    two yearbooks (Climate and Man 1941, Science for Better Living 1968) and seven NASA educator guides;
  - Reference, computer and phone basics (computer_basics.py): the LibreOffice Impress Guide and Draw Guide
    (CC BY 4.0, read the same way as computer_basics.lo_guide) and the GNOME desktop help (CC BY-SA 3.0,
    share-alike, a separate book; its accessibility pages are already a11yc:gnome_help_accessibility);
  - Reference, typing and keyboard skills (typing_skills.py): more old touch typing courses;
  - Reference, audio and media production (audio_media.py): old phonograph, early radio broadcasting and motion
    picture books, kept as history;
  - Reference, genealogy (genealogy.py): old genealogy handbooks, the Census Bureau's A Century of Population Growth
    (1909, with the commonest surnames of 1790) and Fox-Davies's guide to heraldry;
  - Reference, communication and relationships (relationships.py): Emily Post's Etiquette (1922), Esenwein and
    Carnegie's The Art of Public Speaking (1915), conversation books and letter-writers, each marked as historical
    in its attitudes.

How each kind of book is read and checked, in plain words:
  - an old book (old_ia_books.old_book): the Internet Archive's scan with its text layer, read whole, only when the
    item's own record shows it was published before 1931 (the builder checks the year at every build); its
    description ends with what is out of date in it;
  - a US government book (refs_kit.us_pdf): the Internet Archive's scan (the USDA National Agricultural Library's
    own scans of the Yearbooks and bulletins, ERIC's copies of the NASA guides), a work of the US government
    (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
  - a web guide: every page, its licence line read on its licence page at every build.
Every item was looked up on 2026-11-22: its record's date, a downloadable PDF with words (no lending-library or
picture-only scans), and that no other module of the library names it.

Run from the repository's folder:
  python3 textbooks/oldbooks_life.py --list oldbooks-life-household
  python3 textbooks/oldbooks_life.py olife:post_etiquette_1922 --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402
import computer_basics as CB  # noqa: E402 - the LibreOffice guide entry and the computer safety note
import gardening as GA  # noqa: E402 - the garden safety note
import genealogy as GE  # noqa: E402 - the records note
import household as HO  # noqa: E402 - the cleaning safety note and the old household note
import instrument_care as IC  # noqa: E402 - the instrument safety note
import outdoors as OD  # noqa: E402 - the outdoor safety note
import typing_skills as TY  # noqa: E402 - the typewriter note

PREFIX = "olife"
GROUPS = {}                 # every group here is an existing module's (see the module docstring)

# ====================================================================== the notes (what is out of date)

INSTR_NOTE = ("Published in {year}: an old book. Its glues, varnishes and finishes (some with lead, arsenic or strong "
              "solvents), its prices, makers and some methods are out of date; it is kept for its explanations of how "
              "instruments are built, tuned and cared for. Take a valuable instrument to a qualified repairer. The "
              "machine-read text has the scanner's mistakes, and music examples are not read.")
METHOD_NOTE = ("Published in {year}: an old playing method, kept for its explanations of holding, tuning and "
               "stringing the instrument and its exercises; the music itself is in notation the machine-read text "
               "cannot give (look for the tunes in the library's sheet music), and its strings and gear are of its "
               "time.")
GARDEN_NOTE = ("Published in {year}: an old book. Its pest and disease remedies (arsenic, lead arsenate, Paris green, "
               "nicotine, mercury and other poisons) are dangerous and now banned; plant names and varieties have "
               "changed. It is kept for its explanations of soil, sowing, planting and care. The machine-read text "
               "has the scanner's mistakes.")
OUT_NOTE = ("Published in {year}: an old book. Its camp practices (cutting live trees and boughs for beds and "
            "shelters, trenching tents, big open fires, killing wildlife for food), its gear and its first aid are "
            "out of date and often against today's rules: follow Leave No Trace and the rules of the park or forest. "
            "It is kept for its explanations of camp skills. The machine-read text has the scanner's mistakes.")
BIRD_NOTE = ("Published in {year}: an old bird book. Many birds' names and ranges have changed, some birds it "
             "describes are now rare, and collecting birds or eggs, which it may describe, is against the law "
             "(wild birds are protected); watch and listen instead. The machine-read text has the scanner's "
             "mistakes, and the colour plates are described only by their captions.")
FISH_NOTE = ("Published in {year}: an old angling book. Fishing licences, seasons and limits are set by each state "
             "today (check them before you fish), and its tackle is of its time; it is kept for its explanations of "
             "fish and fishing. The machine-read text has the scanner's mistakes.")
GOV_OUT_NOTE = ("Published in {year} by the US government: an old book. Park and forest rules, roads, fees and "
                "facilities have all changed; check the park's or forest's own pages before you go.")
SCI_NOTE = ("Published in {year}: an old popular science book. Much of its science has moved on (it was written "
            "before much of what is known today), so check facts in a current book; it is kept for its plain "
            "explanations. Do not repeat its experiments with flames, chemicals or electricity without proper "
            "supervision. The machine-read text has the scanner's mistakes.")
SKY_SAFETY = "Never look at the Sun, with or without binoculars or a telescope: it blinds."
MEDIA_NOTE = ("Published in {year}: an old book kept as history of sound recording, radio and film. Its equipment is "
              "long obsolete: old nitrate film is highly flammable, and old radio sets and amplifiers hold dangerous "
              "voltages even when unplugged. The machine-read text has the scanner's mistakes.")
GEN_NOTE = ("Published in {year}: an old genealogy guide. The record offices, archives, addresses and laws it names "
            "have moved or changed and many records are now online; it is kept for its methods and explanations. "
            "The machine-read text has the scanner's mistakes.")
RELATE_NOTE = ("Published in {year}: historical, not current advice. Its manners and attitudes are of their time "
               "(about women and men, marriage, class, servants and race), and some are offensive today; it is kept "
               "for what it says about listening, courtesy, speaking and writing clearly. The machine-read text has "
               "the scanner's mistakes.")
YEARBOOK_NOTICE = ("A Yearbook of Agriculture of the US Department of Agriculture, a US government work (public "
                   "domain), read from the National Agricultural Library's scan on the Internet Archive (the "
                   "machine-read text has the scanner's mistakes). Published in {year}: the pesticides and other "
                   "chemicals it names may now be banned or restricted, and its prices and programmes are of its "
                   "time; follow today's labels and ask your local cooperative extension office.")
BULLETIN_NOTICE = ("A USDA bulletin, a US government work (public domain), read from the National Agricultural "
                   "Library's scan on the Internet Archive (the machine-read text has the scanner's mistakes). "
                   "Published in {year}: the chemicals it names may no longer be sold or allowed; follow today's "
                   "product labels.")
NASA_NOTICE = ("A NASA educator guide, a work of the US government (public domain; NASA says its material is "
               "generally not subject to copyright in the United States), read from ERIC's copy on the Internet "
               "Archive. Published in {year}: missions and facts are as they were then. Activities with heat, sharp "
               "tools or chemicals need an adult.")
HOUSE_EXTRA = " " + HO.CLEAN_SAFETY


def _old(group, name, title, subject, publisher, archive, year, description, note, notice="",
         country="United States"):
    """One old public-domain book of the Internet Archive (published before 1931) for a section's group."""
    return old_book(group, name, title, subject, publisher, archive, year, description, note=note, notice=notice,
                    country=country)


def _gov(group, name, title, subject, publisher, archive, year, description, notice):
    """One US government book read from the Internet Archive (a newer one: after 1930), with its notice."""
    return K.us_pdf(group, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                    description=description, notice=notice.format(year=year))


def _yearbook(group, name, title, subject, archive, year, description, extra=""):
    """One themed Yearbook of Agriculture (the National Agricultural Library's scan, item yoa<year>)."""
    return _gov(group, name, title, subject, "US Department of Agriculture", archive, year, description,
                YEARBOOK_NOTICE + extra)


def _bulletin(group, name, title, subject, archive, year, description, extra=""):
    """One USDA Home and Garden Bulletin or other USDA leaflet."""
    return _gov(group, name, title, subject, "US Department of Agriculture", archive, year, description,
                BULLETIN_NOTICE + extra)


# ====================================================================== cleaning and household management

HOUSE = HO.GROUP
HOUSEHOLD = [
    _old(HOUSE, "beecher_stowe_american_womans_home_1869", "The American Woman's Home (Catharine E. Beecher and "
         "Harriet Beecher Stowe, 1869)", "Housekeeping and home economics", "Catharine E. Beecher and Harriet Beecher "
         "Stowe (J. B. Ford)", "americanwomansho00beecrich", 1869,
         "The Beecher sisters' guide to running a home: planning the house, heating and fresh air, cleanliness, "
         "furniture, the kitchen, food and cooking, the care of the sick, children and the household's work.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "beecher_treatise_domestic_economy_1848", "A Treatise on Domestic Economy (Catharine E. Beecher, "
         "1848)", "Housekeeping and home economics", "Catharine E. Beecher (Harper and Brothers)",
         "treatiseondomest00beec", 1848,
         "Catharine Beecher's textbook of home management for young women: health, food, clothing, cleanliness, "
         "the care of rooms, washing, the kitchen, the garden, economy of time and money, and the care of the sick.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "frederick_new_housekeeping_1913", "The New Housekeeping: Efficiency Studies in Home Management "
         "(Christine Frederick, 1913)", "Household management", "Christine Frederick (Doubleday, Page)",
         "newhousekeeping00fredrich", 1913,
         "Christine Frederick's first book of efficient housework: standard heights and the order of work in the "
         "kitchen, planning the day and week, tools that save effort, buying, records and accounts.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "frederick_you_and_your_laundry_1922", "You and Your Laundry (Christine Frederick, 1922)",
         "Laundry", "Christine Frederick (The Hurley Machine Company)", "youyourlaundry00fred", 1922,
         "A short guide to doing the family wash with an electric washing machine, written for a washing machine "
         "maker: sorting, soaking, washing, rinsing, bluing, drying and ironing.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "richards_chemistry_cooking_cleaning_1882", "The Chemistry of Cooking and Cleaning (Ellen H. "
         "Richards, 1882)", "Cleaning chemistry", "Ellen H. Richards (Estes and Lauriat)", "chemistrycooking00richiala",
         1882,
         "A chemist's manual for housekeepers: what food and dirt are made of, soap and how it cleans, washing "
         "soda, ammonia and other cleaners, removing stains and the chemistry of cooking.",
         HO.OLD_HOUSEHOLD_NOTE + " Its cleaning chemistry in particular is out of date and may be unsafe.",
         HOUSE_EXTRA),
    _old(HOUSE, "richards_home_sanitation_1904", "Home Sanitation: A Manual for Housekeepers (Ellen H. Richards and "
         "Marion Talbot, 1904)", "Home hygiene", "Ellen H. Richards (Whitcomb and Barrows)", "homesanitationma00richrich",
         1904,
         "Questions and answers for keeping a house healthy: its site, cellar, drains and plumbing, water supply, "
         "heating and fresh air, lighting, cleaning and the removal of waste.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "chambers_guide_laundry_work_1915", "A Guide to Laundry-Work: A Manual for Home and School (Mary D. "
         "Chambers, 1915)", "Laundry", "Mary D. Chambers (Boston Cooking-School Magazine)", "cu31924003596818", 1915,
         "Laundry at home step by step: water and soap, soaking, washing white and coloured clothes, woollens and "
         "silks, starching, bluing, drying, ironing and removing stains.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "jack_art_of_laundry_work_1896", "The Art of Laundry Work (Florence B. Jack, 1896)", "Laundry",
         "Florence B. Jack (T. C. and E. C. Jack, Edinburgh)", "artoflaundrywork00jackiala", 1896,
         "A Scottish laundry teacher's lessons for homes and schools: the laundry and its tools, washing each kind "
         "of fabric, starching, ironing and folding, and removing stains.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA, country="United Kingdom"),
    _old(HOUSE, "balderston_laundry_manual_1913", "Laundry Manual (Lydia Ray Balderston and M. C. Limerick, 1913)",
         "Laundry", "Lydia Ray Balderston (Philadelphia)", "laundrymanual00baldrich", 1913,
         "A short laundry textbook: equipment, water softening, soaps, washing, starching, bluing, ironing and "
         "stain removal, with lessons for classes.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "laundry_manual_washing_made_easy_1863", "The Laundry Manual; or, Washing Made Easy (1863)",
         "Laundry", "Published by the author (New York)", "laundrymanualorw00newy", 1863,
         "A small mid-nineteenth-century guide to washing clothes by hand: soaking, boiling, rinsing, bluing, "
         "starching and ironing.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "bentley_good_housekeeping_business_1924", "Good Housekeeping's Book on the Business of Housekeeping "
         "(Mildred Maddocks Bentley, 1924)", "Household management", "Mildred Maddocks Bentley (Good Housekeeping)",
         "goodhousekeeping00bent", 1924,
         "Running a home as a business: planning work and schedules, the budget and accounts, buying, cleaning "
         "routines, laundry, and household equipment.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "parloa_home_economics_1898", "Home Economics: A Guide to Household Management (Maria Parloa, 1898)",
         "Housekeeping and home economics", "Maria Parloa (The Century Company)", "homeeconomicsgui00parluoft", 1898,
         "A complete household guide: the care of each room, floors, woodwork, furniture, metals and glass, the "
         "kitchen, the laundry, the store-room, and the duties of the household.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "campbell_household_economics_1900", "Household Economics (Helen Campbell, 1900 printing)",
         "Household economics", "Helen Campbell (G. P. Putnam's Sons)", "householdeconomi00camprich", 1900,
         "Lectures given at the University of Wisconsin on the household as a working economy: the house, food, "
         "clothing, cleaning, service and the household budget.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _old(HOUSE, "snell_elementary_household_chemistry_1914", "Elementary Household Chemistry (John F. Snell, 1914)",
         "Cleaning chemistry", "John F. Snell (Macmillan)", "elementaryhouseh00snelrich", 1914,
         "An introductory chemistry textbook for home economics students: water, air, fuels, food, soap and "
         "cleaning agents, bleaches, stain removal and textiles.",
         HO.OLD_HOUSEHOLD_NOTE + " Its cleaning chemistry in particular is out of date and may be unsafe.",
         HOUSE_EXTRA),
    _old(HOUSE, "beezley_national_course_home_economics_1917", "The National Course in Home Economics (Ruth A. "
         "Beezley and others, 1917)", "Housekeeping and home economics", "Ruth Allen Beezley and others (Chicago)",
         "nationalcoursein00beez", 1917,
         "A home-study course in household economy: food and meals, cleaning and laundry, sewing and clothing, the "
         "household budget and the care of the family.",
         HO.OLD_HOUSEHOLD_NOTE, HOUSE_EXTRA),
    _yearbook(HOUSE, "usda_yearbook_1965_consumers_all", "Consumers All: The Yearbook of Agriculture 1965",
              "Buying and caring for things at home", "yoa1965", 1965,
              "The USDA's yearbook for consumers: buying and caring for food, clothing, the house and its "
              "furnishings, and managing the family's money.", HOUSE_EXTRA),
    _yearbook(HOUSE, "usda_yearbook_1973_handbook_for_the_home", "Handbook for the Home: The Yearbook of "
              "Agriculture 1973", "Running a home", "yoa1973", 1973,
              "The USDA's yearbook on running a home: housing, furnishings and equipment and their care, food, "
              "clothing, the family's money and health.", HOUSE_EXTRA),
    _yearbook(HOUSE, "usda_yearbook_1974_shoppers_guide", "Shopper's Guide: The Yearbook of Agriculture 1974",
              "Buying wisely", "yoa1974", 1974,
              "The USDA's yearbook on shopping: buying food, clothing, furniture, appliances and other things for "
              "the home, and getting good value.", HOUSE_EXTRA),
    _yearbook(HOUSE, "usda_yearbook_1980_cutting_energy_costs", "Cutting Energy Costs: The 1980 Yearbook of "
              "Agriculture", "Saving energy at home", "yoa1980", 1980,
              "The USDA's yearbook on saving energy: insulation, heating and cooling the home, wood stoves, solar "
              "energy, appliances, transport, and energy on the farm.",
              " Wood stove and heater advice of 1980: follow today's codes and the maker's instructions, and have a "
              "carbon monoxide alarm." + HOUSE_EXTRA),
    _bulletin(HOUSE, "usda_clothing_repairs_1965", "Clothing Repairs (USDA Home and Garden Bulletin, 1965)",
              "Mending clothes", "CAT87213559", 1965,
              "Mending clothes by hand and machine: patches, darns, worn collars and cuffs, seams, zippers, "
              "buttons and fastenings."),
    _bulletin(HOUSE, "usda_storing_perishable_foods_1961", "Storing Perishable Foods in the Home (USDA, 1961)",
              "Storing food", "CAT87213598", 1961,
              "How long fresh foods keep and how to store them in the refrigerator, freezer and cupboard: meat, "
              "poultry, fish, eggs, milk, fruit and vegetables, and leftovers.",
              " Keep the refrigerator at 40 F (4 C) or below and the freezer at 0 F (-18 C)."),
    _bulletin(HOUSE, "usda_equipment_cooling_home_1965", "Equipment for Cooling Your Home (USDA Home and Garden "
              "Bulletin, 1965)", "Cooling the home", "CAT31045481", 1965,
              "Choosing and using fans, evaporative coolers and room and central air conditioners, and keeping a "
              "house cool with shade and ventilation."),
    _bulletin(HOUSE, "usda_subterranean_termites_1969", "Subterranean Termites: Their Prevention and Control in "
              "Buildings (USDA Home and Garden Bulletin, 1969)", "Termites", "CAT10248622", 1969,
              "How termites damage wood, the signs to look for, building so termites cannot get in, and treating "
              "an infested house.",
              " The soil chemicals it names (chlordane, aldrin, dieldrin and heptachlor) were banned in the US in "
              "the 1970s and 1980s; use a licensed pest control company."),
    _gov(HOUSE, "usda_controlling_household_pests_1976", "Controlling Household Pests (USDA Home and Garden Bulletin "
         "No. 96, 1976)", "Household pests", "US Department of Agriculture", "ERIC_ED154984", 1976,
         "Cockroaches, ants, silverfish, clothes moths, carpet beetles, flies, mosquitoes, fleas, bed bugs and "
         "other household pests: identifying them, keeping them out, and controlling them.",
         "A USDA bulletin, a US government work (public domain), read from ERIC's copy on the Internet Archive. "
         "Published in {year}: many of the insecticides it names are no longer sold or allowed; follow today's "
         "labels." + HOUSE_EXTRA),
]

# Every household book carries the cleaning safety note (the old books and yearbooks have it already).
for _e in HOUSEHOLD:
    if HO.CLEAN_SAFETY not in _e["notice"]:
        _e["notice"] += HOUSE_EXTRA

# ====================================================================== musical instrument care

INSTR = IC.GROUP
INSTRUMENTS = [
    _old(INSTR, "abele_violin_and_its_story_1905", "The Violin and Its Story: or, the History and Construction of "
         "the Violin (Hyacinth Abele, 1905)", "Violin making (old book)", "Hyacinth Abele (The Strad, London)",
         "violinitsstoryor00abeluoft", 1905,
         "The history of the violin and how it is constructed: the wood, the parts, varnish, the bow and the "
         "great makers.", INSTR_NOTE, IC.SAFETY, country="United Kingdom"),
    _old(INSTR, "riechers_violin_art_of_construction_1895", "The Violin and the Art of Its Construction (August "
         "Riechers, 1895)", "Violin making (old book)", "August Riechers (F. Wunder, Göttingen)",
         "violinartofitsco00riecuoft", 1895,
         "A violin maker's treatise on building a violin after Stradivari: the wood, the model, the plates and "
         "their thicknesses, the bass bar, the neck and setting up.", INSTR_NOTE, IC.SAFETY, country="Germany"),
    _old(INSTR, "oakes_ancient_modern_violin_making_1899", "A Review of Ancient and Modern Violin Making (W. W. "
         "Oakes, 1899)", "Violin making (old book)", "W. W. Oakes (Metropolitan Printing and Binding Co.)",
         "reviewofancienta014212mbp", 1899,
         "A comparison of old and newer violin making: woods, varnish, construction and tone.", INSTR_NOTE,
         IC.SAFETY),
    _old(INSTR, "rimbault_pianoforte_construction_1860", "The Pianoforte: Its Origin, Progress and Construction "
         "(Edward F. Rimbault, 1860)", "Pianos (old book)", "Edward F. Rimbault (Robert Cocks, London)",
         "pianoforteitsori00rimbuoft", 1860,
         "The history of keyboard instruments and the piano, and how a piano is built: the frame, strings, "
         "soundboard and action.", INSTR_NOTE, IC.SAFETY, country="United Kingdom"),
    _old(INSTR, "fischer_piano_tuning_regulating_1907", "Piano Tuning, Regulating and Repairing (J. Cree Fischer, "
         "1907)", "Piano tuning and repair (old book)", "J. Cree Fischer (Theodore Presser)",
         "pianotuningregul0000fisc", 1907,
         "A self-instruction course for piano tuners: the piano's parts, temperament and setting the bearings, "
         "tuning unisons and octaves, regulating the action, and common repairs.", INSTR_NOTE, IC.SAFETY),
    _old(INSTR, "moore_pianoforte_tuning_1919", "Pianoforte Tuning (H. Keatley Moore, 1919)",
         "Piano tuning (old book)", "H. Keatley Moore", "MoorePianoforteTuning", 1919,
         "A short guide to tuning the piano: the tools, the scale and temperament, and the order of tuning.",
         INSTR_NOTE, IC.SAFETY, country="United Kingdom"),
    _old(INSTR, "baldwin_manuelo_player_piano_care_1916", "The Manuelo Player Piano: Care, Regulation, Repair "
         "(Baldwin Piano Company, 1916)", "Player pianos (old book)", "The Baldwin Piano Company",
         "manueloplayerpia00bald", 1916,
         "The maker's booklet on its player piano: how the pneumatic player works, its care, regulation and "
         "repair.", INSTR_NOTE, IC.SAFETY),
    _old(INSTR, "wicks_organ_building_for_amateurs_1900", "Organ Building for Amateurs (Mark Wicks, 1900 printing)",
         "Organ building (old book)", "Mark Wicks", "organbuildingfor00wick", 1900,
         "A practical guide for home workers building a small pipe organ: the wind chest, bellows, pipes, "
         "keyboard and action, with specifications.", INSTR_NOTE, IC.SAFETY, country="United Kingdom"),
    _old(INSTR, "hopkins_organ_history_construction_1870", "The Organ: Its History and Construction (E. J. Hopkins "
         "and E. F. Rimbault, 1870)", "Organs (old book)", "E. J. Hopkins (Robert Cocks, London)", "cu31924022263655",
         1870,
         "The standard Victorian book on the organ: its history, the parts of the organ, its pipes and stops, "
         "and how organs are built and voiced.", INSTR_NOTE, IC.SAFETY, country="United Kingdom"),
    _old(INSTR, "hinton_organ_construction_1900", "Organ Construction (J. W. Hinton, 1900)", "Organ building (old "
         "book)", "J. W. Hinton (London)", "organconstructio00hint", 1900,
         "The construction of the pipe organ: the wind supply, chests, pipes, actions and stops.", INSTR_NOTE,
         IC.SAFETY, country="United Kingdom"),
    _old(INSTR, "audsley_art_of_organ_building_vol2_1905", "The Art of Organ-Building, volume 2 (George Ashdown "
         "Audsley, 1905)", "Organ building (old book)", "George Ashdown Audsley (Dodd, Mead)", "gri_33125010939367",
         1905,
         "The second volume of Audsley's great treatise on building concert, church and chamber organs: the "
         "mechanical construction of the organ (this scan holds volume 2 only).", INSTR_NOTE, IC.SAFETY),
    _old(INSTR, "clappe_wind_band_instruments_1912", "The Wind-Band and Its Instruments (Arthur A. Clappé, 1912)",
         "Band instruments (old book)", "Arthur A. Clappé (W. Reeves, London)", "windbanditsinstr00clap", 1912,
         "The history, construction, acoustics and technique of the instruments of the wind band (flutes, reeds, "
         "brass and drums), and the band itself.", INSTR_NOTE, IC.SAFETY),
    _old(INSTR, "goldman_amateur_band_guide_1916", "The Amateur Band Guide and Aid to Leaders (Edwin Franko Goldman, "
         "1916)", "Band instruments (old book)", "Edwin Franko Goldman (Carl Fischer)", "amateurbandguide00gold",
         1916,
         "A reference for wind instrument players and band leaders: each band instrument, its range and care, "
         "organising and rehearsing a band.", INSTR_NOTE, IC.SAFETY),
    _old(INSTR, "gallo_band_book_1921", "Gallo's Band Book: A Treatise on Wind Instruments (Stanislao Gallo, 1921)",
         "Band instruments (old book)", "Stanislao Gallo (Boston Music Company)", "gallosbandbooktr01gall", 1921,
         "A treatise on wind instruments and on the symphony and military band: each instrument, its range and "
         "use, and scoring for band.", INSTR_NOTE, IC.SAFETY),
    _old(INSTR, "foden_grand_method_guitar_1920", "Foden's Grand Method for Guitar, book 1 (William Foden, 1920)",
         "Guitar (old method)", "William Foden", "fodens-grand-method-for-guitar-book-1", 1920,
         "The first book of William Foden's guitar method: holding the guitar, tuning, the notes on the "
         "fingerboard and graded exercises.", METHOD_NOTE, IC.SAFETY),
    _old(INSTR, "holland_comprehensive_method_guitar_1874", "Holland's Comprehensive Method for the Guitar (Justin "
         "Holland, 1874)", "Guitar (old method)", "Justin Holland (Oliver Ditson)", "hollandscomprehe00holl", 1874,
         "The guitar method of Justin Holland, the African American guitarist and teacher: the elements of music, "
         "holding and tuning the guitar, and graded lessons.", METHOD_NOTE, IC.SAFETY),
    _old(INSTR, "converse_banjo_how_to_play_1872", "The Banjo and How to Play It (Frank B. Converse, 1872)",
         "Banjo (old method)", "Frank B. Converse", "FBCBanjo1871", 1872,
         "One of the first banjo methods: the banjo's parts, stringing and tuning, holding it, and lessons.",
         METHOD_NOTE, IC.SAFETY),
    _old(INSTR, "grimshaw_banjo_how_to_play_1922", "The Banjo and How to Play It (Emile Grimshaw, 1922)",
         "Banjo (old method)", "Emile Grimshaw (London)", "the-banjo-and-how-to-play-it-emile-grimshaw", 1922,
         "A banjo tutor by the English player Emile Grimshaw: the instrument and its care, tuning, technique and "
         "exercises.", METHOD_NOTE, IC.SAFETY, country="United Kingdom"),
]

# ====================================================================== gardening and lawn care

GARDEN = GA.GROUP
GARDENING = [
    _yearbook(GARDEN, "usda_yearbook_1938_soils_and_men", "Soils and Men: The Yearbook of Agriculture 1938",
              "Soil", "yoa1938", 1938,
              "The USDA's great yearbook on the soil: how soils form, soil fertility and conservation, erosion, "
              "fertilizers and manures, and the soils of the United States."),
    _yearbook(GARDEN, "usda_yearbook_1948_grass", "Grass: The Yearbook of Agriculture 1948", "Grasses and lawns",
              "yoa1948", 1948,
              "The USDA's yearbook on grasses: grasses for pasture, hay and soil conservation, lawns and turf, "
              "grass seed, and the grasses of each region."),
    _yearbook(GARDEN, "usda_yearbook_1949_trees", "Trees: The Yearbook of Agriculture 1949", "Trees", "yoa1949", 1949,
              "The USDA's yearbook on trees: trees around the home and in towns, planting and care, tree diseases "
              "and insects, forests and woodlands, and a guide to important trees."),
    _yearbook(GARDEN, "usda_yearbook_1952_insects", "Insects: The Yearbook of Agriculture 1952", "Garden insects",
              "yoa1952", 1952,
              "The USDA's yearbook on insects: helpful insects and pests of gardens, crops, homes and animals, how "
              "they live, and how they were controlled in 1952.",
              " It recommends insecticides such as DDT, chlordane and parathion that are now banned in the US."),
    _yearbook(GARDEN, "usda_yearbook_1953_plant_diseases", "Plant Diseases: The Yearbook of Agriculture 1953",
              "Plant diseases", "yoa1953", 1953,
              "The USDA's yearbook on plant diseases: fungi, bacteria and viruses, the diseases of vegetables, "
              "fruits, flowers, trees and lawns, and how to prevent and control them."),
    _yearbook(GARDEN, "usda_yearbook_1955_water", "Water: The Yearbook of Agriculture 1955", "Water", "yoa1955", 1955,
              "The USDA's yearbook on water: rain and the water cycle, water in the soil, irrigation, watering, "
              "ponds and wells, floods and water conservation."),
    _yearbook(GARDEN, "usda_yearbook_1957_soil", "Soil: The Yearbook of Agriculture 1957", "Soil", "yoa1957", 1957,
              "The USDA's yearbook on soil management: soil and plant nutrients, fertilizers and lime, organic "
              "matter, tillage, and soils for gardens, lawns and crops in each region."),
    _yearbook(GARDEN, "usda_yearbook_1961_seeds", "Seeds: The Yearbook of Agriculture 1961", "Seeds", "yoa1961", 1961,
              "The USDA's yearbook on seeds: how seeds form and sprout, producing, testing, storing and certifying "
              "seed, and seeds of vegetables, flowers, grasses and trees."),
    _yearbook(GARDEN, "usda_yearbook_1972_landscape_for_living", "Landscape for Living: The Yearbook of "
              "Agriculture 1972", "Landscaping", "yoa1972", 1972,
              "The USDA's yearbook on landscaping: planning the home grounds, trees, shrubs, lawns and flowers, "
              "gardens in cities and the countryside, and the wider landscape."),
    _yearbook(GARDEN, "usda_yearbook_1977_gardening_for_food_and_fun", "Gardening for Food and Fun: The Yearbook of "
              "Agriculture 1977", "Home gardening", "yoa1977", 1977,
              "The USDA's gardening yearbook: planning a vegetable garden, soil and compost, seeds and "
              "transplants, growing vegetables, fruit, herbs and flowers, lawns, container and community gardens, "
              "and pests."),
    _yearbook(GARDEN, "usda_yearbook_1978_living_on_a_few_acres", "Living on a Few Acres: The Yearbook of "
              "Agriculture 1978", "Small acreage and gardens", "yoa1978", 1978,
              "The USDA's yearbook for people living on a few acres: choosing land, water and wells, gardens and "
              "orchards, small livestock, woodlots, and making a living."),
    _bulletin(GARDEN, "usda_suburban_farm_vegetable_gardens_1967", "Suburban and Farm Vegetable Gardens (USDA Home "
              "and Garden Bulletin, 1967)", "Vegetable gardening", "CAT10235055", 1967,
              "Planning, planting and tending a vegetable garden: the site, soil, fertilizer, when to plant, each "
              "vegetable's needs, and harvesting."),
    _bulletin(GARDEN, "usda_insects_diseases_vegetables_1975", "Insects and Diseases of Vegetables in the Home "
              "Garden (USDA Home and Garden Bulletin, 1975)", "Garden pests", "CAT87210097", 1975,
              "Identifying the insects and diseases of home garden vegetables, crop by crop, and how they were "
              "controlled."),
    _bulletin(GARDEN, "usda_lawn_diseases_1971", "Lawn Diseases: How to Control Them (USDA Home and Garden Bulletin, "
              "1971)", "Lawn care", "CAT31127027", 1971,
              "The common diseases of lawn grasses (brown patch, dollar spot, snow mould, rusts and others): how to "
              "recognise them and keep a lawn healthy."),
    _bulletin(GARDEN, "usda_roses_for_the_home_1953", "Roses for the Home (USDA Home and Garden Bulletin, 1953)",
              "Roses", "CAT31040015", 1953,
              "Growing roses at home: choosing kinds, planting, feeding, watering, pruning, winter protection, and "
              "pests and diseases."),
    _bulletin(GARDEN, "usfs_protecting_shade_trees_1971", "Protecting Shade Trees During Home Construction (USDA "
              "Forest Service, 1971)", "Trees", "nfsl_1_37095", 1971,
              "Keeping trees alive while a house is built near them: protecting roots, trunks and soil, and "
              "grading around trees."),
    _bulletin(GARDEN, "usda_pruning_shade_trees_1965", "Pruning Shade Trees and Repairing Their Injuries (USDA, 1965)",
              "Trees", "nfsl_1_137254", 1965,
              "When and how to prune shade trees, remove limbs safely, and treat wounds and storm damage.",
              " Leave work high in trees and near power lines to a trained arborist."),
    _old(GARDEN, "bailey_principles_vegetable_gardening_1912", "The Principles of Vegetable-Gardening (L. H. Bailey, "
         "1912 printing)", "Vegetable gardening (old book)", "L. H. Bailey (Macmillan)", "principlesofveg00bail",
         1912,
         "Liberty Hyde Bailey's textbook of the vegetable garden: soil and its preparation, manures, seeds and "
         "sowing, transplanting, tilling and watering, and each vegetable.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "bailey_farm_garden_rule_book_1911", "Farm and Garden Rule-Book (L. H. Bailey, 1911)",
         "Garden reference (old book)", "L. H. Bailey (Macmillan)", "farmgardenrulebo00bailrich", 1911,
         "A manual of ready rules and reference for the garden and farm: planting tables, seeds per row, soils "
         "and fertilizers, weights and measures, and recipes.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "jekyll_colour_in_flower_garden_1908", "Colour in the Flower Garden (Gertrude Jekyll, 1908)",
         "Flower gardening (old book)", "Gertrude Jekyll (Country Life, London)", "colourinflowerga00jeky", 1908,
         "Gertrude Jekyll's planting plans for borders and gardens by colour and season.", GARDEN_NOTE, GA.SAFETY,
         country="United Kingdom"),
    _old(GARDEN, "jekyll_home_and_garden_1900", "Home and Garden (Gertrude Jekyll, 1900)",
         "Gardening (old book)", "Gertrude Jekyll (Longmans, Green)", "homegardennotest00jeky", 1900,
         "Notes and thoughts, practical and critical, of a worker in both house and garden.", GARDEN_NOTE,
         GA.SAFETY, country="United Kingdom"),
    _old(GARDEN, "jekyll_children_and_gardens_1908", "Children and Gardens (Gertrude Jekyll, 1908)",
         "Gardening with children (old book)", "Gertrude Jekyll (Country Life, London)", "childrengardens00jeky", 1908,
         "Gardens for children: their own plots, easy flowers and vegetables, and garden play.", GARDEN_NOTE,
         GA.SAFETY, country="United Kingdom"),
    _old(GARDEN, "henderson_gardening_for_pleasure_1888", "Gardening for Pleasure (Peter Henderson, 1888 edition)",
         "Home gardening (old book)", "Peter Henderson (Orange Judd)", "gardeningforplea00hend", 1888,
         "A guide for the amateur in the fruit, vegetable and flower garden, with directions for the greenhouse, "
         "conservatory and window garden.",
         GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "fernow_care_of_trees_1910", "The Care of Trees in Lawn, Street and Park (B. E. Fernow, 1910)",
         "Trees (old book)", "B. E. Fernow (Henry Holt)", "careoftreesinlaw00fernuoft", 1910,
         "Planting and caring for trees around homes and in towns, with a list of trees and shrubs for "
         "planting.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "cunningham_lawns_golf_courses_1914", "Lawns, Golf Courses, Polo Fields and How to Treat Them "
         "(S. A. Cunningham, 1914)", "Lawns (old book)", "S. A. Cunningham", "lawnsgolfcourses00cunn", 1914,
         "Making and keeping turf: soil, grass seed, sowing, mowing, rolling, watering and feeding.", GARDEN_NOTE,
         GA.SAFETY),
    _old(GARDEN, "barron_lawns_how_to_make_them_1914", "Lawns and How to Make Them (Leonard Barron, 1914 printing)",
         "Lawns (old book)", "Leonard Barron (Doubleday, Page)", "cu31924089539070", 1914,
         "Making a new lawn and keeping it: soil, seed mixtures, sowing and sodding, mowing, weeds, and putting "
         "greens.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "barron_keeping_the_lawn_1921", "Keeping the Lawn (Leonard Barron, 1921)", "Lawns (old book)",
         "Leonard Barron (Coldwell Lawn Mower Company)", "keepinglawn00barr", 1921,
         "A short guide to mowing, rolling, watering and feeding a lawn, written for a lawn mower maker.",
         GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "barron_roses_how_to_grow_them_1905", "Roses and How to Grow Them (Leonard Barron, 1905)",
         "Roses (old book)", "Leonard Barron (Doubleday, Page)", "roseshowtogrowth00barr", 1905,
         "Growing roses in the garden and under glass: kinds, planting, pruning, feeding and protection.",
         GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "miller_how_to_make_flower_garden_1903", "How to Make a Flower Garden (Wilhelm Miller, ed., 1903)",
         "Flower gardening (old book)", "Wilhelm Miller (Doubleday, Page)", "howtomakeflowerg00mill", 1903,
         "Practical chapters by many gardeners on planning and planting flower gardens, borders, bulbs, roses "
         "and annuals.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "findlay_practical_gardening_1918", "Practical Gardening: Vegetables and Fruits (Hugh Findlay, 1918)",
         "Vegetable gardening (old book)", "Hugh Findlay (D. Appleton)", "cu31924002853327", 1918,
         "Helpful hints for the home vegetable and fruit garden, with the common mistakes to avoid.", GARDEN_NOTE,
         GA.SAFETY),
    _old(GARDEN, "duncan_when_mother_lets_us_garden_1909", "When Mother Lets Us Garden (Frances Duncan, 1909)",
         "Gardening with children (old book)", "Frances Duncan (Moffat, Yard)", "whenmotherletsus00duncrich", 1909,
         "A gardening book for children: making a small garden, easy flowers and vegetables, and caring for "
         "them.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "rexford_home_floriculture_1903", "Home Floriculture (Eben E. Rexford, 1903)",
         "Flowers and house plants (old book)", "Eben E. Rexford (Orange Judd)", "homefloriculture00rexfrich", 1903,
         "Growing flowering and ornamental plants in the house and garden: soil, potting, watering, light, "
         "bulbs, shrubs and plant troubles.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "rexford_abc_vegetable_gardening_1916", "A-B-C of Vegetable Gardening (Eben E. Rexford, 1916)",
         "Vegetable gardening (old book)", "Eben E. Rexford (Harper)", "abcofvegetablega00rexf", 1916,
         "A beginner's book of the vegetable garden: the soil, planting, cultivating and each common vegetable.",
         GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "barnes_house_plants_1914", "House Plants and How to Grow Them (Parker T. Barnes, 1914 printing)",
         "House plants (old book)", "Parker Thayer Barnes (Doubleday, Page)", "houseplantshowto00barn", 1914,
         "Growing plants indoors: choosing plants, pots and soil, light, watering, feeding, propagation and "
         "plant troubles.", GARDEN_NOTE, GA.SAFETY),
    _old(GARDEN, "sanderson_insect_pests_farm_garden_1921", "Insect Pests of Farm, Garden and Orchard (E. Dwight "
         "Sanderson and Leonard M. Peairs, 1921)", "Garden pests (old book)", "E. Dwight Sanderson (John Wiley)",
         "insectpestsoffar00sandrich", 1921,
         "Identifying the insect pests of field crops, vegetables, fruit trees and stored grain, and their life "
         "histories.", GARDEN_NOTE + " Its sprays in particular are dangerous: never use arsenic or lead "
         "compounds.", GA.SAFETY),
]

# ====================================================================== outdoor recreation

OUT = OD.GROUP
OUTDOORS = [
    _yearbook(OUT, "usda_yearbook_1967_outdoors_usa", "Outdoors USA: The Yearbook of Agriculture 1967",
              "Outdoor recreation", "yoa1967", 1967,
              "The USDA's yearbook on outdoor recreation: the national forests and grasslands, camping, hiking, "
              "fishing, hunting, water sports, winter sports, nature study and recreation on farms.",
              " Places, fees and rules have changed since 1967. " + OD.SAFETY),
    _old(OUT, "waugh_recreation_uses_national_forests_1918", "Recreation Uses on the National Forests (Frank A. "
         "Waugh, US Forest Service, 1918)", "National forests", "US Forest Service (Government Printing Office)",
         "recreationuseson00waugrich", 1918,
         "The Forest Service's first study of recreation in the national forests: camping, hiking, summer homes, "
         "hunting, fishing and the planning of recreation areas.", GOV_OUT_NOTE, OD.SAFETY),
    _old(OUT, "usfs_outdoor_recreation_national_forests_1925", "Outdoor Recreation on the National Forests (US Forest "
         "Service, 1925)", "National forests", "US Forest Service", "CAT10680401", 1925,
         "A Forest Service booklet on the national forests as places for camping, hiking, fishing and hunting, "
         "and how to use them.", GOV_OUT_NOTE, OD.SAFETY),
    _old(OUT, "usfs_sunshine_recreation_ground_1922", "The Sunshine Recreation Ground of a Nation (US Forest "
         "Service, 1922)", "National forests", "US Forest Service", "sunshinerecreati00unit", 1922,
         "The Forest Service's guide to the national forests of Arizona and New Mexico for visitors.",
         GOV_OUT_NOTE, OD.SAFETY),
    _old(OUT, "nps_glimpses_national_parks_1920", "Glimpses of Our National Parks (National Park Service, 1920)",
         "National parks", "National Park Service (Government Printing Office)", "glimpsesofournat01unit", 1920,
         "The Park Service's short descriptions of each national park of 1920: what there is to see and do.",
         GOV_OUT_NOTE, OD.SAFETY),
    _old(OUT, "nps_glimpses_national_parks_1930", "Glimpses of Our National Parks (Robert Sterling Yard, National "
         "Park Service, 1930)", "National parks", "National Park Service (Government Printing Office)",
         "glimpsesofournat1930yard", 1930,
         "The 1930 edition of the Park Service's descriptions of the national parks.", GOV_OUT_NOTE, OD.SAFETY),
    _old(OUT, "nps_national_parks_portfolio_1921", "The National Parks Portfolio (National Park Service, 1921)",
         "National parks", "National Park Service (Government Printing Office)", "parksnationalpor00unitrich", 1921,
         "The Park Service's illustrated book of the national parks, park by park (the photographs are described "
         "only by their captions).", GOV_OUT_NOTE, OD.SAFETY),
    _old(OUT, "nps_wild_animals_glacier_1918", "Wild Animals of Glacier National Park (National Park Service, 1918)",
         "Wildlife in parks", "National Park Service (Government Printing Office)", "wildanimalsofgla00unit", 1918,
         "The mammals of Glacier National Park described by Vernon Bailey, with the birds by Florence Merriam "
         "Bailey, and notes on the park's land and life zones.", GOV_OUT_NOTE + " Never feed or approach wild "
         "animals.", OD.SAFETY),
    _old(OUT, "beard_american_boys_camp_lore_1920", "The American Boys' Handybook of Camp-Lore and Woodcraft (Daniel "
         "Carter Beard, 1920)", "Camping and woodcraft (old book)", "Daniel Carter Beard (J. B. Lippincott)",
         "americanboyshand00bear", 1920,
         "Beard's book of camp skills: packs and outfits, tents and camps, fires and camp cooking, trails and "
         "signs, and woodcraft.", OUT_NOTE, OD.SAFETY),
    _old(OUT, "verrill_book_of_camping_1917", "The Book of Camping (A. Hyatt Verrill, 1917)",
         "Camping (old book)", "A. Hyatt Verrill (A. A. Knopf)", "bookofcamping00verrrich", 1917,
         "Choosing a camp site, tents, beds, outfits, cooking, canoe and pack trips, and camping in each season.",
         OUT_NOTE, OD.SAFETY),
    _old(OUT, "cruikshank_canoeing_and_camping_1915", "Canoeing and Camping (James A. Cruikshank, 1915)",
         "Canoeing (old book)", "James A. Cruikshank (American Sports Publishing)", "canoeingcamping00crui", 1915,
         "A small handbook of canoeing (choosing a canoe, paddling, carrying and safety) and canoe camping.",
         OUT_NOTE + " Always wear a life jacket in a canoe.", OD.SAFETY),
    _old(OUT, "bryan_campers_own_book_1912", "The Camper's Own Book (George S. Bryan, ed., 1912)",
         "Camping (old book)", "George S. Bryan (Log Cabin Press)", "campersownbookha00brya", 1912,
         "A handy volume for campers: outfits, tents, camp cooking, canoeing, woodcraft and camp health.",
         OUT_NOTE, OD.SAFETY),
    _old(OUT, "cave_boy_scouts_hike_book_1913", "The Boy Scout's Hike Book (Edward Cave, 1913)", "Hiking (old book)",
         "Edward Cave (Doubleday, Page)", "boyscoutshikeboo00caverich", 1913,
         "Planning and going on hikes: what to carry, walking, camping on the way, cooking, and finding the way.",
         OUT_NOTE, OD.SAFETY),
    _old(OUT, "beard_on_the_trail_girls_1915", "On the Trail: An Outdoor Book for Girls (Lina and Adelia B. Beard, "
         "1915)", "Hiking and camping (old book)", "Lina Beard and Adelia B. Beard (Charles Scribner's Sons)",
         "ontrailoutdoorbo00bear", 1915,
         "Hiking and camping for girls: outfits, packs, trail skills, camp fires and cooking, and nature study.",
         OUT_NOTE, OD.SAFETY),
    _old(OUT, "wright_birdcraft_1897", "Birdcraft: A Field Book of Two Hundred Song, Game and Water Birds (Mabel "
         "Osgood Wright, 1897)", "Birds (old book)", "Mabel Osgood Wright (Macmillan)", "birdcraftfield00wrig", 1897,
         "An early field book of the birds of the eastern United States, with keys by colour and season.",
         BIRD_NOTE, OD.SAFETY),
    _old(OUT, "bailey_birds_village_field_1898", "Birds of Village and Field: A Bird Book for Beginners (Florence "
         "Merriam Bailey, 1898)", "Birds (old book)", "Florence Merriam (Houghton Mifflin)", "birdsofvillagefi00bail",
         1898,
         "A beginner's bird book of the common birds of towns and fields, with field keys and descriptions.",
         BIRD_NOTE, OD.SAFETY),
    _old(OUT, "bailey_birds_through_opera_glass_1899", "Birds Through an Opera-Glass (Florence Merriam Bailey, 1899 "
         "printing)", "Birds (old book)", "Florence Merriam (Chautauqua Press)", "birdsthroughoper00bailrich", 1899,
         "Watching and knowing seventy common birds with field glasses, by one of the first women bird writers.",
         BIRD_NOTE, OD.SAFETY),
    _old(OUT, "bailey_handbook_birds_western_us_1902", "Handbook of Birds of the Western United States (Florence "
         "Merriam Bailey, 1902)", "Birds (old book)", "Florence Merriam Bailey (Houghton Mifflin)",
         "handbookbirdswe01bailgoog", 1902,
         "The western companion to Chapman's eastern handbook: keys and descriptions of the birds of the Great "
         "Plains, Great Basin, Pacific slope and lower Rio Grande valley.", BIRD_NOTE, OD.SAFETY),
    _old(OUT, "chapman_color_key_north_american_birds_1912", "Color Key to North American Birds (Frank M. Chapman, "
         "1912)", "Birds (old book)", "Frank M. Chapman (D. Appleton)", "colorkeytonort00chap", 1912,
         "Identifying North American birds by their colours, with a short description of every species.",
         BIRD_NOTE, OD.SAFETY),
    _old(OUT, "chapman_bird_life_1899", "Bird-Life: A Guide to the Study of Our Common Birds (Frank M. Chapman, "
         "1899)", "Birds (old book)", "Frank M. Chapman (D. Appleton)", "birdlifeguidet00chap", 1899,
         "How birds live (migration, songs, nests, food) and a guide to the common birds of the eastern United "
         "States.", BIRD_NOTE, OD.SAFETY),
    _old(OUT, "henshall_book_of_black_bass_1881", "Book of the Black Bass (James A. Henshall, 1881)",
         "Fishing (old book)", "James A. Henshall (Robert Clarke)", "bookofblackbassc00hens", 1881,
         "The black bass's life history and how to fish for it: tackle, rods, lines, flies and baits, and "
         "angling methods.", FISH_NOTE, OD.SAFETY),
    _old(OUT, "halford_dry_fly_mans_handbook_1913", "The Dry-Fly Man's Handbook (Frederic M. Halford, 1913)",
         "Fly fishing (old book)", "Frederic M. Halford (George Routledge)", "cu31924003437765", 1913,
         "A complete manual of dry-fly fishing, with the fisherman's entomology and the dressing of flies.",
         FISH_NOTE, OD.SAFETY, country="United Kingdom"),
    _old(OUT, "francis_book_on_angling_1920", "A Book on Angling (Francis Francis, 1920 printing)",
         "Fishing (old book)", "Francis Francis (Herbert Jenkins, London)", "bookonanglingbei00franiala", 1920,
         "A complete treatise on angling in every branch: coarse fishing, trout and salmon fishing, tackle and "
         "flies.", FISH_NOTE, OD.SAFETY, country="United Kingdom"),
]

# ====================================================================== science you can use

SCI = "scienceuse"            # science_use.GROUP (not imported: science_use's import list is long)
SCIENCE = [
    _old(SCI, "faraday_chemical_history_candle_1908", "The Chemical History of a Candle (Michael Faraday, 1908 "
         "printing)", "Chemistry (old book)", "Michael Faraday (Harper)", "chemicalhistoryo00faraiala", 1908,
         "Faraday's famous Christmas lectures for young people: what a burning candle shows about flame, air, "
         "water, carbon and breathing.", SCI_NOTE),
    _old(SCI, "faraday_forces_of_matter_1860", "A Course of Six Lectures on the Various Forces of Matter (Michael "
         "Faraday, 1860)", "Physics (old book)", "Michael Faraday (Harper)", "courseofsixlectu00fararich", 1860,
         "Faraday's lectures for young people on gravitation, cohesion, chemical affinity, heat, magnetism and "
         "electricity.", SCI_NOTE),
    _old(SCI, "tyndall_fragments_of_science_1871", "Fragments of Science for Unscientific People (John Tyndall, 1871)",
         "Popular science (old book)", "John Tyndall (D. Appleton)", "fragmentsscience00tyndrich", 1871,
         "Essays and lectures for general readers on light, heat, sound, radiation, dust and disease, and "
         "scientific method.", SCI_NOTE),
    _old(SCI, "tyndall_heat_mode_of_motion_1869", "Heat Considered as a Mode of Motion (John Tyndall, 1869)",
         "Physics (old book)", "John Tyndall (D. Appleton)", "heatconsideredas00tyndrich", 1869,
         "Lectures on heat with demonstrations: temperature, expansion, specific heat, melting and boiling, "
         "conduction and radiant heat.", SCI_NOTE),
    _old(SCI, "huxley_physiography_1905", "Physiography: An Introduction to the Study of Nature (Thomas Henry Huxley, "
         "1905 printing)", "Earth science (old book)", "Thomas Henry Huxley (Macmillan)", "physiographyintr00huxlrich",
         1905,
         "Huxley's introduction to earth science through the River Thames: springs and rivers, rain and dew, "
         "ice, the sea, earthquakes and volcanoes, rocks and the work of living things.", SCI_NOTE),
    _old(SCI, "geikie_class_book_geology_1921", "Class-Book of Geology (Archibald Geikie, 1921 printing)",
         "Geology (old book)", "Archibald Geikie (Macmillan)", "classbookofgeolo00geikiala", 1921,
         "A school geology textbook: minerals and rocks, the work of weather, rivers, ice and the sea, volcanoes "
         "and earthquakes, fossils and the history of the earth.", SCI_NOTE, country="United Kingdom"),
    _old(SCI, "milham_meteorology_1912", "Meteorology: A Text-Book on the Weather (Willis I. Milham, 1912)",
         "Weather (old book)", "Willis I. Milham (Macmillan)", "meteorologytextb00milhrich", 1912,
         "The weather explained: the atmosphere, temperature, pressure, winds, clouds and rain, storms, weather "
         "maps and forecasting.", SCI_NOTE),
    _old(SCI, "henkel_weather_science_1911", "Weather Science: An Elementary Introduction to Meteorology (F. W. "
         "Henkel, 1911)", "Weather (old book)", "F. W. Henkel (T. Fisher Unwin)", "weatherscienceel00henkrich", 1911,
         "A short introduction to the weather for general readers: air, heat, moisture, clouds, winds, storms and "
         "weather signs.", SCI_NOTE, country="United Kingdom"),
    _old(SCI, "serviss_astronomy_opera_glass_1890", "Astronomy with an Opera-Glass (Garrett P. Serviss, 1890 "
         "printing)", "Stargazing (old book)", "Garrett P. Serviss (D. Appleton)", "astronomywithope00servuoft", 1890,
         "A popular introduction to the starry heavens with opera glasses or binoculars: the constellations "
         "season by season, the Moon and the planets.", SCI_NOTE, SKY_SAFETY),
    _old(SCI, "serviss_curiosities_of_the_sky_1909", "Curiosities of the Sky (Garrett P. Serviss, 1909)",
         "Astronomy (old book)", "Garrett P. Serviss (Harper)", "curiositiesofsky00servrich", 1909,
         "Popular chapters on nebulae, star clusters, variable stars, comets, meteors and the Milky Way.",
         SCI_NOTE, SKY_SAFETY),
    _old(SCI, "olcott_field_book_of_stars_1907", "A Field Book of the Stars (William Tyler Olcott, 1907)",
         "Stargazing (old book)", "William Tyler Olcott (G. P. Putnam's Sons)", "fieldbookofstars00olcorich", 1907,
         "A pocket guide to finding the constellations and bright stars with the naked eye, month by month.",
         SCI_NOTE, SKY_SAFETY),
    _old(SCI, "ball_story_of_the_heavens_1887", "The Story of the Heavens (Robert S. Ball, 1887 printing)",
         "Astronomy (old book)", "Robert S. Ball (Cassell)", "storyofheavens00ballrich", 1887,
         "A classic popular astronomy: the telescope, the Sun, Moon and planets, comets and meteors, the stars "
         "and nebulae.", SCI_NOTE, SKY_SAFETY, country="United Kingdom"),
    _old(SCI, "slosson_creative_chemistry_1919", "Creative Chemistry (Edwin E. Slosson, 1919)",
         "Chemistry (old book)", "Edwin E. Slosson (The Century Company)", "creativechemistr00slosuoft", 1919,
         "Popular chapters on the chemical industries of 1919: nitrogen and fertilizers, dyes, perfumes, "
         "plastics, rubber, sugar, metals and explosives in industry.", SCI_NOTE),
    _old(SCI, "thomson_outline_of_science_vol1_1922", "The Outline of Science, volume 1 (J. Arthur Thomson, ed., "
         "1922)", "Popular science (old book)", "J. Arthur Thomson (G. P. Putnam's Sons)", "outlineofscience00thomuoft",
         1922,
         "The first volume of the famous four-volume popular science: the romance of the heavens, the story of "
         "evolution, adaptations, the dawn of mind and the ascent of man.", SCI_NOTE, SKY_SAFETY,
         country="United Kingdom"),
    _old(SCI, "thomson_outline_of_science_vol2_1922", "The Outline of Science, volume 2 (J. Arthur Thomson, ed., "
         "1922)", "Popular science (old book)", "J. Arthur Thomson (G. P. Putnam's Sons)", "outlineofscience02thomuoft",
         1922,
         "The second volume of the four, continuing the popular chapters on the sciences by many writers.",
         SCI_NOTE, country="United Kingdom"),
    _old(SCI, "thomson_outline_of_science_vol3_1922", "The Outline of Science, volume 3 (J. Arthur Thomson, ed., "
         "1922)", "Popular science (old book)", "J. Arthur Thomson (G. P. Putnam's Sons)", "outlineofscience03thomuoft",
         1922,
         "The third volume of the four, continuing the popular chapters on the sciences by many writers.",
         SCI_NOTE, country="United Kingdom"),
    _old(SCI, "comstock_handbook_nature_study_1911", "Handbook of Nature-Study for Teachers and Parents (Anna "
         "Botsford Comstock, 1911)", "Nature study (old book)", "Anna Botsford Comstock (Comstock Publishing)",
         "handbookofnature00coms", 1911,
         "The famous Cornell nature-study handbook: lessons on birds, fish, insects, mammals, wild flowers, "
         "trees, rocks, weather and the sky, for teaching outdoors.", SCI_NOTE, SKY_SAFETY),
    _old(SCI, "lynde_physics_of_household_1914", "Physics of the Household (Carleton John Lynde, 1914)",
         "Everyday physics (old book)", "Carleton John Lynde (Macmillan)", "physicshousehold00lyndrich", 1914,
         "Physics through the home: heating and plumbing, pumps and water pressure, the kitchen range, electric "
         "lights and bells, sound and the telephone, lenses and the camera.",
         SCI_NOTE + " Its electrical wiring and gas advice is out of date: leave them to a qualified electrician "
         "or gas fitter."),
    _old(SCI, "yule_theory_of_statistics_1922", "An Introduction to the Theory of Statistics (G. Udny Yule, 1922 "
         "edition)", "Statistics (old book)", "G. Udny Yule (Charles Griffin, London)", "cu31924013993187", 1922,
         "Yule's classic introduction to statistics: frequency tables, averages, dispersion, correlation and "
         "regression, sampling and probable errors.",
         "Published in {year}: an old statistics textbook. Its methods are still the foundation, but its "
         "notation, computing by hand and some terms are old; the machine-read text of its tables and formulas has "
         "the scanner's mistakes.", country="United Kingdom"),
    _yearbook(SCI, "usda_yearbook_1941_climate_and_man", "Climate and Man: The Yearbook of Agriculture 1941",
              "Weather and climate", "yoa1941", 1941,
              "The USDA's yearbook on climate: how climate shapes farming and life, the science of the "
              "atmosphere, weather forecasting, and the climate of every state, with its weather records.",
              " Its climate tables end in the 1930s; today's climate records are at NOAA."),
    _yearbook(SCI, "usda_yearbook_1968_science_for_better_living", "Science for Better Living: The Yearbook of "
              "Agriculture 1968", "Everyday science", "yoa1968", 1968,
              "The USDA's yearbook on agricultural science in daily life: food and nutrition, clothing and "
              "textiles, housing, health, the environment and the countryside."),
    _gov(SCI, "nasa_exploring_the_moon_1994", "Exploring the Moon: A Teacher's Guide with Activities (NASA, 1994)",
         "The Moon", "National Aeronautics and Space Administration (NASA)", "ERIC_ED390711", 1994,
         "NASA's guide to the Moon for teachers: its surface, rocks and history from the Apollo missions, with "
         "classroom activities.", NASA_NOTICE + " " + SKY_SAFETY),
    _gov(SCI, "nasa_space_based_astronomy_1994", "Space-Based Astronomy: A Teacher's Guide with Activities (NASA, "
         "1994)", "Astronomy", "National Aeronautics and Space Administration (NASA)", "ERIC_ED384510", 1994,
         "NASA's guide to astronomy from space: light and the electromagnetic spectrum, telescopes, and why "
         "observatories are put in orbit, with activities.", NASA_NOTICE + " " + SKY_SAFETY),
    _gov(SCI, "nasa_looking_at_earth_from_space_1995", "Looking at Earth from Space: Teacher's Guide with Activities "
         "(NASA, 1995)", "Earth science", "National Aeronautics and Space Administration (NASA)", "ERIC_ED392630",
         1995,
         "NASA's guide to studying the Earth from satellites: weather, oceans, land, ice and remote sensing, with "
         "activities.", NASA_NOTICE),
    _gov(SCI, "nasa_microgravity_1995", "Microgravity: Teacher's Guide with Activities for Physical Science (NASA, "
         "1995)", "Physics", "National Aeronautics and Space Administration (NASA)", "ERIC_ED406237", 1995,
         "NASA's guide to microgravity (weightlessness): gravity, free fall, orbits and experiments in space, "
         "with activities.", NASA_NOTICE),
    _gov(SCI, "nasa_space_food_nutrition_1999", "Space Food and Nutrition: An Educator's Guide with Activities (NASA, "
         "1999)", "Food science", "National Aeronautics and Space Administration (NASA)", "ERIC_ED448036", 1999,
         "NASA's guide to food in space: nutrition, how astronaut food is prepared, packaged and kept, with "
         "activities.", NASA_NOTICE),
    _gov(SCI, "nasa_plants_in_space_1997", "Teachers and Students Investigating Plants in Space (NASA, 1997)",
         "Biology", "National Aeronautics and Space Administration (NASA)", "ERIC_ED406233", 1997,
         "NASA's guide to plant biology in space: how plants sense gravity and light, with growing experiments.",
         NASA_NOTICE),
    _gov(SCI, "nasa_mars_exploration_water_2000", "Mars Exploration: Is There Water on Mars? An Educator's Guide "
         "(NASA, 2000)", "Planets", "National Aeronautics and Space Administration (NASA)", "ERIC_ED481371", 2000,
         "NASA's guide to Mars and the search for its water, with physical and earth science activities.",
         NASA_NOTICE),
]

# ====================================================================== computer and phone basics, and typing

GNOME = "https://help.gnome.org/gnome-help/"
GNOME_HELP = dict(
    K.WEB, name="gnome_desktop_help", title="GNOME desktop help (Linux)", group=CB.GROUP, country="International",
    subject="Linux desktop (GNOME)", publisher="The GNOME Project (GNOME Help, written by Shaun McCance and others)",
    licence="CC BY-SA 3.0", licence_url="https://creativecommons.org/licenses/by-sa/3.0/", source=GNOME + "index.html",
    licence_page=GNOME + "index.html", licence_text=r"Creative Commons Attribution-ShareAlike 3\.0 Unported License",
    description="The GNOME desktop's own help, every page except its accessibility section (which is "
                "a11yc:gnome_help_accessibility): the desktop and its activities overview, starting and switching "
                "programs, windows and workspaces, files and folders, the internet, Wi-Fi and networking, sound, "
                "video and pictures, printing, hardware and disks, user accounts and passwords, settings, keyboard "
                "shortcuts and tips. GNOME is the desktop of Ubuntu, Fedora and many other Linux systems.",
    notice="From GNOME Help (the GNOME Project), licensed under a Creative Commons Attribution-ShareAlike 3.0 "
           "Unported License (https://creativecommons.org/licenses/by-sa/3.0/); converted to an accessible format, "
           "and this copy is shared under the same licence. Linux systems differ: check your system's own help. "
           + CB.TECH_SAFETY,
    content=(r"<article\b[^>]*>", r"</article>"), title_from=r'<h1 class="title">(.*?)</h1>',
    crawl=[(GNOME + "index.html", 3)], follow=r"^https://help\.gnome\.org/gnome-help/(?!a11y)[a-z0-9-]+\.html$",
    pages=r"^https://help\.gnome\.org/gnome-help/(?!a11y)[a-z0-9-]+\.html$",
    unit_rules=[(r"/(files|nautilus)", "Files"), (r"/(net|wireless)", "Internet and networking"),
                (r"/(sound|media|video|music|photo)", "Sound and media"),
                (r"/(printing|hardware|disk|power|bluetooth|mouse|keyboard|display)", "Hardware"),
                (r"/(user|prefs|privacy|session)", "Settings and accounts"), (r".", "The desktop")],
    version="help.gnome.org/gnome-help as published", limit=400)

COMPUTER = [
    CB.lo_guide("IG", "libreoffice_impress_guide", "LibreOffice Impress Guide (version 26.2)",
                "Presentations (LibreOffice Impress)",
                "The full guide to Impress, LibreOffice's presentation program, every chapter: introducing Impress, "
                "slide masters and templates, adding and formatting text and images, graphic objects, "
                "spreadsheets, charts and other objects, slides, notes and handouts, slide shows, printing and "
                "exporting, setting up Impress, the keyboard shortcuts and the toolbars."),
    CB.lo_guide("DG", "libreoffice_draw_guide", "LibreOffice Draw Guide (version 26.2)",
                "Drawing and diagrams (LibreOffice Draw)",
                "The full guide to Draw, LibreOffice's drawing program, every chapter: introducing Draw, basic "
                "shapes, working with and changing objects, combining objects, editing images, connectors, "
                "flowcharts and organisation charts, text, printing and exporting, advanced techniques, the "
                "keyboard shortcuts and the toolbars."),
    GNOME_HELP,
]
TYPE = TY.GROUP
TYPING = [
    _old(TYPE, "sorelle_rational_typewriting_1916", "Rational Typewriting, revised edition (Rupert P. SoRelle and "
         "Ida McLenan Cutler, 1916)", "Touch typing", "Rupert P. SoRelle and Ida McLenan Cutler (Gregg Publishing)",
         "RationalTypewriting-RevisedEdition", 1916,
         "The Gregg company's touch typing course: the keyboard by rows, graded drills, letters and business forms.",
         TY.OLD_NOTE),
    _old(TYPE, "van_sant_touch_typewriting_1902", "The Van Sant System of Touch Typewriting (A. C. Van Sant, 1902)",
         "Touch typing", "A. C. Van Sant", "TheVanSantSystemOfTouchTypewriting-ForSmithPremier", 1902,
         "One of the first touch typing systems, written for the Smith Premier typewriter: keeping the eyes on the "
         "copy, the finger for each key and graded lessons.", TY.OLD_NOTE),
    _old(TYPE, "barnes_how_to_become_expert_typewriting_1890", "How to Become Expert in Typewriting (Mrs. Arthur J. "
         "Barnes, 1890)", "Typing", "Mrs. Arthur J. Barnes", "howtobecomeexpe00barngoog", 1890,
         "A complete instructor for the Remington typewriter: the keyboard, fingering, exercises and business "
         "letters.", TY.OLD_NOTE),
    _old(TYPE, "parkyn_commercial_handbook_typewriting_1894", "Parkyn's Commercial Handbook of Typewriting (Walter A. "
         "Parkyn, 1894)", "Typing", "Walter A. Parkyn (Isaac Pitman, London)", "parkynscommercia00park", 1894,
         "A handbook for office typists: the machine, fingering, exercises, letters, invoices and legal forms.",
         TY.OLD_NOTE, country="United Kingdom"),
    _old(TYPE, "haven_complete_manual_type_writing_1884", "Haven's Complete Manual of Type Writing (Curtis Haven, "
         "1884)", "Typing", "Curtis Haven", "HavensCompleteManualOfTypeWriting", 1884,
         "An early typewriting manual: the machine, fingering, exercises and the forms of business work.",
         TY.OLD_NOTE),
    _old(TYPE, "humphrey_manual_type_writing_1887", "Humphrey's Manual of Type-Writing (Frank S. Humphrey, 1887)",
         "Typing", "Frank S. Humphrey (Poughkeepsie)", "humphreysmanualo00hump", 1887,
         "A typewriting manual with a business letter-writer and exercises for shorthand writers.", TY.OLD_NOTE),
    _old(TYPE, "new_practical_typewriting_1923", "New Practical Typewriting (1923)", "Touch typing",
         "The Practical Text Book Company (Cleveland)", "newpracticaltype00unse", 1923,
         "A school touch typing course: the home keys, graded keyboard lessons, speed and accuracy drills, letters "
         "and tables.", TY.OLD_NOTE),
    _old(TYPE, "hoke_speed_accuracy_typewriting_1922", "The Improvement of Speed and Accuracy in Typewriting (Roy E. "
         "Hoke, 1922)", "Typing speed", "Roy E. Hoke (Johns Hopkins Press)", "improvementofspe00hoke", 1922,
         "A study of how typists gain speed and accuracy: practice, rhythm, errors and keyboard arrangement.",
         TY.OLD_NOTE),
    _old(TYPE, "clough_typewriting_catechism_1930", "A Typewriting Catechism, fifth edition (Edith R. Clough, 1930)",
         "Typing", "Edith R. Clough", "in.ernet.dli.2015.116964", 1930,
         "Questions and answers on typewriting: the machine, fingering, display, letters and office practice.",
         TY.OLD_NOTE, country="United Kingdom"),
    _old(TYPE, "history_of_touch_typewriting_1900", "The History of Touch Typewriting (Wyckoff, Seamans and Benedict, "
         "1900)", "Typing history", "Wyckoff, Seamans and Benedict", "TheHistoryOfTouchTypewriting1900", 1900,
         "A short history of touch typing (typing without looking at the keys) by the makers of the Remington "
         "typewriter.", TY.OLD_NOTE),
]

# ====================================================================== audio and media production

MEDIA_GROUP = "audiomedia"     # audio_media.GROUP
MEDIA = [
    _old(MEDIA_GROUP, "national_phonograph_how_to_use_1900", "The Phonograph and How to Use It (National Phonograph "
         "Company, 1900)", "Sound recording history", "National Phonograph Company (Thomas A. Edison)",
         "phonographhowtou00nati", 1900,
         "Edison's company's handbook: a short history of the phonograph, how it works, and how to make and play "
         "cylinder records.", MEDIA_NOTE),
    _old(MEDIA_GROUP, "macfarlane_phonograph_book_1917", "The Phonograph Book (Lloyd Macfarlane, 1917)",
         "Sound recording history", "Lloyd Macfarlane", "the-phonograph-book-macfarlane", 1917,
         "A book about getting the best from a phonograph: the machine, records, needles and listening.",
         MEDIA_NOTE),
    _old(MEDIA_GROUP, "du_moncel_telephone_microphone_phonograph_1879", "The Telephone, the Microphone and the "
         "Phonograph (Count Th. du Moncel, 1879)", "Sound recording history", "Th. du Moncel (Harper)",
         "telephonemicroph00dumorich", 1879,
         "How the first telephones, microphones and the phonograph worked, written just after their invention.",
         MEDIA_NOTE),
    _old(MEDIA_GROUP, "seymour_reproduction_of_sound_1918", "The Reproduction of Sound (Henry Seymour, 1918)",
         "Sound recording history", "Henry Seymour (W. B. Tattersall, London)", "TheReproductionOfSound_HSeymour",
         1918,
         "The mechanical appliances and methods of acoustic sound recording and reproduction of the phonograph "
         "and gramophone era.", MEDIA_NOTE, country="United Kingdom"),
    _old(MEDIA_GROUP, "lescarboura_radio_for_everybody_1922", "Radio for Everybody (Austin C. Lescarboura, 1922)",
         "Radio history", "Austin C. Lescarboura (Scientific American Publishing)", "radioforeverybod00lescrich", 1922,
         "A popular guide to radio-telephone reception and broadcasting in its first boom year: stations, "
         "programmes, receiving sets and aerials.", MEDIA_NOTE),
    _old(MEDIA_GROUP, "rca_radio_enters_the_home_1922", "Radio Enters the Home (Radio Corporation of America, 1922)",
         "Radio history", "Radio Corporation of America", "RadioEntersTheHome", 1922,
         "RCA's guide to enjoying the new radio broadcasting at home, with its receiving sets (a maker's "
         "catalogue as well as a guide).", MEDIA_NOTE),
    _old(MEDIA_GROUP, "wwj_detroit_news_broadcasting_1922", "WWJ, The Detroit News: The History of Radiophone "
         "Broadcasting (1922)", "Radio history", "The Evening News Association (Detroit)", "thedetroitnews00detriala",
         1922,
         "The story of one of the first broadcasting stations, told by its newspaper owner: its start in 1920, "
         "its programmes and its studio.", MEDIA_NOTE),
    _old(MEDIA_GROUP, "bennett_handbook_kinematography_1911", "The Handbook of Kinematography (Colin N. Bennett, "
         "1911)", "Film history", "Colin N. Bennett (Kinematograph Weekly, London)", "handbookofkinema00bennuoft",
         1911,
         "The history, theory and practice of motion photography and projection in the silent film era.",
         MEDIA_NOTE, country="United Kingdom"),
    _old(MEDIA_GROUP, "lescarboura_cinema_handbook_1921", "The Cinema Handbook (Austin C. Lescarboura, 1921)",
         "Film history", "Austin C. Lescarboura (Scientific American Publishing)", "cinemahandbookgu00lescrich", 1921,
         "A guide to practical motion picture work outside the theatres: cameras, filming, developing, editing "
         "titles and projecting.", MEDIA_NOTE),
    _old(MEDIA_GROUP, "lescarboura_behind_motion_picture_screen_1921", "Behind the Motion-Picture Screen (Austin C. "
         "Lescarboura, 1921)", "Film history", "Austin C. Lescarboura (Scientific American Publishing)",
         "behindmotionpict00lescrich", 1921,
         "How silent films were made: the scenario writer, director, cameraman, scene painter, actors, "
         "laboratory and projectionist.", MEDIA_NOTE),
    _old(MEDIA_GROUP, "gregory_motion_picture_photography_1927", "Motion Picture Photography (Carl Louis Gregory, ed., "
         "1927)", "Film history", "Carl Louis Gregory (Falk Publishing)", "motionpicturepho00carl", 1927,
         "The New York Institute of Photography's textbook of motion picture camera work: cameras, lenses, "
         "lighting, film, exposure and laboratory work.", MEDIA_NOTE),
]

# ====================================================================== genealogy

GEN = GE.GROUP
GENEALOGY = [
    _old(GEN, "census_century_of_population_growth_1909", "A Century of Population Growth, 1790-1900 (US Census "
         "Bureau, 1909)", "Census history and surnames", "US Bureau of the Census (Government Printing Office)",
         "centuryofpopulat00unit", 1909,
         "The Census Bureau's study of the first census of 1790 and the century after it: the states and counties, "
         "the population, the heads of families, and the surnames of 1790 with how common each was, which "
         "genealogists still use.",
         "Published in {year} by the US government: an old book (and a US government work). Its figures stop at "
         "1900; the machine-read text of its tables has the scanner's mistakes.", GE.NOTE),
    _old(GEN, "rye_records_and_record_searching_1897", "Records and Record Searching: A Guide to the Genealogist "
         "(Walter Rye, 1897 edition)", "Genealogy methods (old book)", "Walter Rye (Elliot Stock, London)",
         "recordsrecordsea00ryew", 1897,
         "A guide to the English records a family historian searches: parish registers, wills, court rolls, "
         "taxes, deeds and the public records.", GEN_NOTE, GE.NOTE, country="United Kingdom"),
    _old(GEN, "martin_record_interpreter_1910", "The Record Interpreter (Charles Trice Martin, 1910 edition)",
         "Reading old records (old book)", "Charles Trice Martin (Stevens and Sons, London)",
         "recordinterprete00martuoft", 1910,
         "A collection of the abbreviations, Latin words and names used in old English records, for reading "
         "them.", GEN_NOTE, GE.NOTE, country="United Kingdom"),
    _old(GEN, "bernau_special_studies_genealogy_1908", "Some Special Studies in Genealogy (Charles A. Bernau, 1908)",
         "Genealogy methods (old book)", "Charles A. Bernau", "somespecialstudi00bern", 1908,
         "Studies of American emigrants and how to trace their English ancestry, and of the records that help.",
         GEN_NOTE, GE.NOTE, country="United Kingdom"),
    _old(GEN, "cox_how_to_write_history_of_parish_1909", "How to Write the History of a Parish (J. Charles Cox, 1909 "
         "edition)", "Local history (old book)", "J. Charles Cox (George Allen, London)", "howtowritehistor00coxj",
         1909,
         "An outline guide to the records, manuscripts and buildings that tell the history of an English parish "
         "and its families.", GEN_NOTE, GE.NOTE, country="United Kingdom"),
    _old(GEN, "durrie_bibliographia_genealogica_americana_1886", "Bibliographia Genealogica Americana (Daniel S. "
         "Durrie, 1886)", "Family histories index (old book)", "Daniel S. Durrie (Joel Munsell's Sons)",
         "bibliographiagen00durruoft", 1886,
         "An alphabetical index by surname to the American family histories and pedigrees printed in books and "
         "journals before 1886.", GEN_NOTE, GE.NOTE),
    _old(GEN, "fox_davies_complete_guide_heraldry_1909", "A Complete Guide to Heraldry (Arthur Charles Fox-Davies, "
         "1909)", "Heraldry (old book)", "Arthur Charles Fox-Davies (T. C. and E. C. Jack)",
         "completeguidetoh00foxdrich", 1909,
         "The classic guide to coats of arms: shields, colours, charges, crests, the language of blazon, and how "
         "arms pass in families.", GEN_NOTE, GE.NOTE, country="United Kingdom"),
]

# ====================================================================== communication and relationships

REL = "relationships"          # relationships.GROUP
RELATIONSHIPS = [
    _old(REL, "post_etiquette_1922", "Etiquette in Society, in Business, in Politics and at Home (Emily Post, 1922)",
         "Etiquette (historical)", "Emily Post (Funk and Wagnalls)", "in.ernet.dli.2015.125556", 1922,
         "Emily Post's first and famous book of manners: introductions, conversation, letters and invitations, "
         "dinners, weddings and funerals, business manners and everyday courtesy.", RELATE_NOTE),
    _old(REL, "esenwein_carnegie_art_of_public_speaking_1915", "The Art of Public Speaking (J. Berg Esenwein and "
         "Dale Carnagey, 1915)", "Public speaking", "J. Berg Esenwein and Dale Carnagey (Dale Carnegie) (Home "
         "Correspondence School)", "artofpublicspeak00esen", 1915,
         "Dale Carnegie's first book, written with J. Berg Esenwein: self-confidence, voice, emphasis, pauses, "
         "gesture, preparing and delivering a speech, and the kinds of speeches.", RELATE_NOTE),
    _old(REL, "winans_public_speaking_1917", "Public Speaking (James A. Winans, 1917)", "Public speaking",
         "James A. Winans (The Century Company)", "publicspeaking000wina", 1917,
         "A college textbook of public speaking: conversation as the model, attention, preparing and organising, "
         "delivery and persuasion.", RELATE_NOTE),
    _old(REL, "robinson_effective_public_speaking_1916", "Effective Public Speaking (Frederick B. Robinson, 1916)",
         "Public speaking", "Frederick B. Robinson (LaSalle Extension University)", "effectivepublics00robirich", 1916,
         "A home-study course in public speaking for business people: voice, preparing, delivering and "
         "debating.", RELATE_NOTE),
    _old(REL, "holyoake_public_speaking_and_debate_1897", "Public Speaking and Debate (George Jacob Holyoake, 1897 "
         "edition)", "Public speaking and debate", "George Jacob Holyoake (Ginn)", "publicspeakingde00holy", 1897,
         "A manual for speakers and debaters: preparing, speaking clearly, meeting objections and the conduct of "
         "debate.", RELATE_NOTE, country="United Kingdom"),
    _old(REL, "mahaffy_art_of_conversation_1888", "The Principles of the Art of Conversation (J. P. Mahaffy, 1888)",
         "Conversation", "J. P. Mahaffy (Macmillan)", "principlesofarto00maharich", 1888,
         "An essay on good conversation: listening, tact, humour, avoiding monologue and drawing others out.",
         RELATE_NOTE, country="United Kingdom"),
    _old(REL, "baker_art_of_conversation_1907", "The Art of Conversation (Josephine Turck Baker, 1907)",
         "Conversation", "Josephine Turck Baker (Correct English Publishing)", "artofconversatio01bake", 1907,
         "Twelve golden rules of conversation, with examples of what to say and what to avoid.", RELATE_NOTE),
    _old(REL, "conklin_conversation_1912", "Conversation: What to Say and How to Say It (Mary Greer Conklin, 1912)",
         "Conversation", "Mary Greer Conklin (Funk and Wagnalls)", "conversationwhat00conkrich", 1912,
         "Advice on talking with others: listening, tact, topics, humour, and conversation at home, at table and "
         "in business.", RELATE_NOTE),
    _old(REL, "krans_lost_art_of_conversation_1910", "The Lost Art of Conversation (Horatio S. Krans, ed., 1910)",
         "Conversation", "Horatio S. Krans (Sturgis and Walton)", "lostartofconvers00kran", 1910,
         "Essays on conversation by writers from Swift to Stevenson, gathered in one book.", RELATE_NOTE),
    _old(REL, "chambers_new_century_letter_writer_1900", "The New Century Standard Letter-Writer (Alfred B. Chambers, "
         "1900)", "Letter writing (historical)", "Alfred B. Chambers (Chicago)", "newcenturystanda00chamrich", 1900,
         "Model letters for business, family and social correspondence, with the forms of address and the rules "
         "of letter writing.", RELATE_NOTE),
    _old(REL, "century_standard_letter_writer_1902", "The Century Standard Business and Social Letter Writer (1902)",
         "Letter writing (historical)", "L. W. Walter Company (Chicago)", "centurystandardb00chic", 1902,
         "Model business and social letters, invitations and replies, with the forms of address.", RELATE_NOTE),
    _old(REL, "johnston_new_business_letter_writer_1920", "The New Business Letter Writer (Bertha Johnston, 1920)",
         "Business letters (historical)", "Bertha Johnston (Sherwood Company)", "newbusinesslette00john", 1920,
         "Model business letters of every kind: orders, enquiries, complaints, collection, applications and "
         "replies.", RELATE_NOTE),
    _old(REL, "cooke_social_etiquette_1896", "Social Etiquette; or, Manners and Customs of Polite Society (Maud C. "
         "Cooke, 1896)", "Etiquette (historical)", "Maud C. Cooke (National Publishing Company)",
         "socialetiquetteo00cook", 1896,
         "A nineteenth-century book of manners: introductions, calls, conversation, dress, letters, dinners, "
         "weddings and travel.", RELATE_NOTE),
    _old(REL, "kingsland_etiquette_all_occasions_1901", "Etiquette for All Occasions (Mrs. Burton Kingsland, 1901)",
         "Etiquette (historical)", "Florence Kingsland (Doubleday, Page)", "etiquetteforallo00kingiala", 1901,
         "Manners of 1901 for every occasion: calls, entertaining, weddings, letters, conversation and public "
         "places.", RELATE_NOTE),
    _old(REL, "sangster_good_manners_all_occasions_1919", "Good Manners for All Occasions (Margaret E. Sangster, "
         "1919 printing)", "Etiquette (historical)", "Margaret E. Sangster (Cupples and Leon)", "cu31924014059103",
         1919,
         "Everyday etiquette: cards and calls, wedding announcements and invitations, dinners, letters and "
         "conversation.", RELATE_NOTE),
]

# ====================================================================== the request words

AREAS = {
    "household": HOUSEHOLD, "instruments": INSTRUMENTS, "garden": GARDENING, "outdoors": OUTDOORS,
    "science": SCIENCE, "computer": COMPUTER + TYPING, "media": MEDIA, "genealogy": GENEALOGY,
    "relationships": RELATIONSHIPS,
}
GUIDES = [e for e in COMPUTER if not e.get("archive")]
PDFS = [e for books in AREAS.values() for e in books if e.get("archive")]


def _keys(entries):
    """The keys of some entries ("olife:<name>")."""
    return [f"{PREFIX}:{e['name']}" for e in entries]


WORDS = {"oldbooks-life": lambda: _keys(e for books in AREAS.values() for e in books)}
WORDS.update({f"oldbooks-life-{area}": (lambda books=books: _keys(books)) for area, books in AREAS.items()})

COLLECTION = K.Collection(PREFIX, HOUSE, guides=GUIDES, pdfs=PDFS, words=WORDS)

LICENCE_LINES = {
    "olife_old_books": "The old books: Internet Archive items whose record's \"date\" is before 1931 (checked at every "
                       "build: old_public_domain); archive.org's robots.txt allows the files; no AI rules (checked "
                       "2026-11-22). Books first published abroad before 1931 are in the US public domain too.",
    "olife_us_government": "The Yearbooks of Agriculture and USDA bulletins (the National Agricultural Library's scans, "
                           "items yoa<year> and CAT..., nfsl_...), the 1976 household pests bulletin and the NASA educator "
                           "guides (ERIC's copies) are works of the US government (17 U.S.C. 105, checked on "
                           "govinfo.gov's policies page at every build). The Forest Service, Park Service and Census "
                           "books of 1909 to 1930 are US government works published before 1931: filed as old books, "
                           "their year checked at every build.",
    "olife_libreoffice": "books.libreoffice.org IG262 and DG262 (each guide's Preface, checked at every build): "
                         "\"distributed and/or modified under the terms of either the GNU General Public License ... or "
                         "the Creative Commons Attribution License ... version 4.0 or later\"; the CC BY 4.0 choice "
                         "is taken. robots.txt allows everything (checked 2026-11-22).",
    "olife_gnome_help": "help.gnome.org/gnome-help/index.html (checked at every build): \"This work is licensed under a "
                        "Creative Commons Attribution-ShareAlike 3.0 Unported License\" (share-alike: a separate "
                        "book); no robots.txt rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("OpenStax and LibreTexts science textbooks (physics, chemistry, biology, astronomy, statistics)", "Every OpenStax "
     "repository on GitHub (56 checked on 2026-11-22) is already in sources.OSBOOKS, pinned to its last CC BY commit "
     "where OpenStax changed licence, and every LibreTexts book with a usable licence is already a course:libretexts "
     "key; OpenStax has no earth science book. Nothing new to add. Index: https://openstax.org/subjects/science"),
    ("NOAA educator guides and Sea Grant curricula", "NOAA's education collections refuse programs (science_use.py), "
     "and the Sea Grant curricula found on ERIC are the universities' own work, not US government works. Index: "
     "https://www.noaa.gov/education/resource-collections"),
    ("LibreOffice Base Guide and Math Guide", "The Base Guide is not on books.libreoffice.org (only as a download "
     "through a file-sharing link), and the Math Guide 26.2's contents page answers \"404\" (checked 2026-11-22). "
     "Index: https://books.libreoffice.org/en/"),
    ("Ubuntu Desktop Guide (help.ubuntu.com, CC BY-SA 3.0)", "help.ubuntu.com answered \"503 Service Unavailable\" to "
     "every request, robots.txt included (2026-11-22); the GNOME desktop help, which Ubuntu's guide is built from, is "
     "built instead (olife:gnome_desktop_help). Index: https://help.ubuntu.com/"),
    ("GCFGlobal, Northstar Digital Literacy, DigitalLearn.org and library digital literacy courses", "Copyright of "
     "each (no open licence found for a whole beginner computer course; Wikibooks' Computers for Beginners is in the "
     "Kiwix library). Link-only. Index: https://edu.gcfglobal.org/en/"),
    ("Audio engineering and recording guides", "No openly licensed whole guide was found beyond the Audacity Manual "
     "(media:audacity_manual) and Wikibooks (in the Kiwix library: Sound Synthesis, Audio Engineering, Acoustics); "
     "the open textbook catalogues are cat:otl and course:libretexts. Index: "
     "https://en.wikibooks.org/wiki/Subject:Audio"),
    ("Old books seen but not built", "Internet Archive items whose only PDF is a picture scan without words (for "
     "example Norton's Construction, Tuning and Care of the Piano-forte, 1887, and White's Regulation and Repair of "
     "Piano and Player Mechanism, 1909, Google scans), items whose record has no date (Smith's Modern Organ Tuning, "
     "Broadhouse's The Organ Viewed from Within, the Bickford mandolin method, Swan's Architectural Acoustics), and "
     "lending-library scans (the 1941, 1955 and 1961 yearbooks' other copies): the builder could not read or date "
     "them. Index: https://archive.org/details/usda-yearbookofagriculture"),
    ("USDA Farmers' Bulletins on home economics, laundry and gardening (before 1931)", "Already in the library as "
     "pub:usda_farmers_bulletins (periodicals.py); not repeated one by one. Index: "
     "https://archive.org/details/usdanationalagriculturallibrary"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
