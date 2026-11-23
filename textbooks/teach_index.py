"""Teaching and homeschooling, a top-level section of the reference library (the owner's request of 23 November 2026:
"make a top level category for teaching and homeschooling, pull relevant resources into that heading"). Its group is
"Teaching and homeschooling", the school books' group under its old key "k12" (sources.GROUPS), so no book's group
key or request word changed. Keys: teach:index (the guide), teach:<name> (the homeschooling booklets below).
Request words: teach-section (the guide, the booklets and every book that moved into the section) and homeschool
(the guide, the booklets and the state-by-state laws and table of teach_states.py).

What moved into the section (keys unchanged; each module says so in its own docstring):
  - the school books, kindergarten to grade 12, already in the group: Illustrative Mathematics and Open Up (k12:),
    Utah's open science textbooks (pdf:utah_science_*), Siyavula, OpenStax's high school books, and the K-12 courses
    of courses.py (CK-12, EngageNY, Core Knowledge, Khan Academy by grade, LibreTexts K-12);
  - the education books: education_help.py (edu:, paying for college, apprenticeships, Job Corps) and
    education_more.py (edumore:, the Department of Education's Helping Your Child booklets, Put Reading First, the
    IEP guide, adult education, the FAFSA form and the old education classics of Dewey, James and Montessori), from
    "Reference, education";
  - the levelled picture books made for learning to read (Book Dash and the African Storybook, readaloud:bookdash:*,
    readaloud:african_storybook:*), from "Reference, parenting and family" (the nursery rhymes stay there);
  - the special education guides of the Center for Parent Information and Resources (parent:cpir_parent_guides);
  - the teachers' guides of oldbooks_life.py: Comstock's Handbook of Nature-Study for Teachers and Parents and seven
    NASA educator guides (olife:), from "Reference, science you can use";
  - the Internet Archive's teaching and homeschooling topic (open_catalogues.py, cat:ia:*-teaching), new here;
  - the state-by-state homeschooling laws and open state curricula (teach_states.py, tstate:).

What this module builds itself:
  - teach:index, the guide (the toolkit's own facts and links, CC0, nothing downloaded): one page per grade band and
    per subject (reading, writing, maths, science, history and civics, geography, arts, music, physical education,
    life skills, special education, and teaching blind and low-vision students with braille literacy), listing
    the books by key, the request words of whole collections (other modules' too: tworld:index and teach-world of
    teach_world.py, pc-teaching,
    lang-open, languages-gov), the picture packs and the link-only sources;
  - five homeschooling booklets of the US government, read IN FULL from ERIC's copies on the Internet Archive (each
    checked at every build to print its publisher or its public-domain line on its front pages):
      teach:nces_homeschooling_2003 and teach:nces_homeschooling_1999 (the National Center for Education
        Statistics' reports Homeschooling in the United States),
      teach:bureau_home_education_1919 (the Bureau of Education's bulletin Home Education, 1919: public domain as a
        federal work published before 1931; it is about the home education division's reading courses for adults
        and homes, and its advice is of its time),
      teach:eric_digest_home_schooling_1995 and teach:eric_digest_homeschooling_2001 (ERIC Digests by Patricia M.
        Lines, each printing "This Digest is in the public domain and may be freely reproduced").

Kept in their own sections and listed here by key or request word: history (hist:, with the Library of Congress
primary source sets for teachers), civics (civ:), geography (geo:), arts and crafts (arts:index), sheet music
(music:), literature (lit:), sports (sport:), fitness (fit:), typing (typing:), computer basics (pcb:), the blind and
low-vision collection (vision:), languages (the language helper's words), and the Peace Corps teaching manuals (the
Peace Corps helper's word pc-teaching). College textbooks stay in "Textbooks".

Not built (NOT_INCLUDED): the US Department of Education's state regulation pages and other ed.gov pages (www.ed.gov
refuses programs), the Education Commission of the States' 50-state homeschool review (copyright), and the
homeschooling advocacy sites (HSLDA, the Coalition for Responsible Home Education: copyright; teach_states.py reads
the states' own pages instead).

Run from the repository's folder:
  python3 textbooks/teach_index.py teach:index --out build/textbooks
  python3 textbooks/teach_index.py --list teach-section
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import education_help as EDU  # noqa: E402
import education_more as EDM  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import teach_states as TS  # noqa: E402

# "Teaching and homeschooling" (named in sources.GROUPS under the school books' key "k12").
GROUP = "k12"
GROUP_NAME = "Teaching and homeschooling"
GROUPS = {}

# Other helpers' request words (their collections are built in their own modules; named here so the guide points to
# them, and checked by the self-test only when the module that answers them is in this repository).
OTHER_WORDS = {
    "teach-world": "Teaching and homeschooling in Canada, the other English-speaking countries and from NGOs",
    "pc-teaching": "Peace Corps teaching manuals (teaching English, maths and science, classroom management)",
    "lang-open": "Open language-learning courses",
    "languages-gov": "Government language courses (FSI, DLI, Peace Corps)",
}

ERIC_FRONT = r"Department\s+of\s+Education|National\s+Center\s+for\s+Education\s+Statistics|Office\s+of\s+" \
             r"Educational\s+Research"
DIGEST_PD = r"public\s+domain\s+and\s+may"


def _eric(name, title, subject, archive, published, description, publisher, check=ERIC_FRONT, notice=""):
    """One US government booklet from its ERIC copy on the Internet Archive."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, pdf_licence_text=check, level="reference",
                    version=f"{published} (ERIC copy, Internet Archive item {archive})", description=description,
                    notice="A work of the US government (public domain), read from its copy in ERIC, the Department "
                           "of Education's education library, on the Internet Archive (ed.gov refuses programs). "
                           "Figures and addresses are as they were when it was printed." + (" " + notice if notice
                                                                                              else ""))


PDFS = [
    _eric("nces_homeschooling_2003", "Homeschooling in the United States: 2003 (NCES 2006-042)", "Homeschooling",
          "ERIC_ED489790", "2006", "The National Center for Education Statistics' report on homeschooling from the "
          "National Household Education Surveys of 2003: how many children were homeschooled, who they were, and the "
          "reasons parents gave.", "National Center for Education Statistics, US Department of Education"),
    _eric("nces_homeschooling_1999", "Homeschooling in the United States: 1999 (NCES 2001-033)", "Homeschooling",
          "ERIC_ED455926", "2001", "The National Center for Education Statistics' first estimate of homeschooling "
          "from the 1999 household survey: numbers, families and parents' reasons.",
          "National Center for Education Statistics, US Department of Education"),
    _eric("bureau_home_education_1919", "Home Education (Bureau of Education Bulletin, 1919, No. 3)",
          "Home education (history)", "ERIC_ED541105", "1919", "The Bureau of Education's 1919 bulletin on its home "
          "education division: reading courses and help for learning at home.",
          "Bureau of Education, US Department of the Interior", check=r"(?i)home\s+education",
          notice="Published in 1919: its ideas and programmes are of its time."),
    _eric("eric_digest_home_schooling_1995", "Home Schooling (ERIC Digest, Number 95, 1995)", "Homeschooling",
          "ERIC_ED381849", "1995", "Patricia M. Lines' short ERIC Digest on home schooling in the United States: "
          "how many families, why, the law and research, and schools working with homeschoolers.",
          "ERIC Clearinghouse on Educational Management (US Department of Education)", check=DIGEST_PD),
    _eric("eric_digest_homeschooling_2001", "Homeschooling (ERIC Digest, 2001)", "Homeschooling", "ERIC_ED457539",
          "2001", "Patricia M. Lines' 2001 ERIC Digest on homeschooling: its growth, the families, its legal status "
          "and what research said.", "ERIC Clearinghouse on Educational Management (US Department of Education)",
          check=DIGEST_PD),
]


def edumore_keys(*names):
    """("key", "edumore:<name>", title) entries of education_more.py's books (names without their "ed_" prefix where
    they have one)."""
    by_name = {e["name"]: e for e in EDM.PDFS}
    out = []
    for n in names:
        e = by_name.get(n) or by_name.get(f"ed_{n}")
        out.append(("key", f"edumore:{e['name']}", e["title"]))
    return out


def own_keys():
    """("key", "teach:<name>", title) entries of this module's booklets."""
    return [("key", f"teach:{e['name']}", e["title"]) for e in PDFS]


def sections():
    """The guide's parts: (part title, intro, entries), as practical_index.index_maker reads them."""
    return [
        ("Homeschooling: the law and getting started", "What each state requires (the law, the official page and the "
         "state's own teaching materials), with the federal reports on homeschooling.", own_keys() + [
             ("key", "tstate:index", "Homeschooling and open teaching materials, state by state (every state, DC and "
                                     "the territories)"),
             ("word", "tstate-laws", "The homeschooling statutes and rules, read from the official sites, by region"),
             ("key", "tworld:index", "Teaching and homeschooling around the world: a guide (Canada, the UK, "
                                     "Ireland, Australia, New Zealand, other countries and NGOs)"),
             ("word", "teach-world", OTHER_WORDS["teach-world"]),
             ("link", "US Department of Education: State Regulation of Private and Home Schools",
              "https://www.ed.gov/birth-grade-12-education/education-choice/state-regulation-of-private-and-home-"
              "schools", "Public domain, but ed.gov refuses programs: open it in a browser.")]),
        ("Early childhood and learning to read", "From birth to about age 8: talking, reading together, phonics and "
         "first books.", edumore_keys("helping_your_preschool_child", "helping_your_child_become_a_reader",
                                       "put_reading_first_parent_guide") + [
             ("key", "fam:cdc_act_early", "Learn the Signs. Act Early: developmental milestones (CDC)"),
             ("word", "readaloud:bookdash", "Book Dash picture books, by language (CC BY)"),
             ("word", "readaloud:african_storybook", "African Storybook stories at five reading levels, by language "
                                                      "(CC BY)"),
             ("word", "dir:storyweaver", "StoryWeaver levelled readers (Pratham Books)"),
             ("word", "dir:gdl", "The Global Digital Library's early-grade readers")]),
        ("Elementary school (kindergarten to grade 5)", "Complete courses and books for the first school years.", [
             ("word", "course:coreknowledge", "Core Knowledge: language arts and history and geography, kindergarten "
                                              "to grade 8"),
             ("word", "course:engageny", "EngageNY maths and English, pre-K to grade 12 (personal use)"),
             ("word", "course:khan", "Khan Academy maths by grade (personal use)"),
             ("word", "course:ck12", "CK-12 maths, science and English"),
             ("word", "k12:im_k5_grade_3_families", "Illustrative Mathematics K-5 family materials (one key per grade)"),
             ("key", "pdf:utah_science_kindergarten", "Utah open science textbooks, kindergarten to grade 8 and high "
                                                       "school (personal use)")]),
        ("Middle school (grades 6 to 8)", "Maths, science and social studies for grades 6 to 8.", [
             ("word", "k12:im_grade_6_math", "Illustrative Mathematics grade 6 (and grades 7 and 8: "
                                             "k12:im_grade_7_math, k12:im_grade_8_math)"),
             ("key", "tstate:utah_math_7_workbook", "Utah Middle School Math Project, grade 7 student workbook (CC BY)"),
             ("key", "tstate:utah_math_8_workbook", "Utah Middle School Math Project, grade 8 student workbook (CC BY)"),
             ("key", "pdf:utah_science_6thgrade", "Utah science, grade 6 (personal use)")]),
        ("High school (grades 9 to 12)", "Algebra, geometry, sciences and the high school textbooks.", [
             ("word", "k12:im_algebra_1", "Illustrative Mathematics Algebra 1, Geometry and Algebra 2"),
             ("word", "k12:our_hs_algebra_1", "Open Up High School Math (personal use)"),
             ("word", "siyavula", "Siyavula maths and science, grades 10 to 12"),
             ("word", "osbooks:biology-bundle", "OpenStax Biology (with Physics and Statistics, the high school "
                                                "OpenStax books in the k12 word)"),
             ("key", "pdf:utah_science_biology", "Utah high school biology (and chemistry, physics, earth and space)"),
             ("word", "k12", "Every school book, kindergarten to grade 12")]),
        ("Reading and writing", "Reading, phonics, writing, grammar and typing.", edumore_keys(
             "put_reading_first_parent_guide", "helping_your_child_become_a_reader") + [
             ("key", "lit:index", "Literature: a guide (novels, poetry, plays and myths)"),
             ("key", "typing:index", "Typing: touch typing courses and keyboard skills"),
             ("word", "writing", "Writing and business communication guides")]),
        ("Mathematics", "Maths from counting to calculus.", edumore_keys("helping_your_child_learn_mathematics") + [
             ("key", "games:dudeney_amusements_in_mathematics_1917", "Amusements in Mathematics (Dudeney, 1917): "
                                                                      "puzzles"),
             ("pack", "synthetic_formulas", "Printed maths, physics and chemistry formulas with a spoken reading"),
             ("pack", "plotqa", "Charts and their values")]),
        ("Science", "Nature study, earth and space, and the teachers' guides.", edumore_keys(
             "helping_your_child_learn_science") + [
             ("key", "olife:comstock_handbook_nature_study_1911", "Handbook of Nature-Study for Teachers and Parents "
                                                                  "(Comstock, 1911)"),
             ("key", "olife:nasa_exploring_the_moon_1994", "NASA educator guides (the Moon, astronomy, Earth from "
                                                           "space, microgravity, food, plants and Mars)"),
             ("key", "science:usgs_water_science_school", "The USGS Water Science School"),
             ("pack", "openstax_figures", "Textbook graphs, charts and diagrams with their descriptions"),
             ("pack", "chem_structures", "Chemical structure drawings")]),
        ("History and civics", "US and world history, primary sources, government and citizenship.",
         edumore_keys("helping_your_child_learn_history", "helping_your_child_become_a_responsible_citizen") + [
             ("key", "hist:index", "History: a guide by era and region"),
             ("key", "hist:loc_primary_source_sets", "Library of Congress primary source sets for teachers"),
             ("key", "civ:bens_guide", "Ben's Guide to the US Government"),
             ("key", "guide:uk_national_archives_teaching_resources", "The UK National Archives' teaching resources"),
             ("key", "tstate:wa_since_time_immemorial", "Since Time Immemorial: tribal sovereignty in Washington "
                                                        "State (CC BY)"),
             ("key", "tstate:wa_social_studies_standards", "Washington's K-12 social studies standards (CC BY)"),
             ("key", "tstate:ma_investigating_history_guidebook", "Investigating History, Massachusetts, grades 3-7 "
                                                                  "(personal use)")]),
        ("Geography", "Maps, countries and the world.", edumore_keys("helping_your_child_learn_geography") + [
             ("key", "geo:index", "Geography: a guide"),
             ("key", "geo:factbook", "The CIA World Factbook")]),
        ("Arts and music", "Art, crafts and music, with braille music.", [
             ("key", "arts:index", "Arts and crafts: a guide"),
             ("key", "music:index", "Sheet music: a guide"),
             ("key", "music:nls_braille_music", "NLS braille music catalogues and guides"),
             ("key", "pdf:braille_music_notation_1930", "Braille Music Notation (1930)")]),
        ("Physical education and health", "Exercise, sport and healthy living for children.", [
             ("key", "fit:odphp_move_your_way", "Move Your Way: physical activity for every age"),
             ("key", "sport:index", "Sports: a guide (rules, adaptive and blind sports)")]),
        ("Life skills", "Study skills, computers, money and getting ready for work.", edumore_keys(
             "helping_your_child_with_homework", "mcmurry_how_to_study_1909") + [
             ("key", "pcb:index", "Computer and phone basics"),
             ("key", "edu:fsa_handbook", "Paying for college: the Federal Student Aid Handbook"),
             ("key", "edu:apprenticeship_gov", "Apprenticeships"),
             ("key", "tstate:wa_sel_standards", "Washington's social-emotional learning standards (CC BY)")]),
        ("Special education", "Disabilities, the IEP, parents' rights and adults with learning disabilities.",
         edumore_keys("guide_to_the_individualized_education_program",
                      "learning_to_achieve_adults_learning_disabilities") + [
             ("key", "parent:cpir_parent_guides", "Parent guides to disabilities, special education and early "
                                                  "intervention (CPIR)"),
             ("key", "dis:ocr_students_postsecondary", "Students with disabilities going to college: rights and "
                                                       "responsibilities")]),
        ("Teaching blind and low-vision students, and braille literacy", "Braille, the blindness collection and the "
         "pictures the describer learns from.", [
             ("key", "vision:index", "Blind and low-vision living: a guide"),
             ("key", "pdf:iceb_rules_of_ueb_2024", "Rules of Unified English Braille (2024)"),
             ("key", "guide:nls_informational_publications", "NLS reference guides on blindness, braille and "
                                                             "disability"),
             ("key", "describe:index", "Describing pictures and video: a guide"),
             ("pack", "commons_braille_writing", "Braille, braille writers and slates"),
             ("pack", "commons_tactile_access", "Tactile graphics and tactile access"),
             ("link", "Utah Braille Core Standards, ELA K-6 (Utah State Board of Education)",
              "https://www.schools.utah.gov/specialeducation/_specialeducation/_disabilityspecific/_visualimpairment/"
              "DisabilityUtahBrailleCoreStandardsELAK6.pdf", "No licence statement: link-only."),
             ("link", "Washington State School for the Blind: resources for teaching braille",
              "https://wssb.wa.gov/sites/default/files/2024-05/WSSBMentorResource-ResourcesForTeachingBraille-"
              "051524.pdf", "Licence not checked: link-only.")]),
        ("Teaching guides and the ideas behind teaching", "How children learn and how to teach, old and new.", [
             ("key", "edumore:dewey_democracy_and_education_1916", "Democracy and Education (Dewey, 1916)"),
             ("key", "edumore:james_talks_to_teachers_1899", "Talks to Teachers on Psychology (James, 1899)"),
             ("key", "edumore:montessori_method_1912", "The Montessori Method (1912)"),
             ("word", "cat:ia:old-teaching", "Old public-domain books on teaching and homeschooling (Internet "
                                             "Archive)"),
             ("word", "pc-teaching", OTHER_WORDS["pc-teaching"])]),
        ("Languages", "Learning other languages (the language collections).", [
             ("word", "lang-open", OTHER_WORDS["lang-open"]),
             ("word", "languages-gov", OTHER_WORDS["languages-gov"])]),
    ]


SECTIONS = sections()
INDEX = X.index_maker("teach", GROUP, "Teaching and homeschooling: a guide to the library", "Teaching and "
                      "homeschooling", "A guide to the library for teaching at home and at school: homeschooling law "
                      "state by state, early childhood and reading, each grade band, every subject, special education, "
                      "and teaching blind and low-vision students with braille, with the books, request words and "
                      "picture packs of each.", SECTIONS)
MAKERS = {"index": INDEX}


def moved_keys():
    """The keys that moved into the section (see the module docstring), except the pieced ones (the picture books and
    the Internet Archive topic, asked for by their own words)."""
    import oldbooks_life as OL
    import parenting as P
    keys = [f"edu:{e['name']}" for e in EDU.GUIDES + EDU.PDFS] + [f"edumore:{e['name']}" for e in EDM.PDFS]
    keys += [f"edumore:{m}" for m in EDM.MAKERS]
    keys += [f"olife:{e['name']}" for e in OL.GUIDES + OL.PDFS if e.get("group") == GROUP]
    keys += [f"parent:{e['name']}" for e in P.GUIDES + P.PDFS if e.get("group") == GROUP]
    return keys


def section_keys():
    """teach:index, this module's booklets, the moved books and the state table (the request word teach-section)."""
    return list(dict.fromkeys(["teach:index"] + [f"teach:{e['name']}" for e in PDFS] + moved_keys() +
                              ["tstate:index"]))


def homeschool_keys():
    """The guide, the booklets, the state table and the law books (the request word homeschool)."""
    return list(dict.fromkeys(["teach:index"] + [f"teach:{e['name']}" for e in PDFS] + TS.WORDS["tstate-laws"]()))


COLLECTION = K.Collection("teach", GROUP, pdfs=PDFS, makers=MAKERS,
                          words={"teach-section": section_keys, "homeschool": homeschool_keys})

LICENCE_LINES = {
    "teach_index": "The teaching and homeschooling guide (teach:index) is the toolkit's own facts and links, CC0; each "
                   "book it lists has its own licence, shown in that book.",
    "teach_eric": "The NCES reports and the Bureau of Education bulletin are works of the US government (17 U.S.C. "
                  "105; the bulletin was also published before 1931); the ERIC Digests print \"This Digest is in the "
                  "public domain and may be freely reproduced\" (checked 2026-11-23 and at every build). "
                  "archive.org's robots.txt allows the files.",
}
NOT_INCLUDED = [
    ("Education Commission of the States: State Homeschool Policies, a 50-state review (2015)", "Copyright of the "
     "Education Commission of the States (ERIC item ED558071 is its copy). Link-only. Index: https://www.ecs.org/"),
    ("Homeschool advocacy summaries of each state's law (HSLDA, the Coalition for Responsible Home Education, "
     "commercial curriculum sites)", "Copyright of their publishers; the states' own pages and statutes are read "
     "instead (teach_states.py). Link-only. Index: https://hslda.org/legal and https://responsiblehomeschooling.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
