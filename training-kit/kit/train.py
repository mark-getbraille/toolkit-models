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

def prepare_data(work, state, size, with_wikipedia):
    """Prepare every chosen collection once (each one remembered as done in state, so a restarted kit skips it);
    writes data/train.jsonl (shuffled) and data/test.jsonl and returns (training rows, test rows). A collection that
    cannot be downloaded now is said and left out, so one broken website never stops the training."""
    import random
    data_dir = os.path.join(work, "data")
    os.makedirs(data_dir, exist_ok=True)
    train_rows, test_rows = [], []
    chosen = sources.chosen(with_wikipedia)
    for number, source in enumerate(chosen, 1):
        say(f"  Collection {number} of {len(chosen)}: {source.name} (downloads {source.download}).")
        try:
            train, test = sources.prepare_source(source, data_dir, work, size)
        except Exception as e:  # noqa: BLE001 - one collection failing does not stop the others
            say(f"    This collection could not be prepared now ({str(e).splitlines()[0][:200]}); it is left out. "
                "Start the kit again later to try it again.")
            continue
        state.mark(f"data-{source.key}-{size}", {"train": len(train), "test": len(test)})
        say(f"    Ready: {len(train)} pictures for training, {len(test)} for the test.")
        train_rows += train
        test_rows += test
    random.Random(5).shuffle(train_rows)
    for name, rows in (("train", train_rows), ("test", test_rows)):
        with open(os.path.join(data_dir, f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
    return train_rows, test_rows


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

def source_name(key):
    """The plain name of a collection key, for the report."""
    return next((s.name for s in sources.SOURCES if s.key == key), key)


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


def attribution(chosen_keys, share_alike):
    """ATTRIBUTION.txt: the licence of the add-on and the credit of every collection it learned from."""
    lines = ["Picture description add-on for Qwen3-VL (huihui-ai's abliterated version, Apache License 2.0)", "",
             "Licence of this add-on: " + ("CC BY-SA 4.0 (it learned from Wikipedia's CC BY-SA text)" if share_alike
                                           else "Apache License 2.0, with the credits below (CC BY sources)"), "",
             "It learned from these collections of described pictures:"]
    for source in sources.SOURCES:
        if source.key in chosen_keys:
            lines += [f"- {source.credit}", f"  Licence: {source.licence}"]
    return "\n".join(lines) + "\n"


def write_report(path, info, before, after, before_rows, after_rows):
    """The report: what was trained, the scores for each collection, the verdict and examples (the person's answer,
    the model's before and after: two from each collection), in plain words."""
    counts = {}
    for row in before_rows:
        counts[row["source"]] = counts.get(row["source"], 0) + 1
    better, words = verdict(before, after, counts)
    lines = ["Picture Model Training Kit: report", "",
             f"Finished: {datetime.datetime.now():%d %B %Y at %H:%M}",
             f"Model: {info['model']} (commit {info['revision'][:12]})",
             f"Graphics card: {info['card']}",
             f"Training pictures: {info['train']}; test pictures: {info['test']}; size: {info['size']}"
             + ("; with Wikipedia (the add-on is CC BY-SA 4.0)" if info["share_alike"] else ""),
             f"Training time: {duration(info['seconds'])}", "",
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
        z.writestr("ATTRIBUTION.txt", attribution(info["collections"], info["share_alike"]))
        z.write(LOG, "training-log.txt")
    return path


# ----------------------------------------------------------------- all steps

def main(argv=None):
    """Run the steps (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", choices=sorted(MODELS), default="4b")
    parser.add_argument("--size", choices=sorted(sources.SIZES), default="normal")
    parser.add_argument("--with-wikipedia", action="store_true", help="also learn from Wikipedia (CC BY-SA 4.0)")
    parser.add_argument("--limit", type=int, default=0, help="train on at most this many pictures")
    args = parser.parse_args(argv)
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    sources.say = say
    work = os.path.join(HERE, "work")
    os.makedirs(work, exist_ok=True)
    state = State(work)
    keep_awake(True)
    tag = ("-wikipedia" if args.with_wikipedia else "") + ("" if args.size == "normal" else f"-{args.size}")
    run = f"{args.model}{tag}"                 # each kind of run keeps its own test results and add-on
    say("")
    say(f"Picture Model Training Kit started for the {args.model.upper()} model, size {args.size}"
        + (", with Wikipedia." if args.with_wikipedia else "."))
    say("Windows will not go to sleep while this runs; the screen may turn off. You can close this window at any time "
        "and start the kit again later: it carries on where it stopped.")
    say("Step 1 of 7: checking the graphics card and the disk.")
    card, _ = check_computer(args.model, work)
    say(f"Step 2 of 7: downloading the {args.model.upper()} model (about {9 if args.model == '4b' else 17} GB; "
        "carries on if stopped).")
    folder = download_model(args.model, work)
    say("Step 3 of 7: downloading the described pictures of each collection and making them smaller. A collection "
        "done before is not downloaded again.")
    train_rows, test_rows = prepare_data(work, state, args.size, args.with_wikipedia)
    if not train_rows:
        stop("No collection could be downloaded. Check the internet connection and start the kit again.")
    if args.limit:
        train_rows = train_rows[:args.limit]
    device = "cuda"
    results = os.path.join(work, f"results-{run}")
    os.makedirs(results, exist_ok=True)
    before_path, after_path = os.path.join(results, "before.jsonl"), os.path.join(results, "after.jsonl")
    if not state.done(f"before-{run}"):
        say(f"Step 4 of 7: testing the model before training on {len(test_rows)} pictures (about half an hour).")
        model, processor = load_model(folder)
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
        model, processor = load_model(folder, trainable=True)
        seconds = train(model, processor, train_rows, adapter_dir, device)
        state.mark(f"train-{run}", {"seconds": seconds})
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
            "size": args.size, "share_alike": args.with_wikipedia,
            "collections": sorted({r["source"] for r in train_rows}),
            "seconds": state.data[f"train-{run}"]["seconds"], "before": before, "after": after,
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
