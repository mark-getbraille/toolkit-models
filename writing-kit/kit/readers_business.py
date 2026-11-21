"""Business and modern American writing readers for the Writing Kit (added at the owner's request; business
communication comes first). writing_sources.py lists each with its licence; sources-not-used.txt lists the ones
checked and left out.

Business:
  read_edgar        SEC EDGAR: company press releases (8-K exhibit 99.1), letters to the SEC staff (CORRESP) and
                    letters to shareholders in proxy statements. Public records. EDGAR asks every program to say who
                    is asking: the kit uses the computer setting SEC_USER_AGENT (for example "Your Name
                    you@example.com"), which stays in your settings, never in these files; without it EDGAR is
                    skipped.
  read_abcd         ABCD, the Action-Based Conversations Dataset (ASAPP, MIT): customer service chats.
  read_openstax_business  the business communication, management and ethics chapters of OpenStax's CC BY books
                    (Introduction to Business, Business Ethics, Principles of Management, Organizational Behavior).
Modern American English:
  read_oanc         the Open American National Corpus (about 15 million words, free for any use): telephone and
                    face-to-face conversations, fundraising letters, Slate magazine articles, government reports.
  read_wikinews     English Wikinews articles (CC BY 2.5), from the official dump.
  read_nsf          National Science Foundation award abstracts (public domain), from its free API.
  read_presidential the Compilation of Presidential Documents on GovInfo (remarks and speeches; public domain).
  read_blog_feeds   Pluralistic (Cory Doctorow, CC BY 4.0) and Global Voices (CC BY 3.0), from their own feeds.
  read_fineweb      a small sample of FineWeb (Hugging Face, ODC-By) web pages that look conversational (forums,
                    reviews, questions and answers), through the Hugging Face dataset viewer interface.
"""

import gzip
import html
import io
import json
import os
import re
import urllib.parse
import zipfile
import bz2

EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index?q={q}&forms={forms}&from={start}"
EDGAR_DOC = "https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{name}"
EDGAR_KINDS = [
    # (search words, form, kind of writing)
    ('"announced today"', "8-K", "press release"),
    ('"response to the comment"', "CORRESP", "letter to the SEC staff"),
    ('"Dear Fellow Shareholders"', "DEF 14A", "letter to shareholders"),
]
ABCD_URL = "https://raw.githubusercontent.com/asappresearch/abcd/master/data/abcd_v1.1.json.gz"
OPENSTAX_RAW = "https://raw.githubusercontent.com/openstax/{repo}/main/"
OPENSTAX_BOOKS = [("osbooks-introduction-business", "introduction-business-2e"),
                  ("osbooks-business-ethics", "business-ethics"),
                  ("osbooks-principles-of-management-bundle", "principles-management"),
                  ("osbooks-principles-of-management-bundle", "organizational-behavior")]
BUSINESS_TOPICS = re.compile(r"(?i)communicat|writing|meeting|negotiat|memo|e-?mail|letter|report|presentation|"
                             r"listening|feedback|conflict|customer|sales|marketing|proposal|team|interview|"
                             r"diversity|ethic|leadership|decision|motivat|change")
OANC_URL = "https://github.com/nancyide/anc-website/releases/download/datasets-2026-09-25/OANC-1.0.1-UTF8.zip"
WIKINEWS_URL = "https://dumps.wikimedia.org/enwikinews/latest/enwikinews-latest-pages-articles.xml.bz2"
NSF_API = ("https://api.nsf.gov/services/v1/awards.json?keyword={kw}&printFields=id,title,abstractText,awardee"
           "&rpp=25&offset={offset}")
NSF_WORDS = ["community", "small business", "students", "workforce", "public health", "climate"]
DCPD_SITEMAP = "https://www.govinfo.gov/sitemap/DCPD_{year}_sitemap.xml"
DCPD_HTM = "https://www.govinfo.gov/content/pkg/{pkg}/html/{pkg}.htm"
FEEDS = [("https://pluralistic.net/feed/", "Pluralistic", "a personal blog about technology and politics"),
         ("https://globalvoices.org/feed/", "Global Voices", "a citizen media news site")]
FINEWEB_ROWS = ("https://datasets-server.huggingface.co/rows?dataset=HuggingFaceFW/fineweb&config=sample-10BT"
                "&split=train&offset={offset}&length=100")
CONVERSATIONAL_URL = re.compile(r"(?i)forum|thread|/t/|topic|review|faq|question|answers|community|discussion|"
                                r"advice|ask|comments")


def html_text(raw):
    """Plain text from HTML: scripts and styles dropped, paragraphs and line breaks kept."""
    raw = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</h\d>|</li>|</tr>", "\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = "\n".join(ln.strip() for ln in text.split("\n") if not re.fullmatch(r"\s*[^\w\s]{2,}\s*", ln))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def cap_words(text, n=2500):
    words = text.split(" ")
    return text if len(words) <= n else " ".join(words[:n]) + " [...]"


# ----------------------------------------------------------------- SEC EDGAR

def edgar_hits(data):
    """[(cik, folder, file name, company)] from one EDGAR full-text search answer (JSON)."""
    out = []
    for hit in json.loads(data).get("hits", {}).get("hits", []):
        adsh, _, name = hit.get("_id", "").partition(":")
        src = hit.get("_source", {})
        ciks = src.get("ciks") or []
        if adsh and name and ciks:
            company = (src.get("display_names") or [""])[0]
            out.append((str(int(ciks[0])), adsh.replace("-", ""), name, re.sub(r"\s*\(CIK.*", "", company)))
    return out


def edgar_instruction(kind, company, text):
    """The instruction for one EDGAR document."""
    company = company or "a company"
    first = next((ln.strip() for ln in text.splitlines() if len(ln.split()) >= 4), "")
    if kind == "press release":
        return f'Write a press release for {company} with this headline: "{first[:200]}".'
    if kind == "letter to the SEC staff":
        return (f"Write a formal business letter from {company} to the staff of the US Securities and Exchange "
                "Commission, answering the staff's comments on a filing point by point, politely and precisely.")
    return f"Write a letter from the leaders of {company} to its shareholders, inviting them to the annual meeting."


def read_edgar(fetcher, say=print, per_kind=40, **_):
    agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not agent:
        say("  SEC EDGAR: skipped. EDGAR asks every program to give a name and email address; put yours in the "
            "computer setting SEC_USER_AGENT (see READ ME FIRST.txt).")
        return
    fetcher.extra_headers["User-Agent"] = agent
    try:
        for q, form, kind in EDGAR_KINDS:
            got, start = 0, 0
            while got < per_kind and start < 400:
                hits = edgar_hits(fetcher.get(EDGAR_SEARCH.format(q=urllib.parse.quote(q),
                                                                  forms=urllib.parse.quote(form), start=start)))
                if not hits:
                    break
                start += len(hits)
                for cik, folder, name, company in hits:
                    if form == "8-K" and not re.search(r"(?i)ex-?99", name):
                        continue
                    text = html_text(fetcher.get(EDGAR_DOC.format(cik=cik, folder=folder, name=name))
                                     .decode("utf-8", "replace"))
                    if len(text.split()) < 80:
                        continue
                    yield {"type": "text", "group": kind, "kind": kind, "form": kind, "tone": "formal",
                           "audience": "investors and the public" if kind != "letter to the SEC staff" else "the SEC",
                           "instruction": edgar_instruction(kind, company, text), "response": cap_words(text)}
                    got += 1
                    if got >= per_kind:
                        break
    finally:
        fetcher.extra_headers.pop("User-Agent", None)


# ----------------------------------------------------------------- ABCD customer service chats

def read_abcd(fetcher, say=print, **_):
    say("  ABCD: downloading the official file from GitHub (37 MB).")
    data = json.loads(gzip.decompress(fetcher.get(ABCD_URL)))
    for convo in data["train"]:
        turns = []
        for who, text in convo["original"]:
            who = "Agent" if who == "agent" else "Customer" if who == "customer" else None
            if not who:
                continue
            if turns and turns[-1][0] == who:
                turns[-1] = (who, turns[-1][1] + " " + text)
            else:
                turns.append((who, text))
        flow = convo.get("scenario", {}).get("flow", "").replace("_", " ")
        yield {"type": "chat", "turns": turns, "group": flow or "abcd",
               "setting": f"an online customer service chat for a clothing shop ({flow})"}


# ----------------------------------------------------------------- OpenStax business books (CC BY 4.0)

def cnxml_text(xml):
    """(title, plain text) of an OpenStax CNXML module: paragraphs, list items and headings, in order."""
    title = html.unescape(re.sub(r"<[^>]+>", "", (re.search(r"<title>(.*?)</title>", xml, re.S) or [None, ""])[1]))
    body = xml.split("<content>", 1)[-1]
    body = re.sub(r"(?s)<(figure|table|media|equation|exercise|glossary)\b.*?</\1>", " ", body)
    body = re.sub(r"(?i)</(para|item|title|p)>", "\n", body)
    text = html.unescape(re.sub(r"<[^>]+>", "", body))
    text = "\n".join(re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines())
    return title.strip(), re.sub(r"\n{2,}", "\n\n", text).strip()


def read_openstax_business(fetcher, say=print, per_book=40, **_):
    for repo, slug in OPENSTAX_BOOKS:
        base = OPENSTAX_RAW.format(repo=repo)
        collection = fetcher.get(f"{base}collections/{slug}.collection.xml").decode("utf-8", "replace")
        modules = re.findall(r'<col:module document="(m\d+)"', collection) or \
            re.findall(r'document="(m\d+)"', collection)
        say(f"  OpenStax {slug}: {len(modules)} sections; reading the business communication ones.")
        got = 0
        for module in modules:
            xml = fetcher.get(f"{base}modules/{module}/index.cnxml").decode("utf-8", "replace")
            title, text = cnxml_text(xml)
            if not BUSINESS_TOPICS.search(title) or len(text.split()) < 150:
                continue
            yield {"type": "text", "group": slug, "kind": "guide", "form": "textbook section", "tone": "formal",
                   "audience": "business students",
                   "instruction": f'Write a clear textbook section titled "{title}" for a business course, '
                                  "explaining it in plain American English with practical examples.",
                   "response": cap_words(text)}
            got += 1
            if got >= per_book:
                break


# ----------------------------------------------------------------- Open American National Corpus

OANC_GENRES = [("spoken/telephone/switchboard", "phone"), ("spoken/face-to-face/charlotte", "face"),
               ("written_1/letters/icic", "letter"), ("written_1/journal/slate", "slate"),
               ("written_2/technical/government", "government"), ("written_2/travel_guides", "travel")]


def oanc_turns(text):
    """[(speaker, words)] from an OANC conversation file: blocks separated by blank lines are turns, by two
    speakers taking turns."""
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n\s*\n", text)]
    blocks = [b for b in blocks if b]
    return [("Speaker " + "AB"[i % 2], b) for i, b in enumerate(blocks)]


def oanc_records(zip_bytes, per_genre=60):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = sorted(n for n in z.namelist() if n.endswith(".txt"))
        for genre, kind in OANC_GENRES:
            files = [n for n in names if f"/data/{genre}/" in n][:per_genre]
            for name in files:
                text = z.read(name).decode("utf-8", "replace").strip()
                plain = re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n\s*(\n\s*)+", "\n\n", text))
                if kind in ("phone", "face"):
                    turns = oanc_turns(text)
                    if len(turns) >= 4:
                        yield {"type": "chat", "turns": turns, "group": kind, "style": "speech",
                               "setting": "a telephone conversation between two strangers" if kind == "phone"
                               else "a recorded face-to-face conversation", "raw": plain,
                               "raw_name": os.path.basename(name)}
                elif kind == "letter":
                    yield {"type": "text", "group": kind, "kind": "fundraising letter", "form": "letter",
                           "tone": "warm and persuasive", "audience": "supporters",
                           "instruction": "Write a fundraising letter for a local charity asking supporters for a "
                                          "donation. Make it warm and persuasive.", "response": plain}
                else:
                    title = next((ln.strip() for ln in plain.splitlines() if ln.strip()), "")[:150]
                    what = {"slate": ("a magazine article for Slate", "lively and conversational"),
                            "government": ("a report for a US government agency", "formal"),
                            "travel": ("a travel guide section", "friendly and informative")}[kind]
                    yield {"type": "text", "group": kind, "kind": kind, "form": what[0], "tone": what[1],
                           "audience": "general readers",
                           "instruction": f'Write {what[0]} titled "{title}". Keep it {what[1]}.',
                           "response": cap_words(plain)}


def read_oanc(fetcher, say=print, local_file=None, **_):
    """Records from the OANC. The official download is a GitHub release file, and GitHub's robots.txt closes
    "/*/*/download/*" to programs, so normally the owner downloads OANC-1.0.1-UTF8.zip once in a web browser (from
    anc.org/data/oanc/download/) and passes it with --oanc-file; the kit tries the address itself only without it."""
    if local_file:
        with open(local_file, "rb") as f:
            yield from oanc_records(f.read())
        return
    say("  Open American National Corpus: trying the official file (330 MB). If GitHub's robots.txt refuses, "
        "download OANC-1.0.1-UTF8.zip in a browser from anc.org and use --oanc-file.")
    yield from oanc_records(fetcher.get(OANC_URL))


# ----------------------------------------------------------------- Wikinews (CC BY 2.5)

def read_wikinews(fetcher, say=print, **_):
    import readers_more
    say("  Wikinews: reading the official dump as it arrives (stops early).")
    resp = fetcher.open_stream(WIKINEWS_URL)
    try:
        title, ns, buf, inside = "", "", [], False
        for raw in bz2.BZ2File(resp):
            line = raw.decode("utf-8", "replace")
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
                wikitext = html.unescape("".join(buf).replace("</text>", ""))
                buf = []
                if wikitext.lstrip().upper().startswith("#REDIRECT"):
                    continue
                body = re.split(r"\n==\s*(Sources|Related news|External links)", wikitext)[0]
                text = readers_more.wiki_plain(body)
                text = re.sub(r"(?m)^\s*(\[\[)?(Category|File|Image):.*$", "", text)
                text = re.sub(r"\n{3,}", "\n\n", text).strip()
                if len(text.split()) >= 120:
                    yield {"type": "text", "group": "wikinews", "kind": "news report", "form": "news article",
                           "tone": "neutral", "audience": "general readers",
                           "instruction": f'Write a short, neutral news report with the headline "{title}".',
                           "response": cap_words(text)}
    finally:
        resp.close()


# ----------------------------------------------------------------- NSF award abstracts

def read_nsf(fetcher, say=print, pages=2, **_):
    for word in NSF_WORDS:
        for page in range(pages):
            data = json.loads(fetcher.get(NSF_API.format(kw=urllib.parse.quote(word), offset=1 + 25 * page)))
            for award in data.get("response", {}).get("award", []):
                text = html.unescape(re.sub(r"<br\s*/?>", "\n", award.get("abstractText") or "")).strip()
                if len(text.split()) < 80:
                    continue
                yield {"type": "text", "group": word, "kind": "grant abstract", "form": "project summary",
                       "tone": "formal", "audience": "reviewers and the public",
                       "instruction": f'Write the public project summary for a research grant proposal titled '
                                      f'"{award.get("title", "").strip()}", explaining what it will do and why it '
                                      "matters, in plain language.", "response": text}


# ----------------------------------------------------------------- Presidential documents (GovInfo DCPD)

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def presidential_parts(text):
    """(title, body) of a presidential document's text, whether it has line breaks or is one long line."""
    m = re.match(r"\s*Administration of [^,\n]+, \d{4}\s+(.{3,200}?)\s+((?:" + MONTHS + r") \d{1,2}, \d{4})\s+(.*)",
                 text, re.S)
    if m:
        return m.group(1).strip(), m.group(3).strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 3:
        return "", ""
    return (lines[1], "\n".join(lines[2:])) if lines[0].startswith("Administration of") else \
        (lines[0], "\n".join(lines[1:]))


def read_presidential(fetcher, say=print, years=("2016", "2011", "2023"), per_year=30, **_):
    for year in years:
        sitemap = fetcher.get(DCPD_SITEMAP.format(year=year)).decode("utf-8", "replace")
        packages = re.findall(r"<loc>https://www\.govinfo\.gov/app/details/(DCPD-\d+)</loc>", sitemap)
        say(f"  Presidential documents: {len(packages)} listed for {year}; reading {per_year}.")
        for pkg in packages[:per_year]:
            text = html_text(fetcher.get(DCPD_HTM.format(pkg=pkg)).decode("utf-8", "replace"))
            title, body = presidential_parts(text)
            if not title:
                continue
            body = re.split(r"\nCategories:|\nNOTE:", body)[0]
            if len(body.split()) < 80:
                continue
            kind = "remarks" if re.match(r"(?i)remarks|address", title) else "statement" if \
                re.match(r"(?i)statement", title) else "letter" if re.match(r"(?i)letter|message", title) else \
                "presidential document"
            yield {"type": "text", "group": year, "kind": kind, "form": kind, "tone": "formal",
                   "audience": "the public", "instruction": f'Write the President\'s {kind}: "{title}".',
                   "response": cap_words(body), "raw": text, "raw_name": pkg + ".txt"}


# ----------------------------------------------------------------- open-licence blogs and news (feeds)

def feed_items(xml):
    """[(title, text)] from an RSS feed with full posts (content:encoded)."""
    out = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        title = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", (re.search(r"<title>(.*?)</title>", item, re.S)
                                                                  or [None, ""])[1])).strip()
        body = re.search(r"<content:encoded>(.*?)</content:encoded>", item, re.S)
        if body:
            out.append((title, html_text(re.sub(r"<!\[CDATA\[|\]\]>", "", body.group(1)))))
    return out


def read_blog_feeds(fetcher, say=print, **_):
    for url, name, what in FEEDS:
        for title, text in feed_items(fetcher.get(url).decode("utf-8", "replace")):
            if len(text.split()) < 100:
                continue
            yield {"type": "text", "group": name, "kind": "blog post", "form": "blog post", "tone": "conversational",
                   "audience": "readers", "instruction": f'Write a post for {what} titled "{title}".',
                   "response": cap_words(text)}


# ----------------------------------------------------------------- FineWeb sample (conversational pages)

def read_fineweb(fetcher, say=print, pages=20, **_):
    say("  FineWeb: reading a small sample through the Hugging Face dataset viewer.")
    for page in range(pages):
        data = json.loads(fetcher.get(FINEWEB_ROWS.format(offset=page * 100)))
        for row in data.get("rows", []):
            r = row.get("row", {})
            url, text = r.get("url", ""), r.get("text", "")
            host = urllib.parse.urlsplit(url).netloc
            if not CONVERSATIONAL_URL.search(url) or not 60 <= len(text.split()) <= 1500:
                continue
            if r.get("language") not in (None, "en"):
                continue
            kind = "review" if re.search(r"(?i)review", url) else "forum post" if \
                re.search(r"(?i)forum|thread|/t/|topic|discussion|community|comments", url) else "question and answer"
            yield {"type": "text", "group": host, "kind": kind, "form": kind, "tone": "casual",
                   "audience": "other readers online",
                   "instruction": f"Write a casual {kind} for a website, in everyday American English, like the "
                                  f"page at {host}.", "response": text}
