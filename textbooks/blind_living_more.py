"""More books for blind and low-vision living, in the same group as vision_living.py: "Reference, blind and
low-vision living" (the owner's request of 2026-11-23: fill this area further). Keys: blind:<name>. Request words by
theme: blind-nls, blind-services, blind-mobility, blind-daily-living, blind-screen-readers, blind-braille,
blind-history, and blind-living for every book of this module (vision-living stays the word of vision_living.py).

The owner is blind and a braille transcriber. The area's index, vision:index ("Blind and low-vision living: a guide
to the library", in vision_living.py), lists these books with the ones the library already had (NVDA, Orca,
liblouis, the NLS pages and reference guides, the VA Blind Rehabilitation Service pages, the National Eye Institute,
the IRS publications 501, 502, 554 and 907, the ADA guidance on service animals, the Access Board's standards,
Helen Keller's The Story of My Life, Harry Best's The Blind, Moon's Light for the Blind ...). Nothing here repeats
them.

What this module builds, in plain words, each IN FULL:
  blind-nls        the Library of Congress's own braille transcribing course books, read from the Internet
                   Archive's copies of the APH M.C. Migel Library: the Instruction Manual for Braille Transcribing in
                   its 1961, 1971 (1977 printing), 1984 and 2000 editions (the literary braille course of their day,
                   English Braille American Edition, before UEB: history for transcribers), An Introduction to
                   Braille Mathematics (1978, the Nemeth Code course), the Dictionary of Braille Music Signs (1979)
                   and That All May Read (1983, the history and practice of library service to blind people);
  blind-services   the VA's directive on blind and visual impairment rehabilitation (VHA Directive 1174, from
                   va.gov), Coordinated Services for Blinded Veterans (1991), Occupations of Totally Blinded
                   Veterans (1956, as history), the Rehabilitation Services Administration's Services to the Blind
                   (1973), the Office of Education's pamphlet on blind and partially seeing children (1933) and IRS
                   Publication 524 (the credit for the elderly or the disabled);
  blind-mobility   Dorothy Harrison Eustis's article "The Seeing Eye" (1927), which started guide dog work in America
                   (the mobility books of other groups are listed in the index: PROWAG, the ADA's service animal
                   rules, Levy's and Villey's chapters on finding one's way);
  blind-daily-living  Head Start's guide for teachers and parents of blind and visually impaired preschoolers (1978:
                   self-help, motor and social skills, the classroom and the home);
  blind-screen-readers  the BRLTTY Reference Manual and BrlAPI Reference Manual, and BRLTTY's guides (commands, key
                   tables, text and contraction tables, devices, Linux, Windows, Android, and the key bindings of
                   every braille display it supports): GNU LGPL 2.1 or later, share-alike books;
  blind-braille    old braille code books and the "war of the dots" (all public domain, published before 1931):
                   William B. Wait's Key to the New York Point System (1908) and his history of New York Point (1892),
                   The Uniform Type Question (1915), the Uniform Type Committee's fifth report (1915), New York Point
                   or Braille? (1909), Revised Braille and How to Learn It in Ten Lessons (1924), the Rules for Revised
                   Braille Grade 2 (1924), Robert Irwin's study of Grade 1 1/2 and Grade 2 (1929), One Hundred Years of
                   Braille Reading (1929), and the VA's Introductory Notes on the Braille System (1959);
  blind-history    Helen Keller's The World I Live In (1908), Optimism (1903), The Song of the Stone Wall (1910), Out
                   of the Dark (1913), My Religion (1927) and Midstream (1929); Laura Bridgman's life by Maud Howe
                   Elliott and Florence Howe Hall (1903) and by Mary Swift Lamson (1878), and Samuel Gridley Howe's
                   account of her (1843); W. Hanks Levy's Blindness and the Blind (1872), T. R. Armitage's The
                   Education and Employment of the Blind (1886), Pierre Villey's The World of the Blind (1930); the
                   Perkins Institution's annual reports from 1833 to 1930 (Howe's reports among them); the Outlook
                   for the Blind, 1927 to 1930; the Louis Braille centenary at Paris (1909, in French); a 1916 article
                   on a blind proofreader; the Census Bureau's The Blind in the United States, 1910; and the VA's
                   history of its Blind Rehabilitation Service (1998).

Every old book says plainly that its words and many of its ideas about blind people are those of its day, and that
old braille codes are not today's (UEB in the US since 2016; BANA's codes for mathematics, music and formats).

Not built (NOT_INCLUDED, link-only, each with its index address): the NFB's current braille transcribing and
proofreading courses (NLS handed its certification to the National Federation of the Blind; copyright), the Outlook
for the Blind before 1927 (the Internet Archive's records give no year, so the builder cannot confirm the date),
1931 to 1963 books without evidence of non-renewal (Cooking and Sewing for Blind Students 1931, the 1930s guide dog
books), books whose status is not clear (Techniques for Eating 1981, Preprimer Cooking 1973, the 1975 Workshop on
Low Vision Mobility, Braille Into the Next Millennium 2000, Introduction to Braille Music Transcription 1974 with
other publishers' music), Social Security's old booklets (out of date), the Speech Dispatcher and eSpeak NG manuals
(only on GitHub, which refuses programs), the FHWA/NCHRP guide to accessible pedestrian signals (copyright), and two
government reports whose scans have no text layer (the 1969 folding cane report and the VA's 1975 Instructional
Manual for Visual Skills).

Licences: the Library of Congress and VA books are US government publications: written by government staff (17
U.S.C. 105) and printed without a copyright notice; those before 1989 are also public domain because a work
published in the US without a notice then lost its copyright (17 U.S.C. 405; the line checked on copyright.gov at
every build, and the first pages of each PDF must name the Library of Congress, or the Department of Health,
Education and Welfare, and print no copyright line). The
old books: published before 1931 (the builder checks each item's year on the Internet Archive at every build).
BRLTTY's documentation: GNU LGPL 2.1 or later (the line checked on the manual's licence page at every build).
robots.txt of archive.org, va.gov, irs.gov and brltty.app (none) allow the files; no AI rules (checked 2026-11-23).

Run from the repository's folder:
  python3 textbooks/blind_living_more.py blind:keller_world_i_live_in_1908 --out build/textbooks --limit 3
  python3 textbooks/blind_living_more.py --list blind-living
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import vision_living as V  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = V.GROUP                        # "vision": the same group as vision_living.py
GROUPS = dict(V.GROUPS)                # {"vision": "Reference, blind and low-vision living"}
PREFIX = "blind"

# ====================================================================== licences

# A US government publication printed without a copyright notice before 1 March 1989 (the same words as
# approtech.py, so sources.ALLOWED has one entry for it).
NO_NOTICE = "Public domain (US government publication without a copyright notice, before 1989)"
NO_NOTICE_URL = "https://www.copyright.gov/title17/92chap4.html#405"
NO_NOTICE_PAGE = "https://www.copyright.gov/title17/92chap4.html"
NO_NOTICE_TEXT = r"Omission of notice on certain copies"
# A later US government publication, written by its staff, with no copyright notice (peace_corps.py's words).
GOV_NO_NOTICE = "Public domain (US government publication without copyright notice)"
LGPL = "LGPL-2.1-or-later"
LGPL_URL = "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html"
ALLOWED = {NO_NOTICE: "open", GOV_NO_NOTICE: "open"}

# The first twelve pages of a Library of Congress PDF must name the Library of Congress and print no copyright line
# ("Copyright 1984" or "Copyright by ..."): checked at every build by build_textbooks.pdfdoc_book.
LOC_FRONT = r"(?is)^(?!.*copyright\s*(?:©|\(c\))?\s*(?:19\d\d|20\d\d|by)).*library\s+of\s+congress"
HEW_FRONT = r"(?is)^(?!.*copyright\s*(?:©|\(c\))?\s*(?:19\d\d|by)).*health,\s*education,?\s*and\s+welfare"

SCAN = ("Read from the Internet Archive's copy (from the M.C. Migel Library of the American Foundation for the Blind, "
        "scanned for the American Printing House for the Blind): the machine-read text has the scanner's mistakes, "
        "and braille cells and pictures are described only by their captions. ")
OLD_BRAILLE = ("This is an old braille course: it teaches English Braille American Edition (EBAE) and the rules of "
               "its day. Since 2016 the US uses Unified English Braille (UEB), with BANA's Braille Formats and its "
               "Nemeth and music codes; check every rule against the current codes before transcribing. Kept for "
               "transcribers as the history of the code and of the course. ")
LOC_WORDS = ("Published by the Library of Congress (its Division for the Blind, later the National Library Service "
             "for the Blind and Physically Handicapped), a US government agency, with no copyright notice; written "
             "by its staff, whose works are public domain (17 U.S.C. 105), and a work published in the US without a "
             "notice before 1 March 1989 also lost any copyright (17 U.S.C. 405). ")
VA_WORDS = "A work of the US Department of Veterans Affairs (Veterans Administration): public domain (17 U.S.C. 105). "


def _loc(name, title, subject, archive, year, description, notice="", licence=NO_NOTICE):
    """One Library of Congress (NLS) publication read whole from its Internet Archive copy: printed without a
    copyright notice, its first pages checked at every build (LOC_FRONT)."""
    entry = K.us_pdf(GROUP, name=name, title=title, subject=subject, archive=archive, published=str(year),
                     publisher="Library of Congress, National Library Service for the Blind and Physically "
                               "Handicapped (NLS)",
                     version=f"{year} edition (Internet Archive item {archive})", description=description,
                     licence=licence, pdf_licence_text=LOC_FRONT, notice=LOC_WORDS + SCAN + notice)
    if licence == NO_NOTICE:
        entry.update(licence_url=NO_NOTICE_URL, licence_page=NO_NOTICE_PAGE, licence_text=NO_NOTICE_TEXT)
    return entry


def _fed(name, title, subject, archive, year, publisher, description, notice=""):
    """One other federal publication (Office of Education, Census Bureau) written by government staff, read whole from
    its Internet Archive copy (a US government work)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, archive=archive, published=str(year),
                    publisher=publisher, version=f"{year} (Internet Archive item {archive})",
                    description=description, notice=f"A work of the US government ({publisher}): public domain (17 "
                    "U.S.C. 105). " + SCAN + notice)


def _hew(name, title, subject, archive, year, publisher, description, notice=""):
    """One Department of Health, Education and Welfare publication read whole from its Internet Archive copy:
    published by the department with no copyright notice before 1989, so public domain (NO_NOTICE); its first
    pages must name the department and print no copyright line (HEW_FRONT)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, archive=archive, published=str(year),
                    publisher=publisher, version=f"{year} (Internet Archive item {archive})", description=description,
                    licence=NO_NOTICE, licence_url=NO_NOTICE_URL, licence_page=NO_NOTICE_PAGE,
                    licence_text=NO_NOTICE_TEXT, pdf_licence_text=HEW_FRONT,
                    notice="Published by the US Department of Health, Education and Welfare, a US government "
                           "department, with no copyright notice: a work published in the US without a notice before "
                           "1978 entered the public domain at once, and one published from 1978 to 1 March 1989 lost "
                           "its copyright unless it was registered within five years and the notice added (17 U.S.C. "
                           "405). " + SCAN + notice)


def _va(name, title, subject, archive, year, publisher, description, notice=""):
    """One VA (or other federal) publication read whole from its Internet Archive copy (a US government work)."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, archive=archive, published=str(year),
                    publisher=publisher, version=f"{year} (Internet Archive item {archive})",
                    description=description, notice=VA_WORDS + SCAN + notice)


# ====================================================================== blind-nls: Library of Congress braille books

NLS_BOOKS = [
    _loc("nls_braille_transcribing_manual_1961", "Instruction Manual for Braille Transcribing, Second Edition (Maxine "
         "B. Dorf and Earl R. Scharry, Library of Congress, 1961)", "Braille transcribing (course, history)",
         "instructionmanua00byma", 1961,
         "The Library of Congress's literary braille course for volunteer transcribers, by its senior braille "
         "specialist and braille instructor: the braille alphabet, capitals, punctuation and numbers, every "
         "contraction lesson by lesson with drills and exercises, the braille page, mailing the exercises and the "
         "application for certification.", OLD_BRAILLE),
    _loc("nls_braille_transcribing_manual_1977", "Instruction Manual for Braille Transcribing, revised 1971 and 1973 "
         "(Maxine B. Dorf and Earl R. Scharry, Library of Congress; 1977 printing)",
         "Braille transcribing (course, history)", "instructionmanua00byma_0", 1977,
         "The Division for the Blind and Physically Handicapped's revised course: the same lessons arranged in "
         "numbered sections, with an alphabetical index of braille signs, braille writers and slates, every "
         "contraction with drills and exercises, and the rules for formats and title pages of its day.",
         OLD_BRAILLE),
    _loc("nls_braille_transcribing_manual_1984", "Instruction Manual for Braille Transcribing, Third Edition (Maxine "
         "B. Dorf with Barbara H. Tate, NLS, 1984, with the 1987 code changes)",
         "Braille transcribing (course, history)", "instructionmanua00maxi_1", 1984,
         "NLS's third edition of the literary braille course: lessons with drills and exercises, from the "
         "alphabet through every contraction and the rules of usage, to formats, title pages and the trial "
         "manuscript, with the code changes of 1987.", OLD_BRAILLE),
    _loc("nls_braille_transcribing_manual_2000", "Instruction Manual for Braille Transcribing, Fourth Edition "
         "(Constance Risjord, John Wilkinson and Mary Lou Stark, NLS, 2000)", "Braille transcribing (course, "
         "history)", "instructionmanua00cons", 2000,
         "NLS's fourth edition of the literary braille course, by its literary braille transcriber, literary braille "
         "advisor and the head of its braille development section: braille writers, computer braille programs and "
         "slates, every lesson with drills, reading practice and exercises, proofreading, grading and "
         "certification, the trial manuscript, and an index of rules.", OLD_BRAILLE + "Published by the Library of "
         "Congress in 2000 with no copyright notice; its three authors are named with their NLS positions.",
         licence=GOV_NO_NOTICE),
    _loc("nls_intro_braille_mathematics_1978", "An Introduction to Braille Mathematics, based on the Nemeth Code 1972 "
         "(Helen Roberts, Bernard M. Krebs and Barbara Taffet, NLS, 1978)", "Braille transcribing (Nemeth Code)",
         "introductiontobr00byhe", 1978,
         "NLS's course in transcribing mathematics in the Nemeth Braille Code (1972 revision): numerals and the "
         "numeric indicator, punctuation, signs of operation and comparison, alphabets and type forms, grouping, "
         "superscripts and subscripts, fractions and radicals, shapes, modifiers, function names, format and the "
         "certification test.", "The Nemeth Code has been revised since (BANA's current edition, used with UEB); "
         "check every rule against it."),
    _loc("nls_dictionary_braille_music_signs_1979", "Dictionary of Braille Music Signs (Bettye Krolick, NLS, 1979)",
         "Braille music", "dictionaryofbrai00bybe", 1979,
         "A dictionary of braille music signs listed by their braille cells, with what each means, the history of "
         "the braille music code, the formats for braille music (bar-over-bar, line-by-line, paragraphs and the "
         "others), chord symbols, figured bass and tablature, and the fundamentals of braille music.",
         "Braille music signs have been revised since (the Music Braille Code 2015 and the New International "
         "Manual of Braille Music Notation); check every sign against the current code."),
    _loc("nls_that_all_may_read_1983", "That All May Read: Library Service for Blind and Physically Handicapped People "
         "(NLS, 1983)", "Library services for blind readers (history)", "thatallmayreadli00libr", 1983,
         "NLS's book on library service to blind and physically handicapped people: the history of the national "
         "service from 1931, federal laws and agencies, readers, publishers and materials, reading aids and devices, "
         "the network of libraries, school, public and academic libraries, training and research, other countries, "
         "the free mailing privilege and a long bibliography.", "Details of services, machines and addresses are "
         "those of 1983; for today's service see vision:nls_services."),
]

# ====================================================================== blind-services: VA, IRS

VHA_LIST = "https://www.va.gov/vhapublications/publications.cfm?pub=1&order=asc&orderby=pub_Number"
SERVICES = [
    K.us_pdf(GROUP, name="va_vha_directive_1174", title="Blind and Visual Impairment Rehabilitation Continuum of Care "
             "(VHA Directive 1174, Department of Veterans Affairs)", subject="Rehabilitation services for blinded "
             "veterans", publisher="Veterans Health Administration, US Department of Veterans Affairs",
             pdf="https://www.va.gov/vhapublications/ViewPublication.asp?pub_ID=9244", page=VHA_LIST,
             version="VHA Directive 1174 as published on va.gov",
             description="The VA's directive on its blind and low vision rehabilitation services: who is eligible, "
                         "the Visual Impairment Services Team (VIST) coordinators, the Blind Rehabilitation Centers, "
                         "outpatient and home services, low vision clinics, orientation and mobility, living skills, "
                         "assistive technology and how veterans are referred.",
             notice=VA_WORDS + "A directive for VA staff; veterans ask their VA eye clinic or VIST coordinator."),
    _va("va_coordinated_services_blinded_veterans_1991", "Coordinated Services for Blinded Veterans (Department of "
        "Veterans Affairs, 1991)", "Rehabilitation services for blinded veterans", "coordinatedservi00vete_0", 1991,
        "Veterans Health Administration, Blind Rehabilitation Service",
        "The VA's booklet on its services for blinded veterans: legal blindness and low vision, the Visual "
        "Impairment Services Teams, the Blind Rehabilitation Centers and what they teach (orientation and mobility, "
        "living skills, communication, manual skills, low vision, adjustment), and benefits.",
        "Some services and addresses have changed since 1991; see eyes:va_blind_rehabilitation for today's pages."),
    _va("va_occupations_totally_blinded_veterans_1956", "Occupations of Totally Blinded Veterans of World War II and "
        "Korea (Veterans Administration, 1956)", "Employment of blind people (history)", "occupationsoftot00depa",
        1956, "Veterans Administration, Department of Veterans Benefits",
        "The VA's survey of the jobs that totally blinded veterans of the Second World War and Korea held, for use "
        "in vocational rehabilitation: professions, business, sales, clerical, skilled and unskilled work, farming "
        "and the training behind them.",
        "A record of 1956: today's jobs, technology and rights (the ADA, Section 504) are very different."),
    _hew("hew_services_to_the_blind_1973", "Services to the Blind: A Community Concern (Eleventh Institute on "
         "Rehabilitation Services, Rehabilitation Services Administration, 1973)", "Rehabilitation services for blind "
         "people", "servicestoblindcsoci", 1973, "Rehabilitation Services Administration, Social and Rehabilitation "
         "Service, US Department of Health, Education and Welfare",
         "A training resource for vocational rehabilitation staff on serving blind people in the community: the "
         "agencies for the blind, public and private, working together, rehabilitation facilities and their "
         "standards, planning services in each state, and the counsellor's work.",
         "A record of 1973: the laws (the Rehabilitation Act of 1973 and later) and services have changed since; see "
         "vision:rsa_blind_programs for today's programmes."),
    _fed("oe_teachers_problems_blind_partially_seeing_1933", "Teachers' Problems with Exceptional Children I: Blind "
         "and Partially Seeing Children (Beatrice McLeod, Office of Education, 1933)", "Education of blind children "
         "(history)", "teachersproblems00beat", 1933, "Office of Education, US Department of the Interior (Pamphlet "
         "No. 40)",
         "Twenty questions and answers for the ordinary classroom teacher, by the Office of Education's senior "
         "specialist in the education of physically handicapped children: who is a blind or partially seeing child, "
         "signs of eye trouble and simple tests, getting medical care, schools for the blind, sight-saving classes, "
         "lighting, supplies and methods, and the agencies that help.",
         "A record of 1933: today children's rights to education are set by IDEA and Section 504 (law:us_code_idea), "
         "and teaching methods have changed."),
    K.us_pdf(GROUP, name="irs_pub_524", title="Credit for the Elderly or the Disabled (IRS Publication 524)",
             subject="Taxes and disability", publisher="Internal Revenue Service (IRS), US Department of the "
             "Treasury", pdf="https://www.irs.gov/pub/irs-pdf/p524.pdf",
             page="https://www.irs.gov/forms-pubs/about-publication-524", version="the IRS's newest edition",
             description="Who can take the credit for the elderly or the disabled (people 65 or older, or retired on "
                         "permanent and total disability), the income limits, the physician's statement and how to "
                         "figure the credit (Schedule R).",
             notice="From the Internal Revenue Service: a US government work. Tax laws change every year: this is "
                    "the IRS's newest edition (the builder reads it again when the IRS changes it). The higher "
                    "standard deduction for blind people is in Publication 501 (pdf:irs_pub_501). Information, not "
                    "tax advice."),
]

# ====================================================================== blind-mobility, blind-daily-living

OLD_DOG_NOTE = ("Published in {year}: guide dog work has changed a great deal since (training methods, schools and the "
                "law: the ADA's service animal rules today). Its words are those of its day.")
MOBILITY = [
    old_book(GROUP, "eustis_seeing_eye_1927", "The Seeing Eye (Dorothy Harrison Eustis, 1927)", "Guide dogs (history)",
             "Dorothy Harrison Eustis (first printed in The Saturday Evening Post, 5 November 1927)",
             "seeingeye0000dheu", 1927,
             "The article that started guide dog work in America: Dorothy Harrison Eustis's account of the German "
             "school at Potsdam that trained shepherd dogs to guide blinded soldiers, how the dogs were trained and "
             "worked, and what a dog guide meant to a blind man's freedom. Morris Frank read it, wrote to her, and "
             "with her founded The Seeing Eye in 1929.", note=OLD_DOG_NOTE),
]

DAILY = [
    _hew("hew_head_start_children_visual_handicaps_1978", "Mainstreaming Preschoolers: Children with Visual "
         "Handicaps, a guide for teachers, parents and others (Head Start Bureau, 1978)", "Young blind children: "
         "daily life and learning", "childrenwithvisu00loua", 1978, "Head Start Bureau, Administration for Children, "
         "Youth and Families, US Department of Health, Education and Welfare (DHEW Publication No. (OHDS) 78-31112)",
         "Head Start's guide for teachers and parents of blind and visually impaired children aged three to five: "
         "what visual handicaps are and how they are found, how they affect a young child's self-concept, motor, "
         "self-help, language and social skills, planning the classroom and teaching techniques with activities, "
         "what parents can do at home, where to find help, and a chart of normal development from birth to six.",
         "A record of 1978: services and laws (IDEA's early intervention and preschool programmes today) have "
         "changed; words such as \"visually handicapped\" are those of its day."),
]

# ====================================================================== blind-screen-readers: BRLTTY (LGPL)

BRLTTY_DOC = "https://brltty.app/doc/"
BRLTTY_MANUAL = BRLTTY_DOC + "Manual-BRLTTY/English/"
BRLAPI_MANUAL = BRLTTY_DOC + "Manual-BrlAPI/English/"
BRLTTY_LICENCE_PAGE = BRLTTY_MANUAL + "BRLTTY-1.html"
BRLTTY_LICENCE_TEXT = r"The GNU Lesser General Public License"
BRLTTY_NOTICE = ("BRLTTY and its documentation are the work of the BRLTTY team (Dave Mielke and the BRLTTY "
                 "contributors), free software under the GNU Lesser General Public License, version 2.1 or any later "
                 "version, as the manual's licence section says; converted to an accessible format. A book made "
                 "from it keeps the same licence.")
BRLTTY_GUIDE_FILES = ["Introduction", "CommandReference", "KeyTables", "TextTables", "ContractionTables",
                      "AttributesTables", "Customize", "Profiles", "Devices", "BrailleDots", "Bluetooth", "Linux",
                      "Windows", "Android", "X11", "Systemd"]
BRLTTY_COMMON = dict(K.WEB, group=GROUP, country="International", licence=LGPL, licence_url=LGPL_URL,
                     licence_page=BRLTTY_LICENCE_PAGE, licence_text=BRLTTY_LICENCE_TEXT, notice=BRLTTY_NOTICE,
                     publisher="The BRLTTY team (brltty.app)", version="brltty.app as published")
SCREEN_READERS = [
    dict(BRLTTY_COMMON, name="brltty_manual", title="BRLTTY Reference Manual and BrlAPI Reference Manual",
         subject="Braille displays (BRLTTY, Linux)", source=BRLTTY_MANUAL + "BRLTTY.html",
         description="The whole reference manual of BRLTTY, the program that gives a blind person access to the "
                     "Linux console (and other systems) on a refreshable braille display: the build and "
                     "installation, starting it, the command line and configuration file, using the braille display "
                     "(cursor routing, cut and paste, speech, preferences menu), braille and text tables, and the "
                     "drivers; and the BrlAPI manual, the interface programs such as Orca use to share the display.",
         content=(r"(?i)<HR>", r"(?i)<HR>\s*<A\b"),
         title_from=r"<TITLE>(?:BRLTTY|BrlAPI) Reference Manual: (.*?)</TITLE>",
         crawl=[(BRLTTY_MANUAL + "BRLTTY.html", 1), (BRLAPI_MANUAL + "BrlAPI.html", 1)],
         pages=r"^https://brltty\.app/doc/Manual-(BRLTTY|BrlAPI)/English/(BRLTTY|BrlAPI)-\d+\.html$",
         unit_rules=[(r"/Manual-BrlAPI/", "BrlAPI Reference Manual"), (r".", "BRLTTY Reference Manual")], limit=80),
    dict(BRLTTY_COMMON, name="brltty_guides", title="BRLTTY guides: commands, tables, devices and the key bindings of "
         "every braille display", subject="Braille displays (BRLTTY)", source=BRLTTY_DOC + "Introduction.html",
         description="BRLTTY's own guides beside its manual: the introduction, the command reference, key tables, "
                     "text, contraction and attributes tables, customizing and profiles, devices and braille dots, "
                     "Bluetooth, Linux, Windows, Android, X11 and systemd, and the key bindings of every braille "
                     "display and keyboard it supports, one page per display family.",
         content=(r"(?i)<body\b[^>]*>", r"(?i)</body>"), title_from=r"(?is)<title>(.*?)</title>",
         urls=[BRLTTY_DOC + f + ".html" for f in BRLTTY_GUIDE_FILES], crawl=[(BRLTTY_DOC + "KeyBindings/", 1)],
         pages=r"^https://brltty\.app/doc/([A-Za-z0-9]+|KeyBindings/[A-Za-z0-9_-]+)\.html$",
         unit_rules=[(r"/KeyBindings/", "Key bindings of braille displays and keyboards"), (r".", "Guides")],
         limit=200),
]

# ====================================================================== blind-braille: old codes and the war of the dots

OLD_CODE_NOTE = ("Published in {year}: a historical book about a braille or embossed code that is no longer in use in "
                 "this form (American Braille, New York Point, Revised Braille Grade 1 1/2 and Grade 2 before "
                 "Standard English Braille and UEB). Kept as the history of braille; today's code in the US is UEB. "
                 "The scanned text has the scanner's mistakes and braille cells are shown only as pictures.")


def _old(name, title, subject, publisher, archive, year, description, note, country="United States", **more):
    """One old public-domain book (old_ia_books.old_book) in this module's group, with fields such as language."""
    entry = old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, country=country)
    entry.update(more)
    return entry


BRAILLE = [
    _old("wait_key_new_york_point_1908", "Key to the New York Point System of Tangible Writing and Printing (William "
         "B. Wait, 1908)", "New York Point (history)", "William B. Wait (New York Institute for the Education of the "
         "Blind)", "keytonewyorkpoin00wmbw", 1908,
         "The key to New York Point by its inventor, the superintendent of the New York Institution for the Blind: "
         "the letters, contractions, punctuation and numbers, and the signs for instrumental and vocal music and "
         "mathematics, for teachers and blind readers.", OLD_CODE_NOTE),
    _old("wait_origin_new_york_point_1892", "Origin of the New York Institution for the Blind; the Origin and "
         "Development of the New York Point System (William B. Wait, 1892)", "New York Point (history)",
         "William B. Wait (Bradstreet Press)", "originofnewyorki00wait", 1892,
         "Wait's account of the New York Institution for the Blind and of how New York Point was developed, with "
         "his case for it against braille.", OLD_CODE_NOTE),
    _old("new_york_point_or_braille_1909", "New York Point or Braille: Which Tactile Print for New York City (1909)",
         "The war of the dots (history)", "Reprinted from the Outlook for the Blind (Cambridge, Massachusetts)",
         "newyorkpointorbr00unse", 1909,
         "The report of the public hearing of 24 March 1909 before a committee of New York City's Board of "
         "Education, which was about to teach blind children in its public schools, on whether to teach New York "
         "Point or braille, with the arguments and briefs presented and the alphabets and slates of both.",
         OLD_CODE_NOTE),
    _old("wait_uniform_type_question_1915", "The Uniform Type Question: an Examination of the Report of the Uniform "
         "Type Committee of June 1913 (William B. Wait, 1915)", "The war of the dots (history)",
         "William B. Wait (Bradstreet Press)", "uniformtypequest00wait", 1915,
         "Wait's reply to the committee that studied which raised type all American blind readers should share, "
         "defending New York Point.", OLD_CODE_NOTE),
    _old("uniform_type_committee_fifth_report_1915", "Fifth Biennial Report of the Uniform Type Committee of the "
         "American Association of Workers for the Blind (1915)", "The war of the dots (history)",
         "American Association of Workers for the Blind, Uniform Type Committee", "fifthbiennialrep0000unse", 1915,
         "The Uniform Type Committee's report on its tests of the raised types read by blind people (American "
         "Braille, British Braille and New York Point), with an exhibit of the Standard Dot System it proposed.",
         OLD_CODE_NOTE),
    _old("loomis_revised_braille_ten_lessons_1924", "Revised Braille and How to Learn It in Ten Lessons (Madeleine S. "
         "Loomis, 1924)", "Braille (history)", "Madeleine S. Loomis (as taught in the Chicago Chapter, American Red "
         "Cross)", "revisedbrailleho00made", 1924,
         "A course for sighted volunteers learning to write Revised Braille, in ten lessons with exercises, as the "
         "American Red Cross taught it in Chicago, when volunteer transcribing for blind readers was growing.",
         OLD_CODE_NOTE),
    _old("rules_revised_braille_grade_2_1924", "Rules for Reading and Writing Revised Braille Grade 2, for American "
         "Readers of Grade 1 1/2 (1924)", "Braille (history)", "Permanent Blind Relief War Fund", "rulesforreadingw00unse",
         1924, "The rules of British Revised Braille Grade 2 explained for American readers who knew Grade 1 1/2: "
         "the extra contractions and how they are used.", OLD_CODE_NOTE),
    _old("irwin_grade_one_half_grade_two_1929", "Comparative Study of Braille Grade One and a Half and Braille Grade Two "
         "(Robert B. Irwin and Ruth E. Wilcox, 1929)", "Braille (history)", "Bureau of Research and Education, "
         "American Foundation for the Blind", "comparativestud00robe", 1929,
         "The American Foundation for the Blind's study comparing how quickly and accurately blind readers read "
         "Grade 1 1/2 and Grade 2, part of the work that led to Standard English Braille in 1932.", OLD_CODE_NOTE),
    _va("va_introductory_notes_braille_1959", "Introductory Notes on the Braille System of Reading and Writing for the "
        "Blind (Veterans Administration, 1959)", "Braille (history)", "introductorynote00euge", 1959,
        "Research and Development Division, Prosthetic and Sensory Aids Service, Veterans Administration (Eugene F. "
        "Murphy; prepared by Arthur Lipton)",
        "The VA's short description of braille for the engineers working on reading machines and braille output: "
        "Louis Braille and the cell, Grade 1 and Grade 2, contractions, numbers, the space braille takes, and "
        "braille production.", "A record of 1959 (Standard English Braille, before UEB)."),
]

# ====================================================================== blind-history

OLD_HISTORY_NOTE = ("Published in {year}: an old book. Its words for blind and deafblind people (\"the blind\", "
                    "\"deaf and dumb\", \"afflicted\") and many of its ideas about them are those of its day, not "
                    "today's; it is kept as history and for its own voice.")
KELLER_NOTE = ("Published in {year}. Helen Keller wrote in the words of her day; her later life and work (she lived "
               "until 1968) are told in other books.")
# (the item's numbers in its identifier, the year its record gives, the first and last report in it, a note)
PERKINS = [
    ("110", 1834, 1, 10, " Samuel Gridley Howe's first reports: the founding of the school and the education of "
                         "Laura Bridgman."),
    ("1120", 1843, 11, 20, ""), ("2138", 1853, 21, 38, ""), ("3946", 1871, 39, 46, ""), ("4752", 1879, 47, 52, ""),
    ("5357", 1885, 53, 57, ""), ("5860", 1890, 58, 60, ""), ("6163", 1893, 61, 63, ""), ("6466", 1896, 64, 66, ""),
    ("6769", 1899, 67, 69, ""), ("7072", 1902, 70, 72, ""), ("7375", 1904, 73, 75, ""), ("7680", 1908, 76, 80, ""),
    ("8185", 1913, 81, 85, ""), ("8692", 1918, 86, 92, ""),
    ("9399", 1925, 93, 99, " The last report in it is the ninety-ninth, dated 1930."),
]
OUTLOOK = [(21, 1927), (22, 1928), (23, 1929), (24, 1930)]

HISTORY = [
    _old("keller_world_i_live_in_1908", "The World I Live In (Helen Keller, 1908)", "Helen Keller", "Helen Keller "
         "(The Century Company)", "worldilivei00kell", 1908,
         "Helen Keller's essays on how she knows the world through touch, smell and the other senses, her dreams "
         "and her thinking, with the poem \"A Chant of Darkness\".", KELLER_NOTE),
    _old("keller_optimism_1903", "Optimism: an Essay (Helen Keller, 1903)", "Helen Keller", "Helen Keller (T. Y. "
         "Crowell)", "optimismessay00kelliala", 1903,
         "Helen Keller's essay, written while she was a student at Radcliffe, on optimism within herself and in the "
         "world.", KELLER_NOTE),
    _old("keller_song_of_the_stone_wall_1910", "The Song of the Stone Wall (Helen Keller, 1910)", "Helen Keller",
         "Helen Keller (The Century Company)", "songofstonewall00kellrich", 1910,
         "Helen Keller's long poem on the old stone walls of New England and the people who built them, written "
         "after she explored them by touch.", KELLER_NOTE),
    _old("keller_out_of_the_dark_1913", "Out of the Dark: Essays, Letters, and Addresses on Physical and Social Vision "
         "(Helen Keller, 1913)", "Helen Keller", "Helen Keller (Doubleday, Page)", "outofdarkessays00kell", 1913,
         "Helen Keller's essays, letters and speeches on preventing blindness, on the education and work of blind "
         "people, and on social questions of her day.", KELLER_NOTE),
    _old("keller_my_religion_1927", "My Religion (Helen Keller, 1927)", "Helen Keller", "Helen Keller (Doubleday, "
         "Page)", "myreligion00hele", 1927,
         "Helen Keller on her religious faith and on the writings of Emanuel Swedenborg, and what they meant to "
         "her as a deafblind woman.", KELLER_NOTE),
    _old("keller_midstream_1929", "Midstream: My Later Life (Helen Keller, 1929)", "Helen Keller", "Helen Keller "
         "(Doubleday, Doran)", "midstreammylater017614mbp", 1929,
         "Helen Keller's second memoir, from Radcliffe to 1929: her work for blind people and the American "
         "Foundation for the Blind, her lecture tours and vaudeville, the film of her life, her travels and the "
         "people she met, and her life with Anne Sullivan Macy.", KELLER_NOTE),
    _old("elliott_hall_laura_bridgman_1903", "Laura Bridgman: Dr. Howe's Famous Pupil and What He Taught Her (Maud Howe "
         "Elliott and Florence Howe Hall, 1903; the 1904 London printing)", "Laura Bridgman", "Maud Howe Elliott "
         "and Florence Howe Hall (Hodder and Stoughton)", "laurabridgmandrh00elli", 1904,
         "The life of Laura Bridgman, the first deafblind child to be educated in English, by Samuel Gridley Howe's "
         "daughters, from his reports and her journals: how he taught her to read raised letters and to "
         "fingerspell, and her life at the Perkins Institution.", OLD_HISTORY_NOTE),
    _old("lamson_life_education_laura_bridgman_1884", "Life and Education of Laura Dewey Bridgman (Mary Swift Lamson, "
         "1878; the 1884 printing)", "Laura Bridgman", "Mary Swift Lamson (Houghton, Mifflin)",
         "lifeeducationofl00lams", 1884,
         "The life of Laura Bridgman by one of her teachers at the Perkins Institution, with the teachers' journals "
         "of her lessons.", OLD_HISTORY_NOTE),
    _old("howe_account_laura_bridgman_1843", "An Account of Laura Bridgman, of Boston, a Blind, Deaf and Dumb Girl "
         "(Samuel Gridley Howe, 1843)", "Laura Bridgman", "Samuel Gridley Howe (J. Wright, London)",
         "gu_accountlaurab00perk", 1843,
         "Howe's own account of Laura Bridgman's education, from his reports, with notes on three other deafblind "
         "pupils of the Perkins Institution.", OLD_HISTORY_NOTE),
    _old("levy_blindness_and_the_blind_1872", "Blindness and the Blind, or A Treatise on the Science of Typhlology "
         "(W. Hanks Levy, 1872)", "Blind people's lives (history)", "William Hanks Levy (Chapman and Hall, London)",
         "blindnessblindor00levyiala", 1872,
         "A blind writer's book on blindness in Victorian Britain: the causes of blindness, training blind "
         "children, the senses, \"on the blind walking alone, and of guides\", the printing and reading systems "
         "(Moon, Lucas, Frere, braille and others), writing, arithmetic, tangible maps, and lives of blind people "
         "through history.",
         OLD_HISTORY_NOTE, country="United Kingdom"),
    _old("armitage_education_employment_blind_1886", "The Education and Employment of the Blind: What It Has Been, Is "
         "and Ought to Be (T. R. Armitage, 1886)", "Blind people's lives (history)", "Thomas Rhodes Armitage "
         "(Harrison and Sons, London)", "educationemploym00armi", 1886,
         "The second edition of the book by the blind physician who founded the British and Foreign Blind "
         "Association (later the RNIB) and won braille's adoption in Britain: education, reading systems, trades "
         "and employment of blind people.", OLD_HISTORY_NOTE, country="United Kingdom"),
    _old("villey_world_of_the_blind_1930", "The World of the Blind: A Psychological Study (Pierre Villey, 1930)",
         "Blind people's lives (history)", "Pierre Villey, translated by Alys Hallard (Duckworth, London)",
         "worldofblindpsyc00pier", 1930,
         "The blind French scholar Pierre Villey's study of blind people's minds and lives: intelligence and "
         "ideas, tactile reading and the braille alphabet, intellectual work, how the other senses take over, the "
         "\"sense of obstacles\", finding one's way, gymnastics and games, and everyday physical activity.", OLD_HISTORY_NOTE, country="United Kingdom"),
    _old("braille_centenary_paris_1909", "Compte rendu des fêtes du centenaire de Louis Braille, 27 et 28 janvier 1909 "
         "(Institution nationale des jeunes aveugles, 1910)", "Louis Braille (history, in French)",
         "Institution nationale des jeunes aveugles (Paul Dupont, Paris)", "compterendudefet00inst", 1910,
         "The French account of the celebrations at Paris for the hundredth birthday of Louis Braille in 1909: the "
         "speeches at the national institution for blind youth where he studied and taught.", OLD_HISTORY_NOTE,
         country="France", language="fra"),
    _old("proofreader_cant_see_1916", "This Proofreader Can't See (Illustrated World, 1916)", "Blind people at work "
         "(history)", "Illustrated World (magazine)", "thisproofreaderc00unse", 1916,
         "A short magazine article of July 1916 about Mrs. L. N. Muck of College View, Nebraska, one of the few "
         "blind proofreaders of her day, at a newspaper printed for blind readers, and how its editor wrote copy on "
         "a braille writing machine.", OLD_HISTORY_NOTE),
    _fed("census_blind_in_united_states_1910", "The Blind in the United States, 1910 (Bureau of the Census, 1917)",
         "Blind people in the US (history)", "blindinuniteds00unit", 1917, "Bureau of the Census, US Department of "
         "Commerce",
         "The Census Bureau's report on blind people counted in the 1910 census: their numbers by state and city, "
         "sex, age, race and nativity, marriage, occupations and those in institutions, and from special schedules "
         "the age at which sight was lost, its causes, education and work.",
         "A record of its time, in the words of 1917."),
    K.us_pdf(GROUP, name="va_blind_rehabilitation_50_years_1998", title="Blind Rehabilitation Service: 50 Years of "
             "Excellence, 1948 to 1998 (Department of Veterans Affairs)", subject="Blinded veterans (history)",
             publisher="Hines Blind Rehabilitation Center and Medical Media, US Department of Veterans Affairs",
             archive="blindrehabilitat00hine", published="1998",
             version="1998 (Internet Archive item blindrehabilitat00hine)",
             description="The VA's history of its Blind Rehabilitation Service, from the training of blinded "
                         "servicemen at Avon Old Farms and Valley Forge in the Second World War and the first Blind "
                         "Rehabilitation Center at Hines in 1948 to the centres, VIST coordinators and services of "
                         "1998, with the pioneers of the long cane and orientation and mobility.",
             notice=VA_WORDS + "Prepared and published by the staff of the Hines Blind Rehabilitation Center and "
                    "Medical Media (the Blind American Veterans Foundation shared the cost of printing). " + SCAN),
] + [
    _old(f"perkins_annual_reports_{span}", f"Annual Reports of the Trustees of the Perkins Institution for the "
         f"Blind, reports {first} to {last} (bound volume of {year})", "Perkins Institution (history)",
         "Trustees of the Perkins Institution and Massachusetts Asylum (later School) for the Blind",
         f"annualreportoftr{span}perk", year,
         f"The annual reports {first} to {last} of the Perkins Institution for the Blind in Boston, bound together: "
         "each year's report of the trustees and the director (Samuel Gridley Howe until 1876, then Michael "
         "Anagnos and, from 1907, Edward E. Allen) on the pupils, teaching, music, raised print, work and the "
         f"accounts.{note}", OLD_HISTORY_NOTE)
    for span, year, first, last, note in PERKINS
] + [
    _old(f"outlook_for_the_blind_{year}", f"Outlook for the Blind, volume {vol} ({year})", "Outlook for the Blind "
         "(journal, history)", "American Foundation for the Blind", f"outlookforblind{vol}unse", year,
         f"The year {year} of the Outlook for the Blind, published by the American Foundation for the Blind (the "
         "journal now called the Journal of Visual Impairment & Blindness): articles and news of the work for "
         "blind people in its day.", OLD_HISTORY_NOTE)
    for vol, year in OUTLOOK
]

# ====================================================================== words and the collection

THEMES = {
    "blind-nls": NLS_BOOKS, "blind-services": SERVICES, "blind-mobility": MOBILITY, "blind-daily-living": DAILY,
    "blind-screen-readers": SCREEN_READERS, "blind-braille": BRAILLE, "blind-history": HISTORY,
}
GUIDES = SCREEN_READERS                                      # web guides; every other entry is a PDF
PDFS = NLS_BOOKS + SERVICES + MOBILITY + DAILY + BRAILLE + HISTORY


def _keys(entries):
    """The keys of some entries ("blind:<name>")."""
    return [f"{PREFIX}:{e['name']}" for e in entries]


WORDS = {word: (lambda entries=entries: _keys(entries)) for word, entries in THEMES.items()}
WORDS["blind-living"] = lambda: [k for entries in THEMES.values() for k in _keys(entries)]

COLLECTION = K.Collection(PREFIX, GROUP, guides=GUIDES, pdfs=PDFS, words=WORDS)

LICENCE_LINES = {
    "blind_loc_nls": "Library of Congress (Division for the Blind, NLS) publications on the Internet Archive "
                     "(collection aphmigel): no copyright notice on their title pages (checked 2026-11-23, and the "
                     "first twelve pages of each PDF at every build); written by Library of Congress staff (17 U.S.C. "
                     "105); before 1989 also public domain for lack of notice (copyright.gov, title 17 chapter 4, "
                     "\"Omission of notice on certain copies\", checked at every build).",
    "blind_va_federal": "va.gov (VHA Directive 1174), irs.gov (Publication 524) and the VA's, Office of "
                        "Education's and Census Bureau's own publications on the Internet Archive: works of the US "
                        "government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build); the HEW "
                        "publications of 1973 and 1978 carry no copyright notice (their first pages checked at every "
                        "build). robots.txt of va.gov, irs.gov and archive.org allow the files; no AI rules (checked "
                        "2026-11-23).",
    "blind_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                       "a later reprint is refused). The British and French books are public domain in the US as "
                       "published before 1931.",
    "blind_brltty": "brltty.app/doc/Manual-BRLTTY/English/BRLTTY-1.html (checked at every build): \"You may "
                    "redistribute it and/or modify it under the terms of The GNU Lesser General Public License ... "
                    "Version 2.1 (or any later version)\"; brltty.app has no robots.txt (checked 2026-11-23).",
}

NOT_INCLUDED = [
    ("Today's braille transcribing and proofreading courses (literary UEB, Nemeth, music, proofreading)", "NLS handed "
     "its transcriber and proofreader certification to the National Federation of the Blind; the courses are the "
     "NFB's copyright: link-only. The Library of Congress's own older course books are built (blind-nls). Index: "
     "https://nfb.org/programs-services/braille-certification"),
    ("Outlook for the Blind, 1907 to 1926", "The Internet Archive's records of these volumes (outlookforblind190709unse "
     "to outlookforblind1926unse) give no year, so the builder cannot confirm they were published before 1931 and "
     "would refuse them; the volumes for 1927 to 1930 are built. Index: "
     "https://archive.org/search?query=outlookforblind"),
    ("Books of 1931 to 1963: Cooking and Sewing for Blind Students (1931), the guide dog books of the 1930s (Skipper "
     "the Guide Dog, Beowulf, The Seeing Eye Dog) and First Lady of the Seeing Eye (1957)", "No evidence was found "
     "that their copyrights were not renewed: link-only. Index: https://archive.org/details/aphmigel"),
    ("Techniques for Eating: A Guide for Blind Persons (Western Michigan University, 1981), Preprimer Cooking (APH, "
     "1973) and the Workshop on Low Vision Mobility (1975)", "Published by a university, by APH and by a workshop with "
     "VA support, not by the government itself; their copyright status is not clear: link-only for the owner's "
     "personal use. Index: https://archive.org/details/techniquesforea00lloy"),
    ("Braille Into the Next Millennium (NLS, 2000)", "Essays by many outside authors, published in 2000 with the "
     "Friends of Libraries for Blind and Physically Handicapped Individuals; no open licence: link-only. Index: "
     "https://archive.org/details/brailleintonextm00edit"),
    ("Introduction to Braille Music Transcription (Mary Turner De Garmo, Library of Congress, 1974)", "It reprints "
     "music examples by permission of their publishers (copyright notices of 1939 and 1959 among them): link-only. "
     "The Dictionary of Braille Music Signs (1979) is built. Index: "
     "https://archive.org/details/introductiontobr00mary_0"),
    ("Social Security's booklets for blind people (Disability Benefits for Blind People, 1973, and others)", "The "
     "only copies a program may read are decades old and out of date; www.ssa.gov refuses programs. Index: "
     "https://www.ssa.gov/pubs/EN-05-10052.pdf"),
    ("Speech Dispatcher and eSpeak NG manuals", "Their manuals are published only on GitHub (freebsoft.org's "
     "address sends readers to a GitHub preview), which refuses programs: link-only. Index: "
     "https://github.com/brailcom/speechd and https://github.com/espeak-ng/espeak-ng"),
    ("Accessible Pedestrian Signals: A Guide to Best Practices (NCHRP, Transportation Research Board)", "Copyright of "
     "the National Academies: link-only. The Access Board's own guidelines for accessible pedestrian signals and "
     "detectable warnings are built (travel:access_board_prowag). Index: https://www.apsguide.org/"),
    ("Design and Development of a Collapsible Folding Cane (1969) and the VA's Instructional Manual for Visual "
     "Skills (1975)", "Public domain government reports, but the Internet Archive's PDFs of both are mostly scanned "
     "pictures without their words, so the builder refuses them (tried 2026-11-23); open them in the Internet "
     "Archive's own reader. Index: https://archive.org/details/designdevelopmen00unse and "
     "https://archive.org/details/instructionalman00alic"),
    ("USDA Food and Nutrition Service and HUD guides for blind people", "Not looked for in this round beyond what the "
     "library already has (HUD's reasonable accommodation and modification pages, civic:); the index links those. "
     "Index: https://www.fns.usda.gov/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
