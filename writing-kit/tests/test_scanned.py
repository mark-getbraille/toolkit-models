"""Tests of the scanned-release reading (kit/ocr.py, kit/readers_scanned.py) and --scanned-folder in
kit/build_dataset.py. All text is made up (tests/scanned_fixture.py). The OCR engine is replaced by a stand-in in
most tests; the tests marked "real OCR" run RapidOCR on the generated scanned PDF and are skipped when it is not
installed. No network is used."""

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
sys.path.insert(0, HERE)
import build_dataset  # noqa: E402
import ocr  # noqa: E402
import readers_scanned as rs  # noqa: E402
import scrub  # noqa: E402
import scanned_fixture  # noqa: E402


def page(n, text, confidence=0.95, kept=True, reason=""):
    return ocr.Page(number=n, text=text, confidence=confidence, kept=kept, reason=reason, png=b"",
                    lines=[(line, confidence, [(0, i * 40), (500, i * 40), (500, i * 40 + 30), (0, i * 40 + 30)])
                           for i, line in enumerate(text.split("\n"))])


def fake_pages():
    """The fixture's pages as the OCR would read them, plus one blurred page with a low score."""
    out = [page(1, "Release 7", 0.0, False, "almost no text (2 words)")]
    out.append(page(2, "\n".join(scanned_fixture.PAGES[1])))
    out.append(page(3, "\n".join(scanned_fixture.PAGES[2])))
    out.append(page(4, "blurred words here and there on a page that could not be read well", 0.41, False,
                    "confidence 0.41 is under 0.80"))
    out.append(page(5, "\n".join(scanned_fixture.PAGES[3])))
    return out


@pytest.fixture
def fake_ocr(monkeypatch):
    monkeypatch.setattr(ocr, "read_pdf", lambda data, **kw: iter(fake_pages()))
    monkeypatch.setattr(ocr, "available", lambda: (True, ""))
    monkeypatch.setattr(ocr, "page_count", lambda data: 5)


def test_header_words_misread_by_ocr_are_fixed():
    assert ocr.fix_header_line("Frorn; Lee, Jo") == "From: Lee, Jo"
    assert ocr.fix_header_line("Sen t. Monday, May 4") == "Sent: Monday, May 4"
    assert ocr.fix_header_line("Subiect: Re: water") == "Subject: Re: water"
    assert ocr.fix_header_line("T0: Bo Ray") == "To: Bo Ray"
    assert ocr.fix_header_line("Attachrnent: plan.docx") == "Attachment: plan.docx"
    assert ocr.fix_header_line("To. the store we went") == "To. the store we went"
    assert ocr.fix_header_line("Date, place and time") == "Date, place and time"


def test_lines_are_put_in_reading_order_with_paragraphs():
    box = lambda x, y: [(x, y), (x + 100, y), (x + 100, y + 30), (x, y + 30)]
    lines = [("world", 0.9, box(200, 0)), ("Hello", 0.9, box(0, 2)), ("next", 0.9, box(0, 40)),
             ("new paragraph", 0.9, box(0, 140))]
    assert ocr.lines_to_text(lines) == "Hello world\nnext\n\nnew paragraph"


def test_split_messages_and_stamps():
    text = ("U.S. Department of State Case No. F-2016-00001 Doc No. C00000001\nFrom: Jo\nSent: Monday\nTo: Bo\n"
            "Subject: Hi\n\nBo, see you at noon.\nB6\nFrom: Bo\nDate: Sunday\nSubject: Lunch\n\nLunch tomorrow?\n")
    parts = rs.split_messages(text)
    assert [rs.header_value(h, "Subject") for h, _ in parts] == ["Hi", "Lunch"]
    assert rs.clean_text(parts[0][1]) == "Bo, see you at noon."
    assert rs.split_messages("From: the desk of Jo\nHello there") == []


def test_licence_rules():
    assert rs.is_federal_domain("state.gov") and rs.is_federal_domain("epa.gov") and rs.is_federal_domain("va.gov")
    assert not rs.is_federal_domain("michigan.gov") and not rs.is_federal_domain("flintcity.gov")
    assert rs.sender_outside_government("From: Bo <bo@example.com>\nSent: x")
    assert not rs.sender_outside_government("From: Lee, Jo <leej@state.gov>")
    assert not rs.sender_outside_government("From: Lee, Jo\nSent: x")           # address removed: release decides
    assert rs.government_reason("B:/Original sources/public domain/a.pdf", "")
    assert rs.government_reason("x.pdf", "Redacted (b)(6) here")
    assert rs.government_reason("palin/061206.pdf", "From: Gov. Sarah Palin\nSent: x") == ""


def test_records_from_a_scanned_pdf(fake_ocr):
    log = []
    records = list(rs.records_from_pdf(b"pdf", "release.pdf", say=lambda t: None, page_log=log,
                                       mask=scrub.mask_identifiers))
    assert [r["subject"] for r in records] == ["Re: water samples", "water samples"]
    reply, earlier = records
    # the reply: its own words, the attachment pages saved as pictures and OCR text, the attachment's text used
    assert reply["body"].startswith("Bo, thanks for the quick turnaround")
    assert "Sampling plan" not in reply["body"].split("From: Bo Ray")[0]
    names = [a[0] for a in reply["attachments"]]
    assert "page 0002 OCR.txt" in names and "page 0003 OCR.txt" in names
    assert reply["text_from"] == ["Sampling plan.docx (OCR text).txt"]
    ocr_text = dict((a[0], a[1]) for a in reply["attachments"])["page 0002 OCR.txt"].decode()
    assert "4111 1111" not in ocr_text and "[card number]" in ocr_text
    # the earlier message is joined below the reply, so the example shows what it answers
    assert "From: Bo Ray" in reply["body"] and "first samples are back" in reply["body"]
    # licences: a State Department release; the outside sender's own message is personal use
    assert reply["licence_open"] is True and earlier["licence_open"] is False
    assert log == [("release.pdf", 1, "almost no text (2 words)"), ("release.pdf", 4, "confidence 0.41 is under 0.80")]


def test_build_with_scanned_folder(fake_ocr, tmp_path):
    folder = tmp_path / "Original sources"
    folder.mkdir()
    (folder / "release.pdf").write_bytes(b"%PDF-1.4 made up")
    out = tmp_path / "out"
    assert build_dataset.main(["--out", str(out), "--scanned-folder", str(folder)]) == 0
    rows = [json.loads(x) for name in ("train.jsonl", "validation.jsonl")
            for x in open(out / name, encoding="utf-8")]
    by_kind = {r["kind"]: r for r in rows}
    assert {r["source"] for r in rows} == {"scanned_folder"}
    assert "attachment" in by_kind and "twelve homes" in by_kind["attachment"]["response"]
    reply = next(r for r in rows if "quick turnaround" in r["response"])
    assert "The message you are answering" in reply["instruction"] and "[card number]" in reply["response"]
    assert reply["licence_class"] == "open" and reply["style"] == "email_business"
    earlier = next(r for r in rows if r["response"].startswith("Jo, the first samples"))
    assert earlier["licence_class"] == "personal use only"
    log = (out / "scanned-pages-left-out.txt").read_text(encoding="utf-8")
    assert "release.pdf, page 4: confidence 0.41" in log
    saved = [os.path.join(d, f) for d, _, files in os.walk(out / "messages" / "scanned_folder") for f in files]
    assert any(f.endswith("page 0003 OCR.txt") for f in saved) and any(f.endswith("message.txt") for f in saved)
    assert "Licence by message" in (out / "ATTRIBUTION.txt").read_text(encoding="utf-8")


def test_without_the_ocr_reader_the_source_is_skipped(monkeypatch, tmp_path):
    monkeypatch.setattr(ocr, "available", lambda: (False, "the OCR reader is not installed"))
    (tmp_path / "in").mkdir()
    assert build_dataset.main(["--out", str(tmp_path / "out"), "--scanned-folder", str(tmp_path / "in")]) == 0
    report = (tmp_path / "out" / "build-report.txt").read_text(encoding="utf-8")
    assert "skipped: the OCR reader is not installed" in report


def test_ia_items_are_checked(monkeypatch):
    meta = {"metadata": {"collection": ["state-department"], "licenseurl": ""},
            "files": [{"name": "a.pdf", "source": "original", "size": "1000"}]}

    class F:
        asked = []

        def get(self, url):
            self.asked.append(url)
            return json.dumps(meta).encode()
    monkeypatch.setattr(ocr, "available", lambda: (True, ""))
    monkeypatch.setattr(rs, "IA_FEDERAL", [("item1", "a release")])
    said = []
    assert list(rs.read_ia_federal(F(), say=said.append, page_log=[])) == []
    assert "not marked public domain" in said[0] and not any("download" in u for u in F.asked)
    assert rs.ia_pdfs({"files": [{"name": "b.pdf", "source": "original", "size": "900"},
                                 {"name": "deletes/c.pdf", "source": "original", "size": "1"},
                                 {"name": "d_text.pdf", "source": "derivative", "size": "1"},
                                 {"name": "big.pdf", "source": "original", "size": str(200 * 2 ** 20)}]}, 80) \
        == [("b.pdf", 900)]


def test_govinfo_hint():
    assert rs.exhibit_hint("the emails we received follow:\n\n[GRAPHICS NOT AVAILABLE IN TIFF FORMAT]")
    assert not rs.exhibit_hint("[GRAPHIC(S) NOT AVAILABLE IN TIFF FORMAT] a chart of costs")


real_ocr = pytest.mark.skipif(not ocr.available()[0], reason="RapidOCR is not installed")


@real_ocr
def test_real_ocr_reads_the_generated_scanned_pdf():
    data = scanned_fixture.make_pdf()
    log = []
    records = list(rs.records_from_pdf(data, "fixture.pdf", say=lambda t: None, page_log=log,
                                       mask=scrub.mask_identifiers))
    assert [r["subject"] for r in records] == ["Re: water samples", "water samples"]
    assert "Can you send the results" in records[0]["body"]
    assert records[0]["licence_open"] and not records[1]["licence_open"]
    assert records[0]["confidence"] >= ocr.MIN_PAGE_CONFIDENCE
    assert log and log[0][:2] == ("fixture.pdf", 1)
    assert any(a[0] == "page 0002.png" and a[1].startswith(b"\x89PNG") for a in records[0]["attachments"])
