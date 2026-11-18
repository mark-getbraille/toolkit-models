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
  volunteers  the kinds of the Picture Describers export taken ("cooking", "directions", "warnings", "storage")
"""

OFF_US = 'countries_tags:"en:united-states"'
# More words for Wikidata's kinds ("instance of" labels such as "laptop model", "car model").
WIKIDATA_WORDS = {"personal_electronics": ["laptop", "computer", "keyboard", "monitor", "mobile phone", "camera",
                                           "smartwatch", "tablet computer", "headphone"],
                  "cars": ["car model", "automobile model", "vehicle model", "motorcycle model"],
                  "office_equipment": ["printer", "computer printer", "photocopier"],
                  "small_kitchen": ["kitchen appliance"], "home_appliances": ["home appliance", "major appliance"]}

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
    "home_appliances": dict(
        name="Home appliances (manuals)",
        description="Washers, dryers, dishwashers, microwave ovens, ranges, refrigerators, air conditioners, "
                    "thermostats, dehumidifiers and vacuum cleaners.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["washer", "washing machine", "dryer", "dishwasher", "microwave", "range", "oven", "refrigerator",
            "freezer", "air conditioner", "thermostat", "dehumidifier", "humidifier", "vacuum", "water heater",
            "heat pump", "furnace", "cooktop"],
        wikidata=True,
        energystar=["p5st-her9", "bghd-e2wd", "t9u7-4d2j", "5xn2-dv4h", "q8py-6w3f", "8t9c-g3tn", "mgiu-hu4z",
                    "7p2p-wkbf"]),
    "personal_electronics": dict(
        name="Personal electronics and phones (manuals)",
        description="Mobile phones, radios, headphones, speakers, cameras, music players, tablets, e-readers and "
                    "watches.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        ia=["mobile phone", "cell phone", "cellular", "smartphone", "radio", "headphones", "headset", "speaker",
            "digital camera", "camcorder", "mp3 player", "tablet", "e-reader", "watch", "gps", "walkie talkie",
            "television"],
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
}
