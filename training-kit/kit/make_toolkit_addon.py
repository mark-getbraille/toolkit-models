"""The toolkit version of a trained describer add-on: turns the add-on the kit trains into the file the Digital
Accessibility Toolkit can use, and puts it into the training's result zip.

The kit trains a LoRA add-on (PEFT: work/adapter-<run>/final, with adapter_config.json and
adapter_model.safetensors) for the Hugging Face copy of the picture model. The toolkit runs the GGUF copy of the same
model with llama.cpp's llama-server, which takes an add-on in llama.cpp's own GGUF LoRA format:
    llama-server -m <base gguf> --mmproj <mmproj gguf> --lora toolkit/describer-addon.gguf
This file makes that GGUF add-on with llama.cpp's own converter (convert_lora_to_gguf.py), from the same llama.cpp
release the toolkit uses (LLAMA_TAG, which must match LLAMA_TAG in the toolkit's app/toolkit/vision/vlm.py), and
adds a folder "toolkit/" to the result zip:
    toolkit/describer-addon.gguf                   the add-on in llama.cpp's format (16-bit numbers, "f16")
    toolkit/addon.json                             what it is (the toolkit reads this; see addon_info)
    toolkit/HOW TO USE THIS IN THE TOOLKIT.txt     plain-language steps for the person
    toolkit/addon-label.json                       only for a topic add-on: its label (kit/topics.py), copied from
                                                   addon-label.json at the top of the zip

How the converter is got: once, the source code zip of llama.cpp's release LLAMA_TAG is downloaded from GitHub, and
only the files the converter needs are kept (NEEDED: the two convert scripts, the "conversion" folder, the gguf-py
library and the licence, about 5 MB) in work/llama-convert-<tag>. They are checked against SOURCE_SHA256 (one
fingerprint of every kept file); a download that does not match is thrown away. The converter runs with the kit's
own Python (it needs torch, transformers, safetensors, numpy, PyYAML, tqdm and requests, which the kit already has:
its transformers is the version llama.cpp's converter is pinned to) and with the gguf-py library from the same
release (the converter puts it on its own search path), so no new package is installed. Nothing is sent anywhere;
the converter is told to work offline. llama.cpp is under the MIT licence (kept as LICENSE beside it).

The converter needs the base model's config.json (only its sizes; not the model itself): it is copied from the
downloaded model in work/model-4b or work/model-8b, or, when that was deleted, downloaded alone from Hugging Face
at the model's pinned commit.

The made file is checked before it is put into the zip (check_gguf): it must be a GGUF adapter (general.type
"adapter", adapter.type "lora") for llama.cpp's Qwen3-VL text model (general.architecture "qwen3vl"), with a
lora_a and a lora_b of the right sizes for each of the 7 parts of every layer (blk.N.attn_q.weight.lora_a and so
on), so llama.cpp can load it on the matching model.

Used by train.py (package() makes it for every new result zip; main() adds it once, at the start, to earlier result
zips that lack it while their add-on folder is still there) and by "Make Toolkit Add-on.cmd", which runs this file:
    python kit/make_toolkit_addon.py [ZIP ...] [--source-zip LLAMA_SOURCE_ZIP]
With no ZIP it does every result zip that lacks the toolkit version. --source-zip: a llama.cpp source zip of the
release already on this computer, instead of downloading it.
"""

import datetime
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # the kit folder

LLAMA_TAG = "b11747"           # the llama.cpp release the toolkit runs (app/toolkit/vision/vlm.py LLAMA_TAG)
SOURCE_URL = f"https://github.com/ggml-org/llama.cpp/archive/refs/tags/{LLAMA_TAG}.zip"
# The files kept from the source zip (paths inside it, after its top folder; a path ending in "/" is a folder).
NEEDED = ("convert_lora_to_gguf.py", "convert_hf_to_gguf.py", "LICENSE", "conversion/", "gguf-py/gguf/",
          "gguf-py/LICENSE")
SOURCE_FILES = 125             # how many files that is at LLAMA_TAG
SOURCE_SHA256 = "3ccf378215c3f15ab4b146cb976b3bd223e7e7621f575ca3ca899552d20fe2d2"   # source_fingerprint at LLAMA_TAG

# The base models the kit trains (train.MODELS), by their Hugging Face repository: (the kit's key, the toolkit's
# VlmModel key, the size for names). The toolkit runs the GGUF copies of the same models
# (mradermacher/Huihui-Qwen3-VL-4B-Instruct-abliterated-GGUF and the 8B one).
BASES = {
    "huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated": ("4b", "qwen3vl-4b", "4B"),
    "huihui-ai/Huihui-Qwen3-VL-8B-Instruct-abliterated": ("8b", "qwen3vl-8b", "8B"),
}

FOLDER = "toolkit/"                                    # the folder in the result zip
ADDON_FILE = FOLDER + "describer-addon.gguf"
INFO_FILE = FOLDER + "addon.json"
HOW_TO_FILE = FOLDER + "HOW TO USE THIS IN THE TOOLKIT.txt"
PERSONAL_MARK = "PERSONAL-USE-ONLY.txt"               # train.package puts it into a personal-use training's zip
LABEL_NAME = "addon-label.json"                       # a topic add-on's label (topics.LABEL_FILE), at the zip's top
LABEL_FILE = FOLDER + LABEL_NAME

# The parts of each layer the add-on changes (train.load_model's target modules), by llama.cpp's names, with the
# sizes going in and coming out, from the model's text settings (see expected_sizes).
PARTS = ("attn_q", "attn_k", "attn_v", "attn_output", "ffn_gate", "ffn_up", "ffn_down")
TENSOR_NAME = re.compile(r"^blk\.(\d+)\.(" + "|".join(PARTS) + r")\.weight\.lora_([ab])$")
ZIP_NAME = re.compile(r"^picture-training-(.+)-(\d{4}-\d{2}-\d{2})\.zip$", re.IGNORECASE)
F16 = 1                                                # ggml's number for 16-bit floating point tensors


class AddonError(Exception):
    """A plain-words reason the toolkit version could not be made."""


def _say(text):
    """Say text on the screen (the default when no say function is given)."""
    print(text, flush=True)


# ----------------------------------------------------------------- llama.cpp's converter

def source_fingerprint(folder):
    """(how many files, one SHA-256 of all of them) for the converter files kept in folder: the SHA-256 of the
    lines "<path>\\t<SHA-256 of the file>", sorted by path ("/" between folders), so the same files give the same
    fingerprint on any computer. Python's own cache folders (__pycache__) are not counted."""
    lines = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            path = os.path.join(root, name)
            relative = os.path.relpath(path, folder).replace(os.sep, "/")
            if relative == "VERIFIED.txt":
                continue
            with open(path, "rb") as f:
                lines.append(f"{relative}\t{hashlib.sha256(f.read()).hexdigest()}\n")
    whole = hashlib.sha256("".join(sorted(lines)).encode("utf-8")).hexdigest()
    return len(lines), whole


def is_needed(path):
    """True when path (inside the source zip, after its top folder) is one of the files the converter needs."""
    if path.endswith("/"):
        return False                                   # a folder entry: its files are taken one by one
    return any(path == n or (n.endswith("/") and path.startswith(n)) for n in NEEDED)


def unpack_converter(source_zip, folder):
    """Keep the needed files of the llama.cpp source zip source_zip in folder (made new), check them against
    SOURCE_SHA256 and mark them checked (VERIFIED.txt); raises AddonError when they do not match."""
    partial = folder + ".partial"
    shutil.rmtree(partial, ignore_errors=True)
    try:
        with zipfile.ZipFile(source_zip) as z:
            for item in z.infolist():
                inner = item.filename.split("/", 1)[1] if "/" in item.filename else ""
                if not inner or not is_needed(inner) or ".." in inner.split("/"):
                    continue
                target = os.path.join(partial, *inner.split("/"))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with z.open(item) as source, open(target, "wb") as out:
                    shutil.copyfileobj(source, out)
    except (OSError, zipfile.BadZipFile) as e:
        shutil.rmtree(partial, ignore_errors=True)
        raise AddonError(f"the llama.cpp converter could not be unpacked ({e})") from e
    count, whole = source_fingerprint(partial)
    if (count, whole) != (SOURCE_FILES, SOURCE_SHA256):
        shutil.rmtree(partial, ignore_errors=True)
        raise AddonError(f"the downloaded llama.cpp converter is not the expected release {LLAMA_TAG} (its files do "
                         "not match their fingerprint), so it is not used")
    with open(os.path.join(partial, "VERIFIED.txt"), "w", encoding="utf-8") as f:
        f.write(f"llama.cpp {LLAMA_TAG} converter files, checked: {count} files, fingerprint {whole}\n")
    shutil.rmtree(folder, ignore_errors=True)
    os.replace(partial, folder)


def converter_folder(work, say=_say, source_zip=None):
    """The folder with llama.cpp's converter (work/llama-convert-<tag>), got and checked once: from source_zip when
    given, else downloaded from GitHub (about 40 MB). Raises AddonError when it cannot be got."""
    folder = os.path.join(work, f"llama-convert-{LLAMA_TAG}")
    marker = os.path.join(folder, "VERIFIED.txt")
    if os.path.exists(marker) and os.path.exists(os.path.join(folder, "convert_lora_to_gguf.py")):
        return folder
    os.makedirs(work, exist_ok=True)
    if source_zip is None:
        say(f"  Getting llama.cpp's add-on converter (release {LLAMA_TAG}, about 40 MB, once).")
        source_zip = os.path.join(work, f"llama-source-{LLAMA_TAG}.zip")
        try:
            import requests
            with requests.get(SOURCE_URL, stream=True, timeout=120,
                              headers={"User-Agent": "Picture-Model-Training-Kit"}) as r:
                r.raise_for_status()
                with open(source_zip, "wb") as f:
                    for block in r.iter_content(1 << 20):
                        f.write(block)
        except Exception as e:  # noqa: BLE001 - said in plain words
            try:
                os.remove(source_zip)                  # a part of a download is never used
            except OSError:
                pass
            raise AddonError(f"llama.cpp's converter could not be downloaded from GitHub ({str(e)[:200]}); check the "
                             "internet connection") from e
        try:
            unpack_converter(source_zip, folder)
        finally:
            try:
                os.remove(source_zip)
            except OSError:
                pass
    else:
        unpack_converter(source_zip, folder)
    say("  The converter is ready and checked.")
    return folder


# ----------------------------------------------------------------- reading a GGUF file

def read_gguf(path):
    """(settings, tensors) of the GGUF file at path, read without any library: settings is {key: value} (arrays as
    lists), tensors is [(name, sizes, ggml type number)]. Raises AddonError when it is not a GGUF file."""
    scalar = {0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 6: "<f", 7: "<?", 10: "<Q", 11: "<q", 12: "<d"}
    with open(path, "rb") as f:
        def take(fmt):
            """One number of struct format fmt."""
            size = struct.calcsize(fmt)
            data = f.read(size)
            if len(data) != size:
                raise AddonError("the add-on file ends too early")
            return struct.unpack(fmt, data)[0]

        def text():
            """One GGUF string (its length, then UTF-8)."""
            length = take("<Q")
            if length > 1 << 24:
                raise AddonError("the add-on file has a broken text in it")
            return f.read(length).decode("utf-8", "replace")

        def value(kind):
            """One setting value of GGUF type kind."""
            if kind == 8:
                return text()
            if kind == 9:
                inner, count = take("<I"), take("<Q")
                return [value(inner) for _ in range(count)]
            if kind not in scalar:
                raise AddonError(f"the add-on file has an unknown kind of setting ({kind})")
            return take(scalar[kind])

        if f.read(4) != b"GGUF":
            raise AddonError("the made file is not a GGUF file")
        version = take("<I")
        if version not in (2, 3):
            raise AddonError(f"the made file is GGUF version {version}, which is not known here")
        tensor_count, setting_count = take("<Q"), take("<Q")
        settings = {}
        for _ in range(setting_count):
            key = text()
            settings[key] = value(take("<I"))
        tensors = []
        for _ in range(tensor_count):
            name = text()
            sizes = [take("<Q") for _ in range(take("<I"))]
            kind = take("<I")
            take("<Q")                          # where its numbers are in the file
            tensors.append((name, sizes, kind))
    return settings, tensors


def expected_sizes(config):
    """{part: (size going in, size coming out)} of the 7 parts of a layer, from the model's config.json (its
    text_config, as the converter reads it)."""
    text = dict(config, **config.get("text_config", {}))
    hidden, inner = text["hidden_size"], text["intermediate_size"]
    heads = text["num_attention_heads"]
    kv_heads = text.get("num_key_value_heads", heads)
    head = text.get("head_dim") or hidden // heads
    return {"attn_q": (hidden, heads * head), "attn_k": (hidden, kv_heads * head), "attn_v": (hidden, kv_heads * head),
            "attn_output": (heads * head, hidden), "ffn_gate": (hidden, inner), "ffn_up": (hidden, inner),
            "ffn_down": (inner, hidden)}


def check_gguf(path, config, rank, alpha):
    """Check that the made add-on is one llama.cpp loads on the Qwen3-VL model of config: a GGUF LoRA adapter for
    the "qwen3vl" text model, with alpha, and for every layer a lora_a (sizes [in, rank]) and a lora_b ([rank,
    out]) of each of the 7 parts, all 16-bit, and nothing else. Raises AddonError with the first thing wrong."""
    settings, tensors = read_gguf(path)
    for key, wanted in (("general.type", "adapter"), ("adapter.type", "lora"), ("general.architecture", "qwen3vl")):
        if settings.get(key) != wanted:
            raise AddonError(f"the made file is not a Qwen3-VL LoRA add-on ({key} is {settings.get(key)!r}, not "
                             f"{wanted!r})")
    if abs(float(settings.get("adapter.lora.alpha", -1)) - float(alpha)) > 1e-6:
        raise AddonError(f"the made add-on has the strength (alpha) {settings.get('adapter.lora.alpha')}, not {alpha}")
    sizes = expected_sizes(config)
    layers = dict(config, **config.get("text_config", {}))["num_hidden_layers"]
    found = {}
    for name, dims, kind in tensors:
        match = TENSOR_NAME.match(name)
        if not match:
            raise AddonError(f"the made add-on has a part llama.cpp's Qwen3-VL model does not have: {name}")
        layer, part, which = int(match.group(1)), match.group(2), match.group(3)
        if layer >= layers:
            raise AddonError(f"the made add-on has layer {layer}, but the model has only {layers} layers")
        in_size, out_size = sizes[part]
        want = [in_size, rank] if which == "a" else [rank, out_size]
        if list(dims) != want:
            raise AddonError(f"the made add-on's {name} has the sizes {list(dims)}, not {want}")
        if kind != F16:
            raise AddonError(f"the made add-on's {name} is not in 16-bit form")
        found[name] = True
    missing = [f"blk.{n}.{p}.weight.lora_{w}" for n in range(layers) for p in PARTS for w in "ab"
               if f"blk.{n}.{p}.weight.lora_{w}" not in found]
    if missing:
        raise AddonError(f"the made add-on lacks {len(missing)} of its parts, for example {missing[0]}")
    return len(tensors)


# ----------------------------------------------------------------- making the add-on

def base_config(work, repo, revision):
    """The base model's config.json as a dict, and a folder holding only it (for the converter's --base): copied
    from the downloaded model (work/model-<key>), or downloaded alone from Hugging Face at revision."""
    key = BASES[repo][0]
    folder = os.path.join(work, "toolkit-addon", f"base-{key}")
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, "config.json")
    source = os.path.join(work, f"model-{key}", "config.json")
    if os.path.exists(source):
        shutil.copyfile(source, target)
    elif not os.path.exists(target):
        try:
            from huggingface_hub import hf_hub_download
            shutil.copyfile(hf_hub_download(repo, "config.json", revision=revision), target)
        except Exception as e:  # noqa: BLE001 - said in plain words
            raise AddonError(f"the model's settings file (config.json) was not found in {os.path.dirname(source)} "
                             f"and could not be downloaded ({str(e)[:200]})") from e
    with open(target, encoding="utf-8") as f:
        return json.load(f), folder


def convert(final, out_path, work, repo, revision, say=_say, python=None, source_zip=None):
    """Make the GGUF add-on out_path from the PEFT add-on folder final (adapter_config.json and
    adapter_model.safetensors) for the base model repo at revision, with llama.cpp's convert_lora_to_gguf.py
    (--outtype f16), run by the kit's own Python (python, default sys.executable), and check it (check_gguf).
    Returns how many tensors it has. Raises AddonError in plain words."""
    if repo not in BASES:
        raise AddonError(f"the add-on was trained on {repo}, which the toolkit does not run as a describer")
    for name in ("adapter_config.json", "adapter_model.safetensors"):
        if not os.path.exists(os.path.join(final, name)):
            raise AddonError(f"the add-on folder {final} has no {name}")
    converter = converter_folder(work, say, source_zip)
    config, base_folder = base_config(work, repo, revision)
    with open(os.path.join(final, "adapter_config.json"), encoding="utf-8") as f:
        adapter = json.load(f)
    # A copy of the add-on: the settings point at the model's name instead of a folder on this computer, and the
    # PEFT README (which names that folder) is left out, so no local path goes into the made file.
    copy = os.path.join(work, "toolkit-addon", "describer-addon")
    shutil.rmtree(copy, ignore_errors=True)
    os.makedirs(copy)
    shutil.copyfile(os.path.join(final, "adapter_model.safetensors"), os.path.join(copy, "adapter_model.safetensors"))
    with open(os.path.join(copy, "adapter_config.json"), "w", encoding="utf-8") as f:
        json.dump(dict(adapter, base_model_name_or_path=repo, revision=revision), f, indent=1)
    temporary = out_path + ".partial"
    env = {k: v for k, v in os.environ.items() if k != "NO_LOCAL_GGUF"}      # use the release's own gguf-py
    env.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
               HF_HUB_DISABLE_TELEMETRY="1", PYTHONWARNINGS="ignore", TRANSFORMERS_VERBOSITY="error")
    command = [python or sys.executable, os.path.join(converter, "convert_lora_to_gguf.py"), "--base", base_folder,
               "--outtype", "f16", "--outfile", temporary, copy]
    say("  Converting the add-on with llama.cpp's converter (a minute or two).")
    try:
        done = subprocess.run(command, check=False, cwd=os.path.dirname(copy), env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    finally:
        shutil.rmtree(copy, ignore_errors=True)
    if done.returncode != 0 or not os.path.exists(temporary):
        lines = [line for line in (done.stderr or done.stdout or "").splitlines() if line.strip()]
        raise AddonError("llama.cpp's converter failed (" + (lines[-1].strip()[:300] if lines else
                                                             f"code {done.returncode}") + ")")
    try:
        count = check_gguf(temporary, config, int(adapter.get("r", 16)), adapter.get("lora_alpha", 32))
    except AddonError:
        os.remove(temporary)
        raise
    os.replace(temporary, out_path)
    return count


# ----------------------------------------------------------------- what goes into the zip

def sha256_of(path):
    """The SHA-256 of the file at path, as hexadecimal text."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run_and_date(zip_path, info):
    """(run name, training date) of a result zip: the run from scores.json ("run", written since the toolkit version
    was added) or else from the file name (picture-training-<run>-<date>.zip, as train.package names it); the date
    from the file name, or the zip file's own date."""
    match = ZIP_NAME.match(os.path.basename(zip_path))
    run = info.get("run") or (match.group(1) if match else None)
    try:
        day = datetime.date.fromisoformat(match.group(2)) if match else None
    except ValueError:
        day = None
    if day is None:
        day = datetime.date.fromtimestamp(os.path.getmtime(zip_path))
    return run, day


def personal_use(info, names=()):
    """True when the add-on is for personal use only: the zip holds PERSONAL-USE-ONLY.txt (train.package writes it
    when train.personal_chosen(info): personal-use collections or review collections), or the training's choices say
    personal-use collections, review collections or the person's own pictures were used."""
    return bool(PERSONAL_MARK in names or info.get("with_noncommercial") or info.get("with_research") or
                info.get("review_pictures") or info.get("own_pictures"))


def addon_info(info, run, day, gguf_path, personal):
    """addon.json for the toolkit (format 1): which model it is for, its name, the training's run and date, its
    licence facts (share_alike: Wikipedia's CC BY-SA 4.0; personal_use), the content choices, the scores before and
    after, the llama.cpp release it was made with, and the file's SHA-256 and size."""
    repo = info["model"]
    _key, toolkit_key, size_name = BASES[repo]
    return {"format": 1, "kind": "describer-lora", "base": toolkit_key, "base_repo": repo,
            "base_revision": info.get("revision", ""),
            "name": f"Your describer, trained {day.day} {day:%B %Y} ({size_name})",
            "run": run, "trained": day.isoformat(), "share_alike": bool(info.get("share_alike")),
            "personal_use": bool(personal),
            "content": {c: bool(info.get(f"with_{c}")) for c in ("nudity", "medical", "graphic", "sexual")},
            "score_before": float((info.get("before") or {}).get("all", 0.0)),
            "score_after": float((info.get("after") or {}).get("all", 0.0)),
            "llama_cpp": LLAMA_TAG, "sha256": sha256_of(gguf_path), "size": os.path.getsize(gguf_path)}


def how_to_text(addon):
    """HOW TO USE THIS IN THE TOOLKIT.txt: plain-language steps for installing the add-on in the toolkit."""
    size_name = BASES[addon["base_repo"]][2]
    lines = [
        "How to use your trained describer in the Digital Accessibility Toolkit", "",
        f"This zip holds \"{addon['name']}\": an add-on for the toolkit's Qwen3-VL {size_name} picture model that "
        "describes pictures the way your training taught it.",
        f"Its score went from {addon['score_before']:.3f} before training to {addon['score_after']:.3f} after (from 0 "
        "to 1; higher means closer to the people's descriptions).", "",
        "To install it:",
        "1. Open the Digital Accessibility Toolkit.",
        "2. Go to the Describe pictures settings.",
        "3. Choose \"Install a trained describer...\".",
        "4. Choose this zip file (the whole zip, not the files inside it).", "",
        "To use it on another computer: copy this zip file to that computer (by USB stick, a shared drive or email), "
        "and install it there the same way.", "",
        f"It works only with the matching model, Qwen3-VL {size_name} (the toolkit's \"Qwen3-VL {size_name}\" "
        "picture model), and only with the llama.cpp engine the toolkit uses. It does not work with other models.",
    ]
    if addon["personal_use"]:
        lines += ["", "PERSONAL USE ONLY: this add-on learned from pictures that may only be used personally (your "
                      "own pictures, non-commercial or research-only collections, or review collections). Do not "
                      "sell it, publish it, put it in a product or share it outside personal, non-commercial use. "
                      "See PERSONAL-USE-ONLY.txt in this zip."]
    if addon["share_alike"]:
        lines += ["", "This add-on learned from Wikipedia, so it is under the CC BY-SA 4.0 licence: if you share it, "
                      "share it under the same licence. See ATTRIBUTION.txt in this zip."]
    lines += ["", "The add-on file is toolkit/describer-addon.gguf (llama.cpp's LoRA format, made with llama.cpp "
                  f"release {addon['llama_cpp']}); toolkit/addon.json says what it is."]
    return "\n".join(lines) + "\n"


def has_toolkit(zip_path):
    """True when the result zip already holds the toolkit version (toolkit/describer-addon.gguf)."""
    with zipfile.ZipFile(zip_path) as z:
        return ADDON_FILE in z.namelist()


def read_scores(zip_path):
    """(scores.json of the result zip as a dict, the names in the zip). Raises AddonError when it has none."""
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            return json.loads(z.read("scores.json").decode("utf-8")), names
    except (KeyError, ValueError, zipfile.BadZipFile) as e:
        raise AddonError(f"{os.path.basename(zip_path)} is not a training result zip with scores.json ({e})") from e


def add_to_zip(zip_path, work, final=None, say=_say, python=None, source_zip=None, gguf=None):
    """Add the toolkit/ folder to the result zip at zip_path and return the addon.json written. final: the trained
    add-on folder (default: work/adapter-<run>/final, the run read from the zip); gguf: an add-on already converted
    (then it is only checked, against the base model's config.json). The zip is written anew beside the old one and
    only then put in its place, so a failure never spoils it. Raises AddonError in plain words."""
    info, names = read_scores(zip_path)
    run, day = run_and_date(zip_path, info)
    repo = info.get("model")
    if repo not in BASES:
        raise AddonError(f"the training was of {repo}, which the toolkit does not run as a describer")
    if final is None and gguf is None:
        if not run:
            raise AddonError(f"the training's name cannot be read from {os.path.basename(zip_path)}")
        final = os.path.join(work, f"adapter-{run}", "final")
        if not os.path.isdir(final):
            raise AddonError(f"the trained add-on of {run} is no longer in {os.path.dirname(final)}")
    made = os.path.join(work, "toolkit-addon", "describer-addon.gguf")
    os.makedirs(os.path.dirname(made), exist_ok=True)
    if gguf is None:
        convert(final, made, work, repo, info.get("revision", ""), say, python, source_zip)
    else:
        config, _folder = base_config(work, repo, info.get("revision", ""))
        settings = (info.get("settings") or {})
        check_gguf(gguf, config, settings.get("lora_r", 16), settings.get("lora_alpha", 32))
        shutil.copyfile(gguf, made)
    addon = addon_info(info, run, day, made, personal_use(info, names))
    new_path = zip_path + ".new"
    try:
        with zipfile.ZipFile(zip_path) as old, zipfile.ZipFile(new_path, "w", zipfile.ZIP_DEFLATED) as new:
            for item in old.infolist():
                if not item.filename.startswith(FOLDER):
                    with old.open(item) as source, new.open(item, "w") as out:
                        shutil.copyfileobj(source, out, 1 << 20)
            new.write(made, ADDON_FILE, compress_type=zipfile.ZIP_STORED)    # 16-bit numbers hardly shrink
            new.writestr(INFO_FILE, json.dumps(addon, indent=1) + "\n")
            new.writestr(HOW_TO_FILE, how_to_text(addon).replace("\n", "\r\n"))   # Windows line ends for Notepad
            if LABEL_NAME in names:                    # a topic add-on: its label goes beside the toolkit file too
                new.writestr(LABEL_FILE, old.read(LABEL_NAME))
        with zipfile.ZipFile(new_path) as check:
            if check.testzip() is not None or check.getinfo(ADDON_FILE).file_size != addon["size"]:
                raise AddonError("the new zip could not be checked")
        os.replace(new_path, zip_path)
    except OSError as e:
        raise AddonError(f"the zip could not be written ({e})") from e
    finally:
        for path in (new_path, made):
            try:
                os.remove(path)
            except OSError:
                pass
    return addon


def zips_without_toolkit(result_folder):
    """The result zips (picture-training-*.zip) in result_folder that lack the toolkit version, oldest first."""
    if not os.path.isdir(result_folder):
        return []
    found = []
    for name in os.listdir(result_folder):
        path = os.path.join(result_folder, name)
        if ZIP_NAME.match(name):
            try:
                if not has_toolkit(path):
                    found.append(path)
            except (OSError, zipfile.BadZipFile):
                continue
    return sorted(found, key=os.path.getmtime)


def addon_folder_of(zip_path, work):
    """The trained add-on folder (work/adapter-<run>/final) of a result zip when it is still there, else None."""
    try:
        info, _names = read_scores(zip_path)
    except AddonError:
        return None
    run, _day = run_and_date(zip_path, info)
    final = os.path.join(work, f"adapter-{run}", "final") if run else None
    return final if final and os.path.isdir(final) else None


def catch_up(kit_folder, say=_say, only_with_addon=True, source_zip=None, zips=None):
    """Add the toolkit version to each earlier result zip in kit_folder/result that lacks it (or to zips), saying
    each in plain words. only_with_addon: skip, without a word, a zip whose trained add-on folder is gone (at the
    kit's start); otherwise that is said. A failure is said and never stops anything. Returns (made, failed)."""
    work = os.path.join(kit_folder, "work")
    made = failed = 0
    for path in zips if zips is not None else zips_without_toolkit(os.path.join(kit_folder, "result")):
        name = os.path.basename(path)
        if addon_folder_of(path, work) is None:
            if not only_with_addon:
                say(f"{name}: its trained add-on is no longer in the kit's work folder, so the toolkit version "
                    "cannot be made for it.")
                failed += 1
            continue
        say(f"Making the toolkit version of your earlier training {name} (a few minutes, once).")
        try:
            addon = add_to_zip(path, work, say=say, source_zip=source_zip)
        except Exception as e:  # noqa: BLE001 - said in plain words, never stops the kit
            say(f"  The toolkit version of the add-on could not be made: {str(e).splitlines()[0][:300]}. Start the "
                "kit again to try again.")
            failed += 1
            continue
        size = max(addon["size"] / 1024 ** 2, 0.1)
        say(f"  Done: {name} now holds the toolkit version ({size:.1f} MB). Install it in the Digital Accessibility "
            "Toolkit with \"Install a trained describer...\" in the Describe pictures settings.")
        made += 1
    return made, failed


def main(argv=None):
    """"Make Toolkit Add-on.cmd": add the toolkit version to the result zips named, or to every result zip in the
    kit's result folder that lacks it; says what was done. Returns 0, or 1 when one could not be made."""
    import argparse
    parser = argparse.ArgumentParser(description="Add the Digital Accessibility Toolkit version of the trained "
                                                 "describer add-on to the training's result zips.")
    parser.add_argument("zips", nargs="*", help="result zips (default: every one in the result folder that lacks it)")
    parser.add_argument("--source-zip", default=None, help=f"llama.cpp's source zip of release {LLAMA_TAG}, "
                                                           "instead of downloading it")
    args = parser.parse_args(argv)
    if args.zips:
        zips = []
        for path in (os.path.abspath(z) for z in args.zips):
            if has_toolkit(path):
                print(f"{os.path.basename(path)} already holds the toolkit version.")
            else:
                zips.append(path)
    else:
        zips = zips_without_toolkit(os.path.join(HERE, "result"))
    if not zips:
        print("Every result zip in the result folder already holds the toolkit version (or there is no result zip "
              "yet).")
        return 0
    made, failed = catch_up(HERE, only_with_addon=False, source_zip=args.source_zip, zips=zips)
    print(f"Finished: {made} made, {failed} could not be made.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
