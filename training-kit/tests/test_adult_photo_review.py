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
    return apr.documented([r["title"], r["catalogue_text"]], r["names"], r["dates"], r["kind"])


def test_minor_and_ambiguous_words_leave_a_record_out():
    for title in ("Nude girl on a beach", "Two boys bathing nude", "Nude study of a young woman",
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
    assert counts["a child or young person, or an age under 18"] == 2
    text = all_text(folder)
    for title in ("Nude girl by a stream", "Nude study of a young woman", "loc-3", "loc-4", "loc-5"):
        assert title not in text, title                                    # left out: only counted, never named
    assert "left out, a child or young person, or an age under 18: 2" in text
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
