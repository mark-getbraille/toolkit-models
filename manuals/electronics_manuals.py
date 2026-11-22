"""Electronics repair and assistive-technology care in the manual library (the owner's request of 2026-11-22).
categories.py adds these three collections; build_manuals.py builds them. An INDEX of facts and links only: every
manual belongs to its maker or author, and the toolkit fetches it from its own address for the owner's own use.

  electronics_service      service manuals, schematics and repair manuals of televisions, radios, stereos,
                           amplifiers, turntables, tape decks, VCRs, camcorders, CD and DVD players, computers,
                           laptops and game consoles: ONE Internet Archive search of the Manual Library ("ia_any": a
                           title with a kind of device AND a kind of service paper, as appliance_troubleshooting does),
                           the copies of manual-copying sites left out as everywhere; iFixit's device pages for phones,
                           tablets, laptops, desktops, consoles, TVs and audio gear, LINK ONLY (troubleshooting.
                           IFIXIT_REASON); and the US Navy's NEETS modules on test equipment and test methods as public
                           guides.
  electronics_test_equipment  multimeters, oscilloscopes, signal generators, bench power supplies and soldering
                           stations: the makers' own libraries, LINK ONLY in this first version (their terms were not
                           checked one by one, so nothing is read; each library is listed for the person to open), the
                           Internet Archive's manuals of test equipment, and OSHA's guide to electrical hazards.
  assistive_tech_repair    care, troubleshooting and repair of assistive devices: video magnifiers, electronic
                           magnifiers, braille displays and notetakers, braille embossers, talking devices, DAISY and
                           NLS players, reading machines and travel aids. The makers' manuals (HumanWare, Freedom
                           Scientific and Vispero, Optelec, Eschenbach, Zeiss, Enhanced Vision, Orbit Research, APH,
                           Index Braille, ViewPlus, HIMS, Zoomax, Shinano Kenshi/Plextalk) are LINK ONLY: their
                           copyright; the owner fetches them himself with Program Downloader. NLS's own player guides
                           and service manual, the VA Blind Rehabilitation Service's and ACL's Assistive Technology Act
                           pages are US government works ("full": they may be downloaded where robots.txt allows); the
                           FCC's deaf-blind equipment programme is linked (fcc.gov refuses programs). The Internet
                           Archive's manuals of these devices are in the collection "accessibility" already (its words:
                           talking, braille, magnifier, daisy player ...), so they are not searched again here.

Each collection's safety notice ("notice") is said first by the toolkit.
"""

from troubleshooting import IFIXIT_RIGHTS, IFIXIT_REASON

INDEX_LICENCE = "CC0 (facts and links); each manual and page belongs to its maker or author"
US_GOV = "a US government work (public domain)"

MAINS_NOTICE = ("Unplug the device before opening it. Televisions, picture tubes, valve sets, microwave ovens and "
                "power supplies hold dangerous voltages long after unplugging: their insides are work for a trained "
                "technician. Never charge or open a swollen lithium battery; take it to a battery recycling drop-off.")
TEST_NOTICE = ("Read the safety section first. Use a meter rated for the job (its CAT rating), check it on a known live "
               "circuit, keep fingers behind the probe guards, and never measure mains if you are unsure: a licensed "
               "electrician can. A soldering iron's tip burns at a touch: keep it in its stand, and work with "
               "ventilation.")
DEVICE_NOTICE = ("Check the warranty, loan agreement or repair programme before opening an assistive device: NLS "
                 "players are repaired or replaced free through your network library (1-888-657-7323); veterans can "
                 "ask their VIST coordinator; state Assistive Technology Act programmes lend, reuse and help repair "
                 "devices. Use only the maker's battery and charger, never charge a swollen battery, and clean "
                 "screens, lenses and braille cells only as the maker's guide says.")

# ------------------------------------------------------------------------------- electronics_service

SERVICE_KINDS = [
    (r"televisions?|\btv\b|crt", "television"), (r"radios?|receivers?|tuners?", "radio or receiver"),
    (r"amplifiers?|\bamp\b|stereo|hi-?fi", "amplifier or stereo"), (r"turntables?|record players?", "turntable"),
    (r"cassette|tape decks?|reel", "tape deck"), (r"\bvcr\b|video ?cassette|camcorders?", "VCR or camcorder"),
    (r"\bcd\b|\bdvd\b|blu-?ray|compact disc", "disc player"), (r"laptops?|notebooks?", "laptop"),
    (r"computers?|\bpc\b|desktops?|monitors?", "computer"), (r"consoles?|playstation|xbox|nintendo|sega", "game "
                                                                                                           "console"),
]
_SERVICE_DEVICES = ["television", "tv", "radio", "receiver", "tuner", "amplifier", "stereo", "turntable",
                    "cassette deck", "tape deck", "reel to reel", "vcr", "camcorder", "cd player", "dvd player",
                    "laptop", "notebook computer", "computer", "monitor", "game console", "playstation", "xbox",
                    "nintendo"]
_SERVICE_PAPERS = ["service manual", "service guide", "repair manual", "schematic", "schematics",
                   "technical manual", "troubleshooting", "service data", "circuit diagram", "alignment"]
SERVICE_IA = {"kinds": _SERVICE_DEVICES, "documents": _SERVICE_PAPERS}
# Sales papers and parts lists are not service manuals; nor are car radios' vehicle manuals or ham transceivers
# (ham_radio's collection).
SERVICE_EXCLUDE = (r"catalog(?:ue)?s?\b|price ?list|brochure|flyer|parts? (?:list|catalog|book)|owner'?s manual|"
                   r"transceiver|ham radio|amateur radio")


def _ifixit(kind, page):
    """The hand-entered record of one iFixit device page (link only, personal use)."""
    return dict(key=f"ifixit-{page.lower()}", by="iFixit (community repair wiki)", product=kind,
                title=f"iFixit: {kind} repair guides (community pages)", url=f"https://www.ifixit.com/Device/{page}",
                type=kind, document="repair guides", access="link", rights=IFIXIT_RIGHTS, reason=IFIXIT_REASON)


SERVICE_DOCUMENTS = [
    _ifixit("phone", "Phone"), _ifixit("iPhone", "iPhone"), _ifixit("Android phone", "Android_Phone"),
    _ifixit("tablet", "Tablet"), _ifixit("iPad", "iPad"), _ifixit("laptop", "PC_Laptop"),
    _ifixit("MacBook", "Mac_Laptop"), _ifixit("desktop computer", "PC_Desktop"),
    _ifixit("game console", "Game_Console"), _ifixit("television", "Television"),
    _ifixit("headphones", "Headphone"), _ifixit("speaker", "Speaker"), _ifixit("audio amplifier", "Amplifier"),
    _ifixit("electronics (all devices)", "Electronics"),
]


def _guide(ia, title, by, year, military=False):
    """One public-domain guide: an Internet Archive item, its title, who wrote it, its year, and whether it is a
    military training manual (whose front text must say it is approved for public release)."""
    return dict(ia=ia, title=title, by=by, year=year, military=military)


NAVY = "the US Navy"
GUIDES = {
    "neets_16": _guide("NEETSModule16", "NEETS Module 16: Introduction to Test Equipment", NAVY, 1998, True),
    "neets_21": _guide("NEETSModule21", "NEETS Module 21: Test Methods and Practices", NAVY, 1998, True),
    "neets_19": _guide("NEETSModule19", "NEETS Module 19: The Technician's Handbook", NAVY, 1998, True),
    "electrical_hazards": _guide("DTIC_ADA400134", "Controlling Electrical Hazards (OSHA 3075, 1997)",
                                 "the US Occupational Safety and Health Administration", 1997),
}

# ------------------------------------------------------------------------------- electronics_test_equipment

LINK_REASON = ("listed for the person to open in a browser; nothing is read from its site in this first version "
               "(its terms were not checked one by one)")
_TEST_COMMON = dict(prefix="et", types=[], documents="manuals", category="electronics_test_equipment")
TEST_MAKERS = [dict(_TEST_COMMON, access="link", reason=LINK_REASON, **m) for m in [
    dict(key="fluke", maker="Fluke", type="multimeter and test tool", library="https://www.fluke.com/en-us/support"),
    dict(key="tektronix", maker="Tektronix", type="oscilloscope", library="https://www.tek.com/en/support"),
    dict(key="keysight", maker="Keysight", type="test equipment", library="https://www.keysight.com/us/en/support.html"),
    dict(key="rigol", maker="RIGOL", type="oscilloscope and signal generator",
         library="https://www.rigolna.com/download/"),
    dict(key="siglent", maker="SIGLENT", type="oscilloscope and signal generator",
         library="https://siglentna.com/resources/"),
    dict(key="owon", maker="OWON", type="oscilloscope and multimeter", library="https://www.owon.com.hk/"),
    dict(key="hakko", maker="HAKKO", type="soldering station", library="https://www.hakkousa.com/"),
    dict(key="weller", maker="Weller", type="soldering station", library="https://www.weller-tools.com/"),
    dict(key="pine64-pinecil", maker="PINE64 (Pinecil soldering iron)", type="soldering iron",
         library="https://wiki.pine64.org/wiki/Pinecil"),
    dict(key="uni-t", maker="UNI-T", type="multimeter", library="https://meters.uni-trend.com/"),
    dict(key="extech", maker="Extech (Teledyne FLIR)", type="multimeter and meter",
         library="https://www.extech.com/"),
    dict(key="bk-precision", maker="B&K Precision", type="bench power supply and test equipment",
         library="https://www.bkprecision.com/support"),
]]
TEST_IA = ["oscilloscope", "signal generator", "function generator", "logic analyzer", "frequency counter",
           "bench power supply", "soldering station", "rework station", "lcr meter", "tube tester", "capacitance meter"]

# ------------------------------------------------------------------------------- assistive_tech_repair

AT_REASON = ("the maker's manuals and support pages are its copyright: nothing is read; its support page is listed "
             "for the owner to open, or to fetch for his own use with Program Downloader")
_AT_COMMON = dict(prefix="at", types=[], documents="manuals and support pages", category="assistive_tech_repair")
AT_MAKERS = [dict(_AT_COMMON, access="link", reason=AT_REASON, **m) for m in [
    dict(key="humanware", maker="HumanWare (Brailliant, BrailleNote, Victor Reader, explore magnifiers)",
         type="braille display, notetaker, DAISY player and magnifier", library="https://support.humanware.com/"),
    dict(key="vispero", maker="Freedom Scientific and Vispero (Focus braille displays, Topaz and ONYX video "
                              "magnifiers, RUBY handheld magnifiers, Optelec)",
         type="braille display and video magnifier", library="https://support.freedomscientific.com/"),
    dict(key="eschenbach", maker="Eschenbach Optik (electronic magnifiers)", type="electronic magnifier",
         library="https://www.eschenbach.com/"),
    dict(key="zeiss-low-vision", maker="ZEISS (low-vision and electronic magnifiers, binoculars and monoculars)",
         type="magnifier, binocular and monocular", library="https://www.zeiss.com/consumer-products/us/service.html"),
    dict(key="enhanced-vision", maker="Enhanced Vision (Merlin, Acrobat, DaVinci video magnifiers)",
         type="video magnifier", library="https://www.enhancedvision.com/support"),
    dict(key="orbit-research", maker="Orbit Research (Orbit Reader, Graphiti)", type="braille display",
         library="https://www.orbitresearch.com/support/"),
    dict(key="aph", maker="American Printing House for the Blind (Mantis, Chameleon, talking devices)",
         type="braille display and talking device", library="https://www.aph.org/support/"),
    dict(key="index-braille", maker="Index Braille", type="braille embosser",
         library="https://www.indexbraille.com/en-us/support"),
    dict(key="viewplus", maker="ViewPlus", type="braille embosser", library="https://viewplus.com/support/"),
    dict(key="hims", maker="HIMS (BrailleSense, QBraille)", type="braille notetaker and display",
         library="https://hims-inc.com/support/"),
    dict(key="zoomax", maker="Zoomax", type="video magnifier", library="https://www.zoomax.com/"),
    dict(key="plextalk", maker="Shinano Kenshi (PLEXTALK DAISY players)", type="DAISY player",
         library="https://www.plextalk.com/"),
    dict(key="envision", maker="Envision (Envision Glasses and app)", type="OCR reading device",
         library="https://www.letsenvision.com/support"),
    dict(key="sunu", maker="Sunu (Sunu Band travel aid)", type="electronic travel aid", library="https://sunu.com/"),
    dict(key="wewalk", maker="WeWALK (smart cane)", type="smart cane", library="https://wewalk.io/"),
]]

NLS_EQUIPMENT = "https://www.loc.gov/nls/services-and-resources/equipment-for-nls-materials/"
NLS_REASON = "a US government work (Library of Congress, NLS); robots.txt allows /nls/"
AT_DOCUMENTS = [
    dict(key="nls-dtbm-library-manual", by="National Library Service for the Blind and Print Disabled (NLS)",
         product="NLS digital talking-book machine", title="Digital Talking Book Machine: Library Manual (NLS)",
         url="https://www.loc.gov/nls/wp-content/uploads/2018/08/Digital-Talking-Book-Library-Manual-1.00-28.Feb_."
             "10.pdf", type="talking-book player", document="manual", access="full", rights=US_GOV,
         reason=NLS_REASON),
    dict(key="nls-dtbm-service-manual", by="National Library Service for the Blind and Print Disabled (NLS)",
         product="NLS digital talking-book machine", title="Digital Talking Book Machine: Service Manual for "
                                                           "Technicians (NLS)",
         url="https://www.loc.gov/nls/wp-content/uploads/2018/08/Digital-Talking-Book-Service-Manual-1.0-"
             "Technician.pdf", type="talking-book player", document="service manual", access="full",
         rights=US_GOV, reason=NLS_REASON),
    dict(key="nls-da2-user-guide", by="National Library Service for the Blind and Print Disabled (NLS)",
         product="NLS DA2 player", title="NLS Digital Advanced Player 2 (DA2) User Guide",
         url=NLS_EQUIPMENT + "da2-user-guide/", type="talking-book player", document="user guide", access="full",
         rights=US_GOV, reason=NLS_REASON),
    dict(key="nls-da2-getting-started", by="National Library Service for the Blind and Print Disabled (NLS)",
         product="NLS DA2 player", title="NLS DA2 player: getting started", url=NLS_EQUIPMENT + "da2-getting-started/",
         type="talking-book player", document="quick start guide", access="full", rights=US_GOV, reason=NLS_REASON),
    dict(key="nls-braille-ereader", by="NLS (guides written with HumanWare and Zoomax)",
         product="NLS Braille eReader", title="NLS Braille eReader user guides and FAQs",
         url=NLS_EQUIPMENT + "nls-braille-ereader-humanware-user-guide/", type="braille display",
         document="user guide", access="link", rights="may be the makers' copyright (written for NLS by the makers)",
         reason="link only: loc.gov makes no blanket public-domain statement and these guides were written by the "
                "makers"),
    dict(key="va-blind-rehabilitation", by="US Department of Veterans Affairs", product="every device",
         title="VA Blind Rehabilitation Service (VIST coordinators arrange devices and their repair)",
         url="https://www.prosthetics.va.gov/blindrehab/index.asp", type="assistive technology services",
         document="guide", access="full", rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="acl-at-act", by="Administration for Community Living (HHS)", product="every device",
         title="State Assistive Technology Act programmes: device loans, reuse and repair help (ACL)",
         url="https://acl.gov/programs/assistive-technology/assistive-technology", type="assistive technology "
                                                                                        "services",
         document="guide", access="full", rights=US_GOV, reason="a US government work; robots.txt allows the page"),
    dict(key="fcc-ndbedp", by="Federal Communications Commission", product="communication devices for deaf-blind "
                                                                           "people",
         title="National Deaf-Blind Equipment Distribution Program (iCanConnect)",
         url="https://www.fcc.gov/general/national-deaf-blind-equipment-distribution-program",
         type="assistive technology services", document="guide", access="link", rights=US_GOV,
         reason="link only: fcc.gov refuses programs (HTTP 403), so the page is not read"),
]

CATEGORIES = {
    "electronics_service": dict(
        name="Electronics service manuals and repair guides (TVs, radios, stereos, computers, consoles)",
        description="Service manuals, schematics and repair manuals of televisions, radios and receivers, stereos "
                    "and amplifiers, turntables and tape decks, VCRs and camcorders, disc players, computers, "
                    "laptops and game consoles from the Internet Archive; iFixit's repair guides for phones, "
                    "tablets, laptops, consoles, TVs and audio gear (links, personal use); and the US Navy's guides "
                    "to test equipment and test methods.",
        kind="manuals", licence=INDEX_LICENCE, ia_any=SERVICE_IA, ia_kinds=SERVICE_KINDS, ia_exclude=SERVICE_EXCLUDE,
        documents=SERVICE_DOCUMENTS, public_guides=[GUIDES["neets_16"], GUIDES["neets_21"], GUIDES["neets_19"]],
        notice=MAINS_NOTICE),
    "electronics_test_equipment": dict(
        name="Electronic test equipment and soldering stations (manuals)",
        description="Multimeters, oscilloscopes, signal generators, logic analysers, bench power supplies and "
                    "soldering stations: the makers' libraries (Fluke, Tektronix, Keysight, RIGOL, SIGLENT, OWON, "
                    "HAKKO, Weller, PINE64, UNI-T, Extech, B&K Precision; links), the Internet Archive's manuals and "
                    "OSHA's guide to electrical hazards.",
        kind="manuals", licence=INDEX_LICENCE, ia=TEST_IA, makers=TEST_MAKERS,
        public_guides=[GUIDES["electrical_hazards"]], notice=TEST_NOTICE),
    "assistive_tech_repair": dict(
        name="Assistive technology care, troubleshooting and repair (manuals and programmes)",
        description="Video and handheld magnifiers, braille displays and notetakers, braille embossers, talking "
                    "devices, DAISY and NLS talking-book players, OCR reading devices and travel aids: the makers' "
                    "manuals and support pages (links), NLS's player guides and technicians' service manual, and "
                    "where to get devices repaired or replaced (NLS, VA, state AT programmes, the FCC's deaf-blind "
                    "equipment programme).",
        kind="manuals", licence=INDEX_LICENCE, makers=AT_MAKERS, documents=AT_DOCUMENTS, notice=DEVICE_NOTICE),
}
