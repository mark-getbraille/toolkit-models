"""The manual and instruction collections, by category: what each one is, its licence, and where its products come
from (manuals/build_manuals.py builds them; the Digital Accessibility Toolkit downloads them with its Packages
window, category "Manual collections").

Two kinds:
  instructions  plain-text instructions published IN FULL, because their text is openly licensed: cooking
                instructions read from Open Food Facts' back-of-pack photos and its "preparation" field (CC BY-SA),
                and the instructions written and checked by the Picture Describers website's volunteers (their
                licence as given, CC BY-SA 4.0). Each record keeps its credit.
  manuals       an INDEX only: products (brand, model, name, barcodes, FCC IDs) with the addresses of their manuals
                at official sources whose terms allow automated use (the Internet Archive's documented search
                interface; Wikidata's "user manual URL" property, P2078, which points to makers' own sites; openFDA's
                device identifiers for health devices). The manuals themselves are the makers' copyright and are NOT
                published here: the toolkit fetches each one from its official address for the owner's own use.
                Thumbnails only when their licence allows passing them on (Wikimedia Commons CC0, CC BY, CC BY-SA).

Each category: name, description, kind, licence (of the index), and its sources:
  off         Open Food Facts (or a sister database) searches: [(database, query)] for search.openfoodfacts.org /
              the database's own v2 search
  ia          words searched in the titles of the Internet Archive's manual collections
  wikidata    True: the product models on Wikidata that have a user manual URL (P2078) and whose kind ("instance
              of" label) has one of the category's words (ia, plus WIKIDATA_WORDS)
  udi         openFDA device identifier searches (GMDN term names)
  energystar  ENERGY STAR certified-product datasets (data.energystar.gov ids): brand, model and, for some, the UPC
              barcode (US EPA data, a US government work)
  energuide   words of the file names of Natural Resources Canada's EnerGuide appliance lists ("dishwashers",
              "ranges"): brand and model of appliances sold in Canada (Open Government Licence - Canada)
  volunteers  the kinds of the Picture Describers export taken ("cooking", "directions", "warnings", "storage")
  makers      makers' own manual libraries (MAKERS below): read by the builder only where the maker's robots.txt
              allows it AND its terms do not forbid programs; otherwise the library's address is only listed, by
              hand, for the person to open (build_manuals.maker_entries)
  exclude     a regular expression: products and documents whose name or kind matches are never put in the index
  guidance    general guidance pages linked from the collection (title, address, who publishes it)
"""

OFF_US = 'countries_tags:"en:united-states"'
# More words for Wikidata's kinds ("instance of" labels such as "laptop model", "car model").
WIKIDATA_WORDS = {"personal_electronics": ["laptop", "computer", "keyboard", "monitor", "mobile phone", "camera",
                                           "smartwatch", "tablet computer", "headphone"],
                  "cars": ["car model", "automobile model", "vehicle model", "motorcycle model"],
                  "office_equipment": ["printer", "computer printer", "photocopier"],
                  "small_kitchen": ["kitchen appliance"], "home_appliances": ["home appliance", "major appliance"],
                  "computers": ["computer model", "personal computer", "desktop computer", "laptop", "notebook computer",
                                "video game console", "home video game console", "handheld game console", "router",
                                "computer monitor"],
                  "tv_audio_video": ["television", "television model", "smart TV", "home theater", "AV receiver",
                                     "streaming media player", "soundbar", "Blu-ray player", "DVD player"],
                  "older_electronics": ["videocassette recorder", "camcorder", "personal digital assistant",
                                        "portable cassette player", "portable CD player", "MiniDisc", "pager"],
                  "firearms": ["firearm model", "firearm", "pistol", "revolver", "rifle", "shotgun", "handgun",
                               "air gun", "air rifle", "air pistol", "BB gun", "gun safe"]}

# ------------------------------------------------------------------------------------------- firearms
# Why this collection exists (the owner's and his team's decision): a blind person living in a household with a
# firearm deserves the same information on handling, storing and maintaining it safely that its maker gives every
# sighted owner, in the maker's own owner's manual. The index holds facts and links only; the toolkit puts a short
# safety note first whenever it offers one of these manuals.
#
# Never in this collection (FIREARMS_EXCLUDE, checked on every product and document name and kind): suppressors and
# other NFA items, conversion or modification parts and kits, automatic-fire parts, unfinished receivers and jigs,
# reloading equipment, armorer's (gunsmith) manuals, and military-only weapon kinds; nor sales papers (catalogues,
# warranty and order forms, spec sheets).
FIREARMS_EXCLUDE = (r"suppressor|silencer|solvent trap|\bnfa\b|short[- ]barrel(?:l?ed)? (?:rifle|shotgun)|\bsb[rs]\b|"
                    r"conver(?:sion|t)|auto[- ]?sear|full[- ]?auto|select[- ]?fire|machine ?gun|machine pistol|"
                    r"submachine|assault rifle|battle rifle|automatic rifle|bump[- ]?stock|forced[- ]reset|"
                    r"binary trigger|trigger (?:kit|group|upgrade|information)|performance[- ]trigger|"
                    r"80 ?%|unfinished|jig\b|build kit|lower receiver|reload|powder measure|bullet mold|"
                    r"armou?rer|grenade|personal defen[cs]e weapon|anti[- ]materi[ae]l")
NOT_A_MANUAL = (r"warranty|buyer'?s? ?guide|annual|catalog|patent|order form|inspection form|awareness form|"
                r"price ?list|rebate|code of conduct|spec ?sheet|fact ?sheet|press release|dealer")

# The makers. access:
#   read     robots.txt allows programs and the terms (read on 2026-11-19) do not forbid them: the builder reads the
#            pages listed (only those) and keeps the manual links on them that point to the maker's own files
#            (hosts); "page_links": links to the maker's manuals published as web pages (Browning, Winchester).
#   link     the terms forbid robots, scraping or indexing, or the site refuses programs: nothing is read; the
#            library's address (entered by hand) is listed for the person to open in their browser.
#   mention  the terms forbid even linking without permission: the site is named in words only, no address.
# type: what the maker's products are when a document does not say ("pistol", "firearm", "airgun", "safe").
MAKERS = [
    dict(key="glock", maker="GLOCK", type="pistol", access="read",
         library="https://us.glock.com/en/owners-resources/downloadable-materials",
         pages=["https://us.glock.com/en/owners-resources/downloadable-materials"],
         hosts=["eu-assets.contentstack.com", "us.glock.com"],
         reason="robots.txt allows all; terms allow downloading content for personal, non-commercial use"),
    dict(key="henry", maker="Henry Repeating Arms", type="rifle", access="read",
         library="https://www.henryusa.com/own-a-henry/henry-owners-manuals/",
         pages=["https://www.henryusa.com/own-a-henry/henry-owners-manuals/"], hosts=["www.henryusa.com"],
         reason="robots.txt allows the page (crawl delay 10 seconds, kept); no terms page found"),
    dict(key="remington", maker="Remington", type="firearm", access="read",
         library="https://remington-arms.com/owners-manuals/", pages=["https://remington-arms.com/owners-manuals/"],
         hosts=["remington-arms.com"], reason="robots.txt allows all; no terms page found"),
    dict(key="browning", maker="Browning", type="firearm", access="read",
         library="https://www.browning.com/support/owners-manuals.html",
         pages=["https://www.browning.com/support/owners-manuals.html"], hosts=["www.browning.com"],
         page_links=r"^https://www\.browning\.com/support/owners-manuals/[a-z0-9-]+\.html$",
         reason="robots.txt allows the pages; its terms page has no rule against programs"),
    dict(key="winchester", maker="Winchester", type="firearm", access="read",
         library="https://www.winchesterguns.com/support/owners-manuals.html",
         pages=["https://www.winchesterguns.com/support/owners-manuals.html"], hosts=["www.winchesterguns.com"],
         page_links=r"^https://www\.winchesterguns\.com/support/owners-manuals/[a-z0-9-]+\.html$",
         reason="no robots.txt (all allowed); its legal page has no rule against programs"),
    dict(key="smith-wesson", maker="Smith & Wesson", type="firearm", access="mention", site="smith-wesson.com",
         reason="terms forbid data mining and placing links to its sites without permission"),
    dict(key="ruger", maker="Ruger", type="firearm", access="link",
         library="https://ruger.com/dataProcess/serialHistory/manuals.php",
         reason="terms forbid robots and indexing (only search engines)"),
    dict(key="marlin", maker="Marlin (Ruger)", type="rifle", access="link",
         library="https://www.marlinfirearms.com/s/instructionManuals/",
         reason="terms forbid robots and indexing (only search engines)"),
    dict(key="taurus", maker="Taurus", type="firearm", access="link", library="https://www.taurususa.com/support/",
         reason="terms forbid robots and indexing (only search engines)"),
    dict(key="savage", maker="Savage Arms", type="firearm", access="link",
         library="https://savagearms.com/content/manuals", reason="terms forbid data mining and robots"),
    dict(key="sig", maker="SIG Sauer", type="firearm", access="link",
         library="https://www.sigsauer.com/support/owners-manuals/",
         reason="the site refuses programs (HTTP 403), so its terms could not be read"),
    dict(key="mossberg", maker="Mossberg", type="firearm", access="link", library="https://www.mossberg.com/",
         reason="the site refuses programs (HTTP 403); manual library address not confirmed"),
    dict(key="springfield", maker="Springfield Armory", type="firearm", access="link",
         library="https://support.springfield-armory.com/manuals",
         reason="the manual list is built by scripts in the browser; not read"),
    dict(key="kimber", maker="Kimber", type="firearm", access="link",
         library="https://www.kimberamerica.com/manuals-and-catalogs",
         reason="the site refuses programs (HTTP 403); address from Kimber's own FAQ"),
    dict(key="beretta", maker="Beretta", type="firearm", access="link",
         library="https://www.beretta.com/en/services/beretta-services/user-manuals",
         reason="robots.txt could not be read from the build machine; not read"),
    dict(key="benelli", maker="Benelli", type="shotgun", access="link", library="https://www.benelliusa.com/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="cz", maker="CZ", type="firearm", access="link", library="https://www.czfirearms.com/hub",
         reason="the site could not be reached from the build machine; not read"),
    dict(key="hk", maker="Heckler & Koch (civilian models)", type="firearm", access="link",
         library="https://hk-usa.com/", reason="the site refuses programs (HTTP 403)"),
    # Airguns and BB guns.
    dict(key="umarex", maker="Umarex", type="airgun", access="link", library="https://www.umarexusa.com/product-manuals",
         reason="its manual files are on mediacenter.umarexusa.com, whose robots.txt disallows everything"),
    dict(key="crosman", maker="Crosman", type="airgun", access="link", library="https://www.crosman.com/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="daisy", maker="Daisy", type="airgun", access="link", library="https://www.daisy.com/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="gamo", maker="Gamo", type="airgun", access="link", library="https://www.gamousa.com/",
         reason="the site refuses programs (HTTP 403)"),
    # Safes and locks for storing firearms.
    dict(key="sentrysafe", maker="SentrySafe", type="safe", access="link",
         library="https://www.sentrysafe.com/support/product-manuals",
         reason="terms (Master Lock) forbid spiders, robots and indexers"),
    dict(key="stack-on", maker="Stack-On", type="safe", access="link",
         library="https://stack-on.com/support/product-manuals/", reason="terms forbid bots and scraping tools"),
    dict(key="liberty", maker="Liberty Safe", type="safe", access="link", library="https://libertysafe.com/",
         reason="terms forbid robots and spiders"),
    dict(key="vaultek", maker="Vaultek", type="safe", access="link", library="https://vaulteksafe.com/",
         reason="terms forbid spidering, crawling and scraping"),
]

# General safe-storage guidance linked from the collection (linking allowed: NSSF's linking policy grants plain-text
# links to projectchildsafe.org).
FIREARMS_GUIDANCE = [
    dict(title="Securing your firearm (Project ChildSafe)", url="https://projectchildsafe.org/securing-your-firearm/",
         by="Project ChildSafe, a program of the National Shooting Sports Foundation"),
]

CATEGORIES = {
    "frozen_meals": dict(
        name="Frozen and microwave meals (cooking instructions)",
        description="Cooking instructions of frozen pizzas, frozen meals and microwave meals sold in the United "
                    "States, as plain text in numbered steps, found by barcode or photo.",
        kind="instructions", licence="CC BY-SA 4.0 (Open Food Facts contributors; Picture Describers volunteers)",
        off=[("food", f'categories_tags:"{tag}" AND {OFF_US}') for tag in
             ("en:frozen-pizzas", "en:frozen-ready-made-meals", "en:microwave-meals", "en:frozen-meals",
              "en:frozen-foods", "en:pizzas", "en:instant-noodles", "en:frozen-appetizers", "en:pot-pies",
              "en:frozen-entrees", "en:frozen-breakfasts", "en:frozen-vegetables")],
        volunteers=("cooking",)),
    "product_directions": dict(
        name="Product directions (beauty, cleaning and household)",
        description="Directions for use and warnings printed on beauty, cleaning and household products, as plain "
                    "text, found by barcode or photo.",
        kind="instructions", licence="CC BY-SA 4.0 (Open Beauty Facts and Open Products Facts contributors; "
                                     "Picture Describers volunteers)",
        off=[("beauty", "countries_tags_en=united-states"), ("products", "countries_tags_en=united-states")],
        volunteers=("directions", "warnings", "storage")),
    "small_kitchen": dict(
        name="Small kitchen appliances (manuals)",
        description="Toasters, blenders, coffee makers, mixers, food processors, slow cookers, rice cookers, air "
                    "fryers, kettles and more.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["toaster", "blender", "coffee maker", "coffeemaker", "mixer", "food processor", "slow cooker",
            "rice cooker", "air fryer", "juicer", "kettle", "waffle", "bread maker", "breadmaker", "espresso",
            "toaster oven", "can opener", "griddle", "deep fryer", "pressure cooker"],
        wikidata=True),
    "office_supplies": dict(
        name="Office supplies (manuals)",
        description="Staplers, label makers, laminators, calculators, paper cutters and pencil sharpeners.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["label maker", "labeler", "label printer", "laminator", "calculator", "stapler", "paper cutter",
            "pencil sharpener", "postage scale", "binding machine"]),
    "computers": dict(
        name="Computers, game consoles and home networks (manuals)",
        description="Desktop and laptop computers, monitors, keyboards, mice, printers' cousins the scanners aside: "
                    "routers, modems, Wi-Fi extenders, external drives, webcams and game consoles.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["desktop computer", "laptop", "notebook computer", "computer", "monitor", "keyboard", "mouse",
            "router", "modem", "wireless", "network", "hard drive", "external drive", "webcam", "chromebook",
            "macbook", "imac", "thinkpad", "nintendo", "playstation", "xbox", "game console", "sega"],
        wikidata=True),
    "tv_audio_video": dict(
        name="Televisions, home theater and audio (manuals)",
        description="Televisions, remote controls, cable and satellite boxes, streaming players, DVD and Blu-ray "
                    "players, soundbars, home theater receivers, stereos, CD players and turntables.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["television", "tv", "lcd tv", "plasma", "remote control", "universal remote", "cable box",
            "satellite receiver", "digital converter", "roku", "streaming", "dvd player", "blu-ray", "soundbar",
            "home theater", "receiver", "amplifier", "stereo", "cd player", "turntable", "boombox"],
        wikidata=True, energystar=["pd96-rr3d"]),
    "older_electronics": dict(
        name="Older electronics still around (1990s and 2000s manuals)",
        description="VCRs, TV-VCR combos, camcorders, DVD recorders, cassette and CD players, Walkmans and "
                    "Discmans, MiniDisc, answering machines, cordless phones, pagers, PDAs, film cameras, clock "
                    "radios and digital photo frames.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["vcr", "videocassette recorder", "video cassette recorder", "tv/vcr", "camcorder", "video camera",
            "dvd recorder", "cassette", "walkman", "discman", "minidisc", "answering machine", "cordless",
            "pager", "palm", "pda", "film camera", "35mm", "clock radio", "photo frame", "caller id",
            "word processor", "typewriter"],
        wikidata=True),
    "office_equipment": dict(
        name="Office equipment (manuals)",
        description="Printers, copiers, shredders, fax machines, scanners and office telephones.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["printer", "copier", "shredder", "fax", "scanner", "cordless phone", "telephone", "answering machine",
            "projector", "multifunction"],
        wikidata=True),
    "power_tools": dict(
        name="Power tools (manuals)",
        description="Drills, saws, sanders, grinders, routers, impact drivers and nailers.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["drill", "circular saw", "jigsaw", "miter saw", "table saw", "sander", "grinder", "router",
            "impact driver", "nailer", "rotary tool", "chainsaw", "trimmer", "leaf blower", "pressure washer"]),
    "hand_tools": dict(
        name="Hand and measuring tools (manuals)",
        description="Laser levels, multimeters, stud finders, calipers, tape measures and torque wrenches.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["laser level", "multimeter", "stud finder", "caliper", "tape measure", "torque wrench",
            "laser measure", "distance meter", "voltage tester", "thermometer gun"]),
    "lawn_garden": dict(
        name="Lawn, garden and outdoor equipment (manuals)",
        description="Lawn mowers and riding mowers, string trimmers, leaf blowers, hedge trimmers, snow blowers, "
                    "tillers, chainsaws, generators, pressure washers, sprinkler timers, grills and smokers.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["lawn mower", "lawnmower", "riding mower", "lawn tractor", "zero turn", "string trimmer",
            "weed eater", "leaf blower", "hedge trimmer", "snow blower", "snowblower", "snow thrower", "tiller",
            "chainsaw", "generator", "pressure washer", "sprinkler", "irrigation", "gas grill", "grill",
            "smoker", "edger", "log splitter", "pool pump"]),
    "home_systems": dict(
        name="Around the house: safety, comfort and smart home (manuals)",
        description="Smoke and carbon monoxide alarms, garage door openers, doorbells, security systems, smart "
                    "speakers, light timers, ceiling fans, space heaters, fans, air purifiers, water softeners, "
                    "garbage disposals, sump pumps, alarm clocks and sewing machines.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["smoke alarm", "smoke detector", "carbon monoxide", "garage door", "doorbell", "security system",
            "alarm system", "smart speaker", "echo", "timer", "ceiling fan", "space heater", "fan",
            "air purifier", "water softener", "water filter", "garbage disposal", "sump pump", "alarm clock",
            "sewing machine", "iron", "steamer", "hair dryer", "shaver", "electric toothbrush", "treadmill",
            "exercise bike", "elliptical"],
        energystar=[]),
    "home_appliances": dict(
        name="Home appliances (manuals)",
        description="Washers, dryers, dishwashers, microwave ovens, ranges, refrigerators, air conditioners, "
                    "thermostats, dehumidifiers and vacuum cleaners, with the models sold in Canada (EnerGuide).",
        kind="manuals", licence="CC0 (facts and links); EnerGuide models: Open Government Licence - Canada; each "
                                "manual belongs to its maker",
        ia=["washer", "washing machine", "dryer", "dishwasher", "microwave", "range", "oven", "refrigerator",
            "freezer", "air conditioner", "thermostat", "dehumidifier", "humidifier", "vacuum", "water heater",
            "heat pump", "furnace", "cooktop"],
        wikidata=True,
        energystar=["p5st-her9", "bghd-e2wd", "t9u7-4d2j", "5xn2-dv4h", "q8py-6w3f", "8t9c-g3tn", "mgiu-hu4z",
                    "7p2p-wkbf"],
        energuide=["clothes dryers", "clothes washers", "cooktops", "dishwashers", "freezers", "ovens", "ranges",
                   "refrigerators", "room air conditioners"]),
    "personal_electronics": dict(
        name="Personal electronics and phones (manuals)",
        description="Mobile phones, radios, headphones, speakers, digital cameras, music players, tablets, "
                    "e-readers and watches.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["mobile phone", "cell phone", "cellular", "smartphone", "radio", "headphones", "headset", "speaker",
            "digital camera", "mp3 player", "tablet", "e-reader", "watch", "gps", "walkie talkie"],
        wikidata=True, energystar=["pd96-rr3d"]),
    "accessibility": dict(
        name="Accessibility devices (manuals)",
        description="Talking clocks, watches, scales and thermometers, braille displays, magnifiers, DAISY "
                    "players, hearing aids and TTY telephones.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["talking", "braille", "magnifier", "daisy player", "victor reader", "screen reader", "hearing aid",
            "tty", "amplified phone", "large button", "low vision", "notetaker", "refreshable"],
        udi=['"hearing aid"', '"talking"']),
    "health_devices": dict(
        name="Health devices (manuals and device records)",
        description="Blood pressure monitors, glucose meters, thermometers, pulse oximeters, nebulizers and "
                    "scales: manuals at the Internet Archive and the FDA's device records (brand, model, barcode).",
        kind="manuals", licence="CC0 (facts and links); FDA device records are public domain; each manual "
                                "belongs to its maker",
        ia=["blood pressure", "glucose", "glucometer", "thermometer", "pulse oximeter", "oximeter", "nebulizer",
            "tens unit", "bathroom scale", "body fat"],
        udi=['"blood pressure monitor"', '"glucose meter"', '"blood glucose"', '"clinical thermometer"',
             '"pulse oximeter"', '"nebulizer"']),
    "cars": dict(
        name="Cars (owner's manuals)",
        description="Owner's manuals of car models from official free sources: the Internet Archive's manual "
                    "collections and makers' own sites listed by Wikidata.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["owner's manual", "owners manual", "owner manual"], ia_collections=("manuals_toyota",),
        wikidata=True),
    "firearms": dict(
        name="Firearms (owner's manuals)",
        description="Makers' own owner's and instruction manuals for civilian pistols, revolvers, rifles and "
                    "shotguns, airguns and BB guns, and gun safes and locks: how to handle, store, clean and "
                    "maintain them safely, as the maker tells every owner. Links only, fetched from the maker.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        makers=MAKERS, wikidata=True, exclude=FIREARMS_EXCLUDE, guidance=FIREARMS_GUIDANCE),
}
