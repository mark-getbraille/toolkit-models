"""Teaching and homeschooling outside the United States: Canada, the United Kingdom, Ireland, Australia, New Zealand,
other English-speaking countries, non-governmental organisations and the old homeschooling classics (the owner's
request of 23 November 2026: a top-level "Teaching and homeschooling" category; the 50 US states are in the sister
module of the teach-us branch). Keys: tworld:<name>. Request words: teach-world (everything here) and one per region:
tworld-canada, tworld-uk, tworld-oak (with tworld-oak-primary and tworld-oak-secondary), tworld-ireland,
tworld-australia, tworld-nz, tworld-africa-asia, tworld-ngo and tworld-classics.

What this module builds, in plain words:
  - tworld:index, the guide to teaching and homeschooling around the world: the toolkit's own facts and links (CC0,
    nothing downloaded). One page per region, each with a TABLE: for Canada one row for every province and territory
    (its curriculum, its home-schooling rules, the licence of its documents, and what the library has); then the UK
    nations, Ireland, the Australian states and territories, New Zealand, other English-speaking countries and the
    organisations (NGOs). A source the library cannot copy is a link with the reason (link-only).
  - Canada: Government of Alberta education publications under the Open Government Licence - Alberta (the licence
    line read on each publication page at every build): the Guide to Education ECS to Grade 12, the guiding framework
    for K-12 curriculum, the off-campus education and severe-disabilities handbooks, and two teaching guides for First
    Nations, Metis and Inuit learners (Our Words, Our Ways and Successful Practices).
  - United Kingdom (Open Government Licence v3.0, the line read on each page at every build): the national
    curriculum in England (framework, primary, secondary), the early years foundation stage frameworks, the elective
    home education guidance for parents and for local authorities (gov.uk); Scotland's home education guidance
    (gov.scot) and Curriculum for Excellence experiences and outcomes and benchmarks (Education Scotland); Wales's
    elective home education guidance (gov.wales).
  - Oak National Academy (England's national curriculum lessons, OGL v3.0, read from Oak's own Curriculum API bulk
    download, one book per subject and phase: tworld:oak:<subject>-<phase>, 27 books). A SIGN-UP ENTRY: the bulk
    download needs the owner's own free Oak API key, read from the environment variable OAK_API_KEY at build time and
    never written into the repository. Without it the manifest says where to ask for one. Each book has every unit
    in teaching order (its description, why it comes here, prior knowledge and national curriculum links) and every
    published lesson (outcome, key learning points, keywords, misconceptions with Oak's responses, teacher tips,
    content guidance and the video transcript). Lessons Oak marks "restricted" (third-party material) keep their
    lesson text but not their transcript. Oak's main website says ai-train=no in its robots.txt and is never read;
    its API site (open-api.thenational.academy) allows programs (checked 2026-11-23). French, German and Spanish are
    left to the language collections.
  - Australia: the Australian Curriculum (Version 9.0) "understand this learning area / general capability /
    cross-curriculum priority" pages and its F-10 overview (ACARA, CC BY 4.0, the licence line read on ACARA's
    copyright page at every build), made into one book by this module's own reader (the pages are not plain HTML).
  - Classics popular with homeschoolers, all published before 1931 (the year read from the Internet Archive record at
    every build): Charlotte Mason's Home Education series (volumes 1 to 5, with the 1886 first edition of Home
    Education), the McGuffey Eclectic Readers (primer and first to sixth, 1879 revised edition), Ray's Arithmetic
    (primary, intellectual, practical, higher, the key, and the primary algebra), and Montessori's
    own handbook, the Advanced Montessori Method and The Montessori Elementary Material. The Montessori Method (1912)
    is already in education_more.py (edumore:montessori_method_1912) and is listed, not repeated.

Already in the library and only listed in the index (never built twice): Alberta's other open publications
(sources.ALBERTA), Siyavula (South Africa, key siyavula), OpenStax, BCcampus (course:bccampus), LibreTexts,
Illustrative Mathematics and Open Up HS Math (k12), Core Knowledge, CK-12, Khan Academy and EngageNY (personal use,
courses.py), PhET (the Kiwix library), StoryWeaver and the African Storybook (read_aloud.py), NASA and NOAA (science_use.py
and emergency_prep.py), Paths to Literacy, APH and Perkins (vision_living.py, link-only).

Not built (NOT_INCLUDED, each with the reason and the address): provincial curricula under Crown copyright (BC,
Ontario and others), Ireland (no open licence; gov.ie shuts out AI companies' readers), the New Zealand Curriculum
(Tāhūrangi is a JavaScript application; education.govt.nz is CC BY-NC), Hwb (Wales) curriculum pages, CCEA, the
Australian states' syllabuses, South Africa's DBE, NCERT, other ministries, the NGO curricula under non-commercial
or own terms, Charlotte Mason's sixth volume (no PDF copy), and others.

Run from the repository's folder:
  python3 textbooks/teach_world.py tworld:index --out build/textbooks
  python3 textbooks/teach_world.py tworld:uk_national_curriculum_primary --out build/textbooks --limit 3
  python3 textbooks/teach_world.py --list teach-world
"""

import datetime
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

# The top-level group "Teaching and homeschooling": the group key "k12" of sources.GROUPS, the same key the teach-us
# branch's modules (teach_states.py, teach_index.py) use; that branch renames the group's label from "School books
# (K-12)" to "Teaching and homeschooling", so nothing is named here.
GROUP = "k12"
GROUPS = {}
PREFIX = "tworld"
CHECKED = "2026-11-23"

# ====================================================================== licences

OGL_UK = dict(licence="OGL-UK-3.0", licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/"
              "version/3/", licence_text=r"Open Government Licen[cs]e")
ALBERTA = dict(country="Canada", licence="OGL-Alberta", licence_url="https://open.alberta.ca/licence",
               publisher="Government of Alberta (Alberta Education)",
               licence_text=r"Licence\s+Open Government Licence - Alberta")
CC_BY = "CC BY 4.0"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"

CURRENT_NOTE = ("Rules, curricula and addresses change: check the publisher's own page for the newest edition before "
                "relying on it.")


def _pdf(name, title, subject, publisher, page, description, pattern=r"\.pdf$", country="United Kingdom",
         licence=None, **more):
    """One official PDF read whole from its publication page (the newest PDF the page links matching pattern), its
    licence line read on that page (or on licence_page) at every build."""
    lic = licence or OGL_UK
    return dict(dict(lic, group=GROUP, name=name, title=title, subject=subject, publisher=publisher, page=page,
                     pdf_pattern=pattern, country=country, level="reference", description=description,
                     notice=f"{CURRENT_NOTE}"), **more)


# ====================================================================== Canada (Alberta's open licence)

ALBERTA_PDFS = [
    _pdf("alberta_guide_to_education", "Guide to Education: ECS to Grade 12 (Alberta Education)",
         "Schools in Alberta: the rules", ALBERTA["publisher"], "https://open.alberta.ca/publications/1496-7359",
         "Alberta Education's yearly handbook for schools: the programs of study each grade follows, required "
         "instruction time, high school credits and diplomas, home education and other programs, students with "
         "special needs, and assessment.", country="Canada", licence=ALBERTA),
    _pdf("alberta_k12_curriculum_framework", "The Guiding Framework for the Design and Development of Kindergarten "
         "to Grade 12 Curriculum (Alberta)", "Curriculum design", ALBERTA["publisher"],
         "https://open.alberta.ca/publications/guiding-framework-design-development-k-12-curriculum",
         "How Alberta designs its K-12 curriculum: the principles, the structure of programs of study, literacy and "
         "numeracy, and how subjects build from grade to grade.", country="Canada", licence=ALBERTA),
    _pdf("alberta_off_campus_education_handbook", "Off-Campus Education Handbook (Alberta Education)",
         "Learning outside school: work experience", ALBERTA["publisher"],
         "https://open.alberta.ca/publications/off-campus-education-handbook",
         "Alberta's handbook for off-campus education: work experience, the Registered Apprenticeship Program, "
         "Green Certificate and other credit courses taken outside the school building, with safety rules.",
         country="Canada", licence=ALBERTA),
    _pdf("alberta_severe_disabilities_handbook", "Handbook for the Identification and Review of Severe Disabilities: "
         "ECS to Grade 12 (Alberta Education)", "Special education", ALBERTA["publisher"],
         "https://open.alberta.ca/publications/handbook-identification-review-severe-disabilities-ecs-grade12",
         "Alberta's criteria for identifying students with severe disabilities (including severe visual and "
         "hearing disabilities), the documents schools keep, and how files are reviewed.", country="Canada",
         licence=ALBERTA),
    _pdf("alberta_our_words_our_ways", "Our Words, Our Ways: Teaching First Nations, Métis and Inuit Learners "
         "(Alberta Education, 2017)", "Indigenous education", ALBERTA["publisher"],
         "https://open.alberta.ca/publications/9781460134757",
         "A resource for teachers of First Nations, Métis and Inuit students: background, sample strategies, the "
         "perspectives of Elders and scholars, and stories from Aboriginal teachers, in seven chapters.",
         country="Canada", licence=ALBERTA),
    _pdf("alberta_successful_practices_fnmi", "Successful Practices in First Nations, Métis and Inuit Education: "
         "Collaborative Frameworks Building Relationships, Companion Resource (Alberta Education)",
         "Indigenous education", ALBERTA["publisher"], "https://open.alberta.ca/publications/9781460106495",
         "A guide for schools, parents and communities working together to improve First Nations, Métis and Inuit "
         "students' education, with examples of collaborative frameworks.", country="Canada", licence=ALBERTA),
]

# ====================================================================== United Kingdom (Open Government Licence)

DFE = "Department for Education (England)"
GOV_UK = "https://www.gov.uk/government/publications"
UK_PDFS = [
    _pdf("uk_national_curriculum_framework", "The National Curriculum in England: Framework Document (key stages 1 to "
         "4)", "England: the national curriculum", DFE, f"{GOV_UK}/national-curriculum-in-england-framework-for-key-"
         "stages-1-to-4", "The whole national curriculum for England in one document: its aims, the school "
         "curriculum, inclusion, numeracy and language, and the programmes of study for every subject from key stage "
         "1 to 4 (ages 5 to 16).", pattern=r"national_curriculum[^/]*\.pdf$"),
    _pdf("uk_national_curriculum_primary", "The National Curriculum in England: Primary Curriculum (key stages 1 and "
         "2)", "England: the national curriculum", DFE, f"{GOV_UK}/national-curriculum-in-england-primary-curriculum",
         "The programmes of study for key stages 1 and 2 (ages 5 to 11): English, mathematics, science, art and "
         "design, computing, design and technology, geography, history, music and physical education.",
         pattern=r"PRIMARY_national_curriculum[^/]*\.pdf$"),
    _pdf("uk_national_curriculum_secondary", "The National Curriculum in England: Secondary Curriculum (key stages 3 "
         "and 4)", "England: the national curriculum", DFE,
         f"{GOV_UK}/national-curriculum-in-england-secondary-curriculum",
         "The programmes of study for key stages 3 and 4 (ages 11 to 16): English, mathematics, science, and the "
         "other subjects including citizenship and computing.", pattern=r"Secondary_national_curriculum[^/]*\.pdf$"),
    _pdf("uk_eyfs_group_and_school", "Early Years Foundation Stage Statutory Framework: for group and school-based "
         "providers (England)", "England: early years (birth to 5)", DFE,
         f"{GOV_UK}/early-years-foundation-stage-framework--2",
         "The standards for learning, development and care for children from birth to 5 in nurseries and schools: "
         "the seven areas of learning, the early learning goals, assessment, and safeguarding and welfare.",
         pattern=r"EYFS_group_and_school[^/]*\.pdf$"),
    _pdf("uk_eyfs_childminders", "Early Years Foundation Stage Statutory Framework: for childminders (England)",
         "England: early years (birth to 5)", DFE, f"{GOV_UK}/early-years-foundation-stage-framework--2",
         "The early years foundation stage as it applies to childminders: learning and development, assessment, "
         "and safeguarding and welfare.", pattern=r"EYFS_childminders[^/]*\.pdf$"),
    _pdf("uk_ehe_guidance_parents", "Elective Home Education: Guidance for Parents (England)",
         "Home education: England", DFE, f"{GOV_UK}/elective-home-education",
         "The Department for Education's guidance for parents in England who educate their children at home: the "
         "law, what a suitable education is, local authorities' role, children with special educational needs, "
         "and exams.", pattern=r"EHE_guidance_for_parents[^/]*\.pdf$"),
    _pdf("uk_ehe_guidance_local_authorities", "Elective Home Education: Departmental Guidance for Local Authorities "
         "(England)", "Home education: England", DFE, f"{GOV_UK}/elective-home-education",
         "The guidance local authorities in England follow on home education: parents' rights and duties, making "
         "informal enquiries, school attendance orders, safeguarding, and support for families.",
         pattern=r"Elective_home_education_departmental_guidance[^/]*\.pdf$"),
    _pdf("scotland_home_education_guidance", "Home Education Guidance (Scottish Government)",
         "Home education: Scotland", "Scottish Government",
         "https://www.gov.scot/publications/home-education-guidance/documents/",
         "The Scottish Government's guidance on home education: parents' rights and duties, withdrawing a child "
         "from school (consent), what an efficient education is, local authorities' role, and children with "
         "additional support needs.", pattern=r"0055026\.pdf$"),
]

# Education Scotland: Curriculum for Excellence (its terms of use: "Crown copyright ... under the terms of the Open
# Government Licence", checked on the terms page at every build). The language areas are left to the language
# collections.
ES = "https://education.gov.scot"
ES_EO = f"{ES}/curriculum-for-excellence/experiences-and-outcomes/"
ES_BM = f"{ES}/curriculum-for-excellence/curriculum-for-excellence-benchmarks/"
ES_TERMS = dict(licence_page=f"{ES}/terms-of-use/")
SCOTLAND_CFE = [
    ("all_experiences_outcomes", ES_EO, r"all-experiencesoutcomes[^/]*\.pdf$",
     "Curriculum for Excellence: all experiences and outcomes",
     "Every experience and outcome of Scotland's Curriculum for Excellence, from early level to fourth level, in "
     "one document: expressive arts, health and wellbeing, languages, mathematics, religious and moral education, "
     "sciences, social studies and technologies."),
    ("benchmarks_literacy_english", ES_BM, r"literacyenglishbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: literacy and English",
     "What a learner shows at each level in listening, talking, reading and writing in English."),
    ("benchmarks_numeracy_maths", ES_BM, r"numeracyandmathematicsbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: numeracy and mathematics",
     "What a learner shows at each level in number, money, time, measurement, shape, data and analysis."),
    ("benchmarks_sciences", ES_BM, r"sciencesbenchmarks[^/]*\.pdf$", "Curriculum for Excellence benchmarks: sciences",
     "What a learner shows at each level in the planet, forces, the body, materials and topical science."),
    ("benchmarks_social_studies", ES_BM, r"social-studiesbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: social studies",
     "What a learner shows at each level in history, geography and society."),
    ("benchmarks_technologies", ES_BM, r"technologiesbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: technologies",
     "What a learner shows at each level in digital literacy, computing, food, textiles and craft."),
    ("benchmarks_expressive_arts", ES_BM, r"expressive-arts-benchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: expressive arts", "What a learner shows at each level in art and "
     "design, dance, drama and music."),
    ("benchmarks_rme", ES_BM, r"rmebenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: religious and moral education",
     "What a learner shows at each level in Christianity, world religions and moral values."),
    ("benchmarks_rerc", ES_BM, r"rerc_benchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: religious education in Roman Catholic schools",
     "What a learner shows at each level in religious education in Roman Catholic schools."),
    ("benchmarks_physical_education", ES_BM, r"hwbphysicaleducationbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: physical education", "What a learner shows at each level in physical "
     "education: movement, skills, fitness and cooperation."),
    ("benchmarks_food_health", ES_BM, r"hwbfoodhealthbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: food and health", "What a learner shows at each level in food, "
     "nutrition, hygiene and health."),
    ("benchmarks_personal_social", ES_BM, r"hwbpersonalsocial-educationbenchmarks[^/]*\.pdf$",
     "Curriculum for Excellence benchmarks: personal and social education", "What a learner shows at each level in "
     "mental, emotional and social wellbeing, relationships and safety."),
]
UK_PDFS += [
    _pdf(f"scotland_cfe_{name}", f"{title} (Education Scotland)", "Scotland: Curriculum for Excellence",
         "Education Scotland", page, description, pattern=pattern, **ES_TERMS)
    for name, page, pattern, title, description in SCOTLAND_CFE
]

# Wales: the elective home education guidance (2025) as a web page; gov.wales's copyright statement names the OGL.
WALES_EHE = "https://www.gov.wales/elective-home-education-guidance-html"
UK_GUIDES = [
    X.page_list_book(
        GROUP, "wales_ehe_guidance", "Elective Home Education Guidance (Welsh Government)", "Home education: Wales",
        "Welsh Government", [WALES_EHE], r"^https://www\.gov\.wales/elective-home-education-guidance-html$",
        "The Welsh Government's guidance on elective home education (2025): parents' rights and duties, local "
        "authorities' role, support for home-educating families, and children with additional learning needs.",
        CURRENT_NOTE, country="United Kingdom", licence=OGL_UK["licence"], licence_url=OGL_UK["licence_url"],
        licence_page="https://www.gov.wales/copyright-statement", licence_text=r"Open Government Licence"),
]

# ====================================================================== Oak National Academy (sign-up entry)

OAK_API = "https://open-api.thenational.academy"
OAK_KEY_ENV = "OAK_API_KEY"
OAK_SIGNUP = f"{OAK_API}/docs/about-oaks-api/api-keys"
OAK_LICENCE_PAGE = f"{OAK_API}/docs/about-oaks-api/api-limits"
OAK_LICENCE_TEXT = r"licensed on the Open Government Licence \(OGL\) v3\.0"
# (slug, title, phases) from Oak's bulk download page (checked 2026-11-23); French, German and Spanish left out.
OAK_SUBJECTS = [
    ("art", "Art and design", ("primary", "secondary")),
    ("citizenship", "Citizenship", ("secondary",)),
    ("computing", "Computing", ("primary", "secondary")),
    ("cooking-nutrition", "Cooking and nutrition", ("primary", "secondary")),
    ("design-technology", "Design and technology", ("primary", "secondary")),
    ("english", "English", ("primary", "secondary")),
    ("geography", "Geography", ("primary", "secondary")),
    ("history", "History", ("primary", "secondary")),
    ("maths", "Maths", ("primary", "secondary")),
    ("music", "Music", ("primary", "secondary")),
    ("physical-education", "Physical education", ("primary", "secondary")),
    ("rshe-pshe", "RSHE (PSHE): relationships, sex and health education", ("primary", "secondary")),
    ("religious-education", "Religious education", ("primary", "secondary")),
    ("science", "Science", ("primary", "secondary")),
]
OAK_LANGUAGES = ("french", "german", "spanish")


def oak_pieces():
    """The Oak pieces ("maths-primary"), one per subject and phase, in Oak's order."""
    return [f"{slug}-{phase}" for slug, _t, phases in OAK_SUBJECTS for phase in phases]


def oak_subject(piece):
    """(slug, title, phase) of an Oak piece, or None when it is not one of OAK_SUBJECTS."""
    for slug, title, phases in OAK_SUBJECTS:
        for phase in phases:
            if piece == f"{slug}-{phase}":
                return slug, title, phase
    return None


def oak_download(piece, key):
    """The bulk JSON of one Oak piece ({sequenceSlug, subjectTitle, sequence, lessons}) from Oak's bulk download
    (POST /api/bulk with the owner's key; the answer is a zip of one JSON file per piece). None when the key is
    refused."""
    import build_textbooks as B
    body = json.dumps({"subjects": [piece]}).encode("utf-8")
    try:
        # keyed_urlopen: the key goes only to Oak's own site, also when it answers "moved" (the bulk zip may be
        # handed out from another address, which gets the request without the key).
        with B.keyed_urlopen(f"{OAK_API}/api/bulk", {"Authorization": f"Bearer {key}"}, data=body, method="POST",
                             headers={"User-Agent": B.USER_AGENT, "Content-Type": "application/json"},
                             timeout=600) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return None
        raise
    return oak_json_from_zip(data, piece)


def oak_json_from_zip(data, piece):
    """The piece's JSON from the bulk zip (the one file whose sequenceSlug is the piece, else the only JSON file)."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        found = []
        for name in z.namelist():
            if name.lower().endswith(".json"):
                doc = json.loads(z.read(name).decode("utf-8"))
                if doc.get("sequenceSlug") == piece:
                    return doc
                found.append(doc)
    if len(found) == 1:
        return found[0]
    raise ValueError(f"the bulk download has no file for {piece}")


def _items(values, field):
    """The text of a list of Oak records ([{field: text}] or [text])."""
    out = []
    for v in values or []:
        text = v.get(field, "") if isinstance(v, dict) else str(v)
        if text:
            out.append(str(text))
    return out


def oak_lesson_html(lesson):
    """One Oak lesson as HTML (its own heading level 3 and below): outcome, key learning points, keywords,
    misconceptions with Oak's responses, teacher tips, content guidance and supervision, and the transcript (not for a
    restricted lesson)."""
    import build_textbooks as B
    out = [f'<h3>{B.esc(lesson.get("lessonTitle", ""))}</h3>']
    if lesson.get("pupilLessonOutcome"):
        out.append(f"<p>Lesson outcome: {B.esc(lesson['pupilLessonOutcome'])}</p>")
    points = _items(lesson.get("keyLearningPoints"), "keyLearningPoint")
    if points:
        out.append("<h4>Key learning points</h4><ul>" + "".join(f"<li>{B.esc(p)}</li>" for p in points) + "</ul>")
    words = [(k.get("keyword", ""), k.get("description", "")) for k in lesson.get("lessonKeywords") or []
             if isinstance(k, dict)]
    if words:
        out.append("<h4>Keywords</h4><dl>" + "".join(f"<dt>{B.esc(w)}</dt><dd>{B.esc(d)}</dd>" for w, d in words)
                   + "</dl>")
    mis = [(m.get("misconception", ""), m.get("response", "")) for m in
           lesson.get("misconceptionsAndCommonMistakes") or [] if isinstance(m, dict)]
    if mis:
        out.append("<h4>Common misconceptions</h4><ul>" + "".join(
            f"<li>{B.esc(m)} Response: {B.esc(r)}</li>" for m, r in mis) + "</ul>")
    tips = _items(lesson.get("teacherTips"), "teacherTip")
    if tips:
        out.append("<h4>Teacher tips</h4><ul>" + "".join(f"<li>{B.esc(t)}</li>" for t in tips) + "</ul>")
    guidance = [g.get("contentGuidanceLabel") or g.get("contentGuidanceDescription", "")
                for g in lesson.get("contentGuidance") or [] if isinstance(g, dict)]
    if guidance or lesson.get("supervisionLevel"):
        out.append("<h4>Content guidance</h4><p>" + B.esc("; ".join([g for g in guidance if g] +
                   ([f"supervision: {lesson['supervisionLevel']}"] if lesson.get("supervisionLevel") else [])))
                   + "</p>")
    if lesson.get("transcript_sentences") and not lesson.get("restricted"):
        out.append("<h4>Video transcript</h4>" + K.text_html(str(lesson["transcript_sentences"])))
    elif lesson.get("restricted"):
        out.append("<p>Oak marks this lesson restricted (it uses material of other owners), so its transcript is "
                   "left out; open the lesson on Oak's website.</p>")
    if lesson.get("canonicalUrl") or lesson.get("oakUrl"):
        url = lesson.get("canonicalUrl") or lesson.get("oakUrl")
        out.append(f'<p>On Oak\'s website: <a href="{B.esc(url)}">{B.esc(url)}</a></p>')
    return "".join(out)


def oak_book_from_json(doc, piece, limit=None):
    """The Book of one Oak piece from its bulk JSON: one page per unit in teaching order (unit facts, then each of its
    published lessons in lesson order); a lesson no unit lists goes on a last page."""
    import build_textbooks as B
    slug, title, phase = oak_subject(piece) or (piece, doc.get("subjectTitle", piece), "")
    lessons = {le["lessonSlug"]: le for le in doc.get("lessons", []) if le.get("lessonSlug")}
    used = set()
    book = K.new_book(f"{PREFIX}_oak_{piece.replace('-', '_')}", f"Oak National Academy: {title}, {phase} "
                      f"(England's national curriculum lessons)", f"England: {title}", GROUP,
                      "Oak National Academy", "OGL-UK-3.0", OGL_UK["licence_url"], f"{OAK_API}/bulk-download",
                      f"Oak National Academy's {phase} {title.lower()} curriculum for England: every unit in teaching "
                      "order with its description and prior knowledge, and every published lesson with its outcome, "
                      "key learning points, keywords, misconceptions, teacher tips and video transcript.",
                      "Contains Oak National Academy material licensed under the Open Government Licence v3.0 "
                      "(Oak's own lessons; material of other owners is not included). Read from Oak's Curriculum API "
                      "bulk download with the owner's API key. " + CURRENT_NOTE, country="United Kingdom",
                      level="school", changes="Oak's bulk curriculum data made into web pages, one per unit")
    for number, unit in enumerate(doc.get("sequence", []), 1):
        if limit and len(book.pages) >= limit:
            break
        head = unit.get("unitTitle", f"Unit {number}")
        year = unit.get("year") or unit.get("yearSlug") or ""
        tier = unit.get("tier") if isinstance(unit.get("tier"), str) else (unit.get("tier") or {}).get("title", "")
        facts = K.dl([("Year", year), ("Key stage", unit.get("keyStageSlug", "")),
                      ("Pathway", unit.get("pathway") or ""), ("Tier", tier or ""),
                      ("Exam board", (unit.get("examBoard") or {}).get("title", "")
                       if isinstance(unit.get("examBoard"), dict) else unit.get("examBoard") or ""),
                      ("Threads", ", ".join(_items(unit.get("threads"), "title")))])
        body = facts
        if unit.get("description"):
            body += f"<p>{B.esc(unit['description'])}</p>"
        if unit.get("whyThisWhyNow"):
            body += f"<h2>Why this, why now</h2><p>{B.esc(unit['whyThisWhyNow'])}</p>"
        for label, field in (("Prior knowledge", "priorKnowledgeRequirements"),
                             ("National curriculum content", "nationalCurriculumContent")):
            values = _items(unit.get(field), "")
            if values:
                body += f"<h2>{label}</h2><ul>" + "".join(f"<li>{B.esc(v)}</li>" for v in values) + "</ul>"
        unit_lessons = sorted(unit.get("unitLessons") or [], key=lambda x: x.get("lessonOrder") or 0)
        if unit_lessons:
            body += "<h2>Lessons</h2>"
        for ul in unit_lessons:
            le = lessons.get(ul.get("lessonSlug"))
            if le is None:
                body += f"<h3>{B.esc(ul.get('lessonTitle', ''))}</h3><p>Not published yet.</p>"
                continue
            used.add(ul["lessonSlug"])
            body += oak_lesson_html(le)
        label = f"{head} ({year})" if year and str(year) not in head else head
        book.pages.append(B.Page(f"unit-{number}-{B.slug(head, 40)}", label, body, number, ""))
    rest = [le for s, le in lessons.items() if s not in used]
    if rest and not (limit and len(book.pages) >= limit):
        book.pages.append(B.Page("other-lessons", "Other lessons", "".join(oak_lesson_html(le) for le in rest),
                                 len(book.pages) + 1, ""))
    return book


def oak_book(name, work, cache=None, left_out=None, limit=None):
    """The book of one Oak piece (name "oak:<piece>"): a sign-up entry (see the module docstring)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    piece = name.split(":", 1)[1] if ":" in name else ""
    found = oak_subject(piece)
    if not found:
        left_out.append({"title": name, "reason": "Not one of the Oak subjects built here (OAK_SUBJECTS)."})
        return None
    title = f"Oak National Academy: {found[1]}, {found[2]}"
    key = os.environ.get(OAK_KEY_ENV, "").strip()
    if not key:
        left_out.append({"title": title, "reason": f"A sign-up entry: Oak's bulk download needs the owner's own free "
                         f"Oak API key (ask for one at {OAK_SIGNUP}, then set {OAK_KEY_ENV} in the build's settings, "
                         "never in the repository).", "url": OAK_SIGNUP, "fetch_yourself": True})
        return None
    if not K.readable(f"{OAK_API}/api/bulk", cache):
        left_out.append({"title": title, "reason": "Oak's API site does not allow programs now (robots.txt)."})
        return None
    words = " ".join(B.fetch(OAK_LICENCE_PAGE, cache).split())
    if not re.search(OAK_LICENCE_TEXT, words):
        left_out.append({"title": title, "reason": f"Oak's licence line was not found on {OAK_LICENCE_PAGE}; not "
                         "built until it is checked again."})
        return None
    doc = oak_download(piece, key)
    if doc is None:
        left_out.append({"title": title, "reason": f"Oak refused the key in {OAK_KEY_ENV}; check it at {OAK_SIGNUP}."})
        return None
    book = oak_book_from_json(doc, piece, limit)
    book.version = f"Oak bulk download, read {datetime.date.today().isoformat()}"
    return book


def oak_sign(name):
    """The weekly sign of an Oak piece: the piece and the month (Oak adds lessons from time to time)."""
    import directory_sources as D
    return K.sha(name, D.month_token())


# ====================================================================== Australia: ACARA (CC BY 4.0)

ACARA = "https://www.australiancurriculum.edu.au"
ACARA_TERMS = f"{ACARA}/content/acara-curriculum/au/en/copyright-and-terms-of-use.html"
ACARA_TEXT = r"Creative Commons Attribution 4\.0 International"
ACARA_INFO = f"{ACARA}/curriculum-information"
ACARA_PAGES = [f"{ACARA}/help/f-10-curriculum-overview"] + [
    f"{ACARA}/help/f-10-curriculum-overview/{p}" for p in (
        "why-do-we-have-an-australian-curriculum", "the-three-dimensions-of-the-australian-curriculum",
        "planning--teaching--assessing-and-reporting")] + [
    f"{ACARA_INFO}/understand-this-learning-area/{a}" for a in (
        "english", "mathematics", "science", "humanities-and-social-sciences", "health-and-physical-education",
        "the-arts", "technologies")] + [
    f"{ACARA_INFO}/understand-this-general-capability/{c}" for c in (
        "literacy", "numeracy", "digital-literacy", "critical-and-creative-thinking", "ethical-understanding",
        "intercultural-understanding", "personal-and-social-capability")] + [
    f"{ACARA_INFO}/understand-this-cross-curriculum-priority/{p}" for p in (
        "aboriginal-and-torres-strait-islander-histories-and-cultures", "asia-and-australias-engagement-with-asia",
        "sustainability")]

_CMP = re.compile(r'<div data-cmp-data-layer="[^"]*"\s+id="([^"]*)"\s+class="cmp-text\s*">(.*?)</div>', re.S)
_KEEP = {"p", "ul", "ol", "li", "strong", "b", "em", "i", "table", "tr", "td", "th", "thead", "tbody", "br"}


def acara_html(page_text):
    """(title, body HTML) of one ACARA page: the text blocks (div class "cmp-text") in order, the "On this page" list
    and the footer left out, its h1 to h6 headings made level 2 and 3, links and other tags reduced to their words."""
    import html as _html
    m = re.search(r"<title>(.*?)</title>", page_text, re.S)
    title = " ".join(_html.unescape(re.sub(r"\s*\|.*$", "", m.group(1))).split()) if m else ""
    parts = []
    for ident, inner in _CMP.findall(page_text):
        if ident.startswith("footer") or re.fullmatch(r"\s*On this page\s*", re.sub(r"<[^>]+>", " ", inner)):
            continue
        if "<a " in inner and not re.sub(r"<a\b.*?</a>|<[^>]+>|&nbsp;|\s", "", inner, flags=re.S):
            continue                         # a block of links only: the page's own "On this page" list

        def tag(mt):
            """Keep a few plain tags without their attributes; headings become h2 (h1 to h4) or h3 (h5, h6)."""
            closing, name = mt.group(1), mt.group(2).lower()
            if re.fullmatch(r"h[1-6]", name):
                return f"<{closing}{'h2' if name in ('h1', 'h2', 'h3', 'h4', 'h6') else 'h3'}>"
            return f"<{closing}{name}>" if name in _KEEP else ""
        clean = re.sub(r"<(/?)([a-zA-Z0-9]+)\b[^>]*>", tag, inner)
        clean = re.sub(r"(&nbsp;|\s)+", " ", clean).replace("<p> </p>", "").strip()
        if re.sub(r"<[^>]+>|\s", "", clean):
            parts.append(clean)
    return title, "".join(parts)


def acara_book(name, work, cache=None, left_out=None, limit=None):
    """The Australian Curriculum guide pages (ACARA_PAGES) as one book, after checking ACARA's licence line."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    if not re.search(ACARA_TEXT, " ".join(B.fetch(ACARA_TERMS, cache).split())):
        left_out.append({"title": "The Australian Curriculum", "reason": f"ACARA's licence line was not found on "
                         f"{ACARA_TERMS}; not built until it is checked again."})
        return None
    book = K.new_book(f"{PREFIX}_acara_curriculum_guide", "The Australian Curriculum (Version 9.0): understanding the "
                      "learning areas, general capabilities and cross-curriculum priorities (ACARA)",
                      "Australia: the national curriculum", GROUP,
                      "Australian Curriculum, Assessment and Reporting Authority (ACARA)", CC_BY, CC_BY_URL,
                      ACARA_PAGES[0], "ACARA's own explanation of the Australian Curriculum, Foundation to Year 10: "
                      "why there is a national curriculum, its three dimensions, planning and reporting, and for "
                      "each learning area, general capability and cross-curriculum priority its rationale, aims, "
                      "structure and key considerations.",
                      "© Australian Curriculum, Assessment and Reporting Authority (ACARA) 2010 to present, unless "
                      "otherwise indicated, licensed under CC BY 4.0; ACARA does not endorse this copy. The year-by-"
                      "year content descriptions are on ACARA's website. " + CURRENT_NOTE, country="Australia",
                      changes="the text of ACARA's pages made into one book; menus and logos left out")
    for number, url in enumerate(ACARA_PAGES, 1):
        if limit and len(book.pages) >= limit:
            break
        if not K.readable(url, cache):
            left_out.append({"title": url, "reason": "ACARA's robots.txt does not allow this page now."})
            continue
        try:
            title, body = acara_html(B.fetch(url, cache))
        except (urllib.error.URLError, OSError) as e:
            left_out.append({"title": url, "reason": f"It could not be read ({e})."})
            continue
        if not body:
            left_out.append({"title": url, "reason": "The page has no text blocks now."})
            continue
        body += f'<p>Source: <a href="{B.esc(url)}">{B.esc(url)}</a></p>'
        book.pages.append(B.Page(f"part-{number}-{B.slug(title or url, 40)}", title or url, body, number, ""))
    return book


def acara_sign(name):
    """The weekly sign of the ACARA book: the list of pages and the month."""
    import directory_sources as D
    return K.sha(ACARA_PAGES, D.month_token())


# ====================================================================== classics popular with homeschoolers

CLASSIC_NOTE = ("Published in {year}: an old schoolbook or book on education kept for its lessons and its history. "
                "Its science, its views of children, of girls and boys, of disabled children and of other peoples "
                "and religions are those of its time; some of what it says is outdated or offensive today.")


def _old(name, title, subject, publisher, archive, year, description, country="United States"):
    """One old classic of the Internet Archive (published before 1931, the year checked at every build)."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=CLASSIC_NOTE,
                    country=country)


MASON = "Charlotte M. Mason (Kegan Paul, Trench, Trübner)"
CLASSICS = [
    _old("mason_home_education_1886", "Home Education: A Course of Lectures to Ladies (Charlotte Mason, first "
         "edition, 1886)", "Homeschooling: Charlotte Mason", MASON, "cu31924031757283", 1886,
         "The first edition of Charlotte Mason's lectures on bringing up and teaching children under nine: "
         "out-of-door life, habit, lessons (reading, number, nature study, history and more) and the will and "
         "conscience.", country="United Kingdom"),
    _old("mason_home_education_series_vol1", "Home Education (Home Education Series, volume 1, Charlotte Mason, 1906 "
         "edition)", "Homeschooling: Charlotte Mason", MASON, "homeeducationser01masouoft", 1906,
         "Volume 1 of Charlotte Mason's Home Education series in its revised edition: the education of children "
         "under nine at home.", country="United Kingdom"),
    _old("mason_parents_and_children_1897", "Parents and Children: A Sequel to Home Education (Home Education Series, "
         "volume 2, Charlotte Mason, 1897)", "Homeschooling: Charlotte Mason", MASON, "b2195916x", 1897,
         "Charlotte Mason's essays for parents on family life, the training of character, and the parent as "
         "educator.", country="United Kingdom"),
    _old("mason_school_education_vol3", "School Education (Home Education Series, volume 3, Charlotte Mason, 1906 "
         "edition)", "Homeschooling: Charlotte Mason", MASON, "homeeducationser03masouoft", 1906,
         "Charlotte Mason on the education of children from nine to twelve: books, narration, the curriculum and "
         "the Parents' Union School.", country="United Kingdom"),
    _old("mason_ourselves_vol4", "Ourselves (Home Education Series, volume 4, Charlotte Mason, 1905)",
         "Homeschooling: Charlotte Mason", MASON, "home-education-series-vol-iv-ourselves", 1905,
         "Charlotte Mason's book written for young people themselves: self-knowledge and self-direction, in two "
         "books.", country="United Kingdom"),
    _old("mason_formation_of_character_vol5", "Some Studies in the Formation of Character (Home Education Series, "
         "volume 5, Charlotte Mason)", "Homeschooling: Charlotte Mason", MASON,
         "some-studies-in-the-formation-of-charact", 1923,
         "Charlotte Mason's case studies and essays on the formation of character in children and young people.",
         country="United Kingdom"),
]
MCGUFFEY_PUB = "William Holmes McGuffey (Van Antwerp, Bragg; American Book Company)"
CLASSICS += [
    _old(f"mcguffey_{n}", f"McGuffey's {t} (revised edition)", "Reading: McGuffey Readers", MCGUFFEY_PUB, a, y, d)
    for n, t, a, y, d in [
        ("eclectic_primer", "Eclectic Primer", "mcguffeyseclecti00mcgu_3", 1896,
         "The first book of the McGuffey series: the alphabet, short words and very short lessons with phonic "
         "drills."),
        ("first_reader", "First Eclectic Reader", "mcguffeysfirstec00mcgu_0", 1879,
         "Simple lessons in reading and spelling with word lists, script lessons and short stories."),
        ("second_reader", "Second Eclectic Reader", "mcguffeysseconde00mcgu_0", 1896,
         "Short stories and poems for young readers, each with its new words and questions."),
        ("third_reader", "Third Eclectic Reader", "mcguffeysthirdec00mcgu_0", 1879,
         "Longer stories, poems and fables, with definitions and exercises in reading aloud."),
        ("fourth_reader", "Fourth Eclectic Reader", "mcguffeysfourthe00mcgu_1", 1879,
         "Stories, poems and lessons on nature and conduct, with notes on authors, definitions and articulation."),
        ("fifth_reader", "Fifth Eclectic Reader", "mcguffeysfifthec00mcgu_0", 1879,
         "Selections of prose and poetry by well-known authors, with rules of elocution and notes."),
        ("sixth_reader", "Sixth Eclectic Reader", "mcguffeyssixthec00mcgu_0", 1879,
         "Advanced selections of English and American literature and oratory, with the principles of elocution."),
    ]
]
RAY_PUB = "Joseph Ray (Van Antwerp, Bragg; American Book Company)"
CLASSICS += [
    _old(f"rays_{n}", t, "Mathematics: Ray's Arithmetic", RAY_PUB, a, y, d)
    for n, t, a, y, d in [
        ("new_primary_arithmetic", "Ray's New Primary Arithmetic for Young Learners (1877)",
         "raysnewprimarya00raygoog", 1877, "The first book of Ray's series: counting, adding, subtracting, "
         "multiplying and dividing small numbers with oral and written exercises."),
        ("new_intellectual_arithmetic", "Ray's New Intellectual Arithmetic (1877)", "raysnewintellect00rayjrich",
         1877, "Ray's mental arithmetic: problems worked in the head, fractions, and simple business arithmetic."),
        ("new_practical_arithmetic", "Ray's New Practical Arithmetic (1877)", "raysnewpractical0000jose", 1877,
         "Ray's written arithmetic: whole numbers, fractions, decimals, measures, percentage, interest, ratio, "
         "roots and mensuration."),
        ("new_higher_arithmetic", "Ray's New Higher Arithmetic (1880)", "cu31924031236627", 1880,
         "The advanced book of the series: the principles of arithmetic, number theory, business arithmetic, "
         "progressions and mensuration."),
        ("key_new_arithmetic", "Key to Ray's New Arithmetic: Intellectual and Practical (1907 printing)",
         "keytoraysnewarit00rayj", 1907, "The worked answers to Ray's New Intellectual and New Practical "
         "Arithmetic, for the teacher."),
        ("primary_elements_of_algebra", "Ray's Primary Elements of Algebra for Common Schools and Academies (1866)",
         "cu31924031244258", 1866,
         "The first algebra of Ray's series: symbols, equations, factoring, fractions, powers and roots."),
    ]
]
CLASSICS += [
    _old("montessori_own_handbook_1914", "Dr. Montessori's Own Handbook (Maria Montessori, 1914)",
         "Education: Montessori", "Maria Montessori (Frederick A. Stokes)", "drmontessorisown01mont", 1914,
         "Montessori's short practical guide to her materials and exercises: motor education, the senses, "
         "writing, reading and number.", country="Italy"),
    _old("montessori_spontaneous_activity_1917", "Spontaneous Activity in Education (The Advanced Montessori Method, "
         "volume 1, Maria Montessori, 1917)", "Education: Montessori", "Maria Montessori (Frederick A. Stokes)",
         "spontaneousactiv0000unse_d0a4", 1917,
         "Montessori's method for children of seven to eleven: attention, intelligence, imagination and the will.",
         country="Italy"),
    _old("montessori_advanced_method_vol2_1917", "The Advanced Montessori Method, volume 2 (Maria Montessori, 1917)",
         "Education: Montessori", "Maria Montessori (William Heinemann)", "b32842028_0002", 1917,
         "The second volume of the Advanced Montessori Method: the elementary materials for grammar, reading, "
         "arithmetic, geometry, drawing, music and metrics.", country="Italy"),
    _old("montessori_elementary_material_1917", "The Montessori Elementary Material (Maria Montessori, 1917)",
         "Education: Montessori", "Maria Montessori (Frederick A. Stokes; Robert Bentley)", "montessorielemen0000mari",
         1917, "The American edition of the Advanced Montessori Method's second volume: the materials and lessons "
         "for the elementary school years.", country="Italy"),
]

# ====================================================================== the index (tables, the toolkit's own CC0)

# Each region's table: (place, what, address, licence and status, in the library). "library" names keys or request
# words; "" for none. The Canada table has one row for every province and territory (tests check this).
PROVINCES = ["British Columbia", "Alberta", "Saskatchewan", "Manitoba", "Ontario", "Quebec", "New Brunswick",
             "Nova Scotia", "Prince Edward Island", "Newfoundland and Labrador", "Yukon", "Northwest Territories",
             "Nunavut"]
NO_ANSWER = f"its site refused or did not answer the build machine's reader ({CHECKED}); address as published"

CANADA_ROWS = [
    ("British Columbia", "Curriculum (K-12)", "https://curriculum.gov.bc.ca/",
     "Copyright Province of BC, all rights reserved (link-only)", ""),
    ("British Columbia", "Homeschooling", "https://www2.gov.bc.ca/gov/content/education-training/k-12/support/"
     "classroom-alternatives/homeschooling", "Copyright Province of BC (link-only)", ""),
    ("Alberta", "Curriculum (new.learnalberta.ca)", "https://curriculum.learnalberta.ca/",
     "Its own terms; the programs of study are not on Alberta's open-licence site (link-only)", ""),
    ("Alberta", "Home education", "https://www.alberta.ca/home-education", "Link-only (alberta.ca page)",
     "tworld:alberta_guide_to_education (its home education part)"),
    ("Alberta", "Open Government Licence - Alberta publications", "https://open.alberta.ca/publications",
     "Open Government Licence - Alberta (built)", "request word tworld-canada"),
    ("Saskatchewan", "Curriculum", "https://curriculum.gov.sk.ca/", "Crown copyright (link-only)", ""),
    ("Saskatchewan", "Home-based education", "https://www.saskatchewan.ca/residents/education-and-learning/"
     "prek-12-education-early-learning-and-schools/home-schooling", "Crown copyright (link-only)", ""),
    ("Manitoba", "Curriculum", "https://www.edu.gov.mb.ca/k12/cur/index.html", "Crown copyright (link-only)", ""),
    ("Manitoba", "Homeschooling Office", "https://www.edu.gov.mb.ca/k12/schools/ind/homeschool/index.html",
     "Crown copyright (link-only)", ""),
    ("Ontario", "Curriculum and resources", "https://www.dcp.edu.gov.on.ca/en/",
     "King's Printer for Ontario: copies for non-commercial use without changes only (link-only)", ""),
    ("Ontario", "Home schooling: Policy/Program Memorandum 131", "https://www.ontario.ca/document/education-ontario-"
     "policy-and-program-direction/policyprogram-memorandum-131", "King's Printer for Ontario (link-only)", ""),
    ("Quebec", "Quebec Education Program (English)", "https://www.education.gouv.qc.ca/en/teachers/quebec-education-"
     "program/", "Gouvernement du Québec copyright (link-only)", ""),
    ("Quebec", "Homeschooling: process and steps", "https://www.quebec.ca/en/education/preschool-elementary-and-"
     "secondary-schools/programs-training-evaluation/homeschooling/process-steps",
     "Gouvernement du Québec copyright (link-only)", ""),
    ("New Brunswick", "Curriculum, Anglophone sector", "https://curriculum.nbed.ca/", "Crown copyright (link-only)",
     ""),
    ("New Brunswick", "Kindergarten to grade 12 (home schooling application through the district)",
     "https://www.gnb.ca/en/topic/education-training/kindergarten-grade-12.html", "Crown copyright (link-only)", ""),
    ("Nova Scotia", "Curriculum", "https://curriculum.novascotia.ca/", "Crown copyright (link-only)", ""),
    ("Nova Scotia", "Home schooling", "https://www.ednet.ns.ca/homeschooling", "Crown copyright (link-only)", ""),
    ("Prince Edward Island", "Education and child care (curriculum)", "https://www.princeedwardisland.ca/en/topic/"
     "education-and-child-care", f"Crown copyright (link-only; {NO_ANSWER})", ""),
    ("Prince Edward Island", "Home Education Notice of Intent (form)", "https://www.princeedwardisland.ca/sites/"
     "default/files/forms/home_education_-_notice_of_intent.pdf", f"Crown copyright (link-only; {NO_ANSWER})", ""),
    ("Newfoundland and Labrador", "Curriculum", "https://www.gov.nl.ca/education/k12/curriculum/",
     "Crown copyright (link-only)", ""),
    ("Newfoundland and Labrador", "Home schooling", "https://www.gov.nl.ca/education/k12/homeschooling/",
     "Crown copyright (link-only)", ""),
    ("Yukon", "Homeschooling: register (English through Aurora Virtual School)",
     "https://yukon.ca/en/homeschool-distant-register", f"Crown copyright (link-only; {NO_ANSWER})",
     "Yukon follows the BC curriculum, adapted"),
    ("Northwest Territories", "Home schooling", "https://www.ece.gov.nt.ca/en/services/jk-12-school-curriculum/"
     "home-schooling-northwest-territories", f"Crown copyright (link-only; {NO_ANSWER})", ""),
    ("Nunavut", "Curriculum and learning resources", "https://www.gov.nu.ca/en/education-and-schools/curriculum-and-"
     "learning-resources", f"Crown copyright (link-only; {NO_ANSWER}); home schooling is under the Nunavut "
     "Education Act", ""),
    ("Canada (Indigenous education)", "First Nations Education Steering Committee (BC): Learning First Peoples "
     "classroom resources", "https://www.fnesc.ca/learningfirstpeoples/", "Copyright FNESC, free to download "
     "(link-only)", "tworld:alberta_our_words_our_ways, tworld:alberta_successful_practices_fnmi"),
    ("Canada (open textbooks)", "BCcampus open textbooks", "https://open.bccampus.ca/",
     "CC BY mostly (already in the library)", "course:bccampus"),
]
UK_ROWS = [
    ("England", "National curriculum, early years and home education guidance (gov.uk)", "https://www.gov.uk/"
     "home-education", "Open Government Licence v3.0 (built)", "request word tworld-uk"),
    ("England", "Oak National Academy lessons (Curriculum API bulk download)", f"{OAK_API}/",
     "Open Government Licence v3.0 (built: sign-up entry, needs the owner's Oak API key)",
     "request words tworld-oak, tworld-oak-primary, tworld-oak-secondary"),
    ("Scotland", "Curriculum for Excellence (Education Scotland) and home education guidance (gov.scot)",
     ES_EO, "Open Government Licence v3.0 (built)", "request word tworld-uk"),
    ("Wales", "Curriculum for Wales (Hwb)", "https://hwb.gov.wales/curriculum-for-wales/",
     "Hwb's terms: content protected by copyright, no open licence stated (link-only)", ""),
    ("Wales", "Elective home education guidance (gov.wales)", WALES_EHE, "Open Government Licence (built)",
     "tworld:wales_ehe_guidance"),
    ("Northern Ireland", "Northern Ireland Curriculum (CCEA)", "https://ccea.org.uk/learning-resources",
     f"CCEA copyright, no open licence found (link-only; {NO_ANSWER})", ""),
    ("Northern Ireland", "Educating your child at home (nidirect)", "https://www.nidirect.gov.uk/articles/"
     "educating-your-child-home", "Crown copyright (link-only)", ""),
]
IRELAND_ROWS = [
    ("Ireland", "Curriculum Online (NCCA)", "https://www.curriculumonline.ie/",
     f"No open licence found (link-only; {NO_ANSWER})", ""),
    ("Ireland", "NCCA", "https://www.ncca.ie/en/", f"No open licence found (link-only; {NO_ANSWER})", ""),
    ("Ireland", "Scoilnet", "https://www.scoilnet.ie/", f"No open licence found (link-only; {NO_ANSWER})", ""),
    ("Ireland", "Department of Education (gov.ie)", "https://www.gov.ie/en/department-of-education/",
     "gov.ie's robots.txt shuts out AI companies' readers: never read (link-only)", ""),
    ("Ireland", "Home education: Tusla Education Support Service (Alternative Education Assessment and "
     "Registration)", "https://www.tusla.ie/tess/", "Link-only", ""),
]
AUSTRALIA_ROWS = [
    ("Australia", "The Australian Curriculum, Version 9.0 (ACARA)", f"{ACARA}/",
     "CC BY 4.0 (built: the guide pages; the content descriptions are on the website)",
     "tworld:acara_curriculum_guide"),
    ("New South Wales", "Home schooling (NESA)", "https://educationstandards.nsw.edu.au/wps/portal/nesa/regulation/"
     "home-schooling", "NESA copyright (link-only)", ""),
    ("New South Wales", "Teaching and learning (Department of Education)", "https://www.education.nsw.gov.au/"
     "teaching-and-learning", "Mostly CC BY 4.0 per resource: check each resource (link-only, not checked one "
     "by one)", ""),
    ("Victoria", "Home schooling (VRQA)", "https://www.vrqa.vic.gov.au/home-schooling", "Link-only", ""),
    ("Victoria", "Department of Education", "https://www.education.vic.gov.au/", "Link-only", ""),
    ("Queensland", "Home education", "https://education.qld.gov.au/schools-educators/other-education/home-education",
     "Link-only", ""),
    ("Western Australia", "Home educator responsibilities and registration", "https://www.education.wa.edu.au/"
     "home-educator-responsibilities-and-registration", "Link-only", ""),
    ("South Australia", "Home education", "https://www.education.sa.gov.au/parents-and-families/enrol-school-or-"
     "preschool/home-education", f"Link-only ({NO_ANSWER})", ""),
    ("Tasmania", "Tasmanian Home Education Advisory Council (THEAC)", "https://www.theac.tas.gov.au/",
     f"Link-only ({NO_ANSWER})", ""),
    ("Australian Capital Territory", "Home education", "https://www.act.gov.au/education-and-training/find-a-school-"
     "and-enrol/home-education-home-schooling", f"Link-only ({NO_ANSWER})", ""),
    ("Northern Territory", "Home education", "https://education.nt.gov.au/education/home-education",
     f"Link-only ({NO_ANSWER})", ""),
]
NZ_ROWS = [
    ("New Zealand", "The New Zealand Curriculum (Tāhūrangi)", "https://newzealandcurriculum.tahurangi.education."
     "govt.nz/", "A JavaScript application with no readable pages for a program (link-only)", ""),
    ("New Zealand", "Home education (Ministry of Education)", "https://www.education.govt.nz/parents-and-caregivers/"
     "schools-year-0-13/home-education", "CC BY-NC 4.0 NZ (education.govt.nz's copyright page): personal use; "
     "link-only", ""),
]
AFRICA_ASIA_ROWS = [
    ("South Africa", "Curriculum and Assessment Policy Statements (CAPS)", "https://www.education.gov.za/Curriculum/"
     "CurriculumAssessmentPolicyStatements(CAPS).aspx", "Copyright Department of Basic Education (link-only)", ""),
    ("South Africa", "DBE workbooks", "https://www.education.gov.za/Curriculum/LearningandTeachingSupportMaterials"
     "(LTSM)/Workbooks.aspx", "Copyright Department of Basic Education (link-only)", ""),
    ("South Africa", "Siyavula textbooks (grades 7 to 12)", "https://www.siyavula.com/",
     "CC BY (already in the library)", "siyavula"),
    ("Kenya", "Kenya Institute of Curriculum Development", "https://kicd.ac.ke/", "No open licence found (link-only)",
     ""),
    ("Nigeria", "Nigerian Educational Research and Development Council", "https://nerdc.gov.ng/",
     "No open licence found (link-only)", ""),
    ("Ghana", "National Council for Curriculum and Assessment", "https://nacca.gov.gh/",
     f"Link-only ({NO_ANSWER})", ""),
    ("India", "NCERT textbooks", "https://ncert.nic.in/textbook.php", "Copyright NCERT, all rights reserved "
     f"(link-only; {NO_ANSWER})", ""),
    ("Singapore", "Ministry of Education: primary curriculum", "https://www.moe.gov.sg/primary/curriculum",
     "Copyright Government of Singapore (link-only)", ""),
    ("Philippines", "DepEd K to 12 curriculum", "https://www.deped.gov.ph/k-to-12/about/k-to-12-basic-education-"
     "curriculum/", f"Link-only ({NO_ANSWER})", ""),
    ("Jamaica", "Ministry of Education and Youth", "https://moey.gov.jm/", "No open licence found (link-only)", ""),
    ("Caribbean", "Caribbean Examinations Council (CXC) syllabuses", "https://www.cxc.org/",
     f"Copyright CXC (link-only; {NO_ANSWER})", ""),
    ("Africa", "African Storybook and StoryWeaver picture books", "https://www.africanstorybook.org/",
     "CC BY (already in the library)", "readaloud"),
]
NGO_ROWS = [
    ("NGO", "Open Up Resources (EL Education K-8, Bookworms, K-5 Math and others)", "https://www.openupresources.org/",
     "Most CC BY-NC 4.0: personal use (link-only; Open Up HS Math is built)", "k12"),
    ("NGO", "EL Education curriculum", "https://curriculum.eleducation.org/", "CC BY-NC 4.0: personal use (link-only;"
     " not built yet)", ""),
    ("NGO", "Core Knowledge (CKLA, history and geography)", "https://www.coreknowledge.org/",
     "CC BY-NC-SA 4.0: personal use (already in the library)", "personaluse (course:coreknowledge)"),
    ("NGO", "CK-12", "https://www.ck12.org/", "CK-12's own licence: personal use (already, from Kolibri)",
     "course:ck12"),
    ("NGO", "Khan Academy", "https://www.khanacademy.org/", "Personal use only; never read from its site (already, "
     "from Kolibri and Kiwix)", "course:khan"),
    ("NGO", "OER Project and Big History Project", "https://www.oerproject.com/", "CC BY-NC per course (its terms of "
     "use): personal use (link-only; a sign-in site)", ""),
    ("NGO", "Smithsonian Learning Lab", "https://learninglab.si.edu/", "Its robots.txt says ai-train=no and refuses "
     "programs: never read (link-only)", ""),
    ("NGO", "PhET Interactive Simulations: teaching resources", "https://phet.colorado.edu/en/teaching-resources",
     "Simulations CC BY 4.0 (already in the Kiwix library); teacher activities each have their own licence "
     "(link-only)", "Kiwix phet_en_all"),
    ("US federal", "NASA learning resources", "https://www.nasa.gov/learning-resources/",
     "Public domain (US government; already in the library)", "science"),
    ("US federal", "NOAA education", "https://www.noaa.gov/education", "Public domain (US government; already in "
     "the library)", "science"),
    ("US federal", "Peace Corps teaching manuals (teaching English, maths and science, classroom management)",
     "https://www.peacecorps.gov/", "Public domain (US government; already in the library)", "pc-teaching"),
    ("Blind students", "American Printing House (APH): free resources", "https://www.aph.org/",
     "Copyright APH, all rights reserved (link-only)", "vision"),
    ("Blind students", "Paths to Literacy (Perkins and TSBVI)", "https://www.pathstoliteracy.org/",
     "All rights reserved (link-only)", "vision"),
    ("Blind students", "Perkins eLearning", "https://www.perkins.org/elearning/",
     f"Copyright Perkins (link-only; {NO_ANSWER})", "vision"),
]
CLASSIC_ROWS = [
    ("Classics", "Charlotte Mason: Home Education series (volumes 1 to 5)", "https://archive.org/details/"
     "homeeducationser01masouoft", "Public domain (published before 1931): built", "tworld-classics"),
    ("Classics", "McGuffey Eclectic Readers (primer to sixth)", "https://archive.org/details/"
     "mcguffeysfirstec00mcgu_0", "Public domain (published before 1931): built", "tworld-classics"),
    ("Classics", "Ray's Arithmetic", "https://archive.org/details/raysnewpractical0000jose",
     "Public domain (published before 1931): built", "tworld-classics"),
    ("Classics", "Montessori: own handbook, Advanced Method, elementary material", "https://archive.org/details/"
     "drmontessorisown01mont", "Public domain (published before 1931): built", "tworld-classics"),
    ("Classics", "The Montessori Method (1912), Dewey, William James", "https://archive.org/details/"
     "democracyeducati1916dewe", "Public domain (already in the library)", "education-more"),
]

INDEX_SECTIONS = [
    ("Canada", "Every province and territory: its curriculum, its home-schooling rules and the licence of its "
     "documents. Education is provincial in Canada; most provinces keep Crown copyright, so their documents are "
     "links. Alberta publishes many under an open licence, and those are built.", CANADA_ROWS),
    ("United Kingdom", "England, Scotland, Wales and Northern Ireland: curricula, Oak National Academy's lessons and "
     "home education guidance.", UK_ROWS),
    ("Ireland", "Ireland's curriculum and home education.", IRELAND_ROWS),
    ("Australia", "The national curriculum (ACARA) and each state's and territory's home education rules.",
     AUSTRALIA_ROWS),
    ("New Zealand", "The national curriculum and home education.", NZ_ROWS),
    ("Africa, Asia and the Caribbean", "Other English-speaking countries. Only clearly open licences are built.",
     AFRICA_ASIA_ROWS),
    ("Organisations (NGOs), US federal and blind students", "Open curricula of non-profit organisations, US federal "
     "education resources and teaching resources for blind students.", NGO_ROWS),
    ("Homeschooling classics", "Old books popular with homeschoolers, all published before 1931.", CLASSIC_ROWS),
]


def index_book(name, work, cache=None, left_out=None, limit=None):
    """tworld:index: one page per region (INDEX_SECTIONS), each a table, plus a page of what was not built."""
    import build_textbooks as B
    book = K.new_book(f"{PREFIX}_index", "Teaching and homeschooling around the world: a guide (Canada, UK, Ireland, "
                      "Australia, New Zealand, other countries, NGOs and classics)", "Teaching and homeschooling",
                      GROUP, "Digital Accessibility Toolkit (an index of the library)", X.CC0_INDEX, K.CC0_URL,
                      X.TOOLKIT_REPO, "A guide to curricula, home-schooling rules and open teaching resources outside "
                      "the United States: a table for every Canadian province and territory, the UK nations, "
                      "Ireland, the Australian states, New Zealand, other English-speaking countries, organisations "
                      "and the old homeschooling classics, saying what the library has and what is a link only.",
                      "Facts and links only (CC0). Each book listed has its own licence, shown in that book; each "
                      "link-only source belongs to its publisher. " + CURRENT_NOTE, country="International",
                      changes="an index written for the toolkit")
    head = ("Place", "What", "Address", "Licence and status", "In the library")
    for number, (part, intro, rows) in enumerate(INDEX_SECTIONS, 1):
        if limit and len(book.pages) >= limit:
            break
        body = f"<p>{B.esc(intro)}</p>" + K.rows_table(rows, head)
        book.pages.append(B.Page(f"part-{number}-{B.slug(part, 40)}", part, body, number, ""))
    if not (limit and len(book.pages) >= limit):
        rows = [(title, reason) for title, reason in NOT_INCLUDED]
        book.pages.append(B.Page("not-built", "Looked at and not built", "<p>Each with the reason.</p>" +
                                 K.rows_table(rows, ("Source", "Why not built")), len(book.pages) + 1, ""))
    book.published = CHECKED
    return book


def index_sign(name):
    """The weekly sign of the index: a fingerprint of its tables."""
    return K.sha(INDEX_SECTIONS, NOT_INCLUDED)


# ====================================================================== the collection

PDFS = ALBERTA_PDFS + UK_PDFS + CLASSICS
GUIDES = UK_GUIDES
MAKERS = {"index": (index_book, index_sign), "oak": (oak_book, oak_sign), "acara_curriculum_guide":
          (acara_book, acara_sign)}
PIECES = {"oak": oak_pieces}


def _keys(entries):
    """The keys of some entries."""
    return [f"{PREFIX}:{e['name']}" for e in entries]


def _oak(phase=None):
    """The Oak keys (of one phase, or all)."""
    return [f"{PREFIX}:oak:{p}" for p in oak_pieces() if phase is None or p.endswith("-" + phase)]


WORDS = {
    "tworld-canada": lambda: [f"{PREFIX}:index"] + _keys(ALBERTA_PDFS),
    "tworld-uk": lambda: [f"{PREFIX}:index"] + _keys(UK_PDFS + UK_GUIDES),
    "tworld-oak": lambda: _oak(),
    "tworld-oak-primary": lambda: _oak("primary"),
    "tworld-oak-secondary": lambda: _oak("secondary"),
    "tworld-ireland": lambda: [f"{PREFIX}:index"],
    "tworld-australia": lambda: [f"{PREFIX}:index", f"{PREFIX}:acara_curriculum_guide"],
    "tworld-nz": lambda: [f"{PREFIX}:index"],
    "tworld-africa-asia": lambda: [f"{PREFIX}:index"],
    "tworld-ngo": lambda: [f"{PREFIX}:index"],
    "tworld-classics": lambda: [f"{PREFIX}:index"] + _keys(CLASSICS),
}
WORDS["teach-world"] = lambda: list(dict.fromkeys(k for w, f in WORDS.items() if w != "teach-world" for k in f()))
COLLECTION = K.Collection(PREFIX, GROUP, words=WORDS, guides=GUIDES, pdfs=PDFS, makers=MAKERS, pieces=PIECES)

LICENCE_LINES = {
    "tworld_index": "The teaching and homeschooling index (tworld:index) is the toolkit's own facts and links, CC0.",
    "tworld_alberta": "open.alberta.ca publication pages: \"Licence Open Government Licence - Alberta\", read on each "
                      "page at every build (checked 2026-11-23). open.alberta.ca's robots.txt closes /api/; only the "
                      "publication pages and their files are read.",
    "tworld_uk": "gov.uk and gov.scot publication pages: \"All content is available under the Open Government "
                 "Licence v3.0, except where otherwise stated\", read on each page at every build; gov.wales's "
                 "copyright statement and Education Scotland's terms of use name the Open Government Licence "
                 "(checked 2026-11-23).",
    "tworld_oak": "Oak Curriculum API (open-api.thenational.academy): its API limits page says the lesson content "
                  "\"is licensed on the Open Government Licence (OGL) v3.0, except where otherwise stated\" (read at "
                  "every build); its robots.txt says ai-train=yes and allows all. A sign-up entry: the owner's free "
                  "API key is read from OAK_API_KEY at build time, never stored. Lessons marked restricted lose "
                  "their transcripts. Oak's main site (www.thenational.academy) says ai-train=no and is never read.",
    "tworld_acara": "ACARA's copyright and terms of use page: \"licensed under a Creative Commons Attribution 4.0 "
                    "International (CC BY) licence\" (read at every build); logos and trade marks excluded. Its "
                    "robots.txt allows the pages read (it closes PDFs and /download, which are not read).",
    "tworld_classics": "Internet Archive items: each item's metadata date before 1931 (checked at every build). "
                       "Charlotte Mason's books were published in London; all are public domain in the US as published "
                       "before 1931.",
}

NOT_INCLUDED = [
    ("Provincial curricula of British Columbia, Saskatchewan, Manitoba, Quebec, New Brunswick, Nova Scotia, Prince "
     "Edward Island, Newfoundland and Labrador and the territories", "Crown copyright without an open licence (BC's "
     "copyright page: all rights reserved); listed with their addresses in tworld:index. Index: "
     "https://curriculum.gov.bc.ca/"),
    ("Ontario curriculum documents", "King's Printer for Ontario: copies only for non-commercial use without changes; "
     "not repackaged. Index: https://www.dcp.edu.gov.on.ca/en/"),
    ("Alberta programs of study (new.learnalberta.ca)", "Not on Alberta's open-licence site; LearnAlberta's own terms. "
     "Index: https://curriculum.learnalberta.ca/"),
    ("Curriculum for Wales (Hwb)", "Hwb's terms say its content is protected by copyright and name no open licence. "
     "Index: https://hwb.gov.wales/curriculum-for-wales/"),
    ("Northern Ireland Curriculum (CCEA)", "CCEA's site refuses the build machine's reader (403) and no open licence "
     "was found. Index: https://ccea.org.uk/learning-resources"),
    ("Ireland: NCCA, Curriculum Online, Scoilnet, gov.ie", "No open licence found; their sites refuse programs (403) "
     "and gov.ie's robots.txt shuts out AI companies' readers. Index: https://www.curriculumonline.ie/"),
    ("The Australian Curriculum content descriptions and PDFs", "ACARA's robots.txt closes its PDFs and downloads; "
     "the year-by-year content pages are an interactive application. The guide pages are built "
     "(tworld:acara_curriculum_guide). Index: https://www.australiancurriculum.edu.au/f-10-curriculum"),
    ("Australian state syllabuses and home education guides (NESA, VCAA, QCAA, SCSA, SA, Tasmania, ACT, NT)",
     "Each has its own copyright or terms, several refuse programs (403); not checked one by one. Listed in "
     "tworld:index. Index: https://educationstandards.nsw.edu.au/"),
    ("The New Zealand Curriculum (Tāhūrangi) and TKI", "Tāhūrangi is a JavaScript application with no pages a "
     "program can read; education.govt.nz is CC BY-NC 4.0 NZ (personal use) and was not built. Index: "
     "https://newzealandcurriculum.tahurangi.education.govt.nz/"),
    ("South Africa: DBE CAPS documents and workbooks", "Copyright Department of Basic Education; no open licence "
     "found. Siyavula's open books are already built (siyavula). Index: https://www.education.gov.za/"),
    ("Kenya (KICD), Nigeria (NERDC), Ghana (NaCCA), India (NCERT), Singapore, Philippines (DepEd), Jamaica, CXC",
     "No clear open licence found (NCERT: all rights reserved); several refuse programs or did not answer. Index: "
     "https://kicd.ac.ke/"),
    ("Open Up Resources ELA and K-5 curricula, EL Education", "Mostly CC BY-NC 4.0 (personal use) and each in its own "
     "web application; not built yet. Index: https://curriculum.eleducation.org/"),
    ("OER Project and Big History Project", "CC BY-NC per course (personal use) behind a sign-in. Index: "
     "https://www.oerproject.com/"),
    ("Smithsonian Learning Lab", "Its robots.txt says ai-train=no and refuses programs. Index: "
     "https://learninglab.si.edu/"),
    ("PhET teacher activities", "Each activity has its own author and licence; the simulations are already in the "
     "Kiwix library. Index: https://phet.colorado.edu/en/teaching-resources"),
    ("APH free resources, Paths to Literacy, Perkins eLearning", "All rights reserved by each organisation; listed "
     "as links (vision_living.py has them too). Index: https://www.pathstoliteracy.org/"),
    ("A Philosophy of Education (Charlotte Mason, Home Education Series volume 6, 1925)", "Public domain in the US, "
     "but the Internet Archive's copy (AnEssayTowardsAPhilosophyOfEducation) has no PDF, and the other copies are "
     "lending-only reprints. Index: https://archive.org/details/AnEssayTowardsAPhilosophyOfEducation"),
    ("Ray's New Test Examples in Arithmetic (1883)", "Public domain, but the Internet Archive copies found "
     "(raysnewtestexam00beckgoog, raysnewtestexam01beckgoog, raysnewtestexamp00rayjrich) are scans without a usable "
     "text layer or a year the builder can read. Index: https://archive.org/details/raysnewtestexam00beckgoog"),
    ("Oak National Academy's website (www.thenational.academy)", "Its robots.txt says ai-train=no: never read. Oak's "
     "lessons come only from its API bulk download (tworld-oak). Index: https://www.thenational.academy/"),
    ("Oak National Academy French, German and Spanish", "Language learning belongs to the language collections. "
     "Index: https://open-api.thenational.academy/bulk-download"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
