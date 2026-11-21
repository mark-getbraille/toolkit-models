"""Public meeting readers for the Writing Kit: real speech and public notices from US and Canadian public bodies, added
at the owner's request for colloquial, spoken English. writing_sources.py lists each with its licence;
sources-not-used.txt lists the meeting sources checked and left out (with the reason).

  read_scotus       US Supreme Court oral argument transcripts (supremecourt.gov PDFs; public domain)
  read_hearings     US Congress committee hearing transcripts (GovInfo, collection CHRG; public domain)
  read_fedreg       public meeting notices in the Federal Register (its free API, no key; public domain)
  read_hansard      Canada's House of Commons debates (ourcommons.ca XML; reproduction allowed for non-commercial
                    use only, so personal use only). Canadian English spelling and parliamentary procedure.

Each yields chat records ("write the next speaker's words", see build_dataset.examples_from_chat) with the whole
transcript in "raw", which the builder also saves as a plain text file (output/transcripts/<source>/), or text
records for the notices. Every request goes through fetch.Fetcher (robots.txt obeyed, AI-training refusals obeyed,
requests paced).
"""

import html
import json
import re
import shutil
import subprocess
import tempfile
import os

SCOTUS_LIST = "https://www.supremecourt.gov/oral_arguments/argument_transcript/{term}"
SCOTUS_PDF = "https://www.supremecourt.gov/oral_arguments/"
GOVINFO_SITEMAP = "https://www.govinfo.gov/sitemap/CHRG_{year}_sitemap.xml"
GOVINFO_HTM = "https://www.govinfo.gov/content/pkg/{pkg}/html/{pkg}.htm"
FEDREG_API = ("https://www.federalregister.gov/api/v1/documents.json?per_page=100&page={page}"
              "&conditions%5Btype%5D%5B%5D=NOTICE&conditions%5Bterm%5D=%22public+meeting%22"
              "&fields%5B%5D=title&fields%5B%5D=abstract&fields%5B%5D=agencies&fields%5B%5D=document_number"
              "&order=newest")
HANSARD_XML = "https://www.ourcommons.ca/Content/House/{parl}{sess}/Debates/{num:03d}/HAN{num:03d}-E.XML"
CANADA_NOTE = ("Canadian English (spellings such as 'colour' and 'centre') and Canadian parliamentary procedure "
               "(the Speaker, 'Mr. Speaker', members addressed through the Chair).")


def pdf_text(data):
    """The text of a PDF (with the pdftotext program), keeping the page layout; "" without the program."""
    tool = shutil.which("pdftotext")
    if not tool:
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "in.pdf")
        with open(path, "wb") as f:
            f.write(data)
        out = subprocess.run([tool, "-q", "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, timeout=120)
        return out.stdout.decode("utf-8", "replace")


def join_turns(lines, speaker_re):
    """[(speaker, words)] from transcript lines: a line that starts with a speaker label starts a new turn."""
    turns = []
    for line in lines:
        m = speaker_re.match(line)
        if m:
            turns.append([m.group(1).strip().rstrip(".:"), m.group(2).strip()])
        elif turns and line.strip():
            turns[-1][1] += " " + line.strip()
    return [(who, re.sub(r"\s+", " ", words).strip()) for who, words in turns if words.strip()]


# ----------------------------------------------------------------- US Supreme Court oral arguments

SCOTUS_SPEAKER = re.compile(r"^\s*((?:CHIEF )?JUSTICE [A-Z'\-]+|M[RS]S?\. [A-Z'\-]+|GENERAL [A-Z'\-]+):\s*(.*)$")


def scotus_turns(text):
    """[(speaker, words)] from the text of an oral argument transcript: line numbers, page headers and footers and
    the index pages left out."""
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s*\d{1,2}(\s+|$)", "", line)                   # the line numbers 1 to 25
        if re.search(r"Heritage Reporting Corporation|Official - Subject to Final Review|^\s*\d+\s*$", line):
            continue
        lines.append(line)
    body = "\n".join(lines)
    start = re.search(r"P R O C E E D I N G S", body)
    body = body[start.end():] if start else body
    end = re.search(r"\(Whereupon,? at .*?the case was submitted", body, re.S)
    body = body[:end.start()] if end else body
    return join_turns(body.splitlines(), SCOTUS_SPEAKER)


def read_scotus(fetcher, say=print, terms=("2024", "2023"), per_term=8, **_):
    for term in terms:
        page = fetcher.get(SCOTUS_LIST.format(term=term)).decode("utf-8", "replace")
        links = []
        for link in re.findall(r"href=['\"](?:\.\./)?(argument_transcripts/\d{4}/[^'\"]+\.pdf)['\"]", page, re.I):
            if link not in links:
                links.append(link)
        say(f"  Supreme Court: {len(links)} transcripts listed for the {term} term; reading {per_term}.")
        for link in links[:per_term]:
            text = pdf_text(fetcher.get(SCOTUS_PDF + link))
            turns = scotus_turns(text)
            if len(turns) >= 4:
                yield {"type": "chat", "turns": turns, "setting": "a US Supreme Court oral argument", "group": term,
                       "style": "speech", "raw": text, "raw_name": link.split("/")[-1].replace(".pdf", ".txt")}


# ----------------------------------------------------------------- US Congress hearings (GovInfo CHRG)

HEARING_SPEAKER = re.compile(r"^ {4}((?:Mr|Ms|Mrs|Dr)\. [A-Z][A-Za-z'\-]+(?: of [A-Z][a-z]+)?|The CHAIRMAN|"
                             r"Chairman [A-Z][A-Za-z'\-]+|Chairwoman [A-Z][A-Za-z'\-]+|Senator [A-Z][A-Za-z'\-]+|"
                             r"Voice|The Clerk)\. (.*)$")


def hearing_turns(text):
    """[(speaker, words)] from a hearing transcript's plain text (the part inside <pre>)."""
    lines = [ln for ln in text.splitlines() if not re.match(r"^\s*\[[^\]]*\]\s*$", ln)]   # [Applause.] and the like
    turns = join_turns(lines, HEARING_SPEAKER)
    return [(who, words) for who, words in turns if not words.startswith("[")]


def read_hearings(fetcher, say=print, years=("2023", "2019", "2015"), per_year=6, **_):
    for year in years:
        sitemap = fetcher.get(GOVINFO_SITEMAP.format(year=year)).decode("utf-8", "replace")
        packages = re.findall(r"<loc>https://www\.govinfo\.gov/app/details/(CHRG-[\w-]+)</loc>", sitemap)
        say(f"  GovInfo hearings: {len(packages)} listed for {year}; reading {per_year}.")
        for pkg in packages[:per_year]:
            page = fetcher.get(GOVINFO_HTM.format(pkg=pkg)).decode("utf-8", "replace")
            m = re.search(r"<pre>(.*?)</pre>", page, re.S | re.I)
            text = html.unescape(m.group(1)) if m else ""
            turns = hearing_turns(text)
            if len(turns) >= 4:
                yield {"type": "chat", "turns": turns, "setting": "a US Congress committee hearing", "group": year,
                       "style": "speech", "raw": text, "raw_name": pkg + ".txt"}


# ----------------------------------------------------------------- Federal Register public meeting notices

def read_fedreg(fetcher, say=print, pages=4, **_):
    """Text records: "write a public notice announcing this meeting" with the notice's own summary."""
    for page in range(1, pages + 1):
        data = json.loads(fetcher.get(FEDREG_API.format(page=page)))
        for doc in data.get("results", []):
            abstract = (doc.get("abstract") or "").strip()
            if len(abstract.split()) < 15:
                continue
            agency = ", ".join(a.get("name", "") for a in doc.get("agencies", []) if a.get("name")) or "a US agency"
            yield {"type": "text", "group": "fedreg", "kind": "announcement", "form": "public notice",
                   "tone": "formal", "audience": "the public",
                   "instruction": f"Write a short public notice for the {agency} announcing a public meeting: "
                                  f"\"{doc.get('title', '').strip()}\". Say who is meeting, when and why, and how "
                                  "the public can take part.",
                   "response": abstract}


# ----------------------------------------------------------------- Canada: House of Commons debates

def hansard_turns(xml):
    """[(speaker, words)] from a Debates XML file: each <Intervention> with its <PersonSpeaking> and paragraphs."""
    turns = []
    for block in re.findall(r"<Intervention\b.*?</Intervention>", xml, re.S):
        who = re.search(r"<Affiliation[^>]*>(.*?)</Affiliation>", block, re.S)
        paras = re.findall(r"<ParaText[^>]*>(.*?)</ParaText>", block, re.S)
        if not who or not paras:
            continue
        speaker = html.unescape(re.sub(r"<[^>]+>", "", who.group(1))).strip()
        words = " ".join(html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in paras)
        turns.append((speaker, re.sub(r"\s+", " ", words)))
    return turns


def read_hansard(fetcher, say=print, sittings=((45, 1, range(2, 60)),), **_):
    """Chat records from House of Commons debates (English XML), with the whole debate kept as raw text."""
    for parl, sess, numbers in sittings:
        for num in numbers:
            url = HANSARD_XML.format(parl=parl, sess=sess, num=num)
            try:
                xml = fetcher.get(url).decode("utf-8-sig", "replace")
            except Exception as err:
                if "robots" in str(err):
                    raise
                continue
            turns = hansard_turns(xml)
            if len(turns) >= 4:
                raw = "\n\n".join(f"{who}:\n{words}" for who, words in turns)
                yield {"type": "chat", "turns": turns, "group": f"{parl}-{sess}", "style": "speech",
                       "setting": "a debate in Canada's House of Commons. " + CANADA_NOTE, "raw": raw,
                       "raw_name": f"HAN{num:03d}-{parl}-{sess}.txt"}
