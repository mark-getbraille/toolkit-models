"""Tests of the documented-adult photographs (kit/adult_photo_review.py and wizard/adult_photo_window.py), with
made-up records and made-up downloads only: nothing is fetched from the internet.

They check that:
  - a record with a minor word, an age under 18 or ambiguous wording ("young woman", "maiden", "youthful") is left
    out ENTIRELY: never listed, never fetched, and only counted (its title is in no file of the review folder);
  - anonymous records, a named person under 18 at the photo date, a person without a birth year, a couple with only
    one proven adult, "unidentified" people, and artworks are left out;
  - a record stating adult models, and a single nude whose named sitter is proven 18+, are approved automatically,
    downloaded, marked checked with "adult_approved_by", listed and logged "approved: documented adult (...)";
  - rights decide the group: open, or personal use only (a "noncommercial" workspace);
  - Reject and Unsure delete the picture and its description and block it: a later search never fetches it again;
  - every decision is logged with the reviewer's name and time;
  - the training loader (own_data.check_folder) uses an approved picture only with the review choice and the
    content choice, a personal-use one only with the personal-use category, and never one whose approval is gone;
  - the reviewer window follows the accessibility rules, and Y, N, Escape and F1 work.

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests
"""

import io
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
for part in ("wizard", "kit"):
    sys.path.insert(0, os.path.join(KIT, part))

import adult_photo_review as apr  # noqa: E402
import describe_package as dp  # noqa: E402
import own_data  # noqa: E402

PHOTO = ["photograph", "gelatin silver print"]


def jpeg():
    """A small real JPEG, made in memory."""
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (200, 150), (120, 90, 60)).save(out, "JPEG")
    return out.getvalue()


def record(rid, title, text="", names=(), dates=("1925",), kind=PHOTO, rights="No known restrictions on publication."):
    """A made-up catalogue record as the sources give it."""
    return {"id": rid, "title": title, "institution": "Library of Congress", "page_url": f"https://www.loc.gov/item/{rid}/",
            "image_url": f"https://tile.loc.gov/{rid}.jpg", "catalogue_text": text, "names": list(names),
            "dates": list(dates), "kind": list(kind), "rights": rights}


def gate(r):
    """documented() on a made-up record."""
    return apr.documented([r["title"], r["catalogue_text"]], r["names"], r["dates"], r["kind"], r["rights"])


def test_minor_and_ambiguous_words_leave_a_record_out():
    for title in ("Nude girl on a beach", "Two boys bathing nude", "Sexual intercourse, a young woman",
                  "Nude maiden", "Youthful nude model", "Teenage couple, sexual intercourse", "Nude, aged 16",
                  "Nude schoolgirl", "Infant nude", "Nude study of an adolescent", "A 17-year-old nude model"):
        reason, why = gate(record("x", title, "The models were adults.", ("Doe, Jane, 1890-1960",)))
        assert reason == "" and why == "a child or young person, or an age under 18", title


def test_documentation_is_required():
    cases = {
        "anonymous": record("a", "Nude study of a woman"),
        "under 18 at the photo date": record("b", "Nude study", names=("Doe, Jane, 1910-1990",), dates=("1925",)),
        "no birth year": record("c", "Nude study", names=("Doe, Jane",)),
        "couple, one proven": record("d", "Couple, sexual intercourse", names=("Doe, Jane, 1890-1960",)),
        "unidentified": record("e", "Nude study, unidentified model", names=("Doe, Jane, 1890-1960",)),
        "an artwork": record("f", "Nude woman", "The models were adults.", kind=["engraving"]),
        "not nudity or sex": record("g", "Portrait of a woman", names=("Doe, Jane, 1890-1960",)),
        "taken back": record("h", "Nude study", "The models were possibly not adult models."),
    }
    for case, r in cases.items():
        assert gate(r)[0] == "", case
    assert gate(record("i", "Nude study", names=("Doe, Jane, 1890-1960--Portraits",)))[0].startswith("named")
    assert gate(record("j", "Couple, sexual intercourse", names=("Doe, Jane, 1890-1960", "Roe, John, 1885-1950")))[1] \
        == "sexual"
    assert gate(record("k", "Sex education photograph", "The models were over 18."))[0].startswith("the record states")
    # An uncertain date counts as its earliest year: 1906-1925 with a sitter born 1890 is not proven.
    assert gate(record("l", "Nude study", names=("Doe, Jane, 1890-1960",), dates=("between 1906 and 1925",)))[0] == ""


def test_licence_groups():
    assert apr.licence_group("No known restrictions on publication.") == apr.OPEN
    assert apr.licence_group("Public Domain Mark") == apr.OPEN
    assert apr.licence_group("CC BY 4.0") == apr.OPEN
    for rights in ("CC BY-NC 4.0", "In copyright", "Rights status not evaluated.", ""):
        assert apr.licence_group(rights) == apr.PERSONAL, rights


RECORDS = [
    record("loc-1", "Nude study of a woman", "Photograph of a nude woman seated.", ("Doe, Jane, 1890-1960",)),
    record("loc-2", "Sex education photograph", "Couple demonstrating a position. The models were adults.",
           rights="Rights status not evaluated."),
    record("loc-3", "Nude girl by a stream", "Nude study.", ("Roe, Ann, 1890-1960",)),
    record("loc-4", "Nude study of a young woman", "Seated nude."),
    record("loc-5", "Nude study", "A seated nude woman."),
]


class FakeSession:
    """Made-up downloads: every fetched address is remembered."""

    def __init__(self):
        """No address fetched yet."""
        self.fetched = []

    def get(self, url, **_):
        """A picture answer."""
        self.fetched.append(url)
        return type("R", (), {"status_code": 200, "content": jpeg()})()


def run(folder, s=None, records=RECORDS):
    """search() with the made-up records."""
    s = s or FakeSession()
    approved, counts = apr.search(folder, sources=(("Made up", lambda _s, _m: iter([dict(r) for r in records])),),
                                  s=s, say=lambda *_: None)
    return approved, counts, s


def all_text(folder):
    """Everything written in the review folder's text files."""
    out = []
    for base, _dirs, files in os.walk(folder):
        for name in files:
            if name.endswith((".csv", ".txt", ".json")):
                with open(os.path.join(base, name), encoding="utf-8") as f:
                    out.append(f.read())
    return "\n".join(out)


def test_search_approves_only_documented_and_never_lists_the_rest(tmp_path):
    folder = str(tmp_path / "review")
    approved, counts, s = run(folder)
    assert approved == 2
    assert s.fetched == ["https://tile.loc.gov/loc-1.jpg", "https://tile.loc.gov/loc-2.jpg"]   # nothing else fetched
    assert counts["a child or young person, or an age under 18"] == 1
    assert counts[apr.STUDY_CATEGORY] == 2                   # open nude studies: the nude_photo_studies pack's
    text = all_text(folder)
    for title in ("Nude girl by a stream", "Nude study of a young woman", "loc-3", "loc-4", "loc-5"):
        assert title not in text, title                                    # left out: only counted, never named
    assert "left out, a child or young person, or an age under 18: 1" in text
    review = apr.ReviewFolder(folder)
    items = {i["id"]: i for i in review.items()}
    assert set(items) == {"loc-1", "loc-2"}
    assert items["loc-1"]["group"] == apr.OPEN and items["loc-2"]["group"] == apr.PERSONAL
    assert items["loc-1"]["content"] == "nudity" and items["loc-2"]["content"] == "sexual"
    ws = dp.open_workspace(os.path.dirname(os.path.join(folder, items["loc-2"]["file"])))
    assert ws.data["review_only"] and ws.data["documented_adults"] and ws.data["never_for_picture_making"]
    assert ws.data["review_category"] == "noncommercial" and ws.data["content"] == "sexual"
    entry = ws.pictures[os.path.basename(items["loc-2"]["file"])]
    assert entry["status"] == dp.CHECKED and entry["adult_approved_by"].startswith("documented adult (the record")
    logged = review.decisions()
    assert [d["decision"].split(" (")[0] for d in logged] == ["approved: documented adult"] * 2
    assert all(d["time"] and d["by"] == "automatic" for d in logged)
    # A second search fetches nothing new.
    again, counts, s2 = run(folder)
    assert again == 0 and not s2.fetched and counts["already approved"] == 2


def test_reject_deletes_blocks_and_logs(tmp_path):
    folder = str(tmp_path / "review")
    run(folder)
    review = apr.ReviewFolder(folder)
    item = next(i for i in review.items() if i["id"] == "loc-1")
    path = os.path.join(folder, item["file"])
    assert os.path.isfile(path)
    assert apr.reject(review, "loc-1", "Pat")
    assert not os.path.exists(path) and not os.path.exists(os.path.splitext(path)[0] + ".txt")
    assert os.path.basename(path) not in dp.open_workspace(os.path.dirname(path)).pictures
    assert "loc-1" in review.blocked()
    apr.reject(review, "loc-2", "Pat", "unsure")
    last = review.decisions()[-2:]
    assert [(d["id"], d["decision"], d["by"]) for d in last] == [("loc-1", "rejected", "Pat"), ("loc-2", "unsure", "Pat")]
    _, counts, s = run(folder)
    assert not s.fetched and counts["blocked earlier"] == 2              # never fetched again
    apr.confirm(review, "loc-1", "Pat")
    assert review.decisions()[-1]["decision"].startswith("confirmed")


def test_the_loader_uses_approved_pictures_only_with_the_choices(tmp_path):
    folder = str(tmp_path / "review")
    run(folder)
    approved = os.path.join(folder, apr.APPROVED)
    rows, *_ = own_data.check_folder(approved, contents=())
    assert rows == []                                                    # no content choice: nothing
    rows, *_ = own_data.check_folder(approved, contents=("nudity", "sexual"), review=False)
    assert rows == []                                                    # picture-making (review off): nothing
    rows, *_ = own_data.check_folder(approved, contents=("nudity", "sexual"))
    assert {os.path.basename(r["original"]) for r in rows} == {"loc-1.jpg"}   # the personal one needs its choice
    rows, *_ = own_data.check_folder(approved, contents=("nudity", "sexual"),
                                     categories=own_data.OPEN_CATEGORIES + ("noncommercial",))
    assert {os.path.basename(r["original"]) for r in rows} == {"loc-1.jpg", "loc-2.jpg"}
    assert all(r.get("review") == apr.KEY for r in rows)
    # An entry whose approval is gone is never used, even if it still says "checked".
    item = next(i for i in apr.ReviewFolder(folder).items() if i["id"] == "loc-1")
    ws = dp.open_workspace(os.path.dirname(os.path.join(folder, item["file"])))
    ws.pictures["loc-1.jpg"]["adult_approved_by"] = ""
    ws.save()
    rows, *_ = own_data.check_folder(approved, contents=("nudity", "sexual"))
    assert rows == []


def test_fetch_into_memory_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(os.listdir(tmp_path))
    data = apr.fetch_into_memory(FakeSession(), "https://example.org/x.jpg")
    assert data and set(os.listdir(tmp_path)) == before


wx = pytest.importorskip("wx")


@pytest.fixture
def app():
    """One wx.App."""
    yield wx.GetApp() or wx.App(False)


def test_the_window_is_accessible_and_its_keys_work(app, tmp_path, monkeypatch):
    import adult_photo_window as w
    from test_accessibility import assert_accessible, press
    folder = str(tmp_path / "review")
    run(folder)
    window = w.ReviewWindow(None, folder, "Pat")
    assert_accessible(window)
    assert_accessible(w.NameDialog(None))
    opened, ended = [], []
    monkeypatch.setattr(w, "open_file", lambda path: opened.append(path))
    monkeypatch.setattr(window, "EndModal", lambda code: ended.append(code))
    window.list.SetSelection(0)
    first = window.current()["id"]
    press(window, ord("Y"))
    assert apr.ReviewFolder(folder).decisions()[-1]["decision"].startswith("confirmed")
    window.list.SetSelection(0)
    press(window, ord("N"))
    assert first in apr.ReviewFolder(folder).blocked()
    press(window, wx.WXK_F1)
    assert opened and opened[0].endswith("HOW TO REVIEW DOCUMENTED ADULT PHOTOGRAPHS.txt") and os.path.exists(opened[0])
    press(window, wx.WXK_ESCAPE)
    assert ended
    window.Destroy()


def test_descriptions_follow_the_guide():
    """A description says how adulthood is documented and uses no judgement words."""
    text = apr.description_of({"institution": "Library of Congress", "year": 1925, "title": "Obscene nude study",
                               "catalogue_text": "A lewd photograph of a seated nude woman."},
                              "named, photo year 1925: Doe, Jane, born 1890")
    assert "documents that the people shown are adults (named, photo year 1925" in text
    assert not apr.JUDGEMENT.search(text) and "explicit" in text


def test_non_sexual_nude_studies():
    """A non-sexual nude photograph describing an adult is taken here when its rights are personal use only (open
    ones are the nude_photo_studies pack's); one describing no adult, naming a group, family or young person, or
    anything sexual needs documentation as before."""
    personal, open_rights = "In copyright", "Public Domain Mark"
    study = record("s1", "A young woman posing naked in a photographic studio. Photograph, ca.1900.", rights=personal)
    reason, content = apr.documented([study["title"]], (), study["dates"], study["kind"], personal)
    assert reason.startswith("a non-sexual nude study") and content == "nudity"
    assert apr.documented([study["title"]], (), study["dates"], study["kind"], open_rights) == ("", apr.STUDY_CATEGORY)
    for title in ("A naked figure in a studio. Photograph.", "A family posing naked. Photograph.",
                  "A naked girl in a studio. Photograph.", "Group of naked women. Photograph.",
                  "A naked youth. Photograph.", "A young couple, naked, making love. Photograph."):
        assert apr.documented([title], (), ("1900",), PHOTO, personal)[0] == "", title


def test_nude_study_words_match_the_pack():
    """The local builder's nude-study words are the open pack's (packs/adult_art_packs.py)."""
    sys.path.insert(0, os.path.join(os.path.dirname(KIT), "packs"))
    import build_packs  # noqa: F401 - loaded first, as the pack files expect
    import adult_art_packs as pack
    assert apr.ADULT_CUE.pattern == pack.ADULT_CUE.pattern
    assert apr.PEOPLE_UNKNOWN.pattern == pack.PEOPLE_UNKNOWN.pattern


LINK_RECORDS = [
    record("loc-10", "Couple, sexual intercourse. Photograph.", "Anonymous studio photograph, ca. 1900."),
    record("loc-11", "A girl and a man, sexual intercourse. Photograph."),
    record("loc-12", "A boy, sexual intercourse. Photograph."),
    record("loc-13", "Couple, sexual intercourse, she is aged 16. Photograph."),
]


def test_link_only_list_has_no_pictures_and_no_minor_records(tmp_path):
    folder = str(tmp_path / "review")
    approved, counts, s = run(folder, records=LINK_RECORDS)
    assert approved == 0 and s.fetched == []                         # nothing fetched at all
    review = apr.ReviewFolder(folder)
    items = apr.link_items(review)
    assert [i["id"] for i in items] == ["loc-10", "loc-11", "loc-12"]   # an age under 18: never listed
    assert items[0]["section"] == apr.NO_DOCUMENTATION_SECTION
    assert items[1]["section"] == items[2]["section"] == apr.ASK_FIRST_SECTION
    assert set(items[0]) == set(apr.LINK_COLUMNS) and "image" not in " ".join(apr.LINK_COLUMNS)
    with open(review.path(apr.LINK_ONLY), encoding="utf-8") as f:
        text = f.read()
    assert "tile.loc.gov" not in text and "loc-13" not in text and "aged 16" not in text
    assert not any(n.lower().endswith((".jpg", ".png")) for _b, _d, files in os.walk(folder) for n in files)


def test_enquiry_has_placeholders_only(tmp_path):
    folder = str(tmp_path / "review")
    run(folder, records=LINK_RECORDS)
    review = apr.ReviewFolder(folder)
    path = apr.enquiry(review, "loc-10")
    assert path.startswith(review.path(apr.ENQUIRIES))
    with open(path, encoding="utf-8") as f:
        text = f.read()
    assert "[YOUR NAME]" in text and "[YOUR EMAIL]" in text and "loc-10" in text and "model releases" in text
    assert "@" not in text.replace("<[YOUR EMAIL]>", "")


def test_approval_needs_documentation_and_fetches_only_then(tmp_path):
    folder = str(tmp_path / "review")
    run(folder, records=LINK_RECORDS)
    review = apr.ReviewFolder(folder)
    s = FakeSession()
    for evidence in ("", "looks old", "They look well over 18 to me"[:15]):
        with pytest.raises(apr.NotEnoughEvidence):
            apr.approve_documented(review, "loc-10", "Pat", evidence, s=s, image_url="https://tile.loc.gov/x.jpg")
    with pytest.raises(apr.NotEnoughEvidence):
        apr.approve_documented(review, "loc-10", "", "The archive's model release forms name both sitters, born "
                               "1870 and 1872.", s=s, image_url="https://tile.loc.gov/x.jpg")
    assert s.fetched == []                                           # nothing fetched before a documented approval
    evidence = "Email from the archive, 3 Dec 2026: model releases on file; both sitters born 1870 and 1872."
    assert apr.approve_documented(review, "loc-10", "Pat", evidence, s=s, image_url="https://tile.loc.gov/x.jpg")
    assert s.fetched == ["https://tile.loc.gov/x.jpg"]
    last = review.decisions()[-1]
    assert (last["id"], last["decision"], last["by"]) == ("loc-10", "approved with documentation", "Pat")
    assert "model releases" in last["reason"] and last["time"]
    item = next(i for i in review.items() if i["id"] == "loc-10")
    assert item["status"].startswith("approved: documented by the institution")
    rows, *_ = own_data.check_folder(os.path.join(folder, apr.APPROVED), contents=("nudity", "sexual"))
    assert [os.path.basename(r["original"]) for r in rows] == ["loc-10.jpg"]


def test_not_approved_blocks(tmp_path):
    folder = str(tmp_path / "review")
    run(folder, records=LINK_RECORDS)
    review = apr.ReviewFolder(folder)
    apr.not_approved(review, "loc-10", "Pat", "unsure")
    assert "loc-10" in review.blocked() and apr.link_items(review)[0]["status"] == "unsure"
    rows, *_ = own_data.check_folder(os.path.join(folder, apr.APPROVED), contents=("nudity", "sexual")) \
        if os.path.isdir(os.path.join(folder, apr.APPROVED)) else ([],)
    assert rows == []


def test_ask_the_institution_first(tmp_path):
    """Girl, boy, lad or lass alone in a sexual photograph's record: listed first, approved only with documentation
    of age; any other minor word still leaves the record out and unlisted."""
    folder = str(tmp_path / "review")
    others = [record("loc-20", "A girl and a teenager, sexual intercourse. Photograph."),
              record("loc-21", "Schoolgirl, sexual intercourse. Photograph."),
              record("loc-22", "A boy and a child, sexual intercourse. Photograph."),
              record("loc-23", "A lass and a lad, sexual intercourse. Photograph.")]
    run(folder, records=LINK_RECORDS + others)
    review = apr.ReviewFolder(folder)
    listed = {i["id"]: i["section"] for i in apr.link_items(review)}
    assert set(listed) == {"loc-10", "loc-11", "loc-12", "loc-23"}
    assert listed["loc-23"] == apr.ASK_FIRST_SECTION and "BEFORE opening the page" in apr.ASK_FIRST_SECTION
    s = FakeSession()
    with pytest.raises(apr.NotEnoughEvidence):        # documentation that says nothing about age is not enough
        apr.approve_documented(review, "loc-11", "Pat", "The archive replied that the photographer is known.",
                               s=s, image_url="https://tile.loc.gov/x.jpg")
    assert s.fetched == []
    assert apr.approve_documented(review, "loc-11", "Pat", "The archive's model register gives both sitters' "
                                  "birth years, 1871 and 1874; the photograph is dated 1899.", s=s,
                                  image_url="https://tile.loc.gov/x.jpg")


def test_the_window_offers_no_judgement_option(app, tmp_path):
    """The reviewer window approves link-only records only with documentation: no button about how old people look."""
    import adult_photo_window as w
    folder = str(tmp_path / "review")
    run(folder, records=LINK_RECORDS)
    window = w.ReviewWindow(None, folder, "Pat")
    labels = [c.GetLabel().lower() for c in window.panel.GetChildren() if isinstance(c, wx.Button)]
    assert not any("over 18" in l or "look" in l or "judg" in l for l in labels)
    assert window.links.GetString(0).startswith("ASK THE INSTITUTION FIRST")
    window.Destroy()
