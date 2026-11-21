"""Tests of the "Personal use: everything allowed" switch (wizard/training_wizard.py) and of the sign-up collections
(kit/signup_sources.py): which collections the switch ticks and the total download size, unticking puts the boxes
back, the switch is remembered; each sign-up entry is skipped cleanly without its key or files and works with them;
the key file stays in the user's own settings folder and no key is ever said.
Every record, key and picture here is made up: nothing is downloaded from the internet.

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests     (on Windows: python -m pytest -q training-kit\\tests)
"""

import io
import json
import os
import sys
import tarfile
import types
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
for part in ("wizard", "kit"):
    sys.path.insert(0, os.path.join(KIT, part))

import sources  # noqa: E402
import signup_sources as su  # noqa: E402

FAKE_KEY = "made-up-key-123"


@pytest.fixture(autouse=True)
def private_home(tmp_path, monkeypatch):
    """Each test has its own settings folder and user folder, no real keys, and collects what the kit says."""
    for name in ("APPDATA", "USERPROFILE", "HOME"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    for name in su.SIGNUP_KEYS:
        monkeypatch.delenv(name, raising=False)
    said = []
    monkeypatch.setattr(sources, "say", said.append)
    return said


def picture_bytes(colour=(200, 30, 30)):
    """A made-up 120 by 100 JPEG."""
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (120, 100), colour).save(out, "JPEG")
    return out.getvalue()


def source(key):
    """A sign-up Source by key."""
    return next(s for s in su.SIGNUP_SOURCES if s.key == key)


# ----------------------------------------------------------------- the switch's selection logic

def fake_sources(signup_ready=lambda s: True):
    """A made-up sources module: one collection of each group and content."""
    S = sources.Source
    rows = [S("open1", "Open", "", "", "permissive", 10, 1, None, "1 GB"),
            S("sa1", "Share-alike", "", "", "share-alike", 10, 1, None, "2 GB"),
            S("nc1", "Non-commercial", "", "", "noncommercial", 10, 1, None, "about 500 MB of pictures"),
            S("rs1", "Research", "", "", "research", 10, 1, None, "1.5 GB"),
            S("rs_people", "Research people", "", "", "research", 10, 1, None, "1 GB"),
            S("nc_graphic", "Graphic", "", "", "noncommercial", 10, 1, None, "3 GB", content="graphic"),
            S("signup1", "Sign-up", "", "", "research", 10, 1, None, "4 GB")]
    return types.SimpleNamespace(SOURCES=rows, NOT_FOR_PICTURE_MAKING=("rs_people", "nc_graphic"),
                                 PERSONAL_PICTURE_MAKING_OK={"nc1", "rs_people"}, signup_ready=signup_ready)


def test_the_switch_ticks_share_alike_noncommercial_research_but_not_content_choices():
    import training_wizard as tw
    module = fake_sources()
    added, waiting = tw.everything_collections(module, "describer", {""})
    assert [s.key for s in added] == ["sa1", "nc1", "rs1", "rs_people", "signup1"]
    assert not waiting
    # The graphic collection only comes with its own choice (the switch never ticks it).
    added, _ = tw.everything_collections(module, "describer", {"", "graphic"})
    assert "nc_graphic" in [s.key for s in added]


def test_the_switch_leaves_out_signup_collections_without_a_key():
    import training_wizard as tw
    module = fake_sources(signup_ready=lambda s: s.key != "signup1")
    added, waiting = tw.everything_collections(module, "describer", {""})
    assert "signup1" not in [s.key for s in added]
    assert [s.key for s in waiting] == ["signup1"]


def test_the_switch_respects_picture_making_rules():
    import training_wizard as tw
    added, _ = tw.everything_collections(fake_sources(), "pictures", {""})
    # rs_people is NOT_FOR_PICTURE_MAKING (even though in PERSONAL_PICTURE_MAKING_OK); rs1 and signup1 are not OK.
    assert [s.key for s in added] == ["sa1", "nc1"]


def test_the_total_download_size():
    import training_wizard as tw
    assert tw.parse_size("7.6 GB") == int(7.6 * 1024 ** 3)
    assert tw.parse_size("up to about 400 MB of pictures") == 400 * 1024 ** 2
    assert tw.parse_size("several files") == 0
    text = tw.everything_text(fake_sources(), "describer", {""})
    assert "5 collections" in text and "about 9.0 gigabytes" in text     # 2 + 0.5 + 1.5 + 1 + 4 GB
    assert "never publish" in text.lower() or "Never publish" in text
    assert "forbid selling" in text


def test_unticking_restores_the_previous_ticks():
    import training_wizard as tw
    before = {"wikipedia": False, "noncommercial": True, "research": False}
    assert tw.everything_on(before) == {"wikipedia": True, "noncommercial": True, "research": True}
    assert tw.everything_off(before) == before
    assert tw.everything_off(None) == {"wikipedia": False, "noncommercial": False, "research": False}


@pytest.fixture
def wizard(monkeypatch):
    """The wizard's window, silent, with the switch's window answered by monkeypatch."""
    wx = pytest.importorskip("wx")
    import training_wizard as tw
    app = wx.GetApp() or wx.App(False)
    monkeypatch.setattr(tw, "speak", lambda *a, **k: None)
    monkeypatch.setattr(tw, "SETTINGS_FILE", os.path.join(os.environ["APPDATA"], "Picture Model Training",
                                                           "settings.json"))
    monkeypatch.setattr(tw, "log", lambda *a, **k: None)
    w = tw.Wizard()
    w.timer.Stop()
    yield w
    w.Destroy()
    del app


def test_the_switch_in_the_window_ticks_restores_and_is_remembered(wizard, monkeypatch):
    import wx
    import training_wizard as tw
    wizard.noncommercial.SetValue(True)
    monkeypatch.setattr(tw.EverythingDialog, "ShowModal", lambda self: wx.ID_OK)
    wizard.everything_box.SetValue(True)
    wizard.on_everything(None)
    assert wizard.boxes() == {"wikipedia": True, "noncommercial": True, "research": True}
    assert not wizard.nudity.GetValue() or wizard.nudity.GetValue() == wizard.content["describer"]["nudity"]
    # Remembered: Start saves it (the work itself is not started here).
    monkeypatch.setattr(tw, "check_computer", lambda *a: (["ok"], True))
    monkeypatch.setattr(tw.threading, "Thread", lambda *a, **k: types.SimpleNamespace(start=lambda: None))
    wizard.on_start(None)
    saved = tw.load_choices()
    assert saved["everything_describer"] is True
    assert saved["before_everything_describer"] == {"wikipedia": False, "noncommercial": True, "research": False}
    # Unticking puts the boxes back.
    wizard.everything_box.SetValue(False)
    wizard.on_everything(None)
    assert wizard.boxes() == {"wikipedia": False, "noncommercial": True, "research": False}


def test_the_switch_cancelled_changes_nothing(wizard, monkeypatch):
    import wx
    import training_wizard as tw
    monkeypatch.setattr(tw.EverythingDialog, "ShowModal", lambda self: wx.ID_CANCEL)
    wizard.everything_box.SetValue(True)
    wizard.on_everything(None)
    assert not wizard.everything_box.GetValue()
    assert wizard.boxes() == {"wikipedia": False, "noncommercial": False, "research": False}


def test_unticking_a_box_by_hand_turns_the_switch_off(wizard, monkeypatch):
    import wx
    import training_wizard as tw
    monkeypatch.setattr(tw.EverythingDialog, "ShowModal", lambda self: wx.ID_OK)
    wizard.everything_box.SetValue(True)
    wizard.on_everything(None)
    wizard.noncommercial.SetValue(False)
    wizard.on_noncommercial(None)
    assert not wizard.everything_box.GetValue()


# ----------------------------------------------------------------- the keys

def test_keys_come_from_the_environment_then_the_key_file(monkeypatch, tmp_path):
    assert su.get_key("DVIDS_API_KEY") == ""
    assert su.save_key_file({"DVIDS_API_KEY": FAKE_KEY, "NOT_A_KEY": "x", "KAGGLE_KEY": ""})
    path = su.key_file()
    assert path.startswith(str(tmp_path / "home")) and "Picture Model Training" in path
    assert json.load(open(path, encoding="utf-8")) == {"DVIDS_API_KEY": FAKE_KEY}
    assert su.get_key("DVIDS_API_KEY") == FAKE_KEY
    monkeypatch.setenv("DVIDS_API_KEY", "from-windows")
    assert su.get_key("DVIDS_API_KEY") == "from-windows"


def test_the_key_file_feeds_the_other_kit_entries(monkeypatch):
    su.save_key_file({"EUROPEANA_KEY": FAKE_KEY, "DPLA_API_KEY": FAKE_KEY})
    monkeypatch.setenv("DPLA_API_KEY", "already-set")
    copied = su.use_key_file()
    assert copied == ["EUROPEANA_KEY"]
    assert os.environ["EUROPEANA_KEY"] == FAKE_KEY and os.environ["DPLA_API_KEY"] == "already-set"
    monkeypatch.delenv("EUROPEANA_KEY")


def test_kaggle_json_is_read(tmp_path):
    folder = tmp_path / "home" / ".kaggle"
    folder.mkdir(parents=True)
    (folder / "kaggle.json").write_text(json.dumps({"username": "someone", "key": FAKE_KEY}))
    assert su.get_key("KAGGLE_USERNAME") == "someone" and su.get_key("KAGGLE_KEY") == FAKE_KEY


def test_every_entry_explains_itself_once_and_never_says_a_key(tmp_path, private_home):
    su.save_key_file({"DVIDS_API_KEY": FAKE_KEY})
    s = source("dvids_us")
    assert su.explain_once(s, str(tmp_path / "data"))
    text = " ".join(private_home)
    assert "api.dvidshub.net" in text and "free for commercial use" in text and "What it adds" in text
    assert FAKE_KEY not in text
    assert not su.explain_once(s, str(tmp_path / "data"))
    for entry in su.SIGNUP_SOURCES:
        info = su.SIGNUP_INFO[entry.key]
        assert info["where"] and info["terms"] and info["terms_url"].startswith("https://") and info["adds"]
        assert entry.group in ("research", "noncommercial")
    assert FAKE_KEY not in su.keys_text() and "Never paste a key" in su.keys_text()


@pytest.mark.parametrize("key", ["dvids_us", "dvids_caf", "kaggle_chess"])
def test_entries_without_a_key_are_skipped_cleanly(key, tmp_path, private_home):
    s = source(key)
    assert not su.ready(s)
    assert s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), 50) == []
    assert any("left out" in line for line in private_home)


def test_flickr30k_without_files_is_skipped_cleanly(tmp_path, private_home):
    s = source("flickr30k")
    assert not su.ready(s)
    assert s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), 50) == []
    assert any("left out" in line for line in private_home)


def test_signup_collections_are_wired_into_sources():
    keys = {s.key for s in sources.SOURCES}
    assert {s.key for s in su.SIGNUP_SOURCES} <= keys
    assert all(s.key in sources.NOT_FOR_PICTURE_MAKING for s in su.SIGNUP_SOURCES)
    assert sources.signup_ready(next(s for s in sources.SOURCES if s.group == "permissive"))


# ----------------------------------------------------------------- DVIDS with a key (made-up answers)

def dvids_fake(records):
    """A made-up DVIDS API: search gives the ids, asset gives each record."""
    calls = []

    def get(url, params):
        """The made-up answer to one request."""
        calls.append((url, dict(params)))
        assert params["api_key"] == FAKE_KEY
        if url.endswith("search"):
            return {"results": [{"id": f"image:{r['n']}", "type": "image"} for r in records]}
        n = int(params["id"].split(":")[1])
        return {"results": next(r["record"] for r in records if r["n"] == n)}
    return get, calls


def test_dvids_reads_captions_and_leaves_out_ceremonies_and_detainees():
    records = [
        {"n": 1, "record": {"title": "Flood relief", "description": "Soldiers load sandbags onto a truck beside a "
                            "flooded road during relief work. (U.S. Army photo by Sgt. Ann Example)",
                            "image": "https://example.org/1.jpg", "unit_name": "1st Brigade",
                            "location": {"city": "Tulsa", "state": "Oklahoma", "country": "United States"},
                            "credit": [{"rank": "Sgt.", "name": "Ann Example"}], "url": "https://example.org/1"}},
        {"n": 2, "record": {"title": "Change of command", "description": "Officers stand during the change of "
                            "command ceremony on the parade field.", "image": "https://example.org/2.jpg"}},
        {"n": 3, "record": {"title": "Detainee", "description": "A detainee is processed at the facility by the "
                            "military police.", "image": "https://example.org/3.jpg"}},
        {"n": 4, "record": {"title": "Exercise", "description": "Canadian Armed Forces members cross a frozen lake "
                            "on snowshoes during a winter exercise.", "image": "https://example.org/4.jpg",
                            "unit_name": "Canadian Armed Forces Combat Camera"}},
    ]
    get, calls = dvids_fake(records)
    items = su.dvids_items(FAKE_KEY, False, 2, 1, get=get, pause=0)
    rows = [r for _n, _u, r in items]
    assert {n for n, _u, _r in items} == {"dvids-1.jpg"}
    assert rows[0]["answer"].startswith("Soldiers load sandbags") and "photo by" not in rows[0]["answer"]
    assert "Tulsa" in rows[0].get("place", "") or any("Tulsa" in str(r) for r in rows)
    get, _ = dvids_fake(records)
    caf = su.dvids_items(FAKE_KEY, True, 2, 1, get=get, pause=0)
    assert {n for n, _u, _r in caf} == {"dvids-4.jpg"}


def test_dvids_with_a_key_fetches_pictures(tmp_path, monkeypatch):
    su.save_key_file({"DVIDS_API_KEY": FAKE_KEY})
    s = source("dvids_us")
    assert su.ready(s)
    seen = {}

    def items(key, canadian, want, seed):
        seen["key"] = key
        return [("dvids-1.jpg", "https://example.org/1.jpg", {"question": "Describe this picture.",
                                                              "answer": "A made-up caption of six words or more.",
                                                              "split": ""})]
    monkeypatch.setattr(su, "dvids_items", items)
    import more_sources
    monkeypatch.setattr(more_sources, "fetch_shared",
                        lambda items, folder, workers=8: [dict(r, picture=os.path.join(folder, n)) for n, _u, r in items])
    rows = s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), 10)
    assert seen["key"] == FAKE_KEY and len(rows) == 1 and rows[0]["picture"].endswith("dvids-1.jpg")


# ----------------------------------------------------------------- Kaggle Chess Positions with a key

def test_chess_answer_reads_the_board():
    answer = su.chess_answer("train/1b1B1b2-2pK2q1-4p1rB-7k-8-8-3B4-3rb3.jpeg")
    assert answer.startswith("A diagram of a chess board with 13 pieces.")
    assert "White: king on d7; bishops on d2, d8 and h6." in answer
    assert "Black: king on h5; queen on g7" in answer
    assert su.chess_answer("readme.jpeg") == "" and su.chess_answer("9-8-8-8-8-8-8-8.jpeg") == ""


def test_kaggle_chess_with_a_key(tmp_path, monkeypatch):
    su.save_key_file({"KAGGLE_USERNAME": "someone", "KAGGLE_KEY": FAKE_KEY})
    s = source("kaggle_chess")
    assert su.ready(s)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("train/1b1B1b2-2pK2q1-4p1rB-7k-8-8-3B4-3rb3.jpeg", picture_bytes())
        z.writestr("test/8-8-8-4k3-8-8-8-4K3.jpeg", picture_bytes((10, 10, 10)))
        z.writestr("notes.txt", "not a picture")

    class Answer:
        """A made-up download answer."""
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def raise_for_status(self):
            """Fine."""

        def iter_content(self, size):
            """The made-up zip."""
            yield archive.getvalue()

    asked = {}

    def get(url, auth=None, **k):
        asked["url"], asked["auth"] = url, auth
        return Answer()
    path = str(tmp_path / "work" / "kaggle_chess" / "chess-positions.zip")
    assert su.kaggle_download(su.CHESS_DATASET, path, {"KAGGLE_USERNAME": "someone", "KAGGLE_KEY": FAKE_KEY},
                              get=get)
    assert asked["auth"] == ("someone", FAKE_KEY) and asked["url"].endswith("koryakinp/chess-positions")
    rows = s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), 10)
    assert len(rows) == 2
    assert {r["split"] for r in rows} == {"", "test"}
    assert all(os.path.exists(r["picture"]) and r["question"] == su.CHESS_QUESTION for r in rows)
    assert any("White: king on e1." in r["answer"] for r in rows)


# ----------------------------------------------------------------- Flickr30k with the owner's files

def test_flickr30k_with_files(tmp_path):
    s = source("flickr30k")
    folder = su.signup_folder("flickr30k")
    token = ("100.jpg#0\tA man rides a bicycle down a busy city street .\n"
             "100.jpg#1\tA cyclist in a red jacket rides past parked cars on a street .\n"
             "200.jpg#0\tA little girl plays with a dog in the yard .\n"
             "300.jpg#0\tToo short .\n")
    captions = io.BytesIO()
    with tarfile.open(fileobj=captions, mode="w:gz") as t:
        data = token.encode()
        info = tarfile.TarInfo("flickr30k/results_20130124.token")
        info.size = len(data)
        t.addfile(info, io.BytesIO(data))
    open(os.path.join(folder, "flickr30k.tar.gz"), "wb").write(captions.getvalue())
    images = io.BytesIO()
    with tarfile.open(fileobj=images, mode="w:gz") as t:
        for name in ("100.jpg", "200.jpg", "300.jpg"):
            data = picture_bytes()
            info = tarfile.TarInfo(f"flickr30k-images/{name}")
            info.size = len(data)
            t.addfile(info, io.BytesIO(data))
    open(os.path.join(folder, "flickr30k-images.tar.gz"), "wb").write(images.getvalue())
    assert su.ready(s)
    rows = s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), 10)
    by_answer = {r["answer"]: r for r in rows}
    assert "A cyclist in a red jacket rides past parked cars on a street ." in by_answer
    assert by_answer["A little girl plays with a dog in the yard ."]["child"] is True
    assert all(os.path.exists(r["picture"]) for r in rows) and len(rows) == 2
    # The originals were kept unchanged in the downloads folder.
    assert os.path.exists(tmp_path / "work" / "flickr30k" / "100.jpg")


# ----------------------------------------------------------------- Museums Victoria (made-up answers)

VICTORIA_RECORDS = [
    {"id": "items/1", "recordType": "item", "displayTitle": "Toaster - Sunbeam, 1950s",
     "physicalDescription": "Chrome electric toaster with two slots, black bakelite handles and a cloth cord.",
     "media": [{"type": "image", "licence": {"name": "Public Domain"}, "large": {"uri": "https://example.org/1.jpg"}}]},
    {"id": "items/2", "recordType": "item", "displayTitle": "Radio",
     "physicalDescription": "Wooden mantel radio with a round dial and two knobs on the front.",
     "media": [{"type": "image", "licence": {"name": "All Rights Reserved"}, "large": {"uri": "https://e.org/2.jpg"}}]},
    {"id": "items/3", "recordType": "item", "displayTitle": "Telephone",
     "physicalDescription": "Black bakelite telephone with a rotary dial and a coiled cord.",
     "media": [{"type": "image", "licence": {"name": "Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)"},
                "large": {"uri": "https://e.org/3.jpg"}}]},
    {"id": "items/4", "recordType": "item", "displayTitle": "Rifle",
     "physicalDescription": "Bolt action rifle with a wooden stock and a leather sling attached.",
     "media": [{"type": "image", "licence": {"name": "Public Domain"}, "large": {"uri": "https://e.org/4.jpg"}}]},
    {"id": "items/5", "recordType": "item", "displayTitle": "Kettle",
     "physicalDescription": "Electric kettle of polished aluminium with a black handle and a whistle.",
     "media": [{"type": "image", "licence": {"name": "Attribution 4.0 International (CC BY 4.0)"},
                "large": {"uri": "https://e.org/5.jpg"}}]},
]


def test_museums_victoria_takes_only_allowed_licences():
    calls = []
    items = su.victoria_items(10, 1, get=lambda url, params: calls.append(params) or (200, VICTORIA_RECORDS),
                              pause=0)
    names = {n for n, _u, _r in items}
    assert names == {"mv-items-1.jpg", "mv-items-5.jpg"}
    assert all(c["hasimages"] == "yes" for c in calls)


def test_museums_victoria_says_clearly_when_refused(tmp_path, private_home, monkeypatch):
    s = source("museums_victoria")

    def refused(want, seed, get=None, pause=3.0):
        raise su.Refused("Museums Victoria answered 403")
    monkeypatch.setattr(su, "victoria_items", refused)
    assert s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), 10) == []
    assert any("refused this computer" in line for line in private_home)


# ----------------------------------------------------------------- local-file entries (made-up downloads)

LOCAL_KEYS = ["lisa_traffic_lights", "lisa_traffic_signs", "bdd100k", "mapillary_signs", "mapillary_vistas",
              "deepfashion", "fastener_sets", "mvtec_d2s"]


def put_zip(key, zip_name, files):
    """A made-up download: a zip of {path: bytes or text} in the entry's sign-up folder."""
    path = os.path.join(su.signup_folder(key), zip_name)
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
    return path


def put_loose(key, files):
    """Made-up unpacked files {path: bytes or text} in the entry's sign-up folder."""
    for name, data in files.items():
        path = os.path.join(su.signup_folder(key), *name.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data.encode() if isinstance(data, str) else data)


def run(key, tmp_path, cap=10):
    """The entry's rows from the made-up files."""
    s = source(key)
    return s.prepare(s, str(tmp_path / "data"), str(tmp_path / "work"), cap)


@pytest.mark.parametrize("key", LOCAL_KEYS)
def test_local_entries_without_files_are_skipped_cleanly(key, tmp_path, private_home):
    s = source(key)
    assert not su.ready(s)
    assert run(key, tmp_path) == []
    assert any("left out" in line for line in private_home)
    info = su.SIGNUP_INFO[key]
    assert info["keys"] == [] and "sign-up files" in info["where"]


def test_local_entries_are_personal_and_never_for_picture_making():
    for key in LOCAL_KEYS:
        s = source(key)
        assert s.group in ("research", "noncommercial") and s.terms.startswith("https://")
        assert key in sources.NOT_FOR_PICTURE_MAKING and key in su.LOCAL_LABEL_FILES


def test_lisa_traffic_lights_from_the_kaggle_zip(tmp_path):
    box = ("Filename;Annotation tag;Upper left corner X;Upper left corner Y;Lower right corner X;Lower right corner Y\n"
           "dayTraining/dayClip1--00001.jpg;stop;1;2;3;4\n"
           "dayTraining/dayClip1--00001.jpg;stop;5;6;7;8\n"
           "dayTraining/dayClip1--00001.jpg;goLeft;5;6;7;8\n"
           "dayTraining/dayClip1--00002.jpg;go;1;2;3;4\n")
    night = ("Filename;Annotation tag;Upper left corner X\nnightTraining/nightClip1--00001.jpg;warning;1\n")
    put_zip("lisa_traffic_lights", "archive.zip", {
        "Annotations/Annotations/dayTrain/dayClip1/frameAnnotationsBOX.csv": box,
        "Annotations/Annotations/nightTrain/nightClip1/frameAnnotationsBOX.csv": night,
        "dayTrain/dayTrain/dayClip1/frames/dayClip1--00001.jpg": picture_bytes(),
        "dayTrain/dayTrain/dayClip1/frames/dayClip1--00002.jpg": picture_bytes(),
        "nightTrain/nightTrain/nightClip1/frames/nightClip1--00001.jpg": picture_bytes()})
    assert su.ready(source("lisa_traffic_lights"))
    answers = {r["answer"] for r in run("lisa_traffic_lights", tmp_path)}
    assert answers == {"The traffic lights marked in this photo: 2 red (stop) and 1 green left-turn arrow.",
                       "The traffic lights marked in this photo: 1 green (go).",
                       "The traffic lights marked in this photo: 1 yellow (about to turn red). It is night."}


def test_lisa_traffic_signs_unpacked(tmp_path):
    put_loose("lisa_traffic_signs", {
        "signDatabasePublicFramesOnly/allAnnotations.csv":
            "Filename;Annotation tag;Upper left corner X\n"
            "aiua120214-0/frameAnnotations-x/stop_1.png;stop;1\n"
            "aiua120214-0/frameAnnotations-x/stop_1.png;speedLimit35;1\n"
            "aiua120214-0/frameAnnotations-x/yield_2.png;yield;1\n",
        "signDatabasePublicFramesOnly/aiua120214-0/frameAnnotations-x/stop_1.png": picture_bytes(),
        "signDatabasePublicFramesOnly/aiua120214-0/frameAnnotations-x/yield_2.png": picture_bytes()})
    answers = {r["answer"] for r in run("lisa_traffic_signs", tmp_path)}
    assert answers == {"The road signs marked in this photo: a stop sign and a speed limit 35 sign.",
                       "The road signs marked in this photo: a yield sign."}
    assert su.camel_words("pedestrianCrossing") == "pedestrian crossing"


def test_bdd100k_attributes_things_and_lights(tmp_path):
    frames = [{"name": "b1.jpg", "attributes": {"weather": "rainy", "scene": "city street", "timeofday": "night"},
               "labels": [{"category": "car"}, {"category": "car"}, {"category": "person"},
                          {"category": "traffic light", "attributes": {"trafficLightColor": "red"}},
                          {"category": "traffic light", "attributes": {"trafficLightColor": "none"}}]},
              {"name": "b2.jpg", "attributes": {"weather": "undefined", "scene": "highway", "timeofday": "daytime"},
               "labels": []}]
    put_zip("bdd100k", "bdd100k_labels_images_trainval.zip",
            {"bdd100k/labels/bdd100k_labels_images_val.json": json.dumps(frames)})
    put_zip("bdd100k", "bdd100k_images_100k.zip", {"bdd100k/images/100k/val/b1.jpg": picture_bytes(),
                                                     "bdd100k/images/100k/val/b2.jpg": picture_bytes()})
    rows = run("bdd100k", tmp_path)
    got = {r["question"]: r["answer"] for r in rows}
    assert got[su.BDD_SCENE_Q] == "Night, rainy weather, on a city street."
    assert got[su.BDD_THINGS_Q] == "Marked in this photo: 2 cars, 1 person on foot and 2 traffic lights."
    assert got[su.LIGHT_Q] == "The traffic lights marked in this photo: 1 red."
    assert len({r["picture"] for r in rows}) == 1          # b2 has nothing to say


def test_mapillary_signs_and_vistas(tmp_path):
    put_zip("mapillary_signs", "mtsd_v2_fully_annotated_annotation.zip", {
        "mtsd_v2_fully_annotated/annotations/k1.json": json.dumps({"objects": [
            {"label": "regulatory--stop--g1"}, {"label": "warning--pedestrians-crossing--g4"},
            {"label": "other-sign"}]}),
        "mtsd_v2_fully_annotated/annotations/k2.json": json.dumps({"objects": [{"label": "other-sign"}]})})
    put_zip("mapillary_signs", "mtsd_v2_fully_annotated_images.train.0.zip",
            {"images/k1.jpg": picture_bytes(), "images/k2.jpg": picture_bytes()})
    answers = [r["answer"] for r in run("mapillary_signs", tmp_path)]
    assert answers == ["The traffic signs marked in this photo: stop sign (a rule) and pedestrians crossing sign "
                       "(a warning)."]
    config = {"labels": [{"name": "construction--flat--sidewalk", "readable": "Sidewalk"},
                         {"name": "object--vehicle--car", "readable": "Car"},
                         {"name": "void--ego-vehicle", "readable": "Ego Vehicle"}]}
    put_loose("mapillary_vistas", {
        "config_v2.0.json": json.dumps(config),
        "training/v2.0/polygons/v1.json": json.dumps({"objects": [
            {"label": "object--vehicle--car"}, {"label": "object--vehicle--car"},
            {"label": "construction--flat--sidewalk"}, {"label": "void--ego-vehicle"}]}),
        "training/images/v1.jpg": picture_bytes()})
    assert [r["answer"] for r in run("mapillary_vistas", tmp_path)] == [
        "Marked in this street photo: car and sidewalk."]


def test_deepfashion_categories(tmp_path):
    put_loose("deepfashion", {
        "Anno_coarse/list_category_cloth.txt": "3\ncategory_name  category_type\nBlouse 1\nTee 1\nJeans 2\n",
        "Anno_coarse/list_category_img.txt": "3\nimage_name  category_label\n"
                                             "img/Sheer_Blouse/img_00000001.jpg 1\n"
                                             "img/Graphic_Tee/img_00000002.jpg 2\n"
                                             "img/Skinny_Jeans/img_00000003.jpg 3\n"})
    put_zip("deepfashion", "img.zip", {"img/Sheer_Blouse/img_00000001.jpg": picture_bytes(),
                                       "img/Graphic_Tee/img_00000002.jpg": picture_bytes(),
                                       "img/Skinny_Jeans/img_00000003.jpg": picture_bytes()})
    assert {r["answer"] for r in run("deepfashion", tmp_path)} == {"This is a blouse.", "This is a T-shirt.",
                                                                    "These are jeans."}


def test_fastener_sets_by_folder(tmp_path):
    put_loose("fastener_sets", {"The Fasteners/bolt/1.jpg": picture_bytes(),
                                "The Fasteners/nut/2.jpg": picture_bytes(),
                                "SortScrews/train/hex_screw/3.jpg": picture_bytes(),
                                "SortScrews/train/4.jpg": picture_bytes(), "SortScrews/0/5.jpg": picture_bytes()})
    rows = run("fastener_sets", tmp_path)
    assert {r["answer"] for r in rows} == {"This is a bolt, as the set's makers sorted it.",
                                           "This is a nut, as the set's makers sorted it.",
                                           "This is a hex screw, as the set's makers sorted it."}
    assert any(r["credit"].startswith("SortScrews") for r in rows)


def test_mvtec_d2s_products(tmp_path):
    coco = {"categories": [{"id": 1, "name": "avocado"}, {"id": 2, "name": "coca_cola_bottle"}],
            "images": [{"id": 7, "file_name": "D2S_000200.jpg"}],
            "annotations": [{"image_id": 7, "category_id": 1}, {"image_id": 7, "category_id": 1},
                            {"image_id": 7, "category_id": 2}]}
    put_loose("mvtec_d2s", {"annotations/D2S_training.json": json.dumps(coco),
                            "images/D2S_000200.jpg": picture_bytes()})
    assert [r["answer"] for r in run("mvtec_d2s", tmp_path)] == [
        "The products marked in this photo: avocado (2) and coca cola bottle (1)."]
