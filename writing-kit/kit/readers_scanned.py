"""Email releases that are SCANNED PAGES (pictures of printed emails, with no text), read with OCR (ocr.py).

  split_messages(text)        [(header lines, body)] for each email printed in a page's text (From, Sent, To,
                              Subject headers start a message)
  government_reason(...)      why a PDF counts as a US federal government work, or "" when it does not
  sender_outside_government   True when a message's From line shows an address outside the US federal government
  records_from_pdf(...)       email records from one PDF, with the pages each message came from saved beside it
                              as page pictures plus their OCR text
  read_scanned_folder         the PDFs in a folder the owner downloaded himself (--scanned-folder)
  read_ia_federal             Internet Archive copies of US federal email releases (Clinton State Department
                              emails, a DHS release, NIH FOIA emails, EPA Flint documents)
  read_ia_state               Internet Archive copies of state email releases (Sarah Palin's Alaska emails,
                              Governor Snyder's Flint emails): personal use only
  read_govinfo_exhibits       scanned exhibits printed inside US Congress hearing records on GovInfo

Licences: a US federal government work is public domain (open). A state's records, and any message whose sender
writes from outside the federal government (a company, a private address, a state office), are personal use only.
Privacy is the same as everywhere in the kit: only identity, card and bank numbers and passwords are masked, in the
text and (as black boxes) on the saved page pictures; everything else is kept.
"""

import json
import os
import re

import ocr

HEADER_WORDS = r"(?:From|Sent|Date|To|Cc|Bcc|Subject|Attachments?|Importance)"
HEADER_LINE = re.compile(r"^\s*" + HEADER_WORDS + r"\s*:", re.I)

# Lines that are release stamps, page numbers or redaction codes, not the writer's words.
STAMP_LINES = [
    r"U\.?\s?S\.? Department of State.*(Case|Doc) No",
    r"^\s*UNCLASSIFIED\b.*$",
    r"^\s*(RELEASE IN (FULL|PART)|RELEASED? IN (FULL|PART))\b.*$",
    r"^\s*(B\d|\(b\)\s*\(\d\)(\s*\(\w\))?)([\s,]+(B\d|\(b\)\s*\(\d\)(\s*\(\w\))?))*\s*$",
    r"^\s*b\d\s*-\s*\d.*$",
    r"STATE DEPT\.? - PRODUCED TO HOUSE",
    r"SUBJECT TO AGREEMENT ON SENSITIVE INFORMATION",
    r"^\s*(Page|Pg\.?)\s*\d+\s*(of\s*\d+)?\s*$",
    r"^\s*\d{1,4}\s*$",
    r"^\s*[A-Z]{2,8}[-_ ]?\d{5,}\s*$",                      # Bates numbers such as EPA-0012345
    r"^\s*(Date|Doc No|Case No)\.?\s*:?\s*[A-Z]?[-\d/]+\s*$",
]
STAMP_RE = re.compile("|".join("(?:%s)" % s for s in STAMP_LINES), re.I | re.M)

# Signs of a US federal FOIA release (exemption codes and federal stamps); state releases use other words.
FEDERAL_SIGNS = [
    (r"U\.?\s?S\.? Department of State", "a US State Department release stamp"),
    (r"\(b\)\s*\((?:5|6|7)\)", "US federal FOIA exemption codes, such as (b)(6)"),
    (r"FEDERAL BUREAU OF INVESTIGATION|\bFBI\b.*\bb6\b", "an FBI release"),
    (r"Environmental Protection Agency|@epa\.gov", "an EPA release"),
    (r"@(?:\w+\.)*(?:state|nih|hhs|dhs|epa|doj|usdoj|eop|ed|dot|doi|usda|va|treasury|fda|cdc)\.gov\b",
     "federal email addresses"),
]

US_STATES = ("alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho "
             "illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota "
             "mississippi missouri montana nebraska nevada newhampshire newjersey newmexico newyork northcarolina "
             "northdakota ohio oklahoma oregon pennsylvania rhodeisland southcarolina southdakota tennessee texas "
             "utah vermont virginia washington westvirginia wisconsin wyoming myflorida mass ny nj ca tx wa or "
             "mi il pa oh ga nc az co mn wi mo md tn ct sc la ky ok ia ut nv ar ms ks nm ne wv id hi me nh ri "
             "mt de sd nd ak vt wy dc").split()


def clean_text(text):
    """text without release stamps, page numbers and lone redaction codes, with spaces tidied."""
    text = STAMP_RE.sub("", text or "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def _header_block_at(lines, i):
    """The number of header lines starting at lines[i] when they form an email header (a From line followed,
    within eight lines, by a Sent or Date line and a To or Subject line), otherwise 0."""
    if not re.match(r"^\s*From\s*:", lines[i], re.I):
        return 0
    seen, j = {"from"}, i + 1
    while j < len(lines) and j - i <= 8:
        m = re.match(r"^\s*(" + HEADER_WORDS + r")\s*:", lines[j], re.I)
        if m:
            seen.add(m.group(1).lower().rstrip("s") if m.group(1).lower().startswith("attach") else
                     m.group(1).lower())
        elif lines[j].strip() and j + 1 < len(lines) and not HEADER_LINE.match(lines[j + 1]) and \
                "subject" in seen:
            break
        elif not lines[j].strip() and "subject" in seen:
            break
        j += 1
    if seen & {"sent", "date"} and seen & {"to", "subject"}:
        return j - i
    return 0


def split_messages(text):
    """[(header text, body)] for each email in text, in order. A message starts at a header block (see
    _header_block_at) and runs to the next one. Header lines that wrap onto the next line are kept with their
    header. Text before the first header (a cover page) is left out."""
    lines = (text or "").split("\n")
    starts = []
    i = 0
    while i < len(lines):
        n = _header_block_at(lines, i)
        if n:
            starts.append((i, n))
            i += n
        else:
            i += 1
    out = []
    for k, (start, n) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        header = "\n".join(x.strip() for x in lines[start:start + n] if x.strip())
        body = "\n".join(lines[start + n:end]).strip()
        out.append((header, body))
    return out


def header_value(header, word):
    m = re.search(r"(?im)^\s*" + word + r"\s*:\s*(.*)$", header or "")
    return m.group(1).strip() if m else ""


def is_federal_domain(domain):
    """True for a US federal email domain: .mil, or .gov when it is not a state or city one (michigan.gov,
    ci.flint.mi.us, mass.gov ...)."""
    domain = domain.lower().strip(". >")
    if domain.endswith(".mil"):
        return True
    if not domain.endswith(".gov"):
        return False
    parts = domain[:-4].split(".")
    if parts[-1] == "state":                     # state.gov is the US Department of State
        return True
    return not any(p.replace("-", "") in US_STATES or p in ("co", "ci") or p.startswith("state")
                   or any(w in p for w in ("city", "county", "town", "village", "parish", "borough"))
                   for p in parts[-2:])


def sender_outside_government(header):
    """True when the From line shows an email address and it is not a US federal one. A message with no address
    (often removed by the agency) is left with the release's own licence."""
    sender = header_value(header, "From")
    addresses = re.findall(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)", sender)
    if not addresses:
        return False
    return not any(is_federal_domain(a) for a in addresses)


def government_reason(path, sample_text):
    """Why a PDF counts as a US federal government work, or "" when it does not: its folder or file name says
    so ("public domain", "government work", "federal"), or its pages carry federal release stamps or codes."""
    name = (path or "").replace("\\", "/").lower()
    if re.search(r"public[ _-]?domain|government[ _-]?works?|us[ _-]?government|federal", name):
        return "the folder or file name says it is a government work"
    for pattern, why in FEDERAL_SIGNS:
        if re.search(pattern, sample_text or "", re.I):
            return why
    return ""


def _normal_subject(subject):
    return re.sub(r"[^a-z0-9]+", "", re.sub(r"^\s*((re|fw|fwd)\s*:\s*)+", "", subject or "", flags=re.I).lower())


def link_threads(records):
    """records with each reply joined to the earlier message printed right below it (the same subject without
    "Re:"), so the example shows the message being answered. The earlier message is still yielded on its own."""
    held = None
    for record in records:
        if held is not None:
            if held["is_reply"] and _normal_subject(held["subject"]) and \
                    _normal_subject(held["subject"]) == _normal_subject(record["subject"]):
                held["body"] += "\n\n" + record["header"] + "\n\n" + record["body"]
            yield held
        held = record
    if held is not None:
        yield held


def _page_messages(pages, page_log, name, mask, group):
    """The raw email records (without a licence) in pages, a sequence of ocr.Page, and the text of the pages kept
    (for the licence decision) through the list seen."""
    pending, n = None, 0

    def finish(msg):
        header, body = msg["header"], clean_text("\n".join(msg["parts"]))
        subject = header_value(header, "Subject")
        if len(body.split()) < 5:
            return None
        files, text_from = [], []
        listed = header_value(header, "Attachments?")
        for p in msg["pages"]:
            stem = f"page {p.number:04d}"
            if p.png:
                files.append((stem + ".png", ocr.mask_page_image(p, mask), "image/png"))
            files.append((stem + " OCR.txt", mask(p.text).encode("utf-8"), "text/plain"))
        own_body = body
        if listed and len(msg["pages"]) > 1:
            own_body = clean_text(msg["parts"][0]) or body
            rest = clean_text("\n".join(msg["parts"][1:]))
            if len(rest.split()) >= 20:
                att_name = re.sub(r"[^\w.\- ()]+", "_", re.split(r"[;,]", listed)[0].strip())[:80] or "attachment"
                files.append((att_name + " (OCR text).txt", mask(rest).encode("utf-8"), "text/plain"))
                text_from.append(att_name + " (OCR text).txt")
        return {"type": "email", "subject": subject, "body": own_body, "header": header,
                "audience": "a colleague", "is_reply": bool(re.match(r"(?i)\s*re\s*:", subject)),
                "group": group or name, "msg_id": f"{name}#{msg['pages'][0].number}#{msg['n']}",
                "attachments": files, "text_from": text_from, "file": name,
                "pages": [p.number for p in msg["pages"]],
                "confidence": round(min(p.confidence for p in msg["pages"]), 3)}

    for page in pages:
        if not page.kept:
            if page.reason != "no scanned picture on this page":
                page_log.append((name, page.number, page.reason))
            continue
        yield None, page.text                       # lets the caller see each kept page's text
        pieces = split_messages(page.text)
        lead = page.text
        if pieces:
            first_header = re.search(r"(?im)^\s*From\s*:", page.text)
            lead = page.text[:first_header.start()] if first_header else ""
        if pending is not None:
            if lead.strip():
                pending["parts"].append(lead)
                pending["pages"].append(page)
            if pieces:
                done, pending = finish(pending), None
                if done:
                    yield done, ""
        for k, (header, body) in enumerate(pieces):
            n += 1
            msg = {"header": header, "parts": [body], "pages": [page], "n": n}
            if k < len(pieces) - 1:
                done = finish(msg)
                if done:
                    yield done, ""
            else:
                pending = msg
    if pending is not None:
        done = finish(pending)
        if done:
            yield done, ""


def records_from_pdf(data, name, say=print, page_log=None, mask=None, group="", first=1, last=None,
                     only_image_pages=False, licence_open=None):
    """Email records from one scanned PDF (bytes). Pages left out (low confidence, almost no text) are added to
    page_log as (file, page, reason). Each record keeps the pictures and OCR text of the pages it came from as
    attachments; when its header lists attachments, the pages after its first page are the attachment, and their
    text becomes an attachment text ("text_from"). licence_open: True or False (the release's own class), or None
    to decide from the file name and the first pages' stamps (government_reason). Each record's "licence_open" is
    True only for a government work whose message does not come from outside the federal government."""
    mask = mask or (lambda t: t)
    page_log = page_log if page_log is not None else []
    federal, seen, kept_pages, queue = licence_open, "", 0, []

    def ready():
        for record in queue:
            record["licence_open"] = bool(federal) and not sender_outside_government(record["header"])
        out = list(queue)
        queue.clear()
        return out

    def decide():
        why = government_reason(name, seen)
        say(f"  {name}: " + (f"a US government work ({why})." if why else
                             "personal use only (no sign of a US federal release)."))
        return bool(why)

    def raw():
        nonlocal federal, seen, kept_pages
        pages = ocr.read_pdf(data, first=first, last=last, only_image_pages=only_image_pages)
        for record, text in _page_messages(pages, page_log, name, mask, group):
            if record is None:
                kept_pages += 1
                if federal is None:
                    seen += text + "\n"
                    if kept_pages >= 3:
                        federal = decide()
                continue
            queue.append(record)
            if federal is not None:
                yield from ready()
        if federal is None:
            federal = decide()
        yield from ready()

    yield from link_threads(raw())


# ----------------------------------------------------------------- the owner's own folder of PDFs

def read_scanned_folder(fetcher=None, say=print, folder="", page_log=None, max_pages=0, **_):
    """Email records from every PDF in folder (and its subfolders), in name order. Nothing is downloaded."""
    ok, why = ocr.available()
    if not ok:
        raise ocr.OcrUnavailable(why)
    if not folder or not os.path.isdir(folder):
        raise ValueError(f"the scanned folder {folder!r} was not found")
    import scrub
    paths = []
    for root, _dirs, files in os.walk(folder):
        paths += [os.path.join(root, f) for f in files if f.lower().endswith(".pdf")]
    paths.sort(key=lambda p: p.lower())
    say(f"  Scanned folder: {len(paths)} PDF files in {folder}.")
    for path in paths:
        rel = os.path.relpath(path, folder)
        with open(path, "rb") as f:
            data = f.read()
        try:
            pages = ocr.page_count(data)
        except Exception as err:                     # a damaged or protected PDF: note it and go on
            say(f"  {rel}: cannot be opened ({err}); left out.")
            if page_log is not None:
                page_log.append((rel, 0, f"the PDF cannot be opened: {err}"))
            continue
        say(f"  Reading {rel} ({pages} pages) with OCR.")
        yield from records_from_pdf(data, rel, say, page_log, scrub.mask_identifiers, group=rel,
                                    last=max_pages or None)


# ----------------------------------------------------------------- Internet Archive copies of releases

IA_META = "https://archive.org/metadata/{item}"
IA_FILE = "https://archive.org/download/{item}/{name}"

# The releases, checked by hand in November 2026 (each item's metadata is read again at every build).
IA_FEDERAL = [
    ("ClintonEmails10-21", "Clinton State Department emails, release of 21 October 2016"),
    ("2018hqfo01030", "DHS emails, FOIA request 2018-HQFO-01030"),
    ("hillary-clinton-emails-august-31-release", "Clinton State Department emails, release of 31 August 2015"),
    ("francis-collins-nih-emails-industry-fnih-foia-april-2022-production", "NIH emails, FOIA 47589"),
    ("epa-flint-documents", "EPA Flint water documents, interim release of 12 May 2016"),
]
IA_STATE = [
    ("palinemails", "Sarah Palin's Alaska governor emails, released 10 June 2011 (scanned by the Anchorage Daily "
                    "News)"),
    ("296110961SnyderEMails", "Michigan Governor Rick Snyder's Flint emails, January 2016 release"),
    ("snyder_flint_emails", "Michigan Governor Rick Snyder's and state departments' Flint emails"),
]
IA_LEFT_OUT_COLLECTIONS = {"documentcloud"}     # DocumentCloud mirrors: DocumentCloud reserves AI training


def ia_pdfs(meta, max_mb):
    """[(name, size)] of an Internet Archive item's own PDF files (not derived copies or deleted ones) under max_mb
    megabytes, smallest first."""
    out = []
    for f in meta.get("files", []):
        name = f.get("name", "")
        if not name.lower().endswith(".pdf") or f.get("source") != "original" or name.startswith("deletes/"):
            continue
        size = int(f.get("size") or 0)
        if size and size <= max_mb * 1024 * 1024:
            out.append((name, size))
    return sorted(out, key=lambda x: (x[1], x[0]))


def _read_ia(items, fetcher, say, page_log, federal, max_mb=80, files_per_item=4, max_pages=300):
    import scrub
    ok, why = ocr.available()
    if not ok:
        raise ocr.OcrUnavailable(why)
    for item, label in items:
        meta = json.loads(fetcher.get(IA_META.format(item=item)))
        md = meta.get("metadata", {})
        collections = md.get("collection") or []
        collections = [collections] if isinstance(collections, str) else collections
        if set(collections) & IA_LEFT_OUT_COLLECTIONS:
            say(f"  {item}: left out (a DocumentCloud mirror; DocumentCloud reserves AI training).")
            continue
        licence = str(md.get("licenseurl") or "")
        if federal and "publicdomain" not in licence:
            say(f"  {item}: left out (not marked public domain on the Internet Archive).")
            continue
        pdfs = ia_pdfs(meta, max_mb)
        say(f"  {label} ({item}): {len(pdfs)} PDF files under {max_mb} MB; reading up to {files_per_item}.")
        for name, size in pdfs[:files_per_item]:
            data = fetcher.get(IA_FILE.format(item=item, name=name))
            yield from records_from_pdf(data, f"{item}/{name}", say, page_log, scrub.mask_identifiers,
                                        group=item, last=max_pages, licence_open=federal)


def read_ia_federal(fetcher, say=print, page_log=None, scanned_max_mb=80, **_):
    yield from _read_ia(IA_FEDERAL, fetcher, say, page_log, True, scanned_max_mb, files_per_item=30)


def read_ia_state(fetcher, say=print, page_log=None, scanned_max_mb=80, **_):
    yield from _read_ia(IA_STATE, fetcher, say, page_log, False, scanned_max_mb)


# ----------------------------------------------------------------- GovInfo hearing records with scanned exhibits

GOVINFO_SITEMAP = "https://www.govinfo.gov/sitemap/CHRG_{year}_sitemap.xml"
GOVINFO_HTM = "https://www.govinfo.gov/content/pkg/{pkg}/html/{pkg}.htm"
GOVINFO_PDF = "https://www.govinfo.gov/content/pkg/{pkg}/pdf/{pkg}.pdf"


def exhibit_hint(page_text):
    """True when a hearing record's text shows scanned exhibits (graphics) placed near the words email or e-mail,
    so its PDF is worth reading with OCR."""
    for m in re.finditer(r"\[GRAPHICS?(?:\(S\))? NOT AVAILABLE IN TIFF FORMAT\]|\[GRAPHIC\] \[TIFF OMITTED\]",
                         page_text):
        if re.search(r"(?i)\be-?mails?\b", page_text[max(0, m.start() - 600): m.start()]):
            return True
    return False


def read_govinfo_exhibits(fetcher, say=print, page_log=None, years=("2016", "2015", "2017"), per_year=40,
                          max_pdfs=6, scanned_max_mb=80, **_):
    """Email records from scanned exhibits in House and Senate hearing records: the hearings whose text shows
    graphics next to the word email; only the pages with pictures are read."""
    import scrub
    ok, why = ocr.available()
    if not ok:
        raise ocr.OcrUnavailable(why)
    read = 0
    for year in years:
        sitemap = fetcher.get(GOVINFO_SITEMAP.format(year=year)).decode("utf-8", "replace")
        packages = re.findall(r"<loc>https://www\.govinfo\.gov/app/details/(CHRG-[\w-]+)</loc>", sitemap)
        say(f"  GovInfo hearing records: {len(packages)} listed for {year}; looking at {per_year} for email "
            "exhibits.")
        for pkg in packages[:per_year]:
            if read >= max_pdfs:
                return
            text = fetcher.get(GOVINFO_HTM.format(pkg=pkg)).decode("utf-8", "replace")
            if not exhibit_hint(text):
                continue
            data = fetcher.get(GOVINFO_PDF.format(pkg=pkg))
            if len(data) > scanned_max_mb * 1024 * 1024:
                continue
            read += 1
            say(f"  {pkg}: scanned exhibits found; reading their pages with OCR.")
            yield from records_from_pdf(data, pkg, say, page_log, scrub.mask_identifiers, group=pkg,
                                        only_image_pages=True, licence_open=True)
