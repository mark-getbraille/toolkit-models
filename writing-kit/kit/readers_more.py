"""More readers for the Writing Kit: sources of colloquial, informal English added at the owner's request (old Usenet
groups, the Debian mailing lists, Ubuntu's IRC logs, conversation datasets, text messages, Wikipedia talk pages,
public-domain letters, real recorded conversations and public comments to US agencies). writing_sources.py lists
each with its licence; sources-not-used.txt lists the ones checked and left out.

Each reader reads only official addresses through fetch.Fetcher (robots.txt obeyed, AI-training refusals obeyed,
requests paced) and yields records of these kinds (build_dataset.py turns them into examples):
  email  {"type": "email", "subject", "body", "audience", "is_reply", "group", "attachments": [(name, bytes,
         content type)], "msg_id"}: a real message;
  chat   {"type": "chat", "turns": [(speaker, text), ...], "setting", "group"}: a conversation, from which the
         builder takes "write the next message" pairs;
  text   {"type": "text", "instruction", "response", "kind", "form", "tone", "audience", "group"}: a ready pair.
"""

import bz2
import csv
import email
import email.policy
import gzip
import html
import io
import json
import os
import re
import zipfile

USENET_ITEMS = [
    # (Internet Archive item, file in it): Giganews' Usenet collection, one mbox file per newsgroup.
    ("usenet-alt.vacation", "alt.vacation.20140307.mbox.gz"),
    ("usenet-misc.writing", "misc.writing.moderated.20140309.mbox.gz"),
    ("usenet-misc.writing", "misc.writing.20140823.mbox.gz"),
]
DEBIAN_LISTS = ["debian-user"]
IRC_CHANNELS = ["#ubuntu", "#ubuntu-offtopic"]
IRC_DAYS = ["2024/03/05", "2024/03/12", "2023/11/14", "2023/06/20", "2024/01/09", "2024/05/21", "2022/09/13",
            "2023/02/07", "2024/07/16", "2022/12/06"]
SMS_URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
GH = "https://raw.githubusercontent.com/"
TASKMASTER_URL = GH + "google-research-datasets/Taskmaster/master/TM-1-2019/woz-dialogs.json"
SGD_URL = GH + "google-research-datasets/dstc8-schema-guided-dialogue/master/train/dialogues_001.json"
MULTIWOZ_URL = GH + "budzianowski/multiwoz/master/data/MultiWOZ_2.2/train/dialogues_001.json"
TOPICAL_URL = GH + "alexa/Topical-Chat/master/conversations/valid_freq.json"
WIKITALK_URL = "https://dumps.wikimedia.org/simplewiki/latest/simplewiki-latest-pages-meta-current.xml.bz2"
GUTENBERG_MIRROR = "https://gutenberg.pglaf.org/"
SBC_BASE = "https://www.linguistics.ucsb.edu/sites/default/files/sitefiles/research/SBC/"
REGULATIONS_API = "https://api.regulations.gov/v4/"


# ----------------------------------------------------------------- email messages with their attachments

def parse_mail(raw):
    """(message, body text, attachments) from the bytes of one email or news article. The body is the first plain
    text part (or the HTML part as text); attachments are every part with a file name, as (name, bytes, type)."""
    msg = email.message_from_bytes(raw, policy=email.policy.compat32)
    body, files = "", []
    for part in msg.walk() if msg.is_multipart() else [msg]:
        if part.is_multipart():
            continue
        name = part.get_filename()
        ctype = part.get_content_type()
        try:
            data = part.get_payload(decode=True) or b""
        except Exception:
            data = b""
        if name:
            files.append((name, data, ctype))
        elif ctype == "text/plain" and not body:
            body = data.decode(part.get_content_charset() or "latin-1", "replace")
        elif ctype == "text/html" and not body:
            body = html.unescape(re.sub(r"<[^>]+>", " ", data.decode(part.get_content_charset() or "latin-1",
                                                                       "replace")))
    # old Usenet binaries written into the text (uuencode) are not text: leave them out of the body
    body = re.sub(r"(?ms)^begin [0-7]{3} \S+\n.*?^end$", "[uuencoded file left out]", body)
    return msg, body, files


def mail_record(raw, group, audience):
    """An email record from the bytes of one message, or None."""
    try:
        msg, body, files = parse_mail(raw)
    except Exception:
        return None
    subject = str(msg.get("Subject", "") or "")
    return {"type": "email", "subject": subject, "body": body, "audience": audience,
            "is_reply": bool(re.match(r"\s*re\s*:", subject, re.I)) or bool(msg.get("In-Reply-To")),
            "group": group, "attachments": files, "msg_id": str(msg.get("Message-ID", "") or ""),
            "known_names": [str(msg.get(k, "") or "") for k in ("To", "Cc", "Newsgroups")],
            "writer_names": [str(msg.get("From", "") or "")]}


def mbox_messages(lines):
    """The raw bytes of each message in an mbox, read line by line (lines are bytes)."""
    current = []
    for line in lines:
        if line.startswith(b"From ") and current:
            yield b"".join(current)
            current = []
        if current or line.startswith(b"From "):
            current.append(line[1:] if line.startswith(b">From ") else line)
    if current:
        yield b"".join(current)


# ----------------------------------------------------------------- Usenet (Internet Archive, Giganews collection)

def read_usenet(fetcher, say=print, items=None, **_):
    """Email records from the Giganews Usenet mbox files on the Internet Archive, read as they arrive."""
    for item, name in items or USENET_ITEMS:
        url = f"https://archive.org/download/{item}/{name}"
        say(f"  Usenet: reading {name} from the Internet Archive as it arrives.")
        resp = fetcher.open_stream(url)
        try:
            with gzip.GzipFile(fileobj=resp) as lines:
                for raw in mbox_messages(lines):
                    rec = mail_record(raw, name.split(".2")[0], "a newsgroup")
                    if rec:
                        yield rec
        finally:
            resp.close()


# ----------------------------------------------------------------- Debian mailing lists (lists.debian.org)

def debian_message(page):
    """An email record from one MHonArc page of lists.debian.org, or None."""
    m = re.search(r"<!--X-Body-of-Message-->(.*?)<!--X-Body-of-Message-End-->", page, re.S)
    if not m:
        return None
    body = re.sub(r"(?i)<br\s*/?>|</p>", "\n", m.group(1))
    body = re.sub(r"(?is)<blockquote[^>]*>(.*?)</blockquote>",
                  lambda q: "\n".join("> " + ln for ln in q.group(1).split("\n")), body)
    body = html.unescape(re.sub(r"<[^>]+>", "", body))
    subject = html.unescape((re.search(r"<title>(.*?)</title>", page, re.S) or [None, ""])[1]).strip()
    links = re.findall(r'<a href="(msg\d+/[^"]+)"', page)
    return {"type": "email", "subject": subject, "body": body, "audience": "the members of a mailing list",
            "is_reply": subject.lower().startswith("re:"), "attachment_links": links,
            "known_names": [], "writer_names": []}


def read_debian(fetcher, say=print, lists=None, months=None, pages=60, **_):
    """Email records from the public Debian list archives, one page at a time."""
    for name in lists or DEBIAN_LISTS:
        for month in months or ["2024/03", "2023/10"]:
            base = f"https://lists.debian.org/{name}/{month}/"
            index = fetcher.get(base + "maillist.html").decode("utf-8", "replace")
            for page_name in sorted(set(re.findall(r'href="(msg\d+\.html)"', index)))[:pages]:
                rec = debian_message(fetcher.get(base + page_name).decode("utf-8", "replace"))
                if rec:
                    files = []
                    for link in rec.pop("attachment_links"):
                        try:
                            files.append((link.split("/")[-1], fetcher.get(base + link), ""))
                        except Exception:
                            pass
                    rec.update(group=name, attachments=files, msg_id=base + page_name)
                    yield rec


# ----------------------------------------------------------------- Ubuntu IRC logs (irclogs.ubuntu.com)

IRC_LINE = re.compile(r"^\[(\d\d:\d\d)\] <([^>]+)> (.*)$")


def irc_turns(text):
    """[(nick, message)] from one day's plain-text IRC log (joins, parts and actions left out)."""
    turns = []
    for line in text.splitlines():
        m = IRC_LINE.match(line)
        if m and not m.group(2).lower().endswith(("bot", "-bot")):
            turns.append((m.group(2), m.group(3)))
    return turns


def read_irc(fetcher, say=print, channels=None, days=None, **_):
    """Chat records: each day's log of a channel, cut into pieces of 40 lines."""
    for day in days or IRC_DAYS:
        for channel in channels or IRC_CHANNELS:
            url = f"https://irclogs.ubuntu.com/{day}/{channel.replace('#', '%23')}.txt"
            try:
                turns = irc_turns(fetcher.get(url).decode("utf-8", "replace"))
            except Exception as err:                     # a channel with no log that day
                if "robots" in str(err):
                    raise
                continue
            for i in range(0, len(turns), 40):
                yield {"type": "chat", "turns": turns[i:i + 40], "setting": f"the Ubuntu IRC help channel {channel}",
                       "group": channel, "style": "irc"}


# ----------------------------------------------------------------- SMS Spam Collection (UCI), the real texts only

def sms_records(zip_bytes):
    """Text records from the SMS Spam Collection: only the ordinary ("ham") messages, never the spam."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        name = [n for n in z.namelist() if n.endswith("SMSSpamCollection")][0]
        for line in z.read(name).decode("utf-8", "replace").splitlines():
            label, _, text = line.partition("\t")
            if label == "ham" and len(text.split()) >= 4:
                yield {"type": "sms", "text": text.strip(), "group": "sms"}


def read_sms(fetcher, say=print, **_):
    say("  SMS Spam Collection: downloading the official file from the UCI repository.")
    yield from sms_records(fetcher.get(SMS_URL))


# ----------------------------------------------------------------- task conversations (Taskmaster, SGD, MultiWOZ)

def read_taskmaster(fetcher, say=print, **_):
    """Chat records from Taskmaster-1 (two people talking, one playing an assistant)."""
    say("  Taskmaster-1: downloading the official file from GitHub (37 MB).")
    for d in json.loads(fetcher.get(TASKMASTER_URL)):
        turns = [("Customer" if u["speaker"] == "USER" else "Assistant", u["text"]) for u in d.get("utterances", [])]
        yield {"type": "chat", "turns": turns, "setting": "a phone call where a customer asks an assistant to book "
               "or order something", "group": d.get("instruction_id", "taskmaster").split("-")[0]}


def read_sgd(fetcher, say=print, **_):
    """Chat records from the Schema-Guided Dialogue dataset (first training file)."""
    say("  Schema-Guided Dialogue: downloading one official file from GitHub.")
    for d in json.loads(fetcher.get(SGD_URL)):
        turns = [("Customer" if t["speaker"] == "USER" else "Assistant", t["utterance"]) for t in d["turns"]]
        yield {"type": "chat", "turns": turns, "setting": "a chat between a customer and a virtual assistant about "
               + ", ".join(s.split("_")[0].lower() for s in d.get("services", [])), "group": "sgd"}


def read_multiwoz(fetcher, say=print, **_):
    """Chat records from MultiWOZ 2.2 (first training file)."""
    say("  MultiWOZ 2.2: downloading one official file from GitHub.")
    for d in json.loads(fetcher.get(MULTIWOZ_URL)):
        turns = [("Customer" if t["speaker"] == "USER" else "Clerk", t["utterance"]) for t in d["turns"]]
        yield {"type": "chat", "turns": turns, "setting": "a chat between a visitor and a tourist information clerk",
               "group": "multiwoz"}


def read_topical(fetcher, say=print, **_):
    """Chat records from Topical-Chat (two people chatting about a topic)."""
    say("  Topical-Chat: downloading one official file from GitHub.")
    for key, conv in json.loads(fetcher.get(TOPICAL_URL)).items():
        turns = [("Person A" if t["agent"] == "agent_1" else "Person B", t["message"]) for t in conv["content"]]
        yield {"type": "chat", "turns": turns, "setting": "a friendly online chat between two strangers",
               "group": "topical"}


# ----------------------------------------------------------------- Wikipedia talk pages (Simple English Wikipedia dump)

def wiki_plain(text):
    """Wiki markup made plain: links to their words, templates and tables removed, bold and italics marks removed."""
    text = re.sub(r"\{\{w\|(?:[^{}|]*\|)?([^{}|]*)\}\}", r"\1", text)     # Wikinews' {{w|link|words}}
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", text)
    text = re.sub(r"'{2,}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)


def talk_comments(wikitext):
    """[(user, comment)] from a talk page: each comment ends with a signature "(UTC)"; the user is the last
    [[User:...]] link in it."""
    out = []
    for chunk in re.split(r"(?<=\(UTC\))\s*\n", wikitext):
        if "(UTC)" not in chunk:
            continue
        users = re.findall(r"\[\[User(?: talk)?:([^|\]/]+)", chunk)
        text = re.sub(r"\[\[User(?: talk)?:[^\]]*\]\].*$", "", chunk.strip(), flags=re.S)
        text = wiki_plain(re.sub(r"^[:*#]+\s*", "", text.split("\n==")[-1].strip(), flags=re.M)).strip(" -—")
        text = re.sub(r"^=+[^=\n]+=+\s*", "", text).strip()
        if users and len(text.split()) >= 3:
            out.append((users[-1].strip(), text))
    return out


def read_wikitalk(fetcher, say=print, **_):
    """Chat records from the talk pages (namespace 1) of the Simple English Wikipedia dump, read as it arrives."""
    say("  Wikipedia talk pages: reading the Simple English Wikipedia dump as it arrives (stops early).")
    try:
        resp = fetcher.open_stream(WIKITALK_URL)
    except Exception as err:
        if "404" in str(err):
            say("  Wikipedia talk pages: Wikimedia offers this dump file only from the 1st to the 14th of each "
                "month while it moves to new dumps; try again then.")
            return
        raise
    try:
        page, buf, inside = {}, [], False
        for raw in bz2.BZ2File(resp):
            line = raw.decode("utf-8", "replace")
            if "<title>" in line:
                page = {"title": html.unescape(re.sub(r"\s*</?title>\s*", "", line))}
            elif "<ns>" in line:
                page["ns"] = re.sub(r"\D", "", line)
            elif "<text" in line and page.get("ns") == "1":
                inside, buf = True, [re.sub(r"^\s*<text[^>]*>", "", line)]
                if "</text>" in line:
                    inside = False
            elif inside:
                buf.append(line)
                if "</text>" in line:
                    inside = False
            if not inside and buf and page.get("ns") == "1":
                text = html.unescape("".join(buf).replace("</text>", ""))
                buf = []
                comments = talk_comments(text)
                if len(comments) >= 2:
                    yield {"type": "chat", "turns": comments, "setting": "a Wikipedia talk page discussion about the "
                           "article " + page["title"].replace("Talk:", ""), "group": "wikitalk", "style": "talk"}
    finally:
        resp.close()


# ----------------------------------------------------------------- letters in the public domain (Project Gutenberg)

SALUTATION = re.compile(r"^\s*((my )?(dear|dearest|beloved|honou?red)\b[^\n]{0,40}[,:.]|sir[,:]|madam[,:]|"
                        r"gentlemen[,:])\s*$", re.I | re.M)


def gutenberg_body(text):
    """The book without Project Gutenberg's header and licence at the start and end (allowed for public-domain
    books)."""
    start = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text)
    end = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", text)
    return text[start.end() if start else 0:end.start() if end else len(text)]


def letters_in(text, max_words=600):
    """The letters in a book of letters: from each salutation ("My dear Lucy,") to the next one."""
    marks = [m.start() for m in SALUTATION.finditer(text)]
    for a, b in zip(marks, marks[1:] + [len(text)]):
        letter = text[a:b].strip()
        letter = re.split(r"\n\s*\n\s*(?:[IVXLC]+\.?|LETTER [IVXLC\d]+\.?|[A-Z][A-Z ,.'-]{8,})\s*\n", letter)[0]
        words = len(letter.split())
        if 30 <= words <= max_words:
            yield re.sub(r"[ \t]*\n[ \t]*(?=\S)", lambda m: "\n" if m.group(0).count("\n") > 1 else "\n",
                         letter).strip()


def read_gutenberg(fetcher, say=print, books=None, **_):
    """Text records: letters from public-domain books of letters, from Project Gutenberg's mirror. The books are
    found in Gutenberg's own catalogue (English books whose subject or title says letters/correspondence)."""
    say("  Project Gutenberg: reading the catalogue from the official mirror.")
    if not books:
        catalogue = fetcher.get(GUTENBERG_MIRROR + "cache/epub/feeds/pg_catalog.csv").decode("utf-8", "replace")
        books = []
        for row in csv.DictReader(io.StringIO(catalogue)):
            subj = (row.get("Subjects") or "").lower()
            if row.get("Language") == "en" and row.get("Type") == "Text" and \
                    ("correspondence" in subj or re.match(r"(the )?letters\b", (row.get("Title") or "").lower())) \
                    and "fiction" not in subj:
                books.append((row["Text#"], row.get("Title", "").replace("\n", " ")))
            if len(books) >= 12:
                break
    for number, title in books:
        try:
            text = fetcher.get(f"{GUTENBERG_MIRROR}cache/epub/{number}/pg{number}.txt").decode("utf-8", "replace")
        except Exception as err:
            if "robots" in str(err):
                raise
            continue
        for letter in letters_in(gutenberg_body(text)):
            yield {"type": "letter", "text": letter, "title": title, "group": f"gutenberg-{number}"}


# ----------------------------------------------------------------- Santa Barbara Corpus (whole and unchanged)

def read_sbcsae(fetcher, say=print, numbers=range(1, 61), **_):
    """Text records: each transcript of the Santa Barbara Corpus of Spoken American English, whole and unchanged
    (its licence, CC BY-ND, allows no changes)."""
    say("  Santa Barbara Corpus: reading the transcripts from UC Santa Barbara.")
    for n in numbers:
        url = f"{SBC_BASE}SBC{n:03d}.trn"
        try:
            text = fetcher.get(url).decode("latin-1")
        except Exception as err:
            if "robots" in str(err):
                raise
            continue
        yield {"type": "text", "group": "sbcsae", "kind": "transcript", "form": "transcript", "tone": "casual",
               "audience": "", "unchanged": True,
               "instruction": "Here is a transcript of a real, everyday spoken conversation in American English "
                              f"(Santa Barbara Corpus of Spoken American English, SBC{n:03d}), whole and unchanged. "
                              "Learn how people really talk.",
               "response": text}


# ----------------------------------------------------------------- public comments to US agencies (regulations.gov)

def read_regulations(fetcher, say=print, api_key=None, pages=2, **_):
    """Text records: public comments people sent to US federal agencies, from the regulations.gov API. The API
    needs a free key from api.data.gov, given in the environment variable REGULATIONS_GOV_API_KEY."""
    key = api_key or os.environ.get("REGULATIONS_GOV_API_KEY", "")
    if not key:
        say("  regulations.gov: no API key (set REGULATIONS_GOV_API_KEY, free from api.data.gov); skipped.")
        return
    for page in range(1, pages + 1):
        listing = json.loads(fetcher.get(f"{REGULATIONS_API}comments?sort=-postedDate&page%5Bsize%5D=25&"
                                         f"page%5Bnumber%5D={page}&api_key={key}"))
        for item in listing.get("data", []):
            detail = json.loads(fetcher.get(f"{REGULATIONS_API}comments/{item['id']}?api_key={key}"))
            attrs = detail.get("data", {}).get("attributes", {})
            text = html.unescape(re.sub(r"<[^>]+>", " ", attrs.get("comment") or "")).strip()
            if len(text.split()) < 15 or re.fullmatch(r"(?i)see attached.*", text):
                continue
            yield {"type": "comment", "text": text, "agency": attrs.get("agencyId", ""),
                   "title": item.get("attributes", {}).get("title", ""), "group": attrs.get("agencyId", "regs")}
