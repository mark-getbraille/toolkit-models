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
    # Added on 2026-11-21 from OpenStax's own list of approved repositories (content-manager-approved-books,
    # checked with git ls-remote): Python programming, the nursing books and Principles of Management.
    "introduction-python-programming", "nursing-external-bundle", "principles-of-management-bundle",
]

# OpenStax books written for high school (openstax.org's catalogue lists them with K-12 subjects): put in the K-12
# group with grades 9-12. OpenStax's other books with K-12 subjects are college books also used in high school
# ("High school and college").
OPENSTAX_HIGH_SCHOOL = {"physics", "statistics", "biology-ap-courses", "college-physics-ap-courses-2e", "algebra-1"}

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
    # Added on 2026-11-21 (www.siyavula.com/read lists them; the builder checks each reader page's licence line:
    # Computer Applications Technology and Mathematical Literacy state none there, so they are left out and said).
    ("mathematics", 7, "Mathematics Grade 7", "Mathematics"),
    ("mathematics", 8, "Mathematics Grade 8", "Mathematics"),
    ("mathematics", 9, "Mathematics Grade 9", "Mathematics"),
    ("life-sciences", 10, "Life Sciences Grade 10", "Biology"),
    ("information-technology", 10, "Information Technology Grade 10", "Information technology"),
    ("information-technology", 11, "Information Technology Grade 11", "Information technology"),
    ("information-technology", 12, "Information Technology Grade 12", "Information technology"),
    ("computer-applications-technology", 10, "Computer Applications Technology Grade 10", "Computer applications"),
    ("computer-applications-technology", 11, "Computer Applications Technology Grade 11", "Computer applications"),
    ("computer-applications-technology", 12, "Computer Applications Technology Grade 12", "Computer applications"),
    ("mathematical-literacy", 10, "Mathematical Literacy Grade 10", "Mathematical literacy"),
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
    # UK Parliament's licence for Hansard and other Parliamentary copyright material (like the OGL).
    "Open Parliament Licence v3.0": "open",
    # US drug labels as published by DailyMed (NLM) and openFDA (public domain, CC0): see medications.LICENCE_LINES.
    "Public domain (US drug labeling)": "open",
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

# Sites whose terms forbid or limit downloads by programs even where robots.txt would allow them: an original on
# one of these hosts gets "may_download": false with this reason in textbooks.json "originals"
# (build_textbooks.download_permission); the owner can still open the link in a browser. Every other original is
# downloadable only when its licence allows copying and the site's robots.txt allows programs (checked at build time).
NO_AUTOMATED_DOWNLOAD = {
    "www.khanacademy.org": "Khan Academy's terms limit automated access (khanacademy.org is never read here; its "
                           "lessons come only through Kolibri Studio).",
    "www.ck12.org": "CK-12's own terms of use, not a standard open licence (ck12.org is never read here; its lessons "
                    "come only through Kolibri Studio).",
}

# What was looked at and not included, with the reason (shown in textbooks.json and the toolkit's manual).
NOT_INCLUDED = [
    ("BCcampus Open Textbooks (Canada), from its own site", "Its Pressbooks site answers automated requests with a "
     "bot check (Cloudflare \"Just a moment\"), and its robots.txt shuts out AI companies' readers. Its books are "
     "built from BCcampus' Kolibri Studio channel instead (courses.py, key course:bccampus)."),
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
    ("Siyavula Mathematical Literacy, Life Sciences 11-12", "Only PDFs without a reader version with text formulas; "
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
     "copyright under the terms of the canada.ca web pages (non-commercial reproduction only, not an open licence): "
     "personal use at most, so not built. The Safe Boating Guide's page was not found at its old address (404). The "
     "publications deposited on open.canada.ca under the Open Government Licence - Canada are different: commercial "
     "use allowed (Transport Canada's are built as pub:canada_ogl:transport-...)."),
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
    # The official labels of medicines (medications.py; keys medicines, med:...):
    "medicines": "Reference, medicines", "vet_medicines": "Reference, animal medicines",
    # School books, kindergarten to grade 12 (the owner's request of 2026-11-21): K12_GUIDES, the K-12 PDFs, Siyavula,
    # OpenStax's high school books and the K-12 courses of courses.py.
    "k12": "School books (K-12)",
    # Cookbooks and recipes (cookbooks.py; keys cookbooks, cook:...), the owner's request of 2026-11-21.
    "cookbooks": "Reference, cookbooks and recipes",
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
         licence_url="https://creativecommons.org/licenses/by-nc-nd/2.5/au/", unchanged=True, split_sections=True,
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
         sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"),
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
         sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"),
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
    key: osbooks:<repository>, siyavula, dspace, nonprofit:<name>, pdf:<name>, guide:<name>, law:<name>; medicines
    (every medicine book, medications.py) or med:<piece>; publications or pub:<piece> (periodicals.py). "all" does
    not include the medicines or the publications: ask for them by name."""
    pdfs = lambda g: [f"pdf:{e['name']}" for e in PDF_DOCS if e["group"] == g]   # noqa: E731
    every = [f"osbooks:{r}" for r in OSBOOKS] + ["siyavula", "dspace"] + \
        [f"nonprofit:{e['name']}" for e in NONPROFIT] + [f"pdf:{e['name']}" for e in PDF_DOCS] + \
        [f"guide:{e['name']}" for e in GOV_GUIDES] + [f"law:{e['name']}" for e in LAWS] + \
        [f"k12:{e['name']}" for e in K12_GUIDES]
    keys = []
    for w in words or ["all"]:
        if w == "all":
            keys += every
        elif w in ("k12", "opencourses", "personaluse") or w.startswith("course:"):
            # School books (K-12), the open courses, the personal-use courses (courses.py)
            import courses                        # here, not at the top: courses imports the builder
            if w == "k12":
                keys += [f"k12:{e['name']}" for e in K12_GUIDES] + pdfs("k12") + ["siyavula"] + \
                    [f"osbooks:{r}" for r in ("physics", "statistics", "biology-bundle", "college-physics-bundle")]
            keys += courses.expand_keys([w])
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
        elif w == "drinks":
            # Wine, beer, spirits and soft drinks, and making them (2026-11-21): the hand-written guide and the TTB
            # wine manual (drinks_reference.py), then every law, guide, Wikibook and PDF of the group "drinks"
            keys += ["drinks:guide", "drinks:ttb_wine_bam"] + expand_keys(["group:drinks"]) + \
                [f"nonprofit:{e['name']}" for e in NONPROFIT if e.get("group") == "drinks"] + \
                ["law:cfr_21_101_food_labeling"]
        elif w.startswith("group:"):
            g = w[6:]
            keys += pdfs(g) + [f"guide:{e['name']}" for e in GOV_GUIDES if e["group"] == g] + \
                [f"law:{e['name']}" for e in LAWS + LAWS_MORE if e.get("group", "law") == g]
        elif w == "medicines" or w.startswith("med:"):
            import medications                    # here, not at the top: medications imports the builder
            keys += medications.expand_keys([w])
        elif w == "cookbooks" or w.startswith("cook:"):
            import cookbooks                      # here, not at the top: cookbooks imports the builder
            keys += cookbooks.expand_keys([w])
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
    ("canada.ca guidance on the Accessible Canada Act", "The terms of the canada.ca web pages allow non-commercial "
     "reproduction only, not an open licence; the Act and its regulations are built from Justice Laws instead. (The "
     "publications deposited on open.canada.ca under the Open Government Licence - Canada allow commercial use: "
     "pub:canada_ogl.)"),
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

# ====================================================================== North American animals (added 2026-11-21)
# Reference works on the wild and domestic animals of the United States and Canada, for the Assistant (group
# "science"). Checked by hand on 2026-11-21; the licence line is checked again at every build.
#
# NOAA Fisheries' species directory: www.fisheries.noaa.gov/disclaimer, "Copyright Policy: Information created by
# the U.S. government and presented on U.S. government websites is not subject to copyright in the United States."
# (It also asks for the credit "Courtesy: National Oceanic and Atmospheric Administration", given in the notice, and
# says it marks text and pictures of others: only the text is kept, and a picture only as its description.) Its
# robots.txt allows /species/; its sitemap lists 309 species profiles.
LICENCE_LINES["noaa_fisheries"] = ("www.fisheries.noaa.gov/disclaimer: \"Information created by the U.S. government and "
                                   "presented on U.S. government websites is not subject to copyright in the United "
                                   "States.\"")
GOV_GUIDES += [
    dict(name="noaa_fisheries_species_directory", title="NOAA Fisheries species directory: whales, dolphins, seals, "
         "sea turtles, fish and shellfish of US waters", subject="Animals (marine)", group="science",
         publisher="NOAA Fisheries (National Marine Fisheries Service)", country="United States", licence=US_GOV,
         licence_url=US_GOV_URL, source="https://www.fisheries.noaa.gov/species-directory",
         description="NOAA Fisheries' profile of each marine species it manages or protects: what it looks like, "
                     "where it lives, what it eats, its life history, threats, its status under the Endangered "
                     "Species Act and the Marine Mammal Protection Act, and how it is fished or protected. Marine "
                     "mammals, sea turtles, sharks and rays, fish, corals, shellfish and other invertebrates.",
         notice="Courtesy: National Oceanic and Atmospheric Administration (NOAA Fisheries).",
         licence_page="https://www.fisheries.noaa.gov/disclaimer",
         licence_text=r"Information created by the U\.S\. government and presented on U\.S\. government websites is "
                      r"not subject to copyright",
         page_mark="", start=[], units="", pages=r"^https://www\.fisheries\.noaa\.gov/species/[a-z0-9-]+$",
         sitemap="https://www.fisheries.noaa.gov/sitemap.xml",
         unit_rules=[(r"whale|dolphin|porpoise|seal|sea-lion|otter|manatee|walrus|orca|narwhal|beluga|dugong",
                      "Marine mammals"),
                     (r"turtle", "Sea turtles"), (r"coral", "Corals"),
                     (r"shark|-ray$|stingray|skate|sawfish|manta", "Sharks and rays"),
                     (r"crab|lobster|shrimp|abalone|clam|oyster|scallop|squid|octopus|conch|urchin|sea-cucumber|"
                      r"mussel|geoduck|snail", "Shellfish and other invertebrates"),
                     (r".", "Fish")],
         content=(r"<main\b[^>]*>", r"</main>"),
         drop=[r"<nav\b.*?</nav>", r"<figure\b.*?</figure>",
               r'<div class="[^"]*(?:teaser|related|promo|card-list|feature-story)[^"]*".*?</div>\s*</div>'],
         changes="made into web pages with the site's menus, related stories and pictures left out (only NOAA's own "
                 "text is kept)", limit=320),
]

# Old field guides and natural histories of North American animals, in the US public domain (published before 1931,
# more than 95 years ago), from the Internet Archive's scans with their machine-read text. The builder checks the
# item's publication year at every build (build_textbooks.archive_year). They are OLD: names, ranges, numbers and
# advice are out of date (some species have been renamed, some are now rare or extinct, and they come from before
# modern conservation and animal welfare), and the machine-read text has the scanner's mistakes. Each description
# says so.
OLD_PD = dict(group="science", country="United States", licence="Public domain (published before 1931)",
              licence_url="https://www.copyright.gov/help/faq/faq-duration.html", old_public_domain=True,
              changes="its scanned pages' machine-read text (with the scanner's mistakes) made into web pages, ten "
                      "pages at a time or one per chapter")
OLD_NOTE = (" Published in {year}: an old book whose names, ranges and advice are out of date, kept for its "
            "descriptions of the animals.")
PDF_DOCS += [
    dict(OLD_PD, name="reed_bird_guide_land_birds_1909", title="Bird Guide: Land Birds East of the Rockies (Chester A. "
         "Reed, 1909)", subject="Birds", publisher="Chester A. Reed (Doubleday, Page and Company)",
         archive="birdguidelandbir00reedrich", published="1909",
         description="A pocket field guide to the land birds of eastern North America, from parrots to bluebirds: "
                     "each bird's size, colours and markings, song, nest and eggs, and range." + OLD_NOTE.format(
                         year=1909)),
    dict(OLD_PD, name="chapman_handbook_birds_eastern_na_1895", title="Handbook of Birds of Eastern North America "
         "(Frank M. Chapman, 1895)", subject="Birds", publisher="Frank M. Chapman (D. Appleton and Company)",
         archive="handbookofbirdso00chaprich", published="1895",
         description="The American Museum of Natural History ornithologist's handbook of the birds of eastern North "
                     "America, with keys to the species, descriptions of plumage, nests, eggs, songs and ranges." +
                     OLD_NOTE.format(year=1895)),
    dict(OLD_PD, name="anthony_field_book_na_mammals_1928", title="Field Book of North American Mammals (H. E. "
         "Anthony, 1928)", subject="Mammals", publisher="H. E. Anthony (G. P. Putnam's Sons)",
         archive="fieldbookofnorth00anth", published="1928",
         description="A field book describing every mammal then known north of Mexico: size, colour, signs, habits "
                     "and range." + OLD_NOTE.format(year=1928)),
    dict(OLD_PD, name="ditmars_reptile_book_1907", title="The Reptile Book (Raymond L. Ditmars, 1907)",
         subject="Reptiles", publisher="Raymond L. Ditmars (Doubleday, Page and Company)",
         archive="reptilebookcom00ditm", published="1907",
         description="The Bronx Zoo curator's book of the turtles, crocodilians, lizards and snakes of the United "
                     "States and northern Mexico, with how to tell the venomous snakes." + OLD_NOTE.format(year=1907)),
    dict(OLD_PD, name="dickerson_frog_book_1906", title="The Frog Book: North American Toads and Frogs (Mary C. "
         "Dickerson, 1906)", subject="Amphibians", publisher="Mary C. Dickerson (Doubleday, Page and Company)",
         archive="frogbooknorthame00dick2", published="1906",
         description="A study of the toads and frogs of North America: how to recognise each, their calls, eggs and "
                     "tadpoles, and their habits." + OLD_NOTE.format(year=1906)),
    dict(OLD_PD, name="holland_butterfly_book_1902", title="The Butterfly Book (W. J. Holland, 1902)",
         subject="Insects (butterflies)", publisher="W. J. Holland (Doubleday, Page and Company)",
         archive="butterflybookpop00holluoft", published="1902",
         description="A popular guide to the butterflies of North America: how to recognise each, its caterpillar "
                     "and food plants, and how butterflies live." + OLD_NOTE.format(year=1902)),
    dict(OLD_PD, name="jordan_evermann_food_game_fishes_1902", title="American Food and Game Fishes (David Starr "
         "Jordan and Barton Warren Evermann, 1902)", subject="Fish",
         publisher="David Starr Jordan and Barton Warren Evermann (Doubleday, Page and Company)",
         archive="americanfoodgame1902jord", published="1902",
         description="A popular account of the food and game fishes of North American waters, fresh and salt: how "
                     "to recognise each, where it lives and its habits." + OLD_NOTE.format(year=1902)),
    dict(OLD_PD, name="hornaday_american_natural_history_1904", title="The American Natural History (William T. "
         "Hornaday, 1904)", subject="Animals", publisher="William T. Hornaday (Charles Scribner's Sons)",
         archive="americannaturalh00horn", published="1904",
         description="The New York Zoological Park director's natural history of the animals of North America and "
                     "the world: mammals, birds, reptiles, amphibians and fishes." + OLD_NOTE.format(year=1904)),
]

# Looked at for North American animals on 2026-11-21 and not built, with the reason.
ANIMALS_NOT_INCLUDED = [
    ("US Fish and Wildlife Service species profiles (fws.gov/species)", "Public domain (US government), and robots.txt "
     "allows them, but the site has no sitemap of its species pages (its sitemaps list programs, refuges, stories and "
     "documents) and no copyright line on its policies page to check at build time; its tens of thousands of species "
     "pages would have to be found through its search service. Not built yet."),
    ("National Park Service species pages", "Public domain, but spread over each park's own pages (nps.gov/<park>/"
     "learn/nature/...), not one guide; the picture describer has NPS photos (npgallery)."),
    ("CDC pages on ticks, zoonoses and Healthy Pets; USDA APHIS animal health pages", "Public domain, but cdc.gov and "
     "aphis.usda.gov refuse automated requests (403), robots.txt included. They are linked in the manual collection "
     "pet_livestock_supplies for the person to open."),
    ("EPA pet and flea and tick pages, and the Pesticide Product Label System (flea and tick labels)", "EPA's "
     "disclaimer says its documents \"may be freely distributed and used for non-commercial, scientific and "
     "educational purposes\" and that commercial use \"may be protected\", not a plain public-domain statement; the "
     "labels in the Label System are written by each product's maker. Linked in pet_livestock_supplies, not built."),
    ("Biodiversity Heritage Library", "Its robots.txt says \"Content-Signal: search=yes,ai-train=no\"; its old "
     "public-domain North American natural histories are taken from the Internet Archive's own copies instead."),
    ("Cornell Lab of Ornithology, All About Birds", "Copyright of the Cornell Lab; no open licence."),
    ("Animal Diversity Web (University of Michigan)", "No open licence was confirmed for its species accounts in this "
     "pass, and its robots.txt asks programs to wait 8 to 16 seconds between pages; not built."),
    ("Smithsonian National Zoo animal fact sheets", "Only the Smithsonian's Open Access items are CC0; the zoo's web "
     "pages were not found among them, so they are not built."),
    ("Wikipedia and Wikispecies", "Already in the Kiwix library (CC BY-SA)."),
    ("Hinterland Who's Who, Canadian Wildlife Service, Parks Canada and the Species at Risk Public Registry",
     "The terms of the canada.ca web pages allow non-commercial reproduction only, not an open licence (unlike the "
     "open.canada.ca publications under the Open Government Licence - Canada); Hinterland Who's Who is copyright "
     "of Environment and Climate Change Canada and the Canadian Wildlife Federation."),
    ("State and provincial wildlife agency species guides", "Not checked one by one in this pass; state agency sites "
     "usually carry \"Copyright © State of ...\" footers without an open licence, and Ontario's and British "
     "Columbia's pages are under their King's Printer terms rather than the Open Government Licence. Alberta's OGL "
     "publications (open.alberta.ca) can be added to PDF_DOCS one checked record at a time."),
    ("Extension service guides on pests and livestock", "University extension publications are each university's "
     "copyright (some CC BY-NC-ND, which a rebuilt book may not use); none with an open licence and a full-text "
     "source was found in this pass."),
    ("AKC and CKC breed standards, AVMA and ASPCA pages, AAFCO pet food label guides", "Copyright of each "
     "organisation; no open licence."),
    ("Animal drug labels (DailyMed animal labels, the FDA Green Book, Health Canada veterinary drugs)", "Left to the "
     "reference library's drug-label work."),
]
NOT_INCLUDED = NOT_INCLUDED + ANIMALS_NOT_INCLUDED


# ====================================================================== where a non-US source's practice may differ
#
# The owner's rule (November 2026): every book from outside the United States carries a short notice saying where
# its practice may differ from US practice, as specific to its subject as the subject's words allow. The builder
# shows it on the book's welcome page and puts it in textbooks.json ("practice_note"); practice_note() gives it.

# How each country is named at the start of the notice ("" for the United States: no notice).
PRACTICE_COUNTRY = {
    "United Kingdom": "UK", "Canada": "Canadian", "Australia": "Australian", "New Zealand": "New Zealand",
    "Ireland": "Irish", "South Africa": "South African", "India": "Indian", "International": "International",
}

# (words in a book's subject or title, what may differ), first match wins; the last line is for any other subject.
PRACTICE_SUBJECTS = [
    (r"electric|wiring|electronics", "wiring rules and electrical codes (not the US National Electrical Code), "
     "mains voltage and frequency, plug types, wire colours and metric units"),
    (r"plumb|gas fitt|hvac|heating|refrigerat", "plumbing and gas codes, pipe sizes and metric units, refrigerant "
     "rules and approved fittings"),
    (r"carpent|construct|building|millwright|joiner", "building codes, lumber sizes and metric units, and "
     "workplace safety rules (not OSHA)"),
    (r"weld|machin|metal|fabricat", "welding and safety standards (not AWS or OSHA), material grades and metric "
     "units"),
    (r"automotive|vehicle|motor|mechanic|driving", "the side of the road and the driver's seat, vehicle standards "
     "and inspections, and metric units"),
    (r"medic|nurs|pharm|health|first aid|drug|anatomy", "medicine names (international or local brand names, not "
     "US ones), doses and units (mmol/L, kilograms), emergency numbers, and the laws on practice and prescribing"),
    (r"law|legal|rights|regulat|employment|workplace", "the laws themselves, courts, rights and workplace rules, "
     "which apply only there"),
    (r"cook|food|culinary|nutrition", "food safety rules, metric measures and oven temperatures in Celsius, and "
     "food names"),
    (r"account|business|financ|tax|econom", "tax rules, accounting standards (IFRS, not US GAAP), currency and "
     "business law"),
    (r"agricult|farm|horticult", "pesticide approvals, farming rules, climate and seasons, and metric units"),
    (r"history|social stud|civics|geograph|government|citizenship", "history, civics and geography taught from "
     "that country's point of view, with its own spelling and curriculum"),
    (r"math|algebra|geometr|calculus|statistic", "spelling, notation (decimal comma, the way division and dates are "
     "written), the order of the curriculum, grade names and exams"),
    (r"science|physics|chemistr|biolog", "metric units, spelling, the order of the curriculum, grade names and "
     "exams, and local plants, animals and safety rules"),
    (r"english|reading|literacy|language arts|writing", "spelling (colour, centre), vocabulary, grammar terms and "
     "the books studied"),
    (r"", "units (metric), spelling, laws, standards and everyday practice"),
]


def practice_note(country, subject, title=""):
    """The notice for a book from a country outside the US, or "" for a US book or an unknown country:
    "Canadian source: wiring rules and electrical codes (...) may differ from US practice." """
    import re
    who = PRACTICE_COUNTRY.get(country, "")
    if not who:
        return ""
    words = f"{subject} {title}".lower()
    what = next(text for pattern, text in PRACTICE_SUBJECTS if re.search(pattern, words))
    return f"{who} source: {what} may differ from US practice."


# ====================================================================== more reference books (added 2026-11-21)
# FAA handbooks, more Navy rate training manuals and Army field manuals, NIST handbooks, more CFR parts and the UK
# National Archives' teaching resources: their entries, checks and reasons are in reference_more.py.
import reference_more as _more  # noqa: E402

PDF_DOCS += _more.PDF_DOCS
LAWS += [dict(_cfr(*row[:7]), **({"cfr": [dict(title=row[3], volume=row[4], part=row[5])] +
                                         [dict(title=t, volume=v, part=p) for t, v, p in row[7]]}
                                        if len(row) > 7 else {})) for row in _more.CFR_LAWS]
LAWS_MORE += [dict(_cfr(*row[:7]), **({"cfr": [dict(title=row[3], volume=row[4], part=row[5])] +
                                              [dict(title=t, volume=v, part=p) for t, v, p in row[7]]}
                                             if len(row) > 7 else {})) for row in _more.CFR_LAWS_MORE]
GOV_GUIDES += _more.GOV_GUIDES
LICENCE_LINES.update(_more.LICENCE_LINES)
NOT_INCLUDED = NOT_INCLUDED + _more.NOT_INCLUDED
PRACTICE_SUBJECTS[:0] = _more.PRACTICE_SUBJECTS


# ====================================================================== open courses: candidates (step 5, 2026-11-21)
#
# SETTLED later on 2026-11-21: what was built from these lists is in courses.py (LibreTexts, BCcampus through Kolibri,
# Khan Academy, CK-12 and EngageNY through Kolibri, MIT OpenCourseWare, Core Knowledge), in K12_GUIDES (Illustrative
# Mathematics, Open Up HS Math) and PDF_DOCS (Utah's science books), with Siyavula's and OpenStax's new books above;
# what was not built, and why, is in courses.NOT_INCLUDED. The lists below are kept as the record of the first look.
#
# Open courses and course textbooks of every subject, looked at for the "course" group. Each is (name, address,
# licence as found, country, what was checked, what to do next). Only robots.txt was read for these on 2026-11-21;
# no licence is taken as checked until a book's own page is read by the builder. Sources already recorded above
# (BCcampus, eCampusOntario, CAUL, OpenLearn, Saylor, Open Yale, MIT OpenCourseWare, OpenStax, Siyavula, Te Pukenga,
# Scoilnet) are not repeated. MIT OpenCourseWare and OpenLearn are CC BY-NC-SA: the library's "non-commercial" kind
# (ALLOWED), shown with "not for commercial use", for personal and school use.
OPEN_COURSE_CANDIDATES = [
    ("Open Textbook Library (University of Minnesota)", "https://open.umn.edu/opentextbooks", "per book (catalogue: "
     "RSL licence.xml permits all uses with CC BY attribution)", "United States", "robots.txt allows all, "
     "Crawl-delay 120", "Use as the catalogue: read each book's licence and its source (often a Pressbooks site, "
     "some of them blocked as BCcampus is); build the CC BY, CC0 and BY-SA ones."),
    ("LibreTexts (all its libraries: med, eng, chem, bio, workforce ...)", "https://commons.libretexts.org",
     "per book (mixed: CC BY, BY-SA, BY-NC-SA, some all rights reserved)", "United States", "robots.txt: "
     "Crawl-delay 5, Special: pages disallowed, files allowed", "Read each book's licence from its own page; the "
     "Workforce library has trades courses (welding, HVAC, electrical, automotive)."),
    ("MIT OpenCourseWare", "https://ocw.mit.edu", "CC BY-NC-SA 4.0 (each course page)", "United States",
     "robots.txt allows all", "Non-commercial kind; start with courses whose notes are text, not scans."),
    ("SkillsCommons (US Department of Labor TAACCCT)", "https://www.skillscommons.org", "CC BY 4.0 (grant "
     "condition)", "United States", "not reachable from the build machine on 2026-11-21 (no answer)", "Try again; "
     "look for its OAI-PMH feed (DSpace). Strong picture-pack candidate: labelled trade photos and diagrams."),
    ("Washington SBCTC Open Course Library", "https://www.opencourselibrary.org", "CC BY (as stated by SBCTC)",
     "United States", "address redirects; robots.txt not read yet", "Follow the redirect and read its terms."),
    ("OER Commons (ISKME), CTE and all subjects", "https://www.oercommons.org", "per item (filter CC BY, CC0)",
     "United States", "robots.txt refuses automated requests (403)", "Not fetched; each item links to its own "
     "host, which can be added directly."),
    ("Open Polytechnic of New Zealand", "https://www.openpolytechnic.ac.nz", "not yet found", "New Zealand",
     "robots.txt read (200)", "Look for openly licensed course material; most is enrolment-only."),
    ("Ako Aotearoa (New Zealand)", "https://ako.ac.nz", "not yet found (resources for teachers)", "New Zealand",
     "robots.txt read (200)", "Check each resource's licence."),
    ("OpenLearn Create (The Open University, UK)", "https://www.open.edu/openlearncreate", "per course (many "
     "CC BY-NC-SA)", "United Kingdom", "create.open.edu did not answer; www.open.edu refuses (403, see above)",
     "Not fetched unless the Open University allows it."),
    ("TAFE and Australian open courses", "", "TAFE course material is mostly copyright; CAUL's collection is "
     "blocked (see above)", "Australia", "not checked", "Look for Australian Pressbooks hosts that allow "
     "automated download, and state government (CC BY 4.0) training resources."),
    ("Irish and Scottish open resources (e.g. Ireland's National Forum, Scotland's college OER)", "", "not yet "
     "found", "Ireland", "not checked", "Search their repositories for CC BY course books."),
    ("State CTE curriculum centres (Oklahoma CareerTech, Texas CTE resource centre)", "", "mostly copyright",
     "United States", "not checked", "Check each; keep only those with an open licence."),
]

# K-12 (kindergarten to grade 12) open textbooks and courses looked at on 2026-11-21: (name, address, licence as
# found, country, grades, what was checked, what to do next). Grades are US grades ("K-5", "6-8", "9-12") or the
# country's own years. Already recorded above and not repeated: CK-12 (its own licence, not a standard open one;
# not CC BY-NC as sometimes said), Siyavula (built: grades 7 to 12), Oak National Academy (API key needed), Khan
# Academy (see PERSONAL_USE_CANDIDATES: offline routes only, never the website). OpenStax's high school titles come with the
# OpenStax repositories (OSBOOKS) when a "high-school" repository is listed there.
K12_CANDIDATES = [
    ("OpenStax high school titles (Physics, Biology, Statistics for high school)", "https://openstax.org",
     "CC BY 4.0", "United States", "9-12", "robots.txt read (GPTBot shut out of /books/; other readers allowed)",
     "Find the osbooks-* repository of each high school title with git ls-remote and add it to OSBOOKS."),
    ("Illustrative Mathematics and Open Up Resources", "https://illustrativemathematics.org", "CC BY 4.0 "
     "(their own statement)", "United States", "K-12", "not checked", "Check robots.txt and the licence page; the "
     "student books are web pages."),
    ("EngageNY / NYSED curriculum (New York)", "https://www.nysed.gov/curriculum-instruction", "CC BY-NC-SA 3.0",
     "United States", "PreK-12", "not checked", "Non-commercial kind; mostly PDF modules."),
    ("Utah Open Textbook Project (Utah State Board of Education)", "https://www.schools.utah.gov", "CC BY",
     "United States", "K-12 (mostly 6-12 maths, science and language arts)", "not checked", "Find the current "
     "address; the books are PDFs."),
    ("Washington OSPI OER", "https://ospi.k12.wa.us", "CC BY 4.0 (OSPI's own material)", "United States", "K-12",
     "not checked", "Check each item: OSPI links to others' material too."),
    ("Oregon and other state K-12 OER hubs (OER Commons state hubs)", "https://www.oercommons.org/hubs",
     "per item (CC BY or CC0 only)", "United States", "K-12", "OER Commons refuses automated requests (403)",
     "Use each item's own host where it allows automated download."),
    ("Core Knowledge (Core Knowledge Language Arts, history and geography)", "https://www.coreknowledge.org",
     "CC BY-NC-SA 4.0", "United States", "PreK-8", "not checked", "Non-commercial kind; PDFs."),
    ("BC open K-12 resources (British Columbia, Canada)", "https://www2.gov.bc.ca", "OGL-BC or CC BY where stated",
     "Canada", "K-12", "not checked", "Look for openly licensed BC curriculum resources; OGL-BC is allowed."),
    ("Australian state school resources (e.g. NSW, Victoria, Queensland)", "", "often CC BY 4.0 for state "
     "government material", "Australia", "Foundation-Year 12", "not checked", "Check each state's licence page."),
    ("OER Commons K-12 (CC BY or CC0 only)", "https://www.oercommons.org", "per item", "United States", "K-12",
     "robots.txt refuses automated requests (403)", "Not fetched; use each item's own host."),
]

# Personal-use and open sources reached only through OFFLINE packages made for that purpose (the owner's request,
# 2026-11-21): (name, licence as stated, route, label, what to do next). khanacademy.org itself is NEVER fetched (its
# website terms limit automated access); its content comes only from Kiwix ZIM files (the toolkit's library already
# reads the Kiwix catalogue, and the Kiwix library lists Khan Academy and PhET, see NONPROFIT_NOT_INCLUDED's note) or
# from Learning Equality's Kolibri Studio public channels, which are packaged for offline use with the publishers'
# permission. Every non-commercial or no-derivatives one is labelled "personal use only".
PERSONAL_USE = "personal use only"
PERSONAL_USE_CANDIDATES = [
    ("Khan Academy (English)", "CC BY-NC-SA (most content)", "Kiwix ZIM (library.kiwix.org) or Kolibri Studio "
     "public channel \"Khan Academy (English)\"", PERSONAL_USE, "Check the Kiwix catalogue entry first (the toolkit "
     "reads it already); the Kolibri channel needs a Kolibri export reader."),
    ("PhET Interactive Simulations", "CC BY 4.0", "Kiwix ZIM or Kolibri public channel", "open",
     "Already in the Kiwix library; nothing to build here."),
    ("CK-12", "CK-12's own licence (described elsewhere as CC BY-NC)", "Kolibri public channel \"CK-12\"",
     PERSONAL_USE, "Check the channel's licence field; NOT_INCLUDED notes CK-12's own terms."),
    ("TED-Ed", "CC BY-NC-ND 4.0", "Kiwix ZIM (TED and TED-Ed) or Kolibri channel", PERSONAL_USE,
     "No-derivatives: only whole and unchanged (WHOLE_AND_UNCHANGED)."),
    ("Crash Course", "CC BY-NC-ND on some videos only; check each", "Kiwix ZIM if listed", PERSONAL_USE,
     "Check the licence per video; leave out any all-rights-reserved."),
    ("African Storybook", "CC BY (most stories)", "Kolibri public channel", "open", "Check each story's licence."),
    ("OpenStax (Kolibri channel)", "CC BY 4.0", "Kolibri public channel", "open",
     "Already built from GitHub (OSBOOKS): not repeated."),
    ("Ciencia NASA", "public domain (NASA) and CC BY", "Kolibri public channel", "open",
     "Spanish; check the language rule before adding."),
    ("MIT OpenCourseWare", "CC BY-NC-SA 4.0", "Kiwix ZIM if listed, else ocw.mit.edu (robots.txt allows)",
     PERSONAL_USE, "See OPEN_COURSE_CANDIDATES."),
    ("OpenLearn (The Open University)", "CC BY-NC-SA 4.0 (most courses)", "Kiwix ZIM if listed (www.open.edu "
     "refuses automated requests)", PERSONAL_USE, "Only through an offline package."),
]


# ====================================================================== K-12 school books (2026-11-21)
#
# School books from web sites, made into one ZIM book each by build_textbooks.webguide_book (keys k12:<name>), with
# the fields of NONPROFIT plus level, grades, personal_use, latex/mathml, title_from, extra_pages, extra_titles,
# path_from_url and fix (see webguide_book). Checked by hand on 2026-11-21 (robots.txt and the licence lines quoted
# in LICENCE_LINES); the builder checks the licence again at every build (licence_page/licence_text, and page_mark on
# every page).
LICENCE_LINES.update({
    "illustrative_mathematics": "Every page of im.kendallhunt.com ends: \"IM 6–8 Math was originally developed by "
                                "Open Up Resources and authored by Illustrative Mathematics®, and is copyright "
                                "2017-2019 by Open Up Resources. It is licensed under the Creative Commons Attribution "
                                "4.0 International License (CC BY 4.0).\" (the same for IM 9–12 and K–5 Math); "
                                "robots.txt has no rules.",
    "open_up_hs_math": "www.openupresources.org/help-support/licensing-questions/: \"Open Up HS Math ... © Open Up "
                       "Resources and Mathematics Vision Project. Unless otherwise noted, content produced by Open Up "
                       "Resources and its partners in this book are published under a Creative Commons Attribution-"
                       "NonCommercial 4.0 International License (CC BY-NC 4.0). ... Pre-Unit, Mid-Unit, and End-of-"
                       "Unit Assessments do not fall under the Creative Commons License\" (so assessments are left out; "
                       "personal use only).",
    "utah_science": "Each Utah State Board of Education science book's credits page: \"Unless otherwise noted, the "
                    "contents of this book are licensed under the Creative Commons Attribution NonCommercial "
                    "ShareAlike license ... http://creativecommons.org/licenses/by-nc-sa/3.0/legalcode\" (adapted "
                    "from CK-12, CC BY-NC 3.0); schools.utah.gov/robots.txt allows /curr/.",
})

IM_SITE = "https://im.kendallhunt.com"
IM = dict(group="k12", level="school", subject="Mathematics", country="United States", licence="CC BY 4.0",
          licence_url="https://creativecommons.org/licenses/by/4.0/",
          publisher="Illustrative Mathematics (with Open Up Resources), published by Kendall Hunt",
          licence_text=r"[Ll]icensed under the Creative Commons Attribution 4\.0 (International )?[Ll]icense",
          page_mark=r"Creative\s+Commons\s+Attribution\s+4\.0", sitemap="", unit_rules=[],
          content=(r"<main\b[^>]*>", r"</main>"), drop=[], fix=[(r"&lt;/?p&gt;", " ")], latex=True,
          title_from=r'<h1[^>]*>(.*?)</h1>\s*<p class="im-c-heading[^"]*">(.*?)</p>', path_from_url=True,
          extra_pages=[(r"/index\.html$", "/practice.html")], extra_titles=[(r"/practice\.html$", "practice problems")],
          limit=900)


def _im(name, title, grades, part, number, description):
    """One Illustrative Mathematics student book (part "MS" or "HS", book number) as a K12_GUIDES entry."""
    base = f"{IM_SITE}/{part}/students/{number}"
    return dict(IM, name=name, title=title, grades=grades, source=f"{base}/index.html", licence_page=f"{base}/index.html",
                start=[f"{base}/index.html"], units=r"^%s/\d+/index\.html$" % __import__("re").escape(base),
                pages=r"^%s/(\d+/\d+/index|glossary)\.html$" % __import__("re").escape(base), description=description)


def _im_k5(grade, words):
    """The family materials of one IM K-5 Math grade (its student workbooks are printed only)."""
    base = f"{IM_SITE}/k5/families/{grade}"
    return dict(IM, name=f"im_k5_{grade.replace('-', '_')}_families", title=f"Illustrative Mathematics K-5: {words}, "
                "Family Materials", grades=words.replace("Grade ", "").replace("Kindergarten", "K"), source=f"{IM_SITE}/K5/families/{grade}/units.html",
                licence_page=f"{IM_SITE}/K5/families/{grade}/units.html", start=[f"{IM_SITE}/K5/families/{grade}/units.html"],
                units="", pages=r"^%s/(information-for-families|unit-\d+/family-materials)\.html$" %
                __import__("re").escape(base), extra_pages=[], extra_titles=[], title_from="",
                titles=[(r"/information-for-families\.html$", "Information for families")],
                description=f"IM K-5 Math, {words}: the letter to families for each unit, which says what the "
                            "children learn, with sample problems and their solutions.")


OUR_SITE = "https://access.openupresources.org/curricula/our-hs-math/en"
OUR = dict(group="k12", level="school", subject="Mathematics", country="United States", licence="CC BY-NC 4.0",
           licence_url="https://creativecommons.org/licenses/by-nc/4.0/", personal_use=True,
           publisher="Open Up Resources and Mathematics Vision Project",
           licence_page="https://www.openupresources.org/help-support/licensing-questions/",
           licence_text=r"Open Up HS Math.{0,300}Creative Commons Attribution-NonCommercial 4\.0 International License",
           page_mark="", sitemap="", unit_rules=[], content=(r"<main\b[^>]*>", r"</main>"), drop=[], mathml=True,
           title_from=r'<h1[^>]*>\s*<span class="hed-alpha__superhed">(.*?)</span>\s*<span class="hed-alpha__hed"[^>]*>(.*?)</span>',
           path_from_url=True, extra_titles=[(r"/ready_set_go\.html$", "Ready, Set, Go practice")], grades="9-12",
           limit=900, notice="Open Up HS Math © Open Up Resources and Mathematics Vision Project, CC BY-NC 4.0. Its "
                             "pre-unit, mid-unit and end-of-unit assessments are not under the licence and are not "
                             "included.")


def _our(name, path, words):
    """One Open Up HS Math course (path under OUR_SITE) as a K12_GUIDES entry."""
    base = f"{OUR_SITE}/{path}"
    e = __import__("re").escape(base)
    return dict(OUR, name=name, title=f"Open Up HS Math: {words}", source=f"{base}/index.html",
                start=[f"{base}/index.html"], units=r"^%s/unit-\d+/index\.html$" % e,
                pages=r"^%s/unit-\d+/lesson-\d+/(index|ready_set_go)\.html$" % e,
                description=f"Open Up High School Mathematics, {words}: every lesson of the student edition (its "
                            "tasks, learning focus and summaries) with its Ready, Set, Go practice; personal use only.")


K12_GUIDES = [
    _im("im_grade_6_math", "Illustrative Mathematics Grade 6 (student book)", "6", "MS", 1,
        "IM 6-8 Math, grade 6: every lesson of the student book with its practice problems, lesson summaries and "
        "glossary; formulas written as text and pictures described."),
    _im("im_grade_7_math", "Illustrative Mathematics Grade 7 (student book)", "7", "MS", 2,
        "IM 6-8 Math, grade 7: every lesson of the student book with its practice problems, lesson summaries and "
        "glossary."),
    _im("im_grade_8_math", "Illustrative Mathematics Grade 8 (student book)", "8", "MS", 3,
        "IM 6-8 Math, grade 8: every lesson of the student book with its practice problems, lesson summaries and "
        "glossary."),
    _im("im_algebra_1", "Illustrative Mathematics Algebra 1 (student book)", "9-12", "HS", 1,
        "IM 9-12 Math, Algebra 1: every lesson of the student book with its practice problems and glossary."),
    _im("im_geometry", "Illustrative Mathematics Geometry (student book)", "9-12", "HS", 2,
        "IM 9-12 Math, Geometry: every lesson of the student book with its practice problems and glossary."),
    _im("im_algebra_2", "Illustrative Mathematics Algebra 2 (student book)", "9-12", "HS", 3,
        "IM 9-12 Math, Algebra 2: every lesson of the student book with its practice problems and glossary."),
    _im("im_algebra_1_supports", "Illustrative Mathematics Algebra 1 Extra Supports (student book)", "9-12", "HS", 4,
        "IM 9-12 Math, the extra support lessons for Algebra 1 (Alg1+)."),
] + [_im_k5(g, w) for g, w in [("kindergarten", "Kindergarten"), ("grade-1", "Grade 1"), ("grade-2", "Grade 2"),
                               ("grade-3", "Grade 3"), ("grade-4", "Grade 4"), ("grade-5", "Grade 5")]] + [
    _our("our_hs_algebra_1", "aga/algebra-1", "Algebra 1"),
    _our("our_hs_geometry", "aga/geometry", "Geometry"),
    _our("our_hs_algebra_2", "aga/algebra-2", "Algebra 2"),
    _our("our_hs_math_1", "integrated/math-1", "Integrated Math 1"),
    _our("our_hs_math_2", "integrated/math-2", "Integrated Math 2"),
    _our("our_hs_math_3", "integrated/math-3", "Integrated Math 3"),
]

# Utah State Board of Education open science textbooks (the Utah Open Textbook Project), one PDF each: CC BY-NC-SA 3.0
# (checked in each PDF's credits page at every build), so personal use only.
UTAH_PAGE = "https://www.schools.utah.gov/curr/science"
UTAH = dict(group="k12", level="school", country="United States", licence="CC BY-NC-SA 3.0",
            licence_url="https://creativecommons.org/licenses/by-nc-sa/3.0/", personal_use=True,
            publisher="Utah State Board of Education (adapted from CK-12 Foundation)", page=UTAH_PAGE,
            licence_page=UTAH_PAGE, licence_text=r"OER|textbook",
            pdf_licence_text=r"(?i)licenses/by-nc-sa/3\.0|Attribution\s*Non\s*-?Commercial\s*Share\s*-?Alike")
PDF_DOCS += [
    dict(UTAH, name=f"utah_science_{key.lower()}", title=f"Utah {words} Science (SEEd)", subject=f"Science, {words}",
         grades=grades, pdf=f"https://www.schools.utah.gov/curr/science/_science_/{key}OERSciTextbook.pdf",
         description=f"The Utah State Board of Education's open science textbook for {words.lower()}, written for "
                     "Utah's SEEd standards (Science with Engineering Education); personal use only.")
    for key, words, grades in [
        ("Kindergarten", "Kindergarten", "K"), ("1stGrade", "Grade 1", "1"), ("2ndGrade", "Grade 2", "2"),
        ("3rdGrade", "Grade 3", "3"), ("4thGrade", "Grade 4", "4"), ("5thGrade", "Grade 5", "5"),
        ("6thGrade", "Grade 6", "6"), ("7thGrade", "Grade 7", "7"), ("8thGrade", "Grade 8", "8"),
        ("Biology", "High School Biology", "9-12"), ("Chemistry", "High School Chemistry", "9-12"),
        ("EarthSpace", "High School Earth and Space", "9-12"), ("Physics", "High School Physics", "9-12")]
]


# ====================================================================== drinks: wine, beer, spirits, soft drinks and making them
#
# The owner's request of 2026-11-21: reference material on wine, beer, spirits and every other drink, how to taste and
# describe them, how they are labelled, and how they are made (brewing, winemaking and distilling, at home too), IN
# FULL wherever the licence allows (whole documents and books, not summaries). Checked by hand on 2026-11-21. The
# hand-written guide "How to describe a drink" and the TTB's wine manual (one PDF per chapter) are built by
# drinks_reference.py (keys drinks:guide and drinks:ttb_wine_bam); everything below is built by the usual readers.
# Key "drinks" builds all of it (expand_keys). Answers about home distilling always give the legal and safety notes
# first (drinks_reference.DISTILLING_WARNING): in the US it is illegal without federal permits (26 U.S.C. 5601).
GROUPS["drinks"] = "Reference, drinks: wine, beer, spirits, soft drinks, and brewing, winemaking and distilling"
TTB_POLICY = "https://www.ttb.gov/about-ttb/privacy-policy/"
TTB_TEXT = r"You may copy text and images from our website freely"
LICENCE_LINES["ttb"] = ("www.ttb.gov/about-ttb/privacy-policy/ (section 11, Copyright): \"Federal employees cannot claim "
                        "copyright for any work on the TTB.gov website that was created or maintained during the course "
                        "of their duties. You may copy text and images from our website freely, with the exception of "
                        "official seals, names, and symbols (see below), but credit must be given to TTB.\"")
LICENCE_LINES["wikibooks"] = ("en.wikibooks.org/wiki/Wikibooks:Copyrights: Wikibooks text is under the Creative Commons "
                              "Attribution-ShareAlike licence (CC BY-SA 4.0): use with credit, and changed copies keep "
                              "the same licence. The library shows such books as share-alike.")
DRINKS_LAW = dict(group="drinks")
LAWS += [
    _cfr("cfr_27_4_wine_labeling", "Labeling and Advertising of Wine (27 CFR part 4)", "Wine (standards of identity "
         "and labels)", 27, 1, 4, "The TTB's rules for wine labels and advertising, with the standards of identity: "
         "what may be called grape wine, sparkling wine, dessert wine, fruit wine and the other classes and types, "
         "varietal (grape variety) names, appellations of origin and viticultural areas, vintage dates and alcohol "
         "content statements.", group="drinks"),
    _cfr("cfr_27_5_distilled_spirits_labeling", "Labeling and Advertising of Distilled Spirits (27 CFR part 5)",
         "Spirits (standards of identity and labels)", 27, 1, 5, "The TTB's rules for distilled spirits labels and "
         "advertising, with the standards of identity (section 5.143 and the table of classes and types): what may be "
         "called vodka, whisky, bourbon whisky (made from a fermented mash of at least 51 percent corn), rye whisky, "
         "malt whisky, gin, brandy, rum, agave spirits and tequila, liqueurs and the others; age statements, proof and "
         "alcohol content.", group="drinks"),
    _cfr("cfr_27_7_malt_beverage_labeling", "Labeling and Advertising of Malt Beverages (27 CFR part 7)", "Beer (labels)",
         27, 1, 7, "The TTB's rules for beer and other malt beverage labels and advertising: class and type "
         "designations (beer, ale, porter, stout, lager, malt liquor and others), alcohol content statements, net "
         "contents and name and address.", group="drinks"),
    _cfr("cfr_27_16_health_warning", "Alcoholic Beverage Health Warning Statement (27 CFR part 16)", "Alcohol labels "
         "(health warning)", 27, 1, 16, "The government warning every US alcoholic drink label carries (pregnancy, "
         "driving and operating machinery, health problems), its exact wording and how it must be printed.",
         group="drinks"),
    _cfr("cfr_21_146_canned_fruit_juices", "Canned Fruit Juices (21 CFR part 146)", "Juices (standards of identity)",
         21, 2, 146, "The FDA's standards of identity for fruit juices and beverages: orange juice in its forms "
         "(fresh, pasteurized, from concentrate, frozen concentrate), grapefruit, lemon, pineapple and prune juice, "
         "canned fruit nectars and lemonade concentrates.", group="drinks"),
    _cfr("cfr_21_120_juice_haccp", "Hazard Analysis and Critical Control Point Systems for Juice (21 CFR part 120)",
         "Juices (safety)", 21, 2, 120, "The FDA's safety rules for juice makers: the hazard analysis, the 5-log "
         "pathogen reduction, and the warning label untreated juice must carry.", group="drinks"),
    _usc("us_code_26_ch51_distilled_spirits_wines_beer", "Distilled Spirits, Wines, and Beer (26 U.S.C. chapter 51)",
         "Alcohol law (taxes, home production and penalties)", 26, ["subtitleE-chap51"], "The federal law on alcoholic drinks "
         "as codified in the Internal Revenue Code: taxes on spirits, wine and beer; the exemptions that let adults "
         "make wine (section 5042) and beer (section 5053) at home for personal or family use within limits; and the "
         "penalties, including section 5601 (distilling without registration, which is why distilling spirits at home "
         "is illegal in the US without federal permits)."),
]
LAWS[-1]["group"] = "drinks"
LAWS_MORE += [
    _cfr("cfr_27_19_distilled_spirits_plants", "Distilled Spirits Plants (27 CFR part 19)", "Spirits (production)", 27,
         1, 19, "The TTB's rules for licensed distilleries: registration, premises and equipment, production, storage "
         "and bottling of spirits, gauging and records. In the US, distilling spirits needs this federal "
         "registration even for personal use.", group="drinks"),
    _cfr("cfr_27_24_wine", "Wine (27 CFR part 24)", "Wine (production, including at home)", 27, 1, 24, "The TTB's rules "
         "for bonded wineries and wine production, including section 24.75 (wine for personal or family use: an adult "
         "may make up to 100 gallons a year, or 200 gallons for a household of two or more adults, without paying "
         "tax), cellar treatments and the materials allowed.", group="drinks"),
    _cfr("cfr_27_25_beer", "Beer (27 CFR part 25)", "Beer (production, including at home)", 27, 1, 25, "The TTB's rules "
         "for breweries, including sections 25.205 and 25.206 (beer for personal or family use: an adult may brew up to "
         "100 gallons a year, or 200 gallons for a household of two or more adults, not for sale).", group="drinks"),
]

# 21 CFR part 101 (food labeling, with section 101.30 on the juice percentage) is already a book of LAWS
# (cfr_21_101_food_labeling, group "law"); expand_keys("drinks") adds it.

# Government web guides about drinks (webguide_book).
GOV_GUIDES += [
    dict(name="ttb_beverage_alcohol_guidance", title="TTB guidance on wine, beer and spirits: labels, classes and "
         "types, and FAQs", subject="Wine, beer and spirits (labels and rules)", group="drinks",
         publisher="Alcohol and Tobacco Tax and Trade Bureau (TTB), US Department of the Treasury",
         country="United States", licence=US_GOV, licence_url=US_GOV_URL,
         source="https://www.ttb.gov/regulated-commodities/beverage-alcohol",
         description="The TTB's plain guidance pages: what every wine, beer and spirits label must say (brand, class "
                     "and type, alcohol content, net contents, sulfites, the health warning), anatomy-of-a-label "
                     "tools, grape variety names and American viticultural areas, malt beverage classes, and its "
                     "questions and answers on wine, beer (including home brewing), spirits, cider and caffeinated "
                     "alcohol drinks.",
         notice="Courtesy: Alcohol and Tobacco Tax and Trade Bureau (TTB).",
         licence_page=TTB_POLICY, licence_text=TTB_TEXT, page_mark="", start=[], units="",
         pages=r"^https://www\.ttb\.gov/(regulated-commodities/beverage-alcohol/(wine|beer|distilled-spirits)/(?!.*"
               r"(online-reading-room|statistics|proprietorship|contact-information|covid|forms|proposed|rulings|"
               r"import|certification|el-manual|le-manuel|wholesaler|exporting|qualification|pending))[a-z0-9/-]*|"
               r"regulated-commodities/labeling/malt-beverages/|faqs/(alcohol|general-alcohol|cider|flavored-malt-"
               r"beverages|alcohol-beverages-with-added-caffiene|allergen-labeling|alcohol-labeling-and-formulation)/|"
               r"business-central/consumer/[a-z0-9/-]*)$",
         sitemap="https://www.ttb.gov/sitemap.xml",
         unit_rules=[(r"/wine/", "Wine"), (r"/beer/|malt-beverages|flavored-malt", "Beer and malt beverages"),
                     (r"/distilled-spirits/", "Distilled spirits"), (r".", "Questions and answers, and consumers")],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"],
         changes="made into web pages with the site's menus and pictures left out (only TTB's own text is kept)",
         limit=160),
    dict(name="fda_drink_labels_and_caffeine", title="FDA: reading the Nutrition Facts label, added sugars, caffeine "
         "and juice safety", subject="Drinks (labels, sugar and caffeine)", group="drinks",
         publisher="US Food and Drug Administration (FDA)", country="United States", licence=US_GOV,
         licence_url=US_GOV_URL, source="https://www.fda.gov/food/nutrition-facts-label",
         description="The FDA's plain-language guides to reading the Nutrition Facts label (serving size, calories, "
                     "percent Daily Value, added sugars), how much caffeine is too much (energy drinks, coffee and "
                     "tea; up to 400 milligrams a day for most healthy adults), and what to know about juice safety "
                     "(untreated juice and its warning label).",
         licence_page="https://www.fda.gov/about-fda/about-website/website-policies",
         licence_text=r"They are in the public domain and may be republished", page_mark="", start=[], units="",
         urls=["https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label",
               "https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label",
               "https://www.fda.gov/food/nutrition-facts-label/lows-and-highs-percent-daily-value-nutrition-facts-label",
               "https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much",
               "https://www.fda.gov/food/buy-store-serve-safe-food/what-you-need-know-about-juice-safety"],
         pages=r"^https://www\.fda\.gov/(food|consumers)/[a-z0-9/-]+$", sitemap="", unit_rules=[],
         content=(r"<main\b[^>]*>", r"</main>"), drop=[r"<nav\b.*?</nav>"], limit=10),
]

# Wikibooks' drink books (CC BY-SA 4.0: share-alike), whole: every page of each book.
WIKIBOOKS = dict(group="drinks", country="International", licence="CC BY-SA 4.0",
                 licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
                 publisher="Wikibooks contributors (en.wikibooks.org)",
                 notice="From Wikibooks (en.wikibooks.org), written by its contributors, CC BY-SA 4.0; each page's "
                        "history lists its authors.",
                 licence_page="https://en.wikibooks.org/wiki/Wikibooks:Copyrights",
                 licence_text=r"Creative Commons Attribution-ShareAlike", page_mark=r"Creative Commons Attribution-"
                 r"ShareAlike", sitemap="", unit_rules=[],
                 content=(r'<div id="mw-content-text"[^>]*>', r'<div class="printfooter"'),
                 drop=[r'<span class="mw-editsection">.*?</span>\s*</span>', r'<div class="(?:navbox|noprint)[^"]*".*?'
                       r'</div>', r'<table class="[^"]*(?:ambox|metadata|navbox)[^"]*".*?</table>'],
                 changes="every page of the book made into web pages, with the site's menus, edit links and notices "
                         "left out (its pictures' descriptions kept)")


def _wikibook(name, book, title, subject, description):
    """A Wikibooks book as a NONPROFIT entry: its contents page, the pages it links and the pages those link (units),
    all within the book."""
    pages = rf"^https://en\.wikibooks\.org/wiki/{book}/[^?#:]+$"
    return dict(WIKIBOOKS, name=name, title=title, subject=subject, description=description,
                source=f"https://en.wikibooks.org/wiki/{book}", start=[f"https://en.wikibooks.org/wiki/{book}"],
                units=pages, pages=pages, limit=500)


NONPROFIT += [
    _wikibook("wikibooks_brewing", "Brewing", "Brewing (Wikibooks)", "Beer (home brewing)", "Wikibooks' open book on "
              "brewing beer at home: ingredients (malt, hops, yeast, water), equipment, cleaning and sanitising, "
              "milling, mashing, lautering, boiling, cooling, fermentation, bottling and kegging, and recipes with "
              "their grain bills and hop schedules (units as written)."),
    _wikibook("wikibooks_wine", "Wine", "Wine (Wikibooks)", "Wine (tasting, regions, making)", "Wikibooks' open book "
              "on the informed enjoyment of wine: the vine, types of wine, the art and science of winemaking, wine "
              "regions, tasting and evaluating, food pairing, serving and storage, and a glossary."),
    _wikibook("wikibooks_bartending", "Bartending", "Bartending (Wikibooks)", "Cocktails and mixed drinks",
              "Wikibooks' open bartending guide: spirits, liqueurs, beer and wine behind the bar, equipment and "
              "glassware, techniques, and hundreds of cocktail and mixed drink recipes (measures as written)."),
]

# The TTB's Beverage Alcohol Manuals for spirits and beer (one complete PDF each; the wine manual is one PDF per
# chapter: drinks_reference.wine_bam_book).
TTB_PDF = dict(group="drinks", country="United States", licence=US_GOV, licence_url=US_GOV_URL,
               licence_page=TTB_POLICY, licence_text=TTB_TEXT,
               publisher="Alcohol and Tobacco Tax and Trade Bureau (TTB), US Department of the Treasury",
               notice="Courtesy: Alcohol and Tobacco Tax and Trade Bureau (TTB).")
PDF_DOCS += [
    dict(TTB_PDF, name="ttb_bam_distilled_spirits", title="The Beverage Alcohol Manual: Distilled Spirits (TTB)",
         subject="Spirits (labels and classes)",
         pdf="https://www.ttb.gov/system/files/images/pdfs/spirits_bam/complete-distilled-spirit-beverage-alcohol-"
             "manual.pdf", page="https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/"
                                "beverage-alcohol-manual/",
         description="The TTB's practical guide to distilled spirits labels: mandatory information, type size, the "
                     "health warning, class and type designations (the kinds of whisky, rum, gin, brandy and the "
                     "others), name and address, standards of fill, colouring and flavouring, age statements and "
                     "containers. TTB notes that it has not been updated for the newest part 5 rules (also in this "
                     "library)."),
    dict(TTB_PDF, name="ttb_bam_malt_beverages", title="The Beverage Alcohol Manual: Malt Beverages (TTB)",
         subject="Beer (labels)",
         pdf="https://www.ttb.gov/system/files/images/pdfs/beer-bam/complete-malt-beverage-alcohol-manual.pdf",
         page="https://www.ttb.gov/regulated-commodities/beverage-alcohol/beer/beverage-alcohol-manual/",
         description="The TTB's practical guide to beer and malt beverage labels: mandatory information, type size, "
                     "the health warning, class and type, alcohol content and net contents."),
]

# Old books on drinks and making them, in the US public domain (published before 1931), from the Internet Archive's
# scans with their machine-read text (the builder checks each item's year). They are OLD: their methods, hygiene and
# safety advice, measures and the laws they mention are out of date (some recipes use ingredients now known to be
# harmful), and the machine-read text has the scanner's mistakes. Units are kept as written (gallons, bushels,
# pounds, gills, wine glasses): nothing is converted. Each description says so; the distilling books start with the
# legal and safety notes.
DRINKS_OLD = dict(OLD_PD, group="drinks")
DRINKS_OLD_NOTE = (" Published in {year}: an old book whose methods, hygiene and safety advice and laws are out of "
                   "date, kept whole for its history and recipes; its units are as written (nothing converted).")
DISTILLING_NOTE = ("Legal and safety notes first: in the US, distilling spirits at home is illegal without federal "
                   "permits, even for personal use (26 U.S.C. 5601), unlike home brewing and winemaking, which "
                   "federal law allows for adults within limits; laws differ by state and country (New Zealand, for "
                   "example, allows home distilling). Distilling carries real risks: methanol poisoning from improper "
                   "cuts, fire and explosion from ethanol vapour, and pressure. ")


def _old_drink(name, title, subject, publisher, archive, year, description, country="United States",
               distilling=False):
    """An old public-domain drinks book from the Internet Archive as a PDF_DOCS entry."""
    return dict(DRINKS_OLD, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                published=str(year), country=country,
                description=(DISTILLING_NOTE if distilling else "") + description + DRINKS_OLD_NOTE.format(year=year))


PDF_DOCS += [
    # brewing
    _old_drink("wahl_henius_handy_book_brewing_1901", "American Handy-Book of the Brewing, Malting and Auxiliary "
               "Trades (Robert Wahl and Max Henius, 1901)", "Beer (brewing and malting)", "Wahl-Henius Institute "
               "(Chicago)", "americanhandyboo00wahl", 1901, "The Chicago brewing school's reference book of the whole "
               "trade: barley and malting, hops, water, yeast, mashing, boiling, fermentation, cellar work, beer types "
               "and their analysis."),
    _old_drink("pitt_how_to_brew_good_beer_1864", "How to Brew Good Beer (John Pitt, 1864)", "Beer (home brewing)",
               "John Pitt (Longman)", "howtobrewgoodbee00pitt", 1864, "A complete guide to brewing ale, bitter ale, "
               "table ale, brown stout, porter and table beer at home, with quantities, mashing heats and "
               "fermentation.", country="United Kingdom"),
    _old_drink("cobbett_cottage_economy_1833", "Cottage Economy (William Cobbett, 1833)", "Beer (home brewing) and "
               "household", "William Cobbett", "cottageeconomyco00cobbrich", 1833, "Cobbett's famous household book: "
               "brewing beer at home (with the utensils and quantities), making bread, keeping cows, pigs and bees.",
               country="United Kingdom"),
    _old_drink("booth_art_of_brewing_1829", "The Art of Brewing (David Booth, 1829)", "Beer (brewing)", "David Booth "
               "(Society for the Diffusion of Useful Knowledge)", "artofbrewing00bootrich", 1829, "A practical "
               "treatise on brewing for private families and the trade: malt, hops, water, mashing, boiling, "
               "fermenting and cellaring.", country="United Kingdom"),
    # wine, cider and fruit wines
    _old_drink("haraszthy_grape_culture_wines_1862", "Grape Culture, Wines, and Wine-Making (Agoston Haraszthy, 1862)",
               "Wine (grapes and winemaking)", "Agoston Haraszthy (Harper and Brothers)", "grapeculturewine02hara",
               1862, "The California pioneer's report on European vineyards and winemaking, written for the state of "
               "California: grape varieties, vineyards, pressing, fermentation, cellar work and sparkling wine."),
    _old_drink("roos_wine_making_hot_climates_1900", "Wine-Making in Hot Climates (L. Roos, 1900)", "Wine (making)",
               "L. Roos, translated for the Viticultural Station, Rutherglen (Victoria)", "winemakinginhotc00roosrich",
               1900, "A practical winemaking manual: the grapes, crushing, fermentation and its temperature, pressing, "
               "cellar care and wine faults.", country="Australia"),
    _old_drink("wright_old_time_recipes_home_made_wines_1922", "Old-Time Recipes for Home Made Wines, Cordials and "
               "Liqueurs (Helen S. Wright, 1922)", "Wine (country and fruit wines, cordials)", "Helen S. Wright "
               "(Dana Estes)", "oldtimerecipesfo00wrig", 1922, "Old family recipes for wines from fruits, flowers, "
               "vegetables and shrubs (elderberry, dandelion, currant, rhubarb, mead and many more), cordials, "
               "liqueurs and non-alcoholic drinks, with their quantities as written."),
    _old_drink("brannt_vinegar_cider_fruit_wines_1890", "A Practical Treatise on the Manufacture of Vinegar and "
               "Acetates, Cider, and Fruit-Wines (William T. Brannt, 1890)", "Cider and fruit wines", "William T. "
               "Brannt (Henry Carey Baird)", "practicaltreatis00branrich", 1890, "A manual of cider making, fruit "
               "wines and vinegar: the fruit, pressing, fermentation, clarifying, preserving and bottling."),
    _old_drink("alwood_cider_making_1903", "A Study of Cider Making in France, Germany, and England (William B. "
               "Alwood, 1903)", "Cider (making)", "US Department of Agriculture, Bureau of Plant Industry",
               "studyofcidermaki00alworich", 1903, "The USDA's report on how cider was made in Europe's cider "
               "countries, with comments on American methods: apples, milling, pressing, fermentation and storage."),
    _old_drink("crampton_fermented_alcoholic_beverages_1887", "Fermented Alcoholic Beverages, Malt Liquors, Wine and "
               "Cider (Charles A. Crampton, 1887)", "Beer, wine and cider (composition)", "US Department of "
               "Agriculture, Division of Chemistry (Bulletin 13, part 3)", "fermentedalcohol00cramrich", 1887, "The "
               "USDA chemists' study of American beer, wine and cider: how they are made, what is in them, and the "
               "adulterations of the time."),
    # spirits and distilling
    _old_drink("rattlehead_complete_practical_distiller_1880", "The Complete Practical Distiller (M. Lafayette Byrn "
               "as David Rattlehead, 1880)", "Spirits (distilling)", "Henry Carey Baird", "completepractica00rattrich",
               1880, "A distiller's manual of the time: mashing grain, fermenting, distilling and rectifying whisky, "
               "brandy, rum and gin, with mash bills and quantities as written.", distilling=True),
    _old_drink("wright_distillation_alcohol_farm_products_1918", "A Practical Handbook on the Distillation of Alcohol "
               "from Farm Products (F. B. Wright, 1918)", "Spirits (distilling)", "Frederic B. Wright (Spon and "
               "Chamberlain)", "practicalhandboo00wrig", 1918, "A handbook of making alcohol from grain, potatoes, "
               "fruit and molasses: mashing, fermentation, stills and their working, and denaturing (written for "
               "industrial alcohol).", distilling=True),
    _old_drink("boucherie_art_of_making_whiskey_1819", "The Art of Making Whiskey (Anthony Boucherie, 1819)",
               "Spirits (whiskey making)", "Anthony Boucherie (Lexington, Kentucky)", "the_art_of_making_whiskey_202011",
               1819, "An early American whiskey maker's treatise: grain, mashing, fermentation and distilling, so as "
               "to obtain a greater quantity and better quality of spirit.", distilling=True),
    _old_drink("rack_french_wine_and_liquor_manufacturer_1868", "The French Wine and Liquor Manufacturer (John Rack, "
               "1868)", "Spirits, liqueurs and cordials", "Dick and Fitzgerald", "b28061561", 1868, "A practical guide "
               "and receipt book for the liquor merchant of the time: distillation, liqueurs, cordials, bitters and "
               "syrups, with recipes and quantities as written.", distilling=True),
    # bars and cocktails
    _old_drink("thomas_bar_tenders_guide_1887", "The Bar-Tender's Guide, or How to Mix All Kinds of Plain and Fancy "
               "Drinks (Jerry Thomas, 1887)", "Cocktails and mixed drinks", "Jerry Thomas (Dick and Fitzgerald)",
               "bartendersguideo00thom", 1887, "The famous early bartender's book of recipes: punches, cocktails, "
               "juleps, sours, fizzes, cobblers, egg nogs, temperance drinks and syrups, measures as written."),
    _old_drink("haywood_mixology_1898", "Mixology: the Art of Preparing All Kinds of Drinks (Joseph L. Haywood, 1898)",
               "Cocktails and mixed drinks", "Joseph L. Haywood", "mixologyartofpre00hayw", 1898, "A bartender's "
               "recipe book of the 1890s: cocktails, punches, fizzes and other mixed drinks."),
    # soft drinks, juices and syrups
    _old_drink("sulz_treatise_on_beverages_1888", "A Treatise on Beverages, or the Complete Practical Bottler "
               "(Charles Herman Sulz, 1888)", "Soft drinks, mineral waters and syrups", "Dick and Fitzgerald",
               "treatiseonbevera00sulzrich", 1888, "The bottler's handbook of soda water, mineral waters, ginger ale, "
               "root beer, syrups and fruit juices: making, carbonating and bottling them, with formulas as written."),
    _old_drink("saxe_soda_water_dispensers_1894", "Saxe's New Guide, or Hints to Soda Water Dispensers (De Forest W. "
               "Saxe, 1894)", "Soft drinks (soda fountain)", "De Forest W. Saxe", "saxesnewguideorh00saxerich", 1894,
               "Formulas for the soda fountain's syrups, crushed fruits, phosphates, egg drinks and other soft drinks "
               "of the time."),
    _old_drink("wiley_beverages_and_their_adulteration_1919", "Beverages and Their Adulteration (Harvey W. Wiley, "
               "1919)", "Drinks of every kind", "Harvey W. Wiley (P. Blakiston's Son)", "beveragestheirad00wileuoft",
               1919, "The first FDA chief's book on every kind of drink: water, mineral waters, soft drinks, fruit "
               "juices, tea, coffee and cocoa, beer, wine and spirits, how they are made and how they were "
               "adulterated."),
    _old_drink("dearing_unfermented_grape_juice_home_1919", "Unfermented Grape Juice: How to Make It in the Home "
               "(Charles Dearing, 1919)", "Juices (making at home)", "US Department of Agriculture (Farmers' "
               "Bulletin 1075)", "CAT87203087", 1919, "The USDA's bulletin on making and keeping grape juice at home: "
               "the grapes, extracting, pasteurising, bottling and storage."),
    _old_drink("cruess_unfermented_fruit_juices_1920", "Unfermented Fruit Juices (W. V. Cruess, 1920)", "Juices "
               "(making)", "University of California Agricultural Experiment Station (Circular 220)",
               "unfermentedfruit220crue", 1920, "A circular on making fruit juices at home and in small plants: "
               "apple, grape, berry and citrus juices, extracting, clarifying, pasteurising and bottling."),
    _old_drink("moore_uncle_sams_water_wagon_1919", "On Uncle Sam's Water Wagon: 500 Recipes for Delicious Drinks, "
               "Which Can Be Made at Home (Helen Watkeys Moore, 1919)", "Soft drinks and mocktails (recipes)",
               "Helen Watkeys Moore (G. P. Putnam's Sons)", "cu31924000559967", 1919, "Non-alcoholic drinks for the "
               "home from the first year of Prohibition: fruit drinks, punches, syrups, sodas, milk drinks, tea and "
               "coffee drinks."),
]

# A drinks subject's practice note (non-US books): drinking ages, alcohol and home-production laws and label rules.
PRACTICE_SUBJECTS.insert(0, (r"\b(wine|beer|brew\w*|spirits?|distill\w*|cider|whisk(e?)y|cocktails?|drinks?|juices?|"
                             r"bartend\w*|malt\w*|liqueurs?)\b",
                             "drinking ages, alcohol laws, home brewing, winemaking and distilling rules (home "
                             "distilling is legal in some countries, such as New Zealand, but not in the US), label "
                             "rules and metric units"))

# Looked at for drinks on 2026-11-21 and not built, with the reason.
DRINKS_NOT_INCLUDED = [
    ("BJCP Style Guidelines (Beer Judge Certification Program, bjcp.org)", "Not openly licensed: the guidelines page "
     "asks anyone wanting to use them 'for purposes other than BJCP-sanctioned competitions or educational judge "
     "training' to contact the BJCP for permission. No licence allows copying them into a library, so they are not "
     "included (a link only: https://www.bjcp.org/bjcp-style-guidelines/)."),
    ("Brewers Association beer style guidelines and American Homebrewers Association recipes", "Copyrighted, with no "
     "open licence found; not included. Commercial recipe sites (Brewer's Friend and similar) are copyrighted too."),
    ("NIAAA (niaaa.nih.gov) and Rethinking Drinking", "Public domain (US government), but niaaa.nih.gov's robots.txt "
     "says 'Content-Signal: search=yes,ai-train=no,use=reference' and shuts out ClaudeBot and other AI crawlers by "
     "name, so it is not read."),
    ("Open Food Facts (labels and nutrition of drinks)", "Its robots.txt shuts out AI crawlers by name (GPTBot, "
     "anthropic-ai, ClaudeBot) on every host, and search.openfoodfacts.org disallows every robot; not read."),
    ("TTB COLAs Online public registry (approved label images)", "ttbonline.gov refused this machine's connections, "
     "so its robots.txt and terms could not be checked; it has no official bulk download, and the labels are the "
     "companies' own artwork. Not read."),
    ("eCFR (ecfr.gov) full-text services", "Its robots.txt shuts out automated readers of its full-text services; the "
     "same regulations come whole from govinfo.gov's annual edition."),
    ("UCI Wine Quality data set (CC BY 4.0)", "Chemical measurements only (acidity, sugar, alcohol and a score), no "
     "words for describing wine; not a reference book."),
    ("Project Gutenberg", "Its site was down for maintenance on 2026-11-21; the same old books are read from the "
     "Internet Archive's scans."),
    ("University extension guides on home winemaking, cider and brewing", "Each is licensed by its own university, "
     "and none with a clear open licence was confirmed in this pass (Penn State, Minnesota, UC ANR and Oregon State "
     "were looked at: their robots.txt files allow reading, but no open licence was found on their pages). A "
     "candidate for a later pass, one guide at a time; the USDA's and the University of California's old "
     "public-domain bulletins are included instead."),
]
NOT_INCLUDED = NOT_INCLUDED + DRINKS_NOT_INCLUDED
