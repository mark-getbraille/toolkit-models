"""Tests of the sources added in kit/sources_more.py. Every page, feed, letter, essay, review, message, issue and
notice here is made up; no network is used (a fake fetcher hands back the made-up bytes)."""

import csv
import gzip
import io
import json
import os
import sys
import tarfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kit"))
import build_dataset  # noqa: E402
import fetch  # noqa: E402
import sources_more as sm  # noqa: E402
import styles  # noqa: E402
import writing_sources  # noqa: E402


class FakeFetcher:
    """Hands back made-up bytes for each address (a dict); an unknown address is a 404."""

    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def get(self, url):
        self.asked.append(url)
        for key, value in self.pages.items():
            if url == key or (key.endswith("*") and url.startswith(key[:-1])):
                return value if isinstance(value, bytes) else value.encode("utf-8")
        import urllib.error
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)

    def open_stream(self, url):
        return io.BytesIO(self.get(url))


def zip_of(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            z.writestr(name, text)
    return buf.getvalue()


def csv_text(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


SENTENCE = "The volunteers planted forty new trees along the river trail this spring and asked neighbours to help. "


# ----------------------------------------------------------------- the registry and the hooks

def test_every_new_source_is_registered_with_a_reader_licence_and_known_styles():
    keys = {s.key for s in writing_sources.SOURCES}
    for key in ("govblogs", "obama_social", "loc_letters", "persuade", "bawe", "imdb", "yelp", "python_lists",
                "gharchive", "sam", "fedreg_rfi", "fed_speeches", "crec", "wikivoyage", "wikiquote", "recipes_nhlbi",
                "recipes_nhs"):
        assert key in keys, key
    for source in writing_sources.SOURCES:
        assert source.licence_class in writing_sources.CLASSES
        assert any(hasattr(m, source.reader) for m in build_dataset.READER_MODULES), source.key
    assert len(keys) == len(writing_sources.SOURCES)                  # no key twice
    for style in sm.STYLES:
        assert style in styles.STYLES
    assert styles.label({"kind": "x"}, "sam", {"style_label": "procurement"}) == ("procurement", "formal")
    assert any("Founders Online" in name for name, _ in writing_sources.NOT_USED)


def test_local_file_option_reaches_the_reader(tmp_path, monkeypatch):
    path = tmp_path / "persuade.csv"
    path.write_text(csv_text([{"full_text": SENTENCE * 10, "prompt_name": "Car-free cities", "grade_level": "8",
                               "assignment": "Write a letter to your senator about car-free days.",
                               "holistic_essay_score": "4"}]), encoding="utf-8")
    seen = {}

    def fake_build(source, fetcher, per_source, say, seen_set, options, *args, **kw):
        seen[source.key] = options.get("local_file")
        return [], build_dataset.Counter()
    monkeypatch.setattr(build_dataset, "build_source", fake_build)
    monkeypatch.setattr(build_dataset, "write_outputs", lambda *a, **k: ([], []))
    build_dataset.main(["--out", str(tmp_path / "out"), "--sources", "persuade",
                        "--local-file", f"persuade={path}"])
    assert seen["persuade"] == str(path)


# ----------------------------------------------------------------- agency pages and feeds

FEED = """<rss><channel>
<item><title>Ten tips for a safe hike</title><link>https://www.example.gov/hike</link>
<content:encoded><![CDATA[<p>""" + SENTENCE * 15 + """</p>]]></content:encoded></item>
<item><title>Short note</title><link>https://www.example.gov/note</link><description>Just a line.</description></item>
</channel></rss>"""


def test_feed_entries_and_article_text():
    entries = sm.feed_entries(FEED)
    assert entries[0][0] == "Ten tips for a safe hike" and entries[0][1] == "https://www.example.gov/hike"
    assert "forty new trees" in entries[0][2] and entries[1][2] == ""
    page = ("<html><head><title>Tree day | Example Agency</title></head><body><nav><p>Home menu</p></nav>"
            "<main><h1>Tree day</h1><p>" + SENTENCE * 6 + "</p><p>Thank you, everyone.</p></main>"
            "<footer><p>Contact us</p></footer></body></html>")
    title, text = sm.article_text(page)
    assert title == "Tree day"
    assert "forty new trees" in text and "Thank you, everyone." in text
    assert "Home menu" not in text and "Contact us" not in text


def test_govblogs_reads_feeds_fda_pages_and_sitemaps():
    article = "<html><body><article><h1>A park story</h1><p>" + SENTENCE * 12 + "</p></article></body></html>"
    pages = {
        "https://www.nasa.gov/feed/": FEED, "https://news.va.gov/feed/": FEED,
        sm.FDA_FEED: FEED.replace("https://www.example.gov/hike", "http://www.fda.gov/consumers/a"),
        "https://www.fda.gov/consumers/a": article,
        sm.NPS_SITEMAP: "<urlset><url><loc>https://www.nps.gov/articles/000/a-park-story.htm</loc></url></urlset>",
        "https://www.nps.gov/articles/000/a-park-story.htm": article,
        sm.ENERGY_SITEMAP: "<urlset><url><loc>https://www.energy.gov/articles/saving-energy</loc></url></urlset>",
        "https://www.energy.gov/articles/saving-energy": article,
    }
    records = list(sm.read_govblogs(FakeFetcher(pages), say=lambda *_: None, feed_pages=2))
    groups = {r["group"]: r for r in records}
    assert set(groups) == {"NASA", "VA VAntage Point", "FDA", "NPS", "Energy.gov"}
    assert groups["NPS"]["style_label"] == "travel" and groups["FDA"]["style_label"] == "plain_language_gov"
    assert 'titled "Ten tips for a safe hike"' in groups["NASA"]["instruction"]


# ----------------------------------------------------------------- Obama White House tweets

def test_tweets_leave_out_retweets_and_hide_links():
    rows = [{"tweet_id": "1", "retweeted_status_id": "", "text": "Today we honor our veterans and their families. "
             "Thank you for your service. https://t.co/abc123"},
            {"tweet_id": "2", "retweeted_status_id": "9", "text": "RT @someone: a retweet of somebody else"},
            {"tweet_id": "3", "retweeted_status_id": "", "text": "Too short"}]
    data = zip_of({"tweets.csv": csv_text(rows)})
    assert sm.tweets_from_zip(data) == ["Today we honor our veterans and their families. Thank you for your "
                                        "service. [link]"]
    assert "veterans" in sm.tweet_topic("Today we honor our veterans. #VeteransDay")
    pages = {sm.OBAMA_FILES.format(name=n): data for n, _ in sm.OBAMA_ACCOUNTS}
    records = list(sm.read_obama_social(FakeFetcher(pages), say=lambda *_: None))
    assert len(records) == 3 and records[0]["style_label"] == "social_post"
    assert "280 characters" in records[0]["instruction"]


# ----------------------------------------------------------------- Library of Congress letters and diaries

def loc_rows():
    letter = ("My Dear Friend,\n\nI write to tell you that the meet-\ning at the hall was a great\nsuccess and that "
              "we raised more than we hoped for the school. " + SENTENCE * 3)
    diary = "Monday, March 3. 1862.\nRained all day and we stayed in camp reading letters from home. " + SENTENCE * 3
    return [
        {"Item": "Papers: Correspondence; 1862", "ItemId": "a1", "Asset": "a1-2", "Project": "Letters",
         "Transcription": "And so I remain your friend, Mary. " + SENTENCE * 2},
        {"Item": "Papers: Correspondence; 1862", "ItemId": "a1", "Asset": "a1-1", "Project": "Letters",
         "Transcription": "Papers Box 3 Folder 9\n\n" + letter},
        {"Item": "Papers: Diaries; 1862", "ItemId": "d1", "Asset": "d1-1", "Project": "Diaries", "Transcription": diary},
        {"Item": "Papers: Diaries; 1862", "ItemId": "d1", "Asset": "d1-2", "Project": "Diaries",
         "Transcription": "CALENDAR 1862 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 "
                          "29 30 31 32 33 34 35 36 37 38 39 40 41 42"},
        {"Item": "Papers: Speeches and Writings; 1870", "ItemId": "s1", "Asset": "s1-1", "Project": "Speeches",
         "Transcription": "Ladies and gentlemen, " + SENTENCE * 4},
    ]


def test_loc_letters_join_pages_in_order_and_skip_labels_lists_and_speeches():
    records = list(sm.loc_records(loc_rows(), "Test Family Papers"))
    letters = [r for r in records if r["style_label"] == "letter_personal"]
    diaries = [r for r in records if r["style_label"] == "diary"]
    assert len(letters) == 1 and len(diaries) == 1
    text = letters[0]["response"]
    assert text.startswith("My Dear Friend,") and "Box 3" not in text
    assert "meeting at the hall was a great success" in text                # hyphen and line breaks joined
    assert text.index("My Dear Friend") < text.index("your friend, Mary")   # pages in order
    assert "CALENDAR" not in diaries[0]["response"]
    assert "Ladies and gentlemen" not in " ".join(r["response"] for r in records)


def test_loc_zip_url_prefers_the_small_csv_zip():
    item = {"resources": [{"files": [[{"url": "https://tile.loc.gov/x/1_json.zip", "size": 10},
                                      {"url": "https://tile.loc.gov/x/1.zip", "size": 500},
                                      {"url": "https://tile.loc.gov/x/2.zip", "size": 300},
                                      {"url": "https://tile.loc.gov/x/huge.zip", "size": 10 ** 10}]]}]}
    assert sm.loc_zip_url(item) == "https://tile.loc.gov/x/2.zip"


# ----------------------------------------------------------------- student essays and reviews

def test_persuade_and_bawe_records(tmp_path):
    rows = [{"full_text": SENTENCE * 10, "prompt_name": "Car-free cities", "grade_level": "8",
             "assignment": "Write a letter to your senator.", "holistic_essay_score": "4"},
            {"full_text": "Too short.", "prompt_name": "Car-free cities", "grade_level": "8", "assignment": "",
             "holistic_essay_score": "2"}]
    records = list(sm.persuade_records(rows))
    assert len(records) == 1 and records[0]["style_label"] == "essay"
    assert "grade 8" in records[0]["instruction"] and "4 out of 6" in records[0]["instruction"]
    path = tmp_path / "persuade.zip"
    path.write_bytes(zip_of({"persuade_2.0.csv": csv_text(rows)}))
    assert len(list(sm.read_persuade(None, say=lambda *_: None, local_file=str(path)))) == 1
    said = []
    assert list(sm.read_persuade(None, say=said.append)) == [] and "--local-file persuade=" in said[0]
    bawe = list(sm.bawe_records([("0001a.txt", "Urban gardens and wellbeing\n\n" + SENTENCE * 20)]))
    assert 'titled "Urban gardens and wellbeing"' in bawe[0]["instruction"]
    assert "British" in bawe[0]["instruction"]


def test_imdb_and_yelp_reviews(tmp_path):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, text in (("aclImdb/train/pos/1_9.txt", "Loved it.<br /><br />" + SENTENCE * 4),
                           ("aclImdb/train/neg/2_2.txt", "Dull film. " + SENTENCE * 4),
                           ("aclImdb/test/pos/3_8.txt", "Test review " + SENTENCE * 4)):
            data = text.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    records = list(sm.imdb_records(buf.getvalue()))
    assert len(records) == 2
    assert "positive" in records[0]["instruction"] and "9 out of 10" in records[0]["instruction"]
    assert records[0]["response"].startswith("Loved it.\n\n")
    assert "negative" in records[1]["instruction"]
    lines = [json.dumps({"stars": 5, "text": "Great tacos. " + SENTENCE * 3}).encode(),
             json.dumps({"stars": 1, "text": "Cold food."}).encode(), b"not json"]
    yelp = list(sm.yelp_records(lines))
    assert len(yelp) == 1 and "5-star review" in yelp[0]["instruction"]
    path = tmp_path / "review.json"
    path.write_bytes(b"\n".join(lines))
    assert len(list(sm.read_yelp(None, say=lambda *_: None, local_file=str(path)))) == 1


# ----------------------------------------------------------------- developer writing

def test_python_list_message_becomes_an_email_without_the_list_footer():
    data = {"subject": "Re: [Tutor] loops", "content": "Use enumerate() for that, it gives you the index too.\n\n"
            "-- \nhttps://mail.python.org/mailman3/lists/tutor.python.org", "parent": "https://x", "sender_name":
            "Pat Example", "message_id": "m1@example.org", "date": "2026-01-02"}
    record = sm.python_email_record(data, "tutor")
    assert record["type"] == "email" and record["is_reply"] and record["style_label"] == "forum_post"
    assert "mail.python.org" not in record["body"]
    listing = {"results": [{"url": "https://mail.python.org/archives/api/list/tutor@python.org/email/A/"}]}
    pages = {sm.PY_API.format(name="tutor@python.org", offset=0): json.dumps(listing),
             "https://mail.python.org/archives/api/list/tutor@python.org/email/A/": json.dumps(data)}
    got = list(sm.read_python_lists(FakeFetcher(pages), lists=["tutor@python.org"], pages=1))
    assert len(got) == 1 and got[0]["group"] == "tutor"


def test_gharchive_issues_and_comments_leave_out_bots_and_pull_requests():
    issue = {"title": "Crash when the file name has a space", "user": {"type": "User"},
             "body": "<!-- template hint -->When I open a file with a space in its name the app crashes and "
                     "shows this error. It did not happen with the last version, so this is new."}
    events = [
        {"type": "IssuesEvent", "actor": {"login": "sam"}, "repo": {"name": "example/editor"},
         "payload": {"action": "opened", "issue": issue}},
        {"type": "IssueCommentEvent", "actor": {"login": "lee"}, "repo": {"name": "example/editor"},
         "payload": {"action": "created", "issue": issue, "comment": {"user": {"type": "User"}, "body":
                     "Thanks for the report. I can reproduce it on Linux too, and I think the path is not quoted."}}},
        {"type": "IssueCommentEvent", "actor": {"login": "helper[bot]"}, "repo": {"name": "example/editor"},
         "payload": {"action": "created", "issue": issue, "comment": {"body": "This issue is stale and it will "
                                                                               "be closed soon if nothing happens."}}},
        {"type": "IssuesEvent", "actor": {"login": "kim"}, "repo": {"name": "example/editor"},
         "payload": {"action": "opened", "issue": dict(issue, pull_request={})}},
    ]
    records = [sm.gharchive_record(e) for e in events]
    assert records[2] is None and records[3] is None
    assert records[0]["style_label"] == "bug_report" and "template hint" not in records[0]["response"]
    assert "The issue says" in records[1]["instruction"] and "reproduce" in records[1]["response"]
    data = gzip.compress("\n".join(json.dumps(e) for e in events).encode())
    got = list(sm.read_gharchive(FakeFetcher({sm.GH_URL.format(hour="h"): data}), say=lambda *_: None,
                                 hours=["h"]))
    assert len(got) == 2


# ----------------------------------------------------------------- notices, RFIs and speeches

def test_sam_needs_a_key_and_reads_descriptions(monkeypatch):
    monkeypatch.delenv("SAM_GOV_API_KEY", raising=False)
    said = []
    assert list(sm.read_sam(None, say=said.append)) == [] and "SAM_GOV_API_KEY" in said[0]
    search = {"opportunitiesData": [{"title": "Janitorial services for the field office", "fullParentPathName":
                                     "DEPARTMENT OF EXAMPLES.FIELD OFFICE",
                                     "description": "https://api.sam.gov/prod/opportunities/v1/noticedesc?noticeid=1"}]}
    desc = {"description": "<p>" + "The contractor shall provide all labour and supplies to clean the office. " * 12
            + "</p>"}
    pages = {"https://api.sam.gov/opportunities/v2/search*": json.dumps(search),
             "https://api.sam.gov/prod/opportunities/v1/noticedesc?noticeid=1&api_key=TESTKEY": json.dumps(desc)}
    records = list(sm.read_sam(FakeFetcher(pages), say=lambda *_: None, api_key="TESTKEY", per_type=1))
    assert records and records[0]["style_label"] == "procurement"
    assert "Department Of Examples" in records[0]["instruction"] and "TESTKEY" not in records[0]["instruction"]


def test_fedreg_body_keeps_the_notice_and_unwraps_lines():
    page = ("<html><body><pre>[Federal Register Volume 91]\nDEPARTMENT OF EXAMPLES\n\nAGENCY: Office of Examples."
            "\n\nACTION: Request for information.\n\nSUMMARY: The Office asks the public\nfor ideas about safer "
            "bicycle lanes.\n-----------------------------------------------------------------------\n\n[[Page 7]]"
            "\n\nDATES: Send ideas by March 1.\n\n[FR Doc. 2026-1 Filed 1-1-26]\nBILLING CODE 1234</pre></body></html>")
    text = sm.fedreg_body(page)
    assert text.startswith("AGENCY: Office of Examples.")
    assert "The Office asks the public for ideas about safer bicycle lanes." in text
    assert "FR Doc" not in text and "BILLING" not in text and "Page 7" not in text and "----" not in text
    assert sm.fedreg_body("<html><title>Federal Register :: Request Access</title></html>") == ""


def test_fed_speech_page_without_footnotes():
    page = ('<div id="article"><h3 class="title"><em>Planting for Growth</em></h3><p class="speaker">'
            '<a href="#">Governor Pat Example</a></p><p class="location">At the Garden Club, Springfield</p>'
            "<p>Thank you for having me.<a href=\"#fn1\">1</a></p><p>" + SENTENCE + "</p><hr><p>1. The views are "
            "my own.</p></div>")
    title, speaker, place, text = sm.fed_speech(page)
    assert (title, speaker, place) == ("Planting for Growth", "Governor Pat Example", "At the Garden Club, Springfield")
    assert text.startswith("Thank you for having me.") and "views are my own" not in text


CREC_SPEECH = """<html><body><pre>
[Congressional Record Volume 169]
[House]

                          LIBRARY HOURS

  (Ms. EXAMPLE asked and was given permission to address the House for 1
minute.)
  Ms. EXAMPLE. Madam Speaker, I rise to thank the librarians of my town,
who kept the doors open late all winter so students had a warm place to
study. """ + "They helped hundreds of families find jobs and forms. " * 8 + """

[[Page H976]]

  It is time we thank them.
                          ____________________
</pre></body></html>"""

CREC_DEBATE = """<html><body><pre>
  Mr. ALPHA. Mr. President, I rise to talk about the bridge in my State. """ + "It carries thousands of cars. " * 6 + """
  The PRESIDING OFFICER. The Senator from Somewhere.
  Mr. BETA. Will the Senator yield for a question about the bridge funding and the timeline?
  Mr. ALPHA. I am glad to yield to my friend for a question about the bridge.
  Mr. BETA. I thank the Senator. When will the repairs start, and who pays for the detour?
  Mr. ALPHA. I ask unanimous consent that the order for the quorum call be rescinded.
  Mr. ALPHA. The repairs start in spring, and the State pays for the detour this year.
</pre></body></html>"""


def test_crec_speech_debate_and_procedure():
    mods = ('<relatedItem type="constituent" ID="id-CREC-2023-03-01-pt1-PgH975-2"><titleInfo><title>PRAYER</title>'
            '</titleInfo></relatedItem><relatedItem type="constituent" ID="id-CREC-2023-03-01-pt1-PgH976">'
            "<titleInfo><title>LIBRARY HOURS</title></titleInfo></relatedItem>"
            '<relatedItem type="constituent" ID="id-CREC-2023-03-01-pt1-PgD1"><titleInfo><title>Daily Digest</title>'
            "</titleInfo></relatedItem>")
    assert sm.crec_granules(mods) == [("CREC-2023-03-01-pt1-PgH976", "LIBRARY HOURS")]
    speech = sm.crec_record("CREC-2023-03-01-pt1-PgH976", "LIBRARY HOURS", CREC_SPEECH)
    assert speech["type"] == "text" and speech["style_label"] == "speech"
    assert speech["response"].startswith("Madam Speaker, I rise") and "It is time we thank them." in speech["response"]
    assert "asked and was given" not in speech["response"] and "Page H976" not in speech["response"]
    assert 'titled "Library Hours"' in speech["instruction"]
    debate = sm.crec_record("CREC-2023-03-01-pt1-PgS540", "Bridge Repairs", CREC_DEBATE)
    assert debate["type"] == "chat" and "Senate" in debate["setting"] and debate["raw"]
    assert all(not who.startswith("The ") for who, _ in debate["turns"])
    assert not any("quorum call" in w for _, w in debate["turns"])
    vote = CREC_SPEECH.replace("It is time we thank them.", "YEAS--216")
    assert sm.crec_record("CREC-2023-03-01-pt1-PgH977", "On Passage", vote) is None


# ----------------------------------------------------------------- Wikivoyage and Wikiquote

DUMP = """<mediawiki>
<page>
<title>Riverton</title>
<ns>0</ns>
<revision>
<text xml:space="preserve">
'''Riverton''' is a small town on a river.
== Understand ==
""" + SENTENCE * 6 + """
== See ==
* {{see|name=Old Mill|address=1 Mill Road|content=A water mill from 1850 with a small museum [[history]] display.}}
""" + SENTENCE * 5 + """
== Talk ==
Not used.
</text>
</revision>
</page>
<page>
<title>Old place</title>
<ns>0</ns>
<text>#REDIRECT [[Riverton]]</text>
</page>
<page>
<title>Talk:Riverton</title>
<ns>1</ns>
<text>talk about the town</text>
</page>
</mediawiki>"""


def test_wikivoyage_sections_with_listings():
    pages = list(sm.dump_pages(DUMP.splitlines(True)))
    assert [t for t, _ in pages] == ["Riverton"]
    records = list(sm.wikivoyage_records(pages))
    assert [r["instruction"].split('"')[1] for r in records] == ["Understand", "See"]
    see = records[1]["response"]
    assert see.startswith("- Old Mill, 1 Mill Road. A water mill from 1850 with a small museum history display.")
    assert "{{" not in see and records[0]["style_label"] == "travel"


def test_wikiquote_only_old_quotations_and_short_proverbs():
    old = ("'''Ada Example''' (1815 – 1852) was a writer.\n== Quotes ==\n* Patience is the art of hoping while "
           "you keep on working.\n** Letter to a friend (1840)\n* Hi.\n== About ==\n* Someone said she was kind.")
    modern = "'''Bo Example''' (born 1960) is a singer.\n== Quotes ==\n* A modern line that is still under copyright."
    proverbs = "Proverbs of Example Land.\n== A ==\n* A full basket is a light heart for the walk home.\n"
    pages = [("Ada Example", old), ("Bo Example", modern), ("Example proverbs", proverbs)]
    records = list(sm.wikiquote_records(pages))
    assert [r["response"] for r in records] == ["Patience is the art of hoping while you keep on working.",
                                                "A full basket is a light heart for the walk home."]
    assert "(1815–1852)" in records[0]["instruction"]


# ----------------------------------------------------------------- recipes

def test_recipe_text_and_records():
    recipe = {"title": "Bean Soup", "body": "<p>A warm soup.</p><h2>Ingredients</h2><ul><li>1 C beans</li>"
                                            "<li>2 C water</li></ul><h2>Directions</h2><ol><li>Simmer the beans "
                                            "in the water for one hour, stirring now and then.</li><li>Season and "
                                            "serve hot with bread and a green salad on the side.</li></ol>"
                                            "<p>Makes 4 servings of soup for a family lunch or a light dinner.</p><p>" + SENTENCE * 2 + "</p>"}
    text = sm.recipe_text(recipe)
    assert "Ingredients\n- 1 C beans\n- 2 C water" in text
    records = list(sm.recipe_records([recipe], "Example Institute", uk=True))
    assert records[0]["style_label"] == "recipe" and "metric" in records[0]["instruction"]


# ----------------------------------------------------------------- the builder keeps the new labels

def test_build_source_labels_new_styles():
    source = writing_sources.by_key()["wikivoyage"]
    fake = FakeFetcher({sm.WIKIVOYAGE_URL: DUMP})
    original = sm.stream_dump
    try:
        sm.stream_dump = lambda fetcher, url: iter(fetcher.get(url).decode().splitlines(True))
        rows, counts = build_dataset.build_source(source, fake, 10, lambda *_: None, set(), {})
    finally:
        sm.stream_dump = original
    assert counts["kept"] == 2 and {r["style"] for r in rows} == {"travel"}
    assert rows[0]["licence_class"] == writing_sources.SHARE_ALIKE


def test_robots_are_still_checked_for_new_addresses():
    robots = fetch.Robots("https://example.org", "User-agent: *\nDisallow: /archives/list/*/export/\n")
    assert robots.check("https://example.org/archives/api/list/tutor@python.org/emails/")[0]
    assert not robots.check("https://example.org/archives/list/tutor@python.org/export/x.mbox.gz")[0]
