"""Picture Model Training Kit: teach the Digital Accessibility Toolkit's picture model (huihui-ai's uncensored
Qwen3-VL) to describe pictures the way a blind reader needs, on your own computer's NVIDIA graphics card.

Started by "Start Training.cmd" (4B model) or "Start Training 8B.cmd". Every step says what it does in plain words,
on the screen and in training-log.txt. A step that is finished is not done again: if the computer restarts or the
window is closed, start it again and it carries on where it stopped (training itself from its last save, every
200 pictures).

The steps:
  1. check the graphics card (NVIDIA, enough memory) and the free disk space;
  2. download the model at a pinned commit from Hugging Face;
  3. download the pictures with their descriptions and make them smaller (at most 896 pixels on the long side):
       DOCCI (Google, CC BY 4.0): 15,000 photos, each described in about 120 words; its "train" part is used for
       training and 70 of its "test" part for the test;
       VizWiz Captions (CC BY 4.0, the lmms-lab copy on Hugging Face): 7,750 photos taken by blind people, each with
       a one-sentence description; 30 are kept back for the test;
  4. test the model before training: it describes the 100 test pictures, and each description is scored against
     the human one (ROUGE-L, from 0 to 1: how much of the human description's wording it shares);
  5. train a small add-on (a LoRA adapter of the language part; the model itself stays as it is), one pass over the
     training pictures, on the model loaded in 4-bit form so it fits a 12 to 16 GB card;
  6. test again with the add-on, and write report.txt: the scores before and after, whether it got better, and 15
     examples to read;
  7. put the add-on, the report and the scores in one zip in the "result" folder, for sending.

The questions it is trained on are the toolkit's own (vision/vlm.py): PICTURE ("Describe this picture in detail.")
with DOCCI's long descriptions, and a short question with VizWiz's one-sentence ones, with the toolkit's SYSTEM text.

Command line (the .cmd files pass these): --model 4b|8b, --limit N (train on at most N pictures, for a quick try),
--test-size N.
"""

import argparse
import ctypes
import datetime
import io
import json
import math
import os
import random
import re
import shutil
import sys
import tarfile
import time
import zipfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # the kit folder
LOG = os.path.join(HERE, "training-log.txt")

MODELS = {   # the toolkit's uncensored picture models (app/toolkit/vision/engines/models.py), pinned
    "4b": ("huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated", "ce72a7c22aacb493fb94478de3bfbe834c61844a", 11),
    "8b": ("huihui-ai/Huihui-Qwen3-VL-8B-Instruct-abliterated", "b47a0690b22eaf1d9a63874d967a03781c90f9cf", 15),
}   # key: (Hugging Face repository, commit, the least graphics card memory in GB)
DOCCI = "https://storage.googleapis.com/docci/data/"
VIZWIZ = "lmms-lab/VizWiz-Caps"
VIZWIZ_REVISION = "main"

# The toolkit's own words (vision/vlm.py SYSTEM, PICTURE), so the add-on learns the questions the program asks.
SYSTEM = "The user is blind. Never describe anyone who may be under 18 in a sexual way."
DETAILED = "Describe this picture in detail."
BRIEF = "Describe this picture in one sentence."

LONG_SIDE = 896            # pixels: pictures are made this small (about 780 picture tokens at most)
SAVE_EVERY = 200           # training pictures between saves
FREE_GB_NEEDED = {"4b": 70, "8b": 90}


# ----------------------------------------------------------------- saying what happens

def say(text=""):
    """Write one line to the screen and to training-log.txt, with the time in the log."""
    print(text, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  {text}\n")


def stop(text):
    """Say why the kit stops, and stop (the .cmd file then waits for a key)."""
    say("")
    say("STOPPED: " + text)
    sys.exit(1)


def duration(seconds):
    """A length of time in plain words: "3 hours 20 minutes", "12 minutes"."""
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    return f"{max(minutes, 1)} minute{'s' if minutes > 1 else ''}"


def keep_awake(on=True):
    """Ask Windows not to sleep while the kit runs (the screen may still turn off); nothing elsewhere."""
    if os.name == "nt":
        flags = 0x80000000 | (0x00000001 if on else 0)          # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        ctypes.windll.kernel32.SetThreadExecutionState(flags)


# ----------------------------------------------------------------- steps that are done once

class State:
    """Which steps are finished (state.json in the work folder), so a restarted kit carries on."""

    def __init__(self, folder):
        """Read state.json from folder (empty when there is none)."""
        self.path = os.path.join(folder, "state.json")
        self.data = {}
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as f:
                self.data = json.load(f)

    def done(self, step):
        """True when step is finished."""
        return bool(self.data.get(step))

    def mark(self, step, value=True):
        """Record step as finished (value: anything worth keeping about it)."""
        self.data[step] = value
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=1)


# ----------------------------------------------------------------- 1. the graphics card and the disk

def check_computer(model_key, work):
    """Stop with a plain reason unless there is an NVIDIA card with enough memory and enough free disk space;
    returns the card's name and memory in GB."""
    import torch
    if not torch.cuda.is_available():
        stop("No NVIDIA graphics card can be used. The kit needs an NVIDIA card with at least 12 GB of memory and an "
             "up-to-date NVIDIA driver (from nvidia.com).")
    props = torch.cuda.get_device_properties(0)
    memory = props.total_memory / 1024 ** 3
    need = MODELS[model_key][2]
    say(f"Graphics card: {props.name}, {memory:.0f} GB of memory.")
    if memory < need:
        stop(f"The {model_key.upper()} model needs a card with at least {need + 1} GB of memory; this card has "
             f"{memory:.0f} GB." + (" Try Start Training.cmd (the 4B model) instead." if model_key == "8b" else ""))
    free = shutil.disk_usage(work).free / 1024 ** 3
    say(f"Free disk space on this drive: {free:.0f} GB.")
    if free < FREE_GB_NEEDED[model_key]:
        stop(f"The kit needs about {FREE_GB_NEEDED[model_key]} GB of free disk space here; there is {free:.0f} GB. "
             "Free some space, or move the kit folder to a bigger drive, and start it again.")
    return props.name, memory


# ----------------------------------------------------------------- 2. the model

def download_model(model_key, work):
    """Download the model at its pinned commit into work/model-<key> (resumed if stopped); returns the folder."""
    from huggingface_hub import snapshot_download
    repo, revision, _ = MODELS[model_key]
    folder = os.path.join(work, f"model-{model_key}")
    snapshot_download(repo, revision=revision, local_dir=folder)
    return folder


# ----------------------------------------------------------------- 3. the pictures

def download_file(url, path):
    """Download url to path, carrying on from a part already there; says the progress every 5 percent."""
    import requests
    done = os.path.getsize(path) if os.path.exists(path) else 0
    head = requests.head(url, timeout=60, allow_redirects=True)
    total = int(head.headers.get("content-length", 0))
    if total and done == total:
        return
    headers = {"Range": f"bytes={done}-"} if done else {}
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        if done and r.status_code != 206:
            done = 0                                       # the server started again from the beginning
        next_say = 5
        with open(path, "ab" if done else "wb") as f:
            for block in r.iter_content(1 << 20):
                f.write(block)
                done += len(block)
                if total and done * 100 // total >= next_say:
                    say(f"    {done * 100 // total} percent of {total / 1024 ** 3:.1f} GB")
                    next_say = done * 100 // total + 5


def smaller(data, path):
    """Save picture bytes as a JPEG at most LONG_SIDE pixels on its long side; False when it cannot be read."""
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGB")
    except Exception:  # noqa: BLE001 - a damaged picture is left out
        return False
    img.thumbnail((LONG_SIDE, LONG_SIDE))
    img.save(path, "JPEG", quality=90)
    return True


def prepare_docci(work, data_dir):
    """DOCCI's pictures (made smaller) and descriptions: [(split, picture path, description)]."""
    import requests
    pictures = os.path.join(data_dir, "docci")
    os.makedirs(pictures, exist_ok=True)
    descriptions = {}
    for line in requests.get(DOCCI + "docci_descriptions.jsonlines", timeout=120).text.splitlines():
        if line.strip():
            entry = json.loads(line)
            descriptions[entry["image_file"]] = (entry["split"], entry["description"])
    archive = os.path.join(work, "docci_images.tar.gz")
    say("  Downloading DOCCI's pictures (7.6 GB).")
    download_file(DOCCI + "docci_images.tar.gz", archive)
    say("  Making the DOCCI pictures smaller (this takes a while).")
    out, count = [], 0
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            name = os.path.basename(member.name)
            if not member.isfile() or name not in descriptions:
                continue
            split, text = descriptions[name]
            if split not in ("train", "test"):
                continue
            path = os.path.join(pictures, name)
            if os.path.exists(path) or smaller(tar.extractfile(member).read(), path):
                out.append((split, path, text))
            count += 1
            if count % 1000 == 0:
                say(f"    {count} pictures done")
    os.remove(archive)                                     # the small copies are kept; 7.6 GB freed
    return out


def prepare_vizwiz(data_dir):
    """VizWiz's photos taken by blind people (made smaller) with their one-sentence descriptions: [(split, path,
    description)], all of split "train" (the test pictures are picked later)."""
    from huggingface_hub import HfApi, hf_hub_download
    import pyarrow.parquet as pq
    pictures = os.path.join(data_dir, "vizwiz")
    os.makedirs(pictures, exist_ok=True)
    files = sorted(f for f in HfApi().list_repo_files(VIZWIZ, repo_type="dataset", revision=VIZWIZ_REVISION)
                   if f.startswith("data/val-") and f.endswith(".parquet"))
    out = []
    for number, name in enumerate(files, 1):
        say(f"  Downloading VizWiz part {number} of {len(files)} (about 500 MB).")
        local = hf_hub_download(VIZWIZ, name, repo_type="dataset", revision=VIZWIZ_REVISION)
        for row in pq.read_table(local).to_pylist():
            caption = (row.get("caption") or "").strip()
            image = row.get("image") or {}
            if not caption or "quality issues are too severe" in caption.lower():
                continue                                   # VizWiz's "picture too blurry to describe" marker
            path = os.path.join(pictures, f"{row['image_id']}.jpg".replace("/", "_"))
            if os.path.exists(path) or smaller(image.get("bytes") or b"", path):
                out.append(("train", path, caption))
    return out


def prepare_data(work, test_size, seed=7):
    """Download and prepare the pictures once; writes data/train.jsonl and data/test.jsonl ({"picture", "question",
    "answer", "source"}) and returns (number of training pictures, number of test pictures)."""
    data_dir = os.path.join(work, "data")
    os.makedirs(data_dir, exist_ok=True)
    docci = prepare_docci(work, data_dir)
    vizwiz = prepare_vizwiz(data_dir)
    rng = random.Random(seed)
    docci_test = [d for d in docci if d[0] == "test"]
    rng.shuffle(docci_test)
    rng.shuffle(vizwiz)
    test_docci = round(test_size * 0.7)
    test = [(p, DETAILED, t, "DOCCI") for _, p, t in docci_test[:test_docci]] + \
           [(p, BRIEF, t, "VizWiz") for _, p, t in vizwiz[:test_size - test_docci]]
    train = [(p, DETAILED, t, "DOCCI") for s, p, t in docci if s == "train"] + \
            [(p, BRIEF, t, "VizWiz") for _, p, t in vizwiz[test_size - test_docci:]]
    rng.shuffle(train)
    for name, rows in (("train", train), ("test", test)):
        with open(os.path.join(data_dir, f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for picture, question, answer, source in rows:
                f.write(json.dumps({"picture": picture, "question": question, "answer": answer,
                                    "source": source}) + "\n")
    return len(train), len(test)


def read_rows(path):
    """The rows of a .jsonl file."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ----------------------------------------------------------------- the model in memory

def load_model(folder, four_bit=True, adapter=None, trainable=False):
    """(model, processor): the model from folder (in 4-bit form unless four_bit is False), with the add-on at
    adapter when given, or a new trainable add-on when trainable."""
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    kwargs = {"dtype": torch.bfloat16 if torch.cuda.is_available() else torch.float32}
    if four_bit:
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                           bnb_4bit_use_double_quant=True,
                                                           bnb_4bit_compute_dtype=torch.bfloat16)
        kwargs["device_map"] = {"": 0}
    model = AutoModelForImageTextToText.from_pretrained(folder, **kwargs)
    processor = AutoProcessor.from_pretrained(folder)
    if trainable:
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        if four_bit:
            model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
        else:
            model.gradient_checkpointing_enable()
            model.enable_input_require_grads()
        config = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                            target_modules=r".*language_model.*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|"
                                           r"down_proj)")
        model = get_peft_model(model, config)
    elif adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    return model, processor


def free():
    """Give the graphics card memory of a model already let go of (del) back before the next one is loaded."""
    import gc

    import torch
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def messages(row, with_answer):
    """The conversation of one picture in the chat form the model knows (the toolkit's SYSTEM text, the picture and
    the question, and the human description as the answer when with_answer)."""
    from PIL import Image
    conversation = [{"role": "system", "content": [{"type": "text", "text": SYSTEM}]},
                    {"role": "user", "content": [{"type": "image", "image": Image.open(row["picture"])},
                                                 {"type": "text", "text": row["question"]}]}]
    if with_answer:
        conversation.append({"role": "assistant", "content": [{"type": "text", "text": row["answer"]}]})
    return conversation


def encode(processor, row, device):
    """The model's input for one training picture, with labels only on the answer (the rest -100, not learned)."""
    full = processor.apply_chat_template(messages(row, True), tokenize=True, return_dict=True, return_tensors="pt")
    prompt = processor.apply_chat_template(messages(row, False), tokenize=True, return_dict=True,
                                           add_generation_prompt=True, return_tensors="pt")
    labels = full["input_ids"].clone()
    labels[:, :prompt["input_ids"].shape[1]] = -100
    full["labels"] = labels
    return {k: v.to(device) for k, v in full.items()}


def describe(model, processor, row, device):
    """The model's description of one test picture (greedy, at most 350 words' worth for the detailed question)."""
    import torch
    inputs = processor.apply_chat_template(messages(row, False), tokenize=True, return_dict=True,
                                           add_generation_prompt=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    limit = 450 if row["question"] == DETAILED else 60
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=limit, do_sample=False)
    return processor.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


# ----------------------------------------------------------------- 4 and 6. the test

def words_of(text):
    """The words of a text in lower case, without punctuation."""
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def rouge_l(reference, text):
    """ROUGE-L F score of text against reference (0 to 1): the longest run of words, in order but not necessarily
    next to each other, that both share, as a share of each one's length (precision and recall), combined."""
    a, b = words_of(reference), words_of(text)
    if not a or not b:
        return 0.0
    previous = [0] * (len(b) + 1)
    for word in a:
        current = [0]
        for j, other in enumerate(b, 1):
            current.append(previous[j - 1] + 1 if word == other else max(previous[j], current[j - 1]))
        previous = current
    common = previous[-1]
    if not common:
        return 0.0
    precision, recall = common / len(b), common / len(a)
    return 2 * precision * recall / (precision + recall)


def run_test(model, processor, rows, out_path, device, label):
    """Describe each test picture, score it, write out_path (.jsonl) and return the mean scores {"DOCCI", "VizWiz",
    "all"}. Already written descriptions are kept (a restarted test carries on)."""
    model.eval()
    done = read_rows(out_path) if os.path.exists(out_path) else []
    with open(out_path, "a", encoding="utf-8") as f:
        for number, row in enumerate(rows[len(done):], len(done) + 1):
            text = describe(model, processor, row, device)
            result = dict(row, description=text, score=rouge_l(row["answer"], text))
            f.write(json.dumps(result) + "\n")
            f.flush()
            done.append(result)
            if number % 10 == 0 or number == len(rows):
                say(f"    {label}: {number} of {len(rows)} pictures described")
    return scores(done)


def scores(results):
    """The mean ROUGE-L of results, per source and all together."""
    out = {}
    for source in ("DOCCI", "VizWiz"):
        values = [r["score"] for r in results if r["source"] == source]
        if values:
            out[source] = sum(values) / len(values)
    out["all"] = sum(r["score"] for r in results) / max(len(results), 1)
    return out


# ----------------------------------------------------------------- 5. training

def train(model, processor, rows, adapter_dir, device, epochs=1, rate=1e-4, accumulate=8):
    """Train the add-on over rows (one pass), saving it with the optimizer every SAVE_EVERY pictures into
    adapter_dir/checkpoint, and carrying on from there when started again; the finished add-on goes into
    adapter_dir/final. Returns the training time in seconds, over every start."""
    import torch
    checkpoint = os.path.join(adapter_dir, "checkpoint")
    final = os.path.join(adapter_dir, "final")
    params = [p for p in model.parameters() if p.requires_grad]
    try:
        import bitsandbytes as bnb
        optimizer = bnb.optim.PagedAdamW8bit(params, lr=rate, weight_decay=0.0)
    except Exception:  # noqa: BLE001 - no bitsandbytes (the self-test on a processor)
        optimizer = torch.optim.AdamW(params, lr=rate)
    total = len(rows) * epochs
    steps = math.ceil(total / accumulate)
    warmup = max(1, steps // 30)

    def rate_at(step):
        """Warm up, then a cosine fall to a tenth."""
        if step < warmup:
            return (step + 1) / warmup
        progress = (step - warmup) / max(1, steps - warmup)
        return 0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * progress))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, rate_at)
    position, earlier = 0, 0.0
    if os.path.exists(os.path.join(checkpoint, "progress.json")):
        with open(os.path.join(checkpoint, "progress.json"), encoding="utf-8") as f:
            progress = json.load(f)
        position, earlier = progress["pictures"], progress.get("seconds", 0.0)
        from peft import set_peft_model_state_dict  # noqa: I001
        from safetensors.torch import load_file
        set_peft_model_state_dict(model, load_file(os.path.join(checkpoint, "adapter_model.safetensors")))
        state = torch.load(os.path.join(checkpoint, "optimizer.pt"), map_location="cpu", weights_only=False)
        optimizer.load_state_dict(state["optimizer"])
        scheduler.load_state_dict(state["scheduler"])
        say(f"  Carrying on from picture {position} of {total}.")
    model.train()
    start, started_at, losses = time.time(), position, []
    order = [rows[i % len(rows)] for i in range(total)]
    for index in range(position, total):
        row = order[index]
        try:
            batch = encode(processor, row, device)
            loss = model(**batch).loss / accumulate
            loss.backward()
            losses.append(loss.item() * accumulate)
        except torch.cuda.OutOfMemoryError:
            optimizer.zero_grad(set_to_none=True)
            torch.cuda.empty_cache()
            say(f"    picture {index + 1} was too big for the card's memory and is skipped")
        if (index + 1) % accumulate == 0 or index + 1 == total:
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)
        if (index + 1) % SAVE_EVERY == 0 or index + 1 == total:
            os.makedirs(checkpoint, exist_ok=True)
            model.save_pretrained(checkpoint)
            torch.save({"optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict()},
                       os.path.join(checkpoint, "optimizer.pt"))
            with open(os.path.join(checkpoint, "progress.json"), "w", encoding="utf-8") as f:
                json.dump({"pictures": index + 1, "seconds": earlier + time.time() - start}, f)
            per = (time.time() - start) / (index + 1 - started_at)
            recent = sum(losses[-SAVE_EVERY:]) / max(len(losses[-SAVE_EVERY:]), 1)
            say(f"    {index + 1} of {total} pictures trained ({(index + 1) * 100 // total} percent); about "
                f"{duration(per * (total - index - 1))} left. Error {recent:.3f} (lower is better). Saved.")
    model.save_pretrained(final)
    return earlier + time.time() - start


# ----------------------------------------------------------------- 7. the report and the zip

def verdict(before, after):
    """(better, words): better is True when the add-on raised the score of both kinds of picture, by at least 0.01
    together and lowered neither by more than 0.005."""
    gain = after["all"] - before["all"]
    worse = [k for k in ("DOCCI", "VizWiz") if k in before and after.get(k, 0) < before[k] - 0.005]
    if gain >= 0.01 and not worse:
        return True, f"BETTER: the trained model's descriptions are closer to the human ones (+{gain:.3f})."
    if worse:
        return False, ("NOT BETTER: the trained model got worse on " + " and ".join(worse) +
                       " pictures. Send the result anyway; it will not be published as it is.")
    return False, f"NO CLEAR CHANGE (+{gain:.3f}). Send the result anyway; it will not be published as it is."


def write_report(path, info, before, after, before_rows, after_rows):
    """report.txt: what was trained, the scores, the verdict and 15 examples (the human description, before and
    after), in plain words."""
    better, words = verdict(before, after)
    lines = ["Picture Model Training Kit: report", "",
             f"Finished: {datetime.datetime.now():%d %B %Y at %H:%M}",
             f"Model: {info['model']} (commit {info['revision'][:12]})",
             f"Graphics card: {info['card']}",
             f"Training pictures: {info['train']} (DOCCI and VizWiz); test pictures: {info['test']}",
             f"Training time: {duration(info['seconds'])}", "",
             "RESULT: " + words, "",
             "Scores (ROUGE-L, from 0 to 1: how close each description is to a person's; higher is better):"]
    for key, name in (("DOCCI", "Detailed descriptions (DOCCI)"), ("VizWiz", "One-sentence descriptions of photos "
                                                                            "taken by blind people (VizWiz)"),
                      ("all", "All test pictures")):
        if key in before:
            lines.append(f"  {name}: before {before[key]:.3f}, after {after[key]:.3f}")
    lines += ["", "Examples (each: the person's description, the model before training, after training):", ""]
    pick = before_rows[:10] + [r for r in before_rows if r["source"] == "VizWiz"][:5]
    after_by_picture = {r["picture"]: r for r in after_rows}
    for number, row in enumerate(pick, 1):
        later = after_by_picture.get(row["picture"], {})
        lines += [f"Example {number} ({row['source']}):",
                  f"  Person: {row['answer']}",
                  f"  Before: {row['description']}",
                  f"  After: {later.get('description', '')}", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return better, words


def package(work, model_key, final, report, info):
    """The zip to send: the add-on, report.txt, scores.json and settings; returns its path."""
    folder = os.path.join(HERE, "result")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"picture-training-{model_key}-{datetime.date.today():%Y-%m-%d}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in os.listdir(final):
            z.write(os.path.join(final, name), f"adapter/{name}")
        z.write(report, "report.txt")
        z.writestr("scores.json", json.dumps(info, indent=1))
        z.write(LOG, "training-log.txt")
    return path


# ----------------------------------------------------------------- all steps

def main(argv=None):
    """Run the steps (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", choices=sorted(MODELS), default="4b")
    parser.add_argument("--limit", type=int, default=0, help="train on at most this many pictures")
    parser.add_argument("--test-size", type=int, default=100)
    args = parser.parse_args(argv)
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    work = os.path.join(HERE, "work")
    os.makedirs(work, exist_ok=True)
    state = State(work)
    keep_awake(True)
    say("")
    say(f"Picture Model Training Kit started for the {args.model.upper()} model.")
    say("Windows will not go to sleep while this runs; the screen may turn off. You can close this window at any time "
        "and start the kit again later: it carries on where it stopped.")
    say("Step 1 of 7: checking the graphics card and the disk.")
    card, _ = check_computer(args.model, work)
    say(f"Step 2 of 7: downloading the {args.model.upper()} model (about {9 if args.model == '4b' else 17} GB; "
        "carries on if stopped).")
    folder = download_model(args.model, work)
    if not state.done("data"):
        say("Step 3 of 7: downloading the pictures and their descriptions (about 11 GB) and making them smaller.")
        train_count, test_count = prepare_data(work, args.test_size)
        state.mark("data", {"train": train_count, "test": test_count})
    else:
        say("Step 3 of 7: the pictures are ready (done before).")
    data_dir = os.path.join(work, "data")
    train_rows = read_rows(os.path.join(data_dir, "train.jsonl"))
    test_rows = read_rows(os.path.join(data_dir, "test.jsonl"))
    if args.limit:
        train_rows = train_rows[:args.limit]
    device = "cuda"
    results = os.path.join(work, f"results-{args.model}")
    os.makedirs(results, exist_ok=True)
    before_path, after_path = os.path.join(results, "before.jsonl"), os.path.join(results, "after.jsonl")
    if not state.done(f"before-{args.model}"):
        say(f"Step 4 of 7: testing the model before training on {len(test_rows)} pictures (about 20 minutes).")
        model, processor = load_model(folder)
        before = run_test(model, processor, test_rows, before_path, device, "before training")
        state.mark(f"before-{args.model}", before)
        del model, processor
        free()
    else:
        say("Step 4 of 7: the test before training is done (done before).")
    before = state.data[f"before-{args.model}"]
    say(f"  Score before training: {before['all']:.3f}.")
    adapter_dir = os.path.join(work, f"adapter-{args.model}")
    final = os.path.join(adapter_dir, "final")
    if not state.done(f"train-{args.model}"):
        say(f"Step 5 of 7: training on {len(train_rows)} pictures. This is the long part, several hours; the time "
            f"left is said every {SAVE_EVERY} pictures.")
        model, processor = load_model(folder, trainable=True)
        seconds = train(model, processor, train_rows, adapter_dir, device)
        state.mark(f"train-{args.model}", {"seconds": seconds})
        del model, processor
        free()
    else:
        say("Step 5 of 7: training is done (done before).")
    if not state.done(f"after-{args.model}"):
        say(f"Step 6 of 7: testing the trained model on the same {len(test_rows)} pictures.")
        model, processor = load_model(folder, adapter=final)
        after = run_test(model, processor, test_rows, after_path, device, "after training")
        state.mark(f"after-{args.model}", after)
        del model, processor
        free()
    after = state.data[f"after-{args.model}"]
    say(f"  Score after training: {after['all']:.3f} (before: {before['all']:.3f}).")
    say("Step 7 of 7: writing the report and the zip to send.")
    repo, revision, _ = MODELS[args.model]
    info = {"model": repo, "revision": revision, "card": card, "train": len(train_rows), "test": len(test_rows),
            "seconds": state.data[f"train-{args.model}"]["seconds"], "before": before, "after": after,
            "settings": {"lora_r": 16, "lora_alpha": 32, "rate": 1e-4, "accumulate": 8, "four_bit": True,
                         "long_side": LONG_SIDE, "system": SYSTEM, "detailed": DETAILED, "brief": BRIEF}}
    report = os.path.join(HERE, f"report-{args.model}.txt")
    _, words = write_report(report, info, before, after, read_rows(before_path), read_rows(after_path))
    path = package(work, args.model, final, report, info)
    keep_awake(False)
    say("")
    say("FINISHED. " + words)
    say(f"The report is {report}")
    say(f"The file to send is {path}")
    say("Tell Claude that the training has finished; you will be told how to send the file.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        say("Stopped by you. Start the kit again to carry on.")
        sys.exit(1)
