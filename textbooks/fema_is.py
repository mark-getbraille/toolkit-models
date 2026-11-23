"""FEMA's Independent Study (IS) courses, for the reference library, in the group "Reference, FEMA emergency management
courses (Independent Study)" (the owner's request of 2026-11-23: offline emergency and disaster training). Keys:
fema:<course> (one course, such as fema:is100c), fema:nims_2017, fema:ics_training_reference_guide and fema:index.
Request words: fema-is (every book) and one word per theme: fema-ics, fema-hazards, fema-community, fema-mass-care,
fema-recovery and fema-management.

What this module builds, in plain words. FEMA's Emergency Management Institute (EMI, now part of FEMA's National
Disaster and Emergency Management University, NDEMU) offers about 110 free self-paced courses on
training.fema.gov. Each course is read WHOLE, from the best copy EMI publishes openly:
  - the Student Manual PDF of the course's "Course Materials" (classroom version): IS-100.c and IS-200.c (from the
    course's complete-course zip file, of which only the Student Manual is read) and IS-700.b (its own PDF);
  - otherwise the web-based lesson itself on emilms.fema.gov. Newer courses use one data file
    ("courseStructure.js") that holds every screen of every lesson: its text and tables, the descriptions of its
    pictures and its knowledge-check questions with the right answers marked. Items are tagged for the printed
    classroom guides ("publish filters": Instructor Guide, Student Guide, Visuals); the builder keeps what the web
    lesson shows when EMI's course page opens it (_filtered: the older version of the player shows only untagged
    items, the newer one shows them all), leaves out repeats and screens titled "PRINT ONLY" (classroom
    discussions). Older courses use a lesson player whose table of contents ("curriculum/1.html") lists every screen
    ("groups/<n>.html"), which are read one by one, at the builder's pace (about 5,200 screens in all);
  - two reference documents the courses use: the National Incident Management System, Third Edition (October 2017),
    a handout of IS-700.b, and the ICS Training Reference Guide of IS-995;
  - fema:index, written here (CC0): every course in plain words, by theme, with its number, what it teaches, how
    long it takes, its course date and its key (or why it is a link only), how to take the free online exam for a
    certificate, and the related books already in the library (FEMA's "Are You Ready?" guides, the CERT Basic
    Training participant manual, Ready.gov and others).
Pop-up windows of the old player (a lesson's printable version, extra summaries) and the final exams are not read
(exam questions are kept secret by EMI to protect the test).

Leaving things out (the owner's rules): a screen or PDF part that prints someone else's copyright notice ("©",
"Copyright 2015", "All rights reserved", "used with permission") is left out and said in the manifest (left_out);
a course whose text carries a restricted handling marking (FOR OFFICIAL USE ONLY, LAW ENFORCEMENT SENSITIVE,
CONTROLLED UNCLASSIFIED INFORMATION) or says it "includes copyrighted content" is not built at all. When the courses
were surveyed on 2026-11-23 (every newer lesson file whole, the first 15 screens of every older lesson), only IS-904
said so (it is a link only); no copyright notice or marking was found elsewhere, but the builder checks at every
build.

Licences: every course and document is a work of FEMA, part of the US government (17 U.S.C. 105: public domain; the
line is checked on govinfo.gov's policies page at every build). training.fema.gov and emilms.fema.gov have no
robots.txt (404, so no rules and no AI rules; checked 2026-11-23, and the builder asks again at every build).

Already in the library and linked from fema:index (not repeated): FEMA's "Are You Ready?" (IS-22, 2004:
prep:fema_are_you_ready; 2020: gpo:fema_are_you_ready_2020), the CERT Basic Training participant manual
(gpo:fema_cert_basic_training_2019) and the other FEMA booklets of govinfo_fill.py (request word gpo-ready),
Ready.gov and CISA's active shooter pages (disaster_ready.py, request word disasters), the NWS weather safety pages
(preparedness) and the US Fire Administration's home fire pages (home-crafts).

Not built (NOT_INCLUDED): IS-905 and IS-917 (active shooter courses made of interactive animations with no
readable text), IS-904 (it says it includes copyrighted content used with permission), IS-800.d (EMI points to the
National Response Framework on www.fema.gov, which refuses programs), IS-324.a (hosted by COMET at UCAR, a
non-federal site with its own copyright), IS-271.a (withdrawn for review), and the retired courses asked about
(IS-368, IS-394.a, IS-325, IS-326, IS-632.a, IS-552, IS-522 and others: retired by EMI, most without lesson files left
online). IS-907 (Active Shooter: What You Can Do) is retired too, but EMI still publishes its lesson, so it is built
with a notice that it is retired.

Run from the repository's folder:
  python3 textbooks/fema_is.py --list fema-is
  python3 textbooks/fema_is.py fema:is909 --out build/textbooks --limit 5
"""

import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

PREFIX = "fema"
GROUP = "fema"
GROUPS = {GROUP: "Reference, FEMA emergency management courses (Independent Study)"}

PUBLISHER = ("FEMA Emergency Management Institute (National Disaster and Emergency Management University), US "
             "Department of Homeland Security")
CATALOGUE = "https://training.fema.gov/is/crslist.aspx?all=true"
OVERVIEW = "https://training.fema.gov/programs/independent-study/courseoverview.aspx?code={code}&lang=en"
EMILMS = "https://emilms.fema.gov/{folder}/"
COURSE_FILES = "https://training.fema.gov/programs/independent-study/_course-files/"
SID = "https://cdp.dhs.gov/femasid"

# What every course book says about the exam and about real emergencies.
EXAM_NOTE = ("To earn FEMA's certificate, take the course's free final exam online at training.fema.gov (open the "
             "course's page from the course list and choose Take Final Exam). You need a free FEMA Student "
             "Identification number (SID), from " + SID + "; the pass mark is 75 percent.")
TRAINING_NOTE = ("This is training material, not instructions for a real emergency: then follow your local "
                 "officials, and call 911 in danger.")

# Someone else's copyright notice, and restricted handling markings (written in capitals, as they are printed).
THIRD_PARTY = re.compile(r"©|&copy;|\(c\)\s*(19|20)\d\d|\bcopyright\s*(©|\(c\)|(19|20)\d\d)|all rights reserved|"
                         r"(used|reprinted|reproduced) (here )?with (the )?permission", re.I)
# A course's own statement that it holds other people's copyrighted material: then the whole course is left out.
COURSE_COPYRIGHT = re.compile(r"(training|course|lesson) (includes|contains|uses) copyrighted (content|material)", re.I)
RESTRICTED = re.compile(r"FOR OFFICIAL USE ONLY|//\s*FOUO\b|LAW ENFORCEMENT SENSITIVE|"
                        r"CONTROLLED UNCLASSIFIED INFORMATION|//\s*CUI\b")

# The themes: request word, part title in the index, and the subject words of their books.
THEMES = {
    "ics": ("fema-ics", "Incident command, NIMS and the national frameworks", "Incident command and NIMS"),
    "hazards": ("fema-hazards", "Hazards, floods and mitigation", "Hazards and mitigation"),
    "community": ("fema-community", "Community, schools, animals and people's needs", "Community preparedness"),
    "mass_care": ("fema-mass-care", "Mass care, shelters, logistics and volunteers", "Mass care and logistics"),
    "recovery": ("fema-recovery", "Damage assessment, recovery and Public Assistance", "Disaster recovery"),
    "management": ("fema-management", "Emergency management, planning, leadership and exercises",
                   "Emergency management"),
}


def key_of(code):
    """The key name of a course number: "IS-100.c" -> "is100c", "IS-246.25" -> "is246_25", "IS-1300.a" ->
    "is1300a"."""
    name = code.lower().replace("-", "")
    name = re.sub(r"(\d)\.(\d)", r"\1_\2", name)
    return name.replace(".", "")


def C(code, title, date, hours, via, folder, theme, teaches, **more):
    """One course: its number and title as EMI gives them, its course date (the "Course Date" of its page,
    "YYYY-MM-DD"), its length in hours, how it is read (via: "sm" the Student Manual PDF, "web" the newer lesson's
    courseStructure.js, "old" the older lesson's screens, "link" not built), its emilms.fema.gov folder, its theme
    (THEMES), what it teaches in plain words, and more: zip and member (the complete-course zip and the regular
    expression of its Student Manual), pdf (the Student Manual's own address), note (said in the notice), why (for a
    link-only course: the reason), link (the address a link-only course points to)."""
    return dict(code=code, title=title, date=date, hours=hours, via=via, folder=folder, theme=theme, teaches=teaches,
                name=key_of(code), **more)


# Why two active shooter courses are links only.
STORYLINE = ("Its lesson is made of interactive animations (Articulate Storyline) shown from another server, with "
             "no readable text in the lesson file (checked 2026-11-23); take it online. The CISA active shooter "
             "pages are in the library (ready:cisa_active_shooter), and the older IS-907 is built here.")

COURSES = [
    # ------------------------------------------------------------------ incident command, NIMS and frameworks
    C("IS-100.c", "Introduction to the Incident Command System, ICS 100", "2018-06-25", 2, "sm", "is_0100-c", "ics",
      "The Incident Command System (ICS): its history, features and principles, how an incident organisation is "
      "built, and how ICS fits in the National Incident Management System (NIMS). The first ICS course.",
      zip=COURSE_FILES + "is-100.c/English/IS-0100c_complete-course.zip", member=r"(^|/)IS0100c_SM\.pdf$"),
    C("IS-200.c", "Basic Incident Command System for Initial Response, ICS-200", "2019-03-11", 4, "sm", "_is_0200c",
      "ics", "ICS for people who may supervise in the first hours of an incident: leadership and management, "
      "delegating authority, functional areas and positions, briefings, organisational flexibility and transfer of "
      "command.", zip=COURSE_FILES + "is-200.c/English/IS-200c-complete-course.zip", member=r"(^|/)[^/]*SM[^/]*\.pdf$"),
    C("IS-201.a", "Forms Used for the Development of the Incident Action Plan and Incident Management", "2024-05-17",
      3.8, "web", "is_0201a", "ics",
      "FEMA's standard ICS forms and how they are filled in at each step of the incident action planning process."),
    C("IS-700.b", "An Introduction to the National Incident Management System", "2018-06-25", 3.5, "sm", "_is0700b",
      "ics", "The National Incident Management System (NIMS): how all levels of government, voluntary groups and "
      "businesses work together in an incident; resource management, command and coordination, and communications "
      "and information management.", pdf=COURSE_FILES + "is-700.b/Student%20Manual/SMIS0700b.pdf"),
    C("IS-703.b", "National Incident Management System Resource Management", "2020-05-04", 3.5, "old", "is_0703b",
      "ics", "NIMS resource management: identifying, typing, ordering, tracking, mobilising and demobilising the "
      "people, teams, equipment and supplies an incident needs."),
    C("IS-706", "NIMS Intrastate Mutual Aid - An Introduction", "2013-10-31", 2.5, "web", "is_0706", "ics",
      "Mutual aid within a state: why it matters, what NIMS says about it, and how to write mutual aid agreements "
      "and operational plans."),
    C("IS-800.d", "National Response Framework, An Introduction", "2020-05-06", 3, "link", "", "ics",
      "The National Response Framework: how the whole nation responds to disasters and emergencies, its core "
      "capabilities and the Emergency Support Functions.",
      link="https://www.fema.gov/emergency-managers/national-preparedness/frameworks/response",
      why="EMI has taken its online lesson down and asks students to read the National Response Framework itself "
          "before the exam; that document is on www.fema.gov, which refuses programs (403, checked 2026-11-23). "
          "The exam is still offered."),
    C("IS-802.a", "Emergency Support Function (ESF) #2 - Communications", "2024-04-01", 1.25, "web", "is_0802a", "ics",
      "Emergency Support Function 2, Communications: how government and industry restore communications networks "
      "and services after a disaster and support the response with communications."),
    C("IS-951", "DHS Radio Interoperability", "2016-09-22", 2, "old", "is_0951", "ics",
      "How portable and mobile radios and radio systems work, and the principles of interoperable communications "
      "(different agencies talking to each other) within NIMS."),
    C("IS-995", "ICS Position Foundations", "2026-05-05", 16, "web", "is_0995", "ics",
      "The duties, responsibilities and abilities of each position in an ICS organisation, through guided "
      "activities with the ICS Training Reference Guide (fema:ics_training_reference_guide)."),
    C("IS-2000", "National Preparedness Goal and System Overview", "2018-03-26", 2, "old", "is_2000", "ics",
      "The National Preparedness Goal, its core capabilities for the five mission areas (prevention, protection, "
      "mitigation, response and recovery), and the National Preparedness System."),
    C("IS-2200", "Basic Emergency Operations Center Functions", "2019-05-17", 4, "web", "is_2200", "ics",
      "The emergency operations center (EOC): its role, design, staffing and functions, and how it supports the "
      "people at the incident."),
    C("IS-2500", "National Prevention Framework, an Introduction", "2018-03-27", 2, "web", "is_2500", "ics",
      "The National Prevention Framework: how governments, businesses, voluntary groups and people prevent, avoid "
      "or stop a threatened or actual act of terrorism."),
    C("IS-2600", "National Protection Framework, An Introduction", "2018-03-27", 3, "old", "is_2600", "ics",
      "The National Protection Framework: how the whole community safeguards against terrorism, natural disasters "
      "and other threats."),
    C("IS-2700", "National Mitigation Framework, an Introduction", "2018-03-27", 3, "old", "is_2700", "ics",
      "The National Mitigation Framework: how the nation reduces the loss of life and property from disasters and "
      "builds resilience."),
    C("IS-2901", "Introduction to Community Lifelines", "2025-08-05", 1, "web", "is_2901", "ics",
      "The eight Community Lifelines (such as safety and security, food, water and shelter, health, energy and "
      "communications) and how they guide priorities and decisions to stabilise an incident."),
    # ------------------------------------------------------------------ hazards, floods and mitigation
    C("IS-5.a", "An Introduction to Hazardous Materials", "2013-10-31", 10, "old", "IS-0005a", "hazards",
      "Hazardous materials: the health and environmental laws, the identification systems (placards, labels and "
      "shipping papers), recognising hazardous materials, their effects on health, and preparing a community for "
      "an incident. An introduction only: it does not meet the HAZWOPER responder training requirement."),
    C("IS-30.b", "Mitigation eGrants System for the Subgrant Applicant", "2018-01-10", 3, "old", "is_0030b",
      "hazards", "How a subapplicant uses FEMA's eGrants computer system to apply for hazard mitigation grants."),
    C("IS-31.b", "Mitigation eGrants System for the Applicant", "2018-01-10", 5.25, "old", "is_0031b", "hazards",
      "How a state, tribe or territory uses FEMA's eGrants system to review subapplications and apply for hazard "
      "mitigation grants."),
    C("IS-66", "Preparing the Nation for Space Weather Events", "2022-09-19", 2, "web", "is_0066", "hazards",
      "Space weather (solar storms): what happens, what it can do to power grids, satellites, radio and GPS, and how "
      "federal agencies and local emergency managers prepare for it."),
    C("IS-212.b", "Introduction to Unified Hazard Mitigation Assistance (HMA)", "2015-12-07", 3, "old", "is_0212b",
      "hazards", "FEMA's Hazard Mitigation Assistance grant programmes and how to prepare good mitigation planning "
      "and project applications for them."),
    C("IS-271.a", "Anticipating Hazardous Weather & Community Risk, 2nd Edition", "2013-10-31", None, "link", "",
      "hazards", "Weather hazards and how emergency managers use forecasts and warnings to judge community risk.",
      link=OVERVIEW.format(code="IS-271.a"),
      why="EMI has withdrawn it for review (\"Temporarily Unavailable\", checked 2026-11-23); no lesson or course "
          "materials are online. The NWS weather safety pages are in the library (prep:nws_safety)."),
    C("IS-273", "How to Read a Flood Insurance Rate Map (FIRM)", "2020-03-10", 2.5, "old", "is_0273", "hazards",
      "Flood Insurance Rate Maps: the kinds of flood maps, what each part of a map means, and how to use one to "
      "find a property's flood risk."),
    C("IS-274", "How to Use a Flood Insurance Study (FIS)", "2020-03-10", 1.6, "old", "is_0274", "hazards",
      "Flood Insurance Studies: finding and using one to learn a property's flood risk, so it can be protected or "
      "insured."),
    C("IS-284.a", "Using the Substantial Damage Estimator 3.0 Tool", "2025-09-16", 3, "web", "is_0284a", "hazards",
      "FEMA's Substantial Damage Estimator 3.0 software: filling in its forms, saving structure and community "
      "data, running its reports and exporting data."),
    C("IS-285", "Substantial Damage Estimation for Floodplain Administrators", "2025-12-29", 8, "web", "is_0285",
      "hazards", "How local officials decide whether flood-damaged buildings are \"substantially damaged\" under the "
      "National Flood Insurance Program, using the Substantial Damage Estimator."),
    C("IS-318.b", "Local Mitigation Planning Training", "2026-02-12", 3.1, "web", "is_0318b", "hazards",
      "What a local hazard mitigation plan must contain, according to FEMA's Local Mitigation Planning Policy Guide "
      "(2022) and 44 CFR Part 201."),
    C("IS-324.a", "Community Hurricane Preparedness", "2013-10-31", 10, "link", "", "hazards",
      "How hurricanes form, the hazards they bring, how the National Weather Service forecasts them, and the tools "
      "emergency managers use to prepare their communities.",
      link="https://www.meted.ucar.edu/hurrican/chp/",
      why="EMI's page says the course is on a non-federal website run by COMET (University Corporation for "
          "Atmospheric Research), whose material carries its own copyright: link-only (open it in a browser). The "
          "NWS hurricane safety pages are in the library (prep:nws_safety)."),
    C("IS-328.a", "Plan Review for Local Mitigation Plans", "2026-02-12", 3, "web", "is_0328a", "hazards",
      "How plan reviewers check a local hazard mitigation plan against the Local Mitigation Planning Policy Guide."),
    C("IS-393.b", "Introduction to Hazard Mitigation", "2017-06-15", 1.5, "old", "is_0393b", "hazards",
      "Hazard mitigation (lasting action that reduces the risk from hazards) for newcomers: why it matters, "
      "mitigation planning and the kinds of mitigation actions."),
    C("IS-815", "ABCs of Temporary Emergency Power", "2016-12-27", 2, "old", "IS0815", "hazards",
      "Temporary emergency power for critical facilities (hospitals, water plants, shelters) after the power grid "
      "fails: assessing needs, generators and planning."),
    C("IS-2101", "Cooperating Technical Partners (CTP) 101 Beginner Training Course", "2017-12-28", 2, "old",
      "is_2101", "hazards", "FEMA's Cooperating Technical Partners programme, in which communities and states help "
      "make flood maps: its mission, activities, funding and tools."),
    # ------------------------------------------------------------------ community, schools, animals, people's needs
    C("IS-10.a", "Animals in Disasters: Awareness and Preparedness", "2015-10-02", 4, "web", "is_0010a", "community",
      "Animals in disasters for owners, carers and animal businesses: the hazards, how incidents are managed, and "
      "how to prepare pets, livestock and other animals."),
    C("IS-11.a", "Animals in Disasters: Community Planning", "2015-10-02", 4, "web", "is_0011a", "community",
      "How a community writes a plan to care for animals, their owners and animal businesses in disasters."),
    C("IS-36.a", "Preparedness for Child Care Providers", "2021-10-01", 2, "old", "is_0036a", "community",
      "How child care providers find, assess and plan for the hazards at their child care site."),
    C("IS-111.a", "Livestock in Disasters", "2013-10-31", 4, "web", "is_0111a", "community",
      "Livestock producers and emergency managers working together to reduce the effect of disasters on farm "
      "animals and animal agriculture."),
    C("IS-315.a", "CERT and the Incident Command System (ICS)", "2020-05-01", 2, "web", "is_0315a", "community",
      "How Community Emergency Response Teams (CERT) use the Incident Command System to keep volunteers safe and "
      "organised."),
    C("IS-317.a", "Introduction to Community Emergency Response Team (CERTs)", "2020-05-01", 2, "web", "is_0317a",
      "community", "The CERT programme: what CERT volunteers do and how to become involved; also a first step "
      "before CERT Basic Training (its participant manual is gpo:fema_cert_basic_training_2019)."),
    C("IS-360", "Preparing for Mass Casualty Incidents: A Guide for Schools, Higher Education, and Houses of Worship",
      "2013-06-24", 3, "old", "is_0360", "community",
      "How schools, colleges and houses of worship plan to prepare for, respond to and recover from incidents with "
      "many casualties."),
    C("IS-362.a", "Multi-Hazard Emergency Planning for Schools", "2013-10-31", 3, "old", "is_0362a", "community",
      "How a school writes, practises and keeps up its emergency operations plan."),
    C("IS-363", "Introduction to Emergency Management for Higher Education", "2018-12-18", 3, "web", "is_0363",
      "community", "Emergency management for colleges and universities: planning to protect lives, property and "
      "the campus."),
    C("IS-366.a", "Planning for the Needs of Children in Disasters", "2015-12-09", 6, "web", "is_0366a", "community",
      "Children's particular needs in disasters and how emergency managers and children's programmes plan for "
      "them in mitigation, preparedness, response and recovery."),
    C("IS-505", "Concepts of Religious Literacy for Emergency Management", "2016-03-04", 4, "web",
      "is_0505.2026.2.11", "community", "Working respectfully with religious and faith-based communities before, "
      "during and after disasters: religious literacy and partnership."),
    C("IS-650.b", "Building Partnerships with Tribal Governments", "2018-11-02", 2, "old", "is_0650b", "community",
      "Tribal governments in the United States, their history with the federal government, and how to build "
      "working relationships with them for emergency management."),
    C("IS-904", "Active Shooter Prevention: You Can Make a Difference", "2021-09-02", 1, "link", "is_0904",
      "community", "What you can do at work to lower the likelihood of an active shooter incident: recognising "
      "warning signs and reporting concerns.", link=OVERVIEW.format(code="IS-904"),
      why="Its first screen says \"This training includes copyrighted content used with permission or by right, and "
          "may not be used commercially\" (a Georgia Southern University video among it), and most of its screens "
          "are videos and animations (checked 2026-11-23): link-only, take it online. The CISA active shooter pages "
          "are in the library (ready:cisa_active_shooter)."),
    C("IS-905", "Responding to an Active Shooter: You Can Make a Difference", "2022-12-14", 1, "link", "is_0905",
      "community", "How to respond if an active shooter or targeted attack happens where you are, and how to help "
      "afterwards.", link=OVERVIEW.format(code="IS-905"), why=STORYLINE),
    C("IS-907", "Active Shooter: What You Can Do (IS-907.A, retired)", "", 1, "web", "is_0907a",
      "community", "The older active shooter course for everyone: run, hide, fight; what to do when police arrive; "
      "and preparing a workplace. Retired by EMI without a replacement; IS-904, IS-905 and IS-917 are the current "
      "courses.", note="EMI has retired this course without a replacement, so its exam is no longer offered; its "
      "lesson is still published on emilms.fema.gov (files dated 2025-05-07). The current courses are IS-904, "
      "IS-905 and IS-917."),
    C("IS-909", "Community Preparedness: Implementing Simple Activities for Everyone", "2013-10-31", 1, "old",
      "is_0909", "community", "A model programme for teaching community preparedness: choosing topics, planning "
      "the sessions in six steps, and getting feedback."),
    C("IS-917", "Active Shooter Leadership", "2025-09-09", 1, "link", "is_0917", "community",
      "How organisational leaders lead whole-community efforts to prevent, respond to and recover from an active "
      "shooter or targeted violence event.", link=OVERVIEW.format(code="IS-917"), why=STORYLINE),
    C("IS-1150", "DHS Human Trafficking Awareness for FEMA Employees", "2016-09-14", 0.5, "old", "is_1150",
      "community", "What human trafficking is (and how it differs from smuggling), how disaster workers may meet "
      "it, and how to report it."),
    C("IS-1151", "Blue Campaign Disaster Responder Training", "2021-11-17", 0.3, "old", "is_1151", "community",
      "A short Blue Campaign lesson for disaster responders on recognising and reporting suspected human "
      "trafficking."),
    C("IS-1152", "Blue Campaign First Responder Training", "2021-11-17", 1, "old", "is_1152", "community",
      "The Blue Campaign's lessons for first responders: what human trafficking is, who can become a victim, and "
      "how to identify and respond to suspected victims."),
    # ------------------------------------------------------------------ mass care, logistics and volunteers
    C("IS-26", "Guide to Points of Distribution", "2010-08-11", 4, "web", "is_0026", "mass_care",
      "Points of distribution (PODs), where people collect water, food and supplies after a disaster: planning, "
      "staffing, running and closing them, safety and equipment."),
    C("IS-27", "Orientation to FEMA Logistics", "2013-10-31", 4, "old", "is_0027", "mass_care",
      "FEMA's field logistics: its functions, roles and responsibilities from a disaster declaration to closing "
      "the field offices."),
    C("IS-52", "Introduction to Disaster Logistics and Supply Chain Management", "2026-07-30", 4, "web", "is-0052",
      "mass_care", "Disaster logistics and supply chains: terms, supply chain parts, risks, resilience, governance "
      "and technology."),
    C("IS-102.c", "Preparing for Federal Disaster Operations: FEMA Response Partners", "2013-10-31", 1, "web",
      "is_0102c", "mass_care", "Practical tips for response partners deploying to a disaster with FEMA."),
    C("IS-238", "Critical Concepts of Supply Chain Flow and Resilience", "2022-06-08", 2, "web", "is_0238",
      "mass_care", "Lessons of the 2017 hurricanes about local supply chains after disasters, and how public and "
      "private partners share information to keep goods flowing."),
    C("IS-244.b", "Developing and Managing Volunteers", "2013-03-29", 4, "web", "is_0244b", "mass_care",
      "Finding, recruiting, assigning, training, supervising and motivating volunteers in disasters, spontaneous "
      "volunteers included."),
    C("IS-245.c", "Introduction to the Federal Priorities and Allocations System", "2024-08-09", 1, "web", "is_0245c",
      "mass_care", "The Federal Priorities and Allocations System (FPAS), a rule that gives priority to contracts "
      "for critical goods and services, and how it supports FEMA's mission."),
    C("IS-246.25", "Implementing the Federal Priorities and Allocations System (FPAS)", "2025-01-23", 3, "web",
      "is_00246.25", "mass_care", "How FEMA staff use FPAS priority ratings: placing rated orders, roles and "
      "solving problems."),
    C("IS-288.a", "The Role of Voluntary Organizations in Emergency Management", "2015-02-12", 1, "web", "is_0288a",
      "mass_care", "The history, roles and services of voluntary disaster relief agencies."),
    C("IS-289", "Voluntary Agency Liaison (VAL) Overview", "2021-06-02", 2.5, "web", "is_0289", "mass_care",
      "FEMA's Voluntary Agency Liaisons: what they do and how they help voluntary, faith-based and community groups "
      "meet survivors' needs."),
    C("IS-403.a", "Introduction to Individual Assistance (IA)", "2025-05-29", 1, "web", "is_0403a", "mass_care",
      "FEMA's Individual Assistance programme, which helps people and households recover after a disaster."),
    C("IS-405.a", "Mass Care/Emergency Assistance Overview", "2025-12-17", 1, "web", "is_0405a", "mass_care",
      "Mass care and emergency assistance (sheltering, feeding, distributing supplies, reuniting families) and how "
      "government, voluntary groups and businesses work together on it."),
    C("IS-406", "Operating a Shelter", "2023-10-02", 5, "web", "is_0406", "mass_care",
      "Managing a congregate shelter: opening, staffing, running and closing it, with best practices."),
    # ------------------------------------------------------------------ damage assessment, recovery, Public Assistance
    C("IS-559", "Local Damage Assessment", "2013-10-31", 2, "old", "is_0559", "recovery",
      "Planning a damage assessment programme and doing quick, effective damage assessments after a disaster."),
    C("IS-713", "Essentials of Procurement Under Grants and Build America, Buy America", "2026-09-01", 3, "web",
      "is_0713", "recovery", "The federal procurement rules (2 CFR 200.317 to 327) for FEMA grant recipients: "
      "methods, thresholds, contract terms, fraud prevention and Build America, Buy America."),
    C("IS-715", "Procurement Under Grants: Exigency and Emergency Circumstances", "2026-09-01", 1, "web", "is_0715",
      "recovery", "Federal procurement rules in emergencies: sole-sourcing, using existing contracts, and the "
      "documentation needed."),
    C("IS-1000", "Public Assistance Program and Eligibility", "2019-02-28", 8, "old", "is_1000", "recovery",
      "FEMA's Public Assistance programme, which helps governments and some nonprofits repair public facilities "
      "after disasters: who and what is eligible."),
    C("IS-1002", "FEMA Grants Portal - Transparency at Every Step", "2019-02-28", 7, "old", "is_1002", "recovery",
      "Using the Grants Portal software for Public Assistance."),
    C("IS-1004", "The FEMA Site Inspection Process", "2019-02-28", 4, "old", "is_1004", "recovery",
      "Preparing for and taking part in a Public Assistance site inspection of disaster damage."),
    C("IS-1006", "Documenting Disaster Damage and Developing Project Files", "2019-02-28", 8, "old", "IS1006",
      "recovery", "Documenting disaster damage, the scope of work and costs, and organising project files for "
      "Public Assistance."),
    C("IS-1007", "Detailed Damage Description and Dimensions", "2019-02-28", 5, "old", "is_1007", "recovery",
      "Writing the Damage Description and Dimensions of a Public Assistance project."),
    C("IS-1008", "Scope of Work Development (Scoping and Costing)", "2019-02-28", 5, "old", "is_1008", "recovery",
      "Developing and reviewing a Public Assistance scope of work and cost estimate."),
    C("IS-1009", "Conditions of the Public Assistance Grant", "2019-02-28", 7, "web", "is_1009", "recovery",
      "The conditions a Public Assistance grant comes with, and how to comply with them."),
    C("IS-1010", "Emergency Protective Measures", "2019-02-28", 3, "old", "is_1010", "recovery",
      "Documenting the costs of emergency protective measures (overtime, equipment and materials) for Public "
      "Assistance."),
    C("IS-1011", "Roads and Culverts", "2019-02-28", 4, "old", "is_1011", "recovery",
      "Telling disaster damage to roads and culverts from ordinary maintenance, and the rules for Public "
      "Assistance grants for them."),
    C("IS-1013", "Costing - Estimates and the Cost Estimating Format", "2019-02-28", 6, "old", "is_1013", "recovery",
      "Cost estimates for Public Assistance projects and FEMA's Cost Estimating Format."),
    C("IS-1014", "Integrating 406 Mitigation Considerations into Your Public Assistance Grant", "2019-02-28", 3.25,
      "old", "is_1014", "recovery", "Adding hazard mitigation (Section 406 of the Stafford Act) to repairs paid for "
      "by Public Assistance."),
    C("IS-1015", "Insurance Considerations, Compliance, and Requirements", "2019-02-28", 3.25, "old", "is_1015",
      "recovery", "How insurance affects Public Assistance funding, and the insurance requirements that follow."),
    C("IS-1017", "Scope Change Requests, Time Extensions, Improved/Alternate Project Requests", "2019-02-28", 2.5,
      "old", "IS1017", "recovery", "Changing an approved Public Assistance project: scope changes, time extensions "
      "and improved or alternate projects."),
    C("IS-1021", "Bridge Damage Considerations", "2019-02-28", 3, "old", "is_1021", "recovery",
      "Public Assistance rules for disaster damage to bridges."),
    C("IS-1023", "Electrical Systems Considerations", "2019-02-28", 3, "old", "is_1023", "recovery",
      "Public Assistance rules for disaster damage to electrical systems."),
    C("IS-1024", "Water and Wastewater Treatment System Considerations", "2019-02-28", 3, "web", "is_1024",
      "recovery", "Public Assistance rules for disaster damage to water and wastewater treatment systems."),
    C("IS-2900.a", "National Disaster Recovery Framework (NDRF) Overview", "2018-07-11", 3, "web", "is_2900a",
      "recovery", "The National Disaster Recovery Framework: how communities, states and the federal government "
      "work together on recovery, and its recovery support functions."),
    C("IS-2905", "Coordinating Health and Social Services Recovery", "2020-03-10", 3, "old", "is_2905", "recovery",
      "The Health and Social Services Recovery Support Function: restoring health care, social services and "
      "people's well-being after a disaster."),
    # ------------------------------------------------------------------ emergency management, planning, leadership
    C("IS-13", "NDEMU Conduct and Behavior", "2024-04-26", 0.5, "web", "is_0013", "management",
      "The conduct rules for students and instructors at FEMA's National Disaster and Emergency Management "
      "University (formerly EMI) courses."),
    C("IS-15.b", "Special Events Contingency Planning for Public Safety Agencies", "2013-10-31", 4, "web", "is_0015b",
      "management", "Planning for public safety at special events (fairs, concerts, parades): the planning team, "
      "hazard analysis and responding to incidents during the event."),
    C("IS-29.a", "Public Information Officer Awareness", "2019-08-05", 7, "old", "is_0029a", "management",
      "The role of the Public Information Officer (PIO), who gives the public and the media information in an "
      "emergency."),
    C("IS-42.a", "Social Media in Emergency Management", "2021-08-24", 3, "web", "is_0042a", "management",
      "Using social media in emergency management: tools, techniques and a plan for building the capability."),
    C("IS-45", "Continuous Improvement (CI) Overview", "2020-07-13", 1, "old", "is_0045", "management",
      "Continuous improvement in emergency management: the process, ways to collect data, and building a "
      "programme."),
    C("IS-75", "Military Resources in Emergency Management", "2011-02-25", 2, "web", "is_0075", "management",
      "The US military resources that can help civilian authorities in disasters, and how to request and work with "
      "them."),
    C("IS-120.c", "An Introduction to Exercises", "2018-02-12", 3, "web", "is_0120c", "management",
      "Emergency management exercises (drills, tabletop and full-scale exercises): the basics, and the Homeland "
      "Security Exercise and Evaluation Program (HSEEP)."),
    C("IS-130.a", "How to be an Exercise Evaluator", "2018-02-12", 2.75, "web", "is_0130a", "management",
      "Evaluating emergency management exercises and planning improvements afterwards, as HSEEP describes."),
    C("IS-144.a", "TERT Basic Course", "2021-06-03", 3, "web", "is_0144a", "management",
      "For 911 call takers and dispatchers deploying to another emergency communications centre in a disaster "
      "(Telecommunicator Emergency Response Teams): what to expect."),
    C("IS-230.e", "Fundamentals of Emergency Management", "2021-06-15", 6, "web", "is_0230e", "management",
      "An overview of FEMA and emergency management: the basic ideas, the partners and how FEMA meets its "
      "mission."),
    C("IS-235.c", "Emergency Planning", "2015-12-15", 5, "web", "is_0235c", "management",
      "The emergency planning process and how to take part in writing an all-hazards emergency operations plan."),
    C("IS-236", "Introduction to Deliberate Planning", "2025-03-20", 4.5, "web", "is_0236", "management",
      "Deliberate (advance) planning, for members of a planning team who bring their own subject knowledge."),
    C("IS-240.c", "Leadership and Influence", "2021-08-13", 3, "web", "is_0240c", "management",
      "Leadership in emergency management: leading from within, facilitating change, building trust, influence and "
      "developing leaders."),
    C("IS-241.c", "Decision Making and Problem Solving", "2021-08-13", 2, "web", "is_0241c", "management",
      "Making decisions and solving problems in emergencies, alone and in groups."),
    C("IS-242.c", "Effective Communication", "2021-08-13", 8, "old", "is_0242c", "management",
      "Communication skills for emergency management: basic skills, communicating in an emergency, community "
      "issues, technology and oral presentations."),
    C("IS-247.c", "Integrated Public Alert and Warning System (IPAWS) for Alert Originators", "2024-06-03", 2, "web",
      "is_0247c", "management", "IPAWS, the system behind Wireless Emergency Alerts and the Emergency Alert System, "
      "and how to write effective and accessible alert and warning messages."),
    C("IS-251.b", "Integrated Public Alert and Warning System (IPAWS) for Alerting Administrators", "2024-07-25",
      1.5, "web", "is_0251b", "management", "Running an IPAWS alerting authority: policies, approval process, "
      "training, exercises and best practices."),
    C("IS-293", "Mission Assignment Overview", "2021-02-24", 3, "web", "is_0293", "management",
      "How FEMA tasks other federal agencies in a disaster (Mission Assignments): from the request for federal "
      "assistance to billing and closing."),
    C("IS-453", "Introduction to Homeland Security Planning", "2013-10-31", 2, "old", "is_0453", "management",
      "An overview of homeland security planning for staff who may or may not plan as part of their job."),
    C("IS-545.a", "Reconstitution Planning Course", "2024-02-13", 5, "web", "is_0545a", "management",
      "Continuity of operations: planning how an organisation returns to normal operations (reconstitution) after "
      "an emergency."),
    C("IS-822", "Fundamentals of Management and Support Coordination of Federal Disaster Operations", "2013-11-27",
      4, "old", "is_822", "management", "The basics of FEMA's disaster operations for federal staff in incident "
      "management or support roles."),
    C("IS-908", "Emergency Management for Senior Officials", "2013-10-31", 1, "old", "is_0908", "management",
      "The role of elected and senior officials in emergency management, and simple steps to prepare."),
    C("IS-922.a", "Applications of GIS for Emergency Management", "2021-07-06", 3, "web", "is_0922a", "management",
      "Geographic information systems (GIS, computer mapping) in emergency management: the basics, history, uses "
      "and tools."),
    C("IS-1173.a", "Identify and Assess Risk, Develop and Implement a Risk Management Strategy and Measure "
      "Performance", "2025-03-14", 1.5, "web", "is_1173a", "management",
      "The last four steps of the Interagency Security Committee's risk management process for federal buildings, "
      "and its levels of protection."),
    C("IS-1200", "TERT Team Leader Course", "2016-12-02", 4, "old", "is_1200", "management",
      "For supervisors of Telecommunicator Emergency Response Teams (911 staff deploying to a disaster)."),
    C("IS-1300.a", "Introduction to Continuity", "2024-06-04", 1, "web", "is_1300_a", "management",
      "Continuity: keeping an organisation's essential functions going during and after an emergency."),
    C("IS-2002", "Introduction to FEMA Operational Planning", "2018-06-08", 4, "web", "is_2002", "management",
      "How FEMA does operational planning, and how it coordinates with state, local and tribal planners."),
]
BY_NAME = {c["name"]: c for c in COURSES}
BUILT = [c for c in COURSES if c["via"] != "link"]

# The two reference documents (official PDFs on training.fema.gov, read whole by build_textbooks.pdfdoc_book).
DOCS = [
    K.us_pdf(GROUP, name="nims_2017", title="National Incident Management System, Third Edition (FEMA, October "
             "2017)", subject="Incident command and NIMS", publisher="Federal Emergency Management Agency (FEMA), US "
             "Department of Homeland Security",
             pdf=COURSE_FILES + "is-700.b/Handouts/National_Incident_Management%20System_Third%20Edition_October_"
             "2017.pdf", page=OVERVIEW.format(code="IS-700.b").replace("courseoverview", "courseMaterials"),
             published="2017-10", version="Third Edition, October 2017 (handout of IS-700.b)",
             description="The National Incident Management System itself, the doctrine taught in IS-700.b: its "
             "fundamentals and concepts, resource management, command and coordination (the Incident Command "
             "System, emergency operations centres, multiagency coordination groups and the Joint Information "
             "System), and communications and information management, with its glossary.",
             notice="A work of FEMA, part of the US government (public domain), read from the course materials of "
             "IS-700.b on training.fema.gov. " + TRAINING_NOTE),
    K.us_pdf(GROUP, name="ics_training_reference_guide", title="ICS Position Training Reference Guide (FEMA, IS-995)",
             subject="Incident command and NIMS", publisher=PUBLISHER,
             pdf="https://training.fema.gov/emiweb/is/icsresource/assets/ics_training_reference_guide.pdf",
             page=OVERVIEW.format(code="IS-995"), version="as published with IS-995 (course date 2026-05-05)",
             description="The reference guide used in IS-995, ICS Position Foundations: for each position of an "
             "Incident Command System organisation, its duties, responsibilities and what it does in each step of "
             "the incident.",
             notice="A work of FEMA, part of the US government (public domain), read from training.fema.gov. "
             + TRAINING_NOTE),
]

# The related books already in the library, linked from the index (their keys are checked by the self-tests).
RELATED = [
    ("prep:fema_are_you_ready", "Are You Ready? An In-depth Guide to Citizen Preparedness (FEMA IS-22, 2004)",
     "FEMA's long guide to preparing for every kind of disaster; it was once the IS-22 course book."),
    ("gpo:fema_are_you_ready_2020", "Are You Ready? (FEMA P-2064, 2020)", "The newer, shorter edition."),
    ("gpo:fema_cert_basic_training_2019", "CERT Basic Training: Participant Manual (FEMA, 2019)",
     "The classroom course that IS-317.a introduces."),
    ("gpo:fema_take_control_older_adults_2023", "Take Control in 1, 2, 3 (FEMA, 2023)",
     "Disaster preparedness for older adults."),
    ("gpo:fema_alerts_and_warnings_2021", "A Guide for Alerts and Warnings (FEMA, 2021)",
     "The alerts the public receives, which IS-247.c and IS-251.b teach officials to send."),
    ("ready:ready_gov", "Ready.gov (FEMA)", "Plans, kits and every hazard, for people and families."),
    ("ready:cisa_active_shooter", "Active shooter preparedness: Run, Hide, Fight (CISA)",
     "The public pages that go with IS-904, IS-905 and IS-917."),
    ("prep:nws_safety", "Weather safety (National Weather Service)", "Hurricanes, tornadoes, floods, winter weather "
     "and more."),
]


# ---------------------------------------------------------------------- reading the web lessons

def _norm(text):
    """Text for comparing: the words of a bit of HTML, lower case, on one line."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text or "")).replace("\xa0", " ").split()).lower()


def _clean(fragment, base="", layout=False):
    """A bit of lesson HTML made plain: script links (pop-up windows) dropped with their words, layout tables taken
    apart (layout=True: the older player builds every screen of tables), and only plain structure kept
    (build_textbooks._Cleaner: headings, paragraphs, lists, tables, links and "Picture: " with each picture's
    description)."""
    import build_textbooks as B
    fragment = re.sub(r"<a\b[^>]*href=\"javascript:[^\"]*\"[^>]*>.*?</a>", "", fragment or "", flags=re.S | re.I)
    fragment = re.sub(r"<a\b[^>]*href=\"#[^\"]*\"[^>]*>\s*click this link.*?</a>", "", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<a\b[^>]*href=\"#[^\"]*\"[^>]*>(.*?)</a>", r"<p>\1</p>", fragment, flags=re.S | re.I)
    if layout:
        fragment = re.sub(r"</?(table|tbody|thead|tr|td|th)\b[^>]*>", " ", fragment, flags=re.I)
    fragment = re.sub(r"<img\b[^>]*\balt=\"\s*(%s)\s*\"[^>]*>" % DECORATIVE, "", fragment, flags=re.I)
    out = B._Cleaner({}, base).clean(fragment)
    out = re.sub(r"</?(div|span|section)\b[^>]*>", " ", out)       # the player's layout boxes
    out = re.sub(r' id="[^"]*"', "", out)
    out = re.sub(r"<(p|li|h3|strong|em|b|i)>\s*</\1>", "", out)
    return re.sub(r"\s*\n\s*", "\n", re.sub(r"[ \t]+", " ", out)).strip()


# Pictures that are only buttons or decoration in the lesson player (their descriptions are left out).
DECORATIVE = r"print|printer|clock|icon|image|picture|spacer|empty space|blank|line|arrow|next|back|button|bullet"


def _is_html(text):
    """True when a value looks like HTML (has tags)."""
    return bool(re.search(r"<[a-zA-Z][^>]*>", text or ""))


def _filtered(filters, lang="en-US"):
    """True when an item with these "publish filters" (tags such as Instructor Guide, Student Guide, Visuals, IS) is
    not shown in the web lesson, as the lesson player decides when it is opened without a filter in its address
    (the way EMI's course pages open it). The older player (its filters have no "type") shows only untagged items;
    the newer one (typed filters) shows every item, except, when the course names no language, items tagged for a
    language (type 2)."""
    if not filters:
        return False
    if not any(isinstance(f, dict) and "type" in f for f in filters):
        return True
    return not lang and any(isinstance(f, dict) and f.get("type") == 2 for f in filters)


def _hidden(element, lang="en-US"):
    """True when a lesson element is not shown in the web lesson: filtered out (_filtered), switched off, or hidden
    at every screen size."""
    if _filtered(element.get("publish_filters"), lang) or element.get("active") is False:
        return True
    params = element.get("parameters")
    layout = (((params or {}).get("responsive") or {}).get("layout") or {}) if isinstance(params, dict) else {}
    sizes = [v for v in layout.values() if isinstance(v, dict)]
    return bool(sizes) and all(v.get("hidden") for v in sizes)


def _correct(element):
    """True when a question's option is marked as the right answer."""
    params = element.get("parameters")
    return isinstance(params, dict) and bool((params.get("config") or {}).get("correct"))


# Element kinds that hold no lesson words of their own (buttons, spacers, drawings, answer boxes, embedded
# animations): only what is inside them is read.
NO_WORDS = {"btn", "spacer", "placeholder", "svg", "input", "textbox", "html", "icon", "progress", "panelFooter",
            "panelHeader", "jumbotron", "list", "panel", "timeline", "tabset", "contentCarousel", "flipCardSet",
            "flipCardSetCard"}
# Words that only name a part of the player ("Option1", "New Button", "Knowledge Check 2").
PLACEHOLDER = re.compile(r"(option\s*\d*|new button|panel footer|lesson list|rich text|placeholder|image|video|audio|"
                         r"(knowledge check|question|review question)\s*#?\d*)", re.I)


def _words(e):
    """The words an element shows: its "meta" (HTML or text), else its "txt"; "" for a player placeholder."""
    for value in (e.get("meta") or "", e.get("txt") or ""):
        if _norm(value) and not PLACEHOLDER.fullmatch(_norm(value)):
            return _clean(value) if _is_html(value) else f"<p>{html.escape(' '.join(value.split()))}</p>"
    return ""


def element_parts(elements, lang="en-US"):
    """[HTML] of a list of lesson elements of a newer course (courseStructure.js), in order: rich text, tables, cards
    and speech bubbles, picture descriptions, videos and sounds by their description, and questions with their
    options (the right answers marked); elements inside others (call-outs, tabs, panels, timelines, scenarios) are
    read too."""
    out = []
    for e in elements or []:
        if _hidden(e, lang):
            continue
        kind = e.get("elementtype") or ""
        kids = [k for k in e.get("elements") or [] if not _hidden(k, lang)]
        if kind == "image":
            alt = " ".join((e.get("description") or e.get("txt") or e.get("asset_description") or "").split())
            if alt and not re.fullmatch(r"[\w .-]+\.(png|jpe?g|gif|svg)", alt, re.I) and \
                    not re.fullmatch(DECORATIVE, alt, re.I):
                out.append(f"<p>Picture: {html.escape(alt)}</p>")
        elif kind in ("video", "audio"):
            words = " ".join((e.get("txt") or "").split())
            if words and not PLACEHOLDER.fullmatch(words):
                out.append(f"<p>{'Video' if kind == 'video' else 'Sound'}: {html.escape(words)}</p>")
        elif kind == "videoembed":
            m = re.search(r'title="([^"]+)"', e.get("meta") or "")
            out.append(f"<p>Video (online only): {html.escape(m.group(1) if m else 'a video')}</p>")
        elif kind.endswith("Question"):
            stem = _words({"meta": e.get("txt") or "", "txt": e.get("meta") or ""})
            out.append("<p><strong>Knowledge check:</strong></p>" + stem)
            options = [k for k in kids if (k.get("elementtype") or "").endswith("Option") or
                       (k.get("elementtype") or "").startswith("matching")]
            items = []
            for k in options:
                words = re.sub(r"^<p>(.*)</p>$", r"\1", _words(k), flags=re.S)
                if words:
                    items.append(f"<li>{words}{' (correct answer)' if _correct(k) else ''}</li>")
            if items:
                out.append("<ul>" + "".join(items) + "</ul>")
            out += element_parts([k for k in kids if k not in options], lang)
            continue
        elif kind not in NO_WORDS:
            body = _words(e)
            if body:
                out.append(_block(body))
        out += element_parts(kids, lang)
    return out


def _block(body):
    """A part that starts with bare words put in a box of its own, so it does not run into the next part."""
    return body if re.match(r"\s*<(p|ul|ol|h\d|table|dl|blockquote|pre|div)\b", body) else f"<div>{body}</div>"


# Screens that only explain the online lesson player (its buttons and keys): not read.
PLAYER_HELP = re.compile(r"^(screen features|navigating using your keyboard|using the course player|course player|"
                         r"link to screen features description)\b", re.I)


def screen_title(text):
    """A screen's title without the player's marks ("Screen Features [Official]" -> "Screen Features") and
    invisible characters."""
    text = re.sub(r"[\u200b-\u200f\u2060\ufeff]", "", text or "")
    return re.sub(r"\s*\[official\]\s*$", "", " ".join(text.split()), flags=re.I)


def _dedupe(parts, title=""):
    """The parts without repeats (the same text for another screen size) and without a part that only repeats the
    screen's title."""
    seen, out = {_norm(title)}, []
    for p in parts:
        n = _norm(p)
        if n and n not in seen:
            seen.add(n)
            out.append(p)
    return out


def web_lessons(text):
    """[(lesson title, [(screen title, body HTML)])] of a newer course's courseStructure.js: every lesson and every
    screen the web lesson shows (_filtered decides, as the player does); screens titled "PRINT ONLY" (classroom
    discussions EMI marks for the printed guides) and the player's help screens are left out."""
    data = json.loads(text[text.index("{"): text.rindex("}") + 1])
    lang = (data.get("crslanguage") or "").strip()
    lessons = []
    for module in data.get("modules") or []:
        if _filtered(module.get("publish_filters"), lang):
            continue
        for obj in module.get("objects") or []:
            if _filtered(obj.get("publish_filters"), lang):
                continue
            screens = []
            for sub in obj.get("subeos") or []:
                page = sub.get("page") or {}
                title = screen_title(page.get("title") or sub.get("title"))
                if not page or _filtered(sub.get("publish_filters"), lang) or \
                        _filtered(page.get("publish_filters"), lang) or re.search(r"print\s*only", title, re.I) or \
                        PLAYER_HELP.search(title):
                    continue
                parts = []
                for group in page.get("groups") or []:
                    if not _filtered(group.get("publish_filters"), lang):
                        parts += element_parts(group.get("elements"), lang)
                parts = _dedupe(parts, title)
                if parts:
                    screens.append((title or "Screen", "".join(parts)))
            lesson = screen_title(obj.get("eodesc") or obj.get("title") or "Lesson")
            if screens:
                lessons.append((lesson, screens))
    return lessons


def old_plan(text, base):
    """[(lesson title, [(screen title, address)])] of an older course's table of contents (curriculum/1.html): its
    tree (de.addObject) lists every screen (type 11) in order under its lesson (type 2), and its urlMap gives each
    screen's page, in the same order. The final exam is left out."""
    line = next((ln for ln in text.splitlines() if ln.strip().startswith("de.addObject(")), "")
    if not line:
        return []
    line = line.strip()
    tree = json.loads(line[len("de.addObject("): line.rindex(")")])
    pages = dict((int(i), u) for i, u in re.findall(r"mapURL\[(\d+)\]\s*=\s*\"([^\"]+)\"", text))
    plan, count = [], [0]

    def walk(node, lesson):
        """Add the screens below node, in order."""
        kind = node.get("type")
        label = " ".join((node.get("label") or "").split())
        if kind == 2:
            lesson = label
        if kind == 11:
            number = count[0]
            count[0] += 1
            exam = re.search(r"final exam|showexam", label, re.I) or \
                any(k.get("contentType") == 18 for k in node.get("children") or [])
            if not exam and number in pages and not PLAYER_HELP.search(screen_title(label)):
                if not plan or plan[-1][0] != lesson:
                    plan.append((lesson, []))
                plan[-1][1].append((screen_title(label), base + re.sub(r"^\.\./", "", pages[number])))
            return
        for child in node.get("children") or []:
            walk(child, lesson)
    walk(tree, " ".join((tree.get("label") or "Lesson").split()))
    return plan


def old_screen(text, url):
    """The body HTML of one screen of an older course (groups/<n>.html): its content area, each part's title as a
    heading and its text, picture descriptions kept; "" when the page is not a lesson screen."""
    m = re.search(r"<div\b[^>]*class=\"group_container\"[^>]*>", text)
    if not m:
        return ""
    body = text[m.end():]
    questions = old_questions(body)
    body = re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S | re.I)
    body = re.sub(r"<span\b[^>]*class=\"title\"[^>]*>(.*?)</span>", r"<h3>\1</h3>", body, flags=re.S)
    body = re.sub(r"<div\b[^>]*class=\"imagetitle[^\"]*\"[^>]*>(.*?)</div>", r"<p>\1</p>", body, flags=re.S)
    return (_clean(body, url, layout=True) + questions).strip()


def old_questions(text):
    """The knowledge-check questions of an older screen, from its script (c.description and c.answers: the question
    and its choices, the right ones marked, with any feedback), as HTML; "" when it has none. The question form on
    the page itself is left out by the cleaner (forms are not read)."""
    out = []
    for m in re.finditer(r'c\.description = ("(?:[^"\\]|\\.)*");(.*?)c\.answers = (\[.*?\]);', text, re.S):
        try:
            stem, answers = json.loads(m.group(1)), json.loads(m.group(3))
        except ValueError:
            continue
        items = []
        for a in answers if isinstance(answers, list) else []:
            words = _clean(str(a.get("text") or ""))
            words = re.sub(r"^<p>(.*)</p>$", r"\1", words, flags=re.S)
            if words:
                feedback = re.sub(r"^<p>(.*)</p>$", r"\1", _clean(str(a.get("feedback") or "")), flags=re.S)
                items.append(f"<li>{words}{' (correct answer)' if a.get('correct') else ''}"
                             f"{(' ' + feedback) if feedback else ''}</li>")
        out.append("<p><strong>Knowledge check:</strong></p>" + _block(_clean(stem)) +
                   ("<ul>" + "".join(items) + "</ul>" if items else "") + _remediation(text[m.end():]))
    return "".join(out)


def _remediation(text):
    """The explanation an older screen shows after a right answer (its script's remediation "correct" text), without
    the player's "Correct. Review the feedback below ... click on the Next button." words; "" when it has none."""
    m = re.search(r"\.remediation = (\{.*?\});\s*\n", text, re.S)
    if not m:
        return ""
    try:
        words = " ".join(json.loads(m.group(1)).get("correct") or [])
    except (ValueError, AttributeError):
        return ""
    words = _clean(words)
    words = re.sub(r"(?i)\bcorrect[.!]?\s*(?=review the feedback)|review the feedback below\.?|when you are ready to "
                   r"proceed, (click|select) (on )?the next button\.?", "", words)
    words = re.sub(r"<(p|strong|span)>\s*</\1>", "", words).strip()
    return f"<p><strong>Explanation:</strong></p>{words}" if _norm(words) else ""


# ---------------------------------------------------------------------- the course books

def _licence_ok(cache, left_out, title):
    """True when govinfo.gov's policies page still quotes 17 U.S.C. 105 (the US government's works are not under
    copyright); else the reason goes into left_out."""
    import build_textbooks as B
    words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", B.fetch(K.GOVINFO_POLICY, cache))).split())
    if re.search(K.GOVINFO_TEXT, words):
        return True
    left_out.append({"title": title, "reason": f"Its licence page ({K.GOVINFO_POLICY}) no longer states the licence "
                     "that was checked."})
    return False


def book_title(c):
    """A course book's title: "IS-100.c: Introduction to the Incident Command System, ICS 100 (FEMA course, 2018)"."""
    year = (c.get("date") or "")[:4]
    return f"{c['code']}: {c['title']} (FEMA Independent Study course{', ' + year if year else ''})"


def notice_of(c, read_from):
    """A course book's notice: who wrote it, the course number and date, that it is public domain, where it was
    read, the exam and a training note."""
    hours = f"about {c['hours']:g} hours" if c.get("hours") else "a short course"
    date = f"course date {c['date']}" if c.get("date") else "no course date given"
    return (f"FEMA Emergency Management Institute, course {c['code']} ({hours}; {date}). A work of "
            f"the US government (FEMA, Department of Homeland Security): public domain. Read from {read_from}; the "
            f"course page is {OVERVIEW.format(code=c['code'])}. " + (c.get("note", "") + " " if c.get("note") else "")
            + EXAM_NOTE + " " + TRAINING_NOTE)


def new_course_book(c, read_from, changes):
    """An empty Book for course c (its pages are added by the caller)."""
    hours = f" It takes about {c['hours']:g} hours." if c.get("hours") else ""
    book = K.new_book(f"{PREFIX}_{c['name']}", book_title(c), THEMES[c["theme"]][2], GROUP, PUBLISHER, K.US_GOV,
                      K.US_GOV_URL, OVERVIEW.format(code=c["code"]), c["teaches"] + hours, notice_of(c, read_from),
                      changes=changes)
    book.published = c["date"]
    return book


def screen_ok(c, screen_title, body, left_out):
    """True when a screen may be kept: it prints no one else's copyright notice (else it is left out, said in
    left_out)."""
    if THIRD_PARTY.search(html.unescape(body)):
        left_out.append({"title": f"{c['code']}: {screen_title}", "reason": "This screen prints a copyright notice "
                         "of someone other than FEMA, so it is left out."})
        return False
    return True


def restricted(c, words, left_out):
    """True (and the reason in left_out) when a course's text carries a restricted handling marking, or says the
    course includes other people's copyrighted material."""
    m = RESTRICTED.search(words or "")
    if m:
        left_out.append({"title": book_title(c), "reason": f"Its text carries the handling marking \"{m.group(0)}\", "
                         "so it is not built."})
        return True
    m = COURSE_COPYRIGHT.search(words or "")
    if m:
        left_out.append({"title": book_title(c), "reason": f"It says it includes other people's copyrighted material "
                         f"(\"{m.group(0)}\"), so it is not built; take it online."})
        return True
    return False


def _drop_repeat(title, body):
    """A screen's body without its first heading when that heading only repeats the screen's title."""
    m = re.match(r"\s*<h3>(.*?)</h3>", body, re.S)
    return body[m.end():] if m and _norm(m.group(1)) == _norm(title) else body


def lessons_book(c, lessons, read_from, changes, left_out):
    """The Book of a course from [(lesson title, [(screen title, body)])]: one page per lesson, each screen a
    heading of its own; screens with someone else's copyright notice left out; None when a restricted marking is
    found or nothing is left."""
    import build_textbooks as B
    if restricted(c, " ".join(html.unescape(re.sub(r"<[^>]+>", " ", b)) for _l, s in lessons for _t, b in s),
                  left_out):
        return None
    book = new_course_book(c, read_from, changes)
    for number, (lesson, screens) in enumerate(lessons, 1):
        kept = [(t, b) for t, b in screens if screen_ok(c, t, b, left_out)]
        if not kept:
            continue
        body = "".join(f"<h2>{html.escape(t)}</h2>{_drop_repeat(t, b)}" for t, b in kept)
        book.pages.append(B.Page(f"lesson-{number}-{B.slug(lesson, 40)}", lesson, body, number))
    return book


def web_book(c, work, cache, left_out, limit):
    """A newer course's book, from its courseStructure.js."""
    url = EMILMS.format(folder=c["folder"]) + "courseStructure.js"
    import build_textbooks as B
    text = B.fetch(url, cache)
    if not text.lstrip().startswith("var courseStructure"):
        left_out.append({"title": book_title(c), "reason": f"Its lesson file ({url}) could not be found."})
        return None
    lessons = web_lessons(text)
    if limit:
        lessons = [(lesson, screens[:limit]) for lesson, screens in lessons[:limit]]
    book = lessons_book(c, lessons, f"its web-based lesson ({EMILMS.format(folder=c['folder'])})",
                        "its web-based lesson made into one page per lesson, each screen a heading, with the "
                        "descriptions of its pictures and its knowledge checks (right answers marked); the "
                        "classroom-only screens and the final exam left out", left_out)
    if book is not None:
        book.originals.append({"url": url, "kind": "json"})
        book.version = f"course date {c['date'] or 'not given'}; lesson file dated {K.last_modified(url) or 'unknown'}"
    return book


def old_book(c, work, cache, left_out, limit):
    """An older course's book: its table of contents, then every screen of every lesson, one request each."""
    import build_textbooks as B
    base = EMILMS.format(folder=c["folder"])
    contents = base + "curriculum/1.html"
    text = B.fetch(contents, cache)
    plan = old_plan(text, base)
    if not plan:
        left_out.append({"title": book_title(c), "reason": f"Its lesson's table of contents ({contents}) could not be "
                         "read."})
        return None
    lessons, read, missing = [], [], 0
    for lesson, screens in plan:
        got = []
        for title, url in screens:
            if limit and len(read) >= limit:
                break
            if not B.allowed_by_robots(url, cache):
                missing += 1
                continue
            try:
                body = old_screen(B.fetch(url, cache), url)
            except OSError:
                body = ""
            read.append(url)
            if body:
                got.append((title, body))
            else:
                missing += 1
        if got:
            lessons.append((lesson, got))
    if missing:
        left_out.append({"title": book_title(c), "reason": f"{missing} screens could not be read."})
    book = lessons_book(c, lessons, f"its web-based lesson ({base})",
                        "its web-based lesson made into one page per lesson, each screen a heading, with the "
                        "descriptions of its pictures; pop-up windows and the final exam left out", left_out)
    if book is not None:
        book.originals += [{"url": contents, "kind": "html"}] + [{"url": u, "kind": "html"} for u in read]
        book.version = f"course date {c['date']}; lesson contents dated {K.last_modified(contents) or 'unknown'}"
    return book


def sm_book(c, work, cache, left_out, limit):
    """A course's book from its Student Manual PDF (classroom course materials), read whole by
    build_textbooks.pdfdoc_book: from the complete-course zip file (only the Student Manual is taken out) or from
    its own address. Parts with someone else's copyright notice are left out; a restricted marking stops it."""
    import zipfile
    import build_textbooks as B
    name = f"{PREFIX}_{c['name']}"
    os.makedirs(work, exist_ok=True)
    local = os.path.join(work, f"{name}.pdf")
    source = c.get("pdf") or c["zip"]
    if c.get("zip") and not os.path.exists(local):
        if not B.allowed_by_robots(c["zip"], cache):
            left_out.append({"title": book_title(c), "reason": "The site's robots.txt does not allow its course "
                             "files."})
            return None
        archive = K.download_file(c["zip"], cache, name=f"{name}.zip")
        with zipfile.ZipFile(archive) as z:
            member = next((n for n in z.namelist() if re.search(c["member"], n, re.I)), None)
            if not member:
                left_out.append({"title": book_title(c), "reason": "Its course files no longer hold a Student "
                                 "Manual."})
                return None
            with z.open(member) as f, open(local + ".part", "wb") as out:
                out.write(f.read())
        os.replace(local + ".part", local)
    entry = K.us_pdf(GROUP, name=name, title=book_title(c), subject=THEMES[c["theme"]][2], publisher=PUBLISHER,
                     pdf=source, page=OVERVIEW.format(code=c["code"]), published=c["date"],
                     description=c["teaches"] + (f" It takes about {c['hours']:g} hours." if c.get("hours") else ""),
                     notice=notice_of(c, f"the Student Manual of its course materials ({source})"),
                     changes="its Student Manual made into web pages, one per lesson")
    book = B.pdfdoc_book(entry, work, cache, left_out)
    if book is None:
        return None
    if restricted(c, " ".join(html.unescape(re.sub(r"<[^>]+>", " ", p.body)) for p in book.pages), left_out):
        return None
    book.pages = [p for p in book.pages if screen_ok(c, p.title, p.body, left_out)]
    if limit:
        book.pages = book.pages[:limit]
    book.notice, book.published = entry["notice"], c["date"]
    book.version = f"course date {c['date']}; Student Manual file dated {K.last_modified(source) or 'unknown'}"
    return book


def course_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one course key (fema:<course>), or None (the reason in left_out)."""
    left_out = left_out if left_out is not None else []
    c = BY_NAME[name]
    if c["via"] == "link" or not _licence_ok(cache, left_out, book_title(c)):
        if c["via"] == "link":
            left_out.append({"title": book_title(c), "reason": c["why"]})
        return None
    return {"web": web_book, "old": old_book, "sm": sm_book}[c["via"]](c, work, cache, left_out, limit)


def course_sign(name):
    """A course's weekly sign of change: the server's date and size of what is read first (its lesson file, its
    table of contents, or its Student Manual or course zip)."""
    import updates
    c = BY_NAME[name]
    base = EMILMS.format(folder=c["folder"])
    url = {"web": base + "courseStructure.js", "old": base + "curriculum/1.html"}.get(c["via"]) or \
        c.get("pdf") or c.get("zip")
    return K.sha(url, updates.head_signs(url))


# ---------------------------------------------------------------------- the index

def index_book(name, work, cache=None, left_out=None, limit=None):
    """fema:index: every course by theme (number, title, what it teaches, length, date, key or why it is a link
    only), the exam, the two reference documents and the related books already in the library; written here
    (CC0)."""
    import build_textbooks as B
    book = K.new_book("fema_index", "FEMA Independent Study courses: a guide to every course", "Emergency "
                      "management training (guide)", GROUP, "Digital Accessibility Toolkit (this guide's own words)",
                      K.CC0, K.CC0_URL, CATALOGUE,
                      f"A plain-language guide to the {len(COURSES)} free FEMA Independent Study courses in this "
                      "library, by theme: what each teaches, how long it takes, its date, and the book that holds it.",
                      "This guide's own words are CC0; the courses are works of FEMA (public domain). " + EXAM_NOTE,
                      changes="written for this library from EMI's course list and course pages")
    book.published = "2026-11-23"
    start = (f"<p>FEMA's Emergency Management Institute (EMI, now part of the National Disaster and Emergency "
             f"Management University) offers free self-paced courses for anyone: emergency managers, first "
             f"responders, volunteers and the public. This library holds {len(BUILT)} of them in full, read from "
             f"EMI's own lessons and course materials, plus two reference documents. Each course is one book, "
             f"one page per lesson. The others are listed with the reason and the address.</p>"
             f"<p>{html.escape(EXAM_NOTE)}</p>"
             "<p>Where to start: IS-100.c and IS-700.b (incident command and NIMS, the basics nearly every course "
             "assumes), IS-230.e (fundamentals of emergency management), IS-317.a (CERT) and IS-909 (community "
             "preparedness).</p><p>The themes:</p><ul>"
             + "".join(f"<li>{html.escape(t[1])} (request word {t[0]})</li>" for t in THEMES.values()) + "</ul>")
    book.pages.append(B.Page("about", "About these courses and the exam", start, 0))
    for number, (theme, (word, title, _subject)) in enumerate(THEMES.items(), 1):
        rows = []
        courses = [c for c in COURSES if c["theme"] == theme]
        for c in courses[:limit] if limit else courses:
            where = f"Book key {PREFIX}:{c['name']}" if c["via"] != "link" else f"Link only: {c['why']} {c['link']}"
            rows.append(f"<h2>{html.escape(c['code'])}: {html.escape(c['title'])}</h2>" + K.dl([
                ("What it teaches", c["teaches"]),
                ("How long", f"about {c['hours']:g} hours" if c.get("hours") else ""),
                ("Course date", c["date"]),
                ("Where", where)]))
        book.pages.append(B.Page(f"theme-{number}-{B.slug(title, 40)}", title,
                                 f"<p>Request word: {html.escape(word)}.</p>" + "".join(rows), number))
    docs = "".join(f"<h2>{html.escape(d['title'])}</h2>" + K.dl([("What it is", d["description"]),
                                                                  ("Book key", f"{PREFIX}:{d['name']}")])
                   for d in DOCS)
    related = "".join(f"<h2>{html.escape(t)}</h2>" + K.dl([("What it is", what), ("Book key", key)])
                      for key, t, what in RELATED)
    book.pages.append(B.Page("documents", "Reference documents", docs, len(THEMES) + 1))
    book.pages.append(B.Page("related", "Related books already in the library", related, len(THEMES) + 2))
    return book


def index_sign(name):
    """The index's sign of change: the course list itself (it changes only when this file does)."""
    return K.sha(COURSES, [d["name"] for d in DOCS], RELATED)


# ---------------------------------------------------------------------- keys and words

def theme_keys(theme):
    """The keys of one theme's built courses (and, for incident command, the two reference documents)."""
    keys = [f"{PREFIX}:{c['name']}" for c in BUILT if c["theme"] == theme]
    if theme == "ics":
        keys += [f"{PREFIX}:{d['name']}" for d in DOCS]
    return keys


def all_keys():
    """Every key: the index first, then every course and the documents."""
    return [f"{PREFIX}:index"] + [k for theme in THEMES for k in theme_keys(theme)]


WORDS = {"fema-is": all_keys}
WORDS.update({word: (lambda theme=theme: theme_keys(theme)) for theme, (word, _t, _s) in THEMES.items()})

MAKERS = {c["name"]: (course_book, course_sign) for c in BUILT}
MAKERS["index"] = (index_book, index_sign)

COLLECTION = K.Collection(PREFIX, GROUP, pdfs=DOCS, words=WORDS, makers=MAKERS)

LICENCE_LINES = {
    "fema_is_courses": "training.fema.gov and emilms.fema.gov (FEMA's Emergency Management Institute): works of the "
                       "US government (17 U.S.C. 105, checked on govinfo.gov's policies page at every build). Both "
                       "sites have no robots.txt (404: no rules, no AI rules; checked 2026-11-23). Screens or parts "
                       "with another owner's copyright notice, and courses with restricted handling markings, are "
                       "left out at every build.",
    "fema_is_index": "fema:index is this toolkit's own words (CC0), made from EMI's course list.",
}

NOT_INCLUDED = [(f"FEMA {c['code']}: {c['title']}", c["why"] + " Index: " + c["link"])
                for c in COURSES if c["via"] == "link"] + [
    ("FEMA retired Independent Study courses: IS-368 (Including People With Disabilities and Others With Access and "
     "Functional Needs in Disaster Operations), IS-394.a (Protecting Your Home or Small Business From Disaster), "
     "IS-325 (Earthquake Basics), IS-326 (Community Tsunami Preparedness), IS-632.a (Introduction to Debris "
     "Operations), IS-522 (Exercising Continuity Plans for Pandemics), IS-552 (The Public Works Role in Emergency "
     "Management), IS-554, IS-1.a, IS-101.c, IS-320 to IS-323, IS-660, IS-662, IS-912 to IS-916 and others",
     "EMI's pages say each \"has been retired\" (most \"without a replacement\") or that the course cannot be found "
     "(checked 2026-11-23); no exam is offered and, but for IS-552, no lesson files are left on emilms.fema.gov. "
     "IS-552's lesson is still online but retired, so it is not built (the current courses are preferred). Their "
     "topics are covered by current courses and books: IS-406 and IS-405.a (shelters and mass care), IS-559 and "
     "the Public Assistance courses (damage and debris), IS-1300.a and IS-545.a (continuity), Ready.gov "
     "(ready:ready_gov) for protecting a home. IS-907 is retired too but still published, so it is built. Index: "
     + CATALOGUE),
    ("FEMA Independent Study course materials in Spanish (IS-100.c and IS-200.c, \"curso completo\")", "Public "
     "domain, but the library's course books are in English; the Spanish zip files are on the course materials "
     "pages. Index: https://training.fema.gov/programs/independent-study/courseMaterials.aspx?code=IS-100.c"),
    ("FEMA Independent Study instructor guides and slide files (classroom course materials)", "Public domain; only "
     "the Student Manual of a course's materials is read (the instructor guide repeats it with teaching notes; the "
     "slides are pictures of the same text). Index: "
     "https://training.fema.gov/programs/independent-study/courseMaterials.aspx?code=IS-700.b"),
    ("FEMA radiological courses IS-3 and IS-301 to IS-303", "Now given by the Center for Domestic Preparedness "
     "(cdp.dhs.gov) as online courses that need an account (AWR-923-W and others), not as open Independent Study "
     "lessons. Index: https://cdp.dhs.gov/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
