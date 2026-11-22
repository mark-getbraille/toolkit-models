"""Blind and low-vision living for the reference library, in its own group "Reference, blind and low-vision living"
(the owner's request of 2026-11-22). Keys: vision-living (every book), vision:<name>.

The owner is blind. Much of this subject was already in the library, scattered over other groups (NVDA's guides,
liblouis, the ICEB rules of UEB, the NLS reference guides and player manuals, the ADA, the Rehabilitation Act, IDEA,
air travel rules, Social Security, Medicare, voting, fair housing, ODEP, Ticket to Work, the National Eye Institute,
the VA Blind Rehabilitation Service ...). This module does not copy those again: its first book is an INDEX that
gathers them by subject, with the new books below and the link-only sources, so the owner (and his offline
assistant) find everything in one place.

What this module builds, in plain words, each IN FULL:
  - vision:index, "Blind and low-vision living: a guide to the library": one page per subject (screen readers and
    magnification, braille, braille writer care and repair, orientation and mobility, daily living, rights and
    services, education and employment, low vision, deafblind, devices and their repair), each listing the books of
    the library by key with what they hold, the manual collections and picture packs, and the sources that are
    link-only, with the reason (facts and links only: CC0);
  - the GNOME Orca screen reader's help (help.gnome.org, written by Joanmarie Diggs, "Creative Commons Share Alike
    3.0": a share-alike book), every page: getting started, the Orca modifier, reading, flat review, structural
    navigation, tables, forms, documents, profiles, preferences and every command;
  - the National Library Service for the Blind and Print Disabled's own pages about its service (Library of
    Congress): who can enrol and how, BARD and the NLS players (information pages only: the owner chose not to have
    BARD downloads), braille education and braille on demand, music service, the US Currency Reader Program,
    services for blind, low-vision and deafblind readers and veterans, the network libraries, the laws and the FAQ;
  - the Bureau of Engraving and Printing's currency accessibility pages: the Meaningful Access Program, the free US
    Currency Reader Program (who may apply and how, the FAQ) and the mobile apps that identify bills;
  - the US Access Board's pages on accessible prescription drug container labels (the FDASIA section 904 best
    practices for braille, large print and talking labels);
  - the EEOC's "Visual Disabilities in the Workplace and the Americans with Disabilities Act" (questions and
    answers on hiring, accommodations and the law);
  - the Rehabilitation Services Administration's programme pages (US Department of Education): the
    Randolph-Sheppard Vending Facility Program (its eligibility, laws and resources), vocational rehabilitation,
    independent living services for older blind people, braille training and the Client Assistance Program;
  - vision:aph_museum_articles: the Museum of the American Printing House for the Blind's articles that APH itself
    marked with the Public Domain Mark on the Internet Archive (braille writers such as the Hall braillewriter, the
    Moon writer, talking book machines, the Optacon, CCTVs, canes, braille history): the text of each, or the
    subtitles of each museum video, checked item by item at every build. Only the museum's own items by APH or its
    director are taken (APH's mark on other people's work is not the author's own).

Not built (NOT_INCLUDED, link-only, each with its index address for the owner's Program Downloader): JAWS, ZoomText
and Fusion (Freedom Scientific), Narrator, VoiceOver and TalkBack guides (the makers' copyright), Be My Eyes, Seeing
AI and Aira, BANA's codes and tactile graphics guidelines, Hadley, APH, AFB, NFB, ACB, Perkins (its site refuses
programs) and the Perkins Brailler maintenance guides, HathiTrust (it refuses programs), the Helen Keller National
Center, the National Center on Deaf-Blindness, the FCC's deaf-blind equipment programme and SSA's blindness pages
(both refuse programs), ScripTalk, guide dog schools, Bookshare (the owner's choice) and others.

Licences: GNOME's help pages CC BY-SA 3.0 (the line checked on Orca's index page at every build); the government
pages are works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
APH's museum articles carry the Public Domain Mark that APH put on them (checked item by item at every build).
robots.txt of help.gnome.org (none), loc.gov (Crawl-delay 5, kept), bep.gov, access-board.gov, eeoc.gov, rsa.ed.gov
and archive.org allow the pages; none has AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/vision_living.py vision:index --out build/textbooks
  python3 textbooks/vision_living.py vision:orca_help --out build/textbooks --limit 5
  python3 textbooks/vision_living.py --list vision-living
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "vision"
GROUPS = {GROUP: "Reference, blind and low-vision living"}

# The licence of the APH museum articles (added to sources.ALLOWED as open): APH, their author, marked them with the
# Public Domain Mark 1.0 on the Internet Archive.
PDM = "Public domain (marked by its publisher, Public Domain Mark 1.0)"
PDM_URL = "https://creativecommons.org/publicdomain/mark/1.0/"
ALLOWED = {PDM: "open"}
CC0_INDEX = "CC0 1.0"


def page_list_book(group, name, title, subject, publisher, urls, pages, description, notice, units=(), **more):
    """A US government web guide of a fixed list of pages (no crawl beyond them): the first address is its source."""
    return K.us_web(group, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=notice, crawl=[(urls[0], 0)], urls=list(urls), pages=pages,
                    unit_rules=list(units), limit=len(urls) + 5, **more)


# ====================================================================== GNOME Orca help (CC BY-SA 3.0)

ORCA = "https://help.gnome.org/orca/"
ORCA_HELP = dict(
    K.WEB, name="orca_help", title="Orca Screen Reader help (GNOME)", group=GROUP, country="International",
    subject="Screen readers (Orca, Linux)", publisher="The GNOME Project (written by Joanmarie Diggs)",
    licence="CC BY-SA 3.0", licence_url="https://creativecommons.org/licenses/by-sa/3.0/",
    source=ORCA + "index.html", licence_page=ORCA + "index.html",
    licence_text=r"Creative Commons Share Alike 3\.0",
    description="The whole help of Orca, the free screen reader of the GNOME desktop on Linux, every page: "
                "introduction and getting started, setting up Orca, the Orca modifier, learn mode, reading, flat "
                "review, mouse review, structural navigation, tables, forms, live regions, documents, profiles, key "
                "bindings and keyboard layouts, notifications, Where Am I, every preference (speech, voice, braille, "
                "key echo, pronunciation, text attributes, table navigation, web) and every command.",
    notice="Orca help by Joanmarie Diggs and the GNOME Documentation Project, licensed under the Creative Commons "
           "Attribution-ShareAlike 3.0 licence (https://creativecommons.org/licenses/by-sa/3.0/); converted to an "
           "accessible format. A book made from it keeps the same licence.",
    content=(r"<article\b[^>]*>", r"</article>"), title_from=r'<h1 class="title">(.*?)</h1>',
    crawl=[(ORCA + "index.html", 2)], follow=r"^https://help\.gnome\.org/orca/(index|commands|preferences)\.html$",
    pages=r"^https://help\.gnome\.org/orca/[a-z_]+\.html$",
    unit_rules=[(r"/commands", "Commands"), (r"/preferences", "Preferences"), (r"/howto_", "How to"),
                (r".", "Getting started")],
    version="help.gnome.org/orca as published", limit=120)

# ====================================================================== NLS (Library of Congress)

NLS = "https://www.loc.gov/nls/"
NLS_PAGES = [NLS + p for p in (
    "how-to-enroll/", "how-to-enroll/apply-for-nls-services/", "how-to-enroll/enroll-for-music-service-and-materials/",
    "how-to-enroll/request-nls-equipment-for-nls-materials/", "how-to-enroll/sign-up-for-bard-and-bard-mobile/",
    "services-and-resources/catalog-and-bard/", "services-and-resources/braille-education/",
    "services-and-resources/braille-on-demand/", "services-and-resources/music-service-and-materials/",
    "services-and-resources/us-currency-reader-program/", "services-and-resources/overseas-services/",
    "who-we-serve/blind/", "who-we-serve/visually-impaired/", "who-we-serve/deafblind/", "who-we-serve/veterans/",
    "who-we-serve/family-friends-caregivers/", "who-we-are/overview/", "who-we-are/faq/",
    "who-we-are/laws-regulations/", "who-we-are/network-libraries/", "braille-200/")]
GUIDES = [ORCA_HELP, page_list_book(
    GROUP, "nls_services", "Talking books and braille from the National Library Service: who can enrol, BARD, "
    "players, braille and music (NLS)", "Library services for blind readers",
    "National Library Service for the Blind and Print Disabled (NLS), Library of Congress", NLS_PAGES,
    r"^https://www\.loc\.gov/nls/(how-to-enroll|services-and-resources|who-we-serve|who-we-are|braille-200)/"
    r"([a-z0-9-]+/)?$",
    "The NLS's own pages about its free service: who is eligible and how to apply, the music service, requesting a "
    "talking-book player, signing up for BARD and BARD Mobile and the catalogue (information pages only), braille "
    "education and braille on demand, the US Currency Reader Program, overseas service, its services for blind, "
    "low-vision and deafblind readers, veterans and families, an overview, the FAQ, the laws and regulations, the "
    "network of cooperating libraries, and Braille 200.",
    "From the National Library Service for the Blind and Print Disabled (NLS), Library of Congress: a US government "
    "work. To enrol or for help with a player, call your network library or NLS at 1-888-657-7323.",
    units=[(r"/how-to-enroll/", "Enrolling"), (r"/services-and-resources/", "Services"),
           (r"/who-we-serve/", "Who NLS serves"), (r".", "About NLS")])]

# ====================================================================== Bureau of Engraving and Printing

BEP = "https://www.bep.gov/services/currency-accessibility/"
BEP_PAGES = [BEP, BEP + "meaningful-access-program/", BEP + "us-currency-reader-program/",
             BEP + "us-currency-reader-program/us-currency-reader-program-faqs/",
             BEP + "us-currency-reader-program/us-currency-reader-application-form/", BEP + "mobile-applications/"]
GUIDES.append(page_list_book(
    GROUP, "bep_currency_access", "Telling US bills apart: the currency reader programme and accessible currency "
    "(Bureau of Engraving and Printing)", "Money identification", "Bureau of Engraving and Printing (US Department "
    "of the Treasury)", BEP_PAGES,
    r"^https://www\.bep\.gov/services/currency-accessibility/([a-z0-9-]+/)*$",
    "The Bureau of Engraving and Printing's currency accessibility pages: the Meaningful Access Program for blind "
    "and visually impaired people, the free US Currency Reader Program (who may apply, how to apply, the "
    "questions and answers) and the mobile applications that identify US bills.",
    "From the Bureau of Engraving and Printing (US Department of the Treasury): a US government work. Currency "
    "readers are free to eligible blind and visually impaired people in the US; the NLS takes applications too.",
    units=[(r"reader", "US Currency Reader Program"), (r".", "Currency accessibility")]))

# ====================================================================== US Access Board: prescription labels

AB = "https://www.access-board.gov/"
GUIDES.append(page_list_book(
    GROUP, "access_board_rx_labels", "Accessible prescription drug container labels: braille, large print and "
    "talking labels (US Access Board)", "Medication labels", "US Access Board",
    [AB + "rx.html", AB + "rx/pharma-convention.html", AB + "rx/fda-section-904.html"],
    r"^https://www\.access-board\.gov/rx(/[a-z0-9-]+)?\.html$",
    "The US Access Board's pages on making prescription drug container labels accessible to people who are blind, "
    "visually impaired or elderly: the working group under section 904 of the Food and Drug Administration Safety "
    "and Innovation Act, its best practices for pharmacies (braille, large print and auditory labels such as "
    "talking labels and RFID tags), and the pharmacies' commitments.",
    "From the US Access Board: a US government work. The best practices are advice for pharmacies, not rules; ask "
    "your pharmacy which accessible label it offers."))

# ====================================================================== EEOC

GUIDES.append(page_list_book(
    GROUP, "eeoc_visual_disabilities", "Visual disabilities in the workplace and the ADA (EEOC)",
    "Employment rights", "US Equal Employment Opportunity Commission (EEOC)",
    ["https://www.eeoc.gov/laws/guidance/visual-disabilities-workplace-and-americans-disabilities-act"],
    r"^https://www\.eeoc\.gov/laws/guidance/visual-disabilities-workplace-and-americans-disabilities-act$",
    "The EEOC's questions and answers on blindness and vision impairments at work under the Americans with "
    "Disabilities Act: when a vision impairment is a disability, what an employer may ask before and after a job "
    "offer, reasonable accommodations (screen readers, braille, magnifiers, guide dogs, flexible schedules and "
    "more), safety concerns and harassment.",
    "From the US Equal Employment Opportunity Commission: a US government work. General information, not legal "
    "advice; to file a charge, contact the EEOC (1-800-669-4000) within the time the law allows."))

# ====================================================================== Rehabilitation Services Administration

RSA = "https://rsa.ed.gov/about/programs/"
RS = RSA + "randolph-sheppard-vending-facility-program"
RSA_PAGES = [RS, RS + "/eigibility", RS + "/legislation-regulations-and-sub-regulatory-guidance", RS + "/resources",
             RSA + "vocational-rehabilitation-state-grants",
             RSA + "independent-living-services-for-older-individuals-who-are-blind", RSA + "braille-training",
             RSA + "client-assistance-program",
             RSA + "supported-employment-services-for-individuals-with-the-most-significant-disabilities"]
GUIDES.append(page_list_book(
    GROUP, "rsa_blind_programs", "Vocational rehabilitation, the Randolph-Sheppard programme and services for older "
    "blind people (Rehabilitation Services Administration)", "Rehabilitation and employment services",
    "Rehabilitation Services Administration (US Department of Education)", RSA_PAGES,
    r"^https://rsa\.ed\.gov/about/programs/[a-z0-9-]+(/[a-z0-9-]+)?$",
    "The Rehabilitation Services Administration's programme pages: the Randolph-Sheppard Vending Facility Program "
    "(blind vendors operating vending facilities on federal and other property: eligibility, the laws, regulations "
    "and guidance, resources), the state vocational rehabilitation programme, independent living services for "
    "older individuals who are blind, braille training, the Client Assistance Program and supported employment.",
    "From the Rehabilitation Services Administration (US Department of Education): a US government work. To apply "
    "for services, contact your state vocational rehabilitation agency or agency for the blind.",
    units=[(r"randolph", "Randolph-Sheppard Vending Facility Program"), (r".", "Rehabilitation programmes")]))

# ====================================================================== the index (facts and links only)

# Each subject: (title, introduction, [entries]). An entry is ("key", key, what it holds) for a book of the library,
# ("manuals", category key, what it holds) for a manual collection, ("pack", pack key, what it shows) for a picture
# pack, or ("link", title, address, why it is a link only).
SECTIONS = [
    ("Screen readers and magnification", "Screen readers, braille translation, keyboard commands, accessible "
     "documents and the web.", [
        ("key", "atdoc:nvda_user_guide", "NVDA User Guide (NV Access, GPL), the whole current guide"),
        ("key", "atdoc:nvda_key_commands", "NVDA Commands Quick Reference"),
        ("key", "atdoc:nvda_whats_new", "NVDA What's New, every release"),
        ("key", "atdoc:nvda_developer_guide", "NVDA Developer Guide"),
        ("key", "atdoc:nvda_addons_gpl2", "NVDA add-ons under GPL version 2, with their documentation"),
        ("key", "atdoc:nvda_addons_open", "NVDA add-ons under other open licences"),
        ("key", "vision:orca_help", "Orca Screen Reader help (GNOME, Linux), every page"),
        ("key", "atdoc:aem_center", "AEM Center guides: accessible formats, creating accessible documents, EPUB"),
        ("key", "guide:section508_gov", "Section508.gov: creating accessible documents, testing, buying accessible "
                                        "technology"),
        ("key", "nonprofit:w3c_wcag22", "WCAG 2.2, with Understanding WCAG and the WAI tutorials beside it"),
        ("key", "nonprofit:w3c_accessibility_fundamentals", "How people with disabilities use the web (W3C WAI)"),
        ("key", "nonprofit:w3c_epub_a11y_11", "EPUB Accessibility 1.1"),
        ("manuals", "release_notes", "Release notes of NVDA, Orca and BRLTTY in full"),
        ("link", "JAWS, ZoomText and Fusion documentation and training (Freedom Scientific, Vispero)",
         "https://support.freedomscientific.com/", "The maker's copyright: link-only; Program Downloader fetches "
                                                   "them for the owner's own use."),
        ("link", "Narrator guide (Microsoft)", "https://support.microsoft.com/",
         "Microsoft's copyright: link-only (search for \"Complete guide to Narrator\")."),
        ("link", "VoiceOver user guides for iPhone and Mac (Apple)", "https://support.apple.com/guide/",
         "Apple's copyright: link-only."),
        ("link", "TalkBack help (Google Android accessibility)", "https://support.google.com/accessibility/android/",
         "Google's copyright: link-only."),
        ("link", "Be My Eyes, Seeing AI and Aira (describer apps)", "https://www.bemyeyes.com/",
         "The companies' own help pages are copyright: link-only; their pictures are never used."),
     ]),
    ("Braille", "Braille codes, braille translation and learning braille.", [
        ("key", "pdf:iceb_rules_of_ueb_2024", "Rules of Unified English Braille, Third Edition 2024 (ICEB), whole and "
                                              "unchanged"),
        ("key", "pdf:braille_music_notation_1930", "Braille Music Notation (American Braille Press, 1930: old)"),
        ("key", "atdoc:liblouis_manual", "The liblouis manual (braille translation tables and programming)"),
        ("key", "atdoc:liblouisutdml_manual", "The liblouisutdml manual"),
        ("key", "atdoc:liblouis_tables", "Every liblouis braille table with its metadata"),
        ("key", "guide:nls_informational_publications", "NLS reference guides on braille, blindness and "
                                                        "disability (including braille instruction and equipment)"),
        ("key", "vision:nls_services", "NLS braille education, braille on demand and the music service"),
        ("key", "vision:aph_museum_articles", "APH Museum articles: braille history, braille writers, New York Point"),
        ("pack", "commons_braille_writing", "Pictures: braille writers, braille charts, numbers and music, Moon type "
                                            "and New York Point"),
        ("pack", "commons_disability", "Pictures: braille texts, refreshable braille displays, people reading "
                                       "braille"),
        ("link", "BANA codes (Nemeth, music, computer braille), Braille Formats and the Guidelines and Standards for "
                 "Tactile Graphics (Braille Authority of North America)", "https://www.brailleauthority.org/",
         "Free to download but copyright of BANA: link-only, for personal use."),
        ("link", "Hadley braille courses", "https://hadleyhelps.org/",
         "Hadley's copyright: link-only."),
        ("link", "Paths to Literacy (Perkins and TSBVI)", "https://www.pathstoliteracy.org/",
         "All rights reserved: link-only."),
     ]),
    ("Braille writer care and repair", "Perkins Braillers (the classic Howe Press model, the Next Generation and "
     "the SMART Brailler) and other braille writers: care, faults and where to have them repaired. No repair manual "
     "was found that the library may copy; the makers' manuals are listed as links in the manual collection.", [
        ("manuals", "vision_devices", "Braille writer, slate, display, notetaker, embosser, magnifier and talking "
                                      "device manuals (links), with the braille writer repair services"),
        ("manuals", "assistive_tech_repair", "Care and repair programmes for assistive devices (NLS, VA, state AT "
                                             "programmes)"),
        ("key", "vision:aph_museum_articles", "APH Museum articles on braille writers (the Hall braillewriter, the "
                                              "Moon writer and others) and other devices"),
        ("key", "elec:acl_assistive_technology", "State Assistive Technology Act programmes: device loans, reuse and "
                                                 "repair help"),
        ("pack", "commons_braille_writing", "Pictures: Perkins and other braille writers, manual embossers"),
        ("pack", "aph_museum_objects", "Pictures: the APH Museum's own items marked public domain (braille writers, "
                                       "the Moon writer)"),
        ("link", "Perkins Brailler support, parts and repair (Perkins Solutions)", "https://brailler.perkins.org/",
         "Perkins' copyright; perkins.org refuses programs: link-only, the owner fetches the manuals himself."),
        ("link", "Perkins Brailler Written Guide, Level 1 General Maintenance (on the Internet Archive)",
         "https://archive.org/details/written-guide-level-1-general-maintenance-guide-english",
         "No licence is given (Perkins' copyright): link-only, personal use."),
        ("link", "HathiTrust (old Howe Press and Perkins publications)", "https://catalog.hathitrust.org/",
         "It refuses programs (a challenge page): open it in a browser."),
     ]),
    ("Orientation and mobility", "Canes, guide dogs, crossing streets, transit and paratransit.", [
        ("key", "travel:access_board_prowag", "PROWAG: sidewalks, crossings, accessible pedestrian signals and "
                                              "detectable warnings"),
        ("key", "travel:access_board_vehicles", "Accessibility guidelines for buses, vans and rail cars"),
        ("key", "law:cfr_49_37_transportation_ada", "ADA transportation rules, including paratransit (49 CFR 37)"),
        ("key", "law:cfr_14_382_air_travel_disability", "Air Carrier Access Act rules (14 CFR 382), including "
                                                        "service animals and assistance"),
        ("key", "guide:ada_gov_guidance", "ADA.gov guidance, including service animals"),
        ("pack", "commons_mobility_deafblind", "Pictures: orientation and mobility training, sighted guiding, "
                                               "mobility canes, guide horses"),
        ("pack", "commons_crosswalks_signals", "Pictures: crossings, accessible pedestrian signals and push buttons"),
        ("pack", "tapad_tactile_paving", "Pictures: tactile paving and its condition"),
        ("link", "Guide dog schools (for example Guide Dogs for the Blind, The Seeing Eye)",
         "https://www.guidedogs.com/", "The schools' copyright: link-only."),
        ("link", "FTA ADA paratransit guidance", "https://www.transit.dot.gov/regulations-and-guidance/civil-rights-ada/"
                                                 "americans-disabilities-act", "transit.dot.gov refuses programs: "
                                                                               "link-only."),
     ]),
    ("Daily living", "Labelling, money, medicines, cooking, clothing and the home.", [
        ("key", "vision:bep_currency_access", "The free US Currency Reader Program and accessible currency"),
        ("key", "vision:access_board_rx_labels", "Accessible prescription labels: braille, large print, talking labels"),
        ("key", "civic:hud_doj_reasonable_modifications", "Home modifications under the Fair Housing Act"),
        ("pack", "commons_money_sides", "Pictures: US and Canadian money with how to tell it by touch or low vision"),
        ("pack", "commons_tactile_access", "Pictures: tactile graphics and models, large print, reading machines"),
        ("link", "ScripTalk talking prescription labels (En-Vision America)", "https://www.envisionamerica.com/",
         "The maker's copyright: link-only."),
        ("link", "Daily living courses and guides (Hadley, AFB VisionAware)", "https://hadleyhelps.org/",
         "Copyright: link-only."),
     ]),
    ("Rights and services", "The laws, benefits and services for blind people.", [
        ("key", "law:us_code_ada", "The Americans with Disabilities Act"),
        ("key", "law:us_code_rehabilitation_act", "The Rehabilitation Act (sections 501, 503, 504 and 508)"),
        ("key", "law:cfr_45_84_section_504_hhs", "Section 504 regulations (HHS)"),
        ("key", "law:cfr_36_1194_section_508_standards", "Section 508 standards"),
        ("key", "law:us_code_idea", "The Individuals with Disabilities Education Act"),
        ("key", "law:cfr_34_300_idea_regulations", "The IDEA regulations"),
        ("key", "law:us_code_fair_housing", "The Fair Housing Act"),
        ("key", "civic:hud_doj_reasonable_accommodations", "Reasonable accommodations under the Fair Housing Act, "
                                                           "including assistance animals"),
        ("key", "civic:eac_voters", "Accessible voting and your rights as a voter (EAC)"),
        ("key", "code:usc:52", "The US Code, title 52 (voting, including the Help America Vote Act)"),
        ("key", "code:usc:20", "The US Code, title 20 (education, including the Randolph-Sheppard Act)"),
        ("key", "code:usc:02", "The US Code, title 2 (the Library of Congress, including the NLS)"),
        ("key", "vision:rsa_blind_programs", "Vocational rehabilitation, Randolph-Sheppard and services for older "
                                             "blind people"),
        ("key", "law:us_code_social_security_benefits", "The Social Security Act: SSDI and SSI"),
        ("key", "law:cfr_20_416_supplemental_security_income", "SSI regulations for the aged, blind and disabled"),
        ("key", "ben:poms:di-1", "SSA's POMS, disability insurance (DI), with the statutory blindness rules"),
        ("key", "ben:poms:si", "SSA's POMS, Supplemental Security Income (SI)"),
        ("key", "work:ticket_to_work", "Ticket to Work and work incentives"),
        ("key", "help:medicare_guides", "Medicare.gov: what Medicare covers (eye exams, glasses after cataract "
                                        "surgery)"),
        ("key", "vision:nls_services", "NLS Talking Books and BARD (information pages)"),
        ("key", "eyes:va_blind_rehabilitation", "VA Blind Rehabilitation Service"),
        ("key", "legal:adata_factsheets", "ADA National Network fact sheets"),
        ("link", "SSA Red Book and \"If You Are Blind Or Have Low Vision\"", "https://www.ssa.gov/redbook/",
         "Public domain, but ssa.gov refuses programs: link-only."),
        ("link", "Bookshare", "https://www.bookshare.org/", "Left out by the owner's choice."),
     ]),
    ("Education and employment", "Accessible STEM, careers and workplace accommodations.", [
        ("key", "vision:eeoc_visual_disabilities", "Visual disabilities in the workplace and the ADA (EEOC)"),
        ("key", "law:cfr_29_1630_ada_employment", "ADA Title I regulations (employment)"),
        ("key", "work:odep", "ODEP: accommodations, technology and employment supports"),
        ("key", "atdoc:aem_center", "Accessible educational materials, NIMAS and NIMAC"),
        ("key", "parent:cpir_parent_guides", "Parent guides to special education (visual impairment included)"),
        ("key", "pub:eric_open:vision", "Open ERIC papers on blindness and low vision"),
        ("link", "Job Accommodation Network (askjan.org)", "https://askjan.org/",
         "Its robots.txt shuts out AI readers: link-only."),
        ("link", "AFB CareerConnect and APH's educational products", "https://www.afb.org/",
         "Copyright: link-only."),
     ]),
    ("Low vision", "Eye conditions, magnifiers, lighting and large print.", [
        ("key", "eyes:nei_eye_health", "National Eye Institute: eye conditions, low vision and vision "
                                       "rehabilitation"),
        ("key", "eyes:cdc_vision_health", "CDC Vision Health"),
        ("key", "eyes:nhs_eyes", "NHS eye conditions"),
        ("key", "pub:europepmc_reviews:vision", "Open-access review articles on blindness and low vision"),
        ("pack", "commons_eye_care", "Pictures: magnifying glasses, loupes, reading glasses, Snellen charts"),
        ("pack", "commons_assistive_devices", "Pictures: braille embossers, talking clocks, monoculars"),
     ]),
    ("Deafblind", "Equipment, services and tactile communication.", [
        ("key", "vision:nls_services", "NLS services for deafblind readers"),
        ("pack", "commons_mobility_deafblind", "Pictures: deafblind people and the Lorm hand alphabet"),
        ("link", "National Deaf-Blind Equipment Distribution Program (iCanConnect, FCC)",
         "https://www.fcc.gov/general/national-deaf-blind-equipment-distribution-program",
         "fcc.gov refuses programs: link-only."),
        ("link", "Helen Keller National Center", "https://www.helenkeller.org/", "Copyright: link-only."),
        ("link", "National Center on Deaf-Blindness", "https://www.nationaldb.org/",
         "No open licence was found: link-only."),
     ]),
    ("Devices and their repair", "Talking-book players, braille displays, magnifiers and where to get them "
     "repaired.", [
        ("key", "elec:nls_players", "NLS talking-book players: the DA2 user guide and compatible players"),
        ("key", "elec:nls_dtbm_library_manual", "The NLS digital talking-book machine library manual"),
        ("key", "elec:nls_dtbm_service_manual", "The NLS digital talking-book machine service manual"),
        ("key", "elec:va_blind_rehabilitation", "VA Blind Rehabilitation: who supplies and repairs veterans' devices"),
        ("manuals", "vision_devices", "Manuals of braille writers, displays, notetakers, embossers, magnifiers and "
                                      "talking devices (links)"),
        ("manuals", "accessibility", "Accessibility device manuals at the Internet Archive"),
     ]),
]


def key_exists(key):
    """True when key is a book key of the library (a sources.py record, a key of a more_refs module, a publication or
    a benefits manual piece). Imported here, not at the top: sources imports this module at its end."""
    import sources
    import more_refs
    prefix, _, name = key.partition(":")
    tables = {"guide": sources.GOV_GUIDES, "law": sources.LAWS + sources.LAWS_MORE, "pdf": sources.PDF_DOCS,
              "nonprofit": sources.NONPROFIT}
    if prefix in tables:
        return any(e["name"] == name for e in tables[prefix])
    if prefix == "pub":
        return key in sources.expand_keys(["publications"])
    if prefix == "ben":
        return key in sources.expand_keys(["benefits"])
    m = more_refs.module_for(key)
    return bool(m) and key in m.COLLECTION.own_keys()


def index_sign(name):
    """The weekly sign of the index: a fingerprint of its subjects and entries (it changes only when this file
    does)."""
    return K.sha(SECTIONS)


def index_book(name, work, cache=None, left_out=None, limit=None):
    """The index book: one page per subject listing its books (by key, with what each holds), manual collections,
    picture packs and link-only sources. A key the library no longer has is left out and said in left_out."""
    import build_textbooks as B
    book = K.new_book("vision_index", "Blind and low-vision living: a guide to the library", "Blind and low-vision "
                      "living", GROUP, "Digital Accessibility Toolkit (an index of the library)", CC0_INDEX,
                      K.CC0_URL, "https://github.com/mark-getbraille/toolkit-models",
                      "A guide to everything in the library about living blind or with low vision, one page per "
                      "subject: screen readers and magnification, braille, braille writer care and repair, "
                      "orientation and mobility, daily living, rights and services, education and employment, low "
                      "vision, deafblind, and devices and their repair. Each page lists the books by key with what "
                      "each holds, the manual collections, the picture packs and the sources that are links only, "
                      "with the reason.",
                      "Facts and links only (CC0). Each book listed has its own licence, shown in that book.",
                      country="International", changes="an index written for the toolkit")
    for number, (title, intro, entries) in enumerate(SECTIONS, 1):
        if limit and len(book.pages) >= limit:
            break
        books, manuals, packs, links = [], [], [], []
        for kind, what, words, *more in entries:
            if kind == "key":
                if not key_exists(what):
                    left_out.append({"title": what, "reason": "The library has no book with this key now."})
                    continue
                books.append(f"<li>{B.esc(words)} (key {B.esc(what)})</li>")
            elif kind == "manuals":
                manuals.append(f"<li>{B.esc(words)} (manual collection {B.esc(what)})</li>")
            elif kind == "pack":
                packs.append(f"<li>{B.esc(words)} (picture pack {B.esc(what)})</li>")
            else:
                links.append(f"<li>{B.esc(what)}: {B.esc(words)}. {B.esc(more[0])}</li>")
        body = f"<p>{B.esc(intro)}</p>"
        for head, items in (("Books in the library", books), ("Manual collections", manuals),
                            ("Picture packs (for the picture describer)", packs),
                            ("Links only (open them in a browser or with Program Downloader)", links)):
            if items:
                body += f"<h2>{head}</h2><ul>{''.join(items)}</ul>"
        book.pages.append(B.Page(f"part-{number}-{B.slug(title, 40)}", title, body, number, ""))
    return book


# ====================================================================== APH Museum articles (Public Domain Mark)

IA_SEARCH = "https://archive.org/advancedsearch.php"
APH_QUERY = ('collection:aphmigel AND mediatype:texts AND licenseurl:("https://creativecommons.org/publicdomain/mark/1.0/" '
             'OR "http://creativecommons.org/publicdomain/mark/1.0/")')


# Only APH's own writing is taken: the museum's articles (identifiers "museum-...") whose creator is APH or its
# museum's director (Mike Hudson, in the spellings the collection uses). The collection also marks other people's work (AFB slides, Helen Keller's and John Macy's
# writings, letters, scrapbooks): APH's mark on those is not the author's own, so they are left out.
APH_AUTHORS = re.compile(r"^(American Printing House for the Blind|M[Ii]ke Hudson|Mic(ha|he)al Hudson)$")


def aph_items(cache=None):
    """[(identifier, title, date)] of the APH Museum's Internet Archive texts marked with the Public Domain Mark and
    written by APH itself (its "museum-" articles by APH_AUTHORS; loan agreements, presentations and scrapbooks
    that quote others are left out)."""
    import build_textbooks as B
    q = urllib.parse.urlencode([("q", APH_QUERY), ("fl[]", "identifier"), ("fl[]", "title"), ("fl[]", "date"),
                                ("fl[]", "creator"), ("rows", "1000"), ("sort[]", "identifier asc"),
                                ("output", "json")])
    docs = json.loads(B.fetch(f"{IA_SEARCH}?{q}", None))["response"]["docs"]
    return [(d["identifier"], str(d.get("title") or d["identifier"]), str(d.get("date") or "")[:10]) for d in docs
            if d["identifier"].startswith("museum-") and aph_own(d.get("creator"))]


def aph_own(creator):
    """True when an item's creator (a name or a list of names) is APH or its museum director alone."""
    names = creator if isinstance(creator, list) else [creator or ""]
    return bool(names) and all(APH_AUTHORS.match(str(n).strip()) for n in names)


def aph_sign(name):
    """The weekly sign of the APH book: a fingerprint of the list of marked items."""
    return K.sha(aph_items())


def aph_book(name, work, cache=None, left_out=None, limit=None):
    """The APH Museum's public-domain-marked articles, one page each, from each item's text file; an item whose
    metadata no longer carries the Public Domain Mark, or that has no text file, is left out (said in left_out)."""
    import build_textbooks as B
    if not K.readable(IA_SEARCH, cache):
        left_out.append({"title": "APH Museum articles", "reason": "archive.org's robots.txt does not allow it."})
        return None
    book = K.new_book("vision_aph_museum_articles", "Museum of the American Printing House for the Blind: articles "
                      "marked public domain", "History of blindness technology and braille", GROUP,
                      "Museum of the American Printing House for the Blind (APH)", PDM, PDM_URL,
                      "https://archive.org/details/aphmigel",
                      "The articles, museum notes and how-tos of the APH Museum that APH itself marked with the "
                      "Public Domain Mark on the Internet Archive: braille writers (such as the Hall braillewriter "
                      "and the Moon writer), talking book machines and records, the Optacon, CCTVs, canes, braille "
                      "history, tactile and teaching devices, and caring for museum objects. One page per article.",
                      "From the Museum of the American Printing House for the Blind, which marked these items with "
                      "the Public Domain Mark 1.0 on the Internet Archive (checked item by item at every build). The "
                      "text is the Internet Archive's reading of each scan, or the subtitles of each museum video, so "
                      "it may hold reading errors. Old "
                      "devices are history: today's models and advice differ.",
                      changes="each item's text made into a web page")
    for ident, title, date in aph_items(cache):
        if limit and len(book.pages) >= limit:
            break
        try:
            meta = json.loads(B.fetch(f"https://archive.org/metadata/{ident}", cache))
        except (urllib.error.URLError, OSError, ValueError):
            left_out.append({"title": title, "reason": "Its record could not be read."})
            continue
        if "publicdomain/mark" not in str((meta.get("metadata") or {}).get("licenseurl", "")):
            left_out.append({"title": title, "reason": "It no longer carries the Public Domain Mark."})
            continue
        files = [f.get("name", "") for f in meta.get("files") or []]
        text_file = next((f for f in files if f.endswith("_djvu.txt")), "") or \
            next((f for f in files if f.endswith(".srt")), "")        # a museum video's own subtitles
        if not text_file:
            left_out.append({"title": title, "reason": "It has no text file or subtitles."})
            continue
        url = f"https://archive.org/download/{ident}/{urllib.parse.quote(text_file)}"
        try:
            text = B.fetch(url, cache)
        except (urllib.error.URLError, OSError):
            left_out.append({"title": title, "reason": "Its text could not be read."})
            continue
        if text_file.endswith(".srt"):
            text = srt_text(text)
        if len(text.split()) < 20:
            left_out.append({"title": title, "reason": "Its text is too short (a picture or a recording)."})
            continue
        head = K.dl([("Item", f"https://archive.org/details/{ident}"), ("Date", date)])
        book.pages.append(B.Page(B.slug(ident, 60), title, head + K.text_html(text), 0, "Articles"))
        book.originals.append({"url": url, "kind": "txt"})
    book.pages.sort(key=lambda p: p.title.lower())
    return book


def srt_text(srt):
    """The words of a subtitle file (.srt) as running paragraphs: cue numbers and times dropped, a paragraph about
    every ten cues."""
    cues = [" ".join(ln.strip() for ln in block.splitlines()
                     if ln.strip() and not ln.strip().isdigit() and "-->" not in ln)
            for block in re.split(r"\n\s*\n", srt.replace("\r", ""))]
    cues = [c for c in cues if c]
    return "\n\n".join(" ".join(cues[i:i + 10]) for i in range(0, len(cues), 10))


MAKERS = {"index": (index_book, index_sign), "aph_museum_articles": (aph_book, aph_sign)}

COLLECTION = K.Collection(
    "vision", GROUP, guides=GUIDES, makers=MAKERS,
    words={"vision-living": lambda: ["vision:index"] + [f"vision:{g['name']}" for g in GUIDES] +
           ["vision:aph_museum_articles"]})

LICENCE_LINES = {
    "vision_orca_help": "help.gnome.org/orca/index.html (checked at every build): \"License: Creative Commons Share "
                        "Alike 3.0\"; help.gnome.org has no robots.txt rules (checked 2026-11-22).",
    "vision_us_government": "loc.gov/nls, bep.gov, access-board.gov, eeoc.gov and rsa.ed.gov: works of the US "
                            "government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build); "
                            "robots.txt allows the pages, no AI rules; loc.gov asks a 5-second pause, which the "
                            "builder keeps (checked 2026-11-22).",
    "vision_aph_museum": "archive.org collection aphmigel: each item read is marked by APH, its uploader and author, "
                         "with the Public Domain Mark 1.0 (licenseurl checked item by item at every build); about "
                         "245 of its 11,493 items' texts carried it on 2026-11-22, of which about 80 are the museum's own articles "
                         "(\"museum-\" items with APH or its museum director as creator); the others (other people's "
                         "work, presentations, agreements, scrapbooks) are left out.",
    "vision_index": "The index of the library (vision:index) is the toolkit's own list of facts and links, CC0.",
}

NOT_INCLUDED = [
    ("JAWS, ZoomText and Fusion user guides and training (Freedom Scientific, Vispero)", "The maker's copyright; "
     "link-only for the owner's Program Downloader. Index: https://support.freedomscientific.com/"),
    ("Narrator, VoiceOver and TalkBack user guides (Microsoft, Apple, Google)", "The makers' copyright; link-only. "
     "Index: https://support.apple.com/guide/ and https://support.google.com/accessibility/android/"),
    ("Be My Eyes, Seeing AI and Aira help pages", "The companies' copyright; link-only. Index: "
     "https://www.bemyeyes.com/"),
    ("BANA's Nemeth, music and computer braille codes, Braille Formats and the Guidelines and Standards for Tactile "
     "Graphics", "Free to download but copyright of the Braille Authority of North America (no open licence on "
     "brailleauthority.org, checked 2026-11-22): personal use, link-only. Index: https://www.brailleauthority.org/"),
    ("Hadley courses (braille, daily living, technology)", "Hadley's copyright; link-only. Index: "
     "https://hadleyhelps.org/"),
    ("Perkins School for the Blind, Perkins Solutions and the Perkins Archives (brailler manuals, parts guides, "
     "archive photos)", "www.perkins.org answers programs \"403\" (checked 2026-11-22) and its manuals are Perkins' "
     "copyright; the Perkins Brailler maintenance guide on the Internet Archive carries no licence. Link-only for "
     "the owner to fetch himself. Index: https://brailler.perkins.org/ and https://archive.org/details/"
     "written-guide-level-1-general-maintenance-guide-english"),
    ("Old Howe Press and Perkins braille writer service manuals (Internet Archive and HathiTrust)", "None was found on the Internet Archive (searched "
     "2026-11-22: brailler, braillewriter, braille writer repair, Perkins brailler); HathiTrust answers programs with "
     "a challenge page, so it was not searched by program. Index: https://catalog.hathitrust.org/"),
    ("American Printing House for the Blind (APH) product guides, AFB, NFB and ACB publications", "Copyright of each "
     "organisation; link-only (APH's own public-domain-marked museum articles are built: "
     "vision:aph_museum_articles). Index: https://www.aph.org/ and https://www.afb.org/"),
    ("Helen Keller National Center and the National Center on Deaf-Blindness", "No open licence was found on "
     "helenkeller.org or nationaldb.org; link-only. Index: https://www.helenkeller.org/ and "
     "https://www.nationaldb.org/"),
    ("Social Security: the Red Book and \"If You Are Blind Or Have Low Vision: How We Can Help\"", "Public domain, "
     "but www.ssa.gov answers programs \"403\" (robots.txt included, checked 2026-11-22); the only Internet Archive "
     "copy found of the Red Book is the 1999 edition, too old. SSA's POMS (ben:poms) and the SSI rules are built. "
     "Index: https://www.ssa.gov/redbook/"),
    ("ScripTalk talking prescription labels (En-Vision America)", "The maker's copyright; link-only (the Access "
     "Board's best practices are built: vision:access_board_rx_labels). Index: https://www.envisionamerica.com/"),
    ("Guide dog schools' handbooks (Guide Dogs for the Blind, The Seeing Eye and others)", "The schools' copyright; "
     "link-only. Index: https://www.guidedogs.com/"),
    ("The U.S. Currency Education Program's denomination pages (uscurrency.gov)", "A Federal Reserve Board "
     "programme whose pages were not confirmed as US government works; its facts on large numerals are in the "
     "money picture pack, and the Bureau of Engraving and Printing's own pages are built (vision:bep_currency_access). "
     "Index: https://www.uscurrency.gov/denominations"),
    ("BARD downloads and Bookshare", "Left out by the owner's choice (the NLS information pages are built: "
     "vision:nls_services). Index: https://nlsbard.loc.gov/ and https://www.bookshare.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
