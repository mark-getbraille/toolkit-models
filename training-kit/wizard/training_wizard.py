"""Picture Model Training: the one-click wizard of the Picture Model Training Kit (Picture Model Training.exe).

It does what the kit's .cmd files do, in one window that a screen reader user can follow:
  0. what to train: a picture describer (pictures to words: kit\\train.py) or a picture-making model (words to
     pictures: kit\\train_pictures.py, Stable Diffusion XL or 1.5, chosen in "Picture-making model:", which is shown
     only then);
  1. the first page: the picture library folder (B:\\Picture Library when drive B: exists: every picture, larger
     copies and download kept for good, for future training), the training folder (C:\\Training by default), the model (4B or 8B), how much to train (a quick
     try, normal, full: several days, or a follow-up that carries on from the last finished training with only
     the new collections), Wikipedia or not, the content choices (art with nudity, medical and anatomy pictures:
     both ticked for a describer, neither for a picture-making model, and remembered for each), the personal-use
     collections (non-commercial licences, research-only terms: both off at first, remembered for each kind; ticking
     the research box opens ResearchTermsDialog, which lists their terms and must be agreed to), your own pictures
     folder ("Check my pictures" says what was found in it, kit\\own_data.py) and whether to train on them alone, and
     whether to prepare this computer first; "Check this computer" says the NVIDIA card, its memory and the free
     disk space;
  2. "Start training": the kit's files are copied into "<folder>\\Picture Model Training Kit" (a newer wizard
     updates them; the downloads, pictures, training and results there are kept), "Prepare This Computer.cmd" runs
     as administrator when asked for, the helper uv and the training tools are installed once into the kit folder
     (for a picture-making model also kit\\requirements-pictures.txt), and kit\\train.py (or kit\\train_pictures.py)
     runs without a console window;
  3. the progress page: every line the training says goes into "Everything said:", the latest into "Status:", and
     the important ones (each step, each collection, the training progress every 200 pictures, FINISHED or STOPPED,
     and how to install the result zip in the Digital Accessibility Toolkit: train.py puts the toolkit version of
     the add-on into it, kit\\make_toolkit_addon.py) are spoken by the running screen reader (Tolk, through cytolk,
     as in the Digital Accessibility Toolkit). "Read the status" says the status and the percent again; the log, the
     report and the result folder open from their buttons; "Stop the training" stops it (starting again carries on
     from the last save).

Accessibility: standard wx controls only; a label ending ":" right before each field; every button and check box
has an Alt letter, named in its tooltip, and no letter is used twice in the window (both pages together; with this
many controls some labels have no letter); Escape closes (asking first while training runs); F1 opens READ ME
FIRST.txt; Enter presses only the focused button (no default button). Letters: first page B, L, W, Y (nudity),
A (anatomy), Q (non-commercial collections, shown in brackets), Z (research-only collections, in brackets), O (own
pictures folder), K (check my pictures), J (describe pictures), M (only my own), P, C, S, I and the labels T and H;
second page R, G, E, F, U, N, D and the label V; X (Exit) on both. Every letter is then taken, so the
"Personal use: everything allowed" box uses the digit: Alt+1 (shown in brackets).

Personal-use collections: when either box is ticked the training is for personal use only (train.py and
train_pictures.py get --personal-noncommercial and --personal-research --accept-research-terms), which the Check
result and the Status field say. The research-terms window has its own letters: T (the terms list), I (I have read
these terms), A (Agree), C (Cancel); Escape is Cancel and F1 opens READ ME FIRST.txt.

Personal use: everything allowed (Alt+1): one box that, after EverythingDialog explains in plain words what it means
(personal, private use; never published; the licences of the non-commercial and research collections forbid selling
the model or what it makes), shows how many collections it adds and their total download size, lists the
research-only terms and asks "I understand ...", ticks Wikipedia (share-alike), the non-commercial and the
research-only boxes at once. The sign-up collections (kit\\signup_sources.py) are in those groups and are used when
their key or files are on the computer. It never ticks the content choices (nudity, medical, graphic, adult sexual
content), and a picture-making model still leaves out everything in NOT_FOR_PICTURE_MAKING. Unticking it puts the
three boxes back as they were; unticking one of them by hand turns the switch off. It is remembered for each kind
("everything_<kind>" and "before_everything_<kind>" in settings.json). Its window's letters: A (the explanation),
I (I understand), O (OK), K (Sign-up keys), C (Cancel). Sign-up keys (SignupKeysDialog: A, S Save, C Cancel) keeps the
owner's own keys in signup-keys.json in the same settings folder, never in the kit folder and never in the log.

Adult sexual content (review collections only): every Alt letter of this window is taken, so there is no box for
it here. Ticking "Include art with nudity" for a picture describer opens SexualDialog, which asks "Also include adult
sexual content from collections you have reviewed?" (its letters: A the explanation, S the check box, O OK,
C Cancel; Escape is Cancel, which leaves it off). The answer is remembered for the describer ("sexual_describer" in
settings.json); unticking art with nudity turns it off too, and it is always off for a picture-making model. With it,
train.py gets --with-sexual (only ever together with --with-nudity).
Graphic scenes (war, disasters, injuries and death, described plainly): there is no free Alt letter for a box either,
so ticking "Include medical and anatomy pictures" for a picture describer opens GraphicDialog, which asks "Also
include graphic scenes: war, disasters, injuries and death, described plainly?" (its letters: A the explanation,
G the check box, O OK, C Cancel; Escape is Cancel, which leaves them out). The box starts ticked for the describer,
as the owner wants, and the answer is remembered for each kind of training ("graphic_describer" and
"graphic_pictures" in settings.json); it is used only while medical and anatomy pictures are ticked, and never for a
picture-making model. With it, train.py gets --with-graphic.
Review collections: they are downloaded and screened in Describe pictures (its "Review collections" button). For a
picture describer every review workspace in <library>\\Review is passed to train.py as --review FOLDER; only its
pictures marked "checked" are used, subject to the content choices, and the training is then for personal use only.
A picture-making model never gets them.

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
                    r"\s*Score (before|after)|FINISHED|STOPPED|Getting ready|\s*This collection could not|"
                    # the toolkit version of the add-on (kit\\make_toolkit_addon.py): how to install it, or why not
                    r"To use it in the Digital Accessibility Toolkit|\s*The toolkit version of the add-on could not|"
                    r"Making the toolkit version of your earlier)")


def is_computer_line(line):
    """True for the kit's computer-use lines (kit\\system_monitor.py: "Computer:", "Computer use ..."), which go
    into the logs and Everything said, but not into Status or speech (a "Computer use warning" is still said)."""
    return line.lstrip().startswith(("Computer:", "Computer use"))


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
        if name in ("wizard", "prepare", "tests", "__pycache__") or name.startswith("."):
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
    try:                                     # the computer-use spreadsheet goes beside the desktop logs
        env["KIT_LOG_FOLDER"] = log_folder()
    except OSError:
        pass
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


# ----------------------------------------------------------------- personal-use collections

PERSONAL_NOTE = "This training will be for personal use only."
NONCOMMERCIAL_HINT = ("Personal use only: collections whose licences do not allow commercial use. You may not sell or "
                      "publish what you make with them, put it in a product or share it outside personal use.")


def sources_module():
    """The kit's sources.py (bundled into the program, or beside the wizard in the kit), which lists the collections
    and, through personal_sources.py when it is there, the personal-use ones; None when it cannot be loaded."""
    folder = resource("kit")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    try:
        import sources
        return sources
    except Exception:  # noqa: BLE001 - said by the caller
        return None


def research_collections():
    """[(name, terms link, one-line summary of its terms)] of the research-only collections in the kit (empty when
    there are none or the list cannot be read)."""
    module = sources_module()
    if module is None:
        return []
    out = []
    for source in module.SOURCES:
        if getattr(source, "group", "") == "research":
            link = module.terms_link(source) if hasattr(module, "terms_link") else ""
            summary = module.terms_summary(source) if hasattr(module, "terms_summary") else source.licence
            out.append((source.name, link, summary))
    return out


def research_terms_text(collections):
    """The research-only collections and their terms as plain text for the terms window's list (one paragraph each,
    so a screen reader reads them line by line)."""
    if not collections:
        return ("This version of the kit has no research-only collections yet, so ticking the box changes nothing "
                "for now. If some are added later, they are for personal, non-commercial use only.")
    parts = [(f"{len(collections)} research-only collection{'s' if len(collections) != 1 else ''}. Each may only be "
              "used for research or personal, non-commercial purposes.")]
    for number, (name, link, summary) in enumerate(collections, 1):
        parts.append(f"{number}. {name}\nTerms: {link or 'see its licence'}\nIn short: {summary}")
    return "\n\n".join(parts)


class ResearchTermsDialog(wx.Dialog):
    """Asked when "Include research-only collections" is ticked: lists each research-only collection with its terms
    page and a one-line summary (in one read-only, scrollable text field), and asks the person to tick "I have read
    these terms ..." and press Agree. Agree without the tick says what is missing and keeps the window open; Cancel
    or Escape closes it (the box is then unticked). Standard controls, a label before the field, Alt letters named in
    the tooltips, no default button, F1 opens READ ME FIRST.txt."""

    def __init__(self, parent, collections):
        """The terms list, the agreement check box and the two buttons."""
        super().__init__(parent, title="Research-only collections: their terms", size=(680, 520),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.mnemonics = {}
        panel = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(panel, label="Research-only collections and their &terms:")
        s.Add(label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self.terms = wx.TextCtrl(panel, value=research_terms_text(collections),
                                 style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.Add(self.terms, 1, wx.EXPAND | wx.ALL, 8)
        self.mnemonics["t"] = self.terms
        self.agree_box = wx.CheckBox(panel, label="&I have read these terms and will use the result only for "
                                                  "personal, non-commercial purposes")
        self.agree_box.SetToolTip("Needed before Agree (Alt+I)")
        s.Add(self.agree_box, 0, wx.ALL, 8)
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.agree_button = wx.Button(panel, label="&Agree")
        self.agree_button.SetToolTip("Keep the research-only collections in the training (Alt+A)")
        self.agree_button.Bind(wx.EVT_BUTTON, self.on_agree)
        self.cancel_button = wx.Button(panel, label="&Cancel")
        self.cancel_button.SetToolTip("Leave the research-only collections out (Alt+C)")
        self.cancel_button.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        for b in (self.agree_button, self.cancel_button):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        panel.SetSizer(s)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.terms.SetFocus()

    def on_agree(self, _event):
        """Agree: only with the check box ticked; otherwise say what is missing and stay open."""
        if not self.agree_box.GetValue():
            speak("First tick I have read these terms and will use the result only for personal, non-commercial "
                  "purposes, with Alt+I, then press Agree.", True)
            self.agree_box.SetFocus()
            return
        self.EndModal(wx.ID_OK)

    def on_key(self, event):
        """Escape is Cancel; F1 opens READ ME FIRST.txt; Alt and the label's letter moves to the terms list."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif key == wx.WXK_F1:
            open_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()


SEXUAL_QUESTION = "Also include adult sexual content from collections you have reviewed?"
SEXUAL_ABOUT = ("Adult sexual content comes only from the adult review collections you downloaded in Describe "
                "pictures (Review collections), and only from pictures a trusted sighted adult has looked at and "
                "marked checked. It is used only together with art with nudity, never for a picture-making model, and "
                "a model trained with it is for personal use only: never publish it, share it or put it in a product. "
                "Leave the box unticked to leave it out.")


class SexualDialog(wx.Dialog):
    """Asked when "Include art with nudity" is ticked for a picture describer: "Also include adult sexual content
    from collections you have reviewed?", with an explanation (a read-only field), a check box and OK and Cancel.
    OK keeps what the box says; Cancel or Escape leaves it off. Standard controls, a label before the field, Alt
    letters named in the tooltips, no default button, F1 opens READ ME FIRST.txt."""

    def __init__(self, parent, value=False):
        """The explanation, the check box (ticked when value) and the two buttons."""
        super().__init__(parent, title="Adult sexual content", size=(620, 400),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.mnemonics = {}
        panel = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(wx.StaticText(panel, label="&About this choice:"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self.about = wx.TextCtrl(panel, value=f"{SEXUAL_QUESTION} {SEXUAL_ABOUT}",
                                 style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.Add(self.about, 1, wx.EXPAND | wx.ALL, 8)
        self.mnemonics["a"] = self.about
        self.box = wx.CheckBox(panel, label="Also include adult &sexual content from collections you have reviewed")
        self.box.SetValue(bool(value))
        self.box.SetToolTip("Only checked pictures of the adult review collections; personal use only (Alt+S)")
        s.Add(self.box, 0, wx.ALL, 8)
        row = wx.BoxSizer(wx.HORIZONTAL)
        ok = wx.Button(panel, label="&OK")
        ok.SetToolTip("Keep what the check box says (Alt+O)")
        ok.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        cancel = wx.Button(panel, label="&Cancel")
        cancel.SetToolTip("Leave adult sexual content out (Alt+C)")
        cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        for b in (ok, cancel):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        panel.SetSizer(s)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.box.SetFocus()

    def chosen(self):
        """True when the box is ticked."""
        return self.box.GetValue()

    def on_key(self, event):
        """Escape is Cancel; F1 opens READ ME FIRST.txt; Alt+A moves to the explanation."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif key == wx.WXK_F1:
            open_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()


GRAPHIC_QUESTION = "Also include graphic scenes: war, disasters, injuries and death, described plainly?"
GRAPHIC_ABOUT = ("Graphic scenes are photographs of war, disasters, injuries and death: the dead and wounded, wounds, "
                 "destroyed towns, and the dangers around someone caught in a war zone or a disaster, such as rubble, "
                 "fire, floods, fallen power lines and warning signs. They are described accurately and plainly, from "
                 "each photograph's own caption, without hiding what they show. Nothing sexual is included, nor "
                 "pictures whose focus is a dead or injured child. They are never used for a picture-making model. "
                 "Leave the box unticked to leave them out.")


class GraphicDialog(wx.Dialog):
    """Asked when "Include medical and anatomy pictures" is ticked for a picture describer: "Also include graphic
    scenes: war, disasters, injuries and death, described plainly?", with an explanation (a read-only field), a check
    box (ticked when value: at first, for the describer) and OK and Cancel. OK keeps what the box says; Cancel or
    Escape leaves graphic scenes out. Standard controls, a label before the field, Alt letters named in the tooltips
    (A, G, O, C), no default button, F1 opens READ ME FIRST.txt."""

    def __init__(self, parent, value=True):
        """The explanation, the check box (ticked when value) and the two buttons."""
        super().__init__(parent, title="Graphic scenes", size=(620, 400),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.mnemonics = {}
        panel = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(wx.StaticText(panel, label="&About this choice:"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self.about = wx.TextCtrl(panel, value=f"{GRAPHIC_QUESTION} {GRAPHIC_ABOUT}",
                                 style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.Add(self.about, 1, wx.EXPAND | wx.ALL, 8)
        self.mnemonics["a"] = self.about
        self.box = wx.CheckBox(panel, label="Also include &graphic scenes: war, disasters, injuries and death, "
                                            "described plainly")
        self.box.SetValue(bool(value))
        self.box.SetToolTip("Photographs of war, disasters, injuries and death, described plainly; never for "
                            "picture-making (Alt+G)")
        s.Add(self.box, 0, wx.ALL, 8)
        row = wx.BoxSizer(wx.HORIZONTAL)
        ok = wx.Button(panel, label="&OK")
        ok.SetToolTip("Keep what the check box says (Alt+O)")
        ok.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        cancel = wx.Button(panel, label="&Cancel")
        cancel.SetToolTip("Leave graphic scenes out (Alt+C)")
        cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        for b in (ok, cancel):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        panel.SetSizer(s)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.box.SetFocus()

    def chosen(self):
        """True when the box is ticked."""
        return self.box.GetValue()

    def on_key(self, event):
        """Escape is Cancel; F1 opens READ ME FIRST.txt; Alt+A moves to the explanation."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif key == wx.WXK_F1:
            open_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()


# ----------------------------------------------------------------- "Personal use: everything allowed"

# The boxes the switch ticks: share-alike (Wikipedia and the other CC BY-SA collections), non-commercial and
# research-only. It never touches the content choices (art with nudity, medical and anatomy pictures, graphic scenes,
# adult sexual content): those keep their own explicit questions.
EVERYTHING_BOXES = ("wikipedia", "noncommercial", "research")
EVERYTHING_GROUPS = ("share-alike", "noncommercial", "research")
EVERYTHING_ABOUT = (
    "Personal use: everything allowed ticks every collection you may use for your own, private training: the open "
    "ones, the share-alike ones (Wikipedia and other CC BY-SA collections), the non-commercial ones, the research-only "
    "ones, and the sign-up ones whose key or files are on this computer. "
    "What it means: the model you train is for your personal, private use only. Never publish it, share it, sell it "
    "or put it in a product. The licences of the non-commercial and research collections forbid selling the model or "
    "anything it makes. "
    "What it does not do: it does not tick art with nudity, medical and anatomy pictures, graphic scenes or adult "
    "sexual content; those keep their own questions. For a picture-making model, collections of people and every "
    "collection not allowed for picture-making are still left out. "
    "Unticking it puts the three boxes back as they were before.")


def parse_size(text):
    """The number of bytes in a download size written for people ("7.6 GB", "about 400 MB of pictures"); 0 when
    none is given."""
    m = re.search(r"([\d.,]+)\s*(KB|MB|GB|TB)\b", str(text or ""), re.I)
    if not m:
        return 0
    try:
        number = float(m.group(1).replace(",", ""))
    except ValueError:
        return 0
    return int(number * 1024 ** ("KB", "MB", "GB", "TB").index(m.group(2).upper()) * 1024)


def size_words(size):
    """A size in bytes in plain words ("about 12.5 gigabytes")."""
    if size >= 1024 ** 4:
        return f"about {size / 1024 ** 4:.1f} terabytes"
    if size >= 1024 ** 3:
        return f"about {size / 1024 ** 3:.1f} gigabytes"
    return f"about {max(1, round(size / 1024 ** 2))} megabytes"


def everything_collections(module, kind, contents):
    """(collections the switch would add, sign-up collections left out for want of a key or files) for a kind of
    training: the collections of EVERYTHING_GROUPS whose content the current content choices allow; for a
    picture-making model not those in NOT_FOR_PICTURE_MAKING, and a personal-use one only when it is in
    PERSONAL_PICTURE_MAKING_OK. module is the kit's sources.py; contents a set from allowed_contents."""
    if module is None:
        return [], []
    never = set(getattr(module, "NOT_FOR_PICTURE_MAKING", ()) or ())
    making_ok = set(getattr(module, "PERSONAL_PICTURE_MAKING_OK", ()) or ())
    ready = getattr(module, "signup_ready", lambda s: True)
    added, waiting = [], []
    for s in module.SOURCES:
        if s.group not in EVERYTHING_GROUPS or s.content not in contents:
            continue
        if kind == "pictures" and (s.key in never or (s.group in ("noncommercial", "research")
                                                       and s.key not in making_ok)):
            continue
        (added if ready(s) else waiting).append(s)
    return added, waiting


def everything_on(before):
    """The three boxes with the switch ticked (before, the boxes as they were, is kept by the caller)."""
    return {box: True for box in EVERYTHING_BOXES}


def everything_off(before):
    """The three boxes after unticking the switch: as they were before it was ticked (all off when unknown)."""
    before = before or {}
    return {box: bool(before.get(box, False)) for box in EVERYTHING_BOXES}


def everything_text(module, kind, contents):
    """The switch's explanation with the collections it adds, their total download size and the sign-up collections
    still waiting for a key, and the research-only terms, for EverythingDialog."""
    added, waiting = everything_collections(module, kind, contents)
    total = sum(parse_size(s.download) for s in added)
    parts = [EVERYTHING_ABOUT,
             f"It adds {len(added)} collection{'s' if len(added) != 1 else ''}, {size_words(total)} to download in all "
             "(roughly; pictures already in your picture library are not downloaded again)."]
    if waiting:
        parts.append("Sign-up collections left out until their key or files are on this computer (press Sign-up "
                     "keys to add keys): " + "; ".join(s.name for s in waiting) + ".")
    parts.append(research_terms_text(research_collections()))
    return "\n\n".join(parts)


class EverythingDialog(wx.Dialog):
    """Asked when "Personal use: everything allowed" is ticked: what it means in plain words, the collections it adds
    with their total download size, the research-only terms (one read-only field), "I understand ..." (needed), and
    OK, Sign-up keys and Cancel. OK without the tick says what is missing; Cancel or Escape leaves everything as it
    was. Standard controls, a label before the field, Alt letters named in the tooltips (A, I, O, K, C), no default
    button, F1 opens READ ME FIRST.txt."""

    def __init__(self, parent, text):
        """The explanation, the agreement box and the three buttons."""
        super().__init__(parent, title="Personal use: everything allowed", size=(700, 560),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.mnemonics = {}
        panel = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(wx.StaticText(panel, label="&About this choice:"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self.about = wx.TextCtrl(panel, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.Add(self.about, 1, wx.EXPAND | wx.ALL, 8)
        self.mnemonics["a"] = self.about
        self.agree_box = wx.CheckBox(panel, label="&I understand: personal, private use only, never published or "
                                                  "sold, and I agree to the research-only terms")
        self.agree_box.SetToolTip("Needed before OK (Alt+I)")
        s.Add(self.agree_box, 0, wx.ALL, 8)
        row = wx.BoxSizer(wx.HORIZONTAL)
        ok = wx.Button(panel, label="&OK")
        ok.SetToolTip("Tick every collection allowed for personal use (Alt+O)")
        ok.Bind(wx.EVT_BUTTON, self.on_ok)
        keys = wx.Button(panel, label="Sign-up &keys...")
        keys.SetToolTip("Enter your own keys for the sign-up collections (Alt+K)")
        keys.Bind(wx.EVT_BUTTON, self.on_keys)
        cancel = wx.Button(panel, label="&Cancel")
        cancel.SetToolTip("Leave the boxes as they are (Alt+C)")
        cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        for b in (ok, keys, cancel):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        panel.SetSizer(s)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.about.SetFocus()

    def on_ok(self, _event):
        """OK: only with the agreement ticked; otherwise say what is missing and stay open."""
        if not self.agree_box.GetValue():
            speak("First tick I understand, with Alt+I, then press OK.", True)
            self.agree_box.SetFocus()
            return
        self.EndModal(wx.ID_OK)

    def on_keys(self, _event):
        """Open the Sign-up keys window."""
        dialog = SignupKeysDialog(self)
        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

    def on_key(self, event):
        """Escape is Cancel; F1 opens READ ME FIRST.txt; Alt+A moves to the explanation."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif key == wx.WXK_F1:
            open_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()


def signup_module():
    """The kit's signup_sources.py (bundled into the program, or beside the wizard in the kit); None when it cannot
    be loaded."""
    folder = resource("kit")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    try:
        import signup_sources
        return signup_sources
    except Exception:  # noqa: BLE001 - said by the caller
        return None


class SignupKeysDialog(wx.Dialog):
    """The owner's own keys for the sign-up collections: an explanation (where to get each key, the terms line agreed
    to, what it adds, and never to paste a key into a chat or an e-mail), one hidden-text field per key, Save and
    Cancel. The keys are saved only in the user's own settings folder (signup_sources.KEY_FILE), never in the kit
    folder, and never written to the log or said. A key already set as a Windows environment variable is used first;
    its field says so. Letters: A (the explanation), S (Save), C (Cancel); the key fields have labels without letters.
    Escape is Cancel; F1 opens READ ME FIRST.txt; no default button."""

    def __init__(self, parent):
        """The explanation, the key fields and the two buttons."""
        super().__init__(parent, title="Sign-up keys", size=(700, 620), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.module = signup_module()
        self.mnemonics = {}
        self.fields = {}
        panel = wx.Panel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(wx.StaticText(panel, label="&About these keys:"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        text = self.module.keys_text() if self.module else "The sign-up collections are missing from this program."
        self.about = wx.TextCtrl(panel, value=text, style=wx.TE_MULTILINE | wx.TE_READONLY)
        s.Add(self.about, 1, wx.EXPAND | wx.ALL, 8)
        self.mnemonics["a"] = self.about
        saved = self.module.load_key_file() if self.module else {}
        for name, (label, _where) in (self.module.SIGNUP_KEYS.items() if self.module else []):
            in_windows = bool(os.environ.get(name, "").strip()) and name not in saved
            s.Add(wx.StaticText(panel, label=f"{label} ({name}{', set in Windows' if in_windows else ''}):"), 0,
                  wx.LEFT | wx.RIGHT | wx.TOP, 8)
            field = wx.TextCtrl(panel, value=saved.get(name, ""), style=wx.TE_PASSWORD)
            s.Add(field, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
            self.fields[name] = field
        row = wx.BoxSizer(wx.HORIZONTAL)
        save = wx.Button(panel, label="&Save")
        save.SetToolTip("Keep the keys in your own settings folder on this computer (Alt+S)")
        save.Bind(wx.EVT_BUTTON, self.on_save)
        cancel = wx.Button(panel, label="&Cancel")
        cancel.SetToolTip("Close without saving (Alt+C)")
        cancel.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        for b in (save, cancel):
            row.Add(b, 0, wx.ALL, 4)
        s.Add(row, 0, wx.ALL, 4)
        panel.SetSizer(s)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.about.SetFocus()

    def values(self):
        """{key name: what is typed} (never logged)."""
        return {name: field.GetValue().strip() for name, field in self.fields.items()}

    def on_save(self, _event):
        """Save the keys in the user's own settings folder and say how many (never their values)."""
        if self.module is None:
            self.EndModal(wx.ID_CANCEL)
            return
        values = self.values()
        if self.module.save_key_file(values):
            count = sum(1 for v in values.values() if v)
            speak(f"{count} key{'s' if count != 1 else ''} saved on this computer.", True)
            log(f"Sign-up keys saved: {count} (the keys themselves are never written here).")
            self.EndModal(wx.ID_OK)
        else:
            speak("The keys could not be saved in your settings folder.", True)

    def on_key(self, event):
        """Escape is Cancel; F1 opens READ ME FIRST.txt; Alt+A moves to the explanation."""
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        elif key == wx.WXK_F1:
            open_help(None)
        elif event.AltDown() and not event.ControlDown() and 0 < key < 256 and chr(key).lower() in self.mnemonics:
            self.mnemonics[chr(key).lower()].SetFocus()
        else:
            event.Skip()


def open_help(kit):
    """Open READ ME FIRST.txt (the kit folder's copy when there is one, else the program's)."""
    path = os.path.join(kit, "READ ME FIRST.txt") if kit else resource("READ ME FIRST.txt")
    if os.path.exists(path) and hasattr(os, "startfile"):
        os.startfile(path)  # noqa: S606 - opens the text file in Notepad


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
        # Adult sexual content (review collections): asked when art with nudity is ticked (SexualDialog), only for
        # a picture describer, remembered for it; never for a picture-making model.
        self.sexual = {kind: bool(chosen.get(f"sexual_{kind}", False)) and kind == "describer" for kind, _ in KINDS}
        # Graphic scenes (war, disasters, injuries and death): asked when medical and anatomy pictures are ticked
        # (GraphicDialog), only for a picture describer, where it starts ticked; remembered for each kind, never used
        # for a picture-making model.
        self.graphic = {kind: bool(chosen.get(f"graphic_{kind}", kind == "describer")) and kind == "describer"
                        for kind, _ in KINDS}
        self.nudity = self.check(page, "Include art with nudit&y (non-sexual)",
                                 "Paintings, drawings, sculptures and photographs from museums that show nude people, "
                                 "described plainly; nothing sexual and no children. For a picture describer, ticking "
                                 "it asks whether to include adult sexual content from collections you have reviewed",
                                 False)
        self.nudity.Bind(wx.EVT_CHECKBOX, self.on_nudity)
        s.Add(self.nudity, 0, wx.ALL, 8)
        self.medical = self.check(page, "Include medical and &anatomy pictures",
                                  "Anatomy textbook figures and old anatomy plates showing the inside and outside of "
                                  "the human body, with their captions. For a picture describer, ticking it asks "
                                  "whether to include graphic scenes: war, disasters, injuries and death", False)
        self.medical.Bind(wx.EVT_CHECKBOX, self.on_medical)
        s.Add(self.medical, 0, wx.ALL, 8)
        # The personal-use collections, remembered for each kind of training, both off at first. Few Alt letters are
        # left, so theirs (Q and Z) are shown in brackets.
        self.personal = {kind: {"noncommercial": bool(chosen.get(f"noncommercial_{kind}", False)),
                                "research": bool(chosen.get(f"research_{kind}", False))} for kind, _ in KINDS}
        self.noncommercial = self.check(page, "Include non-commercial collections (personal use only) (&Q)",
                                        NONCOMMERCIAL_HINT, False)
        self.noncommercial.Bind(wx.EVT_CHECKBOX, self.on_noncommercial)
        s.Add(self.noncommercial, 0, wx.ALL, 8)
        self.noncommercial_hint = wx.StaticText(page, label=NONCOMMERCIAL_HINT)
        s.Add(self.noncommercial_hint, 0, wx.LEFT | wx.RIGHT, 28)
        self.research = self.check(page, "Include research-only collections (personal use only) (&Z)",
                                   "Collections whose terms allow only research or academic use; you are shown their "
                                   "terms and must agree first. Personal use only", False)
        self.research.Bind(wx.EVT_CHECKBOX, self.on_research)
        s.Add(self.research, 0, wx.ALL, 8)
        # "Personal use: everything allowed": ticks the share-alike, non-commercial and research boxes at once (after
        # EverythingDialog), and unticking it puts them back as they were. Remembered for each kind with the boxes
        # as they were before ("everything_<kind>", "before_everything_<kind>"). Every letter of this window is
        # taken, so its key is Alt+1.
        self.everything = {kind: bool(chosen.get(f"everything_{kind}", False)) for kind, _ in KINDS}
        self.before_everything = {kind: dict(chosen.get(f"before_everything_{kind}") or {}) for kind, _ in KINDS}
        self.everything_box = self.check(page, "Personal use: everything allowed (&1)",
                                         "Ticks every collection you may use for personal, private training: "
                                         "share-alike, non-commercial, research-only and the sign-up ones with your "
                                         "own keys; never published or sold; not the content choices", False)
        self.everything_box.Bind(wx.EVT_CHECKBOX, self.on_everything)
        s.Add(self.everything_box, 0, wx.ALL, 8)
        if self.everything.get(self.kind_key()):
            self.wikipedia.SetValue(True)
        self.wikipedia.Bind(wx.EVT_CHECKBOX, self.on_wikipedia)
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
        self.noncommercial.SetValue(self.personal[kind]["noncommercial"])
        self.research.SetValue(self.personal[kind]["research"])
        if hasattr(self, "everything_box"):         # not yet while the page is being built
            self.everything_box.SetValue(self.everything.get(kind, False))
            if self.everything.get(kind):
                self.wikipedia.SetValue(True)
                self.noncommercial.SetValue(True)
                self.research.SetValue(True)
        if getattr(self, "first", None):          # not yet while the page is being built
            self.first.Layout()

    def on_kind(self, _event):
        """Another kind chosen: keep the content choices of the one before, show the fitting fields, and say it."""
        self.content[self.shown_kind] = {"nudity": self.nudity.GetValue(), "medical": self.medical.GetValue()}
        self.personal[self.shown_kind] = self.personal_choice()
        self.everything[self.shown_kind] = self.everything_box.GetValue()
        self.sexual["pictures"] = False                 # never for a picture-making model
        self.graphic["pictures"] = False                # never for a picture-making model
        self.shown_kind = self.kind_key()
        self.show_kind(self.shown_kind)
        ticked = [w for w, c in (("art with nudity", self.nudity), ("medical and anatomy pictures", self.medical))
                  if c.GetValue()]
        if self.sexual_on():
            ticked.append("adult sexual content from collections you have reviewed")
        if self.graphic_on():
            ticked.append("graphic scenes")
        speak(("Picture-making model chosen: choose Stable Diffusion in Picture-making model. "
               if self.shown_kind == "pictures" else "Picture describer chosen. ")
              + ("Ticked: " + " and ".join(ticked) + "." if ticked else
                 "Art with nudity and medical pictures are not ticked.")
              + (" " + PERSONAL_NOTE if self.is_personal() else ""), True)

    # -- adult sexual content (review collections)
    def sexual_on(self):
        """True when adult sexual content is chosen: only for a picture describer, and only with art with nudity."""
        kind = self.kind_key()
        return kind == "describer" and self.nudity.GetValue() and self.sexual.get(kind, False)

    def on_nudity(self, _event):
        """Art with nudity ticked or unticked. For a picture describer, ticking it asks whether to include adult
        sexual content from reviewed collections (SexualDialog); unticking it turns that off too."""
        kind = self.kind_key()
        if not self.nudity.GetValue():
            had = self.sexual.get(kind, False)
            self.sexual[kind] = False
            self.show_result("Art with nudity left out." + (" Adult sexual content is left out too: it needs art "
                                                            "with nudity." if had else ""))
            return
        if kind != "describer":
            self.sexual[kind] = False                  # never for a picture-making model
            self.show_result("Art with nudity included. Adult sexual content is never used for a picture-making "
                             "model.")
            return
        self.sexual[kind] = self.ask_sexual(self.sexual.get(kind, False))
        self.show_result("Art with nudity included. " + ("Adult sexual content from collections you have reviewed "
                                                         "included: only checked pictures, for personal use only."
                                                         if self.sexual[kind] else "Adult sexual content left out."))
        self.nudity.SetFocus()

    def ask_sexual(self, value):
        """Show SexualDialog; True when the person ticked its box and pressed OK (Cancel and Escape: False)."""
        dialog = SexualDialog(self, value)
        try:
            speak(f"{SEXUAL_QUESTION} The check box is ticked." if value else SEXUAL_QUESTION, True)
            return dialog.ShowModal() == wx.ID_OK and dialog.chosen()
        finally:
            dialog.Destroy()

    # -- graphic scenes: war, disasters, injuries and death
    def graphic_on(self):
        """True when graphic scenes are chosen: only for a picture describer, and only while medical and anatomy
        pictures are ticked (the question is asked with them)."""
        kind = self.kind_key()
        return kind == "describer" and self.medical.GetValue() and self.graphic.get(kind, False)

    def on_medical(self, _event):
        """Medical and anatomy pictures ticked or unticked. For a picture describer, ticking them asks whether to
        include graphic scenes (GraphicDialog: its box starts as last answered, ticked at first); unticking them leaves
        graphic scenes out too (the answer is kept for the next time the box is ticked)."""
        kind = self.kind_key()
        if not self.medical.GetValue():
            self.show_result("Medical and anatomy pictures left out." + (" Graphic scenes are left out too: they are "
                                                                         "chosen with medical pictures."
                                                                         if self.graphic.get(kind) else ""))
            return
        if kind != "describer":
            self.graphic[kind] = False                 # never for a picture-making model
            self.show_result("Medical and anatomy pictures included. Graphic scenes are never used for a "
                             "picture-making model.")
            return
        self.graphic[kind] = self.ask_graphic(self.graphic.get(kind, True))
        self.show_result("Medical and anatomy pictures included. " + (
            "Graphic scenes included: war, disasters, injuries and death, described plainly." if self.graphic[kind]
            else "Graphic scenes left out."))
        self.medical.SetFocus()

    def ask_graphic(self, value):
        """Show GraphicDialog; True when the person left its box ticked and pressed OK (Cancel and Escape: False)."""
        dialog = GraphicDialog(self, value)
        try:
            speak(f"{GRAPHIC_QUESTION} The check box is ticked." if value else
                  f"{GRAPHIC_QUESTION} The check box is not ticked.", True)
            return dialog.ShowModal() == wx.ID_OK and dialog.chosen()
        finally:
            dialog.Destroy()

    # -- the personal-use collections
    def personal_choice(self):
        """{"noncommercial": ticked, "research": ticked}: the personal-use boxes as they are now."""
        return {"noncommercial": self.noncommercial.GetValue(), "research": self.research.GetValue()}

    def is_personal(self):
        """True when either personal-use box is ticked: the training is then for personal use only."""
        return self.noncommercial.GetValue() or self.research.GetValue()

    def say_personal(self, first=""):
        """Show and say first in Check result, followed by the personal-use note when either box is ticked."""
        text = (first + (" " + PERSONAL_NOTE if self.is_personal() else "")).strip()
        self.show_result(text)

    def on_noncommercial(self, _event):
        """The non-commercial box changed: say what it means."""
        self.box_changed_by_hand(self.noncommercial)
        if self.noncommercial.GetValue():
            self.say_personal("Non-commercial collections included. " + NONCOMMERCIAL_HINT)
        else:
            self.say_personal("Non-commercial collections left out.")

    def on_research(self, _event):
        """The research box was ticked: show the research-only collections' terms; it stays ticked only when the
        person ticks "I have read these terms ..." and presses Agree (Cancel unticks it)."""
        self.box_changed_by_hand(self.research)
        if not self.research.GetValue():
            self.say_personal("Research-only collections left out.")
            return
        if self.agree_to_research_terms():
            self.say_personal("Research-only collections included; you agreed to their terms.")
        else:
            self.research.SetValue(False)
            self.say_personal("Research-only collections left out: their terms were not agreed to.")
        self.research.SetFocus()

    # -- "Personal use: everything allowed"
    def boxes(self):
        """{"wikipedia", "noncommercial", "research": ticked} as the boxes are now."""
        return {"wikipedia": self.wikipedia.GetValue(), "noncommercial": self.noncommercial.GetValue(),
                "research": self.research.GetValue()}

    def set_boxes(self, values):
        """Tick or untick the three boxes (no questions asked)."""
        self.wikipedia.SetValue(values["wikipedia"])
        self.noncommercial.SetValue(values["noncommercial"])
        self.research.SetValue(values["research"])

    def box_changed_by_hand(self, box):
        """One of the three boxes was unticked by hand while the switch is on: the switch goes off (the boxes stay as
        they are now)."""
        if self.everything_box.GetValue() and not box.GetValue():
            self.everything_box.SetValue(False)
            self.everything[self.kind_key()] = False

    def on_wikipedia(self, _event):
        """The Wikipedia (share-alike) box changed by hand."""
        self.box_changed_by_hand(self.wikipedia)

    def on_everything(self, _event):
        """The switch ticked: explain it first (EverythingDialog, with the total download size); OK ticks the
        share-alike, non-commercial and research boxes, keeping how they were. Unticked: the boxes go back."""
        kind = self.kind_key()
        if not self.everything_box.GetValue():
            self.set_boxes(everything_off(self.before_everything.get(kind)))
            self.everything[kind] = False
            self.say_personal("Personal use: everything allowed is off. The collection boxes are back as they were.")
            return
        module = sources_module()
        contents, _categories = self.content_checks()
        dialog = EverythingDialog(self, everything_text(module, kind, contents))
        try:
            speak("Personal use: everything allowed. Read what it means, tick I understand, then press OK.", True)
            agreed = dialog.ShowModal() == wx.ID_OK
        finally:
            dialog.Destroy()
        if not agreed:
            self.everything_box.SetValue(False)
            self.say_personal("Personal use: everything allowed was not turned on; nothing changed.")
            self.everything_box.SetFocus()
            return
        self.before_everything[kind] = self.boxes()
        self.set_boxes(everything_on(self.before_everything[kind]))
        self.everything[kind] = True
        added, waiting = everything_collections(module, kind, contents)
        size = size_words(sum(parse_size(s.download) for s in added))
        self.say_personal(f"Personal use: everything allowed is on: {len(added)} collections, {size} to download. "
                          + (f"{len(waiting)} sign-up collections wait for a key. " if waiting else "")
                          + "Never publish or sell what you train.")
        self.everything_box.SetFocus()

    def agree_to_research_terms(self):
        """Show ResearchTermsDialog; True when the person agreed."""
        dialog = ResearchTermsDialog(self, research_collections())
        try:
            return dialog.ShowModal() == wx.ID_OK
        finally:
            dialog.Destroy()

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
        self.result_button = self.button(page, "Open the result &folder",
                                         "The zip to send, which also installs in the toolkit", self.on_open_result)
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
        contents, categories = self.content_checks()
        review = self.kind_key() == "describer"         # a picture-making model never uses review collections

        def check():
            """Check the folder; the result is shown on the window's own thread."""
            try:
                try:
                    _rows, _problems, summary = module.check_folder(folder, contents=contents, categories=categories,
                                                                   review=review)
                except TypeError:                       # an older own_data.py without the content rules
                    _rows, _problems, summary = module.check_folder(folder)
            except Exception as e:  # noqa: BLE001 - said in plain words
                summary = f"Your pictures could not be checked: {e}"
            wx.CallAfter(self.show_result, summary)
        threading.Thread(target=check, daemon=True).start()

    def content_checks(self):
        """(content tags allowed, review categories allowed) for own_data.check_folder, from the boxes as they are
        now (a picture-making model: never intimate, sexual or graphic)."""
        nudity, medical = self.nudity.GetValue(), self.medical.GetValue()
        module = sources_module()
        if module is not None and hasattr(module, "allowed_contents"):
            try:
                contents = module.allowed_contents(nudity, medical, self.sexual_on(), self.graphic_on())
            except TypeError:                          # an older sources.py without the graphic-scenes choice
                contents = module.allowed_contents(nudity, medical, self.sexual_on())
        else:
            contents = {""} | {t for t, on in (("nudity", nudity), ("medical", medical),
                                               ("graphic", self.graphic_on())) if on}
        if self.kind_key() != "describer":
            contents -= {"intimate", "sexual", "graphic"}
        categories = {"", "open", "share-alike", "permission"} | {c for c, on in self.personal_choice().items() if on}
        return contents, categories

    def review_folders(self):
        """The review workspaces in the picture library's Review folder (passed to train.py as --review)."""
        try:
            import describe_window
            return describe_window.review_workspaces(self.library.GetValue().strip())
        except Exception:  # noqa: BLE001 - no review collections then
            return []

    def on_describe(self, _event):
        """Open the Describe pictures window; when it says "Use this workspace for training", the workspace goes
        into Your own pictures folder."""
        try:
            import describe_window
        except Exception as e:  # noqa: BLE001 - said in plain words
            self.show_result(f"The Describe pictures window cannot be opened: {e}")
            return
        kit = os.path.join(self.folder.GetValue().strip(), KIT_NAME) if self.folder.GetValue().strip() else None
        with describe_window.DescribeWindow(self, sys.modules[__name__], kit,
                                            self.library.GetValue().strip() or None) as window:
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
        open_help(self.kit)

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
        self.personal[kind] = self.personal_choice()
        self.everything[kind] = self.everything_box.GetValue()
        sexual = self.sexual_on()
        graphic = self.graphic_on()
        choices = {"folder": self.folder.GetValue(), "library": self.library.GetValue(),
                   "model": MODELS[self.model.GetSelection()][0], "size": size,
                   "wikipedia": self.wikipedia.GetValue(), "prepare": self.prepare.GetValue(), "what": kind,
                   "picture_model": PICTURE_MODELS[self.picture_model.GetSelection()][0], "own_folder": own,
                   "own_only": self.own_only.GetValue()}
        for name, values in self.content.items():
            choices[f"nudity_{name}"], choices[f"medical_{name}"] = values["nudity"], values["medical"]
        choices["sexual_describer"] = bool(self.sexual.get("describer"))   # never remembered for picture-making
        choices["sexual_pictures"] = False
        choices["graphic_describer"] = bool(self.graphic.get("describer"))  # remembered for each kind
        choices["graphic_pictures"] = False                                 # never for picture-making
        for name, values in self.personal.items():     # the personal-use boxes, for each kind
            choices[f"noncommercial_{name}"], choices[f"research_{name}"] = values["noncommercial"], values["research"]
        for name, on in self.everything.items():     # the switch, and the boxes as they were before it, for each kind
            choices[f"everything_{name}"] = bool(on)
            choices[f"before_everything_{name}"] = self.before_everything.get(name) or {}
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
        reviews = self.review_folders() if kind == "describer" else []    # never for a picture-making model
        if sexual and kind == "describer":
            args.append("--with-sexual")             # only ever with --with-nudity (sexual_on)
        if graphic and kind == "describer":
            args.append("--with-graphic")            # only while medical pictures are ticked (graphic_on)
        for folder in reviews:
            args += ["--review", folder]
        if reviews:
            note = (f"{len(reviews)} review collection{'s' if len(reviews) != 1 else ''} in the library: only their "
                    "checked pictures are used, as the content choices allow. With any of them this training will be "
                    "for personal use only.")
            self.lines.put(note)
            speak(note)
        if self.noncommercial.GetValue():
            args.append("--personal-noncommercial")
        if self.research.GetValue():                 # only ticked after Agree in the terms window
            args += ["--personal-research", "--accept-research-terms"]
        self.personal_run = self.is_personal()
        if self.personal_run:
            self.lines.put(PERSONAL_NOTE)            # into the Status field and Everything said
            speak(PERSONAL_NOTE)
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
            if is_computer_line(line):           # computer use: logged, not put in Status or said (warnings are)
                if line.lstrip().startswith("Computer use warning"):
                    speak(line.strip())
                continue
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
        personal = getattr(self, "personal_run", False) and PERSONAL_NOTE not in self.status.GetValue()
        speak(f"{self.status.GetValue()} Overall {self.percent} percent." + (" " + PERSONAL_NOTE if personal else ""),
              True)

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
                 os.path.join("kit", "run_review.cmd"), os.path.join("kit", "run_review.py"),
                 os.path.join("kit", "review_sources.py"), os.path.join("kit", "requirements.txt"),
                 os.path.join("kit", "make_toolkit_addon.py"), "Make Toolkit Add-on.cmd"):
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
    kit_sources = sources_module()
    if kit_sources is None or not hasattr(kit_sources, "PERSONAL_GROUPS"):
        raise SystemExit("sources.py cannot be loaded, or has no personal-use groups")
    research_terms_text(research_collections())     # the research-terms list can be read
    import describe_window
    package = describe_window.load_package_module(sys.modules[__name__])
    if package is None:
        raise SystemExit("describe_package.py cannot be loaded")
    with tempfile.TemporaryDirectory() as folder:
        package.self_test(folder)                   # make, describe, export and import a tiny workspace
        rows, _problems, _summary = module.check_folder(os.path.join(folder, "second"))
        if len(rows) != 1:
            raise SystemExit("own_data.check_folder did not read the self-test workspace")
        review_self_test(package, module, kit_sources, os.path.join(folder, "review"))
    app = wx.App()
    window = Wizard()
    window.kind.SetSelection(1)                    # both kinds of training can be shown
    window.on_kind(None)
    window.kind.SetSelection(0)
    window.on_kind(None)
    ResearchTermsDialog(window, research_collections()).Destroy()    # the research-terms window can be made
    SexualDialog(window).Destroy()                                    # the adult sexual content question
    GraphicDialog(window).Destroy()                                   # the graphic scenes question
    EverythingDialog(window, everything_text(kit_sources, "describer", {""})).Destroy()   # the switch's window
    SignupKeysDialog(window).Destroy()                                # the sign-up keys window
    describe = describe_window.DescribeWindow(window, sys.modules[__name__], None, tempfile.gettempdir())
    describe_window.ReviewDialog(describe, sys.modules[__name__], tempfile.gettempdir()).Destroy()
    describe.Destroy()
    window.Destroy()
    app.Destroy()
    print("OK")


def review_self_test(package, own_data, kit_sources, folder):
    """For the build: a tiny review-only workspace trains nothing until its picture is marked checked (a described
    picture, and a draft still saying "<description needed>", are refused), and an intimate picture needs both art
    with nudity and medical pictures. Raises SystemExit when something is wrong."""
    workspace = package.make_workspace(folder, "Self-test review")
    workspace.data.update(review_only=True, content="medical", review_source="self_test", review_category="open")
    workspace.save()
    source = os.path.join(os.path.dirname(folder), "review-source")
    os.makedirs(source, exist_ok=True)
    with open(os.path.join(source, "grey.png"), "wb") as f:
        f.write(package.tiny_png())
    package.add_pictures(workspace, [source], "Tester")
    every = kit_sources.allowed_contents(True, True, True)

    def used():
        """How many rows the workspace gives with every content choice made."""
        return len(own_data.check_folder(folder, contents=every)[0])
    package.describe(workspace, "grey.png", "A plain grey square. <description needed>", "Tester")
    if used():
        raise SystemExit("a review picture that is only described was trained on")
    try:
        package.mark_checked(workspace, "grey.png", "Checker")
        raise SystemExit("a description saying <description needed> could be marked checked")
    except package.PackageProblem:
        pass
    package.describe(workspace, "grey.png", "A plain grey square.", "Tester")
    if used():
        raise SystemExit("a described (not checked) review picture was trained on")
    package.mark_checked(workspace, "grey.png", "Checker")
    rows = own_data.check_folder(folder, contents=every)[0]
    if len(rows) != 1 or not rows[0].get("review"):
        raise SystemExit("a checked review picture was not used")
    if own_data.check_folder(folder, contents=every, review=False)[0]:
        raise SystemExit("a review picture was used with review=False (picture-making)")
    workspace = package.open_workspace(folder)
    workspace.entry("grey.png")["content"] = "intimate"
    workspace.save()
    if own_data.check_folder(folder, contents=kit_sources.allowed_contents(False, True))[0]:
        raise SystemExit("an intimate picture was used without art with nudity")
    if len(own_data.check_folder(folder, contents=kit_sources.allowed_contents(True, True))[0]) != 1:
        raise SystemExit("an intimate picture was not used with art with nudity and medical pictures")


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
