"""Tests of the pictures that need a description on the training computer: opening a needs zip as a Describe pictures
workspace (kit/needs_workspace.py), building a review pack (kit/review_pack.py: page text, robots.txt, the pack's
format, carrying on after a stop) and the "Build a review pack" window of Dataset Preparation (accessibility, keys).
Every web answer is made up: nothing is downloaded from the internet.

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests     (on Windows: python -m pytest -q training-kit\\tests)
"""

import io
import json
import os
import sys
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
for part in ("wizard", "kit", "prepare"):
    sys.path.insert(0, os.path.join(KIT, part))

import describe_package  # noqa: E402
import needs_workspace  # noqa: E402
import own_data  # noqa: E402
import review_pack  # noqa: E402

PAGE = """<html><head><title>Object 1</title><meta name="description" content="A museum record of a red jug.">
<script>var x = "<p>not text</p>";</script>
<script type="application/ld+json">{"@type": "VisualArtwork", "name": "Red jug", "description": "Earthenware jug."}
</script></head><body><nav><p>Menu text</p></nav>
<h1>Collection highlights</h1>
<h2>The red jug</h2>
<p>Before the picture: the jug was made in Delft about 1700.</p>
<figure><img src="/images/full/jug-12345678_large.jpg" alt="A red jug with a white handle" title="Red jug">
<figcaption>Figure 3. Red earthenware jug, side view.</figcaption></figure>
<p>After the picture: it holds two litres.</p>
<h2>Other things</h2>
<p>As Figure 3 shows, the glaze is cracked.</p>
<img src="/images/logo.png" alt="Museum logo">
</body></html>"""


def jpeg(shade):
    """A small made-up JPEG picture of one colour."""
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (96, 72), (shade, 90, 255 - shade)).save(out, "JPEG", quality=90)
    return out.getvalue()


def needs_zip(path, rows, pictures):
    """A made-up needs zip in the format packs/build_packs.write_needs writes (needs.jsonl, the pictures and a
    describing.json of a review collection)."""
    entries = {}
    for row in rows:
        if row.get("file"):
            entries[os.path.basename(row["file"])] = dict(needs_workspace.entry_fields(row), status="new",
                                                          question="Describe this picture.")
    meta = {"format": 1, "name": "Needs a description: test", "people": [], "pictures": entries,
            "review_only": True, "review_source": "needs-test", "review_category": "open",
            "never_for_picture_making": True, "package": {"made_by": "test", "made_at": "2026-11-18T00:00:00Z"}}
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("needs.jsonl", "".join(json.dumps(r) + "\n" for r in rows))
        z.writestr("describing.json", json.dumps(meta))
        z.writestr("README.txt", "test")
        for name, data in pictures.items():
            z.writestr(f"pictures/{name}", data)
    return path


ROWS = [{"file": "pictures/jug.jpg", "url": "https://museum.example/images/full/jug-12345678_large.jpg",
         "page_url": "https://museum.example/object/1", "credit": "Red jug, Example Museum, CC0", "licence": "CC0",
         "category": "open", "source": "test", "hints": {"title": "Jug", "text": "Jug."},
         "reason": "its caption is under six words", "place": "Delft, Netherlands", "place_kind": "origin",
         "content": "", "child": False, "not_for_picture_making": False, "added": "2026-11-18"},
        {"file": "pictures/boys.jpg", "url": "https://museum.example/images/boys-87654321.jpg",
         "page_url": "https://museum.example/private/2", "credit": "Boys, Example Museum, CC0", "licence": "CC0",
         "category": "open", "source": "test", "hints": {"title": "Two boys"}, "reason": "no description",
         "place": "", "place_kind": "", "content": "", "child": True, "not_for_picture_making": True,
         "added": "2026-11-18"},
        {"url": "https://other.example/pictures/only-address-55555555.jpg", "page_url": "", "credit": "x, CC BY 2.0",
         "licence": "CC BY 2.0", "category": "open", "source": "test", "hints": {}, "reason": "no description",
         "url_only": True, "added": "2026-11-18"}]


class FakeWeb:
    """Made-up websites: robots.txt of museum.example forbids /private/, other.example forbids everything; every
    request is counted."""

    def __init__(self):
        """No requests yet."""
        self.asked = []

    def __call__(self, url, headers=None):
        """One answer: (status, body, headers)."""
        self.asked.append(url)
        if url == "https://museum.example/robots.txt":
            return 200, b"User-agent: *\nDisallow: /private/\n", {}
        if url == "https://other.example/robots.txt":
            return 200, b"User-agent: *\nDisallow: /\n", {}
        if url == "https://museum.example/object/1":
            return 200, PAGE.encode("utf-8"), {}
        return 404, b"", {}


def polite(web, sleeps=None):
    """A Polite downloader on the made-up web, with a made-up clock (no real waiting)."""
    clock = [0.0]

    def sleep(seconds):
        """Pass the made-up time."""
        (sleeps if sleeps is not None else []).append(seconds)
        clock[0] += seconds
    return review_pack.Polite(opener=web, clock=lambda: clock[0], sleep=sleep)


# ----------------------------------------------------------------- page text

def test_page_text_finds_alt_caption_heading_and_nearby_text():
    fields = review_pack.extract_page_text(PAGE, ("https://museum.example/images/full/jug-12345678_large.jpg",))
    assert fields["alt"] == "A red jug with a white handle" and fields["title"] == "Red jug"
    assert fields["caption"] == "Figure 3. Red earthenware jug, side view."
    assert fields["heading"] == "The red jug"
    assert "it holds two litres" in fields["nearby"] and "made in Delft" in fields["nearby"]
    assert "glaze is cracked" in fields["nearby"], "a paragraph that refers to Figure 3 is kept"
    assert "Menu text" not in json.dumps(fields) and "not text" not in json.dumps(fields)
    assert fields["summary"] == "A museum record of a red jug." and "Earthenware jug." in fields["api"]


def test_page_text_without_a_matching_picture():
    fields = review_pack.extract_page_text(PAGE, ("https://elsewhere.example/totally-other-99999999.jpg",))
    assert "alt" not in fields and "caption" not in fields and "nearby" not in fields
    assert fields["heading"] == "Collection highlights" and fields["summary"]


def test_commons_pages_use_the_api():
    assert review_pack.commons_title("https://commons.wikimedia.org/wiki/File:Red_jug.jpg") == "File:Red jug.jpg"
    assert review_pack.commons_title("https://museum.example/wiki/File:x.jpg") == ""


# ----------------------------------------------------------------- polite downloads

def test_robots_txt_is_obeyed_and_sites_are_paced():
    web, sleeps = FakeWeb(), []
    p = polite(web, sleeps)
    with pytest.raises(review_pack.Refused):
        p.get("https://museum.example/private/2")
    assert "https://museum.example/private/2" not in web.asked, "a forbidden page is never asked for"
    assert p.get("https://museum.example/object/1").startswith(b"<html>")
    p.get("https://museum.example/object/1")
    assert web.asked.count("https://museum.example/robots.txt") == 1, "robots.txt is read once per site"
    assert sleeps and all(s <= review_pack.PER_SITE_SECONDS for s in sleeps) and \
        sum(sleeps) >= 2 * review_pack.PER_SITE_SECONDS - 0.01, "one request every few seconds per site"
    with pytest.raises(review_pack.Refused):
        p.get("https://other.example/pictures/only-address-55555555.jpg")


def test_a_site_that_refuses_robots_txt_is_not_fetched():
    p = polite(lambda url, headers=None: (403, b"", {}))
    assert not p.allowed("https://closed.example/page")


def test_a_stopped_download_carries_on(tmp_path):
    data = b"0123456789" * 50
    import hashlib
    target = str(tmp_path / "needs-x.v1.zip")
    with open(target + ".part", "wb") as f:
        f.write(data[:200])                            # what came before the stop
    asked = []

    def opener(url, headers=None):
        """Answers a Range request with the rest (206)."""
        asked.append(headers)
        start = int(headers["Range"].split("=")[1].rstrip("-")) if headers else 0
        return (206 if start else 200), data[start:], {}
    review_pack.download_resumable("https://x/needs-x.v1.zip", target, len(data), hashlib.sha256(data).hexdigest(),
                                   opener)
    assert asked == [{"Range": "bytes=200-"}] and open(target, "rb").read() == data


# ----------------------------------------------------------------- the needs zip as a workspace

def test_a_needs_zip_opens_as_a_review_workspace(tmp_path):
    zip_path = needs_zip(str(tmp_path / "needs-test.v1.zip"), ROWS, {"jug.jpg": jpeg(10), "boys.jpg": jpeg(200)})
    folder = str(tmp_path / "ws")
    summary = needs_workspace.open_needs_zip(zip_path, folder)
    assert "2 new pictures" in summary and "1 picture comes with only an address" in summary, summary
    ws = describe_package.open_workspace(folder)
    assert describe_package.is_review(ws) and ws.data["never_for_picture_making"] is True
    assert {ws.entry(n)["status"] for n in ws.pictures} == {"new"}
    assert ws.entry("jug.jpg")["page_url"] == "https://museum.example/object/1"
    assert "title: Jug" in ws.entry("jug.jpg")["notes"] and ws.entry("boys.jpg")["child"] == "yes"
    rows, _problems, _summary = own_data.check_folder(folder)
    assert rows == [], "nothing is trained on before a person describes and checks it"
    describe_package.describe(ws, "boys.jpg", "Two boys sit on a stone wall by the sea.", "Mark")
    rows, _problems, _summary = own_data.check_folder(folder)
    assert rows == [], "described is not enough in a review collection"
    describe_package.mark_checked(ws, "boys.jpg", "Anna")
    rows, _problems, _summary = own_data.check_folder(folder)
    assert len(rows) == 1 and rows[0]["child"] is True and rows[0]["source"] == "review"
    rows, _problems, _summary = own_data.check_folder(folder, review=False)
    assert rows == [], "never used for picture-making"


def test_export_has_every_field(tmp_path):
    zip_path = needs_zip(str(tmp_path / "needs-test.v1.zip"), ROWS[:1], {"jug.jpg": jpeg(10)})
    folder = str(tmp_path / "ws")
    needs_workspace.open_needs_zip(zip_path, folder)
    out = str(tmp_path / "out.jsonl")
    needs_workspace.export_jsonl(folder, out)
    row = json.loads(open(out, encoding="utf-8").readline())
    assert tuple(row) == needs_workspace.EXPORT_FIELDS
    assert row["source"] == "test" and row["hints"] == {"title": "Jug", "text": "Jug."} and row["status"] == "new"
    assert row["licence"] == "CC0" and row["category"] == "open" and row["place"] == "Delft, Netherlands"


# ----------------------------------------------------------------- the review pack

def test_the_review_pack_format_and_carrying_on(tmp_path):
    zips = tmp_path / "zips"
    zips.mkdir()
    needs_zip(str(zips / "needs-test.v1.zip"), ROWS, {"jug.jpg": jpeg(10), "boys.jpg": jpeg(200)})
    web = FakeWeb()
    folder = str(tmp_path / "Review pack")
    said = []
    text = review_pack.build(folder, ["all"], str(zips), drafts=False, polite=polite(web), report=said.append)
    assert text.startswith("Finished") and "2 pictures" in text, text
    ws = describe_package.open_workspace(folder)
    assert describe_package.is_review(ws) and {ws.entry(n)["status"] for n in ws.pictures} == {"new"}
    jug = ws.entry("jug.jpg")
    assert jug["page_text"]["alt"] == "A red jug with a white handle"
    assert jug["page_text"]["caption"].startswith("Figure 3") and jug["page_text_sources"]["alt"].endswith("/1")
    assert ws.entry("boys.jpg")["page_text_done"].startswith("refused by robots.txt")
    problems = open(os.path.join(folder, review_pack.PROBLEMS_FILE), encoding="utf-8").read()
    assert "robots.txt" in problems and "only-address" in problems
    assert "https://other.example/pictures/only-address-55555555.jpg" not in web.asked, "robots.txt said no"
    exported = [json.loads(line) for line in open(os.path.join(folder, review_pack.EXPORT_FILE), encoding="utf-8")]
    assert {r["file"] for r in exported} == {"jug.jpg", "boys.jpg"}
    assert next(r for r in exported if r["file"] == "jug.jpg")["page_text"]["heading"] == "The red jug"
    readme = open(os.path.join(folder, review_pack.README_FILE), encoding="utf-8").read()
    assert "your own computers only" in readme and "Do not upload" in readme
    with zipfile.ZipFile(folder + ".zip") as z:
        names = z.namelist()
    assert "describing.json" in names and "jug.jpg" in names and review_pack.EXPORT_FILE in names
    assert not any(n.startswith((review_pack.PAGE_CACHE, review_pack.DOWNLOADS)) for n in names), names

    # Started again (as after a stop): nothing is fetched again and no picture is added twice.
    asked = len(web.asked)
    text = review_pack.build(folder, ["all"], str(zips), drafts=False, polite=polite(web), report=said.append)
    assert text.startswith("Finished") and "2 pictures" in text, text
    assert len(web.asked) == asked + 0, "pages already read are not fetched again"


def test_review_pack_lists_collections_with_sizes():
    lines = review_pack.list_lines({"loc_fsa": {"count": 1200, "size": 380_000_000, "category": "open",
                                                "date": "2026-11-18"}})
    assert lines == ["loc_fsa: 1,200 pictures, 380 MB, open, 2026-11-18"]


# ----------------------------------------------------------------- the windows

wx = pytest.importorskip("wx")


@pytest.fixture
def dialog(monkeypatch, tmp_path):
    """The Build a review pack window, without speaking or timers, with its settings in tmp_path."""
    for name in ("APPDATA", "LOCALAPPDATA", "HOME", "USERPROFILE"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    os.makedirs(tmp_path / "home", exist_ok=True)
    app = wx.GetApp() or wx.App(False)
    import training_wizard
    monkeypatch.setattr(training_wizard, "speak", lambda *a, **k: None)
    import dataset_preparation
    main = dataset_preparation.PrepareWindow()
    main.timer.Stop()
    d = dataset_preparation.ReviewPackDialog(main)
    d.timer.Stop()
    yield d
    for w in [w for w in wx.GetTopLevelWindows() if w]:
        w.Destroy()
    for _ in range(3):
        wx.Yield()
    assert app


def test_the_review_pack_window_is_accessible(dialog):
    from test_accessibility import assert_accessible
    assert_accessible(dialog)
    assert_accessible(dialog.parent)            # the main window's new button keeps its letters unique


def test_the_review_pack_window_keys(dialog, monkeypatch):
    import dataset_preparation
    import training_wizard
    from test_accessibility import assert_keys
    monkeypatch.setattr(training_wizard, "resource", lambda *a: __file__)
    monkeypatch.setattr(dataset_preparation.wizard, "resource", lambda *a: __file__)
    closed = []
    monkeypatch.setattr(dialog, "Close", lambda *a: closed.append(True))
    assert_keys(dialog, monkeypatch, lambda w: bool(closed))


def test_the_review_pack_window_says_what_to_do_first(dialog, tmp_path):
    said = []
    dialog.say = lambda text, *a, **k: said.append(text)
    dialog.folder.SetValue(str(tmp_path / "pack"))
    dialog.on_build(None)
    assert "Tick at least one collection" in said[-1]
    zips = tmp_path / "zips"
    zips.mkdir()
    needs_zip(str(zips / "needs-test.v2.zip"), ROWS[:1], {"jug.jpg": jpeg(10)})
    dialog.fill_from_folder(str(zips))
    assert dialog.keys == ["test"] and dialog.collections.GetCount() == 1
    dialog.zips.SetValue(str(zips))
    dialog.collections.Check(0)
    args = dialog.arguments()
    assert args[:4] == [str(tmp_path / "pack"), "review-pack", "--keys", "test"]
    assert args[args.index("--engines") + 1] == "qwen,internvl" and args[args.index("--zips") + 1] == str(zips)


def test_describe_pictures_shows_the_page_text(dialog, tmp_path):
    import describe_window
    entry = {"hint": "title: Jug", "page_text": {"alt": "A red jug", "caption": "Figure 3."},
             "page_url": "https://museum.example/object/1", "licence": "CC0"}
    text = describe_window.DescribeWindow.collection_text(entry)
    assert "Alt text on its web page: A red jug" in text and "Caption on its web page: Figure 3." in text
    assert "The collection's notes: title: Jug" in text and "Licence: CC0" in text
    assert describe_window.DescribeWindow.collection_text({}) == "Nothing."


def test_pictures_with_only_an_address_are_fetched_politely(tmp_path):
    """A picture whose collection gives only its address is downloaded from a site whose robots.txt allows it, gets
    its entry fields and a copy in the Picture Library."""
    picture = jpeg(77)
    row = dict(ROWS[2], url="https://open.example/pics/only-address-55555555.jpg", source="test")

    def web(url, headers=None):
        """robots.txt allows everything; the picture is there."""
        if url.endswith("/robots.txt"):
            return 200, b"User-agent: *\nAllow: /\n", {}
        return (200, picture, {}) if url == row["url"] else (404, b"", {})
    zip_path = needs_zip(str(tmp_path / "needs-test.v1.zip"), [row], {})
    folder, library = str(tmp_path / "ws"), str(tmp_path / "library")
    summary = needs_workspace.open_needs_zip(zip_path, folder, fetch=polite(web).get, library=library)
    assert "1 picture downloaded" in summary, summary
    ws = describe_package.open_workspace(folder)
    (name,) = list(ws.pictures)
    assert ws.entry(name)["source_url"] == row["url"] and ws.entry(name)["licence"] == "CC BY 2.0"
    assert os.path.exists(os.path.join(library, "needs-description", "test", name))
    assert needs_workspace.pending(folder) == []
