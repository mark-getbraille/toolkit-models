"""The picture-making add-on's folder for Accessible AI Studio (kit/train_pictures.py package): laid out exactly as
that program's own "Train add-ons" lays out an add-on it trained (models\\trained-<slug>\\ with
pytorch_lora_weights.safetensors, trained.json and .complete; its app/training.py register() and slug())."""

import json
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit"))


@pytest.fixture
def tp():
    """kit/train_pictures.py (skipped where its imports are missing)."""
    try:
        import train_pictures
    except ImportError as e:
        pytest.skip(f"train_pictures cannot be imported here: {e}")
    return train_pictures


def test_the_folder_name_is_the_studio_s_own(tp):
    # Accessible AI Studio: re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "add-on"
    assert tp.studio_slug("picture-making-sdxl-normal") == "picture-making-sdxl-normal"
    assert tp.studio_slug("Picture making SDXL (full) #2") == "picture-making-sdxl-full-2"
    assert tp.studio_slug("!!!") == "add-on"
    assert len(tp.studio_slug("x" * 90)) == 40


def test_the_zip_carries_the_studio_folder(tp, tmp_path, monkeypatch):
    final, run_dir = tmp_path / "final", tmp_path / "run"
    final.mkdir()
    (final / "picture-making-sdxl-normal.safetensors").write_bytes(b"kohya")
    (final / "pytorch_lora_weights.safetensors").write_bytes(b"diffusers form")
    for part in ("test-before", "test-after"):
        (run_dir / part).mkdir(parents=True)
        (run_dir / part / "01.png").write_bytes(b"png")
    (run_dir / "captions.txt").write_text("A red bicycle.\n")
    report = tmp_path / "REPORT.txt"
    report.write_text("report")
    monkeypatch.setattr(tp, "HERE", str(tmp_path))
    monkeypatch.setattr(tp, "attribution_text", lambda info: "credits")
    info = {"key": "sdxl", "base_name": "Stable Diffusion XL base 1.0", "repo": "stabilityai/stable-diffusion-xl-base-1.0",
            "revision": "abc", "licence": "CreativeML Open RAIL++-M", "share_alike": False, "own": 0,
            "collections": {}, "captions": []}
    monkeypatch.setattr(tp, "personal_lines", lambda info: [])
    path = tp.package(str(run_dir), str(final), "picture-making-sdxl-normal", info, str(report))
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        folder = "Accessible AI Studio/trained-picture-making-sdxl-normal/"
        assert {folder + "pytorch_lora_weights.safetensors", folder + "trained.json", folder + ".complete",
                "Accessible AI Studio/HOW TO USE IN ACCESSIBLE AI STUDIO.txt"} <= names
        assert z.read(folder + "pytorch_lora_weights.safetensors") == b"diffusers form"
        trained = json.loads(z.read(folder + "trained.json"))
    # The fields Accessible AI Studio's register() writes, with its values for this add-on.
    assert trained["name"] == "picture-making-sdxl-normal" and trained["family"] == "sdxl"
    assert trained["trigger"] == "" and trained["kind"] in ("character", "style", "object")
    assert trained["trained_on_real"] is True        # real photographs: the studio's second content rule applies
