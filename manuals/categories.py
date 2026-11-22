"""The manual and instruction collections, by category: what each one is, its licence, and where its products come
from (manuals/build_manuals.py builds them; the Digital Accessibility Toolkit downloads them with its Packages
window, category "Manual collections").

Two kinds:
  instructions  plain-text instructions published IN FULL, because their text is openly licensed: the
                instructions written and checked by the Picture Describers website's volunteers (their licence as
                given, CC BY-SA 4.0). Each record keeps its credit. (Open Food Facts' back-of-pack photos were read
                before; no longer: see off_blocked.)
  manuals       an INDEX only: products (brand, model, name, barcodes, FCC IDs) with the addresses of their manuals
                at official sources whose terms allow automated use (the Internet Archive's documented search
                interface; Wikidata's "user manual URL" property, P2078, which points to makers' own sites; openFDA's
                device identifiers for health devices). The manuals themselves are the makers' copyright and are NOT
                published here: the toolkit fetches each one from its official address for the owner's own use.
                Thumbnails only when their licence allows passing them on (Wikimedia Commons CC0, CC BY, CC BY-SA).

Each category: name, description, kind, licence (of the index), and its sources:
  off_blocked the Open Food Facts databases this collection took products from before 2026-11-21 and no longer
              reads (their websites block AI crawlers, and the open dump has no directions field): the index's
              notes say "not built" and why (build_manuals.OFF_NOT_BUILT)
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
                               "air gun", "air rifle", "air pistol", "BB gun", "gun safe", "bolt-action rifle",
                               "lever-action rifle", "pump-action shotgun", "semi-automatic rifle",
                               "semi-automatic shotgun", "double-barreled shotgun", "single-shot rifle",
                               "telescopic sight", "red dot sight", "holographic weapon sight", "laser sight",
                               "weapon-mounted light", "bipod", "holster", "firearm suppressor", "machine gun",
                               "submachine gun", "light machine gun", "general-purpose machine gun",
                               "heavy machine gun"]}

# ------------------------------------------------------------------------------------------- firearms
# Why this collection exists (the owner's and his team's decision): a blind person living in a household with a
# firearm deserves the same information on handling, storing and maintaining it safely that its maker gives every
# sighted owner, in the maker's own owner's manual. The index holds facts and links only; the toolkit puts a short
# safety note first whenever it offers one of these manuals.
#
# What it covers (owner's decisions of November 2026): civilian firearms (handguns, and rifles and shotguns of every
# common action: bolt, lever, pump, semi-automatic, break-action, single-shot), airguns and BB guns; gun safes, lock
# boxes and gun locks; holsters, magazines, speed loaders, moon clips and magazine loaders; cleaning tools and
# chemicals (for chemicals the maker's SAFETY DATA SHEET is the important document); mounted accessories (scopes,
# red-dot and holographic sights, magnifiers, iron sights, laser sights, weapon lights, slings, bipods, mounts and
# rings); and COMMERCIALLY MADE suppressors (legal and regulated in much of Europe and most US states: the makers'
# owner's manuals for mounting, cleaning and safe use).
#
# Legal but regulated items (the owner's and his team's policy of November 2026: "identify what it is, mention that
# it may not be legal, and link to the manual; it is not our place to gatekeep information"): the toolkit identifies
# them with a plain legal note and offers the MAKER'S OWN published instructions, under the same robots.txt and
# terms rules as every maker. They are: unfinished frames and receivers ("80 percent" lowers and frames), their jigs
# and weapon parts kits; magazine extensions and capacity kits; bump stocks; forced-reset and binary triggers;
# solvent traps sold as cleaning accessories; short-barrelled rifles and shotguns and other NFA firearms; and
# AUTOMATIC firearms (machine guns, submachine guns, select-fire rifles), with their makers' manuals where openly
# published and US military manuals ONLY when publicly released (Distribution Statement A printed on the document
# itself, checked again at every build: PUBLIC_MANUALS).
#
# Never in this collection (FIREARMS_EXCLUDE, checked on every product and document name and kind): anything for
# MAKING a suppressor (suppressor or baffle kits and parts, pre-drilled or indexed cups and cones, fuel or oil filter
# adapters, Form 1 build kits); automatic-fire CONVERSION parts, which civilians cannot legally own in the US unless
# registered before 1986 and which have no civilian manuals (auto sears, drop-in auto sears, "lightning links",
# "switches", conversion kits); destructive devices and grenades; reloading equipment; armorer's (gunsmith) manuals;
# nor sales papers (catalogues, warranty and order forms, spec sheets, flyers).
FIREARMS_EXCLUDE = (r"(?:suppressor|silencer|baffle|wipe|monocore)s?\s+(?:build\s+)?(?:kit|parts?|tubes?|cups?|cones?|"
                    r"stacks?|blanks?)\b|baffle\s+(?:kit|cone|cup|stack)|"
                    r"(?<!un)(?:pre-?)?drilled\b.{0,30}?(?:cups?|cones?)|indexed\b.{0,30}?(?:cups?|cones?)|"
                    r"fuel[- ]filter|oil[- ]filter\s+(?:adapt|kit)|form\s*1\b|"
                    r"destructive device|conver(?:sion|t)|auto[- ]?sear|lightning[- ]link|swift[- ]link|"
                    r"(?:glock|auto|selector)\s+switch|grenade|anti[- ]materi[ae]l|reload|powder measure|bullet mold|"
                    r"armou?rer")
NOT_A_MANUAL = (r"warranty|buyer'?s? ?guide|annual|catalog|patent|order form|inspection form|awareness form|"
                r"price ?list|rebate|code of conduct|spec ?sheet|fact ?sheet|press release|dealer|flyer|brochure|"
                r"sell ?sheet|sales|product codes")

# The makers. access:
#   read     robots.txt allows programs and the terms (read on 2026-11-19) do not forbid them: the builder reads the
#            pages listed (only those) and keeps the manual links on them that point to the maker's own files
#            (hosts); "page_links": links to the maker's manuals published as web pages (Browning, Winchester).
#   link     the terms forbid robots, scraping or indexing, or the site refuses programs: nothing is read; the
#            library's address (entered by hand) is listed for the person to open in their browser.
#   mention  the terms forbid even linking without permission: the site is named in words only, no address.
# type: what the maker's products are when a document does not say: "pistol", "rifle", "shotgun", "firearm",
#   "airgun", "safe", "lock", "holster", "magazine", "loader", "cleaning" (tools and kits), "chemical" (solvents,
#   bore cleaners, oils and lubricants: their safety data sheets), "optic" (scopes and sights), "laser", "light",
#   "mount" (slings, bipods, rails and rings), "suppressor" (commercially made), "frame" (unfinished frames and
#   receivers, their jigs and parts kits), "trigger" (binary and forced-reset triggers), "stock" (bump stocks) or
#   "automatic" (automatic firearms).
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
    # Long guns (read on 2026-11-19).
    dict(key="weatherby", maker="Weatherby", type="rifle", access="read",
         library="https://weatherby.com/support/owners-manuals/",
         pages=["https://weatherby.com/support/owners-manuals/"], hosts=["weatherby.com"],
         reason="robots.txt allows the page; no terms page found (only a privacy policy)"),
    dict(key="bergara", maker="Bergara", type="rifle", access="read",
         library="https://www.bergara.online/us/support/user-manuals/",
         pages=["https://www.bergara.online/us/support/user-manuals/"], hosts=["www.bergara.online"],
         reason="robots.txt allows all; its terms of use have no rule against programs"),
    dict(key="franchi", maker="Franchi", type="shotgun", access="link",
         library="https://www.franchiusa.com/resources/manuals",
         reason="robots.txt allows, but its terms (on shopfranchi.com) refuse programs (HTTP 403), so they could "
                "not be read"),
    dict(key="stoeger", maker="Stoeger", type="shotgun", access="link", library="https://stoegerindustries.com/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="tikka", maker="Tikka (Sako)", type="rifle", access="link",
         library="https://www.sako.global/tikka/support",
         reason="its support pages are built by scripts in the browser; not read"),
    dict(key="ithaca", maker="Ithaca", type="shotgun", access="link", library="https://ithacagun.com/",
         reason="robots.txt allows and its legal notice has no rule against programs, but the site often resets "
                "the build machine's connections; its Model 37 manual is linked from its home page"),
    dict(key="rossi", maker="Rossi", type="firearm", access="link", library="https://www.rossiusa.com/",
         reason="the site could not be reached from the build machine (HTTP/2 error)"),
    # More safes and gun locks.
    dict(key="gunvault", maker="GunVault", type="safe", access="link",
         library="https://gunvault.com/support/product-manuals/",
         reason="terms forbid automated systems (bots, scraping tools)"),
    dict(key="fortress", maker="Fortress", type="safe", access="link",
         library="https://www.fortresssafe.com/user-manual.html",
         reason="the site resets the build machine's connections; not read"),
    dict(key="hornady-security", maker="Hornady Security", type="safe", access="link",
         library="https://www.hornady.com/support/user-manuals",
         reason="robots.txt allows and the terms have no rule against programs, but the manual list is built by "
                "scripts in the browser; not read"),
    dict(key="master-lock", maker="Master Lock", type="lock", access="link", library="https://www.masterlock.com/",
         reason="the company of SentrySafe: linked only, as SentrySafe is"),
    # Holsters, magazines and loaders.
    dict(key="safariland", maker="Safariland", type="holster", access="link", library="https://safariland.com/",
         reason="terms forbid robots and data mining, and allow links to the home page only"),
    dict(key="galco", maker="Galco", type="holster", access="link", library="https://www.galco.com/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="magpul", maker="Magpul", type="magazine", access="link", library="https://magpul.com/",
         reason="no manual library found (instructions are on product pages); not read"),
    dict(key="maglula", maker="maglula (UpLULA)", type="loader", access="link", library="https://www.maglula.com/",
         reason="no manual library found; not read"),
    dict(key="hks", maker="HKS", type="loader", access="link", library="https://www.hksspeedloaders.com/",
         reason="no manual library found; not read"),
    # Cleaning tools and chemicals: for chemicals, the maker's safety data sheets (SDS).
    dict(key="hoppes", maker="Hoppe's", type="chemical", access="link",
         library="https://www.primos.com/pages/hoppes-sds",
         reason="Hoppe's (with M-Pro 7 and Gunslick) publishes its safety data sheets on primos.com; robots.txt "
                "allows the page, but the terms the site links (Revelyst) forbid data mining and robots"),
    dict(key="m-pro-7", maker="M-Pro 7", type="chemical", access="link",
         library="https://www.primos.com/pages/hoppes-sds",
         reason="its safety data sheets are on the Hoppe's SDS page (primos.com), whose terms forbid robots"),
    dict(key="otis", maker="Otis Technology", type="cleaning", access="link", library="https://otistec.com/",
         reason="robots.txt allows its SDS page, but its terms forbid deep links for any commercial purpose "
                "without permission (the toolkit is sold): only its home page is linked; the safety data sheets "
                "are under Product information, SDS"),
    dict(key="break-free", maker="Break-Free (Safariland)", type="chemical", access="link",
         library="https://safariland.com/",
         reason="breakfree.com could not be reached (HTTP 530); Safariland's terms forbid robots and allow links "
                "to the home page only"),
    dict(key="ballistol", maker="Ballistol", type="chemical", access="link", library="https://ballistol.com/",
         reason="terms forbid spidering, crawling and scraping; no safety data sheet page found on the site"),
    dict(key="real-avid", maker="Real Avid", type="cleaning", access="link", library="https://realavid.com/",
         reason="terms forbid spidering, crawling and scraping; no manual or SDS page found on the site"),
    dict(key="lucas", maker="Lucas Oil", type="chemical", access="link", library="https://www.lucasoil.com/sds/",
         reason="terms forbid bots, spiders and indexing agents (linking is allowed)"),
    dict(key="birchwood-casey", maker="Birchwood Casey", type="chemical", access="link",
         library="https://www.birchwoodcasey.com/", reason="the site refuses programs (Incapsula)"),
    dict(key="rem-oil", maker="Rem Oil (Remington gun care)", type="chemical", access="link",
         library="https://www.remington.com/",
         reason="terms (The Kinetic Group) forbid data mining and robots; no SDS page found on the site"),
    # Mounted accessories: optics, lasers, lights, slings, bipods and mounts.
    dict(key="burris", maker="Burris", type="optic", access="read",
         library="https://www.burrisoptics.com/support/user-manuals",
         pages=["https://www.burrisoptics.com/support/user-manuals"], hosts=["www.burrisoptics.com"],
         reason="robots.txt allows the page; its terms of use have no rule against programs"),
    dict(key="eotech", maker="EOTECH", type="optic", access="read",
         library="https://www.eotechinc.com/pages/help-center-product-manuals",
         pages=["https://www.eotechinc.com/pages/help-center-product-manuals"],
         hosts=["cdn.shopify.com", "www.eotechinc.com"],
         reason="robots.txt allows the page; its terms of service have no rule against programs"),
    dict(key="vortex", maker="Vortex Optics", type="optic", access="link", library="https://vortexoptics.com/",
         reason="no manual library page found to read (its manuals are on product pages); not read"),
    dict(key="leupold", maker="Leupold", type="optic", access="link", library="https://www.leupold.com/support",
         reason="its manuals are not on a page programs can read (scripts); not read"),
    dict(key="trijicon", maker="Trijicon", type="optic", access="link", library="https://www.trijicon.com/support",
         reason="its manuals are not on a page programs can read (scripts); not read"),
    dict(key="aimpoint", maker="Aimpoint", type="optic", access="link", library="https://www.aimpoint.us/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="holosun", maker="Holosun", type="optic", access="link", library="https://www.holosun.com/",
         reason="no manual library page found to read; not read"),
    dict(key="bushnell", maker="Bushnell", type="optic", access="link", library="https://www.bushnell.com/",
         reason="terms (Revelyst) forbid data mining and robots"),
    dict(key="nikon", maker="Nikon (sport optics, legacy)", type="optic", access="link",
         library="https://downloadcenter.nikonimglib.com/en/index.html",
         reason="Nikon's terms reserve the right to block automated systems, bots and crawlers; not read"),
    dict(key="primary-arms", maker="Primary Arms", type="optic", access="link", library="https://www.primaryarms.com/",
         reason="no manual library page found to read; not read"),
    dict(key="surefire", maker="SureFire", type="light", access="link", library="https://www.surefire.com/",
         reason="no manual library page found to read; not read (SureFire also makes suppressors)"),
    dict(key="streamlight", maker="Streamlight", type="light", access="link",
         library="https://www.streamlight.com/support",
         reason="its manuals are not on a page programs can read (scripts); not read"),
    dict(key="crimson-trace", maker="Crimson Trace", type="laser", access="link",
         library="https://www.crimsontrace.com/", reason="terms (American Outdoor Brands) forbid data mining"),
    dict(key="viridian", maker="Viridian", type="laser", access="link", library="https://viridian.tech/product-manuals",
         reason="terms forbid robots, spiders and indexing (only search engines)"),
    dict(key="harris", maker="Harris Bipods", type="mount", access="link", library="https://www.harrisbipods.com/",
         reason="the site resets the build machine's connections; not read"),
    # Commercially made suppressors (owner's decision of November 2026: legal and regulated in much of Europe and
    # most US states; the makers' owner's manuals for mounting, cleaning and safe use).
    dict(key="dead-air", maker="Dead Air", type="suppressor", access="read",
         library="https://deadairsilencers.com/owners-manuals/",
         pages=["https://deadairsilencers.com/owners-manuals/"], hosts=["deadairsilencers.com"],
         reason="robots.txt allows the page; no terms page found (only a privacy policy)"),
    dict(key="huxwrx", maker="HUXWRX", type="suppressor", access="read", library="https://huxwrx.com/manuals",
         pages=["https://huxwrx.com/manuals"], hosts=["huxwrx.com"],
         reason="robots.txt allows the page; its terms have no rule against programs"),
    dict(key="silencerco", maker="SilencerCo", type="suppressor", access="link", library="https://silencerco.com/",
         reason="the site refuses programs (HTTP 403)"),
    dict(key="rugged", maker="Rugged Suppressors", type="suppressor", access="link",
         library="https://www.ruggedsuppressors.com/", reason="terms forbid spidering, crawling and scraping"),
    dict(key="thunder-beast", maker="Thunder Beast Arms", type="suppressor", access="link",
         library="https://www.thunderbeastarms.com/",
         reason="its certificate could not be checked from the build machine; not read"),
    dict(key="banish", maker="Banish (Silencer Central)", type="suppressor", access="link",
         library="https://www.banishsuppressors.com/customer-care/product-manuals/",
         reason="terms forbid automated tools that extract content beyond what the terms allow"),
    dict(key="q", maker="Q", type="suppressor", access="link", library="https://thebigq.com/",
         reason="no manual library page found; not read"),
    dict(key="griffin", maker="Griffin Armament", type="suppressor", access="link",
         library="https://griffinarmament.com/manuals/",
         reason="its manual and terms pages refuse programs (HTTP 403)"),
    dict(key="ase-utra", maker="Ase Utra", type="suppressor", access="link",
         library="https://www.aseutra.fi/product-support/",
         reason="no terms page found; its support page holds product leaflets, not read"),
    dict(key="jaki", maker="Jaki", type="suppressor", access="link", library="https://jaki.fi/",
         reason="no manual library page found; not read"),
    dict(key="hausken", maker="Hausken", type="suppressor", access="link",
         library="https://www.hausken-silencers.com/en/downloads",
         reason="its downloads page holds flyers and sales sheets, not manuals; not read"),
    dict(key="a-tec", maker="A-TEC", type="suppressor", access="link",
         library="https://www.a-tec.no/maintenance-and-instructions",
         reason="no terms page found; its instructions are not files a program can list; not read"),
    # Legal but regulated items (the owner's policy of November 2026; read on 2026-11-19). Unfinished frames and
    # receivers ("80 percent" lowers and frames), their jigs and weapon parts kits: the makers' own instructions.
    # Polymer80 is not listed: the company closed and its site is a parked page. JSD Supply is not listed: its
    # site's certificate does not match its name, so it could not be checked.
    dict(key="80-percent-arms", maker="80% Arms", type="frame", access="read",
         library="https://www.80percentarms.com/instructions-and-faq/",
         pages=["https://www.80percentarms.com/instructions-and-faq/"], hosts=["www.80percentarms.com"],
         reason="robots.txt allows the page (it disallows some older manual files, which are left out); no terms "
                "page found"),
    dict(key="5d-tactical", maker="5D Tactical", type="frame", access="read",
         library="https://www.5dtactical.com/Instructions/", pages=["https://www.5dtactical.com/Instructions/"],
         hosts=["www.5dtactical.com"],
         reason="robots.txt allows the page; its terms have no rule against programs (they allow copies for your "
                "own non-commercial use)"),
    dict(key="juggernaut", maker="Juggernaut Tactical", type="frame", access="read",
         library="https://jtactical.com/products/80-lower-jig-ar10-ar15-ultimate",
         pages=["https://jtactical.com/products/80-lower-jig-ar10-ar15-ultimate"], hosts=["jtactical.com"],
         reason="robots.txt allows the page; its terms are terms of sale, with no rule against programs"),
    dict(key="modulus", maker="Modulus Arms", type="frame", access="link",
         library="https://www.modulusarms.com/instructions",
         reason="terms forbid spidering, crawling and scraping"),
    dict(key="lone-wolf", maker="Lone Wolf", type="frame", access="link", library="https://lonewolfdist.com/",
         reason="terms forbid robots and allow links to the home page only"),
    # Binary and forced-reset triggers, bump stocks.
    dict(key="franklin", maker="Franklin Armory", type="firearm", access="read",
         library="https://franklinarmory.com/manuals-install-videos/",
         pages=["https://franklinarmory.com/manuals-install-videos/"], hosts=["franklinarmory.com"],
         reason="robots.txt allows the page; its terms have no rule against programs and allow downloading for "
                "personal, non-commercial use (as GLOCK's do)"),
    dict(key="fostech", maker="Fostech", type="trigger", access="read", library="https://fostech.com/manuals-patents/",
         pages=["https://fostech.com/manuals-patents/"], hosts=["fostech.com"],
         reason="robots.txt allows the page; its terms forbid robots only for entering its sweepstakes"),
    dict(key="rare-breed", maker="Rare Breed Triggers", type="trigger", access="link",
         library="https://rarebreedtriggers.com/installation-videos/",
         reason="terms forbid spidering, crawling and scraping"),
    dict(key="slide-fire", maker="Slide Fire", type="stock", access="link", library="https://bumpstock.com/shop",
         reason="robots.txt allows and its terms have no rule against programs, but its installation instructions "
                "are pictures on each product page, not files a program can list; not read"),
    # Magazine extensions and capacity kits.
    dict(key="pearce", maker="Pearce Grip", type="magazine", access="link", library="https://www.pearcegrip.com/",
         reason="terms forbid spidering, crawling and scraping"),
    dict(key="shield-arms", maker="Shield Arms", type="magazine", access="link", library="https://shieldarms.com/",
         reason="the site refuses programs (a browser check)"),
]

# Automatic firearms: US military manuals, ONLY when publicly released (the owner's decision of November 2026). Each
# is the Internet Archive's copy (armypubs.army.mil's robots.txt shuts out programs) and is put in the index only
# when the front of its text says "Approved for public release; distribution is unlimited" (Distribution Statement
# A) and shows no restricted marking (Distribution B to F, FOUO, CUI ...): build_manuals.public_manual_entries
# checks it at every build. Checked by hand on 2026-11-19: all three print Distribution Statement A.
PUBLIC_MANUALS = [
    dict(ia="tc-3-22.249-light-machine-gun-m-249-series-2017", brand="US Army", model="M249",
         name="TC 3-22.249, Light Machine Gun M249 Series (2017)"),
    dict(ia="medium-machine-gun-tc-3-22.240", brand="US Army", model="M240",
         name="TC 3-22.240, Medium Machine Gun M240 Series (2017)"),
    dict(ia="heavy-machine-gun-m-2-series-tc-3-22.50", brand="US Army", model="M2",
         name="TC 3-22.50, Heavy Machine Gun M2 Series (2017)"),
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
        kind="instructions", licence="CC BY-SA 4.0 (Picture Describers volunteers)",
        off_blocked=("Open Food Facts",),
        volunteers=("cooking",)),
    "product_directions": dict(
        name="Product directions (beauty, cleaning and household)",
        description="Directions for use and warnings printed on beauty, cleaning and household products, as plain "
                    "text, found by barcode or photo.",
        kind="instructions", licence="CC BY-SA 4.0 (Picture Describers volunteers)",
        off_blocked=("Open Beauty Facts", "Open Products Facts"),
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
                    "shotguns, airguns and BB guns; gun safes and locks; holsters, magazines and loaders; cleaning "
                    "tools and the safety data sheets of cleaning chemicals; scopes, sights, lasers, lights and "
                    "mounts; commercially made suppressors; and legal but regulated items (unfinished frames and "
                    "receivers with their jigs and kits, magazine extensions, bump stocks, binary and forced-reset "
                    "triggers, solvent traps, NFA firearms and automatic firearms, with publicly released military "
                    "manuals for the last): how to handle, store, clean and maintain them safely, as the maker "
                    "tells every owner. The toolkit says a plain legal note with each regulated item. Links only, "
                    "fetched from the maker.",
        kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
        makers=MAKERS, wikidata=True, exclude=FIREARMS_EXCLUDE, guidance=FIREARMS_GUIDANCE,
        public_manuals=PUBLIC_MANUALS),
}

# Vaporizers, pipes and smoking accessories: its makers, their access decisions and exclusions are in
# manuals/smoking_vaping.py (kept apart from the firearms lists above).
from smoking_vaping import CATEGORY as _SMOKING_VAPING  # noqa: E402

CATEGORIES["smoking_vaping"] = _SMOKING_VAPING

# Pet and livestock supplies: its makers, their access decisions and exclusions are in
# manuals/pet_livestock_supplies.py (pet- and livestock-specific; household pest control is not in it).
from pet_livestock_supplies import CATEGORY as _PET_LIVESTOCK  # noqa: E402

CATEGORIES["pet_livestock_supplies"] = _PET_LIVESTOCK

# Home health tests (instructions for use; the owner's request of 2026-11-22): makers (link-only), the FDA's device
# records and guidance are in manuals/home_health_tests.py.
from home_health_tests import CATEGORY as _HOME_TESTS  # noqa: E402

CATEGORIES["home_health_tests"] = _HOME_TESTS

# Hardware, tools and shop equipment: their makers, access decisions, safety notices and public-domain guides are in
# manuals/hardware_tools.py. Its new categories are added, and power_tools, hand_tools and lawn_garden are extended
# (more Internet Archive words, the makers' libraries, a safety notice and the guides).
from hardware_tools import CATEGORIES as _HARDWARE_TOOLS, EXTEND as _HARDWARE_EXTEND  # noqa: E402

CATEGORIES.update(_HARDWARE_TOOLS)
for _key, _more in _HARDWARE_EXTEND.items():
    _cat = CATEGORIES[_key]
    _cat["ia"] = list(_cat.get("ia", [])) + [w for w in _more.get("ia", []) if w not in _cat.get("ia", [])]
    for _field in ("makers", "public_guides", "guidance"):
        if _more.get(_field):
            _cat[_field] = list(_cat.get(_field) or []) + list(_more[_field])
    if _more.get("notice"):
        _cat["notice"] = _more["notice"]

# The household and garage chemical collections (cleaners, pool, garden, paints, oils, wood finishes, automotive
# fluids, glues, solvents, pest control, batteries, fuels, extinguishers and more, the official pesticide labels and
# the chemical safety guides): their makers, sources and guidance are in manuals/chemicals.py.
from chemicals import CHEMICAL_CATEGORIES as _CHEMICALS  # noqa: E402

CATEGORIES.update(_CHEMICALS)

# More collections from the reference inventory of 2026-11-21 (baby gear and toys, home medical and mobility
# equipment, amateur radio, musical instruments, video games, motorcycles and outboards, marine electronics, farm
# tractors, camping gear, software, vintage computers) and the Internet Archive collections no category reached:
# manuals/more_categories.py. The firearms category also lists the Internet Archive's firearms collection, without
# anything FIREARMS_EXCLUDE forbids, sales papers, or any military manual (those come only through PUBLIC_MANUALS).
from more_categories import CATEGORIES as _MORE, EXTEND as _MORE_EXTEND, MILITARY as _MILITARY  # noqa: E402

CATEGORIES.update(_MORE)
for _key, _more in _MORE_EXTEND.items():
    _cat = CATEGORIES[_key]
    _cat["ia_whole"] = dict(_cat.get("ia_whole") or {}, **_more.get("ia_whole", {}))
CATEGORIES["firearms"]["ia_exclude"] = f"{FIREARMS_EXCLUDE}|{NOT_A_MANUAL}|{_MILITARY}"

# Appliance error codes and troubleshooting (the Internet Archive's service manuals, the makers' error-code pages as
# links, iFixit's pages as links, US government guides) and firmware and software release notes ("full" where openly
# licensed, else links): manuals/troubleshooting.py.
from troubleshooting import CATEGORIES as _TROUBLESHOOTING  # noqa: E402

CATEGORIES.update(_TROUBLESHOOTING)
