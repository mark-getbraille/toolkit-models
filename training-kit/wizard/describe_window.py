"""The "Describe pictures" window of Picture Model Training: describe pictures together with friends, offline.

Opened from the wizard's first page ("Describe pictures (J)"). A WORKSPACE is a folder of pictures with their
descriptions in text files of the same name, plus the work file describing.json (kit\\describe_package.py does all
the work with the files; this module is only the window). In the window a person:
  - chooses or makes a workspace (Workspace folder, Browse, Open or make the workspace) and writes their name
    (remembered in the wizard's settings.json);
  - goes through the pictures (the Pictures list, with a Filter), sees each one (with the description as its
    alternative text), and writes its Question and Description;
  - saves (Save and next, Ctrl+S), marks a picture checked (a second person confirms it), needing another look or
    skipped, and chooses between two versions of a description (Show the other version);
  - adds pictures, takes stills from videos (kit\\run_video.cmd runs kit\\video_frames.py in the kit's own Python),
    exports a package (a zip) for a friend and imports a friend's package;
  - points "Your own pictures folder" at the workspace for training (Use this workspace for training).

Accessibility (the same rules as the wizard): standard wx controls only; a label ending ":" right before each field
and list; every button and check box has an Alt letter named in its tooltip, no letter twice in a window; Escape
closes; F1 opens "HOW TO DESCRIBE PICTURES WITH FRIENDS.txt", which lists the keyboard commands; Enter presses only
the focused button (no default button). Long tasks move the Progress bar and are said through the screen reader and
in the Status field, and written into the desktop logs.

The letters in the main window: F (Workspace folder), B (Browse), W (Open or make the workspace), M (Your name),
R (Filter), U (Pictures), Q (Question), D (Description), S (Save and next), P (Previous), C (Mark as checked),
N (Needs another look), K (Skip this picture), O (Show the other version), A (Add pictures), V (Take stills from
videos), E (Export a package), I (Import a package), T (Use this workspace for training), H (Help), L (Close).
Keys: Ctrl+S saves, Ctrl+Page Down and Ctrl+Page Up go to the next and previous picture (keeping what was written).
"""

import os
import re
import subprocess
import sys
import threading

import wx

GUIDE = "HOW TO DESCRIBE PICTURES WITH FRIENDS.txt"
PICTURE_BOX = (520, 390)        # the largest size a picture is shown at, in pixels
FILTERS = [("all", "All"), ("not described", "Not described"), ("needs another look", "Needs another look"),
           ("described", "Described (and checked)"), ("checked", "Checked")]
VIDEO_ENDINGS = "*.mp4;*.mov;*.m4v;*.mkv;*.avi;*.webm;*.3gp;*.mts;*.m2ts;*.wmv;*.ogv"
PICTURE_FILES = "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.gif;*.tif;*.tiff"
# The lines of the video tool that are spoken (the rest only go into the Status field and the log).
SPOKEN = re.compile(r"^\s*(Video \d+ of \d+|Online video|Getting ready|STOPPED|Finished|.*still need a description)")


def load_package_module(wizard):
    """The kit's describe_package.py (bundled into the program, or in the kit beside the wizard); None when it
    cannot be loaded."""
    folder = wizard.resource("kit")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    try:
        import describe_package
        return describe_package
    except Exception:  # noqa: BLE001 - said by the caller
        return None


def open_file(path):
    """Open a file or folder with its usual program (Notepad for a .txt file). Never raises."""
    try:
        if hasattr(os, "startfile"):
            os.startfile(path)  # noqa: S606
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:  # noqa: BLE001 - nothing to open with
        pass


# ----------------------------------------------------------------- the shared helpers of every window

class AccessibleDialog(wx.Dialog):
    """A dialog following the accessibility rules: labels before fields, Alt letters in tooltips, Escape closes,
    F1 opens the guide, no default button. The windows below are made from it."""

    def __init__(self, parent, title, wizard, size):
        """Make the dialog with a panel to put the controls on."""
        super().__init__(parent, title=title, size=size, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.wizard = wizard
        self.mnemonics = {}
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def labelled(self, sizer, label, factory, proportion=0, flag=wx.EXPAND):
        """A label ending ":" and, right after it, its control; an &letter in the label moves focus to it."""
        text = wx.StaticText(self.panel, label=label)
        sizer.Add(text, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
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
        c.SetValue(value)
        c.SetToolTip(f"{tip} (Alt+{re.search(r'&(\w)', label).group(1).upper()})")
        return c

    def on_key(self, event):
        """Escape closes; F1 opens the guide; Alt and a label's letter moves focus to its field."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.on_escape()
        elif key == wx.WXK_F1:
            self.on_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()

    def on_escape(self):
        """Escape: close without doing anything."""
        self.EndModal(wx.ID_CANCEL)

    def on_help(self, _event):
        """Open the guide, HOW TO DESCRIBE PICTURES WITH FRIENDS.txt."""
        path = self.wizard.resource(GUIDE)
        if os.path.exists(path):
            open_file(path)
        else:
            self.wizard.speak("The guide is missing from the program.", True)


# ----------------------------------------------------------------- small windows

class NameDialog(AccessibleDialog):
    """Asks the name of a new workspace."""

    def __init__(self, parent, wizard, folder):
        """The workspace name field (the folder's name to start with) and two buttons."""
        super().__init__(parent, "Make a describing workspace", wizard, (520, 230))
        s = wx.BoxSizer(wx.VERTICAL)
        self.field = self.labelled(s, f"Workspace &name (for the new workspace in {folder}):",
                                   lambda: wx.TextCtrl(self.panel, value=os.path.basename(folder.rstrip("\\/"))))
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("&Make the workspace", "Make the workspace in this folder",
                            lambda e: self.EndModal(wx.ID_OK)), 0, wx.ALL, 4)
        row.Add(self.button("&Cancel", "Do not make it", lambda e: self.EndModal(wx.ID_CANCEL)), 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        self.panel.SetSizer(s)
        self.field.SetFocus()


class ExportDialog(AccessibleDialog):
    """Asks which pictures go into a package."""

    def __init__(self, parent, wizard, package):
        """The choice of pictures and two buttons."""
        super().__init__(parent, "Export a package", wizard, (560, 230))
        self.keys = list(package.WHICH)
        s = wx.BoxSizer(wx.VERTICAL)
        self.which = self.labelled(s, "&Which pictures to put in the package:", lambda: wx.Choice(
            self.panel, choices=[f"{k.capitalize()}: {v}" for k, v in package.WHICH.items()]))
        self.which.SetSelection(0)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("&Export...", "Choose where to save the package", lambda e: self.EndModal(wx.ID_OK)),
                0, wx.ALL, 4)
        row.Add(self.button("&Cancel", "Do not export", lambda e: self.EndModal(wx.ID_CANCEL)), 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        self.panel.SetSizer(s)
        self.which.SetFocus()

    def chosen(self):
        """The key of the chosen pictures ("all", "not described", "described" or "to check")."""
        return self.keys[self.which.GetSelection()]


class VideoDialog(AccessibleDialog):
    """Asks for the videos and the options of "Take stills from videos"."""

    def __init__(self, parent, wizard):
        """The video list with its buttons, the options and the start and cancel buttons."""
        super().__init__(parent, "Take stills from videos", wizard, (640, 520))
        s = wx.BoxSizer(wx.VERTICAL)
        self.videos = self.labelled(s, "&Videos:", lambda: wx.ListBox(self.panel, style=wx.LB_EXTENDED), 1)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("&Add videos...", "Choose video files", self.on_add), 0, wx.ALL, 4)
        row.Add(self.button("&Remove the selected videos", "Take them off the list", self.on_remove), 0, wx.ALL, 4)
        s.Add(row, 0, wx.LEFT, 4)
        self.every = self.labelled(s, "At most one picture every how many &seconds:", lambda: wx.SpinCtrlDouble(
            self.panel, min=0.5, max=60, initial=2.0, inc=0.5), flag=0)
        self.language = self.labelled(s, "Spoken &language (en for English, fr, de, es ...):",
                                      lambda: wx.TextCtrl(self.panel, value="en"), flag=0)
        self.speech = self.check("Use what is said in the video as &descriptions",
                                 "Turn the speech into text and give each still what was said at that moment", True)
        s.Add(self.speech, 0, wx.ALL, 6)
        self.blur = self.check("&Blur the faces of people", "Blur every face found in the stills", False)
        s.Add(self.blur, 0, wx.ALL, 6)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("Start &taking stills", "Take the stills and add them to the workspace", self.on_start),
                0, wx.ALL, 4)
        row.Add(self.button("&Help (F1)", "Open the guide", self.on_help), 0, wx.ALL, 4)
        row.Add(self.button("&Cancel", "Do not take stills", lambda e: self.EndModal(wx.ID_CANCEL)), 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        self.panel.SetSizer(s)

    def on_add(self, _event):
        """Choose video files and put them on the list."""
        with wx.FileDialog(self, "Choose videos", wildcard=f"Videos|{VIDEO_ENDINGS}|All files|*.*",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as d:
            if d.ShowModal() == wx.ID_OK:
                for path in d.GetPaths():
                    if path not in self.videos.GetItems():
                        self.videos.Append(path)
                self.wizard.speak(f"Videos on the list: {self.videos.GetCount()}.", True)

    def on_remove(self, _event):
        """Take the selected videos off the list."""
        for index in sorted(self.videos.GetSelections(), reverse=True):
            self.videos.Delete(index)
        self.wizard.speak(f"Videos on the list: {self.videos.GetCount()}.", True)

    def on_start(self, _event):
        """Start, when there is at least one video."""
        if not self.videos.GetCount():
            self.wizard.speak("Add at least one video first (Alt+A).", True)
            return
        self.EndModal(wx.ID_OK)

    def arguments(self, out_folder):
        """The command line for kit\\video_frames.py."""
        args = list(self.videos.GetItems()) + ["--out", out_folder, "--every", f"{self.every.GetValue():g}",
                                               "--language", self.language.GetValue().strip() or "en"]
        if not self.speech.GetValue():
            args.append("--no-speech")
        if self.blur.GetValue():
            args.append("--blur-faces")
        return args


class OtherDialog(AccessibleDialog):
    """Shows a description and its other versions, and lets the person keep one, or a merged one they edit."""

    def __init__(self, parent, wizard, current, others):
        """current: the description in use; others: [(path, person, text)]."""
        super().__init__(parent, "Two versions of a description", wizard, (720, 640))
        self.current, self.others, self.result = current, others, None
        s = wx.BoxSizer(wx.VERTICAL)
        self.in_use = self.labelled(s, "Description in use:", lambda: wx.TextCtrl(
            self.panel, value=current or "(none)", style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        self.which = self.labelled(s, "&Which other version:", lambda: wx.Choice(
            self.panel, choices=[f"By {person} ({os.path.basename(path)})" for path, person, _t in others]))
        self.which.SetSelection(0)
        self.which.Bind(wx.EVT_CHOICE, self.on_which)
        self.other = self.labelled(s, "Other version:", lambda: wx.TextCtrl(
            self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        self.keep = self.labelled(s, "Description to &keep (edit it to merge the two):", lambda: wx.TextCtrl(
            self.panel, value=current, style=wx.TE_MULTILINE), 1)
        row = wx.BoxSizer(wx.HORIZONTAL)
        for b in (self.button("Keep the description in &use", "Keep the description in use; the other versions are "
                              "put away", lambda e: self.finish(self.current)),
                  self.button("Keep the &other version", "Keep the other version shown",
                              lambda e: self.finish(self.others[self.which.GetSelection()][2])),
                  self.button("Keep the &edited description", "Keep what is in Description to keep",
                              lambda e: self.finish(self.keep.GetValue())),
                  self.button("&Cancel", "Decide later", lambda e: self.EndModal(wx.ID_CANCEL))):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        self.panel.SetSizer(s)
        self.on_which(None)
        self.other.SetFocus()

    def on_which(self, _event):
        """Show the chosen other version."""
        self.other.SetValue(self.others[self.which.GetSelection()][2])

    def finish(self, text):
        """Keep text (not an empty one)."""
        if not " ".join(text.split()):
            self.wizard.speak("The description to keep is empty.", True)
            return
        self.result = text
        self.EndModal(wx.ID_OK)


# ----------------------------------------------------------------- the main window

class DescribeWindow(AccessibleDialog):
    """The "Describe pictures" window (see the module docstring)."""

    def __init__(self, parent, wizard, kit=None):
        """wizard: the training_wizard module (its log, speak, settings and kit helpers); kit: the kit folder the
        training uses ("<training folder>\\Picture Model Training Kit"), for taking stills from videos."""
        super().__init__(parent, "Describe pictures", wizard, (1060, 900))
        self.package = load_package_module(wizard)
        self.kit = kit
        self.workspace = None
        self.names = []                 # the pictures in the list (after the filter)
        self.current = None             # the picture shown
        self.loaded = ("", "", "")      # its description, question and notes as loaded (to see changes)
        self.busy = ""                  # what is being done in the background, or ""
        self.process = None             # the video tool while it runs
        self.training_folder = None     # set by "Use this workspace for training"
        chosen = wizard.load_choices()
        s = wx.BoxSizer(wx.VERTICAL)

        top = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.BoxSizer(wx.VERTICAL)
        self.folder = self.labelled(left, "Workspace &folder:", lambda: wx.TextCtrl(
            self.panel, value=chosen.get("describe_workspace", "")))
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.button("&Browse for the workspace folder...", "Choose the workspace folder, or an empty folder "
                            "for a new one", self.on_browse), 0, wx.ALL, 4)
        row.Add(self.button("Open or make the &workspace", "Open the workspace in Workspace folder, or make one there",
                            self.on_open), 0, wx.ALL, 4)
        left.Add(row, 0, wx.LEFT, 2)
        self.person = self.labelled(left, "Your na&me:", lambda: wx.TextCtrl(
            self.panel, value=chosen.get("describe_name", "")))
        self.person.SetToolTip("Saved with each description and check, so the others know who wrote it")
        self.filter = self.labelled(left, "Filte&r:", lambda: wx.Choice(self.panel, choices=[f[1] for f in FILTERS]))
        self.filter.SetSelection(0)
        self.filter.Bind(wx.EVT_CHOICE, self.on_filter)
        self.list = self.labelled(left, "Pict&ures:", lambda: wx.ListBox(self.panel, size=(360, -1)), 1)
        self.list.Bind(wx.EVT_LISTBOX, self.on_select)
        top.Add(left, 0, wx.EXPAND)

        right = wx.BoxSizer(wx.VERTICAL)
        self.picture = self.labelled(right, "Picture:", lambda: wx.StaticBitmap(
            self.panel, bitmap=wx.Bitmap(*PICTURE_BOX), size=PICTURE_BOX), flag=0)
        self.question = self.labelled(right, "&Question:", lambda: wx.TextCtrl(
            self.panel, value=self.package.DEFAULT_QUESTION if self.package else "Describe this picture."))
        self.description = self.labelled(right, "&Description:", lambda: wx.TextCtrl(
            self.panel, style=wx.TE_MULTILINE), 1)
        self.notes = self.labelled(right, "Notes for each other:", lambda: wx.TextCtrl(self.panel))
        top.Add(right, 1, wx.EXPAND)
        s.Add(top, 1, wx.EXPAND)

        actions = wx.WrapSizer(wx.HORIZONTAL)
        for b in (self.button("&Save and next (Ctrl+S saves)", "Save the description and go to the next picture",
                              self.on_save_next),
                  self.button("&Previous", "Go to the previous picture (Ctrl+Page Up)", self.on_previous),
                  self.button("Mark as &checked", "You confirm the description is right", self.on_checked),
                  self.button("&Needs another look", "Mark the picture for another look", self.on_look),
                  self.button("S&kip this picture", "Leave this picture out", self.on_skip)):
            actions.Add(b, 0, wx.ALL, 4)
        self.other_button = self.button("Show the &other version", "Show both versions of the description and "
                                        "choose one, or merge them", self.on_other)
        actions.Add(self.other_button, 0, wx.ALL, 4)
        s.Add(actions, 0, wx.LEFT | wx.RIGHT, 4)

        self.progress = self.labelled(s, "Progress:", lambda: wx.TextCtrl(self.panel, style=wx.TE_READONLY))
        self.status = self.labelled(s, "Status:", lambda: wx.TextCtrl(self.panel, style=wx.TE_READONLY))
        self.gauge = self.labelled(s, "Working:", lambda: wx.Gauge(self.panel, range=100))

        tools = wx.WrapSizer(wx.HORIZONTAL)
        for b in (self.button("&Add pictures...", "Copy pictures or a folder of pictures into the workspace",
                              self.on_add),
                  self.button("Take stills from &videos...", "Turn videos into still pictures for describing",
                              self.on_videos),
                  self.button("&Export a package...", "Make a zip of pictures and descriptions for a friend",
                              self.on_export),
                  self.button("&Import a package...", "Add a friend's package to this workspace", self.on_import),
                  self.button("Use this workspace for &training", "Put this workspace in Your own pictures folder "
                              "and close", self.on_use),
                  self.button("&Help (F1)", "Open the guide", self.on_help),
                  self.button("C&lose", "Close this window (Escape)", lambda e: self.on_escape())):
            tools.Add(b, 0, wx.ALL, 4)
        s.Add(tools, 0, wx.ALL, 4)
        self.panel.SetSizer(s)

        self.pulse = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda e: self.gauge.Pulse(), self.pulse)
        self.Bind(wx.EVT_CLOSE, lambda e: self.on_escape())
        self.show_picture(None)
        if self.package is None:
            self.say("Describing cannot work: the kit's describe_package.py is missing from the program.")
        elif self.folder.GetValue() and self.package.is_workspace(self.folder.GetValue()):
            self.open_folder(self.folder.GetValue())
        else:
            self.say("Choose a workspace folder with Browse (Alt+B), or an empty folder for a new workspace. "
                     "Press F1 for the guide.")
        self.Centre()

    # -- speaking and the status
    def say(self, text, interrupt=True):
        """Put text in the Status field, write it into the desktop log and have the screen reader say it."""
        if not self:                                   # the window was closed meanwhile
            return
        self.status.SetValue(" ".join(text.split()))
        self.wizard.log("Describe pictures: " + text)
        self.wizard.speak(" ".join(text.split()), interrupt)

    def ready(self, need_picture=False):
        """True when a workspace is open (and a picture shown, with need_picture) and nothing runs in the
        background; otherwise it says why not."""
        if self.busy:
            self.say(f"Please wait: {self.busy} is still working.")
        elif self.workspace is None:
            self.say("Open or make a workspace first: choose its folder with Browse (Alt+B).")
        elif need_picture and self.current is None:
            self.say("There is no picture to work on. Add pictures (Alt+A), or choose All in Filter.")
        else:
            return True
        return False

    def keep_settings(self):
        """Remember the name and the workspace folder in settings.json (the wizard's other choices are kept)."""
        choices = self.wizard.load_choices()
        choices["describe_name"] = self.person.GetValue().strip()
        choices["describe_workspace"] = self.workspace.folder if self.workspace else self.folder.GetValue().strip()
        self.wizard.save_choices(choices)

    # -- background work
    def run_task(self, what, work, then=None):
        """Do work(say) in the background (what: a few words saying what it is); its progress lines are said; the
        summary it returns is said at the end, and then() runs on the window's thread."""
        self.busy = what
        self.pulse.Start(150)
        self.say(f"{what.capitalize()}. Please wait.")

        def run():
            """The background part."""
            try:
                summary = work(lambda text: wx.CallAfter(self.say, text, False))
            except self.package.PackageProblem as e:
                summary = str(e)
            except Exception as e:  # noqa: BLE001 - said in plain words
                summary = f"That did not work: {e}"
            wx.CallAfter(self.task_done, summary, then)
        threading.Thread(target=run, daemon=True).start()

    def task_done(self, summary, then):
        """The background work has finished: stop the bar, say the summary and refresh the list."""
        if not self:
            return
        self.busy = ""
        self.pulse.Stop()
        self.gauge.SetValue(100)
        if self.workspace is not None:
            try:
                self.workspace = self.package.open_workspace(self.workspace.folder)
            except self.package.PackageProblem as e:
                summary += " " + str(e)
        if then:
            then()
        self.refresh(self.current)
        self.say(summary)

    # -- the workspace
    def on_browse(self, _event):
        """Choose the workspace folder, and open it (or offer to make a workspace there)."""
        if self.busy:
            self.ready()
            return
        with wx.DirDialog(self, "Choose the workspace folder, or an empty folder for a new workspace",
                          self.folder.GetValue()) as d:
            if d.ShowModal() == wx.ID_OK:
                self.folder.SetValue(d.GetPath())
                self.open_folder(d.GetPath())

    def on_open(self, _event):
        """Open the workspace in Workspace folder, or make one there."""
        if self.busy:
            self.ready()
            return
        folder = self.folder.GetValue().strip()
        if not folder:
            self.say("Write or choose a folder in Workspace folder first (Browse, Alt+B).")
            return
        self.open_folder(folder)

    def open_folder(self, folder, make_name=None):
        """Open the workspace in folder; when it is not one, ask its name and make it (make_name: the name to use
        without asking, for tests). Pictures already in the folder are recorded."""
        if self.package is None:
            return
        self.save_changes()
        if not self.package.is_workspace(folder):
            if make_name is None:
                with NameDialog(self, self.wizard, folder) as d:
                    if d.ShowModal() != wx.ID_OK:
                        self.say("No workspace was made.")
                        return
                    make_name = d.field.GetValue()
            try:
                self.workspace = self.package.make_workspace(folder, make_name)
            except (OSError, self.package.PackageProblem) as e:
                self.say(f"The workspace could not be made in {folder}: {e}")
                return
            made = f"A new workspace, {self.workspace.name}, was made in {folder}. "
        else:
            try:
                self.workspace = self.package.open_workspace(folder)
                self.package.register_new(self.workspace)
            except (OSError, self.package.PackageProblem) as e:
                self.say(str(e))
                return
            made = f"Workspace {self.workspace.name} opened. "
        self.folder.SetValue(self.workspace.folder)
        self.keep_settings()
        self.current = None
        self.refresh(None)
        self.say(made + self.progress.GetValue() + " The Pictures list is next; press Alt+U to go there.")

    # -- the list
    def filter_key(self):
        """The chosen filter ("all", "not described" ...)."""
        return FILTERS[self.filter.GetSelection()][0]

    def refresh(self, keep=None):
        """Fill the Pictures list again (after the filter) and show keep, or the first picture, or the nearest one
        to where the list was."""
        if self.workspace is None:
            return
        old_index = self.names.index(self.current) if self.current in self.names else 0
        self.names = self.package.picture_names(self.workspace, self.filter_key())
        self.list.Set([f"{n}: {self.workspace.entry(n)['status']}" for n in self.names])
        if keep in self.names:
            index = self.names.index(keep)
        elif self.names:
            index = min(old_index, len(self.names) - 1)
        else:
            index = None
        if index is None:
            self.show_picture(None)
        else:
            self.list.SetSelection(index)
            self.show_picture(self.names[index])

    def update_progress(self):
        """The Progress line: "Picture 14 of 120. 63 described, 20 checked." (with the filter when one is chosen)."""
        if self.workspace is None:
            self.progress.SetValue("No workspace is open.")
            return
        c = self.package.counts(self.workspace)
        shown = f"Picture {self.names.index(self.current) + 1} of {len(self.names)}." if self.current in self.names \
            else f"No pictures shown ({len(self.names)} in the list)."
        if self.filter_key() != "all":
            shown += f" Filter: {FILTERS[self.filter.GetSelection()][1]}, of {c['all']} pictures in all."
        text = f"{shown} {c['described'] + c['checked']} described, {c['checked']} checked."
        if c["needs another look"]:
            text += f" {c['needs another look']} need another look."
        self.progress.SetValue(text)

    def on_filter(self, _event):
        """Another filter: fill the list again and say how many pictures it shows."""
        if self.workspace is None:
            return
        self.save_changes()
        self.refresh(self.current)
        self.say(f"{len(self.names)} {'picture' if len(self.names) == 1 else 'pictures'} shown. "
                 f"{self.progress.GetValue()}")

    def on_select(self, _event):
        """A picture chosen in the list: keep what was written for the one before, and show it."""
        index = self.list.GetSelection()
        if index == wx.NOT_FOUND or index >= len(self.names) or self.names[index] == self.current:
            return
        self.save_changes()
        name = self.names[index]
        self.refresh(name)

    # -- showing a picture
    def show_picture(self, name):
        """Show a picture (None: none), its question, description and notes, with the description as the picture's
        alternative text."""
        self.current = name
        bitmap = wx.Bitmap(*PICTURE_BOX)
        if name is None or self.workspace is None:
            text, question, notes, alt = "", "", "", "No picture."
        else:
            entry = self.workspace.entry(name)
            text = self.package.description(self.workspace, name)
            question, notes = self.package.question_of(self.workspace, name), entry["notes"]
            alt = text or "No description yet"
            bitmap = self.scaled(self.workspace.path(name)) or bitmap
        self.picture.SetBitmap(bitmap)
        for setter in (self.picture.SetLabel, self.picture.SetName, self.picture.SetToolTip):
            setter(alt)                                # the picture's alternative text for the screen reader
        self.question.SetValue(question or (self.package.DEFAULT_QUESTION if self.package else ""))
        self.description.SetValue(text)
        self.notes.SetValue(notes)
        self.loaded = (text, self.question.GetValue(), notes)
        has_other = bool(name and self.workspace and self.package.other_versions(self.workspace, name))
        self.other_button.Enable(has_other)
        self.update_progress()
        self.panel.Layout()

    def scaled(self, path):
        """The picture at path as a bitmap fitting in PICTURE_BOX, or None when it cannot be shown."""
        with wx.LogNull():                              # no message boxes for a picture wx cannot read
            image = wx.Image(path)
        if not image.IsOk():
            try:
                from PIL import Image
                with Image.open(path) as picture:
                    picture = picture.convert("RGB")
                    image = wx.Image(picture.width, picture.height, picture.tobytes())
            except Exception:  # noqa: BLE001 - shown as an empty picture
                return None
        width, height = image.GetWidth(), image.GetHeight()
        share = min(PICTURE_BOX[0] / width, PICTURE_BOX[1] / height, 1)
        image = image.Scale(max(1, int(width * share)), max(1, int(height * share)), wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image)

    def announce(self):
        """Say where we are and the picture's status and description."""
        if self.current is None:
            self.say("No more pictures in this list. " + self.progress.GetValue())
            return
        entry = self.workspace.entry(self.current)
        text = self.description.GetValue().strip()
        others = " It has another version: Show the other version, Alt+O." if self.other_button.IsEnabled() else ""
        self.say(f"{self.progress.GetValue().split('.')[0]}: {self.current}, {entry['status']}. "
                 + (f"Description: {text}" if text else "No description yet.") + others)

    # -- saving
    def changed(self):
        """True when the description, question or notes were changed since the picture was shown."""
        return (self.description.GetValue(), self.question.GetValue(), self.notes.GetValue()) != self.loaded

    def need_person(self):
        """True when Your name is filled in; otherwise it says so and goes there."""
        if self.person.GetValue().strip():
            return True
        self.say("Write your name in Your name first (Alt+M), so the others know who wrote it.")
        self.person.SetFocus()
        return False

    def save_changes(self, force=False):
        """Save what was written for the shown picture when it was changed (force: also an unchanged description,
        which then counts as described). True when it is saved or nothing needed saving."""
        if self.workspace is None or self.current is None or not (force or self.changed()):
            return True
        if not self.need_person():
            return False
        name, person = self.current, self.person.GetValue().strip()
        text = self.description.GetValue()
        try:
            if self.notes.GetValue() != self.loaded[2]:
                self.package.set_notes(self.workspace, name, self.notes.GetValue())
            if text.strip() or self.loaded[0]:
                self.package.describe(self.workspace, name, text, person, self.question.GetValue())
        except OSError as e:
            self.say(f"The description could not be saved: {e}")
            return False
        self.loaded = (text, self.question.GetValue(), self.notes.GetValue())
        self.keep_settings()
        return True

    def move(self, step):
        """Go step pictures on (1 next, -1 previous) in the list."""
        if self.current not in self.names:
            self.refresh(None)
        else:
            index = self.names.index(self.current) + step
            if 0 <= index < len(self.names):
                self.refresh(self.names[index])
            else:
                self.refresh(self.current)
                self.say("That was the " + ("last" if step > 0 else "first") + " picture in the list. "
                         + self.progress.GetValue())
                return
        self.announce()

    def after_change(self, saved_message):
        """After a picture's status changed: go to the next picture in the list (the changed one may have left the
        list because of the filter) and say what happened."""
        name = self.current
        index = self.names.index(name) if name in self.names else 0
        next_name = self.names[index + 1] if index + 1 < len(self.names) else None
        self.refresh(next_name or name)
        self.description.SetFocus()
        if next_name is None and self.current == name:
            self.say(f"{saved_message} That was the last picture in the list. {self.progress.GetValue()}")
        else:
            self.say(saved_message)
            self.announce()

    # -- the buttons
    def on_save_next(self, _event):
        """Save and go to the next picture."""
        if not self.ready(need_picture=True):
            return
        if not self.description.GetValue().strip() and not self.loaded[0]:
            if self.changed() and not self.save_changes():
                return
            self.after_change("Nothing was written, so the picture stays not described.")
            return
        if self.save_changes(force=True):
            self.after_change(f"Saved: {self.current}, {self.workspace.entry(self.current)['status']}.")

    def save_only(self):
        """Ctrl+S: save and stay on the picture."""
        if self.ready(need_picture=True) and self.save_changes(force=bool(self.description.GetValue().strip())):
            self.refresh(self.current)
            self.say(f"Saved: {self.current}, {self.workspace.entry(self.current)['status']}.")

    def on_previous(self, _event):
        """Go to the previous picture (what was written is kept)."""
        if self.ready(need_picture=True) and self.save_changes():
            self.move(-1)

    def next_picture(self):
        """Ctrl+Page Down: go to the next picture (what was written is kept)."""
        if self.ready(need_picture=True) and self.save_changes():
            self.move(1)

    def on_checked(self, _event):
        """Mark the picture as checked: a second person confirms the description is right."""
        if not self.ready(need_picture=True) or not self.need_person():
            return
        person = self.person.GetValue().strip()
        if not self.save_changes():
            return
        entry = self.workspace.entry(self.current)
        if entry["described_by"] and entry["described_by"].lower() == person.lower():
            answer = wx.MessageBox(f"You described this picture yourself, {person}. Usually a second person checks "
                                   "it. Mark it as checked anyway?", "Describe pictures", wx.YES_NO | wx.NO_DEFAULT,
                                   self)
            if answer != wx.YES:
                return
        try:
            self.package.mark_checked(self.workspace, self.current, person)
        except self.package.PackageProblem as e:
            self.say(str(e))
            return
        self.after_change(f"Checked by {person}: {self.current}.")

    def on_look(self, _event):
        """Mark the picture as needing another look (a note in Notes for each other says why)."""
        if self.ready(need_picture=True) and self.save_changes():
            self.package.set_status(self.workspace, self.current, self.package.LOOK, self.person.GetValue())
            self.after_change(f"Marked as needing another look: {self.current}. "
                              + ("" if self.notes.GetValue().strip() else
                                 "Tip: write why in Notes for each other next time."))

    def on_skip(self, _event):
        """Skip the picture: it is left out of the training."""
        if self.ready(need_picture=True) and self.save_changes():
            self.package.set_status(self.workspace, self.current, self.package.SKIP, self.person.GetValue())
            self.after_change(f"Skipped: {self.current}. It is left out of the training.")

    def on_other(self, _event):
        """Show the description and its other versions, and keep one (or a merged one)."""
        if not self.ready(need_picture=True) or not self.need_person() or not self.save_changes():
            return
        others = self.package.other_versions(self.workspace, self.current)
        if not others:
            self.say("This picture has no other version.")
            return
        with OtherDialog(self, self.wizard, self.package.description(self.workspace, self.current), others) as d:
            self.wizard.speak(f"Two versions. In use: {d.current or 'none'}. Other version: {others[0][2]}", True)
            if d.ShowModal() != wx.ID_OK:
                self.say("Nothing was changed. The picture still needs another look.")
                return
            self.package.resolve(self.workspace, self.current, d.result, self.person.GetValue().strip())
        self.refresh(self.current)
        self.say(f"Kept: {d.result} The other versions are put away in the hidden folder .resolved versions.")

    def on_add(self, _event):
        """Copy pictures into the workspace (files, or a whole folder when none are chosen)."""
        if not self.ready() or not self.save_changes():
            return
        with wx.FileDialog(self, "Choose pictures (Cancel to choose a whole folder instead)",
                           wildcard=f"Pictures|{PICTURE_FILES}|All files|*.*",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST) as d:
            paths = d.GetPaths() if d.ShowModal() == wx.ID_OK else []
        if not paths:
            with wx.DirDialog(self, "Choose a folder of pictures to add") as d:
                if d.ShowModal() != wx.ID_OK:
                    self.say("No pictures were added.")
                    return
                paths = [d.GetPath()]
        workspace, person = self.workspace, self.person.GetValue().strip()
        self.run_task("adding the pictures", lambda say: self.package.add_pictures(workspace, paths, person, say))

    def on_export(self, _event):
        """Make a package of the chosen pictures, for a friend."""
        if not self.ready() or not self.need_person() or not self.save_changes():
            return
        with ExportDialog(self, self.wizard, self.package) as d:
            if d.ShowModal() != wx.ID_OK:
                return
            which = d.chosen()
        person = self.person.GetValue().strip()
        import time
        default = re.sub(r'[<>:"/\\|?*]', "_", f"{self.workspace.name} - {which} - {person} - "
                                               f"{time.strftime('%Y-%m-%d')}.zip")
        with wx.FileDialog(self, "Save the package as", defaultFile=default, wildcard="Zip files|*.zip",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as d:
            if d.ShowModal() != wx.ID_OK:
                return
            out = d.GetPath()
        if not out.lower().endswith(".zip"):
            out += ".zip"
        workspace = self.workspace
        self.run_task("making the package",
                      lambda say: self.package.export_package(workspace, out, which, person, say))

    def on_import(self, _event):
        """Merge a friend's package into the workspace."""
        if not self.ready() or not self.save_changes():
            return
        with wx.FileDialog(self, "Choose the package to import", wildcard="Zip files|*.zip",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as d:
            if d.ShowModal() != wx.ID_OK:
                return
            path = d.GetPath()
        workspace = self.workspace
        self.run_task("importing the package", lambda say: self.package.import_package(workspace, path, say))

    def on_use(self, _event):
        """Put the workspace in the main window's "Your own pictures folder" and close."""
        if not self.ready() or not self.save_changes():
            return
        c = self.package.counts(self.workspace)
        ready = c["described"] + c["checked"]
        if not ready:
            self.say("No picture is described or checked yet, so there is nothing to train on.")
            return
        self.training_folder = self.workspace.folder
        self.keep_settings()
        self.wizard.speak(f"Your own pictures folder is now the workspace. {ready} described or checked pictures "
                          "are used for training; the others are left out.", True)
        self.EndModal(wx.ID_OK)

    # -- taking stills from videos
    def on_videos(self, _event):
        """Choose videos and options, then run kit\\run_video.cmd (kit\\video_frames.py in the kit's own Python)
        into the workspace, and record the new stills."""
        if not self.ready() or not self.save_changes():
            return
        if not os.path.exists(self.wizard.resource("kit", "video_frames.py")):
            self.say("Taking stills from videos is not in this version of the program yet (kit\\video_frames.py is "
                     "missing). Get the newest program.")
            return
        if os.name != "nt":
            self.say("Taking stills from videos works on Windows only.")
            return
        if not self.kit:
            self.say("Choose the training folder in the main window first: the video tools are installed there.")
            return
        with VideoDialog(self, self.wizard) as d:
            if d.ShowModal() != wx.ID_OK:
                return
            args = d.arguments(self.workspace.folder)
        workspace = self.workspace

        def work(say):
            """Copy the kit, run the video tool and record the stills."""
            say(f"Copying the kit's files into {self.kit}. The first time, the tools are installed there too, which "
                "takes 10 to 30 minutes.")
            self.wizard.copy_kit(self.kit)
            script = os.path.join(self.kit, "kit", "run_video.cmd")
            command = f'"{os.environ.get("ComSpec", "cmd.exe")}" /d /s /c ""{script}" {subprocess.list2cmdline(args)}"'
            env = dict(self.wizard.kit_environment(self.kit), KIT_NO_PAUSE="1")
            self.wizard.log(f"Take stills from videos: {command}")
            self.process = subprocess.Popen(command, cwd=self.kit, env=env, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                            encoding="utf-8", errors="replace", creationflags=self.wizard.NO_WINDOW)
            last = []
            for line in self.process.stdout:
                line = line.rstrip()
                if not line:
                    continue
                last = (last + [line])[-12:]
                if SPOKEN.match(line):
                    say(line.strip())
                else:
                    wx.CallAfter(self.quiet_status, line)
            self.process.wait()
            self.process = None
            recorded = self.package.register_new(workspace)
            finished = [x for x in last if x.startswith(("Finished", "STOPPED"))]
            return " ".join(finished[-1:] + [recorded])
        self.run_task("taking stills from the videos", work)

    def quiet_status(self, line):
        """A line of the video tool that is not spoken: shown in Status and written into the log."""
        if self:
            self.status.SetValue(line.strip())
            self.wizard.log("Describe pictures: " + line)

    # -- keys and closing
    def on_key(self, event):
        """Besides Escape, F1 and the Alt letters: Ctrl+S saves, Ctrl+Page Down and Ctrl+Page Up go to the next and
        previous picture."""
        key = event.GetKeyCode()
        if event.ControlDown() and not event.AltDown():
            if key in (ord("S"), ord("s")):
                self.save_only()
                return
            if key in (wx.WXK_PAGEDOWN, wx.WXK_NUMPAD_PAGEDOWN):
                self.next_picture()
                return
            if key in (wx.WXK_PAGEUP, wx.WXK_NUMPAD_PAGEUP):
                self.on_previous(None)
                return
        super().on_key(event)

    def on_escape(self):
        """Close: keep what was written; while stills are being taken, ask first."""
        if self.process is not None and self.process.poll() is None:
            answer = wx.MessageBox("Stills are still being taken from the videos. Stop and close? Videos already done "
                                   "are kept.", "Describe pictures", wx.YES_NO | wx.NO_DEFAULT, self)
            if answer != wx.YES:
                return
            subprocess.run(["taskkill", "/PID", str(self.process.pid), "/T", "/F"], capture_output=True,
                           creationflags=self.wizard.NO_WINDOW)
        elif self.busy:
            self.say(f"Please wait: {self.busy} is still working.")
            return
        if not self.save_changes():
            answer = wx.MessageBox("What you wrote for this picture is not saved, because Your name is empty. Close "
                                   "anyway and lose it?", "Describe pictures", wx.YES_NO | wx.NO_DEFAULT, self)
            if answer != wx.YES:
                return
        self.pulse.Stop()
        self.keep_settings()
        if self.IsModal():
            self.EndModal(wx.ID_CANCEL)
        else:
            self.Destroy()
