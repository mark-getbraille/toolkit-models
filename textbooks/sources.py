"""Which textbooks and reference works the textbooks workflow builds, where each comes from, and what was checked.

Every source here was checked by hand on 2026-11-18 (the licence line is quoted in LICENCE_LINES), and the builder
checks each book's licence again from the source itself every time it runs (build_textbooks.py: the OpenStax
collection file, the Siyavula book's copyright page, the DSpace record of the international body). A book whose
licence is not one of ALLOWED, or no longer says what is written here, is left out of the release and listed with
the reason in textbooks.json ("left_out").

Licences and how they are shown in the Digital Accessibility Toolkit:
  open          CC BY, CC0, public domain, Open Government Licence: shown as they are
  share-alike   CC BY-SA: shown as they are (copies and changes keep the same licence)
  non-commercial  CC BY-NC, CC BY-NC-SA: shown with "not for commercial use" (fine for personal and school use)
  never         any "NoDerivatives" (ND) licence: a ZIM file is a new arrangement of the work (its pages split
                and rewritten as web pages, math turned into text), which counts as an adaptation, so ND works are
                left out.

Kinds of source:
  osbooks   an OpenStax book repository on GitHub (github.com/openstax/osbooks-*), CNXML and pictures; one
            repository can hold several books (its META-INF/books.xml lists them)
  siyavula  a Siyavula textbook read from its online reader (www.siyavula.com/read/..., allowed by its robots.txt);
            the reader has the formulas as LaTeX, which is turned into text (the EPUB has them only as pictures
            without descriptions)
  dspace    a publication in the open repository of an international body (a DSpace 7 site: the World Health
            Organization's IRIS, the World Bank's Open Knowledge Repository, FAO's): its record gives the title,
            licence and the original PDF, which is turned into one page per chapter of its bookmarks
"""

# The OpenStax repositories (each holds one or more books). Checked with "git ls-remote" on 2026-11-18.
OSBOOKS = [
    "anatomy-physiology", "biology-bundle", "chemistry-bundle", "college-physics-bundle",
    "university-physics-bundle", "physics", "statistics", "astronomy", "psychology", "introduction-sociology",
    "microbiology", "american-government", "us-history", "world-history", "principles-economics-bundle",
    "introductory-statistics-bundle", "calculus-bundle", "college-algebra-bundle", "prealgebra-bundle",
    "contemporary-mathematics", "business-ethics", "introduction-business", "introduction-philosophy",
    "writing-guide", "entrepreneurship", "principles-accounting-bundle", "introduction-intellectual-property",
    "introduction-anthropology", "introduction-political-science", "college-success-bundle", "principles-marketing",
    "business-law", "principles-finance", "data-science", "lifespan-development", "organic-chemistry",
    "life-liberty-pursuit-happiness", "foundations-information-systems", "workplace-software-skills",
]

# Siyavula (South Africa): the books of its online reader; subject path, grade, title, subject in words.
SIYAVULA = [
    ("mathematics", 10, "Mathematics Grade 10", "Mathematics"),
    ("mathematics", 11, "Mathematics Grade 11", "Mathematics"),
    ("mathematics", 12, "Mathematics Grade 12", "Mathematics"),
    ("physical-sciences", 10, "Physical Sciences Grade 10", "Physics and chemistry"),
    ("physical-sciences", 11, "Physical Sciences Grade 11", "Physics and chemistry"),
    ("physical-sciences", 12, "Physical Sciences Grade 12", "Physics and chemistry"),
    ("natural-sciences", 7, "Natural Sciences Grade 7", "Science"),
    ("natural-sciences", 8, "Natural Sciences Grade 8", "Science"),
    ("natural-sciences", 9, "Natural Sciences Grade 9", "Science"),
]

# Reference works of international bodies (the "Reference works" part of the Textbooks group): DSpace site,
# handle, id, short title, subject, body, licence expected (checked again from the record when built).
DSPACE = [
    ("https://iris.who.int", "10665/371090", "who_essential_medicines_2023",
     "WHO Model List of Essential Medicines, 23rd list (2023)", "Medicine", "World Health Organization",
     "CC BY-NC-SA 3.0 IGO"),
    ("https://openknowledge.worldbank.org", "10986/41919", "worldbank_wdr_2024", "World Development Report 2024",
     "Economics", "World Bank", "CC BY 3.0 IGO"),
    ("https://openknowledge.fao.org", "20.500.14283/cd2616en", "fao_sofa_2024",
     "The State of Food and Agriculture 2024", "Agriculture", "Food and Agriculture Organization (FAO)",
     "CC BY-NC-SA 3.0 IGO"),
]

# The licence lines found when each source was checked by hand (quoted from the source).
LICENCE_LINES = {
    "osbooks": "Each OpenStax collection file states its own licence, for example osbooks-physics: "
               "<md:license url=\"http://creativecommons.org/licenses/by/4.0/\">Creative Commons Attribution "
               "License</md:license>; osbooks-anatomy-physiology (since March 2026): \"Creative Commons "
               "Attribution-NonCommercial-ShareAlike 4.0 International\".",
    "siyavula": "Siyavula's reader pages: \"All Siyavula textbook content made available on this site is released "
                "under the terms of a Creative Commons Attribution License.\" The books' copyright page: \"This "
                "book is released under the CC-BY 4.0 license. ... you have to acknowledge Siyavula Education as "
                "the original author ... Everything Maths and Everything Science are trademarks of Siyavula "
                "Education and cannot be used without permission\" (so the books are named by subject and grade, "
                "with Siyavula credited, never with those trademarks).",
    "who": "WHO IRIS record 10665/371090: dc.rights \"CC BY-NC-SA 3.0 IGO\".",
    "worldbank": "World Bank OKR record 10986/41919: dc.rights \"CC BY 3.0 IGO\".",
    "fao": "FAO record 20.500.14283/cd2616en: dc.rights.license \"CC BY NC SA 3.0 IGO\" (its page also mentions a "
           "CC BY 4.0 copyright page; the stricter licence of the record is used).",
    "eff": "www.eff.org/copyright: \"Any and all original material on the EFF website may be freely distributed at "
           "will under the Creative Commons Attribution 4.0 International License (CC-BY), unless otherwise noted.\" "
           "Every Surveillance Self-Defense page ends \"Copyright (CC BY)\", linking there.",
    "peoples_law_school": "www.peopleslawschool.ca/terms-use/: \"The content on the People's Law School website, "
                          "except for the images and videos, is licensed under a Creative Commons Attribution-"
                          "NonCommercial-ShareAlike 4.0 International Licence\" (so the book has the text only; "
                          "its pictures are left out).",
    "field_manuals": "Each manual's own front page, for example ATP 3-50.21: \"DISTRIBUTION RESTRICTION: Approved "
                     "for public release; distribution is unlimited.\"; the Navy courses: \"DISTRIBUTION STATEMENT "
                     "A: Approved for public release; distribution is unlimited.\" US government works (17 U.S.C. "
                     "105).",
    "gov_uk": "Each gov.uk publication page: \"All content is available under the Open Government Licence v3.0, "
              "except where otherwise stated\"; MSN 1560: \"© Crown copyright 1994\".",
    "alberta": "Each open.alberta.ca publication page: \"Usage / Licence ... Open Government Licence - Alberta\".",
    "w3c_wai_curricula": "www.w3.org/WAI/curricula/ and each module page: \"This work is licensed under a Creative "
                         "Commons Attribution 4.0 International License.\" (Most other WAI pages are under the W3C "
                         "Document License, which allows no changes, so they are not included.)",
}

# Reference works of non-profit organisations (the toolkit's collection "Reference, non-profits"): guides published
# as web pages under an open licence, made into one ZIM book each by build_textbooks.webguide_book. Checked by hand
# on 2026-11-18 (robots.txt allows the pages; the licence line is quoted in LICENCE_LINES). Each entry:
#   name, title, subject, publisher, country, licence (expected), licence_url, source (the guide's home page),
#   description
#   licence_page + licence_text  a page fetched at every build that must still contain licence_text (a regular
#                                expression), or the whole guide is left out
#   page_mark                    a regular expression every page must contain (the page's own licence line), or
#                                "" when the licence page covers the whole site; a page without it is left out
#   start                        the pages read first (the guide's contents pages)
#   units                        a regular expression for the part pages linked from start ("" for none); each
#                                part's title (its <h1>) becomes a heading of the book's contents
#   pages                        a regular expression for the article pages, linked from the part pages (or from
#                                start, or listed in sitemap)
#   sitemap                      a sitemap.xml whose addresses matching pages are the articles ("" for none)
#   unit_rules                   [(regular expression, part name)] to sort sitemap articles into parts
#   content                      (start, end): the article's text is between the first match of start and the
#                                first match of end after it (regular expressions)
#   drop                         regular expressions of parts of the article to leave out (menus, "print" links)
#   limit                        the most articles read (a guard against a site that changed shape)
NONPROFIT = [
    {
        "name": "eff_surveillance_self_defense", "title": "Surveillance Self-Defense",
        "subject": "Digital security and privacy", "publisher": "Electronic Frontier Foundation (EFF)",
        "country": "International", "licence": "CC BY 4.0",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/", "source": "https://ssd.eff.org/",
        "description": "The Electronic Frontier Foundation's guides to protecting yourself from surveillance and "
                       "online threats: strong passwords, two-factor authentication, phishing, encryption, safe "
                       "messaging, phones and computers, with step-by-step tool guides and security scenarios.",
        "licence_page": "https://www.eff.org/copyright",
        "licence_text": r"Creative Commons Attribution 4\.0 International License",
        "page_mark": r"Copyright \(CC BY\)",
        "start": ["https://ssd.eff.org/"],
        "units": r"^https://ssd\.eff\.org/module-categories/[a-z0-9-]+$",
        "pages": r"^https://ssd\.eff\.org/module/[a-z0-9-]+$",
        "sitemap": "", "unit_rules": [],
        "content": (r'id="main-content"[^>]*>', r"<footer"),
        "drop": [r'<p class="breadcrumbs".*?</p>', r'<div class="[^"]*share[^"]*".*?</div>'],
        "limit": 300,
    },
    {
        "name": "peoples_law_school_bc", "title": "People's Law School: everyday legal problems (British Columbia)",
        "subject": "Law (British Columbia, Canada)", "publisher": "People's Law School", "country": "Canada",
        "licence": "CC BY-NC-SA 4.0", "licence_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "source": "https://www.peopleslawschool.ca/",
        "description": "Plain-language legal information for British Columbia, Canada, from the non-profit People's "
                       "Law School: work, renting, consumer problems and scams, cars, health, money and debt, "
                       "families, wills and estates, planning for future care, and its questions and answers. It is "
                       "general information, not legal advice, and applies to British Columbia.",
        "licence_page": "https://www.peopleslawschool.ca/terms-use/",
        "licence_text": r"Creative Commons Attribution-NonCommercial-ShareAlike 4\.0 International",
        "page_mark": "",
        "start": [],
        "units": "",
        "pages": r"^https://www\.peopleslawschool\.ca/(qa/)?(?!fr/|zh-Hans/|category/|news/|webinar/|person/|about/"
                 r"|publications/|privacy-policy/|terms-use/)[a-z0-9-]+/$",
        "sitemap": "https://www.peopleslawschool.ca/sitemap.xml",
        "unit_rules": [(r"^(?!.*/qa/)", "Guides"), (r"/qa/", "Questions and answers")],
        "content": (r"<main\b[^>]*>", r"</main>"),
        "drop": [r"<aside\b.*?</aside>", r"<svg\b.*?</svg>", r"<img\b[^>]*>"],   # its pictures are not licensed
        "limit": 700,
    },
    {
        "name": "w3c_wai_curricula", "title": "Curricula on Web Accessibility (W3C WAI)",
        "subject": "Web accessibility", "publisher": "W3C Web Accessibility Initiative (WAI)",
        "country": "International", "licence": "CC BY 4.0",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/", "source": "https://www.w3.org/WAI/curricula/",
        "description": "Curricula on Web Accessibility: A Framework to Build Your Own Courses, by the W3C Web "
                       "Accessibility Initiative (Daniel Montalvo and Shadi Abou-Zahra, eds.; Copyright World Wide "
                       "Web Consortium). Teaching modules on accessibility foundations and on accessible content, "
                       "design and development.",
        "licence_page": "https://www.w3.org/WAI/curricula/",
        "licence_text": r"licensed under a\s*<a[^>]*>\s*Creative Commons Attribution 4\.0 International License",
        "page_mark": r"Creative Commons Attribution 4\.0 International License",
        "start": ["https://www.w3.org/WAI/curricula/"],
        "units": r"^https://www\.w3\.org/WAI/curricula/[a-z-]+-modules/$",
        "pages": r"^https://www\.w3\.org/WAI/curricula/[a-z-]+-modules/[a-z0-9-]+/$",
        "sitemap": "", "unit_rules": [],
        "content": (r"<main\b[^>]*>", r"</main>"),
        "drop": [r'<nav\b.*?</nav>'],
        "limit": 80,
    },
]

# Official PDF documents (the toolkit's collections "Reference, field manuals" and "Reference, governments"), made into
# one ZIM book each by build_textbooks.pdfdoc_book. Each entry: name, title, subject, publisher, country, group
# ("fieldmanual" or "government"), licence, licence_url, description, and where the PDF is:
#   archive          an Internet Archive item holding a copy of a US military manual (the official site,
#                    armypubs.army.mil, shuts out automated readers in its robots.txt; marines.mil, the Coast Guard's
#                    and FEMA's sites refuse automated requests). distribution_a: True makes the builder read the
#                    manual's own front matter and keep it only when it says "Approved for public release;
#                    distribution is unlimited" (Distribution Statement A) and shows no restricted marking
#                    (Distribution B to F, FOUO, CUI); its parts about weapons, tactics or harm are left out.
#   page + licence_text + pdf_pattern   an official publication page that must still state licence_text (a regular
#                    expression, checked at every build); its newest PDF matching pdf_pattern is used.
# The field manuals were checked by hand on 2026-11-18: each front page reads "DISTRIBUTION RESTRICTION: Approved
# for public release; distribution is unlimited." They are works of the US government (17 U.S.C. 105), so public
# domain. Only survival, first aid, map reading, knots and rigging, field hygiene and cold-weather and mountain
# safety are chosen; never anything about weapons, explosives or tactics.
US_GOV = "Public domain (US government work)"
US_GOV_URL = "https://www.copyright.gov/title17/92chap1.html#105"
FIELD = dict(group="fieldmanual", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
             distribution_a=True)
PDF_DOCS = [
    dict(FIELD, name="army_atp_3_50_21_survival", title="Survival (ATP 3-50.21, 2018)", subject="Survival",
         publisher="Headquarters, Department of the Army", archive="survival-atp-3-50-21",
         description="The US Army's survival manual: survival medicine, water, food, fire, shelter and clothing, "
                     "movement and navigation, survival equipment, and knots and rope."),
    dict(FIELD, name="army_fm_4_25_11_first_aid", title="First Aid (FM 4-25.11, 2002)", subject="First aid",
         publisher="Headquarters, Department of the Army (with the Navy and Air Force)", archive="FM4-25x11",
         description="The US armed forces' first-aid manual for everyone: checking a casualty, breathing, "
                     "bleeding, shock, fractures, burns, heat and cold injuries, bites and stings, and "
                     "psychological first aid."),
    dict(FIELD, name="army_fm_3_25_26_map_reading", title="Map Reading and Land Navigation (FM 3-25.26, 2001)",
         subject="Maps and navigation", publisher="Headquarters, Department of the Army", archive="FM3-25x26",
         description="The US Army's manual of map reading and land navigation: map symbols, grids, scale and "
                     "distance, direction, the compass, elevation and relief, terrain association, orienteering "
                     "and GPS."),
    dict(FIELD, name="army_fm_4_25_12_field_sanitation", title="Unit Field Sanitation Team (FM 4-25.12, 2002)",
         subject="Field hygiene and sanitation", publisher="Headquarters, Department of the Army",
         archive="FM4-25x12",
         description="The US Army's field sanitation manual: safe drinking water, food safety, waste disposal, "
                     "insects and pests, and heat and cold injury prevention in the field."),
    dict(FIELD, name="army_fm_5_125_rigging", title="Rigging Techniques, Procedures, and Applications (FM 5-125, 1995)",
         subject="Knots, rope and rigging", publisher="Headquarters, Department of the Army",
         archive="fm-5-125-rigging-techniques-procedures-and-applications-1995",
         description="The US Army's rigging manual: fibre and wire rope, knots, hitches and splices, anchors, "
                     "blocks and tackle, and lifting safely."),
    dict(FIELD, name="army_tc_3_97_61_mountaineering", title="Military Mountaineering (TC 3-97.61, 2025)",
         subject="Mountaineering and mountain safety", publisher="Headquarters, Department of the Army",
         archive="military-mountaineering-tc-3-97.61-november-2025",
         description="The US Army's mountaineering manual: the mountain environment, environmental injuries, "
                     "avalanches, moving in the mountains, navigation, knots and rope, anchors, climbing, fixed "
                     "ropes, stream crossing, glacier travel, and mountain rescue."),
    dict(FIELD, name="army_tc_21_3_cold_weather", title="Soldier's Handbook for Individual Operations and Survival "
         "in Cold-Weather Areas (TC 21-3, 1986)", subject="Cold-weather safety and survival",
         publisher="Headquarters, Department of the Army",
         archive="soldiers-handbook-for-individual-operations-and-survival-in-cold-weather-areas-tc-21-3",
         description="The US Army's cold-weather handbook: clothing, shelters, rations, hygiene and first aid in "
                     "the cold (hypothermia, frostbite, carbon monoxide), skis and snowshoes, navigation and "
                     "survival."),
]

# US Navy nonresident training courses (NAVEDTRA), the toolkit's collection "Courses": correspondence courses made
# for sailors to study on their own, with Distribution Statement A on their own front page (checked by hand on
# 2026-11-18: "DISTRIBUTION STATEMENT A: Approved for public release; distribution is unlimited.", and again by the
# builder in every PDF); US government works. Copies from the Internet Archive (the Navy's own course site needs a
# login).
COURSE = dict(FIELD, group="course", publisher="Naval Education and Training Professional Development and "
              "Technology Center (US Navy)")
PDF_DOCS += [
    dict(COURSE, name="navy_basic_machines", title="Basic Machines (NAVEDTRA 14037, 1994)",
         subject="Mechanics", archive="navedtra-14037-basic-machines-1994",
         description="The US Navy's course on levers, pulleys, the wheel and axle, the inclined plane, the screw, "
                     "gears, work and power, hydraulics, and machines built from them."),
    dict(COURSE, name="navy_culinary_specialist", title="Culinary Specialist (NAVEDTRA 15008, 2010)",
         subject="Cooking and food service", archive="navedtra-15008-culinary-specialist-2010",
         description="The US Navy's course for cooks: food safety and sanitation, nutrition, menus, recipes and "
                     "cooking methods, baking, and running a galley."),
    dict(COURSE, name="navy_hospital_corpsman", title="Hospital Corpsman (NAVEDTRA 14295, 2000)",
         subject="Medicine and first aid", archive="hospital-corpsman-nonresident-training-course-navedtra-14295",
         description="The US Navy's course for hospital corpsmen: anatomy and physiology, first aid and emergency "
                     "care, patient care, pharmacy, laboratory, dental and preventive medicine."),
]

# When each manual and course was published (the year on its own title page; "published" in textbooks.json, which the
# toolkit uses to rank newer works higher).
PUBLISHED_YEARS = {
    "army_atp_3_50_21_survival": "2018", "army_fm_4_25_11_first_aid": "2002", "army_fm_3_25_26_map_reading": "2001",
    "army_fm_4_25_12_field_sanitation": "2002", "army_fm_5_125_rigging": "1995",
    "army_tc_3_97_61_mountaineering": "2025-11", "army_tc_21_3_cold_weather": "1986", "navy_basic_machines": "1994",
    "navy_culinary_specialist": "2010", "navy_hospital_corpsman": "2000",
}
for _e in PDF_DOCS:
    if _e["name"] in PUBLISHED_YEARS:
        _e["published"] = PUBLISHED_YEARS[_e["name"]]

# United Kingdom: Maritime and Coastguard Agency and Ministry of Defence publications on gov.uk ("All content is
# available under the Open Government Licence v3.0, except where otherwise stated", checked on each publication page
# at every build; the PDFs say "© Crown copyright"). Checked by hand on 2026-11-18.
UK = dict(group="fieldmanual", country="United Kingdom", licence="OGL-UK-3.0",
          licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
          licence_text=r"Open Government Licence v3\.0")
PDF_DOCS += [
    dict(UK, name="uk_mca_msn_1560_survival_at_sea", title="Survival at Sea (MSN 1560, Maritime and Coastguard "
         "Agency)", subject="Sea survival", publisher="Maritime and Coastguard Agency (UK)",
         page="https://www.gov.uk/government/publications/msn-1560-survival-at-sea", pdf_pattern=r"msn1560\.pdf$",
         description="The UK merchant shipping notice on sea survival training: what a basic sea survival course "
                     "teaches (lifejackets, liferafts, abandoning ship, survival in the water and in a craft)."),
    dict(UK, name="uk_mod_jsp_375_first_aid", title="First Aid at Work in Defence (JSP 375, volume 1, chapter 5)",
         subject="First aid", publisher="Ministry of Defence (UK)",
         page="https://www.gov.uk/government/publications/management-of-health-and-safety-in-defence-chapter-5-"
              "first-aid-jsp-375-volume-1", pdf_pattern=r"First_Aid[^/]*\.pdf$",
         description="The UK Ministry of Defence's rules for first aid at work: assessing first-aid needs, "
                     "first-aiders, kits and rooms, and training."),
]

# The Navy Electricity and Electronics Training Series (NEETS): module number and title. The copies named
# "NEETSModuleNN" on the Internet Archive have their words (other copies are scans without a text layer, which the
# builder refuses).
NEETS = [
    (1, "Introduction to Matter, Energy, and Direct Current"),
    (2, "Introduction to Alternating Current and Transformers"),
    (3, "Introduction to Circuit Protection, Control, and Measurement"),
    (4, "Introduction to Electrical Conductors, Wiring Techniques, and Schematic Reading"),
    (5, "Introduction to Generators and Motors"),
    (6, "Introduction to Electronic Emission, Tubes, and Power Supplies"),
    (7, "Introduction to Solid-State Devices and Power Supplies"),
    (8, "Introduction to Amplifiers"),
    (9, "Introduction to Wave Generation and Wave Shaping"),
    (10, "Introduction to Wave Propagation, Transmission Lines, and Antennas"),
    (13, "Introduction to Number Systems and Logic"),
    (14, "Introduction to Microelectronics"),
    (16, "Introduction to Test Equipment"),
    (19, "The Technician's Handbook"),
    (22, "Introduction to Digital Computers"),
    (24, "Introduction to Fiber Optics"),
]
PDF_DOCS += [
    dict(COURSE, name=f"navy_neets_module_{n:02d}", title=f"NEETS Module {n}: {words}",
         subject="Electricity and electronics", archive=f"NEETSModule{n:02d}",
         description=f"Module {n} of the US Navy's Electricity and Electronics Training Series (NEETS), a self-study "
                     f"course: {words[0].lower() + words[1:]}.")
    for n, words in NEETS
]

# Provincial publications under Alberta's open licence (open.alberta.ca: "Usage / Licence ... Open Government Licence
# - Alberta", checked by hand on 2026-11-18 and again from each page at every build).
ALBERTA = dict(group="government", country="Canada", licence="OGL-Alberta",
               licence_url="https://open.alberta.ca/licence", publisher="Government of Alberta",
               licence_text=r"Licence\s+Open Government Licence - Alberta")
PDF_DOCS += [
    dict(ALBERTA, name="alberta_drivers_guide", title="Alberta Driver's Guide: cars and light trucks",
         subject="Driving", page="https://open.alberta.ca/publications/drivers-guide",
         pdf_pattern=r"drivers-guide[^/]*\.pdf$",
         description="Alberta's official driver's guide for cars and light trucks: licences, the rules of the "
                     "road, signs and signals, safe driving, and sharing the road."),
    dict(ALBERTA, name="alberta_spot_the_difference_elder_abuse",
         title="Spot the difference: elder abuse, bullying, frauds and scams (Alberta)", subject="Seniors' safety",
         page="https://open.alberta.ca/publications/spot-the-difference-learn-to-recognize-elder-abuse-bullying-and-"
              "frauds-and-scams",
         description="Alberta's guide to telling elder abuse, bullying, frauds and scams apart, and where to get "
                     "help."),
    dict(ALBERTA, name="alberta_its_your_money_financial_abuse",
         title="It's your money: protect yourself from financial abuse (Alberta)", subject="Seniors' safety",
         page="https://open.alberta.ca/publications/its-your-money-financial-abuse",
         description="Alberta's guide for older adults on recognising and preventing financial abuse."),
    dict(ALBERTA, name="alberta_power_outages", title="Power outages: be prepared (Alberta)",
         subject="Emergency preparedness", page="https://open.alberta.ca/publications/power-outages",
         description="Alberta's emergency fact sheet on getting ready for a power outage and staying safe during "
                     "one."),
]

# Federal laws of Canada: the Reproduction of Federal Law Order (SI/97-5) allows copying and publishing them without
# charge (with due diligence for accuracy, and a copy is not presented as the official version: said on each book's
# welcome page).
CANADA_LAW = "Reproduction of Federal Law Order (Canada)"

ALLOWED = {
    "CC0": "open", "PD": "open", "OGL": "open", "CC BY": "open", "CC BY-SA": "share-alike",
    CANADA_LAW: "open",
    US_GOV: "open", "OGL-UK-3.0": "open", "OGL-Alberta": "open", "OGL-Canada": "open", "OGL-Ontario": "open", "OGL-BC": "open",
    "CC BY-NC": "non-commercial", "CC BY-NC-SA": "non-commercial",
    # Old works in the US public domain (more than 95 years after publication): the historic newspapers.
    "Public domain (published before 1931)": "open",
}

# The whole-and-unchanged rule (the owner's decision of 2026-11-18). A NoDerivatives licence (CC BY-ND, CC BY-NC-ND)
# or another no-changes licence (NO_CHANGES) is allowed when the work is kept WHOLE with its TEXT UNCHANGED and only
# its format is converted for accessibility: Creative Commons 4.0 section 2(a)(4) allows "technical modifications
# necessary to exercise the Licensed Rights in all media and formats" and says they "never produce Adapted
# Material"; CC 2.5 and 3.0 have the same clause ("modifications as are technically necessary to exercise the
# rights in other media and formats"). So such a work is never excerpted, cut, summarised or reworded: only its
# HTML is cleaned up (menus, scripts and decorative pictures left out, headings and the descriptions of pictures
# kept, links kept), and every page carries the credit, the licence's name and address, the original address and
# the line "Converted to an accessible format; the text is unchanged." (build_textbooks.UNCHANGED). Such entries
# have "unchanged": True; the builder gives their books unchanged=True and licence_kind "no-changes" (or
# "non-commercial-no-changes"). Without that mark an ND licence is still refused.
WHOLE_AND_UNCHANGED = True
NO_CHANGES = {
    # W3C Document License (2023): "permission to copy, and distribute the contents of this document ... in any
    # medium for any purpose" on condition of the URL, the copyright notice and the status; no modifications.
    "W3C Document License": "no-changes",
}

# What was looked at and not included, with the reason (shown in textbooks.json and the toolkit's manual).
NOT_INCLUDED = [
    ("BCcampus Open Textbooks (Canada)", "Its Pressbooks site answers automated requests with a bot check "
     "(Cloudflare \"Just a moment\"), also for the book exports, so it cannot be fetched automatically."),
    ("eCampusOntario Open Library (Canada)", "Its Pressbooks site refuses automated requests (403), robots.txt "
     "included."),
    ("CAUL Open Educational Resources Collective (Australia and New Zealand)", "Its Pressbooks site refuses "
     "automated requests (403)."),
    ("OpenLearn, The Open University (UK)", "www.open.edu refuses automated requests (403), robots.txt included; "
     "its courses are mostly CC BY-NC-SA and could be added if the Open University allows automated download."),
    ("Oak National Academy (UK)", "Its curriculum resources are offered through an API that needs a sign-up key; "
     "not fetched without one."),
    ("Scoilnet and NCCA (Ireland)", "No open licence was found for their materials."),
    ("Te Pūkenga and New Zealand open textbooks", "No openly licensed collection with an automated download was "
     "found."),
    ("NCERT textbooks (India)", "Copyright NCERT, all rights reserved: not openly licensed."),
    ("NROER (India)", "Licences differ per item and were not checked one by one."),
    ("DOT4D and UCT open textbooks (South Africa)", "Their repository (open.uct.ac.za) allows automated download, "
     "but each book's licence was not checked one by one yet; add them to DSPACE after checking each."),
    ("Commonwealth of Learning (oasis.col.org)", "The repository is mostly reports; its open textbooks were not "
     "checked one by one yet."),
    ("UNESCO (unesdoc.unesco.org)", "Its document pages refuse automated requests (403)."),
    ("OECD", "Its licences differ per publication and were not checked one by one."),
    ("Siyavula Mathematical Literacy and Life Sciences", "Only PDFs without a reader version with text formulas; "
     "left out until their pictures of formulas can be described."),
]

# Non-profit reference works looked at for "Reference, non-profits" and not built, with the reason. Many good ones
# are already in the Kiwix library (Khan Academy, PhET, MedlinePlus, Ready.gov, the CDC's Travelers' Health, the
# OpenStreetMap wiki, DevDocs with the MDN Web Docs for HTML, CSS and JavaScript, Appropedia, Wikivoyage, Project
# Gutenberg, the Post Disaster, Medical and Water Treatment libraries), so they are not built again here.
NONPROFIT_NOT_INCLUDED = [
    ("Hesperian Health Guides (Where There Is No Doctor and the other HealthWiki books)", "Their own \"open "
     "copyright\" lets anyone copy and adapt the books to be given away free or at cost, not for profit, and asks to "
     "be contacted before an adaptation; it is not a standard licence the builder can check, and the toolkit is a "
     "paid program, so Hesperian's written permission is asked for first."),
    ("MSF medical guidelines (Médecins Sans Frontières)", "Copyright MSF; its robots.txt also shuts out automated "
     "readers of AI companies."),
    ("IFRC International First Aid, Resuscitation and Education Guidelines", "The IFRC website refuses automated "
     "requests (403), and no open licence was found."),
    ("ICEB Guidelines for Technical Material (2014)", "Its PDF states no licence (the Rules of Unified English "
     "Braille do, and are built whole and unchanged); ask ICEB."),
    ("BANA guidelines (Braille Formats and the other BANA codes)", "Copyright of the Braille Authority of North "
     "America; no Creative Commons or other open licence was found automatically (its site states none on the "
     "pages read). Ask BANA, or check each PDF's copyright page by hand."),
    ("Practical Action technical briefs", "Their resource pages state no licence; each PDF would have to be checked "
     "one by one."),
    ("Steps to Justice (CLEO, Ontario)", "Copyright CLEO: pages may be printed whole for non-commercial or "
     "educational use, not repackaged."),
    ("Paths to Literacy (Perkins School for the Blind and TSBVI)", "All rights reserved (Perkins terms and "
     "conditions); permission needed."),
    ("DAISY Consortium knowledge base", "© The DAISY Consortium; no open licence was found."),
    ("American Printing House, NFB, AFB, CNIB, RNIB and BANA guides", "Copyright of each organisation; only with "
     "written permission."),
    ("CK-12", "Its own CK-12 licence and terms of use, not a standard open licence the builder can check."),
    ("Our World in Data articles", "CC BY and allowed, but their pages are built around interactive charts that do "
     "not read well as text; its chart pictures with their titles are used in the picture describer's training "
     "instead (packs/ngo_packs.py)."),
    ("UNICEF and UNHCR publications", "Licences differ per publication (many all rights reserved); not checked one "
     "by one."),
    ("AARP, GCFGlobal (Goodwill) and WebAIM", "No open licence was found (copyright of each organisation)."),
]
# Courses and the manuals of other English-speaking forces and coastguards looked at on 2026-11-18 and not built (yet),
# with the licence line found or why it could not be checked.
COURSES_AND_FORCES_NOT_INCLUDED = [
    ("NEETS modules from other Internet Archive copies (\"NeetsModule1introductionTo...\")", "Scans without a text "
     "layer: the builder refuses them; the \"NEETSModuleNN\" copies with words are used."),
    ("Saylor Academy courses (learn.saylor.org)", "Its footer: \"content authored by Saylor University is available "
     "under a Creative Commons Attribution 3.0 Unported license. Third-party materials are the copyright of their "
     "respective owners\". Allowed, but each course mixes Saylor's own pages with third-party readings in a Moodle "
     "site; not built yet (each page's own licence would have to be checked)."),
    ("Open Yale Courses (oyc.yale.edu)", "Its terms: \"Most of the lectures and course material within Open Yale "
     "Courses are licensed under a Creative Commons Attribution-Noncommercial-Share Alike 3.0 license\" (third-party "
     "content excluded). Allowed (not for commercial use); not built yet."),
    ("MIT OpenCourseWare", "CC BY-NC-SA 4.0 (each course page). Not in the Kiwix library. Most course material is "
     "PDF lecture notes and videos; not built yet."),
    ("OpenLearn (The Open University)", "Its site refuses automated requests (403), as noted above."),
    ("Coursera, edX, Udemy", "Copyright, all rights reserved."),
    ("US Army Correspondence Course Program subcourses", "Not found as copies with text and Distribution Statement A "
     "on the Internet Archive in this search; the Army's own site needs a login."),
    ("US Coast Guard Navigation Rules handbook", "The Internet Archive's copies are lending-library scans that "
     "cannot be downloaded; uscg.mil refuses automated requests (403)."),
    ("Other US Navy rate training manuals (Boatswain's Mate, Damage Controlman, Engineman, Seabee rates)", "Not "
     "found as downloadable copies with text on the Internet Archive in this search (Damage Controlman only as a "
     "microfiche scan)."),
    ("armypubs.army.mil, marines.mil, uscg.mil, fema.gov", "armypubs' robots.txt disallows every automated reader; the "
     "others refuse automated requests (403). Internet Archive copies are used where their own front matter shows "
     "Distribution Statement A."),
    ("UK Ministry of Defence and Maritime and Coastguard Agency, other documents", "gov.uk: \"All content is "
     "available under the Open Government Licence v3.0, except where otherwise stated\". Allowed; the MOD publishes "
     "few non-combat training documents there (most are policy). Two are built; more can be added to PDF_DOCS."),
    ("RNLI (charity)", "Its website refuses automated requests (403); its guides are its own copyright."),
    ("Canadian Armed Forces and Canadian Coast Guard manuals; Transport Canada's Safe Boating Guide", "Crown "
     "copyright under the canada.ca terms (non-commercial reproduction only, not an open licence): personal use at "
     "most, so not built. The Safe Boating Guide's page was not found at its old address (404)."),
    ("Australian Department of Defence and Australian Maritime Safety Authority", "amsa.gov.au refuses automated "
     "requests (403), its copyright page included, so its CC BY statement could not be checked."),
    ("New Zealand Defence Force and Maritime New Zealand", "maritimenz.govt.nz refuses automated requests (403) to "
     "its copyright page, so its CC BY statement could not be checked."),
    ("Irish Defence Forces and Irish Coast Guard", "Not checked in this search."),
]
NOT_INCLUDED = NOT_INCLUDED + NONPROFIT_NOT_INCLUDED + COURSES_AND_FORCES_NOT_INCLUDED

# ====================================================================== reference groups added on 2026-11-18
# The toolkit's collections ("group" in textbooks.json -> the name it shows). New keys: law, consumer, health,
# disability, science.
GROUPS = {
    "textbooks": "Textbooks", "reference": "Reference works", "nonprofit": "Reference, non-profits",
    "government": "Reference, governments", "university": "Reference, universities",
    "fieldmanual": "Reference, field manuals", "course": "Courses",
    "law": "Reference, laws and rights", "consumer": "Reference, consumer and money",
    "health": "Reference, health and safety", "disability": "Reference, disability and accessibility",
    "science": "Reference, science and nature",
    # Publications that come out again and again (periodicals.py; keys pub:...), and history:
    "reports": "Reference, government reports", "journals": "Articles, open-access journals",
    "news": "News, open-licensed", "periodicals": "Magazines and newsletters", "history": "Reference, history",
}

# W3C WAI documents under the W3C Document License, kept whole and unchanged (WHOLE_AND_UNCHANGED). Checked by hand
# on 2026-11-18: www.w3.org/WAI/about/using-wai-material/ says "Most WAI material (including the standards and
# guidelines) is provided under the W3C Document License, which grants permission to copy and distribute complete
# documents in any medium for any purpose, without fee or royalty, provided that you include the URL, copyright,
# and status (if it exists)"; robots.txt allows /TR/ and /WAI/.
W3C_NOTICE = ("Copyright © World Wide Web Consortium (W3C®). Used under the W3C Document License "
              "(https://www.w3.org/copyright/document-license-2023/); the status of each document is on its page.")
W3C = dict(group="disability", subject="Web accessibility", publisher="W3C Web Accessibility Initiative (WAI)",
           country="International", licence="W3C Document License",
           licence_url="https://www.w3.org/copyright/document-license-2023/", unchanged=True, notice=W3C_NOTICE,
           licence_page="https://www.w3.org/WAI/about/using-wai-material/",
           licence_text=r"W3C Document License\s*,?\s*which grants permission to copy and distribute complete documents "
                        r"in any medium",
           page_mark=r"World Wide Web Consortium", sitemap="", unit_rules=[], units="",
           content=(r"<main\b[^>]*>", r"</main>"), drop=[], limit=200)
NONPROFIT += [
    dict(W3C, name="w3c_wcag22", title="Web Content Accessibility Guidelines (WCAG) 2.2",
         source="https://www.w3.org/TR/WCAG22/",
         description="The W3C Recommendation WCAG 2.2 (with its status section), whole and unchanged.",
         start=["https://www.w3.org/WAI/standards-guidelines/wcag/"],
         pages=r"^https://www\.w3\.org/TR/WCAG22/$", content=(r"<body\b[^>]*>", r"</body>"), limit=1),
    dict(W3C, name="w3c_understanding_wcag22", title="Understanding WCAG 2.2 (W3C WAI)",
         source="https://www.w3.org/WAI/WCAG22/Understanding/",
         description="W3C's explanations of each WCAG 2.2 success criterion: its intent, benefits, examples and "
                     "techniques; every page whole and unchanged.",
         start=["https://www.w3.org/WAI/WCAG22/Understanding/"],
         pages=r"^https://www\.w3\.org/WAI/WCAG22/Understanding/[a-z0-9-]+(?:\.html)?$"),
    dict(W3C, name="w3c_wai_tutorials", title="Web Accessibility Tutorials (W3C WAI)",
         source="https://www.w3.org/WAI/tutorials/",
         description="W3C WAI's tutorials on accessible page structure, menus, tables, forms, images and carousels; "
                     "every page whole and unchanged.",
         start=["https://www.w3.org/WAI/tutorials/"], units=r"^https://www\.w3\.org/WAI/tutorials/[a-z-]+/$",
         pages=r"^https://www\.w3\.org/WAI/tutorials/[a-z-]+/[a-z0-9-]+/$"),
]

# The ICEB Rules of Unified English Braille, kept whole and unchanged (WHOLE_AND_UNCHANGED). Its copyright page,
# checked by hand on 2026-11-18 and checked again in the PDF at every build (pdf_licence_text): "This publication is
# licensed under the Creative Commons Attribution-Noncommercial-No Derivative Works 2.5 Australia Licence."
# iceb.org's robots.txt only disallows /wp-admin/. The braille examples are in Unicode braille in the PDF's text.
PDF_DOCS += [
    dict(name="iceb_rules_of_ueb_2024", title="Rules of Unified English Braille, Third Edition 2024",
         subject="Braille (Unified English Braille)", group="disability", country="International",
         publisher="International Council on English Braille (ICEB)", licence="CC BY-NC-ND 2.5 AU",
         licence_url="https://creativecommons.org/licenses/by-nc-nd/2.5/au/", unchanged=True,
         pdf="https://iceb.org/wp-content/uploads/2025/10/Rules-of-Unified-English-Braille-2024.pdf",
         page="https://iceb.org/ueb.html", licence_page="https://iceb.org/ueb.html",
         licence_text=r"Rules of Unified English Braille",
         pdf_licence_text=r"Creative\s+Commons\s+Attribution\W*Noncommercial\W*No\s+Derivative\s+Works\s+2\.5\s+"
                          r"Australia",              # (the PDF's text has an odd hyphen character there)
         notice="Third Edition © 2024, International Council on English Braille. Second Edition © 2013 (original © "
                "2010), Round Table on Information Access for People with Print Disabilities Inc. and International "
                "Council on English Braille. Licensed under the Creative Commons Attribution-Noncommercial-No "
                "Derivative Works 2.5 Australia Licence.",
         description="The rulebook of Unified English Braille (UEB), the whole book with its braille examples in "
                     "Unicode braille, unchanged."),
]

# US federal works: 17 U.S.C. 105, as quoted on govinfo.gov's policy page (checked at every build for the laws, the
# IRS and Medicare publications, whose own sites state no copyright policy).
GOVINFO_POLICY = "https://www.govinfo.gov/about/policies"
GOVINFO_TEXT = r"Copyright protection under this title is not available for any work of the United States Government"
DOJ_POLICY = "https://www.justice.gov/legalpolicies"
DOJ_TEXT = r"Unless otherwise indicated, information on Department of Justice websites is in the public domain"

LICENCE_LINES.update({
    "w3c_document_license": "www.w3.org/WAI/about/using-wai-material/: \"Most WAI material (including the standards "
                            "and guidelines) is provided under the W3C Document License, which grants permission to "
                            "copy and distribute complete documents in any medium for any purpose, without fee or "
                            "royalty, provided that you include the URL, copyright, and status (if it exists). This "
                            "does not allow modifications or the creation of derivative works\" (kept whole and "
                            "unchanged: WHOLE_AND_UNCHANGED).",
    "iceb_ueb": "Rules of Unified English Braille, Third Edition 2024, page ii: \"This publication is licensed under "
                "the Creative Commons Attribution-Noncommercial-No Derivative Works 2.5 Australia Licence.\" (kept "
                "whole and unchanged: WHOLE_AND_UNCHANGED).",
    "us_federal": "govinfo.gov/about/policies (Public Domain & Copyright Notice): \"Title 17, Section 105, United "
                  "States Code, provides that: Copyright protection under this title is not available for any work "
                  "of the United States Government\". Used for the US Code and the Code of Federal Regulations (from "
                  "govinfo.gov), and for IRS and Medicare publications.",
    "doj_ada": "www.justice.gov/legalpolicies: \"Unless otherwise indicated, information on Department of Justice "
               "websites is in the public domain and may be copied and distributed without permission.\" (ADA.gov is "
               "the Department of Justice's ADA website.)",
    "section508": "www.section508.gov/website-policies/: \"Most material on our site is free of copyright and may be "
                  "copied and distributed without permission.\"",
    "cfpb": "www.consumerfinance.gov/privacy/website-privacy-policy/: \"Information created by the CFPB is in the "
            "public domain and you may reproduce, publish, or otherwise use it without the Bureau's permission.\"",
    "niddk": "www.niddk.nih.gov/copyright: \"The majority of information on this site is copyright free and can be "
             "freely downloaded and reproduced.\" (\"Generally, copyrighted materials will include a copyright "
             "statement.\")",
    "fda": "www.fda.gov website policies: the contents of the FDA website \"both text and graphics — are not "
           "copyrighted. They are in the public domain and may be republished, reprinted and otherwise used freely by "
           "anyone without the need to obtain permission from FDA.\"",
    "nci": "www.cancer.gov/policies/copyright-reuse: \"Unless otherwise indicated, all text within National Cancer "
           "Institute (NCI) products is free of copyright and may be reused without our permission.\" Graphics are a "
           "mix, so only text and picture descriptions are kept; changed pages say they are adapted from NCI.",
    "usgs": "www.usgs.gov/information-policies-and-instructions/copyrights-and-credits: \"While the content of most "
            "USGS websites is in the U.S. Public Domain, not all information, illustrations, or photographs on our "
            "site are.\" (text kept, pictures left out)",
    "nhs": "www.nhs.uk/our-policies/terms-and-conditions/: \"Copyright and database rights in NHS Website Content are "
           "released free-of-charge under the current version of the Open Government Licence (\"OGL\"), except where "
           "specified\".",
    "legislation_gov_uk": "Every legislation.gov.uk page: \"All content is available under the Open Government Licence "
                          "v3.0 except where otherwise stated\".",
    "justice_laws_canada": "Reproduction of Federal Law Order, SI/97-5 (laws-lois.justice.gc.ca): \"Anyone may, "
                           "without charge or request for permission, reproduce enactments and consolidations of "
                           "enactments of the Government of Canada ... provided due diligence is exercised in ensuring "
                           "the accuracy of the materials reproduced and the reproduction is not represented as an "
                           "official version.\"",
})

# ---------------------------------------------------------------------- laws and regulations (lawdoc_book, key law:)
# Each is one ZIM book, so a reader downloads only the laws wanted. Fields: see build_textbooks.lawdoc_book and
# law_pages. US laws come from govinfo.gov's annual editions (the newest one is found at build time).
US_LAW = dict(group="law", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
              licence_page=GOVINFO_POLICY, licence_text=GOVINFO_TEXT)
CFR = dict(US_LAW, publisher="Office of the Federal Register (Code of Federal Regulations, annual edition from "
           "govinfo.gov)", split=r'<h3 class="cfr-section"', unit=r'<h2 class="cfr-subpart"')
USC = dict(US_LAW, publisher="Office of the Law Revision Counsel, US House of Representatives (United States Code, "
           "from govinfo.gov)", content=(r"<body[^>]*>", r"</body>"), split=r'<h3 class="section-head"',
           unit=r'<h3 class="subchapter-head"',
           drop=[r'<h4 class="note-head">.*?(?=<h3 class="(?:section|subchapter)-head"|\Z)',
                 r'<div class="analysis">.*?</div>', r"<!--.*?-->"])


def _cfr(name, title, subject, t, vol, part, description, subpart="", group="law"):
    """A CFR part as a LAWS entry."""
    where = f"title-{t}/part-{part}" + (f"/subpart-{subpart}" if subpart else "")
    return dict(CFR, name=name, title=title, subject=subject, group=group,
                cfr=dict(title=t, volume=vol, part=part, subpart=subpart),
                source=f"https://www.ecfr.gov/current/{where}", description=description)


def _usc(name, title, subject, t, files, description):
    """Chapters of the US Code as a LAWS entry."""
    return dict(USC, name=name, title=title, subject=subject, usc=[dict(title=t, file=f) for f in files],
                source=f"https://uscode.house.gov/browse/prelim@title{t}", description=description)


CANADA = dict(group="law", country="Canada", licence=CANADA_LAW,
              licence_url="https://laws-lois.justice.gc.ca/eng/regulations/SI-97-5/FullText.html",
              licence_page="https://laws-lois.justice.gc.ca/eng/regulations/SI-97-5/FullText.html",
              licence_text=r"Anyone may, without charge or request for permission, reproduce enactments",
              publisher="Department of Justice Canada (Justice Laws website)",
              notice="This copy is not the official version; the official version is on the Justice Laws website "
                     "(laws-lois.justice.gc.ca).",
              content=(r"<div class='docContents' id='docCont'>", r"<footer|</main>"),
              split=r'<h2 class="(?:Part|Subheading)"', date_pattern=r"last amended(?:</a>)? on (\d{4}-\d\d-\d\d)")


def _canada(name, title, subject, path, description):
    """A federal act or regulation of Canada from Justice Laws (path "acts/A-0.6")."""
    url = f"https://laws-lois.justice.gc.ca/eng/{path}/FullText.html"
    return dict(CANADA, name=name, title=title, subject=subject, urls=[url], source=url, description=description)


# legislation.gov.uk makes every subsection number, such as "(1)" or "(a)", a heading of its own; they become the
# start of their paragraph (a number can be wrapped in <ins> when it was inserted by a later act).
UK_NUMBER = r'<h[2-6]><span class="num">((?:<[^>]+>)*\([^<]*\)(?:</[^>]+>)*)</span></h[2-6]>'
UK_LAW = dict(group="law", country="United Kingdom", licence="OGL-UK-3.0",
              licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
              licence_text=r"Open Government Licence v3\.0", publisher="The National Archives (legislation.gov.uk)",
              content=(r"<article\b[^>]*>", r"</article>"), split=r'<section class="(?:section|schedule)"',
              unit=r'<section class="(?:part|chapter)"',
              drop=[r'<footer class="annotations">.*?</footer>', r'<a class="noteRef[^"]*"[^>]*>.*?</a>',
                    r'<span class="noteRef[^"]*"[^>]*>.*?</span>'],
              rewrite=[(UK_NUMBER + r"((?:\s*<div\b[^>]*>)*)\s*<p>", r"\2<p>\1 "),   # "(1)" starts its paragraph
                       (UK_NUMBER, r"<span>\1 </span>"),
                       (r'</span><span class="heading">', '</span> <span class="heading">')],
              date_pattern=r'http-equiv="Last-Modified" content="([0-9-]+)',
              notice="Revised (consolidated) text as published on legislation.gov.uk; amendment notes left out.")


def _uk(name, title, subject, path, description):
    """A UK act from legislation.gov.uk (path "ukpga/2010/15")."""
    return dict(UK_LAW, name=name, title=title, subject=subject,
                licence_page=f"https://www.legislation.gov.uk/{path}/contents",
                urls=[f"https://www.legislation.gov.uk/{path}/data.html"],
                source=f"https://www.legislation.gov.uk/{path}/contents", description=description)


LAWS = [
    # United States Code (statutes)
    _usc("us_code_ada", "Americans with Disabilities Act (42 U.S.C. chapter 126)", "Disability rights", 42,
         ["chap126"], "The Americans with Disabilities Act as codified in the United States Code: employment, state "
         "and local government services and public transportation, public accommodations, telecommunications relay "
         "services, and miscellaneous provisions."),
    _usc("us_code_rehabilitation_act", "Rehabilitation Act (29 U.S.C. chapter 16)", "Disability rights", 29,
         ["chap16"], "The Rehabilitation Act of 1973 as codified: vocational rehabilitation services, independent "
         "living, the Access Board, and sections 501, 503, 504 and 508 (nondiscrimination and accessible "
         "electronic and information technology)."),
    _usc("us_code_idea", "Individuals with Disabilities Education Act (20 U.S.C. chapter 33)", "Disability and "
         "education", 20, ["chap33"], "The Individuals with Disabilities Education Act (IDEA) as codified: free "
         "appropriate public education, individualized education programs, procedural safeguards, and early "
         "intervention for infants and toddlers."),
    _usc("us_code_fair_housing", "Fair Housing Act (42 U.S.C. chapter 45)", "Housing rights", 42, ["chap45"],
         "The Fair Housing Act as codified: discrimination in the sale, rental and financing of housing, including "
         "reasonable accommodations and accessible design for people with disabilities, and enforcement."),
    _usc("us_code_consumer_credit", "Consumer Credit Protection Act (15 U.S.C. chapter 41)", "Consumer credit", 15,
         ["chap41"], "The Consumer Credit Protection Act as codified: Truth in Lending, Fair Credit Billing, Fair "
         "Credit Reporting, Equal Credit Opportunity, Fair Debt Collection Practices and Electronic Fund Transfers."),
    _usc("us_code_social_security_benefits", "Social Security Act: retirement, survivors and disability insurance "
         "(Title II) and Supplemental Security Income (Title XVI)", "Social Security", 42,
         ["chap7-subchapII", "chap7-subchapXVI"], "Titles II and XVI of the Social Security Act as codified (42 U.S.C. "
         "chapter 7, subchapters II and XVI): retirement, survivors and disability insurance benefits, and "
         "Supplemental Security Income for aged, blind and disabled people."),
    # Code of Federal Regulations
    _cfr("cfr_14_382_air_travel_disability", "Nondiscrimination on the Basis of Disability in Air Travel (14 CFR "
         "part 382)", "Air travel and disability", 14, 4, 382, "The Department of Transportation's Air Carrier Access "
         "Act rules: assistance, wheelchairs and other devices, service animals, seating, accessible information "
         "and websites, and complaints."),
    _cfr("cfr_28_35_ada_state_local_government", "ADA Title II regulations: state and local government services "
         "(28 CFR part 35)", "Disability rights", 28, 1, 35, "The Department of Justice's rules for state and local "
         "governments under ADA Title II, including effective communication and the web and mobile app "
         "accessibility rule."),
    _cfr("cfr_28_36_ada_public_accommodations", "ADA Title III regulations: public accommodations and commercial "
         "facilities (28 CFR part 36)", "Disability rights", 28, 1, 36, "The Department of Justice's rules for "
         "businesses open to the public under ADA Title III: auxiliary aids and services, service animals, "
         "examinations and courses, and new construction and alterations."),
    _cfr("cfr_29_1630_ada_employment", "ADA Title I regulations: employment (29 CFR part 1630)", "Disability rights",
         29, 4, 1630, "The Equal Employment Opportunity Commission's rules for employment under ADA Title I, with its "
         "interpretive guidance (reasonable accommodation, undue hardship, medical examinations)."),
    _cfr("cfr_24_100_fair_housing", "Fair Housing Act regulations (24 CFR part 100)", "Housing rights", 24, 1, 100,
         "The Department of Housing and Urban Development's rules on discriminatory housing practices, including "
         "reasonable accommodations, reasonable modifications and accessible design."),
    _cfr("cfr_49_37_transportation_ada", "Transportation services for individuals with disabilities (49 CFR part 37)",
         "Transportation and disability", 49, 1, 37, "The Department of Transportation's ADA rules for buses, rail, "
         "paratransit and other public and private transportation services."),
    dict(_cfr("cfr_47_telecom_accessibility", "Telecommunications accessibility rules (47 CFR parts 6, 7 and 14, and "
              "part 64 subpart F)", "Telecommunications and disability", 47, 1, 6, "The Federal Communications "
              "Commission's accessibility rules: telecommunications equipment and services (parts 6 and 7), advanced "
              "communications services (part 14) and telecommunications relay services (part 64, subpart F)."),
         cfr=[dict(title=47, volume=1, part=6), dict(title=47, volume=1, part=7), dict(title=47, volume=1, part=14),
              dict(title=47, volume=3, part=64, subpart="F")], source="https://www.ecfr.gov/current/title-47"),
    _cfr("cfr_36_1194_section_508_standards", "Section 508 Standards and Section 255 Guidelines (36 CFR part 1194)",
         "Digital accessibility", 36, 3, 1194, "The US Access Board's Information and Communication Technology "
         "standards and guidelines (Section 508 of the Rehabilitation Act and Section 255 of the Communications "
         "Act), which incorporate WCAG 2.0 Level AA."),
    _cfr("cfr_34_300_idea_regulations", "IDEA regulations: assistance to states for the education of children with "
         "disabilities (34 CFR part 300)", "Disability and education", 34, 2, 300, "The Department of Education's "
         "rules for special education under IDEA Part B: evaluations, individualized education programs, "
         "procedural safeguards and discipline."),
    _cfr("cfr_21_101_food_labeling", "Food labeling (21 CFR part 101)", "Food labeling", 21, 2, 101, "The Food and "
         "Drug Administration's food labeling rules: nutrition facts, ingredient lists, allergens, nutrient content "
         "and health claims."),
    # Canada (federal)
    _canada("canada_accessible_canada_act", "Accessible Canada Act (S.C. 2019, c. 10)", "Disability rights",
            "acts/A-0.6", "Canada's federal accessibility law: identifying, removing and preventing barriers in "
            "federal jurisdiction, accessibility plans, the Accessibility Commissioner and Accessibility Standards "
            "Canada."),
    _canada("canada_human_rights_act", "Canadian Human Rights Act (R.S.C. 1985, c. H-6)", "Human rights",
            "acts/H-6", "Canada's federal human rights law: prohibited grounds of discrimination (including "
            "disability), discriminatory practices, the Canadian Human Rights Commission and Tribunal."),
    _canada("canada_employment_equity_act", "Employment Equity Act (S.C. 1995, c. 44)", "Employment rights",
            "acts/E-5.401", "Canada's federal employment equity law for women, Indigenous peoples, persons with "
            "disabilities and members of visible minorities."),
    _canada("canada_accessible_canada_regulations", "Accessible Canada Regulations (SOR/2021-241)",
            "Disability rights", "regulations/SOR-2021-241", "The regulations under the Accessible Canada Act: "
            "accessibility plans, feedback processes, progress reports, and penalties."),
    _canada("canada_accessible_transportation_regulations", "Accessible Transportation for Persons with Disabilities "
            "Regulations (SOR/2019-244)", "Transportation and disability", "regulations/SOR-2019-244",
            "The Canadian Transportation Agency's rules for air, rail, bus and ferry travel by persons with "
            "disabilities: services, communication, equipment and terminals."),
    # United Kingdom
    _uk("uk_equality_act_2010", "Equality Act 2010 (United Kingdom)", "Equality and disability rights",
        "ukpga/2010/15", "The UK's equality law: protected characteristics including disability, discrimination, "
        "reasonable adjustments, services, work, education, premises and transport."),
    _uk("uk_consumer_rights_act_2015", "Consumer Rights Act 2015 (United Kingdom)", "Consumer rights",
        "ukpga/2015/15", "The UK's consumer law: rights for goods, digital content and services, unfair terms, and "
        "enforcement."),
    _uk("uk_care_act_2014", "Care Act 2014 (United Kingdom)", "Social care", "ukpga/2014/23",
        "England's law on adult social care and support: assessments, eligibility, care and support plans, carers "
        "and safeguarding."),
    _uk("uk_landlord_and_tenant_act_1985", "Landlord and Tenant Act 1985 (United Kingdom)", "Tenants and landlords",
        "ukpga/1985/70", "UK law on rented homes: information for tenants, repairing obligations, service charges "
        "and fitness for human habitation."),
]

# "More titles" (key laws-more): larger regulations built only when asked for.
LAWS_MORE = [
    _cfr("cfr_36_1191_ada_aba_guidelines", "ADA and ABA Accessibility Guidelines (36 CFR part 1191)",
         "Accessible buildings", 36, 3, 1191, "The US Access Board's accessibility guidelines for buildings and "
         "facilities under the ADA and the Architectural Barriers Act (scoping and technical requirements)."),
    _cfr("cfr_12_1026_regulation_z", "Truth in Lending (Regulation Z, 12 CFR part 1026)", "Consumer credit", 12, 9,
         1026, "The Consumer Financial Protection Bureau's Truth in Lending rules: credit cards, mortgages and other "
         "consumer credit disclosures, with the official interpretations."),
    _cfr("cfr_12_1006_regulation_f", "Debt Collection Practices (Regulation F, 12 CFR part 1006)", "Debt collection",
         12, 9, 1006, "The Consumer Financial Protection Bureau's rules for debt collectors."),
    _cfr("cfr_12_1022_regulation_v", "Fair Credit Reporting (Regulation V, 12 CFR part 1022)", "Credit reports", 12,
         8, 1022, "The Consumer Financial Protection Bureau's rules under the Fair Credit Reporting Act."),
    _cfr("cfr_20_404_social_security_disability", "Federal Old-Age, Survivors and Disability Insurance (20 CFR part "
         "404)", "Social Security", 20, 2, 404, "The Social Security Administration's rules for retirement, survivors "
         "and disability benefits, including the disability evaluation process and the listing of impairments."),
    _cfr("cfr_20_416_supplemental_security_income", "Supplemental Security Income for the Aged, Blind, and Disabled "
         "(20 CFR part 416)", "Social Security", 20, 3, 416, "The Social Security Administration's rules for "
         "Supplemental Security Income."),
    _cfr("cfr_45_84_section_504_hhs", "Section 504 regulations of the Department of Health and Human Services (45 CFR "
         "part 84)", "Disability rights", 45, 1, 84, "Nondiscrimination on the basis of disability in programs "
         "receiving HHS funds (health care, social services), including accessible medical equipment and web "
         "content."),
]

# ---------------------------------------------------------------------- government web guides (webguide_book, guide:)
GOV_GUIDES = [
    dict(name="section508_gov", title="Section508.gov: accessible technology guidance", subject="Digital "
         "accessibility", group="disability", publisher="US General Services Administration (Section508.gov)",
         country="United States", licence=US_GOV, licence_url=US_GOV_URL, source="https://www.section508.gov/",
         description="The US government's guidance on accessible information and communication technology: "
                     "creating accessible documents, PDFs, presentations, spreadsheets and video; testing; buying "
                     "accessible products; and running an accessibility programme.",
         licence_page="https://www.section508.gov/website-policies/",
         licence_text=r"Most material on our site is free of copyright", page_mark="", start=[], units="",
         pages=r"^https://www\.section508\.gov/(develop|test|buy|manage|create|training|content|policy)/[a-z0-9/-]*$",
         sitemap="https://www.section508.gov/sitemap.xml",
         unit_rules=[(r"/create/", "Create accessible content"), (r"/develop/", "Design and develop"),
                     (r"/test/", "Test"), (r"/buy/", "Buy accessible products"), (r"/manage/", "Manage a programme"),
                     (r"/(training|content|policy)/", "Training and policy")],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=400),
    dict(name="ada_gov_guidance", title="ADA.gov: guidance on the Americans with Disabilities Act",
         subject="Disability rights", group="disability", publisher="US Department of Justice, Civil Rights "
         "Division (ADA.gov)", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
         source="https://www.ada.gov/", description="The Department of Justice's plain-language ADA guidance: service "
         "animals, effective communication, web accessibility, mobility devices, businesses, state and local "
         "governments, and how to file a complaint.",
         licence_page=DOJ_POLICY, licence_text=DOJ_TEXT, page_mark="", start=[], units="",
         pages=r"^https://www\.ada\.gov/(resources|topics)/[a-z0-9-]+/$", sitemap="https://www.ada.gov/sitemap.xml",
         unit_rules=[(r"/topics/", "Topics"), (r"/resources/", "Guidance and resources")],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=150),
    dict(name="cfpb_ask_cfpb", title="Ask CFPB: answers to money questions", subject="Money and credit",
         group="consumer", publisher="Consumer Financial Protection Bureau (CFPB)", country="United States",
         licence=US_GOV, licence_url=US_GOV_URL, source="https://www.consumerfinance.gov/ask-cfpb/",
         description="The Consumer Financial Protection Bureau's plain answers to common money questions: credit "
                     "reports and scores, credit cards, debt collection, bank accounts, mortgages, auto loans, "
                     "student loans, prepaid cards, money transfers, and frauds and scams.",
         licence_page="https://www.consumerfinance.gov/privacy/website-privacy-policy/",
         licence_text=r"Information created by the CFPB is in the public domain", page_mark="", start=[], units="",
         pages=r"^https://www\.consumerfinance\.gov/ask-cfpb/[a-z0-9-]+-en-\d+/$",
         sitemap="https://www.consumerfinance.gov/sitemap.xml", unit_rules=[],
         content=(r"<main\b[^>]*>", r"</main>"),
         drop=[r"<nav\b.*?</nav>", r'<div class="[^"]*(?:feedback|related|o-well)[^"]*".*?</div>'], limit=900),
    dict(name="niddk_health_information", title="NIDDK health information: diabetes, digestive, kidney and other "
         "diseases", subject="Health", group="health", publisher="National Institute of Diabetes and Digestive and "
         "Kidney Diseases (NIDDK), National Institutes of Health", country="United States", licence=US_GOV,
         licence_url=US_GOV_URL, source="https://www.niddk.nih.gov/health-information",
         description="Patient health information from the NIDDK: diabetes, digestive diseases, kidney disease, "
                     "weight management, liver, urologic, endocrine and blood diseases, diet and nutrition, and "
                     "diagnostic tests.",
         licence_page="https://www.niddk.nih.gov/copyright",
         licence_text=r"The majority of information on this site is copyright free", page_mark="", start=[],
         units="", pages=r"^https://www\.niddk\.nih\.gov/health-information/[a-z0-9/-]+$",
         sitemap="https://www.niddk.nih.gov/sitemap.xml",
         unit_rules=[(r"/diabetes", "Diabetes"), (r"/digestive-diseases", "Digestive diseases"),
                     (r"/kidney-disease", "Kidney disease"), (r"/weight-management", "Weight management"),
                     (r"/liver-disease", "Liver disease"), (r"/urologic-diseases", "Urologic diseases"),
                     (r"/endocrine-diseases", "Endocrine diseases"), (r"/diet-nutrition", "Diet and nutrition"),
                     (r".", "Other topics")],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>", r"<aside\b.*?</aside>"], limit=600),
    dict(name="fda_consumer_updates", title="FDA Consumer Updates", subject="Health and safety", group="health",
         publisher="US Food and Drug Administration (FDA)", country="United States", licence=US_GOV,
         licence_url=US_GOV_URL, source="https://www.fda.gov/consumers/consumer-updates",
         description="The FDA's plain-language articles on using medicines, food safety, dietary supplements, "
                     "medical devices, cosmetics and other products safely.",
         licence_page="https://www.fda.gov/about-fda/about-website/website-policies",
         licence_text=r"They are in the public domain and may be republished", page_mark="",
         start=["https://www.fda.gov/consumers/consumer-updates"], units="",
         pages=r"^https://www\.fda\.gov/consumers/consumer-updates/[a-z0-9-]+$",
         sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=120),
    dict(name="nci_about_cancer", title="National Cancer Institute: about cancer", subject="Cancer",
         group="health", publisher="National Cancer Institute (NCI), National Institutes of Health",
         country="United States", licence=US_GOV, licence_url=US_GOV_URL,
         source="https://www.cancer.gov/about-cancer",
         description="The National Cancer Institute's information for patients and families: understanding "
                     "cancer, causes and prevention, screening, diagnosis, treatment, side effects, coping, and "
                     "advanced cancer. Adapted from the National Cancer Institute (text only).",
         licence_page="https://www.cancer.gov/policies/copyright-reuse",
         licence_text=r"all text within National Cancer Institute \(NCI\) products is free of copyright",
         page_mark="", start=[], units="", pages=r"^https://www\.cancer\.gov/about-cancer/[a-z0-9/-]+$",
         sitemap="https://www.cancer.gov/sitemap.xml",
         unit_rules=[(r"/understanding", "Understanding cancer"), (r"/causes-prevention", "Causes and prevention"),
                     (r"/screening", "Screening"), (r"/diagnosis-staging", "Diagnosis and staging"),
                     (r"/treatment", "Treatment"), (r"/coping", "Coping with cancer"),
                     (r"/advanced-cancer", "Advanced cancer"), (r".", "More")],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"],
         changes="adapted from the National Cancer Institute: made into web pages with the site's menus and "
                 "pictures left out (their descriptions kept)", limit=500),
    dict(name="nhs_health_a_to_z", title="NHS Health A to Z (conditions)", subject="Health", group="health",
         publisher="NHS England (nhs.uk)", country="United Kingdom", licence="OGL-UK-3.0",
         licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
         source="https://www.nhs.uk/conditions/",
         description="The NHS website's guides to health conditions from A to Z: symptoms, causes, diagnosis, "
                     "treatment and when to get help (UK services and phone numbers).",
         licence_page="https://www.nhs.uk/our-policies/terms-and-conditions/",
         licence_text=r"released free-of-charge under the current version of the Open Government Licence",
         page_mark="", start=["https://www.nhs.uk/conditions/"], units="",
         pages=r"^https://www\.nhs\.uk/conditions/[a-z0-9-]+/$", sitemap="", unit_rules=[],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>", r"<aside\b.*?</aside>"], limit=1200),
    dict(name="govuk_disabled_people", title="GOV.UK: disabled people (benefits, rights, equipment and care)",
         subject="Disability", group="disability", publisher="UK Government (GOV.UK)", country="United Kingdom",
         licence="OGL-UK-3.0", licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
         source="https://www.gov.uk/browse/disabilities",
         description="GOV.UK's guides for disabled people and carers: benefits (PIP, Attendance Allowance, Access "
                     "to Work), rights under the Equality Act, the Blue Badge and transport, and help at home.",
         licence_page="https://www.gov.uk/help/terms-conditions",
         licence_text=r"published under the Open Government Licence", page_mark=r"Open Government Licence v3\.0",
         start=["https://www.gov.uk/browse/disabilities"], units=r"^https://www\.gov\.uk/browse/disabilities/[a-z-]+$",
         pages=r"^https://www\.gov\.uk/(?!search|help|contact|cymraeg|government|browse|world|cookies|privacy|"
               r"accessibility|sign-in|account)[a-z0-9-]+$",
         fetch_as=(r"$", "/print"), sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"),
         drop=[r'<div class="gem-c-contextual-sidebar.*?</div>', r"<nav\b.*?</nav>"], limit=300),
    dict(name="govuk_benefits", title="GOV.UK: benefits", subject="Benefits", group="consumer",
         publisher="UK Government (GOV.UK)", country="United Kingdom", licence="OGL-UK-3.0",
         licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
         source="https://www.gov.uk/browse/benefits",
         description="GOV.UK's guides to UK benefits: Universal Credit, benefits for families, carers, disability, "
                     "unemployment, low income, heating and housing, and how to apply or complain.",
         licence_page="https://www.gov.uk/help/terms-conditions",
         licence_text=r"published under the Open Government Licence", page_mark=r"Open Government Licence v3\.0",
         start=["https://www.gov.uk/browse/benefits"], units=r"^https://www\.gov\.uk/browse/benefits/[a-z-]+$",
         pages=r"^https://www\.gov\.uk/(?!search|help|contact|cymraeg|government|browse|world|cookies|privacy|"
               r"accessibility|sign-in|account)[a-z0-9-]+$",
         fetch_as=(r"$", "/print"), sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"),
         drop=[r'<div class="gem-c-contextual-sidebar.*?</div>', r"<nav\b.*?</nav>"], limit=300),
    dict(name="uk_highway_code", title="The Highway Code (Great Britain)", subject="Driving and road safety",
         group="government", publisher="Department for Transport and Driver and Vehicle Standards Agency (GOV.UK)",
         country="United Kingdom", licence="OGL-UK-3.0",
         licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
         source="https://www.gov.uk/guidance/the-highway-code",
         description="The official Highway Code for Great Britain: rules for pedestrians, cyclists, horse riders, "
                     "motorcyclists and drivers, road signs and markings, and the hierarchy of road users.",
         licence_page="https://www.gov.uk/guidance/the-highway-code",
         licence_text=r"Open Government Licence v3\.0", page_mark=r"Open Government Licence v3\.0",
         start=["https://www.gov.uk/guidance/the-highway-code"], units="",
         pages=r"^https://www\.gov\.uk/guidance/the-highway-code/[a-z0-9-]+$", sitemap="", unit_rules=[],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=60),
    dict(name="usgs_this_dynamic_earth", title="This Dynamic Earth: the story of plate tectonics (USGS)",
         subject="Earth science", group="science", publisher="US Geological Survey (USGS)",
         country="United States", licence=US_GOV, licence_url=US_GOV_URL,
         source="https://pubs.usgs.gov/gip/dynamic/dynamic.html",
         description="The USGS general-interest book on plate tectonics (published in print in 1996, online "
                     "edition): its history, how the theory developed, plate motions, hotspots, and plate "
                     "tectonics and people.",
         licence_page="https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
         licence_text=r"the content of most USGS websites is in the U\.S\. Public Domain", page_mark="",
         start=["https://pubs.usgs.gov/gip/dynamic/dynamic.html"], units="",
         pages=r"^https://pubs\.usgs\.gov/gip/dynamic/[A-Za-z_]+\.html$", sitemap="", unit_rules=[],
         content=(r"(?i)<body[^>]*>", r"(?i)</body>"), drop=[r"(?i)<img\b[^>]*>"], published="1996-02", limit=60),
]

# ---------------------------------------------------------------------- official PDFs of these groups (pdfdoc_book)
US_PDF = dict(country="United States", licence=US_GOV, licence_url=US_GOV_URL, licence_page=GOVINFO_POLICY,
              licence_text=GOVINFO_TEXT)
PDF_DOCS += [
    dict(US_PDF, name="irs_pub_17_your_federal_income_tax", group="consumer",
         title="Your Federal Income Tax (IRS Publication 17)", subject="Taxes",
         publisher="Internal Revenue Service (IRS)", pdf="https://www.irs.gov/pub/irs-pdf/p17.pdf",
         page="https://www.irs.gov/forms-pubs/about-publication-17",
         description="The IRS's complete plain-language guide to filing a US individual income tax return: filing "
                     "status, dependents, income, adjustments, deductions and credits."),
    dict(US_PDF, name="irs_pub_907_tax_highlights_disabilities", group="disability",
         title="Tax Highlights for Persons With Disabilities (IRS Publication 907)", subject="Taxes and disability",
         publisher="Internal Revenue Service (IRS)", pdf="https://www.irs.gov/pub/irs-pdf/p907.pdf",
         page="https://www.irs.gov/forms-pubs/about-publication-907",
         description="Tax rules that matter to people with disabilities: disability income, the credit for the "
                     "elderly or disabled, impairment-related work expenses, medical expenses and ABLE accounts."),
    dict(US_PDF, name="irs_pub_554_tax_guide_seniors", group="consumer",
         title="Tax Guide for Seniors (IRS Publication 554)", subject="Taxes",
         publisher="Internal Revenue Service (IRS)", pdf="https://www.irs.gov/pub/irs-pdf/p554.pdf",
         page="https://www.irs.gov/forms-pubs/about-publication-554",
         description="The IRS's guide for people 65 and older: filing requirements, retirement and Social "
                     "Security income, the higher standard deduction, and credits."),
    dict(US_PDF, name="medicare_and_you", group="health", title="Medicare & You (the official Medicare handbook)",
         subject="Health insurance", publisher="Centers for Medicare & Medicaid Services (CMS)",
         pdf="https://www.medicare.gov/publications/10050-medicare-and-you.pdf",
         page="https://www.medicare.gov/publications",
         description="The official US government Medicare handbook: what Parts A, B, C and D cover, costs, "
                     "enrolment periods, Medicare Advantage and Medigap, drug coverage, help paying costs, and your "
                     "rights."),
    dict(US_PDF, name="ada_2010_standards_accessible_design", group="disability",
         title="2010 ADA Standards for Accessible Design", subject="Accessible buildings",
         publisher="US Department of Justice", pdf="https://www.ada.gov/assets/pdfs/2010-design-standards.pdf",
         page="https://www.ada.gov/law-and-regs/design-standards/2010-stds/", licence_page=DOJ_POLICY,
         licence_text=DOJ_TEXT, published="2010-09-15",
         description="The Department of Justice's 2010 ADA Standards for Accessible Design with its guidance: "
                     "accessible routes, entrances, doors, ramps, elevators, toilet rooms, signs (including braille "
                     "and raised characters), parking and other elements."),
]

# Keys of the workflow and the builder (see expand_keys).
def expand_keys(words):
    """The build keys a request asks for: "all" (every book except "laws-more"), osbooks, nonprofit, fieldmanuals,
    government (Alberta's PDFs), courses, laws (sources.LAWS), laws-more (sources.LAWS_MORE), guides
    (sources.GOV_GUIDES), group:<group> (every web guide, PDF and law of that group, such as group:health), or one
    key: osbooks:<repository>, siyavula, dspace, nonprofit:<name>, pdf:<name>, guide:<name>, law:<name>."""
    pdfs = lambda g: [f"pdf:{e['name']}" for e in PDF_DOCS if e["group"] == g]   # noqa: E731
    every = [f"osbooks:{r}" for r in OSBOOKS] + ["siyavula", "dspace"] + \
        [f"nonprofit:{e['name']}" for e in NONPROFIT] + [f"pdf:{e['name']}" for e in PDF_DOCS] + \
        [f"guide:{e['name']}" for e in GOV_GUIDES] + [f"law:{e['name']}" for e in LAWS]
    keys = []
    for w in words or ["all"]:
        if w == "all":
            keys += every
        elif w == "osbooks":
            keys += [f"osbooks:{r}" for r in OSBOOKS]
        elif w == "nonprofit":
            keys += [f"nonprofit:{e['name']}" for e in NONPROFIT]
        elif w in ("fieldmanuals", "government", "courses"):
            keys += pdfs({"fieldmanuals": "fieldmanual", "courses": "course"}.get(w, w))
        elif w == "laws":
            keys += [f"law:{e['name']}" for e in LAWS]
        elif w == "laws-more":
            keys += [f"law:{e['name']}" for e in LAWS_MORE]
        elif w == "guides":
            keys += [f"guide:{e['name']}" for e in GOV_GUIDES]
        elif w.startswith("group:"):
            g = w[6:]
            keys += pdfs(g) + [f"guide:{e['name']}" for e in GOV_GUIDES if e["group"] == g] + \
                [f"law:{e['name']}" for e in LAWS + LAWS_MORE if e.get("group", "law") == g]
        elif w == "publications" or w.startswith("pub:"):
            import periodicals                    # here, not at the top: periodicals imports the builder
            keys += periodicals.expand_keys(["pub:all" if w == "publications" else w])
        else:
            keys.append(w)
    return list(dict.fromkeys(keys))

# Looked at on 2026-11-18 for the groups law, consumer, health, disability, science and books, and not built (yet),
# with the reason.
REFERENCE_NOT_INCLUDED = [
    ("FTC consumer advice (consumer.ftc.gov)", "Public domain (US government), but the site refuses automated "
     "requests (403)."),
    ("Social Security Administration publications (ssa.gov/pubs)", "Public domain, but ssa.gov refuses automated "
     "requests (403); the Social Security Act and its regulations are built instead (law group)."),
    ("FoodSafety.gov, USDA FSIS, CPSC, OSHA, NHTSA, CDC (with NIOSH) and the National Institute on Aging",
     "Public domain, but their sites refuse automated requests (403, or a bot check at nia.nih.gov)."),
    ("NOAA National Weather Service JetStream", "Public domain (weather.gov: \"The information on National Weather "
     "Service (NWS) Web pages are in the public domain\"), but the JetStream pages refuse automated requests (403)."),
    ("USDA MyPlate recipes (myplate.gov)", "The site could not be reached from the build (502)."),
    ("USDA Complete Guide to Home Canning, Ready.gov, CDC Travelers' Health, MedlinePlus, NHS Medicines A to Z, "
     "Citizens Information (Ireland), Wikibooks (with its Cookbook), Wikisource, iFixit, Project Gutenberg",
     "Already in the Kiwix library."),
    ("1911 Encyclopaedia Britannica", "Public domain; its clean transcription is on Wikisource, which is in the Kiwix "
     "library (wikisource_en_all). A separate book would need about 40,000 page requests; not built."),
    ("Standard Ebooks", "CC0 and not in the Kiwix library, but its robots.txt shuts AI agents out of the book texts; "
     "the same public-domain works are in Kiwix's Project Gutenberg."),
    ("WordNet and Webster's 1913 dictionary", "WordNet's licence is permissive and it is not in the Kiwix library, "
     "but it needs a dictionary builder (one page per word); not built yet. No clean Webster's 1913 source was "
     "checked."),
    ("Directory of Open Access Books and OAPEN", "Answer this build's requests with 429 (too many requests) after an "
     "earlier lock-out; their CC BY books can be added through DSPACE later, one checked record at a time."),
    ("Pressbooks Directory, Global Text Project, Saylor Academy books, Unglue.it, FLOSS Manuals", "Not built in this "
     "pass (licences differ per book; flossmanuals.net's certificate is not valid)."),
    ("FDIC Money Smart", "US government work, but fdic.gov states no copyright policy for its own pages and the "
     "curriculum is PDFs per module; not built yet."),
    ("USA.gov benefit guides", "US government work (usa.gov/government-copyright explains federal works); asks a "
     "10-second crawl delay; not built yet."),
    ("US Access Board guides", "The Guide to the ADA Standards is no longer at its address (404) and the site states "
     "no copyright policy; the Board's standards are built from the CFR (36 CFR parts 1191 and 1194)."),
    ("Job Accommodation Network (askjan.org)", "Its robots.txt shuts out AI crawlers (ClaudeBot, anthropic-ai, GPTBot "
     "and others) and no reuse terms were found (it is run by West Virginia University); not built."),
    ("NLS (Library of Congress) braille transcribing instruction materials", "loc.gov: \"we generally do not own the "
     "rights to materials in our collections\"; the copyright of each NLS manual was not established; not built."),
    ("NASA education guides", "NASA: content \"generally [is] not subject to copyright\", but pages mix third-party "
     "material; not built in this pass."),
    ("eCFR (ecfr.gov) and uscode.house.gov", "The eCFR's robots.txt disallows its full-text services and its reader "
     "needs JavaScript; uscode.house.gov's pages were not found (404). The CFR and US Code are read from govinfo.gov's "
     "annual editions instead (public domain)."),
    ("US Code titles 26 (tax) and 47 (communications), 49 U.S.C. 41705", "Whole titles are very large; IRS "
     "Publication 17 and the FCC's and DOT's accessibility rules (47 CFR, 14 CFR part 382) are built instead."),
    ("California statutes and state guides", "leginfo.legislature.ca.gov refuses automated requests (403); the DMV "
     "handbook and other agency pages say \"Copyright © State of California\" with no reuse licence, so they are not "
     "built (California public records are often public domain, but no agency licence line was found)."),
    ("Florida Statutes and Florida agency guides", "The Legislature's site says \"Copyright © 1995-2026 The Florida "
     "Legislature\" (Florida claims copyright in its statutes compilation); agency sites state no reuse licence."),
    ("Washington, New York and Texas statutes", "app.leg.wa.gov's robots.txt disallows everything; New York's Open "
     "Legislation needs an API key; Texas's terms were not checked. State statutes themselves are not copyrightable "
     "(Georgia v. Public.Resource.Org, 2020), but each site's terms and robots.txt decide."),
    ("State attorneys general, health, driver-handbook and blind-services agency guides", "Copyright of each state "
     "(\"Copyright © State of ...\" footers); not checked one by one."),
    ("Ontario e-Laws", "The King's Printer \"permits any person to reproduce the text and images contained in the "
     "statutes, regulations and judicial decisions without seeking permission and without charge\", but e-Laws pages "
     "need JavaScript; not built yet."),
    ("BC Laws (British Columbia)", "The King's Printer Licence – British Columbia allows commercial and "
     "non-commercial use with its statement, but bclaws.gov.bc.ca's robots.txt allows only Googlebot and Bingbot."),
    ("Alberta King's Printer laws", "qp.alberta.ca's robots.txt disallows everything; kings-printer.alberta.ca says "
     "its materials are \"owned by the Government of Alberta and protected by law\". (open.alberta.ca's OGL "
     "publications are built.)"),
    ("Nova Scotia legislation", "nslegislature.ca closed the connection to automated requests."),
    ("canada.ca guidance on the Accessible Canada Act", "canada.ca terms allow non-commercial reproduction only, "
     "not an open licence; the Act and its regulations are built from Justice Laws instead."),
    ("New Zealand legislation (legislation.govt.nz) and govt.nz", "Answer automated requests with a bot challenge "
     "(202, empty page)."),
    ("Australia: legislation.gov.au, Services Australia, ACCC, healthdirect", "legislation.gov.au's PDFs can be "
     "downloaded, but its CC BY 4.0 statement is shown only by JavaScript and not in the PDFs, so it cannot be checked "
     "at build time; Services Australia and the ACCC copyright pages could not be read; healthdirect: all rights "
     "reserved."),
    ("Irish Statute Book (Ireland)", "Re-use under the Oireachtas (Open Data) PSI Licence, which \"incorporates the "
     "Creative Commons Attribution 4.0 International License\": allowed, but only as-enacted texts in an old table "
     "layout without headings; not built yet."),
    ("South Africa (gov.za) and India Code (indiacode.nic.in)", "No copyright page was found on gov.za (404); "
     "indiacode.nic.in did not answer in time."),
]
NOT_INCLUDED = NOT_INCLUDED + REFERENCE_NOT_INCLUDED
