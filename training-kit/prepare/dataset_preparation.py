"""Dataset Preparation (Dataset Preparation.exe): gets pictures ready for training, so the person who reviews them
starts from a good draft instead of an empty box. It is the Picture Model Training Kit's second program; it runs on
the training computer when no training is running (both use the graphics card).

The window goes through four steps, each with its own buttons, all said through the screen reader:
  1. Workspace and kit: the describing workspace (a folder of pictures with describing.json, the same workspaces
     the training wizard's "Describe pictures" window uses) and the kit folder ("C:\\Training\\Picture Model Training
     Kit" by default, from the wizard's settings): the kit's own Python and the models are there.
  2. Add pictures and videos: pictures and folders of pictures are copied in (duplicates skipped, big pictures made
     smaller: kit\\describe_package.py); "Take stills from videos" opens the same window as in Describe pictures and
     runs kit\\video_frames.py (good sharp stills, what was said as descriptions, date stamps and station logos
     cropped off or filled in, faces blurred).
  3. Clean up and drafts: kit\\run_prepare.cmd runs kit\\prepare_data.py in the kit's own Python: it sets aside dark,
     blurry and near-identical pictures, removes date stamps and logos from groups of pictures, blurs faces, and has
     the chosen picture models write draft descriptions (Qwen3-VL 8B, InternVL 3.5 8B, Florence-2 large, and your
     own trained describer when a training has finished), combined into one starting description per picture.
  4. Review: Describe pictures opens on the workspace; each picture without a description shows the computer's draft
     in Description (said as a draft), every model's draft is in "Drafts by each picture model", and the Filter can
     list first the pictures whose drafts disagree. Nothing is trained on until a person saves a description.

Accessibility (the same rules as the wizard; training-kit/tests/test_accessibility.py checks them before every
publish): standard wx controls only; a label ending ":" right before each field; every button and check box has an
Alt letter named in its tooltip, none used twice; Escape closes (asking first while work runs); F1 opens
"HOW TO PREPARE PICTURES FOR TRAINING.txt"; Enter presses only the focused button; long work moves the Progress
bar, and its important lines are said and shown in Status and in "What was done", and written into the desktop logs
("Picture Model Training logs", like the wizard).
Letters: K (Workspace folder), B (Browse for the workspace), F (Kit folder), D (Browse for the kit), P (Add
pictures), O (Add a folder of pictures), V (Take stills from videos), E (Set aside dark, blurry and repeated
pictures), U (Blur faces), G (Date stamps and logos), C (Clean up), Q (Qwen3-VL), I (InternVL), R (Florence-2),
Y (Your own trained describer), M (Combine the drafts), A (Write the drafts), N (Clean up, then write the drafts),
W (Review and correct in Describe pictures), S (Stop), H (Help), L (Close).

Command line: "Dataset Preparation.exe --self-test" checks that the window can be made and the kit's parts are
inside (the build's check).
"""

import glob
import os
import queue
import re
import subprocess
import sys
import threading

import wx

HERE = os.path.dirname(os.path.abspath(__file__))
for part in ("wizard", "kit"):
    folder = os.path.join(os.path.dirname(HERE), part)
    if os.path.isdir(folder) and folder not in sys.path:
        sys.path.insert(0, folder)

import describe_window  # noqa: E402
import training_wizard as wizard  # noqa: E402

TITLE = "Dataset Preparation"
GUIDE = "HOW TO PREPARE PICTURES FOR TRAINING.txt"
# The draft models (kit\prepare_data.py ENGINES): (key, check box label, tooltip, ticked at first).
ENGINES = [
    ("qwen", "&Qwen3-VL 8B: long, plain descriptions", "The kit's own 8B model (Apache-2.0, about 17 GB). It also "
     "writes the combined description", True),
    ("internvl", "&InternVL 3.5 8B: a second opinion from another family", "OpenGVLab's model (Apache-2.0, about "
     "17 GB): trained on different pictures, so its mistakes are different", True),
    ("florence", "Flo&rence-2 large: quick caption and the text it can read", "Microsoft's small model (MIT, about "
     "1.5 GB): a detailed caption and the words it reads in the picture", True),
    ("yours", "&Your own trained describer (after a training has finished)", "The kit's model with the add-on of your "
     "newest finished training: it describes the way you taught it", True),
]
OVERLAYS = [("keep", "Leave them"), ("crop", "Crop them off (fill in when cropping would lose too much)"),
            ("fill", "Fill them in")]
COUNT_LINE = re.compile(r"(\d+) of (\d+)\b")
SPOKEN = re.compile(r"^\s*(Model \d+ of \d+|Cleaning up|Clean-up done|Combining|Drafts are ready|There are no|"
                    r"Getting ready|STOPPED|Finished|Video \d+ of \d+|Your own trained describer is left out|"
                    r".*could not be loaded)")


def open_file(path):
    """Open a file or folder with its usual program (the guide, the workspace)."""
    if hasattr(os, "startfile"):
        os.startfile(path)  # noqa: S606 - the person's own file
    else:
        subprocess.Popen(["xdg-open", path])  # noqa: S603,S607


def finished_training(kit):
    """True when the kit has a finished training (an add-on in work\\adapter-*\\final) to write drafts with."""
    return bool(kit) and any(os.path.isdir(p) for p in glob.glob(os.path.join(kit, "work", "adapter-*", "final")))


class PrepareWindow(wx.Frame):
    """The Dataset Preparation window (see the module docstring)."""

    def __init__(self):
        """Make the window from the remembered choices (the wizard's settings.json)."""
        super().__init__(None, title=TITLE, size=(900, 940))
        self.mnemonics = {}
        self.process = None              # kit\run_prepare.cmd or kit\run_video.cmd while it runs
        self.busy = ""                   # what runs in the background, or ""
        self.lines = queue.Queue()       # what the background work says, for the window's thread
        self.package = describe_window.load_package_module(wizard)
        chosen = wizard.load_choices()
        panel = self.panel = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        self.about = self.labelled(s, "About this program:", lambda: wx.TextCtrl(
            panel, value=("Dataset Preparation gets pictures ready for training. Put pictures and videos into a "
                          "workspace, clean them up, and let two or three picture models write draft descriptions. "
                          "Then a person checks and corrects each description in Describe pictures: nothing is "
                          "trained on until a person saves it. Run it when no training is running: both use the "
                          "graphics card. Press F1 for the full guide."),
            style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 70)))

        # 1. the workspace and the kit
        self.workspace = self.labelled(s, "Wor&kspace folder:", lambda: wx.TextCtrl(
            panel, value=chosen.get("prepare_workspace") or chosen.get("describe_workspace", "")))
        s.Add(self.button("&Browse for the workspace folder...", "Choose the workspace folder, or an empty folder for "
                          "a new one", self.on_browse_workspace), 0, wx.LEFT, 8)
        default_kit = os.path.join(chosen.get("folder") or wizard.DEFAULT_FOLDER, wizard.KIT_NAME)
        self.kit = self.labelled(s, "Training kit &folder (its tools and models are used):", lambda: wx.TextCtrl(
            panel, value=chosen.get("prepare_kit") or default_kit))
        s.Add(self.button("Browse for the training kit fol&der...", "Choose the Picture Model Training Kit folder",
                          self.on_browse_kit), 0, wx.LEFT, 8)

        # 2. adding pictures and videos
        row = wx.WrapSizer(wx.HORIZONTAL)
        for b in (self.button("Add &pictures...", "Copy chosen pictures into the workspace", self.on_add),
                  self.button("Add a picture f&older...", "Copy every picture in a folder and its sub-folders into the "
                              "workspace", self.on_add_folder),
                  self.button("Take stills from &videos...", "Take good sharp stills out of videos, with what was said "
                              "and without date stamps and logos", self.on_videos)):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.LEFT, 4)

        # 3. clean-up and drafts
        self.set_aside = self.check("S&et aside dark, blurry and repeated pictures", "They are not deleted: Describe "
                                    "pictures can show them (Filter: Set aside or skipped)",
                                    chosen.get("prepare_set_aside", True))
        s.Add(self.set_aside, 0, wx.ALL, 6)
        self.blur = self.check("Bl&ur the faces of people", "Blur every face found in the new pictures (the originals "
                               "are kept in the hidden folder .originals)", chosen.get("prepare_blur", False))
        s.Add(self.blur, 0, wx.ALL, 6)
        self.overlays = self.labelled(s, "Date stamps and lo&gos in the pictures:", lambda: wx.Choice(
            panel, choices=[label for _key, label in OVERLAYS]), flag=0)
        self.overlays.SetToolTip("A camera's date stamp or a TV station's logo, found by what stays the same over many "
                                 "pictures of the same size")
        keys = [key for key, _label in OVERLAYS]
        self.overlays.SetSelection(keys.index(chosen.get("prepare_overlays", "keep"))
                                   if chosen.get("prepare_overlays", "keep") in keys else 0)
        s.Add(self.button("&Clean up the new pictures", "Set aside, remove date stamps and logos and blur faces, as "
                          "chosen above", self.on_clean), 0, wx.LEFT, 8)
        remembered = chosen.get("prepare_engines")
        self.engines = {}
        for key, label, tip, ticked in ENGINES:
            box = self.check(label, tip, (key in remembered) if isinstance(remembered, list) else ticked)
            self.engines[key] = box
            s.Add(box, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
        self.combine = self.check("Co&mbine the drafts into one starting description", "Qwen3-VL 8B looks at each "
                                  "picture again with all the drafts and writes one description to start from",
                                  chosen.get("prepare_combine", True))
        s.Add(self.combine, 0, wx.ALL, 6)
        row = wx.WrapSizer(wx.HORIZONTAL)
        for b in (self.button("Write the dr&afts", "Have the ticked models write draft descriptions of the new "
                              "pictures", self.on_drafts),
                  self.button("Clea&n up, then write the drafts", "Both steps, one after the other", self.on_all),
                  self.button("Revie&w and correct in Describe pictures...", "Open the workspace in Describe "
                              "pictures, where each new picture starts from the computer's draft", self.on_review),
                  self.button("&Stop", "Stop the work that is running (it carries on from there next time)",
                              self.on_stop)):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.LEFT, 4)

        # what is happening
        self.summary = self.labelled(s, "Workspace summary:", lambda: wx.TextCtrl(panel, style=wx.TE_READONLY))
        self.status = self.labelled(s, "Status:", lambda: wx.TextCtrl(panel, style=wx.TE_READONLY))
        self.gauge = self.labelled(s, "Progress:", lambda: wx.Gauge(panel, range=100))
        self.log_box = self.labelled(s, "What was done:", lambda: wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("&Help (F1)", "Open the guide", self.on_help), 0, wx.ALL, 4)
        row.Add(self.button("C&lose", "Close the program (Escape)", lambda e: self.Close()), 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        panel.SetSizer(s)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(250)
        self.update_engines()
        self.update_summary()
        self.Centre()

    # -- helpers following the accessibility rules
    def labelled(self, sizer, label, factory, proportion=0, flag=wx.EXPAND):
        """A label ending ":" and, right after it, its control; an &letter in the label moves focus to it."""
        sizer.Add(wx.StaticText(self.panel, label=label), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        control = factory()
        sizer.Add(control, proportion, flag | wx.ALL, 6)
        letter = re.search(r"&(\w)", label)
        if letter:
            self.mnemonics[letter.group(1).lower()] = control
        return control

    def button(self, label, tip, handler):
        """A button with an &letter named in its tooltip "(Alt+X)"."""
        b = wx.Button(self.panel, label=label)
        b.SetToolTip(f"{tip} (Alt+{re.search(r'&(\w)', label).group(1).upper()})")
        b.Bind(wx.EVT_BUTTON, handler)
        return b

    def check(self, label, tip, value):
        """A check box with an &letter named in its tooltip."""
        c = wx.CheckBox(self.panel, label=label)
        c.SetValue(bool(value))
        c.SetToolTip(f"{tip} (Alt+{re.search(r'&(\w)', label).group(1).upper()})")
        return c

    # -- saying what happens
    def say(self, text, interrupt=True, spoken=True):
        """Show text in Status and What was done, write it into the desktop log and (spoken) say it."""
        if not self:
            return
        text = " ".join(str(text).split())
        self.status.SetValue(text)
        self.log_box.AppendText(text + "\n")
        wizard.log(f"{TITLE}: {text}")
        if spoken:
            wizard.speak(text, interrupt)

    def keep_choices(self):
        """Remember this window's choices in the wizard's settings.json (its other choices are kept)."""
        choices = wizard.load_choices()
        choices.update(prepare_workspace=self.workspace.GetValue().strip(), prepare_kit=self.kit.GetValue().strip(),
                       prepare_set_aside=self.set_aside.GetValue(), prepare_blur=self.blur.GetValue(),
                       prepare_overlays=self.overlay_key(), prepare_combine=self.combine.GetValue(),
                       prepare_engines=[k for k, box in self.engines.items() if box.GetValue()])
        wizard.save_choices(choices)

    def overlay_key(self):
        """The chosen key of Date stamps and logos."""
        return OVERLAYS[max(0, self.overlays.GetSelection())][0]

    def update_engines(self):
        """Your own trained describer can only be ticked when the kit has a finished training."""
        done = finished_training(self.kit.GetValue().strip())
        self.engines["yours"].Enable(done)
        if not done:
            self.engines["yours"].SetToolTip("No training has finished in this kit yet; when one has, its model can "
                                             "write drafts too (Alt+Y)")

    def update_summary(self):
        """The Workspace summary line: how many pictures are new, have a draft, are described or set aside."""
        folder = self.workspace.GetValue().strip()
        if not self.package or not folder or not self.package.is_workspace(folder):
            self.summary.SetValue("No workspace yet: choose a folder (Alt+B), then add pictures or videos.")
            return
        ws = self.package.open_workspace(folder)
        c = self.package.counts(ws)
        drafted = sum(1 for n in ws.pictures if ws.entry(n).get("draft") and ws.entry(n)["status"] == "new")
        self.summary.SetValue(f"{c['all']} pictures: {c['new']} without a description ({drafted} of them with a "
                              f"draft), {c['described'] + c['checked']} described, {c['checked']} checked, "
                              f"{c['skip']} set aside or skipped.")

    # -- checks before work
    def ready(self, need_kit=False):
        """The workspace (made when the folder is new) when nothing runs and the folders are usable, else None."""
        if self.busy:
            self.say(f"Please wait: {self.busy} is still working. Stop it with Alt+S.")
            return None
        if self.package is None:
            self.say("This program is missing kit\\describe_package.py. Get the newest program.")
            return None
        folder = self.workspace.GetValue().strip()
        if not folder:
            self.say("Choose the workspace folder first (Alt+B).")
            self.workspace.SetFocus()
            return None
        if need_kit:
            if os.name != "nt":
                self.say("The clean-up, the drafts and the videos run in the training kit, which works on Windows "
                         "only.")
                return None
            if not self.kit.GetValue().strip():
                self.say("Choose the training kit folder first (Alt+D).")
                return None
        try:
            ws = (self.package.open_workspace(folder) if self.package.is_workspace(folder)
                  else self.package.make_workspace(folder))
        except Exception as e:  # noqa: BLE001 - said in plain words
            self.say(f"The workspace cannot be used: {e}")
            return None
        self.keep_choices()
        return ws

    # -- the buttons
    def on_browse_workspace(self, _event):
        """Choose the workspace folder."""
        with wx.DirDialog(self, "Choose the workspace folder, or an empty folder for a new one") as d:
            if d.ShowModal() == wx.ID_OK:
                self.workspace.SetValue(d.GetPath())
                self.keep_choices()
                self.update_summary()
                self.say(f"Workspace folder: {d.GetPath()}. {self.summary.GetValue()}")

    def on_browse_kit(self, _event):
        """Choose the training kit folder."""
        with wx.DirDialog(self, "Choose the Picture Model Training Kit folder") as d:
            if d.ShowModal() == wx.ID_OK:
                self.kit.SetValue(d.GetPath())
                self.keep_choices()
                self.update_engines()
                self.say(f"Training kit folder: {d.GetPath()}.")

    def on_add(self, _event):
        """Copy chosen pictures into the workspace."""
        ws = self.ready()
        if ws is None:
            return
        with wx.FileDialog(self, "Choose pictures", wildcard=f"Pictures|{describe_window.PICTURE_FILES}|All files|*.*",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as d:
            if d.ShowModal() != wx.ID_OK:
                return
            paths = d.GetPaths()
        self.start("adding the pictures", lambda: self.package.add_pictures(ws, paths, "", self.queue_line))

    def on_add_folder(self, _event):
        """Copy every picture in a folder and its sub-folders into the workspace."""
        ws = self.ready()
        if ws is None:
            return
        with wx.DirDialog(self, "Choose a folder of pictures (its sub-folders are searched too)") as d:
            if d.ShowModal() != wx.ID_OK:
                return
            folder = d.GetPath()
        self.start("adding the pictures", lambda: self.package.add_pictures(ws, [folder], "", self.queue_line))

    def on_videos(self, _event):
        """Choose videos and options (the Describe pictures video window) and run kit\\run_video.cmd."""
        ws = self.ready(need_kit=True)
        if ws is None:
            return
        with describe_window.VideoDialog(self, wizard) as d:
            if d.ShowModal() != wx.ID_OK:
                return
            args = d.arguments(ws.folder)
        self.run_kit("taking stills from the videos", "run_video.cmd", args, ws)

    def prepare_args(self, job, ws):
        """The command line for kit\\prepare_data.py (job: clean, drafts or all), or None when nothing is chosen."""
        args = [ws.folder, job]
        if job in ("clean", "all"):
            if not self.set_aside.GetValue():
                args.append("--no-set-aside")
            if self.blur.GetValue():
                args.append("--blur-faces")
            if self.overlay_key() != "keep":
                args += ["--overlays", self.overlay_key()]
        if job in ("drafts", "all"):
            engines = [k for k, box in self.engines.items() if box.GetValue() and box.IsEnabled()]
            if not engines:
                self.say("Tick at least one picture model for the drafts (Alt+Q, Alt+I, Alt+R or Alt+Y).")
                return None
            args += ["--engines", ",".join(engines)]
            if not self.combine.GetValue():
                args.append("--no-combine")
        return args

    def on_clean(self, _event):
        """Clean up the new pictures."""
        self.run_job("clean", "cleaning up the pictures")

    def on_drafts(self, _event):
        """Write the drafts."""
        self.run_job("drafts", "writing the drafts")

    def on_all(self, _event):
        """Clean up, then write the drafts."""
        self.run_job("all", "cleaning up and writing the drafts")

    def run_job(self, job, what):
        """Run kit\\prepare_data.py for job."""
        ws = self.ready(need_kit=True)
        if ws is None:
            return
        args = self.prepare_args(job, ws)
        if args is not None:
            self.run_kit(what, "run_prepare.cmd", args, ws)

    def on_review(self, _event):
        """Open the workspace in Describe pictures."""
        ws = self.ready()
        if ws is None:
            return
        choices = wizard.load_choices()
        choices["describe_workspace"] = ws.folder
        wizard.save_choices(choices)
        library = choices.get("library") or None
        with describe_window.DescribeWindow(self, wizard, self.kit.GetValue().strip() or None, library) as window:
            window.ShowModal()
        self.update_summary()
        self.say(f"Back in {TITLE}. {self.summary.GetValue()}")

    def on_stop(self, _event):
        """Stop the work that runs (the drafts carry on from there next time)."""
        if self.process is None or self.process.poll() is not None:
            self.say("Nothing is running.")
            return
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(self.process.pid)], capture_output=True,
                           creationflags=wizard.NO_WINDOW)
        else:
            self.process.kill()
        self.say("Stopping. What was done so far is kept; start it again to carry on.")

    def on_help(self, _event):
        """Open the guide."""
        path = wizard.resource(GUIDE)
        if os.path.exists(path):
            open_file(path)
        else:
            self.say("The guide is missing from the program.")

    # -- background work
    def queue_line(self, text):
        """A line from the background work, shown and said on the window's thread."""
        self.lines.put(("line", str(text)))

    def start(self, what, work):
        """Do work() in the background; what it returns is said at the end."""
        self.busy = what
        self.gauge.Pulse()
        self.say(f"{what.capitalize()}. Please wait.")

        def run():
            """The work, with any error said in plain words."""
            try:
                result = work()
            except Exception as e:  # noqa: BLE001
                result = f"STOPPED: {e}"
            self.lines.put(("done", result or "Finished."))
        threading.Thread(target=run, daemon=True).start()

    def run_kit(self, what, script, args, ws):
        """Copy the kit's files into the kit folder and run one of its .cmd files with args, without a window."""
        kit = self.kit.GetValue().strip()

        def work():
            """Run the kit, pass its lines on, and record new pictures in the workspace afterwards."""
            self.queue_line(f"Copying the kit's files into {kit}. The first time, the tools are installed there too, "
                            "which takes 10 to 30 minutes.")
            wizard.copy_kit(kit)
            path = os.path.join(kit, "kit", script)
            command = f'"{os.environ.get("ComSpec", "cmd.exe")}" /d /s /c ""{path}" {subprocess.list2cmdline(args)}"'
            wizard.log(f"{TITLE}: {command}")
            self.process = subprocess.Popen(command, cwd=kit, env=dict(wizard.kit_environment(kit), KIT_NO_PAUSE="1"),
                                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                                            creationflags=wizard.NO_WINDOW)
            last = ""
            for line in self.process.stdout:
                if line.strip():
                    last = line.strip()
                    self.queue_line(line.rstrip())
            code = self.process.wait()
            self.process = None
            recorded = self.package.register_new(ws)
            if code and not last.startswith("STOPPED"):
                return f"STOPPED: the work ended early. {recorded}"
            return recorded
        self.start(what, work)

    def on_timer(self, _event):
        """Show and say what the background work said; at the end say its result."""
        while True:
            try:
                kind, text = self.lines.get_nowait()
            except queue.Empty:
                break
            if kind == "done":
                self.busy = ""
                self.gauge.SetValue(0 if text.startswith("STOPPED") else 100)
                self.update_summary()
                self.say(f"{text} {self.summary.GetValue()}")
                continue
            count = COUNT_LINE.search(text)
            if count and int(count.group(2)):
                self.gauge.SetValue(min(100, int(count.group(1)) * 100 // int(count.group(2))))
            elif self.busy:
                self.gauge.Pulse()
            self.say(text, interrupt=False, spoken=bool(SPOKEN.match(text)))

    # -- keys and closing
    def on_key(self, event):
        """Escape closes; F1 opens the guide; Alt and a label's letter moves focus to its field."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.Close()
        elif key == wx.WXK_F1:
            self.on_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()

    def on_close(self, event):
        """Close; while work runs, ask first (it carries on from where it stopped next time)."""
        if self.process is not None and self.process.poll() is None and event.CanVeto():
            answer = wx.MessageBox("Work is still running. Stop it and close? What was done so far is kept.", TITLE,
                                   wx.YES_NO | wx.NO_DEFAULT, self)
            if answer != wx.YES:
                event.Veto()
                return
            self.on_stop(None)
        self.timer.Stop()
        if self.workspace and self.kit:
            self.keep_choices()
        self.Destroy()


def self_test():
    """The build's check: the window can be made and the kit's parts are inside the program."""
    for part in (("kit", "prepare_data.py"), ("kit", "run_prepare.cmd"), ("kit", "describe_package.py"), (GUIDE,)):
        if not os.path.exists(wizard.resource(*part)):
            raise SystemExit(f"Missing from the program: {os.path.join(*part)}")
    app = wx.App(False)
    window = PrepareWindow()
    window.timer.Stop()
    window.Destroy()
    app.Destroy()
    print("Self-test passed.")


def main():
    """Start the program (--self-test: the build's check)."""
    if "--self-test" in sys.argv:
        self_test()
        return
    sys.excepthook = wizard.log_crash          # any unexpected error goes into the desktop log, as in the wizard
    threading.excepthook = lambda args: wizard.log_crash(args.exc_type, args.exc_value, args.exc_traceback)
    app = wx.App(False)
    PrepareWindow().Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
