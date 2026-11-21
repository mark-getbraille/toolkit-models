"""Tests of the business and modern American readers (kit/readers_business.py). All data here is made up; no
network is used."""

import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import readers_business as rb  # noqa: E402


class FakeFetcher:
    """Answers get(url) from a dict of {part of the address: bytes}."""

    def __init__(self, answers):
        self.answers = answers
        self.extra_headers = {}
        self.asked = []

    def get(self, url):
        self.asked.append((url, dict(self.extra_headers)))
        for key, value in self.answers.items():
            if key in url:
                return value
        raise OSError("not found: " + url)


def test_edgar_needs_a_declared_user_agent(monkeypatch):
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    said = []
    assert list(rb.read_edgar(FakeFetcher({}), say=said.append)) == []
    assert "SEC_USER_AGENT" in said[0]


def test_edgar_reads_press_releases_with_the_declared_agent(monkeypatch):
    monkeypatch.setenv("SEC_USER_AGENT", "Test Person test@example.com")
    monkeypatch.setattr(rb, "EDGAR_KINDS", [('"announced today"', "8-K", "press release")])
    search = json.dumps({"hits": {"hits": [
        {"_id": "0000123456-26-000001:ex99-1.htm", "_source": {"ciks": ["0000123456"],
                                                               "display_names": ["Acme Widgets Inc  (CIK 0000123456)"]}},
        {"_id": "0000123456-26-000001:form8-k.htm", "_source": {"ciks": ["0000123456"]}}]}}).encode()
    release = ("<html><body><p>Acme Widgets Reports Record Third Quarter Sales</p><p>" + "Acme announced today "
               "that sales grew strongly in every region. " * 12 + "</p></body></html>").encode()
    f = FakeFetcher({"search-index": search, "ex99-1.htm": release})
    records = list(rb.read_edgar(f, say=lambda t: None, per_kind=1))
    assert len(records) == 1
    assert records[0]["kind"] == "press release"
    assert "Acme Widgets Inc" in records[0]["instruction"]
    assert "Record Third Quarter Sales" in records[0]["instruction"]
    assert all(h.get("User-Agent") == "Test Person test@example.com" for _, h in f.asked)
    assert "edgar/data/123456/000012345626000001/ex99-1.htm" in f.asked[1][0]
    assert f.extra_headers == {}


def test_openstax_sections_are_read_as_plain_text():
    xml = ("<document><title>Effective Business Communication</title><content><para>Good messages are clear."
           "</para><list><item>Know your audience.</item></list><figure><caption>skip</caption></figure>"
           "</content></document>")
    title, text = rb.cnxml_text(xml)
    assert title == "Effective Business Communication"
    assert text == "Good messages are clear.\nKnow your audience."
    assert rb.BUSINESS_TOPICS.search(title)


def test_oanc_conversations_and_letters():
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as z:
        z.writestr("OANC/data/spoken/telephone/switchboard/1/sw1-a.txt",
                   "\n hi what did you do this weekend\n\n not much um we went camping\n\n oh nice where\n\n "
                   "up at the lake it was cold\n")
        z.writestr("OANC/data/written_1/letters/icic/1.txt", "Dear Friends of Literacy,\nPlease give today.\n")
    records = list(rb.oanc_records(data.getvalue()))
    chat = [r for r in records if r["type"] == "chat"][0]
    assert chat["turns"][:2] == [("Speaker A", "hi what did you do this weekend"),
                                 ("Speaker B", "not much um we went camping")]
    assert chat["raw_name"] == "sw1-a.txt"
    letter = [r for r in records if r["type"] == "text"][0]
    assert letter["form"] == "letter" and letter["response"].startswith("Dear Friends of Literacy")


def test_feeds_give_full_posts():
    xml = ("<rss><channel><item><title>Why plain words win</title><content:encoded><![CDATA[<p>First.</p>"
           "<p>Second &amp; last.</p>]]></content:encoded></item><item><title>No body</title></item></channel></rss>")
    assert rb.feed_items(xml) == [("Why plain words win", "First.\nSecond & last.")]


def test_fineweb_keeps_only_conversational_pages():
    rows = {"rows": [{"row": {"url": "https://example.com/forum/thread-12", "text": "word " * 100, "language": "en"}},
                     {"row": {"url": "https://example.com/products/page", "text": "word " * 100, "language": "en"}},
                     {"row": {"url": "https://example.com/reviews/1", "text": "too short", "language": "en"}}]}
    f = FakeFetcher({"datasets-server": json.dumps(rows).encode()})
    records = list(rb.read_fineweb(f, say=lambda t: None, pages=1))
    assert [r["kind"] for r in records] == ["forum post"]


def test_nsf_abstracts_become_grant_summaries():
    award = {"response": {"award": [{"title": "Community Water Monitoring", "abstractText": "This project " * 90}]}}
    f = FakeFetcher({"api.nsf.gov": json.dumps(award).encode()})
    rec = next(rb.read_nsf(f, say=lambda t: None, pages=1))
    assert "Community Water Monitoring" in rec["instruction"] and rec["form"] == "project summary"
