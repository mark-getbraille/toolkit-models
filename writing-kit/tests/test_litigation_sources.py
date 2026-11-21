"""Tests of the litigation and investigation email readers (kit/readers_litigation.py). All data is made up; no
network is used."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import readers_litigation as rl  # noqa: E402
import readers_meetings  # noqa: E402


class FakeFetcher:
    def __init__(self, answer):
        self.answer = answer
        self.asked = []

    def get(self, url):
        self.asked.append(url)
        return self.answer(url)


def test_email_parts_split_the_printed_header():
    text = ("﻿Subject: Re: Q4 targets\nFrom: \"Quill, Tam\" <tam@example.com>\nDate: Thu, 03 Oct 2013\n"
            "To: \"Ray, Bo\" <bo@example.com>,\n    \"Lee, Jo\" <jo@example.com>\n\nBo, the numbers look right to me.\n")
    subject, body, header = rl.email_parts(text)
    assert subject == "Re: Q4 targets"
    assert body == "Bo, the numbers look right to me."
    assert "Lee, Jo" in header


def test_idl_reads_public_emails_with_their_attachments(monkeypatch):
    monkeypatch.setattr(rl, "IDL_INDUSTRIES", ["Opioids"])
    email_doc = {"id": "abcd0001", "ti": "Re: Q4 targets", "dddate": ["2013-10-03T00:00:00Z"],
                 "attachment": ["BATES0002"],
                 "ot": "Subject: Re: Q4 targets\nFrom: Tam <tam@example.com>\n\nBo, my PIN 4471 is on the form."}
    att_doc = {"id": "abcd0002", "bn": "BATES0002", "ti": "Q4 plan.docx", "ot": "Plan for the fourth quarter."}

    def answer(url):
        if "bn%3A" in url:
            return json.dumps({"response": {"docs": [att_doc]}}).encode()
        if "start=0" in url:
            return json.dumps({"response": {"numFound": 1, "docs": [email_doc]}}).encode()
        return json.dumps({"response": {"docs": []}}).encode()

    f = FakeFetcher(answer)
    records = list(rl.read_idl(f, say=lambda t: None, per_industry=1))
    assert len(records) == 1
    r = records[0]
    assert r["subject"] == "Re: Q4 targets" and r["is_reply"] and r["date"] == "2013-10-03"
    assert r["attachments"] == [("Q4 plan.docx", b"Plan for the fourth quarter.", "text/plain")]
    assert "availability%3Apublic" in f.asked[0]


def test_doj_exhibits_keep_only_emails(monkeypatch):
    page = ('<a href="https://www.justice.gov/d9/2023-10/1.pdf">PSX001</a>'
            '<a href="https://www.justice.gov/d9/2023-10/2.pdf">PSX002</a>').encode()
    texts = {b"pdf1": "Slide deck\nRevenue chart\n",
             b"pdf2": "REDACTED FOR PUBLIC FILING\nFrom: Jo Lee\nSent: Monday, May 4, 2015\nTo: Bo Ray\n"
                      "Subject: Re: default search deal\n\nBo, can we talk about the renewal terms this week? "
                      "I think we can get there.\n"}
    monkeypatch.setattr(readers_meetings, "pdf_text", lambda data: texts[data])
    f = FakeFetcher(lambda url: page if url == rl.DOJ_GOOGLE else (b"pdf1" if url.endswith("1.pdf") else b"pdf2"))
    records = list(rl.read_doj_google(f, say=lambda t: None, limit=5))
    assert len(records) == 1
    assert records[0]["subject"] == "Re: default search deal"
    assert records[0]["body"].startswith("Bo, can we talk")
    assert records[0]["attachments"][0][0] == "PSX002.pdf" and records[0]["no_attachment_text"]
