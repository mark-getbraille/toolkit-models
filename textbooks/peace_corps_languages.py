"""The Peace Corps's language courses for the reference library, in the group "Reference, language learning" (the
owner's request of 2026-11-23: every Peace Corps manual and guide; this module has the language courses). Keys:
pclang:index (a guide to every language, in plain words) and pclang:<course>. Request words: peace-corps-languages
(every book), pclang-africa, pclang-asia-pacific, pclang-europe-asia, pclang-americas and pclang-mena.

What this module builds, in plain words:
  - the language courses, lesson books, phrasebooks, grammars, dictionaries and technical-language lessons the Peace
    Corps wrote for training its volunteers, from the 1960s to 2013, one book per course (every volume of it), for
    the countries it served in Africa, Asia and the Pacific, Eastern Europe and Central Asia, Latin America and the
    Caribbean, and North Africa and the Middle East;
  - each course's TEXT is the book, read with the builder's PDF reader (pdf_set.pdf_set_book, the same as the FSI
    courses of languages.py), from one of two places, both allowing programs:
      * the Internet Archive's copies of ERIC documents ("ERIC_ED......"), when ERIC's record names a Peace Corps
        office as the document's author ("institution"), checked with ERIC's own records on 2026-11-23;
      * fsi-languages.yojik.eu's copy of the Peace Corps language archive (its robots.txt: "Allow crawling of all
        content"; languages.py already reads its FSI courses), for the courses ERIC does not have: the Peace Corps's
        "Language Lessons" for invitees (2005 to 2011) with their recordings, the Togo workbooks of 2010, the Gambia
        tape scripts, and later manuals;
  - each course's AUDIO, where the Peace Corps recorded it, is not downloaded: every MP3 file is listed in the book's
    "originals" (address and size, from the archive's folder list) for the owner to download himself, as for the FSI
    courses;
  - pclang:index: every language in plain words: where it is spoken, which course or courses the library has (key,
    year and level), whether recordings are listed, and the courses that are links only, with the reason.

Checked and NOT built (NOT_INCLUDED, link-only, each with its reason and address): courses written for the Peace
Corps under contract by universities and companies (the "Peace Corps Language Handbook Series" of the Experiment in
International Living, Michigan State University, the Center for Applied Linguistics, CHP International, Brigham Young
University, Indiana University, the University of Hawaii, George Washington University, Lingoco and Wisma Bahasa):
a contractor's work is not a work of the US government, and these copies carry no public-domain statement; books
whose own pages ask for permission to copy them (the 1965 Gambia courses, the Aklanon grammar, Beginning Aymara, the
Yemen field guide, the Tetun course); books written by single volunteers in their own names (volunteers are not
federal employees for copyright); scans whose text cannot be read (the machine-read text is mostly nonsense: Spoken
Twi, Conversational Telugu, Lessons in Ponapean, Madi from ERIC, the Thai dictionaries, the Bulgarian, Russian and
Mongolian books whose Cyrillic was misread); ERIC records without a copy (Krio, Mende, Susu, Chichewa, Lao, Tuvaluan,
Wolof teacher's manual); and Live Lingua's own pages (built by scripts, with no terms allowing programs; the same
government works are read from the copies above). Already in the library and not repeated: the Peace Corps Tagalog
correspondence course (lang:fsi:tagalog, languages.py), listed in the index.

Licences: the Peace Corps is a US government agency; works its staff make are public domain (17 U.S.C. 105, the line
checked on govinfo.gov's policies page at every build). Every book says which Peace Corps office made it and where it
was read, and notes poor scans in its notice.

Run from the repository's folder:
  python3 textbooks/peace_corps_languages.py pclang:swahili_tanzania_1994 --out build/textbooks --limit 3
  python3 textbooks/peace_corps_languages.py --list pclang-africa
"""

import datetime
import html as _html
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import languages as L  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = L.GROUP                       # "languages": the same group as the FSI courses
GROUPS = dict(L.GROUPS)               # {"languages": "Reference, language learning"}

IA = "https://archive.org"
YOJIK_PC = "https://fsi-languages.yojik.eu/languages/PeaceCorps"
PUBLISHER = "US Peace Corps"

# The regions: (request word, title, what the region covers).
REGIONS = {
    "africa": ("pclang-africa", "Africa", "West, Central, East and Southern Africa and the Indian Ocean islands"),
    "asia-pacific": ("pclang-asia-pacific", "Asia and the Pacific", "South and East Asia and the Pacific islands"),
    "europe-asia": ("pclang-europe-asia", "Eastern Europe and Central Asia",
                    "the Balkans, the Baltic, the Black Sea and Caucasus countries and Central Asia"),
    "americas": ("pclang-americas", "Latin America and the Caribbean", "Central and South America and the Caribbean"),
    "mena": ("pclang-mena", "North Africa and the Middle East", "Morocco, Tunisia and Jordan"),
    "general": ("", "Learning any language", "learning a language as a volunteer, for every country"),
}

# Every language: (region, where it is spoken, in plain words).
LANGS = {
    # Africa
    "Swahili (Kiswahili)": ("africa", "Tanzania, Kenya, Uganda and much of East and Central Africa"),
    "Hausa": ("africa", "Niger, northern Nigeria, northern Ghana and across West Africa as a trade language"),
    "Zarma (Djerma)": ("africa", "western Niger, along the Niger River"),
    "Wolof": ("africa", "Senegal, The Gambia and Mauritania"),
    "Mandinka": ("africa", "The Gambia, Senegal and Guinea-Bissau"),
    "Jahanka": ("africa", "eastern Gambia and Senegal (a Mandinka language)"),
    "Jola (Joola)": ("africa", "southern Senegal (Casamance), The Gambia and Guinea-Bissau"),
    "Pulaar, Pular and Fulfulde (Fula)": ("africa", "across the Sahel from Senegal and Mauritania to Niger, Guinea's "
                                                    "Fuuta Jallon and Cameroon"),
    "Sarahule (Soninke)": ("africa", "Mauritania, Mali, Senegal and The Gambia"),
    "Hassaniya Arabic": ("africa", "Mauritania and Western Sahara"),
    "Bambara": ("africa", "Mali, the main language of its people"),
    "Malinke (Maninka)": ("africa", "western Mali and Guinea"),
    "French": ("africa", "the official language of Mali, Niger, Cameroon, Gabon, the Central African Republic, Togo "
                         "and much of West and Central Africa"),
    "Moore (Mooré)": ("africa", "Burkina Faso, the language of the Mossi"),
    "Kanuri": ("africa", "eastern Niger, northeastern Nigeria and around Lake Chad"),
    "Sara": ("africa", "southern Chad"),
    "Chad Arabic": ("africa", "Chad and neighbouring countries, a spoken Arabic"),
    "Cameroonian Pidgin": ("africa", "Cameroon, especially its English-speaking west"),
    "Lingala": ("africa", "the Democratic Republic of the Congo (formerly Zaire) and the Republic of the Congo"),
    "Ciluba (Tshiluba)": ("africa", "the Kasai region of the Democratic Republic of the Congo"),
    "Kikongo (Kituba)": ("africa", "western Democratic Republic of the Congo, the Republic of the Congo and Angola"),
    "Anufo": ("africa", "northern Togo and Ghana"),
    "Bassar": ("africa", "western Togo"),
    "Ifè": ("africa", "central Togo and Benin"),
    "Ikposso": ("africa", "southwestern Togo"),
    "Kabiyè": ("africa", "northern Togo"),
    "Konkomba": ("africa", "northern Togo and Ghana"),
    "Lamba (Lama)": ("africa", "northern Togo and Benin"),
    "Moba": ("africa", "northern Togo and Burkina Faso"),
    "Tem (Kotokoli)": ("africa", "central Togo"),
    "Ewe": ("africa", "southern Togo and southeastern Ghana"),
    "Basaa": ("africa", "central and southern Cameroon"),
    "Fante": ("africa", "southern Ghana, along the coast (an Akan language)"),
    "Twi": ("africa", "southern and central Ghana (an Akan language)"),
    "Temne": ("africa", "northern and central Sierra Leone"),
    "Krio": ("africa", "Sierra Leone, the language everyone shares"),
    "Mende": ("africa", "southern Sierra Leone"),
    "Susu": ("africa", "coastal Guinea and Sierra Leone"),
    "Crioulo (Kriol)": ("africa", "Guinea-Bissau, a Portuguese creole"),
    "Kriolu (Cape Verdean Creole)": ("africa", "Cape Verde"),
    "Igbo": ("africa", "southeastern Nigeria"),
    "Oromo": ("africa", "Ethiopia and northern Kenya"),
    "Luganda": ("africa", "central Uganda"),
    "Lunyoro and Rutoro": ("africa", "western Uganda"),
    "Lwo and Acholi": ("africa", "northern Uganda"),
    "Madi": ("africa", "northwestern Uganda and South Sudan"),
    "Kikamba": ("africa", "eastern Kenya, east of Nairobi"),
    "Maa (Maasai)": ("africa", "southern Kenya and northern Tanzania"),
    "Chichewa and Nyanja": ("africa", "Malawi, eastern Zambia and Mozambique"),
    "Bemba": ("africa", "northern Zambia"),
    "Sesotho": ("africa", "Lesotho and South Africa"),
    "Setswana": ("africa", "Botswana and South Africa"),
    "siSwati": ("africa", "Eswatini (formerly Swaziland) and South Africa"),
    "Malagasy": ("africa", "Madagascar"),
    "Seychelles Kreol": ("africa", "the Seychelles"),
    "Oshikwanyama and Oshindonga": ("africa", "northern Namibia and southern Angola"),
    "Liberian English": ("africa", "Liberia"),
    # Asia and the Pacific
    "Thai": ("asia-pacific", "Thailand"),
    "Nepali": ("asia-pacific", "Nepal"),
    "Mongolian": ("asia-pacific", "Mongolia"),
    "Chinese (Mandarin)": ("asia-pacific", "China"),
    "Bangla (Bengali)": ("asia-pacific", "Bangladesh and eastern India"),
    "Tagalog (Filipino)": ("asia-pacific", "the Philippines, its national language"),
    "Cebuano": ("asia-pacific", "the central and southern Philippines (Cebu, Bohol and Mindanao)"),
    "Ilokano": ("asia-pacific", "northern Luzon, the Philippines"),
    "Hiligaynon (Ilonggo)": ("asia-pacific", "Panay and Negros, the Philippines"),
    "Bikol": ("asia-pacific", "the Bicol region of southern Luzon, the Philippines"),
    "Ivatan": ("asia-pacific", "the Batanes islands, the far north of the Philippines"),
    "Aklanon": ("asia-pacific", "Aklan province on Panay, the Philippines"),
    "Korean": ("asia-pacific", "Korea"),
    "Hindi": ("asia-pacific", "northern and central India"),
    "Tamil": ("asia-pacific", "southern India (Tamil Nadu) and Sri Lanka"),
    "Telugu": ("asia-pacific", "southern India (Andhra Pradesh and Telangana)"),
    "Dari and Persian": ("asia-pacific", "Afghanistan (Dari) and Iran (Persian, Farsi)"),
    "Sinhala": ("asia-pacific", "Sri Lanka"),
    "Fijian": ("asia-pacific", "Fiji"),
    "Fiji Hindi": ("asia-pacific", "Fiji, among Fijians of Indian descent"),
    "Samoan": ("asia-pacific", "Samoa and American Samoa"),
    "Pohnpeian": ("asia-pacific", "Pohnpei, Federated States of Micronesia"),
    "Solomon Islands Pijin": ("asia-pacific", "the Solomon Islands"),
    "Tok Pisin": ("asia-pacific", "Papua New Guinea"),
    "Bislama": ("asia-pacific", "Vanuatu"),
    "Marshallese": ("asia-pacific", "the Marshall Islands"),
    "Tetun": ("asia-pacific", "Timor-Leste (East Timor)"),
    "Indonesian": ("asia-pacific", "Indonesia"),
    "Lao": ("asia-pacific", "Laos"),
    "Tuvaluan": ("asia-pacific", "Tuvalu"),
    # Eastern Europe and Central Asia
    "Albanian": ("europe-asia", "Albania, Kosovo and western North Macedonia"),
    "Armenian": ("europe-asia", "Armenia"),
    "Azerbaijani": ("europe-asia", "Azerbaijan"),
    "Bulgarian": ("europe-asia", "Bulgaria"),
    "Estonian": ("europe-asia", "Estonia"),
    "Latvian": ("europe-asia", "Latvia"),
    "Georgian": ("europe-asia", "Georgia"),
    "Kazakh": ("europe-asia", "Kazakhstan"),
    "Kyrgyz": ("europe-asia", "Kyrgyzstan"),
    "Macedonian": ("europe-asia", "North Macedonia"),
    "Romanian (and Moldovan)": ("europe-asia", "Romania and Moldova"),
    "Russian": ("europe-asia", "Russia, and widely in Ukraine, Kazakhstan, Kyrgyzstan and Turkmenistan"),
    "Turkmen": ("europe-asia", "Turkmenistan"),
    "Ukrainian": ("europe-asia", "Ukraine"),
    "Uzbek": ("europe-asia", "Uzbekistan"),
    # Latin America and the Caribbean
    "Spanish": ("americas", "Latin America and Spain; these courses are for Uruguay, Chile and Latin America"),
    "Guarani": ("americas", "Paraguay, alongside Spanish"),
    "Jamaican Creole (Patois)": ("americas", "Jamaica"),
    "Q'eqchi'": ("americas", "northern Guatemala and Belize (a Mayan language)"),
    "Sranan Tongo": ("americas", "Suriname"),
    "Aymara": ("americas", "the highlands of Bolivia and Peru"),
    "Kaqchikel": ("americas", "the central highlands of Guatemala (a Mayan language)"),
    "Belizean Creole": ("americas", "Belize"),
    # North Africa and the Middle East
    "Moroccan Arabic (Darija)": ("mena", "Morocco"),
    "Tamazight and Tashelhit (Berber)": ("mena", "the Atlas mountains and the south of Morocco"),
    "Tunisian Arabic": ("mena", "Tunisia"),
    "Jordanian Arabic": ("mena", "Jordan"),
    "Yemeni Arabic": ("mena", "Yemen"),
    # every country
    "Language learning": ("general", "every country"),
}


def folder(path):
    """The address of a folder of the Peace Corps archive on fsi-languages.yojik.eu ("Albanian/Albania Language
    Files" -> its address, spaces as %20, ending in "/")."""
    return f"{YOJIK_PC}/{urllib.parse.quote(path)}/"


def eric(number, part=""):
    """A text source: the Internet Archive's copy of an ERIC document (ERIC_<number>), every PDF of it; part is the
    part's title in the book (empty: the course's title)."""
    return ("ia", f"ERIC_{number}", r"\.pdf$", part)


def yj(path, file_pattern, part=""):
    """A text source: the PDFs of a yojik archive folder whose file name matches file_pattern."""
    return ("page", folder(path), r"/" + file_pattern + r"$", part)


def mp3(path, file_pattern=r"[^/]+\.mp3"):
    """An audio source: the MP3 files of a yojik archive folder whose file name matches file_pattern."""
    return ("page", folder(path), r"/" + file_pattern + r"$")


# What every Peace Corps course's notice says, and the notes on poor scans.
NOTICE = ("Made by the Peace Corps ({office}) for training its volunteers: a work of the US government (public "
          "domain). {source} Peace Corps courses are written for volunteers in a host country, so their dialogues, "
          "prices and customs are those of the country and year of the course.")
FROM_ERIC = "Read from the Internet Archive's copy of ERIC document {number}, whose ERIC record names the Peace Corps."
FROM_YOJIK = ("Read from the Peace Corps language archive's copy on fsi-languages.yojik.eu (it was gathered by Live "
              "Lingua, whose front page may come first).")
POOR_OCR = (" Poor scan: this is an old typewritten copy and the machine-read text has many mistakes, so some words "
            "come out wrong; check doubtful words with a teacher, the recordings or another course.")
SCRIPT_OCR = (" The {script} words of this scan were misread by the scanner and come out as wrong letters; the English "
              "explanations, notes and romanised words read well. Learn the {script} words themselves from a course "
              "with real {script} text or recordings (see the index, pclang:index).")
FONT_NOTE = (" The {script} script is typed in an old font that a screen reader reads as wrong letters; the "
             "romanised words and the English read well.")
AUDIO_LISTED = " Its recordings (MP3) are listed as originals for you to download; they are not inside this book."
NO_AUDIO = " No recordings of it were found, so none are listed."


def course(key, language, title, year, level, office, text, description, audio=(), ocr="", script="",
           country=""):
    """One course: key (pclang:<key>), language (a key of LANGS), title, year, level (course, introduction,
    phrasebook, dictionary, grammar, workbook, teacher's manual, technical lessons), office (the Peace Corps office that
    made it), text sources (eric() or yj()), description, audio sources (mp3()), ocr ("" readable, "poor" a poor
    scan, "script" a foreign script misread, "font" an old-font script) with script (the script's name), country
    (the host country, for the index)."""
    return dict(key=key, language=language, title=title, year=year, level=level, office=office, text=list(text),
                description=description, audio=list(audio), ocr=ocr, script=script, country=country)


# ====================================================================== the courses

COURSES = [
    # ------------------------------------------------------------------ Africa: East
    course("swahili_tanzania_1994", "Swahili (Kiswahili)", "Kiswahili Book for Peace Corps Tanzania", "1994",
           "course", "Peace Corps Tanzania, Arusha", [eric("ED402737")],
           "76 lessons of Swahili for volunteers in Tanzania: vocabulary and phrase lists, a dialogue, grammar notes "
           "and exercises on greetings and introductions, numbers, commands, questions, time, family, shopping and "
           "daily life.", country="Tanzania"),
    course("swahili_kenya_1995", "Swahili (Kiswahili)", "Kiswahili Competency Based Manual (Revised)", "1995",
           "course", "Peace Corps Kenya", [eric("ED402760")],
           "Swahili for volunteers in Kenya: topical lessons with short dialogues, a vocabulary list, grammar notes, "
           "exercises and cultural notes, from greetings, numbers and money onwards.", country="Kenya"),
    course("kikamba_kenya", "Kikamba", "Kikamba Self-Instruction Manual", "", "course", "Peace Corps Kenya",
           [yj("Kikamba", r"Kikamba manual\.pdf")],
           "A self-study Kikamba course from Peace Corps Kenya's training: lessons on greetings, introductions, "
           "work, food, numbers, family and ordering food, each with a dialogue, vocabulary and grammar notes. Its "
           "pages do not name its writers.", country="Kenya"),
    course("maa_kenya", "Maa (Maasai)", "Maasai (Maa) Self-Instruction Manual", "", "course", "Peace Corps Kenya",
           [yj("Maasai", r"Maa manual\.pdf")],
           "A competency-based Maa course written by the language and cross-cultural facilitators of Peace Corps "
           "Kenya: pronunciation, then lessons of dialogues, vocabulary and grammar for daily life.",
           country="Kenya"),
    course("acholi_uganda_2009", "Lwo and Acholi", "Acholi Language Manual (June 2009) and Exercise Workbook",
           "2009", "course", "Peace Corps Uganda",
           [yj("Acholi", r"Acholi Language Manual June 2009\.pdf", "Language manual"),
            yj("Acholi", r"Acholi Excercise Work Book\.pdf", "Exercise workbook")],
           "Peace Corps Uganda's Acholi course: about the language (a tonal Luo language of Gulu, Kitgum, Amuru and "
           "Pader), communicative units with dialogues, vocabulary, grammar and culture notes, an Acholi-English "
           "glossary, and the workbook of practice activities that goes with each unit.", country="Uganda"),
    course("acholi_phrasebook_uganda", "Lwo and Acholi", "Acholi Phrasebook", "2007", "phrasebook",
           "Peace Corps Uganda", [yj("Acholi", r"Acholi Phrasebook\.pdf")],
           "Peace Corps Uganda's Acholi phrasebook, prepared in 2005 and revised in 2007 by its volunteers with a "
           "team of Ugandan writers and translators: everyday phrases by topic.", country="Uganda"),
    course("acholi_survival_uganda", "Lwo and Acholi", "An Introduction to Survival Acholi", "", "introduction",
           "Peace Corps Uganda", [yj("Acholi", r"An Introduction to survival Acholi\.pdf")],
           "Easy, simple Acholi phrases for getting by in Uganda, practised in everyday situations and conversations.",
           country="Uganda"),
    course("luganda_uganda_1969", "Luganda", "Luganda Continuation, Book 2", "1969", "course",
           "Peace Corps Uganda", [eric("ED143240")],
           "The second Luganda book for Peace Corps students (after the 1968 first book): fifteen lessons alternating "
           "conversations on various subjects with grammar notes.", country="Uganda"),
    course("lunyoro_rutoro_uganda_1971", "Lunyoro and Rutoro", "Lunyoro/Rutoro Instructions", "1971", "course",
           "Peace Corps Uganda", [eric("ED148157")],
           "32 lessons of Lunyoro/Rutoro for volunteers: sample phrases to master, with dialogues and conversations on "
           "names, meals and buying food, the weather, health, travel and daily schedules.", ocr="poor",
           country="Uganda"),
    course("lwo_uganda_1971", "Lwo and Acholi", "Lwo Instructions", "1971", "course", "Peace Corps Uganda",
           [eric("ED148160")],
           "95 lessons of Lwo, the dialects of northern Uganda: pattern drills, conversations and notes on grammar and "
           "usage, with eight model conversations and a Lwo-English vocabulary.", country="Uganda"),
    course("madi_uganda_1971", "Madi", "Madi Instructions", "1971", "course", "Peace Corps Uganda",
           [yj("Madi", r"Peace Corps Madi Instructions\.pdf")],
           "Short, simple Madi lessons for volunteers posted where Madi is spoken in northwestern Uganda, prepared "
           "for the Peace Corps by Frederick K. Kamoga of Makerere University with two Madi speakers (ERIC "
           "ED148161 names the Peace Corps as its author; this archive copy's text reads better than ERIC's scan).",
           ocr="poor", country="Uganda"),
    course("oromo_ethiopia_1975", "Oromo", "Oromo for Beginners", "1975", "course", "Peace Corps Ethiopia",
           [eric("ED226615")],
           "An introduction to Oromo (Galla) for volunteers, in the standard language of Wollega, Illubabor and Kaffa "
           "in western Ethiopia.", country="Ethiopia"),
    # ------------------------------------------------------------------ Africa: West (Sahel)
    course("hausa_ghana_1974", "Hausa", "Spoken Hausa for Non-Hausa Beginners", "1974", "course", "Peace Corps Ghana",
           [eric("ED142070")],
           "62 lessons in spoken Hausa, best studied with a Hausa speaker; English only where needed.", ocr="poor",
           country="Ghana"),
    course("hausa_niger_1976", "Hausa", "Cours de Hausa pour le Niger (Hausa Course for Niger), Trainees' Manual",
           "1976", "course", "Peace Corps Niger", [eric("ED290338")],
           "Twelve Hausa lessons for volunteers in Niger, on grammar and vocabulary for daily needs and the market.",
           country="Niger"),
    course("hausa_niger_intro", "Hausa", "An Introduction to the Hausa Language (Peace Corps Niger)", "", "introduction",
           "Peace Corps Niger", [yj("Hausa", r"NE_Hausa_Language_Lessons\.pdf")],
           "Peace Corps Niger's first Hausa lessons for invitees, with the recordings that go with them.",
           audio=[mp3("Hausa", r"NE_Hausa_Lesson[^/]*\.mp3")], country="Niger"),
    course("zarma_niger_intro", "Zarma (Djerma)", "Zarma Language: An Introduction (Peace Corps Niger)", "",
           "introduction", "Peace Corps Niger", [yj("Zarma", r"NE_Zarma_Language_Lessons\.pdf")],
           "Peace Corps Niger's first Zarma lessons for invitees, with the recordings that go with them.",
           audio=[mp3("Zarma", r"NE_Zarma_Lesson[^/]*\.mp3")], country="Niger"),
    course("zarma_niger_1995", "Zarma (Djerma)", "Technical Language Manual for AFSI/NRM Volunteers: Zarma", "1995",
           "technical lessons", "Peace Corps Niger, Niamey", [eric("ED402777")],
           "Zarma for agriculture and natural resource volunteers in Niger: useful phrases, then the words and talk "
           "of farming, gardens, trees and village work.", country="Niger"),
    course("djerma_niger_1966", "Zarma (Djerma)", "Djerma Basic Course", "1966", "course", "Peace Corps",
           [eric("ED143238")],
           "The essential structure of Djerma as spoken in western Niger, in 30 units for 300 to 400 hours of "
           "intensive classes.", ocr="poor", country="Niger"),
    course("fulfulde_niger_1993", "Pulaar, Pular and Fulfulde (Fula)", "Manuel de Fulfulde (Fulfulde Manual)",
           "1993", "course", "Peace Corps Niger, Niamey", [eric("ED401765")],
           "32 Fulfulde lessons for volunteers in Niger, each on one competency, in ten themes from greetings and "
           "introductions to daily life.", country="Niger"),
    course("fulfulde_dictionary_niger_1991", "Pulaar, Pular and Fulfulde (Fula)",
           "Dictionnaire de Fulfulde (Fulfulde Dictionary), Trainee's Book", "1991", "dictionary",
           "Peace Corps Niger, Niamey", [eric("ED403752")],
           "A Fulfulde dictionary for volunteers in Niger: pronouns and verb endings, then English words with their "
           "French and Fulfulde, and the reverse.", country="Niger"),
    course("kanuri_niger_1993", "Kanuri", "Manuel de Kanuri (Kanuri Manual)", "1993", "course",
           "Peace Corps Niger, Niamey", [eric("ED401747")],
           "Kanuri lessons in ten themes: introductions, family, greetings and condolences, needs, shopping, the "
           "tailor, meals, directions, travel, daily activities and gardening.", country="Niger"),
    course("kanuri_niger_chad_1966", "Kanuri", "Kanouri (lessons in French)", "1966", "course", "Peace Corps",
           [eric("ED131695")],
           "Lessons in French introducing Kanuri, made for the Niger-Chad Peace Corps training of summer 1966.",
           ocr="poor", country="Niger and Chad"),
    course("wolof_senegal_1980", "Wolof", "Practical Course in Wolof: An Audio-Aural Approach", "1980", "course",
           "Peace Corps Senegal", [eric("ED226616")],
           "A Wolof course for Senegal and The Gambia, to be taught by a Wolof speaker in intensive sessions.",
           country="Senegal"),
    course("wolof_mauritania_intro", "Wolof", "Wolof Lessons (Peace Corps Mauritania)", "", "introduction",
           "Peace Corps Mauritania", [yj("Wolof", r"MR_Wolof_Language_Lessons\.pdf")],
           "Ten first Wolof lessons from Peace Corps Mauritania: the alphabet, vocabulary, greetings, numbers, days, "
           "introducing yourself, leave-taking and useful phrases, with recordings.",
           audio=[mp3("Wolof", r"MR_Wolof_Lesson[^/]*\.mp3")], country="Mauritania"),
    course("wolof_gambia_tape", "Wolof", "Trainee Wolof Manual: Tape Script (Peace Corps The Gambia)", "",
           "introduction", "Peace Corps The Gambia", [yj("Wolof", r"Peace Corps- Wolof Course\.pdf")],
           "The Gambia's pre-service Wolof tape script: greetings, questions and everyday exchanges, Wolof with "
           "English.", country="The Gambia"),
    course("mandinka_gambia_tape", "Mandinka", "Mandinka Language Tape Script (Peace Corps The Gambia)", "",
           "introduction", "Peace Corps The Gambia", [yj("Mandinka", r"Peace Corps - Mandinka Course\.pdf")],
           "The Gambia's pre-service Mandinka tape script: greetings and everyday exchanges, Mandinka with English.",
           country="The Gambia"),
    course("mandinka_french_lexicon_1968", "Mandinka", "Lexique Mandinque-Francais (Mandinka-French Lexicon)",
           "1968", "dictionary", "Peace Corps", [eric("ED144352")],
           "A Mandinka-French glossary with sample sentences and notes on grammar and usage.", ocr="poor",
           country="Senegal and The Gambia"),
    course("jahanka_gambia", "Jahanka", "Jahanka Language Tape Script (Peace Corps The Gambia)", "", "introduction",
           "Peace Corps The Gambia", [yj("Jahanka", r"Peace Corps-Jahanka course\.pdf")],
           "The Gambia's pre-service Jahanka tape script, with its recordings: greetings and everyday exchanges.",
           audio=[mp3("Jahanka/audios")], country="The Gambia"),
    course("jola_gambia", "Jola (Joola)", "Joola Tape Script (Peace Corps The Gambia)", "", "introduction",
           "Peace Corps The Gambia", [yj("Jola", r"Peace Corps-Jola Course\.pdf")],
           "The Gambia's pre-service Joola tape script, with its recordings: greetings and everyday exchanges.",
           audio=[mp3("Jola/audios")], country="The Gambia"),
    course("pulaar_gambia_tape", "Pulaar, Pular and Fulfulde (Fula)", "Pulaar Language Tape Script (Peace Corps The "
           "Gambia)", "", "introduction", "Peace Corps The Gambia",
           [yj("Pulaar-Mauritania", r"Peace Corps- Pulaar Course\.pdf")],
           "The Gambia's pre-service Pulaar tape script: greetings and everyday exchanges, Pulaar with English.",
           country="The Gambia"),
    course("sarahule_gambia", "Sarahule (Soninke)", "Sarahule Tape Scripts, Workbook and Dictionary (Peace Corps The "
           "Gambia)", "2013", "course", "Peace Corps The Gambia",
           [yj("Sarahulle", r"Peace Corps- Sarahulle Course - 2013\.pdf", "Tape scripts (2013)"),
            yj("Sarahulle", r"Peace Corps- Sarahulle Course\.pdf", "Tape scripts (earlier edition)"),
            yj("Sarahulle", r"Sarahule workbook\.pdf", "Workbook"),
            yj("Sarahulle", r"Sarahule workbook answers\.pdf", "Workbook answers"),
            yj("Sara", r"Sarahule dictionary\.pdf", "English-Sarahule and Sarahule-English dictionary")],
           "Peace Corps The Gambia's Sarahule (Soninke) materials: the tape scripts of greetings and daily talk, a "
           "56-page workbook on origins, greetings, numbers, transport, shopping, time, family, verbs, food, housing "
           "and more, its answers, and a small two-way dictionary.", country="The Gambia"),
    course("pulaar_1987", "Pulaar, Pular and Fulfulde (Fula)", "Pulaar Language Manual", "1987", "course",
           "Peace Corps", [eric("ED290339")],
           "A Pulaar guide for volunteers: the alphabet and its sounds, twelve lessons of culture notes, vocabulary, "
           "dialogue and grammar, and Pulaar-English-French glossaries.", country="Senegal"),
    course("pulaar_mauritania_intro", "Pulaar, Pular and Fulfulde (Fula)", "Pulaar Lessons (Peace Corps Mauritania)",
           "", "introduction", "Peace Corps Mauritania",
           [yj("Pulaar-Mauritania", r"MR_Pulaar_Language_Lessons\.pdf")],
           "Ten first Pulaar lessons from Peace Corps Mauritania: the alphabet, vocabulary, greetings, numbers, days, "
           "introductions, leave-taking and useful phrases, with recordings.",
           audio=[mp3("Pulaar-Mauritania/audios", r"MR_Pulaar_Lesson[^/]*\.mp3")], country="Mauritania"),
    course("pular_guinea", "Pulaar, Pular and Fulfulde (Fula)", "Learner's Guide to Pular (Fuuta Jallon)", "",
           "grammar", "Peace Corps Guinea", [yj("Pulaar-Mauritania", r"Peace Corps Learner Guide to Pular\.pdf")],
           "A guide to the Pular of Guinea's Fuuta Jallon, written to go with Peace Corps Guinea's three-month "
           "training: a short history of the Fulbe, how the language works, tips for learning at post and further "
           "reading.", country="Guinea"),
    course("hassaniya_mauritania_intro", "Hassaniya Arabic", "Hassaniya Lessons (Peace Corps Mauritania)", "",
           "introduction", "Peace Corps Mauritania",
           [yj("Arabic-Mauritanian", r"MR_Hassaniya_Language_Lessons\.pdf")],
           "Ten first Hassaniya lessons from Peace Corps Mauritania: the alphabet, vocabulary, greetings, numbers, "
           "days, introductions, leave-taking and useful phrases, with recordings.",
           audio=[mp3("Arabic-Mauritanian/audios", r"MR_Hassaniya_Lesson[^/]*\.mp3")], country="Mauritania"),
    course("soninke_mauritania_intro", "Sarahule (Soninke)", "Soninke Lessons (Peace Corps Mauritania)", "",
           "introduction", "Peace Corps Mauritania", [yj("Soninke", r"MR_Soninke_Language_Lessons\.pdf")],
           "Ten first Soninke lessons from Peace Corps Mauritania, with recordings.",
           audio=[mp3("Soninke", r"MR_Soninke_Lesson[^/]*\.mp3")], country="Mauritania"),
    course("bambara_mali_intro", "Bambara", "An Introduction to Bambara (Peace Corps Mali)", "", "introduction",
           "Peace Corps Mali", [yj("Bambara", r"ML_Bambara_Language_Lessons\.pdf")],
           "Peace Corps Mali's first Bambara lessons, the script of thirteen recordings.",
           audio=[mp3("Bambara", r"ML_Bambara_Lesson[^/]*\.mp3")], country="Mali"),
    course("french_mali_intro", "French", "An Introduction to French (Peace Corps Mali)", "", "introduction",
           "Peace Corps Mali", [yj("Bambara", r"ML_French_Language_Lessons\.pdf")],
           "Peace Corps Mali's first French lessons for invitees, the script of seventeen recordings.",
           audio=[mp3("Bambara", r"ML_French_Lesson[^/]*\.mp3")], country="Mali"),
    course("malinke_mali", "Malinke (Maninka)", "Malinke Introductory Book: Learner's Guide", "", "course",
           "Peace Corps Mali", [yj("Maninka-Malinke", r"MalinkeManualLearneguide\.pdf")],
           "Malinke as spoken in Bafing and Gangaran in western Mali, by competency: greetings, introductions, "
           "places, directions and daily life, with culture notes, grammar, tasks and self-evaluation.",
           country="Mali"),
    course("moore_burkina_intro", "Moore (Mooré)", "An Introduction to the Moore Language (Peace Corps Burkina "
           "Faso)", "", "introduction", "Peace Corps Burkina Faso",
           [yj("BurkinaFaso", r"BF_Moore_Language_Lessons\.pdf")],
           "Peace Corps Burkina Faso's first Moore lessons, the script of 21 recordings.",
           audio=[mp3("BurkinaFaso", r"BF_Moore_Lesson[^/]*\.mp3")], country="Burkina Faso"),
    # ------------------------------------------------------------------ Africa: Central
    course("sara_chad_1966", "Sara", "Sara Basic Course and Sara Intermediate Course", "1966", "course",
           "Peace Corps", [eric("ED143239", "Basic course"), eric("ED152113", "Intermediate course")],
           "Sara, a language of southern Chad: the basic course (95 short cycles of mimicry and conversation, modelled "
           "on the FSI's experimental Hausa course) and the intermediate course (40 readings and dialogues in Sara "
           "with English translations).", country="Chad"),
    course("chad_arabic_1966", "Chad Arabic", "Spoken Chad Arabic", "1966", "course", "Peace Corps",
           [eric("ED144356")],
           "An intensive course in spoken Chad Arabic for about 360 hours, starting with a listening phase of 60 "
           "lessons.", ocr="poor", country="Chad"),
    course("cameroon_pidgin_1983", "Cameroonian Pidgin", "An Introduction to Cameroonian Pidgin, Student's Book "
           "(Second Edition)", "1983", "course", "Peace Corps Cameroon", [eric("ED255041")],
           "The background, sounds and alphabet of Cameroonian Pidgin, then fifteen lessons on greetings, the tenses, "
           "pronouns, question words and everyday verbs.", country="Cameroon"),
    course("french_cameroon_intro", "French", "French Pre-Departure Lessons (Peace Corps Cameroon)", "",
           "introduction", "Peace Corps Cameroon", [yj("French-Cameroon", r"CM_French_Language_Lessons\.pdf")],
           "Peace Corps Cameroon's online French course before departure: the expressions you need in your first days "
           "with a host family and in the training town, with recordings.",
           audio=[mp3("French-Cameroon")], country="Cameroon"),
    course("french_gabon_math_1987", "French", "Peace Corps Gabon Technical Language: Math/Education", "1987",
           "technical lessons", "Peace Corps Gabon", [eric("ED290336")],
           "Six lessons of technical French for volunteers teaching mathematics in Gabon, with notes on Gabon's "
           "schools.", country="Gabon"),
    course("french_car_1991", "French", "Le francais fonde sur la competence (Competency Based French), four levels",
           "1991", "course", "Peace Corps Central African Republic, Bangui",
           [eric("ED401734", "Novice"), eric("ED401735", "Intermediate"), eric("ED401736", "Advanced"),
            eric("ED401737", "Superior")],
           "French for volunteers in the Central African Republic at four levels, each a series of topical lessons "
           "of competencies and short situational dialogues.", country="Central African Republic"),
    course("lingala_zaire_1986", "Lingala", "Lingala, Livre du formateur (Teacher's Manual)", "1986",
           "teacher's manual", "Peace Corps Zaire, Bukavu Teaching Center", [eric("ED294440")],
           "Twenty lessons for teaching volunteers spoken Lingala in six weeks, with culture through texts and "
           "discussion (in French and Lingala).", country="Zaire (Democratic Republic of the Congo)"),
    course("ciluba_zaire_1986", "Ciluba (Tshiluba)", "Ciluba, Livre du formateur (Teacher's Manual)", "1986",
           "teacher's manual", "Peace Corps Zaire, Bukavu Teaching Center", [eric("ED294441")],
           "Twenty lessons for teaching volunteers spoken Ciluba in six weeks (in French and Ciluba).",
           country="Zaire (Democratic Republic of the Congo)"),
    course("kikongo_zaire_1986", "Kikongo (Kituba)", "Kikongo, Livre du formateur (Teacher's Manual)", "1986",
           "teacher's manual", "Peace Corps Zaire, Bukavu Teaching Center", [eric("ED294442")],
           "Twenty lessons for teaching volunteers spoken Kikongo in six weeks (in French and Kikongo).",
           country="Zaire (Democratic Republic of the Congo)"),
    # ------------------------------------------------------------------ Africa: Togo, Ghana, coast
    *[course(f"{k}_togo_2010", lang, f"{name} Oral Proficiency Learning Workbook (Peace Corps Togo)", "2010",
             "workbook", "Peace Corps Togo", [yj(path, file)],
             f"Peace Corps Togo's first {name} manual for its trainees and volunteers (2010): lessons for speaking "
             "in daily life, with vocabulary, dialogues, grammar and culture notes.", country="Togo")
      for k, lang, name, path, file in [
          ("anufo", "Anufo", "Anufo", "Anufo-Chokossi", r"anufo\.pdf"),
          ("bassar", "Bassar", "Bassar (Ncam)", "Bassar", r"bassar2010\.pdf"),
          ("ife", "Ifè", "Ifè", "Ifè", r"ife2010\.pdf"),
          ("ikposso", "Ikposso", "Ikposso", "Ikposso-Kposo", r"ikposso2010\.pdf"),
          ("kabiye", "Kabiyè", "Kabiyè", "Kabiyè", r"kabiye2010\.pdf"),
          ("konkomba", "Konkomba", "Konkomba (Likpakpaaln)", "Konkomba", r"konkomba2010\.pdf"),
          ("lamba", "Lamba (Lama)", "Lamba (Lama)", "Lamba", r"lamba2010\.pdf"),
          ("moba", "Moba", "Moba", "Moba", r"moba2010\.pdf"),
          ("tem", "Tem (Kotokoli)", "Tem", "Tem-Tembo", r"tem2010\.pdf")]],
    course("fante_ghana_1974", "Fante", "Spoken Fante for Non-Fante Beginners", "1974", "course", "Peace Corps Ghana",
           [eric("ED140608")],
           "66 lessons in spoken Fante, best studied with a Fante speaker; English only where needed.",
           country="Ghana"),
    course("twi_ghana_intro", "Twi", "Twi for All: An Introduction to the Akan Twi Language (Peace Corps Ghana)", "",
           "introduction", "Peace Corps Ghana", [yj("Twi", r"GH_Twi_Language_Lessons\.pdf")],
           "Peace Corps Ghana's introduction to Twi: key words, phrases and sentences with their pronunciation, notes "
           "on greetings and Ghana's languages, and the index of the recordings.",
           audio=[mp3("Twi", r"GH_Twi_Lesson[^/]*\.mp3")], country="Ghana"),
    course("temne_sierra_leone_1987", "Temne", "Sierra Leone Temne Language Manual", "1987", "course",
           "Peace Corps Sierra Leone", [eric("ED290325")],
           "About the Temne and their spelling and sounds, notes for the teacher, and twelve lessons of dialogue, "
           "vocabulary, exercises and grammar.", country="Sierra Leone"),
    course("susu_guinea", "Susu", "Xarandi Xa Buki: Susu Trainee Book (Peace Corps Guinea)", "", "course",
           "Peace Corps Guinea", [yj("Susu", r"susu-language-course\.pdf")],
           "Peace Corps Guinea's Susu book for trainees: vocabulary, culture notes, readings, grammar, exercises, "
           "learning tasks and self-evaluation.", country="Guinea"),
    course("crioulo_guinea_bissau_1991", "Crioulo (Kriol)", "Crioulo Grammar Made Simple", "1991", "grammar",
           "Peace Corps Guinea-Bissau", [eric("ED402736")],
           "Guinea-Bissau Crioulo, the Portuguese creole shared by all its peoples: an introduction and its grammar "
           "for volunteers.", country="Guinea-Bissau"),
    course("igbo_nigeria_1964", "Igbo", "Igbo", "1964", "course", "Peace Corps", [eric("ED233567")],
           "Twelve Igbo lessons to study with an Igbo speaker: pronunciation (its tones above all), the main grammar "
           "and some practical conversation.", country="Nigeria"),
    # ------------------------------------------------------------------ Africa: Southern and islands
    course("chichewa_malawi_intro", "Chichewa and Nyanja", "An Introduction to the Chichewa Language (Peace Corps "
           "Malawi)", "", "introduction", "Peace Corps Malawi", [yj("Chichewa", r"MW_Chichewa_Language_Lessons\.pdf")],
           "Peace Corps Malawi's first Chichewa lessons, the script of its recordings and dialogues.",
           audio=[mp3("Chichewa")], country="Malawi"),
    course("chinyanja_health_malawi_1966", "Chichewa and Nyanja", "Health Vocabulary, English-Chinyanja", "1966",
           "dictionary", "Peace Corps Malawi", [eric("ED161241")],
           "An English-Chinyanja word list for health work in Malawi, with verbs and common expressions.",
           ocr="poor", country="Malawi"),
    course("bemba_zambia_1995", "Bemba", "Peace Corps/Zambia PST 1995 Special Lessons: Bemba", "1995", "course",
           "Peace Corps Zambia", [eric("ED402738")],
           "Survival phrases and vocabulary, a noun and affix chart, the national anthem, verb tenses and negation "
           "with grammar notes, questions, and lessons for daily life.", country="Zambia"),
    course("nyanja_zambia_1995", "Chichewa and Nyanja", "Peace Corps/Zambia PST 1995 Special Lessons: Nyanja",
           "1995", "course", "Peace Corps Zambia", [eric("ED402743")],
           "A Nyanja survival kit of phrases and vocabulary, the verb \"to be\", the national anthem, and notes on the "
           "tenses and questions.", country="Zambia"),
    course("sesotho_lesotho_1996", "Sesotho", "Language Manual II: Sesotho", "1996", "course",
           "Peace Corps Lesotho", [eric("ED401739")],
           "Sesotho sounds, tone and length, its noun classes and concords and its sentences, then lessons for "
           "volunteers.", country="Lesotho"),
    course("sesotho_tutorial_lesotho", "Sesotho", "Puo ea Sechaba: A Beginner's Tutorial in Sesotho", "",
           "course", "Peace Corps Lesotho", [yj("Sesotho", r"Peace Corps- A Beginner's Tutorial in Sesotho\.pdf")],
           "A beginner's Sesotho tutorial, a Peace Corps Lesotho publication created by Colin Hoag with its "
           "training staff: chapters on sounds, names, greetings, grammar and daily life.", country="Lesotho"),
    course("setswana_botswana_intro", "Setswana", "An Introduction to the Setswana Language (Peace Corps Botswana)",
           "", "introduction", "Peace Corps Botswana", [yj("Botswana", r"BW_Setswana_Language_Lessons\.pdf")],
           "Peace Corps Botswana's first Setswana lessons for new learners, with recordings.",
           audio=[mp3("Botswana", r"BW_Setswana_Lesson[^/]*\.mp3")], country="Botswana"),
    course("siswati_swaziland_intro", "siSwati", "Pre-Departure siSwati Language Materials (Peace Corps Swaziland)",
           "", "introduction", "Peace Corps Swaziland", [yj("Siswati", r"SZ_siswati_language_Lessons\.pdf")],
           "Nine siSwati lessons with cultural notes, safety tips and etiquette, with recordings.",
           audio=[mp3("Siswati")], country="Swaziland (Eswatini)"),
    course("malagasy_madagascar_1996", "Malagasy", "Peace Corps Madagascar Trainee Book: Official Malagasy", "1996",
           "course", "Peace Corps Madagascar, Antananarivo", [eric("ED454700")],
           "29 topical Malagasy lessons for volunteers in Madagascar, in English and Malagasy with introductions in "
           "French.", country="Madagascar"),
    course("sakalava_madagascar_1996", "Malagasy", "Peace Corps Madagascar Teacher's Book: Sakalava", "1996",
           "teacher's manual", "Peace Corps Madagascar, Antananarivo", [eric("ED461285")],
           "29 topical lessons in Sakalava, a Malagasy dialect, for the teachers of volunteers (in French and "
           "Sakalava).", country="Madagascar"),
    course("malagasy_madagascar_intro", "Malagasy", "An Introduction to the Malagasy Language (Peace Corps "
           "Madagascar)", "", "introduction", "Peace Corps Madagascar",
           [yj("Malagasy-Sakalava/Malagasy-peace-corps", r"MG_Malagasy_Language_Lessons\.pdf")],
           "Peace Corps Madagascar's first Malagasy lessons, with recordings.",
           audio=[mp3("Malagasy-Sakalava/Malagasy-peace-corps")], country="Madagascar"),
    course("kreol_seychelles_1985", "Seychelles Kreol", "Kreol: A Language Training Program for Peace "
           "Corps-Seychelles", "1985", "course", "Peace Corps Seychelles", [eric("ED290348")],
           "36 lessons of Seychelles Kreol with stories, dialogues, expressions, exercises and notes.",
           country="Seychelles"),
    # ------------------------------------------------------------------ Asia and the Pacific
    course("thai_intro", "Thai", "Basic Introduction to Thai Language (Peace Corps Thailand)", "2005",
           "introduction", "Peace Corps Thailand", [yj("Thai", r"TH_Thai_Language_Lessons\.pdf")],
           "Peace Corps Thailand's basic Thai, the script of thirteen recordings, with Thai script and romanised "
           "Thai.", audio=[mp3("Thai")], country="Thailand"),
    course("nepali_1966", "Nepali", "Lessons in Nepali (revised) and Nepali Supplements", "1966", "course",
           "Peace Corps", [eric("ED143237", "Lessons in Nepali"), eric("ED152115", "Nepali supplements")],
           "The Peace Corps's Nepali course in romanised Nepali, with the supplements: songs, dialogues in Devanagari, "
           "Nepali-English and English-Nepali glossaries and a surveyor's glossary.", country="Nepal"),
    course("mongolian_intro", "Mongolian", "Basic Mongolian Expressions (Peace Corps Mongolia)", "2007",
           "introduction", "Peace Corps Mongolia", [yj("Mongolian", r"MN_Mongolian_Language_Lessons\.pdf")],
           "Peace Corps Mongolia's first expressions for trainees: the alphabet, sounds, greetings and politeness, "
           "the script of fifteen recordings.", audio=[mp3("Mongolian")], country="Mongolia"),
    course("mongolian_pst_book", "Mongolian", "Pre-Service Training Mongolian Language Book", "", "course",
           "Peace Corps Mongolia", [yj("Mongolian", r"Peace-Corps-Pre-Service-Training-Book-Mongilian\.pdf")],
           "Peace Corps Mongolia's training course: a primer of the Cyrillic alphabet, reading and pronunciation, "
           "then units of lessons from greetings onwards, with grammar.", country="Mongolia"),
    course("mongolian_phrasebook", "Mongolian", "Phrase Book English-Mongolian (Peace Corps Mongolia)", "",
           "phrasebook", "Peace Corps Mongolia", [yj("Mongolian", r"Phrase book English-Mongolian\.pdf")],
           "Phrases by topic in English and Mongolian: greetings, getting acquainted, thanks, apologies, family, "
           "questions, requests, numbers, time and more.", country="Mongolia"),
    course("mongolian_flashcards", "Mongolian", "Mongolian Flashcards (Peace Corps Mongolia)", "", "workbook",
           "Peace Corps Mongolia", [yj("Mongolian", r"Mongolian Flashcards\.pdf")],
           "Words and sentences to practise, with Mongolian word order and greetings.", country="Mongolia"),
    course("mandarin_china_intro", "Chinese (Mandarin)", "Chinese Basic Lessons for Invitees (Peace Corps China)",
           "2006", "introduction", "Peace Corps China", [yj("Chinese-Mandarin", r"CN_Mandarin_Language_Lessons\.pdf")],
           "Peace Corps China's basic Mandarin for invitees, the script of fifteen recordings.",
           audio=[mp3("Chinese-Mandarin")], country="China"),
    course("bangla_bangladesh_intro", "Bangla (Bengali)", "Introduction to the Bangla Language (Peace Corps "
           "Bangladesh)", "", "introduction", "Peace Corps Bangladesh",
           [yj("Bangladesh", r"BD_Bangla_Language_Lessons\.pdf")],
           "Peace Corps Bangladesh's first Bangla, the script of ten recordings, with romanised Bangla and English.",
           audio=[mp3("Bangladesh")], ocr="font", script="Bangla", country="Bangladesh"),
    course("tagalog_packet_1990", "Tagalog (Filipino)", "Tagalog Language Packet", "1990", "course",
           "Peace Corps Philippines, Manila", [eric("ED402768")],
           "Peace Corps Philippines's Tagalog packet: lessons for daily life and work (the 1994 correspondence "
           "course is lang:fsi:tagalog).", country="Philippines"),
    course("tagalog_humor_1992", "Tagalog (Filipino)", "Ngumiti ka naman! Tagalog with Humor: Language and Culture "
           "through Cartoons", "1992", "workbook", "Peace Corps Philippines, Manila", [eric("ED401738")],
           "Tagalog and Filipino culture learnt through cartoons, with notes on the words and grammar.",
           country="Philippines"),
    course("cebuano_1993", "Cebuano", "Cebuano Language Packet", "1993", "course", "Peace Corps Philippines, Manila",
           [eric("ED401767")], "Peace Corps Philippines's Cebuano lessons for daily life and work.",
           country="Philippines"),
    course("ilokano_1996", "Ilokano", "Ilokano Language Packet", "1996", "course", "Peace Corps Philippines, Manila",
           [eric("ED401763")], "Peace Corps Philippines's Ilokano lessons for daily life and work.",
           country="Philippines"),
    course("ilonggo_1990", "Hiligaynon (Ilonggo)", "Ilonggo Language Packet", "1990", "course",
           "Peace Corps Philippines, Manila", [eric("ED402758")],
           "Peace Corps Philippines's Ilonggo (Hiligaynon) lessons for daily life and work.", country="Philippines"),
    course("bikol", "Bikol", "Bikol: Viracnon Language Packet (1990), Standard Bikol and Bikol Lessons (1967)", "1990",
           "course", "Peace Corps Philippines",
           [eric("ED402759", "Viracnon Language Packet (1990)"), eric("ED018772", "Standard Bikol (1967)"),
            eric("ED018773", "Bikol Lessons (1967)")],
           "Peace Corps Philippines's Viracnon (the Bikol of Catanduanes) packet, and the 1967 Standard Bikol grammar "
           "and Bikol lessons by Jon Epstein for the Peace Corps.", country="Philippines"),
    course("ivatan_1993", "Ivatan", "Ivatan Language Packet", "1993", "course", "Peace Corps Philippines, Manila",
           [eric("ED402781")], "Peace Corps Philippines's Ivatan lessons for the Batanes islands.",
           country="Philippines"),
    course("aklanon_dictionary_1969", "Aklanon", "A Study of the Aklanon Dialect, Volume Two: Dictionary", "1969",
           "dictionary", "Peace Corps Philippines, Kalibo, Aklan", [eric("ED145704")],
           "A dictionary of Aklanon root words and their derivations, made by a Peace Corps project with Aklanon "
           "teachers; its title page says \"Public Domain\". (Volume One, the grammar, asks for the authors' "
           "permission to copy it and is a link only.)", ocr="poor", country="Philippines"),
    course("korean_phrasebook_1973", "Korean", "Korean Phrase Book", "1973", "phrasebook", "Peace Corps Korea",
           [eric("ED131691")],
           "Phrases by topic in English, Korean spelling and a pronunciation guide.", ocr="script", script="Korean",
           country="South Korea"),
    course("korean_culture_1970", "Korean", "Lessons in the Korean Language and Culture for Teachers of English",
           "1970", "course", "Peace Corps Korea", [eric("ED131696")],
           "Korean language and customs for volunteers teaching English in Korea, in romanised Korean.",
           country="South Korea"),
    course("hindi_agriculture_1983", "Hindi", "India 103 Agricultural Extension: Madhya Pradesh Hindi Language",
           "1983", "technical lessons", "Peace Corps India", [eric("ED402756")],
           "Hindi lessons for agricultural extension volunteers in Madhya Pradesh: warm-ups, vocabulary and "
           "dialogues for village and farm work.", ocr="script", script="Devanagari", country="India"),
    course("tamil_1961", "Tamil", "Conversational Tamil", "1961", "course", "Peace Corps", [eric("ED148158")],
           "A conversational Tamil course in romanised Tamil.", country="India"),
    course("dari_intermediate_1966", "Dari and Persian", "Intermediate Dari for Peace Corps Volunteers, Afghanistan",
           "1966", "course", "Peace Corps Afghanistan", [eric("ED131692")],
           "Intermediate Dari conversations and drills for volunteers in Afghanistan.", ocr="poor",
           country="Afghanistan"),
    course("dari_dictionary_1979", "Dari and Persian", "English-Dari Dictionary", "1979", "dictionary",
           "Peace Corps Afghanistan", [eric("ED192577")], "An English-Dari dictionary for volunteers.",
           ocr="script", script="Dari (Arabic)", country="Afghanistan"),
    course("persian_introductory_1966", "Dari and Persian", "Introductory Persian", "1966", "course",
           "Peace Corps Iran", [eric("ED131694")],
           "An introductory Persian course developed for the Peace Corps training for Iran, summer 1966.",
           ocr="poor", country="Iran"),
    course("persian_conversational_1966", "Dari and Persian", "Conversational Persian", "1966", "course",
           "Peace Corps Iran", [eric("ED132838")], "A conversational Persian course for volunteers in Iran.",
           country="Iran"),
    course("sinhala_1995", "Sinhala", "Sinhala Language Trainer's Manual", "1995", "teacher's manual",
           "Peace Corps Sri Lanka, Colombo", [eric("ED402783")],
           "Lesson plans for teaching volunteers Sinhala: warm-ups, presentation and practice.", ocr="script",
           script="Sinhala", country="Sri Lanka"),
    course("fijian_1968", "Fijian", "Lessons in Fijian", "1968", "course", "Peace Corps Fiji", [eric("ED131693")],
           "A Fijian course by Albert J. Schutz and Ratu Rusiate T. Komaitai for Peace Corps volunteers.",
           country="Fiji"),
    course("samoan_1975", "Samoan", "Samoan Language: A Manual for the Study and Teaching of the Samoan Language as "
           "Taught by Peace Corps/W. Samoa", "1975", "course", "Peace Corps Western Samoa", [eric("ED233587")],
           "Peace Corps Western Samoa's full Samoan course: units of lessons on nouns, demonstratives, questions, "
           "verbs and more, with drills.", country="Samoa"),
    course("samoan_1991", "Samoan", "Gagana Samoa mo Pisikoa: Peace Corps Samoan Language Handbook", "1991",
           "course", "Peace Corps Western Samoa", [eric("ED402740")],
           "Peace Corps Western Samoa's later Samoan handbook for volunteers.", country="Samoa"),
    course("pijin_solomons_1978", "Solomon Islands Pijin", "Iumi Lanem Pijin: A Basic Course in Solomon Islands "
           "Pijin", "1978", "course", "Peace Corps Solomon Islands, Honiara", [eric("ED294417")],
           "A basic course in Solomon Islands Pijin for volunteers.", country="Solomon Islands"),
    course("tok_pisin_png_1991", "Tok Pisin", "Tokpisin Grammar Workbook for English Speakers", "1991", "grammar",
           "Peace Corps Papua New Guinea", [eric("ED401761")],
           "A practical approach to the sentence structure of Melanesian Pidgin (Tok Pisin), with exercises.",
           country="Papua New Guinea"),
    course("bislama_vanuatu_2011", "Bislama", "Bislama Handbook (Revision July 2011)", "2011", "course",
           "Peace Corps Vanuatu", [yj("Bislama", r"Bislama Handbook - Revision July 2011\.pdf")],
           "Peace Corps Vanuatu's Bislama workbook, written by its language and cross-cultural trainers: Vanuatu's "
           "history and languages, then lessons for daily life.", country="Vanuatu"),
    course("bislama_vanuatu_intro", "Bislama", "Bislama Introductory Language Lessons (Peace Corps Vanuatu)", "",
           "introduction", "Peace Corps Vanuatu", [yj("Bislama", r"VU_Bislama_Language_Lessons\.pdf")],
           "Peace Corps Vanuatu's first Bislama lessons, with recordings.",
           audio=[mp3("Bislama/Bislama Lessons on MP3")], country="Vanuatu"),
    # ------------------------------------------------------------------ Eastern Europe and Central Asia
    course("albanian_1992", "Albanian", "Albanian Language Competencies for Peace Corps Volunteers in Albania",
           "1992", "course", "Peace Corps", [eric("ED402763")],
           "Albanian by competency for volunteers: topics with dialogues, vocabulary, grammar and culture notes.",
           country="Albania"),
    course("albanian_intro", "Albanian", "The Albanian Language for Invitees (Peace Corps Albania)", "2005",
           "introduction", "Peace Corps Albania",
           [yj("Albanian/Albania Language Files", r"AL_Albanian_Language_Lessons\.pdf")],
           "Peace Corps Albania's first Albanian: the alphabet and sounds, greetings, useful phrases, the restaurant, "
           "directions, drinks, food, fruits and home items, with recordings, and recordings of verb tables and "
           "declensions.", audio=[mp3("Albanian/Albania Language Files"), mp3("Albanian/Albanian-peace-corps")],
           country="Albania"),
    course("macedonia_intro", "Macedonian", "Macedonian (and Albanian) for Invitees (Peace Corps Macedonia)", "2006",
           "introduction", "Peace Corps Macedonia",
           [yj("Macedonian", r"MC_Macedonian_Language_Lessons\.pdf", "Macedonian"),
            yj("Macedonian", r"AL_Albanian_Language_Lessons\.pdf", "Albanian")],
           "Peace Corps Macedonia's first Macedonian (the alphabet, greetings, numbers, days, money, directions, "
           "expressions, problems and introductions) and a short Albanian part, with recordings.",
           audio=[mp3("Macedonian")], country="North Macedonia"),
    course("armenian_1992", "Armenian", "Armenian Language Competencies for Peace Corps Volunteers in Armenia",
           "1992", "course", "Peace Corps", [eric("ED401764")],
           "Armenian by competency for volunteers: topics with dialogues, vocabulary, grammar and culture notes.",
           ocr="script", script="Armenian", country="Armenia"),
    course("armenian_intro", "Armenian", "An Introduction to Armenian (Peace Corps Armenia)", "", "introduction",
           "Peace Corps Armenia", [yj("Armenian/Armenia Language Files", r"AR_Armenian_Language_Lessons\.pdf")],
           "Peace Corps Armenia's first Armenian, the script of fourteen recordings, in Armenian letters with "
           "romanised Armenian.", audio=[mp3("Armenian/Armenia Language Files")], country="Armenia"),
    course("azerbaijani_intro", "Azerbaijani", "Azerbaijan Language Manual (Peace Corps Azerbaijan)", "",
           "introduction", "Peace Corps Azerbaijan", [yj("Azerbaijani", r"AZ_Azerbaijan_Language_Lessons\.pdf")],
           "Peace Corps Azerbaijan's first Azerbaijani, the script of 23 recordings.", audio=[mp3("Azerbaijani")],
           country="Azerbaijan"),
    course("bulgarian_intro", "Bulgarian", "An Introductory Guide to the Bulgarian Language (Peace Corps Bulgaria)",
           "", "introduction", "Peace Corps Bulgaria",
           [yj("Bulgarian/Bulgaria Language Files", r"BG_Bulgarian_Language_Lessons\.pdf")],
           "Peace Corps Bulgaria's introduction to Bulgarian, in Cyrillic letters, with recordings.",
           audio=[mp3("Bulgarian/Bulgaria Language Files")], country="Bulgaria"),
    course("estonian_1992", "Estonian", "Estonian Language Competencies for Peace Corps Volunteers in the Republic of "
           "Estonia", "1992", "course", "Peace Corps", [eric("ED402761")],
           "Estonian by competency for volunteers: topics with dialogues, vocabulary, grammar and culture notes.",
           country="Estonia"),
    course("latvian_1992", "Latvian", "Latvian Language Competencies for Peace Corps Volunteers in the Republic of "
           "Latvia", "1992", "course", "Peace Corps", [eric("ED402764")],
           "Latvian by competency for volunteers: topics with dialogues, vocabulary, grammar and culture notes.",
           country="Latvia"),
    course("georgian_intro", "Georgian", "Georgian Language Beginner Program and Podcast Reference Guide (Peace Corps "
           "Georgia)", "2011", "introduction", "Peace Corps Georgia",
           [yj("Georgian/Georgian Audio Language Files", r"GE_Georgian_Language_Lessons\.pdf", "Beginner program"),
            yj("Georgian/Georgian Video Language Files", r"GE_Georgian_Language_Reference_Guide\.pdf",
               "Podcast reference guide (2011)")],
           "Peace Corps Georgia's beginner Georgian, the script of thirteen recordings, and its 2011 podcast guide "
           "that teaches the Georgian alphabet a few letters a lesson.",
           audio=[mp3("Georgian/Georgian Audio Language Files")], country="Georgia"),
    course("kazakh_1992", "Kazakh", "Kazakh: Language Competencies for Peace Corps Volunteers in Kazakhstan", "1992",
           "course", "Peace Corps", [eric("ED353810")],
           "Kazakh by competency for volunteers, with culture notes.", ocr="script", script="Cyrillic",
           country="Kazakhstan"),
    course("kazakh_1995", "Kazakh", "Kazakh Language Course for Peace Corps Volunteers in Kazakhstan", "1995",
           "course", "Peace Corps Kazakhstan, Almaty", [eric("ED402757")],
           "Peace Corps Kazakhstan's Kazakh course: sounds, dialogues, exercises and culture.", ocr="script",
           script="Cyrillic", country="Kazakhstan"),
    course("russian_kazakhstan_intro", "Russian", "Basic Russian Expressions for Peace Corps Trainees in Kazakhstan",
           "2005", "introduction", "Peace Corps Kazakhstan",
           [yj("Russian-Kazakhstan", r"KZ_Russian_Language_Lessons\.pdf")],
           "Peace Corps Kazakhstan's first Russian: the alphabet, greetings and everyday expressions, the script of "
           "its recordings, in Cyrillic letters.", audio=[mp3("Russian-Kazakhstan")], country="Kazakhstan"),
    course("kyrgyz_1993", "Kyrgyz", "Kirghiz Language Competencies for Peace Corps Volunteers in Kirghizstan",
           "1993", "course", "Peace Corps", [eric("ED358742")], "Kyrgyz by competency for volunteers.",
           ocr="script", script="Cyrillic", country="Kyrgyzstan"),
    course("kyrgyz_1997", "Kyrgyz", "Kyrgyz Language Manual", "1997", "course", "Peace Corps Kyrgyzstan, Bishkek",
           [eric("ED461284")], "Peace Corps Kyrgyzstan's Kyrgyz manual, with grammar explained in English.",
           ocr="script", script="Cyrillic", country="Kyrgyzstan"),
    course("kyrgyz_intro", "Kyrgyz", "Basic Interactive Kyrgyz Language Lessons (Peace Corps Kyrgyz Republic)", "",
           "introduction", "Peace Corps Kyrgyz Republic", [yj("Kyrgyz", r"KY_Kyrgyz_Language_Lessons\.pdf")],
           "Interactive Kyrgyz for greetings, telling about yourself, likes and dislikes, opinions and asking "
           "permission, with recordings.", audio=[mp3("Kyrgyz", r"KY_Kyrgyz_Lesson[^/]*\.mp3")],
           country="Kyrgyzstan"),
    course("russian_kyrgyz_intro", "Russian", "Basic Interactive Russian Language Lessons (Peace Corps Kyrgyz "
           "Republic)", "", "introduction", "Peace Corps Kyrgyz Republic",
           [yj("Kyrgyz", r"KY_Russian_Language_Lessons\.pdf")],
           "Interactive Russian for greetings, telling about yourself, likes and dislikes, opinions and asking "
           "permission, with recordings.", audio=[mp3("Kyrgyz", r"KY_Russian_Lesson[^/]*\.mp3")],
           country="Kyrgyzstan"),
    course("romanian_moldova_1995", "Romanian (and Moldovan)", "Limba Romana: Pre-Service Training Language Manual",
           "1995", "course", "Peace Corps Moldova", [eric("ED401768")],
           "Peace Corps Moldova's Romanian course for training.", country="Moldova"),
    course("romanian_moldova_more", "Romanian (and Moldovan)", "Romanian Workbooks of Peace Corps Moldova "
           "(1996 to 1998)", "1998", "workbook", "Peace Corps Moldova",
           [eric("ED424733", "PC Volunteers' First Steps in Romanian (1998)"),
            eric("ED424731", "Romanian Grammar Workbook (1996)"),
            eric("ED424732", "Practicum for Reading and Writing in Romanian (1997)"),
            eric("ED424734", "Limba noastra-i o comoara: Our Language is a Treasure (1998)")],
           "First steps in Romanian, a grammar workbook, a reading and writing practicum, and a reader of texts about "
           "the Romanian language.", country="Moldova"),
    course("romanian_moldova_intro", "Romanian (and Moldovan)", "An Introductory Guide to the Romanian Language "
           "(Peace Corps Moldova)", "", "introduction", "Peace Corps Moldova",
           [yj("Romanian", r"MD_Romanian_Language_Lessons\.pdf")],
           "Peace Corps Moldova's introduction to Romanian, the script of nineteen recordings.",
           audio=[mp3("Romanian", r"MD_Romanian_Lesson[^/]*\.mp3")], country="Moldova"),
    course("romanian_romania_intro", "Romanian (and Moldovan)", "Survival Romanian (Peace Corps Romania)", "",
           "introduction", "Peace Corps Romania", [yj("Romanian", r"RO_Romanian_Language_Lessons\.pdf")],
           "Peace Corps Romania's survival Romanian: the alphabet, greetings, introducing yourself, days and numbers, "
           "with recordings.", audio=[mp3("Romanian", r"RO_Romanian_Lesson[^/]*\.mp3")], country="Romania"),
    course("russian_1994", "Russian", "Russian Language Course for Peace Corps Trainees in Russia", "1994", "course",
           "Peace Corps Russia, Saratov", [eric("ED402767")],
           "Peace Corps Russia's Russian course: units of dialogues, structures and exercises.", ocr="script",
           script="Cyrillic", country="Russia"),
    course("turkmen_1993", "Turkmen", "Turkmen Language Competencies and Turkmen Language Manual", "1993", "course",
           "Peace Corps", [eric("ED358743", "Turkmen Language Competencies"),
                           eric("ED362052", "Turkmen Language Manual")],
           "Two Turkmen texts written for the first volunteers in Turkmenistan in 1993: competencies with dialogues "
           "and culture notes, and a manual with grammar.", ocr="script", script="Cyrillic",
           country="Turkmenistan"),
    course("turkmen_intro", "Turkmen", "Introduction to the Turkmen Language (Peace Corps Turkmenistan)", "",
           "introduction", "Peace Corps Turkmenistan", [yj("Turkmen", r"TK_Turkmen_Language_Lessons\.pdf")],
           "The alphabet, words, phrases and short dialogues on greetings, colours, numbers, the apartment, family and "
           "the Peace Corps, with recordings.", audio=[mp3("Turkmen")], country="Turkmenistan"),
    course("ukrainian_1992", "Ukrainian", "Ukrainian: Language Competencies for Peace Corps Volunteers in Ukraine",
           "1992", "course", "Peace Corps", [eric("ED353811")],
           "Ukrainian by competency for volunteers, with grammar notes.", ocr="script", script="Cyrillic",
           country="Ukraine"),
    course("ukrainian_intro", "Ukrainian", "Survival Ukrainian (Peace Corps Ukraine)", "", "introduction",
           "Peace Corps Ukraine", [yj("Ukrainian", r"UA_Ukraine_Language_Lessons\.pdf")],
           "Peace Corps Ukraine's survival Ukrainian: the alphabet and pronunciation, greetings and useful phrases, "
           "in Cyrillic letters, with recordings.", audio=[mp3("Ukrainian")], country="Ukraine"),
    course("uzbek_1992", "Uzbek", "Uzbek: Language Competencies for Peace Corps Volunteers in Uzbekistan", "1992",
           "course", "Peace Corps", [eric("ED353829")], "Uzbek by competency for volunteers, with culture notes.",
           ocr="script", script="Cyrillic", country="Uzbekistan"),
    # ------------------------------------------------------------------ Latin America and the Caribbean
    course("spanish_uruguay_1993", "Spanish", "Espanol I: Manual para Peace Corps Volunteers (Uruguay)", "1993",
           "course", "Peace Corps Uruguay, Montevideo", [eric("ED402766")],
           "Peace Corps Uruguay's Spanish course: eleven units of competencies with texts, dialogues, vocabulary, "
           "grammar and pronunciation notes and drills.", country="Uruguay"),
    course("spanish_chile_1995", "Spanish", "Manual de Espanol para Profesores del Cuerpo de Paz (Chile) and Spanish "
           "Language Workbook", "1995", "teacher's manual", "Peace Corps Chile, Santiago",
           [eric("ED402742", "Teacher's manual"), eric("ED402753", "Workbook")],
           "Peace Corps Chile's Spanish: the teacher's manual and the trainees' workbook.", country="Chile"),
    course("spanish_technical_1966", "Spanish", "Spanish for Peace Corps Volunteers in Specialized Technical Jobs",
           "1966", "technical lessons", "Peace Corps", [eric("ED230017")],
           "Spanish for volunteers in agriculture, construction, adult literacy and other technical work in Latin "
           "America.", country="Latin America"),
    course("guarani_1968", "Guarani", "Guarani Basic Course, Parts I and II", "1968", "course", "Peace Corps Paraguay",
           [eric("ED200014", "Part I"), eric("ED200015", "Part II")],
           "The Peace Corps's basic Guarani course for Paraguay in two parts, with Spanish where Paraguayans use it.",
           country="Paraguay"),
    course("guarani_1995", "Guarani", "Guarani I and Work Book (for Peace Corps Volunteers)", "1995", "course",
           "Peace Corps Paraguay", [eric("ED402744")], "Peace Corps Paraguay's Guarani course and workbook.",
           country="Paraguay"),
    course("jamaican_creole_1968", "Jamaican Creole (Patois)", "Jamaican Creole Language Course (for English "
           "Speaking Students)", "1968", "course", "Peace Corps", [eric("ED130535")],
           "A Jamaican Creole course in cycles of dialogues and drills, by Beryl Loftman Bailey for the Peace Corps.",
           country="Jamaica"),
    course("qeqchi_guatemala", "Q'eqchi'", "Survival Q'eqchi' (Peace Corps Guatemala)", "", "introduction",
           "Peace Corps Guatemala", [yj("Q'eqchi'-Kekchi", r"Q'eqchi' Survival Guide\.pdf")],
           "Q'eqchi' pronunciation, courtesy phrases and basic vocabulary from Peace Corps Guatemala's programming and "
           "training department.", country="Guatemala"),
    course("sranan_suriname_intro", "Sranan Tongo", "Sranan Tongo Pre-Departure Language Training (Peace Corps "
           "Suriname)", "", "introduction", "Peace Corps Suriname",
           [yj("Sranan", r"SR_SrananTongo_Language_Lessons\.pdf")],
           "Peace Corps Suriname's Sranan Tongo lessons with songs and dialogues: greetings, goodbyes, family, about "
           "you, numbers, days and months, with 116 recordings.", audio=[mp3("Sranan/Audio Recordings MP3")],
           country="Suriname"),
    # ------------------------------------------------------------------ North Africa and the Middle East
    course("moroccan_arabic_1996", "Moroccan Arabic (Darija)", "Moroccan Arabic: A Competency Based Curriculum, "
           "Beginning and Intermediate", "1996", "course", "Peace Corps Morocco, Rabat", [eric("ED401741")],
           "Peace Corps Morocco's Moroccan Arabic course by competency, for beginning and intermediate students.",
           country="Morocco"),
    course("moroccan_arabic_2011", "Moroccan Arabic (Darija)", "Moroccan Arabic Textbook (2011)", "2011", "course",
           "Peace Corps Morocco", [yj("Arabic-Moroccan", r"Moroccan Arabic textbook 2011\.pdf")],
           "Peace Corps Morocco's 2011 Moroccan Arabic textbook, revised and rewritten from its 1994 book by its "
           "language instructors: lessons with dialogues, vocabulary, grammar and culture, in Arabic letters and a "
           "romanised spelling.", country="Morocco"),
    course("moroccan_arabic_intro", "Moroccan Arabic (Darija)", "Basic Introduction to Arabic (Peace Corps Morocco)",
           "", "introduction", "Peace Corps Morocco", [yj("Arabic-Moroccan", r"MO_Arabic_Language_Lessons\.pdf")],
           "Key beginner parts of the Moroccan Arabic book, read by Peace Corps Morocco's language and culture "
           "facilitators on its recordings.", audio=[mp3("Arabic-Moroccan")], country="Morocco"),
    course("darija_environment_morocco", "Moroccan Arabic (Darija)", "Darija Technical Booklet for Environment "
           "Volunteers", "", "technical lessons", "Peace Corps Morocco",
           [yj("Arabic-Moroccan", r"DarijaENVTechnincalbooklet\.pdf")],
           "Darija for environment volunteers: dialogues on community walks, schools, tree planting and health, with "
           "translations and safety and culture points.", country="Morocco"),
    course("tamazight_morocco_1994", "Tamazight and Tashelhit (Berber)", "Tamazight: A Competency-Based Curriculum, "
           "Beginning and Intermediate", "1994", "course", "Peace Corps Morocco, Rabat", [eric("ED401732")],
           "Peace Corps Morocco's Tamazight (Middle Atlas Berber) course by competency.", country="Morocco"),
    course("tashelhit_morocco_1996", "Tamazight and Tashelhit (Berber)", "Tashelheet: A Competency-Based Curriculum, "
           "Beginning and Intermediate", "1996", "course", "Peace Corps Morocco, Rabat", [eric("ED401731")],
           "Peace Corps Morocco's Tashelhit (southern Berber) course by competency.", country="Morocco"),
    course("tunisian_arabic_1990", "Tunisian Arabic", "A Beginner's Course in Tunisian Arabic", "1990", "course",
           "Peace Corps Tunisia, Tunis", [eric("ED402739")],
           "Peace Corps Tunisia's beginner course: competency lessons with themes, grammar points and the materials "
           "the teacher needs.", ocr="poor", country="Tunisia"),
    course("tunisian_arabic_1979", "Tunisian Arabic", "Peace Corps/Tunisia Course in Tunisian Arabic", "1979",
           "course", "Peace Corps Tunisia", [eric("ED183018")],
           "The Peace Corps's 1979 Tunisian Arabic course, in romanised Arabic.", ocr="poor", country="Tunisia"),
    course("tunisian_arabic_1988", "Tunisian Arabic", "Tunisian Arabic (1988)", "1988", "course",
           "Peace Corps Tunisia", [eric("ED401742")],
           "Tunisian Arabic grammar and lessons in romanised Arabic.", ocr="poor", country="Tunisia"),
    course("tunisian_arabic_dictionary_1977", "Tunisian Arabic", "Peace Corps English-Tunisian Arabic Dictionary",
           "1977", "dictionary", "Peace Corps Tunisia", [eric("ED183017")],
           "English words with their Tunisian Arabic, in romanised and Arabic spelling, with example sentences.",
           ocr="poor", country="Tunisia"),
    course("french_tunisia", "French", "Peace Corps Tunisia French: Situation Course (1987) and Complementary Course "
           "(1996)", "1996", "course", "Peace Corps Tunisia",
           [eric("ED402785", "Cours de situation (1987)"), eric("ED401733", "Cours complementaire (1996)")],
           "French for volunteers in Tunisia: the situation course and the complementary course.", country="Tunisia"),
    course("jordanian_arabic_intro", "Jordanian Arabic", "Pre-Departure Arabic Language Materials (Peace Corps "
           "Jordan)", "", "introduction", "Peace Corps Jordan", [yj("Arabic-Jordanian", r"Arabic-Jordan\.pdf")],
           "Ten lessons of Jordanian Arabic before departure (greetings, how you feel, family, useful expressions, "
           "problems communicating, food, directions, numbers and money, question words and time), with grammar and "
           "culture notes and learning tips, with recordings.", audio=[mp3("Arabic-Jordanian")], country="Jordan"),
    # ------------------------------------------------------------------ every country
    course("where_do_i_go_from_here_1966", "Language learning", "Where Do I Go From Here? A Handbook for Continuing "
           "Language Study in the Field", "1966", "guide", "Peace Corps", [eric("ED012925")],
           "Charles and Marguerite Kraft's handbook for volunteers on going on learning a language at their post, "
           "with a language helper, without a course.", country="every country"),
]
COURSE = {c["key"]: c for c in COURSES}

# The courses that are links only: (language, title, address, why).
LINKS = [
    ("Mandinka", "A Basic Mandinka Course with Cultural Notes, A Basic Olof (Wolof) Course and English-Mandinka "
     "Dictionary (Peace Corps The Gambia, 1965)", f"{IA}/details/ERIC_ED131734",
     "Each says \"The Government of the United States of America is the sole owner of the material published "
     "herein. No part of the book may be reproduced in any form without written permission\" from the Peace Corps "
     "Country Director (ERIC ED131734, ED131733, ED131732)"),
    ("Aklanon", "A Study of the Aklanon Dialect, Volume One: Grammar (1968)", f"{IA}/details/ERIC_ED145705",
     "Its page says no part may be copied without the authors' permission"),
    ("Aymara", "Beginning Aymara: A Course for English Speakers (1967)", f"{IA}/details/ERIC_ED019630",
     "Its page says it may not be reproduced without the editor's permission"),
    ("Yemeni Arabic", "A Field Guide for Continued Study of the Arabic Language in Yemen and Oman (1979)",
     f"{IA}/details/ERIC_ED289374", "Copyright 1979 by David Lawrence Critchfield, with only a licence for the Peace "
     "Corps to copy it"),
    ("Tetun", "Peace Corps Tetun Language Course (Peace Corps East Timor)",
     f"{YOJIK_PC}/Tetun/Peace%20Corps%20Tetun.pdf", "\"Copyright Peace Corps East Timor\", revised by Catharina "
     "Williams-van Klinken and the Dili Institute of Technology, to be copied only unchanged; not a public-domain "
     "work"),
    ("Indonesian", "Indonesian Language Training Books 1 to 3 (Peace Corps Indonesia, 2013)",
     f"{YOJIK_PC}/Indonesian-Bahasa/", "Written by the Wisma Bahasa team (a language school under contract), its "
     "copyright held by Peace Corps Indonesia: not public domain"),
    ("Marshallese", "Marshallese Language Training Manual (1992)",
     f"{YOJIK_PC}/Marshallese/Peace%20Corps%20Marshallese%20Language%20Training%20Manual.pdf",
     "Written by a volunteer, Richard Cook, in his own name; volunteers are not federal employees for copyright"),
    ("Setswana", "There Is No Word for Grammar in Setswana", f"{YOJIK_PC}/Setswana/",
     "Written by a volunteer in his own voice, with no statement that the Peace Corps published it"),
    ("Oshikwanyama and Oshindonga", "Oshikwanyama and Oshindonga: A Beginner's Guide", f"{YOJIK_PC}/Ndonga/",
     "Its own words say it began as a Peace Corps manual but grew into an independent book; its writers are not "
     "named and it quotes a copyrighted proverb book"),
    ("Jordanian Arabic", "Jordanian Arabic Grammar for Beginners", f"{YOJIK_PC}/Arabic-Jordanian/",
     "Its pages do not say who wrote it or that the Peace Corps did"),
    ("Wolof", "Wolof Dictionary and Wolof Grammar (The Gambia)", f"{YOJIK_PC}/Wolof/",
     "The dictionary does not say who made it; the grammar's text is in a broken font that reads as question marks"),
    ("Mandinka", "Mandinka Grammar Manual and Mandinka-English Dictionary (Peace Corps The Gambia)",
     f"{YOJIK_PC}/Mandinka/", "Their text is in a broken font that reads as question marks"),
    ("Kriolu (Cape Verdean Creole)", "English-Kriolu Dictionary and Communications Tools in Kriolu",
     f"{YOJIK_PC}/Kriolu/", "The dictionary does not say who made it; the other is a scan without words"),
    ("Sesotho", "An Introduction to Spoken Sesotho (567 pages)", f"{YOJIK_PC}/Sesotho/",
     "Its pages do not say who wrote it"),
    ("Krio", "Krio Language Manual, Revised Edition (Peace Corps Sierra Leone, 1985), with 44 recordings",
     f"{YOJIK_PC}/Krio/", "The archive's copy is a scan without words and ERIC (ED294418) has no copy; its "
     "recordings are in the folder Krio/audios"),
    ("Mende", "Mende Language Manual, Revised Edition (Peace Corps Sierra Leone, 1987)", f"{YOJIK_PC}/Mende/",
     "A scan without words; ERIC (ED294419) has no copy"),
    ("Susu", "Susu Language Manual: Sierra Leone (1987)", "https://eric.ed.gov/?id=ED294421",
     "ERIC has no copy (Peace Corps Guinea's Susu book is built)"),
    ("Chichewa and Nyanja", "Chichewa Language Manual, Peace Corps Malawi (1985)", "https://eric.ed.gov/?id=ED313893",
     "ERIC has no copy"),
    ("Chichewa and Nyanja", "Learning Chichewa, Books 1 and 2 and Teacher's Manual (1980)",
     f"{IA}/details/ERIC_ED206157", "Peace Corps Language Handbook Series, written under contract by Michigan State "
     "University's African Studies Center: a contractor's work, not a US government work"),
    ("Hausa", "Lecons speciales Hausa (Hausa Special Lessons, Niger, 1987)", "https://eric.ed.gov/?id=ED294415",
     "ERIC has no copy"),
    ("Wolof", "Wolof Teachers Manual, Draft Chapters I to VI (Peace Corps Senegal, 1987)",
     "https://eric.ed.gov/?id=ED294420", "ERIC has no copy"),
    ("Lao", "Lao Language Competencies for Peace Corps Volunteers (1991)", "https://eric.ed.gov/?id=ED347833",
     "ERIC has no copy"),
    ("Tuvaluan", "Tuvaluan Lexicon (1981)", "https://eric.ed.gov/?id=ED294414", "ERIC has no copy"),
    ("Mandinka", "English-French-Mandinka Lexicon (1983)", "https://eric.ed.gov/?id=ED289381", "ERIC has no copy"),
    ("French", "A Vous de Parler: French Trainee Book and Teacher's Manual (Peace Corps Morocco, 1983)",
     "https://eric.ed.gov/?id=ED294422", "ERIC has no copy"),
    ("Spanish", "Aprendemos Espanol (Peace Corps Ecuador, 1986)", "https://eric.ed.gov/?id=ED294429",
     "ERIC has no copy"),
    ("Spanish", "Spanish I and Work Book (1995)", f"{IA}/details/ERIC_ED402784",
     "Written under contract by CHP International: a contractor's work, not a US government work"),
    ("Spanish", "A Microwave Course in Spanish (1968)", f"{IA}/details/ERIC_ED157372",
     "Written by Lingoco Corporation, whose copy says \"All rights reserved\""),
    ("French", "French for West Africa (1966)", f"{IA}/details/ERIC_ED153464",
     "Written under contract by George Washington University: a contractor's work"),
    ("French", "Le Francais essentiel pour l'Afrique francophone (1984)", f"{IA}/details/ERIC_ED290342",
     "Written under contract by the Experiment in International Living: a contractor's work"),
    ("Hassaniya Arabic", "Mauritanian Arabic: Grammar, Communication and Culture, Literacy and Teacher's Handbooks "
     "(1979)", f"{IA}/details/ERIC_ED290326", "Peace Corps Language Handbook Series, written under contract by the "
     "Experiment in International Living: a contractor's work"),
    ("siSwati", "Siswati Special Skills Handbook (1980)", f"{IA}/details/ERIC_ED294413",
     "Peace Corps Language Handbook Series, written under contract by the Experiment in International Living"),
    ("Solomon Islands Pijin", "Solomon Islands Pijin: Grammar, Special Skills, Culture and Communication and "
     "Teacher's Handbooks (1979)", f"{IA}/details/ERIC_ED205040", "Peace Corps Language Handbook Series, written "
     "under contract by the School for International Training"),
    ("Luganda", "Luganda Self-Instructing Learner's Manual (1994)", f"{IA}/details/ERIC_ED402762",
     "Written under contract by CHP International: a contractor's work"),
    ("Kanuri", "Introductory Kanuri (1969)", f"{IA}/details/ERIC_ED051717",
     "Written by the Center for Applied Linguistics: not a US government work (the 1966 and 1993 Peace Corps Kanuri "
     "books are built)"),
    ("Basaa", "Cameroon Basaa (1968)", f"{IA}/details/ERIC_ED048593",
     "Written by the Center for Applied Linguistics: not a US government work"),
    ("Kaqchikel", "Cakchiquel Basic Course (1969)", f"{IA}/details/ERIC_ED028425",
     "Written by Brigham Young University: not a US government work"),
    ("Tunisian Arabic", "Spoken Tunisian Arabic, First Draft (1966)", f"{IA}/details/ERIC_ED294424",
     "Written by Indiana University's Intensive Language Training Center: not a US government work"),
    ("Liberian English", "An Introduction to Liberian English (1981)", f"{IA}/details/ERIC_ED226617",
     "Written with Michigan State University's African Studies Center: a contractor's work"),
    ("Fiji Hindi", "Lessons in Colloquial Hindustani for Fiji (1968)", f"{IA}/details/ERIC_ED144353",
     "Written with the University of Hawaii: a contractor's work"),
    ("Ewe", "Ewe Pronunciation (1966)", f"{IA}/details/ERIC_ED152111",
     "Written with Indiana University's Intensive Language Training Center: a contractor's work"),
    ("Language learning", "Language Learning Strategies for Peace Corps Volunteers (1988)", f"{YOJIK_PC}/Bislama/",
     "Prepared for the Peace Corps by the Center for Applied Linguistics: a contractor's work"),
    ("Twi", "Spoken Twi for Non-Twi Beginners (1974)", f"{IA}/details/ERIC_ED140609",
     "The scan's machine-read text is mostly nonsense; Peace Corps Ghana's Twi introduction is built"),
    ("Telugu", "Conversational Telugu (1962)", f"{IA}/details/ERIC_ED152110",
     "The scan's machine-read text is mostly nonsense"),
    ("Pohnpeian", "Lessons in Ponapean (1962)", f"{IA}/details/ERIC_ED152112",
     "The scan has almost no readable text"),
    ("Madi", "Madi Instructions (ERIC's scan, 1971)", f"{IA}/details/ERIC_ED148161",
     "ERIC's scan reads as nonsense; the archive's better copy is built (pclang:madi_uganda_1971)"),
    ("Thai", "Central-E-Saan, Northern-Central and Central Southern Thai Dictionaries (1986)",
     f"{IA}/details/ERIC_ED401728", "The Thai script was misread by the scanner, so the dictionaries cannot be read"),
    ("Bulgarian", "Bulgarian Language for Peace Corps Volunteers (1997 and 1998)", f"{IA}/details/ERIC_ED424735",
     "Written mostly in Bulgarian, whose Cyrillic letters the scanner misread"),
    ("Russian", "Russian Language Competencies and Workbook (1996), Russian Supplementary Dialogues (1994)",
     f"{IA}/details/ERIC_ED393317", "Mostly Russian, whose Cyrillic letters the scanner misread"),
    ("Mongolian", "Mongol Language Competencies (1993), English-Mongolian Phrase Book (1992), Learner's "
     "Mongol-English Dictionary (1993), Mongolian-English Mini-dictionary", f"{IA}/details/ERIC_ED401762",
     "Their Mongolian Cyrillic was misread by the scanner or typed in a broken font; Peace Corps Mongolia's training "
     "book, phrase book and flashcards with real Cyrillic are built"),
    ("Moroccan Arabic (Darija)", "Moroccan Arabic Technical Lessons for Rehabilitation and Special Education (1984)",
     f"{IA}/details/ERIC_ED289373", "The Arabic of the scan reads as nonsense"),
    ("Language learning", "Peace Corps Volunteer On-Going Language Learning Manual: Beyond Hello (2000)",
     "https://eric.ed.gov/?id=ED463649", "ERIC has no copy"),
]

LIVE_LINGUA = "https://www.livelingua.com/project"


# ====================================================================== reading the courses

def folder_files(page, pattern, cache=None):
    """[(address, size in bytes)] of the files of an archive folder page (an Apache folder list) whose address
    matches pattern; the size is the folder list's rounded size ("2.6M" -> 2600000), 0 when it gives none."""
    import build_textbooks as B
    text = B.fetch(page, cache)
    out = []
    for m in re.finditer(r'<a href="([^"?/][^"]*)">.*?</a>(.*?)</tr>', text, re.S):
        url = urllib.parse.urljoin(page, _html.unescape(m.group(1)))
        if not re.search(pattern, urllib.parse.unquote(url)):
            continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", m.group(2))
        size = 0
        if len(cells) >= 2:
            s = re.match(r"\s*([\d.]+)([KMG]?)", cells[1])
            if s:
                size = int(float(s.group(1)) * {"": 1, "K": 1e3, "M": 1e6, "G": 1e9}[s.group(2)])
        out.append((urllib.parse.quote(urllib.parse.unquote(url), safe=":/?&=#~+'"), size))
    return out


def course_parts(c, cache=None):
    """[(part title, PDF address, page address)] of a course's text PDFs, in the order of its sources."""
    parts = []
    for kind, where, pattern, part in c["text"]:
        if kind == "ia":
            names = L.pick_pdfs(L.ia_files(where, cache), pattern)
            for i, name in enumerate(names, 1):
                title = part or c["title"]
                parts.append((f"{title} ({i})" if len(names) > 1 else title,
                              f"{IA}/download/{where}/{urllib.parse.quote(name)}", f"{IA}/details/{where}"))
        else:
            found = folder_files(where, pattern, cache)
            for i, (url, _size) in enumerate(found, 1):
                title = part or c["title"]
                parts.append((f"{title} ({i})" if len(found) > 1 else title, url, where))
    return parts


def course_audio(c, cache=None):
    """[{url, kind, size}] of a course's recordings (originals, never downloaded here), from the archive's folder
    lists."""
    out = []
    for _kind, where, pattern in c["audio"]:
        out += [{"url": url, "kind": "mp3", "size": size} for url, size in folder_files(where, pattern, cache)]
    return out


def course_notice(c):
    """A course's notice: who made it, where it was read, the scan notes and the audio line."""
    first = c["text"][0]
    source = (FROM_ERIC.format(number=first[1].replace("ERIC_", "")) if first[0] == "ia" else FROM_YOJIK)
    if len({t[0] for t in c["text"]}) > 1:
        source = "Read from the Internet Archive's ERIC copies and the Peace Corps language archive."
    notice = NOTICE.format(office=c["office"], source=source)
    if c["ocr"] == "poor":
        notice += POOR_OCR
    elif c["ocr"] == "script":
        notice += SCRIPT_OCR.format(script=c["script"])
    elif c["ocr"] == "font":
        notice += FONT_NOTE.format(script=c["script"])
    return notice + (AUDIO_LISTED if c["audio"] else NO_AUDIO)


def course_entry(c):
    """The PDF_DOCS-like entry of a course (refs_kit.us_pdf), for pdf_set.pdf_set_book."""
    first = c["text"][0]
    source = f"{IA}/details/{first[1]}" if first[0] == "ia" else first[1]
    return K.us_pdf(GROUP, name=f"pclang_{c['key']}", title=f"{c['title']} ({c['language']}, Peace Corps)",
                    subject=f"Language learning: {c['language']}", publisher=f"{PUBLISHER} ({c['office']})",
                    source=source, description=c["description"], notice=course_notice(c), published=c["year"],
                    level="course")


def course_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one course (its key's name): every text PDF read with pdf_set.pdf_set_book, its recordings
    added to its originals."""
    import pdf_set
    left_out = left_out if left_out is not None else []
    c = COURSE.get(name)
    if c is None:
        left_out.append({"title": name, "reason": "Unknown course."})
        return None
    parts = course_parts(c, cache)
    if not parts:
        left_out.append({"title": c["title"], "reason": "No text PDF of the course was found."})
        return None
    book = pdf_set.pdf_set_book(course_entry(c), parts, work, cache, left_out, limit)
    if book is None:
        return None
    book.originals += course_audio(c, cache)
    book.version = f"read from {', '.join(sorted({p[2] for p in parts}))} on {datetime.date.today().isoformat()}"
    return book


def course_sign(name):
    """A course's sign of change: the names and checksums of its Internet Archive files, or its folders' file
    addresses and sizes."""
    c = COURSE[name]
    signs = []
    for kind, where, pattern, _part in c["text"]:
        if kind == "ia":
            signs += sorted((f.get("name"), f.get("md5")) for f in L.ia_files(where) if re.search(pattern, f["name"]))
        else:
            signs += folder_files(where, pattern)
    return K.sha(signs)


# ====================================================================== the index

def region_of(c):
    """The region of a course (from its language)."""
    return LANGS[c["language"]][0]


def keys_of(region):
    """The keys of a region's courses, in the module's order."""
    return [f"pclang:{c['key']}" for c in COURSES if region_of(c) == region]


def index_pages():
    """[(path, title, body HTML)] of the index: a first page (how to use these books), then one page per region,
    each language with where it is spoken, its courses (key, year, level, recordings) and its links only."""
    import build_textbooks as B
    by_lang = {}
    for c in COURSES:
        by_lang.setdefault(c["language"], []).append(c)
    links = {}
    for lang, title, url, why in LINKS:
        links.setdefault(lang, []).append((title, url, why))
    words = ", ".join(f"{REGIONS[r][0]} ({REGIONS[r][1]})" for r in REGIONS if REGIONS[r][0])
    first = (f"<p>The Peace Corps's language courses in the library: {len(COURSES)} books for "
             f"{len(by_lang)} languages, written by the Peace Corps for training its volunteers. Each page is one "
             "part of the world; each language says where it is spoken, which books the library has (with each "
             "book's key, year and level), whether the Peace Corps's recordings are listed with the book, and the "
             "courses that are links only, with the reason.</p>"
             f"<p>Request words: peace-corps-languages (every book), {B.esc(words)}.</p>"
             "<p>About the recordings: they are never inside a book. A book with recordings lists each MP3 file's "
             "address and size in its originals, for you to download with Program Downloader. Most recordings go "
             "with the short \"introduction\" lessons the Peace Corps gave its invitees before departure.</p>"
             "<p>About old scans: many courses are typewritten scans from the 1960s to the 1990s. Their notice says "
             "when the machine-read text has many mistakes, or when a foreign script (Cyrillic, Armenian, Arabic, "
             "Korean, Devanagari, Sinhala) was misread: then the English explanations read well but the foreign "
             "words do not, and a newer course with real script or recordings is the better start.</p>"
             "<p>Also in the library: the Peace Corps's Tagalog correspondence course (key lang:fsi:tagalog) and "
             "the Foreign Service Institute's courses (request word languages). More Peace Corps courses, with "
             "recordings, are listed by Live Lingua's Peace Corps archive: "
             f'<a href="{LIVE_LINGUA}">{LIVE_LINGUA}</a> (open it in a browser) and its copy on '
             f'<a href="{YOJIK_PC}/">{YOJIK_PC}/</a>.</p>')
    pages = [("how-to-use", "How to use the Peace Corps language courses", first)]
    for number, (region, (word, title, covers)) in enumerate(REGIONS.items(), 1):
        body = f"<p>{B.esc(title)}: {B.esc(covers)}." + (f" Request word: {B.esc(word)}." if word else "") + "</p>"
        for lang in sorted(lng for lng, (rg, _w) in LANGS.items() if rg == region):
            have, only = by_lang.get(lang, []), links.get(lang, [])
            if lang == "Tagalog (Filipino)":
                have = have + [dict(key=None, title="Language Correspondence Course: Tagalog, Modules 1 to 21",
                                    year="1994", level="course", audio=[], country="Philippines")]
            if not have and not only:
                continue
            body += f"<h2>{B.esc(lang)}</h2><p>Where it is spoken: {B.esc(LANGS[lang][1])}.</p>"
            if have:
                items = []
                for c in have:
                    key = f"pclang:{c['key']}" if c["key"] else "lang:fsi:tagalog"
                    sound = "recordings listed" if c["audio"] else "no recordings"
                    when = f", {c['year']}" if c["year"] else ""
                    items.append(f"<li>{B.esc(c['title'])} ({B.esc(c['country'])}{B.esc(when)}; {B.esc(c['level'])}; "
                                 f"{sound}): key {B.esc(key)}</li>")
                body += f"<h3>Books in the library</h3><ul>{''.join(items)}</ul>"
            if only:
                items = [f'<li>{B.esc(t)}: <a href="{B.esc(u)}">{B.esc(u)}</a>. {B.esc(w)}.</li>' for t, u, w in only]
                body += f"<h3>Links only</h3><ul>{''.join(items)}</ul>"
        pages.append((f"region-{number}-{B.slug(title, 40)}", title, body))
    return pages


def index_book(name, work, cache=None, left_out=None, limit=None):
    """The index book (pclang:index): the toolkit's own facts and links (CC0), made offline from this module's
    lists."""
    import build_textbooks as B
    book = K.new_book("pclang_index", "Peace Corps language courses: a guide to every language",
                      "Language learning: Peace Corps courses", GROUP,
                      "Digital Accessibility Toolkit (an index of the library)", K.CC0, K.CC0_URL,
                      "https://github.com/mark-getbraille/toolkit-models",
                      "Every language of the Peace Corps courses in the library, in plain words: where it is spoken, "
                      "which course or courses, their level and year, whether recordings are listed, and the "
                      "courses that are links only, with the reason.",
                      "Facts and links only (CC0). Each course has its own licence, shown in that book; each "
                      "link-only source belongs to its publisher.", level="reference",
                      changes="an index written for the toolkit")
    for number, (path, title, body) in enumerate(index_pages(), 1):
        if limit and len(book.pages) >= limit:
            break
        book.pages.append(B.Page(path, title, body, number, ""))
    return book


def index_sign(name):
    """The weekly sign of the index: a fingerprint of the module's lists."""
    return K.sha([[c["key"], c["title"], c["year"], bool(c["audio"])] for c in COURSES], LINKS, LANGS)


# ====================================================================== the collection

MAKERS = {"index": (index_book, index_sign)}
MAKERS.update({c["key"]: (course_book, course_sign) for c in COURSES})

WORDS = {"peace-corps-languages": lambda: ["pclang:index"] + [f"pclang:{c['key']}" for c in COURSES]}
WORDS.update({word: (lambda r=region: ["pclang:index"] + keys_of(r))
              for region, (word, _t, _c) in REGIONS.items() if word})

COLLECTION = K.Collection("pclang", GROUP, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "pclang": "Peace Corps language courses: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
              "policies page at every build); each ERIC document's record names a Peace Corps office as its author "
              "(ERIC's records, checked 2026-11-23); read from the Internet Archive (robots.txt allows programs) and "
              "from fsi-languages.yojik.eu (robots.txt: \"Allow crawling of all content\", checked 2026-11-23). The "
              "audio is listed, never downloaded by the builder.",
    "pclang_index": "The index (pclang:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [(f"{title} ({lang}, Peace Corps)", f"{why}. Index: {url}") for lang, title, url, why in LINKS] + [
    ("Live Lingua's Peace Corps language archive (livelingua.com/project)", "Its course pages are built by scripts "
     "from a private service, its terms say nothing allowing programs, and its site is \"Copyright Live Lingua\"; the "
     "same Peace Corps works are read from ERIC's copies on the Internet Archive and the archive's copy on "
     "fsi-languages.yojik.eu. Index: https://www.livelingua.com/project"),
    ("Peace Corps language-training guides for trainers (Language Coordinators Resource Kit, Language Training "
     "Reference Manual, classroom testing handbooks, competency curriculum guides)", "Guides for running language "
     "programmes, not courses for learners; left to the Peace Corps manuals collection. Index: "
     "https://eric.ed.gov/?q=%22Peace+Corps%22+language+training"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
