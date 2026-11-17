"""Tests of kit/system_monitor.py: the computer-use lines, warnings and spreadsheet, with a stand-in for NVIDIA's
tool (nvidia-smi), so they run on any computer."""

import csv
import os
import sys
import time

import pytest

pytest.importorskip("psutil")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))
import system_monitor  # noqa: E402

FAKE_SMI = """import sys
args = " ".join(sys.argv[1:])
if "name,driver_version" in args:
    print("NVIDIA GeForce RTX 5060 Ti, 581.42, 16311, 180.00, 200.00, 5, 8")
else:
    print("97, 41, 14210, 16311, 84, 171.5, 180.00, 2805, 14001, 55, 4, 8, 0x0000000000000044")
"""


@pytest.fixture
def fake_smi(tmp_path, monkeypatch):
    """A stand-in nvidia-smi that answers like a busy, hot RTX 5060 Ti slowed by its power limit and heat."""
    script = tmp_path / "fake_smi.py"
    script.write_text(FAKE_SMI)
    if os.name == "nt":
        tool = tmp_path / "nvidia-smi.cmd"
        tool.write_text(f'@"{sys.executable}" "{script}" %*\n')
    else:
        tool = tmp_path / "nvidia-smi"
        tool.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{script}" "$@"\n')
        tool.chmod(0o755)
    monkeypatch.setattr(system_monitor, "nvidia_smi", lambda: str(tool))
    return str(tool)


def test_the_graphics_card_reading_and_its_slowdown_in_plain_words(fake_smi):
    row = system_monitor.gpu_sample(fake_smi)
    assert row["gpu_pct"] == 97 and row["gpu_temp_c"] == 84 and row["vram_used_mb"] == 14210
    assert system_monitor.slowdown_words(row["gpu_slowdown"]) == "the power limit, heat (hardware)"
    assert system_monitor.slowdown_words(0x1) == ""          # idle is not a slowdown


def test_the_monitor_writes_the_computer_its_use_warnings_and_a_spreadsheet(fake_smi, tmp_path, monkeypatch):
    monkeypatch.setenv("KIT_LOG_FOLDER", str(tmp_path / "logs"))
    lines = []
    monitor = system_monitor.Monitor(lines.append, sample_every=0.3, report_every=0.9)
    monitor.begin()
    monitor.phase = "Step 5 of 7: training on 77006 pictures."
    time.sleep(2.5)
    monitor.end()
    text = "\n".join(lines)
    assert "Computer: graphics card NVIDIA GeForce RTX 5060 Ti, driver 581.42, 16 GB of memory" in text
    assert "Computer: processor" in text and "Computer: memory" in text
    use = [line for line in lines if line.startswith("Computer use (last")]
    assert use, text
    assert "Step 5 of 7" in use[-1] and "graphics card 97% busy" in use[-1] and "84 °C" in use[-1]
    assert "slowed at times by heat (hardware) and the power limit" in use[-1]
    assert "processor" in use[-1] and "memory" in use[-1] and "disks reading" in use[-1]
    warnings = [line for line in lines if line.startswith("Computer use warning")]
    assert any("84 °C" in w for w in warnings) and any("heat" in w for w in warnings)
    assert len(warnings) == len({w for w in warnings})        # each kind once, not every sample
    sheets = os.listdir(tmp_path / "logs")
    assert len(sheets) == 1 and sheets[0].startswith("Picture Model Training computer use ")
    with open(tmp_path / "logs" / sheets[0], encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 3 and rows[0]["gpu_pct"] == "97.0" and rows[0]["phase"].startswith("Step 5 of 7")
    assert rows[-1]["cpu_pct"] != "" and rows[-1]["ram_total_gb"] != ""


def test_without_nvidia_the_monitor_says_so_and_carries_on(monkeypatch, tmp_path):
    monkeypatch.setenv("KIT_LOG_FOLDER", str(tmp_path))
    monkeypatch.setattr(system_monitor, "nvidia_smi", lambda: None)
    lines = []
    monitor = system_monitor.Monitor(lines.append, sample_every=0.3, report_every=0.6)
    monitor.begin()
    time.sleep(1.2)
    monitor.end()
    assert any("nvidia-smi) was not found" in line for line in lines)
    assert any(line.startswith("Computer use (last") and "processor" in line for line in lines)


def test_the_timer_says_where_the_time_went():
    timer = system_monitor.Timer()
    timer.add("preparing pictures (processor)", 0.0)
    time.sleep(0.2)
    timer.add("graphics card work", 0.15)
    line = timer.line(200)
    assert line.startswith("Computer use (the last 200 pictures):") and "graphics card work" in line


def test_the_phase_comes_from_the_programs_lines():
    system_monitor._monitor = system_monitor.Monitor(lambda line: None)
    try:
        system_monitor.note("Step 3 of 7: downloading the described pictures of each collection.")
        assert system_monitor._monitor.phase.startswith("Step 3 of 7")
        system_monitor.note("    1000 pictures done")
        assert system_monitor._monitor.phase.startswith("Step 3 of 7")
    finally:
        system_monitor._monitor = None


def test_the_programs_keep_computer_lines_out_of_status_and_speech():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wizard"))
    pytest.importorskip("wx")
    import training_wizard
    assert training_wizard.is_computer_line("Computer use (last 5 minutes): ...")
    assert training_wizard.is_computer_line("  Computer use (the last 200 pictures): 1.16 seconds each")
    assert not training_wizard.is_computer_line("Step 5 of 7: training on 77006 pictures.")
