"""More books for the library's thin topics (the owner's request of 2026-11-21): the topics that had only one or two
books, and no Kiwix book of their own, get three to ten more open or public-domain books each.

How the thin topics were found: every book of sources.py, cookbooks.py, periodicals.py, publications_more.py,
medications.py, courses.py and drinks_reference.py was sorted into about fifty topics by its subject and title;
the LibreTexts catalogue's books with a usable licence (course:libretexts) and the Kiwix catalogue's English books
(the toolkit reads all of Kiwix) were counted for each topic too. A topic with a Kiwix book of its own (knots:
zimgit-knots; plants: Gardenology; emergencies: Ready.gov; first aid: MedlinePlus, WikEM and others; home repair:
iFixit) was not counted as thin. The thin topics, what was added and what could not be found are listed in THIN.

Everything here is a PDF_DOCS entry (sources.py adds this module's lists to its own, as it does reference_more's),
so the builder, the weekly update check (updates.pdf_sign), the "originals" list and the kept versions all work as
for every other PDF. Keys: thin (every book below), thin:<topic> (one topic, such as thin:birds), or pdf:<name>.

Where the books come from:
  - the Internet Archive's scans with their machine-read text of books published before 1931 (in the US public
    domain: the builder checks the item's publication year at every build, old_public_domain), many of them
    published by the US government (the Smithsonian's US National Museum bulletins, the Bureau of Biological
    Survey's North American Fauna);
  - official US government PDFs (IRS, USGS, NOAA, FAA): works of the US government (17 U.S.C. 105), the licence line
    checked at every build is govinfo's quotation of that law, as for the IRS and FAA books already built.
Every site's robots.txt was read on 2026-11-21 (archive.org, irs.gov, pubs.usgs.gov, faa.gov allow it; nauticalcharts.
noaa.gov has none) and is obeyed again at every build.
"""

# These names are the same as in sources.py (this module is imported at its end, so it cannot import them).
US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"
GOVINFO_POLICY = "https://www.govinfo.gov/about/policies"
GOVINFO_TEXT = r"Copyright protection under this title is not available for any work of the United States Government"
OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"

US_PDF = dict(country="United States", licence=US_GOV, licence_url=US_GOV_URL, licence_page=GOVINFO_POLICY,
              licence_text=GOVINFO_TEXT, level="reference")
OLD = dict(country="United States", licence=OLD_LICENCE, licence_url=OLD_URL, old_public_domain=True,
           level="reference",
           changes="its scanned pages' machine-read text (with the scanner's mistakes) made into web pages, ten pages "
                   "at a time or one per chapter")

# The notes every old book's description ends with (what is out of date in it).
OLD_ANIMAL_NOTE = (" Published in {year}: an old book whose names, ranges, numbers and advice are out of date (some "
                   "animals have been renamed, some are now rare or protected), kept for its descriptions of the "
                   "animals; the machine-read text has the scanner's mistakes.")
SNAKE_NOTE = ("Safety first: never touch or handle a snake that may be venomous. For a snakebite, call 911 (or the "
              "local emergency number) at once; in the US, Poison Control is 1-800-222-1222. ")
OLD_SEA_NOTE = (" Published in {year}: an old book whose rules of the road, equipment and safety advice are out of "
                "date; never use it for navigation (use current charts, the Navigation Rules and Notices to "
                "Mariners), kept for its explanations of boats, rigging and seamanship.")
OLD_SEWING_NOTE = (" Published in {year}: an old book whose patterns, sizes and fashions are out of date, kept for "
                   "its explanations of stitches and methods; measures are in inches and yards.")
TAX_NOTE = (" Tax laws change every year: this is the IRS's newest edition (the builder reads it again when the IRS "
            "changes it). Information, not tax advice.")
NAV_NOTE = " Not for navigation by itself: always use current official charts."


def _old(name, title, subject, group, publisher, archive, year, description, note=OLD_ANIMAL_NOTE, **extra):
    """One old public-domain book of the Internet Archive as a PDF_DOCS entry."""
    return dict(OLD, name=name, title=title, subject=subject, group=group, publisher=publisher, archive=archive,
                published=str(year), description=description + note.format(year=year), **extra)


def _gov(name, title, subject, group, publisher, description, published="", **where):
    """One US government publication (an official PDF address, or an Internet Archive copy) as a PDF_DOCS entry."""
    entry = dict(US_PDF, name=name, title=title, subject=subject, group=group, publisher=publisher,
                 description=description, **where)
    if published:
        entry["published"] = published
    return entry


USNM = "Smithsonian Institution, United States National Museum (Government Printing Office)"

# ---------------------------------------------------------------------- birds (had 2: Reed 1909, Chapman 1895)
BIRDS = [
    _old("bent_diving_birds_1919", "Life Histories of North American Diving Birds (A. C. Bent, 1919)", "Birds",
         "science", USNM + ", Bulletin 107", "cu31924094811852", 1919,
         "The first volume of Bent's famous life histories: grebes, loons, auks, murres and puffins, each bird's "
         "courtship, nest, eggs, young, plumages, food, behaviour, voice, migration and range, much of it in the "
         "words of the observers."),
    _old("bent_gulls_terns_1921", "Life Histories of North American Gulls and Terns (A. C. Bent, 1921)", "Birds",
         "science", USNM + ", Bulletin 113", "cu31924022523868", 1921,
         "Bent's life histories of the skuas, jaegers, gulls, terns and skimmers of North America."),
    _old("bent_petrels_pelicans_1922", "Life Histories of North American Petrels and Pelicans and Their Allies (A. C. "
         "Bent, 1922)", "Birds", "science", USNM + ", Bulletin 121", "cu31924094812041", 1922,
         "Bent's life histories of the albatrosses, shearwaters, petrels, tropicbirds, gannets, cormorants, "
         "pelicans and frigatebirds."),
    _old("bent_wild_fowl_1923", "Life Histories of North American Wild Fowl, part 1 (A. C. Bent, 1923)", "Birds",
         "science", USNM + ", Bulletin 126", "lifehistoriesofnawf00bent", 1923,
         "Bent's life histories of the mergansers and ducks of North America (the first part of the wild fowl)."),
    _old("bent_marsh_birds_1926", "Life Histories of North American Marsh Birds (A. C. Bent, 1926)", "Birds",
         "science", USNM + ", Bulletin 135", "lifehistoriesofn0005bent", 1926,
         "Bent's life histories of the flamingos, herons, bitterns, storks, ibises, cranes, rails, gallinules and "
         "coots."),
]

# ---------------------------------------------------------------------- mammals (had 1: Anthony 1928)
MAMMALS = [
    _old("stone_cram_american_animals_1902", "American Animals: a popular guide to the mammals of North America "
         "(Witmer Stone and William Everett Cram, 1902)", "Mammals", "science",
         "Witmer Stone and William Everett Cram (Doubleday, Page and Company)", "americananimal00ston", 1902,
         "A popular guide to the mammals of North America north of Mexico: how to recognise each, its habits, home "
         "and range, with the authors' field notes."),
    _old("seton_northern_animals_1_1909", "Life-Histories of Northern Animals, volume 1: grass-eaters (Ernest "
         "Thompson Seton, 1909)", "Mammals", "science", "Ernest Thompson Seton (Charles Scribner's Sons)",
         "lifehistoriesofn01seto", 1909,
         "Seton's account of the mammals of Manitoba and the north: deer, moose, caribou, bison, hares, squirrels, "
         "beavers, porcupines and the other plant-eaters, their lives through the year."),
    _old("seton_northern_animals_2_1909", "Life-Histories of Northern Animals, volume 2: flesh-eaters (Ernest "
         "Thompson Seton, 1909)", "Mammals", "science", "Ernest Thompson Seton (Charles Scribner's Sons)",
         "lifehistoriesofn02seto", 1909,
         "Seton's account of the meat-eating mammals of the north: wolves, foxes, bears, weasels, mink, otters, "
         "skunks, badgers, lynx and cougar, and the bats and shrews."),
    _old("cory_mammals_illinois_wisconsin_1912", "The Mammals of Illinois and Wisconsin (Charles B. Cory, 1912)",
         "Mammals", "science", "Charles B. Cory (Field Museum of Natural History)", "mammalsofillinoi00cory", 1912,
         "The Field Museum's handbook of the mammals of the Midwest, with keys to the species, their descriptions, "
         "measurements, habits and ranges."),
    _old("nelson_wild_animals_north_america_1918", "Wild Animals of North America (Edward W. Nelson, 1918)",
         "Mammals", "science", "Edward W. Nelson (National Geographic Society)", "wildanimalsofnor00nels", 1918,
         "The chief of the US Biological Survey's popular studies of the big and little mammals of North America."),
    _old("merriam_mammals_adirondack_1884", "The Mammals of the Adirondack Region (C. Hart Merriam, 1884)",
         "Mammals", "science", "C. Hart Merriam (published by the author)", "mammalsofadirond00merr", 1884,
         "The first chief of the US Biological Survey's study of the mammals of northeastern New York, from bats and "
         "shrews to moose, wolves and panthers, with long accounts of their habits."),
]

# ---------------------------------------------------------------------- reptiles and amphibians (had 2)
REPTILES = [
    _old("ditmars_reptiles_of_the_world_1910", "Reptiles of the World (Raymond L. Ditmars, 1910)", "Reptiles",
         "science", "Raymond L. Ditmars (Sturgis and Walton)", "reptilesofworld00ditm", 1910,
         SNAKE_NOTE + "The Bronx Zoo curator's account of the tortoises and turtles, crocodilians, lizards and snakes "
         "of the world: how to tell them apart, where they live and how they behave."),
    _old("stejneger_poisonous_snakes_na_1895", "The Poisonous Snakes of North America (Leonhard Stejneger, 1895)",
         "Reptiles (venomous snakes)", "science", USNM, "poisonoussnakeso00stej", 1895,
         SNAKE_NOTE + "The US National Museum's account of the coral snakes, rattlesnakes, copperhead and "
         "cottonmouth: how to recognise each, its range, and what was known of its venom. Its first-aid advice is "
         "out of date and must not be followed."),
    _old("stejneger_barbour_checklist_1917", "A Check List of North American Amphibians and Reptiles (Leonhard "
         "Stejneger and Thomas Barbour, 1917)", "Reptiles and amphibians", "science",
         "Leonhard Stejneger and Thomas Barbour (Harvard University Press)", "checklistofnorth00stejuoft", 1917,
         "The standard list of the salamanders, frogs, toads, turtles, lizards, snakes and crocodilians of North "
         "America, with each one's range."),
    _old("babcock_turtles_new_england_1919", "The Turtles of New England (Harold L. Babcock, 1919)", "Reptiles "
         "(turtles)", "science", "Harold L. Babcock (Boston Society of Natural History)", "turtlesofnewengl00babc",
         1919, "The turtles of the northeastern United States, land, pond and sea: how to recognise each, its habits, "
         "eggs and range."),
]

# ---------------------------------------------------------------------- insects and spiders (had 1: Holland 1902)
INSECTS = [
    _old("howard_insect_book_1901", "The Insect Book (L. O. Howard, 1901)", "Insects", "science",
         "L. O. Howard (Doubleday, Page and Company)", "insectbookpopu00howa", 1901,
         "The US government's chief entomologist's popular account of the bees, wasps, ants, grasshoppers, flies "
         "and other North American insects (not the butterflies and moths), their life histories and habits."),
    _old("lutz_field_book_insects_1918", "Field Book of Insects (Frank E. Lutz, 1918)", "Insects", "science",
         "Frank E. Lutz (G. P. Putnam's Sons)", "fieldbookofinsec00lutz", 1918,
         "The American Museum of Natural History's pocket field guide to the insects of the northeastern United "
         "States: how to name an insect you find, order by order."),
    _old("comstock_manual_study_insects_1895", "A Manual for the Study of Insects (John Henry Comstock and Anna "
         "Botsford Comstock, 1895)", "Insects", "science", "John Henry Comstock (Comstock Publishing Company)",
         "manualforstudyof1895coms", 1895,
         "Cornell's classic textbook of entomology: the structure of insects and every order and family, with keys "
         "to identify them."),
    _old("holland_moth_book_1903", "The Moth Book (W. J. Holland, 1903)", "Insects (moths)", "science",
         "W. J. Holland (Doubleday, Page and Company)", "mothbookpopularg00holla", 1903,
         "The companion of The Butterfly Book: a popular guide to the moths of North America, how to recognise them "
         "and their caterpillars."),
    _old("comstock_spider_book_1912", "The Spider Book (John Henry Comstock, 1912)", "Spiders", "science",
         "John Henry Comstock (Doubleday, Page and Company)", "thespiderbook00coms", 1912,
         "A manual of the spiders of the United States and their relatives, the scorpions, mites, ticks and "
         "harvestmen: their structure, webs, habits and how to identify them."),
    _old("comstock_how_to_know_butterflies_1904", "How to Know the Butterflies (John Henry Comstock and Anna "
         "Botsford Comstock, 1904)", "Insects (butterflies)", "science",
         "John Henry Comstock and Anna Botsford Comstock (D. Appleton and Company)", "cu31924022557353", 1904,
         "A manual of the butterflies of the eastern United States, with keys to identify them."),
]

# ---------------------------------------------------------------------- maps, navigation and charts (had 2)
USGS = "US Geological Survey (USGS), US Department of the Interior"
MAPS = [
    _gov("noaa_us_chart_no_1", "U.S. Chart No. 1: Symbols, Abbreviations and Terms used on Paper and Electronic "
         "Navigational Charts (NOAA and NGA)", "Maps and navigation (nautical charts)", "government",
         "NOAA Office of Coast Survey and the National Geospatial-Intelligence Agency",
         "The key to US nautical charts: every symbol, abbreviation and term on paper and electronic charts, with "
         "its meaning (depths, dangers, buoys and beacons, lights, ports, tracks and areas)." + NAV_NOTE,
         page="https://nauticalcharts.noaa.gov/publications/us-chart-1.html",
         pdf="https://nauticalcharts.noaa.gov/publications/docs/us-chart-1/ChartNo1.pdf"),
    _gov("faa_aeronautical_chart_users_guide", "Aeronautical Chart User's Guide (FAA)", "Maps and navigation "
         "(aeronautical charts)", "government", "Federal Aviation Administration (FAA), Aeronautical Information "
         "Services", "How to read the FAA's charts: the symbols of VFR sectional and terminal area charts, "
         "helicopter charts, IFR en route charts, terminal procedures and airport diagrams." + NAV_NOTE,
         page="https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/aero_guide/",
         pdf_pattern=r"aeronav\.faa\.gov/user_guide/cug-complete"),
    _gov("usgs_topographic_map_symbols", "Topographic Map Symbols (USGS)", "Maps and navigation (topographic maps)",
         "government", USGS, "The USGS's guide to reading a topographic map: contour lines and elevation, and the "
         "symbols for roads, buildings, boundaries, water, vegetation and landforms.",
         pdf="https://pubs.usgs.gov/gip/TopographicMapSymbols/topomapsymbols.pdf",
         page="https://pubs.usgs.gov/gip/TopographicMapSymbols/"),
    _gov("usgs_map_projections_working_manual", "Map Projections: A Working Manual (John P. Snyder, USGS "
         "Professional Paper 1395, 1987)", "Maps and navigation (map projections)", "government", USGS,
         "The standard reference on map projections: how the round Earth is drawn on a flat map, with the history, "
         "properties, uses and formulas of each projection the USGS uses.", "1987",
         pdf="https://pubs.usgs.gov/pp/1395/report.pdf", page="https://pubs.usgs.gov/publication/pp1395"),
    _gov("usgs_map_projections_bulletin_1532", "Map Projections Used by the U.S. Geological Survey (John P. Snyder, "
         "USGS Bulletin 1532)", "Maps and navigation (map projections)", "government", USGS,
         "The earlier, shorter USGS manual of the map projections it uses, with their properties and formulas.",
         "1982", pdf="https://pubs.usgs.gov/bul/1532/report.pdf", page="https://pubs.usgs.gov/publication/b1532"),
    _old("bowditch_american_practical_navigator_1914", "American Practical Navigator (Nathaniel Bowditch, US "
         "Hydrographic Office edition of 1914)", "Maps and navigation (navigation at sea)", "government",
         "US Navy Hydrographic Office (Government Printing Office)", "americanpracnavi00bowdrich", 1914,
         "\"Bowditch\", the classic US manual of navigation and nautical astronomy, with its tables (the National "
         "Geospatial-Intelligence Agency publishes the current edition, whose site could not be reached from the "
         "build machine).", note=OLD_SEA_NOTE.replace("rules of the road, equipment", "methods, tables") + NAV_NOTE),
]

# ---------------------------------------------------------------------- boating and seamanship (had 1: MSN 1560)
BOATING = [
    _old("knight_modern_seamanship_1921", "Modern Seamanship (Austin M. Knight, 1921)", "Boating and seamanship",
         "reference", "Austin M. Knight, Rear Admiral, US Navy (D. Van Nostrand Company)",
         "modernseamanship00knigrich", 1921,
         "The US Navy's standard book of seamanship: ships and their parts, rope and knots, anchors, boats and "
         "their handling, steering, the rules of the road, weather and storms, and handling ships in all "
         "conditions.", note=OLD_SEA_NOTE),
    _old("knight_small_boat_sailing_1902", "Small-Boat Sailing (E. F. Knight, 1902)", "Boating and seamanship",
         "reference", "E. F. Knight (E. P. Dutton and Company)", "smallboatsailing01knig", 1902,
         "An explanation of the management of small yachts, half-decked and open sailing boats: rigs, sails, "
         "handling under sail, moorings, and seamanship for beginners.", note=OLD_SEA_NOTE,
         country="United Kingdom"),
    _old("kemp_manual_yacht_boat_sailing_1900", "A Manual of Yacht and Boat Sailing (Dixon Kemp, 1900)", "Boating "
         "and seamanship", "reference", "Dixon Kemp (Horace Cox, London)", "manualofyachtboa00kemp", 1900,
         "The classic British manual of sailing: choosing, rigging and sailing yachts and small boats, seamanship, "
         "racing rules and boat design.", note=OLD_SEA_NOTE, country="United Kingdom"),
]

# ---------------------------------------------------------------------- sewing, knitting and needlework (had 1)
# In "Reference, arts and crafts" (the group of crafts_books.py), the one top-level group for crafts (the owner's
# request of 22 November 2026); they keep the request words of their old group "reference" (word_group, as
# power_books.py does), so group:reference still asks for them.
CRAFTS = "crafts"
SEWING = [
    _old("carens_dressmaking_self_taught_1911", "Dressmaking Self Taught in Twenty Complete Lessons (Edith Marie "
         "Carens, 1911)", "Sewing and dressmaking", CRAFTS, "Edith Marie Carens (Toledo, Ohio)",
         "dressmakingselft00care", 1911,
         "Twenty lessons in dressmaking: tools, taking measures, drafting and cutting patterns, stitches, seams, "
         "fitting and finishing.", note=OLD_SEWING_NOTE, word_group="reference"),
    _old("allington_practical_sewing_dressmaking_1913", "Practical Sewing and Dressmaking (Sara May Allington, 1913)",
         "Sewing and dressmaking", CRAFTS, "Sara May Allington (Dana Estes and Company)",
         "practicalsewingd00alli", 1913,
         "Hand and machine sewing from the first stitches: seams, hems, buttonholes, patching and darning, and "
         "making garments.", note=OLD_SEWING_NOTE, word_group="reference"),
    _old("butterick_new_dressmaker_1921", "The New Dressmaker (Butterick Publishing Company, 1921)", "Sewing and "
         "dressmaking", CRAFTS, "Butterick Publishing Company", "newdressmakerwit00butt", 1921,
         "Complete instructions on every point of dressmaking: stitches, seams, fitting, collars, sleeves, "
         "fastenings and children's clothes.", note=OLD_SEWING_NOTE, word_group="reference"),
    _old("butterick_art_of_knitting_1892", "The Art of Knitting (Butterick Publishing Company, 1892)", "Knitting",
         CRAFTS, "Butterick Publishing Company", "artofknitting00butt", 1892,
         "Knitting from casting on: the stitches, then patterns for stockings, mittens, shawls, children's clothes "
         "and lace, each worked out row by row.", note=OLD_SEWING_NOTE, word_group="reference"),
    _old("perkins_embroidery_crochet_knitting_1899", "A Treatise on Embroidery, Crochet and Knitting (George C. "
         "Perkins, 1899)", "Needlework (embroidery, crochet, knitting)", CRAFTS,
         "George C. Perkins (M. Heminway and Sons Silk Company)", "treatiseonembroi00perk", 1899,
         "The stitches of embroidery, crochet and knitting with silk, with patterns.", note=OLD_SEWING_NOTE, word_group="reference"),
    _old("robinson_priscilla_filet_crochet_1915", "The Priscilla Filet Crochet Book (Belle Robinson, 1915)",
         "Crochet", CRAFTS, "Belle Robinson (Priscilla Publishing Company)", "priscillafiletc00robi", 1915,
         "How to work filet crochet, with designs for edgings, insertions and pieces; the designs themselves are "
         "pictures of squares, described only by their captions.", note=OLD_SEWING_NOTE, word_group="reference"),
]

# ---------------------------------------------------------------------- taxes (had 3, one for disability)
IRS = "Internal Revenue Service (IRS), US Department of the Treasury"


def _irs(number, title, description):
    """One IRS publication (its newest PDF at irs.gov) as a PDF_DOCS entry."""
    file = number.lower().replace("-", "")
    return _gov(f"irs_pub_{file[1:]}", f"{title} (IRS Publication {number[1:]})", "Taxes", "consumer", IRS,
                description + TAX_NOTE, pdf=f"https://www.irs.gov/pub/irs-pdf/{file}.pdf",
                page=f"https://www.irs.gov/forms-pubs/about-publication-{file[1:]}")


TAXES = [
    _irs("p501", "Dependents, Standard Deduction, and Filing Information", "Who must file a federal income tax "
         "return, filing status, dependents and the standard deduction."),
    _irs("p502", "Medical and Dental Expenses", "Which medical and dental expenses (including those for a "
         "disability, guide dogs and equipment) can be deducted, and how."),
    _irs("p525", "Taxable and Nontaxable Income", "Which kinds of income are taxed and which are not: pay and "
         "benefits, sickness and injury benefits, gifts, prizes and others."),
    _irs("p526", "Charitable Contributions", "Which gifts to charity can be deducted, how much, and the records "
         "needed."),
    _irs("p590-A", "Contributions to Individual Retirement Arrangements (IRAs)", "Putting money into traditional "
         "and Roth IRAs: who may, how much, and the tax rules."),
    _irs("p590-B", "Distributions from Individual Retirement Arrangements (IRAs)", "Taking money out of IRAs: "
         "required minimum distributions, early withdrawals, inherited IRAs and the tax rules."),
    _irs("p915", "Social Security and Equivalent Railroad Retirement Benefits", "When Social Security and "
         "railroad retirement benefits are taxed, with the worksheets."),
    _irs("p970", "Tax Benefits for Education", "Education credits, student loan interest, scholarships, 529 plans "
         "and other tax help for education."),
    _irs("p596", "Earned Income Credit (EIC)", "Who can claim the earned income credit, with the rules for "
         "qualifying children and the worksheets."),
    _irs("p334", "Tax Guide for Small Business", "Federal taxes for sole proprietors and the self-employed: income, "
         "expenses, self-employment tax and records."),
]

# ---------------------------------------------------------------------- braille and blindness skills (had 1)
BRAILLE = [
    _old("braille_music_notation_1930", "Braille Music Notation (American Braille Press, 1930)", "Braille (music)",
         "disability", "American Braille Press", "braillemusicnota00unse", 1930,
         "An explanation of the braille music code of 1930: notes and their values, rests, octave marks, "
         "intervals and chords, and the other signs, with examples.",
         note=" Published in {year}: an old book, out of date: braille music signs have been revised since (the "
              "current code is "
              "the Music Braille Code 2015 and the New International Manual of Braille Music Notation), so check "
              "every sign against the current code; the machine-read text has the scanner's mistakes and its "
              "braille examples may be pictures."),
]

# Topic key -> (topic name, how many books it had before, its books). thin:<key> builds one topic.
THIN = {
    "birds": ("Birds", 2, BIRDS), "mammals": ("Mammals", 1, MAMMALS),
    "reptiles": ("Reptiles and amphibians", 2, REPTILES), "insects": ("Insects and spiders", 1, INSECTS),
    "maps": ("Maps, navigation and charts", 2, MAPS), "boating": ("Boating and seamanship", 1, BOATING),
    "sewing": ("Sewing, knitting and needlework", 1, SEWING), "taxes": ("Taxes", 3, TAXES),
    "braille": ("Braille and blindness skills", 1, BRAILLE),
}

PDF_DOCS = [entry for _name, _before, books in THIN.values() for entry in books]


def expand_keys(words):
    """The pdf:<name> keys of "thin" (every topic) or "thin:<topic>"."""
    keys = []
    for w in words:
        topics = list(THIN) if w == "thin" else [w[5:]]
        for topic in topics:
            keys += [f"pdf:{e['name']}" for e in THIN[topic][2]]
    return keys


LICENCE_LINES = {
    "thin_topics": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build); US "
                   "government publications: govinfo.gov/about/policies, \"Copyright protection under this title is "
                   "not available for any work of the United States Government\" (17 U.S.C. 105).",
}

# Looked at for the thin topics on 2026-11-21 and not added, with the reason.
NOT_INCLUDED = [
    ("Braille transcribing manuals and current braille codes (BANA, NLS, APH)", "Copyright of their publishers, with "
     "no open licence; the Rules of Unified English Braille (CC BY-NC-ND, whole and unchanged) and one public-domain "
     "braille music book are all that could be found. Old braille books (before 1931) describe codes no longer in "
     "use (New York Point, American Braille, English Braille before UEB), so they were not added as instruction."),
    ("Orientation and mobility, daily living skills for blind people", "No openly licensed or public-domain book was "
     "found (Perkins, Hadley, APH and others are copyright)."),
    ("The current American Practical Navigator (Bowditch, NGA Pub. 9)", "msi.nga.mil did not answer (503) from the "
     "build machine; the 1914 edition is added instead, marked old."),
    ("NOAA Nautical Chart User's Manual", "No longer at its address on nauticalcharts.noaa.gov (404); U.S. Chart "
     "No. 1 is added."),
    ("Navigation Rules (US Coast Guard)", "navcen.uscg.gov refuses automated requests (403)."),
    ("Later volumes of Bent's Life Histories of North American Birds (1932 to 1968)", "Works of the US government, "
     "but the Internet Archive's copies of the later volumes are mostly Dover reprints with the reprinter's own "
     "material; the five original Smithsonian volumes before 1931 are added."),
    ("Encyclopedia of Needlework (Thérèse de Dillmont)", "Public domain and already in the Kiwix library's Project "
     "Gutenberg books."),
]
