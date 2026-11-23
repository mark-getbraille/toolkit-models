"""Government language-learning books for the reference library, in the top-level section "Languages" (group
"languages", the group of languages.py), the owner's request of 23 November 2026: "Make a new top level section for
languages and find all open resources from DoD, State Department, other governments and NGOs". This module has the
governments' part (another module adds the non-profits' and open educational resources). Keys: lgov:<name>.

Request words (each at most 256 keys, sources.expand_keys):
  lgov-fsi              the State Department's Foreign Service Institute courses not already in languages.py
  lgov-dli              the Defense Language Institute's courses and its Language Survival Kits
  lgov-dli-countries    the Defense Language Institute's "Countries in Perspective" books (culture and country
                        background; kept apart so languages-gov stays under 256 keys)
  lgov-military         the War Department's Second World War language guides, phrase books and dictionaries (the
                        TM 30 series and others)
  lgov-other-gov        other governments: the Smithsonian's and the Bureau of Indian Affairs' Native American
                        dictionaries and grammars, the Navy's Chamorro dictionary, and Canada's TERMIUM Plus
                        terminology bank (Open Government Licence - Canada)
  languages-gov         all of the above except lgov-dli-countries

What this module builds, in plain words:
  - lgov:fsi:<course>: a Foreign Service Institute (US Department of State) course: its text volumes, read from the
    Internet Archive's copies with a text layer (the FSI's own items, or the ERIC microfiche copies, which the
    Department of Education's ERIC made) or, where only it has a copy with words, from fsi-languages.yojik.eu (its
    robots.txt allows every program). The AUDIO is never downloaded: every recording on the course's page at
    fsi-languages.yojik.eu is listed in the book's originals (address and size) for the owner to download himself,
    as in languages.py. US government works (17 U.S.C. 105), public domain.
  - lgov:dli:<course>: a Defense Language Institute course or Headstart program, read from the Internet Archive
    (mostly ERIC's microfiche copies). Judged at every build by the release rule for military publications
    (military_release.py, military=True): a copy that prints a restricted marking goes to the personal-use route.
    The courses checked before they were listed print no copyright stamp and no "not for general distribution"
    line in their first pages; those that do are in NOT_INCLUDED.
  - lgov:lsk:<language>: the Defense Language Institute's Language Survival Kits for one language (the basic,
    medical, civil affairs, air crew, navy, public affairs, force protection, military police and cordon and search
    guides), read from the Institute's own Field Support site (fieldsupport.dliflc.edu, robots.txt allows it):
    each phrase in English, in the Institute's spelling for English speakers, and in the language's own script. The
    weapons guides sit behind a sign-in (".../products/secure/...") and are left out; so is any part about mines or
    explosives (MINE_WORDS). One page per part of each guide.
  - lgov:cip_<country>: a "Countries in Perspective" book (geography, history, economy, society, security), the
    Institute's PDF on its Field Support site.
  - lgov:<name>: one Internet Archive PDF: the Second World War language guides, phrase books and military
    dictionaries of the War Department (military=True), and the Native American dictionaries and grammars of the
    Smithsonian Institution's Bureau of American Ethnology and the Bureau of Indian Affairs.
  - lgov:termium:<subject>: Canada's TERMIUM Plus terminology bank for one subject (English, French, and Spanish and
    Portuguese where given), from its open data files on open.canada.ca (Open Government Licence - Canada, checked
    at every build on the dataset's own record), one table row per term, alphabetical, 250 to a page.

The DLIFLC Field Support books: DLIFLC is a school of the US Department of Defense; its pages show "Copyright
DLIFLC", but works of the US government have no US copyright (17 U.S.C. 105), and www.dliflc.edu says "Information
presented on this site is considered public information and may be distributed or copied unless otherwise
specified" (DLIFLC_TEXT, checked at every build). Both facts are written in each book's notice. Its host is not a
.mil address, so the release rule is not asked; these products are published openly, without a sign-in, by the
Institute itself.

Skipped, with reasons, in NOT_INCLUDED: Rapport and the Cultural Orientation courses (sign-in), Headstart2 (an
online program, no text files), the DLI copies on fsi-languages.yojik.eu (a private mirror, not a government or
Internet Archive copy), FSI and DLI courses whose only copies are scans without a text layer, and copies that print
"not for general distribution" or a copyright stamp; the other governments' sources that were checked.

Run from the repository's folder:
  python3 textbooks/languages_gov.py lgov:fsi:twi --out build/textbooks --limit 5
  python3 textbooks/languages_gov.py --list languages-gov
"""

import csv
import datetime
import html
import io
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import languages as L  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = L.GROUP                      # "languages": the top-level section "Languages" (named in languages.py's GROUPS)
GROUPS = {}

IA = "https://archive.org"
YOJIK = "https://fsi-languages.yojik.eu/languages/FSI"
FSI = "Foreign Service Institute, US Department of State"
DLI = "Defense Language Institute, US Department of Defense"
FSI_NOTICE = ("A course of the Foreign Service Institute (US Department of State), a work of the US government "
              "(public domain). An old course: some dialogues, prices and customs are out of date, and the scanned "
              "text has the scanner's mistakes; foreign scripts may be partly missing from the text layer. Its audio "
              "recordings, where there are any, are listed as originals for you to download; they are not inside "
              "this book.")
DLI_NOTICE = ("A course of the Defense Language Institute (US Department of Defense), a work of the US government. An "
              "old course written for service members: some dialogues are about military life, and the scanned text "
              "has the scanner's mistakes; foreign scripts may be partly missing from the text layer.")


def ia(item, pattern=r"\.pdf$"):
    """A text source: the PDFs of an Internet Archive item whose names match pattern."""
    return ("ia", item, pattern)


def yj(page, pattern):
    """A text source: the PDFs linked from a course page of fsi-languages.yojik.eu whose addresses match pattern."""
    return ("page", f"{YOJIK}/{page}", pattern)


def audio(page, folder=""):
    """An audio source: the MP3 files linked from a course page of fsi-languages.yojik.eu, only those whose address
    (with its spaces) contains folder when folder is given (a page can hold several courses)."""
    return ("page", f"{YOJIK}/{page}", folder)


def fsi(key, language, title, text, sound=(), year="", description=""):
    """One FSI course record."""
    return dict(key=key, language=language, title=title, year=year, text=list(text), audio=list(sound),
                description=description, publisher=FSI)


# ====================================================================== Foreign Service Institute courses
# Every FSI course found with a text layer that languages.py does not already build (its COURSES: Spanish Basic and
# FAST, French Basic, German Basic, Italian Programmed, Brazilian Portuguese FAST, Standard Chinese, Cantonese,
# Japanese FAST, Korean, Russian FAST, Saudi Arabic, Vietnamese Basic, Hebrew, Greek). The ERIC microfiche items
# ("micro_IA...") are the Department of Education's ERIC copies, each checked: its ERIC record names the FSI as the
# institution, and its first pages print no copyright stamp.
FSI_COURSES = [
    fsi("amharic", "Amharic", "FSI Amharic Basic Course", [ia("Fsi-AmharicBasicCourse-StudentText",
        r"StudentText(_text)?\.pdf$")], [audio("fsi-amharic.html", " new/")], "1964",
        "The FSI's Amharic course in two volumes (units 1 to 60): dialogues, pronunciation, grammar notes and "
        "drills, in transcription and in the Ethiopic script."),
    fsi("bulgarian", "Bulgarian", "FSI Bulgarian Basic Course", [ia("Fsi-BulgarianBasicCourse-StudentText",
        r"StudentText\.pdf$")], [audio("fsi-bulgarian.html")], "",
        "The FSI's Bulgarian course in two volumes: dialogues, grammar and drills."),
    fsi("cambodian", "Khmer (Cambodian)", "FSI Cambodian Basic Course", [ia("Fsi-CambodianBasicCourse-StudentText",
        r"StudentText(_text)?\.pdf$")], [audio("fsi-cambodian-basic-course.html")], "1970",
        "The FSI's Cambodian (Khmer) course in two volumes, in transcription: dialogues, grammar and drills."),
    fsi("cambodian_contemporary", "Khmer (Cambodian)", "FSI Contemporary Cambodian",
        [ia("Fsi-ContemporaryCambodian-Introduction-StudentText")], [audio("fsi-cambodian-contemporary.html")], "",
        "The FSI's Contemporary Cambodian: the introduction, the grammatical sketch and the glossary."),
    fsi("chinyanja", "Chichewa (Chinyanja)", "FSI Chinyanja Basic Course", [ia("Fsi-ChinyanjaBasicCourse-StudentText",
        r"StudentText(_text)?\.pdf$")], [audio("fsi-chinyanja.html")], "1965",
        "The FSI's course in Chinyanja (Chichewa) of Malawi and Zambia: dialogues, grammar and drills."),
    fsi("finnish", "Finnish", "FSI Conversational Finnish", [ia("Fsi-ConversationalFinnish-StudentText")],
        [audio("fsi-finnish.html", "/Conversational/")], "",
        "The FSI's Conversational Finnish: the textbook and the workbook."),
    fsi("fula", "Fula (Pulaar)", "FSI Fula Basic Course", [ia("Fsi-FulaBasicCourse-StudentText")],
        [audio("fsi-fula.html")], "1965", "The FSI's course in Fula (Pulaar) of West Africa."),
    fsi("german_programmed", "German", "FSI German Programmed Introduction",
        [ia("Fsi-GermanProgrammedIntroduction-StudentText")], [audio("fsi-german-programmed-introduction-course.html")],
        "", "The FSI's self-paced programmed introduction to German."),
    fsi("german_fast", "German", "FSI German FAST Course (Familiarization and Short-Term Training)",
        [yj("fsi-german-fast.html", r"German FAST - Student Text\.pdf$")], [audio("fsi-german-fast.html")], "",
        "The FSI's short German course for everyday survival in Germany, Austria and Switzerland."),
    fsi("hausa", "Hausa", "FSI Hausa Basic Course", [ia("Fsi-HausaBasicCourse-StudentText",
        r"StudentText(_text)?\.pdf$")], [audio("fsi-hausa.html")], "1963",
        "The FSI's course in Hausa of Nigeria and Niger: dialogues, grammar and drills."),
    fsi("hindi_active", "Hindi", "FSI Hindi: An Active Introduction", [ia("Fsi-Hindi-AnActiveIntroduction",
        r"StudentText(_text)?\.pdf$")], [], "1966", "The FSI's short active introduction to spoken Hindi."),
    fsi("hindi", "Hindi", "FSI Hindi Basic Course", [ia("micro_IA41153618_0050")], [], "1960",
        "The FSI's Hindi basic course (ERIC's microfiche copy, ED 010 493)."),
    fsi("hungarian", "Hungarian", "FSI Hungarian Basic Course", [ia("Fsi-HungarianBasicCourse-StudentText",
        r"BasicCourse-Volume\d-StudentText\.pdf$")], [audio("fsi-hungarian.html", "Hungarian/Basic/")], "",
        "The FSI's Hungarian course in two volumes: dialogues, grammar and drills."),
    fsi("hungarian_reader", "Hungarian", "FSI Hungarian Graded Reader", [ia("Fsi-HungarianBasicCourse-StudentText",
        r"GradedReader-StudentText(_text)?\.pdf$")], [audio("fsi-hungarian.html", "Hungarian/Graded Reader/")], "",
        "The FSI's graded Hungarian readings, from simple to harder texts."),
    fsi("igbo", "Igbo", "FSI Igbo Basic Course", [ia("Fsi-IgboBasicCourse-StudentText", r"StudentText(_text)?\.pdf$")],
        [audio("fsi-igbo.html")], "1965", "The FSI's course in Igbo of Nigeria."),
    fsi("kirundi", "Kirundi", "FSI Kirundi Basic Course", [ia("micro_IA41153618_0036")], [audio("fsi-kirundi.html")],
        "1965", "The FSI's course in Kirundi of Burundi (ERIC's microfiche copy, ED 010 479)."),
    fsi("kituba", "Kituba", "FSI Kituba Basic Course", [ia("FSIKitubaBasicCourseStudentText", r"_text\.pdf$")],
        [audio("fsi-kituba.html")], "1963", "The FSI's course in Kituba of the Congo."),
    fsi("lao", "Lao", "FSI Lao Basic Course", [ia("fsi-lao-basic-course-student-text-volume-1", r"_text\.pdf$"),
                                                ia("fsi-lao-basic-course-volume-2", r"_text\.pdf$")],
        [audio("fsi-lao.html", "Lao/Basic/")], "1970", "The FSI's Lao course in two volumes."),
    fsi("lao_reading", "Lao", "FSI Reading Lao", [ia("fsi-reading-lao", r"_text\.pdf$")],
        [audio("fsi-lao.html", "Lao/Reading Lao/")], "1974", "The FSI's course in reading the Lao script."),
    fsi("lao_everyday", "Lao", "FSI Everyday Lao", [yj("fsi-lao.html", r"Every-day-lao/Everyday Lao\.pdf$")],
        [audio("fsi-lao.html", "Lao/Every-day-lao/")], "2014",
        "The FSI's newer short course of everyday Lao (2014)."),
    fsi("lingala", "Lingala", "FSI Lingala Basic Course", [ia("micro_IA41153618_0038")], [audio("fsi-lingala.html")],
        "1963", "The FSI's course in Lingala of the Congo (ERIC's microfiche copy, ED 010 481)."),
    fsi("luganda", "Luganda", "FSI Luganda Basic Course", [ia("micro_IA41153063_0143")], [audio("fsi-luganda.html")],
        "1968", "The FSI's course in Luganda of Uganda, made with the help of the Peace Corps (ERIC's microfiche copy, "
        "ED 024 933)."),
    fsi("more", "Moore (More)", "FSI More Basic Course", [ia("micro_IA41153663_0433")], [audio("fsi-moré.html")],
        "1966", "The FSI's course in Moore (More) of Burkina Faso (ERIC's microfiche copy, ED 012 022)."),
    fsi("persian", "Persian (Farsi)", "FSI Persian Basic Course, Units 1 to 12", [ia("micro_IA41152926_0302")], [],
        "1963", "The FSI's Persian course, units 1 to 12 (ERIC's microfiche copy, ED 053 628)."),
    fsi("polish_fast", "Polish", "FSI Polish FAST Course (Familiarization and Short-Term Training)",
        [yj("fsi-polish.html", r"Polish FAST\.pdf$")], [audio("fsi-polish.html")], "",
        "The FSI's short Polish course for everyday survival. Its cover photo is by another author, under CC BY 2.0, "
        "credited on the cover."),
    fsi("portuguese_spoken", "Portuguese (Brazilian)", "FSI Spoken Brazilian Portuguese, Units 1 to 18",
        [yj("fsi-portuguese.html", r"ED102873\.pdf$")], [], "1974",
        "The FSI's Brazilian Portuguese basic course, units 1 to 18 (ERIC ED 102 873)."),
    fsi("portuguese_from_spanish", "Portuguese (Brazilian)", "FSI From Spanish to Portuguese",
        [yj("fsi-from-spanish-to-portuguese.html", r"From Spanish to Portuguese - Student Text\.pdf$")],
        [audio("fsi-from-spanish-to-portuguese.html")], "",
        "The FSI's short book for Spanish speakers learning Portuguese: the sounds and words that differ."),
    fsi("serbo_croatian", "Serbo-Croatian", "FSI Serbo-Croatian Basic Course, Volume 1", [ia("micro_IA41153609_0050")],
        [audio("fsi-serbo-croatian.html", "/Volume 1/")], "1965",
        "The FSI's Serbo-Croatian course, units 1 to 25 (ERIC's microfiche copy, ED 013 452)."),
    fsi("shona", "Shona", "FSI Shona Basic Course", [ia("micro_IA41153663_0434")], [audio("fsi-shona.html")], "1965",
        "The FSI's course in Shona of Zimbabwe (ERIC's microfiche copy, ED 012 023)."),
    fsi("sinhala", "Sinhala", "FSI Sinhala Basic Course", [ia("micro_IA41153527_0730"), ia("micro_IA41153527_0731"),
                                                          ia("micro_IA41153527_0732")], [], "1979",
        "The FSI's Sinhala course of Sri Lanka in three modules: beginning signs and letters, general conversation, "
        "Sinhala structures (ERIC's microfiche copies, ED 192 569 to 571)."),
    fsi("swahili", "Swahili", "FSI Swahili Basic Course", [ia("fsi-swahili-basic-course-student-text",
        r"_text\.pdf$")], [audio("fsi-swahili.html", "Swahili/Basic/")], "1963", "The FSI's Swahili course."),
    fsi("swahili_active", "Swahili", "FSI Swahili: An Active Introduction, General Conversation",
        [yj("fsi-swahili.html", r"Active Introduction - General Conversation\.pdf$")],
        [audio("fsi-swahili.html", "Swahili/Active Introduction/")], "1966",
        "The FSI's short conversational introduction to Swahili, made with the help of the Peace Corps."),
    fsi("swahili_newspaper", "Swahili", "FSI An Active Introduction to Newspaper Swahili",
        [ia("micro_IA41153656_0198")], [], "1966", "The FSI's introduction to reading Swahili newspapers (ERIC's "
                                                   "microfiche copy)."),
    fsi("swedish", "Swedish", "FSI Swedish Basic Course", [ia("fsi-swedish-basic-course-student-text")],
        [audio("fsi-swedish.html")], "", "The FSI's Swedish course."),
    fsi("thai", "Thai", "FSI Thai Basic Course", [ia("Fsi-ThaiBasicCourse-StudentText",
        r"Volume\d-StudentText(_text)?\.pdf$")], [audio("fsi-thai.html")], "1970",
        "The FSI's Thai course in two volumes, in transcription."),
    fsi("thai_grammar", "Thai", "FSI Thai Reference Grammar", [ia("Fsi-ThaiBasicCourse-StudentText",
        r"ThaiReferenceGrammar\.pdf$")], [], "", "The FSI's reference grammar of Thai."),
    fsi("turkish", "Turkish", "FSI Turkish Basic Course, Volume 1", [ia("fsi-turkish-basic-course-volume-1-student-text",
        r"_text\.pdf$")], [audio("fsi-turkish.html", "/Volume 1/")], "",
        "The FSI's Turkish course, volume 1 (volume 2's only copy is a scan without words)."),
    fsi("turkish_reader", "Turkish", "FSI Turkish Basic Course: Graded Reader",
        [yj("fsi-turkish.html", r"ED041267\.pdf$")], [], "1968", "The FSI's graded Turkish readings (ERIC ED 041 267)."),
    fsi("twi", "Twi (Akan)", "FSI Twi Basic Course", [ia("micro_IA41153150_0120")], [audio("fsi-twi.html")], "1963",
        "The FSI's course in Twi (Akan) of Ghana (ERIC's microfiche copy, ED 030 120)."),
    fsi("yoruba", "Yoruba", "FSI Yoruba Basic Course", [ia("micro_IA41153618_0019")],
        [audio("fsi-yoruba-basic-course.html")], "1963",
        "The FSI's course in Yoruba of Nigeria (ERIC's microfiche copy, ED 010 462)."),
    fsi("yoruba_intermediate", "Yoruba", "FSI Yoruba Intermediate Texts",
        [yj("fsi-yoruba-intermediate-texts.html", r"Yoruba Intermediate Texts\.pdf$")],
        [audio("fsi-yoruba-intermediate-texts.html")], "", "The FSI's intermediate Yoruba readings."),
    fsi("indonesian_newspaper", "Indonesian", "FSI Indonesian Newspaper Reader", [ia("micro_IA41153063_0142")], [],
        "1968", "The FSI's reader of Indonesian newspaper articles (ERIC's microfiche copy, ED 024 932)."),
    fsi("italian_fast", "Italian", "FSI Italian FAST Course (Familiarization and Short-Term Training)",
        [yj("fsi-italian-fast-updated.html", r"Short term Training - Volume \d\.pdf$")],
        [audio("fsi-italian-fast-updated.html")], "", "The FSI's short Italian course in two volumes."),
    fsi("french_phonology", "French", "FSI Introduction to French Phonology",
        [ia("Fsi-IntroductionToFrenchPhonology-Texts")], [audio("fsi-french-introduction-phonolgy.html")], "",
        "The FSI's course in French pronunciation: the student text and the instructor's manual."),
    fsi("french_monde", "French", "FSI Le Monde Francophone", [ia("Fsi-LeMondeFrancophone")], [], "",
        "The FSI's French readings about the French-speaking countries of the world."),
    fsi("french_fast_metropolitan", "French", "FSI Metropolitan French FAST Course",
        [ia("Fsi-MetropolitanFrenchFast-StudentText")], [audio("fsi-french-fast-course.html", "Metropolitan FAST/")],
        "", "The FSI's short course in the French of France."),
    fsi("french_fast_subsaharan", "French", "FSI Sub-Saharan French FAST Course",
        [ia("Fsi-Sub-saharanFrenchFast-StudentText")], [audio("fsi-french-fast-course.html", "Sub-Saharan FAST/")],
        "1984", "The FSI's short course in the French of West and Central Africa."),
    fsi("testing_kit", "French and Spanish", "FSI Testing Kit: French and Spanish",
        [ia("Fsi-TestingKit-FrenchAndSpanish-Text")], [], "",
        "The FSI's practice material for its French and Spanish speaking tests."),
    fsi("spanish_programmatic", "Spanish", "FSI Spanish Programmatic Course",
        [ia("Fsi-SpanishProgrammaticCourse-Texts", r"(StudentText|Workbook)(_text)?\.pdf$")],
        [audio("fsi-spanish-programmatic.html")], "", "The FSI's self-paced Spanish course: student texts and "
                                                       "workbooks of its two volumes."),
    fsi("spanish_secretarias", "Spanish", "FSI Suplemento para Secretarias", [ia("FSISuplementoParaSecretarias")], [],
        "", "The FSI's Spanish supplement for office secretaries."),
    fsi("arabic_levantine_pronunciation", "Arabic (Levantine)", "FSI Levantine Arabic: Pronunciation",
        [ia("Fsi-LevantineArabic-Pronunciation-StudentText", r"_text\.pdf$")], [audio("fsi-levantine-arabic.html")],
        "", "The FSI's course in the sounds of the Arabic of Syria, Lebanon, Jordan and Palestine."),
    fsi("arabic_modern_written", "Arabic (Modern Standard)", "FSI Modern Written Arabic",
        [ia("Fsi-ModernWrittenArabic-StudentText", r"StudentText(_text)?\.pdf$")],
        [audio("fsi-written-arabic.html", "Arabic/Written/")], "", "The FSI's course in reading Modern Standard Arabic, "
                                                                   "three volumes."),
    fsi("arabic_writing_system", "Arabic (Modern Standard)", "FSI Classical Arabic: The Writing System",
        [ia("FSIClassicalArabicTheWritingSystem", r"_text\.pdf$")], [], "",
        "The FSI's introduction to the Arabic alphabet and writing."),
    fsi("arabic_eastern_western", "Arabic", "FSI From Eastern to Western Arabic",
        [ia("FSIFromEasternToWesternArabic", r"_text\.pdf$")], [], "",
        "The FSI's short guide for speakers of eastern Arabic learning the Arabic of North Africa."),
    fsi("vietnamese_familiarization", "Vietnamese", "FSI Vietnamese Familiarization Course",
        [ia("fsi-vietnamese-familiarization-course")], [], "1969", "The FSI's short Vietnamese course."),
]
FSI_COURSE = {c["key"]: c for c in FSI_COURSES}


def dli(key, language, title, text, year="", description=""):
    """One Defense Language Institute course record (judged by the military release rule at every build)."""
    return dict(key=key, language=language, title=title, year=year, text=list(text), audio=[],
                description=description, publisher=DLI, military=True)


# ====================================================================== Defense Language Institute courses
# Internet Archive copies (ERIC's microfiche copies unless said), each checked: its ERIC record names the Defense
# Language Institute, and its first pages print no copyright stamp and no "not for general distribution" line.
DLI_COURSES = [
    dli("arabic_12_weeks", "Arabic", "DLI Arabic 12 Weeks Course", [ia("micro_IA41153017_0006")], "1969",
        "The Defense Language Institute's short Arabic course (ERIC ED 031 696)."),
    dli("arabic_msa", "Arabic (Modern Standard)", "DLI Modern Standard Arabic Basic Course",
        [ia("micro_IA41153131_0290")], "1966", "The Defense Language Institute's Modern Standard Arabic basic course "
                                               "with its word list (ERIC ED 030 886; some pages are hard to read)."),
    dli("arabic_1981", "Arabic (Modern Standard)", "DLI Arabic Basic Course (revised 1981): volumes, grammar, writing "
        "and glossaries", [ia("DefenseLanguageInstituteForeignLanguageArabicPart2And3",
                             r"(Volume\d+|ArabicEnglishGlossary|ArabicSoundAndScript|TheWritingSystem|"
                             r"GrammarReferenceBook|DictionaryOfMilitaryTerminology)(_text)?\.pdf$")], "1981",
        "The Defense Language Institute's Arabic course (revised 1981): the lesson volumes, the sound and script "
        "book, the writing system, the grammar reference and the glossaries."),
    dli("burmese", "Burmese", "DLI Burmese Basic Course", [ia("micro_IA41153031_0059")], "1964",
        "The Defense Language Institute's Burmese course (ERIC ED 023 096)."),
    dli("czech", "Czech", "DLI Czech Basic Course", [ia("micro_IA41153132_0083")], "1968",
        "The Defense Language Institute's Czech course, eight volumes (ERIC ED 034 203)."),
    dli("indonesian", "Indonesian", "DLI Indonesian Basic Course", [ia("micro_IA41153063_0162")], "1966",
        "The Defense Language Institute's Indonesian course (ERIC ED 024 955)."),
    dli("pashto", "Pashto", "DLI Pashto Basic Course: Textbook, Units 1 to 7", [ia("micro_IA41153424_0341")], "1986",
        "The Defense Language Institute's Pashto textbook (ERIC ED 286 347)."),
    dli("persian", "Persian (Farsi)", "DLI Persian Basic Course", [ia(f"micro_IA41153359_06{n:02d}") for n in
                                                                   (4, 5, 6, 9, 10, 11, 12, 13, 14, 16)] +
        [ia("micro_IA41153527_0697"), ia("micro_IA41153527_0708")], "1966",
        "The Defense Language Institute's Persian course: volumes I to IX (lessons and the reader), the "
        "Persian-English glossary, the guide to reading and writing, and the area background reader (ERIC's "
        "microfiche copies)."),
    dli("polish", "Polish", "DLI Polish Basic Course", [ia("micro_IA41153161_0429")], "1969",
        "The Defense Language Institute's Polish course (ERIC ED 033 357)."),
    dli("romanian", "Romanian", "DLI Romanian Basic Course", [ia("micro_IA41153031_0057")], "1966",
        "The Defense Language Institute's Romanian course (ERIC ED 023 094)."),
    dli("serbo_croatian", "Serbo-Croatian", "DLI Serbo-Croatian Basic Course", [ia("micro_IA41153140_0464")], "1966",
        "The Defense Language Institute's Serbo-Croatian course (ERIC ED 031 688)."),
    dli("swahili", "Swahili", "DLI Swahili Basic Course", [ia("micro_IA41153018_0073")], "1966",
        "The Defense Language Institute's Swahili course (ERIC ED 032 546)."),
    dli("thai", "Thai", "DLI Thai Basic Course", [ia("micro_IA41153031_0056")], "1967",
        "The Defense Language Institute's Thai course (ERIC ED 023 093)."),
    dli("turkish", "Turkish", "DLI Turkish Basic Course", [ia("micro_IA41153132_0077")], "1968",
        "The Defense Language Institute's Turkish course (ERIC ED 034 196)."),
    dli("vietnamese_saigon", "Vietnamese", "DLI Vietnamese (Saigon Dialect) Basic Course", [ia("micro_IA41153031_0051")],
        "1967", "The Defense Language Institute's Vietnamese course in the Saigon dialect (ERIC ED 023 083)."),
    dli("vietnamese_saigon_special", "Vietnamese", "DLI Vietnamese (Saigon Dialect) Special Course (12 Weeks)",
        [ia("micro_IA41153053_0520")], "1966", "The Defense Language Institute's short Vietnamese course (ERIC ED "
                                               "021 241)."),
    dli("german_headstart", "German", "DLI Headstart German Program (1977)",
        [ia(f"micro_IA41153527_06{n}") for n in range(80, 93)], "1977",
        "The Defense Language Institute's Headstart German program for service members going to Germany: the "
        "student guide, modules 1 to 10, the cultural notes and the glossary (ERIC's microfiche copies, ED 192 518 "
        "to 530)."),
    dli("headstart_philippines", "Tagalog (Filipino)", "DLI Headstart for the Philippines (1985)",
        [ia("headstart-for-the-philippines-modules-i-v"), ia("headstart-for-the-philippines-cultural-notes")], "1985",
        "The Defense Language Institute's Headstart program for the Philippines: Tagalog modules I to V and the "
        "cultural notes (Internet Archive copies)."),
    dli("russian_radio", "Russian", "DLI Russian Aural Comprehension Course: Radio Procedures (1976)",
        [ia("RussianRadioProcedures", r"_text\.pdf$")], "1976",
        "The Defense Language Institute's course in understanding Russian radio procedure and its terms."),
]
DLI_COURSE = {c["key"]: c for c in DLI_COURSES}
COURSES_BY_BASE = {"fsi": FSI_COURSE, "dli": DLI_COURSE}


def course_entry(base, course):
    """The PDF_DOCS-like entry of an FSI or DLI course (refs_kit.us_pdf), for pdf_set.pdf_set_book."""
    where = course["text"][0]
    source = f"{IA}/details/{where[1]}" if where[0] == "ia" else where[1]
    sound = (" Its recordings are listed as originals (from fsi-languages.yojik.eu)." if course["audio"] else "")
    notice = FSI_NOTICE if base == "fsi" else DLI_NOTICE
    entry = K.us_pdf(GROUP, name=f"lgov_{base}_{course['key']}", title=f"{course['title']} ({course['language']})",
                     subject=f"Language learning: {course['language']}", publisher=course["publisher"], source=source,
                     description=course["description"] + sound, notice=notice, published=course["year"],
                     level="course")
    if course.get("military"):
        entry.update(military=True, work="a work of the Defense Language Institute (US Department of Defense)")
    return entry


def course_parts(course, cache=None):
    """[(part title, PDF address, page address)] of a course's text PDFs (languages.course_parts does the reading)."""
    return L.course_parts(course, cache)


def course_audio(course, cache=None, sizes=True):
    """[{url, kind, size}] of a course's recordings, never downloaded here: the MP3 links of its yojik course page,
    only those under its folder (audio(page, folder)), with the size the server gives (sizes=False: none asked)."""
    import updates
    out = []
    for _kind, page, folder in course["audio"]:
        for url in L.page_links(page, r"\.mp3$", cache):
            if folder and folder not in urllib.parse.unquote(url):
                continue
            size = 0
            if sizes:
                head = updates.head_signs(url).split("|")
                size = int(head[-1]) if head and head[-1].isdigit() else 0
            out.append({"url": url, "kind": "mp3", "size": size})
    return out


def course_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one course ("fsi:<key>" or "dli:<key>"): its text volumes read with pdf_set.pdf_set_book (each
    volume with its licence line checked, robots.txt asked, a scan without words refused, and for a DLI course the
    military release rule), its recordings added to its originals."""
    import pdf_set
    base, _, key = name.partition(":")
    course = COURSES_BY_BASE.get(base, {}).get(key)
    if course is None:
        left_out.append({"title": name, "reason": "Unknown course."})
        return None
    parts = course_parts(course, cache)
    if not parts:
        left_out.append({"title": course["title"], "reason": "No text PDF of the course was found."})
        return None
    book = pdf_set.pdf_set_book(course_entry(base, course), parts, work, cache, left_out, limit)
    if book is None:
        return None
    if course["audio"]:
        book.originals += course_audio(course, cache, sizes=not limit)
    book.version = f"read from {', '.join(sorted({p[2] for p in parts}))} on {datetime.date.today().isoformat()}"
    return book


def course_sign(name):
    """A course's sign of change: the names and checksums of its Internet Archive files, or its page's PDF links."""
    base, _, key = name.partition(":")
    course = COURSES_BY_BASE[base][key]
    signs = []
    for kind, where, pattern in course["text"]:
        if kind == "ia":
            signs += sorted((f.get("name"), f.get("md5")) for f in L.ia_files(where) if re.search(pattern, f["name"]))
        else:
            signs += L.page_links(where, pattern)
    return K.sha(signs)


# ====================================================================== DLIFLC Field Support: survival kits, countries

FIELD = "https://fieldsupport.dliflc.edu"
LSK_LIST = f"{FIELD}/productList.aspx?v=lsk"
DLIFLC_TERMS = "https://www.dliflc.edu/privacy"
DLIFLC_TEXT = r"considered public information and may be distributed or copied"
DLIFLC_NOTICE = ("Made by the Defense Language Institute Foreign Language Center (DLIFLC), a school of the US "
                 "Department of Defense, and published openly on its Field Support site. Its pages show \"Copyright "
                 "DLIFLC\"; works of the US government have no copyright in the US (17 U.S.C. 105), and www.dliflc.edu "
                 "says \"Information presented on this site is considered public information and may be distributed or "
                 "copied unless otherwise specified\". Written for service members: many phrases are about checkpoints, "
                 "searches and military work.")
# Parts of a survival kit left out: anything about mines or explosives (the library's safety rule for military
# material: build_textbooks.NOT_FIELD_SAFE).
MINE_WORDS = re.compile(r"\b(mines?|minefields?|explosives?|demolitions?|booby|ied|bombs?|grenades?)\b", re.I)
# Guides behind a sign-in (their addresses go to /products/secure/): not read.
SECURE = "/products/secure/"

# (key piece, the product list's label, the language). The labels are the Field Support site's own, as it listed them
# on 23 November 2026 (89 languages); a label it no longer lists makes the book say so in left_out.
LSK_LANGUAGES = [
    ("albanian", "Albanian", "Albanian"), ("algerian", "Algerian", "Arabic (Algerian)"),
    ("amharic", "Amharic", "Amharic"), ("arabic_egyptian", "Arabic-Egyptian", "Arabic (Egyptian)"),
    ("arabic_iraqi", "Arabic-Iraqi", "Arabic (Iraqi)"), ("arabic_jordanian", "Arabic-Jordanian", "Arabic (Jordanian)"),
    ("arabic_lebanese", "Arabic-Lebanese", "Arabic (Lebanese)"), ("arabic_libyan", "Arabic-Libyan", "Arabic (Libyan)"),
    ("arabic_moroccan", "Arabic-Moroccan", "Arabic (Moroccan)"),
    ("arabic_msa", "Arabic (Modern Standard)", "Arabic (Modern Standard)"),
    ("arabic_saudi", "Arabic-Saudi", "Arabic (Saudi)"), ("arabic_sudanese", "Arabic-Sudanese", "Arabic (Sudanese)"),
    ("arabic_syrian", "Arabic-Syrian", "Arabic (Syrian)"), ("arabic_tunisian", "Arabic-Tunisian", "Arabic (Tunisian)"),
    ("arabic_yemeni", "Arabic-Yemeni", "Arabic (Yemeni)"), ("azeri", "Azeri", "Azerbaijani"),
    ("balochi", "Balochi", "Balochi"), ("bengali", "Bengali", "Bengali"), ("bosnian", "Bosnian", "Bosnian"),
    ("bulgarian", "Bulgarian", "Bulgarian"), ("burmese", "Burmese", "Burmese"), ("cebuano", "Cebuano", "Cebuano"),
    ("chavacano", "Chavacano", "Chavacano"), ("chinese_cantonese", "Chinese-Cantonese", "Chinese (Cantonese)"),
    ("chinese_gan", "Chinese-Gan", "Chinese (Gan)"), ("chinese_mandarin", "Chinese-Mandarin", "Chinese (Mandarin)"),
    ("chinese_wu", "Chinese-Wu", "Chinese (Wu)"), ("croatian", "Croatian", "Croatian"), ("czech", "Czech", "Czech"),
    ("dari", "Dari", "Dari"), ("emirati", "Emirati", "Arabic (Emirati)"), ("georgian", "Georgian", "Georgian"),
    ("gujarati", "Gujarati", "Gujarati"), ("haitian", "Haitian", "Haitian Creole"),
    ("hassaniya", "Hassaniya", "Arabic (Hassaniya)"), ("hausa", "Hausa", "Hausa"), ("hebrew", "Hebrew", "Hebrew"),
    ("hindi", "Hindi", "Hindi"), ("igbo", "Igbo", "Igbo"), ("ilocano", "Ilocano", "Ilocano"),
    ("indonesian", "Indonesian-Bahasa", "Indonesian"), ("italian", "Italian", "Italian"),
    ("japanese", "Japanese", "Japanese"), ("javanese", "Javanese", "Javanese"), ("kashmiri", "Kashmiri", "Kashmiri"),
    ("kazakh", "Kazakh", "Kazakh"), ("korean_north", "Korean-North", "Korean (North)"),
    ("kosovar", "Kosovar (Albania)", "Albanian (Kosovar)"), ("kurmanji", "Kurmanji", "Kurdish (Kurmanji)"),
    ("kyrgyz", "Kyrgyz", "Kyrgyz"), ("lingala", "Lingala", "Lingala"), ("malay", "Malay", "Malay"),
    ("mongolian", "Mongolian", "Mongolian"), ("nepalese", "Nepalese", "Nepali"),
    ("palestinian", "Palestinian", "Arabic (Palestinian)"), ("pashto", "Pashto", "Pashto"),
    ("pashto_pakistan", "Pashto (Pakistan)", "Pashto (Pakistan)"), ("persian", "Persian-Farsi", "Persian (Farsi)"),
    ("polish", "Polish", "Polish"), ("portuguese_brazilian", "Portuguese-Brazilian", "Portuguese (Brazilian)"),
    ("portuguese_european", "Portuguese-European", "Portuguese (European)"), ("punjabi", "Punjabi", "Punjabi"),
    ("quechua", "Quechua", "Quechua"), ("romanian", "Romanian", "Romanian"), ("russian", "Russian", "Russian"),
    ("serbian", "Serbian", "Serbian"), ("sindhi", "Sindhi", "Sindhi"), ("somali", "Somali", "Somali"),
    ("sorani", "Sorani", "Kurdish (Sorani)"), ("spanish_colombia", "Spanish-Colombia", "Spanish (Colombian)"),
    ("spanish_mexico", "Spanish-Mexico", "Spanish (Mexican)"), ("spanish_venezuela", "Spanish-Venezuela",
                                                                "Spanish (Venezuelan)"),
    ("swahili", "Swahili", "Swahili"), ("tagalog", "Tagalog", "Tagalog (Filipino)"), ("tajik", "Tajik", "Tajik"),
    ("tamil", "Tamil", "Tamil"), ("tausug", "Tausug", "Tausug"), ("telugu", "Telugu", "Telugu"), ("thai", "Thai", "Thai"),
    ("tigrinya", "Tigrinya", "Tigrinya"), ("turkish", "Turkish", "Turkish"), ("turkmen", "Turkmen", "Turkmen"),
    ("uighur", "Uighur", "Uyghur"), ("ukrainian", "Ukrainian", "Ukrainian"), ("urdu", "Urdu", "Urdu"),
    ("uzbek", "Uzbek", "Uzbek"), ("vietnamese", "Vietnamese", "Vietnamese"), ("yakan", "Yakan", "Yakan"),
    ("yoruba", "Yoruba", "Yoruba"),
]
LSK = {k: (label, language) for k, label, language in LSK_LANGUAGES}


def label_words(label):
    """A product list label made comparable: "Arabic-Lebanese  .  Language Survival Kits" -> "arabic-lebanese"."""
    label = re.sub(r"Language Survival Kits?", "", html.unescape(label), flags=re.I)
    return " ".join(label.replace(".", " ").split()).lower()


def lsk_guides(list_html, label):
    """[(counter number, guide title)] of one language's survival kit guides in the Field Support product list."""
    blocks = dict((label_words(name), block) for block, name in
                  re.findall(r"showLSK\(this, \"(conLSK\d+)\"\)'>([^<]*)</div>", list_html))
    block = blocks.get(label_words(label))
    if not block:
        return []
    m = re.search(r"<div id='%s' class='lsk'>(.*?)</div></div>" % re.escape(block), list_html, re.S)
    if not m:
        return []
    return [(n, " ".join(html.unescape(t).split())) for n, t in
            re.findall(r"counter\.aspx\?i=(\d+)&t=language' target='_blank'>([^<]*)</a>", m.group(1))]


class _Stay(urllib.request.HTTPRedirectHandler):
    """A redirect handler that does not follow: the product list's links are counters that answer with the guide's
    address (a redirect), and only that address is wanted."""

    def redirect_request(self, *args, **kwargs):
        """Do not follow the redirect (urllib then raises it as an HTTPError holding the Location header)."""
        return None


def guide_address(counter):
    """The address of a survival kit guide from its counter number ("" when the counter does not send on): one
    request, with the builder's pause and user agent."""
    import build_textbooks as B
    url = f"{FIELD}/counter.aspx?i={counter}&t=language"
    if not K.readable(url):
        return ""
    wait = B.PAUSE - (time.monotonic() - B._last.get("fieldsupport.dliflc.edu", 0))
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": B.USER_AGENT})
    try:
        urllib.request.build_opener(_Stay).open(req, timeout=60)
        return ""
    except urllib.error.HTTPError as e:
        location = e.headers.get("Location", "") if e.code in (301, 302, 303, 307, 308) else ""
        return urllib.parse.urljoin(FIELD + "/", location) if location else ""
    finally:
        B._last["fieldsupport.dliflc.edu"] = time.monotonic()


def _xml_values(text, record, fields):
    """[{field: value}] of the records of a small XML file (regular expressions: the files are simple and some have
    a byte-order mark)."""
    out = []
    for body in re.findall(rf"<{record}>(.*?)</{record}>", text, re.S):
        row = {}
        for f in fields:
            m = re.search(rf"<{f}>(.*?)</{f}>", body, re.S)
            row[f] = " ".join(html.unescape(m.group(1)).split()) if m else ""
        out.append(row)
    return out


def lsk_xml_modules(cat_xml, kit_xml):
    """[(part title, [(English, romanized, script)])] of a survival kit of the newer kind (its phrases in
    xml/dbo_langKit.xml, its parts' names in xml/dbo_catID.xml), in part order then phrase order."""
    names = {r["categoryID"]: r["categoryDesc"] for r in _xml_values(cat_xml, "dbo_catID",
                                                                      ("categoryID", "categoryDesc"))}
    rows = _xml_values(kit_xml, "dbo_langKit", ("catID", "phraseOrder", "englishPhrase", "romanized", "unicode"))
    parts = {}
    for r in rows:
        parts.setdefault(r["catID"], []).append(r)

    def number(value):
        """A number from a field ("12" -> 12; anything else last)."""
        return int(value) if value.isdigit() else 10 ** 6

    out = []
    for cat in sorted(parts, key=number):
        phrases = sorted(parts[cat], key=lambda r: number(r["phraseOrder"]))
        out.append((names.get(cat, f"Part {cat}"), [(r["englishPhrase"], r["romanized"], r["unicode"])
                                                    for r in phrases if r["englishPhrase"]]))
    return out


def lsk_index_modules(index_html):
    """[(address part, part title)] of a survival kit of the older kind: the module pages its index page links."""
    return [(h, " ".join(html.unescape(t).split())) for h, t in
            re.findall(r'<a href="(module\d+\.html)" class="css_link" title="([^"]*)"', index_html)]


def lsk_module_rows(module_html):
    """[(English, romanized, script)] of an older survival kit's module page: each table row's "css_cnt" cells."""
    out = []
    for tr in re.findall(r"<tr>(.*?)</tr>", module_html, re.S):
        cells = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split())
                 for c in re.findall(r'<td[^>]*class="css_cnt"[^>]*>(.*?)</td>', tr, re.S)]
        if len(cells) >= 2 and cells[0]:
            out.append((cells[0], cells[1], cells[2] if len(cells) > 2 else ""))
    return out


def lsk_table(language, phrases):
    """The HTML table of a part's phrases."""
    import build_textbooks as B
    rows = "".join(f"<tr><td>{B.esc(e)}</td><td>{B.esc(r)}</td><td>{B.esc(s)}</td></tr>" for e, r, s in phrases)
    return (f"<table><tr><th>English</th><th>How to say it (DLIFLC spelling)</th><th>{B.esc(language)}</th></tr>"
            f"{rows}</table>")


def lsk_guide_parts(base, cache=None):
    """[(part title, [(English, romanized, script)])] of one survival kit guide at base (its address, ending "/"):
    the newer XML files when it has them, else its index page's module pages."""
    import build_textbooks as B
    try:
        return lsk_xml_modules(B.fetch(base + "xml/dbo_catID.xml", cache), B.fetch(base + "xml/dbo_langKit.xml", cache))
    except urllib.error.HTTPError:
        pass
    parts = []
    for href, title in lsk_index_modules(B.fetch(base, cache)):
        parts.append((title, lsk_module_rows(B.fetch(base + href, cache))))
    return parts


def lsk_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one language's Language Survival Kits ("lsk:<language>"): every guide the Field Support product
    list names for it (the weapons guides and anything behind a sign-in left out), one page per part, the parts
    about mines and explosives left out. The licence line is checked on www.dliflc.edu first."""
    import build_textbooks as B
    key = name.split(":", 1)[1] if ":" in name else ""
    if key not in LSK:
        left_out.append({"title": name, "reason": "Unknown language."})
        return None
    label, language = LSK[key]
    words = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", B.fetch(DLIFLC_TERMS, cache))).split())
    if not re.search(DLIFLC_TEXT, words):
        left_out.append({"title": name, "reason": "www.dliflc.edu no longer says its information may be distributed "
                                                  "or copied."})
        return None
    guides = lsk_guides(B.fetch(LSK_LIST, cache), label)
    if not guides:
        left_out.append({"title": name, "reason": f"The Field Support product list no longer names {label}."})
        return None
    book = K.new_book(f"lgov_lsk_{key}", f"Language Survival Kits: {language} (Defense Language Institute)",
                      f"Language learning: {language}", GROUP, "Defense Language Institute Foreign Language Center "
                      "(DLIFLC), US Department of Defense", K.US_GOV, K.US_GOV_URL, LSK_LIST,
                      f"The Defense Language Institute's pocket phrase guides for {language}: each phrase in English, "
                      f"in the Institute's spelling for English speakers, and in {language} writing. One page per part "
                      f"of each guide (greetings, helpful phrases, directions, medical words and more).",
                      DLIFLC_NOTICE, level="reference",
                      changes="each part of each guide made into a table (English, how to say it, the language's "
                              "own writing); the parts about mines and explosives and the guides behind a sign-in "
                              "left out")
    chapter = 0
    for counter, guide in guides:
        if limit and len(book.pages) >= limit:
            break
        if re.search(r"weapon", guide, re.I):
            left_out.append({"title": f"{label}: {guide}", "reason": "The weapons guides are behind a sign-in."})
            continue
        address = guide_address(counter)
        if not address or SECURE in address:
            left_out.append({"title": f"{label}: {guide}", "reason": "Its address needs a sign-in or does not answer."})
            continue
        base = address.rstrip("/") + "/"
        try:
            parts = lsk_guide_parts(base, cache)
        except (urllib.error.URLError, OSError) as e:
            left_out.append({"title": f"{label}: {guide}", "reason": f"It could not be read ({e})."})
            continue
        chapter += 1
        for title, phrases in parts:
            if limit and len(book.pages) >= limit:
                break
            if MINE_WORDS.search(title):
                left_out.append({"title": f"{label}: {guide}: {title}", "reason": "About mines or explosives: left "
                                                                                  "out by the library's safety rule."})
                continue
            if not phrases:
                continue
            path = f"{B.slug(guide, 30)}-{B.slug(title, 40)}"
            book.pages.append(B.Page(path, f"{guide}: {title.capitalize()}", lsk_table(language, phrases), chapter,
                                     guide))
        book.originals.append({"url": base, "kind": "html", "size": 0})
    if not book.pages:
        left_out.append({"title": name, "reason": "No phrases could be read."})
        return None
    book.version = f"read from fieldsupport.dliflc.edu on {datetime.date.today().isoformat()}"
    return book


def lsk_sign(name):
    """A language's sign of change: its part of the Field Support product list."""
    import build_textbooks as B
    label = LSK[name.split(":", 1)[1]][0]
    return K.sha(lsk_guides(B.fetch(LSK_LIST), label))


# Countries in Perspective: (key piece, country, the product's address part), as the Field Support site listed them
# on 23 November 2026 (83 countries). Each page links the country's PDF.
CIP_COUNTRIES = [
    ("afghanistan", "Afghanistan", "afghanistan"), ("albania", "Albania", "albania"), ("algeria", "Algeria", "algeria"),
    ("angola", "Angola", "angola"), ("azerbaijan", "Azerbaijan", "azerbaijan"), ("bahrain", "Bahrain", "bahrain"),
    ("belarus", "Belarus", "belarus"), ("bosnia", "Bosnia", "bosnia"), ("brazil", "Brazil", "brazil"),
    ("bulgaria", "Bulgaria", "bulgaria"), ("burma", "Burma", "burma"), ("cambodia", "Cambodia", "cambodia"),
    ("chad", "Chad", "chad"), ("china", "China", "china"), ("colombia", "Colombia", "colombia"),
    ("congo", "Democratic Republic of the Congo", "DRCongo"), ("croatia", "Croatia", "croatia"),
    ("cuba", "Cuba", "cuba"), ("czech", "Czech Republic", "czech"), ("cote_divoire", "Côte d'Ivoire", "cote_dIvoire"),
    ("djibouti", "Djibouti", "Djibouti"), ("egypt", "Egypt", "egypt"), ("eritrea", "Eritrea", "Eritrea"),
    ("ethiopia", "Ethiopia", "ethiopia"), ("georgia", "Georgia", "georgia"), ("germany", "Germany", "germany"),
    ("haiti", "Haiti", "haiti"), ("hungary", "Hungary", "hungary"), ("india", "India", "india"),
    ("indonesia", "Indonesia", "indonesia"), ("iran", "Iran", "Iran"), ("iraq", "Iraq", "Iraq"),
    ("israel", "Israel", "israel"), ("italy", "Italy", "italy"), ("japan", "Japan", "japan"),
    ("jordan", "Jordan", "jordan"), ("kazakhstan", "Kazakhstan", "Kazakhstan"), ("kenya", "Kenya", "Kenya"),
    ("north_korea", "North Korea", "northkorea"), ("south_korea", "South Korea", "southkorea"),
    ("kuwait", "Kuwait", "kuwait"), ("kyrgyzstan", "Kyrgyzstan", "kyrgyzstan"), ("latvia", "Latvia", "lativia"),
    ("lebanon", "Lebanon", "lebanon"), ("liberia", "Liberia", "Liberia"), ("libya", "Libya", "libya"),
    ("lithuania", "Lithuania", "lithuania"), ("malaysia", "Malaysia", "Malaysia"), ("mali", "Mali", "mali"),
    ("mauritania", "Mauritania", "Mauritania"), ("mexico", "Mexico", "mexico"), ("mongolia", "Mongolia", "mongolia"),
    ("morocco", "Morocco", "morocco"), ("nepal", "Nepal", "nepal"), ("niger", "Niger", "niger"),
    ("nigeria", "Nigeria", "nigeria"), ("norway", "Norway", "norway"), ("oman", "Oman", "oman"),
    ("pakistan", "Pakistan", "pakistan"), ("palestine", "Palestinian Territories", "Palestine"),
    ("peru", "Peru", "Peru"), ("philippines", "Philippines", "Philippines"), ("poland", "Poland", "poland"),
    ("qatar", "Qatar", "qatar"), ("romania", "Romania", "romania"), ("russia", "Russia", "russia"),
    ("saudi_arabia", "Saudi Arabia", "saudi"), ("serbia", "Serbia", "serbia"), ("somalia", "Somalia", "somalia"),
    ("sri_lanka", "Sri Lanka", "srilanka"), ("sudan", "Sudan", "Sudan"), ("syria", "Syria", "syria"),
    ("tajikistan", "Tajikistan", "tajikistan"), ("thailand", "Thailand", "thailand"), ("tunisia", "Tunisia", "tunisia"),
    ("turkey", "Turkey", "turkey"), ("turkmenistan", "Turkmenistan", "turkmenistan"), ("ukraine", "Ukraine", "ukraine"),
    ("uae", "United Arab Emirates", "UAE"), ("uzbekistan", "Uzbekistan", "uzbekistan"),
    ("venezuela", "Venezuela", "venezuela"), ("vietnam", "Vietnam", "vietnam"), ("yemen", "Yemen", "yemen"),
]


def cip_entry(key, country, path):
    """The PDF entry of one Countries in Perspective book: its product page (which links the PDF), the licence line
    checked on www.dliflc.edu."""
    page = f"{FIELD}/products/cip/{path}/"
    return K.us_pdf(GROUP, name=f"cip_{key}", title=f"{country} in Perspective (Defense Language Institute)",
                    subject=f"Countries and cultures: {country}", publisher="Defense Language Institute Foreign "
                    "Language Center (DLIFLC), US Department of Defense", page=page, source=page,
                    pdf_pattern=r"\.pdf$", licence_page=DLIFLC_TERMS, licence_text=DLIFLC_TEXT,
                    description=f"The Defense Language Institute's country book on {country}: geography, history, "
                                f"economy, society, security and the chapter assessments, for service members going "
                                f"there.", notice=DLIFLC_NOTICE.replace(" Written for service members: many phrases "
                                                                        "are about checkpoints, searches and military "
                                                                        "work.", ""))


CIP_PDFS = [cip_entry(*c) for c in CIP_COUNTRIES]

# ====================================================================== single Internet Archive PDFs

WAR_NOTE = (" A guide of the Second World War for soldiers: its phrases are for that war, its spellings are the "
            "Army's of the time, and some words about people are outdated.")


def ia_pdf(name, title, language, archive, year, publisher, description, military=True, subject=None):
    """One Internet Archive PDF of a US government work (refs_kit.us_pdf), judged by the military release rule when
    military (at every build)."""
    entry = K.us_pdf(GROUP, name=name, title=title, subject=subject or f"Language learning: {language}",
                     publisher=publisher, archive=archive, source=f"{IA}/details/{archive}", published=str(year),
                     language_name=language, description=description,
                     notice="A work of the US government (public domain), read from its Internet Archive scan: the "
                            "machine-read text has the scanner's mistakes, and words in other scripts may be missing.")
    if military:
        entry.update(military=True, work="a work of the War Department (US Army)")
    return entry


WAR = "War Department (US Army)"
MILITARY_PDFS = [
    ia_pdf("tm30_250_spanish_dictionary", "TM 30-250 Military Dictionary: English-Spanish, Spanish-English (1941)",
           "Spanish", "TM30-250MilitaryDictionarySpanish", 1941, WAR, "The Army's English-Spanish and Spanish-English "
           "dictionary of military words." + WAR_NOTE),
    ia_pdf("tm30_254_russian_dictionary", "TM 30-254 Military Dictionary: English-Russian, Russian-English (1941)",
           "Russian", "TM30254Russian", 1941, WAR, "The Army's English-Russian and Russian-English military "
           "dictionary (advance installment)." + WAR_NOTE),
    ia_pdf("tm30_301_portuguese", "TM 30-301 Portuguese as Spoken in Brazil: A Guide to the Spoken Language (1943)",
           "Portuguese (Brazilian)", "TM30-301", 1943, WAR, "The Army's language guide to Brazilian Portuguese: "
           "pronunciation, useful phrases and a word list." + WAR_NOTE),
    ia_pdf("tm30_302_french", "TM 30-302 French: A Guide to the Spoken Language (1943)", "French", "TM30-302", 1943, WAR,
           "The Army's French language guide: pronunciation, useful phrases and a word list." + WAR_NOTE),
    ia_pdf("tm30_313_icelandic", "TM 30-313 Icelandic: A Guide to the Spoken Language (1944)", "Icelandic",
           "TM30-313Icelandic", 1944, WAR, "The Army's Icelandic language guide." + WAR_NOTE),
    ia_pdf("tm30_316_hungarian", "TM 30-316 Hungarian: A Guide to the Spoken Language (1943)", "Hungarian", "TM30-316",
           1943, WAR, "The Army's Hungarian language guide." + WAR_NOTE),
    ia_pdf("tm30_321_north_african_arabic", "TM 30-321 North African Arabic: A Guide to the Spoken Language (1943)",
           "Arabic (North African)", "TM30-321", 1943, WAR, "The Army's guide to the Arabic of North Africa." + WAR_NOTE),
    ia_pdf("tm30_327_hindustani", "TM 30-327 Hindustani: A Guide to the Spoken Language (1944)", "Hindustani "
           "(Hindi-Urdu)", "TM30-327", 1944, WAR, "The Army's Hindustani (Hindi-Urdu) language guide." + WAR_NOTE),
    ia_pdf("tm30_331_thai", "TM 30-331 Thai (Siamese): A Guide to the Spoken Language (1944)", "Thai", "TM30-331", 1944,
           WAR, "The Army's Thai language guide." + WAR_NOTE),
    ia_pdf("tm30_333_chinese", "TM 30-333 Chinese: A Guide to the Spoken Language (1943)", "Chinese (Mandarin)",
           "TM30-333", 1943, WAR, "The Army's Chinese (Mandarin) language guide." + WAR_NOTE),
    ia_pdf("tm30_340_tagalog", "TM 30-340 Tagalog: A Guide to the Spoken Language (1944)", "Tagalog (Filipino)",
           "tm-30-340-tagalog-philippines-language-guide-1944", 1944, WAR, "The Army's Tagalog language guide for the "
           "Philippines." + WAR_NOTE),
    ia_pdf("tm30_341_japanese", "TM 30-341 Japanese: A Guide to the Spoken Language (1943)", "Japanese", "TM30-341",
           1943, WAR, "The Army's Japanese language guide." + WAR_NOTE),
    ia_pdf("tm30_345_bulgarian", "TM 30-345 Bulgarian: A Guide to the Spoken Language (1943)", "Bulgarian", "TM30-345",
           1943, WAR, "The Army's Bulgarian language guide." + WAR_NOTE),
    ia_pdf("tm30_349_rumanian", "TM 30-349 Rumanian: A Guide to the Spoken Language (1943)", "Romanian", "TM30-349",
           1943, WAR, "The Army's Romanian language guide." + WAR_NOTE),
    ia_pdf("tm30_352_albanian", "TM 30-352 Albanian: A Guide to the Spoken Language (1943)", "Albanian", "TM30-352",
           1943, WAR, "The Army's Albanian language guide." + WAR_NOTE),
    ia_pdf("tm30_485_japanese_glossary", "TM 30-485 Japanese-English Glossary of Technical Communication Terms (1943)",
           "Japanese", "TM30-485", 1943, WAR, "The Army's Japanese-English glossary of radio and telephone terms."
           + WAR_NOTE),
    ia_pdf("tm30_501_portuguese_dictionary", "TM 30-501 Portuguese Military Dictionary (1944)", "Portuguese",
           "TM30-501", 1944, WAR, "The Army's Portuguese-English and English-Portuguese military dictionary." + WAR_NOTE),
    ia_pdf("tm30_506_german_dictionary", "TM 30-506 German Military Dictionary (1944)", "German", "TM30-506", 1944, WAR,
           "The Army's German-English and English-German military dictionary." + WAR_NOTE),
    ia_pdf("tm30_533_chinese_dictionary", "TM 30-533 Chinese Military Dictionary (1944)", "Chinese (Mandarin)",
           "TM30-533", 1944, WAR, "The Army's Chinese-English and English-Chinese military dictionary." + WAR_NOTE),
    ia_pdf("tm30_541_japanese_dictionary", "TM 30-541 Japanese Military Dictionary (1944)", "Japanese", "TM30-541",
           1944, WAR, "The Army's Japanese-English and English-Japanese military dictionary." + WAR_NOTE),
    ia_pdf("tm30_544_russian_dictionary", "TM 30-544 Russian Military Dictionary (1945)", "Russian", "TM30-544-nsia",
           1945, WAR, "The Army's English-Russian and Russian-English military dictionary." + WAR_NOTE),
    ia_pdf("tm30_601_portuguese_phrase_book", "TM 30-601 Portuguese Phrase Book (1943)", "Portuguese", "TM30-601", 1943,
           WAR, "The Army's Portuguese phrase book: phrases by situation with how to say them." + WAR_NOTE),
    ia_pdf("tm30_611_japanese_phrase_book", "TM 30-611 Japanese Phrase Book (1944)", "Japanese", "TM30-611", 1944, WAR,
           "The Army's Japanese phrase book." + WAR_NOTE),
    ia_pdf("tm30_642_korean_phrase_book", "TM 30-642 Korean Phrase Book (1944)", "Korean",
           "tm-30-642-korean-phrase-book", 1944, WAR, "The Army's Korean phrase book." + WAR_NOTE),
    ia_pdf("tm20_633_chinese_phrase_book", "TM 20-633 Chinese Phrase Book (1943)", "Chinese (Mandarin)", "TM20-633-nsia",
           1943, WAR, "The Army's Chinese phrase book." + WAR_NOTE),
    ia_pdf("tm30_1512_spoken_english", "TM 30-1512 O Inglês Falado: Spoken English, Basic Course (1945)", "English "
           "(for Portuguese speakers)", "TM30-1512", 1945, WAR, "The Army's basic course in spoken English for "
           "Portuguese-speaking (Brazilian) soldiers." + WAR_NOTE),
    ia_pdf("german_phrase_book_1943", "German Phrase Book (War Department, 1943)", "German", "GermanPhraseBook_987",
           1943, WAR, "The Army's German phrase book." + WAR_NOTE),
    ia_pdf("serbo_croatian_phrase_book_1943", "Serbo-Croatian Phrase Book (War Department, 1943)", "Serbo-Croatian",
           "serbocroatianphr00unit", 1943, WAR, "The Army's Serbo-Croatian phrase book." + WAR_NOTE),
    ia_pdf("melanesian_pidgin_1944", "Melanesian Pidgin English Language Guide (War Department, 1944)",
           "Tok Pisin (Melanesian Pidgin)", "MelanesianPidginEnglishLanguageGuide", 1944, WAR,
           "The Army's guide to Melanesian Pidgin (today's Tok Pisin) of New Guinea and the Solomon Islands." + WAR_NOTE),
    ia_pdf("dictionary_spoken_russian_1945", "Dictionary of Spoken Russian (War Department, 1945)", "Russian",
           "DictionaryOfSpokenRussian", 1945, WAR, "The War Department's Russian-English and English-Russian "
           "dictionary of the spoken language (TM 30-944)." + WAR_NOTE),
    ia_pdf("dictionary_spoken_chinese_1945", "Dictionary of Spoken Chinese (War Department, 1945)", "Chinese "
           "(Mandarin)", "dictionaryofspok00unse", 1945, WAR, "The War Department's Chinese-English and English-Chinese "
           "dictionary of spoken Mandarin (TM 30-933)." + WAR_NOTE),
    ia_pdf("civil_affairs_german_dictionary_1944", "Civil Affairs Guide: German-English Dictionary of German "
           "Administrative Terms (War Department, 1944)", "German", "civilaffairsguid00neub", 1944, WAR,
           "The War Department's dictionary of German government and administrative words, for civil affairs officers."
           + WAR_NOTE),
]

BAE = "Bureau of American Ethnology, Smithsonian Institution (Government Printing Office)"
NATIVE_NOTE = (" An old government work about a living language: its spelling system is the author's own and older "
               "than the one the nation teaches today, and some of its words about the people are outdated. The "
               "nation's own language program is the place to learn the language as it is spoken now.")
OTHER_US_PDFS = [
    ia_pdf("navajo_english_dictionary_1958", "Navajo-English Dictionary (Bureau of Indian Affairs, 1958)", "Navajo",
           "micro_IA41153043_0168", 1958, "Bureau of Indian Affairs, US Department of the Interior",
           "Leon Wall and William Morgan's Navajo-English dictionary, made for the Bureau of Indian Affairs (ERIC's "
           "microfiche copy)." + NATIVE_NOTE, military=False),
    ia_pdf("choctaw_dictionary_1915", "A Dictionary of the Choctaw Language (Cyrus Byington, 1915)", "Choctaw",
           "adictionarychoc00byingoog", 1915, BAE, "Cyrus Byington's Choctaw-English and English-Choctaw dictionary, "
           "Bulletin 46 of the Bureau of American Ethnology." + NATIVE_NOTE, military=False),
    ia_pdf("osage_dictionary_1932", "A Dictionary of the Osage Language (Francis La Flesche, 1932)", "Osage",
           "b31365346", 1932, BAE, "Francis La Flesche's Osage-English dictionary, Bulletin 109 of the Bureau of "
           "American Ethnology; La Flesche was an Omaha scholar." + NATIVE_NOTE, military=False),
    ia_pdf("dakota_grammar_1893", "Dakota Grammar, Texts, and Ethnography (Stephen Return Riggs, 1893)", "Dakota",
           "dakotagrammartex00rigguoft", 1893, "US Geographical and Geological Survey of the Rocky Mountain Region "
           "(Government Printing Office)", "Stephen Return Riggs's grammar of the Dakota language with Dakota texts and "
           "their translations (Contributions to North American Ethnology, volume IX)." + NATIVE_NOTE, military=False),
    ia_pdf("dakota_language_1872", "The Language of the Dakota or Sioux Indians (F. L. O. Roehrig, 1872)", "Dakota",
           "cu31924027108137", 1872, "Smithsonian Institution (Government Printing Office)", "A short study of the "
           "Dakota (Sioux) language from the Smithsonian's annual report of 1871." + NATIVE_NOTE, military=False),
    ia_pdf("chamorro_dictionary_1918", "Dictionary and Grammar of the Chamorro Language of the Island of Guam (Edward "
           "R. von Preissig, 1918)", "Chamorro", "aff7166.0001.001.umich.edu", 1918, "US Navy, Naval Government of "
           "Guam (Government Printing Office)", "Paymaster Edward von Preissig's Chamorro grammar and Chamorro-English, "
           "English-Chamorro dictionary for the Navy's government of Guam. Its spelling is older than the one taught "
           "on Guam today.", military=True),
]
OTHER_US_PDFS[-1]["work"] = "a work of the US Navy"

# ====================================================================== Canada: TERMIUM Plus (Open Government Licence)

TERMIUM_DATASET = "https://open.canada.ca/data/api/action/package_show?id=94fc74d6-9b9a-4c2e-9c6c-45a5092453aa"
TERMIUM_PAGE = "https://open.canada.ca/data/en/dataset/94fc74d6-9b9a-4c2e-9c6c-45a5092453aa"
TERMIUM_TEXT = r"Open Government Licence - Canada"
TERMIUM_FILES = "https://donnees-data.tpsgc-pwgsc.gc.ca/bt1/tp-tp"
TERMIUM_NOTICE = ("Contains information licensed under the Open Government Licence - Canada "
                  "(https://open.canada.ca/en/open-government-licence-canada). TERMIUM Plus, the Government of "
                  "Canada's terminology and linguistic data bank, by the Translation Bureau, Public Services and "
                  "Procurement Canada. Terms for translators: each is the bank's recommended term in its subject.")
# (key piece, subject, file name under TERMIUM_FILES), as the dataset listed them on 23 November 2026.
TERMIUM_SUBJECTS = [
    ("administration", "Administration", "domaine-subject-administration.zip"),
    ("agriculture", "Agriculture", "domaine-subject-agriculture.zip"),
    ("arts_recreation_sports", "Arts, recreation and sports", "domaine-ArtsLoisirsSports-subject-ArtsRecreationSports.zip"),
    ("construction", "Construction", "domaine-subject-construction.zip"),
    ("economy", "Economy", "domaine-economie-subject-economy.zip"),
    ("electricity", "Electricity", "domaine-electricite-subject_electricity.zip"),
    ("electronics_informatics", "Electronics and informatics",
     "domaine-ElectroniqueInformatique-subject-ElectronicsInformatics.zip"),
    ("environmental_sciences", "Environmental sciences", "domaine-SciencesMilieu-suject-EnvironmentalSciences.zip"),
    ("home_economics", "Home economics and accommodation",
     "domaine-EconomieDomHotellerie-subject-HomeEconomicsAccommodationSc.zip"),
    ("humanities", "Humanities and social sciences", "domaine-ScienceHumaines-subject-HumanitiesSocialSciences.zip"),
    ("industries", "Industries", "domaine-subject-industries.zip"),
    ("law_justice", "Law and justice", "domaine-droitJustice-Subject-LawJustice.zip"),
    ("math_physics", "Mathematics, physics and natural sciences",
     "domaine-Math_Physique_ScNaturelles-Subject-Math_Physics_NaturalSc.zip"),
    ("mechanics_heat", "Mechanics and heat", "domaine-MecaniqueEtChaleur-subject-MechanicsAndHeat.zip"),
    ("medicine_health", "Medicine and health", "domaine-MedecineEtSante-subject-MedicineAndHealth.zip"),
    ("metallurgy", "Metallurgy", "domaine-metallurgie-sbject-metallurgy.zip"),
    ("military_security", "Military and security", "domaine-MilitaireEtSecurite-Subject-MilitaryAndSecurity.zip"),
    ("mines_quarries", "Mines and quarries", "domaine-MinesEtCarrieres-subject-MinesAndQuarries.zip"),
    ("names_titles", "Names and titles", "domaine-Appellations-subject-NamesAndTitles.zip"),
    ("petroleum", "Petroleum", "domaine-petrole-subject-petroleum.zip"),
    ("space_robotics", "Space robotics", "domaine-RobotiqueSpatiale-subject-SpaceRobotics.zip"),
    ("telecommunications", "Telecommunications and postal service",
     "domaine-TelecommunicationsPostes-subject-TelecommunicationsPostalService.zip"),
    ("transportation", "Transportation and materials handling",
     "domaine-TransportManutention-subject-TransportationMaterialsHandling.zip"),
]
TERMIUM = {k: (subject, f) for k, subject, f in TERMIUM_SUBJECTS}
TERMS_PER_PAGE = 250


def termium_rows(csv_text):
    """[(English, French, Spanish, Portuguese, subject)] of one TERMIUM Plus CSV file (its first line names the
    columns); a row without an English or a French term is left out."""
    out = []
    for r in csv.DictReader(io.StringIO(csv_text.lstrip("﻿"))):
        en, fr = (r.get("TERM_EN") or "").strip(), (r.get("TERME_FR") or "").strip()
        if en and fr:
            out.append((en, fr, (r.get("TERME_TERM_ES") or "").strip(), (r.get("TERME_TERM_PT") or "").strip(),
                        (r.get("SUBJECT_EN") or "").strip()))
    return out


def termium_sorted(rows):
    """The rows without repeats, in alphabetical order of the English term (case and accents aside)."""
    import unicodedata

    def plain(text):
        """A word without accents, in small letters, for sorting."""
        return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))
    return sorted(set(rows), key=lambda r: (plain(r[0]), r))


def termium_pages(subject, rows, limit=None):
    """[(path, title, body HTML)] of the rows, TERMS_PER_PAGE to a page, each page titled by its first and last
    English terms."""
    import build_textbooks as B
    out = []
    for start in range(0, len(rows), TERMS_PER_PAGE):
        if limit and len(out) >= limit:
            break
        chunk = rows[start:start + TERMS_PER_PAGE]
        body = ("<table><tr><th>English</th><th>French</th><th>Spanish</th><th>Portuguese</th><th>Subject</th></tr>" +
                "".join(f'<tr><td>{B.esc(en)}</td><td lang="fr">{B.esc(fr)}</td><td lang="es">{B.esc(es)}</td>'
                        f'<td lang="pt">{B.esc(pt)}</td><td>{B.esc(sub)}</td></tr>' for en, fr, es, pt, sub in chunk) +
                "</table>")
        out.append((f"terms-{start + 1}", f"{chunk[0][0][:40]} to {chunk[-1][0][:40]}", body))
    return out


def termium_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one TERMIUM Plus subject ("termium:<subject>"): the licence checked on the dataset's record, its
    zip file downloaded once (kept in the cache folder for 30 days), every CSV file in it read."""
    import build_textbooks as B
    key = name.split(":", 1)[1] if ":" in name else ""
    if key not in TERMIUM:
        left_out.append({"title": name, "reason": "Unknown subject."})
        return None
    subject, file_name = TERMIUM[key]
    if not re.search(TERMIUM_TEXT, B.fetch(TERMIUM_DATASET, cache)):
        left_out.append({"title": name, "reason": "The dataset's record no longer names the Open Government Licence - "
                                                  "Canada."})
        return None
    url = f"{TERMIUM_FILES}/{file_name}"
    path = K.download_file(url, cache, name=f"termium-{key}.zip", max_age_days=30)
    rows = []
    with zipfile.ZipFile(path) as z:
        for member in z.namelist():
            if member.lower().endswith(".csv"):
                rows += termium_rows(z.read(member).decode("utf-8", "replace"))
    rows = termium_sorted(rows)
    if not rows:
        left_out.append({"title": name, "reason": "The file has no terms with English and French."})
        return None
    book = K.new_book(f"lgov_termium_{key}", f"TERMIUM Plus: {subject} (English, French, Spanish, Portuguese)",
                      "Language learning: terminology (English and French)", GROUP, "Translation Bureau, Public "
                      "Services and Procurement Canada (Government of Canada)", "OGL-Canada",
                      "https://open.canada.ca/en/open-government-licence-canada", TERMIUM_PAGE,
                      f"The Government of Canada's terminology bank for {subject.lower()}: {len(rows):,} terms, each "
                      f"in English and French, with Spanish and Portuguese where the bank gives them, in "
                      f"alphabetical order of the English term, {TERMS_PER_PAGE} to a page.", TERMIUM_NOTICE,
                      country="Canada", level="reference",
                      changes="each term's English, French, Spanish and Portuguese forms and subject put in a table, "
                              "sorted alphabetically; the bank's notes and sources left out")
    book.version = f"TERMIUM Plus open data, read {datetime.date.today().isoformat()}"
    book.originals.append({"url": url, "kind": "zip", "size": os.path.getsize(path)})
    for page_path, title, body in termium_pages(subject, rows, limit):
        book.pages.append(B.Page(page_path, title, body, 0, subject))
    return book


def termium_sign(name):
    """A subject's sign of change: the server's date and size of its zip file."""
    import updates
    return K.sha(updates.head_signs(f"{TERMIUM_FILES}/{TERMIUM[name.split(':', 1)[1]][1]}"))


# ====================================================================== the collection and its words

def fsi_keys():
    """The keys of the FSI courses (request word lgov-fsi)."""
    return [f"lgov:fsi:{c['key']}" for c in FSI_COURSES]


def dli_keys():
    """The keys of the DLI courses and survival kits (request word lgov-dli)."""
    return [f"lgov:dli:{c['key']}" for c in DLI_COURSES] + [f"lgov:lsk:{k}" for k, _l, _n in LSK_LANGUAGES]


def cip_keys():
    """The keys of the Countries in Perspective books (request word lgov-dli-countries)."""
    return [f"lgov:{e['name']}" for e in CIP_PDFS]


def military_keys():
    """The keys of the War Department's language guides, phrase books and dictionaries (request word lgov-military)."""
    return [f"lgov:{e['name']}" for e in MILITARY_PDFS]


def other_gov_keys():
    """The keys of the other governments' books (request word lgov-other-gov)."""
    return [f"lgov:{e['name']}" for e in OTHER_US_PDFS] + [f"lgov:termium:{k}" for k, _s, _f in TERMIUM_SUBJECTS]


COLLECTION = K.Collection(
    "lgov", GROUP, pdfs=CIP_PDFS + MILITARY_PDFS + OTHER_US_PDFS,
    makers={"fsi": (course_book, course_sign), "dli": (course_book, course_sign), "lsk": (lsk_book, lsk_sign),
            "termium": (termium_book, termium_sign)},
    pieces={"fsi": lambda: [c["key"] for c in FSI_COURSES], "dli": lambda: [c["key"] for c in DLI_COURSES],
            "lsk": lambda: [k for k, _l, _n in LSK_LANGUAGES], "termium": lambda: [k for k, _s, _f in TERMIUM_SUBJECTS]},
    words={"lgov-fsi": fsi_keys, "lgov-dli": dli_keys, "lgov-dli-countries": cip_keys, "lgov-military": military_keys,
           "lgov-other-gov": other_gov_keys,
           "languages-gov": lambda: fsi_keys() + dli_keys() + military_keys() + other_gov_keys()})

LICENCE_LINES = {
    "lgov_fsi": "Foreign Service Institute courses: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
                "policies page at every build), read from the Internet Archive (robots.txt allows programs; the ERIC "
                "microfiche copies are the Department of Education's) and from fsi-languages.yojik.eu (robots.txt: "
                "\"Allow crawling of all content\", checked 2026-11-23). The audio is listed, never downloaded.",
    "lgov_dli": "Defense Language Institute courses from the Internet Archive: works of the US government, judged at "
                "every build by the release rule for military publications (military_release.py).",
    "lgov_fieldsupport": "DLIFLC Field Support (fieldsupport.dliflc.edu, robots.txt allows all but its search page, "
                         "checked 2026-11-23): Language Survival Kits and Countries in Perspective, published openly "
                         "by the Defense Language Institute; works of the US government (17 U.S.C. 105); "
                         "www.dliflc.edu/privacy: \"Information presented on this site is considered public "
                         "information and may be distributed or copied unless otherwise specified\" (checked at every "
                         "build). The products' pages show \"Copyright DLIFLC\"; the notice says so.",
    "lgov_military": "War Department language guides, phrase books and dictionaries (1941 to 1945) from the Internet "
                     "Archive: works of the US government, judged at every build by the military release rule.",
    "lgov_native": "Bureau of American Ethnology, Smithsonian, Bureau of Indian Affairs and Navy dictionaries and "
                   "grammars from the Internet Archive: works of the US government (17 U.S.C. 105).",
    "lgov_termium": "open.canada.ca's record of TERMIUM Plus (checked at every build): \"Open Government Licence - "
                    "Canada\"; its files at donnees-data.tpsgc-pwgsc.gc.ca (no robots.txt, checked 2026-11-23).",
}

NOT_INCLUDED = [
    ("DLIFLC Rapport and the Cultural Orientation courses", "Both need a sign-in (an account) on the Field Support "
     "site (checked 2026-11-23); not read. Index: https://fieldsupport.dliflc.edu/"),
    ("DLIFLC Headstart2", "An online program with lessons in the browser, not text files; the older Headstart "
     "programs on the Internet Archive are built (lgov:dli:german_headstart, lgov:dli:headstart_philippines). Index: "
     "https://hs2.dliflc.edu/"),
    ("DLIFLC Language Survival Kits: the weapons guides", "Behind a sign-in (their addresses go to "
     "fieldsupport.dliflc.edu/products/secure/). Index: https://fieldsupport.dliflc.edu/productList.aspx?v=lsk"),
    ("DLI Headstart programs on fsi-languages.yojik.eu (Japanese, Korean, Norwegian, Italian, German, Spanish for "
     "Latin America, Puerto Rico and Spain, French for Belgium)", "Copies on a private mirror, not on a government "
     "site or the Internet Archive, so the military release rule does not let them in. Link-only. Index: "
     "https://fsi-languages.yojik.eu/languages/fsi.html"),
    ("DLI Japanese Basic Course (1967, 21 volumes, Internet Archive)", "Its front pages print \"It is NOT for general "
     "distribution\" and no government site publishes it: personal use at most. Link-only. Index: "
     "https://archive.org/details/Japanese-Basic-Course"),
    ("DLI French Basic Course (1968, ERIC ED 029 529 to 531) and DLI Russian Basic Course volumes (ERIC ED 029 532)",
     "Their front pages print \"solely for official purposes ... NOT for general distribution\" and ERIC's stamp "
     "\"permission to reproduce this copyrighted material\". Link-only. Index: https://files.eric.ed.gov/fulltext/"
     "ED029531.pdf"),
    ("DLI Korean Basic Course (1966, ERIC ED 024 943), DLI Indonesian Basic Course volumes 1 to 3 (1971, ERIC ED 057 "
     "696, 057 707, 058 791), DLI Czech Basic Course volume III and grammar (1971 to 1972)", "ERIC's copies carry "
     "the stamp \"permission to reproduce this copyrighted material\" or \"not for general distribution\". "
     "Link-only. Index: https://archive.org/details/micro_IA41153063_0150"),
    ("DLI Speak Better Russian: A Conversation Manual", "It says it uses copyrighted material by permission. "
     "Link-only. Index: https://archive.org/details/defense-language-institute-speak-better-russian-a-conversation-"
     "manual"),
    ("DLI Thai Modular Course (2002 to 2003, 178 files on the Internet Archive)", "A community upload of many loose "
     "files; the FSI Thai course and the DLI Thai Basic Course of 1967 are built. Index: https://archive.org/details/"
     "dli-thai"),
    ("FSI courses whose only copies are scans without a text layer (fsi-languages.yojik.eu): Bengali, Czech FAST and "
     "the Czech basic course, Romanian Reference Grammar, Russian Active Introduction, Persian (Spoken Persian, A "
     "Reader in Modern Persian), Portuguese Programmatic, Turkish volume 2, Levantine and Egyptian Arabic, Nepali "
     "(audio only), French Bridges and the French supplementary exercises", "Scans without their words cannot be "
     "read aloud (checked 2026-11-23); their audio is on the same pages. Index: https://fsi-languages.yojik.eu/"
     "languages/fsi.html"),
    ("Army Pocket Guides of the Second World War (to France, China, Iran and others)", "Country guides for soldiers, "
     "not language courses (a few pages of phrases each); not built here. Index: https://archive.org/details/"
     "PocketGuideToFrance"),
    ("Native American language materials in ERIC by schools, universities and tribes (Navajo, Hawaiian, Cherokee, "
     "Lakota, Yupik)", "Their publishers are not the federal government, so their copyright is not settled; the "
     "federal dictionaries and grammars are built. Index: https://eric.ed.gov/?q=native+language"),
    ("Hawaii State Department of Education Hawaiian language materials", "A state government's works are not public "
     "domain by law and no open licence was found. Link-only. Index: https://archive.org/details/ERIC_ED200029"),
    ("New Zealand: Te Taura Whiri i te Reo Māori and the Ministry of Education's te reo Māori resources",
     "tetaurawhiri.govt.nz shows its pages only through scripts (no licence statement could be read) and "
     "tereomaori.tki.org.nz refuses programs (403, checked 2026-11-23). Link-only. Index: "
     "https://www.tetaurawhiri.govt.nz/"),
    ("Wales: Learn Welsh (National Centre for Learning Welsh)", "No open licence statement on learnwelsh.cymru "
     "(checked 2026-11-23); its courses are its own copyright. Link-only. Index: https://learnwelsh.cymru/"),
    ("Ireland: téarma.ie (National Terminology Database for Irish) and Scotland: LearnGaelic", "No open licence for "
     "bulk reuse was found (checked 2026-11-23). Link-only. Index: https://www.tearma.ie/"),
    ("European Union: IATE terminology and the DGT translation memories", "Terminology and translation data, not "
     "learning material; IATE answers no robots.txt (404) and its download page asks for acceptance of terms. "
     "Link-only. Index: https://iate.europa.eu/download-iate"),
    ("UK: GOV.UK and British Council language material", "GOV.UK publishes no language courses (its content is under "
     "the Open Government Licence); the British Council is not the government and its material is its copyright. "
     "Index: https://www.britishcouncil.org/english"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
