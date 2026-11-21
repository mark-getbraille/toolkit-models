"""Recent business email released through court cases and government investigations (about 2010 to now), added at
the owner's request because the Enron emails are over twenty years old. writing_sources.py lists each with its
licence; sources-not-used.txt lists the ones checked and left out.

  read_idl         the UCSF Industry Documents Library: internal company emails made public in litigation (opioids,
                   tobacco, chemicals, food, drugs, fossil fuels), with their attachments, through the library's own
                   search interface (Solr), which gives each document's text. Only documents marked public with no
                   restrictions are read.
  read_doj_google  the trial exhibits the US Department of Justice published for United States v. Google LLC (the
                   2023 search trial): the exhibits that are emails, read from the official PDFs.

The companies' emails keep their writers' copyright, so both are personal use only. The same narrow masking applies
(Social Security, card, bank and account numbers, passwords); everything else is kept.
"""

import json
import re
import urllib.parse

IDL_SOLR = ("https://solr.idl.ucsf.edu/solr/ltdl3/select?q={q}&fq={fq}&fl={fl}&rows={rows}&start={start}"
            "&wt=json")
IDL_FIELDS = "id,bn,ti,industry,collection,dddate,attachment,ot,au,rc"
IDL_INDUSTRIES = ["Opioids", "Drug", "Food", "Chemical", "Fossil Fuel", "Tobacco"]
DOJ_GOOGLE = "https://www.justice.gov/atr/us-and-plaintiff-states-v-google-llc-2020-trial-exhibits"


def idl_query(q, fq, rows, start, fields=IDL_FIELDS):
    return IDL_SOLR.format(q=urllib.parse.quote(q), fq=urllib.parse.quote(fq), fl=fields, rows=rows, start=start)


def email_parts(text):
    """(subject, body, header text) of an email printed as text with Subject:, From:, Date: and To: lines at the top."""
    text = (text or "").replace("﻿", "").replace("\r\n", "\n").strip()
    m = re.match(r"((?:[ \t]*(?:Subject|From|Date|Sent|To|Cc|CC|Bcc|Attachments?|Importance)\s*:.*\n(?:[ \t]+.*\n)*)+)",
                 text + "\n")
    header = m.group(1) if m else ""
    subject = (re.search(r"(?im)^\s*Subject\s*:\s*(.*)$", header) or [None, ""])[1].strip()
    return subject, text[len(header):].strip() if header else text, header


def read_idl(fetcher, say=print, per_industry=60, since="2010-01-01", **_):
    """Email records (with attachment texts) from the Industry Documents Library, from 2010 on, from each industry."""
    fq = f"availability:public AND dddate:[{since}T00:00:00Z TO *]"
    for industry in IDL_INDUSTRIES:
        q = f'dt:Email AND industry:"{industry}"'
        got, start = 0, 0
        while got < per_industry and start < per_industry * 4:
            data = json.loads(fetcher.get(idl_query(q, fq, 25, start)))
            docs = data.get("response", {}).get("docs", [])
            if start == 0:
                say(f"  Industry Documents Library, {industry}: {data.get('response', {}).get('numFound', 0)} "
                    f"public emails since {since[:4]}.")
            if not docs:
                break
            start += len(docs)
            for doc in docs:
                subject, body, header = email_parts(doc.get("ot", ""))
                if len(body.split()) < 5:
                    continue
                files = []
                numbers = doc.get("attachment") or []
                if numbers:
                    found = json.loads(fetcher.get(idl_query("bn:(" + " OR ".join(numbers[:5]) + ")",
                                                             "availability:public", 5, 0, "id,bn,ti,ot")))
                    for att in found.get("response", {}).get("docs", []):
                        name = re.sub(r"[^\w.\- ]+", "_", att.get("ti") or att.get("bn") or "attachment")[:80]
                        files.append((name if "." in name[-6:] else name + ".txt", (att.get("ot") or "")
                                      .encode("utf-8"), "text/plain"))
                yield {"type": "email", "subject": subject or doc.get("ti", ""), "body": body,
                       "audience": "a colleague", "is_reply": bool(re.match(r"(?i)\s*re\s*:", subject)),
                       "group": industry, "attachments": files, "msg_id": doc.get("id", ""),
                       "header": header, "date": (doc.get("dddate") or [""])[0][:10]}
                got += 1
                if got >= per_industry:
                    break


def read_doj_google(fetcher, say=print, limit=60, **_):
    """Email records from the US v. Google trial exhibits that are emails (the PDF is saved beside each one)."""
    import readers_meetings
    page = fetcher.get(DOJ_GOOGLE).decode("utf-8", "replace")
    links = re.findall(r'<a href="(https://www\.justice\.gov/d9/[^"]+\.pdf)">([^<]{1,40})</a>', page)
    say(f"  US v. Google exhibits: {len(links)} listed; reading up to {limit * 3} to find {limit} emails.")
    got = 0
    for url, label in links[:limit * 3]:
        data = fetcher.get(url)
        text = readers_meetings.pdf_text(data)
        if not re.search(r"(?im)^\s*From\s*:", text) or not re.search(r"(?im)^\s*(Sent|Date|To)\s*:", text):
            continue
        text = re.sub(r"(?m)^\s*(REDACTED FOR PUBLIC FILING|HIGHLY CONFIDENTIAL.*|CONFIDENTIAL.*|GOOG-DOJ-\d+|"
                      r"Plaintiffs?'? ?Exhibit.*|PSX\d+|UPX\d+|DX\d+)\s*$", "", text)
        text = re.sub(r"[ \t]{3,}", "  ", text)
        start = re.search(r"(?im)^\s*From\s*:", text)
        subject, body, header = email_parts(text[start.start():].lstrip())
        if len(body.split()) < 10:
            continue
        yield {"type": "email", "subject": subject, "body": body, "audience": "a colleague", "is_reply":
               bool(re.match(r"(?i)\s*re\s*:", subject)), "group": "doj-google", "msg_id": url,
               "attachments": [(label.strip() + ".pdf", data, "application/pdf")], "no_attachment_text": True}
        got += 1
        if got >= limit:
            break
