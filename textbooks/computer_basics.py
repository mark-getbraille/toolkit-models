"""Computer and phone basics for beginners for the reference library, in the group "Reference, computer and phone
basics" (the owner's request of 2026-11-22). Keys: computer-basics (every book), pcb:<name>.

What this module builds, in plain words:
  - pcb:index, a guide to the library for someone learning computers and phones (the toolkit's own facts and links,
    CC0): the parts of a computer and first steps, files, email, the web, printing and Wi-Fi, phones and tablets,
    office programs, keyboard shortcuts, troubleshooting, and screen readers, with the books by key, the picture
    packs, and the beginner courses that are links only (GCFGlobal, Northstar, DigitalLearn, the makers' help);
  - IN FULL, under CC BY 4.0 (the LibreOffice Documentation Team's guides say "may be distributed and/or modified
    under the terms of either the GNU General Public License ... or the Creative Commons Attribution License ...
    version 4.0 or later"; the CC BY choice is taken): the LibreOffice Getting Started Guide (every chapter: the
    basics, Writer, Calc, Impress, Draw, Base, Math, file formats, settings and the keyboard shortcuts), the Writer
    Guide (the word processor) and the Calc Guide (the spreadsheet), version 26.2, from books.libreoffice.org;
  - IN FULL: the Library of Congress's Personal Digital Archiving pages (keeping digital photos, email, records,
    audio, video and websites safe: copies, folders, file names, backups), a US government work.
  Every book carries TECH_SAFETY in its notice (restart first, updates, backups, downloads only from the maker or the
  official store, never give a password or code to a caller).

Already in the library and not repeated: Microsoft's support articles for Windows, Office, Outlook, Edge and Teams
and the Microsoft 365 documentation (techdocs, tech:ms_*), NVDA's user guide and key commands (at-docs), digital.gov
and USA.gov (gov-help), and scams and online security (the privacy collection).

Not built (NOT_INCLUDED, link-only): GCFGlobal, Northstar Digital Literacy and DigitalLearn.org (copyright), Apple's
and Google's user guides (copyright), the FCC's consumer guides (public domain, but fcc.gov refuses programs),
DigitalLiteracy.gov (retired), and Wikibooks' Computers for Beginners (already in the Kiwix library).

Run from the repository's folder:
  python3 textbooks/computer_basics.py pcb:libreoffice_getting_started --out build/textbooks --limit 3
  python3 textbooks/computer_basics.py --list computer-basics
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "computer"
GROUPS = {GROUP: "Reference, computer and phone basics"}

TECH_SAFETY = ("Computer safety: when something stops working, restart it first; keep the system and apps updated; "
               "back up your files in two places; download programs and apps only from the maker's own site or the "
               "official app store; and never give a password or a sign-in code to someone who calls, texts or "
               "emails you.")

# ====================================================================== LibreOffice guides (CC BY 4.0)

LO = "https://books.libreoffice.org/en/"
LO_VERSION = "262"            # LibreOffice 26.2, the newest guides on books.libreoffice.org (2026-11-22)
LO_LICENCE_TEXT = (r"distributed and/or modified under the terms of either the GNU General Public License .{0,80}"
                   r"or the Creative Commons Attribution License .{0,80}version 4\.0 or later")
LO_NOTICE = ("By the LibreOffice Documentation Team (contributors named in the guide's Preface), licensed under the "
             "Creative Commons Attribution License 4.0 (https://creativecommons.org/licenses/by/4.0/), one of the two "
             "licences the guide offers; converted to an accessible format, pictures described by their captions. "
             "LibreOffice is a trademark of The Document Foundation. " + TECH_SAFETY)


def lo_guide(code, name, title, subject, description):
    """One LibreOffice guide of books.libreoffice.org: its contents page and every chapter page (code: "GS" Getting
    Started, "WG" Writer, "CG" Calc), its licence line read from the Preface at every build."""
    book = f"{code}{LO_VERSION}"
    return dict(K.WEB, name=name, title=title, group=GROUP, country="International", subject=subject,
                publisher="The LibreOffice Documentation Team (The Document Foundation)", licence="CC BY 4.0",
                licence_url="https://creativecommons.org/licenses/by/4.0/", source=f"{LO}{book}/{book}.html",
                licence_page=f"{LO}{book}/{book}00-Preface.html", licence_text=LO_LICENCE_TEXT,
                description=description, notice=LO_NOTICE,
                content=(r'<div id="SECDISPLAYAREAregion"[^>]*>', r'<div id="SECTOCregion"'),
                crawl=[(f"{LO}{book}/{book}.html", 1)], pages=rf"^{LO}{book}/{book}(\d\d-[A-Za-z]+)?\.html$",
                unit_rules=[(rf"{book}\.html", "Contents"), (rf"{book}00-", "Preface"), (r".", "Chapters")],
                version=f"LibreOffice {LO_VERSION[:2]}.{LO_VERSION[2:]} guide (books.libreoffice.org)", limit=40)


GUIDES = [
    lo_guide("GS", "libreoffice_getting_started", "LibreOffice Getting Started Guide (version 26.2)",
             "Office programs (LibreOffice)",
             "The beginner's guide to the free LibreOffice suite, every chapter: LibreOffice basics (starting it, "
             "menus, toolbars, opening and saving files), getting started with Writer (word processing), Calc "
             "(spreadsheets), Impress (presentations), Draw, Base (databases) and Math, styles and templates, "
             "images, file formats and exporting to PDF and Microsoft Office formats, macros, settings, "
             "customising, and the keyboard shortcuts."),
    lo_guide("WG", "libreoffice_writer_guide", "LibreOffice Writer Guide (version 26.2)",
             "Word processing (LibreOffice Writer)",
             "The full guide to Writer, LibreOffice's word processor, every chapter: text basics and advanced text, "
             "formatting text and pages, printing and exporting, styles and templates, images, lists, tables, mail "
             "merge, tables of contents and indexes, fields, forms, and the keyboard shortcuts."),
    lo_guide("CG", "libreoffice_calc_guide", "LibreOffice Calc Guide (version 26.2)",
             "Spreadsheets (LibreOffice Calc)",
             "The full guide to Calc, LibreOffice's spreadsheet, every chapter: entering and editing data, "
             "formatting, styles, charts, printing and exporting, formulas and functions, pivot tables, data "
             "analysis, linking data, sharing and reviewing, Calc as a database, settings, the keyboard shortcuts "
             "and the error codes."),
]

# ====================================================================== Library of Congress: personal digital archiving

LOC_PDA = "https://www.digitalpreservation.gov/personalarchiving/"
LOC_PAGES = [LOC_PDA] + [LOC_PDA + p for p in ("photos.html", "email.html", "records.html", "audio.html",
                                                "video.html", "websites.html")]
GUIDES.append(X.page_list_book(
    GROUP, "loc_personal_digital_archiving", "Personal Digital Archiving: keeping your digital photos, email and "
    "records safe (Library of Congress)", "Saving and backing up files", "Library of Congress", LOC_PAGES,
    r"^https://www\.digitalpreservation\.gov/personalarchiving/([a-z]+\.html)?$",
    "The Library of Congress's advice for keeping personal digital files: what you have and where, deciding what to "
    "keep, organising files in folders with clear names, making copies on different storage and in different places, "
    "and checking them, for digital photos, email, personal records, audio, video and websites.",
    f"From the Library of Congress: a US government work (public domain). {TECH_SAFETY}",
    units=[(r"photos", "Photos"), (r"email", "Email"), (r"records", "Records"), (r"audio|video", "Audio and video"),
           (r"websites", "Websites"), (r".", "Personal archiving")],
    content=(r'<div id="main_body"[^>]*>', r'<div id="footer"')))

# ====================================================================== the index

SECTIONS = [
    ("Getting started: the parts of a computer, turning it on and off, files and folders",
     "The first steps with a computer, for a beginner or someone helping one.", [
         ("key", "pcb:libreoffice_getting_started", "LibreOffice Getting Started: opening, saving and organising "
                                                    "documents"),
         ("key", "pcb:loc_personal_digital_archiving", "Keeping files safe: folders, file names and backups"),
         ("key", "comp:index", "Going further: Linux, programming, the Windows command prompt, home networking "
                               "and phones (the computers guide)"),
         ("pack", "commons_computer_basics", "Power buttons, touchpads, keys, memory and SIM cards, cartridges"),
         ("pack", "open_images_computer_basics", "Floppy disks, hubs, mousepads, tablet chargers and stands"),
         ("link", "GCFGlobal Computer Basics (free lessons)", "https://edu.gcfglobal.org/en/computerbasics/",
          "Goodwill Community Foundation's copyright; open it in a browser"),
         ("link", "DigitalLearn.org (Public Library Association's beginner courses)", "https://www.digitallearn.org/",
          "the PLA's copyright; open it in a browser"),
         ("link", "Northstar Digital Literacy (skills checks)", "https://www.digitalliteracyassessment.org/",
          "Literacy Minnesota's copyright; open it in a browser")]),
    ("Email, the web, downloading safely, printing and Wi-Fi", "Using the internet and a printer at home.", [
        ("key", "tech:ms_outlook_support", "Microsoft Outlook support articles"),
        ("key", "tech:ms_edge_support", "Microsoft Edge (web browser) support articles"),
        ("key", "tech:ms_windows_support", "Windows support articles: Wi-Fi, printers, updates and storage"),
        ("link", "FCC consumer guides (internet, Wi-Fi, phones and accessibility)",
         "https://www.fcc.gov/consumers/guides", "public domain, but fcc.gov refuses programs; open it in a browser")]),
    ("Smartphones and tablets: calls, texts, apps, settings and updates", "Phones and tablets for beginners.", [
        ("link", "iPhone and iPad user guides (Apple)", "https://support.apple.com/guide/iphone/welcome/ios",
         "Apple's copyright; open it in a browser"),
        ("link", "Android help (Google)", "https://support.google.com/android/", "Google's copyright; open it in a "
                                                                                "browser"),
        ("manuals", "personal_electronics", "Phone and tablet manuals, as links")]),
    ("Video calls and cloud storage", "Talking over video and keeping files online.", [
        ("key", "tech:ms_teams_support", "Microsoft Teams support articles"),
        ("key", "tech:ms_sharepoint_onedrive_support", "OneDrive and SharePoint support articles"),
        ("pack", "commons_computer_basics", "Video calls and docking stations")]),
    ("Office programs: word processors and spreadsheets", "Writing documents and keeping figures.", [
        ("key", "pcb:libreoffice_writer_guide", "LibreOffice Writer Guide, in full"),
        ("key", "pcb:libreoffice_calc_guide", "LibreOffice Calc Guide, in full"),
        ("key", "tech:ms_office_support", "Microsoft Office support articles"),
        ("manuals", "software", "Old program manuals (word processors, spreadsheets), as links")]),
    ("Keyboard shortcuts and screen readers", "Doing everything from the keyboard, and hearing the screen.", [
        ("key", "atdoc:nvda_user_guide", "NVDA user guide (the free Windows screen reader)"),
        ("key", "atdoc:nvda_key_commands", "NVDA key commands"),
        ("word", "vision-living", "The vision collection's books on screen readers and magnification"),
        ("link", "Keyboard shortcuts in Windows (Microsoft)", "https://support.microsoft.com/en-us/windows/keyboard-"
                                                              "shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-"
                                                              "cb9706c75eec", "Microsoft's copyright; open it in a "
                                                                              "browser")]),
    ("Troubleshooting: restart, updates, storage full", "When something goes wrong.", [
        ("key", "tech:ms_windows_support", "Windows troubleshooting articles"),
        ("manuals", "computers", "Computer and router manuals, as links")]),
]
INDEX = X.index_maker("pcb", GROUP, "Computer and phone basics: a guide to the library", "Computer and phone basics",
                      "A guide to the library for anyone learning computers and phones: the parts of a computer and "
                      "first steps, email, the web, printing and Wi-Fi, phones and tablets, video calls and cloud "
                      "storage, office programs, keyboard shortcuts and screen readers, and troubleshooting.",
                      SECTIONS, country="International")
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("pcb", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"computer-basics": lambda: ["pcb:index"] + [f"pcb:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "computer_libreoffice": "books.libreoffice.org: each guide's Preface (checked at every build) says it \"may be "
                            "distributed and/or modified under the terms of either the GNU General Public License ... "
                            "version 3 or later, or the Creative Commons Attribution License ... version 4.0 or "
                            "later\"; the CC BY 4.0 choice is used, with credit. robots.txt allows everything; no AI "
                            "rules (checked 2026-11-22).",
    "computer_loc": "www.digitalpreservation.gov: a Library of Congress site, a US government work (17 U.S.C. 105, "
                    "checked on govinfo.gov's policies page at every build); it has no robots.txt rules (checked "
                    "2026-11-22).",
    "computer_index": "The index (pcb:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("GCFGlobal computer, internet, email, smartphone and office lessons", "Copyright of the Goodwill Community "
     "Foundation; its terms do not allow copying. Link-only (pcb:index). Index: https://edu.gcfglobal.org/en/topics/"
     "tech/"),
    ("Northstar Digital Literacy curriculum and assessments", "Copyright of Literacy Minnesota (licensed to "
     "libraries and schools). Link-only. Index: https://www.digitalliteracyassessment.org/"),
    ("DigitalLearn.org courses (Public Library Association)", "The PLA's copyright; no open licence on its pages "
     "(checked 2026-11-22). Link-only. Index: https://www.digitallearn.org/"),
    ("DigitalLiteracy.gov (NTIA)", "Retired; the address no longer answered (2026-11-22) and its archived copies are "
     "only in the Wayback Machine, which did not answer this build machine. Index: "
     "https://web.archive.org/web/2019/https://digitalliteracy.gov/"),
    ("FCC consumer guides (internet and Wi-Fi, phones, robocalls, hearing aid compatibility, accessibility)",
     "Public domain, but www.fcc.gov refuses programs (\"403\", robots.txt included, 2026-11-22). Link-only. Index: "
     "https://www.fcc.gov/consumers/guides"),
    ("Apple's iPhone, iPad and Mac user guides and Google's Android and Chromebook help", "The makers' copyright; "
     "link-only. Microsoft's open documentation is built (techdocs). Index: https://support.apple.com/guide/ and "
     "https://support.google.com/android/"),
    ("LibreOffice Help (help.libreoffice.org)", "Under the Mozilla Public License 2.0, a file-level copyleft licence "
     "the library does not list; the Documentation Team's guides (CC BY 4.0) cover the same ground and are built. "
     "Index: https://help.libreoffice.org/"),
    ("Wikibooks: Computers for Beginners, Basic Computing Using Windows", "CC BY-SA, and already whole in the Kiwix "
     "library's Wikibooks. Index: https://en.wikibooks.org/wiki/Computers_for_Beginners"),
    ("Scams, passwords and online security", "The privacy collection covers them; not repeated. Index: "
     "https://consumer.ftc.gov/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
