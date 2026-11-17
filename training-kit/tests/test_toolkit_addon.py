"""Tests of kit/make_toolkit_addon.py: the toolkit version of the trained describer add-on in the result zip.

The cheap tests run anywhere (also on the GitHub Windows test job, which has no PyTorch): they use a small GGUF file
written here, a made-up result zip and made-up model settings, never a real model. The real conversion with
llama.cpp's converter (test_real_conversion) runs only where PyTorch, Transformers, PEFT and safetensors are
installed and LLAMA_SOURCE_ZIP names llama.cpp's source zip of release make_toolkit_addon.LLAMA_TAG; it is skipped
on GitHub."""

import ast
import json
import os
import struct
import sys
import zipfile

import pytest

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit")
sys.path.insert(0, KIT)
import make_toolkit_addon as mta  # noqa: E402

REPO_4B = "huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated"
REVISION_4B = "ce72a7c22aacb493fb94478de3bfbe834c61844a"
# A made-up Qwen3-VL with the real model's shape rules but tiny sizes: 2 layers; the attention's inner size
# (4 heads of 32) differs from the hidden size (64), as in the real 4B model.
CONFIG = {"architectures": ["Qwen3VLForConditionalGeneration"], "model_type": "qwen3_vl",
          "text_config": {"hidden_size": 64, "intermediate_size": 96, "num_hidden_layers": 2,
                          "num_attention_heads": 4, "num_key_value_heads": 2, "head_dim": 32}}
CONTRACT_KEYS = ["format", "kind", "base", "base_repo", "base_revision", "name", "run", "trained", "share_alike",
                 "personal_use", "content", "score_before", "score_after", "llama_cpp", "sha256", "size"]


def gguf_text(text):
    """A GGUF string: its length, then UTF-8."""
    data = text.encode("utf-8")
    return struct.pack("<Q", len(data)) + data


def write_gguf(path, settings, tensors):
    """Write a small GGUF file (version 3): settings {key: str or float}, tensors [(name, sizes, ggml type)] (the
    tensor data itself is left out: only the header is read by the checks)."""
    out = b"GGUF" + struct.pack("<IQQ", 3, len(tensors), len(settings))
    for key, value in settings.items():
        out += gguf_text(key)
        if isinstance(value, str):
            out += struct.pack("<I", 8) + gguf_text(value)
        else:
            out += struct.pack("<If", 6, float(value))
    for name, sizes, kind in tensors:
        out += gguf_text(name) + struct.pack("<I", len(sizes)) + b"".join(struct.pack("<Q", s) for s in sizes)
        out += struct.pack("<IQ", kind, 0)
    with open(path, "wb") as f:
        f.write(out)


def good_tensors(config=CONFIG, rank=16):
    """The tensors a correct add-on for config has: lora_a [in, rank] and lora_b [rank, out] of every part."""
    sizes = mta.expected_sizes(config)
    tensors = []
    for layer in range(config["text_config"]["num_hidden_layers"]):
        for part in mta.PARTS:
            tensors.append((f"blk.{layer}.{part}.weight.lora_a", [sizes[part][0], rank], mta.F16))
            tensors.append((f"blk.{layer}.{part}.weight.lora_b", [rank, sizes[part][1]], mta.F16))
    return tensors


GOOD_SETTINGS = {"general.architecture": "qwen3vl", "general.type": "adapter", "adapter.type": "lora",
                 "adapter.lora.alpha": 32.0}


def make_kit(tmp_path, run="4b-full", day="2026-11-16", info_extra=None, personal=False, with_addon=True):
    """A made-up kit folder: work/model-4b/config.json, the trained add-on folder of run (when with_addon) and a
    result zip as an older kit made it (scores.json without "run"); returns (kit folder, zip path)."""
    kit = tmp_path / "Picture Model Training Kit"
    (kit / "work" / "model-4b").mkdir(parents=True)
    (kit / "work" / "model-4b" / "config.json").write_text(json.dumps(CONFIG))
    if with_addon:
        final = kit / "work" / f"adapter-{run}" / "final"
        final.mkdir(parents=True)
        (final / "adapter_config.json").write_text(json.dumps({"r": 16, "lora_alpha": 32}))
        (final / "adapter_model.safetensors").write_bytes(b"made up")
    (kit / "result").mkdir()
    info = {"model": REPO_4B, "revision": REVISION_4B, "size": "full", "share_alike": False, "with_nudity": True,
            "with_medical": True, "with_graphic": False, "with_sexual": False, "own_pictures": 0,
            "before": {"all": 0.2}, "after": {"all": 0.25}, "settings": {"lora_r": 16, "lora_alpha": 32},
            **(info_extra or {})}
    path = kit / "result" / f"picture-training-{run}-{day}.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("adapter/adapter_config.json", "{}")
        z.writestr("report.txt", "the report")
        z.writestr("scores.json", json.dumps(info))
        z.writestr("ATTRIBUTION.txt", "credits")
        if personal:
            z.writestr(mta.PERSONAL_MARK, "personal use only")
    return kit, str(path)


def test_check_gguf_accepts_a_correct_addon(tmp_path):
    """A GGUF LoRA with every part of every layer at the right sizes passes."""
    path = tmp_path / "a.gguf"
    write_gguf(path, GOOD_SETTINGS, good_tensors())
    assert mta.check_gguf(str(path), CONFIG, 16, 32) == 2 * 7 * 2


@pytest.mark.parametrize("change, words", [
    (lambda s, t: (dict(s, **{"general.type": "model"}), t), "not a Qwen3-VL LoRA add-on"),
    (lambda s, t: (dict(s, **{"adapter.type": "control_vector"}), t), "not a Qwen3-VL LoRA add-on"),
    (lambda s, t: (dict(s, **{"general.architecture": "qwen3"}), t), "not a Qwen3-VL LoRA add-on"),
    (lambda s, t: (dict(s, **{"adapter.lora.alpha": 16.0}), t), "alpha"),
    (lambda s, t: (s, t + [("v.blk.0.attn_q.weight.lora_a", [64, 16], mta.F16)]), "does not have"),
    (lambda s, t: (s, t + [("blk.2.attn_q.weight.lora_a", [64, 16], mta.F16)]), "only 2 layers"),
    (lambda s, t: (s, [(n, [99, 16] if n == "blk.0.attn_output.weight.lora_a" else d, k) for n, d, k in t]),
     "sizes"),
    (lambda s, t: (s, [(n, d, 0) for n, d, k in t]), "16-bit"),
    (lambda s, t: (s, t[2:]), "lacks"),
])
def test_check_gguf_refuses_a_wrong_addon(tmp_path, change, words):
    """A file that is not a Qwen3-VL LoRA, or has a part llama.cpp would not know, a wrong size, another number
    form or a missing part, is refused with plain words."""
    settings, tensors = change(dict(GOOD_SETTINGS), good_tensors())
    path = tmp_path / "b.gguf"
    write_gguf(path, settings, tensors)
    with pytest.raises(mta.AddonError, match=words):
        mta.check_gguf(str(path), CONFIG, 16, 32)


def test_read_gguf_refuses_another_file(tmp_path):
    """A file that is not GGUF is said so."""
    path = tmp_path / "c.gguf"
    path.write_bytes(b"PK\x03\x04 not a gguf")
    with pytest.raises(mta.AddonError, match="not a GGUF"):
        mta.read_gguf(str(path))


def test_add_to_zip_follows_the_contract(tmp_path):
    """add_to_zip adds toolkit/ with the add-on, addon.json (exactly the toolkit's keys, in order) and the how-to,
    keeps everything else, reads the run and the date from an older kit's file name, and leaves nothing behind."""
    kit, path = make_kit(tmp_path)
    gguf = tmp_path / "made.gguf"
    write_gguf(gguf, GOOD_SETTINGS, good_tensors())
    addon = mta.add_to_zip(path, str(kit / "work"), gguf=str(gguf))
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        written = json.loads(z.read("toolkit/addon.json"))
        data = z.read("toolkit/describer-addon.gguf")
        how_to = z.read("toolkit/HOW TO USE THIS IN THE TOOLKIT.txt").decode("utf-8")
    assert {"adapter/adapter_config.json", "report.txt", "scores.json", "ATTRIBUTION.txt"} <= set(names)
    assert written == addon and list(written) == CONTRACT_KEYS
    assert written["format"] == 1 and written["kind"] == "describer-lora"
    assert written["base"] == "qwen3vl-4b" and written["base_repo"] == REPO_4B
    assert written["base_revision"] == REVISION_4B
    assert written["run"] == "4b-full" and written["trained"] == "2026-11-16"
    assert written["name"] == "Your describer, trained 16 November 2026 (4B)"
    assert written["share_alike"] is False and written["personal_use"] is False
    assert written["content"] == {"nudity": True, "medical": True, "graphic": False, "sexual": False}
    assert written["score_before"] == 0.2 and written["score_after"] == 0.25
    assert written["llama_cpp"] == "b11747" == mta.LLAMA_TAG
    assert written["size"] == len(data) == os.path.getsize(gguf)
    assert written["sha256"] == mta.hashlib.sha256(data).hexdigest()
    assert "Install a trained describer..." in how_to and "Describe pictures settings" in how_to
    assert "another computer" in how_to and "copy this zip" in how_to and "Qwen3-VL 4B" in how_to
    assert sorted(os.listdir(kit / "result")) == [os.path.basename(path)]       # no .new file left
    assert mta.has_toolkit(path)


def test_add_to_zip_marks_personal_use_and_share_alike(tmp_path):
    """A personal-use training (PERSONAL-USE-ONLY.txt in the zip, or the person's own pictures) and a training with
    Wikipedia are marked so in addon.json and in the how-to; a newer kit's "run" in scores.json is used."""
    kit, path = make_kit(tmp_path, run="4b-plus-20261117-0900-personal", personal=True,
                         info_extra={"share_alike": True, "run": "4b-plus-20261117-0900-personal"})
    gguf = tmp_path / "made.gguf"
    write_gguf(gguf, GOOD_SETTINGS, good_tensors())
    addon = mta.add_to_zip(path, str(kit / "work"), gguf=str(gguf))
    assert addon["personal_use"] is True and addon["share_alike"] is True
    assert addon["run"] == "4b-plus-20261117-0900-personal"
    with zipfile.ZipFile(path) as z:
        how_to = z.read("toolkit/HOW TO USE THIS IN THE TOOLKIT.txt").decode("utf-8")
    assert "PERSONAL USE ONLY" in how_to and "CC BY-SA 4.0" in how_to
    assert mta.personal_use({"own_pictures": 3}) is True and mta.personal_use({}) is False


def test_a_wrong_addon_leaves_the_zip_as_it_was(tmp_path):
    """When the add-on cannot be made or checked, the zip is not changed and nothing is left behind."""
    kit, path = make_kit(tmp_path)
    with open(path, "rb") as f:
        before = f.read()
    gguf = tmp_path / "wrong.gguf"
    write_gguf(gguf, dict(GOOD_SETTINGS, **{"general.type": "model"}), good_tensors())
    with pytest.raises(mta.AddonError):
        mta.add_to_zip(path, str(kit / "work"), gguf=str(gguf))
    with open(path, "rb") as f:
        assert f.read() == before
    assert sorted(os.listdir(kit / "result")) == [os.path.basename(path)]


def test_zips_without_toolkit_and_catch_up(tmp_path, monkeypatch):
    """A result zip without toolkit/ is found; catch_up makes it once (saying so) when the training's add-on folder
    is still there, and passes over, without a word at the kit's start, one whose add-on folder is gone."""
    kit, path = make_kit(tmp_path)
    with zipfile.ZipFile(kit / "result" / "picture-training-8b-2026-11-01.zip", "w") as z:     # its add-on is gone
        z.writestr("scores.json", json.dumps({"model": REPO_4B.replace("4B", "8B")}))
    (kit / "result" / "notes.zip").write_bytes(b"not a result")
    assert sorted(os.path.basename(p) for p in mta.zips_without_toolkit(str(kit / "result"))) == [
        "picture-training-4b-full-2026-11-16.zip", "picture-training-8b-2026-11-01.zip"]

    def fake_convert(final, out_path, work, repo, revision, say=None, python=None, source_zip=None):
        """Stand-in for llama.cpp's converter: writes a correct small add-on."""
        assert final.endswith(os.path.join("adapter-4b-full", "final"))
        write_gguf(out_path, GOOD_SETTINGS, good_tensors())
        return 28
    monkeypatch.setattr(mta, "convert", fake_convert)
    said = []
    assert mta.catch_up(str(kit), say=said.append) == (1, 0)
    assert any("Making the toolkit version of your earlier training picture-training-4b-full" in s for s in said)
    assert not any("8b" in s for s in said)
    assert mta.has_toolkit(path)
    assert [os.path.basename(p) for p in mta.zips_without_toolkit(str(kit / "result"))] == [
        "picture-training-8b-2026-11-01.zip"]
    said.clear()
    assert mta.catch_up(str(kit), say=said.append) == (0, 0) and not said      # once: nothing more to do


def test_catch_up_says_a_failure_and_goes_on(tmp_path, monkeypatch):
    """A conversion that fails is said in plain words and does not stop anything; the zip stays without toolkit/."""
    kit, path = make_kit(tmp_path)

    def failing_convert(*_args, **_kwargs):
        """Stand-in converter that fails."""
        raise mta.AddonError("llama.cpp's converter failed (made up)")
    monkeypatch.setattr(mta, "convert", failing_convert)
    said = []
    assert mta.catch_up(str(kit), say=said.append) == (0, 1)
    assert any("could not be made: llama.cpp's converter failed" in s and "Start the kit again" in s for s in said)
    assert not mta.has_toolkit(path)


def test_package_never_stops_for_the_toolkit_version(tmp_path, monkeypatch):
    """train.package makes the zip even when the toolkit version fails, and says so in the agreed words."""
    pytest.importorskip("psutil")                  # train.py's computer-use lines need it
    import train
    monkeypatch.setattr(train, "HERE", str(tmp_path))
    monkeypatch.setattr(train, "LOG", str(tmp_path / "training-log.txt"))
    (tmp_path / "training-log.txt").write_text("log\n")
    final = tmp_path / "work" / "adapter-4b" / "final"
    final.mkdir(parents=True)
    (final / "adapter_config.json").write_text("{}")
    report = tmp_path / "report-4b.txt"
    report.write_text("report")

    def failing(*_args, **_kwargs):
        """Stand-in add_to_zip that fails."""
        raise mta.AddonError("made-up reason")
    monkeypatch.setattr(mta, "add_to_zip", failing)
    info = {"model": REPO_4B, "revision": REVISION_4B, "run": "4b", "collections": [], "share_alike": False}
    path = train.package("4b", str(final), str(report), info, "")
    assert os.path.exists(path) and not mta.has_toolkit(path)
    log = (tmp_path / "training-log.txt").read_text(encoding="utf-8")
    assert ("The toolkit version of the add-on could not be made: made-up reason; the zip is made without it. "
            "Start the kit again to try again.") in log


def test_bases_match_the_kit_models():
    """Every model train.py trains (MODELS) has its toolkit model key, and the same pinned commit is meant."""
    with open(os.path.join(KIT, "train.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    models = next(ast.literal_eval(node.value) for node in ast.walk(tree) if isinstance(node, ast.Assign) and
                  any(getattr(t, "id", "") == "MODELS" for t in node.targets))
    for key, (repo, _revision, _memory) in models.items():
        assert mta.BASES[repo][0] == key
        assert mta.BASES[repo][1] == f"qwen3vl-{key}"


def test_converter_source_is_checked(tmp_path):
    """Only the converter's files are kept from llama.cpp's source zip, and a zip whose files do not match the
    release's fingerprint is refused and left nowhere."""
    assert mta.is_needed("convert_lora_to_gguf.py") and mta.is_needed("gguf-py/gguf/constants.py")
    assert mta.is_needed("conversion/qwen3vl.py") and not mta.is_needed("conversion/")
    assert not mta.is_needed("src/llama.cpp") and not mta.is_needed("gguf-py/tests/test.py")
    source = tmp_path / "llama.cpp-b11747.zip"
    with zipfile.ZipFile(source, "w") as z:
        z.writestr("llama.cpp-b11747/convert_lora_to_gguf.py", "print('not the real one')")
        z.writestr("llama.cpp-b11747/conversion/", "")
        z.writestr("llama.cpp-b11747/src/llama.cpp", "int main() {}")
    with pytest.raises(mta.AddonError, match="not the expected release"):
        mta.converter_folder(str(tmp_path / "work"), say=lambda _t: None, source_zip=str(source))
    assert not os.path.exists(tmp_path / "work" / "llama-convert-b11747")
    assert not os.path.exists(tmp_path / "work" / "llama-convert-b11747.partial")


def heavy_tools_ready():
    """True where the real conversion can be tried: PyTorch, Transformers, PEFT and safetensors installed, and
    LLAMA_SOURCE_ZIP naming llama.cpp's source zip; never on GitHub's test job."""
    if os.environ.get("GITHUB_ACTIONS") or not os.path.isfile(os.environ.get("LLAMA_SOURCE_ZIP", "")):
        return False
    import importlib.util
    return all(importlib.util.find_spec(m) for m in ("torch", "transformers", "peft", "safetensors"))


@pytest.mark.skipif(not heavy_tools_ready(), reason="needs PyTorch, Transformers, PEFT, safetensors and "
                                                    "LLAMA_SOURCE_ZIP (llama.cpp's source zip of the release)")
def test_real_conversion(tmp_path):
    """The real thing on a tiny random Qwen3-VL: the kit's own LoRA settings (train.load_model), saved by PEFT,
    converted by llama.cpp's converter through add_to_zip, and checked."""
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForImageTextToText, Qwen3VLConfig
    kit, path = make_kit(tmp_path, with_addon=False)
    rope = {"mrope_interleaved": True, "mrope_section": [8, 4, 4], "rope_type": "default"}
    text = dict(CONFIG["text_config"], vocab_size=512, rope_scaling=rope)
    vision = {"depth": 1, "hidden_size": 32, "intermediate_size": 64, "num_heads": 2, "out_hidden_size": 64,
              "deepstack_visual_indexes": [0]}
    config = Qwen3VLConfig(text_config=text, vision_config=vision)
    config.architectures = ["Qwen3VLForConditionalGeneration"]
    torch.manual_seed(0)
    model = AutoModelForImageTextToText.from_config(config)
    (kit / "work" / "model-4b" / "config.json").write_text(config.to_json_string())
    lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                      target_modules=r".*language_model.*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)")
    get_peft_model(model, lora).save_pretrained(str(kit / "work" / "adapter-4b-full" / "final"))
    addon = mta.add_to_zip(path, str(kit / "work"), say=lambda _t: None, source_zip=os.environ["LLAMA_SOURCE_ZIP"])
    assert addon["base"] == "qwen3vl-4b" and addon["size"] > 0
    with zipfile.ZipFile(path) as z:
        (tmp_path / "out.gguf").write_bytes(z.read("toolkit/describer-addon.gguf"))
    assert mta.check_gguf(str(tmp_path / "out.gguf"), json.loads(config.to_json_string()), 16, 32) == 2 * 7 * 2
