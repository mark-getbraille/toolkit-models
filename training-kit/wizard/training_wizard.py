"""Picture Model Training: the one-click wizard of the Picture Model Training Kit (Picture Model Training.exe).

It does what the kit's .cmd files do, in one window that a screen reader user can follow:
  0. what to train: a picture describer (pictures to words: kit\\train.py) or a picture-making model (words to
     pictures: kit\\train_pictures.py, Stable Diffusion XL or 1.5, chosen in "Picture-making model:", which is shown
     only then);
  1. the first page: the picture library folder (B:\\Picture Library when drive B: exists: every picture, larger
     copies and download kept for good, for future training), the training folder (C:\\Training by default), the model (4B or 8B), how much to train (a quick
     try, normal, full: several days, or a follow-up that carries on from the last finished training with only
     the new collections), Wikipedia or not, the content choices (art with nudity, medical and anatomy pictures:
     both ticked for a describer, neither for a picture-making model, and remembered for each), your own pictures
     folder ("Check my pictures" says what was found in it, kit\\own_data.py) and whether to train on them alone, and
     whether to prepare this computer first; "Check this computer" says the NVIDIA card, its memory and the free
     disk space;
  2. "Start training": the kit's files are copied into "<folder>\\Picture Model Training Kit" (a newer wizard
     updates them; the downloads, pictures, training and results there are kept), "Prepare This Computer.cmd" runs
     as administrator when asked for, the helper uv and the training tools are installed once into the kit folder
     (for a picture-making model also kit\\requirements-pictures.txt), and kit\\train.py (or kit\\train_pictures.py)
     runs without a console window;
  3. the progress page: every line the training says goes into "Everything said:", the latest into "Status:", and
     the important ones (each step, each collection, the training progress every 200 pictures, FINISHED or STOPPED)
     are spoken by the running screen reader (Tolk, through cytolk, as in the Digital Accessibility Toolkit).
     "Read the status" says the status and the percent again; the log, the report and the result folder open from
     their buttons; "Stop the training" stops it (starting again carries on from the last save).

Accessibility: standard wx controls only; a label ending ":" right before each field; every button and check box
has an Alt letter, named in its tooltip, and no letter is used twice in the window (both pages together; with this
many controls some labels have no letter); Escape closes (asking first while training runs); F1 opens READ ME
FIRST.txt; Enter presses only the focused button (no default button). Letters: first page B, L, W, Y (nudity),
A (anatomy), O (own pictures folder), K (check my pictures), J (describe pictures), M (only my own), P, C, S, I
and the labels T and H;
second page R, G, E, F, U, N, D and the label V; X (Exit) on both.

Describe pictures (Alt+J) opens describe_window.py: describing pictures together with friends, offline, in a
workspace folder that "Your own pictures folder" can then point at (the data side is kit\\describe_package.py).

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


def fixed_drives():
    """The computer's own drives that are there now ("C:\\", "D:\\" ...); on other systems, the root."""
    if os.name != "nt":
        return ["/"]
    import ctypes
    drives = []
    mask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if mask & (1 << i):
            root = f"{chr(65 + i)}:\\"
            if ctypes.windll.kernel32.GetDriveTypeW(root) == 3:       # DRIVE_FIXED: not a USB stick or DVD
                drives.append(root)
    return drives


def default_library():
    """The picture library's suggested place: "Picture Library" on the fixed drive with the most free space (no
    drive letter is assumed: it is worked out on each computer)."""
    best, free = None, -1
    for root in fixed_drives():
        try:
            room = shutil.disk_usage(root).free
        except OSError:
            continue
        if room > free:
            best, free = root, room
    return os.path.join(best or os.path.expanduser("~"), "Picture Library")


SETTINGS_FILE = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_NAME, "settings.json")


def load_choices():
    """The choices made last time on this computer ({} the first time)."""
    import json
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_choices(choices):
    """Remember the choices for next time (in the user's own application data). Never raises."""
    import json
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(choices, f, indent=1)
    except OSError:
        pass
# What to train: the picture describer (kit\\train.py) or a picture-making model (kit\\train_pictures.py, written
# separately; its command line: --base sd15|sdxl --library FOLDER --size quick|normal|full [--with-wikipedia]
# [--with-nudity] [--with-medical] [--own FOLDER] [--own-only] [--limit N]).
KINDS = [("describer", "A picture describer (pictures to words)"),
         ("pictures", "A picture-making model (words to pictures)")]
PICTURE_MODELS = [("sdxl", "Stable Diffusion XL (best, about 1 to 2 days)"),
                  ("sd15", "Stable Diffusion 1.5 (faster, smaller)")]
# The content choices' starting values for each kind, until the person changes them (then remembered).
CONTENT_DEFAULTS = {"describer": True, "pictures": False}
TRAIN_SCRIPTS = {"describer": "train.py", "pictures": "train_pictures.py"}

MODELS = [("4b", "Qwen3-VL 4B (needs an NVIDIA card with 12 GB or more)"),
          ("8b", "Qwen3-VL 8B (needs 16 GB or more; train the 4B model first)")]
SIZES = [("quick", "Quick try: a tenth of the pictures, an hour or two"),
         ("normal", "Normal: about 44,000 pictures, roughly a day"),
         ("full", "Full: about 110,000 pictures, roughly three days (the best result)"),
         ("continue", "Follow-up: carry on from the last finished training with only the new collections (a few hours)")]
NO_WINDOW = 0x08000000 if os.name == "nt" else 0          # CREATE_NO_WINDOW

# Where the training is, as a share of the whole run (the progress bar): each step's start and end percent (the
# describer's 7 steps; a training with another number of steps gets equal parts, see step_span).
STEP_SPAN = {1: (0, 1), 2: (1, 6), 3: (6, 16), 4: (16, 20), 5: (20, 92), 6: (92, 99), 7: (99, 100)}
STEP_LINE = re.compile(r"^Step (\d+) of (\d+):")
TRAINED_LINE = re.compile(r"(\d+) of (\d+) pictures trained \((\d+) percent\)")
SPOKEN = re.compile(r"^(Step \d+ of \d+:|\s*Collection \d+ of \d+:|\s*Ready:|\s+\d+ of \d+ pictures trained|"
                    r"\s*Score (before|after)|FINISHED|STOPPED|Getting ready|\s*This collection could not)")


def step_span(step, total):
    """(start, end) percent of a step: STEP_SPAN for the describer's 7 steps, otherwise equal parts."""
    if total == 7 and step in STEP_SPAN:
        return STEP_SPAN[step]
    total = max(total, 1)
    step = min(max(step, 1), total)
    return (100 * (step - 1) // total, 100 * step // total)


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


def check_computer(folder, library=None):
    """Plain sentences about the NVIDIA card, the free space where the kit goes and where the picture library is,
    and whether training can start ([sentences], ready)."""
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
    needs = [(folder, 40 if library else 90, "the training folder")]
    if library:
        needs.append((library, 100, "the picture library"))
    for path, gb, what in needs:
        drive = os.path.splitdrive(os.path.abspath(path))[0] + "\\"
        try:
            free = shutil.disk_usage(drive).free / 1024 ** 3
            lines.append(f"Free disk space for {what} on {drive}: {free:,.0f} GB.")
            if free < gb:
                lines.append(f"{what.capitalize()} needs about {gb} GB: choose a folder on a bigger drive.")
                ready = False
        except OSError:
            lines.append(f"The drive {drive} for {what} could not be found.")
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


def install_tools(kit, report, pictures=False):
    """Download the helper uv and install the kit's own Python and training tools once (again when the kit's
    requirements change); with pictures, also the picture-making tools in kit\\requirements-pictures.txt (when that
    file is there; remembered in env\\installed-pictures.txt). report(text) says what happens."""
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
    env = kit_environment(kit)
    if not (os.path.exists(mark) and open(mark, encoding="utf-8").read().strip() == wanted):
        report("Getting ready: installing the training tools in the kit folder, about 5 GB. This takes 10 to 30 "
               "minutes, and nothing is said while it works.")
        if not os.path.exists(os.path.join(kit, "env", "Scripts", "python.exe")):
            run_quiet([uv, "venv", "env", "--python", "3.12", "--quiet"], kit, env)
        pip_install(uv, kit, env, requirements)
        with open(mark, "w", encoding="utf-8") as f:
            f.write(wanted)
        report("Getting ready: the training tools are installed.")
    extra = os.path.join(kit, "kit", "requirements-pictures.txt")
    if pictures and os.path.exists(extra):
        with open(extra, "rb") as f:
            wanted = hashlib.sha256(f.read()).hexdigest()
        mark = os.path.join(kit, "env", "installed-pictures.txt")
        if not installed(mark, wanted):
            report("Getting ready: installing the picture-making tools in the kit folder. This can take 10 to 30 "
                   "minutes, and nothing is said while it works.")
            pip_install(uv, kit, env, extra)
            with open(mark, "w", encoding="utf-8") as f:
                f.write(wanted)
            report("Getting ready: the picture-making tools are installed.")


def installed(mark, wanted):
    """True when the mark file says the requirements with the checksum wanted are installed."""
    try:
        with open(mark, encoding="utf-8") as f:
            return f.read().strip() == wanted
    except OSError:
        return False


def pip_install(uv, kit, env, requirements):
    """Install a requirements file into the kit's own Python (with PyTorch's CUDA packages)."""
    run_quiet([uv, "pip", "install", "--python", os.path.join("env", "Scripts", "python.exe"), "-r", requirements,
               "--extra-index-url", TORCH_INDEX, "--index-strategy", "unsafe-best-match", "--quiet"], kit, env)


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


# ----------------------------------------------------------------- your own pictures

def own_data_module():
    """The kit's own_data.py (bundled into the program, or beside the wizard in the kit), which checks a folder of
    your own pictures; None when it cannot be loaded."""
    folder = resource("kit")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    try:
        import own_data
        return own_data
    except Exception:  # noqa: BLE001 - said by the caller
        return None


# ----------------------------------------------------------------- the window

class Wizard(wx.Frame):
    """The wizard's one window, with its two pages (see the module docstring)."""

    def __init__(self):
        """Build both pages; the first is shown."""
        super().__init__(None, title=APP_NAME, size=(800, 860))
        self.process = None
        self.lines = queue.Queue()
        self.percent = 0
        self.step = (5, 7)             # the step said last (number, of how many), for the progress bar
        self.kit = None
        self.mnemonics = {}
        self.last_label = None         # the label labelled() made last (to hide it with its field)
        self.panel = wx.Panel(self)
        outer = wx.BoxSizer(wx.VERTICAL)
        self.first = self.build_first(self.panel)
        self.second = self.build_second(self.panel)
        outer.Add(self.first, 1, wx.EXPAND)
        outer.Add(self.second, 1, wx.EXPAND)
        self.close_button = self.button(self.panel, "E&xit", "Close the wizard", self.on_close)
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
        self.last_label = text
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
        """The settings page (the Alt letters are listed in the module docstring)."""
        page = wx.Panel(parent)
        s = wx.BoxSizer(wx.VERTICAL)
        self.about = self.labelled(page, s, "About this wizard:", lambda: wx.TextCtrl(
            page, value=("This wizard teaches a picture model on this computer's NVIDIA graphics card: either the "
                         "Digital Accessibility Toolkit's picture describer, to describe pictures the way a blind "
                         "reader needs, or a picture-making model that draws pictures from words. Choose what to "
                         "train, the folders and how much to train, then press Start training. Every step is said as "
                         "it happens. You can close the wizard at any time; starting again carries on where it "
                         "stopped. Press F1 for the full instructions."), style=wx.TE_MULTILINE | wx.TE_READONLY), 1)
        chosen = load_choices()
        self.kind = self.labelled(page, s, "What to train:", lambda: wx.Choice(page, choices=[k[1] for k in KINDS]))
        self.kind.SetSelection(next((i for i, k in enumerate(KINDS) if k[0] == chosen.get("what")), 0))
        self.kind.Bind(wx.EVT_CHOICE, self.on_kind)
        self.picture_model = self.labelled(page, s, "Picture-making model:", lambda: wx.Choice(
            page, choices=[m[1] for m in PICTURE_MODELS]))
        self.picture_model_label = self.last_label
        self.picture_model.SetSelection(next((i for i, m in enumerate(PICTURE_MODELS)
                                              if m[0] == chosen.get("picture_model")), 0))
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.folder = self.labelled(page, s, "&Training folder:", lambda: wx.TextCtrl(
            page, value=chosen.get("folder") or DEFAULT_FOLDER))
        row.Add(self.button(page, "&Browse for the training folder...", "Choose the training folder", self.on_browse),
                0, wx.ALL, 4)
        s.Add(row, 0, wx.LEFT, 4)
        self.library = self.labelled(page, s, "Picture library folder:", lambda: wx.TextCtrl(
            page, value=chosen.get("library") or default_library()))
        self.library.SetToolTip("All pictures, full-size copies and downloads are kept here for good, for future "
                                "training. It starts on the drive with the most free space.")
        s.Add(self.button(page, "Browse for the &library folder...", "Choose where the picture library is",
                          self.on_browse_library), 0, wx.LEFT, 12)
        self.model = self.labelled(page, s, "Model:", lambda: wx.Choice(page, choices=[m[1] for m in MODELS]))
        self.model_label = self.last_label
        self.model.SetSelection(next((i for i, m in enumerate(MODELS) if m[0] == chosen.get("model")), 0))
        self.size = self.labelled(page, s, "&How much to train:", lambda: wx.Choice(page, choices=[x[1] for x in SIZES]))
        self.size.SetSelection(next((i for i, x in enumerate(SIZES) if x[0] == chosen.get("size")), 2))
        self.wikipedia = self.check(page, "Include &Wikipedia (the add-on is then CC BY-SA 4.0)",
                                    "Also learn from Wikipedia's alt text", False)
        s.Add(self.wikipedia, 0, wx.ALL, 8)
        # The content choices, remembered for each kind of training (see CONTENT_DEFAULTS).
        self.content = {kind: {"nudity": chosen.get(f"nudity_{kind}", CONTENT_DEFAULTS[kind]),
                               "medical": chosen.get(f"medical_{kind}", CONTENT_DEFAULTS[kind])} for kind, _ in KINDS}
        self.nudity = self.check(page, "Include art with nudit&y (non-sexual)",
                                 "Paintings, drawings, sculptures and photographs from museums that show nude people, "
                                 "described plainly; nothing sexual and no children", False)
        s.Add(self.nudity, 0, wx.ALL, 8)
        self.medical = self.check(page, "Include medical and &anatomy pictures",
                                  "Anatomy textbook figures and old anatomy plates showing the inside and outside of "
                                  "the human body, with their captions", False)
        s.Add(self.medical, 0, wx.ALL, 8)
        self.own = self.labelled(page, s, "Your own pictures folder:", lambda: wx.TextCtrl(
            page, value=chosen.get("own_folder") or ""))
        self.own.SetToolTip("Optional: a folder of your own pictures with their descriptions, for personal use. "
                            "See HOW TO ADD YOUR OWN PICTURES.txt. Leave it empty to use only the collections.")
        own_row = wx.BoxSizer(wx.HORIZONTAL)
        for b in (self.button(page, "Browse for your &own pictures folder...", "Choose the folder of your own pictures",
                              self.on_browse_own),
                  self.button(page, "Chec&k my pictures", "Say what was found in your own pictures folder",
                              self.on_check_own),
                  self.button(page, "Describe pictures (&J)...", "Describe pictures with friends, and pass the work "
                              "between you as packages", self.on_describe)):
            own_row.Add(b, 0, wx.ALL, 4)
        s.Add(own_row, 0, wx.LEFT, 4)
        self.own_only = self.check(page, "Only &my own pictures",
                                   "Train on the pictures in your own pictures folder alone, without the collections",
                                   bool(chosen.get("own_only", False)))
        s.Add(self.own_only, 0, wx.ALL, 8)
        self.prepare = self.check(page, "&Prepare this computer first (asks for administrator permission)",
                                  "No sleep or hibernation, Windows Update paused, Defender skips the kit folder", True)
        s.Add(self.prepare, 0, wx.ALL, 8)
        self.check_result = self.labelled(page, s, "Check result:", lambda: wx.TextCtrl(
            page, value="Not checked yet.", style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 90)))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for b in (self.button(page, "&Check this computer", "Say the graphics card and the free space", self.on_check),
                  self.button(page, "&Start training", "Prepare, install and train", self.on_start),
                  self.button(page, "Read the &instructions (F1)", "Open READ ME FIRST.txt", self.on_help)):
            buttons.Add(b, 0, wx.ALL, 4)
        s.Add(buttons, 0, wx.ALL, 4)
        page.SetSizer(s)
        self.shown_kind = self.kind_key()
        self.show_kind(self.shown_kind)
        return page

    # -- what to train
    def kind_key(self):
        """"describer" or "pictures": what is chosen in "What to train"."""
        return KINDS[self.kind.GetSelection()][0]

    def show_kind(self, kind):
        """Show the model choice that fits kind (the describer's or the picture-making one) and put that kind's
        content choices in the check boxes."""
        pictures = kind == "pictures"
        for control in (self.picture_model_label, self.picture_model):
            control.Show(pictures)
        for control in (self.model_label, self.model):
            control.Show(not pictures)
        self.nudity.SetValue(self.content[kind]["nudity"])
        self.medical.SetValue(self.content[kind]["medical"])
        if getattr(self, "first", None):          # not yet while the page is being built
            self.first.Layout()

    def on_kind(self, _event):
        """Another kind chosen: keep the content choices of the one before, show the fitting fields, and say it."""
        self.content[self.shown_kind] = {"nudity": self.nudity.GetValue(), "medical": self.medical.GetValue()}
        self.shown_kind = self.kind_key()
        self.show_kind(self.shown_kind)
        ticked = [w for w, c in (("art with nudity", self.nudity), ("medical and anatomy pictures", self.medical))
                  if c.GetValue()]
        speak(("Picture-making model chosen: choose Stable Diffusion in Picture-making model. "
               if self.shown_kind == "pictures" else "Picture describer chosen. ")
              + ("Ticked: " + " and ".join(ticked) + "." if ticked else
                 "Art with nudity and medical pictures are not ticked."), True)

    # -- the progress page
    def build_second(self, parent):
        """The progress page."""
        page = wx.Panel(parent)
        s = wx.BoxSizer(wx.VERTICAL)
        self.status = self.labelled(page, s, "Status:", lambda: wx.TextCtrl(page, style=wx.TE_READONLY))
        self.gauge = self.labelled(page, s, "Progress:", lambda: wx.Gauge(page, range=100))
        self.log = self.labelled(page, s, "E&verything said:", lambda: wx.TextCtrl(
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

    def on_browse_library(self, _event):
        """Choose the picture library folder."""
        with wx.DirDialog(self, "Choose the picture library folder", self.library.GetValue()) as d:
            if d.ShowModal() == wx.ID_OK:
                self.library.SetValue(d.GetPath())

    def on_browse_own(self, _event):
        """Choose the folder of your own pictures."""
        with wx.DirDialog(self, "Choose the folder of your own pictures", self.own.GetValue()) as d:
            if d.ShowModal() == wx.ID_OK:
                self.own.SetValue(d.GetPath())

    def on_check_own(self, _event):
        """Check the own pictures folder in the background (a big folder takes a while) and show and say what was
        found: how many pictures, how they are described, the test pictures and any problems."""
        folder = self.own.GetValue().strip()
        if not folder:
            self.show_result("Choose your own pictures folder first (Browse for your own pictures folder, Alt+O).")
            return
        module = own_data_module()
        if module is None:
            self.show_result("Your pictures cannot be checked: the kit's own_data.py is missing from the program.")
            return
        self.show_result("Checking your pictures. This can take a minute for a big folder.")

        def check():
            """Check the folder; the result is shown on the window's own thread."""
            try:
                _rows, _problems, summary = module.check_folder(folder)
            except Exception as e:  # noqa: BLE001 - said in plain words
                summary = f"Your pictures could not be checked: {e}"
            wx.CallAfter(self.show_result, summary)
        threading.Thread(target=check, daemon=True).start()

    def on_describe(self, _event):
        """Open the Describe pictures window; when it says "Use this workspace for training", the workspace goes
        into Your own pictures folder."""
        try:
            import describe_window
        except Exception as e:  # noqa: BLE001 - said in plain words
            self.show_result(f"The Describe pictures window cannot be opened: {e}")
            return
        kit = os.path.join(self.folder.GetValue().strip(), KIT_NAME) if self.folder.GetValue().strip() else None
        with describe_window.DescribeWindow(self, sys.modules[__name__], kit) as window:
            window.ShowModal()
            folder = window.training_folder
        if folder:
            self.own.SetValue(folder)
            self.show_result(f"Your own pictures folder is now the describing workspace {folder}. Only its described "
                             "and checked pictures are used. Press Check my pictures (Alt+K) to see them.")

    def show_result(self, text):
        """Put text in the Check result field, write it in the log and say it."""
        if not self:                               # the window was closed meanwhile
            return
        self.check_result.SetValue(text)
        log(text)
        speak(text.replace("\n", " "), True)

    def on_check(self, _event):
        """Check the card and the disk, show and say it."""
        lines, _ready = check_computer(self.folder.GetValue(), self.library.GetValue())
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
        lines, ready = check_computer(self.folder.GetValue(), self.library.GetValue())
        self.check_result.SetValue("\n".join(lines))
        log("Computer check: " + " ".join(lines))
        if not ready:
            speak(" ".join(lines), True)
            return
        kind = self.kind_key()
        size = SIZES[self.size.GetSelection()][0]
        own = self.own.GetValue().strip()
        problem = None
        if kind == "pictures" and size == "continue":
            problem = ("A follow-up is only for the picture describer. Choose a quick try, normal or full in How much "
                       "to train.")
        elif self.own_only.GetValue() and not own:
            problem = ("Only my own pictures is ticked, but no folder is chosen. Choose your own pictures folder, or "
                       "untick Only my own pictures.")
        elif own and not os.path.isdir(own):
            problem = f"Your own pictures folder was not found: {own}"
        elif kind == "pictures" and not os.path.exists(resource("kit", TRAIN_SCRIPTS[kind])):
            problem = ("This version of the program cannot train a picture-making model yet (kit\\train_pictures.py "
                       "is missing). Get the newest program, or choose A picture describer.")
        if problem:
            self.show_result(problem)
            return
        self.kit = os.path.join(self.folder.GetValue(), KIT_NAME)
        self.content[kind] = {"nudity": self.nudity.GetValue(), "medical": self.medical.GetValue()}
        choices = {"folder": self.folder.GetValue(), "library": self.library.GetValue(),
                   "model": MODELS[self.model.GetSelection()][0], "size": size,
                   "wikipedia": self.wikipedia.GetValue(), "prepare": self.prepare.GetValue(), "what": kind,
                   "picture_model": PICTURE_MODELS[self.picture_model.GetSelection()][0], "own_folder": own,
                   "own_only": self.own_only.GetValue()}
        for name, values in self.content.items():
            choices[f"nudity_{name}"], choices[f"medical_{name}"] = values["nudity"], values["medical"]
        save_choices({**load_choices(), **choices})    # keeps the Describe pictures window's own choices
        self.first.Hide()
        self.second.Show()
        self.panel.Layout()
        self.status.SetFocus()
        if kind == "pictures":
            args = ["--base", PICTURE_MODELS[self.picture_model.GetSelection()][0], "--size", size]
        else:
            args = ["--model", MODELS[self.model.GetSelection()][0], "--size", "normal" if size == "continue" else size]
            if size == "continue":
                args.append("--continue")
        if self.library.GetValue().strip():
            args += ["--library", self.library.GetValue().strip()]
        if self.wikipedia.GetValue():
            args.append("--with-wikipedia")
        if self.nudity.GetValue():
            args.append("--with-nudity")
        if self.medical.GetValue():
            args.append("--with-medical")
        if own:
            args += ["--own", own]
            if self.own_only.GetValue():
                args.append("--own-only")
        log(f"Start training ({kind}, {TRAIN_SCRIPTS[kind]}): folder {self.kit}, settings {' '.join(args)}, prepare "
            f"this computer {'yes' if self.prepare.GetValue() else 'no'}.")
        threading.Thread(target=self.work, args=(args, self.prepare.GetValue(), kind), daemon=True).start()

    # -- the work, in the background
    def work(self, args, prepare, kind="describer"):
        """Copy the kit, prepare the computer, install the tools and run the training (kit\\train.py, or
        kit\\train_pictures.py for a picture-making model); every line goes to the queue the window reads, and from
        there into the log on the desktop."""
        say = self.lines.put
        try:
            say("Copying the kit's files into " + self.kit)
            copy_kit(self.kit)
            if prepare:
                prepare_computer(self.kit, say)
            install_tools(self.kit, say, pictures=kind == "pictures")
            python = os.path.join(self.kit, "env", "Scripts", "python.exe")
            self.process = subprocess.Popen([python, "-u", os.path.join("kit", TRAIN_SCRIPTS[kind]), *args],
                                            cwd=self.kit,
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
                self.step = (int(step.group(1)), int(step.group(2)))
                self.percent = step_span(*self.step)[0]
            elif trained:
                # the training step's share: step 5 of the describer's 7, else the step said last
                start, end = step_span(*self.step) if self.step[1] != 7 else STEP_SPAN[5]
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
    for name in ("READ ME FIRST.txt", "Prepare This Computer.cmd", "HOW TO ADD YOUR OWN PICTURES.txt",
                 "HOW TO DESCRIBE PICTURES WITH FRIENDS.txt", os.path.join("kit", "train.py"),
                 os.path.join("kit", "sources.py"), os.path.join("kit", "own_data.py"),
                 os.path.join("kit", "describe_package.py"), os.path.join("kit", "run_video.cmd"),
                 os.path.join("kit", "requirements.txt")):
        if not os.path.exists(resource(name)):
            raise SystemExit(f"missing from the program: {name}")
    module = own_data_module()
    if module is None:
        raise SystemExit("own_data.py cannot be loaded")
    import tempfile
    with tempfile.TemporaryDirectory() as empty:
        rows, problems, _summary = module.check_folder(empty)
        if rows or not problems:
            raise SystemExit("own_data.check_folder did not report an empty folder")
    import describe_window
    package = describe_window.load_package_module(sys.modules[__name__])
    if package is None:
        raise SystemExit("describe_package.py cannot be loaded")
    with tempfile.TemporaryDirectory() as folder:
        package.self_test(folder)                   # make, describe, export and import a tiny workspace
        rows, _problems, _summary = module.check_folder(os.path.join(folder, "second"))
        if len(rows) != 1:
            raise SystemExit("own_data.check_folder did not read the self-test workspace")
    app = wx.App()
    window = Wizard()
    window.kind.SetSelection(1)                    # both kinds of training can be shown
    window.on_kind(None)
    window.kind.SetSelection(0)
    window.on_kind(None)
    describe_window.DescribeWindow(window, sys.modules[__name__], None).Destroy()
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
