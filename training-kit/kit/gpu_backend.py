"""Which graphics card the kit trains on, and how: NVIDIA (CUDA, unchanged, always first) or, as a second choice
that is new and being tested, an AMD Radeon with AMD's own PyTorch for Windows (ROCm).

Order of preference, as the owner asked:
  1. an NVIDIA card (its driver's tool nvidia-smi is found): the kit's usual way, CUDA PyTorch from
     kit\\requirements.txt; nothing here changes it;
  2. otherwise an AMD Radeon that AMD's ROCm PyTorch wheels for Windows support (kit\\requirements-amd.txt);
  3. otherwise the kit stops with its usual message (it needs an NVIDIA card).

Two moments use this file:
  * before anything is installed, kit\\amd_setup.cmd (called by run.cmd and run_pictures.cmd when there is no
    NVIDIA driver) and the wizard run "python gpu_backend.py --check": it reads the graphics cards' names from
    Windows (WMI, Win32_VideoController: the name and the PCI vendor number, 1002 for AMD) and says in plain words
    whether AMD's wheels support that card. Exit code 0: an AMD card AMD supports; 2: no AMD card; 3: an AMD card
    AMD's wheels do not support; 4: an AMD card whose name the kit does not know (the person can still try with
    KIT_AMD_TRY=1, and the training then checks the chip itself).
  * during training, train.py and train_pictures.py ask torch_device() which card PyTorch sees, which backend it
    is ("cuda" for NVIDIA, "rocm" for AMD: AMD's PyTorch answers through the same torch.cuda functions, with
    torch.version.hip set), the chip (gcnArchName, for example gfx1151), the memory the kit may plan with, the
    number type to compute in, and which NVIDIA-only parts must be swapped for ordinary ones. Every choice and its
    reason is said in the training log (report_lines()).

What changes on AMD (and why):
  * bitsandbytes (the 8-bit AdamW optimisers and the 4-bit model loading) works only on NVIDIA cards on Windows, so
    on AMD the kit uses PyTorch's ordinary AdamW and loads the model in 16 bits (it needs more memory: see
    AMD_MEMORY_NEEDED in train.py);
  * flash-attention and torch.compile are not used by the kit at all; attention is PyTorch's own (SDPA), which works
    on AMD;
  * the number type: bf16 when PyTorch says the chip has it and a small test sum works, otherwise fp16 (AMD's
    support table lists only fp16 for Windows); fp16 training uses a gradient scaler;
  * memory: a Ryzen AI Max (and other processors with built-in graphics) shares the computer's memory with the
    graphics. Windows reports a budget (the dedicated part, sometimes with the shared part added) that the rest of
    the computer also needs, so the kit plans with the smallest of: what PyTorch reports, what PyTorch says is free
    now, and three quarters of the computer's memory (conservative_memory_gb()).

AMD's own limits (from AMD's Windows notes for ROCm 7.2.1, read 27 November 2026): Windows 11 and Python 3.12
only; graphics driver 26.2.2 or newer; "No ML training support" is listed as a limitation, so training on AMD is a
test; Smart App Control and Windows Defender Application Guard should be off; torch.distributed is not available.

Only the Python standard library is needed for --check (it runs before the training tools are installed).
"""

import os
import re
import subprocess
import sys

NO_WINDOW = 0x08000000 if os.name == "nt" else 0       # CREATE_NO_WINDOW: no console flashes up

AMD_VENDOR, NVIDIA_VENDOR = "1002", "10DE"             # PCI vendor numbers, in Windows' PNPDeviceID

# The chips AMD's ROCm 7.2.1 PyTorch wheels for Windows are built and supported for (AMD's Windows support
# matrices for Radeon and for Ryzen, rocm.docs.amd.com/projects/radeon-ryzen, read 27 November 2026).
SUPPORTED_ARCHS = {
    "gfx1100": "Radeon RX 7900 series, Radeon PRO W7900 / W7800",
    "gfx1101": "Radeon RX 7800 / 7700 series, Radeon PRO W7700",
    "gfx1200": "Radeon RX 9060 XT",
    "gfx1201": "Radeon RX 9070 series, Radeon AI PRO R9700",
    "gfx1150": "Ryzen AI 300 and 400 series built-in graphics (Radeon 890M / 880M)",
    "gfx1151": "Ryzen AI Max series built-in graphics (Radeon 8060S / 8050S / 8040S)",
}
AMD_RELEASE = "ROCm 7.2.1 for Windows (PyTorch 2.9.1)"
AMD_DRIVER = "26.2.2"

# Card names (as Windows says them) -> chip. First match wins. "assumed" marks a name that is not yet on AMD's own
# list, whose chip is assumed from its family; the training checks the real chip (gcnArchName) before it starts.
NAME_TABLE = [
    (r"\b80[4-6]5S\b", "gfx1151", True),       # Radeon 8065S and similar (newer Ryzen AI Max PRO): assumed family
    (r"\b80[4-6]0S\b", "gfx1151", False),      # Radeon 8060S / 8050S / 8040S (Ryzen AI Max 300)
    (r"\b(890M|880M)\b", "gfx1150", False),    # Ryzen AI 9 HX 370 / 375 / 470 / 475, Ryzen AI 9 365 / 465
    (r"\b(860M|840M|820M)\b", "gfx1152", False),   # Ryzen AI 5 / 7 300 (not supported by AMD's wheels)
    (r"\bR9700\b", "gfx1201", False),
    (r"\bRX\s*9070\b", "gfx1201", False),
    (r"\bRX\s*9060\b", "gfx1200", False),
    (r"\bRX\s*7900\b", "gfx1100", False),
    (r"\bW7[89]00\b", "gfx1100", False),
    (r"\bRX\s*7[78]00\b", "gfx1101", False),
    (r"\bW7700\b", "gfx1101", False),
    (r"\bRX\s*7600\b", "gfx1102", False),      # not supported
    (r"\bW7[56]00\b", "gfx1102", False),       # not supported
    (r"\bRX\s*6\d{3}", "gfx103x", False),      # RX 6000 series: not supported
    (r"\bRX\s*5\d{3}", "gfx101x", False),      # RX 5000 series: not supported
    (r"\b(Vega|RX\s*[45]\d0|R[579]\s)", "older", False),
]

NVIDIA_STOP = ("STOPPED: no NVIDIA graphics card driver was found. The kit needs an NVIDIA card with at least 12 GB "
               "of memory and its driver from nvidia.com. If this computer has an AMD or Intel graphics card instead, "
               "tell Claude its name.")


# ----------------------------------------------------------------- before installing: Windows' list of cards

def video_controllers(runner=None):
    """[(name, vendor number)] of the graphics adapters Windows lists (WMI Win32_VideoController); [] when they
    cannot be read. runner(command) -> text is for the tests."""
    command = ["powershell", "-NoProfile", "-Command",
               "Get-CimInstance Win32_VideoController | ForEach-Object { \"$($_.Name)|$($_.PNPDeviceID)\" }"]
    try:
        if runner:
            out = runner(command)
        else:
            out = subprocess.run(command, capture_output=True, text=True, timeout=60,
                                 creationflags=NO_WINDOW).stdout
    except Exception:  # noqa: BLE001 - not Windows, or PowerShell missing: no list
        return []
    cards = []
    for line in (out or "").splitlines():
        name, _, pnp = line.strip().partition("|")
        if not name:
            continue
        match = re.search(r"VEN_([0-9A-Fa-f]{4})", pnp)
        vendor = match.group(1).upper() if match else ""
        if not vendor and re.search(r"\b(AMD|Radeon)\b", name, re.I):
            vendor = AMD_VENDOR
        cards.append((name.strip(), vendor))
    return cards


def classify_amd(name):
    """(chip, supported, assumed) for an AMD card's name: chip like "gfx1151" or None when the name is not known;
    supported: AMD's Windows wheels are made for that chip; assumed: the chip is guessed from the card's family."""
    for pattern, arch, assumed in NAME_TABLE:
        if re.search(pattern, name, re.I):
            return arch, arch in SUPPORTED_ARCHS, assumed
    return None, False, False


def amd_choice(cards):
    """The kit's decision before installing, from Windows' list of cards: (code, card name or "", [plain lines]).
    code: "supported", "unknown", "unsupported" or "none" (no AMD card)."""
    amd = [name for name, vendor in cards if vendor == AMD_VENDOR]
    if not amd:
        return "none", "", []
    found = []
    for name in amd:
        arch, supported, assumed = classify_amd(name)
        found.append((0 if supported else 1 if arch is None else 2, name, arch, assumed))
    found.sort(key=lambda f: f[0])                     # a supported card first, then an unknown one
    rank, name, arch, assumed = found[0]
    if rank == 0:
        lines = [f"No NVIDIA card was found, but an AMD graphics card was: {name} (chip {arch}, "
                 f"{SUPPORTED_ARCHS[arch]}).",
                 f"Training on AMD graphics is new and being tested. The kit uses AMD's own PyTorch, {AMD_RELEASE}; "
                 f"it needs AMD's graphics driver {AMD_DRIVER} or newer (from amd.com)."]
        if assumed:
            lines.append(f"This card is not on AMD's list yet; its chip is assumed to be {arch} from its family. The "
                         "training checks the real chip before it starts.")
        return "supported", name, lines
    if rank == 1:
        return "unknown", name, [
            f"No NVIDIA card was found, but an AMD graphics card was: {name}. The kit does not know whether AMD's "
            f"PyTorch for Windows ({AMD_RELEASE}) works with it.",
            "AMD's list: " + "; ".join(SUPPORTED_ARCHS.values()) + ".",
            "Tell Claude the card's name. To try anyway, start the kit from a console window after typing: "
            "set KIT_AMD_TRY=1"]
    return "unsupported", name, [
        f"STOPPED: this computer has an AMD graphics card ({name}, chip {arch}), but AMD's PyTorch for Windows "
        f"({AMD_RELEASE}) does not support it, so the kit cannot train on it.",
        "AMD's list: " + "; ".join(SUPPORTED_ARCHS.values()) + ".",
        "The kit trains on an NVIDIA card with at least 12 GB of memory, or on one of the AMD graphics above."]


def check(runner=None, environ=None):
    """--check: say the decision and return the exit code (0 supported, 2 no AMD card, 3 unsupported, 4 unknown;
    4 becomes 0 when KIT_AMD_TRY=1)."""
    environ = os.environ if environ is None else environ
    code, _name, lines = amd_choice(video_controllers(runner))
    if code == "none":
        print(NVIDIA_STOP)
        return 2
    for line in lines:
        print(line)
    if code == "unknown" and environ.get("KIT_AMD_TRY") == "1":
        print("KIT_AMD_TRY=1 is set: trying AMD's PyTorch anyway.")
        return 0
    return {"supported": 0, "unknown": 4, "unsupported": 3}[code]


def requirements_file(kit, cards=None, nvidia=True):
    """The kit's requirements file for this computer: requirements.txt whenever an NVIDIA driver is there (nvidia:
    the caller found nvidia-smi), requirements-amd.txt only for an AMD card AMD's wheels support (or an unknown one
    with KIT_AMD_TRY=1), else requirements.txt as before (the training then stops with its usual message)."""
    normal = os.path.join(kit, "kit", "requirements.txt")
    if nvidia:
        return normal
    code, _name, _lines = amd_choice(video_controllers() if cards is None else cards)
    if code == "supported" or (code == "unknown" and os.environ.get("KIT_AMD_TRY") == "1"):
        return os.path.join(kit, "kit", "requirements-amd.txt")
    return normal


# ----------------------------------------------------------------- during training: what PyTorch sees

def is_rocm(torch):
    """True for AMD's PyTorch (ROCm/HIP), which answers through torch.cuda."""
    return bool(getattr(getattr(torch, "version", None), "hip", None))


def bf16_works(torch):
    """True when the card computes in bf16: PyTorch says so and a small bf16 sum on the card gives the right
    answer."""
    try:
        if not torch.cuda.is_bf16_supported():
            return False
        a = torch.ones((16, 16), device="cuda", dtype=torch.bfloat16)
        return float((a @ a).float().mean()) == 16.0
    except Exception:  # noqa: BLE001 - any failure: not bf16
        return False


def conservative_memory_gb(total_gb, free_gb=None, system_gb=None, integrated=False):
    """The memory (GB) the kit plans with. A separate card: what PyTorch reports. Built-in graphics that share the
    computer's memory (integrated): the smallest of the reported budget, what is free on it now, and three quarters
    of the computer's memory, so Windows and the picture preparation keep room."""
    if not integrated:
        return total_gb
    choices = [total_gb] + [x for x in (free_gb, None if system_gb is None else system_gb * 0.75) if x]
    return min(choices)


class Device:
    """What the kit trains on: name, backend ("cuda", "rocm" or "cpu"), chip (gfx... on AMD), memory_gb (planned
    with), reported_gb, integrated, dtype (torch dtype to compute in), use_bitsandbytes, reasons ([plain lines])."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def torch_device(torch=None, system_gb=None):
    """The card PyTorch sees, as a Device, or None when PyTorch sees no card. For NVIDIA it says what the kit has
    always done (bf16, bitsandbytes); for AMD it makes the substitutions in the module docstring."""
    if torch is None:
        import torch
    if not torch.cuda.is_available():
        return None
    props = torch.cuda.get_device_properties(0)
    reported = props.total_memory / 1024 ** 3
    if not is_rocm(torch):
        return Device(name=props.name, backend="cuda", chip="", memory_gb=reported, reported_gb=reported,
                      integrated=False, dtype=torch.bfloat16, use_bitsandbytes=True,
                      reasons=[f"NVIDIA card, CUDA {torch.version.cuda}: bf16 and bitsandbytes as usual."])
    chip = (getattr(props, "gcnArchName", "") or "").split(":")[0]
    integrated = bool(getattr(props, "is_integrated", False))
    free_gb = None
    try:
        free_gb = torch.cuda.mem_get_info(0)[0] / 1024 ** 3
    except Exception:  # noqa: BLE001 - not every build answers
        pass
    if system_gb is None:
        try:
            import psutil
            system_gb = psutil.virtual_memory().total / 1024 ** 3
        except Exception:  # noqa: BLE001 - no psutil: planned without it
            system_gb = None
    memory = conservative_memory_gb(reported, free_gb, system_gb, integrated)
    bf16 = bf16_works(torch)
    reasons = [f"AMD graphics, {AMD_RELEASE} (HIP {torch.version.hip}), chip {chip or 'unknown'}: new, being tested."]
    if integrated:
        reasons.append(f"Built-in graphics sharing the computer's memory: Windows reports {reported:.0f} GB for it; "
                       f"the kit plans with {memory:.0f} GB (the smallest of that, the free part"
                       + (f" {free_gb:.0f} GB" if free_gb else "")
                       + (f" and three quarters of the computer's {system_gb:.0f} GB" if system_gb else "") + ").")
    reasons.append("Numbers: bf16 (the chip has it)." if bf16 else
                   "Numbers: fp16 with a gradient scaler (bf16 did not work on this chip).")
    reasons.append("bitsandbytes (8-bit AdamW, 4-bit models) works only on NVIDIA: ordinary AdamW and 16-bit models "
                   "are used instead, which need more memory.")
    reasons.append("Attention: PyTorch's own (SDPA); flash-attention and torch.compile are not used.")
    return Device(name=props.name, backend="rocm", chip=chip, memory_gb=memory, reported_gb=reported,
                  integrated=integrated, dtype=torch.bfloat16 if bf16 else torch.float16, use_bitsandbytes=False,
                  reasons=reasons)


def chip_problem(device):
    """A plain STOPPED reason when an AMD card's chip is not one AMD's wheels support, else None."""
    if device is None or device.backend != "rocm" or not device.chip or device.chip in SUPPORTED_ARCHS:
        return None
    return (f"The AMD graphics {device.name} has chip {device.chip}, which AMD's PyTorch for Windows ({AMD_RELEASE}) "
            "does not support. AMD's list: " + "; ".join(SUPPORTED_ARCHS.values()) + ".")


def smoke_test(torch, device):
    """None when a small sum on the card works, else the error in one line (AMD: wrong driver, a chip without
    kernels, Smart App Control blocking the libraries ...)."""
    try:
        a = torch.ones((64, 64), device="cuda", dtype=device.dtype)
        (a @ a).float().sum().item()
        return None
    except Exception as e:  # noqa: BLE001 - said by the caller
        return (str(e).splitlines() or [type(e).__name__])[0][:300]


def report_lines(device):
    """Plain lines for the log: which card, which backend and why."""
    if device is None:
        return ["Graphics: none that PyTorch can use."]
    kind = {"cuda": "NVIDIA (CUDA)", "rocm": "AMD (ROCm)"}.get(device.backend, device.backend)
    return [f"Graphics: {device.name}, {kind}, {device.memory_gb:.0f} GB of memory planned with."] + \
        ["  " + r for r in device.reasons]


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        sys.exit(check())
    print(__doc__)
