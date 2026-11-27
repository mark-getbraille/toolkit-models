"""Tests of the AMD graphics choice (new, being tested): kit/gpu_backend.py, its use in kit/train.py, the AMD list
of packages and the start files. Everything uses stand-ins (a made-up Windows card list, a made-up PyTorch), so it
runs on any computer without a graphics card; the tests that run a real (tiny) training step need PyTorch and are
skipped without it. They also check that the NVIDIA way stays exactly as it was."""

import os
import re
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "kit")
sys.path.insert(0, KIT)
import gpu_backend  # noqa: E402


# ----------------------------------------------------------------- Windows' list of cards (before installing)

def fake_wmi(*cards):
    """A stand-in for PowerShell's answer: one "name|PNPDeviceID" line per card."""
    return lambda command: "\n".join(cards) + "\n"


NVIDIA_CARD = r"NVIDIA GeForce RTX 5060 Ti|PCI\VEN_10DE&DEV_2D04&SUBSYS_12345678&REV_A1\4&1"
INTEL_CARD = r"Intel(R) UHD Graphics 770|PCI\VEN_8086&DEV_4680&SUBSYS_00000000&REV_0C\3&1"
HALO_CARD = r"AMD Radeon(TM) 8060S Graphics|PCI\VEN_1002&DEV_1586&SUBSYS_00000000&REV_C1\3&1"
NEW_HALO_CARD = r"AMD Radeon(TM) 8065S Graphics|PCI\VEN_1002&DEV_1586&SUBSYS_00000000&REV_D1\3&1"
XTX_CARD = r"AMD Radeon RX 7900 XTX|PCI\VEN_1002&DEV_744C&SUBSYS_00000000&REV_C8\4&1"
OLD_CARD = r"AMD Radeon RX 6800 XT|PCI\VEN_1002&DEV_73BF&SUBSYS_00000000&REV_C1\4&1"
GENERIC_CARD = r"AMD Radeon(TM) Graphics|PCI\VEN_1002&DEV_164E&SUBSYS_00000000&REV_C1\3&1"


def test_video_controllers_reads_names_and_vendors():
    cards = gpu_backend.video_controllers(fake_wmi(NVIDIA_CARD, HALO_CARD, "", "Some Radeon card|"))
    assert cards == [("NVIDIA GeForce RTX 5060 Ti", "10DE"), ("AMD Radeon(TM) 8060S Graphics", "1002"),
                     ("Some Radeon card", "1002")]


def test_video_controllers_survives_no_powershell():
    def broken(command):
        raise FileNotFoundError("powershell")
    assert gpu_backend.video_controllers(broken) == []


@pytest.mark.parametrize("name, chip, supported, assumed", [
    ("AMD Radeon(TM) 8060S Graphics", "gfx1151", True, False),
    ("AMD Radeon(TM) 8050S Graphics", "gfx1151", True, False),
    ("AMD Radeon(TM) 8065S Graphics", "gfx1151", True, True),         # the PRO 495's graphics: assumed family
    ("AMD Radeon(TM) 890M Graphics", "gfx1150", True, False),
    ("AMD Radeon(TM) 860M Graphics", "gfx1152", False, False),
    ("AMD Radeon RX 9070 XT", "gfx1201", True, False),
    ("AMD Radeon AI PRO R9700", "gfx1201", True, False),
    ("AMD Radeon RX 9060 XT", "gfx1200", True, False),
    ("AMD Radeon RX 7900 XTX", "gfx1100", True, False),
    ("AMD Radeon PRO W7900", "gfx1100", True, False),
    ("AMD Radeon RX 7800 XT", "gfx1101", True, False),
    ("AMD Radeon RX 7600", "gfx1102", False, False),
    ("AMD Radeon RX 6800 XT", "gfx103x", False, False),
    ("AMD Radeon(TM) Graphics", None, False, False),
])
def test_card_names_map_to_chips(name, chip, supported, assumed):
    assert gpu_backend.classify_amd(name) == (chip, supported, assumed)


def test_no_amd_card_means_the_usual_nvidia_message(capsys):
    assert gpu_backend.amd_choice([("Intel(R) UHD Graphics 770", "8086")])[0] == "none"
    assert gpu_backend.check(fake_wmi(INTEL_CARD), environ={}) == 2
    assert capsys.readouterr().out.strip() == gpu_backend.NVIDIA_STOP
    assert gpu_backend.check(fake_wmi(), environ={}) == 2           # nothing listed at all


def test_a_supported_amd_card_is_chosen_and_explained(capsys):
    assert gpu_backend.check(fake_wmi(INTEL_CARD, HALO_CARD), environ={}) == 0
    out = capsys.readouterr().out
    assert "AMD Radeon(TM) 8060S Graphics (chip gfx1151" in out and "new and being tested" in out
    assert gpu_backend.AMD_DRIVER in out


def test_the_newer_ryzen_ai_max_is_tried_and_said_to_be_assumed(capsys):
    assert gpu_backend.check(fake_wmi(NEW_HALO_CARD), environ={}) == 0
    assert "not on AMD's list yet" in capsys.readouterr().out


def test_the_supported_card_wins_over_built_in_graphics():
    code, name, _ = gpu_backend.amd_choice([("AMD Radeon(TM) Graphics", "1002"), ("AMD Radeon RX 7900 XTX", "1002")])
    assert (code, name) == ("supported", "AMD Radeon RX 7900 XTX")


def test_an_unsupported_amd_card_stops_plainly(capsys):
    assert gpu_backend.check(fake_wmi(OLD_CARD), environ={}) == 3
    out = capsys.readouterr().out
    assert out.startswith("STOPPED:") and "RX 6800 XT" in out and "does not support it" in out


def test_an_unknown_amd_card_can_be_tried_on_request(capsys):
    assert gpu_backend.check(fake_wmi(GENERIC_CARD), environ={}) == 4
    assert "KIT_AMD_TRY=1" in capsys.readouterr().out
    assert gpu_backend.check(fake_wmi(GENERIC_CARD), environ={"KIT_AMD_TRY": "1"}) == 0


def test_requirements_file_keeps_nvidia_on_its_own_list(tmp_path):
    kit = str(tmp_path)
    amd = [("AMD Radeon RX 7900 XTX", "1002")]
    assert gpu_backend.requirements_file(kit, amd, nvidia=True).endswith(os.path.join("kit", "requirements.txt"))
    assert gpu_backend.requirements_file(kit, amd, nvidia=False).endswith("requirements-amd.txt")
    assert gpu_backend.requirements_file(kit, [("AMD Radeon RX 6800", "1002")], nvidia=False).endswith(
        os.path.join("kit", "requirements.txt"))
    assert gpu_backend.requirements_file(kit, [], nvidia=False).endswith(os.path.join("kit", "requirements.txt"))


# ----------------------------------------------------------------- during training (a made-up PyTorch)

class FakeProps:
    def __init__(self, name, gb, arch="", integrated=False):
        self.name, self.total_memory, self.gcnArchName = name, int(gb * 1024 ** 3), arch
        self.is_integrated = integrated


def fake_torch(name="AMD Radeon(TM) 8065S Graphics", gb=144, arch="gfx1151:sramecc-:xnack-", integrated=True,
               hip="7.2.53211", bf16=True, free_gb=140, available=True):
    """A stand-in for PyTorch: AMD's ROCm build when hip is set, NVIDIA's CUDA build when hip is None."""
    torch = types.SimpleNamespace(bfloat16="torch.bfloat16", float16="torch.float16", float32="torch.float32")
    torch.version = types.SimpleNamespace(hip=hip, cuda=None if hip else "12.8")

    class Matrix:
        def __matmul__(self, other):
            return self

        def float(self):
            return self

        def mean(self):
            return 16.0

        def sum(self):
            return self

        def item(self):
            return 0.0

    torch.ones = lambda shape, device=None, dtype=None: Matrix()
    torch.cuda = types.SimpleNamespace(
        is_available=lambda: available, get_device_properties=lambda i: FakeProps(name, gb, arch, integrated),
        is_bf16_supported=lambda: bf16, mem_get_info=lambda i: (int(free_gb * 1024 ** 3), int(gb * 1024 ** 3)))
    return torch


def test_nvidia_device_is_what_the_kit_always_did():
    device = gpu_backend.torch_device(fake_torch(name="NVIDIA GeForce RTX 5060 Ti", gb=16, hip=None,
                                                 integrated=False))
    assert (device.backend, device.dtype, device.use_bitsandbytes) == ("cuda", "torch.bfloat16", True)
    assert round(device.memory_gb) == 16
    assert gpu_backend.chip_problem(device) is None


def test_rocm_uses_the_cuda_api_and_substitutes_nvidia_only_parts():
    torch = fake_torch()
    assert gpu_backend.is_rocm(torch)
    device = gpu_backend.torch_device(torch, system_gb=192)
    assert (device.backend, device.chip, device.use_bitsandbytes) == ("rocm", "gfx1151", False)
    assert device.dtype == "torch.bfloat16"
    lines = gpu_backend.report_lines(device)
    assert "AMD (ROCm)" in lines[0]
    assert any("ordinary AdamW" in line for line in lines) and any("SDPA" in line for line in lines)


def test_shared_memory_is_planned_conservatively():
    # A 192 GB Ryzen AI Max whose graphics report 144 GB (dedicated and shared), with 140 GB free on it now.
    device = gpu_backend.torch_device(fake_torch(gb=144, free_gb=140), system_gb=192)
    assert round(device.memory_gb) == 140
    device = gpu_backend.torch_device(fake_torch(gb=180, free_gb=178), system_gb=192)
    assert round(device.memory_gb) == 144                                  # three quarters of 192
    assert gpu_backend.conservative_memory_gb(24, 23, 64, integrated=False) == 24      # a separate card
    assert any("plans with 144 GB" in r for r in device.reasons)


def test_fp16_when_bf16_does_not_work():
    device = gpu_backend.torch_device(fake_torch(bf16=False), system_gb=192)
    assert device.dtype == "torch.float16"
    assert any("fp16 with a gradient scaler" in r for r in device.reasons)


def test_an_unsupported_chip_seen_by_pytorch_is_stopped():
    device = gpu_backend.torch_device(fake_torch(name="AMD Radeon RX 6800 XT", arch="gfx1030", integrated=False,
                                                 gb=16), system_gb=64)
    assert "gfx1030" in gpu_backend.chip_problem(device)


def test_no_card_seen_by_pytorch():
    assert gpu_backend.torch_device(fake_torch(available=False)) is None
    assert gpu_backend.report_lines(None) == ["Graphics: none that PyTorch can use."]


def test_train_check_computer_on_amd(monkeypatch, tmp_path):
    """train.py's step 1 on a made-up 192 GB Ryzen AI Max: says the backend and why, and uses the AMD memory need."""
    import train
    torch = fake_torch(gb=144, free_gb=140)
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setattr(train, "LOG", str(tmp_path / "log.txt"))
    monkeypatch.setattr(train, "CARD", [gpu_backend.torch_device(torch, system_gb=192)])
    name, memory = train.check_computer("8b", str(tmp_path), free_needed=0)
    log = (tmp_path / "log.txt").read_text(encoding="utf-8")
    assert name == "AMD Radeon(TM) 8065S Graphics" and memory <= 144
    assert "AMD (ROCm)" in log and "ordinary AdamW" in log


def test_train_check_computer_stops_on_a_small_amd_card(monkeypatch, tmp_path):
    import train
    monkeypatch.setitem(sys.modules, "torch", fake_torch(name="AMD Radeon RX 7800 XT", gb=16, arch="gfx1101",
                                                          integrated=False))
    monkeypatch.setattr(train, "LOG", str(tmp_path / "log.txt"))
    monkeypatch.setattr(train, "CARD", [])
    with pytest.raises(SystemExit):
        train.check_computer("4b", str(tmp_path), free_needed=0)
    assert f"at least {train.AMD_MEMORY_NEEDED['4b']} GB" in (tmp_path / "log.txt").read_text(encoding="utf-8")


def test_train_says_when_amd_pytorch_cannot_use_the_card(monkeypatch, tmp_path):
    import train
    monkeypatch.setitem(sys.modules, "torch", fake_torch(available=False))
    monkeypatch.setattr(train, "LOG", str(tmp_path / "log.txt"))
    with pytest.raises(SystemExit):
        train.check_computer("4b", str(tmp_path), free_needed=0)
    assert "Smart App Control" in (tmp_path / "log.txt").read_text(encoding="utf-8")


# ----------------------------------------------------------------- the optimiser (a real, tiny training)

def tiny_training(monkeypatch, tmp_path, amd):
    """Run train.train() for 2 pictures on a tiny real PyTorch model on the processor, with a stand-in bitsandbytes
    that records whether it was used; returns the names of the optimisers made."""
    torch = pytest.importorskip("torch")
    import train
    made = []

    class Paged(torch.optim.AdamW):
        def __init__(self, *a, **k):
            made.append("PagedAdamW8bit")
            super().__init__(*a, **k)
    monkeypatch.setitem(sys.modules, "bitsandbytes", types.SimpleNamespace(optim=types.SimpleNamespace(
        PagedAdamW8bit=Paged)))
    real_adamw = torch.optim.AdamW

    class Plain(real_adamw):
        def __init__(self, *a, **k):
            made.append("AdamW")
            super().__init__(*a, **k)
    monkeypatch.setattr(torch.optim, "AdamW", Plain)

    class Tiny(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layer = torch.nn.Linear(4, 1)

        def forward(self, x):
            return types.SimpleNamespace(loss=self.layer(x).pow(2).mean())

        def save_pretrained(self, folder):
            os.makedirs(folder, exist_ok=True)
    monkeypatch.setattr(train, "encode", lambda processor, row, device: {"x": torch.ones(1, 4)})
    monkeypatch.setattr(train, "LOG", str(tmp_path / "log.txt"))
    monkeypatch.setattr(train, "on_amd", lambda: amd)
    monkeypatch.setattr(train, "card", lambda: gpu_backend.Device(dtype=torch.bfloat16))
    train.train(Tiny(), None, [{"picture": "a"}, {"picture": "b"}], str(tmp_path / "adapter"), "cpu", accumulate=2)
    return made


def test_nvidia_training_still_uses_8bit_adamw(monkeypatch, tmp_path):
    assert tiny_training(monkeypatch, tmp_path, amd=False) == ["PagedAdamW8bit"]


def test_amd_training_uses_plain_adamw_and_never_bitsandbytes(monkeypatch, tmp_path):
    assert tiny_training(monkeypatch, tmp_path, amd=True) == ["AdamW"]


# ----------------------------------------------------------------- the package lists and the start files

def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as f:
        return f.read()


def pins(text):
    """{name: line} of a requirements text, without comments."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out[re.split(r"[=@\[ ]", line, maxsplit=1)[0].strip()] = line
    return out


def test_nvidia_requirements_are_unchanged():
    normal = pins(read("kit", "requirements.txt"))
    assert normal["torch"] == "torch==2.9.1+cu128" and normal["torchvision"] == "torchvision==0.24.1+cu128"
    assert "bitsandbytes" in normal and not any("radeon" in line for line in normal.values())


def test_amd_requirements_are_pinned_with_checksums_from_amd():
    amd, normal = pins(read("kit", "requirements-amd.txt")), pins(read("kit", "requirements.txt"))
    for name in ("rocm", "rocm-sdk-core", "rocm-sdk-libraries-custom", "torch", "torchvision"):
        assert re.fullmatch(rf"{name}(\[libraries\])? @ https://repo\.radeon\.com/rocm/windows/rocm-rel-7\.2\.1/\S+ "
                            r"--hash=sha256:[0-9a-f]{64}", amd[name]), amd[name]
    assert "2.9.1%2Brocm7.2.1" in amd["torch"] and "0.24.1%2Brocm7.2.1" in amd["torchvision"]
    assert "bitsandbytes" not in amd
    # Every other package is pinned exactly as for NVIDIA.
    for name, line in normal.items():
        if name not in ("torch", "torchvision", "bitsandbytes"):
            assert amd[name] == line


def test_start_files_keep_the_nvidia_way_and_add_amd_after_it():
    for name, script in (("run.cmd", "train.py"), ("run_pictures.cmd", "train_pictures.py")):
        text = read("kit", name)
        assert "\r\n" in text
        assert ("-r kit\\requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128 "
                "--index-strategy unsafe-best-match --quiet") in text
        assert text.index("where nvidia-smi") < text.index("if not defined NVSMI goto :amd")
        amd = text[text.index("\r\n:amd\r\n"):]
        assert "call kit\\amd_setup.cmd" in amd and f"env\\Scripts\\python.exe kit\\{script} %*" in amd


def test_amd_setup_is_safe_cmd():
    text = read("kit", "amd_setup.cmd")
    assert text.count("\n") == text.count("\r\n")                     # Windows line ends
    assert "gpu_backend.py --check" in text and "-r kit\\requirements-amd.txt" in text
    assert "download.pytorch.org" not in text                          # never NVIDIA's PyTorch here
    assert "VEN_1002" in text
    run = read("kit", "run.cmd")
    assert re.search(r'set "UV_SHA256=([0-9a-f]{64})"', run)            # the helper's checksum comes from run.cmd
    # An echo inside a ( ... ) block must not contain brackets: cmd would end the block there.
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("echo") and depth > 0:
            assert "(" not in stripped and ")" not in stripped, line
        elif not stripped.lower().startswith(("rem", "powershell")):
            depth += stripped.count("(") - stripped.count(")")


# ----------------------------------------------------------------- the wizard

def wizard(monkeypatch, cards, nvidia=None):
    """The wizard module with a made-up NVIDIA tool (None: no NVIDIA driver) and a made-up Windows card list."""
    pytest.importorskip("wx")
    sys.path.insert(0, os.path.join(ROOT, "wizard"))
    import training_wizard
    monkeypatch.setattr(training_wizard, "nvidia_smi", lambda: nvidia)
    monkeypatch.setattr(gpu_backend, "video_controllers", lambda runner=None: cards)
    monkeypatch.setitem(sys.modules, "gpu_backend", gpu_backend)
    return training_wizard


def test_wizard_check_accepts_a_supported_amd_card(monkeypatch, tmp_path):
    w = wizard(monkeypatch, [("AMD Radeon(TM) 8065S Graphics", "1002")])
    lines, _ready = w.check_computer(str(tmp_path))
    assert any("8065S" in line for line in lines)
    assert not any(line.startswith("No NVIDIA graphics card driver") for line in lines)


def test_wizard_check_without_nvidia_or_supported_amd_says_what_it_always_said(monkeypatch, tmp_path):
    w = wizard(monkeypatch, [("AMD Radeon RX 6800 XT", "1002")])
    lines, ready = w.check_computer(str(tmp_path))
    assert not ready and lines[0] == ("No NVIDIA graphics card driver was found. The training needs an NVIDIA card "
                                      "with 12 GB or more.")
    w = wizard(monkeypatch, [])
    lines, ready = w.check_computer(str(tmp_path))
    assert not ready and lines[0].startswith("No NVIDIA graphics card driver") and "AMD" not in lines[1]


def test_wizard_installs_amd_packages_without_the_cuda_index(monkeypatch, tmp_path):
    w = wizard(monkeypatch, [])
    commands = []
    monkeypatch.setattr(w, "run_quiet", lambda command, cwd, env=None: commands.append(command))
    w.pip_install("uv", str(tmp_path), {}, os.path.join("kit", "requirements-amd.txt"))
    w.pip_install("uv", str(tmp_path), {}, os.path.join("kit", "requirements.txt"))
    assert w.TORCH_INDEX not in commands[0] and w.TORCH_INDEX in commands[1]
