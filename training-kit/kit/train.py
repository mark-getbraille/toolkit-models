"""Picture Model Training Kit: teach the Digital Accessibility Toolkit's picture model (huihui-ai's uncensored
Qwen3-VL) to describe pictures the way a blind reader needs, on your own computer's NVIDIA graphics card.

Started by "Start Training.cmd" (4B model), "Start Training 8B.cmd", or the "with Wikipedia" versions of both.
Every step says what it does in plain words, on the screen and in training-log.txt. A step that is finished is not
done again: if the computer restarts or the window is closed, start it again and it carries on where it stopped
(training itself from its last save, every 200 pictures).

The steps:
  1. check the graphics card (NVIDIA, enough memory) and the free disk space;
  2. download the model at a pinned commit from Hugging Face;
  3. download the described pictures of every collection in sources.py (photos described in detail, photos taken
     by blind people, questions blind people asked, pictures with text to read, museum descriptions written for
     accessibility, the Met's and Europeana's museum objects, NASA's pictures, and with --with-wikipedia Wikipedia's
     alt text) and make them smaller; a few of each collection are kept back for the test;
  4. test the model before training: it answers every test picture, and each answer is scored against the
     person's (ROUGE-L, from 0 to 1: how much of the person's wording it shares);
  5. train a small add-on (a LoRA adapter of the language part; the model itself stays as it is), one pass over the
     training pictures, on the model loaded in 4-bit form so it fits a 12 to 16 GB card;
  6. test again with the add-on, and write the report: the scores before and after for each collection, whether it
     got better, and examples to read;
  7. put the add-on, the report, the scores and ATTRIBUTION.txt (the credits and licences) in one zip in the
     "result" folder, for sending.

The questions are the toolkit's own where it has them (vision/vlm.py PICTURE: "Describe this picture in detail."),
with its SYSTEM text; museum names and NASA captions have their own questions, so they add knowledge without
changing how pictures are described.

Command line (the .cmd files pass these): --model 4b|8b, --size quick|normal|full, --with-wikipedia (the add-on is
then CC BY-SA 4.0), --limit N (train on at most N pictures).

Content choices: --with-nudity also learns from non-sexual nudes in art, and --with-medical from medical and anatomy
pictures (collections marked so in sources.py; without the choice they are left out, in a follow-up too). The report
and ATTRIBUTION.txt say which choices were used, and a training with them gets its own name ("4b-nudity-medical").

Personal-use collections (sources.py, groups "noncommercial" and "research", from personal_sources.py):
--personal-noncommercial also learns from collections under non-commercial licences (CC BY-NC, BY-NC-SA, BY-NC-ND),
and --personal-research from research-only ("academic use") collections, which also needs --accept-research-terms
(the person has read their terms). The add-on is then for PERSONAL USE ONLY: its name gets "-personal", the report
starts with a warning listing those collections with their licence and terms page, ATTRIBUTION.txt lists them under
their own heading, and the zip gets PERSONAL-USE-ONLY.txt. A follow-up never carries on from such an add-on unless
the same choice is made again.

Your own pictures (own_data.py): --own FOLDER adds the described pictures in FOLDER to the collections, and with
--own-only the training uses them alone. About 1 in 20 of them is kept back for the test. The add-on is then for
personal use only, which the report and ATTRIBUTION.txt say.

The picture library (--library FOLDER, which the program sets): every collection's pictures, their descriptions,
larger copies of the pictures (up to 2,048 pixels, for future models), the original downloads and the Hugging Face
files are kept there for good, so a later training (of this model or another) never downloads them again. Pictures
an earlier run kept in the kit's work folder are moved there once, and their lists rewritten to the new place.

A follow-up run (--continue): carries on from the newest finished add-on instead of starting a new one, and trains
only on the collections that run did not have (or the ones named with --collections), mixed with a share of the
earlier pictures (--replay, 0.25 by default: one earlier picture for every four new ones) so the model does not
forget what it learned. Its "before" test is the earlier add-on, on every collection's test pictures, so the report
shows whether anything got worse. It takes hours, not days.
"""


import argparse
import ctypes
import datetime
import json
import math
import os
import re
import shutil
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # the kit folder
LOG = os.path.join(HERE, "training-log.txt")

MODELS = {   # the toolkit's uncensored picture models (app/toolkit/vision/engines/models.py), pinned
    "4b": ("huihui-ai/Huihui-Qwen3-VL-4B-Instruct-abliterated", "ce72a7c22aacb493fb94478de3bfbe834c61844a", 11),
    "8b": ("huihui-ai/Huihui-Qwen3-VL-8B-Instruct-abliterated", "b47a0690b22eaf1d9a63874d967a03781c90f9cf", 15),
}   # key: (Hugging Face repository, commit, the least graphics card memory in GB)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402 - the collections, beside this file

# The toolkit's own words (vision/vlm.py SYSTEM), so the add-on learns with the instructions the program sends.
SYSTEM = "The user is blind. Never describe anyone who may be under 18 in a sexual way."
DETAILED, BRIEF = sources.DETAILED, sources.BRIEF

SAVE_EVERY = 200           # training pictures between saves
FREE_GB_NEEDED = {"4b": 90, "8b": 110}
ANSWER_TOKENS = {sources.DETAILED: 450, sources.NARRATE: 250, sources.ALT_TEXT: 160}    # others: 100


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

LIBRARY = None          # the picture library folder (--library), or None: everything in the work folder


def data_root(work):
    """Where the prepared pictures and their lists are: the library's "data" folder, or the work folder's."""
    return os.path.join(LIBRARY, "data") if LIBRARY else os.path.join(work, "data")


def downloads_root(work):
    """Where downloads (archives, data files, packs) go: the library's "downloads" folder, or the work folder."""
    return os.path.join(LIBRARY, "downloads") if LIBRARY else work


def open_library(work, library):
    """Use library as the picture library: make its folders, point the downloads and the Hugging Face files there,
    and move what an earlier run kept in the work folder (data, hf-cache) there once, rewriting the pictures' places
    in every list."""
    global LIBRARY
    LIBRARY = os.path.abspath(library)
    for name in ("data", "originals", "downloads"):
        os.makedirs(os.path.join(LIBRARY, name), exist_ok=True)
    sources.ARCHIVE_DIR = os.path.join(LIBRARY, "originals")
    sources.DATA_DIR = os.path.join(LIBRARY, "data")
    sources.KEEP_DOWNLOADS = True
    os.environ["HF_HOME"] = os.path.join(LIBRARY, "hf-cache")
    old_data, new_data = os.path.join(work, "data"), os.path.join(LIBRARY, "data")
    if os.path.isdir(old_data) and os.listdir(old_data):
        say(f"Moving the pictures downloaded before into the picture library {LIBRARY} (once; this can take a while).")
        for name in os.listdir(old_data):
            target = os.path.join(new_data, name)
            if not os.path.exists(target):
                shutil.move(os.path.join(old_data, name), target)
        for name in os.listdir(new_data):
            if name.endswith(".jsonl"):
                path = os.path.join(new_data, name)
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                old = json.dumps(old_data)[1:-1]            # the folder as written inside the JSON lines
                if old in text:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text.replace(old, json.dumps(new_data)[1:-1]))
        shutil.rmtree(old_data, ignore_errors=True)
        say("  Moved.")
    old_hf = os.path.join(work, "hf-cache")
    if os.path.isdir(old_hf) and not os.path.exists(os.environ["HF_HOME"]):
        say("Moving the Hugging Face files downloaded before into the picture library (once).")
        shutil.move(old_hf, os.environ["HF_HOME"])


def prepare_data(work, state, size, with_wikipedia, keys=None, with_nudity=False, with_medical=False,
                 with_noncommercial=False, with_research=False):
    """Prepare every chosen collection once (each one remembered as done in state, so a restarted kit skips it);
    writes data/train.jsonl (shuffled) and data/test.jsonl and returns (training rows, test rows). A collection that
    cannot be downloaded now is said and left out, so one broken website never stops the training. with_nudity and
    with_medical: the content choices; with_noncommercial and with_research: the personal-use choices (see
    sources.chosen)."""
    import random
    data_dir = data_root(work)
    os.makedirs(data_dir, exist_ok=True)
    train_rows, test_rows = [], []
    chosen = [s for s in sources.chosen(with_wikipedia, with_nudity=with_nudity, with_medical=with_medical,
                                        with_noncommercial=with_noncommercial, with_research=with_research)
              if keys is None or s.key in keys]
    for number, source in enumerate(chosen, 1):
        say(f"  Collection {number} of {len(chosen)}: {source.name} (downloads {source.download}).")
        try:
            train, test = sources.prepare_source(source, data_dir, downloads_root(work), size)
        except Exception as e:  # noqa: BLE001 - one collection failing does not stop the others
            say(f"    This collection could not be prepared now ({str(e).splitlines()[0][:200]}); it is left out. "
                "Start the kit again later to try it again.")
            continue
        state.mark(f"data-{source.key}-{size}", {"train": len(train), "test": len(test)})
        say(f"    Ready: {len(train)} pictures for training, {len(test)} for the test.")
        train_rows += train
        test_rows += test
    random.Random(5).shuffle(train_rows)
    suffix = "-follow-up" if keys else ""
    for name, rows in (("train", train_rows), ("test", test_rows)):
        with open(os.path.join(data_dir, f"{name}{suffix}.jsonl"), "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
    return train_rows, test_rows


def own_rows(work, folder):
    """(training rows, test rows) of the person's own pictures in folder (own_data.py), with their smaller copies
    in work/own-pictures; the summary and any problems are said. Also returns the folder's short code (own_data.
    folder_tag), which names the training."""
    import own_data
    copies = os.path.join(work, "own-pictures", own_data.folder_tag(folder, []))
    say(f"  Your own pictures: reading {folder} and making the training copies.")
    rows, _problems, summary = own_data.check_folder(folder, copies=copies, report=say)
    for line in summary.splitlines():
        say("    " + line)
    train_rows = [r for r in rows if r["split"] != "test"]
    test_rows = [r for r in rows if r["split"] == "test"]
    return train_rows, test_rows, own_data.folder_tag(folder, rows)


ASK_COUNTRY = "Which country might this photo be from?"
ASK_REGION = "Which part of the world might this photo be from?"
ASK_MADE = "Where was this object made?"
PLACE_EVERY = 5            # about one picture in this many with a place gets a place question


def place_rows(rows):
    """Extra training rows about where pictures are from (never test rows): for about one in PLACE_EVERY pictures
    with a place, chosen by the picture's name so a restart picks the same ones,
      - a photo (place_kind "photo" or none) from a collection whose photos show the place itself
        (sources.PLACE_VISIBLE: streets, homes, shops, landscapes): "Which country might this photo be from?" ->
        "It was taken in Japan." (the country only; "Which part of the world ..." for a region such as East Asia);
      - an object whose record says where it was made (place_kind "origin"): "Where was this object made?" ->
        "It was made in Kyoto, Japan."
    The place is never put into a description's answer: the model must not learn to state what it cannot see."""
    import zlib
    out, seen = [], set()
    for row in rows:
        place, kind, picture = row.get("place"), row.get("place_kind") or "photo", row.get("picture")
        if not place or not picture or picture in seen or row.get("split") == "test":
            continue
        if zlib.crc32(os.path.basename(picture).encode("utf-8")) % PLACE_EVERY:
            continue
        if kind == "photo" and row.get("source") in sources.PLACE_VISIBLE:
            country = sources.place_country(place)
            question = ASK_REGION if sources.is_region(place) else ASK_COUNTRY
            answer = f"It was taken in {sources.place_words(country)}."
        elif kind == "origin":
            question, answer = ASK_MADE, f"It was made in {sources.place_words(place)}."
        else:
            continue
        seen.add(picture)
        out.append({"picture": picture, "question": question, "answer": answer, "split": "no-test",
                    "source": row.get("source"), "place": place, **({"place_kind": kind} if kind != "photo" else {})})
    return out


def place_counts(rows):
    """(pictures with a place, place questions added) among training rows, for the report."""
    asked = (ASK_COUNTRY, ASK_REGION, ASK_MADE)
    pictures = {r["picture"] for r in rows if r.get("place") and r.get("picture")}
    return len(pictures), sum(1 for r in rows if r.get("question") in asked and r.get("split") == "no-test")


def read_rows(path):
    """The rows of a .jsonl file."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ----------------------------------------------------------------- the model in memory

def load_model(folder, four_bit=True, adapter=None, trainable=False):
    """(model, processor): the model from folder (in 4-bit form unless four_bit is False), with the add-on at
    adapter when given (trainable: it is trained further, for a follow-up run), or a new trainable add-on when
    trainable."""
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
        if adapter:
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, adapter, is_trainable=True)
        else:
            config = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                                target_modules=r".*language_model.*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|"
                                               r"up_proj|down_proj)")
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
    """The model's answer for one test picture (greedy; at most ANSWER_TOKENS for its question, 100 otherwise)."""
    import torch
    inputs = processor.apply_chat_template(messages(row, False), tokenize=True, return_dict=True,
                                           add_generation_prompt=True, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    limit = ANSWER_TOKENS.get(row["question"], 100)
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
    """The mean ROUGE-L of results for each collection (its key) and all together ("all")."""
    out = {}
    for key in sorted({r["source"] for r in results}):
        values = [r["score"] for r in results if r["source"] == key]
        out[key] = sum(values) / len(values)
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

OWN_NOTE = ("Includes your own pictures: for personal use only; do not publish this add-on unless you own the rights "
            "to those pictures.")


def source_name(key):
    """The plain name of a collection key, for the report ("own": the person's own pictures)."""
    if key == "own":
        return "Your own pictures"
    return next((s.name for s in sources.SOURCES if s.key == key), key)


def content_lines(info):
    """The content choices and, when used, the note about the person's own pictures, as lines for the report and
    ATTRIBUTION.txt. A choice made whose collections could not be downloaded is said too."""
    lines = [sources.content_choices_text(info.get("with_nudity", False), info.get("with_medical", False))]
    for content, words in (("nudity", "Art with nudity was"), ("medical", "Medical and anatomy pictures were")):
        if info.get(f"with_{content}") and not any(sources.content_of(k) == content for k in info["collections"]):
            lines.append(f"  ({words} chosen, but none of those pictures could be downloaded.)")
    if info.get("own_pictures"):
        lines.append(OWN_NOTE + f" ({info['own_pictures']} questions and answers about your own pictures"
                     + (", trained on alone" if info.get("own_only") else "") + ".)")
    return lines


def personal_chosen(info):
    """True when a personal-use choice was made (non-commercial or research-only collections), or a personal-use
    collection is among those learned from: the add-on is then for personal use only."""
    return bool(info.get("with_noncommercial") or info.get("with_research") or
                any(sources.is_personal(s) for s in sources.SOURCES if s.key in info.get("collections", ())))


def personal_lines(info):
    """The PERSONAL USE ONLY block that starts the report (and PERSONAL-USE-ONLY.txt): the warning, then each
    personal-use collection learned from with its licence and terms page; [] when no personal-use choice was made."""
    if not personal_chosen(info):
        return []
    lines = [sources.PERSONAL_WARNING]
    used = [s for s in sources.SOURCES if sources.is_personal(s) and s.key in info.get("collections", ())]
    if used:
        lines.append("The personal-use collections it learned from:")
        for source in used:
            kind = "research-only" if source.group == "research" else "non-commercial"
            lines += [f"  - {source.name} ({kind})", f"    Licence: {source.licence}",
                      f"    Terms: {sources.terms_link(source) or 'see the licence above'}"]
    else:
        lines.append("(Personal-use collections were chosen, but none of them could be downloaded or none are in this "
                     "kit. The add-on is still labelled for personal use only.)")
    return lines


def verdict(before, after, counts=None):
    """(better, words): better when the add-on raised the score of all test pictures by at least 0.01 and lowered no
    collection with 10 or more test pictures by more than 0.03 (smaller collections vary too much to judge)."""
    gain = after["all"] - before["all"]
    worse = [k for k in before if k != "all" and (counts or {}).get(k, 10) >= 10 and
             after.get(k, 0) < before[k] - 0.03]
    if gain >= 0.01 and not worse:
        return True, f"BETTER: the trained model's answers are closer to the people's (+{gain:.3f})."
    if worse:
        return False, ("NOT BETTER: the trained model got worse on " + "; ".join(source_name(k) for k in worse) +
                       ". Send the result anyway; it will not be published as it is.")
    return False, f"NO CLEAR CHANGE (+{gain:.3f}). Send the result anyway; it will not be published as it is."


def attribution(chosen_keys, share_alike, info=None):
    """ATTRIBUTION.txt: the licence of the add-on, the content choices (info, when given) and the credit of every
    collection it learned from."""
    personal = personal_chosen(dict(info or {}, collections=chosen_keys))
    licence = ("CC BY-SA 4.0 (it learned from Wikipedia's CC BY-SA text)" if share_alike
               else "Apache License 2.0, with the credits below (CC BY sources)")
    if personal:
        licence = "PERSONAL USE ONLY (see the personal-use collections below); otherwise " + licence
    lines = ["Picture description add-on for Qwen3-VL (huihui-ai's abliterated version, Apache License 2.0)", "",
             "Licence of this add-on: " + licence, "",
             "It learned from these collections of described pictures:"]
    for source in sources.SOURCES:
        if source.key in chosen_keys and not sources.is_personal(source):
            lines += [f"- {source.credit}", f"  Licence: {source.licence}"]
    if "own" in chosen_keys:
        lines += ["- The trainer's own pictures and descriptions (not credited here; not for publishing)."]
    if personal:
        # The personal-use collections under their own heading, with their terms.
        lines += ["", "Personal-use collections (non-commercial licences or research-only terms):",
                  sources.PERSONAL_WARNING]
        used = [s for s in sources.SOURCES if sources.is_personal(s) and s.key in chosen_keys]
        for source in used:
            lines += [f"- {source.credit}", f"  Licence: {source.licence}",
                      f"  Terms: {sources.terms_link(source) or 'see the licence above'}"]
        if not used:
            lines.append("- (chosen, but none of them could be downloaded)")
    if info:
        lines += [""] + content_lines(info)
    return "\n".join(lines) + "\n"


def place_lines(info):
    """The report's line about where the pictures are from (how many training pictures had a place)."""
    pictures, asked = info.get("places") or (0, 0)
    if not pictures:
        return []
    return [f"Pictures with a place (where in the world they are from): {pictures}; {asked} training questions asked "
            "where a photo was taken or an object made (never in the test)."]


def write_report(path, info, before, after, before_rows, after_rows):
    """The report: what was trained, the scores for each collection, the verdict and examples (the person's answer,
    the model's before and after: two from each collection), in plain words."""
    counts = {}
    for row in before_rows:
        counts[row["source"]] = counts.get(row["source"], 0) + 1
    better, words = verdict(before, after, counts)
    block = personal_lines(info)                     # PERSONAL USE ONLY first, when chosen
    lines = [*block, *([""] if block else []), "Picture Model Training Kit: report", "",
             f"Finished: {datetime.datetime.now():%d %B %Y at %H:%M}",
             f"Model: {info['model']} (commit {info['revision'][:12]})",
             f"Graphics card: {info['card']}",
             f"Training pictures: {info['train']}; test pictures: {info['test']}; size: {info['size']}"
             + ("; with Wikipedia (the add-on is CC BY-SA 4.0)" if info["share_alike"] else ""),
             f"Training time: {duration(info['seconds'])}", *content_lines(info), *place_lines(info), "",
             "RESULT: " + words, "",
             "Scores (ROUGE-L, from 0 to 1: how close each answer is to a person's; higher is better):"]
    for key in [k for k in before if k != "all"] + ["all"]:
        name = "All test pictures" if key == "all" else f"{source_name(key)} ({counts.get(key, 0)} pictures)"
        lines.append(f"  {name}: before {before[key]:.3f}, after {after.get(key, 0):.3f}")
    lines += ["", "Examples (each: the question, the person's answer, the model before training, after training):",
              ""]
    pick = []
    for key in before:
        pick += [r for r in before_rows if r["source"] == key][:2]
    after_by_picture = {(r["picture"], r["question"]): r for r in after_rows}
    for number, row in enumerate(pick, 1):
        later = after_by_picture.get((row["picture"], row["question"]), {})
        lines += [f"Example {number} ({source_name(row['source'])}):",
                  f"  Question: {row['question']}",
                  f"  Person: {row['answer']}",
                  f"  Before: {row['description']}",
                  f"  After: {later.get('description', '')}", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return better, words


def package(model_key, final, report, info, tag):
    """The zip to send: the add-on, the report, scores.json, ATTRIBUTION.txt and the log; returns its path."""
    folder = os.path.join(HERE, "result")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"picture-training-{model_key}{tag}-{datetime.date.today():%Y-%m-%d}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in os.listdir(final):
            z.write(os.path.join(final, name), f"adapter/{name}")
        z.write(report, "report.txt")
        z.writestr("scores.json", json.dumps(info, indent=1))
        z.writestr("ATTRIBUTION.txt", attribution(info["collections"], info["share_alike"], info))
        if personal_chosen(info):
            z.writestr("PERSONAL-USE-ONLY.txt", "\n".join(personal_lines(info)) + "\n")
        z.write(LOG, "training-log.txt")
    return path


# ----------------------------------------------------------------- a follow-up run

def finished_runs(work, state):
    """[(run name, its add-on folder)] of the runs that finished training, newest last."""
    runs = []
    for name in state.data:
        if name.startswith("train-"):
            run = name[len("train-"):]
            final = os.path.join(work, f"adapter-{run}", "final")
            if os.path.isdir(final):
                runs.append((os.path.getmtime(final), run, final))
    return [(run, final) for _, run, final in sorted(runs)]


def prepared_collections(state):
    """{collection key: size} of every collection prepared before (from its "data-<key>-<size>" mark)."""
    found = {}
    for name in state.data:
        if name.startswith("data-"):
            key, _, size = name[len("data-"):].rpartition("-")
            if key and size in sources.SIZES:
                found[key] = size
    return found


def follow_up_rows(work, state, plan, with_wikipedia, size, replay, with_nudity=False, with_medical=False,
                   with_noncommercial=False, with_research=False):
    """(training rows, test rows) of a follow-up run: the new collections' pictures, a share (replay) of the earlier
    collections' pictures, and every collection's test pictures. Collections whose content or personal-use group was
    not chosen (with_nudity, with_medical, with_noncommercial, with_research) are left out, also the earlier ones."""
    import random
    choices = {"with_nudity": with_nudity, "with_medical": with_medical, "with_noncommercial": with_noncommercial,
               "with_research": with_research}
    new_train, new_test = prepare_data(work, state, size, with_wikipedia, keys=set(plan["new"]), **choices)
    allowed = {s.key for s in sources.chosen(with_wikipedia, **choices)}
    old_train, old_test = [], []
    data_dir = data_root(work)
    for key, old_size in plan["old"].items():
        source = next((s for s in sources.SOURCES if s.key == key), None)
        if source is None or key not in allowed or \
                not os.path.exists(os.path.join(data_dir, f"{key}-{old_size}.jsonl")):
            continue
        train, test = sources.prepare_source(source, data_dir, downloads_root(work), old_size)
        old_train += train
        old_test += test
    random.Random(9).shuffle(old_train)
    mixed = new_train + old_train[:int(len(new_train) * replay)]
    random.Random(10).shuffle(mixed)
    return mixed, new_test + old_test


# ----------------------------------------------------------------- all steps

def main(argv=None):
    """Run the steps (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", choices=sorted(MODELS), default="4b")
    parser.add_argument("--size", choices=sorted(sources.SIZES), default="normal")
    parser.add_argument("--with-wikipedia", action="store_true", help="also learn from Wikipedia (CC BY-SA 4.0)")
    parser.add_argument("--limit", type=int, default=0, help="train on at most this many pictures")
    parser.add_argument("--library", default="", help="the permanent picture library folder")
    parser.add_argument("--continue", dest="follow_up", action="store_true",
                        help="carry on from the newest finished add-on with the collections it did not have")
    parser.add_argument("--collections", default="", help="with --continue: the collection keys to add (commas)")
    parser.add_argument("--replay", type=float, default=0.25, help="with --continue: share of earlier pictures")
    parser.add_argument("--with-nudity", action="store_true", help="also learn from non-sexual nudes in art")
    parser.add_argument("--with-medical", action="store_true", help="also learn from medical and anatomy pictures")
    parser.add_argument("--own", default="", help="a folder of your own described pictures (own_data.py)")
    parser.add_argument("--own-only", action="store_true", help="with --own: train on your own pictures alone")
    parser.add_argument("--personal-noncommercial", action="store_true",
                        help="also learn from non-commercial collections (the add-on is for personal use only)")
    parser.add_argument("--personal-research", action="store_true",
                        help="also learn from research-only collections (personal use only; needs "
                             "--accept-research-terms)")
    parser.add_argument("--accept-research-terms", action="store_true",
                        help="you have read the research-only collections' terms and will use the result only for "
                             "personal, non-commercial purposes")
    args = parser.parse_args(argv)
    content = {"with_nudity": args.with_nudity, "with_medical": args.with_medical,
               "with_noncommercial": args.personal_noncommercial, "with_research": args.personal_research}
    personal = args.personal_noncommercial or args.personal_research
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    sources.say = say
    work = os.path.join(HERE, "work")
    os.makedirs(work, exist_ok=True)
    state = State(work)
    keep_awake(True)
    if args.library:
        open_library(work, args.library)
    if args.own_only and not args.own:
        stop("Only your own pictures was chosen, but no folder of your own pictures was given (--own FOLDER).")
    if args.own and not os.path.isdir(args.own):
        stop(f"The folder of your own pictures was not found: {args.own}")
    if args.personal_research and not args.accept_research_terms:
        stop("Research-only collections were chosen, but their terms were not accepted. Read their terms and agree "
             "to use the result only for personal, non-commercial purposes (in the program: tick Include "
             "research-only collections and press Agree; with the .cmd files: add --accept-research-terms).")
    tag = ("-wikipedia" if args.with_wikipedia else "") + ("" if args.size == "normal" else f"-{args.size}")
    run = f"{args.model}{tag}"                 # each kind of run keeps its own test results and add-on
    plan = None
    if args.follow_up:
        plan = state.data.get("follow-up")
        # What today's choices allow: a training that learned from art with nudity, medical pictures, your own
        # pictures, or non-commercial or research-only collections (personal use) is only carried on from when that
        # is chosen again now.
        wanted_now = {"nudity": args.with_nudity, "medical": args.with_medical, "own": bool(args.own),
                      "noncommercial": args.personal_noncommercial, "research": args.personal_research}
        if plan and not state.done(f"after-{plan['run']}") and \
                any(on and not wanted_now.get(c) for c, on in plan.get("needs", {}).items()):
            say("The follow-up started before carries on from a training made with choices that are not made now "
                "(" + ", ".join(c for c, on in plan["needs"].items() if on and not wanted_now.get(c)) + "); a new "
                "follow-up is planned instead.")
            plan = None
        if not plan or state.done(f"after-{plan['run']}"):      # a new follow-up (the last one has finished)
            earlier = [(r, f) for r, f in finished_runs(work, state) if r.startswith(args.model) and
                       all(wanted_now[c] or not state.data[f"train-{r}"].get(c) for c in wanted_now)]
            if not earlier:
                # Say when a personal-use training was passed over, so the person knows which choice it needs.
                skipped = {c for r, _f in finished_runs(work, state) if r.startswith(args.model)
                           for c in ("noncommercial", "research") if state.data[f"train-{r}"].get(c)
                           and not wanted_now[c]}
                names = {"noncommercial": "non-commercial", "research": "research-only"}
                hint = (" A training for personal use only (with " + " and ".join(names[c] for c in sorted(skipped))
                        + " collections) is only carried on from when the same choice is made again."
                        if skipped else "")
                stop("There is no finished training to carry on from that fits these choices. Train once first "
                     "(Start Training)." + hint)
            base_run, base_final = earlier[-1]
            old = prepared_collections(state)
            wanted = [k.strip() for k in args.collections.split(",") if k.strip()]
            allowed = [s.key for s in sources.chosen(args.with_wikipedia, **content)]
            new = wanted or [k for k in allowed if k not in old]
            left = [k for k in new if k not in allowed and any(s.key == k for s in sources.SOURCES)]
            if left:
                say("Left out because of the content choices: " + ", ".join(left) + ".")
            new = [k for k in new if k in allowed]
            if args.own_only:
                new = []                         # only the person's own pictures are added
            if not new and not args.own:
                stop("Every collection was already in the earlier training: there is nothing new to add yet.")
            import time as _time
            # A follow-up with a personal-use choice is personal too ("-personal" in its name), and remembers which
            # choices it needs (its earlier training's, and the personal-use ones made now).
            needs = {c: bool(state.data[f"train-{base_run}"].get(c)) for c in wanted_now}
            needs.update({c: wanted_now[c] or needs[c] for c in ("noncommercial", "research")})
            plan = {"run": f"{args.model}-plus-{_time.strftime('%Y%m%d-%H%M')}" + ("-personal" if personal else ""),
                    "from": base_run, "from_final": base_final, "needs": needs,
                    "new": new, "old": {k: v for k, v in old.items() if k not in new}}
            state.mark("follow-up", plan)
        run = plan["run"]
        tag = run[len(args.model):]
    say("")
    say(f"Picture Model Training Kit started for the {args.model.upper()} model, size {args.size}"
        + (", with Wikipedia." if args.with_wikipedia else "."))
    say(sources.content_choices_text(args.with_nudity, args.with_medical))
    if personal:
        say("Personal-use collections: " + " and ".join(w for w, on in (
            ("non-commercial", args.personal_noncommercial), ("research-only", args.personal_research)) if on)
            + " included. This training will be for personal use only.")
    if args.own:
        say(f"With your own pictures from {args.own}" + (", alone." if args.own_only else ", added to the collections."))
    if plan:
        if plan["new"]:
            say(f"This is a follow-up: it carries on from the training {plan['from']} and adds "
                f"{len(plan['new'])} collection{'s' if len(plan['new']) != 1 else ''}: "
                + ", ".join(source_name(k).split(":")[0] for k in plan["new"]) + ".")
        else:
            say(f"This is a follow-up: it carries on from the training {plan['from']} and adds your own pictures.")
    say("Windows will not go to sleep while this runs; the screen may turn off. You can close this window at any time "
        "and start the kit again later: it carries on where it stopped.")
    say("Step 1 of 7: checking the graphics card and the disk.")
    card, _ = check_computer(args.model, work)
    say(f"Step 2 of 7: downloading the {args.model.upper()} model (about {9 if args.model == '4b' else 17} GB; "
        "carries on if stopped).")
    folder = download_model(args.model, work)
    say("Step 3 of 7: downloading the described pictures of each collection and making them smaller. A collection "
        "done before is not downloaded again.")
    if args.own_only:
        train_rows, test_rows = [], []
    elif plan:
        train_rows, test_rows = follow_up_rows(work, state, plan, args.with_wikipedia, args.size, args.replay,
                                               **content)
    else:
        train_rows, test_rows = prepare_data(work, state, args.size, args.with_wikipedia, **content)
    own_count = 0
    if args.own:
        own_train, own_test, own_tag = own_rows(work, args.own)
        own_count = len(own_train) + len(own_test)
        if not own_train and args.own_only:
            stop("None of your own pictures can be used. Read the problems above, then start again.")
        if not own_train:
            say("  None of your own pictures can be used (see the problems above); training goes on without them.")
        else:
            import random
            train_rows = train_rows + own_train
            random.Random(6).shuffle(train_rows)
            test_rows = test_rows + own_test
            if not plan:          # a training with own pictures is its own training, named after them
                run += ("-own-only-" if args.own_only else "-own-") + own_tag
                tag += ("-own-only-" if args.own_only else "-own-") + own_tag
    used = {sources.content_of(r["source"]) for r in train_rows + test_rows}
    if any(r["source"] == "own" for r in train_rows):
        used.add("own")
    if not plan:
        # A training with the content choices is its own training too ("4b-nudity-medical"); named after the
        # collections really prepared, so a training started before those packs existed carries on as it was.
        extra = "".join(f"-{c}" for c in ("nudity", "medical") if c in used)
        extra += "-personal" if personal else ""     # personal use only: its own training, never mixed up
        run, tag = run + extra, tag + extra
    if not train_rows:
        stop("No collection could be downloaded. Check the internet connection and start the kit again.")
    extra = place_rows(train_rows)                     # "Which country might this photo be from?" and the like
    if extra:
        import random
        train_rows = train_rows + extra
        random.Random(7).shuffle(train_rows)
        say(f"  {len(extra)} questions about where pictures are from were added to the training.")
    if args.limit:
        train_rows = train_rows[:args.limit]
    device = "cuda"
    results = os.path.join(work, f"results-{run}")
    os.makedirs(results, exist_ok=True)
    before_path, after_path = os.path.join(results, "before.jsonl"), os.path.join(results, "after.jsonl")
    if not state.done(f"before-{run}"):
        say(f"Step 4 of 7: testing the model before training on {len(test_rows)} pictures (about half an hour)"
            + (", with the earlier add-on." if plan else "."))
        model, processor = load_model(folder, adapter=plan["from_final"] if plan else None)
        before = run_test(model, processor, test_rows, before_path, device, "before training")
        state.mark(f"before-{run}", before)
        del model, processor
        free()
    else:
        say("Step 4 of 7: the test before training is done (done before).")
    before = state.data[f"before-{run}"]
    say(f"  Score before training: {before['all']:.3f}.")
    adapter_dir = os.path.join(work, f"adapter-{run}")
    final = os.path.join(adapter_dir, "final")
    if not state.done(f"train-{run}"):
        say(f"Step 5 of 7: training on {len(train_rows)} pictures. This is the long part; the time left is said every "
            f"{SAVE_EVERY} pictures.")
        model, processor = load_model(folder, trainable=True, adapter=plan["from_final"] if plan else None)
        seconds = train(model, processor, train_rows, adapter_dir, device)
        state.mark(f"train-{run}", {"seconds": seconds, "nudity": "nudity" in used, "medical": "medical" in used,
                                    "own": "own" in used, "noncommercial": args.personal_noncommercial,
                                    "research": args.personal_research})
        del model, processor
        free()
    else:
        say("Step 5 of 7: training is done (done before).")
    if not state.done(f"after-{run}"):
        say(f"Step 6 of 7: testing the trained model on the same {len(test_rows)} pictures.")
        model, processor = load_model(folder, adapter=final)
        after = run_test(model, processor, test_rows, after_path, device, "after training")
        state.mark(f"after-{run}", after)
        del model, processor
        free()
    after = state.data[f"after-{run}"]
    say(f"  Score after training: {after['all']:.3f} (before: {before['all']:.3f}).")
    say("Step 7 of 7: writing the report and the zip to send.")
    repo, revision, _ = MODELS[args.model]
    info = {"model": repo, "revision": revision, "card": card, "train": len(train_rows), "test": len(test_rows),
            "size": args.size, "share_alike": args.with_wikipedia, **content,
            "own_pictures": own_count, "own_only": args.own_only, "places": place_counts(train_rows),
            "collections": sorted({r["source"] for r in train_rows}),
            "seconds": state.data[f"train-{run}"]["seconds"], "before": before, "after": after,
            "continued_from": plan["from"] if plan else None,
            "settings": {"lora_r": 16, "lora_alpha": 32, "rate": 1e-4, "accumulate": 8, "four_bit": True,
                         "long_side": sources.LONG_SIDE, "system": SYSTEM}}
    report = os.path.join(HERE, f"report-{run}.txt")
    _, words = write_report(report, info, before, after, read_rows(before_path), read_rows(after_path))
    path = package(args.model, final, report, info, tag)
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
