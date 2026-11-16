"""Picture Model Training: the one-click wizard of the Picture Model Training Kit (Picture Model Training.exe).

It does what the kit's .cmd files do, in one window that a screen reader user can follow:
  1. the first page: the training folder (C:\\Training by default), the model (4B or 8B), how much to train (a quick
     try, normal, or full: several days), Wikipedia or not, and whether to prepare this computer first; "Check this
     computer" says the NVIDIA card, its memory and the free disk space;
  2. "Start training": the kit's files are copied into "<folder>\\Picture Model Training Kit" (a newer wizard
     updates them; the downloads, pictures, training and results there are kept), "Prepare This Computer.cmd" runs
     as administrator when asked for, the helper uv and the training tools are installed once into the kit folder,
     and kit\\train.py runs without a console window;
  3. the progress page: every line the training says goes into "Everything said:", the latest into "Status:", and
     the important ones (each step, each collection, the training progress every 200 pictures, FINISHED or STOPPED)
     are spoken by the running screen reader (Tolk, through cytolk, as in the Digital Accessibility Toolkit).
     "Read the status" says the status and the percent again; the log, the report and the result folder open from
     their buttons; "Stop the training" stops it (starting again carries on from the last save).

Accessibility: standard wx controls only; a label ending ":" right before each field; every button and check box
has an Alt letter, named in its tooltip, and no letter is used twice in the window; Escape closes (asking first while
training runs); F1 opens READ ME FIRST.txt; Enter presses only the focused button (no default button).

Logs: like the Digital Accessibility Toolkit, everything the wizard says (and any error) is written, with the time,
into "Picture Model Training logs" on the desktop, one file a day ("Picture Model Training log 2026-11-16.txt");
when the training has finished, its report and full log are copied there too. Files older than 30 days are deleted.

Nothing is sent anywhere: the wizard and the kit only download the helper, the tools, the model and the pictures.
"""

import hashlib
import io
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import urllib.request
import zipfile

import wx

APP_NAME = "Picture Model Training"
UV_URL = "https://github.com/astral-sh/uv/releases/download/0.9.5/uv-x86_64-pc-windows-msvc.zip"
TORCH_INDEX = "https://download.pytorch.org/whl/cu128"
KIT_NAME = "Picture Model Training Kit"
DEFAULT_FOLDER = "C:\\Training"
MODELS = [("4b", "Qwen3-VL 4B (needs an NVIDIA card with 12 GB or more)"),
          ("8b", "Qwen3-VL 8B (needs 16 GB or more; train the 4B model first)")]
SIZES = [("quick", "Quick try: a tenth of the pictures, an hour or two"),
         ("normal", "Normal: about 44,000 pictures, roughly a day"),
         ("full", "Full: about 110,000 pictures, roughly three days (the best result)")]
NO_WINDOW = 0x08000000 if os.name == "nt" else 0          # CREATE_NO_WINDOW

# Where the training is, as a share of the whole run (the progress bar): each step's start and end percent.
STEP_SPAN = {1: (0, 1), 2: (1, 6), 3: (6, 16), 4: (16, 20), 5: (20, 92), 6: (92, 99), 7: (99, 100)}
STEP_LINE = re.compile(r"^Step (\d) of 7:")
TRAINED_LINE = re.compile(r"(\d+) of (\d+) pictures trained \((\d+) percent\)")
SPOKEN = re.compile(r"^(Step \d of 7:|\s*Collection \d+ of \d+:|\s*Ready:|\s+\d+ of \d+ pictures trained|"
                    r"\s*Score (before|after)|FINISHED|STOPPED|Getting ready|\s*This collection could not)")


def resource(*parts):
    """A file bundled with the program (PyInstaller's folder when frozen, else the kit beside this file)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bundled = os.path.join(base, "training-kit", *parts)
    return bundled if os.path.exists(bundled) else os.path.join(base, *parts)


# ----------------------------------------------------------------- the logs on the desktop

LOG_FOLDER_NAME = f"{APP_NAME} logs"   # like the Digital Accessibility Toolkit's "... logs" folder
KEEP_DAYS = 30


def desktop_dir():
    """The user's desktop folder (also when Windows keeps it in OneDrive)."""
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            class GUID(ctypes.Structure):
                """A Windows GUID, for SHGetKnownFolderPath's folder id."""
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                            ("Data4", ctypes.c_ubyte * 8)]
            # FOLDERID_Desktop {B4BFCC3A-DB2C-424C-B029-7FE99A87C641}
            guid = GUID(0xB4BFCC3A, 0xDB2C, 0x424C, (ctypes.c_ubyte * 8)(0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87,
                                                                        0xC6, 0x41))
            path = ctypes.c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(path)) == 0:
                result = path.value
                ctypes.windll.ole32.CoTaskMemFree(path)
                if result:
                    return result
        except Exception:  # noqa: BLE001 - the usual place then
            pass
    return os.path.join(os.environ.get("USERPROFILE") or os.path.expanduser("~"), "Desktop")


def log_folder():
    """The "Picture Model Training logs" folder on the desktop (made when missing; files older than KEEP_DAYS days
    are deleted)."""
    import time
    folder = os.path.join(desktop_dir(), LOG_FOLDER_NAME)
    os.makedirs(folder, exist_ok=True)
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        try:
            if os.path.isfile(path) and time.time() - os.path.getmtime(path) > KEEP_DAYS * 86400:
                os.remove(path)
        except OSError:
            pass
    return folder


_log_lock = threading.Lock()


def log(text):
    """Add text to today's log on the desktop ("Picture Model Training log 2026-11-16.txt"), each line with the
    time. Never raises."""
    import time
    try:
        path = os.path.join(log_folder(), f"{APP_NAME} log {time.strftime('%Y-%m-%d')}.txt")
        stamp = time.strftime("%H:%M:%S ")
        with _log_lock, open(path, "a", encoding="utf-8") as f:
            f.write("".join(stamp + line + "\n" for line in (str(text).splitlines() or [""])))
    except Exception:  # noqa: BLE001 - the log never stops the wizard
        pass


def copy_to_logs(path):
    """Copy a file (the report) into the logs folder on the desktop. Never raises."""
    try:
        shutil.copy2(path, os.path.join(log_folder(), os.path.basename(path)))
    except Exception:  # noqa: BLE001
        pass


# ----------------------------------------------------------------- speech

_tolk = None
_tolk_tried = False


def speak(text, interrupt=False):
    """Have the running screen reader say text (Tolk through cytolk); does nothing without one. Never raises."""
    global _tolk, _tolk_tried
    if not _tolk_tried:
        _tolk_tried = True
        try:
            from cytolk import tolk
            tolk.load()
            _tolk = tolk
        except Exception:  # noqa: BLE001 - no screen reader library: the Status field still shows it
            _tolk = None
    if _tolk is not None:
        try:
            _tolk.output(text, interrupt)
        except Exception:  # noqa: BLE001 - never breaks the wizard
            pass


# ----------------------------------------------------------------- the computer

def nvidia_smi():
    """The NVIDIA tool's path (in the search path, or the older drivers' NVSMI folder), or None."""
    found = shutil.which("nvidia-smi")
    if found:
        return found
    for folder in (os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "NVIDIA Corporation", "NVSMI"),
                   os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")):
        path = os.path.join(folder, "nvidia-smi.exe")
        if os.path.exists(path):
            return path
    return None


def check_computer(folder):
    """Plain sentences about the NVIDIA card and the free space where the kit goes, and whether training can start
    ([sentences], ready)."""
    lines, ready = [], True
    tool = nvidia_smi()
    if tool is None:
        lines.append("No NVIDIA graphics card driver was found. The training needs an NVIDIA card with 12 GB or more.")
        ready = False
    else:
        try:
            out = subprocess.run([tool, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                                 capture_output=True, text=True, timeout=30, creationflags=NO_WINDOW).stdout
            name, memory = [x.strip() for x in out.strip().splitlines()[0].split(",")[:2]]
            gb = int(memory) / 1024
            lines.append(f"Graphics card: {name}, {gb:.0f} GB of memory.")
            if gb < 11.5:
                lines.append("That is less than the 12 GB the training needs.")
                ready = False
        except Exception as e:  # noqa: BLE001 - said
            lines.append(f"The NVIDIA card could not be read ({e}).")
            ready = False
    drive = os.path.splitdrive(os.path.abspath(folder))[0] + "\\"
    try:
        free = shutil.disk_usage(drive).free / 1024 ** 3
        lines.append(f"Free disk space on {drive}: {free:,.0f} GB.")
        if free < 90:
            lines.append("The training needs about 90 GB: choose a folder on a bigger drive.")
            ready = False
    except OSError:
        lines.append(f"The drive {drive} could not be found.")
        ready = False
    lines.append("This computer is ready to train." if ready else "Training cannot start until this is solved.")
    return lines, ready


# ----------------------------------------------------------------- setting up the kit folder

def copy_kit(kit):
    """Copy the kit's own files (the .cmd files, READ ME FIRST.txt and the kit folder) into kit, replacing older
    copies; work, env, tools and result are never touched."""
    source = resource()
    os.makedirs(os.path.join(kit, "kit"), exist_ok=True)
    for name in os.listdir(source):
        path = os.path.join(source, name)
        if name in ("wizard", "__pycache__") or name.startswith("."):
            continue
        if os.path.isdir(path):
            for inner in os.listdir(path):
                if inner.endswith((".py", ".txt", ".cmd")):
                    shutil.copy2(os.path.join(path, inner), os.path.join(kit, name, inner))
        elif name.endswith((".cmd", ".txt")):
            shutil.copy2(path, os.path.join(kit, name))


def run_quiet(command, cwd, env=None):
    """Run a command without a window; raises RuntimeError with its last output line when it fails."""
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, creationflags=NO_WINDOW)
    if done.returncode != 0:
        last = (done.stderr or done.stdout or "").strip().splitlines()
        raise RuntimeError(last[-1] if last else f"{command[0]} failed")


def kit_environment(kit):
    """The environment the training runs in: its caches inside the kit folder, plain output for the wizard."""
    env = dict(os.environ, UV_CACHE_DIR=os.path.join(kit, "work", "uv-cache"),
               UV_PYTHON_INSTALL_DIR=os.path.join(kit, "tools", "python"), HF_HOME=os.path.join(kit, "work", "hf-cache"),
               PYTHONUTF8="1", PYTHONUNBUFFERED="1", TRANSFORMERS_VERBOSITY="error", PYTHONWARNINGS="ignore")
    return env


def install_tools(kit, report):
    """Download the helper uv and install the kit's own Python and training tools once (again when the kit's
    requirements change). report(text) says what happens."""
    tools = os.path.join(kit, "tools")
    os.makedirs(tools, exist_ok=True)
    uv = os.path.join(tools, "uv.exe")
    if not os.path.exists(uv):
        report("Getting ready: downloading the installer helper, about 20 MB.")
        request = urllib.request.Request(UV_URL, headers={"User-Agent": APP_NAME})
        with urllib.request.urlopen(request, timeout=300) as r:
            zipfile.ZipFile(io.BytesIO(r.read())).extractall(tools)
    requirements = os.path.join(kit, "kit", "requirements.txt")
    with open(requirements, "rb") as f:
        wanted = hashlib.sha256(f.read()).hexdigest()
    mark = os.path.join(kit, "env", "installed.txt")
    if os.path.exists(mark) and open(mark, encoding="utf-8").read().strip() == wanted:
        return
    report("Getting ready: installing the training tools in the kit folder, about 5 GB. This takes 10 to 30 minutes, "
           "and nothing is said while it works.")
    env = kit_environment(kit)
    if not os.path.exists(os.path.join(kit, "env", "Scripts", "python.exe")):
        run_quiet([uv, "venv", "env", "--python", "3.12", "--quiet"], kit, env)
    run_quiet([uv, "pip", "install", "--python", os.path.join("env", "Scripts", "python.exe"), "-r", requirements,
               "--extra-index-url", TORCH_INDEX, "--index-strategy", "unsafe-best-match", "--quiet"], kit, env)
    with open(mark, "w", encoding="utf-8") as f:
        f.write(wanted)
    report("Getting ready: the training tools are installed.")


def prepare_computer(kit, report):
    """Run "Prepare This Computer.cmd" as administrator (Windows asks first) and wait for it."""
    report("Preparing this computer. Windows asks for administrator permission: answer Yes.")
    script = os.path.join(kit, "Prepare This Computer.cmd")
    command = (f"Start-Process -FilePath $env:ComSpec -ArgumentList '/c \"\"{script}\" /nopause\"' -Verb RunAs "
               "-Wait")
    done = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True,
                          creationflags=NO_WINDOW)
    if done.returncode != 0:
        report("This computer was not prepared (the permission was not given). The training goes on anyway; keep the "
               "computer from sleeping yourself.")
    else:
        report("This computer is prepared: no sleep, no hibernation, Windows Update paused for 7 days.")


# ----------------------------------------------------------------- the window

class Wizard(wx.Frame):
    """The wizard's one window, with its two pages (see the module docstring)."""

    def __init__(self):
        """Build both pages; the first is shown."""
        super().__init__(None, title=APP_NAME, size=(760, 640))
        self.process = None
        self.lines = queue.Queue()
        self.percent = 0
        self.kit = None
        self.mnemonics = {}
        self.panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        self.first = self.build_first(self.panel)
        self.second = self.build_second(self.panel)
        outer.Add(self.first, 1, wx.EXPAND)
        outer.Add(self.second, 1, wx.EXPAND)
        self.close_button = self.button(self.panel, "C&lose", "Close the wizard", self.on_close)
        outer.Add(self.close_button, 0, wx.ALL | wx.ALIGN_RIGHT, 8)
        self.panel.SetSizer(outer)
        self.second.Hide()
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(300)
        self.Centre()

    # -- helpers following the accessibility rules
    def labelled(self, parent, sizer, label, factory, proportion=0):
        """A label ending ":" and, right after it, its control; an &letter in the label moves focus to it."""
        text = wx.StaticText(parent, label=label)
        sizer.Add(text, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        control = factory()
        sizer.Add(control, proportion, wx.EXPAND | wx.ALL, 8)
        letter = re.search(r"&(\w)", label)
        if letter:
            self.mnemonics[letter.group(1).lower()] = control
        return control

    def button(self, parent, label, tip, handler):
        """A button with an &letter named in its tooltip "(Alt+X)"."""
        b = wx.Button(parent, label=label)
        letter = re.search(r"&(\w)", label).group(1).upper()
        b.SetToolTip(f"{tip} (Alt+{letter})")
        b.Bind(wx.EVT_BUTTON, handler)
        return b

    def check(self, parent, label, tip, value):
        """A check box with an &letter named in its tooltip."""
        c = wx.CheckBox(parent, label=label)
        c.SetValue(value)
        letter = re.search(r"&(\w)", label).group(1).upper()
        c.SetToolTip(f"{tip} (Alt+{letter})")
        return c

    # -- the first page
    def build_first(self, parent):
        """The settings page."""
        page = wx.Panel(parent)
        s = wx.BoxSizer(wx.VERTICAL)
        self.about = self.labelled(page, s, "About this wizard:", lambda: wx.TextCtrl(
            page, value=("This wizard teaches the Digital Accessibility Toolkit's picture model to describe pictures "
                         "the way a blind reader needs, on this computer's NVIDIA graphics card. Choose the folder and "
                         "how much to train, then press Start training. Every step is said as it happens. You can "
                         "close the wizard at any time; starting again carries on where it stopped. Press F1 for the "
                         "full instructions."), style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.folder = self.labelled(page, s, "&Training folder:", lambda: wx.TextCtrl(page, value=DEFAULT_FOLDER))
        row.Add(self.button(page, "&Browse...", "Choose the training folder", self.on_browse), 0, wx.ALL, 4)
        s.Add(row, 0, wx.LEFT, 4)
        self.model = self.labelled(page, s, "&Model:", lambda: wx.Choice(page, choices=[m[1] for m in MODELS]))
        self.model.SetSelection(0)
        self.size = self.labelled(page, s, "&How much to train:", lambda: wx.Choice(page, choices=[x[1] for x in SIZES]))
        self.size.SetSelection(2)
        self.wikipedia = self.check(page, "Include &Wikipedia (the add-on is then CC BY-SA 4.0)",
                                    "Also learn from Wikipedia's alt text", False)
        s.Add(self.wikipedia, 0, wx.ALL, 8)
        self.prepare = self.check(page, "&Prepare this computer first (asks for administrator permission)",
                                  "No sleep or hibernation, Windows Update paused, Defender skips the kit folder", True)
        s.Add(self.prepare, 0, wx.ALL, 8)
        self.check_result = self.labelled(page, s, "Computer chec&k result:", lambda: wx.TextCtrl(
            page, value="Not checked yet.", style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 90)))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for b in (self.button(page, "&Check this computer", "Say the graphics card and the free space", self.on_check),
                  self.button(page, "&Start training", "Prepare, install and train", self.on_start),
                  self.button(page, "Read the &instructions (F1)", "Open READ ME FIRST.txt", self.on_help)):
            buttons.Add(b, 0, wx.ALL, 4)
        s.Add(buttons, 0, wx.ALL, 4)
        page.SetSizer(s)
        return page

    # -- the progress page
    def build_second(self, parent):
        """The progress page."""
        page = wx.Panel(parent)
        s = wx.BoxSizer(wx.VERTICAL)
        self.status = self.labelled(page, s, "St&atus:", lambda: wx.TextCtrl(page, style=wx.TE_READONLY))
        self.gauge = self.labelled(page, s, "Progress:", lambda: wx.Gauge(page, range=100))
        self.log = self.labelled(page, s, "Ever&ything said:", lambda: wx.TextCtrl(
            page, style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.read_button = self.button(page, "&Read the status", "Say the status and the percent again", self.on_read)
        self.log_button = self.button(page, "Open the lo&g", "Open training-log.txt in Notepad", self.on_open_log)
        self.report_button = self.button(page, "Open the r&eport", "Open the report in Notepad", self.on_open_report)
        self.result_button = self.button(page, "Open the result &folder", "The zip to send", self.on_open_result)
        self.restore_button = self.button(page, "Restore the &usual settings", "Undo Prepare this computer",
                                          self.on_restore)
        self.stop_button = self.button(page, "Stop the trai&ning", "Stop; starting again carries on", self.on_stop)
        self.logs_button = self.button(page, "Open the logs fol&der", "The logs folder on the desktop",
                                       self.on_open_logs)
        for b in (self.read_button, self.log_button, self.report_button, self.result_button, self.logs_button,
                  self.restore_button, self.stop_button):
            buttons.Add(b, 0, wx.ALL, 4)
        self.report_button.Disable()
        s.Add(buttons, 0, wx.ALL, 4)
        page.SetSizer(s)
        return page

    # -- keys
    def on_key(self, event):
        """Escape closes; F1 opens the instructions; Alt+a label's letter moves focus to its control."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.on_close(None)
        elif key == wx.WXK_F1:
            self.on_help(None)
        elif event.AltDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics and \
                self.mnemonics[chr(key).lower()].IsShownOnScreen():
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()

    # -- the first page's buttons
    def on_browse(self, _event):
        """Choose the training folder."""
        with wx.DirDialog(self, "Choose the training folder", self.folder.GetValue()) as d:
            if d.ShowModal() == wx.ID_OK:
                self.folder.SetValue(d.GetPath())

    def on_check(self, _event):
        """Check the card and the disk, show and say it."""
        lines, _ready = check_computer(self.folder.GetValue())
        log("Computer check: " + " ".join(lines))
        self.check_result.SetValue("\n".join(lines))
        speak(" ".join(lines), True)

    def on_help(self, _event):
        """Open READ ME FIRST.txt."""
        path = os.path.join(self.kit, "READ ME FIRST.txt") if self.kit else resource("READ ME FIRST.txt")
        if os.path.exists(path):
            os.startfile(path)  # noqa: S606 - opens the text file in Notepad

    def on_start(self, _event):
        """Check, then show the progress page and start the work in the background."""
        lines, ready = check_computer(self.folder.GetValue())
        self.check_result.SetValue("\n".join(lines))
        log("Computer check: " + " ".join(lines))
        if not ready:
            speak(" ".join(lines), True)
            return
        self.kit = os.path.join(self.folder.GetValue(), KIT_NAME)
        self.first.Hide()
        self.second.Show()
        self.panel.Layout()
        self.status.SetFocus()
        args = ["--model", MODELS[self.model.GetSelection()][0], "--size", SIZES[self.size.GetSelection()][0]]
        if self.wikipedia.GetValue():
            args.append("--with-wikipedia")
        log(f"Start training: folder {self.kit}, settings {' '.join(args)}, prepare this computer "
            f"{'yes' if self.prepare.GetValue() else 'no'}.")
        threading.Thread(target=self.work, args=(args, self.prepare.GetValue()), daemon=True).start()

    # -- the work, in the background
    def work(self, args, prepare):
        """Copy the kit, prepare the computer, install the tools and run the training; every line goes to the
        queue the window reads."""
        say = self.lines.put
        try:
            say("Copying the kit's files into " + self.kit)
            copy_kit(self.kit)
            if prepare:
                prepare_computer(self.kit, say)
            install_tools(self.kit, say)
            python = os.path.join(self.kit, "env", "Scripts", "python.exe")
            self.process = subprocess.Popen([python, "-u", os.path.join("kit", "train.py"), *args], cwd=self.kit,
                                            env=kit_environment(self.kit), stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                                            creationflags=NO_WINDOW)
            for line in self.process.stdout:
                if line.strip():
                    say(line.rstrip())
            code = self.process.wait()
            if code not in (0, 1) and code is not None:
                say(f"STOPPED: the training ended unexpectedly (code {code}). Open the log and send its end to Claude.")
        except Exception as e:  # noqa: BLE001 - said in plain words
            say(f"STOPPED: {e}")
        finally:
            say("\x00done")

    # -- reading the work's lines
    def on_timer(self, _event):
        """Show and say the new lines (see SPOKEN), and move the progress bar."""
        while True:
            try:
                line = self.lines.get_nowait()
            except queue.Empty:
                return
            if line == "\x00done":
                self.process = None
                self.stop_button.Disable()
                continue
            self.log.AppendText(line + "\n")
            log(line)
            self.status.SetValue(line.strip())
            step = STEP_LINE.match(line)
            trained = TRAINED_LINE.search(line)
            if step:
                self.percent = STEP_SPAN[int(step.group(1))][0]
            elif trained:
                start, end = STEP_SPAN[5]
                self.percent = start + (end - start) * int(trained.group(3)) // 100
            if line.startswith("FINISHED"):
                self.percent = 100
                self.report_button.Enable()
                for name in os.listdir(self.kit) if self.kit and os.path.isdir(self.kit) else []:
                    if name.startswith("report-") or name == "training-log.txt":
                        copy_to_logs(os.path.join(self.kit, name))
            self.gauge.SetValue(self.percent)
            if SPOKEN.match(line):
                speak(line.strip(), line.startswith(("FINISHED", "STOPPED")))

    # -- the progress page's buttons
    def on_read(self, _event):
        """Say the status and the percent again."""
        speak(f"{self.status.GetValue()} Overall {self.percent} percent.", True)

    def on_open_log(self, _event):
        """Open training-log.txt."""
        path = os.path.join(self.kit or "", "training-log.txt")
        if os.path.exists(path):
            os.startfile(path)  # noqa: S606
        else:
            speak("There is no log yet.", True)

    def on_open_logs(self, _event):
        """Open the "Picture Model Training logs" folder on the desktop."""
        os.startfile(log_folder())  # noqa: S606

    def on_open_report(self, _event):
        """Open the newest report."""
        reports = sorted((os.path.join(self.kit, n) for n in os.listdir(self.kit) if n.startswith("report-")),
                         key=os.path.getmtime)
        if reports:
            os.startfile(reports[-1])  # noqa: S606

    def on_open_result(self, _event):
        """Open the result folder."""
        path = os.path.join(self.kit or "", "result")
        if os.path.isdir(path):
            os.startfile(path)  # noqa: S606
        else:
            speak("There is no result yet: it is made when the training has finished.", True)

    def on_restore(self, _event):
        """Run "Restore Normal Settings.cmd" as administrator."""
        script = os.path.join(self.kit or "", "Restore Normal Settings.cmd")
        if os.path.exists(script):
            subprocess.Popen(["powershell", "-NoProfile", "-Command",
                              f"Start-Process -FilePath $env:ComSpec -ArgumentList '/c \"\"{script}\"\"' -Verb RunAs"],
                             creationflags=NO_WINDOW)

    def on_stop(self, _event):
        """Stop the training (the whole process tree); starting again carries on from the last save."""
        if self.process and self.process.poll() is None:
            subprocess.run(["taskkill", "/PID", str(self.process.pid), "/T", "/F"], capture_output=True,
                           creationflags=NO_WINDOW)
            self.lines.put("Stopped by you. Start the wizard again to carry on where it stopped.")

    def on_close(self, _event):
        """Close; while training runs, ask first (stopping it, or keeping the wizard open)."""
        if self.process and self.process.poll() is None:
            answer = wx.MessageBox("The training is still running. Stop it and close the wizard? Starting again "
                                   "carries on from the last save.", APP_NAME, wx.YES_NO | wx.NO_DEFAULT, self)
            if answer != wx.YES:
                return
            self.on_stop(None)
        self.timer.Stop()
        self.Destroy()


def self_test():
    """For the build: the bundled kit files are there and the window can be made; prints OK or raises."""
    for name in ("READ ME FIRST.txt", "Prepare This Computer.cmd", os.path.join("kit", "train.py"),
                 os.path.join("kit", "sources.py"), os.path.join("kit", "requirements.txt")):
        if not os.path.exists(resource(name)):
            raise SystemExit(f"missing from the program: {name}")
    app = wx.App()
    window = Wizard()
    window.Destroy()
    app.Destroy()
    print("OK")


def log_crash(kind, value, trace):
    """Write an unexpected error into the desktop log (sys.excepthook and threading.excepthook)."""
    import traceback
    log("ERROR: " + "".join(traceback.format_exception(kind, value, trace)))


def main():
    """Start the wizard (--self-test: the build's check)."""
    if "--self-test" in sys.argv:
        self_test()
        return
    sys.excepthook = log_crash
    threading.excepthook = lambda args: log_crash(args.exc_type, args.exc_value, args.exc_traceback)
    log(f"{APP_NAME} started.")
    app = wx.App()
    Wizard().Show()
    speak("Picture Model Training wizard. Choose how much to train, then press Alt+S to start.")
    app.MainLoop()


if __name__ == "__main__":
    main()
