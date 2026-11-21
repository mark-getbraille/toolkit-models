"""More sources for the Writing Kit (added in November 2026 at the owner's request), kept in this one file so they are
easy to merge with other work on the kit. writing_sources.py adds SOURCES and NOT_USED from here to its own lists,
build_dataset.py reads with the readers here, and styles.py has the new style labels.

What is here, by key (each reader yields the same kinds of records as readers_more.py: "text", "email" or "chat"):
  Modern government writing (public domain)
    govblogs       agency blogs and articles: NASA, VA VAntage Point, FDA Consumer Updates, the National Park
                   Service's articles and Energy.gov's articles (feeds and the sites' own sitemaps)
    obama_social   the Obama White House's archived tweets (@POTUS44, @ObamaWhiteHouse, @FLOTUS44), from the zip
                   files the Obama Presidential Library (National Archives) offers for download
    fedreg_rfi     requests for information and requests for comments in the Federal Register (its free API)
    sam            contract notices and requests for proposals from SAM.gov (its API; needs SAM_GOV_API_KEY)
    fed_speeches   speeches by the Federal Reserve Board's chair and governors (federalreserve.gov)
    crec           floor speeches and debates in the Congressional Record (GovInfo, not congress.gov)
    recipes_nhlbi  heart-healthy recipes from the NHLBI, the same recipes as the reference library's cookbook
  Letters and diaries
    loc_letters    Library of Congress "By the People" transcriptions (volunteers' text, no known copyright) of
                   19th-century letters and diaries: Susan B. Anthony, Frederick Douglass, Civil War soldiers ...
  Student and learner writing
    persuade       the PERSUADE 2.0 corpus of US students' argumentative essays (CC BY 4.0), from a file the owner
                   downloads in a browser (Google Drive closes downloads to programs)
    bawe           the British Academic Written English corpus (personal use), from a file the owner downloads
  Developer and community writing (personal use: the writers keep their copyright)
    python_lists   the Python tutor and python-list mailing lists, through their archive's own API
    gharchive      GitHub issues and issue comments from GH Archive's hourly files
  Reviews (personal use)
    imdb           the Large Movie Review Dataset (Stanford)
    yelp           the Yelp Open Dataset's reviews, from the file the owner downloads after accepting Yelp's terms
  Share-alike
    wikivoyage     travel guide sections from the English Wikivoyage dump (CC BY-SA)
    wikiquote      quotations of people who died before 1956, and proverbs, from the English Wikiquote dump
  Open (UK)
    recipes_nhs    NHS Healthier Families recipes (Open Government Licence), British English and metric measures

Every request goes through fetch.Fetcher: robots.txt and AI-training refusals obeyed, requests paced, nothing sent
but the kit's name. API keys come only from the computer's settings (environment variables), never from these files.
Files the owner downloads by hand are given with --local-file KEY=PATH (see READ ME FIRST.txt).
"""

import csv
import datetime
import gzip
import html
import io
import json
import os
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import zipfile

import readers_business
import readers_meetings
import readers_more

html_text, cap_words, wiki_plain = readers_business.html_text, readers_business.cap_words, readers_more.wiki_plain
csv.field_size_limit(2 ** 31 - 1)

# Sources whose records come from many groups (here: GitHub repositories): the builder keeps no more than a tenth of a
# source's examples from one group.
GROUPED = {"gharchive"}

# New style labels (styles.py adds them to its list): name -> what it is.
STYLES = {
    "essay": "student and learner essays: argumentative and academic assignments",
    "diary": "diaries and journals",
    "travel": "travel guides and descriptive writing about places",
    "quotation": "quotations, sayings and proverbs",
    "bug_report": "bug reports, feature requests and replies on software projects",
    "procurement": "contract notices, requests for proposals and requests for information",
    "recipe": "recipes and step-by-step cooking instructions",
}
FORMAL = {"procurement"}
CASUAL = {"bug_report"}


# ====================================================================== shared helpers

def words(text):
    """How many words text has."""
    return len((text or "").split())


def paragraphs_of(fragment, tags="p|h2|h3"):
    """The text of the paragraphs (and headings) in an HTML fragment, one per line, blank lines between."""
    out = []
    for _, inner in re.findall(r"(?is)<(" + tags + r")\b[^>]*>(.*?)</\1>", fragment):
        inner = re.sub(r'(?is)<sup\b.*?</sup>|<a\b[^>]*href="#[^"]*"[^>]*>.*?</a>', "", inner)
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", inner))).strip()
        if text:
            out.append(text)
    return "\n\n".join(out)


def page_title(page):
    """A page's title: its og:title, else its first <h1>, else its <title>, without the site's name."""
    m = re.search(r'(?is)<meta[^>]+property="og:title"[^>]+content="([^"]*)"', page) or \
        re.search(r"(?is)<h1\b[^>]*>(.*?)</h1>", page) or re.search(r"(?is)<title>(.*?)</title>", page)
    title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""
    return re.sub(r"\s+", " ", re.split(r"\s+[|–—]\s+|\s+-\s+(?=[A-Z][\w. ]+$)", title)[0]).strip()


def article_text(page):
    """(title, text) of an article page: the paragraphs inside its <article>, else its <main>, else the part marked
    id="main" or id="article", else the whole page. Menus, footers and scripts are left out."""
    page = re.sub(r"(?is)<(script|style|nav|header|footer|aside|form)\b.*?</\1>", " ", page)
    region = None
    for pattern in (r"(?is)<article\b.*</article>", r"(?is)<main\b.*?</main>",
                    r'(?is)<[^>]+id="(?:main|main-content|article|content)".*'):
        m = re.search(pattern, page)
        if m and words(re.sub(r"<[^>]+>", " ", m.group(0))) > 50:
            region = m.group(0)
            break
    return page_title(page), paragraphs_of(region or page)


def feed_entries(xml):
    """[(title, link, full content as HTML or "")] from an RSS feed."""
    out = []
    for item in re.findall(r"(?s)<item\b.*?</item>", xml):
        def field(name):
            m = re.search(r"(?s)<" + name + r"\b[^>]*>(.*?)</" + name + ">", item)
            return re.sub(r"(?s)<!\[CDATA\[(.*?)\]\]>", r"\1", m.group(1)).strip() if m else ""
        out.append((html.unescape(re.sub(r"<[^>]+>", "", field("title"))).strip(), html.unescape(field("link")),
                    field("content:encoded")))
    return out


def sitemap_locs(xml, pattern=""):
    """The addresses listed in a sitemap (or sitemap index), only those matching pattern when one is given."""
    locs = [html.unescape(x.strip()) for x in re.findall(r"<loc>(.*?)</loc>", xml, re.S)]
    return [u for u in locs if re.search(pattern, u)] if pattern else locs


def spread(items, n):
    """At most n of items, taken evenly from the whole list (so not only the newest or the oldest)."""
    items = list(items)
    if len(items) <= n:
        return items
    step = len(items) / n
    return [items[int(i * step)] for i in range(n)]


def local_rows(path, member_filter=lambda name: name.lower().endswith(".csv")):
    """The rows (dicts) of the CSV file at path, or of every CSV file inside the zip file at path."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if member_filter(name) and not name.startswith("__MACOSX"):
                    with z.open(name) as f:
                        yield from csv.DictReader(io.TextIOWrapper(f, "utf-8", errors="replace"))
        return
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        yield from csv.DictReader(f)


def text_record(group, style, kind, form, tone, audience, instruction, response, **more):
    """A ready instruction and answer pair (the "text" record build_dataset.py understands)."""
    return {"type": "text", "group": group, "style_label": style, "kind": kind, "form": form, "tone": tone,
            "audience": audience, "instruction": instruction, "response": response, **more}


def no_file(say, name, how):
    """Say that a source read from a downloaded file was skipped because no file was given."""
    say(f"  {name}: skipped, because it is read from a file you download yourself. {how}")


# ====================================================================== agency blogs and articles (public domain)

AGENCY_FEEDS = [
    # (group, feed address, style, what the site is)
    ("NASA", "https://www.nasa.gov/feed/", "blog", "NASA's news and blog site"),
    ("VA VAntage Point", "https://news.va.gov/feed/", "blog",
     "VAntage Point, the US Department of Veterans Affairs' official blog"),
]
FDA_FEED = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/consumers/rss.xml"
NPS_SITEMAP = "https://www.nps.gov/sitemap/sitemap1.xml"
ENERGY_SITEMAP = "https://www.energy.gov/sitemap.xml?page=1"


def read_govblogs(fetcher, say=print, per_site=40, feed_pages=4, fda_pages=12, **_):
    """Text records: posts from agency blogs (full text in their feeds, page after page), FDA Consumer Updates
    (FDA's site asks programs to wait 30 seconds between pages, so fewer), and articles from the National Park
    Service and Energy.gov found in each site's own sitemap."""
    for group, feed, style, what in AGENCY_FEEDS:
        got = 0
        for n in range(1, feed_pages + 1):
            try:
                xml = fetcher.get(feed + (f"?paged={n}" if n > 1 else "")).decode("utf-8", "replace")
            except urllib.error.HTTPError:
                break
            for title, _, content in feed_entries(xml):
                text = html_text(content)
                if words(text) < 120 or got >= per_site:
                    continue
                got += 1
                yield text_record(group, style, "blog post", "blog post", "friendly and plain", "the public",
                                  f'Write a post for {what} titled "{title}".', cap_words(text))
            if got >= per_site:
                break
        say(f"  {group}: {got} posts.")
    # FDA Consumer Updates: the feed has summaries, so each article page is read
    xml = fetcher.get(FDA_FEED).decode("utf-8", "replace")
    for title, link, _ in feed_entries(xml)[:fda_pages]:
        try:
            _, text = article_text(fetcher.get(link.replace("http://", "https://")).decode("utf-8", "replace"))
        except urllib.error.HTTPError:
            continue
        text = re.split(r"\n\n(?:Back to Top|Related Information|Content current as of)", text)[0]
        if words(text) >= 120:
            yield text_record("FDA", "plain_language_gov", "consumer article", "article", "plain and helpful",
                              "the public", f'Write a plain-language consumer article for the US Food and Drug '
                              f'Administration titled "{title}", explaining it clearly to the public.',
                              cap_words(text))
    for group, sitemap, pattern, instruction in (
            ("NPS", NPS_SITEMAP, r"/articles/\d{3}/", 'Write an article for the National Park Service website titled '
             '"{title}", describing the place, its history or its nature for visitors.'),
            ("Energy.gov", ENERGY_SITEMAP, r"energy\.gov/articles/", "Write an article for the US Department of "
             'Energy\'s website titled "{title}", in plain language for the public.')):
        links = spread(sitemap_locs(fetcher.get(sitemap).decode("utf-8", "replace"), pattern), per_site * 2)
        got = 0
        for link in links:
            if got >= per_site:
                break
            try:
                title, text = article_text(fetcher.get(link).decode("utf-8", "replace"))
            except urllib.error.HTTPError:
                continue
            if words(text) < 150 or not title:
                continue
            got += 1
            style = "travel" if group == "NPS" else "blog"
            yield text_record(group, style, "article", "article", "plain and descriptive", "the public",
                              instruction.format(title=title), cap_words(text))
        say(f"  {group}: {got} articles.")


# ====================================================================== Obama White House tweets (public domain)

OBAMA_FILES = "https://obamawhitehouse.archives.gov/sites/default/files/{name}.zip"
OBAMA_ACCOUNTS = [
    ("POTUS111716", "@POTUS44, President Obama's own account"),
    ("WhiteHouse111716", "@ObamaWhiteHouse, the White House's official account"),
    ("FLOTUS111716", "@FLOTUS44, First Lady Michelle Obama's account"),
]
STOP_WORDS = set("""the a an and or but of to in on for with at by from is are was were be been being it its this that
these those we you i our your my their his her they he she as not no so do does did have has had will would can could
should just about into than then them there here what which who whom when where why how all any each more most other
some such only own same too very now today let get make sure going every year years time want help thank thanks""".split())


def tweet_topic(text):
    """A few words that say what a tweet is about: its hashtags and mentions, then its longest content words."""
    tags = re.findall(r"[#@]\w+", text)
    plain = re.sub(r"https?://\S+|[#@]\w+", " ", text)
    content = []
    for w in re.findall(r"[A-Za-z][A-Za-z'\-]{3,}", plain):
        if w.lower() not in STOP_WORDS and w.lower() not in (c.lower() for c in content):
            content.append(w)
    content = sorted(content, key=len, reverse=True)[:4]
    return ", ".join(tags[:3] + content) or "the day's news"


def tweets_from_zip(data):
    """[tweet text] from one archived account's zip (its tweets.csv), leaving out retweets."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        name = next((n for n in z.namelist() if n.endswith("tweets.csv")), None)
        if not name:
            return []
        rows = csv.DictReader(io.TextIOWrapper(z.open(name), "utf-8", errors="replace"))
        out = []
        for row in rows:
            text = html.unescape(row.get("text") or "").strip()
            if row.get("retweeted_status_id") or text.startswith("RT @"):
                continue
            text = re.sub(r"https?://t\.co/\w+", "[link]", text).strip()
            if words(re.sub(r"\[link\]", "", text)) >= 6:
                out.append(text)
        return out


def read_obama_social(fetcher, say=print, **_):
    """Text records: one tweet each, taken in turn from the three accounts so every account is represented."""
    lists = []
    for name, account in OBAMA_ACCOUNTS:
        tweets = tweets_from_zip(fetcher.get(OBAMA_FILES.format(name=name)))
        say(f"  Obama White House: {len(tweets)} tweets from {account.split(',')[0]}.")
        lists.append((account, tweets))
    for i in range(max((len(t) for _, t in lists), default=0)):
        for account, tweets in lists:
            if i < len(tweets):
                yield text_record(account.split(",")[0], "social_post", "social media post", "tweet",
                                  "upbeat and plain", "the public",
                                  f"Write a tweet (at most 280 characters) for {account}, in its plain, upbeat public "
                                  f"voice, about: {tweet_topic(tweets[i])}.", tweets[i])


# ====================================================================== Library of Congress transcriptions (open)

LOC_ITEM = "https://www.loc.gov/item/{id}/?fo=json"
LOC_DATASETS = [
    # (dataset item number, collection name): 19th-century papers only, so the letters themselves are old enough to be
    # in the public domain; the volunteers' transcriptions carry no known copyright.
    ("2020445591", "Susan B. Anthony Papers"),
    ("2020445592", "Elizabeth Cady Stanton Papers"),
    ("2023514913", "Frederick Douglass Papers"),
    ("2025474987", "Christian A. Fleetwood Papers"),
    ("2023527888", "Anna E. Dickinson Papers"),
    ("2019667237", "William Oland Bourne Papers (letters from Civil War soldiers)"),
    ("2023527887", "letters and diaries of women in the American Civil War"),
    ("2023527890", "James A. Garfield's diaries"),
    ("2019667238", "Samuel J. Gibson's diary and correspondence"),
    ("2023514955", "Benajah Jay Antrim's journals"),
    ("2025474986", "Joseph Holt Papers"),
    ("2025465720", "Abraham Lincoln Papers"),
]
LOC_MAX_BYTES = 80_000_000


def loc_zip_url(item_json, max_bytes=LOC_MAX_BYTES):
    """The address of the smallest zip file (CSV, not JSON or Parquet) a Library of Congress dataset item offers."""
    files = []
    for res in item_json.get("resources", []):
        for group in res.get("files", []):
            for f in group if isinstance(group, list) else [group]:
                url = f.get("url", "")
                if url.endswith(".zip") and not re.search(r"_(json|parquet)\.zip$", url):
                    files.append((int(f.get("size") or 0), url))
    files = [f for f in files if f[0] <= max_bytes] or []
    return min(files)[1] if files else ""


def asset_order(asset):
    """The page number at the end of an asset name ("mss123-0004" -> 4), for putting pages in order."""
    m = re.search(r"(\d+)\D*$", asset or "")
    return int(m.group(1)) if m else 0


ARCHIVE_NOTE = re.compile(r"(?i)\b(box \d+|folder \d+|series \d+|general correspondence \d{4}|[a-z]+ (?:&|and) "
                          r"writings file|subject file)\b")
NOT_LETTERS = re.compile(r"(?i)speech|writings|scrapbook|printed|clipping|subject file|legal file|financial|"
                         r"miscellany|newspaper")


def loc_documents(rows):
    """[(item title, project, [page texts])] from the rows of a By the People CSV, pages in order."""
    items, order = {}, []
    for row in rows:
        text = (row.get("Transcription") or "").strip()
        key = row.get("ItemId") or row.get("Item")
        if not key:
            continue
        if key not in items:
            items[key] = (row.get("Item", ""), row.get("Project", ""), [])
            order.append(key)
        if text:
            paras = re.split(r"\n\s*\n", text)
            if paras and ARCHIVE_NOTE.search(paras[0]) and len(paras[0].split()) <= 30:
                text = "\n\n".join(paras[1:]).strip()   # the archive's folder label, not the writer's words
            if text:
                items[key][2].append((asset_order(row.get("Asset")), text))
    return [(items[k][0], items[k][1], [t for _, t in sorted(items[k][2])]) for k in order]


DATE_LINE = re.compile(r"(?i)^\s*(?:(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|(?:jan|feb|mar|apr|"
                       r"may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?[ ,]+(?:\d|[a-z]+day)|dear\b|my dear\b)")


def join_lines(page):
    """A transcribed page with the manuscript's line breaks joined into sentences: a word broken with a hyphen at the
    end of a line is joined, blank lines stay as paragraph breaks, and a line that starts a diary date or a
    salutation ("Dear ...") starts a new line."""
    out = []
    for para in re.split(r"\n\s*\n", page.strip()):
        lines = [ln.strip() for ln in para.split("\n") if ln.strip()]
        text = ""
        for ln in lines:
            if not text:
                text = ln
            elif DATE_LINE.match(ln):
                text += "\n" + ln
            elif re.search(r"\w-$", text) and not text.endswith("--"):
                text = text[:-1] + ln
            else:
                text += " " + ln
        if text:
            out.append(re.sub(r"[ \t]{2,}", " ", text))
    return "\n\n".join(out)


def mostly_words(text):
    """True when most of text is words of letters (not a list of figures, addresses or names)."""
    tokens = text.split()
    return bool(tokens) and sum(1 for t in tokens if re.fullmatch(r"[A-Za-z][a-z'’]+[,.;:!?]?", t)) / len(tokens) > 0.6


def chunk_pages(pages, max_words=700):
    """Pages joined into pieces of at most about max_words words, never splitting a page."""
    out, current = [], []
    for page in pages:
        page = join_lines(page)
        if current and words("\n\n".join(current + [page])) > max_words:
            out.append("\n\n".join(current))
            current = []
        current.append(page)
    if current:
        out.append("\n\n".join(current))
    return out


def loc_records(rows, collection, per_dataset=25, per_item=3):
    """Text records (letters or diary entries) from one By the People dataset: at most per_item pieces from one
    item (a long diary is many pieces), and items spread over the whole dataset."""
    got = 0
    documents = loc_documents(rows)
    for item, project, pages in spread(documents, max(per_dataset, len(documents) // 3)):
        diary = bool(re.search(r"(?i)diar|journal", item + " " + project + " " + collection))
        if not diary and NOT_LETTERS.search(item + " " + project):
            continue
        pages = [p for p in pages if mostly_words(p)]          # leave out lists of figures, names and addresses
        pieces = [p for p in chunk_pages(pages) if words(p) >= 40]
        if diary:      # a diary's printed pages (calendars, postage rates, almanac) have no dated entries
            pieces = [p for p in pieces if len(re.findall(r"(?im)^\s*(?:(?:mon|tues|wednes|thurs|fri|satur|sun)day|"
                                                          r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
                                                          r"\.?,? +(?:\d|[a-z]+day))", p)) >= 1]
        for n, piece in enumerate(spread(pieces, per_item)):
            if got >= per_dataset:
                continue
            item_name = re.sub(r"\s+", " ", item).strip()
            if diary:
                instruction = (f'Write a diary entry like those in the {collection} ("{item_name}"), in the writer\'s '
                               "own style, spelling and punctuation of the time.")
            else:
                instruction = (f'Write a letter like this one from the {collection} at the Library of Congress '
                               f'("{item_name}"), in the writer\'s own style, spelling and punctuation of the time.')
            got += 1
            yield text_record(collection, "diary" if diary else "letter_personal", "diary" if diary else "letter",
                              "diary entry" if diary else "letter", "personal, of its time",
                              "family, friends or colleagues", instruction, piece)
        if got >= per_dataset:
            return


def read_loc_letters(fetcher, say=print, datasets=None, per_dataset=25, **_):
    for number, collection in datasets or LOC_DATASETS:
        item = json.loads(fetcher.get(LOC_ITEM.format(id=number)))
        url = loc_zip_url(item)
        if not url:
            say(f"  Library of Congress: no small CSV file for the {collection}; skipped.")
            continue
        with zipfile.ZipFile(io.BytesIO(fetcher.get(url))) as z:
            rows = []
            for name in z.namelist():
                if name.lower().endswith(".csv"):
                    rows += list(csv.DictReader(io.TextIOWrapper(z.open(name), "utf-8", errors="replace")))
        say(f"  Library of Congress: {len(rows)} transcribed pages in the {collection}.")
        yield from loc_records(rows, collection, per_dataset)


# ====================================================================== student writing (files the owner downloads)

def persuade_records(rows, per_prompt=25):
    """Text records from the PERSUADE 2.0 CSV: each essay with its assignment and the student's grade."""
    per = {}
    for row in rows:
        text = (row.get("full_text") or row.get("text") or "").strip()
        prompt = (row.get("prompt_name") or "an essay prompt").strip()
        if words(text) < 80 or per.get(prompt, 0) >= per_prompt:
            continue
        per[prompt] = per.get(prompt, 0) + 1
        grade = (row.get("grade_level") or "").strip()
        assignment = re.sub(r"\s+", " ", (row.get("assignment") or "").strip()) or f'"{prompt}"'
        who = f"a US student in grade {grade}" if grade and grade.lower() != "nan" else "a US secondary school student"
        score = (row.get("holistic_essay_score") or "").strip()
        instruction = f"Write an argumentative essay as {who} would, for this assignment: {assignment}"
        if score and score.lower() != "nan":
            instruction += f"\n(Teachers scored this essay {score} out of 6.)"
        yield text_record(prompt, "essay", "student essay", "essay", "student", "a teacher", instruction, text)


def read_persuade(fetcher, say=print, local_file=None, **_):
    if not local_file:
        no_file(say, "PERSUADE 2.0", "Download the training CSV from the links on github.com/scrosseye/persuade_corpus_2.0 "
                "in your browser and add --local-file persuade=<where you saved it>.")
        return
    yield from persuade_records(local_rows(local_file))


def bawe_title(text):
    """The first short line of a BAWE text, taken as its title ("" when the first line is a sentence)."""
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return first if 0 < len(first.split()) <= 15 and not first.endswith(".") else ""


def bawe_records(texts):
    """Text records from (file name, text) pairs of the BAWE corpus."""
    for name, text in texts:
        text = re.sub(r"\n{3,}", "\n\n", re.sub(r"<[^>]+>", "", text)).strip()
        if words(text) < 150:
            continue
        title = bawe_title(text)
        titled = f' titled "{title}"' if title else ""
        yield text_record("bawe", "essay", "university assignment", "essay", "academic", "a university tutor",
                          f"Write a university student's assignment{titled}, in British academic English (British "
                          "spelling and the conventions of UK university writing).", cap_words(text, 2000))


def read_bawe(fetcher, say=print, local_file=None, **_):
    if not local_file:
        no_file(say, "BAWE", "Download the BAWE corpus (the zip of plain text files) from the Oxford Text Archive in "
                "your browser after accepting its licence, and add --local-file bawe=<where you saved it>.")
        return
    with zipfile.ZipFile(local_file) as z:
        names = [n for n in z.namelist() if n.lower().endswith((".txt", ".xml")) and "readme" not in n.lower()]
        yield from bawe_records((n, z.read(n).decode("utf-8", "replace")) for n in names)


# ====================================================================== reviews (personal use)

IMDB_URL = "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"


def imdb_records(tar_bytes, per_side=400):
    """Text records from the Large Movie Review Dataset: the training reviews, positive and negative in turn."""
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tar:
        sides = {"pos": [], "neg": []}
        for member in tar.getmembers():
            m = re.search(r"/train/(pos|neg)/\d+_(\d+)\.txt$", member.name)
            if m and member.isfile():
                sides[m.group(1)].append((member, int(m.group(2))))
        chosen = {k: spread(v, per_side) for k, v in sides.items()}
        for pair in zip(chosen["pos"], chosen["neg"]):
            for member, rating in pair:
                text = tar.extractfile(member).read().decode("utf-8", "replace")
                text = html.unescape(re.sub(r"<br\s*/?>", "\n", text)).strip()
                text = re.sub(r"\n{3,}", "\n\n", text)
                if not 30 <= words(text) <= 700:
                    continue
                feeling = "positive" if rating >= 7 else "negative"
                yield text_record("imdb", "review", "review", "movie review", "casual and personal", "other viewers",
                                  f"Write a {feeling} movie review, rating the film {rating} out of 10, in a casual, "
                                  "personal style, as a viewer would post it on a movie website.", text)


def read_imdb(fetcher, say=print, **_):
    say("  Large Movie Review Dataset: reading the official file (84 MB).")
    yield from imdb_records(fetcher.get(IMDB_URL))


def yelp_lines(path):
    """The lines of the Yelp reviews file, from the dataset's tar or zip file or the JSON file itself."""
    if tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as tar:
            for member in tar:
                if member.isfile() and re.search(r"review\.json$", member.name):
                    yield from tar.extractfile(member)
                    return
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.endswith("review.json")), None)
            if name:
                yield from z.open(name)
    else:
        with open(path, "rb") as f:
            yield from f


def yelp_records(lines, per_star=200):
    """Text records from Yelp review lines (JSON), no more than per_star for each star rating."""
    count = {}
    for line in lines:
        try:
            review = json.loads(line)
        except ValueError:
            continue
        stars = int(float(review.get("stars") or 0))
        text = (review.get("text") or "").strip()
        if not 1 <= stars <= 5 or not 30 <= words(text) <= 600 or count.get(stars, 0) >= per_star:
            continue
        count[stars] = count.get(stars, 0) + 1
        yield text_record(f"{stars} stars", "review", "review", "business review", "casual and personal",
                          "other customers", f"Write a {stars}-star review of a local business for a review website, "
                          "in a casual, personal style.", text)
        if len(count) == 5 and all(v >= per_star for v in count.values()):
            return


def read_yelp(fetcher, say=print, local_file=None, **_):
    if not local_file:
        no_file(say, "Yelp Open Dataset", "Download it from yelp.com/dataset in your browser (you must accept Yelp's "
                "Dataset Terms of Use there), and add --local-file yelp=<where you saved it>.")
        return
    yield from yelp_records(yelp_lines(local_file))


# ====================================================================== the Python mailing lists (personal use)

PY_LISTS = ["tutor@python.org", "python-list@python.org"]
PY_API = "https://mail.python.org/archives/api/list/{name}/emails/?limit=50&offset={offset}"
PY_FOOTER = re.compile(r"(?s)\n(?:-- \n|_{20,}\n).{0,300}mail\.python\.org.*$")


def python_email_record(data, list_name):
    """An email record from one message of the HyperKitty archive API (JSON), or None."""
    body = PY_FOOTER.sub("", (data.get("content") or "").replace("\r\n", "\n")).strip()
    if words(body) < 8:
        return None
    return {"type": "email", "subject": data.get("subject", ""), "body": body, "group": list_name,
            "audience": "a mailing list of Python programmers", "is_reply": bool(data.get("parent")),
            "msg_id": data.get("message_id", ""), "style_label": "forum_post",
            "header": f"From: {data.get('sender_name', '')}\nSubject: {data.get('subject', '')}\n"
                      f"Date: {data.get('date', '')}\n"}


def read_python_lists(fetcher, say=print, lists=None, pages=2, **_):
    """Email records from the Python mailing lists, through the archive's own API (the bulk "export" addresses
    are closed to programs by robots.txt, so the kit does not use them)."""
    for name in lists or PY_LISTS:
        for page in range(pages):
            listing = json.loads(fetcher.get(PY_API.format(name=name, offset=page * 50)))
            for item in listing.get("results", []):
                record = python_email_record(json.loads(fetcher.get(item["url"])), name.split("@")[0])
                if record:
                    yield record


# ====================================================================== GitHub issues from GH Archive (personal use)

GH_HOURS = ["2024-03-05-15", "2023-10-17-16", "2024-09-10-14", "2022-11-15-17"]
GH_URL = "https://data.gharchive.org/{hour}.json.gz"
ENGLISH = re.compile(r"(?i)\b(the|and|is|to|it|when|this|with|not|have)\b")


def clean_issue_text(text):
    """An issue or comment body without HTML comments (template hints) and with tidy blank lines."""
    text = re.sub(r"(?s)<!--.*?-->", "", (text or "").replace("\r\n", "\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def looks_english(text):
    """True when text is mostly plain ASCII and has several common English words."""
    if not text:
        return False
    ascii_share = sum(1 for c in text if ord(c) < 128) / len(text)
    return ascii_share > 0.95 and len(ENGLISH.findall(text)) >= 3


def gharchive_record(event):
    """A text record from one GH Archive event (an issue opened, or a comment on an issue), or None."""
    kind, payload = event.get("type"), event.get("payload") or {}
    actor = (event.get("actor") or {}).get("login", "")
    repo = (event.get("repo") or {}).get("name", "")
    issue = payload.get("issue") or {}
    if not issue or "pull_request" in issue or actor.endswith("[bot]") or \
            (issue.get("user") or {}).get("type") == "Bot":
        return None
    title, issue_body = (issue.get("title") or "").strip(), clean_issue_text(issue.get("body"))
    if kind == "IssuesEvent" and payload.get("action") == "opened":
        if not 15 <= words(issue_body) <= 600 or not looks_english(issue_body):
            return None
        return text_record(repo, "bug_report", "issue", "issue report", "plain and practical", "the project's developers",
                           f'Write a GitHub issue for the open-source project {repo} titled "{title}", describing the '
                           "problem or request clearly.", issue_body)
    if kind == "IssueCommentEvent" and payload.get("action") == "created":
        comment = payload.get("comment") or {}
        if (comment.get("user") or {}).get("type") == "Bot":
            return None
        body = clean_issue_text(comment.get("body"))
        if not 12 <= words(body) <= 500 or not looks_english(body):
            return None
        shown = " ".join(issue_body.split()[:300]) + (" [...]" if words(issue_body) > 300 else "")
        return text_record(repo, "bug_report", "issue comment", "issue comment", "plain and practical",
                           "the project's developers and users",
                           f'Write a reply on the GitHub issue "{title}" in the project {repo}.'
                           + (f"\n\nThe issue says:\n{shown}" if shown else ""), body)
    return None


def read_gharchive(fetcher, say=print, hours=None, per_hour=150, **_):
    """Text records from GH Archive's hourly files, read as they arrive and stopped early."""
    for hour in hours or GH_HOURS:
        say(f"  GH Archive: reading the hour {hour} (stops early).")
        resp = fetcher.open_stream(GH_URL.format(hour=hour))
        got = 0
        try:
            for line in gzip.GzipFile(fileobj=resp):
                try:
                    record = gharchive_record(json.loads(line))
                except ValueError:
                    continue
                if record:
                    got += 1
                    yield record
                    if got >= per_hour:
                        break
        finally:
            resp.close()


# ====================================================================== SAM.gov contract notices (public domain)

SAM_SEARCH = ("https://api.sam.gov/opportunities/v2/search?api_key={key}&postedFrom={start}&postedTo={end}"
              "&limit=100&offset=0&ptype={ptype}")
SAM_TYPES = [("o", "solicitation"), ("k", "combined synopsis and solicitation"), ("r", "sources sought notice"),
             ("p", "presolicitation notice")]


def sam_description(data):
    """The plain text of a SAM.gov notice description (the API answers with JSON holding HTML, or with HTML)."""
    try:
        text = json.loads(data).get("description", "")
    except ValueError:
        text = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    return html_text(text or "")


def read_sam(fetcher, say=print, api_key=None, per_type=10, **_):
    """Text records: federal contract notices and requests for proposals, from the SAM.gov Get Opportunities API.
    The API needs a free key from SAM.gov (an account's "Public API Key") in the setting SAM_GOV_API_KEY. A personal
    key allows only about ten requests a day, so the kit reads a few notices each time and keeps them in the cache."""
    key = api_key or os.environ.get("SAM_GOV_API_KEY", "").strip()
    if not key:
        say("  SAM.gov: no API key (set SAM_GOV_API_KEY, free from your SAM.gov account); skipped.")
        return
    today = datetime.date.today()
    start, end = (today - datetime.timedelta(days=60)).strftime("%m/%d/%Y"), today.strftime("%m/%d/%Y")
    try:
        for ptype, what in SAM_TYPES:
            data = json.loads(fetcher.get(SAM_SEARCH.format(key=key, start=urllib.parse.quote(start, safe=""),
                                                            end=urllib.parse.quote(end, safe=""), ptype=ptype)))
            got = 0
            for opp in data.get("opportunitiesData", []):
                desc_url = opp.get("description") or ""
                if got >= per_type or not desc_url.startswith("https://api.sam.gov/"):
                    continue
                text = sam_description(fetcher.get(desc_url + ("&" if "?" in desc_url else "?") + "api_key=" + key))
                if words(text) < 80:
                    continue
                got += 1
                agency = (opp.get("fullParentPathName") or opp.get("department") or "a federal agency").split(".")[0]
                yield text_record(agency.title(), "procurement", what, what, "formal", "contractors",
                                  f'Write a US government contract notice (a {what}) for the {agency.title()}: '
                                  f'"{opp.get("title", "").strip()}". Describe what is needed, the requirements and how '
                                  "to respond, in the formal style of a federal notice.", cap_words(text))
    except urllib.error.HTTPError as err:
        if err.code == 429:
            say("  SAM.gov: the daily request limit for this key is used up; the notices read so far are kept, and "
                "the next build continues from the cache.")
            return
        raise


# ====================================================================== Federal Register RFIs and comment requests

FR_API = ("https://www.federalregister.gov/api/v1/documents.json?per_page=100&page=1"
          "&conditions%5Btype%5D%5B%5D=NOTICE&conditions%5Bterm%5D={term}&fields%5B%5D=title"
          "&fields%5B%5D=publication_date&fields%5B%5D=agencies&fields%5B%5D=document_number&order=newest")
# The Federal Register's own full-text pages answer programs with a "Request Access" page, so each notice's text is
# read from GovInfo's copy of the same day's Federal Register.
FR_GOVINFO = "https://www.govinfo.gov/content/pkg/FR-{date}/html/{number}.htm"
FR_TERMS = [("%22request+for+information%22", "rfi", r"(?i)request for information"),
            ("%22request+for+comments%22", "rfc", r"(?i)request for (public )?comments?")]
FR_SKIP = re.compile(r"(?i)information collection|paperwork reduction|submission for omb|sunshine act|"
                     r"meeting notice|privacy act of 1974")


def unwrap(text):
    """Text whose lines were wrapped at a fixed width, with each paragraph joined back into one line."""
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    return "\n\n".join(p for p in paras if p)


def fedreg_body(raw):
    """The notice's own text from GovInfo's copy of the Federal Register (the text inside <pre>): from "AGENCY:" to
    the end, without the "[FR Doc." line, the billing code and the rules of dashes, paragraphs unwrapped."""
    text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
    if re.search(r"(?i)<title>[^<]*request access", text):
        return ""
    m = re.search(r"(?is)<pre>(.*?)</pre>", text)
    text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1) if m else text))
    m = re.search(r"(?m)^\s*AGENCY:", text)
    text = text[m.start():] if m else text
    text = re.split(r"\n\s*\[FR Doc\.", text)[0]
    text = re.sub(r"(?m)^\s*(BILLING CODE.*|-{10,}|\[\[Page \d+\]\])\s*$", "", text)
    return unwrap(text)


def read_fedreg_rfi(fetcher, say=print, per_term=40, **_):
    for term, kind, in_title in FR_TERMS:
        got = 0
        for doc in json.loads(fetcher.get(FR_API.format(term=term))).get("results", []):
            title = (doc.get("title") or "").strip()
            if got >= per_term or FR_SKIP.search(title) or not re.search(in_title, title) or \
                    not doc.get("publication_date") or not doc.get("document_number"):
                continue
            try:
                text = fedreg_body(fetcher.get(FR_GOVINFO.format(date=doc["publication_date"],
                                                                 number=doc["document_number"])))
            except urllib.error.HTTPError:
                continue
            if words(text) < 150:
                continue
            got += 1
            agency = ", ".join(a.get("name", "") for a in doc.get("agencies", []) if a.get("name")) or "a US agency"
            if kind == "rfi":
                yield text_record(agency, "procurement", "request for information", "Federal Register notice",
                                  "formal", "industry and the public",
                                  f'Write a request for information (RFI) for the Federal Register from the {agency}: '
                                  f'"{title}". Explain the background, the questions the agency wants answered and '
                                  "how to respond.", cap_words(text))
            else:
                yield text_record(agency, "plain_language_gov", "request for comments", "Federal Register notice",
                                  "formal", "the public",
                                  f'Write a Federal Register notice from the {agency} asking the public for comments: '
                                  f'"{title}". Say what is proposed, why, and how and by when to comment.',
                                  cap_words(text))


# ====================================================================== Federal Reserve speeches (public domain)

FED_SITE = "https://www.federalreserve.gov"
FED_INDEX = FED_SITE + "/newsevents/speech/{year}-speeches.htm"


def fed_speech(page):
    """(title, speaker, place, text) of a Federal Reserve speech page; the footnotes after the rule are left out."""
    m = re.search(r'(?is)id="article".*', page)
    region = m.group(0) if m else page
    title = re.search(r"(?is)<h3[^>]*class=['\"]title['\"][^>]*>(.*?)</h3>", region)
    speaker = re.search(r"(?is)<p[^>]*class=['\"]speaker['\"][^>]*>(.*?)</p>", region)
    place = re.search(r"(?is)<p[^>]*class=['\"]location['\"][^>]*>(.*?)</p>", region)
    clean = lambda x: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", x.group(1)))).strip() if x else ""
    body = region[place.end():] if place else region
    body = re.split(r"(?i)<hr\b", body)[0]
    return clean(title), clean(speaker), clean(place), paragraphs_of(body, "p|h4")


def read_fed_speeches(fetcher, say=print, years=("2024", "2019", "2014"), per_year=15, **_):
    for year in years:
        index = fetcher.get(FED_INDEX.format(year=year)).decode("utf-8", "replace")
        links = list(dict.fromkeys(re.findall(r'href="(/newsevents/speech/[a-z]+\d{8}[a-z]?\.htm)"', index)))
        say(f"  Federal Reserve: {len(links)} speeches listed for {year}; reading {per_year}.")
        for link in spread(links, per_year):
            title, speaker, place, text = fed_speech(fetcher.get(FED_SITE + link).decode("utf-8", "replace"))
            if words(text) < 200 or not title:
                continue
            where = f", {place[0].lower() + place[1:]}" if place else ""
            yield text_record(year, "speech", "speech", "speech", "formal", "an audience",
                              f'Write a speech by {speaker or "a Federal Reserve official"} of the Federal Reserve Board, '
                              f'"{title}"{where}.', cap_words(text))


# ====================================================================== Congressional Record floor speeches (GovInfo)

CREC_SITEMAP = "https://www.govinfo.gov/sitemap/CREC_{year}_sitemap.xml"
CREC_MODS = "https://www.govinfo.gov/metadata/pkg/{pkg}/mods.xml"
CREC_HTM = "https://www.govinfo.gov/content/pkg/{pkg}/html/{granule}.htm"
CREC_SKIP = re.compile(r"(?i)^(prayer|pledge|the journal|adjournment|announcement|congressional record|house of "
                       r"representatives|senate|constitutional authority|executive communications|public bills|"
                       r"additional (co)?sponsors|messages? from|presidential messages|reports? of committees|executive "
                       r"report|introduction of bills|submission of|authority for committees|cloture motion|executive "
                       r"calendar|legislative session|executive session|arms sales|orders for|order for|morning business|"
                       r"conclusion of|reservation of leader|notice of|amendments submitted|text of amendments|"
                       r"leave of absence|enrolled bills|daily digest|recess|quorum|unanimous consent|confirmation|"
                       r"statements on introduced|senate resolution|.*continuation of the national emergency|motion to|"
                       r"appointment of|.*\bvote\b|yeas and nays|providing for consideration|"
                       r"[a-z]+ \d{1,2}, \d{4}\.?$)")
CREC_SPEAKER = re.compile(r"^  ((?:Mr|Ms|Mrs|Miss|Dr)\. (?:[A-Z][a-z]+ )?[A-Z][A-Z'\-]+(?: [A-Z][A-Z'\-]+)?"
                          r"(?: of [A-Z][a-z]+(?: [A-Z][a-z]+)?)?|The (?:SPEAKER|PRESIDING OFFICER|ACTING PRESIDENT|"
                          r"VICE PRESIDENT|CHAIR|CHAIRMAN|Acting CHAIR)[A-Za-z ()]*)\. (.*)$")


def crec_granules(mods_xml):
    """[(granule, title)] of the House, Senate and Extensions of Remarks parts of a day's Record that are speeches
    (procedural parts such as the prayer, the journal and lists of bills are left out)."""
    out = []
    for m in re.finditer(r'(?s)<relatedItem type="constituent" ID="id-(CREC[^"]+)".*?<title>(.*?)</title>', mods_xml):
        granule, title = m.group(1), html.unescape(m.group(2)).strip()
        if re.search(r"-Pg[HSE]\d", granule) and not CREC_SKIP.match(re.sub(r"\s*\(.*?\)\s*$", "", title)):
            out.append((granule, title))
    return out


def crec_turns(page):
    """[(speaker, words)] from one granule's HTML (the text inside <pre>), without page marks and the
    "(Mr. X asked and was given permission ...)" lines."""
    m = re.search(r"(?is)<pre>(.*?)</pre>", page)
    text = html.unescape(re.sub(r"<[^>]+>", "", m.group(1) if m else page))
    text = re.sub(r"\[\[Page [A-Z]?\d+\]\]", "", text)
    text = re.sub(r"(?s)\n  \((?:Mr|Ms|Mrs|Miss|Dr)\. [^)]*?(?:asked and was given|was given permission)[^)]*\)", "\n",
                  text)
    lines = [ln for ln in text.split("\n") if not re.match(r"^\s*\[.*\]\s*$|^\s*_{5,}\s*$", ln)]
    turns = readers_meetings.join_turns(lines, CREC_SPEAKER)
    return [(who, w) for who, w in turns if w and not w.startswith("[")]


PROCEDURE = re.compile(r"(?i)^(?:(?:Mr|Madam|Mrs)\. (?:President|Speaker|Chair(?:man)?),? )?(?:I (?:ask unanimous consent|"
                       r"suggest the absence of a quorum|yield (?:back|the floor)|reserve the balance|move to|demand|"
                       r"make a point of order)|the clerk will|without objection|is there objection|the question is|"
                       r"the yeas and nays)")


def crec_record(granule, title, page):
    """A record for one floor speech (text) or debate (chat, with the whole text kept), or None."""
    chamber = "Senate" if "-PgS" in granule else "House"
    turns = crec_turns(page)
    if any(re.match(r"\[?(?:Roll(?:call)? (?:No|Vote)|YEAS--)", w) or "YEAS--" in w for _, w in turns):
        return None                                   # a roll-call vote, a list of names
    # the presiding officer's words and short procedural lines are left out: they are not speeches
    turns = [(who, w) for who, w in turns if not who.startswith("The ") and
             not (PROCEDURE.match(w) and words(w) < 40)]
    if not turns:
        return None
    nice = title if not title.isupper() else title.title()
    speakers = {who for who, _ in turns if not who.startswith("The ")}
    if len(turns) >= 4 and len(speakers) >= 2:
        raw = html.unescape(re.sub(r"<[^>]+>", "", page))
        return {"type": "chat", "turns": turns, "group": granule[:15], "style": "speech", "style_label": "speech",
                "setting": f'a debate on the floor of the US {chamber} ("{nice}")', "raw": raw,
                "raw_name": granule + ".txt"}
    who = max(speakers or {turns[0][0]}, key=lambda s: sum(words(w) for x, w in turns if x == s))
    text = "\n\n".join(w for x, w in turns if x == who)
    if words(text) < 80:
        return None
    if "-PgE" in granule:
        instruction = (f'Write a statement for the Extensions of Remarks in the Congressional Record, from a Member of '
                       f'the House, titled "{nice}".')
    else:
        member = "a Senator" if chamber == "Senate" else "a Member of the House"
        instruction = f'Write a floor speech for {member} in the US {chamber}, titled "{nice}".'
    return text_record(granule[:15], "speech", "floor speech", "speech", "formal", f"the US {chamber}", instruction,
                       cap_words(text))


def read_crec(fetcher, say=print, years=("2023", "2018", "2013"), days=3, per_day=15, **_):
    for year in years:
        sitemap = fetcher.get(CREC_SITEMAP.format(year=year)).decode("utf-8", "replace")
        packages = sorted(set(re.findall(r"/details/(CREC-\d{4}-\d{2}-\d{2})</loc>", sitemap)))
        say(f"  Congressional Record: {len(packages)} days listed for {year}; reading {days}.")
        for pkg in spread(packages, days):
            granules = crec_granules(fetcher.get(CREC_MODS.format(pkg=pkg)).decode("utf-8", "replace"))
            for granule, title in spread(granules, per_day):
                record = crec_record(granule, title, fetcher.get(CREC_HTM.format(pkg=pkg, granule=granule))
                                     .decode("utf-8", "replace"))
                if record:
                    yield record


# ====================================================================== Wikivoyage and Wikiquote dumps (CC BY-SA)

WIKIVOYAGE_URL = "https://dumps.wikimedia.org/enwikivoyage/latest/enwikivoyage-latest-pages-articles.xml.bz2"
WIKIQUOTE_URL = "https://dumps.wikimedia.org/enwikiquote/latest/enwikiquote-latest-pages-articles.xml.bz2"


def dump_pages(lines):
    """(title, wikitext) of every article (namespace 0) in the lines of a MediaWiki XML dump; redirects skipped."""
    title, ns, buf, inside = "", "", [], False
    for line in lines:
        if isinstance(line, bytes):
            line = line.decode("utf-8", "replace")
        if "<title>" in line:
            title = html.unescape(re.sub(r"\s*</?title>\s*", "", line))
        elif "<ns>" in line:
            ns = re.sub(r"\D", "", line)
        elif "<text" in line and ns == "0":
            inside, buf = "</text>" not in line, [re.sub(r"^\s*<text[^>]*>", "", line)]
        elif inside:
            buf.append(line)
            inside = "</text>" not in line
        if buf and not inside:
            text = html.unescape("".join(buf).replace("</text>", ""))
            buf = []
            if not text.lstrip().upper().startswith("#REDIRECT"):
                yield title, text


def stream_dump(fetcher, url):
    """The lines of a .bz2 dump, read as they arrive (the caller stops early)."""
    import bz2
    resp = fetcher.open_stream(url)
    try:
        yield from bz2.BZ2File(resp)
    finally:
        resp.close()


def template_spans(text, start):
    """(start, end) of the template that begins at text[start] ("{{"), counting nested braces."""
    depth, i = 0, start
    while i < len(text) - 1:
        if text.startswith("{{", i):
            depth, i = depth + 1, i + 2
        elif text.startswith("}}", i):
            depth, i = depth - 1, i + 2
            if depth == 0:
                return start, i
        else:
            i += 1
    return start, len(text)


def split_params(inner):
    """The parameters of a template's inside, split on "|" outside links and inner templates."""
    out, depth, current = [], 0, ""
    for i, ch in enumerate(inner):
        two = inner[i:i + 2]
        if two in ("{{", "[["):
            depth += 1
        elif two in ("}}", "]]"):
            depth -= 1
        if ch == "|" and depth <= 0:
            out.append(current)
            current = ""
        else:
            current += ch
    out.append(current)
    return out


def voyage_listings(text):
    """Wikivoyage's listing templates ({{see|name=...|content=...}}) as plain sentences: "Name, address. What it
    is. Price." Other templates are left for wiki_plain to remove."""
    out, i = [], 0
    for m in re.finditer(r"\{\{\s*(see|do|eat|drink|sleep|buy|go|listing|marker)\s*\|", text, re.I):
        if m.start() < i:
            continue
        a, b = template_spans(text, m.start())
        params = {}
        for p in split_params(text[a + 2:b - 2])[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                params[k.strip().lower()] = v.strip()
        parts = [params.get("name", ""), params.get("address", "")]
        line = ", ".join(x for x in parts if x)
        for k in ("content", "description", "hours", "price"):
            if params.get(k):
                line += (". " if line else "") + params[k]
        out.append(text[i:a] + line)
        i = b
    out.append(text[i:])
    return "".join(out)


VOYAGE_SECTIONS = ["Understand", "Get in", "Get around", "See", "Do", "Eat", "Drink", "Sleep", "Buy", "Stay safe",
                   "Respect", "Cope"]


def voyage_sections(wikitext):
    """[(section name, plain text)] of the main sections of a Wikivoyage article."""
    parts = re.split(r"(?m)^==\s*([^=].*?)\s*==\s*$", wikitext)
    out = []
    for name, body in zip(parts[1::2], parts[2::2]):
        if name.strip() not in VOYAGE_SECTIONS:
            continue
        body = voyage_listings(body)
        body = re.sub(r"(?m)^\s*\[\[(File|Image):.*$", "", body)
        text = wiki_plain(body)
        text = re.sub(r"(?m)^\*+\s*", "- ", text)
        text = re.sub(r"\s*\(\s*[,;]?\s*\)|(?<=\w) {2,}(?=\w)", lambda m: " " if m.group(0).strip() == "" else "", text)
        text = re.sub(r"(?m)^=+\s*(.*?)\s*=+\s*$", r"\1", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        out.append((name.strip(), text))
    return out


def wikivoyage_records(pages, per_article=3):
    for title, text in pages:
        if "/" in title or re.search(r"(?i)\{\{\s*(disamb|outline|stub|title-index)", text):
            continue
        got = 0
        for section, body in voyage_sections(text):
            if not 80 <= words(body) <= 1200 or got >= per_article:
                continue
            got += 1
            yield text_record("wikivoyage", "travel", "travel guide", "travel guide section", "friendly and practical",
                              "travellers", f'Write the "{section}" section of a travel guide to {title}, in the '
                              "friendly, practical style of Wikivoyage.", body)


def read_wikivoyage(fetcher, say=print, **_):
    say("  Wikivoyage: reading the official dump as it arrives (stops early).")
    yield from wikivoyage_records(dump_pages(stream_dump(fetcher, WIKIVOYAGE_URL)))


def life_years(wikitext):
    """(born, died) years from the first lines of a Wikiquote page about a person, e.g. "(1809 – 1865)"; None
    when the page does not show both."""
    head = wikitext[:1500]
    m = re.search(r"\((?:[^()]*?\b)?(?:c\. )?(\d{3,4})\s*(?:–|-|&ndash;|—|to)\s*(?:c\. )?(?:[^()]*?\b)?(\d{3,4})\)", head)
    if not m:
        return None
    born, died = int(m.group(1)), int(m.group(2))
    return (born, died) if born < died <= born + 110 else None


def wikiquote_quotes(wikitext, max_quotes=4):
    """The top-level quotations of a Wikiquote page's quotes section(s) (lines starting with one "*")."""
    parts = re.split(r"(?m)^==\s*([^=].*?)\s*==\s*$", wikitext)
    body = "".join(b for n, b in zip(parts[1::2], parts[2::2])
                   if re.match(r"(?i)(quotes|quotations|sourced|proverbs|[A-Z]$)", n.strip()))
    if not body and "proverb" in wikitext[:300].lower():
        body = wikitext
    out = []
    for line in re.findall(r"(?m)^\*(?!\*)\s*(.+)$", body):
        quote = wiki_plain(re.sub(r"(?i)<br\s*/?>", "\n", line))
        quote = re.sub(r"[ \t]+", " ", quote).strip().strip('"').strip()
        if 8 <= words(quote) <= 120 and not re.match(r"(?i)(see also|as quoted|reported in)", quote):
            out.append(quote)
        if len(out) >= max_quotes:
            break
    return out


def wikiquote_records(pages, latest_death=1955):
    for title, text in pages:
        if re.search(r"(?i)^(list of|lists of)|disambiguation", title) or "{{disambig" in text.lower():
            continue
        if re.search(r"(?i)proverbs", title):
            for quote in [q for q in wikiquote_quotes(text, 10) if words(q) <= 40][:5]:
                yield text_record("proverbs", "quotation", "proverb", "saying", "traditional", "anyone",
                                  f'Write a short traditional saying, like those collected in "{title}".', quote)
            continue
        years = life_years(text)
        if not years or years[1] > latest_death:
            continue
        for quote in wikiquote_quotes(text):
            yield text_record("quotes", "quotation", "quotation", "quotation", "memorable", "anyone",
                              f"Write a short, memorable saying in the voice of {title} ({years[0]}–{years[1]}).",
                              quote)


def read_wikiquote(fetcher, say=print, **_):
    say("  Wikiquote: reading the official dump as it arrives (stops early).")
    yield from wikiquote_records(dump_pages(stream_dump(fetcher, WIKIQUOTE_URL)))


# ====================================================================== recipes (the reference library's cookbooks)

def cookbooks_module():
    """textbooks/cookbooks.py from this repository (the reference library's recipe readers), or None when the
    writing kit is used on its own."""
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "textbooks")
    if not os.path.exists(os.path.join(folder, "cookbooks.py")):
        return None
    if folder not in sys.path:
        sys.path.append(folder)
    try:
        import cookbooks
        return cookbooks
    except Exception:
        return None


def recipe_text(recipe):
    """A recipe (from cookbooks.nhlbi_recipe or nhs_recipe) as plain text: the body's headings, lists and steps."""
    body = re.sub(r"(?i)<li\b[^>]*>", "\n- ", recipe["body"])
    body = re.sub(r"(?i)<h(\d)\b[^>]*>", "\n\n", body)
    text = re.sub(r"\n{3,}", "\n\n", html_text(body)).strip()
    return re.sub(r"\n\n(?=- )", "\n", text)


def recipe_records(recipes, publisher, uk=False):
    for recipe in recipes:
        text = recipe_text(recipe)
        if words(text) < 60:
            continue
        note = " Use metric measures, Celsius and gas marks, and British cooking words." if uk else ""
        yield text_record(publisher, "recipe", "recipe", "recipe", "plain and practical", "home cooks",
                          f'Write a recipe for "{recipe["title"]}", with the ingredient list and numbered steps, in the '
                          f"plain style of the {publisher}.{note}", text)


def read_recipes(fetcher, say, site, limit):
    cb = cookbooks_module()
    if not cb:
        say("  Recipes: the reference library's cookbook reader (textbooks/cookbooks.py) is not here; skipped.")
        return
    if site == "nhlbi":
        links, n = [], 0
        while n < 30:
            page = fetcher.get(f"{cb.NHLBI_RECIPES}?page={n}").decode("utf-8", "replace")
            found = [urllib.parse.urljoin(cb.NHLBI_SITE, h) for h in re.findall(
                r'href="(/health/heart-healthy-living/healthy-foods/healthy-eating-recipes/[a-z0-9-]+)"', page)]
            new = [u for u in dict.fromkeys(found) if u not in links]
            if not new:
                break
            links += new
            n += 1
        parse, publisher, uk = cb.nhlbi_recipe, "National Heart, Lung, and Blood Institute (NHLBI)", False
    else:
        page = fetcher.get(cb.NHS_RECIPES).decode("utf-8", "replace")
        links = list(dict.fromkeys(urllib.parse.urljoin(cb.NHS_SITE, h) for h in re.findall(
            r'href="(/healthier-families/recipes/[a-z0-9-]+/)"', page)))
        parse, publisher, uk = cb.nhs_recipe, "NHS Healthier Families recipes", True
    say(f"  Recipes: {len(links)} pages listed by the {publisher}; reading {min(limit, len(links))}.")
    recipes = []
    for link in spread(links, limit):
        recipe = parse(fetcher.get(link).decode("utf-8", "replace"), link)
        if recipe:
            recipes.append(recipe)
    yield from recipe_records(recipes, publisher, uk)


def read_recipes_nhlbi(fetcher, say=print, limit=80, **_):
    yield from read_recipes(fetcher, say, "nhlbi", limit)


def read_recipes_nhs(fetcher, say=print, limit=80, **_):
    yield from read_recipes(fetcher, say, "nhs", limit)


# ====================================================================== the sources and the ones left out

def sources(Source, OPEN, SHARE_ALIKE, PERSONAL):
    """The Source entries for writing_sources.SOURCES (it passes its own Source class and licence classes in, so
    this file does not import it)."""
    PD = "Public domain (US government work)"
    PD_URL = "https://www.usa.gov/government-copyright"
    return [
        Source(key="govblogs", name="US agency blogs and articles (NASA, VA VAntage Point, FDA Consumer Updates, "
               "National Park Service, Energy.gov)", licence=PD, licence_class=OPEN, licence_url=PD_URL,
               credit="NASA, the US Department of Veterans Affairs, the US Food and Drug Administration, the National "
                      "Park Service and the US Department of Energy",
               home="https://www.nasa.gov/, https://news.va.gov/, https://www.fda.gov/consumers/consumer-updates, "
                    "https://www.nps.gov/, https://www.energy.gov/", reader="read_govblogs",
               notes="Feeds with whole posts (NASA, VAntage Point), FDA's Consumer Updates feed and pages (FDA's "
                     "robots.txt asks for 30 seconds between pages), and articles listed in the NPS and Energy.gov "
                     "sitemaps.",
               warnings=["VAntage Point and NASA sometimes publish guest posts by people outside government, and "
                         "pages may quote others; those parts keep their writers' copyright."]),
        Source(key="obama_social", name="Obama White House archived tweets (@POTUS44, @ObamaWhiteHouse, @FLOTUS44)",
               licence="Public domain (presidential records, US government work)", licence_class=OPEN,
               licence_url=PD_URL, credit="The Obama White House; archived by the National Archives (Barack Obama "
               "Presidential Library)", home="https://www.obamalibrary.gov/digital-research-room/archived-white-house-"
               "websites-and-social-media", reader="read_obama_social",
               notes="The tweets.csv files in the zip downloads the library links to; retweets left out, t.co links "
                     "shown as [link]."),
        Source(key="loc_letters", name="Library of Congress By the People transcriptions: 19th-century letters and "
               "diaries", licence="No known copyright (volunteer transcriptions; the documents are 19th-century and "
               "in the public domain)", licence_class=OPEN, licence_url="https://www.loc.gov/legal/",
               credit="Library of Congress, By the People volunteers", home="https://www.loc.gov/collections/"
               "selected-datasets/", reader="read_loc_letters",
               notes="The CSV datasets the Library publishes on loc.gov (crowd.loc.gov itself is closed to programs). "
                     "Each README says the text 'is subject to no known copyright restrictions and is free to use and "
                     "re-use'. Only 19th-century papers are used (Anthony, Stanton, Douglass, Fleetwood, Dickinson, "
                     "Civil War soldiers and women, Garfield, Gibson, Antrim, Holt, Lincoln)."),
        Source(key="persuade", name="PERSUADE 2.0 corpus (US students' argumentative essays)", licence="CC BY 4.0",
               licence_class=OPEN, licence_url="https://creativecommons.org/licenses/by/4.0/",
               credit="Scott Crossley, Perpetual Baffour, Yu Tian, Alex Franklin, Meg Benner and Ulrich Boser "
                      "(Vanderbilt University and The Learning Agency Lab)",
               home="https://github.com/scrosseye/persuade_corpus_2.0", reader="read_persuade",
               notes="The repository's README states CC BY 4.0. The CSV is on Google Drive, which closes downloads to "
                     "programs, so the owner downloads it in a browser (--local-file persuade=...).",
               warnings=["The essays are by students in grades 6 to 12; they keep their spelling and grammar "
                         "mistakes, which is what learner writing is like."]),
        Source(key="bawe", name="British Academic Written English corpus (BAWE)",
               licence="BAWE licence through the Oxford Text Archive (CC BY-NC-SA)", licence_class=PERSONAL,
               licence_url="https://creativecommons.org/licenses/by-nc-sa/3.0/",
               credit="Hilary Nesi, Sheena Gardner, Paul Thompson and Paul Wickens (Universities of Warwick, Reading "
                      "and Oxford Brookes), Oxford Text Archive", home="https://llds.ling-phil.ox.ac.uk/",
               reader="read_bawe", notes="Read from the zip the owner downloads after accepting the licence "
                                          "(--local-file bawe=...). Non-commercial, so personal use only.",
               warnings=["British English (UK spelling and university conventions); every instruction says so."]),
        Source(key="imdb", name="Large Movie Review Dataset (IMDb reviews, Stanford)",
               licence="No licence stated; released for research", licence_class=PERSONAL,
               licence_url="https://ai.stanford.edu/~amaas/data/sentiment/",
               credit="Andrew L. Maas and others (Stanford University), from IMDb users' reviews",
               home="https://ai.stanford.edu/~amaas/data/sentiment/", reader="read_imdb",
               notes="The training reviews, positive and negative in turn, with the viewer's rating."),
        Source(key="yelp", name="Yelp Open Dataset (reviews)", licence="Yelp Dataset Terms of Use (personal, "
               "educational and academic use only)", licence_class=PERSONAL, licence_url="https://www.yelp.com/dataset",
               credit="Yelp Inc. and its reviewers", home="https://www.yelp.com/dataset", reader="read_yelp",
               notes="Yelp's robots.txt closes the download page to programs and the terms are accepted in a browser, "
                     "so the owner downloads the file (--local-file yelp=...).",
               warnings=["Use it only if you agree that Yelp's Dataset Terms of Use allow your use: they allow "
                         "personal, educational and academic use and forbid commercial use and sharing."]),
        Source(key="python_lists", name="Python mailing lists (tutor, python-list)", licence="Writers keep copyright "
               "(public archive)", licence_class=PERSONAL, licence_url="https://mail.python.org/archives/",
               credit="The writers of the Python mailing lists; archive by the Python Software Foundation",
               home="https://mail.python.org/archives/", reader="read_python_lists",
               notes="Through the archive's own API (HyperKitty); its robots.txt closes only the bulk export "
                     "addresses, which the kit does not use."),
        Source(key="gharchive", name="GitHub issues and issue comments (GH Archive)", licence="Writers keep copyright; "
               "GitHub Acceptable Use Policies", licence_class=PERSONAL,
               licence_url="https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-"
                           "policies", credit="GitHub users; GH Archive (Ilya Grigorik)", home="https://www.gharchive.org/",
               reader="read_gharchive",
               notes="Public events from a few hours of GH Archive's hourly files: issues opened and comments on issues "
                     "(not pull requests, not bots).",
               warnings=["GitHub's Acceptable Use Policies allow public information to be used for research and "
                         "archiving, not for spam or selling people's details; keep this personal (your own model "
                         "only) and do not share the files."]),
        Source(key="sam", name="SAM.gov contract notices and requests for proposals", licence=PD, licence_class=OPEN,
               licence_url=PD_URL, credit="US federal agencies, through SAM.gov (General Services Administration)",
               home="https://sam.gov/", reader="read_sam",
               notes="The Get Opportunities API with the key in SAM_GOV_API_KEY. A personal key allows about ten "
                     "requests a day; the cache keeps what was read."),
        Source(key="fedreg_rfi", name="Federal Register requests for information and requests for comments",
               licence=PD, licence_class=OPEN, licence_url=PD_URL, credit="US federal agencies, Office of the Federal "
               "Register", home="https://www.federalregister.gov/developers/documentation/api/v1",
               reader="read_fedreg_rfi", notes="The free API (no key) and each notice's plain text; paperwork notices "
                                                "and meeting notices left out."),
        Source(key="fed_speeches", name="Federal Reserve Board speeches", licence="Public domain (Federal Reserve "
               "Board: 'information on Board's website is in the public domain')", licence_class=OPEN,
               licence_url="https://www.federalreserve.gov/disclaimer.htm", credit="Board of Governors of the Federal "
               "Reserve System", home="https://www.federalreserve.gov/newsevents/speeches.htm",
               reader="read_fed_speeches", notes="Speeches by the chair and governors from the yearly lists; "
                                                  "footnotes left out."),
        Source(key="crec", name="Congressional Record floor speeches and debates (GovInfo)", licence=PD,
               licence_class=OPEN, licence_url=PD_URL, credit="US Congress, Government Publishing Office (GovInfo)",
               home="https://www.govinfo.gov/app/collection/crec", reader="read_crec",
               notes="A few days from each chosen year: one-minute speeches, Senate floor speeches, debates (kept whole "
                     "in the transcripts folder) and Extensions of Remarks; procedural parts left out. congress.gov "
                     "blocks AI training, so GovInfo is used."),
        Source(key="wikivoyage", name="English Wikivoyage (travel guides)", licence="CC BY-SA 4.0",
               licence_class=SHARE_ALIKE, licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
               credit="Wikivoyage contributors", home="https://dumps.wikimedia.org/enwikivoyage/",
               reader="read_wikivoyage", notes="Sections such as Understand, Get in, See, Eat and Sleep from the "
                                                "official dump, with the listings written out as sentences."),
        Source(key="wikiquote", name="English Wikiquote (quotations and proverbs)", licence="CC BY-SA 4.0",
               licence_class=SHARE_ALIKE, licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
               credit="Wikiquote contributors", home="https://dumps.wikimedia.org/enwikiquote/",
               reader="read_wikiquote",
               notes="Only quotations of people who died by 1955 (so the words themselves are old) and the proverb "
                     "pages; films, television and living people are left out."),
        Source(key="recipes_nhlbi", name="NHLBI heart-healthy recipes (the reference library's cookbook)",
               licence="Public domain (NHLBI: 'Most of the information on the NHLBI website is in the public domain')",
               licence_class=OPEN, licence_url=PD_URL, credit="National Heart, Lung, and Blood Institute (NIH)",
               home="https://www.nhlbi.nih.gov/health/heart-healthy-living/healthy-foods/healthy-eating-recipes",
               reader="read_recipes_nhlbi", notes="Read with the reference library's own recipe reader "
                                                   "(textbooks/cookbooks.py), so the text matches the built book."),
        Source(key="recipes_nhs", name="NHS Healthier Families recipes (the reference library's cookbook)",
               licence="Open Government Licence v3.0", licence_class=OPEN,
               licence_url="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
               credit="NHS England (Better Health, Healthier Families); contains public sector information licensed "
                      "under the Open Government Licence v3.0", home="https://www.nhs.uk/healthier-families/recipes/",
               reader="read_recipes_nhs", notes="Read with the reference library's own recipe reader.",
               warnings=["British English, metric measures and UK food names; every instruction says so."]),
    ]


NOT_USED = [
    ("NIH Director's Blog (directorsblog.nih.gov)",
     "The blog's site does not answer (its robots.txt cannot be read, which under RFC 9309 means stay away), and "
     "www.nih.gov answers programs with 403 Forbidden."),
    ("CDC blogs (blogs.cdc.gov)", "Retired: the address now sends visitors to the CDC home page; no archive download."),
    ("USDA blog, Department of Labor blog (blog.dol.gov) and NOAA news",
     "These sites answer programs with 403 Forbidden (even their robots.txt), so the kit leaves them alone."),
    ("Agency email newsletters (GovDelivery bulletins)",
     "No public archive or bulk download; they are sent by email to subscribers."),
    ("Archived social media of the Trump and Biden administrations and of agencies (National Archives)",
     "Their pages offer no download files; the records are in the National Archives catalogue, whose robots.txt "
     "turns programs away. Only the Obama White House tweet archives have download files (used: obama_social)."),
    ("Founders Online (founders.archives.gov)",
     "The site answers programs with an empty browser check (a challenge page), so it cannot be read without a web "
     "browser, and its documents are the university presses' editions for non-commercial use (personal use at best)."),
    ("By the People website (crowd.loc.gov)",
     "Its robots.txt turns all programs away. The same transcriptions are published as datasets on loc.gov, which "
     "the kit uses instead (loc_letters)."),
    ("Library of Congress letters from the 20th century (Rosa Parks, Branch Rickey, Carrie Chapman Catt, Georgia "
     "O'Keeffe and Alfred Stieglitz, Leonard Bernstein, George S. Patton)",
     "The transcriptions are free, but these letters can still be under their writers' copyright, so they were left "
     "out."),
    ("MICUSP (Michigan Corpus of Upper-level Student Papers)",
     "Its site does not answer, there is no bulk download, and its terms allow only non-commercial study through "
     "its own web interface."),
    ("ASAP automated essay scoring essays (Kaggle)",
     "Recorded only: Kaggle's competition rules limit the data to the competition, and the download needs a Kaggle "
     "login."),
    ("Mozilla Bugzilla (bugzilla.mozilla.org)",
     "Its robots.txt closes the REST interface and bulk addresses to programs (only single bug pages, with a 30-second "
     "wait), and the comments keep their writers' copyright with no licence stated."),
    ("Mozilla mailing lists", "lists.mozilla.org turns programs away in its robots.txt; the lists moved to Google "
     "Groups, which has no official bulk download, and to Discourse forums."),
    ("Python mailing list bulk exports (mail.python.org .../export/)",
     "Its robots.txt closes the export addresses to programs; the kit reads the same lists through the archive's "
     "API instead (python_lists)."),
    ("CFPB consumer complaint narratives",
     "The Consumer Financial Protection Bureau's public complaint API no longer includes the consumers' own words, "
     "only the categories."),
    ("USPTO patent full texts",
     "The old bulk site (bulkdata.uspto.gov) is gone; the new Open Data Portal needs a key tied to an identity check, "
     "and its weekly full-text files are zip files of a gigabyte or more that cannot be read in part. Not built yet."),
    ("Kiwix copies of Wikivoyage and Wikiquote (download.kiwix.org)",
     "Its robots.txt turns programs away; the kit reads Wikimedia's own dumps instead."),
    ("Yelp and BAWE downloads by program",
     "Yelp's robots.txt closes its dataset page, and BAWE needs the licence accepted on the Oxford Text Archive; "
     "both are read only from files the owner downloads in a browser."),
]
