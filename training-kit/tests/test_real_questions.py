"""Tests of the real-questions test (kit/real_questions.py): VizWiz's scoring with made-up answers, the "said
unanswerable when it should" check, the topic and question-type rules, the privacy rules, the shipped question list,
leaving its pictures out of training, the downloads (with a made-up server), the reports, train.py's --evaluate, and
the Topic add-ons window's "Test on real questions" button. Nothing here downloads anything or needs a graphics
card; every answer, picture and server reply is made up."""

import json
import os
import sys
import zlib

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kit")
sys.path.insert(0, KIT)
import real_questions as rq  # noqa: E402
import topics  # noqa: E402


def vizwiz_row(answers, answerable=1, topic="food", **extra):
    """A made-up VizWiz row with these ten answers."""
    return {"id": extra.pop("id", "vizwiz-test-1"), "source": "vizwiz", "image": "VizWiz_test_00000001.jpg",
            "question": extra.pop("question", "What is this?"), "answers": answers, "answerable": answerable,
            "topic": topic, "kind": "what", "licence": rq.LICENCE, **extra}


# ----------------------------------------------------------------- scoring

def test_the_official_tidying():
    assert rq.normalise("Two Cans.") == "2 cans"
    assert rq.normalise("The Coke") == "coke"
    assert rq.normalise("dont know") == "don't know"
    assert rq.normalise("1,000") == "1000"
    assert rq.normalise("3.5") == "3.5"
    assert rq.normalise("red-white") == "red white"


@pytest.mark.parametrize("same, score", [(10, 1.0), (4, 1.0), (3, 0.9), (2, 0.6), (1, 0.3), (0, 0.0)])
def test_vizwiz_accuracy_counts_agreeing_people(same, score):
    """An answer three or more of the others gave scores 1; averaged over leaving each person out."""
    people = ["corn flakes"] * same + [f"other {i}" for i in range(10 - same)]
    assert rq.vizwiz_accuracy("Corn Flakes.", people) == pytest.approx(score)


def test_giving_up_is_scored_as_unanswerable():
    row = vizwiz_row(["unanswerable"] * 8 + ["blurry", "coke"], answerable=0)
    for answer in ("Unanswerable", "I can't tell from this picture.", "The label is too blurry to read.",
                   "I cannot read the text."):
        assert rq.said_unanswerable(answer), answer
        scores = rq.score_row(row, answer)
        assert scores["accuracy"] == pytest.approx(1.0) and scores["should_give_up"] and scores["gave_up"]
    scores = rq.score_row(row, "Coca-Cola")
    assert scores["accuracy"] < 0.4 and not scores["gave_up"]
    assert not rq.said_unanswerable("Corn flakes")


def test_giving_up_on_an_answerable_question_scores_nothing():
    scores = rq.score_row(vizwiz_row(["corn flakes"] * 10), "Unanswerable")
    assert scores == {"accuracy": 0.0, "contains": 0.0, "should_give_up": False, "gave_up": True}


def test_the_kinder_contains_check():
    """A sentence holding what at least two people said counts for "contains", not for accuracy."""
    row = vizwiz_row(["corn flakes"] * 2 + ["cereal"] * 2 + [f"x{i}" for i in range(6)])
    scores = rq.score_row(row, "This is a box of Kellogg's Corn Flakes cereal.")
    assert scores["contains"] == 1.0 and scores["accuracy"] == 0.0
    assert rq.score_row(row, "A box of flakes")["contains"] == 0.0


def test_orbit_rows_score_naming_the_thing():
    row = {"id": "orbit-1", "source": "orbit", "image": "P1--keys--clean--v-00001.jpg", "question": "What is this?",
           "answers": ["keys", "key"], "answerable": 1, "topic": "everyday", "kind": "what"}
    assert rq.score_row(row, "A set of house keys.")["accuracy"] == 1.0
    assert rq.score_row(row, "A keyboard")["accuracy"] == 0.0           # whole words only
    assert rq.score_row(row, "I can't tell")["accuracy"] == 0.0


def test_summary_and_plain_words():
    rows = [dict(vizwiz_row(["coke"] * 10, id=f"a{i}", topic="drinks"), **rq.score_row(vizwiz_row(["coke"] * 10), a),
                 model_answer=a) for i, a in enumerate(["Coke", "Pepsi"])]
    rows.append(dict(vizwiz_row(["unanswerable"] * 10, 0, id="u", topic="drinks"),
                     **rq.score_row(vizwiz_row(["unanswerable"] * 10, 0), "Unanswerable"), model_answer="Unanswerable"))
    s = rq.summarise(rows)
    assert s["drinks"]["questions"] == 3 and s["drinks"]["accuracy"] == pytest.approx(2 / 3)
    assert s["drinks"]["should"] == 1 and s["drinks"]["gave_up_right"] == 1 and s["all"]["questions"] == 3
    text = "\n".join(rq.report_lines("the 4B model itself", rows))
    assert "Drinks (no alcohol) (3 questions): accuracy 0.67" in text
    assert "Of 1 questions the photo could not answer, it said so for 1 (100 percent)" in text
    assert "VizWiz VQA" in text and "CC BY 4.0" in text


def test_the_topic_report_compares_before_and_after():
    topic = topics.find("medicines")

    def scored(answer, n=4):
        return [dict(vizwiz_row(["tylenol"] * 10, id=f"m{i}", topic=t), model_answer=answer,
                     **rq.score_row(vizwiz_row(["tylenol"] * 10), answer)) for i in range(n)
                for t in ("medicines", "everyday", "home_tests")]
    lines = rq.compare_lines(topic, scored("aspirin"), scored("Tylenol"))
    text = "\n".join(lines)
    assert "On this topic (4 questions): accuracy before 0.00, after 1.00: better." in text
    assert "On home health tests" in text and "On everyday questions" in text
    lines = rq.compare_lines(topics.find("firearms"), scored("x"), scored("y"))
    assert "This topic has no real questions yet" in "\n".join(lines)
    summaries = rq.compare_lines(topic, rq.summarise(scored("aspirin")), rq.summarise(scored("Tylenol")))
    assert summaries == lines[:0] + rq.compare_lines(topic, scored("aspirin"), scored("Tylenol"))


# ----------------------------------------------------------------- sorting into topics and kinds

@pytest.mark.parametrize("question, answers, topic", [
    ("What kind of pills are these?", ["tylenol"] * 3, "medicines"),
    ("What is this?", ["campbell's chicken noodle soup"] * 3, "food"),
    ("What is this?", ["coke"] * 3, "drinks"),
    ("What kind of wine is this?", ["merlot"] * 3, "alcohol"),
    ("Is my oven on?", ["yes"] * 3, "machines"),
    ("What does this letter say?", ["unanswerable"] * 3, "documents"),
    ("What color is my dog?", ["black"] * 3, "nature"),
    ("What is this a statue of?", ["horse"] * 3, "art"),
    ("What kind of cigarettes are these?", ["marlboro"] * 3, "drugs"),
    ("What does this pregnancy test show?", ["negative"] * 3, rq.HOME_TESTS),
    ("Does this test show one or two pink lines?", ["1"] * 3, rq.HOME_TESTS),
    ("Are there any red lines on the screen?", ["no"] * 3, "documents"),
    ("What color is this shirt?", ["blue"] * 3, rq.EVERYDAY),
    ("What company makes this?", ["glue gun"] * 3, rq.EVERYDAY),        # firearms needs a word in the question
    ("What is the title of this book?", ["cats"] * 3, "documents"),     # a book's title is reading, not nature
    ("What is this?", ["apple tv remote"] * 3, "machines"),
])
def test_topic_rules(question, answers, topic):
    assert rq.classify_topic(question, answers) == topic


@pytest.mark.parametrize("question, topic, kind", [
    ("What is the expiration date?", "food", "expiry"),
    ("What denomination is this bill?", "everyday", "money"),
    ("Is the light on or off?", "machines", "on_off"),
    ("Which button is start?", "machines", "button"),
    ("What color is this?", "everyday", "colour"),
    ("How many calories are in this?", "food", "amount"),
    ("What does this say?", "documents", "read"),
    ("What is this?", "food", "what"),
    ("What is this?", "medicines", "medicine"),
    ("What is the label on this jar?", "food", "read"),
])
def test_question_kinds(question, topic, kind):
    assert rq.classify_kind(question, topic) == kind
    assert kind in rq.KIND_WORDS


def test_private_questions_are_left_out_but_everyday_paperwork_is_kept():
    for question, answers in (("What is my password?", ["abc"]), ("How do I look?", ["good"]),
                              ("What is the phone number?", ["555 123 4567"]), ("Is this tattoo nice?", ["yes"]),
                              ("What is this?", ["naked man"])):
        assert rq.private_reason(question, answers), question
    for question, answers in (("How much is this bill for?", ["62.31"]), ("What is this envelope?", ["mail"]),
                              ("What does my prescription label say?", ["take 1 daily"]),
                              ("What is on my screen?", ["windows update"])):
        assert not rq.private_reason(question, answers), question


def test_a_balanced_pick():
    rows = [vizwiz_row(["a"] * 10, answerable=i % 2, id=f"r{i}", kind=["read", "what", "colour"][i % 3],
                       question=f"q{i % 5}") for i in range(60)]
    taken = rq.pick_mix(rows, 20)
    assert len(taken) == 20 and len({r["id"] for r in taken}) == 20
    assert sum(1 for r in taken if not r["answerable"]) <= 5
    assert {r["kind"] for r in taken} == {"read", "what", "colour"}
    assert rq.pick_mix(rows, 20) == taken                                  # the same each time
    same_kind = [dict(r, kind="what", answerable=1) for r in rows]
    assert len({r["question"] for r in rq.pick_mix(same_kind, 5)}) == 5      # repeated questions only at the end


# ----------------------------------------------------------------- the shipped list

@pytest.fixture(scope="module")
def shipped():
    return rq.load_set()


def test_the_shipped_list_is_small_and_balanced(shipped):
    assert 550 <= len(shipped) <= 650
    assert os.path.getsize(rq.SET_FILE) < 400_000
    counts = rq.counts(shipped)
    for topic in ("medicines", "food", "drinks", "alcohol", "machines", "documents", "nature"):
        assert 40 <= counts.get(topic, 0) <= 50, topic
    assert counts.get(rq.HOME_TESTS, 0) >= 10 and counts.get(rq.EVERYDAY, 0) >= 100
    for empty in ("nudity", "sexual", "firearms"):
        assert empty not in counts
    known = {t.id for t in topics.TOPICS} | {rq.HOME_TESTS, rq.EVERYDAY}
    assert set(counts) <= known
    assert len({r["id"] for r in shipped}) == len(shipped)


def test_every_shipped_row_is_complete_and_open(shipped):
    for r in shipped:
        assert r["licence"] == "CC BY 4.0" and r["source"] in ("vizwiz", "orbit")
        assert r["question"].strip() and r["answers"] and r["kind"] in rq.KIND_WORDS
        if r["source"] == "vizwiz":
            assert len(r["answers"]) == 10 and r["image"].startswith("VizWiz_")
            assert not rq.private_reason(r["question"], r["answers"])
            if not r["image"].startswith("VizWiz_test_"):              # train and val: masked photos, home tests
                number = int(r["image"][-12:-4])
                assert r.get("masked") == (23431 <= number <= 23958 and "train" in r["image"]) or \
                    r["topic"] == rq.HOME_TESTS
            if r.get("masked"):
                assert r["image"].startswith("VizWiz_train_") and 23431 <= int(r["image"][-12:-4]) <= 23958
        else:
            assert r["zip"] == "train" and r["offset"] > 0 and r["size"] > 0 and r["question"] == "What is this?"


def test_the_shipped_list_has_the_question_types_blind_people_ask(shipped):
    kinds = {r["kind"] for r in shipped}
    for kind in ("read", "expiry", "amount", "colour", "button", "on_off", "money", "medicine", "what"):
        assert kind in kinds, kind
    assert any(not r["answerable"] for r in shipped) and any(r.get("masked") for r in shipped)


def test_a_topic_test_has_its_own_and_everyday_questions(shipped):
    food = rq.for_topic(shipped, "food")
    assert {r["topic"] for r in food} == {"food", rq.EVERYDAY}
    assert rq.HOME_TESTS in {r["topic"] for r in rq.for_topic(shipped, "medicines")}
    assert len(rq.for_topic(shipped)) == len(shipped)


def test_real_question_pictures_are_never_trained_on(shipped):
    vizwiz = next(r for r in shipped if r.get("masked"))
    orbit = next(r for r in shipped if r["source"] == "orbit")
    rows = [{"picture": f"/lib/vizwiz_vqa/vizwizq-{vizwiz['image']}"},
            {"picture": f"/lib/orbit/orbit-{orbit['image']}"},
            {"picture": "/lib/vizwiz_vqa/vizwizq-VizWiz_train_00000001.jpg"}]
    kept, held = rq.leave_out(rows)
    assert held == 2 and kept == rows[2:]


# ----------------------------------------------------------------- downloads, with a made-up server

class FakeAnswer:
    """A made-up web reply."""

    def __init__(self, content=b"", status=200, url=""):
        self.content, self.status_code, self.url = content, status, url

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("refused")


def test_pictures_are_downloaded_once(tmp_path, monkeypatch):
    frame = b"\xff\xd8 made-up frame \xff\xd9" * 10
    packed = zlib.compressobj(9, zlib.DEFLATED, -15)
    body = packed.compress(frame) + packed.flush()
    name = b"train/P1/keys/clean/v/P1--keys--clean--v-00001.jpg"
    header = b"PK\x03\x04" + b"\0" * 22 + len(name).to_bytes(2, "little") + (0).to_bytes(2, "little") + name
    rows = [vizwiz_row(["a"] * 10, id="v1"),
            {"id": "o1", "source": "orbit", "image": "P1--keys--clean--v-00001.jpg", "question": "What is this?",
             "answers": ["keys"], "answerable": 1, "topic": "everyday", "kind": "what", "zip": "train",
             "offset": 1000, "size": len(body), "method": 8}]
    asked = []

    class FakeSession:
        headers = {}

        def get(self, url, headers=None, timeout=None, allow_redirects=True):
            asked.append(url)
            if "vizwiz" in url:
                return FakeAnswer(b"vizwiz photo")
            if headers and headers.get("Range") == "bytes=0-0":
                return FakeAnswer(b"P", 206, url="https://signed.example/train.zip")
            assert headers["Range"].startswith("bytes=1000-")
            return FakeAnswer(header + body + b"\0" * 50, 206)
    monkeypatch.setattr(rq, "_session", lambda: FakeSession())
    said = []
    here, missing = rq.fetch_pictures(rows, str(tmp_path), said.append)
    assert missing == 0 and len(here) == 2
    assert (tmp_path / "VizWiz_test_00000001.jpg").read_bytes() == b"vizwiz photo"
    assert (tmp_path / "orbit-P1--keys--clean--v-00001.jpg").read_bytes() == frame
    assert any("Downloading 2 photos" in s for s in said)
    asked.clear()
    rq.fetch_pictures(rows, str(tmp_path), said.append)
    assert not asked                                                       # never fetched again


def test_answers_are_kept_and_a_stopped_test_carries_on(tmp_path):
    rows = [vizwiz_row(["coke"] * 10, id=f"q{i}", picture="x.jpg") for i in range(3)]
    out = str(tmp_path / "answers.jsonl")
    calls = []

    def answer(row):
        calls.append(row["id"])
        if len(calls) == 2:
            raise KeyboardInterrupt
        return "Coke"
    with pytest.raises(KeyboardInterrupt):
        rq.answer_all(answer, rows, out, lambda *a: None)
    done = rq.answer_all(lambda row: "Pepsi", rows, out, lambda *a: None)
    assert [r["id"] for r in done] == ["q0", "q1", "q2"]
    assert done[0]["model_answer"] == "Coke" and done[0]["accuracy"] == 1.0 and done[2]["model_answer"] == "Pepsi"


# ----------------------------------------------------------------- what is tested

def test_what_to_test(tmp_path):
    assert rq.resolve_target("4b", str(tmp_path))[1:] == (None, "4b")
    addon = tmp_path / "work" / "adapter-8b-topic-food" / "final"
    addon.mkdir(parents=True)
    (addon / "adapter_config.json").write_text(json.dumps({"base_model_name_or_path": "x/Huihui-Qwen3-VL-8B-Instruct"}))
    assert rq.resolve_target(str(addon.parent), str(tmp_path))[1:] == (str(addon), "8b")
    assert rq.find_addon(str(tmp_path / "work"), "food", "8b") == str(addon)
    assert rq.find_addon(str(tmp_path / "work"), "drinks", "8b") is None
    import zipfile
    zipped = tmp_path / "result.zip"
    with zipfile.ZipFile(zipped, "w") as z:
        z.writestr("adapter/adapter_config.json", "{}")
        z.writestr("adapter/adapter_model.safetensors", "weights")
    _what, folder, _model = rq.resolve_target(str(zipped), str(tmp_path))
    assert os.path.exists(os.path.join(folder, "adapter_model.safetensors"))
    with pytest.raises(ValueError, match="is not 4b, 8b"):
        rq.resolve_target("nothing-here", str(tmp_path))


def importable_train():
    """True when train.py can be imported here (it needs psutil for its computer-use lines)."""
    import importlib.util
    return importlib.util.find_spec("psutil") is not None


@pytest.mark.parametrize("argv, words", [
    (["--evaluate", "nothing-here"], "is not 4b, 8b, an add-on folder or a result zip"),
    (["--evaluate", "4b", "--topic", "cooking"], "There is no topic called cooking"),
])
def test_evaluate_stops_in_plain_words(tmp_path, monkeypatch, argv, words):
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import system_monitor
    import train
    monkeypatch.setattr(train, "LOG", str(tmp_path / "training-log.txt"))
    monkeypatch.setattr(train, "HERE", str(tmp_path))
    monkeypatch.setattr(system_monitor, "start", lambda *a, **k: None)
    with pytest.raises(SystemExit):
        train.main(argv)
    assert words in (tmp_path / "training-log.txt").read_text(encoding="utf-8")


def test_evaluate_writes_a_report(tmp_path, monkeypatch):
    """The whole --evaluate run with a made-up model: photos fetched, questions answered, the report written."""
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import system_monitor
    import train
    monkeypatch.setattr(train, "LOG", str(tmp_path / "training-log.txt"))
    monkeypatch.setattr(train, "HERE", str(tmp_path))
    monkeypatch.setattr(system_monitor, "start", lambda *a, **k: None)
    monkeypatch.setattr(train, "check_computer", lambda *a, **k: ("card", 16))
    monkeypatch.setattr(train, "download_model", lambda *a, **k: str(tmp_path / "model"))

    class FakeModel:
        def eval(self):
            return self
    monkeypatch.setattr(train, "load_model", lambda *a, **k: (FakeModel(), None))
    monkeypatch.setattr(rq, "fetch_pictures", lambda rows, folder, say: ([dict(r, picture="x") for r in rows], 0))
    monkeypatch.setattr(rq, "answer_one", lambda m, p, row, d, s: "Unanswerable" if not row["answerable"] else
                        rq.agreed_answers(row["answers"], 1)[0] if row["source"] == "vizwiz" else row["answers"][0])
    assert train.main(["--evaluate", "4b", "--topic", "drinks"]) == 0
    report = (tmp_path / "report-real-questions-4b-drinks.txt").read_text(encoding="utf-8")
    assert "Real questions test: the 4B model itself" in report and "Drinks (no alcohol) (" in report
    assert "Everyday questions (" in report and "Medicines" not in report
    log = (tmp_path / "training-log.txt").read_text(encoding="utf-8")
    assert "Step 3 of 3" in log and "FINISHED. Real questions test" in log


def test_the_topic_training_report_has_the_real_questions(tmp_path):
    if not importable_train():
        pytest.skip("train.py needs psutil")
    import train
    before = [dict(vizwiz_row(["coke"] * 10, id=f"d{i}", topic=t), model_answer="pepsi",
                   **rq.score_row(vizwiz_row(["coke"] * 10), "pepsi"))
              for i in range(3) for t in ("drinks", "everyday")]
    after = [dict(r, model_answer="coke", **rq.score_row(r, "coke")) for r in before]
    info = {"topic": "drinks", "label": {"licence_class": "open"}, "topic_replay": 0.15, "replay_pictures": 10,
            "model": "m", "revision": "r" * 12, "card": "c", "train": 1, "test": 1, "size": "quick",
            "share_alike": False, "seconds": 60, "real_questions": train.real_questions_summary(before, after)}
    path = tmp_path / "report.txt"
    rows = [{"source": "docci", "picture": "p", "question": "q", "answer": "a", "description": "d", "score": 0.1}]
    train.write_report(str(path), info, {"docci": 0.1, "all": 0.1}, {"docci": 0.2, "all": 0.2}, rows, rows)
    text = path.read_text(encoding="utf-8")
    assert "On blind people's real questions" in text
    assert "On this topic (3 questions): accuracy before 0.00, after 1.00: better." in text
    assert json.dumps(info)                                                 # scores.json stays plain and small
    assert train.real_questions_summary([], after) == {}


# ----------------------------------------------------------------- the window's button

try:
    import wx
except ImportError:                       # the window tests are skipped where wxPython is missing
    wx = None
APP = None


@pytest.fixture
def wizard(monkeypatch, tmp_path):
    """The training wizard's main window, without speaking or timers, with its settings in tmp_path."""
    if wx is None:
        pytest.skip("needs wxPython")
    for name in ("APPDATA", "LOCALAPPDATA", "HOME", "USERPROFILE"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    os.makedirs(tmp_path / "home", exist_ok=True)
    global APP
    APP = wx.GetApp() or wx.App(False)                    # kept, so it lives while the windows do
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "wizard"))
    import training_wizard
    monkeypatch.setattr(training_wizard, "speak", lambda *a, **k: None)
    w = training_wizard.Wizard()
    w.timer.Stop()
    yield w
    for window in [x for x in wx.GetTopLevelWindows() if x]:
        window.Destroy()
    for _ in range(3):
        wx.Yield()


def test_the_topic_window_has_the_test_button(wizard):
    import training_wizard
    window = training_wizard.TopicAddonDialog(wizard, training_wizard.topics_module(),
                                              training_wizard.sources_module(), wizard.boxes())
    buttons = [c for c in window.GetChildren()[0].GetChildren() if isinstance(c, wx.Button)]
    test = [b for b in buttons if b.GetLabel() == "Test on real &questions"]
    assert len(test) == 1 and "(Alt+Q)" in test[0].GetToolTipText()
    ended = []
    window.EndModal = ended.append
    event = wx.CommandEvent(wx.wxEVT_BUTTON, test[0].GetId())
    event.SetEventObject(test[0])
    test[0].GetEventHandler().ProcessEvent(event)
    assert ended == [training_wizard.TEST_REAL_QUESTIONS]


def test_testing_on_real_questions_starts_the_kit(wizard, monkeypatch, tmp_path):
    """The test runs kit\\train.py --evaluate with the topic's newest add-on, or the model itself."""
    import training_wizard
    monkeypatch.setattr(training_wizard, "check_computer", lambda *a, **k: (["Ready."], True))
    started = []

    class FakeThread:
        """Records the run's arguments instead of starting it."""

        def __init__(self, target=None, args=(), daemon=None):
            started.append(args)

        def start(self):
            pass
    monkeypatch.setattr(training_wizard.threading, "Thread", FakeThread)
    wizard.folder.SetValue(str(tmp_path))
    wizard.library.SetValue("")
    topic = training_wizard.topics_module().find("food")
    wizard.start_evaluation(topic)
    args = started[-1][0]
    assert args == ["--model", "4b", "--evaluate", "4b", "--topic", "food"]
    assert wizard.second.IsShown() and "the 4B model itself is tested" in wizard.lines.get_nowait()
    addon = tmp_path / training_wizard.KIT_NAME / "work" / "adapter-4b-topic-food-quick" / "final"
    addon.mkdir(parents=True)
    wizard.start_evaluation(topic)
    assert started[-1][0][3] == str(addon)
    assert training_wizard.SPOKEN.match("Real questions test: the 4B model itself, on 222 questions")
    assert training_wizard.SPOKEN.match("    real questions, after training: 25 of 222 questions answered")


def test_the_guide_explains_the_real_questions():
    with open(os.path.join(os.path.dirname(KIT), "READ ME FIRST.txt"), encoding="utf-8") as f:
        text = f.read()
    section = text[text.index("\nTesting on real questions\n"):]
    for words in ("Alt+Q", "--evaluate", "VizWiz", "ORBIT", "CC BY 4.0", "home health tests", "unanswerable",
                  "report-real-questions"):
        assert words in section, words
