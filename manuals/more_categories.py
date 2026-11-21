"""More manual collections (added 2026-11-21 from the reference inventory's top 50): baby gear and toys, home medical
and mobility equipment, amateur radio, musical instruments and pro audio, video games, motorcycles and outboard
motors, marine electronics, farm tractors, camping gear, software and vintage computers; and the Internet Archive
collections that no category reached before, each mapped to a category (COLLECTION_MAP).

How a category reaches the Internet Archive (build_manuals.ia_search and ia_collection_entries):
  ia          words searched in the titles of the whole Manual Library (collection "manuals", which includes every
              brand collection inside it) and "computermanuals", as before
  ia_whole    {collection: kind}: a collection whose every item belongs to the category (Hasbro's toys, a console's
              game manuals, the DLARC amateur radio library). Every item is listed, no title words needed. This is
              also how collections OUTSIDE the Manual Library (the DLARC ones) are searched.
  ia_mixed    {collection: kind}: a collection that holds other products too (Graco's paint sprayers beside its car
              seats; Yamaha's motorcycles beside its keyboards and receivers): searched with the category's words
  any_year    True: items older than 1990 are kept (old game consoles, synthesizers, tractors, ham radios and home
              computers are still used and collected)
  ia_exclude  a regular expression: Internet Archive items whose title matches are left out (catalogues; for the
              firearms collection, everything firearms.FIREARMS_EXCLUDE forbids and every military manual, which
              is taken only through categories.PUBLIC_MANUALS with its Distribution Statement A check)
  notice      a short safety notice the toolkit says first
Only facts and links are published (the index); the manuals stay at the Internet Archive and belong to their makers.

The Internet Archive's robots.txt allows advancedsearch.php and metadata/, its documented interfaces, which the
builder already uses; the collection names below were read from its own lists on 2026-11-21.
"""

INDEX_LICENCE = "CC0 (facts and links); each manual belongs to its maker"
FDA_LICENCE = "CC0 (facts and links); FDA device records are public domain; each manual belongs to its maker"
CATALOGUES = r"\bcatalog(?:ue)?s?\b|price ?list|flyer|brochure|advertis|order form|\bad\b"

# Video game manuals: each console's own collection (its "kind" names the console).
GAME_COLLECTIONS = {
    "manuals_snes": "Super Nintendo game manual", "snes-kirklands-manual-labor": "Super Nintendo game manual",
    "famicommanuals": "Famicom (Japanese NES) game manual", "nintendo64manuals": "Nintendo 64 game manual",
    "gameboyadvancemanuals": "Game Boy Advance game manual", "tabor62gbamanual": "Game Boy Advance game manual",
    "virtualboymanuals": "Virtual Boy game manual", "playstationmanuals": "PlayStation game manual",
    "sonyplaystation2manuals": "PlayStation 2 game manual", "ps2-kirklands-manual-labor": "PlayStation 2 game manual",
    "xboxmanuals": "Xbox game manual", "xbox360manuals": "Xbox 360 game manual",
    "sega_master_system_manuals": "Sega Master System game manual", "segagenesismanuals": "Sega Genesis game manual",
    "megacdmanuals": "Sega CD (Mega-CD) game manual", "sega32xmanuals": "Sega 32X game manual",
    "segasaturnmanuals": "Sega Saturn game manual", "segadreamcastmanuals": "Sega Dreamcast game manual",
    "sg1000manuals": "Sega SG-1000 game manual", "atari2600manuals": "Atari 2600 game manual",
    "a2600-kirklands-manual-labor": "Atari 2600 game manual", "atari5200manuals": "Atari 5200 game manual",
    "atari7800manuals": "Atari 7800 game manual", "atarijaguarmanuals": "Atari Jaguar game manual",
    "atarilynxmanuals": "Atari Lynx game manual", "colecovisionmanuals": "ColecoVision game manual",
    "intellivisionmanuals": "Intellivision game manual", "magnavoxodysseymanuals": "Magnavox Odyssey game manual",
    "odysseymanuals": "Odyssey 2 game manual", "ballyastrocademanuals": "Bally Astrocade game manual",
    "apf_imagination_machine": "APF Imagination Machine manual", "3domanuals": "3DO game manual",
    "amigacdtvmanuals": "Amiga CDTV game manual", "cd32manuals": "Amiga CD32 game manual",
    "amstradgx4000manuals": "Amstrad GX4000 game manual", "neogeomanuals": "Neo Geo game manual",
    "turbografix16manuals": "TurboGrafx-16 game manual", "philipscdimanuals": "Philips CD-i game manual",
    "manuals_nuon": "Nuon game manual", "manuals_epoch": "Epoch console game manual",
    "manuals-handheld-games": "handheld electronic game manual", "gamemanuals_atari8bit": "Atari 8-bit computer game manual",
    "gamemanuals_c64": "Commodore 64 game manual", "gamemanuals_msx": "MSX computer game manual",
    "arcademanuals": "arcade machine manual", "gamemanuals": "computer game manual",
    "consolemanuals_unsorted": "console game manual", "consolemanuals": "console game manual",
}

# The synthesizer collection's makers (each a sub-collection of "synthmanuals", which is searched whole: a search of
# a collection includes its sub-collections, checked on 2026-11-21: synthmanuals AND synthmanuals-roland = 313).
SYNTH_SUBCOLLECTIONS = [
    "synthmanuals-akai", "synthmanuals-alesis", "synthmanuals-analogue-solutions", "synthmanuals-analogue-systems",
    "synthmanuals-aries", "synthmanuals-arp", "synthmanuals-arturia", "synthmanuals-buchla", "synthmanuals-casio",
    "synthmanuals-cbs", "synthmanuals-cockos", "synthmanuals-crumar", "synthmanuals-digisound", "synthmanuals-doepfer",
    "synthmanuals-drbohm", "synthmanuals-edirol", "synthmanuals-elby", "synthmanuals-electronic-music-laboratories",
    "synthmanuals-electronics-today-maplin", "synthmanuals-emu", "synthmanuals-encore", "synthmanuals-fairlight",
    "synthmanuals-flame", "synthmanuals-formanta", "synthmanuals-frequency", "synthmanuals-futureretro",
    "synthmanuals-hinton", "synthmanuals-intellijel", "synthmanuals-kawai", "synthmanuals-kenton",
    "synthmanuals-korg", "synthmanuals-linn", "synthmanuals-lunar", "synthmanuals-m-audio", "synthmanuals-madrona",
    "synthmanuals-makenoise", "synthmanuals-malekko", "synthmanuals-manikin", "synthmanuals-megaohm",
    "synthmanuals-metasonix", "synthmanuals-mfb", "synthmanuals-misc", "synthmanuals-moog", "synthmanuals-novation",
    "synthmanuals-oakley", "synthmanuals-oberheim", "synthmanuals-octave", "synthmanuals-paia",
    "synthmanuals-philiprees", "synthmanuals-propellerhead", "synthmanuals-ralphdyck", "synthmanuals-roland",
    "synthmanuals-rupertneve", "synthmanuals-sequential", "synthmanuals-sherman", "synthmanuals-siel",
    "synthmanuals-ssl", "synthmanuals-steinberg", "synthmanuals-sycologic", "synthmanuals-tiptop",
    "synthmanuals-univox", "synthmanuals-waldorf", "synthmanuals-waves", "synthmanuals-yamaha",
]

# Old home computers (their own collections; the "computers" category's words caught only some titles).
VINTAGE_COMPUTER_COLLECTIONS = {
    "manuals_commodore": "Commodore computer manual", "commodore_c64_manuals": "Commodore 64 manual",
    "vic20manuals": "Commodore VIC-20 manual", "commodorec16manuals": "Commodore 16 manual",
    "commodore128manuals": "Commodore 128 manual", "commodore-manuals": "Commodore computer manual",
    "atari8bitmanuals": "Atari 8-bit computer manual", "ataristmanuals": "Atari ST manual",
    "trs80manuals": "TRS-80 computer manual", "tandycocomanuals": "Tandy Color Computer manual",
    "dicksmithsystem80manuals": "Dick Smith System 80 manual", "eg2000colourgeniesmanuals": "EG2000 Colour Genie manual",
    "apple_documentation": "Apple computer manual", "manuals-apple": "Apple computer manual",
    "apple_tech_info_library": "Apple Tech Info Library note", "apple_iigs_technical_notes": "Apple IIGS technical note",
    "texasinstrumentsmanuals": "Texas Instruments computer manual", "dragondatamanuals": "Dragon computer manual",
    "msxpalcommanuals": "MSX computer manual", "amstradcpcmanuals": "Amstrad CPC manual",
    "archimedesmanuals": "Acorn Archimedes manual", "acornsystem1manuals": "Acorn System 1 manual",
    "jupiteracemanuals": "Jupiter Ace manual", "exidysorcerermanuals": "Exidy Sorcerer manual",
    "microkeyprimomanuals": "Microkey Primo manual", "aamberpegasusmanuals": "Aamber Pegasus manual",
    "homelabmanuals": "Homelab computer manual", "dec-manuals": "DEC computer manual",
    "manuals_hack42": "computer manual (Hack42 scans)", "computermanuals_miscellaneous": "computer manual",
}

CATEGORIES = {
    # 1. Baby gear and toys.
    "baby_gear": dict(
        name="Baby gear and toys (manuals)",
        description="Car seats, booster seats, strollers, high chairs, play yards, cribs and bassinets, swings and "
                    "bouncers, baby carriers, safety gates, baby monitors, breast pumps and bottle warmers, and "
                    "electronic toys and games: the makers' instructions at the Internet Archive.",
        kind="manuals", licence=INDEX_LICENCE,
        ia=["car seat", "booster seat", "stroller", "high chair", "highchair", "play yard", "playard", "pack n play",
            "bassinet", "crib", "baby swing", "bouncer", "baby carrier", "safety gate", "baby gate", "baby monitor",
            "breast pump", "bottle warmer", "bottle sterilizer", "baby walker", "activity center", "jumperoo", "playmat",
            "learning toy", "electronic toy", "toy"],
        ia_whole={"manuals_fisherprice": "baby gear or toy (Fisher-Price)", "manuals_Hasbro": "toy or game (Hasbro)"},
        ia_mixed={"manuals_graco": "baby gear (Graco)", "manuals_vtech": "learning toy (VTech)"},
        notice="Install a car seat exactly as its manual and your vehicle's manual say, and check it for recalls "
               "(in the US: nhtsa.gov/recalls). Follow the weight, height and age limits printed on every seat, "
               "crib and carrier."),
    # 2. Home medical and mobility equipment (with the FDA's device records: brand, model, barcode).
    "home_medical": dict(
        name="Home medical and mobility equipment (manuals and device records)",
        description="Wheelchairs and power chairs, mobility scooters, walkers and rollators, canes and crutches, "
                    "hospital beds and bed rails, patient lifts, commodes, shower chairs and bath seats, oxygen "
                    "concentrators, CPAP and BiPAP machines, and stair lifts: manuals at the Internet Archive and "
                    "the FDA's device records of the ones sold over the counter.",
        kind="manuals", licence=FDA_LICENCE,
        ia=["wheelchair", "power chair", "powerchair", "mobility scooter", "walker", "rollator", "quad cane",
            "crutch", "hospital bed", "homecare bed", "bed rail", "patient lift", "hoyer", "commode", "shower chair",
            "bath seat", "transfer bench", "oxygen concentrator", "cpap", "bipap", "apap", "stair lift",
            "stairlift", "lift chair", "alternating pressure"],
        ia_whole={"manuals_invacare": "home medical equipment (Invacare)"},
        ia_mixed={"manuals_medicaldevices": "medical device"},
        udi=['"wheelchair"', '"walker"', '"walking stick"', '"crutch"', '"hospital bed"', '"commode"', '"bath"',
             '"toilet"', '"scooter"', '"lift"', '"oxygen"', '"CPAP"'],
        notice="Medical equipment: follow your prescriber's and supplier's instructions first. Oxygen feeds fire: "
               "no smoking or open flames near it. Check the weight limit of every chair, bed and lift."),
    # 4. Amateur radio, scanners and CB (the Digital Library of Amateur Radio and Communications, outside the
    #    Manual Library).
    "ham_radio": dict(
        name="Amateur radio, scanners and CB (manuals)",
        description="Amateur (ham) radio transceivers and handhelds, receivers and shortwave radios, police and "
                    "weather scanners, CB radios, antenna tuners, amplifiers, power supplies and test equipment: "
                    "the Digital Library of Amateur Radio and Communications (DLARC) and the Manual Library.",
        kind="manuals", licence=INDEX_LICENCE, any_year=True,
        ia=["transceiver", "ham radio", "amateur radio", "scanner radio", "police scanner", "scanning receiver",
            "cb radio", "citizens band", "shortwave", "short wave", "communications receiver", "antenna tuner",
            "swr meter", "linear amplifier", "handheld transceiver", "2 meter", "hf transceiver", "vhf transceiver"],
        ia_whole={"dlarc-manuals": "radio equipment manual (DLARC)",
                  "dlarc-manuals-catalogs": "radio equipment manual (DLARC)",
                  "kenwood-hamradio-library": "Kenwood amateur radio manual",
                  "radioshack-hamradio-library": "Radio Shack radio manual"},
        ia_mixed={"manuals_uniden": "scanner or CB radio (Uniden)", "manuals_cobra": "CB radio (Cobra)",
                  "manuals_midland": "CB or weather radio (Midland)", "manuals_kenwood": "radio (Kenwood)",
                  "manuals_radioshack": "radio (Radio Shack)", "manuals_motorola": "two-way radio (Motorola)"},
        ia_exclude=CATALOGUES),
    # 5. Musical instruments and pro audio.
    "musical_instruments": dict(
        name="Musical instruments and pro audio (manuals)",
        description="Digital pianos and keyboards, synthesizers, drum machines and electronic drums, samplers, "
                    "guitar amplifiers and effects, microphones, mixers, audio interfaces, recorders and studio "
                    "equipment.",
        kind="manuals", licence=INDEX_LICENCE, any_year=True,
        ia=["digital piano", "electronic keyboard", "portable keyboard", "synthesizer", "synth", "drum machine",
            "electronic drum", "sampler", "sequencer", "music workstation", "guitar amplifier", "guitar amp",
            "bass amp", "effects pedal", "effects processor", "multi-effects", "microphone", "audio mixer",
            "mixing console", "dj mixer", "audio interface", "multitrack", "midi", "organ", "arranger",
            "guitar tuner", "metronome"],
        ia_whole={"synthmanuals": "synthesizer or studio equipment manual", "manuals_roland": "Roland",
                  "manuals_korg": "Korg", "manuals_behringer": "Behringer", "manuals_peavey": "Peavey",
                  "manuals_fender": "Fender", "manuals_kawai": "Kawai", "manuals_moog": "Moog",
                  "manuals_tascam": "Tascam", "manuals_m-audio": "M-Audio", "manuals_shure": "Shure"},
        ia_mixed={"manuals_akai": "Akai", "yamaha_bike_manuals": "Yamaha", "manuals_casio": "Casio"}),
    # 9. Video game manuals.
    "video_games": dict(
        name="Video game manuals (console, computer and arcade games)",
        description="The instruction booklets of console, handheld, computer and arcade games: controls, menus, "
                    "rules and how to play, from Atari and Intellivision to PlayStation 2 and Xbox 360.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its publisher", any_year=True,
        ia=["game manual", "instruction booklet"], ia_whole=GAME_COLLECTIONS,
        notice="Game manuals describe controls for sighted players; many older games have no audio cues."),
    # 12. Motorcycles, ATVs, scooters and outboard motors.
    "powersports": dict(
        name="Motorcycles, ATVs, snowmobiles and outboard motors (owner's manuals)",
        description="Owner's manuals of motorcycles, scooters and mopeds, ATVs and side-by-sides, dirt bikes, "
                    "snowmobiles, personal watercraft and outboard motors.",
        kind="manuals", licence=INDEX_LICENCE,
        ia=["motorcycle", "scooter", "moped", "atv", "utv", "dirt bike", "snowmobile",
            "personal watercraft", "jet ski", "waverunner", "wave runner", "outboard", "outboard motor",
            "trolling motor", "sea-doo", "ski-doo"],
        ia_mixed={"yamaha_bike_manuals": "Yamaha", "manuals_kawasaki": "Kawasaki", "manuals_suzuki": "Suzuki",
                  "manuals_honda": "Honda", "manuals_briggsstratton": "engine (Briggs & Stratton)"},
        notice="Wear a helmet and the protective gear the manual lists; never run an engine indoors."),
    # 18. Marine electronics.
    "marine_electronics": dict(
        name="Marine electronics (manuals)",
        description="Fishfinders and sonar, chartplotters, marine VHF radios, radar, autopilots, AIS and marine "
                    "GPS.",
        kind="manuals", licence=INDEX_LICENCE,
        ia=["fishfinder", "fish finder", "sonar", "chartplotter", "chart plotter", "marine radio", "marine vhf",
            "vhf radio", "radar", "autopilot", "ais", "depth sounder", "marine gps"],
        ia_mixed={"manuals_furuno": "Furuno", "manuals_lowrance": "Lowrance", "manuals_garmin": "Garmin",
                  "manuals_cobra": "Cobra", "manuals_uniden": "Uniden", "manuals_midland": "Midland",
                  "manuals_magellan": "Magellan", "manuals_navman": "Navman"},
        notice="Electronic charts and depth readings are aids: keep a proper lookout and know your vessel's "
               "position by more than one means."),
    # 20. Farm tractors and implements.
    "farm_equipment": dict(
        name="Farm tractors and implements (operator's manuals)",
        description="Operator's and instruction manuals of farm tractors, combines, balers, mowers and "
                    "conditioners, planters, cultivators, loaders and wagons, old and new (Case, John Deere, "
                    "International Harvester, New Holland, Allis-Chalmers, Oliver and more).",
        kind="manuals", licence=INDEX_LICENCE, any_year=True,
        ia=["farm tractor", "tractor", "combine", "baler", "hay conditioner", "mower conditioner", "corn planter",
            "harrow", "plow", "plough", "disc harrow", "front end loader", "farm wagon", "grain drill",
            "forage harvester", "manure spreader"],
        ia_whole={"tractormanuals": "tractor manual", "Case_Corporation": "Case farm equipment",
                  "John_Deere_Company": "John Deere farm equipment", "GEHL_Company": "Gehl farm equipment",
                  "The_Holland_Machine_Company": "New Holland or International Harvester farm equipment",
                  "The_Oliver_Company": "Oliver farm equipment",
                  "arthusgerarsallischalmers": "Allis-Chalmers farm equipment",
                  "napierandsonsengineeringmanuals": "Napier farm equipment"},
        ia_mixed={"farmingequipmentmanuals": "farm equipment", "manuals_johndeere": "John Deere"},
        ia_exclude=CATALOGUES + r"|parts? (?:list|book|manual)",
        notice="Keep every shield in place and stop the engine and power take-off before clearing or adjusting "
               "anything. Tractor rollovers kill: use the rollover bar and seat belt."),
    # 22. Camping and outdoor gear.
    "camping_outdoor": dict(
        name="Camping and outdoor gear (manuals)",
        description="Camp stoves, lanterns, coolers, tents, air beds and pumps, heaters, roof racks and cargo "
                    "carriers, and bike racks.",
        kind="manuals", licence=INDEX_LICENCE,
        ia=["camp stove", "camping stove", "lantern", "camp cooler", "ice chest", "tent", "air bed", "airbed",
            "air mattress", "camping", "roof rack", "roof box", "cargo box", "cargo carrier", "bike rack",
            "ski rack"],
        ia_whole={"manuals_coleman": "Coleman", "manuals_thule": "Thule"},
        notice="Use stoves, lanterns and heaters only outdoors or with the ventilation the manual asks for "
               "(carbon monoxide)."),
    # 25. Software manuals.
    "software": dict(
        name="Software manuals (programs and operating systems)",
        description="User's guides and references of computer programs and operating systems: MS-DOS and "
                    "Windows, word processors, spreadsheets and databases, accounting and tax programs, and the "
                    "programs of the 1980s to 2000s.",
        kind="manuals", licence=INDEX_LICENCE, any_year=True,
        ia=["ms-dos", "msdos", "windows", "word processor", "wordperfect", "word for windows", "microsoft word",
            "excel", "lotus 1-2-3", "dbase", "spreadsheet", "database", "quicken", "quickbooks", "turbotax",
            "microsoft office", "software", "operating system", "os/2", "unix"],
        ia_whole={"manuals-ibm-microsoft": "IBM or Microsoft software manual"},
        ia_mixed={"computermanuals": "computer manual"}),
    # 28. Vintage home computers and calculators.
    "vintage_computers": dict(
        name="Vintage home computers (manuals)",
        description="Commodore, Atari, Tandy TRS-80 and Color Computer, Apple II and Macintosh, Texas Instruments, "
                    "Acorn, Amstrad, MSX, Dragon and other home computers of the 1970s to 1990s, with their "
                    "programming and technical manuals.",
        kind="manuals", licence=INDEX_LICENCE, any_year=True,
        ia=["commodore", "vic-20", "amiga", "atari st", "atari 800", "trs-80", "tandy", "apple ii", "apple iie",
            "macintosh", "ti-99", "zx spectrum", "amstrad", "msx", "basic programming"],
        ia_whole=VINTAGE_COMPUTER_COLLECTIONS),
}

# Existing categories given more (their own words and sources kept).
#   36. firearms: the Internet Archive's Weapon and Firearms Manuals as a second source of makers' owner's manuals,
#       under the same exclusions; military manuals only through PUBLIC_MANUALS (Distribution Statement A checked).
#   50. chemical_safety: the Lanco safety data sheets collection.
MILITARY = (r"\b(?:TM|FM|TC|ATP|ADP|ADRP|MCWP|MCRP|NAVSEA|NAVAIR|NAVEDTRA|AFMAN|AFI|AFTO|STP|GTA)\s*[-\d]|\barmy\b|"
            r"\bmilitary\b|\bnavy\b|\bnaval\b|marine corps|air force|department of defen[cs]e|field manual|"
            r"technical manual|ordnance|restricted|confidential|classified|for official use")
EXTEND = {
    "firearms": dict(ia_whole={"firearmsmanuals": "firearm owner's manual"}),
    "chemical_safety": dict(ia_whole={"lanco-safety-data-sheets": "safety data sheet (Lanco)"}),
}

# Every Internet Archive collection the reference inventory of 2026-11-21 found missing (141) or only partly
# covered, and where it now goes: (category, how). how: "whole" (ia_whole), "words" (ia_mixed: searched with the
# category's words), "through synthmanuals" (a sub-collection of a collection searched whole), "through
# consolemanuals" (likewise).
COLLECTION_MAP = {}
for _c in GAME_COLLECTIONS:
    COLLECTION_MAP[_c] = [("video_games", "whole")]
for _c in SYNTH_SUBCOLLECTIONS:
    COLLECTION_MAP[_c] = [("musical_instruments", "through synthmanuals")]
for _c in VINTAGE_COMPUTER_COLLECTIONS:
    COLLECTION_MAP[_c] = [("vintage_computers", "whole")]
for _key, _cat in list(CATEGORIES.items()) + list(EXTEND.items()):
    for _c in _cat.get("ia_whole") or {}:
        COLLECTION_MAP.setdefault(_c, [])
        if (_key, "whole") not in COLLECTION_MAP[_c]:
            COLLECTION_MAP[_c].append((_key, "whole"))
    for _c in _cat.get("ia_mixed") or {}:
        COLLECTION_MAP.setdefault(_c, []).append((_key, "words"))

# The 141 collections the inventory listed as "Missing (relevant)", for the test that each is mapped.
MISSING_IN_INVENTORY = (
    list(k for k in GAME_COLLECTIONS) + SYNTH_SUBCOLLECTIONS +
    ["manuals_Hasbro", "manuals_fisherprice", "manuals_graco", "manuals_vtech", "Case_Corporation", "GEHL_Company",
     "John_Deere_Company", "The_Holland_Machine_Company", "The_Oliver_Company", "arthusgerarsallischalmers",
     "farmingequipmentmanuals", "manuals_johndeere", "napierandsonsengineeringmanuals", "tractormanuals",
     "manuals_kawasaki", "manuals_suzuki", "yamaha_bike_manuals", "manuals_akai", "manuals_behringer",
     "manuals_fender", "manuals_kawai", "manuals_korg", "manuals_m-audio", "manuals_moog", "manuals_peavey",
     "manuals_roland", "manuals_shure", "manuals_tascam", "synthmanuals"])
