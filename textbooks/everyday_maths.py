"""Everyday maths for adults for the reference library (the owner's request of 2026-11-23), in its own group
"Reference, everyday maths". Keys: emath:<name>. Request words (each well under 256 jobs):
  emath-practical       old public-domain practical, business and mental arithmetic books
  emath-measure-money   weights and measures, unit tables and the slide rule
  everyday-maths        every book of this module, with the index

What this module builds, in plain words, each IN FULL:
  - old public-domain books from the Internet Archive (published before 1931; the builder reads each item's record
    at every build), each marked as an old book:
      practical maths: Palmer's Practical Mathematics for Home Study (1919: arithmetic, geometry, algebra and
      trigonometry for the working adult), Howe's Mathematics for the Practical Man (1918), Thompson's Calculus Made
      Easy (1914), Hoyt and Peet's Everyday Arithmetic (1915), the business arithmetics of Van Tuyl (1915), Thurston
      (1917) and Kiggen (1922: interest, discounts, payroll, taxes, insurance and accounts), Milne's Mental
      Arithmetic (1897) and Evans's Rapid Calculator (1905);
      measurement: Hallock and Wade's Outlines of the Evolution of Weights and Measures and the Metric System (1906),
      Watson's British Weights and Measures (1910), Pickworth's The Slide Rule (1920) and Hoare's The Slide Rule and
      How to Use It (1896);
  - the National Bureau of Standards' Units of Weight and Measure: International (Metric) and U.S. Customary,
    Definitions and Tables of Equivalents (Miscellaneous Publication 286, 1967), a US government work, read whole
    from NIST's own copy;
  - emath:index, "Everyday maths: a guide to the library" (facts and links, CC0): every maths book here and
    elsewhere by key (the Navy and Army maths courses, the K-12 maths books, OpenStax Prealgebra, Contemporary
    Mathematics and the statistics books, the textbook catalogues, NIST's units guides and Handbook 44, the money
    guides of the CFPB and FDIC, Dudeney's puzzles, Yule's statistics) and the link-only sources with the reason.
  Every book's notice says that its maths is machine-read: fractions, formulas and tables can be garbled by the
  scanner, so check a figure against the page picture or another book before relying on it.

Already in the library and not repeated: Ray's arithmetics (tworld:), the Navy's mathematics courses (navy-rates-general)
and the Army's basic mathematics subcourses (skill:), Illustrative Mathematics and Open Up (k12), OpenStax Prealgebra,
Contemporary Mathematics, Introductory Statistics and Principles of Finance (osbooks), LibreTexts and the Open Textbook
Library (course:libretexts and cat:otl, with Business Math: A Step-by-Step Handbook, Arithmetic for College Students,
Math in Society and OpenIntro Statistics where their licences allow), NIST SP 811, SP 330 and its unit conversion
pages (science:) and Handbook 44 (pdf:nist_handbook_44_2025), the CFPB's and FDIC's money guides (money:), Helping
Your Child Learn Mathematics (edumore:), Yule's Theory of Statistics (olife:) and Dudeney's puzzles (games:).

Not built (NOT_INCLUDED, link-only): the Nemeth Code (BANA and APH copyright), the Department of Education's LINCS
adult numeracy resources (its site refuses programs), Moore's Practical Business Arithmetic and other books whose
Internet Archive record gives the year only as "c1906" (the builder cannot read a year it is not sure of, so they
are left out rather than guessed), and lending-library copies.

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); the old books by the pre-1931 year check.

Run from the repository's folder:
  python3 textbooks/everyday_maths.py emath:index --out build/textbooks
  python3 textbooks/everyday_maths.py emath:palmer_practical_mathematics_1919 --out build/textbooks --limit 3
  python3 textbooks/everyday_maths.py --list everyday-maths
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

PREFIX = "emath"
GROUP = "emath"
GROUPS = {GROUP: "Reference, everyday maths"}

# The note every book carries: maths is the scanner's weak spot.
SCANNED_MATHS = ("Its maths was machine-read from scanned pages: fractions, formulas, tables and worked sums can be "
                 "garbled, so check a figure against another book before relying on it.")
OLD_MONEY = ("Published in {year}: an old book; its prices, wages, interest rates and tax rules are of its time, "
             "but its methods of working are still sound.")
OLD_MATHS = "Published in {year}: an old book; its methods are still sound, though some words and notation are dated."


def book(name, title, subject, publisher, archive, year, description, note=OLD_MATHS, country="United States"):
    """One old maths book of the Internet Archive (published before 1931), with the machine-read maths notice."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=SCANNED_MATHS, country=country)


# ====================================================================== practical, business and mental arithmetic

PRACTICAL_PDFS = [
    book("palmer_practical_mathematics_1919", "Practical Mathematics for Home Study (Claude Irwin Palmer, 1919)",
         "Practical maths", "Claude Irwin Palmer (McGraw-Hill)", "practicalmathema00palmiala", 1919,
         "Maths for the adult studying alone: arithmetic (fractions, decimals, percentage, ratio and proportion, "
         "powers and roots), measurement of areas and volumes, the essentials of algebra and of trigonometry, "
         "logarithms and the slide rule, each with worked examples and exercises with answers."),
    book("howe_mathematics_practical_man_1918", "Mathematics for the Practical Man (George Howe, 1918 printing)",
         "Practical maths", "George Howe (D. Van Nostrand)", "cu31924031266871", 1918,
         "Algebra, geometry, trigonometry, logarithms and the first ideas of the calculus, explained simply and "
         "quickly for working people who need them."),
    book("thompson_calculus_made_easy_1914", "Calculus Made Easy (Silvanus P. Thompson, 1914)", "Practical maths: "
         "calculus", "Silvanus P. Thompson (Macmillan)", "CalculusMadeEasy", 1914,
         "The famous plain-language introduction to calculus, \"being a very-simplest introduction to those "
         "beautiful methods of reckoning\": what a small change is, rates of change, differentiating and "
         "integrating, with worked examples and exercises.", country="United Kingdom"),
    book("hoyt_peet_everyday_arithmetic_1915", "Everyday Arithmetic (Franklin S. Hoyt and Harriet E. Peet, 1915)",
         "Practical maths: arithmetic", "Franklin Sherman Hoyt and Harriet E. Peet (Houghton Mifflin)",
         "everydayarithme11peetgoog", 1915,
         "Arithmetic taught through the problems of daily life: shopping, the household, the farm, the shop and "
         "the bank, with mental exercises and written problems.", note=OLD_MONEY),
    book("van_tuyl_complete_business_arithmetic_1915", "Complete Business Arithmetic (George H. Van Tuyl, 1915)",
         "Business maths", "George H. Van Tuyl (American Book Company)", "completebusiness00vant", 1915,
         "The arithmetic of business: fast addition and checking, fractions and decimals, percentage, profit and "
         "loss, trade and cash discounts, commission, interest and bank discount, payroll, taxes, insurance, "
         "stocks and bonds, and the accounts.", note=OLD_MONEY),
    book("thurston_business_arithmetic_1917", "Business Arithmetic for Secondary Schools (E. L. Thurston, 1917)",
         "Business maths", "Ernest Lawton Thurston (Macmillan)", "businessarithmet00thurrich", 1917,
         "Business arithmetic for students going into work: short methods of calculation, bills and invoices, "
         "percentage, interest, banking, payroll, and the arithmetic of buying and selling.", note=OLD_MONEY),
    book("kiggen_practical_business_arithmetic_1922", "Practical Business Arithmetic (Helen J. Kiggen, 1922)",
         "Business maths", "Helen J. Kiggen (Macmillan)", "practicalbusines00kigguoft", 1922,
         "Arithmetic for office and shop work: quick reckoning, aliquot parts, percentage, discounts, profit and "
         "loss, interest, payrolls, and household and business accounts.", note=OLD_MONEY),
    book("milne_mental_arithmetic_1897", "A Mental Arithmetic (William J. Milne, 1897)", "Mental arithmetic",
         "William J. Milne (American Book Company)", "mentalarithmetic00milnrich", 1897,
         "Arithmetic done in the head: graded exercises in adding, subtracting, multiplying and dividing, "
         "fractions, percentage and interest, with the reasoning spoken aloud, useful for anyone who calculates "
         "without paper."),
    book("evans_rapid_calculator_1905", "The George M. Evans Rapid Calculator (George M. Evans, 1905)",
         "Mental arithmetic", "George M. Evans", "georgemevansrapi00evan", 1905,
         "Short cuts for fast calculation: quick ways to add columns, multiply and divide, square numbers, and "
         "work out interest and percentages.", note=OLD_MONEY),
]

# ====================================================================== measurement, units and the slide rule

NBS = "National Bureau of Standards (now NIST), US Department of Commerce"
MEASURE_PDFS = [
    K.us_pdf(GROUP, name="nbs_mp286_units_weight_measure_1967", title="Units of Weight and Measure: International "
             "(Metric) and U.S. Customary, Definitions and Tables of Equivalents (NBS Miscellaneous Publication 286, "
             "1967)", subject="Measurement and units", publisher=NBS,
             pdf="https://nvlpubs.nist.gov/nistpubs/Legacy/MP/nbsmiscellaneouspub286.pdf",
             page="https://nvlpubs.nist.gov/nistpubs/Legacy/MP/nbsmiscellaneouspub286.pdf", published="1967",
             version="1967 edition (NIST's own scan)",
             description="The National Bureau of Standards' tables of units: the definitions of the metric and US "
                         "customary units of length, area, volume (liquid and dry), weight and mass, and their "
                         "equivalents, with conversion tables for each kind of measure. The definitions of some "
                         "units have been refined since 1967 (the 2019 SI is in science:nist_sp330_si_2019).",
             notice=f"A work of the National Bureau of Standards (public domain). {SCANNED_MATHS}"),
    book("hallock_wade_weights_measures_1906", "Outlines of the Evolution of Weights and Measures and the Metric "
         "System (William Hallock and Herbert T. Wade, 1906)", "Measurement and units", "William Hallock and Herbert "
         "T. Wade (Macmillan)", "outlinesofevolut00halluoft", 1906,
         "Where our units came from and how they work: ancient measures, the English and US customary units, the "
         "making of the metric system, and tables of the units and their equivalents.",
         note="Published in {year}: an old book; the metric units have been redefined since (the 2019 SI)."),
    book("watson_british_weights_measures_1910", "British Weights and Measures as Described in the Laws of England "
         "(Charles Moore Watson, 1910)", "Measurement and units", "Charles Moore Watson (John Murray)",
         "britishweightsme00watsuoft", 1910,
         "The history of the British (imperial) weights and measures from Anglo-Saxon times: the yard, the pound, "
         "the gallon and the bushel, and how the US customary units grew from them.",
         note="Published in {year}: an old book; the imperial units were redefined in 1963 and later.",
         country="United Kingdom"),
    book("pickworth_slide_rule_1920", "The Slide Rule: a Practical Manual (Charles N. Pickworth, 1920 edition)",
         "Measurement and calculation: the slide rule", "Charles N. Pickworth (Emmott and Co.)", "cu31924003979105",
         1920,
         "How to use the slide rule for multiplying, dividing, proportion, squares and roots, trigonometry and "
         "logarithms, with the special rules for engineers.",
         note="Published in {year}: an old book; the slide rule has given way to the calculator, but its ideas "
              "(logarithms, estimating the answer first) still help.", country="United Kingdom"),
    book("hoare_slide_rule_1896", "The Slide Rule and How to Use It (Charles Hoare, 1896)", "Measurement and "
         "calculation: the slide rule", "Charles Hoare (Crosby Lockwood)", "sliderulehowtous00char", 1896,
         "A short guide to the slide rule: its scales, multiplying and dividing, proportions and the use of the "
         "rule in measuring and in trade.",
         note="Published in {year}: an old book; the slide rule has given way to the calculator.",
         country="United Kingdom"),
]

PDFS = PRACTICAL_PDFS + MEASURE_PDFS


def keys_of(entries):
    """The build keys of some entries of this module."""
    return [f"{PREFIX}:{e['name']}" for e in entries]


# ====================================================================== the index

INDEX_SECTIONS = [
    ("Practical and business maths", "Arithmetic for daily life, work and business, from the old books here to the "
     "open textbooks and the military maths courses.",
     [("key", k, e["title"]) for k, e in zip(keys_of(PRACTICAL_PDFS), PRACTICAL_PDFS)] +
     [("word", "osbooks:prealgebra-bundle", "OpenStax Prealgebra (whole numbers, fractions, decimals, percent, "
                                            "measurement)"),
      ("word", "osbooks:contemporary-mathematics", "OpenStax Contemporary Mathematics (money management, "
                                                    "measurement, probability, logic)"),
      ("word", "navy-rates-general", "the Navy's mathematics courses (basic maths and algebra, trigonometry, "
                                     "statistics) among its general rating books"),
      ("key", "skill:accp_qm0113_basic_mathematics_i_addition_subtraction_multipl", "Basic Mathematics 1 (Army "
                                                                                     "subcourse QM0113)"),
      ("key", "skill:accp_qm0114_basic_mathematics_ii_decimal_fractions", "Basic Mathematics 2: Decimal Fractions "
                                                                          "(Army subcourse QM0114)"),
      ("key", "skill:accp_qm0115_basic_mathematics_iii_area_and_volume", "Basic Mathematics 3: Area and Volume "
                                                                         "(Army subcourse QM0115)"),
      ("key", "skill:accp_qm0116_basic_mathematics_iv_ratio_and_proportion", "Basic Mathematics 4: Ratio and "
                                                                             "Proportion (Army subcourse QM0116)"),
      ("key", "pc:agricultural_mathematics_1981", "Agricultural Mathematics for Peace Corps Volunteers (1981)"),
      ("word", "tworld-classics", "Ray's arithmetics (1877 to 1907) among the old teaching classics"),
      ("word", "k12", "the school maths books: Illustrative Mathematics 6-8 and Open Up high school maths"),
      ("word", "course:libretexts", "LibreTexts' open textbooks, among them Business Math: A Step-by-Step Handbook "
                                    "(CC BY-NC-SA, personal use) and Arithmetic for College Students"),
      ("word", "cat:otl", "the Open Textbook Library, among them Math in Society (CC BY-SA)"),
      ("key", "edumore:ed_helping_your_child_learn_mathematics", "Helping Your Child Learn Mathematics (US "
                                                                 "Department of Education)"),
      ("key", "games:dudeney_amusements_in_mathematics_1917", "Dudeney's Amusements in Mathematics (puzzles)"),
      ("word", "biz-bookkeeping", "old bookkeeping and accounting books in the business collection")]),
    ("Measurement, units and money", "Units, conversions and the maths of money.",
     [("key", k, e["title"]) for k, e in zip(keys_of(MEASURE_PDFS), MEASURE_PDFS)] +
     [("key", "science:nist_sp811_si_guide", "NIST's guide to the metric system (SP 811), with conversion factors"),
      ("key", "science:nist_sp330_si_2019", "The International System of Units (NIST SP 330, 2019)"),
      ("key", "science:nist_unit_conversion", "NIST's unit conversion pages (cooking, length, weight, volume, "
                                              "temperature)"),
      ("key", "pdf:nist_handbook_44_2025", "NIST Handbook 44: specifications and tolerances for weighing and "
                                           "measuring devices"),
      ("key", "money:fdic_consumer", "FDIC consumer resource center and Money Smart"),
      ("key", "money:cfpb_your_money_your_goals", "Your Money, Your Goals (CFPB)"),
      ("key", "skill:usmc_mci_personal_finance_1985", "Personal Finance (Marine Corps Institute, 1985)"),
      ("word", "osbooks:principles-finance", "OpenStax Principles of Finance (time value of money, interest)"),
      ("manuals", "office_supplies", "calculators and other office supplies")]),
    ("Statistics for everyone", "Making sense of numbers, averages and charts.",
     [("key", "olife:yule_theory_of_statistics_1922", "Yule's Introduction to the Theory of Statistics (1922)"),
      ("key", "skill:accp_fi0921_basic_statistics", "Basic Statistics (Army subcourse FI0921)"),
      ("word", "osbooks:introductory-statistics-bundle", "OpenStax Introductory Statistics"),
      ("word", "osbooks:statistics", "OpenStax Statistics (high school)"),
      ("link", "OpenIntro Statistics (CC BY-SA)", "https://www.openintro.org/book/os/",
       "In the Open Textbook Library catalogue (cat:otl), built there when its host allows; otherwise fetch it "
       "yourself.")]),
    ("Braille maths", "The braille codes for maths.",
     [("link", "Nemeth Code for Mathematics and Science Notation (BANA, APH)", "https://www.brailleauthority.org/",
       "Copyright of the Braille Authority of North America and the American Printing House for the Blind: free to "
       "download for personal use, link-only."),
      ("link", "UEB technical material guidance (BANA)", "https://www.brailleauthority.org/",
       "BANA's copyright; link-only."),
      ("key", "vision:nls_services", "the National Library Service: braille and talking books, including maths "
                                     "textbooks on request")]),
]

INDEX_BOOK, INDEX_SIGN = X.index_maker(
    PREFIX, GROUP, "Everyday maths: a guide to the library", "Everyday maths for adults",
    "A guide to the library's maths books for adults: practical and business arithmetic, mental arithmetic, "
    "measurement and units, the maths of money, statistics and braille maths, with the key of each book and the "
    "sources that are links only.", INDEX_SECTIONS)

WORDS = {
    "emath-practical": lambda: keys_of(PRACTICAL_PDFS),
    "emath-measure-money": lambda: keys_of(MEASURE_PDFS),
    "everyday-maths": lambda: [f"{PREFIX}:index"] + keys_of(PDFS),
}
COLLECTION = K.Collection(PREFIX, GROUP, pdfs=PDFS, makers={"index": (INDEX_BOOK, INDEX_SIGN)}, words=WORDS)

LICENCE_LINES = {
    "emath_old_books": "archive.org (its robots.txt allows the files): books published before 1931 are in the US "
                       "public domain; the builder checks each item's year on the Internet Archive's record at every "
                       "build. Lending-library-only copies are not used.",
    "emath_nbs": "nvlpubs.nist.gov: NBS Miscellaneous Publication 286 (1967), a work of the US government (17 U.S.C. "
                 "105, checked on govinfo.gov's policies page at every build).",
    "emath_index": "The index (emath:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("Nemeth Code for Mathematics and Science Notation (BANA, APH)", "Copyright of BANA and APH; free for personal "
     "use, link-only (also in vision_living.py). No public-domain braille maths introduction from before 1931 was "
     "found on the Internet Archive (searched 2026-11-23). Index: https://www.brailleauthority.org/"),
    ("Department of Education LINCS adult numeracy resources (lincs.ed.gov)", "Federal and public domain where made by "
     "the Department, but lincs.ed.gov answers programs \"403\" (robots.txt included, checked 2026-11-23). Index: "
     "https://lincs.ed.gov/"),
    ("Moore's Practical Business Arithmetic (1906, 1915), Harvey's Essentials of Arithmetic (1914) and Bailey's "
     "American Mental Arithmetic (1892)", "Their Internet Archive records give the year only as \"c1906\" and the "
     "like, which the builder's year check cannot read, so it would refuse them; left out rather than guessed. "
     "Index: https://archive.org/details/practicalbusines00moorrich"),
    ("Business Math: A Step-by-Step Handbook (Jean-Paul Olivier, Lyryx, CC BY-NC-SA)", "Non-commercial: personal use "
     "only; it comes with the LibreTexts catalogue (course:libretexts) when its licence there allows. Index: "
     "https://lyryx.com/business-math-step-by-step/"),
    ("Financial calculators and money apps (CFPB, FDIC, Investor.gov)", "Interactive tools, not books; Investor.gov "
     "refuses programs. Index: https://www.investor.gov/financial-tools-calculators"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
