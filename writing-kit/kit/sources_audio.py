"""Audio-and-text sources and government form letters for the Writing Kit (added in November 2026 at the owner's
request), kept in this one file so they are easy to merge with other work on the kit. writing_sources.py adds
SOURCES and NOT_USED from here, build_dataset.py reads with the readers here and saves the audio pairs (save_pair),
and styles.py has the new style labels.

What is here, by key:
  Audio with matching text (for speech and TTS work, such as the owner's NLS-TTS project)
    librispeech    LibriSpeech (CC BY 4.0) and LibriTTS (CC BY 4.0), from openslr.org: short utterances read from
                   LibriVox audiobooks, each with its exact transcript (LibriSpeech's in capitals without
                   punctuation; LibriTTS's with the book's own punctuation and capitals, and 24 kHz audio, made for
                   TTS). The official .tar.gz files are read as they arrive and the kit stops when it has enough,
                   so only the first part is downloaded.
    librivox       public-domain LibriVox audiobooks (the copies on the Internet Archive, collection librivoxaudio)
                   with the matching Project Gutenberg text (found in Gutenberg's own catalogue by title and author),
                   paired chapter by chapter: each chapter's MP3 with that chapter's text. ON by default since the
                   owner decided so (22 November 2026): librivox.org's own robots.txt says "ai-train=no", so the kit
                   never uses LibriVox's site or API, only the public-domain recordings on the Internet Archive,
                   which allows programs; this goes around LibriVox's stated wish, for the owner's personal use. The book texts
                   also become writing examples, labelled fiction_prose or nonfiction_prose.
  Government form letters and notices (public domain)
    gov_letters    the plainlanguage.gov example letters and before-and-after rewrites (the same pages the
                   reference library's "Plain language examples" book reads, textbooks/writing_business.py
                   EXAMPLE_PARTS, from GSA's public repository on GitHub), and the IRS's "Understanding your notice
                   or letter" pages (what each CP and LTR notice means and what to do), found in irs.gov's sitemap.

The audio pairs are NOT training examples: build_dataset.py saves them in their own output folder,
out/audio_text/<source>/: each pair's audio file (FLAC, WAV or MP3) beside a .txt file with its text, and
pairs.jsonl listing every pair (audio, text, alignment, speaker (LibriSpeech, LibriTTS), book, chapter, licence, credit
and the official addresses). "alignment" says how closely they match: "utterance" (LibriSpeech, LibriTTS: the text is
exactly what is said) or "chapter" (LibriVox: the whole chapter's text for the whole recording, which also has
LibriVox's short spoken introduction and ending).

Every request goes through fetch.Fetcher: robots.txt and AI-training refusals obeyed, requests paced.
"""

import csv
import io
import json
import os
import re
import tarfile
import urllib.error
import urllib.parse

import readers_business
import readers_creative
import readers_more
import sources_more

cap_words = readers_business.cap_words

# Sources that are left out of a build unless named in --sources (build_dataset.py).
OPT_IN = set()                 # LibriVox is on by default (the owner's decision of 22 November 2026)

# New style labels (styles.py adds them to its list): name -> what it is.
STYLES = {
    "nonfiction_prose": "nonfiction books: history, essays, biography, travel and science (public domain)",
    "form_letter": "form letters and notices from agencies to the public, in plain language",
}
FORMAL = {"form_letter"}
CASUAL = set()


def words(text):
    """How many words text has."""
    return len((text or "").split())


# ====================================================================== saving the audio and text pairs

_STARTED = set()        # the audio_text/<source> folders started in this run (their pairs.jsonl is begun again)
CC_BY = "https://creativecommons.org/licenses/by/4.0/"
PD_MARK = "https://creativecommons.org/publicdomain/mark/1.0/"
README = """Audio and text pairs (made by the Writing Kit), for speech and text-to-speech work.

Each folder is one source. In it, every pair is an audio file and a .txt file of the same name with its text, and
pairs.jsonl lists every pair with its details: audio (the file, relative to this folder), text, alignment, speaker
(LibriSpeech, LibriTTS), book, chapter, licence, credit and the official addresses.

alignment "utterance": the text is exactly what is said in the audio (LibriSpeech, LibriTTS).
alignment "chapter": the text is the whole chapter of the book and the audio the whole chapter as read
  (LibriVox); the recording also has LibriVox's short spoken introduction and ending, and the reader may have
  used another edition, so small differences are possible.

Licences, by folder:
"""


def safe(name):
    """A file or folder name made of letters, digits, dots, hyphens and underscores only."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("._") or "item"


def save_pair(root, source_key, record):
    """Save one audio and text pair (a record of type "audio_pair") under root/<source_key>/: the audio file and its
    .txt beside it in a folder for its group, and a line in pairs.jsonl. Returns the audio file's path."""
    folder = os.path.join(root, safe(source_key))
    group = os.path.join(folder, safe(record.get("group") or "pairs"))
    os.makedirs(group, exist_ok=True)
    readme = os.path.join(root, "README.txt")
    if root not in _STARTED:                    # the first pair of this run: the README is written again
        _STARTED.add(root)
        with open(readme, "w", encoding="utf-8") as f:
            f.write(README)
    if folder not in _STARTED:                  # the first pair of this source: its licence line, a new pairs.jsonl
        _STARTED.add(folder)
        with open(readme, "a", encoding="utf-8") as f:
            f.write(f"  {safe(source_key)}: {record.get('licence', '')}. Credit: {record.get('credit', '')}.\n")
        open(os.path.join(folder, "pairs.jsonl"), "w", encoding="utf-8").close()
    name = safe(record["audio_name"])
    audio_path = os.path.join(group, name)
    with open(audio_path, "wb") as f:
        f.write(record["audio"])
    with open(os.path.splitext(audio_path)[0] + ".txt", "w", encoding="utf-8") as f:
        f.write(record["text"].strip() + "\n")
    line = {"audio": os.path.relpath(audio_path, folder).replace(os.sep, "/"), "text": record["text"].strip(),
            **{k: v for k, v in record.items() if k not in ("type", "audio", "audio_name", "text", "group")}}
    with open(os.path.join(folder, "pairs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return audio_path


# ====================================================================== LibriSpeech and LibriTTS (CC BY 4.0)

OPENSLR = "https://www.openslr.org/resources/"
# (name, address, layout): only the official openslr.org host (us.openslr.org's robots.txt closes it to programs).
SPEECH_SETS = [
    ("librispeech-dev-clean", OPENSLR + "12/dev-clean.tar.gz", "librispeech"),
    ("libritts-dev-clean", OPENSLR + "60/dev-clean.tar.gz", "libritts"),
]
SPEECH_CREDIT = {
    "librispeech": ("CC BY 4.0", "LibriSpeech ASR corpus (Vassil Panayotov, Guoguo Chen, Daniel Povey and Sanjeev "
                    "Khudanpur), made from LibriVox recordings", "https://www.openslr.org/12/"),
    "libritts": ("CC BY 4.0", "LibriTTS corpus (Heiga Zen, Viet Dang, Rob Clark, Yu Zhang, Ron J. Weiss, Ye Jia, "
                 "Zhifeng Chen and Yonghui Wu), made from LibriSpeech's LibriVox recordings",
                 "https://www.openslr.org/60/"),
}


def speech_pairs(members, layout, limit):
    """[(id, audio name, audio bytes, text, extra)] from the members of a LibriSpeech or LibriTTS archive read in
    order ((name, bytes) pairs; directories have None). An utterance is given as soon as both its audio and its
    text have been seen (the archives do not keep them in one order), up to limit utterances.
      librispeech   <speaker>/<chapter>/<id>.flac, and <speaker>-<chapter>.trans.txt with "<id> TEXT" lines
      libritts      <speaker>/<chapter>/<id>.wav, <id>.original.txt (the book's text) and <id>.normalized.txt"""
    audio, text, normal, out = {}, {}, {}, []
    for name, data in members:
        if data is None:
            continue
        base = name.rsplit("/", 1)[-1]
        ready = []
        if layout == "librispeech":
            if base.endswith(".flac"):
                audio[base[:-5]] = (base, data)
                ready.append(base[:-5])
            elif base.endswith(".trans.txt"):
                for line in data.decode("utf-8", "replace").splitlines():
                    if " " in line:
                        uid, said = line.split(" ", 1)
                        text[uid] = said.strip()
                        ready.append(uid)
        else:
            if base.endswith(".wav"):
                audio[base[:-4]] = (base, data)
                ready.append(base[:-4])
            elif base.endswith(".original.txt"):
                text[base[:-13]] = data.decode("utf-8", "replace").strip()
                ready.append(base[:-13])
            elif base.endswith(".normalized.txt"):
                normal[base[:-15]] = data.decode("utf-8", "replace").strip()
        for uid in ready:
            if uid in audio and uid in text and text[uid]:
                file_name, data_bytes = audio.pop(uid)
                parts = re.split(r"[-_]", uid)
                extra = {"speaker": parts[0], "chapter": parts[1] if len(parts) > 1 else ""}
                if layout == "libritts":
                    extra["normalized_text"] = normal.get(uid, "")
                out.append((uid, file_name, data_bytes, text.pop(uid), extra))
                if len(out) >= limit:
                    return out
    return out


def tar_members(stream):
    """(name, bytes) for each member of a .tar.gz read as it arrives (None for directories and links)."""
    with tarfile.open(fileobj=stream, mode="r|gz") as tar:
        for m in tar:
            yield m.name, (tar.extractfile(m).read() if m.isfile() else None)


def read_librispeech(fetcher, say=print, sets=None, audio_pairs=200, **_):
    """Audio pair records: the first utterances of each set in SPEECH_SETS (half of audio_pairs each), with their
    transcripts. Only the start of each official archive is downloaded."""
    chosen = [s for s in SPEECH_SETS if not sets or s[0] in sets]
    per_set = max(1, int(audio_pairs or 200) // max(1, len(chosen)))
    for set_name, url, layout in chosen:
        licence, credit, home = SPEECH_CREDIT[layout]
        resp = fetcher.open_stream(url)
        try:
            pairs = speech_pairs(tar_members(resp), layout, per_set)
        finally:
            resp.close()
        for uid, file_name, data, said, extra in pairs:
            yield {"type": "audio_pair", "group": f"{set_name}/{extra['speaker']}", "audio_name": file_name,
                   "audio": data, "text": said, "alignment": "utterance", "set": set_name, **extra,
                   "licence": licence, "licence_url": CC_BY, "credit": credit, "home": home, "archive": url}
        say(f"  {set_name}: {len(pairs)} utterances with their text.")


# ====================================================================== LibriVox with Project Gutenberg (public domain)

IA_SEARCH = ("https://archive.org/advancedsearch.php?q={q}&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=creator"
             "&fl%5B%5D=description&sort%5B%5D=downloads+desc&rows={rows}&page={page}&output=json")
IA_QUERY = "collection:librivoxaudio AND mediatype:audio AND language:(eng OR English)"
IA_META = "https://archive.org/metadata/{id}"
IA_FILE = "https://archive.org/download/{id}/{name}"
GUTENBERG_LINK = re.compile(r"gutenberg\.org/(?:etext|ebooks|files)/(\d+)", re.I)
# A chapter heading: a short line of its own ("CHAPTER I.", "Chapter 12. The Storm"), not a sentence that starts so.
CHAPTER_HEAD = re.compile(r"(?m)^[ \t]*(?:CHAPTER|Chapter)[ \t]+(?:[IVXLCDM]+|\d+|[A-Z][A-Za-z-]+)\b[^\n]{0,60}$")
FICTION = re.compile(r"(?i)\bfiction\b|\bnovels?\b|short stories|fairy tales|\bstories\b|\bromance\b|adventure stories")
LIBRIVOX_LICENCE = ("Public domain (LibriVox recordings are dedicated to the public domain; the Project Gutenberg text "
                    "is of a book in the public domain in the United States)")
LIBRIVOX_CREDIT = "LibriVox volunteers (recording, via the Internet Archive) and Project Gutenberg volunteers (text)"


def plain_title(text):
    """A title in a form for matching: small letters and digits only, without ", by ..." and a leading article."""
    text = re.split(r"(?i),?\s+by\s+", str(text or ""))[0]
    text = re.sub(r"(?i)\s*\(.*?(version|librivox|dramatic reading|abridged).*?\)", "", text)
    return re.sub(r"^(the|a|an)", "", re.sub(r"[^a-z0-9]+", "", text.lower()))


def surname(creator):
    """The last word of an author's name ("Lewis Carroll" -> "carroll")."""
    names = re.findall(r"[A-Za-z]+", str(creator or "").split(";")[0])
    return names[-1].lower() if names else ""


def gutenberg_match(rows, title, creator, description=""):
    """The Gutenberg catalogue row of a LibriVox book: the etext its description links to, else the English text
    whose title matches and whose author list has the reader's author's surname (the lowest number when several:
    usually the first edition Gutenberg made). None when there is no match."""
    link = GUTENBERG_LINK.search(str(description or ""))
    by_number = {r.get("Text#"): r for r in rows}
    if link and link.group(1) in by_number:
        return by_number[link.group(1)]
    want, last = plain_title(title), surname(creator)
    if not want or not last:
        return None
    hits = [r for r in rows if plain_title(r.get("Title", "").split("\n")[0]) == want
            and last in (r.get("Authors") or "").lower()]
    return min(hits, key=lambda r: int(r["Text#"]) if str(r.get("Text#", "")).isdigit() else 10 ** 9) if hits else None


def chapters_of(body, min_words=150):
    """[(heading, text)] of a Gutenberg book's chapters ("CHAPTER I.", "Chapter 12"), leaving out the headings of
    the table of contents (a heading followed by fewer than min_words words before the next one)."""
    heads = list(CHAPTER_HEAD.finditer(body))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        text = body[h.end():end].strip()
        if words(text) >= min_words:
            out.append((" ".join(h.group(0).split()), text))
    return out


def chapter_files(meta):
    """The chapter recordings of a LibriVox item: its 64 kbit/s MP3 files in name order (one per section)."""
    files = [f for f in meta.get("files") or [] if str(f.get("name", "")).endswith("_64kb.mp3")]
    return sorted(files, key=lambda f: f["name"])


def book_style(row):
    """fiction_prose or nonfiction_prose, from the book's Gutenberg subjects and bookshelves."""
    words_ = f"{row.get('Subjects', '')} {row.get('Bookshelves', '')}"
    return "fiction_prose" if FICTION.search(words_) else "nonfiction_prose"


def gutenberg_author(row):
    """The first author of a catalogue row, first name first ("Carroll, Lewis, 1832-1898" -> "Lewis Carroll")."""
    author = re.sub(r",\s*\d.*$", "", (row.get("Authors") or "").split(";")[0]).strip()
    if "," in author:
        last, first = author.split(",", 1)
        author = f"{first.strip()} {last.strip()}"
    return author


def book_records(body, title, author, style, number, max_pairs=8):
    """Writing examples from a LibriVox book's text: "continue this book" passages (readers_creative's rule)."""
    pairs = readers_creative.continuation_pairs(body, title, author, "fiction_prose", max_pairs=max_pairs)
    for instruction, answer in pairs:
        if style == "nonfiction_prose":
            instruction = instruction.replace("Continue this story in the same style",
                                              "Continue this nonfiction book in the same style", 1)
        yield {"type": "text", "group": f"gutenberg-{number}", "kind": "book", "form": "book",
               "tone": "literary", "audience": "readers", "style_label": style, "instruction": instruction,
               "response": answer}


def read_librivox(fetcher, say=print, books=3, chapters=3, max_mb=40, audio_pairs=200, search_rows=50, **_):
    """Audio pair records (each chapter's MP3 with that chapter's Gutenberg text) and text records (the book's text
    as writing examples) for up to books LibriVox books whose chapters match the Gutenberg text's chapters one for
    one; at most chapters chapters of each book and audio_pairs in all; MP3 files over max_mb megabytes skipped."""
    catalogue = fetcher.get(readers_more.GUTENBERG_MIRROR + "cache/epub/feeds/pg_catalog.csv").decode("utf-8",
                                                                                                    "replace")
    rows = [r for r in csv.DictReader(io.StringIO(catalogue)) if r.get("Language") == "en" and r.get("Type") == "Text"]
    done, pairs = 0, 0
    data = json.loads(fetcher.get(IA_SEARCH.format(q=urllib.parse.quote(IA_QUERY), rows=search_rows, page=1)))
    for doc in (data.get("response") or {}).get("docs") or []:
        if done >= books or pairs >= audio_pairs:
            break
        row = gutenberg_match(rows, doc.get("title"), doc.get("creator"), doc.get("description"))
        if not row:
            continue
        number = row["Text#"]
        text_url = f"{readers_more.GUTENBERG_MIRROR}cache/epub/{number}/pg{number}.txt"
        try:
            text = fetcher.get(text_url).decode("utf-8", "replace").replace("\r\n", "\n")
            meta = json.loads(fetcher.get(IA_META.format(id=urllib.parse.quote(doc["identifier"]))))
        except urllib.error.HTTPError:
            continue
        if re.search(r"(?i)copyrighted project gutenberg|copyright \(c\)|©", text[:6000]):
            continue
        body = readers_more.gutenberg_body(text)
        chaps, files = chapters_of(body), chapter_files(meta)
        if not chaps or len(chaps) != len(files):
            say(f"  LibriVox: {doc.get('title')}: {len(files)} recordings and {len(chaps)} chapters in the text "
                "do not match one for one; skipped.")
            continue
        title = re.sub(r"\s+", " ", row.get("Title", "")).strip()
        author, style = gutenberg_author(row), book_style(row)
        done += 1
        for n, ((heading, chapter_text), f) in enumerate(zip(chaps, files), 1):
            if n > chapters or pairs >= audio_pairs:
                break
            if int(f.get("size") or 0) > max_mb * 1_000_000:
                continue
            url = IA_FILE.format(id=urllib.parse.quote(doc["identifier"]), name=urllib.parse.quote(f["name"]))
            try:
                audio = fetcher.get(url)
            except urllib.error.HTTPError:
                continue
            pairs += 1
            yield {"type": "audio_pair", "group": safe(doc["identifier"]), "audio_name": f["name"], "audio": audio,
                   "text": f"{heading}\n\n{chapter_text}", "alignment": "chapter", "book": title, "author": author,
                   "chapter": n, "chapter_title": heading, "length": f.get("length", ""), "licence": LIBRIVOX_LICENCE, "licence_url": PD_MARK,
                   "credit": LIBRIVOX_CREDIT, "audio_url": url, "text_url": text_url,
                   "home": f"https://archive.org/details/{doc['identifier']}"}
        yield from book_records(body, title, author, style, number)
        say(f"  LibriVox: {title} ({style}): chapters paired.")


# ====================================================================== government form letters (public domain)

PLG_RAW = "https://raw.githubusercontent.com/GSA/plainlanguage.gov/main/_pages/examples/"
# The reference library's page list (textbooks/writing_business.py EXAMPLE_PARTS): the letters and notices, and the
# before-and-after rewrites.
PLG_LETTERS = ["change-in-enrollment-status", "failure-to-provide-claim-information", "medicare-fraud-letter",
               "pension-medical-evidence"]
PLG_BEFORE_AFTER = ["ambiguity", "application-due-date", "application-federal-assistance", "car-safety",
                    "employment-assistance", "fungi-hazards", "lead-warning", "medicaid-eligibility",
                    "medicaid-initiative", "monthly-due-date", "natural-disasters", "printer-recommendations",
                    "register-pesticide", "use-less-water", "water-resources", "wordiness"]
IRS_SITEMAP = "https://www.irs.gov/sitemap.xml"
IRS_NOTICE = re.compile(r"^https://www\.irs\.gov/individuals/understanding-your-(?!irs-notice-or-letter$)[a-z0-9-]+$")
IRS_END = re.compile(r"\n\n(?:Page Last Reviewed or Updated|Related|Resources|Notice resources|Tax forms|Return to "
                     r"top|Was this page helpful)\b.*", re.S)


def front_matter(text):
    """({field: value}, the rest) of a Jekyll page (its "name: value" lines between the two "---" lines)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fields = {}
    for line in m.group(1).splitlines():
        f = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if f and f.group(2).strip():
            fields[f.group(1)] = f.group(2).strip().strip("'\"")
    return fields, text[m.end():]


def md_plain(text):
    """Markdown and HTML of a plainlanguage.gov page as plain text: headings as their words, <br> as line breaks,
    tags, emphasis, attribute lists ({: .class}) and list marks taken out."""
    text = re.sub(r"(?i)<br\s*/?>\s*", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{:[^}]*\}|\{%[^%]*%\}|\{\{[^}]*\}\}", "", text)
    text = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]*", "", text)
    text = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: m.group(1) or m.group(2), text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)|(?<![\w_])_(?![\s_])(.+?)(?<![\s_])_(?!\w)",
                  lambda m: m.group(1) or m.group(2), text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text).replace("\\.", ".")
    lines = [ln.rstrip() for ln in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def plain_letter(md):
    """(title, author, letter, headings) of a plainlanguage.gov letter page."""
    fields, body = front_matter(md)
    letter = md_plain(body)
    headings = [h.strip() for h in re.findall(r"(?m)^\s*#{2,6}\s*(.+)$", body)]
    return fields.get("title", ""), fields.get("author", ""), letter, headings


def before_after(md):
    """(title, author, [(before, after)]) of a plainlanguage.gov before-and-after page: each "#### Before" block
    with the "#### After" block that follows it."""
    fields, body = front_matter(md)
    parts = re.split(r"(?m)^\s*(?:[*-]\s*)?#{2,6}\s*(Before|After)\b[^\n]*\n", body)
    pairs, before = [], None
    for label, block in zip(parts[1::2], parts[2::2]):
        text = md_plain(re.sub(r"(?m)^  ", "", block))
        if label == "Before":
            before = text
        elif before:
            pairs.append((before, text))
            before = None
    return fields.get("title", ""), fields.get("author", ""), pairs


def irs_notice_name(url):
    """The notice's name from its page address ("understanding-your-cp2000-notice" -> "CP2000 notice")."""
    slug = url.rsplit("understanding-your-", 1)[-1]
    parts = slug.split("-")
    return " ".join(p.upper() if re.fullmatch(r"(cp|ltr|letter)?\d+[a-z]*|cp\w*|ltr\w*", p) else p for p in parts)


def irs_page_text(page):
    """(title, text) of an IRS notice page: the paragraphs, headings and list items (as "- " lines) of its <main>
    part, without menus and the page's closing parts."""
    title = sources_more.page_title(page)
    page = re.sub(r"(?is)<(script|style|nav|header|footer|aside|form)\b.*?</\1>", " ", page)
    page = re.sub(r"(?i)<li\b[^>]*>", "<li>- ", page)
    main = re.search(r"(?is)<main\b.*?</main>", page)
    text = sources_more.paragraphs_of(main.group(0) if main else page, tags="p|h2|h3|li")
    return title, IRS_END.sub("", "\n\n" + sources_more.trim_menu(text)).strip()


def read_gov_letters(fetcher, say=print, irs_pages=60, **_):
    """Text records: plainlanguage.gov's example letters (form letters) and before-and-after rewrites (GSA's
    repository), and IRS notice explanations (pages found in irs.gov's sitemap, spread over the whole list)."""
    got = 0
    for name in PLG_LETTERS:
        try:
            md = fetcher.get(f"{PLG_RAW}notices/{name}.md").decode("utf-8", "replace")
        except urllib.error.HTTPError:
            continue
        title, author, letter, headings = plain_letter(md)
        if words(letter) < 60:
            continue
        got += 1
        shape = f' Use these headings: {"; ".join(headings)}.' if headings else ""
        yield sources_more.text_record(
            author or "plainlanguage.gov", "form_letter", "form letter", "letter", "plain and direct",
            "a member of the public", f"Write a plain-language form letter from {author or 'a federal agency'} to a "
            f'person about "{title}": what our records show, what we did, what we need from you and by when, and '
            f"what happens next.{shape}", letter)
    for name in PLG_BEFORE_AFTER:
        try:
            md = fetcher.get(f"{PLG_RAW}before-and-after/{name}.md").decode("utf-8", "replace")
        except urllib.error.HTTPError:
            continue
        title, author, pairs = before_after(md)
        for before, after in pairs:
            if words(before) < 8 or words(after) < 5:
                continue
            got += 1
            yield sources_more.text_record(
                author or "plainlanguage.gov", "plain_language_gov", "plain-language rewrite", "notice",
                "plain and direct", "the public", "Rewrite this government text in plain language, so that anyone "
                f'can understand it on first reading ("{title}"):\n\n{before}', after)
    say(f"  plainlanguage.gov: {got} letters and rewrites.")
    index = fetcher.get(IRS_SITEMAP).decode("utf-8", "replace")
    links = []
    for sitemap in sources_more.sitemap_locs(index, r"sitemap\.xml\?page=\d+"):
        links += sources_more.sitemap_locs(fetcher.get(sitemap).decode("utf-8", "replace"), "")
    notices = [u for u in links if IRS_NOTICE.match(u)]
    got = 0
    for url in sources_more.spread(sorted(set(notices)), irs_pages):
        try:
            title, text = irs_page_text(fetcher.get(url).decode("utf-8", "replace"))
        except urllib.error.HTTPError:
            continue
        if words(text) < 80:
            continue
        got += 1
        notice = irs_notice_name(url)
        yield sources_more.text_record(
            "IRS", "plain_language_gov", "notice explanation", "web page", "plain and helpful", "a taxpayer",
            f'Write the IRS web page "{title or "Understanding your " + notice}" for a taxpayer who received the '
            f"{notice}: why they received it, what they need to do, and how to reply or get help.", cap_words(text))
    say(f"  IRS: {got} notice explanations (of {len(notices)} listed in its sitemap).")


# ====================================================================== the Source entries and the sources not used

def sources(Source, OPEN, SHARE_ALIKE, PERSONAL):
    """The Source entries for writing_sources.SOURCES (it passes its own Source class and licence classes in)."""
    PD_URL = "https://www.usa.gov/government-copyright"
    return [
        Source(key="librispeech", name="LibriSpeech and LibriTTS (audio with exact transcripts, from openslr.org)",
               licence="CC BY 4.0", licence_class=OPEN, licence_url=CC_BY,
               credit="LibriSpeech (Vassil Panayotov, Guoguo Chen, Daniel Povey, Sanjeev Khudanpur) and LibriTTS "
                      "(Heiga Zen and others, Google), both made from LibriVox's public-domain recordings",
               home="https://www.openslr.org/12/, https://www.openslr.org/60/", reader="read_librispeech",
               notes="The dev-clean archives, read as they arrive (the kit stops when it has enough). Audio pairs "
                     "only, saved in out/audio_text/librispeech/ (no training examples). LibriTTS keeps the book's "
                     "punctuation and capitals and has 24 kHz audio, made for text-to-speech."),
        Source(key="librivox", name="LibriVox audiobooks (Internet Archive copies) with Project Gutenberg texts",
               licence=LIBRIVOX_LICENCE, licence_class=OPEN, licence_url=PD_MARK, credit=LIBRIVOX_CREDIT,
               home="https://archive.org/details/librivoxaudio, https://www.gutenberg.org/",
               reader="read_librivox",
               notes="Chapter MP3s from the Internet Archive's LibriVox collection, each paired with that chapter of "
                     "the Gutenberg text (from Gutenberg's official mirror) when the chapters match one for one; "
                     "saved in out/audio_text/librivox/. The book texts also become writing examples labelled "
                     "fiction_prose or nonfiction_prose. Used only when named in --sources.",
               warnings=["librivox.org's robots.txt says 'Content-Signal: ai-train=no', so the kit never reads "
                         "LibriVox's own site or API. The recordings are public domain and the Internet Archive's "
                         "robots.txt allows programs, but using its copies goes around LibriVox's stated wish: the "
                         "owner decides (the source is off unless named in --sources)."]),
        Source(key="gov_letters", name="Government form letters and notice explanations (plainlanguage.gov examples, "
               "IRS notices)", licence="Public domain (US government work; GSA's repository also adds the CC0 1.0 "
               "dedication)", licence_class=OPEN, licence_url=PD_URL,
               credit="The General Services Administration and the Plain Language Action and Information Network "
                      "(plainlanguage.gov examples, with the agencies that wrote them), and the Internal Revenue "
                      "Service", home="https://github.com/GSA/plainlanguage.gov, https://www.irs.gov/individuals/"
                      "understanding-your-irs-notice-or-letter", reader="read_gov_letters",
               notes="The same plainlanguage.gov pages as the reference library's 'Plain language examples' book "
                     "(letters and before-and-after rewrites), and IRS notice explanation pages found in irs.gov's "
                     "sitemap.",
               warnings=["Some plainlanguage.gov examples are decades old or were written for training (they say "
                         "so); the agencies' current letters may differ."]),
    ]


NOT_USED = [
    ("LibriVox's own website and API (librivox.org)",
     "Its robots.txt says 'Content-Signal: ai-train=no'. Not used; the Internet Archive's copies of its public-domain "
     "recordings are offered instead as the source librivox, off unless named in --sources (the owner decides)."),
    ("us.openslr.org (an openslr mirror)", "Its robots.txt closes it to programs; the kit uses www.openslr.org."),
    ("Social Security Administration notices (ssa.gov)",
     "www.ssa.gov answers programs with 403 Forbidden (Access Denied). Not used."),
    ("Agency customer service email templates and sample responses",
     "No public-domain collection of them with a bulk route was found: agencies publish form letters and notice "
     "explanations (used: gov_letters), not their email templates."),
    ("Project Gutenberg's main site (www.gutenberg.org)",
     "Its robots.txt closes the book pages to programs; the kit uses Gutenberg's official mirror "
     "(gutenberg.pglaf.org) and its catalogue file, as before."),
]
