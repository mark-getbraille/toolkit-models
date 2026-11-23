"""More education for the reference library, in the group "Teaching and homeschooling" (group key "k12", the
top-level section of 23 November 2026; keys unchanged). First asked for by the owner on 2026-11-22
(flesh out education; a sibling of education_help.py, edu:). Keys: edumore:<name>. Request word: education-more (every
book here).

The Department of Education's own sites refuse programs (education_help.py's NOT_INCLUDED: ed.gov, studentaid.gov,
LINCS), so its booklets were looked for on govinfo.gov first and the Internet Archive second:
  - govinfo.gov: edumore:govinfo_education_publications is a SIGN-UP ENTRY (govinfo_kit.govinfo_search_maker): with
    the owner's free api.data.gov key in GOVINFO_API_KEY it searches govinfo's agency publications (GOVPUB) for the
    Department of Education's booklets for parents and students and reads each one's public PDF; without the key the
    manifest says where to sign up;
  - the Internet Archive: the ERIC copies (the Department's own education library, ERIC, deposited on the Internet
    Archive) of the Department's booklets, read IN FULL, each checked at every build to print "Department of
    Education" or "National Institute for Literacy" on its front pages (pdf_licence_text):
      the Helping Your Child series for parents: Helping Your Preschool Child, Helping Your Child Become a Reader,
      Learn Mathematics, Learn Science, Learn History, Learn Geography, Become a Responsible Citizen, with
      Homework, and through Early Adolescence; Put Reading First: the parent guide (National Institute for
      Literacy); A Guide to the Individualized Education Program (the IEP, under IDEA); and Learning to Achieve, a
      guide to teaching adults with learning disabilities (adult education);
    and the 2026-27 FAFSA form with its instructions, read from the Wayback Machine's exact copy of studentaid.gov's
    PDF (studentaid.gov refuses programs);
  - old education classics published before 1931, each marked as historical (OLD_EDU_NOTE): John Dewey's Democracy
    and Education (1916), How We Think (1910) and The School and Society (1900), William James's Talks to Teachers on
    Psychology (1899), Maria Montessori's The Montessori Method (1912), and the old study-skills book How to Study
    and Teaching How to Study (Frank McMurry, 1909).

Already in the library and not repeated: education_help.py (edu:: the Federal Student Aid Handbook, Apprenticeship.gov,
Job Corps); OpenStax College Success, with study skills, note taking and test taking (osbooks:college-success-bundle,
pinned to its last CC BY 4.0 commit); LibreTexts' study-skills and learning books in the open courses (opencourses,
course:libretexts:*); IDEA itself and the parent centres' guides (parent:cpir_parent_guides); IRS Publication 970.

Not built (NOT_INCLUDED): GED and HiSET preparation (copyright; no openly licensed GED course a program may read was
found), the FAFSA guides before FAFSA Simplification (out of date), the Department's booklets whose ERIC copy does not
say who published them, and the Spanish editions (not chosen yet).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
the old books are public domain as published before 1931 (the year checked on the Internet Archive's record at every
build).

Run from the repository's folder:
  python3 textbooks/education_more.py edumore:ed_helping_your_child_become_a_reader --out build/textbooks --limit 3
  python3 textbooks/education_more.py --list education-more
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import education_help as EDU  # noqa: E402
import govinfo_kit as GK  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = EDU.GROUP                      # "k12" ("Teaching and homeschooling"): the same group as education_help.py
GROUPS = dict(EDU.GROUPS)              # {} (the group is named in sources.GROUPS)
LEGAL = EDU.LEGAL

# What is said in every old book's description ("{year}" is filled in): it is marked as historical.
OLD_EDU_NOTE = ("Published in {year}: a historical book on education, kept for its ideas and its history. Its "
                "psychology, its schools and its views of children, of girls and boys and of disabled children are "
                "those of its time; much has been learned since, and some of what it says is outdated.")

ED = "US Department of Education"
ED_NOTICE = ("A work of the US government (public domain), read from its copy in ERIC, the Department of Education's "
             "education library, on the Internet Archive, because ed.gov refuses programs. Its front pages print the "
             "publisher (checked at every build). Some telephone numbers, web addresses and programmes it names may "
             "have changed since it was printed.")
ED_FRONT = r"Department\s+of\s+Education|National\s+Institute\s+for\s+Literacy"


def _ed(name, title, subject, archive, published, description, publisher=ED, notice=""):
    """One Department of Education booklet from its ERIC copy on the Internet Archive."""
    return K.us_pdf(GROUP, name=f"ed_{name}", title=title, subject=subject, publisher=publisher, archive=archive,
                    published=published, pdf_licence_text=ED_FRONT,
                    version=f"{published} edition (ERIC copy, Internet Archive item {archive})",
                    description=description, notice=ED_NOTICE + (" " + notice if notice else ""))


PDFS = [
    _ed("helping_your_preschool_child", "Helping Your Preschool Child (US Department of Education, 2005)",
        "Parents: learning from birth to age 5", "ERIC_ED498949", "2005",
        "The Department of Education's booklet for parents of children from birth to age 5: how young children "
        "learn, and everyday activities for language, reading readiness, numbers, play and getting ready for "
        "school."),
    _ed("helping_your_child_become_a_reader", "Helping Your Child Become a Reader (US Department of Education, "
        "2002)", "Parents: reading", "ERIC_ED468665", "2002",
        "The Department of Education's booklet for parents of children from birth to age 6: talking, reading "
        "aloud, learning about print and sounds, and activities that help a child become a reader, with signs of "
        "reading problems."),
    _ed("put_reading_first_parent_guide", "Put Reading First: Helping Your Child Learn to Read, a Parent Guide, "
        "Preschool through Grade 3 (National Institute for Literacy, 2001)", "Parents: reading",
        "ERIC_ED508346", "2001",
        "The parent guide to the research on teaching reading (phonemic awareness, phonics, fluency, vocabulary and "
        "comprehension): what good reading teaching looks like in each grade and what parents can do at home.",
        publisher="National Institute for Literacy (with the US Department of Education)"),
    _ed("helping_your_child_learn_mathematics", "Helping Your Child Learn Mathematics (US Department of Education, "
        "2005)", "Parents: mathematics", "ERIC_ED498947", "2005",
        "The Department of Education's booklet for parents of children from preschool to grade 5: everyday "
        "activities at home, in the shop and on the move for numbers, measuring, shapes, patterns and problem "
        "solving."),
    _ed("helping_your_child_learn_science", "Helping Your Child Learn Science (US Department of Education)",
        "Parents: science", "ERIC_ED502945", "2005",
        "The Department of Education's booklet for parents of children aged 3 to 10: activities at home and in the "
        "community that build an interest in science and the habits of a scientist."),
    _ed("helping_your_child_learn_history", "Helping Your Child Learn History (US Department of Education, 2004)",
        "Parents: history", "ERIC_ED498934", "2004",
        "The Department of Education's booklet for parents of children from preschool to grade 5: activities for "
        "time and chronology, family history, holidays, stories and places that teach history."),
    _ed("helping_your_child_learn_geography", "Helping Your Child Learn Geography (US Department of Education, "
        "revised 1996)", "Parents: geography", "ERIC_ED402261", "1996",
        "The Department of Education's booklet for parents of children under 10: activities built on the five "
        "themes of geography (location, place, people and their surroundings, movement and regions)."),
    _ed("helping_your_child_become_a_responsible_citizen", "Helping Your Child Become a Responsible Citizen (US "
        "Department of Education, revised 2003)", "Parents: character and citizenship", "ERIC_ED475617", "2003",
        "The Department of Education's booklet on helping children grow in compassion, honesty, respect, "
        "responsibility, self-discipline and citizenship, with activities for children of elementary, middle and "
        "high school age."),
    _ed("helping_your_child_with_homework", "Helping Your Child with Homework (US Department of Education, 2002)",
        "Parents: homework", "ERIC_ED468288", "2002",
        "The Department of Education's booklet for parents of children in elementary and middle school: why "
        "teachers give homework, setting up a place and time, helping without doing it for them, working with "
        "teachers, and checklists."),
    _ed("helping_your_child_through_early_adolescence", "Helping Your Child through Early Adolescence (US Department "
        "of Education)", "Parents: ages 10 to 14", "ERIC_ED502925", "2005",
        "The Department of Education's booklet for parents of children aged 10 to 14: growth and changes, "
        "communicating, school, friends and peer pressure, and risks such as alcohol and drugs, with signs that a "
        "child needs help."),
    _ed("guide_to_the_individualized_education_program", "A Guide to the Individualized Education Program (US "
        "Department of Education, Office of Special Education and Rehabilitative Services, 2000)",
        "Special education: the IEP", "ERIC_ED444279", "2000",
        "The Department of Education's guide to the IEP for parents, teachers and students: the steps of special "
        "education, who is on the IEP team, what an IEP holds, the meeting, and parents' rights, under IDEA as it "
        "stood in 2000 (IDEA was reauthorised in 2004; the main steps are the same).", notice=LEGAL),
    _ed("learning_to_achieve_adults_learning_disabilities", "Learning to Achieve: A Professional's Guide to Educating "
        "Adults with Learning Disabilities (National Institute for Literacy, 2010)", "Adult education: learning "
        "disabilities", "ERIC_ED521234", "2010",
        "A guide for adult education teachers and programmes: what learning disabilities are in adults, screening, "
        "teaching reading, writing and maths to adults with learning disabilities, accommodations, the law, and "
        "moving on to work and further study.",
        publisher="National Institute for Literacy (US Department of Education partner agency)"),
]

# The FAFSA form itself (studentaid.gov refuses programs): the Wayback Machine's exact copy of the official PDF.
FAFSA = "https://studentaid.gov/sites/default/files/2026-27-fafsa-form.pdf"
FAFSA_STAMP = "20261012074806"
PDFS.append(K.us_pdf(
    GROUP, name="fafsa_form_2026_27", title="Free Application for Federal Student Aid (FAFSA), 2026-27, with its "
    "instructions (US Department of Education)", subject="Paying for college: the FAFSA form",
    publisher="US Department of Education, Federal Student Aid", pdf=GK.capture(FAFSA_STAMP, FAFSA),
    page=f"{GK.WAYBACK}/{FAFSA_STAMP}/{FAFSA}", published="2026",
    description="The 2026-27 FAFSA form as a PDF, with its questions and instructions: who counts as a contributor, "
                "student and parent information, financial information, signing, and the deadlines. Most people "
                "fill it in online at studentaid.gov; the PDF shows every question in advance.",
    notice=f"A work of the US Department of Education (public domain), read from the Wayback Machine's exact copy of "
           f"the official PDF ({FAFSA}, captured {GK.stamp_date(FAFSA_STAMP)}) because studentaid.gov refuses "
           f"programs. Fill in the FAFSA for the year you need at studentaid.gov. {LEGAL}",
    version=f"the official PDF as the Wayback Machine captured it on {GK.stamp_date(FAFSA_STAMP)}"))


def _old(name, title, subject, publisher, archive, year, description, country="United States"):
    """One old education classic of the Internet Archive (old_ia_books.old_book), marked as historical."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=OLD_EDU_NOTE,
                    country=country)


PDFS += [
    _old("dewey_democracy_and_education_1916", "Democracy and Education: An Introduction to the Philosophy of "
         "Education (John Dewey, 1916)", "Education: philosophy", "John Dewey (Macmillan)",
         "democracyeducati1916dewe", 1916,
         "John Dewey's best-known book on education: education as growth and as a social process, interest and "
         "discipline, thinking, subject matter, and education in a democracy."),
    _old("dewey_how_we_think_1910", "How We Think (John Dewey, 1910)", "Education: thinking and learning",
         "John Dewey (D. C. Heath)", "cu31924014133221", 1910,
         "Dewey on reflective thinking and how schools can train it: the steps of a complete act of thought, "
         "observation, ideas, judgement, and the place of language and activity in learning."),
    _old("dewey_school_and_society_1900", "The School and Society (John Dewey, 1900)", "Education: schools",
         "John Dewey (University of Chicago Press)", "schoolsocietybei00deweuoft", 1900,
         "Dewey's three lectures on the school and social progress, the school and the life of the child, and waste "
         "in education, from his Laboratory School in Chicago."),
    _old("james_talks_to_teachers_1899", "Talks to Teachers on Psychology, and to Students on Some of Life's Ideals "
         "(William James, 1899)", "Education: psychology for teachers", "William James (Henry Holt)",
         "talkstoteacherso00jameiala", 1899,
         "William James's lectures to teachers on attention, habit, memory, interest and the will, and his talks to "
         "students."),
    _old("montessori_method_1912", "The Montessori Method (Maria Montessori, translated by Anne E. George, 1912)",
         "Education: early childhood", "Maria Montessori (Frederick A. Stokes)", "in.ernet.dli.2015.150785", 1912,
         "Maria Montessori's account of her method in the Children's Houses of Rome: the prepared environment, "
         "liberty and discipline, the training of the senses, and learning to write, read and count.",
         country="Italy"),
    _old("mcmurry_how_to_study_1909", "How to Study and Teaching How to Study (Frank M. McMurry, 1909)",
         "Study skills", "Frank M. McMurry (Houghton Mifflin)", "howtostudyteachi00mcmuuoft", 1909,
         "An early book on study skills: finding the purpose of a lesson, judging what matters, organising and using "
         "ideas, memory, and how teachers can teach children to study."),
]

GOVINFO_BOOK = GK.govinfo_search_maker(
    "edumore", GROUP, "govinfo_education_publications", "Department of Education booklets from govinfo.gov",
    "Education: government booklets",
    "Booklets of the US Department of Education for parents and students found on govinfo.gov (the federal "
    "agencies' own publications): the Helping Your Child series, paying for college, special education and adult "
    "education, each read whole from its public PDF. A sign-up entry: it needs the owner's free api.data.gov key.",
    f"Works of the US government (public domain), from govinfo.gov. Older booklets may be out of date. {LEGAL}",
    "(\"helping your child\" OR \"student aid\" OR \"special education\" OR \"adult education\" OR parents) AND "
    "\"Department of Education\"", r"helping your|parent|student aid|college|special education|adult education|"
                                   r"individualized education")

MAKERS = {"govinfo_education_publications": GOVINFO_BOOK}
COLLECTION = K.Collection("edumore", GROUP, pdfs=PDFS, makers=MAKERS,
                          words={"education-more": lambda: [f"edumore:{p['name']}" for p in PDFS] +
                                 ["edumore:govinfo_education_publications"]})

LICENCE_LINES = {
    "edumore_eric": "archive.org ERIC copies (ERIC_ED<number>) of US Department of Education and National Institute "
                    "for Literacy booklets: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
                    "policies page at every build); each PDF's front pages must print the publisher (checked at "
                    "every build). archive.org's robots.txt allows the files; no AI rules (checked 2026-11-22).",
    "edumore_fafsa": "web.archive.org: the Wayback Machine's exact copy (\"id_\") of studentaid.gov's 2026-27 FAFSA "
                     "PDF, captured 2026-10-12: a work of the US government.",
    "edumore_govinfo": "api.govinfo.gov: a sign-up entry; the owner's free api.data.gov key is read from "
                       "GOVINFO_API_KEY at build time, never stored in the repository.",
    "edumore_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build). "
                         "The Montessori Method is the 1912 American translation, public domain in the US as "
                         "published before 1931.",
}

NOT_INCLUDED = [
    ("GED and HiSET preparation", "Copyright of GED Testing Service and ETS; no openly licensed GED course a program "
     "may read was found (checked again 2026-11-22). OpenStax's and LibreTexts' maths, writing, science and social "
     "studies books in the library cover the same subjects. Index: https://ged.com/"),
    ("Funding Your Education and other FAFSA guides before 2024-25", "Out of date: FAFSA Simplification rewrote the "
     "form and the aid formula for 2024-25; the 2026-27 form (edumore:fafsa_form_2026_27) and the current Federal "
     "Student Aid Handbook (edu:fsa_handbook) are built. Index: https://studentaid.gov/resources"),
    ("A Guide for Parents: Helping Your Child Succeed in School (ERIC ED583977) and the Spanish editions of the "
     "Helping Your Child series", "ED583977's ERIC record does not say who published it, so it is not built as a "
     "government work; the Spanish editions are not chosen yet. Index: https://archive.org/details/ERIC_ED583977"),
    ("OpenStax College Success and LibreTexts study skills", "Already in the library (osbooks:college-success-bundle, "
     "pinned to its last CC BY 4.0 commit; course:libretexts:*); not built twice. Index: "
     "https://openstax.org/details/books/college-success"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
