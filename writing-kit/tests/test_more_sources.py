"""Tests of the extra sources (kit/readers_more.py), the attachment reader (kit/attachments.py) and the identifier
masking used under the owner's rule (kit/scrub.py mask_identifiers). Every message, log and letter here is made up;
no network is used."""

import gzip
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import attachments  # noqa: E402
import build_dataset  # noqa: E402
import instructions  # noqa: E402
import readers_more  # noqa: E402
import scrub  # noqa: E402
import writing_sources  # noqa: E402

SOURCE = writing_sources.by_key()["irc"]


# ----------------------------------------------------------------- the one exception: identity-theft identifiers

def test_only_identity_theft_identifiers_are_masked():
    text = ("Hi Quentin, my SSN is 123-45-6789, card 4111 1111 1111 1111, account number is 99887766, routing # "
            "021000021, password: tulip42!, login: qashdown. Call me at 713-555-0142 at 12 Elm Street.")
    out = scrub.mask_identifiers(text)
    for secret in ["123-45-6789", "4111", "99887766", "021000021", "tulip42", "qashdown"]:
        assert secret not in out, secret
    for kept in ["Hi Quentin", "713-555-0142", "12 Elm Street", "password: [password]", "login: [login]",
                 "account number is [account number]"]:
        assert kept in out, kept


def test_ordinary_words_about_accounts_and_passwords_stay():
    for text in ["I forgot my password again.", "The account is fine.", "Deal 4410937 is booked.",
                 "Password:\n\nHi everyone, here is the new process.", "Send your password by today."]:
        assert scrub.mask_identifiers(text) == text


def test_threads_are_split_without_losing_anything():
    body = "Sure, Thursday works.\n\nOn Mon, Pell wrote:\n> Can we meet Thursday?\n> Thanks"
    own, quoted = scrub.split_thread(body)
    assert own == "Sure, Thursday works."
    assert "Can we meet Thursday?" in quoted and "Pell wrote" in quoted


# ----------------------------------------------------------------- attachments

def test_text_documents_are_read_from_attachments():
    assert attachments.extract_text("memo.txt", b"Staff meeting moved to Friday.") == "Staff meeting moved to Friday."
    assert attachments.extract_text("a.html", b"<p>Hello <b>all</b></p><script>x()</script>").split() == \
        ["Hello", "all"]
    docx = io.BytesIO()
    with zipfile.ZipFile(docx, "w") as z:
        z.writestr("word/document.xml", "<w:document><w:p><w:r><w:t>Dear team,</w:t></w:r></w:p>"
                                        "<w:p><w:r><w:t>Lunch is on me.</w:t></w:r></w:p></w:document>")
    assert attachments.extract_text("letter.docx", docx.getvalue()) == "Dear team,\nLunch is on me."
    assert attachments.extract_text("photo.jpg", b"\xff\xd8\xff") == ""


def test_saved_attachment_names_are_safe(tmp_path):
    saved = attachments.save_message(str(tmp_path / "m"), "text", [("../../evil.txt", b"x"), ("evil.txt", b"y")])
    assert saved == ["evil.txt", "evil (2).txt"]
    assert sorted(os.listdir(tmp_path / "m")) == ["evil (2).txt", "evil.txt", "message.txt"]


# ----------------------------------------------------------------- mail, news and list readers

def test_mbox_and_news_articles_are_read_with_attachments():
    mbox = (b"From a@example.com Mon Jan  1 00:00:00 2001\nSubject: Re: Packing for the coast\n"
            b"From: Tam <tam@example.com>\nNewsgroups: alt.vacation\n\nBring a jumper, it gets cold at night.\n"
            b">From the old FAQ\n\nFrom b@example.com Mon Jan  1 00:00:00 2001\nSubject: Ferry times\n\n"
            b"Does anyone know when the last ferry leaves?\n")
    raws = list(readers_more.mbox_messages(io.BytesIO(mbox)))
    assert len(raws) == 2
    rec = readers_more.mail_record(raws[0], "alt.vacation", "a newsgroup")
    assert rec["is_reply"] and "Bring a jumper" in rec["body"] and "From the old FAQ" in rec["body"]


def test_uuencoded_binaries_are_left_out_of_the_text():
    raw = b"Subject: pic\n\nHere it is.\nbegin 644 cat.jpg\nM9F]O\n`\nend\nEnjoy.\n"
    _, body, _ = readers_more.parse_mail(raw)
    assert "M9F]O" not in body and "Enjoy." in body


def test_debian_pages_are_read():
    page = ("<title>Re: Wifi drops after suspend</title><!--X-Body-of-Message--><pre>Try reloading the module."
            "</pre><blockquote>It drops every time.</blockquote><a href=\"msg00012/0001.bin\">att</a>"
            "<!--X-Body-of-Message-End-->")
    rec = readers_more.debian_message(page)
    assert rec["is_reply"] and "Try reloading the module." in rec["body"] and "> It drops" in rec["body"]
    assert rec["attachment_links"] == ["msg00012/0001.bin"]


# ----------------------------------------------------------------- chats

def test_irc_logs_become_reply_pairs():
    log = ("[10:00] <kestrel> my wifi stops after suspend, any idea?\n[10:01]  * owl waves\n"
           "[10:02] <owl> kestrel: try sudo modprobe -r iwlwifi then modprobe it again\n"
           "[10:03] <kestrel> owl: that worked, thanks a lot!\n")
    turns = readers_more.irc_turns(log)
    assert [t[0] for t in turns] == ["kestrel", "owl", "kestrel"]
    record = {"type": "chat", "turns": turns, "setting": "the Ubuntu IRC help channel #ubuntu", "style": "irc"}
    rows = [r for r, _ in build_dataset.examples_from_chat(record, SOURCE)]
    assert rows[0]["response"].startswith("owl: that worked") or rows[0]["response"].startswith("kestrel: try")
    assert "kestrel: my wifi stops after suspend" in rows[0]["instruction"]
    assert rows[0]["form"] == "chat message"


def test_wikipedia_talk_comments_are_split_by_signature():
    text = ("== Picture ==\nShould we add a map here? [[User:Pebble|Pebble]] 10:00, 1 May 2020 (UTC)\n"
            ":Yes, a map of the [[river|rivers]] would help. [[User:Marl|Marl]] ([[User talk:Marl|talk]]) "
            "11:00, 1 May 2020 (UTC)\n")
    comments = readers_more.talk_comments(text)
    assert comments == [("Pebble", "Should we add a map here?"), ("Marl", "Yes, a map of the rivers would help.")]


def test_sms_collection_keeps_only_ordinary_texts():
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as z:
        z.writestr("SMSSpamCollection", "ham\tOk see you at 7 then\nspam\tWIN a prize now call 0900\n"
                                        "ham\tHi\n")
    records = list(readers_more.sms_records(data.getvalue()))
    assert [r["text"] for r in records] == ["Ok see you at 7 then"]
    row = build_dataset.examples_from_record(records[0], writing_sources.by_key()["sms"])[0][0]
    assert row["form"] == "text message" and "text" in row["instruction"].lower()


def test_letters_are_found_in_a_book_of_letters():
    book = ("*** START OF THE PROJECT GUTENBERG EBOOK LETTERS ***\nLETTER I.\n\nMy dear Lucy,\n\n" + "I write to "
            "tell you that the garden is in flower and the weather fine. " * 5 + "\n\nYour loving friend,\nAnne\n\n"
            "LETTER II.\n\nDear Sir,\n\n" + "Thank you for the books, which arrived safely on Tuesday. " * 4 +
            "\n\nYours truly,\nJ. Hale\n*** END OF THE PROJECT GUTENBERG EBOOK LETTERS ***\nLicence text")
    letters = list(readers_more.letters_in(readers_more.gutenberg_body(book)))
    assert len(letters) == 2
    assert letters[0].startswith("My dear Lucy,") and "Licence" not in letters[1]
    instruction, details = instructions.make_letter_instruction(letters[1], "Letters of Nobody")
    assert details["form"] == "letter" and "before 1930" in instruction


def test_unchanged_transcripts_stay_unchanged():
    record = {"type": "text", "instruction": "Here is a transcript.", "response": "LYNNE: password: abc123!",
              "unchanged": True, "kind": "transcript", "form": "transcript", "tone": "casual", "audience": ""}
    row = build_dataset.examples_from_record(record, writing_sources.by_key()["sbcsae"])[0][0]
    assert row["response"] == "LYNNE: password: abc123!"


def test_regulations_needs_a_key(monkeypatch):
    monkeypatch.delenv("REGULATIONS_GOV_API_KEY", raising=False)
    said = []
    assert list(readers_more.read_regulations(None, say=said.append)) == []
    assert "API key" in said[0]


def test_comment_instructions():
    instruction, details = instructions.make_comment_instruction("I oppose this rule, it is unfair to small farms.",
                                                                 "USDA", "Organic labeling")
    assert "USDA" in instruction and "Organic labeling" in instruction and details["kind"] == "complaint"


# ----------------------------------------------------------------- public meetings (kit/readers_meetings.py)

import readers_meetings  # noqa: E402


def test_supreme_court_transcripts_become_turns():
    text = ("1 P R O C E E D I N G S\n2 CHIEF JUSTICE ROBERTS: We'll hear argument\n3 first this morning in Case "
            "24-1, Doe versus Roe.\nHeritage Reporting Corporation\n4 MS. QUILL: Mr. Chief Justice, and may it\n"
            "5 please the Court: the statute is plain.\n6 JUSTICE KAGAN: Well, is it?\n7 (Whereupon, at 11:02 a.m., "
            "the case was submitted.)\n")
    turns = readers_meetings.scotus_turns(text)
    assert turns == [("CHIEF JUSTICE ROBERTS", "We'll hear argument first this morning in Case 24-1, Doe versus Roe."),
                     ("MS. QUILL", "Mr. Chief Justice, and may it please the Court: the statute is plain."),
                     ("JUSTICE KAGAN", "Well, is it?")]


def test_hearing_transcripts_become_turns():
    text = ("    The CHAIRMAN. The committee will come to order. Thank\nyou all for coming.\n"
            "    [Applause.]\n    Ms. Quill. Thank you, Mr. Chairman. I'm glad to be\nhere.\n")
    assert readers_meetings.hearing_turns(text) == [("The CHAIRMAN", "The committee will come to order. Thank you "
                                                     "all for coming."), ("Ms. Quill", "Thank you, Mr. Chairman. I'm "
                                                     "glad to be here.")]


def test_hansard_interventions_become_turns():
    xml = ("<Intervention><PersonSpeaking><Affiliation>Mr. Tam Quill (Somewhere, Lib.)</Affiliation>"
           "</PersonSpeaking><Content><ParaText>Mr. Speaker, the colour of the centre is fine.</ParaText>"
           "</Content></Intervention><Intervention><PersonSpeaking><Affiliation>The Speaker</Affiliation>"
           "</PersonSpeaking><Content><ParaText>Order, please.</ParaText></Content></Intervention>")
    assert readers_meetings.hansard_turns(xml) == [("Mr. Tam Quill (Somewhere, Lib.)", "Mr. Speaker, the colour "
                                                    "of the centre is fine."), ("The Speaker", "Order, please.")]
    assert "Canadian English" in readers_meetings.CANADA_NOTE


def test_speech_records_save_the_whole_transcript(tmp_path, monkeypatch):
    def fake(fetcher, say=print, **_):
        yield {"type": "chat", "turns": [("A", "Good morning everyone, shall we begin?"),
                                         ("B", "Yes, thank you, let's get started then.")],
               "setting": "a US Congress committee hearing", "group": "2023", "style": "speech",
               "raw": "whole transcript text", "raw_name": "CHRG-1.txt"}
    monkeypatch.setattr(readers_meetings, "read_hearings", fake)
    assert build_dataset.main(["--out", str(tmp_path), "--sources", "hearings"]) == 0
    assert (tmp_path / "transcripts" / "hearings" / "CHRG-1.txt").read_text(encoding="utf-8") == \
        "whole transcript text"
