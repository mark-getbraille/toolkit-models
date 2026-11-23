"""Teaching and homeschooling, state by state: the 50-state search of the owner's request of 23 November 2026, for the
50 states, the District of Columbia and the five inhabited US territories. In the group "Teaching and homeschooling"
(group key "k12", sources.GROUPS). Keys: tstate:index, tstate:homeschool_laws:<region>, tstate:<name>.

What this module builds, in plain words:
  - tstate:index, the state table (the toolkit's own facts and links, CC0): one page per region, one section per state
    with (a) its homeschooling law (the statute or rule, the state education agency's official page, and what that
    page says in a sentence) and (b) what openly licensed teaching material the state education agency publishes, with
    the result of the search in plain words: "open, built here", "personal use only", "already in the library",
    "link-only", "no open materials found" or "not searched in depth". Every jurisdiction has a row, even when
    nothing open was found; a first page sums the table up.
  - tstate:homeschool_laws:<region> (northeast, midwest, south, west; the territories have no official text read yet,
    see law_regions): the homeschooling statutes and
    rules themselves, one page per state, read IN FULL from the legislature's or the agency's official page (HTML or
    PDF) at every build. State statutes and the rules a state agency makes under them are not under copyright (the
    "government edicts" doctrine, Georgia v. Public.Resource.Org, 590 U.S. 255 (2020); state_laws.STATE_LAW). Only
    official legislature or agency addresses are read; a site whose robots.txt refuses us or shuts out AI readers is
    left out and said. A state whose official code is only on a publisher's site (LexisNexis, Justia) has no page;
    its index row links the agency's page instead.
  - Washington (OSPI, CC BY 4.0, checked 2026-11-23 on the pages and in the PDFs):
      tstate:wa_since_time_immemorial: John McCoy (lulilas) Since Time Immemorial: Tribal Sovereignty in Washington
        State, the state's tribal history and sovereignty curriculum made with the federally recognized tribes:
        every unit's curriculum PDFs (early learning, elementary, middle and high school), found on the unit pages at
        every build (pdf_set). The curriculum page: '"Since Time Immemorial: Tribal Sovereignty in Washington State"
        by Office of Superintendent of Public Instruction in partnership with the Federally Recognized Tribes in
        Washington State is licensed under a Creative Commons Attribution 4.0 International License.' Parts marked
        with another licence keep it (the page says alternate licences are marked next to the content);
      tstate:wa_social_studies_standards (its PDF says CC BY 4.0), tstate:wa_sel_standards and
        tstate:wa_environmental_sustainability_standards (OSPI's site information page: "Except where otherwise
        noted, content by the Office of Superintendent of Public Instruction on this site is licensed under a
        Creative Commons Attribution License"; neither PDF notes another licence).
  - Utah: the Utah Middle School Math Project (University of Utah with the Utah State Office of Education), each
    PDF printing "This work is published under the Creative Commons Attribution License ("CC BY")" (3.0, checked at
    every build): tstate:utah_math_7_workbook, tstate:utah_math_7_foundations, tstate:utah_math_8_workbook,
    tstate:utah_math_8_foundations. (Utah's open science textbooks, CC BY-NC-SA, are already in the library as
    pdf:utah_science_*, personal use.)
  - Massachusetts, PERSONAL USE ONLY (CC BY-NC 4.0, printed in each PDF): the Investigating History curriculum's
    guidebook and its grade 4, 6 and 7 course overviews (tstate:ma_investigating_history_*).

Every other state's teaching material that was found is link-only (a copyright notice, terms limited to the state's
own teachers, or no licence stated) or was not found; the index says which. NOT_INCLUDED lists them with reasons.

Searched (23 November 2026): each agency's homeschool page and its open-material pages, with web searches for its
open educational resources and licence statements; the PDFs and pages built here were read and their licence lines
checked by hand. OER Commons (most state hubs live there) answers programs "403 Forbidden", so its hubs are named,
not read. The US Department of Education's state-by-state "State Regulation of Private and Home Schools" pages are a
federal (public domain) source, but www.ed.gov answers programs 403; they are linked from teach:index.

Request words (each at most 256 jobs, sources.expand_keys): tstate-laws (the index and the five law books),
tstate-curriculum (the index and every curriculum book), tstate-northeast, tstate-midwest, tstate-south, tstate-west,
tstate-territories (the index, that region's law book and its states' curriculum books), teach-us (all of it).

Run from the repository's folder:
  python3 textbooks/teach_states.py tstate:index --out build/textbooks
  python3 textbooks/teach_states.py tstate:homeschool_laws:west --out build/textbooks --limit 3
  python3 textbooks/teach_states.py --list teach-us
"""

import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

# "Teaching and homeschooling" (named in sources.GROUPS under the school books' key "k12").
GROUP = "k12"
GROUPS = {}
PREFIX = "tstate"

REGIONS = {"northeast": "Northeast", "midwest": "Midwest", "south": "South", "west": "West",
           "territories": "US territories"}

# The licence of statutes and agency rules (the same words as state_laws.py, which builds whole state codes).
STATE_LAW = "Public domain (state law: Georgia v. Public.Resource.Org, 2020)"
STATE_LAW_URL = "https://www.supremecourt.gov/opinions/19pdf/18-1150_7m58.pdf"
ALLOWED = {STATE_LAW: "open"}
LAW_NOTE = ("Homeschooling laws change, often every legislative session: this is the text as the official site showed "
            "it on the day it was read. General information, not legal advice; check the state's own page or ask "
            "the state education agency, your school district or a lawyer.")

# The result words of the state table (one per state, for the curriculum search).
RESULTS = {
    "built": "open, built here",
    "personal": "personal use only (built here, marked)",
    "library": "already in the library",
    "link": "link-only",
    "none": "no open materials found",
    "unsearched": "not searched in depth",
}


def S(key, name, region, law, page, says, statutes=(), found=(), result="unsearched"):
    """One jurisdiction of the table: its key, name and region; its homeschooling law (citation), the agency's official
    page and what that page says in one sentence; the official statute or rule addresses read into the law book; what
    was found of the agency's own teaching material [(kind, words, address or key)] where kind is "built",
    "personal", "library", "link" or "none"; and the search result (a RESULTS key)."""
    return dict(key=key, name=name, region=region, law=law, page=page, says=says, statutes=list(statutes),
                found=list(found), result=result)


NOT_FOUND = ("none", "No openly licensed teaching material of the state education agency was found in a web search "
                     "of its site and of open-resource directories.", "")
UNSEARCHED = ("none", "Only the homeschooling law was looked up; the agency's own teaching materials were not "
                      "searched in depth this time.", "")

STATES = [
    # ------------------------------------------------------------------ Northeast
    S("connecticut", "Connecticut", "northeast", "Conn. Gen. Stat. 10-184 (equivalent instruction)",
      "https://portal.ct.gov/SDE/Homeschooling/Homeschooling-in-Connecticut",
      "The State Department of Education's guidelines recommend a notice of intent to the local board of education; "
      "a 2025 legislative report says this is not a legal requirement.",
      ["https://www.cga.ct.gov/current/pub/chap_168.htm"],
      [("link", "GoOpen CT, the state's open-resource library (an OER Commons hub), and the State Department of "
                "Education's model curricula (maths 6-8, financial literacy 6-12, science 6-8): no licence for the "
                "model curricula was found.", "https://goopenct.org")], "link"),
    S("maine", "Maine", "northeast", "20-A M.R.S. 5001-A (home instruction)",
      "https://www.maine.gov/doe/schools/schoolops/homeinstruction/requirements",
      "A notice of intent to provide home instruction is filed online or on paper; for later years it is due by "
      "1 September with the previous year's assessment.",
      ["https://www.legislature.maine.gov/statutes/20-A/title20-Asec5001-A.html"], [UNSEARCHED]),
    S("massachusetts", "Massachusetts", "northeast", "M.G.L. c. 76, s. 1 (approval by the school committee)",
      "https://www.doe.mass.edu/homeschool/",
      "Home schooling needs the advance approval of the district where the child lives; the Department says this is "
      "a local decision it does not review.",
      ["https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXII/Chapter76/Section1"],
      [("personal", "Investigating History (grades 3-7 history and social science curriculum), CC BY-NC 4.0: the "
                    "guidebook and the grade 4, 6 and 7 course overviews.",
        "tstate:ma_investigating_history_guidebook")],
      "personal"),
    S("new_hampshire", "New Hampshire", "northeast", "RSA 193-A (home education); rules Ed 315",
      "https://www.education.nh.gov/pathways-education/home-education",
      "A parent starting a home education program notifies as RSA 193-A:5 and the Ed 315 rules say, and keeps a "
      "portfolio of records.",
      ["https://gc.nh.gov/rsa/html/XV/193-A/193-A-mrg.htm"], [UNSEARCHED]),
    S("new_jersey", "New Jersey", "northeast", "N.J.S.A. 18A:38-25 (equivalent instruction elsewhere than at school)",
      "https://www.nj.gov/education/safety/nontraditional/faq_homeschool.shtml",
      "The Department's questions and answers say the law allows equivalent instruction elsewhere than at school, "
      "including the home.", [], [UNSEARCHED]),
    S("new_york", "New York", "northeast", "Education Law 3204; Commissioner's regulation 8 NYCRR 100.10",
      "https://www.nysed.gov/nonpublic-schools/home-instruction",
      "Home instruction follows section 100.10 of the Commissioner's regulations (notice, an individualized home "
      "instruction plan, quarterly reports and an annual assessment); NYSED says its questions page is under review.",
      ["https://www.nysed.gov/curriculum-instruction/10010-home-instruction"],
      [("library", "EngageNY (the New York State Education Department's maths and English modules, CC BY-NC-SA, "
                   "personal use) is already in the library.", "course:engageny")], "library"),
    S("pennsylvania", "Pennsylvania", "northeast", "24 P.S. 13-1327.1 (home education program)",
      "https://www.pa.gov/agencies/education/programs-and-services/instruction/elementary-and-secondary-education/"
      "home-education-and-private-tutoring.html",
      "A home education program exists in law only with its affidavit; later affidavits are due by 1 August.",
      ["https://www.pa.gov/agencies/education/resources/policies-acts-and-laws/basic-education-circulars-becs/"
       "purdons-statutes/home-education-program.html"],
      [("link", "The Standards Aligned System (pdesas.org): older materials say \"Copyright Commonwealth of "
                "Pennsylvania\"; no open licence was found.", "https://www.pdesas.org/")], "link"),
    S("rhode_island", "Rhode Island", "northeast", "R.I. Gen. Laws 16-19-1 and 16-19-2 (approval by the school "
      "committee)", "https://ride.ri.gov/Home-Schooling",
      "Approval of at-home instruction is given only by the local school committee; RIDE hears appeals.",
      ["https://webserver.rilegislature.gov/Statutes/TITLE16/16-19/16-19-2.HTM"], [UNSEARCHED]),
    S("vermont", "Vermont", "northeast", "16 V.S.A. 166b (home study)",
      "https://education.vermont.gov/student-support/home-study",
      "A notice of intent goes to the Secretary of Education at least 10 business days before home study starts, "
      "and again each year.",
      ["https://legislature.vermont.gov/statutes/section/16/003/00166b"], [UNSEARCHED]),
    # ------------------------------------------------------------------ Midwest
    S("illinois", "Illinois", "midwest", "105 ILCS 5/26-1 and 5/27-1 (home schooling as private education)",
      "https://www.isbe.net/Pages/Homeschool.aspx",
      "The State Board's page says Illinois does not require parents to register before they begin home schooling; "
      "the required subjects are taught in English.",
      ["https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=010500050K26-1"],
      [("none", "The Illinois Open Educational Resources (IOER) platform was found, but no licence for the State "
                "Board's own curriculum materials.", "")], "none"),
    S("indiana", "Indiana", "midwest", "IC 20-33-2 (compulsory attendance; homeschool attendance records, IC "
      "20-33-2-20)", "https://www.in.gov/doe/students/homeschool-information",
      "Reporting a homeschool's enrollment to the Department is optional (IC 20-33-2-21); daily attendance records "
      "are kept.", [], [NOT_FOUND], "none"),
    S("iowa", "Iowa", "midwest", "Iowa Code chapter 299A (competent and independent private instruction)",
      "https://educate.iowa.gov/pk-12/options/private-instruction",
      "Chapter 299A sets competent private instruction and independent private instruction.",
      ["https://www.legis.iowa.gov/docs/code/2026/299A.pdf"], [UNSEARCHED]),
    S("kansas", "Kansas", "midwest", "K.S.A. 72-4345 to 72-4347 (non-accredited private schools)",
      "https://www.ksde.gov/student-success/learning-alternatives/nonaccredited-private-schools",
      "Homeschools are registered as non-accredited private schools with the State Department of Education; it "
      "supplies no books or curriculum for them.", [],
      [("none", "KSDE's homeschool fact sheet says the Department does not supply books, curriculum materials or "
                "technical assistance for non-accredited private schools.", "")], "none"),
    S("michigan", "Michigan", "midwest", "MCL 380.1561 (compulsory attendance exemptions (3)(a) and (3)(f))",
      "https://www.michigan.gov/mde/services/flexible-learning/options/nonpub-home/home-school-information",
      "A home school may operate as a nonpublic school (and may file the voluntary membership report) or under "
      "exemption (f) without reporting.", [],
      [("link", "The Michigan Open Book Project (social studies e-textbooks commissioned by the Michigan Department of "
                "Education, hosted by Wexford-Missaukee ISD), CC BY-NC-SA 4.0: personal use, not built (each book's "
                "own licence page should be checked first).", "https://textbooks.wmisd.org/the-books.html"),
       ("link", "#GoOpen Michigan (an OER Commons hub; each item has its own licence).",
        "https://www.michigan.gov/mde/services/academic-standards/go-open")], "link"),
    S("minnesota", "Minnesota", "midwest", "Minn. Stat. 120A.22 and 120A.24 (reporting)",
      "https://education.mn.gov/MDE/fam/nonpub/",
      "Home schools report to the school district superintendent as section 120A.24 says.",
      ["https://www.revisor.mn.gov/statutes/cite/120A.22", "https://www.revisor.mn.gov/statutes/cite/120A.24"],
      [("none", "No licence for the Department's Dakota and Ojibwe language curricula was found (Legacy-funded "
                "projects describe their materials as open to the public, without a licence).", "")], "none"),
    S("missouri", "Missouri", "midwest", "RSMo 167.012, 167.031 and 167.042",
      "https://dese.mo.gov/communications/frequently-asked-questions-and-educational-topics",
      "DESE says it does not regulate or monitor home schooling and there is no state registration (section 167.042 "
      "was changed in 2025: read the current text).",
      ["https://revisor.mo.gov/main/OneSection.aspx?section=167.031",
       "https://revisor.mo.gov/main/OneSection.aspx?section=167.042"],
      [("link", "Missouri Open Educational Resources Commons (MOREnet with DESE, an OER Commons hub; each item has "
                "its own licence).", "https://oercommons.org/hubs/missouri")], "link"),
    S("nebraska", "Nebraska", "midwest", "Neb. Rev. Stat. 79-1601; NDE Rules 12 and 13 (exempt schools)",
      "https://www.education.ne.gov/fos/exempt-schools/",
      "Homeschools are \"exempt schools\"; LB 1027 (2024) amended 79-1601 and changed many provisions of the rules.",
      ["https://nebraskalegislature.gov/laws/statutes.php?statute=79-1601"], [UNSEARCHED]),
    S("north_dakota", "North Dakota", "midwest", "N.D.C.C. chapter 15.1-23 (home education)",
      "https://www.nd.gov/dpi/families/home-education",
      "A statement of intent (form SFN 16909) goes to the Department of Public Instruction; instruction is at least "
      "four hours a day for 175 days.", ["https://ndlegis.gov/cencode/t15-1c23.html"], [UNSEARCHED]),
    S("ohio", "Ohio", "midwest", "ORC 3321.042 (home education notification)",
      "https://education.ohio.gov/Topics/Ohio-Education-Options/Home-Schooling",
      "The parent notifies the superintendent of the district of residence (within five days of starting, then by "
      "30 August each year); the Department provides no template.",
      ["https://codes.ohio.gov/ohio-revised-code/section-3321.042"],
      [("link", "Ohio's model curricula: the Department's terms of use for them were not confirmed; link-only.",
        "https://education.ohio.gov/Topics/Learning-in-Ohio/OLS-Graphic-Sections/Model-Curricula")], "link"),
    S("south_dakota", "South Dakota", "midwest", "SDCL 13-27-3 and 13-27-7 (alternative instruction)",
      "https://doe.sd.gov/oatq/homeschooling.aspx",
      "Families file an Alternative Instruction Notification on the Department's form, one per child, within 30 days "
      "of starting.", ["https://sdlegislature.gov/api/Statutes/13-27-3.html"], [UNSEARCHED]),
    S("wisconsin", "Wisconsin", "midwest", "Wis. Stat. 115.001(3g), 118.15(4) and 118.165 (home-based private "
      "educational program)", "https://dpi.wi.gov/parental-education-options/home-based",
      "Parents file the online PI-1206 homeschool enrollment report each school year by 15 October; at least 875 "
      "hours of instruction a year.",
      ["https://docs.legis.wisconsin.gov/statutes/statutes/118/165"],
      [("link", "WISELearn (DPI's OER Commons library; licences chosen item by item). DPI's own web pages are "
                "copyrighted by DPI.", "https://dpi.wi.gov/wiselearn")], "link"),
    # ------------------------------------------------------------------ South
    S("alabama", "Alabama", "south", "Code of Alabama 16-28-3 (church school), 16-28-1 (private school and "
      "certified private tutor)", "https://instructional-services.alsde.edu/homeschool",
      "The Department's page says Alabama has no law dedicated to homeschooling; families use a church school, a "
      "private school or a certified private tutor.", [],
      [("link", "ALEX, the Alabama Learning Exchange (lesson plans and open resources): no current licence statement "
                "was found, and the Department's terms of use say its website materials are copyrighted.",
        "https://alex.alsde.edu/")], "link"),
    S("arkansas", "Arkansas", "south", "Ark. Code 6-15-503 and DESE Rules Governing Home Schools",
      "https://dese.ade.arkansas.gov/Offices/office-of-school-choice-and-parent-empowerment/home-schools",
      "A notice of intent, required by law each academic year, is filed online or with the district superintendent.",
      ["https://dese.ade.arkansas.gov/Files/Home_Schools_6CARpt.33_Legal.pdf"], [NOT_FOUND], "none"),
    S("delaware", "Delaware", "south", "14 Del. C. chapter 4A and 2703 (nonpublic schools)",
      "https://education.delaware.gov/families/k12/homeschools-and-private-schools/opening-a-nonpublic-school",
      "Families homeschool by opening a nonpublic school with the Department and reporting enrollment and attendance "
      "each year.", [],
      [("none", "Delaware announced a #GoOpen statewide repository in 2016; nothing current was found.", "")], "none"),
    S("district_of_columbia", "District of Columbia", "south", "5-E DCMR chapter 52 (home schooling)",
      "https://osse.dc.gov/homeschool",
      "A notification of intent to homeschool goes to OSSE at least 15 business days before home instruction starts, "
      "and a continuation notice by 15 August each year.", [], [UNSEARCHED]),
    S("florida", "Florida", "south", "Fla. Stat. 1002.41 (home education program)",
      "https://www.fldoe.org/schools/school-choice/other-school-choice-options/home-edu/",
      "The parent notifies the district school superintendent, who registers the program; an annual evaluation is "
      "due each year.", ["https://www.flsenate.gov/Laws/Statutes/2024/1002.41"],
      [("link", "CPALMS (run by Florida State University with Department of Education funding): its resources may be "
                "linked to but not copied, and are free only to Florida public school teachers.",
        "https://www.cpalms.org/")], "link"),
    S("georgia", "Georgia", "south", "O.C.G.A. 20-2-690 (home study programs)",
      "https://gadoe.org/Curriculum-Instruction-and-Assessment/Pages/Home-Schools.aspx",
      "A declaration of intent is filed with the Department by 1 September each year (or within 30 days of "
      "starting).", [],
      [("link", "Georgia Virtual Learning's shared course resources (grades 6-12), which it says are licensed CC "
                "BY-NC: personal use, not built (web courses moving to a Canvas public course).",
        "https://gavirtuallearning.org/Resources/Shared-Landing-Page")], "link"),
    S("kentucky", "Kentucky", "south", "KRS 159.030 and 159.040 (homeschool as a private school)",
      "https://education.ky.gov/federal/fed/Documents/Kentucky%20Homeschool%20Information%20Packet.pdf",
      "The Department's packet says a homeschool is a private school; attendance and scholarship records are kept "
      "but not sent to the Department or the district.", [],
      [("link", "KDE's copyright page: its publications are copyrighted and use by anyone other than a Kentucky "
                "educator needs permission.", "https://education.ky.gov/Pages/Copyright.aspx")], "link"),
    S("louisiana", "Louisiana", "south", "La. R.S. 17:236.1 (home study programs; a 2024 bill, HB 550, changed BESE "
      "approval: read the current text)", "https://doe.louisiana.gov/schools/home-study",
      "The Department's page describes applying online for a BESE-approved home study program each year.",
      ["https://legis.la.gov/Legis/Law.aspx?d=80346"],
      [("link", "The Louisiana ELA Guidebooks (open access; no licence statement was found, and the unit readers are "
                "publishers' copyrighted texts).", "https://doe.louisiana.gov/academics/ela-guidebooks")], "link"),
    S("maryland", "Maryland", "south", "COMAR 13A.10.01 (home instruction)",
      "https://marylandpublicschools.org/about/pages/dee/npsa/home-instruction.aspx",
      "The parent signs the MSDE form and gives it to the local superintendent at least 15 days before home "
      "instruction begins.", [], [UNSEARCHED]),
    S("mississippi", "Mississippi", "south", "Miss. Code 37-13-91 (certificate of enrollment)",
      "https://www.mdek12.org/OCSAE",
      "The parent completes the certificate of enrollment (prepared by the Department's Office of Compulsory School "
      "Attendance Enforcement) for the school attendance officer.", [], [UNSEARCHED]),
    S("north_carolina", "North Carolina", "south", "G.S. 115C-563 to 115C-565 (home schools)",
      "https://www.doa.nc.gov/divisions/non-public-education/home-schools/requirements-recommendations",
      "A notice of intent goes to the Division of Non-Public Education; a nationally normed test each year; the "
      "Division provides no curriculum.",
      ["https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_115C/GS_115C-563.html"],
      [("link", "#GoOpenNC (NCDPI's open-resource platform on OER Commons; licences item by item; no licence for "
                "NCDPI's own maths materials was found).", "https://www.dpi.nc.gov/educators/home-base/goopennc")],
      "link"),
    S("oklahoma", "Oklahoma", "south", "Okla. Const. art. XIII, s. 4 (\"other means of education\")",
      "https://sde.ok.gov/", "The constitution requires attendance at a public or other school \"unless other means "
      "of education are provided\"; no Department homeschool page was found.",
      ["https://accessible.oksenate.gov/sites/default/files/2019-12/oc13.pdf"], [UNSEARCHED]),
    S("south_carolina", "South Carolina", "south", "S.C. Code 59-65-40, 59-65-45 and 59-65-47 (three options)",
      "https://ed.sc.gov/districts-schools/state-accountability/home-schooling",
      "Parents choose the district board option, the South Carolina Association of Independent Home Schools, or "
      "another association of at least fifty members.", ["https://www.scstatehouse.gov/code/t59c065.php"],
      [UNSEARCHED]),
    S("tennessee", "Tennessee", "south", "T.C.A. 49-6-3050 (home schools)",
      "https://www.tn.gov/education/families/school-options/home-schooling-in-tn.html",
      "An independent home school files the intent to home school form with the local school district before each "
      "school year.", [],
      [("none", "Reading 360's free decodable books and resources were found, but no open licence.", "")], "none"),
    S("texas", "Texas", "south", "Texas Education Code 25.086(a)(1) as read in Leeper v. Arlington ISD (1995)",
      "https://tea.texas.gov/texas-schools/general-information/finding-a-school-for-your-child/home-schooling",
      "TEA says home schools may operate as private schools and that it does not regulate, register or accredit "
      "them.", [],
      [("link", "Bluebonnet Learning, the state-developed open education resources: the property of the State of "
                "Texas under TEA's own licence agreement (not a Creative Commons licence; the K-5 maths needs "
                "credentials).", "https://tea.texas.gov/bluebonnet")], "link"),
    S("virginia", "Virginia", "south", "Code of Virginia 22.1-254.1 (home instruction)",
      "https://www.doe.virginia.gov/parents-students/for-parents/home-instruction",
      "Parents give notice by 15 August each year and evidence of progress by 1 August after the year.",
      ["https://law.lis.virginia.gov/vacode/title22.1/chapter14/section22.1-254.1/"],
      [("link", "VDOE's curriculum frameworks: \"All rights reserved\", reproduction allowed only in Virginia public "
                "school classrooms.", "https://www.doe.virginia.gov/teaching-learning-assessment/instruction")],
      "link"),
    S("west_virginia", "West Virginia", "south", "W. Va. Code 18-8-1 (home instruction exemption)",
      "https://wvde.us/academics/school-choice/homeschool-state-code",
      "A notice of intent is given on or before the day home instruction begins.",
      ["https://code.wvlegislature.gov/18-8-1/"], [UNSEARCHED]),
    # ------------------------------------------------------------------ West
    S("alaska", "Alaska", "west", "AS 14.30.010(b)(12) (home education by a parent)",
      "https://education.alaska.gov/alaskan_schools/homeschool",
      "The compulsory attendance law does not apply to a child educated at home by a parent; correspondence "
      "programmes are district schooling, not homeschooling.", [],
      [("link", "The Department's Alaska Native Language Literacy Guidebook and the Alaska Native Language Arts K-3 "
                "Reading Standards (with Sealaska Heritage Institute): no licence stated.",
        "https://education.alaska.gov/officeoftribalaffairs/alaska-native-language-literacy-guidebook")], "link"),
    S("arizona", "Arizona", "west", "A.R.S. 15-802 (affidavit of intent)", "https://www.azed.gov/",
      "An affidavit of intent is filed with the county school superintendent (not the state department).",
      ["https://www.azleg.gov/ars/15/00802.htm"], [NOT_FOUND], "none"),
    S("california", "California", "west", "Education Code 48222 and 33190 (private school affidavit)",
      "https://www.cde.ca.gov/sp/ps/homeschool.asp",
      "Homeschools file the Private School Affidavit each year; CDE says filing is not an approval.", [],
      [("link", "CDE's curriculum frameworks are protected by copyright; reproduction needs CDE Press's permission. "
                "CDE's braille reading standards are link-only too.", "https://www.cde.ca.gov/ci/cr/cf/")], "link"),
    S("colorado", "Colorado", "west", "C.R.S. 22-33-104.5 (home-based education)",
      "https://www.cde.state.co.us/choice/homeschool",
      "The letter of intent goes to a school district, not to CDE; testing or an evaluation at grades 3, 5, 7, 9 "
      "and 11.", [],
      [("link", "OERColorado, Colorado's PK-12 OER community on OER Commons (licences item by item).",
        "https://oercommons.org/hubs/oercolorado")], "link"),
    S("hawaii", "Hawaii", "west", "HRS 302A-1132; Hawaii Administrative Rules title 8, chapter 12",
      "https://hawaiipublicschools.org/enrolling-in-school/homeschool/",
      "A notice of intent (form 4140 or a letter) goes to the local school principal before home schooling starts.",
      ["https://boe.hawaii.gov/wp-content/uploads/2024/07/12-Compulsory-Attendance-Exceptions.pdf"],
      [("link", "The Hawaiian-language immersion (Kaiapuni) programme's materials: no open licence was found; the "
                "Department's website terms reserve its copyright.",
        "https://hawaiipublicschools.org/useful-links/terms-of-use/")], "link"),
    S("idaho", "Idaho", "west", "Idaho Code 33-202 (comparable instruction)",
      "https://www.sde.idaho.gov/about-us/departments/school-choice/home-school/",
      "The Department says Idaho does not regulate or monitor homeschooling and no registration is required.",
      ["https://legislature.idaho.gov/statutesrules/idstat/Title33/T33CH2/SECT33-202"], [UNSEARCHED]),
    S("montana", "Montana", "west", "MCA 20-5-109 and 20-5-111 (home schools)",
      "https://opi.mt.gov/Portals/182/Page%20Files/Just%20for%20Parents/Home%20School%20Packet.pdf",
      "Home schools notify the county superintendent each school year and keep attendance and immunization records.",
      ["https://archive.legmt.gov/bills/MCA/title_0200/chapter_0050/part_0010/section_0090/"
       "0200-0050-0010-0090.html"],
      [("link", "Indian Education for All lessons (OPI, with cultural consultants from Montana's Tribal Nations): no "
                "licence was found.", "https://opi.mt.gov/Educators/Teaching-Learning/Indian-Education-for-All/"
                                      "Indian-Education-Curriculum")], "link"),
    S("nevada", "Nevada", "west", "NRS 388D.020 (notice of intent to homeschool)",
      "https://doe.nv.gov/offices/craleo/nevada-homeschooling",
      "The notice of intent, on the Department's form, goes to the school district where the child lives.",
      ["https://www.leg.state.nv.us/NRS/NRS-388D.html"], [UNSEARCHED]),
    S("new_mexico", "New Mexico", "west", "NMSA 22-1-2.1 (home schools)",
      "https://webnew.ped.state.nm.us/bureaus/options-parents-families/home-schools/",
      "A parent notifies the Public Education Department within 30 days of starting a home school and by 1 August "
      "each year.", [],
      [("link", "The PED's companion guide to the braille standards (6.60.5 NMAC): no licence was found.",
        "https://webnew.ped.state.nm.us/wp-content/uploads/2025/02/6.60.5-NMAC-Braille-Standards-Companion-Guide.pdf")],
      "link"),
    S("oregon", "Oregon", "west", "ORS 339.035 (instruction by a parent or private teacher); OAR 581-021-0026",
      "https://www.oregon.gov/ode/learning-options/homeschool/pages/infoforfamilies.aspx",
      "Families notify their Education Service District within 10 days of withdrawing from school or of the start of "
      "the school year.", ["https://www.oregonlegislature.gov/bills_laws/ors/ors339.html"],
      [("link", "The Tribal History/Shared History lesson plans (Senate Bill 13, made with Oregon's nine tribes): no "
                "licence was found.", "https://www.oregon.gov/ode/students-and-family/equity/NativeAmericanEducation/"
                                      "Pages/Senate-Bill-13-Tribal-HistoryShared-History.aspx")], "link"),
    S("utah", "Utah", "west", "Utah Code 53G-6-204 (home school; changed in 2024 and 2025)",
      "https://schools.utah.gov/curr/homeschool",
      "A local board excuses a child for home school when the parent gives the required notice (HB 209 of 2025 "
      "changed the affidavit rules: read the current text).",
      ["https://le.utah.gov/xcode/Title53G/Chapter6/C53G-6-S204_2025050720250507.pdf"],
      [("built", "The Utah Middle School Math Project, grades 7 and 8 (student workbooks and Mathematical "
                 "Foundations), CC BY.", "tstate:utah_math_7_workbook"),
       ("library", "Utah's open science textbooks K-12 (CC BY-NC-SA, personal use) are already in the library.",
        "pdf:utah_science_kindergarten"),
       ("link", "The Utah Braille Core Standards, ELA K-6 (USBE): no licence statement.",
        "https://www.schools.utah.gov/specialeducation/_specialeducation/_disabilityspecific/_visualimpairment/"
        "DisabilityUtahBrailleCoreStandardsELAK6.pdf")], "built"),
    S("washington", "Washington", "west", "RCW 28A.200 and 28A.225.010(4) (home-based instruction)",
      "https://ospi.k12.wa.us/student-success/learning-alternatives/home-based-instruction",
      "A declaration of intent goes to the district superintendent by 15 September each year (or within two weeks "
      "of the start of a term).", ["https://app.leg.wa.gov/RCW/default.aspx?cite=28A.200&full=true"],
      [("built", "John McCoy (lulilas) Since Time Immemorial: Tribal Sovereignty in Washington State (CC BY 4.0).",
        "tstate:wa_since_time_immemorial"),
       ("built", "OSPI's K-12 social studies, social-emotional learning, and environmental and sustainability "
                 "learning standards (CC BY 4.0).", "tstate:wa_social_studies_standards"),
       ("link", "The Washington State School for the Blind's resources for teaching braille (licence not checked).",
        "https://wssb.wa.gov/sites/default/files/2024-05/WSSBMentorResource-ResourcesForTeachingBraille-051524.pdf")],
      "built"),
    S("wyoming", "Wyoming", "west", "W.S. 21-4-101(a)(vi) and 21-4-102(b) (home-based educational program)",
      "https://edu.wyoming.gov/parents/homeschooling/",
      "The programme gives a sequentially progressive curriculum in seven subjects, submitted to the local board "
      "each year.", [], [UNSEARCHED]),
    # ------------------------------------------------------------------ US territories
    S("american_samoa", "American Samoa", "territories", "A.S. Code 16.0701 (private schools; authorization)",
      "https://www.doe.as/", "A home school authorized by the Department of Education is treated as a private "
      "school (as the US Department of Education's 2017 page describes it).", [], [UNSEARCHED]),
    S("guam", "Guam", "territories", "17 GCA chapter 6 (pupils; home schooling standards)",
      "https://www.gdoe.net/", "No current Guam Department of Education homeschool page was found; the Guam Code's "
      "chapter 6 has the home schooling standards.", [], [UNSEARCHED]),
    S("northern_mariana_islands", "Northern Mariana Islands", "territories", "Commonwealth law and the Public School "
      "System's rules (a waiver from the Commissioner of Education)", "https://www.cnmipss.org/",
      "Homeschooling is by a waiver from compulsory attendance (as secondary sources describe it); no official page "
      "was found.", [], [UNSEARCHED]),
    S("puerto_rico", "Puerto Rico", "territories", "Ley 85-2018 (Ley de Reforma Educativa) - no homeschooling "
      "provision was found in it", "https://de.pr.gov/",
      "The Departamento de Educación's 2023-24 special education policy mentions services for students taught at "
      "home (\"enseñanza en el hogar\"); no notice or registration rule was found.", [], [UNSEARCHED]),
    S("us_virgin_islands", "US Virgin Islands", "territories", "17 V.I.C. 84 (home instruction under Board of "
      "Education rules)", "https://vide.vi/",
      "A notice of intent is filed with the Department of Education each year (the 1998 and 2016 rules differ).",
      [], [("link", "GoOpen USVI, the Department's open-resource hub on OER Commons (licences item by item).",
            "https://goopenusvi.vide.vi/")], "link"),
]

BY_KEY = {s["key"]: s for s in STATES}


# ====================================================================== the curriculum books (CC BY, and NC marked)

OSPI = "Office of Superintendent of Public Instruction (OSPI), State of Washington"
OSPI_SITE_INFO = "https://ospi.k12.wa.us/ospi-site-information"
OSPI_SITE_TEXT = r"content by the Office of Superintendent of Public Instruction on this site is licensed under a " \
                 r"Creative Commons Attribution License"
OSPI_FILES = "https://ospi.k12.wa.us/sites/default/files"
STI = ("https://ospi.k12.wa.us/student-success/resources-subject-area/"
       "john-mccoy-lulilas-time-immemorial-tribal-sovereignty-washington-state")
STI_TEXT = r"Since Time Immemorial: Tribal Sovereignty in Washington State.{0,200}licensed under a Creative Commons " \
           r"Attribution 4\.0 International License"
CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
CC_BY_3 = "https://creativecommons.org/licenses/by/3.0/"
CC_BY_NC_4 = "https://creativecommons.org/licenses/by-nc/4.0/"


def _ospi_pdf(name, title, subject, path, description, licence_page=OSPI_SITE_INFO, licence_text=OSPI_SITE_TEXT,
              pdf_licence_text=""):
    """One OSPI PDF (CC BY 4.0 by its own line or OSPI's site-wide line)."""
    return dict(group=GROUP, name=name, title=title, subject=subject, publisher=OSPI, country="United States",
                region="Washington", licence="CC BY 4.0", licence_url=CC_BY_4, level="school",
                pdf=f"{OSPI_FILES}/{path}", page=licence_page, licence_page=licence_page, licence_text=licence_text,
                pdf_licence_text=pdf_licence_text, description=description,
                notice="By the Office of Superintendent of Public Instruction (Washington), CC BY 4.0. These learning "
                       "standards are written for Washington schools; logos and trademarks belong to their owners.")


UTAH_MSM = "https://www.uen.org/emedia/resources/MSM"
UTAH_TEXT = r"Creative\s+Commons\s+Attribution\s+License|Licensed\s+under\s+Creative\s+Commons,\s*cc-by"


def _utah(name, grade, file, kind, description):
    """One complete volume of the Utah Middle School Math Project (CC BY 3.0, checked in the PDF at every build)."""
    return dict(group=GROUP, name=name, title=f"Utah Middle School Math Project, Grade {grade}: {kind}",
                subject="Mathematics, middle school", grades=str(grade),
                publisher="University of Utah Middle School Math Project with the Utah State Office of Education",
                country="United States", region="Utah", licence="CC BY 3.0", licence_url=CC_BY_3, level="school",
                pdf=f"{UTAH_MSM}/{file}", page=f"{UTAH_MSM}/{file}", pdf_licence_text=UTAH_TEXT,
                description=description,
                notice="Utah Middle School Math Project, licensed under the Creative Commons Attribution License (CC BY "
                       "3.0), as printed in the book. Written for the Utah Core Standards (the Common Core).")


MA_IH = "https://www.doe.mass.edu/investigatinghistory/curriculum"
MA_TEXT = r"Creative\s+Commons\s+Attribution-NonCommercial\s+4"


def _ma(name, file, title, description):
    """One Investigating History PDF of the Massachusetts DESE (CC BY-NC 4.0: personal use only)."""
    return dict(group=GROUP, name=name, title=f"Investigating History (Massachusetts DESE): {title}",
                subject="History and social science, grades 3-7", grades="3-7",
                publisher="Massachusetts Department of Elementary and Secondary Education", country="United States",
                region="Massachusetts", licence="CC BY-NC 4.0", licence_url=CC_BY_NC_4, personal_use=True,
                level="school", pdf=f"{MA_IH}/{file}", page="https://www.doe.mass.edu/investigatinghistory/",
                pdf_licence_text=MA_TEXT, description=description + " Personal use only (CC BY-NC 4.0).",
                notice="From the Massachusetts Department of Elementary and Secondary Education: its original content "
                       "is licensed CC BY-NC 4.0 (not for commercial use; personal use only here). Pictures and other "
                       "third-party content keep their own terms.")


PDFS = [
    _ospi_pdf("wa_social_studies_standards", "Washington K-12 Social Studies Learning Standards (OSPI, 2019)",
              "Social studies standards", "2023-08/ospi_socstudies_standards_2019.pdf",
              "Washington's K-12 learning standards for social studies: civics, economics, geography, history and "
              "social studies skills, grade by grade, with the Since Time Immemorial tribal sovereignty links.",
              pdf_licence_text=r"Creative\s+Commons\s+Attribution"),
    _ospi_pdf("wa_sel_standards", "Washington Social Emotional Learning Standards, Benchmarks and Indicators (OSPI)",
              "Social and emotional learning", "2023-08/selstandardsbenchmarksindicatorslongform_0.pdf",
              "Washington's six social-emotional learning standards (self-awareness, self-management, self-efficacy, "
              "social awareness, social management, social engagement) with benchmarks and indicators by grade band."),
    _ospi_pdf("wa_environmental_sustainability_standards", "Washington K-12 Environmental and Sustainability "
              "Learning Standards (OSPI)", "Environmental and sustainability education", "2023-08/esestandards.pdf",
              "Washington's learning standards for environmental and sustainability education: ecological, social and "
              "economic systems, and sustainability and civic responsibility, by grade band."),
    _utah("utah_math_7_workbook", 7, "7-Student-Workbook-Complete.pdf", "Student Workbook",
          "The grade 7 student workbook, every chapter, from Chapter 1 (probability, percent and rational number "
          "equivalence) to geometric figures and scale drawings, real-world equations and inequalities, probability "
          "and statistics, and geometry."),
    _utah("utah_math_7_foundations", 7, "7-Mathematical-Foundations-Complete.pdf", "Mathematical Foundations",
          "The grade 7 teacher's book, Mathematical Foundations: the mathematics behind each chapter of the student "
          "workbook, explained for the teacher or parent."),
    _utah("utah_math_8_workbook", 8, "8-Student-Workbook-Complete.pdf", "Student Workbook",
          "The grade 8 student workbook, every chapter: linear equations in one variable, exploring linear "
          "relations, representations of a line, simultaneous linear equations, functions, statistics, rational and "
          "irrational numbers, integer exponents and scientific notation, and the chapters after them."),
    _utah("utah_math_8_foundations", 8, "8-Mathematical-Foundations-Complete.pdf", "Mathematical Foundations",
          "The grade 8 teacher's book, Mathematical Foundations: the mathematics behind each chapter of the student "
          "workbook, explained for the teacher or parent."),
    _ma("ma_investigating_history_guidebook", "curriculum-guidebook.pdf", "Curriculum Guidebook",
        "The guidebook to Investigating History, the state's history and social science curriculum for grades 3 to "
        "7."),
    _ma("ma_investigating_history_grade_4", "g4-course-overview.pdf", "Grade 4 Course Overview",
        "The grade 4 course, North American Geography, History, and Peoples: its overview (June 2026)."),
    _ma("ma_investigating_history_grade_6", "g6-course-guidebook.pdf", "Grade 6 Course Overview",
        "The grade 6 course, World Geography and Ancient Civilizations I: its overview (June 2025)."),
    _ma("ma_investigating_history_grade_7", "g7-course-guidebook.pdf", "Grade 7 Course Overview",
        "The grade 7 course, World Geography and Ancient Civilizations II: its overview (June 2025)."),
]

LEVEL_PAGES = ["early-learning-curriculum", "elementary-curriculum", "middle-school-curriculum",
               "high-school-curriculum"]


def sti_parts(cache=None):
    """[(part title, PDF address, unit page)] of Since Time Immemorial: each level page's unit pages (in the order
    the level page lists them), and on each unit page the PDFs whose link says "Curriculum" or "Level" (its lesson
    plans), each once. A level page with no unit pages gives its own curriculum PDFs."""
    import build_textbooks as B
    parts, seen = [], set()
    for level in LEVEL_PAGES:
        level_url = f"{STI}/{level}"
        if not B.allowed_by_robots(level_url, cache):
            continue
        page = B.fetch(level_url, cache)
        units = list(dict.fromkeys(
            "https://ospi.k12.wa.us" + h for h in re.findall(r'href="(/student-success/resources-subject-area/'
                                                              r'john-mccoy[^"#?]*/' + re.escape(level) + r'/[^"#?]+)"',
                                                              page)))
        for unit_url in units or [level_url]:
            unit = page if unit_url == level_url else B.fetch(unit_url, cache)
            name = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", (re.search(r"<h1[^>]*>(.*?)</h1>", unit, re.S)
                                                                    or [None, unit_url.rsplit("/", 1)[-1]])[1])).split())
            main = (re.search(r"(?s)<main\b.*?</main>", unit) or [unit])[0]
            for href, words in re.findall(r'(?s)<a[^>]+href="([^"]+\.pdf)"[^>]*>(.*?)</a>', main):
                words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", words)).split())
                if not re.search(r"(?i)curriculum|level\s*\d", words) or re.search(r"-sv\.pdf$", href):
                    continue                      # (the "-sv" files are Spanish versions of the same lessons)
                pdf = href if href.startswith("http") else "https://ospi.k12.wa.us" + href
                if pdf not in seen:
                    seen.add(pdf)
                    parts.append((f"{name}: {words}", pdf, unit_url))
    return parts


STI_ENTRY = dict(group=GROUP, name="tstate_wa_since_time_immemorial",
                 title="Since Time Immemorial: Tribal Sovereignty in Washington State (OSPI curriculum)",
                 subject="Tribal history, sovereignty and government (Washington State)", publisher=OSPI + ", in "
                 "partnership with the Federally Recognized Tribes in Washington State", country="United States",
                 region="Washington", licence="CC BY 4.0", licence_url=CC_BY_4, level="school", source=STI,
                 licence_page=STI, licence_text=STI_TEXT,
                 description="John McCoy (lulilas) Since Time Immemorial: Washington's curriculum on tribal history, "
                             "culture, sovereignty and government, made with the state's federally recognized tribes: "
                             "every unit's lesson plans for early learning, elementary (US and Washington State "
                             "history), middle school and high school (US history and contemporary world problems).",
                 notice="\"Since Time Immemorial: Tribal Sovereignty in Washington State\" by the Office of "
                        "Superintendent of Public Instruction in partnership with the Federally Recognized Tribes in "
                        "Washington State is licensed under a Creative Commons Attribution 4.0 International License. "
                        "OSPI asks that any adaptation be made with care so as not to introduce cultural bias, that "
                        "substantive changes be noted and the work re-titled. Material with another licence is marked "
                        "next to it in the lessons.")


def sti_book(name, work, cache=None, left_out=None, limit=None):
    """The Since Time Immemorial book: every unit's curriculum PDFs, read one after another (pdf_set)."""
    import pdf_set
    left_out = left_out if left_out is not None else []
    parts = sti_parts(cache)
    if not parts:
        left_out.append({"title": STI_ENTRY["title"], "reason": "No curriculum PDF was found on the unit pages."})
        return None
    return pdf_set.pdf_set_book(STI_ENTRY, parts, work, cache, left_out, limit)


# ====================================================================== the homeschooling laws (official texts)

def law_text(url, cache=None):
    """(title, body HTML) of one official statute or rule address: an HTML page (state_laws.html_chapter) or a PDF
    (state_laws.pdf_chapter)."""
    import state_laws as SL
    if re.search(r"\.pdf($|\?)", url, re.I):
        return SL.pdf_chapter(url, cache)
    return SL.html_chapter(url, cache)


def laws_book(name, work, cache=None, left_out=None, limit=None):
    """The homeschooling laws of one region (name "homeschool_laws:<region>"): one page per state with an official
    address, holding every address's text in turn; a site that refuses programs or AI readers, or cannot be read,
    is said in left_out (the index still links the state's page)."""
    import build_textbooks as B
    import directory_sources as D
    left_out = left_out if left_out is not None else []
    region = name.split(":", 1)[1]
    book = K.new_book(f"tstate_homeschool_laws_{region}", f"Homeschooling laws: {REGIONS[region]} (official texts)",
                      "Homeschooling law", GROUP, "The states' legislatures and education agencies (official sites)",
                      STATE_LAW, STATE_LAW_URL, "https://github.com/mark-getbraille/toolkit-models",
                      f"The homeschooling statutes and rules of the {REGIONS[region]} region, one page per state, read "
                      "in full from each legislature's or education agency's official site, with the citation and "
                      "the agency's page. States whose official code is only on a publisher's site have no page "
                      "here: tstate:index links their agency's page.", LAW_NOTE, country="United States",
                      changes="each official page's text, without its menus, one page per state")
    for s in [s for s in STATES if s["region"] == region and s["statutes"]]:
        if limit and len(book.pages) >= limit:
            break
        parts = [f"<p>Law: {B.esc(s['law'])}. The education agency's page: "
                 f'<a href="{B.esc(s["page"])}">{B.esc(s["page"])}</a>.</p>']
        for url in s["statutes"]:
            if not B.allowed_by_robots(url, cache) or D.ai_refused(url, cache):
                left_out.append({"title": f"{s['name']}: {url}", "reason": "The site's robots.txt does not allow "
                                 "reading it (or shuts out AI readers).", "url": url})
                continue
            try:
                title, body = law_text(url, cache)
            except Exception as e:  # noqa: BLE001 - said in left_out, the other states are still read
                left_out.append({"title": f"{s['name']}: {url}", "reason": f"It could not be read ({e}).", "url": url})
                continue
            parts.append(f'<h2>{B.esc(title)}</h2><p>From <a href="{B.esc(url)}">{B.esc(url)}</a>.</p>{body}')
        if len(parts) > 1:
            book.pages.append(B.Page(f"{s['key']}", s["name"], "".join(parts), len(book.pages) + 1, REGIONS[region]))
    book.published = ""
    return book if book.pages else None


def laws_sign(name):
    """The weekly sign of a region's law book: the addresses read (the texts change when the laws do; the build each
    month or on request reads them again)."""
    region = name.split(":", 1)[1]
    return K.sha([(s["key"], s["statutes"]) for s in STATES if s["region"] == region])


# ====================================================================== the index (the state table)

def found_line(kind, words, where):
    """One finding as HTML: its result words, what it is, and its key or address."""
    import build_textbooks as B
    label = {"built": "Open, built here", "personal": "Personal use only, built here", "library": "In the library",
             "link": "Link-only", "none": "Nothing open found"}[kind]
    tail = ""
    if where.startswith("http"):
        tail = f' <a href="{B.esc(where)}">{B.esc(where)}</a>'
    elif where:
        tail = f" (key {B.esc(where)})"
    return f"<li>{label}: {B.esc(words)}{tail}</li>"


def state_html(s):
    """One state's section of the index."""
    import build_textbooks as B
    statutes = "".join(f'<li><a href="{B.esc(u)}">{B.esc(u)}</a></li>' for u in s["statutes"])
    return (f"<h2>{B.esc(s['name'])}</h2>"
            f"<p>Homeschooling law: {B.esc(s['law'])}.</p>"
            f'<p>The education agency\'s page: <a href="{B.esc(s["page"])}">{B.esc(s["page"])}</a>. '
            f"{B.esc(s['says'])}</p>"
            + (f"<p>Official texts read into the law book (key tstate:homeschool_laws:{s['region']}):</p>"
               f"<ul>{statutes}</ul>" if statutes else
               "<p>No official text is read into the law book (the code is only on a publisher's site, or no "
               "official address was found): open the agency's page.</p>")
            + f"<p>Open teaching materials: {B.esc(RESULTS[s['result']])}.</p>"
            + "<ul>" + "".join(found_line(*f) for f in s["found"]) + "</ul>")


def summary_rows():
    """[(state, region, law, result)] of the table, A to Z."""
    return [(s["name"], REGIONS[s["region"]], s["law"], RESULTS[s["result"]])
            for s in sorted(STATES, key=lambda s: s["name"])]


def index_book(name, work, cache=None, left_out=None, limit=None):
    """tstate:index: a summary page with the whole table, then one page per region with each state's section."""
    import build_textbooks as B
    book = K.new_book("tstate_index", "Homeschooling and open teaching materials, state by state",
                      "Homeschooling law and state teaching materials", GROUP,
                      "Digital Accessibility Toolkit (an index of the library)", "CC0 1.0 (facts and links)",
                      K.CC0_URL, "https://github.com/mark-getbraille/toolkit-models",
                      "For each of the 50 states, the District of Columbia and the US territories: the homeschooling "
                      "law with the education agency's official page, and the openly licensed teaching materials the "
                      "state publishes, with what the search found.",
                      "Facts and links only (CC0), as found on 23 November 2026. Laws and pages change: check the "
                      "official page. " + LAW_NOTE, country="United States",
                      changes="an index written for the toolkit")
    counts = {}
    for s in STATES:
        counts[s["result"]] = counts.get(s["result"], 0) + 1
    intro = (f"<p>{len(STATES)} jurisdictions: the 50 states, the District of Columbia and "
             f"{sum(1 for s in STATES if s['region'] == 'territories')} territories. What the search for each state's "
             "own openly licensed teaching materials found: "
             + "; ".join(f"{RESULTS[k]}: {counts[k]}" for k in RESULTS if k in counts) + ".</p>"
             "<p>Open means CC0, public domain or CC BY (built here). Share-alike and non-commercial materials are "
             "personal use; copyrighted or unlicensed ones are link-only (open them yourself or fetch them with "
             "Program Downloader). A state government's works are not public domain just because a state made them "
             "(only federal works are); each was checked for its own licence.</p>")
    book.pages.append(B.Page("summary", "The whole table", intro + K.rows_table(summary_rows(), (
        "State", "Region", "Homeschooling law", "Open teaching materials")), 1, ""))
    for number, (region, words) in enumerate(REGIONS.items(), 2):
        if limit and len(book.pages) >= limit:
            break
        states = sorted((s for s in STATES if s["region"] == region), key=lambda s: s["name"])
        book.pages.append(B.Page(f"region-{region}", words, "".join(state_html(s) for s in states), number, ""))
    book.published = ""
    return book


def index_sign(name):
    """The weekly sign of the index: a fingerprint of the table."""
    return K.sha(STATES)


# ====================================================================== keys and request words

def curriculum_keys(region=None):
    """The curriculum books' keys (of one region's states when region is given)."""
    region_of = {"wa_": "west", "utah_": "west", "ma_": "northeast"}
    keys = [f"{PREFIX}:{p['name']}" for p in PDFS] + [f"{PREFIX}:wa_since_time_immemorial"]
    if region:
        keys = [k for k in keys if next((r for start, r in region_of.items() if k.split(":", 1)[1].startswith(start)),
                                        None) == region]
    return keys


def law_regions():
    """The regions with at least one official text to read (the territories have none yet: their row in the index
    links the agency's page)."""
    return [r for r in REGIONS if any(s["statutes"] for s in STATES if s["region"] == r)]


def law_keys(region=None):
    """The law books' keys."""
    return [f"{PREFIX}:homeschool_laws:{r}" for r in law_regions() if region in (None, r)]


WORDS = {"tstate-laws": lambda: [f"{PREFIX}:index"] + law_keys(),
         "tstate-curriculum": lambda: [f"{PREFIX}:index"] + curriculum_keys(),
         "teach-us": lambda: [f"{PREFIX}:index"] + law_keys() + curriculum_keys()}
WORDS.update({f"tstate-{r}": (lambda r=r: [f"{PREFIX}:index"] + law_keys(r) + curriculum_keys(r)) for r in REGIONS})

COLLECTION = K.Collection(PREFIX, GROUP, words=WORDS, pdfs=PDFS,
                          makers={"index": (index_book, index_sign), "homeschool_laws": (laws_book, laws_sign),
                                  "wa_since_time_immemorial": (sti_book, lambda name: K.sha(STI, LEVEL_PAGES))},
                          pieces={"homeschool_laws": law_regions})

LICENCE_LINES = {
    "tstate_laws": "State statutes and agency rules: not under copyright (the government edicts doctrine, Georgia v. "
                   "Public.Resource.Org, 590 U.S. 255 (2020)); read only from official legislature and agency sites, "
                   "robots.txt asked at every build.",
    "tstate_ospi": "ospi.k12.wa.us/ospi-site-information (checked 2026-11-23): \"Except where otherwise noted, content "
                   "by the Office of Superintendent of Public Instruction on this site is licensed under a Creative "
                   "Commons Attribution License\"; the Since Time Immemorial page: \"licensed under a Creative Commons "
                   "Attribution 4.0 International License\"; the social studies standards PDF prints the same.",
    "tstate_utah": "Each Utah Middle School Math Project PDF (checked 2026-11-23 and at every build): \"This work is "
                   "published under the Creative Commons Attribution License (\"CC BY\") ... "
                   "creativecommons.org/licenses/by/3.0/\". www.uen.org's robots.txt allows /emedia/.",
    "tstate_ma": "Each Investigating History PDF (checked 2026-11-23 and at every build): \"licensed under a Creative "
                 "Commons Attribution-NonCommercial 4.0 International License\": personal use only. "
                 "www.doe.mass.edu's robots.txt allows /investigatinghistory/ (crawl delay 15 seconds).",
    "tstate_index": "The state table (tstate:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    (f"{s['name']}: {words.split(':')[0].split(' (')[0][:120]}", f"Link-only. {words} Index: {where}")
    for s in STATES for kind, words, where in s["found"] if kind == "link"
] + [
    ("US Department of Education: State Regulation of Private and Home Schools (state by state) and its homeschool "
     "comparison chart", "Public domain (a federal work), but www.ed.gov answers programs \"403 Forbidden\" (checked "
     "2026-11-23), and the Wayback Machine could not be reached from the build machine to pin copies. Link-only. "
     "Index: https://www.ed.gov/birth-grade-12-education/education-choice/state-regulation-of-private-and-home-schools"),
    ("OER Commons state hubs (GoOpen CT, #GoOpenNC, Missouri, Colorado, Nebraska, GoOpen USVI and others)",
     "oercommons.org answers programs \"403 Forbidden\" (checked 2026-11-23); each item has its own licence. "
     "Link-only. Index: https://oercommons.org/hubs"),
    ("State statutes hosted only by publishers (Alabama, Alaska, Colorado, Georgia, Indiana, Kentucky, Mississippi, "
     "New Jersey, New Mexico, Tennessee, Wyoming and others)", "The official code is on LexisNexis or another "
     "publisher's site whose terms forbid copying, or on a site that needs JavaScript; the state's agency page is "
     "linked in tstate:index instead. Index: https://www.ed.gov/birth-grade-12-education/education-choice/state-regulation-of-private-and-home-schools"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
