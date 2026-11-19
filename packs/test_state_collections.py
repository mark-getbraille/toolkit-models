"""A self-test of the state digital library and Newberry readers (packs/state_collections_packs.py), with made-up
records only: nothing is downloaded from the internet.

It checks that:
  - rights are read from rightsstatements.org and Creative Commons addresses and from words; an open address with
    restricting words on the same item is not open (the stricter wins); no statement and research-only are told apart;
  - the screens leave out nudity, crime, portraits, violence and atrocity, and American Indian or Indigenous material;
    a child is marked;
  - a collection's shared sentences are taken out of its descriptions; a title-only record is set aside;
  - the CONTENTdm field mapping, record reading, IIIF address and skipped collections work on a made-up API;
  - the OAI-PMH reader follows resumption tokens and finds pictures; the DLG and Newberry records are read;
  - robots.txt is obeyed (AI-crawler blocks, ai-train=no, disallowed paths, crawl delays);
  - the packs are wired into build_packs, the workflows and the kit.

Run it from the repository's folder:   python3 -m pytest packs/test_state_collections.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import state_collections_packs as m  # noqa: E402

NOC = "http://rightsstatements.org/vocab/NoC-US/1.0/"
ROOT = os.path.join(HERE, "..")


def test_rights_open_closed_none_research():
    """Open addresses and words; closed addresses; restricting words win; no statement; research only."""
    assert m.rights_of([NOC])[:2] == ("open", "No Copyright - United States (rightsstatements.org)")
    assert m.rights_of(["http://rightsstatements.org/vocab/NKC/1.0/"])[0] == "open"
    assert m.rights_of(["https://creativecommons.org/licenses/by/4.0/"])[1] == "CC BY 4.0"
    assert m.rights_of(["https://creativecommons.org/publicdomain/zero/1.0/"])[1] == "CC0"
    assert m.rights_of(["No Copyright - United States"])[1] == "No Copyright - United States"
    assert m.rights_of(["Public domain"])[1] == "Public domain"
    assert m.rights_of(["All images are in the public domain."])[0] == "open"
    assert m.rights_of(["http://rightsstatements.org/vocab/InC/1.0/"])[0] == "closed"
    assert m.rights_of(["https://creativecommons.org/licenses/by-nc-nd/4.0/"])[0] == "closed"
    assert m.rights_of(["https://creativecommons.org/licenses/by-sa/4.0/"])[0] == "closed"
    assert m.rights_of(["", None])[0] == "none"
    # Ohio History Connection: NoC-US address, but "research purposes only" in words: not open, research.
    ohio = ["Online access is provided for research purposes only. For rights and reproduction requests or more "
            "information, go to http://www.ohiohistory.org/images/information", NOC]
    assert m.rights_of(ohio)[0] == "research"
    # City archives: NoC-US address, but permission must be obtained: closed.
    savannah = [NOC, "All requests for permission to publish or quote from the collections must be submitted in "
                     "writing to the Municipal Archives."]
    assert m.rights_of(savannah)[0] == "closed"
    # "No permission is required" does not restrict.
    assert m.rights_of([NOC, "No permission is required from the rights-holder(s)."])[0] == "open"
    # The standard NoC-US explanation does not restrict.
    std = ("No Copyright - United States: The organization that has made the Item available believes that the Item "
           "is in the Public Domain under the laws of the United States, but a determination was not made as to its "
           "copyright status under the copyright laws of other countries. The Item may not be in the Public Domain "
           "under the laws of other countries.")
    assert m.rights_of([std])[0] == "open"
    assert m.rights_of(["Copyright 1990, all rights reserved"])[0] == "closed"


def test_screens():
    """Nudity, crime, portraits, violence, the Klan and Indigenous material are left out; a street scene is kept."""
    keep = "Main Street looking north with stores, wagons and a church steeple"
    assert m.why_left_out(keep) == ""
    for words in ("Nude bathers at the river", "Prisoners in the county jail", "Portrait of John Smith",
                  "Lynching in the town square", "Ku Klux Klan parade", "Flood victims, dead bodies in the street",
                  "Navajo weaver at her loom", "American Indian camp near the river", "Bathing beauty contest"):
        assert m.why_left_out(words), words


def test_shared_sentences_and_answers():
    """Collection boilerplate shared by many records is taken out; the record's own words stay."""
    tail = "The Ewing Collection consists of 5,055 glass plate negatives."
    texts = [f"A man with a horse in front of a barn. {tail}", f"Two women on a porch with flowers. {tail}",
             f"A wagon loaded with hay. {tail}", f"A river with a covered bridge. {tail}"]
    shared = m.shared_sentences(texts)
    assert tail in shared
    assert m.own_words(texts[0], shared) == "A man with a horse in front of a barn."


def test_us_place():
    """US places from CONTENTdm, DLG and subject forms; no state, no place."""
    assert m.us_place("Athens (Ohio)") == "Athens, Ohio, USA"
    assert m.us_place(["United States, Georgia, Clarke County, Athens, 33.96095, -83.37794"]) == "Athens, Georgia, USA"
    assert m.us_place("Bismarck, North Dakota") == "Bismarck, North Dakota, USA"
    assert m.us_place("Paris, France") == ""


def candidate(**changes):
    """A made-up candidate dict as the readers make it."""
    item = {"name": "x-1.jpg", "url": "https://example.org/iiif/2/c:1/full/!2048,2048/0/default.jpg",
            "page": "https://example.org/digital/collection/c/id/1", "title": "Main Street, Athens",
            "description": "Main Street looking north, with stores, horse-drawn wagons and people on the sidewalk.",
            "words": "Main Street, Athens Main Street looking north, with stores, wagons", "year": 1910,
            "place": "Athens, Ohio, USA", "library": "Example Library", "collection": "Town views",
            "subjects": ["Streets"], "credit": "Main Street, Athens, Example Library, {licence}, https://example.org",
            "photo": True}
    item.update(changes)
    return item


def test_judge_takes_sets_aside_and_refuses():
    """Taken with its rows; a title-only record set aside; closed rights refused; a child marked."""
    build_packs.reset_needs()
    items, answers = [], set()
    assert m.judge(candidate(), [NOC], items, answers, "k") == "taken"
    name, url, rows = items[0]
    assert rows[0]["question"] == m.DESCRIBE_Q and rows[0]["answer"].startswith("Main Street, Athens. Main Street")
    assert "No Copyright - United States" in rows[0]["credit"] and "{licence}" not in rows[0]["credit"]
    assert rows[1]["question"] == m.WHERE_Q and rows[1]["answer"] == "It was taken in Athens, Ohio, USA."
    assert rows[0]["facts"]["holding_library"] == "Example Library"
    assert m.judge(candidate(name="x-2.jpg", url="https://example.org/2.jpg", description="", title="Barn"),
                   [NOC], items, answers, "k") == "needs"
    assert any(n["name"] == "x-2.jpg" for n in build_packs.NEEDS)
    assert m.judge(candidate(name="x-3.jpg"), ["http://rightsstatements.org/vocab/InC/1.0/"], items, answers,
                   "k") != "taken"
    child = candidate(name="x-4.jpg", url="https://example.org/4.jpg",
                      description="A girl feeding chickens in the farmyard beside the red barn.",
                      words="A girl feeding chickens in the farmyard")
    assert m.judge(child, [NOC], items, answers, "k") == "taken"
    assert items[-1][2][0].get("child") is True
    build_packs.reset_needs()


class FakeResponse:
    """A made-up requests response."""

    def __init__(self, data=None, status=200, text=""):
        self._data, self.status_code, self.text, self.headers = data, status, text, {}
        self.content = text.encode("utf-8")

    def json(self):
        return self._data


class FakeCDM:
    """A made-up CONTENTdm server API answering the calls the reader makes."""

    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(url)
        q = url.split("?q=", 1)[1]
        if q.startswith("dmGetCollectionList"):
            return FakeResponse([{"alias": "/photos", "name": "Town views"},
                                 {"alias": "/news", "name": "Weekly Herald newspaper"},
                                 {"alias": "/tribe", "name": "Cherokee tribal photographs"}])
        if q.startswith("dmGetCollectionFieldInfo/photos"):
            return FakeResponse([{"nick": "title", "dc": "title", "name": "Title"},
                                 {"nick": "descri", "dc": "descri", "name": "Description"},
                                 {"nick": "rights", "dc": "rights", "name": "Rights"},
                                 {"nick": "righta", "dc": "BLANK", "name": "Rights URI"},
                                 {"nick": "type", "dc": "type", "name": "Type"},
                                 {"nick": "place", "dc": "coveraa", "name": "Place"},
                                 {"nick": "date", "dc": "date", "name": "Date"}])
        if q.startswith("dmQuery/photos"):
            recs = [{"pointer": 11, "filetype": "jp2", "title": "Main Street, Athens",
                     "descri": "Main Street looking north with stores, wagons and a church steeple.",
                     "rights": {}, "righta": NOC, "type": "StillImage", "place": "Athens (Ohio)", "date": "1910"},
                    {"pointer": 12, "filetype": "jp2", "title": "Courthouse",
                     "descri": "The county courthouse with its clock tower and the square in front.",
                     "rights": "Copyright Example Society, all rights reserved", "righta": {}, "type": "StillImage",
                     "place": {}, "date": {}},
                    {"pointer": 13, "filetype": "cpd", "title": "Letters of a farmer",
                     "descri": "Letters written by a farmer to his brother about the harvest and the weather.",
                     "rights": {}, "righta": NOC, "type": "Text", "place": {}, "date": {}}]
            return FakeResponse({"pager": {"total": 3}, "records": recs})
        return FakeResponse(None, 404)


def test_contentdm_reader():
    """Field roles, the skipped collections, the open record taken, the closed and text records not."""
    build_packs.reset_needs()
    roles = m.field_roles([{"nick": "righta", "dc": "BLANK", "name": "Rights URI"},
                           {"nick": "title", "dc": "title", "name": "Title"},
                           {"nick": "covera", "dc": "coveraa", "name": "Place"}])
    assert roles["rights"] == ["righta"] and roles["title"] == ["title"] and roles["place"] == ["covera"]
    fake = FakeCDM()
    robots = m.RobotsGuard(fetch=lambda host: "User-agent: *\nDisallow: /oai/\n")
    site = m.ContentDM("cdm.example.org", "Example Memory", s=fake, pause=0, robots=robots, prefix="ex")
    site.pacer = m.Pacer(0)
    items = m.cdm_site_items(site, 10, m.pass_random("t"), "k", set())
    assert [n for n, _, _ in items] == ["ex-photos-11.jpg"]
    assert items[0][1] == "https://cdm.example.org/iiif/2/photos:11/full/!2048,2048/0/default.jpg"
    assert items[0][2][0]["place"] == "Athens, Ohio, USA"
    assert not any("news" in c or "tribe" in c for c in fake.calls)    # skipped by their names
    # The personal-use mode gives the records with no statement (none here) or research-only.
    assert m.cdm_site_items(site, 10, m.pass_random("t"), "k", set(), mode="none") == []


def test_robots_guard():
    """AI-crawler blocks, ai-train=no, disallowed paths and crawl delays."""
    texts = {"a.org": "User-agent: *\nCrawl-delay: 5\nDisallow: /oai/\n",
             "b.org": "User-agent: ClaudeBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n",
             "c.org": "User-agent: *\nContent-Signal: search=yes,ai-train=no\nAllow: /\n",
             "d.org": None}
    g = m.RobotsGuard(fetch=texts.get)
    assert g.allowed("https://a.org/digital/bl/dmwebservices/index.php") == ("", 5.0)
    assert g.allowed("https://a.org/oai/oai.php")[0]
    assert "AI crawlers" in g.allowed("https://b.org/x")[0]
    assert "ai-train=no" in g.allowed("https://c.org/x")[0]
    assert g.allowed("https://d.org/x")[0]
    assert g.delay("https://a.org/x", 1.0) == 5.0
    # RFC 9309 matching: "Disallow: /records?" forbids the search pages, not "/records.json?..." (the DLG API);
    # wildcards and "$"; the longest rule wins.
    dlg = m.RobotsGuard(fetch=lambda host: "User-agent: *\nDisallow: /records?\nDisallow: /records.atom?\n"
                                           "Disallow: /*.jp2$\nDisallow: /a/\nAllow: /a/b/\n")
    assert dlg.allowed("https://dlg.example/records.json?per_page=100")[0] == ""
    assert dlg.allowed("https://dlg.example/records?q=x")[0]
    assert dlg.allowed("https://dlg.example/records.atom?q=x")[0]
    assert dlg.allowed("https://dlg.example/files/x.jp2")[0] and not dlg.allowed("https://dlg.example/x.jp2?s=1")[0]
    assert dlg.allowed("https://dlg.example/a/b/c")[0] == "" and dlg.allowed("https://dlg.example/a/c")[0]
    # A group for this kit by name wins over "*".
    own = m.RobotsGuard(fetch=lambda host: "User-agent: *\nDisallow: /\n\nUser-agent: PictureModelTrainingKit\n"
                                           "Allow: /\n")
    assert own.allowed("https://x.example/y")[0] == ""
    # A site that refuses three API calls in a row is not read further.
    site = m.ContentDM("cdm.example.org", "Example", s=type("S", (), {"get": lambda self, *a, **k: FakeResponse(
        None, 403)})(), pause=0, robots=m.RobotsGuard(fetch=lambda h: ""), prefix="ex")
    site.pacer = m.Pacer(0)
    for _ in range(5):
        site.api("dmGetCollectionList")
    assert site.failures == 3


OAI_PAGE = """<?xml version="1.0"?><OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><ListRecords>
<record><header><identifier>oai:x:1</identifier></header><metadata><oai_dc:dc
 xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>Pamlico River</dc:title><dc:description>Postcard of a drugstore by the river, with a dock.</dc:description>
<dc:identifier>https://lib.example.edu/1</dc:identifier><dc:type>StillImage</dc:type><dc:format>postcards</dc:format>
<dc:rights>{rights}</dc:rights><dc:relation>https://lib.example.edu/files/1.jpg</dc:relation>
<dc:coverage>Washington (N.C.); North Carolina</dc:coverage></oai_dc:dc></metadata></record>
<record><header status="deleted"><identifier>oai:x:2</identifier></header></record>
{token}</ListRecords></OAI-PMH>"""


def test_oai_reader():
    """Records parsed, deleted ones dropped, resumption followed, the picture and rights found."""
    pages = [OAI_PAGE.format(rights=NOC, token="<resumptionToken>t1</resumptionToken>"),
             OAI_PAGE.format(rights="Made available for research, teaching, and private study.", token="")]

    class S:
        def __init__(self):
            self.params = []

        def get(self, url, params=None, timeout=None):
            self.params.append(dict(params))
            return FakeResponse(text=pages[len(self.params) - 1])

    s = S()
    robots = m.RobotsGuard(fetch=lambda host: "")
    recs = m.oai_records(s, "https://lib.example.edu/oai", most=10, pacer=m.Pacer(0), robots=robots)
    assert len(recs) == 2 and s.params[1] == {"verb": "ListRecords", "resumptionToken": "t1"}
    item, rights = m.oai_candidate(recs[0], "Example Library", "ex")
    assert item["url"] == "https://lib.example.edu/files/1.jpg" and item["photo"]
    assert m.rights_of(rights)[0] == "open" and m.rights_of(m.oai_candidate(recs[1], "E", "ex")[1])[0] == "research"
    assert m.oai_picture({"identifier": ["https://cdm.example.org/cdm/ref/collection/pc/id/7"]}) == \
        "https://cdm.example.org/iiif/2/pc:7/full/!2048,2048/0/default.jpg"


def test_dlg_and_newberry_records():
    """A DLG record (its local rights words count too) and a Newberry asset (its own caption, not the summary)."""
    doc = {"id": "aaa_bbb_1", "dcterms_title": ["Peach orchard"], "dcterms_description": [
        "Rows of peach trees in bloom on a farm near Fort Valley."], "dc_right": [NOC], "dlg_local_right": None,
        "edm_is_shown_at": ["http://cdm17413.contentdm.oclc.org/cdm/ref/collection/imagecoll/id/6796"],
        "dcterms_type": ["StillImage"], "dcterms_medium": ["photographs"], "dcterms_provenance": ["Troup County Archives"],
        "dcterms_spatial": ["United States, Georgia, Peach County, Fort Valley, 32.5, -83.8"], "dc_date": ["1925"]}
    item, rights = m.dlg_candidate(doc)
    assert item["url"] == "http://cdm17413.contentdm.oclc.org/iiif/2/imagecoll:6796/full/!2048,2048/0/default.jpg"
    assert item["place"] == "Fort Valley, Georgia, USA" and m.rights_of(rights)[0] == "open"
    doc["dlg_local_right"] = ["This item is protected by copyright. For other uses, permission must be granted."]
    assert m.rights_of(m.dlg_candidate(doc)[1])[0] == "closed"
    asset = {"CoreField.Identifier": "NL1ABC", "CoreField.Title": "Porte Monumentale",
             "CoreField.CaptionLong": "Large white domed building with archways next to a golden statue",
             "new.Summary-Long": "Artistic postcards from the late 19th century.", "new.Format": "Postcards,Printed ephemera",
             "new.Subject": "Expositions,Paris (France)", "new.Rights-Status": "No Copyright - United States",
             "new.Contributing-Institution": "Newberry Library", "Path_TR1": {"URI": "https://cdn.example/NL1ABC.jpg"},
             "MediaType": "Image"}
    item, rights = m.newberry_candidate(asset)
    assert item["description"].startswith("Large white domed building") and item["url"].endswith("NL1ABC.jpg")
    assert m.rights_of(rights)[0] == "open" and item["photo"]
    asset["CoreField.CaptionLong"] = asset["new.Summary-Long"]
    assert m.newberry_candidate(asset)[0]["description"] == ""


def test_wiring():
    """The packs are in build_packs, the workflow's known list and limits, and the kit (people: not for
    picture-making); the personal-use entry and the left-out list are in the kit."""
    keys = set(m.STATE_COLLECTIONS_PACKS)
    assert keys <= set(build_packs.PACKS) and keys == set(m.STATE_COLLECTIONS_LIMITS)
    assert not keys & build_packs.COMMONS_KEYS
    with open(os.path.join(ROOT, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        known = f.read()
    with open(os.path.join(ROOT, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        limits = f.read()
    for key in keys:
        assert f'"{key}"' in known, key
        assert re.search(rf"\b{key}\) limit={m.STATE_COLLECTIONS_LIMITS[key]} ;;", limits), key
    import sources
    kit = {s.key for s in sources.SOURCES}
    assert keys <= kit and keys <= set(sources.PEOPLE_AND_BODILY_PACK_KEYS)
    assert "state_libraries_personal" in kit and "state_libraries_personal" in sources.NOT_FOR_PICTURE_MAKING
