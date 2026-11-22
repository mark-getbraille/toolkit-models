"""Electronics repair and assistive-technology care for the reference library, in the group "Reference, electronics
repair and assistive technology" (the owner's request of 2026-11-22). Keys: electronics (every book), elec:<name>.

What this module builds, each IN FULL:
  - Lessons in Electric Circuits (Tony R. Kuphaldt), in the group "Reference, power and electrical" since
    2026-11-22 (power_books.py; its keys unchanged), all six volumes (DC, AC, semiconductors, digital, reference,
    experiments), CC BY 4.0 by the author's own statement (each volume's Appendix 3, checked at every build), read
    from the author's PDFs on ibiblio.org;
  - the US Navy's Electricity and Electronics Training Series modules the library did not have yet (microwave
    principles, modulation, synchros and servos, radio-frequency communications, radar, test methods and practices,
    magnetic recording), judged at every build by the release rule for military publications (military_release.py;
    their front matter prints Distribution Statement A), from the Internet Archive's copies with their words
    (sources.NEETS has the other modules);
  - Wikibooks' electronics and computer books (Electronics, Practical Electronics, Electronics Handbook, Circuit
    Theory, How To Assemble A Desktop PC), CC BY-SA 4.0 (share-alike), every page;
  - the National Library Service for the Blind and Print Disabled (Library of Congress): its Digital Talking Book
    Machine library manual and technician's service manual (cleaning, cartridges, batteries, faults and their
    remedies), and its pages on the DA2 player (getting started and the full user guide) and the commercial players
    that read NLS books; US government works;
  - the VA Blind Rehabilitation Service's pages (blind rehabilitation centres, outpatient services, VIST coordinators,
    who supplies and repairs veterans' low-vision and blindness devices) and the Administration for Community
    Living's page on the state Assistive Technology Act programmes (device loans, demonstrations, reuse and repair);
    US government works;
  - old public-domain radio books (published before 1931; the builder checks each Internet Archive item's year):
    radio receivers and servicing, the radio amateur's and experimenter's handbooks, practical radio. They are OLD:
    valve sets, out-of-date safety practice and units as written.

Not built (NOT_INCLUDED, each with its index address for the personal assistant): iFixit (ai-train=no and its terms),
the FCC's National Deaf-Blind Equipment Distribution Program pages (fcc.gov refuses programs), the NLS Braille
eReader user guides (written by HumanWare and Zoomax for NLS: they may be the makers' copyright), All About Circuits
(its site's own copyright on the newer text), RESNA, the AT3 Center, and the makers' manuals (HumanWare, Vispero,
Optelec and others: the manual library's links).

Safety: every book's notice starts with MAINS_NOTE or, for the assistive-device books, DEVICE_NOTE.

Run from the repository's folder:
  python3 textbooks/electronics_books.py elec:nls_dtbm_service_manual --out build/textbooks --limit 5
  python3 textbooks/electronics_books.py --list electronics
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "electronics"
GROUPS = {GROUP: "Reference, electronics repair and assistive technology"}

MAINS_NOTE = ("Safety first: mains electricity can kill. Unplug a device before opening it; televisions, picture tubes, "
              "valve sets, microwave ovens and power supplies can hold a dangerous charge long after unplugging. "
              "Lithium batteries can catch fire if damaged or swollen: never charge one that is.")
DEVICE_NOTE = ("Before you open an assistive device, check its warranty and any loan agreement (NLS players belong to "
               "the Library of Congress and are repaired free through your library); use only the maker's battery "
               "and charger, and never charge a swollen battery.")

# ====================================================================== Lessons in Electric Circuits (CC BY 4.0)

LIEC = "https://www.ibiblio.org/kuphaldt/electricCircuits/"
LIEC_TEXT = r"Creative Commons Attribution 4\.0"
LIEC_VOLUMES = [
    ("DC", "DC/DC.pdf", "DC/DC_A3.html", "Volume I: DC", "2023-02-03",
     "direct current: Ohm's law, series and parallel circuits, Kirchhoff's laws, meters and their use, batteries, "
     "capacitors and inductors, magnetism and network analysis"),
    ("AC", "AC/AC.pdf", "AC/AC_A3.html", "Volume II: AC", "2021-11-06",
     "alternating current: reactance and impedance, resonance, transformers, polyphase power, filters and motors"),
    ("semiconductors", "Semi/SEMI.pdf", "Semi/SEMI_A3.html", "Volume III: Semiconductors", "2021-11-06",
     "semiconductors: diodes and rectifiers, transistors, field-effect transistors, thyristors, operational "
     "amplifiers and practical analogue circuits"),
    ("digital", "Digital/DIGI.pdf", "Digital/DIGI_A3.html", "Volume IV: Digital", "2021-11-06",
     "digital electronics: number systems, logic gates, Boolean algebra, flip-flops, counters, shift registers, "
     "converters and memory"),
    ("reference", "Ref/REF.pdf", "Ref/REF_A3.html", "Volume V: Reference", "2021-11-06",
     "a reference volume: useful equations, colour codes, conductor and insulator tables, circuit symbols and "
     "units"),
    ("experiments", "Exper/EXP.pdf", "DC/DC_A3.html", "Volume VI: Experiments", "2021-11-06",
     "hands-on experiments: building and testing circuits with a multimeter, from a simple battery circuit to "
     "amplifiers and digital logic, with safety notes"),
]
# Lessons in Electric Circuits is in the top-level group "Reference, power and electrical" (power_books.GROUP, the
# owner's decision of 2026-11-22); its keys (elec:kuphaldt_liec_*) stay the same.
POWER_GROUP = "power"
PDFS = [
    dict(group=POWER_GROUP, country="International", licence="CC BY 4.0",
         licence_url="https://creativecommons.org/licenses/by/4.0/", licence_page=LIEC + page,
         licence_text=LIEC_TEXT, level="reference", name=f"kuphaldt_liec_{key.lower()}",
         title=f"Lessons in Electric Circuits, {title} (Tony R. Kuphaldt)", subject="Electricity and electronics",
         publisher="Tony R. Kuphaldt", pdf=LIEC + pdf, page=LIEC, published=published,
         version=f"minor revision {published}",
         description=f"Lessons in Electric Circuits, the free textbook series by Tony R. Kuphaldt: {words}.",
         notice="Lessons in Electric Circuits, copyright (C) 2000-2023 Tony R. Kuphaldt, under the Creative Commons "
                "Attribution 4.0 licence (CC BY 4.0); its pages made into chapters. " + MAINS_NOTE)
    for key, pdf, page, title, published, words in LIEC_VOLUMES
]

# ====================================================================== NEETS modules not yet in the library

NEETS_MORE = [
    (11, "Microwave Principles", "NEETSModule11"), (12, "Modulation Principles", "Module12modulation"),
    (15, "Principles of Synchros, Servos, and Gyros", "NEETSModule15"),
    (17, "Radio-Frequency Communications Principles", "NEETSModule17"), (18, "Radar Principles", "NEETSModule18"),
    (21, "Test Methods and Practices", "NEETSModule21"), (23, "Magnetic Recording", "NEETSModule23"),
]
PDFS += [
    K.us_pdf(GROUP, name=f"navy_neets_module_{n:02d}", title=f"NEETS Module {n}: {words}",
             subject="Electricity and electronics", archive=archive, distribution_a=True,
             publisher="Naval Education and Training Professional Development and Technology Center (US Navy)",
             description=f"Module {n} of the US Navy's Electricity and Electronics Training Series (NEETS), a "
                         f"self-study course: {words[0].lower() + words[1:]}.",
             work="a work of the US Navy",          # the builder puts the truthful release line first
             notice=MAINS_NOTE)
    for n, words, archive in NEETS_MORE
]

# ====================================================================== NLS players (Library of Congress)

NLS = "https://www.loc.gov/nls/"
NLS_EQUIPMENT = NLS + "services-and-resources/equipment-for-nls-materials/"
NLS_PUBLISHER = "National Library Service for the Blind and Print Disabled (NLS), Library of Congress"
NLS_NOTICE = ("From the National Library Service for the Blind and Print Disabled (NLS), Library of Congress: a US "
              "government work. NLS players are lent free and repaired or replaced through your cooperating network "
              "library: call it, or 1-888-657-7323, before opening a player. " + DEVICE_NOTE)
PDFS += [
    K.us_pdf(GROUP, name="nls_dtbm_library_manual", title="Digital Talking Book Machine: Library Manual (NLS)",
             subject="Talking-book players", publisher=NLS_PUBLISHER,
             pdf=NLS + "wp-content/uploads/2018/08/Digital-Talking-Book-Library-Manual-1.00-28.Feb_.10.pdf",
             page=NLS_EQUIPMENT, published="2010-02-28", version="version 1.00",
             description="NLS's manual for network library staff on the digital talking-book machines (the standard "
                         "and advanced players): the controls and keys, cartridges and the USB port, batteries and "
                         "charging, tone, speed and volume, cleaning, checking a machine that comes back, the "
                         "machine's own self-test and the common faults with what to do about each.",
             notice=NLS_NOTICE),
    K.us_pdf(GROUP, name="nls_dtbm_service_manual", title="Digital Talking Book Machine: Service Manual for "
             "Technicians (NLS)", subject="Talking-book players (repair)", publisher=NLS_PUBLISHER,
             pdf=NLS + "wp-content/uploads/2018/08/Digital-Talking-Book-Service-Manual-1.0-Technician.pdf",
             page=NLS_EQUIPMENT, published="2010", version="version 1.0",
             description="NLS's service manual for the technicians who repair digital talking-book machines: "
                         "taking the player apart and putting it back, the battery, keypad, speaker, cartridge "
                         "port and main board, diagnostic tests and error codes, and replacement parts.",
             notice=NLS_NOTICE),
]
GUIDES = [
    K.guide(GROUP, "nls_players", "NLS talking-book players: the DA2 user guide, getting started and compatible "
            "players (NLS)", "Talking-book players", NLS_PUBLISHER, NLS_EQUIPMENT.rstrip("/"),
            r"^https://www\.loc\.gov/nls/services-and-resources/equipment-for-nls-materials/(da2-[a-z0-9-]+|"
            r"commercial-players-compatible-with-nls-materials-and-additional-products)/?$",
            "NLS's own pages on its players: getting started with the Digital Advanced Player 2 (DA2) and its full "
            "user guide (the keys, inserting cartridges and USB drives, wireless downloads from BARD, batteries and "
            "charging, sleep timer, bookmarks, settings, cleaning and care, and what to do when it will not play), "
            "and the list of commercial players and apps that read NLS books.",
            NLS_NOTICE, depth=1, limit=20),
]

# ====================================================================== VA and the state AT Act programmes

GUIDES += [
    K.guide(GROUP, "va_blind_rehabilitation", "Blind Rehabilitation Service (US Department of Veterans Affairs)",
            "Assistive technology services for veterans", "US Department of Veterans Affairs, Blind Rehabilitation "
            "Service", "https://www.prosthetics.va.gov/PROSTHETICS/blindrehab/index.asp",
            r"^https://www\.prosthetics\.va\.gov/PROSTHETICS/blindrehab/[A-Za-z_]+\.asp$",
            "The VA Blind Rehabilitation Service's pages, every page: what it offers blind and low-vision veterans, "
            "the blind rehabilitation centres and outpatient specialists, Visual Impairment Services Team (VIST) "
            "coordinators (who arrange devices and their repair), recreation and history.",
            "A work of the US Department of Veterans Affairs (public domain). Veterans: ask your VIST coordinator "
            "about getting, replacing or repairing low-vision and blindness devices.", depth=1, limit=30),
    K.guide(GROUP, "acl_assistive_technology", "State Assistive Technology Act programmes (Administration for "
            "Community Living)", "Assistive technology programmes", "Administration for Community Living (ACL), US "
            "Department of Health and Human Services",
            "https://acl.gov/programs/assistive-technology/assistive-technology",
            r"^https://acl\.gov/programs/assistive-technology/[a-z0-9-]+$",
            "The Administration for Community Living's pages on the Assistive Technology Act: every state's AT "
            "programme lends devices to try, demonstrates them, passes on reused equipment and helps with funding "
            "and repair; how to find your state's programme.",
            "A work of the US Department of Health and Human Services (public domain).", depth=1, limit=20),
]

# ====================================================================== Wikibooks (CC BY-SA 4.0)

WIKIBOOKS = dict(group=GROUP, country="International", licence="CC BY-SA 4.0",
                 licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
                 publisher="Wikibooks contributors (en.wikibooks.org)",
                 notice="From Wikibooks (en.wikibooks.org), written by its contributors, CC BY-SA 4.0; each page's "
                        "history lists its authors.",
                 licence_page="https://en.wikibooks.org/wiki/Wikibooks:Copyrights",
                 licence_text=r"Creative Commons Attribution-ShareAlike", page_mark=r"Creative Commons Attribution-"
                 r"ShareAlike", sitemap="", unit_rules=[], level="reference",
                 content=(r'<div id="mw-content-text"[^>]*>', r'<div class="printfooter"'),
                 drop=[r'<span class="mw-editsection">.*?</span>\s*</span>', r'<div class="(?:navbox|noprint)[^"]*".*?'
                       r'</div>', r'<table class="[^"]*(?:ambox|metadata|navbox)[^"]*".*?</table>'],
                 changes="every page of the book made into web pages, with the site's menus, edit links and notices "
                         "left out (its pictures' descriptions kept)")


def wikibook(group, name, book, title, subject, description, notice=""):
    """A Wikibooks book: its contents page and every page of the book it links (and those pages link), read whole."""
    pages = rf"^https://en\.wikibooks\.org/wiki/{book}/[^?#:]+$"
    entry = dict(WIKIBOOKS, group=group, name=name, title=title, subject=subject, description=description,
                 source=f"https://en.wikibooks.org/wiki/{book}", crawl=[(f"https://en.wikibooks.org/wiki/{book}", 2)],
                 follow=pages, pages=pages, limit=500)
    if notice:
        entry["notice"] = WIKIBOOKS["notice"] + " " + notice
    return entry


GUIDES += [
    wikibook(GROUP, "wikibooks_electronics", "Electronics", "Electronics (Wikibooks)", "Electricity and electronics",
             "Wikibooks' open textbook of electronics: charge, current and voltage, resistors, capacitors and "
             "inductors, circuit analysis, diodes, transistors, amplifiers, digital circuits and instruments.",
             MAINS_NOTE),
    wikibook(GROUP, "wikibooks_practical_electronics", "Practical_Electronics", "Practical Electronics (Wikibooks)",
             "Electronics (practical)", "Wikibooks' hands-on electronics book: components and how to recognise "
             "them, tools, soldering, using a multimeter and an oscilloscope, and simple circuits to build.",
             MAINS_NOTE),
    wikibook(GROUP, "wikibooks_electronics_handbook", "Electronics_Handbook", "Electronics Handbook (Wikibooks)",
             "Electricity and electronics", "Wikibooks' handbook of electronic components and circuits: passive "
             "and active parts, power supplies, amplifiers, oscillators, filters and digital logic.", MAINS_NOTE),
    wikibook(GROUP, "wikibooks_circuit_theory", "Circuit_Theory", "Circuit Theory (Wikibooks)", "Circuit analysis",
             "Wikibooks' circuit theory: laws and theorems, phasors, transient and steady-state analysis, filters "
             "and two-port networks."),
    wikibook(GROUP, "wikibooks_assemble_desktop_pc", "How_To_Assemble_A_Desktop_PC", "How To Assemble A Desktop PC "
             "(Wikibooks)", "Computer repair and building", "Wikibooks' guide to building and upgrading a desktop "
             "computer: choosing parts, static safety, fitting the processor, memory, drives, cards and power "
             "supply, first start-up and troubleshooting.", MAINS_NOTE),
]

# ====================================================================== old public-domain radio books (before 1931)

OLD = dict(group=GROUP, country="United States", licence="Public domain (published before 1931)",
           licence_url="https://www.copyright.gov/help/faq/faq-duration.html", old_public_domain=True,
           level="reference", changes="its scanned pages' machine-read text (with the scanner's mistakes) made into "
                                      "web pages, one per chapter")
OLD_NOTE = (" Published in {year}: an old book about valve (vacuum tube) radio sets, kept for its history and its "
            "plain explanations; its safety advice, parts and units are out of date, and the machine-read text has "
            "the scanner's mistakes. " + MAINS_NOTE)


def old_radio(name, title, publisher, archive, year, description):
    """An old public-domain radio book from the Internet Archive as a PDF entry."""
    return dict(OLD, name=name, title=title, subject="Radio (history and servicing)", publisher=publisher,
                archive=archive, published=str(year), description=description,
                notice=OLD_NOTE.format(year=year).strip())


PDFS += [
    old_radio("radio_receivers_and_servicing_1928", "Radio Receivers and Servicing (International Correspondence "
              "Schools, 1928)", "International Correspondence Schools", "radioreceiversse00icss", 1928,
              "A correspondence-school course on how radio receivers work and how to service them: testing valves, "
              "batteries and loudspeakers, finding faults by symptom and repairing them."),
    old_radio("collins_radio_amateurs_hand_book_1922", "The Radio Amateur's Hand Book (A. Frederick Collins, 1922)",
              "A. Frederick Collins (Thomas Y. Crowell)", "TheRadioAmateursHandBook_709", 1922,
              "A complete early handbook of radio: how receiving and sending sets work, how to build and connect "
              "them, aerials and earths, valves and batteries."),
    old_radio("radio_experimenters_hand_book_1920", "The Radio Experimenter's Hand Book (1920)", "M. B. Sleeper",
              "TheRadioExperimentersHandBook", 1920,
              "A book of practical answers for beginners building radio apparatus: coils, condensers, detectors "
              "and simple receivers."),
    old_radio("moyer_wostrel_practical_radio_1924", "Practical Radio (James A. Moyer and John F. Wostrel, 1924)",
              "James A. Moyer and John F. Wostrel (McGraw-Hill)", "moyer-wostrel-1924-practical-radio", 1924,
              "A practical textbook of radio receivers: how they work, how to build, adjust and repair them, with "
              "the tools and tests of the time."),
]

COLLECTION = K.Collection("elec", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"electronics": lambda: [f"elec:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "electronics_kuphaldt": "www.ibiblio.org/kuphaldt/electricCircuits/ (each volume's Appendix 3, checked at every "
                            "build): \"Creative Commons Attribution 4.0 International (CC BY 4.0)\", Copyright (C) "
                            "2000-2023 Tony R. Kuphaldt. robots.txt: Crawl-delay 2, the book's folder allowed; no AI "
                            "rules (checked 2026-11-22).",
    "electronics_nls": "www.loc.gov/nls/: the NLS manuals and player pages are works of the US government (17 U.S.C. "
                       "105, checked on govinfo.gov's policies page at every build). robots.txt: Crawl-delay 5, "
                       "/nls/ allowed; no AI rules (checked 2026-11-22).",
    "electronics_va_acl": "www.prosthetics.va.gov and acl.gov: works of the US government (17 U.S.C. 105); robots.txt "
                          "allows the pages; no AI rules (checked 2026-11-22).",
    "electronics_old_radio": "Internet Archive scans of radio books published before 1931 (public domain in the US; "
                             "the item's year is checked at every build, build_textbooks.archive_year).",
}
NOT_INCLUDED = [
    ("Wikibooks: Computer Hardware", "CC BY-SA, but its contents page links no pages of the book the reader can "
     "follow (no pages could be read on 2026-11-22); How To Assemble A Desktop PC is built instead. Index: "
     "https://en.wikibooks.org/wiki/Computer_Hardware"),
    ("iFixit repair guides (phones, tablets, laptops, consoles, TVs, assistive devices)", "CC BY-NC-SA, but its "
     "robots.txt says ai-train=no and its Terms of Use allow programs only through its API, keep API answers 24 hours "
     "at most and forbid putting them in indexes or datasets (read 2026-11-21). Link-only, personal use. Index: "
     "https://www.ifixit.com/Device"),
    ("FCC National Deaf-Blind Equipment Distribution Program (iCanConnect)", "Public domain, but www.fcc.gov answers "
     "programs \"403 Forbidden\", robots.txt included (checked 2026-11-22). Link-only. Index: "
     "https://www.fcc.gov/general/national-deaf-blind-equipment-distribution-program and https://www.icanconnect.org/"),
    ("NLS Braille eReader user guides and FAQs (HumanWare and Zoomax models)", "On loc.gov, but written for NLS by "
     "the makers, whose text may be their copyright (loc.gov's legal page makes no blanket public-domain statement, "
     "checked 2026-11-22). Link-only. Index: https://www.loc.gov/nls/services-and-resources/equipment-for-nls-"
     "materials/nls-braille-ereader-humanware-user-guide/"),
    ("All About Circuits textbook", "Built from Lessons in Electric Circuits, which is built here from the author's "
     "own CC BY 4.0 copies; allaboutcircuits.com's pages carry the site's own copyright and terms. Index: "
     "https://www.allaboutcircuits.com/textbook/"),
    ("RESNA and the AT3 Center", "\"Copyright RESNA\" and the AT3 Center's own copyright; not openly licensed "
     "(checked 2026-11-22). The ACL page on the state AT Act programmes is built (elec:acl_assistive_technology). "
     "Link-only. Index: https://www.resna.org/ and https://www.at3center.net/"),
    ("Makers' manuals of assistive devices (HumanWare, Freedom Scientific and Vispero, Optelec, Eschenbach, Zeiss, "
     "Enhanced Vision, Orbit Research, APH, Index Braille, ViewPlus)", "The makers' copyright; listed as links in "
     "the manual library (collection assistive_tech_repair) for the owner to fetch with Program Downloader. Index: "
     "https://www.humanware.com/ and https://www.freedomscientific.com/"),
    ("Instructables, Hackaday and YouTube repair videos", "Their terms do not allow programs to copy their content "
     "(Instructables' and YouTube's terms forbid scraping); not read. Index: https://www.instructables.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
