"""Language learning for the reference library, in the group "Languages" (the owner's request of 2026-11-22). Keys:
languages (every book), lang:<name>; the courses are lang:fsi:<course>, the sentence books lang:tatoeba:<language
code>.

"Languages" is a top-level section of the library (the owner's request of 23 November 2026: "Make a new top level
section for languages"). Its group key stays "languages" (so no key or request word changed); it was called
"Reference, language learning" before. The other language modules put their books in the same group (GROUP):
languages_gov.py (government courses and phrase guides, lgov:), languages_open.py (open resources, lopen:) and
peace_corps_languages.py (Peace Corps courses, pclang:); the guide to the whole section, lang:index, is made by
languages_index.py.

What this module builds, in plain words:
  - the Foreign Service Institute's language courses (US government works, public domain), the languages the owner
    is most likely to meet in the US first: Spanish (the Basic Course and the FAST course), French, German, Italian,
    Brazilian Portuguese, Mandarin Chinese, Cantonese, Japanese, Korean, Russian, Arabic (Saudi Urban Hijazi),
    Vietnamese, Hebrew and Greek, and the Peace Corps's Tagalog course. Each course's TEXT is the book (every volume
    whose PDF has a text layer, read from the Internet Archive's copy, or from fsi-languages.yojik.eu where the
    Archive has none; both allow programs). Its AUDIO is not downloaded: every recording is listed in the book's
    "originals" (address, size, licence, may_download) for the owner to download himself;
  - Wikivoyage's phrasebooks for the same languages (CC BY-SA 4.0: share-alike, kept apart as its own book);
  - Tatoeba's sentences with their English translations (CC BY 2.0 FR), one book per language, shortest sentences
    first, each sentence with its Tatoeba number (its credit).

Already in the library and not repeated: NIDCD's American Sign Language page (dir:nidcd_health), the sign language
picture packs (packs/sign_language_packs.py), Wikivoyage whole and Wiktionary in the Kiwix library.

Not built (NOT_INCLUDED): the State Department's American English site and USCIS's English learning pages (both
refuse programs), the Haitian Creole course of the Defense Language Institute (drawn from Albert Valdman's
copyrighted course; Wikivoyage's and Tatoeba's Haitian Creole are built), "Ann pale kreyol" (Indiana University,
copyright), the Defense Language Institute's large scanned courses (no text layer), and the FSI audio files
themselves (listed as originals, not downloaded: several gigabytes).

Licences: FSI, DLI and Peace Corps courses are works of the US government (17 U.S.C. 105, the line checked on
govinfo.gov's policies page at every build); Wikivoyage's licence line is checked on its copyleft page and Tatoeba's
on its downloads page at every build.

Run from the repository's folder:
  python3 textbooks/languages.py lang:fsi:japanese --out build/textbooks --limit 5
  python3 textbooks/languages.py --list languages
"""

import bz2
import datetime
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "languages"
GROUPS = {GROUP: "Languages"}     # a top-level section (23 November 2026); the key "languages" is unchanged

IA = "https://archive.org"
YOJIK = "https://fsi-languages.yojik.eu/languages"
FSI = "Foreign Service Institute, US Department of State"
FSI_NOTICE = ("A course of the Foreign Service Institute (US Department of State), a work of the US government "
              "(public domain). Old courses: some dialogues, prices and customs are out of date, and the scanned "
              "text has the scanner's mistakes; foreign scripts may be partly missing from the text layer. Its audio "
              "recordings are listed as originals for you to download; they are not inside this book.")

# Each course: key, language, title, the year of the course, where its text PDFs are (("ia", item, file pattern)
# or ("page", yojik page, link pattern)), where its audio is (("ia", item) or ("page", yojik page)), description.
COURSES = [
    dict(key="spanish", language="Spanish", title="FSI Spanish Basic Course", year="1961",
         text=[("ia", "Fsi-SpanishBasicCourse-StudentText", r"StudentText\.pdf$")],
         audio=[("ia", "Fsi-SpanishBasicCourse-Volume1"), ("ia", "FSISpanishBasicCourseVolume2Unit18B"),
                ("ia", "FSISpanishBasicCourseVolume3Unit37A"),
                ("ia", "4601FSISpanishBasicCourseVolume4Unit4646.1BasicSentences")],
         description="The FSI's full Latin American Spanish course in four volumes (units 1 to 55): dialogues, "
                     "pronunciation, grammar drills and conversations."),
    dict(key="spanish_fast", language="Spanish", title="FSI Spanish FAST Course (Familiarization and Short-Term "
         "Training)", year="", text=[("ia", "Fsi-SpanishFastCourse-StudentText", r"\.pdf$")],
         audio=[("ia", "fsi-spanish-fast-audio-tapes")],
         description="The FSI's short Spanish course for everyday survival: greetings, getting around, shopping, "
                     "eating out, the hotel and emergencies."),
    dict(key="french", language="French", title="FSI French Basic Course (Revised)", year="",
         text=[("ia", "Fsi-FrenchBasicCourserevised-StudentText", r"StudentText\.pdf$")],
         audio=[("ia", "Fsi-FrenchBasicCourserevised-Volume1"), ("ia", "FSIFrenchBasicCourseRevisedVolume2Unit1313.02"),
                ("ia", "FSIFrenchBasicCourseRevisedVolume2Unit1919.7")],
         description="The FSI's French course in two volumes: dialogues, pronunciation, grammar and drills."),
    dict(key="german", language="German", title="FSI German Basic Course", year="1961",
         text=[("ia", "Fsi-GermanBasicCourse-StudentText", r"StudentText\.pdf$")],
         audio=[("ia", "FSIGermanBasicCourseVolume1Unit022.2"), ("ia", "FSIGermanBasicCourseVolume2Unit2121.1")],
         description="The FSI's German course in two volumes: basic sentences, pronunciation, grammar and drills."),
    dict(key="italian", language="Italian", title="FSI Italian Programmed Course", year="",
         text=[("ia", "Fsi-ItalianProgrammedCourse-Text", r"StudentText(_text)?\.pdf$")], audio=[],
         description="The FSI's programmed (self-paced) Italian course: pronunciation, grammar and exercises. Its "
                     "tapes are not on the Internet Archive with the text; the Archive's Italian FAST audio is a "
                     "different course."),
    dict(key="portuguese", language="Portuguese (Brazilian)", title="FSI Brazilian Portuguese FAST Course",
         year="", text=[("page", f"{YOJIK}/FSI/fsi-brazilian-portuguese-fast.html", r"FAST - Volume \d+\.pdf$")],
         audio=[("page", f"{YOJIK}/FSI/fsi-brazilian-portuguese-fast.html")],
         description="The FSI's short Brazilian Portuguese course for everyday survival: greetings, getting "
                     "around, shopping, eating and the hotel."),
    dict(key="chinese", language="Chinese (Mandarin)", title="FSI Standard Chinese: A Modular Approach", year="",
         text=[("ia", "FSI-StandardChinese-StudentTexts", r"StudentText(AndWorkbook)?(_text)?\.pdf$")],
         audio=[("ia", "FSIStandardChinese")],
         description="The FSI's Mandarin Chinese course in modules: orientation, biographic information, money, "
                     "directions, transportation, meeting people, society and travel, with the resource module. "
                     "Modules whose PDFs are scans without words are left out (said in the book's record)."),
    dict(key="cantonese", language="Chinese (Cantonese)", title="FSI Cantonese Basic Course", year="",
         text=[("ia", "Fsi-CantoneseBasicCourse-StudentText", r"StudentText(_text)?\.pdf$")], audio=[],
         description="The FSI's Cantonese course in two volumes, in romanised Cantonese."),
    dict(key="japanese", language="Japanese", title="FSI Japanese FAST Course", year="1988",
         text=[("ia", "Fsi-JapaneseFast-StudentText", r"\.pdf$")], audio=[],
         description="The FSI's short Japanese course for everyday survival, in romanised Japanese."),
    dict(key="korean", language="Korean", title="FSI Korean Basic Course", year="",
         text=[("ia", "Fsi-KoreanBasicCourse-StudentText", r"StudentText(_text)?\.pdf$")],
         audio=[("ia", "FSIKoreanBasicCourseVolume1Unit02"), ("ia", "FSIKoreanBasicCourseVolume2Unit30")],
         description="The FSI's Korean course in two volumes: dialogues, pronunciation, grammar and drills."),
    dict(key="russian", language="Russian", title="FSI Russian FAST Course", year="",
         text=[("ia", "Fsi-RussianFastCourse-StudentText", r"_text\.pdf$")], audio=[("ia", "FSIRussianFAST")],
         description="The FSI's short Russian course (lessons 1 to 11) for everyday survival."),
    dict(key="arabic", language="Arabic (Saudi, Urban Hijazi)", title="FSI Saudi Arabic Basic Course (Urban "
         "Hijazi Dialect)", year="", text=[("ia", "Fsi-SaudiArabicBasicCourse-UrbanHijaziDialect-StudentText",
                                            r"_text\.pdf$")],
         audio=[("ia", "FSISaudiArabicBasicCourseUrbanHijaziDialect_201701")],
         description="The FSI's course in the spoken Arabic of the cities of western Saudi Arabia, in romanised "
                     "Arabic."),
    dict(key="vietnamese", language="Vietnamese", title="FSI Vietnamese Basic Course", year="1967",
         text=[("ia", "FSIVietnameseBasicCourseVolume1StudentText_201606", r"Student Text_text\.pdf$")],
         audio=[("ia", "FSIVietnameseBasicCourseVolume1PronunciationTape1")],
         description="The FSI's Vietnamese course in two volumes: pronunciation, dialogues, grammar and drills."),
    dict(key="hebrew", language="Hebrew", title="FSI Hebrew Basic Course", year="",
         text=[("ia", "Fsi-HebrewBasicCourse-StudentText", r"_text\.pdf$")], audio=[("ia", "FSIHebrewBasicCourseUnit14")],
         description="The FSI's modern Hebrew course: dialogues, pronunciation, grammar and drills."),
    dict(key="greek", language="Greek", title="FSI Greek Basic Course", year="",
         text=[("ia", "Fsi-GreekBasicCourse-StudentText", r"StudentText\.pdf$")],
         audio=[("ia", "FSIGreekBasicCourseVolume1Unit25"), ("ia", "FSIGreekBasicCourseVolume2Unit33"),
                ("ia", "FSIGreekBasicCourseVolume3Unit52")],
         description="The FSI's modern Greek course in three volumes."),
    dict(key="tagalog", language="Tagalog (Filipino)", title="Peace Corps Tagalog Language Correspondence Course "
         "(Modules 1 to 21)", year="1994", publisher="US Peace Corps",
         text=[("ia", "ERIC_ED402754", r"_text\.pdf$")], audio=[],
         description="The Peace Corps's self-study Tagalog course for volunteers in the Philippines: 21 modules of "
                     "phrases, dialogues, vocabulary, grammar notes, exercises, culture notes and answer keys."),
]
COURSE = {c["key"]: c for c in COURSES}


def ia_files(item, cache=None):
    """The files of an Internet Archive item (its metadata's "files" list)."""
    import build_textbooks as B
    return json.loads(B.fetch(f"{IA}/metadata/{item}", cache)).get("files", [])


def pick_pdfs(files, pattern):
    """The PDFs of an item's files to read, in name order: those whose name matches pattern, one per volume (the
    "Text PDF" first, then the "Additional Text PDF" with the words, then any other)."""
    rank = {"Text PDF": 0, "Additional Text PDF": 1}
    best = {}
    for f in files:
        name = f.get("name", "")
        if not name.lower().endswith(".pdf") or not re.search(pattern, name):
            continue
        base = re.sub(r"_text\.pdf$", ".pdf", name)
        if base not in best or rank.get(f.get("format"), 2) < rank.get(best[base].get("format"), 2):
            best[base] = f
    return [best[b]["name"] for b in sorted(best)]


def part_title(file_name):
    """A volume's title from its file name ("Fsi-SpanishBasicCourse-Volume2-StudentText.pdf" -> "Volume 2")."""
    base = re.sub(r"(_text)?\.pdf$", "", file_name.rsplit("/", 1)[-1])
    m = re.search(r"Volume\s*-?\s*(\d+)", base, re.I) or re.search(r"Module\s*0*(\d+)\s*([A-Z]{3})?", base)
    if m and m.re.pattern.startswith("Module"):
        return f"Module {m.group(1)}" + (f" ({m.group(2)})" if m.group(2) else "")
    if m:
        return f"Volume {m.group(1)}"
    return " ".join(re.sub(r"[-_]+", " ", base).split())


def page_links(page, pattern, cache=None):
    """[absolute address] of the links on a page whose address matches pattern, in page order, without repeats."""
    import build_textbooks as B
    import html as _html
    text = B.fetch(page, cache)
    links = [urllib.parse.urljoin(page, _html.unescape(h)) for h in re.findall(r'href="([^"]+)"', text)]
    links = [urllib.parse.quote(urllib.parse.unquote(u), safe=":/?&=#~+") for u in links]   # spaces as %20
    return list(dict.fromkeys(u for u in links if re.search(pattern, urllib.parse.unquote(u))))


def course_parts(course, cache=None):
    """[(part title, PDF address, page address)] of a course's text PDFs."""
    parts = []
    for kind, where, pattern in course["text"]:
        if kind == "ia":
            for name in pick_pdfs(ia_files(where, cache), pattern):
                parts.append((part_title(name), f"{IA}/download/{where}/{urllib.parse.quote(name)}",
                              f"{IA}/details/{where}"))
        else:
            for url in page_links(where, pattern, cache):
                parts.append((part_title(urllib.parse.unquote(url)), url, where))
    return parts


def course_audio(course, cache=None, sizes=True):
    """[{url, kind, size}] of a course's recordings (originals, never downloaded here): an Internet Archive item's
    original MP3 files with the sizes its metadata gives, or the MP3 links of a course page with the size its server
    gives (sizes=False: no size asked, for a small test build)."""
    import updates
    out = []
    for kind, where in course["audio"]:
        if kind == "ia":
            for f in ia_files(where, cache):
                if f.get("name", "").lower().endswith(".mp3") and f.get("source", "original") == "original":
                    out.append({"url": f"{IA}/download/{where}/{urllib.parse.quote(f['name'])}", "kind": "mp3",
                                "size": int(f.get("size") or 0)})
        else:
            for url in page_links(where, r"\.mp3$", cache):
                size = 0
                if sizes:
                    head = updates.head_signs(url).split("|")
                    size = int(head[-1]) if head and head[-1].isdigit() else 0
                out.append({"url": url, "kind": "mp3", "size": size})
    return out


def course_entry(course):
    """The PDF_DOCS-like entry of a course (refs_kit.us_pdf), for build_textbooks.pdfdoc_book."""
    where = course["text"][0]
    source = f"{IA}/details/{where[1]}" if where[0] == "ia" else where[1]
    audio = (" Its recordings are listed as originals (" + ", ".join(a[1] for a in course["audio"]) + ")."
             if course["audio"] else " Its recordings were not found with the text, so none are listed.")
    return K.us_pdf(GROUP, name=f"lang_fsi_{course['key']}", title=f"{course['title']} ({course['language']})",
                    subject=f"Language learning: {course['language']}", publisher=course.get("publisher", FSI),
                    source=source, description=course["description"] + audio,
                    notice=FSI_NOTICE.replace("of the Foreign Service Institute (US Department of State)",
                                              f"of the {course.get('publisher', FSI)}"),
                    published=course["year"], level="course")


def fsi_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one course ("fsi:<key>"): its text volumes read with pdf_set.pdf_set_book, its recordings added
    to its originals."""
    import pdf_set
    course = COURSE.get(name.split(":", 1)[1] if ":" in name else "")
    if course is None:
        left_out.append({"title": name, "reason": "Unknown course."})
        return None
    parts = course_parts(course, cache)
    if not parts:
        left_out.append({"title": course["title"], "reason": "No text PDF of the course was found."})
        return None
    book = pdf_set.pdf_set_book(course_entry(course), parts, work, cache, left_out, limit)
    if book is None:
        return None
    book.originals += course_audio(course, cache, sizes=not limit)
    items = sorted({p[2] for p in parts})
    book.version = f"read from {', '.join(items)} on {datetime.date.today().isoformat()}"
    return book


def fsi_sign(name):
    """A course's sign of change: the names, sizes and checksums of its Internet Archive files, or its course
    page's links."""
    course = COURSE[name.split(":", 1)[1]]
    signs = []
    for kind, where, pattern in course["text"]:
        if kind == "ia":
            signs += sorted((f.get("name"), f.get("md5")) for f in ia_files(where) if re.search(pattern, f["name"]))
        else:
            signs += page_links(where, pattern)
    return K.sha(signs)


# ====================================================================== Wikivoyage phrasebooks (CC BY-SA 4.0)

WIKIVOYAGE = "https://en.wikivoyage.org/wiki"
PHRASEBOOKS = ["Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Cantonese", "Japanese", "Korean",
               "Russian", "Arabic", "Vietnamese", "Tagalog", "Haitian_Creole", "Hebrew", "Greek"]
PHRASEBOOK_URLS = [f"{WIKIVOYAGE}/{p}_phrasebook" for p in PHRASEBOOKS]
GUIDES = [
    dict(group=GROUP, country="International", licence="CC BY-SA 4.0",
         licence_url="https://creativecommons.org/licenses/by-sa/4.0/", publisher="Wikivoyage contributors "
         "(en.wikivoyage.org)", name="wikivoyage_phrasebooks",
         title="Phrasebooks for travellers: Spanish, French, Chinese, Vietnamese, Tagalog, Haitian Creole and more "
               "(Wikivoyage)", subject="Language learning: phrasebooks", source=PHRASEBOOK_URLS[0],
         description="Wikivoyage's phrasebooks for " + ", ".join(p.replace("_", " ") for p in PHRASEBOOKS) +
                     ": each one's pronunciation guide, then the phrases travellers need (basics, problems, numbers, "
                     "time, money, transport, eating, the hotel, shopping, the police and emergencies), each with "
                     "how to say it.",
         notice="From Wikivoyage (en.wikivoyage.org), written by its contributors, CC BY-SA 4.0 (share-alike: "
                "anything made from it keeps the same licence); each page's history lists its authors.",
         licence_page=f"{WIKIVOYAGE}/Wikivoyage:Copyleft", licence_text=r"Creative Commons Attribution-ShareAlike",
         page_mark=r"Creative Commons Attribution-ShareAlike", sitemap="", unit_rules=[], level="reference",
         start=[], units="", crawl=[(PHRASEBOOK_URLS[0], 0)], urls=PHRASEBOOK_URLS,
         pages=r"^https://en\.wikivoyage\.org/wiki/[A-Za-z_]+_phrasebook$",
         content=(r'<div id="mw-content-text"[^>]*>', r'<div class="printfooter"'),
         drop=[r'<span class="mw-editsection">.*?</span>\s*</span>', r'<div class="(?:navbox|noprint)[^"]*".*?</div>',
               r'<table class="[^"]*(?:ambox|metadata|navbox)[^"]*".*?</table>'], limit=len(PHRASEBOOKS) + 2,
         changes="each phrasebook made into a web page, with the site's menus, edit links and notices left out"),
]

# ====================================================================== Tatoeba sentences (CC BY 2.0 FR)

TATOEBA = "https://downloads.tatoeba.org/exports/per_language"
TATOEBA_TERMS = "https://tatoeba.org/en/downloads"
TATOEBA_TEXT = r"These files are released under CC BY 2\.0 FR"
# The languages (Tatoeba's ISO 639-3 codes) and their names.
TATOEBA_LANGUAGES = {"spa": "Spanish", "fra": "French", "deu": "German", "ita": "Italian", "por": "Portuguese",
                     "cmn": "Chinese (Mandarin)", "yue": "Chinese (Cantonese)", "jpn": "Japanese", "kor": "Korean",
                     "rus": "Russian", "ara": "Arabic", "vie": "Vietnamese", "tgl": "Tagalog", "hat": "Haitian Creole",
                     "heb": "Hebrew", "ell": "Greek"}
PAIRS_PER_PAGE = 250
MOST_PAIRS = 20000                 # the shortest sentences first: a learner's book, not the whole corpus


def tatoeba_sentences(path, wanted=None):
    """{sentence number: text} of a Tatoeba sentences file (bz2: number, language, text per line); wanted: only
    these numbers (the English file has millions of sentences, so only the ones needed are kept in memory)."""
    out = {}
    with bz2.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3 and (wanted is None or parts[0] in wanted):
                out[parts[0]] = parts[2]
    return out


def tatoeba_links(links_path, foreign):
    """{foreign number: English number} from a links file (bz2: foreign number, English number per line): each
    foreign sentence of foreign with its first English translation."""
    out = {}
    with bz2.open(links_path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and parts[0] in foreign and parts[0] not in out:
                out[parts[0]] = parts[1]
    return out


def tatoeba_pairs(links, foreign, english, most=MOST_PAIRS):
    """[(foreign number, foreign text, English number, English text)], shortest foreign sentence first, at most
    most of them (links from tatoeba_links; a translation missing from english is left out)."""
    pairs = [(f, foreign[f], e, english[e]) for f, e in links.items() if f in foreign and e in english]
    pairs.sort(key=lambda p: (len(p[1]), p[1]))
    return pairs[:most]


def tatoeba_pages(code, pairs, limit=None):
    """[(path, title, body HTML)] of the pairs, PAIRS_PER_PAGE to a page."""
    import build_textbooks as B
    out = []
    for start in range(0, len(pairs), PAIRS_PER_PAGE):
        if limit and len(out) >= limit:
            break
        chunk = pairs[start:start + PAIRS_PER_PAGE]
        rows = "".join(f"<tr><td lang=\"{code}\">{B.esc(f)}</td><td>{B.esc(e)}</td><td>{fn}, {en}</td></tr>"
                       for fn, f, en, e in chunk)
        body = (f"<table><tr><th>{B.esc(TATOEBA_LANGUAGES[code])}</th><th>English</th><th>Tatoeba sentence numbers"
                f"</th></tr>{rows}</table>")
        out.append((f"sentences-{start + 1}", f"Sentences {start + 1} to {start + len(chunk)}", body))
    return out


def tatoeba_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one language's sentences ("tatoeba:<code>"): the licence line checked, Tatoeba's per-language
    files streamed to the cache folder."""
    import build_textbooks as B
    code = name.split(":", 1)[1] if ":" in name else ""
    if code not in TATOEBA_LANGUAGES:
        left_out.append({"title": name, "reason": "Unknown language."})
        return None
    words = " ".join(re.sub(r"<[^>]+>", " ", B.fetch(TATOEBA_TERMS, cache)).split())
    if not re.search(TATOEBA_TEXT, words):
        left_out.append({"title": name, "reason": "Tatoeba's downloads page no longer says CC BY 2.0 FR."})
        return None
    urls = {"links": f"{TATOEBA}/{code}/{code}-eng_links.tsv.bz2", "foreign": f"{TATOEBA}/{code}/{code}_sentences.tsv.bz2",
            "english": f"{TATOEBA}/eng/eng_sentences.tsv.bz2"}
    paths = {k: K.download_file(u, cache, name=u.rsplit("/", 1)[-1], max_age_days=6) for k, u in urls.items()}
    foreign = tatoeba_sentences(paths["foreign"])
    links = tatoeba_links(paths["links"], foreign)
    pairs = tatoeba_pairs(links, foreign, tatoeba_sentences(paths["english"], set(links.values())))
    if not pairs:
        left_out.append({"title": name, "reason": "Tatoeba has no sentences of this language with an English "
                         "translation."})
        return None
    language = TATOEBA_LANGUAGES[code]
    book = K.new_book(f"lang_tatoeba_{code}", f"{language} sentences with English translations (Tatoeba)",
                      f"Language learning: {language}", GROUP, "Tatoeba contributors (tatoeba.org)", "CC BY 2.0 FR",
                      "https://creativecommons.org/licenses/by/2.0/fr/deed.en", TATOEBA_TERMS,
                      f"Up to {MOST_PAIRS:,} {language} sentences from Tatoeba, each with an English translation, "
                      f"the shortest first, {PAIRS_PER_PAGE} to a page: everyday sentences to read, hear with a "
                      f"screen reader's {language} voice, and learn from.",
                      "Sentences and translations by Tatoeba's contributors (tatoeba.org), CC BY 2.0 FR (some also "
                      "CC0); each sentence's Tatoeba number is given, and tatoeba.org/sentences/show/<number> shows "
                      "its page and author. Volunteers wrote them: some may have mistakes.",
                      country="International", level="reference",
                      changes="each sentence paired with its first English translation, sorted shortest first and "
                              "made into tables; no sentence changed")
    book.version = f"Tatoeba exports of {datetime.date.today().isoformat()}"
    book.originals += [{"url": u, "kind": "tsv.bz2", "size": os.path.getsize(paths[k])} for k, u in urls.items()]
    for path, title, body in tatoeba_pages(code, pairs, limit):
        book.pages.append(B.Page(path, title, body, 0, f"{language} and English"))
    return book


def tatoeba_sign(name):
    """A language's sign of change: the server's date and size of its sentence and link files."""
    import updates
    code = name.split(":", 1)[1]
    return K.sha(updates.head_signs(f"{TATOEBA}/{code}/{code}-eng_links.tsv.bz2"),
                 updates.head_signs(f"{TATOEBA}/{code}/{code}_sentences.tsv.bz2"))


# ====================================================================== the collection

COLLECTION = K.Collection(
    "lang", GROUP, guides=GUIDES,
    makers={"fsi": (fsi_book, fsi_sign), "tatoeba": (tatoeba_book, tatoeba_sign)},
    pieces={"fsi": lambda: [c["key"] for c in COURSES], "tatoeba": lambda: list(TATOEBA_LANGUAGES)},
    words={"languages": lambda: [f"lang:fsi:{c['key']}" for c in COURSES] + ["lang:wikivoyage_phrasebooks"] +
           [f"lang:tatoeba:{c}" for c in TATOEBA_LANGUAGES]})

LICENCE_LINES = {
    "lang_fsi": "FSI, DLI and Peace Corps courses: works of the US government (17 U.S.C. 105, checked on govinfo.gov's "
                "policies page at every build), read from the Internet Archive (its items say public domain; "
                "robots.txt allows programs) and from fsi-languages.yojik.eu (robots.txt: \"Allow crawling of all "
                "content\", checked 2026-11-22). The audio is listed, never downloaded by the builder.",
    "lang_wikivoyage": "en.wikivoyage.org/wiki/Wikivoyage:Copyleft (checked at every build): CC BY-SA 4.0, "
                       "share-alike; robots.txt allows /wiki/ for our reader (checked 2026-11-22).",
    "lang_tatoeba": "tatoeba.org/en/downloads (checked at every build): \"These files are released under CC BY 2.0 "
                    "FR\"; downloads.tatoeba.org has no robots.txt; tatoeba.org asks 8 seconds between pages, and "
                    "only its downloads page is read (checked 2026-11-22).",
}

NOT_INCLUDED = [
    ("US State Department American English (americanenglish.state.gov: ESL lessons, Shaping the Way We Teach "
     "English, podcasts)", "The site answers programs \"403\", robots.txt included (checked 2026-11-22), and some "
     "of its materials are copyrighted by their authors. Link-only. Index: https://americanenglish.state.gov/"
     "resources"),
    ("USCIS English learning and citizenship study materials (vocabulary lists, reading and writing tests)",
     "Public domain, but www.uscis.gov answers programs \"403\" (checked 2026-11-22); the civics flash cards and "
     "100 questions are built from Internet Archive copies (civ:). Link-only. Index: https://www.uscis.gov/"
     "citizenship/find-study-materials-and-resources"),
    ("Defense Language Institute Haitian Creole Basic Course (1971, ERIC ED057697)", "Its own record says it is "
     "drawn from Albert Valdman's \"Basic Course in Haitian Creole\", which is copyrighted, so it is not built. "
     "Wikivoyage's Haitian Creole phrasebook and Tatoeba's sentences are. Index: https://archive.org/details/"
     "ERIC_ED057697"),
    ("Ann pale kreyol: An Introductory Course in Haitian Creole (1988)", "Indiana University Creole Institute, "
     "copyright. Link-only. Index: https://archive.org/details/ERIC_ED356617"),
    ("Defense Language Institute basic courses on the Internet Archive (Cantonese, Thai, French, Russian, Czech, "
     "Turkish, Swahili)", "Several gigabytes of page scans, most without a text layer to read aloud; the FSI "
     "courses of the same languages are built. Index: https://archive.org/details/DLI-Cantonese"),
    ("The FSI courses' audio files (several gigabytes per language)", "Not downloaded by the builder (the owner's "
     "rule for this collection): every recording is listed in its course book's originals, with its size, for "
     "the owner to download. Index: https://fsi-languages.yojik.eu/languages/fsi.html"),
    ("Wikivoyage and Wiktionary whole", "Already in the Kiwix library; only the phrasebooks are built here. Index: "
     "https://en.wikivoyage.org/wiki/Wikivoyage:Phrasebooks"),
    ("Tatoeba's audio recordings", "Each recording has the licence its speaker chose (some non-commercial or "
     "all rights reserved); link-only. Index: https://tatoeba.org/en/downloads"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
