"""Whole open catalogues for the textbooks release (the owner's request of 2026-11-21: every legally available open or
public-domain book on the library's topics, non-commercial ones as personal use only, deduplicated).

Three catalogues are read here, each as build keys cat:<source>:<piece> (one piece is one workflow job):

  obp   Open Book Publishers: every active book (monographs, edited books, textbooks) in Thoth, its official open
        metadata service (api.thoth.pub, GraphQL; no robots.txt). Each book's PDF is read from the Internet Archive
        copy that Open Book Publishers itself deposited and lists in Thoth (books.openbookpublishers.com answers
        automated requests with a bot check, so it is never read). CC BY, CC BY-SA and CC0 books are open;
        CC BY-NC and CC BY-NC-SA ones are "personal use only"; NoDerivatives books are left out.
  otl   The Open Textbook Library (University of Minnesota): its catalogue is read from catalogues/otl.json, a
        snapshot made by tools/snapshot_otl.py from its JSON API, two minutes apart as its robots.txt asks
        (Crawl-delay: 120); each book's own PDF is read from its own host where that host's robots.txt allows it and
        does not shut out AI companies' readers. Books also in LibreTexts, OpenStax or BCcampus (built from those
        sources), GNU-licensed and NoDerivatives books are left out.
  ia    The Internet Archive's texts on the library's topics (IA_TOPICS), found with its advanced search API, in
        three kinds per topic: "cc" (items whose licenceurl is CC BY, CC BY-SA, CC0, or CC BY-NC(-SA) as personal
        use, and whose own first pages state a Creative Commons licence without NoDerivatives), "old" (published
        before 1931, checked by the builder at every build) and "usgov" (published by the US Government Printing
        Office or a US department after 1930: works of the US government). The best-read IA_PER_PIECE books of each
        are taken; catalogues, price lists, reports, journals and magazines are left out.

Every book is deduplicated before it is built: against the library's own books (the LibreTexts and OpenStax
catalogues and every entry of sources.py) and across the three catalogues and their editions (normalised titles:
"Introduction to Sociology, 2nd edition" = "Introduction to Sociology"; the newest edition is kept).

Pressbooks Directory, eCampusOntario, BCcampus' own site, Saylor and the GPO bookstore were looked at and could not be
read (see NOT_INCLUDED); BCcampus comes through its Kolibri channel (courses.py) and Wikisource and Project Gutenberg
through the Kiwix library.

Run from the repository's folder:
    python3 textbooks/build_textbooks.py cat:obp:3 --out build/textbooks
"""

import datetime
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import zlib

import build_textbooks as B
import sources

HERE = os.path.dirname(os.path.abspath(__file__))
OTL_SNAPSHOT = os.path.join(HERE, "catalogues", "otl.json")
THOTH = "https://api.thoth.pub/graphql"
OBP_PUBLISHER = "85fd969a-a16c-480b-b641-cb9adf979c3b"   # Open Book Publishers' id in Thoth
IA_SEARCH = "https://archive.org/advancedsearch.php"
TIME_BUDGET = 3.4 * 3600         # seconds one piece may take (the job's limit is 4 hours)
OBP_PIECES = 16
OTL_PIECES = 40
IA_PER_PIECE = 30                # books taken per Internet Archive piece (topic and kind)

US_GOV = sources.US_GOV
US_GOV_URL = sources.US_GOV_URL
OLD_LICENCE = "Public domain (published before 1931)"
OLD_URL = "https://www.copyright.gov/help/faq/faq-duration.html"
PD_MARK = "https://creativecommons.org/publicdomain/mark/1.0/"

# A Creative Commons statement in a PDF's first pages, without any NoDerivatives words (checked by pdfdoc_book).
CC_IN_PDF = r"(?is)^(?!.*(?:no\s*-?\s*deriv|by-nc-nd|by-nd|\bND\s+\d\.\d)).*(?:creative\s*commons|creativecommons\.org)"


# ====================================================================== licences

def cc_short(url_or_name):
    """The short licence of a Creative Commons address or name ("https://creativecommons.org/licenses/by-nc/4.0/"
    or "Attribution-NonCommercial" -> "CC BY-NC 4.0"; CC0; "PD" for the public domain mark), "" for anything else
    (NoDerivatives, GNU, unknown)."""
    text = (url_or_name or "").strip()
    m = re.search(r"creativecommons\.org/licenses/([a-z-]+)/(\d\.\d)", text, re.I)
    if m:
        kind, version = m.group(1).lower(), m.group(2)
        return "" if "nd" in kind.split("-") else f"CC {kind.upper()} {version}"
    if re.search(r"publicdomain/zero", text, re.I):
        return "CC0 1.0"
    if re.search(r"publicdomain/mark", text, re.I):
        return "PD"
    names = {"attribution": "CC BY", "attribution-sharealike": "CC BY-SA", "attribution-noncommercial": "CC BY-NC",
             "attribution-noncommercial-sharealike": "CC BY-NC-SA", "public domain": "PD", "cc0": "CC0 1.0"}
    return names.get(text.lower().replace(" ", ""), names.get(text.lower(), ""))


def licence_url(short):
    """The address of a short licence."""
    if short == "PD":
        return PD_MARK
    if short.startswith("CC0"):
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    m = re.match(r"CC ([A-Z-]+)(?: (\d\.\d))?", short)
    return f"https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2) or '4.0'}/" if m else ""


def personal(short):
    """True for a non-commercial licence (the owner's rule: personal use only)."""
    return "NC" in short.split(" ")[1].split("-") if short.startswith("CC ") else False


def bucket(text, n):
    """A stable bucket (0 .. n-1) of a name."""
    return zlib.crc32(text.encode("utf-8")) % max(1, n)


# ====================================================================== deduplication

EDITION = re.compile(r"\b(\d+(st|nd|rd|th)?|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
                     r"revised|updated|new|expanded)\s+(edition|ed\.?)\b|\b\d+e\b|\bedition\s+\d+(\.\d+)?\b|"
                     r"\bversion\s+\d+(\.\d+)*\b|\bv\d+(\.\d+)*\b|\(\s*[^)]*\)|\[\s*[^\]]*\]", re.I)


def norm_title(title):
    """A title made comparable across editions and catalogues: lower case, without its edition words, bracketed
    notes, subtitle (after ":"), a leading "OpenStax " and punctuation. "Introduction to Sociology 3e" and
    "Introduction to Sociology (Second Edition): A Canadian view" -> "introduction to sociology"."""
    t = html.unescape(title or "")
    t = re.sub(r"^\s*openstax\s+", "", t, flags=re.I)
    t = t.split(":")[0]
    t = EDITION.sub(" ", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t.lower().replace("&", " and "))
    t = re.sub(r"^(the|a|an) ", "", " ".join(t.split()))
    return t


STOP = {"the", "and", "for", "with", "its", "from", "into", "their", "his", "her", "our", "your", "all", "how"}


def title_keys(title):
    """The keys a title is known by: its normalised title, and the set of its words (three letters or more, without
    small words and numbers), so that "TM 10-412 Army Recipes 1944" and "Army Recipes, TM 10-412" are one book."""
    norm = norm_title(title)
    words = sorted({w for w in re.findall(r"[a-z]{3,}", norm_title(title.replace(":", " "))) if w not in STOP})
    return {k for k in (norm, "w:" + " ".join(words) if len(words) >= 2 else "") if k}


def is_duplicate(title, titles):
    """True when a title is already among titles (a set of title_keys)."""
    return bool(title_keys(title) & titles)


def library_titles(cache=None):
    """The normalised titles of the books the library already builds from its other sources: every LibreTexts book
    with a usable licence, every OpenStax book, and every entry of sources.py (PDFs, guides, laws, web books)."""
    names = []
    try:
        import courses                               # here, not at the top: courses imports the builder
        names += [b.get("title", "") for b in courses.lt_catalogue() if courses.lt_licence(b)[0]]
    except Exception:  # noqa: BLE001 - deduplicated against what could be read
        pass
    names += [item.get("title", "") for item in B.openstax_catalogue(cache).values()]
    import cookbooks                                 # (its books are not in sources.py's lists)
    for e in sources.PDF_DOCS + sources.NONPROFIT + sources.GOV_GUIDES + sources.K12_GUIDES + cookbooks.BOOKS:
        names.append(re.sub(r"\s*\([^)]*\)\s*$", "", e["title"]))
    titles = set()
    for name in names:
        titles |= title_keys(name)
    return titles


# ====================================================================== Open Book Publishers (Thoth)

_MEMO = {}

THOTH_QUERY = ("{ works(limit: 2000, publishers: [\"%s\"], workTypes: [MONOGRAPH, EDITED_BOOK, TEXTBOOK], "
               "workStatuses: [ACTIVE]) { workId fullTitle workType license publicationDate updatedAt doi landingPage "
               "longAbstract languages { languageCode languageRelation } subjects { subjectType subjectCode "
               "subjectOrdinal } contributions { fullName "
               "contributionType contributionOrdinal } publications { publicationType locations { fullTextUrl "
               "landingPage locationPlatform } } } }" % OBP_PUBLISHER)


def obp_works():
    """Every active Open Book Publishers book in Thoth (read once per run, never from the cache folder)."""
    if "obp" not in _MEMO:
        import urllib.request
        req = urllib.request.Request(THOTH, data=json.dumps({"query": THOTH_QUERY}).encode(),
                                     headers={"Content-Type": "application/json", "User-Agent": B.USER_AGENT})
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read())
        if data.get("errors"):
            raise ValueError(f"Thoth answered with an error: {data['errors'][0].get('message')}")
        _MEMO["obp"] = data["data"]["works"]
    return _MEMO["obp"]


def obp_archive_pdf(work):
    """(PDF address, Internet Archive item page) of a work's Internet Archive copy, or ("", "")."""
    for pub in work.get("publications") or []:
        if pub.get("publicationType") != "PDF":
            continue
        for loc in pub.get("locations") or []:
            if loc.get("locationPlatform") == "INTERNET_ARCHIVE" and (loc.get("fullTextUrl") or "").endswith(".pdf"):
                return loc["fullTextUrl"], loc.get("landingPage") or loc["fullTextUrl"]
    return "", ""


def obp_entry(work):
    """A pdfdoc_book entry for one Open Book Publishers work, or (None, reason)."""
    short = cc_short(work.get("license") or "")
    if not short or short == "PD":
        return None, f"Its licence ({work.get('license') or 'none stated'}) is not one the toolkit may repackage " \
                     "(NoDerivatives or none)."
    pdf, page = obp_archive_pdf(work)
    if not pdf:
        return None, "Thoth lists no Internet Archive copy of its PDF (the publisher's own site is behind a bot check)."
    authors = ", ".join(c["fullName"] for c in sorted(work.get("contributions") or [],
                                                      key=lambda c: c.get("contributionOrdinal") or 0)
                        if c.get("contributionType") in ("AUTHOR", "EDITOR"))
    keywords = [s["subjectCode"] for s in sorted(work.get("subjects") or [], key=lambda s: s.get("subjectOrdinal") or 0)
                if s.get("subjectType") == "KEYWORD"]
    doi = (work.get("doi") or "").rsplit("/", 1)[-1]
    name = "obp_" + re.sub(r"[^a-z0-9]+", "_", doi.lower().replace("obp.", "")) if doi else \
        "obp_" + work["workId"].replace("-", "")[:12]
    abstract = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", work.get("longAbstract") or "")).split())
    langs = [x["languageCode"].lower() for x in sorted(work.get("languages") or [], key=lambda x: x.get(
        "languageRelation") != "TRANSLATED_INTO") if x.get("languageRelation") in ("ORIGINAL", "TRANSLATED_INTO")]
    return dict(name=name, language=langs[0] if langs else "eng",
                title=work["fullTitle"] + (f" ({authors})" if authors and len(authors) < 80 else ""),
                subject=(keywords[0].capitalize() if keywords else "Humanities and social sciences"),
                group="university", level="college", publisher="Open Book Publishers" +
                (f" ({authors})" if authors else ""), country="United Kingdom", licence=short,
                licence_url=licence_url(short), personal_use=personal(short), pdf=pdf,
                page=work.get("landingPage") or page, published=work.get("publicationDate") or "",
                pdf_licence_text=CC_IN_PDF,
                description=(abstract[:700] + ("..." if len(abstract) > 700 else "")) or work["fullTitle"],
                changes="its PDF's text made into web pages, one per chapter (read from the copy Open Book Publishers "
                        "deposited at the Internet Archive)",
                notice=f"Published by Open Book Publishers under {short}" + (f"; DOI {work['doi']}" if
                                                                            work.get("doi") else "") + "."), ""


def obp_items(piece, titles):
    """(entries, left_out) of one Open Book Publishers piece ("3"), newest edition of each title, deduplicated."""
    entries, left = [], []
    works = sorted(obp_works(), key=lambda w: w.get("publicationDate") or "", reverse=True)
    seen = set()
    for w in works:
        keys = title_keys(w["fullTitle"])
        if keys & seen:
            continue                                      # an older edition of a book already taken
        seen |= keys
        if bucket(w["workId"], OBP_PIECES) != int(piece):
            continue
        if is_duplicate(w["fullTitle"], titles):
            left.append({"title": w["fullTitle"], "reason": "Already in the library from another source."})
            continue
        entry, why = obp_entry(w)
        if entry is None:
            left.append({"title": w["fullTitle"], "reason": why})
        else:
            entries.append(entry)
    return entries, left


# ====================================================================== the Open Textbook Library (snapshot)

OTL_SKIP_HOSTS = re.compile(r"(^|\.)(libretexts\.org|openstax\.org|opentextbc\.ca|bccampus\.ca|pressbooks\.pub|"
                            r"amazon\.com|lulu\.com|oercommons\.org|google\.com)$")


def otl_books():
    """The Open Textbook Library's books from the snapshot (catalogues/otl.json), [] when there is none yet."""
    if not os.path.exists(OTL_SNAPSHOT):
        return []
    with open(OTL_SNAPSHOT, encoding="utf-8") as f:
        return json.load(f).get("books", [])


def otl_pdf(book):
    """The address of the book's own PDF (a PDF format whose address ends in .pdf, on a host that is not one of
    the sources built elsewhere), or ""."""
    for f in book.get("formats", []):
        url = f.get("url") or ""
        host = urllib.parse.urlsplit(url).hostname or ""
        if f.get("type") == "PDF" and re.search(r"\.pdf($|\?)", url, re.I) and not OTL_SKIP_HOSTS.search(host):
            return url
    return ""


def otl_entry(book):
    """A pdfdoc_book entry for one Open Textbook Library book, or (None, reason)."""
    short = cc_short(book.get("license") or "")
    if not short:
        return None, f"Its licence ({book.get('license')}) is not one the toolkit may repackage (NoDerivatives, " \
                     "GNU or other)."
    hosts = {urllib.parse.urlsplit(f.get("url") or "").hostname or "" for f in book.get("formats", [])}
    if any(re.search(r"libretexts\.org$|openstax\.org$|opentextbc\.ca$|bccampus\.ca$", h) for h in hosts):
        return None, "Built from LibreTexts, OpenStax or BCcampus (another source of the library)."
    pdf = otl_pdf(book)
    if not pdf:
        return None, "The Open Textbook Library lists no PDF of it on a host the builder may read (Pressbooks sites " \
                     "refuse automated requests)."
    authors = ", ".join(c.get("name", "") for c in book.get("contributors", [])[:4])
    subjects = [s.get("name", "") for s in book.get("subjects", [])]
    publisher = ", ".join(p.get("name", "") for p in book.get("publishers", [])) or "Open Textbook Library"
    year = str(book.get("copyright_year") or "")
    return dict(name=f"otl_{book['id']}", title=book["title"] + (f" ({authors})" if authors and len(authors) < 80
                                                                 else ""),
                subject=subjects[0] if subjects else "General", group="textbooks", level="college",
                publisher=publisher + (f" ({authors})" if authors else ""), country="United States",
                licence=short, licence_url=licence_url(short), personal_use=personal(short),
                pdf=pdf, page=f"https://open.umn.edu/opentextbooks/textbooks/{book['id']}", published=year,
                pdf_licence_text=CC_IN_PDF if short.startswith("CC") else "",
                description=(book.get("description") or book["title"])[:700],
                changes="its PDF's text made into web pages, one per chapter (found through the Open Textbook "
                        "Library)"), ""


def otl_items(piece, titles):
    """(entries, left_out) of one Open Textbook Library piece, newest edition of each title, deduplicated."""
    entries, left, seen = [], [], set()
    books = sorted(otl_books(), key=lambda b: b.get("copyright_year") or 0, reverse=True)
    for b in books:
        keys = title_keys(b["title"])
        if keys & seen:
            continue                                      # an older edition of a book already taken
        seen |= keys
        if bucket(str(b["id"]), OTL_PIECES) != int(piece):
            continue
        if is_duplicate(b["title"], titles):
            left.append({"title": b["title"], "reason": "Already in the library from another source."})
            continue
        entry, why = otl_entry(b)
        if entry is None:
            left.append({"title": b["title"], "reason": why})
        else:
            entries.append(entry)
    return entries, left


# ====================================================================== the Internet Archive, by topic

# Topic key -> (the library's topic, the toolkit's group, the Internet Archive search words for it). Sewing, art and
# drawing, and crafts are in "Reference, arts and crafts" (group "crafts", crafts_books.py), the one top-level group
# for crafts (the owner's request of 22 November 2026). Foreign languages are in "Languages" (group "languages",
# languages.py), the top-level section for language learning (the owner's request of 23 November 2026).
IA_TOPICS = {
    "birds": ("Birds", "science", 'subject:(birds OR ornithology)'),
    "mammals": ("Mammals", "science", 'subject:(mammals)'),
    "reptiles": ("Reptiles and amphibians", "science", 'subject:(reptiles OR amphibians OR herpetology)'),
    "insects": ("Insects and spiders", "science", 'subject:(insects OR entomology OR spiders OR beekeeping)'),
    "fish": ("Fish and marine life", "science", 'subject:(fishes OR "marine biology" OR shellfish)'),
    "plants": ("Plants, trees and wildflowers", "science", 'subject:(botany OR trees OR "wild flowers" OR mushrooms)'),
    "gardening": ("Gardening and growing food", "science", 'subject:(gardening OR horticulture OR vegetables)'),
    "farming": ("Farming and livestock", "science", 'subject:(agriculture OR livestock OR poultry OR dairying)'),
    "weather": ("Weather and climate", "science", 'subject:(meteorology OR weather OR climatology)'),
    "geology": ("Earth science and geology", "science", 'subject:(geology OR mineralogy OR volcanoes)'),
    "astronomy": ("Astronomy and space", "science", 'subject:(astronomy OR "outer space")'),
    "maps": ("Maps, navigation and charts", "government", 'subject:(navigation OR cartography OR "map reading")'),
    "boating": ("Boating and seamanship", "reference", 'subject:(seamanship OR sailing OR boats OR yachting)'),
    "sewing": ("Sewing, knitting and needlework", "crafts", 'subject:(sewing OR dressmaking OR knitting OR '
              'needlework OR crocheting OR embroidery)'),
    "woodworking": ("Woodworking and carpentry", "reference", 'subject:(woodwork OR carpentry OR cabinetwork)'),
    "home": ("Home repair and housekeeping", "reference", 'subject:("home economics" OR housekeeping OR plumbing '
             'OR "dwellings maintenance")'),
    "cooking": ("Cooking", "cookbooks", 'subject:(cooking OR cookery OR recipes)'),
    "nutrition": ("Nutrition and diet", "health", 'subject:(nutrition OR diet)'),
    "first_aid": ("First aid and home nursing", "health", 'subject:("first aid" OR "home nursing")'),
    "health": ("Health and hygiene", "health", 'subject:(hygiene OR "public health" OR health)'),
    "fitness": ("Exercise and fitness", "health", 'subject:("physical education" OR exercise OR gymnastics)'),
    "blindness": ("Braille and blindness", "disability", 'subject:(braille OR blindness OR "blind, education" OR '
                  '"visually handicapped" OR "blind -- education")'),
    "deafness": ("Sign language and deafness", "disability", 'subject:(deaf OR "sign language")'),
    "music": ("Music", "reference", 'subject:("music theory" OR harmony OR "music instruction")'),
    "art": ("Art and drawing", "crafts", 'subject:(drawing OR painting OR "art instruction")'),
    "crafts": ("Crafts and hobbies", "crafts", 'subject:(handicraft OR basketry OR leatherwork OR pottery)'),
    "games": ("Games, chess and puzzles", "reference", 'subject:(chess OR checkers OR games OR puzzles)'),
    "pets": ("Pets and animal care", "science", 'subject:(dogs OR cats OR pets OR "veterinary medicine")'),
    "money": ("Personal finance and money", "consumer", 'subject:("personal finance" OR budgets OR thrift OR '
              'consumer)'),
    "law": ("Law and rights", "law", 'subject:(law OR "civil rights" OR constitution)'),
    "history": ("History", "history", 'subject:("united states history" OR "world history")'),
    "english": ("Writing, grammar and English usage", "reference", 'subject:("english language" OR grammar OR '
                'composition OR rhetoric)'),
    "languages": ("Languages (foreign)", "languages", 'subject:("spanish language" OR "french language" OR '
                  '"german language" OR "latin language")'),
    "mathematics": ("Mathematics", "textbooks", 'subject:(mathematics OR arithmetic OR algebra OR geometry)'),
    "science": ("Physics and chemistry", "textbooks", 'subject:(physics OR chemistry)'),
    "electricity": ("Electricity and electronics", "reference", 'subject:(electricity OR electronics OR radio)'),
    "engines": ("Engines, cars and machines", "reference", 'subject:(automobiles OR engines OR machinery)'),
    "trades": ("Trades and building", "reference", 'subject:(building OR masonry OR welding OR blacksmithing)'),
    "aviation": ("Aviation", "government", 'subject:(aeronautics OR aviation OR airplanes)'),
    "outdoors": ("Survival and outdoor skills", "fieldmanual", 'subject:(camping OR woodcraft OR "outdoor life" OR '
                 'scouting)'),
    "parenting": ("Parenting and child care", "health", 'subject:("child care" OR "infants care" OR parenting)'),
    # Teaching and homeschooling (the owner's request of 23 November 2026, group key "k12"): teaching methods, school
    # readers and primers, and homeschooling.
    "teaching": ("Teaching and homeschooling", "k12", 'subject:(teaching OR "home schooling" OR homeschooling OR '
                 '"readers (primary)" OR primers OR "education -- study and teaching")'),
    "philosophy": ("Philosophy and religion", "reference", 'subject:(philosophy OR religion OR ethics)'),
    "psychology": ("Psychology", "reference", 'subject:(psychology)'),
    "economics": ("Economics and business", "reference", 'subject:(economics OR business OR accounting)'),
    "geography": ("Geography and travel", "reference", 'subject:(geography OR travel)'),
    "literature": ("Literature and poetry", "reference", 'subject:(poetry OR literature OR drama)'),
}
IA_KINDS = ("cc", "old", "usgov")
IA_NOT_BOOKS = re.compile(r"\b(catalog(ue)?s?|price[- ]lists?|annual report|report of|reports|proceedings|"
                          r"transactions|journal|magazine|bulletin|newsletter|yearbook of the|directory|"
                          r"minutes|hearings?|register|calendar|census|statistics of|index to|abstracts?|finding list|"
                          r"vanity fair|leaves|digest|review)\b", re.I)
GOV_PUBLISHER = re.compile(r"Government Printing Office|Govt\.? Print\.? Off|G\.\s?P\.\s?O\.|U\.\s?S\.\s?Dept|"
                           r"United States\.? Dep(artmen)?t|U\.S\. Government", re.I)


def ia_query(topic, kind):
    """The Internet Archive advanced-search query of one topic and kind."""
    words = IA_TOPICS[topic][2]
    base = f"({words}) AND mediatype:texts AND -access-restricted-item:true AND language:(eng OR English)"
    if kind == "cc":
        return base + " AND licenseurl:*creativecommons* AND -collection:(opensource OR jstor_ejc OR biostor)"
    if kind == "old":
        return base + " AND date:[1800-01-01 TO 1930-12-31]"
    return base + (' AND publisher:("Government Printing Office" OR "Govt. Print. Off." OR "G.P.O." OR "U.S. Dept")'
                   " AND date:[1931-01-01 TO 2026-12-31]")


def ia_search(topic, kind, cache=None, rows=200):
    """The search's items (dicts with identifier, title, date, creator, publisher, licenseurl, downloads), best read
    first."""
    fields = ["identifier", "title", "date", "creator", "publisher", "licenseurl", "downloads", "language",
              "collection", "volume", "issue"]
    url = IA_SEARCH + "?" + urllib.parse.urlencode([("q", ia_query(topic, kind))] + [("fl[]", f) for f in fields] +
                                                   [("rows", rows), ("sort[]", "downloads desc"),
                                                    ("output", "json")])
    key = ("ia", topic, kind)
    if key not in _MEMO:
        _MEMO[key] = json.loads(B.fetch(url, None)).get("response", {}).get("docs", [])
    return _MEMO[key]


def _first(value):
    """The first of a metadata value that may be a list."""
    return (value[0] if isinstance(value, list) and value else value) or ""


def ia_entry(doc, topic, kind):
    """A pdfdoc_book entry for one Internet Archive item, or (None, reason)."""
    title = " ".join(str(_first(doc.get("title"))).split())
    year = re.search(r"(1[5-9]\d\d|20\d\d)", str(_first(doc.get("date"))))
    year = int(year.group(1)) if year else 0
    creator, publisher = str(_first(doc.get("creator"))), str(_first(doc.get("publisher")))
    collections = " ".join(doc.get("collection") if isinstance(doc.get("collection"), list) else
                           [str(doc.get("collection") or "")])
    if IA_NOT_BOOKS.search(title) or doc.get("volume") or doc.get("issue") or \
            re.search(r"serials|periodicals|magazine|newspaper|journals", collections, re.I):
        return None, "A catalogue, report, journal, magazine or other periodical, not a book."
    name_topic, group, _words = IA_TOPICS[topic]
    base = dict(name="ia_" + re.sub(r"[^a-z0-9]+", "_", doc["identifier"].lower())[:60], title=title +
                (f" ({creator.split(',')[0]}, {year})" if creator and year else f" ({year})" if year else ""),
                subject=name_topic, group=group, level="reference", archive=doc["identifier"],
                publisher=" ".join(f"{creator} ({publisher})".split()) if creator else publisher or "Unknown",
                country="United States", published=str(year or ""))
    if kind == "cc":
        if not creator or not year:
            return None, "Its record names no author or no year (an anonymous upload is not taken on its word)."
        short = cc_short(str(_first(doc.get("licenseurl"))))
        if not short or short == "PD":
            return None, f"Its licence ({_first(doc.get('licenseurl'))}) is not a Creative Commons licence the " \
                         "toolkit " \
                         "may repackage."
        return dict(base, licence=short, licence_url=licence_url(short), personal_use=personal(short),
                    pdf_licence_text=CC_IN_PDF, ia_licence=short,
                    description=f"{title}, an openly licensed text from the Internet Archive ({short}, as its record "
                                "and its own first pages state).",
                    changes="its PDF's text made into web pages"), ""
    if kind == "old":
        if not year or year >= 1931:
            return None, "Its record does not show it was published before 1931."
        return dict(base, licence=OLD_LICENCE, licence_url=OLD_URL, old_public_domain=True,
                    description=f"{title}. Published in {year}: an old book whose facts, advice and laws are out of "
                                "date; the machine-read text has the scanner's mistakes.",
                    changes="its scanned pages' machine-read text (with the scanner's mistakes) made into web "
                            "pages"), ""
    if not GOV_PUBLISHER.search(publisher):
        return None, "Its record does not show a US government publisher."
    return dict(base, licence=US_GOV, licence_url=US_GOV_URL, ia_usgov=True,
                licence_page=sources.GOVINFO_POLICY, licence_text=sources.GOVINFO_TEXT,
                description=f"{title}: a publication of the US government ({publisher}, {year or 'year not stated'}); "
                            "its facts, advice and laws may be out of date.",
                changes="its PDF's text made into web pages"), ""


def ia_items(piece, titles, cache=None):
    """(entries, left_out) of one Internet Archive piece ("old-birds"): its best-read IA_PER_PIECE books not already
    in the library, one per title."""
    kind, _, topic = piece.partition("-")
    entries, left, seen = [], [], set()
    for doc in ia_search(topic, kind, cache):
        if len(entries) >= IA_PER_PIECE:
            break
        title = str(_first(doc.get("title")))
        keys = title_keys(title)
        if not keys or keys & seen:
            continue                                      # another copy or edition of a book already taken
        seen |= keys
        if is_duplicate(title, titles):
            left.append({"title": title, "reason": "Already in the library from another source."})
            continue
        entry, why = ia_entry(doc, topic, kind)
        if entry is None:
            left.append({"title": title, "reason": why})
        else:
            entries.append(entry)
    return entries, left


def ia_licence_still_stated(entry, cache=None):
    """For an openly licensed Internet Archive item: True when the item's record still gives the same licence."""
    meta = json.loads(B.fetch(f"https://archive.org/metadata/{entry['archive']}", None)).get("metadata", {})
    return cc_short(str(_first(meta.get("licenseurl")))) == entry["ia_licence"]


# ====================================================================== keys, signs, the build

SOURCES = {
    "obp": dict(title="Open Book Publishers (Thoth)", pieces=lambda: [str(i) for i in range(OBP_PIECES)],
                release=lambda piece: "catalogue-obp"),
    "otl": dict(title="Open Textbook Library", pieces=lambda: [str(i) for i in range(OTL_PIECES)],
                release=lambda piece: f"catalogue-otl-{int(piece) // 10}"),
    "ia": dict(title="Internet Archive by topic", pieces=lambda: [f"{k}-{t}" for k in IA_KINDS for t in IA_TOPICS],
               release=lambda piece: f"catalogue-ia-{piece.partition('-')[0]}-{bucket(piece, 4)}"),
}


def expand_keys(words):
    """The build keys (cat:<source>:<piece>) of "catalogues" (every source), cat:<source> or cat:<source>:<piece>."""
    keys = []
    for w in words:
        if w == "catalogues":
            names = list(SOURCES)
        elif w.startswith("cat:") and w.count(":") == 1:
            names = [w[4:]]
        else:
            keys.append(w)
            continue
        for name in names:
            keys += [f"cat:{name}:{p}" for p in SOURCES[name]["pieces"]()]
    return list(dict.fromkeys(keys))


def items_of(key, titles, cache=None):
    """(entries, left_out) of one key."""
    _cat, name, piece = key.split(":", 2)
    if name == "obp":
        return obp_items(piece, titles)
    if name == "otl":
        return otl_items(piece, titles)
    if name == "ia":
        return ia_items(piece, titles, cache)
    raise KeyError(f"unknown catalogue {name}")


def sign(key):
    """The weekly check's sign of change of a key ("" when it cannot be asked): the piece's books in Thoth with their
    dates of change; the piece's books in the Open Textbook Library snapshot (and the quarter of the year, so they
    are read again four times a year); the identifiers an Internet Archive search finds."""
    _cat, name, piece = key.split(":", 2)
    try:
        if name == "obp":
            rows = sorted((w["workId"], w.get("updatedAt") or "", w.get("license") or "") for w in obp_works()
                          if bucket(w["workId"], OBP_PIECES) == int(piece))
        elif name == "otl":
            today = datetime.date.today()
            rows = [sorted((b["id"], b.get("license"), [f.get("url") for f in b.get("formats", [])])
                           for b in otl_books() if bucket(str(b["id"]), OTL_PIECES) == int(piece)),
                    f"{today.year}-Q{(today.month - 1) // 3 + 1}"]
        else:
            kind, _, topic = piece.partition("-")
            rows = [d["identifier"] for d in ia_search(topic, kind)][:IA_PER_PIECE * 3]
        return hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:24]
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return ""


def make_book(entry, work, cache=None, left_out=None):
    """The Book of one entry (pdfdoc_book), after the checks pdfdoc_book does not make itself: the PDF's host allows
    reading and does not shut out AI companies' readers; an openly licensed Internet Archive item still states its
    licence."""
    import cookbooks                                     # its robots.txt check for AI readers (ai_refused)
    url = entry.get("pdf") or f"https://archive.org/metadata/{entry.get('archive')}"
    if not cookbooks.readable(url, cache):
        left_out.append({"title": entry["title"], "reason": "Its host's robots.txt does not allow reading it, or shuts "
                         "out AI companies' readers."})
        return None
    if entry.get("ia_licence") and not ia_licence_still_stated(entry, cache):
        left_out.append({"title": entry["title"], "reason": "Its Internet Archive record no longer gives the licence "
                         "that was checked."})
        return None
    book = B.pdfdoc_book(entry, work, cache, left_out)
    if book is not None:
        book.language = entry.get("language") or "eng"
    if book is not None and entry.get("ia_usgov"):
        book.notice = "A work of the US government, not under copyright in the United States (17 U.S.C. 105)."
    return book


def build_catalogues(keys, out_dir, cache=None, date=None, only=None):
    """Build the books of keys (cat:...) into out_dir and write manifest-<key>.json for each, as courses.build_courses
    does. only: just these book names (a test build, its manifest named "..._sample")."""
    manifests = {}
    os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(cache or out_dir, "work", "catalogues")
    titles = None
    for key in expand_keys(keys):
        name, piece = key.split(":")[1], key.split(":", 2)[2]
        release = SOURCES[name]["release"](piece)
        left_out, entries_out = [], []
        start = time.monotonic()
        fingerprint = sign(key) if not only else ""
        try:
            if titles is None:
                titles = library_titles(cache)
            items, left = items_of(key, titles, cache)
            left_out += left
        except Exception as e:  # noqa: BLE001 - said in the manifest
            left_out.append({"title": key, "reason": f"It could not be built ({e})."})
            items = []
        if only:
            items = [e for e in items if e["name"] in only]
        for n, entry in enumerate(items):
            if time.monotonic() - start > TIME_BUDGET:
                rest = [e["title"] for e in items[n:]]
                left_out.append({"title": key, "reason": f"The time for one build ran out; not built this time "
                                 f"({len(rest)}): " + "; ".join(rest[:50]) + ("..." if len(rest) > 50 else "")})
                break
            try:
                book = make_book(entry, work, cache, left_out)
            except Exception as e:  # noqa: BLE001 - one book's failure does not stop the others
                left_out.append({"title": entry["title"], "reason": f"It could not be read ({e})."})
                book = None
            local = os.path.join(work, f"{entry['name']}.pdf")
            if os.path.exists(local):
                os.remove(local)                          # keep the build machine's disk free
            if book is None or not book.pages:
                continue
            out = B.write_book(book, out_dir, date, versioned=True)
            out.update({"key": key, "fingerprint": fingerprint, "release": release,
                        "url": f"{B.RELEASE.rsplit('/', 1)[0]}/{release}/{out['file']}"})
            print(f"{out['file']}: {out['article_count']} pages, {out['size']:,} bytes, {out['licence_text']}")
            entries_out.append(out)
        failed = [key] if any("could not be built" in x["reason"] for x in left_out) else []
        manifest = {"key": key, "release": release, "books": entries_out, "left_out": left_out,
                    "files": [e["file"] for e in entries_out], "failed": failed, "done": [] if failed else [key]}
        safe = re.sub(r"[^a-z0-9_-]+", "_", key.lower()) + ("_sample" if only else "")
        with open(os.path.join(out_dir, f"manifest-{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
        manifests[key] = manifest
    return manifests


# ====================================================================== what was checked, and what was not built

LICENCE_LINES = {
    "obp": "Thoth (api.thoth.pub), Open Book Publishers' official metadata: each work's \"license\" (for example "
           "\"https://creativecommons.org/licenses/by/4.0/\"); each PDF's own first pages are checked again at every "
           "build for a Creative Commons statement without NoDerivatives.",
    "otl": "The Open Textbook Library's JSON catalogue (open.umn.edu/opentextbooks/textbooks.json): each book's "
           "\"license\" (\"Attribution\", \"Attribution-ShareAlike\" ...); each PDF's own first pages are checked "
           "again "
           "for a Creative Commons statement without NoDerivatives. open.umn.edu's robots.txt: Crawl-delay 120.",
    "ia_catalogue": "Internet Archive item records: \"licenseurl\" (Creative Commons, checked again at every build "
                    "and in the PDF's first pages), \"date\" before 1931 (checked at every build), or a US government "
                    "publisher (17 U.S.C. 105, as quoted on govinfo.gov/about/policies).",
}

NOT_INCLUDED = [
    ("Pressbooks Directory (pressbooks.directory, 3,571 books)", "Its catalogue (its OPDS feed) was read on "
     "2026-11-21, but the books themselves cannot be: every *.pressbooks.pub site (1,676 books) answers automated "
     "requests with 403 (Pressbooks' CloudFront block), the institutions' own Pressbooks sites (Atlantic OER, "
     "SaskOER, Open Education Alberta, CAUL, Oregon State, CUNY, Rebus, Minnesota and some 70 others) answer 403 to "
     "robots.txt itself, and BCcampus' and the studium.pub sites shut out AI companies' readers with "
     "\"ai-train=no\". Their books are built where another route exists (LibreTexts, BCcampus through Kolibri, the "
     "Open Textbook Library's other hosts)."),
    ("eCampusOntario Open Library", "Its catalogue site answers, but every book is on ecampusontario.pressbooks.pub, "
     "which refuses automated requests (403), robots.txt included."),
    ("Open Book Publishers' own site (books.openbookpublishers.com, www.openbookpublishers.com)", "A bot check (AWS "
     "WAF \"Human Verification\") and 429 answers; its books are read from the Internet Archive copies it lists in "
     "Thoth instead (cat:obp). Its NoDerivatives books (about 90) are left out."),
    ("Saylor Academy's open textbooks", "resources.saylor.org refuses automated requests (403) and its course pages "
     "need a login; the older copies at saylordotorg.github.io are read where the Open Textbook Library lists them."),
    ("US Government Publishing Office bookstore's free e-books (bookstore.gpo.gov)", "The bookstore refuses automated "
     "requests (403), robots.txt included. US government books are taken from the agencies' own sites and from "
     "the Internet Archive's government documents (cat:ia:usgov-...)."),
    ("OpenStax books not on GitHub (Algebra 1, Clinical Nursing Skills, Fundamentals of Nursing, Maternal-Newborn "
     "Nursing, Medical-Surgical Nursing, Psychiatric-Mental Health Nursing, Introduction to Computer Science)",
     "openstax.org lists them, but OpenStax has not published their osbooks-* source repositories, and its own "
     "reader pages are not read; added when the repositories appear."),
    ("Wikisource and Project Gutenberg", "Already in the Kiwix library (wikisource_en_all and the gutenberg_en_lcc-* "
     "books by Library of Congress class), so their public-domain books are not built again here."),
    ("Wikibooks", "Already in the Kiwix library (wikibooks_en_all); only the drink books are built here."),
    ("Internet Archive items marked with the public domain mark by their uploaders", "Taken only when the item was "
     "published before 1931 or by the US government: an uploader's mark on a newer book is not proof."),
    ("Internet Archive items under NoDerivatives licences, and the \"opensource\" community uploads", "NoDerivatives "
     "works cannot be repackaged; community uploads often carry a licence their uploader could not give."),
]
