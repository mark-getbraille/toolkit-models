"""Peace Corps manuals and guides for the reference library, in their own group "Reference, Peace Corps manuals and
guides" (the owner's request of 2026-11-23: every Peace Corps manual and guide). Keys: pc:<name> (one manual each),
pc:index (the guide to every Peace Corps book in the library), and the request words below.

What this module builds, in plain words: the Peace Corps' own manuals, handbooks, idea books and training guides,
each read WHOLE from the Internet Archive's copy of the ERIC scan (the US Department of Education's ERIC library kept
most Peace Corps "Information Collection and Exchange" (ICE) publications; the Internet Archive holds ERIC's PDFs as
"ERIC_ED..." items and its microfiche scans as "micro_IA..." items). By theme, with its request word:
  - pc-teaching: teaching English (TEFL, ESP, community content-based instruction), classroom management, teacher
    training, maths and science teaching, primary arts and crafts, literacy and nonformal education, libraries, and
    the World Wise Schools guides for classrooms;
  - pc-health: personal and community health, oral rehydration, childbirth, child health, nutrition, HIV/AIDS
    teaching, health visual aids, water, sanitation and hygiene in schools (every one marked: follow current medical
    guidance, for old health advice goes out of date);
  - pc-youth: working with young people, life skills, Camp GLOW and girls' empowerment;
  - pc-business: small enterprise, bookkeeping for microbusinesses, management consulting, crafts and agricultural
    marketing, women's enterprise;
  - pc-agriculture: agricultural extension, field crops, crop production, soils and fertilizer, rice, orchards,
    farm maths, grazing land, fisheries planning, and the Spanish and French editions of the field manuals;
  - pc-environment: conservation and environmental education;
  - pc-community: participatory analysis for community action (PACA), project design and management, gender and
    development, programming and training, NGOs, disasters, urban development, resource centres;
  - pc-volunteer: volunteer handbooks, personal safety, motorcycle safety, cross-cultural training, homestays, working
    with counterparts, in-service and close-of-service workshops, training of trainers;
  - peace-corps: all of them and the index.
Languages: most books are in English; the Spanish and French editions say so in their titles (language "spa" or
"fra").

Already in the library and not repeated (pc:index links them): "Culture Matters: The Peace Corps Cross-Cultural
Workbook" (relate:peace_corps_culture_matters); the Peace Corps Tagalog course and the other language courses (the
language collection and the Peace Corps language helper's books); the Peace Corps appropriate-technology manuals on
water, wells, sanitation, irrigation, soil conservation, fish ponds, beekeeping, poultry and small animals, forestry,
building, tools, energy and food preserving (the approtech collection, apt:). pc:index finds those books in the code
at build time (every book whose publisher or title names the Peace Corps), so books added later are listed too.

Licences, checked on each copy's own front pages (2026-11-23), in the same way as the approtech helper's Peace Corps
books (/home/user/notes/approtech-peace-corps-ids.txt):
  - a manual produced by a Peace Corps office or country office ("This publication was produced by the Peace Corps
    Center for Field Assistance and Applied Research", "Peace Corps/Thailand"): a work of the US government
    (17 U.S.C. 105), public domain; the line checked on govinfo.gov's policies page at every build;
  - a manual the Peace Corps published before March 1989 with no copyright notice: public domain in the US (a US
    government publication, and a work published in the US without a notice before 1 March 1989; 17 U.S.C. 405);
  - a manual prepared for the Peace Corps under contract in 1989 or later that prints the Peace Corps' words "This
    manual may be reproduced and/or translated in part or in full without payment or royalty. Please give standard
    acknowledgment": free to copy and translate with credit (PC_PERMISSION, "open"); the credit is in the notice.
  Link-only (NOT_INCLUDED, with the reason): copies that print another owner's copyright (APHA, UNICEF, Boston
  University, VSO and Heinemann, UNESCO, a photographer, a private author); ICE "reprints" of other organisations'
  works (Hesperian, Indiana University, CEDPA, YMCA, the Environmental Health Project, Catholic Relief Services'
  evaluation manual, a UNDP/UNESCO project, St Lucia School for the Deaf); manuals from 1989 or later written by a
  contractor, a volunteer or an outside teacher without the reproduction notice; and items whose ERIC record has no
  full text and no scan. Passages that a Peace Corps manual reprinted with permission are named in that book's notice
  (they stay their owners' copyright and are kept only as part of the whole manual).

Nothing here is read from peacecorps.gov (a Cloudflare bot check, no CAPTCHAs are solved) or files.peacecorps.gov
(robots.txt shuts out its /manuals/ folder); archive.org's robots.txt allows the files and it has no AI rules
(checked 2026-11-23). Pictures are not included; the text is the scanner's machine reading, with its mistakes.

Run from the repository's folder:
  python3 textbooks/peace_corps.py pc:classroom_management_idea_book_2008 --out build/textbooks --limit 5
  python3 textbooks/peace_corps.py --list pc-health
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402

PREFIX = "pc"
GROUP = "peace_corps"
GROUPS = {GROUP: "Reference, Peace Corps manuals and guides"}

# The two licences this module adds (sources.ALLOWED through more_refs.allowed()).
PC_NO_NOTICE = "Public domain (US government publication without copyright notice)"
PC_NO_NOTICE_URL = "https://www.copyright.gov/circs/circ03.pdf"
PC_PERMISSION = "Free to copy and translate with credit (Peace Corps permission)"
PC_PERMISSION_URL = "https://archive.org/details/ERIC_ED330773"
ALLOWED = {PC_NO_NOTICE: "open", PC_PERMISSION: "open"}

REPRODUCE = ("This manual may be reproduced and/or translated in part or in full without payment or royalty. Please "
             "give standard acknowledgment.")
CREDIT = "Source: the Peace Corps of the United States, Information Collection and Exchange."
SCAN = ("Read from the Internet Archive's copy of the ERIC scan: the machine-read text has the scanner's mistakes, and "
        "its pictures are left out (their captions are kept where the scanner read them).")
MICRO = ("Read from the Internet Archive's scan of ERIC's microfiche: the machine-read text has the scanner's "
         "mistakes, and its pictures are left out.")
HEALTH = ("Health advice changes: this manual is from {year}, so some of its facts, medicines and treatments may be "
          "out of date. Follow current medical guidance from a doctor, nurse or health worker, your national health "
          "service or the World Health Organization; in an emergency call your local emergency number.")
HIV = (" HIV testing, treatment and prevention have changed a great deal since then (today's HIV medicines let people "
       "with HIV live long lives); the library's current HIV books are in the sexual health collection (sexhealth:).")
REPRINTED = ("Some passages in this manual were reprinted by the Peace Corps with permission from other publishers "
             "({who}); those passages remain their owners' copyright and are kept only as part of the whole manual.")

THEMES = {
    "teaching": ("pc-teaching", "Teaching: English, classrooms, teacher training, maths and science, literacy and "
                 "libraries"),
    "health": ("pc-health", "Health: community health, mothers and children, nutrition, HIV/AIDS teaching and hygiene"),
    "youth": ("pc-youth", "Youth: working with young people, life skills and girls' leadership"),
    "business": ("pc-business", "Business: small enterprise, bookkeeping, marketing and women's enterprise"),
    "agriculture": ("pc-agriculture", "Agriculture: extension, crops, soils, orchards, grazing and fisheries"),
    "environment": ("pc-environment", "Environment: conservation and environmental education"),
    "community": ("pc-community", "Community development: participatory analysis, project design, gender and "
                  "programming"),
    "volunteer": ("pc-volunteer", "Volunteers: handbooks, safety, cross-cultural training and training of trainers"),
}

# Who reprinted passages with permission, for the "r" books (named on the copies' own pages).
REPRINTS = {
    "ccbi_manual_2004": "PARADE Magazine and Rosemary Zibart, 2002",
    "ccbi_volunteer_workbook_2004": "PARADE Magazine and Rosemary Zibart, 2002",
    "nonformal_education_manual_1989": "other organisations that waived copyright restrictions for non-profit use",
    "nonformal_education_manual_2004": "the writers and publishers thanked in its acknowledgments",
    "womens_enterprise_1986": "Westview Press, from Women in Third World Development, 1984",
    "environmental_education_schools_1993": "the sources named beside the activities in its chapter 7",
    "environmental_education_community_2005": "the writers and publishers thanked in its acknowledgments",
    "ngo_training_guide_2003": "Robert Boostrom, Developing Creative and Critical Thinking, and others named in it",
    "supervisors_counterparts_2002": "Lawrence Salmen, Listen to the People, and others named in it",
    "youth_english_practice_activities_2015": "the Search Institute's 40 Developmental Assets for Adolescents",
    "building_blocks_of_literacy_2015": "USAID's Tanzania early grade reading assessment form",
}

# The books: (theme, name, Internet Archive item, year, title, ICE number, language, kind, description).
# kind letters: o = produced by a Peace Corps office, p = by a Peace Corps country office (post), g = by another US
# agency, c = prepared under contract and printing the reproduction notice (REPRODUCE), "" = published by the Peace
# Corps before March 1989 with no copyright notice; h = health (the HEALTH note), v = HIV (the HIV note too),
# r = has reprinted passages (REPRINTS).
BOOKS = [
    # ------------------------------------------------------------------ teaching
    ("teaching", "tefl_tesl_manual_1989", "micro_IA41155140_0049", "1989", "TEFL/TESL: Teaching English as a "
     "Foreign or Second Language", "M041", "eng", "c",
     "The Peace Corps' main manual for volunteers who teach English, prepared by the Center for Applied Linguistics: "
     "how people learn a language, planning lessons, teaching listening, speaking, reading, writing, grammar and "
     "vocabulary, classroom management, testing, and making teaching materials with few resources."),
    ("teaching", "esp_english_specific_purposes_1986", "ERIC_ED274218", "1986", "ESP: Teaching English for Specific "
     "Purposes", "", "eng", "c",
     "A guide to building an English for Specific Purposes course (English for work or study): finding out what the "
     "learners need, setting goals they can reach, designing the course, and choosing materials and classroom "
     "activities."),
    ("teaching", "linguistics_tefl_teacher_1970", "ERIC_ED043027", "1970", "Linguistics and the TEFL Teacher", "",
     "eng", "",
     "A short paper for teachers of English as a foreign language on how the study of language (sounds, grammar and "
     "meaning) helps in planning and teaching lessons."),
    ("teaching", "english_for_teachers_korea_1974", "ERIC_ED289352", "1974", "English for Teachers (Peace Corps "
     "Korea)", "", "eng", "",
     "A course book used in the Peace Corps' workshops for Korean teachers of English: a review of basic English for "
     "classroom talk, with dialogues and readings on daily life, careers, health and getting along with people, and "
     "notes on grammar."),
    ("teaching", "tefl_crossover_agriculture_trainer_1985", "ERIC_ED288053", "1985", "In-Country TEFL/Crossover "
     "Tropical Agriculture Training Manual: Trainer's Edition (Thailand)", "T-37", "eng", "",
     "The trainers' record of Peace Corps Thailand's 1984 training, in Thailand, of English teachers who would also "
     "work in farming: the schedule, the farming sessions (vegetables, soils, livestock and more), language and "
     "cross-cultural sessions, and the homestay."),
    ("teaching", "tefl_crossover_agriculture_trainee_1985", "ERIC_ED288054", "1985", "In-Country TEFL/Crossover "
     "Tropical Agriculture Training Manual: Trainee Edition (Thailand)", "T-37A", "eng", "",
     "The trainees' book that goes with the trainer's edition: the farming lessons and handouts for English teachers "
     "learning basic tropical agriculture in Thailand."),
    ("teaching", "youth_english_practice_activities_2015", "ERIC_ED591325", "2015", "Youth Development through "
     "English Practice Activities", "M0109", "eng", "or",
     "Activities for volunteers who are asked to teach English to young people: English clubs, camps and lessons that "
     "also build young people's skills, confidence and leadership, with planning tips and many ready activities."),
    ("teaching", "ccbi_manual_2004", "ERIC_ED521840", "2004", "Community Content-Based Instruction Manual", "T0112",
     "eng", "or",
     "How to teach any subject (English, science, health) through topics that matter to the local community, such as "
     "health, the environment or gender: planning lessons and units, activities, and working with counterparts. It "
     "grew out of teacher workshops in Eritrea."),
    ("teaching", "ccbi_volunteer_workbook_2004", "ERIC_ED521839", "2004", "Working with CCBI: Volunteer Workbook",
     "M0073", "eng", "or",
     "The volunteers' workbook for community content-based instruction: exercises and worksheets for planning lessons "
     "around community topics."),
    ("teaching", "classroom_management_idea_book_2008", "ERIC_ED507898", "2008", "Classroom Management Idea Book",
     "M0088", "eng", "o",
     "Practical ideas from volunteer teachers and staff for running a classroom: setting rules and routines, large "
     "classes, motivating students, discipline without beating, cheating, and getting along with the school."),
    ("teaching", "teacher_training_reference_manual_1986", "ERIC_ED288838", "1986", "Teacher Training: A Reference "
     "Manual", "", "eng", "",
     "A reference for volunteers who train teachers: differences between school systems, how adults learn, observing "
     "and giving feedback to teachers, running workshops, and teaching methods. It goes with the training guide."),
    ("teaching", "teacher_training_guide_1986", "ERIC_ED288839", "1986", "Teacher Training: A Training Guide", "",
     "eng", "",
     "The session plans for training volunteers as teacher trainers, each tied to a chapter of the reference manual."),
    ("teaching", "liberia_teacher_training_vol2_1982", "micro_IA41153421_0973", "1982", "Peace Corps Stateside Teacher "
     "Training for Volunteers in Liberia, Volume II: Teacher Trainers and University Educators", "", "eng", "",
     "The training programme (prepared for the Peace Corps by PSI Associates) for volunteers going to Liberia to train "
     "teachers or teach at university: Liberia's education system, teacher training methods, supervising teachers, "
     "and the session plans."),
    ("teaching", "liberia_vocational_teacher_training_vol3_1982", "micro_IA41153421_0974", "1982", "Peace Corps "
     "Stateside Teacher Training for Volunteers in Liberia, Volume III: Vocational Education Teachers", "", "eng", "",
     "The training programme for volunteers going to Liberia to teach vocational subjects, agriculture and home "
     "economics: curriculum, lesson planning and the session plans."),
    ("teaching", "liberia_secondary_teacher_training_vol4_1982", "micro_IA41153421_0975", "1982", "Peace Corps "
     "Stateside Teacher Training for Volunteers in Liberia, Volume IV: Secondary School Teachers", "", "eng", "",
     "The training programme for volunteers going to teach English, maths, science and health in Liberian secondary "
     "schools: teaching methods for each subject, practice teaching and the session plans."),
    ("teaching", "liberia_cross_cultural_support_vol5_1982", "micro_IA41153421_0976", "1982", "Peace Corps Stateside "
     "Teacher Training for Volunteers in Liberia, Volume V: Cross-Cultural Training and Support Services", "", "eng",
     "",
     "The cross-cultural part of the Liberia training: coping with another culture, stereotypes and prejudice, "
     "personal values and expectations, with Liberians and former volunteers as resource people."),
    ("teaching", "preparation_for_teaching_1985", "ERIC_ED288836", "1985", "Preparation for Teaching: A Manual with "
     "Exercises in Curriculum Development", "", "eng", "",
     "Written by a volunteer for trainee teachers of industrial (technical) subjects at St Vincent Teachers' College: "
     "how to plan a course, write objectives, analyse tasks and prepare lessons, with exercises."),
    ("teaching", "role_in_education_sector_study_1984", "ERIC_ED289013", "1984", "The Role of the Peace Corps in "
     "Education in Developing Countries: A Sector Study", "R-49", "eng", "",
     "A study of twenty years of Peace Corps work in education: what volunteers taught and where, a case study of "
     "Sierra Leone, and lessons for planning education projects."),
    ("teaching", "community_data_decisions_education_2014", "ERIC_ED591326", "2014", "Community Data-Driven Decision "
     "Making in Education: A Facilitator's Manual", "M0108", "eng", "o",
     "Workshop sessions that help parents, teachers and community members gather simple facts about their school "
     "(attendance, reading, resources) and use them to choose and plan improvements."),
    ("teaching", "science_teachers_handbook_1968", "ERIC_ED308075", "1985", "Science Teachers' Handbook (Peace Corps "
     "India)", "R-50", "eng", "",
     "Made by Peace Corps volunteers and Indian science teachers in Andhra Pradesh (first printed 1968): how to teach "
     "science actively, with investigations, demonstrations and science apparatus made from local, low-cost "
     "materials."),
    ("teaching", "science_teachers_handbook_spanish", "ERIC_ED308076", "1987", "Manual para los Profesores de Ciencias "
     "(Science Teachers' Handbook, in Spanish)", "R-66", "spa", "",
     "The Spanish edition of the Science Teachers' Handbook: active science teaching with demonstrations and "
     "home-made apparatus."),
    ("teaching", "science_teachers_handbook_french", "ERIC_ED308077", "1987", "Manuel du Professeur de Science "
     "(Science Teachers' Handbook, in French)", "R-64", "fra", "",
     "The French edition of the Science Teachers' Handbook: active science teaching with demonstrations and home-made "
     "apparatus."),
    ("teaching", "nepal_math_science_trainers_1988", "micro_IA41153441_0705", "1988", "Peace Corps Nepal 1988 "
     "Preservice Technical Training Manual for Math and Science Teacher Trainers", "", "eng", "",
     "The technical training sessions and readings for volunteers who trained maths and science teachers in Nepal, "
     "built from a study of the trainer's job."),
    ("teaching", "primary_arts_crafts_1969", "ERIC_ED312174", "1989", "Primary School Arts and Crafts: Developing "
     "Manual Skills, Lesson Plans for Classes I to VI", "R037", "eng", "o",
     "Lesson plans for primary teachers with little arts training, tested in Nigeria and Jamaica (compiled 1969): "
     "paper tearing, folding and cutting, weaving, mosaics, painting and drawing, rubbings, simple book-making and "
     "more, all with cheap local materials."),
    ("teaching", "mali_ruralisation_french_1990", "ERIC_ED401740", "1990", "La Ruralisation de l'enseignement "
     "fondamental au Mali (in French)", "", "fra", "p",
     "A French guide from the Peace Corps in Mali for teaching practical skills on school grounds: nutrition, the "
     "school garden, tree nurseries and other activities linking school to rural life."),
    ("teaching", "vocational_education_tunisia_1982", "ERIC_ED241784", "1982", "Vocational Education Manual (Peace "
     "Corps Tunisia)", "R-46", "eng", "",
     "Training for volunteers who teach vocational subjects in Tunisia: background on the country's schools, human "
     "relations, teaching methods (such as the demonstration), lesson planning and workshop safety."),
    ("teaching", "special_education_rehabilitation_1981", "ERIC_ED214340", "1981", "Peace Corps in Special Education "
     "and Rehabilitation", "CS-2", "eng", "",
     "A study, prepared for the Peace Corps by Partners of the Americas, of volunteers' work with disabled people: "
     "special education, occupational, physical and speech therapy, and vocational rehabilitation, with case studies "
     "and lessons learned."),
    ("teaching", "literacy_handbook_1984", "ERIC_ED251696", "1984", "Peace Corps Literacy Handbook", "M-21", "eng",
     "",
     "An introduction to literacy work for volunteers: the value and levels of literacy, planning a programme, "
     "teaching reading and writing to adults, making materials, and evaluating the work."),
    ("teaching", "literacy_handbook_spanish", "ERIC_ED307471", "1986", "Manual de Alfabetizacion del Cuerpo de Paz "
     "(Peace Corps Literacy Handbook, in Spanish)", "M-28", "spa", "",
     "The Spanish edition of the Peace Corps Literacy Handbook."),
    ("teaching", "literacy_handbook_french", "ERIC_ED307474", "1986", "Manuel d'Alphabetisation du Peace Corps (Peace "
     "Corps Literacy Handbook, in French)", "M-32", "fra", "",
     "The French edition of the Peace Corps Literacy Handbook."),
    ("teaching", "literacy_adult_learning_guide_1979", "ERIC_ED317800", "1979", "A Peace Corps Guide to Literacy, "
     "Adult Learning, and Nonformal Education", "", "eng", "",
     "Written by a volunteer who worked in Nepal: what nonformal education is, how adults learn, ways of teaching "
     "literacy to adults, and examples from the field."),
    ("teaching", "litpak_guide_1986", "micro_IA41155118_0093", "1986", "Guide to the Peace Corps Literacy Packet "
     "(Litpak)", "", "eng", "",
     "A guide to the Peace Corps' literacy packet for volunteers: how to use it, when literacy helps, literacy where "
     "many languages are spoken, and choosing a teaching method."),
    ("teaching", "building_blocks_of_literacy_2015", "ERIC_ED591328", "2015", "The Building Blocks of Literacy: A "
     "Literacy Resource Manual for Peace Corps Volunteers", "M0107", "eng", "or",
     "Early grade reading for volunteers who coach, co-teach or teach reading: the skills of reading (sounds, letters, "
     "fluency, vocabulary, understanding), activities for each, reading assessment and reading clubs."),
    ("teaching", "nonformal_education_manual_1989", "ERIC_ED317722", "1989", "Nonformal Education Manual", "M0042",
     "eng", "cr",
     "Practical skills and theory of nonformal education (learning outside school) for volunteers: an example from "
     "Togo, how adults learn, finding out what people need, planning and running sessions, materials and "
     "evaluation."),
    ("teaching", "nonformal_education_manual_2004", "ERIC_ED521841", "2004", "Nonformal Education Manual (2004 "
     "edition)", "M0042", "eng", "or",
     "The newer edition, joining the earlier Nonformal Education Manual and training module: participatory learning, "
     "facilitation skills, planning and running sessions, and evaluation."),
    ("teaching", "library_development_training_2012", "ERIC_ED536918", "2012", "Sustainable Library Development "
     "Training Package", "", "eng", "o",
     "Training sessions for volunteers who help start or improve school and community libraries: organising books, "
     "running a library, reading promotion and finding resources."),
    ("teaching", "donated_books_sources_2014", "ERIC_ED559644", "2014", "Sources of Donated Books for Schools and "
     "Libraries (2014)", "RE003", "eng", "o",
     "A list of organisations that give books and educational materials to schools and libraries, with how to ask for "
     "them."),
    ("teaching", "building_bridges_2010", "ERIC_ED513112", "2010", "Building Bridges: A Peace Corps Classroom Guide to "
     "Cross-Cultural Understanding", "", "eng", "o",
     "Lessons for school classes, from the Peace Corps' World Wise Schools, on understanding one's own culture and "
     "other people's, respecting differences, and handling cross-cultural misunderstandings, using volunteers' "
     "stories."),
    ("teaching", "looking_at_ourselves_and_others_1998", "ERIC_ED419771", "1998", "Looking at Ourselves and Others",
     "", "eng", "o",
     "A World Wise Schools classroom guide on what culture is, seeing the world from other points of view, and "
     "questioning assumptions, with volunteers' experiences and activities for different grades."),
    ("teaching", "destination_senegal_1991", "ERIC_ED354197", "1991", "Destination: Senegal (World Wise Schools video "
     "guide)", "", "eng", "o",
     "A classroom unit on the geography and culture of Senegal, for grades 3 to 12, written to go with the Peace "
     "Corps video (the video is not included)."),
    ("teaching", "destination_marshall_islands_1992", "ERIC_ED354198", "1992", "Destination: Marshall Islands (World "
     "Wise Schools video guide)", "", "eng", "o",
     "A classroom unit on the Republic of the Marshall Islands, for grades 3 to 12, written to go with the Peace "
     "Corps video."),
    ("teaching", "destination_nepal_1992", "ERIC_ED354199", "1992", "Destination: Nepal (World Wise Schools video "
     "guide)", "", "eng", "o",
     "A classroom unit on Nepal, for grades 3 to 12, written to go with the Peace Corps video."),
    ("teaching", "destination_sri_lanka_1992", "micro_IA41153543_0039", "1992", "Destination: Sri Lanka (World Wise "
     "Schools video guide)", "", "eng", "o",
     "A classroom unit on Sri Lanka and South Asia, written to go with the Peace Corps video and with pupils' letters "
     "to a volunteer."),
    ("teaching", "destination_honduras_1992", "micro_IA41153543_0040", "1992", "Destination: Honduras (World Wise "
     "Schools study guide)", "", "eng", "o",
     "A classroom unit on the geography, environment and culture of Honduras, for grades 3 to 12."),
    # ------------------------------------------------------------------ health
    ("health", "personal_health_training_1982", "ERIC_ED243821", "1982", "Personal Health Training Manual", "TR-21",
     "eng", "h",
     "Training sessions for all volunteers on keeping healthy overseas: food and water safety, common illnesses, "
     "malaria, stress, alcohol, sexual health and using the Peace Corps medical kit."),
    ("health", "technical_health_training_vol1_1985", "ERIC_ED307487", "1985", "Technical Health Training Manual, "
     "Volume 1", "T-35a", "eng", "hc",
     "Preservice training for volunteers in health projects (prepared by CHP International): community health, "
     "finding out a community's health needs, health education, nutrition and child growth, and immunisation."),
    ("health", "technical_health_training_vol2_1985", "ERIC_ED307488", "1985", "Technical Health Training Manual, "
     "Volume 2", "T-35a", "eng", "hc",
     "The second volume of the technical health training sessions: diarrhoea and oral rehydration, maternal and child "
     "health, water and sanitation, and planning health projects."),
    ("health", "oral_rehydration_diarrhoea_1985", "ERIC_ED289005", "1985", "Oral Rehydration Therapy and the Control "
     "of Diarrheal Diseases", "T-34", "eng", "hc",
     "Training for volunteers and community health workers on oral rehydration therapy and preventing diarrhoea: "
     "dehydration, mixing and giving oral rehydration solution, feeding during illness, hygiene and teaching mothers."),
    ("health", "oral_rehydration_diarrhoea_spanish", "ERIC_ED307490", "1985", "Manual de Adiestramiento sobre Terapia "
     "de Rehidratacion Oral (Oral Rehydration Therapy training, in Spanish)", "T-53", "spa", "hc",
     "The Spanish training manual on oral rehydration therapy and the control of diarrhoeal diseases."),
    ("health", "preparation_for_childbirth_1985", "ERIC_ED289004", "1985", "Preparation for Childbirth: A Health "
     "Workers Manual", "R-55", "eng", "h",
     "Four prenatal classes for health workers to teach expectant mothers: the body, pregnancy, comfort and nutrition, "
     "labour and breathing, breastfeeding, danger signs and the newborn."),
    ("health", "child_health_manual_1999", "ERIC_ED438407", "1999", "A New Beginning: The Child Health Manual",
     "", "eng", "ho",
     "Preservice training for volunteers in health projects on children's health: growth and nutrition, "
     "breastfeeding, immunisation, diarrhoea, respiratory infections, malaria and working with mothers."),
    ("health", "homemaking_handbook_usda", "ERIC_ED307465", "1981", "Homemaking Handbook for Village Workers in Many "
     "Countries", "R-39", "eng", "gh",
     "A guide for village workers from the US Department of Agriculture's Extension Service and USAID (reprinted by "
     "the Peace Corps): food and nutrition, child care, keeping the home clean and healthy, sewing and household "
     "management."),
    ("health", "nutrition_mixed_gardening_1984", "ERIC_ED288051", "1984", "Nutrition Improvement through Mixed "
     "Gardening in the Humid Tropics: A Trainer's Manual", "T-19", "eng", "h",
     "Training for community field workers (USAID and the Peace Corps) on growing a mixed home garden for better "
     "family nutrition: local foods, simple low-cost gardening and nutrition teaching."),
    ("health", "promoting_powerful_people_2000", "micro_IA41153662_0517", "2000", "Promoting Powerful People: A Process "
     "for Change", "", "eng", "ho",
     "A guide for trainers in nutrition (prepared by the Peace Corps with USAID): helping people change health "
     "behaviour, such as eating foods rich in vitamin A, through community discussion and participation."),
    ("health", "aids_resource_manual_thailand_1993", "ERIC_ED366556", "1993", "AIDS Resource Manual: A Guide for "
     "Teaching about AIDS in Thailand", "R0082", "eng", "hvp",
     "From Peace Corps Thailand: basic facts about HIV and AIDS as known in 1993, and activities and games for "
     "teaching about them."),
    ("health", "teaching_about_hiv_aids_thailand_1994", "ERIC_ED378146", "1994", "Alternative Techniques for Teaching "
     "about HIV/AIDS in the Classroom", "R0086", "eng", "hvp",
     "From Peace Corps Thailand: interactive games and activities to teach school pupils about HIV and AIDS and to "
     "take the fear out of AIDS education."),
    ("health", "tools_for_teaching_health_1987", "ERIC_ED310083", "1987", "Tools for Teaching: A Visual Aids Workshop "
     "and Instruction Manual for Health Educators", "", "eng", "h",
     "A workshop for health educators on making and using cheap teaching aids: flip charts, flannel boards, puppets, "
     "posters, models and games."),
    ("health", "wash_in_schools_toolkit_2017", "ERIC_ED591324", "2017", "Water, Sanitation, and Hygiene in Schools "
     "Toolkit (Let Girls Learn)", "M0124", "eng", "ho",
     "For volunteers working with schools on water, sanitation and hygiene: handwashing, toilets, safe water, "
     "menstrual hygiene for girls, and changing habits, with activities and planning tools."),
    # ------------------------------------------------------------------ youth
    ("youth", "working_with_youth_2002", "micro_IA41153661_0787", "2002", "Working with Youth: Approaches for "
     "Volunteers", "", "eng", "o",
     "How volunteers can work with young people: positive youth development, building trust, activities, clubs, "
     "preparing young people for work, and working with youth agencies."),
    ("youth", "life_skills_manual_2001", "micro_IA41153755_1061", "2001", "Life Skills Manual (English, French and "
     "Swahili)", "M0063", "eng", "ho",
     "Interactive lessons in skills for life: communication, decision-making, managing emotions, assertiveness, "
     "self-esteem, resisting peer pressure, relationships, and facts about HIV/AIDS and sexually transmitted "
     "diseases. The book holds the English, French and Swahili editions."),
    ("youth", "camp_glow_handbook_2001", "micro_IA41153654_0774", "2001", "Camp GLOW (Girls Leading Our World): "
     "Handbook for Volunteers", "", "eng", "o",
     "How to plan and run a leadership camp for girls, begun in Romania in 1995: planning, money, staff, activities "
     "for self-esteem, goal setting and career planning, and follow-up."),
    ("youth", "empowering_girls_classroom_2002", "ERIC_ED465676", "2002", "In the Classroom: Empowering Girls (Idea "
     "Book)", "", "eng", "o",
     "Ideas for teachers to help girls succeed in class: fair attention, girl-friendly lessons, role models, and "
     "classroom projects."),
    ("youth", "empowering_girls_beyond_classroom_2000", "ERIC_ED464878", "2000", "Beyond the Classroom: Empowering "
     "Girls (Idea Book)", "", "eng", "o",
     "Ideas for workshops, camps, clubs and events that build girls' confidence and skills outside school."),
    ("youth", "youth_development_environment_1998", "ERIC_ED432464", "1998", "Youth Development and the Environment",
     "", "eng", "o",
     "Ideas that join youth development with environmental projects, so young people build leadership while caring "
     "for their environment (ecology camps, clubs and projects)."),
    ("youth", "youth_development_honduras_1989", "ERIC_ED330773", "1989", "Youth Development: A Case Study from "
     "Honduras", "", "eng", "c",
     "The story of a volunteer's work with young people in institutions in Honduras: vocational training, "
     "recreation, informal education and counselling, and what others can learn from it."),
    ("youth", "rededication_to_youth_1992", "ERIC_ED359305", "1992", "Peace Corps' Rededication to Youth: Addressing "
     "the Needs of Youth-at-Risk", "", "eng", "o",
     "Ideas for Peace Corps staff and volunteers on helping young people at risk (street children, school leavers) "
     "through government and private agencies."),
    ("youth", "programming_youth_projects_1994", "ERIC_ED418301", "1994", "Programming and Training for Peace Corps "
     "Youth Development Projects", "T0085", "eng", "o",
     "A supplement to the Programming and Training System manual on planning youth development projects and training "
     "volunteers for them."),
    # ------------------------------------------------------------------ business
    ("business", "accounting_microbusiness_1982", "ERIC_ED241779", "1982", "Accounting for the Microbusiness: A "
     "Teaching Manual", "R-23B", "eng", "",
     "How to teach the MICRON bookkeeping system, a simple accounting system made by a volunteer in Colombia for very "
     "small businesses: cash records, sales, costs and profit."),
    ("business", "accounting_microbusiness_spanish", "ERIC_ED241780", "1981", "Contabilidad para la Micro Empresa "
     "(Accounting for the Microbusiness, in Spanish)", "R-23", "spa", "",
     "The Spanish edition of the MICRON accounting teaching manual."),
    ("business", "management_consulting_small_enterprise_1981", "ERIC_ED241774", "1981", "Guidelines for Management "
     "Consulting Programs for Small-Scale Enterprise", "M-14", "eng", "",
     "For volunteers who advise small businesses: the problems small firms face, choosing businesses to help, "
     "diagnosing a business, and advice on bookkeeping, marketing and management."),
    ("business", "management_consulting_spanish", "ERIC_ED307470", "1986", "Pautas para Programas de Asesoramiento "
     "Gestional para Microempresas (in Spanish)", "", "spa", "",
     "The Spanish edition of the guidelines for management consulting for small businesses."),
    ("business", "management_consulting_french", "ERIC_ED307472", "1986", "Directives Relatives a l'Elaboration de "
     "Programmes de Conseil en Gestion pour Petites Entreprises (in French)", "", "fra", "",
     "The French edition of the guidelines for management consulting for small businesses."),
    ("business", "small_enterprise_preservice_1986", "ERIC_ED288055", "1986", "Small Enterprise Development "
     "Pre-Service Training Manual", "T-42", "eng", "",
     "Forty training sessions in ten modules for volunteers going into small business work: business basics, "
     "bookkeeping, marketing, credit, feasibility and advising entrepreneurs."),
    ("business", "small_enterprise_inservice_1986", "ERIC_ED288056", "1986", "Small Enterprise Development In-Service "
     "Training Manual", "T-43", "eng", "",
     "Training sessions for serving volunteers in small enterprise work, building on the preservice manual."),
    ("business", "small_enterprise_case_studies_1985", "ERIC_ED288041", "1985", "Peace Corps Programming in Small "
     "Enterprise Development: Three Case Studies and Analysis", "", "eng", "",
     "Three case studies of Peace Corps small business projects and what made them succeed or fail."),
    ("business", "womens_enterprise_1986", "ERIC_ED288042", "1986", "Supporting Women's Enterprise Development",
     "M-19", "eng", "cr",
     "For development workers helping women start and run businesses: women's economic situation, choosing a "
     "business, credit, training and working with women's groups."),
    ("business", "crafts_development_marketing_1986", "ERIC_ED289003", "1986", "Crafts Development and Marketing "
     "Manual", "M-24", "eng", "c",
     "How to help local craftspeople start and run small craft businesses: product design, costing and pricing, "
     "quality, and selling locally and abroad."),
    ("business", "agricultural_marketing_1984", "ERIC_ED251698", "1984", "Agricultural Marketing Principles: A "
     "Training Manual", "T-31", "eng", "",
     "A two-week workshop to teach volunteers how farm produce is marketed: prices, costs, storage, transport, "
     "cooperatives and helping farmers sell."),
    ("business", "agribusiness_assessment_1983", "ERIC_ED307463", "1983", "Small and Medium Scale Agribusiness "
     "Assessment", "TR43", "eng", "",
     "A checklist for volunteers helping farmers judge whether a farm business idea will work and write a simple "
     "business plan."),
    # ------------------------------------------------------------------ agriculture
    ("agriculture", "agricultural_extension_1983", "ERIC_ED241776", "1983", "Agricultural Extension", "M-18", "eng",
     "",
     "What agricultural extension is and how to do it: learning about farmers and their needs, planning, record "
     "keeping, demonstrations, farmer groups and working with the extension service."),
    ("agriculture", "agricultural_extension_spanish", "ERIC_ED307477", "1987", "Extension Agricola (Agricultural "
     "Extension, in Spanish)", "M-39", "spa", "",
     "The Spanish edition of the Agricultural Extension manual."),
    ("agriculture", "adw_orientation_vol1_1982", "ERIC_ED242883", "1982", "Agricultural Development Workers Training "
     "Manual, Volume I: Orientation for Trainers", "", "eng", "",
     "The trainers' guide to the agricultural development workers training series: its approach, preparing the "
     "training, the training site and the schedule."),
    ("agriculture", "adw_extension_skills_vol2_1982", "ERIC_ED242884", "1982", "Agricultural Development Workers "
     "Training Manual, Volume II: Extension Skills", "", "eng", "",
     "Training sessions on extension skills: communication, working with farmers, demonstrations and community "
     "entry."),
    ("agriculture", "adw_crops_vol3_1982", "ERIC_ED242885", "1982", "Agricultural Development Workers Training Manual, "
     "Volume III: Crops", "", "eng", "",
     "Training sessions on growing crops: soils, land preparation, seeds and planting, fertilizer, pests, diseases, "
     "weeds and harvest."),
    ("agriculture", "crops_technical_guidelines_1985", "ERIC_ED314592", "1985", "Technical Guidelines and References: "
     "Crops Training Component", "", "eng", "",
     "The crops reference that goes with the training manual: units and conversions, weather, soils, crop "
     "management, pests and the agricultural field worker's job."),
    ("agriculture", "traditional_field_crops_1981", "ERIC_ED241773", "1981", "Traditional Field Crops", "",
     "eng", "",
     "How small farmers grow the main field crops (maize, sorghum, millet, rice, beans and other legumes, peanuts): "
     "planting, fertilizer, pests, diseases, harvest and storage."),
    ("agriculture", "traditional_field_crops_spanish", "ERIC_ED307476", "1981", "Cultivos Tradicionales (Traditional "
     "Field Crops, in Spanish)", "M-35", "spa", "",
     "The Spanish edition of Traditional Field Crops."),
    ("agriculture", "traditional_field_crops_french", "ERIC_ED307466", "1987", "Cultures Traditionnelles de Plein "
     "Champ (Traditional Field Crops, in French)", "R-65", "fra", "",
     "The French edition of Traditional Field Crops."),
    ("agriculture", "crop_production_handbook_1982", "ERIC_ED241777", "1982", "Crop Production Handbook for Peace "
     "Corps Volunteers", "R-6", "eng", "",
     "The basics of growing crops: plants and how they grow, soils, water, fertilizer, pests, weeds and crop "
     "management, with a glossary."),
    ("agriculture", "soils_crops_fertilizer_1980", "ERIC_ED241778", "1980", "Soils, Crops and Fertilizer Use: A What, "
     "How and Why Guide", "R-8", "eng", "",
     "An on-the-job reference for small-farm soil management: soil basics, organic matter and compost, chemical "
     "fertilizers and how much to use, liming, and safe use of farm chemicals."),
    ("agriculture", "rice_production_1982", "ERIC_ED241782", "1982", "Rice Production: A Training Manual and Field "
     "Guide to Small-Farm Irrigated Rice Production", "R-40", "eng", "",
     "A step-by-step guide to growing irrigated rice in Sierra Leone, for volunteers working as extension agents: the "
     "rice plant, nurseries, transplanting, water, fertilizer, weeds, pests and harvest."),
    ("agriculture", "orchard_management_1982", "ERIC_ED242882", "1982", "Orchard Management: Horticultural Practices "
     "for Peace Corps Volunteers", "R-31", "eng", "",
     "Growing fruit trees: orchard soils, plant botany, propagation and grafting, pruning, pests and diseases."),
    ("agriculture", "agricultural_mathematics_1981", "ERIC_ED242551", "1981", "Agricultural Mathematics for Peace "
     "Corps Volunteers", "R-4", "eng", "",
     "Worked examples of the maths volunteers need in the field: measuring land, seed and fertilizer amounts, "
     "mixtures, water, livestock feed and unit conversions."),
    ("agriculture", "grazing_rangeland_1982", "ERIC_ED241785", "1982", "Grazing and Rangeland Development for "
     "Livestock Production", "R-47", "eng", "",
     "Sound management of grazing land in the tropics (written for USAID by Howard Sprague): grasses and legumes, "
     "stocking, rotation, and improving pastures for livestock."),
    ("agriculture", "freshwater_fisheries_planning_1976", "ERIC_ED243648", "1982", "Freshwater Fisheries: Program "
     "Planning", "M-1A", "eng", "",
     "For planners and trainers considering freshwater fish farming projects (by Steven Gregory, 1976): feasibility, "
     "a survey from Zaire, jobs and training of fisheries workers, and support."),
    ("agriculture", "marine_fisheries_extension_1983", "ERIC_ED243658", "1983", "Small Scale Marine Fisheries: An "
     "Extension Training Manual", "TR-30", "eng", "",
     "Eight weeks of preservice training for volunteers working with small fishing communities on the coast: boats "
     "and gear, fish handling and marketing, cooperatives and fisheries extension."),
    ("agriculture", "poultry_raising_french", "ERIC_ED307473", "1986", "Elevage Pratique de la Volaille (Practical "
     "Poultry Raising, in French)", "M-30", "fra", "",
     "The French edition of Practical Poultry Raising (the English edition is in the appropriate technology "
     "collection)."),
    ("agriculture", "poultry_raising_spanish", "ERIC_ED307475", "1987", "Crianza Practica de Aves (Practical Poultry "
     "Raising, in Spanish)", "M-34", "spa", "",
     "The Spanish edition of Practical Poultry Raising."),
    ("agriculture", "beekeeping_spanish", "ERIC_ED307468", "1984", "La Apicultura de Pequena Escala (Small Scale "
     "Beekeeping, in Spanish)", "M-25", "spa", "",
     "The Spanish edition of Small Scale Beekeeping (the English edition is in the appropriate technology "
     "collection)."),
    ("agriculture", "beekeeping_french", "ERIC_ED307469", "1984", "Apiculture de Petite Echelle (Small Scale "
     "Beekeeping, in French)", "M-26", "fra", "",
     "The French edition of Small Scale Beekeeping."),
    ("agriculture", "programming_agriculture_projects_1994", "ERIC_ED418299", "1994", "Programming and Training for "
     "Peace Corps Agricultural Projects", "T0078", "eng", "o",
     "A supplement to the Programming and Training System manual on planning agriculture projects and training "
     "volunteers for them."),
    # ------------------------------------------------------------------ environment
    ("environment", "teaching_conservation_1977", "micro_IA41153502_0721", "1977", "Teaching Conservation in "
     "Developing Nations", "M0007", "eng", "",
     "Ideas, activities and resources for bringing conservation education into everyday community work: a "
     "conservation centre, schools, health and farm centres, nature trails, exhibits and endangered species."),
    ("environment", "conservation_education_planning_1985", "ERIC_ED287739", "1985", "Conservation Education: A "
     "Planning Guide", "M-23", "eng", "c",
     "How to design and run a conservation education programme that changes how people manage their environment: "
     "finding the problem, the audience, the message, methods and evaluation."),
    ("environment", "environmental_education_schools_1993", "ERIC_ED363520", "1993", "Environmental Education in the "
     "Schools: Creating a Program that Works!", "M0044", "eng", "cr",
     "A manual for teachers on building an environmental education programme across grades and cultures: planning, "
     "teaching methods, activities, working with the community, evaluation, and success stories."),
    ("environment", "environmental_education_community_2005", "ERIC_ED496726", "2005", "Environmental Education in the "
     "Community", "M0075", "eng", "or",
     "An update of the older conservation education manuals: environmental education outside school, with community "
     "groups, campaigns, nature centres and clubs, using current research and volunteers' experience."),
    ("environment", "adapting_environmental_materials_1999", "ERIC_ED432466", "1999", "Adapting Environmental Education "
     "Materials", "", "eng", "o",
     "How to adapt existing environmental education materials to local issues, cultures and audiences: finding and "
     "choosing materials, copyright, adapting, testing and evaluating them."),
    ("environment", "local_environmental_knowledge_2002", "micro_IA41153661_0783", "2002", "Learning Local "
     "Environmental Knowledge: A Volunteer's Guide to Community Entry", "M0071", "eng", "o",
     "How volunteers can learn what local people know about their land, plants, animals and seasons when entering a "
     "community, with a trainer's guide."),
    # ------------------------------------------------------------------ community
    ("community", "paca_idea_book_2010", "ERIC_ED536919", "2010", "Using Participatory Analysis for Community Action "
     "(PACA): Idea Book", "M0086", "eng", "o",
     "The PACA tools for working with a community: community mapping, daily activity schedules, seasonal calendars "
     "and needs ranking, looking at the different roles of women and men, and turning the results into action."),
    ("community", "project_design_management_2000", "micro_IA41153662_0516", "2000", "The New Project Design and "
     "Management Workshop Training Manual", "", "eng", "o",
     "Sessions for a workshop where volunteers and community partners learn to design and manage projects together: "
     "participatory analysis, goals and objectives, action plans, budgets, monitoring and evaluation."),
    ("community", "project_design_management_french_2003", "micro_IA41153661_0916", "2003", "Le Nouveau Manuel de "
     "Formation sur l'Elaboration et la Gestion des Projets (Project Design and Management, in French)", "", "fra",
     "o",
     "The French edition of the Project Design and Management workshop training manual."),
    ("community", "small_projects_design_1987", "ERIC_ED289006", "1987", "Small Projects Design and Management: "
     "Training Manual for Volunteers and Counterparts", "T-50", "eng", "c",
     "A two-and-a-half-day workshop that helps volunteers and their counterparts make small projects truly the "
     "community's own: planning, budgets, carrying out and evaluating."),
    ("community", "third_world_women_1981", "ERIC_ED241787", "1981", "Third World Women: Understanding Their Role in "
     "Development, A Training Resource Manual", "", "eng", "",
     "Training sessions for new volunteers on the roles women play in development and how projects can include and "
     "help women."),
    ("community", "programming_women_in_development_1994", "ERIC_ED418302", "1994", "Programming and Training for "
     "Peace Corps Women in Development Projects", "T0084", "eng", "o",
     "A supplement to the Programming and Training System manual on planning women in development projects and "
     "training volunteers for them."),
    ("community", "disasters_and_development_1984", "ERIC_ED288050", "1984", "Disasters and Development: A Peace Corps "
     "Pre-Service Training Module", "T-18", "eng", "",
     "Two training sessions (developed by INTERTECT) on natural disasters, their effects on development, and how "
     "volunteers can help communities prepare and reduce harm."),
    ("community", "urban_development_programming_1991", "ERIC_ED349362", "1991", "Peace Corps: Urban Development "
     "Programming Guidelines", "", "eng", "o",
     "Guidance for Peace Corps staff on finding and planning projects in towns and cities: housing, urban services, "
     "small business and youth."),
    ("community", "ngo_training_guide_2003", "micro_IA41153661_0784", "2003", "An NGO Training Guide for Peace Corps "
     "Volunteers", "", "eng", "or",
     "Training for volunteers who work with non-governmental organisations: how NGOs work, strategic planning, boards, "
     "fundraising, managing volunteers and building the organisation's strength."),
    ("community", "programming_training_system_1989", "ERIC_ED318881", "1989", "Peace Corps Programming and Training "
     "System Manual", "T0054", "eng", "o",
     "The Peace Corps' manual for its staff on planning projects and training volunteers: the six steps of "
     "programming, training design, monitoring and evaluation."),
    ("community", "programming_training_system_spanish_1989", "ERIC_ED338812", "1989", "Cuerpo de Paz Manual de "
     "Sistema de Programacion y Capacitacion (in Spanish)", "", "spa", "o",
     "The Spanish edition of the Programming and Training System manual."),
    ("community", "integrated_programming_system_1986", "ERIC_ED288040", "1986", "Integrated Programming System",
     "PR-002", "eng", "",
     "A handbook for Peace Corps staff on planning, developing, carrying out and evaluating projects."),
    ("community", "programming_education_projects_1994", "ERIC_ED418300", "1994", "Programming and Training for Peace "
     "Corps Education Projects", "T0080", "eng", "o",
     "A supplement to the Programming and Training System manual on planning education projects and training "
     "volunteers for them."),
    ("community", "peace_corps_training_supplement_1994", "ERIC_ED418298", "1994", "Peace Corps Training: Supplement "
     "to the Programming and Training System Manual", "T0083", "eng", "o",
     "A resource for planning training events and preparing training materials: needs, design, staff and "
     "evaluation."),
    ("community", "pt_booklet2_design_project_2001", "ERIC_ED470773", "2001", "Programming and Training Booklet 2: How "
     "to Design or Revise a Project", "", "eng", "o",
     "Step-by-step guidance for Peace Corps staff and partners on designing or revising a project."),
    ("community", "pt_booklet3_second_third_goals_2001", "ERIC_ED470774", "2001", "Programming and Training Booklet 3: "
     "How to Integrate Second and Third Goals into Programming and Training", "", "eng", "o",
     "How projects and training can serve the Peace Corps' cross-cultural goals: helping people understand Americans, "
     "and Americans understand other peoples."),
    ("community", "pt_booklet4_assess_project_2001", "ERIC_ED470775", "2001", "Programming and Training Booklet 4: How "
     "to Assess a Project", "", "eng", "o",
     "How to design and carry out a monitoring and evaluation plan for a project."),
    ("community", "pt_booklet5_implement_project_2001", "ERIC_ED470776", "2001", "Programming and Training Booklet 5: "
     "How to Implement a Project", "", "eng", "o",
     "Carrying out a project: partners, volunteer sites and assignments, support and supervision."),
    ("community", "pt_booklet6_integrate_2003", "micro_IA41153661_0785", "2003", "Programming and Training Booklet 6: "
     "How to Integrate Programming and Training", "", "eng", "o",
     "How project planning and volunteer training fit together."),
    ("community", "programming_training_evaluation_2015", "ERIC_ED591327", "2015", "Programming, Training, and "
     "Evaluation Guidance", "T0140", "eng", "o",
     "The Peace Corps' 2015 guidance for field staff on project planning, training and evaluation."),
    ("community", "resources_for_development_1981", "ERIC_ED241768", "1981", "Resources for Development", "M-3A",
     "eng", "",
     "A 1981 directory of organisations that provided help, materials and information for rural development work "
     "(many addresses are out of date)."),
    ("community", "resource_center_workshop_1986", "ERIC_ED291384", "1986", "In-Country Resource Center Workshop: A "
     "Training Manual", "T-48", "eng", "",
     "A workshop to help Peace Corps staff and volunteers set up or improve a resource centre (a small library of "
     "technical information) in their country."),
    # ------------------------------------------------------------------ volunteer
    ("volunteer", "peace_corps_handbook_1977", "ERIC_ED161707", "1977", "Peace Corps Handbook (Spring 1977)", "",
     "eng", "",
     "The handbook given to new volunteers in 1977: medical, personal and money matters before leaving, training, "
     "volunteer life and work, and living in a developing country (its rules and benefits are long out of date)."),
    ("volunteer", "personal_safety_cross_cultural_1985", "ERIC_ED289014", "1985", "Personal Safety in Cross-Cultural "
     "Transition", "T-3", "eng", "",
     "Training sessions for volunteers before leaving and in the country on personal safety, handling unwanted "
     "attention and harassment, and supporting each other after difficult experiences."),
    ("volunteer", "pc_rider_motorcycle_1975", "ERIC_ED307489", "1975", "PC Rider: A Training Manual (motorcycle "
     "safety)", "T-36", "eng", "",
     "Safe motorcycle riding for volunteers in West Africa: why motorcycles are hard to see, protective gear, riding "
     "skills, road hazards and maintenance (always follow today's helmet and road laws)."),
    ("volunteer", "cross_cultural_training_1981", "ERIC_ED241786", "1981", "Cross-Cultural Training for Peace Corps "
     "Volunteers", "TR-07", "eng", "",
     "Training sessions that build the skills of moving into another culture: entering a community, communication "
     "across cultures, values, and understanding the political, social and religious setting."),
    ("volunteer", "shades_diversity_awareness_1996", "ERIC_ED418296", "1996", "SHADES: A Resource Manual for "
     "Diversity Awareness", "R0104", "eng", "p",
     "From Peace Corps Thailand: activities for trainers and volunteers on the diversity of the United States, to help "
     "them explain to others what it means to be an American."),
    ("volunteer", "homestay_manual_1999", "ERIC_ED438406", "1999", "Host Families Matter: The Homestay Manual", "",
     "eng", "o",
     "Planning and running homestays for trainees: choosing and preparing host families, health and safety, sample "
     "documents and lesson plans."),
    ("volunteer", "community_based_training_1997", "ERIC_ED418297", "1997", "Sourcebook for Community-Based Training "
     "Programs", "T0088", "eng", "o",
     "How to run preservice training in small groups living in separate communities: sites, staff, language and "
     "technical training, health and safety, and budgets."),
    ("volunteer", "role_of_volunteer_1981", "ERIC_ED241788", "1981", "The Role of the Volunteer in Development: A "
     "Training Manual", "", "eng", "",
     "A step-by-step training guide on development and the volunteer's role in it: assumptions about development, "
     "helping relationships, gathering information and solving problems."),
    ("volunteer", "new_role_of_volunteer_1985", "ERIC_ED288046", "1985", "The New Role of the Volunteer in "
     "Development", "T-5", "eng", "",
     "Thirty-two hours of training on the volunteer's role in another country's development, with the trainer's "
     "guide and twelve session plans."),
    ("volunteer", "roles_of_volunteer_toolkits_2002", "ERIC_ED471617", "2002", "Roles of the Volunteer in "
     "Development: Toolkits for Building Capacity", "T0005", "eng", "o",
     "An introductory booklet and six toolkits on the volunteer's roles: learner, co-trainer, co-facilitator, change "
     "agent, mentor and project co-planner, building people's own capacity."),
    ("volunteer", "working_as_counterparts_1985", "ERIC_ED288047", "1985", "Working as Counterparts: A Peace Corps "
     "In-Service Training Manual", "T-6", "eng", "",
     "Training on the frustrations of working inside host country offices and with counterparts, and on working well "
     "together."),
    ("volunteer", "supervisors_counterparts_2002", "micro_IA41153661_0786", "2002", "Working with Supervisors and "
     "Counterparts", "T0121", "eng", "or",
     "How to hold a one-day workshop for volunteers, their supervisors and counterparts, with sample sessions."),
    ("volunteer", "inservice_workshop_model_1981", "ERIC_ED241789", "1981", "In-Service Workshop Model: Development "
     "Work, Volunteer Service and Project Review", "", "eng", "",
     "A five-day in-service workshop in twelve sessions: project review, support for each volunteer, problem solving "
     "and planning future work."),
    ("volunteer", "inservice_training_manual_1985", "ERIC_ED288045", "1985", "In-Service Training Manual", "T-4",
     "eng", "c",
     "Training for serving volunteers on matters outside their technical job that affect their work (prepared by "
     "Creative Associates): project planning, working with others, and personal effectiveness."),
    ("volunteer", "close_of_service_1982", "ERIC_ED241790", "1982", "Peace Corps Close of Service Workshop: Trainer "
     "Guidelines and Workshop Materials (1982)", "", "eng", "",
     "A three-day workshop held two or three months before volunteers leave, to help them finish their work and "
     "prepare to go home."),
    ("volunteer", "close_of_service_trainer_1986", "ERIC_ED288048", "1986", "Close of Service Workshop: Trainer "
     "Guidelines and Workshop Materials (1986)", "T-07", "eng", "",
     "The 1986 trainer's guide to the close of service workshop: looking back on service, finishing the job, and "
     "returning to the United States."),
    ("volunteer", "close_of_service_participant_1986", "ERIC_ED288049", "1986", "Close of Service Workshop: "
     "Participant's Handbook", "T-08", "eng", "",
     "Worksheets and articles for volunteers at the close of service workshop: reverse culture shock, careers and "
     "going home."),
    ("volunteer", "older_volunteers_1985", "ERIC_ED288052", "1985", "Peace Corps Training and Older Volunteers",
     "T-33", "eng", "",
     "A short guide for trainers on the needs and strengths of older volunteers."),
    ("volunteer", "secondary_projects_1987", "ERIC_ED288043", "1987", "Secondary Projects", "", "eng", "o",
     "For education volunteers who take on community projects besides their teaching job: choosing, planning and "
     "running them, with case studies."),
    ("volunteer", "all_volunteer_conferences_1986", "ERIC_ED288057", "1986", "Planning and Conducting All Volunteer "
     "Conferences", "T-44", "eng", "",
     "How to plan an in-country conference for all volunteers that gives personal, programme and technical support."),
    ("volunteer", "training_guidelines_1973", "ERIC_ED137509", "1973", "Peace Corps Training Guidelines: The Program "
     "and Training Loop and a Systematic Approach to Training", "", "eng", "",
     "The eleven steps from planning a programme to evaluating training: task analysis, training objectives, "
     "learning activities and evaluation."),
    ("volunteer", "integrated_training_system_1983", "ERIC_ED307478", "1983", "An Integrated Training System: Policy "
     "and Plans", "T-1", "eng", "",
     "The Peace Corps' philosophy, goals and policy for training volunteers, and how its core training materials are "
     "used."),
    ("volunteer", "training_standards_1983", "ERIC_ED307479", "1983", "Standards for Peace Corps Training", "T-2",
     "eng", "",
     "The minimum standards for Peace Corps training worldwide and how they are monitored."),
    ("volunteer", "trainers_resource_guide_1983", "ERIC_ED307480", "1983", "A Trainer's Resource Guide", "T-12",
     "eng", "",
     "Shared knowledge for Peace Corps trainers: the training philosophy, goals, expected skills, and how to plan and "
     "run a training programme."),
]

# The Peace Corps items the approtech helper builds or keeps link-only (its list of 2026-11-23,
# /home/user/notes/approtech-peace-corps-ids.txt): never built here (the test checks it).
APPROTECH_ITEMS = {
    "ERIC_ED241770", "micro_IA41153301_0080", "ERIC_ED243656", "ERIC_ED242880", "ERIC_ED307464", "ERIC_ED307481",
    "micro_IA41153345_0710", "ERIC_ED308074", "ERIC_ED288044", "micro_IA41152945_0293", "ERIC_ED241775",
    "ERIC_ED242921", "ERIC_ED241781", "ERIC_ED241771", "ERIC_ED241772", "ERIC_ED242886", "ERIC_ED307483",
    "micro_IA41153301_0076", "ERIC_ED242564", "ERIC_ED242877", "ERIC_ED242878", "micro_IA41153345_0711",
    "ERIC_ED307484", "ERIC_ED307485", "ERIC_ED242558", "ERIC_ED242920", "ERIC_ED378400", "ERIC_ED242565",
    "ERIC_ED242563", "ERIC_ED241766", "ERIC_ED241769", "ERIC_ED241783", "ERIC_ED242881", "ERIC_ED309038",
    "micro_IA41152941_0223", "ERIC_ED307486", "ERIC_ED327732", "ERIC_ED287740", "ERIC_ED287741", "ERIC_ED307482",
    "ERIC_ED243661",
}

OFFICES = {"o": "a Peace Corps office (such as the Center for Field Assistance and Applied Research, Information "
                "Collection and Exchange, World Wise Schools, or the Office of Overseas Programming and Training "
                "Support)",
           "p": "a Peace Corps country office",
           "g": "a US government agency (the US Department of Agriculture's Extension Service with USAID)"}


def kind_letters(kind):
    """The licence letter of a book's kind ("o", "p", "g", "c" or "" for published before 1989 with no notice)."""
    return next((k for k in kind if k in "opgc"), "")


def licence_of(row):
    """(licence, licence URL, licence page, licence text) of one BOOKS row (see the module docstring): a Peace Corps
    office's work is a US government work (the line checked on govinfo.gov at every build); a contract manual of 1989
    or later carries the Peace Corps' reproduction permission; the rest were published before March 1989 with no
    notice."""
    _theme, _name, _item, year, _title, _ice, _lang, kind, _desc = row
    letter = kind_letters(kind)
    if letter in ("o", "p", "g"):
        return K.US_GOV, K.US_GOV_URL, K.GOVINFO_POLICY, K.GOVINFO_TEXT
    if letter == "c" and int(year) >= 1989:
        return PC_PERMISSION, PC_PERMISSION_URL, "", ""
    return PC_NO_NOTICE, PC_NO_NOTICE_URL, "", ""


def notice_of(row):
    """The truthful notice of one BOOKS row: who made it and why it may be shared, the reprinted passages, the health
    note, and how the copy was read."""
    _theme, name, item, year, _title, _ice, _lang, kind, _desc = row
    letter = kind_letters(kind)
    if letter in OFFICES:
        words = (f"Made and published by {OFFICES[letter]} (this copy: {year}): a work of the US government (17 U.S.C. 105), in the "
                 f"public domain.")
    elif letter == "c":
        words = (f"Prepared for the Peace Corps under contract and published by the Peace Corps in {year} with these "
                 f"words: \"{REPRODUCE}\" {CREDIT}")
        if int(year) < 1989:
            words += " It carries no copyright notice and was published before March 1989, so it is public domain."
    else:
        words = (f"Published by the Peace Corps, a US government agency, in {year} with no copyright notice: public "
                 f"domain in the US (a US government publication, and a work published in the US without a notice "
                 f"before 1 March 1989).")
    if "r" in kind:
        words += " " + REPRINTED.format(who=REPRINTS[name])
    if "h" in kind:
        words += " " + HEALTH.format(year=year) + (HIV if "v" in kind else "")
    return f"{words} {MICRO if item.startswith('micro_IA') else SCAN}"


def entry_of(row):
    """The PDF entry (refs_kit.us_pdf's fields, read whole by build_textbooks.pdfdoc_book) of one BOOKS row."""
    theme, name, item, year, title, ice, lang, kind, desc = row
    licence, url, page, text = licence_of(row)
    ice_words = f", ICE {ice}" if ice else ""
    copy = (f"ERIC {item[5:]}" if item.startswith("ERIC_") else "ERIC microfiche scan") + \
        f", Internet Archive item {item}"
    return K.us_pdf(GROUP, name=name, title=f"{title} (Peace Corps, {year})", subject=THEMES[theme][1].split(":")[0],
                    publisher=f"Peace Corps, Information Collection and Exchange{ice_words}", archive=item,
                    published=year, version=f"{year} edition ({copy})", description=desc, notice=notice_of(row),
                    licence=licence, licence_url=url, licence_page=page, licence_text=text,
                    language={"eng": "", "spa": "spa", "fra": "fra"}[lang], theme=theme)


PDFS = [entry_of(r) for r in BOOKS]


def theme_keys(theme):
    """The keys of one theme's books, in the order listed."""
    return [f"{PREFIX}:{r[1]}" for r in BOOKS if r[0] == theme]


def all_keys():
    """Every book key of this module, the index first."""
    return [f"{PREFIX}:index"] + [f"{PREFIX}:{r[1]}" for r in BOOKS]


# ====================================================================== the index

# Peace Corps books that are already in the library from other collections (linked by key; the dynamic part below
# finds books added later, such as the approtech and language helpers').
ELSEWHERE = [
    ("key", "relate:peace_corps_culture_matters", "Culture Matters: The Peace Corps Cross-Cultural Workbook (1997)"),
    ("key", "lang:fsi:tagalog", "Peace Corps Tagalog Language Correspondence Course (1994)"),
    ("key", "pclang:index", "Peace Corps language courses: every language, where it is spoken, its courses and "
                            "recordings"),
    ("word", "peace-corps-languages", "Every Peace Corps language course, lesson book, phrasebook and dictionary"),
    ("word", "languages", "Language courses (FSI, DLI and Peace Corps), phrasebooks and example sentences"),
]
LINKS = [
    ("link", "Peace Corps publications and resources (peacecorps.gov)", "https://www.peacecorps.gov/educators/"
     "resources/", "the Peace Corps' own site; it shows a bot check to programs, so open it in a browser"),
    ("link", "Peace Corps Water in Africa classroom units (World Wise Schools)", "https://archive.org/search?query="
     "%22Water+in+Africa%22+peace+corps", "units written by classroom teachers and volunteers; link-only"),
    ("link", "The Peace Corps' library of manuals (files.peacecorps.gov)", "https://files.peacecorps.gov/",
     "its /manuals/ folder is closed to programs by robots.txt; open it in a browser"),
]


def peace_corps_elsewhere():
    """[(key, title, request words)] of the Peace Corps books in the other collections of the library, found in the
    code: every guide or PDF of a more_refs module, and every sources.PDF_DOCS entry, whose publisher or title names
    the Peace Corps (this module's own books left out). The request words are the other collection's words that ask
    for the key."""
    import more_refs
    import sources
    found = []
    for m in more_refs.modules():
        c = m.COLLECTION
        if c.prefix == PREFIX:
            continue
        entries = list(c.guides.values()) + list(c.pdfs.values())
        for course in getattr(m, "COURSES", []):         # the language courses (languages.py: lang:fsi:<key>)
            entries.append(dict(name=f"fsi:{course.get('key', '')}", title=course.get("title", ""),
                                publisher=course.get("publisher", "")))
        for e in entries:
            if re.search(r"peace corps", f"{e.get('publisher', '')} {e.get('title', '')}", re.I):
                key = f"{c.prefix}:{e['name']}"
                if key not in c.own_keys():
                    continue
                words = sorted(w for w, f in c.words.items() if key in f())
                found.append((key, e.get("title", key), words))
    for e in sources.PDF_DOCS:
        if re.search(r"peace corps", f"{e.get('publisher', '')} {e.get('title', '')}", re.I):
            found.append((f"pdf:{e['name']}", e.get("title", e["name"]), []))
    return sorted(set((k, t, tuple(w)) for k, t, w in found))


def sections():
    """The index's parts: one per theme (its request word and books), then the Peace Corps books elsewhere and the
    links."""
    out = []
    for theme, (word, heading) in THEMES.items():
        entries = [("word", word, f"All {len(theme_keys(theme))} books of this theme (request word)")]
        entries += [("key", f"{PREFIX}:{r[1]}", f"{r[4]} ({r[3]})") for r in BOOKS if r[0] == theme]
        out.append((heading, f"The Peace Corps' {theme} manuals in this collection. Ask for them all with the "
                    f"request word {word}.", entries))
    out.append(("Peace Corps books in other collections", "Peace Corps books kept in other parts of the library: "
                "the cross-cultural workbook, the language courses, and the appropriate technology manuals (water, "
                "wells, sanitation, irrigation, soil conservation, fish ponds, beekeeping, poultry and small animals, "
                "forestry, building, tools, energy and food preserving).", list(ELSEWHERE)))
    out.append(("Links only", "Peace Corps sources that programs may not read; open them yourself.", list(LINKS)))
    return out


_BASE_INDEX = None


def index_book(name, work, cache=None, left_out=None, limit=None):
    """The index book (pc:index): the practical_index pages of sections(), and a last page listing every Peace Corps
    book found elsewhere in the library at build time (peace_corps_elsewhere), with its key and request words."""
    import build_textbooks as B
    book_fn, _sign = X.index_maker(PREFIX, GROUP, "Peace Corps manuals and guides: a guide to the library",
                                   "Peace Corps manuals and guides", "A guide to every Peace Corps manual and guide in "
                                   "the library, by theme: teaching, health, youth, business, agriculture, the "
                                   "environment, community development and volunteers, with their request words, and "
                                   "the Peace Corps books kept in other collections.", sections())
    book = book_fn(name, work, cache, left_out, limit)
    found = peace_corps_elsewhere()
    if found and not (limit and len(book.pages) >= limit):
        items = "".join(f"<li>{B.esc(t)} (key {B.esc(k)}" + (f"; request word {B.esc(', '.join(w))}" if w else "") +
                        ")</li>" for k, t, w in found)
        body = (f"<p>Every book of the other collections whose publisher or title names the Peace Corps, found when "
                f"this index was built ({len(found)} books).</p><ul>{items}</ul>")
        book.pages.append(B.Page("part-elsewhere-found", "Every Peace Corps book in the other collections", body,
                                 len(book.pages) + 1, ""))
    return book


def index_sign(name):
    """The weekly sign of the index: a fingerprint of its sections and of the Peace Corps books found elsewhere."""
    return K.sha(sections(), peace_corps_elsewhere())


MAKERS = {"index": (index_book, index_sign)}

WORDS = {word: (lambda t=theme: [f"{PREFIX}:index"] + theme_keys(t)) for theme, (word, _h) in THEMES.items()}
WORDS["peace-corps"] = all_keys

COLLECTION = K.Collection(PREFIX, GROUP, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "pc_office": "Peace Corps manuals produced by a Peace Corps office or country office (the copy's own pages say "
                 "so): works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at "
                 "every build).",
    "pc_no_notice": f"{PC_NO_NOTICE}: Peace Corps manuals published before 1 March 1989 with no copyright notice "
                    "(checked on each copy's front pages, 2026-11-23); a US government publication, and a work "
                    "published in the US without notice before 1989 (17 U.S.C. 405; Copyright Office Circular 3).",
    "pc_permission": f"{PC_PERMISSION}: Peace Corps contract manuals of 1989 or later printing \"{REPRODUCE}\" (the "
                     "credit is in each book's notice).",
    "pc_archive": "The copies are the Internet Archive's ERIC items (ERIC_ED...) and ERIC microfiche scans "
                  "(micro_IA...); archive.org's robots.txt allows the files and it has no AI rules (checked "
                  "2026-11-23).",
    "pc_index": "The index (pc:index) is the toolkit's own facts and links, CC0.",
}

IA = "https://archive.org/details/"
NOT_INCLUDED = [
    # another owner's copyright printed on the copy
    ("Systematic Program Design: A Handbook for Volunteers (ICE, 1982; ERIC ED242867) and its Spanish edition "
     "(ED242868)", f"Prints \"Copyright by Center for Educational Development in Health, Boston University 1980\". "
     f"Link-only. Index: {IA}ERIC_ED242867"),
    ("Community Health Education in Developing Countries (ICE M-8, 1978; ERIC ED243819)", "Prints \"Copyright 1978 by "
     f"American Public Health Association\". Link-only. Index: {IA}ERIC_ED243819"),
    ("Communicating with Pictures (ICE P-8A, 1975; ERIC ED257437)", "Prints \"Copyright: UNICEF, 1975\". Link-only. "
     f"Index: {IA}ERIC_ED257437"),
    ("The Photonovel: A Tool for Development (1976; ERIC ED307467)", "Prints \"Copyright 1976 by Dan Weaks\", all "
     f"rights reserved. Link-only. Index: {IA}ERIC_ED307467"),
    ("Audiovisual Techniques Handbook (1988; ERIC ED316198)", "Prints \"Copyright 1988 Darrel Hess\". Link-only. "
     f"Index: {IA}ERIC_ED316198"),
    ("Methodology for Teachers: Teacher's and Volunteer's Manuals and the Supplement to MFT (Peace Corps Korea, "
     "1975-1976; ERIC ED116452, ED116453, ED289353)", "The copies print \"All rights reserved\" and ERIC's notice "
     "that reproduction requires the copyright owner's permission. Link-only. Index: "
     f"{IA}ERIC_ED116452"),
    ("Guidelines for Peace Corps Cross-Cultural Training, Parts I to IV (1970; ERIC ED059937 to ED059940)",
     "Published under contract by the Center for Research and Education; the copies allow reproduction only \"by the "
     "U.S. Government, its officers, agents, and employees\", and Part III reprints copyrighted readings. Link-only. "
     f"Index: {IA}ERIC_ED059937"),
    ("Setting Up and Running a School Library (ICE ED204, 2012; ERIC ED536911)", "Reprinted with permission from "
     f"Heinemann and VSO (copyright VSO 1994). Link-only. Index: {IA}ERIC_ED536911"),
    ("Libraries for All! How to Start and Run a Basic Library (ICE RE035, 2009 and 2012; ERIC ED521842, ED536916)",
     f"Reprinted with the permission of UNESCO. Link-only. Index: {IA}ERIC_ED521842"),
    # ICE reprints of other organisations' works
    ("Health Education Training Model (ICE T-11, 1983; ERIC ED254659)", "Developed by the Hesperian Foundation (its "
     f"copyright). Link-only. Index: {IA}ERIC_ED254659"),
    ("Audio-Visual/Communications Teaching Aids Packet (ICE P-8, 1982; ERIC ED257435) and the Audio-Visual "
     "Communication Handbook (1969; micro_IA41152949_0824)", "Reprinted from Indiana University's School of Education "
     f"with its permission. Link-only. Index: {IA}ERIC_ED257435"),
    ("Visual Aids: A Guide for Peace Corps Volunteers (ICE R-2, 1982; ERIC ED258564) and Aids for Health and Home "
     "Extension Volunteers (ICE R-3, 1981; ERIC ED243820)", "Compilations that reprint other governments' and "
     "authors' pamphlets and articles (India's Visual Aids in Community Development, Benjamin Paul of Harvard). "
     f"Link-only. Index: {IA}ERIC_ED258564"),
    ("Community Nutrition Action for Child Survival (ICE R-72, 1989; ERIC ED342720)", "Prepared by the Centre for "
     f"Development and Population Activities (CEDPA) and reprinted by the Peace Corps. Link-only. Index: "
     f"{IA}ERIC_ED342720"),
    ("Stimulation Activities: Age Birth to Five Years (ICE R-19, 1983; ERIC ED308005)", "Reprinted with permission. "
     f"Link-only. Index: {IA}ERIC_ED308005"),
    ("Rural Press for Village Post-Literacy Literature (1987; ERIC ED318278) and Writing for New Readers (1987; "
     "micro_IA41155118_0096)", "Papers and a writer's manual reprinted with their authors' permission. Link-only. "
     f"Index: {IA}ERIC_ED318278"),
    ("YMCA Earth Service Corps Club Handbook (ICE M0058, 1998; ERIC ED432478)", "Reprinted with permission from YMCA "
     f"Earth Service Corps. Link-only. Index: {IA}ERIC_ED432478"),
    ("Public Participation in Urban Environmental Management (ICE, 1996; ERIC ED420497) and Participatory Program "
     "Evaluation (ICE R0094, 1995; ERIC ED421509)", "Reprinted with permission of the Environmental Health Project and "
     f"of the evaluation manual's publisher. Link-only. Index: {IA}ERIC_ED421509"),
    ("Teaching in the Whole Garden (ICE R0085, 1994; ERIC ED376975)", "Made for a UNDP/UNESCO project in Sierra "
     f"Leone (1987) and reprinted by the Peace Corps. Link-only. Index: {IA}ERIC_ED376975"),
    ("Early Stimulation Manual for Parents of Deaf Infants (ICE, 1985; ERIC ED280208)", "The St Lucia School for the "
     f"Deaf's manual, printed by the Peace Corps. Link-only. Index: {IA}ERIC_ED280208"),
    ("Strings 'N' Things: A Teaching Manual for the Blind (ICE R-24, 1981; ERIC ED215465)", "Grace Munns's craft "
     "manual from Bogota (1977), reprinted by the Peace Corps; the copy does not show it is a Peace Corps work. "
     f"Link-only. Index: {IA}ERIC_ED215465"),
    ("Guidelines for Development of a Home Industry (ICE R-14, 1981; ERIC ED242879)", "The Volunteer Rehabilitation "
     f"Project's booklet (Ethiopia), reprinted by the Peace Corps. Link-only. Index: {IA}ERIC_ED242879"),
    ("Planning National Parks for Ecodevelopment (ICE R0073, 1989; ERIC ED309033)", "Kenton Miller's book (volume II "
     f"first published 1978 elsewhere), reprinted by the Peace Corps. Link-only. Index: {IA}ERIC_ED309033"),
    ("The Design and Management of Community Projects: A Team Approach (1988; ERIC ED358298)", "Written for the "
     "Foundation for the Peoples of the South Pacific (Canada Fund); its permission covers reproduction only. "
     f"Link-only. Index: {IA}ERIC_ED358298"),
    ("Environmental Education Teachers Manual: Environmental Education Issues in the Pacific (1996; ERIC ED420496)",
     "Written by teachers of the South Pacific education departments (a regional co-publication). Link-only. Index: "
     f"{IA}ERIC_ED420496"),
    ("Adapting Language Materials (Earl Stevick, 1970; ERIC ED044667)", "Drafts of a report under contract; the copy "
     f"does not show who holds the rights. Link-only. Index: {IA}ERIC_ED044667"),
    ("English/Spanish Glossary of Health and Nutrition Terms (ICE reprint, 1985; ERIC ED288837)", "ERIC withholds its "
     "full text and the reprint's original publisher is not shown; link-only. Index: "
     "https://archive.org/details/micro_IA41153325_0051"),
    # 1989 or later, by a contractor, volunteer or outside teacher, without the reproduction notice
    ("Nonformal Education Training Module (ICE T0064, 1991; ERIC ED347390), Pictorial Apprenticeship Program Handbook "
     "(1991; ED358297), Community-Based Solid Waste Management (1997; ED430773), Life Skills and Leadership (M0098, "
     "2013; ED591126)", "Prepared under contract (the Institute for Training and Development; Evan Bloom and Sue Reed; "
     "Susan Malcik; the Firefly Group) and printed without the Peace Corps' reproduction notice. Link-only (the "
     f"shared Peace Corps licence policy). Index: {IA}ERIC_ED591126"),
    ("Volunteers' and outside teachers' manuals of 1993-1996: The World Map Project (1994, 1995; ERIC ED387407, "
     "ED391747), Environmental Activities for People Who Use English as a Foreign Language (ED376054), Income "
     "Generation and Money Management (ED374342), Above and Beyond: Secondary Activities (ED406268), Health "
     "Activities for Primary School Students (ED418953), Peace Corps Tales from Open Space (ED461017), Understanding "
     "Sri Lanka (micro_IA41153634_0721)", "Written by volunteers or others and printed without the Peace Corps' "
     f"reproduction notice. Link-only. Index: {IA}ERIC_ED376054"),
    ("World Wise Schools study guides written by classroom teachers: Destination Cameroon, Paraguay, Lithuania and "
     "Kyrgyzstan (1993-1996; ERIC ED369711, ED391748, ED395836, ED419769), Making the Most of World Wise Schools "
     "(1993), Voices from the Field and Insights from the Field (2002; ED466533, ED466534), and the 21 Water in Africa "
     "units (2000; ED455181 to ED457084)", "Prepared by outside teachers and volunteers, with stories and pictures of "
     f"many contributors; link-only. Index: {IA}ERIC_ED466533"),
    # not readable, or not a manual
    ("Peace Corps manuals whose ERIC record has no full text and no readable scan: HIV/AIDS: Integrating Prevention "
     "and Care into Your Sector (2000; ED482895, only the record page was scanned)", "No copy to read. Link-only. "
     "Index: https://archive.org/details/micro_IA41153754_0746"),
    ("Older editions kept out where a newer Peace Corps edition is built: Building Bridges (2002; ED472008), Looking "
     "at Ourselves and Others (1993; micro_IA41153538_0350), Sources of Donated Books (2012; ED536917)", "The newer "
     f"edition is built (pc:building_bridges_2010, pc:looking_at_ourselves_and_others_1998, "
     f"pc:donated_books_sources_2014). Index: {IA}ERIC_ED472008"),
    ("Peace Corps language courses, annual reports, congressional presentations, research and evaluation reports",
     "Language courses are the language collection's (and the Peace Corps language helper's); reports and research "
     "are not manuals or guides. Index: https://archive.org/search?query=creator%3A%22peace+corps%22"),
    ("Peace Corps appropriate technology manuals (water, wells, sanitation, irrigation, soil conservation, fish ponds, "
     "beekeeping, poultry, animal traction, livestock, forestry, building, tools, energy, food preserving), including "
     "Joseph eleve des poissons au Gabon (ERIC ED290337)", "In the approtech collection (apt:), not built twice; "
     "listed in pc:index. Index: https://archive.org/details/ERIC_ED241770"),
    ("peacecorps.gov and files.peacecorps.gov (the Peace Corps' own library of current manuals)", "peacecorps.gov "
     "shows a Cloudflare bot check to programs and files.peacecorps.gov's robots.txt shuts out /manuals/; link-only "
     "from pc:index. Index: https://www.peacecorps.gov/educators/resources/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
