"""Open language-learning resources from universities, non-governmental organisations and open projects, for the
"Languages" section of the reference library (the owner's request of 2026-11-23: a top-level Languages section with
all open resources). The books go in the group "languages" (languages.py's group; the government courses of FSI,
DLI, the military and other governments, and the Peace Corps courses, are made by their own modules). Prefix lopen:.

What this module builds, in plain words, by request word:

  lopen-textbooks   university language courses that are read from their publishers' own sites (COERLL, the
                    University of Texas at Austin's Center for Open Educational Resources and Language Learning):
                      Tex's French Grammar (CC BY 3.0) and Grimm Grammar, a German grammar (CC BY 4.0), every page
                      of each; the K'iche' Maya course "Chqeta'maj le qach'ab'al K'iche'!" and the Quechua course
                      "Quechua Tinkuy" (both CC BY), every lesson, read from each site's own WordPress API.
                    The open textbooks of the Open Textbook Library (cat:otl), LibreTexts (opencourses) and BCcampus
                    (course:bccampus) are built by their own modules, language books included: not repeated here.
  lopen-readers     Global Storybooks (the Global African Storybook Project, github.com/global-asp): the African
                    Storybook's picture-book stories translated into more than 40 world languages, one book per
                    language, each story page by page with its English beside it (a bilingual reader). Stories under
                    CC BY are in the main book of each language; stories under CC BY-NC are in a separate book
                    marked "personal use only". Pictures are left out (each story's words carry it).
  lopen-dictionaries  FreeDict bilingual dictionaries with English (download.freedict.org), each licence read from the
                    dictionary's own TEI header at every build: GNU GPL ones are share-alike books, CC BY ones open;
                    FreeDict's Wiktionary-derived dictionaries (WikDict) are left out because Wiktionary is already
                    in the Kiwix library. And Tatoeba sentences with English translations (CC BY 2.0 FR) for the
                    languages languages.py does not already have (Esperanto, Latin, Turkish, Polish, Dutch ...).
  lopen-classical   old public-domain grammars, primers and dictionaries (published before 1931, checked on each
                    Internet Archive record at every build): Latin, Ancient Greek, Biblical Hebrew, Sanskrit, Old
                    English and Esperanto.
  lopen-sign        old public-domain sign language books whose words describe each sign (Long's The Sign Language,
                    1918; Michaels's handbook, 1923; Seton's Sign Talk, 1918; Clark's and Tomkins's books of Plains
                    Indian Sign Language; Mallery's study for the Smithsonian, 1880), each marked as historical.
  lopen-braille     a guide to braille in other languages (lopen:braille_index: what the library has and where the
                    codes are published) and four old books on braille and Moon type for other languages (Louis
                    Braille's own Procédé of 1829, Oriental Braille 1902, Braille usuel 1920, Moon's Light for the
                    Blind 1877), kept as history, not as current codes.
  lang-open         all of the above, with lopen:index, a guide to every open language resource in the library.

Licences, truthfully: each book states its own (CC BY, CC BY-SA, GNU GPL, CC BY 2.0 FR, public domain before 1931, or
CC BY-NC with "personal use only"). World Braille Usage (2013), though printed by the Library of Congress's NLS, says
"Copyright 1954, 1990 by UNESCO. Used by permission 2013" and was published with Perkins and ICEB, so it is NOT taken as
a US government work: it is link-only (NOT_INCLUDED, and the braille guide links it).

What was looked at and not built is in NOT_INCLUDED, each with the reason and an index address.

Run from the repository's folder:
  python3 textbooks/languages_open.py --list lang-open
  python3 textbooks/languages_open.py lopen:gsb:es --out build/textbooks --limit 3
"""

import datetime
import html
import io
import json
import os
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402
from old_ia_books import old_book  # noqa: E402

PREFIX = "lopen"
GROUP = "languages"        # languages.py's group (its title is set there); nothing here makes a new group
GROUPS = {}

CC_BY_3 = "https://creativecommons.org/licenses/by/3.0/"
CC_BY_4 = "https://creativecommons.org/licenses/by/4.0/"
GPL2 = "GPL-2.0-or-later"                 # the names at_docs.py adds to sources.ALLOWED (share-alike)
GPL2_URL = "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html"
GPL2_ONLY = "GPL-2.0"
COERLL = "Center for Open Educational Resources and Language Learning (COERLL), University of Texas at Austin"
COERLL_LANG = "https://coerll.utexas.edu/coerll/materials/language/{}/"


def _rx_words(text):
    """The words of an HTML page as one line (tags removed, entities decoded, spaces joined)."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)\b.*?</\1>", " ",
                                                                   text or ""))).split())


def _first_number(text):
    """The first whole number in a text (for ordering lessons "Unit 12" and "Yachana 3"), 9999 when none."""
    m = re.search(r"\d+", text or "")
    return int(m.group(0)) if m else 9999


# ====================================================================== lopen-textbooks: COERLL grammars (static)

# Each grammar site: its index page (which lists every page, in order), the address pattern of its pages, where
# each page's text begins and ends, the page to read for its title, and the licence line (on the index page).
GRAMMARS = {
    "tex_french": dict(
        title="Tex's French Grammar (COERLL, University of Texas at Austin)", language="French",
        index="https://www.laits.utexas.edu/tex/gr/index.html", page=r"^(?!help\b)[a-z]+\d*\.html$",
        start=r"<!-- content -->", end=r"<!-- END content -->", title_drop=r"^[a-z]+\d*:\s*",
        licence="CC BY 3.0", licence_url=CC_BY_3, licence_text=r"creativecommons\.org/licenses/by/3\.0",
        authors="Carl Blyth, Karen Kelton, Nancy Guilloteau and the Tex's French Grammar team",
        description="A complete reference grammar of French for English speakers, written around the comic "
                    "dialogues of Tex the armadillo and his friends: nouns, determiners, adjectives, adverbs, verbs "
                    "and their tenses and moods, negation, prepositions, pronouns, conjunctions and questions, each "
                    "with French examples and their English translations. The companion grammar of Français "
                    "interactif.",
        print_view=""),
    "grimm_german": dict(
        title="Grimm Grammar: a German grammar (COERLL, University of Texas at Austin)", language="German",
        index="https://coerll.utexas.edu/gg/gr/index.html", page=r"^(?!help\b)[a-z]+_\d+\.html$",
        start=r"<!-- content_wrapper -->", end=r"<!-- end content_wrapper -->",
        title_drop=r"^Grimm Grammar\s*:\s*",
        licence="CC BY 4.0", licence_url=CC_BY_4, licence_text=r"creativecommons\.org/licenses/by/4\.0",
        authors="The Grimm Grammar team, Department of Germanic Studies, University of Texas at Austin",
        description="A German reference grammar for English speakers, explained through fairy-tale characters: "
                    "nouns and cases, articles and determiners, verbs and tenses, pronouns, conjunctions, "
                    "adjectives and their endings, adverbs and word order, each with German examples translated "
                    "into English. The companion grammar of Deutsch im Blick.",
        print_view="../pr/"),     # the print view of each page has its words without the site's menus
}


def grammar_links(spec, cache=None):
    """[page address] of a grammar site, in the order its index page lists them (no repeats)."""
    import build_textbooks as B
    text = B.fetch(spec["index"], cache)
    base = spec["index"]
    out = []
    for href in re.findall(r'href="([^"#?]+)"', text):
        if re.match(spec["page"], href) and href not in ("index.html",):
            url = urllib.parse.urljoin(base, (spec["print_view"] + href) if spec["print_view"] else href)
            out.append(url)
    return list(dict.fromkeys(out))


def grammar_page(spec, url, text):
    """(title, body HTML) of one grammar page: its <title> without the site's name, and the text between the
    content marks, cleaned (menus, scripts and pictures without words left out)."""
    import build_textbooks as B
    title = _rx_words((re.search(r"(?is)<title>(.*?)</title>", text) or [None, ""])[1])
    title = re.sub(spec["title_drop"], "", title).strip() or url.rsplit("/", 1)[-1]
    m1, m2 = re.search(spec["start"], text), re.search(spec["end"], text)
    part = text[m1.end():m2.start()] if m1 and m2 and m2.start() > m1.end() else ""
    part = re.sub(r"(?s)<!--.*?-->", "", part)
    return title, B._Cleaner({}, url).clean(part)


def grammar_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one COERLL grammar site ("grammar:<site>"): its licence line checked on its index page, then
    every page its index lists, in order."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    spec = GRAMMARS.get(name.split(":", 1)[1] if ":" in name else "")
    if spec is None:
        left_out.append({"title": name, "reason": "Unknown grammar."})
        return None
    if not K.readable(spec["index"], cache):
        left_out.append({"title": spec["title"], "reason": "The site's robots.txt does not allow reading it."})
        return None
    if not re.search(spec["licence_text"], B.fetch(spec["index"], cache)):
        left_out.append({"title": spec["title"], "reason": "Its index page no longer shows the licence that was "
                         "checked."})
        return None
    book = K.new_book(f"lopen_{name.split(':', 1)[1]}", spec["title"], f"Language learning: {spec['language']}",
                      GROUP, COERLL, spec["licence"], spec["licence_url"], spec["index"], spec["description"],
                      f"By {spec['authors']}, published by COERLL (University of Texas at Austin) under the "
                      f"{spec['licence']} licence. The audio and video of the site are not in this copy.",
                      country="United States", level="course", authors=spec["authors"],
                      changes="each page of the site made into a page of the book, with its menus, search box and "
                              "pictures left out")
    for number, url in enumerate(grammar_links(spec, cache), 1):
        if limit and len(book.pages) >= limit:
            break
        try:
            title, body = grammar_page(spec, url, B.fetch(url, cache))
        except (urllib.error.URLError, OSError) as e:
            left_out.append({"title": url, "reason": f"It could not be read ({e})."})
            continue
        if re.sub(r"<[^>]+>|\s", "", body):
            book.pages.append(B.Page(f"p{number:03d}-{B.slug(title, 40)}", title, body, 0, ""))
    book.originals.append({"url": spec["index"], "kind": "html"})
    return book


def grammar_sign(name):
    """A grammar site's sign of change: the list of its pages."""
    return K.sha(grammar_links(GRAMMARS[name.split(":", 1)[1]]))


# ====================================================================== lopen-textbooks: COERLL courses (WordPress)

# Each course: its WordPress site (the REST API at <site>/wp-json/wp/v2/), the COERLL catalogue page whose licence
# line is checked at every build, the pages to put first (by their address's last part) and which lessons to keep.
WP_COURSES = {
    "kiche": dict(
        title="Chqeta'maj le qach'ab'al K'iche'! A beginner to advanced K'iche' Maya course (COERLL)",
        language="K'iche' (Maya, Guatemala)", site="https://tzij.coerll.utexas.edu",
        licence="CC BY 4.0", licence_url=CC_BY_4, licence_page=COERLL_LANG.format("kiche"),
        licence_text=r"Language: K.iche. Format: [^:]* License: CC-BY(?![-\w])",
        first=["how-to-use-the-lessons", "the-language"], skip_link=r"/es/",
        authors="Sergio Romero, Ignacio Carvajal, Mareike Sattler, Juan Manuel Tahay Tzaj",
        description="An online course in K'iche', a Mayan language spoken by about a million people in Guatemala: "
                    "an introduction to the language and then 46 lessons (Tïjonïk) from greetings and family to "
                    "the Maya calendar and migration, each with its dialogue, vocabulary and grammar explained in "
                    "English. The English version of each lesson is kept (the site also has each in Spanish)."),
    "quechua": dict(
        title="Quechua Tinkuy: a beginner to intermediate Quechua course (COERLL)",
        language="Quechua (Southern Quechua, Peru)", site="https://quechuatinkuy.coerll.utexas.edu/en",
        licence="CC BY 4.0", licence_url=CC_BY_4, licence_page=COERLL_LANG.format("quechua"),
        licence_text=r"Language: Quechua Format: [^:]* License: CC-BY(?![-\w])",
        first=["introduccion", "el-idioma", "vocabulario"], skip_link=r"/es/",
        authors="Sergio Romero, Katherin Patricia Tairo-Quispe, Jermani Ojeda-Ludeña",
        description="An online course in Quechua, the most widely spoken indigenous language of the Americas, as "
                    "spoken in Cusco, Peru: an introduction, a vocabulary and 22 lessons (Yachana) from "
                    "pronunciation to everyday conversation, with grammar explained in English."),
}


def wp_items(site, kind, cache=None):
    """[dict] of every page or post ("pages", "posts") of a WordPress site, from its REST API, 100 at a time:
    id, link, title, modified and content."""
    import build_textbooks as B
    out, page = [], 1
    while page < 50:
        url = (f"{site}/wp-json/wp/v2/{kind}?per_page=100&page={page}"
               "&_fields=id,link,slug,title,modified,content")
        try:
            data = json.loads(B.fetch(url, cache))
        except urllib.error.HTTPError:
            break
        if not data:
            break
        out += data
        if len(data) < 100:
            break
        page += 1
    return out


def wp_course_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one COERLL WordPress course ("wpcourse:<course>"): the licence line checked on COERLL's catalogue
    page, then its introductory pages and every lesson (posts), in lesson order, from the site's REST API."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    spec = WP_COURSES.get(name.split(":", 1)[1] if ":" in name else "")
    if spec is None:
        left_out.append({"title": name, "reason": "Unknown course."})
        return None
    api = f"{spec['site']}/wp-json/wp/v2/posts"
    if not (K.readable(api, cache) and K.readable(spec["licence_page"], cache)):
        left_out.append({"title": spec["title"], "reason": "A robots.txt does not allow reading it."})
        return None
    if not re.search(spec["licence_text"], _rx_words(B.fetch(spec["licence_page"], cache))):
        left_out.append({"title": spec["title"], "reason": "COERLL's catalogue no longer shows the licence that was "
                         "checked."})
        return None
    pages = {p.get("slug"): p for p in wp_items(spec["site"], "pages", cache)}
    lessons = [p for p in wp_items(spec["site"], "posts", cache) if not re.search(spec["skip_link"], p.get("link", ""))]
    lessons.sort(key=lambda p: (_first_number(html.unescape(p["title"]["rendered"])), p["link"]))
    items = [("Introduction", pages[s]) for s in spec["first"] if s in pages] + [("Lessons", p) for p in lessons]
    book = K.new_book(f"lopen_{name.split(':', 1)[1]}", spec["title"], f"Language learning: {spec['language']}",
                      GROUP, COERLL, spec["licence"], spec["licence_url"], spec["site"], spec["description"],
                      f"By {spec['authors']}, published by COERLL (University of Texas at Austin) under the "
                      f"{spec['licence']} licence (as COERLL's catalogue states). The lessons' audio and video "
                      "are on the site and not in this copy.", country="United States", level="course",
                      authors=spec["authors"], changes="each lesson made into a page, with videos, audio players, "
                                                       "exercises and pictures left out")
    newest = ""
    for number, (unit, item) in enumerate(items, 1):
        if limit and len(book.pages) >= limit:
            break
        body = B._Cleaner({}, item.get("link", "")).clean((item.get("content") or {}).get("rendered", ""))
        title = html.unescape(re.sub(r"<[^>]+>", "", (item.get("title") or {}).get("rendered", "")))
        if re.sub(r"<[^>]+>|\s", "", body):
            book.pages.append(B.Page(f"p{number:03d}-{B.slug(title, 40)}", title, body, 0, unit))
            newest = max(newest, str(item.get("modified") or "")[:10])
    book.published = newest
    book.originals.append({"url": api, "kind": "json"})
    return book


def wp_course_sign(name):
    """A course's sign of change: the id and last change of every page and post."""
    spec = WP_COURSES[name.split(":", 1)[1]]
    return K.sha([(p["id"], p.get("modified")) for kind in ("pages", "posts") for p in wp_items(spec["site"], kind)])


# ====================================================================== lopen-readers: Global Storybooks

GASP_RAW = "https://raw.githubusercontent.com/global-asp/global-asp/master"
ASP_RAW = "https://raw.githubusercontent.com/global-asp/asp-source/master"
GASP_SITE = "https://globalstorybooks.net/"
# The languages of github.com/global-asp/global-asp with at least about 15 stories (its INDEX.md, checked
# 2026-11-23): its folder code and the language's name. French, Portuguese, Swahili and the other African languages
# are the African Storybook's own and are built by read_aloud.py (readaloud:african_storybook).
GSB_LANGUAGES = {
    "zh": "Chinese (Mandarin)", "yue": "Chinese (Cantonese)", "de": "German", "es": "Spanish", "it": "Italian",
    "ja": "Japanese", "ko": "Korean", "vi": "Vietnamese", "tl": "Tagalog", "ar": "Arabic", "fa": "Persian (Farsi)",
    "prs": "Dari", "ps": "Pashto", "ur": "Urdu", "hi": "Hindi", "bn": "Bengali", "pa": "Punjabi", "gu": "Gujarati",
    "ru": "Russian", "uk": "Ukrainian", "pl": "Polish", "nl": "Dutch", "sv": "Swedish", "da": "Danish",
    "nb": "Norwegian (Bokmål)", "nn": "Norwegian (Nynorsk)", "el": "Greek", "hu": "Hungarian", "ro": "Romanian",
    "lt": "Lithuanian", "tr": "Turkish", "ckb": "Kurdish (Sorani)", "eo": "Esperanto", "ht": "Haitian Creole",
    "jam": "Jamaican Patois", "mfe": "Mauritian Creole", "tet": "Tetum", "bo": "Tibetan", "adx": "Amdo Tibetan",
    "khg": "Khams Tibetan", "my": "Burmese", "mnw": "Mon", "rki": "Rakhine (Arakanese)", "aeb": "Tunisian Arabic",
}
GSB_NOTICE = ("Stories of the African Storybook (africanstorybook.org, Saide) translated by volunteers of Global "
              "Storybooks (globalstorybooks.net); each story's author, illustrator, translator and licence are on its "
              "page. Pictures are left out. Volunteers translated them: a translation may have mistakes.")


def gsb_rows(readme):
    """[(story number, title, basename, licence short, licence address)] of a language's README.md table: the
    basename from its "Plain HTML" link, the licence from its link ("CC BY 3.0", "CC BY-NC 4.0")."""
    out = []
    for line in readme.splitlines():
        if not re.match(r"^\d{4}\s*\|", line):
            continue
        cells = [c.strip() for c in line.split("|")]
        base = re.search(r"\[Plain HTML\]\(https?://[^)]*/([^/)]+)\.html\)", line)
        lic = re.search(r"\((https?://creativecommons\.org/licenses/([a-z-]+)/(\d\.\d)/?)\)", line)
        if not base or not lic:
            continue
        short = f"CC {lic.group(2).upper()} {lic.group(3)}"
        out.append((cells[0], cells[1], urllib.parse.unquote(base.group(1)), short, lic.group(1)))
    return out


def english_rows(readme):
    """{story number: English basename} from asp-source's en/README.md (number | [title](link) | licence): the
    basename is the number and the title in lower case, spaces as dashes, other punctuation left out."""
    out = {}
    for line in readme.splitlines():
        m = re.match(r"^(\d{4})\s*\|\s*\[([^\]]+)\]", line)
        if m:
            out[m.group(1)] = f"{m.group(1)}_{story_slug(m.group(2))}"
    return out


def story_slug(title):
    """A story title as global-asp names its files ("Goat, Dog, and Cow" -> "goat-dog-and-cow")."""
    words = re.sub(r"[^\w\s'-]", "", title.lower()).replace("'", "").split()
    return "-".join(words)


def story_sections(markdown):
    """(title, [page text], {metadata}) of a global-asp story in its Markdown form: the "# title" line, the pages
    between "##" lines, and the last section's "* Key: value" lines (License, Text, Illustration, Translation)."""
    parts = re.split(r"(?m)^##\s*$", markdown.replace("\r", ""))
    title = re.sub(r"^#\s*", "", parts[0].strip().splitlines()[0]) if parts and parts[0].strip() else ""
    meta, pages = {}, []
    for part in parts[1:]:
        lines = [x.strip() for x in part.strip().splitlines() if x.strip()]
        if lines and all(x.startswith("* ") for x in lines):
            for x in lines:
                key, _, value = x[2:].partition(":")
                meta[key.strip().lower()] = value.strip().strip("[]")
        elif lines:
            pages.append(" ".join(lines))
    return title, pages, meta


def story_file(folder, basename, cache=None):
    """(title, pages, metadata) of one story's Markdown file in folder, or None when it cannot be read. The file
    names are in composed Unicode (NFC) while some README links are decomposed, so the composed form is tried
    first, then the name as the README gives it."""
    import build_textbooks as B
    import unicodedata
    for form in dict.fromkeys([unicodedata.normalize("NFC", basename), basename]):
        try:
            return story_sections(B.fetch(f"{folder}/{urllib.parse.quote(form)}.md", cache))
        except (urllib.error.URLError, OSError):
            continue
    return None


def story_body(code, story, english):
    """The HTML of one bilingual story page: its credits, then each page of the story with its English beside it
    (as a table: page number, the language, English); when the English is missing or has another number of pages,
    the language's pages alone, then the English story after it."""
    import build_textbooks as B
    title, pages, meta = story
    credits = [(k.capitalize(), meta[k]) for k in ("text", "illustration", "translation", "license") if meta.get(k)]
    body = K.dl(credits)
    if english and len(english[1]) == len(pages):
        rows = "".join(f"<tr><td>{n}</td><td lang=\"{code}\">{B.esc(p)}</td><td lang=\"en\">{B.esc(e)}</td></tr>"
                       for n, (p, e) in enumerate(zip(pages, english[1]), 1))
        body += (f"<table><tr><th>Page</th><th>{B.esc(GSB_LANGUAGES[code])}</th><th>English: {B.esc(english[0])}"
                 f"</th></tr>{rows}</table>")
    else:
        body += "".join(f"<p lang=\"{code}\">{B.esc(p)}</p>" for p in pages)
        if english:
            body += f"<h2>In English: {B.esc(english[0])}</h2>" + "".join(f"<p lang=\"en\">{B.esc(e)}</p>"
                                                                          for e in english[1])
    return body


def gsb_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one language's stories ("gsb:<code>" for its CC BY stories, "gsbnc:<code>" for its CC BY-NC
    stories, personal use only)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    base, _, code = name.partition(":")
    if code not in GSB_LANGUAGES:
        left_out.append({"title": name, "reason": "Unknown language."})
        return None
    personal = base == "gsbnc"
    readme_url = f"{GASP_RAW}/{code}/README.md"
    if not K.readable(readme_url, cache):
        left_out.append({"title": name, "reason": "The site's robots.txt does not allow reading it."})
        return None
    rows = [r for r in gsb_rows(B.fetch(readme_url, cache)) if (" NC" in r[3] or "-NC" in r[3]) == personal]
    rows = [r for r in rows if "ND" not in r[3]]
    if not rows:
        left_out.append({"title": name, "reason": "Global Storybooks has no stories of this language under this "
                         "licence."})
        return None
    english = english_rows(B.fetch(f"{ASP_RAW}/en/README.md", cache))
    language = GSB_LANGUAGES[code]
    shorts = sorted({r[3] for r in rows})
    licence = shorts[0] if len(shorts) == 1 else shorts[0].rsplit(" ", 1)[0] + " " + " and ".join(
        s.rsplit(" ", 1)[1] for s in shorts)
    kind = "CC BY-NC (non-commercial)" if personal else "CC BY"
    book = K.new_book(f"lopen_gsb{'nc' if personal else ''}_{code}",
                      f"{language} and English stories: a bilingual reader (Global Storybooks"
                      f"{', personal use only' if personal else ''})", f"Language learning: {language}", GROUP,
                      "Global Storybooks (Global African Storybook Project) and the African Storybook (Saide)",
                      licence, rows[0][4], GASP_SITE,
                      f"Short picture-book stories in {language}, each page with its English beside it, for "
                      f"learners and for reading with children: the stories of Global Storybooks under {kind}. "
                      "The stories go from first words (counting, animals, feelings) to longer folk tales.",
                      GSB_NOTICE + (" These stories are under a non-commercial licence: personal use only."
                                    if personal else ""),
                      country="International", level="reference",
                      changes="each story's words read from its Markdown file and set beside its English; pictures "
                              "left out; no words changed")
    book.personal_use = personal
    for number, (story_no, title, basename, short, lic_url) in enumerate(rows, 1):
        if limit and len(book.pages) >= limit:
            break
        story = story_file(f"{GASP_RAW}/{code}", basename, cache)
        if story is None:
            left_out.append({"title": f"{title} ({story_no})", "reason": "Its Markdown file could not be read."})
            continue
        eng = None
        if story_no in english:
            eng = story_file(f"{ASP_RAW}/en", english[story_no], cache)
        story[2].setdefault("license", short)
        body = story_body(code, story, eng) + f"<p>Licence: <a href=\"{B.esc(lic_url)}\">{B.esc(short)}</a>.</p>"
        book.pages.append(B.Page(f"story-{story_no}", f"{story[0] or title} ({story_no})", body, 0, ""))
    book.originals.append({"url": readme_url, "kind": "md"})
    return book


def gsb_sign(name):
    """A language's sign of change: its README (the list of stories and their licences)."""
    import build_textbooks as B
    return K.sha(B.fetch(f"{GASP_RAW}/{name.split(':', 1)[1]}/README.md"))


# ====================================================================== lopen-dictionaries: FreeDict

FREEDICT_DB = "https://freedict.org/freedict-database.json"
FREEDICT = "https://freedict.org/"
# FreeDict's dictionaries between English and another language that are not made from Wiktionary (FreeDict's own
# and older contributed ones; checked 2026-11-23 in freedict-database.json). The WikDict ones (editions named by a
# date, such as 2025.11.23) are left out at build time too: their TEI header names Wiktionary.
FREEDICT_NAMES = [
    "deu-eng", "eng-deu", "jpn-eng", "eng-ces", "ces-eng", "hun-eng", "eng-hun", "eng-ara", "ara-eng", "hrv-eng",
    "eng-hrv", "epo-eng", "eng-tur", "tur-eng", "eng-hin", "nld-eng", "eng-nld", "eng-ell", "eng-pol", "eng-por",
    "por-eng", "eng-cym", "cym-eng", "isl-eng", "kur-eng", "eng-fra", "fra-eng", "lit-eng", "eng-lit", "eng-afr",
    "afr-eng", "slv-eng", "swe-eng", "dan-eng", "eng-dan", "spa-eng", "eng-lat", "lat-eng", "swh-eng", "eng-swh",
    "kha-eng", "eng-gle", "gle-eng", "eng-rom", "slk-eng", "eng-srp", "srp-eng",
]
LANG3 = {"deu": "German", "jpn": "Japanese", "ces": "Czech", "hun": "Hungarian", "ara": "Arabic", "hrv": "Croatian",
         "epo": "Esperanto", "tur": "Turkish", "hin": "Hindi", "nld": "Dutch", "ell": "Greek", "pol": "Polish",
         "por": "Portuguese", "cym": "Welsh", "isl": "Icelandic", "kur": "Kurdish", "fra": "French",
         "lit": "Lithuanian", "afr": "Afrikaans", "slv": "Slovenian", "swe": "Swedish", "dan": "Danish",
         "spa": "Spanish", "lat": "Latin", "swh": "Swahili", "kha": "Khasi", "gle": "Irish", "rom": "Romani",
         "slk": "Slovak", "srp": "Serbian", "eng": "English"}
ENTRIES_PER_PAGE = 400
TEI = "{http://www.tei-c.org/ns/1.0}"


def freedict_record(name, cache=None):
    """The record of one dictionary in FreeDict's database (edition, headwords, releases), {} when not listed."""
    import build_textbooks as B
    for x in json.loads(B.fetch(FREEDICT_DB, cache)):
        if x.get("name") == name:
            return x
    return {}


def tei_licence(header_text):
    """(licence, licence address) of a FreeDict TEI header's <availability>, or ("", reason) when it names none the
    library may use: GNU GPL version 2 (or later), a Creative Commons licence without NonCommercial or
    NoDerivatives, or public domain. A header that names Wiktionary or WikDict gives ("", ...) too."""
    import build_textbooks as B
    if re.search(r"(?i)wiktionary|wikdict", header_text):
        return "", "Made from Wiktionary, which is already in the Kiwix library."
    m = re.search(r"(?s)<availability\b.*?</availability>", header_text)
    words = " ".join(re.sub(r"<[^>]+>", " ", m.group(0)).split()) if m else ""
    refs = " ".join(re.findall(r'target="([^"]+)"', m.group(0))) if m else ""
    low = f"{words} {refs}".lower()
    if "general public license" in low or "/gpl" in low:
        later = "later version" in low or "or-later" in low or "(at your option)" in low
        return (GPL2, GPL2_URL) if later else (GPL2_ONLY, GPL2_URL)
    if "creative commons" in low or "creativecommons.org" in low:
        short = B.licence_short(words, refs)
        if B.licence_kind(short) in ("open", "share-alike"):
            return short, B._licence_address(short) or refs
        return "", f"Its licence ({short}) is not one the library may repackage."
    if "public domain" in low:
        return "PD", "https://creativecommons.org/publicdomain/mark/1.0/"
    return "", "Its TEI header names no licence the library may use."


def tei_entries(stream):
    """[(headword, details)] of a TEI dictionary file (a file object), read entry by entry: the headword (its
    <orth>), its pronunciation and part of speech, and its translations (<cit type="trans"><quote>) or
    definitions, joined with "; "."""
    out = []
    for _event, el in ET.iterparse(stream, events=("end",)):
        if el.tag != f"{TEI}entry":
            continue
        orths = [" ".join("".join(o.itertext()).split()) for o in el.iter(f"{TEI}orth")]
        prons = [" ".join("".join(p.itertext()).split()) for p in el.iter(f"{TEI}pron")]
        poses = [" ".join("".join(p.itertext()).split()) for p in el.iter(f"{TEI}pos")]
        trans = []
        for cit in el.iter(f"{TEI}cit"):
            if cit.get("type") in ("trans", "translation", None):
                for q in cit.findall(f"{TEI}quote"):
                    t = " ".join("".join(q.itertext()).split())
                    if t and t not in trans:
                        trans.append(t)
        if not trans:
            trans = [" ".join("".join(d.itertext()).split()) for d in el.iter(f"{TEI}def")]
        if orths and orths[0]:
            extra = (f" [{prons[0]}]" if prons and prons[0] else "") + (f" ({poses[0]})" if poses and poses[0] else "")
            out.append((orths[0], extra.strip(), "; ".join(t for t in trans if t)))
        el.clear()
    return out


def dictionary_pages(entries, limit=None):
    """[(path, title, body HTML)] of a dictionary's entries in alphabetical order, ENTRIES_PER_PAGE to a page,
    each page named by its first and last headword; each entry a <dt> headword and a <dd> of its translations."""
    import build_textbooks as B
    entries = sorted(entries, key=lambda e: (e[0].casefold(), e[0]))
    out = []
    for start in range(0, len(entries), ENTRIES_PER_PAGE):
        if limit and len(out) >= limit:
            break
        chunk = entries[start:start + ENTRIES_PER_PAGE]
        items = "".join(f"<dt>{B.esc(h)}{(' ' + B.esc(x)) if x else ''}</dt><dd>{B.esc(t)}</dd>" for h, x, t in chunk)
        title = f"{chunk[0][0]} to {chunk[-1][0]}"
        out.append((f"words-{start // ENTRIES_PER_PAGE + 1:04d}", title, f"<dl>{items}</dl>"))
    return out


def freedict_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one FreeDict dictionary ("freedict:<from>-<to>"): its source release (.src.tar.xz) downloaded
    once to the cache folder, its licence read from the TEI header, its entries made into alphabetical pages."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    dname = name.split(":", 1)[1] if ":" in name else ""
    if dname not in FREEDICT_NAMES:
        left_out.append({"title": name, "reason": "Unknown dictionary."})
        return None
    record = freedict_record(dname, cache)
    src = next((r for r in record.get("releases", []) if r.get("platform") == "src"), None)
    if not src:
        left_out.append({"title": name, "reason": "FreeDict's database lists no source release of it."})
        return None
    if not K.readable(src["URL"], cache):
        left_out.append({"title": name, "reason": "The site's robots.txt does not allow reading it."})
        return None
    path = K.download_file(src["URL"], cache, name=src["URL"].rsplit("/", 1)[-1])
    with tarfile.open(path, "r:xz") as tar:
        member = next((m for m in tar.getmembers() if m.name.endswith(".tei")), None)
        if member is None:
            left_out.append({"title": name, "reason": "Its source release holds no TEI file."})
            return None
        data = tar.extractfile(member).read()
    header = data[:data.find(b"</teiHeader>") + 12].decode("utf-8", "replace")
    licence, licence_url = tei_licence(header)
    if not licence:
        left_out.append({"title": name, "reason": licence_url})
        return None
    entries = tei_entries(io.BytesIO(data))
    if not entries:
        left_out.append({"title": name, "reason": "No entries could be read from its TEI file."})
        return None
    a, b = dname.split("-")
    title_words = _rx_words((re.search(r"(?s)<titleStmt>\s*<title>(.*?)</title>", header) or [None, ""])[1])
    kind = " (share-alike: GNU GPL)" if licence.startswith("GPL") else ""
    book = K.new_book(f"lopen_freedict_{dname.replace('-', '_')}", f"{LANG3[a]}-{LANG3[b]} dictionary (FreeDict)",
                      f"Language learning: {LANG3[a] if a != 'eng' else LANG3[b]}", GROUP,
                      "The FreeDict project and the dictionary's authors (freedict.org)", licence, licence_url,
                      FREEDICT, f"{title_words or dname}: {len(entries):,} {LANG3[a]} headwords with their "
                      f"{LANG3[b]} translations, in alphabetical order, {ENTRIES_PER_PAGE} to a page{kind}.",
                      f"From FreeDict (freedict.org), edition {record.get('edition', '')}: copyright of its authors "
                      f"as its TEI header names them, under {licence}. Volunteers made it: check important words in "
                      "a second dictionary.", country="International",
                      changes="the entries of its TEI file made into alphabetical pages; no entry changed")
    book.published = str(record.get("date") or "")
    book.version = f"FreeDict edition {record.get('edition', '')}"
    book.originals.append({"url": src["URL"], "kind": "tar.xz", "size": int(src.get("size") or 0)})
    for p, title, body in dictionary_pages(entries, limit):
        book.pages.append(B.Page(p, title, body, 0, ""))
    return book


def freedict_sign(name):
    """A dictionary's sign of change: its FreeDict record (edition and releases)."""
    return K.sha(freedict_record(name.split(":", 1)[1]))


# ====================================================================== lopen-dictionaries: more Tatoeba languages

# Tatoeba languages not in languages.TATOEBA_LANGUAGES, each with English links (checked 2026-11-23).
TATOEBA_MORE = {
    "epo": "Esperanto", "lat": "Latin", "grc": "Ancient Greek", "tur": "Turkish", "pol": "Polish", "nld": "Dutch",
    "ukr": "Ukrainian", "hin": "Hindi", "mar": "Marathi", "ben": "Bengali", "urd": "Urdu", "pes": "Persian",
    "swe": "Swedish", "fin": "Finnish", "hun": "Hungarian", "ces": "Czech", "slk": "Slovak", "dan": "Danish",
    "nob": "Norwegian (Bokmål)", "isl": "Icelandic", "ind": "Indonesian", "zsm": "Malay", "tha": "Thai",
    "swh": "Swahili", "lit": "Lithuanian", "lvs": "Latvian", "est": "Estonian", "ron": "Romanian",
    "bul": "Bulgarian", "mkd": "Macedonian", "srp": "Serbian", "hrv": "Croatian", "bel": "Belarusian",
    "cat": "Catalan", "gle": "Irish", "cym": "Welsh", "hye": "Armenian", "kat": "Georgian", "aze": "Azerbaijani",
    "kab": "Kabyle", "ber": "Berber", "tok": "Toki Pona", "ina": "Interlingua",
}


def tatoeba_more_book(name, work, cache=None, left_out=None, limit=None):
    """The Book of one more language's Tatoeba sentences ("tatoeba:<code>"), made with languages.py's own Tatoeba
    reader (the licence line checked on Tatoeba's downloads page, the files streamed to the cache folder)."""
    import build_textbooks as B
    import languages as L
    left_out = left_out if left_out is not None else []
    code = name.split(":", 1)[1] if ":" in name else ""
    if code not in TATOEBA_MORE:
        left_out.append({"title": name, "reason": "Unknown language."})
        return None
    if not re.search(L.TATOEBA_TEXT, _rx_words(B.fetch(L.TATOEBA_TERMS, cache))):
        left_out.append({"title": name, "reason": "Tatoeba's downloads page no longer says CC BY 2.0 FR."})
        return None
    urls = {"links": f"{L.TATOEBA}/{code}/{code}-eng_links.tsv.bz2",
            "foreign": f"{L.TATOEBA}/{code}/{code}_sentences.tsv.bz2",
            "english": f"{L.TATOEBA}/eng/eng_sentences.tsv.bz2"}
    paths = {k: K.download_file(u, cache, name=u.rsplit("/", 1)[-1], max_age_days=6) for k, u in urls.items()}
    foreign = L.tatoeba_sentences(paths["foreign"])
    links = L.tatoeba_links(paths["links"], foreign)
    pairs = L.tatoeba_pairs(links, foreign, L.tatoeba_sentences(paths["english"], set(links.values())))
    if not pairs:
        left_out.append({"title": name, "reason": "Tatoeba has no sentences of this language with an English "
                         "translation."})
        return None
    language = TATOEBA_MORE[code]
    book = K.new_book(f"lopen_tatoeba_{code}", f"{language} sentences with English translations (Tatoeba)",
                      f"Language learning: {language}", GROUP, "Tatoeba contributors (tatoeba.org)", "CC BY 2.0 FR",
                      "https://creativecommons.org/licenses/by/2.0/fr/deed.en", L.TATOEBA_TERMS,
                      f"Up to {L.MOST_PAIRS:,} {language} sentences from Tatoeba, each with an English translation, "
                      f"the shortest first, {L.PAIRS_PER_PAGE} to a page.",
                      "Sentences and translations by Tatoeba's contributors (tatoeba.org), CC BY 2.0 FR (some also "
                      "CC0); each sentence's Tatoeba number is given, and tatoeba.org/sentences/show/<number> shows "
                      "its page and author. Volunteers wrote them: some may have mistakes.",
                      country="International", level="reference",
                      changes="each sentence paired with its first English translation, sorted shortest first and "
                              "made into tables; no sentence changed")
    book.version = f"Tatoeba exports of {datetime.date.today().isoformat()}"
    book.originals += [{"url": u, "kind": "tsv.bz2", "size": os.path.getsize(paths[k])} for k, u in urls.items()]
    for start in range(0, len(pairs), L.PAIRS_PER_PAGE):
        if limit and len(book.pages) >= limit:
            break
        chunk = pairs[start:start + L.PAIRS_PER_PAGE]
        rows = "".join(f"<tr><td lang=\"{code}\">{B.esc(f)}</td><td>{B.esc(e)}</td><td>{fn}, {en}</td></tr>"
                       for fn, f, en, e in chunk)
        body = (f"<table><tr><th>{B.esc(language)}</th><th>English</th><th>Tatoeba sentence numbers</th></tr>"
                f"{rows}</table>")
        book.pages.append(B.Page(f"sentences-{start + 1}", f"Sentences {start + 1} to {start + len(chunk)}", body,
                                 0, f"{language} and English"))
    return book


def tatoeba_more_sign(name):
    """A language's sign of change (languages.py's: the server's date and size of its files)."""
    import languages as L
    return L.tatoeba_sign(name)


# ====================================================================== lopen-classical, lopen-sign, lopen-braille: old books

CLASSICAL_NOTE = ("Published in {year}: an old book, kept for its grammar, which has not changed. Its explanations "
                  "assume a reader of its time, the scanned text has the scanner's mistakes, and Greek, Hebrew and "
                  "Sanskrit letters may be missing or garbled in the machine-read text (check them in a modern "
                  "edition).")
ESPERANTO_NOTE = ("Published in {year}: an early Esperanto book. The language's grammar is the same today (the "
                  "Fundamento of 1905 is still its rule), but some words have changed or been added since; the "
                  "scanned text has the scanner's mistakes and the accented letters (ĉ, ĝ, ĥ, ĵ, ŝ, ŭ) may be "
                  "garbled.")
SIGN_NOTE = ("Published in {year}: a historical book. Signs change over time and differ from place to place, so "
             "many signs it describes are no longer used or are made differently today; learn current signs from Deaf "
             "teachers and the Deaf community. It is kept because its words describe each sign (hand shape, place "
             "and movement), which a reader who cannot see the pictures can follow. The scanned text has the "
             "scanner's mistakes.")
PLAINS_NOTE = ("Published in {year}: a historical book about Plains Indian Sign Language, written by a white author "
               "of its time: its words about Native American peoples are often prejudiced and offensive today, and "
               "its descriptions are an outsider's record, not the nations' own teaching. It is kept for its "
               "descriptions of the signs. The scanned text has the scanner's mistakes.")
BRAILLE_NOTE = ("Published in {year}: a historical book about braille or embossed type for other languages. The codes "
                "it gives are NOT the current ones (today's codes are set by each country's braille authority; see "
                "World Braille Usage, linked from the braille guide lopen:braille_index); it is kept as history. "
                "The scanned text has the scanner's mistakes and braille cells are shown only as pictures in the "
                "scan, so most are not in the text.")


def _old(name, title, subject, publisher, archive, year, description, note):
    """An old public-domain book entry (old_ia_books.old_book) in this module's group."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note)


CLASSICAL = [
    _old("allen_greenough_latin_grammar_1903", "Allen and Greenough's New Latin Grammar (1903)",
         "Language learning: Latin", "Ginn and Company", "allengreenoughsn00alleiala", 1903,
         "The standard reference grammar of classical Latin: sounds, forms, syntax and verse.", CLASSICAL_NOTE),
    _old("dooge_latin_for_beginners_1911", "Latin for Beginners (D'Ooge, 1911)", "Language learning: Latin",
         "Ginn and Company", "latinforbeginner00doog", 1911,
         "A first-year Latin course in lessons, with vocabularies, exercises and reading passages.", CLASSICAL_NOTE),
    _old("lewis_elementary_latin_dictionary_1891", "An Elementary Latin Dictionary (Lewis, 1891)",
         "Language learning: Latin", "Harper and Brothers", "elementarylatind01lewi", 1891,
         "A Latin-English dictionary for students of Caesar, Cicero, Virgil and the other school authors.",
         CLASSICAL_NOTE),
    _old("white_first_greek_book_1896", "The First Greek Book (White, 1896)", "Language learning: Ancient Greek",
         "Ginn and Company", "white-the-first-greek-book-1896", 1896,
         "A first-year course in Attic Greek in lessons, leading to Xenophon's Anabasis.", CLASSICAL_NOTE),
    _old("goodwin_greek_grammar_1892", "A Greek Grammar (Goodwin, 1892)", "Language learning: Ancient Greek",
         "Ginn and Company", "greekgrammar00gooduoft", 1892,
         "A reference grammar of Ancient Greek: letters and sounds, forms, syntax and verse.", CLASSICAL_NOTE),
    _old("smyth_greek_grammar_1920", "A Greek Grammar for Colleges (Smyth, 1920)",
         "Language learning: Ancient Greek", "American Book Company", "agreekgrammarfo02smytgoog", 1920,
         "The fullest English reference grammar of Ancient Greek, still the standard one.", CLASSICAL_NOTE),
    _old("liddell_scott_intermediate_lexicon_1889", "An Intermediate Greek-English Lexicon (Liddell and Scott, 1889)",
         "Language learning: Ancient Greek", "Harper and Brothers", "intermediategree00lidd", 1889,
         "The \"Middle Liddell\": a Greek-English dictionary for readers of Homer, the dramatists, Plato and the "
         "historians.", CLASSICAL_NOTE),
    _old("gesenius_hebrew_grammar_1910", "Gesenius' Hebrew Grammar (Kautzsch and Cowley, 1910)",
         "Language learning: Biblical Hebrew", "Clarendon Press", "geseniushebrewgr00geseuoft", 1910,
         "The classic reference grammar of Biblical Hebrew, in the English edition of 1910.", CLASSICAL_NOTE),
    _old("davidson_introductory_hebrew_grammar_1916", "An Introductory Hebrew Grammar (Davidson, 1916)",
         "Language learning: Biblical Hebrew", "T. and T. Clark", "introductoryhebr00davirich", 1916,
         "A first course in Biblical Hebrew with progressive exercises in reading and writing.", CLASSICAL_NOTE),
    _old("whitney_sanskrit_grammar_1879", "A Sanskrit Grammar (Whitney, 1879)", "Language learning: Sanskrit",
         "Breitkopf and Härtel", "sanskritgrammari00whituoft", 1879,
         "A reference grammar of classical and Vedic Sanskrit.", CLASSICAL_NOTE),
    _old("perry_sanskrit_primer_1901", "A Sanskrit Primer (Perry, 1901)", "Language learning: Sanskrit",
         "Ginn and Company", "sanskritprimer00perrrich", 1901,
         "A first Sanskrit course in lessons, based on Bühler's Leitfaden, with exercises and vocabularies.",
         CLASSICAL_NOTE),
    _old("macdonell_sanskrit_grammar_students_1927", "A Sanskrit Grammar for Students (Macdonell, 1927)",
         "Language learning: Sanskrit", "Oxford University Press", "sanskritgrammarf014425mbp", 1927,
         "A concise Sanskrit grammar for students, third edition.", CLASSICAL_NOTE),
    _old("sweet_anglo_saxon_primer_1886", "An Anglo-Saxon Primer (Sweet, 1886)",
         "Language learning: Old English", "Clarendon Press", "anglosaxonprimer00sweerich", 1886,
         "A first book of Old English: grammar, short readings, notes and a glossary.", CLASSICAL_NOTE),
    _old("bright_anglo_saxon_reader_1891", "An Anglo-Saxon Reader (Bright, 1891)", "Language learning: Old English",
         "Henry Holt", "anglosaxonreader00briguoft", 1891,
         "Old English readings with notes, a complete glossary and an outline of grammar and verse.", CLASSICAL_NOTE),
    _old("zamenhof_fundamento_esperanto_1905", "Fundamento de Esperanto (Zamenhof, 1905)",
         "Language learning: Esperanto", "Hachette", "fundamentodeesp00zamegoog", 1905,
         "The foundation of Esperanto by its creator: the grammar, the exercises and the universal word list "
         "(in Esperanto, French, English, German, Russian and Polish).", ESPERANTO_NOTE),
    _old("kellerman_complete_grammar_esperanto_1910", "A Complete Grammar of Esperanto (Kellerman, 1910)",
         "Language learning: Esperanto", "D. C. Heath", "rosettaproject_epo_morsyn-1", 1910,
         "A full Esperanto course for English speakers in lessons, with reading passages and vocabularies.",
         ESPERANTO_NOTE),
    _old("motteau_esperanto_english_dictionary_1907", "Esperanto-English Dictionary (Motteau, 1907)",
         "Language learning: Esperanto", "Review of Reviews Office", "esperantoenglish00mottrich", 1907,
         "An Esperanto-English dictionary.", ESPERANTO_NOTE),
    _old("oconnor_english_esperanto_dictionary_1907", "English-Esperanto Dictionary (O'Connor and Hayes, 1907)",
         "Language learning: Esperanto", "Review of Reviews Office", "englishesperanto00oconuoft", 1907,
         "An English-Esperanto dictionary.", ESPERANTO_NOTE),
    _old("baker_american_esperanto_book_1907", "The American Esperanto Book (Baker, 1907)",
         "Language learning: Esperanto", "Arthur Baker", "americanesperant00bakeiala", 1907,
         "A compendium of Esperanto for Americans: grammar, exercises, reading and a vocabulary.", ESPERANTO_NOTE),
]

SIGN = [
    _old("long_sign_language_1918", "The Sign Language: A Manual of Signs (Long, 1918)",
         "Language learning: American Sign Language (historical)", "R. Henderson", "gu_signlanguagem00long", 1918,
         "J. Schuyler Long's manual of the signs of American deaf people, a descriptive vocabulary arranged by "
         "subject: each sign's hand shape, place and movement told in words.", SIGN_NOTE),
    _old("michaels_handbook_sign_language_1923", "A Handbook of the Sign Language of the Deaf (Michaels, 1923)",
         "Language learning: American Sign Language (historical)", "Home Mission Board, Southern Baptist Convention",
         "gu_handbooksignl00mich", 1923,
         "J. W. Michaels's handbook of signs, prepared for ministers and others working with deaf people, each "
         "sign described in words.", SIGN_NOTE),
    _old("seton_sign_talk_1918", "Sign Talk: A Universal Signal Code (Seton, 1918)",
         "Language learning: sign languages (historical)", "Doubleday, Page", "signtalkuniversa00setouoft", 1918,
         "Ernest Thompson Seton's dictionary of hand signs drawn from Plains Indian Sign Language and the signs of "
         "deaf people, for use without words, each described in words.", PLAINS_NOTE),
    _old("clark_indian_sign_language_1885", "The Indian Sign Language (Clark, 1885)",
         "Language learning: Plains Indian Sign Language (historical)", "L. R. Hamersly", "cu31924028770570", 1885,
         "W. P. Clark's dictionary of Plains Indian Sign Language, each sign described in words.", PLAINS_NOTE),
    _old("tomkins_universal_indian_sign_language_1926", "Universal Indian Sign Language (Tomkins, 1926)",
         "Language learning: Plains Indian Sign Language (historical)", "William Tomkins",
         "universalindians006602mbp", 1926,
         "William Tomkins's short book of Plains Indian Sign Language for scouts, with a dictionary.", PLAINS_NOTE),
    _old("mallery_sign_language_study_1880", "Introduction to the Study of Sign Language among the North American "
         "Indians (Mallery, 1880)", "Language learning: sign languages (historical)",
         "Smithsonian Institution, Bureau of Ethnology (US Government Printing Office)",
         "introstudysignlang00mallrich", 1880,
         "Garrick Mallery's study for the Smithsonian, comparing Plains Indian signs with the signs of deaf people "
         "and others (also a US government work).", PLAINS_NOTE),
]

BRAILLE = [
    _old("braille_procede_1829", "Procédé pour écrire les paroles, la musique et le plain-chant au moyen de points "
         "(Louis Braille, 1829)", "Braille in other languages (historical)",
         "Institution royale des jeunes aveugles, Paris", "procdpourcrirele00loui", 1829,
         "Louis Braille's own first description of his six-dot system, in French, for words, music and plain "
         "chant.", BRAILLE_NOTE),
    _old("oriental_braille_1902", "Oriental Braille: One Alphabet for the Blind for All Oriental Languages (1902)",
         "Braille in other languages (historical)", "British and Foreign Bible Society", "orientalbrailleo00byre",
         1902, "J. Knowles and L. Garthwaite's proposal for one braille alphabet for the languages of Asia and "
               "Africa, with tables for many languages.", BRAILLE_NOTE),
    _old("braille_usuel_1920", "Braille usuel pour la correspondance entre les aveugles et les clairvoyants (Nouet, "
         "1920)", "Braille in other languages (historical)", "Imprimerie Monnoyer", "brailleusuelpour00mlec", 1920,
         "A French guide to everyday braille for letters between blind and sighted people.", BRAILLE_NOTE),
    _old("moon_light_for_the_blind_1877", "Light for the Blind: Moon's System of Reading for the Blind (Moon, 1877)",
         "Braille in other languages (historical)", "Longmans, Green and Co.", "b2487727x", 1877,
         "William Moon's history of his embossed type and its adaptation to many languages around the world.",
         BRAILLE_NOTE),
]
PDFS = CLASSICAL + SIGN + BRAILLE

# ====================================================================== the guides (index books)

SWADESH = "https://en.wiktionary.org/wiki/Appendix:Swadesh_lists"
INDEX_SECTIONS = [
    ("University language textbooks", "Open textbooks and courses from universities. The whole open catalogues are "
     "built by their own collections, language books included.", [
        ("key", "lopen:grammar:tex_french", "Tex's French Grammar (COERLL, CC BY)"),
        ("key", "lopen:grammar:grimm_german", "Grimm Grammar: German grammar (COERLL, CC BY)"),
        ("key", "lopen:wpcourse:kiche", "K'iche' Maya course (COERLL, CC BY)"),
        ("key", "lopen:wpcourse:quechua", "Quechua Tinkuy (COERLL, CC BY)"),
        ("word", "cat:otl", "The Open Textbook Library: Français interactif, Deutsch im Blick, Trayectos, "
                            "Conversa Brasileira, Japanese, Arabic, ESL and the other language textbooks"),
        ("word", "opencourses", "LibreTexts (its Humanities library has the language shelves) and BCcampus"),
        ("link", "COERLL's full catalogue", "https://coerll.utexas.edu/coerll/materials/",
         "some courses are on Pressbooks sites that refuse programs; open them in a browser"),
        ("link", "Hecho en Texas (Spanish, CC BY-SA) and Giornate Italiane (Italian, CC BY-NC-SA)",
         "https://utexas.pressbooks.pub/hechoentexas", "on UT's Pressbooks, which refuses programs")]),
    ("Readers and stories", "Picture-book stories in many languages, for learners and children.", [
        ("word", "lopen-readers", "Global Storybooks: bilingual readers in more than 40 languages with English"),
        ("word", "read-aloud", "Book Dash and the African Storybook (African languages, English and French)"),
        ("word", "dir:storyweaver", "Pratham Books' StoryWeaver (Indian and many other languages)"),
        ("word", "dir:gdl", "The Global Digital Library"),
        ("link", "Bloom Library (SIL)", "https://bloomlibrary.org/", "its catalogue is open only to its own app"),
        ("link", "Let's Read (The Asia Foundation)", "https://www.letsreadasia.org/",
         "a reading app with no download route"),
        ("link", "Indigenous Storybooks (Canada)", "https://indigenousstorybooks.ca",
         "Global Storybooks' stories in Indigenous languages of Canada; open it in a browser")]),
    ("Dictionaries, word lists and sentences", "Bilingual dictionaries and example sentences.", [
        ("word", "lopen-dictionaries", "FreeDict dictionaries with English and Tatoeba sentences (more languages)"),
        ("word", "languages", "Tatoeba sentences for the first 16 languages and Wikivoyage phrasebooks"),
        ("word", "wordnet", "Open English WordNet: an English dictionary and thesaurus"),
        ("link", "Wiktionary (in the Kiwix library)", "https://en.wiktionary.org/",
         "already in the Kiwix library; not rebuilt"),
        ("link", "Swadesh lists: the 100 and 207 basic words in hundreds of languages", SWADESH,
         "a Wiktionary appendix, in the Kiwix library's Wiktionary")]),
    ("Classical and constructed languages", "Old public-domain grammars and dictionaries.", [
        ("word", "lopen-classical", "Latin, Ancient Greek, Biblical Hebrew, Sanskrit, Old English and Esperanto"),
        ("link", "Lernu (Esperanto course)", "https://lernu.net/", "copyright of lernu.net; use it online")]),
    ("Sign languages", "Books whose words describe each sign, and where to learn current signs.", [
        ("word", "lopen-sign", "Old sign language books (1880 to 1926), marked historical"),
        ("pack", "commons_sign_language", "Sign language pictures, for the picture describer"),
        ("word", "dir:nidcd_health", "NIDCD's pages on American Sign Language and hearing"),
        ("link", "Spread the Sign", "https://www.spreadthesign.com/",
         "a sign language dictionary of many countries; non-commercial licence, so link-only"),
        ("link", "Lifeprint (ASL University)", "https://www.lifeprint.com/", "copyright of Bill Vicars; use online")]),
    ("Braille in other languages", "Braille codes of other countries.", [
        ("key", "lopen:braille_index", "Braille in other languages: the guide"),
        ("word", "lopen-braille", "Old books on braille and Moon type for other languages, as history")]),
]

BRAILLE_SECTIONS = [
    ("The world's braille codes", "Where each country's current braille code is published.", [
        ("link", "World Braille Usage, Third Edition (2013)",
         "https://www.govinfo.gov/content/pkg/GOVPUB-LC19-PURL-gpo38772/pdf/GOVPUB-LC19-PURL-gpo38772.pdf",
         "Perkins, ICEB, NLS and UNESCO: the alphabet and punctuation braille of 133 languages in 142 countries. "
         "Its copyright page says \"Copyright 1954, 1990 by UNESCO. Used by permission 2013\", so it is not taken "
         "as a US government work: link-only (download it yourself). Perkins warns its symbol charts are pictures "
         "that screen readers cannot read"),
        ("link", "Perkins: World Braille Usage page", "https://www.perkins.org/worldbraille",
         "Perkins's page for the book; open it in a browser"),
        ("link", "BANA: Guidelines for Braille Transcription of Languages Other Than English",
         "https://brailleauthority.org/sites/default/files/2023-01/Guidelines%20for%20Braille%20Transcription%20"
         "of%20Languages%20Other%20Than%20English.pdf", "copyright of the Braille Authority of North America"),
        ("link", "BANA: Provisional Guidance for Transcribing Foreign Language Material in UEB",
         "https://brailleauthority.org/foreign-language/Provisional%20Guidance%20for%20Transcribing%20Foreign%20"
         "Language%20Material%20in%20UEB.pdf", "copyright of the Braille Authority of North America")]),
    ("In the library", "Books already in the library that help with other languages' braille.", [
        ("key", "pdf:iceb_rules_of_ueb_2024", "Rules of Unified English Braille (ICEB, 2024): its foreign "
                                              "language section"),
        ("key", "atdoc:liblouis_tables", "liblouis's braille tables: the list of every language's table"),
        ("key", "atdoc:liblouis_manual", "The liblouis manual")]),
    ("History", "Old books on braille and embossed type for other languages.", [
        ("key", "lopen:braille_procede_1829", "Louis Braille's Procédé (1829)"),
        ("key", "lopen:oriental_braille_1902", "Oriental Braille (1902)"),
        ("key", "lopen:braille_usuel_1920", "Braille usuel (1920)"),
        ("key", "lopen:moon_light_for_the_blind_1877", "Moon's Light for the Blind (1877)")]),
]

INDEX = X.index_maker(PREFIX, GROUP, "Open language resources: a guide to the library", "Language learning",
                      "A guide to the open language-learning resources in the library: university textbooks, "
                      "readers, dictionaries, classical languages, sign languages and braille in other languages, "
                      "with the sources that are links only.", INDEX_SECTIONS, country="International")
BRAILLE_INDEX = X.index_maker("lopen_braille", GROUP, "Braille in other languages: a guide",
                              "Braille in other languages", "Where the world's braille codes are published, what "
                              "the library has for them, and old books on braille for other languages.",
                              BRAILLE_SECTIONS, country="International")

# ====================================================================== the collection

MAKERS = {
    "grammar": (grammar_book, grammar_sign), "wpcourse": (wp_course_book, wp_course_sign),
    "gsb": (gsb_book, gsb_sign), "gsbnc": (gsb_book, gsb_sign),
    "freedict": (freedict_book, freedict_sign), "tatoeba": (tatoeba_more_book, tatoeba_more_sign),
    "index": INDEX, "braille_index": BRAILLE_INDEX,
}
PIECES = {
    "grammar": lambda: list(GRAMMARS), "wpcourse": lambda: list(WP_COURSES),
    "gsb": lambda: list(GSB_LANGUAGES), "gsbnc": lambda: list(GSB_LANGUAGES),
    "freedict": lambda: list(FREEDICT_NAMES), "tatoeba": lambda: list(TATOEBA_MORE),
}


def _pieced(base):
    """The keys of every piece of one pieced maker."""
    return [f"{PREFIX}:{base}:{p}" for p in PIECES[base]()]


WORDS = {
    "lopen-textbooks": lambda: _pieced("grammar") + _pieced("wpcourse"),
    "lopen-readers": lambda: _pieced("gsb") + _pieced("gsbnc"),
    "lopen-dictionaries": lambda: _pieced("freedict") + _pieced("tatoeba"),
    "lopen-classical": lambda: [f"{PREFIX}:{p['name']}" for p in CLASSICAL],
    "lopen-sign": lambda: [f"{PREFIX}:{p['name']}" for p in SIGN],
    "lopen-braille": lambda: [f"{PREFIX}:braille_index"] + [f"{PREFIX}:{p['name']}" for p in BRAILLE],
}
WORDS["lang-open"] = lambda: list(dict.fromkeys(
    [f"{PREFIX}:index"] + [k for w in ("lopen-textbooks", "lopen-readers", "lopen-dictionaries", "lopen-classical",
                                       "lopen-sign", "lopen-braille") for k in WORDS[w]()]))

COLLECTION = K.Collection(PREFIX, GROUP, words=WORDS, pdfs=PDFS, makers=MAKERS, pieces=PIECES)

LICENCE_LINES = {
    "lopen_coerll": "COERLL (coerll.utexas.edu/coerll/materials/): Tex's French Grammar's index page links CC BY 3.0 "
                    "and Grimm Grammar's pages CC BY 4.0 (checked at every build); the K'iche' and Quechua courses "
                    "are \"License: CC-BY\" on COERLL's catalogue pages by language (checked at every build). The "
                    "sites' robots.txt allow programs (laits.utexas.edu and coerll.utexas.edu have none; the "
                    "WordPress sites disallow only /wp-admin/), checked 2026-11-23.",
    "lopen_gsb": "github.com/global-asp/global-asp: each language's README.md gives each story's licence (CC BY 3.0 "
                 "or 4.0, or CC BY-NC 3.0 or 4.0, read at every build; NC stories go into the personal-use book), "
                 "and each story's Markdown file repeats it; raw.githubusercontent.com has no robots.txt "
                 "(checked 2026-11-23).",
    "lopen_freedict": "download.freedict.org: each dictionary's licence is read from the <availability> of its own "
                      "TEI header at every build (GNU GPL 2 or later: share-alike; CC BY: open; anything else, and "
                      "Wiktionary-derived dictionaries, left out); freedict.org and download.freedict.org have no "
                      "robots.txt (checked 2026-11-23).",
    "lopen_tatoeba": "tatoeba.org/en/downloads (checked at every build): \"These files are released under CC BY 2.0 "
                     "FR\", as in languages.py.",
    "lopen_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                       "a later reprint is refused); Mallery (1880) is also a US government work; archive.org's "
                       "robots.txt allows the files (checked 2026-11-23).",
    "lopen_index": "The guides (lopen:index, lopen:braille_index) are the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("World Braille Usage, Third Edition (2013: Perkins, ICEB, NLS of the Library of Congress, UNESCO)", "Printed by "
     "NLS, but its copyright page says \"Copyright 1954, 1990 by UNESCO. Used by permission 2013\" and it was "
     "published with Perkins and ICEB, so it is not a plain US government work and no open licence is stated: "
     "link-only, from the braille guide (lopen:braille_index). Index: https://www.govinfo.gov/app/details/"
     "GOVPUB-LC19-PURL-gpo38772"),
    ("BANA's guidelines for braille in languages other than English", "Copyright of the Braille Authority of North "
     "America, no open licence; link-only from the braille guide. Index: https://brailleauthority.org/"),
    ("Pressbooks language textbooks (UT Austin's Hecho en Texas, Giornate Italiane, ClicaBrasil, Tako Lako, "
     "Tex's French Grammar's new edition; Portland State's Japanese and Arabic books; Boise State's Let's Chat ASL)",
     "pressbooks.pub's robots.txt says \"ai-train=no\", and the universities' Pressbooks networks (utexas, pdx, "
     "iu ...) answer programs with \"403\" (checked 2026-11-23). The ones in the Open Textbook Library are built by "
     "cat:otl when their PDF host allows it; Tex's French Grammar is built from its older site. Index: "
     "https://coerll.utexas.edu/coerll/materials/"),
    ("COERLL's Nahuatl course (Nāhuatlahtolli, CC BY-SA)", "Its lesson posts carry no text in the site's API (the "
     "lessons are videos and interactive exercises). Index: https://tlahtolli.coerll.utexas.edu/"),
    ("COERLL's media and exercise sites (Spanish in Texas, Brazilpod, Tá Falado, Reality Czech, Rockin' Russian, "
     "Tadriis, Chinese and Hindi media)", "Mostly videos, audio and interactive exercises; several are CC BY-NC-ND "
     "or CC BY-NC-SA. Link-only. Index: https://coerll.utexas.edu/coerll/materials/"),
    ("SIL International's Language and Culture Archives (literacy primers and language descriptions)", "No "
     "catalogue or download API, its site asks 10 seconds between requests, and each item has its own licence "
     "(most CC BY-NC-SA or CC BY-NC-ND): link-only for the owner to fetch what he wants. Index: "
     "https://www.sil.org/resources/language-culture-archives"),
    ("Bloom Library and Let's Read (picture books in many languages)", "Already recorded by read_aloud.py: no "
     "catalogue or download route open to programs (Bloom's robots.txt refuses /player/ and /readBook/). Linked "
     "from lopen:index. Index: https://bloomlibrary.org/"),
    ("FreeDict's Wiktionary-derived dictionaries (WikDict: eng-spa, eng-rus, eng-ita, eng-fin ...)", "Made from "
     "Wiktionary, which is already in the Kiwix library (the owner's rule: link, don't rebuild). Index: "
     "https://freedict.org/downloads/"),
    ("Open Multilingual Wordnet", "Its wordnets list word senses for linguists rather than a learner's entries, its "
     "data is published as GitHub release files (GitHub's robots.txt refuses programs there) and the licences "
     "differ by language; FreeDict and Tatoeba cover the bilingual word lists. Index: https://omwn.org/"),
    ("Language Science Press (open grammars of many languages, CC BY)", "Descriptive linguistics rather than "
     "learner books; Zenodo, where it deposits them, refuses programs in /api (robots.txt). Could be added from "
     "langsci-press.org's own catalogue with its 5-second pause. Index: https://langsci-press.org/catalog"),
    ("Lernu (Esperanto course)", "\"© 2002-2026 lernu.net\", no open licence; link-only from lopen:index. The "
     "Fundamento de Esperanto, a 1910 grammar and two 1907 dictionaries are built. Index: https://lernu.net/"),
    ("Spread the Sign and Lifeprint (sign language dictionaries with videos)", "Spread the Sign is under a "
     "non-commercial licence and is videos; Lifeprint is copyright of Bill Vicars. Link-only from lopen:index. "
     "Index: https://www.spreadthesign.com/"),
    ("Swadesh lists", "A Wiktionary appendix, already in the Kiwix library's Wiktionary; linked from lopen:index. "
     "Index: " + SWADESH),
    ("Global Storybooks' French, Portuguese, Swahili and other African-language stories", "They are the African "
     "Storybook's own stories, already built by read_aloud.py (readaloud:african_storybook). Index: "
     "https://github.com/global-asp/asp-source"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
