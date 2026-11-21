"""Readers: one function per source in writing_sources.py. Each reads only the source's official address (through
fetch.Fetcher, which obeys robots.txt and waits between requests) and yields raw records for build_dataset.py.

Two kinds of record:
  email records    {"subject", "body", "known_names", "writer_names", "audience", "is_reply", "group"}: a real
                   message, which build_dataset.py scrubs and turns into an instruction (instructions.py);
  writing records  {"instruction", "response", "group"}: a request someone wrote and the human answer to it
                   (OASST2, Dolly), which is scrubbed the same way and keeps its own instruction.
"group" lets the builder spread examples over many mailboxes or lists instead of taking them all from one.

Attachments are kept (the owner's rule): the W3C pages' attachment links are downloaded (robots.txt allows them),
and any attachment inside a message is kept. The CMU copy of the Enron emails has no attachments: they were taken
out before it was published.
"""

import email
import email.policy
import gzip
import html
import io
import json
import re
import tarfile

ENRON_URL = "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz"
ENRON_SENT_FOLDERS = {"sent", "sent_items", "_sent_mail"}
W3C_BASE = "https://lists.w3.org/Archives/Public/"
W3C_LISTS = ["w3c-wai-ig", "w3c-wai-gl", "public-aria"]
OASST2_URL = ("https://huggingface.co/datasets/OpenAssistant/oasst2/resolve/main/"
              "2023-11-05_oasst2_ready.trees.jsonl.gz")
DOLLY_URL = "https://huggingface.co/datasets/databricks/databricks-dolly-15k/resolve/main/databricks-dolly-15k.jsonl"

# A request to write a short message: "write an email ...", "draft a text to my landlord ...".
WRITING_REQUEST = re.compile(
    r"\b(write|draft|compose|create|help me (write|with)|can you write|could you write|generate|formulate)\b"
    r"[^.?!\n]{0,80}?\b(e-?mails?|letters?|(a|short|quick|brief|thank[- ]you|kind) notes?|text messages?|"
    r"(a|short|quick) text\b(?! adventure| game| based)|messages? (to|for)|memos?|replies|reply|announcements?|"
    r"invitations?|thank[- ]you|slack message|follow[- ]up)\b"
    r"|\b(improve|rewrite|re-write|reword|proofread|polish|edit|fix)\b[^.?!\n]{0,40}\b(e-?mails?|letters?|"
    r"messages?|memos?)\b", re.I)
# Answers that ask for more details instead of writing the message.
NOT_AN_ANSWER = re.compile(r"\b(please provide|i need more information|i'll need (a bit )?more|can you (tell|give) "
                           r"me more|could you (please )?provide|i must know more|in order to (craft|write|draft))\b",
                           re.I)
NOT_SHORT_FORM = re.compile(r"\b(poems?|story|stories|essays?|blog|article|song|lyrics|script|code|program|"
                            r"function|novel|haiku|limerick|speech|cover letter|motivation letter|recommendation letter|"
                            r"resume|marketing|sales|newsletter|spam|phishing|prank|fake|cease|html|css|javascript|"
                            r"python|sql|letters? of)\b", re.I)
PREAMBLE = re.compile(r"^\s*(sure|certainly|of course|absolutely|here('s| is)|okay|ok|great)\b[^\n]{0,120}:\s*\n+",
                      re.I)


# ----------------------------------------------------------------- Enron (CMU)

def enron_records(fileobj, say=print):
    """Email records from the sent-mail folders of the Enron tar.gz read from fileobj as it arrives."""
    with tarfile.open(fileobj=fileobj, mode="r|gz") as tar:
        last_user, boxes = None, 0
        for member in tar:
            if not member.isfile():
                continue
            parts = member.name.split("/")
            if len(parts) < 4 or parts[0] != "maildir" or parts[2] not in ENRON_SENT_FOLDERS:
                continue
            user = parts[1]
            if user != last_user:
                boxes += 1
                say(f"  Enron: reading mailbox {boxes}")
                last_user = user
            data = tar.extractfile(member).read()
            record = enron_record(data, user)
            if record:
                yield record


def enron_record(data, user):
    """One email record from the bytes of one Enron message file (with any attachments it carries), or None."""
    import readers_more
    try:
        msg, body, files = readers_more.parse_mail(data)
    except Exception:
        return None
    if not body.strip():
        return None
    header = lambda k: str(msg.get(k, "") or "")
    recipients = ",".join([header("To"), header("Cc"), header("Bcc")])
    addresses = re.findall(r"[\w.\-]+@[\w.\-]+", recipients)
    inside = all(a.lower().endswith("enron.com") for a in addresses) if addresses else True
    if len(addresses) > 3:
        audience = "the team" if inside else "a group of contacts"
    elif inside:
        audience = "a colleague"
    else:
        audience = "an outside contact"
    surname = user.split("-")[0]
    return {
        "type": "email",
        "subject": header("Subject"),
        "body": body,
        "known_names": [header("X-To"), header("X-cc"), header("X-bcc"), header("To"), header("Cc")],
        "writer_names": [header("X-From"), header("From"), surname],
        "audience": audience,
        "is_reply": bool(re.match(r"\s*re\s*:", header("Subject"), re.I)),
        "group": user,
        "attachments": files,
        "msg_id": header("Message-ID"),
    }


def read_enron(fetcher, say=print, local_file=None, **_):
    """Email records from the official Enron file (or a copy of it already on this computer, local_file)."""
    if local_file:
        with open(local_file, "rb") as f:
            yield from enron_records(f, say)
        return
    say("Enron: reading the official file from Carnegie Mellon University as it arrives (it stops early once it "
        "has enough).")
    resp = fetcher.open_stream(ENRON_URL)
    try:
        yield from enron_records(resp, say)
    finally:
        resp.close()


# ----------------------------------------------------------------- W3C public lists

def _strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text))


def w3c_message(page):
    """An email record from one hypermail page of lists.w3.org, or None."""
    m = re.search(r'<pre[^>]*class="body"[^>]*>(.*?)</pre>', page, re.S) or \
        re.search(r'<div[^>]*class="body"[^>]*>(.*?)</div>\s*(?:<!-- body="end" -->|<h2|<ul class="links)', page, re.S)
    if not m:
        return None
    if re.search(r'class="attachment"|<span class="heading">attachment', page, re.I):
        pass                                          # attachments are only links on the page; never followed
    body = _strip_tags(m.group(1))
    subject = html.unescape((re.search(r'<meta name="Subject" content="([^"]*)"', page) or [None, ""])[1])
    author = html.unescape((re.search(r'<meta name="Author" content="([^"]*)"', page) or [None, ""])[1])
    to = _strip_tags((re.search(r'<span class="to">(.*?)</span></li>', page, re.S) or [None, ""])[1])
    cc = _strip_tags((re.search(r'<span class="cc">(.*?)</span></li>', page, re.S) or [None, ""])[1])
    to_list = "w3.org" in to.split(":", 1)[-1] and "@" in to
    links = re.findall(r'<a href="(att-\d+/[^"]+)"', page)
    return {
        "type": "email",
        "attachment_links": links,
        "subject": subject,
        "body": body,
        "known_names": [to, cc],
        "writer_names": [author],
        "audience": "the members of a mailing list" if to_list else "a colleague",
        "is_reply": bool(re.search(r"<!-- inreplyto=\"[^\"]+\" -->", page)),
    }


def read_w3c(fetcher, say=print, lists=None, periods_per_list=3, pages_per_period=30, **_):
    """Email records from the public HTML archives of a few W3C lists (newest periods first, skipping the current
    one), one page at a time with the wait fetch.py keeps."""
    for name in lists or W3C_LISTS:
        top = fetcher.get(W3C_BASE + name + "/").decode("utf-8", "replace")
        periods = []
        for p in re.findall(r'href="(\d{4}[A-Za-z]{3,9}/)"', top):
            if p not in periods:
                periods.append(p)
        for period in periods[1:1 + periods_per_list]:
            index = fetcher.get(W3C_BASE + name + "/" + period).decode("utf-8", "replace")
            pages = sorted(set(re.findall(r'href="(\d{4}\.html)"', index)))
            say(f"  W3C {name} {period.strip('/')}: {len(pages)} messages listed")
            for page_name in pages[:pages_per_period]:
                raw = fetcher.get(W3C_BASE + name + "/" + period + page_name)
                record = w3c_message(raw.decode("iso-8859-1", "replace"))
                if record:
                    files = []
                    for link in record.pop("attachment_links"):
                        try:
                            files.append((link.split("/")[-1], fetcher.get(W3C_BASE + name + "/" + period + link),
                                          ""))
                        except Exception as err:
                            if "robots" in str(err):
                                raise
                    record.update(group=name, attachments=files, msg_id=W3C_BASE + name + "/" + period + page_name)
                    yield record


# ----------------------------------------------------------------- OpenAssistant OASST2 and Dolly

def clean_answer(text):
    """An answer without a chatty first line ("Sure! Here's an email:") and with "[Your Name]" style placeholders
    written the kit's way."""
    text = PREAMBLE.sub("", text.strip())
    text = re.sub(r"\[(your|my) (full )?name\]", "[Your name]", text, flags=re.I)
    text = re.sub(r"\n+\s*(I hope this helps|Let me know if|Feel free to)[^\n]*$", "", text, flags=re.I)
    return text.strip()


def is_writing_request(prompt):
    """True when prompt asks for a short email, note, message, memo or the like (not a poem, essay or code)."""
    return bool(WRITING_REQUEST.search(prompt)) and not NOT_SHORT_FORM.search(prompt) and len(prompt) < 900


def oasst_records(lines):
    """Writing records from OASST message trees (one JSON tree per line)."""
    for line in lines:
        tree = json.loads(line)
        root = tree.get("prompt") or {}
        if root.get("lang") != "en" or root.get("synthetic") or not is_writing_request(root.get("text", "")):
            continue
        answers = [r for r in root.get("replies", []) if r.get("role") == "assistant" and not r.get("synthetic")
                   and not r.get("deleted") and r.get("review_result", True) is not False]
        answers.sort(key=lambda r: (r.get("rank") is None, r.get("rank") if r.get("rank") is not None else 0))
        if answers and not NOT_AN_ANSWER.search(answers[0]["text"]):
            yield {"type": "writing", "instruction": root["text"].strip(), "response": clean_answer(answers[0]["text"]),
                   "group": "oasst2"}


def read_oasst2(fetcher, say=print, **_):
    """Writing records from the official OASST2 file (it includes all of OASST1)."""
    say("OASST2: downloading the official file from Hugging Face (54 MB).")
    data = gzip.decompress(fetcher.get(OASST2_URL))
    yield from oasst_records(io.StringIO(data.decode("utf-8")))


def dolly_records(lines):
    """Writing records from Dolly (one JSON record per line)."""
    for line in lines:
        rec = json.loads(line)
        if rec.get("category") not in ("creative_writing", "generation", "brainstorming", "open_qa", "general_qa"):
            continue
        prompt = (rec.get("instruction", "") + ("\n\n" + rec["context"] if rec.get("context") else "")).strip()
        if is_writing_request(rec.get("instruction", "")) and not NOT_AN_ANSWER.search(rec.get("response", "")):
            yield {"type": "writing", "instruction": prompt, "response": clean_answer(rec.get("response", "")),
                   "group": "dolly"}


def read_dolly(fetcher, say=print, **_):
    say("Dolly: downloading the official file from Hugging Face (13 MB).")
    data = fetcher.get(DOLLY_URL).decode("utf-8")
    yield from dolly_records(io.StringIO(data))
