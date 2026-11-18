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

ALLOWED = {
    "CC0": "open", "PD": "open", "OGL": "open", "CC BY": "open", "CC BY-SA": "share-alike",
    US_GOV: "open", "OGL-UK-3.0": "open", "OGL-Alberta": "open", "OGL-Canada": "open", "OGL-Ontario": "open", "OGL-BC": "open",
    "CC BY-NC": "non-commercial", "CC BY-NC-SA": "non-commercial",
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
    ("Rules of Unified English Braille (ICEB)", "CC BY-NC-ND 2.5 Australia (NoDerivatives): may be shared whole and "
     "unchanged but not made into web pages. Download the PDF from iceb.org and add it with \"Your own "
     "documents\" instead."),
    ("W3C WAI guidance other than the Curricula (WCAG, tutorials, Easy Checks)", "W3C Document License: copies of "
     "whole documents are allowed, changes are not (and a ZIM book changes them); WCAG itself is in the toolkit's "
     "own help."),
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
