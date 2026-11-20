"""The accessibility test for every window of the Picture Model Training Kit (the wizard, its smaller windows, the
Describe pictures windows and the Dataset Preparation program). The kit is only published when this passes
(.github/workflows/training-kit.yml runs it first, on Linux and on Windows).

The rules, the same as the Digital Accessibility Toolkit's (tests/test_gui.py there):
  - every text field, list and choice comes right after a label ending in ":";
  - every button has an Alt letter, named in its tooltip as "(Alt+X)"; check boxes too;
  - no Alt letter is used twice in one window;
  - check boxes and radio groups have labels; tab lists have a name for screen readers;
  - no default button (Enter presses only the focused button);
  - Escape closes the window and F1 opens the guide (each window binds the keys; checked by pressing them).

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests     (on Windows: python -m pytest -q training-kit\\tests)
"""

import os
import sys

import pytest

wx = pytest.importorskip("wx")

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
for part in ("wizard", "kit", "prepare"):
    sys.path.insert(0, os.path.join(KIT, part))


@pytest.fixture(scope="module")
def app():
    """One wx.App for all the window tests."""
    yield wx.GetApp() or wx.App(False)


@pytest.fixture(autouse=True)
def private_settings(tmp_path, monkeypatch):
    """Each test keeps its settings and logs in its own folder, never the person's."""
    for name in ("APPDATA", "LOCALAPPDATA", "HOME", "USERPROFILE"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    os.makedirs(tmp_path / "home", exist_ok=True)
    yield
    for w in [w for w in wx.GetTopLevelWindows() if w]:
        if w:
            w.Destroy()
    for _ in range(3):
        wx.Yield()


def walk(window):
    """Every control inside window, in tab order (depth first); windows of their own are checked on their own."""
    for child in window.GetChildren():
        if isinstance(child, wx.TopLevelWindow):
            continue
        yield child
        # A spin box or combo box is one control to a screen reader; on Windows it is built from an inner text box
        # (its own part, already labelled through the control), which is not checked as a separate field.
        if not isinstance(child, (wx.SpinCtrl, wx.SpinCtrlDouble, wx.ComboBox)):
            yield from walk(child)


def letter_of(label):
    """The Alt letter of a label ("&Browse" -> "b"), or None."""
    label = label.replace("&&", "")
    return label[label.index("&") + 1].lower() if "&" in label and label.index("&") + 1 < len(label) else None


def assert_accessible(window):
    """Check the rules in the module docstring for every control of window."""
    controls = list(walk(window))
    assert controls, "the window has no controls"
    keys = {}
    for c in controls:
        if isinstance(c, (wx.Button, wx.CheckBox, wx.RadioBox, wx.StaticText)):
            key = letter_of(c.GetLabel())
            if key:
                assert key not in keys, f"Alt+{key} is used by both '{keys[key]}' and '{c.GetLabel()}'"
                keys[key] = c.GetLabel()
    for i, c in enumerate(controls):
        if isinstance(c, wx.Button) and c.GetId() not in (wx.ID_CANCEL, wx.ID_OK):
            label = c.GetLabel()
            assert label.strip(), "a button without a label"
            assert letter_of(label), f"button '{label}' has no Alt letter"
            assert f"Alt+{letter_of(label).upper()}" in c.GetToolTipText(), \
                f"the tooltip of '{label}' does not name Alt+{letter_of(label).upper()}: {c.GetToolTipText()!r}"
        if isinstance(c, wx.CheckBox):
            label = c.GetLabel()
            assert label.strip(), "a check box without a label"
            assert letter_of(label), f"check box '{label}' has no Alt letter"
            assert f"Alt+{letter_of(label).upper()}" in c.GetToolTipText(), \
                f"the tooltip of '{label}' does not name Alt+{letter_of(label).upper()}"
        if isinstance(c, (wx.TextCtrl, wx.ListBox, wx.Choice, wx.ComboBox, wx.SpinCtrl, wx.SpinCtrlDouble,
                          wx.ListCtrl, wx.Slider)):
            previous = controls[i - 1] if i else None
            assert isinstance(previous, wx.StaticText), f"a {c.__class__.__name__} has no label right before it"
            assert previous.GetLabel().rstrip().endswith(":"), f"the label {previous.GetLabel()!r} does not end in ':'"
        if isinstance(c, wx.Notebook):
            assert c.GetLabel().strip(), "a tab list without a name for screen readers"
        if isinstance(c, wx.RadioBox):
            assert letter_of(c.GetLabel()), "a radio group without a label and Alt letter"
    if isinstance(window, (wx.Dialog, wx.Frame)):
        assert window.GetDefaultItem() is None, "the window has a default button (Enter must press only the focused one)"


def press(window, code):
    """Give window's key handler (the one bound to EVT_CHAR_HOOK) a key press, as the keyboard does."""
    event = wx.KeyEvent(wx.wxEVT_CHAR_HOOK)
    event.SetEventObject(window)
    event.SetKeyCode(code)
    window.on_key(event)


def assert_keys(window, monkeypatch, closes):
    """F1 opens a guide and Escape closes. closes(window) says whether the window has closed (or ended its modal
    loop); the guide opener is replaced so no program is started."""
    opened = []
    for module in [m for m in list(sys.modules.values()) if m is not None]:
        if hasattr(module, "open_file") and getattr(module, "__file__", "") and \
                os.path.abspath(module.__file__).startswith(KIT):
            monkeypatch.setattr(module, "open_file", lambda path, *a, **k: opened.append(path))
    monkeypatch.setattr(os, "startfile", lambda path, *a, **k: opened.append(path), raising=False)
    press(window, wx.WXK_F1)
    assert opened, "F1 did not open the guide"
    press(window, wx.WXK_ESCAPE)
    assert closes(window), "Escape did not close the window"


# ----------------------------------------------------------------- the wizard

@pytest.fixture
def wizard(app, monkeypatch):
    """The training wizard's main window, without speaking or timers."""
    import training_wizard
    monkeypatch.setattr(training_wizard, "speak", lambda *a, **k: None)
    w = training_wizard.Wizard()
    w.timer.Stop()
    yield w


def test_the_wizard_is_accessible(wizard):
    assert_accessible(wizard)


def test_the_everything_switch_has_its_own_key(wizard):
    """The "Personal use: everything allowed" box: its own Alt key (1), named in its tooltip, used once."""
    box = wizard.everything_box
    assert letter_of(box.GetLabel()) == "1"
    assert "Alt+1" in box.GetToolTipText()
    assert_accessible(wizard)


def test_the_everything_windows_keys(app, wizard, monkeypatch):
    import training_wizard
    for window in (training_wizard.EverythingDialog(wizard, "About."), training_wizard.SignupKeysDialog(wizard)):
        ended = []
        monkeypatch.setattr(window, "EndModal", lambda code, ended=ended: ended.append(code))
        assert_keys(window, monkeypatch, lambda w, ended=ended: bool(ended))
        window.Destroy()


def test_the_wizard_small_windows_are_accessible(app, wizard):
    import training_wizard
    windows = [training_wizard.SexualDialog(wizard, False), training_wizard.GraphicDialog(wizard, True),
               training_wizard.EverythingDialog(wizard, training_wizard.EVERYTHING_ABOUT),
               training_wizard.SignupKeysDialog(wizard)]
    collections = training_wizard.research_collections()
    if collections:
        windows.append(training_wizard.ResearchTermsDialog(wizard, collections))
    for w in windows:
        assert_accessible(w)


def test_the_describe_windows_are_accessible(app, wizard, tmp_path):
    import describe_window
    import training_wizard
    library = str(tmp_path / "library")
    os.makedirs(library)
    main = describe_window.DescribeWindow(wizard, training_wizard, None, library)
    assert_accessible(main)
    package = describe_window.load_package_module(training_wizard)
    folder = str(tmp_path / "workspace")
    workspace = package.make_workspace(folder, "Test")
    windows = [describe_window.NameDialog(main, training_wizard, folder),
               describe_window.ExportDialog(main, training_wizard, package),
               describe_window.VideoDialog(main, training_wizard),
               describe_window.OtherDialog(main, training_wizard, "One description.", [("photo.other-Anna.txt", "Anna", "Another one.")]),
               describe_window.ReviewDialog(main, training_wizard, library)]
    items = describe_window.review_lists(training_wizard)[0]
    if items:
        windows.append(describe_window.ReviewTermsDialog(main, training_wizard, items[:2]))
    for w in windows:
        assert_accessible(w)
    assert workspace


def test_the_describe_window_keys(app, wizard, tmp_path, monkeypatch):
    import describe_window
    import training_wizard
    library = str(tmp_path / "library")
    os.makedirs(library)
    main = describe_window.DescribeWindow(wizard, training_wizard, None, library)
    ended = []
    monkeypatch.setattr(main, "EndModal", lambda code: ended.append(code))
    monkeypatch.setattr(main, "resource", lambda *a: __file__, raising=False)
    monkeypatch.setattr(training_wizard, "resource", lambda *a: __file__)
    assert_keys(main, monkeypatch, lambda w: bool(ended) or not w.IsShown())


# ----------------------------------------------------------------- Dataset Preparation

@pytest.fixture
def prepare(app, monkeypatch, tmp_path):
    """The Dataset Preparation window, without speaking or its timer."""
    import training_wizard
    monkeypatch.setattr(training_wizard, "speak", lambda *a, **k: None)
    import dataset_preparation
    w = dataset_preparation.PrepareWindow()
    w.timer.Stop()
    yield w


def test_dataset_preparation_is_accessible(prepare):
    assert_accessible(prepare)


def test_dataset_preparation_keys(prepare, monkeypatch):
    import dataset_preparation
    import training_wizard
    monkeypatch.setattr(training_wizard, "resource", lambda *a: __file__)
    monkeypatch.setattr(dataset_preparation, "resource", lambda *a: __file__, raising=False)
    closed = []
    monkeypatch.setattr(prepare, "Close", lambda *a: closed.append(True))
    assert_keys(prepare, monkeypatch, lambda w: bool(closed))


def test_dataset_preparation_says_what_to_do_first(prepare):
    said = []
    prepare.say = lambda text, *a, **k: said.append(text)
    prepare.workspace.SetValue("")
    prepare.on_clean(None)
    assert "workspace folder first" in said[-1]


def test_your_own_describer_needs_a_finished_training(prepare, tmp_path):
    prepare.kit.SetValue(str(tmp_path / "kit"))
    prepare.update_engines()
    assert not prepare.engines["yours"].IsEnabled()
    os.makedirs(tmp_path / "kit" / "work" / "adapter-4b-full" / "final")
    prepare.update_engines()
    assert prepare.engines["yours"].IsEnabled()


def test_the_drafts_job_gets_the_ticked_models(prepare, tmp_path):
    import describe_package
    ws = describe_package.make_workspace(str(tmp_path / "ws"), "Test")
    for key, box in prepare.engines.items():
        box.SetValue(key in ("qwen", "florence"))
    prepare.combine.SetValue(False)
    args = prepare.prepare_args("all", ws)
    assert args[:2] == [ws.folder, "all"]
    assert args[args.index("--engines") + 1] == "qwen,florence" and "--no-combine" in args


def test_describe_pictures_starts_from_the_draft(app, wizard, tmp_path, monkeypatch):
    """A picture without a description shows the computer's draft, which is saved only when the person saves."""
    import describe_package
    import describe_window
    import training_wizard
    from PIL import Image
    folder = str(tmp_path / "ws")
    ws = describe_package.make_workspace(folder, "Test")
    Image.new("RGB", (64, 48), (200, 30, 30)).save(os.path.join(folder, "red.jpg"))
    Image.new("RGB", (64, 48), (30, 30, 200)).save(os.path.join(folder, "blue.jpg"))
    describe_package.register_new(ws)
    ws = describe_package.open_workspace(folder)
    ws.entry("red.jpg").update(draft="A red square.", draft_qwen="A red square.", draft_florence="A red box.",
                               draft_agreement="0.30")
    ws.entry("blue.jpg").update(draft="A blue square.", draft_qwen="A blue square.", draft_agreement="0.90")
    ws.save()
    choices = training_wizard.load_choices()
    training_wizard.save_choices({**choices, "describe_workspace": folder, "describe_name": "Mark"})
    window = describe_window.DescribeWindow(wizard, training_wizard, None, str(tmp_path / "library"))
    window.say = lambda *a, **k: None
    window.filter.SetSelection([k for k, _l in describe_window.FILTERS].index("drafts disagree"))
    window.refresh()
    assert window.names == ["red.jpg", "blue.jpg"]           # the one whose drafts disagree most comes first
    assert window.description.GetValue() == "A red square." and window.from_draft
    assert "Qwen3-VL 8B: A red square." in window.drafts.GetValue()
    assert "Florence-2 large: A red box." in window.drafts.GetValue()
    assert not window.changed()                             # moving on does not save an unchecked draft
    window.save_changes()
    assert describe_package.description(describe_package.open_workspace(folder), "red.jpg") == ""
    window.description.SetValue("A red square on white.")
    assert window.save_changes()
    saved = describe_package.open_workspace(folder)
    assert describe_package.description(saved, "red.jpg") == "A red square on white."
    assert saved.entry("red.jpg")["status"] == "described" and saved.entry("red.jpg")["started_from_draft"] == "yes"


def test_drafts_travel_in_packages(tmp_path):
    import describe_package
    from PIL import Image
    first = describe_package.make_workspace(str(tmp_path / "one"), "One")
    Image.new("RGB", (64, 48), (10, 120, 10)).save(os.path.join(first.folder, "green.jpg"))
    describe_package.register_new(first)
    first = describe_package.open_workspace(first.folder)
    first.entry("green.jpg").update(draft="A green square.", draft_internvl="Green.", draft_agreement="0.50")
    first.save()
    zip_path = str(tmp_path / "package.zip")
    describe_package.export_package(first, zip_path, "all", "Mark")
    second = describe_package.make_workspace(str(tmp_path / "two"), "Two")
    describe_package.import_package(second, zip_path)
    entry = describe_package.open_workspace(second.folder).entry("green.jpg")
    assert entry["draft"] == "A green square." and entry["draft_internvl"] == "Green."


def test_the_clean_up_and_its_parts():
    """kit/prepare_data.py's own self-test: agreement, tidy, and setting aside dark, blurry and repeated pictures."""
    pytest.importorskip("numpy")
    import prepare_data
    prepare_data.self_test()


def test_the_clean_up_removes_a_date_stamp_from_photos(tmp_path):
    """A fixed date stamp in the corner of many different photos of the same size is found and filled in, and the
    originals are kept in .originals."""
    np = pytest.importorskip("numpy")
    pytest.importorskip("cv2")
    import describe_package
    import prepare_data
    from PIL import Image, ImageDraw, ImageFont
    folder = str(tmp_path / "ws")
    describe_package.make_workspace(folder, "Stamps")
    font = ImageFont.load_default(size=20)              # a camcorder-style stamp: bright digits with a dark edge
    rng = np.random.default_rng(7)
    for i in range(16):
        base = (rng.random((24, 32, 3)) * 255).astype("uint8")
        img = Image.fromarray(base).resize((320, 240), Image.BILINEAR)
        ImageDraw.Draw(img).text((200, 208), "12 05 98", fill=(255, 160, 0), font=font, stroke_width=2,
                                 stroke_fill=(0, 0, 0))
        img.save(os.path.join(folder, f"photo{i:02}.png"))
    describe_package.register_new(folder)
    summary = prepare_data.clean(folder, set_aside=False, overlays="fill")
    assert "date stamps or logos removed from 16 pictures" in summary, summary
    assert os.path.exists(os.path.join(folder, ".originals", "photo00.png"))
    before = np.asarray(Image.open(os.path.join(folder, ".originals", "photo00.png")).convert("RGB"), dtype=float)
    after = np.asarray(Image.open(os.path.join(folder, "photo00.png")).convert("RGB"), dtype=float)
    assert np.abs(before - after)[205:235, 195:300].mean() > 20      # the stamp is gone ...
    assert np.abs(before - after)[:150, :150].mean() < 1             # ... and the rest of the photo is untouched


# ----------------------------------------------------------------- topic add-ons

def topic_window(wizard, boxes=None):
    """The Topic add-ons window over the wizard, with the kit's own topics and collections."""
    import training_wizard
    return training_wizard.TopicAddonDialog(wizard, training_wizard.topics_module(), training_wizard.sources_module(),
                                            boxes or wizard.boxes())


def test_the_topic_window_is_accessible(app, wizard):
    window = topic_window(wizard)
    assert_accessible(window)
    letters = {letter_of(c.GetLabel()) for c in walk(window)
               if isinstance(c, (wx.Button, wx.CheckBox, wx.StaticText)) and letter_of(c.GetLabel())}
    assert letters == {"t", "a", "e", "s", "c"}
    assert window.topic.GetCount() == 10 and window.share.GetValue() == 15
    assert (window.share.GetMin(), window.share.GetMax()) == (0, 40)


def test_the_topic_window_keys(app, wizard, monkeypatch):
    window = topic_window(wizard)
    ended = []
    monkeypatch.setattr(window, "EndModal", lambda code: ended.append(code))
    assert_keys(window, monkeypatch, lambda w: bool(ended))
    assert ended == [wx.ID_CANCEL]


def test_the_wizard_has_a_topic_button(wizard):
    """Every letter of the first page is taken, so Topic add-ons uses the digit 2, named in its tooltip."""
    found = [c for c in walk(wizard) if isinstance(c, wx.Button) and c.GetLabel() == "Topic add-ons (&2)..."]
    assert len(found) == 1 and "Alt+2" in found[0].GetToolTipText()


def test_the_topic_window_says_the_licence(app, wizard, monkeypatch):
    import training_wizard
    said = []
    monkeypatch.setattr(training_wizard, "speak", lambda text, *a, **k: said.append(text))
    window = topic_window(wizard, {"wikipedia": False, "noncommercial": False, "research": False})
    food = [t.id for t in training_wizard.topics_module().TOPICS].index("food")
    window.topic.SetSelection(food)
    window.on_topic(None)
    text = window.about.GetValue()
    assert text.startswith("Food and packaged goods.") and "Licence of this add-on: open." in text
    assert "Left out until their box is ticked" in text and "never used for making pictures" in text
    assert said and said[-1].startswith("Food and packaged goods. Licence of this add-on: open.")
    window.Destroy()
    window = topic_window(wizard, {"wikipedia": True, "noncommercial": True, "research": True})
    window.topic.SetSelection(food)
    assert "Licence of this add-on: personal use only." in window.show_topic()
    window.topic.SetSelection(window.topic.GetCount() - 1)                  # sexual content
    text = window.show_topic()
    assert "sensitive" in text and "personal use only" in text
    window.share.SetValue(25)
    assert window.chosen().id == "sexual" and window.chosen_share() == 0.25


def test_starting_a_topic_add_on_passes_the_topic(app, wizard, monkeypatch):
    """Start training this add-on runs train.py with --topic and --topic-replay; a follow-up is refused."""
    import training_wizard
    monkeypatch.setattr(training_wizard, "check_computer", lambda *a, **k: (["Ready."], True))
    started = []

    class FakeThread:
        """Records the training's arguments instead of starting it."""

        def __init__(self, target=None, args=(), daemon=None):
            started.append(args)

        def start(self):
            pass
    monkeypatch.setattr(training_wizard.threading, "Thread", FakeThread)
    monkeypatch.setattr(wizard, "review_folders", lambda: [])
    topic = training_wizard.topics_module().find("food")
    wizard.size.SetSelection([k for k, _w in training_wizard.SIZES].index("continue"))
    wizard.topic_run = (topic, 0.2)
    wizard.on_start(None)
    assert not started and "always a new picture describer add-on" in wizard.check_result.GetValue()
    wizard.size.SetSelection([k for k, _w in training_wizard.SIZES].index("quick"))
    wizard.on_start(None)
    args = started[-1][0]
    assert args[args.index("--topic") + 1] == "food" and args[args.index("--topic-replay") + 1] == "0.20"
    assert "--continue" not in args
    assert training_wizard.topic_args("nature", 0.15) == ["--topic", "nature", "--topic-replay", "0.15"]
