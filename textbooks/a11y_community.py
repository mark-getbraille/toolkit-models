"""Accessibility community references for the reference library (the owner's request of 2026-11-22), in the group
"Reference, disability and accessibility" (the same group as at_docs.py). Keys: a11y-community (every book),
a11yc:<name>.

Much of this subject is already in the library and is not copied again (the index links it): NVDA's User Guide,
Commands Quick Reference, What's New and Developer Guide and the NVDA add-ons' documentation (at_docs.py, atdoc:),
Orca's help (vision_living.py, vision:orca_help), the W3C's WCAG and WAI guides (accessibility_guides.py) and the NLS
reference guides. What this module adds, in plain words:

  - a11yc:index, "Accessibility communities: a guide to the library" (facts and links, CC0): screen reader user
    communities (NVDA, Orca, Linux), the community wikis, the open books built here and elsewhere in the library by
    key, the Kiwix library's books, and the community sources that are links only, each with the reason;
  - IN FULL, the GNOME desktop help's accessibility section (help.gnome.org/gnome-help/a11y*: the screen reader,
    braille, magnifier, high contrast, text size, sticky, slow and bounce keys, simulated clicks, visual alerts and
    the accessibility menu), "licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License" (a
    share-alike book; the line checked at every build);
  - IN FULL, the Arch Linux wiki's speech and accessibility pages (Accessibility, Speech dispatcher, Festival, Text
    to speech): "Content is available under GNU Free Documentation License 1.3 or later" (a share-alike book, like the
    GNU licences of at_docs.py; the line checked at every build). The whole ArchWiki is also in the Kiwix library
    (archlinux_en_all);
  - IN FULL, KDE UserBase's accessibility pages (Accessibility, Getting Started, KMag, KMouseTool, KMouth, Jovie):
    "Content is available under Creative Commons License SA 4.0" (a share-alike book; checked at every build).

Link-only (NOT_INCLUDED, with the reason and address): the NVDA GitHub wiki (no licence is stated; anyone may edit
it), the NVDA community add-ons website (its robots.txt says ai-train=no; at_docs.py reads the add-ons' own
repositories instead), the old Orca wiki (wiki.gnome.org was retired and frozen in 2024; it states no licence and
points to orca.gnome.org, whose pages state none either), the Debian wiki's accessibility pages (the Debian wiki's own
licensing page says the licence of its content is unclear), the Ubuntu wiki's Accessibility page (a stub), WebAIM's
articles (copyright of WebAIM, Utah State University: already link-only in accessibility_guides.py, linked from the
index here) and an Accessibility Stack Exchange (none exists; the User Experience site, with accessibility questions,
is listed reference-only by stack_exchange.py).

robots.txt of help.gnome.org (none found), wiki.archlinux.org and userbase.kde.org (no rules for our reader, no AI
rules) were checked on 2026-11-22.

Run from the repository's folder:
  python3 textbooks/a11y_community.py a11yc:index --out build/textbooks
  python3 textbooks/a11y_community.py a11yc:gnome_help_accessibility --out build/textbooks --limit 3
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "disability"                         # "Reference, disability and accessibility" (sources.GROUPS)
GROUPS = {}                                  # the group already exists

GFDL = "GFDL-1.3-or-later"
GFDL_URL = "https://www.gnu.org/licenses/fdl-1.3.html"
# The GNU Free Documentation License is a copyleft licence: the toolkit may repackage it as share-alike, like the GNU
# licences at_docs.py adds (added to sources.ALLOWED through more_refs.allowed()).
ALLOWED = {GFDL: "share-alike"}

COMMUNITY_NOTE = ("Written by volunteers of the project's community: software changes often, so check the date of "
                  "each page and the program's own current documentation.")

GNOME = "https://help.gnome.org/gnome-help/"
GNOME_PAGES = [GNOME + p + ".html" for p in (
    "a11y", "a11y-screen-reader", "a11y-braille", "a11y-mag", "a11y-contrast", "a11y-font-size", "a11y-icon",
    "a11y-stickykeys", "a11y-slowkeys", "a11y-bouncekeys", "a11y-right-click", "a11y-dwellclick",
    "a11y-visualalert")]
ARCH = "https://wiki.archlinux.org/title/"
ARCH_PAGES = [ARCH + p for p in ("Accessibility", "Speech_dispatcher", "Festival", "Text_to_speech")]
KDE = "https://userbase.kde.org/"
KDE_PAGES = [KDE + p for p in ("Accessibility", "Accessibility/Getting_Started", "KMag", "KMouseTool", "KMouth",
                               "Jovie")]

GUIDES = [
    X.page_list_book(
        GROUP, "gnome_help_accessibility", "GNOME desktop help: accessibility", "Linux desktop accessibility",
        "The GNOME Project (GNOME Help, written by Shaun McCance and others)", GNOME_PAGES,
        r"^https://help\.gnome\.org/gnome-help/a11y[a-z-]*\.html$",
        "The GNOME desktop's own help on accessibility: the Orca screen reader, braille displays, the screen "
        "magnifier, high contrast, larger text, the accessibility menu, sticky, slow and bounce keys, simulated "
        "secondary click, hover click and visual alerts.",
        "From GNOME Help (the GNOME Project), licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported "
        "License (CC BY-SA 3.0); this copy is shared under the same licence. " + COMMUNITY_NOTE,
        country="International", licence="CC BY-SA 3.0",
        licence_url="https://creativecommons.org/licenses/by-sa/3.0/", licence_page=GNOME_PAGES[0],
        licence_text=r"Creative Commons Attribution-ShareAlike 3\.0 Unported License",
        version="help.gnome.org/gnome-help as published"),
    X.page_list_book(
        GROUP, "arch_wiki_accessibility", "ArchWiki: accessibility and speech", "Linux accessibility",
        "ArchWiki contributors (Arch Linux)", ARCH_PAGES,
        r"^https://wiki\.archlinux\.org/title/[A-Za-z_]+$",
        "The Arch Linux wiki's pages on accessibility (screen readers, braille, magnification and accessible "
        "consoles on Linux), Speech Dispatcher, the Festival speech synthesiser and text to speech.",
        "From the ArchWiki, by its contributors: content available under the GNU Free Documentation License 1.3 or "
        "later; this copy is shared under the same licence. Commands are for Arch Linux; other Linux systems differ. "
        + COMMUNITY_NOTE,
        country="International", licence=GFDL, licence_url=GFDL_URL, licence_page=ARCH_PAGES[0],
        licence_text=r"Content is available under GNU Free Documentation License 1\.3 or later",
        version="wiki.archlinux.org as published"),
    X.page_list_book(
        GROUP, "kde_userbase_accessibility", "KDE UserBase: accessibility", "Linux desktop accessibility",
        "KDE UserBase contributors (KDE)", KDE_PAGES,
        r"^https://userbase\.kde\.org/[A-Za-z_/]+$",
        "KDE's user wiki on accessibility in the Plasma desktop and KDE programs: getting started, the KMag "
        "magnifier, KMouseTool (clicking without pressing the mouse button), KMouth (typed text spoken aloud) and "
        "Jovie (KDE's older text-to-speech service).",
        "From KDE UserBase, by its contributors: content available under Creative Commons License SA 4.0 (CC BY-SA "
        "4.0); this copy is shared under the same licence. Some pages describe older KDE versions. " + COMMUNITY_NOTE,
        country="International", licence="CC BY-SA 4.0",
        licence_url="https://creativecommons.org/licenses/by-sa/4.0/", licence_page=KDE_PAGES[0],
        licence_text=r"Content is available under Creative Commons License SA 4\.0",
        version="userbase.kde.org as published"),
]

NVDA_WIKI = "https://github.com/nvaccess/nvda/wiki"
SECTIONS = [
    ("NVDA", "NV Access's free screen reader for Windows: its own guides are in the library; its community meets on "
     "mailing lists and its wiki.", [
         ("key", "atdoc:nvda_user_guide", "The NVDA User Guide (GPL)"),
         ("key", "atdoc:nvda_key_commands", "NVDA Commands Quick Reference"),
         ("key", "atdoc:nvda_whats_new", "What's new in each NVDA release"),
         ("key", "atdoc:nvda_developer_guide", "The NVDA Developer Guide"),
         ("key", "atdoc:nvda_addons_gpl2", "NVDA add-ons and their documentation (GPL version 2)"),
         ("key", "atdoc:nvda_addons_open", "NVDA add-ons and their documentation (other open licences)"),
         ("link", "The NVDA wiki (FAQ, application support, guides such as switching from JAWS, extra voices, log "
          "files, braille display drivers)", NVDA_WIKI, "no licence is stated and anyone may edit it: link only"),
         ("link", "The NVDA community add-ons website", "https://addons.nvda-project.org/",
          "its robots.txt says ai-train=no, so it is not read; the add-ons' own documentation is in the books "
          "above"),
         ("link", "NVDA users' mailing list (groups.io)", "https://nvda.groups.io/g/nvda", "a discussion list: "
          "messages are their writers' own; link only")]),
    ("Orca and the Linux desktop", "GNOME's Orca screen reader and the accessibility of the Linux desktops.", [
        ("key", "vision:orca_help", "Orca's own help (CC BY-SA 3.0)"),
        ("key", "a11yc:gnome_help_accessibility", "GNOME desktop help: accessibility (CC BY-SA 3.0)"),
        ("key", "a11yc:kde_userbase_accessibility", "KDE UserBase: accessibility (CC BY-SA 4.0)"),
        ("key", "a11yc:arch_wiki_accessibility", "ArchWiki: accessibility and speech (GFDL)"),
        ("link", "Orca's website", "https://orca.gnome.org/", "states no licence: link only"),
        ("link", "The old Orca wiki (retired in 2024)", "https://wiki.gnome.org/Projects/Orca",
         "frozen and states no licence: link only"),
        ("link", "Orca users' mailing list", "https://www.freelists.org/list/orca", "a discussion list: link only"),
        ("link", "Debian wiki: accessibility", "https://wiki.debian.org/accessibility",
         "the Debian wiki's own licensing page says the licence of its content is unclear: link only"),
        ("link", "Ubuntu wiki: Accessibility", "https://wiki.ubuntu.com/Accessibility", "a stub page: link only"),
        ("link", "AT-SPI2, the Linux accessibility interface (freedesktop.org)",
         "https://www.freedesktop.org/wiki/Accessibility/AT-SPI2/", "a developers' wiki: link only")]),
    ("Web accessibility", "Making and testing accessible web pages and documents.", [
        ("key", "nonprofit:w3c_wcag22", "WCAG 2.2 (W3C)"),
        ("key", "nonprofit:w3c_understanding_wcag22", "Understanding WCAG 2.2 (W3C)"),
        ("key", "nonprofit:w3c_aria_apg", "The ARIA Authoring Practices Guide (W3C)"),
        ("key", "nonprofit:w3c_easy_checks", "Easy Checks: a first review of web accessibility (W3C)"),
        ("key", "guide:section508_gov", "Section508.gov (US government)"),
        ("link", "WebAIM articles", "https://webaim.org/articles/",
         "copyright of WebAIM, Utah State University: link only"),
        ("link", "WebAIM's Screen Reader User Surveys", "https://webaim.org/projects/",
         "copyright of WebAIM: link only")]),
    ("Questions and answers (reading only)", "Community question-and-answer books in the Kiwix library.", [
        ("word", "stack-exchange", "Stack Exchange how-to sites, reference only (not for AI training): User "
                                   "Experience has the accessibility questions; Ask Ubuntu, Super User and Unix and "
                                   "Linux cover screen readers on those systems"),
        ("link", "An Accessibility Stack Exchange", "https://stackexchange.com/sites",
         "no such site exists")]),
]
INDEX = X.index_maker("a11yc", GROUP, "Accessibility communities: a guide to the library",
                      "Accessibility communities", "A guide to the screen reader and accessibility communities "
                      "(NVDA, Orca, the Linux desktops, web accessibility) and their books in the library, with the "
                      "community sources that are links only.", SECTIONS, country="International")
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("a11yc", GROUP, guides=GUIDES, makers=MAKERS, words={
    "a11y-community": lambda: ["a11yc:index"] + [f"a11yc:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "a11yc_gnome_help": "help.gnome.org/gnome-help/a11y.html (checked at every build): \"This work is licensed under "
                        "a Creative Commons Attribution-ShareAlike 3.0 Unported License\"; no robots.txt rules "
                        "(checked 2026-11-22).",
    "a11yc_arch_wiki": "wiki.archlinux.org (checked at every build on the Accessibility page): \"Content is available "
                       "under GNU Free Documentation License 1.3 or later unless otherwise noted\"; robots.txt has no "
                       "rules against our reader and no AI rules (checked 2026-11-22).",
    "a11yc_kde_userbase": "userbase.kde.org (checked at every build on the Accessibility page): \"Content is available "
                          "under Creative Commons License SA 4.0 unless otherwise noted\"; no robots.txt (404) "
                          "(checked 2026-11-22).",
    "a11yc_index": "The index (a11yc:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("NVDA GitHub wiki (github.com/nvaccess/nvda/wiki)", "No licence is stated for the wiki and anyone may edit it; "
     "NV Access is moving its content into the NVDA repository, whose guides are built (atdoc:). Link-only from "
     "a11yc:index. Index: https://github.com/nvaccess/nvda/wiki"),
    ("Old Orca wiki (wiki.gnome.org/Projects/Orca)", "wiki.gnome.org was retired and frozen in 2024 and states no "
     "licence; it points to orca.gnome.org, which states none either. Orca's help is built (vision:orca_help). "
     "Index: https://wiki.gnome.org/Projects/Orca"),
    ("Debian wiki accessibility pages (wiki.debian.org/accessibility)", "The Debian wiki's own page "
     "DebianWiki/LicencingTerms says it is unclear which licence applies to its content; link-only. Index: "
     "https://wiki.debian.org/accessibility"),
    ("Ubuntu wiki Accessibility page (wiki.ubuntu.com/Accessibility)", "A stub with almost no content; link-only. "
     "Index: https://wiki.ubuntu.com/Accessibility"),
    ("Screen reader mailing lists (nvda.groups.io, freelists.org orca)", "Discussion lists: each message belongs to "
     "its writer; link-only. Index: https://nvda.groups.io/g/nvda"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
