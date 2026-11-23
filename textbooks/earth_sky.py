"""Weather, rocks and the sky for the reference library, in their own group "Reference, weather, rocks and the sky"
(the owner's request of 2026-11-23: practical offline knowledge of the weather, rocks, minerals, fossils and
prospecting, and the night sky). Keys: earth-sky (every book), the themes earth-weather, earth-rocks and
earth-night-sky, and earth:<name>.

What this module builds, in plain words:
  - the weather: the National Weather Service's Advanced Spotters' Field Guide (1992), the Air Force's Weather for
    Aircrews (AFH 11-203, two volumes), judged at every build by the release rule for military
    publications; and old public-domain weather books (before 1931): Moore's
    Descriptive Meteorology (1910, by the chief of the Weather Bureau), Humphreys's Physics of the Air (1920),
    Dunwoody's Weather Proverbs (US Signal Service, 1883), the Navy's Illustrative Cloud Forms (1897), the
    Meteorological Office's Cloud Forms according to the International Classification (1918) and Clayden's Cloud
    Studies (1905);
  - rocks, minerals, fossils and prospecting: the US Geological Survey's general-interest booklets, read whole from
    pubs.usgs.gov (Collecting Rocks, Gold, Natural Gemstones, Geologic Time, Fossils, Rocks and Time; Volcanoes,
    Monitoring Active Volcanoes, Eruptions of Hawaiian Volcanoes, Mount St. Helens, Earthquakes, the San Andreas
    Fault, the Interior of the Earth, Deserts), the Bureau of Land Management's pages on mining claims and locatable
    minerals, MSHA's Stay Out-Stay Alive page on abandoned mines, and old public-domain books: Dana's Manual of
    Mineralogy (Ford's 1912 edition), Dana's Minerals and How to Study Them (1895), Loomis's Field Book of Common
    Rocks and Minerals (1923), Kunz's Gems and Precious Stones of North America (1890), Kemp's Handbook of Rocks
    (1908), Anderson's The Prospector's Handbook (1911) and West's The Miner's Guide (1921);
  - the sky: NASA's eclipse pages (types, safety, future eclipses, history), NASA's planetary fact sheets (the
    numbers of every planet, the Moon and Pluto, from the National Space Science Data Center), NASA's facts pages for
    the Sun, the Moon and each planet, and three old beginner books not already in the library: Martin's The Friendly
    Stars (1907), Newcomb's Astronomy for Everybody (1902) and Serviss's Pleasures of the Telescope (1901);
  - earth:index, a guide in plain words to every weather, rock and sky book, manual and picture pack in the library,
    by subject, with the links-only sources (the WMO cloud atlas and others).

Every book carries the safety note of its theme: WEATHER_SAFETY (lightning: when thunder roars, go indoors; never
drive into flood water; spot storms only from a safe place), ROCK_SAFETY (stay out of mine shafts and tunnels, ask
before collecting, wear eye protection when hammering, know the land's rules; mercury and cyanide are poisons) or
SKY_SAFETY (never look at the Sun, even in an eclipse, without proper solar filters).

Already in the library and linked from the index, not repeated: the old weather, geology and astronomy books
(olife:, hfill:), NASA's teacher's guides (olife:nasa_*), NASA Skywatching, USGS earthquakes for everyone and the
water science school (science:), This Dynamic Earth (guide:usgs_this_dynamic_earth), the NWS weather safety pages
(prep:nws_safety), the 2011 Weather Spotter's Field Guide (radio:), the FAA Aviation Weather Handbook, the Army's
Meteorology for Army Aviators (skill:), the Navy's Aerographer's Mate manuals (rate:), ground water (apt:), and the cloud, sky, rock and fossil picture packs.

Not built (NOT_INCLUDED, with the reason and an address): the NWS JetStream weather school (its site refuses this
reader and the Wayback Machine did not answer), the Basic Spotters' Field Guide (no copy found), the WMO International
Cloud Atlas (copyright), and others listed below.

Run from the repository's folder:
  python3 textbooks/earth_sky.py earth:usgs_rocks_minerals_gold --out build/textbooks --limit 3
  python3 textbooks/earth_sky.py --list earth-sky
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker and the fixed page list
from old_ia_books import old_book  # noqa: E402

PREFIX = "earth"
GROUP = "earthsky"
GROUPS = {GROUP: "Reference, weather, rocks and the sky"}

WEATHER_SAFETY = ("Weather safety: when thunder roars, go indoors, and wait 30 minutes after the last thunder; never "
                  "drive or walk into flood water (turn around, don't drown); spot storms only from a safe place, "
                  "never chase them; follow the National Weather Service's warnings and NOAA Weather Radio.")
ROCK_SAFETY = ("Collecting and prospecting safety: stay out of old mine shafts, tunnels and pits (stay out, stay "
               "alive: they hold bad air, rotten timbers, deep water and old explosives); wear eye protection when "
               "you hammer or break rock; watch for falling rock, flash floods and heat; ask the landowner or land "
               "agency before you collect or dig, and learn the rules on public land and mining claims. Mercury and "
               "cyanide, used in old gold recovery, are poisons: never use them.")
SKY_SAFETY = ("Never look at the Sun, with or without binoculars or a telescope, even during an eclipse, except "
              "through proper solar filters made for it (ISO 12312-2 eclipse glasses): it blinds.")
OLD_NOTE = ("Published in {year}: an old book. Its science is that of its day: later discoveries have changed many "
            "of its facts and figures, and some of its methods and names are out of date.")
MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "military aircrews: its forecasting methods and equipment are those of its day. ")

USGS = "US Geological Survey (USGS), US Department of the Interior"
USGS_PAGE = "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits"
USGS_TEXT = r"the content of most USGS websites is in the U\.S\. Public Domain"
NASA = "National Aeronautics and Space Administration (NASA)"
NASA_PAGE = "https://www.nasa.gov/nasa-brand-center/images-and-media/"
NASA_TEXT = r"generally are not subject to copyright in the United States"
NASA_NOTICE = ("From NASA: \"NASA content ... generally are not subject to copyright in the United States\" (NASA's "
               "media usage guidelines, checked at every build); NASA does not endorse this copy. ")
BODY = (r"(?i)<body[^>]*>", r"(?i)</body>")


def _old(name, title, subject, publisher, archive, year, description, safety, country="United States", note=OLD_NOTE):
    """One old public-domain book of the Internet Archive (published before 1931) with its theme's safety note."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, notice=safety,
                    country=country)


def _mil(name, title, subject, publisher, archive, year, description):
    """One US military weather manual of the Internet Archive, judged by the release rule at every build
    (military=True: the builder reads its front pages and says truthfully what they print about distribution)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                    description=description, notice=MIL_NOTICE + WEATHER_SAFETY, military=True,
                    work=f"a work of the {publisher.split('(')[-1].rstrip(')')}")


def _usgs_gip(name, title, subject, folders, starts, description, units):
    """A book of USGS general-interest booklets (pubs.usgs.gov/gip/<folder>/), each read whole by following its own
    contents page; their old pages have no <main>, so the whole body is read, pictures left out."""
    alt = "|".join(folders)
    # a page of the booklet, or a chapter folder ("deserts/dunes/"), never the booklet's bare folder (its index page
    # again under a second address)
    pages = rf"^https://pubs\.usgs\.gov/gip/({alt})/(([A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.html?|[a-z0-9_-]+/)$"
    entry = K.guide(GROUP, name, title, subject, USGS, [f"https://pubs.usgs.gov/gip/{s}" for s in starts], pages,
                    description, "From the US Geological Survey: a US government work (public domain); the "
                    "booklets were written over many years, so some figures are old. " + ROCK_SAFETY, depth=3,
                    follow=pages, units=units, limit=200, content=BODY, drop=[r"(?i)<img\b[^>]*>"])
    return dict(entry, licence_page=USGS_PAGE, licence_text=USGS_TEXT)


# ====================================================================== the weather

WEATHER = [
    dict(K.us_pdf(GROUP, name="nws_advanced_spotters_field_guide_1992", title="Advanced Spotters' Field Guide "
                  "(National Weather Service, NOAA PA 92055, 1992)", subject="Storm spotting",
                  publisher="National Weather Service (NOAA)",
                  pdf="https://www.weather.gov/media/owlie/adv_spotters.pdf", page="https://www.weather.gov/skywarn/",
                  published="1992", version="1992 edition (weather.gov)",
                  description="The NWS guide for experienced SKYWARN spotters: the spotter's role, how thunderstorms "
                              "form and are structured, supercells and their parts (the updraft, the wall cloud, "
                              "the flanking line, the rear-flank downdraft), telling tornadoes from look-alikes "
                              "(scud, gustnadoes), hail and damaging winds, and spotter safety. Its radar wording is "
                              "that of 1992, before Doppler radar covered the country.",
                  notice="From the National Weather Service (NOAA), whose web pages and publications are in the "
                         "public domain. " + WEATHER_SAFETY),
         licence_page="https://www.weather.gov/disclaimer",
         licence_text=r"National Weather Service \(NWS\) Web pages are in the public domain"),
    _mil("usaf_afh_11_203_v1_weather_for_aircrews_1997", "Weather for Aircrews, Volume 1 (Air Force Handbook 11-203, "
         "1997)", "Weather for pilots", "Department of the Air Force (US Air Force)", "DTIC_ADA423996", 1997,
         "The Air Force's weather textbook for pilots, read whole: the atmosphere, temperature, pressure and "
         "density, wind, moisture and stability, clouds, fog and visibility, air masses and fronts, thunderstorms, "
         "turbulence, icing, and weather hazards in the mountains, deserts, tropics and polar lands."),
    _mil("usaf_afh_11_203_v2_weather_for_aircrews_2002", "Weather for Aircrews, Volume 2 (Air Force Handbook 11-203, "
         "2002)", "Weather for pilots", "Department of the Air Force (US Air Force)", "DTIC_ADA424298", 2002,
         "The second volume of the Air Force's weather textbook, read whole: weather reports and forecasts, weather "
         "codes and charts, and how to read them before and during a flight."),
    _old("moore_descriptive_meteorology_1914", "Descriptive Meteorology (Willis L. Moore, 1910, 1914 printing)",
         "Weather (old book)", "Willis L. Moore, chief of the US Weather Bureau (D. Appleton)",
         "descriptivemeteo00moor", 1914,
         "The Weather Bureau chief's textbook: the atmosphere, heat and temperature, pressure, winds and the "
         "general circulation, moisture, clouds, rain and snow, storms (cyclones, thunderstorms, tornadoes and "
         "hurricanes), weather forecasting and climate.", WEATHER_SAFETY),
    _old("humphreys_physics_of_the_air_1920", "Physics of the Air (W. J. Humphreys, 1920)", "Weather science (old book)",
         "William Jackson Humphreys, US Weather Bureau (Franklin Institute, Philadelphia)", "physicsofair00hump",
         1920,
         "A classic of weather science: the mechanics and heat of the atmosphere, winds and storms, thunder and "
         "lightning, and the optics of the sky (rainbows, halos, coronas and mirages).", WEATHER_SAFETY),
    _old("dunwoody_weather_proverbs_1883", "Weather Proverbs (H. H. C. Dunwoody, US Signal Service, 1883)",
         "Weather lore (old book)", "H. H. C. Dunwoody (US Army Signal Service, Government Printing Office)",
         "dunwoody-1883-weather-prov", 1883,
         "The Signal Service's collection of weather sayings from many countries, gathered by its observers: signs "
         "in the sky, the Sun and Moon, clouds, winds, animals and plants, sorted by subject, with notes on which "
         "have a basis in science.", WEATHER_SAFETY,
         note="Published in {year}: weather sayings, many with no basis in science; for a real forecast, listen to "
              "the National Weather Service."),
    _old("navy_illustrative_cloud_forms_1897", "Illustrative Cloud Forms for the Guidance of Observers in the "
         "Classification of Clouds (US Navy Hydrographic Office, 1897)", "Clouds (old book)",
         "Hydrographic Office (US Navy)",
         "IllustrativeCloudFormsForTheGuidanceOfObserversInTheClassificationOfClouds", 1897,
         "The Navy's guide for ships' observers to the international cloud names of 1896: each cloud type "
         "(cirrus, cirro-stratus, cirro-cumulus, alto-cumulus, alto-stratus, strato-cumulus, nimbus, cumulus, "
         "cumulo-nimbus and stratus) described in words, with its height and the weather it brings. Its pictures "
         "are described only by their captions.", WEATHER_SAFETY),
    _old("met_office_cloud_forms_1918", "Cloud Forms according to the International Classification (Meteorological "
         "Office, UK, 1918)", "Clouds (old book)", "Meteorological Office (Great Britain), His Majesty's Stationery "
         "Office", "cloudformsaccord00grearich", 1918,
         "The Meteorological Office's short guide to the ten international cloud types, with their definitions and "
         "descriptions in words. Crown copyright has ended in the UK, and it is public domain in the US as "
         "published before 1931.", WEATHER_SAFETY, country="United Kingdom"),
    _old("clayden_cloud_studies_1905", "Cloud Studies (Arthur W. Clayden, 1905)", "Clouds (old book)",
         "Arthur W. Clayden (John Murray, London)", "cu31924002961203", 1905,
         "A book about watching and understanding clouds: how clouds form, the cloud types, cloud heights and "
         "motion, and what clouds tell about the weather to come.", WEATHER_SAFETY, country="United Kingdom"),
]

# ====================================================================== rocks, minerals, fossils and prospecting

BLM = "https://www.blm.gov/programs/energy-and-minerals/mining-and-minerals/"
BLM_PAGES = [BLM + p for p in ("locatable-minerals", "locatable-minerals/mining-claims", "locatable-minerals/discovery",
                               "locatable-materials/explanation-of-location", "locatable-materials/surface-management",
                               "locatable-minerals/access-mining-notices-and-plans-operations", "unauthorized-use",
                               "about")]
DRUPAL_MAIN = (r'<main\b[^>]*>', r'</main>')

ROCKS = [
    _usgs_gip("usgs_rocks_minerals_gold", "Collecting rocks, gold, gemstones, geologic time and fossils (USGS "
              "general-interest booklets)", "Rocks, minerals and fossils",
              ("collect1", "prospect1", "gemstones", "geotime", "fossils"),
              ("collect1/collectgip.html", "prospect1/goldgip.html", "gemstones/index.html", "geotime/contents.html",
               "fossils/contents.html"),
              "Five USGS booklets for everyone, each read whole: Collecting Rocks (how to start a rock collection, "
              "where to look, tools and labelling), Gold (where gold is found, how it forms, panning and placer "
              "deposits), Natural Gemstones (what gems are, where they are found in the United States), Geologic "
              "Time (the ages of the Earth and how rocks are dated) and Fossils, Rocks, and Time (how fossils form "
              "and what they tell).",
              [(r"/collect1/", "Collecting rocks"), (r"/prospect1/", "Gold"), (r"/gemstones/", "Gemstones"),
               (r"/geotime/", "Geologic time"), (r"/fossils/", "Fossils, rocks and time")]),
    _usgs_gip("usgs_volcanoes_earthquakes", "Volcanoes, earthquakes, the Earth's interior and deserts (USGS "
              "general-interest booklets)", "Volcanoes and earthquakes",
              ("volc", "monitor", "hawaii", "msh", "earthq1", "earthq3", "interior", "deserts"),
              ("volc/index.html", "monitor/index.html", "hawaii/index.html", "msh/index.html", "earthq1/index.html",
               "earthq3/index.html", "interior/index.html", "deserts/index.html"),
              "Eight USGS booklets for everyone, each read whole: Volcanoes (how volcanoes form and erupt), "
              "Monitoring Active Volcanoes, Eruptions of Hawaiian Volcanoes, Mount St. Helens (the 1980 eruption), "
              "Earthquakes (what causes them and how they are measured), The San Andreas Fault, The Interior of the "
              "Earth, and Deserts: Geology and Resources.",
              [(r"/volc/|/monitor/|/hawaii/|/msh/", "Volcanoes"), (r"/earthq1/|/earthq3/", "Earthquakes"),
               (r"/interior/", "The interior of the Earth"), (r"/deserts/", "Deserts")]),
    dict(X.page_list_book(GROUP, "blm_mining_claims", "Mining claims and locatable minerals on public land (Bureau of "
                          "Land Management)", "Prospecting and mining claims",
                          "Bureau of Land Management (BLM), US Department of the Interior", BLM_PAGES,
                          r"^https://www\.blm\.gov/programs/energy-and-minerals/mining-and-minerals/[a-z0-9/-]+$",
                          "The BLM's pages on prospecting and mining on public land: locatable minerals (gold, "
                          "silver and others under the Mining Law of 1872), mining claims and sites, what a "
                          "discovery is, how a claim is located and recorded, surface management (casual use, "
                          "notices and plans of operations), and unauthorized use.",
                          "From the Bureau of Land Management: a work of the US government (public domain). Rules and "
                          "fees change: check with the BLM state office before you prospect or stake a claim. "
                          + ROCK_SAFETY, content=DRUPAL_MAIN)),
    dict(X.page_list_book(GROUP, "msha_stay_out_stay_alive", "Stay Out-Stay Alive: the dangers of abandoned mines "
                          "(Mine Safety and Health Administration)", "Abandoned mine safety",
                          "Mine Safety and Health Administration (MSHA), US Department of Labor",
                          ["https://www.msha.gov/stay-out-stay-alive"],
                          r"^https://www\.msha\.gov/stay-out-stay-alive$",
                          "MSHA's campaign page on the dangers of abandoned mines and quarries: deep shafts, bad "
                          "air, unstable rock and timbers, old explosives, deep cold water in quarries, and why to "
                          "stay out and report them.",
                          "From the Mine Safety and Health Administration: a work of the US government (public "
                          "domain). " + ROCK_SAFETY, content=DRUPAL_MAIN)),
    _old("dana_manual_of_mineralogy_1912", "Dana's Manual of Mineralogy (13th edition, revised by W. E. Ford, 1912)",
         "Mineralogy (old book)", "James Dwight Dana and William E. Ford (John Wiley and Sons)",
         "danasmanualofmin00danarich", 1912,
         "The classic student's manual for identifying minerals: crystals, the physical properties of minerals "
         "(hardness, cleavage, colour, streak, lustre), blowpipe and chemical tests, and every common mineral "
         "described, with the rocks they make.", ROCK_SAFETY),
    _old("dana_minerals_how_to_study_them_1895", "Minerals, and How to Study Them: A Book for Beginners in Mineralogy "
         "(Edward S. Dana, 1895)", "Mineralogy for beginners (old book)", "Edward Salisbury Dana (John Wiley and "
         "Sons)", "mineralshowtostu00danauoft", 1895,
         "A friendly beginner's book: what minerals are, crystals, how to test hardness and other properties, and "
         "the common minerals one by one, with hints on collecting.", ROCK_SAFETY),
    _old("loomis_field_book_rocks_minerals_1923", "Field Book of Common Rocks and Minerals (Frederic Brewster Loomis, "
         "1923)", "Rocks and minerals (old book)", "Frederic Brewster Loomis (G. P. Putnam's Sons)",
         "fieldbookofcommo0000loom", 1923,
         "A pocket field guide for identifying the rocks and minerals of the United States: simple tests in the "
         "field, then the minerals and rocks described one by one, with what to look for.", ROCK_SAFETY),
    _old("kunz_gems_precious_stones_north_america_1890", "Gems and Precious Stones of North America (George F. Kunz, "
         "1890)", "Gemstones (old book)", "George Frederick Kunz (Scientific Publishing Company, New York)",
         "gemspreciousston00kunzrich", 1890,
         "Tiffany's gem expert on the gems of North America: diamonds, sapphires, garnets, tourmaline, beryl, "
         "turquoise, agate, pearls and the rest, where each was found, and their value and history.", ROCK_SAFETY),
    _old("kemp_handbook_of_rocks_1908", "A Handbook of Rocks, for Use without the Microscope (James F. Kemp, 1908 "
         "edition)", "Rocks (old book)", "James Furman Kemp (D. Van Nostrand)", "handbookofrocksf00kempiala", 1908,
         "A handbook for naming rocks by eye and with a hand lens: the rock-forming minerals, igneous, sedimentary "
         "and metamorphic rocks, and a glossary of rock names.", ROCK_SAFETY),
    _old("anderson_prospectors_handbook_1911", "The Prospector's Handbook (J. W. Anderson, 1911 edition)",
         "Prospecting (old book)", "John William Anderson (Crosby Lockwood and Son, London)",
         "prospectorshandb00anderich", 1911,
         "A guide for prospectors and travellers looking for metal-bearing and other valuable minerals: reading the "
         "country rock, signs of ore, simple tests with the blowpipe and the pan, and the ores of gold, silver, "
         "copper, tin and other metals.", ROCK_SAFETY, country="United Kingdom",
         note=OLD_NOTE + " Its chemical tests use mercury, cyanide and strong acids, which are dangerous: never use "
                         "them."),
    _old("west_miners_guide_1921", "The Miner's Guide: A Ready Handbook for the Prospector and Miner (Horace J. West, "
         "1921)", "Prospecting (old book)", "Horace J. West (Los Angeles)", "minersguideready00west", 1921,
         "A small handbook for prospectors in the American West: identifying ores and minerals, testing and "
         "assaying in the field, and the mining laws and claim rules of its day.", ROCK_SAFETY,
         note=OLD_NOTE + " Its mining law is that of 1921: check today's rules with the Bureau of Land Management."),
]

# ====================================================================== the sky

NSSDC = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"
FACT_SHEETS = [NSSDC] + [NSSDC + f"{p}fact.html" for p in ("mercury", "venus", "earth", "moon", "mars", "jupiter",
                                                           "saturn", "uranus", "neptune", "pluto")] + \
    [NSSDC + p for p in ("planetfact_notes.html", "planet_table_ratio.html", "planet_table_british.html")]
FACTS = ["https://science.nasa.gov/sun/facts/", "https://science.nasa.gov/mercury/facts/",
         "https://science.nasa.gov/venus/venus-facts/", "https://science.nasa.gov/earth/facts/",
         "https://science.nasa.gov/moon/facts/", "https://science.nasa.gov/mars/facts/",
         "https://science.nasa.gov/jupiter/jupiter-facts/", "https://science.nasa.gov/saturn/facts/",
         "https://science.nasa.gov/uranus/facts/", "https://science.nasa.gov/neptune/neptune-facts/"]

SKY = [
    dict(K.guide(GROUP, "nasa_eclipses", "Eclipses: types, safety and future eclipses (NASA)", "Eclipses", NASA,
                 "https://science.nasa.gov/eclipses", r"^https://science\.nasa\.gov/eclipses(/[a-z0-9-]+){0,3}/?$",
                 "NASA's eclipse pages: the types of solar and lunar eclipses and why they happen, eye safety "
                 "during a solar eclipse, the coming eclipses and where to see them, the history of eclipses, a "
                 "glossary, the questions people ask, and citizen science.",
                 NASA_NOTICE + SKY_SAFETY, depth=2, follow=r"^https://science\.nasa\.gov/eclipses/[a-z0-9-]+/?$",
                 limit=80, units=[(r"/safety", "Eclipse safety"), (r"/future-eclipses", "Future eclipses"),
                                  (r".", "Eclipses")]),
         licence_page=NASA_PAGE, licence_text=NASA_TEXT),
    dict(X.page_list_book(GROUP, "nasa_planetary_fact_sheets", "Planetary Fact Sheets: the numbers of every planet, "
                          "the Moon and Pluto (NASA)", "Planets in numbers",
                          "NASA Goddard Space Flight Center, National Space Science Data Center", FACT_SHEETS,
                          r"^https://nssdc\.gsfc\.nasa\.gov/planetary/factsheet/([a-z_]+\.html)?$",
                          "NASA's planetary fact sheets, every sheet: the table of the planets (mass, diameter, "
                          "density, gravity, length of day, distance from the Sun, orbital period, temperature, "
                          "moons, rings), the same table compared with Earth and in miles, and a sheet for each "
                          "planet, the Moon and Pluto, with notes on what each number means.",
                          NASA_NOTICE + SKY_SAFETY), licence_page=NASA_PAGE, licence_text=NASA_TEXT),
    dict(X.page_list_book(GROUP, "nasa_planet_facts", "The Sun, the Moon and the planets: facts (NASA Science)",
                          "The solar system", NASA, FACTS,
                          r"^https://science\.nasa\.gov/[a-z]+/([a-z]+-)?facts/$",
                          "NASA Science's facts pages for the Sun, the Moon and each planet in plain words: size and "
                          "distance, orbit and rotation, moons and rings, structure, surface and atmosphere, and "
                          "what it would be like to stand there.", NASA_NOTICE + SKY_SAFETY, content=DRUPAL_MAIN),
         licence_page=NASA_PAGE, licence_text=NASA_TEXT),
    _old("martin_friendly_stars_1907", "The Friendly Stars (Martha Evans Martin, 1907)", "Stargazing (old book)",
         "Martha Evans Martin (Harper and Brothers)", "friendlystarsmar00martrich", 1907,
         "A gentle beginner's book on getting to know the bright stars one by one, season by season, by their "
         "colours and their places among their neighbours, without a telescope.", SKY_SAFETY,
         note=OLD_NOTE + " The stars are the same; the planet positions and some star facts are old."),
    _old("newcomb_astronomy_for_everybody_1902", "Astronomy for Everybody (Simon Newcomb, 1902, 1912 printing)",
         "Astronomy (old book)", "Simon Newcomb (Doubleday, Page)", "astronomyforever00newcrich", 1912,
         "A famous astronomer's popular book: the motions of the heavens, time and the calendar, the telescope, "
         "the Sun, the Moon and eclipses, the planets one by one, comets and meteors, and the stars and nebulae.",
         SKY_SAFETY),
    _old("serviss_pleasures_of_the_telescope_1901", "Pleasures of the Telescope (Garrett P. Serviss, 1901)",
         "Stargazing with a telescope (old book)", "Garrett P. Serviss (D. Appleton)", "pleasuresofteles00servrich",
         1901,
         "An illustrated guide for amateur astronomers with a small telescope: choosing and using a telescope, then "
         "the constellations season by season with their double stars, clusters and nebulae, and the Sun, Moon "
         "and planets.", SKY_SAFETY),
]

# ====================================================================== the index

SECTIONS = [
    ("How to use these books", "Books on the weather, on rocks, minerals, fossils and prospecting, and on the night "
     "sky. The modern government books come first in each part; the old books are history and say what is out of "
     "date.", [
         ("word", "earth-weather", "Every weather book of this section (request word)"),
         ("word", "earth-rocks", "Every rock, mineral and prospecting book (request word)"),
         ("word", "earth-night-sky", "Every sky book (request word)")]),
    ("Weather and storm safety", "Thunderstorms, lightning, tornadoes, floods, hurricanes and winter storms, and "
     "how to stay safe. " + WEATHER_SAFETY, [
         ("key", "prep:nws_safety", "Weather safety (National Weather Service)"),
         ("key", "radio:nws_weather_spotters_field_guide_2011", "Weather Spotter's Field Guide (SKYWARN, 2011)"),
         ("key", "earth:nws_advanced_spotters_field_guide_1992", "Advanced Spotters' Field Guide (NWS, 1992)"),
         ("link", "SKYWARN spotter classes (National Weather Service)", "https://www.weather.gov/skywarn/",
          "a US government page; open it in a browser")]),
    ("How the weather works", "The atmosphere, clouds, fronts, wind and forecasting.", [
        ("key", "earth:usaf_afh_11_203_v1_weather_for_aircrews_1997", "Weather for Aircrews, volume 1 (Air Force)"),
        ("key", "earth:usaf_afh_11_203_v2_weather_for_aircrews_2002", "Weather for Aircrews, volume 2: reports and "
                                                                      "forecasts"),
        ("key", "skill:army_fm_1_230_meteorology_for_army_aviators_1982", "Meteorology for Army Aviators (FM "
                                                                      "1-230, in the service skills books)"),
        ("key", "pdf:faa_aviation_weather_handbook", "Aviation Weather Handbook (FAA)"),
        ("key", "rate:navy_aerographers_mate_3_2_1976", "Aerographer's Mate 3 and 2 (Navy, 1976)"),
        ("key", "rate:navy_aerographers_mate_1_c_1974", "Aerographer's Mate 1 and C (Navy, 1974)"),
        ("key", "olife:usda_yearbook_1941_climate_and_man", "Climate and Man (USDA Yearbook 1941)"),
        ("link", "JetStream, the National Weather Service's online weather school", "https://www.noaa.gov/jetstream",
         "public domain, but its site refuses this library's reader; open it in a browser")]),
    ("Clouds", "The cloud types and what they tell about the weather.", [
        ("key", "earth:met_office_cloud_forms_1918", "Cloud Forms according to the International Classification "
                                                     "(1918)"),
        ("key", "earth:navy_illustrative_cloud_forms_1897", "Illustrative Cloud Forms (Navy, 1897)"),
        ("key", "earth:clayden_cloud_studies_1905", "Cloud Studies (1905)"),
        ("pack", "commons_sky_weather", "Cloud types, sky and weather, for the picture describer"),
        ("link", "WMO International Cloud Atlas", "https://cloudatlas.wmo.int/",
         "copyright of the World Meteorological Organization; open it in a browser"),
        ("link", "NWS and NASA cloud chart (PDF)", "https://www.weather.gov/media/owlie/cloud_chart.pdf",
         "a picture chart; open it in a browser")]),
    ("Old weather books (history)", "Weather science and weather lore before 1931.", [
        ("key", "earth:moore_descriptive_meteorology_1914", "Descriptive Meteorology (Moore, 1914)"),
        ("key", "earth:humphreys_physics_of_the_air_1920", "Physics of the Air (Humphreys, 1920)"),
        ("key", "earth:dunwoody_weather_proverbs_1883", "Weather Proverbs (Signal Service, 1883)"),
        ("key", "olife:milham_meteorology_1912", "Meteorology (Milham, 1912)"),
        ("key", "olife:henkel_weather_science_1911", "Weather Science (Henkel, 1911)")]),
    ("Rocks, minerals and gems", "Collecting and identifying rocks, minerals and gemstones. " + ROCK_SAFETY, [
        ("key", "earth:usgs_rocks_minerals_gold", "Collecting Rocks, Gold, Gemstones, Geologic Time, Fossils (USGS)"),
        ("key", "earth:loomis_field_book_rocks_minerals_1923", "Field Book of Common Rocks and Minerals (1923)"),
        ("key", "earth:dana_minerals_how_to_study_them_1895", "Minerals, and How to Study Them (1895)"),
        ("key", "earth:dana_manual_of_mineralogy_1912", "Dana's Manual of Mineralogy (1912)"),
        ("key", "earth:kemp_handbook_of_rocks_1908", "A Handbook of Rocks (1908)"),
        ("key", "earth:kunz_gems_precious_stones_north_america_1890", "Gems and Precious Stones of North America "
                                                                      "(1890)"),
        ("key", "olife:geikie_class_book_geology_1921", "Class-Book of Geology (1921)"),
        ("key", "olife:huxley_physiography_1905", "Physiography (Huxley, 1905)"),
        ("pack", "commons_rocks_fossils", "Minerals, gemstones, rocks and fossils, for the picture describer")]),
    ("Fossils and the Earth's history", "Fossils, geologic time and plate tectonics.", [
        ("key", "earth:usgs_rocks_minerals_gold", "Fossils, Rocks, and Time and Geologic Time (USGS)"),
        ("key", "guide:usgs_this_dynamic_earth", "This Dynamic Earth: plate tectonics (USGS)"),
        ("pack", "commons_rocks_fossils", "Fossils, for the picture describer")]),
    ("Gold prospecting and mining claims", "Panning, prospecting and the rules on public land. " + ROCK_SAFETY, [
        ("key", "earth:blm_mining_claims", "Mining claims and locatable minerals (BLM)"),
        ("key", "earth:msha_stay_out_stay_alive", "Stay Out-Stay Alive: abandoned mines (MSHA)"),
        ("key", "earth:anderson_prospectors_handbook_1911", "The Prospector's Handbook (1911)"),
        ("key", "earth:west_miners_guide_1921", "The Miner's Guide (1921)"),
        ("link", "USGS Mineral Resources Data System (where minerals have been found)", "https://mrdata.usgs.gov/",
         "a US government database; open it in a browser")]),
    ("Volcanoes, earthquakes and landslides", "How the ground moves, and how to stay safe.", [
        ("key", "earth:usgs_volcanoes_earthquakes", "Volcanoes, Mount St. Helens, Earthquakes, the San Andreas "
                                                    "Fault (USGS)"),
        ("key", "science:usgs_earthquakes_for_everyone", "Earthquakes for everyone (USGS)"),
        ("key", "gpo:fema_earthquake_checklist_2023", "Earthquake Safety Checklist (FEMA)")]),
    ("Water under the ground", "Wells, springs and ground water.", [
        ("key", "science:usgs_water_science_school", "The USGS Water Science School"),
        ("key", "apt:usgs_ground_water_rural_homeowner_1988", "Ground Water and the Rural Homeowner (USGS)")]),
    ("The night sky and stargazing", "Finding the stars and constellations. " + SKY_SAFETY, [
        ("key", "science:nasa_skywatching", "Skywatching: the night sky month by month (NASA)"),
        ("key", "earth:martin_friendly_stars_1907", "The Friendly Stars (1907)"),
        ("key", "olife:olcott_field_book_of_stars_1907", "A Field Book of the Stars (1907)"),
        ("key", "olife:serviss_astronomy_opera_glass_1890", "Astronomy with an Opera-Glass (1890)"),
        ("key", "earth:serviss_pleasures_of_the_telescope_1901", "Pleasures of the Telescope (1901)"),
        ("key", "hfill:serviss_astronomy_naked_eye_1908", "Astronomy with the Naked Eye (1908)"),
        ("key", "hfill:gall_easy_guide_constellations_1910", "An Easy Guide to the Constellations (1910)"),
        ("key", "hfill:barton_guide_constellations_1928", "A Guide to the Constellations (1928)"),
        ("key", "hfill:olcott_star_lore_1911", "Star Lore of All Ages (1911)"),
        ("key", "hfill:index", "Stars and navigation in the homestead skills guide")]),
    ("The Sun, the Moon, the planets and eclipses", "The solar system in words and numbers. " + SKY_SAFETY, [
        ("key", "earth:nasa_planet_facts", "The Sun, the Moon and the planets: facts (NASA)"),
        ("key", "earth:nasa_planetary_fact_sheets", "Planetary Fact Sheets (NASA)"),
        ("key", "earth:nasa_eclipses", "Eclipses and eclipse safety (NASA)"),
        ("key", "olife:nasa_exploring_the_moon_1994", "Exploring the Moon (NASA teacher's guide)"),
        ("key", "olife:nasa_mars_exploration_water_2000", "Is There Water on Mars? (NASA educator's guide)"),
        ("key", "olife:nasa_space_based_astronomy_1994", "Space-Based Astronomy (NASA teacher's guide)")]),
    ("Astronomy books", "Popular astronomy, old and new.", [
        ("key", "earth:newcomb_astronomy_for_everybody_1902", "Astronomy for Everybody (1902)"),
        ("key", "olife:ball_story_of_the_heavens_1887", "The Story of the Heavens (1887)"),
        ("key", "olife:serviss_curiosities_of_the_sky_1909", "Curiosities of the Sky (1909)"),
        ("word", "astronomy", "Astronomy, the OpenStax college textbook (request word)"),
        ("key", "olife:comstock_handbook_nature_study_1911", "Handbook of Nature-Study: rocks, weather and the sky "
                                                             "(1911)")]),
]
INDEX = X.index_maker(PREFIX, GROUP, "Weather, rocks and the sky: a guide to the library", "Weather, rocks and the sky",
                      "A guide in plain words to the weather, rocks, minerals, fossils, prospecting and the night sky "
                      "in the library: storm safety, clouds, how the weather works, collecting rocks and gems, gold "
                      "prospecting and mining claims, volcanoes and earthquakes, stargazing, the planets and "
                      "eclipses, with the picture packs and the links-only sources.", SECTIONS)
MAKERS = {"index": INDEX}


def _keys(entries):
    """The index first, then the keys of the entries."""
    return [f"{PREFIX}:index"] + [f"{PREFIX}:{e['name']}" for e in entries]


GUIDES = [e for e in WEATHER + ROCKS + SKY if e.get("crawl")]
PDFS = [e for e in WEATHER + ROCKS + SKY if not e.get("crawl")]
WORDS = {"earth-sky": lambda: _keys(WEATHER + ROCKS + SKY), "earth-weather": lambda: _keys(WEATHER),
         "earth-rocks": lambda: _keys(ROCKS), "earth-night-sky": lambda: _keys(SKY)}

COLLECTION = K.Collection(PREFIX, GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "earth_usgs_blm_msha": "pubs.usgs.gov (USGS: \"the content of most USGS websites is in the U.S. Public Domain\", "
                           "checked at every build), blm.gov and msha.gov (works of the US government, 17 U.S.C. "
                           "105, checked on govinfo.gov's policies page); robots.txt allows the pages, no AI rules "
                           "(checked 2026-11-23).",
    "earth_nasa_nws": "science.nasa.gov and nssdc.gsfc.nasa.gov (NASA's media usage guidelines: \"generally are not "
                      "subject to copyright in the United States\", checked at every build) and weather.gov "
                      "(weather.gov/disclaimer: \"National Weather Service (NWS) Web pages are in the public "
                      "domain\"); robots.txt allows the pages, no AI rules (checked 2026-11-23).",
    "earth_military": "Internet Archive copies of Air Force (DTIC) and Army weather manuals: works of the US "
                      "government, judged at every build by the release rule for military publications "
                      "(military_release.py); archive.org's robots.txt allows the files (checked 2026-11-23).",
    "earth_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build); "
                       "the Meteorological Office's Cloud Forms, Clayden and Anderson are British, public domain in "
                       "the US as published before 1931.",
    "earth_index": "The index (earth:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("NWS JetStream, the online school for weather", "Public domain (NOAA), but www.noaa.gov answers this library's "
     "reader \"403\" (checked again 2026-11-23), and the Wayback Machine (web.archive.org) could not be reached from "
     "the build machine to read its copies; link-only from earth:index. Index: https://www.noaa.gov/jetstream"),
    ("SKYWARN Basic Spotters' Field Guide", "No copy found on weather.gov or the Internet Archive "
     "(searched 2026-11-23); the 2011 Weather Spotter's Field Guide that replaced it is already built "
     "(radio:nws_weather_spotters_field_guide_2011), and the Advanced guide is built here. Index: "
     "https://www.weather.gov/skywarn/"),
    ("WMO International Cloud Atlas (1956, 1975, 1987 and the online edition)", "Copyright of the World "
     "Meteorological Organization; link-only. The 1896 international cloud names are explained in the Navy's 1897 "
     "guide and the Met Office's 1918 guide, built here. Index: https://cloudatlas.wmo.int/"),
    ("NWS cloud chart and other short NWS brochures", "Picture charts with few words (the cloud chart) or already "
     "covered by the NWS safety pages (prep:nws_safety); link-only. Index: "
     "https://www.weather.gov/media/owlie/cloud_chart.pdf"),
    ("Army and Air Force weather manuals for artillery and chemical warfare (TM 3-240, TM 4-240, FM 6-15, FM 3-09.15)",
     "About ballistic and gas meteorology for guns and chemical weapons, not weather for everyday use; not built. "
     "Index: https://archive.org/details/TM3-240"),
    ("Navy Aerographer's Mate rate training manuals", "Already built in the Navy rates collection (rate:navy_"
     "aerographers_mate_3_2_1976 and the others); linked from earth:index, not repeated. Index: "
     "https://archive.org/search?query=aerographer%27s+mate"),
    ("USGS general-interest booklets that are already in the library or not found", "This Dynamic Earth is built "
     "(guide:usgs_this_dynamic_earth) and Ground Water and the Rural Homeowner (apt:); Prospecting for Gold in the "
     "United States, Geology of Caves, Glaciers and Landslide Types answered \"404\" at their old addresses on "
     "pubs.usgs.gov (checked 2026-11-23). Index: https://pubs.usgs.gov/"),
    ("Old mineralogy and astronomy books already in the library", "Geikie's Class-Book of Geology, Huxley's "
     "Physiography, Milham's and Henkel's weather books, Serviss, Olcott, Ball, Norton, Gall, Barton and Burritt are "
     "built in oldbooks_life.py and homestead_fill.py; not repeated. Index: "
     "https://archive.org/search?query=astronomy+with+the+naked+eye"),
    ("Getting Gold (J. C. F. Johnson, 1898) and other old prospecting books without a text layer", "Their Internet "
     "Archive copies are scanned pictures without the words (no text PDF), so they cannot be read aloud. Index: "
     "https://archive.org/details/gettinggoldapra00johngoog"),
    ("Mindat, the American Meteor Society, Sky and Telescope and Heavens-Above", "Copyright of each site; link-only. "
     "Index: https://www.mindat.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
