"""Education after school age for the reference library, in the group "Teaching and homeschooling" (group key "k12",
the top-level section of the owner's request of 23 November 2026; until then its own group "Reference, education";
the keys and the request word did not change). First asked for on 2026-11-22: paying for college, apprenticeships, job training, and where the rest is in the library. Keys:
education (every book), edu:<name>.

What this module builds, in plain words, each IN FULL (every page of the guide, read from the publisher's own site):
  - the Federal Student Aid Handbook for the current award year (AWARD_YEAR), with its Application and Verification
    Guide: the FAFSA form and how it is filled in, the Student Aid Index and Pell Grant eligibility, verification,
    special cases (independent students, foster youth, students with unusual circumstances), who is eligible for
    federal student aid (citizenship and eligible noncitizens, academic progress), the cost of attendance and how
    aid is packaged, Direct Loans, Pell Grants and campus-based aid, and returning aid after withdrawal. It is the
    Department of Education's handbook for college financial aid offices, read from fsapartners.ed.gov (studentaid.gov
    and ed.gov refuse programs);
  - Apprenticeship.gov (US Department of Labor): what registered apprenticeship is, how to find one, apprenticeships
    by industry, pre-apprenticeship, apprenticeships for young people, veterans and service members, and the
    questions people ask;
  - Job Corps (US Department of Labor): free education and career training for people 16 to 24 (high school
    diploma or equivalency, training areas, centres, who may apply, benefits, help for parents and graduates).
  Every book's notice ends with LEGAL ("General information, not legal advice; check the current rules or ask an
  accredited representative or lawyer."): aid and programme rules change every year.

Already in the library and not repeated (link by name): OpenStax College Success, with study skills, test taking,
note taking, time management and planning a career (osbooks:college-success-bundle), and the open courses of
LibreTexts, BCcampus and others for learning online (opencourses, course:); the school books (k12); CFPB's student
loan, paying-for-college and repayment guides (money:cfpb_consumer_tools); IRS Publication 970, Tax Benefits for
Education (pdf:irs_pub_970); the GI Bill and VA education benefits (dir:va_benefits); IDEA, Section 504 and the
Office for Civil Rights' pamphlet for disabled college students (dis:ocr_students_postsecondary, the IDEA law and
regulations, parent:cpir_parent_guides) and the blindness collection's education books (the vision helper's);
Social Security's Ticket to Work (work:ticket_to_work); the money and work collection's job and career books.

Not built (NOT_INCLUDED, link-only): GED and HiSET materials (copyright of their makers), StudentAid.gov, LINCS and
ed.gov (refuse programs), the College Scorecard and College Navigator (data tools), the BLS Occupational Outlook
Handbook (refuses programs), and homeschooling rules (set by each state).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build).
robots.txt of fsapartners.ed.gov, apprenticeship.gov and jobcorps.gov allows every page read; no AI rules (checked
2026-11-22).

Run from the repository's folder:
  python3 textbooks/education_help.py edu:apprenticeship_gov --out build/textbooks --limit 5
  python3 textbooks/education_help.py --list education
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

# "Teaching and homeschooling" (named in sources.GROUPS under its old key "k12", the school books' group): the one
# top-level section for teaching, school books and homeschooling (the owner's request of 23 November 2026).
GROUP = "k12"
GROUPS = {}

# The line every legal or benefits book of these collections ends with (the owner's words of 2026-11-22).
LEGAL = "General information, not legal advice; check the current rules or ask an accredited representative or lawyer."

# The award year of the Federal Student Aid Handbook built (1 July to 30 June); change it each spring when the
# Department of Education publishes the next one in full.
AWARD_YEAR = "2026-2027"
FSA = f"https://fsapartners.ed.gov/knowledge-center/fsa-handbook/{AWARD_YEAR}"

GUIDES = [
    K.guide(GROUP, "fsa_handbook", f"Federal Student Aid Handbook {AWARD_YEAR}, with the Application and "
            "Verification Guide (US Department of Education)", "Paying for college: federal student aid",
            "US Department of Education, Federal Student Aid", FSA,
            rf"^{FSA.replace('.', chr(92) + '.')}/(application-and-verification-guide|vol\d+|appendices)"
            r"(/[a-z0-9-]+)?$",
            f"The Department of Education's handbook for college financial aid offices, award year {AWARD_YEAR}, "
            "every chapter: the Application and Verification Guide (the FAFSA form and how to fill it in, the "
            "Student Aid Index and Pell Grant eligibility, verification and corrections, special cases such as "
            "independent and homeless students), student eligibility (citizenship and eligible noncitizens, Social "
            "Security numbers, academic progress, financial aid history), school eligibility and consumer "
            "information, the cost of attendance and how aid is packaged, paying out aid, Pell Grants and "
            "campus-based aid, Direct Loans (borrowing, interest, counselling), and returning aid when a student "
            "withdraws.",
            f"A work of the US Department of Education (public domain). Written for financial aid offices: students "
            f"and families apply on studentaid.gov, and each college's aid office explains its own offer. Aid "
            f"rules change every award year (this is {AWARD_YEAR}). {LEGAL}", depth=1,
            units=[(r"/application-and-verification-guide", "Applying: the FAFSA and verification"),
                   (r"/vol1", "Volume 1: Student eligibility"), (r"/vol2", "Volume 2: School eligibility"),
                   (r"/vol3", "Volume 3: Cost of attendance and packaging"), (r"/vol4", "Volume 4: Paying out aid"),
                   (r"/vol5", "Volume 5: Withdrawals and returning aid"), (r"/vol6", "Volume 6: Campus-based aid"),
                   (r"/vol7", "Volume 7: Pell Grants"), (r"/vol8", "Volume 8: Direct Loans"),
                   (r".", "Appendices")], limit=150),
]

APPRENTICE = "https://www.apprenticeship.gov"
GUIDES.append(K.guide(
    GROUP, "apprenticeship_gov", "Apprenticeships: what they are, finding one, and apprenticeships by industry "
    "(Apprenticeship.gov, US Department of Labor)", "Apprenticeships", "US Department of Labor (Apprenticeship.gov)",
    [APPRENTICE + "/career-seekers", APPRENTICE + "/help", APPRENTICE + "/apprenticeship-industries"],
    r"^https://www\.apprenticeship\.gov/(career-seekers|help|apprenticeship-industries|educators|"
    r"employers/explore-pre-apprenticeship|employers/hire-veterans|about-us)(/[a-z0-9-]+)*$",
    "Apprenticeship.gov's pages for people looking for training, every page: what registered apprenticeship is "
    "(paid work with on-the-job learning and classroom instruction, ending in a nationally recognised credential), "
    "how long programmes take, how they differ from other training, pre-apprenticeship, apprenticeships for young "
    "people and through colleges, service members and veterans (with the GI Bill), apprenticeships by industry "
    "(construction, health care, manufacturing, technology, energy and more), and the questions people ask.",
    f"From the US Department of Labor: a US government work (public domain). {LEGAL}", depth=1,
    units=[(r"/help", "Questions and answers"), (r"/apprenticeship-industries", "Apprenticeships by industry"),
           (r"/career-seekers|/educators", "For career seekers"), (r".", "More")], limit=120))

JOBCORPS = "https://www.jobcorps.gov"
GUIDES.append(K.guide(
    GROUP, "job_corps", "Job Corps: free education and career training for ages 16 to 24 (US Department of Labor)",
    "Job Corps", "US Department of Labor, Office of Job Corps", JOBCORPS + "/explore",
    r"^https://www\.jobcorps\.gov/(about|benefits|explore|faqs|i-am-a|student-graduate-resources)(/[a-z0-9-]+)*$",
    "Job Corps' pages: what Job Corps is (free residential education and career training for young people 16 to "
    "24), earning a high school diploma or equivalency, the training areas, the centres, who may apply and how, "
    "living on a centre, benefits, help for parents, graduates' resources, and the questions people ask.",
    f"From the US Department of Labor: a US government work (public domain). {LEGAL}", depth=1,
    urls=[JOBCORPS + p for p in ("/about", "/benefits", "/explore", "/explore/training-areas", "/faqs",
                                 "/i-am-a/student", "/i-am-a/parent", "/student-graduate-resources")],
    units=[(r".", "Job Corps")], limit=60))

PDFS = []

COLLECTION = K.Collection("edu", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"education": lambda: [f"edu:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "education_us": "fsapartners.ed.gov, www.apprenticeship.gov and www.jobcorps.gov: works of the US government (17 "
                    "U.S.C. 105, the line checked on govinfo.gov's policies page at every build); robots.txt allows "
                    "the pages (fsapartners.ed.gov: \"User-agent: * Allow: /\"); none names an AI company's reader or "
                    "says ai-train=no (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("GED and HiSET official study guides and practice tests", "Copyright of GED Testing Service (Pearson) and ETS; "
     "link-only. Free openly licensed GED preparation was looked for: none with a standard open licence was found "
     "that a program may read (checked 2026-11-22); OpenStax's and LibreTexts' maths and writing books in the library "
     "cover the same subjects. Index: https://ged.com/ and https://hiset.org/"),
    ("StudentAid.gov (FAFSA, loan repayment, Public Service Loan Forgiveness, the Loan Simulator)", "Public domain, "
     "but the site closes the connection without answering programs (robots.txt included, checked 2026-11-22). The "
     "Federal Student Aid Handbook is built from fsapartners.ed.gov instead (edu:fsa_handbook), and CFPB's student "
     "loan guides are in the library (money:cfpb_consumer_tools). Link-only. Index: https://studentaid.gov/"),
    ("LINCS (adult education and literacy) and the Department of Education's adult education pages (OCTAE)", "Public "
     "domain, but lincs.ed.gov and www.ed.gov refuse programs (\"403\", robots.txt included, checked 2026-11-22). "
     "Link-only. Index: https://lincs.ed.gov/ and https://www.ed.gov/about/ed-offices/octae"),
    ("College Scorecard and College Navigator", "Data tools (each college's costs, graduation rates and earnings), "
     "not books; College Navigator's robots.txt refuses programs. Link-only. Index: https://collegescorecard.ed.gov/ "
     "and https://nces.ed.gov/collegenavigator/"),
    ("BLS Occupational Outlook Handbook (training needed for each job)", "Public domain, but www.bls.gov refuses "
     "programs (\"403\", checked 2026-11-22); careers are in the money and work collection. Link-only. Index: "
     "https://www.bls.gov/ooh/"),
    ("Homeschooling rules", "Set by each state (laws and the state department of education's pages); link-only. "
     "Index: https://www.usa.gov/education"),
    ("Funding Your Education: The Guide to Federal Student Aid (ERIC copies, 2012-13 and older)", "Out of date: the "
     "FAFSA, the Student Aid Index and Pell Grant rules were rewritten for 2024-25 (FAFSA Simplification); the "
     "current handbook is built instead. Index: https://archive.org/details/ERIC_ED528610"),
    ("OpenStax College Success, LibreTexts and other open textbooks for study skills and online learning", "Already "
     "in the library (osbooks:college-success-bundle, opencourses, cat:otl); not built twice. Index: "
     "https://openstax.org/details/books/college-success"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
