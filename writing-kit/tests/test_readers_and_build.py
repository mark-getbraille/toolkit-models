"""Tests of the readers (kit/readers.py) and the whole build (kit/build_dataset.py) with made-up data: a tiny
Enron-style tar.gz made here, a made-up W3C archive page, and made-up OASST and Dolly lines. No network is used."""

import io
import json
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import build_dataset  # noqa: E402
import readers  # noqa: E402
import readers_more  # noqa: E402
import readers_meetings  # noqa: E402
import readers_business  # noqa: E402
import writing_sources  # noqa: E402

MAIL = """Message-ID: <1.JavaMail.evans@thyme>
Date: Mon, 14 May 2001 16:39:00 -0700 (PDT)
From: wren.calloway@enron.com
To: idris.mavros@enron.com
Subject: Re: Thursday review
X-From: Wren Calloway
X-To: Idris Mavros
X-cc:
X-bcc:

Idris,

Thanks for pulling the numbers together so fast. Could you send me the final version
by Wednesday afternoon so I can read it before the review?

Wren

 -----Original Message-----
From: Mavros, Idris
Private earlier text with 713-555-0142
"""

SICK = MAIL.replace("Thanks for pulling the numbers together so fast.", "I am off sick with the flu today.")


def make_tar(files):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w:gz") as tar:
        for name, text in files.items():
            raw = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    data.seek(0)
    return data


def test_enron_reader_takes_only_sent_mail_and_never_attachments():
    tar = make_tar({"maildir/calloway-w/sent/1.": MAIL,
                    "maildir/calloway-w/inbox/1.": MAIL.replace("Thursday", "Inbox"),
                    "maildir/calloway-w/_sent_mail/2.": "Content-Type: multipart/mixed; boundary=x\n\n--x\n"})
    records = list(readers.enron_records(tar, say=lambda t: None))
    assert len(records) == 1
    r = records[0]
    assert r["subject"] == "Re: Thursday review" and r["is_reply"]
    assert r["audience"] == "a colleague"
    assert "calloway" in r["writer_names"]


W3C_PAGE = """<html><head>
<meta name="Author" content="Peregrine Oduya (p.oduya&#x40;example.org)" />
<meta name="Subject" content="Re: Agenda for Thursday's call" />
</head><body>
<!-- inreplyto="abc&#64;example.org" -->
<li><span class="to"><span class="heading">To</span>: list@w3.org</span></li>
<pre id="start" class="body">
Hi all,

Regrets for Thursday's call, I will be travelling. I will read the minutes afterwards and send any comments by Friday.

Peregrine
</pre>
<a href="att-0001/diagram.png">attachment</a>
</body></html>"""


def test_w3c_page_reader_takes_the_text_only():
    r = readers.w3c_message(W3C_PAGE)
    assert r["subject"] == "Re: Agenda for Thursday's call"
    assert r["is_reply"] and r["audience"] == "the members of a mailing list"
    assert "Regrets for Thursday's call" in r["body"] and "diagram" not in r["body"]


OASST = {"prompt": {"text": "Write a short email to my landlord asking when the boiler will be fixed.",
                    "role": "prompter", "lang": "en", "synthetic": False, "replies": [
                        {"role": "assistant", "rank": 1, "synthetic": False, "text": "Second best answer."},
                        {"role": "assistant", "rank": 0, "synthetic": False,
                         "text": "Sure! Here's an email:\n\nDear Mr. Haldane,\n\nI hope you are well. Could you let "
                                 "me know when the boiler will be repaired? It has not worked since Monday.\n\n"
                                 "Kind regards,\n[Your Name]"}]}}
OASST_POEM = {"prompt": {"text": "Write a poem about email.", "lang": "en", "replies": []}}


def test_oasst_reader_picks_writing_requests_and_the_best_answer():
    lines = [json.dumps(OASST), json.dumps(OASST_POEM)]
    records = list(readers.oasst_records(lines))
    assert len(records) == 1
    assert records[0]["response"].startswith("Dear Mr. Haldane,")
    assert records[0]["response"].endswith("[Your name]")


def test_dolly_reader_picks_writing_requests():
    lines = [json.dumps({"instruction": "Write a thank-you note to a colleague who covered for me.",
                         "context": "", "response": "Thanks so much for covering for me on Friday.",
                         "category": "creative_writing"}),
             json.dumps({"instruction": "What is email?", "context": "", "response": "A way to send messages.",
                         "category": "open_qa"})]
    assert len(list(readers.dolly_records(lines))) == 1


def test_strict_build_writes_scrubbed_files(tmp_path, monkeypatch):
    def fake_enron(fetcher, say=print, **_):
        yield from readers.enron_records(make_tar({"maildir/calloway-w/sent/1.": MAIL,
                                                   "maildir/calloway-w/sent/2.": SICK}), say)

    def fake_oasst(fetcher, say=print, **_):
        yield from readers.oasst_records([json.dumps(OASST)])

    monkeypatch.setattr(readers, "read_enron", fake_enron)
    monkeypatch.setattr(readers, "read_oasst2", fake_oasst)
    out = tmp_path / "out"
    assert build_dataset.main(["--out", str(out), "--sources", "enron,oasst2", "--personal",
                               "--privacy", "strict"]) == 0
    rows = [json.loads(line) for name in ("train.jsonl", "validation.jsonl")
            for line in open(out / name, encoding="utf-8")]
    assert len(rows) == 2                                 # the sick-day message was dropped
    text = json.dumps(rows)
    for private in ["Wren", "Calloway", "Idris", "Mavros", "Haldane", "555", "enron.com", "Private earlier"]:
        assert private not in text, private
    enron = [r for r in rows if r["source"] == "enron"][0]
    assert enron["licence_class"] == writing_sources.PERSONAL
    assert enron["instruction"].startswith(("Write", "Draft", "Reply", "Thank"))
    assert enron["messages"][0] == {"role": "user", "content": enron["instruction"]}
    assert enron["messages"][1]["content"] == enron["response"]
    for key in ["instruction", "response", "source", "licence", "licence_class", "kind", "tone", "audience"]:
        assert key in enron
    report = (out / "build-report.txt").read_text(encoding="utf-8")
    assert "sensitive: health or medical: 1" in report
    assert "PERSONAL USE ONLY" in (out / "ATTRIBUTION.txt").read_text(encoding="utf-8")
    assert "foia.state.gov" in (out / "sources-not-used.txt").read_text(encoding="utf-8")
    assert (out / "samples.txt").exists()


def test_personal_sources_need_the_choice(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(readers, "read_enron", lambda *a, **k: called.append(1) or iter(()))
    monkeypatch.setattr(readers, "read_dolly", lambda *a, **k: iter(()))
    build_dataset.main(["--out", str(tmp_path), "--sources", "enron,dolly"])
    assert not called


def test_every_source_is_recorded_with_a_licence_class():
    for s in writing_sources.SOURCES:
        assert s.licence_class in writing_sources.CLASSES
        assert s.licence and s.credit and s.home.startswith("https://")
        assert any(hasattr(m, s.reader) for m in build_dataset.READER_MODULES)
    assert len(writing_sources.NOT_USED) >= 8


ATTACHED = """From: wren.calloway@example.com
To: idris.mavros@example.com
Subject: Re: Thursday review
Message-ID: <42@example.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="XX"

--XX
Content-Type: text/plain

Idris, I'm off sick today, so the review can wait. My SSN for the form is 123-45-6789 and the
door code password: blue42!

Wren

On Monday Idris Mavros wrote:
> Can we do the review on Thursday?
--XX
Content-Type: text/plain; name="memo.txt"
Content-Disposition: attachment; filename="memo.txt"

MEMO. To all staff: the kitchen will be closed on Friday for cleaning. Please take your mugs home
on Thursday evening and do not leave food in the fridge over the weekend. Thank you all.
--XX--
"""


def test_owner_build_keeps_whole_messages_and_attachments(tmp_path, monkeypatch):
    def fake_enron(fetcher, say=print, **_):
        yield readers.enron_record(ATTACHED.encode(), "calloway-w")

    monkeypatch.setattr(readers, "read_enron", fake_enron)
    out = tmp_path / "out"
    assert build_dataset.main(["--out", str(out), "--sources", "enron", "--personal"]) == 0
    rows = [json.loads(line) for name in ("train.jsonl", "validation.jsonl")
            for line in open(out / name, encoding="utf-8")]
    mail = [r for r in rows if r["kind"] != "attachment"][0]
    memo = [r for r in rows if r["kind"] == "attachment"][0]
    assert "Idris, I'm off sick today" in mail["response"]          # sensitive topics and names are kept
    assert mail["response"].rstrip().endswith("Wren")
    assert "123-45-6789" not in json.dumps(rows) and "[SSN]" in mail["response"]
    assert "blue42" not in json.dumps(rows) and "password: [password]" in mail["response"]
    assert "The message you are answering:" in mail["instruction"]
    assert "Can we do the review on Thursday?" in mail["instruction"]
    assert "kitchen will be closed" in memo["response"] and "memo.txt" in memo["instruction"]
    folders = list((out / "messages" / "enron").iterdir())
    assert len(folders) == 1
    assert sorted(p.name for p in folders[0].iterdir()) == ["memo.txt", "message.txt"]
    report = (out / "build-report.txt").read_text(encoding="utf-8")
    assert "attachments saved: 1" in report and "Privacy setting: owner" in report


# ----------------------------------------------------------------- style labels

import styles  # noqa: E402


def test_every_example_has_a_style_and_register_and_per_style_files(tmp_path, monkeypatch):
    def fake_enron(fetcher, say=print, **_):
        yield readers.enron_record(MAIL.encode(), "calloway-w")

    def fake_sms(fetcher, say=print, **_):
        yield {"type": "sms", "text": "ok see you at 7, bring the snacks", "group": "sms"}

    monkeypatch.setattr(readers, "read_enron", fake_enron)
    monkeypatch.setattr(readers_more, "read_sms", fake_sms)
    out = tmp_path / "out"
    assert build_dataset.main(["--out", str(out), "--sources", "enron,sms", "--personal"]) == 0
    rows = [json.loads(line) for name in ("train.jsonl", "validation.jsonl")
            for line in open(out / name, encoding="utf-8")]
    assert {r["style"] for r in rows} == {"email_business", "text_message"}
    assert all(r["register"] in styles.REGISTERS and r["source"] for r in rows)
    assert (out / "text_message" / "train.jsonl").exists() or (out / "text_message" / "validation.jsonl").exists()
    per_style = sum(1 for style in ("email_business", "text_message") for name in ("train.jsonl", "validation.jsonl")
                    for _ in open(out / style / name, encoding="utf-8"))
    assert per_style == len(rows)
    assert "text_message" in (out / "STYLES.txt").read_text(encoding="utf-8")


def test_only_chosen_styles_are_built(tmp_path, monkeypatch):
    monkeypatch.setattr(readers_more, "read_sms", lambda f, say=print, **_: iter(
        [{"type": "sms", "text": "ok see you at 7, bring the snacks", "group": "sms"}]))
    out = tmp_path / "out"
    build_dataset.main(["--out", str(out), "--sources", "sms", "--styles", "email_business"])
    assert (out / "train.jsonl").read_text(encoding="utf-8") == ""


def test_style_labels_come_from_a_fixed_list():
    assert styles.label({"kind": "press release"}, "edgar") == ("press_release", "formal")
    assert styles.label({"instruction": "Write an email to my neighbor about the noise"}, "oasst2")[0] == \
        "email_personal"
    assert styles.label({}, "scotus") == ("transcript_court", "formal")
    assert styles.label({}, "irc") == ("chat", "casual")
    assert styles.label({}, "gutenberg", {"style_label": "poetry"})[0] == "poetry"
