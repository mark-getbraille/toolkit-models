"""Emergency preparedness and disasters for the reference library, in the group "Reference, emergency preparedness and
disasters" (the owner's request of 2026-11-22: help him and others prepare for and get through emergencies). Keys:
disasters (every book), ready:<name>.

This module EXTENDS the four books of emergency_prep.py (request word "preparedness": the NWS weather safety pages,
the NOAA Weather Radio pages and station list, and FEMA's 2004 "Are You Ready?" guide), which are not repeated here.

What this module builds, in plain words, each IN FULL:
  - Ready.gov (FEMA), every English page for people and families: making a plan (family communication plan,
    meeting places, important documents), building a kit (home, car, work; medications and medical devices; low
    and no-cost preparedness), financial preparedness, every hazard page with what to do before, during and after
    (hurricanes, tornadoes, floods, wildfires, earthquakes, winter weather, extreme heat, power outages, drought,
    landslides, tsunamis, volcanoes, thunderstorms and lightning, pandemics, hazardous materials, household chemical
    emergencies, nuclear and radiation emergencies, explosions, biohazards, cybersecurity, space weather, home fires,
    avalanches, mass gatherings), alerts and warnings, evacuation, shelter (sealing a room, shelter in place),
    people with disabilities, older adults, caregivers, pets and animals, safety skills, recovering from a disaster
    and coping with it. (Ready.gov answered this build machine's reader on 2026-11-22; on another day it refused,
    as the notes of other modules say, so a page that is refused at build time is simply left out.)
  - the Nuclear Regulatory Commission's pages for the public on radiological emergencies (planning zones, how you
    are warned, sheltering, evacuating, potassium iodide ONLY as state or local officials direct);
  - CISA's active shooter preparedness pages (Run, Hide, Fight; emergency action plans; resources for houses of
    worship, schools and businesses);
  - ASPR's pages on at-risk people and people with access and functional needs in disasters (older adults, people
    with disabilities, people without homes, service animals, sheltering in place, language access) and HHS
    emPOWER's pages (the programme that tells local health and emergency officials, in a disaster, how many people
    in an area rely on electricity-dependent medical equipment);
  - the Small Business Administration's disaster loan pages (low-interest disaster loans for homeowners, renters and
    businesses after a declared disaster);
  - the EPA's natural disaster pages (what to do about drinking water, mould, debris, generators and chemicals before
    and after floods, hurricanes, wildfires, tornadoes, earthquakes, winter storms, drought, heat, tsunamis and
    volcanoes) and its wildfire smoke and indoor air pages (making a clean room, air cleaners and filters), marked
    PERSONAL USE ONLY (the EPA's copyright statement allows non-commercial, scientific and educational use);
  - "Where to find more": a short book written here (CC0) of the guides that could not be copied, with what each
    is, who publishes it and its address, so the owner can fetch them himself with Program Downloader: the
    preparedness and food-storage guides of The Church of Jesus Christ of Latter-day Saints (its terms forbid
    automatic copying), Utah State University Extension and BYU, the American Red Cross, CDC, NIH (REMM and the
    Disaster Information Management Research Center), FEMA's CERT manuals and "How to Prepare" guides, the
    Disaster Distress Helpline, Canada's Get Prepared and the UK's Be Ready.

Shared work and where it is: emergency and camp cooking, water boiling, purifying and storing water, food safety in
outages and emergency food storage are the emergency cooking books of the outdoorcook work; first aid, home health
and wilderness and disaster first aid are the life skills books; emergency heating (stoves, kerosene heaters, carbon
monoxide) and emergency lighting are the home crafts books (home-crafts: craft:usfa_home_heating_fire_safety and
craft:epa_burn_wise); the US Army survival manual ATP 3-50.21 (which replaced FM 21-76) is in the field manual
library (fieldmanuals); two-way radio, ham radio, mesh radio and NOAA Weather Radio receivers in depth are the radio
books (radio_books.py, request word "radio").

Safety: every book's notice ends with SAFETY_NOTE (follow your local officials' instructions; generators and other
fuel-burning devices only outdoors, at least 20 feet from windows and doors, carbon monoxide alarm, get out and call
911 if it sounds; turn around, don't drown; stay away from downed power lines; 911 in danger), and the recovery books
with RECOVERY_NOTE (the Disaster Distress Helpline 1-800-985-5990 and 988).

Licences: Ready.gov, NRC, CISA, ASPR, HHS and SBA pages are works of the US government (17 U.S.C. 105, the line
checked on govinfo.gov's policies page at every build); the EPA's copyright statement is checked on its disclaimer
page at every build (personal use only). robots.txt of every site read allows the pages and has no AI rules
(checked 2026-11-22; the builder asks again at every build). The "Where to find more" book is this toolkit's own
words (CC0) with addresses only.

Run from the repository's folder:
  python3 textbooks/disaster_ready.py ready:ready_gov --out build/textbooks --limit 5
  python3 textbooks/disaster_ready.py --list disasters
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "emergency"
GROUPS = {GROUP: "Reference, emergency preparedness and disasters"}

# The safety words every book carries (the same as packs/preparedness_packs.py and the kit; the self-tests check).
SAFETY_NOTE = ("Safety: follow your local officials' instructions, and evacuate when they tell you to. Use generators, "
               "grills and other fuel-burning devices only outdoors, at least 20 feet from windows, doors and vents; "
               "have a working carbon monoxide alarm, and if it sounds or anyone feels dizzy or sick, get out to fresh "
               "air and call 911. Never walk or drive through floodwater: turn around, don't drown. Stay far away "
               "from downed power lines and report them. In danger, call 911.")
RECOVERY_NOTE = ("After a disaster, help is there: the Disaster Distress Helpline, call or text 1-800-985-5990 (any "
                 "time, free, in many languages), or call or text 988 (the Suicide and Crisis Lifeline).")
US_NOTICE = "A work of {who} (public domain in the US). " + SAFETY_NOTE

# The EPA's terms: the same names as home_crafts.py and pets_home.py (pets_home adds EPA_TERMS to sources.ALLOWED as
# non-commercial).
EPA_TERMS = "EPA website copyright statement"
EPA_DISCLAIMER = "https://www.epa.gov/web-policies-and-procedures/epa-disclaimers"
EPA_TEXT = r"These documents may be freely distributed and used for non-commercial, scientific and educational purposes"
EPA_NOTICE = ("From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
              "distributed and used for non-commercial, scientific and educational purposes\". " + SAFETY_NOTE)

# ====================================================================== Ready.gov

READY = "https://www.ready.gov"
# Ready.gov's English pages for people and families, in parts (the sitemap read 2026-11-22, and the pages its menus
# link). Translations, Ready Business, Ready Kids games, social-media toolkits, webinars and campaign pages are left
# out (READY_NOT): they are for organisations, or repeat the pages here in other words.
READY_PARTS = [
    ("Make a plan", ["plan", "make-a-plan", "plan-for-locations", "home-fire-escape-plan", "financial-preparedness",
                     "emergency-financial-first-aid-kit", "get-tech-ready", "low-and-no-cost", "safety-skills",
                     "home-safety", "alerts"]),
    ("Build a kit", ["kit", "car", "water", "food", "preparing-your-own-containers-water",
                     "storing-water-plastic-soda-bottles", "winter-ready", "summer-ready"]),
    ("People with disabilities, older adults, caregivers and pets", ["people-disabilities", "older-adults",
                                                                     "seniors", "caregivers", "pets", "animals"]),
    ("Disasters and emergencies", ["be-informed", "hurricanes", "tornadoes", "floods", "wildfires", "earthquakes",
                                   "winter-weather", "heat", "power-outages", "drought", "landslides-debris-flow",
                                   "tsunamis", "volcanoes", "thunderstorms-lightning", "severe-weather",
                                   "space-weather", "avalanche", "home-fires", "pandemic", "hazmat",
                                   "household-chemical-emergencies", "radiation", "explosions", "biohazard",
                                   "cybersecurity", "mass-gatherings-incidents", "attacks-public-places",
                                   "active-shooter", "bomb-threats", "nuclear-explosion", "chemical"]),
    ("Evacuation and shelter", ["evacuation", "shelter"]),
    ("Get involved: CERT and community", ["get-involved", "cert", "community", "skywarn"]),
    ("Recovering from a disaster", ["recovering-disaster", "coping-disaster"]),
]
READY_NOT = (r"(?:es|ar|fr|ht|ja|ko|ru|tl|vi|zh-hans|zh-hant|pt|de|hi|pl)(?:/.*)?|kids(?:/.*)?|business(?:/.*)?|"
             r"collection/.*|node/.*|about-us(?:/.*)?|terms-and-conditions|accessibility|calendar|resources|"
             r"publications|resource-library|toolkits|testimonials|thanks-your-question|fifa-world-cup-2026|"
             r"community-preparedness-webinar-series.*|individual-and-community-preparedness-webinar.*|"
             r"citizen-corps.*|today-.*|.*toolkit.*|.*-old|lapse-federal.*|20\d\d-.*|resolution|its-not-luck|"
             r"ready-your-language|localized-ready-programs|community-state-info|faqs-state-coordinators|campus|"
             r"shields-ready|national-crime-prevention-council|fema-app|plan-form|make-a-plan-kids|know-facts-kids")
READY_PAGES = rf"^https://www\.ready\.gov/(?!(?:{READY_NOT})$)[a-z0-9-]+$"

GUIDES = [
    K.us_web(GROUP, name="ready_gov", title="Ready.gov: plans, kits, disasters, evacuation and recovery (FEMA)",
             subject="Emergency preparedness", publisher="Federal Emergency Management Agency (Ready.gov)",
             source=f"{READY}/", notice=US_NOTICE.format(who="the Federal Emergency Management Agency (Ready.gov)")
             + " " + RECOVERY_NOTE,
             description="Every Ready.gov page for people and families: making a family emergency plan and a "
                         "communication plan, meeting places, important documents and financial preparedness; "
                         "building a kit for home, car and work, with water, food, medications and medical "
                         "supplies; what to do before, during and after hurricanes, tornadoes, floods, wildfires, "
                         "earthquakes, winter weather, extreme heat, power outages, drought, landslides, tsunamis, "
                         "volcanoes, thunderstorms and lightning, pandemics, hazardous materials, nuclear and "
                         "radiation emergencies, explosions and cyberattacks; alerts and warnings; evacuation and "
                         "shelter; preparing as a person with a disability, an older adult, a caregiver or a pet "
                         "owner; CERT and community preparedness; and recovering from and coping with a disaster.",
             urls=[(f"{READY}/{slug}", part) for part, slugs in READY_PARTS for slug in slugs],
             crawl=[(f"{READY}/be-informed", 1)], pages=READY_PAGES,
             unit_rules=[(r".", "Disasters and emergencies")], limit=160),
]

# ====================================================================== NRC, CISA, ASPR and emPOWER, SBA

NRC = "https://www.nrc.gov/about-nrc/emerg-preparedness"
GUIDES += [
    K.guide(GROUP, "nrc_radiological_emergencies", "Radiological emergencies at nuclear power plants: what to do "
            "(Nuclear Regulatory Commission)", "Nuclear power plant emergencies",
            "US Nuclear Regulatory Commission (NRC)", f"{NRC}.html",
            rf"^https://www\.nrc\.gov/about-nrc/emerg-preparedness(\.html|/(about-emerg-preparedness(/[a-z0-9-]+)?|"
            r"faq|in-radiological-emerg|prepare-for-radiological-emerg|protect-public(/[a-z0-9-]+)*|"
            r"respond-to-emergency)(\.html)?)$",
            "The NRC's pages for the public on emergencies at nuclear power plants: how emergency planning works and "
            "the planning zones around each plant, the four emergency classes, how you would be warned (sirens, "
            "the Emergency Alert System, radio and TV), what to do in a radiological emergency (go inside, stay "
            "inside, stay tuned), sheltering in place and evacuating, potassium iodide (taken only when state or "
            "local officials say to), and frequent questions.",
            US_NOTICE.format(who="the US Nuclear Regulatory Commission") + " Take potassium iodide (KI) only when "
            "your state or local public health or emergency officials tell you to: it protects only the thyroid, "
            "and only from radioactive iodine.", depth=1,
            follow=rf"^https://www\.nrc\.gov/about-nrc/emerg-preparedness/(about-emerg-preparedness|protect-public)$",
            urls=[f"{NRC}/in-radiological-emerg", f"{NRC}/protect-public"], limit=40),
    K.guide(GROUP, "cisa_active_shooter", "Active shooter preparedness: Run, Hide, Fight (CISA)",
            "Active threats", "Cybersecurity and Infrastructure Security Agency (CISA), US Department of Homeland "
            "Security", "https://www.cisa.gov/topics/physical-security/active-shooter-preparedness",
            r"^https://www\.cisa\.gov/topics/physical-security/active-shooter-preparedness(/[a-z0-9-]+)?$",
            "CISA's active shooter preparedness pages: how to respond when an active shooter is nearby (Run, Hide, "
            "Fight), recognising warning signs, emergency action plans, what to do when law enforcement arrives, "
            "and the resources for businesses, houses of worship, schools and first responders.",
            US_NOTICE.format(who="the Cybersecurity and Infrastructure Security Agency (US Department of Homeland "
                                 "Security)").replace(SAFETY_NOTE, "In danger, call 911 when it is safe to do so."),
            depth=1, limit=20),
    K.guide(GROUP, "aspr_at_risk_empower", "People with access and functional needs in disasters, and HHS emPOWER "
            "(ASPR, HHS)", "Disability, older adults and power-dependent equipment in disasters",
            "Administration for Strategic Preparedness and Response (ASPR), US Department of Health and Human "
            "Services", ["https://aspr.hhs.gov/at-risk/Pages/default.aspx", "https://empowerprogram.hhs.gov/"],
            r"^https://(aspr\.hhs\.gov/at-risk/Pages/(?![A-Za-z_-]*spanish)[A-Za-z_-]+\.aspx|"
            r"empowerprogram\.hhs\.gov/(index|about|about-empowermap|faqs|in-action|resources)\.html)$",
            "ASPR's pages on people who may need more help in a disaster: access and functional needs, older "
            "adults, people with disabilities, people without homes, children with special health care needs, "
            "language access, service animals, sheltering in place and tribal preparedness; and the HHS emPOWER "
            "programme, which tells local health and emergency officials how many people in an area rely on "
            "electricity-dependent medical and assistive equipment (oxygen concentrators, ventilators, power "
            "wheelchairs, home dialysis), so they can be checked on in an outage.",
            US_NOTICE.format(who="the Administration for Strategic Preparedness and Response (HHS)") + " If you use "
            "power-dependent medical equipment, tell your power company (many have a medical-needs or medical "
            "baseline programme) and your local emergency management office, and plan for backup power.",
            depth=1, limit=40),
    K.guide(GROUP, "sba_disaster_loans", "Disaster loans for homeowners, renters and businesses (SBA)",
            "Disaster recovery money", "US Small Business Administration (SBA)",
            ["https://www.sba.gov/funding-programs/disaster-assistance", "https://www.sba.gov/disaster"],
            r"^https://www\.sba\.gov/(funding-programs/disaster-assistance(/[a-z0-9-]+)*|disaster(/[a-z0-9-]+)*)/?$",
            "The SBA's disaster assistance pages: low-interest disaster loans for homeowners and renters (to repair or "
            "replace a home and belongings) and for businesses and non-profits, who can apply after a declared "
            "disaster, how to apply, and what happens next.",
            US_NOTICE.format(who="the US Small Business Administration") + " " + RECOVERY_NOTE +
            " Beware of scams after a disaster: government workers never charge for help or ask for money to "
            "apply.", depth=1, limit=30),
]

# ====================================================================== EPA (personal use)

EPA_DISASTERS = (r"natural-disasters(/(?!forms/)[a-z0-9-]+)*|emergencies-iaq/[a-z0-9-]+|"
                 r"indoor-air-quality-iaq/air-cleaners-and-air-filters-home|air-research/smoke-ready-toolbox-wildfires")
GUIDES += [
    dict(K.guide(GROUP, "epa_disasters_smoke", "Natural disasters, flood cleanup and wildfire smoke (EPA)",
                 "Disasters and the environment at home", "US Environmental Protection Agency (EPA)",
                 ["https://www.epa.gov/natural-disasters", "https://www.epa.gov/smoke-ready-toolbox-wildfires"],
                 rf"^https://www\.epa\.gov/({EPA_DISASTERS})$",
                 "The EPA's natural disaster pages, every page: before and after floods, hurricanes, wildfires, "
                 "tornadoes, earthquakes, snow and ice, drought, extreme heat, tsunamis and volcanoes (drinking water "
                 "and private wells, mould and flood cleanup, debris, generators and carbon monoxide, chemicals and "
                 "hazardous waste), and its wildfire smoke pages: the Smoke-Ready Toolbox, making a clean room, "
                 "wildfires and indoor air, and choosing air cleaners and filters for the home.",
                 EPA_NOTICE, depth=2, follow=r"^https://www\.epa\.gov/natural-disasters(/[a-z0-9-]+)?$",
                 units=[(r"/natural-disasters/flood", "Floods"), (r"/natural-disasters/hurricane", "Hurricanes"),
                        (r"/natural-disasters/wildfire|smoke|iaq|air-cleaners", "Wildfires and smoke"),
                        (r".", "Natural disasters")], limit=80),
         licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
         personal_use=True),
]

# ====================================================================== "Where to find more" (link-only guides)

# Each: (title, who publishes it, what it is and why it is not copied, address). The book holds these words only
# (written here, CC0) and the addresses; nothing of the guides themselves.
LINK_ONLY = [
    # The Church of Jesus Christ of Latter-day Saints: a faith community's practical guidance (the coordinator's
    # request of 2026-11-22). Its terms of use (churchofjesuschrist.org/legal/terms-of-use, read 2026-11-22) allow
    # personal, non-commercial viewing and printing but forbid using "any robot, spider, or other automatic device,
    # process, or means to access this site for any purpose, including ... copying any of the material", so nothing
    # is read by program; the owner can save these pages himself with Program Downloader.
    ("Emergency Preparedness and Family Home Storage (The Church of Jesus Christ of Latter-day Saints)",
     "Provident Living, The Church of Jesus Christ of Latter-day Saints (Intellectual Reserve, Inc.)",
     "A faith community's practical guidance on self-reliance: home storage (a three-month supply of everyday "
     "food, drinking water, longer-term storage of basics such as wheat, white rice and beans, rotation and shelf "
     "lives), 72-hour kits, financial reserves, and planning for emergencies. Its terms forbid copying by program; "
     "personal use only, so fetch it yourself.",
     "https://providentliving.churchofjesuschrist.org/food-storage"),
    ("All Is Safely Gathered In: Family Home Storage, and Family Finances (pamphlets)",
     "The Church of Jesus Christ of Latter-day Saints",
     "The Church's two short pamphlets on home storage (food storage and drinking water) and on family finances "
     "(budgeting, staying out of debt, a financial reserve). Its terms forbid copying by program; fetch them "
     "yourself for personal use.",
     "https://www.churchofjesuschrist.org/study/manual/all-is-safely-gathered-in-family-home-storage"),
    ("Home Storage Center product list and longer-term food storage",
     "The Church of Jesus Christ of Latter-day Saints",
     "The products its Home Storage Centers sell for longer-term storage (wheat, rice, beans, oats, dry milk and "
     "others in cans and pouches) with their stated shelf lives, and how to store and rotate them. Its terms forbid "
     "copying by program; fetch it yourself.",
     "https://providentliving.churchofjesuschrist.org/food-storage/home-storage-center-locations"),
    ("Personal Finances for Self-Reliance, and Emergency Response (self-reliance and ward and stake planning)",
     "The Church of Jesus Christ of Latter-day Saints",
     "The self-reliance group course on personal finances (budgeting, protecting against hardship, managing debt, "
     "investing), and the Church's emergency response and ward and stake emergency planning guidance. Its terms "
     "forbid copying by program; fetch them yourself for personal use.",
     "https://www.churchofjesuschrist.org/self-reliance"),
    ("Utah State University Extension: emergency preparedness and food storage",
     "Utah State University Extension",
     "USU Extension's preparedness fact sheets (food storage, water storage, 72-hour kits, emergency planning). "
     "Copyright of Utah State University (its pages state no open licence; checked 2026-11-22), so it is link-only.",
     "https://extension.usu.edu/preparedness/"),
    ("BYU food storage research (Department of Nutrition, Dietetics, and Food Science)",
     "Brigham Young University",
     "BYU's studies of how long stored foods (wheat, rice, dry milk, beans) stay usable. \"All rights reserved\" "
     "(byu.edu, checked 2026-11-22), and byu.edu asks programs to wait 10 seconds between pages; link-only.",
     "https://ndfs.byu.edu/"),
    ("American Red Cross: How to prepare for emergencies",
     "American Red Cross",
     "The Red Cross's preparedness guides and checklists by type of emergency, and its free apps. \"© American Red "
     "Cross\" (copyright, no open licence); link-only.",
     "https://www.redcross.org/get-help/how-to-prepare-for-emergencies.html"),
    ("CDC Emergency Preparedness and Response, natural disasters and radiation emergencies",
     "US Centers for Disease Control and Prevention",
     "Public domain, but www.cdc.gov answered this build machine \"403 Forbidden\" (2026-11-22). It can be built "
     "when CDC answers again.",
     "https://www.cdc.gov/natural-disasters/index.html"),
    ("Radiation Emergency Medical Management (REMM) and the Disaster Information Management Research Center",
     "US National Library of Medicine (NIH) and ASPR",
     "Public domain, but remm.hlm.nih.gov and disasterinfo.nlm.nih.gov could not be reached from this build "
     "machine's network (2026-11-22). REMM is written for health care workers.",
     "https://remm.hlm.nih.gov/"),
    ("CERT Basic Training participant manual, and FEMA's How-to-Prepare guides",
     "Federal Emergency Management Agency (FEMA)",
     "Public domain, but their pages on www.fema.gov and community.fema.gov refused this build machine (403, or no "
     "connection, 2026-11-22), and no Internet Archive copy with their words was found. Ready.gov's own CERT page "
     "is in the Ready.gov book when it answers.",
     "https://www.fema.gov/emergency-managers/individuals-communities/preparedness-activities-webinars/"
     "community-emergency-response-team"),
    ("DisasterAssistance.gov (apply for FEMA help after a disaster)",
     "FEMA and partner agencies",
     "The place to apply for federal help after a declared disaster, and to check an application; an interactive "
     "service, not a guide, so it is listed, not copied. Phone: 1-800-621-3362.",
     "https://www.disasterassistance.gov/"),
    ("Disaster Distress Helpline (SAMHSA)",
     "Substance Abuse and Mental Health Services Administration",
     "Free, confidential crisis counselling for anyone distressed by a disaster: call or text 1-800-985-5990, any "
     "time. samhsa.gov refused this build machine (403, 2026-11-22).",
     "https://www.samhsa.gov/find-help/disaster-distress-helpline"),
    ("HHS emPOWER Map",
     "US Department of Health and Human Services",
     "An interactive map of how many Medicare beneficiaries in each area rely on electricity-dependent equipment; an "
     "interactive tool, so it is listed, not copied (the programme's own pages are in the ASPR book).",
     "https://empowermap.hhs.gov/"),
    ("Get Prepared (Public Safety Canada)",
     "Government of Canada (non-US: Canadian numbers and agencies)",
     "Canada's emergency preparedness guide (Your Emergency Preparedness Guide, kits, plans, hazards). The canada.ca "
     "web pages' terms allow non-commercial reproduction only; Health Canada's and the Public Health Agency's "
     "emergency preparedness pages are listed on open.canada.ca under the Open Government Licence - Canada, but "
     "www.canada.ca and getprepared.gc.ca closed the connection to this build machine (2026-11-22); link-only.",
     "https://www.getprepared.gc.ca/"),
    ("Be Ready (UK government)",
     "UK Government Cabinet Office (non-US: in the UK call 999)",
     "The UK government's preparedness campaign (emergency kits, power cuts, flooding, staying informed). Its site is "
     "a single page that builds itself with scripts, so there was nothing for the builder to read; link-only.",
     "https://prepare.campaign.gov.uk/"),
    ("State and county emergency management guides",
     "US state and county emergency management agencies",
     "Most state guides are each state's copyright, and they differ by state; find yours through your state's "
     "emergency management agency (Ready.gov lists them), and ask about its special-needs or functional-needs "
     "registry and your power company's medical-needs programme.",
     "https://www.ready.gov/community-state-info"),
]


def links_book(name, work, cache=None, left_out=None, limit=None):
    """The "Where to find more" book: one page per guide of LINK_ONLY (its title, publisher, what it is and why it is
    not copied, and its address), written here (CC0)."""
    import build_textbooks as B
    book = K.new_book("ready_where_to_find_more", "Where to find more: preparedness guides to fetch yourself",
                      "Emergency preparedness (links)", GROUP, "Digital Accessibility Toolkit (this list's own words)",
                      K.CC0, K.CC0_URL, "https://github.com/mark-getbraille/toolkit-models",
                      "Preparedness guides that could not be copied into the library (their terms or their sites do "
                      "not allow it): what each is, who publishes it and its address, to open in a browser or fetch "
                      "with Program Downloader for your own use. Among them: The Church of Jesus Christ of Latter-day "
                      "Saints' home storage and emergency preparedness guidance, Utah State University Extension and "
                      "BYU food storage guides, the American Red Cross, CDC, FEMA's CERT manual, the Disaster Distress "
                      "Helpline, Canada's Get Prepared and the UK's Be Ready.",
                      "This list's own words are CC0; each guide belongs to its publisher. " + SAFETY_NOTE + " " +
                      RECOVERY_NOTE, changes="written for this library: addresses and short descriptions only")
    book.published = "2026-11-22"
    for i, (title, who, what, url) in enumerate(LINK_ONLY[:limit] if limit else LINK_ONLY, 1):
        body = K.dl([("Published by", who), ("What it is", what), ("Address", url)])
        book.pages.append(B.Page(f"guide-{i}-{B.slug(title, 40)}", title, body, 0, "Guides to fetch yourself"))
    # The guides' addresses are NOT recorded as originals: nothing was read from them, and the CC0 of this list does
    # not let anyone copy them (originals_of would otherwise mark them downloadable).
    return book


def links_sign(name):
    """The links book's sign of change: the list itself (it changes only when this file does)."""
    return K.sha(LINK_ONLY)


COLLECTION = K.Collection("ready", GROUP, guides=GUIDES, makers={"where_to_find_more": (links_book, links_sign)},
                          words={"disasters": lambda: [f"ready:{g['name']}" for g in GUIDES] +
                                 ["ready:where_to_find_more"]})

LICENCE_LINES = {
    "ready_us_government": "Ready.gov (FEMA), nrc.gov, cisa.gov, aspr.hhs.gov, empowerprogram.hhs.gov and sba.gov: "
                           "works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every "
                           "build). Their robots.txt allow the pages read and name no AI readers (checked "
                           "2026-11-22).",
    "ready_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): \"These documents may "
                 "be freely distributed and used for non-commercial, scientific and educational purposes\", so the "
                 "EPA book is personal use only.",
    "ready_links": "The \"Where to find more\" book is this toolkit's own words (CC0) with addresses; nothing of the "
                   "listed guides is copied.",
}
NOT_INCLUDED = [(title + " [" + who + "]", what + " Index: " + url) for title, who, what, url in LINK_ONLY] + [
    ("The unofficial \"LDS Preparedness Manual\" compilations", "Not the Church's own publication: they bundle other "
     "people's copyrighted material, so they are never used (the owner's rule). Index: "
     "https://providentliving.churchofjesuschrist.org/"),
    ("NHC hurricane preparedness pages (nhc.noaa.gov/prepare)", "Public domain, but the pages are built by scripts "
     "and gave the builder no text to read (2026-11-22); the NWS hurricane safety pages are in prep:nws_safety. "
     "Index: https://www.nhc.noaa.gov/prepare/"),
    ("USGS natural hazards (earthquakes, volcanoes, landslides)", "Public domain, but its hazard pages are mostly "
     "science news and data portals rather than guides; Ready.gov's hazard pages and the EPA's are built instead. "
     "Index: https://www.usgs.gov/programs/earthquake-hazards/prepare"),
    ("Administration for Community Living emergency preparedness page", "Public domain, but its page has no main "
     "content area the builder can find (2026-11-22). Index: https://acl.gov/emergencypreparedness"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
